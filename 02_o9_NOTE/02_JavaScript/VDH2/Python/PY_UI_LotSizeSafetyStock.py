

"""

* 프로그램명
    - PY_UI_LotSizeSafetyStock.py

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.11.28 / ybest7.park (박병훈) / Create
- 2025.04.30 / ybest7.park (박병훈) / input qurey 수정 및 VD Common 적용
- 2025.05.19/ ybest7.park (박병훈) / df_in_LotSize input Query 수정 & Group By Grain 수정

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_Demand = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] * [Item].[Plan Group]) on row, ({Measure.[W Demand Quantity to SCS],Measure.[Dummy]}) on column where {Measure.[W Demand Quantity to SCS]>1};
   - df_in_DCInv =  Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Site Stage].filter(#.Name == "DC").relatedmembers([Location]) * [Documents].[OrderlineID] *[Item].[Plan Group] ) on row, ({Measure.[W Expected Receipts], Measure.[W OnHand Quantity],Measure.[Dummy]}) on column where {(Measure.[W Expected Receipts]>0) || (Measure.[W OnHand Quantity]>1)};
   # - df_in_DCHUBInv = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location].filter(#.relatedmembers([Site Stage]).element(0).Name == "DC") *[Documents].[OrderlineID]) on row, ({Measure.[W Expected Receipts],Measure.[Dummy]}) on column;
   - df_in_LotSize = Select ([Version].[Version Name] * [Location].[Site Stage].filter(#.Name =="DC").relatedmembers([Location]) * [Item].[Item Stage].[SET].relatedmembers("Item")* [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W LotSize Increment], Measure.[W Max LotSize], Measure.[W Min LotSize], Measure.[W Soft LotSize],Measure.[Dummy]}) on column;
   - df_in_TargetStock = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Item].[Plan Group]) on row, ({Measure.[W Quantity Min Target], Measure.[Dummy]}) on column;

* Output Table
    - df_out_TargetStock = Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item] * [Time].[Week] * [Location].[Location] ) on row, ({Measure.[W Quantity Min Target]}) on column;
* 테스트 스크립트
    EXEC plugin instance [PY_UI_LotSizeSafetyStock] for measures {[W Quantity Min Target]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;
    EXEC plugin instance [PY_UI_LotSizeSafetyStock] for measures {[W Quantity Min Target]} using scope (&MPV *[Item].[Plan Group].[1]) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;
    EXEC plugin instance [PY_UI_LotSizeSafetyStock] for measures {[W Quantity Min Target]} using scope (&MPV *[Item].[Plan Group].[2]) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;

* 데이터 삭제
    - DELETE DATA FOR MODEL [001.019W Solver Inputs Inventory Inputs] where {Version.[Version Name].[CWV_MP]};





실행 전 프로시져를 통해 MF Site 삭제  필요

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

from dateutil import parser as date_parser
from typing import Union
import warnings

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_LotSizeSafetyStock'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level
paramOutVersion = 'CWV_MP'
########################################################################################################################
# logic start
########################################################################################################################
class CustomException(Exception):
    pass

def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )

def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)

def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)

def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')

def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, Logger, is_local, log_path)


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


def datetime_check_series(date_series):
    # 가능한 형식들을 순서대로 시도
    date_formats = ['%m/%d/%Y %I:%M:%S %p', '%Y/%m/%d %I:%M:%S %p', '%Y-%m-%d %H:%M:%S']

    # 모든 시도가 실패했을 때 NaT로 초기화
    parsed_dates = pd.Series(pd.NaT, index=date_series.index)

    for fmt in date_formats:
        # 형식을 시도하여 변환하고, NaT 값이 없는 경우에 대해서만 변환을 유지
        new_dates = pd.to_datetime(date_series, format=fmt, errors='coerce')
        parsed_dates = parsed_dates.combine_first(new_dates)

    return parsed_dates

note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')
tracemalloc.start()

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
    # # Value 변수 선언
    # PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_Demand = read_csv_file('df_in_Demand')
        df_in_DCInv = read_csv_file('df_in_DCInv')
        # df_in_DCHUBInv = read_csv_file('df_in_DCHUBInv')
        df_in_LotSize = read_csv_file('df_in_LotSize')
        df_in_TargetStock = read_csv_file('df_in_TargetStock')

    # if df_in_SalesPlan.empty:
    #     raise Exception("Exception: df_in_SalesPlan is empty")
    # # if df_in_SalesAct.empty:
    # #     raise Exception("Exception: df_in_SalesAct is empty")
    # if df_in_SalesHrcy.empty:
    #     raise Exception("Exception: df_in_SalesHrcy is empty")

    # note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_Demand, 'df_in_Demand',True)
    print_df(df_in_DCInv, 'df_in_DCInv',True)
    # print_df(df_in_DCHUBInv, 'df_in_DCHUBInv')
    print_df(df_in_LotSize, 'df_in_LotSize',True)
    print_df(df_in_TargetStock, 'df_in_TargetStock',True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Item_COLUMN = 'Item.[Item]'
    TimeWeek_COLUMN = 'Time.[Week]'
    Location_COLUMN = 'Location.[Location]'
    Sales_Domain_Customer_Group_COLUMN = 'Sales Domain.[Customer Group]'
    Demand_Type_COLUMN = 'Demand Type.[Demand Type]'
    Demand_ID_COLUMN = 'Demand.[DemandID]'
    Documents_OrderlineID_COLUMN = 'Documents.[OrderlineID]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'

    W_Demand_Quantity_to_SCS = 'W Demand Quantity to SCS'
    W_Expected_Receipts = 'W Expected Receipts'
    W_OnHand_Quantity = 'W OnHand Quantity'
    BOD_Item_Multi_Lot_Qty = 'BOD Item_Multi Lot Qty'
    W_Target_Inventory = 'W Target Inventory'
    W_Quantity_Min_Target = "W Quantity Min Target"

    EOH_Target = 'EOH Target'
    Initial_stock = 'initial stock'
    Demand_cumsum = 'demand_cumsum'
    Inventory_qty = 'inventory_qty'
    Pre_inventory_qty = 'pre inventory_qty'
    Net_Demand = 'Net Demand'
    Net_Demand_Cumsum = 'Net Demand Cumsum'
    Min_Production = "Min Production"
    Shortage = 'shortage'
    Production = 'production'
    Ending_inventory = 'Ending_inventory'
    Prev_Ending_Inventory = 'Prev_Ending_Inventory'
    W_LotSize_Increment = 'W LotSize Increment'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')


    ################################################################################################################
    # Step 3 (1) oupput MG 초기화 및 데이터 전 처리
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : 데이터 전 처리')

    # output MG 초기화
    df_in_TargetStock[W_Quantity_Min_Target] = 0

    # Groupby를 위한 Columns 설정
    group_col = [Version_COLUMN, Item_COLUMN, Location_COLUMN, TimeWeek_COLUMN]
    groupby_col = [Version_COLUMN, Item_COLUMN, Location_COLUMN]


    # df_in_Demand & df_in_DCSafetyStock 를 out put 그래인으로 groupby하여 Demand 수량 Sum
    df_in_Demand_Group = df_in_Demand.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN, TimeWeek_COLUMN])[
        W_Demand_Quantity_to_SCS].sum().reset_index()
    print_df(df_in_Demand_Group, 'df_in_Demand_Group', True)
    df_in_DCInv[W_OnHand_Quantity] = df_in_DCInv[W_OnHand_Quantity].fillna(0).astype(int)
    df_in_DCInv[W_Expected_Receipts] = df_in_DCInv[W_Expected_Receipts] + df_in_DCInv[W_OnHand_Quantity]
    df_in_DCInv_Group = df_in_DCInv.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN])[
        W_Expected_Receipts].sum().fillna(0).reset_index()
    print_df(df_in_DCInv_Group, 'df_in_DCInv_Group',True)

    # df_in_DCHUBInv_Group = df_in_DCHUBInv.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN])[
    #     W_Expected_Receipts].sum().reset_index()

    # df_in_LotSize의 최소 Lot Qty 추출
    df_in_LotSize_Temp = df_in_LotSize[df_in_LotSize[W_LotSize_Increment].fillna(0) > 1]
    df_in_LotSize_Temp = df_in_LotSize_Temp.groupby(
        [Version_COLUMN, Item_COLUMN,Location_COLUMN])[W_LotSize_Increment].min().reset_index()
    # 2025.05.19 SubLocation 그룹 바이 컬럼 추가
    df_in_LotSize_Temp = df_in_LotSize_Temp.drop_duplicates()

    print_df(df_in_LotSize_Temp, 'df_in_LotSize_Temp', True)

    # df_in_LotSize_Temp = df_in_LotSize_Temp.rename(columns={SUB_LOCATION_COLUMN : Location_COLUMN}) # 2025.05.19 Merge를 위한 컬럼명 변경

    print_df(df_in_LotSize_Temp, 'df_in_LotSize_Temp', True)


    # df_in_DCSafetyStock_Group & df_in_DCSafetyStock_Group & df_in_LotSize merge
    df_in_Demand_Temp = df_in_Demand_Group.merge(df_in_DCInv_Group,
                                                 on=[Version_COLUMN, Item_COLUMN, Location_COLUMN], how='left')
    print_df(df_in_Demand_Temp, 'df_in_Demand_Temp', True)

    df_in_Demand_Temp = df_in_Demand_Temp.merge(df_in_LotSize_Temp,
                                                on=[Version_COLUMN, Item_COLUMN, Location_COLUMN], how='inner')
    df_in_Demand_Temp[W_Expected_Receipts] = df_in_Demand_Temp[W_Expected_Receipts].fillna(0)

    print_df(df_in_Demand_Temp, 'df_in_Demand_Temp',True)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) 전주 재고를 감안한 최소 생산 수량 및 최종 재고 및 EOH_Target 생성
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : 데이터 전 처리')

    # output MG 초기화
    df_in_TargetStock[W_Quantity_Min_Target] = 0

    # Groupby를 위한 Columns 설정
    group_col = [Version_COLUMN, Item_COLUMN, Location_COLUMN, TimeWeek_COLUMN]
    groupby_col = [Version_COLUMN, Item_COLUMN, Location_COLUMN]

    # df_in_Demand & df_in_DCSafetyStock 를 out put 그래인으로 groupby하여 Demand 수량 Sum
    df_in_Demand_Group = df_in_Demand.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN, TimeWeek_COLUMN])[
        W_Demand_Quantity_to_SCS].sum().reset_index()
    df_in_DCInv_Group = df_in_DCInv.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN])[
        W_Expected_Receipts].sum().fillna(0).reset_index()
    # df_in_DCHUBInv_Group = df_in_DCHUBInv.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN])[
    #     W_Expected_Receipts].sum().reset_index()

    # df_in_LotSize의 최소 Lot Qty 추출
    df_in_LotSize = df_in_LotSize[df_in_LotSize[W_LotSize_Increment].fillna(0) > 1]
    print_df(df_in_LotSize, 'df_in_LotSize', True)
    df_in_LotSize = df_in_LotSize.groupby(
        [Version_COLUMN, Item_COLUMN,Location_COLUMN])[W_LotSize_Increment].min().reset_index()
    # 2025.05.19 SubLocation 그룹 바이 컬럼 추가

    print_df(df_in_LotSize, 'df_in_LotSize', True)

    # df_in_LotSize = df_in_LotSize.rename(columns={SUB_LOCATION_COLUMN: Location_COLUMN})  # 2025.05.19 Merge를 위한 컬럼명 변경

    print_df(df_in_LotSize, 'df_in_LotSize', True)


    # df_in_DCSafetyStock_Group & df_in_DCSafetyStock_Group & df_in_LotSize merge
    df_in_Demand_Temp = df_in_Demand_Group.merge(df_in_DCInv_Group,
                                                 on=[Version_COLUMN, Item_COLUMN, Location_COLUMN], how='left')
    df_in_Demand_Temp = df_in_Demand_Temp.merge(df_in_LotSize, on=[Version_COLUMN, Item_COLUMN,Location_COLUMN], how='inner')
    df_in_Demand_Temp[W_Expected_Receipts] = df_in_Demand_Temp[W_Expected_Receipts].fillna(0)

    print_df(df_in_Demand_Temp, 'df_in_Demand_Temp', True)

    df_in_Demand_Temp[Demand_cumsum] = df_in_Demand_Temp.groupby(groupby_col)[W_Demand_Quantity_to_SCS].cumsum()

    df_in_Demand_Temp[Net_Demand] = (df_in_Demand_Temp[Demand_cumsum] - df_in_Demand_Temp[W_Expected_Receipts]).apply(
        lambda x: x if x > 0 else 0)

    df_in_Demand_Temp[Min_Production] = np.ceil(
        df_in_Demand_Temp[Net_Demand] / df_in_Demand_Temp[W_LotSize_Increment]) * df_in_Demand_Temp[
                                            W_LotSize_Increment]

    df_in_Demand_Temp[W_Quantity_Min_Target] = df_in_Demand_Temp[Min_Production] - df_in_Demand_Temp[Net_Demand]

    print_df(df_in_Demand_Temp, 'df_in_Demand_Temp',True)
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) 최종 Out_Put Save
    ###############################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    df_out_TargetStock = df_in_Demand_Temp.copy()
    df_out_TargetStock = df_out_TargetStock[[Version_COLUMN, Item_COLUMN, TimeWeek_COLUMN, Location_COLUMN,
                                             W_Quantity_Min_Target]]


    print_df(df_out_TargetStock, 'df_out_TargetStock')
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. AP2 기준 초기화 및 값 업데이트
    ###############################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    # df_out_TargetStock = df_out_TargetStock.merge(df_in_TargetStock, on=group_col , how='outer', suffixes=('_x', '_y'))
    #
    # df_out_TargetStock[W_Quantity_Min_Target] = df_out_TargetStock['W Quantity Min Target_x'].fillna(
    #     df_out_TargetStock['W Quantity Min Target_y'])
    #
    # non_zero_start = df_out_TargetStock.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN])[
    #     W_Quantity_Min_Target].transform(lambda x: x.ne(0).idxmax())
    #
    # filtered_df = df_out_TargetStock[df_out_TargetStock.index >= non_zero_start]
    # df_out_TargetStock_temp = df_out_TargetStock.copy()
    # df_out_TargetStock_temp.loc[df_out_TargetStock.index < non_zero_start, W_Quantity_Min_Target] = np.nan
    # df_out_TargetStock_temp = df_out_TargetStock_temp[~df_in_Demand_Temp.index.isin(filtered_df.index)]
    #
    # df_out_TargetStock = pd.concat([filtered_df, df_out_TargetStock_temp]).sort_index()

    # df_out_TargetStock['Zero_flag'] = (df_out_TargetStock['W Quantity Min Target_x'] == 0).astype(int)
    # df_out_TargetStock['Zero_group'] = df_out_TargetStock.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN])[
    #     'Zero_flag'].cumsum()
    #
    # df_out_TargetStock['remove_flag'] = df_out_TargetStock.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN])[
    #     'Zero_group'].transform(lambda x: (x == 1).cumsum())
    #
    # df_out_TargetStock = df_out_TargetStock[df_out_TargetStock['remove_flag'] == 0]

    df_out_TargetStock[W_Quantity_Min_Target] = np.where(df_out_TargetStock[W_Quantity_Min_Target] == 0, np.nan,
                                                         df_out_TargetStock[W_Quantity_Min_Target])

    df_out_TargetStock = df_out_TargetStock[[Version_COLUMN, Item_COLUMN, TimeWeek_COLUMN, Location_COLUMN,
                                             W_Quantity_Min_Target]]

    #
    # def drop_initial_columns(df):
    #     result =[]
    #     for (version, item, location), group in df.groupby([Version_COLUMN, Item_COLUMN, Location_COLUMN]):
    #         group = group.sort_values([TimeWeek_COLUMN]).reset_index(drop=True)
    #         keep =[]
    #         found_nonzero = False
    #
    #         for val in group[W_Quantity_Min_Target]:
    #             if not found_nonzero:
    #                 if val == 0:
    #                     keep.append(False)
    #                 else:
    #                     found_nonzero = True
    #                     keep.append(True)
    #             else:
    #                 keep.append(True)
    #         group = group[keep].reset_index(drop=True)
    #         result.append(group)
    #     return pd.concat(result).reset_index(drop=True)

    # df_out_TargetStock = drop_initial_columns(df_out_TargetStock)

    print_df(df_out_TargetStock, 'df_out_TargetStock',True)
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 7. 최종 Out 설정
    ###############################################################################################################
    step(700, '=====> STEP 7(Start) : output data machining')

    row_count, col_count = df_out_TargetStock.shape
    note(f'=====> Final df_out_SalesAct rows : {row_count} , Columns : {col_count}')
    print_df(df_out_TargetStock, 'df_out_TargetStock',True)



    if is_local:
        note(f'=====> Final output table create')
        print_df(df_out_TargetStock, 'df_out_TargetStock',True)

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_TargetStock = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(700, '===================== plugin Execution End =====================')

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