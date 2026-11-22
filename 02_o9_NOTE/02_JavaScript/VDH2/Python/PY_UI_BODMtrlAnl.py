"""

* 프로그램명
    -PY_UI_BODMtrlAnl

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.01.16 / ybest7.park (박병훈) / Create
- 2025.04.14 / jaemin.im (임재민) / category 수정
- 2025.04.15 / ybest7.park (박병훈) / log 수정 및
- 2025.10.15 / ybest7.park (박병훈) / Logic 수정 및 input query 수정 df_out_BODMtrlAnlChart 추가
- 2025.12.03 / ybest7.park (박병훈) / Logic 수정

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary
    -  df_in_BODACT = Select ([Version].[Version Name] * [Location].[Location] * [Sequence].[Sequence] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl PO Tracking_ETA], Measure.[Mtrl PO Tracking_ETD], Measure.[Mtrl PO Tracking_GR Date], Measure.[Mtrl PO Tracking_GR Qty], Measure.[Mtrl PO Tracking_Global Top Code],  Measure.[Mtrl PO Tracking_Port ATA Date], Measure.[Mtrl PO Tracking_Port ATD Date], Measure.[Mtrl PO Tracking_Port ATD Week], Measure.[Mtrl PO Tracking_Port ETA Date], Measure.[Mtrl PO Tracking_Shipping Method], Measure.[Mtrl PO Tracking_Trans ATA Date], Measure.[Mtrl PO Tracking_Trans ATD Date], Measure.[Mtrl PO Tracking_Trans Port],Measure.[Mtrl PO Tracking_Org Port], Measure.[Mtrl PO Tracking_Vendor],Measure.[Mtrl PO Tracking_Arrival Port], Measure.[Mtrl PO Tracking_PO No],Measure.[Dummy]}) on column where {(~isnull(Measure.[Mtrl PO Tracking_Port ATD Date]))};
    -  df_in_BODLIST = Select ([Version].[Version Name] * Time.Week.filter(#.Key <= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key > &CurrentWeek.element(0).LeadOffset(-53).Key) * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl W_Factory Out], Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Intransit LT], Measure.[BOD Item Mtrl W_Port To Port],Measure.[Dummy]}) on column;
    -  df_in_TMCAL =  select([Time].[Planning Month] * Time.Week.filter(#.Key <= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key > &CurrentWeek.element(0).LeadOffset(-53).Key) * [Time].[Day] * [Time].[Day of Week] );
    -  df_in_TimeWeek = select( [Time].[Week]* [Time].[Day]* [Time].[Day of Week] );
    -  df_in_SHIPMETHOD = Select ([Version].[Version Name] * [Shipping Method].[Shipping Method] ) on row, ({Measure.[Shipping Method Map_TP Mode]}) on column;
    -  df_in_GTCode = Select (&NSUIGlobalTopView);
* Output Table
    - df_out_BODMtrlAnl = Select ([Version].[Version Name].[CWV_MP] * [Time].[Planning Month] * [Location].[Location] * [Trans Ship].[Trans Ship] * [Category].[Category] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Port].[Port] * [Trans Mode].[Trans Mode] * [Shipper].[Shipper] * [To Port].[To Port] ) on row, ({Measure.[BOD Mtrl Anl_JIT Invo], Measure.[BOD Mtrl Anl_JIT Qty], Measure.[BOD Mtrl Anl_Late Invo], Measure.[BOD Mtrl Anl_Late Qty],  Measure.[BOD Mtrl Anl_Pre Invo],  Measure.[BOD Mtrl Anl_Pre Qty]}) on column;
    - df_out_BODMtrlAnlLT = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Planning Month] * [Trans Ship].[Trans Ship] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Port].[Port] * [Aggregate].[Aggregate] * [Trans Mode].[Trans Mode] * [Shipper].[Shipper] * [To Port].[To Port] ) on row, ({Measure.[BOD Mtrl Anl LT_Actual Factory Out_Avg],Measure.[BOD Mtrl Anl LT_Actual Factory Out_Max], Measure.[BOD Mtrl Anl LT_Actual Factory Out_Min], Measure.[BOD Mtrl Anl LT_Actual Factory Out_Mode],  Measure.[BOD Mtrl Anl LT_Actual GR_Avg],  Measure.[BOD Mtrl Anl LT_Actual GR_Max], Measure.[BOD Mtrl Anl LT_Actual GR_Min], Measure.[BOD Mtrl Anl LT_Actual GR_Mode],  Measure.[BOD Mtrl Anl LT_Actual To port_Avg],  Measure.[BOD Mtrl Anl LT_Actual To port_Max], Measure.[BOD Mtrl Anl LT_Actual To port_Min], Measure.[BOD Mtrl Anl LT_Actual To port_Mode], Measure.[BOD Mtrl Anl LT_Plan Factory Out_Avg],Measure.[BOD Mtrl Anl LT_Plan Factory Out_Max], Measure.[BOD Mtrl Anl LT_Plan Factory Out_Min],Measure.[BOD Mtrl Anl LT_Plan Factory Out_Mode], Measure.[BOD Mtrl Anl LT_Plan GR_Avg], Measure.[BOD Mtrl Anl LT_Plan GR_Max],Measure.[BOD Mtrl Anl LT_Plan GR_Min], Measure.[BOD Mtrl Anl LT_Plan GR_Mode],Measure.[BOD Mtrl Anl LT_Plan To port_Avg],Measure.[BOD Mtrl Anl LT_Plan To port_Max], Measure.[BOD Mtrl Anl LT_Plan To port_Min], Measure.[BOD Mtrl Anl LT_Plan To port_Mode],Measure.[BOD Mtrl Anl LT_Plan Intransit LT_VSL],Measure.[BOD Mtrl Anl LT_Actual Intransit LT_VSL]}) on column ;
    - df_out_BODMtrlAnlChart = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Sub Location].[Sub Location] * [Seq1].[Seq1] ) on row, ({Measure.[BOD Mtrl Anl Chart_Invo], Measure.[BOD Mtrl Anl Chart_Plan], Measure.[BOD Mtrl Anl Chart_Qty]}) on column;
* 테스트 스크립트
    EXEC plugin instance [PY_UI_BODMtrlAnl] for measures {[BOD Mtrl Anl_JIT Invo]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (ParamOutVersion, "CWV_MP")};

* 데이터 삭제
    - DELETE DATA FOR MODEL [BOD Mtrl Anl LT] where {Version.[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [BOD Mtrl Anl] where {Version.[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [BOD Mtrl Anl Chart] where {Version.[Version Name].[CWV_MP]};

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
str_instance = 'PY_UI_BODMtrlAnl'
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


def print_df(df, df_name, _localFlag=True):
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
            df_in_BODLIST    = read_csv_file('df_in_BODLIST')
            df_in_BODACT     = read_csv_file('df_in_BODACT')
            df_in_TMCAL      = read_csv_file('df_in_TMCAL')
            df_in_SHIPMETHOD = read_csv_file('df_in_SHIPMETHOD')
            df_in_TimeWeek = read_csv_file('df_in_TimeWeek')
            df_in_GTCode     = read_csv_file('df_in_GTCode')


        dataframes = {
            'df_in_BODLIST':              df_in_BODLIST,
            'df_in_BODACT':               df_in_BODACT,
            'df_in_TMCAL':                df_in_TMCAL,
            'df_in_SHIPMETHOD':           df_in_SHIPMETHOD,
            'df_in_TimeWeek':             df_in_TimeWeek,
            'df_in_GTCode':               df_in_GTCode
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1 End')
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2 Start : DataFrame Column 변수 처리')

        Version_Name_COLUMN = 'Version.[Version Name]'
        Time_Week_COLUMN = 'Time.[Week]'
        # Time_PlanningMonthKey_COLUMN = 'Time.[PlanningMonthKey]'
        Time_Planning_Month_COLUMN = 'Time.[Planning Month]'
        # Time_DayKey_COLUMN = 'Time.[DayKey]'
        Time_Day_COLUM = 'Time.[Day]'
        # Time_DayofWeekKey_COLUM = 'Time.[DayofWeekKey]'
        Time_Day_of_Week_COLUMN = 'Time.[Day of Week]'
        Time_Month_COLUMN = 'Time.[Month]'
        Location_COLUMN = 'Location.[Location]'
        Item_Material_COLUMN = 'Item Material.[Item Material]'
        Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
        Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
        Trans_Ship_COLUMN = 'Trans Ship.[Trans Ship]'
        Sequence_COLUMN = 'Sequence.[Sequence]'
        Category_COLUMN = 'Category.[Category]'
        Port_COLUMN = 'Port.[Port]'
        Shipper_CLOUMN = 'Shipper.[Shipper]'
        To_Port_COLUMN = 'To Port.[To Port]'
        Aggregate_COLUMN = 'Aggregate.[Aggregate]'
        Seq1_COLUMN = 'Seq1.[Seq1]'
        SHIPPING_METHOD_COLUMN = 'Shipping Method.[Shipping Method]'
        SHIPPING_TP_Mode_COLUMN = 'Shipping Method Map_TP Mode'
        Global_Top_GT_Code_COLUMN = 'Global Top.[GT Code]'

        BOD_Item_Mtrl_W_Factory_Out = 'BOD Item Mtrl W_Factory Out'
        BOD_Item_Mtrl_W_GR_LT = 'BOD Item Mtrl W_GR LT'
        BOD_Item_Mtrl_W_Intransit_LT = 'BOD Item Mtrl W_Intransit LT'
        BOD_Item_Mtrl_W_Port_To_Port = 'BOD Item Mtrl W_Port To Port'

        Mtrl_PO_Tracking_Arrival_Port = 'Mtrl PO Tracking_Arrival Port'
        Mtrl_PO_Tracking_ETA = 'Mtrl PO Tracking_ETA'
        Mtrl_PO_Tracking_ETD = 'Mtrl PO Tracking_ETD'
        Mtrl_PO_Tracking_GR_Date = 'Mtrl PO Tracking_GR Date'
        Mtrl_PO_Tracking_GR_Qty = 'Mtrl PO Tracking_GR Qty'
        Mtrl_PO_Tracking_Global_Top_Code = 'Mtrl PO Tracking_Global Top Code'
        Mtrl_PO_Tracking_Org_Port = 'Mtrl PO Tracking_Org Port'
        Mtrl_PO_Tracking_PO_No = 'Mtrl PO Tracking_PO No'
        Mtrl_PO_Tracking_Port_ATA_Date = 'Mtrl PO Tracking_Port ATA Date'
        Mtrl_PO_Tracking_Port_ATD_Date = 'Mtrl PO Tracking_Port ATD Date'
        Mtrl_PO_Tracking_Port_ETA_Date = 'Mtrl PO Tracking_Port ETA Date'
        Mtrl_PO_Tracking_Shipping_Method = 'Mtrl PO Tracking_Shipping Method'
        Mtrl_PO_Tracking_Trans_ATA_Date = 'Mtrl PO Tracking_Trans ATA Date'
        Mtrl_PO_Tracking_Trans_ATD_Date = 'Mtrl PO Tracking_Trans ATD Date'
        Mtrl_PO_Tracking_Trans_Port = 'Mtrl PO Tracking_Trans Port'
        Mtrl_PO_Tracking_Vendor = 'Mtrl PO Tracking_Vendor'

        BOD_Mtrl_Anl_JIT_Invo = 'BOD Mtrl Anl_JIT Invo'
        BOD_Mtrl_Anl_JIT_Qty = 'BOD Mtrl Anl_JIT Qty'

        BOD_Mtrl_Anl_Late_Invo = 'BOD Mtrl Anl_Late Invo'
        BOD_Mtrl_Anl_Late_Qty = 'BOD Mtrl Anl_Late Qty'

        BOD_Mtrl_Anl_Pre_Invo = 'BOD Mtrl Anl_Pre Invo'
        BOD_Mtrl_Anl_Pre_Qty = 'BOD Mtrl Anl_Pre Qty'

        BOD_Mtrl_Anl_Total_Invo = 'BOD Mtrl Anl_Total Invo'
        BOD_Mtrl_Anl_Total_Qty = 'BOD Mtrl Anl_Total Qty'

        BOD_Mtrl_Anl_LT_Actual_Factory_Out_Avg = 'BOD Mtrl Anl LT_Actual Factory Out_Avg'
        BOD_Mtrl_Anl_LT_Actual_Factory_Out_Max = 'BOD Mtrl Anl LT_Actual Factory Out_Max'
        BOD_Mtrl_Anl_LT_Actual_Factory_Out_Min = 'BOD Mtrl Anl LT_Actual Factory Out_Min'
        BOD_Mtrl_Anl_LT_Actual_Factory_Out_Mode = 'BOD Mtrl Anl LT_Actual Factory Out_Mode'

        BOD_Mtrl_Anl_LT_Actual_GR_Avg = 'BOD Mtrl Anl LT_Actual GR_Avg'
        BOD_Mtrl_Anl_LT_Actual_GR_Max = 'BOD Mtrl Anl LT_Actual GR_Max'
        BOD_Mtrl_Anl_LT_Actual_GR_Min = 'BOD Mtrl Anl LT_Actual GR_Min'
        BOD_Mtrl_Anl_LT_Actual_GR_Mode = 'BOD Mtrl Anl LT_Actual GR_Mode'

        BOD_Mtrl_Anl_LT_Actual_To_port_Avg = 'BOD Mtrl Anl LT_Actual To port_Avg'
        BOD_Mtrl_Anl_LT_Actual_To_port_Max = 'BOD Mtrl Anl LT_Actual To port_Max'
        BOD_Mtrl_Anl_LT_Actual_To_port_Min = 'BOD Mtrl Anl LT_Actual To port_Min'
        BOD_Mtrl_Anl_LT_Actual_To_port_Mode = 'BOD Mtrl Anl LT_Actual To port_Mode'

        BOD_Mtrl_Anl_LT_Actual_Total_Avg = 'BOD Mtrl Anl LT_Actual Total_Avg'
        BOD_Mtrl_Anl_LT_Actual_Total_Max = 'BOD Mtrl Anl LT_Actual Total_Max'
        BOD_Mtrl_Anl_LT_Actual_Total_Min = 'BOD Mtrl Anl LT_Actual Total_Min'
        BOD_Mtrl_Anl_LT_Actual_Total_Mode = 'BOD Mtrl Anl LT_Actual Total_Mode'

        BOD_Mtrl_Anl_LT_Gap_GR_Avg = 'BOD Mtrl Anl LT_Gap GR_Avg'
        BOD_Mtrl_Anl_LT_Gap_GR_Max = 'BOD Mtrl Anl LT_Gap GR_Max'
        BOD_Mtrl_Anl_LT_Gap_GR_Min = 'BOD Mtrl Anl LT_Gap GR_Min'
        BOD_Mtrl_Anl_LT_Gap_GR_Mode = 'BOD Mtrl Anl LT_Gap GR_Mode'

        BOD_Mtrl_Anl_LT_Plan_Factory_Out_Avg = 'BOD Mtrl Anl LT_Plan Factory Out_Avg'
        BOD_Mtrl_Anl_LT_Plan_Factory_Out_Max = 'BOD Mtrl Anl LT_Plan Factory Out_Max'
        BOD_Mtrl_Anl_LT_Plan_Factory_Out_Min = 'BOD Mtrl Anl LT_Plan Factory Out_Min'
        BOD_Mtrl_Anl_LT_Plan_Factory_Out_Mode = 'BOD Mtrl Anl LT_Plan Factory Out_Mode'

        BOD_Mtrl_Anl_LT_Plan_GR_Avg = 'BOD Mtrl Anl LT_Plan GR_Avg'
        BOD_Mtrl_Anl_LT_Plan_GR_Max = 'BOD Mtrl Anl LT_Plan GR_Max'
        BOD_Mtrl_Anl_LT_Plan_GR_Min = 'BOD Mtrl Anl LT_Plan GR_Min'
        BOD_Mtrl_Anl_LT_Plan_GR_Mode = 'BOD Mtrl Anl LT_Plan GR_Mode'

        BOD_Mtrl_Anl_LT_Plan_To_port_Avg = 'BOD Mtrl Anl LT_Plan To port_Avg'
        BOD_Mtrl_Anl_LT_Plan_To_port_Max = 'BOD Mtrl Anl LT_Plan To port_Max'
        BOD_Mtrl_Anl_LT_Plan_To_port_Min = 'BOD Mtrl Anl LT_Plan To port_Min'
        BOD_Mtrl_Anl_LT_Plan_To_port_Mode = 'BOD Mtrl Anl LT_Plan To port_Mode'

        BOD_Mtrl_Anl_LT_Plan_Intransit_LT_VSL = 'BOD Mtrl Anl LT_Plan Intransit LT_VSL'
        BOD_Mtrl_Anl_LT_Actual_Intransit_LT_VSL = 'BOD Mtrl Anl LT_Actual Intransit LT_VSL'

        BOD_Mtrl_Anl_LT_Actual_Intransit_LT_VSL_Avg = 'BOD Mtrl Anl LT_Actual Intransit LT_VSL_Avg'
        BOD_Mtrl_Anl_LT_Actual_Intransit_LT_VSL_Max = 'BOD Mtrl Anl LT_Actual Intransit LT_VSL_Max'
        BOD_Mtrl_Anl_LT_Actual_Intransit_LT_VSL_Min = 'BOD Mtrl Anl LT_Actual Intransit LT_VSL_Min'

        BOD_Mtrl_Anl_Chart_Invo = 'BOD Mtrl Anl Chart_Invo'
        BOD_Mtrl_Anl_Chart_Plan = 'BOD Mtrl Anl Chart_Plan'
        BOD_Mtrl_Anl_Chart_Qty = 'BOD Mtrl Anl Chart_Qty'

        Port_LT = 'Port_LT'
        GR_LT = 'GR_LT'
        Port_ETA = 'Port_ETA'
        GR_ETA = 'GR_ETA'
        PGR_ETA = 'PGR_ETA'
        GR_ETAWEEK = 'GR_ETAWEEK'
        PGR_ETAWEEK = 'PGR_ETAWEEK'
        Port_ETAWEEK = 'Port_ETAWEEK'
        Port_ATAWEEK = 'Port_ATAWEEK'
        Port_ATDWEEK = 'Port_ATDWEEK'
        Factory_ATDWEEK = "Factory_ATDWEEK"
        GR_WEEK = 'GR_WEEK'
        GR_DayofWeek = 'GR_DayofWeek'

        step('=====> STEP 2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP 3 Start : input data machining')

        ############################################## 2025-12-03 GT Code 필터 추가 #####################################
        gt_code_list = df_in_GTCode[Global_Top_GT_Code_COLUMN].unique().tolist()
        df_in_BODACT = df_in_BODACT[df_in_BODACT[Mtrl_PO_Tracking_Global_Top_Code].isin(gt_code_list)]
        print_df(df_in_BODACT, 'df_in_BODACT 데이터 확인 0')
        ############################################### 2025-10-17 logic 추가 ##########################################
        df_in_BODACT = df_in_BODACT.copy()
        # df_in_SHIPMETHOD 의 Shipping Method 를 통해 변화하기 위한 TP_MODE 컬럼 생성
        df_in_BODACT['TP_MODE'] = df_in_BODACT[Mtrl_PO_Tracking_Shipping_Method].map(
            df_in_SHIPMETHOD.set_index(SHIPPING_METHOD_COLUMN)[SHIPPING_TP_Mode_COLUMN])

        # Mtrl_PO_Tracking_Shipping_Method 의 값을 df_in_SHIPMETHOD 의 Shipping Method 치환
        df_in_BODACT[Mtrl_PO_Tracking_Shipping_Method] = np.where(df_in_BODACT['TP_MODE'].isna(),
                                                                  df_in_BODACT[Mtrl_PO_Tracking_Shipping_Method],
                                                                  df_in_BODACT['TP_MODE'])

        print_df(df_in_BODACT, 'df_in_BODACT 데이터 확인')
        # 불필요한 'TP_MODE' columns 삭제
        df_in_BODACT.drop(columns='TP_MODE', axis=1, inplace=True)
        ############################################### 2025-10-17 logic 추가 ##########################################

        # df_in_BODLIST 와 merge 를 위해  Columns 변경 전 변수로 지정
        renames_col = {Mtrl_PO_Tracking_Shipping_Method: Trans_Mode_COLUMN,
                       Location_COLUMN: Sub_Location_COLUMN,
                       Mtrl_PO_Tracking_Global_Top_Code: Location_COLUMN}

        # df_in_BODACT 컬럼명 변경
        df_in_BODACT = df_in_BODACT.rename(columns=renames_col)


        # Data columns 을 위한 설정 및 날짜 형태로 변환
        Date_col_list = [Mtrl_PO_Tracking_Port_ATA_Date, Mtrl_PO_Tracking_Port_ATD_Date,
                         Mtrl_PO_Tracking_GR_Date, Mtrl_PO_Tracking_Port_ETA_Date, Mtrl_PO_Tracking_ETA,
                         Mtrl_PO_Tracking_Trans_ATA_Date, Mtrl_PO_Tracking_Trans_ATD_Date, Mtrl_PO_Tracking_ETD]

        # date_type_cols 날짜 타입으로 데이터 타입 변경
        for col in Date_col_list:
            s = df_in_BODACT[col].astype(str)
            head = s.str.partition(' ')[0]
            df_in_BODACT[col] = pd.to_datetime(head, errors='coerce')

        # Mon Day 인 week 설정
        df_in_TMCAL_Mon = df_in_TimeWeek[df_in_TimeWeek[Time_Day_of_Week_COLUMN] == 'MON'].copy()
        df_in_TMCAL_Mon = df_in_TMCAL_Mon.copy()
        df_in_TMCAL_Mon[Time_Week_COLUMN] = df_in_TMCAL_Mon[Time_Week_COLUMN].astype(str)
        df_in_BODLIST[Time_Week_COLUMN] = df_in_BODLIST[Time_Week_COLUMN].astype(str)

        df_in_BODLIST = df_in_BODLIST.merge(df_in_TMCAL_Mon[[Time_Week_COLUMN, Time_Day_COLUM]],
                                            on=Time_Week_COLUMN,
                                            how='left')

        df_in_BODLIST['end_date'] = pd.to_datetime(df_in_BODLIST[Time_Day_COLUM]) - pd.to_timedelta(
            df_in_BODLIST[BOD_Item_Mtrl_W_Intransit_LT], unit='D')

        df_in_BODLIST = df_in_BODLIST.drop(columns=[Time_Day_COLUM, Time_Week_COLUMN], axis=1)
        df_in_BODLIST = df_in_BODLIST.rename(columns={'end_date': Time_Day_COLUM})

        df_in_BODLIST[Time_Day_COLUM] = pd.to_datetime(df_in_BODLIST[Time_Day_COLUM], errors='coerce')
        df_in_TimeWeek[Time_Day_COLUM] = pd.to_datetime(df_in_TimeWeek[Time_Day_COLUM], errors='coerce')
        #
        df_in_BODLIST = df_in_BODLIST.merge(
            df_in_TimeWeek[[Time_Day_COLUM, Time_Week_COLUMN]],
            on=Time_Day_COLUM, how='left')

        print_df(df_in_BODLIST, 'df_in_BODLIST 데이터 확인')

        # Mtrl PO Tracking_GR Qty 0 이 아닌것 필터링 2025-12-11 추가
        df_in_BODACT[Mtrl_PO_Tracking_GR_Qty] = pd.to_numeric(df_in_BODACT[Mtrl_PO_Tracking_GR_Qty])
        df_in_BODACT = df_in_BODACT[df_in_BODACT[Mtrl_PO_Tracking_GR_Qty]>0]


        df_in_BODACT[Time_Week_COLUMN] = df_in_BODACT[Mtrl_PO_Tracking_GR_Date].map(
            df_in_TimeWeek.set_index(Time_Day_COLUM)[Time_Week_COLUMN])

        # print_df(df_in_BODACT , 'df_in_BODACT-----확인')


        # df_in_BODACT 와 df_in_BODLIST merge를 위한 key 설정
        merge_key_cols = df_in_BODACT.columns.intersection(df_in_BODLIST.columns).to_list()
        # note(f"=============merge_key_cols : {merge_key_cols}")
        # merge_key_cols 에서 "Dummy" 제거
        merge_key_cols.remove("Dummy")

        df_in_BODACT[Time_Week_COLUMN] = df_in_BODACT[Time_Week_COLUMN].astype(str)
        df_in_BODLIST[Time_Week_COLUMN] = df_in_BODLIST[Time_Week_COLUMN].astype(str)

        # df_in_BODACT_temp 과 df_in_BODLIST 1차 merge
        df_in_BODACT_temp = df_in_BODACT.drop(columns='Dummy').merge(
            df_in_BODLIST.drop(columns='Dummy'),
            on=merge_key_cols,
            how='left')

        print_df(df_in_BODACT_temp, 'df_in_BODACT_temp_merge_data 확인')

        # 'BOD Item Mtrl W_Factory Out','BOD Item Mtrl W_GR LT','BOD Item Mtrl W_Intransit LT','BOD Item Mtrl W_Port To Port' 0으로 채우기
        fill_zero_col = [col for col in df_in_BODACT_temp.columns if "BOD Item" in col]
        df_in_BODACT_temp.loc[:, fill_zero_col] = df_in_BODACT_temp[fill_zero_col].fillna(0)

        # 기준이 되는 Week를 찾기 위한 Key 설정 - Factory out 주차로 반영 필요
        df_in_BODACT_temp["Key_Day"] = df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATA_Date] - pd.to_timedelta(
            df_in_BODACT_temp[BOD_Item_Mtrl_W_Factory_Out], unit='D')

        # df_in_BODACT_temp["Key_Day"] = df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATA_Date]

        df_in_BODACT_temp = df_in_BODACT_temp.drop_duplicates()

        print_df(df_in_BODACT_temp, 'df_in_BODACT_temp_주차 변환 확인_주차변환 전')

        # merge를 위한 Time_Day_COLUM 타입 변경
        df_in_TMCAL[Time_Day_COLUM] = pd.to_datetime(df_in_TMCAL[Time_Day_COLUM], errors='coerce')

        # df_in_TMCAL 주차를 Key Day 기준으로 mapping
        df_in_BODACT_temp[Time_Week_COLUMN] = df_in_BODACT_temp["Key_Day"].map(
            df_in_TMCAL.set_index(Time_Day_COLUM)[Time_Week_COLUMN])

        print_df(df_in_BODACT_temp, 'df_in_BODACT_temp_주차 변환 확인')


        # Mtrl_PO_Tracking_Port_ATD_Date - BOD_Item_Mtrl_W_Factory_Out df_in_TMCAL 범위에 들어오지 않는 대상은 제외
        df_in_BODACT_temp = df_in_BODACT_temp[df_in_BODACT_temp[Time_Week_COLUMN].notna()]

        # Time_Week_COLUMN 타입 변경
        df_in_BODACT_temp[Time_Week_COLUMN] = df_in_BODACT_temp[Time_Week_COLUMN].astype(int).astype(str)

        # df_in_BODLIST 와 2차 merge 를 위한 리스트 설정
        merge_key_cols.append(Time_Week_COLUMN)

        # df_in_BODLIST의 Time_Week_COLUMN 데이터 타입 변경 (Int → Str)
        df_in_BODLIST[Time_Week_COLUMN] = df_in_BODLIST[Time_Week_COLUMN].astype(str)

        # # df_in_BODLIST 와 2차 merge
        df_in_BODACT_temp = df_in_BODACT_temp.drop(columns=fill_zero_col).merge(df_in_BODLIST.drop(columns="Dummy"),
                                                                                on=merge_key_cols,
                                                                                how='left')

        # 'BOD Item Mtrl W_Factory Out','BOD Item Mtrl W_GR LT','BOD Item Mtrl W_Intransit LT','BOD Item Mtrl W_Port To Port' 0으로 채우기
        df_in_BODACT_temp[fill_zero_col] = df_in_BODACT_temp[fill_zero_col].fillna(0).astype('int64')

        # L/T 를 계산을 위한 로직 진행
        df_in_BODACT_temp[Port_LT] = (df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATA_Date] - df_in_BODACT_temp[
            Mtrl_PO_Tracking_Port_ATD_Date]).dt.days
        df_in_BODACT_temp[Port_LT] = df_in_BODACT_temp[Port_LT].fillna(0).astype('int64')
        df_in_BODACT_temp[GR_LT] = (
                df_in_BODACT_temp[Mtrl_PO_Tracking_GR_Date] - df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATA_Date]).dt.days
        df_in_BODACT_temp[GR_LT] = df_in_BODACT_temp[GR_LT].fillna(0).astype('int64')

        # factory to GR  ( ATD_DATE + Intransit LT - Factory Out LT)
        df_in_BODACT_temp[GR_ETA] = df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATD_Date] + pd.to_timedelta(
            df_in_BODACT_temp[BOD_Item_Mtrl_W_Intransit_LT] - df_in_BODACT_temp[BOD_Item_Mtrl_W_Factory_Out], unit='D')
        # port to port  (ATD_Date + GR_LT)
        df_in_BODACT_temp[Port_ETA] = df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATD_Date] + pd.to_timedelta(
            (df_in_BODACT_temp[BOD_Item_Mtrl_W_Port_To_Port]), unit='D')
        # 도작 port to GR( ATA_Date - GR_LT)
        df_in_BODACT_temp[PGR_ETA] = df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATA_Date] + pd.to_timedelta(
            df_in_BODACT_temp[BOD_Item_Mtrl_W_GR_LT], unit='D')

        print_df(df_in_BODACT_temp, 'df_in_BODACT_temp 데이터 타입 확인 중복 제거 전')
        # df_in_BODACT_temp = df_in_BODACT_temp.drop_duplicates(keep='first')
        # df_in_BODACT_temp = df_in_BODACT_temp.drop_duplicates(subset=merge_key_cols)
        print_df(df_in_BODACT_temp, 'df_in_BODACT_temp 데이터 타입 확인')
        print_df(df_in_TMCAL, 'df_in_TMCAL  주차 변환 확인')

        # Data 형태로 변경
        # Data 변경 필요한 리스티
        date_cols = [GR_ETA, PGR_ETA, Port_ETA, Mtrl_PO_Tracking_Port_ATA_Date,Mtrl_PO_Tracking_Port_ATD_Date,
                     "Key_Day", Mtrl_PO_Tracking_GR_Date,Mtrl_PO_Tracking_GR_Date]

        for c in date_cols:
            df_in_BODACT_temp[c] = pd.to_datetime(df_in_BODACT_temp[c] ,errors='coerce').dt.strftime('%Y-%m-%d')

        df_in_TMCAL[Time_Day_COLUM] = df_in_TMCAL[Time_Day_COLUM].dt.strftime('%Y-%m-%d')

        # df_in_BODACT_temp[date_cols] = df_in_BODACT_temp[date_cols].apply(lambda s: s.dt.date)

        lookup = df_in_TMCAL.set_index(Time_Day_COLUM)[Time_Week_COLUMN]

        # GR_ETAWEEK 값 전처리
        df_in_BODACT_temp[GR_ETAWEEK] = df_in_BODACT_temp[GR_ETA].map(lookup)

        # print_df(df_in_BODACT_temp[df_in_BODACT_temp[GR_ETAWEEK].isna()][[GR_ETA,Time_Week_COLUMN]], "데이터 확인 GR_ETAWEEK ")

        # day_list = df_in_BODACT_temp[df_in_BODACT_temp[GR_ETAWEEK].isna()][GR_ETA].unique()
        #
        # print_df(df_in_TMCAL[df_in_TMCAL[Time_Day_COLUM].isin(day_list)], ' 데이터 확인 여부 확인.......')

        # PGR_ETAWEEK 값 전처리
        df_in_BODACT_temp[PGR_ETAWEEK] = df_in_BODACT_temp[PGR_ETA].map(lookup)
        # Port_ETAWEEK 값 전처리
        df_in_BODACT_temp[Port_ETAWEEK] = df_in_BODACT_temp[Port_ETA].map(lookup)
        # Port_ATAWEEK 값 전처리
        df_in_BODACT_temp[Port_ATAWEEK] = df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATA_Date].map(
            lookup)
        # Port_ATD_Week 값 전처리(주차)
        df_in_BODACT_temp[Port_ATDWEEK] = df_in_BODACT_temp[Mtrl_PO_Tracking_Port_ATD_Date].map(
            lookup)
        # Factory out_Week 값 전처리(주차)
        df_in_BODACT_temp[Factory_ATDWEEK] = df_in_BODACT_temp["Key_Day"].map(
            lookup)
        # GR_Week 값 전처리
        df_in_BODACT_temp[GR_WEEK] = df_in_BODACT_temp[Mtrl_PO_Tracking_GR_Date].map(
           lookup)
        # GR_DayofWeek 값 전처리 (Mtrl_PO_Tracking_GR_Date 기준)
        df_in_BODACT_temp[GR_DayofWeek] = df_in_BODACT_temp[Mtrl_PO_Tracking_GR_Date].map(
            df_in_TMCAL.set_index(Time_Day_COLUM)[Time_Day_of_Week_COLUMN])
        # Planning Month 설정을 위한 merge (GR_ETA 기준)
        df_in_BODACT_temp[Time_Planning_Month_COLUMN] = df_in_BODACT_temp[Mtrl_PO_Tracking_GR_Date].map(
            df_in_TMCAL.set_index(Time_Day_COLUM)[Time_Planning_Month_COLUMN])

        # df_in_BODACT_temp[Time_Planning_Month_COLUMN] = df_in_BODACT_temp['Time_Planning_Month_COLUMN_Week'].map(df_in_TMCAL.set_index(Time_Week_COLUMN)[Time_Planning_Month_COLUMN])

        # print_df(df_in_BODACT_temp[[Time_Planning_Month_COLUMN, Time_Week_COLUMN]], "데이터 확인 구간")

        # 데이터 형 변환을 위한 컬럼 설정
        week_zero_cols = [GR_ETAWEEK, PGR_ETAWEEK, Port_ETAWEEK, Port_ATAWEEK, GR_WEEK]
        #
        # print_df(df_in_BODACT_temp[week_zero_cols],
        #          "df_in_BODACT_temp 확인 전 데이터 확인 NA 채우기 전 ")
        # 벡터 연산을 통해 형태 변환
        df_in_BODACT_temp[week_zero_cols] = df_in_BODACT_temp[week_zero_cols].fillna(0).astype(
            'int64')  # na 값 0으로 채우고 숫자 형으로 변환
        df_in_BODACT_temp[Time_Planning_Month_COLUMN] = df_in_BODACT_temp[Time_Planning_Month_COLUMN].fillna(0).astype(
            'int64')  # na 값 0으로 채우고 숫자 형으로 변환

        # print_df(df_in_BODACT_temp, "df_in_BODACT_temp 확인 전 데이터 확인")

        # Week 값이 0인 값 filter_col 이 0인 경우 필터 (week_zero_cols 기준  : GR_ETAWEEK,PGR_ETAWEEK,Port_ETAWEEK,Port_ATAWEEK,GR_WEEK)
        df_in_BODACT_temp = df_in_BODACT_temp[~(df_in_BODACT_temp[week_zero_cols] == 0).any(axis=1)]

        # df_in_BODACT_temp = df_in_BODACT_temp.drop_duplicates(keep='first')

        print_df(df_in_BODACT_temp, "df_in_BODACT_temp 확인")

        step('=====> STEP 3 End')
        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')

        # output 데이터 프레임 설정
        df_out_BODMtrlAnl_temp = df_in_BODACT_temp.copy()
        # columns 명 변경
        # df_out_BODMtrlAnl_temp[[Location_COLUMN, Sub_Location_COLUMN]] = df_out_BODMtrlAnl_temp[
        #     [Sub_Location_COLUMN, Location_COLUMN]].to_numpy()
        df_out_BODMtrlAnl_temp[Trans_Ship_COLUMN] = np.where(df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_Trans_Port].isna(),
                                                             "Direct", 'T/S') #2025-12-02 기준 컬럼 변경
        # df_out_BODMtrlAnl_temp[Trans_Mode_COLUMN] = df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_Shipping_Method]
        df_out_BODMtrlAnl_temp[Port_COLUMN] = df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_Org_Port]
        df_out_BODMtrlAnl_temp[Shipper_CLOUMN] = df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_Vendor]
        df_out_BODMtrlAnl_temp[To_Port_COLUMN] = df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_Arrival_Port]

        df_out_BODMtrlAnl_temp[Time_Planning_Month_COLUMN] = df_out_BODMtrlAnl_temp[Time_Planning_Month_COLUMN].astype(str)
        print_df(df_out_BODMtrlAnl_temp, 'df_out_BODMtrlAnl_temp')
        # note(f'=====> Time_Planning_Month_COLUMN Value : {df_out_BODMtrlAnl_temp[Time_Planning_Month_COLUMN].unique()}')

        step('=====> STEP 4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')

        # PlanningMonthList 설정
        PlanningMonthList = list(df_in_TMCAL[Time_Planning_Month_COLUMN].unique()[:-1])
        PlanningMonthList.sort()

        # Type 변경
        df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_GR_Qty] = df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_GR_Qty].fillna(
            0).astype(int)

        # Groupby Colulms 설정
        Group_col = [Version_Name_COLUMN, Time_Planning_Month_COLUMN, Location_COLUMN, Category_COLUMN,
                     Trans_Ship_COLUMN,Item_Material_COLUMN, Sub_Location_COLUMN, Port_COLUMN, Trans_Mode_COLUMN,
                     Shipper_CLOUMN,To_Port_COLUMN]

        # Measuar 값 설정을 위한 반복문
        df_out_BODMtrlAnl_AnlJitQty = pd.DataFrame()
        df_out_BODMtrlAnl_AnlPreQty = pd.DataFrame()
        df_out_BODMtrlAnl_AnlLateQty = pd.DataFrame()
        for col in PlanningMonthList:
            col = str(col)
            # note(f'=====> Col Value : {col} , Col Type : {type(col)}')
            df_out_BODMtrlAnl_for = df_out_BODMtrlAnl_temp[df_out_BODMtrlAnl_temp[Time_Planning_Month_COLUMN] == col]
            # BOD_Mtrl_Anl_JIT_Qty  & BOD_Mtrl_Anl_JIT_Invo 값 설정
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[Port_ETAWEEK] == df_out_BODMtrlAnl_for[Port_ATAWEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_port[Category_COLUMN] = 'Port - Port'
            df_out_BODMtrlAnl_port[Category_COLUMN] = 'Mtrl_PORT-PORT'
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_port.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_JIT_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_JIT_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlJitQty = pd.concat([df_out_BODMtrlAnl_AnlJitQty, df_out_BODMtrlAnl_port], axis=0,
                                                    ignore_index=True)
            df_out_BODMtrlAnl_GRETA = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[GR_ETAWEEK] == df_out_BODMtrlAnl_for[GR_WEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_GRETA[Category_COLUMN] = "Factory - GR"
            df_out_BODMtrlAnl_GRETA[Category_COLUMN] = "Mtrl_FACTORYOUT-GR"
            df_out_BODMtrlAnl_GRETA = df_out_BODMtrlAnl_GRETA.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_JIT_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_JIT_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlJitQty = pd.concat([df_out_BODMtrlAnl_AnlJitQty, df_out_BODMtrlAnl_GRETA], axis=0,
                                                    ignore_index=True)
            df_out_BODMtrlAnl_PGR = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[PGR_ETAWEEK] == df_out_BODMtrlAnl_for[GR_WEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_PGR[Category_COLUMN] = "Port - GR"
            df_out_BODMtrlAnl_PGR[Category_COLUMN] = "Mtrl_PORT-GR"
            df_out_BODMtrlAnl_PGR = df_out_BODMtrlAnl_PGR.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_JIT_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_JIT_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))

            df_out_BODMtrlAnl_PGR = pd.concat([df_out_BODMtrlAnl_AnlJitQty, df_out_BODMtrlAnl_PGR], axis=0,
                                              ignore_index=True)
            # print_df(df_out_BODMtrlAnl_AnlJitQty, f'df_out_BODMtrlAnl_AnlJitQty {col}')

            # BOD Mtrl Anl_Pre_Qty & BOD_Mtrl_Anl_Pre_Invo 값 설정
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[Port_ETAWEEK] > df_out_BODMtrlAnl_for[Port_ATAWEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_port[Category_COLUMN] = 'Port - Port'
            df_out_BODMtrlAnl_port[Category_COLUMN] = 'Mtrl_PORT-PORT'
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_port.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_Pre_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_Pre_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlPreQty = pd.concat([df_out_BODMtrlAnl_AnlPreQty, df_out_BODMtrlAnl_port], axis=0,
                                                    ignore_index=True)
            df_out_BODMtrlAnl_GRETA = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[GR_ETAWEEK] > df_out_BODMtrlAnl_for[GR_WEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가 --> 리드 타임 별로 (복사 후 집계 추가 )
            # df_out_BODMtrlAnl_GRETA[Category_COLUMN] = "Factory - GR"
            df_out_BODMtrlAnl_GRETA[Category_COLUMN] = "Mtrl_FACTORYOUT-GR"
            df_out_BODMtrlAnl_GRETA = df_out_BODMtrlAnl_GRETA.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_Pre_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_Pre_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlPreQty = pd.concat([df_out_BODMtrlAnl_AnlPreQty, df_out_BODMtrlAnl_GRETA], axis=0,
                                                    ignore_index=True)
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[PGR_ETAWEEK] > df_out_BODMtrlAnl_for[GR_WEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_port[Category_COLUMN] = "Port - GR"
            df_out_BODMtrlAnl_port[Category_COLUMN] = "Mtrl_PORT-GR"
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_port.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_Pre_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_Pre_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlPreQty = pd.concat([df_out_BODMtrlAnl_AnlPreQty, df_out_BODMtrlAnl_port], axis=0,
                                                    ignore_index=True)

            # print_df(df_out_BODMtrlAnl_AnlPreQty, f'df_out_BODMtrlAnl_AnlPreQty {col}')

            # BOD Mtrl Anl_Late_Qty &  BOD_Mtrl_Anl_Late_Invo 값 설정
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[Port_ETAWEEK] < df_out_BODMtrlAnl_for[Port_ATAWEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_port[Category_COLUMN] = 'Port - Port'
            df_out_BODMtrlAnl_port[Category_COLUMN] = 'Mtrl_PORT-PORT'
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_port.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_Late_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_Late_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlLateQty = pd.concat([df_out_BODMtrlAnl_AnlLateQty, df_out_BODMtrlAnl_port], axis=0,
                                                     ignore_index=True)
            df_out_BODMtrlAnl_GRETA = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[GR_ETAWEEK] < df_out_BODMtrlAnl_for[GR_WEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_GRETA[Category_COLUMN] = "Factory - GR"
            df_out_BODMtrlAnl_GRETA[Category_COLUMN] = "Mtrl_FACTORYOUT-GR"
            df_out_BODMtrlAnl_GRETA = df_out_BODMtrlAnl_GRETA.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_Late_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_Late_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlLateQty = pd.concat([df_out_BODMtrlAnl_AnlLateQty, df_out_BODMtrlAnl_GRETA], axis=0,
                                                     ignore_index=True)
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_for[
                df_out_BODMtrlAnl_for[PGR_ETAWEEK] < df_out_BODMtrlAnl_for[GR_WEEK]].copy()
            # 250414 | jaemin.im | category 멤버로 추가
            # df_out_BODMtrlAnl_port[Category_COLUMN] = "Port - GR"
            df_out_BODMtrlAnl_port[Category_COLUMN] = "Mtrl_PORT-GR"
            df_out_BODMtrlAnl_port = df_out_BODMtrlAnl_port.groupby(Group_col, as_index=False).agg(
                BOD_Mtrl_Anl_Late_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
                BOD_Mtrl_Anl_Late_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))
            df_out_BODMtrlAnl_AnlLateQty = pd.concat([df_out_BODMtrlAnl_AnlLateQty, df_out_BODMtrlAnl_port], axis=0,
                                                     ignore_index=True)

        # planning Month 데이터 타입 변경
        df_out_BODMtrlAnl_AnlJitQty[Time_Planning_Month_COLUMN] = df_out_BODMtrlAnl_AnlJitQty[
            Time_Planning_Month_COLUMN].astype(str)
        df_out_BODMtrlAnl_AnlPreQty[Time_Planning_Month_COLUMN] = df_out_BODMtrlAnl_AnlPreQty[
            Time_Planning_Month_COLUMN].astype(str)
        df_out_BODMtrlAnl_AnlLateQty[Time_Planning_Month_COLUMN] = df_out_BODMtrlAnl_AnlLateQty[
            Time_Planning_Month_COLUMN].astype(str)

        print_df(df_out_BODMtrlAnl_AnlJitQty, 'df_out_BODMtrlAnl_AnlJitQty')
        print_df(df_out_BODMtrlAnl_AnlPreQty, 'df_out_BODMtrlAnl_AnlPreQty')
        print_df(df_out_BODMtrlAnl_AnlLateQty, 'df_out_BODMtrlAnl_AnlLateQty')

        step('=====> STEP 5 End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################
        step('=====> STEP 6 Start : input data machining')

        # Unique한 데이터 프레임 설정
        df_out_BODMtrlAnl_AnlJitQty_unique = df_out_BODMtrlAnl_AnlJitQty[Group_col]
        df_out_BODMtrlAnl_AnlPreQty_unique = df_out_BODMtrlAnl_AnlPreQty[Group_col]
        df_out_BODMtrlAnl_AnlLateQty_unique = df_out_BODMtrlAnl_AnlLateQty[Group_col]

        df_out_BODMtrlAnl = pd.concat([df_out_BODMtrlAnl_AnlJitQty_unique, df_out_BODMtrlAnl_AnlPreQty_unique,
                                       df_out_BODMtrlAnl_AnlLateQty_unique], axis=0, ignore_index=True)
        df_out_BODMtrlAnl = df_out_BODMtrlAnl.drop_duplicates()

        # df_out_BODMtrlAnl Frame 설정 (df_out_BODMtrlAnl_AnlJitQty, df_out_BODMtrlAnl_AnlPreQty, df_out_BODMtrlAnl_AnlLateQty merge)
        df_out_BODMtrlAnl = df_out_BODMtrlAnl.merge(df_out_BODMtrlAnl_AnlJitQty, on=Group_col, how='left')
        df_out_BODMtrlAnl = df_out_BODMtrlAnl.merge(df_out_BODMtrlAnl_AnlPreQty, on=Group_col, how='left')
        df_out_BODMtrlAnl = df_out_BODMtrlAnl.merge(df_out_BODMtrlAnl_AnlLateQty, on=Group_col, how='left')

        # df_out_BODMtrlAnl column 명 변경
        df_out_BODMtrlAnl = df_out_BODMtrlAnl.rename(columns={'BOD_Mtrl_Anl_JIT_Qty': BOD_Mtrl_Anl_JIT_Qty,
                                                              'BOD_Mtrl_Anl_JIT_Invo': BOD_Mtrl_Anl_JIT_Invo,
                                                              'BOD_Mtrl_Anl_Pre_Qty': BOD_Mtrl_Anl_Pre_Qty,
                                                              'BOD_Mtrl_Anl_Pre_Invo': BOD_Mtrl_Anl_Pre_Invo,
                                                              'BOD_Mtrl_Anl_Late_Qty': BOD_Mtrl_Anl_Late_Qty,
                                                              'BOD_Mtrl_Anl_Late_Invo': BOD_Mtrl_Anl_Late_Invo})
        # 데이터 프레임 순서 지정
        df_out_BODMtrlAnl = df_out_BODMtrlAnl[
            [Version_Name_COLUMN, Time_Planning_Month_COLUMN, Location_COLUMN, Trans_Ship_COLUMN, Category_COLUMN,
             Item_Material_COLUMN, Sub_Location_COLUMN, Port_COLUMN, Trans_Mode_COLUMN, Shipper_CLOUMN, To_Port_COLUMN,
             BOD_Mtrl_Anl_JIT_Qty, BOD_Mtrl_Anl_JIT_Invo, BOD_Mtrl_Anl_Pre_Qty, BOD_Mtrl_Anl_Pre_Invo,
             BOD_Mtrl_Anl_Late_Qty,BOD_Mtrl_Anl_Late_Invo]]

        # df_out_BODMtrlAnl column Type 변경
        TypeTrans_col = [BOD_Mtrl_Anl_JIT_Qty, BOD_Mtrl_Anl_JIT_Invo, BOD_Mtrl_Anl_Pre_Qty,
                         BOD_Mtrl_Anl_Pre_Invo, BOD_Mtrl_Anl_Late_Qty, BOD_Mtrl_Anl_Late_Invo]

        # 벡터 연산으로 데이터 타입 변경 및 빈값 처리
        df_out_BODMtrlAnl[TypeTrans_col] = df_out_BODMtrlAnl[TypeTrans_col].fillna(0).astype(int)

        print_df(df_out_BODMtrlAnl, 'df_out_BODMtrlAnl')

        step('=====> STEP 6 End')

        ################################################################################################################
        # STEP 7 :  input data machining
        ################################################################################################################
        step('=====> STEP 7 Start : input data machining')

        # Groupby Colulms 설정
        LTGroup_col = [Version_Name_COLUMN, Time_Planning_Month_COLUMN, Location_COLUMN, Trans_Ship_COLUMN,
                       Item_Material_COLUMN, Sub_Location_COLUMN, Port_COLUMN, Trans_Mode_COLUMN, Shipper_CLOUMN,
                       To_Port_COLUMN]


        # 최빈값 함수
        def calculate_mode(series):
            modes = series.mode()
            return modes.iloc[0] if not modes.empty else None


        # Measuar 값 설정을 위한 반복문
        df_out_BODMtrlAnlLTMin = pd.DataFrame()
        df_out_BODMtrlAnlLTMax = pd.DataFrame()
        df_out_BODMtrlAnlLTAvg = pd.DataFrame()
        df_out_BODMtrlAnlLTMode = pd.DataFrame()

        # Min / Max / Avg / Mode 값 설정
        for col in PlanningMonthList:
            # note(f"========== Cols list  :  {col} ")
            col = str(col)
            df_out_BODMtrlAnlLT_for = df_out_BODMtrlAnl_temp[df_out_BODMtrlAnl_temp[Time_Planning_Month_COLUMN] == col]
            df_out_BODMtrlAnlLT_Min = df_out_BODMtrlAnlLT_for.groupby(LTGroup_col, as_index=False).agg(
                PlanFactoryOut=(BOD_Item_Mtrl_W_Factory_Out, 'min'),
                PlanToPort=(BOD_Item_Mtrl_W_Port_To_Port, 'min'),
                PlanGR=(BOD_Item_Mtrl_W_GR_LT, 'min'),
                ActurlGR=(GR_LT, 'min'),
                ActualToPort=(Port_LT, 'min'))
            df_out_BODMtrlAnlLT_Min[Aggregate_COLUMN] = 'Min'
            df_out_BODMtrlAnlLTMin = pd.concat([df_out_BODMtrlAnlLTMin, df_out_BODMtrlAnlLT_Min], axis=0,
                                               ignore_index=True)
            # print_df(df_out_BODMtrlAnlLTMin , 'df_out_BODMtrlAnlLTMin 데이터 확인')
            # Max값 설정
            df_out_BODMtrlAnlLT_Max = df_out_BODMtrlAnlLT_for.groupby(LTGroup_col, as_index=False).agg(
                PlanFactoryOut=(BOD_Item_Mtrl_W_Factory_Out, 'max'),
                PlanToPort=(BOD_Item_Mtrl_W_Port_To_Port, 'max'),
                PlanGR=(BOD_Item_Mtrl_W_GR_LT, 'max'),
                ActurlGR=(GR_LT, 'max'),
                ActualToPort=(Port_LT, 'max'))
            df_out_BODMtrlAnlLT_Max[Aggregate_COLUMN] = 'Max'
            df_out_BODMtrlAnlLTMax = pd.concat([df_out_BODMtrlAnlLTMax, df_out_BODMtrlAnlLT_Max], axis=0,
                                               ignore_index=True)
            # print_df(df_out_BODMtrlAnlLTMax, 'df_out_BODMtrlAnlLTMax 데이터 확인')
            # Avg값 설정
            df_out_BODMtrlAnlLT_avg = df_out_BODMtrlAnlLT_for.groupby(LTGroup_col, as_index=False).agg(
                PlanFactoryOut=(BOD_Item_Mtrl_W_Factory_Out, 'mean'),
                PlanToPort=(BOD_Item_Mtrl_W_Port_To_Port, 'mean'),
                PlanGR=(BOD_Item_Mtrl_W_GR_LT, 'mean'),
                ActurlGR=(GR_LT, 'mean'),
                ActualToPort=(Port_LT, 'mean'))
            df_out_BODMtrlAnlLT_avg[Aggregate_COLUMN] = 'Avg'
            df_out_BODMtrlAnlLTAvg = pd.concat([df_out_BODMtrlAnlLTAvg, df_out_BODMtrlAnlLT_avg], axis=0,
                                               ignore_index=True)
            # print_df(df_out_BODMtrlAnlLTAvg, 'df_out_BODMtrlAnlLTAvg 데이터 확인')
            # Mode값 설정
            df_out_BODMtrlAnlLT_Mode = df_out_BODMtrlAnlLT_for.groupby(LTGroup_col, as_index=False).agg(
                PlanFactoryOut=(BOD_Item_Mtrl_W_Factory_Out, calculate_mode),
                PlanToPort=(BOD_Item_Mtrl_W_Port_To_Port, calculate_mode),
                PlanGR=(BOD_Item_Mtrl_W_GR_LT, calculate_mode),
                ActurlGR=(GR_LT, calculate_mode),
                ActualToPort=(Port_LT, calculate_mode))
            df_out_BODMtrlAnlLT_Min[Aggregate_COLUMN] = 'Mode'
            df_out_BODMtrlAnlLTMode = pd.concat([df_out_BODMtrlAnlLTMode, df_out_BODMtrlAnlLT_Min], axis=0,
                                                ignore_index=True)
            # print_df(df_out_BODMtrlAnlLTMode, 'df_out_BODMtrlAnlLTMode 데이터 확인')

        # # 데이터 프레임 컬럼명 변경
        df_out_BODMtrlAnlLTMin = df_out_BODMtrlAnlLTMin.rename(
            columns={'PlanFactoryOut': BOD_Mtrl_Anl_LT_Plan_Factory_Out_Min,
                     'PlanToPort': BOD_Mtrl_Anl_LT_Plan_To_port_Min,
                     'PlanGR': BOD_Mtrl_Anl_LT_Plan_GR_Min,
                     'ActurlGR': BOD_Mtrl_Anl_LT_Actual_GR_Min,
                     'ActualToPort': BOD_Mtrl_Anl_LT_Actual_To_port_Min})

        df_out_BODMtrlAnlLTMax = df_out_BODMtrlAnlLTMax.rename(
            columns={'PlanFactoryOut': BOD_Mtrl_Anl_LT_Plan_Factory_Out_Max,
                     'PlanToPort': BOD_Mtrl_Anl_LT_Plan_To_port_Max,
                     'PlanGR': BOD_Mtrl_Anl_LT_Plan_GR_Max,
                     'ActurlGR': BOD_Mtrl_Anl_LT_Actual_GR_Max,
                     'ActualToPort': BOD_Mtrl_Anl_LT_Actual_To_port_Max})

        df_out_BODMtrlAnlLTAvg = df_out_BODMtrlAnlLTAvg.rename(
            columns={'PlanFactoryOut': BOD_Mtrl_Anl_LT_Plan_Factory_Out_Avg,
                     'PlanToPort': BOD_Mtrl_Anl_LT_Plan_To_port_Avg,
                     'PlanGR': BOD_Mtrl_Anl_LT_Plan_GR_Avg,
                     'ActurlGR': BOD_Mtrl_Anl_LT_Actual_GR_Avg,
                     'ActualToPort': BOD_Mtrl_Anl_LT_Actual_To_port_Avg})

        df_out_BODMtrlAnlLTMode = df_out_BODMtrlAnlLTMode.rename(
            columns={'PlanFactoryOut': BOD_Mtrl_Anl_LT_Plan_Factory_Out_Mode,
                     'PlanToPort': BOD_Mtrl_Anl_LT_Plan_To_port_Mode,
                     'PlanGR': BOD_Mtrl_Anl_LT_Plan_GR_Mode,
                     'ActurlGR': BOD_Mtrl_Anl_LT_Actual_GR_Mode,
                     'ActualToPort': BOD_Mtrl_Anl_LT_Actual_To_port_Mode})

        # df_out_BODMtrlAnlLT 설정
        df_out_BODMtrlAnlLT = pd.concat(
            [df_out_BODMtrlAnlLTMin, df_out_BODMtrlAnlLTMax, df_out_BODMtrlAnlLTAvg, df_out_BODMtrlAnlLTMode], axis=0,
            ignore_index=True)

        # mg 값 복사
        df_out_BODMtrlAnlLT[BOD_Mtrl_Anl_LT_Actual_Factory_Out_Min] = df_out_BODMtrlAnlLT[
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Min]
        df_out_BODMtrlAnlLT[BOD_Mtrl_Anl_LT_Actual_Factory_Out_Max] = df_out_BODMtrlAnlLT[
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Max]
        df_out_BODMtrlAnlLT[BOD_Mtrl_Anl_LT_Actual_Factory_Out_Avg] = df_out_BODMtrlAnlLT[
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Avg]
        df_out_BODMtrlAnlLT[BOD_Mtrl_Anl_LT_Actual_Factory_Out_Mode] = df_out_BODMtrlAnlLT[
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Mode]

        # 형변환을 위한 컬럼 설정
        TypeTrans_LTcols = [
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Min, BOD_Mtrl_Anl_LT_Plan_To_port_Min, BOD_Mtrl_Anl_LT_Plan_GR_Min,
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Max, BOD_Mtrl_Anl_LT_Plan_To_port_Max, BOD_Mtrl_Anl_LT_Plan_GR_Max,
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Avg, BOD_Mtrl_Anl_LT_Plan_To_port_Avg, BOD_Mtrl_Anl_LT_Plan_GR_Avg,
            BOD_Mtrl_Anl_LT_Plan_Factory_Out_Mode, BOD_Mtrl_Anl_LT_Plan_To_port_Mode, BOD_Mtrl_Anl_LT_Plan_GR_Mode,
            BOD_Mtrl_Anl_LT_Actual_Factory_Out_Min, BOD_Mtrl_Anl_LT_Actual_To_port_Min, BOD_Mtrl_Anl_LT_Actual_GR_Min,
            BOD_Mtrl_Anl_LT_Actual_Factory_Out_Max, BOD_Mtrl_Anl_LT_Actual_To_port_Max, BOD_Mtrl_Anl_LT_Actual_GR_Max,
            BOD_Mtrl_Anl_LT_Actual_Factory_Out_Avg, BOD_Mtrl_Anl_LT_Actual_To_port_Avg, BOD_Mtrl_Anl_LT_Actual_GR_Avg,
            BOD_Mtrl_Anl_LT_Actual_Factory_Out_Mode, BOD_Mtrl_Anl_LT_Actual_To_port_Mode,BOD_Mtrl_Anl_LT_Actual_GR_Mode]

        # 형 변환 벡터 연산 2025-12-03 조건 수정 fillna(0) 에서 빈 값은 NaN으로 반환
        df_out_BODMtrlAnlLT[TypeTrans_LTcols] = df_out_BODMtrlAnlLT[TypeTrans_LTcols].apply(
            pd.to_numeric, errors='coerce')
        # df_out_BODMtrlAnlLT[TypeTrans_LTcols] = df_out_BODMtrlAnlLT[TypeTrans_LTcols].fillna(0)


        # # 컬럼명 변경
        # df_out_BODMtrlAnlLT = df_out_BODMtrlAnlLT.rename(columns={Time_Planning_Month_COLUMN: Time_Month_COLUMN})

        # 데이터 프레임 순서 지정
        df_out_BODMtrlAnlLT = df_out_BODMtrlAnlLT[
            [Version_Name_COLUMN, Time_Planning_Month_COLUMN, Location_COLUMN, Trans_Ship_COLUMN, Item_Material_COLUMN,
             Sub_Location_COLUMN, Port_COLUMN, Aggregate_COLUMN, Trans_Mode_COLUMN, Shipper_CLOUMN,
             To_Port_COLUMN] + TypeTrans_LTcols]

        print_df(df_out_BODMtrlAnlLT, 'df_out_BODMtrlAnlLT')

        step('=====> STEP 7 End')
        ################################################################################################################
        # STEP 8 :  input data machining 2025-10-17 일  로직 추가
        ################################################################################################################
        step('=====> STEP 8 Start : input data machining')

        # df_in_BODACT_temp 내용 복사
        df_out_BODMtrlAnlLT_temp = df_in_BODACT_temp.copy()

        # Trans_Ship_COLUMN 값 동일하게 변환
        df_out_BODMtrlAnlLT_temp[Trans_Ship_COLUMN] = np.where(df_out_BODMtrlAnl_temp[Mtrl_PO_Tracking_Trans_Port].isna(),
                                                               "Direct", 'T/S')

        # df_out_BODMtrlAnlLT_temp 필터를 위한 컬럼명 변경
        LT_rename_cols = {Mtrl_PO_Tracking_Org_Port: Port_COLUMN,
                          Mtrl_PO_Tracking_Vendor: Shipper_CLOUMN,
                          Mtrl_PO_Tracking_Arrival_Port: To_Port_COLUMN}
        df_out_BODMtrlAnlLT_temp = df_out_BODMtrlAnlLT_temp.rename(columns=LT_rename_cols)

        # 데이터 프레임 필터 컬럼 지정
        filter_df_cols = LTGroup_col + [BOD_Item_Mtrl_W_Intransit_LT, BOD_Item_Mtrl_W_Factory_Out, Port_LT, GR_LT]

        # 데이터 프레임 필터
        df_out_BODMtrlAnlLT_temp = df_out_BODMtrlAnlLT_temp[filter_df_cols]
        # 'VESSEL' 이것만 필터 링
        df_out_BODMtrlAnlLT_temp = df_out_BODMtrlAnlLT_temp[df_out_BODMtrlAnlLT_temp[Trans_Mode_COLUMN] == 'VESSEL']
        # BOD_Mtrl_Anl_LT_Plan_Intransit_LT_VSL 값 설정 BOD_Item_Mtrl_W_Intransit_LT 대입
        df_out_BODMtrlAnlLT_temp[BOD_Mtrl_Anl_LT_Plan_Intransit_LT_VSL] = df_out_BODMtrlAnlLT_temp[
            BOD_Item_Mtrl_W_Intransit_LT]
        # BOD_Item_Mtrl_W_Factory_Out, Port_LT, GR_LT 타입 변경
        df_out_BODMtrlAnlLT_temp[[BOD_Item_Mtrl_W_Factory_Out, Port_LT, GR_LT]] = df_out_BODMtrlAnlLT_temp[
            [BOD_Item_Mtrl_W_Factory_Out, Port_LT, GR_LT]].fillna(0).astype(int)
        # BOD_Mtrl_Anl_LT_Actual_Intransit_LT_VSL 값 설정 ( sum(BOD_Item_Mtrl_W_Factory_Out, Port_LT, GR_LT)
        df_out_BODMtrlAnlLT_temp[BOD_Mtrl_Anl_LT_Actual_Intransit_LT_VSL] = df_out_BODMtrlAnlLT_temp[
                                                                                BOD_Item_Mtrl_W_Factory_Out] + \
                                                                            df_out_BODMtrlAnlLT_temp[Port_LT] + \
                                                                            df_out_BODMtrlAnlLT_temp[GR_LT]

        # print_df(df_out_BODMtrlAnlLT_temp, 'df_out_BODMtrlAnlLT_temp_ 확인!!!!!!!!!!!!!!!!!!!!!!!!!')

        # BOD_Item_Mtrl_W_Intransit_LT, BOD_Item_Mtrl_W_Factory_Out, Port_LT, GR_LT 삭제
        df_out_BODMtrlAnlLT_temp = df_out_BODMtrlAnlLT_temp.drop(
            columns=[BOD_Item_Mtrl_W_Intransit_LT, BOD_Item_Mtrl_W_Factory_Out, Port_LT, GR_LT], axis=1)
        # 컬럼명 변경 및 머지를 위한 타입 변경
        df_out_BODMtrlAnlLT_temp[Time_Planning_Month_COLUMN] = df_out_BODMtrlAnlLT_temp[Time_Planning_Month_COLUMN].astype(str)
        # merge를 위한 키 설정 BOD_Mtrl_Anl_LT_Plan_Intransit_LT_VSL, BOD_Mtrl_Anl_LT_Actual_Intransit_LT_VSL 제외
        BODMtrlAnlLT_merge_key = list(df_out_BODMtrlAnlLT_temp.columns[:-2])
        # df_out_BODMtrlAnlLT 값 merge
        df_out_BODMtrlAnlLT = df_out_BODMtrlAnlLT.merge(df_out_BODMtrlAnlLT_temp, on=BODMtrlAnlLT_merge_key, how='left')

        print_df(df_out_BODMtrlAnlLT, 'df_out_BODMtrlAnlLT')
        step('=====> STEP 8End')
        ################################################################################################################
        # STEP 9 :  input data machining 2025-10-16 일 추가
        ################################################################################################################
        step('=====> STEP 9 Start : input data machining')
        print_df(df_in_BODACT_temp, 'df_in_BODACT_temp _데이터 확인',True)

        df_out_BODMtrlAnlChart_temp = df_in_BODACT_temp.copy()

        # 'VESSEL' 이것만 필터 링
        df_out_BODMtrlAnlChart_temp = df_out_BODMtrlAnlChart_temp[
            df_out_BODMtrlAnlChart_temp[Trans_Mode_COLUMN] == 'VESSEL']

        # 계산을 위한 데이터 타입 변경
        df_out_BODMtrlAnlChart_temp[GR_WEEK] = df_out_BODMtrlAnlChart_temp[GR_WEEK].astype(int)
        df_out_BODMtrlAnlChart_temp[Factory_ATDWEEK] = df_out_BODMtrlAnlChart_temp[Factory_ATDWEEK].astype(int)

        # Seq1_COLUMN 계산 (GR_WEEK - Factory_ATDWEEK)
        df_out_BODMtrlAnlChart_temp[Seq1_COLUMN] = df_out_BODMtrlAnlChart_temp[GR_WEEK] - df_out_BODMtrlAnlChart_temp[
            Factory_ATDWEEK]

        # 필요한 컬럼명만 리스트로 만듬
        df_filter_cols = [Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Sub_Location_COLUMN,
                          Seq1_COLUMN, Mtrl_PO_Tracking_GR_Qty, Mtrl_PO_Tracking_PO_No]
        # 필요한 데이터 프레임 필터
        df_out_BODMtrlAnlChart_temp = df_out_BODMtrlAnlChart_temp[df_filter_cols]

        # groupby_cols_list 생성 df_out_BODMtrlAnlChart_temp 컬럼명 기준으로 key 값 설정
        groupby_cols_list = list(df_out_BODMtrlAnlChart_temp.columns[
                                 :-2])  # 'Version.[Version Name]', 'Location.[Location]','Time.[Week]', 'Sub Location.[Sub Location]', 'Seq1.[Seq1]'

        df_out_BODMtrlAnlChart_temp[Mtrl_PO_Tracking_GR_Qty] = df_out_BODMtrlAnlChart_temp[
            Mtrl_PO_Tracking_GR_Qty].astype(int)
        # 그룹바이 실행
        df_out_BODMtrlAnlChart_temp = df_out_BODMtrlAnlChart_temp.groupby(groupby_cols_list, as_index=False).agg(
            BOD_Mtrl_Anl_Chart_Qty=(Mtrl_PO_Tracking_GR_Qty, 'sum'),
            BOD_Mtrl_Anl_Chart_Invo=(Mtrl_PO_Tracking_PO_No, 'count'))

        # BOD_Item_Mtrl_W_Intransit_LT 값을 구하기 위해 데이터 프레임 복사 및 필터
        df_out_BODMtrlAnlChart_Intransit_LT = df_out_BODMtrlAnl_temp[
            [Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Sub_Location_COLUMN,
             BOD_Item_Mtrl_W_Intransit_LT]].copy()

        # Time_Planning_Month_COLUMN 타입 변경 (그룹바이를 위한 데이터 타입 변경)
        df_out_BODMtrlAnlChart_Intransit_LT[Time_Week_COLUMN] = df_out_BODMtrlAnlChart_Intransit_LT[
            Time_Week_COLUMN].astype(str)

        df_out_BODMtrlAnlChart_Intransit_LT[BOD_Item_Mtrl_W_Intransit_LT] = pd.to_numeric(
            df_out_BODMtrlAnlChart_Intransit_LT[BOD_Item_Mtrl_W_Intransit_LT])

        df_out_BODMtrlAnlChart_Intransit_LT = df_out_BODMtrlAnlChart_Intransit_LT[
            df_out_BODMtrlAnlChart_Intransit_LT[BOD_Item_Mtrl_W_Intransit_LT] > 0]

        # BOD_Item_Mtrl_W_Intransit_LT min 값 구하기
        df_out_BODMtrlAnlChart_Intransit_LT = df_out_BODMtrlAnlChart_Intransit_LT.groupby([
            Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Sub_Location_COLUMN])[
            BOD_Item_Mtrl_W_Intransit_LT].min().reset_index()

        # BOD_Item_Mtrl_W_Intransit_LT 컬럼명 수정 및 중복 삭제
        df_out_BODMtrlAnlChart_Intransit_Seq = df_out_BODMtrlAnlChart_Intransit_LT.copy().rename(
            columns={BOD_Item_Mtrl_W_Intransit_LT: Seq1_COLUMN})
        df_out_BODMtrlAnlChart_Intransit_Seq = df_out_BODMtrlAnlChart_Intransit_Seq.drop_duplicates()

        df_out_BODMtrlAnlChart_base = pd.concat([
            df_out_BODMtrlAnlChart_temp[
                [Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN,
                 Sub_Location_COLUMN, Seq1_COLUMN]], df_out_BODMtrlAnlChart_Intransit_Seq], axis=0, ignore_index=True)

        df_out_BODMtrlAnlChart_temp[Seq1_COLUMN] = df_out_BODMtrlAnlChart_temp[Seq1_COLUMN].astype(str)
        df_out_BODMtrlAnlChart_base[Seq1_COLUMN] = df_out_BODMtrlAnlChart_base[Seq1_COLUMN].astype(str)

        df_out_BODMtrlAnlChart_temp = df_out_BODMtrlAnlChart_base.merge(
            df_out_BODMtrlAnlChart_temp,
            on=[Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Sub_Location_COLUMN, Seq1_COLUMN],
            how='left')

        # df_out_BODMtrlAnlChart_temp 에 구한 BOD_Item_Mtrl_W_Intransit_LT min 값 merge
        df_out_BODMtrlAnlChart_temp = df_out_BODMtrlAnlChart_temp.merge(
            df_out_BODMtrlAnlChart_Intransit_LT,
            on=[Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Sub_Location_COLUMN], how='left')

        df_out_BODMtrlAnlChart_temp['BOD_Mtrl_Anl_Chart_Qty'] = df_out_BODMtrlAnlChart_temp[
            'BOD_Mtrl_Anl_Chart_Qty'].fillna(0).astype(int)
        df_out_BODMtrlAnlChart_temp['BOD_Mtrl_Anl_Chart_Invo'] = df_out_BODMtrlAnlChart_temp[
            'BOD_Mtrl_Anl_Chart_Invo'].fillna(0).astype(int)
        df_out_BODMtrlAnlChart_temp[BOD_Item_Mtrl_W_Intransit_LT] = df_out_BODMtrlAnlChart_temp[
            BOD_Item_Mtrl_W_Intransit_LT].fillna(0).astype(int).astype(str)

        # Seq1_COLUMN 와 BOD_Item_Mtrl_W_Intransit_LT 값이 같으면 BOD_Mtrl_Anl_Chart_Plan 에 1 아니면 0
        df_out_BODMtrlAnlChart_temp[BOD_Mtrl_Anl_Chart_Plan] = np.where(
            df_out_BODMtrlAnlChart_temp[Seq1_COLUMN].isin(df_out_BODMtrlAnlChart_temp[BOD_Item_Mtrl_W_Intransit_LT]), 1,
            0)

        # BOD_Mtrl_Anl_Chart_Plan 데이터 타입 변경
        df_out_BODMtrlAnlChart_temp[BOD_Mtrl_Anl_Chart_Plan] = df_out_BODMtrlAnlChart_temp[
            BOD_Mtrl_Anl_Chart_Plan].astype(int)

        # df_out_BODMtrlAnlChart_temp 컬럼명 변경
        df_out_BODMtrlAnlChart_temp = df_out_BODMtrlAnlChart_temp.rename(
            columns={'BOD_Mtrl_Anl_Chart_Qty': BOD_Mtrl_Anl_Chart_Qty,
                     'BOD_Mtrl_Anl_Chart_Invo': BOD_Mtrl_Anl_Chart_Invo})

        df_out_BODMtrlAnlChart_temp[Seq1_COLUMN] = df_out_BODMtrlAnlChart_temp[Seq1_COLUMN].astype(str)

        note(f"Seq1_COLUMN unique_list : {df_out_BODMtrlAnlChart_temp[Seq1_COLUMN].unique()}")
        # out put data frame 으로 변경
        df_out_BODMtrlAnlChart = df_out_BODMtrlAnlChart_temp.copy()

        print_df(df_out_BODMtrlAnlChart, "df_out_BODMtrlAnlChart _BOD_Item_Mtrl_W_Intransit_LT 확인")
        # BOD_Item_Mtrl_W_Intransit_LT 컬럼 삭제
        df_out_BODMtrlAnlChart = df_out_BODMtrlAnlChart.drop(columns=BOD_Item_Mtrl_W_Intransit_LT)

        print_df(df_out_BODMtrlAnlChart,"df_out_BODMtrlAnlChart")

        step('=====> STEP 9 End')
        ################################################################################################################
        # STEP 9 :  input data machining
        ################################################################################################################
        step('=====> STEP 10 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_BODMtrlAnl, 'df_out_BODMtrlAnl', True)
            print_df(df_out_BODMtrlAnlLT, 'df_out_BODMtrlAnlLT', True)
            print_df(df_out_BODMtrlAnlChart, 'df_out_BODMtrlAnlChart', True)

        print_df(df_out_BODMtrlAnl, 'df_out_BODMtrlAnl', True)
        print_df(df_out_BODMtrlAnlLT, 'df_out_BODMtrlAnlLT', True)
        print_df(df_out_BODMtrlAnlChart, 'df_out_BODMtrlAnlChart', True)

        row_count, col_count = df_out_BODMtrlAnl.shape
        note(f'=====> Final df_out_BODMtrlAnl rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_BODMtrlAnlLT.shape
        note(f'=====> Final df_out_BODMtrlAnlLT rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_BODMtrlAnlChart.shape
        note(f'=====> Final df_out_BODMtrlAnlChart rows : {row_count} , Columns : {col_count}')

        step('=====> STEP 10 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODMtrlAnl = pd.DataFrame([], columns=[])
        df_out_BODMtrlAnlLT = pd.DataFrame([], columns=[])
        df_out_BODMtrlAnlChart = pd.DataFrame([], columns=[])

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