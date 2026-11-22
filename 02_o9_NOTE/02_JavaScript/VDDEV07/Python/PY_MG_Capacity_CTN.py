"""
* 프로그램명
    - PY_MG_Capacity_CTN

* 내용
    - MP Engine 수행을 위한 CTN Capacity Input
    - MP Plan Batch Procedure에서 Call 하는 Program

* 변경이력
    - 2024.08.22 / 권태우 / Create
    - 2024.09.02 / 권태우 / Output Table 내용 변경

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CTNGrpConst   : Select (Version.[Version Name] * [Sequence].[Sequence] * [Group].[Group ID] ) on row, ({Measure.[CTN Grp Const_GC], Measure.[CTN Grp Const_AP2], Measure.[CTN Grp Const_Apply Flag], Measure.[CTN Grp Const_Start Week], Measure.[CTN Grp Const_End Week], Measure.[CTN Grp Const_From Site],  Measure.[CTN Grp Const_Frozen SOP Override Qty] })  on column.filter(Measure.[CTN Grp Const_Apply Flag] == "Y");
    - df_in_GrpConstEcp   : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] * [Sequence].[Sequence] * [Group].[Group ID] ) on row, ({Measure.[CTN Grp Const Ecp_Ecp Flag] }) on column.filter(Measure.[CTN Grp Const Ecp_Ecp Flag] == true);
    - df_in_CTNItemConst  : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Apply Flag], Measure.[CTN Item Const_DP Qty from W0], Measure.[CTN Item Const_EOH at PSI], Measure.[CTN Item Const_End Week], Measure.[CTN Item Const_Frozen SOP DP Diff Qty], Measure.[CTN Item Const_Frozen SOP Diff Qty], Measure.[CTN Item Const_Frozen SOP Override Qty], Measure.[CTN Item Const_Frozen SOP Override Reason], Measure.[CTN Item Const_Frozen SOP Override Remain Qty], Measure.[CTN Item Const_Frozen SOP Qty], Measure.[CTN Item Const_Frozen Week], Measure.[CTN Item Const_Prod Result Qty before W0], Measure.[CTN Item Const_Start Week]}) on column;
    - df_in_ItemSiteAsn   : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Flag], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag] == true);
    - df_in_BOMMaster     : Select (Version.[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column;
    - df_in_TactTime      : Select (Version.[Version Name]  * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  where {  Measure.[Tact Time_Valid Asn] == true};
    - df_in_BODItem       : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT]}) on column;
    - df_in_SiteAP2Map    : Select (Version.[Version Name] * [Location].[Location] ) on row, ({Measure.[Site AP2 Map_GC], Measure.[Site AP2 Map_Ship To], Measure.[Site AP2 Map_Status], Measure.[Site AP2 Map_Valid Flag]}) on column;
    - df_PlanStartEndWeek : Select (Version.[Version Name]) on row, ({Measure.[MP Plan End Week], Measure.[MP Plan Start Week]}) on column;
    - df_in_PlanningWeek  : Select ( &PlanningHorizon ) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};

* Flow Summary
    - STEP1. BOD List 발췌 기준으로 Item Site Asn 조합하여  BOD Item 을 구성한다.
    - STEP2. BOD Prod Set 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_CTNCapacity
    - df_out_CTNConsumeAsn
    - df_out_CTNSimultaneous

* 데이타 초기화
    - DELETE DATA FOR MODEL [001.022W Solver Inputs Capacity] WHERE {[Version].[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [001.004W Solver Inputs Capacity Consumption Association] WHERE {[Version].[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [001.005W Solver Inputs Resource Group Consumption Association] WHERE {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_Capacity_CTN] for measures {[W Resource Base Capacity]} using scope (&MPV, &PlanningHorizon)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_CTNCapacity / MG:  001.022W Solver Inputs Capacity
        Select ([Version].[Version Name].[CWV_MP] * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row,
            ({Measure.[W Resource Base Capacity], Measure.[W Coarser Maximum Utilization Quantity], Measure.[W Coarser Minimum Utilization Quantity]}) on column;

    - df_out_CTNConsumeAsn / MG: 001.004W Solver Inputs Capacity Consumption Association
        Select ([Version].[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row,
            ({Measure.[W Input Resource Priority], Measure.[W Resource Category], Measure.[W Resource Consumed Quantity Per], Measure.[W Resource Consumption Association]}) on column;

    - df_out_CTNSimultaneous / MG: 001.005W Solver Inputs Resource Group Consumption Association
        Select ([Version].[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] * [Resource Group].[Resource Group] ) on row,
            ({Measure.[W Simultaneous Capacity Consumption Association]}) on column;


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
str_instance = 'PY_MG_Capacity_CTN'
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




def run_time_minutes(start_time):
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"


def is_null_or_all(series):
    return series.isnull() | (series.str.upper() == 'ALL')


def is_all(series):
    return series.isnull() | (series.str.upper() == 'ALL')


def is_not_all(series):
    filled_series = series.fillna('ALL').str.upper()
    return filled_series != 'ALL'



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
            df_in_CTNGrpConst = read_csv_file("df_in_CTNGrpConst")
            df_in_GrpConstEcp = read_csv_file("df_in_GrpConstEcp")
            df_in_CTNItemConst = read_csv_file("df_in_CTNItemConst")
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_TactTime = read_csv_file("df_in_TactTime")
            df_in_BODItem = read_csv_file("df_in_BODItem")
            df_in_SiteAP2Map = read_csv_file("df_in_SiteAP2Map")
            df_PlanStartEndWeek = read_csv_file("df_PlanStartEndWeek")
            df_in_PlanningWeek = read_csv_file("df_in_PlanningWeek")
    
    
        print_df(df_in_CTNGrpConst, 'STEP 1 - Input table load .... df_in_CTNGrpConst')
        print_df(df_in_GrpConstEcp, 'STEP 1 - Input table load .... df_in_GrpConstEcp')
        print_df(df_in_CTNItemConst, 'STEP 1 - Input table load .... df_in_CTNItemConst')
        print_df(df_in_BOMMaster, 'STEP 1 - Input table load .... df_in_BOMMaster')
        print_df(df_in_ItemSiteAsn, 'STEP 1 - Input table load .... df_in_ItemSiteAsn')
        print_df(df_in_TactTime, 'STEP 1 - Input table load .... df_in_TactTime')
        print_df(df_in_BODItem, 'STEP 1 - Input table load .... df_in_BODItem')
        print_df(df_in_SiteAP2Map, 'STEP 1 - Input table load .... df_in_SiteAP2Map')
        print_df(df_PlanStartEndWeek, 'STEP 1 - Input table load .... df_PlanStartEndWeek')
        print_df(df_in_PlanningWeek, 'STEP 1 - Input table load .... df_in_PlanningWeek')

        step('=====> STEP1 End')


    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
    
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    
        RESOURCE_COLUMN = 'Resource.[Resource]'
        RESOURCE_GROUP_COLUMN = '[Resource Group].[Resource Group]'
    
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
    
        ITEM_COLUMN = 'Item.[Item]'
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
        # CTN_ITEM_CONST_AP2_COLUMN = 'CTN Item Const_AP2'
        CTN_ITEM_CONST_APPLY_FLAG_COLUMN = 'CTN Item Const_Apply Flag'
        CTN_ITEM_CONST_START_WEEK_COLUMN = 'CTN Item Const_Start Week'
        CTN_ITEM_CONST_END_WEEK_COLUMN = 'CTN Item Const_End Week'
        CTN_ITEM_CONST_FROZEN_WEEK_COLUMN = 'CTN Item Const_Frozen Week'
        CTN_ITEM_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN = 'CTN Item Const_Frozen SOP Override Qty'
    
        TIME_WEEK_COLUMN = 'Time.[Week]'
    
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
    
        ALL_VALUE = 'ALL'

        df_CTNCapacity_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN, W_RESOURCE_BASE_CAPACITY_COLUMN, W_COARSER_MAXIMUM_U_QUANTITY_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN,
        ]

        df_CTNConsumeAsn_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN, RESOURCE_COLUMN, W_INPUT_RESOURCE_PRIORITY_COLUMN, W_RESOURCE_CATEGORY_COLUMN, W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN, W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN,
        ]

        df_CTNSimultaneous_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN, RESOURCE_COLUMN, W_SIMULTANEOUS_CCA_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN
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
    
        drop_column = [col for col in list(df_ItemSiteAsnTemp2.columns) if col not in [ITEM_COLUMN]]
        df_ItemSiteAsnItem = df_ItemSiteAsnTemp2.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[ITEM_COLUMN], keep='first')

        # MP Plan Week 가져오기
        mp_plan_start_week = get_first_value(df_PlanStartEndWeek, MP_PLAN_START_WEEK_COLUMN)
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')

        mp_plan_end_week = get_first_value(df_PlanStartEndWeek, MP_PLAN_END_WEEK_COLUMN)
        step(f'=====> mp_plan_end_week : {mp_plan_end_week}')

        # df_in_PlanningWeek 에서 Time.[Week] 만 발췌
        df_PlanningWeek = df_in_PlanningWeek[[TIME_WEEK_COLUMN]].copy()
        df_PlanningWeek['key'] = 1
    

    
        # ====================> STEP3 by 1 (Start) -> create df_CTNGroupSet

        # 1.1 CTN_ITEM_CONST_GC_COLUMN 와 CTN_ITEM_CONST_AP2_COLUMN 컬럼의 널값을 ALL 로 치환
        df_in_CTNGrpConst[[CTN_GRP_CONST_GC_COLUMN, CTN_GRP_CONST_AP2_COLUMN]] = (
            df_in_CTNGrpConst[[CTN_GRP_CONST_GC_COLUMN, CTN_GRP_CONST_AP2_COLUMN]].fillna(ALL_VALUE)
        )

        df_CTNGroupSet = rename_and_delete_df(df_in_CTNGrpConst)

        # 1.3 컬럼타입 재정의
        df_CTNGroupSet[SEQUENCE_COLUMN] = df_CTNGroupSet[SEQUENCE_COLUMN].astype(str)
    
        #   1.4 Resource 컬럼 create
        df_CTNGroupSet[RESOURCE_COLUMN] = np.where(
            (df_CTNGroupSet[CTN_GRP_CONST_GC_COLUMN].str.upper() == ALL_VALUE) &
            (df_CTNGroupSet[CTN_GRP_CONST_AP2_COLUMN].str.upper() == ALL_VALUE),
            'MCT@' + df_CTNGroupSet[GROUP_ID_COLUMN] + '_' + df_CTNGroupSet[SEQUENCE_COLUMN],
            'SCT@' + df_CTNGroupSet[GROUP_ID_COLUMN] + '_' + df_CTNGroupSet[SEQUENCE_COLUMN]
        )
    
        df_CTNGroupSetCopy = df_CTNGroupSet.copy()
    
        print_df(df_CTNGroupSet, 'STEP3 by 1 ____ df_CTNGroupSet .... final')

        # ====================> STEP3 by 1 (End)
    
    
    
    
    
    
        # ====================> STEP3 by 2 (Start) -> CTN Capacity(df_CTNGroupCapacity) create (df_CTNGroupSet 기준)

        # 2.1 df_CTNGroupSet, df_in_PlanningWeek join (카테시안곱 처리)
        df_CTNGroupSet['key'] = 1
        df_CTNGroupSetWeek = pd.merge(df_CTNGroupSet, df_PlanningWeek, how='outer', on='key')
        df_CTNGroupSetWeek.drop(columns=['key'], inplace=True)
    
        df_CTNGroupSetWeek[W_RESOURCE_BASE_CAPACITY_COLUMN] = 0
        df_CTNGroupSetWeek[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = 0
        df_CTNGroupSetWeek[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = 0


        # 2.2 CTN Grp Const_Start Week 기준으로 Capacity 입력
        #   2.2.1 Define the conditions
        conditions = [
            # WEEK 가 START DATE 보다 작으면 수량에 max_quantity
            df_CTNGroupSetWeek[TIME_WEEK_COLUMN] < df_CTNGroupSetWeek[CTN_GRP_CONST_START_WEEK_COLUMN],
    
            # WEEK 가 END DATE 보다 크면 수량에 min_quantity
            df_CTNGroupSetWeek[TIME_WEEK_COLUMN] > df_CTNGroupSetWeek[CTN_GRP_CONST_END_WEEK_COLUMN],
    
            # WEEk 와 START DATE 가 같으면 수량변경 없음
            df_CTNGroupSetWeek[TIME_WEEK_COLUMN] == df_CTNGroupSetWeek[CTN_GRP_CONST_START_WEEK_COLUMN],
    
            # WEEK 가 START DATE 보다 크고 END DATE 보다 작거나 같으면 수량 null 처리
            (df_CTNGroupSetWeek[TIME_WEEK_COLUMN] > df_CTNGroupSetWeek[CTN_GRP_CONST_START_WEEK_COLUMN]) &
            (df_CTNGroupSetWeek[TIME_WEEK_COLUMN] <= df_CTNGroupSetWeek[CTN_GRP_CONST_END_WEEK_COLUMN])
        ]
    
        #   2.2.2 Define the corresponding values for each condition
        values_for_col1 = [
            1000000,
            0,
            df_CTNGroupSetWeek[CTN_GRP_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN],  # No change
            np.nan  # Null value
        ]
    
        values_for_col2 = [
            0,
            0,
            df_CTNGroupSetWeek[CTN_GRP_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN],  # No change
            np.nan  # Null value
        ]
    
        #   2.2.3 Apply the conditions and assign the values
        df_CTNGroupSetWeek[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = np.select(conditions, values_for_col1, default=0)
        df_CTNGroupSetWeek[W_RESOURCE_BASE_CAPACITY_COLUMN] = np.select(conditions, values_for_col1, default=0)
        df_CTNGroupSetWeek[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = np.select(conditions, values_for_col2, default=0)
    
        #   2.2.4 컬럼타입 재정의
        columns_to_transform = [
            CTN_GRP_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN, W_RESOURCE_BASE_CAPACITY_COLUMN, W_COARSER_MAXIMUM_U_QUANTITY_COLUMN,
            W_COARSER_MINIMUM_U_QUANTITY_COLUMN
        ]
        for column in columns_to_transform:
            df_CTNGroupSetWeek[column] = df_CTNGroupSetWeek[column].astype('Int64')
    
        print_df(df_CTNGroupSetWeek, 'STEP3 by 2.2.4 ____ df_CTNGroupSetWeek .... final')
    
        #   2.2.5 df_CTNCapacity create
        df_CTNGroupCapacity = df_CTNGroupSetWeek.copy()
    
        #   2.2.6. 컬럼명 변경
        df_CTNGroupCapacity.rename(columns={CTN_GRP_CONST_FROM_SITE_COLUMN: LOCATION_COLUMN}, inplace=True)
    
        #   2.2.7 필요컬럼 발췌
        df_CTNGroupCapacity = df_CTNGroupCapacity[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN,
            W_RESOURCE_BASE_CAPACITY_COLUMN, W_COARSER_MAXIMUM_U_QUANTITY_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN
        ]]
        print_df(df_CTNGroupCapacity, 'STEP3 by 2.2.7 ____ df_CTNGroupCapacity .... final')

        # ====================> STEP3 by 2 (End)
    
    
    
    
    
    
        # ====================> STEP3 by 3 (Start)

        # 3.1 df_MCTSetEcpItemAsn create
        #   3.1.1 df_in_GrpConstEcp, df_CTNGroupSetWeek join
        df_in_GrpConstEcp[SEQUENCE_COLUMN] = df_in_GrpConstEcp[SEQUENCE_COLUMN].astype(str)
        df_MCTSetEcp = pd.merge(df_in_GrpConstEcp, df_CTNGroupSetWeek, how='inner',
                                left_on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, SEQUENCE_COLUMN],
                                right_on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, SEQUENCE_COLUMN])
        print_df(df_MCTSetEcp, 'STEP3 by 3.1.1 ____ df_MCTSetEcp .... merge[df_in_GrpConstEcp, df_CTNGroupSetWeek]')
    
        #       3.1.1.1 조건식에 맞는 데이터 copy
        condition_gc_null_or_all = is_null_or_all(df_MCTSetEcp[CTN_GRP_CONST_GC_COLUMN])
        condition_ap2_null_or_all = is_null_or_all(df_MCTSetEcp[CTN_GRP_CONST_AP2_COLUMN])
        conditions_set = condition_gc_null_or_all & condition_ap2_null_or_all
        df_MCTSetEcp = df_MCTSetEcp[conditions_set].copy()
        print_df(df_MCTSetEcp, 'STEP3 by 3.1.1.1 _____ df_MCTSetEcp .... filter')
    
        #   3.1.2 df_MCTSetEcpItem create
        df_MCTSetEcpItem = pd.merge(df_MCTSetEcp, df_in_BOMMaster, how='inner',
                                    left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN],
                                    right_on=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN, LOCATION_COLUMN])
        print_df(df_MCTSetEcpItem, 'STEP3 by 3.1.2 _____ df_MCTSetEcpItem .... merge[df_MCTSetEcp, df_in_BOMMaster]')
    
        #   3.1.3 df_MCTSetEcpItemAsn create
        df_MCTSetEcpItemAsn = pd.merge(df_MCTSetEcpItem, df_in_ItemSiteAsn, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        print_df(df_MCTSetEcpItemAsn, 'STEP3 by 3.1.3 _____ df_MCTSetEcpItemAsn .... merge[df_MCTSetEcpItem, df_in_ItemSiteAsn]')

    
    
        # 3.2 df_CTNSimultaneous1 create
        #   3.2.1
        df_CTNSimultaneous1 = pd.merge(df_MCTSetEcpItemAsn, df_in_TactTime, how='inner', 
                                       left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN], 
                                       right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        print_df(df_CTNSimultaneous1, 'STEP3 by 3.2.1 _____ df_CTNSimultaneous1 .... merge[df_MCTSetEcpItemAsn, df_in_TactTime]')

        df_CTNSimultaneous1[ACTIVITY2_COLUMN] = ('RT_' + df_CTNSimultaneous1[BOM_ID_COLUMN] + '@' + df_CTNSimultaneous1[LOCATION_COLUMN])
        df_CTNSimultaneous1[RESOURCE_GROUP_COLUMN] = ('RT_' + df_CTNSimultaneous1[BOM_ID_COLUMN] + '@' +
                                                      df_CTNSimultaneous1[LOCATION_COLUMN] + '_' +
                                                      df_CTNSimultaneous1[LINE_COLUMN])
        df_CTNSimultaneous1[W_SIMULTANEOUS_CCA_COLUMN] = 1
        df_CTNSimultaneous1.rename(columns={BOM_ID_COLUMN: ACTIVITY1_COLUMN, ITEM_COLUMN: ACTIVITY3_COLUMN}, inplace=True)
    
        #   3.2.2 필요컬럼 발췌
        df_CTNSimultaneous1 = df_CTNSimultaneous1[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]].drop_duplicates()
        print_df(df_CTNSimultaneous1, 'STEP3 by 3.2.2 _____ df_CTNSimultaneous1 .... final')



        # 3.3 df_CTNConsumeAsn1 create
        df_CTNConsumeAsn1 = df_CTNSimultaneous1.copy()
        df_CTNConsumeAsn1[W_INPUT_RESOURCE_PRIORITY_COLUMN] = 1
        df_CTNConsumeAsn1[W_RESOURCE_CATEGORY_COLUMN] = 'O'
        df_CTNConsumeAsn1[W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN] = 1
        df_CTNConsumeAsn1[W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN] = 1
    
        #   3.3.1 필요컬럼 발췌
        df_CTNConsumeAsn1 = df_CTNConsumeAsn1[df_CTNConsumeAsn_columns].drop_duplicates()
        print_df(df_CTNConsumeAsn1, 'STEP3 by 3.3.1 _____ df_CTNConsumeAsn1 .... final')

        # ====================> STEP3 by 3 (End)
    
    
    
    
    
        # ====================> STEP3 by 4 (Start)

        # 4.1 df_SCTEcpSet create
        #   4.1.1 df_CTNGroupSet, df_in_GrpConstEcp join
        df_SCTEcpSet = pd.merge(df_in_GrpConstEcp, df_CTNGroupSetCopy, how='inner',
                                 left_on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, SEQUENCE_COLUMN],
                                 right_on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, SEQUENCE_COLUMN])
        print_df(df_SCTEcpSet, 'STEP3 by 4.1.1 _____ df_SCTEcpSet .... merge[df_in_GrpConstEcp, df_CTNGroupSetCopy]')
    
        #       4.1.1.1 조건식에 맞는 데이터 copy
        condition_gc_not_all = is_not_all(df_SCTEcpSet[CTN_GRP_CONST_GC_COLUMN])
        condition_ap2_not_all = is_not_all(df_SCTEcpSet[CTN_GRP_CONST_AP2_COLUMN])
        conditions_set = condition_gc_not_all | condition_ap2_not_all
        df_SCTEcpSet = df_SCTEcpSet[conditions_set].copy()
        print_df(df_SCTEcpSet, 'STEP3 by 4.1.1.1 _____ df_SCTEcpSet .... filter')
    
        #   4.1.2 df_SCTEcpItemLocation create
        df_SCTEcpItemLocation = pd.merge(df_SCTEcpSet, df_in_BODItem, how='inner', on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        print_df(df_SCTEcpItemLocation, 'STEP3 by 4.1.2 _____ df_SCTEcpItemLocation .... merge[df_SCTEcpSet, df_in_BODItem]')
    
        #   4.1.3 df_ItemSiteAsnLocation[Location, Sub Location] 이 df_SCTEcpItemLocation[Location] 에 속한것 copy
        df_SCTEcpItemLocation = (
            df_SCTEcpItemLocation[
                df_SCTEcpItemLocation[LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN]) |
                df_SCTEcpItemLocation[SUB_LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN])
            ].copy()
        )
        print_df(df_SCTEcpItemLocation, 'STEP3 by 4.1.3 _____ df_SCTEcpItemLocation .... filter')
    
        #   4.1.4 df_ItemSiteAsnItem[Item] 이 df_SCTEcpItemLocation[Item] 에 속한것 copy
        df_SCTEcpItemLocation = df_SCTEcpItemLocation[df_SCTEcpItemLocation[ITEM_COLUMN].isin(df_ItemSiteAsnItem[ITEM_COLUMN])].copy()
        print_df(df_SCTEcpItemLocation, 'STEP3 by 4.1.4 _____ df_SCTEcpItemLocation .... filter')


        # 4.2 df_CTNSimultaneous2 create
        #   4.2.1
        df_CTNSimultaneous2 = pd.merge(df_SCTEcpItemLocation, df_in_SiteAP2Map, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN])
        print_df(df_CTNSimultaneous2, 'STEP3 by 4.2.1 _____ df_CTNSimultaneous2 .... create')

        #   4.2.2 CTN Grp Const 와 Site AP2 Map 조건 맞는것 copy
        df_CTNSimultaneous2 = df_CTNSimultaneous2[
            (df_CTNSimultaneous2[CTN_GRP_CONST_AP2_COLUMN] == df_CTNSimultaneous2[SITE_AP2_MAP_SHIP_TO_COLUMN]) |
            (df_CTNSimultaneous2[CTN_GRP_CONST_GC_COLUMN] == df_CTNSimultaneous2[SITE_AP2_MAP_GC_COLUMN])
        ].copy()
        print_df(df_CTNSimultaneous2, 'STEP3 by 4.2.2 _____ df_CTNSimultaneous2 .... filter')

        #   4.2.3 컬럼편집
        df_CTNSimultaneous2.rename(columns={'Location.[Location]_x': LOCATION_COLUMN}, inplace=True)
        df_CTNSimultaneous2 = df_CTNSimultaneous2.drop(labels=['Location.[Location]_y'], axis=1)
        df_CTNSimultaneous2[ACTIVITY1_COLUMN] = (
                df_CTNSimultaneous2[LOCATION_COLUMN] + '_' + df_CTNSimultaneous2[SUB_LOCATION_COLUMN] + '_' + df_CTNSimultaneous2[TRNAS_MODE_COLUMN]
        )
        df_CTNSimultaneous2[RESOURCE_GROUP_COLUMN] = (
                df_CTNSimultaneous2[LOCATION_COLUMN] + '_' + df_CTNSimultaneous2[SUB_LOCATION_COLUMN] + '_' + df_CTNSimultaneous2[TRNAS_MODE_COLUMN] + '_' + df_CTNSimultaneous2[ITEM_COLUMN]
        )
        df_CTNSimultaneous2[W_SIMULTANEOUS_CCA_COLUMN] = 1
        df_CTNSimultaneous2.rename(columns={TRNAS_MODE_COLUMN: ACTIVITY2_COLUMN, ITEM_COLUMN: ACTIVITY3_COLUMN}, inplace=True)
        print_df(df_CTNSimultaneous2, 'STEP3 by 4.2.3 _____ df_CTNSimultaneous2 .... columns modify')

        #   4.2.4 필요컬럼 발췌
        df_CTNSimultaneous2 = df_CTNSimultaneous2[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]].drop_duplicates()
        print_df(df_CTNSimultaneous2, 'STEP3 by 4.2.4 _____ df_CTNSimultaneous2 .... final')



        # 4.3 df_CTNConsumeAsn2 create
        df_CTNConsumeAsn2 = df_CTNSimultaneous2.copy()
        df_CTNConsumeAsn2[W_INPUT_RESOURCE_PRIORITY_COLUMN] = 1
        df_CTNConsumeAsn2[W_RESOURCE_CATEGORY_COLUMN] = 'O'
        df_CTNConsumeAsn2[W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN] = 1
        df_CTNConsumeAsn2[W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN] = 1
    
        #   4.3.1 필요컬럼 발췌
        df_CTNConsumeAsn2 = df_CTNConsumeAsn2[df_CTNConsumeAsn_columns].drop_duplicates()
        print_df(df_CTNConsumeAsn2, 'STEP3 by 4.3.1 _____ df_CTNConsumeAsn2 .... final')
        
        # ====================> STEP3 by 4 (End)
    
    
    
    
    
    
        # ====================> STEP3 by 5 (Start)

        # 5.1 df_CTNItemSet create
        #   5.1.1 mp_plan_start_week 과 mp_plan_end_week 에 맞는 데이터 copy
        df_CTNItemSet = df_in_CTNItemConst[
            (df_in_CTNItemConst[CTN_ITEM_CONST_START_WEEK_COLUMN] >= mp_plan_start_week) |
            (df_in_CTNItemConst[CTN_ITEM_CONST_END_WEEK_COLUMN] <= mp_plan_end_week)
        ].copy()
    
        #   5.1.2 CTN_GRP_CONST_GC_COLUMN 와 CTN_ITEM_CONST_AP2_COLUMN 컬럼의 널값을 ALL 로 치환
        df_CTNItemSet[SALES_DOMAIN_AP2_COLUMN] = df_CTNItemSet[SALES_DOMAIN_AP2_COLUMN].astype(str)
        df_CTNItemSet[[SALES_DOMAIN_AP2_COLUMN]] = df_CTNItemSet[[SALES_DOMAIN_AP2_COLUMN]].fillna(ALL_VALUE)
        print_df(df_CTNItemSet, 'STEP3 by 5.1.2 _____ df_CTNItemSet .... filter')
    
        #   5.1.3 Resource 컬럼 create
        df_CTNItemSet[RESOURCE_COLUMN] = np.where(
            df_CTNItemSet[SALES_DOMAIN_AP2_COLUMN].str.upper() == ALL_VALUE,
            'MCT@' + df_CTNItemSet[ITEM_COLUMN] + '_' + df_CTNItemSet[LOCATION_COLUMN],
            'SCT@' + df_CTNItemSet[ITEM_COLUMN] + '_' + df_CTNItemSet[SALES_DOMAIN_AP2_COLUMN]
        )
        print_df(df_CTNItemSet, 'STEP3 by 5.1.3 _____ df_CTNItemSet .... final')
    

        df_CTNItemSetCopy = df_CTNItemSet.copy()    # 5.4 에서 사용(미리 복제본 생성)
    
    
        # 5.2 CTN Capacity 에 입력 (df_CTNItemSet 기준)
        #   5.2.1 df_in_PlanningWeek 에서 Time.[Week] 만 발췌
        #          ==> Step 1 이전에 사전 작업 함.
    
        #   5.2.2 df_CTNItemSet 과 df_in_PlanningWeek join
        df_CTNItemSet['key'] = 1
        df_CTNItemSetWeek = pd.merge(df_CTNItemSet, df_PlanningWeek, how='outer', on='key')
        df_CTNItemSetWeek.drop(columns=['key'], inplace=True)
    
        df_CTNItemSetWeek[W_RESOURCE_BASE_CAPACITY_COLUMN] = 0
        df_CTNItemSetWeek[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = 0
        df_CTNItemSetWeek[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = 0
    
        #   5.2.3 CTN Grp Const_Start Week 기준으로 Capacity 입력
        #       5.2.3.1 Define the conditions
        conditions = [
            # WEEK 가 START DATE 보다 작으면 수량에 max_quantity
            df_CTNItemSetWeek[TIME_WEEK_COLUMN] < df_CTNItemSetWeek[CTN_ITEM_CONST_START_WEEK_COLUMN],
    
            # WEEK 가 END DATE 보다 크면 수량에 min_quantity
            df_CTNItemSetWeek[TIME_WEEK_COLUMN] > df_CTNItemSetWeek[CTN_ITEM_CONST_END_WEEK_COLUMN],
    
            # WEEk 와 START DATE 가 같으면 수량변경 없음
            df_CTNItemSetWeek[TIME_WEEK_COLUMN] == df_CTNItemSetWeek[CTN_ITEM_CONST_START_WEEK_COLUMN],
    
            # WEEK 가 START DATE 보다 크고 END DATE 보다 작거나 같으면 수량 null 처리
            (df_CTNItemSetWeek[TIME_WEEK_COLUMN] > df_CTNItemSetWeek[CTN_ITEM_CONST_START_WEEK_COLUMN]) &
            (df_CTNItemSetWeek[TIME_WEEK_COLUMN] <= df_CTNItemSetWeek[CTN_ITEM_CONST_END_WEEK_COLUMN])
        ]
    
        #       5.2.3.2 Define the corresponding values for each condition
        values_for_col1 = [
            1000000,
            0,
            df_CTNItemSetWeek[CTN_ITEM_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN],  # No change
            np.nan  # Null value
        ]
    
        values_for_col2 = [
            0,
            0,
            df_CTNItemSetWeek[CTN_ITEM_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN],  # No change
            np.nan  # Null value
        ]
    
        #       5.2.3.3 Apply the conditions and assign the values
        df_CTNItemSetWeek[W_COARSER_MAXIMUM_U_QUANTITY_COLUMN] = np.select(conditions, values_for_col1, default=0)
        df_CTNItemSetWeek[W_RESOURCE_BASE_CAPACITY_COLUMN] = np.select(conditions, values_for_col1, default=0)
        df_CTNItemSetWeek[W_COARSER_MINIMUM_U_QUANTITY_COLUMN] = np.select(conditions, values_for_col2, default=0)
    
        #   5.2.4 컬럼타입 재정의
        # 컬럼타입 재정의
        int_columns = [CTN_ITEM_CONST_FROZEN_SOP_OVERRIDE_QTY_COLUMN, W_RESOURCE_BASE_CAPACITY_COLUMN, W_COARSER_MAXIMUM_U_QUANTITY_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN]
        for column in int_columns:
            df_CTNItemSetWeek[column] = df_CTNItemSetWeek[column].astype('Int64')
    
        print_df(df_CTNItemSetWeek, 'STEP3 by 5.2.4 _____ df_CTNItemSetWeek .... final')



        # 5.3 df_CTNCapacity create
        #   5.3.1
        df_CTNItemCapacity = df_CTNItemSetWeek.copy()
    
        #   5.3.2 필요컬럼 발췌
        df_CTNItemCapacity = df_CTNItemCapacity[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN, W_RESOURCE_BASE_CAPACITY_COLUMN,
            W_COARSER_MAXIMUM_U_QUANTITY_COLUMN, W_COARSER_MINIMUM_U_QUANTITY_COLUMN
        ]]
        print_df(df_CTNItemCapacity, 'STEP3 by 5.3.2 _____ df_CTNItemCapacity .... final')



        # 5.4 df_MCTItemSetAsn create
        #   5.4.1
        df_MCTItemSetPrev = pd.merge(df_in_BOMMaster, df_CTNItemSetCopy, how='inner',
                                     left_on=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN, LOCATION_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        print_df(df_MCTItemSetPrev, 'STEP3 by 5.4.1 _____ df_MCTItemSetPrev .... merge[df_in_BOMMaster, df_CTNItemSetCopy]')
    
        #   5.4.2 조건식 분리
        condition_ap2_all = is_all(df_MCTItemSetPrev[SALES_DOMAIN_AP2_COLUMN])
    
        #   5.4.3 전체 조건식
        conditions_set = condition_ap2_all
    
        #   5.4.4 조건식에 맞는 데이터 copy
        df_MCTItemSetPrev = df_MCTItemSetPrev[conditions_set].copy()
        print_df(df_MCTItemSetPrev, 'STEP3 by 5.4.4 _____ df_MCTItemSetPrev .... filter')
    
        #   5.4.5 df_MCTItemSetPrev, df_in_ItemSiteAsn
        df_MCTItemSetAsn = pd.merge(df_MCTItemSetPrev, df_in_ItemSiteAsn, how='inner', on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        print_df(df_MCTItemSetAsn, 'STEP3 by 5.4.5 _____ df_MCTItemSetAsn .... final')



        # 5.5 df_buf_MCTItemSet create
        #   5.5.1
        df_buf_MCTItemSet = pd.merge(df_MCTItemSetAsn, df_in_TactTime, how='inner', on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        print_df(df_buf_MCTItemSet, 'STEP3 by 5.5.1 _____ df_buf_MCTItemSet .... create')
    
        #   5.5.2 ACTIVITY 및 RESOURCE create
        df_buf_MCTItemSet[ACTIVITY2_COLUMN] = ('RT_' + df_buf_MCTItemSet[BOM_ID_COLUMN] + '@' + df_buf_MCTItemSet[LOCATION_COLUMN])
        df_buf_MCTItemSet[RESOURCE_GROUP_COLUMN] = ('RT_' + df_buf_MCTItemSet[BOM_ID_COLUMN] + '@' + df_buf_MCTItemSet[LOCATION_COLUMN] + '_' + df_buf_MCTItemSet[LINE_COLUMN])
        df_buf_MCTItemSet[W_SIMULTANEOUS_CCA_COLUMN] = 1
        df_buf_MCTItemSet.rename(columns={
            BOM_ID_COLUMN: ACTIVITY1_COLUMN,
            ITEM_COLUMN: ACTIVITY3_COLUMN
        }, inplace=True)
    
        #   5.5.3 필요컬럼 발췌
        df_buf_MCTItemSet = df_buf_MCTItemSet[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]].drop_duplicates()
        print_df(df_buf_MCTItemSet, 'STEP3 by 5.5.3 _____ df_buf_MCTItemSet .... final')

        #   5.5.4 df_CTNSimultaneous3 create
        df_CTNSimultaneous3 = df_buf_MCTItemSet.copy()
        print_df(df_CTNSimultaneous3, 'STEP3 by 5.5.4 _____ df_CTNSimultaneous3 .... final')



        # 5.6 df_buf_SCTItemSet 구성, df_buf_CTNItemConsumeAsn4 create
        df_SCTItemSetPrev = pd.merge(df_in_BODItem, df_CTNItemSetCopy, how='inner', on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
    
        #   5.6.1 조건식 분리
        condition_ap2_not_all = is_not_all(df_SCTItemSetPrev[SALES_DOMAIN_AP2_COLUMN])
    
        #   5.6.2 전체 조건식
        # conditions_set = condition_gc_not_all | condition_ap2_not_all
        conditions_set = condition_ap2_not_all
    
        #   5.6.3 조건식에 맞는 데이터 copy
        df_SCTItemSetPrev = df_SCTItemSetPrev[conditions_set].copy()
    
        #   5.6.4 df_ItemSiteAsnLocation[Location, Sub Location] 이 df_SCTItemSetPrev[Location] 에 속한것 copy
        df_SCTSetLocation = (
            df_SCTItemSetPrev[
                df_SCTItemSetPrev[LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN]) |
                df_SCTItemSetPrev[SUB_LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN])
            ].copy()
        )
        print_df(df_SCTSetLocation, 'STEP3 by 5.6.4 _____ df_SCTSetLocation .... filter')
    
        #   5.6.5 df_ItemSiteAsnItem[Item] 이 df_SCTSetLocation[Item] 에 속한것 copy
        df_SCTSetLocationItem = df_SCTSetLocation[df_SCTSetLocation[ITEM_COLUMN].isin(df_ItemSiteAsnItem[ITEM_COLUMN])].copy()
        print_df(df_SCTSetLocationItem, 'STEP3 by 5.6.5 _____ df_SCTSetLocationItem ... filter')
    
        #   5.6.6 df_SCTSetLocationItem, df_in_SiteAP2Map join
        df_SCTSetItemSiteAP2Map = pd.merge(df_SCTSetLocationItem, df_in_SiteAP2Map, how='inner',
                                           left_on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN],
                                           right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN])
        df_SCTSetItemSiteAP2Map = df_SCTSetItemSiteAP2Map[
            (df_SCTSetItemSiteAP2Map[SALES_DOMAIN_AP2_COLUMN] == df_SCTSetItemSiteAP2Map[SITE_AP2_MAP_SHIP_TO_COLUMN])
        ].copy()
        print_df(df_SCTSetItemSiteAP2Map, 'STEP3 by 5.6.6 _____ df_SCTSetItemSiteAP2Map .... filter')
    
        #   5.6.7 컬럼명 변경
        df_SCTSetItemSiteAP2Map.rename(columns={'Location.[Location]_x': LOCATION_COLUMN}, inplace=True)
    
        #   5.6.8 컬럼삭제
        df_SCTSetItemSiteAP2Map = df_SCTSetItemSiteAP2Map.drop(labels=['Location.[Location]_y'], axis=1)
        print_df(df_SCTSetItemSiteAP2Map, 'STEP3 by 5.6.8 _____ df_SCTSetItemSiteAP2Map')
    
        #   5.6.9 df_buf_SCTSet create
        df_buf_SCTItemSet = df_SCTSetItemSiteAP2Map.copy()
        df_buf_SCTItemSet[ACTIVITY1_COLUMN] = (
                df_buf_SCTItemSet[LOCATION_COLUMN] + '_' + df_buf_SCTItemSet[SUB_LOCATION_COLUMN] + '_' + df_buf_SCTItemSet[TRNAS_MODE_COLUMN]
        )
        df_buf_SCTItemSet[RESOURCE_GROUP_COLUMN] = (
                df_buf_SCTItemSet[LOCATION_COLUMN] + '_' + df_buf_SCTItemSet[SUB_LOCATION_COLUMN] + '_' + df_buf_SCTItemSet[TRNAS_MODE_COLUMN] + '_' + df_buf_SCTItemSet[ITEM_COLUMN]
        )
        df_buf_SCTItemSet[W_SIMULTANEOUS_CCA_COLUMN] = 1
        df_buf_SCTItemSet.rename(columns={TRNAS_MODE_COLUMN: ACTIVITY2_COLUMN, ITEM_COLUMN: ACTIVITY3_COLUMN}, inplace=True)
    
        #   5.6.10 필요컬럼 발췌
        df_buf_SCTItemSet = df_buf_SCTItemSet[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]].drop_duplicates()
        print_df(df_buf_SCTItemSet, 'STEP3 by 5.6.10 _____ df_buf_SCTItemSet')
    
    
        # 5.7 df_MCTItemSet + df_SCTItemSet  를 Distinct하여  df_CTNSimultaneous 에 Insert
        #   5.7.1 df_MCTItem_CTNSimultaneous 를 distinct
        df_MCTItem_CTNSimultaneous = df_buf_MCTItemSet.copy()
        df_MCTItem_CTNSimultaneous[W_INPUT_RESOURCE_PRIORITY_COLUMN] = 1
        df_MCTItem_CTNSimultaneous[W_RESOURCE_CATEGORY_COLUMN] = 'O'
        df_MCTItem_CTNSimultaneous[W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN] = 1
        df_MCTItem_CTNSimultaneous[W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN] = 1
        df_MCTItem_CTNSimultaneous = df_MCTItem_CTNSimultaneous[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            W_INPUT_RESOURCE_PRIORITY_COLUMN, W_RESOURCE_CATEGORY_COLUMN, W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN, W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN
        ]].drop_duplicates()
        print_df(df_MCTItem_CTNSimultaneous, 'STEP3 by 5.7.1 _____ df_MCTItem_CTNSimultaneous .... filter')
    
        #   5.7.2 df_SCTItem_CTNSimultaneous 를 distinct
        df_SCTItem_CTNSimultaneous = df_buf_SCTItemSet.copy()
        df_SCTItem_CTNSimultaneous[W_INPUT_RESOURCE_PRIORITY_COLUMN] = 1
        df_SCTItem_CTNSimultaneous[W_RESOURCE_CATEGORY_COLUMN] = 'O'
        df_SCTItem_CTNSimultaneous[W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN] = 1
        df_SCTItem_CTNSimultaneous[W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN] = 1
        df_SCTItem_CTNSimultaneous = df_SCTItem_CTNSimultaneous[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, RESOURCE_COLUMN, ACTIVITY3_COLUMN,
            W_INPUT_RESOURCE_PRIORITY_COLUMN, W_RESOURCE_CATEGORY_COLUMN, W_RESOURCE_CONSUMED_QUANTITY_PER_COLUMN, W_RESOURCE_CONSUMPTION_ASSOCIATION_COLUMN
        ]].drop_duplicates()
        print_df(df_SCTItem_CTNSimultaneous, 'STEP3 by 5.7.2 _____ df_SCTItem_CTNSimultaneous .... filter')
    
        #   5.7.3 df_CTNConsumeAsn3 create
        df_CTNConsumeAsn3 = pd.concat([df_MCTItem_CTNSimultaneous, df_SCTItem_CTNSimultaneous])

        # ====================> STEP3 by 5 (End)
    
        step('=====> STEP3 End')
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        # CTNCapacity concat
        df_out_CTNCapacity = pd.concat([df_CTNGroupCapacity, df_CTNItemCapacity])
    
        # CTNSimultaneous concat
        df_out_CTNSimultaneous = pd.concat([df_CTNSimultaneous1, df_CTNSimultaneous2, df_CTNSimultaneous3])
    
        # CTNConsumeAsn concat
        df_out_CTNConsumeAsn = pd.concat([df_CTNConsumeAsn1, df_CTNConsumeAsn2, df_CTNConsumeAsn3])
        
        df_out_CTNCapacity[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_CTNConsumeAsn[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_CTNSimultaneous[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_CTNCapacity, 'output table create .... df_out_CTNCapacity', True)
        print_df(df_out_CTNConsumeAsn, 'output table create .... df_out_CTNConsumeAsn', True)
        print_df(df_out_CTNSimultaneous, 'output table create .... df_out_CTNSimultaneous', True)
    
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_CTNCapacity = pd.DataFrame(columns=df_CTNCapacity_columns)
        df_out_CTNConsumeAsn = pd.DataFrame(columns=df_CTNConsumeAsn_columns)
        df_out_CTNSimultaneous = pd.DataFrame(columns=df_CTNSimultaneous_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_CTNCapacity = pd.DataFrame(columns=df_CTNCapacity_columns)
        df_out_CTNConsumeAsn = pd.DataFrame(columns=df_CTNConsumeAsn_columns)
        df_out_CTNSimultaneous = pd.DataFrame(columns=df_CTNSimultaneous_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
