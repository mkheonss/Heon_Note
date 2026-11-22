"""
* 프로그램명
    - PY_MG_Capacity_SOPFrozen

* 내용
    - MP Engine 수행을 위한 기획생산 Inbound
    - MP Plan Batch Procedure에서 Call 하는 Program

* 변경이력
    - 2024.09.09 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CapaItemSite  : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Capa Item Site_Asn]}) on column.filter(Measure.[Capa Item Site_Asn] == "1");
    - df_in_CapaItemSiteMap : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Group].[Group ID] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Capa Item Site Map_Asn]}) on column.filter(Measure.[Capa Item Site Map_Asn] == "1");
    - df_in_CapaWeek      : Select (Version.[Version Name] * &PlanningHorizon * [Group].[Group ID] ) on row, ({Measure.[Capa Week_Qty]}) on column;
    - df_in_CapaPeriod    : Select (Version.[Version Name] * [Time].[Week] * [To Time].[To Week] * [Group].[Group ID] ) on row, ({Measure.[Capa Period_Qty]}) on column;
    - df_in_ItemSiteAsn   : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Flag], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag] == true);
    - df_in_BOMMaster     : Select (Version.[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column;
    - df_in_BODItem       : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT]}) on column;
    - df_in_TactTime      : Select (Version.[Version Name]  * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  where {  Measure.[Tact Time_Valid Asn] == true};
    - df_PlanStartEndWeek : Select (Version.[Version Name]) on row, ({Measure.[MP Plan End Week], Measure.[MP Plan Start Week]}) on column;
    - df_in_PlanningWeek  : Select ( &PlanningHorizon ) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};

* Flow Summary
    - STEP1. BOD List 발췌 기준으로 Item Site Asn 조합하여  BOD Item 을 구성한다.
    - STEP2. BOD Prod Set 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_SOPFIXCapacity
    - df_out_SOPFIXSimultaneous
    - df_out_SOPFIXConsumeAsn

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_MG_Capacity_SOPFrozen] for measures {[W Resource Base Capacity]}
        using scope (&MPV, &PlanningHorizon)
        using arguments {
        (ExecutionMode, "MediumWeight"),
        ("IncludeNullRows", "False"),
        (paramOutVersion , "CWV_MP"),
        (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ),
        ([Param.o9_sys_log_level], "DEBUG")
      };

* Output Query
    - df_out_SOPFIXCapacity / MG:  001.022W Solver Inputs Capacity
        Select (&MPV * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row,
            ({  Measure.[W Resource Base Capacity], Measure.[W Coarser Maximum Utilization Quantity], Measure.[W Coarser Minimum Utilization Quantity]}) on column;

    - df_out_SOPFIXSimultaneous / MG: 001.005W Solver Inputs Resource Group Consumption Association
        Select (&MPV * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] * [Resource Group].[Resource Group] ) on row,
            ({Measure.[W Simultaneous Capacity Consumption Association]}) on column;

    - df_out_SOPFIXConsumeAsn / MG: 001.004W Solver Inputs Capacity Consumption Association
        Select (&MPV * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row,
            ({Measure.[W Input Resource Priority], Measure.[W Resource Category], Measure.[W Resource Consumed Quantity Per], Measure.[W Resource Consumption Association]}) on column;


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
str_instance = 'PY_MG_Capacity_SOPFrozen'
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
            df_in_CapaItemSite = read_csv_file("df_in_CapaItemSite")
            df_in_CapaItemSiteMap = read_csv_file("df_in_CapaItemSiteMap")
            df_in_CapaWeek = read_csv_file("df_in_CapaWeek")
            df_in_CapaPeriod = read_csv_file("df_in_CapaPeriod")
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_TactTime = read_csv_file("df_in_TactTime")
            df_in_BODItem = read_csv_file("df_in_BODItem")
            df_PlanStartEndWeek = read_csv_file("df_PlanStartEndWeek")
            df_in_PlanningWeek = read_csv_file("df_in_PlanningWeek")
    
    
        print_df(df_in_CapaItemSite, 'input table load .... df_in_CapaItemSite')
        print_df(df_in_CapaItemSiteMap, 'input table load .... df_in_CapaItemSiteMap')
        print_df(df_in_CapaWeek, 'input table load .... df_in_CapaWeek')
        print_df(df_in_CapaPeriod, 'input table load .... df_in_CapaPeriod')
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_BOMMaster, 'input table load .... df_in_BOMMaster')
        print_df(df_in_TactTime, 'input table load .... df_in_TactTime')
        print_df(df_in_BODItem, 'input table load .... df_in_BODItem')
        print_df(df_PlanStartEndWeek, 'input table load .... df_PlanStartEndWeek')
        print_df(df_in_PlanningWeek, 'input table load .... df_in_PlanningWeek')
    
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
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
    
        RESOURCE_COLUMN = 'Resource.[Resource]'
        RESOURCE_GROUP_COLUMN = '[Resource Group].[Resource Group]'
    
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
    
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_X_COLUMN = 'Item.[Item]_x'
        ITEM_Y_COLUMN = 'Item.[Item]_y'
        ITEM_TYPE_COLUMN = 'Item.[Item Type]'
        ITEM_PRODUCT_GROUPL_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_COLUMN = 'Item.[Product]'
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'
    
        BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'
        BOM_MASTER_PRIORITY_COLUMN = 'BOM Master_Priority'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'
    
        TRNAS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        BOD_ITEM_BOD_FROZEN_COLUMN = 'BOD Item_BOD Frozen'
        BOD_OTEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
    
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'
        CTN_GRP_CONST_GC_COLUMN = 'CTN Grp Const_GC'
        CTN_GRP_CONST_AP2_COLUMN = 'CTN Grp Const_AP2'
        CTN_GRP_CONST_APPLY_FLAG_COLUMN = 'CTN Grp Const_Apply Flag'
        CTN_GRP_CONST_START_WEEK_COLUMN = 'CTN Grp Const_Start Week'
        CTN_GRP_CONST_END_WEEK_COLUMN = 'CTN Grp Const_End Week'
        CTN_GRP_CONST_FROM_SITE_COLUMN = 'CTN Grp Const_From Site'
        CTN_GRP_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN = 'CTN Grp Const_Frozen SOP Override Qty'
        CTN_GRP_CONST_ECP_ECP_FLAG_COLUMN = 'CTN Grp Const Ecp_Ecp Flag'
    
        CTN_ITEM_CONST_GC_COLUMN = 'CTN Item Const_GC'
        CTN_ITEM_CONST_APPLY_FLAG_COLUMN = 'CTN Item Const_Apply Flag'
        CTN_ITEM_CONST_START_WEEK_COLUMN = 'CTN Item Const_Start Week'
        CTN_ITEM_CONST_END_WEEK_COLUMN = 'CTN Item Const_End Week'
        CTN_ITEM_CONST_FROZEN_WEEK_COLUMN = 'CTN Item Const_Frozen Week'
        CTN_ITEM_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN = 'CTN Item Const_Frozen SOP Override Qty'
    
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TO_TIME_WEEK_COLUMN = 'To Time.[To Week]'
    
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
    
        SITE_AP2_MAP_SHIP_TO_COLUMN = 'Site AP2 Map_Ship To'
        SITE_AP2_MAP_GC_COLUMN = 'Site AP2 Map_GC'
        SITE_AP2_MAP_STATUS_COLUMN = 'Site AP2 Map_Status'
        SITE_AP2_MAP_VAILD_FLAG_COLUMN = 'Site AP2 Map_Valid Flag'
    
        LINE_COLUMN = 'Line.[Line]'
        TACT_TIME_LOCK_FLAG_COLUMN = 'Tact Time_Lock Flag'
        TACT_TIME_PLAN_FLAG_COLUMN = 'Tact Time_Plan Flag'
        TACT_TIME_PRTY_COLUMN = 'Tact Time_Prty'
        TACT_TIME_TIME_COLUMN = 'Tact Time_Time'
        TACT_TIME_UOM_COLUMN = 'Tact Time_UOM'
        TACT_TIME_VAILD_ASN_COLUMN = 'Tact Time_Valid Asn'
    
        MP_PLAN_START_WEEK_COLUMN = 'MP Plan Start Week'
        MP_PLAN_END_WEEK_COLUMN = 'MP Plan End Week'
    
        W_RESOURCE_BASE_CAPACITY_COLUMN = 'W Resource Base Capacity'
        W_COARSER_MAXIMUM_U_QUANTITY_COLUMN = 'W Coarser Maximum Utilization Quantity'
        W_COARSER_MINIMUM_U_QUANTITY_COLUMN = 'W Coarser Minimum Utilization Quantity'
    
        W_SIMULTANEOUS_CCA_COLUMN = 'W Simultaneous Capacity Consumption Association'
    
        W_INPUT_RESOURCE_PRIORITY_COLUMN = 'W Input Resource Priority'
        W_RESOURCE_CATEGORY_COLUMN = 'W Resource Category'
        W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN = 'W Resource Consumed Quantity Per'
        W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN = 'W Resource Consumption Association'
    
        CAPA_ITEM_SITE_ASN_COLUMN = 'Capa Item Site_Asn'
        CAPA_ITEM_SITE_MAP_ASN_COLUMN = 'Capa Item Site Map_Asn'
        CAPA_PERIOD_QTY_COLUMN = 'Capa Period_Qty'
        CAPA_WEEK_QTY_COLUMN = 'Capa Week_Qty'
    
        FROM_SITE_COLUMN = 'FROM_SITE'
        TO_SITE_COLUMN = 'TO_SITE'
        FROM_WEEK_COLUMN = 'FROM_WEEK'
        TO_WEEK_COLUMN = 'TO_WEEK'
        RANK_COLUMN = 'RANK'
        QTY_COLUMN = 'QTY'
    
        ALL_VALUE = 'ALL'
        
        df_SOPFIXCapacity_columns = [
            VERSION_NAME_COLUMN, RESOURCE_COLUMN, FROM_SITE_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, QTY_COLUMN, W_COARSER_MAXIMUM_U_QUANTITY_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN, W_RESOURCE_BASE_CAPACITY_COLUMN
        ]
    
        df_SOPFIXSimultaneous_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN, RESOURCE_COLUMN, RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]
    
        df_SOPFIXConsumeAsn_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN, RESOURCE_COLUMN, W_RESOURCE_CATEGORY_COLUMN, W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN, W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN
        ]
    
        step('=====> STEP2 End')
    
    
    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # df_in_ItemSiteAsn 을 Location 과 Item 을 구분하여 데이터셋 분리
        df_ItemSiteAsnTemp1 = df_in_ItemSiteAsn.copy()
        df_ItemSiteAsnTemp2 = df_in_ItemSiteAsn.copy()
    
        drop_column = [col for col in list(df_ItemSiteAsnTemp1.columns) if col not in [LOCATION_COLUMN]]
        df_ItemSiteAsnLocation = df_ItemSiteAsnTemp1.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[LOCATION_COLUMN], keep='first')
        print_df(df_ItemSiteAsnLocation, 'STEP3 by 1 ____ df_ItemSiteAsnLocation .... Distinct')
    
        drop_column = [col for col in list(df_ItemSiteAsnTemp2.columns) if col not in [ITEM_COLUMN]]
        df_ItemSiteAsnItem = df_ItemSiteAsnTemp2.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[ITEM_COLUMN], keep='first')
        print_df(df_ItemSiteAsnItem, 'STEP3 by 1 ____ df_ItemSiteAsnItem .... Distinct')
    
        # MP Plan Week 가져오기
        mp_plan_start_week = get_first_value(df_PlanStartEndWeek, MP_PLAN_START_WEEK_COLUMN)
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')

        mp_plan_end_week = get_first_value(df_PlanStartEndWeek, MP_PLAN_END_WEEK_COLUMN)
        step(f'=====> mp_plan_end_week : {mp_plan_end_week}')
    
    
    
    
    
    
    
        # ====================> STEP3 by 1 (Start) -> create df_MFT_FrozenCapa

        # 1.1 MFT_CapaWeek create
        df_buf_MFT_CapaWeek = pd.merge(df_in_CapaWeek, df_in_CapaItemSite, how='inner', on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN])
        print_df(df_buf_MFT_CapaWeek, 'STEP3 by 1.1 ____ df_buf_MFT_CapaWeek .... merge[df_in_CapaWeek, df_in_CapaItemSite]')
    
        #   1.1.1 컬럼설정 및 변경
        df_buf_MFT_CapaWeek[FROM_WEEK_COLUMN] = df_buf_MFT_CapaWeek[TIME_WEEK_COLUMN]
        df_buf_MFT_CapaWeek[TO_WEEK_COLUMN] = df_buf_MFT_CapaWeek[TIME_WEEK_COLUMN]
        df_buf_MFT_CapaWeek[FROM_SITE_COLUMN] = df_buf_MFT_CapaWeek[LOCATION_COLUMN]
        df_buf_MFT_CapaWeek[RANK_COLUMN] = df_buf_MFT_CapaWeek.groupby([FROM_SITE_COLUMN, ITEM_COLUMN]).ngroup() + 1
        df_buf_MFT_CapaWeek.rename(columns={CAPA_WEEK_QTY_COLUMN: QTY_COLUMN}, inplace=True)
    
        #   1.1.2 필요컬럼 발췌
        df_buf_MFT_CapaWeek = df_buf_MFT_CapaWeek[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, ITEM_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, FROM_SITE_COLUMN, QTY_COLUMN, RANK_COLUMN
        ]]
        print_df(df_buf_MFT_CapaWeek, 'STEP3 by 1.1.2 ____ df_buf_MFT_CapaWeek .... filter')
    
        # 1.2 MFT_CapaPeriod create
        df_buf_MFT_CapaPeriod = pd.merge(df_in_CapaPeriod, df_in_CapaItemSite, how='inner', on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN])
        print_df(df_buf_MFT_CapaPeriod, 'STEP3 by 1.1.2 ____ df_buf_MFT_CapaPeriod .... merge[df_in_CapaPeriod, df_in_CapaItemSite]')
    
        #   1.2.1 컬럼설정 및 변경
        df_buf_MFT_CapaPeriod[FROM_WEEK_COLUMN] = df_buf_MFT_CapaPeriod[TIME_WEEK_COLUMN]
        df_buf_MFT_CapaPeriod[TO_WEEK_COLUMN] = df_buf_MFT_CapaPeriod[TO_TIME_WEEK_COLUMN]
        df_buf_MFT_CapaPeriod[FROM_SITE_COLUMN] = df_buf_MFT_CapaPeriod[LOCATION_COLUMN]
        df_buf_MFT_CapaPeriod[RANK_COLUMN] = df_buf_MFT_CapaPeriod.groupby([FROM_SITE_COLUMN, ITEM_COLUMN]).ngroup() + 1
        df_buf_MFT_CapaPeriod.rename(columns={CAPA_PERIOD_QTY_COLUMN: QTY_COLUMN}, inplace=True)
        print_df(df_buf_MFT_CapaPeriod, 'STEP3 by 1.2.1 ____ df_buf_MFT_CapaPeriod .... columns modify')
    
        #   1.2.2 필요컬럼 발췌
        df_buf_MFT_CapaPeriod = df_buf_MFT_CapaPeriod[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, ITEM_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, FROM_SITE_COLUMN, QTY_COLUMN, RANK_COLUMN
        ]]
        print_df(df_buf_MFT_CapaPeriod, 'STEP3 by 1.2.2 ____ df_buf_MFT_CapaPeriod .... filter')
    
        # 1.3 df_MFT_FrozenCapa create
        df_MFT_FrozenCapa = pd.concat([df_buf_MFT_CapaWeek, df_buf_MFT_CapaPeriod]).drop_duplicates()
    
        #   1.3.1 Resource make
        df_MFT_FrozenCapa[RANK_COLUMN] = df_MFT_FrozenCapa[RANK_COLUMN].astype(str)
        df_MFT_FrozenCapa[RESOURCE_COLUMN] = 'MFT_' + df_MFT_FrozenCapa[RANK_COLUMN]
    
        #   1.3.2 필요컬럼 발췌
        df_MFT_FrozenCapa = df_MFT_FrozenCapa[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, FROM_SITE_COLUMN, ITEM_COLUMN, RESOURCE_COLUMN, QTY_COLUMN
        ]]
        print_df(df_MFT_FrozenCapa, 'STEP3 by 1.3.2 ____ df_MFT_FrozenCapa .... filter')

        # ====================> STEP3 by 1 (End)
    
    
    
    
    
    
        # ====================> STEP3 by 2 (Start)

        # 2.1 MFT Capacity 입력 > df_MFT_SOPFIXCapacity create
        #   2.1.1 수량 설정
        df_MFT_SOPFIXCapacity = df_MFT_FrozenCapa.copy()
        df_MFT_SOPFIXCapacity[W_RESOURCE_BASE_CAPACITY_COLUMN] = None
        df_MFT_SOPFIXCapacity[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = None
        df_MFT_SOPFIXCapacity[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = None
    
        #   2.1.2 조건에 따라 값 할당
        conditions = [
            (df_MFT_SOPFIXCapacity[FROM_WEEK_COLUMN] == mp_plan_start_week),
            (df_MFT_SOPFIXCapacity[FROM_WEEK_COLUMN] > mp_plan_start_week),
            (df_MFT_SOPFIXCapacity[TO_WEEK_COLUMN] < mp_plan_end_week)
        ]
    
        choices_max_qty = [df_MFT_SOPFIXCapacity[QTY_COLUMN], 10000000, 10000000]
        choices_min_qty = [df_MFT_SOPFIXCapacity[QTY_COLUMN], 10000000, 10000000]
        choices_base_capacity = [df_MFT_SOPFIXCapacity[QTY_COLUMN], 0, 0]
    
        df_MFT_SOPFIXCapacity[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = np.select(conditions, choices_max_qty, default=None)
        df_MFT_SOPFIXCapacity[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = np.select(conditions, choices_min_qty, default=None)
        df_MFT_SOPFIXCapacity[W_RESOURCE_BASE_CAPACITY_COLUMN] = np.select(conditions, choices_base_capacity, default=None)
    
        #   2.1.3 필요컬럼 발췌
        df_MFT_SOPFIXCapacity = df_MFT_SOPFIXCapacity[[
            VERSION_NAME_COLUMN, RESOURCE_COLUMN, FROM_SITE_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, QTY_COLUMN,
            W_COARSER_MAXIMUM_U_QUANTITY_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN, W_RESOURCE_BASE_CAPACITY_COLUMN
        ]]
        print_df(df_MFT_SOPFIXCapacity, 'STEP3 by 2.1.3 ____ df_MFT_SOPFIXCapacity .... filter')
    
    
    
        # 2.2 df_buf_MFTItemSet create
        #   2.2.1 df_MFT_FrozenCapa, df_in_BOMMaster, df_in_ItemSiteAsn, df_in_TactTime join
        df_buf_MFTItemSet_1 = pd.merge(df_MFT_FrozenCapa, df_in_BOMMaster, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, FROM_SITE_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN, LOCATION_COLUMN])
        print_df(df_buf_MFTItemSet_1, 'STEP3 by 2.2.1 ____ df_buf_MFTItemSet_1 .... create')
    
        df_buf_MFTItemSet_2 = pd.merge(df_buf_MFTItemSet_1, df_in_ItemSiteAsn, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, FROM_SITE_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        df_buf_MFTItemSet_2.rename(columns={LOCATION_X_COLUMN: LOCATION_COLUMN}, inplace=True)
        df_buf_MFTItemSet_2 = df_buf_MFTItemSet_2.drop(labels=[LOCATION_Y_COLUMN], axis=1)
        print_df(df_buf_MFTItemSet_2, 'STEP3 by 2.2.1 ____ df_buf_MFTItemSet_2 .... create')
    
        df_buf_MFTItemSet_3 = pd.merge(df_buf_MFTItemSet_2, df_in_TactTime, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, FROM_SITE_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        df_buf_MFTItemSet_3.rename(columns={LOCATION_X_COLUMN: LOCATION_COLUMN}, inplace=True)
        df_buf_MFTItemSet_3 = df_buf_MFTItemSet_3.drop(labels=[LOCATION_Y_COLUMN], axis=1)
        print_df(df_buf_MFTItemSet_3, 'STEP3 by 2.2.1 ____ df_buf_MFTItemSet_3 .... create')
    
        #   2.2.2 df_MFTItemSet create
        df_MFTItemSet = rename_and_delete_df(df_buf_MFTItemSet_3)
        df_MFTItemSet[ACTIVITY2_COLUMN] = 'RT_' + df_MFTItemSet[BOM_ID_COLUMN] + '@' + df_MFTItemSet[LOCATION_COLUMN]
        df_MFTItemSet[RESOURCE_GROUP_COLUMN] = (
                'RT_' + df_MFTItemSet[BOM_ID_COLUMN] + '@' + df_MFTItemSet[LOCATION_COLUMN] + '_' + df_MFTItemSet[LINE_COLUMN]
        )
        df_MFTItemSet[W_SIMULTANEOUS_CCA_COLUMN] = '1'
        df_MFTItemSet.rename(columns={BOM_ID_COLUMN: ACTIVITY1_COLUMN, ITEM_COLUMN: ACTIVITY3_COLUMN}, inplace=True)
    
        #   2.2.3 필요컬럼발췌
        df_MFTItemSet = df_MFTItemSet[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]]
        print_df(df_MFTItemSet, 'STEP3 by 2.2.3 ____ df_MFTItemSet .... filter')
    
    
    
        # 2.3 df_MFTItemSet 을 Distinct하여 df_MFT_SOPFIXConsumeAsn 에 Insert
        #   2.3.1 df_buf_SOPFIXConsumeAsn create
        df_MFT_SOPFIXConsumeAsn = df_MFTItemSet.copy()

        #   2.3.2 df_buf_SOPFIXConsumeAsn distinct (필요컬럼만 발췌 후 중복제거)
        df_MFT_SOPFIXConsumeAsn = df_MFT_SOPFIXConsumeAsn[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN, RESOURCE_COLUMN
        ]].drop_duplicates()
    
        #   2.3.3 추가컬럼 설정
        df_MFT_SOPFIXConsumeAsn[W_RESOURCE_CATEGORY_COLUMN] = 'O'
        df_MFT_SOPFIXConsumeAsn[W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN] = '1'
        df_MFT_SOPFIXConsumeAsn[W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN] = '1'
        print_df(df_MFT_SOPFIXConsumeAsn, 'STEP3 by 2.3.3 ____ df_MFT_SOPFIXConsumeAsn .... filter')

        # ====================> STEP3 by 2 (End)
    
    
    
    
    
    
        # ====================> STEP3 by 3 (Start)

        # 3.1 df_SRT_FrozenCapa create
        #   3.1.1 df_buf_SRT_CapaWeek create
        df_buf_SRT_CapaWeek = pd.merge(df_in_CapaWeek, df_in_CapaItemSiteMap, how='inner',on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN])
        print_df(df_buf_SRT_CapaWeek, 'STEP3 by 3.1.1 ____ df_buf_SRT_CapaWeek .... merge[df_in_CapaWeek, df_in_CapaItemSiteMap]')
    
        #   3.1.2 컬럼설정 및 변경
        df_buf_SRT_CapaWeek[FROM_WEEK_COLUMN] = df_buf_SRT_CapaWeek[TIME_WEEK_COLUMN]
        df_buf_SRT_CapaWeek[TO_WEEK_COLUMN] = df_buf_SRT_CapaWeek[TIME_WEEK_COLUMN]
        df_buf_SRT_CapaWeek[FROM_SITE_COLUMN] = df_buf_SRT_CapaWeek[LOCATION_COLUMN]
        df_buf_SRT_CapaWeek[RANK_COLUMN] = df_buf_SRT_CapaWeek.groupby([FROM_SITE_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TRNAS_MODE_COLUMN]).ngroup() + 1
        df_buf_SRT_CapaWeek.rename(columns={CAPA_WEEK_QTY_COLUMN: QTY_COLUMN}, inplace=True)
        print_df(df_buf_SRT_CapaWeek, 'STEP3 by 3.1.2 ____ df_buf_SRT_CapaWeek .... columns modify')
    
        #   3.1.3 필요컬럼 발췌
        df_buf_SRT_CapaWeek = df_buf_SRT_CapaWeek[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, ITEM_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, FROM_SITE_COLUMN,
            QTY_COLUMN, RANK_COLUMN, SUB_LOCATION_COLUMN, TRNAS_MODE_COLUMN
        ]]
        print_df(df_buf_SRT_CapaWeek, 'STEP3 by 3.1.3 ____ df_buf_SRT_CapaWeek .... filter')
    
        #   3.1.4 df_buf_SRT_CapaPeriod create
        df_buf_SRT_CapaPeriod = pd.merge(df_in_CapaPeriod, df_in_CapaItemSiteMap, how='inner', on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN])
        print_df(df_buf_SRT_CapaPeriod, 'STEP3 by 3.1.4 ____ df_buf_SRT_CapaPeriod .... merge[df_in_CapaPeriod, df_in_CapaItemSiteMap]')
    
        #   3.1.5 컬럼설정 및 변경
        df_buf_SRT_CapaPeriod[FROM_WEEK_COLUMN] = df_buf_SRT_CapaPeriod[TIME_WEEK_COLUMN]
        df_buf_SRT_CapaPeriod[TO_WEEK_COLUMN] = df_buf_SRT_CapaPeriod[TO_TIME_WEEK_COLUMN]
        df_buf_SRT_CapaPeriod[FROM_SITE_COLUMN] = df_buf_SRT_CapaPeriod[LOCATION_COLUMN]
        df_buf_SRT_CapaPeriod[RANK_COLUMN] = df_buf_SRT_CapaPeriod.groupby([FROM_SITE_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TRNAS_MODE_COLUMN]).ngroup() + 1
        df_buf_SRT_CapaPeriod.rename(columns={CAPA_PERIOD_QTY_COLUMN: QTY_COLUMN}, inplace=True)
    
        #   3.1.6 필요컬럼 발췌
        df_buf_SRT_CapaPeriod = df_buf_SRT_CapaPeriod[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, ITEM_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, FROM_SITE_COLUMN,
             QTY_COLUMN, RANK_COLUMN, SUB_LOCATION_COLUMN, TRNAS_MODE_COLUMN
        ]]
        print_df(df_buf_SRT_CapaPeriod, 'STEP3 by 3.1.6 ____ df_buf_SRT_CapaPeriod .... filter')
    
        #   3.1.7 df_SRT_FrozenCapa create
        df_SRT_FrozenCapa = pd.concat([df_buf_SRT_CapaWeek, df_buf_SRT_CapaPeriod]).drop_duplicates()
    
        #   3.1.8 Resource make
        df_SRT_FrozenCapa[RANK_COLUMN] = df_SRT_FrozenCapa[RANK_COLUMN].astype(str)
        df_SRT_FrozenCapa[RESOURCE_COLUMN] = 'SRT_' + df_SRT_FrozenCapa[RANK_COLUMN]
    
        #   3.1.9 필요컬럼 발췌
        df_SRT_FrozenCapa = df_SRT_FrozenCapa[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, FROM_SITE_COLUMN, ITEM_COLUMN,
            RESOURCE_COLUMN, QTY_COLUMN, SUB_LOCATION_COLUMN, TRNAS_MODE_COLUMN
        ]]
        print_df(df_SRT_FrozenCapa, 'STEP3 by 3.1.9 ____ df_SRT_FrozenCapa .... filter')
    
    
    
        # 3.2 SRT Capacity 입력 > df_SRT_SOPFIXCapacity create
        #   3.2.1 수량 설정
        df_SRT_SOPFIXCapacity = df_SRT_FrozenCapa.copy()
        df_SRT_SOPFIXCapacity[W_RESOURCE_BASE_CAPACITY_COLUMN] = None
        df_SRT_SOPFIXCapacity[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = None
        df_SRT_SOPFIXCapacity[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = None
    
        #   3.2.2 조건에 따라 값 할당
        conditions = [
            (df_SRT_SOPFIXCapacity[FROM_WEEK_COLUMN] == mp_plan_start_week),
            (df_SRT_SOPFIXCapacity[FROM_WEEK_COLUMN] > mp_plan_start_week),
            (df_SRT_SOPFIXCapacity[TO_WEEK_COLUMN] < mp_plan_end_week)
        ]
    
        choices_max_qty = [df_SRT_SOPFIXCapacity[QTY_COLUMN], 10000000, 10000000]
        choices_min_qty = [df_SRT_SOPFIXCapacity[QTY_COLUMN], 10000000, 10000000]
        choices_base_capacity = [df_SRT_SOPFIXCapacity[QTY_COLUMN], 0, 0]
    
        df_SRT_SOPFIXCapacity[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = np.select(conditions, choices_max_qty, default=None)
        df_SRT_SOPFIXCapacity[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = np.select(conditions, choices_min_qty, default=None)
        df_SRT_SOPFIXCapacity[W_RESOURCE_BASE_CAPACITY_COLUMN] = np.select(conditions, choices_base_capacity, default=None)
    
        #   3.2.3 필요컬럼 발췌
        df_SRT_SOPFIXCapacity = df_SRT_SOPFIXCapacity[[
            VERSION_NAME_COLUMN, RESOURCE_COLUMN, FROM_SITE_COLUMN, FROM_WEEK_COLUMN, TO_WEEK_COLUMN, QTY_COLUMN,
            W_COARSER_MAXIMUM_U_QUANTITY_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN, W_RESOURCE_BASE_CAPACITY_COLUMN
        ]]
        print_df(df_SRT_SOPFIXCapacity, 'STEP3 by 3.2.3 ____ df_SRT_SOPFIXCapacity .... filter')
    
    
    
        # 3.3 df_buf_SRTItemSet create
        #   3.2.4 df_buf_SRTItemSet create
        #       3.2.4.1 df_SRT_FrozenCapa, df_in_BODItem, df_in_ItemSiteAsn, df_in_TactTime join
        df_buf_SRTItemSet = pd.merge(df_SRT_FrozenCapa, df_in_BODItem, how='inner',
                                     left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, FROM_SITE_COLUMN, SUB_LOCATION_COLUMN, TRNAS_MODE_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRNAS_MODE_COLUMN])
        print_df(df_buf_SRTItemSet, 'STEP3 by 3.2.4.1 ____ df_buf_SRTItemSet .... merge[df_SRT_SOPFIXCapacity, df_in_BODItem]')
    
        #       3.2.4.2 df_ItemSiteAsnLocation[Location, Sub Location] 이 df_SCTItemSetPrev[Location] 에 속한것 copy
        df_buf_SRTItemSetLocation = (
            df_buf_SRTItemSet[
                df_buf_SRTItemSet[LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN]) |
                df_buf_SRTItemSet[SUB_LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN])
            ].copy()
        )
        print_df(df_buf_SRTItemSetLocation, 'STEP3 by 3.2.4.2 ____ df_buf_SRTItemSetLocation .... filter')
    
        #       3.2.4.3 df_ItemSiteAsnItem[Item] 이 df_buf_SRTItemSetLocation[Item] 에 속한것 copy
        df_buf_SRTItemSetLocationItem = df_buf_SRTItemSetLocation[df_buf_SRTItemSetLocation[ITEM_COLUMN].isin(df_ItemSiteAsnItem[ITEM_COLUMN])].copy()
        print_df(df_buf_SRTItemSetLocationItem, 'STEP3 by 3.2.4.3 ____ df_buf_SRTItemSetLocationItem .... filter')
    
        #   3.2.5 df_SRTItemSet create
        df_SRTItemSet = df_buf_SRTItemSetLocationItem.copy()
        df_SRTItemSet[ACTIVITY1_COLUMN] = (df_SRTItemSet[LOCATION_COLUMN] + '_' + df_SRTItemSet[SUB_LOCATION_COLUMN] + '_' + df_SRTItemSet[TRNAS_MODE_COLUMN])
        df_SRTItemSet[RESOURCE_GROUP_COLUMN] = (
                df_SRTItemSet[LOCATION_COLUMN] + '_' + df_SRTItemSet[SUB_LOCATION_COLUMN] + '_' + df_SRTItemSet[TRNAS_MODE_COLUMN] + '_' + df_SRTItemSet[ITEM_COLUMN]
        )
        df_SRTItemSet[W_SIMULTANEOUS_CCA_COLUMN] = '1'
        df_SRTItemSet.rename(columns={TRNAS_MODE_COLUMN: ACTIVITY2_COLUMN, ITEM_COLUMN: ACTIVITY3_COLUMN}, inplace=True)
        print_df(df_SRTItemSet, 'STEP3 by 3.2.5 ____ df_SRTItemSet .... filter')
    
        #   3.2.6 필요컬럼발췌
        df_SRTItemSet = df_SRTItemSet[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]]
        print_df(df_SRTItemSet, 'STEP3 by 3.2.6 ____ df_SRTItemSet .... filter')
    
    
    
        # 3.3 df_SRTItemSet 를 Distinct하여 df_SRT_SOPFIXConsumeAsn 에 Insert
        #   3.3.1 df_buf_SRT_SOPFIXConsumeAsn create
        df_SRT_SOPFIXConsumeAsn = df_MFTItemSet.copy()
    
        #   3.3.2 df_buf_SOPFIXConsumeAsn distinct (필요컬럼만 발췌 후 중복제거)
        df_SRT_SOPFIXConsumeAsn = df_SRT_SOPFIXConsumeAsn[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN,
            RESOURCE_COLUMN
        ]].drop_duplicates()
    
        #   3.3.3 추가컬럼 설정
        df_SRT_SOPFIXConsumeAsn[W_RESOURCE_CATEGORY_COLUMN] = 'O'
        df_SRT_SOPFIXConsumeAsn[W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN] = '1'
        df_SRT_SOPFIXConsumeAsn[W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN] = '1'
        print_df(df_SRT_SOPFIXConsumeAsn, 'STEP3 by 3.3.2 ____ df_SRT_SOPFIXConsumeAsn .... filter')

        # ====================> STEP3 by 3 (End)
    
        step('=====> STEP3 End')
        
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        # CTNCapacity concat
        df_out_SOPFIXCapacity = pd.concat([df_MFT_SOPFIXCapacity, df_SRT_SOPFIXCapacity])
    
        # CTNSimultaneous concat
        df_out_SOPFIXSimultaneous = pd.concat([df_MFTItemSet, df_SRTItemSet])
    
        # CTNConsumeAsn concat
        df_out_SOPFIXConsumeAsn = pd.concat([df_MFT_SOPFIXConsumeAsn, df_SRT_SOPFIXConsumeAsn])
    
        # 버전 처리
        df_out_SOPFIXCapacity[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPFIXSimultaneous[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPFIXConsumeAsn[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_SOPFIXCapacity, 'output table create .... df_out_SOPFIXCapacity', True)
        print_df(df_out_SOPFIXSimultaneous, 'output table create .... df_out_SOPFIXSimultaneous', True)
        print_df(df_out_SOPFIXConsumeAsn, 'output table create .... df_out_SOPFIXConsumeAsn', True)
    
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPFIXCapacity = pd.DataFrame(columns=df_SOPFIXCapacity_columns)
        df_out_SOPFIXSimultaneous = pd.DataFrame(columns=df_SOPFIXSimultaneous_columns)
        df_out_SOPFIXConsumeAsn = pd.DataFrame(columns=df_SOPFIXConsumeAsn_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SOPFIXCapacity = pd.DataFrame(columns=df_SOPFIXCapacity_columns)
        df_out_SOPFIXSimultaneous = pd.DataFrame(columns=df_SOPFIXSimultaneous_columns)
        df_out_SOPFIXConsumeAsn = pd.DataFrame(columns=df_SOPFIXConsumeAsn_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
