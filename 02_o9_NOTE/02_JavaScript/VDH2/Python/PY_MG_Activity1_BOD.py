"""
* 프로그램명
    - PY_MG_Activity1_BOD

* 내용
    - SourceVersion의 자재 OnHand 잔량 산출

* 변경이력
    - 2025.12.09 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_BODListMtrl : Select ([Location].[Location] * [Item].[Class Category] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[LCM BOD List_BOD Name]}) on column where {Version.[Version Name]};
    - df_in_LCMBODList  : Select ([Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl_Created By], Measure.[BOD List Mtrl_Created Time], Measure.[BOD List Mtrl_EFF Enddate], Measure.[BOD List Mtrl_EFF Startdate], Measure.[BOD List Mtrl_Lot Size], Measure.[BOD List Mtrl_Lot Type], Measure.[BOD List Mtrl_Updated By], Measure.[BOD List Mtrl_Updated Time]}) on column where {Version.[Version Name]};
    - df_in_Activity1   : Select ([Activity1].[Activity1]) on row;

* Flow Summary
    - STEP1. input table1, input table2 조회해서 From, To, Transportmode를 중복제거하고 발췌
    - STEP2. From + To + Transportmode 조합
    - STEP3. STEP2 에서 조합한 결과를 df_in_Activity1 비교 -> df_in_Activity1 에 없는 대상만 발췌해서 output에 구성


* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ActivityBOD

* 데이타 초기화
    - Delete data for model [MP Batch_BODMtrl Bulk Member Creation] where{&MPV};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_Activity1_BOD] for measures {[MP Batch_BODMtrl Bulk Member Creation_BOD Name]} using scope (&MPV)
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
str_instance = 'PY_MG_Activity1_BOD'
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


def get_next_week(df, time_column, base_week, prior_weeks=4):
    try:
        start_idx = df[df[time_column] == base_week].index[0]
        # step(f'=====> start_idx : {start_idx} ')
    except IndexError:
        raise ValueError(f"=====> 타겟 주({target_week})가 데이터프레임에 존재하지 않습니다.")

    target_idx = start_idx + int(PanelFrozenWindow)
    end_idx = target_idx - 1  # 끝 인덱스

    return get_first_value(df.iloc[[end_idx + 1]].copy(), time_column)


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
            df_in_BODListMtrl = read_csv_file("df_in_BODListMtrl")
            df_in_LCMBODList = read_csv_file("df_in_LCMBODList")
            df_in_Activity1 = read_csv_file("df_in_Activity1")


        dataframes = {
            'df_in_BODListMtrl': df_in_BODListMtrl,
            'df_in_LCMBODList': df_in_LCMBODList,
            'df_in_Activity1': df_in_Activity1,
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
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'

        MP_BATCH_BODMTRL_BULK_CREATION_BOD_NAME_COLUMN = 'MP Batch_BODMtrl Bulk Member Creation_BOD Name'
        MP_BATCH_BODMTRL_BULK_CREATION_FROM_SITE_ID_COLUMN = 'MP Batch_BODMtrl Bulk Member Creation_From Site ID'
        MP_BATCH_BODMTRL_BULK_CREATION_TO_SITE_ID_COLUMN = 'MP Batch_BODMtrl Bulk Member Creation_To Site ID'

        version_columns = [VERSION_NAME_COLUMN]
        key_columns = [LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]

        bulk_bod_columns = [
            MP_BATCH_BODMTRL_BULK_CREATION_BOD_NAME_COLUMN, MP_BATCH_BODMTRL_BULK_CREATION_FROM_SITE_ID_COLUMN,
            MP_BATCH_BODMTRL_BULK_CREATION_TO_SITE_ID_COLUMN,
        ]

        fn_activity1_bod_columns = version_columns + key_columns + bulk_bod_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[LOCATION_COLUMN] == 'P306']
        # print_df(df_in_BODProdSET, 'STEP3 by 1.1  ____ df_in_BODProdSET .... filter', True)
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[SUB_LOCATION_COLUMN] == 'L5N0']
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_BODListMtrl.empty & df_in_LCMBODList.empty :
            raise CustomException("STEP3 by 0 ____ df_in_BODListMtrl 과 df_in_LCMBODList 값이 없습니다.")
        


        # df_in_BODListMtrl 필요컬럼 설정 (From Site, To Site, Trans Mode 만 추출)
        df_in_BODListMtrl = df_in_BODListMtrl[key_columns]
        print_df(df_in_BODListMtrl, 'STEP3 by 0.1  ____ df_in_BODListMtrl .... filterd')

        # df_in_LCMBODList 필요컬럼 설정 (From Site, To Site, Trans Mode 만 추출)
        df_in_LCMBODList = df_in_LCMBODList[key_columns]
        print_df(df_in_LCMBODList, 'STEP3 by 0.2  ____ df_in_LCMBODList .... filterd')

        # filter 한 df concat
        df_in_BODList = pd.concat([df_in_BODListMtrl, df_in_LCMBODList], ignore_index=True).drop_duplicates()
        print_df(df_in_BODList, 'STEP3 by 0.3  ____ df_in_BODList .... df concat')
        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : input table1, input table2 조회해서 From, To, Transportmode 를 중복제거하고 발췌')
        df_in_BODListMtrl = df_in_BODListMtrl[key_columns].drop_duplicates()
        print_df(df_in_BODListMtrl, 'STEP4 by 1.1  ____ df_in_BODListMtrl .... filter')

        df_in_LCMBODList = df_in_LCMBODList[key_columns].drop_duplicates()
        print_df(df_in_LCMBODList, 'STEP4 by 1.2  ____ df_in_LCMBODList .... filter')
        step('=====> STEP4 by 1 End')




        step('=====> STEP4 by 2 Start : From + To + Transportmode 조합')
        df_in_BODList = pd.concat([df_in_BODListMtrl, df_in_LCMBODList], ignore_index=True).drop_duplicates()
        print_df(df_in_BODList, 'STEP4 by 2.1  ____ df_in_BODList .... df concat')

        df_in_BODList[MP_BATCH_BODMTRL_BULK_CREATION_BOD_NAME_COLUMN] = (
                df_in_BODList[LOCATION_COLUMN] + '_' +
                df_in_BODList[SUB_LOCATION_COLUMN] + '_' +
                df_in_BODList[TRANS_MODE_COLUMN]
        )
        df_in_BODList[MP_BATCH_BODMTRL_BULK_CREATION_FROM_SITE_ID_COLUMN] = df_in_BODList[LOCATION_COLUMN]
        df_in_BODList[MP_BATCH_BODMTRL_BULK_CREATION_TO_SITE_ID_COLUMN] = df_in_BODList[SUB_LOCATION_COLUMN]
        print_df(df_in_BODList, 'STEP4 by 2.2  ____ df_in_BODList .... From, To, TP Mode 조합')
        step('=====> STEP4 by 2 End')




        step('=====> STEP4 by 3 Start : Step2 에서 조합한 결과를 df_in_Activity1 랑 비교 -> df_in_Activity1 에 없는 대상만 발췌해서 output에 구성')
        df_ActivityBOD = pd.merge(df_in_BODList, df_in_Activity1, how='left', indicator=True,
                               left_on=[MP_BATCH_BODMTRL_BULK_CREATION_BOD_NAME_COLUMN],
                               right_on=[ACTIVITY1_COLUMN])
        df_ActivityBOD = df_ActivityBOD[df_ActivityBOD['_merge'] == 'left_only'].drop('_merge', axis=1)
        print_df(df_ActivityBOD, 'STEP4 by 3.1  ____ df_ActivityBOD .... create')
        step('=====> STEP4 by 3 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_ActivityBOD = rename_and_delete_df(df_ActivityBOD)

        df_out_ActivityBOD[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ActivityBOD = df_out_ActivityBOD[fn_activity1_bod_columns]

        dataframes = {
            'df_out_ActivityBOD': df_out_ActivityBOD,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ActivityBOD = pd.DataFrame(columns=fn_activity1_bod_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ActivityBOD = pd.DataFrame(columns=fn_activity1_bod_columns)
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
