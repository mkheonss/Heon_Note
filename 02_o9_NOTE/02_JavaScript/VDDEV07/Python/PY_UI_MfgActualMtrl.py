"""
* 프로그램명
    - PY_UI_MfgActualMtrl

* 내용
    - Mfg Actual Mtrl_Consume Qty Measure Data Generation

* 변경이력
    - 2025.03.25 / 황수혁 / Create

* Flow Summary
    Mfg Actual Mtrl_Consume Qty Measure Data 생성

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP

* Input Tables
    - df_in_MfgActual(생산 실적) : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-4).Key && #.Key < &CurrentWeek.element(0).LeadOffset(0).Key).relatedmembers([Day]) * [Sequence].[Sequence] * [Sub Location].[Sub Location] ) on row, ({Measure.[Mfg Act_Mfg Qty], Measure.[Mfg Act_SOP Week]}) on column;
    - df_in_FullBom(FullBom) : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Item Stage] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] *  [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type].filter(#.[Name] in {"SET"}) * [BOM Status].[BOM Status] ) on row, ({Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_Consume Qty], Measure.[Full BOM_Consume UOM], Measure.[Full BOM_Flag]}) on column where {(Measure.[Full BOM_Flag] == "True")};
    - df_in_Solver_Inputs_Consumption : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item]) on row, ({Measure.[W Material Consumption Association]}) on column;
    - df_in_Solver_Inputs_Production : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item]) on row, ({Measure.[W Material Production Association]}) on column;

* Output Tables :
    - df_out_MfgActualMtrl

* 테스트 스크립트
    - EXEC plugin instance [PY_UI_MfgActualMtrl] for Measures {[Mfg Actual Mtrl_Consume Qty]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_MfgActualMtrl : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] ) on row, ({Measure.[Mfg Actual Mtrl_Consume Qty]}) on column;


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

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon


########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_MfgActualMtrl'
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

########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()
    formatted_time = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')   # 초 단위를 datetime으로 변환하여 시분초 표시

    logger.debug('[START] {str_instance}')
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
        vdCommon.gfn_stepLog('=====> STEP (Start) : 전처리 - 모듈 내에서 사용될 input table load')

        # csv 파일 이름과 변수명을 매핑한 딕셔너리 생성
        if is_local:
            df_in_MfgActual = read_csv_file("df_in_MfgActual")
            df_in_FullBom = read_csv_file("df_in_FullBom")
            df_in_Solver_Inputs_Consumption = read_csv_file("df_in_Solver_Inputs_Consumption")
            df_in_Solver_Inputs_Production = read_csv_file("df_in_Solver_Inputs_Production")

        vdCommon.gfn_saveDf(df_in_MfgActual, 'df_in_MfgActual')
        vdCommon.gfn_saveDf(df_in_FullBom, 'df_in_FullBom')
        vdCommon.gfn_saveDf(df_in_Solver_Inputs_Consumption, 'df_in_Solver_Inputs_Consumption')
        vdCommon.gfn_saveDf(df_in_Solver_Inputs_Production, 'df_in_Solver_Inputs_Production')

        vdCommon.gfn_stepLog('=====> STEP (End) : 모듈 내에서 사용될 input table load')


        ################################################################################################################
        # STEP : 데이터 선 가공
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP (Start) : 데이터 선 가공')

        df_in_MfgActual = df_in_MfgActual.groupby(['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]', 'Mfg Act_SOP Week']
                                                    , as_index=False)['Mfg Act_Mfg Qty'].sum()
        df_in_FullBom  = df_in_FullBom[['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]', 'To Location.[To Location]', 'Item Material.[Item Material]', 'BOM Info.[BOM Version]', 'Full BOM_Consume Qty']]

        df_Solver_Inputs = pd.concat([df_in_Solver_Inputs_Consumption[['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]']]
                                         , df_in_Solver_Inputs_Production[['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]']]
                                        ], axis=0)
        df_Solver_Inputs.drop_duplicates()

        vdCommon.gfn_stepLog('=====> STEP (End) : 데이터 선 가공')

        ################################################################################################################
        # STEP : 변수 처리
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP (Start) : 변수 처리')

        vdCommon.gfn_stepLog('=====> STEP (End) : 변수 처리')

        ################################################################################################################
        # STEP 1.0 : df_out_MfgActualMtrl 데이터 처리
        ##########################################################################n######################################
        vdCommon.gfn_stepLog('=====> STEP 1.0 (Start) : df_out_MfgActualMtrl 데이터 처리')

        df_out_MfgActualMtrl = pd.merge(df_in_MfgActual, df_in_FullBom
                                     , on=['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]']
                                     , how='inner')

        df_out_MfgActualMtrl.rename(columns={'Item.[Item]': '[To Item].[To Item]'}, inplace=True)
        df_out_MfgActualMtrl.rename(columns={'Mfg Act_SOP Week': 'Time.[Week]', 'Item Material.[Item Material]': 'Item.[Item]'}, inplace=True)
        df_out_MfgActualMtrl['Time.[Week]'] = df_out_MfgActualMtrl['Time.[Week]'].astype(str)
        df_out_MfgActualMtrl['Mfg Actual Mtrl_Consume Qty'] = df_out_MfgActualMtrl['Mfg Act_Mfg Qty'] * df_out_MfgActualMtrl['Full BOM_Consume Qty']

        df_out_MfgActualMtrl = df_out_MfgActualMtrl.groupby(['Version.[Version Name]', 'Location.[Location]', '[To Item].[To Item]', 'Time.[Week]'
                                                               , 'To Location.[To Location]', 'Item.[Item]', 'BOM Info.[BOM Version]']
                                                               , as_index=False)['Mfg Actual Mtrl_Consume Qty'].sum()

        df_out_MfgActualMtrl = pd.merge(df_out_MfgActualMtrl, df_Solver_Inputs
                                      , on=['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]']
                                      , how='inner')

        vdCommon.gfn_stepLog('=====> STEP 1.0 (End) : df_out_MfgActualMtrl 데이터 처리')

        vdCommon.gfn_saveDf(df_out_MfgActualMtrl, 'df_out_MfgActualMtrl', True)

        del df_in_MfgActual
        del df_in_FullBom
        del df_in_Solver_Inputs_Consumption
        del df_in_Solver_Inputs_Production
        del df_Solver_Inputs
        gc.collect()

    except Exception as ex:
        note(f'=====> try exception : {traceback.format_exc()}')
        note(f'An exception occurred: {ex}')

        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        # ouput Table 선언
        df_out_MfgActualMtrl = pd.DataFrame([], columns=[])

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
