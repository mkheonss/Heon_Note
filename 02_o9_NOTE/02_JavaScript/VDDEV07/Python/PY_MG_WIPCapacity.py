"""

* 프로그램명
    - PY_MG_WIPCapacity

* 내용
     - Resource까지 사전 할당하는 WIP
    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.06.26 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary
    Step1.확정생산계획 (in_MfgPlan) 라인 Pre-Allocation


* Input Table
    - df_in_MfgPlan = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Finish Date], Measure.[Mfg Plan_Line Name], Measure.[Mfg Plan_Open Qty], Measure.[Mfg Plan_Order Line ID], Measure.[Mfg Plan_Plan ID], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_Rank No], Measure.[Mfg Plan_Status], Measure.[Mfg Plan_To Site ID],Measure.[Dummy]}) on column;
                     [ Select ( &CWV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Finish Date], Measure.[Mfg Plan_Line Name], Measure.[Mfg Plan_Open Qty], Measure.[Mfg Plan_Order Line ID], Measure.[Mfg Plan_Plan ID], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_Rank No], Measure.[Mfg Plan_Status], Measure.[Mfg Plan_To Site ID]}) on column;]
    - df_in_ItemSiteAsn  = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage],Measure.[Dummy]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
                         [ Select (&MPV * &MFLocation * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);]
    - df_in_BOMMaster = Select ([Version].[Version Name] *  [Activity3].[Activity3] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Location].[Location] * [Item].[Item] ) on row, ({ Measure.[W Material Production Association], Measure.[W Material Production Quantity Per],Measure.[Dummy]}) on column ;
                        [ Select (&MPV  *  [Activity3].[Activity3] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Location].[Location] * [Item].[Item] ) on row, ({ Measure.[W Material Production Association], Measure.[W Material Production Quantity Per]}) on column ;]
    - df_in_time = select ([Time].[Week] * [Time].[Day]);
    - df_in_TackTime = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn],Measure.[Dummy]}) on column  where {  Measure.[Tact Time_Valid Asn] == true } ;

* 데이터 삭제
    DELETE DATA FOR MODEL [001.021W Solver Inputs WIP Capacity] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_WIPCapacity = Select ([Version].[Version Name].[CWV_MP] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * [Resource].[Resource] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[W Capacity Consumption WIP MPBO Override to SCS], Measure.[W Locked WIP Capacity Consumption Quantity], Measure.[W WIP Capacity Consumption Quantity]}) on column ;


* 테스트 스크립트
    EXEC plugin instance [PY_MG_WIPCapacity] for Measures {[W WIP Capacity Consumption Quantity]} using scope ( [Version].[Version Name].filter(#.Name in {"CurrentWorkingView", "CWV_MP"})  * &PlanningHorizon * &MFLocation ) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

"""

import decimal
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

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_WIPCapacity'
is_local = com.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
Logger_level = com.G_log_level


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

def print_df(df, df_name, _localFlag=True):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)

def note(string, p_log_level=Logger_level.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)

def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')


