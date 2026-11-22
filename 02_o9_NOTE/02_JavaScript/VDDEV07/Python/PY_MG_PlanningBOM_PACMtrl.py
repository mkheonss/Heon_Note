"""
* 프로그램명
    - PY_MG_PlanningBOM_PACMtrl

* 내용
    - BOM Header 기준 Pre-alloc. Constraint 대상 BOM Component 생성
    - PY_MG_PlanningBOM 프로그램 다음에 호출

* 변경이력
    - 2024.10.08 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_BOMMaster       : Select (Version.[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column;
    - df_in_PreAllocItem    : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const by Item_Creation Time]}) on column;
    - df_in_PreAllocDetailW : Select (Version.[Version Name] * &PlanningHorizon * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const Detail W_Const Qty] }) on column;

* Flow Summary
    - STEP1. Pre-alloc. Constraint 대상 Group ID(자재) BOM Component 생성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BOMComponent

* 데이타 초기화
    - DELETE DATA FOR MODEL [BOM Component] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_PlanningBOM_PACMtrl] for measures {[BOM Comp_Consume Qty]}
        using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPFIXCapacity / MG:  BOM Component
        Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row,  ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate], Measure.[BOM Comp_Valid Flag]}) on column;
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
str_instance = 'PY_MG_PlanningBOM_PACMtrl'
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
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_PreAllocItem = read_csv_file("df_in_PreAllocItem")
            df_in_PreAllocDetailW = read_csv_file("df_in_PreAllocDetailW")


        print_df(df_in_BOMMaster, 'input table load .... df_in_BOMMaster')
        print_df(df_in_PreAllocItem, 'input table load .... df_in_PreAllocItem')
        print_df(df_in_PreAllocDetailW, 'input table load .... df_in_PreAllocDetailW')

        step('=====> STEP1 End')
        
        
        

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'

        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        ITEM_COLUMN = 'Item.[Item]'

        BOM_INFO_BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_BOM_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_EFF_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'
        BOM_MASTER_PRIRITY_COLUMN = 'BOM Master_Priority'
        BOM_MASTER_PRTY_COLUMN = 'BOM Master_Prty'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'

        TIME_WEEK_COLUMN = 'Time.[Week]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'
        PRE_ALLOC_CONST_DETAIL_W_CONST_QRT_COLUMN = 'Pre Alloc Const Detail W_Const Qty'

        BOM_COMP_CONSUME_QTY_COLUMN = 'BOM Comp_Consume Qty'
        BOM_COMP_EFF_ENDDATE_COLUMN = 'BOM Comp_Eff Enddate'
        BOM_COMP_EFF_STARTDATE_COLUMN = 'BOM Comp_Eff Startdate'
        BOM_COMP_VAILD_FLAG_COLUMN = 'BOM Comp_Valid Flag'

        df_BOMComponent_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_ID_COLUMN, BOM_COMP_CONSUME_QTY_COLUMN,
            BOM_COMP_EFF_ENDDATE_COLUMN, BOM_COMP_EFF_STARTDATE_COLUMN, BOM_COMP_VAILD_FLAG_COLUMN
        ]

        step('=====> STEP2 End')
        
        
        

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ====================> STEP3 by 1 (Start) > df_PreAllocBOM Set 구성하여  df_out_BOMComponent 에 Insert
        # 1.1 df_in_BOMMaster re-create
        drop_column = [col for col in list(df_in_BOMMaster .columns) if col not in [BOM_INFO_BOM_ID_COLUMN, BOM_MASTER_BOM_ID_COLUMN]]
        df_in_BOMMaster = df_in_BOMMaster.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[BOM_INFO_BOM_ID_COLUMN, BOM_MASTER_BOM_ID_COLUMN], keep='first')
        df_in_BOMMaster[BOM_MASTER_PRIRITY_COLUMN] = 1
        df_in_BOMMaster[BOM_MASTER_STATUS_COLUMN] = 'PAC'
        print_df(df_in_BOMMaster, 'STEP3 by 1.1 ____ df_in_BOMMaster .... re-create')


        # 1.2 df_BOMComponent create
        df_BOMComponent = pd.merge(df_in_PreAllocItem, df_in_PreAllocDetailW, how='inner',
                                   on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, LOCATION_COLUMN])
        print_df(df_BOMComponent, 'STEP3 by 1.2 ____ df_BOMComponent .... merge 1')


        # 1.3 df_in_BOMMaster join
        df_BOMComponent = pd.merge(df_BOMComponent, df_in_BOMMaster, how='inner',
                                   left_on=[ITEM_COLUMN], right_on=[BOM_MASTER_BOM_ID_COLUMN])
        print_df(df_BOMComponent, 'STEP3 by 1.3 ____ df_BOMComponent .... merge 2')

        df_BOMComponent = df_BOMComponent[[VERSION_NAME_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_ID_COLUMN]].drop_duplicates()
        df_BOMComponent[BOM_COMP_CONSUME_QTY_COLUMN] = 1
        df_BOMComponent[BOM_COMP_EFF_ENDDATE_COLUMN] = None
        df_BOMComponent[BOM_COMP_EFF_STARTDATE_COLUMN] = None
        df_BOMComponent[BOM_COMP_VAILD_FLAG_COLUMN] = True

        # ====================> STEP3 by 1 (End)

        step('=====> STEP3 End')
        
        
        

        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_out_BOMComponent = rename_and_delete_df(df_BOMComponent)
        df_out_BOMComponent[VERSION_NAME_COLUMN] = paramOutVersion

        step('=====> STEP4 End')
        
        
        

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_BOMComponent, 'output table create .... df_out_BOMComponent')

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BOMComponent = pd.DataFrame(columns=df_BOMComponent_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BOMComponent = pd.DataFrame(columns=df_BOMComponent_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
