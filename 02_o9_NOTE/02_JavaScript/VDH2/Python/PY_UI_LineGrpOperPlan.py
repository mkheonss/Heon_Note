"""

* 프로그램명
    - PY_UI_LineGrpOperPlan

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.02.17 / ybest7.park (박병훈) / Create
- 2025.04.30 /  ybest7.park (박병훈) / VD Common 적용

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
    - df_in_LineGrpOperPlan = Select ([Version].[Version Name] * &planningHorizon * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Line Grp_Created By], Measure.[Line Grp_Creation Time], Measure.[Line Grp_Line Cnt], Measure.[Line Grp_Line Oper Cnt], Measure.[Line Grp_Update Time], Measure.[Line Grp_Updated By],Measure.[Dummy]}) on column;
    - df_in_LineGrpMap = Select ([Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Line].[Line] ) on row, ({Measure.[Line Grp Map_Enddate], Measure.[Line Grp Map_Flag], Measure.[Line Grp Map_Startdate],Measure.[Dummy] }) on column;
    - df_in_TimeWeek =  Select(&planningHorizon);


* 데이터 삭제
    DELETE DATA FOR MODEL [Line Grp Oper Plan] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_LineGrpOperPlan = Select ([Version].[Version Name].[CWV_MP] * &planningHorizon * [Location].[Location] * [Group].[Group ID]) on row, ({Measure.[Line Grp_Line Cnt], Measure.[Line Grp_Line Oper Cnt]}) on column;
                              [Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Group].[Group ID]) on row, ({Measure.[Line Grp_Line Cnt], Measure.[Line Grp_Line Oper Cnt]}) on column; ]
    - df_out_log
    - df_out_logDetail

* 테스트를 위한 데이터 삭제
   Scope: ([Version].[Version Name].[CurrentWorkingView] * &PlanningHorizon * [Location].[Location].[P306] * [Group].[Group ID].[G1]);
    Measure.[Line Grp_Line Cnt] = null;
    Measure.[Line Grp_Line Oper Cnt] = null;
   end scope;
* 테스트 스크립트

    EXEC plugin instance [PY_UI_LineGrpOperPlan] for Measures {[Line Grp_Line Cnt]} using scope (&MPV * &PlanningHorizon) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

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
str_instance = 'PY_UI_LineGrpOperPlan'
is_local = com.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level
paramOutVersion = 'CWV_MP'
########################################################################################################################
# logic start
########################################################################################################################
# Log Df 정의
df_out_log = pd.DataFrame([], columns=["Version.[Version Name]", "Python Batch.[Python Name]","Sequence.[Sequence]", "[Sequence ID].[Sequence ID]",
                                            "Python Batch Log Detail_Desc", "Python Batch Log Detail_Column", "Python Batch Log Detail_Row", "Python Batch Log Detail_DataFrame", "Python Batch Log Detail_Log Time"])

# MG에 Batch Log를 남기는 DF를 만드는 함수
def batchLog(dfDesc, df=None):
    if df is None:
        df_out_log.loc[len(df_out_log)] = [pLogInfo.split(";")[0], pLogInfo.split(";")[1], pLogInfo.split(";")[2], str(len(df_out_log) + 1), dfDesc, "", "", "", datetime.datetime.now().strftime("%H-%M-%S")]
    else:
        df_out_log.loc[len(df_out_log)] = [pLogInfo.split(";")[0], pLogInfo.split(";")[1], pLogInfo.split(";")[2], str(len(df_out_log) + 1), dfDesc + " : " + dfMemory(df), ",".join(df.columns), str(df.shape[0]), df.head(10).to_csv(index=False), datetime.datetime.now().strftime("%H-%M-%S")]

# DF 메모리 사용량 조회
def dfMemory(df):
    return str(round(df.memory_usage(deep=True).sum() / (1024**2), 2)) + " MB"


def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False)


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
Logger.Step(p_step_no=0, p_step_desc=f'plugin Execution Start')

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
    step(100, '=====> STEP 1(Start) : Input Date Frame Read')
    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_LineGrpOperPlan = read_csv_file('df_in_LineGrpOperPlan_VD18')
        df_in_LineGrpMap = read_csv_file('df_in_LineGrpMap')
        df_in_TimeWeek = read_csv_file('df_in_TimeWeek')


    # if df_in_LineGrpOperPlan.empty:
    #     raise Exception("Exception: df_in_LineGrpOperPlan is empty")
    #
    # if df_in_LineGrpMap.empty:
    #     raise Exception("Exception: df_in_LineGrpMap is empty")
    #
    # if df_in_TimeWeek.empty:
    #     raise Exception("Exception: df_in_TimeWeek is empty")

    print_df(df_in_LineGrpOperPlan, "df_in_LineGrpOperPlan input data",True)
    print_df(df_in_LineGrpMap, "df_in_LineGrpMap input data",True)
    print_df(df_in_TimeWeek, "df_in_TimeWeek input data",True)

    # pLogInfo = "CWV_MP;PY_UI_LineGrpOperPlan;1"

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    TIME_WEEK_COLUMN = 'Time.[Week]'
    GroupID_COLUMN = 'Group.[Group ID]'
    Line_COLUMN = 'Line.[Line]'
    Line_Grp_Map_Startdate = 'Line Grp Map_Startdate'
    Line_Grp_Map_Enddate = 'Line Grp Map_Enddate'
    Week_Key = 'Week Key'
    Line_Grp_Line_Cnt = 'Line Grp_Line Cnt'
    Line_Grp_Line_Oper_Cnt = 'Line Grp_Line Oper Cnt'
    Week_min = "week min"
    Strart_Qty = 'Start_Qty'
    End_Qty = 'End_Qty'
    mergeColumn= '_merge'
    right_only = 'right_only'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 1 (1) df_in_LineGrpMap 중복 삭제 및 df_in_TimeWeek로 df_in_LineGrpMap 필요한 주차 정보로 데이터 생성
    #        (2) 필요한 column 명 선택
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    # 기간 설정을 위한 Min / Max 설정
    week_min = df_in_TimeWeek[TIME_WEEK_COLUMN].min()
    week_max = df_in_TimeWeek[TIME_WEEK_COLUMN].max()

    # Start & End 주차 빈 값 설정
    df_in_LineGrpMap[Line_Grp_Map_Startdate] = df_in_LineGrpMap[Line_Grp_Map_Startdate].fillna(week_min).astype(int)
    df_in_LineGrpMap[Line_Grp_Map_Enddate] = df_in_LineGrpMap[Line_Grp_Map_Enddate].fillna(week_max).astype(int)

    print_df(df_in_LineGrpMap, 'df_in_LineGrpMap Step 1 ',True)

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 2. (1) Line Grp Map_Startdate 기준으로 Line 집계
    #         (2) df_in_LineGrpMapMaster 와 merge해서 Line_Grp_Map_Startdate 정보 정리
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : input data machining')

    # Key_columns 설정
    Grain_col = [VERSION_NAME_COLUMN, LOCATION_COLUMN, GroupID_COLUMN]
    # 중복 삭제
    df_in_LineGrpOperPlan_temp = df_in_LineGrpOperPlan[Grain_col]
    df_in_LineGrpOperPlan_temp = df_in_LineGrpOperPlan_temp.drop_duplicates(subset=Grain_col)
    print_df(df_in_LineGrpOperPlan_temp, 'df_in_LineGrpOperPlan_temp Step 1 ', True)
    df_in_LineGrpMap_Temp = df_in_LineGrpMap[Grain_col]
    df_in_LineGrpMap_Temp = df_in_LineGrpMap_Temp.drop_duplicates(subset=Grain_col)
    print_df(df_in_LineGrpMap_Temp, 'df_in_LineGrpMap_Temp Step 1 ', True)

    # df_in_LineGrpMap 중 df_in_LineGrpOperPlan 없는 것 필터링
    df_in_LineGrpOperPlan_temp_index = df_in_LineGrpOperPlan_temp.set_index(Grain_col).index
    df_in_LineGrpMap_Temp_index = df_in_LineGrpMap_Temp.set_index(Grain_col).index
    df_in_LineGrpMap_Temp = df_in_LineGrpMap_Temp[~df_in_LineGrpMap_Temp_index.isin(df_in_LineGrpOperPlan_temp_index)]

    print_df(df_in_LineGrpMap_Temp, 'df_in_LineGrpMap_Temp Step 2 ',True)

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) Line Grp Map_Enddate 기준으로 Line 집계
    #         (2) df_in_LineGrpMapMaster 와 merge해서 Line_Grp_Map_Enddate 정보 정리
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : input data machining')

    # 필터된 내용 과 Start & End 주차 데이터 merge
    df_in_LineGrpMap_Temp = df_in_LineGrpMap_Temp.merge(df_in_LineGrpMap, on=Grain_col, how='left')

    print_df(df_in_LineGrpMap_Temp, 'df_in_LineGrpMap_Temp Step 2-1 ')
    # Start ~ End 주차로 확장 / df_in_LineGrpMap_Temp가 빈 테이블이면  빈 테이블 반환
    if not df_in_LineGrpMap_Temp.empty:
        df_in_LineGrpMap_Temp['expand_week'] = df_in_LineGrpMap_Temp.apply(
            lambda x: np.arange(x[Line_Grp_Map_Startdate], x[Line_Grp_Map_Enddate] + 1), axis=1)
    else:
        df_in_LineGrpMap_Temp['expand_week'] = []
    df_in_LineGrpMap_Temp = df_in_LineGrpMap_Temp.explode('expand_week')

    print_df(df_in_LineGrpMap_Temp, 'df_in_LineGrpMap_Temp Step 2 ')

    # merge를 위한 데이터 타입 통일
    df_in_TimeWeek[TIME_WEEK_COLUMN] = df_in_TimeWeek[TIME_WEEK_COLUMN].astype(str)
    df_in_LineGrpMap_Temp['expand_week'] =  df_in_LineGrpMap_Temp['expand_week'].astype(str)

    # 주차 정보와 확인
    df_in_LineGrpMap_Temp = df_in_LineGrpMap_Temp.merge(df_in_TimeWeek, left_on='expand_week',
                                                        right_on=TIME_WEEK_COLUMN, how='inner').drop(
        columns=['expand_week', Line_Grp_Map_Startdate, Line_Grp_Map_Enddate, 'Dummy',
                 'Line Grp Map_Flag'])

    print_df(df_in_LineGrpMap_Temp, 'df_in_LineGrpMap_Temp Step 3',True)

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. (1) df_in_LineGrpMap_start 와 df_in_LineGrpMap_end merge 하여 필요한 Line 정보 추출
    #         (2) Line_Grp_Line_Cnt 값 설정 (전 주의 수량 + 금주 추라 라인 수 ) - 종료 라인 수
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : input data machining')

    # start 라인 수량 확인
    df_in_LineGrpMap_Temp = df_in_LineGrpMap_Temp.groupby(
        [VERSION_NAME_COLUMN, LOCATION_COLUMN, GroupID_COLUMN, TIME_WEEK_COLUMN]).size().reset_index(name=Strart_Qty)

    df_in_LineGrpMap_Temp['Shift_Line_Cnt'] = df_in_LineGrpMap_Temp[Strart_Qty].shift(1)
    mask = (df_in_LineGrpMap_Temp[VERSION_NAME_COLUMN] != df_in_LineGrpMap_Temp[VERSION_NAME_COLUMN].shift(1)) | \
           (df_in_LineGrpMap_Temp[LOCATION_COLUMN] != df_in_LineGrpMap_Temp[LOCATION_COLUMN].shift(1)) | \
           (df_in_LineGrpMap_Temp[GroupID_COLUMN] != df_in_LineGrpMap_Temp[GroupID_COLUMN].shift(1))

    df_in_LineGrpMap_Temp.loc[mask, 'Shift_Line_Cnt'] = pd.NA

    df_in_LineGrpMap_Temp['Shift_Line_Cnt'] = df_in_LineGrpMap_Temp['Shift_Line_Cnt'].bfill().astype(int)

    df_in_LineGrpMap_Temp[Line_Grp_Line_Cnt] = np.where(
        df_in_LineGrpMap_Temp[Strart_Qty] == df_in_LineGrpMap_Temp['Shift_Line_Cnt'],
        df_in_LineGrpMap_Temp['Shift_Line_Cnt'],
        df_in_LineGrpMap_Temp[Strart_Qty] - df_in_LineGrpMap_Temp['Shift_Line_Cnt'])

    df_in_LineGrpMap_Temp[Line_Grp_Line_Oper_Cnt] = df_in_LineGrpMap_Temp[Line_Grp_Line_Cnt]
    df_in_LineGrpMap_Temp = df_in_LineGrpMap_Temp.drop(columns=['Shift_Line_Cnt', Strart_Qty], axis=1)

    print_df(df_in_LineGrpMap_Temp, 'df_in_LineGrpMap_Temp Step 4',True)

    step(600, '=====> STEP 6(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 5. (1) df_in_LineGrpOperPlan 와 df_in_LineGrpMap merge 해서 df_in_LineGrpMap에 있는 데이터만 추출
    ###############################################################################################################
    step(700, '=====> STEP 7(Start) : input data machining')

    df_out_LineGrpOperPlan = df_in_LineGrpMap_Temp.copy()

    print_df(df_out_LineGrpOperPlan, 'df_out_LineGrpOperPlan Step 1',True)

    step(700, '=====> STEP 7(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 6. (1) 최종 Out_Put Save
    ################################################################################################################
    step(800, '=====> STEP 8(Start) : input data machining')

    print_df(df_out_LineGrpOperPlan, 'df_out_LineGrpOperPlan',True)

    row_count, col_count = df_out_LineGrpOperPlan.shape
    note(f'=====> Final df_out_LineGrpOperPlan rows : {row_count} , Columns : {col_count}')


    if is_local:
        Logger.Step(p_step_no=800, p_step_desc=f'Final Output Tabel create')
        print_df(df_out_LineGrpOperPlan, 'df_out_LineGrpOperPlan',True)



except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_LineGrpOperPlan = pd.DataFrame([], columns=[])

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