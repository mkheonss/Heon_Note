

"""

* 프로그램명
    - PY_MNG_VersionCopyBOD

* 수정일 : 20204-11-20

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.11.18 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_BODList = Select ( &CWV * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Created By], Measure.[BOD List_Creation Time], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT], Measure.[BOD List_Update Time], Measure.[BOD List_Updated By]}) on column.filter(Measure.[BOD List_BOD Valid] == "Y" && ( (isnull(Measure.[BOD List_Eff Enddate])||Measure.[BOD List_Eff Enddate]> Measure.[W Plan Start Date]) && (isnull(Measure.[BOD List_Eff Startdate])||Measure.[BOD List_Eff Startdate]< Measure.[W Plan End Date]))) ;
   - df_in_BODItem = Select (&CWV  * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Asn], Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT], Measure.[BOD Item_BOD LT_Inherit], Measure.[BOD Item_Created By], Measure.[BOD Item_Creation Time], Measure.[BOD Item_Cur Status], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Master BOD LT], Measure.[BOD Item_Master Prty], Measure.[BOD Item_Master Ship LT], Measure.[BOD Item_Master Shipment LT], Measure.[BOD Item_Master Tran Time], Measure.[BOD Item_Min Lot Qty], Measure.[BOD Item_Multi Lot Qty], Measure.[BOD Item_Need Check], Measure.[BOD Item_Period SET Detail], Measure.[BOD Item_Period1], Measure.[BOD Item_Period2], Measure.[BOD Item_Period3], Measure.[BOD Item_Priority], Measure.[BOD Item_Priority_Inherit], Measure.[BOD Item_Prod Item], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Shipment LT_Inherit], Measure.[BOD Item_Time Phased BOD], Measure.[BOD Item_Time Phased Prty], Measure.[BOD Item_Time Phased Shipment], Measure.[BOD Item_To Item], Measure.[BOD Item_Update Time], Measure.[BOD Item_Updated By]}) on column.filter((isnull(Measure.[BOD Item_Eff Enddate])||Measure.[BOD Item_Eff Enddate]> Measure.[W Plan Start Date])&&(isnull(Measure.[BOD Item_Eff Startdate])||Measure.[BOD Item_Eff Startdate]< Measure.[W Plan End Date]));


* Output Table
    - df_out_BODList = Select ( &MPV * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Created By], Measure.[BOD List_Creation Time], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT], Measure.[BOD List_Update Time], Measure.[BOD List_Updated By]}) on column.filter(Measure.[BOD List_BOD Valid] == "Y" && ( (isnull(Measure.[BOD List_Eff Enddate])||Measure.[BOD List_Eff Enddate]> Measure.[W Plan Start Date]) && (isnull(Measure.[BOD List_Eff Startdate])||Measure.[BOD List_Eff Startdate]< Measure.[W Plan End Date]))) ;
    - df_out_BODItem = Select (&MPV  * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Asn], Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT], Measure.[BOD Item_BOD LT_Inherit], Measure.[BOD Item_Created By], Measure.[BOD Item_Creation Time], Measure.[BOD Item_Cur Status], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Master BOD LT], Measure.[BOD Item_Master Prty], Measure.[BOD Item_Master Ship LT], Measure.[BOD Item_Master Shipment LT], Measure.[BOD Item_Master Tran Time], Measure.[BOD Item_Min Lot Qty], Measure.[BOD Item_Multi Lot Qty], Measure.[BOD Item_Need Check], Measure.[BOD Item_Period SET Detail], Measure.[BOD Item_Period1], Measure.[BOD Item_Period2], Measure.[BOD Item_Period3], Measure.[BOD Item_Priority], Measure.[BOD Item_Priority_Inherit], Measure.[BOD Item_Prod Item], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Shipment LT_Inherit], Measure.[BOD Item_Time Phased BOD], Measure.[BOD Item_Time Phased Prty], Measure.[BOD Item_Time Phased Shipment], Measure.[BOD Item_To Item], Measure.[BOD Item_Update Time], Measure.[BOD Item_Updated By]}) on column.filter((isnull(Measure.[BOD Item_Eff Enddate])||Measure.[BOD Item_Eff Enddate]> Measure.[W Plan Start Date])&&(isnull(Measure.[BOD Item_Eff Startdate])||Measure.[BOD Item_Eff Startdate]< Measure.[W Plan End Date]));


* 테스트 스크립트
    EXEC plugin instance [PY_MNG_VersionCopyBOD] for Measures {[BOD List_BOD Frozen]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView"})) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};



실행 전 프로시져를 통해 MF Site 삭제  필요

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

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MNG_VersionCopyBOD'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

def print_df(df, df_name, _localFlag=True):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')


# Logger.debug(f'[START] {str_instance}')
# Logger.Start()
# note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
# step(0, '===================== plugin Execution Start =====================')
# tracemalloc.start()

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
    # # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_BODList = read_csv_file('df_in_BODList')
        df_in_BODItem = read_csv_file('df_in_BODItem')



    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    CWV = 'CurrentWorkingView'

    # if df_in_BODList.empty:
    #     raise Exception("Exception: df_in_BODList is empty")
    # if df_in_BODItem.empty:
    #     raise Exception("Exception: df_in_BODItem is empty")


    note(f'=====> paramOutVersion : {paramOutVersion}')

    dfs = {'df_in_BODList': df_in_BODList, 'df_in_BODItem': df_in_BODItem}

    for name, df in dfs.items():
        print_df(df, name)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2 (1) 데이터 프레임 변수 지정 및 이름 변경
    ################################################################################################################

    step(200, '=====> STEP 2(Start) : input data machining')

    out_dfs = {}
    for name, df in dfs.items():
        df[df[VERSION_NAME_COLUMN]==CWV].copy()
        #
        # if name == 'df_in_BODList':
        #     df = df[((df['BOD List_Shipment LT']==0 )| (df['BOD List_Shipment LT'] % 7 ==0)) &
        #             ((df['BOD List_BOD LT']==0 )| (df['BOD List_BOD LT'] % 7 ==0))].copy()
        #     df.loc[:, 'BOD List_Shipment LT'] = df['BOD List_Shipment LT'].fillna(0)
        #     df.loc[:, 'BOD List_BOD LT'] = df['BOD List_BOD LT'].fillna(0)
        #     dfs[name] = df

        df[VERSION_NAME_COLUMN] = paramOutVersion
        new_name = name.replace('in', 'out')
        out_dfs[new_name] = df

    for name, df in out_dfs.items():
        print_df(df, f'{name}')

    for name, df in out_dfs.items():
        row_count, col_count = df.shape
        note(f'=====> Final {name} rows : {row_count} , Columns : {col_count}')

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3 out 데이터 프레임 크기 확인 및 저장 (Live Server 특성상 반복문 사용 불가 - out Frame 설정 필요
    ###############################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    df_out_BODList = out_dfs['df_out_BODList'] if 'df_out_BODList' in out_dfs else None
    df_out_BODItem = out_dfs['df_out_BODItem'] if 'df_out_BODItem' in out_dfs else None

    print_df(df_out_BODList, 'df_out_BODList')
    print_df(df_out_BODItem, 'df_out_BODItem')


    if is_local:
        note(f'=====> Final output table create')
        for name, df in out_dfs.items():
            if df is not None:
                save_csv_file(df, name)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. 종료
    ################################################################################################################

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_BODList = pd.DataFrame([], columns=[])
    df_out_BODItem = pd.DataFrame([], columns=[])

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