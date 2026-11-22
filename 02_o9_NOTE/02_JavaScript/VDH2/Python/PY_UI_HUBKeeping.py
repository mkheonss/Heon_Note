

"""

* 프로그램명
    - PY_UI_HUBKeeping

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.01.08 / ybest7.park (박병훈) / Create
- 2025.02.10 / input query 추가 수정
- 2025.03.14 / input query 추가 수정 common 추가
- 2025.04.28 / HUB Keeping Period_Keeping Period & HUB Keeping Period_Keeping Period Ch

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_BODItem = Select ([Version].[Version Name]* [Item].[Item].filter(#.relatedmembers([Item Stage]).element(0).Name == "SET") * [Location].[Location] * &NSUISubLocEURHubView * [Sub Location].[Sub Site Stage]* [Trans Mode].[Trans Mode] * [Item].[SCM Type]) on row, ({Measure.[BOD Item_Priority],Measure.[BOD Item_BOD LT],Measure.[BOD Item_Shipment LT],Measure.[Dummy]}) on column where {(Measure.[BOD Item_Eff Startdate] < NOW || isnull(Measure.[BOD Item_Eff Startdate])) && (Measure.[BOD Item_Eff Enddate] > NOW) || isnull(Measure.[BOD Item_Eff Enddate] )};
   - df_in_HUBKeepingPeriod = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[HUB Keeping Period_Chg Flag], Measure.[HUB Keeping Period_Init By], Measure.[HUB Keeping Period_Init Dttm], Measure.[HUB Keeping Period_Keeping Period], Measure.[HUB Keeping Period_Keeping Period Chg], Measure.[HUB Keeping Period_Release Fence], Measure.[HUB Keeping Period_Up By], Measure.[HUB Keeping Period_Up Dttm],Measure.[Dummy]}) on column;
   - df_in_SOPFrozenList = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({ Measure.[SOP Frozen List_FP Period],Measure.[Dummy]}) on column;
   - df_in_HUBLocation = select(&NSUISiteEURHubView);


* Output Table
    - df_out_HUBKeepingPeriod = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[HUB Keeping Period_Chg Flag], Measure.[HUB Keeping Period_Init By], Measure.[HUB Keeping Period_Init Dttm], Measure.[HUB Keeping Period_Keeping Period], Measure.[HUB Keeping Period_Keeping Period Chg], Measure.[HUB Keeping Period_Release Fence], Measure.[HUB Keeping Period_Up By], Measure.[HUB Keeping Period_Up Dttm]}) on column;
    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    EXEC plugin instance [PY_UI_HUBKeeping] for measures {[HUB Keeping Period_Chg Flag]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;

* 데이터 삭제
    - DELETE DATA FOR MODEL [HUB Keeping Period] where {Version.[Version Name].[CWV_MP]};


1


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
warnings.filterwarnings("ignore")

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_HUBKeeping'
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
    step(100, '=====> STEP 1(Start) : Input Date Frame Read')
    # # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_BODItem = read_csv_file('df_in_BODItem')
        df_in_HUBKeepingPeriod = read_csv_file('df_in_HUBKeepingPeriod')
        df_in_SOPFrozenList = read_csv_file('df_in_SOPFrozenList')
        df_in_HUBLocation = read_csv_file('df_in_HUBLocation')


    # if df_in_BODItem.empty:
    #     raise Exception("Exception: df_in_BODItem is empty")

    # note(f'=====> paramOutVersion : {paramOutVersion}')

    vdCommon.gfn_saveDf(df_in_BODItem, 'df_in_BODItem', True)
    vdCommon.gfn_saveDf(df_in_HUBKeepingPeriod, 'df_in_HUBKeepingPeriod',True)
    vdCommon.gfn_saveDf(df_in_SOPFrozenList, 'df_in_SOPFrozenList', True)
    vdCommon.gfn_saveDf(df_in_HUBLocation, 'df_in_HUBLocation', True)


    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Item_COLUMN = 'Item.[Item]'
    Location_COLUMN = 'Location.[Location]'
    Sub_Location_COLUN = 'Sub Location.[Sub Location]'
    # SubSite_Stage_COLUMN = 'Sub Location.[Sub Site Stage]'
    Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'

    BOD_Item_Priority = 'BOD Item_Priority'
    BOD_Item_BOD_LT = 'BOD Item_BOD LT'
    BOD_Item_Shipment_LT = 'BOD Item_Shipment LT'

    HUB_Keeping_Period_Chg_Flag = 'HUB Keeping Period_Chg Flag'
    HUB_Keeping_Period_Init_By = 'HUB Keeping Period_Init By'
    HUB_Keeping_Period_Init_Dttm = 'HUB Keeping Period_Init Dttm'
    HUB_Keeping_Period_Keeping_Period = 'HUB Keeping Period_Keeping Period'
    HUB_Keeping_Period_Keeping_Period_Chg = 'HUB Keeping Period_Keeping Period Chg'
    HUB_Keeping_Period_Release_Fence = 'HUB Keeping Period_Release Fence'
    HUB_Keeping_Period_Up_By = 'HUB Keeping Period_Up By'
    HUB_Keeping_Period_Up_Dttm = 'HUB Keeping Period_Up Dttm'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) BOD_Item 정렬 및 중복 제거 후 결측치 채우기
    ################################################################################################################
    step(300, '=====> STEP 2(End) : Check memory usage & runtime')


    df_in_BODItem_temp = df_in_BODItem.sort_values(by=[Item_COLUMN, Sub_Location_COLUN, BOD_Item_Priority],
                                                   ascending=[True, True, True])
    df_in_BODItem_temp = df_in_BODItem_temp.drop_duplicates(subset=[Item_COLUMN, Sub_Location_COLUN], keep='first')
    df_in_BODItem_temp.loc[:, BOD_Item_BOD_LT] = df_in_BODItem_temp[BOD_Item_BOD_LT].fillna(0)
    df_in_BODItem_temp.loc[:, BOD_Item_Shipment_LT] = df_in_BODItem_temp[BOD_Item_Shipment_LT].fillna(0)


    vdCommon.gfn_saveDf(df_in_BODItem_temp, 'df_in_BODItem_temp', True)

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4 (1) out_data Frame 복사
    #        (2) 불필요한 컬럼 삭제
    #        (3) out_data Frame 값 설정
    ###############################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # df_in_HUBKeepingPeriod애 없는 것만 필터링
    grain_col = [Version_COLUMN,Item_COLUMN,Location_COLUMN]
    # df_in_HUBKeepingPeriod & df_in_BODItem_temp Index 설정
    HUBKeepingPeriod_index = df_in_HUBKeepingPeriod.set_index(grain_col).index
    BODItem_temp_index = df_in_BODItem_temp.set_index(grain_col).index
    # 인덱스를 통한 필터링
    df_in_BODItem_temp = df_in_BODItem_temp[~BODItem_temp_index.isin(HUBKeepingPeriod_index)]

    min_values = df_in_SOPFrozenList.groupby([Item_COLUMN,Sub_Location_COLUN])[
        'SOP Frozen List_FP Period'].min().fillna(0).astype(int)

    note(f"============> SOP Frozen List_FP Period : {min_values}")

    df_out_HUBKeepingPeriod_temp = df_in_BODItem_temp.copy()
    df_out_HUBKeepingPeriod_temp[Location_COLUMN] = df_out_HUBKeepingPeriod_temp[Sub_Location_COLUN]

    # 중복 삭제
    df_out_HUBKeepingPeriod_temp = df_out_HUBKeepingPeriod_temp[[Version_COLUMN,Item_COLUMN,Location_COLUMN]].drop_duplicates()


    df_out_HUBKeepingPeriod_temp[HUB_Keeping_Period_Release_Fence] = df_out_HUBKeepingPeriod_temp.set_index(
        [Item_COLUMN,Location_COLUMN]).index.map(min_values).fillna(0).astype(int)

    vdCommon.gfn_saveDf(df_in_BODItem_temp, 'df_in_BODItem_temp', True)
    vdCommon.gfn_saveDf(df_out_HUBKeepingPeriod_temp, 'df_out_HUBKeepingPeriod_temp', True)

    df_in_BODItem_temp[Location_COLUMN] = df_in_BODItem_temp[Sub_Location_COLUN]


    df_out_HUBKeepingPeriod = df_out_HUBKeepingPeriod_temp.merge(df_in_BODItem_temp, on=[Version_COLUMN,Item_COLUMN, Location_COLUMN],
                                                                 how='left')

    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Keeping_Period] = (df_out_HUBKeepingPeriod[BOD_Item_BOD_LT] + \
                                                                 df_out_HUBKeepingPeriod[BOD_Item_Shipment_LT] + \
                                                                 df_out_HUBKeepingPeriod[
                                                                     HUB_Keeping_Period_Release_Fence].fillna(0).astype(int))/7 # 2025-04-28 수정
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Keeping_Period_Chg] = (df_out_HUBKeepingPeriod[BOD_Item_BOD_LT] + \
                                                                     df_out_HUBKeepingPeriod[BOD_Item_Shipment_LT] + \
                                                                     df_out_HUBKeepingPeriod[
                                                                         HUB_Keeping_Period_Release_Fence].fillna(0).astype(int))/7 # 2025-04-28 수정
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Chg_Flag] = 'N'
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Init_By] = 'PY_UI_KeepingPeriod'
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Up_By] = 'PY_UI_KeepingPeriod'
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Init_Dttm] = datetime.datetime.now().strftime('%Y-%m-%d')
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Up_Dttm] = datetime.datetime.now().strftime('%Y-%m-%d')
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Keeping_Period] = df_out_HUBKeepingPeriod[HUB_Keeping_Period_Keeping_Period].astype(int)
    df_out_HUBKeepingPeriod[HUB_Keeping_Period_Keeping_Period_Chg] = df_out_HUBKeepingPeriod[HUB_Keeping_Period_Keeping_Period_Chg].astype(int)

    hublocation_list = df_in_HUBLocation[Location_COLUMN].unique().tolist()

    df_out_HUBKeepingPeriod = df_out_HUBKeepingPeriod[df_out_HUBKeepingPeriod[Location_COLUMN].isin(hublocation_list)] # 2025-04-28 수정

    # # 중복 삭제
    # df_out_HUBKeepingPeriod = df_out_HUBKeepingPeriod.drop(columns=Sub_Location_COLUN, axis=1).drop_duplicates()


    vdCommon.gfn_saveDf(df_out_HUBKeepingPeriod, 'df_out_HUBKeepingPeriod',True)
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 5. (1) 최종 Out_Put Save
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')
    df_out_HUBKeepingPeriod = df_out_HUBKeepingPeriod[
        [Version_COLUMN, Item_COLUMN, Location_COLUMN, HUB_Keeping_Period_Chg_Flag, HUB_Keeping_Period_Init_By,
         HUB_Keeping_Period_Init_Dttm, HUB_Keeping_Period_Keeping_Period, HUB_Keeping_Period_Keeping_Period_Chg,
         HUB_Keeping_Period_Release_Fence, HUB_Keeping_Period_Up_By, HUB_Keeping_Period_Up_Dttm]]

    vdCommon.gfn_saveDf(df_out_HUBKeepingPeriod, 'df_out_HUBKeepingPeriod')
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    row_count, col_count = df_out_HUBKeepingPeriod.shape
    note(f'=====> Final df_out_HUBKeepingPeriod rows : {row_count} , Columns : {col_count}')
    vdCommon.gfn_saveDf(df_out_HUBKeepingPeriod, 'df_out_HUBKeepingPeriod')

    if is_local:
        note(f'=====> Final output table create')
        vdCommon.gfn_saveDf(df_out_HUBKeepingPeriod, 'df_out_HUBKeepingPeriod',True)

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_HUBKeepingPeriod = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(600, '===================== plugin Execution End =====================')

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