# Logger.debug(f'[START] {str_instance}')
# Logger.Start()
# Logger.Step(p_step_no=0, p_step_desc=f'plugin Execution Start')

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
    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_MfgPlan = read_csv_file("df_in_MfgPlan")
        df_in_ItemSiteAsn = read_csv_file('df_in_ItemSiteAsn')
        df_in_BOMMaster = read_csv_file('df_in_BOMMaster')
        df_in_time = read_csv_file('df_in_Time')
        df_in_TactTime = read_csv_file('df_in_TactTime')


    # if df_in_MfgPlan.empty:
    #     raise Exception("Exception: df_in_ConstraintGroupDetail is empty")
    #
    # if df_in_ItemSiteAsn.empty:
    #     raise Exception("Exception: df_in_ConstraintGroupDetailW is empty")
    #
    # if df_in_BOMMaster.empty:
    #     raise  Exception("Exception df_in_BOMMaster is empty")
    #
    # if df_in_time.empty:
    #     raise  Exception("Exception df_in_time is empty")
    #
    # if df_in_TactTime.empty:
    #     raise Exception("Exception df_in_TactTime is empty")

    # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #     paramOutVersion = PARAM_OUTVERSION_VALUE

    print_df(df_in_MfgPlan,'df_in_MfgPlan')
    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn')
    print_df(df_in_BOMMaster, 'df_in_BOMMaster')
    print_df(df_in_time, 'df_in_Time')
    print_df(df_in_TactTime, 'df_in_TactTime')


    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    ITEM_COLUMN = 'Item.[Item]'
    ORDER_LINE_ID_COLUMN = 'Documents.[OrderlineID]'
    Activity1_COLUMN = "Activity1.[Activity1]"
    Activity2_COLUMN = "Activity2.[Activity2]"
    Activity3_COLUMN = "Activity3.[Activity3]"
    TIME_DAY_COLUMN = "Time.[Day]"
    TIME_WEEK_COLUMN = 'Time.[Week]'
    RESOURCE_COLUMN = 'Resource.[Resource]'
    CWV_MP = 'CWV_MP'
    CWV = 'CurrentWorkingView'
    Line_COLUMN = 'Line.[Line]'

    W_Production_WIP_MPBO_Override_to_SCS = 'W Production WIP MPBO Override to SCS'
    W_WIP_Material_Production_Quantity = 'W WIP Material Production Quantity'
    W_Capacity_Consumption_WIP_MPBO_Override_to_SCS = 'W Capacity Consumption WIP MPBO Override to SCS'
    W_Locked_WIP_Capacity_Consumption_Quantity = 'W Locked WIP Capacity Consumption Quantity'
    W_WIP_Capacity_Consumption_Quantity = 'W WIP Capacity Consumption Quantity'

    Mfg_Plan_Finish_Date = 'Mfg Plan_Finish Date'
    Mfg_Plan_Open_Qty = 'Mfg Plan_Open Qty'
    New_Date = 'New Date'
    New_Date_Delivery_Date = 'New Date Delivery Date'
    Mfg_Plan_Line_Name = 'Mfg Plan_Line Name'
    Tact_Time_Time = 'Tact Time_Time'

    Logger.Step(p_step_no=100, p_step_desc=f'in Table Log')
    # 입력 변수 확인용 로그
    Logger.Note(p_note=f'paramOutVersion : {paramOutVersion}', p_log_level=Logger_level.debug())
    # Logger.PrintDF(p_df=df_in_MfgPlan, p_df_name='df_in_MfgPlan info',
    #                p_log_level=Logger_level.debug(), p_format=1)
    # Logger.Step(p_step_no=110, p_step_desc=f'df_in_MfgPlan Table Log')
    # Logger.PrintDF(p_df=df_in_ItemSiteAsn, p_df_name='df_in_ItemSiteAsn info',
    #                p_log_level=Logger_level.debug(), p_format=1)
    # Logger.Step(p_step_no=120, p_step_desc=f'df_in_ItemSiteAsn Table Log')
    # Logger.PrintDF(p_df=df_in_BOMMaster, p_df_name=' df_in_BOMMaster info',
    #                p_log_level=Logger_level.debug(), p_format=1)
    # Logger.Step(p_step_no=130, p_step_desc=f'df_in_BOMMaster Table Log')
    # Logger.PrintDF(p_df=df_in_time, p_df_name='df_in_Time info',
    #                p_log_level=Logger_level.debug(), p_format=1)
    # Logger.Step(p_step_no=140, p_step_desc=f'df_in_time Table Log')
    # Logger.PrintDF(p_df=df_in_TactTime, p_df_name='df_in_TactTime info',
    #                p_log_level=Logger_level.debug(), p_format=1)
    # Logger.Step(p_step_no=140, p_step_desc=f'df_in_TactTime Table Log')
    ################################################################################################################
    # Step 1. (1) df_in_ItemSiteAsn 중복값 삭제 (Location & Item)
    #         (2) df_in_MfgPlan 필터링
    ################################################################################################################
    df_in_ItemSiteAsn = df_in_ItemSiteAsn[df_in_ItemSiteAsn[VERSION_NAME_COLUMN]==PARAM_OUTVERSION_VALUE]
    Location_series = df_in_ItemSiteAsn[LOCATION_COLUMN].unique()
    Item_series = df_in_ItemSiteAsn[ITEM_COLUMN].unique()
    df_in_MfgPlan = df_in_MfgPlan[df_in_MfgPlan[VERSION_NAME_COLUMN] == CWV]
    df_in_MfgPlan[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE
    df_in_MfgPlan = df_in_MfgPlan[
        (df_in_MfgPlan[LOCATION_COLUMN].isin(Location_series)) & (df_in_MfgPlan[ITEM_COLUMN].isin(Item_series))]

    df_in_BOMMaster = df_in_BOMMaster[df_in_BOMMaster[VERSION_NAME_COLUMN]==PARAM_OUTVERSION_VALUE]
    df_mergeA = df_in_MfgPlan.merge(df_in_BOMMaster, on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN],
                                    how='inner')

    print_df(df_mergeA,'df_mergeA 정보 확인 _ Step 1' )

    Logger.Step(p_step_no=200, p_step_desc=f'df_mergeA Table Log')
    ################################################################################################################
    # Step 2. (1) df_mergeA & df_in_time merge (df_mergeB 생성)
    ################################################################################################################
    df_mergeA[Mfg_Plan_Finish_Date] = df_mergeA[Mfg_Plan_Finish_Date].apply(
        lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_mergeA[New_Date] = pd.to_datetime(df_mergeA[Mfg_Plan_Finish_Date])
    df_mergeA[New_Date] = df_mergeA[New_Date].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_mergeA[New_Date] = df_mergeA[New_Date].astype(str)
    df_in_time[New_Date] = pd.to_datetime(df_in_time[TIME_DAY_COLUMN])
    df_in_time[New_Date] = df_in_time[New_Date].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    df_in_time[New_Date] = df_in_time[New_Date].astype(str)

    df_mergeB = df_mergeA.merge(df_in_time, on=New_Date, how='inner')
    print_df(df_mergeB,'df_mergeB 정보 _ Step 2')
    Logger.Step(p_step_no=300, p_step_desc=f'df_mergeB Table Log')
    ################################################################################################################
    # Step 3. (1) Mfg df_mergeB 와 df_in_TactTime merge
    #         (2) df_out_WIPCapacity 전처리
    ################################################################################################################
    df_mergeB.rename(columns={Mfg_Plan_Line_Name : Line_COLUMN},inplace=True)
    df_mergeC = df_mergeB.merge(df_in_TactTime, on=[VERSION_NAME_COLUMN,ITEM_COLUMN, LOCATION_COLUMN ,Line_COLUMN],
                                how='left')
    df_mergeC[RESOURCE_COLUMN] = df_mergeC[Line_COLUMN]
    df_mergeC[W_Capacity_Consumption_WIP_MPBO_Override_to_SCS] =''
    df_mergeC[W_Locked_WIP_Capacity_Consumption_Quantity] =''
    df_mergeC[W_WIP_Capacity_Consumption_Quantity] = (np.where(df_mergeC[Tact_Time_Time].isna(), 1,
                                                               df_mergeC[Tact_Time_Time])) * df_mergeC[
                                                         Mfg_Plan_Open_Qty]
    df_out_WIPCapacity = df_mergeC[[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, Activity1_COLUMN, Activity2_COLUMN,
                                    Activity3_COLUMN, RESOURCE_COLUMN,LOCATION_COLUMN, ORDER_LINE_ID_COLUMN,
                                    W_Capacity_Consumption_WIP_MPBO_Override_to_SCS,
                                    W_Locked_WIP_Capacity_Consumption_Quantity, W_WIP_Capacity_Consumption_Quantity]]

    print_df(df_out_WIPCapacity, 'df_out_WIPCapacity _ Step 3')
    Logger.Step(p_step_no=300, p_step_desc=f'df_out_WIPCapacity Table Log')
    ###############################################################################################################
    # Step 7. (1) 최종 Out_Put Save
    ################################################################################################################

    if is_local:
        Logger.Step(p_step_no=400, p_step_desc=f'Final Output Tabel create')
        save_csv_file(df_out_WIPCapacity, 'df_out_WIPCapacity')

    row_count, col_count = df_out_WIPCapacity.shape
    Logger.Note(p_note=f'df_out_InputsCapacity rows : {row_count} , Columns : {col_count}',
                      p_log_level=Logger_level.info())

except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg, p_log_level=Logger_level.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_WIPCapacity = pd.DataFrame([], columns=[])
    # df_out_NewModelSumStatus = pd.DataFrame([], columns=[])

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