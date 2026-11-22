"""

* 프로그램명
    - PY_UI_ProductPrice

* 내용
    - Product Price 의 신규 생성 데이터 내용 적용 및 Product Price M 값 업데이트
    - Demand가 있는 경우 Flag의 설정 변경

* 변경 이력
    - 2025-10-31  /best7.park (박병훈) / 신규 생성 Create
    - 2025-11-04 /best7.park (박병훈) / df_in_NowMonth 추가 및 Product_Price_Create_Time 적용 로직 추가 및 Product_Price_View_Flag 로직 추가
    - 2025-12-22 /best7.park (박병훈) / df_in_ProductPrice 에 있어도 Demand가 없으면 'N'으로 처리 하던 내용을  최근 3개월 내 생성되면 Product Price_View Flag 값 유지
    - 2026-01-06 /best7.park (박병훈) / 날짜 데이터 입력 여러개 데이터 때문에 함수 추가
    - 2026-01-21 / best7.park (박병훈) / 로직의 조건 수정
    - 2026-01-27  / best7.park (박병훈) / 빈 데이터 프레임 입력 시 Error 발생하는 것 수정

* Input Table
    - df_in_ProductPrice = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price_NewItemFlag], Measure.[Product Price_View Flag],Measure.[Product Price_Update Time], Measure.[Product Price_Create Time],Measure.[Dummy]}) on column;
    - df_in_ProductPriceM = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_View Flag], Measure.[Dummy] }) on column;
    - df_in_DemandItem = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item]  ) on row, ({Measure.[Item Site Asn_Dmd Flag],Measure.[Dummy]}) on column where { Measure.[Item Site Asn_Dmd Flag] == True };
    - df_in_BODItem = Select ([Version].[Version Name]* [Location].[Site Stage].Filter(#.Name contains("MF")).relatedmembers([Location]) * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Value],Measure.[Dummy]}) on column;
    - df_in_NowMonth = Select (&AllPlanningMonths.filter(#.Key >= &CurrentPlanningMonth.element(0).LeadOffset(-3).Key && #.Key <= &CurrentPlanningMonth.element(0).Key) * [Time].[Day]);

* Output Table
    - df_out_ProductPrice = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location]) on row, ({Measure.[Product Price_NewItemFlag], Measure.[Product Price_View Flag],Measure.[Product Price_Create Time]}) on column;
    - df_out_ProductPriceM =  Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_View Flag] }) on column;


* 데이터 삭제  (주의 필요 삭제 시 Input Data도 전부 삭제 됨
    - DELETE DATA FOR MODEL [Product Price] where {Version.[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [Product Price M] where {Version.[Version Name].[CWV_MP]};

* 테스트 스티립
    - EXEC plugin instance [PY_UI_ProductPrice] for measures {[Product Price_NewItemFlag]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (paramOutVersion ,"CWV_MP")} ;


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
import pytz

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ProductPrice'
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
        step(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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
            df_in_DemandItem       = read_csv_file('df_in_DemandItem')
            df_in_ProductPrice     = read_csv_file('df_in_ProductPrice')
            df_in_ProductPriceM    = read_csv_file('df_in_ProductPriceM')
            df_in_BODItem          = read_csv_file('df_in_BODItem')
            df_in_NowMonth         = read_csv_file('df_in_NowMonth')

        dataframes = {
            'df_in_DemandItem'    :        df_in_DemandItem,
            'df_in_ProductPrice'  :        df_in_ProductPrice,
            'df_in_ProductPriceM' :        df_in_ProductPriceM,
            'df_in_BODItem'       :        df_in_BODItem,
            'df_in_NowMonth'      :        df_in_NowMonth
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수설정
        Version_Name_COLUMN = 'Version.[Version Name]'
        Location_COLUMN = 'Location.[Location]'
        Item_COLUMN = 'Item.[Item]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        Time_Planning_Month_COLUMN = 'Time.[Planning Month]'
        Time_Day_COLUMN = 'Time.[Day]'

        Product_Price_NewItemFlag = 'Product Price_NewItemFlag'
        Product_Price_View_Flag = 'Product Price_View Flag'
        Product_Price_Update_Time = 'Product Price_Update Time'
        Product_Price_Create_Time = 'Product Price_Create Time'

        Product_Price_M_View_Flag = 'Product Price M_View Flag'

        Update_Time_Month = 'Update_Time_Month'
        Create_Time_Month = 'Create_Time_Month'

        step('=====> STEP 2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # df_in_DemandItem = df_in_DemandItem.head(0)
        # df_in_ProductPrice = df_in_ProductPrice.head(0)
        # df_in_ProductPriceM = df_in_ProductPriceM.head(0)
        # df_in_BODItem = df_in_BODItem.head(0)
        # df_in_NowMonth = df_in_NowMonth.head(0)

        # 날짜 변환을 위한 함수
        def to_yyyymm(s: pd.Series) -> pd.Series:
            x = (s.astype("string")
                 .str.replace("\u00A0", " ", regex=False)
                 .str.replace(r"\s+", " ", regex=True)
                 .str.replace(r"[-------]", "-", regex=True)
                 .str.strip())

            # 24시간제 + AM/PM 제거
            hh = pd.to_numeric(x.str.extract(r"\b(\d{1,2}):\d{2}:\d{2}\b")[0], errors="coerce")
            bad_ampm = x.str.contains(r"\bAM\b|bPM\b", case=False, regex=True, na=False) & hh.between(13, 23)
            x = x.mask(bad_ampm, x.str.replace(r"\s*\b(AM|PM)\b$", "", regex=True, case=False))

            dt = pd.Series(pd.NaT, index=x.index, dtype='datetime64[ns]')

            def fill(mask, fmt=None):
                nonlocal dt
                if not mask.any():
                    return
                if fmt is None:
                    dt.loc[mask] = pd.to_datetime(x.loc[mask], errors="coerce", cache=False)
                else:
                    dt.loc[mask] = pd.to_datetime(x.loc[mask], format=fmt, errors="coerce")

            # 1. US AM/PM
            fill(dt.isna() & x.str.match(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} (AM|PM)$", na=False),
                 "%m/%d%Y %I:%M:%S %p")

            # 2. US 24h
            fill(dt.isna() & x.str.match(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2}$", na=False), "%m/%d%Y %I:%M:%S")

            # 3. ISO Date
            fill(dt.isna() & x.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False), "%Y-%m-%d")

            # 4. ISO DateTime 24h
            fill(dt.isna() & x.str.match(r"^\d{4}-\d{2}-\d{2} \d{2}:d{2}:d{2}$", na=False), "%Y-%m-%d %H:%M:%S")

            # 5. YYYY.M.D .... (점 구분) -> '-'로 바뀐 두 일반 파싱
            m_dot = dt.isna() & x.str.match(r"^\d{4}\.\d{1,2}\.\d{1,2}", na=False)
            if m_dot.any():
                x2 = x.where(~m_dot, x.str.replace(".", "-", regex=False))
                dt.loc[m_dot] = pd.to_datetime(x2.loc[m_dot], errors="coerce", cache=False)

            # 6. 숫자만 있는 케이스
            digits = x.str.replace(r"\D+", "", regex=True)
            m8 = dt.isna() & digits.str.len().eq(8)
            m14 = dt.isna() & digits.str.len().eq(14)
            if m8.any():
                dt.loc[m8] = pd.to_datetime(digits.loc[m8], format="%Y/%m/%d", errors="coerce")
            if m14.any():
                dt.loc[m14] = pd.to_datetime(digits.loc[m14], format="%Y/%m/%d%H%M%S", errors="coerce")

            # 7. 마지막 fallback (남은것)
            fill(dt.isna())

            return dt.dt.strftime("%Y-%m-%d")

        def yyyymm_to_midx(x):
            x = x.astype('Int64')
            return (x // 100) * 12 + (x % 100)

        to_day_month = int(pd.Timestamp.today().strftime("%Y%m"))
        midx_today = (to_day_month//100) * 12 + (to_day_month % 100)

        # 1. df_in_DemandItem 기준으로 df_in_ProductPrice 에 데이터가 없는 정보 찾기
        # 1.1 서로 Key 값을 비교하기 위한 key Column 설정
        index_cols = [Version_Name_COLUMN, Item_COLUMN, Location_COLUMN]
        # 1.2 df_in_DemandItem 기준 Index 데이터 만들기
        df_in_DemandItem_index = df_in_DemandItem.set_index(index_cols).index
        # 1.3 df_in_ProductPrice기준 Index 데이터 만들기
        df_in_ProductPrice_index = df_in_ProductPrice.set_index(index_cols).index
        # 1.4 df_in_DemandItem 기준으로 df_in_ProductPrice 에 없는 데이터만 필터링
        df_in_DemandItem_outer = df_in_DemandItem[~df_in_DemandItem_index.isin(df_in_ProductPrice_index)]
        # 1.5 Product_Price_NewItemFlag & Product_Price_Create_Time 값 설정
        df_in_DemandItem_outer = df_in_DemandItem_outer.copy()
        print_df(df_in_DemandItem_outer, 'df_in_DemandItem_outer_ Demand In & Price None _확인 전', True)
        df_in_DemandItem_outer = df_in_DemandItem_outer.assign(Product_Price_NewItemFlag ="Y")
        # df_in_DemandItem_outer[Product_Price_NewItemFlag] = str('Y')
        df_in_DemandItem_outer[Product_Price_View_Flag] = 'Y'
        df_in_DemandItem_outer[Product_Price_Create_Time] = pd.Series(
            [pd.Timestamp.today().normalize()] * len(df_in_DemandItem_outer), index = df_in_DemandItem_outer.index)
        # df_in_DemandItem_outer.loc[:, Product_Price_Create_Time] = pd.Timestamp.today().normalize()
        df_in_DemandItem_outer.loc[:, Product_Price_Create_Time] = to_yyyymm(df_in_DemandItem_outer[Product_Price_Create_Time])
        # df_in_DemandItem_outer.loc[:,Product_Price_Create_Time] = datetime.date.today().strftime("%Y-%m-%d")
        # df_in_DemandItem_outer[Product_Price_Create_Time] = df_in_DemandItem_outer[Product_Price_Create_Time].apply(
        #     convert_date_format)
        # note(f"======================={datetime.date.today().strftime("%Y-%m-%d")}===============================")
        print_df(df_in_DemandItem_outer, 'df_in_DemandItem_outer_ Demand In & Price None')

        # 2. df_in_DemandItem_outer 와 df_in_BODItem 에서 Sub Location 찾기
        # 2.1 df_in_BODItem 의 컬럼명 변경  (Location → Sub Location ,   Sub Location → Location)
        df_in_BODItem = df_in_BODItem.rename(
            columns={Location_COLUMN: SUB_LOCATION_COLUMN, SUB_LOCATION_COLUMN: Location_COLUMN})
        # 2.2 df_in_DemandItem_outer 에 Sub Location 정보 merge (left inner)
        df_in_DemandItem_outer = df_in_DemandItem_outer.merge(df_in_BODItem[index_cols + [SUB_LOCATION_COLUMN]],
                                                              on=index_cols, how='inner')

        print_df(df_in_DemandItem_outer, 'df_in_DemandItem_outer Demand 의 Sub Location 찾기', True)

        # 3 df_in_ProductPrice 기준으로 데이터가 있고 df_in_DemandItem 에 없는 데이터만 필터링
        df_in_ProductPrice_inner = df_in_ProductPrice[~df_in_ProductPrice_index.isin(df_in_DemandItem_index)]
        # 날짜로 변환
        df_in_ProductPrice_inner.loc[:,Product_Price_Update_Time] = to_yyyymm(
            df_in_ProductPrice_inner[Product_Price_Update_Time]).copy()
        df_in_ProductPrice_inner.loc[:,Product_Price_Create_Time] = to_yyyymm(
            df_in_ProductPrice_inner[Product_Price_Create_Time]).copy()

        print_df(df_in_ProductPrice_inner, 'df_in_ProductPrice_inner Prince In & Demand None', True)

        # 4 df_in_ProductPrice 도 있고 df_in_DemandItem 도 있는 데이터
        df_in_ProductPrice_InDemand = df_in_ProductPrice[df_in_ProductPrice_index.isin(df_in_DemandItem_index)]
        df_in_ProductPrice_InDemand.loc[:,Product_Price_Update_Time] = to_yyyymm(
            df_in_ProductPrice_InDemand[Product_Price_Update_Time]).copy()
        df_in_ProductPrice_InDemand.loc[:,Product_Price_Create_Time] = to_yyyymm(
            df_in_ProductPrice_InDemand[Product_Price_Create_Time]).copy()

        print_df(df_in_ProductPrice_InDemand, 'df_in_ProductPrice_InDemand Price & Demand All In',True)

        ############################ 2025-11-04 수정 ybest7.park(박병훈 수정) ############################################

        # 5 df_in_ProductPrice_inner Product_Price_View_Flag 처리 (Prince In & Demand None 데이터 처리)
        df_in_ProductPrice_inner = df_in_ProductPrice_inner.drop(columns=Product_Price_View_Flag, axis=1)

        ############################ 2025-12-22 수정 ybest7.park(박병훈 수정 Start) #######################################

        # 6 df_in_NowMonth의 최소 일자 설정
        min_Month = pd.to_numeric(df_in_NowMonth[Time_Planning_Month_COLUMN]).min()

        note(f"min_Month = {min_Month} 입니다 =================================================================>")

        df_in_ProductPrice_inner[Product_Price_View_Flag] = str('N')

        df_in_ProductPrice_inner = df_in_ProductPrice_inner.copy()

        # df_in_ProductPrice_inner[Update_Time_Month] = to_yyyymm_int(df_in_ProductPrice_inner[Product_Price_Update_Time])
        #
        # df_in_ProductPrice_inner[Update_Time_Month] = df_in_ProductPrice_inner[Update_Time_Month].fillna(0)

        df_in_ProductPrice_inner.loc[:,Update_Time_Month] = pd.to_datetime(
            df_in_ProductPrice_inner[Product_Price_Update_Time], errors='coerce').dt.strftime('%Y%m').fillna(
            0).astype(int)
        # 7.2 Product_Price_Create_Time 데이터를 가지고 월로 만들기
        # df_in_ProductPrice_inner[Create_Time_Month] = to_yyyymm_int(df_in_ProductPrice_inner[Product_Price_Create_Time])
        #
        # df_in_ProductPrice_inner[Create_Time_Month] =  df_in_ProductPrice_inner[Create_Time_Month].fillna(0)

        df_in_ProductPrice_inner.loc[:,Create_Time_Month] = pd.to_datetime(
            df_in_ProductPrice_inner[Product_Price_Create_Time], errors='coerce').dt.strftime('%Y%m').fillna(
            "0").astype('int64')

        ############################# 2026-01-21 조건 수정 (ybest7.park) ################################################
        # 7.3 Product_Price_View_Flag 설정을 위한 조건 지정

        um = pd.to_numeric(df_in_ProductPrice_inner[Update_Time_Month], errors = 'coerce').round().astype(int)
        cm = pd.to_numeric(df_in_ProductPrice_inner[Create_Time_Month], errors = 'coerce').round().astype(int)

        # note(f"Step  확인 1 ================================================================>")
        um_midx = yyyymm_to_midx(um)
        cm_midx = yyyymm_to_midx(cm)

        um_ok = um.notna() & (um % 100).between(1,12)
        cm_ok = cm.notna() & (cm % 100).between(1, 12)

        # note(f"Step  확인 2 ================================================================>")

        # 기존 조건
        m_old  = (um_ok & (um <= min_Month)) | (cm_ok & (cm <= min_Month)).fillna(False).to_numpy(dtype=bool)

        # 최근 3개월 (이번달 포함) 2개월 내 라면 조건 변경
        m_recent3 = (um_ok & um_midx.between(midx_today-2, midx_today)) | \
                    (cm_ok & cm_midx.between(midx_today - 2, midx_today)).fillna(False).to_numpy(dtype=bool)

        # note(f"Step  확인 2 ================================================================>")

        # 8 df_in_ProductPrice_inner 의 Product_Price_View_Flag 값 설정
        # 최종 조건
        df_in_ProductPrice_inner[Product_Price_View_Flag] = ""
        df_in_ProductPrice_inner.loc[m_old.fillna(False), Product_Price_View_Flag] = "N"
        df_in_ProductPrice_inner.loc[m_recent3.fillna(False), Product_Price_View_Flag] = "Y"

        # df_in_ProductPrice_inner[Product_Price_View_Flag] = np.select(
        #     [m_recent3,m_old],["Y","N"], default=" ")

        ############################# 2026-01-21 조건 수정 (ybest7.park) ################################################

        # condition = (df_in_ProductPrice_inner[Update_Time_Month] <= min_Month) | (
        #         df_in_ProductPrice_inner[Create_Time_Month] <= min_Month)
        # # 8 df_in_ProductPrice_inner 의 Product_Price_View_Flag 값 설정
        # df_in_ProductPrice_inner = df_in_ProductPrice_inner.drop(columns=[Product_Price_View_Flag]).copy()
        # df_in_ProductPrice_inner[Product_Price_View_Flag] = np.where(condition, 'N', ' ')
        # df_in_ProductPrice_inner[Product_Price_NewItemFlag] = 'Y'
        ############################ 2025-12-22 수정 ybest7.park(박병훈 수정 Ern) #########################################

        print_df(df_in_ProductPrice_inner, 'df_in_ProductPrice_inner 확인', True)
        # 7 planning Month 설정을 위한 신규 컬럼 생성
        # 7.1 Product_Price_Update_Time 데이터를 가지고 월로 만들기
        df_in_ProductPrice_InDemand = df_in_ProductPrice_InDemand.copy()
        # df_in_ProductPrice_InDemand[Product_Price_Update_Time] = pd.to_datetime(
        #     df_in_ProductPrice_InDemand[Product_Price_Update_Time], format='%Y%m%d',errors='coerce')
        # df_in_ProductPrice_InDemand[Product_Price_Create_Time] = pd.to_datetime(
        #     df_in_ProductPrice_InDemand[Product_Price_Create_Time], format='%Y%m%d', errors='coerce')
        # df_in_ProductPrice_InDemand[Update_Time_Month] = to_yyyymm_int(df_in_ProductPrice_InDemand[Product_Price_Update_Time])
        # df_in_ProductPrice_InDemand[Update_Time_Month] = df_in_ProductPrice_InDemand[Update_Time_Month].fillna(0)


        # 7.2 Product_Price_Create_Time 데이터를 가지고 월로 만들기
        # df_in_ProductPrice_InDemand[Create_Time_Month] = to_yyyymm_int(
        #     df_in_ProductPrice_InDemand[Product_Price_Create_Time])
        # df_in_ProductPrice_InDemand[Create_Time_Month] = df_in_ProductPrice_InDemand[Create_Time_Month].fillna(0)

        df_in_ProductPrice_InDemand[Update_Time_Month] = pd.to_datetime(
            df_in_ProductPrice_InDemand[Product_Price_Update_Time], errors='coerce').dt.strftime('%Y%m').fillna(
            0).astype(int)

        df_in_ProductPrice_InDemand[Create_Time_Month] = pd.to_datetime(
            df_in_ProductPrice_InDemand[Product_Price_Create_Time], errors='coerce').dt.strftime('%Y%m').fillna(
            0).astype(int)


        # 7.3 Product_Price_View_Flag 설정을 위한 조건 지정 (3개월 내)
        cm = df_in_ProductPrice_InDemand[Update_Time_Month].astype(int)
        um = df_in_ProductPrice_InDemand[Create_Time_Month].astype(int)

        cm_midx = yyyymm_to_midx(cm)
        um_midx = yyyymm_to_midx(um)

        cm_ok = (cm % 100).between(1,12)
        um_ok = (um % 100).between(1,12)

        in3_cm = cm_ok & cm_midx.between(midx_today-2, midx_today)
        in3_um = um_ok & um_midx.between(midx_today-2, midx_today)

        skip = in3_cm | in3_um

        do_update = ~skip

        df_in_ProductPrice_InDemand.loc[do_update,Product_Price_View_Flag] = "N"

        # midx_col = (df_in_ProductPrice_InDemand[Update_Time_Month].astype(int) // 100) * 12 + (df_in_ProductPrice_InDemand[Update_Time_Month].astype(int) % 100)
        #
        # condition1 = (midx_col >= midx_today - 2) & (midx_col <= midx_today)
        # # 8 df_in_ProductPrice_inner 의 Product_Price_View_Flag 값 설정
        # df_in_ProductPrice_InDemand = df_in_ProductPrice_InDemand.drop(columns=[Product_Price_View_Flag]).copy()
        # df_in_ProductPrice_InDemand[Product_Price_View_Flag] = np.where(condition1, 'Y', '')

        # print_df(df_in_ProductPrice_InDemand, 'df_in_ProductPrice_InDemand Product_Price_View_Flag 처리 확인 2' , True)

        # df_in_DemandItem_outer[Product_Price_Create_Time] = df_in_DemandItem_outer[Product_Price_Create_Time].astype(
        #     'datetime64[ns]')
        # df_in_ProductPrice_InDemand[Product_Price_Create_Time] = df_in_ProductPrice_InDemand[Product_Price_Create_Time].astype(
        #     'datetime64[ns]')
        # df_in_ProductPrice_inner[Product_Price_Create_Time] = df_in_ProductPrice_inner[Product_Price_Create_Time].astype(
        #     'datetime64[ns]')

        # df_in_DemandItem_outer[Product_Price_Create_Time] = pd.to_datetime(
        #     df_in_DemandItem_outer[Product_Price_Create_Time] ,  errors='coerce')
        #
        # df_in_ProductPrice_InDemand[Product_Price_Create_Time] = pd.to_datetime(
        #     df_in_ProductPrice_InDemand[Product_Price_Create_Time], errors='coerce')
        #
        # df_in_ProductPrice_inner[Product_Price_Create_Time] = pd.to_datetime(
        #     df_in_ProductPrice_inner[Product_Price_Create_Time], errors='coerce')


        print_df(df_in_DemandItem_outer, 'df_in_DemandItem_outer _ 데이터 타입 확인',True)
        print_df(df_in_ProductPrice_InDemand, 'df_in_ProductPrice_InDemand _ 데이터 타입 확인',True)
        print_df(df_in_ProductPrice_inner, 'df_in_ProductPrice_inner _ 데이터 타입 확인',True)

        # 9. Out put 설정 (df_in_DemandItem_outer 와  df_in_ProductPrice_InDemand , df_in_ProductPrice_inner 합치기)
        df_out_ProductPrice = pd.concat([df_in_DemandItem_outer, df_in_ProductPrice_InDemand,df_in_ProductPrice_inner ],
                                        axis=0, ignore_index=True)

        # note(f"=======================================> Step 확인")
        # 10 Product_Price_Create_Time null 값 조건 추가

        # df_out_ProductPrice[Product_Price_Update_Time] = pd.to_datetime(
        #     df_out_ProductPrice[Product_Price_Update_Time], errors='coerce')
        #
        # df_out_ProductPrice[Product_Price_Create_Time] = pd.to_datetime(
        #     df_out_ProductPrice[Product_Price_Create_Time], errors='coerce')

        condition_day = (df_out_ProductPrice[Product_Price_Update_Time].isnull()) & (
            df_out_ProductPrice[Product_Price_Create_Time].isnull())
        df_out_ProductPrice[Product_Price_Create_Time] = np.where(condition_day, pd.Timestamp('1999-01-01'),
                                                                      df_out_ProductPrice[
                                                                          Product_Price_Create_Time])

        print_df(df_out_ProductPrice, "df_out_ProductPrice ____ 데이터 확인 --- 임시")

        # df_out_ProductPrice[Product_Price_Create_Time] = pd.to_datetime(
        #     df_out_ProductPrice[Product_Price_Create_Time], errors='coerce')

        # note(f"=======================================> Step 확인1 ")
        #
        # print_df(df_out_ProductPrice, "df_out_ProductPrice ____ 데이터 확인")

        # df_out_ProductPrice[Product_Price_Create_Time] = df_out_ProductPrice[
        #     Product_Price_Create_Time].astype(
        #     'datetime64[ns]')
        #
        # note(f"=======================================> Step 확인2 ")

        # print_df(df_out_ProductPrice, 'df_out_ProductPrice  임시 확인')

        ############################ 2025-11-04 수정 ybest7.park(박병훈 수정) ############################################

        # # 4. Out put 설정 (df_in_DemandItem_outer 와 df_in_ProductPrice_inner 합치기)
        # df_out_ProductPrice = pd.concat([df_in_DemandItem_outer, df_in_ProductPrice_inner], axis=0, ignore_index=True)

        # 9. Out put 순서 지정
        df_out_ProductPrice = df_out_ProductPrice[
            [Version_Name_COLUMN, Item_COLUMN, Location_COLUMN, SUB_LOCATION_COLUMN, Product_Price_NewItemFlag,
             Product_Price_View_Flag,Product_Price_Create_Time]]

        df_out_ProductPrice.loc[:,Product_Price_Create_Time] = to_yyyymm(df_out_ProductPrice[Product_Price_Create_Time])
        print_df(df_out_ProductPrice , "df_out_ProductPrice 확인")

        step('=====> STEP 3 End')
        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')

        # 1 df_in_ProductPriceM 기준 Index Data 만들기
        df_in_ProductPriceM_index = df_in_ProductPriceM.set_index(index_cols).index
        # 2 df_in_DemandItem 기준 df_in_ProductPriceM 에 있는 것만 필터링
        df_in_DemandItem_outerM = df_in_ProductPriceM[df_in_ProductPriceM_index.isin(df_in_DemandItem_index)]
        # 3. Product_Price_M_View_Flag 기본 값 설정 'N'
        df_in_DemandItem_outerM[Product_Price_M_View_Flag] = 'Y'
        # 4. Out put Columns 설정
        df_out_ProductPriceM = df_in_DemandItem_outerM[
            [Version_Name_COLUMN, Item_COLUMN, Location_COLUMN, SUB_LOCATION_COLUMN,
             Time_Planning_Month_COLUMN,Product_Price_M_View_Flag]].copy()


        print_df(df_out_ProductPriceM ,"df_out_ProductPriceM 확인")

        step('=====> STEP 4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################

        step('=====> STEP 5 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_ProductPrice, 'df_out_ProductPrice', True)
            print_df(df_out_ProductPriceM, 'df_out_ProductPriceM', True)


        print_df(df_out_ProductPrice, 'df_out_ProductPrice', True)
        print_df(df_out_ProductPriceM, 'df_out_ProductPriceM', True)

        row_count, col_count = df_out_ProductPrice.shape
        note(f'=====> Final df_out_ProductPrice rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_ProductPriceM.shape
        note(f'=====> Final df_out_ProductPriceM rows : {row_count} , Columns : {col_count}')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ProductPrice = pd.DataFrame([], columns=[])
        df_out_ProductPriceM = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
