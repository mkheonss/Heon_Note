"""

* 프로그램명
    - PY_MG_MaterialConsumptionAssociation

* 수정일 : 2024/11/12

* 내용
     - Production Capacity 정보 Interface
    - 현재는 CAPA 기준 관리만 대상 ( Target은 아님 )

* 변경이력
- 2024.06.27 / ybest7.park (박병훈) / Create

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary
    STEP1. Plan Hrozion 내의 ITEM Site Asn 대상 Group ID 만 발췌
    STEP2. STEP1  기준 Measure Insert

* ProductIon Constraint
    1) Constraint Group >> 그룹별 Start ~ End 주차 Capa 관리 ( even / odd )
    2) Constraint Group Detail >> item까지
    3) Constraint Group Detail W  >> 주차별 capa 관리
    4) Constraint Group Ecp >> 그룹에서 예외적으로 ITEM 제외 처리 (Const Grp Ecp_Flag)

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn = Select (&MPV  * [Location].[Location] * [Item].[Item] ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
                         [ Select ([Version].[Version Name]  * [Location].[Location] * [Item].[Item] ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);]
        ※ DISTINCT [Item].[Item] * [Location].[Location]
    - df_in_BOD_List = Select (&MPV  * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Created By], Measure.[BOD List_Creation Time], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT], Measure.[BOD List_Update Time], Measure.[BOD List_Updated By]}) on column;
                      [ select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Created By], Measure.[BOD List_Creation Time], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT], Measure.[BOD List_Update Time], Measure.[BOD List_Updated By]}) on column;]
    - df_in_BOD_Item = Select ([Version].[Version Name]* [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT], Measure.[BOD Item_BOD LT_Inherit], Measure.[BOD Item_Created By], Measure.[BOD Item_Creation Time], Measure.[BOD Item_Cur Status], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Min Lot Qty], Measure.[BOD Item_Multi Lot Qty], Measure.[BOD Item_Need Check], Measure.[BOD Item_Period SET Detail], Measure.[BOD Item_Period1], Measure.[BOD Item_Period2], Measure.[BOD Item_Period3], Measure.[BOD Item_Priority], Measure.[BOD Item_Priority_Inherit], Measure.[BOD Item_Prod Item], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Shipment LT_Inherit], Measure.[BOD Item_Time Phased BOD], Measure.[BOD Item_Time Phased Prty], Measure.[BOD Item_Time Phased Shipment], Measure.[BOD Item_To Item], Measure.[BOD Item_Update Time], Measure.[BOD Item_Updated By]}) on column;
    - df_in_BOD_List_Mtrl =  Select (&MPV * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl_EFF Enddate], Measure.[BOD List Mtrl_EFF Startdate]}) on column.filter((isnull(Measure.[BOD List Mtrl_EFF Enddate])||Measure.[BOD List Mtrl_EFF Enddate]> Measure.[W Plan Start Date])&&(isnull(Measure.[BOD List Mtrl_EFF Startdate])||Measure.[BOD List Mtrl_EFF Startdate]< Measure.[W Plan End Date]));
                              [Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl_EFF Enddate], Measure.[BOD List Mtrl_EFF Startdate]}) on column.filter((isnull(Measure.[BOD List Mtrl_EFF Enddate])||Measure.[BOD List Mtrl_EFF Enddate]> Measure.[W Plan Start Date])&&(isnull(Measure.[BOD List Mtrl_EFF Startdate])||Measure.[BOD List Mtrl_EFF Startdate]< Measure.[W Plan End Date]));]
    - df_in_BODItemMtrlFull =  Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_Lot Size]}) on column;
    - df_in_BOMMaster = Select (&MPV  * [Location].[Location] * [BOM Info].[BOM ID] ) on row,({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate],Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Prty], Measure.[BOM Master_Status], Measure.[BOM Master_BOM Location] }) on column ;
                       [Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column ;]
    - df_in_BOMComponent = select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate], Measure.[BOM Comp_Valid Flag]}) on column;
                           [select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate], Measure.[BOM Comp_Valid Flag]}) on column;]
    - df_in_BODItem_INF = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Infinite_EFF Enddate], Measure.[BOD Item Mtrl Infinite_EFF Startdate]}) on column;
                          [Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Infinite_EFF Enddate], Measure.[BOD Item Mtrl Infinite_EFF Startdate]}) on column;]
    - df_in_BODItemUnConst = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl UnConst_EFF Enddate], Measure.[BOD Item Mtrl UnConst_EFF Startdate]}) on column;

* Output Table
    - df_out_MaterialConsAsn = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,  ({Measure.[W Material Consumption Association], Measure.[W Material Consumption Quantity Per]}) on column;

* 데이터 삭제
    DELETE DATA FOR MODEL [001.002W Solver Inputs Material Consumption Association] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
      EXEC plugin instance [PY_MG_MaterialConsumptionAssociation] for Measures {[W Item Location Association]} using scope ( &MPV ) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};

* 데이터 수정
    scope : ([Activity3].[Activity3] * [Activity2].[Activity2] * [Activity1].[Activity1] * [Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item].[Item] );
    Measure.[W Production Holiday] = False;
    end scope;  <- 다시 수정 필요

"""


