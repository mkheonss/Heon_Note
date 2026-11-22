"""

* 프로그램명
    - PY_MG_Demand_REG

* 내용
    - MP Engine 수행을 위한 Netted Demand Input
    - MP Plan Batch Procedure에서 Call 하는 Program
    - Demand Dimension의 Demand.[DemandID]는 이미 LS에 일괄 생성되어있음.
    - 즉, 별도 DemandID Member 생성 필요 없음.
    - GSCM에서 I/F 되어온 Demand Measure Group은 현재 Plan 에 반영해야할 DemandID 만 존재함. (GSCM : Truncate * Insert)

    - Data Source
    - GSCM PG : SP_MG_DEMAND_REG
    - MG_DEMAND(VMG_DEMAND)

* 변경이력
- 2024.06.17 / ybest7.park / Create

* Input
- in_Demand = pd.read_csv(' .csv')

* Flow Summary
     Step1. GSCM에서 I/F 온 MG : Demand W 초기 데이타 Insert

 * 주요 Logic (Data 처리)
    Step1. in_Demand 결과 Count가 0 이면, Logger.warn(in_Demand Query Count : 0)
    Step2. 001.018W Solver Inputs Demand Time Granularity

        003.006W Demand Time Granularity Inputs   : W Demand Quantity

    -  Insert Measure Group

        . W Demand Quantity : Demand 수량, in_Demand - Dmd W_Qty
        . W Demand Quantity to SCS : 엔진에 반영되는 Demand 수량, in_Demand  - Dmd W_Qty
        . W Demand Priority : 우선순위, in_Demand  - Dmd W_Prty
        . W Demand Build Late Limit : Default = 0    > 별도 LS에서 인자로 관리예정
        . W Demand Build Ahead Limit : Default = 0 > 추가중
        . W Demand Debug Flag : Default = 0
        . W Demand Plan Date Offset : Default = 0
        . W Demand Fulfilment Policy : Default =  'MULTIPLE'
        . W Demand Split : Default =  'FALSE'   > 별도 LS에서 인자로 관리예정
        . W Demand SS PreBuild : Default = 0  > 별도 LS에서 인자로 관리예정
        . W Demand No Plan, in_Demand  - Dmd W_No Plan


* Script Parameter
    - param_outVersion : CWV_MP

* Input Table
    - df_in_Demand = Select ( [Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Ship To] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[Dmd W_BAL], Measure.[Dmd W_Cust Rank], Measure.[Dmd W_Dmd Rank], Measure.[Dmd W_Global Prty], Measure.[Dmd W_ID], Measure.[Dmd W_Leadtime Due], Measure.[Dmd W_Local Prty],Measure.[Dmd W_Measure Rank], Measure.[Dmd W_No Plan], Measure.[Dmd W_Plan ID], Measure.[Dmd W_Preference],Measure.[Dmd W_Prod Rank], Measure.[Dmd W_Prty], Measure.[Dmd W_Prty Seq], Measure.[Dmd W_Qty], Measure.[Dmd W_Week Rank]}) on column;
                    [Select ( &CWV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Ship To] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[Dmd W_BAL], Measure.[Dmd W_Cust Rank], Measure.[Dmd W_Dmd Rank], Measure.[Dmd W_Global Prty], Measure.[Dmd W_ID], Measure.[Dmd W_Leadtime Due], Measure.[Dmd W_Local Prty],Measure.[Dmd W_Measure Rank], Measure.[Dmd W_No Plan], Measure.[Dmd W_Plan ID], Measure.[Dmd W_Preference],Measure.[Dmd W_Prod Rank], Measure.[Dmd W_Prty], Measure.[Dmd W_Prty Seq], Measure.[Dmd W_Qty], Measure.[Dmd W_Week Rank]}) on column;]
* Output Table
    - df_out_Demand_Time_Granularity = Select ( &MPV* [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[W Demand Build Ahead Limit], Measure.[W Demand Build Late Limit], Measure.[W Demand Debug Flag], Measure.[W Demand Fair Share Priority], Measure.[W Demand Fulfilment Policy], Measure.[W Demand Incremental Flag], Measure.[W Demand Layer], Measure.[W Demand Leadtime Due], Measure.[W Demand Match Code], Measure.[W Demand Plan Date Offset],  Measure.[W Demand Priority from Netting],  Measure.[W Demand Quantity to SCS], Measure.[W Demand SS PreBuild], Measure.[W Demand Short Code], Measure.[W Demand Split]}) on column;

* 데이터 삭제
   - DELETE DATA FOR MODEL [001.018W Solver Inputs Demand Time Granularity] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
    EXEC plugin instance [PY_MG_Demand_REG] for measures {[W Demand Quantity]} using scope (&CWV) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), ("IncludeNullRows", "False"), (MaxConcurrency, 1 ),([Param.o9_sys_log_level], "DEBUG")} ;



"""
########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
import os.path
import time
import datetime
import decimal
import math
import traceback
import gc
import tracemalloc
import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_Demand_REG'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level
########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8")

def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    Logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)

def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)

def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')


Logger.debug(f'[START] {str_instance}')
Logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')
tracemalloc.start()

