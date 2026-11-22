"""
* 프로그램명
    - PY_MG_SOPFrozenList

* 내용
    - SOP Frozen List 구성을 위한 프로그램

* 변경이력
    - 2024.08.12 / 권태우 / Create
    - 2024.11.11 / 권태우 / 'SOP Frozen_Ecp Item' '^' 처리

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn     : Select (Version.[Version Name] * &FinishedGoods* &MFLocation * [Item].[Item] * [Item].[Product Group] * [Item].[Product] * [Item].[SCM Type] * [Item].[A2] * [Item].[A9] * [Item].[A11] * [Item].[A14]  ) on row, ({Measure.[Item Site Asn_Asn]}) on column.filter(Measure.[Item Site Asn_Asn] == 1);
    - df_in_SOPFrozen       : Select (Version.[Version Name] * [Group].[Group ID] ) on row, ({Measure.[SOP Frozen_Ctg], Measure.[SOP Frozen_Definition], Measure.[SOP Frozen_Ecp Item], Measure.[SOP Frozen_From Site], Measure.[SOP Frozen_Frz], Measure.[SOP Frozen_Frz Enddate], Measure.[SOP Frozen_Frz Startdate], Measure.[SOP Frozen_Inch], Measure.[SOP Frozen_Item], Measure.[SOP Frozen_Mkt Name], Measure.[SOP Frozen_Prod Grp], Measure.[SOP Frozen_Product], Measure.[SOP Frozen_Prty], Measure.[SOP Frozen_SCM Type], Measure.[SOP Frozen_To Site], Measure.[SOP Frozen_Total Flag], Measure.[SOP Frozen_Year]}) on column where {Measure.[SOP Frozen_Valid Flag] == "Y"};
    - df_in_SOPFrozenGrpSET : Select (Version.[Version Name] * [Group].[Group ID] ) on row, ({Measure.[SOP Frozen Grp SET_Ctg], Measure.[SOP Frozen Grp SET_Definition], Measure.[SOP Frozen Grp SET_Digit], Measure.[SOP Frozen Grp SET_From Site], Measure.[SOP Frozen Grp SET_Frz], Measure.[SOP Frozen Grp SET_Frz Enddate], Measure.[SOP Frozen Grp SET_Frz Startdate], Measure.[SOP Frozen Grp SET_Inch], Measure.[SOP Frozen Grp SET_Mkt Name], Measure.[SOP Frozen Grp SET_Prod Grp], Measure.[SOP Frozen Grp SET_Product], Measure.[SOP Frozen Grp SET_Prty], Measure.[SOP Frozen Grp SET_SCM Type], Measure.[SOP Frozen Grp SET_To Site], Measure.[SOP Frozen Grp SET_Total Flag], Measure.[SOP Frozen Grp SET_Year]}) on column where { Measure.[SOP Frozen Grp SET_Valid Flag] == Y};
    - df_in_SOPFrozenPeriod : Select (Version.[Version Name] * [Location].[Location] * [Item].[SCM Type] * [Product].[Product Group] ) on row, ({Measure.[SOP Frozen Period_Smry Copy]}) on column;


* Flow Summary
    - STEP1. BOD List 발췌 기준으로 Item Site Asn 조합하여  BOD Item 을 구성한다.
    - STEP2. BOD Prod Set 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_SopFrozenList

* 데이타 초기화
    - DELETE DATA FOR MODEL [SOP Frozen List] WHERE  {[Version].[Version Name].[CurrentWorkingView]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_SOPFrozenList] for measures {[SOP Frozen List_Ctg]} using scope (&MPV * Group.[Group Type].[MFF_S].relatedmembers([Group ID]))
        using arguments {(ExecutionMode, "MediumWeight"), (IncludeNullRows, "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
    - Select (&MPV * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row,
        ({Measure.[SOP Frozen List_Ctg], Measure.[SOP Frozen List_Digit], Measure.[SOP Frozen List_FP Period], Measure.[SOP Frozen List_Frz], Measure.[SOP Frozen List_Frz Enddate], Measure.[SOP Frozen List_Frz Startdate], Measure.[SOP Frozen List_Grp Frz], Measure.[SOP Frozen List_Grp Frz Enddate], Measure.[SOP Frozen List_Grp Frz Startdate], Measure.[SOP Frozen List_Grp Period Total], Measure.[SOP Frozen List_Period Total]}) on column;

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
str_instance = 'PY_MG_SOPFrozenList'
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




def decode(column, condition, if_all, alternate_value):
    return np.where(column == condition, if_all, alternate_value)




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
            df_in_SOPFrozen = read_csv_file("df_in_SOPFrozen")
            df_in_SOPFrozenGrpSET = read_csv_file("df_in_SOPFrozenGrpSET")
            df_in_SOPFrozenPeriod = read_csv_file("df_in_SOPFrozenPeriod")

        print_df(df_in_ItemSiteAsn,'input table load .....> df_in_ItemSiteAsn')
        print_df(df_in_SOPFrozen, 'input table load .....> df_in_SOPFrozen')
        print_df(df_in_SOPFrozenGrpSET, 'input table load .....> df_in_SOPFrozenGrpSET')
        print_df(df_in_SOPFrozenPeriod, 'input table load .....> df_in_SOPFrozenPeriod')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'

        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = '[Sub Location].[Sub Location]'
        TO_LOCATION_COLUMN = '[To Location].[To Location]'

        ITEM_COLUMN = 'Item.[Item]'
        ITEM_TYPE_COLUMN = 'Item.[Item Type]'
        ITEM_PRODUCT_GROUPL_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_COLUMN = 'Item.[Product]'
        ITEM_SCM_TYPE_COLUMN = 'Item.[SCM Type]'
        ITEM_SCM_TYPE_X_COLUMN = 'Item.[SCM Type]_x'
        ITEM_SCM_TYPE_Y_COLUMN = 'Item.[SCM Type]_y'
        ITEM_A2_COLUMN = 'Item.[A2]'
        ITEM_A9_COLUMN = 'Item.[A9]'
        ITEM_A11_COLUMN = 'Item.[A11]'
        ITEM_A14_COLUMN = 'Item.[A14]'
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'
        ITEM_SITE_ASN_ASN_COLUMN = 'Item Site Asn_Asn'

        PRODUCT_GROUP_PRODUCT_GROUP_COLUMN = 'Product Group.[Product Group]'
        PRODUCT_PRODUCT_GROUP_COLUMN = 'Product.[Product Group]'
        CATEGORY_COLUMN = 'Category.[Category]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'

        SOP_FROZEN_CTG_COLUMN = 'SOP Frozen_Ctg'
        SOP_FROZEN_DEFINITION_COLUMN = 'SOP Frozen_Definition'
        SOP_FROZEN_ECP_ITEM_COLUMN = 'SOP Frozen_Ecp Item'
        SOP_FROZEN_FROM_SITE_COLUMN = 'SOP Frozen_From Site'
        SOP_FROZEN_FRZ_COLUMN = 'SOP Frozen_Frz'
        SOP_FROZEN_FRZ_ENDDATE_COLUMN = 'SOP Frozen_Frz Enddate'
        SOP_FROZEN_FRZ_STARTDATE_COLUMN = 'SOP Frozen_Frz Startdate'
        SOP_FROZEN_INCH_COLUMN = 'SOP Frozen_Inch'
        SOP_FROZEN_ITEM_COLUMN = 'SOP Frozen_Item'
        SOP_FROZEN_MKT_NAME_COLUMN = 'SOP Frozen_Mkt Name'
        SOP_FROZEN_PROD_GRP_COLUMN = 'SOP Frozen_Prod Grp'
        SOP_FROZEN_PRODUCT_COLUMN = 'SOP Frozen_Product'
        SOP_FROZEN_PRTY_COLUMN = 'SOP Frozen_Prty'
        SOP_FROZEN_SCM_TYPE_COLUMN = 'SOP Frozen_SCM Type'
        SOP_FROZEN_TO_SITE_COLUMN = 'SOP Frozen_To Site'
        SOP_FROZEN_TOTAL_FLAG_COLUMN = 'SOP Frozen_Total Flag'
        SOP_FROZEN_YEAR_COLUMN = 'SOP Frozen_Year'

        SOP_FROZEN_GRP_SET_CTG_COLUMN = 'SOP Frozen Grp SET_Ctg'
        SOP_FROZEN_GRP_SET_DEFINITION_COLUMN = 'SOP Frozen Grp SET_Definition'
        SOP_FROZEN_GRP_SET_DIGIT_COLUMN = 'SOP Frozen Grp SET_Digit'
        SOP_FROZEN_GRP_SET_FROM_SITE_COLUMN = 'SOP Frozen Grp SET_From Site'
        SOP_FROZEN_GRP_SET_FRZ_COLUMN = 'SOP Frozen Grp SET_Frz'
        SOP_FROZEN_GRP_SET_FRZ_ENDDATE_COLUMN = 'SOP Frozen Grp SET_Frz Enddate'
        SOP_FROZEN_GRP_SET_FRZ_STARTDATE_COLUMN = 'SOP Frozen Grp SET_Frz Startdate'
        SOP_FROZEN_GRP_SET_INCH_COLUMN = 'SOP Frozen Grp SET_Inch'
        SOP_FROZEN_GRP_SET_MKT_NAME_COLUMN = 'SOP Frozen Grp SET_Mkt Name'
        SOP_FROZEN_GRP_SET_PROD_GRP_COLUMN = 'SOP Frozen Grp SET_Prod Grp'
        SOP_FROZEN_GRP_SET_PRODUCT_COLUMN = 'SOP Frozen Grp SET_Product'
        SOP_FROZEN_GRP_SET_PRTY_COLUMN = 'SOP Frozen Grp SET_Prty'
        SOP_FROZEN_GRP_SET_SCM_TYPE_COLUMN = 'SOP Frozen Grp SET_SCM Type'
        SOP_FROZEN_GRP_SET_TO_SITE_COLUMN = 'SOP Frozen Grp SET_To Site'
        SOP_FROZEN_GRP_SET_TOTAL_FLAG_COLUMN = 'SOP Frozen Grp SET_Total Flag'
        SOP_FROZEN_GRP_SET_YEAR_COLUMN = 'SOP Frozen Grp SET_Year'

        SOP_FROZEN_PERIOD_SMRY_COPY_COLUMN = 'SOP Frozen Period_Smry Copy'

        SOP_FROZEN_LIST_CTG_COLUMN = 'SOP Frozen List_Ctg'
        SOP_FROZEN_LIST_FRZ_COLUMN = 'SOP Frozen List_Frz'
        SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN = 'SOP Frozen List_Frz Enddate'
        SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN = 'SOP Frozen List_Frz Startdate'
        SOP_FROZEN_LIST_PERIOD_TOTAL_COLUMN = 'SOP Frozen List_Period Total'
        SOP_FROZEN_LIST_DIGIT_COLUMN = 'SOP Frozen List_Digit'
        SOP_FROZEN_LIST_FP_PERIOD_COLUMN = 'SOP Frozen List_FP Period'

        SOP_FROZEN_LIST_GRP_FRZ_COLUMN = 'SOP Frozen List_Grp Frz'
        SOP_FROZEN_LIST_GRP_FRZ_ENDDATE_COLUMN = 'SOP Frozen List_Grp Frz Enddate'
        SOP_FROZEN_LIST_GRP_FRZ_STARTDATE_COLUMN = 'SOP Frozen List_Grp Frz Startdate'
        SOP_FROZEN_LIST_GRP_PERIOD_TOTAL_COLUMN = 'SOP Frozen List_Grp Period Total'

        ALL_VALUE = 'ALL'
        
        df_SOPFrozen_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, GROUP_ID_COLUMN,
            SOP_FROZEN_LIST_CTG_COLUMN, SOP_FROZEN_LIST_FRZ_COLUMN, SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN,
            SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN, SOP_FROZEN_LIST_PERIOD_TOTAL_COLUMN, SOP_FROZEN_LIST_DIGIT_COLUMN,
            SOP_FROZEN_LIST_FP_PERIOD_COLUMN,
        ]
        
        df_SopFrozenList_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, GROUP_ID_COLUMN,
            SOP_FROZEN_LIST_CTG_COLUMN, SOP_FROZEN_LIST_GRP_FRZ_COLUMN, SOP_FROZEN_LIST_GRP_FRZ_ENDDATE_COLUMN,
            SOP_FROZEN_LIST_GRP_FRZ_STARTDATE_COLUMN, SOP_FROZEN_LIST_GRP_PERIOD_TOTAL_COLUMN, SOP_FROZEN_LIST_DIGIT_COLUMN,
            SOP_FROZEN_LIST_FP_PERIOD_COLUMN,
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
        
        # -------------------------- 테스트 디버깅 데이터 Start --------------------------
        # df_in_SOPFrozen = df_in_SOPFrozen[df_in_SOPFrozen[SOP_FROZEN_ITEM_COLUMN] == 'QN55LST7TAFXZA^QN75LST7TAFXZA^QN65LST7TAFXZA^QN65LST9TAFXZA']
        # df_in_SOPFrozen = df_in_SOPFrozen[df_in_SOPFrozen[GROUP_ID_COLUMN] == 'MFF_S_00043']
        # print_df(df_in_SOPFrozen, 'STEP 3 by 0.0.0 ____ df_in_SOPFrozen .... filter')
        # -------------------------- 테스트 디버깅 데이터 End --------------------------
        
        df_in_ItemSiteAsn[ITEM_A11_COLUMN] = df_in_ItemSiteAsn[ITEM_A11_COLUMN].astype('str')



        df_in_ItemSiteAsn = pd.merge(df_in_ItemSiteAsn, df_in_SOPFrozenPeriod, how='inner',
                                     left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_SCM_TYPE_COLUMN, ITEM_PRODUCT_GROUPL_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_SCM_TYPE_COLUMN, PRODUCT_PRODUCT_GROUP_COLUMN]).drop_duplicates()
        print_df(df_in_ItemSiteAsn, 'STEP3 by 0.1 ____ df_in_ItemSiteAsn .... merge[df_in_ItemSiteAsn, df_in_SOPFrozenPeriod]')
        df_in_ItemSiteAsn = df_in_ItemSiteAsn.drop(columns=[PRODUCT_PRODUCT_GROUP_COLUMN])




        # ====================> STEP3 by 1 (Start)
        
        # 1.1 df_SOPFrozen create
        #   1.1.1 'SOP Frozen_Ecp Item', 'SOP Frozen_Item' 값을 '^'로 분할 후 explode하여 모든 항목을 개별 행으로 나눔
        df_in_SOPFrozen[SOP_FROZEN_ECP_ITEM_COLUMN] = df_in_SOPFrozen[SOP_FROZEN_ECP_ITEM_COLUMN].astype('str')

        df_in_SOPFrozen[SOP_FROZEN_ECP_ITEM_COLUMN+'_split'] = df_in_SOPFrozen[SOP_FROZEN_ECP_ITEM_COLUMN].str.split('^')
        df_in_SOPFrozen[SOP_FROZEN_ITEM_COLUMN+'_split'] = df_in_SOPFrozen[SOP_FROZEN_ITEM_COLUMN].str.split('^')
        print_df(df_in_SOPFrozen, 'STEP3 by 1.1.1 ____ df_in_SOPFrozen .... split')

        df_in_SOPFrozen = df_in_SOPFrozen.explode(SOP_FROZEN_ECP_ITEM_COLUMN+'_split')
        df_in_SOPFrozen = df_in_SOPFrozen.explode(SOP_FROZEN_ITEM_COLUMN+'_split')
        print_df(df_in_SOPFrozen, 'STEP3 by 1.1.1 ____ df_in_SOPFrozen .... explode')


        #   1.1.2 df_in_ItemSiteAsn, df_in_SOPFrozen join
        df_SOPFrozen = pd.merge(df_in_ItemSiteAsn, df_in_SOPFrozen, how='inner',
                                left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN],
                                right_on=[VERSION_NAME_COLUMN, SOP_FROZEN_FROM_SITE_COLUMN, SOP_FROZEN_ITEM_COLUMN+'_split']).drop_duplicates()
        print_df(df_SOPFrozen, 'STEP3 by 1.1.2 ____ df_SOPFrozen .... merge[df_in_ItemSiteAsn, df_in_SOPFrozen]')

        df_SOPFrozen[SOP_FROZEN_INCH_COLUMN] = df_SOPFrozen[SOP_FROZEN_INCH_COLUMN].astype('str')
        df_SOPFrozen[SOP_FROZEN_ECP_ITEM_COLUMN] = df_SOPFrozen[SOP_FROZEN_ECP_ITEM_COLUMN].astype('str')


        #   1.1.3 filter
        def create_column_filter(df, item_col, sop_frozen_col, all_value):
            sop_frozen_upper = df[sop_frozen_col].str.upper()
            return df[item_col] == decode(sop_frozen_upper, all_value, df[item_col], df[sop_frozen_col])

        def create_item_filter(df, item_column, sop_frozen_item_column, all_value):
            sop_frozen_upper = df[sop_frozen_item_column].str.upper()
            split_column = f"{sop_frozen_item_column}_split"
            return df[item_column].isin(decode(sop_frozen_upper, all_value, df[item_column], df[split_column]))

        def filter_sop_frozen(df, all_value):
            # 초기 ECP 아이템 제외 필터
            initial_filter = ~df[ITEM_COLUMN].isin(df[SOP_FROZEN_ECP_ITEM_COLUMN + '_split'])

            # 컬럼 매핑 정의
            column_pairs = [
                (ITEM_PRODUCT_GROUPL_COLUMN, SOP_FROZEN_PROD_GRP_COLUMN),
                (ITEM_SCM_TYPE_COLUMN, SOP_FROZEN_SCM_TYPE_COLUMN),
                (ITEM_PRODUCT_COLUMN, SOP_FROZEN_PRODUCT_COLUMN),
                (ITEM_A2_COLUMN, SOP_FROZEN_INCH_COLUMN),
                (ITEM_A9_COLUMN, SOP_FROZEN_DEFINITION_COLUMN),
                (ITEM_A11_COLUMN, SOP_FROZEN_YEAR_COLUMN),
                (ITEM_A14_COLUMN, SOP_FROZEN_MKT_NAME_COLUMN)
            ]

            # 모든 컬럼 페어에 대한 필터 생성
            column_filters = [
                create_column_filter(df, item_col, sop_col, all_value)
                for item_col, sop_col in column_pairs
            ]

            # 아이템 필터 추가
            item_filter = create_item_filter(df, ITEM_COLUMN, SOP_FROZEN_ITEM_COLUMN, all_value)

            # 모든 필터 조건 결합
            all_filters = [initial_filter] + column_filters + [item_filter]
            final_filter = np.logical_and.reduce(all_filters)

            return df[final_filter]

        df_SOPFrozen = filter_sop_frozen(df_SOPFrozen, ALL_VALUE)
        print_df(df_SOPFrozen, 'STEP3 by 1.1.3 ____ df_SOPFrozen .... filter')

        df_SOPFrozen = df_SOPFrozen.drop(columns=[SOP_FROZEN_ECP_ITEM_COLUMN+'_split', SOP_FROZEN_ITEM_COLUMN+'_split'])
        df_SOPFrozen.rename(columns={
            SOP_FROZEN_TO_SITE_COLUMN : SUB_LOCATION_COLUMN,
            SOP_FROZEN_CTG_COLUMN: SOP_FROZEN_LIST_CTG_COLUMN,
            SOP_FROZEN_FRZ_COLUMN: SOP_FROZEN_LIST_FRZ_COLUMN,
            SOP_FROZEN_FRZ_ENDDATE_COLUMN: SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN,
            SOP_FROZEN_FRZ_STARTDATE_COLUMN: SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN,
            SOP_FROZEN_TOTAL_FLAG_COLUMN: SOP_FROZEN_LIST_PERIOD_TOTAL_COLUMN,
            SOP_FROZEN_PERIOD_SMRY_COPY_COLUMN: SOP_FROZEN_LIST_FP_PERIOD_COLUMN,
        }, inplace=True)

        #   1.1.4 원하는 컬럼만 선택
        df_SOPFrozen[SOP_FROZEN_LIST_DIGIT_COLUMN] = None
        df_SOPFrozen = df_SOPFrozen[df_SOPFrozen_columns].drop_duplicates()
        print_df(df_SOPFrozen, 'STEP3 by 1.1.4 ____ df_SOPFrozen .... final')
        
        # ====================> STEP3 by 1 (End)




        # ====================> STEP3 by 2 (Start)

        # 2.1 df_SOPFrozenGrpSET create
        #   2.1.1 df_in_ItemSiteAsn, df_in_SOPFrozen join
        df_SOPFrozenGrpSET = pd.merge(df_in_ItemSiteAsn, df_in_SOPFrozenGrpSET, how='inner',
                                      left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN],
                                      right_on=[VERSION_NAME_COLUMN, SOP_FROZEN_GRP_SET_FROM_SITE_COLUMN])
        print_df(df_SOPFrozenGrpSET, 'STEP3 by 2.1.1 ____ df_SOPFrozenGrpSET .... merge[df_in_ItemSiteAsn, df_in_SOPFrozenGrpSET]')

        df_SOPFrozenGrpSET[SOP_FROZEN_GRP_SET_INCH_COLUMN] = df_SOPFrozenGrpSET[SOP_FROZEN_GRP_SET_INCH_COLUMN].astype('str')

        #   2.1.2 조건 필터
        #       비교할 컬럼 쌍을 정의
        column_pairs = [
            (ITEM_PRODUCT_GROUPL_COLUMN, SOP_FROZEN_GRP_SET_PROD_GRP_COLUMN),
            (ITEM_SCM_TYPE_COLUMN, SOP_FROZEN_GRP_SET_SCM_TYPE_COLUMN),
            (ITEM_PRODUCT_COLUMN, SOP_FROZEN_GRP_SET_PRODUCT_COLUMN),
            (ITEM_A2_COLUMN, SOP_FROZEN_GRP_SET_INCH_COLUMN),
            (ITEM_A9_COLUMN, SOP_FROZEN_GRP_SET_DEFINITION_COLUMN),
            (ITEM_A11_COLUMN, SOP_FROZEN_GRP_SET_YEAR_COLUMN),
            (ITEM_A14_COLUMN, SOP_FROZEN_GRP_SET_MKT_NAME_COLUMN)
        ]

        #       모든 조건을 리스트 컴프리헨션으로 생성
        conditions = [
            (df_SOPFrozenGrpSET[item_col] == decode(
                df_SOPFrozenGrpSET[sop_col].str.upper(), ALL_VALUE,
                df_SOPFrozenGrpSET[item_col],
                df_SOPFrozenGrpSET[sop_col]
            ))
            for item_col, sop_col in column_pairs
        ]

        #       모든 조건을 & 연산자로 결합
        final_mask = np.logical_and.reduce(conditions)

        #       필터링 적용
        df_SOPFrozenGrpSET = df_SOPFrozenGrpSET[final_mask]
        print_df(df_SOPFrozenGrpSET, 'STEP3 by 2.1.2 ____ df_SOPFrozenGrpSET .... filter')

        df_SOPFrozenGrpSET.rename(columns={
            SOP_FROZEN_GRP_SET_TO_SITE_COLUMN : SUB_LOCATION_COLUMN,
            SOP_FROZEN_GRP_SET_CTG_COLUMN: SOP_FROZEN_LIST_CTG_COLUMN,
            SOP_FROZEN_GRP_SET_FRZ_COLUMN: SOP_FROZEN_LIST_GRP_FRZ_COLUMN,
            SOP_FROZEN_GRP_SET_FRZ_ENDDATE_COLUMN: SOP_FROZEN_LIST_GRP_FRZ_ENDDATE_COLUMN,
            SOP_FROZEN_GRP_SET_FRZ_STARTDATE_COLUMN: SOP_FROZEN_LIST_GRP_FRZ_STARTDATE_COLUMN,
            SOP_FROZEN_GRP_SET_TOTAL_FLAG_COLUMN: SOP_FROZEN_LIST_GRP_PERIOD_TOTAL_COLUMN,
            SOP_FROZEN_GRP_SET_DIGIT_COLUMN: SOP_FROZEN_LIST_DIGIT_COLUMN,
            SOP_FROZEN_PERIOD_SMRY_COPY_COLUMN: SOP_FROZEN_LIST_FP_PERIOD_COLUMN,
        }, inplace=True)

        #   2.1.3 원하는 컬럼만 선택
        df_SOPFrozenGrpSET = df_SOPFrozenGrpSET[df_SopFrozenList_columns].drop_duplicates()
        print_df(df_SOPFrozenGrpSET, 'STEP3 by 2.1.3 ____ df_SOPFrozenGrpSET .... final')

        # ====================> STEP3 by 2 (End)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_out_SopFrozenList = pd.concat([df_SOPFrozen, df_SOPFrozenGrpSET])
        df_out_SopFrozenList[VERSION_NAME_COLUMN] = paramOutVersion

        str_columns = [SOP_FROZEN_LIST_FRZ_ENDDATE_COLUMN, SOP_FROZEN_LIST_FRZ_STARTDATE_COLUMN,
                       SOP_FROZEN_LIST_GRP_FRZ_ENDDATE_COLUMN, SOP_FROZEN_LIST_GRP_FRZ_STARTDATE_COLUMN,
                       SOP_FROZEN_LIST_GRP_PERIOD_TOTAL_COLUMN,]
        for column in str_columns:
            df_out_SopFrozenList[column] = df_out_SopFrozenList[column].astype(str)
            df_out_SopFrozenList[column] = df_out_SopFrozenList[column].str.replace(r'\.0$', '', regex=True)
            df_out_SopFrozenList[column] = df_out_SopFrozenList[column].replace({pd.NA: None, np.nan: None, '<NA>': None, 'nan': None})


        int_columns = [SOP_FROZEN_LIST_GRP_FRZ_COLUMN]
        for column in int_columns:
            df_out_SopFrozenList[column] = df_out_SopFrozenList[column].astype('Int64')
            df_out_SopFrozenList[column] = df_out_SopFrozenList[column].replace({
                pd.NA: None, np.nan: None, '<NA>': None, 'nan': None, np.inf: None, -np.inf: None, 'inf': None, '-inf': None
            })

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
        
        print_df(df_out_SopFrozenList, 'output table create .... df_out_SopFrozenList', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SopFrozenList = pd.DataFrame(columns=df_SopFrozenList_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SopFrozenList = pd.DataFrame(columns=df_SopFrozenList_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
