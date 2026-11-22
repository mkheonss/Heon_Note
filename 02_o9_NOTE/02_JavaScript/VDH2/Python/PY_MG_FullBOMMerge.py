"""
* 프로그램명
    - PY_MG_FullBOMMerge

* 내용
    - New Model Mapping > Full BOM 추가 구성

* 변경이력
    - 2024.09.20 / 권태우 / Create
    - 2024.10.04 / 권태우 / Full BOM Grain변경/메저추가됨(df_in_FullBOM), STEP1 BOM Status

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_NewModelMap : Select (Version.[Version Name] * [Item].[Item] * [Item Material].[Item Material] ) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[New Model Map BOM_Base Qty], Measure.[New Model Map BOM_Created By], Measure.[New Model Map BOM_Creation Time], Measure.[New Model Map BOM_HQ Dev Purchaser], Measure.[New Model Map BOM_HQ Purchaser], Measure.[New Model Map BOM_User Spec]}) on column;
    - df_in_FullBOM     : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] * [Status].[Status] ) on row, ({ Measure.[Full BOM_Acil Date], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Issue Date], Measure.[Full BOM_SRA Date], Measure.[Full BOM_Safety Date]}) on column;
    - df_in_PlanningWeek: Select ([Time].[Day] * &PlanningHorizon);

* Flow Summary
    - STEP1. Soft Constraint 모델링 대상 ITEM을 가져와서 현재 ITEM BOD와 매핑
    - STEP2. Soft Constraint 주차와 매핑
    - STEP3~4. Soft Constraint ITEM BOD Set 구성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_FullBOM

* 데이타 초기화
    - DELETE DATA FOR MODEL [Full BOM] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_FullBOMMerge] for measures {[Full BOM_Base Qty]}
        using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPFIXCapacity / MG:  Full BOM
        Select ( &MPV * [Item].[Item] * [Location].[Location] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] * [Status].[Status] ) on row, ({
            Measure.[Full BOM_Acil Date], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate],
            Measure.[Full BOM_Issue Date], Measure.[Full BOM_SRA Date], Measure.[Full BOM_Safety Date]}) on column;
"""
import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_FullBOMMerge'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)



########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
log_level_info = LOG_LEVEL.info()
log_level_debug = LOG_LEVEL.debug()
logger.debug(f'[START] {str_instance}')
logger.Start()


########################################################################################################################
# local function
########################################################################################################################
class CustomException(Exception):
    pass


def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def step(string):
    vdCommon.gfn_stepLog(string)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)



def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, logger, is_local, log_path)


def vd_log_end():
    vdCommon.gfn_pyLog_end()


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(target_df):
    new_df = target_df
    delete_dfs(target_df)
    return new_df


def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
        return df[column_name].values[0]
    return None  # 기본값 반환


