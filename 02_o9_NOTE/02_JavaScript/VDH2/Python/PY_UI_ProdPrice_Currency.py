"""
* 프로그램명
    - PY_UI_ProdPrice_Currency

* 내용
    - 입력된 Currency와 Price 기준으로 USD Price를 표기하기 위한 값 계산 (Product Price (EW) 화면)

* 변경이력
    - 2026.03.12 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_RRPPrice    : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_RRP], Measure.[Product Price M_RRP Currency]}) on column where {[Version].[Version Name]};
    - df_in_DPrice      : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_D Price], Measure.[Product Price M_D Price Currency]}) on column where {[Version].[Version Name]};
    - df_in_NPrice      : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_N Price], Measure.[Product Price M_N Price Currency]}) on column where {[Version].[Version Name]};
    - df_in_POPrice     : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_PO Price], Measure.[Product Price M_PO Price Currency]}) on column where {[Version].[Version Name]};
    - df_in_ExchangeRate: Select ([Time].[Planning Month] * [Currency].[Currency] * [Category].[Category] ) on row, ({Measure.[Product Price Currency M_Rate]}) on column where {[Version].[Version Name]};

* Flow Summary
    - STEP1. RRP Price 기준 USD 산출
    - STEP2. D Price 기준 USD 산출
    - STEP3. N Price 기준 USD 산출
    - STEP4. PO Price 기준 USD 산출
    - STEP5. Measure Update

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ThresholdResult

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ProdPrice_Currency] for measures {[Product Price M_RRP USD]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP]  * [Location].[Location] * [Time].[Planning Month] * [Item].[Item] * [Sub Location].[Sub Location] ) on row,
        ({Measure.[Product Price M_D Price USD], Measure.[Product Price M_N Price USD], Measure.[Product Price M_PO Price USD], Measure.[Product Price M_RRP USD]}) on column;

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
str_instance = 'PY_UI_ProdPrice_Currency'
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



def set_unique_combinations(df: pd.DataFrame,
                            weeks_df: pd.DataFrame,
                            columns: list[str]) -> pd.DataFrame:
    """
    df: 실제 데이터
    weeks_df: TIME_WEEK_COLUMN 값(주차) 목록을 가진 데이터프레임(최소 TIME_WEEK_COLUMN 컬럼 필요)
    columns: df에서 완전성 체크할 컬럼들 (TIME_WEEK_COLUMN 포함)
    return: df에 존재하지 않는 (조합×주차) 행들
    """
    if TIME_WEEK_COLUMN not in columns:
        raise ValueError(f"`columns`에는 {TIME_WEEK_COLUMN}가 포함되어야 합니다.")

    dims = [c for c in columns if c != TIME_WEEK_COLUMN]

    # dims 고유 조합 (관측된 조합만 유지)
    unique_dims = df.loc[:, dims].drop_duplicates(ignore_index=True)

    # 주차 고유값
    weeks = (
        weeks_df.loc[:, [TIME_WEEK_COLUMN]]
                .drop_duplicates()[TIME_WEEK_COLUMN]
                .to_numpy()
    )

    n = len(unique_dims)
    m = len(weeks)

    if n == 0 or m == 0:
        return df.loc[:, columns].head(0).copy()

    # (dims 고유조합) × (weeks) 전체 조합 생성
    all_possible = unique_dims.loc[unique_dims.index.repeat(m)].reset_index(drop=True)
    all_possible[TIME_WEEK_COLUMN] = np.tile(weeks, n)

    # df에 실제 존재하는 조합
    existing = df.loc[:, columns].drop_duplicates(ignore_index=True)

    # anti-join: all_possible 중 df에 없는 것만
    out = all_possible.merge(existing, on=columns, how="left", indicator=True)
    out = out.loc[out["_merge"].eq("left_only"), columns].reset_index(drop=True)

    return out


def get_next_week(df, time_column, base_week, offset_weeks=4):
    if time_column not in df.columns:
        raise ValueError(f"컬럼이 없습니다: {time_column}")

    # time 컬럼과 base_week 모두 '정수'로 강제
    s = pd.to_numeric(df[time_column], errors="coerce")
    if s.isna().any():
        bad = df.loc[s.isna(), time_column].head(5).tolist()
        raise ValueError(f"{time_column}에 숫자로 바꿀 수 없는 값이 있습니다. 예: {bad}")

    base_week = int(base_week)

    # 주차 기준 정렬 후, 위치 기반으로 이동
    tmp = df.copy()
    tmp[time_column] = s.astype(int)
    tmp = tmp.sort_values(time_column).reset_index(drop=True)

    matches = tmp.index[tmp[time_column] == base_week].tolist()
    if not matches:
        raise ValueError(f"타겟 주({base_week})가 데이터프레임에 존재하지 않습니다.")

    start_pos = matches[0]
    target_pos = start_pos + int(offset_weeks)

    if target_pos >= len(tmp):
        raise IndexError(
            f"요청한 offset({offset_weeks})가 범위를 벗어났습니다. "
            f"start_pos={start_pos}, len={len(tmp)}"
        )

    return int(tmp.loc[target_pos, time_column])


def process_inventory_sequences(df: pd.DataFrame, sort_cols: list, ascend: list, group_cols: list,
                                nullify_cols: list = None) -> pd.DataFrame:
    """
    Sequence가 1인 행을 복사하여 기본 행(Sequence 0)으로 추가하고
    그룹별로 Sequence를 재할당합니다. (대용량 데이터 대응)
    :param df: 입력 데이터프레임
    :param sort_cols: 정렬 기준 컬럼 리스트
    :param group_cols: 그룹화 기준 컬럼 리스트 (Sequence 재할당용)
    """
    # 1. 정렬
    #   -999 최상위, 0 -> 0순위, 음수 -> 1순위, 양수 -> 2순위
    rank_series = df[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN].astype(float)
    conditions = [
        (rank_series == -999).values,
        (rank_series == 0).values,
        (rank_series < 0).values,
        (rank_series > 0).values,
    ]
    choices = [0, 1, 2, 3] # 정렬 우선순위
    df['priority'] = np.select(conditions, choices, default=99)

    actual_sort_cols = [
        'priority' if col == UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN else col
        for col in sort_cols # 매개변수명인 sort_cols 사용
    ]
    df = df .sort_values(by=actual_sort_cols, ascending=ascend).reset_index(drop=True)
    df.drop(columns=['priority'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 2. 그룹별 Sequence 재할당
    #   1부터 시작하도록 +1
    df[SEQUENCE_COLUMN] = df.groupby(group_cols).cumcount() + 1

    int_columns = [SALES_DOMAIN_AP2_COLUMN, SEQUENCE_COLUMN]
    df[int_columns] = df[int_columns].astype('Int64')

    return df


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

    # 숫자 컬럼: NaN → None (object 변환 필요) -> 숫자컬럼많고 행이 수십만일경우 적용
    # if len(num_cols) > 0:
    #     num_data = df[num_cols].to_numpy(dtype=object, copy=True)
    #     mask = pd.isna(num_data)
    #     num_data[mask] = None
    #     df[num_cols] = num_data

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
            df_in_RRPPrice = read_csv_file("df_in_RRPPrice")
            df_in_DPrice = read_csv_file("df_in_DPrice")
            df_in_NPrice = read_csv_file("df_in_NPrice")
            df_in_POPrice = read_csv_file("df_in_POPrice")
            df_in_ExchangeRate = read_csv_file("df_in_ExchangeRate")

        dataframes = {
            'df_in_RRPPrice': df_in_RRPPrice,
            'df_in_DPrice': df_in_DPrice,
            'df_in_NPrice': df_in_NPrice,
            'df_in_POPrice': df_in_POPrice,
            'df_in_ExchangeRate': df_in_ExchangeRate,
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
        ITEM_COLUMN = 'Item.[Item]'
        CATEGORY_COLUMN = 'Category.[Category]'
        TIME_PLANNUNG_MONTH_COLUMN = 'Time.[Planning Month]'
        CURRENCY_COLUMN = 'Currency.[Currency]'

        PRODUCT_PRICE_M_D_PRICE_COLUMN = 'Product Price M_D Price'
        PRODUCT_PRICE_M_D_PRICE_CURRENCY_COLUMN = 'Product Price M_D Price Currency'
        PRODUCT_PRICE_CURRENCY_M_RATE_COLUMN = 'Product Price Currency M_Rate'
        PRODUCT_PRICE_M_N_PRICE_COLUMN = 'Product Price M_N Price'
        PRODUCT_PRICE_M_N_PRICE_CURRENCY_COLUMN = 'Product Price M_N Price Currency'
        PRODUCT_PRICE_M_PO_PRICE_COLUMN = 'Product Price M_PO Price'
        PRODUCT_PRICE_M_PO_PRICE_CURRENCY_COLUMN = 'Product Price M_PO Price Currency'
        PRODUCT_PRICE_M_RRP_COLUMN = 'Product Price M_RRP'
        PRODUCT_PRICE_M_RRP_CURRENCY_COLUMN = 'Product Price M_RRP Currency'

        PRODUCT_PRICE_M_D_PRICE_USD_COLUMN = 'Product Price M_D Price USD'
        PRODUCT_PRICE_M_N_PRICE_USD_COLUMN = 'Product Price M_N Price USD'
        PRODUCT_PRICE_M_PO_PRICE_USD_COLUMN = 'Product Price M_PO Price USD'
        PRODUCT_PRICE_M_RRP_USD_COLUMN = 'Product Price M_RRP USD'

        version_columns = [VERSION_NAME_COLUMN]

        key_columns = [
            LOCATION_COLUMN, TIME_PLANNUNG_MONTH_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN
        ]

        threshold_result_columns = [
            PRODUCT_PRICE_M_D_PRICE_USD_COLUMN, PRODUCT_PRICE_M_N_PRICE_USD_COLUMN,
            PRODUCT_PRICE_M_PO_PRICE_USD_COLUMN, PRODUCT_PRICE_M_RRP_USD_COLUMN,
        ]

        fn_threshold_result_columns = version_columns + key_columns + threshold_result_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_SyncPlanShort = df_in_SyncPlanShort[df_in_SyncPlanShort[ITEM_COLUMN].isin(['LH32QMRTBGCXZA', 'LH32QMRTBGCXZA', 'LH32QMRTBGCXZA'])]
        # print_df(df_in_SyncPlanShort, 'STEP3 by 0.1  ____ df_in_SyncPlanShort .... filter', True)
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        # if df_in_SyncPlanShort.empty:
        #     raise CustomException("STEP3 ____ df_in_SyncPlanShort 값이 없습니다.")


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : 환율 테이블을 Join하여 USD 값 산출 (RRP USD Price 기준 산출)')

        df_step1 = pd.merge(
            df_in_RRPPrice[
                df_in_RRPPrice[PRODUCT_PRICE_M_RRP_COLUMN].notna() & (df_in_RRPPrice[PRODUCT_PRICE_M_RRP_COLUMN] != '')
            ],
            df_in_ExchangeRate[df_in_ExchangeRate[CATEGORY_COLUMN] == 'Plan'],
            how='inner',
            left_on=[TIME_PLANNUNG_MONTH_COLUMN, PRODUCT_PRICE_M_RRP_CURRENCY_COLUMN],
            right_on=[TIME_PLANNUNG_MONTH_COLUMN, CURRENCY_COLUMN],
        )

        df_step1['rrp_price'] = df_step1[PRODUCT_PRICE_M_RRP_COLUMN] * df_step1[PRODUCT_PRICE_CURRENCY_M_RATE_COLUMN]
        print_df(df_step1, 'STEP4 by 1.1 ____ df_step1 .... merge')

        df_step1 = df_step1[[
            LOCATION_COLUMN, ITEM_COLUMN, TIME_PLANNUNG_MONTH_COLUMN, SUB_LOCATION_COLUMN,
            PRODUCT_PRICE_M_RRP_COLUMN, 'rrp_price'
        ]]
        print_df(df_step1, 'STEP4 by 1.2 ____ df_step1 .... filter')

        step('=====> STEP4 by 1 End')





        step('=====> STEP4 by 2 Start : D USD Price 기준 산출')

        df_step2 = pd.merge(
            df_in_DPrice[
                df_in_DPrice[PRODUCT_PRICE_M_D_PRICE_COLUMN].notna() & (df_in_DPrice[PRODUCT_PRICE_M_D_PRICE_COLUMN] != '')
            ],
            df_in_ExchangeRate[df_in_ExchangeRate[CATEGORY_COLUMN] == 'Plan'],
            how='inner',
            left_on=[TIME_PLANNUNG_MONTH_COLUMN, PRODUCT_PRICE_M_D_PRICE_CURRENCY_COLUMN],
            right_on=[TIME_PLANNUNG_MONTH_COLUMN, CURRENCY_COLUMN],
        )

        df_step2['d_price'] = df_step2[PRODUCT_PRICE_M_D_PRICE_COLUMN] * df_step2[PRODUCT_PRICE_CURRENCY_M_RATE_COLUMN]
        print_df(df_step2, 'STEP4 by 2.1 ____ df_step2 .... merge')

        df_step2 = df_step2[[
            LOCATION_COLUMN, ITEM_COLUMN, TIME_PLANNUNG_MONTH_COLUMN, SUB_LOCATION_COLUMN,
            PRODUCT_PRICE_M_D_PRICE_COLUMN, 'd_price'
        ]]
        print_df(df_step2, 'STEP4 by 2.2 ____ df_step2 .... filter')

        step('=====> STEP4 by 2 End')





        step('=====> STEP4 by 3 Start : N USD Price 기준 산출')

        df_step3 = pd.merge(
            df_in_NPrice[
                df_in_NPrice[PRODUCT_PRICE_M_N_PRICE_COLUMN].notna() & (df_in_NPrice[PRODUCT_PRICE_M_N_PRICE_COLUMN] != '')
            ],
            df_in_ExchangeRate[df_in_ExchangeRate[CATEGORY_COLUMN] == 'Plan'],
            how='inner',
            left_on=[TIME_PLANNUNG_MONTH_COLUMN, PRODUCT_PRICE_M_N_PRICE_CURRENCY_COLUMN],
            right_on=[TIME_PLANNUNG_MONTH_COLUMN, CURRENCY_COLUMN],
        )

        df_step3['n_price'] = df_step3[PRODUCT_PRICE_M_N_PRICE_COLUMN] * df_step3[PRODUCT_PRICE_CURRENCY_M_RATE_COLUMN]
        print_df(df_step3, 'STEP4 by 3.1 ____ df_step3 .... merge', True)

        df_step3 = df_step3[[
            LOCATION_COLUMN, ITEM_COLUMN, TIME_PLANNUNG_MONTH_COLUMN, SUB_LOCATION_COLUMN,
            PRODUCT_PRICE_M_N_PRICE_COLUMN, 'n_price'
        ]]
        print_df(df_step3, 'STEP4 by 3.2 ____ df_step3 .... filter')

        step('=====> STEP4 by 3 End')





        step('=====> STEP4 by 4 Start : PO USD Price 기준 산출')

        df_step4 = pd.merge(
            df_in_POPrice[
                df_in_POPrice[PRODUCT_PRICE_M_PO_PRICE_COLUMN].notna() & (df_in_POPrice[PRODUCT_PRICE_M_PO_PRICE_COLUMN] != '')
            ],
            df_in_ExchangeRate[df_in_ExchangeRate[CATEGORY_COLUMN] == 'Plan'],
            how='inner',
            left_on=[TIME_PLANNUNG_MONTH_COLUMN, PRODUCT_PRICE_M_PO_PRICE_CURRENCY_COLUMN],
            right_on=[TIME_PLANNUNG_MONTH_COLUMN, CURRENCY_COLUMN],
        )

        df_step4['po_price'] = df_step4[PRODUCT_PRICE_M_PO_PRICE_COLUMN] * df_step4[PRODUCT_PRICE_CURRENCY_M_RATE_COLUMN]
        print_df(df_step4, 'STEP4 by 4.1 ____ df_step4 .... merge')

        df_step4 = df_step4[[
            LOCATION_COLUMN, ITEM_COLUMN, TIME_PLANNUNG_MONTH_COLUMN, SUB_LOCATION_COLUMN,
            PRODUCT_PRICE_M_PO_PRICE_COLUMN, 'po_price'
        ]]
        print_df(df_step4, 'STEP4 by 4.2 ____ df_step4 .... filter')

        step('=====> STEP4 by 4 End')



        step('=====> STEP4 by 5 Start : 각 Step 합치기')

        df_ThresholdResult = pd.concat([df_step1, df_step2, df_step3, df_step4], ignore_index=True)
        df_ThresholdResult = df_ThresholdResult.drop_duplicates()
        print_df(df_ThresholdResult, 'STEP4 by 5.1 ____ df_ThresholdResult .... concat')

        df_ThresholdResult.rename(columns={
            'rrp_price': PRODUCT_PRICE_M_RRP_USD_COLUMN,
            'd_price': PRODUCT_PRICE_M_D_PRICE_USD_COLUMN,
            'n_price': PRODUCT_PRICE_M_N_PRICE_USD_COLUMN,
            'po_price': PRODUCT_PRICE_M_PO_PRICE_USD_COLUMN,
        }, inplace=True)
        df_ThresholdResult = df_ThresholdResult[key_columns + threshold_result_columns]
        print_df(df_ThresholdResult, 'STEP4 by 5.2 ____ df_ThresholdResult .... rename')

        int_columns = [
            PRODUCT_PRICE_M_RRP_USD_COLUMN, PRODUCT_PRICE_M_D_PRICE_USD_COLUMN,
            PRODUCT_PRICE_M_N_PRICE_USD_COLUMN, PRODUCT_PRICE_M_PO_PRICE_USD_COLUMN,
        ]
        df_ThresholdResult[int_columns] = (
            df_ThresholdResult[int_columns]
            .round()
            .fillna(0)
            .astype("Int64")
        )
        groupby_columns = [LOCATION_COLUMN, ITEM_COLUMN, TIME_PLANNUNG_MONTH_COLUMN, SUB_LOCATION_COLUMN]
        sum_columns = int_columns
        agg_dict = {col: 'sum' for col in sum_columns}
        df_ThresholdResult = df_ThresholdResult.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)

        step('=====> STEP4 by 5 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_ThresholdResult = rename_and_delete_df(df_ThresholdResult)

        df_out_ThresholdResult[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ThresholdResult = df_out_ThresholdResult[fn_threshold_result_columns].drop_duplicates()
        df_out_ThresholdResult = ultra_fast_replace_to_none(df_out_ThresholdResult)

        dataframes = {
            'df_out_ThresholdResult': df_out_ThresholdResult,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ThresholdResult = pd.DataFrame(columns=fn_threshold_result_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ThresholdResult = pd.DataFrame(columns=fn_threshold_result_columns)
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
