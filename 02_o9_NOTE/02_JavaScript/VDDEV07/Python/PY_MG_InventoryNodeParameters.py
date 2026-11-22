"""
* 프로그램명
    - PY_MG_InventoryNodeParameters

* 내용
    - MP Engine 수행을 위한 ITEM, Location 기준 Inventory Parameter 정보 I/F
    - Plan 대상 Item Site Association (Measure Group : Item Site Asn) 에서
      실제 현재 PLAN 대상에 대한 Item - Location Association 만 반영
      ex) No Carry Buffer

* 변경이력
    - 2024.06.25 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_itemStage   : Select ([Item].[Item] * [Item].[Item Stage] );

* Flow Summary
    - STEP1. Plan 대상 Item, Location(df_in_ItemSiteAsn) 정보 발췌
    - STEP2. Plan 대상 Item, Location 정보 Filtering
    - STEP3. STEP2 에서 구성된 Set을 대상으로 df_out_InventoryNodeParameters Measure 정보 Insert

* 주요 Logic ( Data 처리 )
    - STEP1 : Plan 대상 Item, Location(df_in_ItemSiteAsn) 정보 발췌
              대상  Item, Location 정보 df 구성
    - STEP2 : Plan 대상 BODLane ITEM (ITEM별 BOD) Filtering
                BODLane Item df Set(df_in_BODLaneItem)과 BOD Dimension df Set(df_in_BOD)을 BOD Name 기준으로 join하여
                BODLane Item 에 해당하는 fromsiteid, tositeid 정보를 발췌하고
                df_in_ItemSiteAsn 에 존재하는 item, Location(fromsiteid or tositeid) 를 대상으로 하는 df Set 구성
                    ※ df_in_BODLane 과 df_in_BODLaneItem 은 [BOD].[BOD Name]을 Key로 Join 관계
                    ※ df_in_ItemSiteAsn 에는 ITEM/Location 정보가 들어있어서 Location은 df_in_BOD에서 참조 필요
    - STEP3 : STEP2 에서 구성된 Set을 대상으로 df_out_MaterialConsAsn Measure 정보 Insert

* Output Table
    - df_out_InventoryNodeParams

* 데이타 초기화
    - DELETE DATA FOR MODEL [001.011W Solver Inputs Inventory Node Parameters] where {Version.[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_InventoryNodeParameters] for measures {[W No Carry Inventory]} using scope (&CWV) using arguments {(ExecutionMode, "LightWeight"), (Param_OUT_VERSION, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] ) on row,
        ({Measure.[W Alternate Material Node Group Priority],   // (LPS) 목적식 Minimize Alternate Flow의 priority
          Measure.[W Infinite Material Node],   // 무한자재
          Measure.[W Infinite Material Supply Priority], // (LPS) 목적식 Minimize Infinite Material Supply의 priority
          Measure.[W Inventory Holding Priority],        // (LPS) 목적식 Minimize Inventory Hold의 priority
          Measure.[W Material Node Build Ahead Limit],  // 선행
          Measure.[W No Carry Inventory],  // NO Carry buffer 지정
          Measure.[W WIP Sweep Depth]
         }) on column limit 100 ;

"""
import gc
import time

import numpy as np
import traceback
import pandas as pd
import tracemalloc
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_InventoryNodeParameters'
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
    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    logger.Step(p_step_no=no, p_step_desc=f'{string}')


