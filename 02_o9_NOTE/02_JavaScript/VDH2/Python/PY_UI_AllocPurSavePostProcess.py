
"""
* 프로그램명
    - PY_UI_AllocPurSavePostProcess

* 내용
    - Sum Aggregate ETD Plan on Alloc Pur

* 변경이력
    - 2026.04.06 / 조재연 / Create

* Flow Summary
    1) 하단 ETD Plan을 상단 Summary 데이터 형태에 맞추어 합산

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP
    - saveflag : N

* Input Tables
    - df_in_AllocPur : Select ( [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]) on row, ({Measure.[Alloc Pur_ETD Plan]}) on column where {[Version].[Version Name]};

* Output Tables :
    - df_out_AllocPurSum

* 테스트 스크립트
    - exec plugin instance [PY_UI_AllocPurSavePostProcess] for Measures{[Alloc Pur Sum_ETD Plan]} using scope (&CWVUI)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (saveflag, "N"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_AllocPurSum : Select ([Version].[Version Name] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location]) on row, ({Measure.[Alloc Pur Sum_ETD Plan]}) on column;

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
str_instance = 'PY_UI_ECPMaster'
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

saveflag = (
    "N"
    if is_local or not saveflag or not saveflag.strip()
    else saveflag
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
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


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


def rename_and_delete_df(target_df):
    new_df = target_df
    delete_dfs(target_df)
    return new_df


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
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"


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
        step('=====> 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_AllocPur = read_csv_file("df_in_AllocPur")

        print_df(df_in_AllocPur, 'STEP 1 - Input table load .... df_in_AllocPur')

        step('=====> 전처리 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_MATERIAL_COLUMN = 'Item Material.[Item Material]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'

        ALLOC_PUR_ETD_PLAN_COLUMN = 'Alloc Pur_ETD Plan'
        ALLOC_PUR_SUM_ETD_PLAN_COLUMN = 'Alloc Pur Sum_ETD Plan'
        ALLOC_PUR_SUM_TOT_SUPPLY = 'Alloc Pur Sum_Tot Supply'

        version_columns = [VERSION_NAME_COLUMN]
        key_columns = [TIME_WEEK_COLUMN, ITEM_MATERIAL_COLUMN, SUB_LOCATION_COLUMN]
        alloc_pur_sum_columns = [ALLOC_PUR_SUM_ETD_PLAN_COLUMN]

        fn_alloc_pur_sum_columns = version_columns + key_columns + alloc_pur_sum_columns

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_AllocPur.empty:
            raise CustomException("STEP3 by 0 ____ df_in_AllocPur 값이 없습니다.")

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 : output data machining
        ##########################################################################n######################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_in_AllocPur 중 SUB_LOCATION이 -이 아닌 값만 발췌')
        df_AllocPurSum = df_in_AllocPur[(df_in_AllocPur[SUB_LOCATION_COLUMN] != '-')]
        df_AllocPurSum[ALLOC_PUR_ETD_PLAN_COLUMN] = df_AllocPurSum[ALLOC_PUR_ETD_PLAN_COLUMN].fillna(0).astype(float)

        print_df(df_AllocPurSum, 'STEP4 by 1  ____ df_AllocPurSum .... column preprocessing')
        step('=====> STEP4 by 1 End')


        step('=====> STEP4 by 2 Start : df_AllocPurSum을 Sub Location, Item, Week에 따라 Sum Aggregation.')
        groupby_columns = [SUB_LOCATION_COLUMN, ITEM_MATERIAL_COLUMN, TIME_WEEK_COLUMN]
        sum_columns = [ALLOC_PUR_ETD_PLAN_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_AllocPurSum = df_AllocPurSum.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)
        print_df(df_AllocPurSum, 'STEP4 by 2  ____ df_AllocPurSum .... groupby')
        step('=====> STEP4 by 2 End')


        step('=====> STEP4 by 3 Start : df_in_AllocPur 필드명 수정.')
        df_AllocPurSum.rename(columns={
            ALLOC_PUR_ETD_PLAN_COLUMN: ALLOC_PUR_SUM_ETD_PLAN_COLUMN
        }, inplace=True)
        print_df(df_AllocPurSum, 'STEP4 by 3  ____ df_AllocPurSum .... rename')
        step('=====> STEP4 by 3 End')


        step('=====> STEP4 by 4 Start : saveflag가 "Y"이면, ETD Plan 값을 copy해서 Tot Supply 필드 생성')
        if (saveflag == "Y"):
            df_AllocPurSum[ALLOC_PUR_SUM_TOT_SUPPLY] = df_AllocPurSum[ALLOC_PUR_SUM_ETD_PLAN_COLUMN]
            fn_alloc_pur_sum_columns = fn_alloc_pur_sum_columns + [ALLOC_PUR_SUM_TOT_SUPPLY]
        elif (saveflag == "N"):
            pass
        else:
            raise CustomException("STEP4 by 4 ____ Invalid saveflag, Y 혹은 N 값만 가능합니다.")

        step('=====> STEP4 by 4 End')


        step('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_AllocPurSum = rename_and_delete_df(df_AllocPurSum)

        df_out_AllocPurSum[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AllocPurSum = df_out_AllocPurSum[fn_alloc_pur_sum_columns]
        df_out_AllocPurSum = df_out_AllocPurSum.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_AllocPurSum': df_out_AllocPurSum
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_AllocPurSum = pd.DataFrame(columns=fn_alloc_pur_sum_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_AllocPurSum = pd.DataFrame(columns=fn_alloc_pur_sum_columns)
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
