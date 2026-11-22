"""
* 프로그램명 
    - PY_MG_FrozenWindow

* 내용
    - [Solver Input] MFG(생산) / BOD(선적) Activiy별 확정구간 반영
    - FP Period 기준으로 생산 확정
    - FP Period + Shipment L/T 감안 BOD 확정

* 변경이력
    - 2024.08.23 / 양희영 / Create
    - 2025.06.27 / 양희영 / Update

* Flow Summary

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_FrozenFence : Measure Group: Frozen Fence
                          Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location]  ) on row, ({Measure.[Frozen Fence_Period] }) on column; 
    - 사용안함.df_in_SOPFrozenList : Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] ) on row, ({ Measure.[SOP Frozen List_FP Period] }) on column limit 1000;
    - df_in_BOMMaster : Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, 
                        ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Status]}) on column;
    - df_in_BODItem : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Shipment LT]}) on column;
    	 df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
    	                     ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Flag], Measure.[Item Site Asn_Stage]}) 
    	                     on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_BODItemMtrlFull: MG : BOD Item Mtrl Full
                             Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]) on row, 
                             ({Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_Lot Size], Measure.[BOD Item Mtrl Full_MSL3]}) 
                             on column.filter((isnull(Measure.[BOD Item Mtrl Full_EFF Enddate]) || Measure.[BOD Item Mtrl Full_EFF Enddate] > Measure.[W Plan Start Date]) && (isnull(Measure.[BOD Item Mtrl Full_EFF Startdate]) || Measure.[BOD Item Mtrl Full_EFF Startdate]< Measure.[W Plan End Date]));
    - df_in_L3FrozenPeriod : MG: Supply Frozen Mtrl L3 W
                             Select ([Version].[Version Name] * &MPCurrentWeek * [Item Material].[MSL3]) on row, ({Measure.[Supply Frozen Mtrl L3 W_Fix Range], Measure.[Supply Frozen Mtrl L3 W_IsRelativeWeek]}) on column;
    - df_in_L5FrozenPeriod : MG: Supply Frozen Mtrl L5 W_Fix Range
                             Select ([Version].[Version Name] * &MPCurrentWeek * [Item Material].[MSL5]) on row, ({Measure.[Supply Frozen Mtrl L5 W_Fix Range], Measure.[Supply Frozen Mtrl L5 W_IsRelativeWeek]}) on column;
    - df_in_L5Frozen : MG: Supply Frozen Mtrl L5_Delete
                      Select ([Version].[Version Name] * [Item Material].[MSL5]) on row, ({Measure.[Supply Frozen Mtrl L5_Delete] }) 
                      on column.filter(isnull(Measure.[Supply Frozen Mtrl L5_Delete]) || Measure.[Supply Frozen Mtrl L5_Delete] =="N");
    - df_in_MtrlFrozenPeriod : MG: Supply Frozen Mtrl Item W_Fix Range
                              Select ([Version].[Version Name] * &MPCurrentWeek * [Location].[Location] * [Item Material].[Item Material]) on row, 
                              ({Measure.[Supply Frozen Mtrl Item W_Fix Range], Measure.[Supply Frozen Mtrl Item W_IsRelativeWeek]}) on column;
    - df_in_MtrlFrozen : MG: Supply Frozen Mtrl Item_Delete
                         Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material]) on row, 
                         ({Measure.[Supply Frozen Mtrl Item_Delete]}) on column.filter(isnull(Measure.[Supply Frozen Mtrl Item_Delete]) || Measure.[Supply Frozen Mtrl Item_Delete] =="N");
    - df_in_Material : Item Material Dimension
                      Select ([Item Material].[Item Material] * [Item Material].[MSL3] * [Item Material].[MSL5]);
    - df_in_Time : Select ([Time].[Week] * [Time].[Day]); 
    - df_in_PlanHorizon : MG : MP Bach_Plan Horizon
                         Select ([Version].[Version Name]) on row, ({Measure.[MP Plan Current Week], Measure.[MP Plan End Date], Measure.[MP Plan End Week], Measure.[MP Plan Start Date], Measure.[MP Plan Start Week]}) on column;
* Output Tables
    - df_out_FrozenWindow : Measure Group : 001.009W Solver Inputs Frozen Window
	                        Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Frozen Window]}) on column;
	

* 테스트 스크립트
    EXEC plugin instance [PY_MG_FrozenWindow] for measures {[W Frozen Window]} using scope (&MPV * &MFLocation) using arguments {
      (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (ParamOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
      
"""

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import os
import pandas as pd
import numpy as np
import datetime as dt
import traceback
import gc
import tracemalloc

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_FrozenWindow'
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
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====>STEP 0-1 DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName       = 'Version.[Version Name]'
    itemItem                 = 'Item.[Item]'
    itemMaterialItemMaterial = 'Item Material.[Item Material]'
    itemMaterialMSL3         = 'Item Material.[MSL3]'
    itemMaterialMSL5         = 'Item Material.[MSL5]'
    timeWeek                 = 'Time.[Week]'
    timeDay                  = 'Time.[Day]'
    locationLocation         = "Location.[Location]"
    subLocationSubLocation   = 'Sub Location.[Sub Location]'
    transModeTransMode       = 'Trans Mode.[Trans Mode]'
    activity1activity1       = "Activity1.[Activity1]"
    activity2activity2       = "Activity2.[Activity2]"
    activity3Activity3       = "Activity3.[Activity3]"
    bOMInfoBOMID             = 'BOM Info.[BOM ID]'
    
    bOMMaster_BOMID          = 'BOM Master_BOM ID'
    sOPFrozenList_FPPeriod   = 'SOP Frozen List_FP Period'
    frozenFence_Period       = 'Frozen Fence_Period'
    wFrozenWindow            = 'W Frozen Window'
    frozenfence              = 'frozenfence'
    bODItem_ShipmentLT       = 'BOD Item_Shipment LT'
    last_Day                 = 'Last_Day'
    curweek                  = 'curweek'
    curweekendday            = 'curweekendday'
    mPPlanCurrentWeek        = 'MP Plan Current Week'
    mPPlanStartWeek          = 'MP Plan Start Week'
    mPPlanEndWeek            = 'MP Plan End Week'
    mPPlanStartDate          = 'MP Plan Start Date'
    mPPlanEndDate            = 'MP Plan End Date'
    
    supplyFrozenMtrlItemW_FixRange       = 'Supply Frozen Mtrl Item W_Fix Range'
    supplyFrozenMtrlItemW_IsRelativeWeek = 'Supply Frozen Mtrl Item W_IsRelativeWeek'
    supplyFrozenMtrlL5W_FixRange         = 'Supply Frozen Mtrl L5 W_Fix Range'
    supplyFrozenMtrlL5W_IsRelativeWeek   = 'Supply Frozen Mtrl L5 W_IsRelativeWeek'
    supplyFrozenMtrlL3W_FixRange         = 'Supply Frozen Mtrl L3 W_Fix Range'
    supplyFrozenMtrlL3W_IsRelativeWeek   = 'Supply Frozen Mtrl L3 W_IsRelativeWeek'    
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-2 : Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_FrozenFence   = read_csv_file("df_in_FrozenFence")
        #df_in_SOPFrozenList = read_csv_file("df_in_SOPFrozenList") # df_in_FrozenFence 로 대체
        df_in_BOMMaster     = read_csv_file("df_in_BOMMaster")
        df_in_BODItem       = read_csv_file("df_in_BODItem")
        df_in_ItemSiteAsn   = read_csv_file("df_in_ItemSiteAsn")
        
        df_in_BODItemMtrlFull  = read_csv_file("df_in_BODItemMtrlFull")
        df_in_L3FrozenPeriod   = read_csv_file("df_in_L3FrozenPeriod")
        df_in_L5FrozenPeriod   = read_csv_file("df_in_L5FrozenPeriod")
        df_in_L5Frozen         = read_csv_file("df_in_L5Frozen")
        df_in_MtrlFrozenPeriod = read_csv_file("df_in_MtrlFrozenPeriod")
        df_in_MtrlFrozen       = read_csv_file("df_in_MtrlFrozen")
        df_in_Material         = read_csv_file("df_in_Material")
        df_in_Time             = read_csv_file("df_in_Time")
        df_in_PlanHorizon      = read_csv_file("df_in_PlanHorizon")
        
    #if df_in_BOMMaster.empty:
    #    raise Exception("=====> raise Exception: df_in_BOMMaster is empty")
    #
    #if df_in_ItemSiteAsn.empty:
    #    raise Exception("=====> raise Exception: df_in_ItemSiteAsn is empty")
    #
    #if df_in_Material.empty:
    #    raise Exception("=====> raise Exception: df_in_Material is empty")
    #
    #if df_in_Time.empty:
    #    raise Exception("=====> raise Exception: df_in_Time is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    if df_in_PlanHorizon[mPPlanStartDate].dtype != 'datetime64[ns]':
        df_in_PlanHorizon[mPPlanStartDate] = pd.to_datetime(df_in_PlanHorizon[mPPlanStartDate], format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_PlanHorizon[mPPlanEndDate].dtype != 'datetime64[ns]':
        df_in_PlanHorizon[mPPlanEndDate]   = pd.to_datetime(df_in_PlanHorizon[mPPlanEndDate], format='%m/%d/%Y %I:%M:%S %p')
    
    df_in_Time[timeDay]                = pd.to_datetime(df_in_Time[timeDay], format='%Y-%m-%d')
    
    df_in_Time        = df_in_Time.astype({timeWeek: 'int64'}, copy=True)
    df_in_PlanHorizon = df_in_PlanHorizon.astype({mPPlanCurrentWeek: 'int64', mPPlanStartWeek: 'int64', mPPlanEndWeek: 'int64'}, copy=True)
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_FrozenFence, 'df_in_FrozenFence',False)
    #vdCommon.gfn_saveDf(df_in_SOPFrozenList, 'df_in_SOPFrozenList',False)
    vdCommon.gfn_saveDf(df_in_BOMMaster, 'df_in_BOMMaster',False)
    vdCommon.gfn_saveDf(df_in_BODItem, 'df_in_BODItem',False)
    vdCommon.gfn_saveDf(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',False)
    
    vdCommon.gfn_saveDf(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull',False)
    vdCommon.gfn_saveDf(df_in_L3FrozenPeriod, 'df_in_L3FrozenPeriod',False)
    vdCommon.gfn_saveDf(df_in_L5FrozenPeriod, 'df_in_L5FrozenPeriod',False)
    vdCommon.gfn_saveDf(df_in_L5Frozen, 'df_in_L5Frozen',False)
    vdCommon.gfn_saveDf(df_in_MtrlFrozenPeriod, 'df_in_MtrlFrozenPeriod',False)
    vdCommon.gfn_saveDf(df_in_MtrlFrozen, 'df_in_MtrlFrozen',False)
    vdCommon.gfn_saveDf(df_in_Material, 'df_in_Material',False)
    vdCommon.gfn_saveDf(df_in_Time, 'df_in_Time',False)
    vdCommon.gfn_saveDf(df_in_PlanHorizon, 'df_in_PlanHorizon',False)
    
    vdCommon.gfn_stepLog('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-4 : 추가 df Create ')
    # df_Week 생성
    df_Week = df_in_Time.copy()
    del df_in_Time
    
    df_Week[last_Day] = df_Week[timeDay]
    df_Week = df_Week.groupby([timeWeek], as_index=False)[last_Day].max()
    vdCommon.gfn_saveDf(df_Week, 'df_Week',False)
    
    # df_PlanHorizon 생성 : df_in_PlanHorizon 첫번째 행 : 의미 없음. 전체가 1건
    #df_PlanHorizon = df_in_PlanHorizon.head(1)
    #vdCommon.gfn_saveDf(df_PlanHorizon, 'df_PlanHorizon',False)
    
    # df_curweek 생성
    df_curweek = df_in_PlanHorizon.merge(df_Week, left_on=[mPPlanCurrentWeek], right_on=[timeWeek] , how='inner')
    df_curweek.rename(columns={last_Day:curweekendday, timeWeek:curweek}, inplace=True)
    #df_curweek 칼럼정리
    df_curweek = df_curweek[[versionVersionName, curweek, curweekendday]]
    vdCommon.gfn_saveDf(df_curweek, 'df_curweek',False)
    
    vdCommon.gfn_stepLog('=====> STEP 0-5 : 추가 df Create End')
    ################################################################################################################
    # STEP 1 : 공장 fence 입력 data 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1-1 : BOM fence data Create')
    
    # df_in_ItemSiteAsn distinct 필요없음., df_in_BOMMaster Filtering    
    # -distinct item
    Item_series = df_in_ItemSiteAsn[itemItem].unique()
    
    # -distinct location
    Location_series = df_in_ItemSiteAsn[locationLocation].unique()
    
    #df_in_BOMMaster Merge Filtering
    df_in_BOMMaster = df_in_BOMMaster.merge(df_in_ItemSiteAsn, left_on=[versionVersionName, locationLocation, bOMMaster_BOMID], 
                                                               right_on=[versionVersionName, locationLocation, itemItem], how='inner')
    del df_in_ItemSiteAsn
    
    # column 정리
    df_in_BOMMaster = df_in_BOMMaster[[versionVersionName, locationLocation, bOMInfoBOMID, itemItem]]
    vdCommon.gfn_saveDf(df_in_BOMMaster, 'df_in_BOMMaster Merge Filtering',False)
    
    # df_in_SOPFrozenList group by min
    #df_SOPFrozenList_Min = df_in_SOPFrozenList.groupby([versionVersionName, itemItem, locationLocation], as_index=False)[sOPFrozenList_FPPeriod].min()
    df_FrozenFence_Min = df_in_FrozenFence.groupby([versionVersionName, itemItem, locationLocation], as_index=False)[frozenFence_Period].min()
    df_FrozenFence_Min.rename(columns={frozenFence_Period:frozenfence}, inplace=True)
    vdCommon.gfn_saveDf(df_FrozenFence_Min, 'df_FrozenFence_Min',False)
    del df_in_FrozenFence
    
    # df_FrozenFence_Min & df_in_BOMMaster Merge, BOM fence data Create
    df_BOMFense = df_FrozenFence_Min.merge(df_in_BOMMaster, on=[versionVersionName, itemItem, locationLocation], how='inner')
    df_BOMFense[activity1activity1] = df_BOMFense[bOMInfoBOMID]
    df_BOMFense[activity2activity2] = 'RT_' + df_BOMFense[bOMInfoBOMID] + '@' + df_BOMFense[locationLocation]
    df_BOMFense[activity3Activity3] =  df_BOMFense[itemItem]
    df_BOMFense[wFrozenWindow]      = df_BOMFense[frozenfence]
    del df_in_BOMMaster
    
    # column 정리
    cList_Out = [versionVersionName, activity1activity1, activity2activity2, activity3Activity3, wFrozenWindow]
    df_BOMFense = df_BOMFense[cList_Out]
    vdCommon.gfn_saveDf(df_BOMFense, 'df_BOMFense',False)
    
    vdCommon.gfn_stepLog('=====> STEP 1-2 : BOM fence data Create End')
	   
	   ################################################################################################################
    # STEP 2 :  BOD fence 입력 data 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2-1 : BOD fence Create')
    
    # df_in_BODItem  Item Filtering, df_in_BODItem  location,  sublocation  Filtering
    # Item Filtering: df_in_BODItem & Item_series (Item 기준)
    df_in_BODItem = df_in_BODItem[df_in_BODItem[itemItem].isin(Item_series)]
    
    # Location Filtering
    df_in_BODItem = df_in_BODItem[(df_in_BODItem[locationLocation].isin(Location_series)) | 
                                  (df_in_BODItem[subLocationSubLocation].isin(Location_series))]
    vdCommon.gfn_saveDf(df_in_BODItem, 'df_in_BODItem Filtering',False)
    
    # df_FrozenFence_Min & df_in_BODItem  Merge, BOD fence data Create
    df_BODFense = df_FrozenFence_Min.merge(df_in_BODItem, on=[versionVersionName, itemItem, locationLocation], how='inner')
    df_BODFense[activity1activity1] = (df_BODFense[locationLocation] + "_" + 
                                       df_BODFense[subLocationSubLocation] + "_" + 
                                       df_BODFense[transModeTransMode])
    df_BODFense[activity2activity2] = df_BODFense[transModeTransMode]
    df_BODFense[activity3Activity3] = df_BODFense[itemItem]
    df_BODFense[wFrozenWindow]      = df_BODFense[frozenfence] + df_BODFense[bODItem_ShipmentLT]
    del [df_FrozenFence_Min, df_in_BODItem]
    
    # column 정리
    df_BODFense = df_BODFense[cList_Out]
    vdCommon.gfn_saveDf(df_BODFense, 'df_BODFense',False)
    
    vdCommon.gfn_stepLog('=====> STEP 2-2 : BOD fence Create End')
    
    ################################################################################################################
    # STEP 3 : df_MtrlFrozenItem Set 구성 : Item 레벨 자재 Fence 대상 발췌하여 Set 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 3-1 : df_MtrlFrozenItem Set Create')
    
    # Merge : df_in_MtrlFrozen & df_in_MtrlFrozenPeriod
    df_MtrlFrozen_Period = df_in_MtrlFrozen.merge(df_in_MtrlFrozenPeriod, on=[versionVersionName, itemMaterialItemMaterial, locationLocation], how='inner')
    del [df_in_MtrlFrozen, df_in_MtrlFrozenPeriod]
    vdCommon.gfn_saveDf(df_MtrlFrozen_Period, 'df_MtrlFrozen_Period',False)
    
    ##----------------------------------------------------------
    # df_MtrlFrozenItem_1 구성 :  [Frozen Mtrl Item W_IsRelativeWeek] = false , [Supply Frozen Mtrl Item W_Fix Range] 에는 기간값이 입력 ------ 
    df_MtrlFrozenItem_1 = df_MtrlFrozen_Period.loc[df_MtrlFrozen_Period[supplyFrozenMtrlItemW_IsRelativeWeek].isna() |
                                                  (df_MtrlFrozen_Period[supplyFrozenMtrlItemW_IsRelativeWeek] == False)].copy()
    df_MtrlFrozenItem_1[wFrozenWindow] = df_MtrlFrozenItem_1[supplyFrozenMtrlItemW_FixRange]
    vdCommon.gfn_saveDf(df_MtrlFrozenItem_1, 'df_MtrlFrozenItem_1 ORG',False)
    
    #칼럼정리
    df_MtrlFrozenItem_1 = df_MtrlFrozenItem_1[[versionVersionName,locationLocation,itemMaterialItemMaterial,wFrozenWindow]]
    vdCommon.gfn_saveDf(df_MtrlFrozenItem_1, 'df_MtrlFrozenItem_1',False)
    
    ##----------------------------------------------------------
    # df_MtrlFrozenItem_2 구성 :  [Frozen Mtrl Item W_IsRelativeWeek] = true , [Supply Frozen Mtrl Item W_Fix Range] 에는 주차값이 입력 ------ 
    df_MtrlFrozenItem_2 = df_MtrlFrozen_Period.loc[df_MtrlFrozen_Period[supplyFrozenMtrlItemW_IsRelativeWeek] == True].copy()
    del df_MtrlFrozen_Period
    vdCommon.gfn_saveDf(df_MtrlFrozenItem_2, 'df_MtrlFrozenItem_2 ORG1',False)
    
    # Merge : df_MtrlFrozenItem_2 & df_Week
    df_MtrlFrozenItem_2 = df_MtrlFrozenItem_2.astype({supplyFrozenMtrlItemW_FixRange: 'int64'}, copy=True)
    df_MtrlFrozenItem_2 = df_MtrlFrozenItem_2.merge(df_Week, left_on=[supplyFrozenMtrlItemW_FixRange], right_on=[timeWeek], how='inner', suffixes=('', '_y'))
    vdCommon.gfn_saveDf(df_MtrlFrozenItem_2, 'df_MtrlFrozenItem_2 ORG2',False)
    # Merge : df_MtrlFrozenItem_2 & df_in_PlanHorizon : df_in_PlanHorizon 는 1건
    df_MtrlFrozenItem_2 = df_MtrlFrozenItem_2.merge(df_in_PlanHorizon, on=[versionVersionName], how='inner')
    
    # filtering : c.day >= d.MP Plan Start Date
    df_MtrlFrozenItem_2 = df_MtrlFrozenItem_2.loc[df_MtrlFrozenItem_2[last_Day] >= df_MtrlFrozenItem_2[mPPlanStartDate]]
    vdCommon.gfn_saveDf(df_MtrlFrozenItem_2, 'df_MtrlFrozenItem_2 ORG3',False)
    
    # Merge : df_MtrlFrozenItem_2 & df_curweekday
    df_MtrlFrozenItem_2 = df_MtrlFrozenItem_2.merge(df_curweek, on=[versionVersionName], how='inner')
    
    df_MtrlFrozenItem_2[wFrozenWindow] = np.where(df_MtrlFrozenItem_2[last_Day] > df_MtrlFrozenItem_2[mPPlanEndDate], 34,
                                                  ((df_MtrlFrozenItem_2[last_Day] - df_MtrlFrozenItem_2[curweekendday]).dt.days / 7).astype('int64')  # trunc 소수
                                                 )
    df_MtrlFrozenItem_2[wFrozenWindow] = np.where((df_MtrlFrozenItem_2[wFrozenWindow] < 0), 0, df_MtrlFrozenItem_2[wFrozenWindow]) # greatest ( 값, 0)    
    vdCommon.gfn_saveDf(df_MtrlFrozenItem_2, 'df_MtrlFrozenItem_2 ORG4',False)
    
    # 칼럼정리
    df_MtrlFrozenItem_2 = df_MtrlFrozenItem_2[[versionVersionName, locationLocation, itemMaterialItemMaterial, wFrozenWindow]]
    vdCommon.gfn_saveDf(df_MtrlFrozenItem_2, 'df_MtrlFrozenItem_2',False)
    
    # union all : concat()
    df_MtrlFrozenItem = pd.concat([df_MtrlFrozenItem_1, df_MtrlFrozenItem_2])
    vdCommon.gfn_saveDf(df_MtrlFrozenItem, 'df_MtrlFrozenItem',False)
    
    vdCommon.gfn_stepLog('=====> STEP 3-2 : df_MtrlFrozenItem Set Create End')
    
    ################################################################################################################
    # STEP 4 : df_MtrlFrozenMSL5 Set  구성 : MSL5 레벨 자재 Fence 대상 발췌하여  Set 구성 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 4-1 : df_MtrlFrozenMSL5 Set Create')
    
    # Merge : df_in_MtrlFrozen & df_in_MtrlFrozenPeriod
    df_L5Frozen_Period = df_in_L5Frozen.merge(df_in_L5FrozenPeriod, on=[versionVersionName, itemMaterialMSL5], how='inner')
    del [df_in_L5Frozen, df_in_L5FrozenPeriod]
    
    ##----------------------------------------------------------
    # df_MSL5_1 구성 :  [Supply Frozen Mtrl L5 W_IsRelativeWeek] = false , [Supply Frozen Mtrl L5 W_Fix Range] 에는 기간값이 입력 ------ 
    df_MSL5_1 = df_L5Frozen_Period.loc[df_L5Frozen_Period[supplyFrozenMtrlL5W_IsRelativeWeek].isna() |
                                       (df_L5Frozen_Period[supplyFrozenMtrlL5W_IsRelativeWeek] == False)].copy()
    df_MSL5_1[wFrozenWindow] = df_MSL5_1[supplyFrozenMtrlL5W_FixRange]
    vdCommon.gfn_saveDf(df_MSL5_1, 'df_MSL5_1 ORG',False)
    
    #칼럼정리
    df_MSL5_1 = df_MSL5_1[[versionVersionName,itemMaterialMSL5,wFrozenWindow]]
    vdCommon.gfn_saveDf(df_MSL5_1, 'df_MSL5_1',False)
    
    ##----------------------------------------------------------
    # df_MSL5_2 구성 :  [Supply Frozen Mtrl L5 W_IsRelativeWeek] = true , [Supply Frozen Mtrl L5 W_Fix Range] 에는 주차값이 입력 ------ 
    df_MSL5_2 = df_L5Frozen_Period.loc[df_L5Frozen_Period[supplyFrozenMtrlL5W_IsRelativeWeek] == True].copy()
    del df_L5Frozen_Period
    
    # Merge : df_MSL5_2 & df_Week
    df_MSL5_2 = df_MSL5_2.astype({supplyFrozenMtrlL5W_FixRange: 'int64'}, copy=True)
    df_MSL5_2 = df_MSL5_2.merge(df_Week, left_on=[supplyFrozenMtrlL5W_FixRange], right_on=[timeWeek], how='inner', suffixes=('', '_y'))
    # Merge : df_MSL5_2 & df_in_PlanHorizon : df_in_PlanHorizon 는 1건
    df_MSL5_2 = df_MSL5_2.merge(df_in_PlanHorizon, on=[versionVersionName], how='inner')
    
    # filtering : c.day >= d.MP Plan Start Date
    df_MSL5_2 = df_MSL5_2.loc[df_MSL5_2[last_Day] >= df_MSL5_2[mPPlanStartDate]]
    
    # Merge : df_MSL5_2 & df_curweekday
    df_MSL5_2 = df_MSL5_2.merge(df_curweek, on=[versionVersionName], how='inner')
    
    df_MSL5_2[wFrozenWindow] = np.where(df_MSL5_2[last_Day] > df_MSL5_2[mPPlanEndDate], 34,
                                                  ((df_MSL5_2[last_Day] - df_MSL5_2[curweekendday]).dt.days / 7).astype('int64')  # trunc 소수
                                                 )
    df_MSL5_2[wFrozenWindow] = np.where((df_MSL5_2[wFrozenWindow] < 0), 0, df_MSL5_2[wFrozenWindow]) # greatest ( 값, 0)
    vdCommon.gfn_saveDf(df_MSL5_2, 'df_MSL5_2 ORG',False)
    
    #칼럼정리
    df_MSL5_2 = df_MSL5_2[[versionVersionName,itemMaterialMSL5,wFrozenWindow]]
    vdCommon.gfn_saveDf(df_MSL5_2, 'df_MSL5_2',False)
    
    # union all : concat()
    df_MSL5 = pd.concat([df_MSL5_1, df_MSL5_2])
    del [df_MSL5_1, df_MSL5_2]
    
    # df_MtrlFrozenMSL5 구성 : Merge : df_MSL5 & df_in_Material
    df_MtrlFrozenMSL5 = df_MSL5.merge(df_in_Material, on=[itemMaterialMSL5], how='inner')
    
    # 칼럼정리
    df_MtrlFrozenMSL5 = df_MtrlFrozenMSL5[[versionVersionName, itemMaterialItemMaterial, wFrozenWindow]]
    #df_MtrlFrozenMSL5.drop_duplicates(inplace=True)
    vdCommon.gfn_saveDf(df_MtrlFrozenMSL5, 'df_MtrlFrozenMSL5',False)
    
    vdCommon.gfn_stepLog('=====> STEP 4-2 : df_MtrlFrozenMSL5 Set Create End')
    
    ################################################################################################################
    # STEP 5 : df_MtrlFrozenMSL3 Set  구성 : MSL3 레벨 자재 Fence 대상 발췌하여 Set 구성(기본 Set임)
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 5-1 : df_MtrlFrozenMSL3 Set Create')
    
    ##----------------------------------------------------------
    # df_MSL3_1 구성 :  [Supply Frozen Mtrl L3 W_IsRelativeWeek] = false , [Supply Frozen Mtrl L3 W_Fix Range] 에는 기간값이 입력 ------ 
    df_MSL3_1 = df_in_L3FrozenPeriod.loc[df_in_L3FrozenPeriod[supplyFrozenMtrlL3W_IsRelativeWeek].isna() |
                                         (df_in_L3FrozenPeriod[supplyFrozenMtrlL3W_IsRelativeWeek] == False)].copy()
    df_MSL3_1[wFrozenWindow] = df_MSL3_1[supplyFrozenMtrlL3W_FixRange]
    vdCommon.gfn_saveDf(df_MSL3_1, 'df_MSL3_1 ORG',False)
    
    #칼럼정리
    df_MSL3_1 = df_MSL3_1[[versionVersionName,itemMaterialMSL3,wFrozenWindow]]
    vdCommon.gfn_saveDf(df_MSL3_1, 'df_MSL3_1',False)
    
    ##----------------------------------------------------------
    # df_MSL3_2 구성 :  [Supply Frozen Mtrl L3 W_IsRelativeWeek] = true , [Supply Frozen Mtrl L3 W_Fix Range] 에는 주차값이 입력 ------ 
    df_MSL3_2 = df_in_L3FrozenPeriod.loc[df_in_L3FrozenPeriod[supplyFrozenMtrlL3W_IsRelativeWeek] == True].copy()
    del df_in_L3FrozenPeriod;
    
    # Merge : df_MSL3_2 & df_Week
    df_MSL3_2 = df_MSL3_2.astype({supplyFrozenMtrlL3W_FixRange: 'int64'}, copy=True)
    df_MSL3_2 = df_MSL3_2.merge(df_Week, left_on=[supplyFrozenMtrlL3W_FixRange], right_on=[timeWeek], how='inner', suffixes=('', '_y'))
    # Merge : df_MSL3_2 & df_in_PlanHorizon : df_in_PlanHorizon 는 1건
    df_MSL3_2 = df_MSL3_2.merge(df_in_PlanHorizon, on=[versionVersionName], how='inner')
    
    # filtering : c.day >= d.MP Plan Start Date
    df_MSL3_2 = df_MSL3_2.loc[df_MSL3_2[last_Day] >= df_MSL3_2[mPPlanStartDate]]
    
    # Merge : df_MSL3_2 & df_curweekday
    df_MSL3_2 = df_MSL3_2.merge(df_curweek, on=[versionVersionName], how='inner')
    
    df_MSL3_2[wFrozenWindow] = np.where(df_MSL3_2[last_Day] > df_MSL3_2[mPPlanEndDate], 34,
                                        ((df_MSL3_2[last_Day] - df_MSL3_2[curweekendday]).dt.days / 7).astype('int64')  # trunc 소수
                                                 )
    df_MSL3_2[wFrozenWindow] = np.where((df_MSL3_2[wFrozenWindow] < 0), 0, df_MSL3_2[wFrozenWindow]) # greatest ( 값, 0)
    vdCommon.gfn_saveDf(df_MSL3_2, 'df_MSL3_2 ORG',False)
    
    del [df_in_PlanHorizon, df_Week, df_curweek]
    
    #칼럼정리
    df_MSL3_2 = df_MSL3_2[[versionVersionName,itemMaterialMSL3,wFrozenWindow]]
    vdCommon.gfn_saveDf(df_MSL3_2, 'df_MSL3_2',False)
    
    # union all : concat()
    df_MSL3 = pd.concat([df_MSL3_1, df_MSL3_2])
    del [df_MSL3_1, df_MSL3_2]
    
    # Group by : df_in_Material
    df_Material_MSL3 = df_in_Material.groupby([itemMaterialItemMaterial], as_index=False)[itemMaterialMSL3].max()
    del df_in_Material
    vdCommon.gfn_saveDf(df_Material_MSL3, 'df_Material_MSL3',False)
    
    # df_MtrlFrozenMSL3 구성 : Merge : df_MSL3 & df_Material_MSL3
    df_MtrlFrozenMSL3 = df_MSL3.merge(df_Material_MSL3, on=[itemMaterialMSL3], how='inner')
    del df_Material_MSL3
    
    # 칼럼정리
    df_MtrlFrozenMSL3 = df_MtrlFrozenMSL3[[versionVersionName, itemMaterialItemMaterial, wFrozenWindow]]
    #df_MtrlFrozenMSL3.drop_duplicates(inplace=True)
    vdCommon.gfn_saveDf(df_MtrlFrozenMSL3, 'df_MtrlFrozenMSL3',False)
    
    vdCommon.gfn_stepLog('=====> STEP 5-2 : df_MtrlFrozenMSL3 Set Create End')
    
    ################################################################################################################
    # STEP 6 : 자재 Fence 입력 001.009W Solver Inputs Frozen Window : df_MtrlFense
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 6-1 : 자재 Fence Create')
    
    # df_MtrlBODFrozen 구성 : Merge : df_in_BODItemMtrlFull & df_MtrlFrozenItem----------------------------------------
    df_MtrlBODFrozen = df_in_BODItemMtrlFull.merge(df_MtrlFrozenItem, on=[versionVersionName, locationLocation, itemMaterialItemMaterial], how='inner')
    del df_MtrlFrozenItem
    
    df_MtrlBODFrozen[activity1activity1] = (df_MtrlBODFrozen[locationLocation] + '_' + 
                                            df_MtrlBODFrozen[subLocationSubLocation] + '_' + 
                                            df_MtrlBODFrozen[transModeTransMode])
    df_MtrlBODFrozen[activity2activity2] = df_MtrlBODFrozen[transModeTransMode]
    df_MtrlBODFrozen[activity3Activity3] = df_MtrlBODFrozen[itemMaterialItemMaterial]
        
    vdCommon.gfn_saveDf(df_MtrlBODFrozen, 'df_MtrlBODFrozen',False)
    
    # df_MSL5Frozen 구성 -------------------------------------------
    # df_in_BODItemMtrlFull  Filtering : 
    # df_in_BODItemMtrlFull 중 df_MtrlBODFrozen 에 없는 Data 추출 : not exists
    df_BODItemMtrlFull_Flt_1 = df_in_BODItemMtrlFull[~df_in_BODItemMtrlFull.set_index([versionVersionName, 
                                                                                       itemMaterialItemMaterial, 
                                                                                       locationLocation,
                                                                                       subLocationSubLocation,
                                                                                       transModeTransMode]).index.isin(
                                                      df_MtrlBODFrozen.set_index([versionVersionName, 
                                                                                  itemMaterialItemMaterial, 
                                                                                  locationLocation,
                                                                                  subLocationSubLocation,
                                                                                  transModeTransMode]).index)]
    del df_in_BODItemMtrlFull
    
    vdCommon.gfn_saveDf(df_BODItemMtrlFull_Flt_1, 'df_BODItemMtrlFull_Flt_1',False)
    
    # Merge : df_BODItemMtrlFull_Flt_1 & df_MtrlFrozenMSL5
    df_MSL5Frozen = df_BODItemMtrlFull_Flt_1.merge(df_MtrlFrozenMSL5, on=[versionVersionName, itemMaterialItemMaterial], how='inner')
    del df_MtrlFrozenMSL5
    
    df_MSL5Frozen[activity1activity1] = (df_MSL5Frozen[locationLocation] + '_' + 
                                         df_MSL5Frozen[subLocationSubLocation] + '_' + 
                                         df_MSL5Frozen[transModeTransMode])
    df_MSL5Frozen[activity2activity2] = df_MSL5Frozen[transModeTransMode]
    df_MSL5Frozen[activity3Activity3] = df_MSL5Frozen[itemMaterialItemMaterial]
    
    vdCommon.gfn_saveDf(df_MSL5Frozen, 'df_MSL5Frozen',False)
    
    # df_MSL3Frozen 구성 -------------------------------------------
    # df_in_BODItemMtrlFull 중 df_MtrlBODFrozen 에 없는 Data 추출 : not exists ==> df_BODItemMtrlFull_Flt_1 &
    # df_BODItemMtrlFull_Flt_1 중 df_MSL5Frozen 에 없는 Data 추출 : not exists ==> df_BODItemMtrlFull_Flt_2
    df_BODItemMtrlFull_Flt_2 = df_BODItemMtrlFull_Flt_1[~df_BODItemMtrlFull_Flt_1.set_index([versionVersionName, 
                                                                                             itemMaterialItemMaterial, 
                                                                                             locationLocation,
                                                                                             subLocationSubLocation,
                                                                                             transModeTransMode]).index.isin(
                                                         df_MSL5Frozen.set_index([versionVersionName, 
                                                                                  itemMaterialItemMaterial, 
                                                                                  locationLocation,
                                                                                  subLocationSubLocation,
                                                                                  transModeTransMode]).index)]
    del df_BODItemMtrlFull_Flt_1
    
    vdCommon.gfn_saveDf(df_BODItemMtrlFull_Flt_2, 'df_BODItemMtrlFull_Flt_2',False)

    # Merge : df_BODItemMtrlFull_Flt_2 & df_MtrlFrozenMSL3
    df_MSL3Frozen = df_BODItemMtrlFull_Flt_2.merge(df_MtrlFrozenMSL3, on=[versionVersionName, itemMaterialItemMaterial], how='inner')
    del [df_BODItemMtrlFull_Flt_2, df_MtrlFrozenMSL3]
    
    df_MSL3Frozen[activity1activity1] = (df_MSL3Frozen[locationLocation] + '_' +
                                         df_MSL3Frozen[subLocationSubLocation] + '_' +
                                         df_MSL3Frozen[transModeTransMode])
    df_MSL3Frozen[activity2activity2] = df_MSL3Frozen[transModeTransMode]
    df_MSL3Frozen[activity3Activity3] = df_MSL3Frozen[itemMaterialItemMaterial]
    
    vdCommon.gfn_saveDf(df_MSL3Frozen, 'df_MSL3Frozen',False)
    
        
    # 칼럼정리
    df_MtrlBODFrozen = df_MtrlBODFrozen[cList_Out]
    df_MSL5Frozen = df_MSL5Frozen[cList_Out]
    df_MSL3Frozen = df_MSL3Frozen[cList_Out]
    
    # df_MtrlFense : concat : df_MtrlBODFrozen, df_MSL5Frozen, df_MSL3Frozen
    df_MtrlFense = pd.concat([df_MtrlBODFrozen, df_MSL5Frozen, df_MSL3Frozen])
    del [df_MtrlBODFrozen, df_MSL5Frozen, df_MSL3Frozen]
    
    vdCommon.gfn_saveDf(df_MtrlFense, 'df_MtrlFense',False)
    
    vdCommon.gfn_stepLog('=====> STEP 6-2 : 자재 Fence Create End')
    
    ################################################################################################################
    # STEP 7 : 001.009W Solver Inputs Frozen Window : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 7 : Final output table create')
    
    # out Data 생성 : : df_BOMFense & df_BODFense & df_MtrlFense 통합
    df_out_FrozenWindow = pd.concat([df_BOMFense, df_BODFense, df_MtrlFense])
    del [df_BOMFense, df_BODFense, df_MtrlFense]
    
    # 버전 처리
    #df_out_FrozenWindow[versionVersionName] = paramOutVersion    

    row_count, col_count = df_out_FrozenWindow.shape
    note(f'=====> Final df_out_FrozenWindow rows : {row_count}, column : {col_count}')
    
    vdCommon.gfn_saveDf(df_out_FrozenWindow, 'df_out_FrozenWindow',False)
    vdCommon.gfn_stepLog('=====> STEP 7-1 : Final output table create End')
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_FrozenWindow, 'df_out_FrozenWindow')
    
    vdCommon.gfn_stepLog('=====> STEP 7-2 : End')
    
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_FrozenWindow = pd.DataFrame([], columns=[])
    
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