"""
* 프로그램명
    - PY_UI_LineModelList

* 내용
    - Line별 Tact Time, Total Cons Capa, SOP Qty를 조회하는 Program

* 변경이력
    - 2025.11.10 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ConsCapa : Select (&NSUILocationPlant * &MDMHorizon * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Capacity Consumption Quantity Plan Output]}) on column where {[Version].[Version Name]};
    - df_in_TactTime : Select (&NSUILocationPlant * [Item].[Item] * [Line].[Line] ) on row, ({Measure.[Tact Time_Time]}) on column where {[Version].[Version Name], [Item].[Item Stage].[SET], Measure.[Tact Time_Valid Asn] == TRUE};
    - df_in_LineEff  : Select (&NSUILocationPlant * &MDMHorizon * [Line].[Line] ) on row where {[Version].[Version Name], [Item].[Item Stage].[SET]};

* Flow Summary
    - STEP1. MG(002.004W Solver Outputs Capacity Consumption Plan)에서 MF (Location), Line, Time, Item별 Total Cons Capa을 가공한다.
    - STEP2. Tact Time과 Merge한다.
    - STEP3. Tact Time과 Total Cons Capa로 SOP Qty를 계산한다.
    - STEP4. Line efficiency를 Merge한다.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_LineModelList

* 데이타 초기화
    - DELETE DATA FOR MODEL [Line Model List] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_LineModelList] for measures {[Line Model List_Qty], [Line Model List_Tact Time], [Line Model List_Total]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Line].[Line] ) on row, ({Measure.[Line Model List_Qty], Measure.[Line Model List_Tact Time], Measure.[Line Model List_Total]}) on column;
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
str_instance = 'PY_UI_LineModelList'
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
            df_in_ConsCapa = read_csv_file("df_in_ConsCapa")
            df_in_TactTime = read_csv_file("df_in_TactTime")
            df_in_LineEff = read_csv_file("df_in_LineEff")


        dataframes = {
            'df_in_ConsCapa': df_in_ConsCapa,
            'df_in_TactTime': df_in_TactTime,
            'df_in_LineEff': df_in_LineEff,
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
        TIME_WEEK_KEY_COLUMN = 'Time.[WeekKey]'
        RESOURCE_COLUMN = 'Resource.[Resource]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
        LINE_COLUMN = 'Line.[Line]'
        TACT_TIME_COLUMN = 'Tact Time_Time'
        W_CAPACITY_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN = 'W Capacity Consumption Quantity Plan Output'

        LINE_MODEL_LIST_QTY_COLUMN = 'Line Model List_Qty'
        LINE_MODEL_LIST_TACT_TIME_COLUMN = 'Line Model List_Tact Time'
        LINE_MODEL_LIST_TOTAL_COLUMN = 'Line Model List_Total'
        LINE_MODEL_LIST_COMSUME_CAPA_COLUMN = 'Line Model List_Comsume Capa'

        version_columns = [VERSION_NAME_COLUMN]
        key_columns = [LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, LINE_COLUMN]

        line_model_list_columns = [
            LINE_MODEL_LIST_QTY_COLUMN, LINE_MODEL_LIST_TACT_TIME_COLUMN, LINE_MODEL_LIST_TOTAL_COLUMN,
            LINE_MODEL_LIST_COMSUME_CAPA_COLUMN,
        ]

        fn_line_model_list_columns = version_columns + key_columns + line_model_list_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_TactTime = df_in_TactTime[df_in_TactTime[ITEM_COLUMN] == 'HG55BU800EUXEN']
        # print_df(df_in_BODProdSET, 'STEP3 by 1.1  ____ df_in_BODProdSET .... filter', True)
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[SUB_LOCATION_COLUMN] == 'L5N0']
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_ConsCapa.empty:
            raise CustomException("STEP3 by 0 ____ df_in_ConsCapa 값이 없습니다.")


        # 현재 주차 가져오기
        # current_week = get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN)
        # step(f'=====> current_week : {current_week}')


        # 불필요 컬럼 삭제
        df_in_LineEff.drop(columns=[TIME_WEEK_KEY_COLUMN], inplace=True, errors='ignore')

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : MG(002.004W Solver Outputs Capacity Consumption Plan)에서 MF (Location), Line, Time, Item별 Total Cons Capa을 가공한다.')
        # 1.1 df_in_ConsCapa의 Resource 값에서 '_'와 '@' 사이에 있는 값만을 발췌한다.
        # 1.2 df_in_ConsCapa의 Resource 칼럼 이름을 [Line].[Line]으로 수정한다.
        # 1.3 df_in_ConsCapa의 Activity3 칼럼 이름을 [Item].[Item]으로 수정한다.
        # 1.4 df_in_ConsCapa의 W Capacity Consumption Quantity Plan Output 칼럼 이름을 'Line Model List_Total' 로 수정한다.

        def extract_between_symbols(text):
            try:
                # '_'와 '@' 사이의 문자열을 추출하는 정규 표현식 패턴
                pattern = r'_(.+?)@'
                match = re.search(pattern, text)
                if match:
                    return match.group(1)  # 첫 번째 그룹(괄호 안의 내용)을 반환
                else:
                    return None  # 패턴이 일치하지 않으면 None 반환
            except (TypeError, AttributeError):
                return None  # 텍스트가 None이거나 문자열이 아닌 경우

        # Resource 값에서 '_'와 '@' 사이에 있는 값만을 발췌
        df_in_ConsCapa[LINE_COLUMN] = df_in_ConsCapa[RESOURCE_COLUMN].apply(extract_between_symbols)

        df_in_ConsCapa[LINE_MODEL_LIST_COMSUME_CAPA_COLUMN] = df_in_ConsCapa[W_CAPACITY_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN]
        df_in_ConsCapa.drop(columns=[RESOURCE_COLUMN], inplace=True)
        df_in_ConsCapa.rename(columns={
            ACTIVITY3_COLUMN: ITEM_COLUMN,
            W_CAPACITY_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN: LINE_MODEL_LIST_TOTAL_COLUMN,
        }, inplace=True)
        # df_in_ConsCapa[LINE_MODEL_LIST_TOTAL_COLUMN] = df_in_ConsCapa[LINE_MODEL_LIST_TOTAL_COLUMN].round().astype(int)
        df_in_ConsCapa[LINE_MODEL_LIST_TOTAL_COLUMN] = df_in_ConsCapa[LINE_MODEL_LIST_TOTAL_COLUMN].round(1)
        print_df(df_in_ConsCapa, 'STEP4 by 1.1  ____ df_in_ConsCapa .... recreate')
        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : Tact Time과 Merge 한다.')
        # 2.1 df_in_TactTime을 기준으로 Location, Item, Line에 따라 df_in_ConsCapa를 Merge한다.
        # 2.2 Merge한 테이블의 Tact Time_Time 칼럼 이름을 'Line Model List_Tact Time' 으로 수정한다.
        df_in_TactTime = pd.merge(df_in_TactTime, df_in_ConsCapa, how='inner',
                                  on=[LOCATION_COLUMN, ITEM_COLUMN, LINE_COLUMN])
        df_in_TactTime.rename(columns={
            TACT_TIME_COLUMN: LINE_MODEL_LIST_TACT_TIME_COLUMN,
        }, inplace=True)
        print_df(df_in_TactTime, 'STEP4 by 2.1  ____ df_in_TactTime .... recreate')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : Tact Time과 Total Cons Capa로 SOP Qty를 계산한다.')
        # 3.1 df_in_TactTime 의 row 별로 Line Model List_Total]을 'Line Model List_Tact Time' 로 나눈 값을 'Line Model List_Qty' 에 저장한다.
        #       ('Line Model List_Qty' = 'Line Model List_Total' / 'Line Model List_Tact Time')

        def calculate_qty(df, total_column, tact_time_column, qty_column, operation='round'):
            if operation == 'round':
                df[qty_column] = np.where(
                    df[tact_time_column] != 0,
                    np.round(df[total_column] / df[tact_time_column], decimals=1),
                    0
                )
            elif operation == 'floor':
                df[qty_column] = np.where(
                    df[tact_time_column] != 0,
                    np.floor(df[total_column] / df[tact_time_column] * 10) / 10,
                    0
                )
            elif operation == 'ceil':
                df[qty_column] = np.where(
                    df[tact_time_column] != 0,
                    np.ceil(df[total_column] / df[tact_time_column] * 10) / 10,
                    0
                )
            elif operation == 'int':
                df[qty_column] = np.where(
                    df[tact_time_column] != 0,
                    np.round(df[total_column] / df[tact_time_column], decimals=0).astype(int),
                    0
                )
            else:
                raise ValueError("연산은 'round', 'floor', 'ceil', 'int' 중 하나여야 합니다.")

            return df

        df_in_TactTime = calculate_qty(
            df_in_TactTime,
            LINE_MODEL_LIST_TOTAL_COLUMN,
            LINE_MODEL_LIST_TACT_TIME_COLUMN,
            LINE_MODEL_LIST_QTY_COLUMN,
            'int'  # (소수점 한자리) 계산 후 반올림:round, 내림: floor, 올림:ceil, int: 정수
        )
        print_df(df_in_TactTime, 'STEP4 by 3.1  ____ df_in_TactTime .... Qty 계산')
        step('=====> STEP4 by 3 End')




        step('=====> STEP4 by 4 Start : Line efficiency를 Merge 한다')
        # 4.1 df_in_LineEff 를 기준으로 Location, Time, Line에 따라 df_in_TactTime 을 Merge 한다.
        df_LineModelList = pd.merge(df_in_LineEff, df_in_TactTime, how='inner',
                                    on=[LOCATION_COLUMN, TIME_WEEK_COLUMN, LINE_COLUMN])
        print_df(df_LineModelList, 'STEP4 by 4.1  ____ df_LineModelList .... create')

        # df_LineModelList[LINE_MODEL_LIST_COMSUME_CAPA_COLUMN] = df_LineModelList[LINE_MODEL_LIST_TOTAL_COLUMN]
        # df_LineModelList[LINE_MODEL_LIST_TOTAL_COLUMN] = (
        #     np.floor((df_LineModelList[LINE_MODEL_LIST_QTY_COLUMN] * df_LineModelList[LINE_MODEL_LIST_TACT_TIME_COLUMN]) + 0.5).astype(int)
        # )
        df_LineModelList[LINE_MODEL_LIST_TOTAL_COLUMN] = (
            np.round(
                df_LineModelList[LINE_MODEL_LIST_QTY_COLUMN] * df_LineModelList[LINE_MODEL_LIST_TACT_TIME_COLUMN],
                1
            )
        )

        df_LineModelList = df_LineModelList[df_LineModelList[LINE_MODEL_LIST_QTY_COLUMN] > 0]
        step('=====> STEP4 by 4 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_LineModelList = rename_and_delete_df(df_LineModelList)

        df_out_LineModelList[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_LineModelList = df_out_LineModelList[fn_line_model_list_columns]

        dataframes = {
            'df_out_LineModelList': df_out_LineModelList,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_LineModelList = pd.DataFrame(columns=fn_line_model_list_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_LineModelList = pd.DataFrame(columns=fn_line_model_list_columns)
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
