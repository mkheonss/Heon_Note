

"""

* 프로그램명
    - PY_UI_LoadingResult

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.02.13 / ybest7.park (박병훈) / Create
- 2025.04.30 / ybest7.park (박병훈) / input qurey 수정 및 VD Common 반영

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
    - df_in_DTBLPlan = Select ([Version].[Version Name] * [Item].[Item] * [Item].[Product Group] * [Time].[Day] * [Time].[Week] * [Documents].[OrderlineID] * [Cluster].[Cluster]* [Activity1].[Activity1]* [Activity1].[From Location] * [Activity1].[To Location] * [Sequence].[Sequence] * [Activity2].[Activity2]  * [Equipment].[Equipment ID]) on row, ({Measure.[D TLB Plan Output Quantity], Measure.[D TLB Plan Output Quantity Base UOM], Measure.[Dummy]}) on column where {(Measure.[D TLB Plan Output Quantity]>0) || (Measure.[D TLB Plan Output Quantity Base UOM]>0)};
    - df_in_LoadingMaster = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item]) on row, ({Measure.[Loading Master_CBM],Measure.[Loading Master_Multiple Lot], Measure.[Loading Master_20FT Qty],Measure.[Loading Master_40FT Qty],Measure.[Dummy]}) on column.filter(Measure.[Loading Master_20FT Qty]!="" || Measure.[Loading Master_40FT Qty] !="");

* 데이턱 삭제
    - DELETE DATA FOR MODEL [SOP Container Loading] where {Version.[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [Container Loading] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_SOPContainerLoading = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Container].[ContainerType] * [Loading].[Loading Type] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP CTNR Loading_CBM Prop], Measure.[SOP CTNR Loading_CTNR CBM], Measure.[SOP CTNR Loading_CTNR Prop], Measure.[SOP CTNR Loading_CTNR Qty], Measure.[SOP CTNR Loading_LOT Size], Measure.[SOP CTNR Loading_LOT Size Prop], Measure.[SOP CTNR Loading_Loading Qty], Measure.[SOP CTNR Loading_Navigate], Measure.[SOP CTNR Loading_SOP CBM], Measure.[SOP CTNR Loading_SOP Qty]}) on column;
    - df_out_ContainerLoading = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Product Group] * [Time].[Week] * [Container].[ContainerType] * [Loading].[Loading Type] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[CTNR Loading_CTNR Prop], Measure.[CTNR Loading_CTNR Qty], Measure.[CTNR Loading_Loading Qty], Measure.[CTNR Loading_SOP Qty]}) on column;
    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    EXEC plugin instance [PY_UI_LoadingResult] for measures {[SOP CTNR Loading_CBM Prop]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (paramOutVersion, "CWV_MP")} ;


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
import tracemalloc
import warnings

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_LoadingResult'
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
    # # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_DTBLPlan = read_csv_file('df_in_DTBLPlan')
        df_in_LoadingMaster = read_csv_file('df_in_LoadingMaster')

    # if df_in_BODStructure.empty:
    #     raise Exception("Exception: df_in_BODStructure is empty")
    #
    # if df_in_SiteAP2Map.empty:
    #     raise Exception("Exception: df_in_SiteAP2Map is empty")
    #
    # if df_in_MultiSite.empty:
    #     raise Exception("Exception: df_in_MultiSite is empty")

    # note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_DTBLPlan, 'df_in_DTBLPlan',True)
    print_df(df_in_LoadingMaster, 'df_in_LoadingMaster',True)

    # pLogInfo = "CWV_MP;PY_UI_LoadingResult;1"

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_Name_COLUMN = 'Version.[Version Name]'
    Item_COLUMN = 'Item.[Item]'
    Item_ProductGroup_COLUMN = 'Item.[Product Group]'
    Time_Day_COLUMN = 'Time.[Day]'
    Time_Week_COLUMN = 'Time.[Week]'
    Documents_OrderlineID_COLUMN = 'Documents.[OrderlineID]'
    Cluster_COLUMN = 'Cluster.[Cluster]'
    Activity1_COLUMN = 'Activity1.[Activity1]'
    Activity1_From_Location_COLUMN = 'Activity1.[From Location]'
    Activity1_To_Location_COLUMN = 'Activity1.[To Location]'
    Sequence_COLUMN = 'Sequence.[Sequence]'
    Activity2_COLUMN = 'Activity2.[Activity2]'
    Equipment_ID_COLUMN = 'Equipment.[Equipment ID]'
    Location_COLUMN = 'Location.[Location]'
    ContainerType_COLUMN = 'Container.[ContainerType]'
    Loading_Type_COLUMN = 'Loading.[Loading Type]'
    Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
    Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'

    D_TLB_Plan_Output_Quantity = 'D TLB Plan Output Quantity'
    D_TLB_Plan_Output_Quantity_Base_UOM = 'D TLB Plan Output Quantity Base UOM'
    Dummy = 'Dummy'

    Loading_Master_1st_Container = 'Loading Master_1st Container'
    Loading_Master_20FT_Minimum_Lot = 'Loading Master_20FT Minimum Lot'
    Loading_Master_20FT_Multiple_Lot = 'Loading Master_20FT Multiple Lot'
    Loading_Master_20FT_Qty = 'Loading Master_20FT Qty'
    Loading_Master_2nd_Container = 'Loading Master_2nd Container'
    Loading_Master_40FT_Qty = 'Loading Master_40FT Qty'
    Loading_Master_40HC_Minimum_Lot = 'Loading Master_40HC Minimum Lot'
    Loading_Master_40HC_Multiple_Lot = 'Loading Master_40HC Multiple Lot'
    Loading_Master_40HC_Qty = 'Loading Master_40HC Qty'
    Loading_Master_45FT_Qty = 'Loading Master_45FT Qty'
    Loading_Master_53FT_Qty = 'Loading Master_53FT Qty'
    Loading_Master_BOX_D = 'Loading Master_BOX D'
    Loading_Master_BOX_H = 'Loading Master_BOX H'
    Loading_Master_BOX_W = 'Loading Master_BOX W'
    Loading_Master_CBM = 'Loading Master_CBM'
    Loading_Master_FCL = 'Loading Master_FCL'
    Loading_Master_FCL_Item_Flag = 'Loading Master_FCL Item Flag'
    Loading_Master_Gross_Weight = 'Loading Master_Gross Weight'
    Loading_Master_IF_info_By = 'Loading Master_IF info By'
    Loading_Master_IF_info_Dttm = 'Loading Master_IF info Dttm'
    Loading_Master_Init_By = 'Loading Master_Init By'
    Loading_Master_Init_Dttm = 'Loading Master_Init Dttm'
    Loading_Master_Minimum_Lot = 'Loading Master_Minimum Lot'
    Loading_Master_Multiple_Lot = 'Loading Master_Multiple Lot'
    Loading_Master_Net_Weight = 'Loading Master_Net Weight'
    Loading_Master_PLC = 'Loading Master_PLC'
    Loading_Master_Up_By = 'Loading Master_Up By'
    Loading_Master_Up_Dttm = 'Loading Master_Up Dttm'

    TLB_Loading_Master_1st_Container = 'TLB Loading Master_1st Container'
    TLB_Loading_Master_2nd_Container = 'TLB Loading Master_2nd Container'
    TLB_MAX_Loading_Rate = 'TLB MAX Loading Rate'
    TLB_MIN_Loading_Rate = 'TLB MIN Loading Rate'
    TLB_Mix_Loading_FCL = 'TLB Mix Loading FCL'

    SOP_CTNR_Loading_CBM_Prop = 'SOP CTNR Loading_CBM Prop'
    SOP_CTNR_Loading_CTNR_CBM = 'SOP CTNR Loading_CTNR CBM'
    SOP_CTNR_Loading_CTNR_Prop = 'SOP CTNR Loading_CTNR Prop'
    SOP_CTNR_Loading_CTNR_Qty = 'SOP CTNR Loading_CTNR Qty'
    SOP_CTNR_Loading_LOT_Size = 'SOP CTNR Loading_LOT Size'
    SOP_CTNR_Loading_LOT_Size_Prop = 'SOP CTNR Loading_LOT Size Prop'
    SOP_CTNR_Loading_Loading_Qty = 'SOP CTNR Loading_Loading Qty'
    SOP_CTNR_Loading_SOP_CBM = 'SOP CTNR Loading_SOP CBM'
    SOP_CTNR_Loading_SOP_Qty = 'SOP CTNR Loading_SOP Qty'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) Multi_Site_BOD_Valid_Flag 값 초기화
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : Check memory usage & runtime')

    # Merge 및 데이터 정리를 위해 Columns 명 변경
    df_in_DTBLPlan = df_in_DTBLPlan.rename(
        columns={Activity1_From_Location_COLUMN: Location_COLUMN, Activity1_To_Location_COLUMN: Sub_Location_COLUMN,
                 Activity2_COLUMN: Trans_Mode_COLUMN, Equipment_ID_COLUMN: ContainerType_COLUMN})

    # 불필요한 Dummy 삭제
    df_in_DTBLPlan_Temp = df_in_DTBLPlan.copy().drop(columns=Dummy, axis=1)

    # ContainerType_COLUMN 의 Values 변경
    df_in_DTBLPlan_Temp[ContainerType_COLUMN] = np.where(df_in_DTBLPlan_Temp[ContainerType_COLUMN] == "40FT_Mix",
                                                         "40HC", "20FT")

    # df_in_LoadingMaster의 CBM 및 Multiple_Lot 데이터 전 처리 0으로 채우기
    df_in_LoadingMaster[Loading_Master_CBM] = df_in_LoadingMaster[Loading_Master_CBM].fillna(0).astype(int)
    df_in_LoadingMaster[Loading_Master_Multiple_Lot] = df_in_LoadingMaster[Loading_Master_Multiple_Lot].fillna(
        0).astype(int)

    # Gropyby를 위한 Columns 설정
    on_columns = [Version_Name_COLUMN, Location_COLUMN, Item_COLUMN]

    # df_in_DTBLPlan_Temp & df_in_DTBLPlan_Temp merge
    df_in_DTBLPlan_Temp = df_in_DTBLPlan_Temp.merge(df_in_LoadingMaster.drop(columns=Dummy, axis=1),
                                                    on=on_columns, how='left')

    # ContainerType_COLUMN 분류
    df_in_DTBLPlan_Temp[SOP_CTNR_Loading_Loading_Qty] = np.where(
        df_in_DTBLPlan_Temp[ContainerType_COLUMN] == "40HC", df_in_DTBLPlan_Temp[Loading_Master_40FT_Qty],
        df_in_DTBLPlan_Temp[Loading_Master_20FT_Qty])

    # Loading_Type_COLUMN 값 설정 (Item 의 갯수 확인)
    df_in_DTBLPlan_Temp[Loading_Type_COLUMN] = df_in_DTBLPlan_Temp.groupby(
        [Version_Name_COLUMN, Time_Week_COLUMN, Item_ProductGroup_COLUMN, Location_COLUMN, Sub_Location_COLUMN,
         Trans_Mode_COLUMN, Sequence_COLUMN, ContainerType_COLUMN])[Item_COLUMN].transform('count')

    # Loading_Type_COLUMN 값이 1이면 Full, 아니면 Mix로 설정
    df_in_DTBLPlan_Temp[Loading_Type_COLUMN] = np.where(df_in_DTBLPlan_Temp[Loading_Type_COLUMN] == 1, "Full Container",
                                                        "Mix Container")

    # df_in_LoadingMaster의 CBM 및 Multiple_Lot 데이터 전 처리 0으로 채우기
    df_in_LoadingMaster[Loading_Master_CBM] = df_in_LoadingMaster[Loading_Master_CBM].fillna(0).astype(int)
    df_in_LoadingMaster[Loading_Master_Multiple_Lot] = df_in_LoadingMaster[Loading_Master_Multiple_Lot].fillna(
        0).astype(int)

    # 데이터 프레임 추가 해서 From ~ to Sequence 까지 그룹바이 (max Item에 1 찍어 주기)
    df_in_DTBLPlan_Temp[SOP_CTNR_Loading_CTNR_Qty] = df_in_DTBLPlan_Temp.groupby(
        [Version_Name_COLUMN, Time_Week_COLUMN, Location_COLUMN, Sub_Location_COLUMN, Trans_Mode_COLUMN,
         Sequence_COLUMN, ContainerType_COLUMN])[Item_COLUMN].transform('max')

    # SOP_CTNR_Loading_CTNR_Qty 수량 확인
    df_in_DTBLPlan_Temp[SOP_CTNR_Loading_CTNR_Qty] = np.where(
        df_in_DTBLPlan_Temp[Item_COLUMN] == df_in_DTBLPlan_Temp[SOP_CTNR_Loading_CTNR_Qty], 1, 0)

    df_in_DTBLPlan_allAgg = df_in_DTBLPlan_Temp.groupby(
        [Version_Name_COLUMN, Location_COLUMN, Item_ProductGroup_COLUMN, Time_Week_COLUMN, ContainerType_COLUMN,
         Loading_Type_COLUMN, Sub_Location_COLUMN, Trans_Mode_COLUMN])[
        [SOP_CTNR_Loading_CTNR_Qty,D_TLB_Plan_Output_Quantity_Base_UOM,SOP_CTNR_Loading_Loading_Qty]].sum().reset_index()

    print_df(df_in_DTBLPlan_allAgg, 'df_in_DTBLPlan_allAgg', True)
    print_df(df_in_DTBLPlan_Temp, 'df_in_DTBLPlan_Temp-1',True)

    # save_csv_file(df_in_DTBLPlan_Temp, 'df_in_DTBLPlan_Temp -1 ')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4 (1) Out Put 설정
    ###############################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # out put 설정을 위한 데이터 프레임 복사
    df_out_ContainerLoading = df_in_DTBLPlan_allAgg.copy()
    df_out_ContainerLoading = df_out_ContainerLoading.rename(columns={
        D_TLB_Plan_Output_Quantity_Base_UOM: 'CTNR Loading_CTNR Qty',
        SOP_CTNR_Loading_CTNR_Qty: 'CTNR Loading_SOP Qty',
        SOP_CTNR_Loading_Loading_Qty: 'CTNR Loading_Loading Qty'})

    df_out_ContainerLoading = df_out_ContainerLoading[
        [Version_Name_COLUMN, Location_COLUMN, Item_ProductGroup_COLUMN, Time_Week_COLUMN, ContainerType_COLUMN,
         Loading_Type_COLUMN, Sub_Location_COLUMN, Trans_Mode_COLUMN, 'CTNR Loading_CTNR Qty',
         'CTNR Loading_SOP Qty', 'CTNR Loading_Loading Qty']]

    print_df(df_out_ContainerLoading, 'df_out_ContainerLoading',True)
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5 (1) Out Put 설정
    ###############################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    df_in_DTBLPlan_group = df_in_DTBLPlan_Temp.groupby(
        [Version_Name_COLUMN, Item_COLUMN, Item_ProductGroup_COLUMN, Time_Week_COLUMN, Location_COLUMN,
         Sub_Location_COLUMN,
         Trans_Mode_COLUMN, ContainerType_COLUMN, Loading_Type_COLUMN]).sum().reset_index()

    df_in_DTBLPlan_group = df_in_DTBLPlan_group[
        [Version_Name_COLUMN, Item_COLUMN, Item_ProductGroup_COLUMN, Time_Week_COLUMN, Location_COLUMN,
         Sub_Location_COLUMN,
         Trans_Mode_COLUMN, ContainerType_COLUMN, Loading_Type_COLUMN, D_TLB_Plan_Output_Quantity_Base_UOM,
         SOP_CTNR_Loading_CTNR_Qty, SOP_CTNR_Loading_Loading_Qty]]

    # Merge를 위한 Columns 설정
    on_columns = [Version_Name_COLUMN, Location_COLUMN, Item_COLUMN]

    df_in_DTBLPlan_group = df_in_DTBLPlan_group.merge(df_in_LoadingMaster, on=on_columns, how='left')

    # SOP_CTNR_Loading_CTNR_Qty 값 설정 (D_TLB_Plan_Output_Quantity_Base_UOM * Loading_Master_CBM)
    df_in_DTBLPlan_group[SOP_CTNR_Loading_SOP_CBM] = df_in_DTBLPlan_group[D_TLB_Plan_Output_Quantity_Base_UOM] * \
                                                     df_in_DTBLPlan_group[Loading_Master_CBM]

    # 1. output Data 값 설정
    df_in_DTBLPlan_group[SOP_CTNR_Loading_CTNR_CBM] = 67.5  # 1-1 Default 67.5

    # 1-2 SOP CBM / CTNR CBM 계산
    df_in_DTBLPlan_group[SOP_CTNR_Loading_CBM_Prop] = df_in_DTBLPlan_group[SOP_CTNR_Loading_SOP_CBM] / \
                                                      df_in_DTBLPlan_group[SOP_CTNR_Loading_CTNR_CBM]

    # 1-3 D_TLB_Plan_Output_Quantity_Base_UOM columns 명 변경
    df_in_DTBLPlan_group = df_in_DTBLPlan_group.rename(
        columns={D_TLB_Plan_Output_Quantity_Base_UOM: SOP_CTNR_Loading_SOP_Qty,
                 Loading_Master_Multiple_Lot: SOP_CTNR_Loading_LOT_Size,
                 })

    # 1-4 SOP_CTNR_Loading_CTNR_Prop columns 설정
    df_in_DTBLPlan_group[SOP_CTNR_Loading_CTNR_Prop] = 0

    # 1-5 SOP_CTNR_Loading_LOT_Size_Prop 설정
    df_in_DTBLPlan_group[SOP_CTNR_Loading_LOT_Size_Prop] = np.where(
        df_in_DTBLPlan_group[SOP_CTNR_Loading_SOP_Qty] > df_in_DTBLPlan_group[SOP_CTNR_Loading_LOT_Size], 1 * 100,
        df_in_DTBLPlan_group[SOP_CTNR_Loading_SOP_Qty] / df_in_DTBLPlan_group[SOP_CTNR_Loading_LOT_Size] * 100)

    # Loading_Navigate 설정
    df_in_DTBLPlan_group['SOP CTNR Loading_Navigate'] =  "SOP Ajdust / Loading Master / BOD List"

    # df_in_DTBLPlan_Temp columns 명 순서 지정
    df_in_DTBLPlan_group = df_in_DTBLPlan_group[
        [Version_Name_COLUMN, Item_COLUMN, Time_Week_COLUMN, Location_COLUMN, ContainerType_COLUMN, Loading_Type_COLUMN,
         Sub_Location_COLUMN,
         Trans_Mode_COLUMN, SOP_CTNR_Loading_SOP_Qty, SOP_CTNR_Loading_Loading_Qty, SOP_CTNR_Loading_CTNR_Prop,
         SOP_CTNR_Loading_CTNR_Qty, SOP_CTNR_Loading_SOP_CBM, SOP_CTNR_Loading_CTNR_CBM, SOP_CTNR_Loading_CBM_Prop,
         SOP_CTNR_Loading_LOT_Size, SOP_CTNR_Loading_LOT_Size_Prop,'SOP CTNR Loading_Navigate']]

    print_df(df_in_DTBLPlan_group, 'df_in_DTBLPlan_group',True)
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. (1) 최종 df_out_SOPContainerLoading Save
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    df_out_SOPContainerLoading = df_in_DTBLPlan_group.copy()

    # Grain 기준 중복 삭제
    df_out_SOPContainerLoading = df_out_SOPContainerLoading.drop_duplicates(
        subset=[Version_Name_COLUMN, Item_COLUMN, Time_Week_COLUMN, Location_COLUMN, ContainerType_COLUMN,
                Loading_Type_COLUMN, Sub_Location_COLUMN, Trans_Mode_COLUMN])

    # 최종 Output 확인
    print_df(df_out_SOPContainerLoading, 'df_out_SOPContainerLoading',True)

    step(600, '=====> STEP 6(End) : Check memory usage & runtime')


    ################################################################################################################
    # Step 7. (1) 최종 df_out_SOPContainerLoading Save
    ################################################################################################################
    row_count, col_count = df_out_SOPContainerLoading.shape
    note(f'=====> Final df_out_SOPContainerLoading rows : {row_count} , Columns : {col_count}')

    row_count, col_count = df_out_ContainerLoading.shape
    note(f'=====> Final df_out_ContainerLoading rows : {row_count} , Columns : {col_count}')

    print_df(df_out_SOPContainerLoading, 'df_out_SOPContainerLoading',True)
    print_df(df_out_ContainerLoading, 'df_out_ContainerLoading',True)

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_SOPContainerLoading, 'df_out_SOPContainerLoading')
        save_csv_file(df_out_ContainerLoading, 'df_out_ContainerLoading')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_SOPContainerLoading = pd.DataFrame([], columns=[])
    df_out_ContainerLoading = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(800, '===================== plugin Execution End =====================')

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