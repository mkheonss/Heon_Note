"""

* 프로그램명
    - PY_UI_WorkCalLineGrp

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.01.07 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
    - df_in_LineGrpOperPlan = Select ([Version].[Version Name] * &PlanningHorizon * [Location].[Location] * [Group].[Group ID]) on row, ({Measure.[Line Grp_Line Cnt], Measure.[Line Grp_Line Oper Cnt],Measure.[Dummy] }) on column;
                     [Select ([Version].[Version Name].[CWV_MP] * &PlanningHorizon * [Location].[Location] * [Group].[Group ID]) on row, ({Measure.[Line Grp_Line Cnt], Measure.[Line Grp_Line Oper Cnt],Measure.[Dummy]}) on column;]
    - df_in_LineGrpMap  = Select ([Version].[Version Name]* [Location].[Location] * [Group].[Group ID] * [Line].[Line] ) on row, ({Measure.[Line Grp Map_Enddate], Measure.[Line Grp Map_Flag], Measure.[Line Grp Map_Startdate],Measure.[Dummy]}) on column;
                         [ Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Group].[Group ID] * [Line].[Line] ) on row, ({Measure.[Line Grp Map_Enddate], Measure.[Line Grp Map_Flag], Measure.[Line Grp Map_Startdate],Measure.[Dummy]}) on column;]
    - df_in_TimeWeek = select (&PlanningHorizon);
    - df_in_WorkCallLineGrp = Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Group].[Group ID] * [Line].[Line Type] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal LineGrp_Lock Flag], Measure.[Work Cal LineGrp_Time],Measure.[Dummy]}) on column;


* 데이터 삭제
    DELETE DATA FOR MODEL [001.021W Solver Inputs WIP Capacity] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_WorkCallLineGrp = Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Group].[Group ID] * [Line].[Line Type] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal LineGrp_Lock Flag], Measure.[Work Cal LineGrp_Time]}) on column;
                              [Select ([Version].[Version Name].[CurrentWorkingView]  * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Group].[Group ID] * [Line].[Line Type] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal LineGrp_Lock Flag], Measure.[Work Cal LineGrp_Time]}) on column;];

* 테스트를 위한 데이터 삭제
   Scope: ([Version].[Version Name].[CurrentWorkingView] * &PlanningHorizon * [Location].[Location].[P306] * [Group].[Group ID].[G1]);
    Measure.[Line Grp_Line Cnt] = null;
    Measure.[Line Grp_Line Oper Cnt] = null;
   end scope;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_WorkCalLineGrp] for measures {[Work Cal LineGrp_Lock Flag]} using scope (&MPV * &PlanningHorizon) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;

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

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_WorkCalLineGrp'
is_local = com.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
Logger_level = com.G_log_level
paramOutVersion = 'CWV_MP'
########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def note(string, p_log_level=Logger_level.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')


def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, Logger, is_local, log_path)


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


def datetime_check_series(date_series):
    # 가능한 형식들을 순서대로 시도
    date_formats = ['%m/%d/%Y %I:%M:%S %p', '%Y/%m/%d %I:%M:%S %p', '%Y-%m-%d %H:%M:%S']

    # 모든 시도가 실패했을 때 NaT로 초기화
    parsed_dates = pd.Series(pd.NaT, index=date_series.index)

    for fmt in date_formats:
        # 형식을 시도하여 변환하고, NaT 값이 없는 경우에 대해서만 변환을 유지
        new_dates = pd.to_datetime(date_series, format=fmt, errors='coerce')
        parsed_dates = parsed_dates.combine_first(new_dates)

    return parsed_dates

# Logger.debug(f'[START] {str_instance}')
# Logger.Start()
# Logger.Step(p_step_no=0, p_step_desc=f'plugin Execution Start')

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
    # Value 변수 선언
    # PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_LineGrpOperPlan = read_csv_file('df_in_LineGrpOperPlan')
        df_in_LineGrpMap = read_csv_file('df_in_LineGrpMap')
        df_in_TimeWeek = read_csv_file('df_in_TimeWeek')
        df_in_WorkCallLineGrp = read_csv_file('df_in_WorkCallLineGrp')


    # if df_in_LineGrpOperPlan.empty:
    #     raise Exception("Exception: df_in_LineGrpOperPlan is empty")
    #
    # if df_in_LineGrpMap.empty:
    #     raise Exception("Exception: df_in_LineGrpMap is empty")
    #
    # if df_in_TimeWeek.empty:
    #     raise Exception("Exception: df_in_TimeWeek is empty")


    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    TIME_WEEK_COLUMN = 'Time.[Week]'
    GroupID_COLUMN = 'Group.[Group ID]'
    Line_COLUMN = 'Line.[Line]'
    WorkType_COLUMN = 'Work Type.[Work Type]'
    LineType_COLUMN = 'Line.[Line Type]'
    DataSet_COLUMN = 'Data Set.[Data Set]'

    Week_Key = 'Week Key'
    Work_Cal_LineGrp_Lock_Flag = 'Work Cal LineGrp_Lock Flag'
    Work_Cal_LineGrp_Time = 'Work Cal LineGrp_Time'
    Line_Grp_Line_Cnt = 'Line Grp_Line Cnt'
    Line_Grp_Line_Oper_Cnt = 'Line Grp_Line Oper Cnt'

    daily_work = "Normal RT"
    daily_special_work = "Normal OT"
    special_work = "Special OT"
    special_work_plus = 'TwoShift OT'
    main = 'MAIN'
    master = 'MP'
    mergeColumn = '_merge'
    right_only = 'right_only'


    Logger.Step(p_step_no=100, p_step_desc=f'in Table Log')
    # 입력 변수 확인용 로그
    # Logger.Note(p_note=f'paramOutVersion : {paramOutVersion}', p_log_level=Logger_level.debug())
    Logger.PrintDF(p_df=df_in_LineGrpOperPlan, p_df_name='df_in_LineGrpOperPlan info',
                   p_log_level=Logger_level.debug(), p_format=1)
    Logger.Step(p_step_no=110, p_step_desc=f'df_in_LineGrpOperPlan Table Log')
    Logger.PrintDF(p_df=df_in_LineGrpMap, p_df_name='df_in_LineGrpMap info',
                   p_log_level=Logger_level.debug(), p_format=1)
    Logger.Step(p_step_no=120, p_step_desc=f'df_in_LineGrpMap Table Log')
    Logger.PrintDF(p_df=df_in_TimeWeek, p_df_name='df_in_TimeWeek info',
                   p_log_level=Logger_level.debug(), p_format=1)
    Logger.Step(p_step_no=130, p_step_desc=f'df_in_TimeWeek Table Log')
    Logger.PrintDF(p_df=df_in_WorkCallLineGrp, p_df_name='df_in_WorkCallLineGrp info',
                   p_log_level=Logger_level.debug(), p_format=1)
    Logger.Step(p_step_no=130, p_step_desc=f'df_in_WorkCallLineGrp Table Log')

    ################################################################################################################
    # Step 1 (1) df_in_LineGrpMap 중복 삭제 및 df_in_TimeWeek로 df_in_LineGrpMap 필요한 주차 정보로 데이터 생성
    #        (2) 필요한 column 명 선택
    ################################################################################################################
    df_in_LineGrpMap[Week_Key] = 1
    df_in_TimeWeek[Week_Key] = 1
    week_min = df_in_TimeWeek[TIME_WEEK_COLUMN].min()
    week_max = df_in_TimeWeek[TIME_WEEK_COLUMN].max()
    df_in_LineGrpMapMaster = df_in_LineGrpMap.drop_duplicates(
        subset=[VERSION_NAME_COLUMN, LOCATION_COLUMN, GroupID_COLUMN]).merge(df_in_TimeWeek, on=Week_Key, how='inner')
    df_in_LineGrpMapMaster = df_in_LineGrpMapMaster[
        [VERSION_NAME_COLUMN, LOCATION_COLUMN, GroupID_COLUMN, TIME_WEEK_COLUMN]]

    Logger.PrintDF(p_df=df_in_LineGrpMapMaster, p_df_name='df_in_LineGrpMapMaster Step 1',
                   p_log_level=Logger_level.debug(), p_format=1)

    ################################################################################################################
    # Step 2. (1) output 처리를 위한 전처리
    #         (2) Work Type 정의 , df_in_LineGrpMapMaster Frame 확장 (df_in_LineGrpMapMaster * work Type) 만큼
    #         (3) WorkType_COLUMN 값 정의 및 각종 데이터 값 설정
    ################################################################################################################
    work_type = [daily_work, daily_special_work, special_work, special_work_plus]

    work_type_var = work_type * len(df_in_LineGrpMapMaster)
    df_in_LineGrpMapMaster = df_in_LineGrpMapMaster.loc[
        df_in_LineGrpMapMaster.index.repeat(len(work_type))].reset_index(drop=True)
    df_in_LineGrpMapMaster[WorkType_COLUMN] = work_type_var

    df_in_LineGrpMapMaster[LineType_COLUMN] = main
    df_in_LineGrpMapMaster[DataSet_COLUMN] = master
    df_in_LineGrpMapMaster[Work_Cal_LineGrp_Lock_Flag] = False
    df_in_LineGrpMapMaster[Work_Cal_LineGrp_Time] = 0
    df_in_LineGrpMapMaster = df_in_LineGrpMapMaster[
        df_in_LineGrpMapMaster[TIME_WEEK_COLUMN].between(week_min, week_max)]

    Logger.PrintDF(p_df=df_in_LineGrpMapMaster, p_df_name='df_in_LineGrpMapMaster Step 2',
                   p_log_level=Logger_level.debug(), p_format=1)

    ################################################################################################################
    # Step 3. (1) df_out_WorkCallLineGrp 과 df_in_LineGrpOperPlan merge하여 없는 데이터값 추출
    ################################################################################################################

    df_in_LineGrpOperPlan = df_in_LineGrpOperPlan.drop_duplicates(
        subset=[VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, GroupID_COLUMN]).drop(
        columns=[Line_Grp_Line_Cnt, Line_Grp_Line_Oper_Cnt], axis=1)
    Logger.PrintDF(p_df=df_in_LineGrpOperPlan, p_df_name='df_out_WorkCallLineGrp Step 3-1',
                   p_log_level=Logger_level.debug(), p_format=1)

    # index_col = [VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, Line_COLUMN]
    # df_in_LineGrpMapMaster_index = df_in_LineGrpMapMaster.set_index(index_col).index
    # df_in_LineGrpOperPlan_index = df_in_LineGrpOperPlan.set_index(index_col).index
    # df_out_WorkCallLineGrp = df_in_LineGrpMapMaster[~df_in_LineGrpMapMaster_index.isin(df_in_LineGrpOperPlan_index)]


    df_out_WorkCallLineGrp = df_in_LineGrpMapMaster.merge(df_in_LineGrpOperPlan,
                                                          on =[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN,
                                                               LOCATION_COLUMN, GroupID_COLUMN],
                                                          how='outer')

    index_col = [VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, WorkType_COLUMN, GroupID_COLUMN, LineType_COLUMN]
    df_in_WorkCallLineGrp_index = df_in_WorkCallLineGrp.set_index(index_col).index
    df_out_WorkCallLineGrp_index = df_out_WorkCallLineGrp.set_index(index_col).index
    df_out_WorkCallLineGrp_index = df_in_WorkCallLineGrp[~df_in_WorkCallLineGrp_index.isin(df_out_WorkCallLineGrp_index)]

    Logger.PrintDF(p_df=df_out_WorkCallLineGrp, p_df_name='df_out_WorkCallLineGrp Step 3',
                   p_log_level=Logger_level.debug(), p_format=1)

    ################################################################################################################
    # Step 4. (1) df_out_WorkCallLineGrp 설정 및 데이터 프레임 순서 지정
    ################################################################################################################
    df_out_WorkCallLineGrp = df_out_WorkCallLineGrp[[VERSION_NAME_COLUMN,TIME_WEEK_COLUMN, LOCATION_COLUMN,
                                                     WorkType_COLUMN, GroupID_COLUMN, LineType_COLUMN,
                                                     DataSet_COLUMN, Work_Cal_LineGrp_Lock_Flag,
                                                     Work_Cal_LineGrp_Time]]


    Logger.PrintDF(p_df=df_out_WorkCallLineGrp, p_df_name='df_out_WorkCallLineGrp Step 4',
                   p_log_level=Logger_level.debug(), p_format=1)

    Logger.Step(p_step_no=200, p_step_desc=f'df_out_WorkCallLineGrp Table Log Step 3')


    if is_local:
        Logger.Step(p_step_no=300, p_step_desc=f'Final Output Tabel create')
        save_csv_file(df_out_WorkCallLineGrp, 'df_out_WorkCallLineGrp')


    row_count, col_count = df_out_WorkCallLineGrp.shape
    Logger.Note(p_note=f'df_out_WorkCallLineGrp rows : {row_count} , Columns : {col_count}',
                p_log_level=Logger_level.info())


except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg, p_log_level=Logger_level.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_WorkCallLineGrp = pd.DataFrame([], columns=[])

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