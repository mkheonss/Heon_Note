"""
* 프로그램명 
    - PY_MG_CapacityConsumptionAssociation

* 내용
    - [Basic Input] MP Engine 수행을 위한 Tact Tact Time Input 
    - MP Plan Batch Procedure에서 Call 하는 Program  
    - 기존 메저는 Batch Procedure에서 Delete 

* 변경이력
    - 2024.06.26 / 양희영 / Create
    - 2025.06.27 / 양희영 / Update

* Input

* Flow Summary
    STEP1. df_in_TactTime 중 Plan 대상 Item, Location 정보 대상 SET 구성
    STEP2. STEP1에서 구성한 SET을 대상으로 Measure Insert    
* Execution 
 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용한함.
* Input Tables
    - df_in_TactTime : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, 
                       ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  
                       where {Measure.[Tact Time_Valid Asn] == true };
    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
                          ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag] == true);
    - df_in_BOMMaster : Select ([Version].[Version Name] * [Activity3].[Activity3] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Location].[Location] * [Item].[Item] ) on row, 
                        ({ Measure.[W Material Production Association], Measure.[W Material Production Quantity Per]}) on column;

* Output Tables
    - df_out_TimeVaryingTact : Measure Group : 001.004W Solver Inputs Capacity Consumption Association
      Select ([Version].[Version Name].[CWV_MP] * [Resource].[Resource] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] * [Location].[Location] ) on row, 
             ({Measure.[W Input Resource Priority], Measure.[W Resource Category], Measure.[W Resource Consumed Quantity Per], Measure.[W Resource Consumption Association]}) on column ;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_CapacityConsumptionAssociation] for measures {[W Resource Consumed Quantity Per]} using scope (&MPV  *  &MFLocation)                                          
     using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )}; 

"""

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import os
import pandas as pd
import numpy as np
import datetime
import traceback
import gc
import tracemalloc

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_CapacityConsumptionAssociation'
is_local = common.gfn_get_isLocal()
COMMON_SOURCE_VERSION = common.G_SourceVersion

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)

def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

#def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
#    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)

def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

#def step(no, string):
#    logger.Step(p_step_no=no, p_step_desc=f'{string}')

