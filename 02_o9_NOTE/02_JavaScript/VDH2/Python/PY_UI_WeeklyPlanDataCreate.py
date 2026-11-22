"""
* 프로그램명
    - PY_UI_WeeklyPlanDataCreate.py

* 내용
    - Current Version Weekly Plan을 전주 Version으로 생성함.
     -. 25.04.28 수정
         기존 Work Type을 O/T Hour 만 처리되도록 수정함.
         평일잔업 6시간 + 특근 8시간 합쳐서 14시간을 디폴트 시간으로 처리함.

* 변경이력
    - 2025.04.16 /  강유숙 / 재생성
    - 2025.04.28 / 강유숙 / 수정

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_pre_workcalline
        Select (&LastSyncVersion * [Location].[Location] * [Time].[Week] * [Work Type].[Work Type]
            * [Line].[Line] * [Data Set].[Data Set].[MP] ) on row,
        ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column
        orderby [Time].[Week].Name ;

    - df_in_time
        Select (&Next52Weeks);

    - df_in_worktype
        Select ([Work Type].[Work Type]) ;

    - df_in_line_efficiency
        Select (&LastSyncVersion * [Location].[Location] * [Time].[Week] * [Line].[Line] ) on row,
        ({Measure.[Line Eff W], Measure.[Line Eff W_Oper Plan]}) on column
        Where{Measure.[Line Eff Sub_IsValid] == "Y"} ;

* Flow Summary
    (1) &LastSyncVersion Work Cal Line 데이타를 가져와서 해당 주차 데이타를 Current Version을 Copy함
    (2) Measure.[Work Cal Line_Time] 값 nan 인 경우 디폴트 값으로 세팅함.

* Output Table
    df_out_Work_Cal_Line / MG : Work Cal Line

* 데이타 초기화

* RUN 스크립트
    - EXEC plugin instance [PY_UI_WorkCal_Vereion_Create] for Measures {[Work Cal Line_Time]}
    using scope (&LastSyncVersion)
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),
    (paramOutVersion , "CWV_MP"),
    (MaxSliceTableCells, 200000000),(MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&CWVUI * [Location].[Location] * [Time].[Week] * [Work Type].[Work Type]
            * [Line].[Line] * [Data Set].[Data Set].[MP] ) on row,
        ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column
        orderby [Time].[Week].Name ;

"""

