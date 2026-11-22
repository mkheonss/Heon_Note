"""
* 프로그램명
    - PY_UI_SafetyStockAging

* 내용
    - SS를 Build Ahead Item으로 업데이트한다. 없다면, Build Ahead로 업데이트한다.

* 변경이력
    - 2026.04.14 / 조재연 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_SS              : Select ( [Sales Domain].[AP2] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[SS_3160 Qty], Measure.[SS_61 Qty], Measure.[SS_EOH Week], Measure.[SS_Target EOH], Measure.[SS_Adj WOS], Measure.[SS_Target WOS], Measure.[SS_Demand], Measure.[Dummy]}) on column where {[Version].[Version Name]};
    - df_in_BuildAhead      : Select ( [Sales Domain].[AP2] * [Item].[Item] ) on row, ({Measure.[Build Ahead_3160 Qty], Measure.[Build Ahead_61 Qty], Measure.[Build Ahead_EOH Week], Measure.[Build Ahead_Target EOH], Measure.[Build Ahead_Adj WOS], Measure.[Build Ahead_Target WOS], Measure.[Build Ahead_Demand]}) on column where {[Version].[Version Name]};
    - df_in_BuildAheadItem  : Select ( [Sales Domain].[AP2] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] ) on row, ({Measure.[Build Ahead Item_3160 Qty], Measure.[Build Ahead Item_61 Qty], Measure.[Build Ahead Item_EOH Week], Measure.[Build Ahead Item_Target EOH], Measure.[Build Ahead Item_Adj WOS], Measure.[Build Ahead Item_Target WOS], Measure.[Build Ahead Item_Demand]}) on column where {[Version].[Version Name]};

* Flow Summary
    - STEP1. df_in_SS에 df_in_BuildAhead를 Merge한다.
    - STEP2. df_in_SS에 df_in_BuildAheadItem을 Merge한다.
    - STEP3. df_in_SS의 값에 df_in_BuildAheadItem에 있으면 Update, 없으면 df_in_BuildAhead로 Update, 없으면 업데이트하지 않는다.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_SS

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SafetyStockAging] for measures {[SS_3160 Qty]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ( [Version].[Version Name].[CWV_MP] * [Sales Domain].[AP2] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[SS_3160 Qty], Measure.[SS_61 Qty], Measure.[SS_EOH Week], Measure.[SS_Target EOH], Measure.[SS_Adj WOS], Measure.[SS_Target WOS], Measure.[SS_Demand]}) on column;
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
str_instance = 'PY_UI_SafetyStockAging'
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
            df_in_BuildAhead = read_csv_file("df_in_BuildAhead")
            df_in_BuildAheadItem = read_csv_file("df_in_BuildAheadItem")
            df_in_SS = read_csv_file("df_in_SS")


        dataframes = {
            'df_in_BuildAhead': df_in_BuildAhead,
            'df_in_BuildAheadItem': df_in_BuildAheadItem,
            'df_in_SS': df_in_SS
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        SALESDOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'

        SS_3160_QTY_COLUMN = 'SS_3160 Qty'
        SS_61_QTY_COLUMN = 'SS_61 Qty'
        SS_EOH_WEEK_COLUMN = 'SS_EOH Week'
        SS_TARGET_EOH_COLUMN = 'SS_Target EOH'
        SS_ADJ_WOS_COLUMN = 'SS_Adj WOS'
        SS_TARGET_WOS_COLUMN = 'SS_Target WOS'
        SS_DEMAND_COLUMN = 'SS_Demand'

        BUILD_AHEAD_3160_QTY_COLUMN = 'Build Ahead_3160 Qty'
        BUILD_AHEAD_61_QTY_COLUMN = 'Build Ahead_61 Qty'
        BUILD_AHEAD_EOH_WEEK_COLUMN = 'Build Ahead_EOH Week'
        BUILD_AHEAD_TARGET_EOH_COLUMN = 'Build Ahead_Target EOH'
        BUILD_AHEAD_ADJ_WOS_COLUMN = 'Build Ahead_Adj WOS'
        BUILD_AHEAD_TARGET_WOS_COLUMN = 'Build Ahead_Target WOS'
        BUILD_AHEAD_DEMAND_COLUMN = 'Build Ahead_Demand'

        BUILD_AHEAD_ITEM_3160_QTY_COLUMN = 'Build Ahead Item_3160 Qty'
        BUILD_AHEAD_ITEM_61_QTY_COLUMN = 'Build Ahead Item_61 Qty'
        BUILD_AHEAD_ITEM_EOH_WEEK_COLUMN = 'Build Ahead Item_EOH Week'
        BUILD_AHEAD_ITEM_TARGET_EOH_COLUMN = 'Build Ahead Item_Target EOH'
        BUILD_AHEAD_ITEM_ADJ_WOS_COLUMN = 'Build Ahead Item_Adj WOS'
        BUILD_AHEAD_ITEM_TARGET_WOS_COLUMN = 'Build Ahead Item_Target WOS'
        BUILD_AHEAD_ITEM_DEMAND_COLUMN = 'Build Ahead Item_Demand'

        version_columns = [VERSION_NAME_COLUMN]

        ss_columns = [
            SALESDOMAIN_AP2_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, SS_3160_QTY_COLUMN, SS_61_QTY_COLUMN, SS_EOH_WEEK_COLUMN, SS_TARGET_EOH_COLUMN, SS_ADJ_WOS_COLUMN, SS_TARGET_WOS_COLUMN, SS_DEMAND_COLUMN
        ]

        fn_ss_columns = version_columns + ss_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_BuildAhead.empty & df_in_BuildAheadItem.empty:
            raise CustomException("STEP3 by 0 ____ df_in_BuildAhead과 df_in_BuildAheadItem 값이 없습니다.")

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : df_in_SS에 df_in_BuildAhead를 left join')
        df_in_BuildAhead = df_in_BuildAhead.astype({SALESDOMAIN_AP2_COLUMN: 'string'})

        df_SS = df_in_SS.merge(df_in_BuildAhead, how = "left", on=[SALESDOMAIN_AP2_COLUMN, ITEM_COLUMN])

        print_df(df_SS, 'STEP4 by 1  ____ df_in_SS .... left join')

        step('=====> STEP4 by 1 End')


        step('=====> STEP4 by 2 Start : df_SS에 df_in_BuildAheadItem을 left join')
        df_in_BuildAheadItem = df_in_BuildAheadItem.drop(columns=[LOCATION_COLUMN])
        df_in_BuildAheadItem = df_in_BuildAheadItem.drop_duplicates()
        df_in_BuildAheadItem.rename(columns={SUB_LOCATION_COLUMN: LOCATION_COLUMN}, inplace=True)
        df_in_BuildAheadItem = df_in_BuildAheadItem.astype({SALESDOMAIN_AP2_COLUMN: 'string'})

        df_SS = df_SS.merge(df_in_BuildAheadItem, how = "left", on=[SALESDOMAIN_AP2_COLUMN, LOCATION_COLUMN, ITEM_COLUMN])

        print_df(df_SS, 'STEP4 by 2  ____ df_SS .... left join')

        step('=====> STEP4 by 2 End')


        step('=====> STEP4 by 3 Start : df_SS의 column을 Select한다')
        df_SS[SS_3160_QTY_COLUMN] = (
            df_SS[BUILD_AHEAD_3160_QTY_COLUMN]
            .fillna(df_SS[BUILD_AHEAD_ITEM_3160_QTY_COLUMN])
        )

        df_SS[SS_61_QTY_COLUMN] = (
            df_SS[BUILD_AHEAD_61_QTY_COLUMN]
            .fillna(df_SS[BUILD_AHEAD_ITEM_61_QTY_COLUMN])
        )

        df_SS[SS_EOH_WEEK_COLUMN] = (
            df_SS[BUILD_AHEAD_EOH_WEEK_COLUMN]
            .fillna(df_SS[BUILD_AHEAD_ITEM_EOH_WEEK_COLUMN])
        )

        df_SS[SS_TARGET_EOH_COLUMN] = (
            df_SS[BUILD_AHEAD_TARGET_EOH_COLUMN]
            .fillna(df_SS[BUILD_AHEAD_ITEM_TARGET_EOH_COLUMN])
        )

        df_SS[SS_ADJ_WOS_COLUMN] = (
            df_SS[BUILD_AHEAD_ADJ_WOS_COLUMN]
            .fillna(df_SS[BUILD_AHEAD_ITEM_ADJ_WOS_COLUMN])
        )

        df_SS[SS_TARGET_WOS_COLUMN] = (
            df_SS[BUILD_AHEAD_TARGET_WOS_COLUMN]
            .fillna(df_SS[BUILD_AHEAD_ITEM_TARGET_WOS_COLUMN])
        )

        df_SS[SS_DEMAND_COLUMN] = (
            df_SS[BUILD_AHEAD_DEMAND_COLUMN]
            .fillna(df_SS[BUILD_AHEAD_ITEM_DEMAND_COLUMN])
        )

        print_df(df_SS, 'STEP4 by 3  ____ df_SS .... column select', True)

        step('=====> STEP4 by 3 End')


        step('=====> STEP4 End')


        #df_SS

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_SS = rename_and_delete_df(df_SS)
        df_out_SS[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SS = df_out_SS[fn_ss_columns]
        df_out_SS = df_out_SS.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_SS': df_out_SS
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SS = pd.DataFrame(columns=fn_ss_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SS = pd.DataFrame(columns=fn_ss_columns)
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