try:
    ################################################################################################################
    # Batch 시작
    ################################################################################################################
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)
    
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> 전처리 : 모듈 내에서 사용될 Input table load Start')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_TactTime = read_csv_file("df_in_TactTime")
        df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
        df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
    
    #if df_in_TactTime.empty:
    #    raise Exception("=====> raise Exception: df_in_TactTime is empty")
    #
    #if df_in_ItemSiteAsn.empty:
    #    raise Exception("=====> raise Exception: df_in_ItemSiteAsn is empty")
    
    #if df_in_BOMMaster.empty:
    #    raise Exception("=====> raise Exception: df_in_BOMMaster is empty")
    
    vdCommon.gfn_stepLog('=====> Input table load End')
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_TactTime, 'df_in_TactTime',False)
    vdCommon.gfn_saveDf(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',False)
    vdCommon.gfn_saveDf(df_in_BOMMaster, 'df_in_BOMMaster',False)
    
    ################################################################################################################
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName = 'Version.[Version Name]'
    locationLocation = 'Location.[Location]'
    itemItem = 'Item.[Item]'
    lineLine = 'Line.[Line]'
    tactTimeTime = 'Tact Time_Time'
    tactTimePrty = 'Tact Time_Prty'
    resourceResource = 'Resource.[Resource]'
    activity1Activity1 = 'Activity1.[Activity1]'
    activity2Activity2 = 'Activity2.[Activity2]'
    activity3Activity3 = 'Activity3.[Activity3]'
    wInputResourcePriority = 'W Input Resource Priority'
    wResourceCategory = 'W Resource Category'
    wResourceConsumedQuantityPer = 'W Resource Consumed Quantity Per'
    wResourceConsumptionAssociation = 'W Resource Consumption Association'

    ################################################################################################################
    # STEP 1 :  데이터 선 가공
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 : input data machining')
    
    # STEP1-1 : Plan 대상 Item, Location 정보 대상 SET 구성, Item, Location 정보 df 구성, df_in_ItemSiteAsn distinct 필요없음,
    vdCommon.gfn_stepLog('=====> STEP 1-1 : item, Location distinct')
    df_itemLocation = df_in_ItemSiteAsn[[versionVersionName, locationLocation, itemItem]].copy(deep=True)
    #df_itemLocation.drop_duplicates(inplace=True)
    vdCommon.gfn_saveDf(df_itemLocation, 'df_itemLocation column adjust & drop_duplicates',False)
    vdCommon.gfn_stepLog('=====> STEP 1-1 : item, Location distinct End')
    del df_in_ItemSiteAsn
    
    vdCommon.gfn_stepLog('=====> STEP 1-2 : mergeA')
    # STEP1-2 : df_in_TactTime, df_itemLocation 조인
    df_mergeA = df_in_TactTime.merge(df_itemLocation, on=[versionVersionName, locationLocation, itemItem], how='inner')
    vdCommon.gfn_saveDf(df_mergeA, 'df_mergeA Data',False)
    vdCommon.gfn_stepLog('=====> STEP 1-2 : mergeA End')
    del [df_in_TactTime, df_itemLocation]
    
    # STEP1-3 : df_mergeA, df_in_BOMMaster 조인
    vdCommon.gfn_stepLog('=====> STEP 1-2 : mergeB')
    df_mergeB = df_mergeA.merge(df_in_BOMMaster, on=[versionVersionName, locationLocation, itemItem], how='inner')
    vdCommon.gfn_saveDf(df_mergeB, 'df_mergeB Data',False)
    vdCommon.gfn_stepLog('=====> STEP 1-2 : mergeB End')
    del [df_mergeA, df_in_BOMMaster]
    
    ################################################################################################################
    # STEP 2 : STEP1에서 구성한 SET을 대상으로 Measure Group : 001.004W Solver Inputs Capacity Consumption Association 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 : Final output table create')
    
    df_out_TimeVaryingTact = df_mergeB.copy(deep=True)
    
    # column 값 설정
    df_out_TimeVaryingTact[resourceResource]                = df_out_TimeVaryingTact[lineLine]
    df_out_TimeVaryingTact[wInputResourcePriority]          = df_out_TimeVaryingTact[tactTimePrty]
    df_out_TimeVaryingTact[wResourceCategory]               = 'I'
    df_out_TimeVaryingTact[wResourceConsumedQuantityPer]    = df_out_TimeVaryingTact[tactTimeTime]
    df_out_TimeVaryingTact[wResourceConsumptionAssociation] = 1
    
    # out Data 설정
    cList_Out = [versionVersionName, resourceResource, activity1Activity1, activity2Activity2, activity3Activity3, 
                 locationLocation, wInputResourcePriority, wResourceCategory, wResourceConsumedQuantityPer, 
                 wResourceConsumptionAssociation]
    df_out_TimeVaryingTact = df_out_TimeVaryingTact[cList_Out].copy(deep=True)
    
    #df_out_TimeVaryingTact.drop_duplicates(subset=[versionVersionName, resourceResource, activity1Activity1, 
    # activity2Activity2, activity3Activity3, locationLocation],
    #                                       keep='first', inplace=True, ignore_index=True)
    
    # 버전 처리
    #df_out_TimeVaryingTact[versionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_TimeVaryingTact.shape
    note(f'=====> Final df_out_TimeVaryingTact rows : {row_count}, column : {col_count}')
    
    vdCommon.gfn_saveDf(df_out_TimeVaryingTact, 'df_out_TimeVaryingTact',False)
    vdCommon.gfn_stepLog('=====> STEP 2-1 Final output table create End')
    del df_mergeB

    if is_local:
        vdCommon.gfn_stepLog('=====> STEP 2-2 Local CSV create')
        save_csv_file(df_out_TimeVaryingTact, 'df_out_TimeVaryingTact')
    
    vdCommon.gfn_stepLog('=====> STEP 2-3 End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_TimeVaryingTact = pd.DataFrame([], columns=[])
    
finally:
    vdCommon.gfn_stepLog('plugin Execution End ')
    
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    
    # logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    # logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    
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