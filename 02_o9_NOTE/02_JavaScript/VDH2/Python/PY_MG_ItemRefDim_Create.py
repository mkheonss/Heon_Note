"""

* 프로그램명
    - PY_MG_ItemRefDim_Create

* 프로그램 등록일 : 2025/12/18

* 내용

    - 현재는 확정생산계획만 대상(생산라인)
    - 2025/12/18 → Item Basic Name, Project, Inch의 데이터(멤버를)
        Basic Name, Project, Inch에 Attribute 추가


* 변경이력
- 2025/12/18 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary

* Input Table
     - df_in_ItemBase = Select ([Item].[Item] * [Item].[Basic Name] * [Item].[Project] * [Item].[Inch] ) on row;
    -  df_in_BasicName = Select ([Basic Name].[Basic Name]) on row;
    -  df_in_Project = Select ([Project].[Project]) on row;
    -  df_in_Inch = Select ([Inch].[Inch]) on row;
* 데이터 삭제
    - DELETE DATA FOR MODEL [MP Batch_Item Bulk Member Creation] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_ItemRefDimCreate = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] ) on row, ({Measure.[MP Batch_Item Bulk Member Creation_BasicName], Measure.[MP Batch_Item Bulk Member Creation_Inch], Measure.[MP Batch_Item Bulk Member Creation_Project]}) on column;
    - df_out_log
    - df_out_logDetail
* 실행구문
    - EXEC plugin instance [PY_MG_ItemRefDim_Create] for measures {[MP Batch_Item Bulk Member Creation_BasicName]} using scope ( &CWVUI ) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000),(paramOutVersion,"CWV_MP"), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };

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
str_instance = 'PY_MG_ItemRefDim_Create'
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
            df_in_ItemBase = read_csv_file('df_in_ItemBase')
            df_in_BasicName = read_csv_file('df_in_BasicName')
            df_in_Project = read_csv_file('df_in_Project')
            df_in_Inch = read_csv_file('df_in_Inch')

        dataframes = {
            'df_in_ItemBase': df_in_ItemBase,
            'df_in_BasicName': df_in_BasicName,
            'df_in_Project': df_in_Project,
            'df_in_Inch': df_in_Inch,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        Version_Name_COLUMNS = 'Version.[Version Name]'
        Item_COLUMNS = 'Item.[Item]'
        Item_Basic_Name_COLUMN = 'Item.[Basic Name]'
        Item_Project_COLUMN = 'Item.[Project]'
        Item_Inch_COLUMN = 'Item.[Inch]'
        Basic_COLUMN = 'Basic Name.[Basic Name]'
        Project_COLUMN = 'Project.[Project]'
        Inch_COLUMN = 'Inch.[Inch]'

        MP_Batch_Item_Bulk_Member_Creation_BasicName = 'MP Batch_Item Bulk Member Creation_BasicName'
        MP_Batch_Item_Bulk_Member_Creation_Inch = 'MP Batch_Item Bulk Member Creation_Inch'
        MP_Batch_Item_Bulk_Member_Creation_Project = 'MP Batch_Item Bulk Member Creation_Project'

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 비교 대상을 Series로 변환
        # 기본이 되는 데이터 프레임  데이터 타입 변경 및 Series로 변환
        b_basic_name = df_in_ItemBase[Item_Basic_Name_COLUMN].astype(str)
        b_Project = df_in_ItemBase[Item_Project_COLUMN].astype(str)
        b_Inch = df_in_ItemBase[Item_Inch_COLUMN].astype(str)

        # 비교할 대상에 대해서 Series 로 변환 및 데이터 타입 변환
        r_basic_name = df_in_BasicName[Basic_COLUMN].astype(str)
        r_Project = df_in_Project[Project_COLUMN].astype(str)
        r_Inch = df_in_Inch[Inch_COLUMN].astype(str)

        # 비교할 내용을 mask로 변환
        # 원본에만 있는 데이터 찾기 (Item_Basic_Name_COLUMN/Item_Project_COLUMN/Item_Inch_COLUMN 중 하나라도 있으면 True)
        mask = (
                ~b_basic_name.isin(r_basic_name) |
                ~b_Project.isin(r_Project) |
                ~b_Inch.isin(r_Inch)
        )

        # Out put Data Frame 설정
        df_out_ItemRefDimCreate = df_in_ItemBase.loc[
            mask, [Item_COLUMNS, Item_Basic_Name_COLUMN, Item_Project_COLUMN, Item_Inch_COLUMN]].copy().reset_index(
            drop=True)

        df_out_ItemRefDimCreate[Version_Name_COLUMNS] = paramOutVersion

        df_out_ItemRefDimCreate = df_out_ItemRefDimCreate.rename(
            columns=
            {Item_Basic_Name_COLUMN: MP_Batch_Item_Bulk_Member_Creation_BasicName,
             Item_Project_COLUMN: MP_Batch_Item_Bulk_Member_Creation_Project,
             Item_Inch_COLUMN: MP_Batch_Item_Bulk_Member_Creation_Inch})

        # 데이터 프레임 순서 지정

        df_out_ItemRefDimCreate = df_out_ItemRefDimCreate[[
            Version_Name_COLUMNS, Item_COLUMNS, MP_Batch_Item_Bulk_Member_Creation_BasicName,
            MP_Batch_Item_Bulk_Member_Creation_Project, MP_Batch_Item_Bulk_Member_Creation_Inch]]

        print_df(df_out_ItemRefDimCreate, "df_out_ItemRefDimCreate data 확인", True)

        step('=====> STEP3 End')


    ################################################################################################################
    # STEP 4 :  input data machining
    ################################################################################################################
        step('=====> STEP4 Start : Final output table create')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_ItemRefDimCreate, 'df_out_ItemRefDimCreate', True)

        print_df(df_out_ItemRefDimCreate, 'df_out_ItemRefDimCreate', True)


        row_count, col_count = df_out_ItemRefDimCreate.shape
        note(f'=====> Final df_out_ItemRefDimCreate rows : {row_count} , Columns : {col_count}')

        step('=====> STEP4 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ItemRefDimCreate = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
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
