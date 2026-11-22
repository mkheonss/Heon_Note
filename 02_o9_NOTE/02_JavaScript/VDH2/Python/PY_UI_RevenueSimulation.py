"""
* 프로그램명
    - PY_UI_RevenueSimulation

* 내용
    - SEDA에서 과거 실적을 바탕으로 Sales Domain별 expected lead time을 구하고, 이를 바탕으로 GI Qty를 계산하는 로직.

* 변경이력
    - 2025.12.30 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_LTRatioMaster : Select ([Category].[Category] ) on row, ({Measure.[LT Ratio Master_Period]}) on column where {[Version].[Version Name]};
    - df_in_Month         : Select ([Time].[Month].filter(#.Key <= &CurrentMonth.element(0).Key && #.Key >= &CurrentMonth.element(0).LeadOffset(-24).Key) ) on row, () on column;
    - df_in_Week          : Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffSet(-24).Key && #.Key <= &CurrentWeek.element(0).LeadOffSet(60).Key)) on row, () on column;
    - df_in_LastYear      : Select (&CurrentMonth.element(0).LeadOffSet(-12) ) on row, () on column;
    - df_in_Sequence      : Select ([Sequence].[Sequence].filter(#.Name in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"})) on row, () on column;
    - df_in_BLShipTo      : Select ([Time].[Month].filter( (#.Key <= &CurrentMonth.element(0).Key && #.Key >= &CurrentMonth.element(0).LeadOffset(-4).Key) || (#.Key <= &CurrentMonth.element(0).LeadOffset(-10).Key && #.Key >= &CurrentMonth.element(0).LeadOffset(-14).Key) ) * [Sales Domain].[Ship To] * [Sequence].[Sequence] * [Ship To Party].[Ship To Party] ) on row, ({Measure.[GI BL Actual M_GI Qty]}) on column where {[Version].[Version Name]};
    - df_in_GIShipTo      : Select ([Item].[Item] * [Item].[Product Group] * [Time].[Week] * [Sales Domain].[AP2] * [Sales Domain].[Ship To] * [Ship To Party].[Ship To Party] ) on row, ({Measure.[LT Ratio GI W_GI Qty]}) on column where {[Version].[Version Name]};
    - df_in_SiteShipToMap : Select ([Location].[Location] ) on row, ({Measure.[Site AP2 Map_Ship To]}) on column where{[Version].[Version Name], Measure.[Site AP2 Map_Valid Flag] == "Y"};
    - df_in_BODMOD        : Select ([Location].[Location] * [Item].[Product Group] ) on row, ({Measure.[BOD Customer Mode_BOD LT]}) on column where {[Version].[Version Name], Measure.[BOD Customer Mode_Valid Flag] == "Y"};

* Flow Summary
    - STEP0. df_in_BLShipTo, df_in_GIShipTo를 Ship To Party를 제외하고 sum aggregation하여 df_in_BLAcc, df_in_GIAcc 생성.
    - STEP1. LTRatioMaster의 Category와 Period에 따라 df_in_BLShipTo와 df_in_BLAcc의 [Time].[Month]를 조정.
    - STEP2. df_in_BLShipTo와 df_in_BLAcc의 Sales Domain별 수량 (BL Total Qty)을 구함.
    - STEP3. df_in_BLShipTo와 df_in_BLAcc의 Sales Domain, Sequence별 수량 (BL Qty)을 구함.
    - STEP4. df_in_BLShipTo와 df_in_BLAcc의 BL Rate (= BL Qty / Total BL Qty)을 구함.
    - STEP5. df_in_BLShipTo와 df_in_BLAcc를 df_in_GIShipTo와 df_in_GIAcc에 Merge.
    - STEP6. Sequence별 Sales Qty 계산 (= BL Rate * GI Qty)
    - STEP7. 필드 이름 정정.
    - STEP8. Product Group, Ship To 기준으로 Cust BOD 추가

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_LTRatioShipTo
    - df_out_LTRatioAcc
    - df_out_LTRatioShipToW
    - df_out_LTRatioAccW

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_RevenueSimulation] for measures {[LT Ratio Rslt W_GIBLLT Qty]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    -
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
str_instance = 'PY_UI_RevenueSimulation'
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
    # df = pd.read_csv('파일.csv', dtype=str)
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


# def ultra_fast_replace_to_none(df):
#     """NumPy 기반 초고속 변환"""
#     df = df.copy()
#
#     # object 컬럼과 숫자 컬럼 분리
#     obj_cols = df.select_dtypes(include=['object']).columns
#     num_cols = df.select_dtypes(include=['number']).columns
#
#     # 문자열 컬럼 일괄 처리
#     if len(obj_cols) > 0:
#         obj_data = df[obj_cols].values
#         # 조건 마스크 생성
#         mask = (
#             (obj_data == 'nan') |
#             (obj_data == '<NA>') |
#             (obj_data == '0') |
#             pd.isna(obj_data)
#         )
#         df.loc[:, obj_cols] = df.loc[:, obj_cols].mask(mask, None)
#
#     # 숫자 컬럼: NaN → None (object 변환 필요)
#     for col in num_cols:
#         if df[col].isna().any():
#             if pd.api.types.is_integer_dtype(df[col]):
#                 df[col] = df[col].astype('Int64')
#             else:
#                 df[col] = df[col].astype('Float64')
#
#     # 숫자 컬럼: NaN → None (object 변환 필요) -> 숫자컬럼많고 행이 수십만일경우 적용
#     # if len(num_cols) > 0:
#     #     num_data = df[num_cols].to_numpy(dtype=object, copy=True)
#     #     mask = pd.isna(num_data)
#     #     num_data[mask] = None
#     #     df[num_cols] = num_data
#
#     return df

def ultra_fast_replace_to_none(df):
    """dtype를 최대한 유지하면서 문자열 결측 표현과 숫자 결측을 정리한다."""
    df = df.copy()

    # object 컬럼과 숫자 컬럼 분리
    obj_cols = df.select_dtypes(include=["object"]).columns
    num_cols = df.select_dtypes(include=["number"]).columns

    # object 컬럼: 문자열 형태의 결측/특정 값만 None으로 치환
    if len(obj_cols) > 0:
        obj_data = df[obj_cols].to_numpy(dtype=object, copy=True)
        mask = (
            (obj_data == "nan") |
            (obj_data == "<NA>") |
            (obj_data == "0") |
            pd.isna(obj_data)
        )
        obj_data[mask] = None
        df[obj_cols] = obj_data

    # 숫자 컬럼:
    # - int 계열은 nullable integer(Int64)로 바꿔서 dtype 유지
    # - float 계열은 nullable float(Float64)로 바꿔서 dtype 유지
    for col in num_cols:
        if not df[col].isna().any():
            continue

        if pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype("Int64")
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype("Float64")
        else:
            # 숫자처럼 보이지만 object로 들어온 경우 대비
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if pd.api.types.is_integer_dtype(df[col]):
                df[col] = df[col].astype("Int64")
            else:
                df[col] = df[col].astype("Float64")

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
            df_in_LTRatioMaster = read_csv_file("df_in_LTRatioMaster")
            df_in_Month = read_csv_file("df_in_Month")
            df_in_Week = read_csv_file("df_in_Week")
            df_in_LastYear = read_csv_file("df_in_LastYear")
            df_in_Sequence = read_csv_file("df_in_Sequence")
            df_in_BLShipTo = read_csv_file("df_in_BLShipTo")
            df_in_GIShipTo = read_csv_file("df_in_GIShipTo")
            df_in_SiteShipToMap = read_csv_file("df_in_SiteShipToMap")
            df_in_BODMOD = read_csv_file("df_in_BODMOD")


        dataframes = {
            'df_in_LTRatioMaster': df_in_LTRatioMaster,
            'df_in_Month': df_in_Month,
            'df_in_Week': df_in_Week,
            'df_in_LastYear': df_in_LastYear,
            'df_in_Sequence': df_in_Sequence,
            'df_in_BLShipTo': df_in_BLShipTo,
            'df_in_GIShipTo': df_in_GIShipTo,
            'df_in_SiteShipToMap': df_in_SiteShipToMap,
            'df_in_BODMOD': df_in_BODMOD,
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
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_COLUMN = 'Item.[Item]'
        PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        CATEGORY_COLUMN = 'Category.[Category]'
        LT_RATIO_MASTER_PERIOD_COLUMN = 'LT Ratio Master_Period'
        TIME_MONTHKEY_COLUMN = 'Time.[MonthKey]'
        TIME_MONTH_COLUMN = 'Time.[Month]'
        SALES_DEMAIN_ACCOUNT_COLUMN = 'Sales Domain.[Account]'
        SALES_DOMAIN_SHIP_TO_COLUMN = 'Sales Domain.[Ship To]'
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        RELATIVE_WEEK_COLUMN = 'Relative Week.[Relative Week]'
        SHIP_TO_PARTY_COLUMN = 'Ship To Party.[Ship To Party]'

        BL_TOTAL_QTY_COLUMN = 'BL Total Qty'
        BL_QTY_COLUMN = 'BL Qty'
        BL_RATE_COLUMN = 'BL Rate'
        SALES_QTY_COLUMN = 'Sales Qty'
        SITE_AP2_MAP_SHIP_TO = 'Site AP2 Map_Ship To'
        BOD_CUSTOMER_MODE_BOD_LT = 'BOD Customer Mode_BOD LT'

        BL_ACTUAL_M_GIBL_QTY_COLUMN = 'BL Actual M_GIBL Qty'
        GI_BL_ACTUAL_M_GI_QTY_COLUMN = 'GI BL Actual M_GI Qty'
        LT_RATIO_GI_W_GI_QTY_COLUMN = 'LT Ratio GI W_GI Qty'
        LT_RATIO_GI_ACC_W_GI_QTY_COLUMN = 'LT Ratio GI Acc W_GI Qty'

        LT_RATIO_RSLT_W_GI_QTY_COLUMN = 'LT Ratio Rslt W_GI Qty'
        LT_RATIO_RSLT_W_BL_QTY_COLUMN = 'LT Ratio Rslt W_BL Qty'
        LT_RATIO_RSLT_W_GIBLLT_QTY_COLUMN = 'LT Ratio Rslt W_GIBLLT Qty'
        LT_RATIO_RSLT_W_GIBLLT_RATE_COLUMN = 'LT Ratio Rslt W_GIBLLT Rate'
        LT_RATIO_RSLT_W_SMOOTHING_QTY_COLUMN = 'LT Ratio Rslt W_Smoothing Qty'

        LT_RATIO_RSLT_ACC_W_GIBLLT_QTY_COLUMN = 'LT Ratio Rslt Acc W_GIBLLT Qty'
        LT_RATIO_RSLT_ACC_W_GIBLLT_RATE_COLUMN = 'LT Ratio Rslt Acc W_GIBLLT Rate'
        LT_RATIO_RSLT_ACC_W_SMOOTHING_QTY_COLUMN = 'LT Ratio Rslt Acc W_Smoothing Qty'
        LT_RATIO_RSLT_ACC_W_GI_QTY_COLUMN = 'LT Ratio Rslt Acc W_GI Qty'
        LT_RATIO_RSLT_ACC_W_BL_QTY_COLUMN = 'LT Ratio Rslt Acc W_BL Qty'
        LT_RATIO_GI_ACC_W_CUST_BOD = 'LT Ratio GI Acc W_Cust BOD'
        LT_RATIO_GI_W_CUST_BOD = 'LT Ratio GI W_Cust BOD'

        CATEGORY_LIST = ['Last Month', 'Seasonality']

        version_columns = [VERSION_NAME_COLUMN]

        lt_ratio_ship_to_key_columns = [
            SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, SHIP_TO_PARTY_COLUMN, CATEGORY_COLUMN,
            TO_TIME_TO_WEEK_COLUMN, RELATIVE_WEEK_COLUMN
        ]
        lt_ratio_ship_to_columns = [
            LT_RATIO_RSLT_W_GI_QTY_COLUMN, LT_RATIO_RSLT_W_BL_QTY_COLUMN, LT_RATIO_RSLT_W_GIBLLT_QTY_COLUMN,
            LT_RATIO_RSLT_W_GIBLLT_RATE_COLUMN, LT_RATIO_RSLT_W_SMOOTHING_QTY_COLUMN,
        ]

        lt_ratio_acc_key_columns = [
            SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_TIME_TO_WEEK_COLUMN, CATEGORY_COLUMN,
            RELATIVE_WEEK_COLUMN,
        ]
        lt_ratio_acc_columns = [
            LT_RATIO_RSLT_ACC_W_GI_QTY_COLUMN, LT_RATIO_RSLT_ACC_W_BL_QTY_COLUMN, LT_RATIO_RSLT_ACC_W_GIBLLT_QTY_COLUMN,
            LT_RATIO_RSLT_ACC_W_GIBLLT_RATE_COLUMN, LT_RATIO_RSLT_ACC_W_SMOOTHING_QTY_COLUMN,
        ]

        lt_ratio_ship_to_w_key_columns = [
            SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, SHIP_TO_PARTY_COLUMN,
        ]
        lt_ratio_ship_to_w_columns = [
            LT_RATIO_GI_W_CUST_BOD,
        ]

        lt_ratio_acc_w_key_columns = [
            SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN,
        ]
        lt_ratio_acc_w_columns = [
            LT_RATIO_GI_ACC_W_CUST_BOD,
        ]

        fn_lt_ratio_ship_to_columns = version_columns + lt_ratio_ship_to_key_columns + lt_ratio_ship_to_columns
        fn_lt_ratio_acc_columns = version_columns + lt_ratio_acc_key_columns + lt_ratio_acc_columns

        fn_lt_ratio_ship_to_w_columns = version_columns + lt_ratio_ship_to_w_key_columns + lt_ratio_ship_to_w_columns
        fn_lt_ratio_acc_w_columns = version_columns + lt_ratio_acc_w_key_columns + lt_ratio_acc_w_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[LOCATION_COLUMN] == 'P306']
        # print_df(df_in_BODProdSET, 'STEP3 by 1.1  ____ df_in_BODProdSET .... filter', True)
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[SUB_LOCATION_COLUMN] == 'L5N0']
        # df_in_GIShipTo = df_in_GIShipTo[df_in_GIShipTo[ITEM_COLUMN] == 'HW-LS60D/ZD']

        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_LTRatioMaster.empty:
            raise CustomException("STEP3 by 0 ____ df_in_LTRatioMaster 값이 없습니다.")


        # week 필터
        df_in_Week = df_in_Week[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)

        # Month 필터
        df_in_Month = df_in_Month[[TIME_MONTH_COLUMN]].drop_duplicates().reset_index(drop=True)
        print_df(df_in_Month, 'STEP3 by 0.1  ____ df_in_Month .... month uniqe')

        # # LastYear 필터
        # df_in_LastYear = df_in_LastYear[[TIME_MONTH_COLUMN]].drop_duplicates().reset_index(drop=True)
        # print_df(df_in_LastYear, 'STEP3 by 0.2  ____ df_in_LastYear .... month uniqe')

        # last year month
        last_year_month = get_first_value(df_in_LastYear, TIME_MONTH_COLUMN)
        step(f'=====> last_year_month : {last_year_month}')


        step('=====> STEP3 by 1 Start : df_in_BLShipTo, df_in_BLAcc 각각을 sum aggregation하여 df_BLShipTo, df_BLAcc를 만든다.')
        groupby_columns = [TIME_MONTH_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, SEQUENCE_COLUMN]
        agg_dict = {
            GI_BL_ACTUAL_M_GI_QTY_COLUMN: 'sum'
        }
        df_in_BLAcc = df_in_BLShipTo.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)

        print_df(df_in_BLAcc, 'STEP3 by 1.1  ____ df_in_BLAcc .... groupby')

        groupby_columns = [ITEM_COLUMN, PRODUCT_GROUP_COLUMN, TIME_WEEK_COLUMN, SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN]
        agg_dict = {
            LT_RATIO_GI_W_GI_QTY_COLUMN: 'sum'
        }
        df_in_GIAcc = df_in_GIShipTo.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_in_GIAcc.rename(columns={
            LT_RATIO_GI_W_GI_QTY_COLUMN: LT_RATIO_GI_ACC_W_GI_QTY_COLUMN
        }, inplace=True)

        print_df(df_in_GIAcc, 'STEP3 by 1.2  ____ df_in_GIAcc .... groupby')

        step('=====> STEP3 by 1 End')

        step('=====> STEP3 End')


        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 0 Start : df_in_BLShipTo, df_in_BLAcc 각각을 df_in_LTRatioMaster 와 cross join 한다.')
        # 예를 들어, df_in_BLShipTo 의 row가 6개, df_in_LTRatioMaster 의 row가 2개라면 cross joint 한 결과 총 12 (=6 * 2)개가 나와야한다.
        # 1. Cross Join 수행
        df_in_BLShipTo = pd.merge(df_in_BLShipTo, df_in_LTRatioMaster, how='cross')
        df_in_BLShipTo = df_in_BLShipTo[[
            CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, TIME_MONTH_COLUMN, SEQUENCE_COLUMN, SHIP_TO_PARTY_COLUMN,
            GI_BL_ACTUAL_M_GI_QTY_COLUMN, LT_RATIO_MASTER_PERIOD_COLUMN,
        ]]
        print_df(df_in_BLShipTo, 'STEP4 by 0.1  ____ df_in_BLShipTo .... cross join')

        df_in_BLAcc = pd.merge(df_in_BLAcc, df_in_LTRatioMaster, how='cross')
        df_in_BLAcc = df_in_BLAcc[[
            CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, TIME_MONTH_COLUMN, SEQUENCE_COLUMN,
            GI_BL_ACTUAL_M_GI_QTY_COLUMN, LT_RATIO_MASTER_PERIOD_COLUMN,
        ]]
        print_df(df_in_BLAcc, 'STEP4 by 0.2  ____ df_in_BLAcc .... cross join')
        step('=====> STEP4 by 0 End')



        step('=====> STEP4 by 1 Start : df_in_BLShipTo 와 df_in_BLAcc 테이블에 [Category].[Category] 필드를 만들고 df_in_LTRatioMaster 의 [Category].[Category] 값을 넣는다.')
        # Case1. [Category].[Category] = "Last Month"
        #   df_in_BLShipTo, df_in_BLAcc의 [Time].[Month]가 df_in_Month 테이블 밑에서 첫 번째 ~ [LT Ratio Master_Period] 번째 [Time].[Month]들에 해당하지 않으면 row를 삭제한다.
        #   예를 들어, [LT Ratio Master_Period] = 5, df_in_Month 맨 밑의 값 [Time].[Month] = 202511 라면, df_in_BLShipTo와 df_in_BLAcc 테이블의 [Time].[Month]가 202511, 202510, 202509, 202508, 202507이 아닌 row를 삭제한다.
        def filter_bl_by_lt_case1(df_month, df_bl, category_name):
            """
            LT Ratio에 따라 시작 월을 계산하고, 해당 기간 내의 데이터만 필터링.

            :param df_month: 월 마스터 데이터프레임
            :param df_bl: 필터링할 대상 데이터프레임
            :return: 필터링된 데이터프레임
            """
            # 1. 월 리스트 및 정보 추출
            month_list = df_month[TIME_MONTH_COLUMN].tolist()
            total_months = len(month_list)
            last_month = month_list[-1]

            # 2. LT Ratio별 시작 월 매핑 사전 생성 (최적화)
            unique_lt_ratios = df_bl[LT_RATIO_MASTER_PERIOD_COLUMN].unique()
            lt_to_start_month = {
                lt: month_list[max(0, total_months - int(lt))]
                for lt in unique_lt_ratios
            }

            # 3. 임시 컬럼 생성 및 필터링
            result_df = df_bl[df_bl[CATEGORY_COLUMN] == category_name].copy()
            result_df['calculated_start_month'] = result_df[LT_RATIO_MASTER_PERIOD_COLUMN].map(lt_to_start_month)

            # 4. 불리언 인덱싱으로 필터링
            condition = (
                (result_df[TIME_MONTH_COLUMN] >= result_df['calculated_start_month']) &
                (result_df[TIME_MONTH_COLUMN] <= last_month)
            )

            return result_df.loc[condition].drop(columns=['calculated_start_month'])

        # df_BLShipTo_1
        df_BLShipTo_1 = filter_bl_by_lt_case1(
            df_in_Month,
            df_in_BLShipTo,
            CATEGORY_LIST[0],
        )

        selected_columns = [
            CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, TIME_MONTH_COLUMN, SEQUENCE_COLUMN,
            SHIP_TO_PARTY_COLUMN, GI_BL_ACTUAL_M_GI_QTY_COLUMN, LT_RATIO_MASTER_PERIOD_COLUMN,
        ]
        df_BLShipTo_1 = df_BLShipTo_1[selected_columns]
        print_df(df_BLShipTo_1, 'STEP4 by 1.1.1  ____ df_BLShipTo_1 .... filter')

        # df_BLAcc_1
        df_BLAcc_1 = filter_bl_by_lt_case1(
            df_in_Month,
            df_in_BLAcc,
            CATEGORY_LIST[0],
        )

        selected_columns = [
            CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, TIME_MONTH_COLUMN, SEQUENCE_COLUMN,
            GI_BL_ACTUAL_M_GI_QTY_COLUMN, LT_RATIO_MASTER_PERIOD_COLUMN,
        ]
        df_BLAcc_1 = df_BLAcc_1[selected_columns]
        print_df(df_BLAcc_1, 'STEP4 by 1.1.2  ____ df_BLAcc_1 .... filter')



        # Case2. [Category].[Category] = "Seasonality"
        #   df_in_BLShipTom df_in_BLAcc의 [Time].[Month]가 df_in_Month에서 df_in_LastYear을 중심으로 위/아래 ( Measure.[LT Ratio Master_Period] - 1 ) / 2 번째 [Time].[Month]들에 해당하지 않으면 row를 삭제한다.
        #   예를 들어, Measure.[LT Ratio Master_Period] = 5, df_in_LastYear=202411 이면, df_in_BLShipTo, df_in_BLAcc 테이블의 [Time].[Month]가 202409, 202410, 202411, 202412, 202501이 아닌 row를 삭제한다.
        #   c.f. Measure.[LT Ratio Master_Period]는 항상 홀수, df_in_LastYear는 df_in_Month 밑에서 13번째 값.
        def filter_bl_by_lt_case2(df_month, df_bl, category_name):
            """
            LT Ratio에 따른 Month 범위를 계산하여 df_bl 데이터를 필터링

            :param df_month: 월 마스터 데이터프레임
            :param df_bl: 필터링할 대상 데이터프레임
            :return: 필터링된 데이터프레임
            """
            df_bl_temp = df_bl[df_bl[CATEGORY_COLUMN] == category_name].copy()
            # print_df(df_bl_temp, 'STEP4 by 1.2.0  ____ df_bl_temp .... filter')

            # 1. 기준 정보 및 Month 리스트 준비
            month_list = df_month[TIME_MONTH_COLUMN].tolist()

            try:
                base_idx = month_list.index(last_year_month)
            except ValueError:
                raise ValueError(f"last_year_month {last_year_month} 가 df_in_Month 에 존재하지 않습니다.")

            # 2. LT Ratio Master_Period별로 Month 범위를 계산한 '룩업 테이블' 생성
            # A에 존재하는 모든 LT 값 추출
            unique_lts = df_bl_temp[LT_RATIO_MASTER_PERIOD_COLUMN].unique()

            lookup_data = []
            for lt in unique_lts:
                lt_val = int(lt)
                # lt_val = (lt_val - 1) // 2 if lt_val % 2 == 0 else lt_val
                # lt_val = int(round((lt_val - 1) / 2)) if lt_val % 2 == 0 else lt_val
                lt_val = int(round((lt_val - 1) / 2))

                lower_idx = base_idx - lt_val
                upper_idx = base_idx + lt_val
                # step(f'==============> lt : {lt}, upper_idx : {upper_idx}, lower_idx : {lower_idx}')

                # 인덱스 범위 유효성 체크 후 Month 값 할당
                upper_m = month_list[upper_idx] if 0 <= upper_idx < len(month_list) else None
                lower_m = month_list[lower_idx] if 0 <= lower_idx < len(month_list) else None
                # step(f'==============> upper_m : {upper_m}, lower_m : {lower_m}')

                lookup_data.append({
                    LT_RATIO_MASTER_PERIOD_COLUMN: lt,
                    'upper_limit_month': upper_m,
                    'lower_limit_month': lower_m,
                })

            if not lookup_data:
                lookup_data.append({
                    LT_RATIO_MASTER_PERIOD_COLUMN: None,
                    'upper_limit_month': None,
                    'lower_limit_month': None,
                })

            lookup_df = pd.DataFrame(lookup_data)
            # print_df(lookup_df, 'STEP4 by 1.2.0.1  ____ lookup_df .... filter')

            # 3. Main 데이터프레임과 룩업 테이블 병합 (Join)
            result_df = df_bl_temp.merge(lookup_df, on=LT_RATIO_MASTER_PERIOD_COLUMN, how='left')
            # print_df(result_df, 'STEP4 by 1.2.0.2  ____ result_df .... filter', True)

            # 4. 벡터화된 비교 연산으로 필터링
            #   None(범위 초과)인 경우를 대비해 fillna 처리 혹은 조건문 적용
            result_df = result_df[
                (result_df['upper_limit_month'].notnull()) &
                (result_df['lower_limit_month'].notnull()) &
                (result_df[TIME_MONTH_COLUMN] <= result_df['upper_limit_month']) &
                (result_df[TIME_MONTH_COLUMN] >= result_df['lower_limit_month'])
            ].copy()

            return result_df.drop(columns=['upper_limit_month', 'lower_limit_month'])

        # df_BLShipTo_2
        df_BLShipTo_2 = filter_bl_by_lt_case2(
            df_in_Month,
            df_in_BLShipTo,
            CATEGORY_LIST[1],
        )
        selected_columns = [
            CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, TIME_MONTH_COLUMN, SEQUENCE_COLUMN,
            SHIP_TO_PARTY_COLUMN, GI_BL_ACTUAL_M_GI_QTY_COLUMN, LT_RATIO_MASTER_PERIOD_COLUMN,
        ]
        df_BLShipTo_2 = df_BLShipTo_2[selected_columns]
        print_df(df_BLShipTo_2, 'STEP4 by 1.2.1  ____ df_BLShipTo_2 .... filter')

        # df_BLAcc_2
        df_BLAcc_2 = filter_bl_by_lt_case2(
            df_in_Month,
            df_in_BLAcc,
            CATEGORY_LIST[1],
        )
        selected_columns = [
            CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, TIME_MONTH_COLUMN, SEQUENCE_COLUMN,
            GI_BL_ACTUAL_M_GI_QTY_COLUMN, LT_RATIO_MASTER_PERIOD_COLUMN,
        ]
        df_BLAcc_2 = df_BLAcc_2[selected_columns]
        print_df(df_BLAcc_2, 'STEP4 by 1.2.2  ____ df_BLAcc_2 .... filter')

        df_BLShipTo = pd.concat([df_BLShipTo_1, df_BLShipTo_2], ignore_index=True)
        print_df(df_BLShipTo, 'STEP4 by 1.2.3  ____ df_BLShipTo .... concat')

        df_BLAcc = pd.concat([df_BLAcc_1, df_BLAcc_2], ignore_index=True)
        print_df(df_BLAcc, 'STEP4 by 1.2.4  ____ df_BLAcc .... concat')
        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : df_in_BLShipTo, df_in_BLAcc 을 각각 df_BLShipTo, df_BLAcc 로 복사한다')
        # 1. df_BLShipTo을 [Category].[Category], [Sales Domain].[Ship To], [Ship To Party].[Ship To Party] 기준으로 Sum Aggregation해서 얻은 GI BL Actual M_GI Qty를 BL Total Qty로 명명한다.
        #       BL Total Qty = Sum(GI BL Actual M_GI Qty)
        # 2. df_BLAcc을 [Category].[Category], [Sales Domain].[Ship To] 기준으로 Sum Aggregation해서 얻은 GI BL Actual M_GI Qty를 BL Total Qty로 명명한다.
        #       BL Total Qty = Sum(GI BL Actual M_GI Qty)

        int_columns = [GI_BL_ACTUAL_M_GI_QTY_COLUMN]
        for column in int_columns:
            df_BLShipTo[column] = df_BLShipTo[column].fillna(0).astype(float)
            df_BLAcc[column] = df_BLAcc[column].fillna(0).astype(float)

        groupby_columns = [CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, SHIP_TO_PARTY_COLUMN]
        sum_columns = int_columns
        agg_dict = {col: 'sum' for col in sum_columns}
        df_BLShipTo_step2 = df_BLShipTo.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_BLShipTo_step2.rename(columns={
            GI_BL_ACTUAL_M_GI_QTY_COLUMN: BL_TOTAL_QTY_COLUMN,
        }, inplace=True)
        print_df(df_BLShipTo_step2, 'STEP4 by 2.1  ____ df_BLShipTo_step2 .... groupby')

        groupby_columns = [CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN]
        df_BLAcc_step2 = df_BLAcc.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_BLAcc_step2.rename(columns={
            GI_BL_ACTUAL_M_GI_QTY_COLUMN: BL_TOTAL_QTY_COLUMN,
        }, inplace=True)
        print_df(df_BLAcc_step2, 'STEP4 by 2.2  ____ df_BLAcc_step2 .... groupby')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : BL Qty create')
        # 1. df_in_BLShipTo 을 [Category].[Category], [Sales Domain].[Ship To], [Ship To Party].[Ship To Party], [Sequence].[Sequence] 기준으로 Sum Aggregation해서 얻은 GI BL Actual M_GI Qty를 BL Qty로 명명한다
        #       BL Qty = Sum(GI BL Actual M_GI Qty)
        # 2. df_in_BLAcc 을  [Category].[Category], [Sales Domain].[Ship To], [Sequence].[Sequence] 기준으로 Sum Aggregation해서 얻은 GI BL Actual M_GI Qty를 BL Qty로 명명한다.
        #       BL Qty = Sum(GI BL Actual M_GI Qty)

        groupby_columns = [CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, SHIP_TO_PARTY_COLUMN, SEQUENCE_COLUMN]
        sum_columns = int_columns
        agg_dict = {col: 'sum' for col in sum_columns}
        df_BLShipTo_step3 = df_BLShipTo.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_BLShipTo_step3.rename(columns={
            GI_BL_ACTUAL_M_GI_QTY_COLUMN: BL_QTY_COLUMN,
        }, inplace=True)
        print_df(df_BLShipTo_step3, 'STEP4 by 3.1  ____ df_BLShipTo_step3 .... groupby')

        groupby_columns = [CATEGORY_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, SEQUENCE_COLUMN]
        df_BLAcc_step3 = df_BLAcc.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_BLAcc_step3.rename(columns={
            GI_BL_ACTUAL_M_GI_QTY_COLUMN: BL_QTY_COLUMN,
        }, inplace=True)
        print_df(df_BLAcc_step3, 'STEP4 by 3.2  ____ df_BLAcc_step3 .... groupby')
        step('=====> STEP4 by 3 End')



        step('=====> STEP4 by 4 Start : BL Rate create')
        # 1. df_in_BLShipTo 을 기준으로 [Sales Domain].[Ship To], [Ship To Party].[Ship To Party] 에 따라 df_BLShipTo 의 [BL Total Qty]을 Merge (inner join)하여 BL Rate을 구한다.
        #       BL Rate = BL Qty / BL Total Qty
        # 2. df_in_BLAcc 을 기준으로 [Sales Domain].[Ship To]에 따라 df_BLAcc의 [BL Total Qty] 을 Merge (inner join)하여 BL Rate을 구한다.
        #       BL Rate = BL Qty / BL Total Qty

        df_BLShipTo_step4 = pd.merge(df_BLShipTo_step2, df_BLShipTo_step3, on=[SALES_DOMAIN_SHIP_TO_COLUMN, SHIP_TO_PARTY_COLUMN, CATEGORY_COLUMN], how='inner')
        print_df(df_BLShipTo_step4, 'STEP4 by 4.1.1  ____ df_BLShipTo_step4 .... merge')

        # 분모가 NaN인 경우를 대비해 fill_value 사용
        df_BLShipTo_step4[BL_RATE_COLUMN] = df_BLShipTo_step4[BL_QTY_COLUMN].div(df_BLShipTo_step4[BL_TOTAL_QTY_COLUMN], fill_value=0)
        print_df(df_BLShipTo_step4, 'STEP4 by 4.1.2  ____ df_BLShipTo_step4 .... div')

        df_BLAcc_step4 = pd.merge(df_BLAcc_step2, df_BLAcc_step3, on=[SALES_DOMAIN_SHIP_TO_COLUMN, CATEGORY_COLUMN], how='inner')
        print_df(df_BLAcc_step4, 'STEP4 by 4.2.1  ____ df_BLAcc_step4 .... merge')

        df_BLAcc_step4[BL_RATE_COLUMN] = df_BLAcc_step4[BL_QTY_COLUMN].div(df_BLAcc_step4[BL_TOTAL_QTY_COLUMN], fill_value=0)
        print_df(df_BLAcc_step4, 'STEP4 by 4.2.2  ____ df_BLAcc_step4 .... div')
        step('=====> STEP4 by 4 End')


        step('=====> STEP4 by 5 Start : df_GIShipTo, df_GIAcc 생성')
        # df_in_GIShipTo 을 기준으로 [Sales Domain].[Ship To], [Ship To Party].[Ship To Party]에 따라 df_in_BLShipTo, df_in_BLAcc 의 [Category].[Category], [Sequence].[Sequence], BL Qty, BL Total Qty, BL Rate을 각각 Merge (left join)한다.
        # df_in_GIAcc 을 기준으로 [Sales Domain].[Ship To]에 따라 df_in_BLShipTo, df_in_BLAcc 의 [Category].[Category], [Sequence].[Sequence], BL Qty, BL Total Qty, BL Rate을 각각 Merge (left join)한다.

        df_in_GIShipTo = pd.merge(df_in_GIShipTo, df_in_Sequence, how='cross')

        df_GIShipTo = df_in_GIShipTo.merge(
            df_BLShipTo_step4[[SALES_DOMAIN_SHIP_TO_COLUMN, SHIP_TO_PARTY_COLUMN, CATEGORY_COLUMN, BL_TOTAL_QTY_COLUMN]], how='left',
            left_on=[SALES_DOMAIN_AP2_COLUMN, SHIP_TO_PARTY_COLUMN],
            right_on=[SALES_DOMAIN_SHIP_TO_COLUMN, SHIP_TO_PARTY_COLUMN],
        ).drop_duplicates()
        df_GIShipTo.drop(columns=[SALES_DOMAIN_SHIP_TO_COLUMN+'_y'], inplace=True)
        df_GIShipTo.rename(columns={SALES_DOMAIN_SHIP_TO_COLUMN+'_x': SALES_DOMAIN_SHIP_TO_COLUMN}, inplace=True)

        df_GIShipTo = df_GIShipTo.merge(
            df_BLShipTo_step4[[SALES_DOMAIN_SHIP_TO_COLUMN, SHIP_TO_PARTY_COLUMN, SEQUENCE_COLUMN, CATEGORY_COLUMN, BL_QTY_COLUMN, BL_RATE_COLUMN]], how='left',
            left_on=[SALES_DOMAIN_AP2_COLUMN, SHIP_TO_PARTY_COLUMN, SEQUENCE_COLUMN, CATEGORY_COLUMN],
            right_on=[SALES_DOMAIN_SHIP_TO_COLUMN, SHIP_TO_PARTY_COLUMN, SEQUENCE_COLUMN, CATEGORY_COLUMN],
        )

        df_GIShipTo.drop(columns=[SALES_DOMAIN_SHIP_TO_COLUMN+'_y'], inplace=True)
        df_GIShipTo.rename(columns={SALES_DOMAIN_SHIP_TO_COLUMN+'_x': SALES_DOMAIN_SHIP_TO_COLUMN}, inplace=True)

        #df_GIShipTo[BL_QTY_COLUMN] = df_GIShipTo[BL_QTY_COLUMN].fillna(0)
        #df_GIShipTo[BL_RATE_COLUMN] = df_GIShipTo[BL_RATE_COLUMN].fillna(0)

        print_df(df_GIShipTo, 'STEP4 by 5.1  ____ df_GIShipTo .... merge')

        df_in_GIAcc = pd.merge(df_in_GIAcc, df_in_Sequence, how='cross')

        df_GIAcc = df_in_GIAcc.merge(
            df_BLAcc_step4[[SALES_DOMAIN_SHIP_TO_COLUMN, CATEGORY_COLUMN, BL_TOTAL_QTY_COLUMN]], how='left',
            left_on=[SALES_DOMAIN_AP2_COLUMN],
            right_on=[SALES_DOMAIN_SHIP_TO_COLUMN],
        ).drop_duplicates()
        df_GIAcc.drop(columns=[SALES_DOMAIN_SHIP_TO_COLUMN+'_y'], inplace=True)
        df_GIAcc.rename(columns={SALES_DOMAIN_SHIP_TO_COLUMN+'_x': SALES_DOMAIN_SHIP_TO_COLUMN}, inplace=True)

        df_GIAcc = df_GIAcc.merge(
            df_BLAcc_step4[[SALES_DOMAIN_SHIP_TO_COLUMN, SEQUENCE_COLUMN, CATEGORY_COLUMN, BL_QTY_COLUMN, BL_RATE_COLUMN]], how='left',
            left_on=[SALES_DOMAIN_AP2_COLUMN, SEQUENCE_COLUMN, CATEGORY_COLUMN],
            right_on=[SALES_DOMAIN_SHIP_TO_COLUMN, SEQUENCE_COLUMN, CATEGORY_COLUMN],
        )
        df_GIAcc.drop(columns=[SALES_DOMAIN_SHIP_TO_COLUMN+'_y'], inplace=True)
        df_GIAcc.rename(columns={SALES_DOMAIN_SHIP_TO_COLUMN+'_x': SALES_DOMAIN_SHIP_TO_COLUMN}, inplace=True)

        #df_GIAcc[BL_QTY_COLUMN] = df_GIAcc[BL_QTY_COLUMN].fillna(0)
        #df_GIAcc[BL_RATE_COLUMN] = df_GIAcc[BL_RATE_COLUMN].fillna(0)

        print_df(df_GIAcc, 'STEP4 by 5.2  ____ df_GIAcc .... merge')

        step('=====> STEP4 by 5 End')



        step('=====> STEP4 by 6 Start : Sales Qty 및')
        # 1. df_in_GIShipTo, df_in_GIAcc의 row 별로 [To Time].[To Week] = [Time].[Week] + [Sequence].[Sequence]를 구한다.
        #       df_in_Week 에서 [Time].[Week]의 row 번호(n) 찾기.
        #       df_in_Week 에서 n + [Sequence].[Sequence]번째 row를 [To Time].[To Week]으로 사용.
        # 2. df_in_GIShipTo, df_in_GIAcc 의 row 별로 Sales Qty를 구한다.
        #       Sales Qty = LT Ratio GI W_GI Qty * BL Rate
        # 3. [Sequence].[Sequence] 앞에 'W' 혹은 'W0'를 붙이고, [Relative Week].[Relative Week] 로 필드명 수정.
        #       [Sequence].[Sequence]가 한자리 숫자면 앞에 'W0'을 붙임.   예를 들어, [Sequence].[Sequence] = 4면, [Relative Week].[Relative Week] = W04
        #       [Sequence].[Sequence]가 한자리 숫자가 아니라면 앞에 'W'을 붙임.   예를 들어, [Sequence].[Sequence] = 13면, [Relative Week].[Relative Week] = W13
        #       [Sequence].[Sequence] 필드 제거

        def generator_col(df_week: pd.DataFrame, df_bl: pd.DataFrame, qty_col: str, rate_col: str):
            """
            컬럼 generator

            :param df_week: 주차 마스터 데이터프레임
            :param df_bl: generator 대상 데이터프레임
            :param qty_col: 계산에 사용할 Qty 컬럼명
            :param rate_col: 계산에 사용할 Rate 컬럼명
            :return: 계산이 완료된 데이터프레임
            """
            # 1. Relative Week 생성
            df_bl[RELATIVE_WEEK_COLUMN] = 'W' + df_bl[SEQUENCE_COLUMN].astype(str).str.zfill(2)

            # 2. To Week 계산
            #   df_in_Week의 인덱스를 n으로 활용
            df_week_indexed = df_week[[TIME_WEEK_COLUMN]].copy().reset_index(drop=True)
            df_week_indexed['n'] = df_week_indexed.index

            # [A] 현재 Week의 인덱스(n)를 df_bl에 병합
            df_bl = pd.merge(
                df_bl,
                df_week_indexed.rename(columns={'n': '_current_n'}),
                on=TIME_WEEK_COLUMN,
                how='left'
            )
            # print_df(df_bl, 'STEP4 by 6.1.1  ____ df_bl .... merge')

            # [B] target_n 계산 (n + sequence)
            df_bl['_target_n'] = df_bl['_current_n'] + df_bl[SEQUENCE_COLUMN].fillna(0).astype(int)

            # [C] target_n을 사용하여 df_in_Week의 Week 값을 가져옴 (다시 병합)
            df_bl = pd.merge(
                df_bl,
                df_week_indexed.rename(columns={TIME_WEEK_COLUMN: TO_TIME_TO_WEEK_COLUMN, 'n': '_target_n'}),
                on='_target_n',
                how='left'
            )
            df_bl[TO_TIME_TO_WEEK_COLUMN] = df_bl[TO_TIME_TO_WEEK_COLUMN].astype('Int64')

            # 임시 계산 컬럼 삭제
            df_bl.drop(columns=['_current_n', '_target_n'], inplace=True)

            # 3. Sales Qty 계산 (Vectorized)
            df_bl[SALES_QTY_COLUMN] = df_bl[qty_col] * df_bl[rate_col]

            return df_bl

        # df_GIShipTo
        df_GIShipTo = generator_col(
            df_week=df_in_Week,
            df_bl=df_GIShipTo,
            qty_col=LT_RATIO_GI_W_GI_QTY_COLUMN,
            rate_col=BL_RATE_COLUMN,
        )

        select_columns = [
            SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, PRODUCT_GROUP_COLUMN, TIME_WEEK_COLUMN, SHIP_TO_PARTY_COLUMN, CATEGORY_COLUMN,
            LT_RATIO_GI_W_GI_QTY_COLUMN, RELATIVE_WEEK_COLUMN, BL_QTY_COLUMN, BL_TOTAL_QTY_COLUMN, BL_RATE_COLUMN,
            TO_TIME_TO_WEEK_COLUMN, SALES_QTY_COLUMN,
        ]
        df_GIShipTo = df_GIShipTo[select_columns]

        print_df(df_GIShipTo, 'STEP4 by 6.1  ____ df_GIShipTo .... select')


        # df_GIAcc
        df_GIAcc = generator_col(
            df_week=df_in_Week,
            df_bl=df_GIAcc,
            qty_col=LT_RATIO_GI_ACC_W_GI_QTY_COLUMN,
            rate_col=BL_RATE_COLUMN,
        )

        select_columns = [
            SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, PRODUCT_GROUP_COLUMN, TIME_WEEK_COLUMN, CATEGORY_COLUMN,
            LT_RATIO_GI_ACC_W_GI_QTY_COLUMN, RELATIVE_WEEK_COLUMN, BL_QTY_COLUMN, BL_TOTAL_QTY_COLUMN, BL_RATE_COLUMN,
            TO_TIME_TO_WEEK_COLUMN, SALES_QTY_COLUMN,
        ]
        df_GIAcc = df_GIAcc[select_columns]

        print_df(df_GIAcc, 'STEP4 by 6.2  ____ df_GIAcc .... select')

        step('=====> STEP4 by 6 End')



        step('=====> STEP4 by 7 Start : ')
        # df_in_GIShipTo, df_in_GIAcc 의 칼럼 네임을 정정한다.
        # BL Qty, Smoothing Qty는 소수 첫째자리에서 반올림. / GIBLLT Rate은 소수 셋째자리에서 반올림. 부탁드립니다.

        df_GIShipTo[LT_RATIO_RSLT_W_BL_QTY_COLUMN] = df_GIShipTo[SALES_QTY_COLUMN]
        df_GIShipTo.rename(columns={
            LT_RATIO_GI_W_GI_QTY_COLUMN: LT_RATIO_RSLT_W_GI_QTY_COLUMN,
            BL_QTY_COLUMN: LT_RATIO_RSLT_W_GIBLLT_QTY_COLUMN,
            BL_RATE_COLUMN: LT_RATIO_RSLT_W_GIBLLT_RATE_COLUMN,
            SALES_QTY_COLUMN: LT_RATIO_RSLT_W_SMOOTHING_QTY_COLUMN,
        }, inplace=True)
        df_GIShipTo[LT_RATIO_RSLT_W_GIBLLT_RATE_COLUMN] = df_GIShipTo[LT_RATIO_RSLT_W_GIBLLT_RATE_COLUMN].round(3)

        int_col = [LT_RATIO_RSLT_W_BL_QTY_COLUMN, LT_RATIO_RSLT_W_SMOOTHING_QTY_COLUMN]
        df_GIShipTo[int_col] = df_GIShipTo[int_col].round(0).astype('Int64')

        print_df(df_GIShipTo, 'STEP4 by 7.1  ____ df_GIShipTo .... rename')

        df_GIAcc[LT_RATIO_RSLT_ACC_W_BL_QTY_COLUMN] = df_GIAcc[SALES_QTY_COLUMN]
        df_GIAcc.rename(columns={
            LT_RATIO_GI_ACC_W_GI_QTY_COLUMN: LT_RATIO_RSLT_ACC_W_GI_QTY_COLUMN,
            BL_QTY_COLUMN: LT_RATIO_RSLT_ACC_W_GIBLLT_QTY_COLUMN,
            BL_RATE_COLUMN: LT_RATIO_RSLT_ACC_W_GIBLLT_RATE_COLUMN,
            SALES_QTY_COLUMN: LT_RATIO_RSLT_ACC_W_SMOOTHING_QTY_COLUMN,
        }, inplace=True)
        df_GIAcc[LT_RATIO_RSLT_ACC_W_GIBLLT_RATE_COLUMN] = df_GIAcc[LT_RATIO_RSLT_ACC_W_GIBLLT_RATE_COLUMN].round(3)

        int_col = [LT_RATIO_RSLT_ACC_W_BL_QTY_COLUMN, LT_RATIO_RSLT_ACC_W_SMOOTHING_QTY_COLUMN]
        df_GIAcc[int_col] = df_GIAcc[int_col].round(0).astype('Int64')

        print_df(df_GIAcc, 'STEP4 by 7.2  ____ df_GIAcc .... rename')
        step('=====> STEP4 by 7 End')


        step('=====> STEP4 by 8 Start')

        df_GIShipTo[LT_RATIO_RSLT_W_GI_QTY_COLUMN] = np.where(
            df_GIShipTo[RELATIVE_WEEK_COLUMN] == 'W00',
            df_GIShipTo[LT_RATIO_RSLT_W_GI_QTY_COLUMN], None
        )

        df_GIAcc[LT_RATIO_RSLT_ACC_W_GI_QTY_COLUMN] = np.where(
            df_GIAcc[RELATIVE_WEEK_COLUMN] == 'W00',
            df_GIAcc[LT_RATIO_RSLT_ACC_W_GI_QTY_COLUMN], None
        )

        step('=====> STEP4 by 8 End')


        step('=====> STEP4 by 9 Start')
        df_GIShipTo_New = df_GIShipTo[df_GIShipTo[LT_RATIO_RSLT_W_GIBLLT_QTY_COLUMN].notna()]
        min_columns = [
            TIME_WEEK_COLUMN, LT_RATIO_RSLT_W_GIBLLT_QTY_COLUMN, LT_RATIO_RSLT_W_GIBLLT_RATE_COLUMN
        ]

        groupby_columns = [SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, SHIP_TO_PARTY_COLUMN, CATEGORY_COLUMN, RELATIVE_WEEK_COLUMN]
        agg_dict = {col: 'min' for col in min_columns}
        df_GIShipTo_New = df_GIShipTo_New.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        df_GIShipTo.drop(columns=[LT_RATIO_RSLT_W_GIBLLT_QTY_COLUMN, LT_RATIO_RSLT_W_GIBLLT_RATE_COLUMN], inplace=True)
        df_GIShipTo = pd.merge(df_GIShipTo, df_GIShipTo_New, how='left', on=[SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, SHIP_TO_PARTY_COLUMN, CATEGORY_COLUMN, RELATIVE_WEEK_COLUMN, TIME_WEEK_COLUMN])

        print_df(df_GIShipTo, 'STEP4 by 9.1  ____ df_GIShipTo .... groupby')


        df_GIAcc_New = df_GIAcc[df_GIAcc[LT_RATIO_RSLT_ACC_W_GIBLLT_QTY_COLUMN].notna()]
        min_columns = [
            TIME_WEEK_COLUMN, LT_RATIO_RSLT_ACC_W_GIBLLT_QTY_COLUMN, LT_RATIO_RSLT_ACC_W_GIBLLT_RATE_COLUMN
        ]

        groupby_columns = [SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, CATEGORY_COLUMN, RELATIVE_WEEK_COLUMN]
        agg_dict = {col: 'min' for col in min_columns}
        df_GIAcc_New = df_GIAcc_New.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        df_GIAcc.drop(columns=[LT_RATIO_RSLT_ACC_W_GIBLLT_QTY_COLUMN, LT_RATIO_RSLT_ACC_W_GIBLLT_RATE_COLUMN], inplace=True)
        df_GIAcc = pd.merge(df_GIAcc, df_GIAcc_New, how='left', on=[SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, CATEGORY_COLUMN, RELATIVE_WEEK_COLUMN, TIME_WEEK_COLUMN])

        print_df(df_GIShipTo, 'STEP4 by 9.2  ____ df_GIAcc .... groupby')

        step('=====> STEP4 by 9 End')



        step('=====> STEP4.5 Start')
        #
        df_GIShipToCustBOD = df_GIShipTo.copy()
        df_GIShipToCustBOD = pd.merge(df_GIShipToCustBOD, df_in_SiteShipToMap, how='left', left_on=[SALES_DOMAIN_AP2_COLUMN], right_on=[SITE_AP2_MAP_SHIP_TO]).drop_duplicates()
        print_df(df_GIShipToCustBOD, 'STEP4.5.1.1  ____ df_GIShipToCustBOD .... merge')

        df_GIShipToCustBOD = pd.merge(df_GIShipToCustBOD, df_in_BODMOD, how='left', on=[LOCATION_COLUMN, PRODUCT_GROUP_COLUMN])
        df_GIShipToCustBOD[BOD_CUSTOMER_MODE_BOD_LT] = df_GIShipToCustBOD[BOD_CUSTOMER_MODE_BOD_LT].astype('Int64')
        print_df(df_GIShipToCustBOD, 'STEP4.5.1.2  ____ df_GIShipToCustBOD .... merge')


        groupby_columns = [SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, SHIP_TO_PARTY_COLUMN]
        max_columns = [BOD_CUSTOMER_MODE_BOD_LT]
        agg_dict = {col: 'max' for col in max_columns}
        df_GIShipToCustBOD = df_GIShipToCustBOD.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_GIShipToCustBOD, 'STEP4.5.1.3  ____ df_GIShipToCustBOD .... groupby')

        df_GIShipToCustBOD.rename(columns={
            BOD_CUSTOMER_MODE_BOD_LT: LT_RATIO_GI_W_CUST_BOD,
        }, inplace=True)
        # df_GIShipToCustBOD[LT_RATIO_GI_W_CUST_BOD] = (
        #     pd.to_numeric(df_GIShipToCustBOD[LT_RATIO_GI_W_CUST_BOD], errors='coerce')
        #     .div(7)
        #     .round(0)
        #     .astype('Int64')
        # )
        print_df(df_GIShipToCustBOD, 'STEP4.5.1.4  ____ df_GIShipToCustBOD .... rename')

        df_GIShipToCustBOD[LT_RATIO_GI_W_CUST_BOD] = (df_GIShipToCustBOD[LT_RATIO_GI_W_CUST_BOD]/7).round(0).astype('Int64')
        print_df(df_GIShipToCustBOD, 'STEP4.5.1.5  ____ df_GIShipToCustBOD .... rename')

        #
        df_GIAccCustBOD = df_GIAcc.copy()
        df_GIAccCustBOD = pd.merge(df_GIAccCustBOD, df_in_SiteShipToMap, how='left', left_on=[SALES_DOMAIN_AP2_COLUMN], right_on=[SITE_AP2_MAP_SHIP_TO])
        print_df(df_GIAccCustBOD, 'STEP4.5.2.1  ____ df_GIAccCustBOD .... merge')

        df_GIAccCustBOD = pd.merge(df_GIAccCustBOD, df_in_BODMOD, how='left', on=[LOCATION_COLUMN, PRODUCT_GROUP_COLUMN])
        # df_GIAccCustBOD = df_GIAccCustBOD[df_GIAccCustBOD[BOD_CUSTOMER_MODE_BOD_LT].notna()]
        df_GIAccCustBOD[BOD_CUSTOMER_MODE_BOD_LT] = df_GIAccCustBOD[BOD_CUSTOMER_MODE_BOD_LT].astype('Int64')
        print_df(df_GIAccCustBOD, 'STEP4.5.2.2  ____ df_GIAccCustBOD .... merge')

        groupby_columns = [SALES_DOMAIN_SHIP_TO_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN]
        max_columns = [BOD_CUSTOMER_MODE_BOD_LT]
        agg_dict = {col: 'max' for col in max_columns}
        df_GIAccCustBOD = df_GIAccCustBOD.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_GIAccCustBOD, 'STEP4.5.2.3  ____ df_GIAccCustBOD .... groupby')

        df_GIAccCustBOD.rename(columns={
            BOD_CUSTOMER_MODE_BOD_LT: LT_RATIO_GI_ACC_W_CUST_BOD,
        }, inplace=True)
        df_GIAccCustBOD[LT_RATIO_GI_ACC_W_CUST_BOD] = (df_GIAccCustBOD[LT_RATIO_GI_ACC_W_CUST_BOD]/7).round(0).astype('Int64')
        print_df(df_GIAccCustBOD, 'STEP4.5.2.4  ____ df_GIAccCustBOD .... rename')

        step('=====> STEP4.5 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_LTRatioShipTo = rename_and_delete_df(df_GIShipTo)
        df_out_LTRatioShipTo[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_LTRatioShipTo = df_out_LTRatioShipTo[fn_lt_ratio_ship_to_columns].drop_duplicates()
        df_out_LTRatioShipTo[SHIP_TO_PARTY_COLUMN] = df_out_LTRatioShipTo[SHIP_TO_PARTY_COLUMN].astype(str).str.zfill(10)
        df_out_LTRatioShipTo = ultra_fast_replace_to_none(df_out_LTRatioShipTo)

        df_out_LTRatioAcc = rename_and_delete_df(df_GIAcc)
        df_out_LTRatioAcc[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_LTRatioAcc = df_out_LTRatioAcc[fn_lt_ratio_acc_columns].drop_duplicates()
        df_out_LTRatioAcc = ultra_fast_replace_to_none(df_out_LTRatioAcc)

        df_out_LTRatioShipToW = rename_and_delete_df(df_GIShipToCustBOD)
        df_out_LTRatioShipToW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_LTRatioShipToW = df_out_LTRatioShipToW[fn_lt_ratio_ship_to_w_columns].drop_duplicates()
        df_out_LTRatioShipToW[SHIP_TO_PARTY_COLUMN] = df_out_LTRatioShipToW[SHIP_TO_PARTY_COLUMN].astype(str).str.zfill(10)
        df_out_LTRatioShipToW = ultra_fast_replace_to_none(df_out_LTRatioShipToW)

        df_out_LTRatioAccW = rename_and_delete_df(df_GIAccCustBOD)
        df_out_LTRatioAccW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_LTRatioAccW = df_out_LTRatioAccW[fn_lt_ratio_acc_w_columns].drop_duplicates()
        df_out_LTRatioAccW = ultra_fast_replace_to_none(df_out_LTRatioAccW)

        dataframes = {
            'df_out_LTRatioShipTo': df_out_LTRatioShipTo,
            'df_out_LTRatioAcc': df_out_LTRatioAcc,
            'df_out_LTRatioShipToW': df_out_LTRatioShipToW,
            'df_out_LTRatioAccW': df_out_LTRatioAccW,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_LTRatioShipTo = pd.DataFrame(columns=fn_lt_ratio_ship_to_columns)
        df_out_LTRatioAcc = pd.DataFrame(columns=fn_lt_ratio_acc_columns)
        df_out_LTRatioShipToW = pd.DataFrame(columns=fn_lt_ratio_ship_to_w_columns)
        df_out_LTRatioAccW = pd.DataFrame(columns=fn_lt_ratio_acc_w_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_LTRatioShipTo = pd.DataFrame(columns=fn_lt_ratio_ship_to_columns)
        df_out_LTRatioAcc = pd.DataFrame(columns=fn_lt_ratio_acc_columns)
        df_out_LTRatioShipToW = pd.DataFrame(columns=fn_lt_ratio_ship_to_w_columns)
        df_out_LTRatioAccW = pd.DataFrame(columns=fn_lt_ratio_acc_w_columns)
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