import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import time
import os
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_WeeklyPlanDataCreate'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
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
# 공통 함수 정의
########################################################################################################################
# DF를 출력하는 함수
saveDf_idx = 1
def saveDf(_df, _csvName):
    if common.gfn_get_isLocal():
        global saveDf_idx
        _df.to_csv(os.path.dirname(__file__) + "\\" + f"out_{saveDf_idx}_{_csvName}.csv", index=False)
        saveDf_idx = saveDf_idx + 1

    dfMemory = format(round(_df.memory_usage(deep=True).sum() / (1024 ** 2), 2), ",")
    dfDetailInfo = " ( " + format(_df.shape[0], ",") + " Row * " + str(_df.shape[1]) + " Column, " + dfMemory + " Mb )"

    logger.PrintDF(p_df=_df, p_df_name=_csvName + dfDetailInfo, p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    vdCommon.gfn_pyLog_detail(_csvName, _df)

# Step 로그를 남긴다.
def batchLogStep(log):
    logger.Step(p_step_desc=log)
    # MG 로그를 남긴다.
    vdCommon.gfn_pyLog_detail(log)

########################################################################################################################
# local function
########################################################################################################################
def read_csv_file_converter(file_name, convert):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8", converters = convert)

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


def vd_log_end():
    vdCommon.gfn_pyLog_end()


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
# Batch 시작
vd_log_start()

# 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
tracemalloc.start()
start_time = time.time()

step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

try:
    ################################################################################################################
    # STEP 1 : input table load
    ################################################################################################################
    step('=====> STEP1 Start : input table load')
    if is_local:
        df_in_pre_workcalline = read_csv_file("df_in_pre_workcalline")
        df_in_time = read_csv_file("df_in_time_Next52Weeks")
        df_in_worktype = read_csv_file("df_in_worktype")
        df_in_line_efficiency = read_csv_file("df_in_line_efficiency")

    print_df(df_in_pre_workcalline, 'input table load .... df_in_Pre_WorkCalLine')
    print_df(df_in_time, 'input table load .... df_in_time')
    print_df(df_in_worktype, 'input table load .... df_in_worktype')
    print_df(df_in_line_efficiency, 'input table load .... df_in_line_efficiency')

    step('=====> STEP1 End : input table load')
    ################################################################################################################
    # STEP 2 : DataFrame Column 변수 처리
    ################################################################################################################
    step('=====> STEP2 Start : DataFrame Column 변수 처리')
    # 컬럼 변수 선언
    VERSION_NAME_COLUMN = "Version.[Version Name]"
    LOCATION_COLUMN = 'Location.[Location]'
    TIME_WEEK_COLUMN = 'Time.[Week]'
    WORK_TYPE_COLUMN= 'Work Type.[Work Type]'
    LINE_COLUMN = 'Line.[Line]'
    DATASET_COLUMN = 'Data Set.[Data Set]'

    WORK_CAL_LINE_LOCK_FLAG = 'Work Cal Line_Lock Flag'
    WORK_CAL_LINE_TIME = 'Work Cal Line_Time'

    #Work Type별 Default Time
    WORKTYPE_OTHOUR_TIME = 14

    step('=====> STEP2 End')
    ################################################################################################################
    # STEP 3 : Data 처리
    ################################################################################################################

    step('=====> STEP3-1 Start : Unique Data')
    df_in_time = df_in_time.assign(key=1)
    df_in_time['key'] = df_in_time['key'].astype(int)

    df_in_worktype = df_in_worktype.assign(key=1)
    df_in_worktype['key'] = df_in_worktype['key'].astype(int)

    #Line Efficiency 데이타 가공
    unique_key01 = [LOCATION_COLUMN, LINE_COLUMN]
    df_lineEfficiency = df_in_line_efficiency[unique_key01].sort_values(by=unique_key01)
    df_lineEfficiency = df_lineEfficiency[unique_key01].drop_duplicates()

    # Weekly Plan 데이타 가공
    df_workcalline01 = df_in_pre_workcalline[unique_key01].sort_values(by=unique_key01)
    df_workcalline01 = df_workcalline01[unique_key01].drop_duplicates()

    # Copy 할 대상이 되는 Location + Line 데이타 추출함
    df_lineEfficiency = pd.merge(df_lineEfficiency, df_workcalline01, how="left", on=unique_key01)

    #Master 데이타 Merge 함.
    unique_key02 = [LOCATION_COLUMN, LINE_COLUMN, DATASET_COLUMN]
    df_workcalline = df_in_pre_workcalline[unique_key02].sort_values(by=unique_key02)
    df_workcalline = df_workcalline[unique_key02].drop_duplicates()

    df_workcalline = pd.merge( df_lineEfficiency, df_workcalline,  how="left", on=unique_key01)
    df_workcalline[DATASET_COLUMN] = np.select([df_workcalline[DATASET_COLUMN].isnull()],
                                               ["MP"],default=df_workcalline[DATASET_COLUMN])
    df_workcalline = df_workcalline.assign(key=1)
    df_workcalline['key'] = df_workcalline['key'].astype(int)
    df_workcalline = pd.merge(df_workcalline, df_in_worktype, how="outer", on="key")
    df_workcalline = pd.merge(df_workcalline, df_in_time, how="outer", on="key").drop(columns=['key'])

    join_key = [LOCATION_COLUMN, LINE_COLUMN, WORK_TYPE_COLUMN, DATASET_COLUMN, TIME_WEEK_COLUMN]
    df_workcalline = pd.merge(df_workcalline, df_in_pre_workcalline, how="left", on=join_key)

    df_workcalline[WORK_CAL_LINE_TIME] = np.select(
        [
            (df_workcalline[WORK_TYPE_COLUMN] == 'O/T Hour') & (df_workcalline[WORK_CAL_LINE_TIME].isnull())
        ],
        [WORKTYPE_OTHOUR_TIME], default=df_workcalline[WORK_CAL_LINE_TIME]
    )
    step('=====> STEP3-1 End : ')
    step('=====> STEP3-2 Start : Output DataFrame')
    df_out_Work_Cal_Line = df_workcalline
    df_out_Work_Cal_Line[VERSION_NAME_COLUMN] = paramOutVersion
    step('=====> STEP3-2 End : Output DataFrame')
    ################################################################################################################
    # Step Local 인 경우 최종 Output 파일을 Local에 저장함.
    ################################################################################################################
    if is_local:
        save_csv_file(df_out_Work_Cal_Line, "Fact.df_out_Work_Cal_Line")

    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    step(f'=====> current: {format_size(current)}, '
         f'peak: {format_size(peak)}, '
         f'execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    tracemalloc.stop()
except CustomException as e:
    step(f'=====> CustomException : {e}')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
finally:
    # Batch 종료
    vd_log_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    step('=====> Batch end')