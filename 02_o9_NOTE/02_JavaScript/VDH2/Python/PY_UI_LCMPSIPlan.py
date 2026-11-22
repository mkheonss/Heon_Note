"""
* 프로그램명
    - PY_UI_LCMPSIPlan

* 내용
    - LCM PSI Data 생성

* 변경이력
    - 2025.02.06 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_StartWeek   : Select (&CurrentWeek);
    - df_in_AllWeek     : Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
    - df_in_MDMHorizon  : Select (&MDMHorizon);
    - df_in_DemandW     : Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage] * Location.[Location] * &MDMHorizon ) on row,  ({Measure.[W Demand Quantity to SCS],Measure.[W Demand Fulfilled Quantity],Measure.[W Total Short Quantity],Measure.[W OnHand Quantity],Measure.[W Beginning On Hand],Measure.[W Material Production Quantity Plan Output],Measure.[W Material Consumption Quantity Plan Output], Measure.[W Expected Receipts],Measure.[W Ending On Hand],Measure.[W Target Inventory],Measure.[W Infinite Material Node]}) on column orderby Time.Week.Name;
    - df_in_SOPW        : Select ([Version].[Version Name] * [Item].[Item] * &MDMHorizon * [To Location].[To Location] * [To Item].[To Item] * [Location].[Location] * [To Time].[To Week] * [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [BOM Info].[BOM Version] * [Week2].[Week2] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row, ({Measure.[SOP W_BOM Cfm W], Measure.[SOP W_BOM Status], Measure.[SOP W_Chg Reason], Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID], Measure.[SOP W_Sht Qty], Measure.[SOP W_Sht Reason]}) on column;
    - df_in_SSMonitor   : Select (Version.[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({ Measure.[SS Monitor_Shipment], Measure.[SS Monitor_Shipment BuildAhead], Measure.[SS Monitor_SS Target Qty], Measure.[SS Monitor_SS Target Time], Measure.[SS Monitor_Shipment SS], Measure.[SS Monitor_Arrival SS], Measure.[SS Monitor_SS] }) on column;
    - df_in_LCMPSIActual: Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-4).Key && #.Key < &CurrentWeek.element(0).Key) * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[LCM PSI Actual_BOH], Measure.[LCM PSI Actual_EOH], Measure.[LCM PSI Actual_EOH W], Measure.[LCM PSI Actual_EOH+NOH], Measure.[LCM PSI Actual_EOH+NOH W], Measure.[LCM PSI Actual_GI], Measure.[LCM PSI Actual_Inv], Measure.[LCM PSI Actual_Inv W], Measure.[LCM PSI Actual_Inv+NOH], Measure.[LCM PSI Actual_Inv+NOH W], Measure.[LCM PSI Actual_NOH LCM]}) on column;
    - df_in_LCMPSIPlan  : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week].filter(#.Key == &CurrentWeek.element(0).LeadOffset(-1).Key) * [To Item].[To Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[LCM PSI Plan_SET SOP], Measure.[LCM PSI Plan_SET SOP Short]}) on column;
    - df_in_OnhandMtrlTTL: Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Dummy], Measure.[Onhand Mtrl Status_Unavail TTL]}) on column;

* Flow Summary
    -

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_LCMPSIPlan
    - df_out_LCMPSIActual

* 데이타 초기화
    - DELETE DATA FOR MODEL [LCM PSI Plan] WHERE {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_LCMPSIPlan] for measures {[LCM PSI Plan_Ship]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_LCMPSIPlan / MG:  LCM PSI Plan
        Select (&MPV * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Item].[To Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[LCM PSI Plan_Arrival], Measure.[LCM PSI Plan_Arrival Detail], Measure.[LCM PSI Plan_Arrival Detail SS], Measure.[LCM PSI Plan_Avg 8W Flow Qty], Measure.[LCM PSI Plan_BOH], Measure.[LCM PSI Plan_Block Onhand], Measure.[LCM PSI Plan_EOH], Measure.[LCM PSI Plan_EOH W], Measure.[LCM PSI Plan_EOH+NOH], Measure.[LCM PSI Plan_EOH+NOH W], Measure.[LCM PSI Plan_GI], Measure.[LCM PSI Plan_Intransit], Measure.[LCM PSI Plan_Inv], Measure.[LCM PSI Plan_Inv W], Measure.[LCM PSI Plan_Inv+NOH], Measure.[LCM PSI Plan_Inv+NOH W], Measure.[LCM PSI Plan_NOH LCM], Measure.[LCM PSI Plan_Open PO], Measure.[LCM PSI Plan_Prod], Measure.[LCM PSI Plan_Prod Detail], Measure.[LCM PSI Plan_Prod Detail SS], Measure.[LCM PSI Plan_Prod Short], Measure.[LCM PSI Plan_SET SOP], Measure.[LCM PSI Plan_SET SOP BLA], Measure.[LCM PSI Plan_SET SOP SS], Measure.[LCM PSI Plan_SET SOP Short], Measure.[LCM PSI Plan_SS], Measure.[LCM PSI Plan_SS Tar MinQ], Measure.[LCM PSI Plan_SS Tar MinTime], Measure.[LCM PSI Plan_Ship], Measure.[LCM PSI Plan_Ship Detail], Measure.[LCM PSI Plan_Ship Detail SS], Measure.[LCM PSI Plan_Ship Short]}) on column;
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
str_instance = 'PY_UI_LCMPSIPlan'
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
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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


def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
        return df[column_name].values[0]
    return None  # 기본값 반환


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



def set_unique_combinations(df, df2, columns):
    cols = list(filter(lambda col: col != TIME_WEEK_COLUMN, columns))

    # 데이터의 모든 고유 조합 생성
    unique_combinations = df[cols].copy().drop_duplicates()

    # 주차(TIME_WEEK_COLUMN) 데이터의 모든 조합 산출
    # df2 = df2.assign(key=1)
    df2 = df2.reset_index(drop=True).assign(key=1)  # 인덱스 리셋 추가
    unique_combinations = unique_combinations.assign(key=1)
    all_possible_combinations = unique_combinations.merge(df2, how="outer").drop(columns=['key']).drop_duplicates()

    # 결측 데이터 찾기 (left join & 필터링)
    df_copy = df[columns].copy().reset_index(drop=True)  # 인덱스 리셋 추가
    missing_rows = all_possible_combinations.merge(df_copy,
                                                   on=columns, how="left", indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return missing_rows


def get_previous_weeks_data(df, time_column, target_week, prior_weeks=4):
    """
    지정된 주(target_week)를 기준으로 이전 주(prior_weeks)만큼의 데이터를 반환하는 함수.

    Args:
        df (pd.DataFrame): 데이터를 포함한 데이터프레임.
        time_column (str): 주 정보를 포함한 열 이름.
        target_week (int): 기준 주 (예: 202427).
        prior_weeks (int): 기준 주 이전에 포함할 주의 개수 (기본값: 4).

    Returns:
        pd.DataFrame: 기준 주 이전 n주를 포함한 새로운 데이터프레임.
    """
    # 기준 주의 인덱스 찾기
    try:
        initial_idx = df[df[time_column] == target_week].index[0]
    except IndexError:
        raise ValueError(f"=====> 타겟 주({target_week})가 데이터프레임에 존재하지 않습니다.")

    # 시작 인덱스와 끝 인덱스 계산
    start_idx = max(0, initial_idx - prior_weeks)  # 시작 인덱스
    end_idx = initial_idx - 1  # 끝 인덱스

    # 데이터프레임 슬라이싱
    return df.iloc[start_idx:end_idx + 1].copy()


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
            df_in_StartWeek = read_csv_file("df_in_StartWeek")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_MDMHorizon = read_csv_file("df_in_MDMHorizon")
            df_in_DemandW = read_csv_file("df_in_DemandW")
            df_in_SOPW = read_csv_file("df_in_SOPW")
            df_in_SSMonitor = read_csv_file("df_in_SSMonitor")
            df_in_LCMPSIActual = read_csv_file("df_in_LCMPSIActual")
            df_in_LCMPSIPlan = read_csv_file("df_in_LCMPSIPlan")
            df_in_OnhandMtrlTTL = read_csv_file("df_in_OnhandMtrlTTL")


        dataframes = {
            'df_in_StartWeek': df_in_StartWeek,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_MDMHorizon': df_in_MDMHorizon,
            'df_in_DemandW': df_in_DemandW,
            'df_in_SOPW': df_in_SOPW,
            'df_in_SSMonitor': df_in_SSMonitor,
            'df_in_LCMPSIActual': df_in_LCMPSIActual,
            'df_in_LCMPSIPlan': df_in_LCMPSIPlan,
            'df_in_OnhandMtrlTTL': df_in_OnhandMtrlTTL,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        CODE_MAP_LCM_PROD_ITEM_COLUMN = 'Code Map LCM_Prod Item'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAY_KEY_COLUMN = 'Time.[DayKey]'
        TIME_DAY_WEEK_COLUMN = 'Time.[Day of Week]'
        TIME_DAY_COLUMN = 'Time.[Day]'
        LOCATION_COLUMN = 'Location.[Location]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        SOP_ID_COLUMN = 'SOP ID.[SOP ID]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'

        SOP_W_SOP_QTY_COLUMN = 'SOP W_SOP Qty'
        SOP_W_SHT_QTY_COLUMN = 'SOP W_Sht Qty'
        SOP_W_LCM_SOP_QTY_COLUMN = 'SOP W_LCM SOP Qty'
        SOP_W_LCM_BOH_QTY_COLUMN = 'SOP W_LCM BOH Qty'
        SOP_W_LCM_MFG_QTY_COLUMN = 'SOP W_LCM MFG Qty'
        SOP_W_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'
        SOP_W_SET_SOP_QTY_COLUMN = 'SOP W_SET SOP Qty'
        SOP_W_SET_BOH_QTY_COLUMN = 'SOP W_SET BOH Qty'

        TIME_W_SOLVER_CURRENT_BUCKET_COLUMN = 'Time.[W Solver Current Bucket]'
        TIME_W_SOLVER_START_BUCKET_COLUMN = 'Time.[W Solver Start Bucket]'
        TIME_W_SOLVER_END_BUCKET_COLUMN = 'Time.[W Solver End Bucket]'

        BOD_ITEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
        BOD_ITEM_EFF_ENDDATE_COLUMN = 'BOD Item_Eff Enddate'
        BOD_ITEM_EFF_STARTDATE_COLUMN = 'BOD Item_Eff Startdate'

        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        SALES_DOMAIN_CUSTOMER_GROUP_COLUMN = 'Sales Domain.[Customer Group]'
        SALES_DOMAIN_SHIP_TO_COLUMN = 'Sales Domain.[Ship To]'

        DEMAND_TYPE_COLUMN = 'Demand Type.[Demand Type]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'
        W_DEMAND_QUANTITY_COLUMN = 'W Demand Quantity'
        W_DEMAND_QUANTITY_TO_SCS_COLUMN = 'W Demand Quantity to SCS'
        W_DEMAND_FULFILLED_QUANTITY_COLUMN = 'W Demand Fulfilled Quantity'
        W_TOTAL_SHORT_QUANTITY_COLUMN = 'W Total Short Quantity'
        W_BEGINNING_ON_HAND_COLUMN = 'W Beginning On Hand'
        W_ENDDING_ON_HAND_COLUMN = 'W Ending On Hand'
        W_ONHAND_QUANTITY_COLUMN = 'W OnHand Quantity'

        SS_MONITOR_SHIPMENT_BUILDAHEAD_COLUMN = 'SS Monitor_Shipment BuildAhead'
        SS_MONITOR_SS_TARGET_QTY_COLUMN = 'SS Monitor_SS Target Qty'
        SS_MONITOR_SS_TARGET_TIME_COLUMN = 'SS Monitor_SS Target Time'
        SS_MONITOR_SHIPMENT_COLUMN = 'SS Monitor_Shipment'
        SS_MONITOR_SHIPMENT_SS_COLUMN = 'SS Monitor_Shipment SS'
        SS_MONITOR_ARRIVAL_SS_COLUMN = 'SS Monitor_Arrival SS'
        SS_MONITROT_SS_COLUMN = 'SS Monitor_SS'
        SS_MONITROT_SS_TARGET_TIME_COLUMN = 'SS Monitor_SS Target Time'
        SS_MONITROT_SS_TARGET_QTY_COLUMN = 'SS Monitor_SS Target Qty'

        ONHAND_MTRL_STATUS_UNAVAIL_TTL_COLUMN = 'Onhand Mtrl Status_Unavail TTL'

        LCM_PSI_PLAN_ARRIVAL_COLUMN = 'LCM PSI Plan_Arrival'
        LCM_PSI_PLAN_ARRIVAL_DETAIL_COLUMN = 'LCM PSI Plan_Arrival Detail'
        LCM_PSI_PLAN_ARRIVAL_DETAIL_SS_COLUMN = 'LCM PSI Plan_Arrival Detail SS'
        LCM_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN = 'LCM PSI Plan_Avg 8W Flow Qty'
        LCM_PSI_PLAN_BOH_COLUMN = 'LCM PSI Plan_BOH'
        LCM_PSI_PLAN_BLOCK_ONHAND_COLUMN = 'LCM PSI Plan_Block Onhand'
        LCM_PSI_PLAN_EOH_COLUMN = 'LCM PSI Plan_EOH'
        LCM_PSI_PLAN_EOH_W_COLUMN = 'LCM PSI Plan_EOH W'
        LCM_PSI_PLAN_EOH_NOH_COLUMN = 'LCM PSI Plan_EOH+NOH'
        LCM_PSI_PLAN_EOH_NOH_W_COLUMN = 'LCM PSI Plan_EOH+NOH W'
        LCM_PSI_PLAN_GI_COLUMN = 'LCM PSI Plan_GI'
        LCM_PSI_PLAN_INTRANSIT_COLUMN = 'LCM PSI Plan_Intransit'
        LCM_PSI_PLAN_INV_COLUMN = 'LCM PSI Plan_Inv'
        LCM_PSI_PLAN_INV_W_COLUMN = 'LCM PSI Plan_Inv W'
        LCM_PSI_PLAN_INV_NOH_COLUMN = 'LCM PSI Plan_Inv+NOH'
        LCM_PSI_PLAN_INV_NOH_W_COLUMN = 'LCM PSI Plan_Inv+NOH W'
        LCM_PSI_PLAN_NOH_LCM_COLUMN = 'LCM PSI Plan_NOH LCM'
        LCM_PSI_PLAN_OPEN_PO_COLUMN = 'LCM PSI Plan_Open PO'
        LCM_PSI_PLAN_PROD_COLUMN = 'LCM PSI Plan_Prod'
        LCM_PSI_PLAN_PROD_DETAIL_COLUMN = 'LCM PSI Plan_Prod Detail'
        LCM_PSI_PLAN_PROD_DETAIL_SS_COLUMN = 'LCM PSI Plan_Prod Detail SS'
        LCM_PSI_PLAN_PROD_SHORT_COLUMN = 'LCM PSI Plan_Prod Short'
        LCM_PSI_PLAN_SET_SOP_COLUMN = 'LCM PSI Plan_SET SOP'
        LCM_PSI_PLAN_SET_SOP_BLA_COLUMN = 'LCM PSI Plan_SET SOP BLA'
        LCM_PSI_PLAN_SET_SOP_SS_COLUMN = 'LCM PSI Plan_SET SOP SS'
        LCM_PSI_PLAN_SET_SOP_SHORT_COLUMN = 'LCM PSI Plan_SET SOP Short'
        LCM_PSI_PLAN_SS_COLUMN = 'LCM PSI Plan_SS'
        LCM_PSI_PLAN_SS_TAR_MIN_Q_COLUMN = 'LCM PSI Plan_SS Tar MinQ'
        LCM_PSI_PLAN_SS_TAR_MIN_TIME_COLUMN = 'LCM PSI Plan_SS Tar MinTime'
        LCM_PSI_PLAN_SHIP_COLUMN = 'LCM PSI Plan_Ship'
        LCM_PSI_PLAN_SHIP_DETAIL_COLUMN = 'LCM PSI Plan_Ship Detail'
        LCM_PSI_PLAN_SHIP_DETAIL_SS_COLUMN = 'LCM PSI Plan_Ship Detail SS'
        LCM_PSI_PLAN_SHIP_SHORT_COLUMN = 'LCM PSI Plan_Ship Short'

        LCM_PSI_ACTUAL_BOH_COLUMN = 'LCM PSI Actual_BOH'
        LCM_PSI_ACTUAL_EOH_COLUMN = 'LCM PSI Actual_EOH'
        LCM_PSI_ACTUAL_EOH_W_COLUMN = 'LCM PSI Actual_EOH W'
        LCM_PSI_ACTUAL_EOH_NOH_COLUMN = 'LCM PSI Actual_EOH+NOH'
        LCM_PSI_ACTUAL_EOH_NOH_W_COLUMN = 'LCM PSI Actual_EOH+NOH W'
        LCM_PSI_ACTUAL_GI_COLUMN = 'LCM PSI Actual_GI'
        LCM_PSI_ACTUAL_INV_COLUMN = 'LCM PSI Actual_Inv'
        LCM_PSI_ACTUAL_INV_W_COLUMN = 'LCM PSI Actual_Inv W'
        LCM_PSI_ACTUAL_INV_NOH_COLUMN = 'LCM PSI Actual_Inv+NOH'
        LCM_PSI_ACTUAL_INV_NOH_W_COLUMN = 'LCM PSI Actual_Inv+NOH W'
        LCM_PSI_ACTUAL_NOH_LCM_COLUMN = 'LCM PSI Actual_NOH LCM'
        LCM_PSI_ACTUAL_SET_SOP_COLUMN = 'LCM PSI Actual_SET SOP'
        LCM_PSI_ACTUAL_SET_SOP_SHORT_COLUMN = 'LCM PSI Actual_SET SOP Short'

        OCELL_PSI_ETA_COLUMN = 'Open Cell PSI_ETA'
        OCELL_PSI_ETD_COLUMN = 'Open Cell PSI_ETD'
        OCELL_PSI_NOH_LCM_COLUMN = 'Open Cell PSI_NOH_LCM'
        OCELL_PSI_NOH_LCM_ALL_COLUMN = 'Open Cell PSI_NOH_LCM_All'
        OCELL_PSI_ONHAND_COLUMN = 'Open Cell PSI_Onhand'
        OCELL_PSI_ONHAND_BLOCK_COLUMN = 'Open Cell PSI_Onhand_Block'
        OCELL_PSI_PROD_COLUMN = 'Open Cell PSI_Prod'
        OCELL_PSI_PROD_ALL_COLUMN = 'Open Cell PSI_Prod_All'
        OCELL_PSI_PROD_SHRT_COLUMN = 'Open Cell PSI_Prod_Shrt'
        OCELL_PSI_PROD_SHRT_ALL_COLUMN = 'Open Cell PSI_Prod_Shrt_All'
        OCELL_PSI_SET_SOP_COLUMN = 'Open Cell PSI_SET SOP'
        OCELL_PSI_SET_SOP_ALL_COLUMN = 'Open Cell PSI_SET SOP_All'
        OCELL_PSI_SET_SHORT_COLUMN = 'Open Cell PSI_SET Short'
        OCELL_PSI_SET_SHORT_ALL_COLUMN = 'Open Cell PSI_SET Short_All'

        QTY_COLUMN = 'QTY'
        AVG_COLUMN = 'AVG'
        EOH_W_QTY_COLUMN = 'EOH_W_QTY'
        EOH_W_AVG_COLUMN = 'EOH_W_AVG'
        AVG_8W_FLOW_QTY_COLUMN = 'AVG_8W_FLOW_QTY'
        AVG_8W_FLOW_AVG_COLUMN = 'AVG_8W_FLOW_AVG'
        EOH_NOH_W_QTY_COLUMN = 'EOH_NOH_W_QTY'
        EOH_NOH_W_AVG_COLUMN = 'EOH_NOH_W_AVG'
        INV_W_QTY_COLUMN = 'INV_W_QTY'
        INV_W_AVG_COLUMN = 'INV_W_AVG'
        INV_NOH_QTY_COLUMN = 'INV_NOH_QTY'
        INV_NOH_AVG_COLUMN = 'INV_NOH_AVG'
        INV_NOH_W_QTY_COLUMN = 'INV_NOH_W_QTY'
        INV_NOH_W_AVG_COLUMN = 'INV_NOH_W_AVG'

        df_LCMPSIPlan_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, LOCATION_COLUMN,
            SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TRANS_MODE_COLUMN, LCM_PSI_ACTUAL_BOH_COLUMN
        ]

        df_LCMPSIPlan2_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, LOCATION_COLUMN,
            SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TRANS_MODE_COLUMN,
            LCM_PSI_PLAN_SET_SOP_COLUMN, LCM_PSI_PLAN_SET_SOP_SS_COLUMN, LCM_PSI_PLAN_SET_SOP_BLA_COLUMN, LCM_PSI_PLAN_GI_COLUMN,
            LCM_PSI_PLAN_ARRIVAL_COLUMN, LCM_PSI_PLAN_BOH_COLUMN, LCM_PSI_PLAN_SS_COLUMN, LCM_PSI_PLAN_SS_TAR_MIN_TIME_COLUMN,
            LCM_PSI_PLAN_SS_TAR_MIN_Q_COLUMN, LCM_PSI_PLAN_ARRIVAL_DETAIL_SS_COLUMN, LCM_PSI_PLAN_SHIP_DETAIL_COLUMN,
            LCM_PSI_PLAN_SET_SOP_SHORT_COLUMN, LCM_PSI_PLAN_ARRIVAL_DETAIL_COLUMN, LCM_PSI_PLAN_SHIP_COLUMN,
            LCM_PSI_PLAN_SHIP_SHORT_COLUMN, LCM_PSI_PLAN_NOH_LCM_COLUMN, LCM_PSI_PLAN_INTRANSIT_COLUMN,
            LCM_PSI_PLAN_PROD_DETAIL_SS_COLUMN, LCM_PSI_PLAN_SHIP_DETAIL_SS_COLUMN,
            LCM_PSI_PLAN_PROD_COLUMN, LCM_PSI_PLAN_PROD_DETAIL_COLUMN, LCM_PSI_PLAN_PROD_SHORT_COLUMN,
            LCM_PSI_PLAN_BLOCK_ONHAND_COLUMN,
            LCM_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN,
            LCM_PSI_PLAN_EOH_NOH_W_COLUMN, LCM_PSI_PLAN_INV_W_COLUMN, LCM_PSI_PLAN_INV_NOH_W_COLUMN,
        ]

        df_LCMPSIActual_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, LOCATION_COLUMN,
            SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TRANS_MODE_COLUMN,
            LCM_PSI_ACTUAL_SET_SOP_COLUMN, LCM_PSI_ACTUAL_SET_SOP_SHORT_COLUMN,
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_DemandW = df_in_DemandW[df_in_DemandW[ITEM_COLUMN] == 'QE43LS03DAUXXH']
        # ------------------ 테스트 디버깅용 ------------------ end

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_SOPW.empty:
            raise CustomException("STEP3 by 0 ____ df_in_SOPW 값이 없습니다.")


        # ====================> 컬럼삭제 Start
        drop_columns = ['Dummy']
        for col in drop_columns:
            df_in_OnhandMtrlTTL.drop(columns=[col], inplace=True, errors='ignore')

        # ====================> End


        # ====================> Week 컬럼 추출 Start
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        df_in_MDMHorizon = df_in_MDMHorizon[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        # ====================> End


        # ====================> AP2 Start Week 추출 Start
        actual_start_week = int(get_first_value(df_in_StartWeek, TIME_WEEK_COLUMN))
        step(f'=====> actual_start_week : {actual_start_week}')
        # ====================> End




        # ====================> Week 타입 변경 Start
        dataframes = [
            df_in_AllWeek,
            df_in_LCMPSIActual,
            df_in_DemandW,
            df_in_MDMHorizon,
            df_in_SOPW,
            df_in_SSMonitor,
        ]
        for df in dataframes:
            df[TIME_WEEK_COLUMN] = pd.to_numeric(df[TIME_WEEK_COLUMN], errors='coerce')

        # ====================> End





        # ====================> STEP1 (Start) > df_in_SOPW, df_in_DemandW merge

        df_in_SOPW[TO_TIME_TO_WEEK_COLUMN] = pd.to_numeric(df_in_SOPW[TO_TIME_TO_WEEK_COLUMN], errors='coerce')
        df_in_SOPW = pd.merge(df_in_SOPW, df_in_DemandW, how='left',
                                     left_on=[VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_in_SOPW, 'STEP3 by 1.1  ____ df_in_SOPW .... merge')

        df_in_SOPW.drop(columns=[ITEM_COLUMN+'_y', TIME_WEEK_COLUMN+'_y'], inplace=True)
        df_in_SOPW.rename(columns={
            ITEM_COLUMN+'_x': ITEM_COLUMN,
            TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
        }, inplace=True)
        print_df(df_in_SOPW, 'STEP3 by 1.2  ____ df_in_SOPW .... column rename')

        # ====================> STEP1 (End)




        # ====================> Step 2 (Start) > df_in_SOPW, df_in_SSMonitor merge

        df_in_SOPW = pd.merge(df_in_SOPW, df_in_SSMonitor, how='left',
                                     left_on=[VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN, TRANS_MODE_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_in_SOPW, 'STEP3 by 2.1  ____ df_in_SOPW .... merge')

        df_in_SOPW.drop(columns=[TIME_WEEK_COLUMN+'_y', ITEM_COLUMN+'_y', SUB_LOCATION_COLUMN+'_y'], inplace=True)
        df_in_SOPW.rename(columns={
            TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
            ITEM_COLUMN+'_x': ITEM_COLUMN,
            SUB_LOCATION_COLUMN+'_x': SUB_LOCATION_COLUMN,
        }, inplace=True)
        print_df(df_in_SOPW, 'STEP3 by 2.2  ____ df_in_SOPW .... column rename')

        # ====================> Step 2 (End)

        step('=====> STEP3 End')



        # ################################################################################################################
        # # STEP 4 : output data machining
        # ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # 1 df_LCMPSIPlan create ================================================================
        #   1.1 데이터프레임 복사 및 Grain 컬럼 지정
        df_LCMPSIPlan = rename_and_delete_df(df_in_SOPW)
        df_LCMPSIPlan.drop(columns=[
            TIME_WEEK_COLUMN, TO_TIME_TO_WEEK_COLUMN, WEEK2_COLUMN, TRANS_MODE_COLUMN,
        ], inplace=True)
        print_df(df_LCMPSIPlan, 'STEP4 by 1.1.1  ____ df_LCMPSIPlan .... grain columns drop')

        df_LCMPSIPlan.rename(columns={
            TO_ITEM_TO_ITEM_COLUMN: TO_ITEM_TO_ITEM_COLUMN+'_x',
            ITEM_COLUMN: ITEM_COLUMN+'_x',
        }, inplace=True)
        df_LCMPSIPlan.rename(columns={
            ITEM_COLUMN+'_x': TO_ITEM_TO_ITEM_COLUMN,
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            TO_TRANS_MODE_COLUMN: TRANS_MODE_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN+'_x': ITEM_COLUMN,
        }, inplace=True)
        df_LCMPSIPlan = df_LCMPSIPlan[df_LCMPSIPlan[ITEM_COLUMN] != '-'].copy()
        print_df(df_LCMPSIPlan, 'STEP4 by 1.1.2  ____ df_LCMPSIPlan .... grain columns rename')

        #   1.2 컬럼편집
        df_LCMPSIPlan = df_LCMPSIPlan[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN,
            ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            SOP_W_LCM_BOH_QTY_COLUMN, SOP_W_LCM_MFG_QTY_COLUMN, SOP_W_LCM_SOP_QTY_COLUMN, SOP_W_SET_MFG_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN,
            W_DEMAND_QUANTITY_TO_SCS_COLUMN, W_DEMAND_FULFILLED_QUANTITY_COLUMN,
            SS_MONITOR_SHIPMENT_COLUMN, SS_MONITOR_SHIPMENT_BUILDAHEAD_COLUMN, SS_MONITROT_SS_COLUMN, SS_MONITROT_SS_TARGET_TIME_COLUMN,
            SS_MONITROT_SS_TARGET_QTY_COLUMN, SS_MONITOR_ARRIVAL_SS_COLUMN, SS_MONITOR_SHIPMENT_SS_COLUMN
        ]].reset_index(drop=True)
        print_df(df_LCMPSIPlan, 'STEP4 by 1.2.1  ____ df_LCMPSIPlan .... columns modify')

        df_LCMPSIPlan.rename(columns={
            SOP_W_SET_SOP_QTY_COLUMN: LCM_PSI_PLAN_SET_SOP_COLUMN,
            SS_MONITOR_SHIPMENT_COLUMN: LCM_PSI_PLAN_SET_SOP_SS_COLUMN,
            SS_MONITOR_SHIPMENT_BUILDAHEAD_COLUMN: LCM_PSI_PLAN_SET_SOP_BLA_COLUMN,
            SOP_W_LCM_SOP_QTY_COLUMN: LCM_PSI_PLAN_GI_COLUMN,
            SOP_W_LCM_MFG_QTY_COLUMN: LCM_PSI_PLAN_ARRIVAL_COLUMN,
            SOP_W_LCM_BOH_QTY_COLUMN: LCM_PSI_PLAN_BOH_COLUMN,
            SS_MONITROT_SS_COLUMN: LCM_PSI_PLAN_SS_COLUMN,
            SS_MONITROT_SS_TARGET_TIME_COLUMN: LCM_PSI_PLAN_SS_TAR_MIN_TIME_COLUMN,
            SS_MONITROT_SS_TARGET_QTY_COLUMN: LCM_PSI_PLAN_SS_TAR_MIN_Q_COLUMN,
            SS_MONITOR_ARRIVAL_SS_COLUMN: LCM_PSI_PLAN_ARRIVAL_DETAIL_SS_COLUMN,
            SS_MONITOR_SHIPMENT_SS_COLUMN: LCM_PSI_PLAN_SHIP_DETAIL_COLUMN,
        }, inplace=True)
        df_LCMPSIPlan[LCM_PSI_PLAN_SET_SOP_SHORT_COLUMN] = df_LCMPSIPlan[W_DEMAND_QUANTITY_TO_SCS_COLUMN] - df_LCMPSIPlan[W_DEMAND_FULFILLED_QUANTITY_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_ARRIVAL_DETAIL_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_GI_COLUMN] - df_LCMPSIPlan[LCM_PSI_PLAN_ARRIVAL_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_SHIP_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_GI_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_SHIP_SHORT_COLUMN] = df_LCMPSIPlan[W_DEMAND_QUANTITY_TO_SCS_COLUMN] - df_LCMPSIPlan[W_DEMAND_FULFILLED_QUANTITY_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_NOH_LCM_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_BOH_COLUMN] + df_LCMPSIPlan[LCM_PSI_PLAN_ARRIVAL_COLUMN] - df_LCMPSIPlan[LCM_PSI_PLAN_GI_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_INTRANSIT_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_GI_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_PROD_DETAIL_SS_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_SHIP_DETAIL_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_SHIP_DETAIL_SS_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_SHIP_DETAIL_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_PROD_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_ARRIVAL_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_PROD_DETAIL_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_ARRIVAL_COLUMN]
        df_LCMPSIPlan[LCM_PSI_PLAN_PROD_SHORT_COLUMN] = df_LCMPSIPlan[W_DEMAND_QUANTITY_TO_SCS_COLUMN] - df_LCMPSIPlan[W_DEMAND_FULFILLED_QUANTITY_COLUMN]

        print_df(df_LCMPSIPlan, 'STEP4 by 1.2.2  ____ df_LCMPSIPlan .... columns modify final')
        



        # 2 빈 주차 채워넣기 ================================================================
        columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN,
            ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN
        ]
        df_LCMPSIPlan[TIME_WEEK_COLUMN] = pd.to_numeric(df_LCMPSIPlan[TIME_WEEK_COLUMN], errors='coerce')
        df_in_MDMHorizon[TIME_WEEK_COLUMN] = pd.to_numeric(df_in_MDMHorizon[TIME_WEEK_COLUMN], errors='coerce')
        df_missing_rows = set_unique_combinations(df_LCMPSIPlan, df_in_MDMHorizon, columns)
        df_LCMPSIPlan = pd.concat([df_LCMPSIPlan, df_missing_rows], ignore_index=True).drop_duplicates()



        
        # 3 groupby ================================================================
        df_LCMPSIPlan[LCM_PSI_PLAN_EOH_COLUMN] = 0
        df_LCMPSIPlan[LCM_PSI_PLAN_EOH_NOH_COLUMN] = 0
        df_LCMPSIPlan[LCM_PSI_PLAN_INV_NOH_COLUMN] = 0
        int_columns = [
            LCM_PSI_PLAN_SET_SOP_COLUMN, LCM_PSI_PLAN_SET_SOP_SS_COLUMN, LCM_PSI_PLAN_SET_SOP_BLA_COLUMN, LCM_PSI_PLAN_GI_COLUMN,
            LCM_PSI_PLAN_ARRIVAL_COLUMN, LCM_PSI_PLAN_BOH_COLUMN, LCM_PSI_PLAN_SS_COLUMN, LCM_PSI_PLAN_SS_TAR_MIN_TIME_COLUMN,
            LCM_PSI_PLAN_SS_TAR_MIN_Q_COLUMN, LCM_PSI_PLAN_ARRIVAL_DETAIL_SS_COLUMN, LCM_PSI_PLAN_SHIP_DETAIL_COLUMN,
            LCM_PSI_PLAN_SET_SOP_SHORT_COLUMN, LCM_PSI_PLAN_ARRIVAL_DETAIL_COLUMN, LCM_PSI_PLAN_SHIP_COLUMN,
            LCM_PSI_PLAN_SHIP_SHORT_COLUMN, LCM_PSI_PLAN_NOH_LCM_COLUMN, LCM_PSI_PLAN_INTRANSIT_COLUMN,
            LCM_PSI_PLAN_PROD_DETAIL_SS_COLUMN, LCM_PSI_PLAN_SHIP_DETAIL_SS_COLUMN,
            LCM_PSI_PLAN_PROD_COLUMN, LCM_PSI_PLAN_PROD_DETAIL_COLUMN, LCM_PSI_PLAN_PROD_SHORT_COLUMN,
            LCM_PSI_PLAN_EOH_COLUMN, LCM_PSI_PLAN_EOH_NOH_COLUMN, LCM_PSI_PLAN_INV_NOH_COLUMN,
        ]
        for col in int_columns:
            df_LCMPSIPlan[col] = df_LCMPSIPlan[col].fillna(0).astype(int)

        groupby_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN,
            ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN
        ]
        sum_columns = (int_columns)
        agg_dict = {col: 'sum' for col in sum_columns}
        df_LCMPSIPlan = df_LCMPSIPlan.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_LCMPSIPlan, 'STEP4 by 3.1 ____ df_LCMPSIPlan .... groupby')

        
        
        # 4 EOH 및 BOH 설정 ================================================================
        #   4.1 eoh / boh 계산 수행
        #       첫번째 주차 EOH = BOH + Arrival - Req
        #         -> 첫번째 주차의 EOH 는 차주의 BOH로 설정

        #   NumPy group 백터연산
        def compute_group_numpy(group):
            # 주차별 정렬
            group = group.sort_values(by=TIME_WEEK_COLUMN).reset_index(drop=True)

            # NumPy 배열로 계산
            boh = group[LCM_PSI_PLAN_BOH_COLUMN].to_numpy()
            arrival = group[LCM_PSI_PLAN_ARRIVAL_COLUMN].to_numpy()
            gi = group[LCM_PSI_PLAN_GI_COLUMN].to_numpy()

            eoh = np.zeros_like(boh)
            eoh_noh = np.where(eoh < 0, 0, eoh)
            inv_noh = np.where(eoh < 0, 0, eoh)

            # 첫 번째 값
            eoh[0] = boh[0] + arrival[0] - gi[0]

            # 이후 값 계산
            for i in range(1, len(boh)):
                boh[i] = eoh[i - 1]
                eoh[i] = boh[i] + arrival[i] - gi[i]

            # 결과를 DataFrame에 반영
            group[LCM_PSI_PLAN_BOH_COLUMN] = boh
            group[LCM_PSI_PLAN_EOH_COLUMN] = eoh
            group[LCM_PSI_PLAN_EOH_NOH_COLUMN] = eoh_noh
            group[LCM_PSI_PLAN_INV_NOH_COLUMN] = inv_noh
            return group

        # 그룹화 및 벡터화 계산 수행
        # df_LCMPSIPlan = df_LCMPSIPlan.sort_values(
        #     by=[TIME_WEEK_COLUMN, ITEM_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN,
        #         ITEM_COMPONENT_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
        #     ascending=[True, True, True, True, True, True, True, True])

        df_LCMPSIPlan = df_LCMPSIPlan.groupby([
            VERSION_NAME_COLUMN, ITEM_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN,
            SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN
        ], sort=False, as_index=False).apply(compute_group_numpy)

        df_LCMPSIPlan[LCM_PSI_PLAN_INV_COLUMN] = df_LCMPSIPlan[LCM_PSI_PLAN_BOH_COLUMN] + df_LCMPSIPlan[LCM_PSI_PLAN_ARRIVAL_COLUMN] - df_LCMPSIPlan[LCM_PSI_PLAN_GI_COLUMN]
        print_df(df_LCMPSIPlan, 'STEP4 by 4.1 ____ df_LCMPSIPlan .... eoh & boh')



        # 5 EOHW 및 NOHW 설정 ================================================================

        # 기준정보
        initial_week = int(actual_start_week)   #202427
        prior_weeks = int(4)  # 이전 4주
        following_weeks = int(4)  # 다음 4주(current_week 포함)

        # 5.1 ap2_start_week 기준 이전 4주 가져오기
        df_before_4Week = get_previous_weeks_data(
            df=df_in_AllWeek,
            time_column=TIME_WEEK_COLUMN,
            target_week=initial_week,
            prior_weeks=prior_weeks  # 이전 4주
        )
        print_df(df_before_4Week, 'STEP4 by 5.1.1 ____ df_before_4Week .... range')


        # 5.2 실적수량 가져오기
        if not df_in_LCMPSIActual.empty:
            df_LCMPSIActual = pd.merge(df_before_4Week, df_in_LCMPSIActual, how='inner', on=[TIME_WEEK_COLUMN])
            print_df(df_LCMPSIActual, 'STEP4 by 5.2.1 ____ df_LCMPSIActual .... merge[df_before_4Week, df_in_LCMPSIActual]')

            #   2.2 컬럼 select
            columns = [
                ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TRANS_MODE_COLUMN,
                LCM_PSI_ACTUAL_GI_COLUMN, LCM_PSI_ACTUAL_EOH_NOH_COLUMN, LCM_PSI_ACTUAL_INV_COLUMN, LCM_PSI_ACTUAL_INV_NOH_W_COLUMN
            ]
            df_LCMPSIActual = df_LCMPSIActual[columns].drop_duplicates()
            print_df(df_LCMPSIActual, 'STEP4 by 5.2.2 ____ df_LCMPSIActual .... column select')

            #   2.3 실적 수량을 QTY 로 변경
            df_LCMPSIActual.rename(columns={
                LCM_PSI_ACTUAL_GI_COLUMN: EOH_W_QTY_COLUMN,
                LCM_PSI_ACTUAL_EOH_NOH_COLUMN: EOH_NOH_W_QTY_COLUMN,
                LCM_PSI_ACTUAL_INV_COLUMN: INV_W_QTY_COLUMN,
                LCM_PSI_ACTUAL_INV_NOH_W_COLUMN: INV_NOH_W_QTY_COLUMN,
            }, inplace=True)

            columns = [EOH_W_QTY_COLUMN, EOH_NOH_W_QTY_COLUMN, INV_W_QTY_COLUMN, INV_NOH_W_QTY_COLUMN]
            df_LCMPSIActual[columns] = df_LCMPSIActual[columns].fillna(np.nan).astype('float64')
            print_df(df_LCMPSIActual, 'STEP4 by 5.2.3 ____ df_LCMPSIActual .... column modify')

        else:
            columns = [
                ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TRANS_MODE_COLUMN,
            ]
            df_LCMPSIActual = df_LCMPSIPlan[columns].copy()
            df_LCMPSIActual[EOH_W_QTY_COLUMN] = 0
            df_LCMPSIActual[EOH_NOH_W_QTY_COLUMN] = 0
            df_LCMPSIActual[INV_W_QTY_COLUMN] = 0
            df_LCMPSIActual[INV_NOH_W_QTY_COLUMN] = 0

            df_missing_rows = set_unique_combinations(df_LCMPSIActual, df_before_4Week, columns)
            df_LCMPSIActual = pd.concat([df_LCMPSIActual, df_missing_rows], ignore_index=True).drop_duplicates()
            print_df(df_LCMPSIActual, 'STEP4 by 5.2.1 ____ df_LCMPSIActual .... week add')



        # 5.3 계획정보 편집
        #   5.3.1 actual_start_week 기준 이전4주차를 가지는 LCMPSIPlan create (qty 는 RTF)
        df_LCMPSIPlanModify = df_LCMPSIPlan.copy()
        print_df(df_LCMPSIPlanModify, 'STEP4 by 5.3.0 ____ df_LCMPSIPlanModify .... copy')
        columns = [
            ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TRANS_MODE_COLUMN,
            LCM_PSI_PLAN_SET_SOP_COLUMN, LCM_PSI_PLAN_EOH_NOH_COLUMN, LCM_PSI_PLAN_INV_COLUMN,
        ]
        df_LCMPSIPlanModify = df_LCMPSIPlanModify[columns].drop_duplicates()
        print_df(df_LCMPSIPlanModify, 'STEP4 by 5.3.1 ____ df_LCMPSIPlanModify .... columns select')


        # 5.4 계획과 실적 합치기
        #   5.4.1 df_LCMPSIActual, df_LCMPSIPlanModify concat
        df_eoh_w = pd.concat([df_LCMPSIActual, df_LCMPSIPlanModify]).drop_duplicates()
        print_df(df_eoh_w, 'STEP4 by 5.4.1 ____ df_eoh_w .... concat[df_LCMPSIActual, df_LCMPSIPlanModify]')

        #   5.4.2 실적 + 계획 모든 주차 생성
        df_plan_week = df_in_MDMHorizon.copy()
        df_all_actual_plan_week = pd.concat([df_before_4Week, df_plan_week], ignore_index=True).drop_duplicates()
        print_df(df_all_actual_plan_week, 'STEP4 by 5.4.2 ____ df_all_actual_plan_week .... all actual_plan week make')

        #   5.4.3 eoh 계산 위한 주차 채워넣기
        columns = [ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TRANS_MODE_COLUMN]
        df_missing_rows = set_unique_combinations(df_eoh_w, df_all_actual_plan_week, columns)
        print_df(df_missing_rows, 'STEP4 by 5.4.3 ____ df_missing_rows .... week add')
        df_eoh_w = pd.concat([df_eoh_w, df_missing_rows], ignore_index=True).drop_duplicates()
        print_df(df_eoh_w, 'STEP4 by 5.4.3 ____ df_eoh_w .... week add')

        #   5.4.4 계획 수량을 QTY로 변경
        int_columns = [LCM_PSI_PLAN_SET_SOP_COLUMN, LCM_PSI_PLAN_EOH_NOH_COLUMN, LCM_PSI_PLAN_INV_COLUMN]
        for col in int_columns:
            df_eoh_w[col] = df_eoh_w[col].fillna(np.nan).astype('float64')

        df_eoh_w[EOH_W_QTY_COLUMN] = df_eoh_w[LCM_PSI_PLAN_SET_SOP_COLUMN]
        df_eoh_w[EOH_NOH_W_QTY_COLUMN] = df_eoh_w[LCM_PSI_PLAN_EOH_NOH_COLUMN]
        df_eoh_w[INV_W_QTY_COLUMN] = df_eoh_w[LCM_PSI_PLAN_INV_COLUMN]
        df_eoh_w[INV_NOH_W_QTY_COLUMN] = df_eoh_w[LCM_PSI_PLAN_INV_COLUMN]
        print_df(df_eoh_w, 'STEP4 by 5.4.3.1 ____ df_eoh_w .... reselect')


        #   5.4.5 수량 sum
        groupby_columns = [ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [EOH_W_QTY_COLUMN, EOH_NOH_W_QTY_COLUMN, INV_W_QTY_COLUMN, INV_NOH_W_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_eoh_w = df_eoh_w.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_eoh_w, 'STEP5 by 5.4.5 ____ df_eoh_w .... groupby')


        # 5.6 EOH W 평균 계산
        def calculate_avg(df_group):
            # 그룹 데이터를 바로 처리 (numpy 적용)
            weeks = df_group[TIME_WEEK_COLUMN].values
            eoh_w_qty = df_group[EOH_W_QTY_COLUMN].values
            eoh_noh_w_qty = df_group[EOH_NOH_W_QTY_COLUMN].values
            inv_w_qty = df_group[INV_W_QTY_COLUMN].values
            inv_noh_w_qty = df_group[INV_NOH_W_QTY_COLUMN].values

            avg_results = []
            week_size = len(df_AllWeek) - 1  # 전체 데이터 길이

            for i in range(len(weeks)):
                week = weeks[i]
                if week < initial_week:
                    continue

                # 인덱스 시작 및 종료 탐색 최적화
                initial_idx = df_AllWeek_index.get(week, None)  # 미리 저장된 map을 활용, 없으면 None
                if initial_idx is None:
                    continue  # 해당 주가 없으면 건너뜀

                start_idx = max(initial_idx - prior_weeks, 0)
                end_idx = min(initial_idx + following_weeks, week_size)

                start_week = df_AllWeek_array[start_idx]
                end_week = df_AllWeek_array[end_idx]

                # 벡터화된 마스크 사용
                mask = (weeks >= start_week) & (weeks <= end_week)

                avg_eoh_w_qty = round(np.mean(eoh_w_qty[mask]), 1)
                avg_eoh_noh_w_qty = round(np.mean(eoh_noh_w_qty[mask]), 1)
                avg_inv_w_qty = round(np.mean(inv_w_qty[mask]), 1)
                avg_inv_noh_w_qty = round(np.mean(inv_noh_w_qty[mask]), 1)

                avg_results.append({
                    ITEM_COLUMN: df_group[ITEM_COLUMN].iloc[0],
                    LOCATION_COLUMN: df_group[LOCATION_COLUMN].iloc[0],
                    ITEM_METERIAL_COLUMN: df_group[ITEM_METERIAL_COLUMN].iloc[0],
                    SUB_LOCATION_COLUMN: df_group[SUB_LOCATION_COLUMN].iloc[0],
                    ITEM_COMPONENT_COLUMN: df_group[ITEM_COMPONENT_COLUMN].iloc[0],
                    TRANS_MODE_COLUMN: df_group[TRANS_MODE_COLUMN].iloc[0],
                    TIME_WEEK_COLUMN: week,
                    EOH_W_AVG_COLUMN: avg_eoh_w_qty,
                    EOH_NOH_W_AVG_COLUMN: avg_eoh_noh_w_qty,
                    INV_W_AVG_COLUMN: avg_inv_w_qty,
                    INV_NOH_W_AVG_COLUMN: avg_inv_noh_w_qty,
                })

            return avg_results

        #   5.6.1 전체 데이터셋 사전 준비 (벡터화 또는 데이터 인덱싱 개선)
        df_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].copy().drop_duplicates().reset_index(drop=True)
        df_AllWeek_array = df_AllWeek[TIME_WEEK_COLUMN].values  # numpy array로 전환
        df_AllWeek_index = {week: idx for idx, week in enumerate(df_AllWeek_array)}  # map으로 미리 계산된 인덱스

        #   5.6.2 그룹별 처리
        groupby_columns = [ITEM_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TRANS_MODE_COLUMN]
        df_eoh_w_grouped = df_eoh_w.groupby(groupby_columns)

        #   5.6.3 순차적으로 처리하여 계산
        results = []
        for _, group in df_eoh_w_grouped:
            group_results = calculate_avg(group)
            results.extend(group_results)  # 결과를 리스트에 추가

        #   5.6.4 결과 데이터프레임으로 변환
        df_eoh_w_results = pd.DataFrame(results)

        int_columns = [EOH_W_AVG_COLUMN, EOH_NOH_W_AVG_COLUMN, INV_W_AVG_COLUMN, INV_NOH_W_AVG_COLUMN]
        for col in int_columns:
            df_eoh_w_results[col] = df_eoh_w_results[col].fillna(0).astype(float)

        df_eoh_w_results.rename(columns={
            EOH_W_AVG_COLUMN: LCM_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN,
            EOH_NOH_W_AVG_COLUMN: LCM_PSI_PLAN_EOH_NOH_W_COLUMN,
            INV_W_AVG_COLUMN: LCM_PSI_PLAN_INV_W_COLUMN,
            INV_NOH_W_AVG_COLUMN: LCM_PSI_PLAN_INV_NOH_W_COLUMN,
        }, inplace=True)
        print_df(df_eoh_w_results, 'STEP4 by 5.6.4 ____ df_eoh_w_results .... final')

        #   5.6.7
        df_eoh_w_results = pd.merge(df_LCMPSIPlan, df_eoh_w_results, how='left',
                                    on=[ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN,
                                        ITEM_COMPONENT_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_eoh_w_results, 'STEP4 by 5.6.7 ____ df_eoh_w_results .... merge')

        int_columns = [
            LCM_PSI_PLAN_SET_SOP_COLUMN, LCM_PSI_PLAN_SET_SOP_SS_COLUMN, LCM_PSI_PLAN_SET_SOP_BLA_COLUMN, LCM_PSI_PLAN_GI_COLUMN,
            LCM_PSI_PLAN_ARRIVAL_COLUMN, LCM_PSI_PLAN_BOH_COLUMN, LCM_PSI_PLAN_SS_COLUMN, LCM_PSI_PLAN_SS_TAR_MIN_TIME_COLUMN,
            LCM_PSI_PLAN_SS_TAR_MIN_Q_COLUMN, LCM_PSI_PLAN_ARRIVAL_DETAIL_SS_COLUMN, LCM_PSI_PLAN_SHIP_DETAIL_COLUMN,
            LCM_PSI_PLAN_SET_SOP_SHORT_COLUMN, LCM_PSI_PLAN_ARRIVAL_DETAIL_COLUMN, LCM_PSI_PLAN_SHIP_COLUMN,
            LCM_PSI_PLAN_SHIP_SHORT_COLUMN, LCM_PSI_PLAN_NOH_LCM_COLUMN, LCM_PSI_PLAN_INTRANSIT_COLUMN,
            LCM_PSI_PLAN_PROD_DETAIL_SS_COLUMN, LCM_PSI_PLAN_PROD_COLUMN, LCM_PSI_PLAN_PROD_DETAIL_COLUMN, LCM_PSI_PLAN_PROD_SHORT_COLUMN,
            LCM_PSI_PLAN_AVG_8W_FLOW_QTY_COLUMN,
            LCM_PSI_PLAN_EOH_NOH_W_COLUMN, LCM_PSI_PLAN_INV_W_COLUMN, LCM_PSI_PLAN_INV_NOH_W_COLUMN
        ]
        for col in int_columns:
            df_eoh_w_results[col] = df_eoh_w_results[col].fillna(0).astype(int)

        # 6 df_in_OnhandMtrlTTL merge
        df_eoh_w_results = pd.merge(df_eoh_w_results, df_in_OnhandMtrlTTL, how='left',
                                     left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN],
                                     right_on=[VERSION_NAME_COLUMN, ITEM_METERIAL_COLUMN, LOCATION_COLUMN])
        print_df(df_eoh_w_results, 'STEP4 by 6.1.1  ____ df_eoh_w_results .... merge[df_eoh_w_results, df_in_OnhandMtrlTTL]')

        df_eoh_w_results.rename(columns={
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            ITEM_METERIAL_COLUMN+'_x': ITEM_METERIAL_COLUMN,
            ONHAND_MTRL_STATUS_UNAVAIL_TTL_COLUMN: LCM_PSI_PLAN_BLOCK_ONHAND_COLUMN,
        }, inplace=True)

        df_eoh_w_results.drop(columns=[
            LOCATION_COLUMN+'_y', ITEM_METERIAL_COLUMN+'_y',
        ], inplace=True)
        print_df(df_eoh_w_results, 'STEP4 by 6.1.2  ____ df_eoh_w_results .... final')

        df_eoh_w_results[LCM_PSI_PLAN_BLOCK_ONHAND_COLUMN] = df_eoh_w_results[LCM_PSI_PLAN_BLOCK_ONHAND_COLUMN].fillna(0).astype('Int64')
        df_eoh_w_results.loc[df_eoh_w_results[TIME_WEEK_COLUMN] > actual_start_week, LCM_PSI_PLAN_BLOCK_ONHAND_COLUMN] = 0


        df_out_LCMPSIPlan = rename_and_delete_df(df_eoh_w_results)
        df_out_LCMPSIPlan[VERSION_NAME_COLUMN] = paramOutVersion


        # 7 LCM_PSI_ACTUAL_SET 설정 ================================================================
        df_in_LCMPSIPlan.rename(columns={
            LCM_PSI_PLAN_SET_SOP_COLUMN: LCM_PSI_ACTUAL_SET_SOP_COLUMN,
            LCM_PSI_PLAN_SET_SOP_SHORT_COLUMN: LCM_PSI_ACTUAL_SET_SOP_SHORT_COLUMN,
        }, inplace=True)
        df_out_LCMPSIActual = rename_and_delete_df(df_in_LCMPSIPlan)
        print_df(df_out_LCMPSIActual, 'STEP4 by 7.1.1 ____ df_out_LCMPSIActual .... final')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        dataframes = {
            'df_out_LCMPSIPlan': df_out_LCMPSIPlan,
            'df_out_LCMPSIActual': df_out_LCMPSIActual,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')

        step('=====> STEP5 End')
        
    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_LCMPSIPlan = pd.DataFrame(columns=df_LCMPSIPlan_columns)
        df_out_LCMPSIActual = pd.DataFrame(columns=df_LCMPSIActual_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_LCMPSIPlan = pd.DataFrame(columns=df_LCMPSIPlan_columns)
        df_out_LCMPSIActual = pd.DataFrame(columns=df_LCMPSIActual_columns)
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
