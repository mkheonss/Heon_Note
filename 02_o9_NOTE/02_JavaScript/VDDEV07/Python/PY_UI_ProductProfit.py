"""

* 프로그램명
    - PY_UI_ProductProfit

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024-10-04 / ybest7.park (박병훈) / Create
- 2025-12-03 / ybest7.park (박병훈) / 전체적으로 신규 생성

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
     - df_in_ProductProfitUpload =  Select ([Version].[Version Name].[VD] * [Location].[Location] * [To Time].[To Year] * [Item].[Product Group] * [Item].[Definition] * [Item].[Series] * [Item].[Strategy] * [Item].[KPI] * [Item].[Item] * [Item].[Inch] * [Time].[Planning Month]* [Item].[Marketing Name] * [Sales Domain].[AP2] * [Execution Version].[Execution Version] * [Business Area].[Business Area] ) on row, ({Measure.[Product Profit Upload_C Profit Rate], Measure.[Product Profit Upload_N Price], Measure.[Product Profit Upload_N Price Currency], Measure.[Product Profit Upload_Sales Qty], Measure.[Dummy]}) on column where {(Measure.[Product Profit Upload_N Price]>=0)};
     - df_in_DmdW = Select ([Version].[Version Name].[CWV_MP]* [Item].[Product Group] * [Item].[Marketing Name] * [Item].[Inch] * [Item].[Strategy] * [Item].[Series] * [Item].[KPI]  * [Item].[Definition] * [Item].[Item] * [Sales Domain].[AP2] ) on row,({Measure.[Dmd W_Qty], Measure.[Dummy]}) on column;
     - df_in_Toyear = Select([Time].[Year] * [Time].[Planning Month]);


* 데이터 삭제
     DELETE DATA FOR MODEL [Product Profit] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_ProductProfit = Select ([Version].[Version Name].[CWV_MP] * [To Time].[To Year] * [Item].[Item] * [Time].[Planning Month] * [Sales Domain].[AP2] * [Execution Version].[Execution Version] ) on row, ({Measure.[Product Profit_C Profit Rate], Measure.[Product Profit_N Price], Measure.[Product Profit_N Price Currency], Measure.[Product Profit_Product Grade], Measure.[Product Profit_Profit Grade], Measure.[Product Profit_Profit Rank], Measure.[Product Profit_Rank], Measure.[Product Profit_Sales Qty]}) on column;


* 테스트 스크립트
    EXEC plugin instance [PY_UI_ProductProfit] for Measures {[Product Profit_C Profit Rate]} using scope ([Version].[Version Name].filter((#.Name == "CWV_MP") || (#.Name == "VD")))  using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


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
str_instance = 'PY_UI_ProductProfit'
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


def print_df(df, df_name, _localFlag=True):
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
        step('=====> STEP 1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_ProductProfitUpload = read_csv_file('df_in_ProductProfitUpload')
            df_in_DmdW = read_csv_file('df_in_DmdW')
            df_in_Toyear = read_csv_file('df_in_Toyear')


        dataframes = {
             'df_in_ProductProfitUpload'                   :        df_in_ProductProfitUpload,
            'df_in_DmdW'                                   :        df_in_DmdW,
            'df_in_Toyear'                                 :        df_in_Toyear,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1 End')
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2 Start : DataFrame Column 변수 처리')

        Version_COLUMN = 'Version.[Version Name]'
        Location_COLUMN = 'Location.[Location]'
        To_Time_Year_COLUMN = 'To Time.[To Year]'
        Time_Year_COLUMN = 'Time.[Year]'
        Item_Product_GROUP_COLUMN = 'Item.[Product Group]'
        Item_Definition_COLUMN = 'Item.[Definition]'
        Item_Inch_COLUMN = 'Item.[Inch]'
        Item_Series_COLUMN = 'Item.[Series]'
        Item_KPI_COLUMN = 'Item.[KPI]'
        Item_Item_COLUMN = 'Item.[Item]'
        Item_Strategy_COLUMN = 'Item.[Strategy]'
        Item_Marketing_Name_COLUMN = 'Item.[Marketing Name]'
        Time_Planning_Month_COLUMN = 'Time.[Planning Month]'
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        Execution_Version_COLUMN = 'Execution Version.[Execution Version]'
        Business_Area_COLUMN = 'Business Area.[Business Area]'

        Product_Profit_Upload_C_Profit_Rate = 'Product Profit Upload_C Profit Rate'
        Product_Profit_Upload_N_Price = 'Product Profit Upload_N Price'
        Product_Profit_Upload_N_Price_Currency = 'Product Profit Upload_N Price Currency'
        Product_Profit_Upload_Sales_Qty = 'Product Profit Upload_Sales Qty'

        Dmd_W_BAL = 'Dmd W_BAL'
        Dummy = 'Dummy'

        Product_Profit_C_Profit_Rate = 'Product Profit_C Profit Rate'
        Product_Profit_N_Price = 'Product Profit_N Price'
        Product_Profit_N_Price_Currency = 'Product Profit_N Price Currency'
        Product_Profit_Sales_Qty = 'Product Profit_Sales Qty'
        Product_Profit_Product_Grade = 'Product Profit_Product Grade'
        Product_Profit_Profit_Grade = 'Product Profit_Profit Grade'
        Product_Profit_Profit_Rank = 'Product Profit_Profit Rank'
        Product_Profit_Rank = 'Product Profit_Rank'

        TV = 'TV'
        AV = 'AV'
        MONITOR = 'MONITOR'

        A = 'A'
        B = 'B'
        C = 'C'
        D = 'D'
        E = 'E'

        OLED = 'OLED'
        QLED = 'QLED'
        UHD = 'UHD'
        Gaming = 'Gaming'
        Main_Stream = 'Main Stream'

        key_on = 'key on'

        step('=====> STEP 2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP 3 Start : input data machining')

        #Step 1 df_in_ProductProfitUpload 의 Time_Planning_Month_COLUMN Min & Max 설정
        min_month = pd.to_numeric(df_in_ProductProfitUpload[Time_Planning_Month_COLUMN].min())
        max_month = pd.to_numeric(df_in_ProductProfitUpload[Time_Planning_Month_COLUMN].max())

        #Step 2 df_in_Toyear 의 범위 설정
        # df_in_Toyear 의 Time_Planning_Month_COLUMN 데이터 타입 변경
        df_in_Toyear[Time_Planning_Month_COLUMN] = df_in_Toyear[Time_Planning_Month_COLUMN].astype(int)
        # 설정된 범위로 필터링
        df_in_Toyear = df_in_Toyear[df_in_Toyear[Time_Planning_Month_COLUMN].between(min_month, max_month)]


        #Step 1 df_in_ProductProfitUpload 데이터 전 처리
        # df_in_ProductProfitUpload 그룹 바이를 통해 계산
        # 함수 생성
        def agg_func(m):
            amount = (m[Product_Profit_N_Price] * m[Product_Profit_Sales_Qty]).sum()
            amount_rate = (
                    m[Product_Profit_N_Price] * m[Product_Profit_Sales_Qty] * m[Product_Profit_C_Profit_Rate]).sum()
            qty_sum = m[Product_Profit_Sales_Qty].sum()
            # currency_max = m[Product_Profit_Upload_N_Price_Currency].max()

            return pd.Series({
                Product_Profit_C_Profit_Rate: amount / amount_rate,
                Product_Profit_N_Price: amount / qty_sum,
                Product_Profit_Sales_Qty: qty_sum,
                # Product_Profit_N_Price_Currency : currency_max
            })


        # 함수 적용을 위한 컬럼명 변경
        df_in_ProductProfitUpload = df_in_ProductProfitUpload.rename(columns={
            Product_Profit_Upload_N_Price: Product_Profit_N_Price,
            Product_Profit_Upload_Sales_Qty: Product_Profit_Sales_Qty,
            Product_Profit_Upload_C_Profit_Rate: Product_Profit_C_Profit_Rate
        })


        # 그룹 바이를 위한 컬럼 설정
        # 그룹 바이를 위한 컬럼 설정
        groupby_cols = [
            To_Time_Year_COLUMN, Time_Planning_Month_COLUMN, Execution_Version_COLUMN,
            SALES_DOMAIN_AP2_COLUMN, Item_Item_COLUMN, Item_Product_GROUP_COLUMN, Item_Strategy_COLUMN,
            Item_Inch_COLUMN, Item_Marketing_Name_COLUMN, Item_Definition_COLUMN, Item_Series_COLUMN,
            Item_KPI_COLUMN, Product_Profit_Upload_N_Price_Currency]

        # df_in_ProductProfitUpload 그룹바이 실행
        df_in_ProductProfitUpload_temp = df_in_ProductProfitUpload.groupby(groupby_cols).apply(agg_func).reset_index()


        # Product_Profit_Profit_Grade 설정을 위한 처리
        # 공통 마스트
        is_tv = df_in_ProductProfitUpload_temp[Item_Product_GROUP_COLUMN].eq(TV)
        is_av = df_in_ProductProfitUpload_temp[Item_Product_GROUP_COLUMN].eq(AV)
        is_mnt = df_in_ProductProfitUpload_temp[Item_Product_GROUP_COLUMN].eq(MONITOR)

        # Item_Definition_COLUMN 데이터 형식에 따르 변수 설정
        definition_str = df_in_ProductProfitUpload_temp[Item_Definition_COLUMN].astype(str)
        definition_num = pd.to_numeric(definition_str, errors='coerce')

        # 필터 적용을 위한 conditions  지정
        conditions = [
            # ------ TV -----
            is_tv & definition_str.isin([OLED, QLED]),  # TV + OLED/QLED 이면 → A
            is_tv & definition_str.eq(UHD),  # TV + UHD  이면 → B
            is_tv & ~definition_str.isin([OLED, QLED, UHD]),  # TV 그 외는 → C

            # ----- AV -----
            is_av & definition_num.between(8, 9),  # AV + 8 ~ 9 이며 → A
            is_av & definition_num.between(6, 7),  # AV + 6 ~ 7 이며 → B
            is_av & (definition_num <= 5),  # AV + 5 이하 이면  → C

            # ----- MONITOR -----
            is_mnt & definition_str.isin([Gaming, '고해상도']),  # MONITOR + Gaming/고해상도 이면 → A
            is_mnt & definition_str.eq(Main_Stream),  # MONITOR + Main Stream 이면 → B
        ]

        # 선택 변수 설정
        choices = [
            A,  # TV + OLED/QLED
            B,  # TV + UHD
            C,  # 그외
            A,  # AV + 8 ~ 9
            B,  # AV + 6 ~ 7
            C,  # AV + 5 이하
            A,  # MONITOR + Gaming/고해상도
            B,  # MONITOR + Main Stream
        ]

        df_in_ProductProfitUpload_temp[Product_Profit_Product_Grade] = np.select(conditions, choices,
                                                                                 default=C)  # 예외는 모두 C


        # Product Profit_Profit Grade 등급 나누기
        # 등급 설정
        bins = [-np.inf, 0, 0.05, 0.10, 0.15, np.inf]
        labels = [E, D, C, B, A]
        # 등급 적용 전 데이터 타입 변경
        df_in_ProductProfitUpload_temp[Product_Profit_C_Profit_Rate] = pd.to_numeric(
            df_in_ProductProfitUpload_temp[Product_Profit_C_Profit_Rate], errors='coerce')
        # 등급 적용
        df_in_ProductProfitUpload_temp[Product_Profit_Profit_Grade] = pd.cut(
            df_in_ProductProfitUpload_temp[Product_Profit_C_Profit_Rate],
            bins=bins,
            labels=labels,
            right=False
        )

        # Product_Profit_Profit_Rank 설정 Product_Profit_Product_Grade + Product_Profit_Profit_Grade
        df_in_ProductProfitUpload_temp[Product_Profit_Profit_Rank] = df_in_ProductProfitUpload_temp[
                                                                         Product_Profit_Profit_Grade].astype(str) + \
                                                                     df_in_ProductProfitUpload_temp[
                                                                         Product_Profit_Product_Grade].astype(str)

        # Product_Profit_Profit_Rank 조건에 따른 Product_Profit_Rank 설정
        # 등급 만들기
        first_conditions = [A, B, C, D, E]
        second_conditions = [A, B, C]
        # 15개 등급 순선대로 생성
        grade_list = [f + s for f in first_conditions for s in second_conditions]
        # 생성된 등급 순서에 맞추어 번호 지정
        grade_to_rank = {g: i + 1 for i, g in enumerate(grade_list)}
        # 등급 값 지정
        df_in_ProductProfitUpload_temp[Product_Profit_Rank] = df_in_ProductProfitUpload_temp[
            Product_Profit_Profit_Rank].map(grade_to_rank)

        # df_in_ProductProfitUpload_temp = df_in_ProductProfitUpload_temp.drop(
        #     columns=Product_Profit_Upload_N_Price_Currency, axis=1)

        print_df(df_in_ProductProfitUpload_temp, 'df_in_ProductProfitUpload_temp 확인')

        step('=====> STEP 3 End')
        ################################################################################################################
        # Step 4. (1) Out put 처리를 위한 전처리 및 Month의 범의 값 확인
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')

        # Year & Month로 확장하기
        # df_in_Toyear = df_in_Toyear.copy().assign(**{key_on: 1})
        # df_in_DmdW = df_in_DmdW.copy().assign(**{key_on: 1})
        df_in_Toyear[key_on] = 1
        df_in_DmdW[key_on] = 1

        # 데이터 프레임 확장하기
        df_in_DmdW = df_in_DmdW.merge(
            df_in_Toyear[
                [Time_Year_COLUMN, Time_Planning_Month_COLUMN,
                 key_on]],
            on=key_on,
            how='left')

        # Execution_Version list 생성
        Execution_Version_list = df_in_ProductProfitUpload_temp[Execution_Version_COLUMN].unique().tolist()

        # df_in_DmdW 에 Execution_Version 추가하기
        df_in_DmdW[Execution_Version_COLUMN] = df_in_DmdW.apply(lambda x: list(Execution_Version_list), axis=1)
        # Execution_Version_COLUMN 확장하기
        df_in_DmdW = df_in_DmdW.explode(Execution_Version_COLUMN)

        # 필터를 위한 데이터 타입 변경
        df_in_ProductProfitUpload_temp[SALES_DOMAIN_AP2_COLUMN] = df_in_ProductProfitUpload_temp[
            SALES_DOMAIN_AP2_COLUMN].astype(str)
        df_in_ProductProfitUpload_temp[Time_Planning_Month_COLUMN] = df_in_ProductProfitUpload_temp[
            Time_Planning_Month_COLUMN].astype(str)
        df_in_DmdW[SALES_DOMAIN_AP2_COLUMN] = df_in_DmdW[SALES_DOMAIN_AP2_COLUMN].astype(str)
        df_in_DmdW[Time_Planning_Month_COLUMN] = df_in_DmdW[Time_Planning_Month_COLUMN].astype(str)

        # Step 1 df_in_DmdW 에 있는 데이터 중 df_in_ProductProfitUpload 에 없는 것만 필터링
        # 1. Index Columns 설정 (Item과 AP2 기준으로 없는 것만 필터링)
        index_cols = [Item_Item_COLUMN, SALES_DOMAIN_AP2_COLUMN, Time_Planning_Month_COLUMN]
        # df_in_ProductProfitUpload 와 df_in_DmdW index 컬럼 설정
        df_in_ProductProfitUpload_index = df_in_ProductProfitUpload_temp.set_index(index_cols).index
        df_in_DmdW_index = df_in_DmdW.set_index(index_cols).index
        # df_in_DmdW 데이터 프레임에서 필터링
        df_in_DmdW = df_in_DmdW[~df_in_DmdW_index.isin(df_in_ProductProfitUpload_index)]

        print_df(df_in_DmdW, 'df_in_DmdW 확인')

        step('=====> STEP 3 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')

        # 1. 제품별 데이터 찾을 롤 정의
        fallback_rules = {
            TV: [
                [Item_Product_GROUP_COLUMN, Item_Inch_COLUMN],  # 1 순위 : TV + inch
                [Item_Product_GROUP_COLUMN, Item_Marketing_Name_COLUMN],  # 2 순위 : TV + Marketing Name
                [Item_Product_GROUP_COLUMN],  # 3 순위 : TV 전체
            ],
            AV: [
                [Item_Product_GROUP_COLUMN, Item_Series_COLUMN],  # 1 순위 : AV + Series
                [Item_Product_GROUP_COLUMN, Item_Strategy_COLUMN],  # 2 순위 : AV + Strategy
                [Item_Product_GROUP_COLUMN],  # 3 순위 : AV 전체
            ],
            MONITOR: [
                [Item_Product_GROUP_COLUMN, Item_Inch_COLUMN],  # 1 순위 : Monitor + inch
                [Item_Product_GROUP_COLUMN, Item_KPI_COLUMN],  # 2 순위 : Monitor + KPI
                [Item_Product_GROUP_COLUMN],  # 3 순이 : Monitor 전체
            ],
        }

        # 기본 값을 추가해야 한는 measure cols 설정
        measure_cols = [Product_Profit_N_Price, Product_Profit_Sales_Qty, Product_Profit_C_Profit_Rate]


        # 값을 적용하기 위한 함수
        def add_fallback_rules(df_base, df_ref, Item_Product_GROUP_COLUMN, levels, value_cols):
            # 해당 product만 필터
            base = df_base[df_base[Item_Product_GROUP_COLUMN] == product].copy()
            ref = df_ref[df_ref[Item_Product_GROUP_COLUMN] == product].copy()
            note(f'[{product}] base rows = {len(base)}, ref rows = {len(ref)}')

            if base.empty:
                return base  # 해당 Product가 기준에 되는 곳에 갑이 없으면 그대로 반환

            if ref.empty:
                return None

            # 전부 평균을 반환
            agg_dict = {col: 'mean' for col in value_cols}
            agg_dict[Product_Profit_Upload_N_Price_Currency] = 'max'

            # 레벨별 집계 + merge
            for i, keys in enumerate(levels, start=1):
                agg = (
                    ref.groupby(keys, as_index=False)
                    .agg(agg_dict)
                )
                agg = agg.rename(columns={col: f"{col}_lv{i}" for col in value_cols})
                base = base.merge(agg, on=keys, how='left')

            # 레벨별 fallback (inch → marketing name → 전체 / Series → Strategy → 전체 / inch → KPI → 전체)
            for col in value_cols:
                lv_cols = [f'{col}_lv{i}' for i in range(1, len(levels) + 1)]
                base[col] = base[lv_cols].bfill(axis=1).iloc[:, 0]

            # cur_lv_cols = [
            #     f"{Product_Profit_Upload_N_Price_Currency}_lv(i)" for i in range(1, len(levels) + 1)
            # ]
            # base[Product_Profit_Upload_N_Price_Currency] = base[cur_lv_cols].bfill(axis=1).iloc[:, 0]
            # s = base[lv_cols[0]]
            # for c in lv_cols[1:]:
            #     s = s.fillna(base[c])
            # base[col + '_final'] = s

            # 중간 lv 컬럼 정리
            lv_cols_all = []
            for col in value_cols:
                lv_cols_all.extend([f'{col}_lv{i}' for i in range(1, len(levels) + 1)])
            base = base.drop(columns=[c for c in lv_cols_all if c in base.columns])
            return base


        df_in_ProductProfitUpload_temp[Item_Inch_COLUMN] = df_in_ProductProfitUpload_temp[Item_Inch_COLUMN].astype(str)
        df_in_DmdW[Item_Inch_COLUMN] = df_in_DmdW[Item_Inch_COLUMN].astype(str)

        results = []

        for product, levels in fallback_rules.items():
            base_p = add_fallback_rules(
                df_base=df_in_DmdW.drop(columns=[key_on, 'Dummy']),
                df_ref=df_in_ProductProfitUpload_temp,
                Item_Product_GROUP_COLUMN=Item_Product_GROUP_COLUMN,
                levels=levels,
                value_cols=measure_cols,
            )
            results.append(base_p)

        # TV/AV/Monitor 외 다른 Product는 그대로 유지
        other_base = df_in_ProductProfitUpload_temp[
            ~df_in_ProductProfitUpload_temp[Item_Product_GROUP_COLUMN].isin(fallback_rules.keys())].copy()

        if not other_base.empty:
            results.append(other_base)

        df_in_DmdW_temp = pd.concat(results, ignore_index=True)

        print_df(df_in_DmdW_temp, 'df_in_DmdW_temp 확인')
        step('=====> STEP 5 End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################
        step('=====> STEP 6 Start : input data machining')

        # 그룹바이 전 컬럼명 변경
        df_in_DmdW_temp = df_in_DmdW_temp.rename(columns={Time_Year_COLUMN: To_Time_Year_COLUMN})


        # df_in_DmdW_temp 그룹바이 진행
        df_in_DmdW_temp = df_in_DmdW_temp.groupby(groupby_cols).apply(agg_func).reset_index()


        # Product_Profit_Profit_Grade 설정을 위한 처리
        # 공통 마스트
        dmdw_tv = df_in_DmdW_temp[Item_Product_GROUP_COLUMN].eq(TV)
        dmdw_av = df_in_DmdW_temp[Item_Product_GROUP_COLUMN].eq(AV)
        dmdw_mnt = df_in_DmdW_temp[Item_Product_GROUP_COLUMN].eq(MONITOR)

        # Item_Definition_COLUMN 데이터 형식에 따르 변수 설정
        definition_str = df_in_DmdW_temp[Item_Definition_COLUMN].astype(str)
        definition_num = pd.to_numeric(definition_str, errors='coerce')

        # 필터 적용을 위한 conditions  지정
        conditions = [
            # ------ TV -----
            dmdw_tv & definition_str.isin([OLED, QLED]),  # TV + OLED/QLED 이면 → A
            dmdw_tv & definition_str.eq(UHD),  # TV + UHD  이면 → B
            dmdw_tv & ~definition_str.isin([OLED, QLED, UHD]),  # TV 그 외는 → C

            # ----- AV -----
            dmdw_av & definition_num.between(8, 9),  # AV + 8 ~ 9 이며 → A
            dmdw_av & definition_num.between(6, 7),  # AV + 6 ~ 7 이며 → B
            dmdw_av & (definition_num <= 5),  # AV + 5 이하 이면  → C

            # ----- MONITOR -----
            dmdw_mnt & definition_str.isin([Gaming, '고해상도']),  # MONITOR + Gaming/고해상도 이면 → A
            dmdw_mnt & definition_str.eq(Main_Stream),  # MONITOR + Main Stream 이면 → B
        ]

        df_in_DmdW_temp[Product_Profit_Product_Grade] = np.select(conditions, choices, default=C)  # 예외는 모두 C

        # 등급 적용 전 데이터 타입 변경
        df_in_DmdW_temp[Product_Profit_C_Profit_Rate] = pd.to_numeric(
            df_in_DmdW_temp[Product_Profit_C_Profit_Rate], errors='coerce')
        # 등급 적용
        df_in_DmdW_temp[Product_Profit_Profit_Grade] = pd.cut(
            df_in_DmdW_temp[Product_Profit_C_Profit_Rate],
            bins=bins,
            labels=labels,
            right=False
        )

        # Product_Profit_Profit_Rank 설정 Product_Profit_Product_Grade + Product_Profit_Profit_Grade
        df_in_DmdW_temp[Product_Profit_Profit_Rank] = df_in_DmdW_temp[Product_Profit_Profit_Grade].astype(str) + \
                                                      df_in_DmdW_temp[Product_Profit_Product_Grade].astype(str)

        # 등급 값 지정
        df_in_DmdW_temp[Product_Profit_Rank] = df_in_DmdW_temp[Product_Profit_Profit_Rank].map(grade_to_rank)

        # output 설정을 위한 column 변경
        df_in_DmdW_temp = df_in_DmdW_temp.rename(columns={
            Product_Profit_Upload_N_Price_Currency: Product_Profit_N_Price_Currency})

        print_df(df_in_DmdW_temp, 'df_in_DmdW_temp 확인 1')

        step('=====> STEP 6 End')

        ################################################################################################################
        # STEP 7 :  input data machining
        ################################################################################################################
        step('=====> STEP 7 Start : input data machining')

        # # concat을 위한 컬럼명 변경
        df_in_ProductProfitUpload_temp = df_in_ProductProfitUpload_temp.rename(
            columns={Product_Profit_Upload_N_Price_Currency: Product_Profit_N_Price_Currency})

        print_df(df_in_ProductProfitUpload_temp, 'df_in_ProductProfitUpload_temp 최종 확인')

        # output 설정
        df_out_ProductProfit = pd.concat([df_in_ProductProfitUpload_temp, df_in_DmdW_temp], axis=0, ignore_index=True)

        # Version 설정
        df_out_ProductProfit[Version_COLUMN] = paramOutVersion

        # 데이터 프레임 순서 설정
        df_out_ProductProfit = df_out_ProductProfit[[
            Version_COLUMN, To_Time_Year_COLUMN, Item_Item_COLUMN, Time_Planning_Month_COLUMN, SALES_DOMAIN_AP2_COLUMN,
            Execution_Version_COLUMN, Product_Profit_N_Price_Currency, Product_Profit_N_Price, Product_Profit_Sales_Qty,
            Product_Profit_C_Profit_Rate, Product_Profit_Product_Grade, Product_Profit_Profit_Grade,
            Product_Profit_Profit_Rank, Product_Profit_Rank
        ]]

        # df_out_ProductProfit = df_out_ProductProfit.drop_duplicates(
        #     subset=[Version_COLUMN, To_Time_Year_COLUMN, Item_Item_COLUMN, Time_Planning_Month_COLUMN,
        #             SALES_DOMAIN_AP2_COLUMN, Execution_Version_COLUMN], keep='first')


        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_ProductProfit, 'df_out_ProductProfit', True)


        print_df(df_out_ProductProfit, 'df_out_ProductProfit', True)


        row_count, col_count = df_out_ProductProfit.shape
        note(f'=====> Final df_out_ProductProfitrows : {row_count} , Columns : {col_count}')


        step('=====> STEP 7 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ProductProfit = pd.DataFrame([], columns=[])


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