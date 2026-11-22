"""
* 프로그램명
    - PY_UI_BODItem_NewAlt

* 내용
    - 신규 추가 BOD From,To Site,TP,PG의 모든 Item생성 생성을 위한 Program (Set BOD Altanative UI에서 Save시 호출)

* 변경이력
    - 2025.10.22 / 권태우 / Create
    - 2026.03.03 / 이상엽 / STEP1~4 수정
        InputTable Namedset 변경 : &MFlocation → &MFStageSETLocation
        STEP 5,6 BOD Item_PyRunFlag 값 추가

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek     : Select (&CurrentWeek);
    - df_in_AllWeek      : Select (Time.[Day] * Time.[Day of Week] * [Time].[Week]);
    - df_in_BODList      : Select (&MFStageSETLocation * &SubLocationDC * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Shipment LT] }) on column where {[Version].[Version Name], Measure.[BOD List_BOD Valid] == "Y"};
    - df_in_BODListMF    : Select (&MFStageSETLocation * &SubLocationMF * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Shipment LT] }) on column where {[Version].[Version Name], Measure.[BOD List_BOD Valid] == "Y"};
    - df_in_BODListDC    : Select (&DClocation * &SubLocationDC * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Shipment LT] }) on column where {[Version].[Version Name], Measure.[BOD List_BOD Valid] == "Y"};
    - df_in_BODProdSET   : Select ([Item].[Product Group] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Prod SET_BOD Name], Measure.[BOD Prod SET_BOD Valid], Measure.[BOD Prod SET_Time Phased Prty], Measure.[BOD Prod SET_Time Phased BOD LT],  Measure.[BOD Prod SET_Priority], Measure.[BOD Prod SET_Time Phased Shipment LT]}) on column where {[Version].[Version Name]};
    - df_in_ItemSiteAsn1 : Select ([Item].[Item] * [Item].[Product Group] * [Item].[Product] * &ProductTypeList * &FinishedGoods * &MFStageSETLocation) on row, ({Measure.[Item Site Asn_Cur Status]}) on column where {[Version].[Version Name], Measure.[Item Site Asn_Cur Status] in {"PLANNED","ACTIVE"}};
    - df_in_ItemSiteAsn2 : Select ([Item].[Item] * [Item].[Product Group] * [Item].[Product] * &ProductTypeList * &FinishedGoods * &DClocation) on row, ({Measure.[Item Site Asn_Sales Prod Flag]}) on column where {[Version].[Version Name], Measure.[Item Site Asn_Sales Prod Flag] in {True}};
    - df_in_BODItem      : Select ([Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_Asn], Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Update Time], Measure.[BOD Item_Updated By], Measure.[BOD Item_Created By], Measure.[BOD Item_Creation Time]}) on column where {[Version].[Version Name]};
    - df_in_LoadMstToSite: Select ([Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Loading Master To Site_Minimum Lot], Measure.[Loading Master To Site_Multiple Lot], Measure.[Loading Master To Site_Valid]}) on column where {[Version].[Version Name], Measure.[Loading Master To Site_Valid] == "Y"};

* Flow Summary
    - STEP1. df_in_BODList,  BOD Prod Set, Item Site Asn1, Item Site Asn2 조합하여 BOD Item1 생성
    - STEP2. df_in_BODListMF, BOD Prod Set, Item Site Asn1 조합하여 BOD Item2 생성
    - STEP3. df_in_BODListDC, BOD Prod Set, Item Site Asn2 조합하여 BOD Item3 생성
    - STEP4. BOD Item1, BOD Item2, BOD Item3 Concat하여 BOD Item 데이터 셋 구성
    - STEP5. Step4와 df_in_BODItem 비교하여 BOD Item에 이미 존재한 데이터 기준 Measure Update
    - STEP6. Step4와 df_in_BODItem 비교하여 BOD Item에 없는 데이터 신규 생성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BODItem

* 데이타 초기화
    - DELETE DATA FOR MODEL [BOD Item] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_BODItem_NewAlt] for measures {[BOD Item_BOD LT]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT],  Measure.[BOD Item_Cur Status], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Endweek], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Eff Startweek], Measure.[BOD Item_Priority],  Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Time Phased Prty], Measure.[BOD Item_Asn]}) on column limit 100;
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
str_instance = 'PY_UI_BODItem_NewAlt'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = (
    "CWV_MP"
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
    try:
        file_path = f"{file_name}.csv"
        if not os.path.exists(file_path):
            step(f"=====> 파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame()  # 빈 DataFrame 반환
        return pd.read_csv(file_path, low_memory=False, encoding="UTF-8")

    except Exception as e:
        step(f"=====> CSV 파일 읽기 실패: {file_name}, 오류: {str(e)}")
        return pd.DataFrame()  # 에러 발생시 빈 DataFrame 반환


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


def vd_log_end() -> tuple:
    """
    로그 처리를 종료하고 로그 데이터프레임들을 반환하는 공통 함수

    Returns:
        tuple: (df_out_log, df_out_logDetail) 형태의 튜플
    """
    try:
        # 로그 종료 처리
        vdCommon.gfn_pyLog_end()

        # 로그 데이터프레임 가져오기
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()

        return df_out_log, df_out_logDetail

    except Exception as e:
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(df):
    """데이터프레임 최적화 및 메모리 사용량 감소"""
    if df is None:
        return None

    # 데이터프레임 복사 및 메모리 최적화
    result = df.copy()

    # 숫자형 컬럼의 데이터 타입 최적화
    for col in result.select_dtypes(include=['int', 'float']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')

    # # 범주형 데이터 최적화
    # for col in result.select_dtypes(include=['object']).columns:
    #     if result[col].nunique() / len(result) < 0.5:  # 고유값이 50% 미만일 경우
    #         result[col] = result[col].astype('category')

    delete_dfs(df)
    return result


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
    """실행 시간을 계산하고, 분 또는 초 단위로 반환.
    초 단위가 0일 경우 초로 표시하고, 그 외에는 분으로 표시."""
    elapsed = time.time() - start_time
    if elapsed < 60:  # 1분 미만일 경우
        return str(round(elapsed, 2)) + " seconds"
    else:
        return str(round(elapsed / 60, 2)) + " minutes"


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


def get_current_date_str(tz: str | None = None) -> str:
    """
    현재 시각을 'YYYY-MM-DD HH:MM:SS' 형식 문자열로 반환.
    tz 인자로 'UTC' (대소문자 무관)를 주면 UTC 기준, 그 외에는 로컬 타임존 기준.
    """
    if isinstance(tz, str) and tz.upper() == "UTC":
        now = datetime.datetime.now(datetime.timezone.utc)
    else:
        # now = datetime.datetime.now().astimezone()
        now = datetime.datetime.now()

    return now.strftime("%Y-%m-%d %H:%M:%S")


def ultra_fast_replace_to_none(df):
    """NumPy 기반 초고속 변환"""
    df = df.copy()

    # object 컬럼과 숫자 컬럼 분리
    obj_cols = df.select_dtypes(include=['object']).columns
    num_cols = df.select_dtypes(include=['number']).columns

    # 문자열 컬럼 일괄 처리
    if len(obj_cols) > 0:
        obj_data = df[obj_cols].values
        # 조건 마스크 생성
        mask = (
            (obj_data == 'nan') |
            (obj_data == '<NA>') |
            (obj_data == '0') |
            pd.isna(obj_data)
        )
        obj_data[mask] = None
        df[obj_cols] = obj_data

    # 숫자 컬럼: NaN → None (object 변환 필요)
    for col in num_cols:
        if df[col].isna().any():
            df[col] = df[col].astype(object).where(df[col].notna(), None)

    return df


########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    # Batch 시작
    vd_log_start()
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
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_BODList = read_csv_file("df_in_BODList")
            df_in_BODListMF = read_csv_file("df_in_BODListMF")
            df_in_BODListDC = read_csv_file("df_in_BODListDC")
            df_in_BODProdSET = read_csv_file("df_in_BODProdSET")
            df_in_ItemSiteAsn1 = read_csv_file("df_in_ItemSiteAsn1")
            df_in_ItemSiteAsn2 = read_csv_file("df_in_ItemSiteAsn2")
            df_in_BODItem = read_csv_file("df_in_BODItem")
            df_in_LoadMstToSite = read_csv_file("df_in_LoadMstToSite")


        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_BODList': df_in_BODList,
            'df_in_BODListMF': df_in_BODListMF,
            'df_in_BODListDC': df_in_BODListDC,
            'df_in_BODProdSET': df_in_BODProdSET,
            'df_in_ItemSiteAsn1': df_in_ItemSiteAsn1,
            'df_in_ItemSiteAsn2': df_in_ItemSiteAsn2,
            'df_in_BODItem': df_in_BODItem,
            'df_in_LoadMstToSite': df_in_LoadMstToSite,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_DAY_KEY_COLUMN = 'Time.[DayKey]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAY_WEEK_COLUMN = 'Time.[Day of Week]'
        TIME_DAY_COLUMN = 'Time.[Day]'

        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_COLUMN = 'Item.[Product]'
        ITEM_PRODUCT_TYPE_COLUMN = 'Item.[ProductType]'
        ITEM_TYPE_COLUMN = 'Item.[Item Type]'
        ITEM_SITE_ASN_CUR_STATUS_COLUMN = 'Item Site Asn_Cur Status'

        BOD_LIST_BOD_FROZEN_COLUMN = 'BOD List_BOD Frozen'
        BOD_LIST_BOD_LT_COLUMN = 'BOD List_BOD LT'
        BOD_LIST_BOD_VAILD_COLUMN = 'BOD List_BOD Valid'
        BOD_LIST_EFF_ENDDATE_COLUMN = 'BOD List_Eff Enddate'
        BOD_LIST_EFF_STARTDATE_COLUMN = 'BOD List_Eff Startdate'
        BOD_LIST_SHIPMENT_LT_COLUMN = 'BOD List_Shipment LT'

        BOD_PROD_SET_BOD_NAME_COLUMN = 'BOD Prod SET_BOD Name'
        BOD_PROD_SET_BOD_VAILD_COLUMN = 'BOD Prod SET_BOD Valid'
        BOD_PROD_SET_TIME_PHASED_PRTY_COLUMN = 'BOD Prod SET_Time Phased Prty'
        BOD_PROD_SET_TIME_PHASED_BOD_LT_COLUMN = 'BOD Prod SET_Time Phased BOD LT'
        BOD_PROD_SET_PRIORITY_COLUMN = 'BOD Prod SET_Priority'
        BOD_PROD_SET_TIME_PHASED_SHIPMENT_LT_COLUMN = 'BOD Prod SET_Time Phased Shipment LT'

        LOADING_MST_TO_SITE_MIN_LOT_COLUMN = 'Loading Master To Site_Minimum Lot'
        LOADING_MST_TO_SITE_MULTI_LOT_COLUMN = 'Loading Master To Site_Multiple Lot'

        BOD_ITEM_LOCK_FLAG_COLUMN = 'BOD Item_Lock Flag'
        BOD_ITEM_BOD_FROZEN_COLUMN = 'BOD Item_BOD Frozen'
        BOD_ITEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
        BOD_ITEM_CUR_STATUS_COLUMN = 'BOD Item_Cur Status'
        BOD_ITEM_EFF_ENDDATE_COLUMN = 'BOD Item_Eff Enddate'
        BOD_ITEM_EFF_ENDWEEK_COLUMN = 'BOD Item_Eff Endweek'
        BOD_ITEM_EFF_STARTDATE_COLUMN = 'BOD Item_Eff Startdate'
        BOD_ITEM_EFF_STARTWEEK_COLUMN = 'BOD Item_Eff Startweek'
        BOD_ITEM_PRIORITY_COLUMN = 'BOD Item_Priority'
        BOD_ITEM_SHIPMENT_LT_COLUMN = 'BOD Item_Shipment LT'
        BOD_ITEM_ASN_COLUMN = 'BOD Item_Asn'
        BOD_ITEM_BOD_VAILD_COLUMN = 'BOD Item_BOD Valid'
        BOD_ITEM_TIME_PHASED_PRTY_COLUMN = 'BOD Item_Time Phased Prty'
        BOD_ITEM_TIME_PHASED_BOD_LT_COLUMN = 'BOD Item_Time Phased BOD LT'
        BOD_ITEM_TIME_PHASED_SHIPMENT_LT_COLUM = 'BOD Item_Time Phased Shipment LT'
        BOD_ITEM_TIME_PHASED_BOD_COLUMN = 'BOD Item_Time Phased BOD'
        BOD_ITEM_TIME_PHASED_SHIPMENT_COLUM = 'BOD Item_Time Phased Shipment'
        BOD_ITEM_BOD_NAME_COLUM = 'BOD Item_BOD Name'
        BOD_ITEM_UPDATED_BY_COLUMN = 'BOD Item_Updated By'
        BOD_ITEM_UPDATE_TIME_COLUMN = 'BOD Item_Update Time'
        BOD_ITEM_CREATED_BY_COLUMN = 'BOD Item_Created By'
        BOD_ITEM_CREATE_TIME_COLUMN = 'BOD Item_Creation Time'
        BOD_ITEM_PYRUNFLAG_COLUMN = 'BOD Item_PyRunFlag'

        BOD_ITEM_MULTI_LOT_QTY_COLUMN = 'BOD Item_Multi Lot Qty'
        BOD_ITEM_MIN_LOT_QTY_COLUMN = 'BOD Item_Min Lot Qty'

        version_columns = [VERSION_NAME_COLUMN]

        bod_prod_set_columns = [
            LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, ITEM_SITE_ASN_CUR_STATUS_COLUMN,
            BOD_PROD_SET_BOD_NAME_COLUMN, BOD_PROD_SET_BOD_VAILD_COLUMN,
            BOD_PROD_SET_TIME_PHASED_PRTY_COLUMN, BOD_PROD_SET_TIME_PHASED_BOD_LT_COLUMN,
            BOD_PROD_SET_PRIORITY_COLUMN, BOD_PROD_SET_TIME_PHASED_SHIPMENT_LT_COLUMN,
        ]

        bod_item_columns = [
            ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_ASN_COLUMN, BOD_ITEM_LOCK_FLAG_COLUMN,
            BOD_ITEM_BOD_LT_COLUMN, BOD_ITEM_SHIPMENT_LT_COLUMN, BOD_ITEM_EFF_ENDDATE_COLUMN, BOD_ITEM_EFF_ENDWEEK_COLUMN,
            BOD_ITEM_EFF_STARTDATE_COLUMN, BOD_ITEM_EFF_STARTWEEK_COLUMN, BOD_ITEM_PRIORITY_COLUMN,
            BOD_ITEM_BOD_VAILD_COLUMN, BOD_ITEM_TIME_PHASED_PRTY_COLUMN, BOD_ITEM_TIME_PHASED_BOD_COLUMN,
            BOD_ITEM_TIME_PHASED_SHIPMENT_COLUM, BOD_ITEM_CUR_STATUS_COLUMN,
            BOD_ITEM_BOD_NAME_COLUM, BOD_ITEM_MULTI_LOT_QTY_COLUMN, BOD_ITEM_MIN_LOT_QTY_COLUMN,
            BOD_ITEM_UPDATED_BY_COLUMN, BOD_ITEM_UPDATE_TIME_COLUMN,
            BOD_ITEM_CREATED_BY_COLUMN, BOD_ITEM_CREATE_TIME_COLUMN,
            BOD_ITEM_PYRUNFLAG_COLUMN,
        ]

        bod_item_final_columns = version_columns + bod_item_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[LOCATION_COLUMN] == 'P306']
        # print_df(df_in_BODProdSET, 'STEP3 by 1.1  ____ df_in_BODProdSET .... filter', True)
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[SUB_LOCATION_COLUMN] == 'L5N0']

        # df_in_ItemSiteAsn1 = df_in_ItemSiteAsn1[df_in_ItemSiteAsn1[ITEM_COLUMN] == 'QA50QN90FAJXZK']
        # print_df(df_in_ItemSiteAsn1, 'STEP3 by 1.1  ____ df_in_ItemSiteAsn1 .... filter', True)
        # df_in_ItemSiteAsn1 = df_in_ItemSiteAsn1[df_in_ItemSiteAsn1[LOCATION_COLUMN] == 'P306']

        # df_in_ItemSiteAsn2 = df_in_ItemSiteAsn2[df_in_ItemSiteAsn2[ITEM_COLUMN] == 'QA50QN90FAJXZK']
        # print_df(df_in_ItemSiteAsn2, 'STEP3 by 1.1  ____ df_in_ItemSiteAsn2 .... filter', True)
        # df_in_ItemSiteAsn2 = df_in_ItemSiteAsn2[df_in_ItemSiteAsn2[LOCATION_COLUMN] == 'L5N0']

        # df_in_BODItem = df_in_BODItem[df_in_BODItem[ITEM_COLUMN] == 'QA50QN90FAJXZK']
        # df_in_BODList = df_in_BODList[df_in_BODList[TRANS_MODE_COLUMN] == 'EXPRESS']
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_BODProdSET.empty:
            raise CustomException("STEP3 by 0 ____ df_in_BODProdSET  값이 없습니다.")


        # 현재 주차 가져오기
        current_week = get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN)
        step(f'=====> current_week : {current_week}')

        # 현재 날짜 시간
        # current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # current_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        current_date = get_current_date_str('UTC')
        step(f'=====> current_date : {current_date}')




        # df_in_AllWeek 필요컬럼 설정
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN, TIME_DAY_COLUMN]].drop_duplicates()
        df_in_AllWeek[TIME_DAY_COLUMN] = df_in_AllWeek[TIME_DAY_COLUMN].astype(str)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1-1 Start : df_in_BODList,  BOD Prod Set, Item Site Asn1 조합한 데이터 셋 생성')
        df_step1_1 = pd.merge(
            df_in_BODList, df_in_BODProdSET, how='inner',
            left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
            right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
        )
        print_df(df_step1_1, 'STEP4 by 1-1.1  ____ df_step1_1 .... merge[df_in_BODProdSET]')

        df_step1_1 = df_step1_1.merge(
            df_in_ItemSiteAsn1, how='inner',
            left_on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
        )
        print_df(df_step1_1, 'STEP4 by 1-1.2  ____ df_step1_1 .... merge[df_in_ItemSiteAsn1]')
        step('=====> STEP4 by 1-1 End')



        step('=====> STEP4 by 1-2 Start : STEP 1-1과 Item Site Asn2 조합하여 BOD Item1 생성 (Inner Join)')
        df_step1_2 = pd.merge(
            df_step1_1, df_in_ItemSiteAsn2, how='inner',
            left_on=[SUB_LOCATION_COLUMN, ITEM_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_COLUMN],
        )
        print_df(df_step1_2, 'STEP4 by 1-2.1  ____ df_step1_2 .... merge[df_in_ItemSiteAsn2]')

        df_step1_2.rename(columns={
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            ITEM_PRODUCT_GROUP_COLUMN+'_x': ITEM_PRODUCT_GROUP_COLUMN,
            ITEM_PRODUCT_COLUMN+'_x': ITEM_PRODUCT_COLUMN,
            ITEM_TYPE_COLUMN+'_x': ITEM_TYPE_COLUMN,
            ITEM_PRODUCT_TYPE_COLUMN+'_x': ITEM_PRODUCT_TYPE_COLUMN,
        }, inplace=True)
        print_df(df_step1_2, 'STEP4 by 1-2.2  ____ df_step1_2 .... rename')
        step('=====> STEP4 by 1-2 End')



        step('=====> STEP4 by 2-1 Start : df_in_BODListMF,  BOD Prod Set, Item Site Asn1 조합한 데이터 셋 생성')
        df_step2_1 = pd.merge(
            df_in_BODListMF, df_in_BODProdSET, how='inner',
            left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
            right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
        )

        df_step2_1 = df_step2_1.merge(
            df_in_ItemSiteAsn1, how='inner',
            left_on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
        )
        print_df(df_step2_1, 'STEP4 by 2-1.1  ____ df_step2_1 .... merge[df_in_BODListMF]')
        step('=====> STEP4 by 2-1 End')




        step('=====> STEP4 by 2-2 Start : STEP 2-1과 Item Site Asn1 조합하여 BOD Item2 생성 (Inner Join)')
        df_step2_2 = df_step2_1.merge(
            df_in_ItemSiteAsn1, how='inner',
            left_on=[SUB_LOCATION_COLUMN, ITEM_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_COLUMN],
        )
        print_df(df_step2_2, 'STEP4 by 2-2.1  ____ df_step2_2 .... merge[df_in_ItemSiteAsn1]')

        df_step2_2.rename(columns={
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            ITEM_PRODUCT_GROUP_COLUMN+'_x': ITEM_PRODUCT_GROUP_COLUMN,
            ITEM_PRODUCT_COLUMN+'_x': ITEM_PRODUCT_COLUMN,
            ITEM_TYPE_COLUMN+'_x': ITEM_TYPE_COLUMN,
            ITEM_PRODUCT_TYPE_COLUMN+'_x': ITEM_PRODUCT_TYPE_COLUMN,
            ITEM_SITE_ASN_CUR_STATUS_COLUMN+'_x': ITEM_SITE_ASN_CUR_STATUS_COLUMN,
        }, inplace=True)
        print_df(df_step2_2, 'STEP4 by 2-2.2  ____ df_step2_2 .... rename')
        step('=====> STEP4 by 2-2 End')




        step('=====> STEP4 by 3-1 Start : df_in_BODListDC,  BOD Prod Set, Item Site Asn2 조합한 데이터 셋 생성')
        df_step3_1 = pd.merge(
            df_in_BODListDC, df_in_BODProdSET, how='inner',
            left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
            right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
        )
        print_df(df_step3_1, 'STEP4 by 3-1.1  ____ df_step3_1 .... merge[df_in_BODProdSET]')

        df_step3_1 = df_step3_1.merge(
            df_in_ItemSiteAsn2, how='inner',
            left_on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
        )
        print_df(df_step3_1, 'STEP4 by 3-1.2  ____ df_step3_1 .... merge[df_in_ItemSiteAsn2]')
        step('=====> STEP4 by 3-1 End')



        step('=====> STEP4 by 3-2 Start : STEP 3-1과 Item Site Asn2 조합하여 BOD Item3 생성 (Inner Join)')
        df_step3_2 = df_step3_1.merge(
            df_in_ItemSiteAsn2, how='inner',
            left_on=[SUB_LOCATION_COLUMN, ITEM_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_COLUMN],
        )
        print_df(df_step3_2, 'STEP4 by 3-2.1  ____ df_step3_2 .... merge[df_in_ItemSiteAsn2]')

        df_step3_2.rename(columns={
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            ITEM_PRODUCT_GROUP_COLUMN+'_x': ITEM_PRODUCT_GROUP_COLUMN,
            ITEM_PRODUCT_COLUMN+'_x': ITEM_PRODUCT_COLUMN,
            ITEM_TYPE_COLUMN+'_x': ITEM_TYPE_COLUMN,
            ITEM_PRODUCT_TYPE_COLUMN+'_x': ITEM_PRODUCT_TYPE_COLUMN,
        }, inplace=True)
        print_df(df_step3_2, 'STEP4 by 3-2.2  ____ df_step3_2 .... rename')
        step('=====> STEP4 by 3-2 End')




        step('=====> STEP4 by 4.0 Start : Step1, 2, 3 BOD Item1, BOD Item2, BOD Item3 Concat하여 BOD Item 데이터 셋 구성 및 df_in_LoadMstToSite merge(Left Join)')
        df_BODListConcat = pd.concat([df_step1_2, df_step2_2, df_step3_2], ignore_index=True).drop_duplicates()
        print_df(df_BODListConcat, 'STEP4 by 4.0.1  ____ df_BODListConcat .... df concat')

        # (Join 조건 = Location, Sub Location, Item, TP Mode)
        df_BODListConcat = pd.merge(df_BODListConcat, df_in_LoadMstToSite, how='left', on=[ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_BODListConcat, 'STEP4 by 4.0.2  ____ df_BODListConcat .... recreate')

        # 주차 컬럼 생성
        #   날짜 형식 지정 (명확하게 정의)
        formats = [
            '%m/%d/%Y %I:%M:%S %p',  # 11/24/2024 12:00:00 AM
            '%Y-%m-%d %H:%M:%S'  # 2024-11-24 00:00:00
        ]

        def parse_dates(column):
            parsed_dates_1 = pd.to_datetime(df_BODListConcat[column], format=formats[0], errors='coerce')
            parsed_dates_2 = pd.to_datetime(df_BODListConcat[column], format=formats[1], errors='coerce')
            return parsed_dates_1.fillna(parsed_dates_2).dt.date

        df_BODListConcat['EFF_ENDDATE'] = parse_dates(BOD_LIST_EFF_ENDDATE_COLUMN)
        df_BODListConcat['EFF_ENDDATE'] = df_BODListConcat['EFF_ENDDATE'].astype(str)

        df_BODListConcat['EFF_STARTDATE'] = parse_dates(BOD_LIST_EFF_STARTDATE_COLUMN)
        df_BODListConcat['EFF_STARTDATE'] = df_BODListConcat['EFF_STARTDATE'].astype(str)
        print_df(df_BODListConcat, 'STEP4 by 4.0.3  ____ df_BODListConcat .... effdate add]')

        df_BODListConcat = pd.merge(df_BODListConcat, df_in_AllWeek, how='left',
                                    left_on=['EFF_ENDDATE'], right_on=[TIME_DAY_COLUMN])
        df_BODListConcat.rename(columns={TIME_WEEK_COLUMN: 'EFF_ENDWEEK'}, inplace=True)
        df_BODListConcat.drop(columns=[TIME_DAY_COLUMN, 'EFF_ENDDATE'], inplace=True)
        df_BODListConcat['EFF_ENDWEEK'] = df_BODListConcat['EFF_ENDWEEK'].astype(str).replace(r'\.0$', '', regex=True)
        print_df(df_BODListConcat, 'STEP4 by 4.0.4  ____ df_BODListConcat .... enddate week add]')

        df_BODListConcat = pd.merge(df_BODListConcat, df_in_AllWeek, how='left',
                                    left_on=['EFF_STARTDATE'], right_on=[TIME_DAY_COLUMN])
        df_BODListConcat.rename(columns={TIME_WEEK_COLUMN: 'EFF_STARTWEEK'}, inplace=True)
        df_BODListConcat.drop(columns=[TIME_DAY_COLUMN, 'EFF_STARTDATE'], inplace=True)
        df_BODListConcat['EFF_STARTWEEK'] = df_BODListConcat['EFF_STARTWEEK'].astype(str).replace(r'\.0$', '', regex=True)
        print_df(df_BODListConcat, 'STEP4 by 4.0.5  ____ df_BODListConcat .... startdate week add]')

        df_BODListConcat.drop_duplicates()
        print_df(df_BODListConcat, 'STEP4 by 4.0.6  ____ df_BODListConcat .... final')
        step('=====> STEP4 by 4.0 End')




        step('=====> STEP4 by 5 Start : Step4와 BOD Item 목록 비교하여 이미 BOD Item 에 있으며, BOD Item_Lock Flag  == "N" or null 일때,  아래와 같이 Measure Update')
        df_BODItem1 = pd.merge(df_BODListConcat, df_in_BODItem, how='inner',
                               left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN],
                               right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN])
        df_BODItem1 = df_BODItem1[(df_BODItem1[BOD_ITEM_LOCK_FLAG_COLUMN] == "N") | (df_BODItem1[BOD_ITEM_LOCK_FLAG_COLUMN].isnull())]
        print_df(df_BODItem1, 'STEP4 by 5.1  ____ df_BODItem1 .... merge[df_in_BODItem]')

        if not df_BODItem1.empty:
            df_BODItem1[BOD_ITEM_BOD_LT_COLUMN] = df_BODItem1[BOD_LIST_BOD_LT_COLUMN]
            df_BODItem1[BOD_ITEM_SHIPMENT_LT_COLUMN] = df_BODItem1[BOD_LIST_SHIPMENT_LT_COLUMN]

            # 'BOD Prod SET_BOD Valid' 가 'N'인 경우 당일/당주 사용
            valid_condition = df_BODItem1[BOD_PROD_SET_BOD_VAILD_COLUMN] == 'N'
            df_BODItem1[BOD_ITEM_EFF_ENDDATE_COLUMN] = df_BODItem1[BOD_LIST_EFF_ENDDATE_COLUMN].mask(
                valid_condition, current_date
            )

            df_BODItem1[BOD_ITEM_EFF_ENDWEEK_COLUMN] = df_BODItem1['EFF_ENDWEEK'].mask(
                valid_condition, current_week
            )

            df_BODItem1[BOD_ITEM_EFF_STARTDATE_COLUMN] = df_BODItem1[BOD_LIST_EFF_STARTDATE_COLUMN]
            df_BODItem1[BOD_ITEM_EFF_STARTWEEK_COLUMN] = df_BODItem1['EFF_STARTWEEK']
            df_BODItem1[BOD_ITEM_PRIORITY_COLUMN] = df_BODItem1[BOD_PROD_SET_PRIORITY_COLUMN]
            df_BODItem1[BOD_ITEM_BOD_VAILD_COLUMN] = df_BODItem1[BOD_PROD_SET_BOD_VAILD_COLUMN]
            df_BODItem1[BOD_ITEM_TIME_PHASED_PRTY_COLUMN] = df_BODItem1[BOD_PROD_SET_TIME_PHASED_PRTY_COLUMN]
            df_BODItem1[BOD_ITEM_TIME_PHASED_BOD_COLUMN] = df_BODItem1[BOD_PROD_SET_TIME_PHASED_BOD_LT_COLUMN]
            df_BODItem1[BOD_ITEM_TIME_PHASED_SHIPMENT_COLUM] = df_BODItem1[BOD_PROD_SET_TIME_PHASED_SHIPMENT_LT_COLUMN]
            df_BODItem1[BOD_ITEM_BOD_NAME_COLUM] = df_BODItem1[BOD_PROD_SET_BOD_NAME_COLUMN]
            df_BODItem1[BOD_ITEM_CUR_STATUS_COLUMN] = df_BODItem1[ITEM_SITE_ASN_CUR_STATUS_COLUMN]
            df_BODItem1[BOD_ITEM_UPDATED_BY_COLUMN] = 'PY_UI_BODItem_NewAlt'
            df_BODItem1[BOD_ITEM_UPDATE_TIME_COLUMN] = current_date

            df_BODItem1[BOD_ITEM_MULTI_LOT_QTY_COLUMN] = np.where(
                df_BODItem1[LOADING_MST_TO_SITE_MULTI_LOT_COLUMN].notna(),
                df_BODItem1[LOADING_MST_TO_SITE_MULTI_LOT_COLUMN],
                "1"
            )

            df_BODItem1[BOD_ITEM_MIN_LOT_QTY_COLUMN] = np.where(
                df_BODItem1[LOADING_MST_TO_SITE_MIN_LOT_COLUMN].notna(),
                df_BODItem1[LOADING_MST_TO_SITE_MIN_LOT_COLUMN],
                "1"
            )

            df_BODItem1[BOD_ITEM_PYRUNFLAG_COLUMN] = 1
        else:
            df_BODItem1 = pd.DataFrame(columns=bod_item_columns)

        df_BODItem1 = df_BODItem1[bod_item_columns]
        print_df(df_BODItem1, 'STEP4 by 5.2  ____ df_BODItem1 .... create')
        step('=====> STEP4 by 5 End')




        step('=====> STEP4 by 6 Start : Step4와 BOD Item 목록 비교하여 이미 BOD Item 에 없으면 신규 생성')
        df_BODItem2 = pd.merge(df_BODListConcat, df_in_BODItem, how='left', indicator=True,
                               left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN],
                               right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN])
        df_BODItem2 = df_BODItem2[df_BODItem2['_merge'] == 'left_only'].drop('_merge', axis=1)
        print_df(df_BODItem2, 'STEP4 by 6.1  ____ df_BODItem2 .... merge[df_in_BODItem]')

        if not df_BODItem2.empty:
            df_BODItem2[BOD_ITEM_ASN_COLUMN] = 1
            df_BODItem2[BOD_ITEM_LOCK_FLAG_COLUMN] = 'N'
            df_BODItem2[BOD_ITEM_BOD_LT_COLUMN] = df_BODItem2[BOD_LIST_BOD_LT_COLUMN]
            df_BODItem2[BOD_ITEM_SHIPMENT_LT_COLUMN] = df_BODItem2[BOD_LIST_SHIPMENT_LT_COLUMN]
            df_BODItem2[BOD_ITEM_EFF_ENDDATE_COLUMN] = df_BODItem2[BOD_LIST_EFF_ENDDATE_COLUMN]
            df_BODItem2[BOD_ITEM_EFF_ENDWEEK_COLUMN] = df_BODItem2['EFF_ENDWEEK']
            df_BODItem2[BOD_ITEM_EFF_STARTDATE_COLUMN] = df_BODItem2[BOD_LIST_EFF_STARTDATE_COLUMN]
            df_BODItem2[BOD_ITEM_EFF_STARTWEEK_COLUMN] = df_BODItem2['EFF_STARTWEEK']
            df_BODItem2[BOD_ITEM_PRIORITY_COLUMN] = df_BODItem2[BOD_PROD_SET_PRIORITY_COLUMN]
            df_BODItem2[BOD_ITEM_BOD_VAILD_COLUMN] = df_BODItem2[BOD_PROD_SET_BOD_VAILD_COLUMN]
            df_BODItem2[BOD_ITEM_TIME_PHASED_PRTY_COLUMN] = df_BODItem2[BOD_PROD_SET_TIME_PHASED_PRTY_COLUMN]
            df_BODItem2[BOD_ITEM_TIME_PHASED_BOD_COLUMN] = df_BODItem2[BOD_PROD_SET_TIME_PHASED_BOD_LT_COLUMN]
            df_BODItem2[BOD_ITEM_TIME_PHASED_SHIPMENT_COLUM] = df_BODItem2[BOD_PROD_SET_TIME_PHASED_SHIPMENT_LT_COLUMN]
            df_BODItem2[BOD_ITEM_BOD_NAME_COLUM] = df_BODItem2[BOD_PROD_SET_BOD_NAME_COLUMN]
            df_BODItem2[BOD_ITEM_CUR_STATUS_COLUMN] = df_BODItem2[ITEM_SITE_ASN_CUR_STATUS_COLUMN]
            df_BODItem2[BOD_ITEM_CREATED_BY_COLUMN] = 'PY_UI_BODItem_NewAlt'
            df_BODItem2[BOD_ITEM_CREATE_TIME_COLUMN] = current_date

            df_BODItem2[BOD_ITEM_MULTI_LOT_QTY_COLUMN] = np.where(
                df_BODItem2[LOADING_MST_TO_SITE_MULTI_LOT_COLUMN].notna(),
                df_BODItem2[LOADING_MST_TO_SITE_MULTI_LOT_COLUMN],
                "1"
            )

            df_BODItem2[BOD_ITEM_MIN_LOT_QTY_COLUMN] = np.where(
                df_BODItem2[LOADING_MST_TO_SITE_MIN_LOT_COLUMN].notna(),
                df_BODItem2[LOADING_MST_TO_SITE_MIN_LOT_COLUMN],
                "1"
            )

            df_BODItem2[BOD_ITEM_PYRUNFLAG_COLUMN] = 1
        else:
            df_BODItem2 = pd.DataFrame(columns=bod_item_columns)

        df_BODItem2 = df_BODItem2[bod_item_columns]
        print_df(df_BODItem2, 'STEP4 by 6.2  ____ df_BODItem2 .... create')
        step('=====> STEP4 by 6 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_BODItem = pd.concat([df_BODItem1, df_BODItem2], ignore_index=True).drop_duplicates()
        print_df(df_out_BODItem, 'STEP5 by 5.1  ____ df_out_BODItem .... df concat')

        df_out_BODItem[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_BODItem = df_out_BODItem[bod_item_final_columns]
        df_out_BODItem = ultra_fast_replace_to_none(df_out_BODItem)

        dataframes = {
            'df_out_BODItem': df_out_BODItem,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODItem = pd.DataFrame(columns=bod_item_final_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BODItem = pd.DataFrame(columns=bod_item_final_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
