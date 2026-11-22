"""
* 프로그램명
    - PY_UI_HUBPSIPlan

* 내용
    - HUB PSI Data 생성

* 변경이력
    - 2025.02.25 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_AP2StartWeek: Select (&CurrentWeek);
    - df_in_AllWeek     : Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
    - df_in_MDMHorizon  : Select (&MDMHorizon * [Time].[Day]);
    - df_in_LastSyncVersion : Select (&LastSyncVersion);
    - df_in_HUBPSIActual: Select (Version.[Version Name] * [Item].[Item] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-4).Key && #.Key < &CurrentWeek.element(0).Key) * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[HUB PSI Actual_GI Qty], Measure.[HUB PSI Actual_EOH]}) on column;
    - df_in_Demand      : Select (Version.[Version Name] * [Item].[Item]  * Location.[Location] * &MDMHorizon) on row,  ({Measure.[W Demand Quantity to SCS],Measure.[W Demand Fulfilled Quantity],Measure.[W Total Short Quantity],Measure.[W OnHand Quantity],Measure.[W Beginning On Hand],Measure.[W Material Production Quantity Plan Output],Measure.[W Material Consumption Quantity Plan Output], Measure.[W Expected Receipts],Measure.[W Ending On Hand],Measure.[W Target Inventory],Measure.[W Infinite Material Node]}) on column orderby Time.Week.Name;
    - df_in_Production  : Select (Version.[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Material Production Quantity Plan Output]}) on column;
    - df_in_Consumption : Select (Version.[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Material Consumption Quantity Plan Output]}) on column;
    - df_in_SiteAP2Map  : Select (Version.[Version Name] * [Location].[Location] ) on row, ({Measure.[Site AP2 Map_GC], Measure.[Site AP2 Map_Ship To], Measure.[Site AP2 Map_Status], Measure.[Site AP2 Map_Valid Flag]}) on column;
    - df_in_SSMonitor   : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * &MDMHorizon * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SS Monitor_Arrival], Measure.[SS Monitor_Arrival BuildAhead], Measure.[SS Monitor_Arrival JIT], Measure.[SS Monitor_Arrival SS], Measure.[SS Monitor_BuildAhead Limit], Measure.[SS Monitor_Demand], Measure.[SS Monitor_EOH], Measure.[SS Monitor_GI], Measure.[SS Monitor_Item BOD LT], Measure.[SS Monitor_SS], Measure.[SS Monitor_SS Short], Measure.[SS Monitor_SS Target Qty], Measure.[SS Monitor_SS Target Time], Measure.[SS Monitor_Shipment], Measure.[SS Monitor_Shipment BuildAhead], Measure.[SS Monitor_Shipment JIT], Measure.[SS Monitor_Shipment SS], Measure.[SS Monitor_Short]}) on column;
    - df_in_SetItem     : Select ([Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET"})) on row;
    - df_in_SOPW        : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [To Time].[To Week] * [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [BOM Info].[BOM Version] * [Week2].[Week2] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row, ({Measure.[Dummy],  Measure.[SOP W_SOP ID]}) on column where {[To Location].[To Location Region].filter(#.Name in {"EUROPE"})};
    - df_in_BODItem     : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Location].[Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC", "DC_HUB_MC_AP2"})) on row, ({Measure.[Dummy], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Priority]}) on column where {[Sub Location].[Sub Location Region].filter(#.Name in {"EUROPE"})};

* Flow Summary
    -

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_HUBPSIPlan

* 데이타 초기화
    - DELETE DATA FOR MODEL [HUB PSI Plan] WHERE {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_HUBPSIPlan] for measures {[HUB PSI Plan_Dmd]} using scope (&MPV.unionwith(&LastSyncVersion))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_LCMPSIPlan / MG:  HUB PSI Plan
        Select (&MPV * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Hub Location].[Hub Location] * [Trans Mode].[Trans Mode] ) on row, ({
        Measure.[HUB PSI Plan_Aging Over 30days], Measure.[HUB PSI Plan_Aging Over 60days], Measure.[HUB PSI Plan_Aging Rate Over 30days], Measure.[HUB PSI Plan_Aging Rate Over 60days], Measure.[HUB PSI Plan_Arrival],
        Measure.[HUB PSI Plan_Arrival Detail], Measure.[HUB PSI Plan_BOH], Measure.[HUB PSI Plan_Build Ahead], Measure.[HUB PSI Plan_Dmd], Measure.[HUB PSI Plan_Dmd Fill Rate], Measure.[HUB PSI Plan_Dmd GI],
        Measure.[HUB PSI Plan_EOH], Measure.[HUB PSI Plan_EOH Adj], Measure.[HUB PSI Plan_EOH Amt KRW], Measure.[HUB PSI Plan_EOH Amt USD], Measure.[HUB PSI Plan_EOH W], Measure.[HUB PSI Plan_GI Amt KRW],
        Measure.[HUB PSI Plan_GI Amt USD], Measure.[HUB PSI Plan_GI Qty], Measure.[HUB PSI Plan_GI W Accum], Measure.[HUB PSI Plan_GI W Accum Rate], Measure.[HUB PSI Plan_Intransit], Measure.[HUB PSI Plan_Inv Del DIR],
        Measure.[HUB PSI Plan_Inventory], Measure.[HUB PSI Plan_RTF], Measure.[HUB PSI Plan_SS Target Q], Measure.[HUB PSI Plan_SS Target Vio], Measure.[HUB PSI Plan_SS Target W], Measure.[HUB PSI Plan_Safety Stock],
        Measure.[HUB PSI Plan_Sales], Measure.[HUB PSI Plan_Shipment], Measure.[HUB PSI Plan_Shipment Detail], Measure.[HUB PSI Plan_Short], Measure.[HUB PSI Plan_Short CAPA], Measure.[HUB PSI Plan_Short CH Const],
        Measure.[HUB PSI Plan_Short Frz], Measure.[HUB PSI Plan_Short Inv Adj], Measure.[HUB PSI Plan_Short Manual], Measure.[HUB PSI Plan_Short Master], Measure.[HUB PSI Plan_Short Mtrl], Measure.[HUB PSI Plan_Short PBC/Rel],
        Measure.[HUB PSI Plan_Short PLC], Measure.[HUB PSI Plan_Short Payment], Measure.[HUB PSI Plan_Short Quality], Measure.[HUB PSI Plan_Short by ORG]}) on column;
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
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_HUBPSIPlan'
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


def filter_dataframe(dataframe, version_column, time_week_column, pre_version, plan_horizon):
    return dataframe.loc[
        (dataframe[version_column] != pre_version) &
        (dataframe[time_week_column].isin(plan_horizon[time_week_column]))
    ].copy()



def set_unique_combinations(df, df2, columns):
    cols = list(filter(lambda col: col != TIME_WEEK_COLUMN, columns))

    # 데이터의 모든 고유 조합 생성
    unique_combinations = df[cols].copy().drop_duplicates()

    # 주차(TIME_WEEK_COLUMN) 데이터의 모든 조합 산출
    df2 = df2.assign(key=1)
    unique_combinations = unique_combinations.assign(key=1)
    all_possible_combinations = unique_combinations.merge(df2, how="outer").drop(columns=['key']).drop_duplicates()

    # 결측 데이터 찾기 (left join & 필터링)
    missing_rows = all_possible_combinations.merge(
        df[columns], on=columns, how="left", indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return missing_rows



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
            df_in_MDMHorizon = read_csv_file("df_in_MDMHorizon")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_LastSyncVersion = read_csv_file("df_in_LastSyncVersion")
            df_in_AP2StartWeek = read_csv_file("df_in_AP2StartWeek")
            df_in_HUBPSIActual = read_csv_file("df_in_HUBPSIActual")
            df_in_Demand = read_csv_file("df_in_Demand")
            df_in_Production = read_csv_file("df_in_Production")
            df_in_Consumption = read_csv_file("df_in_Consumption")
            df_in_SSMonitor = read_csv_file("df_in_SSMonitor")
            df_in_SiteAP2Map = read_csv_file("df_in_SiteAP2Map")
            df_in_SetItem = read_csv_file("df_in_SetItem")
            df_in_SOPW = read_csv_file("df_in_SOPW")
            df_in_BODItem = read_csv_file("df_in_BODItem")


        print_df(df_in_MDMHorizon, 'input table load .... df_in_MDMHorizon')
        print_df(df_in_AllWeek, 'input table load .... df_in_AllWeek')
        print_df(df_in_LastSyncVersion, 'input table load .... df_in_LastSyncVersion')
        print_df(df_in_AP2StartWeek, 'input table load .... df_in_AP2StartWeek')
        print_df(df_in_HUBPSIActual, 'input table load .... df_in_HUBPSIActual')
        print_df(df_in_Demand, 'input table load .... df_in_Demand')
        print_df(df_in_Production, 'input table load .... df_in_Production')
        print_df(df_in_Consumption, 'input table load .... df_in_Consumption')
        print_df(df_in_SSMonitor, 'input table load .... df_in_SSMonitor')
        print_df(df_in_SiteAP2Map, 'input table load .... df_in_SiteAP2Map')
        print_df(df_in_SetItem, 'input table load .... df_in_SetItem')
        print_df(df_in_SOPW, 'input table load .... df_in_SOPW')
        print_df(df_in_BODItem, 'input table load .... df_in_BODItem')

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
        LOCATION_SITE_STAGE = 'Location.[Site Stage]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAY_COLUMN= 'Time.[Day]'
        ITEM_COLUMN = 'Item.[Item]'
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        SALES_DOMAIN_CUSTOMER_GROUP_COLUMN = 'Sales Domain.[Customer Group]'
        SALES_DOMAIN_SHIP_TO_COLUMN = 'Sales Domain.[Ship To]'

        DEMAND_TYPE_COLUMN = 'Demand Type.[Demand Type]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'
        W_DEMAND_QUANTITY_COLUMN = 'W Demand Quantity'
        W_DEMAND_QUANTITY_TO_SCS_COLUMN = 'W Demand Quantity to SCS'
        W_DEMAND_FULFILLED_QUANTITY_COLUMN = 'W Demand Fulfilled Quantity'
        W_TOTAL_SHORT_QUANTITY_COLUMN = 'W Total Short Quantity'
        W_BEGINNING_ON_HAND_COLUMN = 'W Beginning On Hand'
        W_ENDDING_ON_HAND_COLUMN = 'W Ending On Hand'
        W_ONHAND_QUANTITY_COLUMN = 'W OnHand Quantity'

        W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN = 'W Material Production Quantity Plan Output'
        W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN = 'W Material Consumption Quantity Plan Output'
        W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_DETAIL_COLUMN = 'W Material Production Quantity Plan Output Detail'
        W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_DETAIL_COLUMN = 'W Material Consumption Quantity Plan Output Detail'
        W_ACTIVITY_LEAD_TIME_COLUMN = 'W Activity Lead Time'
        W_TARGET_INVENTORY_COLUMN = 'W Target Inventory'
        W_EXPECTED_RECEIPTS_COLUMN = 'W Expected Receipts'
        W_INFINITE_METERIAL_NODE_COLUMN = 'W Infinite Material Node'

        EXCEPTED_RECEIPTS_COLUMN = 'Expected Receipts'

        ORDERLINEID_COLUMN = 'Documents.[OrderlineID]'
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        SS_MONITOR_SHIPMENT_BUILDAHEAD_COLUMN = 'SS Monitor_Shipment BuildAhead'
        SS_MONITOR_SS_TARGET_QTY_COLUMN = 'SS Monitor_SS Target Qty'
        SS_MONITOR_SS_TARGET_TIME_COLUMN = 'SS Monitor_SS Target Time'
        SS_MONITOR_SHIPMENT_SS_COLUMN = 'SS Monitor_Shipment SS'
        SS_MONITOR_ARRIVAL_SS_COLUMN = 'SS Monitor_Arrival SS'
        SS_MONITOR_BUILDAHEAD_LIMIT_COLUMN = 'SS Monitor_BuildAhead Limit'
        SS_MONITOR_ARRIVAL_BUILDAHEAD_COLUMN = 'SS Monitor_Arrival BuildAhead'
        SS_MONITOR_ARRIVAL_JIT_COLUMN = 'SS Monitor_Arrival JIT'
        SS_MONITOR_SHIPMENT_JIT_COLUMN = 'SS Monitor_Shipment JIT'

        HUB_PSI_PLAN_DMD_COLUMN = 'HUB PSI Plan_Dmd'
        HUB_PSI_PLAN_RTF_COLUMN = 'HUB PSI Plan_RTF'
        HUB_PSI_PLAN_GI_QTY_COLUMN = 'HUB PSI Plan_GI Qty'
        HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN = 'HUB PSI Plan_Dmd Fill Rate'
        HUB_PSI_PLAN_SALES_COLUMN = 'HUB PSI Plan_Sales'
        HUB_PSI_PLAN_SHORT_COLUMN = 'HUB PSI Plan_Short'
        HUB_PSI_PLAN_BOH_COLUMN = 'HUB PSI Plan_BOH'
        HUB_PSI_PLAN_EOH_COLUMN = 'HUB PSI Plan_EOH'
        HUB_PSI_PLAN_EOH_W_COLUMN = 'HUB PSI Plan_EOH W'
        HUB_PSI_PLAN_INTRANSIT_COLUMN = 'HUB PSI Plan_Intransit'
        HUB_PSI_PLAN_INVENTORY_COLUMN = 'HUB PSI Plan_Inventory'
        HUB_PSI_PLAN_ARRIVAL_COLUMN = 'HUB PSI Plan_Arrival'
        HUB_PSI_PLAN_ARRIVAL_DETAIL_COLUMN = 'HUB PSI Plan_Arrival Detail'
        HUB_PSI_PLAN_SHIPMENT_COLUMN = 'HUB PSI Plan_Shipment'
        HUB_PSI_PLAN_SHIPMENT_DETAIL_COLUMN = 'HUB PSI Plan_Shipment Detail'
        HUB_PSI_PLAN_AGING_OVER_30DAY_COLUMN = 'HUB PSI Plan_Aging Over 30days'
        HUB_PSI_PLAN_AGING_OVER_60DAY_COLUMN = 'HUB PSI Plan_Aging Over 60days'
        HUB_PSI_PLAN_AGING_RATE_OVER_30DAT_COLUMN = 'HUB PSI Plan_Aging Rate Over 30days'
        HUB_PSI_PLAN_AGING_RATE_OVER_60DAT_COLUMN = 'HUB PSI Plan_Aging Rate Over 60days'
        HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN = 'HUB PSI Plan_Short by ORG'
        HUB_PSI_PLAN_SAFETY_STOCK_COLUMN = 'HUB PSI Plan_Safety Stock'
        HUB_PSI_PLAN_SHORT_CH_CONST_COLUMN = 'HUB PSI Plan_Short CH Const'
        HUB_PSI_PLAN_SHORT_CAPA_COLUMN = 'HUB PSI Plan_Short CAPA'
        HUB_PSI_PLAN_SHORT_MASTER_COLUMN = 'HUB PSI Plan_Short Master'
        HUB_PSI_PLAN_SHORT_PLC_COLUMN = 'HUB PSI Plan_Short PLC'
        HUB_PSI_PLAN_GI_W_ACCUM_COLUMN = 'HUB PSI Plan_GI W Accum'
        HUB_PSI_PLAN_GI_W_ACCUM_RATE_COLUMN = 'HUB PSI Plan_GI W Accum Rate'
        HUB_PSI_PLAN_BUILD_AHEAD_COLUMN = 'HUB PSI Plan_Build Ahead'
        HUB_PSI_PLAN_SS_TARGET_W_COLUMN = 'HUB PSI Plan_SS Target W'
        HUB_PSI_PLAN_SS_TARGET_Q_COLUMN = 'HUB PSI Plan_SS Target Q'
        HUB_PSI_PLAN_SS_TARGET_VIO_COLUMN = 'HUB PSI Plan_SS Target Vio'
        HUB_PSI_PLAN_SS_SHIP_DETAIL_COLUMN = 'HUB PSI Plan_SS Ship Detail'
        HUB_PSI_PLAN_SS_AVRRIVAL_DETAIL_COLUMN = 'HUB PSI Plan_SS Avrrival Detail'
        HUB_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN = 'HUB PSI Plan_Avg 8W Flow Qty'
        HUB_PSI_PLAN_DMD_GI_COLUMN = 'HUB PSI Plan_Dmd GI'

        HUB_PSI_ACTUAL_GI_QTY_COLUMN = 'HUB PSI Actual_GI Qty'

        SITE_AP2_MAP_SHIP_TO_COLUMN = 'Site AP2 Map_Ship To'

        BOD_ITEM_PERIORITY = 'BOD Item_Priority'
        BOD_ITEM_EFF_ENDDATE = 'BOD Item_Eff Enddate'
        BOD_ITEM_EFF_STARTDATE = 'BOD Item_Eff Startdate'

        SOURCE_VERSION = 'CWV_MP'
        QTY_COLUMN = 'QTY'
        AVG_COLUMN = 'AVG'

        DC_HUB_VALUE = 'DC_HUB'
        DC_HUB_DC_VALUE = 'DC_HUB_MC'
        DC_HUB_MC_AP2_VALUE = 'DC_HUB_MC_AP2'

        df_common_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, SALES_DOMAIN_AP2_COLUMN,
        ]

        df_to_location_columns = [TO_LOCATION_TO_LOCATION_COLUMN]

        df_Pegging_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ORDERLINEID_COLUMN,
            W_DEMAND_QUANTITY_TO_SCS_COLUMN, W_DEMAND_FULFILLED_QUANTITY_COLUMN, W_TOTAL_SHORT_QUANTITY_COLUMN, W_TARGET_INVENTORY_COLUMN,
            W_ENDDING_ON_HAND_COLUMN, W_BEGINNING_ON_HAND_COLUMN, W_EXPECTED_RECEIPTS_COLUMN, W_INFINITE_METERIAL_NODE_COLUMN,
            W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN, W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN,
            HUB_PSI_PLAN_GI_QTY_COLUMN, HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN, HUB_PSI_PLAN_SALES_COLUMN,
            HUB_PSI_PLAN_DMD_COLUMN, HUB_PSI_PLAN_SHORT_COLUMN, HUB_PSI_PLAN_RTF_COLUMN,
            HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN, HUB_PSI_PLAN_SAFETY_STOCK_COLUMN,
        ]

        df_Pegging2_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN,
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN, W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN,
            W_ENDDING_ON_HAND_COLUMN, W_BEGINNING_ON_HAND_COLUMN, W_EXPECTED_RECEIPTS_COLUMN,
            HUB_PSI_PLAN_GI_QTY_COLUMN, HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN, HUB_PSI_PLAN_SALES_COLUMN,
            HUB_PSI_PLAN_DMD_COLUMN, HUB_PSI_PLAN_SHORT_COLUMN, HUB_PSI_PLAN_RTF_COLUMN,
            HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN, HUB_PSI_PLAN_SAFETY_STOCK_COLUMN,
        ]

        df_HUBPSIPlan_columns = [
            HUB_PSI_PLAN_DMD_COLUMN, HUB_PSI_PLAN_RTF_COLUMN, HUB_PSI_PLAN_GI_QTY_COLUMN,
            HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN, HUB_PSI_PLAN_SALES_COLUMN, HUB_PSI_PLAN_SHORT_COLUMN,
            HUB_PSI_PLAN_BOH_COLUMN, HUB_PSI_PLAN_EOH_COLUMN, HUB_PSI_PLAN_INTRANSIT_COLUMN,
            HUB_PSI_PLAN_INVENTORY_COLUMN, HUB_PSI_PLAN_SHIPMENT_DETAIL_COLUMN, HUB_PSI_PLAN_ARRIVAL_DETAIL_COLUMN,
            HUB_PSI_PLAN_AGING_OVER_30DAY_COLUMN, HUB_PSI_PLAN_AGING_OVER_60DAY_COLUMN,
            HUB_PSI_PLAN_AGING_RATE_OVER_30DAT_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_60DAT_COLUMN,
            HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN, HUB_PSI_PLAN_SAFETY_STOCK_COLUMN,
            HUB_PSI_PLAN_BUILD_AHEAD_COLUMN, HUB_PSI_PLAN_SS_TARGET_W_COLUMN, HUB_PSI_PLAN_SS_TARGET_Q_COLUMN,
            HUB_PSI_PLAN_SS_TARGET_VIO_COLUMN,
        ]

        df_HUBPSIPlan_eoh_columns = [HUB_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_Demand = df_in_Demand[df_in_Demand[ITEM_COLUMN] == 'QE43LS03DAUXXH']
        # df_in_SetItem = df_in_SetItem[df_in_SetItem[ITEM_COLUMN] == 'QE43LS03DAUXXH']
        # ------------------ 테스트 디버깅용 ------------------ end




        # 이전버전 추출
        pre_version = str(get_first_value(df_in_LastSyncVersion, VERSION_NAME_COLUMN))
        step(f'=====> pre_version : {pre_version}')



        # pre_version 값이 없거나 None인 경우에 예외 발생
        if not pre_version:  # 값이 비어있거나 None이면 False로 평가됨
            raise CustomException("STEP3 by 0 ____ pre_version 값이 없습니다. 첫 번째 값을 확인하세요.")

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_Production.empty:
            raise CustomException("STEP3 by 0 ____ df_in_Production 값이 없습니다.")

        if df_in_Consumption.empty:
            raise CustomException("STEP3 by 0 ____ df_in_Consumption 값이 없습니다.")




        # ====================> Set Item 추출 Start
        df_in_SetItem = df_in_SetItem[[ITEM_COLUMN]].drop_duplicates()
        df_in_Demand = df_in_Demand.merge(df_in_SetItem, how='inner', on=[ITEM_COLUMN])
        df_in_BODItem = df_in_BODItem.merge(df_in_SetItem, how='inner', on=[ITEM_COLUMN])
        df_in_HUBPSIActual = df_in_HUBPSIActual.merge(df_in_SetItem, how='inner', on=[ITEM_COLUMN])
        df_in_Consumption = df_in_Consumption.merge(df_in_SetItem, how='inner', on=[ITEM_COLUMN])
        df_in_Production = df_in_Production.merge(df_in_SetItem, how='inner', on=[ITEM_COLUMN])
        # ====================> End



        # ====================> Week 컬럼 추출 Start
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        df_in_MDMHorizon = df_in_MDMHorizon[[TIME_WEEK_COLUMN, TIME_DAY_COLUMN]].drop_duplicates().reset_index(drop=True)
        # ====================> End



        # ====================> 컬럼삭제 Start
        drop_columns = ['Dummy', 'SOP W_SOP ID', TIME_WEEK_COLUMN]
        for col in drop_columns:
            df_in_BODItem.drop(columns=[col], inplace=True, errors='ignore')
            df_in_SOPW.drop(columns=[col], inplace=True, errors='ignore')

        df_in_BODItem = df_in_BODItem.drop_duplicates()
        df_in_SOPW = df_in_SOPW.drop_duplicates()
        # ====================> End



        # ====================> AP2 Start Week 추출 Start
        ap2_start_week = int(get_first_value(df_in_AP2StartWeek, TIME_WEEK_COLUMN))
        step(f'=====> ap2_start_week : {ap2_start_week}')
        # ====================> End


        # ====================> Week 타입 변경 Start
        dataframes = [
            df_in_AllWeek,
            df_in_HUBPSIActual,
            df_in_Demand,
            df_in_Production,
            df_in_Consumption,
            df_in_SSMonitor
        ]
        for df in dataframes:
            df[TIME_WEEK_COLUMN] = pd.to_numeric(df[TIME_WEEK_COLUMN], errors='coerce')

        # ====================> End



        # ====================> df_in_SiteAP2Map 필요컬럼 추출
        df_in_SiteAP2Map = df_in_SiteAP2Map[[VERSION_NAME_COLUMN, LOCATION_COLUMN, SITE_AP2_MAP_SHIP_TO_COLUMN]].drop_duplicates()
        # ====================> End



        # ====================> df_in_Demand 제외 각 DF -> &LastSyncVersion 제외 filter Start
        df_in_HUBPSIActual = df_in_HUBPSIActual[df_in_HUBPSIActual[VERSION_NAME_COLUMN] != pre_version].copy()
        df_in_Production = filter_dataframe(df_in_Production, VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, pre_version, df_in_MDMHorizon)
        df_in_Consumption = filter_dataframe(df_in_Consumption, VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, pre_version, df_in_MDMHorizon)
        df_in_SSMonitor = filter_dataframe(df_in_SSMonitor, VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, pre_version, df_in_MDMHorizon)
        df_in_SiteAP2Map = df_in_SiteAP2Map[df_in_SiteAP2Map[VERSION_NAME_COLUMN] != pre_version].copy()
        df_in_BODItem = df_in_BODItem[df_in_BODItem[VERSION_NAME_COLUMN] != pre_version].copy()
        df_in_SOPW = df_in_SOPW[df_in_SOPW[VERSION_NAME_COLUMN] != pre_version].copy()
        # ====================> End



        # ====================> df_in_Production, df_in_Consumption > Activity1 에 '_' filter Start
        df_in_Production = df_in_Production[df_in_Production[ACTIVITY1_COLUMN].str.contains('_')].copy()
        df_in_Consumption = df_in_Consumption[df_in_Consumption[ACTIVITY1_COLUMN].str.contains('_')].copy()
        # ====================> End




        # ====================> df_in_BODItem > 주차 설정
        #                           1 enddate 과거는 삭제,
        #                           2 startdate 가 과거면 현재로 치환하고 enddate 가 horizen 보다 크거나 null 이면 horizeon end 값으로 치환
        formats = [     # 날짜 형식 지정 (명확하게 정의)
            '%m/%d/%Y %I:%M:%S %p',  # 11/24/2024 12:00:00 AM
            '%Y-%m-%d %H:%M:%S'  # 2024-11-24 00:00:00
        ]

        # 날짜 파싱 함수: 여러 형식을 시도
        def parse_dates(column):
            parsed_dates_1 = pd.to_datetime(df_in_BODItem[column], format=formats[0], errors='coerce')
            parsed_dates_2 = pd.to_datetime(df_in_BODItem[column], format=formats[1], errors='coerce')
            return parsed_dates_1.fillna(parsed_dates_2).dt.date

        df_in_BODItem[BOD_ITEM_EFF_ENDDATE] = parse_dates(BOD_ITEM_EFF_ENDDATE)
        df_in_BODItem[BOD_ITEM_EFF_STARTDATE] = parse_dates(BOD_ITEM_EFF_STARTDATE)

        horizon_start_date = pd.to_datetime(df_in_MDMHorizon[TIME_DAY_COLUMN].min())
        horizon_end_date = pd.to_datetime(df_in_MDMHorizon[TIME_DAY_COLUMN].max())

        # 날짜 타입으로 변환
        df_in_MDMHorizon[TIME_DAY_COLUMN] = pd.to_datetime(df_in_MDMHorizon[TIME_DAY_COLUMN])
        df_in_BODItem[BOD_ITEM_EFF_STARTDATE] = pd.to_datetime(df_in_BODItem[BOD_ITEM_EFF_STARTDATE])
        df_in_BODItem[BOD_ITEM_EFF_ENDDATE] = pd.to_datetime(df_in_BODItem[BOD_ITEM_EFF_ENDDATE])

        # startdate 과거면 horizon_start_week 로 치환
        df_in_BODItem[BOD_ITEM_EFF_STARTDATE] = df_in_BODItem[BOD_ITEM_EFF_STARTDATE].where(
            df_in_BODItem[BOD_ITEM_EFF_STARTDATE].isin(df_in_MDMHorizon[TIME_DAY_COLUMN]), horizon_start_date
        )

        # startdate 가 horizon_end_date 보다 작거나 같은것
        df_in_BODItem = df_in_BODItem[df_in_BODItem[BOD_ITEM_EFF_STARTDATE] <= horizon_end_date].copy()

        # enddate 가 horizen 보다 크거나 null 이면 horizeon end 값으로 치환
        df_in_BODItem[BOD_ITEM_EFF_ENDDATE] = df_in_BODItem[BOD_ITEM_EFF_ENDDATE].where(
            df_in_BODItem[BOD_ITEM_EFF_ENDDATE] <= horizon_end_date, horizon_end_date
        )
        
        # enddate 과거는 삭제
        df_in_BODItem = df_in_BODItem[df_in_BODItem[BOD_ITEM_EFF_ENDDATE] >= horizon_start_date].copy()
        print_df(df_in_BODItem, 'STEP3 by 0.4  ____ df_in_BODItem .... plan horizon filter')


        df_in_BODItem = df_in_BODItem[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            LOCATION_SITE_STAGE, BOD_ITEM_PERIORITY
        ]].drop_duplicates()

        max_columns = [LOCATION_COLUMN, BOD_ITEM_PERIORITY]
        groupby_columns = [VERSION_NAME_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, LOCATION_SITE_STAGE]
        agg_dict = {col: 'max' for col in max_columns}
        df_in_BODItem = df_in_BODItem.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_in_BODItem, 'STEP3 by 0.6  ____ df_in_BODItem .... groupby')
        # ====================> End



        # ====================> df_in_MDMHorizon Week 컬럼 재추출 Start
        df_in_MDMHorizon = df_in_MDMHorizon[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        # ====================> End





        # ====================> STEP3 by 1 (Start) -> df_in_Production, df_in_Consumption DataFrame modify

        # 1.1 df_in_Production > 'Activity1.[Activity1]' 로 Trans Mode, Sub Location 생성하기
        # split_cols = df_in_Production[ACTIVITY1_COLUMN].str.split('_', n=2, expand=True)
        # split_cols.columns = [LOCATION_COLUMN+'_p', SUB_LOCATION_COLUMN+'_p', TRANS_MODE_COLUMN+'_p']
        try:
            # 기본값으로 빈 DataFrame 생성
            split_cols = pd.DataFrame(columns=[LOCATION_COLUMN+'_p', SUB_LOCATION_COLUMN+'_p', TRANS_MODE_COLUMN+'_p'])

            # ACTIVITY1_COLUMN이 존재하고 비어있지 않은 경우에만 split 실행
            if ACTIVITY1_COLUMN in df_in_Production.columns:
                temp_split = df_in_Production[ACTIVITY1_COLUMN].fillna('').str.split('_', n=2, expand=True)
                if not temp_split.empty and temp_split.shape[1] > 0:
                    # 필요한 경우 누락된 컬럼 추가
                    while temp_split.shape[1] < 3:
                        temp_split[temp_split.shape[1]] = ''
                    temp_split.columns = [LOCATION_COLUMN+'_p', SUB_LOCATION_COLUMN+'_p', TRANS_MODE_COLUMN+'_p']
                    split_cols = temp_split

        except Exception as e:
            split_cols = pd.DataFrame(columns=[LOCATION_COLUMN+'_p', SUB_LOCATION_COLUMN+'_p', TRANS_MODE_COLUMN+'_p'])


        df_in_Production = pd.concat([df_in_Production, split_cols], axis=1)
        df_in_Production[LOCATION_COLUMN] = df_in_Production[LOCATION_COLUMN+'_p']
        df_in_Production[SUB_LOCATION_COLUMN] = df_in_Production[SUB_LOCATION_COLUMN+'_p']
        df_in_Production[TRANS_MODE_COLUMN] = df_in_Production[TRANS_MODE_COLUMN+'_p']
        print_df(df_in_Production, 'STEP3 by 1.1.1  ____ df_in_Production .... ACTIVITY1_COLUMN split')

        df_in_Production = df_in_Production.drop(columns=[LOCATION_COLUMN+'_p', SUB_LOCATION_COLUMN+'_p', TRANS_MODE_COLUMN+'_p'])
        print_df(df_in_Production, 'STEP3 by 1.1.2  ____ df_in_Production .... ACTIVITY1_COLUMN split remove')

        df_in_Production = pd.merge(df_in_Production, df_in_SiteAP2Map, how='left',
                                    left_on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN],
                                    right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN])

        df_in_Production = df_in_Production.drop(columns=[LOCATION_COLUMN+'_y'])
        df_in_Production.rename(columns={LOCATION_COLUMN+'_x': LOCATION_COLUMN}, inplace=True)
        df_in_Production = df_in_Production[
            (df_in_Production[SUB_LOCATION_COLUMN].notnull()) & (df_in_Production[TRANS_MODE_COLUMN].notnull())
        ]
        print_df(df_in_Production, 'STEP3 by 1.1.3  ____ df_in_Production .... columns modify')

        int_columns = [W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN]
        for col in int_columns:
            df_in_Production[col] = df_in_Production[col].fillna(0)

        df_in_Production.rename(columns={
            W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN: W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_DETAIL_COLUMN,
        }, inplace=True)
        df_in_Production = df_in_Production[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_DETAIL_COLUMN, SITE_AP2_MAP_SHIP_TO_COLUMN,
        ]].drop_duplicates()
        print_df(df_in_Production, 'STEP3 by 1.1.4  ____ df_in_Production .... final')



        # 1.2 df_in_Consumption > 'Activity1.[Activity1]' 로 Trans Mode, Sub Location 생성하기
        # split_cols = df_in_Consumption[ACTIVITY1_COLUMN].str.split('_', n=2, expand=True)
        # split_cols.columns = [LOCATION_COLUMN+'_c', SUB_LOCATION_COLUMN+'_c', TRANS_MODE_COLUMN+'_c']
        try:
            # 기본값으로 빈 DataFrame 생성
            split_cols = pd.DataFrame(columns=[LOCATION_COLUMN+'_c', SUB_LOCATION_COLUMN+'_c', TRANS_MODE_COLUMN+'_c'])

            # ACTIVITY1_COLUMN이 존재하고 비어있지 않은 경우에만 split 실행
            if ACTIVITY1_COLUMN in df_in_Consumption.columns:
                temp_split = df_in_Consumption[ACTIVITY1_COLUMN].fillna('').str.split('_', n=2, expand=True)
                if not temp_split.empty and temp_split.shape[1] > 0:
                    # 필요한 경우 누락된 컬럼 추가
                    while temp_split.shape[1] < 3:
                        temp_split[temp_split.shape[1]] = ''
                    temp_split.columns = [LOCATION_COLUMN+'_c', SUB_LOCATION_COLUMN+'_c', TRANS_MODE_COLUMN+'_c']
                    split_cols = temp_split

        except Exception as e:
            split_cols = pd.DataFrame(columns=[LOCATION_COLUMN+'_c', SUB_LOCATION_COLUMN+'_c', TRANS_MODE_COLUMN+'_c'])

        df_in_Consumption = pd.concat([df_in_Consumption, split_cols], axis=1)
        df_in_Consumption[LOCATION_COLUMN] = df_in_Consumption[LOCATION_COLUMN+'_c']
        df_in_Consumption[SUB_LOCATION_COLUMN] = df_in_Consumption[SUB_LOCATION_COLUMN+'_c']
        df_in_Consumption[TRANS_MODE_COLUMN] = df_in_Consumption[TRANS_MODE_COLUMN+'_c']
        print_df(df_in_Consumption, 'STEP3 by 1.2.1  ____ df_in_Consumption .... ACTIVITY1_COLUMN split')

        df_in_Consumption = df_in_Consumption.drop(columns=[LOCATION_COLUMN+'_c', SUB_LOCATION_COLUMN+'_c', TRANS_MODE_COLUMN+'_c'])
        print_df(df_in_Consumption, 'STEP3 by 1.2.2  ____ df_in_Consumption .... ACTIVITY1_COLUMN split remove')

        df_in_Consumption = pd.merge(df_in_Consumption, df_in_SiteAP2Map, how='left',
                                     left_on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN])

        df_in_Consumption = df_in_Consumption.drop(columns=[LOCATION_COLUMN+'_y'])
        df_in_Consumption.rename(columns={LOCATION_COLUMN+'_x': LOCATION_COLUMN}, inplace=True)
        df_in_Consumption = df_in_Consumption[
            (df_in_Consumption[SUB_LOCATION_COLUMN].notnull()) &(df_in_Consumption[TRANS_MODE_COLUMN].notnull())
        ]
        int_columns = [W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN]
        for col in int_columns:
            df_in_Consumption[col] = df_in_Consumption[col].fillna(0)

        print_df(df_in_Consumption, 'STEP 3 by 1.2.3 ____ df_Consumption .... activity1 final')

        df_in_Consumption.rename(columns={
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN: W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_DETAIL_COLUMN,
        }, inplace=True)
        df_in_Consumption = df_in_Consumption[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_DETAIL_COLUMN, SITE_AP2_MAP_SHIP_TO_COLUMN,
        ]].drop_duplicates()
        print_df(df_in_Production, 'STEP3 by 1.2.4  ____ df_in_Production .... final')

        # ====================> STEP3 by 1 (End)




        # ====================> STEP3 by 2 (Start) -> df_in_Demand DataFrame modify

        # 2.1 df_in_Demand Version별 분리
        df_PeggingCurr = df_in_Demand[df_in_Demand[VERSION_NAME_COLUMN] == SOURCE_VERSION].copy()
        print_df(df_PeggingCurr, f'STEP3 by 2.1  ____ df_PeggingCurr .... version : {SOURCE_VERSION}')

        df_PeggingPrev = df_in_Demand[df_in_Demand[VERSION_NAME_COLUMN] == pre_version].copy()
        print_df(df_PeggingPrev, f'STEP3 by 2.1  ____ df_PeggingPrev .... version : {pre_version}')

        df_Pegging = pd.merge(df_PeggingCurr, df_PeggingPrev, how='left', on=[ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_Pegging, 'STEP3 by 2.1  ____ df_Pegging .... version merge')

        int_columns = [
            W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x', W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x', W_TOTAL_SHORT_QUANTITY_COLUMN+'_x',
            W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_y', W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_y', W_TOTAL_SHORT_QUANTITY_COLUMN+'_y',
        ]
        for col in int_columns:
            df_Pegging[col] = df_Pegging[col].fillna(0).astype(int)

        print_df(df_Pegging, 'STEP3 by 2.1  ____ df_Pegging .... version merge final')


        #   2.4.2 컬럼명 변경 및 추가
        df_Pegging[HUB_PSI_PLAN_DMD_COLUMN] = df_Pegging[W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x']
        df_Pegging[HUB_PSI_PLAN_RTF_COLUMN] = df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        df_Pegging[HUB_PSI_PLAN_GI_QTY_COLUMN] = df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        df_Pegging[HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN] = (
               df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x'] / df_Pegging[W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x'] * 100
        ).replace([np.inf, -np.inf], 0).map("{:.1f}".format)
        df_Pegging[HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN] = df_Pegging[HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN].fillna(0).astype(float)
        df_Pegging[HUB_PSI_PLAN_SALES_COLUMN] = df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        df_Pegging[HUB_PSI_PLAN_SHORT_COLUMN] = (
                df_Pegging[W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x'] - df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        )
        df_Pegging[HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN] = df_Pegging[HUB_PSI_PLAN_SHORT_COLUMN]
        df_Pegging[HUB_PSI_PLAN_SAFETY_STOCK_COLUMN] = df_Pegging[W_TARGET_INVENTORY_COLUMN+'_x']
        print_df(df_Pegging, 'STEP3 by 2.2  ____ df_Pegging .... column add')

        df_Pegging.rename(columns={
            VERSION_NAME_COLUMN+'_x': VERSION_NAME_COLUMN,
            W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x': W_DEMAND_QUANTITY_TO_SCS_COLUMN,
            W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x': W_DEMAND_FULFILLED_QUANTITY_COLUMN,
            W_TOTAL_SHORT_QUANTITY_COLUMN+'_x': W_TOTAL_SHORT_QUANTITY_COLUMN,
            W_TARGET_INVENTORY_COLUMN+'_x': W_TARGET_INVENTORY_COLUMN,
            W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN+'_x': W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN,
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN+'_x': W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN,
            W_ONHAND_QUANTITY_COLUMN+'_x': W_ONHAND_QUANTITY_COLUMN,
            W_BEGINNING_ON_HAND_COLUMN+'_x': W_BEGINNING_ON_HAND_COLUMN,
            W_EXPECTED_RECEIPTS_COLUMN+'_x': W_EXPECTED_RECEIPTS_COLUMN,
            W_ENDDING_ON_HAND_COLUMN+'_x': W_ENDDING_ON_HAND_COLUMN,
            W_INFINITE_METERIAL_NODE_COLUMN+'_x': W_INFINITE_METERIAL_NODE_COLUMN,
        }, inplace=True)
        print_df(df_Pegging, 'STEP3 by 2.4  ____ df_Pegging .... column rename')



        # 2.5 df_Pegging final
        df_Pegging = df_Pegging[df_Pegging2_columns].drop_duplicates()
        int_columns = [
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN, W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN,
            W_BEGINNING_ON_HAND_COLUMN, W_ENDDING_ON_HAND_COLUMN, W_EXPECTED_RECEIPTS_COLUMN,
            HUB_PSI_PLAN_GI_QTY_COLUMN, HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN, HUB_PSI_PLAN_SALES_COLUMN,
            HUB_PSI_PLAN_DMD_COLUMN, HUB_PSI_PLAN_SHORT_COLUMN, HUB_PSI_PLAN_RTF_COLUMN,
            HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN, HUB_PSI_PLAN_SAFETY_STOCK_COLUMN,
        ]
        for col in int_columns:
            df_Pegging[col] = df_Pegging[col].fillna(0)

        print_df(df_Pegging, 'STEP3 by 2.5 ____ df_Pegging .... final')

        # ====================> STEP3 by 2 (End)



        # ====================> STEP3 by 3 (Start) -> df_HubPSIPlan 구성

        # 3.1 df_in_Production, df_in_Consumption concat
        df_HubPSIPlan = pd.concat([df_Pegging, df_in_Production, df_in_Consumption]).drop_duplicates()
        print_df(df_HubPSIPlan, 'STEP3 by 3.1.1 ____ df_HubPSIPlan .... concat(df_Pegging, df_in_Production, df_in_Consumption)')
        int_columns = [
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_DETAIL_COLUMN, W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_DETAIL_COLUMN,
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN, W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN,
        ]
        for col in int_columns:
            df_HubPSIPlan[col] = df_HubPSIPlan[col].fillna(0)

        df_HubPSIPlan[HUB_PSI_PLAN_SHIPMENT_COLUMN] = df_HubPSIPlan[W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN]
        df_HubPSIPlan[HUB_PSI_PLAN_ARRIVAL_COLUMN] = df_HubPSIPlan[W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN]
        df_HubPSIPlan[HUB_PSI_PLAN_SHIPMENT_DETAIL_COLUMN] = df_HubPSIPlan[W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_DETAIL_COLUMN]
        df_HubPSIPlan[HUB_PSI_PLAN_ARRIVAL_DETAIL_COLUMN] = df_HubPSIPlan[W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_DETAIL_COLUMN]
        print_df(df_HubPSIPlan, 'STEP3 by 3.1.2 ____ df_HubPSIPlan .... columns modify')


        # 3.2 df_in_SiteAP2Map merge
        df_HubPSIPlan = pd.merge(df_HubPSIPlan, df_in_SiteAP2Map, how='left', on=[VERSION_NAME_COLUMN, LOCATION_COLUMN])
        print_df(df_HubPSIPlan, 'STEP3 by 3.2.1 ____ df_HubPSIPlan .... merge[df_HubPSIPlan, df_in_SiteAP2Map]')

        df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN] = np.where(
            df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN+'_x'].notna(), df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN+'_x'],
            df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN+'_y']
        )
        df_HubPSIPlan = df_HubPSIPlan.drop(columns=[SITE_AP2_MAP_SHIP_TO_COLUMN+'_x', SITE_AP2_MAP_SHIP_TO_COLUMN+'_y'])

        df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN] = df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN].astype(str)
        df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN] = df_HubPSIPlan[SITE_AP2_MAP_SHIP_TO_COLUMN].str.replace(r'\.0$', '', regex=True)

        str_columns = [LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, SITE_AP2_MAP_SHIP_TO_COLUMN]
        for col in str_columns:
            df_HubPSIPlan[col] = df_HubPSIPlan[col].fillna('-').astype(str)

        print_df(df_HubPSIPlan, 'STEP3 by 3.2.2 ____ df_HubPSIPlan .... columns modify')


        # 3.3 df_HubPSIPlan, df_in_SSMonitor join
        df_in_SSMonitor[SALES_DOMAIN_AP2_COLUMN] = df_in_SSMonitor[SALES_DOMAIN_AP2_COLUMN].astype(str)
        df_in_SSMonitor[SALES_DOMAIN_AP2_COLUMN] = df_in_SSMonitor[SALES_DOMAIN_AP2_COLUMN].str.replace(r'\.0$', '', regex=True)
        df_HubPSIPlan = pd.merge(df_HubPSIPlan, df_in_SSMonitor, how='left',
                                   left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, SITE_AP2_MAP_SHIP_TO_COLUMN],
                                   right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN])
        df_HubPSIPlan.drop(columns=[SALES_DOMAIN_AP2_COLUMN], inplace=True)
        df_HubPSIPlan.rename(columns={TRANS_MODE_COLUMN+'_x': TRANS_MODE_COLUMN,}, inplace=True)
        print_df(df_HubPSIPlan, 'STEP3 by 3.3.1 ____ df_HubPSIPlan .... merge[df_HubPSIPlan, df_in_SSMonitor]')

        columns = [
            HUB_PSI_PLAN_AGING_OVER_30DAY_COLUMN, HUB_PSI_PLAN_AGING_OVER_60DAY_COLUMN,
            HUB_PSI_PLAN_AGING_RATE_OVER_30DAT_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_60DAT_COLUMN,
        ]
        for column in columns:
            df_HubPSIPlan[column] = 0

        print_df(df_HubPSIPlan, 'STEP3 by 3.3.2 ____ df_HubPSIPlan .... column rename')


        # 3.5 컬럼명 변경
        df_HubPSIPlan.rename(columns={
            W_BEGINNING_ON_HAND_COLUMN: HUB_PSI_PLAN_BOH_COLUMN,
            W_ENDDING_ON_HAND_COLUMN: HUB_PSI_PLAN_EOH_COLUMN,
            W_EXPECTED_RECEIPTS_COLUMN: HUB_PSI_PLAN_INTRANSIT_COLUMN,
            SITE_AP2_MAP_SHIP_TO_COLUMN: SALES_DOMAIN_AP2_COLUMN,
            SS_MONITOR_BUILDAHEAD_LIMIT_COLUMN: HUB_PSI_PLAN_BUILD_AHEAD_COLUMN,
            SS_MONITOR_SS_TARGET_QTY_COLUMN: HUB_PSI_PLAN_SS_TARGET_Q_COLUMN,
            SS_MONITOR_SS_TARGET_TIME_COLUMN: HUB_PSI_PLAN_SS_TARGET_W_COLUMN,
        }, inplace=True)
        df_HubPSIPlan[HUB_PSI_PLAN_INVENTORY_COLUMN] = df_HubPSIPlan[HUB_PSI_PLAN_EOH_COLUMN]
        df_HubPSIPlan[HUB_PSI_PLAN_SS_TARGET_VIO_COLUMN] = df_HubPSIPlan[SS_MONITOR_ARRIVAL_SS_COLUMN] - df_HubPSIPlan[HUB_PSI_PLAN_SS_TARGET_Q_COLUMN]
        print_df(df_HubPSIPlan, 'STEP3 by 3.5 ____ df_HubPSIPlan .... column rename')



        # 3.6 널 값 '-' 처리 및 기타 타입 설정
        int_columns = [
            HUB_PSI_PLAN_DMD_COLUMN, HUB_PSI_PLAN_RTF_COLUMN, HUB_PSI_PLAN_GI_QTY_COLUMN, HUB_PSI_PLAN_SALES_COLUMN, HUB_PSI_PLAN_SHORT_COLUMN,
            HUB_PSI_PLAN_BOH_COLUMN, HUB_PSI_PLAN_EOH_COLUMN, HUB_PSI_PLAN_INTRANSIT_COLUMN, HUB_PSI_PLAN_INVENTORY_COLUMN,
            HUB_PSI_PLAN_SHIPMENT_DETAIL_COLUMN, HUB_PSI_PLAN_ARRIVAL_DETAIL_COLUMN, HUB_PSI_PLAN_AGING_OVER_30DAY_COLUMN,
            HUB_PSI_PLAN_AGING_OVER_60DAY_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_30DAT_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_60DAT_COLUMN,
            HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN, HUB_PSI_PLAN_SAFETY_STOCK_COLUMN,
            HUB_PSI_PLAN_BUILD_AHEAD_COLUMN, HUB_PSI_PLAN_SS_TARGET_W_COLUMN, HUB_PSI_PLAN_SS_TARGET_Q_COLUMN,
            HUB_PSI_PLAN_SS_TARGET_VIO_COLUMN,
        ]
        for col in int_columns:
            df_HubPSIPlan[col] = df_HubPSIPlan[col].fillna(0).astype('Int64')


        df_HubPSIPlan[TIME_WEEK_COLUMN] = pd.to_numeric(df_HubPSIPlan[TIME_WEEK_COLUMN], errors='coerce')
        columns = df_common_columns + df_HUBPSIPlan_columns
        df_HubPSIPlan = df_HubPSIPlan[columns].drop_duplicates()
        print_df(df_HubPSIPlan, 'STEP3 by 3.6 ____ df_HubPSIPlan .... final')

        # ====================> STEP3 by 3 (End)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # 기준정보
        initial_week = int(ap2_start_week)   #202427
        prior_weeks = int(4)  # 이전 4주
        following_weeks = int(4)  # 다음 4주(current_week 포함)

        # 기준 주차의 위치 (index 값) 및 start와 end 위치 계산
        initial_idx = df_in_AllWeek[df_in_AllWeek[TIME_WEEK_COLUMN] == initial_week].index[0]
        start_idx = max(initial_idx - prior_weeks, 0)  # 시작 index는 0보다 작지 않도록 처리
        end_idx = min(initial_idx - 1, len(df_in_AllWeek) - 1)  # 끝 index는 DataFrame 범위를 초과하지 않도록 처리

        # 1 ap2_start_week 기준 이전 4주 가져오기
        df_before_4Week = df_in_AllWeek.iloc[start_idx:end_idx + 1].copy()
        print_df(df_before_4Week, 'STEP4 by 1 ____ df_before_4Week .... range')


        # 2 실적수량 가져오기
        #   2.1 ap2_start_week 이전 4주 실적 가져오기.
        if not df_in_HUBPSIActual.empty:
            df_in_HUBPSIActual[SALES_DOMAIN_AP2_COLUMN] = df_in_HUBPSIActual[SALES_DOMAIN_AP2_COLUMN].astype(str)

            df_HUBPSIActual = pd.merge(df_before_4Week, df_in_HUBPSIActual, how='inner', on=[TIME_WEEK_COLUMN])
            print_df(df_HUBPSIActual, 'STEP4 by 2.1 ____ df_HUBPSIActual .... merge[df_before_4Week, df_in_HUBPSIActual]')

            #   2.2 컬럼 select
            columns = [ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, HUB_PSI_ACTUAL_GI_QTY_COLUMN]
            df_HUBPSIActual = df_HUBPSIActual[columns].drop_duplicates()
            print_df(df_HUBPSIActual, 'STEP4 by 2.2 ____ df_HUBPSIActual .... column select')

            #   2.3 실적 수량을 QTY 로 변경
            df_HUBPSIActual.rename(columns={HUB_PSI_ACTUAL_GI_QTY_COLUMN: QTY_COLUMN}, inplace=True)
            df_HUBPSIActual[QTY_COLUMN] = df_HUBPSIActual[QTY_COLUMN].fillna(np.nan).astype('float64')
            print_df(df_HUBPSIActual, 'STEP4 by 2.3 ____ df_HUBPSIActual .... column modify')

        else:
            columns = [ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN]
            df_HUBPSIActual = df_HubPSIPlan[columns].copy()

            df_HUBPSIActual = set_unique_combinations(df_HUBPSIActual, df_before_4Week, columns)
            df_HUBPSIActual[QTY_COLUMN] = 0
            print_df(df_HUBPSIActual, 'STEP4 by 2.1 ____ df_HUBPSIActual .... week add')


        # 3 계획정보 편집
        df_SetHubPSIPlan = df_HubPSIPlan.copy()
        columns = [ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN]
        df_SetHubPSIPlan = df_SetHubPSIPlan[columns].drop_duplicates()
        df_SetHubPSIPlan.rename(columns={HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN: QTY_COLUMN}, inplace=True)
        print_df(df_SetHubPSIPlan, 'STEP4 by 3.1 ____ df_SetHubPSIPlan .... columns select')



        # 4 계획과 실적 합치기
        #   4.1  df_SetHubPSIPlan, df_HUBPSIActual concat
        df_eoh_w = pd.concat([df_HUBPSIActual, df_SetHubPSIPlan]).drop_duplicates()
        df_eoh_w[QTY_COLUMN] = df_eoh_w[QTY_COLUMN].fillna(np.nan).astype('float64')
        print_df(df_eoh_w, 'STEP4 by 4.1 ____ df_eoh_w .... concat')

        #   4.2 실적 + 계획 모든 주차 생성
        df_plan_week = df_in_MDMHorizon[[TIME_WEEK_COLUMN]].copy().drop_duplicates()
        df_all_actual_plan_week = pd.concat([df_before_4Week, df_plan_week], ignore_index=True).drop_duplicates()
        print_df(df_all_actual_plan_week, 'STEP4 by 4.2 ____ df_all_actual_plan_week .... all actual_plan week make')

        #   4.3 eoh 계산 위한 주차 채워넣기
        columns = [ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN]
        df_missing_rows = set_unique_combinations(df_eoh_w, df_all_actual_plan_week, columns)
        df_eoh_w = pd.concat([df_eoh_w, df_missing_rows], ignore_index=True).drop_duplicates()
        print_df(df_eoh_w, 'STEP4 by 4.3 ____ df_eoh_w .... week add')

        #   4.4 수량 sum
        groupby_columns = [ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN]
        sum_columns = [QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_eoh_w = df_eoh_w.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        # df_eoh_w.reset_index(drop=True, inplace=True)
        df_eoh_w[TIME_WEEK_COLUMN] = pd.to_numeric(df_eoh_w[TIME_WEEK_COLUMN], errors='coerce')
        print_df(df_eoh_w, 'STEP4 by 4.4 ____ df_eoh_w .... groupby')



        # 5 EOH W 계산
        def calculate_avg(df_group):
            # 그룹 데이터를 바로 처리 (numpy 적용)
            weeks = df_group[TIME_WEEK_COLUMN].values
            qty = df_group[QTY_COLUMN].values

            avg_results = []
            week_size = len(df_AllWeek) - 1  # 전체 데이터 길이

            for i in range(len(weeks)):
                week = weeks[i]
                if week < initial_week:
                    continue

                # 인덱스 시작 및 종료 탐색 최적화
                initial_idx = df_AllWeek_index.get(week, None)  # 미리 저장된 map을 활용, 없으면 None
                if initial_idx is None:
                    continue  # 해당 주가 없으면 건너뜀

                start_idx = max(initial_idx - prior_weeks, 0)
                end_idx = min(initial_idx + following_weeks, week_size)

                start_week = df_AllWeek_array[start_idx]
                end_week = df_AllWeek_array[end_idx]

                # 벡터화된 마스크 사용
                mask = (weeks >= start_week) & (weeks <= end_week)
                avg_qty = round(np.mean(qty[mask]), 1)

                avg_results.append({
                    ITEM_COLUMN: df_group[ITEM_COLUMN].iloc[0],
                    LOCATION_COLUMN: df_group[LOCATION_COLUMN].iloc[0],
                    SALES_DOMAIN_AP2_COLUMN: df_group[SALES_DOMAIN_AP2_COLUMN].iloc[0],
                    TIME_WEEK_COLUMN: week,
                    AVG_COLUMN: avg_qty
                })

            return avg_results

        #   5.1 전체 데이터셋 사전 준비 (벡터화 또는 데이터 인덱싱 개선)
        df_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].copy().drop_duplicates().reset_index(drop=True)
        df_AllWeek_array = df_AllWeek[TIME_WEEK_COLUMN].values  # numpy array로 전환
        df_AllWeek_index = {week: idx for idx, week in enumerate(df_AllWeek_array)}  # map으로 미리 계산된 인덱스

        #   5.2 그룹별 처리
        groupby_columns = [ITEM_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN]
        df_eoh_w_grouped = df_eoh_w.groupby(groupby_columns)

        #   5.3 순차적으로 처리하여 계산
        results = []
        for _, group in df_eoh_w_grouped:
            group_results = calculate_avg(group)
            results.extend(group_results)  # 결과를 리스트에 추가

        #   5.4 결과 데이터프레임으로 변환
        df_eoh_w_results = pd.DataFrame(results)
        df_eoh_w_results[AVG_COLUMN] = df_eoh_w_results[AVG_COLUMN].fillna(0).astype(float)
        df_eoh_w_results.rename(columns={AVG_COLUMN: HUB_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN}, inplace=True)
        print_df(df_eoh_w_results, 'STEP4 by 5 ____ df_eoh_w_results .... final')



        # 6 df_out_HUBPSIPlan create
        df_out_HUBPSIPlan = pd.merge(df_HubPSIPlan, df_eoh_w_results, how='left',
                                     on=[ITEM_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_out_HUBPSIPlan, 'STEP4 by 6.1 ____ df_out_HUBPSIPlan .... merge[df_HubPSIPlan, df_eoh_w_results]')


        # 7 실적 + 결과 합치기
        df_HUBPSIActualCopy = df_HUBPSIActual.copy()
        df_HUBPSIActualCopy.drop(columns=[QTY_COLUMN], inplace=True)
        df_HUBPSIActualCopy[VERSION_NAME_COLUMN] = paramOutVersion
        df_HUBPSIActualCopy[TIME_WEEK_COLUMN] = df_HUBPSIActualCopy[TIME_WEEK_COLUMN].astype(int)
        df_out_HUBPSIPlan = pd.concat([df_out_HUBPSIPlan, df_HUBPSIActualCopy], ignore_index=True)
        print_df(df_out_HUBPSIPlan, 'STEP4 by 7.1 ____ df_out_HUBPSIPlan .... concat[df_out_HUBPSIPlan, df_HUBPSIActualCopy]')

        df_out_HUBPSIPlan[VERSION_NAME_COLUMN] = paramOutVersion
        columns = df_common_columns + df_HUBPSIPlan_columns + df_HUBPSIPlan_eoh_columns
        df_out_HUBPSIPlan = df_out_HUBPSIPlan[columns].drop_duplicates()

        int_columns = [
            HUB_PSI_PLAN_DMD_COLUMN, HUB_PSI_PLAN_RTF_COLUMN, HUB_PSI_PLAN_GI_QTY_COLUMN, HUB_PSI_PLAN_SALES_COLUMN, HUB_PSI_PLAN_SHORT_COLUMN,
            HUB_PSI_PLAN_BOH_COLUMN, HUB_PSI_PLAN_EOH_COLUMN, HUB_PSI_PLAN_INTRANSIT_COLUMN, HUB_PSI_PLAN_INVENTORY_COLUMN,
            HUB_PSI_PLAN_SHIPMENT_DETAIL_COLUMN, HUB_PSI_PLAN_ARRIVAL_DETAIL_COLUMN, HUB_PSI_PLAN_AGING_OVER_30DAY_COLUMN,
            HUB_PSI_PLAN_AGING_OVER_60DAY_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_30DAT_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_60DAT_COLUMN,
            HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN, HUB_PSI_PLAN_SAFETY_STOCK_COLUMN,
            HUB_PSI_PLAN_BUILD_AHEAD_COLUMN, HUB_PSI_PLAN_SS_TARGET_W_COLUMN, HUB_PSI_PLAN_SS_TARGET_Q_COLUMN,
            HUB_PSI_PLAN_SS_TARGET_VIO_COLUMN,
        ]
        for col in int_columns:
            df_out_HUBPSIPlan[col] = df_out_HUBPSIPlan[col].fillna(0).astype('Int64')

        print_df(df_out_HUBPSIPlan, 'STEP4 by 7.2 ____ df_out_HUBPSIPlan .... modify final')



        # 8 HUB Location 구성
        #   8.1 SOW merge
        df_out_HUBPSIPlan = pd.merge(df_out_HUBPSIPlan, df_in_SOPW, how='inner',
                                     left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN]).drop_duplicates()
        print_df(df_out_HUBPSIPlan, 'STEP4 by 8.1 ____ df_out_HUBPSIPlan .... merge[df_out_HUBPSIPlan, df_in_SOPW]')

        df_out_HUBPSIPlan = df_out_HUBPSIPlan.drop(labels=[
            TO_LOCATION_TO_LOCATION_COLUMN, SUB_LOCATION_X_COLUMN, SUB_LOCATION_Y_COLUMN,
        ], axis=1)

        df_out_HUBPSIPlan.rename(columns={
            LOCATION_X_COLUMN: LOCATION_COLUMN,
            LOCATION_Y_COLUMN: SUB_LOCATION_COLUMN,
            TRANS_MODE_COLUMN+'_y': TRANS_MODE_COLUMN,
        }, inplace=True)
        print_df(df_out_HUBPSIPlan, 'STEP4 by 8.2 ____ df_out_HUBPSIPlan .... colunms rename')

        columns = df_common_columns + df_HUBPSIPlan_columns + df_HUBPSIPlan_eoh_columns
        df_out_HUBPSIPlan = df_out_HUBPSIPlan[columns].drop_duplicates()
        print_df(df_out_HUBPSIPlan, 'STEP4 by 8.3 ____ df_out_HUBPSIPlan .... colunms reselect')



        # 9 BODItem merge
        #   9.1
        df_out_HUBPSIPlan = pd.merge(df_out_HUBPSIPlan, df_in_BODItem, how='left',
                                     left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]).drop_duplicates()
        print_df(df_out_HUBPSIPlan, 'STEP4 by 9.1.1 ____ df_out_HUBPSIPlan .... merge[df_HubPSIPlan, df_in_BODItem]')

        df_out_HUBPSIPlan.rename(columns={
            LOCATION_X_COLUMN: LOCATION_COLUMN,
            LOCATION_Y_COLUMN: TO_LOCATION_TO_LOCATION_COLUMN,
            SUB_LOCATION_X_COLUMN: SUB_LOCATION_COLUMN,
        }, inplace=True)
        print_df(df_out_HUBPSIPlan, 'STEP4 by 9.1.2 ____ df_out_HUBPSIPlan .... colunms rename')

        #   9.2 df_in_BODItem 의 [Sub Site Stage] 가 "DC_HUB","DC_HUB_MC", "DC_HUB_MC_AP2"가 아니면 Sub Location 을 '-' 처리
        df_out_HUBPSIPlan.loc[~df_out_HUBPSIPlan[LOCATION_SITE_STAGE].isin([DC_HUB_VALUE, DC_HUB_DC_VALUE, DC_HUB_MC_AP2_VALUE]), TO_LOCATION_TO_LOCATION_COLUMN] = '-'

        columns = df_common_columns + df_to_location_columns + df_HUBPSIPlan_columns + df_HUBPSIPlan_eoh_columns
        df_out_HUBPSIPlan = df_out_HUBPSIPlan[columns].drop_duplicates()
        print_df(df_out_HUBPSIPlan, 'STEP4 by 9.2 ____ df_out_HUBPSIPlan .... Sub Site Stage filter')



        # 10 최종 Output
        #   10.1 Hub PSI Plan_Dmd GI << 과거 4주는 Hub PSI Actual AP2_GI Qty, 미래 5주 이후는 Hub PSI Plan_Dmd 값 저장
        #       10.1.1 'Time.[Week]' 기준으로 quick lookup을 위해 actual을 dictionary로 변환
        actual_dict = df_HUBPSIActual.set_index(TIME_WEEK_COLUMN)[QTY_COLUMN].to_dict()

        #       10.1.2 벡터화 조건 처리 > 'Time.[Week]'가 `initial_week`보다 작은 경우
        mask_actual_weeks = (df_out_HUBPSIPlan[TIME_WEEK_COLUMN] < initial_week) & (df_out_HUBPSIPlan[TIME_WEEK_COLUMN].isin(actual_dict))

        #       10.1.3 새로운 gi 설정
        df_out_HUBPSIPlan[HUB_PSI_PLAN_DMD_GI_COLUMN] = 0  # 기본값 초기화
        df_out_HUBPSIPlan.loc[mask_actual_weeks, HUB_PSI_PLAN_DMD_GI_COLUMN] = df_out_HUBPSIPlan.loc[mask_actual_weeks, TIME_WEEK_COLUMN].map(actual_dict)  # actual 값 매핑
        df_out_HUBPSIPlan.loc[~mask_actual_weeks, HUB_PSI_PLAN_DMD_GI_COLUMN] = df_out_HUBPSIPlan.loc[~mask_actual_weeks, HUB_PSI_PLAN_DMD_COLUMN]  # 나머지는 qty로 설정
        print_df(df_out_HUBPSIPlan, 'STEP4 by 10.1 ____ df_out_HUBPSIPlan .... final')

        #   10.2 컬럼정리
        str_columns = [ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, SALES_DOMAIN_AP2_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN]
        for column in str_columns:
            df_out_HUBPSIPlan[column] = df_out_HUBPSIPlan[column].replace({pd.NA: '-', np.nan: '-', '<NA>': '-', 'nan': '-'})
            df_out_HUBPSIPlan[column] = df_out_HUBPSIPlan[column].fillna('-').astype(str)

        df_out_HUBPSIPlan[HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN] = df_out_HUBPSIPlan[HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN].astype(str)
        df_out_HUBPSIPlan[HUB_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN] = df_out_HUBPSIPlan[HUB_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN].astype(str)
        int_columns = [HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN, HUB_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN]
        for column in int_columns:
            # 값들을 일관된 None 처리: pd.NA, np.nan, '<NA>' 등
            df_out_HUBPSIPlan[column] = df_out_HUBPSIPlan[column].replace({pd.NA: None, np.nan: None, '<NA>': None, 'nan': None, np.inf: None, -np.inf: None, 'inf': None, '-inf': None})

            # 숫자로 변환 가능한 값만 처리 (coerce를 사용해 변환 불가능한 값은 NaN으로 대체)
            df_out_HUBPSIPlan[column] = pd.to_numeric(df_out_HUBPSIPlan[column], errors='coerce')

            # NaN 값은 0으로 채우고 float로 변환
            df_out_HUBPSIPlan[column] = df_out_HUBPSIPlan[column].fillna(0).astype('float')

        df_out_HUBPSIPlan[VERSION_NAME_COLUMN] = paramOutVersion
        print_df(df_out_HUBPSIPlan, 'STEP4 by 10.2 ____ df_out_HUBPSIPlan .... final')

        # ====================> STEP4 by 4 (End)


        # # @ 포함 여부 확인 및 @ 이후 값 추출을 벡터화 처리
        # df_out_HUBPSIPlan[SALES_DOMAIN_AP2_COLUMN] = np.where(
        #     df_out_HUBPSIPlan[LOCATION_COLUMN].str.contains('@', na=False),  # @ 포함 여부 확인
        #     df_out_HUBPSIPlan[LOCATION_COLUMN].str.split('@').str[1],        # @ 이후 값 추출
        #     df_out_HUBPSIPlan[SALES_DOMAIN_AP2_COLUMN]                       # 기존 값 유지
        # )

        # # @ 포함된 행만 선택적으로 처리
        # mask = df_out_HUBPSIPlan[LOCATION_COLUMN].str.contains('@', na=False)
        # df_out_HUBPSIPlan.loc[mask, SALES_DOMAIN_AP2_COLUMN] = df_out_HUBPSIPlan.loc[mask, LOCATION_COLUMN].str.split('@').str[1]

        # 먼저 복사본을 만들어 원본 데이터 보존
        new_lo = df_out_HUBPSIPlan[LOCATION_COLUMN].copy()
        new_ap = df_out_HUBPSIPlan[SALES_DOMAIN_AP2_COLUMN].copy()

        # @ 포함된 행 찾기
        mask = df_out_HUBPSIPlan[LOCATION_COLUMN].str.contains('@', na=False)

        # @ 포함된 행만 처리
        split_data = df_out_HUBPSIPlan.loc[mask, LOCATION_COLUMN].str.split('@', expand=True)

        # 해당 행들만 업데이트
        new_lo[mask] = split_data[0]
        new_ap[mask] = split_data[1].astype(str)

        # 최종 결과 적용
        df_out_HUBPSIPlan[LOCATION_COLUMN] = new_lo
        df_out_HUBPSIPlan[SALES_DOMAIN_AP2_COLUMN] = new_ap

        groupby_columns = [VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
                           SALES_DOMAIN_AP2_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,]
        sum_columns = [
            HUB_PSI_PLAN_DMD_COLUMN, HUB_PSI_PLAN_RTF_COLUMN, HUB_PSI_PLAN_GI_QTY_COLUMN, HUB_PSI_PLAN_DMD_FILL_RATE_COLUMN,
            HUB_PSI_PLAN_SALES_COLUMN, HUB_PSI_PLAN_SHORT_COLUMN,
            HUB_PSI_PLAN_BOH_COLUMN, HUB_PSI_PLAN_EOH_COLUMN, HUB_PSI_PLAN_INTRANSIT_COLUMN, HUB_PSI_PLAN_INVENTORY_COLUMN,
            HUB_PSI_PLAN_SHIPMENT_DETAIL_COLUMN, HUB_PSI_PLAN_ARRIVAL_DETAIL_COLUMN, HUB_PSI_PLAN_AGING_OVER_30DAY_COLUMN,
            HUB_PSI_PLAN_AGING_OVER_60DAY_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_30DAT_COLUMN, HUB_PSI_PLAN_AGING_RATE_OVER_60DAT_COLUMN,
            HUB_PSI_PLAN_SHORT_BY_ORG_COLUMN, HUB_PSI_PLAN_SAFETY_STOCK_COLUMN,
            HUB_PSI_PLAN_BUILD_AHEAD_COLUMN, HUB_PSI_PLAN_SS_TARGET_W_COLUMN, HUB_PSI_PLAN_SS_TARGET_Q_COLUMN,
            HUB_PSI_PLAN_SS_TARGET_VIO_COLUMN, HUB_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN, HUB_PSI_PLAN_DMD_GI_COLUMN,
        ]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_out_HUBPSIPlan[TIME_WEEK_COLUMN] = df_out_HUBPSIPlan[TIME_WEEK_COLUMN].astype('str')
        df_out_HUBPSIPlan = df_out_HUBPSIPlan.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)

        step('=====> STEP4 End')
        



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_HUBPSIPlan, 'output table create .... df_out_HUBPSIPlan', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_HUBPSIPlan = pd.DataFrame(columns=df_HUBPSIPlan_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_HUBPSIPlan = pd.DataFrame(columns=df_HUBPSIPlan_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