# 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
tracemalloc.start()

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

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
        df_in_itemStage = read_csv_file("df_in_itemStage")

    if df_in_ItemSiteAsn.empty:
        raise Exception("=====> raise Exception: df_in_ItemSiteAsn is empty")

    if df_in_itemStage.empty:
        raise Exception("=====> raise Exception: df_in_itemStage is empty")

    # 입력 변수 확인
    if paramOutVersion is None or paramOutVersion.strip() == '':
        paramOutVersion = PARAM_OUTVERSION_VALUE

    # input dataframe 확인용 로그
    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn')
    print_df(df_in_itemStage, 'df_in_itemStage')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 2 : DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수 선언
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    ITEM_COLUMN = 'Item.[Item]'
    ITEM_STAGE_COLUMN = 'Item.[Item Stage]'

    ITEM_SITE_ASN_CUR_STATUS_COLUMN = "Item Site Asn_Cur Status"
    ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = "Item Site Asn_Engine Flag"
    ITEM_SITE_ASN_ITEM_GRP_COLUMN = "Item Site Asn_Item Grp"
    ITEM_SITE_ASN_SALES_PROD_ASN_COLUMN = "Item Site Asn_Sales Prod Asn"
    ITEM_SITE_ASN_STAGE_COLUMN = "Item Site Asn_Stage"

    W_ALTERNATE_METERIAL_NODE_GROUP_PRIORITY_COLUMN = "W Alternate Material Node Group Priority"
    W_INFINITE_METERIAL_NODE_COLUMN = "W Infinite Material Node"
    W_INFINITE_METERIAL_SUPPLY_PRIORITY_COLUMN = "W Infinite Material Supply Priority"
    W_INVENTORY_HOLDING_PRIORITY_COLUMN = "W Inventory Holding Priority"
    W_METERIAL_NODE_BUILD_AHEAD_LIMIT_COLUMN = "W Material Node Build Ahead Limit"
    W_NO_CARRY_INVENTORY_COLUMN = "W No Carry Inventory"
    W_WIP_SWEEP_DEPTH_COLUMN = "W WIP Sweep Depth"

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 3 :  데이터 선 가공
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    # location, item, version 만 발췌, 중복값 삭제(Location, item, version Distinct) 및 미사용 컬럼 삭제
    #   df_in_ItemSiteAsn remake
    drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [VERSION_NAME_COLUMN,
                                                                                 LOCATION_COLUMN,
                                                                                 ITEM_COLUMN]]
    df_in_ItemSiteAsn = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
        subset=[LOCATION_COLUMN], keep='first')
    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn')

    # No Carry Inventory 지정
    #   - SET, LCM ITEM 에 대해서는 No Carry Buffer 지정
    #   - df_in_itemStage 와 df_in_ItemSiteAsn 의 item이 같고 df_in_itemStage[Item_Stage] 값이 ('SKU', 'LCM') 이면
    #       W No Carry Inventory = 1 을 추가
    df_filtered = df_in_itemStage[(df_in_itemStage[ITEM_STAGE_COLUMN] == 'SKU') |
                                  (df_in_itemStage[ITEM_STAGE_COLUMN] == 'LCM')]

    df_combined1 = pd.merge(df_filtered, df_in_ItemSiteAsn, on=ITEM_COLUMN, how='inner')
    df_combined1[W_NO_CARRY_INVENTORY_COLUMN] = 1
    print_df(df_combined1, 'df_combined1')

    # W Infinite Material Node 지정
    #   - SET, LCM ITEM 에 대해서는 No Carry Buffer 지정
    #   - df_in_ItemSiteAsn item 이 'DUMMY%' 로 시작하는 item의 경우 W Infinite Material Node = 1 을 추가
    #   - df_in_itemStage 의 ITEM_STAGE_COLUMN 값이 'DUMMY' 로 시작하는 행만 선택
    df_in_itemStage = df_in_itemStage[df_in_itemStage[ITEM_STAGE_COLUMN].str.startswith('DUMMY')]

    # df_in_itemStage df_in_ItemSiteAsn 에서 'ITEM_COLUMN' 열이 일치하는 행만 선택하여 df_combined2 생성
    df_combined2 = pd.merge(df_in_itemStage, df_in_ItemSiteAsn, on=ITEM_COLUMN)

    # W_INFINITE_METERIAL_NODE_COLUMN 열을 추가하고 값 '1'을 설정
    df_combined2[W_INFINITE_METERIAL_NODE_COLUMN] = '1'
    print_df(df_combined2, 'df_combined2')

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 4 : output data machining
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # df_InventoryNodeParams 생성
    df_InventoryNodeParams = pd.concat([df_combined1, df_combined2])

    df_InventoryNodeParams[W_ALTERNATE_METERIAL_NODE_GROUP_PRIORITY_COLUMN] = np.nan
    df_InventoryNodeParams[W_INFINITE_METERIAL_SUPPLY_PRIORITY_COLUMN] = np.nan
    df_InventoryNodeParams[W_INVENTORY_HOLDING_PRIORITY_COLUMN] = np.nan
    df_InventoryNodeParams[W_METERIAL_NODE_BUILD_AHEAD_LIMIT_COLUMN] = np.nan
    df_InventoryNodeParams[W_WIP_SWEEP_DEPTH_COLUMN] = np.nan

    # 컬럼명 변경 및 순서 재정렬
    df_InventoryNodeParams = df_InventoryNodeParams[[VERSION_NAME_COLUMN, ITEM_COLUMN,
                                                     LOCATION_COLUMN,
                                                     W_ALTERNATE_METERIAL_NODE_GROUP_PRIORITY_COLUMN,
                                                     W_INFINITE_METERIAL_NODE_COLUMN,
                                                     W_INFINITE_METERIAL_SUPPLY_PRIORITY_COLUMN,
                                                     W_INVENTORY_HOLDING_PRIORITY_COLUMN,
                                                     W_METERIAL_NODE_BUILD_AHEAD_LIMIT_COLUMN,
                                                     W_NO_CARRY_INVENTORY_COLUMN,
                                                     W_WIP_SWEEP_DEPTH_COLUMN
                                                     ]]

    # 버전 처리
    df_InventoryNodeParams[VERSION_NAME_COLUMN] = paramOutVersion

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 5 : output table create
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : Final output table create')

    df_out_InventoryNodeParams = df_InventoryNodeParams.copy()
    print_df(df_out_InventoryNodeParams, 'df_out_InventoryNodeParams')

    note(f'=====> Final output table create')
    save_csv_file(df_out_InventoryNodeParams, 'df_out_ItemVaild')

    row_count, col_count = df_out_InventoryNodeParams.shape
    note(f'=====> Final df_out_InventoryNodeParams rows : {row_count}, column : {col_count}')

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception : {trace_msg}', LOG_LEVEL.info())
    logger.Error()
    raise Exception(e)

else:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB')
    step(600, '===================== plugin Execution End =====================')

finally:
    logger.Finish()
