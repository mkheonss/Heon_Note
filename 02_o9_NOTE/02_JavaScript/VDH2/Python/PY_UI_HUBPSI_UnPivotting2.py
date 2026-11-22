"""

* 프로그램명
    -  PY_UI_HUBPSI_UnPivotting

* 내용
    - HUB PSI W Data Unpivot!

* 변경 이력
    - 2026-03-24  /jaemin.im

* Input Table
    -df_in_HUBPSI

 Select ([Version].[Version Name] * [Sales Domain].[AP2] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] ) on row,  ({Measure.[Hub PSI AP2 W_Aging Over 30days], Measure.[Hub PSI AP2 W_Aging Over 60days], Measure.[Hub PSI AP2 W_Aging Rate Over 30days], Measure.[Hub PSI AP2 W_Aging Rate Over 60days], Measure.[Hub PSI AP2 W_Arrival], Measure.[Hub PSI AP2 W_Arrival BuildAhead], Measure.[Hub PSI AP2 W_Arrival Detail], Measure.[Hub PSI AP2 W_BOH], Measure.[Hub PSI AP2 W_Build Ahead], Measure.[Hub PSI AP2 W_Dmd], Measure.[Hub PSI AP2 W_Dmd Fill Rate], Measure.[Hub PSI AP2 W_Dmd GI], Measure.[Hub PSI AP2 W_EOH], Measure.[Hub PSI AP2 W_EOH Amt KRW], Measure.[Hub PSI AP2 W_EOH Amt USD], Measure.[Hub PSI AP2 W_EOH W], Measure.[Hub PSI AP2 W_GI Amt KRW], Measure.[Hub PSI AP2 W_GI Amt USD], Measure.[Hub PSI AP2 W_GI Qty], Measure.[Hub PSI AP2 W_Intransit], Measure.[Hub PSI AP2 W_Inventory], Measure.[Hub PSI AP2 W_Prod], Measure.[Hub PSI AP2 W_Prod Detail], Measure.[Hub PSI AP2 W_RTF], Measure.[Hub PSI AP2 W_SS Arrival], Measure.[Hub PSI AP2 W_SS Arrival BuildAhead], Measure.[Hub PSI AP2 W_SS Arrival JIT], Measure.[Hub PSI AP2 W_SS Shipment], Measure.[Hub PSI AP2 W_SS Shipment BuildAhead], Measure.[Hub PSI AP2 W_SS Shipment JIT], Measure.[Hub PSI AP2 W_Safety Stock], Measure.[Hub PSI AP2 W_Sales], Measure.[Hub PSI AP2 W_Shipment], Measure.[Hub PSI AP2 W_Shipment Detail], Measure.[Hub PSI AP2 W_Short], Measure.[Hub PSI AP2 W_Short Inv Risk AP2], Measure.[Hub PSI AP2 W_Short Inv Risk GC]}) on column;


* Output Table
    - df_out_HUBPSI_UnPivot
Select ([Version].[Version Name] * [Sales Domain].[AP2] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] * [Category].[Category] ) on row, 
({Measure.[Hub PSI AP2 W Unpivot_Value]}) on column;


* 데이터 삭제  (주의 필요 삭제 시 Input Data도 전부 삭제 됨)
    DELETE DATA FOR MODEL [Hub PSI AP2 W Unpivot] where {Version.[Version Name].[CWV_MP]};


* 테스트 스티립
    EXEC plugin instance [PY_UI_HUBPSI_UnPivotting] for measures {[Hub PSI AP2 W Unpivot_Value]} using scope (&CWVUI) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (paramOutVersion ,"CWV_MP")} ;


"""

import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import pytz

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_HUBPSI_UnPivotting'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = (
    "CWV_MP"
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
log_level_info = LOG_LEVEL.info()
log_level_debug = LOG_LEVEL.debug()
logger.debug(f'[START] {str_instance}')
logger.Start()


