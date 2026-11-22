"""
* 프로그램명 
    - PY_MG_VendorMtrlQuota

* 내용
    - 자재별 Vendor Quota 정보 Inbound

* 변경이력
- 2024.10.08 / 양희영 / Create
- 2025.10.16 / 양희영 / Update

* Input
  - 자재/업체/Plant 간 공급비율 설정을 위한 Resource Grouping
  - From ResourceGroup to To Resource Group 간 Quota(공급배분율) 설정
  
* Flow Summary
    STEP1. 
    STEP2. 
    STEP3. 
    
* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_GlobalQuota : Select ([Version].[Version Name] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID]) on row, 
                          ({Measure.[Global Quota Mtrl_Status] }) on column.filter(Measure.[Global Quota Mtrl_Status] == "CONFIRM");
	   - df_in_PlantQuotaW : Select ([Version].[Version Name] * &PlanningHorizon * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, 
	                         ({Measure.[Plant Quota Mtrl W_Portion]}) on column.filter(~Isnull(Measure.[Plant Quota Mtrl W_Portion]));
	   - df_in_GlobalQuotaW : Select ([Version].[Version Name] * &PlanningHorizon * [Item Material].[Item Material] * [Group].[Group ID]) on row, 
	                          ({Measure.[Global Quota Mtrl W_Portion] }) on column.filter (~Isnull(Measure.[Global Quota Mtrl W_Portion]));
    - df_in_BODItemMtrl : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                          ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lot Size]}) 
                          on column.filter((isnull(Measure.[BOD Item Mtrl_EFF Enddate]) || Measure.[BOD Item Mtrl_EFF Enddate] > Measure.[W Plan Start Date]) && 
                                           (isnull(Measure.[BOD Item Mtrl_EFF Startdate]) || Measure.[BOD Item Mtrl_EFF Startdate] < Measure.[W Plan End Date]));
	   
* Output Tables
    - df_out_SourcingAsn : MG :  001.51W Group Sourcing Material Node
                           Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Resource Group].[Resource Group] ) on row, 
                                  ({Measure.[W Group Sourcing MN Association]}) on column;
    - df_out_SourcingRate : Graph: 001.051W Group Sourcing Proportion Inputs
                            Select (FROM.[Time].[Week] * FROM.[Resource Group].[Resource Group] * TO.[Resource Group].[Resource Group]) on row, 
                                   ({Edge.[001.051W Group Sourcing Proportion Inputs].[W Group Sourcing Proportion]}) 
                                    on column where {RelationshipType.[001.051W Group Sourcing Proportion Inputs], Version.[Version Name]};


* 테스트 스크립트
    EXEC plugin instance [PY_MG_VendorMtrlQuota] for measures {[W Group Sourcing MN Association]} using scope (&MPV) 
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
str_instance = 'PY_MG_VendorMtrlQuota'
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
    versionVersionName         = 'Version.[Version Name]'
    groupGroupID               = 'Group.[Group ID]'
    itemItem                   = 'Item.[Item]'
    itemMaterialItemMaterial   = 'Item Material.[Item Material]'
    locationLocation           = 'Location.[Location]'
    subLocationSubLocation     = 'Sub Location.[Sub Location]'
    resourceGroupResourceGroup = 'Resource Group.[Resource Group]'
    timeWeek                   = 'Time.[Week]'    

    from_TimeWeek                   = 'from.[Time].[Week]'
    from_ResourceGroupResourceGroup = 'from.[Resource Group].[Resource Group]'
    to_ResourceGroupResourceGroup   = 'to.[Resource Group].[Resource Group]'
    wGroupSourcingProportion        = '001.051W Group Sourcing Proportion Inputs.[W Group Sourcing Proportion]'
    wGroupSourcingMNAssociation     = 'W Group Sourcing MN Association'
         
    globalQuotaMtrlW_Portion = 'Global Quota Mtrl W_Portion'
    plantQuotaMtrlW_Portion  = 'Plant Quota Mtrl W_Portion'    
    
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

        df_in_GlobalQuota  = read_csv_file("df_in_GlobalQuota")
        df_in_PlantQuotaW  = read_csv_file("df_in_PlantQuotaW")
        df_in_GlobalQuotaW = read_csv_file("df_in_GlobalQuotaW")
        df_in_BODItemMtrl  = read_csv_file("df_in_BODItemMtrl")
        
    #if df_in_GlobalQuota.empty:
    #    raise Exception("=====> raise Exception: df_in_GlobalQuota is empty")
    #    
    #if df_in_BODItemMtrl.empty:
    #    raise Exception("=====> raise Exception: df_in_BODItemMtrl is empty")

    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_GlobalQuota, 'df_in_GlobalQuota',False)
    print_df(df_in_PlantQuotaW, 'df_in_PlantQuotaW',False)
    print_df(df_in_GlobalQuotaW, 'df_in_GlobalQuotaW',False)
    print_df(df_in_BODItemMtrl, 'df_in_BODItemMtrl',False)
    
    step('=====> Input table load End')
    
    # distint df_in_GlobalQuota : Sub Location.[Sub Location] 제외
    df_in_GlobalQuota.drop(columns=[subLocationSubLocation], inplace=True)
    df_in_GlobalQuota.drop_duplicates(inplace=True)
    print_df(df_in_GlobalQuota, 'df_in_GlobalQuota distinct', False)
    
    ################################################################################################################
    # STEP 1 : ITEM BOD SET 구성
    ################################################################################################################
    step('=====> STEP 1 : Global Quota Set create')
    
    # ITEM BOD SET 구성
    df_bodItemMtrlSet = df_in_BODItemMtrl[[versionVersionName, locationLocation, subLocationSubLocation, itemMaterialItemMaterial]].copy()
    del df_in_BODItemMtrl
    df_bodItemMtrlSet.drop_duplicates(inplace=True)
    
    print_df(df_bodItemMtrlSet, 'df_bodItemMtrlSet',False)    
    step('=====> STEP 1 : Global Quota Set create End')
    
    ################################################################################################################
    # STEP 2-1 : Plant Quota Set 구성
    ################################################################################################################
    step('=====> STEP 2-1 : Plant Quota Set create')
    
    # Merge : df_in_GlobalQuota & df_in_PlantQuotaW
    df_PlantQuotaSet = df_in_GlobalQuota.merge(df_in_PlantQuotaW, on=[versionVersionName, itemMaterialItemMaterial, groupGroupID], how='inner')
    del df_in_PlantQuotaW
    
    # Merge : df_PlantQuotaSet & df_bodItemMtrlSet
    df_PlantQuotaSet = df_PlantQuotaSet.merge(df_bodItemMtrlSet, on=[versionVersionName, itemMaterialItemMaterial, locationLocation, subLocationSubLocation], how='inner')
    
    df_PlantQuotaSet[from_ResourceGroupResourceGroup] = df_PlantQuotaSet[groupGroupID] + '_' + df_PlantQuotaSet[locationLocation]
    df_PlantQuotaSet[to_ResourceGroupResourceGroup]   = df_PlantQuotaSet[groupGroupID] + '_' + df_PlantQuotaSet[subLocationSubLocation]    
    
    #칼럼 정리
    df_PlantQuotaSet = df_PlantQuotaSet[[versionVersionName, timeWeek, itemMaterialItemMaterial, locationLocation, from_ResourceGroupResourceGroup,
                                         subLocationSubLocation, to_ResourceGroupResourceGroup, plantQuotaMtrlW_Portion]]
    print_df(df_PlantQuotaSet, 'df_PlantQuotaSet',False)
    step('=====> STEP 2-1 : Plant Quota Set create End')
    
    ################################################################################################################
    # STEP 2-2 : Global Quota Set 구성
    ################################################################################################################
    step('=====> STEP 2-2 : RGlobal Quota Set create')
    
    # Merge : df_in_GlobalQuota & df_in_GlobalQuotaW
    df_GlobalQuotaSet = df_in_GlobalQuota.merge(df_in_GlobalQuotaW, on=[versionVersionName, itemMaterialItemMaterial, groupGroupID], how='inner')
    del df_in_GlobalQuota
    del df_in_GlobalQuotaW
    #print_df(df_GlobalQuotaSet, 'df_GlobalQuotaSet 0-1', False)
    
    # Merge : df_GlobalQuotaSet & df_in_BODItemMtrl
    df_GlobalQuotaSet = df_GlobalQuotaSet.merge(df_bodItemMtrlSet, on=[versionVersionName, itemMaterialItemMaterial], how='inner')
    del df_bodItemMtrlSet
    #print_df(df_GlobalQuotaSet, 'df_GlobalQuotaSet 0-2', False)
    
    df_GlobalQuotaSet[from_ResourceGroupResourceGroup] = df_GlobalQuotaSet[groupGroupID] + '_' + df_GlobalQuotaSet[locationLocation]
    df_GlobalQuotaSet[to_ResourceGroupResourceGroup]   = df_GlobalQuotaSet[groupGroupID] + '_' + df_GlobalQuotaSet[subLocationSubLocation]    
    
    # not exists df_PlantQuotaSet -----------------------------------------------
    df_PQSet = df_PlantQuotaSet[[versionVersionName, itemMaterialItemMaterial, locationLocation, subLocationSubLocation]].copy()
    #df_PQSet['check_value'] = 1
    df_PQSet.drop_duplicates(inplace=True)
    
    df_GlobalQuotaSet = df_GlobalQuotaSet[
        ~df_GlobalQuotaSet.set_index([versionVersionName, itemMaterialItemMaterial,
                                      locationLocation, subLocationSubLocation]).index.isin(
         df_PQSet.set_index([versionVersionName, itemMaterialItemMaterial,
                             locationLocation, subLocationSubLocation]).index)]
    
    #df_GlobalQuotaSet = df_GlobalQuotaSet.merge(df_PQSet, on=[versionVersionName, itemMaterialItemMaterial, locationLocation, subLocationSubLocation], how='left')
    #df_GlobalQuotaSet = df_GlobalQuotaSet.loc[df_GlobalQuotaSet['check_value'].isna()]
    print_df(df_GlobalQuotaSet, 'df_GlobalQuotaSet 1',False)
    #----------------------------------------------------------------------------    
    
    # 칼럼 정리
    df_GlobalQuotaSet = df_GlobalQuotaSet[[versionVersionName, timeWeek, itemMaterialItemMaterial, locationLocation, from_ResourceGroupResourceGroup,
                                           subLocationSubLocation, to_ResourceGroupResourceGroup, globalQuotaMtrlW_Portion]]
    #df_GlobalQuotaSet.drop_duplicates(inplace=True)
    print_df(df_GlobalQuotaSet, 'df_GlobalQuotaSet 2',False)
    step('=====> STEP 2-2 : RGlobal Quota Set create End')
    ################################################################################################################
    # STEP 3-1 : MG :  001.51W Group Sourcing Material Node 구성, df_QuotaAsn
    ################################################################################################################
    step('=====> STEP 3-1 : Group Sourcing Material Node create')
    
    # df_QuotaAsn_1 : df_PlantQuotaSet , Location.[Location]
    df_QuotaAsn_1 =  df_PlantQuotaSet[[versionVersionName, itemMaterialItemMaterial, locationLocation, from_ResourceGroupResourceGroup]].copy()
    df_QuotaAsn_1.drop_duplicates(inplace=True)
    df_QuotaAsn_1.rename(columns={from_ResourceGroupResourceGroup:resourceGroupResourceGroup}, inplace=True)
    df_QuotaAsn_1[wGroupSourcingMNAssociation] = True    
    print_df(df_QuotaAsn_1, 'df_QuotaAsn_1',False)
    
    # df_QuotaAsn_2 : df_PlantQuotaSet , Sub Location.[Sub Location]
    df_QuotaAsn_2 =  df_PlantQuotaSet[[versionVersionName, itemMaterialItemMaterial, subLocationSubLocation, to_ResourceGroupResourceGroup]].copy()
    df_QuotaAsn_2.drop_duplicates(inplace=True)
    df_QuotaAsn_2.rename(columns={subLocationSubLocation:locationLocation,
                                  to_ResourceGroupResourceGroup:resourceGroupResourceGroup}, inplace=True)
    df_QuotaAsn_2[wGroupSourcingMNAssociation] = True    
    print_df(df_QuotaAsn_2, 'df_QuotaAsn_2',False)

    # df_QuotaAsn_3 : df_GlobalQuotaSet , Location.[Location]
    df_QuotaAsn_3 =  df_GlobalQuotaSet[[versionVersionName, itemMaterialItemMaterial, locationLocation, from_ResourceGroupResourceGroup]].copy()
    df_QuotaAsn_3.drop_duplicates(inplace=True)
    df_QuotaAsn_3.rename(columns={from_ResourceGroupResourceGroup:resourceGroupResourceGroup}, inplace=True)
    df_QuotaAsn_3[wGroupSourcingMNAssociation] = True    
    print_df(df_QuotaAsn_3, 'df_QuotaAsn_3',False)
    
    # df_QuotaAsn_4 : df_GlobalQuotaSet , Sub Location.[Sub Location]
    df_QuotaAsn_4 =  df_GlobalQuotaSet[[versionVersionName, itemMaterialItemMaterial, subLocationSubLocation, to_ResourceGroupResourceGroup]].copy()
    df_QuotaAsn_4.drop_duplicates(inplace=True)
    df_QuotaAsn_4.rename(columns={subLocationSubLocation:locationLocation,
                                  to_ResourceGroupResourceGroup:resourceGroupResourceGroup}, inplace=True)
    df_QuotaAsn_4[wGroupSourcingMNAssociation] = True    
    print_df(df_QuotaAsn_4, 'df_QuotaAsn_4',False)
    
    df_QuotaAsn = pd.concat([df_QuotaAsn_1, df_QuotaAsn_2, df_QuotaAsn_3, df_QuotaAsn_4])
    del df_QuotaAsn_1
    del df_QuotaAsn_2
    del df_QuotaAsn_3
    del df_QuotaAsn_4
    
    df_QuotaAsn.rename(columns={itemMaterialItemMaterial: itemItem}, inplace=True)
    df_QuotaAsn.drop_duplicates(inplace=True)
    
    print_df(df_QuotaAsn, 'df_QuotaAsn',False)
    
    step('=====> STEP 3-1 : Group Sourcing Material Node create End')
    ################################################################################################################
    # STEP 3-2 : Graph: 001.051W Group Sourcing Proportion Inputs 구성
    ################################################################################################################
    step('=====> STEP 3-2 : Graph W Group Sourcing Proportion Inputs create')
    df_graph_WGrpSrcPrptn_1 = df_PlantQuotaSet[[versionVersionName, timeWeek, from_ResourceGroupResourceGroup, to_ResourceGroupResourceGroup
                                               ,plantQuotaMtrlW_Portion]].copy()
    
    df_graph_WGrpSrcPrptn_1.rename(columns={timeWeek:from_TimeWeek, plantQuotaMtrlW_Portion:wGroupSourcingProportion}, inplace=True)
    df_graph_WGrpSrcPrptn_1.drop_duplicates(inplace=True)
    print_df(df_graph_WGrpSrcPrptn_1, 'df_graph_WGrpSrcPrptn_1',False)
    
    df_graph_WGrpSrcPrptn_2 = df_GlobalQuotaSet[[versionVersionName, timeWeek, from_ResourceGroupResourceGroup, to_ResourceGroupResourceGroup
                                               ,globalQuotaMtrlW_Portion]].copy()
    
    df_graph_WGrpSrcPrptn_2.rename(columns={timeWeek:from_TimeWeek, globalQuotaMtrlW_Portion:wGroupSourcingProportion}, inplace=True)
    df_graph_WGrpSrcPrptn_2.drop_duplicates(inplace=True)
    print_df(df_graph_WGrpSrcPrptn_2, 'df_graph_WGrpSrcPrptn_2',False)
    
    df_graph_WGrpSrcPrptn = pd.concat([df_graph_WGrpSrcPrptn_1, df_graph_WGrpSrcPrptn_2])
    del df_graph_WGrpSrcPrptn_1
    del df_graph_WGrpSrcPrptn_2    
    df_graph_WGrpSrcPrptn.drop_duplicates(inplace=True)
    print_df(df_graph_WGrpSrcPrptn, 'df_graph_WGrpSrcPrptn',False)
    step('=====> STEP 3-2 : Graph W Group Sourcing Proportion Inputs create End')
    ################################################################################################################
    # STEP 4 : output table create
    ################################################################################################################
    step('=====> STEP 4 : Final output table create')
    
    # out Data 생성 
    df_out_SourcingAsn = df_QuotaAsn.copy()    
    del df_QuotaAsn
    
    df_out_SourcingRate = df_graph_WGrpSrcPrptn.copy()
    del df_graph_WGrpSrcPrptn
    
    # 버전 처리
    #df_out_SourcingAsn[versionVersionName] = paramOutVersion
    #df_out_SourcingRate[versionVersionName] = paramOutVersion
    
    # out 칼럼 설정
    
    row_count, col_count = df_out_SourcingAsn.shape
    note(f'=====> Final df_out_SourcingAsn rows : {row_count}, column : {col_count}')
    
    row_count, col_count = df_out_SourcingRate.shape
    note(f'=====> Final df_out_SourcingRate rows : {row_count}, column : {col_count}')
    
    print_df(df_out_SourcingAsn, 'df_out_SourcingAsn',False)
    print_df(df_out_SourcingRate, 'df_out_SourcingRate',False)
    step('=====> STEP 4-1 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_SourcingAsn, 'df_out_SourcingAsn')
        save_csv_file(df_out_SourcingRate, 'df_out_SourcingRate')
        
    
    step('=====> STEP 4-2 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_SourcingAsn = pd.DataFrame([], columns=[])
    df_out_SourcingRate = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()