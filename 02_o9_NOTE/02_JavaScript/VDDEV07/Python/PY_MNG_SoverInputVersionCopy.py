"""
* 프로그램명
    - PY_MNG_SoverInputVersionCopy

* 내용
    - 지정한 paramOutVersion input을 Copy 하는 프로시져

* 변경이력
    - 2024.11.15 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 지정버전, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_Param : Select (Version.[Version Name] ) on row, ({Measure.[Adherence To Production Actual KPI Minimum Limit], Measure.[Adherence To Production KPI With Exception Minimum Limit], Measure.[Adherence to Production Max Limit], Measure.[Adherence to Production Min Limit], Measure.[LP Horizon], Measure.[W Capacity Constrained], Measure.[W Enable Capacity Bands For SS], Measure.[W Global Demand Build Ahead Limit], Measure.[W Global Demand Build Late Limit], Measure.[W Inventory Planning Parameter], Measure.[W Item Final Set], Measure.[W LP Solver Name], Measure.[W Late Plan Strategy], Measure.[W Location Final Set], Measure.[W Master Calendar Code], Measure.[W Material Constrained], Measure.[W Min Time Hard Peg], Measure.[W Plan Current Bucket], Measure.[W Plan Current Date], Measure.[W Plan Date Hard Peg], Measure.[W Plan End Bucket], Measure.[W Plan End Date], Measure.[W Plan Start Bucket], Measure.[W Plan Start Date], Measure.[W Planning Owner], Measure.[W Resource Final Set], Measure.[W Skip SS For Unviable Buckets], Measure.[W Solver Capacity Bands To Minimize Lateness], Measure.[W Solver Delete Data], Measure.[W Solver Demand Slice Factor], Measure.[W Solver Demand Slice Threshold], Measure.[W Solver Flag Allow NOH], Measure.[W Solver Flag Avoid Build Ahead In Inventory Plan], Measure.[W Solver Flag Avoid Material Reallocation], Measure.[W Solver Flag Expedite WIP], Measure.[W Solver Flag Inventory Plan Policy], Measure.[W Solver Flag Inventory Plan Strategy], Measure.[W Solver Flag Inventory Plan Type], Measure.[W Solver Flag Minimize Inventory Build Ahead], Measure.[W Solver Flag Minimize No Carry Violations], Measure.[W Solver Flag No Peggings], Measure.[W Solver Flag Respect Freeze Window For WIPs], Measure.[W Solver Flag Shelf Life Plan], Measure.[W Solver Flag SupplyCode Plan], Measure.[W Solver Flag Try Material Reallocation In RCA], Measure.[W Solver Inventory Plan Bands], Measure.[W Solver Run Type Flag], Measure.[W Solver SS Build Ahead Limit], Measure.[W Storage Constrained]}) on column;
    - df_in_MatConsAsn : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Material Consumption Association], Measure.[W Material Consumption Quantity Per]}) on column;
    - df_in_ProdAsn : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Priority], Measure.[W Eff End], Measure.[W Eff Start], Measure.[W Material Production Association], Measure.[W Material Production Quantity Per], Measure.[W Production Edge Offset], Measure.[W WIP Sweep Priority]}) on column;
    - df_in_CapaConsAsn : Select (Version.[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Input Resource Priority], Measure.[W Resource Category], Measure.[W Resource Consumed Quantity Per], Measure.[W Resource Consumption Association]}) on column;
    - df_in_ResGrpConsAsn : Select (Version.[Version Name] * [Location].[Location] * [Resource Group].[Resource Group] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Simultaneous Capacity Consumption Association]}) on column;
    - df_in_ActParam : Select (Version.[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Cost Per Unit], Measure.[W Activity End Date], Measure.[W Activity Flow Priority], Measure.[W Activity Lead Time], Measure.[W Activity Lead Time Standard Deviation], Measure.[W Activity Mandatory Offset], Measure.[W Activity ReEntrant], Measure.[W Activity Start Date], Measure.[W Lot Size Penalty Per Unit Qty], Measure.[W Lot Size Priority]}) on column;
    - df_in_ActShare : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Priority Time Varying], Measure.[W Activity Share]}) on column;
    - df_in_FrozenWindow : Select (Version.[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Frozen Window], Measure.[W Frozen Window Apply At]}) on column;
    - df_in_LotSizeParam : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W LotSize Increment], Measure.[W Max LotSize], Measure.[W Min LotSize], Measure.[W Soft LotSize]}) on column;
    - df_in_InvNodeParam : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[W Alternate Material Node Group Priority], Measure.[W Constant Min Time Target], Measure.[W Constant Target Inventory], Measure.[W Constant Unit Price], Measure.[W Constant WOS Target], Measure.[W Default Max Inventory Qty], Measure.[W Default Min Inventory Qty], Measure.[W Early Production Period], Measure.[W Early Route Mix Policy], Measure.[W Finite Period], Measure.[W Finite Period UOM], Measure.[W Forced Policy], Measure.[W IL Demand Split], Measure.[W Infinite Material Node], Measure.[W Infinite Material Node BK], Measure.[W Infinite Material Node Backup], Measure.[W Infinite Material Supply Priority], Measure.[W Inventory Holding Cost Per Unit Time], Measure.[W Inventory Holding Priority], Measure.[W Is No Stock], Measure.[W Is Reentrant Capacity Plan], Measure.[W Is Release Exclusion], Measure.[W Item Incremental Scope], Measure.[W Late Route Mix Policy], Measure.[W Look Ahead Horizon], Measure.[W Material Chain Custom Short Type], Measure.[W Material Incremental Flag], Measure.[W Material Node Build Ahead Limit], Measure.[W Material Node Build Ahead Limit UOM], Measure.[W Material Reallocation Policy], Measure.[W Max Stock Layer], Measure.[W Max Stock Measure], Measure.[W Max Stock Penalty Cost], Measure.[W Max Stock WOS Measure], Measure.[W Minimize Inventory Build Ahead At Node], Measure.[W No Carry Inventory], Measure.[W Plan Date Node Marker], Measure.[W Plan Date Search Alternate], Measure.[W Production Policy], Measure.[W SS Build Ahead Limit], Measure.[W SS Build Ahead Limit UOM], Measure.[W Safety Quantity Period], Measure.[W Safety Quantity Period UOM], Measure.[W Safety Quantity Policy], Measure.[W Safety Stock Priority], Measure.[W Safety Stock Violation Cost Per Unit Time], Measure.[W Safety Time Policy], Measure.[W Soft No Carry Inventory], Measure.[W Split Material Segment], Measure.[W Stock Devouring Level], Measure.[W Target Stock Layer], Measure.[W UOM], Measure.[W Universal SupplyCode], Measure.[W WIP Sweep Depth]}) on column;
    - df_in_HolidayCal : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Consumption Holiday], Measure.[W Production Holiday]}) on column;
    - df_in_ResGrpPriority : Select (Version.[Version Name] * [Resource Group].[Resource Group] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Input Resource Group Priority]}) on column;
    - df_in_Demand : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[W Cascading RCA Limit], Measure.[W Demand Build Ahead Limit], Measure.[W Demand Build Ahead Limit UOM], Measure.[W Demand Build Late Limit], Measure.[W Demand Build Late Limit UOM], Measure.[W Demand Debug Flag], Measure.[W Demand Delivery LotSize], Measure.[W Demand Fair Share Priority], Measure.[W Demand Fulfilment Policy], Measure.[W Demand Incremental Flag], Measure.[W Demand Layer], Measure.[W Demand Layer Temp], Measure.[W Demand Leadtime Due], Measure.[W Demand Match Code], Measure.[W Demand Multi Path RCA], Measure.[W Demand Plan Date Offset], Measure.[W Demand Priority], Measure.[W Demand Priority from Netting], Measure.[W Demand Priority to Final SCS], Measure.[W Demand Quantity Temp], Measure.[W Demand Quantity to SCS], Measure.[W Demand SS PreBuild], Measure.[W Demand Short Code], Measure.[W Demand Split], Measure.[W Demand Supply Code], Measure.[W DumDemand Quantity to SCS], Measure.[W Early Capacity Layer Least], Measure.[W Early Capacity Layer Max], Measure.[W Is Stock Redevour], Measure.[W Late Capacity Layer Least], Measure.[W Late Capacity Layer Max], Measure.[W Late Delivery Penalty Cost], Measure.[W Minimum Shippable Age], Measure.[W Plan Along Single Path], Measure.[W SegmentID], Measure.[W Short Delivery Penalty Cost]}) on column;
    - df_in_Inv : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] ) on row, ({Measure.[W Material Node for Demand Split], Measure.[W Quantity Max Target], Measure.[W Quantity Min Target], Measure.[W Quantity Target Stock Time Varying], Measure.[W Re-Order Point Quantity], Measure.[W Re-Order Point WOS], Measure.[W SS Demand Priority], Measure.[W SS Due Date], Measure.[W SS Pre-Build Node Marker], Measure.[W SS Pre-Build WOS Target], Measure.[W Target Inventory], Measure.[W Target Inventory Backup], Measure.[W Time Varying Inventory Holding Cost Per Unit Time], Measure.[W WOS Max Target], Measure.[W WOS Min Target], Measure.[W WOS Target], Measure.[W WOS Target Stock Time Varying]}) on column;
    - df_in_InvOrder : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[W Expected Receipts], Measure.[W Expected Receipts Backup], Measure.[W Expected Receipts Pegging ID], Measure.[W OnHand Dedication Policy], Measure.[W OnHand Pegging ID], Measure.[W OnHand Quantity], Measure.[W OnHand Quantity Backup], Measure.[W OnHand Quantity Increment %], Measure.[W OnHand Quantity Input], Measure.[W OnHand Quantity Override]}) on column;
    - df_in_WIP : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Consume Outbound Capacity], Measure.[W Consumption WIP MPBO Override to SCS], Measure.[W Locked WIP Material Consumption Quantity], Measure.[W Locked WIP Material Production Quantity], Measure.[W Production WIP MPBO Override], Measure.[W Production WIP MPBO Override to SCS], Measure.[W WIP Acceptable Lot], Measure.[W WIP Due Date], Measure.[W WIP LotSize], Measure.[W WIP LotSize Cal], Measure.[W WIP Material Consumption Quantity], Measure.[W WIP Material Consumption Quantity Backup], Measure.[W WIP Material Consumption Quantity Lot], Measure.[W WIP Material Production Incremental Flag], Measure.[W WIP Material Production Quantity], Measure.[W WIP Material Production Quantity Backup], Measure.[W WIP Material Production Quantity Intermediate], Measure.[W WIP Pegging ID]}) on column;
    - df_in_WIPCapa : Select (Version.[Version Name] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Capacity Consumption WIP MPBO Override to SCS], Measure.[W Locked WIP Capacity Consumption Quantity], Measure.[W WIP Capacity Consumption Quantity]}) on column;
    - df_in_Capa : Select (Version.[Version Name] * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row, ({Measure.[W Capacity Incremental Flag], Measure.[W Capacity Incremental Flag Count], Measure.[W Coarser Maximum Utilization Quantity], Measure.[W Coarser Minimum Utilization Quantity], Measure.[W Flex Capacity Band1], Measure.[W Flex Capacity Band1 %], Measure.[W Flex Capacity Band2], Measure.[W Flex Capacity Band2 %], Measure.[W Infinite Capacity Node], Measure.[W Maximum Utilization Penalty Per Unit Qty], Measure.[W Minimum Utilization Penalty Per Unit Qty], Measure.[W Minimum Utilization Target], Measure.[W Remaining Capacity], Measure.[W Resource Base Capacity], Measure.[W Resource Calendar Bucket Size], Measure.[W Resource Calendar Bucket Size UOM], Measure.[W Resource Calendar Repeat Pattern]}) on column;
    - df_in_INF : Select (Version.[Version Name] * [Location].[Location] * [Resource].[Resource] ) on row, ({Measure.[W Capacity Fence], Measure.[W Capacity Maximum Utilization Priority], Measure.[W Capacity Minimum Utilization Priority], Measure.[W Infinite Capacity], Measure.[W Infinite Capacity Supply Priority]}) on column;
    - df_in_BOMCompEff : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Component End Date], Measure.[W Component Start Date]}) on column;
    - df_in_LPSObj : Select (Version.[Version Name] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [LPObjective].[Objective Type] ) on row, ({Measure.[W LP Active], Measure.[W Scope Max], Measure.[W Scope Min]}) on column;
    - df_in_FlexCapaPriority : Select (Version.[Version Name] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [Location].[Location] * [Resource].[Resource] ) on row, ({Measure.[W Flex Capacity Cost Per Unit Qty], Measure.[W Flex Capacity Priority]}) on column;
    - df_in_GSProp : Select (FROM.[Time].[Week] * FROM.[Resource Group].[Resource Group] * TO.[Resource Group].[Resource Group]) on row, ({Edge.[001.051W Group Sourcing Proportion Inputs].[W Group Sourcing Proportion]}) on column where {RelationshipType.[001.051W Group Sourcing Proportion Inputs], Version.[Version Name]};
    - df_in_FlexCapa : Select (Version.[Version Name] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row, ({Measure.[W LP Flex Capacity]}) on column;
    - df_in_BODW : Select (Version.[Version Name] * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Lead Time Time Varying]}) on column;
    - df_in_GSNode : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Resource Group].[Resource Group] ) on row, ({Measure.[W Group Sourcing MN Association]}) on column;
    - df_in_GSPriority : Select (Version.[Version Name] * [Resource Group].[Resource Group] ) on row, ({Measure.[W Group Proportional Sourcing Priority]}) on column;
    - df_in_ItemLoc : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[W Alternate Item Input Final Association], Measure.[W Item Location Association], Measure.[W Valid Network Item Location]}) on column;
    - df_in_TactTimeW : Select (Version.[Version Name] * [Time].[Week] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Resource Consumed Time Varying Quantity Per]}) on column;
    - df_in_MCMap : Select (Version.[Version Name] * [Documents].[OrderlineID] ) on row, ({Measure.[W Original Owner Association], Measure.[W Original Owner Location]}) on column;
    - df_in_MCLoc : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Multi Level SS Association], Measure.[Multi Level SS Hub], Measure.[Preallocation Association], Measure.[Preallocation Hub]}) on column;


* Flow Summary
    - STEP1.
    - STEP2.

* Output Table
    - df_out_Param
    - df_out_MatConsAsn
    - df_out_ProdAsn
    - df_out_CapaConsAsn
    - df_out_ResGrpConsAsn
    - df_out_ActParam
    - df_out_ActShare
    - df_out_FrozenWindow
    - df_out_LotSizeParam
    - df_out_InvNodeParam
    - df_out_HolidayCal
    - df_out_ResGrpPriority
    - df_out_Demand
    - df_out_Inv
    - df_out_InvOrder
    - df_out_WIP
    - df_out_WIPCapa
    - df_out_Capa
    - df_out_INF
    - df_out_BOMCompEff
    - df_out_LPSObj
    - df_out_FlexCapaPriority
    - df_out_GSProp
    - df_out_FlexCapa
    - df_out_BODW
    - df_out_GSNode
    - df_out_GSPriority
    - df_out_ItemLoc
    - df_out_TactTimeW
    - df_out_MCMap
    - df_out_MCLoc

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_MNG_SoverInputVersionCopy] for measures {[W Capacity Constrained]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "PEG_TEST"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    -

;

"""
import gc
import traceback
import pandas as pd
import tracemalloc
import time
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MNG_PlanGroupUpdate'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
COMMON_SOURCE_VERSION = common.G_SourceVersion


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(f"{file_name}.csv", index=False)


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    empty_status = "is empty" if df.empty else ""
    df_name = f"{df_name} {empty_status}"
    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    logger.Step(p_step_no=no, p_step_desc=f'{string}')


