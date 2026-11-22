"""

* 프로그램명
    - PY_UI_TargetEcp

* 내용
     - 

* 변경이력
- 2024.10.2 / ybest7.park (박병훈) / Create
- 2025-08-21 / ybest7.park (박병훈) / 수정
- 2025-09-26 / ybest7.park (박병훈) / input query 및 out put query 수정
- 2025-09-29 / ybest7.park (박병훈) / SALES_DOMAIN_AP2_COLUMN이 "All"인 데이터 추가

* Input

* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_TargetEcpDim = Select ([Version].[Version Name] * [Item].[Segment] * [Sales Domain].[AP2]) on row,({Measure.[Sales Item Asn_Valid Flag], Measure.[Dummy]}) on column ;
   - df_in_TargetEcp = Select ([Version].[Version Name]* [Sales Domain].[AP2] * [Item].[Segment] ) on row, ({Measure.[Target Ecp Set_Build Ahead Must], Measure.[Target Ecp Set_EOH], Measure.[Target Ecp Set_SS Must], Measure.[Target Ecp Set_WOS],Measure.[Dummy]}) on column;

* Output Table
    - df_out_TargetEcp = Select ([Version].[Version Name].[CWV_MP] * [Sales Domain].[AP2] * [Item].[Segment] ) on row, ({Measure.[Target Ecp Set_Build Ahead Must], Measure.[Target Ecp Set_EOH], Measure.[Target Ecp Set_SS Must], Measure.[Target Ecp Set_WOS]}) on column;


* 데이터 삭제
    DELETE DATA FOR MODEL [Target Ecp Set] where {Version.[Version Name].[CurrentWorkingView]};


* 테스트 스크립트
    EXEC plugin instance [PY_UI_TargetEcp] for measures {[Target Ecp Set_Build Ahead Must]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), (paramOutVersion,"CWV_MP"), ([Param.o9_sys_log_level], "DEBUG")} ;


* 데이터 확인


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

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_TargetEcp'
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
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_TargetEcpDim = read_csv_file('df_in_TargetEcpDim')
            df_in_TargetEcp = read_csv_file('df_in_TargetEcp')

        dataframes = {
            'df_in_TargetEcpDim': df_in_TargetEcpDim,
            'df_in_TargetEcp': df_in_TargetEcp,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_SEGMENT_COLUMN = 'Item.[Segment]'
        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'

        Sales_Item_Asn_Valid_Flag = 'Sales Item Asn_Valid Flag'

        Target_Ecp_Set_Build_Ahead_Must = 'Target Ecp Set_Build Ahead Must'
        Target_Ecp_Set_EOH = 'Target Ecp Set_EOH'
        Target_Ecp_Set_SS_Must = 'Target Ecp Set_SS Must'
        Target_Ecp_Set_WOS = 'Target Ecp Set_WOS'

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        ############### SALES_DOMAIN_AP2_COLUMN이 "All"인 데이터 추가 - 2025-09-29 ########################### ybest7.park
        df_in_TargetEcpDim_temp = df_in_TargetEcpDim[[VERSION_NAME_COLUMN, ITEM_SEGMENT_COLUMN]].drop_duplicates(
            keep='first')
        df_in_TargetEcpDim_temp[SALES_DOMAIN_AP2_COLUMN] = 'All'

        print_df(df_in_TargetEcpDim_temp, 'df_in_TargetEcpDim_temp 확인')
        note(f"df_in_TargetEcpDim_temp shape {df_in_TargetEcpDim_temp.shape}")
        note(f"df_in_TargetEcpDim shape {df_in_TargetEcpDim.shape}")

        df_in_TargetEcpDim_temp = pd.concat([df_in_TargetEcpDim, df_in_TargetEcpDim_temp], ignore_index=True)

        note(f"df_in_TargetEcpDim_temp concat 후 shape {df_in_TargetEcpDim.shape}")

        # Index Columns 설정  2025-08-21 수정 (ybest7.park)
        Index_cols = [VERSION_NAME_COLUMN, ITEM_SEGMENT_COLUMN, SALES_DOMAIN_AP2_COLUMN]

        # df_in_TargetEcpDim 과 df_in_TargetEcp 서로 없는 것들만 필터링
        df_out_TargetEcp = df_in_TargetEcpDim_temp[
            ~df_in_TargetEcpDim_temp.set_index(Index_cols).index.isin(df_in_TargetEcp.set_index(Index_cols).index)].drop(
            columns='Dummy')

        # Version 값 변경
        df_out_TargetEcp.loc[:, VERSION_NAME_COLUMN] = paramOutVersion
        # df_out_TargetEcp 데이터 프레임 값 설정
        df_out_TargetEcp = pd.concat([df_out_TargetEcp, df_in_TargetEcp], axis=0, ignore_index=True)
        # Vector 연산을 위해 Columns 설정
        N_col = [Target_Ecp_Set_Build_Ahead_Must, Target_Ecp_Set_SS_Must]
        percent_col = [Target_Ecp_Set_EOH, Target_Ecp_Set_WOS]
        df_out_TargetEcp[N_col] = df_out_TargetEcp[N_col].fillna('N')
        df_out_TargetEcp[percent_col] = df_out_TargetEcp[percent_col].fillna(1)
        # Out frame 순서 지정
        df_out_TargetEcp = df_out_TargetEcp[
            [VERSION_NAME_COLUMN, SALES_DOMAIN_AP2_COLUMN, ITEM_SEGMENT_COLUMN, Target_Ecp_Set_Build_Ahead_Must,
             Target_Ecp_Set_EOH, Target_Ecp_Set_SS_Must, Target_Ecp_Set_WOS]]

        print_df(df_out_TargetEcp, 'df_out_TargetEcp 최종 출력결과 확인')

        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################

        step('=====> STEP4 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_TargetEcp, 'df_out_TargetEcp', True)

        print_df(df_out_TargetEcp, 'df_out_TargetEcp', True)

        row_count, col_count = df_out_TargetEcp.shape
        note(f'=====> Final df_out_SalesAct rows : {row_count} , Columns : {col_count}')

        step('=====> STEP4 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_TargetEcp = pd.DataFrame([], columns=[])

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