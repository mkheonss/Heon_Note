"""
* 프로그램명
    - PY_UI_BALModification

* 내용
    - W Demand Build Ahead Limit으로 SP_MGS_MAXSTOCK Logic을 바탕으로 W Quantity Max Target 정보 변형하기

* 변경이력
    - 2025.09.30 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrentWeek : Select (&CurrentWeek);
    - df_in_AllWeek     : Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));

    - df_in_DemandBAL   : Select ([Location].[Location] * [Item].[Item] * [Time].[Week]  * [Demand].[DemandID] ) on row, ({Measure.[W Demand Build Ahead Limit], Measure.[W Demand Quantity to SCS]}) on column where {[Version].[Version Name]};
    - df_in_MaxTarget   : Select ([Location].[Location] * [Item].[Item] * [Time].[Week] ) on row, ({Measure.[W Quantity Max Target]}) on column where {[Version].[Version Name]};



* Flow Summary
    -

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_MaxTarget

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_BALModification] for measures {[W Quantity Max Target]} using scope (&MPV)
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
str_instance = 'PY_UI_BALModification'
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
            df_in_CurrentWeek = read_csv_file("df_in_CurrentWeek")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_DemandBAL = read_csv_file("df_in_DemandBAL")
            df_in_MaxTarget = read_csv_file("df_in_MaxTarget")



        dataframes = {
            'df_in_CurrentWeek': df_in_CurrentWeek,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_DemandBAL': df_in_DemandBAL,
            'df_in_MaxTarget': df_in_MaxTarget,
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
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAY_COLUMN= 'Time.[Day]'
        ITEM_COLUMN = 'Item.[Item]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'

        W_DEMAND_BUILD_AHEAD_LIMIT_COLUMN = 'W Demand Build Ahead Limit'
        W_DEMAND_QUANTITY_TO_SCS_COLUMN = 'W Demand Quantity to SCS'

        W_QUANTITY_MAX_TARGET_COLUMN = 'W Quantity Max Target'

        NEW_TIME_WEEK_COLUMN = 'NewTimeWeek'
        NEW_MAX_TARGET_COLUMN = 'NewMaxTarget'

        df_MaxTarget_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, W_QUANTITY_MAX_TARGET_COLUMN,
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_Demand = df_in_Demand[df_in_Demand[ITEM_COLUMN] == 'QE43LS03DAUXXH']
        # df_in_SetItem = df_in_SetItem[df_in_SetItem[ITEM_COLUMN] == 'QE43LS03DAUXXH']
        # ------------------ 테스트 디버깅용 ------------------ end


        # 0.2 현재 주차 가져오기
        current_week = int(get_first_value(df_in_CurrentWeek, TIME_WEEK_COLUMN))
        step(f'=====> current_week : {current_week}')



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_DemandBAL.empty:
            raise CustomException("STEP3 by 0 ____ df_in_DemandBAL 값이 없습니다.")

        if df_in_MaxTarget.empty:
            raise CustomException("STEP3 by 0 ____ df_in_MaxTarget 값이 없습니다.")



        # ====================> Week 컬럼 추출 Start
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        # ====================> End




        # ====================> df_in_DemandBAL 가공
        # df_in_DemandBAL에서 Week와 W Demand Build Ahead Limit를 이용해서 Week_BAL 필드 생성.
        # (범위는 max(Plan Start Week, Week - W Demand Build Ahead Limit) <= Week_BAL <= Week)

        # 'Demand.[DemandID]' 컬럼이 'DMD_'로 시작하는 조건과 'W Demand Quantity to SCS' 값이 반드시 있는 조건 필터
        condition1 = df_in_DemandBAL[DEMAND_ID_COLUMN].str.startswith('DMD_')
        condition2 = df_in_DemandBAL[W_DEMAND_QUANTITY_TO_SCS_COLUMN].notna()

        # 두 조건을 모두 만족하는 데이터만 필터링
        df_DemandBAL = df_in_DemandBAL[condition1 & condition2].copy()
        delete_dfs(df_in_DemandBAL)


        int_columns = [
            W_DEMAND_BUILD_AHEAD_LIMIT_COLUMN, W_DEMAND_QUANTITY_TO_SCS_COLUMN,
        ]
        for col in int_columns:
            df_DemandBAL[col] = df_DemandBAL[col].fillna(0).astype(int)

        print_df(df_DemandBAL, 'STEP3 by 1.1  ____ df_DemandBAL .... filtered')
        # ====================> End


        # ====================> df_in_MaxTarget 가공
        int_columns = [
            W_QUANTITY_MAX_TARGET_COLUMN,
        ]
        for col in int_columns:
            df_in_MaxTarget[col] = df_in_MaxTarget[col].fillna(0).astype(int)

        print_df(df_in_MaxTarget, 'STEP3 by 2.1  ____ df_in_MaxTarget .... modify column name')
        # ====================> End


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_DemandBAL 의 W Demand Build Ahead Limit 과 Time.[Week] 에 맞는 데이터 추가')
        # NumPy 배열 활용
        def process_rows_numpy(df1, df2, current):
            # 원본 데이터 복제
            result_rows = df2.to_dict('records')

            # NewTimeWeek 열 생성
            for row in result_rows:
                row[NEW_TIME_WEEK_COLUMN] = 0

            # df1의 'Time.[Week]' 값을 정렬된 상태로 준비
            # 모든 주차 값을 int 타입으로 변환하여 NumPy 배열 생성
            unique_weeks = np.array([int(w) for w in sorted(df1[TIME_WEEK_COLUMN].unique())], dtype=int)

            additional_rows = []

            for row in result_rows:
                w_value = int(row[TIME_WEEK_COLUMN])  # 정수로 변환 확인
                limit_value = int(row[W_DEMAND_BUILD_AHEAD_LIMIT_COLUMN])  # 정수로 변환 확인
                current_int = int(current)  # 정수로 변환 확인

                if limit_value > 0:
                    # NumPy 연산으로 조건에 맞는 주차 찾기
                    mask = (unique_weeks < w_value) & (unique_weeks >= current_int)
                    previous_weeks = unique_weeks[mask]
                    previous_weeks = np.sort(previous_weeks)[::-1][:limit_value]

                    # 찾은 각 주차에 대해 행 추가
                    for prev_week in previous_weeks:
                        new_row = row.copy()
                        new_row[NEW_TIME_WEEK_COLUMN] = int(prev_week)  # 정수로 변환 확인
                        additional_rows.append(new_row)

            # 모든 행 병합
            result_rows.extend(additional_rows)
            return pd.DataFrame(result_rows)

        # 함수 실행
        df_DemandBAL = process_rows_numpy(df_in_AllWeek, df_DemandBAL, current_week)
        df_DemandBAL[NEW_TIME_WEEK_COLUMN] = df_DemandBAL[NEW_TIME_WEEK_COLUMN].astype(str)
        print_df(df_DemandBAL, 'STEP4 by 1.1  ____ df_DemandBAL .... create')
        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : df_DemandBAL > Location, Item, NewTimeWeek 기준으로 W Demand Quantity to SCS를 sum aggregation')
        groupby_columns = [LOCATION_COLUMN, ITEM_COLUMN, NEW_TIME_WEEK_COLUMN]
        sum_columns = [W_DEMAND_QUANTITY_TO_SCS_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_DemandBAL = df_DemandBAL.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_DemandBAL, 'STEP4 by 2.1  ____ df_DemandBAL .... Sum aggregation')

        df_DemandBAL.rename(columns={
            NEW_TIME_WEEK_COLUMN: TIME_WEEK_COLUMN,
        }, inplace=True)
        df_DemandBAL[TIME_WEEK_COLUMN] = df_DemandBAL[TIME_WEEK_COLUMN].astype(int)
        print_df(df_DemandBAL, 'STEP4 by 2.2  ____ df_DemandBAL .... modify column name')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : df_in_MaxTarget에서 W Quantity Max Target 값을 전부 0으로 초기화하여 df_MaxTarget 생성')
        # STEP 3 :  데이터 선 가공 에서 처리
        step('=====> STEP4 by 3 End')



        step('=====> STEP4 by 4 Start : df_MaxTarget를 Location, Item, Week 기준으로 agg 한 df_DemandBAL 와 merge (merge 기준은 df_MaxTarget)')
        df_in_MaxTarget[TIME_WEEK_COLUMN] = df_in_MaxTarget[TIME_WEEK_COLUMN].astype(int)
        df_MaxTarget = pd.merge(df_in_MaxTarget, df_DemandBAL, how='inner', on=[LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_MaxTarget, 'STEP4 by 4.1  ____ df_MaxTarget .... merge[df_in_MaxTarget, df_DemandBAL]')
        step('=====> STEP4 by 4 End')



        step('=====> STEP4 by 5 Start : df_in_DemandBAL의 W Demand Build Ahead Limit 과 Time.[Week] 에 맞는 데이터 추가')
        df_MaxTarget[NEW_MAX_TARGET_COLUMN] = df_MaxTarget[W_QUANTITY_MAX_TARGET_COLUMN] + df_MaxTarget[W_DEMAND_QUANTITY_TO_SCS_COLUMN]
        print_df(df_MaxTarget, 'STEP4 by 5.1  ____ df_MaxTarget .... colum add')
        step('=====> STEP4 by 5 End')



        step('=====> STEP4 by 6 Start : df_in_DemandBAL의 W Demand Build Ahead Limit 과 Time.[Week] 에 맞는 데이터 추가')
        df_MaxTarget.drop(columns=[W_QUANTITY_MAX_TARGET_COLUMN], inplace=True)
        print_df(df_MaxTarget, 'STEP4 by 6.1  ____ df_MaxTarget .... colum remove')

        df_MaxTarget.rename(columns={
            NEW_MAX_TARGET_COLUMN: W_QUANTITY_MAX_TARGET_COLUMN,
        }, inplace=True)
        print_df(df_MaxTarget, 'STEP4 by 6.2  ____ df_MaxTarget .... colum rename')
        step('=====> STEP4 by 6 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_MaxTarget = rename_and_delete_df(df_MaxTarget)
        df_out_MaxTarget[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_MaxTarget = df_out_MaxTarget[df_MaxTarget_columns]

        dataframes = {
            'df_out_MaxTarget': df_out_MaxTarget,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_MaxTarget = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_MaxTarget = pd.DataFrame([], columns=[])
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
