"""
* 프로그램명
    - PY_MG_DemandBAL

* 내용
    - Demand BAL UI에서 입력한 선행일수 Update

* 변경이력
    - 2024.10.15 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_Demand          : Select (&MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({ Measure.[W Demand Build Ahead Limit], Measure.[W Demand Build Ahead Limit UOM]}) on column;
    - df_in_Item            : Select (&SETItem * [Item].[Project] * [Item].[Product Group] * [Item].[Inch] * [Item].[Definition] * [Item].[Year] * [Item].[Marketing Name]);
    - df_in_BAL_ProductGrp  : Select (&MPV * [Item].[Product Group] * [Location].[Location] * [Sub Location].[Sub Location] ) on row, ({ Measure.[Build Ahead Prod_Valid]}) on column.filter(Measure.[Build Ahead Prod_Valid]== "Y");
    - df_in_BAL_ProductGrpW : Select (&MPV * [Item].[Product Group] * &PlanningHorizon *  [Location].[Location] * [Sub Location].[Sub Location] ) on row, ({Measure.[Build Ahead Prod W_Period]}) on column;
    - df_in_BAL_Item        : Select (&MPV * [Group].[Group ID] ) on row, ({Measure.[Build Ahead Item_Definition], Measure.[Build Ahead Item_Description], Measure.[Build Ahead Item_From Site], Measure.[Build Ahead Item_Inch], Measure.[Build Ahead Item_Item], Measure.[Build Ahead Item_MKT Name], Measure.[Build Ahead Item_Product Group], Measure.[Build Ahead Item_Project], Measure.[Build Ahead Item_To Site],Measure.[Build Ahead Item_Year]}) on column;
    - df_in_BAL_ItemW       : Select (&MPV * [Time].[Week] * [Group].[Group ID] ) on row, ({Measure.[Build Ahead Item W_Period]}) on column;
    - df_in_BAL_Item_Ecp    : Select (&MPV * [Item].[Item] * [Group].[Group ID] ) on row, ({Measure.[Build Ahead Item Ecp_Flag]}) on column.filter(Measure.[Build Ahead Item Ecp_Flag]== true);
    - df_in_BODList         : Select (&MPV * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Valid] }) on column.filter(Measure.[BOD List_BOD Valid] == "Y");
    - df_in_BODItem         : Select (&MPV * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD LT],   Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Shipment LT] }) on column.filter((isnull(Measure.[BOD Item_Eff Enddate])||Measure.[BOD Item_Eff Enddate]> Measure.[W Plan Start Date]) &&(isnull(Measure.[BOD Item_Eff Startdate])||Measure.[BOD Item_Eff Startdate]< Measure.[W Plan End Date]));
    - df_in_BODItemW        : Select (&MPV * [Item].[Item] * &PlanningHorizon  * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item W_Ship LT], Measure.[BOD Item W_Tran Time]}) on column;
    - df_in_PlanningWeek    : Select (&PlanningHorizon ) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};

* Flow Summary
    - STEP1. df_ProductGrpBAL Set 구성
    - STEP2. df_bod  Set  구성
    - STEP3. df_ProductGrpBAL_BOD Set  구성
    - STEP4. df_GroupBAL  SET 구성
    - STEP5. df_GroupItemBAL  SET 구성
    - STEP6. df_GroupBAL_BOD SET 생성
    - STEP7. df_MinBAL Set 구성
    - STEP8. Demand 테이블에 W Demand Build Ahead Limit Update

* Output Table
    - df_out_Demand

* 데이타 초기화
    - DELETE DATA FOR MODEL [SOP Frozen List] where {Version.[Version Name].filter(#.Name in {"CWV_MP","CurrentWorkingView"})};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_DemandBAL] for Measures {Measure.[W Demand Build Ahead Limit]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - MG: 001.018W Solver Inputs Demand Time Granularity
        Select ( &MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row,
            ({Measure.[W Demand Build Ahead Limit], Measure.[W Demand Build Ahead Limit UOM]}) on column;
"""
import gc
import traceback
import time
import numpy as np
import pandas as pd
import tracemalloc
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_DemandBAL'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
COMMON_SOURCE_VERSION = common.G_SourceVersion


########################################################################################################################
# 내부함수
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(f"{file_name}.csv", index=False)


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    logger.Step(p_step_no=no, p_step_desc=f'{string}')


def create_message(df, step_description):
    # DataFrame이 비어 있는지 확인하고 메시지 생성
    empty_status = "is empty" if df.empty else ""
    return f"{step_description} {empty_status}"



