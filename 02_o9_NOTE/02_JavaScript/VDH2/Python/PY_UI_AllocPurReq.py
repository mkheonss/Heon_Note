"""
* 프로그램명 
    - PY_UI_AllocPurReq

* 내용
    - Alloc Pur UI Measure 데이터 생성

* 변경이력
    - 2024.12.18 / 양희영 / Create
    - 2025.10.16 / 양희영 / Update
    
* Flow Summary
    Alloc Pur 화면에 사용되는 Open Cell의 할당 정보 생성

* Execution 

* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.

* Input Tables
    - df_in_OC_LCM : OC투입~ LCM생산
          Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID] * FROM.[Activity2].[Activity2] * FROM.[Activity1].[Activity1] * 
          FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * 
          TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID].filter(#.Name != "InventoryDemand") * TO.[To Item].[To Item Stage].filter(#.Name in {"LCM"}).relatedmembers([To Item]) * 
          TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * 
          TO.[To Location].[To Site Stage].filter(#.Name in {"MF_LCM","MF_LCM_EX"}).relatedmembers([To Location]) * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * 
          TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
          ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_OC_SET  : OC투입~ SET생산
          Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID] * FROM.[Activity2].[Activity2] * FROM.[Activity1].[Activity1] * 
          FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * 
          TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Activity3].[Activity3] * 
          TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity Type1].[Manufacturing].relatedmembers([Activity1]) * 
          TO.[To Location].[To Site Stage].filter(#.Name in {"MF_LCM","MF_LCM_EX","MF","MF_SET","MF_KD"}).relatedmembers([To Location]) * TO.[Time].[Week] * TO.[Location].[Location] * 
          TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
          ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_BOMMaster
          Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, 
          ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_BOM Location], Measure.[BOM Master_BOM Status], Measure.[BOM Master_BOM Type], Measure.[BOM Master_BOM Version], 
          Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column;
    - df_in_ToSite
          Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID] * FROM.[Activity2].[Activity2] * FROM.[Activity1].[Activity1] * 
          FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * 
          TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * TO.[To Item].[To Item Stage].[SET].relatedmembers([To Item]) * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * 
          TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * TO.[To Location].[To Location] * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * 
          TO.[Activity2].[Activity2]) on row,
           ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
          //추가조건 : Substr(FROM.[Location].[Location], 1, 4) != TO.[Location].[Location] 
    - df_in_NOH_LCM : NOH (LCM)
          Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID].filter(#.Name == "000SCS_LOT" || #.Name startswith "ER_") * FROM.[Activity2].[Activity2] * 
          FROM.[Activity1].[Activity1].[ExpectedReceiptActivity] * FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity3].[Activity3] * 
          FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID].filter(#.Name != "InventoryDemand") * 
          TO.[To Item].[To Item Stage].filter(#.Name in {"LCM"}).relatedmembers([To Item]) * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * 
          TO.[Activity1].[Activity1] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_LCM","MF_LCM_EX"}).relatedmembers([To Location]) * TO.[Time].[Week] * TO.[Location].[Location] * 
          TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
          ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_NOH_SET : NOH (SET)
          Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID].filter(#.Name == "000SCS_LOT" || #.Name startswith "ER_") * FROM.[Activity2].[Activity2] * 
          FROM.[Activity1].[Activity1].[ExpectedReceiptActivity] * FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity3].[Activity3] * 
          FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item])* TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID].filter(#.Name != "InventoryDemand") * 
          TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * 
          TO.[Activity1].[Activity1] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_LCM","MF_LCM_EX","MF","MF_SET","MF_KD"}).relatedmembers([To Location]) * TO.[Time].[Week] * 
          TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
          ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_Short_SETDC : Short (SET (DC))
          Select (Version.[Version Name] * FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * FROM.[RootCause].[Problem Type] * 
          FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Time].[Week] *  FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * 
          TO.[Demand Type].[Demand Type] * TO.[Sales Domain].[Customer Group] * TO.[Time].[Week] * TO.[Demand].[DemandID] * TO.[Location].[Location] * TO.[Item].[Item]) on row, 
          ({Edge.[002.005W Solver Outputs Material Root Cause].[W Material Root Cause Quantity]}) on column where {RelationshipType.[002.005W Solver Outputs Material Root Cause]};
* Output Tables
    - df_out_AllocPurReq
          Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Sequence].[Sequence] * [Item Material].[Item Material] * [Category].[Category] ) on row, 
           ({Measure.[Alloc Pur Req_LCM Item], Measure.[Alloc Pur Req_LCM Qty], Measure.[Alloc Pur Req_Qty], Measure.[Alloc Pur Req_SET DC Qty], Measure.[Alloc Pur Req_SET DC Site], 
           Measure.[Alloc Pur Req_SET DC Week], Measure.[Alloc Pur Req_SET MFG Item], Measure.[Alloc Pur Req_SET MFG Qty], Measure.[Alloc Pur Req_SET MFG Site], 
           Measure.[Alloc Pur Req_SET MFG Week], Measure.[Alloc Pur Req_ToSite], Measure.[Alloc Pur Req_Total]}) on column;


* 테스트 스크립트
    EXEC plugin instance [PY_UI_AllocPurReq] for Measures {[Alloc Pur Req_Qty]} using scope (&MPV)
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
str_instance = 'PY_UI_AllocPurReq'
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
    col_VersionVersionName         = 'Version.[Version Name]'
    col_ItemItem                   = 'Item.[Item]'
    col_LocationLocation           = 'Location.[Location]'
    col_SubLocationSubLocation     = 'Sub Location.[Sub Location]'
    col_BOMInfoBOMID               = 'BOM Info.[BOM ID]'
    col_TimeWeek                   = 'Time.[Week]'
    col_ItemMaterialItemMaterial   = 'Item Material.[Item Material]'
    col_CategoryCategory           = 'Category.[Category]'
    col_SequenceSequence           = 'Sequence.[Sequence]'
    col_TransModeTransMode         = 'Trans Mode.[Trans Mode]'
    col_MarketingNameMarketingName = 'Marketing Name.[Marketing Name]'
    
    col_fromTimeWeek              = 'from.[Time].[Week]'
    col_fromLocationLocation      = 'from.[Location].[Location]'
    col_fromActivity1FromLocation = 'from.[Activity1].[From Location]'
    col_fromActivity2Activity2    = 'from.[Activity2].[Activity2]'
    col_fromItemItem              = 'from.[Item].[Item]'
    
    col_toActivity1Activity1   = 'to.[Activity1].[Activity1]'
    col_toLocationLocation     = 'to.[Location].[Location]'
    col_toToLocationToLocation = 'to.[To Location].[To Location]'
    col_toToItemToItem         = 'to.[To Item].[To Item]'
    col_toTimeWeek             = 'to.[Time].[Week]'
    col_toToTimeToWeek         = 'to.[To Time].[To Week]'
    col_toDemandDemandID       = 'to.[Demand].[DemandID]'    
    
    col_BOMMaster_BOMID        = 'BOM Master_BOM ID'
    col_BOMMaster_Status       = 'BOM Master_Status'
    col_AllocPurReq_Qty        = 'Alloc Pur Req_Qty'
    col_AllocPurReq_ToSite     = 'Alloc Pur Req_ToSite'
    col_AllocPurReq_LCMItem    = 'Alloc Pur Req_LCM Item'
    col_AllocPurReq_LCMQty     = 'Alloc Pur Req_LCM Qty'
    col_AllocPurReq_SETMFGItem = 'Alloc Pur Req_SET MFG Item'
    col_AllocPurReq_SETMFGSite = 'Alloc Pur Req_SET MFG Site'
    col_AllocPurReq_SETMFGWeek = 'Alloc Pur Req_SET MFG Week'
    col_AllocPurReq_SETMFGQty  = 'Alloc Pur Req_SET MFG Qty'
    col_AllocPurReq_SETDCSite  = 'Alloc Pur Req_SET DC Site'
    col_AllocPurReq_SETDCWeek  = 'Alloc Pur Req_SET DC Week'
    col_AllocPurReq_SETDCQty   = 'Alloc Pur Req_SET DC Qty'
    
    col_SOPBUPProducertoProducerFromPegged = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Producer From Pegged]'
    col_WMaterialRootCauseQuantity = '002.005W Solver Outputs Material Root Cause.[W Material Root Cause Quantity]'
        
    # 칼럼 List 설정
        
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_OC_LCM      = read_csv_file("df_in_OC_LCM")
        df_in_OC_SET      = read_csv_file("df_in_OC_SET")
        df_in_BOMMaster   = read_csv_file("df_in_BOMMaster")
        df_in_ToSite      = read_csv_file("df_in_ToSite")
        df_in_NOH_LCM     = read_csv_file("df_in_NOH_LCM")
        df_in_NOH_SET     = read_csv_file("df_in_NOH_SET")
        df_in_Short_SETDC = read_csv_file("df_in_Short_SETDC")
        
    
    # if df_in_InfoRecord.empty:
    #    raise Exception("=====> raise Exception: df_in_InfoRecord is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정    
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    print_df(df_in_OC_LCM, 'df_in_OC_LCM', False)
    print_df(df_in_OC_SET, 'df_in_OC_SET', False)
    print_df(df_in_BOMMaster, 'df_in_BOMMaster', False)
    print_df(df_in_ToSite, 'df_in_ToSite', False)
    print_df(df_in_NOH_LCM, 'df_in_NOH_LCM', False)
    print_df(df_in_NOH_SET, 'df_in_NOH_SET', False)
    print_df(df_in_Short_SETDC, 'df_in_Short_SETDC', False)
    
    df_in_OC_LCM = df_in_OC_LCM.astype({col_fromTimeWeek: 'str', col_toToTimeToWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    df_in_OC_SET = df_in_OC_SET.astype({col_fromTimeWeek: 'str', col_toToTimeToWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    df_in_ToSite = df_in_ToSite.astype({col_fromTimeWeek: 'str', col_toToTimeToWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    df_in_NOH_LCM = df_in_NOH_LCM.astype({col_fromTimeWeek: 'str', col_toToTimeToWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    df_in_NOH_SET = df_in_NOH_SET.astype({col_fromTimeWeek: 'str', col_toToTimeToWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    df_in_Short_SETDC = df_in_Short_SETDC.astype({col_fromTimeWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    
    print_df(df_in_OC_LCM, 'df_in_OC_LCM -2', False)
    print_df(df_in_OC_SET, 'df_in_OC_SET -2', False)
    print_df(df_in_ToSite, 'df_in_ToSite -2', False)
    print_df(df_in_NOH_LCM, 'df_in_NOH_LCM -2', False)
    print_df(df_in_NOH_SET, 'df_in_NOH_SET -2', False)
    print_df(df_in_Short_SETDC, 'df_in_Short_SETDC -2', False)
    
    step('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 1 : Category.[Category] : SOP(Fix), SOP(unFix) 생성
    ################################################################################################################
    step('=====> STEP 1-1 : SOP(Fix), SOP(unFix) Create')
    
    cList_Group = [col_VersionVersionName, col_SubLocationSubLocation, col_TimeWeek, col_ItemMaterialItemMaterial, 
                   col_CategoryCategory]
    cList_LCM_SET_Merge = cList_Group + [col_toDemandDemandID]
    cList_LCM_SET_GROUP = cList_Group + [col_AllocPurReq_ToSite, col_AllocPurReq_LCMItem, col_AllocPurReq_SETMFGItem,
                                         col_AllocPurReq_SETMFGSite, col_AllocPurReq_SETMFGWeek]
    
    cList_Grain = cList_Group + [col_SequenceSequence]
    cList_LCM_SET = cList_Grain + [col_AllocPurReq_Qty, col_AllocPurReq_ToSite, 
                                   col_AllocPurReq_LCMItem, col_AllocPurReq_LCMQty, 
                                   col_AllocPurReq_SETMFGItem, col_AllocPurReq_SETMFGSite, col_AllocPurReq_SETMFGWeek, 
                                   col_AllocPurReq_SETMFGQty]
    
    cList_all = cList_LCM_SET + [col_AllocPurReq_SETDCSite, col_AllocPurReq_SETDCWeek, col_AllocPurReq_SETDCQty]
    
    df_BOMMaster = df_in_BOMMaster[[col_VersionVersionName, col_LocationLocation, col_BOMInfoBOMID, col_BOMMaster_Status]].copy()
    #df_BOMMaster.drop_duplicates(inplace=True)
    print_df(df_BOMMaster, 'df_BOMMaster', False)
    
    #==================================================================================================
    cList_LCM_Group = cList_Group + [col_AllocPurReq_LCMItem, col_AllocPurReq_ToSite]
    cList_LCM = cList_Grain + [col_AllocPurReq_LCMItem, col_AllocPurReq_ToSite, 
                               col_AllocPurReq_Qty, col_AllocPurReq_LCMQty]
    # Merge : df_in_OC_LCM & df_BOMMaster
    df_OC_LCM = df_in_OC_LCM.merge(df_BOMMaster, left_on=[col_VersionVersionName, col_toToLocationToLocation, col_toActivity1Activity1],
                                                 right_on=[col_VersionVersionName, col_LocationLocation, col_BOMInfoBOMID], how='left')
    del df_in_OC_LCM
    df_OC_LCM.rename(columns={col_fromTimeWeek: col_TimeWeek, 
                              col_fromLocationLocation: col_SubLocationSubLocation,
                              col_fromItemItem: col_ItemMaterialItemMaterial, 
                              col_toToItemToItem: col_AllocPurReq_LCMItem, 
                              col_toToLocationToLocation: col_AllocPurReq_ToSite}, inplace=True)
    
    df_OC_LCM[col_CategoryCategory] = np.where(df_OC_LCM[col_BOMMaster_Status] == "Fixed", "SOP(Fix)", "SOP(unFix)")
    df_OC_LCM[col_AllocPurReq_LCMQty] = df_OC_LCM[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_OC_LCM = df_OC_LCM.groupby(cList_LCM_Group, as_index=False)[col_AllocPurReq_LCMQty].sum()
    df_OC_LCM[col_AllocPurReq_Qty] = df_OC_LCM[col_AllocPurReq_LCMQty]
    
    df_OC_LCM['init_seq'] = np.where((df_OC_LCM[col_CategoryCategory] == 'SOP(Fix)'), 1001, 2001)    
    df_OC_LCM[col_SequenceSequence] = df_OC_LCM.groupby(cList_Group).cumcount() + df_OC_LCM['init_seq']
    
    #print_df(df_OC_LCM, 'df_OC_LCM 1', False)
    
    #칼럼정리
    df_OC_LCM = df_OC_LCM[cList_LCM]
    
    print_df(df_OC_LCM, 'df_OC_LCM', False)
    
    # ==================================================================================================
    cList_SET_Group = cList_Group + [col_AllocPurReq_SETMFGItem, col_AllocPurReq_SETMFGWeek, col_AllocPurReq_SETMFGSite]
    cList_SET = cList_Grain + [col_AllocPurReq_SETMFGItem, col_AllocPurReq_SETMFGWeek, col_AllocPurReq_SETMFGSite, 
                               col_AllocPurReq_SETMFGQty]
    
    # Merge : df_in_OC_SET & df_BOMMaster    
    df_OC_SET = df_in_OC_SET.merge(df_BOMMaster, left_on=[col_VersionVersionName, col_toToLocationToLocation, col_toActivity1Activity1],                               
                                                 right_on=[col_VersionVersionName, col_LocationLocation, col_BOMInfoBOMID], how='left')
    del [df_in_OC_SET, df_BOMMaster]
    
    df_OC_SET.rename(columns={col_fromTimeWeek: col_TimeWeek, 
                              col_fromLocationLocation: col_SubLocationSubLocation,
                              col_fromItemItem: col_ItemMaterialItemMaterial,
                              col_toToItemToItem: col_AllocPurReq_SETMFGItem,
                              col_toToTimeToWeek: col_AllocPurReq_SETMFGWeek,
                              col_toToLocationToLocation: col_AllocPurReq_SETMFGSite,
                              col_toTimeWeek: col_AllocPurReq_SETDCWeek,
                              col_toLocationLocation: col_AllocPurReq_SETDCSite}, inplace=True)
    
    df_OC_SET[col_CategoryCategory] = np.where(df_OC_SET[col_BOMMaster_Status] == "Fixed", "SOP(Fix)", "SOP(unFix)")
    df_OC_SET[col_AllocPurReq_SETMFGQty] = df_OC_SET[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_OC_SET = df_OC_SET.groupby(cList_SET_Group, as_index=False)[col_AllocPurReq_SETMFGQty].sum()
    
    df_OC_SET['init_seq'] = np.where((df_OC_SET[col_CategoryCategory] == 'SOP(Fix)'), 1001, 2001)
    df_OC_SET[col_SequenceSequence] = df_OC_SET.groupby(cList_Group).cumcount() + df_OC_SET['init_seq']
    
    #print_df(df_OC_SET, 'df_OC_SET 1', False)
    
    # 칼럼정리
    df_OC_SET = df_OC_SET[cList_SET]
    
    print_df(df_OC_SET, 'df_OC_SET', False)
    
    # Merge ==================================================================================================
    df_SOP = df_OC_LCM.merge(df_OC_SET, on=cList_Grain, how='outer', suffixes=('', '_y'))
    del [df_OC_LCM, df_OC_SET]
    
    #칼럼 정리
    df_SOP = df_SOP[cList_LCM_SET]
    
    print_df(df_SOP, 'df_SOP', False)
    
    step('=====> STEP 1-2 : SOP(Fix), SOP(unFix) Create End')
    
    ################################################################################################################
    # STEP 2 :  Category.[Category] : ToSite 생성 : Substr(FROM.[Location].[Location], 1, 4) != TO.[Location].[Location]
    ################################################################################################################
    step('=====> STEP 2-1 : ToSite Create')
    cList_ToSite_Group = cList_Group + [col_AllocPurReq_ToSite]
    cList_ToSite = cList_Grain + [col_AllocPurReq_Qty, col_AllocPurReq_ToSite]
    
    #df_ToSite = df_in_ToSite.copy()
    #Substr(FROM.[Location].[Location], 1, 4) != TO.[Location].[Location]
    df_ToSite = df_in_ToSite[df_in_ToSite[col_fromLocationLocation].str.slice(0, 4) != df_in_ToSite[col_toLocationLocation]].copy()
    
    del df_in_ToSite
    
    df_ToSite.rename(columns={col_fromTimeWeek: col_TimeWeek, 
                              col_fromLocationLocation: col_SubLocationSubLocation,
                              col_fromItemItem: col_ItemMaterialItemMaterial}, inplace=True)
    
    df_ToSite[col_AllocPurReq_ToSite] = df_ToSite[col_SubLocationSubLocation]
    df_ToSite[col_CategoryCategory]   = 'ToSite'
    
    df_ToSite[col_AllocPurReq_Qty] = df_ToSite[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_ToSite = df_ToSite.groupby(cList_ToSite_Group, as_index=False)[col_AllocPurReq_Qty].sum()
    
    df_ToSite['init_seq'] = 3001
    df_ToSite[col_SequenceSequence] = df_ToSite.groupby(cList_Group).cumcount() + df_ToSite['init_seq']
    
    # 칼럼정리
    df_ToSite = df_ToSite[cList_ToSite]
    
    print_df(df_ToSite, 'df_ToSite', False)
    
    step('=====> STEP 2-2 : ToSite Create End')
    
    ################################################################################################################
    # STEP 3 :  Category.[Category] : NOH 생성
    ################################################################################################################
    step('=====> STEP 3-1 : NOH Create')
    
    # NOH(LCM) -----------------------------------------------------------------
    df_NOH_LCM = df_in_NOH_LCM.copy()
    del df_in_NOH_LCM
    
    df_NOH_LCM.rename(columns={col_fromTimeWeek: col_TimeWeek,
                               col_fromLocationLocation: col_SubLocationSubLocation,
                               col_fromItemItem: col_ItemMaterialItemMaterial,
                               col_toToItemToItem: col_AllocPurReq_LCMItem,
                               col_toToLocationToLocation: col_AllocPurReq_ToSite}, inplace=True)
    
    df_NOH_LCM[col_CategoryCategory] = 'NOH'
    df_NOH_LCM[col_AllocPurReq_LCMQty] = df_NOH_LCM[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_NOH_LCM = df_NOH_LCM.groupby(cList_LCM_Group, as_index=False)[col_AllocPurReq_LCMQty].sum()
    df_NOH_LCM[col_AllocPurReq_Qty] = df_NOH_LCM[col_AllocPurReq_LCMQty]
    
    df_NOH_LCM['init_seq'] = 4001
    df_NOH_LCM[col_SequenceSequence] = df_NOH_LCM.groupby(cList_Group).cumcount() + df_NOH_LCM['init_seq']
    
    print_df(df_NOH_LCM, 'df_NOH_LCM', False)
    
    # NOH(SET) -----------------------------------------------------------------
    df_NOH_SET = df_in_NOH_SET.copy()
    del df_in_NOH_SET
    
    df_NOH_SET.rename(columns={col_fromTimeWeek: col_TimeWeek,
                               col_fromLocationLocation: col_SubLocationSubLocation,
                               col_fromItemItem: col_ItemMaterialItemMaterial,
                               col_toToItemToItem: col_AllocPurReq_SETMFGItem,
                               col_toToTimeToWeek: col_AllocPurReq_SETMFGWeek,
                               col_toToLocationToLocation: col_AllocPurReq_SETMFGSite}, inplace=True)
    
    df_NOH_SET[col_CategoryCategory] = 'NOH'
    df_NOH_SET[col_AllocPurReq_SETMFGQty] = df_NOH_SET[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_NOH_SET = df_NOH_SET.groupby(cList_SET_Group, as_index=False)[col_AllocPurReq_SETMFGQty].sum()
    
    df_NOH_SET['init_seq'] = 4001
    df_NOH_SET[col_SequenceSequence] = df_NOH_SET.groupby(cList_Group).cumcount() + df_NOH_SET['init_seq']
    
    print_df(df_NOH_SET, 'df_NOH_SET', False)
    
    # Merge ==================================================================================================
    df_NOH = df_NOH_LCM.merge(df_NOH_SET, on=cList_Grain, how='outer', suffixes=('', '_y'))
    del [df_NOH_LCM, df_NOH_SET]
    
    # 칼럼 정리
    df_NOH = df_NOH[cList_LCM_SET]
    
    print_df(df_NOH, 'df_NOH', False)
    
    step('=====> STEP 3-2 : NOH Create End')
    
    ################################################################################################################
    # STEP 4 :  Category.[Category] : Short SETDC 생성
    ################################################################################################################
    step('=====> STEP 4-1 : Short SETDC Create')
    cList_ShortSetDc_Group = cList_Group + [col_AllocPurReq_SETDCWeek, col_AllocPurReq_SETDCSite]
    cList_ShortSetDc = cList_Grain + [col_AllocPurReq_Qty, col_AllocPurReq_SETDCWeek, col_AllocPurReq_SETDCSite, 
                                      col_AllocPurReq_SETDCQty]
    
    df_ShortSetDc = df_in_Short_SETDC.copy()
    del df_in_Short_SETDC
    
    df_ShortSetDc.rename(columns={col_fromTimeWeek: col_TimeWeek,
                             col_fromLocationLocation: col_SubLocationSubLocation,
                             col_fromItemItem: col_ItemMaterialItemMaterial,
                             col_toTimeWeek: col_AllocPurReq_SETDCWeek,
                             col_toLocationLocation: col_AllocPurReq_SETDCSite}, inplace=True)
    
    df_ShortSetDc[col_CategoryCategory] = 'Short'
    df_ShortSetDc[col_AllocPurReq_SETDCQty] = df_ShortSetDc[col_WMaterialRootCauseQuantity].fillna(0).astype('int64')
    df_ShortSetDc = df_ShortSetDc.groupby(cList_ShortSetDc_Group, as_index=False)[col_AllocPurReq_SETDCQty].sum()
    df_ShortSetDc[col_AllocPurReq_Qty] = df_ShortSetDc[col_AllocPurReq_SETDCQty]
    
    df_ShortSetDc['init_seq'] = 5001
    df_ShortSetDc[col_SequenceSequence] = df_ShortSetDc.groupby(cList_Group).cumcount() + df_ShortSetDc['init_seq']
    
    # 칼럼정리
    df_ShortSetDc = df_ShortSetDc[cList_ShortSetDc]
    
    print_df(df_ShortSetDc, 'df_ShortSetDc', False)
    
    step('=====> STEP 4-2 : Short SETDC Create End')
    
    ################################################################################################################
    # STEP 5 :  Category.[Category] : Total 생성
    ################################################################################################################
    step('=====> STEP 5-1 : Total Create')
    
    # conacat : df_SOP & df_NOH
    df_AllocPurReq = pd.concat([df_SOP, df_ToSite])
    del [df_SOP, df_ToSite]
        
    # conacat : df_AllocPurReq & df_NOH
    df_AllocPurReq = pd.concat([df_AllocPurReq, df_NOH])
    del df_NOH
        
    # conacat : df_AllocPurReq & df_NOH
    df_AllocPurReq = pd.concat([df_AllocPurReq, df_ShortSetDc])
    del df_ShortSetDc
    
    cList_Total = [col_VersionVersionName, col_SubLocationSubLocation, col_TimeWeek, col_ItemMaterialItemMaterial]
    df_Total = df_AllocPurReq.groupby(cList_Total, as_index=False)[col_AllocPurReq_Qty].sum()
    df_Total[col_CategoryCategory] = 'Total'
    df_Total[col_SequenceSequence] = 1
    
    print_df(df_Total, 'df_Total', False)
    
    # conacat : df_AllocPurReq & df_Total
    df_AllocPurReq = pd.concat([df_AllocPurReq, df_Total])
    del df_Total
    
    # 칼럼 정리
    df_AllocPurReq = df_AllocPurReq[cList_all]
    
    #Sub Location.[Sub Location] ==> Location.[Location] 로 output 칼럼 변경 : 2025.07.04
    df_AllocPurReq.rename(columns={col_SubLocationSubLocation:col_LocationLocation}, inplace=True)
    
    print_df(df_AllocPurReq, 'df_AllocPurReq', False)
    
    # 임시 확인용
    #df_AllocPurReq_sum = df_AllocPurReq.groupby(cList_Group, as_index=False).agg({col_AllocPurReq_Qty: "sum",
    #                                                                              col_AllocPurReq_LCMQty: "sum",
    #                                                                              col_AllocPurReq_SETMFGQty: "sum"}
    #                                                                             , skipna = True)
    
    step('=====> STEP 5-2 : Total End')
    
    ################################################################################################################
    # STEP 6 : output table create
    ################################################################################################################
    step('=====> STEP 6-1 : Final output table create')
    
    # out Data 생성 :
    df_out_AllocPurReq = df_AllocPurReq.copy()
    del df_AllocPurReq
    
    # 버전 처리
    #df_out_AllocPurReq[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_AllocPurReq.shape
    note(f'=====> Final df_out_AllocPurReq rows : {row_count}, column : {col_count}')
    print_df(df_out_AllocPurReq, 'df_out_AllocPurReq', False)
    step('=====> STEP 6-2 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_AllocPurReq, 'df_out_AllocPurReq')
    
    step('=====> STEP 6-3 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_AllocPurReq = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()