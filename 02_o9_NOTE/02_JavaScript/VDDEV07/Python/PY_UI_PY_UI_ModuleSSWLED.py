"""
* 프로그램명
    - PY_UI_PY_UI_ModuleSSWLED

* 내용
    - Module SS LED Measure Data Create

* 변경이력
    - 2025.04.22 / 황수혁 / Create

* Flow Summary
    Module SS LED Measure Data 생성

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP

* Input Tables
    - df_in_Week : select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(52).Key)) orderby [Time].[Week].Key;
    - df_in_UI_ModuleSSWLED: Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(52).Key) ) on row, ({Measure.[Module SS W LED_Qty]}) on column;

* Output Tables :
    -  df_out_ModuleSSWLED

* 테스트 스크립트
    - EXEC plugin instance [PY_UI_PY_UI_ModuleSSWLED] for Measures {[Module SS W LED_Qty]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(52).Key) ) on row, ({Measure.[Module SS W LED_Qty]}) on column;

"""

import time
import traceback
import datetime
import os
import warnings
import numpy as np
import pandas as pd
import tracemalloc
import gc
import re

from numpy.ma.core import inner

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_PY_UI_ModuleSSWLED'
is_local = common.gfn_get_isLocal()

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"
SEQ_VALUE = 1

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
COMMON_SOURCE_VERSION = common.G_SourceVersion

########################################################################################################################
# local function
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    memory_using = str(round(df.memory_usage(deep=True).sum() / (1024**2), 2)) + " MB"
    row_count, col_count = df.shape

########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()
    formatted_time = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')   # 초 단위를 datetime으로 변환하여 시분초 표시

    logger.debug(f'[START] {str_instance}')
    logger.Start()
    note(f'===================== plugin Execution Start ({formatted_time}) =====================')
    note(f'=====> Input value checkparamOutVersion : {paramOutVersion}')
    note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')

    try:
        #Batch 시작
        if common.gfn_get_isLocal():
            vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), os.path.dirname(__file__))
        else:
            vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), "")


        vdCommon.gfn_stepLog("plugin Execution Start ")
        vdCommon.gfn_stepLog(common.G_SourceVersion)
        vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

        pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
        warnings.simplefilter(action='ignore', category=FutureWarning)


        ################################################################################################################
        # STEP : 모듈 내에서 사용될 input table load
        ################################################################################################################
        vdCommon.gfn_stepLog('10 =====> STEP (Start) : 전처리 - 모듈 내에서 사용될 input table load')

        # csv 파일 이름과 변수명을 매핑한 딕셔너리 생성
        if is_local:
            df_in_Week = read_csv_file("df_in_Week")
            df_in_UI_ModuleSSWLED = read_csv_file("df_in_UI_ModuleSSWLED")

        vdCommon.gfn_saveDf(df_in_Week, 'df_in_Week')
        vdCommon.gfn_saveDf(df_in_UI_ModuleSSWLED, 'df_in_UI_ModuleSSWLED')

        # input value 확인용 로그
        note(f'Input value check =====> paramOutVersion : {paramOutVersion}')

        vdCommon.gfn_stepLog('10 =====> STEP (End) : 모듈 내에서 사용될 input table load')


        ################################################################################################################
        # STEP : DataFrame Column 변수 처리
        ################################################################################################################
        vdCommon.gfn_stepLog('20 =====> STEP (Start) : DataFrame Column 변수 처리')

        # 컬럼 변수 선언

        vdCommon.gfn_stepLog('20 =====> STEP (End) : DataFrame Column 변수 처리')

        ################################################################################################################
        # STEP : 데이터 프레임 선 가공
        ################################################################################################################
        vdCommon.gfn_stepLog('30 =====> STEP (Start) : 데이터 선 가공')
        df_in_Week['Time.[Week]'] = df_in_Week['Time.[Week]'].astype('str')

        vdCommon.gfn_stepLog('30 =====> STEP (End) : 데이터 선 가공')

        ################################################################################################################
        # STEP 1.0 : df_out_ModuleSSWLED Data 처리
        ################################################################################################################
        vdCommon.gfn_stepLog('100 =====> STEP 1.0 (Start) : SOP Volatility Map_Asn')

        df_in_UI_ModuleSSWLED['Time.[Week]'] = df_in_UI_ModuleSSWLED['Time.[Week]'].astype('int')
        df_out_ModuleSSWLED = df_in_UI_ModuleSSWLED.loc[df_in_UI_ModuleSSWLED.groupby(['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]'])['Time.[Week]'].idxmax(axis=0)]
        df_out_ModuleSSWLED['Time.[Week]'] = df_out_ModuleSSWLED['Time.[Week]'].astype('str')

        df_out_ModuleSSWLED['Key'] = 'A'
        df_in_Week['Key'] = 'A'
        
        df_out_ModuleSSWLED = pd.merge(df_in_Week, df_out_ModuleSSWLED, on = 'Key', how='left', suffixes=('', '_y'))
        del_idx = df_out_ModuleSSWLED[df_out_ModuleSSWLED['Time.[Week]'] <= df_out_ModuleSSWLED['Time.[Week]_y']].index
        df_out_ModuleSSWLED.drop(del_idx, inplace=True)
        df_out_ModuleSSWLED = df_out_ModuleSSWLED.drop(['Key', 'Time.[Week]_y'], axis=1, errors='ignore')
        df_out_ModuleSSWLED = df_out_ModuleSSWLED[['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]', 'Time.[Week]', 'Module SS W LED_Qty' ]].copy()

        vdCommon.gfn_saveDf(df_out_ModuleSSWLED, 'df_out_ModuleSSWLED')

        vdCommon.gfn_stepLog('100 =====> STEP 1.0 (End) : SOP Volatility Map_Asn')

        del df_in_Week
        del df_in_UI_ModuleSSWLED

        gc.collect()

    except Exception as ex:
        note(f'=====> try exception : {traceback.format_exc()}')
        note(f'An exception occurred: {ex}')

        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        # ouput Table 선언
        df_out_SOPVolatility_SET = pd.DataFrame([], columns=[])
        #df_out_SOPVolatility_Mtrl = pd.DataFrame([], columns=[])

    else:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        end_time = time.time()
        run_time_seconds = end_time - start_time
        run_time_minutes = run_time_seconds / 60
        formatted_time = datetime.datetime.fromtimestamp(end_time).strftime('%H:%M:%S')  # 초 단위를 datetime으로 변환하여 시분초 표시
        note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, Peak was {round(peak / 10 ** 6, 2)}MB, Execution time: {run_time_minutes:.4f} minutes')
        note(f'===================== plugin Execution End ({formatted_time}) =====================')

    finally:
        vdCommon.gfn_pyLog_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()

        vdCommon.gfn_stepLog('=====> Batch end')


    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')