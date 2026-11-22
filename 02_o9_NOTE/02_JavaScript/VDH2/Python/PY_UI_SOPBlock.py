"""
* 프로그램명
    - PY_UI_SOPBlock

* 내용
    - Version , Product Group, Location 별 관리되는 Flag 기준으로 입력 가능하게 Cell을 오픈해주고 닫아주는 기능을 구현하기 위한 데이터 값 생성

* 변경이력
    - 2026.03.25 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek: Select (&CurrentWeek);
    - df_in_release : Select ([Location].[Location] * [Item].[Product Group]) on row, ({Measure.[SOP Adjustment Release_Block Flag]}) on column where {[Version].[Version Name]};
    - df_in_dsr     : Select ([Location].[Location] * [Item].[Product Group] * [Item].[Item] *  [To Location].[To Location] * [Time].[Week] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP Adjust SET W_DSR GO], Measure.[SOP Adjust SET W_DSR Detail1],Measure.[SOP Adjust SET W_DSR Detail2],Measure.[SOP Adjust SET W_DSR Detail3]}) on column where {[Version].[Version Name]};

* Flow Summary
    - STEP1.  SOP Adjustment Release_Block Flag = Y (BLOCK ON) 기준 산출
    -   1.1 Measure.[SOP Adjust SET W_DSR Detail3] = 1 로 Measure 업데이트
    -   1.2 MIN(Measure.[SOP Adjust SET W_DSR Detail1],Measure.[SOP Adjust SET W_DSR Detail2]) 로 Measure.[SOP Adjust SET W_DSR GO] 구성
    - STEP2.  SOP Adjustment Release_Block Flag = N (BLOCK OFF) 기준 산출
    -   2.1 Measure.[SOP Adjust SET W_DSR Detail3] = 2 로 Measure 업데이트
    -   2.2 MAX(Measure.[SOP Adjust SET W_DSR Detail1],Measure.[SOP Adjust SET W_DSR Detail2],Measure.[SOP Adjust SET W_DSR Detail3]) 로 Measure.[SOP Adjust SET W_DSR GO] 구성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_dsr

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SOPBlock] for measures {[SOP Adjust SET W_DSR GO]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Time].[Week] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[SOP Adjust SET W_DSR GO], Measure.[SOP Adjust SET W_DSR Detail3]}) on column limit 100;

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
str_instance = 'PY_UI_SOPBlock'
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
    weeks = (weeks_df.loc[:, [TIME_WEEK_COLUMN]].drop_duplicates()[TIME_WEEK_COLUMN].to_numpy())

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
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_release = read_csv_file("df_in_release")
            df_in_dsr = read_csv_file("df_in_dsr")

        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_release': df_in_release,
            'df_in_dsr': df_in_dsr,
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
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        SOP_ADJUSTMENT_RELEASE_BLOCK_FLAG_COLUMN = 'SOP Adjustment Release_Block Flag'
        SOP_ADJUST_SET_W_DSR_GO_COLUMN = 'SOP Adjust SET W_DSR GO'
        SOP_ADJUST_SET_W_DSR_DETAIL1_COLUMN = 'SOP Adjust SET W_DSR Detail1'
        SOP_ADJUST_SET_W_DSR_DETAIL2_COLUMN = 'SOP Adjust SET W_DSR Detail2'
        SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN = 'SOP Adjust SET W_DSR Detail3'

        version_columns = [VERSION_NAME_COLUMN]

        key_columns = [LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN]

        dsr_columns = [
            SOP_ADJUST_SET_W_DSR_GO_COLUMN, SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN,
        ]

        fn_dsr_columns = version_columns + key_columns + dsr_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start

        # df_in_GroupIdPanel = df_in_GroupIdPanel[
        #     (df_in_GroupIdPanel[ITEM_COLUMN].isin(['LH55VHCEBGBXXL']))
        # ]

        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_dsr.empty :
            raise CustomException("STEP3 by 0 ____ df_in_dsr 값이 없습니다.")


        # 현재 week 가져오기
        mp_plan_start_week = int(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')


        columns = [
            SOP_ADJUST_SET_W_DSR_DETAIL1_COLUMN, SOP_ADJUST_SET_W_DSR_DETAIL2_COLUMN,
            SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN,
        ]
        df_in_dsr[columns] = df_in_dsr[columns].astype('Int64')

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : SOP Adjustment Release_Block Flag =Y (BLOCK ON) 기준 산출')

        # Step 1-1: Measure.[SOP Adjust SET W_DSR Detail3] = 1 로 Measure 업데이트
        df_joined = pd.merge(
            df_in_dsr, df_in_release,
            how='inner',
            on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
        )
        df_joined[TIME_WEEK_COLUMN] = df_joined[TIME_WEEK_COLUMN].astype(int)
        print_df(df_joined, 'STEP4 by 1.1.1  ____ df_joined .... merge')

        mask = (
            (df_joined[SOP_ADJUSTMENT_RELEASE_BLOCK_FLAG_COLUMN] == 'Y') &
            (df_joined[TIME_WEEK_COLUMN] >= mp_plan_start_week)
        )
        df_step1_1 = df_joined.loc[mask].copy()
        df_step1_1[SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN] = 1

        df_step1_1 = df_step1_1[[
            LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN,
            SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN,
        ]]

        df_step1_1.rename(columns={SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN: 'dsr_detail3'}, inplace=True)
        print_df(df_step1_1, 'STEP4 by 1.1.2  ____ df_step1_1 .... create')



        # Step 1-2: MIN(Measure.[SOP Adjust SET W_DSR Detail1],Measure.[SOP Adjust SET W_DSR Detail2]) 로 Measure.[SOP Adjust SET W_DSR GO] 구성
        df_joined = pd.merge(
            df_in_dsr, df_in_release,
            how='inner',
            on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
        )
        df_joined[TIME_WEEK_COLUMN] = df_joined[TIME_WEEK_COLUMN].astype(int)
        print_df(df_joined, 'STEP4 by 1.2.1  ____ df_joined .... merge')

        mask = (
            (df_joined[SOP_ADJUSTMENT_RELEASE_BLOCK_FLAG_COLUMN] == 'Y') &
            (df_joined[TIME_WEEK_COLUMN] >= mp_plan_start_week)
        )
        df_step1_2 = df_joined.loc[mask].copy()

        # df_step1_2.loc[:, SOP_ADJUST_SET_W_DSR_GO_COLUMN] = np.minimum.reduce([
        #     df_step1_2[SOP_ADJUST_SET_W_DSR_DETAIL1_COLUMN],
        #     df_step1_2[SOP_ADJUST_SET_W_DSR_DETAIL2_COLUMN],
        # ])
        df_step1_2.loc[:, SOP_ADJUST_SET_W_DSR_GO_COLUMN] = df_step1_2[
            [SOP_ADJUST_SET_W_DSR_DETAIL1_COLUMN, SOP_ADJUST_SET_W_DSR_DETAIL2_COLUMN]
        ].min(axis=1)
        print_df(df_step1_2, 'STEP4 by 1.2.1.1  ____ df_step1_2 .... min', True)

        df_step1_2 = df_step1_2[[
            LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN,
            SOP_ADJUST_SET_W_DSR_GO_COLUMN,
        ]]
        df_step1_2.rename(columns={SOP_ADJUST_SET_W_DSR_GO_COLUMN: 'dsr_go'}, inplace=True)
        print_df(df_step1_2, 'STEP4 by 1.2.2  ____ df_step1_2 .... create')

        # df_step1 = pd.concat([df_step1_1, df_step1_2], ignore_index=True).drop_duplicates()
        df_step1 = pd.merge(
            df_step1_1, df_step1_2,
            how='inner',
            on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN],
        )
        print_df(df_step1, 'STEP4 by 1.2.3  ____ df_step1 .... concat', True)

        step('=====> STEP4 by 1 End')




        step('=====> STEP4 by 2 Start : Step 2: SOP Adjustment Release_Block Flag = N (BLOCK OFF) 기준 산출')

        # Step 2-1: Measure.[SOP Adjust SET W_DSR Detail3] = 2 로 Measure 업데이트
        df_joined = pd.merge(
            df_in_dsr, df_in_release,
            how='inner',
            on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
        )
        df_joined[TIME_WEEK_COLUMN] = df_joined[TIME_WEEK_COLUMN].astype(int)
        print_df(df_joined, 'STEP4 by 2.1.1  ____ df_joined .... merge')

        mask = (
            (df_joined[SOP_ADJUSTMENT_RELEASE_BLOCK_FLAG_COLUMN] == 'N') &
            (df_joined[TIME_WEEK_COLUMN] >= mp_plan_start_week)
        )
        df_step2_1 = df_joined.loc[mask].copy()
        df_step2_1[SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN] = 2

        df_step2_1 = df_step2_1[[
            LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN,
            SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN,
        ]]

        df_step2_1.rename(columns={SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN: 'dsr_detail3'}, inplace=True)
        print_df(df_step2_1, 'STEP4 by 2.1.2  ____ df_step2_1 .... create')


        # Step 2-2: MAX(Measure.[SOP Adjust SET W_DSR Detail1],Measure.[SOP Adjust SET W_DSR Detail2],Measure.[SOP Adjust SET W_DSR Detail3]) 로 Measure.[SOP Adjust SET W_DSR GO] 구성
        df_joined = pd.merge(
            df_in_dsr, df_in_release,
            how='inner',
            on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN],
        )
        df_joined[TIME_WEEK_COLUMN] = df_joined[TIME_WEEK_COLUMN].astype(int)
        print_df(df_joined, 'STEP4 by 2.2.1  ____ df_joined .... merge')

        mask = (
            (df_joined[SOP_ADJUSTMENT_RELEASE_BLOCK_FLAG_COLUMN] == 'N') &
            (df_joined[TIME_WEEK_COLUMN] >= mp_plan_start_week)
        )
        df_step2_2 = df_joined.loc[mask].copy()

        df_step2_2.loc[:, SOP_ADJUST_SET_W_DSR_GO_COLUMN] = df_step2_2[
            [SOP_ADJUST_SET_W_DSR_DETAIL1_COLUMN, SOP_ADJUST_SET_W_DSR_DETAIL2_COLUMN, SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN]
        ].max(axis=1)
        print_df(df_step2_2, 'STEP4 by 2.2.1.1  ____ df_step2_2 .... max', True)

        df_step2_2 = df_step2_2[[
            LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN,
            SOP_ADJUST_SET_W_DSR_GO_COLUMN,
        ]]
        df_step2_2.rename(columns={SOP_ADJUST_SET_W_DSR_GO_COLUMN: 'dsr_go'}, inplace=True)
        print_df(df_step2_2, 'STEP4 by 2.2.2  ____ df_step2_2 .... create')

        # df_step2 = pd.concat([df_step2_1, df_step2_2], ignore_index=True).drop_duplicates()
        df_step2 = pd.merge(
            df_step2_1, df_step2_2,
            how='inner',
            on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN],
        )
        print_df(df_step2, 'STEP4 by 2.2.3  ____ df_step2 .... concat', True)

        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : df_in_OCell, df_in_LCM 를 합친다.')

        df_out_dsr = pd.concat([df_step1, df_step2], ignore_index=True)
        print_df(df_out_dsr, 'STEP4 by 3.1  ____ df_out_dsr .... concat')

        df_out_dsr.rename(columns={
            'dsr_go': SOP_ADJUST_SET_W_DSR_GO_COLUMN,
            'dsr_detail3': SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN,
        }, inplace=True)
        print_df(df_out_dsr, 'STEP4 by 3.2  ____ df_out_dsr .... rename')

        columns = [
            SOP_ADJUST_SET_W_DSR_GO_COLUMN, SOP_ADJUST_SET_W_DSR_DETAIL3_COLUMN,
        ]
        df_out_dsr[columns] = df_out_dsr[columns].astype('Int64')

        step('=====> STEP4 by 3 End')


        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_dsr[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_dsr = df_out_dsr[fn_dsr_columns]
        df_out_dsr = ultra_fast_replace_to_none(df_out_dsr)

        dataframes = {
            'df_out_dsr': df_out_dsr,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_dsr = pd.DataFrame(columns=fn_dsr_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_dsr = pd.DataFrame(columns=fn_dsr_columns)
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
