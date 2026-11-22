"""

* 프로그램명
    - PY_UI_WorkCalAnnual

* 내용
     - Tact Time에 있는 Location*Line*Item 중에 Tact Time W에 없는 Location*Line*Item 추가

* 변경이력
- 2025.1.7 / ybest7.park (박병훈) / Create
- 2025/02/27 수정 (input data)
- 2025/03/24 수정

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_Location :  Select ([Version].[Version Name] * [Location].[Location] * [Line].[Line] ) on row,({Measure.[Line Eff Sub_IsValid],Measure.[Dummy]}) on column;
                    (Select ([Version].[Version Name] * [Location].[Location] * &PlanningHorizon * [Line].[Line] ) on row, ({Measure.[Line Eff W], Measure.[Line Eff W_Created By], Measure.[Line Eff W_Creation Time], Measure.[Line Eff W_Oper Plan], Measure.[Line Eff W_Update Time], Measure.[Line Eff W_Updated By] , Measure.[Dummy]}) on column;
   - df_in_WorkCalAnnual : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] ) on row, ({Measure.[Work Cal Annual_Lock Flag], Measure.[Work Cal Annual_Week Work Days],Measure.[Dummy]}) on column;
                       (Select (&MPV  * &PlanningHorizon  * [Location].[Location] ) on row, ({Measure.[Work Cal Annual_Lock Flag], Measure.[Work Cal Annual_Week Work Days]}) on column;)
   - df_in_Week : Select ([Time].[Week]);
                  (Select (&PlanningHorizon);)
  - df_in_Version : select ([Version].[Version Name]);

* Output Table
    - df_out_WorkCalAnnual = Select ([Version].[Version Name].[CWV_MP]  * &PlanningHorizon  * [Location].[Location] ) on row, ({Measure.[Work Cal Annual_Lock Flag], Measure.[Work Cal Annual_Week Work Days]}) on column;


* 데이터 삭제
    DELETE DATA FOR MODEL [Work Cal Annual] where {Version.[Version Name].[CWV_MP]};


* 테스트 스크립트
    EXEC plugin instance [PY_UI_WorkCalAnnual] for measures {[Work Cal Annual_Lock Flag]} using scope (&MPV * &PlanningHorizon ) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


* 데이터 확인
   select (&CWV  * &PlanningHorizon  * [Location].[Location].[P630LCD] ) on row, ({Measure.[Work Cal Annual_Lock Flag], Measure.[Work Cal Annual_Week Work Days]}) on column;


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
str_instance = 'PY_UI_WorkCalAnnual'
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

def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    Logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)

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

        df_in_Location = read_csv_file("df_in_Location")
        df_in_WorkCalAnnual = read_csv_file('df_in_WorkCalAnnual')
        # df_in_LineEffSub = read_csv_file('df_in_LineEffSub')
        df_in_Week = read_csv_file('df_in_Week')
        df_in_Version = read_csv_file('df_in_Version')



    vdCommon.gfn_saveDf(df_in_Location, 'df_in_Location',True)
    vdCommon.gfn_saveDf(df_in_WorkCalAnnual, 'df_in_WorkCalAnnual',True)
    # vdCommon.gfn_saveDf(df_in_LineEffSub, 'df_in_LineEffSub',True)
    vdCommon.gfn_saveDf(df_in_Week, 'df_in_Week',True)
    vdCommon.gfn_saveDf(df_in_Version, 'df_in_Version',True)

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
    Location_Column = 'Location.[Location]'
    Location_MF_Site_Stage = 'Location.[MF Site Stage]'
    Time_Column = 'Time.[Week]'


    key_values = 'key_values'
    Work_Cal_Annual_Lock_Flag = 'Work Cal Annual_Lock Flag'
    Work_Cal_Annual_Week_Work_Days = 'Work Cal Annual_Week Work Days'

    vdCommon.gfn_stepLog('200 =====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) df_in_Location 중복 삭제 및 필터링 (Location_Column, I)
    ################################################################################################################
    vdCommon.gfn_stepLog('300 =====> STEP 3(Start) : input data machining')

    VERSION_Values = df_in_Version[VERSION_NAME_COLUMN][0]
    note(f'=====> Version Name : {VERSION_Values}')

    # Loaction, MF_Site_Stage의 중복 삭제
    df_in_Location = df_in_Location[[Location_Column]].drop_duplicates()
    # df_in_LineEffSub = df_in_LineEffSub[[Location_Column]].drop_duplicates()
    #
    # df_in_Location = pd.concat([df_in_Location, df_in_LineEffSub], axis=0).drop_duplicates()

    row_count, col_count = df_in_Location.shape
    note(f'=====> Final df_in_Location rows : {row_count} , Columns : {col_count}')
    vdCommon.gfn_saveDf(df_in_Location, 'df_in_Location',True)
    vdCommon.gfn_stepLog('300 =====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. df_in_TactTime 와 df_in_Week merge
    ################################################################################################################
    vdCommon.gfn_stepLog('400 =====> STEP 4(Start) : input data machining')
    # 로케이션과 주차를 확장하기 위한 키 설정 및 merge
    # df_in_Week 범위 설정
    week_list = df_in_Week[Time_Column].to_list()

    # Time Week 컬럼 리스트로 만들기
    df_in_Location[Time_Column] = df_in_Location.apply(lambda x : week_list, axis=1)
    # 주차 확장하기
    df_in_Location = df_in_Location.explode(Time_Column)


    row_count, col_count = df_in_Location.shape
    note(f'=====> Final df_in_Location rows : {row_count} , Columns : {col_count}')
    vdCommon.gfn_saveDf(df_in_Location, 'df_in_Location - 1',True)

    vdCommon.gfn_stepLog('400 =====> STEP 4(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 5. df_in_TactTimeW 와 Outer Merge
    ################################################################################################################
    vdCommon.gfn_stepLog( '500 =====> STEP 5(Start) : input data machining')

    # Unique한 Date Frame 추출
    df_unique = df_in_Location[~df_in_Location.set_index([Location_Column, Time_Column]).index.isin(
        df_in_WorkCalAnnual.set_index([Location_Column, Time_Column]).index)]
    # out data frame의 값 설정
    df_unique[Work_Cal_Annual_Lock_Flag] = False
    df_unique[Work_Cal_Annual_Week_Work_Days] = 5
    df_unique[VERSION_NAME_COLUMN] = VERSION_Values

    row_count, col_count = df_unique.shape
    note(f'=====> Final df_unique rows : {row_count} , Columns : {col_count}')
    vdCommon.gfn_saveDf(df_unique, 'df_unique ',True)
    vdCommon.gfn_stepLog('500 =====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) df_out_Safety_Stock  & df_unique  concat
    ################################################################################################################
    vdCommon.gfn_stepLog( '600 =====> STEP 6(Start) : input data machining')

    df_out_WorkCalAnnual = pd.concat([df_in_WorkCalAnnual, df_unique], axis=0, ignore_index=True)
    df_out_WorkCalAnnual = df_out_WorkCalAnnual[[VERSION_NAME_COLUMN, Time_Column,Location_Column,
                                                 Work_Cal_Annual_Lock_Flag,Work_Cal_Annual_Week_Work_Days]]

    vdCommon.gfn_saveDf(df_out_WorkCalAnnual, 'df_out_WorkCalAnnual ',True)
    vdCommon.gfn_stepLog('600 =====> STEP 6(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. (1) 최종 Out_Put Save
    ################################################################################################################
    vdCommon.gfn_stepLog( '700 =====> STEP 6(Start) : input data machining')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_WorkCalAnnual, 'df_out_WorkCalAnnual')

    row_count, col_count = df_out_WorkCalAnnual.shape
    note(f'=====> Final df_out_WorkCalAnnual rows : {row_count} , Columns : {col_count}')
    print_df(df_out_WorkCalAnnual, 'df_out_WorkCalAnnual')

except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg,p_log_level=LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    df_out_WorkCalAnnual = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    vdCommon.gfn_stepLog( '700 ===================== plugin Execution End =====================')

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