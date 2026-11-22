"""

* 프로그램명
    - PY_UI_POProposal

* 내용
    - Panel PO Proposal 데이터 생성

* 변경이력
    - 2025.01.14 / de0413.shin (신동언) / Create
    - 2026.02.12 / 양희영 / Update
    - 2026.04.14 / 양희영 / Update

* Flow Summary    

* Execution 

* Script Parameter
    - paramOutVersion : 사용 안함.

* Input Tables
    - df_in_AllocPur : Select ([Version].[Version Name] * [Sub Location].[Sub Location]  * [Location].[Location] * [Item Material].[S09] * [Item Material].[Class Category] * [Trans Mode].[Trans Mode] * [Item Material].[Item Material] * [Time].[Week]) on row, 
                       ({Measure.[Alloc Pur_ETD Plan]}) on column;
    - df_in_PoMgmt : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Class Category] * [Sub Location].[Sub Location] * [Vendor].[Vendor] * [Product].[Product Group] * [Trans Mode].[Trans Mode]) on row, 
                     ({Measure.[Purchasing Proposal Master_FCST Week], Measure.[Purchasing Proposal Master_Lot Size], Measure.[Purchasing Proposal Master_POP Week], Measure.[Purchasing Proposal Master_POPSTL], 
                     Measure.[Purchasing Proposal Master_STATUS]}) on column where {Measure.[Purchasing Proposal Master_STATUS] == "COM"};
    - df_in_Adhoc1POPFlag : Select ([Version].[Version Name] * [Location].[Location] * [Sequence].[Sequence] ) on row, 
                            ({Measure.[PO Proposal Flag_CY Flag], Measure.[PO Proposal Flag_DE Flag], Measure.[PO Proposal Flag_Description], Measure.[PO Proposal Flag_Plant], Measure.[PO Proposal Flag_PurORG], 
                            Measure.[PO Proposal Flag_Status]}) on column;
    - df_in_Adhoc2Purch_grp : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] ) on row, 
                              ({Measure.[Item Material Spec Plant_Procurement Type], Measure.[Item Material Spec Plant_Purchase Group], Measure.[Item Material Spec Plant_Storage Location]}) on column;
    - df_in_Adhoc3Purch_SLOC : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[PO Proposal SLoc_PurORG], Measure.[PO Proposal SLoc_StorageLocation]}) on column;
    - df_in_POProposal : CurrentWorkingView  ==> CWV_MP 로 변경 2026.04.03
                         Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Sequence].[Sequence] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                         ({Measure.[Panel PO Proposal_CY Flag], Measure.[Panel PO Proposal_Calc QTY], Measure.[Panel PO Proposal_Class Category], Measure.[Panel PO Proposal_Confirm POP QTY], Measure.[Panel PO Proposal_Currency], 
                         Measure.[Panel PO Proposal_DE Flag], Measure.[Panel PO Proposal_ERP Vendor], Measure.[Panel PO Proposal_ETA Week], Measure.[Panel PO Proposal_ETD QTY], Measure.[Panel PO Proposal_ETD Week], 
                         Measure.[Panel PO Proposal_GERP Send], Measure.[Panel PO Proposal_Incoterms1], Measure.[Panel PO Proposal_Incoterms2], Measure.[Panel PO Proposal_Open PO QTY], Measure.[Panel PO Proposal_Order No], 
                         Measure.[Panel PO Proposal_Order item], Measure.[Panel PO Proposal_Org POP ID], Measure.[Panel PO Proposal_POP ID], Measure.[Panel PO Proposal_POP Reason], Measure.[Panel PO Proposal_POP Reason Detail], 
                         Measure.[Panel PO Proposal_POP Status], Measure.[Panel PO Proposal_POP Status Asn], Measure.[Panel PO Proposal_Plant], Measure.[Panel PO Proposal_Price], Measure.[Panel PO Proposal_Pur Grp], 
                         Measure.[Panel PO Proposal_Pur Org], Measure.[Panel PO Proposal_Qty], Measure.[Panel PO Proposal_Receive Time], Measure.[Panel PO Proposal_Received By], Measure.[Panel PO Proposal_Reject Reason], 
                         Measure.[Panel PO Proposal_Send Date], Measure.[Panel PO Proposal_Send User], Measure.[Panel PO Proposal_Status], Measure.[Panel PO Proposal_Storage Loc], Measure.[Panel PO Proposal_Update Time], 
                         Measure.[Panel PO Proposal_Updated By]}) on column;
    - df_in_Incoterms : Select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Vendor].[Vendor] * [Product].[Product Group] ) on row, ({Measure.[Purchasing Proposal Vendor_INCO1]}) on column;
    - df_in_MtrlInforecord : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sequence].[Sequence] * [Vendor].[Vendor] * [Partner Vendor].[Partner Vendor] ) on row, 
                             ({Measure.[Mtrl Info Record_Currency], Measure.[Mtrl Info Record_GT Code], Measure.[Mtrl Info Record_Price], Measure.[Mtrl Info Record_Purchase Org]}) on column;
    - df_in_MtrlItemBOD : Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl W_Intransit LT]}) on column;
    - df_in_CurrentWeek : Select (&CurrentWeek * [Time].[Day]) where {[Time].[Day of Week].[MON]};
    - df_in_Version : CurrentWorkingView ==> CWV_MP 로 변경 2026.04.03
                      Select ([Version].[Version Name]);
* Output Tables
    - 
* 테스트 스크립트
    EXEC plugin instance [PY_UI_POProposal] for measures {[Panel PO Proposal_POP ID]} using scope (&MPV)
     using arguments {("IncludeNullRows", "False"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_POProposal'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
#paramOutVersion = "CWV_MP"
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
    cl_VersionName        = 'Version.[Version Name]'
    cl_Location           = 'Location.[Location]'
    cl_SubLocation        = 'Sub Location.[Sub Location]'
    cl_TransMode          = 'Trans Mode.[Trans Mode]'
    cl_Item               = 'Item.[Item]'
    cl_Item_ClassCategory = 'Item.[Class Category]'
    cl_ProductGroup       = 'Product.[Product Group]'
    cl_TimeWeek           = 'Time.[Week]'
    cl_TimeDay            = 'Time.[Day]'
    cl_Sequence           = 'Sequence.[Sequence]'
    cl_Vendor             = 'Vendor.[Vendor]'
    
    cl_ItemMaterial               = 'Item Material.[Item Material]'
    cl_ItemMaterial_S09           = 'Item Material.[S09]'
    cl_ItemMaterial_ClassCategory = 'Item Material.[Class Category]'
    
    cl_POPID               = 'Panel PO Proposal_POP ID'
    cl_ETDWeek             = 'Panel PO Proposal_ETD Week'
    cl_ETAWeek             = 'Panel PO Proposal_ETA Week'
    cl_POPStatus           = 'Panel PO Proposal_POP Status'
    cl_ERPVendor           = 'Panel PO Proposal_ERP Vendor'
    cl_Incoterms1          = 'Panel PO Proposal_Incoterms1'
    cl_Incoterms2          = 'Panel PO Proposal_Incoterms2'
    cl_Price               = 'Panel PO Proposal_Price'
    cl_Currency            = 'Panel PO Proposal_Currency'
    cl_ETDQTY              = 'Panel PO Proposal_ETD QTY'
    cl_OpenPOQTY           = 'Panel PO Proposal_Open PO QTY'
    cl_SendDate            = 'Panel PO Proposal_Send Date'
    cl_Status              = 'Panel PO Proposal_Status'
    cl_POPStatus           = 'Panel PO Proposal_POP Status'
    cl_ConfirmPOPQTY       = 'Panel PO Proposal_Confirm POP QTY'
    cl_POPReason           = 'Panel PO Proposal_POP Reason'
    cl_POPro_CYFLAG        = 'Panel PO Proposal_CY Flag'
    cl_POPro_DEFlag        = 'Panel PO Proposal_DE Flag'
    cl_POPro_Plant         = 'Panel PO Proposal_Plant'
    cl_POPro_PurOrg        = 'Panel PO Proposal_Pur Org'
    cl_POPro_PurGrp        = 'Panel PO Proposal_Pur Grp'
    cl_POPro_StorageLoc    = 'Panel PO Proposal_Storage Loc'
    cl_POPro_ClassCategory = 'Panel PO Proposal_Class Category'
    cl_POPro_GERPSend      = 'Panel PO Proposal_GERP Send'
    
    cl_ETDPlan = 'Alloc Pur_ETD Plan'
    cl_POPWeek = 'Purchasing Proposal Master_POP Week'
    cl_INCO1   = 'Purchasing Proposal Vendor_INCO1'
    
    cl_ADHOC_Col01 = 'ADHOC_Col01'
    cl_ADHOC_Col02 = 'ADHOC_Col02'
    cl_ADHOC_Col03 = 'ADHOC_Col03'
    cl_ADHOC_Col04 = 'ADHOC_Col04'
    cl_ADHOC_Col05 = 'ADHOC_Col05'
    

    cl_Flag_PurORG     = 'PO Proposal Flag_PurORG'
    cl_Flag_CYFlag      = 'PO Proposal Flag_CY Flag'
    cl_Flag_DEFlag      = 'PO Proposal Flag_DE Flag'
    cl_Flag_Description = 'PO Proposal Flag_Description'
    cl_Flag_Status      = 'PO Proposal Flag_Status'
    
    cl_Plant_ProcurementType = 'Item Material Spec Plant_Procurement Type'
    cl_Plant_PurchaseGroup   = 'Item Material Spec Plant_Purchase Group'
    cl_Plant_StorageLocation = 'Item Material Spec Plant_Storage Location'
    
    cl_SLoc_PurORG          = 'PO Proposal SLoc_PurORG'
    cl_SLoc_StorageLocation = 'PO Proposal SLoc_StorageLocation'
    
    cl_SITEID        = 'SITEID'
    cl_PUR_ORG       = 'PUR_ORG'
    cl_CY_FLAG       = 'CY_FLAG'
    cl_DE_FLAG       = 'DE_FLAG'
    cl_DESCRIPTION   = 'DESCRIPTION'
    cl_STATUS        = 'STATUS'
    cl_PROCUMENTTYPE = 'PROCUMENTTYPE'
    
    cl_PURCH_GRP       = 'PURCH_GRP'
    cl_STORAGELOCATION = 'STORAGELOCATION'
    
    cl_GTCode      = 'Mtrl Info Record_GT Code'
    cl_PurchaseOrg = 'Mtrl Info Record_Purchase Org'
    cl_MIR_Currency    = 'Mtrl Info Record_Currency'
    cl_MIR_Price       = 'Mtrl Info Record_Price'
    
    cl_BODW_IntransitLT = 'BOD Item Mtrl W_Intransit LT'
    
    # 칼럼 List 설정
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    
    # 데이터 파일 읽기
    if is_local:
        df_in_AllocPur = read_csv_file("df_in_AllocPur")        
        df_in_PoMgmt = read_csv_file("df_in_PoMgmt")
        df_in_Adhoc1POPFlag = read_csv_file("df_in_Adhoc1POPFlag")
        df_in_Adhoc2Purch_grp = read_csv_file("df_in_Adhoc2Purch_grp")
        df_in_Adhoc3Purch_SLOC = read_csv_file("df_in_Adhoc3Purch_SLOC")
        df_in_POProposal = read_csv_file("df_in_POProposal")
        df_in_Incoterms = read_csv_file("df_in_Incoterms")
        df_in_MtrlInforecord = read_csv_file("df_in_MtrlInforecord")
        df_in_MtrlItemBOD = read_csv_file("df_in_MtrlItemBOD")
        df_in_CurrentWeek = read_csv_file("df_in_CurrentWeek")
        df_in_Version = read_csv_file("df_in_Version")
        
    print_df(df_in_AllocPur, 'df_in_AllocPur', False)
    print_df(df_in_PoMgmt, 'df_in_PoMgmt', False)
    print_df(df_in_Adhoc1POPFlag, 'df_in_Adhoc1POPFlag', False)
    print_df(df_in_Adhoc2Purch_grp, 'df_in_Adhoc2Purch_grp', False)
    print_df(df_in_Adhoc3Purch_SLOC, 'df_in_Adhoc3Purch_SLOC', False)
    print_df(df_in_POProposal, 'df_in_POProposal', False)
    print_df(df_in_Incoterms, 'df_in_Incoterms', False)
    print_df(df_in_MtrlInforecord, 'df_in_MtrlInforecord', False)
    print_df(df_in_MtrlItemBOD, 'df_in_MtrlItemBOD', False)
    print_df(df_in_CurrentWeek, 'df_in_CurrentWeek', False)
    print_df(df_in_Version, 'df_in_Version', False)
    
    step('=====> STEP 0-3 : Input table load End')

    # DATA TYPE 설정
    df_in_AllocPur    = df_in_AllocPur.astype({cl_TimeWeek: 'str'}, copy=True)    
    df_in_CurrentWeek = df_in_CurrentWeek.astype({cl_TimeWeek: 'str'}, copy=True)
    df_in_CurrentWeek[cl_TimeDay] = pd.to_datetime(df_in_CurrentWeek[cl_TimeDay], format='%Y-%m-%d')        
    df_in_POProposal = df_in_POProposal.astype({cl_POPID: 'str'}, copy=True)
    
    if df_in_POProposal[cl_SendDate].dtype != 'datetime64[ns]':
        df_in_POProposal[cl_SendDate] = pd.to_datetime(df_in_POProposal[cl_SendDate], format='%m/%d/%Y %I:%M:%S %p')
    
    df_in_MtrlItemBOD = df_in_MtrlItemBOD.astype({cl_TimeWeek: 'str'}, copy=True)
    print_df(df_in_MtrlItemBOD, 'df_in_MtrlItemBOD 2', False)
    
    #칼럼 정리    
    df_in_CurrentWeek = df_in_CurrentWeek[[cl_TimeWeek, cl_TimeDay]]
    df_in_CurrentWeek.rename(columns={cl_TimeWeek:'CurrentWeek', cl_TimeDay: 'CurrentMonDay'}, inplace=True)
    #6개월 전 일자
    df_in_CurrentWeek['Last6M_Day'] = (df_in_CurrentWeek['CurrentMonDay'].apply(lambda x: x - relativedelta(months=6)))
    #전월 1일
    df_in_CurrentWeek['LastM_FrstDay'] = (df_in_CurrentWeek['CurrentMonDay'].apply(lambda x: x - relativedelta(months=1))).dt.strftime('%Y%m')+"01"
    df_in_CurrentWeek['LastM_FrstDay'] = pd.to_datetime(df_in_CurrentWeek['LastM_FrstDay'], format='%Y%m%d')
    #전주
    df_in_CurrentWeek['LastWeek'] = df_in_CurrentWeek.apply(lambda x: common.gfn_add_week(x['CurrentWeek'], -1), axis=1)
        
    print_df(df_in_CurrentWeek, 'df_in_CurrentWeek 2', False)
    
    df_in_Adhoc1POPFlag.rename(columns={cl_Flag_PurORG: cl_PUR_ORG, cl_Flag_CYFlag: cl_CY_FLAG, cl_Flag_DEFlag: cl_DE_FLAG,
                                        cl_Flag_Description: cl_DESCRIPTION, cl_Flag_Status: cl_STATUS}, inplace=True)
    
    # ADHOC_Col01 : PUR_ORG, ADHOC_Col02 : CY_FLAG, ADHOC_Col03 : DE_FLAG, ADHOC_Col04 : DESCRIPTION, ADHOC_Col05 : STATUS
    
    df_in_Adhoc2Purch_grp.rename(columns={cl_Plant_ProcurementType: cl_PROCUMENTTYPE, cl_Plant_PurchaseGroup: cl_PURCH_GRP, 
                                          cl_Plant_StorageLocation: cl_STORAGELOCATION}, inplace=True)
        
    #ADHOC_Col01 : PROCUMENTTYPE, ADHOC_Col02 : PURCH_GRP, ADHOC_Col03 : STORAGELOCATION
    
    df_in_Adhoc3Purch_SLOC.rename(columns={cl_SLoc_PurORG: cl_PUR_ORG, cl_SLoc_StorageLocation: cl_STORAGELOCATION}, inplace=True)
    
    #ADHOC_Col01 : PUR_ORG, ADHOC_Col02 : STORAGELOCATION
    print_df(df_in_Adhoc1POPFlag, 'df_in_Adhoc1POPFlag 2', False)
    print_df(df_in_Adhoc2Purch_grp, 'df_in_Adhoc2Purch_grp 2', False)
    print_df(df_in_Adhoc3Purch_SLOC, 'df_in_Adhoc3Purch_SLOC 2', False)
    
    step('=====> STEP 0-3 : DATA TYPE End')
    
    ################################################################################################################
    # STEP 1 : Alloc Pur SUM : Alloc Pur 기준으로 아래 Key 조건으로 Inner Join 하여, W+0 ~ W+{{POP Week -1}} 만큼 Sum 한다
    #                          Purchasing Proposal Master_STATUS = COM 인대상만 : 
    #                           ==> df_in_PoMgmt, IBPL 에서 처리 where {Measure.[Purchasing Proposal Master_STATUS] == "COM"
    ################################################################################################################
    step('=====> STEP 1-1 :  Alloc Pur SUM')
    
    df_in_PoMgmt = df_in_PoMgmt[df_in_PoMgmt[cl_POPWeek] > 0]
    cList_Left = [cl_VersionName, cl_SubLocation, cl_Location, cl_ItemMaterial_S09, cl_ItemMaterial_ClassCategory, cl_TransMode]
    cList_right = [cl_VersionName, cl_Location, cl_SubLocation, cl_ProductGroup, cl_Item_ClassCategory, cl_TransMode]
    
    df_AllocPur = df_in_AllocPur.merge(df_in_PoMgmt, left_on=cList_Left, right_on=cList_right, how='inner',
                                          suffixes=('', '_y'))
    del [df_in_AllocPur, df_in_PoMgmt]
    
    df_AllocPur = df_AllocPur.merge(df_in_CurrentWeek, how='cross') # CurrentWeek merge
    
    if df_AllocPur.empty :
        df_AllocPur['EndWeek'] = ''
    else :
        df_AllocPur['EndWeek'] = df_AllocPur.apply(lambda x: common.gfn_add_week(x['CurrentWeek'], (x[cl_POPWeek]-1)), axis=1)
    
    df_AllocPur = df_AllocPur.astype({cl_TimeWeek: 'int64', 'CurrentWeek': 'int64', 'EndWeek': 'int64', cl_ETDPlan: 'int64'}, copy=True)
    print_df(df_AllocPur, 'df_AllocPur 1', False)
    df_AllocPur = df_AllocPur[(df_AllocPur[cl_TimeWeek] >= df_AllocPur['CurrentWeek']) &
                              (df_AllocPur[cl_TimeWeek] <= df_AllocPur['EndWeek'])].copy()
    print_df(df_AllocPur, 'df_AllocPur 2', False)
    
    cList_group = [cl_SubLocation, cl_Location, cl_ItemMaterial_S09, cl_ItemMaterial_ClassCategory, cl_TransMode, 
                   cl_ItemMaterial, 'CurrentWeek', cl_POPWeek]
    
    df_AllocPur_sum = df_AllocPur.groupby(cList_group, as_index=False).agg({cl_ETDPlan: "sum"})
    #print_df(df_AllocPur_sum, 'df_AllocPur_sum 1-1', False)
    
    df_AllocPur_sum.rename(columns={'CurrentWeek': cl_TimeWeek, cl_ETDPlan: cl_ETDQTY}, inplace=True)
    del df_AllocPur
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 1', False)
    
    ################################################################################################################
    # STEP 2 : 위에서 생성한 Alloc Pur Sum 기준으로 ds_in_Adhoc1 POP Flag Key 조건으로 Inner Join 하여, MAX값을 가져온다
    ################################################################################################################
    step('=====> STEP 2-1 :  Adhoc1POPFlag Merge')
    
    df_Adhoc1POPFlag = df_in_Adhoc1POPFlag[[cl_Location,cl_PUR_ORG,cl_CY_FLAG,cl_DE_FLAG,cl_DESCRIPTION,
                                            cl_STATUS]].copy()
    del df_in_Adhoc1POPFlag
    
    df_Adhoc1POPFlag = df_Adhoc1POPFlag.groupby([cl_Location], as_index=False).agg({cl_PUR_ORG: "max",                                                                              
                                                                                    cl_CY_FLAG: "max",
                                                                                    cl_DE_FLAG: "max",
                                                                                    cl_DESCRIPTION: "max",
                                                                                    cl_STATUS: "max"})
    df_AllocPur_sum = df_AllocPur_sum.merge(df_Adhoc1POPFlag, on=[cl_Location], how='inner')
    del df_Adhoc1POPFlag
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 2', False)
    
    ################################################################################################################
    # STEP 3 : Alloc Pur Sum + Flag Add + Purch_GRP 에 Plant/Item Key 조건으로 Left Out Join 하여, Adhoc2의 Purch_GRP, STORAGELOCATION 값 생성
    ################################################################################################################
    step('=====> STEP 3-1 :  Adhoc2Purch_grp Merge')
    
    df_Adhoc2Purch_grp = df_in_Adhoc2Purch_grp[[cl_Location, cl_ItemMaterial, cl_PURCH_GRP, cl_STORAGELOCATION]].copy()
    del df_in_Adhoc2Purch_grp
    print_df(df_Adhoc2Purch_grp, 'df_Adhoc2Purch_grp', False)
    
    cList_on = [cl_Location, cl_ItemMaterial]
    cList_right = [cl_Location, cl_ItemMaterial]
    
    df_AllocPur_sum = df_AllocPur_sum.merge(df_Adhoc2Purch_grp, on=cList_on, how='left')
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 3', False)
    
    ################################################################################################################
    # STEP 4 : Alloc Pur Sum + Flag Add + Purch_GRP Plant/PUR_ORG Key 조건으로 Left Out Join 하여, STORAGELOCATION 이 Null 인경우 Adhoc3의 STORAGELOCATION 값을 가져온다
    ################################################################################################################
    step('=====> STEP 4-1 :  Adhoc3Purch_SLOC Merge')
    
    df_Adhoc3Purch_SLOC = df_in_Adhoc3Purch_SLOC[[cl_Location, cl_PUR_ORG, cl_STORAGELOCATION]].copy()
    del df_in_Adhoc3Purch_SLOC
    #print_df(df_Adhoc3Purch_SLOC, 'df_Adhoc3Purch_SLOC', False)
    
    df_AllocPur_sum = df_AllocPur_sum.merge(df_Adhoc3Purch_SLOC, on=[cl_Location, cl_PUR_ORG], how='left', 
                                            suffixes=('', '_y'))
    del df_Adhoc2Purch_grp
    df_AllocPur_sum[cl_STORAGELOCATION] = np.where(df_AllocPur_sum[cl_STORAGELOCATION].isna(),
                                                   df_AllocPur_sum[cl_STORAGELOCATION + '_y'],
                                                   df_AllocPur_sum[cl_STORAGELOCATION])
    df_AllocPur_sum.drop(columns=[cl_STORAGELOCATION + '_y'], inplace=True)
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 4', False)
    
    ################################################################################################################
    # STEP 5 : Alloc Pur Sum + Flag Add + Purch_GRP   와 POProposal 에서 Key 로 Left Outer Join 하여 ERP Vendor  값 생성
    #           과거 6개월 내 동일 Item * GT Code * To Site 를 갖고,  Status = "PO_CREATE" 인 항목들 중
    #           가장 큰 POPID를 갖는 데이터의 ERP Vendor를 복사 (* 참조할 값 없으면 null로 입력)
    ################################################################################################################
    step('=====> STEP 5-1 :  df_in_POProposal Merge 1')
    
    df_in_POProposal = df_in_POProposal.merge(df_in_CurrentWeek, how='cross') # CurrentWeek merge
    #print_df(df_POProposal, 'df_POProposal', False)
    #과거 6개월 내
    df_POProposal = df_in_POProposal[(df_in_POProposal[cl_SendDate] >= df_in_POProposal['Last6M_Day']) & # 과거 6개월 내
                                     (df_in_POProposal[cl_POPStatus] == "PO_CREATE")].copy()            # Status = "PO_CREATE"
    #print_df(df_POProposal, 'df_POProposal 1', False)
    
    df_POProposal_1 = df_POProposal.copy()
    # Item Material.[Item Material], Sub Location.[Sub Location], Location.[Location]    
    cList_Group = [cl_VersionName, cl_ItemMaterial, cl_SubLocation, cl_Location]
    df_POProposal_1['MAX_POPID'] = df_POProposal_1.groupby(cList_Group)[cl_POPID].transform('max')
    
    df_POProposal_1 = df_POProposal_1[df_POProposal_1[cl_POPID] == df_POProposal_1['MAX_POPID']].copy() # GROUP별 가장 큰 POPID
    df_POProposal_1 = df_POProposal_1[[cl_ItemMaterial, cl_SubLocation, cl_Location, cl_TransMode, cl_ERPVendor]]
    df_POProposal_1.drop_duplicates(inplace=True)
    print_df(df_POProposal_1, 'df_POProposal_1 2', False)
    
    df_AllocPur_sum = df_AllocPur_sum.merge(df_POProposal_1, on=[cl_ItemMaterial, cl_SubLocation, cl_Location, 
                                                                 cl_TransMode], how='left', suffixes=('', '_y'))
    del df_POProposal_1
    
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 5', False)
    
    ################################################################################################################
    # STEP 6 : Alloc Pur Sum + Flag Add + Purch_GRP + ERP Vendor   와 Incoterms 에서 Key 로 Left Outer Join 하여 Incoterms1  값 생성
    #          (* 참조할 값 없으면 null로 입력)
    ################################################################################################################
    step('=====> STEP 6-1 :  df_in_Incoterms Merge')
    
    df_in_Incoterms = df_in_Incoterms[[cl_Location, cl_SubLocation, cl_ProductGroup,  cl_Vendor, cl_INCO1]]
    
    if df_AllocPur_sum[cl_ERPVendor].dtype != 'object':
        df_AllocPur_sum = df_AllocPur_sum.astype({cl_ERPVendor: 'object'}, copy=True)
        
    if df_in_Incoterms[cl_Vendor].dtype != 'object':
        df_in_Incoterms = df_in_Incoterms.astype({cl_Vendor: 'object'}, copy=True)
        
    cList_Left  = [cl_SubLocation, cl_Location,    cl_ItemMaterial_S09, cl_ERPVendor]
    cList_right = [cl_Location,    cl_SubLocation, cl_ProductGroup,     cl_Vendor]
    
    df_AllocPur_sum = df_AllocPur_sum.merge(df_in_Incoterms, left_on=cList_Left, right_on=cList_right, how='left', 
                                            suffixes=('', '_y'))
    del df_in_Incoterms
    df_AllocPur_sum.drop(columns=[cl_Location + '_y', cl_SubLocation + '_y', cl_ProductGroup, cl_Vendor], inplace=True)
    
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 6', False)
    
    ################################################################################################################
    # STEP 7 : Alloc Pur Sum + Flag Add + Purch_GRP   와 POProposal 에서 아래 Key 로 Left Outer Join 하여 Incoterms2  값 생성
    #          과거 6개월 내 동일 Item * GT Code * To Site * ERP Vendor * Inco.1 를 갖고 Status = "PO_CREATE" 인 항목들 중 가장 큰 POPID 를 갖는 데이터의 Inco.2 를 복사
    #          (* 참조할 값 없으면 null로 입력)
    ################################################################################################################
    step('=====> STEP 7-1 :  df_in_POProposal Merge 2')
    
    # df_POProposal : 과거 6개월 내, Status = "PO_CREATE"    
    # Item Material.[Item Material], Sub Location.[Sub Location], Location.[Location], [Panel PO Proposal_ERP Vendor],  [Panel PO Proposal_Incoterms1]
    cList_Group = [cl_VersionName, cl_ItemMaterial, cl_SubLocation, cl_Location, cl_ERPVendor, cl_Incoterms1]
    df_POProposal['MAX_POPID'] = df_POProposal.groupby(cList_Group)[cl_POPID].transform('max')
    
    df_POProposal = df_POProposal[df_POProposal[cl_POPID] == df_POProposal['MAX_POPID']].copy()  # GROUP별 가장 큰 POPID
    df_POProposal = df_POProposal[[cl_ItemMaterial, cl_SubLocation, cl_Location, cl_ERPVendor, cl_Incoterms1, 
                                   cl_Incoterms2]]
    df_POProposal.drop_duplicates(inplace=True)
    #print_df(df_POProposal, 'df_POProposal', False)
    
    # Panel PO Proposal_Incoterms2 구하기
    df_AllocPur_sum.rename(columns={cl_INCO1: cl_Incoterms1}, inplace=True)    
    cList_On = [cl_SubLocation, cl_Location, cl_ItemMaterial, cl_ERPVendor, cl_Incoterms1]
    df_AllocPur_sum = df_AllocPur_sum.merge(df_POProposal, on=cList_On, how='left', suffixes=('', '_y'))
    del df_POProposal
    
    #Panel PO Proposal_POP ID 구하기 : 전체 df_in_POProposal 에서 주차정보 제외한 뒤 8자리 max 값 구한다.
    df_PopID = df_in_POProposal[[cl_VersionName, cl_POPID]].copy()
    df_PopID = df_PopID[df_PopID[cl_POPID].notna() & (df_PopID[cl_POPID] != 'nan')] #2026.02.11 추가
    #print_df(df_PopID, 'df_PopID 1', False)
    
    if df_PopID.empty:
        # df_in_POProposal DATA가 없는 경우
        df_PopID = pd.DataFrame(columns=['TEMP_ID'])
        df_PopID.loc[0] = [0]
    else :
        df_PopID['TEMP_ID'] = df_PopID[cl_POPID].str[4:4+8].astype('int64')
        df_PopID= df_PopID.groupby([cl_VersionName], as_index=False)['TEMP_ID'].max()
        df_PopID['TEMP_ID'] = (df_PopID['TEMP_ID'])
        df_PopID = df_PopID[['TEMP_ID']]
        
    print_df(df_PopID, 'df_PopID', False)
        
    # MAX 값 : Panel PO Proposal_POP ID 의 MAX로 계산 (뒤에 8자리 + 1로 신규채번), (Null일경우 YYWW + 00000001 로 설정)
    df_AllocPur_sum['CurrentWeek'] = df_AllocPur_sum[cl_TimeWeek].astype('str')
    df_AllocPur_sum = df_AllocPur_sum.merge(df_PopID, how='cross')
    
    df_AllocPur_sum['DUMMY'] = 'DUMMY'
    clist_sort = [cl_SubLocation, cl_Location, cl_ItemMaterial_S09, cl_ItemMaterial_ClassCategory, cl_TransMode, 
                  cl_ItemMaterial, cl_TimeWeek]
    df_AllocPur_sum.sort_values(by=clist_sort, ascending=[True, True, True, True, True, True, True], 
                                axis=0, inplace=True)
    df_AllocPur_sum['R_NUM'] = 1
    df_AllocPur_sum['R_NUM'] = df_AllocPur_sum.groupby(['DUMMY'])['R_NUM'].cumsum()
    
    df_AllocPur_sum['TEMP_ID'] = df_AllocPur_sum['TEMP_ID'] + df_AllocPur_sum['R_NUM']    
    df_AllocPur_sum['TEMP_ID'] = df_AllocPur_sum['TEMP_ID'].astype('str').str.pad(width=8, side='left', fillchar='0')    
    df_AllocPur_sum[cl_POPID] = df_AllocPur_sum['CurrentWeek'].str[2:2+4] + df_AllocPur_sum['TEMP_ID']
    df_AllocPur_sum.drop(columns=['CurrentWeek', 'TEMP_ID', 'DUMMY', 'R_NUM'], inplace=True)
    
    #Panel PO Proposal_Status : OPEN 인 대상 (전월 1일~) : 당일 제한은 필요없음.
    df_in_POProposal['OPEN_QTY'] = np.where((df_in_POProposal[cl_Status] == "OPEN") &
                                            ((df_in_POProposal[cl_SendDate] >= df_in_POProposal['LastM_FrstDay'])), #전월 1일~
                                            df_in_POProposal[cl_ConfirmPOPQTY], 0)
    
    #Panel PO Proposal_POP Status 가 SEND 인 대상 : (전 주 ~ 당주 내 SEND) : 당주 제한은 필요없음. SEND ==> REQ / SND 로 변경(2026.04.14)
    df_in_POProposal = df_in_POProposal.astype({cl_TimeWeek: 'int64', 'LastWeek': 'int64'}, copy=True)
    df_in_POProposal['SEND_QTY'] = np.where((df_in_POProposal[cl_POPStatus].isin(["REQ","SND"])) &   #(df_in_POProposal[cl_POPStatus] == "SEND") &
                                            ((df_in_POProposal[cl_TimeWeek] >= df_in_POProposal['LastWeek'])),  # 전 주~
                                            df_in_POProposal[cl_ConfirmPOPQTY], 0)
    
    df_in_POProposal['OPEN_SEND_QTY'] = df_in_POProposal['OPEN_QTY'] + df_in_POProposal['SEND_QTY']
    #print_df(df_in_POProposal, 'df_in_POProposal 7', True)
    
    cList_group = [cl_SubLocation, cl_Location, cl_TransMode, cl_ItemMaterial]
    df_POProposal_GRP = df_in_POProposal.groupby(cList_group, as_index=False).agg({'OPEN_SEND_QTY': "sum"})
    
    df_POProposal_GRP.rename(columns={'OPEN_SEND_QTY': cl_ConfirmPOPQTY}, inplace=True)
    print_df(df_POProposal_GRP, 'df_POProposal_GRP', False)
    
    # merge : Panel PO Proposal_Confirm POP QTY :  
    # merge조건 : Sub Location.[Sub Location],Location.[Location],Trans Mode.[Trans Mode],Item Material.[Item Material]
    cList_on = [cl_SubLocation, cl_Location, cl_TransMode, cl_ItemMaterial]
    df_AllocPur_sum = df_AllocPur_sum.merge(df_POProposal_GRP, on=cList_on, how='left')
    del [df_PopID, df_in_POProposal, df_POProposal_GRP]
    
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 7', False)
    
    ################################################################################################################
    # STEP 8 : Alloc Pur Sum + Flag Add + Purch_GRP + ERP Vendor + Incoterms와 아래 Key 조건으로 
    #          ds_in_inforecord Left Out Join 하여,  Currency / Price 값을 가져온다. (* 참조할 값 없으면 null로 입력)
    ################################################################################################################
    step('=====> STEP 8-1 :  df_in_MtrlInforecord Merge ')
    
    # groupby 속도 문제로, data 필터 후 max 처리
    df_in_MtrlInforecord = df_in_MtrlInforecord[
        df_in_MtrlInforecord.set_index([cl_GTCode, cl_Location, cl_Item, cl_PurchaseOrg, cl_Vendor]).index.isin(
        df_AllocPur_sum.set_index([cl_SubLocation, cl_Location, cl_ItemMaterial, cl_PUR_ORG, cl_ERPVendor]).index)].copy()
    
    cList_Group = [cl_Location, cl_Item, cl_GTCode, cl_PurchaseOrg, cl_Vendor]
    df_in_MtrlInforecord = df_in_MtrlInforecord.groupby(cList_Group, as_index=False).agg({cl_MIR_Currency: "max",
                                                                                          cl_MIR_Price:    "max"})    
    
    #print_df(df_in_MtrlInforecord, 'df_in_MtrlInforecord', False)
        
    cList_Left  = [cl_SubLocation, cl_Location, cl_ItemMaterial, cl_PUR_ORG,     cl_ERPVendor]
    cList_right = [cl_GTCode,      cl_Location, cl_Item,         cl_PurchaseOrg, cl_Vendor]
        
    df_AllocPur_sum = df_AllocPur_sum.merge(df_in_MtrlInforecord, left_on=cList_Left, right_on=cList_right, how='left',
                                            suffixes=('', '_y'))
    del df_in_MtrlInforecord
    df_AllocPur_sum.rename(columns={cl_MIR_Currency: cl_Currency, cl_MIR_Price: cl_Price}, inplace=True)
    df_AllocPur_sum.drop(columns=[cl_GTCode, cl_Item, cl_PurchaseOrg, cl_Vendor], inplace=True)
    
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 8', False)
    
    ################################################################################################################
    # STEP 9 : Alloc Pur Sum + Flag Add + Purch_GRP + ERP Vendor + Incoterms + Currency 와 bod 를 아래 Key 조건으로 
    #          Left Out Join 하여,  Intransit LT 값을 가져온다
    ################################################################################################################
    step('=====> STEP 9-1 :  df_in_MtrlItemBOD Merge ')
    
    df_AllocPur_sum = df_AllocPur_sum.astype({cl_TimeWeek: 'str'}, copy=True)
    
    cList_Left  = [cl_SubLocation, cl_Location,    cl_TransMode, cl_ItemMaterial, cl_TimeWeek]
    cList_right = [cl_Location,    cl_SubLocation, cl_TransMode, cl_ItemMaterial, cl_TimeWeek]
    
    df_AllocPur_sum = df_AllocPur_sum.merge(df_in_MtrlItemBOD, left_on=cList_Left, right_on=cList_right, how='left',
                                            suffixes=('', '_y'))
    df_AllocPur_sum.drop(columns=[cl_VersionName, cl_Location+'_y', cl_SubLocation+'_y'], inplace=True)
    del df_in_MtrlItemBOD
    
    df_AllocPur_sum[cl_POPWeek] = df_AllocPur_sum[cl_POPWeek].fillna(0).astype('int64')
    df_AllocPur_sum[cl_BODW_IntransitLT] = df_AllocPur_sum[cl_BODW_IntransitLT].fillna(0).astype('int64')
    df_AllocPur_sum[cl_BODW_IntransitLT] = (df_AllocPur_sum[cl_BODW_IntransitLT] / 7).astype('int64') #2O26.02.23 추가
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 9 -1', False)
    
    #Panel PO Proposal_ETD Week : 당주 + Purchasing Proposal Master_POP Week - 1
    #Panel PO Proposal_ETA Week : (당주 + Purchasing Proposal Master_POP Week - 1) + BOD Item Mtrl W_Intransit LT
    if df_AllocPur_sum.empty :
        df_AllocPur_sum[cl_ETDWeek] = ''
        df_AllocPur_sum[cl_ETAWeek] = ''
    else :
        df_AllocPur_sum[cl_ETDWeek] = df_AllocPur_sum.apply(lambda x: common.gfn_add_week(x[cl_TimeWeek], 
                                                                                          (x[cl_POPWeek]-1)),
                                                            axis=1)
        df_AllocPur_sum[cl_ETAWeek] = df_AllocPur_sum.apply(lambda x: common.gfn_add_week(x[cl_TimeWeek], 
                                                                                          ((x[cl_POPWeek]-1) + 
                                                                                           x[cl_BODW_IntransitLT])),
                                                            axis=1)
    
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 9', False)
    
    ################################################################################################################
    # STEP 10 : output table create
    ################################################################################################################
    step('=====> STEP 10-1 : Final output table create')

    cList_POPro = [cl_VersionName, cl_SubLocation, cl_Location, cl_TransMode, cl_ItemMaterial, cl_TimeWeek, cl_Sequence,
                   cl_POPID, cl_ETDWeek, cl_ETAWeek, cl_POPStatus, cl_ERPVendor, cl_Incoterms1, cl_Incoterms2, 
                   cl_Price, cl_Currency, 
                   cl_ETDQTY, cl_OpenPOQTY, cl_POPReason, cl_POPro_CYFLAG, cl_POPro_DEFlag, cl_POPro_Plant,
                   cl_POPro_PurOrg, cl_POPro_PurGrp, cl_POPro_StorageLoc, cl_POPro_ClassCategory]
    
    df_AllocPur_sum = df_AllocPur_sum.merge(df_in_Version, how='cross') # CurrentWeek merge
    
    df_AllocPur_sum[cl_Sequence] = 1
    #clist_sort = [cl_VersionName, cl_SubLocation, cl_Location, cl_TransMode, cl_ItemMaterial, cl_TimeWeek, cl_POPID]
    #df_AllocPur_sum.sort_values(by=clist_sort, ascending=[True,True,True,True,True,True,True], axis=0, inplace=True)
    clist_sort = [cl_VersionName, cl_TimeWeek, cl_POPID]  #2O26.02.23 수정
    df_AllocPur_sum.sort_values(by=clist_sort, ascending=[True,True,True], axis=0, inplace=True)
    
    #clist_group = [cl_VersionName, cl_SubLocation, cl_Location, cl_TransMode, cl_ItemMaterial, cl_TimeWeek]
    clist_group = [cl_VersionName, cl_TimeWeek]
    df_AllocPur_sum[cl_Sequence] = df_AllocPur_sum.groupby(clist_group)[cl_Sequence].cumsum()
    
    df_AllocPur_sum[cl_ETDQTY] = df_AllocPur_sum[cl_ETDQTY].fillna(0).astype('int64')
    df_AllocPur_sum[cl_ConfirmPOPQTY] = df_AllocPur_sum[cl_ConfirmPOPQTY].fillna(0).astype('int64')
    df_AllocPur_sum[cl_POPStatus] = np.where((df_AllocPur_sum[cl_ETDQTY] -df_AllocPur_sum[cl_ConfirmPOPQTY]) <0,
                                             'ERR', 'INI')
    df_AllocPur_sum[cl_POPReason] = 'Normal (SOP)' #2O26.02.23 수정
    df_AllocPur_sum[cl_POPro_Plant] = df_AllocPur_sum[cl_Location]
    
    df_AllocPur_sum.rename(columns={cl_ConfirmPOPQTY: cl_OpenPOQTY, cl_CY_FLAG: cl_POPro_CYFLAG,
                                    cl_DE_FLAG: cl_POPro_DEFlag, cl_PUR_ORG:cl_POPro_PurOrg, 
                                    cl_PURCH_GRP:cl_POPro_PurGrp, cl_STORAGELOCATION: cl_POPro_StorageLoc,
                                    cl_ItemMaterial_ClassCategory: cl_POPro_ClassCategory}, inplace=True)
    
    df_AllocPur_sum = df_AllocPur_sum[cList_POPro]
    print_df(df_AllocPur_sum, 'df_AllocPur_sum 10', False)
    
    # out Data 생성 :
    df_out_PanelPOProposal = df_AllocPur_sum.copy()
    del df_AllocPur_sum
    
    # 버전 처리
    
    row_count, col_count = df_out_PanelPOProposal.shape
    note(f'=====> Final df_out_PanelPOProposal rows : {row_count}, column : {col_count}')
    print_df(df_out_PanelPOProposal, 'df_out_PanelPOProposal', False)
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_PanelPOProposal, 'df_out_PanelPOProposal')
    
    step('=====> STEP 5-2 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')
    
except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_PanelPOProposal = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    save_csv_file(df_out_log, 'df_out_log')
    save_csv_file(df_out_logDetail, 'df_out_logDetail')
    logger.Finish()