

"""

* 프로그램명
    - PY_MG_INFLocation

* 내용
    - Soft Constraint 용 가상 Infinite Location 생성을 위한 Member Buffer입력

* 변경이력
- 2024.09.15 / 박병훈 / Create

* Input
-

* Flow Summary
    STEP1.Infinite 대상 가상 Location 발췌 및 Measure Insert
* Execution

* Input Table
  - df_in_MtrlConstType = Select ([Version].[Version Name].[CWV_MP] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Batch_Type]})  on column.filter(Measure.[Mtrl Const Type Batch_Type]== "Soft");
  - df_in_BODItemMtrlFull = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_Lot Size]}) on column;


* 데이터 삭제
     DELETE DATA FOR MODEL [MP Batch_INF Location Bulk Member Creation] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_INFLoc = Select ([Version].[Version Name].[CWV_MP] * [MP Batch_Sequence].[MP Batch_Sequence_ID] ) on row, ({Measure.[MP Batch_INF Location_Location], Measure.[MP Batch_INF Location_Location Category], Measure.[MP Batch_INF Location_Location Key], Measure.[MP Batch_INF Location_Location Type], Measure.[MP Batch_INF Location_Site Stage]}) on column;

* 테스트를 위한 데이터 삭제
   - DELETE DATA FOR MODEL [MP Batch_INF Location Bulk Member Creation] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
    EXEC plugin instance [PY_MG_INFLocation] for measures {[MP Batch_INF Location_Site Stage]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

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
str_instance = 'PY_MG_INFLocation'
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

        df_in_MtrlConstType = read_csv_file('df_in_MtrlConstType')
        df_in_BODItemMtrlFull = read_csv_file('df_in_BODItemMtrlFull')

    # if df_in_MtrlConstType.empty:
    #     raise Exception("Exception: df_in_MtrlConstType is empty")
    #
    # if df_in_BODItemMtrlFull.empty:
    #     raise Exception("Exception: df_in_BODItemMtrlFull is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_MtrlConstType, 'df_in_MtrlConstType')
    print_df(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Location_COLUMN = 'Location.[Location]'
    Item_Material_COLUMN = 'Item Material.[Item Material]'
    MP_Batch_Sequence_ID_COLUMN = 'MP Batch_Sequence.[MP Batch_Sequence_ID]'

    MP_Batch_INF_Location_Location = 'MP Batch_INF Location_Location'
    MP_Batch_INF_Location_Location_Category = 'MP Batch_INF Location_Location Category'
    MP_Batch_INF_Location_Location_Key = 'MP Batch_INF Location_Location Key'
    MP_Batch_INF_Location_Location_Type = 'MP Batch_INF Location_Location Type'
    MP_Batch_INF_Location_Site_Stage = 'MP Batch_INF Location_Site Stage'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 1  (1) df_in_MtrlConstType & df_in_BOD_Item_Mtrl 데이터 merge 0n = Item_Material_COLUMN
    #         (2) Unique 한 Location 추출
    #         (3) Out Put Data Frame 생성
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    df_Location = df_in_MtrlConstType.merge(df_in_BODItemMtrlFull, on=[Version_COLUMN, Item_Material_COLUMN], how='inner')
    Location_Series = df_Location[Location_COLUMN].unique()

    df_out_INFLoc = pd.DataFrame()
    df_out_INFLoc[MP_Batch_INF_Location_Location] = Location_Series + "_@INF"
    df_out_INFLoc[Version_COLUMN] = 'CWV_MP'
    df_out_INFLoc[MP_Batch_Sequence_ID_COLUMN] = df_out_INFLoc.index + 1
    df_out_INFLoc[MP_Batch_INF_Location_Location_Category] = 'Vendor'
    df_out_INFLoc[MP_Batch_INF_Location_Location_Type] = 'MF'
    df_out_INFLoc[MP_Batch_INF_Location_Site_Stage] = 'SP'
    df_out_INFLoc[MP_Batch_INF_Location_Location_Key] = ''

    print_df(df_out_INFLoc, 'df_out_INFLoc')


    df_out_INFLoc = df_out_INFLoc[[Version_COLUMN, MP_Batch_Sequence_ID_COLUMN, MP_Batch_INF_Location_Location,
                                   MP_Batch_INF_Location_Location_Category, MP_Batch_INF_Location_Location_Key,
                                   MP_Batch_INF_Location_Location_Type, MP_Batch_INF_Location_Site_Stage]]

    print_df(df_out_INFLoc, 'df_out_INFLoc')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2 (1) 최종 Out_Put Save
    ################################################################################################################

    row_count, col_count = df_out_INFLoc.shape
    note(f'=====> Final df_out_INFLoc rows : {row_count} , Columns : {col_count}')
    print_df(df_out_INFLoc, 'df_out_MtrlFull')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_INFLoc, 'df_out_INFLoc')


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
