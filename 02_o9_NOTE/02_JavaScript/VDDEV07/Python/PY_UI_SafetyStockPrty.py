"""

* 프로그램명
    - PY_UI_SafetyStockPrty

* 내용
     - Location의 Location Type 과 Location MF Site Stage의 값을  Safety_Stock_Prty 에 없는 Location을 추가

* 변경이력
- 2025.01.07 / ybest7.park (박병훈) / Create
- 2025.02.06 수정
    → output 설정 변경 (unique 한 내용 필터링)


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_Location :  select ([Location].[Location] * [Location].[MF Site Stage].filter(#.Name in{[LCM],[SET]}) * [Location].[Location Type].filter(#.Name in{[DC],[MF]}));
   - df_in_SafetyStockPrty : Select (&MPV * [Location].[Location] ) on row, ({Measure.[SS Prty_Created By], Measure.[SS Prty_Creation Time], Measure.[SS Prty_Must Flag], Measure.[SS Prty_Prty], Measure.[SS Prty_Update Time], Measure.[SS Prty_Updated By],Measure.[Dummy]}) on column;
                            (Select ([Version].[Version Name] * [Location].[Location] ) on row, ({Measure.[SS Prty_Created By], Measure.[SS Prty_Creation Time], Measure.[SS Prty_Must Flag], Measure.[SS Prty_Prty], Measure.[SS Prty_Update Time], Measure.[SS Prty_Updated By],Measure.[Dummy]}) on column;)

* Output Table
    - df_out_SafetyStockPrty = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] ) on row, ({Measure.[SS Prty_Created By], Measure.[SS Prty_Creation Time], Measure.[SS Prty_Must Flag], Measure.[SS Prty_Prty], Measure.[SS Prty_Update Time], Measure.[SS Prty_Updated By]}) on column;


* 데이터 삭제
    DELETE DATA FOR MODEL [SS Prty] where {Version.[Version Name].[CWV_MP]};


* 테스트 스크립트
    EXEC plugin instance [PY_UI_SafetyStockPrty] for measures {[SS Prty_Must Flag]}
    using scope (&MPV)
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG") ,(paramOutVersion,"CWV_MP")} ;


* 데이터 확인
    Select ([Version].[Version Name].[CWV_MP] * [Location].[Location].[P701LCD] ) on row, ({Measure.[SS Prty_Created By], Measure.[SS Prty_Creation Time], Measure.[SS Prty_Must Flag], Measure.[SS Prty_Prty], Measure.[SS Prty_Update Time], Measure.[SS Prty_Updated By]}) on column;


"""
import pytz

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

import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re
import warnings
import tracemalloc

from dateutil import parser as date_parser
from typing import Union

