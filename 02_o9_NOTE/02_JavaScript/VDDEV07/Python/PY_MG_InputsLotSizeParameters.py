"""
* 프로그램명 
    - PY_MG_InputsLotSizeParameters

* 내용
    - MP Engine 수행을 위한 BOM/BOD Activity 기준 Lotsize I/F
    - Plan 대상 Item Site Association (Measure Group : Item Site Asn) 에서 
      실제 현재 PLAN 대상에 대한 Item - Location Association 만 반영 

* 변경이력
    - 2024.06.25 / 양희영 / Create
    - 2025.06.27 / 양희영 / Update

* Inpu
- df_in_InputsLotSizeParameters = pd.read_csv(' .csv') 

* Flow Summary
    STEP1. Plan 대상 Item, Location(df_in_ItemSiteAsn) 정보 발췌
    STEP2. Plan 대상 BOD ITEM (ITEM별 BOD) Filtering
    STEP3. STEP2 에서 구성된 Set을 대상으로 df_out_InputsLotSize Measure 정보 Insert

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
                          ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) 
                          on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - 삭제(2024.08.16) : df_in_BOD : Select ([BOD].[BOD Name] * [BOD].[From Site ID] * [BOD].[To Site ID] * [BOD].[Transport Mode]) ;
    - df_in_BODList : Select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                      ({Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT],  Measure.[BOD List_BOD LT]}) on column;
    - df_in_BODItem : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                      ({Measure.[BOD Item_BOD Frozen],  Measure.[BOD Item_Multi Lot Qty], Measure.[BOD Item_Priority], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_BOD LT] })  on column;
    - df_in_BOMMaster : Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, 
                        ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column;
    - df_in_BODItemMtrlFull : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                              ({ Measure.[BOD Item Mtrl Full_Lot Size]}) on column;
    - 삭제(2024.09.30) : df_in_BOD_List_Mtrl : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                                   ({Measure.[BOD List Mtrl_EFF Enddate], Measure.[BOD List Mtrl_EFF Startdate]}) on column.filter((isnull(Measure.[BOD List Mtrl_EFF Enddate]) || Measure.[BOD List Mtrl_EFF Enddate] > Measure.[W Plan Start Date])
                                    && (isnull(Measure.[BOD List Mtrl_EFF Startdate]) || Measure.[BOD List Mtrl_EFF Startdate] < Measure.[W Plan End Date]));
    - 삭제(2024.09.30) : df_in_BOD_Item_mtrl : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]) on row, 
                                   ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lock Flag], Measure.[BOD Item Mtrl_Lot Size], Measure.[BOD Item Mtrl_Lot Type]}
                                   ) on column.filter((isnull(Measure.[BOD Item Mtrl_EFF Enddate]) || Measure.[BOD Item Mtrl_EFF Enddate] > Measure.[W Plan Start Date]) 
                                   && (isnull(Measure.[BOD Item Mtrl_EFF Startdate]) || Measure.[BOD Item Mtrl_EFF Startdate] < Measure.[W Plan End Date]));

* Output Tables
    - df_out_InputsLotSize : 001.010W Solver Inputs LotSize Parameters
                             Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, 
                             ({Measure.[W LotSize Increment], Measure.[W Max LotSize], Measure.[W Min LotSize], Measure.[W Soft LotSize]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_InputsLotSizeParameters] for Measures {[W LotSize Increment]} using scope (&MPV) 
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
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
import warnings
warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_InputsLotSizeParameters'
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
    vdCommon.gfn_stepLog('=====> Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_ItemSiteAsn     = read_csv_file("df_in_ItemSiteAsn")
        df_in_BODList         = read_csv_file("df_in_BODList")
        df_in_BODItem         = read_csv_file("df_in_BODItem")
        df_in_BOMMaster       = read_csv_file("df_in_BOMMaster")
        df_in_BODItemMtrlFull = read_csv_file("df_in_BODItemMtrlFull")
        #df_in_BOD_List_Mtrl = read_csv_file("df_in_BOD_List_Mtrl")
        #df_in_BOD_Item_mtrl = read_csv_file("df_in_BOD_Item_mtrl")
        
    #if df_in_ItemSiteAsn.empty:
    #    raise Exception("=====> raise Exception: df_in_ItemSiteAsn is empty")

    #if df_in_BODList.empty:
    #    raise Exception("=====> raise Exception: df_in_BODList is empty")

    #if df_in_BODItem.empty:
    #    raise Exception("=====> raise Exception: df_in_BODItem is empty")
    
    #if df_in_BOMMaster.empty:
    #    raise Exception("=====> raise Exception: df_in_BOMMaster is empty")
        
    #if df_in_BODItemMtrlFull.empty:
    #    raise Exception("=====> raise Exception: df_in_BODItemMtrlFull is empty")
    
    #if df_in_BOD_List_Mtrl.empty:
    #    raise Exception("=====> raise Exception: df_in_BOD_List_Mtrl is empty")

    #if df_in_BOD_Item_mtrl.empty:
    #    raise Exception("=====> raise Exception: df_in_BOD_Item_mtrl is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE

    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    vdCommon.gfn_saveDf(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',False)
    vdCommon.gfn_saveDf(df_in_BODList, 'df_in_BODList',False)
    vdCommon.gfn_saveDf(df_in_BODItem, 'df_in_BODItem',False)
    vdCommon.gfn_saveDf(df_in_BOMMaster, 'df_in_BOMMaster',False)
    vdCommon.gfn_saveDf(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull',False)
    #vdCommon.gfn_saveDf(df_in_BOD_List_Mtrl, 'df_in_BOD_List_Mtrl',False)
    #vdCommon.gfn_saveDf(df_in_BOD_Item_mtrl, 'df_in_BOD_Item_mtrl',False)
    
    vdCommon.gfn_stepLog('=====> Input table load End')
    ################################################################################################################
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> DataFrame Column : 변수 처리')

    # 컬럼 변수 선언
    versionVersionName       = 'Version.[Version Name]'
    itemItem                 = 'Item.[Item]'
    bodBodName               = 'BOD.[BOD Name]'
    locationLocation         = "Location.[Location]"
    subLocationSubLocation   = "Sub Location.[Sub Location]"
    transModeTransMode       = "Trans Mode.[Trans Mode]"
    activity1activity1       = "Activity1.[Activity1]"
    activity2activity2       = "Activity2.[Activity2]"
    activity3Activity3       = "Activity3.[Activity3]"
    itemMaterialItemMaterial = 'Item Material.[Item Material]'
    
    bODItem_MultiLotQty     = "BOD Item_Multi Lot Qty"
    bODItemMtrl_LotSize     = 'BOD Item Mtrl_Lot Size'
    bODItemMtrlFull_LotSize = 'BOD Item Mtrl Full_Lot Size'
    
    bOMInfoBOMID   = 'BOM Info.[BOM ID]'
    bOMMasterBOMID = 'BOM Master_BOM ID'
    
    wLotSizeIncrement = 'W LotSize Increment'
    wMaxLotSize       = 'W Max LotSize'
    wMinLotSize       = 'W Min LotSize'
    wSoftLotSize      = 'W Soft LotSize'
    
    ################################################################################################################
    # STEP 1 :  데이터 선 가공, Item, Location 정보 df 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 : input data machining')
    # STEP1-1 : Plan 대상 Item, Location(df_in_ItemSiteAsn) 정보 발췌, Item, Location 정보 df 구성
    #-df_in_ItemSiteAsn distinct 필요없음, Version Name, Itme, Location
    # column 정리
    df_in_ItemSiteAsn = df_in_ItemSiteAsn[[versionVersionName, itemItem, locationLocation]]
    #vdCommon.gfn_saveDf(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn column adjust',False)
    
    #STEP1-2-distinct item
    Item_series = df_in_ItemSiteAsn[itemItem].unique()
    
    #STEP1-3 -distinct location
    Location_series = df_in_ItemSiteAsn[locationLocation].unique()

    vdCommon.gfn_stepLog('=====> STEP1-1 : input data machining End')
    ################################################################################################################
    # STEP 2 : BOD data Filtering
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 : BOD data Filtering')
    
    # Item Filtering: df_in_BODItem & Item_series (Item 기준)
    df_in_BODItem = df_in_BODItem[df_in_BODItem[itemItem].isin(Item_series)]
    vdCommon.gfn_saveDf(df_in_BODItem, 'df_in_BODItem Item Filtering',False)
    
    # Location Filtering
    df_in_BODItem = df_in_BODItem[(df_in_BODItem[locationLocation].isin(Location_series)) | (df_in_BODItem[subLocationSubLocation].isin(Location_series))]
    vdCommon.gfn_saveDf(df_in_BODItem, 'df_in_BODItem Location Filtering',False)
    
    vdCommon.gfn_stepLog('=====> STEP 2-1 : BOD data Filtering End')
    
    ################################################################################################################
    # STEP 3 : df_BOD Measure 정보 생성 (STEP2의 결과 df로 생성)
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 3 : BOD data Create')
    
    # df_in_BODItem  & df_in_BODLane  Merge
    df_BOD = df_in_BODItem.merge(df_in_BODList,on=[versionVersionName, locationLocation, subLocationSubLocation, transModeTransMode], how='inner')
    vdCommon.gfn_saveDf(df_BOD, 'df_BOD Merge',False)
    
    # activity1 (BOD Name)
    df_BOD[activity1activity1] = df_BOD[locationLocation] + '_' + df_BOD[subLocationSubLocation] + '_' + df_BOD[transModeTransMode]
    df_BOD = df_BOD[[versionVersionName, itemItem, activity1activity1, locationLocation, subLocationSubLocation, transModeTransMode, bODItem_MultiLotQty]]
    #vdCommon.gfn_saveDf(df_BOD, 'df_BOD',False)
    del df_in_BODItem
    del df_in_BODList
    
    # BOD column 값 설정
    df_BOD[wLotSizeIncrement]  = df_BOD[bODItem_MultiLotQty]
    df_BOD[wMinLotSize]        = df_BOD[bODItem_MultiLotQty]
    df_BOD[wMaxLotSize]        = np.nan
    df_BOD[wSoftLotSize]       = np.nan
    df_BOD[activity2activity2] = df_BOD[transModeTransMode]
    df_BOD[activity3Activity3] = df_BOD[itemItem]

    # BOD Data column 설정
    df_BOD = df_BOD[[versionVersionName, itemItem, locationLocation, activity1activity1, activity2activity2, activity3Activity3,
                     wLotSizeIncrement, wMaxLotSize, wMinLotSize, wSoftLotSize]]
    vdCommon.gfn_saveDf(df_BOD, 'df_BOD',False)
    vdCommon.gfn_stepLog('=====> STEP 3-1 : df_BOD Create End')
    
    ################################################################################################################
    # STEP 4 : df_BOD Mtrl Measure 정보 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 4 : BOD Mtrl data Create')
    
    df_in_BODItemMtrlFull.rename(columns={itemMaterialItemMaterial:itemItem}, inplace=True)    

    # Item Filtering: df_in_BODItemMtrlFull & Item_series (Item 기준)
    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[df_in_BODItemMtrlFull[itemItem].isin(Item_series)]
    vdCommon.gfn_saveDf(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull Item Filtering',False)
    
    # Location Filtering
    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[(df_in_BODItemMtrlFull[locationLocation].isin(Location_series)) | (df_in_BODItemMtrlFull[subLocationSubLocation].isin(Location_series))]
    vdCommon.gfn_saveDf(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull Location Filtering',False)
    
    # df_BOD_Mtrl 생성
    df_BOD_Mtrl = df_in_BODItemMtrlFull.copy()
    del df_in_BODItemMtrlFull
    
    # BOD Mtrl column 값 설정
    df_BOD_Mtrl[wLotSizeIncrement] = df_BOD_Mtrl[bODItemMtrlFull_LotSize]
    df_BOD_Mtrl[wMinLotSize] = np.nan
    df_BOD_Mtrl[wMaxLotSize] = np.nan
    df_BOD_Mtrl[wSoftLotSize] = np.nan
    df_BOD_Mtrl[activity1activity1] = df_BOD_Mtrl[locationLocation] + '_' + df_BOD_Mtrl[subLocationSubLocation] + '_' + df_BOD_Mtrl[transModeTransMode]
    df_BOD_Mtrl[activity2activity2] = df_BOD_Mtrl[transModeTransMode]
    df_BOD_Mtrl[activity3Activity3] = df_BOD_Mtrl[itemItem]
    
    # BOD Mtrl Data column 정리
    df_BOD_Mtrl = df_BOD_Mtrl[[versionVersionName, itemItem, locationLocation, activity1activity1, activity2activity2, activity3Activity3,
                               wLotSizeIncrement, wMaxLotSize, wMinLotSize, wSoftLotSize]]
    
    vdCommon.gfn_saveDf(df_BOD_Mtrl, 'df_BOD_Mtrl',False)
    
    vdCommon.gfn_stepLog('=====> STEP 4-1 : BOD Mtrl data Create End')
    ################################################################################################################
    # STEP 5 : df_BOM Measure 정보 생성 : df_in_BOMMaster & df_in_ItemSiteAsn 통합
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 5 : BOM data Create')
    
    df_BOM = df_in_BOMMaster.merge(df_in_ItemSiteAsn,
                                   left_on=[versionVersionName, bOMMasterBOMID, locationLocation],
                                   right_on=[versionVersionName, itemItem, locationLocation], how='inner')
    
    # BOM column 값 설정
    df_BOM[wLotSizeIncrement]  = 1
    df_BOM[wMinLotSize]        = np.nan
    df_BOM[wMaxLotSize]        = np.nan
    df_BOM[wSoftLotSize]       = np.nan
    df_BOM[activity1activity1] = df_BOM[bOMInfoBOMID]
    df_BOM[activity2activity2] = 'RT_' + df_BOM[bOMInfoBOMID] + '@' + df_BOM[locationLocation]
    df_BOM[activity3Activity3] = df_BOM[bOMMasterBOMID]
    
    # BOM Data 설정
    df_BOM = df_BOM[[versionVersionName, itemItem, locationLocation, activity1activity1, activity2activity2, activity3Activity3,
                     wLotSizeIncrement, wMaxLotSize, wMinLotSize, wSoftLotSize]]
    
    vdCommon.gfn_saveDf(df_BOM, 'df_BOM',False)
    vdCommon.gfn_stepLog('=====> STEP 5-1 : df_BOM Create End')
    del df_in_BOMMaster
    del df_in_ItemSiteAsn
    
    ################################################################################################################
    # STEP 6 : 001.010W Solver Inputs LotSize Parameters : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 6 : Final output table create')
    
    # out Data 생성 : : df_BOD & df_BOM 통합
    df_out_InputsLotSize = pd.concat([df_BOD, df_BOD_Mtrl, df_BOM])
    del df_BOD
    del df_BOD_Mtrl
    del df_BOM
    
    # 버전 처리
    #df_out_InputsLotSize[versionVersionName] = paramOutVersion
    
    vdCommon.gfn_saveDf(df_out_InputsLotSize, 'df_out_InputsLotSize',False)
    vdCommon.gfn_stepLog('=====> STEP 6-1 : Output table 생성 End')
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_InputsLotSize, 'df_out_InputsLotSize') 
        
    row_count, col_count = df_out_InputsLotSize.shape
    note(f'=====> Final df_out_InputsLotSize rows : {row_count}, column : {col_count}')
    vdCommon.gfn_stepLog('=====> STEP 6-2 End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_InputsLotSize = pd.DataFrame([], columns=[])

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