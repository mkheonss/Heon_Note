"""

* 프로그램명
    - PY_UI_TargetEOH

* 내용
     - Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Product Group] * [Sales Domain].[AP2]),
      where [Item].[Item Stage] = 'SKU' 값을

* 변경이력
- 2025.02.19 / ybest7.park (박병훈) / Create / df_in_PlanningMonth input data 추가
- 2025.09.26 / ybest7.park (박병훈) / 수정 및 삭제 / Input Query 수정에 따른 로직 수정
- 2025-09-29 / ybest7.park (박병훈) / SALES_DOMAIN_AP2_COLUMN이 "All"인 데이터 추가
- 2025-10-24 / ybest7.park (박병훈) / SALES_DOMAIN_AP2_COLUMN이 "All"인 데이터 제거 
                                    → 2025-09-29 추가되었던 부분 주석 처리

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_TargetEcpDim = Select ([Version].[Version Name] * [Item].[Segment] * [Sales Domain].[AP2]) on row,({Measure.[Sales Item Asn_Valid Flag], Measure.[Dummy]}) on column ;
   - df_in_TargetEOHSet = Select ([Version].[Version Name] * [Item].[Segment]  * [Time].[Planning Month] * [Sales Domain].[AP2] ) on row, ({Measure.[Target EOH Set_Week],Measure.[Dummy]}) on column;
   - df_in_PlanningMonth = Select ([Time].[Planning Month].filter(#.Key >= dateadd(&CWVUI.element(0).[Current Time For Version], -1, "month") && #.Key <= dateadd(&CWVUI.element(0).[Current Time For Version], 12, "month")));

* Output Table
    - df_out_TargetEOHSet = Select ([Version].[Version Name].[CWV_MP] * [Item].[Segment]  * [Time].[Planning Month] * [Sales Domain].[AP2] ) on row, ({Measure.[Target EOH Set_Week]}) on column;


* 데이터 삭제
    DELETE DATA FOR MODEL [Target EOH Set] where {Version.[Version Name].[CWV_MP]};


* 테스트 스크립트
    EXEC plugin instance [PY_UI_TargetEOH] for measures {[Target EOH Set_Week]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), (paramOutVersion,"CWV_MP"),([Param.o9_sys_log_level], "DEBUG")} ;


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
str_instance = 'PY_UI_TargetEOH'
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
            df_in_TargetEcpDim = read_csv_file('df_in_TragetEcpDim')
            df_in_TargetEOHSet = read_csv_file('df_in_TargetEOHSet')
            df_in_PlanningMonth = read_csv_file('df_in_PlanningMonth')

        dataframes = {
            'df_in_TargetEcpDim': df_in_TargetEcpDim,
            'df_in_TargetEOHSet': df_in_TargetEOHSet,
            'df_in_PlanningMonth': df_in_PlanningMonth
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
        TIME_PLANNING_MONTH_COLUMN = 'Time.[Planning Month]'

        Sales_Item_Asn_Valid_Flag = 'Sales Item Asn_Valid Flag'
        Target_EOH_Set_Week = 'Target EOH Set_Week'

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        # Grain 기준으로 df_in_TragetEcpDim 에만 있는 데이터 추출
        # Grain Columns 설정
        Grain_columns = [VERSION_NAME_COLUMN, ITEM_SEGMENT_COLUMN, SALES_DOMAIN_AP2_COLUMN]

        # df_in_TargetEOHSet 중복 삭제
        df_in_TargetEOHSet_temp = df_in_TargetEOHSet[Grain_columns].drop_duplicates()
        # df_in_TargetEOHSet Index 설정
        df_in_TargetEOHSet_index = df_in_TargetEOHSet_temp.set_index(Grain_columns).index
        # df_in_TragetEcpDim 중복삭제
        df_in_TargetEcpDim_temp = df_in_TargetEcpDim[Grain_columns].drop_duplicates()
        print_df(df_in_TargetEcpDim_temp, 'df_in_TargetEcpDim_temp 중복 삭제 후 확인 ')
        ############################ SALES_DOMAIN_AP2_COLUMN이 "All"인 데이터 추가 - 2025-09-29 - ybest7.park ############
        # df_in_TargetEcpDim_temp2 = df_in_TargetEcpDim[[VERSION_NAME_COLUMN, ITEM_SEGMENT_COLUMN]].drop_duplicates(
        #     keep='first')
        # df_in_TargetEcpDim_temp2[SALES_DOMAIN_AP2_COLUMN] = 'All'
        # print_df(df_in_TargetEcpDim_temp2, 'df_in_TargetEcpDim_temp2 데이터 추가 후 확인 ')
        #
        # df_in_TargetEcpDim_temp = pd.concat([df_in_TargetEcpDim_temp, df_in_TargetEcpDim_temp2], ignore_index=True)
        # print_df(df_in_TargetEcpDim_temp, 'df_in_TargetEcpDim_temp concat 후 확인 ')
        ############################ SALES_DOMAIN_AP2_COLUMN이 "All"인 데이터 추가 - 2025-09-29 - ybest7.park ############
        ############################ SALES_DOMAIN_AP2_COLUMN이 "All"인 데이터 불필요해 주석 처리 2025-10-24 ybest7.park ####
        # df_in_TragetEcpDim index 설정
        df_in_TargetEcpDim_index = df_in_TargetEcpDim_temp.set_index(Grain_columns).index
        # df_in_TragetEcpDim 에만 있는 Data filtering
        df_in_TargetEcpDim_temp = df_in_TargetEcpDim_temp[~df_in_TargetEcpDim_index.isin(df_in_TargetEOHSet_index)]

        print_df(df_in_TargetEcpDim_temp, 'df_in_TargetEcpDim_temp step - 01', True)
        ############################ 2025-08-21 수정 ####################################################################
        # Planning Month List 설정
        PlanningMonth_list = df_in_PlanningMonth[TIME_PLANNING_MONTH_COLUMN].unique().tolist()

        # Planning Month List 확장을 위한 column 설정
        df_in_TargetEcpDim_temp[TIME_PLANNING_MONTH_COLUMN] = df_in_TargetEcpDim_temp.apply(
            lambda x: PlanningMonth_list,
            axis=1)
        # Planning Month List 확장
        df_in_TragetEcpDim_temp = df_in_TargetEcpDim_temp.explode(TIME_PLANNING_MONTH_COLUMN)

        # reset index()
        df_in_TragetEcpDim_temp.reset_index(drop=True, inplace=True)

        # merge를 위한 타입 변경
        df_in_TragetEcpDim_temp[TIME_PLANNING_MONTH_COLUMN] = df_in_TragetEcpDim_temp[
            TIME_PLANNING_MONTH_COLUMN].astype(
            str)
        df_in_TargetEOHSet[TIME_PLANNING_MONTH_COLUMN] = df_in_TargetEOHSet[TIME_PLANNING_MONTH_COLUMN].astype(str)

        # Target EOH Set_Week 값을 위한 merge
        df_in_TragetEcpDim_temp = df_in_TragetEcpDim_temp.merge(df_in_TargetEOHSet.drop(columns='Dummy'),
                                                                on=[VERSION_NAME_COLUMN, ITEM_SEGMENT_COLUMN,
                                                                    SALES_DOMAIN_AP2_COLUMN,
                                                                    TIME_PLANNING_MONTH_COLUMN],
                                                                how='left')

        # Target_EOH_Set_Week 값 설정 Target_EOH_Set_Week 값이 null 이면 0
        df_in_TragetEcpDim_temp[Target_EOH_Set_Week] = (pd.to_numeric(
            df_in_TragetEcpDim_temp[Target_EOH_Set_Week], errors='coerce').fillna(0).astype(int))

        # # "Time_Planning_month" Columns 삭제 - 2025-09-26 삭제
        # df_in_TragetEcpDim_temp = df_in_TragetEcpDim_temp.drop(columns=TIME_PLANNING_MONTH_COLUMN, axis=1)
        ############################ 2025-08-21 수정 ####################################################################
        # df_in_TragetEcpDim_temp Data Frame 순서 지정
        df_in_TragetEcpDim_temp = df_in_TragetEcpDim_temp[
            [VERSION_NAME_COLUMN, ITEM_SEGMENT_COLUMN, TIME_PLANNING_MONTH_COLUMN, SALES_DOMAIN_AP2_COLUMN,
             Target_EOH_Set_Week]]

        print_df(df_in_TragetEcpDim_temp, 'df_in_TragetEcpDim_temp step - 02', True)
        step('=====> STEP3 End')
        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP4 Start : input data machining')

        df_out_TargetEOHSet = df_in_TragetEcpDim_temp.copy()

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_TargetEOHSet, 'df_out_TargetEOHSet', True)

        print_df(df_out_TargetEOHSet, 'df_out_TargetEOHSet', True)

        row_count, col_count = df_out_TargetEOHSet.shape
        note(f'=====> Final df_out_SalesAct rows : {row_count} , Columns : {col_count}')

        step('=====> STEP4 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_TargetEOHSet = pd.DataFrame([], columns=[])

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