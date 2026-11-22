"""
* 프로그램명
    - PY_MG_PlanningBOM

* 내용
    - Full BOM 기준 BOM Header / BOM Component 구성

* 변경이력
    - 2024.08.27 / 권태우 / Create
    - 2024.09.09 / 권태우 / [BOM_STATUS_COLUMN] == '1. Fixed' 조건 삭제
    - 2024.09.20 / 권태우 / output에 [BOM Master_Prty] = '1' 컬럼 추가
    - 2024.10.08 / 권태우 / df_in_PreAllocItem, df_in_PreAllocDetailW, df_PlanStartEndDate 추가

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column;
    - df_in_FullBOM     : Select (Version.[Version Name] * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [Location].[Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, ({Measure.[Full BOM_Acil Date], Measure.[Full BOM_Avail Qty], Measure.[Full BOM_BOM Date], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_Consume Qty], Measure.[Full BOM_Consume UOM], Measure.[Full BOM_Creation Time], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Flag], Measure.[Full BOM_HQ Dev Purchaser], Measure.[Full BOM_HQ Purchaser], Measure.[Full BOM_Issue Date], Measure.[Full BOM_MRP Controller], Measure.[Full BOM_Part Eff Enddate], Measure.[Full BOM_Part Eff Startdate], Measure.[Full BOM_Prty], Measure.[Full BOM_Purchaser], Measure.[Full BOM_SOP SET Qty], Measure.[Full BOM_SOP Version Qty], Measure.[Full BOM_SRA Date], Measure.[Full BOM_Safety Date], Measure.[Full BOM_Unit], Measure.[Full BOM_Update Time], Measure.[Full BOM_Valid]}) on column;
    - df_in_PreAllocItem    : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const by Item_Creation Time]}) on column;
    - df_in_PreAllocDetailW : Select (Version.[Version Name] * &PlanningHorizon * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const Detail W_Const Qty] }) on column;
    - df_PlanStartEndDate : Select (Version.[Version Name]) on row, ({Measure.[MP Plan End Date], Measure.[MP Plan Start Date]}) on column;

* Flow Summary
    - STEP1. Full BOM Data 발췌
    - STEP2. BOM Component 구성
    - STEP3. BOM Master 구성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BOMMaster
    - df_out_BOMComponent

* 데이타 초기화
    -

* RUN 스크립트
    - exec plugin instance [PY_MG_PlanningBOM] for Measures {[BOM Master_BOM ID]}
       using scope (&MPV)
       using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Measure Group : BOM Master
        Select (&MPV * [Location].[Location] * [BOM Info].[BOM ID] ) on row,
        ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column limit 1000;

    - Measure Group : BOM Component
        Select (&MPV * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row,
        ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate], Measure.[BOM Comp_Valid Flag]}) on column limit 1000;

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
str_instance = 'PY_MG_PlanningBOM'
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
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_FullBOM = read_csv_file("df_in_FullBOM")
            df_in_PreAllocItem = read_csv_file("df_in_PreAllocItem")
            df_in_PreAllocDetailW = read_csv_file("df_in_PreAllocDetailW")
            df_PlanStartEndDate = read_csv_file("df_PlanStartEndDate")
    
    
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_FullBOM, 'input table load .... df_in_FullBOM')
        print_df(df_in_PreAllocItem, 'input table load .... df_in_PreAllocItem')
        print_df(df_in_PreAllocDetailW, 'input table load .... df_in_PreAllocDetailW')
        print_df(df_PlanStartEndDate, 'input table load .... df_PlanStartEndDate')
    
        step('=====> STEP1 End')
        
        
        
    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
    
        LOCATION_COLUMN = 'Location.[Location]'
        TO_LOCATION_COLUMN = 'To Location.[To Location]'
        ITEM_COLUMN = 'Item.[Item]'
    
        BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_ID_COLUMN = 'BOM Master_BOM ID'
        TO_ITEM_COLUMN = 'To Item.[To Item]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        BOM_TYPE_COLUMN = 'BOM Type.[BOM Type]'
        BOM_STATUS_COLUMN = 'Status.[Status]'
        BOM_BOMSTATUS_COLUMN = 'BOM Status.[BOM Status]'
        FULL_BOM_EFF_ENDDATE_COLUMN = 'Full BOM_Eff Enddate'
        FULL_BOM_EFF_STARTDATE_COLUMN = 'Full BOM_Eff Startdate'
        FULL_BOM_PART_EFF_ENDDATE_COLUMN = 'Full BOM_Part Eff Enddate'
        FULL_BOM_PART_EFF_STARTDATE_COLUMN = 'Full BOM_Part Eff Startdate'
        FULL_BOM_BASE_QTY_COLUMN = 'Full BOM_Base Qty'
        FULL_BOM_FLAG_COLUMN = 'Full BOM_Flag'  # 용도 생각할것
        FULL_BOM_VAILD_COLUMN = 'Full BOM_Valid'
    
        BOM_COMP_CONSUME_QTY_COLUMN = 'BOM Comp_Consume Qty'
        BOM_COMP_EFF_ENDDATE_COLUMN = 'BOM Comp_Eff Enddate'
        BOM_COMP_EFF_STARTDATE_COLUMN = 'BOM Comp_Eff Startdate'
        BOM_COMP_VAILD_FLAG_COLUMN = 'BOM Comp_Valid Flag'
    
        TOP_ITEM_COLUMN = 'Top Item'
        CONSUMED_PART_COLUMN = 'Consumed Part'
        SOP_ITEM_COLUMN = 'SOP Item'
    
        BOM_MASTER_BOM_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_EFF_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'
        BOM_MASTER_PRIORITY_COLUMN = 'BOM Master_Prty'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'
        BOM_MASTER_BOM_STATUS_COLUMN = 'BOM Master_BOM Status'
        BOM_MASTER_BOM_TYPE_COLUMN = 'BOM Master_BOM Type'
        BOM_MASTER_BOM_VERSION_COLUMN = 'BOM Master_BOM Version'
        BOM_MASTER_BOM_LOCATION_COLUMN = 'BOM Master_BOM Location'
    
        MP_PLAN_START_DATE_COLUMN = 'MP Plan Start Date'
        MP_PLAN_END_DATE_COLUMN = 'MP Plan End Date'
    
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'
        ITEM_SITE_ASN_CUR_STATUS_COLUMN = 'Item Site Asn_Cur Status'
        ITEM_SITE_ASN_ITEM_GRP_COLUMN = 'Item Site Asn_Item Grp'
    
        GROUP_ID_COLUMN = 'Group.[Group ID]'
        PRE_ALLOC_CONST_DETAIL_W_CONST_QRT_COLUMN = 'Pre Alloc Const Detail W_Const Qty'

        df_BOMMaster_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, BOM_ID_COLUMN, BOM_MASTER_ID_COLUMN, BOM_MASTER_BOM_VERSION_COLUMN,
            BOM_MASTER_BOM_STATUS_COLUMN, BOM_MASTER_BOM_TYPE_COLUMN, BOM_MASTER_BOM_LOCATION_COLUMN,
            BOM_MASTER_EFF_STARTDATE_COLUMN, BOM_MASTER_EFF_ENDDATE_COLUMN, BOM_MASTER_PRIORITY_COLUMN,
        ]

        df_BOMComponent_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, BOM_ID_COLUMN, BOM_COMP_CONSUME_QTY_COLUMN,
            BOM_COMP_EFF_ENDDATE_COLUMN, BOM_COMP_EFF_STARTDATE_COLUMN, BOM_COMP_VAILD_FLAG_COLUMN,
        ]

        step('=====> STEP2 End')
        
        
        
    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # Item, Location 만 발췌, 중복값 삭제(Item, Location Distinct) 및 미사용 컬럼 삭제
        #   - df_in_ItemSiteAsn remake
        drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN]]
        df_in_ItemSiteAsn = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN], keep='first'
        )
    
        # MP Plan Week 가져오기
        df_PlanStartEndDate[MP_PLAN_START_DATE_COLUMN] = pd.to_datetime(df_PlanStartEndDate[MP_PLAN_START_DATE_COLUMN]).dt.strftime('%Y-%m-%d')
        df_PlanStartEndDate[MP_PLAN_END_DATE_COLUMN] = pd.to_datetime(df_PlanStartEndDate[MP_PLAN_END_DATE_COLUMN]).dt.strftime('%Y-%m-%d')
        print_df(df_PlanStartEndDate, 'STEP3 by 0.1 ____ df_PlanStartEndDate .... convert')
    
        mp_plan_start_date = get_first_value(df_PlanStartEndDate, MP_PLAN_START_DATE_COLUMN)
        step(f'=====> mp_plan_start_date : {mp_plan_start_date}')

        mp_plan_end_date = get_first_value(df_PlanStartEndDate, MP_PLAN_END_DATE_COLUMN)
        step(f'=====> mp_plan_end_date : {mp_plan_end_date}')
    
    
    
    
        # ====================> STEP3 by 1 (Start) -> df_fullbomset  Set 구성 / bom status에 따라 bom version의 처리
    
        # 1.1 df_fullbomset create // TOP Item / Location 기준의 비교
        #   1.1.1
        df_fullbomset = pd.merge(df_in_FullBOM, df_in_ItemSiteAsn, how='inner',
                                 left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN],
                                 right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
        print_df(df_fullbomset, 'STEP3 by 1.1.1 ____ df_fullbomset .... merge')
    
        #   1.1.2 df_fullbomset = df_fullbomset .drop(columns=[LOCATION_COLUMN])
        df_fullbomset.rename(columns={
            LOCATION_COLUMN: BOM_MASTER_BOM_LOCATION_COLUMN,
            TO_LOCATION_COLUMN: LOCATION_COLUMN,
        }, inplace=True)
    
    
        #   1.2.1 BOM_ID make
        df_fullbomset[BOM_ID_COLUMN] = np.where(
            (df_fullbomset[ITEM_COLUMN] == df_fullbomset[TO_ITEM_COLUMN]),
            df_fullbomset[TO_ITEM_COLUMN] + '_' + df_fullbomset[BOM_VERSION_COLUMN],
            df_fullbomset[TO_ITEM_COLUMN] + '_NA'
        )
    
        df_fullbomset[SOP_ITEM_COLUMN] = df_fullbomset[TO_ITEM_COLUMN]
    
        #   1.1.2 필요컬럼 발췌
        df_fullbomset = df_fullbomset[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, ITEM_METERIAL_COLUMN, SOP_ITEM_COLUMN, LOCATION_COLUMN, BOM_ID_COLUMN,
            BOM_VERSION_COLUMN, BOM_TYPE_COLUMN, BOM_STATUS_COLUMN, BOM_BOMSTATUS_COLUMN, BOM_MASTER_BOM_LOCATION_COLUMN,
            FULL_BOM_BASE_QTY_COLUMN, FULL_BOM_EFF_STARTDATE_COLUMN, FULL_BOM_EFF_ENDDATE_COLUMN, FULL_BOM_PART_EFF_STARTDATE_COLUMN,
            FULL_BOM_PART_EFF_ENDDATE_COLUMN, FULL_BOM_FLAG_COLUMN,
        ]].drop_duplicates()
        print_df(df_fullbomset, 'STEP3 by 1.1.2 ____ df_fullbomset .... column rename')
    
        #   1.1.3 컬럼명 변경
        df_fullbomset.rename(columns={
            ITEM_COLUMN: TOP_ITEM_COLUMN,
            ITEM_METERIAL_COLUMN: CONSUMED_PART_COLUMN,
            FULL_BOM_FLAG_COLUMN: BOM_COMP_VAILD_FLAG_COLUMN,
        }, inplace=True)
        print_df(df_fullbomset, 'STEP3 by 1.1 ____ df_fullbomset .... final')
    
        # ====================> STEP3 by 1 (End)
    
    
    
    
    
    
        # ====================> STEP3 by 2 (Start) -> df_fullbomset  Set 을  df_out_BOMComponent Measure 정보 Insert
    
        # 2.1 df_fullbomset 을 df_out_BOMComponent Measure 정보 Insert
        #   2.1.1 df_bom_component_set create
        df_bom_component_set = df_fullbomset.copy()
        df_bom_component_set[BOM_COMP_CONSUME_QTY_COLUMN] = df_bom_component_set[FULL_BOM_BASE_QTY_COLUMN]
        df_bom_component_set[BOM_COMP_EFF_ENDDATE_COLUMN] = df_bom_component_set[FULL_BOM_EFF_ENDDATE_COLUMN]
        df_bom_component_set[BOM_COMP_EFF_STARTDATE_COLUMN] = df_bom_component_set[FULL_BOM_EFF_STARTDATE_COLUMN]
        print_df(df_bom_component_set, 'STEP3 by 2.1.1 ____ df_bom_component_set .... create')
    
        df_bom_component_set.rename(columns={CONSUMED_PART_COLUMN: ITEM_COLUMN}, inplace=True)

        df_bom_component_set = df_bom_component_set[df_BOMComponent_columns].drop_duplicates()
        print_df(df_bom_component_set, 'STEP3 by 2.1 ____ df_bom_component_set .... final')
    
    
        # 2.2 df_fullbomset 을 Distinct 하여 BOM Master 정보 Insert
        #   2.2.1 df_bom_master_set create
        df_bom_master_set = df_fullbomset.copy()
        print_df(df_bom_master_set, 'STEP3 by 2.2.1 ____ df_bom_master_set .... create')
    
        df_bom_master_set.rename(columns={
            TOP_ITEM_COLUMN: BOM_MASTER_ID_COLUMN,
            BOM_VERSION_COLUMN: BOM_MASTER_BOM_VERSION_COLUMN,
            BOM_STATUS_COLUMN: BOM_MASTER_BOM_STATUS_COLUMN,
            BOM_TYPE_COLUMN: BOM_MASTER_BOM_TYPE_COLUMN,
            FULL_BOM_EFF_STARTDATE_COLUMN: BOM_MASTER_EFF_STARTDATE_COLUMN,
            FULL_BOM_EFF_ENDDATE_COLUMN: BOM_MASTER_EFF_ENDDATE_COLUMN,
        }, inplace=True)
    
        #   2.2.2 필요컬럼선택 및 설정
        df_bom_master_set[BOM_MASTER_PRIORITY_COLUMN] = 1
        df_bom_master_set = df_bom_master_set[df_BOMMaster_columns].drop_duplicates()
        print_df(df_bom_master_set, 'STEP3 by 2.2 ____ df_bom_master_set .... final')
    
        # ====================> STEP3 by 2 (End)
    
    
    
    
    
        # ====================> STEP3 by 3 (Start) -> update  df_in_ItemSiteAsn set Item Site Asn_Engine Flag = 'true'
    
        # 3.1
        #   3.1.1
        df_buf_bom_set_1 = df_fullbomset.copy()
        print_df(df_buf_bom_set_1, 'STEP3 by 3.1.1 ____ df_buf_bom_set_1 .... create')
    
        #   3.1.2 'Consumed Part' 처리
        df_buf_bom_set_1 = df_buf_bom_set_1[[CONSUMED_PART_COLUMN]].drop_duplicates()
        df_buf_bom_set_1.rename(columns={CONSUMED_PART_COLUMN: ITEM_COLUMN,}, inplace=True)
        print_df(df_buf_bom_set_1, 'STEP3 by 3.1.2 ____ df_buf_bom_set_1 .... final')
    
        #   3.1.3 'SOP Item' 처리
        df_buf_bom_set_2 = df_fullbomset.copy()
        df_buf_bom_set_2 = df_buf_bom_set_2[[SOP_ITEM_COLUMN]].drop_duplicates()
        df_buf_bom_set_2.rename(columns={SOP_ITEM_COLUMN: ITEM_COLUMN,}, inplace=True)
    
        # 3.2 df_buf_bom_set create
        df_buf_bom_set = pd.concat([df_buf_bom_set_1, df_buf_bom_set_2]).drop_duplicates()
        print_df(df_buf_bom_set, 'STEP3 by 3.2 ____ df_buf_bom_set .... final')
    
        # ====================> STEP3 by 3 (End)
    
    
    
    
    
        # ====================> STEP3 by 4 (Start) -> Pre Alloc Constriant 대상 Item Site Asn에 넣기
    
        # EXISTS 조건을 만족하는 행을 필터링
        df_filtered = df_in_PreAllocDetailW[df_in_PreAllocDetailW[GROUP_ID_COLUMN].isin(df_in_PreAllocItem[GROUP_ID_COLUMN])]
    
        # 선택된 컬럼으로 새로운 데이터프레임을 만듭니다.
        df_result = df_filtered[[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, LOCATION_COLUMN]].drop_duplicates()
    
        # 새로운 컬럼 추가
        df_result[ITEM_SITE_ASN_CUR_STATUS_COLUMN] = 'Active'
        df_result[ITEM_SITE_ASN_ENGINE_FLAG_COLUMN] = 'true'
        df_result[ITEM_SITE_ASN_ITEM_GRP_COLUMN] = 'PAC'
        print_df(df_result, 'STEP3 by 4 ____ df_result .... final')
    
        # ====================> STEP3 by 4 (End)
    
        step('=====> STEP3 End')
        
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        df_out_BOMMaster = rename_and_delete_df(df_bom_master_set)
        df_out_BOMComponent = rename_and_delete_df(df_bom_component_set)

        df_bom_master_set[VERSION_NAME_COLUMN] = paramOutVersion
        df_bom_component_set[VERSION_NAME_COLUMN] = paramOutVersion

        step('=====> STEP4 End')
        
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_BOMMaster, 'output table create .... df_out_BOMMaster', True)
        print_df(df_out_BOMComponent, 'output table create .... df_out_BOMComponent', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BOMMaster = pd.DataFrame(columns=df_BOMMaster_columns)
        df_out_BOMComponent = pd.DataFrame(columns=df_BOMComponent_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BOMMaster = pd.DataFrame(columns=df_BOMMaster_columns)
        df_out_BOMComponent = pd.DataFrame(columns=df_BOMComponent_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')