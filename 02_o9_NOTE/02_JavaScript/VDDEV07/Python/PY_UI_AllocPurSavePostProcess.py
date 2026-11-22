
"""
* 프로그램명
    - PY_UI_AllocPurSavePostProcess

* 내용
    - Update ETD Plan LT and Aggregate ETD Plan on Alloc Pur

* 변경이력
    - 2025.08.07 / 김교승 / Create

* Flow Summary
    1) 신규 ETD Plan에 대응되는 LT 메져에 값 업데이트
    2) 하단 ETD Plan을 상단 Summary 데이터 형태에 맞추어 합산

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP

* Input Tables
    - df_in_AllocPur : Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]) on row, ({Measure.[Alloc Pur_ETD Plan], Measure.[Alloc Pur_ETD Plan LT]}) on column;
    - df_in_MatlBOD : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Time].[Week]) on row, ({Measure.[BOD Item Mtrl W_GR LT]}) on column;

* Output Tables :
    - df_out_AllocPur
    - df_out_AllocPurSum

* 테스트 스크립트
    - exec plugin instance [PY_UI_AllocPurSavePostProcess] for Measures{[Alloc Pur_ETD Plan], [Alloc Pur Sum_ETD Plan]} using scope (&CWVUI)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_AllocPur : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]) on row, ({Measure.[Alloc Pur_ETD Plan], Measure.[Alloc Pur_ETD Plan LT]}) on column;
    - df_out_AllocPurSum : Select ([Version].[Version Name].[CWV_MP] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location]) on row, ({Measure.[Alloc Pur Sum_ETD Plan]}) on column;

"""
import time
import traceback
import datetime
import os
import warnings
import pandas as pd
import tracemalloc

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon


########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_AllocPurSavePostProcess'
is_local = common.gfn_get_isLocal()

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

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
            df_in_AllocPur = read_csv_file("df_in_AllocPur")
            df_in_MatlBOD = read_csv_file("df_in_MatlBOD")

        vdCommon.gfn_saveDf(df_in_AllocPur, 'df_in_AllocPur')
        vdCommon.gfn_saveDf(df_in_MatlBOD, 'df_in_MatlBOD')

        vdCommon.gfn_stepLog('=====> STEP (End) : 모듈 내에서 사용될 input table load')

        ################################################################################################################
        # STEP 1.0 : df_out_AllocPur 데이터 처리
        ##########################################################################n######################################
        vdCommon.gfn_stepLog('=====> STEP 1.0 (Start) : df_out_AllocPur 데이터 처리')

        df_allocPur_new = df_in_AllocPur[(df_in_AllocPur['Sub Location.[Sub Location]'] != '-') &
                                         (df_in_AllocPur['Trans Mode.[Trans Mode]'] != '-') &
                                         (df_in_AllocPur['Alloc Pur_ETD Plan'].notna()) &
                                         (df_in_AllocPur['Alloc Pur_ETD Plan LT'].isna())]

        df_in_MatlBOD.rename(columns={'Location.[Location]': 'Sub Location.[Sub Location]',
                                      'Sub Location.[Sub Location]': 'Location.[Location]'}, inplace=True)
        df_in_MatlBOD = df_in_MatlBOD[
            (df_in_MatlBOD['BOD Item Mtrl W_GR LT'].notnull() & df_in_MatlBOD['BOD Item Mtrl W_GR LT'] > 0)]

        ##########################################################################n######################################
        # 일자 -> 주차로 변환
        ##########################################################################n######################################
        df_in_MatlBOD['BOD Item Mtrl W_GR LT'] = df_in_MatlBOD['BOD Item Mtrl W_GR LT'] / 7
        ##########################################################################n######################################

        df_out_AllocPur = pd.merge(df_allocPur_new, df_in_MatlBOD,
                                   on=['Version.[Version Name]', 'Location.[Location]', 'Item Material.[Item Material]',
                                       'Sub Location.[Sub Location]', 'Trans Mode.[Trans Mode]', 'Time.[Week]'])
        df_out_AllocPur.drop(columns='Alloc Pur_ETD Plan LT', inplace=True, errors='ignore')
        df_out_AllocPur.rename(columns={'BOD Item Mtrl W_GR LT': 'Alloc Pur_ETD Plan LT'}, inplace=True)

        vdCommon.gfn_saveDf(df_out_AllocPur, 'df_out_AllocPur', True)

        vdCommon.gfn_stepLog('=====> STEP 1.0 (End) : df_out_AllocPur 데이터 처리')

        ################################################################################################################
        # STEP 2.0 : df_out_AllocPurSum 데이터 처리
        ##########################################################################n######################################
        vdCommon.gfn_stepLog('=====> STEP 2.0 (Start) : df_out_AllocPurSum 데이터 처리')

        df_out_AllocPurSum = df_in_AllocPur[(df_in_AllocPur['Sub Location.[Sub Location]'] != '-')]
        df_out_AllocPurSum.drop(columns=['Location.[Location]', 'Trans Mode.[Trans Mode]', 'Alloc Pur_ETD Plan LT'],
                                inplace=True, errors='ignore')
        df_out_AllocPurSum = df_out_AllocPurSum.groupby(
            ['Version.[Version Name]', 'Time.[Week]', 'Item Material.[Item Material]', 'Sub Location.[Sub Location]'])[
            'Alloc Pur_ETD Plan'].sum().reset_index()
        df_out_AllocPurSum.rename(columns={'Alloc Pur_ETD Plan': 'Alloc Pur Sum_ETD Plan'}, inplace=True)

        vdCommon.gfn_saveDf(df_out_AllocPurSum, 'df_out_AllocPurSum', True)

        vdCommon.gfn_stepLog('=====> STEP 2.0 (End) : df_out_AllocPurSum 데이터 처리')
    except Exception as ex:
        note(f'=====> try exception : {traceback.format_exc()}')
        note(f'An exception occurred: {ex}')

        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        # ouput Table 선언
        df_out_AllocPur = pd.DataFrame([], columns=[])
        df_out_AllocPurSum = pd.DataFrame([], columns=[])

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
