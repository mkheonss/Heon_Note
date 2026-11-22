"""
* 프로그램명 
    - PY_UI_BOMVersionMgmt

* 내용
    - BOM Version Management UI 초기 값 데이타 구성 

* 변경이력
- 2024.08.30 / 양희영 / Create
- 2025.06.30 / 양희영 / Update

* Flow Summary
    STEP1~4. BOM Version Prty W 초기 구성값 구성 
           > BOM SET Item, Version 기준 자재별 세부 우선순위 선정  
    STEP5~6. Mtrl Usage, Mtrl Usage Prty W 초기 구성값 구성
            > 자재기준 상이자재 우선순위 지정  
              UI 에서는 자재 기준으로 관리하여 세부우선순위설정으로 Override 한다고함..

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_fullbom : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * 
                      [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, 
                      ({Measure.[Full BOM_Acil Date], Measure.[Full BOM_Avail Qty], Measure.[Full BOM_BOM Date], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_Consume Qty], 
                      Measure.[Full BOM_Consume UOM], Measure.[Full BOM_Creation Time], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Flag], 
                      Measure.[Full BOM_HQ Dev Purchaser], Measure.[Full BOM_HQ Purchaser], Measure.[Full BOM_Issue Date], Measure.[Full BOM_MRP Controller], Measure.[Full BOM_Part Eff Enddate], 
                      Measure.[Full BOM_Part Eff Startdate], Measure.[Full BOM_Prty], Measure.[Full BOM_Purchaser], Measure.[Full BOM_SOP SET Qty], Measure.[Full BOM_SOP Version Qty], Measure.[Full BOM_SRA Date], 
                      Measure.[Full BOM_Safety Date], Measure.[Full BOM_Unit], Measure.[Full BOM_Update Time], Measure.[Full BOM_Valid]}) on column;
    - df_in_LCMItem : Select ( [Item].[Item] * [Item].[Item Stage].filter(#.Name == "LCM"));
    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
                          ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) 
                          on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_Keyitem : // 250310 임재민 수정 / 대상자재 변경
                      select ([Item Material].[Const Type].[Soft].relatedmembers([Item Material]).unionwith(&NSUIMtrlMSL3View.filter(#.Name contains"Panel").relatedmembers([Item Material])));
    - df_in_PlanningHorizon : Select (&PlanningHorizon * [Time].[Day]) on row, () on column include memberproperties{[Time].[Week], Key,  [W Solver Start Bucket], [W Solver End Bucket]};
    - df_in_BOMVersionPrtyW : Select ([Version].[Version Name] * [Item].[Item] * &PlanningHorizon * [Location].[Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Item Component].[Item Component] ) on row, 
                              ({Measure.[BOM Version Prty W_Alert], Measure.[BOM Version Prty W_Horizon Ancestor], Measure.[BOM Version Prty W_Horizon Asn], Measure.[BOM Version Prty W_Horizon Fix], Measure.[BOM Version Prty W_OC], Measure.[BOM Version Prty W_Prty]}) 
                              on column.filter( Measure.[BOM Version Prty W_Prty] == "X" || Measure.[BOM Version Prty W_Prty] == "999" || Measure.[BOM Version Prty W_Prty] == "1");
    - df_in_BOM Version : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Item Component].[Item Component] ) on row, 
                          ({Measure.[BOM Version_Comment], Measure.[BOM Version_Fix Flag], Measure.[BOM Version_Prty]} ) on column;
    - df_in_MtrlUsagePrtyW : Select ([Version].[Version Name] * &PlanningHorizon * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Usage Prty W_Prty]}) on column;

* Output Tables
    - df_out_BOMVersion : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Item Component].[Item Component] ) on row, 
                           ({Measure.[BOM Version_Comment], Measure.[BOM Version_Fix Flag], Measure.[BOM Version_Prty]}) on column;
    - df_out_BOMVersionPrtyW : Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Item Component].[Item Component]) on row, 
                               ({Measure.[BOM Version Prty W_Alert], Measure.[BOM Version Prty W_Horizon Ancestor], Measure.[BOM Version Prty W_Horizon Asn], Measure.[BOM Version Prty W_Horizon Fix], Measure.[BOM Version Prty W_OC], 
                                 Measure.[BOM Version Prty W_Prty]}) on column;
    - df_out_MtrlUsage : Select ([Version].[Version Name] * [Location].[Location] *  [Item Material].[Item Material] ) on row, 
                          ({Measure.[Mtrl Usage_Comment], Measure.[Mtrl Usage_Model Cnt], Measure.[Mtrl Usage_Update Time], Measure.[Mtrl Usage_Updated By]}) on column;
    - df_out_MtrlUsagePrtyW : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material] ) on row, 
                              ({Measure.[Mtrl Usage Prty W_Prty]}) on column;
    - df_out_MtrlMapSET : Mtrl Map SET
                          Select ([Item].[Item] * [Version].[Version Name] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Map SET_Asn]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_BOMVersionMgmt] for measures {[BOM Version Prty W_Prty]} using scope (&MPV * &PlanningHorizon) 
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};

      
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
from datetime import datetime

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BOMVersionMgmt'
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

def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

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
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName         = 'Version.[Version Name]'
    timeWeek                   = 'Time.[Week]'
    locationLocation           = 'Location.[Location]'
    itemItem                   = 'Item.[Item]'
    itemMaterialItemMaterial   = 'Item Material.[Item Material]'
    bOMInfoBOMVersion          = 'BOM Info.[BOM Version]'
    itemComponentItemComponent = 'Item Component.[Item Component]'
    
    bOMVersionPrtyW_Prty  = 'BOM Version Prty W_Prty' #String
    bOMVersion_Prty       = 'BOM Version_Prty'     # Integer
    bOMVersion_FixFlag    = 'BOM Version_Fix Flag' # String
    mtrlUsage_ModelCnt    = 'Mtrl Usage_Model Cnt' # Integer
    mtrlUsagePrtyW_Prty   = 'Mtrl Usage Prty W_Prty' #String
    bOMDiffMgmtW_Priority = 'BOM Diff Mgmt W_Priority' #String
    
    bOMVersionPrtyW_HorizonAsn = 'BOM Version Prty W_Horizon Asn' #Integer
    mtrlMapSET_Asn             = 'Mtrl Map SET_Asn' #Integer
    
    keymaterial           = 'key material'
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
        
        df_in_fullbom         = read_csv_file("df_in_fullbom")
        df_in_LCMItem         = read_csv_file("df_in_LCMItem")
        df_in_ItemSiteAsn     = read_csv_file("df_in_ItemSiteAsn")
        df_in_Keyitem         = read_csv_file("df_in_Keyitem")
        df_in_PlanningHorizon = read_csv_file("df_in_PlanningHorizon")
        df_in_BOMVersion      = read_csv_file("df_in_BOMVersion")
        df_in_BOMVersionPrtyW = read_csv_file("df_in_BOMVersionPrtyW")
        df_in_MtrlUsagePrtyW = read_csv_file("df_in_MtrlUsagePrtyW")
        
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    df_in_BOMVersion = df_in_BOMVersion.astype({bOMVersion_FixFlag: 'str'}, copy=True)
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_fullbom, 'df_in_fullbom', False) 
    vdCommon.gfn_saveDf(df_in_LCMItem, 'df_in_LCMItem', False)
    vdCommon.gfn_saveDf(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn', False)
    vdCommon.gfn_saveDf(df_in_Keyitem, 'df_in_Keyitem', False)
    vdCommon.gfn_saveDf(df_in_PlanningHorizon, 'df_in_PlanningHorizon', False)
    vdCommon.gfn_saveDf(df_in_BOMVersionPrtyW, 'df_in_BOMVersionPrtyW', False)
    vdCommon.gfn_saveDf(df_in_BOMVersion, 'df_in_BOMVersion', False)
    vdCommon.gfn_saveDf(df_in_MtrlUsagePrtyW, 'df_in_MtrlUsagePrtyW', False)
    #vdCommon.gfn_stepLog('=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : df_SETLCMSet 구성 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 : df_SETLCMSet create')
    # STEP 1-1
    df_itemLocation = df_in_ItemSiteAsn[[versionVersionName, locationLocation, itemItem]].copy(deep=True)
    del df_in_ItemSiteAsn
    
    df_SETLCMSet = df_in_fullbom.merge(df_itemLocation, on=[versionVersionName,locationLocation,itemItem], how='inner')
    df_SETLCMSet = df_SETLCMSet.loc[df_SETLCMSet[bOMInfoBOMVersion].notna() & 
                                    (df_SETLCMSet[bOMInfoBOMVersion] != 'NA')]
    
    df_in_LCMItem.rename(columns={itemItem:itemMaterialItemMaterial}, inplace=True)
    df_SETLCMSet = df_SETLCMSet.merge(df_in_LCMItem, on=[itemMaterialItemMaterial], how='inner')
    df_SETLCMSet = df_SETLCMSet.groupby([versionVersionName, locationLocation, itemItem, bOMInfoBOMVersion], 
                                        as_index=False)[itemMaterialItemMaterial].max().astype('str')
    
    vdCommon.gfn_saveDf(df_SETLCMSet, 'df_SETLCMSet', False)
    #vdCommon.gfn_stepLog('=====> STEP 1-1 : df_SETLCMSet create End')
    
    ################################################################################################################
    # STEP 2 : df_SETLCMKeyItem Set 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 : df_SETLCMKeyItem Set create')
    # Item, Location Filtering
    df_SETLCMKeyItem = df_in_fullbom.merge(df_itemLocation, on=[versionVersionName, itemItem, locationLocation], 
                                           how='inner')
    del [df_in_fullbom, df_itemLocation]
    
    #df_in_Keyitem Merge : a.item material = c.item material 
    df_SETLCMKeyItem = df_SETLCMKeyItem.merge(df_in_Keyitem, on=[itemMaterialItemMaterial], how='inner')
    df_SETLCMKeyItem[keymaterial] = df_SETLCMKeyItem[itemMaterialItemMaterial]
    del df_in_Keyitem
    
    df_SETLCMSet.rename(columns={itemMaterialItemMaterial:itemComponentItemComponent}, inplace=True)
    # df_SETLCMSet Merge : a.location = d.location,  a.item = d.item, a.bom version = d.bom version
    df_SETLCMKeyItem = df_SETLCMKeyItem.merge(df_SETLCMSet, on=[versionVersionName, locationLocation, itemItem, 
                                                                bOMInfoBOMVersion], how='inner')
    del df_SETLCMSet
    
    df_SETLCMKeyItem = df_SETLCMKeyItem[[versionVersionName, locationLocation, itemItem, bOMInfoBOMVersion, 
                                         itemMaterialItemMaterial, itemComponentItemComponent, keymaterial]]
    
    vdCommon.gfn_saveDf(df_SETLCMKeyItem, 'df_SETLCMKeyItem', False)
    #vdCommon.gfn_stepLog('=====> STEP 2-1 : df_SETLCMKeyItem Set create End')
    
    ################################################################################################################
    # STEP 3 :  MG : BOM Version 구성 (df_SETLCMKeyItem  기준으로 df_in_BOMVersion 에 없는)
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 3 : BOM Version create')
    df_in_BOMVersion['col_chk'] = 'x'
    df_SETLCMKeyItem_BOM = df_SETLCMKeyItem.merge(df_in_BOMVersion, 
                                                  on=[versionVersionName, locationLocation, itemItem, bOMInfoBOMVersion, 
                                                      itemComponentItemComponent, itemMaterialItemMaterial], how='left')
    del df_in_BOMVersion
    
    #mereg 결과 df_in_BOMVersion 에 없는(not exsits) data
    #df_SETLCMKeyItem_BOM = df_SETLCMKeyItem_BOM.loc[df_SETLCMKeyItem_BOM[bOMVersion_Prty].isna()].copy()
    df_SETLCMKeyItem_BOM = df_SETLCMKeyItem_BOM.loc[df_SETLCMKeyItem_BOM['col_chk'].isna()].copy()
    df_SETLCMKeyItem_BOM[bOMVersion_Prty] = 1
    # (250216)임재민 변경요청 : BOM Version_Fix Flag 에 "N" 고정값 추가(기존값은 유지)
    df_SETLCMKeyItem_BOM[bOMVersion_FixFlag] = 'N'
    
    vdCommon.gfn_saveDf(df_SETLCMKeyItem_BOM, 'df_SETLCMKeyItem_BOM', False)
    #vdCommon.gfn_stepLog('=====> STEP 3-1 : BOM Version create End')
    
    ################################################################################################################
    # STEP 4 : MG : BOM Version Prty W 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 4 : BOM Version Prty W create')
    df_PlanningHorizon = df_in_PlanningHorizon[[timeWeek]].copy()
    df_PlanningHorizon.drop_duplicates(inplace=True)
    del df_in_PlanningHorizon
    
    df_PlanningHorizon['key'] = 'x'
    df_SETLCMKeyItem['key'] = 'x'
    
    df_BOMVersionPrtyW = df_SETLCMKeyItem.merge(df_PlanningHorizon, on=['key'], how='inner')
    df_BOMVersionPrtyW.drop(columns=['key'], inplace=True)
    
    #vdCommon.gfn_saveDf(df_BOMVersionPrtyW, 'df_BOMVersionPrtyW', False)
    
    df_BOMVersionPrtyW_FinalSet = df_BOMVersionPrtyW.merge(df_in_BOMVersionPrtyW, 
                                                           on=[versionVersionName, itemItem, locationLocation, 
                                                               bOMInfoBOMVersion, itemComponentItemComponent, 
                                                               itemMaterialItemMaterial, timeWeek], how='left')
    del df_BOMVersionPrtyW; del df_in_BOMVersionPrtyW
    
    # BOM Version Prty W_Prty(+) is null 
    df_BOMVersionPrtyW_FinalSet = df_BOMVersionPrtyW_FinalSet[df_BOMVersionPrtyW_FinalSet[bOMVersionPrtyW_Prty].isna()]
    df_BOMVersionPrtyW_FinalSet[bOMVersionPrtyW_Prty] = '1'
    # 250208 jm 추가
    #(250216)임재민 변경 요청 : 
    df_BOMVersionPrtyW_FinalSet[bOMVersionPrtyW_HorizonAsn] = 1
    
    vdCommon.gfn_saveDf(df_BOMVersionPrtyW_FinalSet, 'df_BOMVersionPrtyW_FinalSet', False)
    #vdCommon.gfn_stepLog('=====> STEP 4-1 : BOM Version Prty W create End')
    
    ################################################################################################################
    # STEP 5 : MG : Mtrl Usage 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 5 : Mtrl Usage create')
    df_MtrlUsage = df_SETLCMKeyItem.groupby([versionVersionName, locationLocation, itemMaterialItemMaterial], 
                                            as_index=False)[itemItem].nunique() #count(distinct)
    df_MtrlUsage.rename(columns={itemItem:mtrlUsage_ModelCnt}, inplace=True)
        
    vdCommon.gfn_saveDf(df_MtrlUsage, 'df_MtrlUsage', False)
    #vdCommon.gfn_stepLog('=====> STEP 5-1 : Mtrl Usage create End')
    
    ################################################################################################################
    # STEP 6 : MG : Mtrl Usage Prty W 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 6 : trl Usage Prty create')
    df_MtrlUsagePrtyW = df_SETLCMKeyItem.merge(df_PlanningHorizon, on=['key'], how='inner')
    del df_SETLCMKeyItem; del df_PlanningHorizon
    
    df_MtrlUsagePrtyW = df_MtrlUsagePrtyW[[versionVersionName,locationLocation,itemMaterialItemMaterial,timeWeek]].copy()
    df_MtrlUsagePrtyW.drop_duplicates(inplace=True)
    
    df_MtrlUsagePrtyW = df_MtrlUsagePrtyW.merge(df_in_MtrlUsagePrtyW, on=[versionVersionName, locationLocation,
                                                                          itemMaterialItemMaterial, timeWeek], how='left')
    del df_in_MtrlUsagePrtyW
    
    # mtrl usage prty w prty(+)  is null
    df_MtrlUsagePrtyW = df_MtrlUsagePrtyW.loc[df_MtrlUsagePrtyW[mtrlUsagePrtyW_Prty].isna()].copy()
    df_MtrlUsagePrtyW[mtrlUsagePrtyW_Prty]  = '1'
    df_MtrlUsagePrtyW[bOMDiffMgmtW_Priority] = '1'
    
    vdCommon.gfn_saveDf(df_MtrlUsagePrtyW, 'df_MtrlUsagePrtyW', False)
    #vdCommon.gfn_stepLog('=====> STEP 6-1 : trl Usage Prty create End')
    
    ################################################################################################################
    # STEP 9 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 9 : Final output table create')
    
    # out Data 생성    
    df_out_BOMVersion = df_SETLCMKeyItem_BOM[[versionVersionName, itemItem, locationLocation, itemMaterialItemMaterial, 
                                              bOMInfoBOMVersion, itemComponentItemComponent, bOMVersion_Prty,
                                              bOMVersion_FixFlag]].copy()
    del df_SETLCMKeyItem_BOM
    df_out_BOMVersion.drop_duplicates(inplace=True)
    
    df_out_BOMVersionPrtyW = df_BOMVersionPrtyW_FinalSet[[versionVersionName, itemItem, timeWeek, locationLocation, 
                                                          itemMaterialItemMaterial, bOMInfoBOMVersion, 
                                                          itemComponentItemComponent, bOMVersionPrtyW_Prty,
                                                          bOMVersionPrtyW_HorizonAsn]].copy()
    del df_BOMVersionPrtyW_FinalSet
    df_out_BOMVersionPrtyW.drop_duplicates(inplace=True)
    
    df_out_MtrlUsage = df_MtrlUsage[[versionVersionName, locationLocation, itemMaterialItemMaterial, 
                                     mtrlUsage_ModelCnt]].copy()
    del df_MtrlUsage
    df_out_MtrlUsage.drop_duplicates(inplace=True)
    
    df_out_MtrlUsagePrtyW = df_MtrlUsagePrtyW[[versionVersionName, timeWeek, locationLocation, itemMaterialItemMaterial,
                                               bOMDiffMgmtW_Priority, mtrlUsagePrtyW_Prty]].copy()
    del df_MtrlUsagePrtyW
    df_out_MtrlUsagePrtyW.drop_duplicates(inplace=True)
    
    #(250208)임재민 변경 요청 : output추가
    df_out_MtrlMapSET = df_out_BOMVersionPrtyW[[versionVersionName, itemItem, locationLocation, itemMaterialItemMaterial]].copy()
    df_out_MtrlMapSET.drop_duplicates(inplace=True)
    df_out_MtrlMapSET[mtrlMapSET_Asn] = 1
    # (250216)임재민 변경 요청 : distinct  "Version.[Version Name]", "Item.[Item]", "Location.[Location]", "Item Material.[Item Material]" 의후에 count
    # Measure.[Mtrl Map SET_Asn] 는 위의 count
    df_out_MtrlMapSET = df_out_MtrlMapSET.groupby([versionVersionName, itemItem, locationLocation, itemMaterialItemMaterial],
                                                   as_index=False).agg({mtrlMapSET_Asn: "count"})
    
    # 버전 처리 :
    #df_out_BOMVersion[versionVersionName]      = paramOutVersion
    #df_out_BOMVersionPrtyW[versionVersionName] = paramOutVersion
    #df_out_MtrlUsage[versionVersionName]       = paramOutVersion
    #df_out_MtrlUsagePrtyW[versionVersionName]  = paramOutVersion
    #df_out_MtrlMapSET[versionVersionName]      = paramOutVersion
    
    row_count, col_count = df_out_BOMVersion.shape
    note(f'=====> df_out_BOMVersion rows : {row_count}, column : {col_count}')
    
    row_count, col_count = df_out_BOMVersionPrtyW.shape
    note(f'=====> df_out_BOMVersionPrtyW rows : {row_count}, column : {col_count}')
    
    row_count, col_count = df_out_MtrlUsage.shape
    note(f'=====> df_out_MtrlUsage rows : {row_count}, column : {col_count}')
    
    row_count, col_count = df_out_MtrlUsagePrtyW.shape
    note(f'=====> df_out_MtrlUsagePrtyW rows : {row_count}, column : {col_count}')
    
    row_count, col_count = df_out_MtrlMapSET.shape
    note(f'=====> df_out_MtrlMapSET rows : {row_count}, column : {col_count}')
    
    vdCommon.gfn_saveDf(df_out_BOMVersion, 'df_out_BOMVersion', False)
    vdCommon.gfn_saveDf(df_out_BOMVersionPrtyW, 'df_out_BOMVersionPrtyW', False)
    vdCommon.gfn_saveDf(df_out_MtrlUsage, 'df_out_MtrlUsage', False)
    vdCommon.gfn_saveDf(df_out_MtrlUsagePrtyW, 'df_out_MtrlUsagePrtyW', False)
    vdCommon.gfn_saveDf(df_out_MtrlMapSET, 'df_out_MtrlMapSET', False)
    
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_BOMVersion, 'df_out_BOMVersion')
        save_csv_file(df_out_BOMVersionPrtyW, 'df_out_BOMVersionPrtyW')
        save_csv_file(df_out_MtrlUsage, 'df_out_MtrlUsage')
        save_csv_file(df_out_MtrlUsagePrtyW, 'df_out_MtrlUsagePrtyW')
        save_csv_file(df_out_MtrlMapSET, 'df_out_MtrlMapSET')
    
    vdCommon.gfn_stepLog('=====> STEP 9-1 : Final output table create End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_BOMVersion = pd.DataFrame([], columns=[])
    df_out_BOMVersionPrtyW = pd.DataFrame([], columns=[])
    df_out_MtrlUsage = pd.DataFrame([], columns=[])
    df_out_MtrlUsagePrtyW = pd.DataFrame([], columns=[])
    df_out_MtrlMapSET = pd.DataFrame([], columns=[])
    
finally:
    vdCommon.gfn_stepLog('plugin Execution End ')
    
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    
    #logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    #logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
            
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