########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
from NSCMCommon import VDCommon as vdCommon
import os.path
import time
import datetime
import decimal
import math
import traceback
import gc
import tracemalloc
import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re
import warnings

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_MaterialConsumptionAssociation'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level

########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')

# Logger.debug(f'[START] {str_instance}')
# Logger.Start()
# note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
# step(0, '===================== plugin Execution Start =====================')
# tracemalloc.start()

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, Logger, com.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if com.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(com.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    step(100, '=====> STEP 1(Start) : Input Date Frame Read')
    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
        df_in_BOD = read_csv_file('df_in_BOD')
        df_in_BOD_List = read_csv_file('df_in_BOD_List')
        df_in_BOD_Item = read_csv_file('df_in_BOD_Item')
        # df_in_BOD_List_Mtrl = read_csv_file('df_in_BOD_List_Mtrl')
        df_in_BODItemMtrlFull = read_csv_file('df_in_BODItemMtrlFull')
        df_in_BOMMaster = read_csv_file('df_in_BOMMaster')
        df_in_BOMComponent = read_csv_file('df_in_BOMComponent')
        df_in_BODItem_INF = read_csv_file('df_in_BODItem_INF')
        df_in_BODItemUnConst = read_csv_file('df_in_BODItemUnConst')


    # if df_in_ItemSiteAsn.empty:
    #     raise Exception("Exception: df_in_ItemSiteAsn is empty")

    # if df_in_BOD_List.empty:
    #     raise Exception("Exception df_in_BOD_List is empty")

    # if df_in_BOD_Item.empty:
    #     raise Exception("Exception df_in_BOD_Item is empty")

    # if df_in_BOD_List_Mtrl.empty:
    #     raise Exception("Exception df_in_BOD_List_Mtrl is empty")

    # if df_in_BODItemMtrlFull.empty:
    #     raise Exception("Exception df_in_BODItemMtrlFull is empty")

    # if df_in_BOMMaster.empty:
    #     raise Exception("Exception df_in_BOMMaster is empty")
    #
    # if df_in_BOMComponent.empty:
    #     raise Exception("Exception df_in_BOMComponent is empty")

    # if df_in_BODItem_INF.empty:
    #     raise Exception("Exception df_in_BODItem_INF is empty")

    # if df_in_BODItemUnConst.empty:
    #     raise Exception("Exception df_in_BODItemUnConst is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',True)
    print_df(df_in_BOD_List, 'df_in_BOD_List',True)
    print_df(df_in_BOD_Item, 'df_in_BOD_Item',True)
    # print_df(df_in_BOD_List_Mtrl, 'df_in_BOD_List_Mtrl')
    print_df(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull',True)
    print_df(df_in_BOMMaster, 'df_in_BOMMaster',True)
    print_df(df_in_BOMComponent, 'df_in_BOMComponent',True)
    print_df(df_in_BODItem_INF, 'df_in_BODItem_INF',True)
    print_df(df_in_BODItemUnConst, 'df_in_BODItemUnConst',True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    ITEM_COLUMN = 'Item.[Item]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    Item_Material_COLUMN = 'Item Material.[Item Material]'

    Activity1_COLUMN = "Activity1.[Activity1]"
    Activity2_COLUMN = "Activity2.[Activity2]"
    Activity3_COLUMN = "Activity3.[Activity3]"
    BODNAME_COLUMN = 'BOD.[BOD Name]'
    FROMSITEID_COLUMN = 'BOD.[From Site ID]'
    TOSITEID_COLUMN = 'BOD.[To Site ID]'
    TRANSPORTMODE_COLUMN = 'Trans Mode.[Trans Mode]'
    BODTRANSORTMODE_COLUMN = 'BOD.[Transport Mode]'
    BOMID_COLUMN = 'BOM Master_BOM ID'
    BOMINFOID = 'BOM Info.[BOM ID]'
    BOM_Comp_Consume_Qty = 'BOM Comp_Consume Qty'
    BOM_Master_BOM_Location ='BOM Master_BOM Location'

    W_Material_Consumption_Association = 'W Material Consumption Association'
    W_Material_Consumption_Quantity_Per = 'W Material Consumption Quantity Per'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) df_in_ItemSiteAsn 중복제거 기준 item & Loaction series 생성
    #         (2) Location 조건은 Location & Sub Location은 OR 조건 Item은 And 조건으로 df_in_BOD_Item 필터
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')
    # Location & Item 의 Unique한 Values 추출 (df_in_ItemSiteAsn 기준)
    Location_series = df_in_ItemSiteAsn[LOCATION_COLUMN].unique()
    Item_series = df_in_ItemSiteAsn[ITEM_COLUMN].unique()
    # 추출된 조건을 기준으로 df_in_BOD_Item 에서 필터 (LOCATION_COLUMN or SUB_LOCATION_COLUMN 포함기준)
    df_in_BOD_Item = df_in_BOD_Item[(df_in_BOD_Item[LOCATION_COLUMN].isin(Location_series)) | (
        df_in_BOD_Item[SUB_LOCATION_COLUMN].isin(Location_series))]
    df_in_BOD_Item = df_in_BOD_Item[df_in_BOD_Item[ITEM_COLUMN].isin(Item_series)]

    print_df(df_in_BOD_Item, 'df_in_BOD_Item',True)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) df_in_BOD_Item 과 df_in_BOD_List merge하여 1차 Output Data 생성
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    df_in_BOD_Item = df_in_BOD_Item.merge(df_in_BOD_List, on=[VERSION_NAME_COLUMN, LOCATION_COLUMN,
                                                         TRANSPORTMODE_COLUMN, SUB_LOCATION_COLUMN], how='inner')
    df_in_BOD_Item[Activity1_COLUMN] = df_in_BOD_Item[LOCATION_COLUMN] + "_" + df_in_BOD_Item[
        SUB_LOCATION_COLUMN] + '_' + df_in_BOD_Item[
                                           TRANSPORTMODE_COLUMN]
    df_in_BOD_Item[Activity2_COLUMN] = df_in_BOD_Item[TRANSPORTMODE_COLUMN]
    df_in_BOD_Item[Activity3_COLUMN] = df_in_BOD_Item[ITEM_COLUMN]
    df_in_BOD_Item[W_Material_Consumption_Association] = 1
    df_in_BOD_Item[W_Material_Consumption_Quantity_Per] = 1
    df_in_BOD_Item = df_in_BOD_Item[
        [VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN,
         W_Material_Consumption_Association, W_Material_Consumption_Quantity_Per]]

    print_df(df_in_BOD_Item, 'df_in_BOD_Item',True)
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) df_in_BOD_Item_mtrl 기준 Location & Item 필터 및 merge data 생성
    #         (2) 생성된 merge data와 df_in_BOD_List_Mtrl merge하여 mergeB 생성
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')
    # df_in_BOD_Item_mtrl의 Location과 subLocation 과 df_in_ItemSiteAsn의 Location을 포함한 것 or 조건으로 필터링
    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[(df_in_BODItemMtrlFull[LOCATION_COLUMN].isin(Location_series)) |
                                              (df_in_BODItemMtrlFull[SUB_LOCATION_COLUMN].isin(Location_series))]
    # 1차 필터링 된 df_in_BOD_Item_mtrl에서 Item 기준으로 df_in_ItemSiteAsn의 포함 된 것 필터링
    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[df_in_BODItemMtrlFull[Item_Material_COLUMN].isin(Item_series)]
    df_in_BODItemMtrlFull[Activity1_COLUMN] = df_in_BODItemMtrlFull[LOCATION_COLUMN] + '_' + df_in_BODItemMtrlFull[
        SUB_LOCATION_COLUMN] + '_' + df_in_BODItemMtrlFull[TRANSPORTMODE_COLUMN]
    df_in_BODItemMtrlFull[Activity2_COLUMN] = df_in_BODItemMtrlFull[TRANSPORTMODE_COLUMN]
    df_in_BODItemMtrlFull[Activity3_COLUMN] = df_in_BODItemMtrlFull[Item_Material_COLUMN]
    df_in_BODItemMtrlFull[W_Material_Consumption_Association] =1
    df_in_BODItemMtrlFull[W_Material_Consumption_Quantity_Per] =1
    df_in_BODItemMtrlFull.rename(columns={Item_Material_COLUMN:ITEM_COLUMN}, inplace=True)

    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[
        [VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN,
         W_Material_Consumption_Association, W_Material_Consumption_Quantity_Per]]

    print_df(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull',True)
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 6. (1) df_in_BOMComponent 의 Item 중 df_in_ItemSiteAsn 포함된 것 들만 필터링
    #         (2) df_in_BOMComponent 와 df_in_BOMMaster merge 하여 mergeC 생성
    ################################################################################################################
    step(600, '=====> STEP 5(Start) : output data machining')

    df_in_BOMComponent = df_in_BOMComponent[df_in_BOMComponent[ITEM_COLUMN].isin(Item_series)]
    df_in_BOMComponent = df_in_BOMComponent.merge(df_in_BOMMaster, on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, BOMINFOID],
                                         how='inner')
    df_in_BOMComponent[LOCATION_COLUMN] = np.where(df_in_BOMComponent[BOM_Master_BOM_Location].isna(),
                                                   df_in_BOMComponent[LOCATION_COLUMN],
                                                   df_in_BOMComponent[BOM_Master_BOM_Location])
    df_in_BOMComponent[Activity1_COLUMN] = df_in_BOMComponent[BOMINFOID]
    df_in_BOMComponent[Activity2_COLUMN] = "RT_"+df_in_BOMComponent[BOMINFOID]+'_@'+df_in_BOMComponent[LOCATION_COLUMN]
    df_in_BOMComponent[Activity3_COLUMN] = df_in_BOMComponent[BOMID_COLUMN]
    df_in_BOMComponent[W_Material_Consumption_Association] = 1
    df_in_BOMComponent[W_Material_Consumption_Quantity_Per] = np.where(df_in_BOMComponent[BOM_Comp_Consume_Qty].isna(), 1,
                                                              df_in_BOMComponent[BOM_Comp_Consume_Qty])
    df_in_BOMComponent = df_in_BOMComponent[
        [VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN,
         W_Material_Consumption_Association, W_Material_Consumption_Quantity_Per]]

    print_df(df_in_BOMComponent, 'df_in_BOMComponent',True)
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 7. (1) 최종 OutPut Data Frame 생성
    ################################################################################################################
    step(700, '=====> STEP 7(Start) : output data machining')
    df_in_BODItem_INF[Activity1_COLUMN] = df_in_BODItem_INF[LOCATION_COLUMN] + '_' + df_in_BODItem_INF[
        SUB_LOCATION_COLUMN] + '_' + df_in_BODItem_INF[TRANSPORTMODE_COLUMN]
    df_in_BODItem_INF[Activity2_COLUMN] = df_in_BODItem_INF[TRANSPORTMODE_COLUMN]
    df_in_BODItem_INF[Activity3_COLUMN] = df_in_BODItem_INF[Item_Material_COLUMN]
    df_in_BODItem_INF[W_Material_Consumption_Association] = 1
    df_in_BODItem_INF[W_Material_Consumption_Quantity_Per] = 1
    df_in_BODItem_INF.rename(columns={Item_Material_COLUMN:ITEM_COLUMN}, inplace=True)
    df_in_BODItem_INF = df_in_BODItem_INF[[VERSION_NAME_COLUMN,ITEM_COLUMN, LOCATION_COLUMN, Activity1_COLUMN,
                                           Activity2_COLUMN, Activity3_COLUMN, W_Material_Consumption_Association,
                                           W_Material_Consumption_Quantity_Per]]

    print_df(df_in_BODItem_INF, 'df_in_BODItem_INF',True)
    step(700, '=====> STEP 7(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 8. (1) df_in_BODItemUnConst 추가 insert
    ################################################################################################################
    step(800, '=====> STEP 8(Start) : output data machining')
    df_in_BODItemUnConst = df_in_BODItemUnConst.rename(columns={Item_Material_COLUMN:ITEM_COLUMN})
    df_in_BODItemUnConst[W_Material_Consumption_Association] = 1
    df_in_BODItemUnConst[W_Material_Consumption_Quantity_Per] = 1
    df_in_BODItemUnConst[Activity1_COLUMN] = df_in_BOMComponent[LOCATION_COLUMN] + '_' + df_in_BODItemUnConst[
        SUB_LOCATION_COLUMN] + '_' + df_in_BODItemUnConst[TRANSPORTMODE_COLUMN]
    df_in_BODItemUnConst[Activity2_COLUMN] = df_in_BODItemUnConst[TRANSPORTMODE_COLUMN]
    df_in_BODItemUnConst[Activity3_COLUMN] = df_in_BODItemUnConst[ITEM_COLUMN]
    df_in_BODItemUnConst = df_in_BODItemUnConst[[VERSION_NAME_COLUMN,ITEM_COLUMN, LOCATION_COLUMN, Activity1_COLUMN,
                                           Activity2_COLUMN, Activity3_COLUMN, W_Material_Consumption_Association,
                                           W_Material_Consumption_Quantity_Per]]

    print_df(df_in_BODItemUnConst, 'df_in_BODItemUnConst',True)
    step(800, '=====> STEP 8(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 9. (1) 최종 OutPut Data Frame 생성
    ################################################################################################################
    step(900, '=====> STEP 9(Start) : output data machining')

    df_out_MaterialConsAsn = pd.concat(
        [df_in_BOD_Item, df_in_BODItemMtrlFull, df_in_BOMComponent, df_in_BODItem_INF, df_in_BODItemUnConst],
        axis=0)

    del(df_in_BOD_Item, df_in_BODItemMtrlFull, df_in_BOMComponent, df_in_BODItem_INF, df_in_BODItemUnConst)

    print_df(df_out_MaterialConsAsn, 'df_out_MaterialConsAsn',True)
    step(900, '=====> STEP 8(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 7. (1) 최종 Out_Put Save
    ################################################################################################################

    row_count, col_count = df_out_MaterialConsAsn.shape
    note(f'=====> Final df_out_MaterialConsAsn rows : {row_count} , Columns : {col_count}')
    print_df(df_out_MaterialConsAsn, 'df_out_MaterialConsAsn')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_MaterialConsAsn, 'df_out_MaterialConsAsn')


except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_MaterialConsAsn = pd.DataFrame([], columns=[])
    # df_out_NewModelSumStatus = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(500, '===================== plugin Execution End =====================')

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    Logger.Finish()
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')