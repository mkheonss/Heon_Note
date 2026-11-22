"""

* 프로그램명
    - PY_MG_WIP

* 내용
    - MP Engine 수행을 위한 확정생산 및 선적계획 Input
    - MP Plan Batch Procedure에서 Call 하는 Program
    - 확정생산 및 선적에 해당하는 Document Dimension의 Documents.[OrderlineID]는 이미 LS에 일괄 생성되어있음.
    - 즉, 별도 OrderlineID Member 생성 필요 없음.
    - GSCM에서 I/F 되어온 확정계획 Measure Group은 현재 Plan 에 반영해야할 OrderlineID 만 존재함. (GSCM : Truncate * Insert)

    - Data Source(GSCM)
    - VMG_DISTORDER(GSCM) > Distribution Order(LS)
    - VMG_MFGPLAN(GSCM) > Mfg Plan(LS)

* 변경이력
    - 2024.06.18 / ybest7.park (박병훈) / Create

* Input
    - in_DistributionOrder = pd.read_csv(' .csv')
    - in_ProductionOrder = pd.read_csv(' .csv')


* Flow Summary



* Input Table
     - df_in_DistributionOrder = Select ([Version].[Version Name] * [Item].[Item] * [Documents].[OrderlineID] * [BOD].[BOD Name] ) on row, ({Measure.[Dist Order Shuffle_Plan ID], Measure.[Dist Order Shuffle_Sales ID], Measure.[Dist Order_From Site ID], Measure.[Dist Order_Order Line ID], Measure.[Dist Order_Plan ID], Measure.[Dist Order_SS Delivery Date],Measure.[Dist Order_SS Qty],Measure.[Dist Order_SS Startdate], Measure.[Dist Order_Sales ID], Measure.[Dist Order_To Site ID]}) on column  ;
    - df_in_MfgPlan = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Finish Date], Measure.[Mfg Plan_Line Name], Measure.[Mfg Plan_Open Qty], Measure.[Mfg Plan_Order Line ID], Measure.[Mfg Plan_Plan ID], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_Rank No], Measure.[Mfg Plan_Status], Measure.[Mfg Plan_To Site ID]}) on column;
    - df_in_BOD = Select ([BOD].[BOD Name] * [BOD].[From Site ID] * [BOD].[To Site ID] * [BOD].[Transport Mode]) ;
    - df_in_time = select ( &PlanningHorizon * [Time].[Day]);
* 데이터 삭제
    DELETE DATA FOR MODEL [001.021W Solver Inputs WIP] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_BODWIPConsumption = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,({Measure.[W Consumption WIP MPBO Override to SCS],Measure.[W Production WIP MPBO Override to SCS],Measure.[W WIP Material Consumption Quantity],Measure.[W WIP Material Production Quantity]}) on column;
    - df_out_BODWIPProduction = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Consumption WIP MPBO Override to SCS],Measure.[W Production WIP MPBO Override to SCS],Measure.[W WIP Material Consumption Quantity], Measure.[W WIP Material Production Quantity]}) on column;
    - df_out_BOMWIPProduction = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID]* [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Consumption WIP MPBO Override to SCS],Measure.[W Production WIP MPBO Override to SCS],Measure.[W WIP Material Consumption Quantity], Measure.[W WIP Material Production Quantity]} ) on column ;


* 테스트 스크립트
    EXEC plugin instance [PY_MG_WIP] for measures {[CM Artificial Base Capacity Override]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView"}) * &PlanningHorizon) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;
"""

########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
from NSCMCommon import VDCommon as vdCommon
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
import warnings

from dateutil import parser as date_parser
from typing import Union
from pandas.tseries.offsets import MonthEnd
########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_WIP'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=True):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')

