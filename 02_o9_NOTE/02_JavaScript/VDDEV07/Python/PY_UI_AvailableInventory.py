"""
* 프로그램명
    - PY_UI_AvailableInventory

* 내용
    - Shortage 발생 모델을 리스트업하여 대체모델 판매를 제안하는 UI (조회) - AP2(법인내 소진), GC(법인간 이동)

* 변경이력
    - 2026.01.13 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_SyncPlanShort     : Select ([Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[Customer Group] * [Sales Domain].[AP2] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[W Total Short Quantity]}) on column where { [Version].[Version Name], (Measure.[W Total Short Quantity]) > 0 };
    - df_in_ForwardPlanResult : Select ([Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[Customer Group] * [Sales Domain].[AP2] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[W Total Met On Time Quantity], Measure.[W Total Late Quantity]}) on column where  { [Version].[Version Name], (Measure.[W Total Met On Time Quantity] > 0 ) || (Measure.[W Total Late Quantity] > 0 )};
    - df_in_Upselling         : Select ([Location].[Location] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[Upselling Item List_Ctg], Measure.[Upselling Item List_Like Ctg], Measure.[Upselling Item List_Like Ctg Name], Measure.[Upselling Item List_Like Item], Measure.[Upselling Item List_Like Rank], Measure.[Upselling Item List_Like Sub Ctg], Measure.[Upselling Item List_Like Sub Ctg Name], Measure.[Upselling Item List_Sub Ctg], Measure.[Upselling Item List_UpsellingYN]}) on column where { [Version].[Version Name] };
    - df_in_AvailInvGCSub     : Select ([Sales Domain].[AP2] * [Item].[Item] ) on row, ({Measure.[Avail Inv GC Sub_ASP], Measure.[Avail Inv GC Sub_ASP Week], Measure.[Avail Inv GC Sub_Sell Out F4], Measure.[Avail Inv GC Sub_TWOS], Measure.[Avail Inv GC Sub_WOS]}) on column where {[Version].[Version Name]};

* Flow Summary
    - STEP0. df_in_SyncPlanShort 와 df_in_Upselling Merge 해서 유사,상위,하위모델 및 기본 데이터프레임 생성
    - STEP1. df_in_Upselling 기준으로 Available Inventory AP2 생성
    - STEP2. df_in_Upselling 기준으로 Available Inventory AP2 W 생성
    - STEP4. df_in_Upselling 기준으로 Available Inventory GC 생성
    - STEP4. df_in_Upselling 기준으로 Available Inventory GC W 생성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_AvailableInventoryGC
    - df_out_AvailableInventoryGCW
    - df_out_AvailableInventoryAP2
    - df_out_AvailableInventoryAP2W

* 데이타 초기화
    - DELETE DATA FOR MODEL [Avail Inv AP2] where{[Version].[Version Name].filter(#.Name == "CWV_MP")};
    - DELETE DATA FOR MODEL [Avail Inv AP2 W] where{[Version].[Version Name].filter(#.Name == "CWV_MP")};
    - DELETE DATA FOR MODEL [Avail Inv GC] where{[Version].[Version Name].filter(#.Name == "CWV_MP")};
    - DELETE DATA FOR MODEL [Avail Inv GC W] where{[Version].[Version Name].filter(#.Name == "CWV_MP")};

* RUN 스크립트
    - exec procedure PR_UI_AvailableInventory {"Version":"CWV_MP"};

    - EXEC plugin instance [PY_UI_AvailableInventory] for measures {[Avail Inv AP2 W_Down Qty]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Location].[Rep AP2] * [Sales Domain].[AP2] * [To Item].[To Item] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[Avail Inv GC_ASP], Measure.[Avail Inv GC_ASP Week Info], Measure.[Avail Inv GC_Profit], Measure.[Avail Inv GC_Sell Out F4], Measure.[Avail Inv GC_TWOS], Measure.[Avail Inv GC_WOS], Measure.[Avail Inv GC_vs TWOS]}) on column where { [Version].[Version Name].[CWV_MP] } limit 100;
    - Select ([Location].[Rep AP2] * [Sales Domain].[AP2] * [To Item].[To Item] * [Time].[Week] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[Avail Inv GC W_Qty], Measure.[Avail Inv GC W_vs TWOS Short]}) on column where { [Version].[Version Name].[CWV_MP] } limit 100;
    - Select ([Sales Domain].[AP2] * [To Item].[To Item] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[Avail Inv AP2_ASP], Measure.[Avail Inv AP2_ASP Week]}) on column where { [Version].[Version Name].[CWV_MP] } limit 100;
    - Select ([Sales Domain].[AP2] * [To Item].[To Item] * [Time].[Week] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[Avail Inv AP2 W_Down Qty], Measure.[Avail Inv AP2 W_Short Qty], Measure.[Avail Inv AP2 W_Similar Qty], Measure.[Avail Inv AP2 W_Up Qty]}) on column where { [Version].[Version Name].[CWV_MP] } limit 100;

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
str_instance = 'PY_UI_AvailableInventory'
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
            df_in_SyncPlanShort = read_csv_file("df_in_SyncPlanShort")
            df_in_ForwardPlanResult = read_csv_file("df_in_ForwardPlanResult")
            df_in_Upselling = read_csv_file("df_in_Upselling")
            df_in_AvailInvGCSub = read_csv_file("df_in_AvailInvGCSub")

        dataframes = {
            'df_in_SyncPlanShort': df_in_SyncPlanShort,
            'df_in_ForwardPlanResult': df_in_ForwardPlanResult,
            'df_in_Upselling': df_in_Upselling,
            'df_in_AvailInvGCSub': df_in_AvailInvGCSub,
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
        LOCATION_REP_AP2_COLUMN = 'Location.[Rep AP2]'
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        ITEM_COLUMN = 'Item.[Item]'
        TO_ITEM_COLUMN = 'To Item.[To Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        CATEGORY_COLUMN = 'Category.[Category]'
        SALES_DOMAIN_CUSTOMER_GROUP_COLUMN = 'Sales Domain.[Customer Group]'
        DEMAND_TYPE_COLUMN = 'Demand Type.[Demand Type]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'

        W_TOTAL_SHORT_QTY_COLUMN = 'W Total Short Quantity'
        W_TOTAL_MET_ON_TIME_QTY_COLUMN = 'W Total Met On Time Quantity'
        W_TOTAL_LATE_QTY_COLUMN = 'W Total Late Quantity'

        AVAIL_INV_GC_SUB_ASP_COLUMN = 'Avail Inv GC Sub_ASP'
        AVAIL_INV_GC_SUB_ASP_WEEK_COLUMN = 'Avail Inv GC Sub_ASP Week'
        AVAIL_INV_GC_SUB_SELL_OUT_F4_COLUMN = 'Avail Inv GC Sub_Sell Out F4'
        AVAIL_INV_GC_SUB_TWOS_COLUMN = 'Avail Inv GC Sub_TWOS'
        AVAIL_INV_GC_SUB_WOS_COLUMN = 'Avail Inv GC Sub_WOS'

        UPSELLING_ITEM_LIST_CTG_COLUMN = 'Upselling Item List_Ctg'
        UPSELLING_ITEM_LIST_LIKE_CTG_COLUMN = 'Upselling Item List_Like Ctg'
        UPSELLING_ITEM_LIST_LIKE_CTG_NAME_COLUMN = 'Upselling Item List_Like Ctg Name'
        UPSELLING_ITEM_LIST_LIKE_ITEM_COLUMN = 'Upselling Item List_Like Item'
        UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN = 'Upselling Item List_Like Rank'
        UPSELLING_ITEM_LIST_LIKE_SUB_CTG_COLUMN = 'Upselling Item List_Like Sub Ctg'
        UPSELLING_ITEM_LIST_LIKE_SUB_CTG_NAME_COLUMN = 'Upselling Item List_Like Sub Ctg Name'
        UPSELLING_ITEM_LIST_SUB_CTG_COLUMN = 'Upselling Item List_Sub Ctg'
        UPSELLING_ITEM_LIST_UPSELLINGYN_COLUMN = 'Upselling Item List_UpsellingYN'

        AVAIL_INV_AP2_ASP_COLUMN = 'Avail Inv AP2_ASP'
        AVAIL_INV_AP2_ASP_WEEK_COLUMN = 'Avail Inv AP2_ASP Week'
        AVAIL_INV_AP2_W_DOWN_QTY_COLUMN = 'Avail Inv AP2 W_Down Qty'
        AVAIL_INV_AP2_W_SHORT_QTY_COLUMN = 'Avail Inv AP2 W_Short Qty'
        AVAIL_INV_AP2_W_SIMILAR_QTY_COLUMN = 'Avail Inv AP2 W_Similar Qty'
        AVAIL_INV_AP2_W_UP_QTY_COLUMN = 'Avail Inv AP2 W_Up Qty'
        AVAIL_INV_GC_ASP_COLUMN = 'Avail Inv GC_ASP'
        AVAIL_INV_GC_ASP_WEEK_INFO_COLUMN = 'Avail Inv GC_ASP Week Info'
        AVAIL_INV_GC_PROFIT_COLUMN = 'Avail Inv GC_Profit'
        AVAIL_INV_GC_SELL_OUT_F4_COLUMN = 'Avail Inv GC_Sell Out F4'
        AVAIL_INV_GC_TWOS_COLUMN = 'Avail Inv GC_TWOS'
        AVAIL_INV_GC_WOS_COLUMN = 'Avail Inv GC_WOS'
        AVAIL_INV_GC_VS_TWOS_COLUMN = 'Avail Inv GC_vs TWOS'
        AVAIL_INV_GC_W_QTY_COLUMN = 'Avail Inv GC W_Qty'
        AVAIL_INV_GC_W_VS_TWOS_SHORT_COLUMN = 'Avail Inv GC W_vs TWOS Short'

        version_columns = [VERSION_NAME_COLUMN]

        avail_inv_ap2_columns = [
            SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, SEQUENCE_COLUMN,
            AVAIL_INV_AP2_ASP_COLUMN, AVAIL_INV_AP2_ASP_WEEK_COLUMN,
        ]

        avail_inv_ap2_w_columns = [
            SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, SEQUENCE_COLUMN, TIME_WEEK_COLUMN,
            AVAIL_INV_AP2_W_SHORT_QTY_COLUMN, AVAIL_INV_AP2_W_SIMILAR_QTY_COLUMN, AVAIL_INV_AP2_W_UP_QTY_COLUMN,
            AVAIL_INV_AP2_W_DOWN_QTY_COLUMN,
        ]

        avail_inv_gc_columns = [
            SALES_DOMAIN_AP2_COLUMN, LOCATION_REP_AP2_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, SEQUENCE_COLUMN,
            AVAIL_INV_GC_ASP_COLUMN, AVAIL_INV_GC_ASP_WEEK_INFO_COLUMN, AVAIL_INV_GC_SELL_OUT_F4_COLUMN,
            AVAIL_INV_GC_TWOS_COLUMN, AVAIL_INV_GC_WOS_COLUMN,
        ]

        avail_inv_gc_w_columns = [
            SALES_DOMAIN_AP2_COLUMN, LOCATION_REP_AP2_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, SEQUENCE_COLUMN, TIME_WEEK_COLUMN,
            AVAIL_INV_GC_W_QTY_COLUMN,
        ]

        fn_avail_inv_ap2_columns = version_columns + avail_inv_ap2_columns
        fn_avail_inv_ap2_w_columns = version_columns + avail_inv_ap2_w_columns
        fn_avail_inv_gc_columns = version_columns + avail_inv_gc_columns
        fn_avail_inv_gc_w_columns = version_columns + avail_inv_gc_w_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_SyncPlanShort = df_in_SyncPlanShort[df_in_SyncPlanShort[ITEM_COLUMN].isin(['LH32QMRTBGCXZA', 'LH32QMRTBGCXZA', 'LH32QMRTBGCXZA'])]
        # df_in_SyncPlanShort = df_in_SyncPlanShort[df_in_SyncPlanShort[ITEM_COLUMN].isin(['QE50Q60DAUXXN'])]
        # print_df(df_in_SyncPlanShort, 'STEP3 by 0.1  ____ df_in_SyncPlanShort .... filter', True)

        # df_in_ForwardPlanResult = df_in_ForwardPlanResult[df_in_ForwardPlanResult[ITEM_COLUMN].isin(['LS49CG952ENXZA', 'QN55Q8FAAFXZC'])]
        # print_df(df_in_ForwardPlanResult, 'STEP3 by 0.2  ____ df_in_ForwardPlanResult .... filter', True)

        # df_in_Upselling = df_in_Upselling[df_in_Upselling[ITEM_COLUMN].isin(['QE50Q60DAUXXN', 'QE50Q60DAUXXN'])]
        # print_df(df_in_Upselling, 'STEP3 by 0.3  ____ df_in_Upselling .... filter', True)

        # df_in_AvailInvGCSub = df_in_AvailInvGCSub[df_in_AvailInvGCSub[ITEM_COLUMN].isin(['GQ50Q7F2AUXZG', 'GQ50Q7F2AUXZG'])]
        # print_df(df_in_AvailInvGCSub, 'STEP3 by 0.4  ____ df_in_AvailInvGCSub .... filter', True)
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_SyncPlanShort.empty:
            raise CustomException("STEP3 ____ df_in_SyncPlanShort 값이 없습니다.")

        # ===================== df_in_Upselling 가공 =====================
        df_in_Upselling[SEQUENCE_COLUMN] = df_in_Upselling[SEQUENCE_COLUMN].astype('Int64')
        df_in_Upselling[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN] = df_in_Upselling[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN].astype('Int64')

        # 'Upselling Item List_LikeRank'
        #   유사모델 (로직 보완 예정) -> Upselling Item List_Like Rank = 0
        #   상위모델 -> Upselling Item List_Like Rank < 0
        #   하위모델 -> Upselling Item List_Like Rank > 0
        df_in_Upselling = df_in_Upselling[
            (df_in_Upselling[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN] == 0) |
            (df_in_Upselling[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN] < 0) |
            (df_in_Upselling[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN] > 0)
        ]

        # Upselling 필요컬럼만
        df_in_Upselling = df_in_Upselling[[
            ITEM_COLUMN, LOCATION_COLUMN, SEQUENCE_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN,
            UPSELLING_ITEM_LIST_LIKE_ITEM_COLUMN,
        ]]

        # Upselling Item 최상위 추가
        new_rows = df_in_Upselling[df_in_Upselling[SEQUENCE_COLUMN] == 1].copy()
        new_rows[UPSELLING_ITEM_LIST_LIKE_ITEM_COLUMN] = '-'
        new_rows[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN] = -999
        # new_rows[SEQUENCE_COLUMN] = 0
        print_df(new_rows, 'STEP3 by 1.1 ____ new_rows .... add_new_rows')
        df_in_Upselling = pd.concat([df_in_Upselling, new_rows], ignore_index=True).drop_duplicates()

        # Upselling :  'Upselling Item List_Like Item' -> 'To Item' 으로 변경 및 컬럼삭제
        df_in_Upselling.drop(columns=[SEQUENCE_COLUMN], inplace=True)
        df_in_Upselling.rename(columns={UPSELLING_ITEM_LIST_LIKE_ITEM_COLUMN: TO_ITEM_COLUMN}, inplace=True)
        print_df(df_in_Upselling, 'STEP3 by 1.2 ____ df_in_Upselling .... add_new_rows')




        # ===================== df_in_SyncPlanShort 가공 =====================
        df_in_SyncPlanShort = df_in_SyncPlanShort.drop(columns=[DEMAND_TYPE_COLUMN, DEMAND_ID_COLUMN])
        df_in_SyncPlanShort[SALES_DOMAIN_AP2_COLUMN] = df_in_SyncPlanShort[SALES_DOMAIN_AP2_COLUMN].astype(str)
        df_in_SyncPlanShort[SALES_DOMAIN_CUSTOMER_GROUP_COLUMN] = df_in_SyncPlanShort[SALES_DOMAIN_CUSTOMER_GROUP_COLUMN].astype(str)

        groupby_columns = [
            LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, SALES_DOMAIN_CUSTOMER_GROUP_COLUMN, SALES_DOMAIN_AP2_COLUMN,
        ]
        sum_columns = [W_TOTAL_SHORT_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_SyncPlanShort = df_in_SyncPlanShort.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_in_SyncPlanShort, 'STEP3 by 1.3 ____ df_in_SyncPlanShort .... remake')




        # ===================== df_in_ForwardPlanResult 가공 (df_ForwardPlanResult 사용) =====================
        df_in_ForwardPlanResult = df_in_ForwardPlanResult.drop(columns=[DEMAND_TYPE_COLUMN, DEMAND_ID_COLUMN])
        df_in_ForwardPlanResult[SALES_DOMAIN_AP2_COLUMN] = df_in_ForwardPlanResult[SALES_DOMAIN_AP2_COLUMN].astype(str)
        df_in_ForwardPlanResult[SALES_DOMAIN_CUSTOMER_GROUP_COLUMN] = df_in_ForwardPlanResult[SALES_DOMAIN_CUSTOMER_GROUP_COLUMN].astype(str)
        print_df(df_in_ForwardPlanResult, 'STEP3 by 1.4.1 ____ df_in_ForwardPlanResult .... remake')

        df_ForwardPlanResult = df_in_ForwardPlanResult[[
            ITEM_COLUMN, TIME_WEEK_COLUMN, SALES_DOMAIN_AP2_COLUMN,
            W_TOTAL_MET_ON_TIME_QTY_COLUMN, W_TOTAL_LATE_QTY_COLUMN,
        ]].copy()
        print_df(df_ForwardPlanResult, 'STEP3 by 1.4.2 ____ df_ForwardPlanResult .... re_select')

        groupby_columns = [
            ITEM_COLUMN, TIME_WEEK_COLUMN, SALES_DOMAIN_AP2_COLUMN,
        ]
        sum_columns = [W_TOTAL_MET_ON_TIME_QTY_COLUMN, W_TOTAL_LATE_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_ForwardPlanResult = df_ForwardPlanResult.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_ForwardPlanResult, 'STEP3 by 1.4.3 ____ df_ForwardPlanResult .... agg')




        # ===================== df_in_AvailInvGCSub 가공 =====================
        df_in_AvailInvGCSub[SALES_DOMAIN_AP2_COLUMN] = df_in_AvailInvGCSub[SALES_DOMAIN_AP2_COLUMN].astype(str)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 0 Start : df_in_SyncPlanShort 와 df_in_Upselling Merge 해서 유사,상위,하위모델 및 기본 데이터프레임 생성')

        df_SyncPlanShort_UpSel = df_in_SyncPlanShort.merge(
            df_in_Upselling, how='inner',
            left_on=[ITEM_COLUMN, LOCATION_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN],
        )
        print_df(df_SyncPlanShort_UpSel, 'STEP4 by 0.1  ____ df_SyncPlanShort_UpSel .... merge[df_in_SyncPlanShort, df_in_Upselling]')

        df_SyncPlanShort_UpSel = df_SyncPlanShort_UpSel[[
            ITEM_COLUMN, TO_ITEM_COLUMN, TIME_WEEK_COLUMN, SALES_DOMAIN_CUSTOMER_GROUP_COLUMN, SALES_DOMAIN_AP2_COLUMN,
            UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN, W_TOTAL_SHORT_QTY_COLUMN
        ]]

        df_SyncPlanShort_UpSel[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN] = (
            df_SyncPlanShort_UpSel[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN].astype('Int64').replace({pd.NA: None})
        )
        print_df(df_SyncPlanShort_UpSel, 'STEP4 by 0.2  ____ df_SyncPlanShort_UpSel .... re_select')

        step('=====> STEP4 by 0 End')





        step('=====> STEP4 by 1 Start : df_SyncPlanShort_UpSel 기준으로 Available Inventory AP2 생성')

        df_avail_inv_ap2 = df_SyncPlanShort_UpSel[[
            SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN,
        ]].copy().drop_duplicates()
        print_df(df_avail_inv_ap2, 'STEP4 by 1.1 ____ df_avail_inv_ap2 .... re_select')

        # TO_ITEM_COLUMN == '-'인 행만 조인
        df_seq_0 = df_avail_inv_ap2[df_avail_inv_ap2[TO_ITEM_COLUMN] == '-'].merge(
            df_in_AvailInvGCSub, how='left',
            left_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
            right_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
        )
        print_df(df_seq_0, 'STEP4 by 1.3 ____ df_seq_0 .... add_new_rows')
        df_seq_0.drop(columns=[AVAIL_INV_GC_SUB_SELL_OUT_F4_COLUMN, AVAIL_INV_GC_SUB_TWOS_COLUMN, AVAIL_INV_GC_SUB_WOS_COLUMN], inplace=True)

        # TO_ITEM_COLUMN != '-' 아닌 행만 조인
        df_seq_other = df_avail_inv_ap2[df_avail_inv_ap2[TO_ITEM_COLUMN] != '-'].merge(
            df_in_AvailInvGCSub, how='left',
            left_on=[TO_ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
            right_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
        )
        print_df(df_seq_other, 'STEP4 by 1.4 ____ df_seq_other .... add_new_rows')

        df_seq_other.drop(columns=[ITEM_COLUMN+'_y', AVAIL_INV_GC_SUB_SELL_OUT_F4_COLUMN, AVAIL_INV_GC_SUB_TWOS_COLUMN, AVAIL_INV_GC_SUB_WOS_COLUMN], inplace=True)
        df_seq_other.rename(columns={
            ITEM_COLUMN+'_x': ITEM_COLUMN,
        }, inplace=True)

        # 데이터프레임 합치기
        df_avail_inv_ap2 = pd.concat([df_seq_0, df_seq_other], ignore_index=True)
        print_df(df_avail_inv_ap2, 'STEP4 by 1.5 ____ df_avail_inv_ap2 .... concat[df_seq_0, df_seq_other]')

        # 컬럼명 변경
        df_avail_inv_ap2.rename(columns={
            AVAIL_INV_GC_SUB_ASP_COLUMN: AVAIL_INV_AP2_ASP_COLUMN,
            AVAIL_INV_GC_SUB_ASP_WEEK_COLUMN: AVAIL_INV_AP2_ASP_WEEK_COLUMN,
        }, inplace=True)
        print_df(df_avail_inv_ap2, 'STEP4 by 1.7 ____ df_avail_inv_ap2 .... rename')

        # 전체정렬
        sort_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN, TO_ITEM_COLUMN]
        ascend = [True, True, True, True]
        group_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN]
        none_columns = [AVAIL_INV_AP2_ASP_WEEK_COLUMN]
        df_avail_inv_ap2 = process_inventory_sequences(df_avail_inv_ap2, sort_columns, ascend, group_columns, none_columns)
        print_df(df_avail_inv_ap2, 'STEP4 by 1.8  ____ df_avail_inv_ap2 .... create')

        # 전체 Sequence 재설정
        group_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN]
        df_avail_inv_ap2[SEQUENCE_COLUMN] = df_avail_inv_ap2.groupby(group_columns).cumcount() + 1

        df_avail_inv_ap2[AVAIL_INV_AP2_ASP_COLUMN] = (
            df_avail_inv_ap2[AVAIL_INV_AP2_ASP_COLUMN].astype(float).fillna(0)
        )

        df_avail_inv_ap2[AVAIL_INV_AP2_ASP_WEEK_COLUMN] = (
            df_avail_inv_ap2[AVAIL_INV_AP2_ASP_WEEK_COLUMN].astype('Int64')
        )

        step('=====> STEP4 by 1 End')





        step('=====> STEP4 by 2 Start : df_SyncPlanShort_UpSel 기준으로 Available Inventory AP2 W 생성')

        df_avail_inv_ap2_w = df_SyncPlanShort_UpSel[[
            SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, TIME_WEEK_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN,
            W_TOTAL_SHORT_QTY_COLUMN,
        ]].copy().drop_duplicates()
        print_df(df_avail_inv_ap2_w, 'STEP4 by 2.1 ____ df_avail_inv_ap2_w .... re_select')

        groupby_columns = [
            SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, TIME_WEEK_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN,
        ]
        sum_columns = [W_TOTAL_SHORT_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_avail_inv_ap2_w = df_avail_inv_ap2_w.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_avail_inv_ap2_w, 'STEP4 by 2.1.1 ____ df_avail_inv_ap2_w .... agg')

        df_avail_inv_ap2_w = df_avail_inv_ap2_w.merge(
            df_ForwardPlanResult, how='left',
            left_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN],
            right_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN],
        )
        print_df(df_avail_inv_ap2_w, 'STEP4 by 2.3 ____ df_avail_inv_ap2_w .... merge')

        # 수량컬럼 생성
        calcu_values = (
            df_avail_inv_ap2_w[W_TOTAL_MET_ON_TIME_QTY_COLUMN].fillna(0).values +
            df_avail_inv_ap2_w[W_TOTAL_LATE_QTY_COLUMN].fillna(0).values
        )

        int_columns = [AVAIL_INV_AP2_W_SIMILAR_QTY_COLUMN, AVAIL_INV_AP2_W_UP_QTY_COLUMN, AVAIL_INV_AP2_W_DOWN_QTY_COLUMN]
        for col in int_columns:
            df_avail_inv_ap2_w[col] = calcu_values

        df_avail_inv_ap2_w.rename(columns={
            W_TOTAL_SHORT_QTY_COLUMN: AVAIL_INV_AP2_W_SHORT_QTY_COLUMN,
        }, inplace=True)
        df_avail_inv_ap2_w.drop(columns=[W_TOTAL_MET_ON_TIME_QTY_COLUMN, W_TOTAL_LATE_QTY_COLUMN], inplace=True)
        print_df(df_avail_inv_ap2_w, 'STEP4 by 2.4  ____ df_avail_inv_ap2_w .... calcu_values')

        #   전체 Sequence 설정
        sort_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN, TO_ITEM_COLUMN]
        ascend = [True, True, True, True, True]
        group_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN]
        df_avail_inv_ap2_w = process_inventory_sequences(df_avail_inv_ap2_w, sort_columns, ascend, group_columns)
        print_df(df_avail_inv_ap2_w, 'STEP4 by 2.5  ____ df_avail_inv_ap2_w .... create')

        int_columns = [
            AVAIL_INV_AP2_W_SHORT_QTY_COLUMN,
            AVAIL_INV_AP2_W_SIMILAR_QTY_COLUMN, AVAIL_INV_AP2_W_UP_QTY_COLUMN, AVAIL_INV_AP2_W_DOWN_QTY_COLUMN,
        ]
        df_avail_inv_ap2_w[int_columns] = df_avail_inv_ap2_w[int_columns].astype('Int64').replace({pd.NA: None})

        rank_col = df_avail_inv_ap2_w[UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN]
        # 1. 'Upselling Item List_Like Rank' 가 -999 가 아닌 경우 Avail Inv AP2 W_Short Qty 값 None 처리
        target_columns = [
            AVAIL_INV_AP2_W_SIMILAR_QTY_COLUMN, AVAIL_INV_AP2_W_UP_QTY_COLUMN, AVAIL_INV_AP2_W_DOWN_QTY_COLUMN
        ]
        df_avail_inv_ap2_w.loc[rank_col == -999, target_columns] = None

        # 2. 'Upselling Item List_Like Rank' 가  0 이 아닌 경우 Avail Inv AP2 W_Similar Qty 값 None 처리
        target_columns = [
            AVAIL_INV_AP2_W_SHORT_QTY_COLUMN, AVAIL_INV_AP2_W_UP_QTY_COLUMN, AVAIL_INV_AP2_W_DOWN_QTY_COLUMN
        ]
        df_avail_inv_ap2_w.loc[(rank_col == 0), target_columns] = None

        # 3. 'Upselling Item List_Like Rank' 가 0 보다 큰 경우 Avail Inv AP2 W_Up Qty 값 None 처리
        target_columns = [
            AVAIL_INV_AP2_W_SHORT_QTY_COLUMN, AVAIL_INV_AP2_W_SIMILAR_QTY_COLUMN, AVAIL_INV_AP2_W_UP_QTY_COLUMN
        ]
        df_avail_inv_ap2_w.loc[(rank_col > 0), target_columns] = None

        # 4. 'Upselling Item List_Like Rank' 가 0 보다 작은 경우 Avail Inv AP2 W_Down Qty 값 None 처리
        target_columns = [
            AVAIL_INV_AP2_W_SHORT_QTY_COLUMN, AVAIL_INV_AP2_W_SIMILAR_QTY_COLUMN, AVAIL_INV_AP2_W_DOWN_QTY_COLUMN
        ]
        df_avail_inv_ap2_w.loc[(rank_col < 0) & (rank_col != -999), target_columns] = None
        print_df(df_avail_inv_ap2_w, 'STEP4 by 2.6  ____ df_avail_inv_ap2_w .... filter')

        # 전체 Sequence 재설정
        group_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN]
        df_avail_inv_ap2_w[SEQUENCE_COLUMN] = df_avail_inv_ap2_w.groupby(group_columns).cumcount() + 1
        step('=====> STEP4 by 2 End')





        step('=====> STEP4 by 3 Start : df_SyncPlanShort_UpSel 기준으로 Available Inventory GC 생성')

        df_avail_inv_gc = df_SyncPlanShort_UpSel[[
            SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_CUSTOMER_GROUP_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN,
            UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN,
        ]].copy().drop_duplicates()
        print_df(df_avail_inv_gc, 'STEP4 by 3.1 ____ df_avail_inv_gc .... re_select')

        # TO_ITEM_COLUMN == '-'인 행만 조인
        df_seq_0 = df_avail_inv_gc[df_avail_inv_gc[TO_ITEM_COLUMN] == '-'].merge(
            df_in_AvailInvGCSub, how='left',
            left_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
            right_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
        )
        print_df(df_seq_0, 'STEP4 by 3.2 ____ df_seq_0 .... add_new_rows')

        # TO_ITEM_COLUMN != '-' 아닌 행만 조인
        df_seq_other = df_avail_inv_gc[df_avail_inv_gc[TO_ITEM_COLUMN] != '-'].merge(
            df_in_AvailInvGCSub, how='left',
            left_on=[TO_ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
            right_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN],
        )
        print_df(df_seq_other, 'STEP4 by 3.3 ____ df_seq_other .... add_new_rows')
        df_seq_other.drop(columns=[ITEM_COLUMN+'_y'], inplace=True)
        df_seq_other.rename(columns={
            ITEM_COLUMN+'_x': ITEM_COLUMN,
        }, inplace=True)

        # 데이터프레임 합치기
        df_avail_inv_gc = pd.concat([df_seq_0, df_seq_other], ignore_index=True)
        print_df(df_avail_inv_gc, 'STEP4 by 3.4 ____ df_avail_inv_gc .... concat[df_seq_0, df_seq_other]')

        df_avail_inv_gc.rename(columns={
            SALES_DOMAIN_CUSTOMER_GROUP_COLUMN: LOCATION_REP_AP2_COLUMN,
            AVAIL_INV_GC_SUB_ASP_COLUMN: AVAIL_INV_GC_ASP_COLUMN,
            AVAIL_INV_GC_SUB_ASP_WEEK_COLUMN: AVAIL_INV_GC_ASP_WEEK_INFO_COLUMN,
            AVAIL_INV_GC_SUB_SELL_OUT_F4_COLUMN: AVAIL_INV_GC_SELL_OUT_F4_COLUMN,
            AVAIL_INV_GC_SUB_TWOS_COLUMN: AVAIL_INV_GC_TWOS_COLUMN,
            AVAIL_INV_GC_SUB_WOS_COLUMN: AVAIL_INV_GC_WOS_COLUMN,
        }, inplace=True)
        print_df(df_avail_inv_gc, 'STEP4 by 3.5  ____ df_avail_inv_gc .... rename')


        # sort
        sort_columns = [SALES_DOMAIN_AP2_COLUMN, LOCATION_REP_AP2_COLUMN, ITEM_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN, TO_ITEM_COLUMN]
        ascend = [True, True, True, True, True]
        group_columns = [SALES_DOMAIN_AP2_COLUMN, LOCATION_REP_AP2_COLUMN, ITEM_COLUMN]
        none_columns = [AVAIL_INV_GC_ASP_COLUMN, AVAIL_INV_GC_ASP_WEEK_INFO_COLUMN, AVAIL_INV_GC_SELL_OUT_F4_COLUMN, AVAIL_INV_GC_TWOS_COLUMN, AVAIL_INV_GC_WOS_COLUMN]
        df_avail_inv_gc = process_inventory_sequences(df_avail_inv_gc, sort_columns, ascend, group_columns, none_columns)
        print_df(df_avail_inv_gc, 'STEP4 by 3.6  ____ df_avail_inv_gc .... create', True)

        # 전체 Sequence 재설정
        group_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN]
        df_avail_inv_gc[SEQUENCE_COLUMN] = df_avail_inv_gc.groupby(group_columns).cumcount() + 1

        df_avail_inv_gc[AVAIL_INV_GC_ASP_COLUMN] = (
            df_avail_inv_gc[AVAIL_INV_GC_ASP_COLUMN].astype(float).fillna(0)
        )
        df_avail_inv_gc[AVAIL_INV_GC_ASP_WEEK_INFO_COLUMN] = (
            df_avail_inv_gc[AVAIL_INV_GC_ASP_WEEK_INFO_COLUMN].astype('Int64')
        )
        step('=====> STEP4 by 3 End')





        step('=====> STEP4 by 4 Start : df_SyncPlanShort_UpSel 기준으로 Available Inventory GC W 생성')

        # 필요컬럼 선택
        df_avail_inv_gc_w = df_SyncPlanShort_UpSel[[
            SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_CUSTOMER_GROUP_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, TIME_WEEK_COLUMN,
            UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN, W_TOTAL_SHORT_QTY_COLUMN,
        ]].copy().drop_duplicates()
        print_df(df_avail_inv_gc_w, 'STEP4 by 4.1 ____ df_avail_inv_gc_w .... re_select')

        # groupby
        groupby_columns = [
            SALES_DOMAIN_AP2_COLUMN, SALES_DOMAIN_CUSTOMER_GROUP_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, TIME_WEEK_COLUMN,
            UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN
        ]
        sum_columns = [W_TOTAL_SHORT_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_avail_inv_gc_w = df_avail_inv_gc_w.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_avail_inv_gc_w, 'STEP4 by 4.1.1 ____ df_avail_inv_gc_w .... agg')

        df_avail_inv_gc_w = df_avail_inv_gc_w.merge(
            df_ForwardPlanResult, how='left',
            left_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN],
            right_on=[ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN],
        )
        print_df(df_avail_inv_ap2_w, 'STEP4 by 4.3 ____ df_avail_inv_ap2_w .... merge')

        # 수량컬럼 생성
        calcu_values = (
            df_avail_inv_gc_w[W_TOTAL_SHORT_QTY_COLUMN].fillna(0).values +
            df_avail_inv_gc_w[W_TOTAL_MET_ON_TIME_QTY_COLUMN].fillna(0).values +
            df_avail_inv_gc_w[W_TOTAL_LATE_QTY_COLUMN].fillna(0).values
        )

        int_columns = [AVAIL_INV_GC_W_QTY_COLUMN]
        for col in int_columns:
            df_avail_inv_gc_w[col] = calcu_values

        df_avail_inv_gc_w.rename(columns={
            SALES_DOMAIN_CUSTOMER_GROUP_COLUMN: LOCATION_REP_AP2_COLUMN,
        }, inplace=True)
        df_avail_inv_gc_w.drop(columns=[W_TOTAL_MET_ON_TIME_QTY_COLUMN, W_TOTAL_LATE_QTY_COLUMN], inplace=True)
        df_avail_inv_gc_w[int_columns] = df_avail_inv_gc_w[int_columns].astype('Int64').fillna(0)
        print_df(df_avail_inv_gc_w, 'STEP4 by 4.4  ____ df_avail_inv_gc_w .... calcu_values')


        # sort
        sort_columns = [SALES_DOMAIN_AP2_COLUMN, LOCATION_REP_AP2_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, UPSELLING_ITEM_LIST_LIKE_RANK_COLUMN, TO_ITEM_COLUMN]
        ascend = [True, True, True, True, True, True]
        group_columns = [SALES_DOMAIN_AP2_COLUMN, LOCATION_REP_AP2_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN]
        df_avail_inv_gc_w = process_inventory_sequences(df_avail_inv_gc_w, sort_columns, ascend, group_columns)
        print_df(df_avail_inv_gc_w, 'STEP4 by 4.5  ____ df_avail_inv_gc_w .... create')

        # Sequence 가 1인 Item : Avail Inv GC W_Qty 를 W Total Short Quantity 로 설정
        mask = (df_avail_inv_gc_w[SEQUENCE_COLUMN] == 1)
        df_avail_inv_gc_w.loc[mask, AVAIL_INV_GC_W_QTY_COLUMN] = df_avail_inv_gc_w.loc[mask, W_TOTAL_SHORT_QTY_COLUMN]
        print_df(df_avail_inv_gc_w, 'STEP4 by 4.6  ____ df_avail_inv_gc_w .... mask')

        # 전체 Sequence 재설정
        group_columns = [SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN]
        df_avail_inv_gc_w[SEQUENCE_COLUMN] = df_avail_inv_gc_w.groupby(group_columns).cumcount() + 1

        step('=====> STEP4 by 4 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_AvailableInventoryAP2 = rename_and_delete_df(df_avail_inv_ap2)
        df_out_AvailableInventoryAP2W = rename_and_delete_df(df_avail_inv_ap2_w)
        df_out_AvailableInventoryGC = rename_and_delete_df(df_avail_inv_gc)
        df_out_AvailableInventoryGCW = rename_and_delete_df(df_avail_inv_gc_w)

        df_out_AvailableInventoryAP2[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AvailableInventoryAP2 = df_out_AvailableInventoryAP2[fn_avail_inv_ap2_columns]
        df_out_AvailableInventoryAP2 = ultra_fast_replace_to_none(df_out_AvailableInventoryAP2)

        df_out_AvailableInventoryAP2W[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AvailableInventoryAP2W = df_out_AvailableInventoryAP2W[fn_avail_inv_ap2_w_columns]
        df_out_AvailableInventoryAP2W = ultra_fast_replace_to_none(df_out_AvailableInventoryAP2W)

        df_out_AvailableInventoryGC[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AvailableInventoryGC = df_out_AvailableInventoryGC[fn_avail_inv_gc_columns]
        df_out_AvailableInventoryGC = ultra_fast_replace_to_none(df_out_AvailableInventoryGC)

        df_out_AvailableInventoryGCW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AvailableInventoryGCW = df_out_AvailableInventoryGCW[fn_avail_inv_gc_w_columns]
        df_out_AvailableInventoryGCW = ultra_fast_replace_to_none(df_out_AvailableInventoryGCW)



        dataframes = {
            'df_out_AvailableInventoryAP2': df_out_AvailableInventoryAP2,
            'df_out_AvailableInventoryAP2W': df_out_AvailableInventoryAP2W,
            'df_out_AvailableInventoryGC': df_out_AvailableInventoryGC,
            'df_out_AvailableInventoryGCW': df_out_AvailableInventoryGCW,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_AvailableInventoryAP2 = pd.DataFrame(columns=fn_avail_inv_ap2_columns)
        df_out_AvailableInventoryAP2W = pd.DataFrame(columns=fn_avail_inv_ap2_w_columns)
        df_out_AvailableInventoryGC = pd.DataFrame(columns=fn_avail_inv_gc_columns)
        df_out_AvailableInventoryGCW = pd.DataFrame(columns=fn_avail_inv_gc_w_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_AvailableInventoryAP2 = pd.DataFrame(columns=fn_avail_inv_ap2_columns)
        df_out_AvailableInventoryAP2W = pd.DataFrame(columns=fn_avail_inv_ap2_w_columns)
        df_out_AvailableInventoryGC = pd.DataFrame(columns=fn_avail_inv_gc_columns)
        df_out_AvailableInventoryGCW = pd.DataFrame(columns=fn_avail_inv_gc_w_columns)
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
