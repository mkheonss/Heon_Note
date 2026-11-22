"""

* 프로그램명
    - PY_UI_LoadingMasterManagement

* 내용
    - SOP W_SET SOP Qty 의 Container 용적 율 계산
    - Demand가 있는 경우 Flag의 설정 변경

* 변경 이력
    - 2026-01-08  /best7.park (박병훈) / 신규 생성 Create

* Input Table
    - df_in_LoadingMaster = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Loading Master_40FT Qty],  Measure.[Loading Master_CBM],Measure.[Loading Master_Minimum Lot], Measure.[Dummy]}) on column where {Measure.[Loading Master_40FT Qty] >0} ;
    - df_in_SOPW = Select ([Version].[Version Name] * [Location].[Location] * [To Time].[To Week] * [Item].[Item] *  [To Location].[To Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP W_SET SOP Qty], Measure.[Dummy]}) on column  where {Measure.[SOP W_SET SOP Qty] >0};
    - df_in_TimeWeek = select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(1).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(6).Key));

* Output Table
    - df_out_SOPContainerLoading = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Container].[ContainerType] * [Loading].[Loading Type] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP CTNR Loading_CBM Prop], Measure.[SOP CTNR Loading_CTNR CBM], Measure.[SOP CTNR Loading_CTNR Prop], Measure.[SOP CTNR Loading_CTNR Qty], Measure.[SOP CTNR Loading_CTNR Type], Measure.[SOP CTNR Loading_LOT Size], Measure.[SOP CTNR Loading_LOT Size Prop], Measure.[SOP CTNR Loading_Loading Qty], Measure.[SOP CTNR Loading_Navigate], Measure.[SOP CTNR Loading_SOP CBM], Measure.[SOP CTNR Loading_SOP Qty]}) on column;

* 데이터 삭제  (주의 필요 삭제 시 Input Data도 전부 삭제 됨)
    - DELETE DATA FOR MODEL [SOP Container Loading] where {Version.[Version Name].[CWV_MP]};


* 테스트 스티립
    - EXEC plugin instance [PY_UI_LoadingMasterManagement] for measures {[SOP CTNR Loading_CTNR Qty]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (paramOutVersion ,"CWV_MP")} ;


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
str_instance = 'PY_UI_LoadingMasterManagement'
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
            df_in_LoadingMaster = read_csv_file('df_in_LoadingMaster')
            df_in_SOPW = read_csv_file('df_in_SOPW')
            df_in_TimeWeek = read_csv_file('df_in_TimeWeek')

        dataframes = {
            'df_in_LoadingMaster'    :        df_in_LoadingMaster,
            'df_in_SOPW'             :        df_in_SOPW,
            'df_in_TimeWeek'         :        df_in_TimeWeek
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수설정
        Version_COLUMN = 'Version.[Version Name]'
        Item_COLUMN = 'Item.[Item]'
        Location_COLUMN = 'Location.[Location]'
        Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        To_Location_COLUMN = 'To Location.[To Location]'
        To_Time_Week_COLUMN = 'To Time.[To Week]'
        ContainerType_COLUMN = 'Container.[ContainerType]'
        Loading_Type_COLUMN = 'Loading.[Loading Type]'
        Time_Week_COLUMN = 'Time.[Week]'

        SOP_W_SET_SOP_Qty = 'SOP W_SET SOP Qty'

        Loading_Master_40FT_Qty = 'Loading Master_40FT Qty'
        Loading_Master_CBM = 'Loading Master_CBM'
        Loading_Master_Minimum_Lot = 'Loading Master_Minimum Lot'

        SOP_CTNR_Loading_LOT_Size_Prop = 'SOP CTNR Loading_LOT Size Prop'
        SOP_CTNR_Loading_CTNR_Qty = 'SOP CTNR Loading_CTNR Qty'
        SOP_CTNR_Loading_Loading_Qty = 'SOP CTNR Loading_Loading Qty'
        SOP_CTNR_Loading_CTNR_CBM = 'SOP CTNR Loading_CTNR CBM'

        Full_Container = 'Full Container'
        Mix_Container = 'Mix Container'
        inf = 'inf'
        Dummy = 'Dummy'

        step('=====> STEP 2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # df_in_SOPW 에서 To_Time_Week_COLUMN 기준으로 df_in_TimeWeek 의 주차 필터링
        week_list = df_in_TimeWeek[Time_Week_COLUMN].astype(str).unique().tolist()
        # df_in_SOPW To_Time_Week_COLUMN 데이터 형 변환
        df_in_SOPW[To_Time_Week_COLUMN] = df_in_SOPW[To_Time_Week_COLUMN].astype(str)
        # df_in_SOPW 주차 필터링
        df_in_SOPW_temp = df_in_SOPW[df_in_SOPW[To_Time_Week_COLUMN].isin(week_list)]

        # df_in_LoadingMaster & df_in_SOPW Merge
        # Merge key 설정
        merge_key = [Version_COLUMN, Location_COLUMN, Item_COLUMN]

        df_in_SOPW_temp = df_in_SOPW_temp.drop(columns=Dummy).merge(
            df_in_LoadingMaster.drop(columns=Dummy), on=merge_key, how='left')

        # number columns 에 대한 빈 값 0으로 채우기
        numbers_cols = [Loading_Master_40FT_Qty, Loading_Master_CBM, Loading_Master_Minimum_Lot]
        df_in_SOPW_temp[numbers_cols] = df_in_SOPW_temp[numbers_cols].fillna(0).astype(int)

        # df_in_SOPW 에는 있으나 df_in_LoadingMaster 에 없는 데이터 필터링
        df_in_SOPW_temp = df_in_SOPW_temp[df_in_SOPW_temp[Loading_Master_40FT_Qty] > 0]

        # container 수량  및  Qty 구하기
        df_in_SOPW_temp['full_container'] = df_in_SOPW_temp[SOP_W_SET_SOP_Qty] // df_in_SOPW_temp[
            Loading_Master_40FT_Qty]
        df_in_SOPW_temp['full_qty'] = df_in_SOPW_temp['full_container'] * df_in_SOPW_temp[Loading_Master_40FT_Qty]
        df_in_SOPW_temp['mix_qty'] = df_in_SOPW_temp[SOP_W_SET_SOP_Qty] % df_in_SOPW_temp[Loading_Master_40FT_Qty]

        # ContainerType_COLUMN 타입 설정
        df_in_SOPW_temp[ContainerType_COLUMN] = '40HC'

        # full_container copy
        df_in_SOPW_temp_full = df_in_SOPW_temp[df_in_SOPW_temp['full_container'] > 0].copy()
        df_in_SOPW_temp_full[Loading_Type_COLUMN] = Full_Container
        df_in_SOPW_temp_full = df_in_SOPW_temp_full.drop(columns=['mix_qty'], axis=1)
        df_in_SOPW_temp_full = df_in_SOPW_temp_full.rename(columns={
            To_Time_Week_COLUMN: Time_Week_COLUMN,
            To_Location_COLUMN: SUB_LOCATION_COLUMN,
            'full_container': SOP_CTNR_Loading_CTNR_Qty,
            'full_qty': SOP_CTNR_Loading_Loading_Qty})

        # mix_container copy
        df_in_SOPW_temp_mix = df_in_SOPW_temp[df_in_SOPW_temp['mix_qty'] > 0].copy()
        df_in_SOPW_temp_mix[Loading_Type_COLUMN] = Mix_Container
        df_in_SOPW_temp_mix = df_in_SOPW_temp_mix.drop(columns=['full_container', 'full_qty'])
        df_in_SOPW_temp_mix = df_in_SOPW_temp_mix.rename(columns={
            To_Time_Week_COLUMN: Time_Week_COLUMN,
            To_Location_COLUMN: SUB_LOCATION_COLUMN,
            'mix_qty': SOP_CTNR_Loading_Loading_Qty})
        df_in_SOPW_temp_mix[SOP_CTNR_Loading_CTNR_Qty] = 1


        print_df(df_in_SOPW_temp_full, "df_in_SOPW_temp_full 확인")
        print_df(df_in_SOPW_temp_mix, "df_in_SOPW_temp_mix 확인")

        step('=====> STEP 3 End')
        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')

        df_out_SOPContainerLoading = pd.concat([df_in_SOPW_temp_full, df_in_SOPW_temp_mix], axis=0, ignore_index=True)

        df_out_SOPContainerLoading[SOP_CTNR_Loading_CTNR_CBM] = 67.5

        # Output 컬럼 설정
        out_put_cols = [Version_COLUMN, Location_COLUMN, Item_COLUMN, Time_Week_COLUMN, ContainerType_COLUMN,
                        Loading_Type_COLUMN, SUB_LOCATION_COLUMN, Trans_Mode_COLUMN,
                        SOP_CTNR_Loading_CTNR_Qty, SOP_CTNR_Loading_Loading_Qty, SOP_CTNR_Loading_CTNR_CBM]
        # 컬럼 필터
        df_out_SOPContainerLoading = df_out_SOPContainerLoading[out_put_cols]

        print_df(df_out_SOPContainerLoading ,"df_out_SOPContainerLoading 확인")

        step('=====> STEP 4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_SOPContainerLoading, 'df_out_SOPContainerLoading', True)


        print_df(df_out_SOPContainerLoading, 'df_out_SOPContainerLoading', True)


        row_count, col_count = df_out_SOPContainerLoading.shape
        note(f'=====> Final df_out_ProductPrice rows : {row_count} , Columns : {col_count}')


    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPContainerLoading = pd.DataFrame([], columns=[])


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


