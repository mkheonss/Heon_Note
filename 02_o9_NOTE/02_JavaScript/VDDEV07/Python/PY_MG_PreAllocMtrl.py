

"""

* 프로그램명
    - PY_MG_PreAllocMtrl

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.10.11 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
     - df_in_PreAlloc = Select ( [Version].[Version Name] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const_Grp Description]}) on column;
    - df_in_PACMtrl  =  select(&PACMtrl);


* 데이터 삭제
     DELETE DATA FOR MODEL [Quota Anl Chart] where {Version.[Version Name].[CWV_MP]};
     DELETE DATA FOR MODEL [Quota Anl] where {Version.[Version Name].[CWV_MP]};

* Output Table
    df_out_ItemMtrl = Select (&MPV * [MP Batch_Sequence].[MP Batch_Sequence_ID] ) on row, ({Measure.[MP Batch_Item Mtrl_Const Type], Measure.[MP Batch_Item Mtrl_Item], Measure.[MP Batch_Item Mtrl_Item Mtrl Stage], Measure.[MP Batch_Item Mtrl_Item Type], Measure.[MP Batch_Item Mtrl_Material Group]}) on column;

* 테스트를 위한 데이터 삭제
   Scope: ([Version].[Version Name].[CurrentWorkingView] * &PlanningHorizon * [Location].[Location].[P306] * [Group].[Group ID].[G1]);
    Measure.[Line Grp_Line Cnt] = null;
    Measure.[Line Grp_Line Oper Cnt] = null;
   end scope;
* 테스트 스크립트
    EXEC plugin instance [PY_MG_PreAllocMtrl] for Measures {[MP Batch_Item Mtrl_Const Type]} using scope ( &MPV ) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};

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
str_instance = 'PY_MG_PreAllocMtrl'
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
    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_PreAlloc = read_csv_file('df_in_PreAlloc')
        df_in_PACMtrl = read_csv_file('df_in_PACMtrl')

    if df_in_PreAlloc.empty:
        raise Exception("Exception: df_in_PreAlloc is empty")

    if df_in_PACMtrl.empty:
        raise Exception("Exception: df_in_PACMtrl is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_PreAlloc, 'df_in_PreAlloc')
    print_df(df_in_PACMtrl, 'df_in_PACMtrl')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Item_COLUMN = 'Item.[Item]'
    Item_Group_COLUMN = 'Item.[Material Group]'
    GROUP_ID_COLUMN = 'Group.[Group ID]'
    GROUP_NAME_COLUMN = 'Group.[Group Name]'
    GROUP_Type_COLUMN = 'Group.[Group Type]'
    Version_COLUMN = 'Version.[Version Name]'
    MP_SEQUENCE_ID_COLUMN = 'MP Batch_Sequence.[MP Batch_Sequence_ID]'
    MP_Batch_Item_Mtrl_Const_Type = 'MP Batch_Item Mtrl_Const Type'
    MP_Batch_Item_Mtrl_Item = 'MP Batch_Item Mtrl_Item'
    MP_Batch_Item_Mtrl_Item_Mtrl_Stage = 'MP Batch_Item Mtrl_Item Mtrl Stage'
    MP_Batch_Item_Mtrl_Item_Type = 'MP Batch_Item Mtrl_Item Type'
    MP_Batch_Item_Mtrl_Material_Group = 'MP Batch_Item Mtrl_Material Group'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) 날짜 데이터 설정을 위한 전처리 → 현재 Sever Error 발생
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    df_in_PreAlloc.drop_duplicates(subset=[GROUP_ID_COLUMN], keep='first', inplace=True)
    df_in_PreAlloc[Item_COLUMN] = df_in_PreAlloc[GROUP_ID_COLUMN]
    df_in_PreAlloc = df_in_PreAlloc[~df_in_PreAlloc[Item_COLUMN].isin(df_in_PACMtrl[Item_COLUMN].unique())]
    df_in_PreAlloc = df_in_PreAlloc.drop_duplicates(subset=Item_COLUMN)
    df_in_PreAlloc[MP_SEQUENCE_ID_COLUMN] = range(1, len(df_in_PreAlloc) + 1)
    df_in_PreAlloc[MP_Batch_Item_Mtrl_Item] = df_in_PACMtrl[Item_COLUMN]
    df_in_PreAlloc[MP_Batch_Item_Mtrl_Item_Type] = 'RawMaterials'
    df_in_PreAlloc[MP_Batch_Item_Mtrl_Material_Group] = 'PAC'
    df_in_PreAlloc[MP_Batch_Item_Mtrl_Const_Type] = 'Hard'
    df_in_PreAlloc[MP_Batch_Item_Mtrl_Item_Mtrl_Stage] = 'PAC'
    df_in_PreAlloc[Version_COLUMN] = paramOutVersion
    df_out_ItemMtrl = df_in_PreAlloc[
        [Version_COLUMN, MP_SEQUENCE_ID_COLUMN, MP_Batch_Item_Mtrl_Const_Type, MP_Batch_Item_Mtrl_Item,
         MP_Batch_Item_Mtrl_Item_Mtrl_Stage, MP_Batch_Item_Mtrl_Item_Type, MP_Batch_Item_Mtrl_Material_Group]]

    print_df(df_out_ItemMtrl, 'df_out_ItemMtrl')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) 최종 Out_Put Save
    ################################################################################################################

    row_count, col_count = df_out_ItemMtrl.shape
    note(f'=====> Final df_out_ItemMtrl rows : {row_count} , Columns : {col_count}')
    print_df(df_out_ItemMtrl, 'df_out_ItemMtrl')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_ItemMtrl, 'df_out_ItemMtrl')


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
    step(400, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()
