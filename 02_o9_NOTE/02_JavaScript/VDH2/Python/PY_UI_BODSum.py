"""
* 프로그램명 
    - PY_UI_BODSum

* 내용
    - BOD Sum 생성

* 변경이력
- 2024.08.16 / 양희영 / Create
- 2025.12.23 / 양희영 / Update

* Input
- df_in_Table = pd.read_csv(' .csv') 

* Flow Summary

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
    
* Input Tables
    - df_in_BODSumW   : BOD Sum W
                       Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] ) on row, 
                       ({Measure.[BOD Sum W_DC BOD LT], Measure.[BOD Sum W_DC Ship LT], Measure.[BOD Sum W_DC Total LT], 
                       Measure.[BOD Sum W_Hub BOD LT], Measure.[BOD Sum W_Hub Ship LT], Measure.[BOD Sum W_Hub Total LT], 
                       Measure.[BOD Sum W_KD BOD LT], Measure.[BOD Sum W_KD Ship LT], Measure.[BOD Sum W_KD Total LT], 
                       Measure.[BOD Sum W_LCM BOD LT], Measure.[BOD Sum W_LCM Ship LT], Measure.[BOD Sum W_LCM Total LT], 
                       Measure.[BOD Sum W_OCell BOD LT], Measure.[BOD Sum W_OCell Ship LT], Measure.[BOD Sum W_OCell Total LT], 
                       Measure.[BOD Sum W_SET BOD LT], Measure.[BOD Sum W_SET Ship LT], Measure.[BOD Sum W_SET Total LT], 
                       Measure.[BOD Sum W_Tot BOD LT], Measure.[BOD Sum W_Tot Ship LT], Measure.[BOD Sum W_Tot Total LT]}) on column;
    - df_in_BODAll : BOD All
                     Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] ) on row, 
                     ({Measure.[BOD All_BOD Prty], Measure.[BOD All_CH BOD LT], Measure.[BOD All_DC BOD LT], Measure.[BOD All_DC BOD Prty], Measure.[BOD All_DC Ship LT], 
                     Measure.[BOD All_DC Site], Measure.[BOD All_DC Trans Mode], Measure.[BOD All_DC Trans Time], Measure.[BOD All_Hub BOD LT], Measure.[BOD All_Hub BOD Prty], 
                     Measure.[BOD All_Hub Ship LT], Measure.[BOD All_Hub Site], Measure.[BOD All_Hub Trans Mode], Measure.[BOD All_Hub Trans Time], Measure.[BOD All_KD BOD LT], 
                     Measure.[BOD All_KD BOD Prty], Measure.[BOD All_KD Code], Measure.[BOD All_KD Ship LT], Measure.[BOD All_KD Site], Measure.[BOD All_KD Trans Mode], 
                     Measure.[BOD All_KD Trans Time], Measure.[BOD All_LCM BOD LT], Measure.[BOD All_LCM BOD Prty], Measure.[BOD All_LCM Code], Measure.[BOD All_LCM Ship LT], 
                     Measure.[BOD All_LCM Site], Measure.[BOD All_LCM Trans Mode], Measure.[BOD All_LCM Trans Time], Measure.[BOD All_Min LT Flag], Measure.[BOD All_OCell BOD LT], 
                     Measure.[BOD All_OCell BOD Prty], Measure.[BOD All_OCell Code], Measure.[BOD All_OCell Ship LT], Measure.[BOD All_OCell Site], Measure.[BOD All_OCell Trans Mode], 
                     Measure.[BOD All_OCell Trans Time], Measure.[BOD All_SET BOD LT], Measure.[BOD All_SET BOD Prty], Measure.[BOD All_SET BOM Version], Measure.[BOD All_SET SOP], 
                     Measure.[BOD All_SET Ship LT], Measure.[BOD All_SET Site], Measure.[BOD All_SET Trans Mode], Measure.[BOD All_SET Trans Time], Measure.[BOD All_Tot BOD LT], 
                     Measure.[BOD All_Tot Ship LT], Measure.[BOD All_Tot Trans Time]}) on column where {Measure.[BOD All_BOD Prty] == 1};

     -삭제 df_in_BODItemW : SELECT ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Time].[Week]) on row, ({Measure.[BOD Item W_Tran Time]}) on column limit 100;
    
* Output Tables
    - df_out_BODSum : Select ([Version].[Version Name]  * [Location].[Location] * [Item].[Item] * [Sequence].[Sequence] ) on row, 
                      ({Measure.[BOD Sum_CH BOD LT], Measure.[BOD Sum_DC BOD LT], Measure.[BOD Sum_DC Ship LT], Measure.[BOD Sum_DC Site], Measure.[BOD Sum_DC Total LT], 
                      Measure.[BOD Sum_DC Trans Mode], Measure.[BOD Sum_End Week], Measure.[BOD Sum_Hub BOD LT], Measure.[BOD Sum_Hub Ship LT], Measure.[BOD Sum_Hub Site], 
                      Measure.[BOD Sum_Hub Total LT], Measure.[BOD Sum_Hub Trans Mode], Measure.[BOD Sum_KD BOD LT], Measure.[BOD Sum_KD Code], Measure.[BOD Sum_KD Ship LT], 
                      Measure.[BOD Sum_KD Site], Measure.[BOD Sum_KD Total LT], Measure.[BOD Sum_KD Trans Mode], Measure.[BOD Sum_LCM BOD LT], Measure.[BOD Sum_LCM Code], 
                      Measure.[BOD Sum_LCM Ship LT], Measure.[BOD Sum_LCM Site], Measure.[BOD Sum_LCM Total LT], Measure.[BOD Sum_LCM Trans Mode], Measure.[BOD Sum_OCell BOD LT], 
                      Measure.[BOD Sum_OCell Code], Measure.[BOD Sum_OCell Ship LT], Measure.[BOD Sum_OCell Site], Measure.[BOD Sum_OCell Total LT], Measure.[BOD Sum_OCell Trans Mode], 
                      Measure.[BOD Sum_SET BOD LT], Measure.[BOD Sum_SET SOP], Measure.[BOD Sum_SET Ship LT], Measure.[BOD Sum_SET Site], Measure.[BOD Sum_SET Total LT], 
                      Measure.[BOD Sum_SET Trans Mode], Measure.[BOD Sum_Start Week], Measure.[BOD Sum_Tot BOD LT], Measure.[BOD Sum_Tot Ship LT], Measure.[BOD Sum_Tot Total LT]}) on column;


* 테스트 스크립트
    EXEC plugin instance [PY_UI_BODSum] for measures {[BOD Sum_Start Week]} using scope (&MPV)
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )} ;

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
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BODSum'
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
    step('=====> STEP 0-1 : DataFrame Column : 변수 처리')
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 컬럼 변수 선언
    versionVersionName     = 'Version.[Version Name]'
    itemItem               = 'Item.[Item]'
    locationLocation       = 'Location.[Location]'
    sequenceSequence       = 'Sequence.[Sequence]'
    subLocationSubLocation = 'Sub Location.[Sub Location]'
    transModeTransMode     = 'Trans Mode.[Trans Mode]'
    timeWeek               = 'Time.[Week]'
    
    #prevTotShipLT   = 'Prev Tot Ship LT'
    #nextTotShipLT   = 'Next Tot Ship LT'
    #tempTotShipLT   = 'Temp Tot Ship LT'
    
    #2025.11.18 추가
    prevTotLT       = 'Prev Tot LT' 
    nextTotLT       = 'Next Tot LT'
    tempTotLT       = 'Temp Tot LT'
    
    prevWeek        = 'Prev Week'
    nextWeek        = 'Next Week'
    startWeek       = 'Start Week'
    endWeek         = 'End Week'
    prevStartWeek   = 'Prev Start Week'
    
    #BOD Sum W
    bODSumW_TotTotalLT     = 'BOD Sum W_Tot Total LT' # Start Week, End Week 정하는 기준 값, 2025.12.02 추가
    bODSumW_TotBODLT       = 'BOD Sum W_Tot BOD LT' 
    #bODSumW_TotTransTime   = 'BOD Sum W_Tot Trans Time' #사용하지 않음. 2025.12.02
    bODSumW_TotShipLT      = 'BOD Sum W_Tot Ship LT' 
    bODSumW_DCBODLT        = 'BOD Sum W_DC BOD LT'
    #bODSumW_DCTransTime    = 'BOD Sum W_DC Trans Time' #사용하지 않음. 2025.12.02
    bODSumW_DCShipLT       = 'BOD Sum W_DC Ship LT'
    bODSumW_DCTotalLT      = 'BOD Sum W_DC Total LT' # 2025.12.02 추가
    bODSumW_HubBODLT       = 'BOD Sum W_Hub BOD LT'
    #bODSumW_HubTransTime   = 'BOD Sum W_Hub Trans Time' #사용하지 않음. 2025.12.02
    bODSumW_HubShipLT      = 'BOD Sum W_Hub Ship LT'
    bODSumW_HubTotalLT     = 'BOD Sum W_Hub Total LT' # 2025.12.02 추가
    bODSumW_SETBODLT       = 'BOD Sum W_SET BOD LT'
    #bODSumW_SETTransTime   = 'BOD Sum W_SET Trans Time' #사용하지 않음. 2025.12.02
    bODSumW_SETShipLT      = 'BOD Sum W_SET Ship LT'
    bODSumW_SETTotalLT     = 'BOD Sum W_SET Total LT' # 2025.12.02 추가
    bODSumW_KDBODLT        = 'BOD Sum W_KD BOD LT'
    #bODSumW_KDTransTime    = 'BOD Sum W_KD Trans Time' #사용하지 않음. 2025.12.02
    bODSumW_KDShipLT       = 'BOD Sum W_KD Ship LT'
    bODSumW_KDTotalLT      = 'BOD Sum W_KD Total LT' # 2025.12.02 추가
    bODSumW_LCMBODLT       = 'BOD Sum W_LCM BOD LT'
    #bODSumW_LCMTransTime   = 'BOD Sum W_LCM Trans Time' #사용하지 않음. 2025.12.02
    bODSumW_LCMShipLT      = 'BOD Sum W_LCM Ship LT'
    bODSumW_LCMTotalLT     = 'BOD Sum W_LCM Total LT' # 2025.12.02 추가
    bODSumW_OCellBODLT     = 'BOD Sum W_OCell BOD LT'
    #bODSumW_OCellTransTime = 'BOD Sum W_OCell Trans Time' #사용하지 않음. 2025.12.02
    bODSumW_OCellShipLT    = 'BOD Sum W_OCell Ship LT'
    bODSumW_OCellTotalLT   = 'BOD Sum W_OCell Total LT' # 2025.12.02 추가
    bODSumW_OCellCode      = 'BOD Sum W_OCell Code'

    #BOD All
    bODAll_CHBODLT         = 'BOD All_CH BOD LT' # 2025.12.23 추가
    bODAll_DCSite          = 'BOD All_DC Site'
    bODAll_DCTransMode     = 'BOD All_DC Trans Mode'
    bODAll_HubSite         = 'BOD All_Hub Site'
    bODAll_HubTransMode    = 'BOD All_Hub Trans Mode'
    bODAll_SETSite         = 'BOD All_SET Site'
    bODAll_SETTransMode    = 'BOD All_SET Trans Mode'
    bODAll_KDSite          = 'BOD All_KD Site'
    bODAll_KDTransMode     = 'BOD All_KD Trans Mode'
    bODAll_KDCode          = 'BOD All_KD Code'
    bODAll_LCMSite         = 'BOD All_LCM Site'
    bODAll_LCMTransMode    = 'BOD All_LCM Trans Mode'
    bODAll_LCMCode         = 'BOD All_LCM Code'
    bODAll_OCellSite       = 'BOD All_OCell Site'
    bODAll_OCellTransMode  = 'BOD All_OCell Trans Mode'
    bODAll_OCellCode       = 'BOD All_OCell Code'
    bODAll_SETSOP          = 'BOD All_SET SOP'
    
    #BOD Sum
    bODSum_CHBODLT        = 'BOD Sum_CH BOD LT' # 2025.12.23 추가
    bODSum_StartWeek      = 'BOD Sum_Start Week'
    bODSum_EndWeek        = 'BOD Sum_End Week'
    bODSum_TotTotalLT     = 'BOD Sum_Tot Total LT' # 2025.12.02 추가
    bODSum_TotBODLT       = 'BOD Sum_Tot BOD LT'
    #bODSum_TotTransTime   = 'BOD Sum_Tot Trans Time' #사용하지 않음. 2025.12.02
    bODSum_TotShipLT      = 'BOD Sum_Tot Ship LT'
    bODSum_DCSite         = 'BOD Sum_DC Site'
    bODSum_DCTransMode    = 'BOD Sum_DC Trans Mode'
    bODSum_DCBODLT        = 'BOD Sum_DC BOD LT'
    #bODSum_DCTransTime    = 'BOD Sum_DC Trans Time' #사용하지 않음. 2025.12.02
    bODSum_DCShipLT       = 'BOD Sum_DC Ship LT'
    bODSum_DCTotalLT      = 'BOD Sum_DC Total LT' # 2025.12.02 추가
    bODSum_HubSite        = 'BOD Sum_Hub Site'
    bODSum_HubTransMode   = 'BOD Sum_Hub Trans Mode'
    bODSum_HubBODLT       = 'BOD Sum_Hub BOD LT'
    #bODSum_HubTransTime   = 'BOD Sum_Hub Trans Time' #사용하지 않음. 2025.12.02
    bODSum_HubShipLT      = 'BOD Sum_Hub Ship LT'
    bODSum_HubTotalLT     = 'BOD Sum_Hub Total LT' # 2025.12.02 추가
    bODSum_SETSOP         = 'BOD Sum_SET SOP'
    bODSum_SETSite        = 'BOD Sum_SET Site'
    bODSum_SETTransMode   = 'BOD Sum_SET Trans Mode'
    bODSum_SETBODLT       = 'BOD Sum_SET BOD LT'
    #bODSum_SETTransTime   = 'BOD Sum_SET Trans Time' #사용하지 않음. 2025.12.02
    bODSum_SETShipLT      = 'BOD Sum_SET Ship LT'
    bODSum_SETTotalLT     = 'BOD Sum_SET Total LT' # 2025.12.02 추가
    bODSum_KDSite         = 'BOD Sum_KD Site'
    bODSum_KDTransMode    = 'BOD Sum_KD Trans Mode'
    bODSum_KDBODLT        = 'BOD Sum_KD BOD LT'
    #bODSum_KDTransTime    = 'BOD Sum_KD Trans Time' #사용하지 않음. 2025.12.02
    bODSum_KDShipLT       = 'BOD Sum_KD Ship LT'
    bODSum_KDTotalLT      = 'BOD Sum_KD Total LT' # 2025.12.02 추가
    bODSum_KDCode         = 'BOD Sum_KD Code'
    bODSum_LCMSite        = 'BOD Sum_LCM Site'
    bODSum_LCMTransMode   = 'BOD Sum_LCM Trans Mode'
    bODSum_LCMBODLT       = 'BOD Sum_LCM BOD LT'
    #bODSum_LCMTransTime   = 'BOD Sum_LCM Trans Time' #사용하지 않음. 2025.12.02
    bODSum_LCMShipLT      = 'BOD Sum_LCM Ship LT'
    bODSum_LCMTotalLT     = 'BOD Sum_LCM Total LT' # 2025.12.02 추가
    bODSum_LCMCode        = 'BOD Sum_LCM Code'
    bODSum_OCellSite      = 'BOD Sum_OCell Site'
    bODSum_OCellTransMode = 'BOD Sum_OCell Trans Mode'
    bODSum_OCellBODLT     = 'BOD Sum_OCell BOD LT'
    #bODSum_OCellTransTime = 'BOD Sum_OCell Trans Time' #사용하지 않음. 2025.12.02
    bODSum_OCellShipLT    = 'BOD Sum_OCell Ship LT'
    bODSum_OCellTotalLT   = 'BOD Sum_OCell Total LT' # 2025.12.02 추가
    bODSum_OCellCode      = 'BOD Sum_OCell Code'

    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : 전처리 : Input table load')
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_BODSumW  = read_csv_file("df_in_BODSumW")
        df_in_BODAll   = read_csv_file("df_in_BODAll")
    
    #if df_in_BODSumW.empty:
    #    raise Exception("=====> raise Exception: df_in_BODSumW is empty")
    
    #if df_in_BODAll.empty:
    #    raise Exception("=====> raise Exception: df_in_BODAll is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    df_in_BODSumW = df_in_BODSumW.astype({timeWeek: 'str'}, copy=True)
    
    # null 비교를 위해 'Temp Tot Ship LT' 를 활용
    # df_in_BODSumW[bODSumW_TotShipLT] = np.nan
    #df_in_BODSumW[tempTotShipLT] = df_in_BODSumW[bODSumW_TotShipLT]
    #df_in_BODSumW.fillna({tempTotShipLT: -999}, inplace=True)
    
    # null 비교를 위해 'Temp Tot LT' 를 활용
    # df_in_BODSumW[bODSumW_TotBODLT] = np.nan
    #df_in_BODSumW[tempTotLT] = df_in_BODSumW[bODSumW_TotBODLT]
    df_in_BODSumW[tempTotLT] = df_in_BODSumW[bODSumW_TotTotalLT] # 기준값 [BOD Sum W_Tot Total LT] 로 수정, 2025.12.02
    df_in_BODSumW.fillna({tempTotLT: -999}, inplace=True)
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    print_df(df_in_BODSumW, 'df_in_BODSumW', False)
    print_df(df_in_BODAll, 'df_in_BODAll', False)
    
    step('=====> STEP 0-3 : 전처리 : Input table load End')
    
    ################################################################################################################
    # STEP 1 :  Week Summary 데이터 생성
    ################################################################################################################
    step('=====> STEP 1-1 : Week Summary Data Create')
    df_week_summary = df_in_BODSumW.copy()
    del df_in_BODSumW
    
    # 초기 정렬
    df_week_summary.sort_values(by=[versionVersionName, itemItem, locationLocation, timeWeek], ascending=True, axis=0, inplace=True)
    
    # 이전 Tot BOD LT , 다음 Tot BOD LT 구하기 : Tot Ship LT ==> Tot BOD LT 변경 2025.11.18
    #df_week_summary[prevTotShipLT] = df_week_summary.sort_values(by=timeWeek, ascending=True).groupby([versionVersionName, itemItem, locationLocation])[tempTotShipLT].shift(1)
    #df_week_summary[nextTotShipLT] = df_week_summary.sort_values(by=timeWeek, ascending=False).groupby([versionVersionName, itemItem, locationLocation])[tempTotShipLT].shift(1)
    df_week_summary[prevTotLT] = df_week_summary.sort_values(by=timeWeek, ascending=True).groupby([versionVersionName, itemItem, locationLocation])[tempTotLT].shift(1)
    df_week_summary[nextTotLT] = df_week_summary.sort_values(by=timeWeek, ascending=False).groupby([versionVersionName, itemItem, locationLocation])[tempTotLT].shift(1)
    
    # Start Week, End Week 구하기 : Tot BOD LT이 이전 Tot BOD LT 과 다르면 Start Week, 다음 Tot BOD LT 와 다르면 End Week 값 입력. : Tot Ship LT ==> Tot BOD LT 변경 2025.11.18
    #df_week_summary[startWeek] = np.select([(df_week_summary[prevTotShipLT] != df_week_summary[tempTotShipLT]), True], [df_week_summary[timeWeek], np.nan])
    #df_week_summary[endWeek]   = np.select([(df_week_summary[nextTotShipLT] != df_week_summary[tempTotShipLT]), True], [df_week_summary[timeWeek], np.nan])
    df_week_summary[startWeek] = np.select([(df_week_summary[prevTotLT] != df_week_summary[tempTotLT]), True], [df_week_summary[timeWeek], np.nan])
    df_week_summary[endWeek]   = np.select([(df_week_summary[nextTotLT] != df_week_summary[tempTotLT]), True], [df_week_summary[timeWeek], np.nan])
    #print_df(df_week_summary, 'df_week_summary_1', True)
    
    # Tot Ship LT 값이 변하지 않은 Week 제외, Start Week, End Week 값이 있는 Data 만 선택 
    df_week_summary = df_week_summary.loc[df_week_summary[startWeek].notna() | df_week_summary[endWeek].notna()].copy()
    
    #이전 Start Week 구하여 Start Week 값이 없는 경우 이전 Start Week 값으로 입력.
    df_week_summary[prevStartWeek] = df_week_summary.sort_values(by=timeWeek, ascending=True).groupby([versionVersionName, itemItem, locationLocation])[startWeek].shift(1)
    df_week_summary[startWeek]     = np.select([(df_week_summary[startWeek].isna()), True],[df_week_summary[prevStartWeek], df_week_summary[startWeek]])
    #print_df(df_week_summary, 'df_week_summary_2', True)
    
    # Start Week, End Week 값이 모두 있는 data만 선택
    df_week_summary = df_week_summary.loc[df_week_summary[endWeek].notna()].copy()
    
    #df_week_summary[bODSum_SETSOP] = 0 # TBD(미정), 0으로 Setting : [BOD All_SET SOP] 으로 입력(20250408)
    # 칼럼 조정    
    df_week_summary = df_week_summary[[versionVersionName, itemItem, locationLocation, #sequenceSequence,
                                       startWeek, endWeek, #bODSum_SETSOP, # bODSum_SETSOP <-- bODAll_SETSOP 로 입력
                                       bODSumW_TotBODLT, bODSumW_TotShipLT, bODSumW_TotTotalLT, #bODSumW_TotTransTime, 
                                       bODSumW_DCBODLT, bODSumW_DCShipLT, bODSumW_DCTotalLT, #bODSumW_DCTransTime, 
                                       bODSumW_HubBODLT, bODSumW_HubShipLT, bODSumW_HubTotalLT, #bODSumW_HubTransTime, 
                                       bODSumW_SETBODLT, bODSumW_SETShipLT, bODSumW_SETTotalLT, #bODSumW_SETTransTime, 
                                       bODSumW_KDBODLT, bODSumW_KDShipLT, bODSumW_KDTotalLT, #bODSumW_KDTransTime, 
                                       bODSumW_LCMBODLT, bODSumW_LCMShipLT, bODSumW_LCMTotalLT, #bODSumW_LCMTransTime, 
                                       bODSumW_OCellBODLT, bODSumW_OCellShipLT, bODSumW_OCellTotalLT #,bODSumW_OCellTransTime
                                       ]]
    
    print_df(df_week_summary, 'df_week_summary', False)
    step('=====> STEP 1-2 : Week Summary Data Create End')
    
    ################################################################################################################
    # STEP 2 :  BOD Sum 데이터 생성
    ################################################################################################################
    step('=====> STEP 2-1 : BOD Sum Create')
    
    df_BODSum = df_week_summary.merge(df_in_BODAll,
                                      on=[versionVersionName, itemItem, locationLocation],
                                      how='inner', suffixes=('', '_y'), )
    del [df_week_summary, df_in_BODAll]
    
    df_BODSum.rename(columns={startWeek: bODSum_StartWeek, endWeek: bODSum_EndWeek,
                              bODAll_SETSOP : bODSum_SETSOP,
                              bODSumW_TotBODLT: bODSum_TotBODLT, bODSumW_TotShipLT: bODSum_TotShipLT, 
                              bODSumW_TotTotalLT: bODSum_TotTotalLT, #bODSumW_TotTransTime: bODSum_TotTransTime,
                              bODAll_CHBODLT: bODSum_CHBODLT,
                              # DC
                              bODAll_DCSite: bODSum_DCSite, bODAll_DCTransMode: bODSum_DCTransMode, 
                              bODSumW_DCBODLT: bODSum_DCBODLT, bODSumW_DCShipLT: bODSum_DCShipLT, 
                              bODSumW_DCTotalLT: bODSum_DCTotalLT, #bODSumW_DCTransTime: bODSum_DCTransTime,
                              # Hub
                              bODAll_HubSite: bODSum_HubSite, bODAll_HubTransMode: bODSum_HubTransMode,
                              bODSumW_HubBODLT: bODSum_HubBODLT, bODSumW_HubShipLT: bODSum_HubShipLT, 
                              bODSumW_HubTotalLT: bODSum_HubTotalLT, #bODSumW_HubTransTime: bODSum_HubTransTime,
                              # SET
                              bODAll_SETSite: bODSum_SETSite, bODAll_SETTransMode: bODSum_SETTransMode , 
                              bODSumW_SETBODLT: bODSum_SETBODLT, bODSumW_SETShipLT: bODSum_SETShipLT, 
                              bODSumW_SETTotalLT: bODSum_SETTotalLT, #bODSumW_SETTransTime: bODSum_SETTransTime, 
                              # KD
                              bODAll_KDSite: bODSum_KDSite, bODAll_KDCode: bODSum_KDCode, 
                              bODAll_KDTransMode: bODSum_KDTransMode, bODSumW_KDBODLT: bODSum_KDBODLT, 
                              bODSumW_KDShipLT: bODSum_KDShipLT, bODSumW_KDTotalLT: bODSum_KDTotalLT, 
                              #bODSumW_KDTransTime: bODSum_KDTransTime, 
                              # LCM
                              bODAll_LCMSite: bODSum_LCMSite, bODAll_LCMCode: bODSum_LCMCode,
                              bODAll_LCMTransMode: bODSum_LCMTransMode, bODSumW_LCMBODLT: bODSum_LCMBODLT, 
                              bODSumW_LCMShipLT: bODSum_LCMShipLT, bODSumW_LCMTotalLT: bODSum_LCMTotalLT, 
                              #bODSumW_LCMTransTime: bODSum_LCMTransTime, 
                              # OCell
                              bODAll_OCellSite: bODSum_OCellSite, bODAll_OCellCode:bODSum_OCellCode,
                              bODAll_OCellTransMode: bODSum_OCellTransMode, bODSumW_OCellBODLT: bODSum_OCellBODLT, 
                              bODSumW_OCellShipLT: bODSum_OCellShipLT, bODSumW_OCellTotalLT: bODSum_OCellTotalLT 
                              #,bODSumW_OCellTransTime: bODSum_OCellTransTime
                              }, inplace=True)
    
    df_BODSum = df_BODSum[[versionVersionName, itemItem, locationLocation, #sequenceSequence,
                           bODSum_StartWeek, bODSum_EndWeek, bODSum_TotBODLT, 
                           bODSum_TotShipLT, bODSum_TotTotalLT, #bODSum_TotTransTime, 
                           bODSum_CHBODLT,
                           # DC
                           bODSum_DCSite, bODSum_DCTransMode, bODSum_DCBODLT, 
                           bODSum_DCShipLT, bODSum_DCTotalLT, #bODSum_DCTransTime, 
                           # Hub
                           bODSum_HubSite, bODSum_HubTransMode, bODSum_HubBODLT, 
                           bODSum_HubShipLT, bODSum_HubTotalLT, #bODSum_HubTransTime, 
                           # SET
                           bODSum_SETSite, bODSum_SETSOP, bODSum_SETTransMode, bODSum_SETBODLT, 
                           bODSum_SETShipLT, bODSum_SETTotalLT, #bODSum_SETTransTime, 
                           # KD
                           bODSum_KDSite, bODSum_KDCode, bODSum_KDTransMode, bODSum_KDBODLT, 
                           bODSum_KDShipLT, bODSum_KDTotalLT, #bODSum_KDTransTime, 
                           # LCM
                           bODSum_LCMSite, bODSum_LCMCode, bODSum_LCMTransMode, bODSum_LCMBODLT, 
                           bODSum_LCMShipLT, bODSum_LCMTotalLT, #bODSum_LCMTransTime, 
                           # OCell
                           bODSum_OCellSite, bODSum_OCellCode, bODSum_OCellTransMode, bODSum_OCellBODLT, 
                           bODSum_OCellShipLT, bODSum_OCellTotalLT #,bODSum_OCellTransTime
                           ]].copy(deep=True)
    
    df_BODSum.drop_duplicates(inplace=True)
    df_BODSum[sequenceSequence] = df_BODSum.groupby([versionVersionName, itemItem, locationLocation]).cumcount() + 1
    
    
    #추가 NULL 처리(2025.11.04, 임채수프로요청) ##########################################################################
    #1. BOD LT, TRANS TIME, SHIP LT 필드의 경우 SITE코드가 없는 경우 Null 처리 부탁드립니다. (추가 확인 : TP Mode 포함)
    #2. DC 정보의 경우 DC Site Code가 있더라도 BOD LT, TRANS TIME, SHIP LT, TP MODE 값은 Null 처리 (추가 확인 : DC Site Code  NULL , NOT NULL 무관하게 NULL 처리)
    #3. HUB정보의 경우 DC Site Code가 없을때 BOD LT, TRANS TIME, SHIP LT, TP MODE 값은 Null 처리 (추가 확인 : DC가 없다는 것은 hub가 최종 도착지라는 의미)
    
    # DC
    df_BODSum[bODSum_DCBODLT]     = np.nan
    df_BODSum[bODSum_DCShipLT]    = np.nan
    df_BODSum[bODSum_DCTotalLT]   = np.nan
    df_BODSum[bODSum_DCTransMode] = np.nan
    #df_BODSum[bODSum_DCTransTime] = np.nan
    
    # Hub
    df_BODSum[bODSum_HubBODLT]     = np.where(df_BODSum[bODSum_HubSite].isna() | df_BODSum[bODSum_DCSite].isna(),
                                              np.nan,
                                              df_BODSum[bODSum_HubBODLT])
    df_BODSum[bODSum_HubShipLT]    = np.where(df_BODSum[bODSum_HubSite].isna() | df_BODSum[bODSum_DCSite].isna(),
                                              np.nan,
                                              df_BODSum[bODSum_HubShipLT])
    df_BODSum[bODSum_HubTotalLT]  = np.where(df_BODSum[bODSum_HubSite].isna() | df_BODSum[bODSum_DCSite].isna(),
                                             np.nan,
                                             df_BODSum[bODSum_HubTotalLT])
    df_BODSum[bODSum_HubTransMode] = np.where(df_BODSum[bODSum_HubSite].isna() | df_BODSum[bODSum_DCSite].isna(),
                                              np.nan,
                                              df_BODSum[bODSum_HubTransMode])
    #df_BODSum[bODSum_HubTransTime] = np.where(df_BODSum[bODSum_HubSite].isna() | df_BODSum[bODSum_DCSite].isna(),
    #                                          np.nan,
    #                                          df_BODSum[bODSum_HubTransTime])
    
    # SET
    df_BODSum[bODSum_SETBODLT]     = np.where(df_BODSum[bODSum_SETSite].isna(), np.nan, df_BODSum[bODSum_SETBODLT])
    df_BODSum[bODSum_SETShipLT]    = np.where(df_BODSum[bODSum_SETSite].isna(), np.nan, df_BODSum[bODSum_SETShipLT])
    df_BODSum[bODSum_SETTotalLT]   = np.where(df_BODSum[bODSum_SETSite].isna(), np.nan, df_BODSum[bODSum_SETTotalLT])
    df_BODSum[bODSum_SETTransMode] = np.where(df_BODSum[bODSum_SETSite].isna(), np.nan, df_BODSum[bODSum_SETTransMode])
    #df_BODSum[bODSum_SETTransTime] = np.where(df_BODSum[bODSum_SETSite].isna(), np.nan, df_BODSum[bODSum_SETTransTime])
    
    # KD
    df_BODSum[bODSum_KDBODLT]     = np.where(df_BODSum[bODSum_KDSite].isna(), np.nan, df_BODSum[bODSum_KDBODLT])
    df_BODSum[bODSum_KDShipLT]    = np.where(df_BODSum[bODSum_KDSite].isna(), np.nan, df_BODSum[bODSum_KDShipLT])
    df_BODSum[bODSum_KDTotalLT]   = np.where(df_BODSum[bODSum_KDSite].isna(), np.nan, df_BODSum[bODSum_KDTotalLT])
    df_BODSum[bODSum_KDTransMode] = np.where(df_BODSum[bODSum_KDSite].isna(), np.nan, df_BODSum[bODSum_KDTransMode])
    #df_BODSum[bODSum_KDTransTime] = np.where(df_BODSum[bODSum_KDSite].isna(), np.nan, df_BODSum[bODSum_KDTransTime])
    
    # LCM
    df_BODSum[bODSum_LCMBODLT]     = np.where(df_BODSum[bODSum_LCMSite].isna(), np.nan, df_BODSum[bODSum_LCMBODLT])
    df_BODSum[bODSum_LCMShipLT]    = np.where(df_BODSum[bODSum_LCMSite].isna(), np.nan, df_BODSum[bODSum_LCMShipLT])
    df_BODSum[bODSum_LCMTotalLT]   = np.where(df_BODSum[bODSum_LCMSite].isna(), np.nan, df_BODSum[bODSum_LCMTotalLT])
    df_BODSum[bODSum_LCMTransMode] = np.where(df_BODSum[bODSum_LCMSite].isna(), np.nan, df_BODSum[bODSum_LCMTransMode])
    #df_BODSum[bODSum_LCMTransTime] = np.where(df_BODSum[bODSum_LCMSite].isna(), np.nan, df_BODSum[bODSum_LCMTransTime])
    
    # OCell
    df_BODSum[bODSum_OCellBODLT]     = np.where(df_BODSum[bODSum_OCellSite].isna(), np.nan, df_BODSum[bODSum_OCellBODLT])
    df_BODSum[bODSum_OCellShipLT]    = np.where(df_BODSum[bODSum_OCellSite].isna(), np.nan, df_BODSum[bODSum_OCellShipLT])
    df_BODSum[bODSum_OCellTotalLT]   = np.where(df_BODSum[bODSum_OCellSite].isna(), np.nan, df_BODSum[bODSum_OCellTotalLT])
    df_BODSum[bODSum_OCellTransMode] = np.where(df_BODSum[bODSum_OCellSite].isna(), np.nan, df_BODSum[bODSum_OCellTransMode])
    #df_BODSum[bODSum_OCellTransTime] = np.where(df_BODSum[bODSum_OCellSite].isna(), np.nan, df_BODSum[bODSum_OCellTransTime])
    
    ###################################################################################################################
    
    print_df(df_BODSum, 'df_BODSum', False)
    
    step('=====> STEP 2-2 : BOD Sum Create End')
    ################################################################################################################
    # STEP 3 : : output table create
    ################################################################################################################
    step('=====> STEP 3-1 : output table create')
    
    # out Data 생성 :    
    df_out_BODSum = df_BODSum.copy()
    del df_BODSum
    
    # out Data 설정
    df_out_BODSum = df_out_BODSum[[versionVersionName, itemItem, locationLocation, sequenceSequence,
                                   bODSum_StartWeek, bODSum_EndWeek, bODSum_CHBODLT,
                                   # Reporting Measure 주석처리, 2025.12.02
                                   # bODSum_TotBODLT, bODSum_TotShipLT, bODSum_TotTotalLT, #bODSum_TotTransTime,
                                   # DC
                                   bODSum_DCSite, bODSum_DCTransMode, bODSum_DCBODLT,
                                   bODSum_DCShipLT, bODSum_DCTotalLT, #bODSum_DCTransTime, 
                                   # Hub
                                   bODSum_HubSite, bODSum_HubTransMode, bODSum_HubBODLT, 
                                   bODSum_HubShipLT, bODSum_HubTotalLT, #bODSum_HubTransTime, 
                                   # SET
                                   bODSum_SETSite,  bODSum_SETSOP, bODSum_SETTransMode, bODSum_SETBODLT, 
                                   bODSum_SETShipLT, bODSum_SETTotalLT, #bODSum_SETTransTime, 
                                   # KD
                                   bODSum_KDSite, bODSum_KDCode, bODSum_KDTransMode, bODSum_KDBODLT, 
                                   bODSum_KDShipLT, bODSum_KDTotalLT, #bODSum_KDTransTime, 
                                   # LCM
                                   bODSum_LCMSite, bODSum_LCMCode, bODSum_LCMTransMode, bODSum_LCMBODLT, 
                                   bODSum_LCMShipLT, bODSum_LCMTotalLT, #bODSum_LCMTransTime, 
                                   # OCell
                                   bODSum_OCellSite, bODSum_OCellCode, bODSum_OCellTransMode, bODSum_OCellBODLT, 
                                   bODSum_OCellShipLT, bODSum_OCellTotalLT #,bODSum_OCellTransTime, 
                                   ]].copy(deep=True)
    
    row_count, col_count = df_out_BODSum.shape
    note(f'=====> Final df_out_BODSum rows : {row_count}, column : {col_count}')    
    print_df(df_out_BODSum, 'df_out_BODSum', False)
    step('=====> STEP 3-2 : output table create End')
    
    if is_local:
        step('=====> Output CSV create')
        save_csv_file(df_out_BODSum, 'df_out_BODSum')    
    
    step('=====> STEP 3-3 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_BODSum = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()