########################################################################################################################
# local function
########################################################################################################################
class CustomException(Exception):
    pass


def read_csv_file(file_name):
    try:
        file_path = f"{file_name}.csv"
        if not os.path.exists(file_path):
            step(f"=====> 파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame()  # 빈 DataFrame 반환
        return pd.read_csv(file_path, low_memory=False, encoding="UTF-8")

    except Exception as e:
        step(f"=====> CSV 파일 읽기 실패: {file_name}, 오류: {str(e)}")
        return pd.DataFrame()  # 에러 발생시 빈 DataFrame 반환


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def step(string):
    vdCommon.gfn_stepLog(string)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, logger, is_local, log_path)


def vd_log_end() -> tuple:
    """
    로그 처리를 종료하고 로그 데이터프레임들을 반환하는 공통 함수

    Returns:
        tuple: (df_out_log, df_out_logDetail) 형태의 튜플
    """
    try:
        # 로그 종료 처리
        vdCommon.gfn_pyLog_end()

        # 로그 데이터프레임 가져오기
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()

        return df_out_log, df_out_logDetail

    except Exception as e:
        step(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(df):
    """데이터프레임 최적화 및 메모리 사용량 감소"""
    if df is None:
        return None

    # 데이터프레임 복사 및 메모리 최적화
    result = df.copy()

    # 숫자형 컬럼의 데이터 타입 최적화
    for col in result.select_dtypes(include=['int', 'float']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')

    # # 범주형 데이터 최적화
    # for col in result.select_dtypes(include=['object']).columns:
    #     if result[col].nunique() / len(result) < 0.5:  # 고유값이 50% 미만일 경우
    #         result[col] = result[col].astype('category')

    delete_dfs(df)
    return result


def get_formatted_time(timestamp):
    """타임스탬프를 사람이 읽을 수 있는 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def format_size(size_in_bytes):
    """바이트 단위를 적절히 MB 또는 GB로 변환하여 문자열 반환"""
    if size_in_bytes >= 1024 ** 3:  # 1GB 이상일 때
        return f"{size_in_bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{size_in_bytes / 1024 ** 2:.1f} MB"


def run_time_minutes(start_time):
    """실행 시간을 계산하고, 분 또는 초 단위로 반환.
    초 단위가 0일 경우 초로 표시하고, 그 외에는 분으로 표시."""
    elapsed = time.time() - start_time
    if elapsed < 60:  # 1분 미만일 경우
        return str(round(elapsed, 2)) + " seconds"
    else:
        return str(round(elapsed / 60, 2)) + " minutes"


########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    # Batch 시작
    vd_log_start()
    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:


        ################################################################################################################
        #df_in_HUBPSI
        
        # step0. in 확인
        print_df(df_in_HUBPSI, 'df_in_HUBPSI', True)
        step('=====> STEP 0 End')
        
        # step1. UnPivot 대상 Measure Group
        category = [col for col in df_in_HUBPSI if col.startswith("Hub PSI")]
        print_df(category, 'category', True)
        step('=====> STEP 1 End')

        
        # step2. Unpivot
        df_out_HUBPSI_UnPivot = pd.melt(
            df_in_HUBPSI, 
            id_vars=['Version.[Version Name]', 'Sales Domain.[AP2]', 'Location.[Location]', 'Item.[Item]', 'Time.[Week]', 'Trans Mode.[Trans Mode]', 'Sub Location.[Sub Location]'],
            value_vars=category,
            var_name='Category.[Category]',
            value_name='Hub PSI AP2 W Unpivot_Value'
        )
        step('=====> STEP 2 End')


        # step3. out 확인
        print_df(df_out_HUBPSI_UnPivot, 'df_out_HUBPSI_UnPivot', True)
        step('=====> STEP 1 End')
        


    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPContainerLoading = pd.DataFrame([], columns=[])
        df_out_CTNRLoading = pd.DataFrame([], columns=[])


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
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

