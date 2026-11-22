"""

* 프로그램명
    - PY_UI_UpsellingSEGPrty

* 내용
     - select [Item].[Product Group] * [Item].[Marketing Name]
      where [Item].[Item Stage] = 'SKU' AND [Item].[Product Group] = 'TV'
      "Upselling SEG Priority TV" MG에 없는 Product Group * Marketing Name을 추가(Insert)

* 변경이력
- 2024.10.17 / de0413.shin (신동언) / Create
- 2025.10.23 / ybest7.park(박병훈) 수정
    → input query 하나로 통합 및 전체 적인 로직 수정

* Input
- df_in_Item = pd.read_csv('Item.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_ProductGroup  = Select ([Item].[Item Stage].[SET] * [Item].[Product Group].filter(#.Name in {"TV","AV","MONITOR"}) * [Item].[Marketing Name] *  [Item].[Strategy] *  [Item].[KPI] *[Item].[SCM Type].[SET]);
   - df_in_UpsellingTV = Select ([Version].[Version Name] * [Item].[Marketing Name] * [Product].[Product Group] ) on row,({Measure.[Upselling SEG Prty TV_Ctg], Measure.[Upselling SEG Prty TV_Prty], Measure.[Dummy] }) on column;
   - df_in_UpsellingAV = Select ([Version].[Version Name] * [Item].[Strategy] * [Product].[Product Group] ) on row,({Measure.[Upselling SEG Prty AV_Ctg], Measure.[Upselling SEG Prty AV_Prty],Measure.[Dummy]}) on column;
   - df_in_UpsellingMNT = Select ([Version].[Version Name] * [Item].[KPI] * [Product].[Product Group] ) on row,({Measure.[Upselling SEG Prty MNT_Ctg], Measure.[Upselling SEG Prty MNT_Prty],Measure.[Dummy]}) on column;

* Output Table
    - df_out_UpsellingTV = Select ([Version].[Version Name].[CWV_MP] * [Item].[Marketing Name] * [Product].[Product Group] ) on row,
                                              ({Measure.[Upselling SEG Prty TV_Ctg], Measure.[Upselling SEG Prty TV_Prty]}) on column;
    - df_out_UpsellingAV = Select ([Version].[Version Name].[CWV_MP] * [Item].[Strategy] * [Product].[Product Group] ) on row,
                                              ({Measure.[Upselling SEG Prty AV_Ctg], Measure.[Upselling SEG Prty AV_Prty]}) on column;
    - df_out_UpsellingMNT = Select ([Version].[Version Name].[CWV_MP] * [Item].[KPI] * [Product].[Product Group] ) on row,
                                            ({Measure.[Upselling SEG Prty MNT_Ctg], Measure.[Upselling SEG Prty MNT_Prty]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_UpsellingSEGPrty] for measures {[Upselling SEG Prty TV_Prty]} using scope (&MPV)
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* 데이터 삭제
    DELETE DATA FOR MODEL [Upselling SEG Priority TV] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [Upselling SEG Priority AV] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [Upselling SEG Priority Monitor] where {Version.[Version Name].[CWV_MP]};

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
str_instance = 'PY_UI_UpsellingSEGPrty'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = (
    "CWV_MP"
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion)
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
        step('=====> STEP 1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_ProductGroup    = read_csv_file('df_in_ProductGroup')
            df_in_UpsellingTV     = read_csv_file('df_in_UpsellingTV')
            df_in_UpsellingAV     = read_csv_file('df_in_UpsellingAV')
            df_in_UpsellingMNT    = read_csv_file('df_in_UpsellingMNT')


        dataframes = {
            'df_in_ProductGroup'    :    df_in_ProductGroup,
            'df_in_UpsellingTV'     :    df_in_UpsellingTV,
            'df_in_UpsellingAV'     :    df_in_UpsellingAV,
            'df_in_UpsellingMNT'    :    df_in_UpsellingMNT }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1 End')
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        MARKETING_NAME_COLUMN = 'Item.[Marketing Name]'
        PRODUCT_GROUP_COLUMN = 'Product.[Product Group]'
        ITEM_STRATEGY = 'Item.[Strategy]'
        ITEM_KPI = 'Item.[KPI]'

        TV_CFG = 'Upselling SEG Prty TV_Ctg'
        TV_PRTY = 'Upselling SEG Prty TV_Prty'
        AV_CFG = 'Upselling SEG Prty AV_Ctg'
        AV_PRTY = 'Upselling SEG Prty AV_Prty'
        MNT_CFG = 'Upselling SEG Prty MNT_Ctg'
        MNT_PRTY = 'Upselling SEG Prty MNT_Prty'

        TV = 'TV'
        AV = 'AV'
        MONITOR = 'MONITOR'

        step('=====> STEP 2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP 3 Start : input data machining')

        # ITEM_PRODUCT_GROUP_COLUMN 컬럼 명 변경 --> PRODUCT_GROUP_COLUMN 으로 변경
        df_in_ProductGroup = df_in_ProductGroup.rename(columns={ITEM_PRODUCT_GROUP_COLUMN: PRODUCT_GROUP_COLUMN})
        df_in_ProductGroup = df_in_ProductGroup.copy()
        # df_out_UpsellingTV Version 값 설정
        note(f"Version Name: {paramOutVersion}")
        df_in_ProductGroup[VERSION_NAME_COLUMN] = pd.Series(paramOutVersion, index=df_in_ProductGroup.index)

        # # 초기 데이터 프레임 정의
        # df_in_ItemProdTV     = pd.DataFrame()
        # df_in_ItemProdAV     = pd.DataFrame()
        # df_in_ItemProdMNT    = pd.DataFrame()
        # df_out_UpsellingTV   = pd.DataFrame()
        # df_out_UpsellingAV   = pd.DataFrame()
        # df_out_UpsellingMNT  = pd.DataFrame()

        # 각 ITEM_PRODUCT_GROUP 으로 데이터 프레임 나누기
        df_in_ItemProdTV = df_in_ProductGroup[df_in_ProductGroup[PRODUCT_GROUP_COLUMN] == TV].drop(
            columns=[ITEM_STRATEGY, ITEM_KPI], axis=1)  # TV 필터

        df_in_ItemProdAV = df_in_ProductGroup[df_in_ProductGroup[PRODUCT_GROUP_COLUMN] == AV].drop(
            columns=[MARKETING_NAME_COLUMN, ITEM_KPI], axis=1)  # AV 필터

        df_in_ItemProdMNT = df_in_ProductGroup[df_in_ProductGroup[PRODUCT_GROUP_COLUMN] == MONITOR].drop(
            columns=[MARKETING_NAME_COLUMN, ITEM_STRATEGY], axis=1)  # MNT 필터

        ############################################## TV #############################################################
        # df_in_UpsellingTV에  PRODUCT_GROUP_COLUMN & MARKETING_NAME_COLUMN 기준으로 없는 데이터만 필터링
        df_out_UpsellingTV = df_in_ItemProdTV[
            ~df_in_ItemProdTV.set_index([VERSION_NAME_COLUMN, PRODUCT_GROUP_COLUMN, MARKETING_NAME_COLUMN]).index.isin(
                df_in_UpsellingTV.set_index([VERSION_NAME_COLUMN, PRODUCT_GROUP_COLUMN, MARKETING_NAME_COLUMN]).index)]

        df_out_UpsellingTV = df_out_UpsellingTV.copy()

        # Out put MG 설정
        df_out_UpsellingTV[TV_CFG] = 'L99999'
        df_out_UpsellingTV[TV_PRTY] = '99999'

        # 칼럼 정리
        df_out_UpsellingTV = df_out_UpsellingTV[
            [VERSION_NAME_COLUMN, MARKETING_NAME_COLUMN, PRODUCT_GROUP_COLUMN, TV_CFG, TV_PRTY]]


        ############################################## AV #############################################################

        df_out_UpsellingAV = df_in_ItemProdAV[
            ~df_in_ItemProdAV.set_index([VERSION_NAME_COLUMN, PRODUCT_GROUP_COLUMN, ITEM_STRATEGY]).index.isin(
                df_in_UpsellingAV.set_index([VERSION_NAME_COLUMN, PRODUCT_GROUP_COLUMN, ITEM_STRATEGY]).index)]

        df_out_UpsellingAV = df_out_UpsellingAV.copy()
        df_out_UpsellingAV[AV_CFG] = 'L99999'
        df_out_UpsellingAV[AV_PRTY] = '99999'

        # 칼럼 정리
        df_out_UpsellingAV = df_out_UpsellingAV[[VERSION_NAME_COLUMN, ITEM_STRATEGY, PRODUCT_GROUP_COLUMN, AV_CFG, AV_PRTY]]

        note(f"====================================> Step ex4")
        ############################################## Mnt #############################################################
        df_out_UpsellingMNT = df_in_ItemProdMNT[
            ~df_in_ItemProdMNT.set_index([VERSION_NAME_COLUMN, PRODUCT_GROUP_COLUMN, ITEM_KPI]).index.isin(
                df_in_UpsellingMNT.set_index([VERSION_NAME_COLUMN, PRODUCT_GROUP_COLUMN, ITEM_KPI]).index)]

        df_out_UpsellingMNT = df_out_UpsellingMNT.copy()
        df_out_UpsellingMNT[MNT_CFG] = 'L99999'
        df_out_UpsellingMNT[MNT_PRTY] = '99999'

        # 칼럼 정리
        df_out_UpsellingMNT = df_out_UpsellingMNT[[VERSION_NAME_COLUMN, ITEM_KPI, PRODUCT_GROUP_COLUMN, MNT_CFG, MNT_PRTY]]

        print_df(df_out_UpsellingTV, 'df_out_UpsellingTV ', True)
        print_df(df_out_UpsellingAV, 'df_out_UpsellingAV ', True)
        print_df(df_out_UpsellingMNT, 'df_out_UpsellingMNT ', True)

        step('=====> STEP 3 End')

        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_UpsellingTV, 'df_out_RTFHistW', True)
            print_df(df_out_UpsellingAV, 'df_out_UpsellingAV', True)
            print_df(df_out_UpsellingMNT, 'df_out_UpsellingMNT', True)

        print_df(df_out_UpsellingTV, 'df_out_UpsellingTV', True)
        row_count, col_count = df_out_UpsellingTV.shape
        note(f'=====> Final df_out_UpsellingTV rows : {row_count} , Columns : {col_count}')

        print_df(df_out_UpsellingAV, 'df_out_UpsellingAV', True)
        row_count, col_count = df_out_UpsellingAV.shape
        note(f'=====> Final df_out_UpsellingAV rows : {row_count} , Columns : {col_count}')

        print_df(df_out_UpsellingMNT, 'df_out_UpsellingMNT', True)
        row_count, col_count = df_out_UpsellingMNT.shape
        note(f'=====> Final df_out_UpsellingMNT rows : {row_count} , Columns : {col_count}')

        step('=====> STEP 4 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_UpsellingTV = pd.DataFrame([], columns=[])
        df_out_UpsellingAV = pd.DataFrame([], columns=[])
        df_out_UpsellingMNT = pd.DataFrame([], columns=[])

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