# 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
tracemalloc.start()
start_time = time.time()

logger.debug(f'[START] {str_instance}')
logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')

try:
    ################################################################################################################
    # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
    ################################################################################################################
    step(100, '=====> STEP 1(Start) : 전처리 - 모듈 내에서 사용될 input table load')

    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_Param = read_csv_file("df_in_Param")
        df_in_MatConsAsn = read_csv_file("df_in_MatConsAsn")
        df_in_ProdAsn = read_csv_file("df_in_ProdAsn")
        df_in_CapaConsAsn = read_csv_file("df_in_CapaConsAsn")
        df_in_ResGrpConsAsn = read_csv_file("df_in_ResGrpConsAsn")
        df_in_ActParam = read_csv_file("df_in_ActParam")
        df_in_ActShare = read_csv_file("df_in_ActShare")
        df_in_FrozenWindow = read_csv_file("df_in_FrozenWindow")
        df_in_LotSizeParam = read_csv_file("df_in_LotSizeParam")
        df_in_InvNodeParam = read_csv_file("df_in_InvNodeParam")
        df_in_HolidayCal = read_csv_file("df_in_HolidayCal")
        df_in_ResGrpPriority = read_csv_file("df_in_ResGrpPriority")
        df_in_Demand = read_csv_file("df_in_Demand")
        df_in_Inv = read_csv_file("df_in_Inv")
        df_in_InvOrder = read_csv_file("df_in_InvOrder")
        df_in_WIP = read_csv_file("df_in_WIP")
        df_in_WIPCapa = read_csv_file("df_in_WIPCapa")
        df_in_Capa = read_csv_file("df_in_Capa")
        df_in_INF = read_csv_file("df_in_INF")
        df_in_BOMCompEff = read_csv_file("df_in_BOMCompEff")
        df_in_LPSObj = read_csv_file("df_in_LPSObj")
        df_in_FlexCapaPriority = read_csv_file("df_in_FlexCapaPriority")
        df_in_GSProp = read_csv_file("df_in_GSProp")
        df_in_FlexCapa = read_csv_file("df_in_FlexCapa")
        df_in_BODW = read_csv_file("df_in_BODW")
        df_in_GSNode = read_csv_file("df_in_GSNode")
        df_in_GSPriority = read_csv_file("df_in_GSPriority")
        df_in_ItemLoc = read_csv_file("df_in_ItemLoc")
        df_in_TactTimeW = read_csv_file("df_in_TactTimeW")
        df_in_MCMap = read_csv_file("df_in_MCMap")
        df_in_MCLoc = read_csv_file("df_in_MCLoc")



    print_df(df_in_Param, 'STEP 1 - Input table load .....> df_in_Param')
    print_df(df_in_MatConsAsn, 'STEP 1 - Input table load .....> df_in_MatConsAsn')
    print_df(df_in_ProdAsn, 'STEP 1 - Input table load .....> df_in_ProdAsn')
    print_df(df_in_CapaConsAsn, 'STEP 1 - Input table load .....> df_in_CapaConsAsn')
    print_df(df_in_ResGrpConsAsn, 'STEP 1 - Input table load .....> df_in_ResGrpConsAsn')
    print_df(df_in_ActParam, 'STEP 1 - Input table load .....> df_in_ActParam')
    print_df(df_in_ActShare, 'STEP 1 - Input table load .....> df_in_ActShare')
    print_df(df_in_FrozenWindow, 'STEP 1 - Input table load .....> df_in_FrozenWindow')
    print_df(df_in_LotSizeParam, 'STEP 1 - Input table load .....> df_in_LotSizeParam')
    print_df(df_in_InvNodeParam, 'STEP 1 - Input table load .....> df_in_InvNodeParam')
    print_df(df_in_HolidayCal, 'STEP 1 - Input table load .....> df_in_HolidayCal')
    print_df(df_in_ResGrpPriority, 'STEP 1 - Input table load .....> df_in_ResGrpPriority')
    print_df(df_in_Demand, 'STEP 1 - Input table load .....> df_in_Demand')
    print_df(df_in_Inv, 'STEP 1 - Input table load .....> df_in_Inv')
    print_df(df_in_InvOrder, 'STEP 1 - Input table load .....> df_in_InvOrder')
    print_df(df_in_WIP, 'STEP 1 - Input table load .....> df_in_WIP')
    print_df(df_in_WIPCapa, 'STEP 1 - Input table load .....> df_in_WIPCapa')
    print_df(df_in_Capa, 'STEP 1 - Input table load .....> df_in_Capa')
    print_df(df_in_INF, 'STEP 1 - Input table load .....> df_in_INF')
    print_df(df_in_BOMCompEff, 'STEP 1 - Input table load .....> df_in_BOMCompEff')
    print_df(df_in_LPSObj, 'STEP 1 - Input table load .....> df_in_LPSObj')
    print_df(df_in_FlexCapaPriority, 'STEP 1 - Input table load .....> df_in_FlexCapaPriority')
    print_df(df_in_GSProp, 'STEP 1 - Input table load .....> df_in_GSProp')
    print_df(df_in_FlexCapa, 'STEP 1 - Input table load .....> df_in_FlexCapa')
    print_df(df_in_BODW, 'STEP 1 - Input table load .....> df_in_BODW')
    print_df(df_in_GSNode, 'STEP 1 - Input table load .....> df_in_GSNode')
    print_df(df_in_GSPriority, 'STEP 1 - Input table load .....> df_in_GSPriority')
    print_df(df_in_ItemLoc, 'STEP 1 - Input table load .....> df_in_ItemLoc')
    print_df(df_in_TactTimeW, 'STEP 1 - Input table load .....> df_in_TactTimeW')
    print_df(df_in_MCMap, 'STEP 1 - Input table load .....> df_in_MCMap')
    print_df(df_in_MCLoc, 'STEP 1 - Input table load .....> df_in_MCLoc')



    # 입력 변수 확인
    if paramOutVersion is None or paramOutVersion.strip() == '':
        paramOutVersion = PARAM_OUTVERSION_VALUE

    # input dataframe 확인용 로그
    note(f'=====> paramOutVersion : {paramOutVersion}')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 2 : DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수 선언
    VERSION_NAME_COLUMN = 'Version.[Version Name]'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 3 :  데이터 선 가공
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    df_out_Param            = df_in_Param.copy()
    df_out_MatConsAsn       = df_in_MatConsAsn.copy()
    df_out_ProdAsn          = df_in_ProdAsn.copy()
    df_out_CapaConsAsn      = df_in_CapaConsAsn.copy()
    df_out_ResGrpConsAsn    = df_in_ResGrpConsAsn.copy()
    df_out_ActParam         = df_in_ActParam.copy()
    df_out_ActShare         = df_in_ActShare.copy()
    df_out_FrozenWindow     = df_in_FrozenWindow.copy()
    df_out_LotSizeParam     = df_in_LotSizeParam.copy()
    df_out_InvNodeParam     = df_in_InvNodeParam.copy()
    df_out_HolidayCal       = df_in_HolidayCal.copy()
    df_out_ResGrpPriority   = df_in_ResGrpPriority.copy()
    df_out_Demand           = df_in_Demand.copy()
    df_out_Inv              = df_in_Inv.copy()
    df_out_InvOrder         = df_in_InvOrder.copy()
    df_out_WIP              = df_in_WIP.copy()
    df_out_WIPCapa          = df_in_WIPCapa.copy()
    df_out_Capa             = df_in_Capa.copy()
    df_out_INF              = df_in_INF.copy()
    df_out_BOMCompEff       = df_in_BOMCompEff.copy()
    df_out_LPSObj           = df_in_LPSObj.copy()
    df_out_FlexCapaPriority = df_in_FlexCapaPriority.copy()
    df_out_GSProp           = df_in_GSProp.copy()
    df_out_FlexCapa         = df_in_FlexCapa.copy()
    df_out_BODW             = df_in_BODW.copy()
    df_out_GSNode           = df_in_GSNode.copy()
    df_out_GSPriority       = df_in_GSPriority.copy()
    df_out_ItemLoc          = df_in_ItemLoc.copy()
    df_out_TactTimeW        = df_in_TactTimeW.copy()
    df_out_MCMap            = df_in_MCMap.copy()
    df_out_MCLoc            = df_in_MCLoc.copy()

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 4 : output data machining
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # 데이터 프레임 리스트
    dataframes = [
        df_out_Param,
        df_out_MatConsAsn,
        df_out_ProdAsn,
        df_out_CapaConsAsn,
        df_out_ResGrpConsAsn,
        df_out_ActParam,
        df_out_ActShare,
        df_out_FrozenWindow,
        df_out_LotSizeParam,
        df_out_InvNodeParam,
        df_out_HolidayCal,
        df_out_ResGrpPriority,
        df_out_Demand,
        df_out_Inv,
        df_out_InvOrder,
        df_out_WIP,
        df_out_WIPCapa,
        df_out_Capa,
        df_out_INF,
        df_out_BOMCompEff,
        df_out_LPSObj,
        df_out_FlexCapaPriority,
        df_out_GSProp,
        df_out_FlexCapa,
        df_out_BODW,
        df_out_GSNode,
        df_out_GSPriority,
        df_out_ItemLoc,
        df_out_TactTimeW,
        df_out_MCMap,
        df_out_MCLoc,
    ]

    # 반복문을 통한 설정
    for df in dataframes:
        df[VERSION_NAME_COLUMN] = paramOutVersion

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 5 : output table create
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : Final output table create')

    note(f'=====> Final output table create')

    print_df(df_in_Param, 'STEP 5 - Output table .....> df_out_Param')
    print_df(df_in_MatConsAsn, 'STEP 5 - Output table .....> df_out_MatConsAsn')
    print_df(df_in_ProdAsn, 'STEP 5 - Output table .....> df_out_ProdAsn')
    print_df(df_in_CapaConsAsn, 'STEP 5 - Output table .....> df_out_CapaConsAsn')
    print_df(df_in_ResGrpConsAsn, 'STEP 5 - Output table .....> df_out_ResGrpConsAsn')
    print_df(df_in_ActParam, 'STEP 5 - Output table .....> df_out_ActParam')
    print_df(df_in_ActShare, 'STEP 5 - Output table .....> df_out_ActShare')
    print_df(df_in_FrozenWindow, 'STEP 5 - Output table .....> df_out_FrozenWindow')
    print_df(df_in_LotSizeParam, 'STEP 5 - Output table .....> df_out_LotSizeParam')
    print_df(df_in_InvNodeParam, 'STEP 5 - Output table .....> df_out_InvNodeParam')
    print_df(df_in_HolidayCal, 'STEP 5 - Output table .....> df_out_HolidayCal')
    print_df(df_in_ResGrpPriority, 'STEP 5 - Output table .....> df_out_ResGrpPriority')
    print_df(df_in_Demand, 'STEP 5 - Output table .....> df_out_Demand')
    print_df(df_in_Inv, 'STEP 5 - Output table .....> df_out_Inv')
    print_df(df_in_InvOrder, 'STEP 5 - Output table .....> df_out_InvOrder')
    print_df(df_in_WIP, 'STEP 5 - Output table .....> df_out_WIP')
    print_df(df_in_WIPCapa, 'STEP 5 - Output table .....> df_out_WIPCapa')
    print_df(df_in_Capa, 'STEP 5 - Output table .....> df_out_Capa')
    print_df(df_in_INF, 'STEP 5 - Output table .....> df_out_INF')
    print_df(df_in_BOMCompEff, 'STEP 5 - Output table .....> df_out_BOMCompEff')
    print_df(df_in_LPSObj, 'STEP 5 - Output table .....> df_out_LPSObj')
    print_df(df_in_FlexCapaPriority, 'STEP 5 - Output table .....> df_out_FlexCapaPriority')
    print_df(df_in_GSProp, 'STEP 5 - Output table .....> df_out_GSProp')
    print_df(df_in_FlexCapa, 'STEP 5 - Output table .....> df_out_FlexCapa')
    print_df(df_in_BODW, 'STEP 5 - Output table .....> df_out_BODW')
    print_df(df_in_GSNode, 'STEP 5 - Output table .....> df_out_GSNode')
    print_df(df_in_GSPriority, 'STEP 5 - Output table .....> df_out_GSPriority')
    print_df(df_in_ItemLoc, 'STEP 5 - Output table .....> df_out_ItemLoc')
    print_df(df_in_TactTimeW, 'STEP 5 - Output table .....> df_out_TactTimeW')
    print_df(df_in_MCMap, 'STEP 5 - Output table .....> df_out_MCMap')
    print_df(df_in_MCLoc, 'STEP 5 - Output table .....> df_out_MCLoc')

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as ex:
    note(f'An exception occurred: {ex}')
    note(f'=====> try exception : {traceback.format_exc()}')
    logger.Error()

else:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    end_time = time.time()
    run_time_seconds = end_time - start_time
    run_time_minutes = run_time_seconds / 60

    note(f'=====> Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB, Execution time: {run_time_minutes:.4f} minutes')
    step(600, '===================== plugin Execution End =====================')

finally:
    logger.Finish()
