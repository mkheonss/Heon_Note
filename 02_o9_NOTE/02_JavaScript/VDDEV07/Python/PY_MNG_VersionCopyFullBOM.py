

"""

* 프로그램명
    - PY_MNG_VersionCopyFullBOM

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.11.5 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_FullBOM = Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item] * [To Location].[To Location] * [Location].[Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, ({Measure.[Full BOM_Acil Date], Measure.[Full BOM_Avail Qty], Measure.[Full BOM_BOM Date], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_Consume Qty], Measure.[Full BOM_Consume UOM], Measure.[Full BOM_Creation Time], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Flag], Measure.[Full BOM_HQ Dev Purchaser], Measure.[Full BOM_HQ Purchaser], Measure.[Full BOM_Issue Date], Measure.[Full BOM_MRP Controller], Measure.[Full BOM_Part Eff Enddate], Measure.[Full BOM_Part Eff Startdate], Measure.[Full BOM_Prty], Measure.[Full BOM_Purchaser], Measure.[Full BOM_SOP SET Qty], Measure.[Full BOM_SOP Version Qty], Measure.[Full BOM_SRA Date], Measure.[Full BOM_Safety Date], Measure.[Full BOM_Unit], Measure.[Full BOM_Update Time], Measure.[Full BOM_Valid]}) on column;

* Output Table
   - df_out_FullBOM = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [To Location].[To Location] * [Location].[Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, ({Measure.[Full BOM_Acil Date], Measure.[Full BOM_Avail Qty], Measure.[Full BOM_BOM Date], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_Consume Qty], Measure.[Full BOM_Consume UOM], Measure.[Full BOM_Creation Time], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Flag], Measure.[Full BOM_HQ Dev Purchaser], Measure.[Full BOM_HQ Purchaser], Measure.[Full BOM_Issue Date], Measure.[Full BOM_MRP Controller], Measure.[Full BOM_Part Eff Enddate], Measure.[Full BOM_Part Eff Startdate], Measure.[Full BOM_Prty], Measure.[Full BOM_Purchaser], Measure.[Full BOM_SOP SET Qty], Measure.[Full BOM_SOP Version Qty], Measure.[Full BOM_SRA Date], Measure.[Full BOM_Safety Date], Measure.[Full BOM_Unit], Measure.[Full BOM_Update Time], Measure.[Full BOM_Valid]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MNG_VersionCopyFullBOM] for Measures {[Full BOM_Acil Date]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView"})) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};



실행 전 프로시져를 통해 MF Site 삭제  필요

"""


########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
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

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MNG_VersionCopyFullBOM'
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

        df_in_FullBOM = read_csv_file('df_in_FullBOM')


    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    CWV = 'CurrentWorkingView'

    if df_in_FullBOM.empty:
        raise Exception("Exception: df_in_FullBOM is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    dfs = {'df_in_FullBOM': df_in_FullBOM}

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

    df_out_FullBOM = out_dfs['df_out_FullBOM'] if 'df_out_FullBOM' in out_dfs else None



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
    raise Exception(e)

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
                       f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(800, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()
