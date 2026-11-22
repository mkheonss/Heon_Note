"""
* 프로그램명 
    - PY_MG_MasterValidationDaily

* 내용
    - Master Validation Data 구성

* 변경이력
    - 2026.01.22 / 양희영 / Create
    - 2026.04.03 / 양희영 / Update

* Flow Summary
    
* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함
    
* Input Tables
    - df_in_MasterValidation : Dimension : Master Validation
                               select ([Master Validation].[Validation Batch Type].[D_1TIMES] * [Master Validation].[Validation Stage] * [Master Validation].[Validation Grp01] * [Master Validation].[Validation Grp02] * 
                                       [Master Validation].[Validation Type] * [Master Validation].[Validation Owner] * [Master Validation].[Validation ID] * [Master Validation].[Validation Name]) on row 
                                       include memberproperties  {[Master Validation].[Validation ID],[Validation ID Desc]} {[Master Validation].[Validation Name],[Validation Name Desc]};
    - df_in_ItemSite : df_in_SETItemSite, df_in_LCMItemSite 대체
                       select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Location].[Location] ) on row, 
                       ({Measure.[Item Site Asn_Cur Status]}) on column where {Measure.[Item Site Asn_Cur Status] IN {"ACTIVE", "PLANNED"}};
    - df_in_Demand : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * 
                     [Demand].[DemandID] ) on row, ({Measure.[W Demand Priority], Measure.[W Demand Quantity to SCS], Measure.[W DumDemand Quantity to SCS], Measure.[Dummy]}) on column;
    - df_in_MfgPlan_SOPFPCmp : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Time].[Week] * [Location].[Location] * [To Item].[To Item] * [BOM Info].[BOM Version] ) on row, 
                               ({Measure.[SOP FP Compare_SOP Qty], Measure.[Dummy]}) on column;
    - df_in_BOM : Select (&CWVUI * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column;
    - df_in_Time : Select ([Time].[Week] * [Time].[Day]);
    - df_in_PlanHorizon : Select (&CWVUI) on row, ({Measure.[MP Plan Current Week], Measure.[MP Plan End Date], Measure.[MP Plan End Week], Measure.[MP Plan Start Date], Measure.[MP Plan Start Week]}) on column;
    - df_in_BOD : Select (&CWVUI * [Location].[Location] * Item.[Item Stage] .filter(#.Name in {"SET","LCM"}) * [Item].[Class Category] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                   ({Measure.[BOD Item_BOD LT], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_BOD Valid]}) on column 
                   where {Item.[Plan Group], Item.[Product Group], Measure.[BOD Item_BOD Valid]=="Y", coalesce(Measure.[BOD List_Eff Startweek],&CurrentWeek.element(0).Name)>=&CurrentWeek.element(0).Name, 
                   coalesce(Measure.[BOD List_Eff Endweek],"299912")>=&CurrentWeek.element(0).Name};
    - df_in_TactTime : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Location].[Location] * [Line].[Line] ) on row, 
                      ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn], Measure.[Dummy]}) on column;
    - df_in_WorkCalLine : Select (&CWVUI * [Time].[Week] * [Location].[Location] * [Location].[MF Site Stage].filter(#.Name == "SET" || #.Name contains "LCM") * [Work Type].[Work Type] * [Line].[Line] * [Data Set].[Data Set] ) on row, 
                          ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column;
    - df_in_SETBuildAheadCalW : Select (&CWVUI * [Item].[Item] * &PlanningHorizon * [Location].[Location] * [Location].[Shipment Type] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] ) on row, ({Measure.[Build Ahead Cal W_Period]}) on column;
    - df_in_SETPLCSales : Measure.[PLC Sales_RTS Com Date], Measure.[PLC Sales_RTS FW Limit Date], Measure.[PLC Sales_EOS Com Date] 중 1개라로 not null 인 data, 모두 null인 경우 필요 없음.
                          Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].[SET] * [Sales Domain].[AP2] ) on row, ({Measure.[PLC Sales_RTS Com Date], Measure.[PLC Sales_RTS FW Limit Date], Measure.[PLC Sales_EOS Com Date]}) on column;
    - df_in_PLCMfg : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Location].[Location] * [Location].[Site Stage] ) on row, ({Measure.[PLC Mfg_SRA Com Date], Measure.[PLC Mfg_SRA FW Limit Date]}) on column;
    - df_in_ConstGrpEcp : Select (&CWVUI *  [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Group].[Group ID] ) on row, ({Measure.[Const Grp Ecp_Flag]}) on column where {Measure.[Const Grp Ecp_Flag] != "Y"};
    - df_in_SOPFrozen : SOP Frozen
                        Select (&CWVUI * [Group].[Group ID] ) on row, ({Measure.[SOP Frozen_From Site], Measure.[SOP Frozen_Item]}) on column where {Measure.[SOP Frozen_Item] != "All" && Measure.[SOP Frozen_Valid Flag] == "Y"};
    - df_in_DemandW : Select (&CWVUI * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Dmd W_Qty]}) on column;
    - df_in_WOnHand : Select (&CWVUI * [Item].[Item Stage].[SET].relatedmembers([Item]) * [Location].[Location] * [Location].[Site Stage]) on row, ({Measure.[W OnHand Quantity]}) on column;
    - df_in_WExp_Intransit : Select (&CWVUI * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[W Expected Receipts]}) on column;
    - df_in_CTN : Select (&CWVUI * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Frozen SOP Override Qty]}) on column;
    - df_in_NewModel : Select (&CWVUI * [Location].[Location] * [Sales Domain].[AP2] * [Category].[Category] * [Item New Model].[Item] ) on row, ({Measure.[New Model_Mfg Date]}) on column;
    - df_in_MFGPlan_LCM : Select (&CWVUI * [Item].[Item] * Item.[Item Stage].[LCM] * [Location].[Location] * [Documents].[OrderlineID] ) on row, 
                          ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Open Qty], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_To Site ID]}) on column;
    - df_in_Fullbom_LCM : Select (&CWVUI * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [To Item].[To Item Stage].[LCM] * [Location].[Location] * 
                          [Item Material].[MSL3].filter(#.Name endswith "OpenCell").relatedmembers([Item Material]) * [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, 
                          ({Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Valid]}) on column;
    - df_in_FullBOM : 당주 BOM,  [BOM Type].[SET]
                      Select (&CWVUI * [Location].[Location] * [Item].[Item] * [BOM Info].[BOM Version].filter( ~(#.Name in {"NA","DUMMY","DUMY"}) && ~(#.Name startswith ([WW]))) ) on row, 
                      ({Measure.[Full BOM_Valid], Measure.[Dummy]}) on column where {[BOM Type].[BOM Type].[SET]};
    - df_in_SOPW_Last : 전주 MST_SOP
                        Select (&LastSyncVersion * [Location].[Location] * [Item].[Item] * [BOM Info].[BOM Version].filter(~(#.Name in {"NA","DUMMY","DUMY"}) && ~(#.Name startswith ([WW]))) ) on row, 
                        ({Measure.[SOP W_SET SOP Qty], Measure.[Dummy]}) on column where {Location.[Location Type].filter(#.Name == "MF"), Item.[Item Stage].[SET]};
    - df_in_SOPW : Select (&CWVUI * [Location].[Location] * [To Location].[To Location] * [Trans Mode].[Trans Mode] * [Item].[Item]) on row, 
                   ({Measure.[SOP W_SET SOP Qty], Measure.[Loading Master To Site_Init Dttm], Measure.[Loading Master To Site_Up Dttm], Measure.[Dummy]}) on column 
                   where {Item.[Item Stage].[SET], Time.[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(11).Key), Coalesce(Measure.[SOP W_SET SOP Qty],0) > 0};
    - df_in_LoadingMaster : Select (&CWVUI * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Item].[Item]) on row,
                            ({Measure.[Loading Master To Site_FCL], Measure.[Loading Master To Site_1st Container], Measure.[Loading Master To Site_2nd Container], Measure.[Loading Master To Site_TLB MAX Loading Rate Override], 
                            Measure.[Loading Master To Site_TLB MIN Loading Rate Override], Measure.[Loading Master To Site_Build Ahead Period], Measure.[Loading Master To Site_20FT Qty Override], 
                            Measure.[Loading Master To Site_40HC Qty Override], Measure.[Loading Master To Site_Valid]}) on column where {Measure.[Loading Master To Site_Valid] == "Y"};
    - df_in_ItemJDM : Select (Item.[Item]) where {Item.[JDM].[JDM]};
    - df_in_ItemSiteAsnMF : Select (&CWVUI * [Location].[Location] * [Item].[Item]) on row, 
                            ({Measure.[Item Site Asn_Cur Status]}) on column where {[Location].[Location Type].[MF], Item.[Item Stage].[SET], Measure.[Item Site Asn_Cur Status] in {"ACTIVE","PLANNED"}};
    - df_in_SETBODList : Select (&CWVUI * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                         ({Measure.[BOD List_BOD LT], Measure.[BOD List_Shipment LT], Measure.[BOD List_BOD Valid]}) on column where {Measure.[BOD List_BOD Valid]=="Y"};
    - df_in_LCMBODList : Select (&CWVUI * [Location].[Location] * [Item].[Class Category] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                         ({Measure.[LCM BOD List_Transit Time], Measure.[LCM BOD List_Shipment LT], Measure.[LCM BOD List_BOD Valid]}) on column where {Measure.[LCM BOD List_BOD Valid]=="Y"};
    - df_in_ItemAll : Select ([Item].[Item] * [Item].[Item Stage]);
    - df_in_VersionName : SELECT (&CWVUI);
    
* Output Tables
    - df_out_MstValidResult : MG : Mst Valid Result
                          Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * 
                          [Master Validation].[Validation ID] * [Line].[Line] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Mst Valid Result_Validation Factor]}) on column;

* 테스트 스크립트 :
    EXEC plugin instance [PY_MG_MasterValidationDaily] for Measures {[Mst Valid Result_Validation Factor]} using scope (&CWVUI.unionWith(&LastSyncVersion) * [Master Validation].[Validation Batch Type].[D_4TIMES])  
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
	
    EXEC plugin instance [PY_MG_MasterValidationDaily] for Measures {[Mst Valid Result_Validation Factor]} using scope (&CWVUI.unionWith(&LastSyncVersion) * [Master Validation].[Validation Batch Type].[D_1TIMES])  
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
    
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
from datetime import datetime as dt
import warnings

warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_MasterValidationDaily'
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
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====>STEP 0-1 DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    col_ValidationBatchType = 'Master Validation.[Validation Batch Type]'
    col_VersionVersionName = 'Version.[Version Name]'
    col_ItemItem = 'Item.[Item]'
    col_ToItemToItem = 'To Item.[To Item]'
    col_ItemItemStage = 'Item.[Item Stage]'
    col_ItemClassCategory = 'Item.[Class Category]'
    col_LocationLocation = 'Location.[Location]'
    col_ToLocationToLocation = 'To Location.[To Location]'
    col_LocationShipmentType = 'Location.[Shipment Type]'
    col_LocationSiteStage = 'Location.[Site Stage]'
    col_LocationMFSiteStage = 'Location.[MF Site Stage]'
    col_SubLocationSubLocation = 'Sub Location.[Sub Location]'
    col_TransModeTransMode = 'Trans Mode.[Trans Mode]'
    col_MasterValidationValidationID = 'Master Validation.[Validation ID]'
    col_LineLine = 'Line.[Line]'
    col_SalesDomainAP2 = 'Sales Domain.[AP2]'
    col_BOMInfoBOMID = 'BOM Info.[BOM ID]'
    col_BOMInfoBOMVersion = 'BOM Info.[BOM Version]'
    col_TimeWeek = 'Time.[Week]'
    col_TimeDay = 'Time.[Day]'
    col_GroupGroupID = 'Group.[Group ID]'
    col_CategoryCategory = 'Category.[Category]'
    col_ItemNewModelItem = 'Item New Model.[Item]'
    
    col_BOMMaster_EffEnddate = 'BOM Master_Eff Enddate'
    col_BOMMaster_EffStartdate = 'BOM Master_Eff Startdate'
    col_BODItem_EffStartdate = 'BOD Item_Eff Startdate'
    col_BODItem_EffEnddate = 'BOD Item_Eff Enddate'
    
    col_BOMMaster_BOMID = 'BOM Master_BOM ID'
    col_MPPlanCurrentWeek = 'MP Plan Current Week'
    col_MPPlanStartWeek = 'MP Plan Start Week'
    col_MPPlanEndWeek = 'MP Plan End Week'
    col_MPPlanStartDate = 'MP Plan Start Date'
    col_MPPlanEndDate = 'MP Plan End Date'
    col_WorkCalLine_Time = 'Work Cal Line_Time'
    col_BuildAheadCalW_Period = 'Build Ahead Cal W_Period'
    col_PLCSales_RTSComDate = 'PLC Sales_RTS Com Date'
    col_PLCSales_RTSFWLimitDate = 'PLC Sales_RTS FW Limit Date'
    col_PLCSales_EOSComDate = 'PLC Sales_EOS Com Date'
    col_PLCMfg_SRAComDate = 'PLC Mfg_SRA Com Date'
    col_PLCMfg_SRAFWLimitDate = 'PLC Mfg_SRA FW Limit Date'
    col_Inv_Qty = 'Inv_Qty'
    col_Intr_Qty = 'Intr_Qty'
    
    col_ValidationFactor = "Mst Valid Result_Validation Factor"
    col_EffStartWeek = 'EffStartWeek'
    col_EffEndWeek = 'EffEndWeek'
    col_EOSComWeek = 'EOS Com Week'
    
    col_PlanHorizonStartWeek = 'PlanHorizonStartWeek'
    col_PlanHorizonEndWeek = 'PlanHorizonEndWeek'
    
    col_SOPFrozen_FromSite = 'SOP Frozen_From Site'
    col_SOPFrozen_Item = 'SOP Frozen_Item'
    col_DmdW_Qty = 'Dmd W_Qty'
    col_WOnHandQuantity = 'W OnHand Quantity'
    col_WExpectedReceipts = 'W Expected Receipts'
    col_NewModel_MfgDate = 'New Model_Mfg Date'
    col_CTNItemConst_FrozenSOPOverrideQty = 'CTN Item Const_Frozen SOP Override Qty'
    col_MfgPlan_Qty = 'Mfg Plan_Qty'
    
    col_LoadingMasterToSite_InitDttm = 'Loading Master To Site_Init Dttm'
    col_LoadingMasterToSite_UpDttm   = 'Loading Master To Site_Up Dttm'
    col_LMToSite_FCL = 'Loading Master To Site_FCL'
    col_LMToSite_1stContainer = 'Loading Master To Site_1st Container'
    col_LMToSite_2ndContainer = 'Loading Master To Site_2nd Container'
    col_LMToSite_MaxLoadingRate = 'Loading Master To Site_TLB MAX Loading Rate Override'
    col_LMToSite_MinLoadingRate = 'Loading Master To Site_TLB MIN Loading Rate Override'
    col_LMToSite_BldAhdPeriod = 'Loading Master To Site_Build Ahead Period'
    col_LMToSite_20FTQty = 'Loading Master To Site_20FT Qty Override'
    col_LMToSite_40HCQty = 'Loading Master To Site_40HC Qty Override'
    
    col_BODItem_BODLT      = 'BOD Item_BOD LT'
    col_BODItem_ShipmentLT = 'BOD Item_Shipment LT'
    col_BODList_BODLT      = 'BOD List_BOD LT'
    col_BODList_ShipmentLT = 'BOD List_Shipment LT'
    col_LCMBODList_TransitTime = 'LCM BOD List_Transit Time'
    col_LCMBODList_ShipmentLT  = 'LCM BOD List_Shipment LT'
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    # paramOutVersion_VALUE = "CWV_MP" # CWV_MP
    
    # Local 함수 선언 ----------------------------------------
    def fn_valid_ITEMSITE(l_col_List, a_ValidationID, a_df_By, a_df_Target):
        
        df_By = a_df_By[l_col_List].copy()
        df_By.drop_duplicates(inplace=True)
        
        df_Target = a_df_Target[l_col_List].copy()
        df_Target[col_MasterValidationValidationID] = a_ValidationID
        df_Target.drop_duplicates(inplace=True)
        
        # Item & Location : 존재 확인 : SETItemSite에 없는 Item, Site 추출
        df_Vd_Return = df_Target[~df_Target.set_index([col_ItemItem, col_LocationLocation]).index.isin(
            df_By.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
        del [df_By, df_Target]
        df_Vd_Return[col_SubLocationSubLocation] = '-'
        df_Vd_Return[col_TransModeTransMode] = '-'
        df_Vd_Return[col_BOMInfoBOMVersion] = '-'
        df_Vd_Return[col_LineLine] = '-'
        df_Vd_Return[col_SalesDomainAP2] = '-'
        df_Vd_Return[col_ValidationFactor] = '-'
        return df_Vd_Return
    
    
    def fn_MULTI_BOD(a_ValidationID, df_source : pd.DataFrame) -> pd.DataFrame:
        # df_in_SETBOD / df_in_LCMBOD 에서 
        # Item, Location, Sub Location 을 기준으로  Trans Mode가 복수개이고, Trans Mode가 AIR, EXPRESS가 포함이 되어 있는 경우
        #    BOD Item_Eff Enddate가 겹치는   Item, Location, Sub Location, Trans Mode (AIR or EXPRESS) 
        #    (Air/Express가 다른 TP Mode와 유효구간이 겹치는 경우)
        
        clist_tmp = [col_VersionVersionName, col_ItemItem, col_LocationLocation, col_SubLocationSubLocation,
                     col_TransModeTransMode, col_BODItem_EffStartdate, col_BODItem_EffEnddate]
        df_Ext_Data = df_source[clist_tmp].copy()
        df_Ext_Data['Startdate'] = df_Ext_Data[col_BODItem_EffStartdate]
        df_Ext_Data['Enddate'] = df_Ext_Data[col_BODItem_EffEnddate]
        
        df_Ext_Data['Startdate'].fillna(pd.to_datetime("2001-01-01"), inplace=True)  # 구간비교용 date
        df_Ext_Data['Enddate'].fillna(pd.to_datetime("2199-01-01"), inplace=True)  # 구간비교용 date
        
        cList_group = [col_VersionVersionName, col_ItemItem, col_LocationLocation, col_SubLocationSubLocation]
        df_Ext_Data['count'] = df_Ext_Data.groupby(cList_group)[col_TransModeTransMode].transform(
            'nunique')  # count(distinct)
        
        df_Ext_Data = df_Ext_Data[df_Ext_Data['count'] >= 2]  # Trans Mode가 복수개
        
        df_AIR_EXPRESS = df_Ext_Data[(df_Ext_Data[col_TransModeTransMode] == 'AIR') |
                                     (df_Ext_Data[col_TransModeTransMode] == 'EXPRESS')].copy()
        
        clist_tmp = [col_VersionVersionName, col_ItemItem, col_LocationLocation, col_SubLocationSubLocation,
                     col_TransModeTransMode, col_BODItem_EffStartdate, col_BODItem_EffEnddate, 'Startdate', 'Enddate']
        df_AIR_EXPRESS = df_AIR_EXPRESS[clist_tmp]
        # print_df(df_AIR_EXPRESS, 'df_AIR_EXPRESS', False)
        
        # Trans Mode가 "AIR", "EXPRESS"가 포함이 되어 있는 경우
        df_Ext_Data = df_Ext_Data[df_Ext_Data.set_index(cList_group).index.isin(
            df_AIR_EXPRESS.set_index(cList_group).index)].copy()
        
        # Trans Mode가 "AIR", "EXPRESS"가 포함이 되어 있는 경우 중 "AIR", "EXPRESS"가 아닌 data
        df_not_A_E = df_Ext_Data[~((df_Ext_Data[col_TransModeTransMode] == 'AIR') |
                                   (df_Ext_Data[col_TransModeTransMode] == 'EXPRESS'))].copy()
        df_not_A_E = df_not_A_E[clist_tmp]
        # print_df(df_not_A_E, 'df_not_A_E', False)
        del df_Ext_Data
        
        # 구간 비교를 위해 df_AIR_EXPRESS 와 df_not_A_E MERGE
        df_Vd_Return = df_AIR_EXPRESS.merge(df_not_A_E, on=cList_group, how='inner', suffixes=('', '_y'))
        del [df_AIR_EXPRESS, df_not_A_E]
        
        # 구간 비교
        df_Vd_Return = df_Vd_Return[(df_Vd_Return['Startdate'] <= df_Vd_Return['Enddate' + '_y']) &
                                  (df_Vd_Return['Enddate'] >= df_Vd_Return['Startdate' + '_y'])]
        
        clist_tmp = [col_VersionVersionName, col_ItemItem, col_LocationLocation, col_SubLocationSubLocation,
                     col_TransModeTransMode, col_BODItem_EffStartdate, col_BODItem_EffEnddate]
        df_Vd_Return = df_Vd_Return[clist_tmp]
        df_Vd_Return.drop_duplicates(inplace=True)
        
        df_Vd_Return[col_MasterValidationValidationID] = a_ValidationID
        # df_Vd_Return[col_SubLocationSubLocation] = '-'
        # df_Vd_Return[col_TransModeTransMode] = '-'
        df_Vd_Return[col_BOMInfoBOMVersion] = '-'
        df_Vd_Return[col_LineLine] = '-'
        df_Vd_Return[col_SalesDomainAP2] = '-'
        df_Vd_Return[col_ValidationFactor] = (
            'BOD Item_Eff Startdate = ' + df_Vd_Return[col_BODItem_EffStartdate].dt.date.astype('str') +
            ', BOD Item_Eff Enddate = ' + df_Vd_Return[col_BODItem_EffEnddate].dt.date.astype('str'))
        
        # print_df(df_Vd_Return, '(SET)MULTI_BOD - df_Vd_Return', False)
        
        # 칼럼정리
        df_Vd_Return = df_Vd_Return[clist_all]
        df_Vd_Return.drop_duplicates(inplace=True)
        return df_Vd_Return
    
    
    # -------------------------------------------------------
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion  = paramOutVersion_VALUE
        
        df_in_MasterValidation = read_csv_file("df_in_MasterValidation")
        df_in_ItemSite = read_csv_file("df_in_ItemSite")
        df_in_Demand = read_csv_file("df_in_Demand")
        df_in_MfgPlan_SOPFPCmp = read_csv_file("df_in_MfgPlan_SOPFPCmp")
        df_in_BOM = read_csv_file("df_in_BOM")
        df_in_PlanHorizon = read_csv_file("df_in_PlanHorizon")
        df_in_Time = read_csv_file("df_in_Time")
        df_in_TactTime = read_csv_file("df_in_TactTime")
        df_in_WorkCalLine = read_csv_file("df_in_WorkCalLine")        
        df_in_SETBuildAheadCalW = read_csv_file("df_in_SETBuildAheadCalW")
        df_in_SETPLCSales = read_csv_file("df_in_SETPLCSales")
        df_in_ConstGrpEcp = read_csv_file("df_in_ConstGrpEcp")
        df_in_SOPFrozen = read_csv_file("df_in_SOPFrozen")
        df_in_DemandW = read_csv_file("df_in_DemandW")
        df_in_WOnHand = read_csv_file("df_in_WOnHand")
        df_in_WExp_Intransit = read_csv_file("df_in_WExp_Intransit")
        df_in_CTN = read_csv_file("df_in_CTN")
        df_in_PLCMfg = read_csv_file("df_in_PLCMfg")
        df_in_NewModel = read_csv_file("df_in_NewModel")
        df_in_MFGPlan_LCM = read_csv_file("df_in_MFGPlan_LCM")
        df_in_Fullbom_LCM = read_csv_file("df_in_Fullbom_LCM")
        df_in_ItemAll = read_csv_file("df_in_ItemAll")
        df_in_LoadingMaster = read_csv_file("df_in_LoadingMaster")
        df_in_SOPW = read_csv_file("df_in_SOPW")
        df_in_ItemJDM = read_csv_file("df_in_ItemJDM")
        df_in_ItemSiteAsnMF = read_csv_file("df_in_ItemSiteAsnMF")
        df_in_BOD = read_csv_file("df_in_BOD")
        df_in_SETBODList = read_csv_file("df_in_SETBODList")
        df_in_LCMBODList = read_csv_file("df_in_LCMBODList")
        df_in_FullBOM = read_csv_file("df_in_FullBOM")
        df_in_SOPW_Last = read_csv_file("df_in_SOPW_Last")
        df_in_VersionName = read_csv_file("df_in_VersionName")
        
    # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # MP Plan End Date     MP Plan Start Date
    # input dataframe 확인용 로그
    # note(f'=====> paramOutVersion : {paramOutVersion}')
    print_df(df_in_MasterValidation, 'df_in_MasterValidation', False)
    print_df(df_in_ItemSite, 'df_in_ItemSite', False)
    #print_df(df_in_Intransit, 'df_in_Intransit', False)
    print_df(df_in_Demand, 'df_in_Demand', False)
    #print_df(df_in_Inventory, 'df_in_Inventory', False)
    print_df(df_in_MfgPlan_SOPFPCmp, 'df_in_MfgPlan_SOPFPCmp', False)
    print_df(df_in_BOM, 'df_in_BOM', False)
    print_df(df_in_PlanHorizon, 'df_in_PlanHorizon', False)
    print_df(df_in_Time, 'df_in_Time', False)
    print_df(df_in_TactTime, 'df_in_TactTime', False)
    print_df(df_in_WorkCalLine, 'df_in_WorkCalLine', False)
    print_df(df_in_SETBuildAheadCalW, 'df_in_SETBuildAheadCalW', False)
    #print_df(df_in_SSW, 'df_in_SSW',False)
    print_df(df_in_SETPLCSales, 'df_in_SETPLCSales', False)
    print_df(df_in_ConstGrpEcp, 'df_in_ConstGrpEcp', False)
    print_df(df_in_SOPFrozen, 'df_in_SOPFrozen', False)
    print_df(df_in_DemandW, 'df_in_DemandW', False)
    print_df(df_in_WOnHand, 'df_in_WOnHand', False)
    print_df(df_in_WExp_Intransit, 'df_in_WExp_Intransit', False)
    print_df(df_in_CTN, 'df_in_CTN', False)
    print_df(df_in_PLCMfg, 'df_in_PLCMfg', False)
    print_df(df_in_NewModel, 'df_in_NewModel', False)
    print_df(df_in_MFGPlan_LCM, 'df_in_MFGPlan_LCM', False)
    print_df(df_in_Fullbom_LCM, 'df_in_Fullbom_LCM', False)
    print_df(df_in_ItemAll, 'df_in_ItemAll', False)
    print_df(df_in_LoadingMaster, 'df_in_LoadingMaster', False)
    print_df(df_in_SOPW, 'df_in_SOPW', False)
    print_df(df_in_ItemJDM, 'df_in_ItemJDM', False)
    print_df(df_in_ItemSiteAsnMF, 'df_in_ItemSiteAsnMF', False)
    print_df(df_in_BOD, 'df_in_BOD',False)
    print_df(df_in_SETBODList, 'df_in_SETBODList', False)
    print_df(df_in_LCMBODList, 'df_in_LCMBODList', False)
    print_df(df_in_FullBOM, 'df_in_FullBOM', False)
    print_df(df_in_SOPW_Last, 'df_in_SOPW_Last', False)
    print_df(df_in_VersionName, 'df_in_VersionName', False)
    
    # DATA TYPE 설정
    
    # PANDAS 지원되는 일자 : 1697년 9월 21일 ~ 2262년 4월 11일
    def replace_date(date_string, rtn_type):
        max_date = dt.strptime("2262-04-11", '%Y-%m-%d')
        
        date_string = str(date_string)
        
        if date_string != 'nan':
            try:
                date_object = dt.strptime(date_string, '%m/%d/%Y %I:%M:%S %p')
            except Exception as e1:
                try:
                    date_object = dt.strptime(date_string, '%Y-%m-%d')
                except Exception as e2:
                    date_object = dt.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            
            if date_object > max_date:
                return_date = max_date
            else:
                return_date = date_object
            
            return return_date.strftime(rtn_type)
    
    
    VALIDATION_BATCH_TYPE_VALUE = df_in_MasterValidation.loc[0, col_ValidationBatchType]
    note(f'=====> Validation Batch Type : {VALIDATION_BATCH_TYPE_VALUE}')
    # -------------------------------------------------------------------------------------   
    
    if df_in_BOD[col_BODItem_EffStartdate].dtype != 'datetime64[ns]':
        df_in_BOD[col_BODItem_EffStartdate] = pd.to_datetime(df_in_BOD[col_BODItem_EffStartdate]
                                                             , format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_BOD[col_BODItem_EffEnddate].dtype != 'datetime64[ns]':
        df_in_BOD[col_BODItem_EffEnddate] = pd.to_datetime(df_in_BOD[col_BODItem_EffEnddate]
                                                           , format='%m/%d/%Y %I:%M:%S %p')
    
    df_in_BOD[col_BODItem_BODLT] = df_in_BOD[col_BODItem_BODLT].fillna(0).astype('int64')
    df_in_BOD[col_BODItem_ShipmentLT] = df_in_BOD[col_BODItem_ShipmentLT].fillna(0).astype('int64')
    df_in_PlanHorizon = df_in_PlanHorizon.astype({col_MPPlanCurrentWeek: 'str', col_MPPlanStartWeek: 'str'
                                                     , col_MPPlanEndWeek: 'str'}, copy=True)
    print_df(df_in_PlanHorizon, 'df_in_PlanHorizon x', False)
    
    df_in_Time[col_TimeDay] = pd.to_datetime(df_in_Time[col_TimeDay], format='%Y-%m-%d')
    df_in_Time = df_in_Time.astype({col_TimeWeek: 'str'}, copy=True)
    print_df(df_in_Time, 'df_in_Time x', False)
    
    if df_in_SETPLCSales[col_PLCSales_EOSComDate].dtype != 'datetime64[ns]':
        # 2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_SETPLCSales[col_PLCSales_EOSComDate] = np.where(df_in_SETPLCSales[col_PLCSales_EOSComDate].isna(),
                                                              df_in_SETPLCSales[col_PLCSales_EOSComDate],
                                                              df_in_SETPLCSales[col_PLCSales_EOSComDate].apply(
                                                                  lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                                                              )
        df_in_SETPLCSales[col_PLCSales_EOSComDate] = pd.to_datetime(df_in_SETPLCSales[col_PLCSales_EOSComDate]
                                                                    , format='%m/%d/%Y %I:%M:%S %p')
    
    print_df(df_in_SETPLCSales, 'df_in_SETPLCSales x', False)
    
    if df_in_PLCMfg[col_PLCMfg_SRAFWLimitDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[col_PLCMfg_SRAFWLimitDate] = pd.to_datetime(df_in_PLCMfg[col_PLCMfg_SRAFWLimitDate]
                                                                 , format='%m/%d/%Y %I:%M:%S %p')
    print_df(df_in_PLCMfg, 'df_in_PLCMfg x', False)
    
    if df_in_NewModel[col_NewModel_MfgDate].dtype != 'datetime64[ns]':
        df_in_NewModel[col_NewModel_MfgDate] = pd.to_datetime(df_in_NewModel[col_NewModel_MfgDate]
                                                              , format='%m/%d/%Y %I:%M:%S %p')
    print_df(df_in_NewModel, 'df_in_NewModel x', False)
    
    df_in_Demand = df_in_Demand.astype({col_TimeWeek: 'str'}, copy=True)
    #df_in_Inventory = df_in_Inventory.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_MfgPlan_SOPFPCmp = df_in_MfgPlan_SOPFPCmp.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_WorkCalLine = df_in_WorkCalLine.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_SETBuildAheadCalW = df_in_SETBuildAheadCalW.astype({col_TimeWeek: 'str'}, copy=True)
    #df_in_SSW = df_in_SSW.astype({col_TimeWeek: 'str'}, copy=True)
    
    print_df(df_in_Demand, 'df_in_Demand 2', False)
    #print_df(df_in_Inventory, 'df_in_Inventory 2', False)
    print_df(df_in_MfgPlan_SOPFPCmp, 'df_in_MfgPlan_SOPFPCmp 2', False)
    print_df(df_in_WorkCalLine, 'df_in_WorkCalLine 2', False)
    print_df(df_in_SETBuildAheadCalW, 'df_in_SETBuildAheadCalW 2', False)
    #print_df(df_in_SSW, 'df_in_SSW 2', False)
    
    #df_in_LoadingMaster.drop(columns=['Dummy'], inplace=True)
    df_in_SOPW.drop(columns=['SOP W_SET SOP Qty', 'Dummy'], inplace=True)
    
    if df_in_SOPW[col_LoadingMasterToSite_InitDttm].dtype != 'datetime64[ns]':
        df_in_SOPW[col_LoadingMasterToSite_InitDttm] = pd.to_datetime(df_in_SOPW[col_LoadingMasterToSite_InitDttm]
                                                              , format='%m/%d/%Y %I:%M:%S %p')
        
    if df_in_SOPW[col_LoadingMasterToSite_UpDttm].dtype != 'datetime64[ns]':
        df_in_SOPW[col_LoadingMasterToSite_UpDttm] = pd.to_datetime(df_in_SOPW[col_LoadingMasterToSite_UpDttm]
                                                              , format='%m/%d/%Y %I:%M:%S %p')
    print_df(df_in_SOPW, 'df_in_SOPW x', False)

    step('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    step('=====> STEP 0-4 : 추가 df Create ')
    # Version Name 값 Setting
    VERSION_VALUE = df_in_VersionName.loc[0, col_VersionVersionName]
    
    # SET, LCM 분리 ---------------------------------------------------
    df_in_SETItemSite = df_in_ItemSite[df_in_ItemSite[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMItemSite = df_in_ItemSite[df_in_ItemSite[col_ItemItemStage] == 'LCM'].copy()
    del df_in_ItemSite
    print_df(df_in_SETItemSite, 'df_in_SETItemSite', False)
    print_df(df_in_LCMItemSite, 'df_in_LCMItemSite', False)
    
    df_in_SETDemand = df_in_Demand[df_in_Demand[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMDemand = df_in_Demand[df_in_Demand[col_ItemItemStage] == 'LCM'].copy()
    del df_in_Demand
    print_df(df_in_SETDemand, 'df_in_SETDemand', False)
    print_df(df_in_LCMDemand, 'df_in_LCMDemand', False)
    
    df_in_SETMfgPlan_SFC = df_in_MfgPlan_SOPFPCmp[df_in_MfgPlan_SOPFPCmp[col_ItemItemStage] == 'SET'].copy()
    del df_in_MfgPlan_SOPFPCmp
    print_df(df_in_SETMfgPlan_SFC, 'df_in_SETMfgPlan_SFC', False)
    
    df_in_SETBOD = df_in_BOD[df_in_BOD[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMBOD = df_in_BOD[df_in_BOD[col_ItemItemStage] == 'LCM'].copy()
    del df_in_BOD
    print_df(df_in_SETBOD, 'df_in_SETBOD',True)
    print_df(df_in_LCMBOD, 'df_in_LCMBOD',False)
    
    df_in_SETTactTime = df_in_TactTime[df_in_TactTime[col_ItemItemStage] == 'SET'].copy()
    del df_in_TactTime
    print_df(df_in_SETTactTime, 'df_in_SETTactTime', False)
    
    df_in_SETWorkCalLine = df_in_WorkCalLine[df_in_WorkCalLine[col_LocationMFSiteStage] == 'SET'].copy()
    del df_in_WorkCalLine
    print_df(df_in_SETWorkCalLine, 'df_in_SETWorkCalLine', False)
    df_in_SETConstGrpEcp = df_in_ConstGrpEcp[df_in_ConstGrpEcp[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMConstGrpEcp = df_in_ConstGrpEcp[df_in_ConstGrpEcp[col_ItemItemStage] == 'LCM'].copy()
    del df_in_ConstGrpEcp
    print_df(df_in_SETConstGrpEcp, 'df_in_SETConstGrpEcp', False)
    print_df(df_in_LCMConstGrpEcp, 'df_in_LCMConstGrpEcp', False)
    
    df_in_SETItem = df_in_ItemAll[df_in_ItemAll[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMItem = df_in_ItemAll[df_in_ItemAll[col_ItemItemStage] == 'LCM'].copy()
    del df_in_ItemAll
    print_df(df_in_SETItem, 'df_in_SETItem', False)
    print_df(df_in_LCMItem, 'df_in_LCMItem', False)
    
    # Version 분리 : VERSION_VALUE 용, LastVersion 용 ---------------------
    # LastVersion : LastVersion 먼저처리----------------------------------------------------------
    
    # df_in_Time 칼럼 정리
    df_in_Time = df_in_Time[[col_TimeWeek, col_TimeDay]]
    
    df_Time_Min_Max = df_in_Time.copy()
    df_Time_Min_Max['Dummy'] = 'A'
    df_Time_Min_Max = df_Time_Min_Max.groupby(['Dummy'], as_index=False).agg(Min_Day=(col_TimeDay, 'min'),
                                                                             Max_Day=(col_TimeDay, 'max'))
    print_df(df_Time_Min_Max, 'df_Time_Min_Max', False)
    
    # df_in_PlanHorizon 칼럼 추가
    df_in_PlanHorizon[col_PlanHorizonStartWeek] = df_in_PlanHorizon[col_MPPlanStartWeek]
    df_in_PlanHorizon[col_PlanHorizonEndWeek] = df_in_PlanHorizon[col_MPPlanEndWeek]
    
    #### df_SETBOM : SET ITEM 에 해당하는 자료 추출
    df_in_BOM[col_ItemItem] = df_in_BOM[col_BOMMaster_BOMID]
    df_SETBOM = df_in_BOM[df_in_BOM.set_index([col_ItemItem]).index.isin(
        df_in_SETItem.set_index([col_ItemItem]).index)].copy()
    del df_in_BOM
    # BOM Info.[BOM ID] = Item + BOM Info.[BOM Version]
    df_SETBOM[col_BOMInfoBOMVersion] = df_SETBOM[col_BOMInfoBOMID].str.split('_').str[1]
    # print_df(df_SETBOM, 'df_SETBOM',False)
    
    
    # 'NA' 값을 nan 으로 읽어들임.
    df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion] = np.where(df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion].isna()
                                                           , "-x-", df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion])
    df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion] = np.where(df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion] == "-x-"
                                                           , "NA", df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion])
    
    
    # 여러번 사용하는 Set 구성 -----------------------------------------------
    df_SETBuildAheadCalW_Demand_Sub_Loc = df_in_SETBuildAheadCalW[
        df_in_SETBuildAheadCalW.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
            df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
    print_df(df_SETBuildAheadCalW_Demand_Sub_Loc, 'df_SETBuildAheadCalW_Demand_Sub_Loc', False)
    
    # ------------------------------------------------------------------------
    step('=====> STEP 0-5 : 추가 df Create End')
    
    ################################################################################################################
    # STEP 1 : Validate data Create
    ################################################################################################################
    step('=====> STEP 1-1 : Validate data Create')
    
    # 칼럼설정
    clist_V_ITM_LOC = [col_VersionVersionName, col_ItemItem, col_LocationLocation]
    clist_V_ITM_LOC_Sub = clist_V_ITM_LOC + [col_SubLocationSubLocation]
    clist_bod = clist_V_ITM_LOC + [col_SubLocationSubLocation, col_TransModeTransMode]
    clist_grain = [col_VersionVersionName, col_MasterValidationValidationID, col_ItemItem, col_LocationLocation,
                   col_SubLocationSubLocation, col_TransModeTransMode, col_BOMInfoBOMVersion,
                   col_LineLine, col_SalesDomainAP2]
    clist_all = [col_VersionVersionName, col_MasterValidationValidationID, col_ItemItem, col_LocationLocation,
                 col_SubLocationSubLocation, col_TransModeTransMode, col_BOMInfoBOMVersion,
                 col_LineLine, col_SalesDomainAP2, col_ValidationFactor]
    
    # 임시 --------------------------------------------------
    #df_in_MasterValidation = df_in_MasterValidation[df_in_MasterValidation[col_MasterValidationValidationID] == '(SET)LOADING_MASTER_ERROR']
    # ------------------------------------------------------
    
    note(f'=====> for Strt ======================================================= ')
    df_Vld_Result_All = pd.DataFrame(columns=clist_all)  # 빈 dataframe
    
    for idx, row in df_in_MasterValidation.iterrows():
        # note(f'=====> Validation ID : {row[col_MasterValidationValidationID]}')
        df_Vld_Result_TMP = pd.DataFrame(columns=clist_all)  # 빈 dataframe
        CHK_I = 0
        # note(f'=====> Validation ID : {row[col_MasterValidationValidationID]} ----Start----')
        if row[col_MasterValidationValidationID] == '(SET)ITEMSITE_DEMAND':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                  , df_in_SETItemSite.copy()
                                                  , df_in_SETDemand.copy())
        
        elif row[col_MasterValidationValidationID] == '(LCM)ITEMSITE_DEMAND':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                  , df_in_LCMItemSite.copy()
                                                  , df_in_LCMDemand.copy())
        
        elif row[col_MasterValidationValidationID] == '(SET)BAL_DIR_SITE':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item 대상으로
            df_Ext_Data = df_SETBuildAheadCalW_Demand_Sub_Loc.copy()
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_LocationShipmentType].isin(['DIR_S', 'DIR_D'])]
            # print_df(df_Ext_Data, 'df_Ext_Data',False)
            
            # Group by Item, Location, Sub Location
            df_Ext_Data['BAL_max'] = df_Ext_Data[col_BuildAheadCalW_Period]
            df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC_Sub,
                                              as_index=False).agg({'BAL_max': 'max'}, skipna=True)
            # Max(BAL) >= 1
            df_Ext_Data = df_Ext_Data[(df_Ext_Data['BAL_max'] >= 1)]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            # df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = ('Max(BAL) = ' + df_Ext_Data['BAL_max'].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(SET)BOD_EFFECTIVENESS':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # >> 날짜 체크 로직은 삭제하고
            # >> df_in_SETBOD 가 매치가 되지 않는 것을 찾는 로직으로 변경 (2026.02.09)
            
            # (Demand) 유효 BOD가 하나도 없음(추출 : Item, Locaion)
            # SETDemand에 있는 Item, Site 대상으로 : SETBOD(Item, Sub Location) 정보
            
            df_Ext_Data = df_in_SETDemand[~df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                       df_in_SETBOD.set_index([col_ItemItem, col_SubLocationSubLocation]).index)].copy()
                       
            # megge : df_in_PlanHorizon
            df_Ext_Data = df_Ext_Data.merge(df_in_PlanHorizon, on=[col_VersionVersionName], how='inner')
                        
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[col_MasterValidationValidationID] == '(SET)BOD_LT_GAP':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #>> df_in_SETBOD 와 df_in_SETBODList 를 Merge한 후 [BOD List_BOD LT] <> [BOD Item_BOD LT] or [BOD List_Shipment LT] <> [BOD Item_Shipment LT] 인 BOD Item 정보
            #>> Version Name, Validation ID, Location, Sub Location, Item, Trans Mode, Validation Factor 만 설정, 나머지는 ‘-’
            # Validation Factor = "SET BOD List([BOD List_BOD LT], [BOD List_Shipment LT]) vs BOD Item ([BOD Item_BOD LT], [BOD Item_Shipment LT])"
            
            cList_tmp = [col_VersionVersionName, col_LocationLocation, col_SubLocationSubLocation, col_TransModeTransMode]
                        
            df_Ext_Data = df_in_SETBOD.merge(df_in_SETBODList, on=cList_tmp, how='inner', suffixes=('', '_y'))
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_BODList_BODLT] != df_Ext_Data[col_BODItem_BODLT]) |
                                      (df_Ext_Data[col_BODList_ShipmentLT] != df_Ext_Data[col_BODItem_ShipmentLT])]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            #df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = ('SET BOD List('+ 
                                                 df_Ext_Data[col_BODList_BODLT].astype('str') + ', ' + 
                                                 df_Ext_Data[col_BODList_ShipmentLT].astype('str') + ') vs BOD Item (' +
                                                 df_Ext_Data[col_BODItem_BODLT].astype('str') + ', ' +
                                                 df_Ext_Data[col_BODItem_ShipmentLT].astype('str') + ')'
                                                 )
            
            #print_df(df_Ext_Data, 'df_Ext_Data', False)
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)   
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_MFGPLAN':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETMfgPlan에 있는 Item, Site가 SETBOD(Item, Location)에 한건도 없을 경우 Item, Site 추출
            df_Ext_Data = df_in_SETMfgPlan_SFC[
                ~df_in_SETMfgPlan_SFC.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                    df_in_SETBOD.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)        
        
        elif row[col_MasterValidationValidationID] == '(SET)BOM_DEMAND':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # SETDemand에 있는 Item, Site 대상으로 : SETDemand join과 같음.
            df_Ext_Data = df_SETBOM[df_SETBOM.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                    df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            
            # megge : df_in_PlanHorizon
            df_Ext_Data = df_Ext_Data.merge(df_in_PlanHorizon, on=[col_VersionVersionName], how='inner')
            
            # >> 날짜 체크 로직은 삭제하고
            # >> df_in_SETBOD 가 매치가 되지 않는 것을 찾는 로직으로 변경 (2026.02.09)
            cList_bom = [col_VersionVersionName, col_ItemItem, col_LocationLocation]
            cList_bod = [col_VersionVersionName, col_ItemItem, col_SubLocationSubLocation]
            
            df_Ext_Data = df_Ext_Data[~df_Ext_Data.set_index(cList_bom).index.isin(
                                       df_in_SETBOD.set_index(cList_bod).index)].copy()
            
            #print_df(df_Ext_Data, 'df_Ext_Data', False)

            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            #df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOM_ECN_DELETE':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            #전주 MST_SOP기준으로 버전이 존재하였으나, 당주 BOM DB에 존재하지 않는 버전 리스트업
            #>> df_in_SOPW_Last 와 df_in_FullBOM을 merge하여 df_in_SOPW_Last에만 있는 것 추출
            
            cList_tmp = [col_LocationLocation, col_ItemItem, col_BOMInfoBOMVersion]
            
            df_Ext_Data = df_in_SOPW_Last[~df_in_SOPW_Last.set_index(cList_tmp).index.isin(
                                            df_in_FullBOM.set_index(cList_tmp).index)].copy()
            
            df_Ext_Data[col_VersionVersionName] = VERSION_VALUE  # Version Name 변경
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            #df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            #print_df(df_Ext_Data, 'df_Ext_Data', False)
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOM_MFGPLAN':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # 생산계획 있으나 BOM 없음
            # SETMfgPlan에 있는 Item, Site, BOM Version이 SETBOM에 Item, Site 추출
            df_Ext_Data = df_in_SETMfgPlan_SFC[
                ~df_in_SETMfgPlan_SFC.set_index([col_ItemItem, col_LocationLocation, col_BOMInfoBOMVersion]).index.isin(
                    df_SETBOM.set_index([col_ItemItem, col_LocationLocation, col_BOMInfoBOMVersion]).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            # df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[
                col_ValidationFactor] = '-'  # BOM Version 그레인 추가됨.('BOM Version=' + df_Ext_Data[col_BOMInfoBOMVersion].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(SET)CTN':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Demand [Item].[Item] * [Location].[Location] 기준 On hand, Intraisit 차감 --> Sales Site 기준 ----------
            df_DemandW = df_in_DemandW.merge(df_in_WOnHand, on=clist_V_ITM_LOC, how='left')
            
            df_DemandW = df_DemandW.merge(df_in_WExp_Intransit, on=clist_V_ITM_LOC, how='left')
            del df_in_WExp_Intransit
            
            df_DemandW[col_WOnHandQuantity] = df_DemandW[col_WOnHandQuantity].fillna(0).astype('int64')
            df_DemandW[col_WExpectedReceipts] = df_DemandW[col_WExpectedReceipts].fillna(0).astype('int64')
            
            df_DemandW['cal_qty'] = df_DemandW[col_DmdW_Qty] - (df_DemandW[col_WOnHandQuantity] +
                                                                df_DemandW[col_WExpectedReceipts])  # 차감
            # print_df(df_DemandW, 'df_DemandW',False)
            
            # Demand [Item].[Item] 기준 Plant onhand 차감 ----------------------------------------------
            # Group by Item
            df_DemandW_item = df_DemandW.groupby([col_VersionVersionName, col_ItemItem],
                                                 as_index=False).agg({'cal_qty': 'sum'})
            
            # Plant onhand
            df_Plant_WOnHand = df_in_WOnHand[(df_in_WOnHand[col_LocationSiteStage].str.startswith('MF'))].copy()
            del df_in_WOnHand
            
            # Group by Item
            df_Plant_WOnHand[col_WOnHandQuantity] = df_Plant_WOnHand[col_WOnHandQuantity].fillna(0).astype('int64')
            df_Plant_WOnHand = df_Plant_WOnHand.groupby([col_VersionVersionName, col_ItemItem],
                                                        as_index=False).agg({col_WOnHandQuantity: 'sum'})
            df_DemandW_item = df_DemandW_item.merge(df_Plant_WOnHand, on=[col_VersionVersionName, col_ItemItem],
                                                    how='left')
            del df_Plant_WOnHand
            df_DemandW_item[col_WOnHandQuantity] = df_DemandW_item[col_WOnHandQuantity].fillna(0).astype('int64')
            df_DemandW_item['cal_qty'] = df_DemandW_item['cal_qty'].fillna(0).astype('int64')
            df_DemandW_item['last_Demand_qty'] = df_DemandW_item['cal_qty'] - df_DemandW_item[col_WOnHandQuantity]  # 차감
            df_DemandW_item.drop(columns=['cal_qty'], inplace=True)
            
            # 최종 Demand 수량 > CTN Item Const_Frozen SOP Override Qty ------------------------------------
            # ITEM 별 합계 수량
            df_in_CTN[col_CTNItemConst_FrozenSOPOverrideQty] = (
                df_in_CTN[col_CTNItemConst_FrozenSOPOverrideQty].fillna(0).astype('int64'))
            
            cList_group = [col_VersionVersionName, col_ItemItem]
            df_CTN = df_in_CTN.groupby(cList_group, as_index=False).agg({col_CTNItemConst_FrozenSOPOverrideQty: "sum"})
            del df_in_CTN
            # print_df(df_CTN, 'df_CTN',False)
            
            # Merge : df_DemandW_item & df_CTN            
            df_DemandW_item = df_DemandW_item.merge(df_CTN, on=[col_VersionVersionName, col_ItemItem], how='inner')
            del df_CTN
            df_DemandW_item[col_CTNItemConst_FrozenSOPOverrideQty] = (
                df_DemandW_item[col_CTNItemConst_FrozenSOPOverrideQty].fillna(0).astype('int64'))
            
            # 최종 Demand 수량 > CTN Item Const_Frozen SOP Override Qty
            df_DemandW_item['last_Demand_qty'] = df_DemandW_item['last_Demand_qty'].fillna(0).astype('int64')
            df_DemandW_item = (df_DemandW_item[df_DemandW_item['last_Demand_qty']
                                               > df_DemandW_item[col_CTNItemConst_FrozenSOPOverrideQty]])
            
            # print_df(df_DemandW_item, 'df_DemandW_item',False)
            
            # Merge df_DemandW & df_DemandW_item
            df_Ext_Data = df_DemandW.merge(df_DemandW_item, on=[col_VersionVersionName, col_ItemItem], how='inner')
            del [df_DemandW, df_DemandW_item]
            
            # print_df(df_Ext_Data, 'df_Ext_Data',False)
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (col_CTNItemConst_FrozenSOPOverrideQty + ' : ' +
                                                 df_Ext_Data[col_CTNItemConst_FrozenSOPOverrideQty].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # print_df(df_Ext_Data, '(SET)CTN',False) 
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
        
        elif row[col_MasterValidationValidationID] == '(SET)LOADING_MASTER_ERROR':  # ---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            #[Sub Location].[Sub Location]!="All"
            df_Loading_Mode_temp1 = df_in_LoadingMaster[df_in_LoadingMaster[col_SubLocationSubLocation] != 'All'].copy()
            #[Sub Location].[Sub Location]=="All"
            df_Loading_Mode_temp2 = df_in_LoadingMaster[df_in_LoadingMaster[col_SubLocationSubLocation] == 'All'].copy()
            del df_in_LoadingMaster
            #print_df(df_Loading_Mode_temp, 'df_Loading_Mode_temp 1', False)
            
            #df_in_SOPW[col_SubLocationSubLocation] = df_in_SOPW[col_ToLocationToLocation] #조인을 위해 SubLocation 갈럼 추가
            df_in_SOPW.rename(columns={col_ToLocationToLocation:col_SubLocationSubLocation}, inplace=True) #조인을 위해 칼럼명 변경
            
            now = datetime.datetime.now().replace(microsecond=0) # 초의 소수점 단위 자르기
            df_in_SOPW[col_LoadingMasterToSite_InitDttm].fillna(now, inplace=True)  # null은 now로
            df_in_SOPW[col_LoadingMasterToSite_UpDttm].fillna(now, inplace=True)  # null은 now로
            #print_df(df_in_SOPW, 'df_in_SOPW 2', False)
            
            cList_tmp1 = [col_VersionVersionName, col_LocationLocation, col_SubLocationSubLocation, 
                         col_TransModeTransMode, col_ItemItem]
            
            cList_tmp2 = [col_VersionVersionName, col_LocationLocation, col_TransModeTransMode, col_ItemItem]
            
            #① [Sub Location].[Sub Location]!=“All”인 df_in_LoadingMaster에서 df_in_SOPW에 있는 것만 추출 (Location, Sub Location(=To Location), Trans Mode, Item으로 조인)
            #② [Sub Location].[Sub Location]==“All”인 df_in_LoadingMaster에서 df_in_SOPW에 있는 것만 추출 (Location, Trans Mode, Item으로 조인)
            #②에서 ①에 없는 것만 추출하여 ①과 ②를 Concat 한다.            
            df_Loading_Mode_temp1 = df_Loading_Mode_temp1.merge(df_in_SOPW, on=cList_tmp1, how='inner',
                                                               suffixes=('', '_y'))
            #print_df(df_Loading_Mode_temp1, 'df_Loading_Mode_temp1', False)
            
            df_Loading_Mode_temp2 = df_Loading_Mode_temp2.merge(df_in_SOPW, on=cList_tmp2, how='inner', suffixes=('', '_y'))
            df_Loading_Mode_temp2 = df_Loading_Mode_temp2[~(df_Loading_Mode_temp2.set_index(cList_tmp1).index.isin(
                                                            df_Loading_Mode_temp1.set_index(cList_tmp1).index))]
            
            #print_df(df_Loading_Mode_temp2, 'df_Loading_Mode_temp2', False)
            
            df_Loading_Mode_temp = pd.concat([df_Loading_Mode_temp1, df_Loading_Mode_temp2])
            del [df_Loading_Mode_temp1, df_Loading_Mode_temp2]
            
            df_Loading_Mode_temp['Init_Up_Min'] = df_Loading_Mode_temp[
                [col_LoadingMasterToSite_InitDttm, col_LoadingMasterToSite_UpDttm]].min(axis=1) # Init/Up 빠른 날
            #print_df(df_Loading_Mode_temp, 'df_Loading_Mode_temp', True)
            
            def fn_MODE_SEL(a_col_Name, df_source: pd.DataFrame) -> pd.DataFrame:
                #df_Data = df_source.copy()
                df_Mode = pd.DataFrame([], columns=[])
                df_Mode[a_col_Name] = df_source[a_col_Name].mode()
                
                if df_Mode.shape[0] == 1:  # 1건이면
                    None
                    #note(f'=====> [{a_col_Name}] Mode CNT :  1 =======')
                else:
                    df_temp = df_source[
                        [a_col_Name,'Init_Up_Min']].groupby(
                        [a_col_Name],as_index=False)['Init_Up_Min'].min()
                    df_Mode = df_Mode.merge(df_temp, on=[a_col_Name], how='inner')            
                    df_Mode = df_Mode.sort_values(by=['Init_Up_Min', a_col_Name],
                                                      ascending=[True, False]).reset_index(drop=True)            
                    df_Mode['RN'] = 1
                    df_Mode['RN'] = df_Mode['RN'].cumsum()
                    #print_df(df_Mode, 'df_Mode', False)
                    df_Mode = df_Mode.loc[df_Mode['RN'] == 1, [a_col_Name]]
                
                return df_Mode
            
            #각 Measure별 최빈값을 산출하여 별도의 DF로 생성  -- 빈도가 높고, 가장 먼저 생성된 것이 우선순위 높음
            #※ Init Dttm/Up Dttm 포함 가장 빠른 날(null은 now로 간주) 
            #------------------------------------------------------------------------------------------
            df_Mode_FCL = fn_MODE_SEL(col_LMToSite_FCL, df_Loading_Mode_temp)
            #print_df(df_Mode_FCL, 'df_Mode_FCL', False)
            
            df_Mode_1st = fn_MODE_SEL(col_LMToSite_1stContainer, df_Loading_Mode_temp)
            #print_df(df_Mode_1st, 'df_Mode_1st', False)

            df_Mode_2nd = fn_MODE_SEL(col_LMToSite_2ndContainer, df_Loading_Mode_temp)
            #print_df(df_Mode_2nd, 'df_Mode_2nd', False)
            
            df_Mode_MaxLoadingRate = fn_MODE_SEL(col_LMToSite_MaxLoadingRate, df_Loading_Mode_temp)
            #print_df(df_Mode_MaxLoadingRate, 'df_Mode_MaxLoadingRate', False)
            
            df_Mode_MinLoadingRate = fn_MODE_SEL(col_LMToSite_MinLoadingRate, df_Loading_Mode_temp)
            #print_df(df_Mode_MinLoadingRate, 'df_Mode_MinLoadingRate', False)
            
            df_Mode_Period = fn_MODE_SEL(col_LMToSite_BldAhdPeriod, df_Loading_Mode_temp)
            #print_df(df_Mode_Period, 'df_Mode_Period', False)
            
            df_Mode_20FT = fn_MODE_SEL(col_LMToSite_20FTQty, df_Loading_Mode_temp)
            #print_df(df_Mode_20FT, 'df_Mode_20FT', False)
            
            df_Mode_40HC = fn_MODE_SEL(col_LMToSite_40HCQty, df_Loading_Mode_temp)
            #print_df(df_Mode_40HC, 'df_Mode_40HC', False)            
            #------------------------------------------------------------------------------------------
            
            df_Loading_Mode = pd.concat([df_Mode_FCL, df_Mode_1st, df_Mode_2nd, df_Mode_MaxLoadingRate, df_Mode_MinLoadingRate,
                                         df_Mode_Period, df_Mode_20FT, df_Mode_40HC], axis=1)
            
            df_Loading_Mode.rename(columns={col_LMToSite_FCL:'FCL',
                                            col_LMToSite_1stContainer:'1st_Container',
                                            col_LMToSite_2ndContainer:'2nd_Container',
                                            col_LMToSite_MaxLoadingRate:'Max_Loading_Rate',
                                            col_LMToSite_MinLoadingRate:'Min_Loading_Rate',
                                            col_LMToSite_BldAhdPeriod:'Build_Ahead_Period',
                                            col_LMToSite_20FTQty:'20FT_Qty',
                                            col_LMToSite_40HCQty:'40HC_Qty'}, inplace=True)
            #print_df(df_Loading_Mode, 'df_Loading_Mode', False)
            
            df_Loading_Mode = df_Loading_Mode_temp.merge(df_Loading_Mode, how='cross')

            #df_Loading_Mode의 Location에서 P63A,P638 제외 #'CreateLED','RETOP' 는 LED Sinage JDM공급처로 validation대상에서 제외
            df_Loading_Mode = df_Loading_Mode[~df_Loading_Mode[col_LocationLocation].isin(['P63A', 'P638'])]
            

            #df_in_SOPW에 존재하는 것만 추출
            df_Loading_Mode = df_Loading_Mode[(df_Loading_Mode.set_index(cList_tmp1).index.isin(
                                               df_in_SOPW.set_index(cList_tmp1).index))].copy()
            del df_in_SOPW
            
            # df_in_SETItemSite에 있는 것만.            
            cList_tmp3 = [col_VersionVersionName, col_LocationLocation, col_ItemItem]
            df_Loading_Mode = df_Loading_Mode[(df_Loading_Mode.set_index(cList_tmp3).index.isin(
                                               df_in_SETItemSite.set_index(cList_tmp3).index))].copy()
            #print_df(df_Loading_Mode, 'df_Loading_Mode', False)
            
            # 추출 1 : df_Loading_Mode과 df_in_LoadingMaster가 상이한 데이터 추출, df_in_SETItemSite에 있는 것만. #########
            # df_Loading_Mode 값과 1개라도 다른것 추출
            df_Ext_Data1 = df_Loading_Mode[
              ~((df_Loading_Mode[col_LMToSite_FCL] == df_Loading_Mode['FCL']) &
                (df_Loading_Mode[col_LMToSite_1stContainer] == df_Loading_Mode['1st_Container']) &
                (df_Loading_Mode[col_LMToSite_2ndContainer] == df_Loading_Mode['2nd_Container']) &
                (df_Loading_Mode[col_LMToSite_MaxLoadingRate] == df_Loading_Mode['Max_Loading_Rate']) &
                (df_Loading_Mode[col_LMToSite_MinLoadingRate] == df_Loading_Mode['Min_Loading_Rate']) &
                (df_Loading_Mode[col_LMToSite_BldAhdPeriod] == df_Loading_Mode['Build_Ahead_Period']) &
                (df_Loading_Mode[col_LMToSite_20FTQty] == df_Loading_Mode['20FT_Qty']) &
                (df_Loading_Mode[col_LMToSite_40HCQty] == df_Loading_Mode['40HC_Qty']))
            ]
            
            if df_Ext_Data1.empty:
                df_Ext_Data1 = pd.DataFrame(columns=clist_all)
            else :
                df_Ext_Data1[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                #df_Ext_Data1[col_ItemItem] = '-'
                #df_Ext_Data1[col_LocationLocation] = '-'
                #df_Ext_Data1[col_SubLocationSubLocation] = '-'
                #df_Ext_Data1[col_TransModeTransMode] = '-'
                df_Ext_Data1[col_BOMInfoBOMVersion] = '-'
                df_Ext_Data1[col_LineLine] = '-'
                df_Ext_Data1[col_SalesDomainAP2] = '-'
                df_Ext_Data1[col_ValidationFactor] = ('최빈값/마스터 – FCL (' + 
                                  df_Ext_Data1['FCL'].astype('str') +'/'+ 
                                  df_Ext_Data1[col_LMToSite_FCL].astype('str') + '), 1st Container  (' +
                                  df_Ext_Data1['1st_Container'].astype('str') +'/'+
                                  df_Ext_Data1[col_LMToSite_1stContainer].astype('str') + '), 2nd Container  (' +
                                  df_Ext_Data1['2nd_Container'].astype('str') +'/'+
                                  df_Ext_Data1[col_LMToSite_2ndContainer].astype('str') + '), Max Loading Rate  (' +
                                  df_Ext_Data1['Max_Loading_Rate'].astype('str') + '/' +
                                  df_Ext_Data1[col_LMToSite_MaxLoadingRate].astype('str')+ '), Min Loading Rate  (' +
                                  df_Ext_Data1['Min_Loading_Rate'].astype('str') + '/' +
                                  df_Ext_Data1[col_LMToSite_MinLoadingRate].astype('str') + '), Build Ahead Period  (' +
                                  df_Ext_Data1['Build_Ahead_Period'].astype('str') + '/' +
                                  df_Ext_Data1[col_LMToSite_BldAhdPeriod].astype('str') + ')'
                                  )
                #최빈값/마스터 – FCL ( ../.. ), 1st Container  ( ../.. ), 2nd Container ( ../.. ), Max Loading Rate ( ../.. ), Min Loading Rate ( ../.. ), Build Ahead Period ( ../.. )
            
            df_Ext_Data1 = df_Ext_Data1[clist_all]    
            df_Ext_Data1.drop_duplicates(inplace=True)
            #print_df(df_Ext_Data1, 'df_Ext_Data1', False)            
            
            # 추출 2 : df_Loading_Mode에서 20FT Qty, 40HC Qty가 0인 데이터 추출, df_in_SETItemSite에 있는 것만. #########
            df_Ext_Data2 = df_Loading_Mode[(df_Loading_Mode['20FT_Qty'] == 0) |
                                           (df_Loading_Mode['40HC_Qty'] == 0)]
            del df_Loading_Mode
            
            if df_Ext_Data2.empty:
                df_Ext_Data2 = pd.DataFrame(columns=clist_all)
            else :
                df_Ext_Data2[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                #df_Ext_Data2[col_ItemItem] = '-'
                #df_Ext_Data2[col_LocationLocation] = '-'
                #df_Ext_Data2[col_SubLocationSubLocation] = '-'
                #df_Ext_Data2[col_TransModeTransMode] = '-'
                df_Ext_Data2[col_BOMInfoBOMVersion] = '-'
                df_Ext_Data2[col_LineLine] = '-'
                df_Ext_Data2[col_SalesDomainAP2] = '-'
                df_Ext_Data2[col_ValidationFactor] = ('최빈값 20FT Qty ('+ 
                                                     df_Ext_Data2['20FT_Qty'].astype('str') +'), 40HC Qty (' + 
                                                     df_Ext_Data2['40HC_Qty'].astype('str') + ')'
                                                     )
            
            # 칼럼정리
            df_Ext_Data2 = df_Ext_Data2[clist_all]            
            df_Ext_Data2.drop_duplicates(inplace=True)
            #print_df(df_Ext_Data2, 'df_Ext_Data2', False)
            
            df_Vld_Result_TMP = pd.concat([df_Ext_Data1, df_Ext_Data2])
            #df_Vld_Result_TMP = df_Ext_Data2.copy() # 임시
            del [df_Ext_Data1, df_Ext_Data2]
        
        elif row[col_MasterValidationValidationID] == '(SET)MP_SRA_DATE':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Max 말고 Category Actual인걸로 처리
            df_NewModel = df_in_NewModel.copy()
            df_NewModel.rename(columns={col_ItemNewModelItem: col_ItemItem}, inplace=True)
            df_NewModel['valeue'] = np.where((df_NewModel[col_CategoryCategory] == 'Actual'), 1, 2)
            
            df_NewModel['rn'] = df_NewModel.groupby(
                clist_V_ITM_LOC, as_index=False)['valeue'].rank(method='first', ascending=True).astype('int64')
            df_NewModel = df_NewModel[df_NewModel['rn'] == 1]
            # print_df(df_NewModel, 'df_NewModel',False)
            
            #  [Location].[Site Stage].filter(#.Name startswith "MF")
            df_Ext_Data = df_in_PLCMfg[(df_in_PLCMfg[col_LocationSiteStage].str.startswith('MF'))].copy()
            # Merge 
            df_Ext_Data = df_Ext_Data.merge(df_NewModel, on=clist_V_ITM_LOC, how='inner')
            del df_NewModel
            # [PLC Mfg_SRA FW Limit Date] > [New Model_Mfg Date]
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_PLCMfg_SRAFWLimitDate].notna() &
                                      df_Ext_Data[col_NewModel_MfgDate].notna() &
                                      (df_Ext_Data[col_PLCMfg_SRAFWLimitDate] > df_Ext_Data[col_NewModel_MfgDate])]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            # df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'PLC Mfg_SRA FW Limit Date = ' + df_Ext_Data[col_PLCMfg_SRAFWLimitDate].dt.date.astype('str') +
                ', New Model_Mfg Date = ' + df_Ext_Data[col_NewModel_MfgDate].dt.date.astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
        
        elif row[col_MasterValidationValidationID] == '(SET)MULTI_BOD':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # MULTI_BOD 처리 함수 호출 (df_in_SETBOD)
            df_Vld_Result_TMP = fn_MULTI_BOD(row[col_MasterValidationValidationID], df_in_SETBOD)
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP', False)
        
        elif row[col_MasterValidationValidationID] == '(SET)MULTI_CONST_GROUP':  # ---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Const Grp Ecp : [Item].[Item] * [Group].[Group ID] 기준 Count > 1
            df_Ext_Data = df_in_SETConstGrpEcp[[col_VersionVersionName, col_ItemItem, col_GroupGroupID]].copy()
            del df_in_SETConstGrpEcp
            df_Ext_Data['Chk_Value'] = 0
            df_Ext_Data['Chk_Value'] = df_Ext_Data.groupby([col_VersionVersionName,
                                                            col_ItemItem])[col_GroupGroupID].transform('nunique')  # count(distinct)
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] > 1]  # [Item].[Item] 기준  [Group].[Group ID]  Count > 1
            
            if df_Ext_Data.empty:
                None
            else:
                df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem],
                                                  as_index=False)[col_GroupGroupID].agg(lambda x: ', '.join(set(x)))
                
                df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                # df_Ext_Data[col_ItemItem] = '-'
                df_Ext_Data[col_LocationLocation] = '-'
                df_Ext_Data[col_SubLocationSubLocation] = '-'
                df_Ext_Data[col_TransModeTransMode] = '-'
                df_Ext_Data[col_BOMInfoBOMVersion] = '-'
                df_Ext_Data[col_LineLine] = '-'
                df_Ext_Data[col_SalesDomainAP2] = '-'
                df_Ext_Data[col_ValidationFactor] = 'Group ID : ' + df_Ext_Data[col_GroupGroupID]
                
                # 칼럼정리
                df_Ext_Data = df_Ext_Data[clist_all]
                df_Ext_Data.drop_duplicates(inplace=True)
                
                df_Vld_Result_TMP = df_Ext_Data.copy()
            
            del df_Ext_Data
        
        elif row[col_MasterValidationValidationID] == '(SET)MULTI_FIX_GROUP':  # ---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Const Grp Ecp : [Item].[Item] * [Group].[Group ID] 기준 Count > 1
            df_Ext_Data = df_in_SOPFrozen.copy()
            
            # 칼럼을 구분자(^)로 분리 후 explode() : 문자열을 구분자로 분리하여 행으로 변환.
            df_Ext_Data[col_SOPFrozen_Item] = df_Ext_Data[col_SOPFrozen_Item].str.split('^')
            df_Ext_Data = df_Ext_Data.explode(col_SOPFrozen_Item).reset_index(drop=True)
            
            # SET Item 대상
            df_Ext_Data = df_Ext_Data[df_Ext_Data.set_index([col_SOPFrozen_Item]).index.isin(
                df_in_SETItem.set_index([col_ItemItem]).index)].copy()
            del df_in_SETItem
            df_Ext_Data['Chk_Value'] = 0
            df_Ext_Data['Chk_Value'] = df_Ext_Data.groupby([col_VersionVersionName, col_SOPFrozen_FromSite,
                                                            col_SOPFrozen_Item])[col_GroupGroupID].transform('count')
            # From Site & 분리된 Item 기준 [Group].[Group ID] Count > 1
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] > 1]
            df_Ext_Data.rename(columns={col_SOPFrozen_FromSite: col_LocationLocation, col_SOPFrozen_Item: col_ItemItem},
                               inplace=True)
            
            if df_Ext_Data.empty:
                None
            else:
                df_Ext_Data['GroupID_SET'] = df_Ext_Data[col_GroupGroupID]
                df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC,
                                                  as_index=False)['GroupID_SET'].agg(lambda x: ', '.join(set(x)))
                
                df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                # df_Ext_Data[col_ItemItem] = '-'
                # df_Ext_Data[col_LocationLocation] = '-'
                df_Ext_Data[col_SubLocationSubLocation] = '-'
                df_Ext_Data[col_TransModeTransMode] = '-'
                df_Ext_Data[col_BOMInfoBOMVersion] = '-'
                df_Ext_Data[col_LineLine] = '-'
                df_Ext_Data[col_SalesDomainAP2] = '-'
                df_Ext_Data[col_ValidationFactor] = 'Group ID : ' + df_Ext_Data['GroupID_SET']
                
                # 칼럼정리
                df_Ext_Data = df_Ext_Data[clist_all]
                df_Ext_Data.drop_duplicates(inplace=True)
                
                df_Vld_Result_TMP = df_Ext_Data.copy()
            
            del df_Ext_Data
            
        elif row[col_MasterValidationValidationID] == '(SET)NO_LINE_MASTER':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item 대상으로
            df_Ext_Data = df_in_SETTactTime[df_in_SETTactTime.set_index([col_ItemItem]).index.isin(
                df_in_SETDemand.set_index([col_ItemItem]).index)
            ].copy()
            df_Ext_Data = df_Ext_Data[[col_VersionVersionName, col_LocationLocation, col_LineLine]]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # SETWorkCalLine(Work Cal Line_Time > 0)
            df_WorkCalLine = df_in_SETWorkCalLine[df_in_SETWorkCalLine[col_WorkCalLine_Time] > 0]
            # print_df(df_WorkCalLine, 'df_WorkCalLine',False)
            
            # SETWorkCalLine(Work Cal Line_Time > 0) 에 없는 Site, Line 추출
            df_Ext_Data = df_Ext_Data[~df_Ext_Data.set_index([col_LineLine]).index.isin(
                df_WorkCalLine.set_index([col_LineLine]).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            # df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(SET)PLANNED_EOL':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand : Version.[Version Name], Item.[Item], Time.[Week], Location.[Location]
            # SETPLCSales : Version.[Version Name], Item.[Item], Sales Domain.[AP2]
            df_Ext_Data = df_in_SETPLCSales.merge(df_in_SETDemand, on=[col_VersionVersionName, col_ItemItem]
                                                  , how='inner', suffixes=('', '_y'))
            # Ext_Data 칼럼정리
            df_Ext_Data = df_Ext_Data[[col_VersionVersionName, col_ItemItem, col_LocationLocation
                , col_SalesDomainAP2, col_TimeWeek, col_PLCSales_EOSComDate]]
            
            df_Ext_Data.drop_duplicates(inplace=True)
            # SETDemand.[Time].[Week] > PLC Sales_EOS Com Date :  PLC Sales_EOS Com Date 의 Week 정보 필요.
            # Merge : df_Ext_Data & df_in_Time
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_PLCSales_EOSComDate], right_on=[col_TimeDay]
                                            , how='inner', suffixes=('', '_y'))
            df_Ext_Data.rename(columns={col_TimeWeek + '_y': col_EOSComWeek}, inplace=True)
            
            df_Ext_Data = df_Ext_Data.astype({col_TimeWeek: 'int64', col_EOSComWeek: 'int64'}, copy=True)
            
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_TimeWeek] > df_Ext_Data[col_EOSComWeek])]
            
            # group by : Version.[Version Name], Item.[Item], Location.[Location], Sales Domain.[AP2]
            df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation
                                                  , col_SalesDomainAP2, col_EOSComWeek],
                                              as_index=False).agg({col_TimeWeek: 'max'
                                                                   # , col_EOSComWeek:'max'
                                                                   })
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            # df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'EOS Com Week = ' + df_Ext_Data[col_EOSComWeek].astype('str') +
                ', Max(Demand Due Week) = ' + df_Ext_Data[col_TimeWeek].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOD_DEMAND':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Demand.[Item].[Item] == Fullbom.[Item].[Item] 
            # --> Fullbom.[To Item].[To Item], Fullbom.[To Location].[To Location], Fullbom.[Location].[Location]
            df_Ext_Data = df_in_Fullbom_LCM[df_in_Fullbom_LCM.set_index([col_ItemItem]).index.isin(
                df_in_DemandW.set_index([col_ItemItem]).index)].copy()
            
            # Fullbom.[To Item].[To Item] ==  BOD.[Item].[Item]
            # Fullbom.[To Location].[To Location] == BOD.[Location].[Location] 
            # Fullbom.[Location].[Location] == BOD.[Sub Location].[Sub Location]
            # --> BOD 기준 데이터 없음
            df_Ext_Data.rename(columns={col_ItemItem: 'Item.[Item]_ORG',
                                        col_ToItemToItem: col_ItemItem,
                                        col_LocationLocation: col_SubLocationSubLocation,
                                        col_ToLocationToLocation: col_LocationLocation}, inplace=True)
            
            # df_in_LCMBOD : BOD 기준 데이터 없음
            df_Ext_Data = df_Ext_Data[~df_Ext_Data.set_index(clist_V_ITM_LOC_Sub).index.isin(
                df_in_LCMBOD.set_index(clist_V_ITM_LOC_Sub).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOD_EFFECTIVENESS':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # >> 날짜 체크 로직은 삭제하고
            # >> df_in_LCMBOD 가 매치가 되지 않는 것을 찾는 로직으로 변경 (2026.02.09)
            
            # Demand.[Item].[Item] == Fullbom.[Item].[Item] 
            # --> Fullbom.[To Item].[To Item], Fullbom.[To Location].[To Location], Fullbom.[Location].[Location]
            df_Ext_Data = df_in_Fullbom_LCM[df_in_Fullbom_LCM.set_index([col_ItemItem]).index.isin(
                df_in_DemandW.set_index([col_ItemItem]).index)].copy()
            
            # Fullbom.[To Item].[To Item] ==  BOD.[Item].[Item]
            # Fullbom.[To Location].[To Location] == BOD.[Location].[Location] 
            # Fullbom.[Location].[Location] == BOD.[Sub Location].[Sub Location]            
            
            #df_in_LCMBOD 가 매치가 되지 않는 것을 찾음.
            cList_bom =  [col_VersionVersionName,col_ToItemToItem,col_ToLocationToLocation,col_LocationLocation]
            clist_bod =  [col_VersionVersionName,col_ItemItem,    col_LocationLocation,    col_SubLocationSubLocation]
            
            df_Ext_Data = df_Ext_Data[~df_Ext_Data.set_index(cList_bom).index.isin(
                                       df_in_LCMBOD.set_index(clist_bod).index)].copy()
                        
            # megge : df_in_PlanHorizon
            df_Ext_Data = df_Ext_Data.merge(df_in_PlanHorizon, on=[col_VersionVersionName], how='inner')
            #print_df(df_Ext_Data, 'df_Ext_Data', False)
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            #df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOD_LT_GAP':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #>> df_in_LCMBOD 와 df_in_LCMBODList 를 Merge한 후 [LCM BOD List_Transit Time] <> [BOD Item_BOD LT] or [LCM BOD List_Shipment LT] <> [BOD Item_Shipment LT] 인 BOD Item 정보
            #>> Version Name, Validation ID, Location, Sub Location, Item, Trans Mode, Validation Factor 만 설정, 나머지는 ‘-’
            # Validation Factor = "LCM BOD List([LCM BOD List_Transit Time], [LCM BOD List_Shipment LT]) vs BOD Item ([BOD Item_BOD LT], [BOD Item_Shipment LT])"

            cList_tmp = [col_VersionVersionName, col_LocationLocation, col_ItemClassCategory,
                         col_SubLocationSubLocation, col_TransModeTransMode]
            
            df_Ext_Data = df_in_LCMBOD.merge(df_in_LCMBODList, on=cList_tmp, how='inner', suffixes=('', '_y'))
            
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_LCMBODList_TransitTime] != df_Ext_Data[col_BODItem_BODLT]) |
                                      (df_Ext_Data[col_LCMBODList_ShipmentLT] != df_Ext_Data[col_BODItem_ShipmentLT])]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            #df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = ('LCM BOD List(' +
                                                 df_Ext_Data[col_LCMBODList_TransitTime].astype('str') + ', ' +
                                                 df_Ext_Data[col_LCMBODList_ShipmentLT].astype('str') + ') vs BOD Item (' +
                                                 df_Ext_Data[col_BODItem_BODLT].astype('str') + ', ' +
                                                 df_Ext_Data[col_BODItem_ShipmentLT].astype('str') + ')'
                                                 )
            
            # print_df(df_Ext_Data, 'df_Ext_Data', False)
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)   
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOD_MFGPLAN':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # MFGPlan.[Item].[Item] == BOD.[Item].[Item]
            # MFGPlan.[Location].[Location] == BOD.[Location].[Location]
            df_Ext_Data = df_in_LCMBOD[df_in_LCMBOD.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                df_in_MFGPlan_LCM.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            
            # megge : df_in_PlanHorizon
            df_Ext_Data = df_Ext_Data.merge(df_in_PlanHorizon, on=[col_VersionVersionName], how='inner')
            
            # megge : df_in_Time : EffStartWeek :주 정보를 가져오기 위해
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_BODItem_EffStartdate], right_on=[col_TimeDay],
                                            how='left')
            df_Ext_Data.rename(columns={col_TimeWeek: col_EffStartWeek}, inplace=True)
            df_Ext_Data.drop(columns=[col_TimeDay], inplace=True)
            
            # megge : df_in_Time : EffEndWeek :주 정보를 가져오기 위해
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_BODItem_EffEnddate], right_on=[col_TimeDay],
                                            how='left')
            df_Ext_Data.rename(columns={col_TimeWeek: col_EffEndWeek}, inplace=True)
            df_Ext_Data.drop(columns=[col_TimeDay], inplace=True)
            
            # megge : df_Time_Min_Max
            df_Ext_Data['Dummy'] = 'A'
            df_Ext_Data = df_Ext_Data.merge(df_Time_Min_Max, on=['Dummy'], how='inner')
            
            # EffEnddate > PlanHorizonStartWeek && EffStartdate < PlanHorizonEndWeek
            df_Ext_Data['Chk_Value'] = np.where(
                (df_Ext_Data[col_BODItem_EffEnddate].isna() |
                 (df_Ext_Data[col_BODItem_EffEnddate] > df_Ext_Data['Max_Day']) |
                 (df_Ext_Data[col_EffEndWeek] >= df_Ext_Data[col_PlanHorizonStartWeek])) &
                (df_Ext_Data[col_BODItem_EffStartdate].isna() |
                 (df_Ext_Data[col_BODItem_EffStartdate] < df_Ext_Data['Min_Day']) |
                 (df_Ext_Data[col_EffStartWeek] <= df_Ext_Data[col_PlanHorizonEndWeek]))
                , 1, 0)
            # print_df(df_Ext_Data, 'df_Ext_Data',False,False)
            # Horizon 기준 Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Eff Enddate]가 겹치는 구간이 없을 경우
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] == 0]  # 결과가 0 인 Item
            # print_df(df_Ext_Data, 'df_Ext_Data',False)
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOM_MFGPLAN':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # MFGPlan.[Item].[Item] == Fullbom.[To Item].[To Item] & MFGPlan.[Location].[Location] == Fullbom.[To Location].[To Location]
            # --> Fullbom 기준 데이터 없을 경우
            df_Ext_Data = df_in_MFGPlan_LCM[
                ~df_in_MFGPlan_LCM.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                    df_in_Fullbom_LCM.set_index([col_ToItemToItem, col_ToLocationToLocation]).index)].copy()
            
            df_Ext_Data[col_MfgPlan_Qty] = df_Ext_Data[col_MfgPlan_Qty].fillna(0).astype('int64')
            df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                              as_index=False).agg({col_MfgPlan_Qty: 'sum'}, skipna=True)
            
            # print_df(df_Ext_Data, 'df_Ext_Data', False)
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = 'MFG Plan Quantity = ' + df_Ext_Data[col_MfgPlan_Qty].astype('str')
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)MULTI_BOD':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # MULTI_BOD 처리 함수 호출 (df_in_LCMBOD)
            df_Vld_Result_TMP = fn_MULTI_BOD(row[col_MasterValidationValidationID], df_in_LCMBOD)
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP', False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)MULTI_FIX_GROUP':  # ---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Const Grp Ecp : [Item].[Item] * [Group].[Group ID] 기준 Count > 1
            df_Ext_Data = df_in_SOPFrozen.copy()
            
            # 칼럼을 구분자(^)로 분리 후 explode() : 문자열을 구분자로 분리하여 행으로 변환.
            df_Ext_Data[col_SOPFrozen_Item] = df_Ext_Data[col_SOPFrozen_Item].str.split('^')
            df_Ext_Data = df_Ext_Data.explode(col_SOPFrozen_Item).reset_index(drop=True)
            
            # LCM Item 대상
            df_Ext_Data = df_Ext_Data[df_Ext_Data.set_index([col_SOPFrozen_Item]).index.isin(
                df_in_LCMItem.set_index([col_ItemItem]).index)].copy()
            del df_in_LCMItem
            df_Ext_Data['Chk_Value'] = 0
            df_Ext_Data['Chk_Value'] = df_Ext_Data.groupby([col_VersionVersionName, col_SOPFrozen_FromSite,
                                                            col_SOPFrozen_Item])[col_GroupGroupID].transform('count')
            # From Site & 분리된 Item 기준 [Group].[Group ID] Count > 1
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] > 1]
            df_Ext_Data.rename(columns={col_SOPFrozen_FromSite: col_LocationLocation, col_SOPFrozen_Item: col_ItemItem},
                               inplace=True)
            
            if df_Ext_Data.empty:
                None
            else:
                df_Ext_Data['GroupID_SET'] = df_Ext_Data[col_GroupGroupID]
                df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC,
                                                  as_index=False)['GroupID_SET'].agg(lambda x: ', '.join(set(x)))
                
                df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                # df_Ext_Data[col_ItemItem] = '-'
                # df_Ext_Data[col_LocationLocation] = '-'
                df_Ext_Data[col_SubLocationSubLocation] = '-'
                df_Ext_Data[col_TransModeTransMode] = '-'
                df_Ext_Data[col_BOMInfoBOMVersion] = '-'
                df_Ext_Data[col_LineLine] = '-'
                df_Ext_Data[col_SalesDomainAP2] = '-'
                df_Ext_Data[col_ValidationFactor] = 'Group ID : ' + df_Ext_Data['GroupID_SET']
                
                # 칼럼정리
                df_Ext_Data = df_Ext_Data[clist_all]
                df_Ext_Data.drop_duplicates(inplace=True)
                
                df_Vld_Result_TMP = df_Ext_Data.copy()
            
            del df_Ext_Data
            
            # if End -------------------------------------------------------------------------------------------------
        
        # row_count, col_count = df_Vld_Result_TMP.shape
        # note(f'=====> {row[col_MasterValidationValidationID]} : rows : {row_count}   ')
        
        # 처리 대상 ValidationID 만 결과건수 출력
        if CHK_I == 1:
            row_count, col_count = df_Vld_Result_TMP.shape
            note(f'=====> {row[col_MasterValidationValidationID]} : rows : {row_count}   ')
        
        if df_Vld_Result_TMP.empty:
            None
        else:
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)            
            if df_Vld_Result_All.empty:
                df_Vld_Result_All = df_Vld_Result_TMP.copy()
            else:
                df_Vld_Result_All = pd.concat([df_Vld_Result_All, df_Vld_Result_TMP])
        
        del df_Vld_Result_TMP
    
    del [df_in_MasterValidation, df_in_SETItemSite, df_in_LCMItemSite, df_in_LCMDemand, df_in_SETMfgPlan_SFC, 
         df_SETBOM, df_in_PlanHorizon, df_in_Time, df_in_SETBOD, df_in_LCMBOD, df_in_SOPFrozen, df_in_SETTactTime, 
         df_in_SETWorkCalLine, df_in_SETBuildAheadCalW, df_in_SETPLCSales, df_SETBuildAheadCalW_Demand_Sub_Loc, 
         df_in_DemandW, df_in_PLCMfg, df_in_NewModel, df_in_Fullbom_LCM, df_in_MFGPlan_LCM]
    
    note(f'=====> for End ======================================================= ')
    
    # print_df(df_Vld_Result_All, 'df_Vld_Result_All',False)
    step('=====> STEP 1-2 : Validate data Create End')
    
    ################################################################################################################
    # STEP 2 : MG: [Mst Valid Result] : output table create
    ################################################################################################################
    step('=====> STEP 2 : Final output table create')
    
    # out Data 생성 :
    df_out_MstValidResult = df_Vld_Result_All.copy()
    df_out_MstValidResult.drop_duplicates(inplace=True)
    del df_Vld_Result_All
    
    # 버전 처리 :
    # df_out_MstValidResult[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_MstValidResult.shape
    note(f'=====> Final df_out_MstValidResult rows : {row_count}, column : {col_count}')
    print_df(df_out_MstValidResult, 'df_out_MstValidResult', False)
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_MstValidResult, 'df_out_MstValidResult')
    
    step('=====> STEP 2-1 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_MstValidResult = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(
        f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()
