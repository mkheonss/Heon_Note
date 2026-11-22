"""
* 프로그램명
    - PY_UI_SOPAdjustSETRemainMtrl

* 내용
    - Solver 실행 완료 후 결과 계획결과 기반으로 SOP Adjust를 위한 사전점검

* 변경이력
    - 2024.08.08 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_SOPAdjustSETRemainMtrl : Select (Version.[Version Name] * FROM.[Item].[Item] * FROM.[Activity1].[Activity1] * FROM.[Activity3].[Activity3] * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID] * FROM.[Time].[Week] * FROM.[Location].[Location] * TO.[Time].[Week] * TO.[Item].[Item] * TO.[Sales Domain].[Customer Group] * TO.[Demand].[DemandID].[InventoryDemand] * TO.[Location].[Location] * TO.[Demand Type].[Demand Type]) on row, ({Edge.[002.003W Solver Outputs Material Production Pegging].[W Material Production Pegged Quantity]}) on column where {RelationshipType.[002.003W Solver Outputs Material Production Pegging],  FROM.[Item].[Item Type].[RawMaterials], TO.[Item].[Item Type].[RawMaterials]};

* Flow Summary
    - STEP1. Solver Output 결과를 기반으로 SOP Adjust 사전점검을 위한 자재 가용(여유)재고 데이터
    - STEP2. Version별로 데이터 처리

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_SOPAdjustSETRemainMtrl

* 데이타 초기화
    - Delete data for model [SOP Adjustment SET Remain Mtrl] where{[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SOPAdjustSETRemainMtrl] for Measures{[SOP Adjust SET Remain Mtrl_Init Remain Supply Qty]} using scope (&MPV * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material] ) on row,
        ({Measure.[SOP Adjust SET Remain Mtrl_Adj Used Qty], Measure.[SOP Adjust SET Remain Mtrl_Cur Remain Qty], Measure.[SOP Adjust SET Remain Mtrl_Init Remain Supply Qty]}) on column;

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
str_instance = 'PY_UI_SOPAdjustSETRemainMtrl'
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
            df_in_SOPAdjustSETRemainMtrl = read_csv_file("df_in_SOPAdjustSETRemainMtrl")

        print_df(df_in_SOPAdjustSETRemainMtrl, 'input table load .... df_in_SOPAdjustSETRemainMtrl')

        step('=====> STEP1 End')


    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
    
        FROM_ITEM_COLUMN = 'from.[Item].[Item]'
        FROM_ACTIVITY1_COLUMN = 'from.[Activity1].[Activity1]'
        FROM_ACTIVITY2_COLUMN = 'from.[Activity2].[Activity2]'
        FROM_ACTIVITY3_COLUMN = 'from.[Activity3].[Activity3]'
        FROM_ORDERLINE_ID_COLUMN = 'from.[Documents].[OrderlineID]'
        FROM_TIME_WEEK_COLUMN = 'from.[Time].[Week]'
        FROM_LOCATION_COLUMN = 'from.[Location].[Location]'
    
        TO_ITEM_COLUMN = 'to.[Item].[Item]'
        TO_TIME_WEEK_COLUMN = 'to.[Time].[Week]'
        TO_CUSTOMER_GROUP_COLUMN = 'to.[Sales Domain].[Customer Group]'
        TO_DEMAND_ID_COLUMN = 'to.[Demand].[DemandID]'
        TO_LOCATION_COLUMN = 'to.[Location].[Location]'
        TO_DEMAND_TYPE_COLUMN = 'to.[Demand Type].[Demand Type]'
    
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
    
        QUANTITY_COLUMN = '002.003W Solver Outputs Material Production Pegging.[W Material Production Pegged Quantity]'
    
        ITEM_METERIAL_COLUMN = '[Item Material].[Item Material]'
        SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN = 'SOP Adjust SET Remain Mtrl_Adj Used Qty'
        SOP_ADJUST_SET_REMAIN_MTRL_CREATE_TIME_COLUMN = 'SOP Adjust SET Remain Mtrl_Create Time'
        SOP_ADJUST_SET_REMAIN_MTRL_CREATE_BY_COLUMN = 'SOP Adjust SET Remain Mtrl_Created By'
        SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN = 'SOP Adjust SET Remain Mtrl_Cur Remain Qty'
        SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN = 'SOP Adjust SET Remain Mtrl_Init Remain Supply Qty'
        SOP_ADJUST_SET_REMAIN_MTRL_UPDATE_TIME_COLUMN = 'SOP Adjust SET Remain Mtrl_Update Time'
        SOP_ADJUST_SET_REMAIN_MTRL_UPDATE_BY_COLUMN = 'SOP Adjust SET Remain Mtrl_Updated By'

        df_SOPAdjustSETRemainMtrl_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN,
            SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN
        ]
    
        step('=====> STEP2 End')


    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
        # BOD List 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다. 이미 BOD Item 에 있으면 구성할 필요는 없음




        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_SOPAdjustSETRemainMtrl.empty:
            raise CustomException(".... df_in_SOPAdjustSETRemainMtrl 값이 없습니다.")



        # input table 에서 필요한 컬럼만 copy
        df_SOPAdjustSETRemainMtrl = df_in_SOPAdjustSETRemainMtrl[[
            VERSION_NAME_COLUMN, TO_LOCATION_COLUMN, TO_TIME_WEEK_COLUMN, TO_ITEM_COLUMN, QUANTITY_COLUMN
        ]].copy()
    
        # 컬럼명 변경
        df_SOPAdjustSETRemainMtrl.rename(columns={TO_LOCATION_COLUMN: LOCATION_COLUMN,
                                                  TO_TIME_WEEK_COLUMN: TIME_WEEK_COLUMN,
                                                  TO_ITEM_COLUMN: ITEM_METERIAL_COLUMN
                                                  }, inplace=True)
    
        # 컬럼명 변경
        df_SOPAdjustSETRemainMtrl.rename(
            columns={QUANTITY_COLUMN: SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN}, inplace=True)
        df_SOPAdjustSETRemainMtrl[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] = df_SOPAdjustSETRemainMtrl[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN]
        print_df(df_SOPAdjustSETRemainMtrl, 'df_SOPAdjustSETRemainMtrl')
    
        step('=====> STEP3 End')


    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP 4(Start) : output data machining')
    
        df_out_SOPAdjustSETRemainMtrl = rename_and_delete_df(df_SOPAdjustSETRemainMtrl)
        df_out_SOPAdjustSETRemainMtrl[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')


    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_SOPAdjustSETRemainMtrl, 'output table create .... df_out_SOPAdjustSETRemainMtrl', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPAdjustSETRemainMtrl = pd.DataFrame(columns=df_SOPAdjustSETRemainMtrl_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SOPAdjustSETRemainMtrl = pd.DataFrame(columns=df_SOPAdjustSETRemainMtrl_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
