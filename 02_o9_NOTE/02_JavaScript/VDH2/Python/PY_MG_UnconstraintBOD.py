"""
* 프로그램명 
    - PY_MG_UnconstraintBOD

* 내용
    - UnConstraint 용 가상 BOD 생성을 위한 Member Buffer입력

* 변경이력
    - 2024.10.15 / 양희영 / Create
    - 2025.10.16 / 양희영 / Update

* Input
  - 
  
* Flow Summary
    STEP1. UnConstraint 용 가상 BOD 생성을 위한 Member Buffer입력
    
* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_UnConItem : Select ([Version].[Version Name] * [Item Material].[Item Material] ) on row, 
                        ({Measure.[Mtrl Const Type Batch_Type]})  on column.filter(Measure.[Mtrl Const Type Batch_Type]== "UnConstraint");
	   - df_in_VendorMtrl : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Vendor].[Vendor] * [Global Top].[GT Code] * [Partner Vendor].[Partner Vendor] ) on row, 
	                        ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Quota]}) on column;
    - df_in_PlanStartEndDate : Select ([Version].[Version Name]) on row, ({Measure.[MP Plan End Date], Measure.[MP Plan Start Date]}) on column;
    
* Output Tables
    - df_out_UnConBOD : UnConstraint BOD Lane 생성 Measure Insert 
                      MG : MP Batch_UnConst BOD Bulk Member Creation
                      Select ([Version].[Version Name] * [MP Batch_Sequence].[MP Batch_Sequence_ID] ) on row, 
                      ({Measure.[MP Batch_UnConst BOD Bulk Member Creation_BOD Name], Measure.[MP Batch_UnConst BOD Bulk Member Creation_From Site ID], Measure.[MP Batch_UnConst BOD Bulk Member Creation_To Site ID]}) on column;
    - df_out_UnConItemBOD : UnConstraint  Item BOD 생성 Measure Insert 
                            MG : BOD Item Mtrl UnConst
                            Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                            ({Measure.[BOD Item Mtrl UnConst_EFF Enddate], Measure.[BOD Item Mtrl UnConst_EFF Startdate]}) on column;
* 테스트 스크립트
    EXEC plugin instance [PY_MG_UnconstraintBOD] for measures {[MP Batch_UnConst BOD Bulk Member Creation_From Site ID]} using scope (&MPV) 
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};
      
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
str_instance = 'PY_MG_UnconstraintBOD'
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
    
    # 컬럼 변수 선언
    versionVersionName       = 'Version.[Version Name]'
    itemMaterialItemMaterial = 'Item Material.[Item Material]'
    locationLocation         = 'Location.[Location]'
    vendorVendor             = 'Vendor.[Vendor]'
    globalTopGTCode          = 'Global Top.[GT Code]'
    subLocationSubLocation   = 'Sub Location.[Sub Location]'
    transModeTransMode       = 'Trans Mode.[Trans Mode]'
    mPBatch_SequenceMPBatch_Sequence_ID = 'MP Batch_Sequence.[MP Batch_Sequence_ID]'
    
    mtrlConstTypeBatch_Type         = 'Mtrl Const Type Batch_Type'
    mPPlanStartDate                 = 'MP Plan Start Date'
    bODItemMtrlUnConst_EFFStartdate = 'BOD Item Mtrl UnConst_EFF Startdate'
    bODItemMtrlUnConst_EFFEnddate   = 'BOD Item Mtrl UnConst_EFF Enddate'
    
    mPBatch_UnConstBODBulkMemberCreation_BODName    = 'MP Batch_UnConst BOD Bulk Member Creation_BOD Name'
    mPBatch_UnConstBODBulkMemberCreation_FromSiteID = 'MP Batch_UnConst BOD Bulk Member Creation_From Site ID'
    mPBatch_UnConstBODBulkMemberCreation_ToSiteID   = 'MP Batch_UnConst BOD Bulk Member Creation_To Site ID'
        
    step('=====> STEP 0-2 : DataFrame Column : 변수 처리 End')
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-3 : Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE

        df_in_UnConItem         = read_csv_file("df_in_UnConItem")
        df_in_VendorMtrl        = read_csv_file("df_in_VendorMtrl")
        df_in_PlanStartEndDate  = read_csv_file("df_in_PlanStartEndDate")
        
    #if df_in_UnConItem.empty:
    #    raise Exception("=====> raise Exception: df_in_UnConItem is empty")
    
    #if df_in_VendorMtrl.empty:
    #    raise Exception("=====> raise Exception: df_in_VendorMtrl is empty")
    
    #if df_in_PlanStartEndDate.empty:
    #    raise Exception("=====> raise Exception: df_in_PlanStartEndDate is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    df_in_PlanStartEndDate[mPPlanStartDate] = pd.to_datetime(df_in_PlanStartEndDate[mPPlanStartDate], format='%m/%d/%Y %I:%M:%S %p')
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_UnConItem, 'df_in_UnConItem',False)
    print_df(df_in_VendorMtrl, 'df_in_VendorMtrl',False)
    print_df(df_in_PlanStartEndDate, 'df_in_PlanStartEndDate',False)
    
    step('=====> STEP 0-4 : Input table load End')
        
    ################################################################################################################
    # STEP 1 : df_UnConBOD Set 구성 및 df_out_UnConItemBOD (BOD Item Mtrl UnConst) 에 입력 
    ################################################################################################################
    step('=====> STEP 1-1 : df_UnConBOD Set create')
    
    # Merge : df_in_UnConItem & df_in_VendorMtrl
    df_UnConBOD = df_in_UnConItem.merge(df_in_VendorMtrl, on=[versionVersionName, itemMaterialItemMaterial], how='inner')
    del df_in_UnConItem
    del df_in_VendorMtrl
    
    # Merge : df_UnConBOD & df_in_PlanStartEndDate
    df_UnConBOD = df_UnConBOD.merge(df_in_PlanStartEndDate, on=[versionVersionName], how='inner')
    del df_in_PlanStartEndDate
    
    df_UnConBOD.rename(columns={locationLocation:subLocationSubLocation,
                                globalTopGTCode:locationLocation}, inplace=True)
    
    df_UnConBOD[transModeTransMode] = 'TRUCK'
    df_UnConBOD[bODItemMtrlUnConst_EFFStartdate] =  df_UnConBOD[mPPlanStartDate].dt.date
    df_UnConBOD[bODItemMtrlUnConst_EFFEnddate]   = ''
    
    # 칼럼 정리
    df_UnConBOD = df_UnConBOD[[versionVersionName, itemMaterialItemMaterial, locationLocation, subLocationSubLocation, 
                               transModeTransMode, bODItemMtrlUnConst_EFFStartdate, bODItemMtrlUnConst_EFFEnddate]]    
    df_UnConBOD.drop_duplicates(inplace=True)
    
    print_df(df_UnConBOD, 'df_UnConBOD',False)
    step('=====> STEP 1-2 : df_UnConBOD Set create End')
    
    ################################################################################################################
    # STEP 2 : df_UnConBOD Set 기준 MP Batch_UnConst BOD Bulk Member Creation 에 입력 
    ################################################################################################################
    step('=====> STEP 2-1 : MP Batch_UnConst BOD Bulk Member create')
    
    df_UnConstBODBulkMember = df_UnConBOD.copy()
    df_UnConstBODBulkMember[mPBatch_UnConstBODBulkMemberCreation_BODName] = (
                                                               df_UnConstBODBulkMember[locationLocation] + "_" +
                                                               df_UnConstBODBulkMember[subLocationSubLocation] + "_" +
                                                               df_UnConstBODBulkMember[transModeTransMode])
    
    df_UnConstBODBulkMember.rename(columns={locationLocation:mPBatch_UnConstBODBulkMemberCreation_FromSiteID,
                                            subLocationSubLocation:mPBatch_UnConstBODBulkMemberCreation_ToSiteID}, inplace=True)
    
    # 칼럼 정리
    df_UnConstBODBulkMember = df_UnConstBODBulkMember[[versionVersionName, 
                                                       mPBatch_UnConstBODBulkMemberCreation_BODName,
                                                       mPBatch_UnConstBODBulkMemberCreation_FromSiteID,
                                                       mPBatch_UnConstBODBulkMemberCreation_ToSiteID]]
    
    df_UnConstBODBulkMember.drop_duplicates(inplace=True)    
    df_UnConstBODBulkMember[mPBatch_SequenceMPBatch_Sequence_ID] = df_UnConstBODBulkMember.reset_index().index + 1
    
    print_df(df_UnConstBODBulkMember, 'df_UnConstBODBulkMember',False)
    step('=====> STEP 2-2 : MP Batch_UnConst BOD Bulk Member create End')
    
    ################################################################################################################
    # STEP 3 : output table create
    ################################################################################################################
    
    step('=====> STEP 3 : Final output table create')
    
    # out Data 생성 1
    df_out_UnConBOD = df_UnConstBODBulkMember[[versionVersionName,
                                               mPBatch_SequenceMPBatch_Sequence_ID,
                                               mPBatch_UnConstBODBulkMemberCreation_BODName,
                                               mPBatch_UnConstBODBulkMemberCreation_FromSiteID,
                                               mPBatch_UnConstBODBulkMemberCreation_ToSiteID]].copy()
    del df_UnConstBODBulkMember
    
    # out Data 생성 2
    df_out_UnConItemBOD = df_UnConBOD[[versionVersionName, locationLocation, itemMaterialItemMaterial, subLocationSubLocation, transModeTransMode,
                                       bODItemMtrlUnConst_EFFEnddate, bODItemMtrlUnConst_EFFStartdate]].copy()
    del df_UnConBOD
    
    # 버전 처리
    #df_out_UnConBOD[versionVersionName] = paramOutVersion
    #df_out_UnConItemBOD[versionVersionName] = paramOutVersion
    
    # df_out_UnConBOD ------
    row_count, col_count = df_out_UnConBOD.shape
    note(f'=====> Final df_out_UnConBOD rows : {row_count}, column : {col_count}')    
    print_df(df_out_UnConBOD, 'df_out_UnConBOD',False)
        
    # df_out_UnConItemBOD ------
    row_count, col_count = df_out_UnConItemBOD.shape
    note(f'=====> Final df_out_UnConItemBOD rows : {row_count}, column : {col_count}')    
    print_df(df_out_UnConItemBOD, 'df_out_UnConItemBOD',False)
    
    step('=====> STEP 3-1 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_UnConBOD, 'df_out_UnConBOD')
        save_csv_file(df_out_UnConItemBOD, 'df_out_UnConItemBOD')
    
    step('=====> STEP 3-2 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_UnConBOD = pd.DataFrame([], columns=[])
    df_out_UnConItemBOD = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()