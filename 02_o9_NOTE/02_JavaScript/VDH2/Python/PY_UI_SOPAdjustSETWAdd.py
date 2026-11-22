"""
* 프로그램명 
    - PY_UI_SOPAdjustSETWAdd

* 내용
    - 
* 변경이력
    - 2026.04.03 / 양희영 / Create
    - 2026.04.03 / 양희영 / Update

* Flow Summary    

* Execution 

* Script Parameter    - 

* Input Tables
    - df_in_SOPAdjSETW : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Time].[Week] * [Trans Mode].[Trans Mode] ) on row, 
                         ({Measure.[SOP Adjust SET W_SOP Qty], Measure.[Dummy]}) on column;
    - df_in_SOPAdjSETSub : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] ) on row, 
                           ({Measure.[SOP Adjust SET Sub_SRA], Measure.[SOP Adjust SET Sub_EOP], Measure.[SOP Adjust SET Sub_Panel Block End], Measure.[SOP Adjust SET Sub_Panel Block Start], 
                           Measure.[SOP Adjust SET Sub_SET Block End], Measure.[SOP Adjust SET Sub_SET Block Start]}) on column;
    - df_in_CurrentWeek : Select (&CurrentWeek);
* Output Tables
    - df_out_SOPAdjSETW : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Time].[Week] * [Trans Mode].[Trans Mode] ) on row, 
                          ({Measure.[SOP Adjust SET W_DSR Detail1], Measure.[SOP Adjust SET W_DSR Detail2], Measure.[SOP Adjust SET W_DSR GO]}) on column;
    
* 테스트 스크립트
    EXEC plugin instance [PY_UI_SOPAdjustSETWAdd] for measures {[SOP Adjust SET W_DSR GO]} using scope (&MPV) 
     using arguments {("IncludeNullRows", "False"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
import warnings

warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SOPAdjustSETWAdd'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = "CWV_MP"
#paramOutVersion = (
#    "CWV_MP"
#    if is_local or not paramOutVersion or not paramOutVersion.strip()
#    else paramOutVersion
#)

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
    col_VersionName = 'Version.[Version Name]'
    col_Location = 'Location.[Location]'
    col_Item = 'Item.[Item]'
    col_ToLocation = 'To Location.[To Location]'
    col_TimeWeek = 'Time.[Week]'
    col_TransMode = 'Trans Mode.[Trans Mode]'
        
    #----------------------------------------------------------
    col_SETSub_SRA = 'SOP Adjust SET Sub_SRA'
    col_SETSub_EOP = 'SOP Adjust SET Sub_EOP'
    
    col_SETSub_PanelBlockStart = 'SOP Adjust SET Sub_Panel Block Start'
    col_SETSub_PanelBlockEnd   = 'SOP Adjust SET Sub_Panel Block End'
    col_SETSub_SETBlockStart   = 'SOP Adjust SET Sub_SET Block Start'
    col_SETSub_SETBlockEnd     = 'SOP Adjust SET Sub_SET Block End'
    
    col_DSRDetail1 = 'SOP Adjust SET W_DSR Detail1'
    col_DSRDetail2 = 'SOP Adjust SET W_DSR Detail2'
    col_DSRGO      = 'SOP Adjust SET W_DSR GO'
        
    # 칼럼 List 설정
    cList_V_L_I = [col_VersionName, col_Location, col_Item]
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    
    # 데이터 파일 읽기
    if is_local:
        df_in_SOPAdjSETW = read_csv_file("df_in_SOPAdjSETW")
        df_in_SOPAdjSETSub = read_csv_file("df_in_SOPAdjSETSub")
        df_in_CurrentWeek = read_csv_file("df_in_CurrentWeek")
    
    print_df(df_in_SOPAdjSETW, 'df_in_SOPAdjSETW', False)
    print_df(df_in_SOPAdjSETSub, 'df_in_SOPAdjSETSub', False)
    print_df(df_in_CurrentWeek, 'df_in_CurrentWeek', False)
    
    step('=====> STEP 0-3 : Input table load End')
    
    # DATA TYPE 설정
    if df_in_SOPAdjSETW[col_TimeWeek].dtype != 'int64':
        df_in_SOPAdjSETW[col_TimeWeek] = df_in_SOPAdjSETW[col_TimeWeek].fillna(0).astype('int64')
        
    if df_in_CurrentWeek[col_TimeWeek].dtype != 'int64':
        df_in_CurrentWeek[col_TimeWeek] = df_in_CurrentWeek[col_TimeWeek].fillna(0).astype('int64')
    
    df_in_CurrentWeek['CurrentWeek'] = df_in_CurrentWeek[col_TimeWeek]
    df_CurrentWeek = df_in_CurrentWeek[['CurrentWeek']]
    del df_in_CurrentWeek    
    print_df(df_CurrentWeek, 'df_CurrentWeek', False)
    
    ################################################################################################################
    # STEP 1 : df_in_SOPAdjSETW & df_CurrentWeek & df_in_SOPAdjSETSub  Merge
    ################################################################################################################
    step('=====> STEP 1 : df_in_SOPAdjSETW & df_CurrentWeek & df_in_SOPAdjSETSub  Merge')
    
    df_SOPAdjSETW = df_in_SOPAdjSETW.merge(df_CurrentWeek, how='cross')
    del [df_in_SOPAdjSETW, df_CurrentWeek]
    
    #Version.[Version Name]    Location.[Location]    Item.[Item]
    df_SOPAdjSETW = df_SOPAdjSETW.merge(df_in_SOPAdjSETSub, on=cList_V_L_I, how='left')
    del df_in_SOPAdjSETSub
    
    if df_SOPAdjSETW[col_SETSub_SRA].dtype != 'int64':
        df_SOPAdjSETW[col_SETSub_SRA] = df_SOPAdjSETW[col_SETSub_SRA].fillna(0).astype('int64')
    
    if df_SOPAdjSETW[col_SETSub_EOP].dtype != 'int64':
        df_SOPAdjSETW[col_SETSub_EOP] = df_SOPAdjSETW[col_SETSub_EOP].fillna(0).astype('int64')
    
    if df_SOPAdjSETW[col_SETSub_PanelBlockStart].dtype != 'int64':
        df_SOPAdjSETW[col_SETSub_PanelBlockStart] = df_SOPAdjSETW[col_SETSub_PanelBlockStart].fillna(0).astype('int64')
    
    if df_SOPAdjSETW[col_SETSub_PanelBlockEnd].dtype != 'int64':
        df_SOPAdjSETW[col_SETSub_PanelBlockEnd] = df_SOPAdjSETW[col_SETSub_PanelBlockEnd].fillna(0).astype('int64')
    
    if df_SOPAdjSETW[col_SETSub_SETBlockStart].dtype != 'int64':
        df_SOPAdjSETW[col_SETSub_SETBlockStart] = df_SOPAdjSETW[col_SETSub_SETBlockStart].fillna(0).astype('int64')
    
    if df_SOPAdjSETW[col_SETSub_SETBlockEnd].dtype != 'int64':
        df_SOPAdjSETW[col_SETSub_SETBlockEnd] = df_SOPAdjSETW[col_SETSub_SETBlockEnd].fillna(0).astype('int64')
    
    print_df(df_SOPAdjSETW, 'df_SOPAdjSETW - 1', False)
    
    ################################################################################################################
    # STEP 2 : SOP Adjust SET W_DSR Detail1, SOP Adjust SET W_DSR Detail2, SOP Adjust SET W_DSR GO
    ################################################################################################################
    step('=====> STEP 2 : SOP Adjust SET W_DSR Detail1, SOP Adjust SET W_DSR Detail2, SOP Adjust SET W_DSR GO  Create')
    
    #SOP Adjust SET W_DSR Detail1 : Time.[Week] 가 SOP Adjust SET Sub_SET Block Start ~ SOP Adjust SET Sub_SET Block End 기간 내 일 경우 1
    df_SOPAdjSETW[col_DSRDetail1] = np.where((df_SOPAdjSETW[col_SETSub_PanelBlockStart] != 0) &
                                             (df_SOPAdjSETW[col_SETSub_PanelBlockEnd] != 0) &
                                             ((df_SOPAdjSETW[col_TimeWeek] >= df_SOPAdjSETW[col_SETSub_PanelBlockStart]) &
                                             (df_SOPAdjSETW[col_TimeWeek] <= df_SOPAdjSETW[col_SETSub_PanelBlockEnd])),
                                             1, 2)
    
    #SOP Adjust SET W_DSR Detail2 : CurrentWeek < SOP Adjust SET Sub_SRA && CurrentWeek > SOP Adjust SET Sub_EOP
    df_SOPAdjSETW[col_DSRDetail2] = np.where((df_SOPAdjSETW[col_SETSub_SRA] != 0) &
                                             (df_SOPAdjSETW[col_SETSub_EOP] != 0) &
                                             (df_SOPAdjSETW['CurrentWeek'] != 0) &
                                             ((df_SOPAdjSETW['CurrentWeek'] < df_SOPAdjSETW[col_SETSub_SRA]) &
                                             (df_SOPAdjSETW['CurrentWeek'] > df_SOPAdjSETW[col_SETSub_EOP])),
                                             1, 2)
    
    #MIN(Measure.[SOP Adjust DSR W_DSR Detail 1],Measure.[SOP Adjust DSR W_DSR Detail 2])
    df_SOPAdjSETW[col_DSRGO] = df_SOPAdjSETW[[col_DSRDetail1, col_DSRDetail2]].min(axis=1)
    
    print_df(df_SOPAdjSETW, 'df_SOPAdjSETW - 2', False)
    
    ################################################################################################################
    # STEP 3 : output table create
    ################ ################################################################################################
    step('=====> STEP 3-1 : Final output table create')
    
    cList_All = [col_VersionName, col_Location, col_Item, col_ToLocation, col_TimeWeek, col_TransMode,
                 col_DSRDetail1, col_DSRDetail2, col_DSRGO]
    
    df_out_SOPAdjSETW = df_SOPAdjSETW[cList_All].copy()
    del df_SOPAdjSETW
    
    # 버전 처리
    # df_out_SOPAdjSETW[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_SOPAdjSETW.shape
    note(f'=====> Final df_out_SOPAdjSETW rows : {row_count}, column : {col_count}')
    print_df(df_out_SOPAdjSETW, 'df_out_SOPAdjSETW', False)
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_SOPAdjSETW, 'df_out_SOPAdjSETW')
    
    step('=====> STEP 3-2 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')
    
except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_SOPAdjSETW = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()