def get_formatted_time(timestamp):
    """타임스탬프를 사람이 읽을 수 있는 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")



def format_size(size_in_bytes):
    """바이트 단위를 적절히 MB 또는 GB로 변환하여 문자열 반환"""
    if size_in_bytes >= 1024 ** 3:  # 1GB 이상일 때
        return f"{size_in_bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{size_in_bytes / 1024 ** 2:.1f} MB"


def run_time_minutes(start_time):
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"




########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # Batch 시작
    vd_log_start()

    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_NewModelMap = read_csv_file("df_in_NewModelMap")
            df_in_FullBOM = read_csv_file("df_in_FullBOM")
            df_in_PlanningWeek = read_csv_file("df_in_PlanningWeek")
    
    
        print_df(df_in_NewModelMap, 'input table load .... df_in_NewModelMap')
        print_df(df_in_FullBOM, 'input table load .... df_in_FullBOM')
        print_df(df_in_PlanningWeek, 'input table load .... df_in_PlanningWeek')

        step('=====> STEP1 End')



    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
    
        LOCATION_COLUMN = 'Location.[Location]'
        LOCATION_X_COLUMN = 'Location.[Location]_x'
        LOCATION_Y_COLUMN = 'Location.[Location]_y'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TIME_DAY_COLUMN = 'Time.[Day]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
    
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_METRIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_METRIAL_X_COLUMN = 'Item Material.[Item Material]_x'
        ITEM_METRIAL_Y_COLUMN = 'Item Material.[Item Material]_y'
        NMM_BOM_BOM_TYPE_COLUMN = 'New Model Map BOM_BOM Type'
        NMM_BOM_BASE_QTY_COLUMN = 'New Model Map BOM_Base Qty'
        NMM_BOM_HQ_DEV_PURCHASRE_COLUMN = 'New Model Map BOM_HQ Dev Purchaser'
        NMM_BOM_HQ_PUCHASER_COLUMN = 'New Model Map BOM_HQ Purchaser'
        NMM_BOM_LOCK_FLAG_COLUMN = 'New Model Map BOM_Lock Flag'
        NMM_BOM_USER_SPEC_COLUMN = 'New Model Map BOM_User Spec'
    
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
        STATUS_COLUMN = 'Status.[Status]'
        BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        BOM_TYPE_COLUMN = 'BOM Type.[BOM Type]'
        BOM_STATUS_COLUMN = 'BOM Status.[BOM Status]'
        FULL_BOM_BOM_LEVEL_COLUMN = 'Full BOM_BOM Level'
        FULL_BOM_BASE_QTY_COLUMN = 'Full BOM_Base Qty'
        FULL_BOM_EFF_STARTDATE_COLUMN = 'Full BOM_Eff Startdate'
        FULL_BOM_EFF_ENDDATE_COLUMN = 'Full BOM_Eff Enddate'
        FULL_BOM_ACIL_DATE_COLUMN = 'Full BOM_Acil Date'
        FULL_BOM_EOP_DATE_COLUMN = 'Full BOM_EOP Date'
        FULL_BOM_ISSUE_DATE_COLUMN = 'Full BOM_Issue Date'
        FULL_BOM_SRA_DATE_COLUMN = 'Full BOM_SRA Date'
        FULL_BOM_SAFETY_DATE_COLUMN = 'Full BOM_Safety Date'
    
        BOM_STATUE_VALUE = 'NSCM Mtrl'

        df_fullBOMAdd_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN,
            ITEM_METRIAL_COLUMN, BOM_VERSION_COLUMN, BOM_TYPE_COLUMN, BOM_STATUS_COLUMN,
            FULL_BOM_ACIL_DATE_COLUMN, FULL_BOM_BOM_LEVEL_COLUMN, FULL_BOM_BASE_QTY_COLUMN,
            FULL_BOM_EOP_DATE_COLUMN, FULL_BOM_EFF_ENDDATE_COLUMN, FULL_BOM_EFF_STARTDATE_COLUMN,
            FULL_BOM_ISSUE_DATE_COLUMN, FULL_BOM_SRA_DATE_COLUMN, FULL_BOM_SAFETY_DATE_COLUMN,
        ]
    
        step('=====> STEP2 End')



    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # ====================> STEP3 by 1 (Start) -> df_fullBOMAdd Set 구성
        # 1.1 min day
        df_in_PlanningWeek[TIME_DAY_COLUMN] = pd.to_datetime(df_in_PlanningWeek[TIME_DAY_COLUMN])
        plan_min_day = df_in_PlanningWeek[TIME_DAY_COLUMN].min()
        step(f'=====> plan_min_day : {plan_min_day}')


        # 1.2 df_in_NewModelMap, df_in_FullBOM join > df_fullBOMAdd create
        df_fullBOMAdd = pd.merge(df_in_NewModelMap, df_in_FullBOM, how='inner',
                                 left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, NMM_BOM_BOM_TYPE_COLUMN],
                                 right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, BOM_TYPE_COLUMN])
        print_df(df_fullBOMAdd, 'STEP3 by 1.2 ____ df_fullBOMAdd ..... merge[df_in_NewModelMap, df_in_FullBOM]')



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_fullBOMAdd.empty:
            raise CustomException(".... df_fullBOMAdd 값이 없습니다.")


    
        df_fullBOMAdd.rename(columns={ITEM_METRIAL_X_COLUMN: ITEM_METRIAL_COLUMN}, inplace=True)
        df_fullBOMAdd.drop(columns=[ITEM_METRIAL_Y_COLUMN], inplace=True)
    
        df_fullBOMAdd = df_fullBOMAdd[df_fullBOMAdd_columns].drop_duplicates()
        df_fullBOMAdd[BOM_STATUS_COLUMN] = BOM_STATUE_VALUE
        print_df(df_fullBOMAdd, 'STEP3 by 1.2 ____ df_fullBOMAdd ..... final')
    
        # ====================> STEP3 by 1 (End)

        step('=====> STEP3 End')



    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        df_out_FullBOM = rename_and_delete_df(df_fullBOMAdd)
        df_out_FullBOM[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')



    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_FullBOM, 'output table create .... df_out_FullBOM', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_FullBOM = pd.DataFrame(columns=df_fullBOMAdd_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_FullBOM = pd.DataFrame(columns=df_fullBOMAdd_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