try:
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    step(100, '=====> STEP 1(Start) : Input Date Frame Read')

    PARAM_OUTVERSION_VALUE = "CWV_MP"
    # Value 변수 선언

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = "CWV_MP"

        df_in_Demand = read_csv_file("df_in_Demand")

    if df_in_Demand.empty:
        raise Exception("Exception: df_in_Demand is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_Demand, 'df_in_Demand')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수 선언
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    ITEM_COLUMN = 'Item.[Item]'
    TIME_WEEK_COLUMN = "Time.[Week]"
    CUSTOMER_GROUP_COLUMN = "Sales Domain.[Customer Group]"
    DEMAND_ID_COLUMN = "Demand.[DemandID]"
    DEMAND_TYPE_COLUMN = "Demand Type.[Demand Type]"
    SHIP_TO_COLUMN = "Sales Domain.[Ship To]"

    Dmd_W_Qty = "Dmd W_Qty"
    Dmd_W_No_Plan = "Dmd W_No Plan"
    Dmd_W_Prty = "Dmd W_Prty"
    Dmd_W_Leadtime_Due = 'Dmd W_Leadtime Due'
    Dmd_W_BAL = 'Dmd W_BAL'
    Dmd_W_Prty_Seq = 'Dmd W_Prty Seq'

    W_Demand_Quantity = "W Demand Quantity"
    W_Demand_Quantity_to_SCS = "W Demand Quantity to SCS"
    W_Demand_Build_Late_Limit = "W Demand Build Late Limit"
    W_Demand_Build_Ahead_Limit = "W Demand Build Ahead Limit"
    W_Demand_Debug_Flag = "W Demand Debug Flag"
    W_Demand_Plan_Date_Offset = "W Demand Plan Date Offset"
    W_Demand_Fulfilment_Policy = "W Demand Fulfilment Policy"
    W_Demand_Split = "W Demand Split"
    W_Demand_SS_PreBuild = "W Demand SS PreBuild"
    W_Demand_No_Plan = "W Demand No Plan"
    W_Demand_Priority_from_Netting = 'W Demand Priority from Netting'
    W_Demand_Priority = 'W Demand Priority'
    W_Demand_Leadtime_Due = 'W Demand Leadtime Due'
    W_Demand_Short_Code = 'W Demand Short Code'
    W_Demand_Incremental_Flag = 'W Demand Incremental Flag'
    W_Demand_Layer = 'W Demand Layer'
    W_Demand_Fair_Share_Priority = 'W Demand Fair Share Priority'
    W_Demand_Match_Code = 'W Demand Match Code'

    multiple = 'MULTIPLE'
    channel_short = 'CHANNEL_SHORT'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    df_in_Demand[CUSTOMER_GROUP_COLUMN] = df_in_Demand[SHIP_TO_COLUMN]
    df_in_Demand[W_Demand_Quantity] = df_in_Demand[Dmd_W_Qty]
    df_in_Demand[W_Demand_Quantity_to_SCS] = np.where(df_in_Demand[Dmd_W_No_Plan]==True, 0, df_in_Demand[Dmd_W_Qty])
    df_in_Demand[W_Demand_Priority_from_Netting] = df_in_Demand[Dmd_W_Prty]
    df_in_Demand[W_Demand_Priority] = df_in_Demand[Dmd_W_Prty_Seq]
    df_in_Demand[W_Demand_Leadtime_Due] = df_in_Demand[Dmd_W_Leadtime_Due]
    df_in_Demand[W_Demand_Build_Late_Limit] = 0
    df_in_Demand[W_Demand_Build_Ahead_Limit] = 0
    df_in_Demand[W_Demand_Short_Code] = np.where(df_in_Demand[Dmd_W_No_Plan]==True,channel_short,'')
    df_in_Demand[W_Demand_Debug_Flag] = 0
    df_in_Demand[W_Demand_Plan_Date_Offset] = 0
    df_in_Demand[W_Demand_Incremental_Flag] = ''
    df_in_Demand[W_Demand_Fulfilment_Policy] = multiple
    df_in_Demand[W_Demand_Layer] = ''
    df_in_Demand[W_Demand_Split] = False
    df_in_Demand[W_Demand_SS_PreBuild] = 0
    df_in_Demand[W_Demand_Fair_Share_Priority] = ''
    df_in_Demand[W_Demand_Match_Code] = ''
    df_in_Demand[W_Demand_Build_Ahead_Limit] = 0

    print_df(df_in_Demand, 'df_in_Demand')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # out DataFrame (df_out_Demand_Time_Granularity)설정
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    df_out_Demand_Time_Granularity = df_in_Demand.copy()
    df_out_Demand_Time_Granularity[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE
    df_out_Demand_Time_Granularity = df_out_Demand_Time_Granularity[
        [VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, CUSTOMER_GROUP_COLUMN, DEMAND_TYPE_COLUMN,
         DEMAND_ID_COLUMN, W_Demand_Build_Ahead_Limit, W_Demand_Build_Late_Limit, W_Demand_Debug_Flag,
         W_Demand_Fair_Share_Priority, W_Demand_Fulfilment_Policy, W_Demand_Incremental_Flag, W_Demand_Layer,
         W_Demand_Leadtime_Due, W_Demand_Match_Code, W_Demand_Plan_Date_Offset,W_Demand_Priority_from_Netting,
         W_Demand_Quantity_to_SCS, W_Demand_SS_PreBuild, W_Demand_Short_Code,W_Demand_Split, ]]

    print_df(df_out_Demand_Time_Granularity, 'df_out_Demand_Time_Granularity')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')
    ################################################################################################################
    # 최종 Output 테이블 만들기
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_Demand_Time_Granularity, 'df_out_Demand_Time_Granularity')

    row_count, col_count = df_out_Demand_Time_Granularity.shape
    note(f'=====> Final df_out_Demand_Time_Granularity rows : {row_count} , Columns : {col_count}')
    print_df(df_out_Demand_Time_Granularity, 'df_out_Demand_Time_Granularity')

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    raise Exception(e)

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(600, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()
