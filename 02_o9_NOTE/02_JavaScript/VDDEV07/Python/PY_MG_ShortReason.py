"""
* 프로그램명 
    - PY_MG_ShortReason

* 내용
    - Short Reason 등록

* 변경이력
- 2024.09.09 / 신동언 / Create
- 2025.10.16 / 양희영 / Update


* Flow Summary

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
    - paramGraph_VALUE : OBO
* Input Tables
    - df_in_MtrlRCA : 002.008W Solver Outputs OBO Material RCA
              Select (Version.[Version Name] * FROM.[Activity2].[Activity2] * FROM.[Time].[Week] * FROM.[RootCause].[Problem Type] * FROM.[Location].[Location] * FROM.[Location].[Site Stage] * 
              FROM.[Activity1].[Activity1] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item] * FROM.[Item].[Item Stage] * TO.[Sequence ID].[Sequence ID] * TO.[Location].[Location] * 
              TO.[Item].[Item] * TO.[Demand].[DemandID] * TO.[Demand Type].[Demand Type] * TO.[Sales Domain].[Customer Group] * TO.[Time].[Week]) on row, 
              ({Edge.[002.008W Solver Outputs OBO Material RCA].[W MP RCA Type OBO Material], Edge.[002.008W Solver Outputs OBO Material RCA].[W OBO Material Constraint Quantity]}) 
              on column where {RelationshipType.[002.008W Solver Outputs OBO Material RCA]};

    - df_in_CapaRCA : Graph : 002.009W Solver Outputs OBO Capacity RCA
                      Select (Version.[Version Name] * FROM.[Activity2].[Activity2] * FROM.[Location].[Location] * FROM.[RootCause].[Problem Type] * FROM.[Resource].[Resource] * 
                      FROM.[Resource].[Resource Type] * FROM.[Activity3].[Activity3] * FROM.[Activity1].[Activity1] * FROM.[Time].[Week] * TO.[Sequence ID].[Sequence ID] * 
                      TO.[Demand Type].[Demand Type] * TO.[Location].[Location] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Time].[Week] * TO.[Item].[Item]) on row, 
                      ({Edge.[002.009W Solver Outputs OBO Capacity RCA].[W MP RCA Type OBO Capacity] , Edge.[002.009W Solver Outputs OBO Capacity RCA].[W OBO Capacity Constraint Quantity]}) 
                      on column where {RelationshipType.[002.009W Solver Outputs OBO Capacity RCA]};
                      
    - df_in_MtrlRtCause : 002.005W Solver Outputs Material Root Cause 
                       Select (Version.[Version Name] * FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * FROM.[RootCause].[Problem Type] * 
                       FROM.[Location].[Location] * FROM.[Location].[Site Stage] * FROM.[Time].[Week] * FROM.[Item].[Item] * FROM.[Item].[Item Stage] * TO.[Time].[Week] * TO.[Demand].[DemandID] * 
                       TO.[Location].[Location] * TO.[Item].[Item] * TO.[Demand Type].[Demand Type] * TO.[Sales Domain].[Customer Group]) on row, 
                       ({Edge.[002.005W Solver Outputs Material Root Cause].[W Material Root Cause Quantity] , Edge.[002.005W Solver Outputs Material Root Cause].[W Material Demand Late Short Revenue Impact] , 
                         Edge.[002.005W Solver Outputs Material Root Cause].[W MP RCA Type Additive Material] , Edge.[002.005W Solver Outputs Material Root Cause].[W Material Short Late Problem Quantity] , 
                         Edge.[002.005W Solver Outputs Material Root Cause].[W Material Demand Late Short Quantity Edge]}) 
                       on column where {RelationshipType.[002.005W Solver Outputs Material Root Cause]};
                       
    - df_in_CapaRtCause : 002.006W Solver Outputs Capacity Root Cause
                        Select (Version.[Version Name] * FROM.[Resource].[Resource] * FROM.[Resource].[Resource Type] * FROM.[Activity1].[Activity1] * FROM.[Activity3].[Activity3] * 
                        FROM.[Activity2].[Activity2] * FROM.[RootCause].[Problem Type] * FROM.[Time].[Week] * FROM.[Location].[Location] * TO.[Demand Type].[Demand Type] * 
                        TO.[Sales Domain].[Customer Group] * TO.[Item].[Item] * TO.[Demand].[DemandID] * TO.[Location].[Location] * TO.[Time].[Week]) on row, 
                        ({Edge.[002.006W Solver Outputs Capacity Root Cause].[W MP RCA Type Additive Capacity] , Edge.[002.006W Solver Outputs Capacity Root Cause].[W Capacity Root Cause Quantity] , 
                        Edge.[002.006W Solver Outputs Capacity Root Cause].[W Capacity JIT Bucket] , Edge.[002.006W Solver Outputs Capacity Root Cause].[W Capacity Short Late Problem Quantity] , 
                        Edge.[002.006W Solver Outputs Capacity Root Cause].[W Capacity Demand Late Short Revenue Impact] , Edge.[002.006W Solver Outputs Capacity Root Cause].[W Capacity Demand Late Short Quantity Edge]}) 
                        on column where {RelationshipType.[002.006W Solver Outputs Capacity Root Cause]};

    - df_in_VsType : Select ([Version].[Version Name] * [Version].[Version Type]);
    - df_in_ProblemType : select ([Problem Type].[Problem Reason] * [Problem Type].[Problem Category1] * [Problem Type].[Problem Category2] * 
                                                 [Problem Type].[Problem Type BY] * [Problem Type].[Problem Type o9] * [Problem Type].[Short Category] * [Problem Type].[Short Reason]) on row 
                                  include memberproperties  {[Problem Type].[Problem Reason],[Problem Node Define]}
                                                                {[Problem Type].[Problem Reason],[Problem Reason Desc]}
                                                                {[Problem Type].[Problem Reason],[Problem Factor Define]}
                                                                {[Problem Type].[Short Reason],[Short Reason Desc]};
    - df_in_Item : Select ([Item].[Item] * [Item].[Item Stage]);
    - df_in_ProblemType : select ([Problem Type].[Problem Reason] * [Problem Type].[Problem Category1] * [Problem Type].[Problem Category2] * [Problem Type].[Problem Type BY] * 
                          [Problem Type].[Problem Type o9] * [Problem Type].[Short Category] * [Problem Type].[Short Reason]) 
                          on row include memberproperties  {[Problem Type].[Problem Reason],[Problem Node Define]} {[Problem Type].[Problem Reason],[Problem Reason Desc]} 
                          {[Problem Type].[Problem Reason],[Problem Factor Define]} {[Problem Type].[Short Reason],[Short Reason Desc]};
    - df_in_Item : Select ([Item].[Item] * [Item].[Item Stage]);
    - df_in_IvnNodeParam : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[W Finite Period]}) on column;
    - df_in_SOPAdjSTBMVrsW : Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                             ({Measure.[SOP Adjust SET W_Chg Reason]}) on column;
    - df_in_ItemAttrRef : Select ([Version].[Version Name] * [Item].[Item] ) on row, ({Measure.[Item Attr Ref_Resolution]}) on column;
    - df_in_ActParam : Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, 
                       ({Measure.[W Activity Lead Time], Measure.[W Activity Start Date]}) on column;
    - df_in_WCapacity : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row, 
                        ({Measure.[W Resource Base Capacity], Measure.[W Flex Capacity Band1], Measure.[W Flex Capacity Band2]}) on column;
    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Item Site Asn_Cur Status]}) on column;
    - df_in_PLCSales : Select ([Version].[Version Name] * [Item].[Item] * [Sales Domain].[AP2] ) on row, ({Measure.[PLC Sales_EOS Com Date], Measure.[PLC Sales_RTS Com Date]}) on column;
    - df_in_TimeWeek : Select ([Time].[Day] * [Time].[Week]);
    - df_in_SalesDomain : select ([Sales Domain].[Customer Group] * [Sales Domain].[AP2]);
    - df_in_Mtrl_CustReason : Select ([Version].[Version Name] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const_Grp2]}) on column;
    - df_in_Capa_CustReason : Select ([Version].[Version Name] * [Sequence].[Sequence] * [Group].[Group ID] ) on row, ({Measure.[Const Grp_Startdate], Measure.[Const Grp_Enddate], Measure.[Const Grp_Reason]}) on column;
* Output Tables
    -  : df_out_ShortReason : Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Sequence].[Sequence] * [Demand].[DemandID] * [Problem Type].[Problem Reason] ) on row, 
                              ({Measure.[Short Reason_Problem Activity1], Measure.[Short Reason_Problem Activity2], Measure.[Short Reason_Problem Activity3], Measure.[Short Reason_Problem BOD], 
                                Measure.[Short Reason_Problem BOM], Measure.[Short Reason_Problem Category1], Measure.[Short Reason_Problem Category2], Measure.[Short Reason_Problem Factor], 
                                Measure.[Short Reason_Problem Item], Measure.[Short Reason_Problem Need Qty], Measure.[Short Reason_Problem Owner], Measure.[Short Reason_Problem Qty], 
                                Measure.[Short Reason_Problem Ref UI], Measure.[Short Reason_Problem Resource], Measure.[Short Reason_Problem Site], Measure.[Short Reason_Problem Type BY], 
                                Measure.[Short Reason_Problem Type o9], Measure.[Short Reason_Problem Value1], Measure.[Short Reason_Problem Value2], Measure.[Short Reason_Problem Value3], 
                                Measure.[Short Reason_Problem Week], Measure.[Short Reason_Short Category], Measure.[Short Reason_Short Reason]}) on column;

* 테스트 스크립트
    //GRAPH : OBO 호출
    EXEC plugin instance [PY_MG_ShortReason] for measures {[Short Reason_Short Reason]} using scope (&MPV)
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (paramGraph, "OBO"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};
    
    //GRAPH : NOT OBO 호출    
    EXEC plugin instance [PY_MG_ShortReason] for measures {[Short Reason_Short Reason]} using scope (&MPV)
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (paramGraph, "NOTOBO"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};

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

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_ShortReason'
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
    versionVersionType         = 'Version.[Version Type]'
    fromRootCauseProblemType   = 'from.[RootCause].[Problem Type]'
    fromItemItem               = 'from.[Item].[Item]'
    fromItemItemStage          = 'from.[Item].[Item Stage]'
    fromActivity1Activity1     = 'from.[Activity1].[Activity1]'
    fromActivity2Activity2     = 'from.[Activity2].[Activity2]'
    fromActivity3Activity3     = 'from.[Activity3].[Activity3]'
    fromLocationLocation       = 'from.[Location].[Location]'
    fromLocationSiteStage      = 'from.[Location].[Site Stage]'
    fromResourceResource       = 'from.[Resource].[Resource]'
    fromResourceResourceType   = 'from.[Resource].[Resource Type]'
    fromTimeWeek               = 'from.[Time].[Week]'
    
    toSequenceIDSequenceID     = 'to.[Sequence ID].[Sequence ID]'
    toDemandDemandID           = 'to.[Demand].[DemandID]'
    toDemandTypeDemandType     = 'to.[Demand Type].[Demand Type]'
    toItemItem                 = 'to.[Item].[Item]'
    toLocationLocation         = 'to.[Location].[Location]'
    toSalesDomainCustomerGroup = 'to.[Sales Domain].[Customer Group]'
    toTimeWeek                 = 'to.[Time].[Week]'
    
    problemTypeProblemReason    = 'Problem Type.[Problem Reason]'
    problemTypeShortCategory    = 'Problem Type.[Short Category]'
    problemTypeShortReason      = 'Problem Type.[Short Reason]'
    problemTypeProblemCategory1 = 'Problem Type.[Problem Category1]'
    problemTypeProblemCategory2 = 'Problem Type.[Problem Category2]'
    problemTypeProblemOwner     = 'Problem Type.[Problem Owner]'
    problemTypeProblemReasonProblemRefUI = 'Problem Type.[Problem Reason].Problem Ref UI' 
    
    demandDemandID           = 'Demand.[DemandID]'
    itemItem                 = 'Item.[Item]'
    itemItemStage            = 'Item.[Item Stage]'
    salesDomainCustomerGroup = 'Sales Domain.[Customer Group]'
    salesDomainAP2           = 'Sales Domain.[AP2]'
    timeWeek                 = 'Time.[Week]'
    timeDay                  = 'Time.[Day]'
    locationLocation         = 'Location.[Location]'
    subLocationSubLocation   = 'Sub Location.[Sub Location]'
    transModeTransMode       = 'Trans Mode.[Trans Mode]'
    sequenceSequence         = 'Sequence.[Sequence]'
    activity1Activity1       = 'Activity1.[Activity1]'
    activity2Activity2       = 'Activity2.[Activity2]'
    Activity3Activity3       = 'Activity3.[Activity3]'
    resourceResource         = 'Resource.[Resource]'
    resourceResourceType     = 'Resource.[Resource Type]'
    groupGroupID             = 'Group.[Group ID]'
    
    col_ResourceType = ''
    
    wMPRCATypeOBOMaterial             = '002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]'
    wOBOMaterialConstraintQuantity    = '002.008W Solver Outputs OBO Material RCA.[W OBO Material Constraint Quantity]'
    wMPRCATypeOBOCapacity             = '002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]'
    wOBOCapacityConstraintQuantity    = '002.009W Solver Outputs OBO Capacity RCA.[W OBO Capacity Constraint Quantity]'
    
    wMPRCATypeAdditiveMaterial = '002.005W Solver Outputs Material Root Cause.[W MP RCA Type Additive Material]'
    wMaterialRootCauseQuantity = '002.005W Solver Outputs Material Root Cause.[W Material Root Cause Quantity]'
    wMPRCATypeAdditiveCapacity = '002.006W Solver Outputs Capacity Root Cause.[W MP RCA Type Additive Capacity]'
    wCapacityRootCauseQuantity = '002.006W Solver Outputs Capacity Root Cause.[W Capacity Root Cause Quantity]'
    
    graph_Rca_Material      = ''
    graph_Material_Quantity = ''
    graph_Rca_Capacity      = ''
    graph_Capacity_Quantity = ''
    
    wActiveStartDate                  = 'W Active Start Date'
    wFinitePeriod                     = 'W Finite Period'
    wActivityLeadTime                 = 'W Activity Lead Time'
    wActivityStartDate                = 'W Activity Start Date'
    wResourceBaseCapacity             = 'W Resource Base Capacity'
    wFlexCapacityBand1                = 'W Flex Capacity Band1'
    wFlexCapacityBand2                = 'W Flex Capacity Band2'
    wFlexCapacityBand3                = 'W Flex Capacity Band3' # Measure 없음 확인필요
    #아래메저로 변경 확인 필요 : sOPAdjustSETBOMVersionW_ChgReason = 'SOP Adjust SET BOM Version W_Chg Reason'
    sOPAdjustSETW_ChgReason           = 'SOP Adjust SET W_Chg Reason'
    itemAttrRef_Resolution            = 'Item Attr Ref_Resolution'
    itemSiteAsn_CurStatus             = 'Item Site Asn_Cur Status'
    pLCSales_EOSComDate               = 'PLC Sales_EOS Com Date'
    pLCSales_RTSComDate               = 'PLC Sales_RTS Com Date'
    preAllocConst_Grp2                = 'Pre Alloc Const_Grp2'
    constGrp_Reason                   = 'Const Grp_Reason'
    constGrp_Startdate                = 'Const Grp_Startdate'
    constGrp_Enddate                  = 'Const Grp_Enddate'
    
    eOSComWeek                        = 'EOSComWeek'
    rTSComWeek                        = 'RTSComWeek'
    custReason_StartWeek             = 'CustReason_StartWeek'
    custReason_EndWeek               = 'CustReason_EndWeek'
    
    shortReason_ProblemActivity1 = 'Short Reason_Problem Activity1'
    shortReason_ProblemActivity2 = 'Short Reason_Problem Activity2'
    shortReason_ProblemActivity3 = 'Short Reason_Problem Activity3'
    shortReason_ProblemBOD       = 'Short Reason_Problem BOD'
    shortReason_ProblemBOM       = 'Short Reason_Problem BOM'
    shortReason_ProblemCategory1 = 'Short Reason_Problem Category1'
    shortReason_ProblemCategory2 = 'Short Reason_Problem Category2'
    shortReason_ProblemFactor    = 'Short Reason_Problem Factor'
    shortReason_ProblemItem      = 'Short Reason_Problem Item'
    shortReason_ProblemNeedQty   = 'Short Reason_Problem Need Qty'
    shortReason_ProblemOwner     = 'Short Reason_Problem Owner'
    shortReason_ProblemQty       = 'Short Reason_Problem Qty'
    shortReason_ProblemRefUI     = 'Short Reason_Problem Ref UI'
    shortReason_ProblemResource  = 'Short Reason_Problem Resource'
    shortReason_ProblemSite      = 'Short Reason_Problem Site'
    shortReason_ProblemTypeBY    = 'Short Reason_Problem Type BY'
    shortReason_ProblemTypeo9    = 'Short Reason_Problem Type o9'
    shortReason_ProblemValue1    = 'Short Reason_Problem Value1'
    shortReason_ProblemValue2    = 'Short Reason_Problem Value2'
    shortReason_ProblemValue3    = 'Short Reason_Problem Value3'
    shortReason_ProblemWeek      = 'Short Reason_Problem Week'
    shortReason_ShortCategory    = 'Short Reason_Short Category'
    shortReason_ShortReason      = 'Short Reason_Short Reason'
    
    sysdate                      = 'sysdate'    
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    paramGraph_VALUE      = "OBO"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        paramGraph      = paramGraph_VALUE
        
        df_in_MtrlRCA        = read_csv_file("df_in_MtrlRCA")
        df_in_CapaRCA        = read_csv_file("df_in_CapaRCA")
        
        df_in_MtrlRtCause    = read_csv_file("df_in_MtrlRtCause")
        df_in_CapaRtCause    = read_csv_file("df_in_CapaRtCause")
        
        df_in_VsType         = read_csv_file("df_in_VsType")
        df_in_ProblemType    = read_csv_file("df_in_ProblemType")
        df_in_Item           = read_csv_file("df_in_Item")
        df_in_IvnNodeParam   = read_csv_file("df_in_IvnNodeParam")
        df_in_SOPAdjSTBMVrsW = read_csv_file("df_in_SOPAdjSTBMVrsW")
        df_in_ItemAttrRef    = read_csv_file("df_in_ItemAttrRef")
        df_in_ActParam       = read_csv_file("df_in_ActParam")
        df_in_WCapacity      = read_csv_file("df_in_WCapacity")
        df_in_ItemSiteAsn    = read_csv_file("df_in_ItemSiteAsn")
        df_in_PLCSales       = read_csv_file("df_in_PLCSales")
        df_in_TimeWeek       = read_csv_file("df_in_TimeWeek")
        df_in_SalesDomain    = read_csv_file("df_in_SalesDomain")

        df_in_Mtrl_CustReason = read_csv_file("df_in_Mtrl_CustReason")
        df_in_Capa_CustReason = read_csv_file("df_in_Capa_CustReason")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    if paramGraph is None or paramGraph.strip() == '':
        paramGraph      = paramGraph_VALUE
    
    print_df(df_in_MtrlRCA, 'df_in_MtrlRCA',False)
    print_df(df_in_CapaRCA, 'df_in_CapaRCA',False)
    
    print_df(df_in_MtrlRtCause, 'df_in_MtrlRtCause',False)
    print_df(df_in_CapaRtCause, 'df_in_CapaRtCause',False)
    
    print_df(df_in_VsType, 'df_in_VsType',False)
    print_df(df_in_ProblemType, 'df_in_ProblemType',False)
    print_df(df_in_Item, 'df_in_Item',False)
    print_df(df_in_IvnNodeParam, 'df_in_IvnNodeParam',False)
    print_df(df_in_SOPAdjSTBMVrsW, 'df_in_SOPAdjSTBMVrsW',False)
    print_df(df_in_ItemAttrRef, 'df_in_ItemAttrRef',False)
    print_df(df_in_ActParam, 'df_in_ActParam',False)
    print_df(df_in_WCapacity, 'df_in_WCapacity',False)
    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',False)
    print_df(df_in_PLCSales, 'df_in_PLCSales',False)
    print_df(df_in_TimeWeek, 'df_in_TimeWeek',False)
    print_df(df_in_SalesDomain, 'df_in_SalesDomain',False)

    print_df(df_in_Mtrl_CustReason, 'df_in_Mtrl_CustReason',False)
    print_df(df_in_Capa_CustReason, 'df_in_Capa_CustReason',False)
    
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
    #--------------------------------------------------------------------------------
    
    if df_in_ActParam[wActivityStartDate].dtype != 'datetime64[ns]':
        df_in_ActParam[wActivityStartDate]  = pd.to_datetime(df_in_ActParam[wActivityStartDate], 
                                                             format='%m/%d/%Y %I:%M:%S %p')
    print_df(df_in_ActParam, 'df_in_ActParam 2', False)
    
    if df_in_PLCSales[pLCSales_EOSComDate].dtype != 'datetime64[ns]':
        # 2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_PLCSales[pLCSales_EOSComDate] = np.where(df_in_PLCSales[pLCSales_EOSComDate].isna(),
                                                       df_in_PLCSales[pLCSales_EOSComDate],
                                                       df_in_PLCSales[pLCSales_EOSComDate].apply(
                                                           lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                                                       )
        df_in_PLCSales[pLCSales_EOSComDate] = pd.to_datetime(df_in_PLCSales[pLCSales_EOSComDate],
                                                             format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_PLCSales[pLCSales_RTSComDate].dtype != 'datetime64[ns]':
        df_in_PLCSales[pLCSales_RTSComDate] = pd.to_datetime(df_in_PLCSales[pLCSales_RTSComDate], 
                                                             format='%m/%d/%Y %I:%M:%S %p')
    
    df_in_PLCSales    = df_in_PLCSales.astype({salesDomainAP2: 'str'}, copy=True)
    print_df(df_in_PLCSales, 'df_in_PLCSales 2', False)
    
    df_in_SalesDomain = df_in_SalesDomain.astype({salesDomainAP2: 'str'}, copy=True)
    print_df(df_in_SalesDomain, 'df_in_SalesDomain 2', False)
    
    df_in_TimeWeek[timeDay] = pd.to_datetime(df_in_TimeWeek[timeDay], format='%Y-%m-%d')
    df_in_TimeWeek  = df_in_TimeWeek.astype({timeWeek: 'str'}, copy=True)
    print_df(df_in_TimeWeek, 'df_in_TimeWeek 2', False)
    
    df_in_WCapacity = df_in_WCapacity.astype({timeWeek: 'str'}, copy=True)
    print_df(df_in_WCapacity, 'df_in_WCapacity 2', False)
    
    df_in_SOPAdjSTBMVrsW = df_in_SOPAdjSTBMVrsW.astype({timeWeek: 'str'}, copy=True)
    print_df(df_in_SOPAdjSTBMVrsW, 'df_in_SOPAdjSTBMVrsW 2', False)
    
    #Measure.[Const Grp_Startdate], Measure.[Const Grp_Enddate] 는 data type : String, 주차 정보 (2025.03.24 확인)
    #if df_in_Capa_CustReason[constGrp_Startdate].dtype != 'datetime64[ns]':
    #    df_in_Capa_CustReason[constGrp_Startdate]  = pd.to_datetime(df_in_Capa_CustReason[constGrp_Startdate], format='%m/%d/%Y %I:%M:%S %p')

    #if df_in_Capa_CustReason[constGrp_Enddate].dtype != 'datetime64[ns]':
    #    df_in_Capa_CustReason[constGrp_Enddate]  = pd.to_datetime(df_in_Capa_CustReason[constGrp_Enddate], format='%m/%d/%Y %I:%M:%S %p')
    #print_df(df_in_Capa_CustReason, 'df_in_Capa_CustReason 2', False)
    
    if df_in_Capa_CustReason[constGrp_Startdate].dtype == 'float64':
        df_in_Capa_CustReason[constGrp_Startdate] = df_in_Capa_CustReason[constGrp_Startdate].fillna(0).astype('int64')
        
    if df_in_Capa_CustReason[constGrp_Enddate].dtype == 'float64':
        df_in_Capa_CustReason[constGrp_Enddate]   = df_in_Capa_CustReason[constGrp_Enddate].fillna(0).astype('int64')
    
    df_in_Capa_CustReason = df_in_Capa_CustReason.astype({constGrp_Startdate: 'str',
                                                          constGrp_Enddate: 'str'}, copy=True)
    df_in_Capa_CustReason[constGrp_Startdate] = np.where((df_in_Capa_CustReason[constGrp_Startdate].str.len() == 6),
                                                         df_in_Capa_CustReason[constGrp_Startdate],
                                                         np.nan)
    
    df_in_Capa_CustReason[constGrp_Enddate] = np.where((df_in_Capa_CustReason[constGrp_Enddate].str.len() == 6),
                                                       df_in_Capa_CustReason[constGrp_Enddate],
                                                        np.nan)
    
    print_df(df_in_Capa_CustReason, 'df_in_Capa_CustReason 2', False)
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    note(f'=====> paramGraph : {paramGraph}')
        
    step('=====> Input table load End')
    
    ################################################################################################################
    # STEP 0 : 데이터 선 가공 
    ################################################################################################################
    step('=====> STEP 0 : Mtrl Data Preprocessing')
    
    # Main df 생성
    '''
    "Parameter == ""OBO"" 
        → 002.008W Solver Outputs OBO Material RCA, 002.009W Solver Outputs OBO Capacity RCA 사용"
    "Parameter <> ""OBO"" 
        → 002.005W Solver Outputs Material Root Cause, 002.006W Solver Outputs Capacity Root Cause 사용"
    '''
    if paramGraph == "OBO" :
        df_Main_MtrlRCA = df_in_MtrlRCA.copy()
        df_Main_CapaRCA = df_in_CapaRCA.copy()
        
        graph_Rca_Material      = wMPRCATypeOBOMaterial
        graph_Material_Quantity = wOBOMaterialConstraintQuantity
        graph_Rca_Capacity      = wMPRCATypeOBOCapacity
        graph_Capacity_Quantity = wOBOCapacityConstraintQuantity
    else :
        df_Main_MtrlRCA = df_in_MtrlRtCause.copy()
        df_Main_CapaRCA = df_in_CapaRtCause.copy()
        
        graph_Rca_Material = wMPRCATypeAdditiveMaterial
        graph_Material_Quantity = wMaterialRootCauseQuantity
        graph_Rca_Capacity = wMPRCATypeAdditiveCapacity
        graph_Capacity_Quantity = wCapacityRootCauseQuantity
        
    del [df_in_MtrlRCA, df_in_CapaRCA, df_in_MtrlRtCause, df_in_CapaRtCause]
    
    # DATA TYPE 설정
    df_Main_MtrlRCA = df_Main_MtrlRCA.astype({fromTimeWeek:'str', toTimeWeek: 'str'}, copy=True)
    df_Main_CapaRCA = df_Main_CapaRCA.astype({toSalesDomainCustomerGroup: 'str', fromTimeWeek: 'str',
                                              toLocationLocation:'str', toTimeWeek: 'str'}, copy=True)
    
    print_df(df_Main_MtrlRCA, 'df_Main_MtrlRCA',False)
    print_df(df_Main_CapaRCA, 'df_Main_CapaRCA',False)
    
    # csv 파일에서 서버와 로컬의 칼럼명이 다르게 설정됨.
    if fromResourceResourceType in df_Main_CapaRCA:
        col_ResourceType = fromResourceResourceType
    else:
        col_ResourceType = resourceResourceType
    
    
    # Merge 를위한 칼럼명 변경
    df_in_ActParam.rename(columns={activity1Activity1: fromActivity1Activity1,
                                   activity2Activity2: fromActivity2Activity2,
                                   Activity3Activity3: fromActivity3Activity3}, inplace=True)
    
    # Merge : Version.[Version Type]
    df_Main_MtrlRCA = df_Main_MtrlRCA.merge(df_in_VsType, on=[versionVersionName], how='inner')    
    del df_in_VsType
    
    # Merge : df_in_ItemAttrRef
    df_in_ItemAttrRef.rename(columns={itemItem: fromItemItem}, inplace=True)
    df_Main_MtrlRCA = df_Main_MtrlRCA.merge(df_in_ItemAttrRef, on=[versionVersionName,fromItemItem], how='left')
    del df_in_ItemAttrRef
    
    # df_in_TimeWeek 칼럼 정리
    df_in_TimeWeek = df_in_TimeWeek[[timeDay,timeWeek]].copy()
    
    # Merge EOSComDate: df_in_PLCSales & df_in_TimeWeek
    df_PLCSales_EOS = df_in_PLCSales.merge(df_in_TimeWeek,left_on=[pLCSales_EOSComDate],right_on=[timeDay], how='inner')
    df_PLCSales_EOS.drop(columns=[timeDay,pLCSales_RTSComDate],inplace=True)
    df_PLCSales_EOS.rename(columns={timeWeek:eOSComWeek}, inplace=True)
    print_df(df_PLCSales_EOS, 'df_PLCSales_EOS',False)
    
    # Merge RTSComDate: df_in_PLCSales & df_in_TimeWeek
    df_PLCSales_RTS = df_in_PLCSales.merge(df_in_TimeWeek, left_on=[pLCSales_RTSComDate], 
                                           right_on=[timeDay], how='inner')
    df_PLCSales_RTS.drop(columns=[timeDay,pLCSales_EOSComDate], inplace=True)
    df_PLCSales_RTS.rename(columns={timeWeek: rTSComWeek}, inplace=True)
    print_df(df_PLCSales_RTS, 'df_PLCSales_RTS',False)    
    del [df_in_PLCSales, df_in_TimeWeek]
    
    # Merge : df_in_Capa_CustReason & df_in_TimeWeek : startWeek
    df_Capa_CustReason = df_in_Capa_CustReason.copy()
    del df_in_Capa_CustReason
    #df_Capa_CustReason = df_in_Capa_CustReason.merge(df_in_TimeWeek, left_on=[constGrp_Startdate], right_on=[timeDay], how='inner')
    #df_Capa_CustReason.drop(columns=[timeDay, constGrp_Startdate], inplace=True)
    #df_Capa_CustReason.rename(columns={timeWeek: custReason_StartWeek}, inplace=True)
    df_Capa_CustReason[custReason_StartWeek] = df_Capa_CustReason[constGrp_Startdate]
    
    # Merge : df_Capa_CustReason & df_in_TimeWeek : endWeek
    #df_Capa_CustReason = df_Capa_CustReason.merge(df_in_TimeWeek, left_on=[constGrp_Enddate], right_on=[timeDay], how='inner')
    #df_Capa_CustReason.drop(columns=[timeDay, constGrp_Enddate], inplace=True)
    #df_Capa_CustReason.rename(columns={timeWeek: custReason_EndWeek}, inplace=True)
    df_Capa_CustReason[custReason_EndWeek] = df_Capa_CustReason[constGrp_Enddate]
    
    print_df(df_Capa_CustReason, 'df_Capa_CustReason',False)
    
    
    # Short Reason Measure 공통 칼럼 입력
    df_Main_MtrlRCA[subLocationSubLocation]       = df_Main_MtrlRCA[fromActivity1Activity1].str.split('_').str[1]
    df_Main_MtrlRCA[transModeTransMode]           = df_Main_MtrlRCA[fromActivity1Activity1].str.split('_').str[2]
    
    df_Main_MtrlRCA[shortReason_ProblemTypeo9]    = df_Main_MtrlRCA[fromRootCauseProblemType]
    df_Main_MtrlRCA[shortReason_ProblemTypeBY]    = df_Main_MtrlRCA[graph_Rca_Material] # capa 는 : W MP RCA Type OBO Capacity
    
    df_Main_MtrlRCA[shortReason_ShortCategory]    = ''
    df_Main_MtrlRCA[shortReason_ShortReason]      = ''
    df_Main_MtrlRCA[shortReason_ProblemCategory1] = ''
    df_Main_MtrlRCA[shortReason_ProblemCategory2] = ''
    df_Main_MtrlRCA[shortReason_ProblemOwner]     = ''
    df_Main_MtrlRCA[shortReason_ProblemRefUI]     = ''
    
    df_Main_MtrlRCA[shortReason_ProblemActivity1] = df_Main_MtrlRCA[fromActivity1Activity1]
    df_Main_MtrlRCA[shortReason_ProblemActivity2] = df_Main_MtrlRCA[fromActivity2Activity2]
    df_Main_MtrlRCA[shortReason_ProblemActivity3] = df_Main_MtrlRCA[fromActivity3Activity3]
    df_Main_MtrlRCA[shortReason_ProblemSite]      = df_Main_MtrlRCA[fromLocationLocation]
    df_Main_MtrlRCA[shortReason_ProblemItem]      = df_Main_MtrlRCA[fromItemItem]
    df_Main_MtrlRCA[shortReason_ProblemResource]  = '' #from.[Resource].[Resource] # 없음 확인필요
    df_Main_MtrlRCA[shortReason_ProblemBOD]       = '' #'(df_Main_MtrlRCA[fromActivity1Activity1] + df_Main_MtrlRCA[fromActivity2Activity2] + df_Main_MtrlRCA[fromActivity3Activity3])
    df_Main_MtrlRCA[shortReason_ProblemBOM]       = (df_Main_MtrlRCA[fromActivity1Activity1] +
                                                     df_Main_MtrlRCA[fromActivity2Activity2] +
                                                     df_Main_MtrlRCA[fromActivity3Activity3])
    df_Main_MtrlRCA[shortReason_ProblemWeek]      = df_Main_MtrlRCA[fromTimeWeek]
    df_Main_MtrlRCA[shortReason_ProblemQty]       = df_Main_MtrlRCA[graph_Material_Quantity].astype('int64') # capa 는 : W OBO Capacity Constraint Quantity
    df_Main_MtrlRCA[shortReason_ProblemNeedQty]   = '' # TBD
    
    print_df(df_Main_MtrlRCA, 'df_Main_MtrlRCA 2',False)
    step('=====> STEP 0-1 : Mtrl Data Preprocessing End')
    
    #--------------------------------------------------------------------------------------------------------------
    step('=====> STEP 0-2 : Capa Data Preprocessing')
    
    # Merge : df_in_Item
    df_Main_CapaRCA = df_Main_CapaRCA.merge(df_in_Item, left_on=[fromActivity3Activity3], right_on=[itemItem], 
                                            how='left')
    df_Main_CapaRCA.rename(columns={itemItem:fromItemItem, itemItemStage:fromItemItemStage}, inplace=True) # Mtrl 과 칼럼명 같게하기 위해 변경
    del df_in_Item
    
    # Short Reason Measure 공통 칼럼 입력
    df_Main_CapaRCA[subLocationSubLocation]    = df_Main_CapaRCA[fromActivity1Activity1].str.split('_').str[1]
    df_Main_CapaRCA[transModeTransMode]        = df_Main_CapaRCA[fromActivity1Activity1].str.split('_').str[2]
    
    df_Main_CapaRCA[shortReason_ProblemTypeo9] = df_Main_CapaRCA[fromRootCauseProblemType]
    df_Main_CapaRCA[shortReason_ProblemTypeBY] = df_Main_CapaRCA[graph_Rca_Capacity]  # capa 는 : W MP RCA Type OBO Capacity
    
    df_Main_CapaRCA[shortReason_ShortCategory]    = ''
    df_Main_CapaRCA[shortReason_ShortReason]      = ''
    df_Main_CapaRCA[shortReason_ProblemCategory1] = ''
    df_Main_CapaRCA[shortReason_ProblemCategory2] = ''
    df_Main_CapaRCA[shortReason_ProblemOwner]     = ''
    df_Main_CapaRCA[shortReason_ProblemRefUI]     = ''
    
    df_Main_CapaRCA[shortReason_ProblemActivity1] = df_Main_CapaRCA[fromActivity1Activity1]
    df_Main_CapaRCA[shortReason_ProblemActivity2] = df_Main_CapaRCA[fromActivity2Activity2]
    df_Main_CapaRCA[shortReason_ProblemActivity3] = df_Main_CapaRCA[fromActivity3Activity3]
    df_Main_CapaRCA[shortReason_ProblemSite]      = df_Main_CapaRCA[fromLocationLocation]
    df_Main_CapaRCA[shortReason_ProblemItem]      = df_Main_CapaRCA[fromActivity3Activity3] # Item
    df_Main_CapaRCA[shortReason_ProblemResource]  = df_Main_CapaRCA[fromResourceResource]
    df_Main_CapaRCA[shortReason_ProblemBOD]       = (df_Main_CapaRCA[fromActivity1Activity1] +
                                                   df_Main_CapaRCA[fromActivity2Activity2] +
                                                   df_Main_CapaRCA[fromActivity3Activity3])
    df_Main_CapaRCA[shortReason_ProblemBOM]       = '' #(df_Main_CapaRCA[fromActivity1Activity1] + df_Main_CapaRCA[fromActivity2Activity2] + df_Main_CapaRCA[fromActivity3Activity3])
    df_Main_CapaRCA[shortReason_ProblemWeek]      = df_Main_CapaRCA[fromTimeWeek]
    df_Main_CapaRCA[shortReason_ProblemQty]       = df_Main_CapaRCA[graph_Capacity_Quantity].astype('int64')  # capa 는 : W OBO Capacity Constraint Quantity
    df_Main_CapaRCA[shortReason_ProblemNeedQty]   = ''  # TBD
    
    print_df(df_Main_CapaRCA, 'df_Main_CapaRCA 2',False)
    step('=====> STEP 0-3 : Capa Data Preprocessing End')
    
    ################################################################################################################
    # STEP 1 : MaterialShort &  & not in ['SET','LCM']  Data 생성
    ################################################################################################################
    step('=====> STEP 1 : MaterialShort Data create')
    
    # MaterialShort 추출
    df_MtrlShort = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromRootCauseProblemType] == 'MaterialShort') &
                                     (~df_Main_MtrlRCA[fromItemItemStage].isin(['SET','LCM','PAC'])) ].copy()
    df_MtrlShort[problemTypeProblemReason]  = 'MTRL_' + df_MtrlShort[fromItemItemStage]
    
    # Problem Type (df_in_ProblemType) Merge 
    df_MtrlShort = df_MtrlShort.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
        
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_MtrlShort[shortReason_ShortCategory]    = df_MtrlShort[problemTypeShortCategory]
    df_MtrlShort[shortReason_ShortReason]      = df_MtrlShort[problemTypeShortReason]
    df_MtrlShort[shortReason_ProblemCategory1] = df_MtrlShort[problemTypeProblemCategory1]
    df_MtrlShort[shortReason_ProblemCategory2] = df_MtrlShort[problemTypeProblemCategory2]
    #df_MtrlShort[shortReason_ProblemOwner]     = df_MtrlShort[problemTypeProblemOwner] # Dimemsion Attribute 없음
    #df_MtrlShort[shortReason_ProblemRefUI]     = df_MtrlShort[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
        
    #print_df(df_MtrlShort, 'df_MtrlShort Merge1',False)
    #df_MtrlShort[shortReason_ProblemReason] = df_MtrlShort[problemTypeProblemReason] #메저 없음.
    
    # Merge : df_in_IvnNodeParam 
    df_in_IvnNodeParam.rename( columns={itemItem: fromItemItem, locationLocation:  fromLocationLocation}, inplace=True)
    df_MtrlShort = df_MtrlShort.merge(df_in_IvnNodeParam, on=[versionVersionName,fromItemItem,fromLocationLocation], 
                                      how='left')
    
    df_MtrlShort[shortReason_ProblemFactor] = 'Mtrl Finite Period'
    df_MtrlShort[shortReason_ProblemValue1]  = df_MtrlShort[wFinitePeriod]
    df_MtrlShort[shortReason_ProblemValue2] = ''
    df_MtrlShort[shortReason_ProblemValue3] = 'STEP-1 MaterialShort'
    
    #칼럼 List
    cList_A = [versionVersionName, toDemandDemandID, toItemItem, toLocationLocation, toSalesDomainCustomerGroup, 
               toTimeWeek, problemTypeProblemReason, shortReason_ProblemTypeo9, shortReason_ProblemTypeBY, 
               shortReason_ShortCategory, shortReason_ShortReason, shortReason_ProblemCategory1, 
               shortReason_ProblemCategory2, #shortReason_ProblemReason, #메저 없음.
               shortReason_ProblemActivity1, shortReason_ProblemActivity2, shortReason_ProblemActivity3,
               shortReason_ProblemSite, shortReason_ProblemItem, shortReason_ProblemResource, shortReason_ProblemBOD, 
               shortReason_ProblemBOM, shortReason_ProblemWeek, shortReason_ProblemFactor, shortReason_ProblemValue1, 
               shortReason_ProblemValue2, shortReason_ProblemValue3, shortReason_ProblemQty, shortReason_ProblemNeedQty, 
               shortReason_ProblemOwner, shortReason_ProblemRefUI, fromItemItemStage]
    
    #칼럼 정리
    df_MtrlShort = df_MtrlShort[cList_A].copy()
    
    df_MtrlShort.drop_duplicates(inplace=True)
    
    print_df(df_MtrlShort, 'df_MtrlShort',False)
    step('=====> STEP 1-1 : MaterialShort Data create End')
    
    ################################################################################################################
    # STEP 2 : [Version Type] = 'MP Sync Plan'  &  [Problem Type] = 'FrozenPeriod' & [Item Stage] = 'SET' (SKU --> SET, 2025.02.03)
    ################################################################################################################
    # FrozenPeriod & SET 추출
    step('=====> STEP 2 : FrozenPeriod & SET Data create')
    
    df_MSPFrznPridSET = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[versionVersionType] == 'MP Sync Plan') & 
                                            (df_Main_MtrlRCA[fromRootCauseProblemType] == 'FrozenPeriod') & 
                                            (df_Main_MtrlRCA[fromItemItemStage] == 'SET')].copy()
        
    # Merge : df_in_SOPAdjSTBMVrsW 
    df_in_SOPAdjSTBMVrsW.rename(columns={itemItem:fromItemItem,
                                         timeWeek:fromTimeWeek,
                                         locationLocation: fromLocationLocation}, inplace=True) 
    
    # Measure.[SOP Adjust SET BOM Version W_Chg Reason] ==> Measure.[SOP Adjust SET W_Chg Reason]  : 변경확인필요
    df_MSPFrznPridSET = df_MSPFrznPridSET.merge(df_in_SOPAdjSTBMVrsW, 
                                                on=[versionVersionName, fromItemItem, fromTimeWeek,
                                                   fromLocationLocation, subLocationSubLocation, transModeTransMode],
                                                how='left') #BOM Info.[BOM Version] 조인 조건 확일필요
    del df_in_SOPAdjSTBMVrsW
    
    df_MSPFrznPridSET[problemTypeProblemReason] = np.select([(df_MSPFrznPridSET[sOPAdjustSETW_ChgReason].isna()), 
                                                             True, ],
                                                            ['SET SOP Released', 
                                                             ('SET_SOP_ADJUST_' + 
                                                              df_MSPFrznPridSET[sOPAdjustSETW_ChgReason])])
    
    #df_MSPFrznPridSET[shortReason_ProblemReason] = df_MSPFrznPridSET[problemTypeProblemReason] #메저 없음.
    
    # Problem Type (df_in_ProblemType) Merge 
    df_MSPFrznPridSET = df_MSPFrznPridSET.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_MSPFrznPridSET[shortReason_ShortCategory]    = df_MSPFrznPridSET[problemTypeShortCategory]
    df_MSPFrznPridSET[shortReason_ShortReason]      = df_MSPFrznPridSET[problemTypeShortReason]
    df_MSPFrznPridSET[shortReason_ProblemCategory1] = df_MSPFrznPridSET[problemTypeProblemCategory1]
    df_MSPFrznPridSET[shortReason_ProblemCategory2] = df_MSPFrznPridSET[problemTypeProblemCategory2]
    # df_MSPFrznPridSET[shortReason_ProblemOwner]     = df_MSPFrznPridSET[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_MSPFrznPridSET[shortReason_ProblemRefUI]     = df_MSPFrznPridSET[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
        
    df_MSPFrznPridSET[shortReason_ProblemFactor] = 'SOP Adj Reason'
    df_MSPFrznPridSET[shortReason_ProblemValue1] = df_MSPFrznPridSET[sOPAdjustSETW_ChgReason]  #df_MSPFrznPridSET[sOPAdjustSETBOMVersionW_ChgReason]
    df_MSPFrznPridSET[shortReason_ProblemValue2] = ''
    df_MSPFrznPridSET[shortReason_ProblemValue3] = 'STEP-2 (MP Sync Plan)&FrozenPeriod'
    
    # 칼럼 정리
    df_MSPFrznPridSET = df_MSPFrznPridSET[cList_A].copy()
    
    df_MSPFrznPridSET.drop_duplicates(inplace=True)
    print_df(df_MSPFrznPridSET, 'df_MSPFrznPridSET',False)
    step('=====> STEP 2-1 : FrozenPeriod & SET Data create End')
    ################################################################################################################
    # STEP 3 : [Version Type] != 'MP Sync Plan'  &  [Problem Type] = 'FrozenPeriod'
    ################################################################################################################
    step('=====> STEP 3 : Not(MP Sync Plan) & FrozenPeriod Data create')
    
    # Not(MP Sync Plan) & FrozenPeriod 추출
    df_NMSPlnFrznPrid = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[versionVersionType] != 'MP Sync Plan') &
                                             (df_Main_MtrlRCA[fromRootCauseProblemType] == 'FrozenPeriod')].copy()
    
    df_NMSPlnFrznPrid[problemTypeProblemReason] = np.select([(df_NMSPlnFrznPrid[toDemandTypeDemandType].isin(
                                                                  ['NEW_BUFF','NEW_FCST','NEW_ORD','UNF_ORD'])), True,],
                                                            ['SET_SOP_REL_NEW', 
                                                             (df_NMSPlnFrznPrid[fromItemItemStage] + '_SOP_REL')])
    
    #df_NMSPlnFrznPrid[shortReason_ProblemReason] = df_NMSPlnFrznPrid[problemTypeProblemReason] #메저 없음.
    
    # Problem Type (df_in_ProblemType) Merge 
    df_NMSPlnFrznPrid = df_NMSPlnFrznPrid.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_NMSPlnFrznPrid[shortReason_ShortCategory]    = df_NMSPlnFrznPrid[problemTypeShortCategory]
    df_NMSPlnFrznPrid[shortReason_ShortReason]      = df_NMSPlnFrznPrid[problemTypeShortReason]
    df_NMSPlnFrznPrid[shortReason_ProblemCategory1] = df_NMSPlnFrznPrid[problemTypeProblemCategory1]
    df_NMSPlnFrznPrid[shortReason_ProblemCategory2] = df_NMSPlnFrznPrid[problemTypeProblemCategory2]
    # df_NMSPlnFrznPrid[shortReason_ProblemOwner]     = df_NMSPlnFrznPrid[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_NMSPlnFrznPrid[shortReason_ProblemRefUI]     = df_NMSPlnFrznPrid[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    # Merge : df_in_IvnNodeParam 
    # df_in_IvnNodeParam.rename(columns={itemItem: fromItemItem, locationLocation: fromLocationLocation}, inplace=True) #위에서처리
    df_NMSPlnFrznPrid = df_NMSPlnFrznPrid.merge(df_in_IvnNodeParam, on=[versionVersionName, fromItemItem, 
                                                                        fromLocationLocation], how='left')
    
    df_NMSPlnFrznPrid[shortReason_ProblemFactor] = 'Mtrl Finite Period'
    df_NMSPlnFrznPrid[shortReason_ProblemValue1] = df_NMSPlnFrznPrid[wFinitePeriod]
    df_NMSPlnFrznPrid[shortReason_ProblemValue2] = '' 
    df_NMSPlnFrznPrid[shortReason_ProblemValue3] = 'STEP-3 Not(MP Sync Plan)&FrozenPeriod'  
    
    # 칼럼 정리
    df_NMSPlnFrznPrid = df_NMSPlnFrznPrid[cList_A].copy()
    
    df_NMSPlnFrznPrid.drop_duplicates(inplace=True)
    
    print_df(df_NMSPlnFrznPrid, 'df_NMSPlnFrznPrid',False)
    step('=====> STEP 3-1 : Not(MP Sync Plan) & FrozenPeriod Data create End')
    ################################################################################################################
    # STEP 4 : [Problem Type] = 'Effectiveness' & in ['MF_KD','MF_LCM_EX','MF_LCM','MF','MF_SET'] & in ['SET','LCM']
    #          [Problem Type] IN ('MaterialShort', 'ActivityNotAvailable') & not in ['MF_KD','MF_LCM_EX','MF_LCM','MF','MF_SET'] & in ['SET','LCM']
    ################################################################################################################
    step('=====> STEP 4 : Effectiveness Data create')
    
    # BOM_EFFECTIVE 추출
    df_BOM_Effective = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromRootCauseProblemType] == 'Effectiveness') &
                                         (df_Main_MtrlRCA[fromLocationSiteStage].isin(
                                             ['MF_KD','MF_LCM_EX','MF_LCM','MF','MF_SET'])) &
                                         (df_Main_MtrlRCA[fromItemItemStage].isin(['SET','LCM']))].copy()
    
    df_BOM_Effective[problemTypeProblemReason] = 'BOM_EFFECTIVE_' + df_BOM_Effective[fromItemItemStage]
    
    # BOD_EFFECTIVE 추출
    # 'Effectiveness' 추가(20250210)
    df_BOD_Effective = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromRootCauseProblemType].isin(
                                                           ['MaterialShort','ActivityNotAvailable','Effectiveness'])) &
                                         (~df_Main_MtrlRCA[fromLocationSiteStage].isin(
                                                                       ['MF_KD','MF_LCM_EX','MF_LCM','MF','MF_SET'])) &
                                         (df_Main_MtrlRCA[fromItemItemStage].isin(['SET','LCM']))].copy()
    
    df_BOD_Effective[problemTypeProblemReason] = 'BOD_EFFECTIVE_' + df_BOD_Effective[fromItemItemStage]
    
    df_Effectiveness = pd.concat([df_BOM_Effective, df_BOD_Effective])
    del [df_BOM_Effective, df_BOD_Effective]
    
    # Problem Type (df_in_ProblemType) Merge 
    df_Effectiveness = df_Effectiveness.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_Effectiveness[shortReason_ShortCategory]    = df_Effectiveness[problemTypeShortCategory]
    df_Effectiveness[shortReason_ShortReason]      = df_Effectiveness[problemTypeShortReason]
    df_Effectiveness[shortReason_ProblemCategory1] = df_Effectiveness[problemTypeProblemCategory1]
    df_Effectiveness[shortReason_ProblemCategory2] = df_Effectiveness[problemTypeProblemCategory2]
    # df_Effectiveness[shortReason_ProblemOwner]     = df_Effectiveness[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_Effectiveness[shortReason_ProblemRefUI]     = df_Effectiveness[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    # Merge : df_in_ActParam 
    df_Effectiveness = df_Effectiveness.merge(df_in_ActParam, 
                                              on=[versionVersionName, fromActivity1Activity1, fromActivity2Activity2, 
                                                  fromActivity3Activity3], how='left')    
    
    # Merge : df_in_IvnNodeParam 
    df_Effectiveness = df_Effectiveness.merge(df_in_IvnNodeParam, 
                                              on=[versionVersionName, fromItemItem, fromLocationLocation], how='left')
    
    #Problem Value1 = W Active Start Date (from.[Item].[Item], from.[Location].[Location]) # W Active Start Date 메저 없음  W Activity Start Date 사용, df_in_ActParam
    #Problem Value2 = W Finite Period (from.[Item].[Item], from.[Location].[Location]) # df_in_IvnNodeParam
    
    df_Effectiveness[shortReason_ProblemFactor] = 'BOM/BOD Effective'
    df_Effectiveness[shortReason_ProblemValue1] = df_Effectiveness[wActivityStartDate].dt.strftime("%Y-%m-%d") # W Active Start Date 메저없음.  W Activity Start Date 사용
    df_Effectiveness[shortReason_ProblemValue2] = df_Effectiveness[wFinitePeriod].astype('str')
    df_Effectiveness[shortReason_ProblemValue3] = 'STEP-4 BOM/BOD Effective'
    
    # 칼럼 정리
    df_Effectiveness = df_Effectiveness[cList_A].copy()
    
    df_Effectiveness.drop_duplicates(inplace=True)
    
    print_df(df_Effectiveness, 'df_Effectiveness',False)
    step('=====> STEP 4-1 : Effectiveness Data create End')
    ################################################################################################################
    # STEP 5 : 
    # NO_BOM : IN ('MaterialShort', 'ActivityNotAvailable') & in ('MF_KD', 'MF_LCM_EX', 'MF_LCM', 'MF', 'MF_SET') & in ('SET', 'LCM') & Item Attr Ref_Resolution != 'N' 
    # NO_BOD : IN ('MaterialShort', 'ActivityNotAvailable') & NOT in ('MF_KD', 'MF_LCM_EX', 'MF_LCM', 'MF', 'MF_SET') & in ('SET', 'LCM') & Item Attr Ref_Resolution != 'N' 
    # NO_REGULATION : IN ('MaterialShort', 'ActivityNotAvailable') & in ('SET', 'LCM') & Item Attr Ref_Resolution = 'N'
    ################################################################################################################
    step('=====> STEP 5 : NoBOM & Ref_Resolution Y Data create')
    
    # NO_BOM : IN ('MaterialShort', 'ActivityNotAvailable') & 
    # in ('MF_KD', 'MF_LCM_EX', 'MF_LCM', 'MF', 'MF_SET') & 
    # in ('SET', 'LCM') & 
    # Item Attr Ref_Resolution != 'N' (null, - 이런거 다 포함) 추출
    df_NO_BOM = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromRootCauseProblemType].isin(
                                                                           ['MaterialShort','ActivityNotAvailable'])) &
                                  (df_Main_MtrlRCA[fromLocationSiteStage].isin(
                                                                       ['MF_KD','MF_LCM_EX','MF_LCM','MF','MF_SET'])) &
                                  (df_Main_MtrlRCA[fromItemItemStage].isin(['SET','LCM'])) &
                                  (df_Main_MtrlRCA[itemAttrRef_Resolution] != 'N')].copy()
    
    df_NO_BOM[problemTypeProblemReason] = 'NO_BOM_'  + df_NO_BOM[fromItemItemStage]
    
    # NO_BOD : IN ('MaterialShort', 'ActivityNotAvailable') & 
    # NOT in ('MF_KD', 'MF_LCM_EX', 'MF_LCM', 'MF', 'MF_SET') & 
    # in ('SET', 'LCM') & 
    # Item Attr Ref_Resolution != 'N' (null, - 이런거 다 포함)
    df_NO_BOD = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromRootCauseProblemType].isin(
                                                                         ['MaterialShort', 'ActivityNotAvailable'])) &
                                  (~df_Main_MtrlRCA[fromLocationSiteStage].isin(
                                                                    ['MF_KD', 'MF_LCM_EX', 'MF_LCM', 'MF', 'MF_SET'])) &
                                  (df_Main_MtrlRCA[fromItemItemStage].isin(['SET', 'LCM'])) &
                                  (df_Main_MtrlRCA[itemAttrRef_Resolution] != 'N')].copy()
    
    df_NO_BOD[problemTypeProblemReason] = 'NO_BOD_' + df_NO_BOD[fromItemItemStage]
    
    # NO_REGULATION : IN ('MaterialShort', 'ActivityNotAvailable') & 
    # in ('SET', 'LCM') & 
    # Item Attr Ref_Resolution = 'N'
    df_NO_REGULATION = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromRootCauseProblemType].isin(
                                                                        ['MaterialShort', 'ActivityNotAvailable'])) &
                                         (df_Main_MtrlRCA[fromItemItemStage].isin(['SET', 'LCM'])) &
                                         (df_Main_MtrlRCA[itemAttrRef_Resolution] == 'N')].copy()
    
    df_NO_REGULATION[problemTypeProblemReason] = 'NO_REGULATION'
    
    df_NO_BOM_BOD_REGULATION = pd.concat([df_NO_BOM, df_NO_BOD, df_NO_REGULATION])
    del [df_NO_BOM, df_NO_BOD, df_NO_REGULATION]
    
    # Problem Type (df_in_ProblemType) Merge 
    df_NO_BOM_BOD_REGULATION = df_NO_BOM_BOD_REGULATION.merge(df_in_ProblemType, on=[problemTypeProblemReason], 
                                                              how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_NO_BOM_BOD_REGULATION[shortReason_ShortCategory]    = df_NO_BOM_BOD_REGULATION[problemTypeShortCategory]
    df_NO_BOM_BOD_REGULATION[shortReason_ShortReason]      = df_NO_BOM_BOD_REGULATION[problemTypeShortReason]
    df_NO_BOM_BOD_REGULATION[shortReason_ProblemCategory1] = df_NO_BOM_BOD_REGULATION[problemTypeProblemCategory1]
    df_NO_BOM_BOD_REGULATION[shortReason_ProblemCategory2] = df_NO_BOM_BOD_REGULATION[problemTypeProblemCategory2]
    # df_NO_BOM_BOD_REGULATION[shortReason_ProblemOwner]   = df_NO_BOM_BOD_REGULATION[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_NO_BOM_BOD_REGULATION[shortReason_ProblemRefUI]   = df_NO_BOM_BOD_REGULATION[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_NO_BOM_BOD_REGULATION[shortReason_ProblemFactor] = 'Produced Item'
    df_NO_BOM_BOD_REGULATION[shortReason_ProblemValue1] = df_NO_BOM_BOD_REGULATION[fromItemItem]
    df_NO_BOM_BOD_REGULATION[shortReason_ProblemValue2] = ''  
    df_NO_BOM_BOD_REGULATION[shortReason_ProblemValue3] = 'STEP-5 NO_BOM_BOD_REGULATION'  
    
    # 칼럼 정리
    df_NO_BOM_BOD_REGULATION = df_NO_BOM_BOD_REGULATION[cList_A].copy()
    
    df_NO_BOM_BOD_REGULATION.drop_duplicates(inplace=True)
    
    print_df(df_NO_BOM_BOD_REGULATION, 'df_NO_BOM_BOD_REGULATION',False)
    step('=====> STEP 5-1 : NoBOM & Ref_Resolution Y Data create End')
    ################################################################################################################
    # STEP 6 : [Problem Type] = 'LeadtimePlanBeforeCurrent' & in ('NEW BUFF', 'NEW_FCST', 'NEW_ORD', 'UNF_ORD')
    ################################################################################################################
    step('=====> STEP 6 : NoBOM & Ref_Resolution N Data create')
    
    # LeadtimePlanBeforeCurrent 추출
    df_Leadtime = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromRootCauseProblemType] == 'LeadtimePlanBeforeCurrent')].copy()
    
    df_Leadtime[problemTypeProblemReason] = np.select([(df_Leadtime[toDemandTypeDemandType].isin(
                                                            ['NEW_BUFF', 'NEW_FCST', 'NEW_ORD', 'UNF_ORD'])), True, ],
                                                      ['PBC_SET_NEW', ('PBC_' + df_Leadtime[fromItemItemStage])])
    
    # Problem Type (df_in_ProblemType) Merge 
    df_Leadtime = df_Leadtime.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_Leadtime[shortReason_ShortCategory]    = df_Leadtime[problemTypeShortCategory]
    df_Leadtime[shortReason_ShortReason]      = df_Leadtime[problemTypeShortReason]
    df_Leadtime[shortReason_ProblemCategory1] = df_Leadtime[problemTypeProblemCategory1]
    df_Leadtime[shortReason_ProblemCategory2] = df_Leadtime[problemTypeProblemCategory2]
    # df_Leadtime[shortReason_ProblemOwner]   = df_Leadtime[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_Leadtime[shortReason_ProblemRefUI]   = df_Leadtime[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    # Merge : df_in_ActParam 
    df_Leadtime = df_Leadtime.merge(df_in_ActParam, on=[versionVersionName, fromActivity1Activity1, 
                                                        fromActivity2Activity2, fromActivity3Activity3], how='left')
    
    df_Leadtime[shortReason_ProblemFactor] = 'Lead Time'
    df_Leadtime[shortReason_ProblemValue1] = df_Leadtime[wActivityLeadTime]
    df_Leadtime[shortReason_ProblemValue2] = ''
    df_Leadtime[shortReason_ProblemValue3] = 'STEP-6 Lead Time'

    # 칼럼 정리
    df_Leadtime = df_Leadtime[cList_A].copy()
    
    df_Leadtime.drop_duplicates(inplace=True)
    
    print_df(df_Leadtime, 'df_Leadtime',False)
    
    step('=====> STEP 6-1 : NoBOM & Ref_Resolution N Data create End')
    ################################################################################################################
    # STEP 7 : [Problem Type] = 'CapacityShort'
    ################################################################################################################
    step('=====> STEP 7 : CapacityShort Data create')
    
    # CapacityShort 추출
    # 'RegularCapacityShort' 조건 추가(20250210)
    df_CapaShort = df_Main_CapaRCA.loc[
                     df_Main_CapaRCA[fromRootCauseProblemType].isin(['CapacityShort','RegularCapacityShort'])].copy()
    #df_CapaShort["Resource_Prefix"] = df_Main_CapaRCA[fromResourceResource].str.slice(start=0, stop=3) #Resource.[Resource Type]을 기준 사용으로 변경
    
    #Resource.[Resource Type] : SRC --> BOD(GRP), MFC --> MFG(GRP), MLC --> MFG(LINE), SCT --> BOD(CTN), MCT --> MFG(CTN), SEC --> BOD(EOL), MEC --> MFG(EOL), 없으면 그대로
    df_CapaShort[problemTypeProblemReason] = (
        np.where((df_CapaShort[col_ResourceType] == 'MFT'),
                 'SOP_FIX',
                 df_CapaShort[fromItemItemStage] + '_' +         
                     np.select([(df_CapaShort[col_ResourceType] == 'SRC'), (df_CapaShort[col_ResourceType] == 'MFC'), 
                                (df_CapaShort[col_ResourceType] == 'MLC'), (df_CapaShort[col_ResourceType] == 'SCT'), 
                                (df_CapaShort[col_ResourceType] == 'MCT'), (df_CapaShort[col_ResourceType] == 'SEC'), 
                                (df_CapaShort[col_ResourceType] == 'MEC'), 
                                True],
                               [ 'BOD(GRP)',                               'MFG(GRP)',
                                 'MFG(LINE)',                              'BOD(CTN)',
                                 'MFG(CTN)',                               'BOD(EOL)',
                                 'MFG(EOL)',                               
                                 'UNKNOWN'])
                   + '_CAPA')
    )
    
    # Problem Type (df_in_ProblemType) Merge 
    df_CapaShort = df_CapaShort.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_CapaShort[shortReason_ShortCategory]    = df_CapaShort[problemTypeShortCategory]
    df_CapaShort[shortReason_ShortReason]      = df_CapaShort[problemTypeShortReason]
    df_CapaShort[shortReason_ProblemCategory1] = df_CapaShort[problemTypeProblemCategory1]
    df_CapaShort[shortReason_ProblemCategory2] = df_CapaShort[problemTypeProblemCategory2]
    # df_CapaShort[shortReason_ProblemOwner]   = df_CapaShort[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_CapaShort[shortReason_ProblemRefUI]   = df_CapaShort[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    # Merge : df_in_WCapacity : 'W Flex Capacity Band3' # Measure 없음 확인필요
    df_in_WCapacity.rename(columns={resourceResource:fromResourceResource, locationLocation:fromLocationLocation, 
                                    timeWeek:fromTimeWeek}, inplace=True)
    df_CapaShort = df_CapaShort.merge(df_in_WCapacity, on=[versionVersionName, fromResourceResource, 
                                                           fromLocationLocation, fromTimeWeek], how='left')
    del df_in_WCapacity
    
    df_CapaShort[shortReason_ProblemFactor] = 'Capacity'
    df_CapaShort[shortReason_ProblemValue1] = (df_CapaShort[wResourceBaseCapacity] + 
                                               df_CapaShort[wFlexCapacityBand1] +
                                               df_CapaShort[wFlexCapacityBand2]).astype('str')
                                               # df_CapaShort[wFlexCapacityBand3] 'W Flex Capacity Band3' # Measure 없음 확인필요
                                               
    df_CapaShort[shortReason_ProblemValue2] = ''
    df_CapaShort[shortReason_ProblemValue3] = 'STEP-7 CapacityShort'
    
    # 칼럼 정리
    df_CapaShort = df_CapaShort[cList_A].copy()
    
    df_CapaShort.drop_duplicates(inplace=True)
    print_df(df_CapaShort, 'df_CapaShort',False)
    
    step('=====> STEP 7-1 : CapacityShort Data create End')    

    ################################################################################################################
    # STEP 8-1 : RCA_Mtrl : CustReason
    ################################################################################################################
    step('=====> STEP 8-1 : RCA_Mtrl : CustReason Data create')
    
    # RCA_Mtrl CustReason 추출
    df_RCAMtrlCustReason = df_Main_MtrlRCA.loc[(df_Main_MtrlRCA[fromItemItemStage] == 'PAC')].copy()
    
    df_in_Mtrl_CustReason.rename(columns={groupGroupID:fromItemItem}, inplace=True)
    
    # Merge : df_RCAMtrlCustReason & df_in_Mtrl_CustReason
    df_RCAMtrlCustReason = df_RCAMtrlCustReason.merge(df_in_Mtrl_CustReason, 
                                                      on=[versionVersionName, fromItemItem], how='left')
    del df_in_Mtrl_CustReason
    df_RCAMtrlCustReason[problemTypeProblemReason] = np.where(df_RCAMtrlCustReason[preAllocConst_Grp2].isna(),
                                                              "PAC_ETC_ETC",
                                                              df_RCAMtrlCustReason[preAllocConst_Grp2])
    
    # Problem Type (df_in_ProblemType) Merge 
    df_RCAMtrlCustReason = df_RCAMtrlCustReason.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_RCAMtrlCustReason[shortReason_ShortCategory]    = df_RCAMtrlCustReason[problemTypeShortCategory]
    df_RCAMtrlCustReason[shortReason_ShortReason]      = df_RCAMtrlCustReason[problemTypeShortReason]
    df_RCAMtrlCustReason[shortReason_ProblemCategory1] = df_RCAMtrlCustReason[problemTypeProblemCategory1]
    df_RCAMtrlCustReason[shortReason_ProblemCategory2] = df_RCAMtrlCustReason[problemTypeProblemCategory2]
    # df_RCAMtrlCustReason[shortReason_ProblemOwner]   = df_RCAMtrlCustReason[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_RCAMtrlCustReason[shortReason_ProblemRefUI]   = df_RCAMtrlCustReason[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_RCAMtrlCustReason[shortReason_ProblemFactor] = 'Mtrl Pre Alloc'
    df_RCAMtrlCustReason[shortReason_ProblemValue1] = '-'
    df_RCAMtrlCustReason[shortReason_ProblemValue2] = ''
    df_RCAMtrlCustReason[shortReason_ProblemValue3] = 'STEP 8-1 RCA_Mtrl CustReason'
    
    # 칼럼 정리
    df_RCAMtrlCustReason = df_RCAMtrlCustReason[cList_A].copy()
    
    df_RCAMtrlCustReason.drop_duplicates(inplace=True)
    
    print_df(df_RCAMtrlCustReason, 'df_RCAMtrlCustReason',False)
    step('=====> STEP 8-1 : RCA_Mtrl : CustReason Data create End')
    
    ################################################################################################################
    # STEP 8-2 : RCA_CAPA : CustReason
    ################################################################################################################    
    step('=====> STEP 8-2 : RCA_CAPA : CustReason Data create')
    
    df_Capa_CustReason.rename(columns={groupGroupID: fromResourceResource}, inplace=True)
    
    # RCA_CAPA CustReason 추출
    df_RCACapaCustReason = df_Main_CapaRCA.loc[(df_Main_CapaRCA[col_ResourceType] == 'MFC')].copy()
    #print_df(df_RCACapaCustReason, 'df_RCACapaCustReason 1',False)
    
    # Merge : df_RCAMtrlCustReason & df_Capa_CustReason
    df_RCACapaCustReason = df_RCACapaCustReason.merge(df_Capa_CustReason, 
                                                      on=[versionVersionName, fromResourceResource], how='left')
    del df_Capa_CustReason
    #print_df(df_RCACapaCustReason, 'df_RCACapaCustReason 2', False)
    
    # CustReason_StartWeek, CustReason_EndWeek : FROM.[Time].[Week] 와 비교
    # FROM.[Time].[Week] >= CustReason_StartWeek & FROM.[Time].[Week] <= CustReason_EndWeek
    df_RCACapaCustReason['Week_Check'] = np.where(df_RCACapaCustReason[constGrp_Reason].notna() &
                                                  ((df_RCACapaCustReason[fromTimeWeek] >= df_RCACapaCustReason[custReason_StartWeek]) &
                                                   (df_RCACapaCustReason[fromTimeWeek] <= df_RCACapaCustReason[custReason_EndWeek])),
                                                  1,2)
    
    #print_df(df_RCACapaCustReason, 'df_RCACapaCustReason 3', True)
    # rank 구하기
    cList_group = [versionVersionName, fromResourceResource, col_ResourceType, fromActivity1Activity1, fromActivity3Activity3, 
                  fromActivity2Activity2, fromRootCauseProblemType, fromTimeWeek, fromLocationLocation, toDemandTypeDemandType, 
                  toSalesDomainCustomerGroup, toItemItem, toDemandDemandID, toLocationLocation, toTimeWeek]
    cList_sort = cList_group + ['Week_Check', sequenceSequence]
    
    # 정렬 후 rank 생성 : constGrp_Reason 값이 있고, 주차 조건이 만족 하는 것이 2건 이상이면 Sequence 빠른것 선택
    df_RCACapaCustReason.sort_values(by=cList_sort, ascending=[True, True, True, True, True,
                                                               True, True, True, True, True,
                                                               True, True, True, True, True,
                                                               True, True
                                                              ], axis=0, inplace=True)
    df_RCACapaCustReason['rank'] = 1
    df_RCACapaCustReason['rank'] = df_RCACapaCustReason.groupby(cList_group)['rank'].cumsum()
    #print_df(df_RCACapaCustReason, 'df_RCACapaCustReason 4', True)
    
    # rank == 1 인 경우만 선택(중복제거)
    df_RCACapaCustReason = df_RCACapaCustReason[df_RCACapaCustReason['rank'] == 1]
    
    df_RCACapaCustReason[problemTypeProblemReason] = np.where(df_RCACapaCustReason[constGrp_Reason].notna() &
                                                              (df_RCACapaCustReason['Week_Check'] == 1), # 날짜 조건이 맞은경우
                                                              df_RCACapaCustReason[constGrp_Reason],
                                                              "PC_ETC")
    
    #print_df(df_RCACapaCustReason, 'df_RCACapaCustReason 2',False)
    
    # Problem Type (df_in_ProblemType) Merge 
    df_RCACapaCustReason = df_RCACapaCustReason.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_RCACapaCustReason[shortReason_ShortCategory] = df_RCACapaCustReason[problemTypeShortCategory]
    df_RCACapaCustReason[shortReason_ShortReason] = df_RCACapaCustReason[problemTypeShortReason]
    df_RCACapaCustReason[shortReason_ProblemCategory1] = df_RCACapaCustReason[problemTypeProblemCategory1]
    df_RCACapaCustReason[shortReason_ProblemCategory2] = df_RCACapaCustReason[problemTypeProblemCategory2]
    # df_RCACapaCustReason[shortReason_ProblemOwner]   = df_RCACapaCustReason[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_RCACapaCustReason[shortReason_ProblemRefUI]   = df_RCACapaCustReason[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_RCACapaCustReason[shortReason_ProblemFactor] = 'Capacity Pre Alloc'
    df_RCACapaCustReason[shortReason_ProblemValue1] = '-'
    df_RCACapaCustReason[shortReason_ProblemValue2] = ''
    df_RCACapaCustReason[shortReason_ProblemValue3] = 'STEP 8-2 RCA_CAPA CustReason'
    
    # 칼럼 정리
    df_RCACapaCustReason = df_RCACapaCustReason[cList_A].copy()
    
    df_RCACapaCustReason.drop_duplicates(inplace=True)
    
    print_df(df_RCACapaCustReason, 'df_RCACapaCustReason',False)
    step('=====> STEP 8-2 : RCA_CAPA : CustReason Data create End')
    
    ################################################################################################################
    # STEP 100 : NoMatch DATA : 추출되지 않은 DATA
    ################################################################################################################
    step('=====> STEP 100 : NoMatch Data create')
    df_BOM_ShortReason = pd.concat([df_MtrlShort,
                                    df_MSPFrznPridSET,
                                    df_NMSPlnFrznPrid,
                                    df_Effectiveness,
                                    df_NO_BOM_BOD_REGULATION,
                                    df_Leadtime,
                                    df_RCAMtrlCustReason])
    del [df_MtrlShort, df_MSPFrznPridSET, df_NMSPlnFrznPrid, df_Effectiveness, df_NO_BOM_BOD_REGULATION, df_Leadtime, 
         df_RCAMtrlCustReason, df_in_IvnNodeParam]
    
    df_BOD_ShortReason = pd.concat([df_CapaShort, df_RCACapaCustReason])
    del [df_CapaShort, df_RCACapaCustReason]
    
    # NoMatch 조건 :  Version.[Version Name]
    #                 TO.[Demand].[DemandID]           ([Demand].[DemandID])
    #                 TO.[Time].[Week]                 [Time].[Week]
    #                 FROM.[RootCause].[Problem Type]  (Short Reason_Problem Type o9)
    #                 FROM.[Activity1].[Activity1]     (Short Reason_Problem Activity1)
    #                 FROM.[Activity2].[Activity2]     (Short Reason_Problem Activity2)
    #                 FROM.[Activity3].[Activity3]     (Short Reason_Problem Activity3)
    #                 FROM.[Location].[Location]       (Short Reason_Problem Site)
    #                 FROM.[Time].[Week]               (Short Reason_Problem Week)
    #
    #                 FROM.[Item].[Item]               (Short Reason_Problem Item),    : BOM
    #                 FROM.[Resource].[Resource]       (Short Reason_Problem Resource) : BOD
    
    # BOM ##########################################################################################################
    df_BOM_Match = df_BOM_ShortReason[[versionVersionName, toDemandDemandID, toTimeWeek, shortReason_ProblemTypeo9,
                                       shortReason_ProblemActivity1, shortReason_ProblemActivity2, shortReason_ProblemActivity3,
                                       shortReason_ProblemSite, shortReason_ProblemWeek, shortReason_ProblemItem]].copy()
    df_BOM_Match['Chk_Valeue'] = 1
    df_BOM_Match.drop_duplicates(inplace=True)
    print_df(df_BOM_Match, 'df_BOM_Match',False)    
    
    df_BOM_ShortReason_NoMatch = df_Main_MtrlRCA.merge(df_BOM_Match, 
                                                   on=[versionVersionName, toDemandDemandID, toTimeWeek, shortReason_ProblemTypeo9,
                                                       shortReason_ProblemActivity1, shortReason_ProblemActivity2, shortReason_ProblemActivity3,
                                                       shortReason_ProblemSite, shortReason_ProblemWeek, shortReason_ProblemItem],
                                                   how='left')
    del df_BOM_Match
    
    df_BOM_ShortReason_NoMatch = df_BOM_ShortReason_NoMatch.loc[df_BOM_ShortReason_NoMatch['Chk_Valeue'].isna()]
    
    df_BOM_ShortReason_NoMatch[problemTypeProblemReason] = 'NO_MATCH'
    
    # Problem Type (df_in_ProblemType) Merge 
    df_BOM_ShortReason_NoMatch = df_BOM_ShortReason_NoMatch.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_BOM_ShortReason_NoMatch[shortReason_ShortCategory]    = df_BOM_ShortReason_NoMatch[problemTypeShortCategory]
    df_BOM_ShortReason_NoMatch[shortReason_ShortReason]      = df_BOM_ShortReason_NoMatch[problemTypeShortReason]
    df_BOM_ShortReason_NoMatch[shortReason_ProblemCategory1] = df_BOM_ShortReason_NoMatch[problemTypeProblemCategory1]
    df_BOM_ShortReason_NoMatch[shortReason_ProblemCategory2] = df_BOM_ShortReason_NoMatch[problemTypeProblemCategory2]
    # df_BOM_ShortReason_NoMatch[shortReason_ProblemOwner]     = df_BOM_ShortReason_NoMatch[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_BOM_ShortReason_NoMatch[shortReason_ProblemRefUI]     = df_BOM_ShortReason_NoMatch[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_BOM_ShortReason_NoMatch[shortReason_ProblemFactor] = ''
    df_BOM_ShortReason_NoMatch[shortReason_ProblemValue1] = ''
    df_BOM_ShortReason_NoMatch[shortReason_ProblemValue2] = ''
    df_BOM_ShortReason_NoMatch[shortReason_ProblemValue3] = 'STEP-100 BOM NO_MATCH'
    
    # 칼럼 정리
    df_BOM_ShortReason_NoMatch = df_BOM_ShortReason_NoMatch[cList_A].copy()
    
    df_BOM_ShortReason_NoMatch.drop_duplicates(inplace=True)
        
    print_df(df_BOM_ShortReason_NoMatch, 'df_BOM_ShortReason_NoMatch',False)
    ################################################################################################################
    # BOD ##########################################################################################################
    df_BOD_Match = df_BOD_ShortReason[[versionVersionName, toDemandDemandID, toTimeWeek, shortReason_ProblemTypeo9,
                                       shortReason_ProblemActivity1, shortReason_ProblemActivity2,
                                       shortReason_ProblemActivity3,
                                       shortReason_ProblemSite, shortReason_ProblemWeek,
                                       shortReason_ProblemResource]].copy()
    
    df_BOD_Match['Chk_Valeue'] = 1
    df_BOD_Match.drop_duplicates(inplace=True)
    print_df(df_BOD_Match, 'df_BOD_Match',False)
    

    df_BOD_ShortReason_NoMatch = df_Main_CapaRCA.merge(df_BOD_Match, 
                                                   on=[versionVersionName, toDemandDemandID, toTimeWeek, shortReason_ProblemTypeo9,
                                                       shortReason_ProblemActivity1, shortReason_ProblemActivity2, shortReason_ProblemActivity3,
                                                       shortReason_ProblemSite, shortReason_ProblemWeek, shortReason_ProblemResource],
                                                   how='left')
    del df_BOD_Match
    
    df_BOD_ShortReason_NoMatch = df_BOD_ShortReason_NoMatch.loc[df_BOD_ShortReason_NoMatch['Chk_Valeue'].isna()]
    
    df_BOD_ShortReason_NoMatch[problemTypeProblemReason] = 'NO_MATCH'
    
    # Problem Type (df_in_ProblemType) Merge 
    df_BOD_ShortReason_NoMatch = df_BOD_ShortReason_NoMatch.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_BOD_ShortReason_NoMatch[shortReason_ShortCategory] = df_BOD_ShortReason_NoMatch[problemTypeShortCategory]
    df_BOD_ShortReason_NoMatch[shortReason_ShortReason] = df_BOD_ShortReason_NoMatch[problemTypeShortReason]
    df_BOD_ShortReason_NoMatch[shortReason_ProblemCategory1] = df_BOD_ShortReason_NoMatch[problemTypeProblemCategory1]
    df_BOD_ShortReason_NoMatch[shortReason_ProblemCategory2] = df_BOD_ShortReason_NoMatch[problemTypeProblemCategory2]
    # df_BOD_ShortReason_NoMatch[shortReason_ProblemOwner]     = df_BOD_ShortReason_NoMatch[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_BOD_ShortReason_NoMatch[shortReason_ProblemRefUI]     = df_BOD_ShortReason_NoMatch[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_BOD_ShortReason_NoMatch[shortReason_ProblemFactor] = ''
    df_BOD_ShortReason_NoMatch[shortReason_ProblemValue1] = ''
    df_BOD_ShortReason_NoMatch[shortReason_ProblemValue2] = ''
    df_BOD_ShortReason_NoMatch[shortReason_ProblemValue3] = 'STEP-100 BOD NO_MATCH'
    
    # 칼럼 정리
    df_BOD_ShortReason_NoMatch = df_BOD_ShortReason_NoMatch[cList_A].copy()
    
    df_BOD_ShortReason_NoMatch.drop_duplicates(inplace=True)
    
    print_df(df_BOD_ShortReason_NoMatch, 'df_BOD_ShortReason_NoMatch',False)
    #========================================================================================================
    
    del [df_Main_MtrlRCA, df_Main_CapaRCA]
    step('=====> STEP 100 : NNoMatch Data create End')
    
    ################################################################################################################
    # STEP 110 : Post Short Reason 처리 1 : Item Site Asn_Cur Status
    ################################################################################################################
    step('=====> STEP 110 : Post Short Reason 1: Item Site Asn_Cur Status Data')
    # Short Reason Data 취합
    df_All_ShortReason = pd.concat([df_BOM_ShortReason, df_BOM_ShortReason_NoMatch,
                                    df_BOD_ShortReason, df_BOD_ShortReason_NoMatch
                                    ])
    del [df_BOM_ShortReason, df_BOM_ShortReason_NoMatch, df_BOD_ShortReason, df_BOD_ShortReason_NoMatch]
    
    print_df(df_All_ShortReason, 'df_All_ShortReason 1',False)
    
    #-------------------------------------------------------------------
    # 1) Measure.[Item Site Asn_Cur Status] not in ("ACTIVE","PLANNED") then 'SET_EOL' : Reference : to.[Item].[Item], to.[Location].[Location]
    df_All_ShortReason = df_All_ShortReason.merge(df_in_ItemSiteAsn,
                                                  left_on=[versionVersionName, toItemItem, toLocationLocation],
                                                  right_on=[versionVersionName, itemItem, locationLocation], how='left')
    df_All_ShortReason.drop(columns=[itemItem, locationLocation], inplace=True)
    
    df_All_ShortReason['Chect_Value'] = np.where(
                                                  df_All_ShortReason[itemSiteAsn_CurStatus].notna() &
                                                ~(df_All_ShortReason[itemSiteAsn_CurStatus].isin(["ACTIVE", "PLANNED"])),
                                                'AA',
                                                'NN'
                                                )
    df_All_ShortReason.rename(columns={itemSiteAsn_CurStatus: 'CurStatus'}, inplace=True)
    
    df_All_ShortReason_A = df_All_ShortReason[df_All_ShortReason['Chect_Value'] == 'AA'].copy()
    df_All_ShortReason_N = df_All_ShortReason[df_All_ShortReason['Chect_Value'] == 'NN'].copy()
    
    print_df(df_All_ShortReason_A, 'df_All_ShortReason_A',False) # 1) 변환대상
    #print_df(df_All_ShortReason_N, 'df_All_ShortReason_N 1',False) # 비 변환대상
    del df_All_ShortReason
    
    df_All_ShortReason_A[problemTypeProblemReason] = 'SET_EOL'
    
    #----------------------------------------------------------------------
    # 2) Measure.[Item Site Asn_Cur Status] not in ("ACTIVE","PLANNED") then 'from.[Item].[Item]의 Item Stage' || '_EOL' : Reference : from.[Item].[Item], from.[Location].[Location]
    df_All_ShortReason_N = df_All_ShortReason_N.merge(df_in_ItemSiteAsn,
                                                  left_on=[versionVersionName, shortReason_ProblemItem,
                                                           shortReason_ProblemSite],
                                                  right_on=[versionVersionName, itemItem, locationLocation], how='left')
    df_All_ShortReason_N.drop(columns=[itemItem, locationLocation, 'CurStatus'], inplace=True)
    
    df_All_ShortReason_N['Chect_Value'] = np.where(
                                              df_All_ShortReason_N[itemSiteAsn_CurStatus].notna() &
                                             ~(df_All_ShortReason_N[itemSiteAsn_CurStatus].isin(["ACTIVE", "PLANNED"])),
                                             'BB',
                                             'NN'
                                             )
    
    df_All_ShortReason_N.rename(columns={itemSiteAsn_CurStatus: 'CurStatus'}, inplace=True)
    del df_in_ItemSiteAsn
    
    df_All_ShortReason_B = df_All_ShortReason_N[df_All_ShortReason_N['Chect_Value'] == 'BB'].copy()
    df_All_ShortReason_N = df_All_ShortReason_N[df_All_ShortReason_N['Chect_Value'] == 'NN'].copy()
    
    print_df(df_All_ShortReason_B, 'df_All_ShortReason_B',False)  # 1) 변환대상
    print_df(df_All_ShortReason_N, 'df_All_ShortReason_N 2',False)  # 비 변환대상
    
    df_All_ShortReason_B[problemTypeProblemReason] = df_All_ShortReason_B[fromItemItemStage] + '_EOL'
    
    df_ShortReason_EX = pd.concat([df_All_ShortReason_A, df_All_ShortReason_B])
    del [df_All_ShortReason_A, df_All_ShortReason_B]
    print_df(df_ShortReason_EX, 'df_ShortReason_EX 1-1',False)
    
    # 초기화 ------------------------------------------
    df_ShortReason_EX[shortReason_ShortCategory] = ''
    df_ShortReason_EX[shortReason_ShortReason] = ''
    df_ShortReason_EX[shortReason_ProblemCategory1] = ''
    df_ShortReason_EX[shortReason_ProblemCategory2] = ''
    # df_ShortReason_EX[shortReason_ProblemOwner]   = '' # Dimemsion Attribute 없음
    # df_ShortReason_EX[shortReason_ProblemRefUI]   = '' # Dimemsion Attribute 없음    
    df_ShortReason_EX[shortReason_ProblemFactor] = ''
    df_ShortReason_EX[shortReason_ProblemValue1] = ''
    df_ShortReason_EX[shortReason_ProblemValue2] = ''
    # df_All_ShortReason[shortReason_ProblemValue3] # 변경이력 관리를 위해 초기화 제외
    
    # Problem Type (df_in_ProblemType) Merge 
    df_ShortReason_EX = df_ShortReason_EX.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_ShortReason_EX[shortReason_ShortCategory]    = df_ShortReason_EX[problemTypeShortCategory]
    df_ShortReason_EX[shortReason_ShortReason]      = df_ShortReason_EX[problemTypeShortReason]
    df_ShortReason_EX[shortReason_ProblemCategory1] = df_ShortReason_EX[problemTypeProblemCategory1]
    df_ShortReason_EX[shortReason_ProblemCategory2] = df_ShortReason_EX[problemTypeProblemCategory2]
    # df_ShortReason_EX[shortReason_ProblemOwner]   = df_ShortReason_EX[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_ShortReason_EX[shortReason_ProblemRefUI]   = df_ShortReason_EX[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_ShortReason_EX[shortReason_ProblemFactor] = 'Cur Status'
    df_ShortReason_EX[shortReason_ProblemValue1] = df_ShortReason_EX['CurStatus']
    df_ShortReason_EX[shortReason_ProblemValue2] = ''
    df_ShortReason_EX[shortReason_ProblemValue3] = df_ShortReason_EX[shortReason_ProblemValue3] + '; STEP 110 Item Site Asn_Cur Status'
    
    df_All_ShortReason = pd.concat([df_All_ShortReason_N, df_ShortReason_EX])
    del [df_All_ShortReason_N, df_ShortReason_EX]
    
    # 칼럼 정리
    df_All_ShortReason = df_All_ShortReason[cList_A].copy()
    
    df_All_ShortReason.drop_duplicates(inplace=True)
    
    print_df(df_All_ShortReason, 'df_All_ShortReason 1',False)
    
    step('=====> STEP 110 : Post Short Reason 1: Item Site Asn_Cur Status Data End')
    
    ################################################################################################################
    # STEP 120 : Post Short Reason 처리 2 : PLC Sales_EOS Date
    ################################################################################################################
    step('=====> STEP 120 : Post Short Reason 2: PLC Sales_EOS Date Data')
    
    now = datetime.datetime.now()
    df_All_ShortReason[sysdate] = pd.to_datetime(now.date(), format='%Y-%m-%d')
    # df_All_ShortReason[sysdate] = pd.to_datetime('2024-08-02', format='%Y-%m-%d') #test용
    
    # Merge : df_in_SalesDomain
    df_in_SalesDomain = df_in_SalesDomain.rename(columns={salesDomainCustomerGroup:toSalesDomainCustomerGroup})
    df_All_ShortReason = df_All_ShortReason.merge(df_in_SalesDomain, on=[toSalesDomainCustomerGroup], how='left')
    del df_in_SalesDomain
    
    # Merge : df_PLCSales_EOS
    df_All_ShortReason = df_All_ShortReason.merge(df_PLCSales_EOS,
                                                  left_on=[versionVersionName, toItemItem, salesDomainAP2],
                                                  right_on=[versionVersionName, itemItem, salesDomainAP2],
                                                  how='left')
    del df_PLCSales_EOS
    
    #변환대상 추출 조건 확인필요. itemItem (조인여부로 추출 구분), itemSiteAsn_CurStatus (값이 있는지여부로 추출 구분)
    df_ShortReason    = df_All_ShortReason.loc[~(df_All_ShortReason[eOSComWeek] < df_All_ShortReason[toTimeWeek])].copy()  #비 변환대상
    df_ShortReason_EX = df_All_ShortReason.loc[df_All_ShortReason[eOSComWeek] < df_All_ShortReason[toTimeWeek]].copy() #변환대상
    del df_All_ShortReason
    
    print_df(df_ShortReason, 'df_ShortReason 2',False)
    print_df(df_ShortReason_EX, 'df_ShortReason_EX 2',False)
    
    df_ShortReason_EX[problemTypeProblemReason] = np.select(
                                      [(df_ShortReason_EX[pLCSales_EOSComDate] < df_ShortReason_EX[sysdate]), True, ],
                                      ['SET_EOL', 'SET_PLANNED_EOL'])
    
    print_df(df_ShortReason_EX, 'df_ShortReason_EX 2-1',False)
    #df_ShortReason_EX[problemTypeProblemReason] = 'SET_PLANNED_EOL'    
    
    # 초기화 ------------------------------------------
    df_ShortReason_EX[shortReason_ShortCategory]    = ''
    df_ShortReason_EX[shortReason_ShortReason]      = ''
    df_ShortReason_EX[shortReason_ProblemCategory1] = ''
    df_ShortReason_EX[shortReason_ProblemCategory2] = ''
    # df_ShortReason_EX[shortReason_ProblemOwner]   = '' # Dimemsion Attribute 없음
    # df_ShortReason_EX[shortReason_ProblemRefUI]   = '' # Dimemsion Attribute 없음    
    df_ShortReason_EX[shortReason_ProblemFactor]    = ''
    df_ShortReason_EX[shortReason_ProblemValue1]    = ''
    df_ShortReason_EX[shortReason_ProblemValue2]    = ''
    # df_All_ShortReason[shortReason_ProblemValue3] # 변경이력 관리를 위해 초기화 제외
    
    # Problem Type (df_in_ProblemType) Merge 
    df_ShortReason_EX = df_ShortReason_EX.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_ShortReason_EX[shortReason_ShortCategory]    = df_ShortReason_EX[problemTypeShortCategory]
    df_ShortReason_EX[shortReason_ShortReason]      = df_ShortReason_EX[problemTypeShortReason]
    df_ShortReason_EX[shortReason_ProblemCategory1] = df_ShortReason_EX[problemTypeProblemCategory1]
    df_ShortReason_EX[shortReason_ProblemCategory2] = df_ShortReason_EX[problemTypeProblemCategory2]
    # df_ShortReason_EX[shortReason_ProblemOwner]   = df_ShortReason_EX[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_ShortReason_EX[shortReason_ProblemRefUI]   = df_ShortReason_EX[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_ShortReason_EX[shortReason_ProblemFactor] = 'EOS Date'
    df_ShortReason_EX[shortReason_ProblemValue1] = df_ShortReason_EX[pLCSales_EOSComDate].dt.date #String YYYY-MM-DD
    df_ShortReason_EX[shortReason_ProblemValue2] = ''
    df_ShortReason_EX[shortReason_ProblemValue3] = df_ShortReason_EX[shortReason_ProblemValue3] + '; STEP 120 PLC Sales_EOS Date'
    
    df_All_ShortReason = pd.concat([df_ShortReason, df_ShortReason_EX])
    del [df_ShortReason, df_ShortReason_EX]
    
    cList_A_AP2 = cList_A + [salesDomainAP2] # Sales Domain.[AP2] 다음 STEP에서 사용
    # 칼럼 정리
    df_All_ShortReason = df_All_ShortReason[cList_A_AP2].copy()
    
    df_All_ShortReason.drop_duplicates(inplace=True)
    
    print_df(df_All_ShortReason, 'df_All_ShortReason 2',False)
    
    step('=====> STEP 120 : Post Short Reason 2: PLC Sales_EOS Date Data End')
    ################################################################################################################
    # STEP 130 : Post Short Reason 처리 3 : PLC Sales_RTS Date
    ################################################################################################################
    step('=====> STEP 130 : Post Short Reason 3: PLC Sales_RTS Date Data')
    
    # Merge : df_PLCSales_RTS
    df_All_ShortReason = df_All_ShortReason.merge(df_PLCSales_RTS,
                                                  left_on=[versionVersionName, toItemItem, salesDomainAP2],
                                                  right_on=[versionVersionName, itemItem, salesDomainAP2],
                                                  how='left')
    del df_PLCSales_RTS
    
    #변환대상 추출 조건 확인필요. itemItem (조인여부로 추출 구분), itemSiteAsn_CurStatus (값이 있는지여부로 추출 구분)
    df_ShortReason    = df_All_ShortReason.loc[~(~(df_All_ShortReason[rTSComWeek].isna()) & (df_All_ShortReason[rTSComWeek] > df_All_ShortReason[toTimeWeek]))].copy()  #비 변환대상
    df_ShortReason_EX = df_All_ShortReason.loc[~(df_All_ShortReason[rTSComWeek].isna()) & (df_All_ShortReason[rTSComWeek] > df_All_ShortReason[toTimeWeek])].copy() #변환대상
    del df_All_ShortReason
    
    print_df(df_ShortReason, 'df_ShortReason 3',False)
    print_df(df_ShortReason_EX, 'df_ShortReason_EX 3',False)
    
    df_ShortReason_EX[problemTypeProblemReason] = 'NEW_MODEL'
    
    # 초기화 ------------------------------------------
    df_ShortReason_EX[shortReason_ShortCategory] = ''
    df_ShortReason_EX[shortReason_ShortReason] = ''
    df_ShortReason_EX[shortReason_ProblemCategory1] = ''
    df_ShortReason_EX[shortReason_ProblemCategory2] = ''
    # df_ShortReason_EX[shortReason_ProblemOwner]   = '' # Dimemsion Attribute 없음
    # df_ShortReason_EX[shortReason_ProblemRefUI]   = '' # Dimemsion Attribute 없음    
    df_ShortReason_EX[shortReason_ProblemFactor] = ''
    df_ShortReason_EX[shortReason_ProblemValue1] = ''
    df_ShortReason_EX[shortReason_ProblemValue2] = ''
    # df_All_ShortReason[shortReason_ProblemValue3] # 변경이력 관리를 위해 초기화 제외
    
    # Problem Type (df_in_ProblemType) Merge 
    df_ShortReason_EX = df_ShortReason_EX.merge(df_in_ProblemType, on=[problemTypeProblemReason], how='left')
    
    # [Problem Type] Dimemsion 조인 후 아래적용
    df_ShortReason_EX[shortReason_ShortCategory] = df_ShortReason_EX[problemTypeShortCategory]
    df_ShortReason_EX[shortReason_ShortReason] = df_ShortReason_EX[problemTypeShortReason]
    df_ShortReason_EX[shortReason_ProblemCategory1] = df_ShortReason_EX[problemTypeProblemCategory1]
    df_ShortReason_EX[shortReason_ProblemCategory2] = df_ShortReason_EX[problemTypeProblemCategory2]
    # df_ShortReason_EX[shortReason_ProblemOwner]   = df_ShortReason_EX[ProblemTypeProblemOwner] # Dimemsion Attribute 없음
    # df_ShortReason_EX[shortReason_ProblemRefUI]   = df_ShortReason_EX[problemTypeProblemReasonProblemRefUI] # Dimemsion Attribute 없음
    
    df_ShortReason_EX[shortReason_ProblemFactor] = 'RTS Date'
    df_ShortReason_EX[shortReason_ProblemValue1] = df_ShortReason_EX[pLCSales_RTSComDate].dt.date #String YYYY-MM-DD
    df_ShortReason_EX[shortReason_ProblemValue2] = ''
    df_ShortReason_EX[shortReason_ProblemValue3] = df_ShortReason_EX[shortReason_ProblemValue3] + '; STEP 130 PLC Sales_RTS Date'
    
    df_All_ShortReason = pd.concat([df_ShortReason, df_ShortReason_EX])
    del [df_ShortReason, df_ShortReason_EX]

    # 칼럼 정리
    df_All_ShortReason = df_All_ShortReason[cList_A].copy()
    
    df_All_ShortReason.drop_duplicates(inplace=True)
    
    print_df(df_All_ShortReason, 'df_All_ShortReason 3',False)
    
    step('=====> STEP 130 : Post Short Reason 3: PLC Sales_RTS Date Data End')
    ################################################################################################################
    # STEP 200 : output table create
    ################################################################################################################
    step('=====> STEP 200 : Final output table create')
    
    # out Data 생성 
    df_out_ShortReason = df_All_ShortReason.copy()
    del [df_All_ShortReason, df_in_ProblemType]
    
    # 칼럼명 변경
    df_out_ShortReason.rename(columns={toDemandDemandID: demandDemandID, toItemItem: itemItem, toLocationLocation: locationLocation,
                                       toSalesDomainCustomerGroup: salesDomainCustomerGroup, toTimeWeek: timeWeek}, inplace=True)
    
    df_out_ShortReason.drop_duplicates(inplace=True)
    df_out_ShortReason[sequenceSequence] = df_out_ShortReason.groupby([versionVersionName, demandDemandID, timeWeek, problemTypeProblemReason]).cumcount() + 1
    
    # 버전 처리
    #df_out_ShortReason[versionVersionName] = paramOutVersion
    
    cList_ShortReason = [versionVersionName, itemItem, timeWeek, locationLocation, salesDomainCustomerGroup, 
                         sequenceSequence, demandDemandID, problemTypeProblemReason, shortReason_ProblemActivity1, 
                         shortReason_ProblemActivity2, shortReason_ProblemActivity3, shortReason_ProblemBOD, 
                         shortReason_ProblemBOM, shortReason_ProblemCategory1, shortReason_ProblemCategory2, 
                         shortReason_ProblemFactor, shortReason_ProblemItem, shortReason_ProblemNeedQty,
                         shortReason_ProblemOwner, shortReason_ProblemQty, shortReason_ProblemRefUI, 
                         shortReason_ProblemResource, shortReason_ProblemSite, shortReason_ProblemTypeBY, 
                         shortReason_ProblemTypeo9, shortReason_ProblemValue1, shortReason_ProblemValue2, 
                         shortReason_ProblemValue3, shortReason_ProblemWeek, shortReason_ShortCategory, 
                         shortReason_ShortReason]
                         # shortReason_ProblemReason, #메저 없음.
    # out 칼럼 설정
    df_out_ShortReason = df_out_ShortReason[cList_ShortReason].copy()
    
    row_count, col_count = df_out_ShortReason.shape
    note(f'=====> Final df_out_ShortReason rows : {row_count}, column : {col_count}')
    
    print_df(df_out_ShortReason, 'df_out_ShortReason',False)
    step('=====> STEP 200-1 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_ShortReason, 'df_out_ShortReason')
    
    step('=====> STEP 200-2 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_ShortReason = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()