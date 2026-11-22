"""
* 프로그램명 
    - PY_UI_BODAnlSet

* 내용
    - BOD Analysis(Set) Measure Data 생성

* 변경이력
    - 2024.12.31 / 양희영 / Create
    - 2025.11.19 / 양희영 / Update2
    
* Flow Summary
    BOD Analysis(Set) Measure Data 생성

* Execution 

* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.

* Input Tables
    - df_in_BODLIST : Select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Sub Location].[Sub Site Stage].filter(#.Name startswith "DC") * 
                      [Sub Location].[Sub Location Rep AP2] * [Trans Mode].[Trans Mode].[VESSEL] ) on row, 
                      ({Measure.[BOD List_BOD LT], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Shipment LT]}) 
                      on column where { Measure.[BOD List_BOD Valid] == "Y"};
    - df_in_BODACT : Select ([Version].[Version Name] * [Item].[Product Group] * [Item].[Item] * [Item].[Item Stage].[SET] * &Last6MonthAndLastYear6Month * [Location].[Location] * 
                     [To Time].[To Day] * [Sales Domain].[AP2] * [Sequence].[Sequence] * [Category].[Category] * [Sub Location].[Sub Location] ) on row, 
                     ({Measure.[BOD Act Anl_Carrier Name], Measure.[BOD Act Anl_ATA], Measure.[BOD Act Anl_Billing Doc], Measure.[BOD Act Anl_Billing Item], Measure.[BOD Act Anl_Container No], 
                     Measure.[BOD Act Anl_ETA], Measure.[BOD Act Anl_GR Date], Measure.[BOD Act Anl_GR Doc Item], Measure.[BOD Act Anl_GR Doc No], Measure.[BOD Act Anl_GR Qty], Measure.[BOD Act Anl_ITTS Container], 
                     Measure.[BOD Act Anl_Invoice Item], Measure.[BOD Act Anl_Invoice No], Measure.[BOD Act Anl_Lead Time], Measure.[BOD Act Anl_MFG Qty], Measure.[BOD Act Anl_PO Item], Measure.[BOD Act Anl_PO No], 
                     Measure.[BOD Act Anl_Prod Date], Measure.[BOD Act Anl_SO Item], Measure.[BOD Act Anl_SO No], Measure.[BOD Act Anl_Shipment Qty]}) on column;
    - df_in_TMCAL : select (&Last18WeeksPlanningMonths * Time.[Week] * [Time].[Day] * [Time].[Day of Week]);
    - df_in_TMCUR : select (Time.[Planning Month] * &CurrentWeek);
    - df_in_TimeWeek : Select ([Time].[Week] * [Time].[Day]);

* Output Tables
    - df_out_BODSETAnl : MG : BOD SET Anl :
                         Select ([Version].[Version Name] * [Item].[Product Group] * [Location].[Location] * [Sales Domain].[AP2] * [Category].[Category] * 
                         [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Sequence].[Sequence]) on row, 
                         ({Measure.[BOD SET Anl_Carrier Name],Measure.[BOD SET Anl_Container Qty],Measure.[BOD SET Anl_MON],Measure.[BOD SET Anl_TUE],
                         Measure.[BOD SET Anl_WED],Measure.[BOD SET Anl_THU],Measure.[BOD SET Anl_FRI],Measure.[BOD SET Anl_SAT],Measure.[BOD SET Anl_SUN],
                         Measure.[BOD SET Anl_Act TTL AVG],Measure.[BOD SET Anl_Act TTL MIN],Measure.[BOD SET Anl_Act TTL MAX],Measure.[BOD SET Anl_Act Ship AVG],
                         Measure.[BOD SET Anl_Act Ship MIN],Measure.[BOD SET Anl_Act Ship MAX],Measure.[BOD SET Anl_Act Ship D.Mode],Measure.[BOD SET Anl_Act To Port AVG],
                         Measure.[BOD SET Anl_Act To Port MIN],Measure.[BOD SET Anl_Act To Port MAX],Measure.[BOD SET Anl_Act To Port D.Mode],Measure.[BOD SET Anl_Act GR AVG],
                         Measure.[BOD SET Anl_Act GR MIN],Measure.[BOD SET Anl_Act GR MAX],Measure.[BOD SET Anl_Act GR D.Mode],Measure.[BOD SET Anl_Act TTL D.MODE],
                         Measure.[BOD SET Anl_Act Ship Pre Month],Measure.[BOD SET Anl_Act To Port Pre Month],Measure.[BOD SET Anl_Act GR Pre Month],
                         Measure.[BOD SET Anl_Act TTL Pre Month],Measure.[BOD SET Anl_BOD Plan],Measure.[BOD SET Anl_Ship Plan],Measure.[BOD SET Anl_TTL Plan],
                         Measure.[BOD SET Anl_INVO],Measure.[BOD SET Anl_JIT INVO],Measure.[BOD SET Anl_Frequent Day INVO],Measure.[BOD SET Anl_before Wed Arrival INVO],
                         Measure.[BOD SET Anl_Pre Arrival 1W INVO],Measure.[BOD SET Anl_Pre Arrival 2W INVO],Measure.[BOD SET Anl_late Arrival 1W INVO],
                         Measure.[BOD SET Anl_late Arrival 2W INVO],Measure.[BOD SET Anl_Qty],Measure.[BOD SET Anl_JIT Qty],Measure.[BOD SET Anl_Frequent Day Qty],
                         Measure.[BOD SET Anl_before Wed Arrival Qty],Measure.[BOD SET Anl_Pre Arrival 1W Qty],Measure.[BOD SET Anl_Pre Arrival 2W Qty],
                         Measure.[BOD SET Anl_late Arrival 1W Qty],Measure.[BOD SET Anl_late Arrival 2W Qty]}) on column;
    - df_out_BODSETAnlLT : MG : BOD Set Anl LT
                        Select ([Version].[Version Name] * [Item].[Product Group] * [Location].[Location] * [Sales Domain].[AP2] * [Category].[Category] * 
                        [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Aggregate].[Aggregate] * [Sequence].[Sequence]) on row, 
                        ({Measure.[BOD SET Anl LT_Carrier Name],Measure.[BOD SET Anl LT_BOD Actual],Measure.[BOD SET Anl LT_Ship Actual],
                        Measure.[BOD SET Anl LT_Total Actual],Measure.[BOD SET Anl LT_BOD Plan],Measure.[BOD SET Anl LT_Ship Plan],Measure.[BOD SET Anl LT_Total Plan]}) on column;
* 테스트 스크립트
    EXEC plugin instance [PY_UI_BODAnlSet] for measures {[BOD SET Anl LT_BOD Actual]} using scope (&MPV) 
     using arguments {("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BODAnlSet'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)

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
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====>STEP 0-1 DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    col_VersionVersionName           = 'Version.[Version Name]'
    col_ItemItem                     = 'Item.[Item]'
    col_ItemProductGroup             = 'Item.[Product Group]'
    col_LocationLocation             = 'Location.[Location]'
    col_SubLocationSubLocation       = 'Sub Location.[Sub Location]'
    col_SubLocationSubLocationRepAP2 = 'Sub Location.[Sub Location Rep AP2]'
    col_TransModeTransMode           = 'Trans Mode.[Trans Mode]'
    col_SalesDomainAP2               = 'Sales Domain.[AP2]'
    col_TimePlanningMonth            = 'Time.[Planning Month]'
    col_TimeWeek                     = 'Time.[Week]'
    col_TimeDay                      = 'Time.[Day]'
    col_TimeDayofWeek                = 'Time.[Day of Week]'
    col_ToTimeToDay                  = 'To Time.[To Day]'
    col_CategoryCategory             = 'Category.[Category]'
    col_CarrierCarrier               = 'Carrier.[Carrier]'
    col_AggregateAggregate           = 'Aggregate.[Aggregate]'
    col_SequenceSequence             = 'Sequence.[Sequence]'
    
    col_BODList_BODLT              = 'BOD List_BOD LT'
    col_BODList_ShipmentLT         = 'BOD List_Shipment LT'
    
    col_BODActAnl_CarrierName      = 'BOD Act Anl_Carrier Name'
    col_BODActAnl_GRDate           = 'BOD Act Anl_GR Date'
    col_BODActAnl_GRQty            = 'BOD Act Anl_GR Qty'
    col_BODActAnl_ATA              = 'BOD Act Anl_ATA'
    col_BODActAnl_ETA              = 'BOD Act Anl_ETA'
    col_BODActAnl_ProdDate         = 'BOD Act Anl_Prod Date'
    col_BODActAnl_PONo             = 'BOD Act Anl_PO No'
    col_BODActAnl_InvoiceNo        = 'BOD Act Anl_Invoice No'
    col_BODActAnl_ContainerNo      = 'BOD Act Anl_Container No'
    
    col_BODSETAnlLT_CarrierName   = 'BOD SET Anl LT_Carrier Name'
    col_BODSETAnlLT_BODActual     = 'BOD SET Anl LT_BOD Actual'
    col_BODSETAnlLT_ShipActual    = 'BOD SET Anl LT_Ship Actual'
    col_BODSETAnlLT_TotalActual   = 'BOD SET Anl LT_Total Actual'
    col_BODSETAnlLT_BODPlan       = 'BOD SET Anl LT_BOD Plan'
    col_BODSETAnlLT_ShipPlan      = 'BOD SET Anl LT_Ship Plan'
    col_BODSETAnlLT_TotalPlan     = 'BOD SET Anl LT_Total Plan'
    
    col_BODSETAnl_CarrierName       = 'BOD SET Anl_Carrier Name'
    col_BODSETAnl_ContainerQty      = 'BOD SET Anl_Container Qty'
    col_BODSETAnl_MON               = 'BOD SET Anl_MON'
    col_BODSETAnl_TUE               = 'BOD SET Anl_TUE'
    col_BODSETAnl_WED               = 'BOD SET Anl_WED'
    col_BODSETAnl_THU               = 'BOD SET Anl_THU'
    col_BODSETAnl_FRI               = 'BOD SET Anl_FRI'
    col_BODSETAnl_SAT               = 'BOD SET Anl_SAT'
    col_BODSETAnl_SUN               = 'BOD SET Anl_SUN'
    col_BODSETAnl_ActTTLAVG         = 'BOD SET Anl_Act TTL AVG'
    col_BODSETAnl_ActTTLD_MODE      = 'BOD SET Anl_Act TTL D.MODE'
    col_BODSETAnl_ActTTLMAX         = 'BOD SET Anl_Act TTL MAX'
    col_BODSETAnl_ActTTLMIN         = 'BOD SET Anl_Act TTL MIN'
    col_BODSETAnl_ActShipAVG        = 'BOD SET Anl_Act Ship AVG'
    col_BODSETAnl_ActShipD_Mode     = 'BOD SET Anl_Act Ship D.Mode'
    col_BODSETAnl_ActShipMAX        = 'BOD SET Anl_Act Ship MAX'
    col_BODSETAnl_ActShipMIN        = 'BOD SET Anl_Act Ship MIN'
    col_BODSETAnl_ActToPortAVG      = 'BOD SET Anl_Act To Port AVG'
    col_BODSETAnl_ActToPortD_Mode   = 'BOD SET Anl_Act To Port D.Mode'
    col_BODSETAnl_ActToPortMAX      = 'BOD SET Anl_Act To Port MAX'
    col_BODSETAnl_ActToPortMIN      = 'BOD SET Anl_Act To Port MIN'
    col_BODSETAnl_ActGRAVG          = 'BOD SET Anl_Act GR AVG'
    col_BODSETAnl_ActGRD_Mode       = 'BOD SET Anl_Act GR D.Mode'
    col_BODSETAnl_ActGRMAX          = 'BOD SET Anl_Act GR MAX'
    col_BODSETAnl_ActGRMIN          = 'BOD SET Anl_Act GR MIN'
    
    col_BODSETAnl_ActShipPreMonth   = 'BOD SET Anl_Act Ship Pre Month'
    col_BODSETAnl_ActToPortPreMonth = 'BOD SET Anl_Act To Port Pre Month'
    col_BODSETAnl_ActGRPreMonth     = 'BOD SET Anl_Act GR Pre Month'
    col_BODSETAnl_ActTTLPreMonth    = 'BOD SET Anl_Act TTL Pre Month'
    
    #2025.10.29 추가 --------------------------------------------------
    col_BODSETAnl_ActShipLastYear   = 'BOD SET Anl_Act Ship Last Year'
    col_BODSETAnl_ActToPortLastYear = 'BOD SET Anl_Act To Port Last Year'
    col_BODSETAnl_ActGRLastYear     = 'BOD SET Anl_Act GR Last Year'
    col_BODSETAnl_ActTTLLastYear    = 'BOD SET Anl_Act TTL Last Year'
    #-----------------------------------------------------------------
    
    col_BODSETAnl_TTLPlan           = 'BOD SET Anl_TTL Plan'
    col_BODSETAnl_BODPlan           = 'BOD SET Anl_BOD Plan'
    col_BODSETAnl_ShipPlan          = 'BOD SET Anl_Ship Plan'

    col_BODSETAnl_INVO                 = 'BOD SET Anl_INVO'
    col_BODSETAnl_JITINVO              = 'BOD SET Anl_JIT INVO'
    col_BODSETAnl_FrequentDay          = 'BOD SET Anl_Frequent Day' #2025.11.11 추가
    col_BODSETAnl_FrequentDayINVO      = 'BOD SET Anl_Frequent Day INVO'
    col_BODSETAnl_beforeWedArrivalINVO = 'BOD SET Anl_before Wed Arrival INVO'
    col_BODSETAnl_PreArrival1WINVO     = 'BOD SET Anl_Pre Arrival 1W INVO'
    col_BODSETAnl_PreArrival2WINVO     = 'BOD SET Anl_Pre Arrival 2W INVO'
    col_BODSETAnl_lateArrival1WINVO    = 'BOD SET Anl_late Arrival 1W INVO'
    col_BODSETAnl_lateArrival2WINVO    = 'BOD SET Anl_late Arrival 2W INVO'
    col_BODSETAnl_Qty                  = 'BOD SET Anl_Qty'
    col_BODSETAnl_JITQty               = 'BOD SET Anl_JIT Qty'
    col_BODSETAnl_FrequentDayQty       = 'BOD SET Anl_Frequent Day Qty'
    col_BODSETAnl_beforeWedArrivalQty  = 'BOD SET Anl_before Wed Arrival Qty'
    col_BODSETAnl_PreArrival1WQty      = 'BOD SET Anl_Pre Arrival 1W Qty'
    col_BODSETAnl_PreArrival2WQty      = 'BOD SET Anl_Pre Arrival 2W Qty'
    col_BODSETAnl_lateArrival1WQty     = 'BOD SET Anl_late Arrival 1W Qty'
    col_BODSETAnl_lateArrival2WQty     = 'BOD SET Anl_late Arrival 2W Qty'
        
    col_LeadTime     = 'LeadTime'
    col_GR_WEEK      = 'GR_WEEK'
    col_ETA_WEEK     = 'ETA_WEEK'
    col_GR_DayofWeek = 'GR Day of Week'
    col_ETAPre1W     = 'ETA Pre 1W'
    col_ETAPre2W     = 'ETA Pre 2W'
    col_ETAlate1W    = 'ETA late 1W'
    col_ETAlate2W    = 'ETA late 2W'
    
    #   ETA Pre 1W    ETA Pre 2W    ETA late 1W    ETA late 2W
    # 칼럼 List 설정
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_BODLIST = read_csv_file("df_in_BODLIST")
        df_in_BODACT  = read_csv_file("df_in_BODACT")
        df_in_TMCAL   = read_csv_file("df_in_TMCAL")
        df_in_TMCUR   = read_csv_file("df_in_TMCUR")
        df_in_TimeWeek = read_csv_file("df_in_TimeWeek") #2025.11.14 추가 : ETA_WEEK 구하기 위해, df_in_TMCAL 대체 사용, df_in_TMCAL 은 조건 사용으로 참조 안되는 일자가 있음.
        
    # if df_in_InfoRecord.empty:
    #    raise Exception("=====> raise Exception: df_in_InfoRecord is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
            
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    print_df(df_in_BODLIST, 'df_in_BODLIST', False)
    print_df(df_in_BODACT, 'df_in_BODACT', False)
    print_df(df_in_TMCAL, 'df_in_TMCAL', False)
    print_df(df_in_TMCUR, 'df_in_TMCUR', False)
    print_df(df_in_TimeWeek, 'df_in_TimeWeek', False)
        
    # DATA TYPE 설정
    if df_in_BODACT[col_BODActAnl_GRDate].dtype != 'datetime64[ns]':
        df_in_BODACT[col_BODActAnl_GRDate] = pd.to_datetime(df_in_BODACT[col_BODActAnl_GRDate], format='%m/%d/%Y %I:%M:%S %p')
        
    if df_in_BODACT[col_BODActAnl_ATA].dtype != 'datetime64[ns]':
        df_in_BODACT[col_BODActAnl_ATA] = pd.to_datetime(df_in_BODACT[col_BODActAnl_ATA], format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_BODACT[col_BODActAnl_ETA].dtype != 'datetime64[ns]':
        df_in_BODACT[col_BODActAnl_ETA] = pd.to_datetime(df_in_BODACT[col_BODActAnl_ETA], format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_BODACT[col_BODActAnl_ProdDate].dtype != 'datetime64[ns]':
        df_in_BODACT[col_BODActAnl_ProdDate] = pd.to_datetime(df_in_BODACT[col_BODActAnl_ProdDate], format='%m/%d/%Y %I:%M:%S %p')    
    
    df_in_BODACT[col_ToTimeToDay] = pd.to_datetime(df_in_BODACT[col_ToTimeToDay], format='%Y-%m-%d')
    df_in_BODACT = df_in_BODACT.astype({col_BODActAnl_ContainerNo: 'str'}, copy=True)
    
    df_in_TMCAL[col_TimeDay] = pd.to_datetime(df_in_TMCAL[col_TimeDay], format='%Y-%m-%d')
    df_in_TMCAL = df_in_TMCAL.astype({col_TimePlanningMonth: 'str', col_TimeWeek: 'str'}, copy=True)
    df_in_TMCUR = df_in_TMCUR.astype({col_TimePlanningMonth: 'str', col_TimeWeek: 'str'}, copy=True)

    df_in_TimeWeek = df_in_TimeWeek[[col_TimeDay, col_TimeWeek]]
    df_in_TimeWeek[col_TimeDay] = pd.to_datetime(df_in_TimeWeek[col_TimeDay], format='%Y-%m-%d')
    df_in_TimeWeek = df_in_TimeWeek.astype({col_TimeWeek: 'str'}, copy=True)
    
    print_df(df_in_BODACT, 'df_in_BODACT -2', False)
    print_df(df_in_TMCAL, 'df_in_TMCAL -2', False)
    print_df(df_in_TMCUR, 'df_in_TMCUR -2', False)
    print_df(df_in_TimeWeek, 'df_in_TimeWeek -2', False)
    
    #step('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 1 : 전처리 : BODACT / BODACT2 생성
    ################################################################################################################
    step('=====> STEP 1-1 :  BODACT Create')
    '''
    Time.[Planning Month] 설정
       -. Category : PORT-GR 또는 SHIP-GR
            Time.[Day] == BOD Act Anl_GR Date
       -. Category : MFG-SHIP
            Time.[Day] == To Time.[To Day] 
       -. Category : SHIP-PORT
            Time.[Day] == BOD Act Anl_ATA
    '''
    df_in_TMCAL = df_in_TMCAL[[col_TimePlanningMonth, col_TimeWeek, col_TimeDay, col_TimeDayofWeek]]
    #df_BODACT = df_in_BODACT.copy()
    
    # df 분리
    df_BODACT_PORTGR   = df_in_BODACT[df_in_BODACT[col_CategoryCategory] == "PORT-GR"].copy()
    df_BODACT_SHIPGR   = df_in_BODACT[df_in_BODACT[col_CategoryCategory] == "SHIP-GR"].copy()
    df_BODACT_MFGSHIP  = df_in_BODACT[df_in_BODACT[col_CategoryCategory] == "MFG-SHIP"].copy()
    df_BODACT_SHIPPORT = df_in_BODACT[df_in_BODACT[col_CategoryCategory] == "SHIP-PORT"].copy()
    
    
    # 기준일자 세팅
    df_BODACT_PORTGR[col_TimeDay]   = df_BODACT_PORTGR[col_BODActAnl_GRDate]
    df_BODACT_SHIPGR[col_TimeDay]   = df_BODACT_SHIPGR[col_BODActAnl_GRDate]
    df_BODACT_MFGSHIP[col_TimeDay]  = df_BODACT_MFGSHIP[col_ToTimeToDay]
    df_BODACT_SHIPPORT[col_TimeDay] = df_BODACT_SHIPPORT[col_BODActAnl_ATA]
    
    # Merge
    df_BODACT_PORTGR   = df_BODACT_PORTGR.merge(df_in_TMCAL, on=[col_TimeDay], how='left')
    df_BODACT_SHIPGR   = df_BODACT_SHIPGR.merge(df_in_TMCAL, on=[col_TimeDay], how='left')
    df_BODACT_MFGSHIP  = df_BODACT_MFGSHIP.merge(df_in_TMCAL, on=[col_TimeDay], how='left')
    df_BODACT_SHIPPORT = df_BODACT_SHIPPORT.merge(df_in_TMCAL, on=[col_TimeDay], how='left')
    
    # LeadTime
    df_BODACT_PORTGR[col_LeadTime]  = (df_BODACT_PORTGR[col_BODActAnl_GRDate] - df_BODACT_PORTGR[col_BODActAnl_ATA]).dt.days
    df_BODACT_SHIPGR[col_LeadTime]  = (df_BODACT_SHIPGR[col_BODActAnl_GRDate] - df_BODACT_SHIPGR[col_ToTimeToDay]).dt.days
    df_BODACT_MFGSHIP[col_LeadTime] = (df_BODACT_MFGSHIP[col_ToTimeToDay] - df_BODACT_MFGSHIP[col_BODActAnl_ProdDate]).dt.days
    df_BODACT_SHIPPORT[col_LeadTime] = (df_BODACT_SHIPPORT[col_BODActAnl_ATA] - df_BODACT_SHIPPORT[col_ToTimeToDay]).dt.days
    
    df_BODACT = pd.concat([df_BODACT_PORTGR, df_BODACT_SHIPGR ,df_BODACT_MFGSHIP,df_BODACT_SHIPPORT])
    del [df_BODACT_PORTGR, df_BODACT_SHIPGR, df_BODACT_MFGSHIP, df_BODACT_SHIPPORT]
    
    df_BODACT[col_TimeDayofWeek] = np.where((df_BODACT[col_CategoryCategory] == "SHIP-GR"),
                                               df_BODACT[col_TimeDayofWeek], '')
    
    df_BODACT.drop(columns=[col_TimeDay], inplace=True)
    
    print_df(df_BODACT, 'df_BODACT', False)
    
    #step('=====> STEP 1-2 :  BODACT Create End')

    #####################################################################################################
    #------------------------------------------------------------------------------
    step('=====> STEP 1-3 :  BODACT2 Create')
    df_BODACT2 = df_in_BODACT[(df_in_BODACT[col_CategoryCategory] == "SHIP-GR") & df_in_BODACT[col_BODActAnl_GRDate].notna()].copy()
    del df_in_BODACT
    
    #df_BODACT2 = df_BODACT2.merge(df_in_TMCAL, left_on=[col_BODActAnl_ETA], right_on=[col_TimeDay], how='inner')
    df_BODACT2 = df_BODACT2.merge(df_in_TimeWeek, left_on=[col_BODActAnl_ETA], right_on=[col_TimeDay], how='inner')
    df_BODACT2.rename(columns={col_TimeWeek: col_ETA_WEEK}, inplace=True)
    #df_BODACT2.drop(columns=[col_TimePlanningMonth, col_TimeDay, col_TimeDayofWeek], inplace=True)
    df_BODACT2.drop(columns=[col_TimeDay], inplace=True)
    del df_in_TimeWeek
    
    # group by
    # Version.[Version Name], Item.[Product Group], Location.[Location], Sales Domain.[AP2], Sub Location.[Sub Location], To Time.[To Day]
    # BOD Act Anl_Carrier Name, BOD Act Anl_PO No, BOD Act Anl_Invoice No, BOD Act Anl_ETA, ETA_WEEK
    cList_group = [col_VersionVersionName, col_ItemProductGroup, col_LocationLocation, col_SalesDomainAP2, 
                      col_SubLocationSubLocation, col_ToTimeToDay, col_BODActAnl_CarrierName, 
                      col_BODActAnl_PONo, col_BODActAnl_InvoiceNo, col_BODActAnl_ETA, col_ETA_WEEK]
    df_BODACT2 = df_BODACT2.groupby(cList_group, as_index=False).agg({col_BODActAnl_GRDate: "min",
                                                                      col_BODActAnl_GRQty: "sum"}, skipna=True).copy()
    # GR_WEEK 구하기
    df_BODACT2 = df_BODACT2.merge(df_in_TMCAL, left_on=[col_BODActAnl_GRDate], right_on=[col_TimeDay], how='inner')
    del df_in_TMCAL
    df_BODACT2.rename(columns={col_TimeWeek:col_GR_WEEK, col_TimeDayofWeek: col_GR_DayofWeek}, inplace=True)
    #df_BODACT2.drop(columns=[col_TimePlanningMonth, col_TimeDay], inplace=True)
    df_BODACT2.drop(columns=[col_TimeDay], inplace=True) # M0 ~ M-6 구할때 col_TimePlanningMonth 사용
    
    df_BODACT2[col_ETAPre1W] = df_BODACT2[col_ETA_WEEK].apply(lambda x: common.gfn_add_week(x, -1))
    df_BODACT2[col_ETAPre2W] = df_BODACT2[col_ETA_WEEK].apply(lambda x: common.gfn_add_week(x, -2))

    df_BODACT2[col_ETAlate1W] = df_BODACT2[col_ETA_WEEK].apply(lambda x: common.gfn_add_week(x, 1))
    df_BODACT2[col_ETAlate2W] = df_BODACT2[col_ETA_WEEK].apply(lambda x: common.gfn_add_week(x, 2))
    
    print_df(df_BODACT2, 'df_BODACT2', False)
    
    #step('=====> STEP 1-4 :  BODACT2 Create End')
    
    ################################################################################################################
    # STEP 2 : BOD Set Anl LT 생성
    ################################################################################################################
    step('=====> STEP 2-1 : M-0 ~ M-6 Create')
    # 당월 M-0 ~ M-6 구하기
    df_TMCUR = df_in_TMCUR[[col_TimePlanningMonth]].copy()
    df_TMCUR['Month_date'] =  pd.to_datetime(df_TMCUR[col_TimePlanningMonth] + '01', format='%Y%m%d')
    df_TMCUR['M0'] = df_TMCUR[col_TimePlanningMonth]
    df_TMCUR['M-1'] = (df_TMCUR['Month_date'].apply(lambda x: x - relativedelta(months=1))).dt.strftime('%Y%m')
    df_TMCUR['M-2'] = (df_TMCUR['Month_date'].apply(lambda x: x - relativedelta(months=2))).dt.strftime('%Y%m')
    df_TMCUR['M-3'] = (df_TMCUR['Month_date'].apply(lambda x: x - relativedelta(months=3))).dt.strftime('%Y%m')
    df_TMCUR['M-6'] = (df_TMCUR['Month_date'].apply(lambda x: x - relativedelta(months=6))).dt.strftime('%Y%m')
    df_TMCUR.drop(columns=[col_TimePlanningMonth, 'Month_date'], inplace=True)
    df_TMCUR['Join_Column'] = 'A'
    print_df(df_TMCUR, 'df_TMCUR', False)
    
    # 전월 M-0 ~ M-6 구하기
    df_TMCUR_Pre = df_in_TMCUR[[col_TimePlanningMonth]].copy()
    df_TMCUR_Pre['Month_date'] = pd.to_datetime(df_TMCUR_Pre[col_TimePlanningMonth] + '01', format='%Y%m%d')
    df_TMCUR_Pre['Pre Month_date'] = df_TMCUR_Pre['Month_date'].apply(lambda x: x - relativedelta(months=1))
    df_TMCUR_Pre['M0']  = df_TMCUR_Pre['Pre Month_date'].dt.strftime('%Y%m')
    df_TMCUR_Pre['M-1'] = (df_TMCUR_Pre['Pre Month_date'].apply(lambda x: x - relativedelta(months=1))).dt.strftime('%Y%m')
    df_TMCUR_Pre['M-2'] = (df_TMCUR_Pre['Pre Month_date'].apply(lambda x: x - relativedelta(months=2))).dt.strftime('%Y%m')
    df_TMCUR_Pre['M-3'] = (df_TMCUR_Pre['Pre Month_date'].apply(lambda x: x - relativedelta(months=3))).dt.strftime('%Y%m')
    df_TMCUR_Pre['M-6'] = (df_TMCUR_Pre['Pre Month_date'].apply(lambda x: x - relativedelta(months=6))).dt.strftime('%Y%m')
    df_TMCUR_Pre.drop(columns=[col_TimePlanningMonth, 'Month_date', 'Pre Month_date'], inplace=True)
    df_TMCUR_Pre['Join_Column'] = 'A'
    
    print_df(df_TMCUR_Pre, 'df_TMCUR_Pre', False)
    
    # 2025.10.29, 임채수 프로 요청 : 전년 동기의 L/T값도 PreMonth 처럼 M0. M-1, M-2, M-3, M-6 로 생성 부탁드립니다.
    # 전년 M-0 ~ M-6 구하기
    df_TMCUR_LastYear = df_in_TMCUR[[col_TimePlanningMonth]].copy()
    del df_in_TMCUR
    df_TMCUR_LastYear['Month_date'] = pd.to_datetime(df_TMCUR_LastYear[col_TimePlanningMonth] + '01', format='%Y%m%d')
    df_TMCUR_LastYear['Last Year_date'] = df_TMCUR_LastYear['Month_date'].apply(lambda x: x - relativedelta(months=12))
    df_TMCUR_LastYear['M0']  = df_TMCUR_LastYear['Last Year_date'].dt.strftime('%Y%m')
    df_TMCUR_LastYear['M-1'] = (df_TMCUR_LastYear['Last Year_date'].apply(lambda x: x - relativedelta(months=1))).dt.strftime('%Y%m')
    df_TMCUR_LastYear['M-2'] = (df_TMCUR_LastYear['Last Year_date'].apply(lambda x: x - relativedelta(months=2))).dt.strftime('%Y%m')
    df_TMCUR_LastYear['M-3'] = (df_TMCUR_LastYear['Last Year_date'].apply(lambda x: x - relativedelta(months=3))).dt.strftime('%Y%m')
    df_TMCUR_LastYear['M-6'] = (df_TMCUR_LastYear['Last Year_date'].apply(lambda x: x - relativedelta(months=6))).dt.strftime('%Y%m')
    df_TMCUR_LastYear.drop(columns=[col_TimePlanningMonth, 'Month_date', 'Last Year_date'], inplace=True)
    df_TMCUR_LastYear['Join_Column'] = 'A'
    
    print_df(df_TMCUR_LastYear, 'df_TMCUR_LastYear', False)

    #####################################################################################################
    step('=====> STEP 2-2 : BOD SET Anl LT_BOD Actual Create')
    #BOD SET Anl LT_BOD Actual 생성 ---------------------------------------------------
    #BOD Act Anl_Carrier Name ==> Carrier.[Carrier]
    #df_BODACT[col_CarrierCarrier] = df_BODACT[col_BODActAnl_CarrierName]
    df_BODACT[col_TransModeTransMode] = 'VESSEL'
    
    df_LT_BOD_Actual = df_BODACT[(df_BODACT[col_CategoryCategory] == "SHIP-GR") &
                                  df_BODACT[col_LeadTime].notna()].copy()
    df_LT_BOD_Actual['Join_Column'] = 'A'
    df_LT_BOD_Actual = df_LT_BOD_Actual.merge(df_TMCUR, on='Join_Column', how='inner')
    #df_LT_BOD_Actual[col_LeadTime] = df_LT_BOD_Actual[col_LeadTime].astype('int64')
    
    print_df(df_LT_BOD_Actual, 'df_LT_BOD_Actual', False)
    
    cList_LT_Grain = [col_VersionVersionName, col_ItemProductGroup, col_LocationLocation, col_SalesDomainAP2,
                      col_CategoryCategory, col_SubLocationSubLocation, col_TransModeTransMode, col_AggregateAggregate]
    cList_LT_All = cList_LT_Grain + [col_SequenceSequence, col_BODActAnl_CarrierName,
                                     col_BODSETAnlLT_BODActual, col_BODSETAnlLT_ShipActual, col_BODSETAnlLT_TotalActual, 
                                     col_BODSETAnlLT_BODPlan, col_BODSETAnlLT_ShipPlan, col_BODSETAnlLT_TotalPlan]
    
    cList_LT_group = cList_LT_Grain + [col_BODActAnl_CarrierName]
    
    cList_LT_BODActual  = cList_LT_group + [col_BODSETAnlLT_BODActual]
    cList_LT_ShipActual  = cList_LT_group + [col_BODSETAnlLT_ShipActual]
    #cList_LT_TotalActual = cList_LT_group + [col_BODSETAnlLT_BODActual, col_BODSETAnlLT_ShipActual, col_BODSETAnlLT_TotalActual]
   
    list_MG =  [col_BODSETAnlLT_BODActual, col_BODSETAnlLT_ShipActual, col_BODSETAnlLT_TotalActual, 
                  col_BODSETAnlLT_BODPlan, col_BODSETAnlLT_ShipPlan, col_BODSETAnlLT_TotalPlan]
    list_Month = ['M0', 'M-1', 'M-2', 'M-3', 'M-6']
    list_Agg = ['Avg', 'Min', 'Max', 'Mode']
        
    # 최빈값의 max값 구하기
    def max_mode(series):
        mode_value = series.mode()
        return mode_value.max()
    
    #note(f'=====> for Start ======================================================= ')
    df_LT_BOD_Actual_result = pd.DataFrame(columns=cList_LT_BODActual) #빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_BOD_Actual[col_TimePlanningMonth] == df_LT_BOD_Actual['M0']
        elif sMonth == 'M-1':
            v_cond = ((df_LT_BOD_Actual[col_TimePlanningMonth] <= df_LT_BOD_Actual['M0']) & 
                      (df_LT_BOD_Actual[col_TimePlanningMonth] >= df_LT_BOD_Actual['M-1']))
        elif sMonth == 'M-2':
            v_cond = ((df_LT_BOD_Actual[col_TimePlanningMonth] <= df_LT_BOD_Actual['M0']) & 
                      (df_LT_BOD_Actual[col_TimePlanningMonth] >= df_LT_BOD_Actual['M-2']))
        elif sMonth == 'M-3':
            v_cond = ((df_LT_BOD_Actual[col_TimePlanningMonth] <= df_LT_BOD_Actual['M0']) & 
                      (df_LT_BOD_Actual[col_TimePlanningMonth] >= df_LT_BOD_Actual['M-3']))
        elif sMonth == 'M-6':
            v_cond = ((df_LT_BOD_Actual[col_TimePlanningMonth] <= df_LT_BOD_Actual['M0']) & 
                      (df_LT_BOD_Actual[col_TimePlanningMonth] >= df_LT_BOD_Actual['M-6']))
        #note(v_cond)
        
        for sAgg in list_Agg:
            
            df_Ext_Data = df_LT_BOD_Actual[v_cond].copy()
            
            if not df_Ext_Data.empty:
                df_Ext_Data[col_CategoryCategory] = sMonth
                df_Ext_Data[col_AggregateAggregate] = sAgg
                
                if sAgg == 'Avg':
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].mean()
                elif  sAgg == 'Min':
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].min()
                elif  sAgg == 'Max':
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].max()
                elif  sAgg == 'Mode':
                    #df_Ext_Data2 = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].agg(lambda x: x.mode().iloc[0])
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].apply(max_mode)
            
            #if not df_Ext_Data.empty:
                df_Ext_Data[col_BODSETAnlLT_BODActual] = df_Ext_Data[col_LeadTime].round(0).astype('int64')            
                
                #칼럼 정리
                df_Ext_Data = df_Ext_Data[cList_LT_BODActual]
                #print_df(df_Ext_Data, 'df_Ext_Data', False)
            
                df_LT_BOD_Actual_result = pd.concat([df_LT_BOD_Actual_result, df_Ext_Data])
                del df_Ext_Data
    
    #note(f'=====> for End ======================================================= ')
    
    del df_LT_BOD_Actual
    df_LT_BOD_Actual_result = df_LT_BOD_Actual_result.astype({col_BODSETAnlLT_BODActual: 'int64'}, copy=True)
    print_df(df_LT_BOD_Actual_result, 'df_LT_BOD_Actual_result', False)
    #step('=====> STEP 2-2 : BOD SET Anl LT_BOD Actual Create End')

    #####################################################################################################
    step('=====> STEP 2-3 : BOD SET Anl LT_Ship Actual Create')
    # BOD SET Anl LT_Ship Actual 생성 ------------------------------------------------------------
    df_LT_MFGSHIP = df_BODACT[(df_BODACT[col_CategoryCategory] == "MFG-SHIP") &
                                  df_BODACT[col_LeadTime].notna() ].copy()
    df_LT_MFGSHIP['Join_Column'] = 'A'
    df_LT_Ship_Actual = df_LT_MFGSHIP.merge(df_TMCUR, on='Join_Column', how='inner')
    
    #print_df(df_LT_Ship_Actual, 'df_LT_Ship_Actual', False)
    
    #note(f'=====> for Start ======================================================= ')
    df_LT_Ship_Actual_result = pd.DataFrame(columns=cList_LT_ShipActual)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_Ship_Actual[col_TimePlanningMonth] == df_LT_Ship_Actual['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-6'])
        
        for sAgg in list_Agg:
            
            df_Ext_Data = df_LT_Ship_Actual[v_cond].copy()
            
            if not df_Ext_Data.empty:
                df_Ext_Data[col_CategoryCategory] = sMonth
                df_Ext_Data[col_AggregateAggregate] = sAgg
                
                if sAgg == 'Avg':
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].mean()
                elif sAgg == 'Min':
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].min()
                elif sAgg == 'Max':
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].max()
                elif sAgg == 'Mode':
                    #df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].agg(pd.Series.mode)
                    df_Ext_Data = df_Ext_Data.groupby(cList_LT_group, as_index=False)[col_LeadTime].apply(max_mode)
                
            #if not df_Ext_Data.empty:
                df_Ext_Data[col_BODSETAnlLT_ShipActual] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
                
                # 칼럼 정리
                df_Ext_Data = df_Ext_Data[cList_LT_ShipActual]
                #print_df(df_Ext_Data, 'df_Ext_Data', False)
                
                df_LT_Ship_Actual_result = pd.concat([df_LT_Ship_Actual_result, df_Ext_Data])
                del df_Ext_Data
    
    #note(f'=====> for End ======================================================= ')

    #del df_LT_Ship_Actual
    df_LT_Ship_Actual_result = df_LT_Ship_Actual_result.astype({col_BODSETAnlLT_ShipActual: 'int64'}, copy=True)
    print_df(df_LT_Ship_Actual_result, 'df_LT_Ship_Actual_result', False)
    #step('=====> STEP 2-3 : BOD SET Anl LT_Ship Actual Create End')

    #####################################################################################################
    step('=====> STEP 2-4 : BOD SET Anl LT_Total Actual Create')
    # BOD SET Anl LT_Total Actual 생성 ------------------------------------------------------------
    # BOD SET Anl LT_BOD Actual + BOD SET Anl LT_Ship Actual
    
    # Merge : df_LT_BOD_Actual_result & df_LT_Ship_Actual_result
    df_LT_Total_Actual = df_LT_BOD_Actual_result.merge(df_LT_Ship_Actual_result, on=cList_LT_group, how='outer')
    
    df_LT_Total_Actual[col_BODSETAnlLT_TotalActual] = (df_LT_Total_Actual[col_BODSETAnlLT_BODActual].fillna(0) +
                                                       df_LT_Total_Actual[col_BODSETAnlLT_ShipActual].fillna(0))
    
    print_df(df_LT_Total_Actual, 'df_LT_Total_Actual', False)
    #step('=====> STEP 2-4 : BOD SET Anl LT_Ship Actual Create End')

    #####################################################################################################
    step('=====> STEP 2-5 : BOD SET Anl LT_BOD Plan Create')
    # BOD SET Anl LT_BOD Plan 생성 ------------------------------------------------------------
    cList_LT_BODPlan = cList_LT_group + [col_BODSETAnlLT_BODPlan]
    
    # BODLIST.BOD List_BOD LT null인경우 0
    df_in_BODLIST[col_BODList_BODLT] = df_in_BODLIST[col_BODList_BODLT].fillna(0)
    df_in_BODLIST[col_BODList_ShipmentLT] = df_in_BODLIST[col_BODList_ShipmentLT].fillna(0)
    
    # Merge : df_in_BODLIST & df_LT_BOD_Actual_result
    df_LT_BODPlan = df_in_BODLIST.merge(df_LT_BOD_Actual_result, 
                                         on=[col_VersionVersionName, col_LocationLocation, col_SubLocationSubLocation, col_TransModeTransMode],
                                         how='inner', suffixes=('', '_y'))
    # 250409 | 임재민 | 실적/계획 모두 있는것으로 변경
    #                                    how='left', suffixes=('', '_y'))
    del df_LT_BOD_Actual_result
    
    # 조인된 경우
    df_LT_BODPlan_1 = df_LT_BODPlan[df_LT_BODPlan[col_CategoryCategory].notna()].copy()
    df_LT_BODPlan_1[col_BODSETAnlLT_BODPlan] = df_LT_BODPlan_1[col_BODList_BODLT]
    
    #칼럼정리
    df_LT_BODPlan_1 = df_LT_BODPlan_1[cList_LT_BODPlan]
    
    print_df(df_LT_BODPlan_1, 'df_LT_BODPlan_1', False)
    
    # 위 250409 | 임재민 | 실적,계획 모두 있는것으로 구성하도록 수정. 에서 inner 조인으로 변경, 조인된 경우만 사용, 아래 부분 필요없음.
    '''
    # 조인되지 않은 경우
    df_LT_BODPlan_2 = df_LT_BODPlan[df_LT_BODPlan[col_CategoryCategory].isna()].copy()
    df_LT_BODPlan_2[col_ItemProductGroup] = '-'
    df_LT_BODPlan_2[col_SalesDomainAP2]   = df_LT_BODPlan_2[col_SubLocationSubLocationRepAP2]
    df_LT_BODPlan_2[col_BODActAnl_CarrierName] = '-'
    df_LT_BODPlan_2[col_BODSETAnlLT_BODPlan] = df_LT_BODPlan_2[col_BODList_BODLT]
    
    print_df(df_LT_BODPlan_2, 'df_LT_BODPlan_2', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_LT_BODPlan_result = pd.DataFrame(columns=cList_LT_BODPlan)  # 빈 dataframe
    for sMonth in list_Month:                
        for sAgg in list_Agg:
            
            df_LT_BODPlan_2[col_CategoryCategory] = sMonth
            df_LT_BODPlan_2[col_AggregateAggregate] = sAgg
            
            df_Ext_Data = df_LT_BODPlan_2.copy()
            
            if not df_Ext_Data.empty:
                # 칼럼 정리
                df_Ext_Data = df_Ext_Data[cList_LT_BODPlan]
                # print_df(df_Ext_Data, 'df_Ext_Data', False)
                
                df_LT_BODPlan_result = pd.concat([df_LT_BODPlan_result, df_Ext_Data])
                del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    
    del df_LT_BODPlan_2
    df_LT_BODPlan_result = pd.concat([df_LT_BODPlan_1, df_LT_BODPlan_result])
    '''
    df_LT_BODPlan_result = df_LT_BODPlan_1.copy()
    del df_LT_BODPlan_1
    df_LT_BODPlan_result[col_BODSETAnlLT_BODPlan] = df_LT_BODPlan_result[col_BODSETAnlLT_BODPlan].fillna(0).astype('int64')
    print_df(df_LT_BODPlan_result, 'df_LT_BODPlan_result', False)
        
    #step('=====> STEP 2-5 : BOD SET Anl LT_BOD Plan Create End')

    #####################################################################################################
    step('=====> STEP 2-6 : BOD SET Anl LT_Ship Plan Create')
    # BOD SET Anl LT_Ship Plan 생성 ------------------------------------------------------------
    cList_LT_ShipPlan = cList_LT_group + [col_BODSETAnlLT_ShipPlan]
    
    # Merge : df_in_BODLIST & df_LT_Ship_Actual_result
    df_LT_ShipPlan = df_in_BODLIST.merge(df_LT_Ship_Actual_result,
                                        on=[col_VersionVersionName, col_LocationLocation, col_SubLocationSubLocation, col_TransModeTransMode],
                                        #how='left', suffixes=('', '_y')).copy()
                                        how='inner', suffixes=('', '_y')).copy() # BOD SET Anl LT_BOD Plan 생성과 동일하게 적용.
    del [df_in_BODLIST, df_LT_Ship_Actual_result]
    
    # 조인된 경우
    df_LT_ShipPlan_1 = df_LT_ShipPlan[df_LT_ShipPlan[col_CategoryCategory].notna()].copy()
    df_LT_ShipPlan_1[col_BODSETAnlLT_ShipPlan] = df_LT_ShipPlan_1[col_BODList_ShipmentLT]
    #print_df(df_LT_ShipPlan_1, 'df_LT_ShipPlan_1', False)
    # 칼럼정리
    df_LT_ShipPlan_1 = df_LT_ShipPlan_1[cList_LT_ShipPlan]
    
    #print_df(df_LT_ShipPlan_1, 'df_LT_ShipPlan_1', False)
    
    # 위 inner 조인으로 변경, 조인된 경우만 사용, 아래 부분 필요없음. 
    '''
    # 조인되지 않은 경우
    df_LT_ShipPlan_2 = df_LT_ShipPlan[df_LT_ShipPlan[col_CategoryCategory].isna()].copy()
    df_LT_ShipPlan_2[col_ItemProductGroup] = '-'
    df_LT_ShipPlan_2[col_SalesDomainAP2] = df_LT_ShipPlan_2[col_SubLocationSubLocationRepAP2]
    df_LT_ShipPlan_2[col_BODActAnl_CarrierName] = '-'
    df_LT_ShipPlan_2[col_BODSETAnlLT_ShipPlan] = df_LT_ShipPlan_2[col_BODList_ShipmentLT]
    
    #print_df(df_LT_ShipPlan_2, 'df_LT_ShipPlan_2', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_LT_ShipPlan_result = pd.DataFrame(columns=cList_LT_ShipPlan)  # 빈 dataframe
    for sMonth in list_Month:
        for sAgg in list_Agg:
            
            df_LT_ShipPlan_2[col_CategoryCategory] = sMonth
            df_LT_ShipPlan_2[col_AggregateAggregate] = sAgg
            
            df_Ext_Data = df_LT_ShipPlan_2.copy()
            
            if not df_Ext_Data.empty:
                # 칼럼 정리
                df_Ext_Data = df_Ext_Data[cList_LT_ShipPlan]
                # print_df(df_Ext_Data, 'df_Ext_Data', False)
                
                df_LT_ShipPlan_result = pd.concat([df_LT_ShipPlan_result, df_Ext_Data])
                del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    
    del df_LT_ShipPlan_2
    df_LT_ShipPlan_result = pd.concat([df_LT_ShipPlan_1, df_LT_ShipPlan_result])
    '''
    df_LT_ShipPlan_result = df_LT_ShipPlan_1.copy()
    del df_LT_ShipPlan_1
    df_LT_ShipPlan_result[col_BODSETAnlLT_ShipPlan] = df_LT_ShipPlan_result[col_BODSETAnlLT_ShipPlan].fillna(0).astype('int64')
    print_df(df_LT_ShipPlan_result, 'df_LT_ShipPlan_result', False)
    
    #step('=====> STEP 2-6 : BOD SET Anl LT_Ship Plan Create End')

    #####################################################################################################
    step('=====> STEP 2-7 : BOD SET Anl LT_Total Plan Create')
    # BOD SET Anl LT_Total Plan 생성 ------------------------------------------------------------
    cList_LT_TotalPlan = cList_LT_group + [col_BODSETAnlLT_BODPlan, col_BODSETAnlLT_ShipPlan, col_BODSETAnlLT_TotalPlan]
    
    # Merge : df_LT_BODPlan_result & df_LT_ShipPlan_result
    df_LT_TotalPlan = df_LT_BODPlan_result.merge(df_LT_ShipPlan_result, on=cList_LT_group, how='outer')     
    del [df_LT_BODPlan_result, df_LT_ShipPlan_result]
    
    df_LT_TotalPlan[col_BODSETAnlLT_TotalPlan] = (df_LT_TotalPlan[col_BODSETAnlLT_BODPlan].fillna(0) + 
                                                  df_LT_TotalPlan[col_BODSETAnlLT_ShipPlan].fillna(0))
    
    # 칼럼정리
    df_LT_TotalPlan = df_LT_TotalPlan[cList_LT_TotalPlan]
    
    print_df(df_LT_TotalPlan, 'df_LT_TotalPlan', False)
    #step('=====> STEP 2-7 : BOD SET Anl LT_Total Plan Create End')

    #####################################################################################################
    step('=====> STEP 2-8 : MG : BOD Set Anl LT Create')
    df_BODSetAnlLT = df_LT_Total_Actual.copy()
    df_BODSetAnlLT = df_BODSetAnlLT.merge(df_LT_TotalPlan, on=cList_LT_group, how='outer')
    
    # Sequence 는 BOD SET Anl 의 Sequence 사용 : 2025.11.13 수정
    '''
    # Sequence 생성
    #df_BODSetAnlLT[col_SequenceSequence] = df_BODSetAnlLT.groupby(cList_LT_Grain, 
    #        as_index=False)[col_BODSETAnlLT_BODPlan].rank(method='first',ascending=True).astype('int64')
    
    clist_sort = cList_LT_group
    df_BODSetAnlLT.sort_values(by=clist_sort, ascending=[True, True, True, True, True, True, True, True,
                                                         True], axis=0, inplace=True)
    df_BODSetAnlLT[col_SequenceSequence] = 1
    df_BODSetAnlLT[col_SequenceSequence] = df_BODSetAnlLT.groupby(cList_LT_Grain)[col_SequenceSequence].cumsum()
    
    #print_df(df_BODSetAnlLT, 'df_BODSetAnlLT', False)
    
    # 칼럼정리
    df_BODSetAnlLT = df_BODSetAnlLT[cList_LT_All]
    '''
    # 칼럼명 변경 : BOD Act Anl_Carrier Name ==> BOD SET Anl LT_Carrier Name 
    df_BODSetAnlLT.rename(columns={col_BODActAnl_CarrierName: col_BODSETAnlLT_CarrierName}, inplace=True)
    
    print_df(df_BODSetAnlLT, 'df_BODSetAnlLT', False)
    
    #step('=====> STEP 2-8 : MG : BOD Set Anl LT Create End')
    
    ################################################################################################################
    # STEP 3 :  BOD Set Anl 생성(BODACT)
    ################################################################################################################
    cList_Anl_Grain = [col_VersionVersionName, col_ItemProductGroup, col_LocationLocation, col_SalesDomainAP2,
                      col_CategoryCategory, col_SubLocationSubLocation, col_TransModeTransMode]
    
    cList_Anl_All = cList_Anl_Grain + [col_SequenceSequence, col_BODActAnl_CarrierName, 
                                       col_BODSETAnl_ContainerQty, col_BODSETAnl_MON, col_BODSETAnl_TUE, col_BODSETAnl_WED, col_BODSETAnl_THU,
                                       col_BODSETAnl_FRI, col_BODSETAnl_SAT, col_BODSETAnl_SUN, col_BODSETAnl_FrequentDay,
                                       col_BODSETAnl_ActTTLAVG, col_BODSETAnl_ActTTLMIN, 
                                       col_BODSETAnl_ActTTLMAX, col_BODSETAnl_ActShipAVG, col_BODSETAnl_ActShipMIN, col_BODSETAnl_ActShipMAX, col_BODSETAnl_ActShipD_Mode, 
                                       col_BODSETAnl_ActToPortAVG, col_BODSETAnl_ActToPortMIN, col_BODSETAnl_ActToPortMAX, col_BODSETAnl_ActToPortD_Mode, col_BODSETAnl_ActGRAVG, 
                                       col_BODSETAnl_ActGRMIN, col_BODSETAnl_ActGRMAX, col_BODSETAnl_ActGRD_Mode, col_BODSETAnl_ActTTLD_MODE, 
                                       col_BODSETAnl_ActShipPreMonth, col_BODSETAnl_ActToPortPreMonth, col_BODSETAnl_ActGRPreMonth, col_BODSETAnl_ActTTLPreMonth, 
                                       col_BODSETAnl_ActShipLastYear, col_BODSETAnl_ActToPortLastYear, col_BODSETAnl_ActGRLastYear, col_BODSETAnl_ActTTLLastYear, #2025.10.29 추가
                                       col_BODSETAnl_BODPlan, col_BODSETAnl_ShipPlan, col_BODSETAnl_TTLPlan, 
                                       col_BODSETAnl_INVO, col_BODSETAnl_JITINVO, col_BODSETAnl_FrequentDayINVO, col_BODSETAnl_beforeWedArrivalINVO,
                                       col_BODSETAnl_PreArrival1WINVO, col_BODSETAnl_PreArrival2WINVO, col_BODSETAnl_lateArrival1WINVO, col_BODSETAnl_lateArrival2WINVO, col_BODSETAnl_Qty,
                                       col_BODSETAnl_JITQty, col_BODSETAnl_FrequentDayQty, col_BODSETAnl_beforeWedArrivalQty, col_BODSETAnl_PreArrival1WQty, col_BODSETAnl_PreArrival2WQty, 
                                       col_BODSETAnl_lateArrival1WQty, col_BODSETAnl_lateArrival2WQty]
    
    cList_Anl_group = cList_Anl_Grain + [col_BODActAnl_CarrierName]
    
    cList_Anl_ContainerQty = cList_Anl_group + [col_BODSETAnl_ContainerQty]

    #####################################################################################################
    # BOD SET Anl_Container Qty 생성 ------------------------------------------------------------
    step('=====> STEP 3-1 : BOD SET Anl_Container Qty Create')
    df_Anl_SHIPGR = df_BODACT[(df_BODACT[col_CategoryCategory] == "SHIP-GR")].copy()
    df_Anl_SHIPGR['Join_Column'] = 'A'
    df_Anl_SHIPGR = df_Anl_SHIPGR.merge(df_TMCUR, on='Join_Column', how='inner')
    
    df_Anl_SHIPGR['ToDay-ContainerNo'] =  df_Anl_SHIPGR[col_ToTimeToDay].dt.date.astype('str') + ':' + df_Anl_SHIPGR[col_BODActAnl_ContainerNo]
    print_df(df_Anl_SHIPGR, 'df_Anl_SHIPGR', False)
    # note(f'=====> for Start ======================================================= ')
    df_Anl_ContainerQty = pd.DataFrame(columns=cList_Anl_ContainerQty)  # 빈 dataframe
    
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_Anl_SHIPGR[col_TimePlanningMonth] == df_Anl_SHIPGR['M0']
        elif sMonth == 'M-1':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-6'])
        
        #df_Ext_Data = df_Anl_SHIPGR.copy()
        df_Ext_Data = df_Anl_SHIPGR[v_cond].copy()
        
        if not df_Ext_Data.empty:
            df_Ext_Data[col_CategoryCategory] = sMonth        
            df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)['ToDay-ContainerNo'].nunique() #count(distinct)
        
        #if not df_Ext_Data.empty:
            df_Ext_Data[col_BODSETAnl_ContainerQty] = df_Ext_Data['ToDay-ContainerNo'].astype('int64')
            
            # 칼럼 정리
            df_Ext_Data = df_Ext_Data[cList_Anl_ContainerQty]
            # print_df(df_Ext_Data, 'df_Ext_Data', False)
            
            df_Anl_ContainerQty = pd.concat([df_Anl_ContainerQty, df_Ext_Data])
            del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    df_Anl_ContainerQty = df_Anl_ContainerQty.astype({col_BODSETAnl_ContainerQty: 'int64'}, copy=True)
    print_df(df_Anl_ContainerQty, 'df_Anl_ContainerQty', False)
    
    #step('=====> STEP 3-1 : BOD SET Anl_Container Qty Create End')

    #####################################################################################################
    # BOD SET Anl_MON ~ SUN 생성 ------------------------------------------------------------
    step('=====> STEP 3-2 : BOD SET Anl_MON ~ SUN Create')
    #cList_Anl_Mon = cList_Anl_group + [col_BODSETAnl_MON]
    
    list_DayofWeek = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    
    cList_Anl_Week = (cList_Anl_group +
                      [col_BODSETAnl_MON, col_BODSETAnl_TUE, col_BODSETAnl_WED, col_BODSETAnl_THU,
                       col_BODSETAnl_FRI, col_BODSETAnl_SAT, col_BODSETAnl_SUN] +
                      list_DayofWeek)
    
    df_Anl_Week = pd.DataFrame(columns=cList_Anl_Week)  # 빈 dataframe
    
    # note(f'=====> for Start ======================================================= ')
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_Anl_SHIPGR[col_TimePlanningMonth] == df_Anl_SHIPGR['M0']
        elif sMonth == 'M-1':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_Anl_SHIPGR[col_TimePlanningMonth] <= df_Anl_SHIPGR['M0']) & (
                df_Anl_SHIPGR[col_TimePlanningMonth] >= df_Anl_SHIPGR['M-6'])
        
        df_Anl_Month_Week = pd.DataFrame(columns=cList_Anl_group)  # 빈 dataframe
        for sDayofWeek in list_DayofWeek:
            df_Ext_Data = df_Anl_SHIPGR[(v_cond) & (df_Anl_SHIPGR[col_TimeDayofWeek] == sDayofWeek)].copy()
            df_Ext_Data[col_CategoryCategory] = sMonth
            
            if not df_Ext_Data.empty:
            #if df_Ext_Data.empty:
            #    df_Ext_Data = df_Ext_Data[cList_Anl_group]
            #    df_Ext_Data['BOD SET Anl_' + sDayofWeek] = np.nan
            #else:
                df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_TimeDayofWeek].count()
                df_Ext_Data['BOD SET Anl_' + sDayofWeek] = df_Ext_Data[col_TimeDayofWeek].astype('int64')
                df_Ext_Data[sDayofWeek] = df_Ext_Data[col_TimeDayofWeek].astype('int64') # max값의 요일을 구하기 위해 생성
                df_Ext_Data.drop(columns=[col_TimeDayofWeek], inplace=True)
                #print_df(df_Ext_Data, 'df_Ext_Data', False)
                
                df_Anl_Month_Week = df_Anl_Month_Week.merge(df_Ext_Data, on=cList_Anl_group, how='outer', suffixes=('', '_y'))
                del df_Ext_Data
        
        df_Anl_Week = pd.concat([df_Anl_Week, df_Anl_Month_Week])
        del df_Anl_Month_Week
    # note(f'=====> for Eed ======================================================= ')
    del df_Anl_SHIPGR
    
    # 2025.11.11 추가
    # BOD SET Anl_Frequent Day : 요일별 값 중 max 값의 요일
    days = ['MON','TUE','WED','THU','FRI','SAT','SUN']
    df_Anl_Week[col_BODSETAnl_FrequentDay] = df_Anl_Week[days].idxmax(axis=1)
    df_Anl_Week.drop(columns=days,inplace=True)
    
    print_df(df_Anl_Week, 'df_Anl_Week', False)
    
    #step('=====> STEP 3-2 : BOD SET Anl_MON ~ SUN Create End')

    #####################################################################################################
    # BOD SET Anl_Act Ship AVG/D.Mode/MAX/MIN 생성 ------------------------------------------------------------
    step('=====> STEP 3-3 : BOD SET Anl_Act Ship AVG/D.Mode/MAX/MIN Create')
    
    # note(f'=====> for Start ======================================================= ')
    #df_Anl_ActShip = pd.DataFrame(columns=cList_Anl_group)  # 빈 dataframe
    cList_Anl_ShipAVG = cList_Anl_group + [col_BODSETAnl_ActShipAVG]
    cList_Anl_ShipMIN = cList_Anl_group + [col_BODSETAnl_ActShipMIN]
    cList_Anl_ShipMAX = cList_Anl_group + [col_BODSETAnl_ActShipMAX]
    cList_Anl_ShipMODE = cList_Anl_group + [col_BODSETAnl_ActShipD_Mode]
    
    df_Anl_ActShip_AVG = pd.DataFrame(columns=cList_Anl_ShipAVG)  # 빈 dataframe
    df_Anl_ActShip_MIN = pd.DataFrame(columns=cList_Anl_ShipMIN)  # 빈 dataframe
    df_Anl_ActShip_MAX = pd.DataFrame(columns=cList_Anl_ShipMAX)  # 빈 dataframe
    df_Anl_ActShip_MODE = pd.DataFrame(columns=cList_Anl_ShipMODE)  # 빈 dataframe
    
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_Ship_Actual[col_TimePlanningMonth] == df_LT_Ship_Actual['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_Ship_Actual[col_TimePlanningMonth] <= df_LT_Ship_Actual['M0']) & (
                      df_LT_Ship_Actual[col_TimePlanningMonth] >= df_LT_Ship_Actual['M-6'])
        
        for sAgg in list_Agg:
            
            df_Ext_Data = df_LT_Ship_Actual[v_cond].copy()
            
            if not df_Ext_Data.empty:
                df_Ext_Data[col_CategoryCategory] = sMonth
                
                if sAgg == 'Avg':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActShipAVG] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActShip_AVG = pd.concat([df_Anl_ActShip_AVG, df_Ext_Data])
                        
                elif sAgg == 'Min':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].min()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActShipMIN] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActShip_MIN = pd.concat([df_Anl_ActShip_MIN, df_Ext_Data])
                        
                elif sAgg == 'Max':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].max()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActShipMAX] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActShip_MAX = pd.concat([df_Anl_ActShip_MAX, df_Ext_Data])
                        
                elif sAgg == 'Mode':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].apply(max_mode)
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActShipD_Mode] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActShip_MODE = pd.concat([df_Anl_ActShip_MODE, df_Ext_Data])
                
                del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_Ship_Actual
    df_Anl_ActShip = df_Anl_ActShip_AVG.copy()
    df_Anl_ActShip = df_Anl_ActShip.merge(df_Anl_ActShip_MIN, on=cList_Anl_group, how='outer')
    df_Anl_ActShip = df_Anl_ActShip.merge(df_Anl_ActShip_MAX, on=cList_Anl_group, how='outer')
    df_Anl_ActShip = df_Anl_ActShip.merge(df_Anl_ActShip_MODE, on=cList_Anl_group, how='outer')
    print_df(df_Anl_ActShip, 'df_Anl_ActShip', False)
    
    #step('=====> STEP 3-3 : BOD SET Anl_Act Ship AVG/D.Mode/MAX/MIN Create End')

    #####################################################################################################
    # BOD SET Anl_Act To Port AVG/D.Mode/MAX/MIN 생성 ------------------------------------------------------------
    step('=====> STEP 3-4 : BOD SET Anl_Act To Port AVG/D.Mode/MAX/MIN Create')
    df_LT_SHIPPORT = df_BODACT[(df_BODACT[col_CategoryCategory] == "SHIP-PORT") &
                                df_BODACT[col_LeadTime].notna()].copy()
    df_LT_SHIPPORT['Join_Column'] = 'A'
    df_LT_SHIPPORT_CUR = df_LT_SHIPPORT.merge(df_TMCUR, on='Join_Column', how='inner')
    
    cList_Anl_ActToPortAVG = cList_Anl_group + [col_BODSETAnl_ActToPortAVG]
    cList_Anl_ActToPortMIN = cList_Anl_group + [col_BODSETAnl_ActToPortMIN]
    cList_Anl_ActToPortMAX = cList_Anl_group + [col_BODSETAnl_ActToPortMAX]
    cList_Anl_ActToPortMODE = cList_Anl_group + [col_BODSETAnl_ActToPortD_Mode]
    
    df_Anl_ActToPort_AVG = pd.DataFrame(columns=cList_Anl_ActToPortAVG)  # 빈 dataframe
    df_Anl_ActToPort_MIN = pd.DataFrame(columns=cList_Anl_ActToPortMIN)  # 빈 dataframe
    df_Anl_ActToPort_MAX = pd.DataFrame(columns=cList_Anl_ActToPortMAX)  # 빈 dataframe
    df_Anl_ActToPort_MODE = pd.DataFrame(columns=cList_Anl_ActToPortMODE)  # 빈 dataframe
    
    # note(f'=====> for Start ======================================================= ')
    #df_Anl_ActToPort = pd.DataFrame(columns=cList_Anl_group)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_SHIPPORT_CUR[col_TimePlanningMonth] == df_LT_SHIPPORT_CUR['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_SHIPPORT_CUR[col_TimePlanningMonth] <= df_LT_SHIPPORT_CUR['M0']) & (
                      df_LT_SHIPPORT_CUR[col_TimePlanningMonth] >= df_LT_SHIPPORT_CUR['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_SHIPPORT_CUR[col_TimePlanningMonth] <= df_LT_SHIPPORT_CUR['M0']) & (
                      df_LT_SHIPPORT_CUR[col_TimePlanningMonth] >= df_LT_SHIPPORT_CUR['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_SHIPPORT_CUR[col_TimePlanningMonth] <= df_LT_SHIPPORT_CUR['M0']) & (
                      df_LT_SHIPPORT_CUR[col_TimePlanningMonth] >= df_LT_SHIPPORT_CUR['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_SHIPPORT_CUR[col_TimePlanningMonth] <= df_LT_SHIPPORT_CUR['M0']) & (
                      df_LT_SHIPPORT_CUR[col_TimePlanningMonth] >= df_LT_SHIPPORT_CUR['M-6'])
        
        for sAgg in list_Agg:
            
            df_Ext_Data = df_LT_SHIPPORT_CUR[v_cond].copy()
            
            if not df_Ext_Data.empty:
                df_Ext_Data[col_CategoryCategory] = sMonth
                
                if sAgg == 'Avg':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActToPortAVG] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActToPort_AVG = pd.concat([df_Anl_ActToPort_AVG, df_Ext_Data])
                        
                elif sAgg == 'Min':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].min()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActToPortMIN] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActToPort_MIN = pd.concat([df_Anl_ActToPort_MIN, df_Ext_Data])
                        
                elif sAgg == 'Max':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].max()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActToPortMAX] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActToPort_MAX = pd.concat([df_Anl_ActToPort_MAX, df_Ext_Data])
                        
                elif sAgg == 'Mode':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].apply(max_mode)
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActToPortD_Mode] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActToPort_MODE = pd.concat([df_Anl_ActToPort_MODE, df_Ext_Data])
                
                del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_SHIPPORT_CUR
    df_Anl_ActToPort = df_Anl_ActToPort_AVG.copy()
    df_Anl_ActToPort = df_Anl_ActToPort.merge(df_Anl_ActToPort_MIN, on=cList_Anl_group, how='outer')
    df_Anl_ActToPort = df_Anl_ActToPort.merge(df_Anl_ActToPort_MAX, on=cList_Anl_group, how='outer')
    df_Anl_ActToPort = df_Anl_ActToPort.merge(df_Anl_ActToPort_MODE, on=cList_Anl_group, how='outer')
    print_df(df_Anl_ActToPort, 'df_Anl_ActToPort', False)
    #step('=====> STEP 3-4 : BOD SET Anl_Act To Port AVG/D.Mode/MAX/MIN Create End')

    #####################################################################################################
    # BOD SET Anl_Act GR AVG/D.Mode/MAX/MIN 생성 ------------------------------------------------------------
    step('=====> STEP 3-5 : BOD SET Anl_Act GR AVG/D.Mode/MAX/MIN Create')
    df_LT_PORTGR = df_BODACT[(df_BODACT[col_CategoryCategory] == "PORT-GR") &
                              df_BODACT[col_LeadTime].notna()].copy()
    df_LT_PORTGR['Join_Column'] = 'A'
    df_LT_PORTGR_CUR = df_LT_PORTGR.merge(df_TMCUR, on='Join_Column', how='inner')
    
    cList_Anl_ActGRAVG = cList_Anl_group + [col_BODSETAnl_ActGRAVG]
    cList_Anl_ActGRMIN = cList_Anl_group + [col_BODSETAnl_ActGRMIN]
    cList_Anl_ActGRMAX = cList_Anl_group + [col_BODSETAnl_ActGRMAX]
    cList_Anl_ActGRMODE = cList_Anl_group + [col_BODSETAnl_ActGRD_Mode]
    
    df_Anl_ActGR_AVG = pd.DataFrame(columns=cList_Anl_ActGRAVG)  # 빈 dataframe
    df_Anl_ActGR_MIN = pd.DataFrame(columns=cList_Anl_ActGRMIN)  # 빈 dataframe
    df_Anl_ActGR_MAX = pd.DataFrame(columns=cList_Anl_ActGRMAX)  # 빈 dataframe
    df_Anl_ActGR_MODE = pd.DataFrame(columns=cList_Anl_ActGRMODE)  # 빈 dataframe
    
    # note(f'=====> for Start ======================================================= ')
    #df_Anl_ActGR = pd.DataFrame(columns=cList_Anl_group)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_PORTGR_CUR[col_TimePlanningMonth] == df_LT_PORTGR_CUR['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_PORTGR_CUR[col_TimePlanningMonth] <= df_LT_PORTGR_CUR['M0']) & (
                      df_LT_PORTGR_CUR[col_TimePlanningMonth] >= df_LT_PORTGR_CUR['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_PORTGR_CUR[col_TimePlanningMonth] <= df_LT_PORTGR_CUR['M0']) & (
                      df_LT_PORTGR_CUR[col_TimePlanningMonth] >= df_LT_PORTGR_CUR['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_PORTGR_CUR[col_TimePlanningMonth] <= df_LT_PORTGR_CUR['M0']) & (
                      df_LT_PORTGR_CUR[col_TimePlanningMonth] >= df_LT_PORTGR_CUR['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_PORTGR_CUR[col_TimePlanningMonth] <= df_LT_PORTGR_CUR['M0']) & (
                      df_LT_PORTGR_CUR[col_TimePlanningMonth] >= df_LT_PORTGR_CUR['M-6'])
        
        for sAgg in list_Agg:
            
            df_Ext_Data = df_LT_PORTGR_CUR[v_cond]
            
            if not df_Ext_Data.empty:
                df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
                
                if sAgg == 'Avg':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActGRAVG] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActGR_AVG = pd.concat([df_Anl_ActGR_AVG, df_Ext_Data])
                        
                elif sAgg == 'Min':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].min()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActGRMIN] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActGR_MIN = pd.concat([df_Anl_ActGR_MIN, df_Ext_Data])
                        
                elif sAgg == 'Max':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].max()
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActGRMAX] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActGR_MAX = pd.concat([df_Anl_ActGR_MAX, df_Ext_Data])
                        
                elif sAgg == 'Mode':
                    df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].apply(max_mode)
                    if not df_Ext_Data.empty:
                        df_Ext_Data[col_BODSETAnl_ActGRD_Mode] = df_Ext_Data[col_LeadTime].astype('int64')
                        df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
                        df_Anl_ActGR_MODE = pd.concat([df_Anl_ActGR_MODE, df_Ext_Data])
                
                del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_PORTGR_CUR
    df_Anl_ActGR = df_Anl_ActGR_AVG.copy()
    df_Anl_ActGR = df_Anl_ActGR.merge(df_Anl_ActGR_MIN, on=cList_Anl_group, how='outer')
    df_Anl_ActGR = df_Anl_ActGR.merge(df_Anl_ActGR_MAX, on=cList_Anl_group, how='outer')
    df_Anl_ActGR = df_Anl_ActGR.merge(df_Anl_ActGR_MODE, on=cList_Anl_group, how='outer')
    print_df(df_Anl_ActGR, 'df_Anl_ActGR', False)
    #step('=====> STEP 3-5 : BOD SET Anl_Act GR AVG/D.Mode/MAX/MIN Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act TTL AVG/D.Mode/MAX/MIN Create 생성 ------------------------------------------------------------
    step('=====> STEP 3-6 : BOD SET Anl_Act TTL AVG/D.Mode/MAX/MIN Create')
    df_Anl_ActTTL = df_Anl_ActShip.copy()
    df_Anl_ActTTL = df_Anl_ActTTL.merge(df_Anl_ActToPort, on=cList_Anl_group, how='outer')
    df_Anl_ActTTL = df_Anl_ActTTL.merge(df_Anl_ActGR, on=cList_Anl_group, how='outer')
    del [df_Anl_ActShip, df_Anl_ActToPort, df_Anl_ActGR]
    
    df_Anl_ActTTL[col_BODSETAnl_ActTTLAVG] = (df_Anl_ActTTL[col_BODSETAnl_ActShipAVG].fillna(0) +
                                              df_Anl_ActTTL[col_BODSETAnl_ActToPortAVG].fillna(0) +
                                              df_Anl_ActTTL[col_BODSETAnl_ActGRAVG].fillna(0) )
    df_Anl_ActTTL[col_BODSETAnl_ActTTLMIN] = (df_Anl_ActTTL[col_BODSETAnl_ActShipMIN].fillna(0) +
                                              df_Anl_ActTTL[col_BODSETAnl_ActToPortMIN].fillna(0) +
                                              df_Anl_ActTTL[col_BODSETAnl_ActGRMIN].fillna(0) )
    df_Anl_ActTTL[col_BODSETAnl_ActTTLMAX] = (df_Anl_ActTTL[col_BODSETAnl_ActShipMAX].fillna(0) +
                                              df_Anl_ActTTL[col_BODSETAnl_ActToPortMAX].fillna(0) +
                                              df_Anl_ActTTL[col_BODSETAnl_ActGRMAX].fillna(0) )
    df_Anl_ActTTL[col_BODSETAnl_ActTTLD_MODE] = (df_Anl_ActTTL[col_BODSETAnl_ActShipD_Mode].fillna(0) +
                                                 df_Anl_ActTTL[col_BODSETAnl_ActToPortD_Mode].fillna(0) +
                                                 df_Anl_ActTTL[col_BODSETAnl_ActGRD_Mode].fillna(0) )
    print_df(df_Anl_ActTTL, 'df_Anl_ActTTL', False)
    #step('=====> STEP 3-6 : BOD SET Anl_Act TTL AVG/D.Mode/MAX/MIN Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act Ship Pre Month 생성 ------------------------------------------------------------
    step('=====> STEP 3-7 : BOD SET Anl_Act Ship Pre Month Create')
    #전월 기준으로 동일 로직 적용
    cList_Anl_ShipPre = cList_Anl_group + [col_BODSETAnl_ActShipPreMonth]
    df_LT_Ship_Pre = df_LT_MFGSHIP.merge(df_TMCUR_Pre, on='Join_Column', how='inner')
    #del df_LT_MFGSHIP
    #print_df(df_LT_Ship_Pre, 'df_LT_Ship_Pre', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_Anl_ActShipPreMonth = pd.DataFrame(columns=cList_Anl_ShipPre)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_Ship_Pre[col_TimePlanningMonth] == df_LT_Ship_Pre['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_Ship_Pre[col_TimePlanningMonth] <= df_LT_Ship_Pre['M0']) & (
                      df_LT_Ship_Pre[col_TimePlanningMonth] >= df_LT_Ship_Pre['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_Ship_Pre[col_TimePlanningMonth] <= df_LT_Ship_Pre['M0']) & (
                      df_LT_Ship_Pre[col_TimePlanningMonth] >= df_LT_Ship_Pre['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_Ship_Pre[col_TimePlanningMonth] <= df_LT_Ship_Pre['M0']) & (
                      df_LT_Ship_Pre[col_TimePlanningMonth] >= df_LT_Ship_Pre['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_Ship_Pre[col_TimePlanningMonth] <= df_LT_Ship_Pre['M0']) & (
                      df_LT_Ship_Pre[col_TimePlanningMonth] >= df_LT_Ship_Pre['M-6'])
                
        df_Ext_Data = df_LT_Ship_Pre[v_cond]
        df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
        df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
        
        if not df_Ext_Data.empty:
            df_Ext_Data[col_BODSETAnl_ActShipPreMonth] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
            df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
            df_Anl_ActShipPreMonth = pd.concat([df_Anl_ActShipPreMonth, df_Ext_Data])
            del df_Ext_Data
           
    # note(f'=====> for End ======================================================= ')
    del df_LT_Ship_Pre
    print_df(df_Anl_ActShipPreMonth, 'df_Anl_ActShipPreMonth', False)
    #step('=====> STEP 3-7 : BOD SET Anl_Act Ship Pre Month Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act To Port Pre Month 생성 ------------------------------------------------------------
    step('=====> STEP 3-8 : BOD SET Anl_Act To Port Pre Month Create')
    # 전월 기준으로 동일 로직 적용
    cList_Anl_ToPortPre = cList_Anl_group + [col_BODSETAnl_ActToPortPreMonth]
    df_LT_SHIPPORT_Pre = df_LT_SHIPPORT.merge(df_TMCUR_Pre, on='Join_Column', how='inner')
    #del df_LT_SHIPPORT
    print_df(df_LT_SHIPPORT_Pre, 'df_LT_SHIPPORT_Pre', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_Anl_ActToPortPreMonth = pd.DataFrame(columns=cList_Anl_ToPortPre)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_SHIPPORT_Pre[col_TimePlanningMonth] == df_LT_SHIPPORT_Pre['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_SHIPPORT_Pre[col_TimePlanningMonth] <= df_LT_SHIPPORT_Pre['M0']) & (
                      df_LT_SHIPPORT_Pre[col_TimePlanningMonth] >= df_LT_SHIPPORT_Pre['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_SHIPPORT_Pre[col_TimePlanningMonth] <= df_LT_SHIPPORT_Pre['M0']) & (
                      df_LT_SHIPPORT_Pre[col_TimePlanningMonth] >= df_LT_SHIPPORT_Pre['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_SHIPPORT_Pre[col_TimePlanningMonth] <= df_LT_SHIPPORT_Pre['M0']) & (
                      df_LT_SHIPPORT_Pre[col_TimePlanningMonth] >= df_LT_SHIPPORT_Pre['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_SHIPPORT_Pre[col_TimePlanningMonth] <= df_LT_SHIPPORT_Pre['M0']) & (
                      df_LT_SHIPPORT_Pre[col_TimePlanningMonth] >= df_LT_SHIPPORT_Pre['M-6'])
        
        df_Ext_Data = df_LT_SHIPPORT_Pre[v_cond]
        df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
        df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
        
        if not df_Ext_Data.empty:
            df_Ext_Data[col_BODSETAnl_ActToPortPreMonth] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
            df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
            df_Anl_ActToPortPreMonth = pd.concat([df_Anl_ActToPortPreMonth, df_Ext_Data])
            del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_SHIPPORT_Pre
    print_df(df_Anl_ActToPortPreMonth, 'df_Anl_ActToPortPreMonth', False)
    #step('=====> STEP 3-8 : BOD SET Anl_Act To Port Pre Month Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act GR Pre Month 생성 ------------------------------------------------------------
    step('=====> STEP 3-9 : BOD SET Anl_Act GR Pre Month Create')
    # 전월 기준으로 동일 로직 적용
    cList_Anl_GRPre = cList_Anl_group + [col_BODSETAnl_ActGRPreMonth]
    df_LT_PORTGR_Pre = df_LT_PORTGR.merge(df_TMCUR_Pre, on='Join_Column', how='inner')
    #del df_LT_PORTGR
    print_df(df_LT_PORTGR_Pre, 'df_LT_PORTGR_Pre', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_Anl_ActGRPreMonth = pd.DataFrame(columns=cList_Anl_GRPre)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_PORTGR_Pre[col_TimePlanningMonth] == df_LT_PORTGR_Pre['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_PORTGR_Pre[col_TimePlanningMonth] <= df_LT_PORTGR_Pre['M0']) & (
                      df_LT_PORTGR_Pre[col_TimePlanningMonth] >= df_LT_PORTGR_Pre['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_PORTGR_Pre[col_TimePlanningMonth] <= df_LT_PORTGR_Pre['M0']) & (
                      df_LT_PORTGR_Pre[col_TimePlanningMonth] >= df_LT_PORTGR_Pre['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_PORTGR_Pre[col_TimePlanningMonth] <= df_LT_PORTGR_Pre['M0']) & (
                      df_LT_PORTGR_Pre[col_TimePlanningMonth] >= df_LT_PORTGR_Pre['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_PORTGR_Pre[col_TimePlanningMonth] <= df_LT_PORTGR_Pre['M0']) & (
                      df_LT_PORTGR_Pre[col_TimePlanningMonth] >= df_LT_PORTGR_Pre['M-6'])
        
        df_Ext_Data = df_LT_PORTGR_Pre[v_cond]
        df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
        df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
        
        if not df_Ext_Data.empty:
            df_Ext_Data[col_BODSETAnl_ActGRPreMonth] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
            df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
            df_Anl_ActGRPreMonth = pd.concat([df_Anl_ActGRPreMonth, df_Ext_Data])
            del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_PORTGR_Pre
    print_df(df_Anl_ActGRPreMonth, 'df_Anl_ActGRPreMonth', False)
    #step('=====> STEP 3-9 : BOD SET Anl_Act GR Pre Month Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act TTL Pre Month 생성 ------------------------------------------------------------
    step('=====> STEP 3-10 : BOD SET Anl_Act TTL Pre Month Create')
    df_Anl_ActPreMonth = df_Anl_ActShipPreMonth.copy()
    df_Anl_ActPreMonth = df_Anl_ActPreMonth.merge(df_Anl_ActToPortPreMonth, on=cList_Anl_group, how='outer')
    df_Anl_ActPreMonth = df_Anl_ActPreMonth.merge(df_Anl_ActGRPreMonth, on=cList_Anl_group, how='outer')
    del [df_Anl_ActShipPreMonth, df_Anl_ActToPortPreMonth, df_Anl_ActGRPreMonth, df_TMCUR_Pre]
    df_Anl_ActPreMonth[col_BODSETAnl_ActTTLPreMonth] = (df_Anl_ActPreMonth[col_BODSETAnl_ActShipPreMonth].fillna(0) +
                                                        df_Anl_ActPreMonth[col_BODSETAnl_ActToPortPreMonth].fillna(0) +
                                                        df_Anl_ActPreMonth[col_BODSETAnl_ActGRPreMonth].fillna(0)
                                                        )
    print_df(df_Anl_ActPreMonth, 'df_Anl_ActPreMonth', False)
    
    #step('=====> STEP 3-10 : BOD SET Anl_Act TTL Pre Month Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act Ship Last Year 생성 ------------------------------------------------------------#2025.10.29 추가
    step('=====> STEP 3-11 : BOD SET Anl_Act Ship Last Year Create')
    # 전년 기준으로 동일 로직 적용
    cList_Anl_ShipLastYear = cList_Anl_group + [col_BODSETAnl_ActShipLastYear]
    df_LT_Ship_LastYear = df_LT_MFGSHIP.merge(df_TMCUR_LastYear, on='Join_Column', how='inner')
    del df_LT_MFGSHIP
    print_df(df_LT_Ship_LastYear, 'df_LT_Ship_LastYear', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_Anl_ActShipLastYear = pd.DataFrame(columns=cList_Anl_ShipLastYear)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_Ship_LastYear[col_TimePlanningMonth] == df_LT_Ship_LastYear['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_Ship_LastYear[col_TimePlanningMonth] <= df_LT_Ship_LastYear['M0']) & (
                      df_LT_Ship_LastYear[col_TimePlanningMonth] >= df_LT_Ship_LastYear['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_Ship_LastYear[col_TimePlanningMonth] <= df_LT_Ship_LastYear['M0']) & (
                      df_LT_Ship_LastYear[col_TimePlanningMonth] >= df_LT_Ship_LastYear['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_Ship_LastYear[col_TimePlanningMonth] <= df_LT_Ship_LastYear['M0']) & (
                      df_LT_Ship_LastYear[col_TimePlanningMonth] >= df_LT_Ship_LastYear['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_Ship_LastYear[col_TimePlanningMonth] <= df_LT_Ship_LastYear['M0']) & (
                      df_LT_Ship_LastYear[col_TimePlanningMonth] >= df_LT_Ship_LastYear['M-6'])
        
        df_Ext_Data = df_LT_Ship_LastYear[v_cond]
        df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
        df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
        
        if not df_Ext_Data.empty:
            df_Ext_Data[col_BODSETAnl_ActShipLastYear] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
            df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
            df_Anl_ActShipPLastYear = pd.concat([df_Anl_ActShipLastYear, df_Ext_Data])
            del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_Ship_LastYear
    print_df(df_Anl_ActShipLastYear, 'df_Anl_ActShipLastYear', False)
    # step('=====> STEP 3-11 : BOD SET Anl_Act Ship Last Year Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act To Port Last Year 생성 ----------------------------------------------------------#2025.10.29 추가
    step('=====> STEP 3-12 : BOD SET Anl_Act To Port Last Year Create')
    # 전년 기준으로 동일 로직 적용
    cList_Anl_ToPortLastYear = cList_Anl_group + [col_BODSETAnl_ActToPortLastYear]
    df_LT_SHIPPORT_LastYear = df_LT_SHIPPORT.merge(df_TMCUR_LastYear, on='Join_Column', how='inner')
    del df_LT_SHIPPORT
    print_df(df_LT_SHIPPORT_LastYear, 'df_LT_SHIPPORT_LastYear', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_Anl_ActToPortLastYear = pd.DataFrame(columns=cList_Anl_ToPortLastYear)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] == df_LT_SHIPPORT_LastYear['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] <= df_LT_SHIPPORT_LastYear['M0']) & (
                df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] >= df_LT_SHIPPORT_LastYear['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] <= df_LT_SHIPPORT_LastYear['M0']) & (
                df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] >= df_LT_SHIPPORT_LastYear['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] <= df_LT_SHIPPORT_LastYear['M0']) & (
                df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] >= df_LT_SHIPPORT_LastYear['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] <= df_LT_SHIPPORT_LastYear['M0']) & (
                df_LT_SHIPPORT_LastYear[col_TimePlanningMonth] >= df_LT_SHIPPORT_LastYear['M-6'])
        
        df_Ext_Data = df_LT_SHIPPORT_LastYear[v_cond]
        df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
        df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
        
        if not df_Ext_Data.empty:
            df_Ext_Data[col_BODSETAnl_ActToPortLastYear] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
            df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
            df_Anl_ActToPortLastYear = pd.concat([df_Anl_ActToPortLastYear, df_Ext_Data])
            del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_SHIPPORT_LastYear
    print_df(df_Anl_ActToPortLastYear, 'df_Anl_ActToPortLastYear', False)
    # step('=====> STEP 3-12 : BOD SET Anl_Act To Port Last Year Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act GR Last Year 생성 ------------------------------------------------------------#2025.10.29 추가
    step('=====> STEP 3-13 : BOD SET Anl_Act GR Last Year Create')
    # 전년 기준으로 동일 로직 적용
    cList_Anl_GRLastYear = cList_Anl_group + [col_BODSETAnl_ActGRLastYear]
    df_LT_PORTGR_LastYear = df_LT_PORTGR.merge(df_TMCUR_LastYear, on='Join_Column', how='inner')
    del df_LT_PORTGR
    print_df(df_LT_PORTGR_LastYear, 'df_LT_PORTGR_LastYear', False)
    
    # note(f'=====> for Start ======================================================= ')
    df_Anl_ActGRLastYear = pd.DataFrame(columns=cList_Anl_GRLastYear)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_LT_PORTGR_LastYear[col_TimePlanningMonth] == df_LT_PORTGR_LastYear['M0']
        elif sMonth == 'M-1':
            v_cond = (df_LT_PORTGR_LastYear[col_TimePlanningMonth] <= df_LT_PORTGR_LastYear['M0']) & (
                df_LT_PORTGR_LastYear[col_TimePlanningMonth] >= df_LT_PORTGR_LastYear['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_LT_PORTGR_LastYear[col_TimePlanningMonth] <= df_LT_PORTGR_LastYear['M0']) & (
                df_LT_PORTGR_LastYear[col_TimePlanningMonth] >= df_LT_PORTGR_LastYear['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_LT_PORTGR_LastYear[col_TimePlanningMonth] <= df_LT_PORTGR_LastYear['M0']) & (
                df_LT_PORTGR_LastYear[col_TimePlanningMonth] >= df_LT_PORTGR_LastYear['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_LT_PORTGR_LastYear[col_TimePlanningMonth] <= df_LT_PORTGR_LastYear['M0']) & (
                df_LT_PORTGR_LastYear[col_TimePlanningMonth] >= df_LT_PORTGR_LastYear['M-6'])
        
        df_Ext_Data = df_LT_PORTGR_LastYear[v_cond]
        df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
        df_Ext_Data = df_Ext_Data.groupby(cList_Anl_group, as_index=False)[col_LeadTime].mean()
        
        if not df_Ext_Data.empty:
            df_Ext_Data[col_BODSETAnl_ActGRLastYear] = df_Ext_Data[col_LeadTime].round(0).astype('int64')
            df_Ext_Data.drop(columns=[col_LeadTime], inplace=True)
            df_Anl_ActGRLastYear = pd.concat([df_Anl_ActGRLastYear, df_Ext_Data])
            del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_LT_PORTGR_LastYear
    print_df(df_Anl_ActGRLastYear, 'df_Anl_ActGRLastYear', False)
    # step('=====> STEP 3-13 : BOD SET Anl_Act GR Last Year Create End')
    
    #####################################################################################################
    # BOD SET Anl_Act TTL Last Year 생성 ------------------------------------------------------------#2025.10.29 추가
    step('=====> STEP 3-14 : BOD SET Anl_Act TTL Last Year Create')
    df_Anl_ActLastYear = df_Anl_ActShipLastYear.copy()
    df_Anl_ActLastYear = df_Anl_ActLastYear.merge(df_Anl_ActToPortLastYear, on=cList_Anl_group, how='outer')
    df_Anl_ActLastYear = df_Anl_ActLastYear.merge(df_Anl_ActGRLastYear, on=cList_Anl_group, how='outer')
    del [df_Anl_ActShipLastYear, df_Anl_ActToPortLastYear, df_Anl_ActGRLastYear, df_TMCUR_LastYear]
    df_Anl_ActLastYear[col_BODSETAnl_ActTTLLastYear] = (df_Anl_ActLastYear[col_BODSETAnl_ActShipLastYear].fillna(0) +
                                                        df_Anl_ActLastYear[col_BODSETAnl_ActToPortLastYear].fillna(0) +
                                                        df_Anl_ActLastYear[col_BODSETAnl_ActGRLastYear].fillna(0)
                                                        )
    print_df(df_Anl_ActLastYear, 'df_Anl_ActLastYear', False)
    
    # step('=====> STEP 3-14 : BOD SET Anl_Act TTL Last Year Create End')
    
    #####################################################################################################
    # BOD SET Anl_TTL Plan 생성 ------------------------------------------------------------
    step('=====> STEP 3-15 : BOD SET Anl_BOD/Ship/TTL Plan Create')
    #[BOD SET Anl LT_BOD Plan], [BOD SET Anl LT_Ship Plan] 값 중 Aggregate.[Aggregate] == "Avg" 인 값만 생성
    df_Anl_TTLPlan = df_LT_TotalPlan[df_LT_TotalPlan[col_AggregateAggregate] == "Avg"].copy()
    del df_LT_TotalPlan
    df_Anl_TTLPlan.drop(columns=[col_AggregateAggregate], inplace=True)
    df_Anl_TTLPlan.rename(columns={col_BODSETAnlLT_BODPlan:col_BODSETAnl_BODPlan,
                                   col_BODSETAnlLT_ShipPlan:col_BODSETAnl_ShipPlan,
                                   col_BODSETAnlLT_TotalPlan:col_BODSETAnl_TTLPlan}, inplace=True)
    
    print_df(df_Anl_TTLPlan, 'df_Anl_TTLPlan', False)
    
    #step('=====> STEP 3-15 : BOD SET Anl_TTL Plan Create End')
    
    ################################################################################################################
    # STEP 4 :  BOD Set Anl 생성(BODACT2)
    ################################################################################################################
    #####################################################################################################
    # BOD SET Anl_INVO/before Wed Arrival INVO/before Wed Arrival INVO 생성 ------------------------------------------------------------
    step('=====> STEP 4-1 : BOD SET Anl_INVO/Qty, before Wed Arrival INVO/Qty Create')
    #df_BODACT2[col_CategoryCategory]   = 'M0'
    df_BODACT2[col_TransModeTransMode] = 'VESSEL'
    
    # M0, M-1, M-2, M-3, M-6 생성되도록 수정 : 2025.11.13 추가.
    df_BODACT2['Join_Column'] = 'A'
    df_BODACT2 = df_BODACT2.merge(df_TMCUR, on='Join_Column', how='inner')
    print_df(df_BODACT2, 'df_BODACT2 TMCUR', False)
    
    cList_BODACT2_CTG = cList_group + [col_TransModeTransMode, col_CategoryCategory, col_BODActAnl_GRDate,
                                       col_BODActAnl_GRQty, col_GR_WEEK, col_GR_DayofWeek, col_TimePlanningMonth,
                                       col_ETAPre1W, col_ETAPre2W, col_ETAlate1W, col_ETAlate2W]
    
    # note(f'=====> for Start ======================================================= ')
    df_BODACT2_CTG = pd.DataFrame(columns=cList_BODACT2_CTG)  # 빈 dataframe
    for sMonth in list_Month:
        if sMonth == 'M0':
            v_cond = df_BODACT2[col_TimePlanningMonth] == df_BODACT2['M0']
        elif sMonth == 'M-1':
            v_cond = (df_BODACT2[col_TimePlanningMonth] <= df_BODACT2['M0']) & (
                      df_BODACT2[col_TimePlanningMonth] >= df_BODACT2['M-1'])
        elif sMonth == 'M-2':
            v_cond = (df_BODACT2[col_TimePlanningMonth] <= df_BODACT2['M0']) & (
                      df_BODACT2[col_TimePlanningMonth] >= df_BODACT2['M-2'])
        elif sMonth == 'M-3':
            v_cond = (df_BODACT2[col_TimePlanningMonth] <= df_BODACT2['M0']) & (
                      df_BODACT2[col_TimePlanningMonth] >= df_BODACT2['M-3'])
        elif sMonth == 'M-6':
            v_cond = (df_BODACT2[col_TimePlanningMonth] <= df_BODACT2['M0']) & (
                      df_BODACT2[col_TimePlanningMonth] >= df_BODACT2['M-6'])
        
        df_Ext_Data = df_BODACT2[v_cond]
        
        if not df_Ext_Data.empty:
            df_Ext_Data.loc[:, col_CategoryCategory] = sMonth
            df_BODACT2_CTG = pd.concat([df_BODACT2_CTG, df_Ext_Data])
            del df_Ext_Data
    
    # note(f'=====> for End ======================================================= ')
    del df_BODACT2
    df_BODACT2_CTG = df_BODACT2_CTG.reset_index(drop=True)
    print_df(df_BODACT2_CTG, 'df_BODACT2_CTG', False)
    
    df_Anl_INVO_Qty = df_BODACT2_CTG.copy()    
    df_Anl_INVO_Qty = df_Anl_INVO_Qty.groupby(cList_Anl_group, as_index=False).agg(
                                total_count=(col_BODActAnl_GRDate, 'count'), # 전체건수
                                M_T_day_count=(col_GR_DayofWeek, lambda x: (x.isin(['MON', 'TUE'])).sum()), #월,화 건수
                                total_qty=(col_BODActAnl_GRQty,'sum'), # 전체 Qty
                                M_T_day_Qty=(col_BODActAnl_GRQty, 
                                  lambda x: x[df_Anl_INVO_Qty.loc[x.index,col_GR_DayofWeek].isin(['MON', 'TUE'])].sum())
                               ) 
    # Count()   
    df_Anl_INVO_Qty[col_BODSETAnl_INVO] = df_Anl_INVO_Qty['total_count'].astype('int64')     
    # Count(Time.[Day of Week] in ("MON", "TUE")) / [BOD SET Anl_INVO]
    df_Anl_INVO_Qty[col_BODSETAnl_beforeWedArrivalINVO] = (df_Anl_INVO_Qty['M_T_day_count'] / 
                                                           df_Anl_INVO_Qty['total_count']).round(0).astype('int64') 
                                                           #Data Type : integer
    
    #Sum(GR_QTY)
    df_Anl_INVO_Qty[col_BODSETAnl_Qty] = df_Anl_INVO_Qty['total_qty'].astype('int64')
    #Sum(GR_QTY) Where Time.[Day of Week] in ("MON", "TUE") / [BOD SET Anl_Qty]
    df_Anl_INVO_Qty[col_BODSETAnl_beforeWedArrivalQty] = (df_Anl_INVO_Qty['M_T_day_Qty'] /
                                                          df_Anl_INVO_Qty['total_qty']).round(0).astype('int64')  
                                                          # Data Type : integer
    
    df_Anl_INVO_Qty.drop(columns=['total_count', 'M_T_day_count', 'total_qty', 'M_T_day_Qty'], inplace=True)
    
    print_df(df_Anl_INVO_Qty, 'df_Anl_INVO_Qty', False)
    #step('=====> STEP 4-1 : BOD SET Anl_INVO/Qty, before Wed Arrival INVO/Qty Create End')
    
    #####################################################################################################
    # BOD SET Anl_JIT INVO 생성 ------------------------------------------------------------
    step('=====> STEP 4-2 : BOD SET Anl_JIT INVO/Qty Create')
    # Ontime : (ETA 주차 == GR 주차) or (ETA 1전 주차 == GR 주차 & 목,금,토,일)
    list_DayofWeek_front = ['MON', 'TUE', 'WED']
    list_DayofWeek_rear  = ['THU', 'FRI', 'SAT', 'SUN']
    
    df_Anl_JITINVO_Qty = df_BODACT2_CTG[(df_BODACT2_CTG[col_ETA_WEEK] == df_BODACT2_CTG[col_GR_WEEK]) |
                                ((df_BODACT2_CTG[col_ETAPre1W] == df_BODACT2_CTG[col_GR_WEEK]) &
                                 (df_BODACT2_CTG[col_GR_DayofWeek].isin(list_DayofWeek_rear)) )].copy()
    
    df_Anl_JITINVO_Qty = df_Anl_JITINVO_Qty.groupby(cList_Anl_group, as_index=False).agg(
                                                                      gr_Count=(col_BODActAnl_GRDate, 'count'),  # 건수
                                                                      gr_Qty=(col_BODActAnl_GRQty,'sum'),  # sum Qty
                                                                      )
    df_Anl_JITINVO_Qty[col_BODSETAnl_JITINVO] = df_Anl_JITINVO_Qty['gr_Count'].astype('int64')
    df_Anl_JITINVO_Qty[col_BODSETAnl_JITQty] = df_Anl_JITINVO_Qty['gr_Qty'].astype('int64')
    df_Anl_JITINVO_Qty.drop(columns=['gr_Count', 'gr_Qty'], inplace=True)
    
    print_df(df_Anl_JITINVO_Qty, 'df_Anl_JITINVO_Qty', False)
    #step('=====> STEP 4-2 : BOD SET Anl_JIT INVO/Qty Create End')
    
    #####################################################################################################
    # BOD SET Anl_Frequent Day INVO 생성 ------------------------------------------------------------
    step('=====> STEP 4-3 : BOD SET Anl_Frequent Day INVO Create')
    # Mode(Time.[Day of Week])
    df_FrequentDay_INVO = df_BODACT2_CTG.copy()
    if df_FrequentDay_INVO.empty:
        cList_Anl_temp = cList_Anl_group + [col_GR_DayofWeek]
        df_FrequentDay_INVO = df_FrequentDay_INVO[cList_Anl_temp]        
    else:
        df_FrequentDay_INVO = df_FrequentDay_INVO.groupby(cList_Anl_group, as_index=False)[col_GR_DayofWeek].agg(lambda x: x.mode()[0])
    
    df_FrequentDay_INVO[col_BODSETAnl_FrequentDayINVO] = df_FrequentDay_INVO[col_GR_DayofWeek]
    df_FrequentDay_INVO.drop(columns=[col_GR_DayofWeek], inplace=True)
    
    print_df(df_FrequentDay_INVO, 'df_FrequentDay_INVO', False)
    #step('=====> STEP 4-3 : BOD SET Anl_Frequent Day INVO Create End')
    
    #####################################################################################################
    # BOD SET Anl_Pre Arrival 1W INVO/Qty 생성 ------------------------------------------------------------
    step('=====> STEP 4-4 : BOD SET Anl_Pre Arrival 1W INVO/Qty Create')
    # 1주 선행 : (ETA 1전 주차 == GR 주차 & 월, 화, 수)    
    df_Anl_Pre_1W = df_BODACT2_CTG[(df_BODACT2_CTG[col_ETAPre1W] == df_BODACT2_CTG[col_GR_WEEK]) &
                               (df_BODACT2_CTG[col_GR_DayofWeek].isin(list_DayofWeek_front)) ].copy()
    
    df_Anl_Pre_1W = df_Anl_Pre_1W.groupby(cList_Anl_group, as_index=False).agg(
                                                                      gr_Count=(col_BODActAnl_GRDate, 'count'),  # 건수
                                                                      gr_Qty=(col_BODActAnl_GRQty, 'sum'),  # sum Qty
                                                                      )
    
    df_Anl_Pre_1W[col_BODSETAnl_PreArrival1WINVO] = df_Anl_Pre_1W['gr_Count'].astype('int64')
    df_Anl_Pre_1W[col_BODSETAnl_PreArrival1WQty] = df_Anl_Pre_1W['gr_Qty'].astype('int64')
    df_Anl_Pre_1W.drop(columns=['gr_Count', 'gr_Qty'], inplace=True)
    
    print_df(df_Anl_Pre_1W, 'df_Anl_Pre_1W', False)
    
    #step('=====> STEP 4-4 : BOD SET Anl_Pre Arrival 1W INVO/Qty Create End')
    
    #####################################################################################################
    # BOD SET Anl_Pre Arrival 2W INVO/Qty 생성 ------------------------------------------------------------
    step('=====> STEP 4-5 : BOD SET Anl_Pre Arrival 2W INVO INVO/Qty Create')
    # 2주 이상 선행 : (ETA 2전 주차 >= GR 주차)
    df_Anl_Pre_2W = df_BODACT2_CTG[(df_BODACT2_CTG[col_ETAPre2W] >= df_BODACT2_CTG[col_GR_WEEK])].copy()
    
    df_Anl_Pre_2W = df_Anl_Pre_2W.groupby(cList_Anl_group, as_index=False).agg(
                                                                      gr_Count=(col_BODActAnl_GRDate, 'count'),  # 건수
                                                                      gr_Qty=(col_BODActAnl_GRQty, 'sum'),  # sum Qty
                                                                      )
    df_Anl_Pre_2W[col_BODSETAnl_PreArrival2WINVO] = df_Anl_Pre_2W['gr_Count'].astype('int64')
    df_Anl_Pre_2W[col_BODSETAnl_PreArrival2WQty] = df_Anl_Pre_2W['gr_Qty'].astype('int64')    
    df_Anl_Pre_2W.drop(columns=['gr_Count', 'gr_Qty'], inplace=True)
    
    print_df(df_Anl_Pre_2W, 'df_Anl_Pre_2W', False)
    
    #step('=====> STEP 4-5 : BOD SET Anl_Pre Arrival 2W INVO INVO/Qty Create End')
    
    #####################################################################################################
    # BOD SET Anl_late Arrival 1W INVO/Qty 생성 ------------------------------------------------------------
    step('=====> STEP 4-6 : BOD SET Anl_late Arrival 1W INVO/Qty Create')
    # 1주 지연 : (ETA 1후 주차 == GR 주차) 
    df_Anl_late_1W = df_BODACT2_CTG[(df_BODACT2_CTG[col_ETAlate1W] == df_BODACT2_CTG[col_GR_WEEK])].copy()
    
    df_Anl_late_1W = df_Anl_late_1W.groupby(cList_Anl_group, as_index=False).agg(
                                                                      gr_Count=(col_BODActAnl_GRDate, 'count'),  # 건수
                                                                      gr_Qty=(col_BODActAnl_GRQty, 'sum'),  # sum Qty
                                                                      )
    df_Anl_late_1W[col_BODSETAnl_lateArrival1WINVO] = df_Anl_late_1W['gr_Count'].astype('int64')
    df_Anl_late_1W[col_BODSETAnl_lateArrival1WQty] = df_Anl_late_1W['gr_Qty'].astype('int64')
    df_Anl_late_1W.drop(columns=['gr_Count', 'gr_Qty'], inplace=True)
    
    print_df(df_Anl_late_1W, 'df_Anl_late_1W', False)
    
    #step('=====> STEP 4-6 : BOD SET Anl_late Arrival 1W INVO/Qty Create End')
    
    #####################################################################################################
    # BOD SET Anl_late Arrival 2W INVO/Qty 생성 ------------------------------------------------------------
    step('=====> STEP 4-7 : BOD SET Anl_late Arrival 2W INVO/Qty Create')
    # 2주 이상 지연 : (ETA 2후 주차 <= GR 주차)
    df_Anl_late_2W = df_BODACT2_CTG[(df_BODACT2_CTG[col_ETAlate2W] <= df_BODACT2_CTG[col_GR_WEEK])].copy()
    
    df_Anl_late_2W = df_Anl_late_2W.groupby(cList_Anl_group, as_index=False).agg(
                                                                      gr_Count=(col_BODActAnl_GRDate, 'count'),  # 건수
                                                                      gr_Qty=(col_BODActAnl_GRQty, 'sum'),  # sum Qty
                                                                      )
    
    df_Anl_late_2W[col_BODSETAnl_lateArrival2WINVO] = df_Anl_late_2W['gr_Count'].astype('int64')
    df_Anl_late_2W[col_BODSETAnl_lateArrival2WQty] = df_Anl_late_2W['gr_Qty'].astype('int64')
    df_Anl_late_2W.drop(columns=['gr_Count', 'gr_Qty'], inplace=True)
    
    print_df(df_Anl_late_2W, 'df_Anl_late_2W', False)
    
    #step('=====> STEP 4-7 : BOD SET Anl_late Arrival 2W INVO/Qty Create End')
    
    #####################################################################################################
    # BOD SET Anl_Frequent Day Qty 생성 ------------------------------------------------------------
    # Time.[Day of Week] Where Max(GR_QTY))
    step('=====> STEP 4-8 : BOD SET Anl_Frequent Day Qty Create')
    cList_Anl_DayQty = cList_Anl_group + [col_BODActAnl_GRDate, col_GR_DayofWeek, col_BODActAnl_GRQty]
    
    df_AnlFrequentDay_Qty = df_BODACT2_CTG[cList_Anl_DayQty].copy()
    df_AnlFrequentDay_Qty['MAX_QTY'] = df_AnlFrequentDay_Qty.groupby(cList_Anl_group)[col_BODActAnl_GRQty].transform('max')
    #df_AnlFrequentDay_Qty['SUM_QTY'] = df_AnlFrequentDay_Qty.groupby(cList_Anl_group)[col_BODActAnl_GRQty].transform('sum')
    df_AnlFrequentDay_Qty['dayofweek2'] = df_AnlFrequentDay_Qty[col_BODActAnl_GRDate].dt.dayofweek
    #print_df(df_AnlFrequentDay_Qty, 'df_AnlFrequentDay_Qty org', False)
    
    df_max_qty_days = df_AnlFrequentDay_Qty[df_AnlFrequentDay_Qty[col_BODActAnl_GRQty] == df_AnlFrequentDay_Qty['MAX_QTY']].copy()
    # 정렬 후 groupby 별로 rownumber 생성
    #clist_sort = cList_Anl_group + ['MAX_QTY', 'SUM_QTY', 'dayofweek2']
    clist_sort = cList_Anl_group + ['MAX_QTY', 'dayofweek2']
    df_max_qty_days.sort_values(by=clist_sort, ascending=[True, True, True, True, True, True, True, True,
                                                          #False, False, True], axis=0, inplace=True)
                                                          False, True], axis=0, inplace=True)
    # 우선순위 로 하나의 요일 선택
    df_max_qty_days['rn'] = 1
    df_max_qty_days['rn'] = df_max_qty_days.groupby(cList_Anl_group)['rn'].cumsum()
    df_max_qty_days = df_max_qty_days[df_max_qty_days['rn'] == 1].copy()
    #df_max_qty_days = df_max_qty_days[[col_VersionVersionName, col_GR_DayofWeek]]
    df_max_qty_days = df_max_qty_days[cList_Anl_group + [col_GR_DayofWeek]]
    print_df(df_max_qty_days, 'df_max_qty_days', False)
    
    # DISTINCT 
    df_AnlFrequentDay_Qty = df_AnlFrequentDay_Qty[cList_Anl_group].copy()
    df_AnlFrequentDay_Qty.drop_duplicates(inplace=True)
    #print_df(df_AnlFrequentDay_Qty, 'df_AnlFrequentDay_Qty DIST', False)
    
    # Merge : max qty의 dayofweek
    df_AnlFrequentDay_Qty = df_AnlFrequentDay_Qty.merge(df_max_qty_days, on=cList_Anl_group, how='inner')
    df_AnlFrequentDay_Qty.rename(columns={col_GR_DayofWeek:col_BODSETAnl_FrequentDayQty},inplace=True)
    #df_AnlFrequentDay_Qty = df_AnlFrequentDay_Qty.merge(df_max_qty_days, on=[col_VersionVersionName, col_GR_DayofWeek], how='inner')
    #print_df(df_AnlFrequentDay_Qty, 'df_AnlFrequentDay_Qty & day', False)
    
    #df_AnlFrequentDay_Qty = df_AnlFrequentDay_Qty.groupby(cList_Anl_group, as_index=False).agg(gr_Qty=(col_BODActAnl_GRQty, 'sum'))  # sum Qty
    #df_AnlFrequentDay_Qty[col_BODSETAnl_FrequentDayQty] = df_AnlFrequentDay_Qty['gr_Qty'].astype('int64')
    #df_AnlFrequentDay_Qty.drop(columns=['gr_Qty'], inplace=True)
    
    print_df(df_AnlFrequentDay_Qty, 'df_AnlFrequentDay_Qty', False)
    del df_BODACT2_CTG
    #step('=====> STEP 4-8 : BOD SET Anl_Frequent Day Qty Create End')
    
    #####################################################################################################
    step('=====> STEP 4-9 : MG : BOD Set Anl Create')
    
    df_BODSetAnl = df_Anl_ContainerQty.copy()
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_Week, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_ActTTL, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_ActPreMonth, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_ActLastYear, on=cList_Anl_group, how='outer') #2025.10.29 추가
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_TTLPlan, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_INVO_Qty, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_JITINVO_Qty, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_FrequentDay_INVO, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_Pre_1W, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_Pre_2W, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_late_1W, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_Anl_late_2W, on=cList_Anl_group, how='outer')
    df_BODSetAnl = df_BODSetAnl.merge(df_AnlFrequentDay_Qty, on=cList_Anl_group, how='outer')
    
    del [df_Anl_ContainerQty, df_Anl_Week, df_Anl_ActTTL, df_Anl_ActPreMonth, df_Anl_ActLastYear, df_Anl_TTLPlan, 
         df_Anl_INVO_Qty, df_Anl_JITINVO_Qty, df_FrequentDay_INVO, df_Anl_Pre_1W, df_Anl_Pre_2W, 
         df_Anl_late_1W, df_Anl_late_2W, df_AnlFrequentDay_Qty]
    
    # Sequence 생성
    clist_sort = cList_Anl_group
    df_BODSetAnl.sort_values(by=clist_sort, ascending=[True, True, True, True, True, True, True,
                                                       True], axis=0, inplace=True)
    df_BODSetAnl[col_SequenceSequence] = 1
    df_BODSetAnl[col_SequenceSequence] = df_BODSetAnl.groupby(cList_Anl_Grain)[col_SequenceSequence].cumsum()
    
    
    # 칼럼정리
    df_BODSetAnl = df_BODSetAnl[cList_Anl_All]
    
    # 칼럼명 변경 : BOD Act Anl_Carrier Name ==> BOD SET Anl_Carrier Name 
    df_BODSetAnl.rename(columns={col_BODActAnl_CarrierName : col_BODSETAnl_CarrierName}, inplace=True)
    
    print_df(df_BODSetAnl, 'df_BODSetAnl', False)
    
    # BOD SET Anl LT Sequence 생성 : 2025.11.13 추가 #===================================================
    # BOD SET Anl 과 BOD SET Anl LT  Sequence 연결 
    cList_Anl_SEQ = cList_Anl_Grain + [col_BODSETAnl_CarrierName, col_SequenceSequence]
    df_BODSetAnl_SEQ = df_BODSetAnl[cList_Anl_SEQ].copy()
    df_BODSetAnl_SEQ.drop_duplicates(inplace=True)
    print_df(df_BODSetAnl_SEQ, 'df_BODSetAnl_SEQ', False)
    
    cList_Left = cList_Anl_Grain + [col_BODSETAnlLT_CarrierName]
    cList_Right = cList_Anl_Grain + [col_BODSETAnl_CarrierName]
    df_BODSetAnlLT = df_BODSetAnlLT.merge(df_BODSetAnl_SEQ, left_on=cList_Left, right_on=cList_Right, how='inner')
    del df_BODSetAnl_SEQ
    print_df(df_BODSetAnlLT, 'df_BODSetAnlLT SEQ', False)
    
    # 칼럼정리
    cList_Anl_LT_All = cList_LT_Grain + [col_SequenceSequence, col_BODSETAnlLT_CarrierName, col_BODSETAnlLT_BODActual,
                                         col_BODSETAnlLT_ShipActual, col_BODSETAnlLT_TotalActual,
                                         col_BODSETAnlLT_BODPlan, col_BODSETAnlLT_ShipPlan, col_BODSETAnlLT_TotalPlan]
    
    df_BODSetAnlLT = df_BODSetAnlLT[cList_Anl_LT_All]
    
    print_df(df_BODSetAnlLT, 'df_BODSetAnlLT Last', False)
    
    #step('=====> STEP 4-9 : MG : BOD Set Anl Create End')
    
    ################################################################################################################
    # STEP 9 : output table create
    ################################################################################################################
    step('=====> STEP 5-1 : Final output table create')
    
    #칼럼정리
    
    # out Data 생성 :
    df_out_BODSETAnlLT = df_BODSetAnlLT.copy()
    del df_BODSetAnlLT
    
    df_out_BODSETAnl = df_BODSetAnl.copy()
    del df_BODSetAnl
    
    # 버전 처리
    #df_out_BODSETAnlLT[col_VersionVersionName] = paramOutVersion
    #df_out_BODSETAnl[col_VersionVersionName]   = paramOutVersion
    
    row_count, col_count = df_out_BODSETAnlLT.shape
    note(f'=====> Final df_out_BODSETAnlLT rows : {row_count}, column : {col_count}')
    print_df(df_out_BODSETAnlLT, 'df_out_BODSETAnlLT', False)
    
    row_count, col_count = df_out_BODSETAnl.shape
    note(f'=====> Final df_out_BODSETAnl rows : {row_count}, column : {col_count}')
    print_df(df_out_BODSETAnl, 'df_out_BODSETAnl', False)
    step('=====> STEP 5-2 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_BODSETAnlLT, 'df_out_BODSETAnlLT')
        save_csv_file(df_out_BODSETAnl, 'df_out_BODSETAnl')
    
    step('=====> STEP 5-3 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_BODSETAnlLT = pd.DataFrame([], columns=[])
    df_out_BODSETAnl = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()