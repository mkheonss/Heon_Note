"""
* 프로그램명 
    - PY_MG_MasterValidation

* 내용
    - Master Validation Data 구성

* 변경이력
    - 2024.11.12 / 양희영 / Create
    - 2025.12.08 / 양희영 / Update2


* Flow Summary
    
* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함
    - 삭제 paramLastVersion : 202403_M :임시 test용 값
* Input Tables
    - df_in_MasterValidation : Dimension : Master Validation
                               select ([Master Validation].[Validation Stage] * [Master Validation].[Validation Grp01] * [Master Validation].[Validation Grp02] * [Master Validation].[Validation Type] * 
                               [Master Validation].[Validation Owner] * [Master Validation].[Validation ID] * [Master Validation].[Validation Name]) 
                               on row include memberproperties  {[Master Validation].[Validation ID],[Validation ID Desc]} {[Master Validation].[Validation Name],[Validation Name Desc]};
    - df_in_ItemSite : df_in_SETItemSite, df_in_LCMItemSite 대체
                       select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] ) on row, 
                       ({Measure.[Item Site Asn_Cur Status]}) on column where {Measure.[Item Site Asn_Cur Status] IN {"ACTIVE", "PLANNED"}};
    - df_in_Intransit : 2개버전 SCOPE
                        Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location]) on row, 
                        ({Measure.[Intr_From Site ID], Measure.[Intr_Qty], Measure.[Dummy]}) on column;
    - df_in_Demand : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Time].[Week] * [Location].[Location] * 
                     [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, 
                     ({Measure.[W Demand Priority], Measure.[W Demand Quantity to SCS], Measure.[W DumDemand Quantity to SCS], Measure.[Dummy]}) on column;
    - df_in_Inventory : 2개버전 SCOPE
                        Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Time].[Week] * 
                        [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv_KRW Amount], Measure.[Inv_Plan ID], Measure.[Inv_Qty], Measure.[Inv_Sales ID], Measure.[Inv_To Site], 
                        Measure.[Inv_USD Amount]}) on column;
    - df_in_MfgPlan_SOPFPCmp : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Time].[Week] * 
                               [Location].[Location] * [To Item].[To Item] * [BOM Info].[BOM Version] ) on row, ({Measure.[SOP FP Compare_SOP Qty], Measure.[Dummy]}) on column;
    - df_in_BOM : Select (&CWVUI * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], 
                  Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column;
    - df_in_Time : Select ([Time].[Week] * [Time].[Day]);
    - df_in_PlanHorizon : Select (&CWVUI) on row, ({Measure.[MP Plan Current Week], Measure.[MP Plan End Date], Measure.[MP Plan End Week], Measure.[MP Plan Start Date], Measure.[MP Plan Start Week]}) on column;
    - df_in_CurrentDay : Select (&CurrentDay);
    - df_in_BOD : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] * 
                  [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                  ({Measure.[BOD Item_Asn], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Priority], Measure.[Dummy]}) on column;
    - df_in_BODW : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * &PlanningHorizon * 
                   [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                   ({Measure.[BOD Item W_Prty], Measure.[BOD Item W_Prty Duplicated Flag], Measure.[BOD Item W_Shipment LT], Measure.[BOD Item W_BOD LT], Measure.[Dummy]}) on column;
    - df_in_TactTime : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] * [Line].[Line] ) on row, 
                       ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn], Measure.[Dummy]}) on column;
    - df_in_WorkCalLine : Select (&CWVUI * [Time].[Week] * [Location].[Location] * [Location].[MF Site Stage].filter(#.Name == "SET" || #.Name contains "LCM") * [Work Type].[Work Type] * 
                         [Line].[Line] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column;
    - df_in_SETBuildAheadCalW : MG : Build Ahead Cal W
                             Select (&CWVUI * [Item].[Item] * [Item].[Plan Group] * [Item].[Product Group] * &PlanningHorizon * [Location].[Location] * [Location].[Shipment Type] * 
                             [Sales Domain].[AP2] * [Sub Location].[Sub Location] ) on row, ({Measure.[Build Ahead Cal W_Period]}) on column;
    - df_in_LCMSS : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].[LCM] * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] ) on row, 
                    ({Measure.[SS_SS Type], Measure.[SS_Valid Flag]}) on column where {Measure.[SS_Valid Flag] == "Y"};
    - df_in_SSW : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * &PlanningHorizon * 
                  [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[SS W_SS Target]}) on column;
    - df_in_SETPLCSales : MG : PLC Sales
                        Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].[SET] * [Item].[Plan Group] * [Item].[Product Group] * [Sales Domain].[AP2] ) on row, 
                        ({Measure.[PLC Sales_RTS Com Date], Measure.[PLC Sales_RTS FW Limit Date], Measure.[PLC Sales_EOS Com Date]}) on column;
    - df_in_PLCMfg : Select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] * [Location].[Site Stage] ) on row, 
                     ({Measure.[PLC Mfg_SRA Com Date], Measure.[PLC Mfg_SRA FW Limit Date]}) on column;
    - df_in_ConstGrpEcp : MG : Constraint Group Ecp
                       Select (&CWVUI *  [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Group].[Group ID] ) on row, 
                       ({Measure.[Const Grp Ecp_Flag]}) on column where {Measure.[Const Grp Ecp_Flag] != "Y"};
    - df_in_SOPFrozen : MG : SOP Frozen
                        Select (&CWVUI * [Group].[Group ID] ) on row, ({Measure.[SOP Frozen_From Site], Measure.[SOP Frozen_Item]}) 
                        on column where {Measure.[SOP Frozen_Item] != "All" && Measure.[SOP Frozen_Valid Flag] == "Y"};
    - df_in_DemandW : MG : Demand W
                      Select (&CWVUI * [Item].[Item] * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] ) on row, ({Measure.[Dmd W_Qty]}) on column;
    - df_in_WOnHand : MG : 001.020W Solver Inputs Inventory Inputs By OrderLine ID
                      Select (&CWVUI * [Item].[Item Stage].[SET].relatedmembers([Item]) * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] * [Location].[Site Stage]) on row, 
                      ({Measure.[W OnHand Quantity]}) on column;
    - df_in_WExp_Intransit : MG : 001.020W Solver Inputs Inventory Inputs By OrderLine ID
                            Select (&CWVUI * [Item].[Item] * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] ) on row, ({Measure.[W Expected Receipts]}) on column;
    - df_in_CTN : MG : CTN Item Const
                 Select (&CWVUI * [Item].[Item] * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Frozen SOP Override Qty]}) on column;
    - df_in_NewModel : Select (&CWVUI * [Location].[Location] * [Sales Domain].[AP2] * [Category].[Category] * [Item New Model].[Item] ) on row, ({Measure.[New Model_Mfg Date]}) on column;
    - df_in_MFGPlan_LCM : Select (&CWVUI * [Item].[Item] * [Item].[Plan Group] * [Item].[Product Group] * Item.[Item Stage].[LCM] * [Location].[Location] * [Documents].[OrderlineID] ) on row, 
                          ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Open Qty], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_To Site ID]}) on column;
    - df_in_Fullbom_LCM : Select (&CWVUI * [Item].[Item] * [Item].[Plan Group] * [Item].[Product Group] * [To Location].[To Location] * [To Item].[To Item] * [To Item].[To Item Stage].[LCM] * 
                          [Location].[Location] * [Item Material].[MSL3].filter(#.Name endswith "OpenCell").relatedmembers([Item Material]) * [BOM Info].[BOM Version] * [Status].[Status] * 
                          [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, ({Measure.[Full BOM_Eff Enddate], Measure.[Full BOM_Eff Startdate], Measure.[Full BOM_Valid]}) on column;
    - df_in_ITEMAttr_LCM : select ([Item].[Item Stage].[LCM].relatedmembers([Item]) * [Item].[CY Code] * [Item].[DP Code] * [Item].[Grade] * [Item].[Cell Vendor] * [Item].[Open Cell] * [Item].[SET Item]);
    - df_in_ItemAll : Select ([Item].[Item] * [Item].[Item Stage] * [Item].[Plan Group] * [Item].[Product Group]);
    - df_in_ItemPG : Select ([Item].[Item] * [Item].[Product Group] * [Item].[Plan Group]);
    - df_in_ItemMKT : Select ([Item].[Item] * [Item].[Marketing Name] * [Item].[Plan Group] * [Item].[Product Group]);
    - df_in_ItemSTRG : Select ([Item].[Item] * [Item].[Strategy] * [Item].[Plan Group] * [Item].[Product Group]);
    - df_in_ItemKPI : Select ([Item].[Item] * [Item].[KPI] * [Item].[Plan Group] * [Item].[Product Group]);
    - df_in_ItemINCH : Select ([Item].[Item] * [Item].[Inch] * [Item].[Plan Group] * [Item].[Product Group]);
    - df_in_ItemSRIS : Select ([Item].[Item] * [Item].[Series] * [Item].[Plan Group] * [Item].[Product Group]);
    - df_in_ItemCH : Select ([Item].[Item] * [Item].[Channel] * [Item].[Plan Group] * [Item].[Product Group]);
    --df_in_VersionName : SELECT (&CWVUI);
    
* Output Tables
    - df_out_MstValidResult : MG : Mst Valid Result
                          Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * 
                          [Master Validation].[Validation ID] * [Line].[Line] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Mst Valid Result_Validation Factor]}) on column;

* 테스트 스크립트 :
    EXEC plugin instance [PY_MG_MasterValidation] for Measures {[Mst Valid Result_Validation Factor]} using scope (&CWVUI.unionWith(&LastSyncVersion)) 
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
    또는
    exec procedure PR_MG_MasterValidation{"Version":"CWV_MP"};
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
str_instance = 'PY_MG_MasterValidation'
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
    col_VersionVersionName              = 'Version.[Version Name]'
    col_ItemItem                        = 'Item.[Item]'
    col_ToItemToItem                    = 'To Item.[To Item]'
    col_ItemItemStage                   = 'Item.[Item Stage]'
    col_ItemProductGroup                = 'Item.[Product Group]'
    col_ItemPlanGroup                   = 'Item.[Plan Group]'
    col_ItemMarketingName               = 'Item.[Marketing Name]'
    col_ItemStrategy                    = 'Item.[Strategy]'
    col_ItemKPI                         = 'Item.[KPI]'
    col_ItemInch                        = 'Item.[Inch]'
    col_ItemSeries                      = 'Item.[Series]'
    col_ItemChannel                     = 'Item.[Channel]'
    col_ItemMaterialItemMaterial        = 'Item Material.[Item Material]'
    col_ItemCYCode                      = 'Item.[CY Code]'
    col_ItemDPCode                      = 'Item.[DP Code]'
    col_ItemGrade                       = 'Item.[Grade]'
    col_ItemCellVendor                  = 'Item.[Cell Vendor]'
    col_ItemOpenCell                    = 'Item.[Open Cell]'
    col_ItemSETItem                     = 'Item.[SET Item]'
    col_LocationLocation                = 'Location.[Location]'
    col_ToLocationToLocation            = 'To Location.[To Location]'
    col_LocationShipmentType            = 'Location.[Shipment Type]'
    col_LocationSiteStage               = 'Location.[Site Stage]'
    col_LocationMFSiteStage             = 'Location.[MF Site Stage]'
    col_SubLocationSubLocation          = 'Sub Location.[Sub Location]'
    col_TransModeTransMode              = 'Trans Mode.[Trans Mode]'
    col_MasterValidationValidationID    = 'Master Validation.[Validation ID]'
    col_LineLine                        = 'Line.[Line]'
    col_SalesDomainAP2                  = 'Sales Domain.[AP2]'
    col_MasterValidationValidationStage = 'Master Validation.[Validation Stage]'
    col_MasterValidationValidationGrp02 = 'Master Validation.[Validation Grp02]'
    col_BOMInfoBOMID                    = 'BOM Info.[BOM ID]'
    col_BOMInfoBOMID                    = 'BOM Info.[BOM ID]'
    col_BOMInfoBOMVersion               = 'BOM Info.[BOM Version]'
    col_TimeWeek                        = 'Time.[Week]'
    col_TimeDay                         = 'Time.[Day]'
    col_GroupGroupID                    = 'Group.[Group ID]'
    col_CategoryCategory                = 'Category.[Category]'
    col_ItemNewModelItem                = 'Item New Model.[Item]'    
    
    #To Location.[To Location]    To Item.[To Item]
    
    col_BOMMaster_EffEnddate            = 'BOM Master_Eff Enddate'
    col_BOMMaster_EffStartdate          = 'BOM Master_Eff Startdate'
    col_BODItem_EffStartdate            = 'BOD Item_Eff Startdate'
    col_BODItem_EffEnddate              = 'BOD Item_Eff Enddate'
    
    col_BOMMaster_BOMID         = 'BOM Master_BOM ID'
    col_MPPlanCurrentWeek       = 'MP Plan Current Week'
    col_MPPlanStartWeek         = 'MP Plan Start Week'
    col_MPPlanEndWeek           = 'MP Plan End Week'
    col_MPPlanStartDate         = 'MP Plan Start Date'
    col_MPPlanEndDate           = 'MP Plan End Date'
    col_BODItem_Priority        = 'BOD Item_Priority'
    col_BODItemW_ShipmentLT     = 'BOD Item W_Shipment LT'
    col_BODItemW_BODLT          = 'BOD Item W_BOD LT' #BOD Item W_Tran Time'
    col_WorkCalLine_Time        = 'Work Cal Line_Time'
    col_BuildAheadCalW_Period   = 'Build Ahead Cal W_Period'
    col_SSW_SSTarget            = 'SS W_SS Target'
    col_WDumDemandQuantitytoSCS = 'W DumDemand Quantity to SCS'
    col_PLCSales_RTSComDate     = 'PLC Sales_RTS Com Date'
    col_PLCSales_RTSFWLimitDate = 'PLC Sales_RTS FW Limit Date'
    col_PLCSales_EOSComDate     = 'PLC Sales_EOS Com Date'
    col_PLCMfg_SRAComDate       = 'PLC Mfg_SRA Com Date'
    col_PLCMfg_SRAFWLimitDate   = 'PLC Mfg_SRA FW Limit Date'
    col_Inv_Qty                 = 'Inv_Qty'
    col_Intr_Qty                = 'Intr_Qty'
    
    col_ValidationFactor = "Mst Valid Result_Validation Factor"
    col_Intr_FromSiteID  = 'Intr_From Site ID'
    #col_VldAddInfo1      = 'Vld Add Info1'
    #col_VldAddInfo2      = 'Vld Add Info2'
    #col_VldAddInfo3      = 'Vld Add Info3'
    col_EffStartWeek     = 'EffStartWeek'
    col_EffEndWeek       = 'EffEndWeek'
    col_EOSComWeek       = 'EOS Com Week'
    
    col_PlanHorizonStartWeek = 'PlanHorizonStartWeek'
    col_PlanHorizonEndWeek   = 'PlanHorizonEndWeek'
    
    col_SOPFrozen_FromSite = 'SOP Frozen_From Site'
    col_SOPFrozen_Item     = 'SOP Frozen_Item'
    col_DmdW_Qty           = 'Dmd W_Qty'
    col_WOnHandQuantity    = 'W OnHand Quantity'
    col_WExpectedReceipts  = 'W Expected Receipts'
    col_NewModel_MfgDate   = 'New Model_Mfg Date'
    col_CTNItemConst_FrozenSOPOverrideQty = 'CTN Item Const_Frozen SOP Override Qty'
    col_MfgPlan_Qty        = 'Mfg Plan_Qty'
    col_SS_SSType          = 'SS_SS Type'
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP" # CWV_MP
    
    # Local 함수 선언 ----------------------------------------
    def fn_valid_ITEMSITE(l_col_List, a_ValidationID, a_df_By, a_df_Target):
            
        df_By = a_df_By[l_col_List].copy()
        df_By.drop_duplicates(inplace=True)
        
        df_Target = a_df_Target[l_col_List].copy()
        df_Target[col_MasterValidationValidationID] = a_ValidationID
        df_Target.drop_duplicates(inplace=True)
        
        # Item & Location : 존재 확인 : SETItemSite에 없는 Item, Site 추출
        df_Vd_Return =  df_Target[~df_Target.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                   df_By.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
        del [df_By, df_Target]
        df_Vd_Return[col_SubLocationSubLocation] = '-'
        df_Vd_Return[col_TransModeTransMode]     = '-'
        df_Vd_Return[col_BOMInfoBOMVersion]      = '-'
        df_Vd_Return[col_LineLine]               = '-'
        df_Vd_Return[col_SalesDomainAP2]         = '-'
        df_Vd_Return[col_ValidationFactor]       = '-'
        #print_df(df_Vd_Return, 'df_Vd_Return',False)
        return df_Vd_Return
    
    #-------------------------------------------------------
    
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion  = paramOutVersion_VALUE
        
        df_in_MasterValidation = read_csv_file("df_in_MasterValidation")
        df_in_ItemSite         = read_csv_file("df_in_ItemSite")
        df_in_Intransit        = read_csv_file("df_in_Intransit")
        df_in_Demand           = read_csv_file("df_in_Demand")
        df_in_Inventory        = read_csv_file("df_in_Inventory")
        df_in_MfgPlan_SOPFPCmp = read_csv_file("df_in_MfgPlan_SOPFPCmp")
        df_in_BOM              = read_csv_file("df_in_BOM")
        df_in_PlanHorizon      = read_csv_file("df_in_PlanHorizon")
        df_in_CurrentDay       = read_csv_file("df_in_CurrentDay")
        df_in_Time             = read_csv_file("df_in_Time")
        df_in_BOD              = read_csv_file("df_in_BOD")
        df_in_BODW             = read_csv_file("df_in_BODW")
        df_in_TactTime         = read_csv_file("df_in_TactTime")
        df_in_WorkCalLine      = read_csv_file("df_in_WorkCalLine")
        
        df_in_SETBuildAheadCalW = read_csv_file("df_in_SETBuildAheadCalW")
        df_in_LCMSS             = read_csv_file("df_in_LCMSS")
        df_in_SSW               = read_csv_file("df_in_SSW")
        df_in_SETPLCSales       = read_csv_file("df_in_SETPLCSales")
        df_in_ConstGrpEcp       = read_csv_file("df_in_ConstGrpEcp")
        df_in_SOPFrozen         = read_csv_file("df_in_SOPFrozen")
        df_in_DemandW           = read_csv_file("df_in_DemandW")
        df_in_WOnHand           = read_csv_file("df_in_WOnHand")
        df_in_WExp_Intransit    = read_csv_file("df_in_WExp_Intransit")
        df_in_CTN               = read_csv_file("df_in_CTN")
        df_in_PLCMfg            = read_csv_file("df_in_PLCMfg")
        df_in_NewModel          = read_csv_file("df_in_NewModel")
        df_in_MFGPlan_LCM       = read_csv_file("df_in_MFGPlan_LCM")
        df_in_Fullbom_LCM       = read_csv_file("df_in_Fullbom_LCM")
        df_in_ITEMAttr_LCM      = read_csv_file("df_in_ITEMAttr_LCM")
        
        df_in_ItemAll  = read_csv_file("df_in_ItemAll")
        df_in_ItemPG   = read_csv_file("df_in_ItemPG")
        df_in_ItemMKT  = read_csv_file("df_in_ItemMKT")
        df_in_ItemSTRG = read_csv_file("df_in_ItemSTRG")
        df_in_ItemKPI  = read_csv_file("df_in_ItemKPI")
        df_in_ItemINCH = read_csv_file("df_in_ItemINCH")
        df_in_ItemSRIS = read_csv_file("df_in_ItemSRIS")
        df_in_ItemCH   = read_csv_file("df_in_ItemCH")
        
        df_in_VersionName = read_csv_file("df_in_VersionName")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # MP Plan End Date     MP Plan Start Date
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    print_df(df_in_MasterValidation, 'df_in_MasterValidation',False)
    print_df(df_in_ItemSite, 'df_in_ItemSite',False)
    print_df(df_in_Intransit, 'df_in_Intransit',False)
    print_df(df_in_Demand, 'df_in_Demand',False)
    print_df(df_in_Inventory, 'df_in_Inventory',False)
    print_df(df_in_MfgPlan_SOPFPCmp, 'df_in_MfgPlan_SOPFPCmp',False)
    
    print_df(df_in_BOM, 'df_in_BOM',False)
    print_df(df_in_PlanHorizon, 'df_in_PlanHorizon',False)
    print_df(df_in_CurrentDay, 'df_in_CurrentDay',False)
    print_df(df_in_Time, 'df_in_Time',False)
    
    # df 건수가 매우 큰경우 print_df 도 시간이 많이 걸림. 건수만 출력
    row_count, col_count = df_in_BOD.shape
    note(f'=====> df_in_BOD rows : {row_count}, column : {col_count}')
    #print_df(df_in_BOD, 'df_in_BOD',False)
    
    # df 건수가 매우 큰경우 print_df 도 시간이 많이 걸림. 건수만 출력
    row_count, col_count = df_in_BODW.shape
    note(f'=====> df_in_BODW rows : {row_count}, column : {col_count}')
    #print_df(df_in_BODW, 'df_in_BODW',False)
    
    print_df(df_in_TactTime, 'df_in_TactTime',False)
    print_df(df_in_WorkCalLine, 'df_in_WorkCalLine',False)
    print_df(df_in_SETBuildAheadCalW, 'df_in_SETBuildAheadCalW',False)    
    print_df(df_in_LCMSS, 'df_in_LCMSS',False)
    print_df(df_in_SSW, 'df_in_SSW',False)
    print_df(df_in_SETPLCSales, 'df_in_SETPLCSales',False)    
    print_df(df_in_ConstGrpEcp, 'df_in_ConstGrpEcp',False)
    print_df(df_in_SOPFrozen, 'df_in_SOPFrozen',False)
    print_df(df_in_DemandW, 'df_in_DemandW',False)
    print_df(df_in_WOnHand, 'df_in_WOnHand',False)
    print_df(df_in_WExp_Intransit, 'df_in_WExp_Intransit',False)
    print_df(df_in_CTN, 'df_in_CTN',False)
    print_df(df_in_PLCMfg, 'df_in_PLCMfg',False)
    print_df(df_in_NewModel, 'df_in_NewModel',False)
    print_df(df_in_MFGPlan_LCM, 'df_in_MFGPlan_LCM',False)
    print_df(df_in_Fullbom_LCM, 'df_in_Fullbom_LCM',False)
    print_df(df_in_ITEMAttr_LCM, 'df_in_ITEMAttr_LCM',False)
    
    print_df(df_in_ItemAll, 'df_in_ItemAll',False)
    print_df(df_in_ItemPG, 'df_in_ItemPG',False)
    print_df(df_in_ItemMKT, 'df_in_ItemMKT',False)
    print_df(df_in_ItemSTRG, 'df_in_ItemSTRG',False)
    print_df(df_in_ItemKPI, 'df_in_ItemKPI',False)
    print_df(df_in_ItemINCH, 'df_in_ItemINCH',False)
    print_df(df_in_ItemSRIS, 'df_in_ItemSRIS',False)
    print_df(df_in_ItemCH, 'df_in_ItemCH',False)
    
    print_df(df_in_VersionName, 'df_in_VersionName',False)
    
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
    
    # -------------------------------------------------------------------------------------    
    if df_in_BOM[col_BOMMaster_EffStartdate].dtype != 'datetime64[ns]':
        df_in_BOM[col_BOMMaster_EffStartdate] = pd.to_datetime(df_in_BOM[col_BOMMaster_EffStartdate]
                                                               , format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_BOM[col_BOMMaster_EffEnddate].dtype != 'datetime64[ns]':
        #2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_BOM[col_BOMMaster_EffEnddate] = np.where(df_in_BOM[col_BOMMaster_EffEnddate].isna(),
                                                       df_in_BOM[col_BOMMaster_EffEnddate], 
                                                       df_in_BOM[col_BOMMaster_EffEnddate].apply(lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                                                       )
        df_in_BOM[col_BOMMaster_EffEnddate]   = pd.to_datetime(df_in_BOM[col_BOMMaster_EffEnddate]
                                                               , format='%m/%d/%Y %I:%M:%S %p')    
    print_df(df_in_BOM, 'df_in_BOM x',False)
    
    if df_in_BOD[col_BODItem_EffStartdate].dtype != 'datetime64[ns]':
        df_in_BOD[col_BODItem_EffStartdate] = pd.to_datetime(df_in_BOD[col_BODItem_EffStartdate]
                                                                , format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_BOD[col_BODItem_EffEnddate].dtype != 'datetime64[ns]':
        df_in_BOD[col_BODItem_EffEnddate]   = pd.to_datetime(df_in_BOD[col_BODItem_EffEnddate]
                                                                , format='%m/%d/%Y %I:%M:%S %p')
    #print_df(df_in_BOD, 'df_in_BOD x',False)
    
    if df_in_PlanHorizon[col_MPPlanStartDate].dtype != 'datetime64[ns]':
        df_in_PlanHorizon[col_MPPlanStartDate] = pd.to_datetime(df_in_PlanHorizon[col_MPPlanStartDate]
                                                                , format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_PlanHorizon[col_MPPlanEndDate].dtype != 'datetime64[ns]':
        df_in_PlanHorizon[col_MPPlanEndDate]   = pd.to_datetime(df_in_PlanHorizon[col_MPPlanEndDate]
                                                                , format='%m/%d/%Y %I:%M:%S %p')    
    df_in_PlanHorizon = df_in_PlanHorizon.astype({col_MPPlanCurrentWeek: 'str', col_MPPlanStartWeek: 'str'
                                                     , col_MPPlanEndWeek: 'str'}, copy=True)
    print_df(df_in_PlanHorizon, 'df_in_PlanHorizon x',False)
    
    df_in_Time[col_TimeDay] = pd.to_datetime(df_in_Time[col_TimeDay], format='%Y-%m-%d')   
    df_in_Time = df_in_Time.astype({col_TimeWeek: 'str'}, copy=True)
    print_df(df_in_Time, 'df_in_Time x',False)
    
    df_in_CurrentDay[col_TimeDay] = pd.to_datetime(df_in_CurrentDay[col_TimeDay], format='%Y-%m-%d')
    print_df(df_in_CurrentDay, 'df_in_CurrentDay x',False)
    
    if df_in_SETPLCSales[col_PLCSales_RTSComDate].dtype != 'datetime64[ns]':
        df_in_SETPLCSales[col_PLCSales_RTSComDate]     = pd.to_datetime(df_in_SETPLCSales[col_PLCSales_RTSComDate]
                                                                        , format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_SETPLCSales[col_PLCSales_RTSFWLimitDate].dtype != 'datetime64[ns]':
        df_in_SETPLCSales[col_PLCSales_RTSFWLimitDate] = pd.to_datetime(df_in_SETPLCSales[col_PLCSales_RTSFWLimitDate]
                                                                        , format='%m/%d/%Y %I:%M:%S %p')
        
    if df_in_SETPLCSales[col_PLCSales_EOSComDate].dtype != 'datetime64[ns]':
        #2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_SETPLCSales[col_PLCSales_EOSComDate] = np.where(df_in_SETPLCSales[col_PLCSales_EOSComDate].isna(),
                                                       df_in_SETPLCSales[col_PLCSales_EOSComDate], 
                                                       df_in_SETPLCSales[col_PLCSales_EOSComDate].apply(lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                                                       )
        df_in_SETPLCSales[col_PLCSales_EOSComDate]   = pd.to_datetime(df_in_SETPLCSales[col_PLCSales_EOSComDate]
                                                               , format='%m/%d/%Y %I:%M:%S %p')
        
    print_df(df_in_SETPLCSales, 'df_in_SETPLCSales x',False)
    
    if df_in_PLCMfg[col_PLCMfg_SRAComDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[col_PLCMfg_SRAComDate]     = pd.to_datetime(df_in_PLCMfg[col_PLCMfg_SRAComDate]
                                                                    , format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_PLCMfg[col_PLCMfg_SRAFWLimitDate].dtype != 'datetime64[ns]':
        df_in_PLCMfg[col_PLCMfg_SRAFWLimitDate] = pd.to_datetime(df_in_PLCMfg[col_PLCMfg_SRAFWLimitDate]
                                                                    , format='%m/%d/%Y %I:%M:%S %p')
    print_df(df_in_PLCMfg, 'df_in_PLCMfg x',False)
    
    if df_in_NewModel[col_NewModel_MfgDate].dtype != 'datetime64[ns]':
        df_in_NewModel[col_NewModel_MfgDate] = pd.to_datetime(df_in_NewModel[col_NewModel_MfgDate]
                                                                    , format='%m/%d/%Y %I:%M:%S %p')
    print_df(df_in_NewModel, 'df_in_NewModel x',False)
    
    df_in_Demand = df_in_Demand.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_Inventory = df_in_Inventory.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_MfgPlan_SOPFPCmp = df_in_MfgPlan_SOPFPCmp.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_BODW = df_in_BODW.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_WorkCalLine = df_in_WorkCalLine.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_SETBuildAheadCalW = df_in_SETBuildAheadCalW.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_SSW = df_in_SSW.astype({col_TimeWeek: 'str'}, copy=True)
    
    print_df(df_in_Demand, 'df_in_Demand 2',False)
    print_df(df_in_Inventory, 'df_in_Inventory 2',False)
    print_df(df_in_MfgPlan_SOPFPCmp, 'df_in_MfgPlan_SOPFPCmp 2',False)
    #print_df(df_in_BODW, 'df_in_BODW 2',False)
    print_df(df_in_WorkCalLine, 'df_in_WorkCalLine 2',False)
    print_df(df_in_SETBuildAheadCalW, 'df_in_SETBuildAheadCalW 2',False)
    print_df(df_in_SSW, 'df_in_SSW 2',False)
    
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
    print_df(df_in_SETItemSite, 'df_in_SETItemSite',False)
    print_df(df_in_LCMItemSite, 'df_in_LCMItemSite',False)
    
    df_in_SETDemand = df_in_Demand[df_in_Demand[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMDemand = df_in_Demand[df_in_Demand[col_ItemItemStage] == 'LCM'].copy()
    del df_in_Demand
    print_df(df_in_SETDemand, 'df_in_SETDemand',False)
    print_df(df_in_LCMDemand, 'df_in_LCMDemand',False)
    
    df_in_SETMfgPlan_SFC = df_in_MfgPlan_SOPFPCmp[df_in_MfgPlan_SOPFPCmp[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMMfgPlan_SFC = df_in_MfgPlan_SOPFPCmp[df_in_MfgPlan_SOPFPCmp[col_ItemItemStage] == 'LCM'].copy()
    del df_in_MfgPlan_SOPFPCmp
    print_df(df_in_SETMfgPlan_SFC, 'df_in_SETMfgPlan_SFC',False)
    print_df(df_in_LCMMfgPlan_SFC, 'df_in_LCMMfgPlan_SFC',False)
    
    df_in_SETInventory = df_in_Inventory[df_in_Inventory[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMInventory = df_in_Inventory[df_in_Inventory[col_ItemItemStage] == 'LCM'].copy()
    del df_in_Inventory
    print_df(df_in_SETInventory, 'df_in_SETInventory',False)
    print_df(df_in_LCMInventory, 'df_in_LCMInventory',False)
    
    df_in_SETIntransit = df_in_Intransit[df_in_Intransit[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMIntransit = df_in_Intransit[df_in_Intransit[col_ItemItemStage] == 'LCM'].copy()
    del df_in_Intransit
    print_df(df_in_SETIntransit, 'df_in_SETIntransit',False)
    print_df(df_in_LCMIntransit, 'df_in_LCMIntransit',False)
    
    df_in_SETBOD = df_in_BOD[df_in_BOD[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMBOD = df_in_BOD[df_in_BOD[col_ItemItemStage] == 'LCM'].copy()
    del df_in_BOD
    # df 건수가 매우 큰경우 print_df 도 시간이 많이 걸림. 건수만 출력
    row_count, col_count = df_in_SETBOD.shape
    note(f'=====> df_in_SETBOD rows : {row_count}, column : {col_count}')
    row_count, col_count = df_in_LCMBOD.shape
    note(f'=====> df_in_LCMBOD rows : {row_count}, column : {col_count}')
    #print_df(df_in_SETBOD, 'df_in_SETBOD',False)
    #print_df(df_in_LCMBOD, 'df_in_LCMBOD',False)
    
    df_in_SETBODW = df_in_BODW[df_in_BODW[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMBODW = df_in_BODW[df_in_BODW[col_ItemItemStage] == 'LCM'].copy()
    del df_in_BODW
    # df 건수가 매우 큰경우 print_df 도 시간이 많이 걸림. 건수만 출력
    row_count, col_count = df_in_SETBODW.shape
    note(f'=====> df_in_SETBODW rows : {row_count}, column : {col_count}')
    row_count, col_count = df_in_LCMBODW.shape
    note(f'=====> df_in_LCMBODW rows : {row_count}, column : {col_count}')
    #print_df(df_in_SETBODW, 'df_in_SETBODW',False)
    #print_df(df_in_LCMBODW, 'df_in_LCMBODW',False)
    
    df_in_SETTactTime = df_in_TactTime[df_in_TactTime[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMTactTime = df_in_TactTime[df_in_TactTime[col_ItemItemStage] == 'LCM'].copy()
    del df_in_TactTime
    print_df(df_in_SETTactTime, 'df_in_SETTactTime',False)
    print_df(df_in_LCMTactTime, 'df_in_LCMTactTime',False)
    
    df_in_SETWorkCalLine = df_in_WorkCalLine[df_in_WorkCalLine[col_LocationMFSiteStage] == 'SET'].copy()
    df_in_LCMWorkCalLine = df_in_WorkCalLine[df_in_WorkCalLine[col_LocationMFSiteStage].str.contains('LCM', na=False)].copy()
    del df_in_WorkCalLine
    print_df(df_in_SETWorkCalLine, 'df_in_SETWorkCalLine',False)
    print_df(df_in_LCMWorkCalLine, 'df_in_LCMWorkCalLine',False)
    
    df_in_SETSSW = df_in_SSW[df_in_SSW[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMSSW = df_in_SSW[df_in_SSW[col_ItemItemStage] == 'LCM'].copy()
    del df_in_SSW
    print_df(df_in_SETSSW, 'df_in_SETSSW',False)
    print_df(df_in_LCMSSW, 'df_in_LCMSSW',False)
    
    df_in_SETConstGrpEcp = df_in_ConstGrpEcp[df_in_ConstGrpEcp[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMConstGrpEcp = df_in_ConstGrpEcp[df_in_ConstGrpEcp[col_ItemItemStage] == 'LCM'].copy()
    del df_in_ConstGrpEcp
    print_df(df_in_SETConstGrpEcp, 'df_in_SETConstGrpEcp',False)
    print_df(df_in_LCMConstGrpEcp, 'df_in_LCMConstGrpEcp',False)
    
    df_in_SETItem = df_in_ItemAll[df_in_ItemAll[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMItem = df_in_ItemAll[df_in_ItemAll[col_ItemItemStage] == 'LCM'].copy()
    print_df(df_in_SETItem, 'df_in_SETItem',False)
    print_df(df_in_LCMItem, 'df_in_LCMItem',False)
    
    # Version 분리 : VERSION_VALUE 용, LastVersion 용 ---------------------
    # LastVersion : LastVersion 먼저처리----------------------------------------------------------
    df_in_SETLastInventory = df_in_SETInventory[df_in_SETInventory[col_VersionVersionName] != VERSION_VALUE]
    df_in_LCMLastInventory = df_in_LCMInventory[df_in_LCMInventory[col_VersionVersionName] != VERSION_VALUE]
    df_in_SETLastIntransit = df_in_SETIntransit[df_in_SETIntransit[col_VersionVersionName] != VERSION_VALUE]
    df_in_LCMLastIntransit = df_in_LCMIntransit[df_in_LCMIntransit[col_VersionVersionName] != VERSION_VALUE]
    
    print_df(df_in_SETLastInventory, 'df_in_SETLastInventory',False)
    print_df(df_in_LCMLastInventory, 'df_in_LCMLastInventory',False)
    print_df(df_in_SETLastIntransit, 'df_in_SETLastIntransit',False)
    print_df(df_in_LCMLastIntransit, 'df_in_LCMLastIntransit',False)
    # ----------------------------------------------------------------------------
    
    # VERSION_VALUE -----------------------------------------------------------
    df_in_SETIntransit      = df_in_SETIntransit[df_in_SETIntransit[col_VersionVersionName] == VERSION_VALUE]
    df_in_LCMIntransit      = df_in_LCMIntransit[df_in_LCMIntransit[col_VersionVersionName] == VERSION_VALUE]
    df_in_SETInventory      = df_in_SETInventory[df_in_SETInventory[col_VersionVersionName] == VERSION_VALUE]
    df_in_LCMInventory      = df_in_LCMInventory[df_in_LCMInventory[col_VersionVersionName] == VERSION_VALUE]
    
    print_df(df_in_SETIntransit, 'df_in_SETIntransit 2',False)
    print_df(df_in_LCMIntransit, 'df_in_LCMIntransit 2',False)
    print_df(df_in_SETInventory, 'df_in_SETInventory 2',False)
    print_df(df_in_LCMInventory, 'df_in_LCMInventory 2',False)
    
    df_in_SETPLCMfg = df_in_PLCMfg[df_in_PLCMfg[col_ItemItemStage] == 'SET'].copy()
    
    # df_in_Time 칼럼 정리
    df_in_Time = df_in_Time[[col_TimeWeek, col_TimeDay]]
    
    df_Time_Min_Max = df_in_Time.copy()
    df_Time_Min_Max['Dummy'] = 'A'    
    df_Time_Min_Max = df_Time_Min_Max.groupby(['Dummy'], as_index=False).agg(Min_Day=(col_TimeDay, 'min'), 
                                                                             Max_Day=(col_TimeDay, 'max'))
    print_df(df_Time_Min_Max, 'df_Time_Min_Max',False)
    
    # df_in_PlanHorizon 칼럼 추가
    df_in_PlanHorizon[col_PlanHorizonStartWeek] = df_in_PlanHorizon[col_MPPlanStartWeek]
    df_in_PlanHorizon[col_PlanHorizonEndWeek]   = df_in_PlanHorizon[col_MPPlanEndWeek]
    
    # df_in_MasterValidation 추가 정보
    #vld_info_TMP = df_in_MasterValidation[col_MasterValidationValidationID].str.split('_', expand=True)
    #df_in_MasterValidation[[col_VldAddInfo1, col_VldAddInfo2, col_VldAddInfo3]] = vld_info_TMP
    
    #### df_SETBOM : SET ITEM 에 해당하는 자료 추출
    df_in_BOM[col_ItemItem] = df_in_BOM[col_BOMMaster_BOMID]
    df_SETBOM = df_in_BOM[df_in_BOM.set_index([col_ItemItem]).index.isin(
                          df_in_SETItem.set_index([col_ItemItem]).index)].copy()    
    del df_in_BOM
    # BOM Info.[BOM ID] = Item + BOM Info.[BOM Version]
    df_SETBOM[col_BOMInfoBOMVersion] = df_SETBOM[col_BOMInfoBOMID].str.split('_').str[1]
    #print_df(df_SETBOM, 'df_SETBOM',False)
    
    # df_in_CurrentDay : Dummy 칼럼 추가
    df_in_CurrentDay['Dummy'] = 'A'
    
    # Item 관련 칼럼 삭제( 호출 시 Scope 활용 칼럼)
    df_in_ItemAll.drop(columns=[col_ItemProductGroup, col_ItemPlanGroup], inplace=True)
    df_in_ItemPG.drop(columns=[col_ItemPlanGroup], inplace=True)
    df_in_ItemMKT.drop(columns=[col_ItemProductGroup, col_ItemPlanGroup], inplace=True)
    df_in_ItemSTRG.drop(columns=[col_ItemProductGroup, col_ItemPlanGroup], inplace=True)
    df_in_ItemKPI.drop(columns=[col_ItemProductGroup, col_ItemPlanGroup], inplace=True)
    df_in_ItemINCH.drop(columns=[col_ItemProductGroup, col_ItemPlanGroup], inplace=True)
    df_in_ItemSRIS.drop(columns=[col_ItemProductGroup, col_ItemPlanGroup], inplace=True)
    df_in_ItemCH.drop(columns=[col_ItemProductGroup, col_ItemPlanGroup], inplace=True)
    
    # Merge Item & ATTR
    df_ItemATTR = df_in_ItemAll.merge(df_in_ItemPG, on=[col_ItemItem], how='left', suffixes=('', '_y'))
    del [df_in_ItemAll, df_in_ItemPG]
    df_ItemATTR = df_ItemATTR.merge(df_in_ItemMKT, on=[col_ItemItem], how='left', suffixes=('', '_y'))
    del df_in_ItemMKT
    df_ItemATTR = df_ItemATTR.merge(df_in_ItemSTRG, on=[col_ItemItem], how='left', suffixes=('', '_y'))
    del df_in_ItemSTRG
    df_ItemATTR = df_ItemATTR.merge(df_in_ItemKPI, on=[col_ItemItem], how='left', suffixes=('', '_y'))
    del df_in_ItemKPI
    df_ItemATTR = df_ItemATTR.merge(df_in_ItemINCH, on=[col_ItemItem], how='left', suffixes=('', '_y'))
    del df_in_ItemINCH
    df_ItemATTR = df_ItemATTR.merge(df_in_ItemSRIS, on=[col_ItemItem], how='left', suffixes=('', '_y'))
    del df_in_ItemSRIS
    df_ItemATTR = df_ItemATTR.merge(df_in_ItemCH, on=[col_ItemItem], how='left', suffixes=('', '_y'))
    del df_in_ItemCH
    
    # df_ItemATTR : Dummy 칼럼 추가
    df_ItemATTR['Dummy'] = df_ItemATTR[col_ItemItem]
    print_df(df_ItemATTR, 'df_ItemATTR',False)
    
    # df_SETInv_SUM --------------------------------------------
    df_SETInv_SUM = df_in_SETInventory[df_in_SETInventory[col_Inv_Qty].notna()]
    df_SETInv_SUM = df_SETInv_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                            as_index=False).agg({col_Inv_Qty: "sum"})
    df_SETInv_SUM[col_Inv_Qty] = df_SETInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_SETInv_SUM, 'df_SETInv_SUM',False)
    
    # df_SETLastInv_SUM  --------------------------------------------
    df_SETLastInv_SUM = df_in_SETLastInventory[df_in_SETLastInventory[col_Inv_Qty].notna()]
    del df_in_SETLastInventory
    df_SETLastInv_SUM = df_SETLastInv_SUM.groupby([col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Inv_Qty: "sum"})
    df_SETLastInv_SUM[col_Inv_Qty] = df_SETLastInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_SETLastInv_SUM, 'df_SETLastInv_SUM',False)
    
    # df_SETIntr_SUM --------------------------------------------
    df_SETIntr_SUM = df_in_SETIntransit[df_in_SETIntransit[col_Intr_Qty].notna()]
    df_SETIntr_SUM = df_SETIntr_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Intr_Qty: "sum"})
    df_SETIntr_SUM[col_Intr_Qty] = df_SETIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_SETIntr_SUM, 'df_SETIntr_SUM',False)

    # df_SETLastIntr_SUM --------------------------------------------
    df_SETLastIntr_SUM = df_in_SETLastIntransit[df_in_SETLastIntransit[col_Intr_Qty].notna()]
    del df_in_SETLastIntransit
    df_SETLastIntr_SUM = df_SETLastIntr_SUM.groupby([col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Intr_Qty: "sum"})
    df_SETLastIntr_SUM[col_Intr_Qty] = df_SETLastIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_SETLastIntr_SUM, 'df_SETLastIntr_SUM',False)
    
    # df_LCMInv_SUM --------------------------------------------
    df_LCMInv_SUM = df_in_LCMInventory[df_in_LCMInventory[col_Inv_Qty].notna()]
    df_LCMInv_SUM = df_LCMInv_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Inv_Qty: "sum"})
    df_LCMInv_SUM[col_Inv_Qty] = df_LCMInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_LCMInv_SUM, 'df_LCMInv_SUM',False)
    
    # df_LCMLastInv_SUM --------------------------------------------
    df_LCMLastInv_SUM = df_in_LCMLastInventory[df_in_LCMLastInventory[col_Inv_Qty].notna()]
    del df_in_LCMLastInventory
    df_LCMLastInv_SUM = df_LCMLastInv_SUM.groupby([col_ItemItem, col_LocationLocation],
                                                  as_index=False).agg({col_Inv_Qty: "sum"})
    df_LCMLastInv_SUM[col_Inv_Qty] = df_LCMLastInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_LCMLastInv_SUM, 'df_LCMLastInv_SUM',False)
    
    # df_LCMIntr_SUM --------------------------------------------
    df_LCMIntr_SUM = df_in_LCMIntransit[df_in_LCMIntransit[col_Intr_Qty].notna()]
    df_LCMIntr_SUM = df_LCMIntr_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Intr_Qty: "sum"})
    df_LCMIntr_SUM[col_Intr_Qty] = df_LCMIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_LCMIntr_SUM, 'df_LCMIntr_SUM',False)

    # df_LCMLastIntr_SUM --------------------------------------------
    df_LCMLastIntr_SUM = df_in_LCMLastIntransit[df_in_LCMLastIntransit[col_Intr_Qty].notna()]
    del df_in_LCMLastIntransit
    df_LCMLastIntr_SUM = df_LCMLastIntr_SUM.groupby([col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Intr_Qty: "sum"})
    df_LCMLastIntr_SUM[col_Intr_Qty] = df_LCMLastIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_LCMLastIntr_SUM, 'df_LCMLastIntr_SUM',False)
    
    # 'NA' 값을 nan 으로 읽어들임.
    df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion] = np.where(df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion].isna()
                                                       , "-x-", df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion])
    df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion] = np.where(df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion] == "-x-"
                                                       , "NA", df_in_SETMfgPlan_SFC[col_BOMInfoBOMVersion])
    
    df_in_LCMMfgPlan_SFC[col_BOMInfoBOMVersion] = np.where(df_in_LCMMfgPlan_SFC[col_BOMInfoBOMVersion].isna()
                                                       , "-x-", df_in_LCMMfgPlan_SFC[col_BOMInfoBOMVersion])
    df_in_LCMMfgPlan_SFC[col_BOMInfoBOMVersion] = np.where(df_in_LCMMfgPlan_SFC[col_BOMInfoBOMVersion] == "-x-"
                                                       , "NA", df_in_LCMMfgPlan_SFC[col_BOMInfoBOMVersion])
    
    # 여러번 사용하는 Set 구성 -----------------------------------------------
    df_SETBOD_Demand_Sub_Loc = df_in_SETBOD[
                                       df_in_SETBOD.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
                                       df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
    #print_df(df_SETBOD_Demand_Sub_Loc, 'df_SETBOD_Demand_Sub_Loc',False)
    
    df_SETBuildAheadCalW_Demand_Sub_Loc = df_in_SETBuildAheadCalW[
                              df_in_SETBuildAheadCalW.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
                              df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
    print_df(df_SETBuildAheadCalW_Demand_Sub_Loc, 'df_SETBuildAheadCalW_Demand_Sub_Loc',False)
    
    df_SETSSW_Demand_Loc = df_in_SETSSW[df_in_SETSSW.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                        df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
    print_df(df_SETSSW_Demand_Loc, 'df_SETSSW_Demand_Loc',False)
    #------------------------------------------------------------------------
    step('=====> STEP 0-5 : 추가 df Create End')
    ################################################################################################################
    # STEP 1 : Validate data Create
    ################################################################################################################
    step('=====> STEP 1-1 : Validate data Create')
    
    # 칼럼설정
    clist_V_ITM_LOC = [col_VersionVersionName, col_ItemItem, col_LocationLocation]
    clist_V_ITM_LOC_Sub = clist_V_ITM_LOC + [col_SubLocationSubLocation]
    clist_bod   = clist_V_ITM_LOC + [col_SubLocationSubLocation, col_TransModeTransMode]
    clist_grain = [col_VersionVersionName, col_MasterValidationValidationID, col_ItemItem, col_LocationLocation,
                      col_SubLocationSubLocation, col_TransModeTransMode, col_BOMInfoBOMVersion,
                      col_LineLine, col_SalesDomainAP2]
    clist_all   = [col_VersionVersionName, col_MasterValidationValidationID, col_ItemItem, col_LocationLocation,
                      col_SubLocationSubLocation, col_TransModeTransMode, col_BOMInfoBOMVersion,
                      col_LineLine, col_SalesDomainAP2, col_ValidationFactor]
    
    #임시 --------------------------------------------------
    #df_in_MasterValidation = df_in_MasterValidation[df_in_MasterValidation[col_MasterValidationValidationID] == '(LCM)BOM_MFGPLAN']
    #------------------------------------------------------
    
    note(f'=====> for Strt ======================================================= ')
    df_Vld_Result_All = pd.DataFrame(columns=clist_all) #빈 dataframe
    
    for idx, row in df_in_MasterValidation.iterrows():
        #note(f'=====> Validation ID : {row[col_MasterValidationValidationID]}')
        df_Vld_Result_TMP = pd.DataFrame(columns=clist_all) #빈 dataframe
        CHK_I = 0
        #note(f'=====> Validation ID : {row[col_MasterValidationValidationID]} ----Start----')
        
        if row[col_MasterValidationValidationID] == '(SET)ITEMSITE_INTRANSIT' :  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                , df_in_SETItemSite.copy()
                                                , df_in_SETIntransit.copy())           
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)ITEMSITE_INTRANSIT':  # ------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                , df_in_LCMItemSite.copy()
                                                , df_in_LCMIntransit.copy())
        
        elif row[col_MasterValidationValidationID] == '(SET)ITEMSITE_DEMAND':  # ------------------------------------
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
        
        elif row[col_MasterValidationValidationID] == '(SET)ITEMSITE_MFGPLAN':  # ------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                , df_in_SETItemSite.copy()
                                                , df_in_SETMfgPlan_SFC.copy())
        
        elif row[col_MasterValidationValidationID] == '(LCM)ITEMSITE_MFGPLAN':  # ------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                , df_in_LCMItemSite.copy()
                                                , df_in_LCMMfgPlan_SFC.copy())
        
        elif row[col_MasterValidationValidationID] == '(SET)ITEMSITE_INVENTORY':  # ------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                , df_in_SETItemSite.copy()
                                                , df_in_SETInventory.copy())
        
        elif row[col_MasterValidationValidationID] == '(LCM)ITEMSITE_INVENTORY':  # ------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                , df_in_LCMItemSite.copy()
                                                , df_in_LCMInventory.copy())
        
        elif row[col_MasterValidationValidationID] == '(SET)BOM_DATE' :  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item, Site 대상으로 : Item, Site 로 SETDemand 와 join
            df_Ext_Data = df_SETBOM[df_SETBOM.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                    df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_BOMMaster_EffStartdate].notna() &
                                     (df_Ext_Data[col_BOMMaster_EffStartdate] > df_Ext_Data[col_BOMMaster_EffEnddate])]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            #df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor] = ('Eff Startdate = ' + df_Ext_Data[col_BOMMaster_EffStartdate].dt.date.astype('str') + 
                                               ', Eff Enddate = ' + df_Ext_Data[col_BOMMaster_EffEnddate].dt.date.astype('str'))
            
            #칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]            
            df_Ext_Data.drop_duplicates(inplace=True)
                        
            #print_df(df_Ext_Data, 'df_(SET)BOM_DATE',False)            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOM_MFGPLAN':  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            #생산계획 있으나 BOM 없음
            #SETMfgPlan에 있는 Item, Site, BOM Version이 SETBOM에 Item, Site 추출
            df_Ext_Data = df_in_SETMfgPlan_SFC[
                  ~df_in_SETMfgPlan_SFC.set_index([col_ItemItem, col_LocationLocation, col_BOMInfoBOMVersion]).index.isin(
                   df_SETBOM.set_index([col_ItemItem, col_LocationLocation, col_BOMInfoBOMVersion]).index)].copy()
                        
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            #df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor]       = '-' # BOM Version 그레인 추가됨.('BOM Version=' + df_Ext_Data[col_BOMInfoBOMVersion].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)

            #print_df(df_Ext_Data, 'df_(SET)BOM_MFGPLAN',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOM_DEMAND':  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item, Site 대상으로 : SETDemand join과 같음.
            df_Ext_Data = df_SETBOM[df_SETBOM.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                    df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            
            # megge : df_in_PlanHorizon
            df_Ext_Data = df_Ext_Data.merge(df_in_PlanHorizon, on=[col_VersionVersionName], how='inner')
            
            # megge : df_in_Time : EffStartWeek :주 정보를 가져오기 위해
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_BOMMaster_EffStartdate],
                                                        right_on=[col_TimeDay], how='left', suffixes=('','_y'))
            
            df_Ext_Data.rename(columns={col_TimeWeek: col_EffStartWeek}, inplace=True)
            df_Ext_Data.drop(columns=[col_TimeDay], inplace=True)
            
            # megge : df_in_Time : EffEndWeek :주 정보를 가져오기 위해
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_BOMMaster_EffEnddate],
                                                        right_on=[col_TimeDay], how='left', suffixes=('','_y'))
            
            df_Ext_Data.rename(columns={col_TimeWeek: col_EffEndWeek}, inplace=True)
            df_Ext_Data.drop(columns=[col_TimeDay], inplace=True)
            
            # megge : df_Time_Min_Max
            df_Ext_Data['Dummy'] = 'A'
            df_Ext_Data = df_Ext_Data.merge(df_Time_Min_Max, on=['Dummy'], how='inner')
            
            df_Ext_Data['Chk_Value'] = np.where(
                                            (df_Ext_Data[col_BOMMaster_EffEnddate].isna() |
                                             (df_Ext_Data[col_BOMMaster_EffEnddate] > df_Ext_Data['Max_Day']) |
                                             (df_Ext_Data[col_EffEndWeek] >= df_Ext_Data[col_PlanHorizonStartWeek])) &
                                            (df_Ext_Data[col_BOMMaster_EffStartdate].isna() |
                                             (df_Ext_Data[col_BOMMaster_EffStartdate] < df_Ext_Data['Min_Day']) |
                                             (df_Ext_Data[col_EffStartWeek] <= df_Ext_Data[col_PlanHorizonEndWeek]))
                                            , 1, 0)
            
            # EffEnddate > PlanHorizonStartWeek && EffStartdate < PlanHorizonEndWeek 인 경우가 1건도 없는 Item, Site 추출
            df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC, as_index=False).agg({'Chk_Value': "sum"})
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] == 0]  # 1건도 없는 Item : sum 결과가 0 인 Item
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor]       = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)BOM_DEMAND',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_PRIORITY':  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item, Site 대상으로
            #df_Ext_Data = df_in_SETBOD[(df_in_SETBOD.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
            #                              df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)) &
            #                             (df_in_SETBOD[col_BODItem_Priority].notna())
            #                             ].copy()
            df_Ext_Data = df_SETBOD_Demand_Sub_Loc[df_SETBOD_Demand_Sub_Loc[col_BODItem_Priority].notna()].copy()
            df_Ext_Data[col_BODItem_Priority]  = df_Ext_Data[col_BODItem_Priority].astype('int64')
            df_Ext_Data['Chk_Value'] = 0
            df_Ext_Data['Chk_Value'] = df_Ext_Data.groupby([col_ItemItem, col_SubLocationSubLocation, 
                                                            col_BODItem_Priority])['Chk_Value'].transform('count')
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] >= 2]  # BOD Item_Priority가 동일한것이 2개이상
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            #df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine]          = '-'
            df_Ext_Data[col_SalesDomainAP2]    = '-'
            df_Ext_Data[col_ValidationFactor]  = ('BOD Prty=' + df_Ext_Data[col_BODItem_Priority].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_MFGPLAN':  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETMfgPlan에 있는 Item, Site가 SETBOD(Item, Location)에 한건도 없을 경우 Item, Site 추출
            df_Ext_Data = df_in_SETMfgPlan_SFC[
                                         ~df_in_SETMfgPlan_SFC.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                          df_in_SETBOD.set_index([col_ItemItem, col_LocationLocation]).index)].copy()

            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor]       = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_DEMAND':  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item, Site 대상으로 SETBOD(Item, Sub Location)가 없는 Item, Site 추출
            df_Ext_Data = df_in_SETDemand[
                                     ~df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                      df_in_SETBOD.set_index([col_ItemItem, col_SubLocationSubLocation]).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor]       = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_Ext_Data')
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_EFFDATE_OUTLIER':  #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item, Site 대상으로 , SETBOD(Item, Sub Location) 
            #df_Ext_Data = df_in_SETBOD[df_in_SETBOD.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
            #                           df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            df_Ext_Data = df_SETBOD_Demand_Sub_Loc.copy()
            df_Ext_Data['Dummy'] = 'A'
            df_Ext_Data = df_Ext_Data.merge(df_in_CurrentDay, on=['Dummy'], how='inner')
            # EffEnddate < Currentdate-365인 Item, Site, From Site 추출
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_BODItem_EffEnddate] < 
                                                  (df_Ext_Data[col_TimeDay] - datetime.timedelta(days=365)) ]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            #df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor] = (
                                     'Eff Startdate = ' + df_Ext_Data[col_BODItem_EffStartdate].dt.date.astype('str') +
                                     ', Eff Enddate = '  + df_Ext_Data[col_BODItem_EffEnddate].dt.date.astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_BOD_EFFDATE_OUTLIER',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_EFFECTIVENESS': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #(Demand) 유효 BOD가 하나도 없음(추출 : Item, Locaion)
            # SETDemand에 있는 Item, Site 대상으로 : SETBOD(Item, Sub Location) 정보
            #df_Ext_Data = df_in_SETBOD[df_in_SETBOD.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
            #                           df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            df_Ext_Data = df_SETBOD_Demand_Sub_Loc.copy()
            
            # EffEnddate > PlanHorizonStartWeek && EffStartdate < PlanHorizonEndWeek  한건도 없는 Item, Site 추출
            # megge : df_in_PlanHorizon
            df_Ext_Data = df_Ext_Data.merge(df_in_PlanHorizon, on=[col_VersionVersionName], how='inner')
            
            # megge : df_in_Time : EffStartWeek :주 정보를 가져오기 위해
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_BODItem_EffStartdate], right_on=[col_TimeDay]
                                            , how='left')
            df_Ext_Data.rename(columns={col_TimeWeek: col_EffStartWeek}, inplace=True)
            df_Ext_Data.drop(columns=[col_TimeDay], inplace=True)            

            # megge : df_in_Time : EffEndWeek :주 정보를 가져오기 위해
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_BODItem_EffEnddate], right_on=[col_TimeDay]
                                            , how='left')
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
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            #한건도 없는 Item, Site 추출
            df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC, as_index=False).agg({'Chk_Value': "sum"})
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] == 0]  # 1건도 없는 Item : sum 결과가 0 인 Item
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor]       = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)BOD_EFFECTIVENESS',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_TIME_PHASED': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item, Site 대상으로
            df_Ext_Data = df_in_SETBODW[(df_in_SETBODW.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
                                        df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)) &
                                        df_in_SETBODW[col_BODItemW_BODLT].notna() &
                                        df_in_SETBODW[col_BODItemW_ShipmentLT].notna()
                                        ].copy()
            
            df_Ext_Data[col_BODItemW_ShipmentLT]  = df_Ext_Data[col_BODItemW_ShipmentLT].astype('int64')
            df_Ext_Data[col_BODItemW_BODLT] = df_Ext_Data[col_BODItemW_BODLT].astype('int64')
            
            # GROUP BY : TranTime, ShipLT
            df_Ext_Data = df_Ext_Data.groupby(clist_bod,
                                               as_index=False).agg(W_TranTime_max=(col_BODItemW_BODLT, 'max'),
                                                                   W_TranTime_min=(col_BODItemW_BODLT, 'min'),
                                                                   W_ShipLT_max=(col_BODItemW_ShipmentLT, 'max'),
                                                                   W_ShipLT_min=(col_BODItemW_ShipmentLT, 'min'))
            
            #Max(BOD Item W_BOD LT) - Min(BOD Item W_BOD LT) >= 2
            df_Ext_Data = df_Ext_Data[((df_Ext_Data['W_TranTime_max'] - df_Ext_Data['W_TranTime_min']) >= 2) |
                                      ((df_Ext_Data['W_ShipLT_max'] - df_Ext_Data['W_ShipLT_min']) >= 2)]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            #df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine]          = '-'
            df_Ext_Data[col_SalesDomainAP2]    = '-'
            df_Ext_Data[col_ValidationFactor]  = ('Min(Transittime) = ' + df_Ext_Data['W_TranTime_min'].astype('str') + 
                                                ', Max(Transittime) = ' + df_Ext_Data['W_TranTime_max'].astype('str') + 
                                                ', Min(Shipping L/T) = ' + df_Ext_Data['W_ShipLT_min'].astype('str') + 
                                                ', Max(Shipping L/T) = ' + df_Ext_Data['W_ShipLT_max'].astype('str') )
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, '(SET)BOD_TIME_PHASED',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BOD_DATE': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item, Site 대상으로 
            df_Ext_Data = df_in_SETBOD[df_in_SETBOD.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                       df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_BODItem_EffStartdate].notna() &
                                         (df_Ext_Data[col_BODItem_EffStartdate] > df_Ext_Data[col_BODItem_EffEnddate])]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            #df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            df_Ext_Data[col_ValidationFactor] = (
                                   'Eff Startdate = ' + df_Ext_Data[col_BODItem_EffStartdate].dt.date.astype('str') + 
                                   ', Eff Enddate = ' + df_Ext_Data[col_BODItem_EffEnddate].dt.date.astype('str'))
            
            #칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
                        
            #print_df(df_Ext_Data, 'df_(SET)BOD_DATE',False)            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)NO_ATTRIBUTE': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item, Site 대상으로
            df_Ext_Data = df_in_SETDemand[[col_VersionVersionName, col_ItemItem]].copy()
            df_Ext_Data.drop_duplicates(inplace=True)
            df_Ext_Data = df_Ext_Data.merge(df_ItemATTR, on=[col_ItemItem], how='left', suffixes=('', '_y'))
            del df_ItemATTR
            
            # ITEM 확인
            df_Ext_Item = df_Ext_Data[df_Ext_Data['Dummy'].isna()].copy()
            df_Ext_Item[col_ValidationFactor] = 'Null'
            
            # Product Group 확인
            df_Ext_PG = df_Ext_Data[df_Ext_Data[col_ItemProductGroup].isna() |
                                    (df_Ext_Data[col_ItemProductGroup] == '-')].copy()
            df_Ext_PG.fillna('Null', inplace=True)
            df_Ext_PG[col_ValidationFactor] = 'Product Group = ' + df_Ext_PG[col_ItemProductGroup].astype('str')
            
            # TV 속성 확인
            df_Ext_TV = df_Ext_Data[(df_Ext_Data[col_ItemProductGroup] == 'TV') & (
                            (df_Ext_Data[col_ItemInch].isna() | (df_Ext_Data[col_ItemInch] == '-')) |
                            (df_Ext_Data[col_ItemMarketingName].isna() | (df_Ext_Data[col_ItemMarketingName] == '-')) |
                            (df_Ext_Data[col_ItemSeries].isna() | (df_Ext_Data[col_ItemSeries] == '-'))
                            )].copy()
            #df_Ext_TV.fillna('Null',inplace=True)
            df_Ext_TV[col_ValidationFactor] = ('Product Group = ' + df_Ext_TV[col_ItemProductGroup].astype('str') +
                                             ', Inch = ' + df_Ext_TV[col_ItemInch].astype('str') +
                                             ', Marketing Name = ' + df_Ext_TV[col_ItemMarketingName].astype('str') +
                                             ', Series = ' + df_Ext_TV[col_ItemSeries].astype('str'))
            
            # MONITOR 속성 확인
            df_Ext_MNT = df_Ext_Data[(df_Ext_Data[col_ItemProductGroup] == 'MONITOR') & (
                            (df_Ext_Data[col_ItemInch].isna() | (df_Ext_Data[col_ItemInch] == '-')) |
                            (df_Ext_Data[col_ItemMarketingName].isna() | (df_Ext_Data[col_ItemMarketingName] == '-')) |
                            (df_Ext_Data[col_ItemStrategy].isna() | (df_Ext_Data[col_ItemStrategy] == '-')) |
                            (df_Ext_Data[col_ItemKPI].isna() | (df_Ext_Data[col_ItemKPI] == '-'))
                            )].copy()
            df_Ext_MNT.fillna('Null',inplace=True)
            df_Ext_MNT[col_ValidationFactor] = ('Product Group = ' + df_Ext_MNT[col_ItemProductGroup].astype('str') +
                                              ', Inch = ' + df_Ext_MNT[col_ItemInch].astype('str') +
                                              ', Marketing Name = ' + df_Ext_MNT[col_ItemMarketingName].astype('str') +
                                              ', Strategy = ' + df_Ext_MNT[col_ItemStrategy].astype('str') +
                                              ', KPI = ' + df_Ext_MNT[col_ItemKPI].astype('str'))

            # AV 속성 확인
            df_Ext_AV = df_Ext_Data[(df_Ext_Data[col_ItemProductGroup] == 'AV') & (
                            (df_Ext_Data[col_ItemMarketingName].isna() | (df_Ext_Data[col_ItemMarketingName] == '-')) |
                            (df_Ext_Data[col_ItemStrategy].isna() | (df_Ext_Data[col_ItemStrategy] == '-')) |
                            (df_Ext_Data[col_ItemChannel].isna() | (df_Ext_Data[col_ItemChannel] == '-')) |
                            (df_Ext_Data[col_ItemSeries].isna() | (df_Ext_Data[col_ItemSeries] == '-'))
                            )].copy()
            df_Ext_AV.fillna('Null',inplace=True)
            df_Ext_AV[col_ValidationFactor] = ('Product Group = ' + df_Ext_AV[col_ItemProductGroup].astype('str') +
                                             ', Marketing Name = ' + df_Ext_AV[col_ItemMarketingName].astype('str') +
                                             ', Strategy = ' + df_Ext_AV[col_ItemStrategy].astype('str') +
                                             ', Channel = ' + df_Ext_AV[col_ItemChannel].astype('str') +
                                             ', Series = ' + df_Ext_AV[col_ItemSeries].astype('str'))
            del df_Ext_Data
            
            #print_df(df_Ext_Item, 'df_Ext_Item',False)
            #print_df(df_Ext_PG, 'df_Ext_PG',False)
            #print_df(df_Ext_TV, 'df_Ext_TV',False)
            #print_df(df_Ext_MNT, 'df_Ext_MNT',False)
            #print_df(df_Ext_AV, 'df_Ext_AV',False)
            
            df_Ext_Data = pd.concat([df_Ext_Item, df_Ext_PG, df_Ext_TV, df_Ext_MNT, df_Ext_AV])
            del [df_Ext_Item, df_Ext_PG, df_Ext_TV, df_Ext_MNT, df_Ext_AV]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_LocationLocation]       = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            df_Ext_Data[col_LineLine]               = '-'
            df_Ext_Data[col_SalesDomainAP2]         = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)NO_ATTRIBUTE',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)MULTI_CONST_GROUP': #---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Const Grp Ecp : [Item].[Item] * [Group].[Group ID] 기준 Count > 1
            df_Ext_Data = df_in_SETConstGrpEcp[[col_VersionVersionName, col_ItemItem, col_GroupGroupID]].copy()
            del df_in_SETConstGrpEcp
            df_Ext_Data['Chk_Value'] = 0
            df_Ext_Data['Chk_Value'] = df_Ext_Data.groupby([col_VersionVersionName, 
                                                            col_ItemItem])[col_GroupGroupID].transform('nunique') #count(distinct)
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] > 1]  # [Item].[Item] 기준  [Group].[Group ID]  Count > 1
           
            if df_Ext_Data.empty :
                None
            else :
                df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem],
                                                  as_index=False)[col_GroupGroupID].agg(lambda x: ', '.join(set(x)))
                
                df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                #df_Ext_Data[col_ItemItem] = '-'
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
                
                #print_df(df_Ext_Data, 'df_(SET)MULTI_CONST_GROUP',False)
                df_Vld_Result_TMP = df_Ext_Data.copy()
                
            del df_Ext_Data
            
        elif row[col_MasterValidationValidationID] == '(SET)NO_LINE_MASTER': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item 대상으로
            df_Ext_Data = df_in_SETTactTime[df_in_SETTactTime.set_index([col_ItemItem]).index.isin(
                                            df_in_SETDemand.set_index([col_ItemItem]).index)
                                            ].copy()
            df_Ext_Data = df_Ext_Data[[col_VersionVersionName, col_LocationLocation, col_LineLine]]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # SETWorkCalLine(Work Cal Line_Time > 0)
            df_WorkCalLine = df_in_SETWorkCalLine[df_in_SETWorkCalLine[col_WorkCalLine_Time] > 0]
            #print_df(df_WorkCalLine, 'df_WorkCalLine',False)
            
            # SETWorkCalLine(Work Cal Line_Time > 0) 에 없는 Site, Line 추출
            df_Ext_Data = df_Ext_Data[~df_Ext_Data.set_index([col_LineLine]).index.isin(
                                      df_WorkCalLine.set_index([col_LineLine]).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion]      = '-'
            #df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2]   = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)NO_LINE_MASTER',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(SET)MULTI_FIX_GROUP': #---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Const Grp Ecp : [Item].[Item] * [Group].[Group ID] 기준 Count > 1
            df_Ext_Data = df_in_SOPFrozen.copy()
            
            #칼럼을 구분자(^)로 분리 후 explode() : 문자열을 구분자로 분리하여 행으로 변환.
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
            df_Ext_Data.rename(columns={col_SOPFrozen_FromSite:col_LocationLocation, col_SOPFrozen_Item: col_ItemItem},
                               inplace=True)
            
            if df_Ext_Data.empty :
                None
            else :
                df_Ext_Data['GroupID_SET'] = df_Ext_Data[col_GroupGroupID]
                df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC,
                                                  as_index=False)['GroupID_SET'].agg(lambda x: ', '.join(set(x)))            
                
                df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                #df_Ext_Data[col_ItemItem] = '-'
                #df_Ext_Data[col_LocationLocation] = '-'
                df_Ext_Data[col_SubLocationSubLocation] = '-'
                df_Ext_Data[col_TransModeTransMode] = '-'
                df_Ext_Data[col_BOMInfoBOMVersion] = '-'
                df_Ext_Data[col_LineLine] = '-'
                df_Ext_Data[col_SalesDomainAP2] = '-'
                df_Ext_Data[col_ValidationFactor] = 'Group ID : ' + df_Ext_Data['GroupID_SET']
                
                # 칼럼정리
                df_Ext_Data = df_Ext_Data[clist_all]
                df_Ext_Data.drop_duplicates(inplace=True)
                
                #print_df(df_Ext_Data, 'df_(SET)MULTI_FIX_GROUP',False)
                df_Vld_Result_TMP = df_Ext_Data.copy()
                
            del df_Ext_Data
            
        elif row[col_MasterValidationValidationID] == '(SET)BAL_TIME_PHASED': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item 대상으로
            #df_Ext_Data = df_in_SETBuildAheadCalW[
            #                 df_in_SETBuildAheadCalW.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
            #                 df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            df_Ext_Data = df_SETBuildAheadCalW_Demand_Sub_Loc.copy()
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            #Group by Item, Location, Sub Location
            df_Ext_Data['BAL_max'] = df_Ext_Data[col_BuildAheadCalW_Period]
            df_Ext_Data['BAL_min'] = df_Ext_Data[col_BuildAheadCalW_Period]
            df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC_Sub,
                                              as_index=False).agg({'BAL_max': 'max',
                                                                   'BAL_min': 'min'}, skipna=True)
            df_Ext_Data = df_Ext_Data[((df_Ext_Data['BAL_max'] - df_Ext_Data['BAL_min']) >= 2)]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = ('Min(BAL) = ' + df_Ext_Data['BAL_min'].astype('str') + 
                                               ', Max(BAL) = ' + df_Ext_Data['BAL_max'].astype('str') )
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)BAL_TIME_PHASED',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)BAL_DIR_SITE': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item 대상으로
            df_Ext_Data = df_SETBuildAheadCalW_Demand_Sub_Loc.copy()
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_LocationShipmentType].isin(['DIR_S', 'DIR_D'])]            
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            
            #Group by Item, Location, Sub Location
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
            
            #print_df(df_Ext_Data, 'df_(SET)BAL_DIR_SITE',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)SST_TIME_PHASED': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item 대상으로
            #df_Ext_Data = df_in_SETSSW[df_in_SETSSW.set_index([col_ItemItem, col_LocationLocation]).index.isin(
            #                           df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            df_Ext_Data = df_SETSSW_Demand_Loc.copy()
            
            #Group by Item, Location
            df_Ext_Data['SSW_SSTarget_max'] = df_Ext_Data[col_SSW_SSTarget]
            df_Ext_Data['SSW_SSTarget_min'] = df_Ext_Data[col_SSW_SSTarget]
            df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC,
                                              as_index=False).agg({'SSW_SSTarget_max': 'max',
                                                                   'SSW_SSTarget_min': 'min'}, skipna=True)
            df_Ext_Data = df_Ext_Data[((df_Ext_Data['SSW_SSTarget_max'] - df_Ext_Data['SSW_SSTarget_min']) >= 2)]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = ('Min(SS W_SS Target) = ' + df_Ext_Data['SSW_SSTarget_min'].astype('str') +
                                               ', Max(SS W_SS Target) = ' + df_Ext_Data['SSW_SSTarget_max'].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)SST_TIME_PHASED',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)SST_OVER': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand에 있는 Item 대상으로
            #df_Ext_Data = df_in_SETSSW[df_in_SETSSW.set_index([col_ItemItem, col_LocationLocation]).index.isin(
            #                           df_in_SETDemand.set_index([col_ItemItem, col_LocationLocation]).index)].copy()
            df_Ext_Data = df_SETSSW_Demand_Loc.copy()
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            #SS W_SS Target > 52
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_SSW_SSTarget] > 52]
            # Group by Item, Location, AP2
            df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation
                                             , col_SalesDomainAP2],
                                             as_index=False).agg({col_SSW_SSTarget: 'max'}, skipna=True)
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            #df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = ('Max(SS W_SS Target) = ' + df_Ext_Data[col_SSW_SSTarget].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)SST_OVER',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)SSQ_OVER': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #SETDemand에 있는 Item, Site 별 SUM(W DumDemand Quantity to SCS)
            # Group by Item, Location
            df_SETDemand_GR = df_in_SETDemand[df_in_SETDemand[col_WDumDemandQuantitytoSCS].notna()
                                             ].groupby(clist_V_ITM_LOC,
                                                       as_index=False).agg({col_WDumDemandQuantitytoSCS:'sum'})
            #print_df(df_SETDemand_GR, 'df_SETDemand_GR',False)
            
            df_Ext_Data = df_in_SETSSW.merge(df_SETDemand_GR, on=[col_VersionVersionName, col_ItemItem
                                                                , col_LocationLocation], how='inner')
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            del df_SETDemand_GR
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_SSW_SSTarget] > df_Ext_Data[col_WDumDemandQuantitytoSCS]]
            # Group by Item, Location, AP2
            df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation
                                             , col_SalesDomainAP2],
                                              as_index=False).agg({col_SSW_SSTarget: 'max'}, skipna=True)
                        
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            # df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = ('Max(SS W_SS Target) = ' + df_Ext_Data[col_SSW_SSTarget].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # print_df(df_Ext_Data, 'df_(SET)SSQ_OVER',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)PLC_RTS_DATE': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #PLC Sales_RTS Com Date > PLC Sales_RTS FW Limit Date
            df_Ext_Data = df_in_SETPLCSales[(df_in_SETPLCSales[col_PLCSales_RTSComDate].notna() &
                                             df_in_SETPLCSales[col_PLCSales_RTSFWLimitDate].notna()) &
                                            (df_in_SETPLCSales[col_PLCSales_RTSComDate] > 
                                             df_in_SETPLCSales[col_PLCSales_RTSFWLimitDate])].copy()
                        
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode]     = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            #df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                     'PLC Sales_RTS Com Date = ' + df_Ext_Data[col_PLCSales_RTSComDate].dt.date.astype('str') +
                   ', PLC Sales_RTS FW Limit Date = ' + df_Ext_Data[col_PLCSales_RTSFWLimitDate].dt.date.astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)PLC_RTS_DATE',False)            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)PLC_SRA_DATE': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #PLC Mfg_SRA Com Date > PLC Mfg_SRA FW Limit Date
            df_Ext_Data = df_in_SETPLCMfg[(df_in_SETPLCMfg[col_PLCMfg_SRAComDate].notna() &
                                           df_in_SETPLCMfg[col_PLCMfg_SRAFWLimitDate].notna()) &
                                          (df_in_SETPLCMfg[col_PLCMfg_SRAComDate] > 
                                           df_in_SETPLCMfg[col_PLCMfg_SRAFWLimitDate])].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                         'PLC Mfg_SRA Com Date = ' + df_Ext_Data[col_PLCMfg_SRAComDate].dt.date.astype('str') +
                       ', PLC Mfg_SRA FW Limit Date = ' + df_Ext_Data[col_PLCMfg_SRAFWLimitDate].dt.date.astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)PLC_SRA_DATE',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)PLANNED_EOL': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # SETDemand : Version.[Version Name], Item.[Item], Time.[Week], Location.[Location]
            # SETPLCSales : Version.[Version Name], Item.[Item], Sales Domain.[AP2]
            df_Ext_Data = df_in_SETPLCSales.merge(df_in_SETDemand, on=[col_VersionVersionName,col_ItemItem]
                                                  , how='inner', suffixes=('', '_y'))
            # Ext_Data 칼럼정리
            df_Ext_Data = df_Ext_Data[[col_VersionVersionName, col_ItemItem, col_LocationLocation
                                     , col_SalesDomainAP2, col_TimeWeek, col_PLCSales_EOSComDate]]
            
            df_Ext_Data.drop_duplicates(inplace=True)
            #SETDemand.[Time].[Week] > PLC Sales_EOS Com Date :  PLC Sales_EOS Com Date 의 Week 정보 필요.
            # Merge : df_Ext_Data & df_in_Time
            df_Ext_Data = df_Ext_Data.merge(df_in_Time, left_on=[col_PLCSales_EOSComDate], right_on=[col_TimeDay]
                                          , how='inner', suffixes=('', '_y'))
            df_Ext_Data.rename(columns={col_TimeWeek+'_y':col_EOSComWeek}, inplace=True)
            
            df_Ext_Data = df_Ext_Data.astype({col_TimeWeek:'int64', col_EOSComWeek:'int64'}, copy=True)
            
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_TimeWeek] > df_Ext_Data[col_EOSComWeek])]
            
            # group by : Version.[Version Name], Item.[Item], Location.[Location], Sales Domain.[AP2]
            df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation
                                             , col_SalesDomainAP2, col_EOSComWeek],
                                             as_index=False).agg({col_TimeWeek:'max'
                                                                #, col_EOSComWeek:'max'
                                                                })
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            #df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                  'EOS Com Week = ' + df_Ext_Data[col_EOSComWeek].astype('str') +
                ', Max(Demand Due Week) = ' + df_Ext_Data[col_TimeWeek].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)PLANNED_EOL',False)           
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)CTN': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            #Demand [Item].[Item] * [Location].[Location] 기준 On hand, Intraisit 차감 --> Sales Site 기준 ----------
            df_DemandW = df_in_DemandW.merge(df_in_WOnHand, on=clist_V_ITM_LOC, how='left')
            
            df_DemandW = df_DemandW.merge(df_in_WExp_Intransit, on=clist_V_ITM_LOC, how='left')
            del df_in_WExp_Intransit
            
            df_DemandW[col_WOnHandQuantity]   = df_DemandW[col_WOnHandQuantity].fillna(0).astype('int64')
            df_DemandW[col_WExpectedReceipts] = df_DemandW[col_WExpectedReceipts].fillna(0).astype('int64')
            
            df_DemandW['cal_qty'] = df_DemandW[col_DmdW_Qty] - (df_DemandW[col_WOnHandQuantity] + 
                                                                df_DemandW[col_WExpectedReceipts]) #차감
            #print_df(df_DemandW, 'df_DemandW',False)
            
            #Demand [Item].[Item] 기준 Plant onhand 차감 ----------------------------------------------
            # Group by Item
            df_DemandW_item = df_DemandW.groupby([col_VersionVersionName, col_ItemItem],
                                              as_index=False).agg({'cal_qty': 'sum'})
            
            #Plant onhand
            df_Plant_WOnHand = df_in_WOnHand[(df_in_WOnHand[col_LocationSiteStage].str.startswith('MF'))].copy()
            del df_in_WOnHand
            
            # Group by Item
            df_Plant_WOnHand[col_WOnHandQuantity] = df_Plant_WOnHand[col_WOnHandQuantity].fillna(0).astype('int64')
            df_Plant_WOnHand = df_Plant_WOnHand.groupby([col_VersionVersionName, col_ItemItem],
                                              as_index=False).agg({col_WOnHandQuantity: 'sum'})
            df_DemandW_item = df_DemandW_item.merge(df_Plant_WOnHand, on=[col_VersionVersionName, col_ItemItem], how='left')
            del df_Plant_WOnHand
            df_DemandW_item[col_WOnHandQuantity] = df_DemandW_item[col_WOnHandQuantity].fillna(0).astype('int64')
            df_DemandW_item['cal_qty'] = df_DemandW_item['cal_qty'].fillna(0).astype('int64')
            df_DemandW_item['last_Demand_qty'] = df_DemandW_item['cal_qty'] - df_DemandW_item[col_WOnHandQuantity] #차감
            df_DemandW_item.drop(columns=['cal_qty'], inplace=True)
            
            #최종 Demand 수량 > CTN Item Const_Frozen SOP Override Qty ------------------------------------
            # ITEM 별 합계 수량
            df_in_CTN[col_CTNItemConst_FrozenSOPOverrideQty] = (
                                           df_in_CTN[col_CTNItemConst_FrozenSOPOverrideQty].fillna(0).astype('int64'))
            
            cList_group = [col_VersionVersionName, col_ItemItem]
            df_CTN = df_in_CTN.groupby(cList_group, as_index=False).agg({col_CTNItemConst_FrozenSOPOverrideQty: "sum"})
            del df_in_CTN
            #print_df(df_CTN, 'df_CTN',False)
            
            # Merge : df_DemandW_item & df_CTN            
            df_DemandW_item = df_DemandW_item.merge(df_CTN, on=[col_VersionVersionName, col_ItemItem], how='inner')
            del df_CTN
            df_DemandW_item[col_CTNItemConst_FrozenSOPOverrideQty] = (
                                      df_DemandW_item[col_CTNItemConst_FrozenSOPOverrideQty].fillna(0).astype('int64'))
            
            # 최종 Demand 수량 > CTN Item Const_Frozen SOP Override Qty
            df_DemandW_item['last_Demand_qty'] = df_DemandW_item['last_Demand_qty'].fillna(0).astype('int64')
            df_DemandW_item = (df_DemandW_item[df_DemandW_item['last_Demand_qty'] 
                                               > df_DemandW_item[col_CTNItemConst_FrozenSOPOverrideQty]])
            
            #print_df(df_DemandW_item, 'df_DemandW_item',False)
            
            # Merge df_DemandW & df_DemandW_item
            df_Ext_Data = df_DemandW.merge(df_DemandW_item, on=[col_VersionVersionName, col_ItemItem], how='inner')
            del [df_DemandW, df_DemandW_item]
            
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
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
            
            #print_df(df_Ext_Data, '(SET)CTN',False) 
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            
        elif row[col_MasterValidationValidationID] == '(SET)MP_SRA_DATE': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Max 말고 Category Actual인걸로 처리
            df_NewModel = df_in_NewModel.copy()
            df_NewModel.rename(columns={col_ItemNewModelItem: col_ItemItem}, inplace=True)
            df_NewModel['valeue'] = np.where((df_NewModel[col_CategoryCategory] == 'Actual'), 1, 2)
            
            df_NewModel['rn'] = df_NewModel.groupby(
                       clist_V_ITM_LOC, as_index=False)['valeue'].rank(method='first', ascending=True).astype('int64')            
            df_NewModel = df_NewModel[df_NewModel['rn'] == 1]
            #print_df(df_NewModel, 'df_NewModel',False)
            
            #  [Location].[Site Stage].filter(#.Name startswith "MF")
            df_Ext_Data = df_in_PLCMfg[(df_in_PLCMfg[col_LocationSiteStage].str.startswith('MF'))].copy()
            # Merge 
            df_Ext_Data = df_Ext_Data.merge(df_NewModel, on=clist_V_ITM_LOC, how='inner')
            del df_NewModel
            #[PLC Mfg_SRA FW Limit Date] > [New Model_Mfg Date]
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_PLCMfg_SRAFWLimitDate].notna() &
                                      df_Ext_Data[col_NewModel_MfgDate].notna() &
                                      (df_Ext_Data[col_PLCMfg_SRAFWLimitDate] > df_Ext_Data[col_NewModel_MfgDate])]
            

            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            #df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                      'PLC Mfg_SRA FW Limit Date = ' + df_Ext_Data[col_PLCMfg_SRAFWLimitDate].dt.date.astype('str') +
                      ', New Model_Mfg Date = ' + df_Ext_Data[col_NewModel_MfgDate].dt.date.astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, '(SET)MP_SRA_DATE',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            
        elif row[col_MasterValidationValidationID] == '(SET)EXCESSIVE_INV_PRODUCT': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_SETInv_SUM & df_SETLastInv_SUM : sum(SETInventory.Inv_Qty), sum(SETLastInventory.Inv_Qty)
            df_Ext_Data = df_SETInv_SUM.merge(df_SETLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))
            
            #SETLastInventory.Inv_Qty > 0
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_Inv_Qty + '_last'] > 0]
            # ABS(SETIntransit.Inv_Qty - SETLastIntransit.Inv_Qty) / SETLastIntransit.Inv_Qty) > 0.5
            df_Ext_Data['cal_rate'] = (abs(df_Ext_Data[col_Inv_Qty] - df_Ext_Data[col_Inv_Qty + '_last'])
                                       / df_Ext_Data[col_Inv_Qty + '_last'])
            
            df_Ext_Data = df_Ext_Data[df_Ext_Data['cal_rate'] > 0.5]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'Last Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty + '_last'].astype('str') +
                ', Current Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty].astype('str'))
                        
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)EXCESSIVE_INV_PRODUCT',False) 
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)NO_INV_REGION': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_SETInv_SUM & df_SETLastInv_SUM : sum(SETInventory.Inv_Qty), sum(SETLastInventory.Inv_Qty)
            df_Ext_Data = df_SETInv_SUM.merge(df_SETLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              ,how='inner', suffixes=('', '_last'))
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            # SETInventory.Inv_Qty = 0 & SETLastInventory.Inv_Qty > 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)]
            #df_Ext_Data = df_Ext_Data[~(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)] # 임시 test용
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'Last Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty + '_last'].astype('str') +
                ', Current Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)NO_INV_REGION',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)EXCESSIVE_INTRANSIT_PRODUCT': #----------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_SETIntr_SUM & df_SETLastIntr_SUM : sum(SETIntransit.Intr_Qty), sum(SETLastIntransit.Intr_Qty)
            df_Ext_Data = df_SETIntr_SUM.merge(df_SETLastIntr_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))
            
            # SETLastIntransit.Intr_Qty > 0 > 0 & SETIntransit.Intr_Qty - SETLastIntransit.Intr_Qty < 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Intr_Qty + '_last'] > 0) &
                                      ((df_Ext_Data[col_Intr_Qty] - df_Ext_Data[col_Intr_Qty + '_last']) < 0)
                                      ]
            
            # ABS(SETIntransit.Intr_Qty - SETLastIntransit.Intr_Qty) / SETLastIntransit.Intr_Qty) > 0.5
            df_Ext_Data['cal_rate'] = (abs(df_Ext_Data[col_Intr_Qty] - df_Ext_Data[col_Intr_Qty + '_last'])
                                       / df_Ext_Data[col_Intr_Qty + '_last'])
            df_Ext_Data = df_Ext_Data[df_Ext_Data['cal_rate'] > 0.5]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'Last Week Intransit Qty = ' + df_Ext_Data[col_Intr_Qty + '_last'].astype('str') +
                ', Current Week Intransit Qty = ' + df_Ext_Data[col_Intr_Qty].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)EXCESSIVE_INTRANSIT_PRODUCT',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)NO_INTRANSIT_REGION': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_SETIntr_SUM & df_SETLastIntr_SUM : sum(SETIntransit.Intr_Qty), sum(SETLastIntransit.Intr_Qty)
            df_Ext_Data = df_SETIntr_SUM.merge(df_SETLastIntr_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))
            
            # SETIntransit.Intr_Qty = 0 & SETLastIntransit.Intr_Qty > 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Intr_Qty] == 0) & (df_Ext_Data[col_Intr_Qty + '_last'] > 0)]
            #df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Intr_Qty] == 1) & (df_Ext_Data[col_Intr_Qty + '_last'] > 0)] # 임시 test용
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'Last Week Intransit Qty = ' + df_Ext_Data[col_Intr_Qty + '_last'].astype('str') +
                ', Current Week Intransit Qty = ' + df_Ext_Data[col_Intr_Qty].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(SET)NO_INTRANSIT_REGION',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)        

        elif row[col_MasterValidationValidationID] == '(LCM)BOM_MFGPLAN': #----------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # MFGPlan.[Item].[Item] == Fullbom.[To Item].[To Item] & MFGPlan.[Location].[Location] == Fullbom.[To Location].[To Location]
            #--> Fullbom 기준 데이터 없을 경우
            df_Ext_Data = df_in_MFGPlan_LCM[~df_in_MFGPlan_LCM.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                               df_in_Fullbom_LCM.set_index([col_ToItemToItem, col_ToLocationToLocation]).index)].copy()
            
            df_Ext_Data[col_MfgPlan_Qty] = df_Ext_Data[col_MfgPlan_Qty].fillna(0).astype('int64')
            df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                              as_index=False).agg({col_MfgPlan_Qty: 'sum'}, skipna=True)
            
            #print_df(df_Ext_Data, 'df_Ext_Data', False)
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
            
            #print_df(df_Ext_Data, 'df_(LCM)BOM_MFGPLAN',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[col_MasterValidationValidationID] == '(LCM)BOD_PRIORITY': #----------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Demand.[Item].[Item] == Fullbom.[Item].[Item] 인 Fullbom
            df_Ext_Data = df_in_Fullbom_LCM[df_in_Fullbom_LCM.set_index([col_ItemItem]).index.isin(
                                             df_in_DemandW.set_index([col_ItemItem]).index)].copy()
            # Merge : df_in_Fullbom_LCM & df_in_LCMBOD
            # Fullbom.[To Item].[To Item] ==  BOD.[Item].[Item]
            # Fullbom.[To Location].[To Location] == BOD.[Location].[Location] 
            # Fullbom.[Location].[Location] == BOD.[Sub Location].[Sub Location]
            df_Ext_Data.rename(columns={col_ItemItem: 'Item.[Item]_ORG',
                                        col_ToItemToItem: col_ItemItem,
                                        col_LocationLocation: col_SubLocationSubLocation,
                                        col_ToLocationToLocation: col_LocationLocation}, inplace=True)
            df_Ext_Data = df_Ext_Data.merge(df_in_LCMBOD, on=clist_V_ITM_LOC_Sub, how='inner', suffixes=('', '_y'))
            
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_BODItem_Priority].notna()].copy()
            df_Ext_Data[col_BODItem_Priority] = df_Ext_Data[col_BODItem_Priority].astype('int64')
            df_Ext_Data['Chk_Value'] = 0
            df_Ext_Data['Chk_Value'] = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation,
                                               col_SubLocationSubLocation, 
                                               col_BODItem_Priority])['Chk_Value'].transform('count')
            
            #BOD.[Item].[Item], BOD.[Location].[Location], BOD.[Sub Location].[Sub Location] 기준 
            # Measure.[BOD Item_Priority]가 같은 경우
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] >= 2]  # [BOD Item_Priority]가 동일한것이 2개이상
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            # df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(LCM)BOD_PRIORITY',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[col_MasterValidationValidationID] == '(LCM)BOD_MFGPLAN': #----------------------------------
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
            #print_df(df_Ext_Data, 'df_Ext_Data',False,False)
            # Horizon 기준 Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Eff Enddate]가 겹치는 구간이 없을 경우
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] == 0]  # 결과가 0 인 Item
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
            
            #print_df(df_Ext_Data, 'df_(LCM)BOD_MFGPLAN',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[col_MasterValidationValidationID] == '(LCM)BOD_DEMAND': #----------------------------------
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
            
            # print_df(df_Ext_Data, 'df_(LCM)BOD_DEMAND',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(O/C)BOD_DEMAND':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Demand.[Item].[Item] == Fullbom.[Item].[Item] 
            # --> Fullbom.[Item Material].[Item Material], Fullbom.[To Location].[To Location]
            df_Ext_Data = df_in_Fullbom_LCM[df_in_Fullbom_LCM.set_index([col_ItemItem]).index.isin(
                                            df_in_DemandW.set_index([col_ItemItem]).index)].copy()
            
            # Fullbom.[Item Material].[Item Material] ==  BOD.[Item].[Item] 
            # Fullbom.[To Location].[To Location] == BOD.[Sub Location].[Sub Location]
            # --> BOD 기준 데이터 없음
            # Merge를 위해 칼럼명 변경
            df_Ext_Data[col_LocationLocation + '_ORG'] = df_Ext_Data[col_LocationLocation]
            df_Ext_Data[col_LocationLocation] = df_Ext_Data[col_ToLocationToLocation]
            df_Ext_Data.rename(columns={col_ItemItem: 'Item.[Item]_ORG',
                                        col_ItemMaterialItemMaterial: col_ItemItem,
                                        col_ToLocationToLocation: col_SubLocationSubLocation}, inplace=True)
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            # BOD 기준 데이터 없음
            df_Ext_Data = df_Ext_Data[~df_Ext_Data.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
                                      df_in_LCMBOD.set_index([col_ItemItem, col_SubLocationSubLocation]).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # print_df(df_Ext_Data, 'df_(O/C)BOD_DEMAND',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOD_EFFECTIVENESS':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Demand.[Item].[Item] == Fullbom.[Item].[Item] 
            # --> Fullbom.[To Item].[To Item], Fullbom.[To Location].[To Location], Fullbom.[Location].[Location]
            df_Ext_Data = df_in_Fullbom_LCM[df_in_Fullbom_LCM.set_index([col_ItemItem]).index.isin(
                                            df_in_DemandW.set_index([col_ItemItem]).index)].copy()
            
            
            
            # Fullbom.[To Item].[To Item] ==  BOD.[Item].[Item]
            # Fullbom.[To Location].[To Location] == BOD.[Location].[Location] 
            # Fullbom.[Location].[Location] == BOD.[Sub Location].[Sub Location]            
            df_Ext_Data.rename(columns={col_ItemItem: 'Item.[Item]_ORG',
                                        col_ToItemToItem: col_ItemItem,
                                        col_LocationLocation: col_SubLocationSubLocation,
                                        col_ToLocationToLocation: col_LocationLocation}, inplace=True)
            # Merge : Fullbom & df_in_LCMBOD
            df_Ext_Data = df_Ext_Data.merge(df_in_LCMBOD, on=clist_V_ITM_LOC_Sub, how='inner', suffixes=('', '_y'))
            
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
            #print_df(df_Ext_Data, 'df_Ext_Data',False)
            # --> Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Eff Enddate]가 Horizon 기준 겹치는 구간 없음
            df_Ext_Data = df_Ext_Data[df_Ext_Data['Chk_Value'] == 0]  # 결과가 0 인 Item
            
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
            
            #print_df(df_Ext_Data, 'df_(LCM)BOD_EFFECTIVENESS',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOD_TIME_PHASED':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Demand.[Item].[Item] == Fullbom.[Item].[Item] 
            # --> Fullbom.[To Item].[To Item], Fullbom.[To Location].[To Location], Fullbom.[Location].[Location]
            df_Ext_Data = df_in_Fullbom_LCM[df_in_Fullbom_LCM.set_index([col_ItemItem]).index.isin(
                                            df_in_DemandW.set_index([col_ItemItem]).index)].copy()
            
            # Fullbom.[To Item].[To Item] ==  BOD.[Item].[Item]
            # Fullbom.[To Location].[To Location] == BOD.[Location].[Location] 
            # Fullbom.[Location].[Location] == BOD.[Sub Location].[Sub Location]
            df_Ext_Data.rename(columns={col_ItemItem: 'Item.[Item]_ORG',
                                        col_ToItemToItem: col_ItemItem,
                                        col_LocationLocation: col_SubLocationSubLocation,
                                        col_ToLocationToLocation: col_LocationLocation}, inplace=True)
            
            # df_in_LCMBODW : Fullbom 존재 확인
            df_Ext_Data = df_in_LCMBODW[df_in_LCMBODW.set_index(clist_V_ITM_LOC_Sub).index.isin(
                                        df_Ext_Data.set_index(clist_V_ITM_LOC_Sub).index)].copy()
            
            # BOD Item W_Tran Time ==>  BOD Item W_BOD LT 로 메져 변경
            df_Ext_Data[col_BODItemW_ShipmentLT] = df_Ext_Data[col_BODItemW_ShipmentLT].fillna(0).astype('int64')
            df_Ext_Data[col_BODItemW_BODLT] = df_Ext_Data[col_BODItemW_BODLT].fillna(0).astype('int64')
            df_Ext_Data['Chk_Value'] = df_Ext_Data[col_BODItemW_ShipmentLT] + df_Ext_Data[col_BODItemW_BODLT]
            
            # GROUP BY : TranTime, ShipLT
            # --> 주차 기준 sum(BOD Item W_Shipment LT + BOD Item W_Tran Time)의 Max - Min >=2 (일자로는 14)
            df_Ext_Data = df_Ext_Data.groupby(clist_bod, as_index=False).agg(MIN_BOD_LT=('Chk_Value', 'min'),
                                                                             MAX_BOD_LT=('Chk_Value', 'max'))
            df_Ext_Data = df_Ext_Data[((df_Ext_Data['MAX_BOD_LT'] - df_Ext_Data['MIN_BOD_LT']) >= 14)]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            #df_Ext_Data[col_SubLocationSubLocation] = '-'
            #df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            # Ex) Min BOD L/T : xxx, Max BOD L/T : yyy
            df_Ext_Data[col_ValidationFactor] = ('Min BOD L/T : ' + df_Ext_Data['MIN_BOD_LT'].astype('str') +
                                                 ', Max BOD L/T : ' + df_Ext_Data['MAX_BOD_LT'].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(LCM)BOD_TIME_PHASED',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)BOD_DATE':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Demand.[Item].[Item] == Fullbom.[Item].[Item] 
            # --> Fullbom.[To Item].[To Item], Fullbom.[To Location].[To Location], Fullbom.[Location].[Location]
            df_Ext_Data = df_in_Fullbom_LCM[df_in_Fullbom_LCM.set_index([col_ItemItem]).index.isin(
                                              df_in_DemandW.set_index([col_ItemItem]).index)].copy()
            
            # Fullbom.[To Item].[To Item] ==  BOD.[Item].[Item]
            # Fullbom.[To Location].[To Location] == BOD.[Location].[Location] 
            # Fullbom.[Location].[Location] == BOD.[Sub Location].[Sub Location]
            df_Ext_Data.rename(columns={col_ItemItem: 'Item.[Item]_ORG',
                                        col_ToItemToItem: col_ItemItem,
                                        col_LocationLocation: col_SubLocationSubLocation,
                                        col_ToLocationToLocation: col_LocationLocation}, inplace=True)
            
            # df_in_LCMBOD : Fullbom 존재 확인
            df_Ext_Data = df_in_LCMBOD[df_in_LCMBOD.set_index(clist_V_ITM_LOC_Sub).index.isin(
                                       df_Ext_Data.set_index(clist_V_ITM_LOC_Sub).index)].copy()
            
            # --> Measure.[BOD Item_Eff Startdate] > Measure.[BOD Item_Eff Enddate]
            df_Ext_Data = df_Ext_Data[df_Ext_Data[
                                         col_BODItem_EffStartdate].notna() &
                                         (df_Ext_Data[col_BODItem_EffStartdate] > df_Ext_Data[col_BODItem_EffEnddate])]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            # df_Ext_Data[col_SubLocationSubLocation] = '-'
            # df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            # Ex) EFF Start Date : yyyy-mm-dd, EFF End Date : yyyy-mm-dd            
            df_Ext_Data[col_ValidationFactor] = (
                                   'Eff Star tdate : ' + df_Ext_Data[col_BODItem_EffStartdate].dt.date.astype('str') + 
                                   ', Eff End date : ' + df_Ext_Data[col_BODItem_EffEnddate].dt.date.astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # print_df(df_Ext_Data, 'df_(LCM)BOD_DATE',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)NO_ATTRIBUTE':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            #[Item.[Item] 기준 각 Field 값 중 "-"가 있는 경우
            df_Ext_Data = df_in_ITEMAttr_LCM[(df_in_ITEMAttr_LCM[col_ItemCYCode] == '-') |
                                             (df_in_ITEMAttr_LCM[col_ItemDPCode] == '-') |
                                             (df_in_ITEMAttr_LCM[col_ItemGrade] == '-') |
                                             (df_in_ITEMAttr_LCM[col_ItemCellVendor] == '-') |
                                             (df_in_ITEMAttr_LCM[col_ItemOpenCell] == '-') |
                                             (df_in_ITEMAttr_LCM[col_ItemSETItem] == '-')].copy()
            del df_in_ITEMAttr_LCM
            df_Ext_Data[col_VersionVersionName] = VERSION_VALUE
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            # Ex) CY Code: xxx, DP Code : yyy, Grade : zzz, Cell Vendor : aaa, Open Cell : sss, Set Item : eee
            df_Ext_Data[col_ValidationFactor] = ('CY Code: ' + df_Ext_Data[col_ItemCYCode] +
                                                 ', DP Code : ' + df_Ext_Data[col_ItemDPCode] +
                                                 ', Grade : ' + df_Ext_Data[col_ItemGrade] +
                                                 ', Cell Vendor : ' + df_Ext_Data[col_ItemCellVendor] +
                                                 ', Open Cell : ' + df_Ext_Data[col_ItemOpenCell] +
                                                 ', Set Item : ' + df_Ext_Data[col_ItemSETItem] )
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(LCM)NO_ATTRIBUTE',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)MULTI_CONST_GROUP':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # [Item].[Item] 기준 두개 이상의 Group ID를 가지고 있는 경우
            # Const Grp Ecp : [Item].[Item] * [Group].[Group ID] 기준 Count > 1
            df_Ext_Data = df_in_LCMConstGrpEcp[[col_VersionVersionName, col_ItemItem, col_GroupGroupID]].copy()            
            del df_in_LCMConstGrpEcp
            df_Ext_Data['Chk_Value'] = 0
            df_Ext_Data['Chk_Value'] = df_Ext_Data.groupby([col_VersionVersionName,
                                                            col_ItemItem])[col_GroupGroupID].transform('nunique') #count(distinct)
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
                
                # print_df(df_Ext_Data, 'df_(LCM)MULTI_CONST_GROUP',False)
                df_Vld_Result_TMP = df_Ext_Data.copy()
            
            del df_Ext_Data
        
        elif row[col_MasterValidationValidationID] == '(LCM)NO_LINE_MASTER':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # TACT에서 distinct Location(Site), Line 정보를 읽어서            
            df_Ext_Data = df_in_LCMWorkCalLine[
                                    df_in_LCMWorkCalLine.set_index([col_LocationLocation, col_LineLine]).index.isin(
                                    df_in_LCMTactTime.set_index([col_LocationLocation, col_LineLine]).index)].copy()
            
            # WC.[Work Cal Line_Time] > 0  Site, Line 추출
            df_WorkCalLine = df_Ext_Data[df_Ext_Data[col_WorkCalLine_Time] > 0]
            #print_df(df_WorkCalLine, 'df_WorkCalLine',False)
            
            # WC.[Work Cal Line_Time] > 0에 없는 Site, Line 추출
            df_Ext_Data = df_Ext_Data[~df_Ext_Data.set_index([col_LineLine]).index.isin(
                                       df_WorkCalLine.set_index([col_LineLine]).index)].copy()
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_ItemItem] = '-'
            #df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            #df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = '-'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # print_df(df_Ext_Data, 'df_(LCM)NO_LINE_MASTER',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(LCM)MULTI_FIX_GROUP': #---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # Const Grp Ecp : [Item].[Item] * [Group].[Group ID] 기준 Count > 1
            df_Ext_Data = df_in_SOPFrozen.copy()
            
            #칼럼을 구분자(^)로 분리 후 explode() : 문자열을 구분자로 분리하여 행으로 변환.
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
            df_Ext_Data.rename(columns={col_SOPFrozen_FromSite:col_LocationLocation, col_SOPFrozen_Item: col_ItemItem},
                               inplace=True)
            
            if df_Ext_Data.empty :
                None
            else :
                df_Ext_Data['GroupID_SET'] = df_Ext_Data[col_GroupGroupID]
                df_Ext_Data = df_Ext_Data.groupby(clist_V_ITM_LOC,
                                                  as_index=False)['GroupID_SET'].agg(lambda x: ', '.join(set(x)))            
                
                df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
                #df_Ext_Data[col_ItemItem] = '-'
                #df_Ext_Data[col_LocationLocation] = '-'
                df_Ext_Data[col_SubLocationSubLocation] = '-'
                df_Ext_Data[col_TransModeTransMode] = '-'
                df_Ext_Data[col_BOMInfoBOMVersion] = '-'
                df_Ext_Data[col_LineLine] = '-'
                df_Ext_Data[col_SalesDomainAP2] = '-'
                df_Ext_Data[col_ValidationFactor] = 'Group ID : ' + df_Ext_Data['GroupID_SET']
                
                # 칼럼정리
                df_Ext_Data = df_Ext_Data[clist_all]
                df_Ext_Data.drop_duplicates(inplace=True)
                
                #print_df(df_Ext_Data, 'df_(LCM)MULTI_FIX_GROUP',False)
                df_Vld_Result_TMP = df_Ext_Data.copy()
                
            del df_Ext_Data
        
        elif row[col_MasterValidationValidationID] == '(LCM)SST_TIME_PHASED': #---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
                        
            # SS.[Item].[Item] == SSW.[Item].[Item] 
            # SS.[Location].[Location] == SSW.[Location].[Location]
            # SS.[SS_SS Type] != "MIN_ONHAND"
            # --> SSW 값 기준
            df_LCMSS = df_in_LCMSS[df_in_LCMSS[col_SS_SSType] != "MIN_ONHAND"].copy()
            
            df_LCMSSW = df_in_LCMSSW[df_in_LCMSSW.set_index(clist_V_ITM_LOC).index.isin(
                                     df_LCMSS.set_index(clist_V_ITM_LOC).index)].copy()
            del df_LCMSS
            
            # SSW(Item, Location) 정보에서 아래 조건의 Item, Site 추출
            #     . 조건 : Group by Item, Location
            #               Max(SS W_SS Target) - Min(SS W_SS Target) >= 2
            
            # Group by Item, Location
            df_LCMSSW['SSW_SSTarget_max'] = df_LCMSSW[col_SSW_SSTarget]
            df_LCMSSW['SSW_SSTarget_min'] = df_LCMSSW[col_SSW_SSTarget]
            df_Ext_Data = df_LCMSSW.groupby(clist_V_ITM_LOC,
                                            as_index=False).agg({'SSW_SSTarget_max': 'max',
                                                                 'SSW_SSTarget_min': 'min'}, skipna=True)
            
            df_Ext_Data = df_Ext_Data[((df_Ext_Data['SSW_SSTarget_max'] - df_Ext_Data['SSW_SSTarget_min']) >= 2)]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            # Ex) Max SS Target = xxx, Min SS Target = xxx
            df_Ext_Data[col_ValidationFactor] = (
                                            'Max SS Target = ' + df_Ext_Data['SSW_SSTarget_min'].astype('str') +
                                          ', Min SS Target = ' + df_Ext_Data['SSW_SSTarget_max'].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # print_df(df_Ext_Data, 'df_(LCM)SST_TIME_PHASED',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            

        elif row[col_MasterValidationValidationID] == '(LCM)SST_OVER': #---------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            # SSW(Item, Location) 정보에서 아래 조건의 Item, Site 추출
            #     . 조건 :  SS W_SS Target > 52
            df_Ext_Data = df_in_LCMSSW[df_in_LCMSSW[col_SSW_SSTarget] > 52].copy()
            
            df_Ext_Data = df_Ext_Data.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation
                                             , col_SalesDomainAP2],
                                              as_index=False).agg({col_SSW_SSTarget: 'max'}, skipna=True) #확인필요
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            #df_Ext_Data[col_SalesDomainAP2] = '-'
            # Ex) SS Target = xxx Weeks
            df_Ext_Data[col_ValidationFactor] = 'SS Target = ' + df_Ext_Data[col_SSW_SSTarget].astype('str') + ' Weeks'
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            # print_df(df_Ext_Data, 'df_(LCM)SST_OVER',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(LCM)EXCESSIVE_INV_PRODUCT': #----------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_LCMInv_SUM & df_LCMLastInv_SUM : sum(LCMInventory.Inv_Qty), sum(LCMLastInventory.Inv_Qty)
            df_Ext_Data = df_LCMInv_SUM.merge(df_LCMLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))
            
            #LCMLastInventory.Inv_Qty > 0
            df_Ext_Data = df_Ext_Data[df_Ext_Data[col_Inv_Qty + '_last'] > 0]
            # ABS(LCMIntransit.Inv_Qty - LCMLastIntransit.Inv_Qty) / LCMLastIntransit.Inv_Qty) > 0.5
            df_Ext_Data['cal_rate'] = (abs(df_Ext_Data[col_Inv_Qty] - df_Ext_Data[col_Inv_Qty + '_last'])
                                       / df_Ext_Data[col_Inv_Qty + '_last'])
            
            df_Ext_Data = df_Ext_Data[df_Ext_Data['cal_rate'] > 0.5]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'Last Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty + '_last'].astype('str') +
                ', Current Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty].astype('str'))
                        
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(LCM)EXCESSIVE_INV_PRODUCT',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(LCM)NO_INV_PLANT': #------------------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_LCMInv_SUM & df_LCMLastInv_SUM : sum(LCMInventory.Inv_Qty), sum(LCMLastInventory.Inv_Qty)
            df_Ext_Data = df_LCMInv_SUM.merge(df_LCMLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              ,how='inner', suffixes=('', '_last'))
            # LCMInventory.Inv_Qty = 0 & LCMLastInventory.Inv_Qty > 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)]
            #df_Ext_Data = df_Ext_Data[~(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)] # 임시 test용
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'Last Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty + '_last'].astype('str') +
                ', Current Week Inventory Qty = ' + df_Ext_Data[col_Inv_Qty].astype('str'))
                        
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(LCM)NO_INV_PLANT',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(LCM)EXCESSIVE_INTRANSIT_PRODUCT': #----------------------------
            CHK_I = 1 
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_LCMIntr_SUM & df_LCMLastIntr_SUM : sum(LCMIntransit.Intr_Qty), sum(LCMLastIntransit.Intr_Qty)
            df_Ext_Data = df_LCMIntr_SUM.merge(df_LCMLastIntr_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))
            
            # LCMLastIntransit.Intr_Qty > 0 > 0 & LCMIntransit.Intr_Qty - LCMLastIntransit.Intr_Qty < 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Intr_Qty + '_last'] > 0)
                                    & ((df_Ext_Data[col_Intr_Qty] - df_Ext_Data[col_Intr_Qty + '_last']) < 0)
                                      ]
            
            # ABS(LCMIntransit.Intr_Qty - LCMLastIntransit.Intr_Qty) / LCMLastIntransit.Intr_Qty) > 0.5
            df_Ext_Data['cal_rate'] = (abs(df_Ext_Data[col_Intr_Qty] - df_Ext_Data[col_Intr_Qty + '_last'])
                                       / df_Ext_Data[col_Intr_Qty + '_last'])
            df_Ext_Data = df_Ext_Data[df_Ext_Data['cal_rate'] > 0.5]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'Last Week Intransit Qty = ' + df_Ext_Data[col_Intr_Qty + '_last'].astype('str') +
                ', Current Week Intransit Qty = ' + df_Ext_Data[col_Intr_Qty].astype('str'))
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, 'df_(LCM)EXCESSIVE_INTRANSIT_PRODUCT',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)  
            
            # if End -------------------------------------------------------------------------------------------------
        
        #row_count, col_count = df_Vld_Result_TMP.shape
        #note(f'=====> {row[col_MasterValidationValidationID]} : rows : {row_count}   ')
        
        #처리 대상 ValidationID 만 결과건수 출력
        if CHK_I == 1 :
            row_count, col_count = df_Vld_Result_TMP.shape
            note(f'=====> {row[col_MasterValidationValidationID]} : rows : {row_count}   ')
        
        if df_Vld_Result_TMP.empty :
            None 
        else :
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)            
            if df_Vld_Result_All.empty:
                df_Vld_Result_All = df_Vld_Result_TMP.copy()
            else :
                df_Vld_Result_All = pd.concat([df_Vld_Result_All, df_Vld_Result_TMP])
                
        del df_Vld_Result_TMP
    
    del [df_in_MasterValidation, df_in_SETItemSite, df_in_LCMItemSite, df_in_SETIntransit
       , df_in_LCMIntransit, df_in_SETDemand, df_in_LCMDemand, df_in_SETInventory
       , df_in_LCMInventory, df_in_SETMfgPlan_SFC, df_in_LCMMfgPlan_SFC, df_SETBOM
       , df_in_PlanHorizon, df_in_Time, df_in_SETBOD, df_in_LCMBOD, df_in_SETBODW, df_in_LCMBODW
       , df_in_CurrentDay, df_in_SOPFrozen, df_in_SETTactTime, df_in_LCMTactTime
       , df_in_SETWorkCalLine, df_in_LCMWorkCalLine, df_in_SETBuildAheadCalW, df_in_SETSSW, df_in_LCMSSW
       , df_in_SETPLCSales, df_in_SETPLCMfg
       , df_SETInv_SUM, df_SETLastInv_SUM, df_SETIntr_SUM, df_SETLastIntr_SUM
       , df_LCMInv_SUM, df_LCMLastInv_SUM, df_LCMIntr_SUM, df_LCMLastIntr_SUM
       , df_SETBOD_Demand_Sub_Loc, df_SETBuildAheadCalW_Demand_Sub_Loc, df_SETSSW_Demand_Loc
       , df_in_DemandW, df_in_PLCMfg, df_in_NewModel, df_in_Fullbom_LCM, df_in_MFGPlan_LCM]
    note(f'=====> for End ======================================================= ')
        
    #print_df(df_Vld_Result_All, 'df_Vld_Result_All',False)
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
    #df_out_MstValidResult[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_MstValidResult.shape
    note(f'=====> Final df_out_MstValidResult rows : {row_count}, column : {col_count}')    
    print_df(df_out_MstValidResult, 'df_out_MstValidResult',False)
    
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
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()