"""

* 프로그램명
    - PY_MG_TimeVaryingQuantityPer

* 수정일 : 2024/11/13

* 내용
     - [Basic Input] MP Engine 수행을 위한 Phased Tact Time Input
    - MP Plan Batch Procedure에서 Call 하는 Program
    - 기존 메저는 Batch Procedure에서 Delete

* 변경이력
- 2024.07.05 / ybest7.park (박병훈) / Create

* Input
    - df_in_TactTimeW = pd.read_csv('TactTimeW.csv')


* Flow Summary
    STEP1. df_in_TactTimeW 중 Plan 대상 Item, Location 정보 대상 SET 구성
    STEP2. STEP1에서 구성한 SET을 대상으로 Measure Insert

* Input Table
    - df_in_TactTimeW = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time W_Time], Measure.[Tact Time W_Time Override], Measure.[Tact Time W_Time Sys]}) on column where { Measure.[Tact Time_Valid Asn] == true } ;
                               [ Select (&MPV * [Item].[Item] * &AllPlanningWeeks * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time W_Time], Measure.[Tact Time W_Time Override], Measure.[Tact Time W_Time Sys]}) on column where { Measure.[Tact Time_Valid Asn] == true }; ]
    - df_in_ItemSiteAsn  = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
                          [Select (&MPV * &MFLocation * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true); ]
    - df_in_BOMMaster = Select (&MPV  * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column ;
                       [Select ([Version].[Version Name] * &MFLocation * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column ;]

    - DELETE DATA FOR MODEL [280.001W MFG Resource Consumed Time Varying Quantity Per] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_TimeVaryingTact = select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Resource Consumed Time Varying Quantity Per]}) on column;
                               [select (&MPV * &MFLocation * &AllPlanningWeeks * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Resource Consumed Time Varying Quantity Per]}) on column;]


* 테스트 스크립트
    EXEC plugin instance [PY_MG_TimeVaryingQuantityPer] for measures {[W Resource Consumed Time Varying Quantity Per]} using scope (&MPV * &MFLocation * &AllPlanningWeeks) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ),([Param.o9_sys_log_level], "DEBUG" )} ;

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
str_instance = 'PY_MG_TimeVaryingQuantityPer'
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

        df_in_TactTimeW = read_csv_file("df_in_TactTimeW")
        df_in_ItemSiteAsn = read_csv_file('df_in_ItemSiteAsn')
        df_in_BOMMaster = read_csv_file('df_in_BOMMaster')

    # if df_in_TactTimeW.empty:
    #     raise Exception("Exception: df_in_TactTimeW is empty")
    #
    # if df_in_ItemSiteAsn.empty:
    #     raise Exception("Exception: df_in_ConstraintGroupDetailW is empty")
    #
    # if df_in_BOMMaster.empty:
    #     raise  Exception("Exception df_in_BOMMaster is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_TactTimeW, 'df_in_TactTimeW')
    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn')
    print_df(df_in_BOMMaster, 'df_in_BOMMaster')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    ITEM_COLUMN = 'Item.[Item]'
    Activity1_COLUMN = "Activity1.[Activity1]"
    Activity2_COLUMN = "Activity2.[Activity2]"
    Activity3_COLUMN = "Activity3.[Activity3]"
    TIME_WEEK_COLUMN = 'Time.[Week]'
    RESOURCE_COKUMN = 'Resource.[Resource]'
    LINE_COLUMN = 'Line.[Line]'
    BOMID_COLUMN = 'BOM Master_BOM ID'
    BOMINFOID = 'BOM Info.[BOM ID]'
    MP_Batch_Sequence_ID_COLUMN = 'MP Batch_Sequence.[MP Batch_Sequence_ID]'

    Tact_Time_W_Time = "Tact Time W_Time"
    W_Resource_Consumed_Time_Varying_Quantity_Per = 'W Resource Consumed Time Varying Quantity Per'
    BULK_Member = 'MP Batch_Resource Group Bulk Member Creation_ResGroup'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) df_in_ItemSiteAsn 중복제거 기준 item & Loaction series 생성
    #         (2) Location 조건은 Location & Sub Location은 OR 조건 Item은 And 조건으로 df_in_BOD_Item 필터
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    Location_series = df_in_ItemSiteAsn[LOCATION_COLUMN].unique()
    Item_series = df_in_ItemSiteAsn[ITEM_COLUMN].unique()
    df_in_TactTimeW = df_in_TactTimeW[(df_in_TactTimeW[LOCATION_COLUMN].isin(Location_series)) &
                                      (df_in_TactTimeW[ITEM_COLUMN].isin(Item_series))]

    print_df(df_in_TactTimeW, 'df_in_TactTimeW')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. (1) df_in_TactTimeW & df_in_BOMMaster merge (df_mergeA 생성) on = [Location, Item, Version Name]
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    df_in_TactTimeW = df_in_TactTimeW.merge(df_in_BOMMaster, left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN],
                                      right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, BOMID_COLUMN], how='inner')
    df_in_TactTimeW[Activity3_COLUMN] = df_in_TactTimeW[ITEM_COLUMN]
    df_in_TactTimeW[Activity1_COLUMN] = df_in_TactTimeW[BOMINFOID]
    df_in_TactTimeW[Activity2_COLUMN] = "RT_" + df_in_TactTimeW[BOMINFOID] + '_@' + df_in_TactTimeW[LOCATION_COLUMN]
    df_in_TactTimeW[W_Resource_Consumed_Time_Varying_Quantity_Per] = df_in_TactTimeW[Tact_Time_W_Time]
    df_in_TactTimeW[RESOURCE_COKUMN] = df_in_TactTimeW[LINE_COLUMN]

    print_df(df_in_TactTimeW, 'df_in_TactTime')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) df_out_MP_Batch 값 설정
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    df_out_MP_Batch = df_in_TactTimeW.copy()
    df_out_MP_Batch = df_out_MP_Batch.reset_index(drop=True)
    df_out_MP_Batch[MP_Batch_Sequence_ID_COLUMN] = df_out_MP_Batch.index + 1
    df_out_MP_Batch[VERSION_NAME_COLUMN] = df_in_TactTimeW[VERSION_NAME_COLUMN]
    df_out_MP_Batch[BULK_Member] = df_out_MP_Batch[Activity2_COLUMN]+'_'+df_out_MP_Batch[RESOURCE_COKUMN]
    df_out_MP_Batch[BULK_Member] = df_out_MP_Batch[BULK_Member].astype(str)
    df_out_MP_Batch = df_out_MP_Batch[[VERSION_NAME_COLUMN, MP_Batch_Sequence_ID_COLUMN, BULK_Member]]

    print_df(df_out_MP_Batch, 'df_out_MP_Batch')
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. (1) df_out_TimeVaryingTact (최종 Output DataFrame 설정)
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    df_out_TimeVaryingTact = df_in_TactTimeW[[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, Activity1_COLUMN,
                                        Activity2_COLUMN, RESOURCE_COKUMN, Activity3_COLUMN,
                                        W_Resource_Consumed_Time_Varying_Quantity_Per]]

    print_df(df_out_TimeVaryingTact, 'df_out_TimeVaryingTact')
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) 최종 Out_Put Save
    ################################################################################################################

    row_count, col_count = df_out_TimeVaryingTact.shape
    note(f'=====> Final df_out_TimeVaryingTact rows : {row_count} , Columns : {col_count}')
    print_df(df_out_TimeVaryingTact, 'df_out_TimeVaryingTact')
    print_df(df_out_MP_Batch, 'df_out_MP_Batch')

    row_count, col_count = df_out_MP_Batch.shape
    note(f'=====> Final df_out_MP_Batch rows : {row_count} , Columns : {col_count}')
    print_df(df_out_MP_Batch, 'df_out_MP_Batch')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_TimeVaryingTact, 'df_out_TimeVaryingTact')
        save_csv_file(df_out_MP_Batch, 'df_out_MP_Batch')

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
    step(600, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()