"""
* 프로그램명 
    - PY_UI_SOPAdjustPreProcess

* 내용
    - 

* 변경이력
    - 2025.09.05 / 양희영 / Create
    - 2025.09.24 / 양희영 / Update

* Flow Summary
    

* Execution 

* Script Parameter
    - 

* Input Tables
    - df_in_SOPW : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [To Time].[To Week] * 
                           [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * 
                           [BOM Info].[BOM Version] * [Week2].[Week2] * [To Trans Mode].[To Trans Mode] * [Trans Mode].[Trans Mode] ) on row, 
                   ({Measure.[SOP W_BLD], Measure.[SOP W_BOD Name], Measure.[SOP W_BOM Cfm W], Measure.[SOP W_BOM Status], Measure.[SOP W_CO Qty], Measure.[SOP W_CY Qty], Measure.[SOP W_Chg Reason], 
                     Measure.[SOP W_FP Qty], Measure.[SOP W_JIT], Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], 
                     Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM Plant BOH Qty], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP ID], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_New Model MP], 
                     Measure.[SOP W_New Model RTS], Measure.[SOP W_New Model SR], Measure.[SOP W_PB Qty], Measure.[SOP W_PY Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], 
                     Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID], Measure.[SOP W_SS], Measure.[SOP W_Sht Qty], Measure.[SOP W_Sht Reason]}) on column;

    - df_in_SafetyStockMonitoring : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                                   ({Measure.[SS Monitor_Shipment BuildAhead], Measure.[SS Monitor_Shipment JIT], Measure.[SS Monitor_Shipment SS]}) on column;

    - df_in_NewModel : Select ([Version].[Version Name] * [Location].[Location] * [Sales Domain].[AP2] * [Category].[Category] * [Item New Model].[Item] ) on row, 
                       ({Measure.[New Model_SET MP], Measure.[New Model_Sales RTS], Measure.[New Model_SET SR]}) on column;

* Output Tables
    - df_out_SOPW : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [To Time].[To Week] * 
                           [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * 
                           [BOM Info].[BOM Version] * [Week2].[Week2] * [To Trans Mode].[To Trans Mode] * [Trans Mode].[Trans Mode] ) on row, 
                    ({Measure.[SOP W_BLD], Measure.[SOP W_JIT], Measure.[SOP W_SS],
                      Measure.[SOP W_BOM Cfm W], Measure.[SOP W_BOM Status], 
                      Measure.[SOP W_New Model MP], Measure.[SOP W_New Model RTS], Measure.[SOP W_New Model SR]}) on column;
    
* 테스트 스크립트
    EXEC plugin instance [PY_UI_SOPAdjustPreProcess] for measures {[SOP W_BLD]} using scope (&MPV) 
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
str_instance = 'PY_UI_SOPAdjustPreProcess'
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
    col_TimeWeek = 'Time.[Week]'
    col_ToLocation = 'To Location.[To Location]'
    col_ToItem = 'To Item.[To Item]'
    col_ToWeek = 'To Time.[To Week]'
    col_Sequence = 'Sequence.[Sequence]'
    col_Week1 = 'Week1.[Week1]'
    col_Week2 = 'Week2.[Week2]'
    col_ItemMaterial = 'Item Material.[Item Material]'
    col_SubLocation = 'Sub Location.[Sub Location]'
    col_ItemComponent = 'Item Component.[Item Component]'
    col_BOMVersion = 'BOM Info.[BOM Version]'
    col_TransMode = 'Trans Mode.[Trans Mode]'
    col_ToTransMode = 'To Trans Mode.[To Trans Mode]'
    col_AP2 ='Sales Domain.[AP2]'
    col_Status = 'Status.[Status]'
    col_BOMType = 'BOM Type.[BOM Type]'
    col_BOMStatus = 'BOM Status.[BOM Status]'
    col_Category = 'Category.[Category]'
    col_NewModelItem = 'Item New Model.[Item]'
    
    col_SOPW_BLD = 'SOP W_BLD'
    col_SOPW_JIT = 'SOP W_JIT'
    col_SOPW_SS  = 'SOP W_SS'
    col_SOPW_BOMCfmW   = 'SOP W_BOM Cfm W'
    col_SOPW_BOMStatus = 'SOP W_BOM Status'
    col_SOPW_NewModelMP  = 'SOP W_New Model MP'
    col_SOPW_NewModelRTS = 'SOP W_New Model RTS'
    col_SOPW_NewModelSR  = 'SOP W_New Model SR'

    col_SSMonitor_ShipmentBuildAhead = 'SS Monitor_Shipment BuildAhead'
    col_SSMonitor_ShipmentJIT = 'SS Monitor_Shipment JIT'
    col_SSMonitor_ShipmentSS = 'SS Monitor_Shipment SS'
    
    col_NewModel_SETMP    = 'New Model_SET MP'
    col_NewModel_SalesRTS = 'New Model_Sales RTS'
    col_NewModel_SETSR = 'New Model_SET SR'
    
    # 칼럼 List 설정
    cList_SOPW = [col_VersionName, col_Location, col_Item, col_TimeWeek, col_ToLocation, col_ToItem, col_ToWeek,
                  col_Sequence, col_ItemMaterial, col_SubLocation, col_ItemComponent, col_BOMVersion,
                  col_Week1, col_Week2, col_ToTransMode, col_TransMode,
                  col_SOPW_BLD, col_SOPW_JIT, col_SOPW_SS,
                  col_SOPW_NewModelMP, col_SOPW_NewModelRTS, col_SOPW_NewModelSR]
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    
    # 데이터 파일 읽기
    if is_local:
        df_in_SOPW = read_csv_file("df_in_SOPW")
        df_in_SafetyStockMonitoring = read_csv_file("df_in_SafetyStockMonitoring")
        df_in_NewModel = read_csv_file("df_in_NewModel")
    
    print_df(df_in_SOPW, 'df_in_SOPW', False)
    print_df(df_in_SafetyStockMonitoring, 'df_in_SafetyStockMonitoring', False)
    print_df(df_in_NewModel, 'df_in_NewModel', False)
    
    step('=====> STEP 0-3 : Input table load End')
    # DATA TYPE 설정
    #df_in_SOPW.fillna(value={col_SOPW_BLD: 0, col_SOPW_JIT: 0, col_SOPW_SS: 0}, inplace=True)
    #df_in_SOPW = df_in_SOPW.astype({#col_SOPW_BLD: 'int64', col_SOPW_JIT: 'int64', col_SOPW_SS: 'int64', #int 는 fillna 선행되어야 함.
    #                                col_SOPW_BOMCfmW: 'str', col_SOPW_BOMStatus: 'str',
    #                                col_SOPW_NewModelMP: 'str', col_SOPW_NewModelRTS: 'str', col_SOPW_NewModelSR: 'str'}
    #                               , copy=True)
    # 'NA' 값을 nan 으로 읽어들임.
    df_in_SOPW[col_BOMVersion] = np.where(df_in_SOPW[col_BOMVersion].isna()
                                         , "NA", df_in_SOPW[col_BOMVersion])
    
    df_in_SOPW[col_SOPW_BOMCfmW] = np.where(df_in_SOPW[col_SOPW_BOMCfmW].notna(), 
                                            df_in_SOPW[col_SOPW_BOMCfmW].astype('str'), np.nan) # col_SOPW_BOMCfmW: 'str'로 바꾸면 nan이 문자로 입력됨.
    
    df_in_SafetyStockMonitoring.fillna(value={col_SSMonitor_ShipmentBuildAhead: 0, 
                                  col_SSMonitor_ShipmentJIT: 0, 
                                  col_SSMonitor_ShipmentSS: 0}, inplace=True)
    
    if df_in_NewModel[col_NewModel_SETMP].dtype != 'datetime64[ns]':
        df_in_NewModel[col_NewModel_SETMP] = pd.to_datetime(df_in_NewModel[col_NewModel_SETMP], format='%m/%d/%Y %I:%M:%S %p')
        
    if df_in_NewModel[col_NewModel_SalesRTS].dtype != 'datetime64[ns]':
        df_in_NewModel[col_NewModel_SalesRTS] = pd.to_datetime(df_in_NewModel[col_NewModel_SalesRTS], format='%m/%d/%Y %I:%M:%S %p')
    
    def cnvt_mixed_date(x):
        try:
            if len(x) == 8:
                #note(f'=====check x1 len: {x} ========')
                return pd.to_datetime(x, format='%Y%m%d', errors='coerce')
            elif '-' in x:
                #note(f'=====check x2: {x} ========')
                return pd.to_datetime(x, format='%Y-%m-%d', errors='coerce')
            elif '.' in x:
                #note(f'=====check x3: {x} ========')
                return pd.to_datetime(x, format='%Y.%m.%d', errors='coerce')
            else:
                #note(f'=====check x4: {x} ========')
                return pd.to_datetime(x, format='%Y%m%d', errors='coerce')
        except:
            return pd.NaT
    
    # float --> str 변환때 붙는 .0 제거
    if df_in_NewModel[col_NewModel_SETSR].dtype == 'float64':
        df_in_NewModel[col_NewModel_SETSR] = df_in_NewModel[col_NewModel_SETSR].astype('str').str.replace('.0', '')
    
    if df_in_NewModel[col_NewModel_SETSR].dtype != 'datetime64[ns]':
        df_in_NewModel[col_NewModel_SETSR] = df_in_NewModel[col_NewModel_SETSR].apply(cnvt_mixed_date)
    
    #칼럼 정리
    df_in_SOPW = df_in_SOPW[cList_SOPW]
    print_df(df_in_SOPW, 'df_in_SOPW 2', False)
    print_df(df_in_NewModel, 'df_in_NewModel 2', False)
    
    step('=====> STEP 0-3 : DATA TYPE End')
    
    ################################################################################################################
    # STEP 1 : SS Monitor Merge
    ################################################################################################################
    step('=====> STEP 1-1 :  SS Monitor Merge')
    cList_group=[col_VersionName, col_Location, col_Item, col_TimeWeek, col_SubLocation, col_TransMode]
    
    df_SSMonitor = df_in_SafetyStockMonitoring.groupby(cList_group, as_index=False).agg({col_SSMonitor_ShipmentBuildAhead: "max",
                                                                             col_SSMonitor_ShipmentJIT: "max",
                                                                             col_SSMonitor_ShipmentSS: "max"}
                                                                            , skipna=True).copy()
    del df_in_SafetyStockMonitoring
    df_SSMonitor.rename(columns={col_SubLocation:col_ToLocation}, inplace=True)
    print_df(df_SSMonitor, 'df_SSMonitor', False)
    
    cList_merge = [col_VersionName, col_Location, col_Item, col_TimeWeek, col_ToLocation, col_TransMode]
    df_SOPW = df_in_SOPW.merge(df_SSMonitor, on=cList_merge, how='left')
    del [df_in_SOPW, df_SSMonitor]
    df_SOPW[col_SOPW_BLD] = df_SOPW[col_SSMonitor_ShipmentBuildAhead]
    df_SOPW[col_SOPW_JIT] = df_SOPW[col_SSMonitor_ShipmentJIT]
    df_SOPW[col_SOPW_SS]  = df_SOPW[col_SSMonitor_ShipmentSS]
    
    df_SOPW.drop(columns=[col_SSMonitor_ShipmentBuildAhead, col_SSMonitor_ShipmentJIT, col_SSMonitor_ShipmentSS], inplace=True)
    
    print_df(df_SOPW, 'df_SOPW', False)
    
    ################################################################################################################
    # STEP 2 : New Model Merge
    ################################################################################################################
    step('=====> STEP 2-1 :  New Model Merge')
    # 칼럼명 변경
    df_in_NewModel.rename(columns={col_NewModelItem: col_Item}, inplace=True)
    
    #사전 작업 : Actual, Plan : Actual 우선
    df_in_NewModel['CHK_VALUE'] = np.where((df_in_NewModel[col_Category] == 'Actual'), 1, 2)
    
    cList_sort = [col_VersionName, col_Location, col_AP2, col_Item, 'CHK_VALUE']    
    # 정렬 후 rank 생성 :
    df_in_NewModel.sort_values(by=cList_sort, ascending=[True, True, True, True, True], axis=0, inplace=True)
    df_in_NewModel['RN'] = 1
    cList_group1 = [col_VersionName, col_Location, col_AP2, col_Item]
    df_in_NewModel['RN'] = df_in_NewModel.groupby(cList_group1)['RN'].cumsum()
    #print_df(df_in_NewModel, 'df_in_NewModel TEST1', False)
    df_in_NewModel = df_in_NewModel[df_in_NewModel['RN'] == 1]
    #df_in_NewModel['CNT'] = 'A' # TEST 확인용
    print_df(df_in_NewModel, 'df_in_NewModel TEST2', False)
    
    cList_group2 = [col_VersionName, col_Location, col_Item]
    # max -> min 으로 수정
    df_NewModel = df_in_NewModel.groupby(cList_group2, as_index=False).agg({col_NewModel_SETMP: "min",
                                                                           col_NewModel_SalesRTS: "min",
                                                                           col_NewModel_SETSR: "min"
                                                                           #,'CNT': "count" # TEST 확인용
                                                                            }
                                                                           , skipna=True).copy()
    del df_in_NewModel    
    print_df(df_NewModel, 'df_NewModel', False)
    
    df_SOPW = df_SOPW.merge(df_NewModel, on=cList_group2, how='left')
    del df_NewModel
    df_SOPW[col_SOPW_NewModelMP]  = np.where(df_SOPW[col_NewModel_SETMP].notna(), 
                                             df_SOPW[col_NewModel_SETMP].dt.date.astype('str'), np.nan)
    df_SOPW[col_SOPW_NewModelRTS] = np.where(df_SOPW[col_NewModel_SalesRTS].notna(), 
                                             df_SOPW[col_NewModel_SalesRTS].dt.date.astype('str'), np.nan)
    df_SOPW[col_SOPW_NewModelSR]  = np.where(df_SOPW[col_NewModel_SETSR].notna(), 
                                             df_SOPW[col_NewModel_SETSR].dt.date.astype('str'), np.nan)
    
    #df_SOPW.drop(columns=[col_NewModel_SETMP, col_NewModel_SalesRTS, col_NewModel_SETSR], inplace=True)
    print_df(df_SOPW, 'df_SOPW', False)
    
    ################################################################################################################
    # STEP 5 : output table create
    ################################################################################################################
    step('=====> STEP 5-1 : Final output table create')
        
    # out Data 생성 :
    df_out_SOPW = df_SOPW[cList_SOPW]
    del df_SOPW
    
    # 버전 처리
    # df_out_SOPW[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_SOPW.shape
    note(f'=====> Final df_out_SOPW rows : {row_count}, column : {col_count}')
    print_df(df_out_SOPW, 'df_out_SOPW', False)
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_SOPW, 'df_out_SOPW')
    
    step('=====> STEP 5-2 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')
    
except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_SOPW = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()