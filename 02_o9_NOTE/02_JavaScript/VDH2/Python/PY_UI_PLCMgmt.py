"""
* 프로그램명
    - PY_UI_PLCMgmt

* 내용
    - PLC Mfg , PLC Sales UPDATE

* 변경이력
- 2024.08.14 / 양희영 / Create
- 2025.04.15 / 신동언 / update
- 2026.04.03 / 양희영 / update


* Input
- df_in_Table = pd.read_csv(' .csv')

* Flow Summary

* Execution
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_PLCMfg : 통함 : df_in_PLCSales_SET, df_in_PLCMfgSRAComDate
                    Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].[SET] * [Location].[Location] * [Location].[Site Stage] ) on row, 
                    ({Measure.[PLC Mfg_SRA FW Limit Date], Measure.[PLC Mfg_EOP FW Limit Date], Measure.[PLC Mfg_CTN End Date], Measure.[PLC Mfg_Short Req Date], Measure.[PLC Mfg_SRA Init Date], 
                    Measure.[PLC Mfg_SRA Com Date], Measure.[PLC Mfg_EOP Chg Date], Measure.[PLC Mfg_SRA Actual Date], Measure.[PLC Mfg_Dev SRA Init Date], Measure.[PLC Mfg_PLC Status]}) on column;
    - df_in_PLCSales_SET : Select ([Version].[Version Name] * [Item].[Item] *  [Item].[Item Stage].[SET] * [Sales Domain].[AP2] ) on row, 
                           ({Measure.[PLC Sales_BOD LT], Measure.[PLC Sales_RTS FW Limit Date], Measure.[PLC Sales_EOS FW Limit Date], Measure.[Dummy]}) on column;
    - df_in_DemandW_SET : Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].[SET] * [Time].[Week] * [Location].[Location] * [Location].[Location Type] * [Sales Domain].[Ship To] * 
                          [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, 
                          ({Measure.[Dmd W_BAL], Measure.[Dmd W_Cust Rank], Measure.[Dmd W_Dmd Rank], Measure.[Dmd W_Global Prty], Measure.[Dmd W_ID], Measure.[Dmd W_Leadtime Due], Measure.[Dmd W_Local Prty], 
                          Measure.[Dmd W_Measure Rank], Measure.[Dmd W_No Plan], Measure.[Dmd W_Plan ID], Measure.[Dmd W_Preference], Measure.[Dmd W_Prod Rank], Measure.[Dmd W_Prty], Measure.[Dmd W_Prty Seq], 
                          Measure.[Dmd W_Qty], Measure.[Dmd W_Week Rank]}) on column;
    - df_in_TimeWeek : Select ([Time].[Week] * [Time].[Day] * [Time].[Day of Week] ) on row;
    - df_in_NewModelSetMP : Select ([Version].[Version Name] * [Item New Model].[Item] * [Location].[Location] * [Sales Domain].[AP2] * [Category].[Category].filter(#.Name=="Plan")) on row, 
                            ({Measure.[New Model_SET MP]}) on column where {~isnull(Measure.[New Model_SET MP])};
    - df_in_CTNItemConstEndWeek : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, 
                                  ({Measure.[CTN Item Const_End Week]}) on column where {~isnull(Measure.[CTN Item Const_End Week])};
    - df_in_CurrentDay : Select (&CurrentDay);
    - df_in_SalesItemAsnValidFlag : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2]) on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column;

* Output Tables
    - df_out_PLCMfg : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] ) on row,
                             ({Measure.[PLC Mfg_SRA FW Limit Date], Measure.[PLC Mfg_EOP FW Limit Date], Measure.[PLC Mfg_CTN End Date], Measure.[PLC Mfg_Short Req Date]}) on column limit 100;
    - df_out_PLCSales : Select ([Version].[Version Name] * [Item].[Item] * [Sales Domain].[AP2] ) on row,
                             ({Measure.[PLC Sales_RTS FW Limit Date], Measure.[PLC Sales_EOS FW Limit Date]}) on column limit 100;
    - df_out_PLCMfgSRAComDate : Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item] * [Location].[Location] ) on row,
                              ({Measure.[PLC Mfg_SRA Com Date], Measure.[PLC Mfg_BOM Status], Measure.[PLC Mfg_PLC Status]}) on column limit 1000;
    - df_out_PLCMfgCTNEndDate : Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[PLC Mfg_CTN End Date]}) on column limit 1000;
    - df_out_PLCSalesRTSValidFlag : Select ([Version].[Version Name] * [Item].[Item] * [Sales Domain].[AP2] ) on row, ({Measure.[PLC Sales_RTS Valid Flag]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_PLCMgmt] for measures {[PLC Mfg_SRA Com Date]} using scope (&MPV)
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
from datetime import datetime as dt

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_PLCMgmt'
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
    # DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====> DataFrame Column : 변수 처리')
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 컬럼 변수 선언
    versionVersionName = 'Version.[Version Name]'
    itemItem = 'Item.[Item]'
    itemItemStage = 'Item.[Item Stage]'
    ItemNewModelItem = 'Item New Model.[Item]'
    locationLocation = 'Location.[Location]'
    locationSiteStage = 'Location.[Site Stage]'
    #locationMFSiteStage = 'Location.[MF Site Stage]'
    timeWeek = 'Time.[Week]'
    timeDay = 'Time.[Day]'
    timeWeekKey = 'Time.[WeekKey]'
    timeDayofWeek = 'Time.[Day of Week]'

    dateTime = 'Date Time'
    dateTimeLT = 'Date Time LT'
    firstDay = 'First_Day'

    pLCMfg_SRAFWLimitDate     = 'PLC Mfg_SRA FW Limit Date'
    pLCMfg_SRAFWLimitDate_Org = 'PLC Mfg_SRA FW Limit Date_Org'

    pLCMfg_EOPFWLimitDate     = 'PLC Mfg_EOP FW Limit Date'
    pLCMfg_EOPFWLimitDate_Org = 'PLC Mfg_EOP FW Limit Date_Org'

    pLCMfg_ShortReqDate     = 'PLC Mfg_Short Req Date'
    pLCMfg_ShortReqDate_Org = 'PLC Mfg_Short Req Date_Org'

    pLCMfg_CTNEndDate     = 'PLC Mfg_CTN End Date'
    pLCMfg_CTNEndDate_Org = 'PLC Mfg_CTN End Date_Org'

    pLCMfg_SRAInitDate  = 'PLC Mfg_SRA Init Date'
    pLCMfg_MfgLTWeek    = 'PLC Mfg_LT Week'
    # pLCMfg_SRADate         = 'PLC Mfg_SRA Date' # 'PLC Mfg_SRA Com Date'로 대체됨.(김보은 10/18)
    pLCMfg_SRAComDate     = 'PLC Mfg_SRA Com Date'
    pLCMfg_SRAComDate_Org = 'PLC Mfg_SRA Com Date_Org'
    # pLCMfg_EOP_Date        = 'PLC Mfg_EOP_Date' # 'PLC Mfg_EOP Chg Date' 로 대체됨.(김보은 10/18)
    pLCMfg_EOPChgDate     = 'PLC Mfg_EOP Chg Date'
    pLCMfg_SRAActualDate  = 'PLC Mfg_SRA Actual Date'
    pLCMfg_DevSRAInitDate = 'PLC Mfg_Dev SRA Init Date'

    # (김보은 25/04/15)추가
    pLCMfg_RtsValidFlag = 'PLC Sales_RTS Valid Flag'
    SalesItemAsnValidFlag = 'Sales Item Asn_Valid Flag'

    demandDemandID = 'Demand.[DemandID]'
    salesDomainAP2 = 'Sales Domain.[AP2]'
    pLCSales_BODLT = 'PLC Sales_BOD LT'
    pLCSales_RTSFWLimitDate = 'PLC Sales_RTS FW Limit Date'
    pLCSales_RTSFWLimitDate_Org = 'PLC Sales_RTS FW Limit Date_Org'
    pLCSales_EOSFWLimitDate = 'PLC Sales_EOS FW Limit Date'
    pLCSales_EOSFWLimitDate_Org = 'PLC Sales_EOS FW Limit Date_Org'
    newModel_SETMP = 'New Model_SET MP'
    cTNItemConst_EndWeek = 'CTN Item Const_End Week'
    currentDay = 'CurrentDay'

    ################################################################################################################
    # STEP 0-1 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-1 : 전처리 : Input table load')

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE

        df_in_PLCMfg       = read_csv_file("df_in_PLCMfg") #통합 : df_in_PLCSales_SET, df_in_PLCMfgSRAComDate
        df_in_PLCSales_SET = read_csv_file("df_in_PLCSales_SET")
        df_in_DemandW_SET  = read_csv_file("df_in_DemandW_SET")
        df_in_TimeWeek     = read_csv_file("df_in_TimeWeek")

        # 추가 요청(2024.10.18) --------
        df_in_NewModelSetMP       = read_csv_file("df_in_NewModelSetMP")
        df_in_CTNItemConstEndWeek = read_csv_file("df_in_CTNItemConstEndWeek")
        df_in_CurrentDay          = read_csv_file("df_in_CurrentDay")

        # 추가 요청(2025.04.15) --------
        df_in_SalesItemAsnValidFlag = read_csv_file("df_in_SalesItemAsnValidFlag")

    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE

    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_PLCMfg, 'df_in_PLCMfg', False)
    # print_df(df_in_PLCMfg_SET, 'df_in_PLCMfg_SET', False)
    print_df(df_in_PLCSales_SET, 'df_in_PLCSales_SET', False)
    print_df(df_in_DemandW_SET, 'df_in_DemandW_SET', False)
    print_df(df_in_TimeWeek, 'df_in_TimeWeek', False)

    print_df(df_in_NewModelSetMP, 'df_in_NewModelSetMP', False)
    print_df(df_in_CTNItemConstEndWeek, 'df_in_CTNItemConstEndWeek', False)
    print_df(df_in_CurrentDay, 'df_in_CurrentDay', False)
    print_df(df_in_SalesItemAsnValidFlag,'df_in_SalesItemAsnValidFlag', False)

    # df_in_PLCMfg = df_in_PLCMfg[df_in_PLCMfg['PLC Mfg_PLC Status'].isin(['ACTIVE', 'PLANNED'])]
    # df_in_PLCMfg_SET = df_in_PLCMfg_SET[df_in_PLCMfg_SET['PLC Mfg_PLC Status'].isin(['ACTIVE', 'PLANNED'])]
    # print_df(df_in_PLCMfg, 'df_in_PLCMfg -2', False)
    # print_df(df_in_PLCMfg_SET, 'df_in_PLCMfg_SET -2', False)

    # DATA TYPE 설정

    # PANDAS 지원되는 일자 : 1697년 9월 21일 ~ 2262년 4월 11일
    def replace_date(date_string, rtn_type):
        #max_date = dt.strptime("2262-04-11", '%Y-%m-%d')
        max_date = dt.strptime("2261-01-01", '%Y-%m-%d') # lt를 더하면 초과 현상 발생으로 최대일자를 줄임.

        date_string = str(date_string)

        if date_string != 'nan':
            try:
                date_object = dt.strptime(date_string, '%m/%d/%Y %I:%M:%S %p')
            except Exception as e1:
                try:
                    date_object = dt.strptime(date_string, '%Y-%m-%d')
                except Exception as e2:
                    date_object = dt.strptime(date_string, '%Y-%m-%d %H:%M:%S')

            if date_object > max_date:
                return_date = max_date
                #print(date_string)
            else:
                return_date = date_object

            return return_date.strftime(rtn_type)


    # --------------------------------------------------------------------------------

    if df_in_PLCMfg[pLCMfg_SRAFWLimitDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_SRAFWLimitDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_SRAFWLimitDate],
                                                             format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_EOPFWLimitDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_EOPFWLimitDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_EOPFWLimitDate],
                                                             format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_SRAInitDate].dtype != 'datetime64[ns]':
        # 2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_PLCMfg[pLCMfg_SRAInitDate] = np.where(df_in_PLCMfg[pLCMfg_SRAInitDate].isna(),
                                                    df_in_PLCMfg[pLCMfg_SRAInitDate],
                                                    df_in_PLCMfg[pLCMfg_SRAInitDate].apply(
                                                        lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                                                    )
        df_in_PLCMfg[pLCMfg_SRAInitDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_SRAInitDate],
                                                          format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_CTNEndDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_CTNEndDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_CTNEndDate],
                                                         format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_ShortReqDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_ShortReqDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_ShortReqDate],
                                                           format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_SRAComDate].dtype != 'datetime64[ns]':
        # 2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_PLCMfg[pLCMfg_SRAComDate] = np.where(df_in_PLCMfg[pLCMfg_SRAComDate].isna(),
                                                   df_in_PLCMfg[pLCMfg_SRAComDate],
                                                   df_in_PLCMfg[pLCMfg_SRAComDate].apply(
                                                       lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                                                   )
        df_in_PLCMfg[pLCMfg_SRAComDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_SRAComDate],
                                                         format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_EOPChgDate].dtype != 'datetime64[ns]':
        # 2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_PLCMfg[pLCMfg_EOPChgDate] = np.where(df_in_PLCMfg[pLCMfg_EOPChgDate].isna(),
                                                   df_in_PLCMfg[pLCMfg_EOPChgDate],
                                                   df_in_PLCMfg[pLCMfg_EOPChgDate].apply(
                                                       lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                                                   )
        df_in_PLCMfg[pLCMfg_EOPChgDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_EOPChgDate],
                                                         format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_SRAActualDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_SRAActualDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_SRAActualDate],
                                                            format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCMfg[pLCMfg_DevSRAInitDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[pLCMfg_DevSRAInitDate] = pd.to_datetime(df_in_PLCMfg[pLCMfg_DevSRAInitDate],
                                                             format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCSales_SET[pLCSales_RTSFWLimitDate].dtype != 'datetime64[ns]':
        df_in_PLCSales_SET[pLCSales_RTSFWLimitDate] = pd.to_datetime(df_in_PLCSales_SET[pLCSales_RTSFWLimitDate],
                                                                     format='%m/%d/%Y %I:%M:%S %p')

    if df_in_PLCSales_SET[pLCSales_EOSFWLimitDate].dtype != 'datetime64[ns]':
        df_in_PLCSales_SET[pLCSales_EOSFWLimitDate] = pd.to_datetime(df_in_PLCSales_SET[pLCSales_EOSFWLimitDate],
                                                                     format='%m/%d/%Y %I:%M:%S %p')

    if df_in_NewModelSetMP[newModel_SETMP].dtype != 'datetime64[ns]':
        df_in_NewModelSetMP[newModel_SETMP] = pd.to_datetime(df_in_NewModelSetMP[newModel_SETMP],
                                                             format='%m/%d/%Y %I:%M:%S %p')

    df_in_DemandW_SET = df_in_DemandW_SET.astype({timeWeek: 'str'}, copy=True)
    df_in_TimeWeek = df_in_TimeWeek.astype({timeWeek: 'str', timeDay: 'str'}, copy=True)

    df_in_CTNItemConstEndWeek = df_in_CTNItemConstEndWeek.astype({cTNItemConst_EndWeek: 'str'}, copy=True)

    df_in_CurrentDay[timeDay] = pd.to_datetime(df_in_CurrentDay[timeDay], format='%Y-%m-%d')
    df_in_CurrentDay.rename(columns={timeDay:currentDay}, inplace=True)

    print_df(df_in_PLCSales_SET, 'df_in_PLCSales_SET 2', False)
    print_df(df_in_PLCMfg, 'df_in_PLCMfg 2', False)
    print_df(df_in_CurrentDay, 'df_in_CurrentDay 2', False)

    step('=====> STEP 0-2 : 전처리 : Input table load End')

    ################################################################################################################
    # STEP 0-2 : 추가 df 생성
    ################################################################################################################
    step('=====> STEP 0-3 : 추가 df Create ')
    # 칼럼 정리
    df_in_TimeWeek = df_in_TimeWeek[[timeWeek, timeDay, timeDayofWeek]]

    # df_Week_FirstDay 생성
    df_Week_FirstDay = df_in_TimeWeek[df_in_TimeWeek[timeDayofWeek] == 'MON'].copy()  # MON 이 주의 첫번째
    df_Week_FirstDay[firstDay] = pd.to_datetime(df_Week_FirstDay[timeDay], format='%Y-%m-%d')
    # df_Week_FirstDay = df_Week_FirstDay.groupby([timeWeek], as_index=False)[firstDay].min()
    df_Week_FirstDay = df_Week_FirstDay[[timeWeek, firstDay]]
    print_df(df_Week_FirstDay, 'df_Week_FirstDay', False)
    step('=====> STEP 0-4 : 추가 df Create End')

    ################################################################################################################
    # STEP 1 : 'PLC Mfg_SRA Com Date' UPDATE
    # 1. Measure.[New Model_SET MP] 와 Measure.[PLC Mfg_SRA Com Date] 가 다른 경우에만 Measure.[New Model_SET MP] 로 엎어친다.
    # 2. Measure.[New Model_SET MP] 값이 없는 경우에는 그냥 Measure.[PLC Mfg_SRA Com Date] 값을 그대로 사용한다.
    ################################################################################################################
    step('=====> STEP 1-1 : PLC Mfg_SRA Com Date Update')

    # 'New Model_SET MP' group by Min : 'PLC Mfg_SRA Com Date' UPDATE 에 사용됨
    df_NewModelSetMP = df_in_NewModelSetMP.groupby([versionVersionName, ItemNewModelItem, locationLocation],
                                                   as_index=False)[newModel_SETMP].min()
    del df_in_NewModelSetMP

    df_NewModelSetMP.rename(columns={ItemNewModelItem: itemItem}, inplace=True)
    print_df(df_NewModelSetMP, 'df_NewModelSetMP', False)

    ################################
    # Merge df_in_PLCMfg & df_NewModelSetMP
    df_PLCMfgSRAComDate = df_in_PLCMfg.merge(df_NewModelSetMP, on=[versionVersionName, itemItem, locationLocation],
                                             how='left')
    df_PLCMfgSRAComDate[pLCMfg_SRAComDate_Org] = df_PLCMfgSRAComDate[pLCMfg_SRAComDate]
    df_PLCMfgSRAComDate[pLCMfg_SRAComDate] = np.where(df_PLCMfgSRAComDate[newModel_SETMP].notna() &
                                        (df_PLCMfgSRAComDate[newModel_SETMP] != df_PLCMfgSRAComDate[pLCMfg_SRAComDate])
                                        , df_PLCMfgSRAComDate[newModel_SETMP],
                                          df_PLCMfgSRAComDate[pLCMfg_SRAComDate])

    # PLC Mfg 데이터 생성용 df , 처리된 pLCMfg_SRAComDate 를 사용
    #df_in_PLCMfg_SET = df_PLCMfgSRAComDate[df_PLCMfgSRAComDate[locationMFSiteStage] == 'SET'].copy()
    # Location.[MF Site Stage] =>  Location.[Site Stage] 'SET' 포함 으로 변경. 2026.02.10 수정
    df_in_PLCMfg_SET = df_PLCMfgSRAComDate[df_PLCMfgSRAComDate[locationSiteStage].str.contains('SET')].copy()
    print_df(df_in_PLCMfg_SET, 'df_in_PLCMfg_SET', False)

    # 변경된 것만 update 대상으로 처리
    df_PLCMfgSRAComDate = df_PLCMfgSRAComDate[df_PLCMfgSRAComDate[pLCMfg_SRAComDate].notna() &
                                              (df_PLCMfgSRAComDate[pLCMfg_SRAComDate] != df_PLCMfgSRAComDate[
                                                  pLCMfg_SRAComDate_Org])
                                              ]
    print_df(df_PLCMfgSRAComDate, 'df_PLCMfgSRAComDate', False)
    ################################

    ################################
    ### df_in_PLCMfg_SET UPDATE :  PLC Sales (df_PLCSales) 데이터 생성 시 [PLC Mfg_SRA Com Date] 사용 #################

    step('=====> STEP 1-2 : PLC Mfg_SRA Com Date Update End')

    ################################################################################################################
    # STEP 2 :  PLC Mfg 데이터 생성
    ################################################################################################################
    step('=====> STEP 2-1 : PLC Mfg Data Create')

    # MAX(Week - BOD L/T) : 가장 큰위크에 가장 작은 BOD LT 적용
    df_DemandW = df_in_DemandW_SET.groupby([versionVersionName, itemItem], as_index=False)[timeWeek].max()
    del df_in_DemandW_SET
    print_df(df_DemandW, 'df_DemandW 1', False)

    # Merge : df_in_PLCMfg_SET & df_DemandW
    df_PLCMfg_SET = df_in_PLCMfg_SET.merge(df_DemandW, on=[versionVersionName, itemItem], how='inner')

    print_df(df_PLCMfg_SET, 'df_PLCMfg_SET 1', False)

    # item / MIN(PLC Sales_BOD LT) : # PLC Sales_df_in_PLCSales_SET 에는 Location 정보가 없음.
    df_PLCSales_SET_LT = df_in_PLCSales_SET.groupby([versionVersionName, itemItem],
                                                    as_index=False)[pLCSales_BODLT].min()
    df_PLCSales_SET_LT[pLCSales_BODLT] = df_PLCSales_SET_LT[pLCSales_BODLT].fillna(0).astype('int64')
    print_df(df_PLCSales_SET_LT, 'df_PLCSales_SET_LT 1', False)

    ## Merge : df_PLCMfg_SET & df_PLCSales_SET_LT
    df_PLCMfg_SET = df_PLCMfg_SET.merge(df_PLCSales_SET_LT, on=[versionVersionName, itemItem], how='left')
    df_PLCMfg_SET[pLCSales_BODLT] = df_PLCMfg_SET[pLCSales_BODLT].fillna(0).astype('int64')
    #print_df(df_PLCMfg_SET, 'df_PLCMfg_SET 2', False)

    df_PLCMfg_SET[pLCMfg_SRAFWLimitDate_Org] = df_PLCMfg_SET[pLCMfg_SRAFWLimitDate]
    df_PLCMfg_SET[pLCMfg_EOPFWLimitDate_Org] = df_PLCMfg_SET[pLCMfg_EOPFWLimitDate]
    df_PLCMfg_SET[pLCMfg_ShortReqDate_Org]   = df_PLCMfg_SET[pLCMfg_ShortReqDate]

    df_TimeWeek = df_in_TimeWeek[df_in_TimeWeek[timeDayofWeek] == 'SUN']
    df_PLCMfg_SET = df_PLCMfg_SET.merge(df_TimeWeek, on=[timeWeek], how='inner')
    df_PLCMfg_SET[dateTime] = pd.to_datetime(df_PLCMfg_SET[timeDay], format='%Y-%m-%d')
    df_PLCMfg_SET[dateTimeLT] = df_PLCMfg_SET[dateTime] - pd.to_timedelta(df_PLCMfg_SET[pLCSales_BODLT], unit='d')

    df_PLCMfg_SET['Dummy'] = 1
    df_in_CurrentDay['Dummy'] = 1

    df_PLCMfg_SET = df_PLCMfg_SET.merge(df_in_CurrentDay, on=['Dummy'], how='inner', suffixes=('', '_y'))
    print_df(df_PLCMfg_SET, 'df_PLCMfg_SET 3', False)
    '''
    measure.[PLC Mfg_SRA FW Limit Date] = 
    if (IsNull(measure.[PLC Mfg_SRA Actual Date]) the null else
    if (~IsNull(measure.[PLC Mfg_SRA Actual Date]) && (measure.[PLC Mfg_Dev SRA Init Date])) < &CurrentDay then &CurrentDay else
    if (~IsNull(measure.[PLC Mfg_SRA Actual Date]) && (measure.[PLC Mfg_Dev SRA Init Date])) > &CurrentDay then measure.[PLC Mfg_Dev SRA Init Date];
    '''
    #df_PLCMfg_SET[pLCMfg_SRAFWLimitDate] = df_PLCMfg_SET[pLCMfg_SRAInitDate]
    '''
    # 1730073600000000000 가 입력되는 현상발생.
    df_PLCMfg_SET[pLCMfg_SRAFWLimitDate] = np.select([df_PLCMfg_SET[pLCMfg_SRAActualDate].isna() | 
                                                      df_PLCMfg_SET[pLCMfg_DevSRAInitDate].isna(),
                                                  (df_PLCMfg_SET[pLCMfg_DevSRAInitDate].notna() & 
                                                   (df_PLCMfg_SET[pLCMfg_DevSRAInitDate] < df_PLCMfg_SET[currentDay])),
                                                  (df_PLCMfg_SET[pLCMfg_DevSRAInitDate].notna() & 
                                                   (df_PLCMfg_SET[pLCMfg_DevSRAInitDate] >= df_PLCMfg_SET[currentDay])),
                                                  True, ],
                                                 [pd.to_datetime(np.nan),
                                                  df_PLCMfg_SET[currentDay],
                                                  df_PLCMfg_SET[pLCMfg_DevSRAInitDate],
                                                  df_PLCMfg_SET[pLCMfg_DevSRAInitDate]])'''
    # str 로 생성 후에 날짜형식으로 변경
    df_PLCMfg_SET['TEMP_DATE'] = np.select([df_PLCMfg_SET[pLCMfg_SRAActualDate].isna() |
                                            df_PLCMfg_SET[pLCMfg_DevSRAInitDate].isna(),
                                            (df_PLCMfg_SET[pLCMfg_DevSRAInitDate].notna() &
                                             (df_PLCMfg_SET[pLCMfg_DevSRAInitDate] < df_PLCMfg_SET[currentDay])),
                                            (df_PLCMfg_SET[pLCMfg_DevSRAInitDate].notna() &
                                             (df_PLCMfg_SET[pLCMfg_DevSRAInitDate] >= df_PLCMfg_SET[currentDay])),
                                            True, ],
                                           [np.nan,
                                            df_PLCMfg_SET[currentDay].astype('str'),
                                            df_PLCMfg_SET[pLCMfg_DevSRAInitDate].astype('str'),
                                            df_PLCMfg_SET[pLCMfg_DevSRAInitDate].astype('str')
                                           ])
    df_PLCMfg_SET[pLCMfg_SRAFWLimitDate] = pd.to_datetime(df_PLCMfg_SET['TEMP_DATE'], format='%Y-%m-%d')

    print_df(df_PLCMfg_SET, 'df_PLCMfg_SET TMP', False)
    df_PLCMfg_SET[pLCMfg_EOPFWLimitDate] = pd.to_datetime(np.nan)
    # df_PLCMfg_SET[pLCMfg_CTNEndDate]     = pd.to_datetime(np.nan) # 미정, df_out_PLCMfgCTNEndDate 에서 UPDATE 됨.
    df_PLCMfg_SET[pLCMfg_ShortReqDate] = df_PLCMfg_SET[dateTimeLT]

    df_PLCMfg_SET = df_PLCMfg_SET[(df_PLCMfg_SET[pLCMfg_SRAFWLimitDate_Org] != df_PLCMfg_SET[pLCMfg_SRAFWLimitDate]) |
                                  (df_PLCMfg_SET[pLCMfg_EOPFWLimitDate_Org] != df_PLCMfg_SET[pLCMfg_EOPFWLimitDate]) |
                                  (df_PLCMfg_SET[pLCMfg_ShortReqDate_Org] != df_PLCMfg_SET[pLCMfg_ShortReqDate])]

    print_df(df_PLCMfg_SET, 'df_PLCMfg_SET 4', False)

    # 칼럼 정리
    df_PLCMfg_SET = df_PLCMfg_SET[[versionVersionName, itemItem, locationLocation, pLCMfg_SRAComDate,
                                   pLCMfg_EOPChgDate, pLCMfg_SRAFWLimitDate, pLCMfg_EOPFWLimitDate,
                                   pLCMfg_ShortReqDate]].copy()

    print_df(df_PLCMfg_SET, 'df_PLCMfg_SET 5', False)
    # --------------------------------------------------------------------------------------------------------------

    step('=====> STEP 2-2 : PLC Mfg Data Create End')

    ################################################################################################################
    # STEP 3 :  PLC Sales 데이터 생성
    ################################################################################################################
    step('=====> STEP 3-1 : PLC Sales Data Create')

    df_PLCMfg_MIN = df_in_PLCMfg_SET.groupby([versionVersionName, itemItem],
                                             as_index=False).agg({pLCMfg_SRAComDate: "min", pLCMfg_EOPChgDate: "min"})
    del df_in_PLCMfg_SET
    print_df(df_PLCMfg_MIN, 'df_PLCMfg_MIN', False)

    df_PLCSales = df_in_PLCSales_SET.merge(df_PLCMfg_MIN, on=[versionVersionName, itemItem], how='inner',
                                           suffixes=('','_y'))
    print_df(df_PLCSales, 'df_PLCSales 1', False)
    del df_in_PLCSales_SET

    df_PLCSales[pLCSales_RTSFWLimitDate_Org] = df_PLCSales[pLCSales_RTSFWLimitDate]
    df_PLCSales[pLCSales_EOSFWLimitDate_Org] = df_PLCSales[pLCSales_EOSFWLimitDate]

    df_PLCSales[pLCSales_BODLT] = df_PLCSales[pLCSales_BODLT].fillna(0).astype('int64')
    df_PLCSales['TDELTA'] = pd.to_timedelta(df_PLCSales[pLCSales_BODLT], unit='d')
    df_PLCSales[pLCSales_RTSFWLimitDate] = df_PLCSales[pLCMfg_SRAComDate] + df_PLCSales['TDELTA'] #pd.to_timedelta(df_PLCSales[pLCSales_BODLT], unit='d')
    df_PLCSales[pLCSales_EOSFWLimitDate] = df_PLCSales[pLCMfg_EOPChgDate] + df_PLCSales['TDELTA'] #pd.to_timedelta(df_PLCSales[pLCSales_BODLT], unit='d')

    df_PLCSales = df_PLCSales[((df_PLCSales[pLCSales_RTSFWLimitDate_Org] != df_PLCSales[pLCSales_RTSFWLimitDate]) |
                               (df_PLCSales[pLCSales_EOSFWLimitDate_Org] != df_PLCSales[pLCSales_EOSFWLimitDate])) &
                              (df_PLCSales[pLCSales_RTSFWLimitDate].notna() |
                                df_PLCSales[pLCSales_EOSFWLimitDate].notna())].copy()

    # 칼럼 정리
    cList_PLCSales = [versionVersionName, itemItem, salesDomainAP2, pLCSales_RTSFWLimitDate, pLCSales_EOSFWLimitDate]
    df_PLCSales = df_PLCSales[cList_PLCSales]
    print_df(df_PLCSales, 'df_PLCSales 3', False)

    step('=====> STEP 3-2 : PLC Sales Data Create End')

    ################################################################################################################
    # STEP 4 :  [PLC Mfg_CTN End Date] 데이터 생성
    ################################################################################################################
    step('=====> STEP 4-1 : PLC Mfg_CTN End Date Create')
    # groupby : Item, Location
    df_CTNItemConstEndWeek = df_in_CTNItemConstEndWeek.groupby([versionVersionName, itemItem, locationLocation],
                                                               as_index=False)[cTNItemConst_EndWeek].min()
    del df_in_CTNItemConstEndWeek

    # Week 의 First Day 구하기 : Merge df_CTNItemConstEndWeek & df_Week_FirstDay
    df_CTNItemConstEndWeek = df_CTNItemConstEndWeek.merge(df_Week_FirstDay, left_on=[cTNItemConst_EndWeek],
                                                          right_on=[timeWeek], how='inner')
    del df_Week_FirstDay
    print_df(df_CTNItemConstEndWeek, 'df_CTNItemConstEndWeek', False)

    # Merge df_in_PLCMfg & df_CTNItemConstEndWeek
    df_PLCMfgCTNEndDate = df_in_PLCMfg.merge(df_CTNItemConstEndWeek,
                                             on=[versionVersionName, itemItem, locationLocation], how='inner')
    del [df_in_PLCMfg, df_CTNItemConstEndWeek]
    df_PLCMfgCTNEndDate[pLCMfg_CTNEndDate_Org] = df_PLCMfgCTNEndDate[pLCMfg_CTNEndDate]

    # First_Day 로 Update
    df_PLCMfgCTNEndDate[pLCMfg_CTNEndDate] = df_PLCMfgCTNEndDate[firstDay]

    df_PLCMfgCTNEndDate = df_PLCMfgCTNEndDate[
                        (df_PLCMfgCTNEndDate[pLCMfg_CTNEndDate_Org] != df_PLCMfgCTNEndDate[pLCMfg_CTNEndDate])].copy()

    print_df(df_PLCMfgCTNEndDate, 'df_PLCMfgCTNEndDate', False)
    step('=====> STEP 4-2 : PLC Mfg_CTN End Date Create End')

    ################################################################################################################
    # STEP 5 :  [PLC Sales_RTS Valid Flag] 데이터 생성
    ################################################################################################################
    step('=====> STEP 5-1 : PLC Sales_RTS Valid Flag Create')
    # groupby : Item, Sales.AP2

    df_in_SalesItemAsnValidFlag[SalesItemAsnValidFlag]  = df_in_SalesItemAsnValidFlag[SalesItemAsnValidFlag].astype('string')

    #df_PLCSales_RTSValidFlag = df_in_SalesItemAsnValidFlag.loc[df_in_SalesItemAsnValidFlag[SalesItemAsnValidFlag].str.contains('TRUE')].copy()
    #df_PLCSales_RTSValidFlag = df_in_SalesItemAsnValidFlag[df_in_SalesItemAsnValidFlag[SalesItemAsnValidFlag] == 'true'].copy()
    df_PLCSales_RTSValidFlag = df_in_SalesItemAsnValidFlag[df_in_SalesItemAsnValidFlag[SalesItemAsnValidFlag].str.lower() == 'true'].copy() #2025.06.27 수정. local에서 문제있어 수정
    #df_PLCSales_RTSValidFlag = df_in_SalesItemAsnValidFlag[[versionVersionName,itemItem,locationLocation,salesDomainAP2,SalesItemAsnValidFlag]]

    df_PLCSales_RTSValidFlag = df_PLCSales_RTSValidFlag.groupby([versionVersionName, itemItem, salesDomainAP2],
                                                               as_index=False)[SalesItemAsnValidFlag].max()

    df_PLCSales_RTSValidFlag.rename(columns={SalesItemAsnValidFlag: pLCMfg_RtsValidFlag}, inplace=True)
    df_PLCSales_RTSValidFlag[pLCMfg_RtsValidFlag] = df_PLCSales_RTSValidFlag[pLCMfg_RtsValidFlag].astype('string')
    print_df(df_PLCSales_RTSValidFlag, 'df_PLCSales_RTSValidFlag', False )
    del df_in_SalesItemAsnValidFlag

    step('=====> STEP 5-2 : PLC Sales_RTS Valid Flag Create End')

    ################################################################################################################
    # STEP 6 : : output table create
    ################################################################################################################
    step('=====> STEP 6-1 : output table create')

    cList_PLCMfg = [versionVersionName, itemItem, locationLocation,
                    pLCMfg_SRAFWLimitDate, pLCMfg_EOPFWLimitDate, pLCMfg_ShortReqDate]

    # out Data 생성 1 :
    df_out_PLCMfg = df_PLCMfg_SET[df_PLCMfg_SET[pLCMfg_SRAFWLimitDate].notna() |
                                  df_PLCMfg_SET[pLCMfg_EOPFWLimitDate].isna() |
                                  df_PLCMfg_SET[pLCMfg_ShortReqDate].notna()].copy()
    del df_PLCMfg_SET

    # out Data 설정
    df_out_PLCMfg = df_out_PLCMfg[cList_PLCMfg].copy(deep=True)

    row_count, col_count = df_out_PLCMfg.shape
    note(f'=====> Final df_out_PLCMfg rows : {row_count}, column : {col_count}')
    print_df(df_out_PLCMfg, 'df_out_PLCMfg', False)

    # out Data 생성 2 :
    df_out_PLCSales = df_PLCSales.copy()
    del df_PLCSales

    row_count, col_count = df_out_PLCSales.shape
    note(f'=====> Final df_out_PLCSales rows : {row_count}, column : {col_count}')
    print_df(df_out_PLCSales, 'df_out_PLCSales', False)

    # out Data 생성 3 :
    df_out_PLCMfgSRAComDate = df_PLCMfgSRAComDate[
        [versionVersionName, itemItem, locationLocation, pLCMfg_SRAComDate]].copy(deep=True)
    del df_PLCMfgSRAComDate

    row_count, col_count = df_out_PLCMfgSRAComDate.shape
    note(f'=====> Final df_out_PLCMfgSRAComDate rows : {row_count}, column : {col_count}')
    print_df(df_out_PLCMfgSRAComDate, 'df_out_PLCMfgSRAComDate', False)

    # out Data 생성 4 :
    #
    df_out_PLCMfgCTNEndDate = df_PLCMfgCTNEndDate[
        [versionVersionName, itemItem, locationLocation, pLCMfg_CTNEndDate]].copy(deep=True)
    del df_PLCMfgCTNEndDate

    row_count, col_count = df_out_PLCMfgCTNEndDate.shape
    note(f'=====> Final df_out_PLCMfgCTNEndDate rows : {row_count}, column : {col_count}')
    print_df(df_out_PLCMfgCTNEndDate, 'df_out_PLCMfgCTNEndDate', False)

    '''
    cList_PLCMfg = [versionVersionName, itemItem, locationLocation,
                    pLCMfg_SRAFWLimitDate, pLCMfg_EOPFWLimitDate, pLCMfg_ShortReqDate]    
    cList_PLCSales = [versionVersionName, itemItem, salesDomainAP2, pLCSales_RTSFWLimitDate, pLCSales_EOSFWLimitDate]
    df_out_PLCMfg = pd.DataFrame(columns=cList_PLCMfg)  # 빈 dataframe
    df_out_PLCSales = pd.DataFrame(columns=cList_PLCSales)  # 빈 dataframe
    df_out_PLCMfgSRAComDate = pd.DataFrame(columns=[versionVersionName, itemItem, locationLocation, pLCMfg_SRAComDate])  # 빈 dataframe
    df_out_PLCMfgCTNEndDate = pd.DataFrame(columns=[versionVersionName, itemItem, locationLocation, pLCMfg_CTNEndDate])  # 빈 dataframe
    '''

    #### 2025.04.15 추가
    df_out_PLCSalesRTSValidFlag = df_PLCSales_RTSValidFlag[[versionVersionName,itemItem,salesDomainAP2,pLCMfg_RtsValidFlag]].copy(deep=True)
    df_out_PLCSalesRTSValidFlag[pLCMfg_RtsValidFlag] = df_out_PLCSalesRTSValidFlag[pLCMfg_RtsValidFlag].astype('string')
    row_count, col_count = df_out_PLCSalesRTSValidFlag.shape
    note(f'=====> Final df_out_PLCSalesRTSValidFlag rows : {row_count}, column : {col_count}')
    print_df(df_out_PLCSalesRTSValidFlag, 'df_out_PLCSalesRTSValidFlag', False)
    del df_PLCSales_RTSValidFlag

    if is_local:
        step('=====> Output CSV create')
        save_csv_file(df_out_PLCMfg, 'df_out_PLCMfg')
        save_csv_file(df_out_PLCSales, 'df_out_PLCSales')
        save_csv_file(df_out_PLCMfgSRAComDate, 'df_out_PLCMfgSRAComDate')
        save_csv_file(df_out_PLCMfgCTNEndDate, 'df_out_PLCMfgCTNEndDate')
        save_csv_file(df_out_PLCSalesRTSValidFlag, 'df_out_PLCSalesRTSValidFlag')

    step('=====> STEP 6-1 : output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_PLCMfg = pd.DataFrame([], columns=[])
    df_out_PLCSales = pd.DataFrame([], columns=[])
    df_out_PLCMfgSRAComDate = pd.DataFrame([], columns=[])
    df_out_PLCMfgCTNEndDate = pd.DataFrame([], columns=[])
    df_out_PLCSalesRTSValidFlag = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()