"""
* 프로그램명 
    - PY_UI_BOMVersionMgmt

* 내용
    - BOM Version Management UI 초기 값 데이타 구성 

* 변경이력
- 2024.08.30 / 양희영 / Create
- 2026.04.09 / 양희영 / Update

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
    - df_in_fullbom : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * 
                      [Status].[Status] * [BOM Type].[BOM Type].filter(#.Name in {"SET","SOP Assy"}) * [BOM Status].[BOM Status].filter(#.Name != "MPI_L") ) on row, 
                      ({Measure.[Full BOM_Acil Date], Measure.[Full BOM_Avail Qty], Measure.[Full BOM_BOM Date], Measure.[Full BOM_BOM Level], Measure.[Full BOM_Base Qty], Measure.[Full BOM_Consume Qty], 
                      Measure.[Full BOM_Consume UOM], Measure.[Full BOM_Creation Time], Measure.[Full BOM_EOP Date], Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Flag], 
                      Measure.[Full BOM_HQ Dev Purchaser], Measure.[Full BOM_HQ Purchaser], Measure.[Full BOM_Issue Date], Measure.[Full BOM_MRP Controller], Measure.[Full BOM_Part Eff Enddate], 
                      Measure.[Full BOM_Part Eff Startdate], Measure.[Full BOM_Prty], Measure.[Full BOM_Purchaser], Measure.[Full BOM_SOP SET Qty], Measure.[Full BOM_SOP Version Qty], Measure.[Full BOM_SRA Date], 
                      Measure.[Full BOM_Safety Date], Measure.[Full BOM_Unit], Measure.[Full BOM_Update Time], Measure.[Full BOM_Valid]}) on column;
    - 사용안함. df_in_LCMItem : Select ( [Item].[Item] * [Item].[Item Stage].filter(#.Name == "LCM"));
    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
                          ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) 
                          on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_Keyitem : //(260402)박상현 쿼리 변경 요청
                      select ([Item].[Const Type].filter(#.Name in {"Soft","Hard"}).relatedmembers([Item]));
    - df_in_PlanningHorizon : Select (&PlanningHorizon * [Time].[Day]) on row, () on column include memberproperties{[Time].[Week], Key,  [W Solver Start Bucket], [W Solver End Bucket]};
    - df_in_BOMVersionPrtyW : Select ([Version].[Version Name] * [Item].[Item] * &PlanningHorizon * [Location].[Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Item Component].[Item Component] ) on row, 
                              ({Measure.[BOM Version Prty W_Alert], Measure.[BOM Version Prty W_Horizon Ancestor], Measure.[BOM Version Prty W_Horizon Asn], Measure.[BOM Version Prty W_Horizon Fix], Measure.[BOM Version Prty W_OC], Measure.[BOM Version Prty W_Prty]}) 
                              on column.filter( Measure.[BOM Version Prty W_Prty] == "X" || Measure.[BOM Version Prty W_Prty] == "999" || Measure.[BOM Version Prty W_Prty] == "1");
    - df_in_BOMVersion : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Item Component].[Item Component] ) on row, 
                          ({Measure.[BOM Version_Comment], Measure.[BOM Version_Fix Flag], Measure.[BOM Version_Prty]} ) on column;
    - df_in_MtrlUsagePrtyW : Select ([Version].[Version Name] * &PlanningHorizon * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Usage Prty W_Prty]}) on column;
    - df_in_ItemMaterial : select ([Item].[Item] * [Item].[Const Type].filter(#.Name in {"Hard","Soft"}));
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
    EXEC plugin instance [PY_UI_BOMVersionMgmt] for measures {[BOM Version Prty W_Prty]} using scope (&MPV) 
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
str_instance = 'PY_UI_BOMVersionMgmt'
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
    timeWeek                   = 'Time.[Week]'
    locationLocation           = 'Location.[Location]'
    itemItem                   = 'Item.[Item]'
    toItemToItem               = 'To Item.[To Item]'
    itemMaterialItemMaterial   = 'Item Material.[Item Material]'
    bOMInfoBOMVersion          = 'BOM Info.[BOM Version]'
    itemComponentItemComponent = 'Item Component.[Item Component]'
    bOMTypeBOMType             = 'BOM Type.[BOM Type]'
    
    bOMVersionPrtyW_Prty  = 'BOM Version Prty W_Prty' #String
    
    bOMVersion_Prty       = 'BOM Version_Prty'     # Integer
    bOMVersion_FixFlag    = 'BOM Version_Fix Flag' # String
    bOMVersion_UpdateTime = 'BOM Version_Update Time' #Datetime
    bOMVersion_UpdatedBy  = 'BOM Version_Updated By'  # String
    
    mtrlUsage_ModelCnt    = 'Mtrl Usage_Model Cnt' # Integer
    mtrlUsagePrtyW_Prty   = 'Mtrl Usage Prty W_Prty' #String
    bOMDiffMgmtW_Priority = 'BOM Diff Mgmt W_Priority' #String
    
    bOMVersionPrtyW_HorizonAsn = 'BOM Version Prty W_Horizon Asn' #Integer
    mtrlMapSET_Asn             = 'Mtrl Map SET_Asn' #Integer
    
    keymaterial           = 'key material'
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
        
        df_in_fullbom         = read_csv_file("df_in_fullbom")
        #df_in_LCMItem         = read_csv_file("df_in_LCMItem")
        df_in_ItemSiteAsn     = read_csv_file("df_in_ItemSiteAsn")
        df_in_Keyitem         = read_csv_file("df_in_Keyitem")
        df_in_PlanningHorizon = read_csv_file("df_in_PlanningHorizon")
        df_in_BOMVersion      = read_csv_file("df_in_BOMVersion")
        df_in_BOMVersionPrtyW = read_csv_file("df_in_BOMVersionPrtyW")
        df_in_MtrlUsagePrtyW = read_csv_file("df_in_MtrlUsagePrtyW")
        df_in_ItemMaterial   = read_csv_file("df_in_ItemMaterial")
        
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    df_in_BOMVersion = df_in_BOMVersion.astype({bOMVersion_FixFlag: 'str'}, copy=True)
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    print_df(df_in_fullbom, 'df_in_fullbom', False) 
    #print_df(df_in_LCMItem, 'df_in_LCMItem', False)
    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn', False)
    print_df(df_in_Keyitem, 'df_in_Keyitem', False)
    print_df(df_in_PlanningHorizon, 'df_in_PlanningHorizon', False)
    print_df(df_in_BOMVersionPrtyW, 'df_in_BOMVersionPrtyW', False)
    print_df(df_in_BOMVersion, 'df_in_BOMVersion', False)
    print_df(df_in_MtrlUsagePrtyW, 'df_in_MtrlUsagePrtyW', False)
    print_df(df_in_ItemMaterial, 'df_in_ItemMaterial', False)
    #step('=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : df_SETLCMSet 구성 
    ################################################################################################################
    step('=====> STEP 1 : df_SETLCMSet create')
    # STEP 1-1
    df_itemLocation = df_in_ItemSiteAsn[[versionVersionName, locationLocation, itemItem]].copy(deep=True)
    del df_in_ItemSiteAsn
    #print_df(df_itemLocation, 'df_itemLocation', True)
    
    #df_in_fullbom Filtering
    df_in_fullbom = df_in_fullbom[df_in_fullbom.set_index([itemMaterialItemMaterial]).index.isin(
                                     df_in_ItemMaterial.set_index([itemItem]).index)].copy()
    print_df(df_in_fullbom, 'df_in_fullbom Filtering', False)
    
    df_SETLCMSet = df_in_fullbom.merge(df_itemLocation, on=[versionVersionName,locationLocation,itemItem], how='inner')
    #print_df(df_SETLCMSet, 'df_SETLCMSet-1', True)
    df_SETLCMSet = df_SETLCMSet.loc[df_SETLCMSet[bOMInfoBOMVersion].notna() & 
                                    (df_SETLCMSet[bOMInfoBOMVersion] != 'NA')]
    
    #2026.04.07 : df_in_LCMItem 확인 방법 변경. (박상현 프로 요청)
    # BOM Type = SOP Assy이면 -> 기존대로
    # BOM Type = SET 이면 -> Item Component = 대쉬(-)
    
    #df_in_LCMItem.rename(columns={itemItem:itemMaterialItemMaterial}, inplace=True)
    #df_SETLCMSet = df_SETLCMSet.merge(df_in_LCMItem, on=[itemMaterialItemMaterial], how='inner')
    
    # ItemComponent : ItemMaterial 활용에서 To Item.[To Item] 활용으로 변경, 2026.04.08
    # group by 없이 그대로 사용으로 변경, 2026.04.08
    df_SETLCMSet[itemComponentItemComponent] = np.where(df_SETLCMSet[bOMTypeBOMType] == "SOP Assy",
                                                        df_SETLCMSet[toItemToItem], "-")
    
    '''
    df_SETLCMSet_Assy = df_SETLCMSet[df_SETLCMSet[bOMTypeBOMType] == "SOP Assy"].copy()
    df_SETLCMSet_Assy[itemComponentItemComponent] = df_SETLCMSet_Assy[toItemToItem]
    
    df_SETLCMSet_SET  = df_SETLCMSet[df_SETLCMSet[bOMTypeBOMType] == "SET"].copy()
    df_SETLCMSet_SET[itemComponentItemComponent] = '-'
    del df_SETLCMSet
    
    #group by
    cList_grp = [versionVersionName, locationLocation, itemItem, bOMInfoBOMVersion]
    
    # ItemComponent ItemMaterial 을 To Item.[To Item] 활용으로 변경
    #df_SETLCMSet_Assy = df_SETLCMSet_Assy.groupby(cList_grp, as_index=False)[itemMaterialItemMaterial].max().astype('str')
    #df_SETLCMSet_SET  = df_SETLCMSet_SET.groupby(cList_grp, as_index=False)[itemMaterialItemMaterial].max().astype('str')
    df_SETLCMSet_Assy = df_SETLCMSet_Assy.groupby(cList_grp, as_index=False)[itemComponentItemComponent].max().astype('str')
    df_SETLCMSet_SET  = df_SETLCMSet_SET.groupby(cList_grp, as_index=False)[itemComponentItemComponent].max().astype('str')
    
    #print_df(df_SETLCMSet_Assy, 'df_SETLCMSet_Assy 1', True)
    #print_df(df_SETLCMSet_SET, 'df_SETLCMSet_SET 1', True)
    
    # df_SETLCMSet_Assy 에 없는 경우만
    df_SETLCMSet_SET = df_SETLCMSet_SET[~df_SETLCMSet_SET.set_index(cList_grp).index.isin(
                                         df_SETLCMSet_Assy.set_index(cList_grp).index)].copy()
    
    #print_df(df_SETLCMSet, 'df_SETLCMSet_org', False)
    #print_df(df_SETLCMSet_Assy, 'df_SETLCMSet_Assy', True)
    #print_df(df_SETLCMSet_SET, 'df_SETLCMSet_SET', True)    
    del df_in_LCMItem
    
    df_SETLCMSet = pd.concat([df_SETLCMSet_Assy, df_SETLCMSet_SET])
    del [df_SETLCMSet_Assy, df_SETLCMSet_SET]
    #df_SETLCMSet.rename(columns={itemMaterialItemMaterial: itemComponentItemComponent}, inplace=True)
    
    #df_SETLCMSet = df_SETLCMSet.groupby([versionVersionName, locationLocation, itemItem, bOMInfoBOMVersion], 
    #                                    as_index=False)[itemMaterialItemMaterial].max().astype('str')
    '''
    print_df(df_SETLCMSet, 'df_SETLCMSet', True)
    #step('=====> STEP 1-1 : df_SETLCMSet create End')
    
    ################################################################################################################
    # STEP 2 : df_SETLCMKeyItem Set 구성
    ################################################################################################################
    step('=====> STEP 2 : df_SETLCMKeyItem Set create')
    # Item, Location Filtering
    #df_SETLCMKeyItem = df_in_fullbom.merge(df_itemLocation, on=[versionVersionName, itemItem, locationLocation], 
    #                                       how='inner')
    
    # df_in_fullbom = df_SETLCMSet , df_SETLCMSet 그대로 사용, 2026.04.08
    df_SETLCMKeyItem = df_SETLCMSet.copy()
    del [df_in_fullbom, df_itemLocation, df_SETLCMSet]
    
    #df_in_Keyitem Merge : a.item material = c.item material , df_in_Keyitem : Item 으로 수정 2026.04.02
    df_SETLCMKeyItem = df_SETLCMKeyItem.merge(df_in_Keyitem, left_on=[itemMaterialItemMaterial], right_on=[itemItem], 
                                              how='inner', suffixes=('', '_y'))
    #df_SETLCMKeyItem[keymaterial] = df_SETLCMKeyItem[itemMaterialItemMaterial]
    del df_in_Keyitem
    
    
    # df_SETLCMSet Merge : a.location = d.location,  a.item = d.item, a.bom version = d.bom version
    # df_SETLCMSet 그대로 사용하여, merge 필요없음, 2026.04.08
    #df_SETLCMKeyItem = df_SETLCMKeyItem.merge(df_SETLCMSet, on=[versionVersionName, locationLocation, itemItem, 
    #                                                            bOMInfoBOMVersion], how='inner')
    #print_df(df_SETLCMKeyItem, 'df_SETLCMKeyItem TEMP', False)
    #del df_SETLCMSet
    
    df_SETLCMKeyItem = df_SETLCMKeyItem[[versionVersionName, locationLocation, itemItem, bOMInfoBOMVersion, 
                                         itemMaterialItemMaterial, itemComponentItemComponent]]#, keymaterial]]
    df_SETLCMKeyItem.drop_duplicates(inplace=True)
    
    print_df(df_SETLCMKeyItem, 'df_SETLCMKeyItem', True)
    #step('=====> STEP 2-1 : df_SETLCMKeyItem Set create End')
    
    ################################################################################################################
    # STEP 3 :  MG : BOM Version 구성 (df_SETLCMKeyItem  기준으로 df_in_BOMVersion 에 없는)
    ################################################################################################################
    step('=====> STEP 3 : BOM Version create')
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
    df_SETLCMKeyItem_BOM[bOMVersion_UpdateTime] = datetime.datetime.now().replace(microsecond=0)  #2026.04.10 추가
    df_SETLCMKeyItem_BOM[bOMVersion_UpdatedBy] = str_instance                                     #2026.04.10 추가

    bOMVersion_UpdateTime = 'BOM Version_Update Time' #Datetime
    bOMVersion_UpdatedBy  = 'BOM Version_Updated By'  # String
    
    print_df(df_SETLCMKeyItem_BOM, 'df_SETLCMKeyItem_BOM', True)
    #step('=====> STEP 3-1 : BOM Version create End')
    
    ################################################################################################################
    # STEP 4 : MG : BOM Version Prty W 구성
    ################################################################################################################
    step('=====> STEP 4 : BOM Version Prty W create')
    df_PlanningHorizon = df_in_PlanningHorizon[[timeWeek]].copy()
    df_PlanningHorizon.drop_duplicates(inplace=True)
    del df_in_PlanningHorizon
    
    df_PlanningHorizon['key'] = 'x'
    df_SETLCMKeyItem['key'] = 'x'
    
    df_BOMVersionPrtyW = df_SETLCMKeyItem.merge(df_PlanningHorizon, on=['key'], how='inner')
    df_BOMVersionPrtyW.drop(columns=['key'], inplace=True)
    
    #print_df(df_BOMVersionPrtyW, 'df_BOMVersionPrtyW', False)
    
    df_BOMVersionPrtyW_FinalSet = df_BOMVersionPrtyW.merge(df_in_BOMVersionPrtyW, 
                                                           on=[versionVersionName, itemItem, locationLocation, 
                                                               bOMInfoBOMVersion, itemComponentItemComponent, 
                                                               itemMaterialItemMaterial, timeWeek], how='left')
    del df_BOMVersionPrtyW; del df_in_BOMVersionPrtyW
    #print_df(df_BOMVersionPrtyW_FinalSet, 'df_BOMVersionPrtyW_FinalSet org', True)
    
    # BOM Version Prty W_Prty(+) is null 
    df_BOMVersionPrtyW_FinalSet = df_BOMVersionPrtyW_FinalSet[df_BOMVersionPrtyW_FinalSet[bOMVersionPrtyW_Prty].isna()]
    df_BOMVersionPrtyW_FinalSet[bOMVersionPrtyW_Prty] = '1'
    # 250208 jm 추가
    #(250216)임재민 변경 요청 : 
    df_BOMVersionPrtyW_FinalSet[bOMVersionPrtyW_HorizonAsn] = 1
    
    print_df(df_BOMVersionPrtyW_FinalSet, 'df_BOMVersionPrtyW_FinalSet', False)
    #step('=====> STEP 4-1 : BOM Version Prty W create End')
    
    ################################################################################################################
    # STEP 5 : MG : Mtrl Usage 구성
    ################################################################################################################
    step('=====> STEP 5 : Mtrl Usage create')
    df_MtrlUsage = df_SETLCMKeyItem.groupby([versionVersionName, locationLocation, itemMaterialItemMaterial], 
                                            as_index=False)[itemItem].nunique() #count(distinct)
    df_MtrlUsage.rename(columns={itemItem:mtrlUsage_ModelCnt}, inplace=True)
        
    print_df(df_MtrlUsage, 'df_MtrlUsage', False)
    #step('=====> STEP 5-1 : Mtrl Usage create End')
    
    ################################################################################################################
    # STEP 6 : MG : Mtrl Usage Prty W 구성
    ################################################################################################################
    step('=====> STEP 6 : trl Usage Prty create')
    df_MtrlUsagePrtyW = df_SETLCMKeyItem.merge(df_PlanningHorizon, on=['key'], how='inner')
    del df_SETLCMKeyItem; del df_PlanningHorizon
    
    df_MtrlUsagePrtyW = df_MtrlUsagePrtyW[[versionVersionName,locationLocation,itemMaterialItemMaterial,timeWeek]].copy()
    df_MtrlUsagePrtyW.drop_duplicates(inplace=True)
    #print_df(df_MtrlUsagePrtyW, 'df_MtrlUsagePrtyW 1', False)
    df_MtrlUsagePrtyW = df_MtrlUsagePrtyW.merge(df_in_MtrlUsagePrtyW, on=[versionVersionName, locationLocation,
                                                                          itemMaterialItemMaterial, timeWeek], how='left')
    del df_in_MtrlUsagePrtyW
    
    # mtrl usage prty w prty(+)  is null
    df_MtrlUsagePrtyW = df_MtrlUsagePrtyW.loc[df_MtrlUsagePrtyW[mtrlUsagePrtyW_Prty].isna()].copy()
    df_MtrlUsagePrtyW[mtrlUsagePrtyW_Prty]  = '1'
    df_MtrlUsagePrtyW[bOMDiffMgmtW_Priority] = '1'
    
    print_df(df_MtrlUsagePrtyW, 'df_MtrlUsagePrtyW', False)
    #step('=====> STEP 6-1 : trl Usage Prty create End')
    
    ################################################################################################################
    # STEP 9 : output table create
    ################################################################################################################
    step('=====> STEP 9 : Final output table create')
    
    # out Data 생성    
    df_out_BOMVersion = df_SETLCMKeyItem_BOM[[versionVersionName, itemItem, locationLocation, itemMaterialItemMaterial, 
                                              bOMInfoBOMVersion, itemComponentItemComponent, bOMVersion_Prty,
                                              bOMVersion_FixFlag, bOMVersion_UpdateTime, bOMVersion_UpdatedBy]].copy()
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
    
    print_df(df_out_BOMVersion, 'df_out_BOMVersion', False)
    print_df(df_out_BOMVersionPrtyW, 'df_out_BOMVersionPrtyW', False)
    print_df(df_out_MtrlUsage, 'df_out_MtrlUsage', False)
    print_df(df_out_MtrlUsagePrtyW, 'df_out_MtrlUsagePrtyW', False)
    print_df(df_out_MtrlMapSET, 'df_out_MtrlMapSET', False)
    step('=====> STEP 9-1 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_BOMVersion, 'df_out_BOMVersion')
        save_csv_file(df_out_BOMVersionPrtyW, 'df_out_BOMVersionPrtyW')
        save_csv_file(df_out_MtrlUsage, 'df_out_MtrlUsage')
        save_csv_file(df_out_MtrlUsagePrtyW, 'df_out_MtrlUsagePrtyW')
        save_csv_file(df_out_MtrlMapSET, 'df_out_MtrlMapSET')
    
    step('=====> STEP 9-2 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_BOMVersion = pd.DataFrame([], columns=[])
    df_out_BOMVersionPrtyW = pd.DataFrame([], columns=[])
    df_out_MtrlUsage = pd.DataFrame([], columns=[])
    df_out_MtrlUsagePrtyW = pd.DataFrame([], columns=[])
    df_out_MtrlMapSET = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()