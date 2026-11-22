"""

* 프로그램명
    - PY_MG_ResourceGroupPriority

* 내용
     - Production Capacity 정보 Interface
    - 현재는 CAPA 기준 관리만 대상 ( Target은 아님 )

* 변경이력
- 2024.08.27 / ybest7.park (박병훈) / Create

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_TactTime = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  where {  Measure.[Tact Time_Valid Asn] == true } ;
                         [ Select (&MPV * [Item].[Item] * &MFLocation * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  where {  Measure.[Tact Time_Valid Asn] == true }; ]
        ※ DISTINCT [Item].[Item] * [Location].[Location]
    - df_in_ItemSiteAsn = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
                          [Select (&MPV * &MFLocation * [Item].[Item] ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]})on column.filter(Measure.[Item Site Asn_Engine Flag]== true); ]
    - df_in_BOMMaster = Select ([Version].[Version Name] *  [Activity3].[Activity3] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Location].[Location] * [Item].[Item] ) on row, ({ Measure.[W Material Production Association], Measure.[W Material Production Quantity Per]}) on column ;
                       [Select (&MPV *  [Activity3].[Activity3] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Location].[Location] * [Item].[Item] ) on row, ({ Measure.[W Material Production Association], Measure.[W Material Production Quantity Per]}) on column ;]

* Output Table
    - df_out_TactTime = Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * [Resource Group].[Resource Group] ) on row, ({Measure.[W Input Resource Group Priority]}) on column;
                        [Select (&MPV * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * [Resource Group].[Resource Group] ) on row, ({Measure.[W Input Resource Group Priority]}) on column; ]
* 데이터 삭제
    DELETE DATA FOR MODEL [001.015W Solver Inputs Resource Group Priority] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
      EXEC plugin instance [PY_MG_ResourceGroupPriority] for Measures {[W Input Resource Group Priority]} using scope ( &MPV ) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};

* 데이터 수정
    scope : ([Activity3].[Activity3] * [Activity2].[Activity2] * [Activity1].[Activity1] * [Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item].[Item] );
    Measure.[W Production Holiday] = False;
    end scope;  <- 다시 수정 필요

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
str_instance = 'PY_MG_ResourceGroupPriority'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

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
    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE
        df_in_TactTime = read_csv_file('df_in_TactTime')
        df_in_ItemSiteAsn = read_csv_file('df_in_ItemSiteAsn')
        df_in_BOMMaster = read_csv_file('df_in_BOMMaster')


    # if df_in_TactTime.empty:
    #     raise Exception("Exception: df_in_TactTime is empty")
    #
    # if df_in_ItemSiteAsn.empty:
    #     raise Exception("Exception df_in_ItemSiteAsn is empty")
    #
    # if df_in_ItemSiteAsn.empty:
    #     raise Exception("Exception df_in_ItemSiteAsn is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_TactTime, 'df_in_TactTime')
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
    Item_Material_COLUMN = 'Item Material.[Item Material]'
    ResourceGrop_COLUMN = 'Resource Group.[Resource Group]'
    Line_COLUMN = 'Line.[Line]'

    Activity1_COLUMN = "Activity1.[Activity1]"
    Activity2_COLUMN = "Activity2.[Activity2]"
    Activity3_COLUMN = "Activity3.[Activity3]"

    tackTime = 'Tact Time_Time'
    W_Input_Resource_Priority = 'W Input Resource Priority'
    W_Input_Resource_Group_Priority = 'W Input Resource Group Priority'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) df_in_ItemSiteAsn 중복제거 기준 item & Loaction series 생성
    #         (2) Location 조건은 Location & Sub Location은 OR 조건 Item은 And 조건으로 df_in_BOD_Item 필터
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    Location_series = df_in_ItemSiteAsn[LOCATION_COLUMN].unique()
    Item_series = df_in_ItemSiteAsn[ITEM_COLUMN].unique()

    df_in_TactTime = df_in_TactTime[(df_in_TactTime[LOCATION_COLUMN].isin(Location_series)) & (
        df_in_TactTime[ITEM_COLUMN].isin(Item_series))]

    print_df(df_in_TactTime, 'df_in_TactTime')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) df_in_BOD_Item 과 df_in_BOD_List merge하여 1차 Output Data 생성 (df_mergeA)
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    df_in_TactTime = df_in_TactTime.merge(df_in_BOMMaster, on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN],
                                          how='inner')
    df_in_TactTime[ResourceGrop_COLUMN] = df_in_TactTime[Activity2_COLUMN] + '_' + df_in_TactTime[Line_COLUMN]
    df_in_TactTime[W_Input_Resource_Priority] = df_in_TactTime[tackTime]

    print_df(df_in_TactTime, 'df_in_TactTime')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) df_in_BOD_Item_mtrl 기준 Location & Item 필터 및 merge data 생성
    #         (2) 생성된 merge data와 df_in_BOD_List_Mtrl merge하여 mergeB 생성
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')
    df_out_TactTime = \
        df_in_TactTime.groupby(
            [VERSION_NAME_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN, ResourceGrop_COLUMN])[
            W_Input_Resource_Priority].min().reset_index()
    df_out_TactTime.rename(columns={W_Input_Resource_Priority: W_Input_Resource_Group_Priority}, inplace=True)

    print_df(df_out_TactTime, 'df_out_TactTime')
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. (1) 최종 Out_Put Save
    ################################################################################################################

    row_count, col_count = df_out_TactTime.shape
    note(f'=====> Final df_out_TactTime rows : {row_count} , Columns : {col_count}')
    print_df(df_out_TactTime, 'df_out_TactTime')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_TactTime, 'df_out_TactTime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_TactTime = pd.DataFrame([], columns=[])
    # df_out_NewModelSumStatus = pd.DataFrame([], columns=[])

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