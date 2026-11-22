"""
* 프로그램명
    - PY_MG_DualizationCheck

* 내용
    - UI Soft 관리 대상에 대해 이원화 여부 Check 하여 메저그룹 Update

* 변경이력
    - 2024.11.21 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_MtrlConstType : Select (Version.[Version Name] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Batch_Plant], Measure.[Mtrl Const Type Batch_Type]}) on column.filter(Measure.[Mtrl Const Type Batch_Type] ==  "Soft"   ) ;
    - df_in_BOMComponent  : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate]}) on column;
    - df_in_BOMMaster     : Select (Version.[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_BOM Status], Measure.[BOM Master_BOM Type], Measure.[BOM Master_BOM Version], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column.filter(Measure.[BOM Master_BOM Type]=="SET" || isnull(Measure.[BOM Master_BOM Type] =="Dummy")  ) ;
    - df_in_BOMID         : Select ([BOM Info].[BOM ID] * [BOM Info].[BOM Version] *  [BOM Info].[Item] );

* Flow Summary
    - STEP1. 이원화 대상 BOM Set 구성
    - STEP2. 이원화 대상 BOM Set 을 참고하여 이원화 대상 Item 추출 Set 구성
    - STEP3. 이원화 대상 메저 표기

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_MtrlConstType

* 데이타 초기화
    - DELETE DATA FOR MODEL [Mtrl Const Type Batch] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_DualizationCheck] for measures {[Mtrl Const Type Batch_Dualization]}
        using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - MG :  Mtrl Const Type Batch
        Select (&MPV * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Batch_Dualization] }) on column;


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
str_instance = 'PY_MG_DualizationCheck'
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
            df_in_MtrlConstType = read_csv_file("df_in_MtrlConstType")
            df_in_BOMComponent = read_csv_file("df_in_BOMComponent")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_BOMID = read_csv_file("df_in_BOMID")
    
    
        print_df(df_in_MtrlConstType, 'input table load .... df_in_MtrlConstType')
        print_df(df_in_BOMComponent, 'input table load .... df_in_BOMComponent')
        print_df(df_in_BOMMaster, 'input table load .... df_in_BOMMaster')
        print_df(df_in_BOMID, 'input table load .... df_in_BOMID')
    
        step('=====> STEP1 End')
        
        
    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
    
        ITEM_COLUMN = 'Item.[Item]'
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
    
        BOM_INFO_BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        BOM_INFO_ITEM_COLUMN = 'BOM Info.[Item]'
    
        MTRL_CONST_TYPE_BATCH_PLANT_COLUMN = 'Mtrl Const Type Batch_Plant'
        MTRL_CONST_TYPE_BATCH_TYPE_COLUMN = 'Mtrl Const Type Batch_Type'
    
        BOM_COMP_CONSUME_QTY_COLUMN = 'BOM Comp_Consume Qty'
        BOM_COMP_EFF_ENDDATE_COLUMN = 'BOM Comp_Eff Enddate'
        BOM_COMP_EFF_STARTDATE_COLUMN = 'BOM Comp_Eff Startdate'
        BOM_COMP_VAILD_FLAG_COLUMN = 'BOM Comp_Valid Flag'
    
        BOM_INFO_BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_BOM_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_EFF_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'
        BOM_MASTER_PRIORITY_COLUMN = 'BOM Master_Priority'
        BOM_MASTER_PRTY_COLUMN = 'BOM Master_Prty'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'
        BOM_MASTER_BOM_VERSION_COLUMN = 'BOM Master_BOM Version'
    
        MTRL_CONST_TYPE_BATCH_DUALIZATION_COLUMN = 'Mtrl Const Type Batch_Dualization'
        TOP_ITEM_COLUMN = 'Top Item'
        
        df_MtrlConstType_columns = [
            VERSION_NAME_COLUMN, ITEM_METERIAL_COLUMN, MTRL_CONST_TYPE_BATCH_DUALIZATION_COLUMN
        ]
    
        step('=====> STEP2 End')
        
        
    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # ====================> STEP3 by 1 (Start) -> 이원화 대상 TOP item Set구성
    
        df_BOMMaster = df_in_BOMMaster.copy()
        df_DualTop = df_BOMMaster.groupby(BOM_MASTER_BOM_ID_COLUMN).agg(ver_cnt=(BOM_MASTER_BOM_VERSION_COLUMN, 'nunique')).reset_index(drop=False)
        df_DualTop = df_DualTop[df_DualTop['ver_cnt'] > 1]
        print_df(df_DualTop, 'STEP3 by 1 ____ df_DualTop .... create')
    
        # ====================> STEP3 by 1 (End)
    


        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_DualTop.empty:
            raise CustomException(".... df_DualTop 값이 없습니다.")

    
    
        # ====================> STEP3 by 2 (Start) -> 이원화 대상 자재 추출 하여 Set구성
    
        df_BOMMaster_distinct = df_in_BOMMaster[[BOM_INFO_BOM_ID_COLUMN]].drop_duplicates()
    
        # 필요한 데이터프레임 간의 조인
        df_merged = pd.merge(df_in_BOMComponent, df_in_MtrlConstType, how='inner', left_on=ITEM_COLUMN, right_on=ITEM_METERIAL_COLUMN)
        print_df(df_merged, 'STEP3 by 2.1 ____ df_merged .... merge 1')
    
        df_merged = pd.merge(df_merged, df_in_BOMID, how='inner', on=BOM_INFO_BOM_ID_COLUMN)
        print_df(df_merged, 'STEP3 by 2.2 ____ df_merged .... merge 2')
    
        df_merged = pd.merge(df_merged, df_BOMMaster_distinct, how='inner', on=BOM_INFO_BOM_ID_COLUMN)
        print_df(df_merged, 'STEP3 by 2.3 ____ df_merged .... merge 3')
    
        df_merged.rename(columns={ITEM_METERIAL_COLUMN: TOP_ITEM_COLUMN}, inplace=True)
    
        # 그룹화 및 결과 집계
        df_merged = df_merged.groupby([ITEM_COLUMN, TOP_ITEM_COLUMN])[BOM_INFO_BOM_VERSION_COLUMN].nunique().reset_index(name='ver_cnt')
        print_df(df_merged, 'STEP3 by 2.4 ____ df_merged .... groupby')

        # ====================> STEP3 by 2 (End)
    
    

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_merged.empty:
            raise CustomException("....> df_merged 값이 없습니다.")

    
    
        # ====================> STEP3 by 3 (Start) -> df_dualItem 대상 Item Material 에 대해 Mtrl Const Type Batch - Mtrl Const Type Batch_Dualization 입력
    
        result = (
            pd.merge(df_merged, df_DualTop, left_on=ITEM_COLUMN, right_on=BOM_MASTER_BOM_ID_COLUMN).query("ver_cnt_x.fillna(0) != ver_cnt_y.fillna(0)").
            assign(Mtrl_Const_Type_Batch_Dualization='Y').drop_duplicates(subset=[ITEM_COLUMN])[[ITEM_COLUMN,  'Mtrl_Const_Type_Batch_Dualization']]
        )
    
        result.rename(columns={
            'Mtrl_Const_Type_Batch_Dualization': MTRL_CONST_TYPE_BATCH_DUALIZATION_COLUMN,
            ITEM_COLUMN: ITEM_METERIAL_COLUMN,
        }, inplace=True)
        print_df(result, 'Step3 by 3.1 ____ result .... final')
    
        # ====================> STEP3 by 3 (End)
    
        step('=====> STEP3 End')
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP 4(Start) : output data machining')
        
        df_out_MtrlConstType = rename_and_delete_df(result)
        df_out_MtrlConstType[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_MtrlConstType = df_out_MtrlConstType[df_MtrlConstType_columns]
    
        step('=====> STEP 4(End) : Check memory usage & runtime')
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_MtrlConstType, 'output table create .... df_out_MtrlConstType', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_MtrlConstType = pd.DataFrame(columns=df_MtrlConstType_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_MtrlConstType = pd.DataFrame(columns=df_MtrlConstType_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
