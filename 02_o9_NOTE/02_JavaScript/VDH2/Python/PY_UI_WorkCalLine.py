"""

* 프로그램명
    - PY_UI_WorkCalLine

* 내용
     - Tact Time에 있는 Location*Line*Item 중에 Tact Time W에 없는 Location*Line*Item 추가

* 변경이력
- 2025.1.7 / ybest7.park (박병훈) / Create
- 2025.3.25 / ybest7.park / 수정

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_LineEfficiencyW = Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Line Eff W], Measure.[Line Eff W_Oper Plan],Measure.[Dummy]}) on column;
                              Select (&MPV * [Time].[Week] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Line Eff W], Measure.[Line Eff W_Oper Plan],Measure.[Dummy]}) on column;
    - df_in_WorkCalLine = Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Line].[Line] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time],Measure.[Dummy]}) on column;
                          Select (&MPV * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Line].[Line] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time],Measure.[Dummy]}) on column;
    - df_in_LineEffSub = Select ([Version].[Version Name] * [Location].[Location] * [Line].[Line] ) on row,({Measure.[Line Eff Sub_IsValid],Measure.[Dummy]}) on column;

* Output Table
    - df_out_WorkCalLine = Select ([Version].[Version Name].[CWV_MP] * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Line].[Line] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column;


* 데이터 삭제
    DELETE DATA FOR MODEL [Work Cal Line] where {Version.[Version Name].[CWV_MP]};


* 테스트 스크립트
    EXEC plugin instance [PY_UI_WorkCalLine] for measures {[Work Cal Line_Lock Flag]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


* 데이터 확인
     Select ([Version].[Version Name].[CWV_MP] * [Time].[Week].[202445] * [Location].[Location].[P306] * [Work Type].[Work Type] * [Line].[Line].[M30] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column;


"""

########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
from NSCMCommon import VDCommon as vdCommon
import os.path
import time
import datetime
import decimal
import math
import traceback
import gc
import tracemalloc

import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re
import warnings

from dateutil import parser as date_parser
from typing import Union

warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_WorkCalLine'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level

########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8")


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)

def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)

def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')

Logger.debug(f'[START] {str_instance}')
Logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')
tracemalloc.start()

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, Logger, com.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if com.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(com.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    vdCommon.gfn_stepLog('100 =====> STEP 1(Start) : Check memory usage & runtime')
    # Value 변수 선언
    # PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = 'CurrentWorkingView'

        df_in_LineEfficiencyW = read_csv_file("df_in_LineEfficiencyW")
        df_in_WorkCalLine = read_csv_file("df_in_WorkCalLine")
        df_in_LineEffSub = read_csv_file('df_in_LineEffSub')

    # if df_in_LineEfficiencyW.empty:
    #     raise Exception("Exception: df_in_LineEfficiencyW is empty")

    vdCommon.gfn_saveDf(df_in_LineEfficiencyW, 'df_in_LineEfficiencyW',True)
    vdCommon.gfn_saveDf(df_in_WorkCalLine, 'df_in_WorkCalLine',True)
    vdCommon.gfn_saveDf(df_in_LineEffSub, 'df_in_LineEffSub',True)

    # # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #     paramOutVersion = PARAM_OUTVERSION_VALUE

    vdCommon.gfn_stepLog('100 =====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('200 =====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    TimeWeek_COLUMN = 'Time.[Week]'
    Location_COLUMN = 'Location.[Location]'
    Line_COLUMN = 'Line.[Line]'
    WorkType_COLUMN = 'Work Type.[Work Type]'
    DataSet_COLUMN = 'Data Set.[Data Set]'

    Work_Cal_Line_Lock_Flag = 'Work Cal Line_Lock Flag'
    Work_Cal_Line_Time = 'Work Cal Line_Time'

    daily_work = "Normal RT"
    daily_special_work = "Normal OT"
    special_work = "Special OT"
    special_work_plus = 'TwoShift OT'

    MP = 'MP'
    WorkType_list = [daily_work, daily_special_work, special_work, special_work_plus]

    vdCommon.gfn_stepLog('200 =====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) 복사 후 WorkType 증가
    ################################################################################################################
    vdCommon.gfn_stepLog('300 =====> STEP 3(Start) : input data machining')

    df_out_WorkCalLine = df_in_LineEfficiencyW.copy()

    row_count, col_count = df_out_WorkCalLine.shape
    note(f'=====> Final df_out_WorkCalLine rows : {row_count} , Columns : {col_count}')

    # input Data Frame에 없는 데이터만 추출
    # Location filtering

    locations_list = df_in_LineEffSub[Location_COLUMN].unique()
    note(f" ===========> locations_list : {locations_list} ")

    df_in_WorkCalLine = df_in_WorkCalLine[df_in_WorkCalLine[Location_COLUMN].isin(locations_list)]
    index_col = [VERSION_NAME_COLUMN, Location_COLUMN, TimeWeek_COLUMN, Line_COLUMN]
    df_in_WorkCalLine_index = df_in_WorkCalLine.set_index(index_col).index
    df_out_WorkCalLine_index = df_out_WorkCalLine.set_index(index_col).index
    df_out_WorkCalLine = df_in_WorkCalLine[~df_in_WorkCalLine_index.isin(df_out_WorkCalLine_index)]
    df_out_WorkCalLine = df_out_WorkCalLine[[VERSION_NAME_COLUMN, Location_COLUMN, TimeWeek_COLUMN, Line_COLUMN]]

    row_count, col_count = df_out_WorkCalLine.shape
    note(f'=====> Final df_out_WorkCalLine rows : {row_count} , Columns : {col_count}')

    # Out Data Frame 의 Measure 추가
    df_out_WorkCalLine[WorkType_COLUMN] = df_out_WorkCalLine.apply(lambda row: WorkType_list, axis=1)
    df_out_WorkCalLine[DataSet_COLUMN] = MP
    df_out_WorkCalLine[Work_Cal_Line_Lock_Flag] = False
    df_out_WorkCalLine[Work_Cal_Line_Time] = 0
    df_out_WorkCalLine = df_out_WorkCalLine.explode(WorkType_COLUMN)

    vdCommon.gfn_saveDf(df_out_WorkCalLine, 'df_out_WorkCalLine', True)
    vdCommon.gfn_stepLog('300 =====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. (1) 최종 Out_Put Save
    ################################################################################################################
    vdCommon.gfn_stepLog('400 =====> STEP 4(Start) : input data machining')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_WorkCalLine, 'df_Out_MultiSitebyItem')

    row_count, col_count = df_out_WorkCalLine.shape
    note(f'=====> Final df_out_WorkCalLine rows : {row_count} , Columns : {col_count}')
    print_df(df_out_WorkCalLine, 'df_Out_MultiSitebyItem')

    vdCommon.gfn_stepLog('400 =====> STEP 4(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    df_out_WorkCalLine = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(500, '===================== plugin Execution End =====================')

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    Logger.Finish()
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')