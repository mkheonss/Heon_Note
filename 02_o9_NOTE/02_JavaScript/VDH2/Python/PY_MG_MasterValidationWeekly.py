"""
* 프로그램명
    - PY_MG_MasterValidationWeekly

* 내용
    - Master Validation Data 구성

* 변경이력
    - 2026.01.22 / 양희영 / Create
    - 2026.01.30 / 양희영 / Update
    - 2026.02.22 / 임채수 / Update
    - 2026.03.04 / 양희영 / Update

* Flow Summary

* Execution
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함

* Input Tables
    - df_in_MasterValidation : Dimension : Master Validation
                               select ([Master Validation].[Validation Stage] * [Master Validation].[Validation Grp01] * [Master Validation].[Validation Grp02] * [Master Validation].[Validation Type] *
                               [Master Validation].[Validation Owner] * [Master Validation].[Validation ID] * [Master Validation].[Validation Name])
                               on row include memberproperties  {[Master Validation].[Validation ID],[Validation ID Desc]} {[Master Validation].[Validation Name],[Validation Name Desc]};
    - df_in_ItemSite : df_in_SETItemSite, df_in_LCMItemSite 대체
                       select (&CWVUI * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Location].[Location] ) on row,
                       ({Measure.[Item Site Asn_Cur Status]}) on column where {Measure.[Item Site Asn_Cur Status] IN {"ACTIVE", "PLANNED"}};
    - df_in_Intransit : 2개버전 SCOPE
                        Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Location].[Location]) on row,
                        ({Measure.[Intr_From Site ID], Measure.[Intr_Qty], Measure.[Dummy]}) on column;
    - df_in_Inventory : 2개버전 SCOPE
                        Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].filter(#.Name in {"SET","LCM"}) * [Item].[Plan Group] * [Item].[Product Group] * [Time].[Week] *
                        [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv_KRW Amount], Measure.[Inv_Plan ID], Measure.[Inv_Qty], Measure.[Inv_Sales ID], Measure.[Inv_To Site],
                        Measure.[Inv_USD Amount]}) on column;
    -- df_in_InventoryShuffle : 2개버전 SCOPE
                               Select ([Version].[Version Name] * &NSUISiteEURHubView * [Item].[Item]) on row, ({Measure.[Inv Shuffle_Qty]}) on column where {Measure.[Inv Shuffle_Qty] > 0};
    -- df_in_VersionName : SELECT (&CWVUI);
    -- df_in_MfgPlanSET : Select (&CWVUI * [Location].[Location] * [Item].[Product Group] * Item.[Item] * [Documents].[OrderlineID] ) on row, 
                          ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Finish Date], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_To Site ID]}) on column 
                          where {Location.[Site Stage].filter(#.Name in {[MF_SET]}), ~isnull(Measure.[Mfg Plan_BOM Version])} orderby [Location].[Location].Name, Item.[Product Group].Name;
    -- df_in_MfgPlanLCM : Select (&CWVUI * [Location].[Location] * [Item].[Product Group] * Item.[Item] * [Documents].[OrderlineID]) on row, 
                          ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Finish Date], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_To Site ID]}) on column where 
                          {Location.[Site Stage].filter(#.Name in {[MF_LCM],[MF_LCM_EX]})} orderby [Location].[Location].Name, Item.[Product Group].Name;
    -- df_in_FullBom_LCM : Select (&CWVUI * [Location].[Location] * [To Location].[To Location] * [To Item].[To Item] * [Item].[Item]) on row, ({Measure.[Full BOM_EOP Date], Measure.[Dummy]}) on column 
                           where {[Item].[Item Stage].filter(#.Name in {[SET]}), [To Item].[To Item Stage].filter(#.Name in {[LCM]}), [To Location].[To Site Stage].filter(#.Name in {[MF_LCM],[MF_LCM_EX]}), 
                           TODATETIME(Measure.[Full BOM_Eff Enddate])>=DateAdd(now(),-7,"Day")};

//df_in_Time
Select (&MPHorizon * Time.[Day]);

* Output Tables
    - df_out_MstValidResult : MG : Mst Valid Result
                          Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] *
                          [Master Validation].[Validation ID] * [Line].[Line] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Mst Valid Result_Validation Factor]}) on column;

* 테스트 스크립트 :
    EXEC plugin instance [PY_MG_MasterValidationWeekly] for Measures {[Mst Valid Result_Validation Factor]} using scope (&CWVUI.unionWith(&LastSyncVersion))
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
str_instance = 'PY_MG_MasterValidationWeekly'
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
    col_VersionVersionName = 'Version.[Version Name]'
    col_ItemItem = 'Item.[Item]'
    col_ToItemToItem = 'To Item.[To Item]'
    col_ItemItemStage = 'Item.[Item Stage]'
    col_ItemProductGroup = 'Item.[Product Group]'
    col_LocationLocation = 'Location.[Location]'
    col_ToLocationToLocation = 'To Location.[To Location]'
    col_SubLocationSubLocation = 'Sub Location.[Sub Location]'
    col_TransModeTransMode = 'Trans Mode.[Trans Mode]'
    col_MasterValidationValidationID = 'Master Validation.[Validation ID]'
    col_LineLine = 'Line.[Line]'
    col_SalesDomainAP2 = 'Sales Domain.[AP2]'
    col_BOMInfoBOMVersion = 'BOM Info.[BOM Version]'
    col_TimeWeek = 'Time.[Week]'
    col_TimeDay  = 'Time.[Day]'
    col_Inv_Qty = 'Inv_Qty'
    col_Intr_Qty = 'Intr_Qty'
    col_ValidationFactor = "Mst Valid Result_Validation Factor"
    col_Intr_FromSiteID = 'Intr_From Site ID'
    col_InvShuffle_Qty = 'Inv Shuffle_Qty'
    col_MfgPlan_FinishDate = 'Mfg Plan_Finish Date'
    col_MfgPlan_ToSiteID = 'Mfg Plan_To Site ID'
    col_MfgPlan_Qty = 'Mfg Plan_Qty'
    col_MfgPlan_BOMVersion = 'Mfg Plan_BOM Version' #사용안함.

    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')

    # Value 변수 선언
    # paramOutVersion_VALUE = "CWV_MP" # CWV_MP

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion  = paramOutVersion_VALUE

        df_in_ItemSite = read_csv_file("df_in_ItemSite")
        #df_in_MfgPlan_SOPFPCmp = read_csv_file("df_in_MfgPlan_SOPFPCmp")
        df_in_MasterValidation = read_csv_file("df_in_MasterValidation")
        df_in_Intransit = read_csv_file("df_in_Intransit")
        df_in_Inventory = read_csv_file("df_in_Inventory")
        df_in_VersionName = read_csv_file("df_in_VersionName")
        df_in_InventoryShuffle = read_csv_file("df_in_InventoryShuffle")
        df_in_MfgPlanSET = read_csv_file("df_in_MfgPlanSET")
        df_in_MfgPlanLCM = read_csv_file("df_in_MfgPlanLCM")
        df_in_FullBom_LCM = read_csv_file("df_in_FullBom_LCM")
        #df_in_Time = read_csv_file("df_in_Time")

    # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE

    # MP Plan End Date     MP Plan Start Date
    # input dataframe 확인용 로그

    print_df(df_in_ItemSite, 'df_in_ItemSite', False)
    #print_df(df_in_MfgPlan_SOPFPCmp, 'df_in_MfgPlan_SOPFPCmp', False)
    print_df(df_in_MasterValidation, 'df_in_MasterValidation', False)
    print_df(df_in_Intransit, 'df_in_Intransit', False)
    print_df(df_in_Inventory, 'df_in_Inventory', False)
    print_df(df_in_VersionName, 'df_in_VersionName', False)
    print_df(df_in_InventoryShuffle, 'df_in_InventoryShuffle', False)
    print_df(df_in_MfgPlanSET, 'df_in_MfgPlanSET', False)
    print_df(df_in_MfgPlanLCM, 'df_in_MfgPlanLCM', False)
    print_df(df_in_FullBom_LCM, 'df_in_FullBom_LCM', False)
    #print_df(df_in_Time, 'df_in_Time', False)

    #칼럼정리
    #df_in_Time = df_in_Time[[col_TimeWeek,col_TimeDay]]
    #df_in_Time[col_TimeDay] = pd.to_datetime(df_in_Time[col_TimeDay], format='%Y-%m-%d')
    #print_df(df_in_Time, 'df_in_Time 2', False)
    # -------------------------------------------------------------------------------------
    #df_in_MfgPlan_SOPFPCmp = df_in_MfgPlan_SOPFPCmp.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_Inventory = df_in_Inventory.astype({col_TimeWeek: 'str'}, copy=True)

    #print_df(df_in_MfgPlan_SOPFPCmp, 'df_in_MfgPlan_SOPFPCmp 2', False)
    print_df(df_in_Inventory, 'df_in_Inventory 2', False)
    
    # 'NA' 값을 nan 으로 읽어들임. nan --> 'NA' 로 입력
    df_in_MfgPlanSET[col_MfgPlan_BOMVersion] = np.where(df_in_MfgPlanSET[col_MfgPlan_BOMVersion].isna()
                                                        , "-x-", df_in_MfgPlanSET[col_MfgPlan_BOMVersion])
    df_in_MfgPlanSET[col_MfgPlan_BOMVersion] = np.where(df_in_MfgPlanSET[col_MfgPlan_BOMVersion] == "-x-"
                                                        , "NA", df_in_MfgPlanSET[col_MfgPlan_BOMVersion])
    
    print_df(df_in_MfgPlanSET, 'df_in_MfgPlanSET 2', False)
    
    step('=====> STEP 0-3 : Input table load End')

    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    step('=====> STEP 0-4 : 추가 df Create ')
    # Version Name 값 Setting
    VERSION_VALUE = df_in_VersionName.loc[0, col_VersionVersionName]

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

        #print_df(df_Vd_Return, 'df_'+a_ValidationID,False)
        return df_Vd_Return

    # SET, LCM 분리 ---------------------------------------------------
    df_in_SETItemSite = df_in_ItemSite[df_in_ItemSite[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMItemSite = df_in_ItemSite[df_in_ItemSite[col_ItemItemStage] == 'LCM'].copy()
    del df_in_ItemSite
    print_df(df_in_SETItemSite, 'df_in_SETItemSite', False)
    print_df(df_in_LCMItemSite, 'df_in_LCMItemSite', False)

    #df_in_SETMfgPlan_SFC = df_in_MfgPlan_SOPFPCmp[df_in_MfgPlan_SOPFPCmp[col_ItemItemStage] == 'SET'].copy()
    #df_in_LCMMfgPlan_SFC = df_in_MfgPlan_SOPFPCmp[df_in_MfgPlan_SOPFPCmp[col_ItemItemStage] == 'LCM'].copy()
    #del df_in_MfgPlan_SOPFPCmp
    #print_df(df_in_SETMfgPlan_SFC, 'df_in_SETMfgPlan_SFC', False)
    #print_df(df_in_LCMMfgPlan_SFC, 'df_in_LCMMfgPlan_SFC', False)

    df_in_SETInventory = df_in_Inventory[df_in_Inventory[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMInventory = df_in_Inventory[df_in_Inventory[col_ItemItemStage] == 'LCM'].copy()
    del df_in_Inventory
    print_df(df_in_SETInventory, 'df_in_SETInventory', False)
    print_df(df_in_LCMInventory, 'df_in_LCMInventory', False)

    df_in_SETIntransit = df_in_Intransit[df_in_Intransit[col_ItemItemStage] == 'SET'].copy()
    df_in_LCMIntransit = df_in_Intransit[df_in_Intransit[col_ItemItemStage] == 'LCM'].copy()
    del df_in_Intransit
    print_df(df_in_SETIntransit, 'df_in_SETIntransit', False)
    print_df(df_in_LCMIntransit, 'df_in_LCMIntransit', False)

    # Version 분리 : VERSION_VALUE 용, LastVersion 용 ---------------------
    # LastVersion : LastVersion 먼저처리----------------------------------------------------------
    df_in_SETLastInventory = df_in_SETInventory[df_in_SETInventory[col_VersionVersionName] != VERSION_VALUE]
    df_in_LCMLastInventory = df_in_LCMInventory[df_in_LCMInventory[col_VersionVersionName] != VERSION_VALUE]
    df_in_SETLastIntransit = df_in_SETIntransit[df_in_SETIntransit[col_VersionVersionName] != VERSION_VALUE]
    df_in_LCMLastIntransit = df_in_LCMIntransit[df_in_LCMIntransit[col_VersionVersionName] != VERSION_VALUE]

    print_df(df_in_SETLastInventory, 'df_in_SETLastInventory : Version', False)
    print_df(df_in_LCMLastInventory, 'df_in_LCMLastInventory : Version', False)
    print_df(df_in_SETLastIntransit, 'df_in_SETLastIntransit : Version', False)
    print_df(df_in_LCMLastIntransit, 'df_in_LCMLastIntransit : Version', False)
    # ----------------------------------------------------------------------------

    # VERSION_VALUE -----------------------------------------------------------
    df_in_SETIntransit = df_in_SETIntransit[df_in_SETIntransit[col_VersionVersionName] == VERSION_VALUE]
    df_in_LCMIntransit = df_in_LCMIntransit[df_in_LCMIntransit[col_VersionVersionName] == VERSION_VALUE]
    df_in_SETInventory = df_in_SETInventory[df_in_SETInventory[col_VersionVersionName] == VERSION_VALUE]
    df_in_LCMInventory = df_in_LCMInventory[df_in_LCMInventory[col_VersionVersionName] == VERSION_VALUE]

    print_df(df_in_SETIntransit, 'df_in_SETIntransit : Version', False)
    print_df(df_in_LCMIntransit, 'df_in_LCMIntransit : Version', False)
    print_df(df_in_SETInventory, 'df_in_SETInventory : Version', False)
    print_df(df_in_LCMInventory, 'df_in_LCMInventory : Version', False)

    # df_in_InventoryShuffle  Version 분리 : df_in_InventoryShuffle(당주), df_in_LastInventoryShuffle(전주)
    df_in_LastInventoryShuffle = df_in_InventoryShuffle[df_in_InventoryShuffle[col_VersionVersionName] != VERSION_VALUE]
    df_in_InventoryShuffle = df_in_InventoryShuffle[df_in_InventoryShuffle[col_VersionVersionName] == VERSION_VALUE]
    print_df(df_in_InventoryShuffle, 'df_in_InventoryShuffle : Version', False)
    print_df(df_in_LastInventoryShuffle, 'df_in_LastInventoryShuffle : Version', False)

    # df_SETInv_SUM --------------------------------------------
    df_SETInv_SUM = df_in_SETInventory[df_in_SETInventory[col_Inv_Qty].notna()]
    df_SETInv_SUM = df_SETInv_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Inv_Qty: "sum"})
    df_SETInv_SUM[col_Inv_Qty] = df_SETInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_SETInv_SUM, 'df_SETInv_SUM', False)

    # df_SETLastInv_SUM  --------------------------------------------
    df_SETLastInv_SUM = df_in_SETLastInventory[df_in_SETLastInventory[col_Inv_Qty].notna()]
    del df_in_SETLastInventory
    df_SETLastInv_SUM = df_SETLastInv_SUM.groupby([col_ItemItem, col_LocationLocation],
                                                  as_index=False).agg({col_Inv_Qty: "sum"})
    df_SETLastInv_SUM[col_Inv_Qty] = df_SETLastInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_SETLastInv_SUM, 'df_SETLastInv_SUM', False)

    # df_SETIntr_SUM --------------------------------------------
    df_SETIntr_SUM = df_in_SETIntransit[df_in_SETIntransit[col_Intr_Qty].notna()]
    df_SETIntr_SUM = df_SETIntr_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                            as_index=False).agg({col_Intr_Qty: "sum"})
    df_SETIntr_SUM[col_Intr_Qty] = df_SETIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_SETIntr_SUM, 'df_SETIntr_SUM', False)

    # df_SETLastIntr_SUM --------------------------------------------
    df_SETLastIntr_SUM = df_in_SETLastIntransit[df_in_SETLastIntransit[col_Intr_Qty].notna()]
    del df_in_SETLastIntransit
    df_SETLastIntr_SUM = df_SETLastIntr_SUM.groupby([col_ItemItem, col_LocationLocation],
                                                    as_index=False).agg({col_Intr_Qty: "sum"})
    df_SETLastIntr_SUM[col_Intr_Qty] = df_SETLastIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_SETLastIntr_SUM, 'df_SETLastIntr_SUM', False)

    # df_LCMInv_SUM --------------------------------------------
    df_LCMInv_SUM = df_in_LCMInventory[df_in_LCMInventory[col_Inv_Qty].notna()]
    df_LCMInv_SUM = df_LCMInv_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                          as_index=False).agg({col_Inv_Qty: "sum"})
    df_LCMInv_SUM[col_Inv_Qty] = df_LCMInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_LCMInv_SUM, 'df_LCMInv_SUM', False)

    # df_LCMLastInv_SUM --------------------------------------------
    df_LCMLastInv_SUM = df_in_LCMLastInventory[df_in_LCMLastInventory[col_Inv_Qty].notna()]
    del df_in_LCMLastInventory
    df_LCMLastInv_SUM = df_LCMLastInv_SUM.groupby([col_ItemItem, col_LocationLocation],
                                                  as_index=False).agg({col_Inv_Qty: "sum"})
    df_LCMLastInv_SUM[col_Inv_Qty] = df_LCMLastInv_SUM[col_Inv_Qty].astype('int64')
    print_df(df_LCMLastInv_SUM, 'df_LCMLastInv_SUM', False)

    # df_LCMIntr_SUM --------------------------------------------
    df_LCMIntr_SUM = df_in_LCMIntransit[df_in_LCMIntransit[col_Intr_Qty].notna()]
    df_LCMIntr_SUM = df_LCMIntr_SUM.groupby([col_VersionVersionName, col_ItemItem, col_LocationLocation],
                                            as_index=False).agg({col_Intr_Qty: "sum"})
    df_LCMIntr_SUM[col_Intr_Qty] = df_LCMIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_LCMIntr_SUM, 'df_LCMIntr_SUM', False)

    # df_LCMLastIntr_SUM --------------------------------------------
    df_LCMLastIntr_SUM = df_in_LCMLastIntransit[df_in_LCMLastIntransit[col_Intr_Qty].notna()]
    del df_in_LCMLastIntransit
    df_LCMLastIntr_SUM = df_LCMLastIntr_SUM.groupby([col_ItemItem, col_LocationLocation],
                                                    as_index=False).agg({col_Intr_Qty: "sum"})
    df_LCMLastIntr_SUM[col_Intr_Qty] = df_LCMLastIntr_SUM[col_Intr_Qty].astype('int64')
    print_df(df_LCMLastIntr_SUM, 'df_LCMLastIntr_SUM', False)

    # 여러번 사용하는 Set 구성 -----------------------------------------------

    # ------------------------------------------------------------------------
    step('=====> STEP 0-5 : 추가 df Create End')
    ################################################################################################################
    # STEP 1 : Validate data Create
    ################################################################################################################
    step('=====> STEP 1-1 : Validate data Create')

    # 칼럼설정
    clist_all = [col_VersionVersionName, col_MasterValidationValidationID, col_ItemItem, col_LocationLocation,
                 col_SubLocationSubLocation, col_TransModeTransMode, col_BOMInfoBOMVersion,
                 col_LineLine, col_SalesDomainAP2, col_ValidationFactor]
    clist_V_ITM_LOC = [col_VersionVersionName, col_ItemItem, col_LocationLocation]

    # 임시 --------------------------------------------------
    #df_in_MasterValidation = df_in_MasterValidation[df_in_MasterValidation[col_MasterValidationValidationID] == '(SET)MFG_SETLCM_UNBAL']
    # ------------------------------------------------------

    note(f'=====> for Strt ======================================================= ')
    df_Vld_Result_All = pd.DataFrame(columns=clist_all)  # 빈 dataframe

    for idx, row in df_in_MasterValidation.iterrows():
        # note(f'=====> Validation ID : {row[col_MasterValidationValidationID]}')
        df_Vld_Result_TMP = pd.DataFrame(columns=clist_all)  # 빈 dataframe
        CHK_I = 0
        # note(f'=====> Validation ID : {row[col_MasterValidationValidationID]} ----Start----')

        if row[col_MasterValidationValidationID] == '(SET)ITEMSITE_INTRANSIT':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                  , df_in_SETItemSite.copy()
                                                  , df_in_SETIntransit.copy())

        elif row[col_MasterValidationValidationID] == '(LCM)ITEMSITE_INTRANSIT':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                  , df_in_LCMItemSite.copy()
                                                  , df_in_LCMIntransit.copy())

        elif row[col_MasterValidationValidationID] == '(SET)ITEMSITE_MFGPLAN':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                  , df_in_SETItemSite.copy()
                                                  , df_in_MfgPlanSET.copy()) #df_in_SETMfgPlan_SFC는 df_in_MfgPlanSET로 교체, 2026.02.27
            
        elif row[col_MasterValidationValidationID] == '(LCM)ITEMSITE_MFGPLAN':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            df_Vld_Result_TMP = fn_valid_ITEMSITE(clist_V_ITM_LOC, row[col_MasterValidationValidationID]
                                                  , df_in_LCMItemSite.copy()
                                                  , df_in_MfgPlanLCM.copy()) #df_in_LCMMfgPlan_SFC는 df_in_MfgPlanLCM로 교체, 2026.02.27
            
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

        elif row[col_MasterValidationValidationID] == '(SET)EXCESSIVE_INTRANSIT_PRODUCT':  # ----------------------------
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
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
        
        elif row[col_MasterValidationValidationID] == '(SET)EXCESSIVE_INV_PRODUCT':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_SETInv_SUM & df_SETLastInv_SUM : sum(SETInventory.Inv_Qty), sum(SETLastInventory.Inv_Qty)
            df_Ext_Data = df_SETInv_SUM.merge(df_SETLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))

            # SETLastInventory.Inv_Qty > 0
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
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)MFG_SETLCM_UNBAL':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            #>> df_in_MfgPlanSET, df_in_MfgPlanLCM에 Mfg Plan_Finish Date를 df_in_Time을 활용하여 Time.[Week] 추가 
            #>>사용안함.            
            
            #>> Full BOM에 존재하는 LCM 생산 Route만 대상으로 추출            
            df_MfgPlanSET = df_in_MfgPlanSET.merge(df_in_FullBom_LCM, left_on=[col_LocationLocation, col_ItemItem],
                                                   right_on=[col_LocationLocation, col_ItemItem],
                                                   how='inner', suffixes=('', '_y'))
            
            df_MfgPlanLCM = df_in_MfgPlanLCM.merge(df_in_FullBom_LCM, left_on=[col_LocationLocation, col_ItemItem],
                                                   right_on=[col_ToLocationToLocation, col_ToItemToItem], 
                                                   how='inner', suffixes=('', '_y'))
            
            del [df_in_MfgPlanSET, df_in_MfgPlanLCM, df_in_FullBom_LCM]
            
            #print_df(df_MfgPlanSET, 'df_MfgPlanSET temp 1', False)
            #print_df(df_MfgPlanLCM, 'df_MfgPlanLCM temp 1', False)
            
            #>> SET생산량 vs LCM생산량을 비교
            # df_in_MfgPlanSET을 [Location, Item, Mfg Plan_BOM Version, To Item] 기준으로 [Mfg Plan_Qty] 계산
            df_MfgPlanSET = df_MfgPlanSET.groupby([col_VersionVersionName, col_LocationLocation, col_ItemItem,
                                                   col_MfgPlan_BOMVersion, col_ToItemToItem], 
                                                  as_index=False).agg({col_MfgPlan_Qty: "sum"})
            
            # df_in_MfgPlanLCM을 [Mfg Plan_To Site ID, Item_y, Item_x] 기준으로 [Mfg Plan_Qty] 계산
            df_MfgPlanLCM = df_MfgPlanLCM.groupby([col_VersionVersionName, col_MfgPlan_ToSiteID, 
                                                   col_ItemItem+'_y', col_ItemItem], 
                                                  as_index=False).agg({col_MfgPlan_Qty: "sum"})
            #df_MfgPlanLCM.rename(columns={col_MfgPlan_ToSiteID:col_LocationLocation}, inplace=True)
            
            #print_df(df_MfgPlanSET, 'df_MfgPlanSET temp 2', False)
            #print_df(df_MfgPlanLCM, 'df_MfgPlanLCM temp 2', False)
            
            # df_in_MfgPlanSET와 df_in_MfgPlanLCM을 merge하여 
            # df_MfgPlan_Temp[[Location, Item, BOM Version, To Item, SET Mfg Plan_Qty, LCM Mfg Plan_Qty]]를 생성
            # df_MfgPlan_Temp에서 [Location, To Item]기준으로 [SET Mfg Plan Qty]를 Sum한 값을 ToItemQty 필드로 추가
            
            cList_left  = [col_VersionVersionName, col_LocationLocation, col_ItemItem,      col_ToItemToItem]
            cList_right = [col_VersionVersionName, col_MfgPlan_ToSiteID, col_ItemItem+'_y', col_ItemItem]
            df_Ext_Data = df_MfgPlanSET.merge(df_MfgPlanLCM, left_on=cList_left,  right_on=cList_right,
                                              how = 'inner', suffixes = ('', '_LCM'))
            df_Ext_Data = df_Ext_Data.fillna(value={col_MfgPlan_Qty: 0, col_MfgPlan_Qty+'_LCM': 0})
            df_Ext_Data['ToItemQty'] = df_Ext_Data.groupby([col_LocationLocation, 
                                                            col_ToItemToItem])[col_MfgPlan_Qty].transform('sum')
            
            #df_MfgPlan_Temp 에서 ToItemQty와 LCM Mfg Plan_Qty가 상이한 정보만 추출 
            df_Ext_Data = df_Ext_Data[df_Ext_Data['ToItemQty'] != df_Ext_Data[col_MfgPlan_Qty+'_LCM']].copy()
            df_Ext_Data[col_BOMInfoBOMVersion] = df_Ext_Data[col_MfgPlan_BOMVersion]
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            #df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            #df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = (
                'SET : ' + df_Ext_Data['ToItemQty'].astype('str') +'대' +
                ' / LCM : ' + df_Ext_Data[col_MfgPlan_Qty+'_LCM'].astype('str') +'대')
            
            #print_df(df_Ext_Data, 'df_Ext_Data', True)
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            #print_df(df_Ext_Data, '(SET)MFG_SETLCM_UNBAL',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)NO_INTRANSIT_REGION':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_SETIntr_SUM & df_SETLastIntr_SUM : sum(SETIntransit.Intr_Qty), sum(SETLastIntransit.Intr_Qty)
            df_Ext_Data = df_SETIntr_SUM.merge(df_SETLastIntr_SUM, on=[col_ItemItem, col_LocationLocation]
                                               , how='inner', suffixes=('', '_last'))

            # SETIntransit.Intr_Qty = 0 & SETLastIntransit.Intr_Qty > 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Intr_Qty] == 0) & (df_Ext_Data[col_Intr_Qty + '_last'] > 0)]
            # df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Intr_Qty] == 1) & (df_Ext_Data[col_Intr_Qty + '_last'] > 0)] # 임시 test용

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
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[col_MasterValidationValidationID] == '(SET)NO_INV_REGION':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_SETInv_SUM & df_SETLastInv_SUM : sum(SETInventory.Inv_Qty), sum(SETLastInventory.Inv_Qty)
            df_Ext_Data = df_SETInv_SUM.merge(df_SETLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))
            # print_df(df_Ext_Data, 'df_Ext_Data',False)
            # SETInventory.Inv_Qty = 0 & SETLastInventory.Inv_Qty > 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)]
            # df_Ext_Data = df_Ext_Data[~(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)] # 임시 test용

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
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[col_MasterValidationValidationID] == '(SET)NO_INV_HUB':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # NO_INV_HUB : L401, L402 Site의 재고 확인, 전주에는 있으나 당주에는 없는 모델
            # df_in_LastInventoryShuffle에만 존재하는 자재
            # >> Version Name, Validation ID, Location, Item, Validation Factor 만 설정, 나머지는 ‘-’
            #             Validation Factor = “Inv Qty : [전주 수량] -> 0”   # [전주 수량]은 실제값으로 채움

            # df_in_LastInventoryShuffle(전주), df_in_InventoryShuffle(당주)
            df_Ext_Data = df_in_LastInventoryShuffle[
                ~df_in_LastInventoryShuffle.set_index([col_LocationLocation, col_ItemItem]).index.isin(
                    df_in_InventoryShuffle.set_index([col_LocationLocation, col_ItemItem]).index)].copy()

            # print_df(df_Ext_Data, 'df_Ext_Data',False)
            df_Ext_Data[col_VersionVersionName] = VERSION_VALUE  # Version Name 변경
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            df_Ext_Data[col_ValidationFactor] = 'Inv Qty : ' + df_Ext_Data[col_InvShuffle_Qty].astype('str') + ' -> 0'

            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]

            #print_df(df_Ext_Data, 'df_Ext_Data : (SET)NO_INV_HUB',False)
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data

        elif row[
            col_MasterValidationValidationID] == '(LCM)EXCESSIVE_INTRANSIT_PRODUCT':  # ----------------------------
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
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[
            col_MasterValidationValidationID] == '(LCM)EXCESSIVE_INV_PRODUCT':  # ----------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_LCMInv_SUM & df_LCMLastInv_SUM : sum(LCMInventory.Inv_Qty), sum(LCMLastInventory.Inv_Qty)
            df_Ext_Data = df_LCMInv_SUM.merge(df_LCMLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))

            # LCMLastInventory.Inv_Qty > 0
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
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

        elif row[col_MasterValidationValidationID] == '(LCM)NO_INV_PLANT':  # ------------------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            # merge : df_LCMInv_SUM & df_LCMLastInv_SUM : sum(LCMInventory.Inv_Qty), sum(LCMLastInventory.Inv_Qty)
            df_Ext_Data = df_LCMInv_SUM.merge(df_LCMLastInv_SUM, on=[col_ItemItem, col_LocationLocation]
                                              , how='inner', suffixes=('', '_last'))
            # LCMInventory.Inv_Qty = 0 & LCMLastInventory.Inv_Qty > 0
            df_Ext_Data = df_Ext_Data[(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)]
            # df_Ext_Data = df_Ext_Data[~(df_Ext_Data[col_Inv_Qty] == 0) & (df_Ext_Data[col_Inv_Qty + '_last'] > 0)] # 임시 test용

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
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)

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

    del [df_in_MasterValidation, df_in_SETIntransit, df_in_LCMIntransit, df_in_SETInventory, df_in_LCMInventory
        , df_SETInv_SUM, df_SETLastInv_SUM, df_SETIntr_SUM, df_SETLastIntr_SUM
        , df_LCMInv_SUM, df_LCMLastInv_SUM, df_LCMIntr_SUM, df_LCMLastIntr_SUM]
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

    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()