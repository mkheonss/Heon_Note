"""
* 프로그램명 
    - PY_MG_ResourceGroup

* 내용
    - Resoruce Group Member 생성용 메저 Insert

* 변경이력
    - 2024.08.29 / 양희영 / Create
    - 2024.10.08 : 이름변경 PY_MG_ResourceGroupCreation -> PY_MG_ResourceGroup
    - 2025.10.16 / 양희영 / Update 2


* Flow Summary

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
	   - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
	                         ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) 
	                         on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_BOMMaster : Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, 
                        ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column;
    - df_in_TactTime : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, 
                       ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]} ) 
                       on column where {  Measure.[Tact Time_Valid Asn] == true };
    - df_in_BODItem : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                      ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT]}) on column;
    - df_in_GlobalQuota : Select ([Version].[Version Name] * [Item Material].[Item Material] * [Group].[Group ID]) on row, 
                         ({Measure.[Global Quota Mtrl_Status] }) on column.filter(Measure.[Global Quota Mtrl_Status] == "CONFIRM");
	   - df_in_GlobalQuotaW : Select ([Version].[Version Name] * &PlanningHorizon * [Item Material].[Item Material] * [Group].[Group ID]) on row, 
	                          ({Measure.[Global Quota Mtrl W_Portion] }) on column.filter (~Isnull(Measure.[Global Quota Mtrl W_Portion]));
    - df_in_BODItemMtrl : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                          ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lot Size]}) 
                          on column.filter((isnull(Measure.[BOD Item Mtrl_EFF Enddate]) || Measure.[BOD Item Mtrl_EFF Enddate] > Measure.[W Plan Start Date]) && 
                                           (isnull(Measure.[BOD Item Mtrl_EFF Startdate]) || Measure.[BOD Item Mtrl_EFF Startdate] < Measure.[W Plan End Date]));

* Output Tables
    - df_out_ResGroup : MP Batch_Resource Group Bulk Member Creation_ResGroup
                        Select ([Version].[Version Name] * [MP Batch_Sequence].[MP Batch_Sequence_ID] ) on row, 
                        ({Measure.[MP Batch_Resource Group Bulk Member Creation_ResGroup], Measure.[MP Batch_Resource Group Bulk Member Creation_ResGroupType]}) on column;


* 테스트 스크립트
    EXEC plugin instance [PY_MG_ResourceGroup] for measures {[MP Batch_Resource Group Bulk Member Creation_ResGroup]} using scope (&MPV * &MFLocation) using arguments {
      (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (ParamOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
      
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
str_instance = 'PY_MG_ResourceGroup'
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
    
    # 컬럼 변수 선언
    versionVersionName       = 'Version.[Version Name]'
    groupGroupID             = 'Group.[Group ID]'
    itemItem                 = 'Item.[Item]'
    itemMaterialItemMaterial = 'Item Material.[Item Material]'
    locationLocation         = 'Location.[Location]'
    subLocationSubLocation   = 'Sub Location.[Sub Location]'
    transModeTransMode       = "Trans Mode.[Trans Mode]"
    bOMInfoBOMID             = 'BOM Info.[BOM ID]'
    lineLine                 = 'Line.[Line]'
    timeWeek                 = 'Time.[Week]'
    
    bOMMaster_BOMID = 'BOM Master_BOM ID'
    mPBatch_SequenceMPBatch_Sequence_ID = 'MP Batch_Sequence.[MP Batch_Sequence_ID]'
    mPBatch_ResourceGroupBulkMemberCreation_ResGroup = 'MP Batch_Resource Group Bulk Member Creation_ResGroup'
    mPBatch_ResourceGroupBulkMemberCreation_ResGroupType = 'MP Batch_Resource Group Bulk Member Creation_ResGroupType'
    
    globalQuotaMtrl_Status   = 'Global Quota Mtrl_Status'
    globalQuotaMtrlW_Portion = 'Global Quota Mtrl W_Portion'
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE

        df_in_ItemSiteAsn  = read_csv_file("df_in_ItemSiteAsn")
        df_in_BOMMaster    = read_csv_file("df_in_BOMMaster")
        df_in_TactTime     = read_csv_file("df_in_TactTime")
        df_in_BODItem      = read_csv_file("df_in_BODItem")
        df_in_GlobalQuota  = read_csv_file("df_in_GlobalQuota")
        df_in_GlobalQuotaW = read_csv_file("df_in_GlobalQuotaW")
        df_in_BODItemMtrl  = read_csv_file("df_in_BODItemMtrl")
            
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정

    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',False)
    print_df(df_in_BOMMaster, 'df_in_BOMMaster',False)
    print_df(df_in_TactTime, 'df_in_TactTime',False)
    print_df(df_in_BODItem, 'df_in_BODItem',False)
    print_df(df_in_GlobalQuota, 'df_in_GlobalQuota',False)
    print_df(df_in_GlobalQuotaW, 'df_in_GlobalQuotaW',False)
    print_df(df_in_BODItemMtrl, 'df_in_BODItemMtrl',False)
    
    step('=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : Global Quota Set 생성
    ################################################################################################################
    step('=====> STEP 1 : Global Quota Set create')
    
    # ITEM BOD SET 구성
    df_bodItemMtrlSet = df_in_BODItemMtrl[[versionVersionName, locationLocation, subLocationSubLocation, itemMaterialItemMaterial]].copy()
    del df_in_BODItemMtrl
    df_bodItemMtrlSet.drop_duplicates(inplace=True)
    
    print_df(df_bodItemMtrlSet, 'df_bodItemMtrlSet',False)
    # Merge : df_in_GlobalQuota & df_in_GlobalQuotaW
    df_GlobalQuotaSet = df_in_GlobalQuota.merge(df_in_GlobalQuotaW, on=[versionVersionName, itemMaterialItemMaterial, groupGroupID], how='inner')
    del df_in_GlobalQuota
    del df_in_GlobalQuotaW
    
    # Merge : df_GlobalQuotaSet & df_bodItemMtrlSet
    df_GlobalQuotaSet = df_GlobalQuotaSet.merge(df_bodItemMtrlSet, on=[versionVersionName, itemMaterialItemMaterial], how='inner')
    del df_bodItemMtrlSet
    
    df_GlobalQuotaSet[mPBatch_ResourceGroupBulkMemberCreation_ResGroup] = df_GlobalQuotaSet[groupGroupID] + '_' + df_GlobalQuotaSet[locationLocation]
    df_GlobalQuotaSet[mPBatch_ResourceGroupBulkMemberCreation_ResGroupType] = 'GroupProportionalSourcing'
    print_df(df_GlobalQuotaSet, 'df_GlobalQuotaSet 1',False)
    
    # 칼럼 정리
    df_GlobalQuotaSet = df_GlobalQuotaSet[[versionVersionName, mPBatch_ResourceGroupBulkMemberCreation_ResGroup, mPBatch_ResourceGroupBulkMemberCreation_ResGroupType]]
    df_GlobalQuotaSet.drop_duplicates(inplace=True)
    
    print_df(df_GlobalQuotaSet, 'df_GlobalQuotaSet 2',False)
    step('=====> STEP 1-1 : Global Quota Set create End')
    
    ################################################################################################################
    # STEP 2 : Resource data 생성
    ################################################################################################################
    step('=====> STEP 2 : Resource Group data create')
    # STEP1-1 -Item, Location 정보 df 구성, df_in_ItemSiteAsn distinct 필요없음,
    df_itemLocation = df_in_ItemSiteAsn[[versionVersionName, locationLocation, itemItem]].copy(deep=True)
    # df_itemLocation.drop_duplicates(inplace=True)
    print_df(df_itemLocation, 'df_itemLocation column adjust & drop_duplicates',False)
    
    # STEP1-2-distinct item, distinct location
    Item_series = df_in_ItemSiteAsn[itemItem].unique()
    Location_series = df_in_ItemSiteAsn[locationLocation].unique()
    del df_in_ItemSiteAsn
    
    # STEP1-3 df_in_BOMMaster, df_itemLocation 조인
    df_in_BOMMaster.rename(columns={bOMMaster_BOMID:itemItem}, inplace=True)
    df_ResGroup_1 = df_in_BOMMaster.merge(df_itemLocation, on=[versionVersionName, locationLocation, itemItem], how='inner')
    del df_in_BOMMaster
    del df_itemLocation
    
    # STEP1-4 df_ResGroup_1, df_in_TactTime 조인
    df_ResGroup_1 = df_ResGroup_1.merge(df_in_TactTime, on=[versionVersionName, locationLocation, itemItem], how='inner')
    del df_in_TactTime
    
    df_ResGroup_1[mPBatch_ResourceGroupBulkMemberCreation_ResGroup] = 'RT_'+df_ResGroup_1[bOMInfoBOMID]+'@'+df_ResGroup_1[locationLocation]+'_'+df_ResGroup_1[lineLine]
    df_ResGroup_1[mPBatch_ResourceGroupBulkMemberCreation_ResGroupType] = 'Simultaneous'
    
    
    # 칼럼 정리
    df_ResGroup_1 = df_ResGroup_1[[versionVersionName, mPBatch_ResourceGroupBulkMemberCreation_ResGroup, mPBatch_ResourceGroupBulkMemberCreation_ResGroupType]]    
    print_df(df_ResGroup_1, 'df_ResGroup_1',False)
    
    # STEP1-5 df_in_BODItem Item Filtering, Location Filtering
    df_in_BODItem = df_in_BODItem[df_in_BODItem[itemItem].isin(Item_series)]
    df_ResGroup_2 = df_in_BODItem[(df_in_BODItem[locationLocation].isin(Location_series)) | (df_in_BODItem[subLocationSubLocation].isin(Location_series))]
    del df_in_BODItem
    
    df_ResGroup_2[mPBatch_ResourceGroupBulkMemberCreation_ResGroup] = (df_ResGroup_2[locationLocation]+'_'+
                                                                       df_ResGroup_2[subLocationSubLocation]+'_'+
                                                                       df_ResGroup_2[transModeTransMode]+'_'+
                                                                       df_ResGroup_2[itemItem])
    df_ResGroup_2[mPBatch_ResourceGroupBulkMemberCreation_ResGroupType] = 'Simultaneous'
    
    # 칼럼 정리
    df_ResGroup_2 = df_ResGroup_2[[versionVersionName, mPBatch_ResourceGroupBulkMemberCreation_ResGroup, mPBatch_ResourceGroupBulkMemberCreation_ResGroupType]]
    
    print_df(df_ResGroup_2, 'df_ResGroup_2',False)
    step('=====> STEP 2-1 : Resource Group data create End')
    
    ################################################################################################################
    # STEP 3 : output table create
    ################################################################################################################
    step('=====> STEP 3 : Final output table create')
    
    # out Data 생성 
    df_out_ResGroup = pd.concat([df_GlobalQuotaSet,
                                 df_ResGroup_1, 
                                 df_ResGroup_2])
    df_out_ResGroup.drop_duplicates(inplace=True)
    del df_GlobalQuotaSet
    del df_ResGroup_1
    del df_ResGroup_2
    
    #df_out_ResGroup[mPBatch_ResourceGroupBulkMemberCreation_ResGroupType] = 'Simultaneous'
    df_out_ResGroup[mPBatch_SequenceMPBatch_Sequence_ID] = df_out_ResGroup.reset_index().index + 1
    
    # 버전 처리
    #df_out_ResGroup[versionVersionName] = paramOutVersion
    
    # out 칼럼 설정
    df_out_ResGroup = df_out_ResGroup[[versionVersionName,
                                       mPBatch_SequenceMPBatch_Sequence_ID,
                                       mPBatch_ResourceGroupBulkMemberCreation_ResGroup,
                                       mPBatch_ResourceGroupBulkMemberCreation_ResGroupType]]
    
    print_df(df_out_ResGroup, 'df_out_ResGroup',False)
    step('=====> STEP 3-1 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_ResGroup, 'df_out_ResGroup')
        
    row_count, col_count = df_out_ResGroup.shape
    note(f'=====> Final df_out_ResGroup rows : {row_count}, column : {col_count}')
    
    step('=====> STEP 3-2 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_ResGroup = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()