# Logger.debug(f'[START] {str_instance}')
# Logger.Start()
# note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
# step(0, '===================== plugin Execution Start =====================')
# tracemalloc.start()
try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, Logger, com.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if com.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(com.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    step(100, '=====> STEP 1(Start) : Input Date Frame Read')

    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_DistributionOrder = read_csv_file('df_in_DistributionOrder')
        df_in_MfgPlan = read_csv_file("df_in_MfgPlan")
        df_in_BOD = read_csv_file('df_in_BOD')
        df_in_time = read_csv_file('df_in_Time')


    # if df_in_DistributionOrder.empty:
    #     raise Exception("Exception: df_in_DistributionOrder is empty")
    #
    # if df_in_MfgPlan.empty:
    #     raise Exception("Exception: df_in_MfgPlan is empty")
    #
    # if df_in_BOD.empty:
    #     raise  Exception("Exception df_in_BOD is empty")
    #
    # if df_in_time.empty:
    #     raise  Exception("Exception df_in_time is empty")

    # # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #     paramOutVersion = PARAM_OUTVERSION_VALUE

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_DistributionOrder, 'df_in_DistributionOrder')
    print_df(df_in_MfgPlan, 'df_in_MfgPlan')
    print_df(df_in_BOD, 'df_in_BOD')
    print_df(df_in_time, 'df_in_time')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    ITEM_COLUMN = 'Item.[Item]'
    ORDER_LINE_ID_COLUMN = 'Documents.[OrderlineID]'
    BOD_NAME_COLUMN ='BOD.[BOD Name]'
    Activity1_COLUMN = "Activity1.[Activity1]"
    Activity2_COLUMN = "Activity2.[Activity2]"
    Activity3_COLUMN = "Activity3.[Activity3]"
    TRANSPORTMODE_COLUMN = 'BOD.[Transport Mode]'
    TIME_DAY_COLUMN = "Time.[Day]"
    TIME_WEEK_COLUMN = 'Time.[Week]'
    TO_SITE_ID_COLUMN = 'BOD.[To Site ID]'
    RESOURCE_COKUMN = 'Resource.[Resource]'
    Mfg_Plan_BOM_Version = 'Mfg Plan_BOM Version'


    Dist_Order_SS_Startdate = "Dist Order_SS Startdate"
    Dist_Order_SS_Startdate_Week = "Dist Order_SS Startdate Week"
    Dist_Order_From_Site_ID = "Dist Order_From Site ID"
    Dist_Order_TO_Site_ID = "Dist Order_To Site ID"
    Dist_Order_SS_Delivery_Date = 'Dist Order_SS Delivery Date'
    Dist_Order_SS_Qty = 'Dist Order_SS Qty'

    W_WIP_Material_Consumption_Quantity = 'W WIP Material Consumption Quantity'
    W_Production_WIP_MPBO_Override_to_SCS = 'W Production WIP MPBO Override to SCS'
    W_WIP_Material_Production_Quantity = 'W WIP Material Production Quantity'
    W_Consumption_WIP_MPBO_Override_to_SCS = 'W Consumption WIP MPBO Override to SCS'
    W_Capacity_Consumption_WIP_MPBO_Override_to_SCS = 'W Capacity Consumption WIP MPBO Override to SCS'
    W_Locked_WIP_Capacity_Consumption_Quantity = 'W Locked WIP Capacity Consumption Quantity'
    W_WIP_Capacity_Consumption_Quantity = 'W WIP Capacity Consumption Quantity'
    W_WIP_Material_Consumption_Quantit = 'W WIP Material Consumption Quantit'

    Mfg_Plan_Finish_Date = 'Mfg Plan_Finish Date'
    Mfg_Plan_Open_Qty = 'Mfg Plan_Open Qty'
    New_Date = 'New Date'
    New_Date_Delivery_Date = 'New Date Delivery Date'
    Mfg_Plan_Line_Name = 'Mfg Plan_Line Name'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 1. (1) df_in_DistributionOrder & df_in_BOD & df_in_time merge
    #         (2) on = BOD Name & [Time.[Day] , Dist Order_SS Startdate]
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    df_mergeA = df_in_DistributionOrder.merge(df_in_BOD, on=BOD_NAME_COLUMN, how='inner')
    df_mergeA[Dist_Order_SS_Startdate] = df_mergeA[Dist_Order_SS_Startdate].apply(
        lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_mergeA[New_Date] = pd.to_datetime(df_mergeA[Dist_Order_SS_Startdate])
    df_mergeA[New_Date] = df_mergeA[New_Date].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_mergeA[New_Date] = df_mergeA[New_Date].astype(str)

    df_in_time[New_Date] = pd.to_datetime(df_in_time[TIME_DAY_COLUMN])
    df_in_time[New_Date] = df_in_time[New_Date].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_in_time[New_Date] = df_in_time[New_Date].astype(str)

    df_mergeA = df_mergeA.merge(df_in_time, on=New_Date, how='inner')

    print_df(df_mergeA, 'df_mergeA Step-3')

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2. (1) Dist Order_SS Startdate → Time Week로 변환
    #         (2) BOD Consume 기준 입력 (BOD Name → Activity1, Transport Mode → Activity2, Item → Activity3
    #         (3) 변수 설정  및 Out Data Frame 순서 설정
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : input data machining')

    df_mergeA[Dist_Order_SS_Startdate] = df_mergeA[TIME_WEEK_COLUMN]
    df_mergeA[LOCATION_COLUMN] = df_mergeA[Dist_Order_From_Site_ID]
    df_mergeA[Activity1_COLUMN] = df_mergeA[BOD_NAME_COLUMN]
    df_mergeA[Activity2_COLUMN] = df_mergeA[TRANSPORTMODE_COLUMN]
    df_mergeA[Activity3_COLUMN] = df_mergeA[ITEM_COLUMN]
    df_mergeA[W_WIP_Material_Consumption_Quantity] = df_mergeA[Dist_Order_SS_Qty]
    df_mergeA[W_Consumption_WIP_MPBO_Override_to_SCS] = np.nan
    df_mergeA[W_Production_WIP_MPBO_Override_to_SCS] = np.nan
    df_mergeA[W_WIP_Material_Production_Quantity] = np.nan
    df_out_BODWIPConsumption = df_mergeA[[VERSION_NAME_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN,LOCATION_COLUMN,
                                          ORDER_LINE_ID_COLUMN,Activity1_COLUMN,Activity2_COLUMN,Activity3_COLUMN,
                                          W_Consumption_WIP_MPBO_Override_to_SCS,
                                          W_Production_WIP_MPBO_Override_to_SCS,W_WIP_Material_Consumption_Quantity,
                                          W_WIP_Material_Production_Quantity]]

    df_out_BODWIPConsumption = df_out_BODWIPConsumption.copy()

    df_out_BODWIPConsumption[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE

    print_df(df_out_BODWIPConsumption, 'df_out_BODWIPConsumption Step 4')

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) df_out_BODWIPProduction 생성
    #         (2) Location 설정 값 변경
    #         (3) df_out_BODWIPProduction의  Out Data Frame 순서 설정
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : input data machining')

    df_mergeB = df_in_DistributionOrder.merge(df_in_BOD, on=BOD_NAME_COLUMN, how='inner')
    df_mergeB[Dist_Order_SS_Delivery_Date] = df_mergeB[Dist_Order_SS_Delivery_Date].apply(
        lambda x: x.split(' ')[0] if isinstance(x, str) else x)

    df_mergeB[New_Date] = pd.to_datetime(df_mergeB[Dist_Order_SS_Delivery_Date])
    df_mergeB[New_Date] = df_mergeA[New_Date].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_mergeB[New_Date] = df_mergeA[New_Date].astype(str)

    df_mergeB = df_mergeB.merge(df_in_time, on=New_Date, how='inner')

    df_mergeB[LOCATION_COLUMN] = df_mergeB[Dist_Order_From_Site_ID]
    df_mergeB[Activity1_COLUMN] = df_mergeB[BOD_NAME_COLUMN]
    df_mergeB[Activity2_COLUMN] = df_mergeB[TRANSPORTMODE_COLUMN]
    df_mergeB[Activity3_COLUMN] = df_mergeB[ITEM_COLUMN]
    df_mergeB[W_WIP_Material_Consumption_Quantity] = df_mergeB[Dist_Order_SS_Qty]
    df_mergeB[W_Consumption_WIP_MPBO_Override_to_SCS] = np.nan
    df_mergeB[W_Production_WIP_MPBO_Override_to_SCS] = np.nan
    df_mergeB[W_WIP_Material_Production_Quantity] = np.nan
    df_out_BODWIPProduction = df_mergeB[[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN,
                                         ORDER_LINE_ID_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN,
                                         W_Consumption_WIP_MPBO_Override_to_SCS,
                                         W_Production_WIP_MPBO_Override_to_SCS, W_WIP_Material_Consumption_Quantity,
                                         W_WIP_Material_Production_Quantity]]

    df_out_BODWIPProduction[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE

    print_df(df_out_BODWIPProduction, 'df_out_BODWIPProduction Step 4')

    step(450, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) df_in_MfgPlan & df_in_time 을 merge하여 df_out_BOMWIPProduction 생성
    #         (2) mer
    #         (3) 변수 설정  및 Out Data Frame 순서 설정
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : input data machining')

    df_in_MfgPlan[Mfg_Plan_Finish_Date] = df_in_MfgPlan[Mfg_Plan_Finish_Date].apply(
        lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_in_MfgPlan[New_Date] = pd.to_datetime(df_in_MfgPlan[Mfg_Plan_Finish_Date])
    df_in_MfgPlan[New_Date] = df_in_MfgPlan[New_Date].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_in_MfgPlan[New_Date] = df_in_MfgPlan[New_Date].astype(str)

    df_in_time[New_Date] = pd.to_datetime(df_in_time[TIME_DAY_COLUMN])
    df_in_time[New_Date] = df_in_time[New_Date].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_in_time[New_Date] = df_in_time[New_Date].astype(str)

    df_out_BOMWIPProduction = df_in_MfgPlan.merge(df_in_time, on=New_Date, how='inner')
    df_out_BOMWIPProduction[Activity1_COLUMN] = df_out_BOMWIPProduction[ITEM_COLUMN] + '_' + \
                                                df_out_BOMWIPProduction[Mfg_Plan_BOM_Version]
    df_out_BOMWIPProduction[Activity2_COLUMN] = 'RT_' + df_out_BOMWIPProduction[ITEM_COLUMN] + '_' + \
                                                df_out_BOMWIPProduction[Mfg_Plan_BOM_Version] + '@' + \
                                                df_out_BOMWIPProduction[LOCATION_COLUMN]
    df_out_BOMWIPProduction[Activity3_COLUMN] = df_out_BOMWIPProduction[ITEM_COLUMN]
    df_out_BOMWIPProduction[W_Consumption_WIP_MPBO_Override_to_SCS] = np.nan
    df_out_BOMWIPProduction[W_WIP_Material_Consumption_Quantity] = np.nan
    df_out_BOMWIPProduction[W_Production_WIP_MPBO_Override_to_SCS] = np.nan
    df_out_BOMWIPProduction[W_WIP_Material_Production_Quantity] = df_out_BOMWIPProduction[Mfg_Plan_Open_Qty]

    df_out_BOMWIPProduction = df_out_BOMWIPProduction[[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN,
                                                       LOCATION_COLUMN, ORDER_LINE_ID_COLUMN, Activity1_COLUMN,
                                                       Activity2_COLUMN, Activity3_COLUMN,
                                                       W_Consumption_WIP_MPBO_Override_to_SCS,
                                                       W_Production_WIP_MPBO_Override_to_SCS,
                                                       W_WIP_Material_Consumption_Quantity,
                                                       W_WIP_Material_Production_Quantity]]

    df_out_BOMWIPProduction[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE

    print_df(df_out_BOMWIPProduction, 'df_out_BOMWIPProduction')
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 7. (1) 최종 Out_Put Save
    ################################################################################################################
    step(700, '=====> STEP 7(Start) : input data machining')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_BODWIPConsumption, 'df_out_BODWIPConsumption')
        save_csv_file(df_out_BODWIPProduction, 'df_out_BODWIPProduction')
        save_csv_file(df_out_BOMWIPProduction, 'df_out_BOMWIPProduction')

    row_count, col_count = df_out_BODWIPConsumption.shape
    note(f'=====> Final df_out_BODWIPConsumption rows : {row_count} , Columns : {col_count}')

    row_count, col_count = df_out_BODWIPProduction.shape
    note(f'=====> Final df_out_BODWIPProduction rows : {row_count} , Columns : {col_count}')

    row_count, col_count = df_out_BOMWIPProduction.shape
    note(f'=====> Final df_out_BOMWIPProduction rows : {row_count} , Columns : {col_count}')

    step(700, '=====> STEP 7(End) : Check memory usage & runtime')
except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_BODWIPConsumption = pd.DataFrame([], columns=[])
    df_out_BODWIPProduction = pd.DataFrame([], columns=[])
    df_out_BOMWIPProduction = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(500, '===================== plugin Execution End =====================')

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    Logger.Finish()
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
