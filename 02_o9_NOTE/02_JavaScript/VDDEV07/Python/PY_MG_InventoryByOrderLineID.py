"""
* 프로그램명
    - PY_MG_InventoryByOrderLineID

* 내용
    - MP Engine 수행을 위한 재고 및 가용성 정보 Input
    - MP Plan Batch Procedure에서 Call 하는 Program
    - 재고에 해당하는 Document Dimension의 Documents.[OrderlineID]는 이미 LS에 일괄 생성되어있음.
    - 즉, 별도 Member 생성 필요없음.
    - GSCM에서 I/F 되어온 재고 Measure Group은 현재 Plan 에 반영해야할 OrderlineID 만 존재함. (GSCM : Truncate * Insert)
    - Onhand, Intransit, Schedule Receipt 해당

    - Data Source : GSCM
    - VMG_INVENTORY
    - VMG_INTRANSIT
    - 자재 가용성은 일단 확인중

* 변경이력
    - 2024.06.17 / 권태우 / Create
    - 2024.10.08 / 권태우 / STEP5 추가

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_Inventory : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv_Qty]}) on column;
    - df_in_Intransit : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Intr_BOD Name], Measure.[Intr_Qty], Measure.[Intr_ETA Date] }) on column;
    - df_in_Time      : Select ([Time].[Week] * [Time].[Day]) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};
    - df_in_inv_shuffle : Select (Version.[Version Name] * [Item].[Item] * &PlanningHorizon * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({ Measure.[Inv Shuffle_Qty]}) on column.filter(Measure.[Inv Shuffle_Qty] > 0);
    - df_in_intransit_shuffle : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({ Measure.[Intr Shuffle_ETA Date], Measure.[Intr Shuffle_Qty]}) on column.filter(Measure.[Intr Shuffle_Qty] > 0);
    - df_in_PreAllocItem    : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const by Item_Creation Time]}) on column;
    - df_in_PreAllocDetailW : Select (Version.[Version Name] * &PlanningHorizon * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const Detail W_Const Qty] }) on column;

* Flow Summary
    - Onhand 재고 수량 Insert  ( GSCM : Inventory )
    - Intransit 재고 수량 Insert ( GSCM : Intransit )

* 주요 Logic ( Data 처리 )
    - STEP1 : Onhand 재고 입력
              Inv_Qty  > W OnHand Quantity
    - STEP2 : Intransit 재고 입력 / Intr_ETA Date 를 in_time 를 참고하여 주차로 전환하여 반영 / 만약 in_time에 없는 Intr_ETA_Date는 Intransit를 갱신하지 않아도 됨.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_OnHandQuantity
    - df_out_ExpectedReceipts

* 데이타 초기화
    - DELETE DATA FOR MODEL [001.020W Solver Inputs Inventory Inputs By OrderLine ID] where {Version.[Version Name].[CWV_MP]};

* RUN 스크립트
    - (plug-in 호출시, &PlanningHorizon를 scoping하여 call)
    - EXEC plugin instance [PY_MG_InventoryByOrderLineID] for measures {[CM Artificial Base Capacity Override]} using scope (&CWV  * &PlanningHorizon) using arguments {(ExecutionMode, "LightWeight"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")

* Output Query
    - Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[W OnHand Quantity]}) on column;
    - Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[W Expected Receipts] }) on column;

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
str_instance = 'PY_MG_InventoryByOrderLineID'
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
            df_in_Inventory = read_csv_file("df_in_Inventory")
            df_in_Intransit = read_csv_file("df_in_Intransit")
            df_in_Time = read_csv_file("df_in_Time")
            df_in_inv_shuffle = read_csv_file("df_in_inv_shuffle")
            df_in_intransit_shuffle = read_csv_file("df_in_intransit_shuffle")
            df_in_PreAllocItem = read_csv_file("df_in_PreAllocItem")
            df_in_PreAllocDetailW = read_csv_file("df_in_PreAllocDetailW")
    
    
        print_df(df_in_Inventory, 'input table load .... df_in_Inventory')
        print_df(df_in_Intransit, 'input table load .... df_in_Intransit')
        print_df(df_in_Time, 'input table load .... df_in_Time')
        print_df(df_in_inv_shuffle, 'input table load .... df_in_inv_shuffle')
        print_df(df_in_intransit_shuffle, 'input table load .... df_in_intransit_shuffle')
        print_df(df_in_PreAllocItem, 'input table load .... df_in_PreAllocItem')
        print_df(df_in_PreAllocDetailW, 'input table load .... df_in_PreAllocDetailW')
    
        step('=====> STEP1 End')
        
        
        
    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2(Start) : DataFrame Column 변수 처리')
    
        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        LOCATION_COLUMN = 'Location.[Location]'
        DOCUMENTS_ORDERLINEID_COLUMN = 'Documents.[OrderlineID]'
        INV_QTY_COLUMN = 'Inv_Qty'
        W_ONHAND_QUANTITY_COLUMN = 'W OnHand Quantity'
    
        INTER_BOD_NAME_COLUMN = 'Intr_BOD Name'
        INTER_QTY_COLUMN = 'Intr_Qty'
        INTER_ETA_DATE_COLUMN = 'Intr_ETA Date'
        NEW_INTER_ETA_DATE_COLUMN = 'New Intr_ETA Date'
        W_EXPECTED_RECEIPTS_QUANTITY_COLUMN = 'W Expected Receipts'
    
        TIME_DAY_COLUMN = 'Time.[Day]'
        TIME_DAYKEY_COLUMN = 'Time.[DayKey]'
        TIME_WEEKKEY_COLUMN = 'Time.[WeekKey]'
    
        INV_SHUFFLE_QTY_COLUMN = 'Inv Shuffle_Qty'
        INTR_SHUFFLE_QTY_COLUMN = 'Intr Shuffle_Qty'
        INTR_SHUFFLE_ETA_DATE_COLUMN = 'Intr Shuffle_ETA Date'
    
        TIME_W_SOLVER_CURRENT_BUCKET_COLUMN = 'Time.[W Solver Current Bucket]'
        TIME_W_SOLVER_START_BUCKET_COLUMN = 'Time.[W Solver Start Bucket]'
        TIME_W_SOLVER_END_BUCKET_COLUMN = 'Time.[W Solver End Bucket]'
    
        BOM_COMP_CONSUME_QTY_COLUMN = 'BOM Comp_Consume Qty'
        BOM_COMP_EFF_ENDDATE_COLUMN = 'BOM Comp_Eff Enddate'
        BOM_COMP_EFF_STARTDATE_COLUMN = 'BOM Comp_Eff Startdate'
        BOM_COMP_VAILD_FLAG_COLUMN = 'BOM Comp_Valid Flag'
    
        GROUP_ID_COLUMN = 'Group.[Group ID]'
        ORDERLINE_ID_COLUMN = 'OrderlineID'
        PRE_ALLOC_CONST_DETAIL_W_CONST_QRT_COLUMN = 'Pre Alloc Const Detail W_Const Qty'

        df_OnHandQuantity_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN, W_ONHAND_QUANTITY_COLUMN
        ]

        df_ExpectedReceipts_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN, W_EXPECTED_RECEIPTS_QUANTITY_COLUMN
        ]
        
        step('=====> STEP2 End')
        
        
        
    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # ====================> STEP3 by 1, STEP3 by 2 (Start) -> Onhand 재고 입력.
        #                                                Intransit 재고 입력.
        #                                                  -> Intr_ETA Date 를 in_time 를 참고하여 주차로 전환하여 반영
        #                                                     만약 in_time에 없는 Intr_ETA_Date는 Intransit를 갱신하지 않아도 됨.
    
        # df_in_Intransit > INTER_ETA_DATE_COLUMN 컬럼 변환 (문자열을 datetime 객체로 변환)
        df_in_Intransit[INTER_ETA_DATE_COLUMN] = pd.to_datetime(df_in_Intransit[INTER_ETA_DATE_COLUMN], format='%m/%d/%Y %I:%M:%S %p')
    
        # datetime 객체를 문자열로 변환(strftime은 datetime 객체를 문자열로 변환)
        df_in_Intransit[INTER_ETA_DATE_COLUMN] = df_in_Intransit[INTER_ETA_DATE_COLUMN].dt.strftime('%Y-%m-%d')
    
        # in_Intransit 와 in_Time merge 후 불필요 컬럼 삭제
        df_in_Intransit = pd.merge(df_in_Intransit, df_in_Time, how='left', left_on=INTER_ETA_DATE_COLUMN, right_on=TIME_DAY_COLUMN)
        df_in_Intransit = df_in_Intransit.drop(labels=[INTER_ETA_DATE_COLUMN, TIME_DAY_COLUMN], axis=1)
        print_df(df_in_Intransit, 'STEP 3 by 1 ____ df_in_Intransit .... final')
    
        # ====================> STEP3 by 1, STEP3 by 2 (End)
    
    
    
    
        # ====================> STEP3 by 3 (Start) -> 매치코드 Onhand 재고 입력 -> df_OnHandQuantity
        
        # 3.1 df_OnHandQuantity create
        df_OnHandQuantity = rename_and_delete_df(df_in_inv_shuffle)
    
        # 3.2 컬럼명 변경
        df_OnHandQuantity.rename(columns={INV_SHUFFLE_QTY_COLUMN: W_ONHAND_QUANTITY_COLUMN}, inplace=True)
        print_df(df_OnHandQuantity, 'STEP 3 by 3.2 ____ df_OnHandQuantity .... final')
        
        # ====================> STEP3 by 3 (End)
    
    
    
    
        # ====================> STEP3 by 4 (Start) -> 매치코드 Intransit 재고 입력 -> df_ExpectedReceipts
        
        # df_in_Intransit > INTER_ETA_DATE_COLUMN 컬럼 변환 (문자열을 datetime 객체로 변환)
        df_in_intransit_shuffle[INTR_SHUFFLE_ETA_DATE_COLUMN] = pd.to_datetime(
            df_in_intransit_shuffle[INTR_SHUFFLE_ETA_DATE_COLUMN], format='%m/%d/%Y %I:%M:%S %p')
    
        # datetime 객체를 문자열로 변환(strftime은 datetime 객체를 문자열로 변환)
        df_in_intransit_shuffle[INTR_SHUFFLE_ETA_DATE_COLUMN] = df_in_intransit_shuffle[
            INTR_SHUFFLE_ETA_DATE_COLUMN].dt.strftime('%Y-%m-%d')
    
        # 4.1 df_ExpectedReceipts create
        df_ExpectedReceipts = pd.merge(df_in_intransit_shuffle , df_in_Time, how='inner', left_on=INTR_SHUFFLE_ETA_DATE_COLUMN, right_on=TIME_DAY_COLUMN)
    
        # 4.2 필요컬럼 발췌
        df_ExpectedReceipts = df_ExpectedReceipts[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN, INTR_SHUFFLE_QTY_COLUMN
        ]].drop_duplicates()
    
        # 4.3 컬럼명 변경
        df_ExpectedReceipts.rename(columns={INTR_SHUFFLE_QTY_COLUMN: W_EXPECTED_RECEIPTS_QUANTITY_COLUMN}, inplace=True)
        print_df(df_ExpectedReceipts, 'STEP 3 by 4.3 ____ df_ExpectedReceipts .... final')
        
        # ====================> STEP3 by 4 (End)
    
    
    
    
        # ====================> STEP3 by 5 (Start) -> Pre-alloc. Constraint Intransit  입력 > df_out_ExpectedReceipts
        
        # 5.1 OrderlineID 생성
        df_in_PreAllocDetailW[ORDERLINE_ID_COLUMN] = (
                'PAC_' + df_in_PreAllocDetailW[GROUP_ID_COLUMN].astype(str) + '@' +
                df_in_PreAllocDetailW[LOCATION_COLUMN] + '_' +
                df_in_PreAllocDetailW[TIME_WEEK_COLUMN].astype(str)
        )
    
        # 5.2 left 외부 조인 수행
        df_PreAllocDetaiItem = pd.merge(df_in_PreAllocDetailW, df_in_PreAllocItem, how='left',
                                        left_on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, LOCATION_COLUMN],
                                        right_on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, LOCATION_COLUMN], indicator=True)
        print_df(df_PreAllocDetaiItem, 'STEP 3 by 5.2 ____ df_PreAllocDetaiItem .... merge[df_in_PreAllocDetailW, df_in_PreAllocItem]')

        # 5.3 컬럼편집
        df_PreAllocDetaiItem.rename(columns={GROUP_ID_COLUMN+'_x': GROUP_ID_COLUMN}, inplace=True)
        df_PreAllocDetaiItem = df_PreAllocDetaiItem.drop(labels=[ITEM_COLUMN], axis=1)
        print_df(df_PreAllocDetaiItem, 'STEP 3 by 5.3 ____ df_PreAllocDetaiItem .... column modify')
    
        # 5.4 존재하지 않는 항목 필터링
        df_PreAllocDetaiItemResult = df_PreAllocDetaiItem[df_PreAllocDetaiItem['_merge'] == 'left_only']
        print_df(df_PreAllocDetaiItemResult, 'STEP 3 by 5.4 ____ df_PreAllocDetaiItemResult .... filter')
    
        df_PreAllocDetaiItemResult.rename(columns={
            PRE_ALLOC_CONST_DETAIL_W_CONST_QRT_COLUMN: W_EXPECTED_RECEIPTS_QUANTITY_COLUMN,
            ORDERLINE_ID_COLUMN: DOCUMENTS_ORDERLINEID_COLUMN,
            GROUP_ID_COLUMN: ITEM_COLUMN
        }, inplace=True)
    
        # 5.5 필요한 컬럼 선택
        df_PreAllocDetaiItemResult = df_PreAllocDetaiItemResult[df_ExpectedReceipts_columns]
        print_df(df_PreAllocDetaiItemResult, 'STEP 3 by 5.5 ____ df_PreAllocDetaiItemResult .... final')
    
        # ====================> STEP3 by 5 (End)
    
        step('=====> STEP3 End')
        
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        df_ExpectedReceipts = pd.concat([df_ExpectedReceipts, df_PreAllocDetaiItemResult], ignore_index=True)
    
        # 컬럼타입 재정의
        columns_object = [TIME_WEEK_COLUMN]
        for column in columns_object:
            df_OnHandQuantity[column] = df_OnHandQuantity[column].astype(object)
            df_ExpectedReceipts[column] = df_ExpectedReceipts[column].astype(object)
    
    
        df_out_OnHandQuantity = rename_and_delete_df(df_OnHandQuantity)
        df_out_ExpectedReceipts = rename_and_delete_df(df_ExpectedReceipts)
        
        df_out_OnHandQuantity[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ExpectedReceipts[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')
        
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_OnHandQuantity, 'output table create .... df_out_OnHandQuantity', True)
        print_df(df_out_ExpectedReceipts, 'output table create .... df_out_ExpectedReceipts', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_OnHandQuantity = pd.DataFrame(columns=df_OnHandQuantity_columns)
        df_out_ExpectedReceipts = pd.DataFrame(columns=df_ExpectedReceipts_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_OnHandQuantity = pd.DataFrame(columns=df_OnHandQuantity_columns)
        df_out_ExpectedReceipts = pd.DataFrame(columns=df_ExpectedReceipts_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