########################################################################################################################
# logic start
########################################################################################################################
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

    # csv 파일 이름과 변수명을 매핑한 딕셔너리 생성
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_Demand = read_csv_file("df_in_Demand")
        df_in_Item = read_csv_file("df_in_Item")
        df_in_BAL_ProductGrp = read_csv_file("df_in_BAL_ProductGrp")
        df_in_BAL_ProductGrpW = read_csv_file("df_in_BAL_ProductGrpW")
        df_in_BAL_Item = read_csv_file("df_in_BAL_Item")
        df_in_BAL_ItemW = read_csv_file("df_in_BAL_ItemW")
        df_in_BAL_Item_Ecp = read_csv_file("df_in_BAL_Item_Ecp")
        df_in_BODList = read_csv_file("df_in_BODList")
        df_in_BODItem = read_csv_file("df_in_BODItem")
        df_in_BODItemW = read_csv_file("df_in_BODItemW")
        df_in_PlanningWeek = read_csv_file("df_in_PlanningWeek")


    print_df(df_in_Demand, create_message(df_in_Demand, 'STEP 1 - Input table load .....> df_in_Demand'))
    print_df(df_in_Item, create_message(df_in_Item, 'STEP 1 - Input table load .....> df_in_Item'))
    print_df(df_in_BAL_ProductGrp, create_message(df_in_BAL_ProductGrp, 'STEP 1 - Input table load .....> df_in_BAL_ProductGrp'))
    print_df(df_in_BAL_ProductGrpW, create_message(df_in_BAL_ProductGrpW, 'STEP 1 - Input table load .....> df_in_BAL_ProductGrpW'))
    print_df(df_in_BAL_Item, create_message(df_in_BAL_Item, 'STEP 1 - Input table load .....> df_in_BAL_Item'))
    print_df(df_in_BAL_ItemW, create_message(df_in_BAL_ItemW, 'STEP 1 - Input table load .....> df_in_BAL_ItemW'))
    print_df(df_in_BAL_Item_Ecp, create_message(df_in_BAL_Item_Ecp, 'STEP 1 - Input table load .....> df_in_BAL_Item_Ecp'))
    print_df(df_in_BODList, create_message(df_in_BODList, 'STEP 1 - Input table load .....> df_in_BODList'))
    print_df(df_in_BODItem, create_message(df_in_BODItem, 'STEP 1 - Input table load .....> df_in_BODItem'))
    print_df(df_in_BODItemW, create_message(df_in_BODItemW, 'STEP 1 - Input table load .....> df_in_BODItemW'))
    print_df(df_in_PlanningWeek, create_message(df_in_PlanningWeek, 'STEP 1 - Input table load .....> df_in_PlanningWeek'))


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

    LOCATION_COLUMN = 'Location.[Location]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'

    GROUP_ID_COLUMN = 'Group.[Group ID]'
    ITEM_COLUMN = 'Item.[Item]'
    ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
    ITEM_PROJECT_COLUMN = 'Item.[Project]'
    ITEM_INCH_COLUMN = 'Item.[Inch]'
    ITEM_DEFINITION_COLUMN = 'Item.[Definition]'
    ITEM_YEAR_COLUMN = 'Item.[Year]'
    ITEM_MARKETING_NAME_COLUMN = 'Item.[Marketing Name]'
    TIME_WEEK_COLUMN = 'Time.[Week]'
    TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'

    BOD_ITEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
    BOD_ITEM_EFF_ENDDATE_COLUMN = 'BOD Item_Eff Enddate'
    BOD_ITEM_EFF_STARTDATE_COLUMN = 'BOD Item_Eff Startdate'
    BOD_ITEM_SHIPMENT_LT_COLUMN = 'BOD Item_Shipment LT'
    BOD_ITEM_W_SHIP_LT_COLUMN = 'BOD Item W_Ship LT'
    BOD_ITEM_W_TRAN_TIME_COLUMN = 'BOD Item W_Tran Time'
    BOD_ITEM_BOD_VAILD_COLUMN = 'BOD List_BOD Valid'

    BUILD_AHEAD_ITEM_DEFINITION_COLUMN = 'Build Ahead Item_Definition'
    BUILD_AHEAD_ITEM_DESCRIPTION_COLUMN = 'Build Ahead Item_Description'
    BUILD_AHEAD_ITEM_FROM_SIE_COLUMN = 'Build Ahead Item_From Site'
    BUILD_AHEAD_ITEM_INCH_COLUMN = 'Build Ahead Item_Inch'
    BUILD_AHEAD_ITEM_ITEM_COLUMN = 'Build Ahead Item_Item'
    BUILD_AHEAD_ITEM_MKT_NAME_COLUMN = 'Build Ahead Item_MKT Name'
    BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN = 'Build Ahead Item_Product Group'
    BUILD_AHEAD_ITEM_PROJECT_COLUMN = 'Build Ahead Item_Project'
    BUILD_AHEAD_ITEM_TO_SITE_COLUMN = 'Build Ahead Item_To Site'
    BUILD_AHEAD_ITEM_YEAR_COLUMN = 'Build Ahead Item_Year'
    BUILD_AHEAD_ITEM_ECP_FLAG_COLUMN = 'Build Ahead Item Ecp_Flag'
    BUILD_AHEAD_ITEM_W_PERIOD_COLUMN = 'Build Ahead Item W_Period'
    BUILD_AHEAD_PROD_VAILD_COLUMN = 'Build Ahead Prod_Valid'
    BUILD_AHEAD_PROD_W_PERIOD_COLUMN = 'Build Ahead Prod W_Period'

    SALES_DOMAIN_CUSTOEMR_GROUP_COLUMN = 'Sales Domain.[Customer Group]'
    DEMAND_TYPE_COLUMN = 'Demand Type.[Demand Type]'
    DEMAND_ID_COLUMN = 'Demand.[DemandID]'
    W_DEMAND_BUILD_AHEAD_LIMIT_COLUMN = 'W Demand Build Ahead Limit'
    W_DEMAND_BUILD_AHEAD_LIMIT_UOM_COLUMN = 'W Demand Build Ahead Limit UOM'

    BOD_SHIPMENT_LT_COLUMN = 'BOD_Shipment LT'
    BOD_TRANSIT_COLUMN = 'BOD_Transit'

    SOP_WEEK_COLUMN = 'sopweek'
    BOD_LT_COLUMN = 'bod LT'
    
    ALL_VALUE = 'ALL'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 3 :  데이터 선 가공
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    # ====================> Step 0 (Start) > 사전작업

    # 0.1 df_in_PlanningWeek . 'week' 만 발췌
    df_PlanningWeek = df_in_PlanningWeek[[TIME_WEEK_COLUMN]].copy()
    df_PlanningWeek['key'] = 1

    df_Demand = df_in_Demand[[ITEM_COLUMN, LOCATION_COLUMN]].copy().drop_duplicates()

    # ====================> Step 0 (End)




    # ====================> Step 1-1 (Start) > df_iteminfo Set 구성

    df_DemandItem = df_in_Demand.copy()
    df_DemandItem = df_Demand[[ITEM_COLUMN]].drop_duplicates()
    df_iteminfo = pd.merge(df_DemandItem, df_in_Item, how='inner', on=[ITEM_COLUMN])
    print_df(df_iteminfo, 'STEP3 by 1-1 ____ df_iteminfo ..... merge')

    # ====================> Step 1-1 (End)




    # ====================> Step 1-2 (Start) > df_ProductGrpBAL Set 구성

    # 1-2.1 productset create
    #   1-2.1.1 join
    df_buf_productset = pd.merge(df_in_BAL_ProductGrp, df_in_BAL_ProductGrpW, how='inner',
                                 on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN]).drop_duplicates()
    print_df(df_buf_productset, 'STEP3 by 1-2.1.1 ____ df_buf_productset ..... merge')

    #   1-2.1.2 df_productset create
    df_productset = pd.merge(df_buf_productset, df_iteminfo, how='inner', on=[ITEM_PRODUCT_GROUP_COLUMN]).drop_duplicates()
    print_df(df_productset, 'STEP3 by 1-2.1.2 ____ df_productset ..... merge')

    #   1-2.1.3 필요컬럼 발췌
    df_productset = df_productset[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_productset, 'STEP3 by 1-2.1 ____ df_productset ..... final')


    # 1-2.2 ProductSetWeek create
    #   1-2.2.1 df_productset 에서 필요컬럼만 복사
    df_buf_productset =  df_productset[[
        ITEM_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN
    ]].copy().drop_duplicates()
    print_df(df_buf_productset, 'STEP3 by 1-2.2.1 ____ df_buf_productset ..... column copy')

    #   1.2.2 week cartesion join
    df_buf_productset['key'] = 1
    df_ProductSetWeek = pd.merge(df_buf_productset, df_PlanningWeek, how='outer', on='key')
    df_ProductSetWeek.drop(columns=['key'], inplace=True)
    print_df(df_ProductSetWeek, 'STEP3 by 1-2.2 ____ df_ProductSetWeek ..... final')


    # 1-2.3 df_ProductGrpBAL create
    #   1-2.3.1
    df_ProductGrpBAL = pd.merge(df_ProductSetWeek, df_productset, how='left',
                                left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN],
                                right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN])
    print_df(df_ProductGrpBAL, 'STEP3 by 1-2.3.1 ____ df_ProductGrpBAL ..... merge')

    #   1-2.3.2 컬럼설정 및 필요컬럼 발췌
    df_ProductGrpBAL[BUILD_AHEAD_PROD_W_PERIOD_COLUMN] = np.where(
        df_ProductGrpBAL[BUILD_AHEAD_PROD_W_PERIOD_COLUMN].isnull(), None, df_ProductGrpBAL[BUILD_AHEAD_PROD_W_PERIOD_COLUMN]
    )

    #   1-2.3.3
    df_ProductGrpBAL =  df_ProductGrpBAL[[
        ITEM_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_ProductGrpBAL, 'STEP3 by 1-2 ____ df_ProductGrpBAL ..... final')
    # save_csv_file(df_ProductGrpBAL, 'STEP3 by 1-2 ____ df_ProductGrpBAL ..... final')

    # ====================> Step 1 (End)




    # ====================> Step 2 (Start) > df_bod Set 구성

    # 2.1 bod
    #   2.1.1 df_buf_bod create
    df_buf_bod_1 = pd.merge(df_in_BODList, df_in_BODItem, how='inner',
                            on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN])
    print_df(df_buf_bod_1, 'STEP3 by 2.1.1 ____ df_buf_bod_1 ..... merge')
    # save_csv_file(df_buf_bod_1, 'STEP3 by 2.1.1 ____ df_buf_bod_1 ..... merge')

    #   2.1.2 df_bod create
    df_buf_bod_2 = pd.merge(df_buf_bod_1, df_Demand, how='inner',
                            left_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN],
                            right_on=[ITEM_COLUMN, LOCATION_COLUMN])
    print_df(df_buf_bod_2, 'STEP3 by 2.1.2 ____ df_buf_bod_2 ..... merge')
    # save_csv_file(df_buf_bod_2, 'STEP3 by 2.1.2 ____ df_buf_bod_2 ..... merge')

    #   2.1.3 컬럼 설정,발췌
    df_buf_bod_2.rename(columns={LOCATION_COLUMN+'_x': LOCATION_COLUMN}, inplace=True)
    df_buf_bod_2 = df_buf_bod_2[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, BOD_ITEM_BOD_LT_COLUMN, BOD_ITEM_SHIPMENT_LT_COLUMN
    ]].drop_duplicates()
    print_df(df_buf_bod_2, 'STEP3 by 2.1 ____ df_buf_bod_2 ..... final')


    # 2.2 bodinfo
    #   2.2.1 df_bodinfo create
    df_buf_bod_2['key'] = 1
    df_bodinfo = pd.merge(df_PlanningWeek, df_buf_bod_2, how='outer', on='key')
    df_bodinfo.drop(columns=['key'], inplace=True)
    print_df(df_bodinfo, 'STEP3 by 2.2.1 ____ df_bodinfo ..... merge')


    #   2.2.2 df_bod set create
    df_bod = pd.merge(df_bodinfo, df_in_BODItemW, how='left', on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                                                                  TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
    print_df(df_bod, 'STEP3 by 2.2.2 ____ df_bod ..... merge')

    #   2.2.3 컬럼설정 및 필요컬럼 발췌
    df_bod[BOD_SHIPMENT_LT_COLUMN] = np.where(
        df_bod[BOD_ITEM_W_SHIP_LT_COLUMN].isnull(), df_bod[BOD_ITEM_SHIPMENT_LT_COLUMN] / 7, df_bod[BOD_ITEM_W_SHIP_LT_COLUMN] / 7
    )

    df_bod[BOD_TRANSIT_COLUMN] = np.where(
        df_bod[BOD_ITEM_W_TRAN_TIME_COLUMN].isnull(), df_bod[BOD_ITEM_BOD_LT_COLUMN] / 7, df_bod[BOD_ITEM_W_TRAN_TIME_COLUMN] / 7
    )

    #   2.2.4
    df_bod = df_bod[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN, BOD_SHIPMENT_LT_COLUMN, BOD_TRANSIT_COLUMN,
    ]].drop_duplicates()
    print_df(df_bod, 'STEP3 by 2 ____ df_bod ..... final')
    # save_csv_file(df_bod, 'STEP3 by 2 ____ df_bod ..... final')

    # ====================> Step 2 (End)




    # ====================> Step 3 (Start) > df_ProductGrpBAL_BOD Set  구성

    # 3.1 df_ProductGrpBAL_BOD_1 set create
    #   3.1.1 df_ProductGrpBAL_BOD_1
    df_ProductGrpBAL_BOD_1 = df_ProductGrpBAL[(df_ProductGrpBAL[LOCATION_COLUMN].str.upper() == ALL_VALUE) &
                                              (df_ProductGrpBAL[SUB_LOCATION_COLUMN].str.upper() != ALL_VALUE)].copy()
    print_df(df_ProductGrpBAL_BOD_1, 'STEP3 by 3.1.1 ____ df_ProductGrpBAL_BOD_1 ..... ALL filter')
    # save_csv_file(df_ProductGrpBAL_BOD_1, 'STEP3 by 3.1.1 ____ df_ProductGrpBAL_BOD_1 ..... ALL filter')

    df_ProductGrpBAL_BOD_1 = df_ProductGrpBAL_BOD_1.merge(df_bod, how='inner', on=[SUB_LOCATION_COLUMN, ITEM_COLUMN])
    print_df(df_ProductGrpBAL_BOD_1, 'STEP3 by 3.1.1 ____ df_ProductGrpBAL_BOD_1 ..... merge')

    #   3.1.2 컬럼설정
    df_ProductGrpBAL_BOD_1.rename(columns={LOCATION_COLUMN+'_y': LOCATION_COLUMN,
                                           TIME_WEEK_COLUMN+'_y': TIME_WEEK_COLUMN,
                                           }, inplace=True)
    df_ProductGrpBAL_BOD_1[TIME_WEEK_COLUMN] = df_ProductGrpBAL_BOD_1[TIME_WEEK_COLUMN].fillna(0).astype('Int64')
    print_df(df_ProductGrpBAL_BOD_1, 'STEP3 by 3.1.1 ____ df_ProductGrpBAL_BOD_1 ..... merge final')

    num_columns = [BOD_SHIPMENT_LT_COLUMN, BOD_TRANSIT_COLUMN]
    for col in num_columns:
        df_ProductGrpBAL_BOD_1[col] = pd.to_numeric(df_ProductGrpBAL_BOD_1[col], errors='coerce')
        df_ProductGrpBAL_BOD_1[col] = df_ProductGrpBAL_BOD_1[col].fillna(0).astype('float')

    df_ProductGrpBAL_BOD_1[SOP_WEEK_COLUMN] = (df_ProductGrpBAL_BOD_1[TIME_WEEK_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_1[BOD_SHIPMENT_LT_COLUMN].fillna(0) +
                                               df_ProductGrpBAL_BOD_1[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_1[BOD_LT_COLUMN] = (df_ProductGrpBAL_BOD_1[BOD_SHIPMENT_LT_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_1[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_1 = df_ProductGrpBAL_BOD_1[df_ProductGrpBAL_BOD_1[TIME_WEEK_COLUMN] == df_ProductGrpBAL_BOD_1[SOP_WEEK_COLUMN]]

    df_ProductGrpBAL_BOD_1 =  df_ProductGrpBAL_BOD_1[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_ProductGrpBAL_BOD_1, 'STEP3 by 3.1 ____ df_ProductGrpBAL_BOD_1 ..... final')


    # 3.2 df_ProductGrpBAL_BOD_2 set create
    #   3.2.1 df_ProductGrpBAL_BOD_2
    df_ProductGrpBAL_BOD_2 = df_ProductGrpBAL[(df_ProductGrpBAL[SUB_LOCATION_COLUMN].str.upper() == ALL_VALUE) &
                                              (df_ProductGrpBAL[LOCATION_COLUMN].str.upper() == ALL_VALUE)].copy()
    print_df(df_ProductGrpBAL_BOD_2, 'STEP3 by 3.2.1 ____ df_ProductGrpBAL_BOD_2 ..... ALL filter')
    # save_csv_file(df_ProductGrpBAL_BOD_2, 'STEP3 by 3.2.1 ____ df_ProductGrpBAL_BOD_2 ..... ALL filter')

    df_ProductGrpBAL_BOD_2 = df_ProductGrpBAL_BOD_2.merge(df_bod, how='inner', on=[LOCATION_COLUMN, ITEM_COLUMN])
    print_df(df_ProductGrpBAL_BOD_2, 'STEP3 by 3.2.1 ____ df_ProductGrpBAL_BOD_2 ..... merge')

    #   3.2.2 컬럼설정
    df_ProductGrpBAL_BOD_2.rename(columns={SUB_LOCATION_COLUMN+'_y': SUB_LOCATION_COLUMN,
                                           TIME_WEEK_COLUMN+'_y': TIME_WEEK_COLUMN,
                                           }, inplace=True)
    df_ProductGrpBAL_BOD_2[TIME_WEEK_COLUMN] = df_ProductGrpBAL_BOD_2[TIME_WEEK_COLUMN].fillna(0).astype('Int64')
    print_df(df_ProductGrpBAL_BOD_2, 'STEP3 by 3.2.1 ____ df_ProductGrpBAL_BOD_2 ..... merge final')

    num_columns = [BOD_SHIPMENT_LT_COLUMN, BOD_TRANSIT_COLUMN]
    for col in num_columns:
        df_ProductGrpBAL_BOD_2[col] = pd.to_numeric(df_ProductGrpBAL_BOD_2[col], errors='coerce')
        df_ProductGrpBAL_BOD_2[col] = df_ProductGrpBAL_BOD_2[col].fillna(0).astype('float')

    df_ProductGrpBAL_BOD_2[SOP_WEEK_COLUMN] = (df_ProductGrpBAL_BOD_2[TIME_WEEK_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_2[BOD_SHIPMENT_LT_COLUMN].fillna(0) +
                                               df_ProductGrpBAL_BOD_2[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_2[BOD_LT_COLUMN] = (df_ProductGrpBAL_BOD_2[BOD_SHIPMENT_LT_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_2[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_2 = df_ProductGrpBAL_BOD_2[df_ProductGrpBAL_BOD_2[TIME_WEEK_COLUMN] == df_ProductGrpBAL_BOD_2[SOP_WEEK_COLUMN]]

    df_ProductGrpBAL_BOD_2 =  df_ProductGrpBAL_BOD_2[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_ProductGrpBAL_BOD_2, 'STEP3 by 3.2 ____ df_ProductGrpBAL_BOD_2 ..... final')


    # 3.3 df_ProductGrpBAL_BOD_3 set create
    #   3.3.1 df_ProductGrpBAL_BOD_3
    df_ProductGrpBAL_BOD_3 = df_ProductGrpBAL[(df_ProductGrpBAL[SUB_LOCATION_COLUMN].str.upper() == ALL_VALUE) &
                                              (df_ProductGrpBAL[LOCATION_COLUMN].str.upper() == ALL_VALUE)].copy()
    print_df(df_ProductGrpBAL_BOD_3, 'STEP3 by 3.3.1 ____ df_ProductGrpBAL_BOD_3 ..... ALL filter')
    # save_csv_file(df_ProductGrpBAL_BOD_3, 'STEP3 by 3.3.1 ____ df_ProductGrpBAL_BOD_3 ..... ALL filter')

    df_ProductGrpBAL_BOD_3 = df_ProductGrpBAL_BOD_3.merge(df_bod, how='inner', on=[ITEM_COLUMN])
    print_df(df_ProductGrpBAL_BOD_3, 'STEP3 by 3.3.1 ____ df_ProductGrpBAL_BOD_3 ..... merge')

    #   3.3.2 컬럼설정
    df_ProductGrpBAL_BOD_3.rename(columns={LOCATION_COLUMN+'_y': LOCATION_COLUMN,
                                           SUB_LOCATION_COLUMN+'_y': SUB_LOCATION_COLUMN,
                                           TIME_WEEK_COLUMN+'_y': TIME_WEEK_COLUMN,
                                           }, inplace=True)
    df_ProductGrpBAL_BOD_3[TIME_WEEK_COLUMN] = df_ProductGrpBAL_BOD_3[TIME_WEEK_COLUMN].fillna(0).astype('Int64')
    print_df(df_ProductGrpBAL_BOD_3, 'STEP3 by 3.3.1 ____ df_ProductGrpBAL_BOD_3 ..... merge final')

    num_columns = [BOD_SHIPMENT_LT_COLUMN, BOD_TRANSIT_COLUMN]
    for col in num_columns:
        df_ProductGrpBAL_BOD_3[col] = pd.to_numeric(df_ProductGrpBAL_BOD_3[col], errors='coerce')
        df_ProductGrpBAL_BOD_3[col] = df_ProductGrpBAL_BOD_3[col].fillna(0).astype('float')

    df_ProductGrpBAL_BOD_3[SOP_WEEK_COLUMN] = (df_ProductGrpBAL_BOD_3[TIME_WEEK_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_3[BOD_SHIPMENT_LT_COLUMN].fillna(0) +
                                               df_ProductGrpBAL_BOD_3[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_3[BOD_LT_COLUMN] = (df_ProductGrpBAL_BOD_3[BOD_SHIPMENT_LT_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_3[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_3 = df_ProductGrpBAL_BOD_3[df_ProductGrpBAL_BOD_3[TIME_WEEK_COLUMN] == df_ProductGrpBAL_BOD_3[SOP_WEEK_COLUMN]]

    df_ProductGrpBAL_BOD_3 =  df_ProductGrpBAL_BOD_3[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_ProductGrpBAL_BOD_3, 'STEP3 by 3.3 ____ df_ProductGrpBAL_BOD_3 ..... final')


    # 3.4 df_ProductGrpBAL_BOD_4 set create
    #   3.4.1 df_ProductGrpBAL_BOD_4
    df_ProductGrpBAL_BOD_4 = df_ProductGrpBAL[(df_ProductGrpBAL[SUB_LOCATION_COLUMN].str.upper() != ALL_VALUE) &
                                              (df_ProductGrpBAL[LOCATION_COLUMN].str.upper() != ALL_VALUE)].copy()
    print_df(df_ProductGrpBAL_BOD_4, 'STEP3 by 3.4.1 ____ df_ProductGrpBAL_BOD_4 ..... ALL filter')
    # save_csv_file(df_ProductGrpBAL_BOD_4, 'STEP3 by 3.4.1 ____ df_ProductGrpBAL_BOD_4 ..... ALL filter')

    df_ProductGrpBAL_BOD_4 = df_ProductGrpBAL_BOD_4.merge(df_bod, how='inner', on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN,
                                                                                   ITEM_COLUMN])
    print_df(df_ProductGrpBAL_BOD_4, 'STEP3 by 3.4.1 ____ df_ProductGrpBAL_BOD_4 ..... merge')

    #   3.4.2 컬럼설정
    df_ProductGrpBAL_BOD_4.rename(columns={LOCATION_COLUMN+'_y': LOCATION_COLUMN,
                                           SUB_LOCATION_COLUMN+'_y': SUB_LOCATION_COLUMN,
                                           TIME_WEEK_COLUMN+'_y': TIME_WEEK_COLUMN,
                                           }, inplace=True)
    df_ProductGrpBAL_BOD_4[TIME_WEEK_COLUMN] = df_ProductGrpBAL_BOD_4[TIME_WEEK_COLUMN].fillna(0).astype('Int64')
    print_df(df_ProductGrpBAL_BOD_4, 'STEP3 by 3.4.1 ____ df_ProductGrpBAL_BOD_4 ..... merge final')

    num_columns = [BOD_SHIPMENT_LT_COLUMN, BOD_TRANSIT_COLUMN]
    for col in num_columns:
        df_ProductGrpBAL_BOD_4[col] = pd.to_numeric(df_ProductGrpBAL_BOD_4[col], errors='coerce')
        df_ProductGrpBAL_BOD_4[col] = df_ProductGrpBAL_BOD_4[col].fillna(0).astype('float')

    df_ProductGrpBAL_BOD_4[SOP_WEEK_COLUMN] = (df_ProductGrpBAL_BOD_4[TIME_WEEK_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_4[BOD_SHIPMENT_LT_COLUMN].fillna(0) +
                                               df_ProductGrpBAL_BOD_4[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_4[BOD_LT_COLUMN] = (df_ProductGrpBAL_BOD_4[BOD_SHIPMENT_LT_COLUMN].fillna(0) + df_ProductGrpBAL_BOD_4[BOD_TRANSIT_COLUMN].fillna(0))

    df_ProductGrpBAL_BOD_4 = df_ProductGrpBAL_BOD_4[df_ProductGrpBAL_BOD_4[TIME_WEEK_COLUMN] == df_ProductGrpBAL_BOD_4[SOP_WEEK_COLUMN]]

    df_ProductGrpBAL_BOD_4 =  df_ProductGrpBAL_BOD_4[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_ProductGrpBAL_BOD_4, 'STEP3 by 3.4 ____ df_ProductGrpBAL_BOD_4 ..... final')


    # 3.5 모든 데이터프레임을 concat
    #   3.5.1  df_ProductGrpBAL_BOD create
    df_ProductGrpBAL_BOD = pd.concat([df_ProductGrpBAL_BOD_1, df_ProductGrpBAL_BOD_2, df_ProductGrpBAL_BOD_3, df_ProductGrpBAL_BOD_4])

    #   3.5.2 각 컬럼명 정리
    df_ProductGrpBAL_BOD = df_ProductGrpBAL_BOD[[
        LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SOP_WEEK_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN
    ]].drop_duplicates()

    #   3.5.3 그룹핑과 최소값 계산 수행
    df_ProductGrpBAL_BOD = df_ProductGrpBAL_BOD.groupby([LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SOP_WEEK_COLUMN],
                                                        as_index=False).agg({BUILD_AHEAD_PROD_W_PERIOD_COLUMN: 'min'})

    print_df(df_ProductGrpBAL_BOD, 'STEP3 by 3 ____ df_ProductGrpBAL_BOD ..... final')

    # ====================> Step  (End)



    # ====================> Step 4 (Start) > df_GroupBAL SET 구성

    # 4.1 df_GroupBAL set
    #   4.1.1 df_GroupBAL create
    df_GroupBAL = pd.merge(df_in_BAL_Item, df_in_BAL_ItemW, how='inner', on=[GROUP_ID_COLUMN])
    print_df(df_GroupBAL, 'STEP3 by 4.1.1 ____ df_GroupBAL ..... merge')

    df_GroupBAL[LOCATION_COLUMN] = df_GroupBAL[BUILD_AHEAD_ITEM_FROM_SIE_COLUMN]
    df_GroupBAL[SUB_LOCATION_COLUMN] = df_GroupBAL[BUILD_AHEAD_ITEM_TO_SITE_COLUMN]

    df_GroupBAL =  df_GroupBAL[[
        GROUP_ID_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN,
        BUILD_AHEAD_ITEM_DEFINITION_COLUMN, BUILD_AHEAD_ITEM_FROM_SIE_COLUMN, BUILD_AHEAD_ITEM_INCH_COLUMN,
        BUILD_AHEAD_ITEM_ITEM_COLUMN, BUILD_AHEAD_ITEM_MKT_NAME_COLUMN, BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN,
        BUILD_AHEAD_ITEM_PROJECT_COLUMN, BUILD_AHEAD_ITEM_TO_SITE_COLUMN, BUILD_AHEAD_ITEM_YEAR_COLUMN,
        BUILD_AHEAD_ITEM_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_GroupBAL, 'STEP3 by 4 ____ df_GroupBAL ..... final')
    # save_csv_file(df_GroupBAL, 'STEP3 by 4 ____ df_GroupBAL ..... final')

    # ====================> Step 4 (End)




    # ====================> Step 5 (Start) > df_GroupItemBAL SET 구성

    # 5.1 df_GroupItemBAL1
    #   5.1.1 join
    df_merged = df_GroupBAL.merge(df_iteminfo, how='inner',
                                  left_on=[BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN], right_on=[ITEM_PRODUCT_GROUP_COLUMN])
    print_df(df_merged, 'STEP3 by 5.1.1 ____ df_merged ..... merge')
    # save_csv_file(df_merged, 'STEP3 by 5.1.1 ____ df_merged ..... merge')

    #   5.1.2 조건 filter
    df_filtered = df_merged[
        ((df_merged[BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN] == df_merged[ITEM_PRODUCT_GROUP_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_DEFINITION_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_DEFINITION_COLUMN] == df_merged[ITEM_DEFINITION_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_PROJECT_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_PROJECT_COLUMN] == df_merged[ITEM_PROJECT_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_MKT_NAME_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_MKT_NAME_COLUMN] == df_merged[ITEM_MARKETING_NAME_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_INCH_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_INCH_COLUMN] == df_merged[ITEM_INCH_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_ITEM_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_ITEM_COLUMN] == df_merged[ITEM_COLUMN])) &
        ((~df_merged[BUILD_AHEAD_ITEM_ITEM_COLUMN].str.contains('%', na=False)))
        ].copy()

    exists_condition = df_filtered.merge(df_in_BAL_Item_Ecp, how='outer', indicator=True,
                                         left_on=[GROUP_ID_COLUMN, BUILD_AHEAD_ITEM_ITEM_COLUMN],
                                         right_on=[GROUP_ID_COLUMN, ITEM_COLUMN],)
    df_GroupItemBAL1 = exists_condition[(~exists_condition['_merge'].eq('both')) & (exists_condition[TIME_WEEK_COLUMN].notnull())].copy()
    # save_csv_file(df_GroupItemBAL1, 'STEP3 by 5.1.2 ____ df_GroupItemBAL1 ..... exists_condition')
    df_GroupItemBAL1[TIME_WEEK_COLUMN] = df_GroupItemBAL1[TIME_WEEK_COLUMN].astype('int64')
    print_df(df_GroupItemBAL1, 'STEP3 by 5.1.2 ____ df_GroupItemBAL1 ..... filter')

    df_GroupItemBAL1.rename(columns={ITEM_COLUMN+'_x': ITEM_COLUMN,},inplace=True)
    df_GroupItemBAL1.drop(columns=[BUILD_AHEAD_ITEM_ITEM_COLUMN], inplace=True)
    df_GroupItemBAL1.rename(columns={ITEM_COLUMN: BUILD_AHEAD_ITEM_ITEM_COLUMN,},inplace=True)

    #   5.1.3 컬럼편집
    df_GroupItemBAL1 = df_GroupItemBAL1[[
        ITEM_PRODUCT_GROUP_COLUMN, BUILD_AHEAD_ITEM_ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN
    ]].drop_duplicates()
    print_df(df_GroupItemBAL1, 'STEP3 by 5.1 ____ df_GroupItemBAL1 ..... final')
    # save_csv_file(df_GroupItemBAL1, 'STEP3 by 5.1 ____ df_GroupItemBAL1 ..... final')



    # 5.2 df_GroupItemBAL2
    #   5.2.1 join
    # df_merged = df_GroupBAL.merge(df_iteminfo, how='inner',
    #                               left_on=[BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN], right_on=[ITEM_PRODUCT_GROUP_COLUMN])
    # print_df(df_merged, 'STEP3 by 5.2.1 ____ df_merged ..... merge')

    #   5.2.2 조건 filter
    df_filtered2 = df_merged[
        ((df_merged[BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_PRODUCT_GROUP_COLUMN] == df_merged[ITEM_PRODUCT_GROUP_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_DEFINITION_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_DEFINITION_COLUMN] == df_merged[ITEM_DEFINITION_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_PROJECT_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_PROJECT_COLUMN] == df_merged[ITEM_PROJECT_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_MKT_NAME_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_MKT_NAME_COLUMN] == df_merged[ITEM_MARKETING_NAME_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_INCH_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_INCH_COLUMN] == df_merged[ITEM_INCH_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_ITEM_COLUMN].str.upper() == ALL_VALUE) | (df_merged[BUILD_AHEAD_ITEM_ITEM_COLUMN] == df_merged[ITEM_COLUMN])) &
        ((df_merged[BUILD_AHEAD_ITEM_ITEM_COLUMN].str.contains('%', na=False)))
        ].copy()
    df_filtered2[BUILD_AHEAD_ITEM_ITEM_COLUMN] = df_filtered2[BUILD_AHEAD_ITEM_ITEM_COLUMN].str.replace('%', '')
    df_filtered2['item_found'] = df_filtered2[BUILD_AHEAD_ITEM_ITEM_COLUMN].map(lambda x: x in df_filtered2[ITEM_COLUMN])
    df_filtered2 = df_filtered2[df_filtered2['item_found'] == True]

    exists_condition = df_filtered2.merge(df_in_BAL_Item_Ecp, how='outer', indicator=True,
                                          left_on=[GROUP_ID_COLUMN, BUILD_AHEAD_ITEM_ITEM_COLUMN],
                                          right_on=[GROUP_ID_COLUMN, ITEM_COLUMN])
    df_GroupItemBAL2 = exists_condition[(~exists_condition['_merge'].eq('both')) & (exists_condition[TIME_WEEK_COLUMN].notnull())].copy()
    df_GroupItemBAL2[TIME_WEEK_COLUMN] = df_GroupItemBAL2[TIME_WEEK_COLUMN].astype('int64')
    print_df(df_GroupItemBAL2, 'STEP3 by 5.2.2 ____ df_GroupItemBAL2 ..... filter')

    df_GroupItemBAL2.rename(columns={ITEM_COLUMN+'_x': ITEM_COLUMN,},inplace=True)
    df_GroupItemBAL2.drop(columns=[BUILD_AHEAD_ITEM_ITEM_COLUMN], inplace=True)
    df_GroupItemBAL2.rename(columns={ITEM_COLUMN: BUILD_AHEAD_ITEM_ITEM_COLUMN,},inplace=True)

    #   5.2.3 컬럼편집
    df_GroupItemBAL2 = df_GroupItemBAL2[[
        ITEM_PRODUCT_GROUP_COLUMN, BUILD_AHEAD_ITEM_ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN
    ]].drop_duplicates()
    print_df(df_GroupItemBAL2, 'STEP3 by 5.2 ____ df_GroupItemBAL2 ..... final')
    # save_csv_file(df_GroupItemBAL2, 'STEP3 by 5.2 ____ df_GroupItemBAL2 ..... final')



    # 5.3 df_GroupItemBAL create
    #   5.3.1 df_GroupItemBAL2
    df_GroupItemBAL = pd.concat([df_GroupItemBAL1, df_GroupItemBAL2], ignore_index=True)
    print_df(df_GroupItemBAL, 'STEP3 by 5.3 ____ df_GroupItemBAL ..... (df_GroupItemBAL1, df_GroupItemBAL2) concat')

    #   5.3.2 각 컬럼명 정리
    df_GroupItemBAL = df_GroupItemBAL[[
        ITEM_PRODUCT_GROUP_COLUMN, BUILD_AHEAD_ITEM_ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN
    ]].drop_duplicates()

    df_GroupItemBAL.rename(columns={BUILD_AHEAD_ITEM_ITEM_COLUMN: ITEM_COLUMN,},inplace=True)

    #   5.3.3 그룹핑과 최소값 계산 수행
    group_by_columns = [ITEM_PRODUCT_GROUP_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN]
    df_GroupItemBAL = df_GroupItemBAL.groupby(group_by_columns, as_index=False).agg({BUILD_AHEAD_ITEM_W_PERIOD_COLUMN: 'min'})

    print_df(df_GroupItemBAL, 'STEP3 by 5 ____ df_GroupItemBAL ..... final')
    # save_csv_file(df_GroupItemBAL, 'STEP3 by 5 ____ df_GroupItemBAL ..... final')

    # ====================> Step 5 (End)




    # ====================> Step 6 (Start) > df_GroupBAL_BOD SET 생성

    # 6.1 df_ProductGrpBAL_BOD_1 set create
    #   6.1.1 df_ProductGrpBAL_BOD_1
    df_GroupBAL_BOD_1 = df_GroupItemBAL[(df_GroupItemBAL[LOCATION_COLUMN].str.upper() == ALL_VALUE) &
                                        (df_GroupItemBAL[SUB_LOCATION_COLUMN].str.upper() != ALL_VALUE)].copy()
    print_df(df_GroupBAL_BOD_1, 'STEP3 by 6.1.1 ____ df_GroupBAL_BOD_1 ..... ALL filter')

    df_GroupBAL_BOD_1 = df_GroupBAL_BOD_1.merge(df_bod, how='inner', on=[SUB_LOCATION_COLUMN, ITEM_COLUMN])
    print_df(df_GroupBAL_BOD_1, 'STEP3 by 6.1.1 ____ df_GroupBAL_BOD_1 ..... df_bod merge')

    #   6.1.2 컬럼설정
    df_GroupBAL_BOD_1.rename(columns={LOCATION_COLUMN+'_y': LOCATION_COLUMN,
                                      TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
                                      }, inplace=True)

    df_GroupBAL_BOD_1[SOP_WEEK_COLUMN] = (df_GroupBAL_BOD_1[TIME_WEEK_COLUMN] + df_GroupBAL_BOD_1[BOD_SHIPMENT_LT_COLUMN] +
                                          df_GroupBAL_BOD_1[BOD_TRANSIT_COLUMN])
    df_GroupBAL_BOD_1[BOD_LT_COLUMN] = (df_GroupBAL_BOD_1[BOD_SHIPMENT_LT_COLUMN] + df_GroupBAL_BOD_1[BOD_TRANSIT_COLUMN])

    df_GroupBAL_BOD_1 = df_GroupBAL_BOD_1[df_GroupBAL_BOD_1[TIME_WEEK_COLUMN] == df_GroupBAL_BOD_1[SOP_WEEK_COLUMN]]

    df_GroupBAL_BOD_1 =  df_GroupBAL_BOD_1[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_GroupBAL_BOD_1, 'STEP3 by 6.1 ____ df_GroupBAL_BOD_1 ..... final')


    # 6.2 df_ProductGrpBAL_BOD_2 set create
    #   6.2.1 df_ProductGrpBAL_BOD_2
    df_GroupBAL_BOD_2 = df_GroupItemBAL[(df_GroupItemBAL[SUB_LOCATION_COLUMN].str.upper() == ALL_VALUE) &
                                        (df_GroupItemBAL[LOCATION_COLUMN].str.upper() != ALL_VALUE)].copy()
    print_df(df_GroupBAL_BOD_2, 'STEP3 by 6.2.1 ____ df_GroupBAL_BOD_2 ..... All filter')

    df_GroupBAL_BOD_2 = df_GroupBAL_BOD_2.merge(df_bod, how='inner', on=[LOCATION_COLUMN, ITEM_COLUMN])
    print_df(df_GroupBAL_BOD_2, 'STEP3 by 6.2.1 ____ df_GroupBAL_BOD_2 ..... merge')

    #   6.2.2 컬럼설정
    df_GroupBAL_BOD_2.rename(columns={SUB_LOCATION_COLUMN+'_y': SUB_LOCATION_COLUMN,
                                      TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
                                      }, inplace=True)

    df_GroupBAL_BOD_2[SOP_WEEK_COLUMN] = (df_GroupBAL_BOD_2[TIME_WEEK_COLUMN] + df_GroupBAL_BOD_2[BOD_SHIPMENT_LT_COLUMN] +
                                          df_GroupBAL_BOD_2[BOD_TRANSIT_COLUMN])

    df_GroupBAL_BOD_2[BOD_LT_COLUMN] = (df_GroupBAL_BOD_2[BOD_SHIPMENT_LT_COLUMN] + df_GroupBAL_BOD_2[BOD_TRANSIT_COLUMN])

    df_GroupBAL_BOD_2 = df_GroupBAL_BOD_2[df_GroupBAL_BOD_2[TIME_WEEK_COLUMN] == df_GroupBAL_BOD_2[SOP_WEEK_COLUMN]]

    df_GroupBAL_BOD_2 =  df_GroupBAL_BOD_2[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_GroupBAL_BOD_2, 'STEP3 by 6.2 ____ df_GroupBAL_BOD_2 ..... final')


    # 6.3 df_GroupBAL_BOD_3 set create
    #   6.3.1 df_GroupBAL_BOD_3
    df_GroupBAL_BOD_3 = df_GroupItemBAL[(df_GroupItemBAL[SUB_LOCATION_COLUMN].str.upper() == ALL_VALUE) &
                                        (df_GroupItemBAL[LOCATION_COLUMN].str.upper() == ALL_VALUE)].copy()
    print_df(df_GroupBAL_BOD_3, 'STEP3 by 6.3.1 ____ df_GroupBAL_BOD_3 ..... All filter')

    df_GroupBAL_BOD_3 = df_GroupBAL_BOD_3.merge(df_bod, how='inner', on=[ITEM_COLUMN])
    print_df(df_GroupBAL_BOD_3, 'STEP3 by 6.3.1 ____ df_GroupBAL_BOD_3 ..... merge')

    #   6.3.2 컬럼설정
    df_GroupBAL_BOD_3.rename(columns={LOCATION_COLUMN+'_y': LOCATION_COLUMN,
                                      SUB_LOCATION_COLUMN+'_y': SUB_LOCATION_COLUMN,
                                      TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
                                      }, inplace=True)

    df_GroupBAL_BOD_3[SOP_WEEK_COLUMN] = (df_GroupBAL_BOD_3[TIME_WEEK_COLUMN] + df_GroupBAL_BOD_3[BOD_SHIPMENT_LT_COLUMN] +
                                          df_GroupBAL_BOD_3[BOD_TRANSIT_COLUMN])
    df_GroupBAL_BOD_3[BOD_LT_COLUMN] = (df_GroupBAL_BOD_3[BOD_SHIPMENT_LT_COLUMN] + df_GroupBAL_BOD_3[BOD_TRANSIT_COLUMN])

    df_GroupBAL_BOD_3 = df_GroupBAL_BOD_3[df_GroupBAL_BOD_3[TIME_WEEK_COLUMN] == df_GroupBAL_BOD_3[SOP_WEEK_COLUMN]]

    df_GroupBAL_BOD_3 =  df_GroupBAL_BOD_3[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_GroupBAL_BOD_3, 'STEP3 by 6.3 ____ df_GroupBAL_BOD_3 ..... final')


    # 6.4 df_GroupBAL_BOD_4 set create
    #   6.4.1 df_GroupBAL_BOD_4
    df_GroupBAL_BOD_4 = df_GroupItemBAL[(df_GroupItemBAL[SUB_LOCATION_COLUMN].str.upper() != ALL_VALUE) &
                                        (df_GroupItemBAL[LOCATION_COLUMN].str.upper() != ALL_VALUE)].copy()
    print_df(df_GroupBAL_BOD_4, 'STEP3 by 6.4.1 ____ df_GroupBAL_BOD_4 ..... All filter')

    df_GroupBAL_BOD_4 = df_GroupBAL_BOD_4.merge(df_bod, how='inner', on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN])
    print_df(df_GroupBAL_BOD_4, 'STEP3 by 6.4.1 ____ df_GroupBAL_BOD_4 ..... merge')


    #   6.4.2 컬럼설정
    df_GroupBAL_BOD_4.rename(columns={LOCATION_COLUMN+'_y': LOCATION_COLUMN,
                                      SUB_LOCATION_COLUMN+'_y': SUB_LOCATION_COLUMN,
                                      TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,},
                             inplace=True)

    df_GroupBAL_BOD_4[SOP_WEEK_COLUMN] = (df_GroupBAL_BOD_4[TIME_WEEK_COLUMN] + df_GroupBAL_BOD_4[BOD_SHIPMENT_LT_COLUMN] +
                                          df_GroupBAL_BOD_4[BOD_TRANSIT_COLUMN])

    df_GroupBAL_BOD_4[BOD_LT_COLUMN] = (df_GroupBAL_BOD_4[BOD_SHIPMENT_LT_COLUMN] + df_GroupBAL_BOD_4[BOD_TRANSIT_COLUMN])

    df_GroupBAL_BOD_4 = df_GroupBAL_BOD_4[df_GroupBAL_BOD_4[TIME_WEEK_COLUMN] == df_GroupBAL_BOD_4[SOP_WEEK_COLUMN]]

    df_GroupBAL_BOD_4 =  df_GroupBAL_BOD_4[[
        ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_WEEK_COLUMN, BOD_LT_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN,
    ]].drop_duplicates()
    print_df(df_GroupBAL_BOD_4, 'STEP3 by 6.4 ____ df_GroupBAL_BOD_4 ..... column modity')


    # 6.5 모든 데이터프레임을 concat
    #   6.5.1  df_GroupBAL_BOD create
    df_GroupBAL_BOD = pd.concat([df_GroupBAL_BOD_1, df_GroupBAL_BOD_2, df_GroupBAL_BOD_3, df_GroupBAL_BOD_4])

    #   6.5.2 각 컬럼명 정리
    df_GroupBAL_BOD = df_GroupBAL_BOD[[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SOP_WEEK_COLUMN, BUILD_AHEAD_ITEM_W_PERIOD_COLUMN]]

    #   6.5.3 그룹핑과 최소값 계산 수행
    group_by_columns = [LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SOP_WEEK_COLUMN]
    df_GroupBAL_BOD = df_GroupBAL_BOD.groupby(group_by_columns, as_index=False).agg({BUILD_AHEAD_ITEM_W_PERIOD_COLUMN: 'min'})

    print_df(df_GroupBAL_BOD, 'STEP3 by 6 ____ df_GroupBAL_BOD ..... final')

    # ====================> Step 6 (End)




    # ====================> Step 7 (Start) > df_MinBAL Set 구성

    # 7.1 df_MinBAL set creeate
    #   7.1.1 df_MinBAL create
    df_MinBAL = pd.merge(df_ProductGrpBAL_BOD, df_GroupBAL_BOD, how='inner', on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN,
                                                                                 ITEM_COLUMN])
    print_df(df_MinBAL, 'STEP3 by 7.1.1 ____ df_MinBAL ..... merge')
    # save_csv_file(df_MinBAL, 'STEP3 by 7.1.1 ____ df_MinBAL ..... merge')

    #   7.1.2 컬럼설정
    df_MinBAL[BUILD_AHEAD_PROD_W_PERIOD_COLUMN] = np.where(
        df_MinBAL[BUILD_AHEAD_ITEM_W_PERIOD_COLUMN].isnull(),
        df_MinBAL[BUILD_AHEAD_PROD_W_PERIOD_COLUMN], df_MinBAL[BUILD_AHEAD_ITEM_W_PERIOD_COLUMN])

    df_MinBAL.rename(columns={SOP_WEEK_COLUMN+'_y': SOP_WEEK_COLUMN,}, inplace=True)

    df_MinBAL = df_MinBAL[[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SOP_WEEK_COLUMN, BUILD_AHEAD_PROD_W_PERIOD_COLUMN]]


    #   7.1.3 그룹핑과 최소값 계산 수행
    group_by_columns = [SUB_LOCATION_COLUMN, ITEM_COLUMN, SOP_WEEK_COLUMN]
    df_MinBAL = df_MinBAL.groupby(group_by_columns, as_index=False).agg({BUILD_AHEAD_PROD_W_PERIOD_COLUMN: 'min'})
    df_MinBAL[SOP_WEEK_COLUMN] = df_MinBAL[SOP_WEEK_COLUMN].astype(int)

    print_df(df_MinBAL, 'STEP3 by 7 ____ df_MinBAL ..... final')
    # save_csv_file(df_MinBAL, 'STEP3 by 7 ____ df_MinBAL ..... final')
    # ====================> Step 7 (End)




    # ====================> Step 8 (Start) > Demand 테이블에 W Demand Build Ahead Limit Update

    # 8.1 df_Demand
    #   8.1.1 df_Demand create
    df_Demand = pd.merge(df_in_Demand, df_MinBAL, how='inner',
                         left_on=[ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN],
                         right_on=[ITEM_COLUMN, SOP_WEEK_COLUMN, SUB_LOCATION_COLUMN])
    print_df(df_Demand, 'STEP3 by 8 ____ df_Demand ..... final')

    # ====================> Step 8 (End)

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')



    ################################################################################################################
    # STEP 4 : output data machining
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')


    step(400, '=====> STEP 4(End) : Check memory usage & runtime')



    ################################################################################################################
    # STEP 5 : output table create
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : Final output table create')



    step(500, '=====> STEP 5(End)')

except Exception as e:
    note(f'An exception occurred: {e}')
    note(f'=====> try exception : {traceback.format_exc()}', LOG_LEVEL.info())
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
