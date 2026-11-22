"""

* 프로그램명
    - PY_UI_PSIAP2Act

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.10.21 / ybest7.park (박병훈) / Create
- 2025.09.19 / ybest7.park (박병훈) / New Template 적용

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_SalesPlan = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales Actual AP2_Aging Over 30days], Measure.[Sales Actual AP2_Aging Over 60days], Measure.[Sales Actual AP2_Aging Rate Over 30days], Measure.[Sales Actual AP2_Aging Rate Over 60days], Measure.[Sales Actual AP2_Annual Plan Amt USD], Measure.[Sales Actual AP2_Annual Plan Qty], Measure.[Sales Actual AP2_Arrival], Measure.[Sales Actual AP2_Arrival Detail], Measure.[Sales Actual AP2_BOH], Measure.[Sales Actual AP2_Build Ahead], Measure.[Sales Actual AP2_Dmd], Measure.[Sales Actual AP2_Dmd Fill Rate], Measure.[Sales Actual AP2_Dmd GI], Measure.[Sales Actual AP2_EOH], Measure.[Sales Actual AP2_EOH Adj], Measure.[Sales Actual AP2_EOH Amt KRW], Measure.[Sales Actual AP2_EOH Amt USD], Measure.[Sales Actual AP2_EOH W], Measure.[Sales Actual AP2_Fcst AP1], Measure.[Sales Actual AP2_Fcst AP2], Measure.[Sales Actual AP2_Fcst GC], Measure.[Sales Actual AP2_Fcst Ords], Measure.[Sales Actual AP2_Fcst RDD AP1], Measure.[Sales Actual AP2_Fcst RDD AP2], Measure.[Sales Actual AP2_GI Amt KRW], Measure.[Sales Actual AP2_GI Amt USD], Measure.[Sales Actual AP2_GI Qty], Measure.[Sales Actual AP2_GI W Accum], Measure.[Sales Actual AP2_GI W Accum Rate], Measure.[Sales Actual AP2_Intransit], Measure.[Sales Actual AP2_Inventory], Measure.[Sales Actual AP2_Prod], Measure.[Sales Actual AP2_RTF], Measure.[Sales Actual AP2_RTF RDD], Measure.[Sales Actual AP2_Sales], Measure.[Sales Actual AP2_Shipment], Measure.[Sales Actual AP2_Shipment Detail], Measure.[Sales Actual AP2_Short], Measure.[Sales Actual AP2_Stretch Plan Amt USD], Measure.[Sales Actual AP2_Stretch Plan Qty],Measure.[Dummy]  }) on column;
                       Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales Plan AP2_Dmd],Measure.[Sales Plan AP2_RTF],Measure.[Sales Plan AP2_Short],Measure.[Sales Plan AP2_Fcst GC],Measure.[Sales Actual AP2_Fcst AP2],Measure.[Sales Plan AP2_Fcst AP1],Measure.[Sales Plan AP2_Annual Plan Qty],Measure.[Sales Plan AP2_Stretch Plan Qty],Measure.[Sales Actual AP2_Annual Plan Amt USD],Measure.[Sales Actual AP2_Stretch Plan Amt USD],Measure.[Dummy]}) on column;
   - df_in_SalesActual =  Select ([Version].[Version Name]* [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Ship To]) on row, ({Measure.[Sales Actual_GI Qty],Measure.[Sales Actual_Sales],Measure.[Sales Actual_GI Amt KRW],Measure.[Sales Actual_GI Amt USD],Measure.[Dummy] }) on column;
   - df_in_SalesActualAP2 = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales Actual AP2_GI Qty], Measure.[Sales Actual AP2_Sales], Measure.[Sales Actual AP2_GI Amt KRW], Measure.[Sales Actual AP2_GI Amt USD], Measure.[Dummy]}) on column;
   - df_in_SalesHrcy = select ([Sales Domain].[GC]*[Sales Domain].[AP2]*[Sales Domain].[AP1]*[Sales Domain].[Ship To]);


* Output Table
    - df_out_SalesAct = Select (&MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,({Measure.[Sales Plan AP2_Dmd], Measure.[Sales Plan AP2_RTF],Measure.[Sales Plan AP2_Short],Measure.[Sales Plan AP2_Fcst GC],  Measure.[Sales Plan AP2_Fcst AP1],Measure.[Sales Plan AP2_Annual Plan Qty],Measure.[Sales Plan AP2_Stretch Plan Qty]}) on column;
    - df_out_SalesActualAP2 = Select (&MPV* [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales Actual AP2_GI Qty], Measure.[Sales Actual AP2_Sales], Measure.[Sales Actual AP2_GI Amt KRW], Measure.[Sales Actual AP2_GI Amt USD]}) on column;
* 테스트 스크립트
    EXEC plugin instance [PY_UI_PSIAP2Act] for measures {[Sales Actual AP2_Dmd]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), (paramOutVersion,"CWV_MP"), ([Param.o9_sys_log_level], "DEBUG")} ;

* 데이터 삭제
    - DELETE DATA FOR MODEL [Sales Plan AP2] where {Version.[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [Sales Actual AP2] where {Version.[Version Name].[CWV_MP]};




실행 전 프로시져를 통해 MF Site 삭제  필요

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
str_instance = 'PY_UI_PSIAP2Act'
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
            df_in_SalesPlan = read_csv_file('df_in_SalesPlan')
            df_in_SalesActual = read_csv_file('df_in_SalesActual')
            df_in_SalesActualAP2 = read_csv_file('df_in_SalesActualAP2')
            df_in_SalesHrcy = read_csv_file('df_in_SalesHrcy')

        dataframes = {
            'df_in_SalesPlan': df_in_SalesPlan,
            'df_in_SalesActual': df_in_SalesActual,
            'df_in_SalesActualAP2': df_in_SalesActualAP2,
            'df_in_SalesHrcy': df_in_SalesHrcy,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        Version_Name_COLUMN = 'Version.[Version Name]'
        Item_COLUMN = 'Item.[Item]'
        Time_Week_COLUM = 'Time.[Week]'
        Location_COLUM = 'Location.[Location]'
        SalesDomain_AP2_COLUMN = 'Sales Domain.[AP2]'
        Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
        Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
        SalesDomain_GC_COLUMN = 'Sales Domain.[GC]'
        SalesDomain_AP1_COLUMN = 'Sales Domain.[AP1]'
        SalesDomain_Ship_To_COLUMN = 'Sales Domain.[Ship To]'

        Sales_Plan_AP2_Dmd = 'Sales Plan AP2_Dmd'
        Sales_Plan_AP2_RTF = 'Sales Plan AP2_RTF'
        Sales_Plan_AP2_Short = 'Sales Plan AP2_Short'
        Sales_Plan_AP2_Fcst_GC = 'Sales Plan AP2_Fcst GC'
        Sales_Plan_AP2_Fcst_AP2 = 'Sales Plan AP2_Fcst AP2'
        Sales_Plan_AP2_Fcst_AP1 = 'Sales Plan AP2_Fcst AP1'
        Sales_Plan_AP2_Annual_Plan_Qty = 'Sales Plan AP2_Annual Plan Qty'
        Sales_Plan_AP2_Stretch_Plan_Qty = 'Sales Plan AP2_Stretch Plan Qty'
        Sales_Plan_AP2_Annual_Plan_Amt_USD = 'Sales Plan AP2_Annual Plan Amt USD'
        Sales_Plan_AP2_Stretch_Plan_Amt_USD = 'Sales Plan AP2_Stretch Plan Amt USD'

        Sales_Actual_AP2_Dmd = 'Sales Actual AP2_Dmd'
        Sales_Actual_AP2_RTF = 'Sales Actual AP2_RTF'
        Sales_Actual_AP2_Short = 'Sales Actual AP2_Short'
        Sales_Actual_AP2_Fcst_GC = 'Sales Actual AP2_Fcst GC'
        Sales_Actual_AP2_Fcst_AP2 = 'Sales Actual AP2_Fcst AP2'
        Sales_Actual_AP2_Fcst_AP1 = 'Sales Actual AP2_Fcst AP1'
        Sales_Actual_AP2_Annual_Plan_Qty = 'Sales Actual AP2_Annual Plan Qty'
        Sales_Actual_AP2_Stretch_Plan_Qty = 'Sales Actual AP2_Stretch Plan Qty'
        Sales_Actual_AP2_Annual_Plan_Amt_USD = 'Sales Actual AP2_Annual Plan Amt USD'
        Sales_Actual_AP2_Stretch_Plan_Amt_USD = 'Sales Actual AP2_Stretch Plan Amt USD'

        Sales_Actual_GI_Qty = 'Sales Actual_GI Qty'
        Sales_Actual_Sales = 'Sales Actual_Sales'
        Sales_Actual_GI_Amt_KRW = 'Sales Actual_GI Amt KRW'
        Sales_Actual_GI_Amt_USD = 'Sales Actual_GI Amt USD'

        Sales_Actual_AP2_GI_Qty = 'Sales Actual AP2_GI Qty'
        Sales_Actual_AP2_Sales = 'Sales Actual AP2_Sales'
        Sales_Actual_AP2_GI_Amt_KRW = 'Sales Actual AP2_GI Amt KRW'
        Sales_Actual_AP2_GI_Amt_USD = 'Sales Actual AP2_GI Amt USD'

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        Grain_col = df_in_SalesPlan.columns[:7]
        Plan_col = [col for col in df_in_SalesPlan.columns if col.startswith('Sales Plan')]
        Actual_col = [col for col in df_in_SalesPlan.columns if col.startswith('Sales Actual')]
        PlanLastWeek = df_in_SalesPlan[Time_Week_COLUM].max()
        df_in_SalesPlan[Actual_col] = 0
        df_in_SalesPlan = df_in_SalesPlan[df_in_SalesPlan[Time_Week_COLUM] == PlanLastWeek].copy()

        for prev_col, current_col in zip(Plan_col, Actual_col):
            df_in_SalesPlan[current_col] = np.where(df_in_SalesPlan[prev_col] >= 0, df_in_SalesPlan[prev_col], 0)

        print_df(df_in_SalesPlan, 'df_in_SalesPlan', True)

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP4 Start : input data machining')

        on_df = df_in_SalesHrcy.iloc[:, :2].copy()
        df_in_SalesPlan[SalesDomain_AP2_COLUMN] = df_in_SalesPlan[SalesDomain_AP2_COLUMN].astype(str)
        # df_in_SalesPlan.loc[:, SalesDomain_AP2_COLUMN] = df_in_SalesPlan[SalesDomain_AP2_COLUMN].astype(str)
        on_df.loc[:, SalesDomain_AP2_COLUMN] = on_df[SalesDomain_AP2_COLUMN].astype(str)

        df_in_SalesPlan = df_in_SalesPlan.merge(on_df, on=SalesDomain_AP2_COLUMN, how='inner')

        df_in_SalesPlan[SalesDomain_AP2_COLUMN] = np.where(df_in_SalesPlan[SalesDomain_GC_COLUMN] == '201', '201',
                                                           df_in_SalesPlan[SalesDomain_AP2_COLUMN])
        df_in_SalesPlan.drop_duplicates(inplace=True, keep='first')
        df_in_SalesPlan.reset_index(drop=True, inplace=True)

        df_Columns = Grain_col.tolist() + Plan_col + Actual_col
        df_in_SalesPlan = df_in_SalesPlan[df_Columns]

        print_df(df_in_SalesPlan, 'df_in_SalesPlan', True)

        df_out_SalesAct = df_in_SalesPlan.copy()
        # df_out_SalesAct.drop(
        #     columns=[Sales_Actual_AP2_Fcst_AP2, Sales_Actual_AP2_Annual_Plan_Amt_USD,
        #              Sales_Actual_AP2_Stretch_Plan_Amt_USD],
        #     axis=1, inplace=True
        # )
        rename_col = { Sales_Actual_AP2_Fcst_AP2 :Sales_Plan_AP2_Fcst_AP2 ,
                       Sales_Actual_AP2_Annual_Plan_Amt_USD: Sales_Plan_AP2_Annual_Plan_Amt_USD,
                       Sales_Actual_AP2_Stretch_Plan_Amt_USD :Sales_Plan_AP2_Stretch_Plan_Amt_USD}

        df_out_SalesAct=df_out_SalesAct.rename(columns=rename_col)

        df_out_SalesAct = df_out_SalesAct.drop_duplicates()

        print_df(df_out_SalesAct, 'df_out_SalesAct', True)

        step('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP5 Start : input data machining')

        Sales_MaxWeek = df_in_SalesActual[Time_Week_COLUM].max()
        Sales_MinWeek = sorted(df_in_SalesActual[Time_Week_COLUM].unique(), reverse=True)[6]

        df_in_SalesActualAP2 = df_in_SalesActualAP2[(df_in_SalesActualAP2[Time_Week_COLUM] >= Sales_MinWeek) & (
                df_in_SalesActualAP2[Time_Week_COLUM] <= Sales_MaxWeek)]
        ActualAP2GI_col = [col for col in df_in_SalesActualAP2.columns if col.startswith('Sales Actual AP2')]
        df_in_SalesActualAP2.loc[:, ActualAP2GI_col] = 0

        df_in_SalesActual[SalesDomain_Ship_To_COLUMN] = df_in_SalesActual[SalesDomain_Ship_To_COLUMN].astype(str)
        # df_in_SalesActual.loc[:, SalesDomain_Ship_To_COLUMN] = df_in_SalesActual[SalesDomain_Ship_To_COLUMN].astype(str)
        df_in_SalesHrcy[SalesDomain_Ship_To_COLUMN] = df_in_SalesHrcy[SalesDomain_Ship_To_COLUMN].astype(str)
        df_in_SalesActual = df_in_SalesActual.merge(df_in_SalesHrcy, on=SalesDomain_Ship_To_COLUMN, how='inner')

        df_in_SalesActual[SalesDomain_AP2_COLUMN] = np.where(df_in_SalesActual[SalesDomain_GC_COLUMN] == '201', '201',
                                                             df_in_SalesActual[SalesDomain_AP2_COLUMN])

        Actual_col = [col for col in df_in_SalesActual.columns if col.startswith('Sales Actual')]

        df_in_SalesActual_group = \
            df_in_SalesActual.groupby(
                [Version_Name_COLUMN, Item_COLUMN, Time_Week_COLUM, Location_COLUM, SalesDomain_AP2_COLUMN])[
                Actual_col].sum().reset_index()

        df_in_SalesActual_group[Trans_Mode_COLUMN] = '-'
        df_in_SalesActual_group[Sub_Location_COLUMN] = '-'
        AP2_rename_col = {Sales_Actual_GI_Qty: Sales_Actual_AP2_GI_Qty, Sales_Actual_Sales: Sales_Actual_AP2_Sales,
                          Sales_Actual_GI_Amt_KRW: Sales_Actual_AP2_GI_Amt_KRW,
                          Sales_Actual_GI_Amt_USD: Sales_Actual_AP2_GI_Amt_USD}
        df_out_SalesActualAP2 = df_in_SalesActual_group

        # df_out_SalesActualAP2[Time_Week_COLUM] = Sales_MaxWeek
        df_out_SalesActualAP2 = df_out_SalesActualAP2.rename(columns=AP2_rename_col)

        df_out_SalesActualAP2 = df_out_SalesActualAP2[Grain_col.tolist() + ActualAP2GI_col]
        df_out_SalesActualAP2 = df_out_SalesActualAP2.drop_duplicates(keep='first')
        df_out_SalesActualAP2 = df_out_SalesActualAP2[df_out_SalesActualAP2[Time_Week_COLUM] > Sales_MinWeek]

        df_out_SalesActualAP2 = df_out_SalesActualAP2.drop_duplicates()
        print_df(df_out_SalesActualAP2, 'df_out_SalesActualAP2', True)

        step('=====> STEP5 End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################
        step('=====> STEP6 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_SalesAct, 'df_out_SalesAct', True)
            print_df(df_out_SalesActualAP2, 'df_out_SalesActualAP2', True)

        print_df(df_out_SalesAct, 'df_out_SalesAct', True)
        print_df(df_out_SalesActualAP2, 'df_out_SalesActualAP2', True)

        row_count, col_count = df_out_SalesAct.shape
        note(f'=====> Final df_out_ProductSetW rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_SalesActualAP2.shape
        note(f'=====> Final df_out_ProductSetWSub rows : {row_count} , Columns : {col_count}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ProductSetW = pd.DataFrame([], columns=[])
        df_out_ProductSetWSub = pd.DataFrame([], columns=[])

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