warnings.filterwarnings("ignore")
########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SafetyStockPrty'
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
        # paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_Location  = read_csv_file("df_in_Location")
        df_in_SafetyStockPrty = read_csv_file('df_in_SafetyStockPrty')

    # if df_in_Location.empty:
    #     raise Exception("Exception: df_in_Location is empty")
    #
    # if df_in_SafetyStockPrty.empty:
    #     raise Exception("Exception: df_in_SafetyStockPrty is empty")

    # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #     paramOutVersion = PARAM_OUTVERSION_VALUE

    print_df(df_in_Location, 'df_in_Location Input Data review',True)
    print_df(df_in_SafetyStockPrty, 'df_in_SafetyStockPrty Input Data review',True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    Location_Column = 'Location.[Location]'
    Location_MF_Site_Stage = 'Location.[MF Site Stage]'
    Location_Location_Type = 'Location.[Location Type]'
    SS_Prty_Created_By = 'SS Prty_Created By'
    SS_Prty_Creation_Time = 'SS Prty_Creation Time'
    SS_Prty_Must_Flag = 'SS Prty_Must Flag'
    SS_Prty_Prty = 'SS Prty_Prty'
    paramOutVersion = 'CWV_MP'

    SET = 'SET'
    MF = 'MF'
    DC = "DC"
    LCM = 'LCM'
    PY_MG_SafetyStockPrty = 'PY_MG_SafetyStockPrty'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 1. (1) df_in_Item_Site_Association 중복 삭제 및 필터링
    #         (2) Location.[MF Site Stage] == 'LCM" | Location.[Location Type] == "DC"
    ################################################################################################################
    step(300, '=====> STEP 3(start) : input data machining')

    # df_in_Location = df_in_Location[
    #     (df_in_Location[Location_MF_Site_Stage] == LCM) | (
    #                 df_in_Location[Location_Location_Type] == DC)]

    df_in_Location = df_in_Location[[Location_Column]]
    df_in_Location.drop_duplicates(subset=[Location_Column], keep='first', inplace=True)

    print_df(df_in_Location, 'df_in_Location unique Values checking',True)

    row_count, col_count = df_in_Location.shape
    note(f"df_in_Location shape =====> row: {row_count} , ===> col: {col_count}  ", p_log_level=LOG_LEVEL.debug())

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2. df_in_Location의 Unique한 Date 추출
    #         (1) df_in_SafetyStockPrty 와 Outer Merge
    #         (2) Unique 한 데이터 생성
    ################################################################################################################
    step(400, '=====> STEP 4(start) : output data machining')
    kst = pytz.timezone('Asia/Seoul')
    today_kst = datetime.datetime.now(kst).date()
    # Version = df_in_SafetyStockPrty[VERSION_NAME_COLUMN].iloc[0]
    # Unique한 Date Frame 추출
    index_col = [Location_Column]
    df_in_Location_index = df_in_Location.set_index(index_col).index
    df_in_SafetyStockPrty_index = df_in_SafetyStockPrty.set_index(index_col).index
    df_unique = df_in_Location[~df_in_Location_index.isin(df_in_SafetyStockPrty_index)]

    # Out Data Frame 의 Measure 추가
    df_unique[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE
    df_unique[SS_Prty_Must_Flag] = 'N'
    df_unique[SS_Prty_Prty] = 999
    df_unique[SS_Prty_Created_By] = PY_MG_SafetyStockPrty
    df_unique[SS_Prty_Creation_Time] = today_kst
    # df_unique[SS_Prty_Creation_Time] = df_unique[SS_Prty_Creation_Time].astype(str)
    # df_unique[SS_Prty_Creation_Time] = df_unique[SS_Prty_Creation_Time].str.split(" ",
    #                                                                               expand=True).iloc[:, 0].astype(str)

    print_df(df_unique, 'df_unique Values checking', True)

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3. (1) df_out_Safety_Stock  & df_unique  concat
    ################################################################################################################
    step(500, '=====> STEP 5(start) : output data machining')
    df_in_SafetyStockPrty[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE

    grain_col = [VERSION_NAME_COLUMN, Location_Column]
    df_unique_index = df_unique.set_index(grain_col).index
    df_in_SafetyStockPrty_index = df_in_SafetyStockPrty.set_index(grain_col).index
    df_out_SafetyStockPrty = df_unique[~df_unique_index.isin(df_in_SafetyStockPrty_index)]
    df_out_SafetyStockPrty[SS_Prty_Created_By] = PY_MG_SafetyStockPrty
    df_out_SafetyStockPrty[SS_Prty_Creation_Time] = today_kst

    print_df(df_out_SafetyStockPrty, 'df_out_SafetyStockPrty data Frame checking',True)

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) 최종 Out_Put Save
    ################################################################################################################

    if is_local:
        Logger.Step(p_step_no=500, p_step_desc=f'Final Output Tabel create')
        save_csv_file(df_out_SafetyStockPrty, 'df_out_SafetyStockPrty')

    row_count, col_count = df_out_SafetyStockPrty.shape
    note(f'df_out_Safety_Stock rows : {row_count} , Columns : {col_count}',
                      p_log_level=LOG_LEVEL.debug())

    print_df(df_out_SafetyStockPrty, 'df_out_SafetyStockPrty 정보확인 _ Step 5',True)

except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg,p_log_level=LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_SafetyStockPrty = pd.DataFrame([], columns=[])


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