"""

* 프로그램명
    - PY_MG_Capacity_ProductionConstraint

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
    - df_in_ConstraintGroupDetail = Select ([Version].[Version Name] * [Group].[Group ID] ) on row, ({Measure.[Const Grp Detail_Desc], Measure.[Const Grp Detail_From Site], Measure.[Const Grp Detail_Item], Measure.[Const Grp Detail_Product Group], Measure.[Const Grp Detail_To Site]}) on column ;
                                   [Select ( &MPV * [Group].[Group ID] ) on row, ({Measure.[Const Grp Detail_Desc], Measure.[Const Grp Detail_From Site], Measure.[Const Grp Detail_Item], Measure.[Const Grp Detail_Product Group], Measure.[Const Grp Detail_To Site]}) on column; ]
    - df_in_ConstraintGroupDetailW = Select ([Version].[Version Name] * [Time].[Week] * [Group].[Group ID] ) on row, ({Measure.[Const Grp Detail W_Lock Flag], Measure.[Const Grp Detail W_Qty]}) on column;
                                   [Select ( &MPV * &PlanningHorizon  * [Group].[Group ID] ) on row, ({Measure.[Const Grp Detail W_Lock Flag], Measure.[Const Grp Detail W_Qty]}) on column;]
    - df_in_ConstraintGroupEcp = Select ([Version].[Version Name] * [Item].[Item] * [Group].[Group ID] ) on row, ({Measure.[Const Grp Ecp_Flag]}) on column.filter(Measure.[Const Grp Ecp_Flag]== false);
                                 [Select (&MPV * [Item].[Item] * [Group].[Group ID] ) on row, ({Measure.[Const Grp Ecp_Flag]}) on column.filter(Measure.[Const Grp Ecp_Flag]== false); ]
    - df_in_ItemSiteAsn = Select ( [Version].[Version Name] * [Location].[Location]  * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn],Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
                               [Select ( &MPV * &MFLocation  * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);]
    - df_in_BOMMaster = Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column;
                        [ Select (&MPV * &MFLocation * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column; ]
    - df_in_TactTime = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  where {  Measure.[Tact Time_Valid Asn] == true } ;
                        [ Select (&MPV * &MFLocation * [Item].[Item] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  where {  Measure.[Tact Time_Valid Asn] == true } ;]
    - df_in_BODItem = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT]}) on column;
                      [Select (&MPV * &MFLocation * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT]}) on column; ]
    - df_in_Time : Select ([Time].[Week] ) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket],[W Solver Start Bucket], [W Solver End Bucket]};
                   [ select (&PlanningHorizon);]


* Output Table
    - df_out_InputsCapacity = Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row, ({ Measure.[W Flex Capacity Band1], Measure.[W Flex Capacity Band2], Measure.[W Resource Base Capacity] }) on column;
                              [Select ( &MPV   * &PlanningHorizon * &MFLocation   * [Resource].[Resource] ) on row, ({ Measure.[W Flex Capacity Band1], Measure.[W Flex Capacity Band2], Measure.[W Resource Base Capacity] }) on column; ]
    - df_out_ProdCapaSimultaneous = Select ([Version].[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] * [Resource Group].[Resource Group] ) on row, ({Measure.[W Simultaneous Capacity Consumption Association]}) on column;
                              [ Select (&MPV  *  &MFLocation * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] * [Resource Group].[Resource Group] ) on row, ({Measure.[W Simultaneous Capacity Consumption Association]}) on column; ]
    - df_out_ProdCapaConsumeAsn = Select ([Version].[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Input Resource Priority], Measure.[W Resource Category], Measure.[W Resource Consumed Quantity Per], Measure.[W Resource Consumption Association]}) on column;
                              [Select (&MPV  *  &MFLocation * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row, ({Measure.[W Input Resource Priority], Measure.[W Resource Category], Measure.[W Resource Consumed Quantity Per], Measure.[W Resource Consumption Association]}) on column; ]

* 데이터 삭제
  DELETE DATA FOR MODEL [001.022W Solver Inputs Capacity] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
    EXEC plugin instance [PY_MG_Capacity_ProductionConstraint] for Measures {[W Resource Base Capacity]} using scope ( &MPV * &PlanningHorizon * &MFLocation) using arguments {(ExecutionMode, "MediumWeight"),("IncludeNullRows", "False"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* 데이터 수정
    scope : ([Activity3].[Activity3] * [Activity2].[Activity2] * [Activity1].[Activity1] * [Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item].[Item] );
    Measure.[W Production Holiday] = False;
    end scope;  <- 다시 수정 필요

"""

import decimal
########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
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

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_Capacity_ProductionConstraint'
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

def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    Logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')



Logger.debug(f'[START] {str_instance}')
Logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')
tracemalloc.start()
try:
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

        df_in_ConstraintGroupDetail = read_csv_file("df_in_ConstraintGroupDetail")
        df_in_ConstraintGroupDetailW = read_csv_file('df_in_ConstraintGroupDetailW')
        df_in_ConstraintGroupEcp = read_csv_file('df_in_ConstraintGroupEcp')
        df_in_ItemSiteAsn = read_csv_file('df_in_ItemSiteAsn')
        df_in_BOMMaster = read_csv_file('df_in_BOMMaster')
        df_in_TactTime = read_csv_file('df_in_TactTime')
        df_in_BODItem = read_csv_file('df_in_BODItem')
        df_in_Time = read_csv_file('df_in_Time')


    if df_in_ConstraintGroupDetail.empty:
        raise Exception("Exception: df_in_ConstraintGroupDetail is empty")

    if df_in_ConstraintGroupDetailW.empty:
        raise Exception("Exception: df_in_ConstraintGroupDetailW is empty")

    if df_in_ConstraintGroupEcp.empty:
        raise  Exception("Exception df_in_ConstraintGroupEcp is empty")

    if df_in_ItemSiteAsn.empty:
        raise Exception("Exception: df_in_ItemSiteAsn is empty")

    if df_in_BOMMaster.empty:
        raise Exception("Exception: df_in_BOMMaster is empty")

    if df_in_TactTime.empty:
        raise  Exception("Exception df_in_TactTime is empty")

    if df_in_BODItem.empty:
        raise Exception("Exception: df_in_BODItem is empty")

    if df_in_Time.empty:
        raise Exception("Exception df_in_Time is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ConstraintGroupDetail, 'df_in_ConstraintGroupDetail')
    print_df(df_in_ConstraintGroupDetailW, 'df_in_ConstraintGroupDetailW')
    print_df(df_in_ConstraintGroupEcp, 'df_in_ConstraintGroupEcp')
    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn')
    print_df(df_in_BOMMaster, 'df_in_BOMMaster')
    print_df(df_in_TactTime, 'df_in_TactTime')
    print_df(df_in_BODItem, 'df_in_BODItem')
    print_df(df_in_Time, 'df_in_Time')

    # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #     paramOutVersion = PARAM_OUTVERSION_VALUE

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')
    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    ITEM_COLUMN = 'Item.[Item]'
    RESOURCE_COLUMN = 'Resource.[Resource]'
    TIME_WEEK_COLUMN = "Time.[Week]"
    GROUP_ID_COLUMN = 'Group.[Group ID]'
    BOM_INFO_COLUMN = 'BOM Info.[BOM ID]'
    LINE_COLUMN = 'Line.[Line]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
    RESOURCE_Group_COLUMN = 'Resource Group.[Resource Group]'

    Activity1_COLUMN = "Activity1.[Activity1]"
    Activity2_COLUMN = "Activity2.[Activity2]"
    Activity3_COLUMN = "Activity3.[Activity3]"

    Const_Grp_Detail_From_Site = 'Const Grp Detail_From Site'
    Const_Grp_Detail_W_Qty = 'Const Grp Detail W_Qty'
    Const_Grp_Detail_To_Site = 'Const Grp Detail_To Site'
    BOM_Master_BOM_ID = 'BOM Master_BOM ID'

    W_Flex_Capacity_Band1 = 'W Flex Capacity Band1'
    W_Flex_Capacity_Band2 = 'W Flex Capacity Band2'
    W_Resource_Base_Capacity = 'W Resource Base Capacity'
    W_Simultaneous_Capacity_Consumption_Association = 'W Simultaneous Capacity Consumption Association'
    W_Input_Resource_Priority = 'W Input Resource Priority'
    W_Resource_Consumed_Quantity_Per = 'W Resource Consumed Quantity Per'
    W_Resource_Category = 'W Resource Category'
    W_Resource_Consumption_Association = 'W Resource Consumption Association'

    merge_key = "merge_key"
    All = 'All'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3. (1) df_in_ItemSiteAsn의 Version 과 Location의 Unique한 값 설정
    #         (2) df_in_ConstraintGroupDetailW & df_in_ConstraintGroupDetail df_in_ItemSiteAsn의 포함한 데이터 구성
    #         (3) df_in_ConstraintGroupDetailW & df_in_ConstraintGroupDetail merge
    #         (4) df_mergeA로 df_ProdCapa(3번 Step 데이터) 로 복사
    #         (5) df_mergeA와 df_in_Time 데이터 merge
    #         (6) df_mergeA와 와 df_ProdCapa merge 하여 df_out_InputsCapacity 값 설정
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    Version_series = df_in_ItemSiteAsn[VERSION_NAME_COLUMN].unique()
    Location_series = df_in_ItemSiteAsn[LOCATION_COLUMN].unique()

    df_in_ConstraintGroupDetailW = df_in_ConstraintGroupDetailW[
        df_in_ConstraintGroupDetailW[VERSION_NAME_COLUMN].isin(Version_series)]
    df_in_ConstraintGroupDetail = df_in_ConstraintGroupDetail[
        df_in_ConstraintGroupDetail[Const_Grp_Detail_From_Site].isin(Location_series)]
    df_ProdCapa = df_in_ConstraintGroupDetailW.merge(df_in_ConstraintGroupDetail,
                                                     on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN], how='inner')
    df_ProdCapa[W_Resource_Base_Capacity] = df_ProdCapa[Const_Grp_Detail_W_Qty]
    df_ProdCapa[W_Flex_Capacity_Band1] = 0
    df_ProdCapa[W_Flex_Capacity_Band2] = 0
    df_ProdCapa[LOCATION_COLUMN] = df_ProdCapa[Const_Grp_Detail_From_Site]
    df_ProdCapa[Const_Grp_Detail_To_Site] = df_ProdCapa[Const_Grp_Detail_To_Site].fillna(All)
    df_ProdCapa[RESOURCE_COLUMN] = np.where(df_ProdCapa[Const_Grp_Detail_To_Site] == All,
                                            "MFC@" + df_ProdCapa[GROUP_ID_COLUMN],
                                            'SRC@' + df_ProdCapa[GROUP_ID_COLUMN])
    df_mergeA = df_ProdCapa.copy()
    df_mergeA = df_mergeA[[VERSION_NAME_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN]].drop_duplicates()
    df_mergeA[merge_key] = 1
    df_in_Time[merge_key] = 1

    df_mergeA = df_mergeA.merge(df_in_Time, on=merge_key)

    df_mergeA = df_mergeA.merge(df_ProdCapa,
                                on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN, TIME_WEEK_COLUMN],
                                how='left')
    df_mergeA[W_Resource_Base_Capacity] = df_mergeA[W_Resource_Base_Capacity].fillna(999999)
    df_mergeA[W_Flex_Capacity_Band1] = df_mergeA[W_Flex_Capacity_Band1].fillna(0)
    df_mergeA[W_Flex_Capacity_Band2] = df_mergeA[W_Flex_Capacity_Band2].fillna(0)

    df_out_InputsCapacity = df_mergeA[
        [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN, W_Flex_Capacity_Band1,
         W_Flex_Capacity_Band2, W_Resource_Base_Capacity]]

    print_df(df_out_InputsCapacity, 'df_out_InputsCapacity')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) df_ProdCapa 를 df_mergeB로 복사 후 Const_Grp_Detail_To_Site 컬럼 필터
    #         (2) df_mergeB를 df_in_ConstraintGroupEcp & df_in_TactTime & df_in_BOMMaster로 merge
    #         (3) BOM Simultaneous Consumption Association 데이터 df_mergeF로 구성
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')
    df_mergeB = df_ProdCapa[df_ProdCapa[Const_Grp_Detail_To_Site] == All]
    df_mergeB = df_mergeB.drop_duplicates(subset=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, LOCATION_COLUMN])
    df_mergeC = df_in_ConstraintGroupEcp.merge(df_mergeB, on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN], how='inner')
    df_mergeC = df_mergeC[
        [VERSION_NAME_COLUMN, ITEM_COLUMN, GROUP_ID_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN]]
    df_mergeD = df_in_TactTime.merge(df_mergeB, on=[VERSION_NAME_COLUMN, LOCATION_COLUMN], how='inner')
    df_mergeD = df_mergeD[
        [VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, LINE_COLUMN, TIME_WEEK_COLUMN, GROUP_ID_COLUMN,
         RESOURCE_COLUMN]]
    merge_onList = {col: df_mergeC[col].equals(df_mergeD[col]) for col in
                    df_mergeD.columns.intersection(df_mergeC.columns).to_list()}
    merge_onList = [k for k in merge_onList.keys()]
    df_mergeE = df_mergeC.merge(df_mergeD, on=merge_onList, how='inner')
    df_in_BOMMaster = df_in_BOMMaster[df_in_BOMMaster[LOCATION_COLUMN].isin(df_mergeB[LOCATION_COLUMN].unique())]
    df_mergeF = df_mergeE.merge(df_in_BOMMaster, left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN],
                                right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, BOM_Master_BOM_ID], how='inner')
    df_mergeF[Activity1_COLUMN] = df_mergeF[BOM_Master_BOM_ID]
    df_mergeF[Activity2_COLUMN] = "RT_" + df_mergeF[BOM_Master_BOM_ID] + "@" + df_mergeF[LOCATION_COLUMN]
    df_mergeF[Activity3_COLUMN] = df_mergeF[ITEM_COLUMN]
    df_mergeF[W_Simultaneous_Capacity_Consumption_Association] = 1
    df_mergeF[RESOURCE_Group_COLUMN] = "RT_" + df_mergeF[BOM_Master_BOM_ID] + "@" + df_mergeF[LOCATION_COLUMN] + '_' + \
                                       df_mergeF[LINE_COLUMN]
    df_mergeF = df_mergeF[
        [VERSION_NAME_COLUMN, LOCATION_COLUMN, Activity1_COLUMN, Activity2_COLUMN, RESOURCE_COLUMN, Activity3_COLUMN,
         RESOURCE_Group_COLUMN,W_Simultaneous_Capacity_Consumption_Association]]

    print_df(df_mergeF, 'df_mergeF')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) BOD Simultaneous Consumption Association 구성
    #         (2) df_ProdCapa의 Const_Grp_Detail_To_Site 필터 후 df_mergeG로 구성
    #         (3) df_mergeG로 구성 후 df_in_ConstraintGroupEcp & df_in_BODItem 순차적으로 merge
    #         (4) df_out_ProdCapaSimultaneous 데이터 프레임 생성 (BOM Simultaneous Consumption Association &
    #             BOD Simultaneous Consumption Association  데이터 프레밈 Concat)
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')
    df_mergeG = df_ProdCapa[df_ProdCapa[Const_Grp_Detail_To_Site] != All]
    df_mergeG = df_mergeG.drop_duplicates(subset=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN, LOCATION_COLUMN])
    df_mergeH = df_in_ConstraintGroupEcp.merge(df_mergeG, on=[VERSION_NAME_COLUMN, GROUP_ID_COLUMN], how='inner')
    df_mergeH = df_mergeH.merge(df_in_BODItem,
                                left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, Const_Grp_Detail_To_Site],
                                right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN],
                                how='inner')
    df_mergeH[Activity1_COLUMN] = df_mergeH[LOCATION_COLUMN] + '_' + df_mergeH[SUB_LOCATION_COLUMN] + '_' + df_mergeH[
        TRANS_MODE_COLUMN]
    df_mergeH[Activity2_COLUMN] = df_mergeH[TRANS_MODE_COLUMN]
    df_mergeH[Activity3_COLUMN] = df_mergeH[ITEM_COLUMN]
    df_mergeH[RESOURCE_Group_COLUMN] = df_mergeH[LOCATION_COLUMN] + '_' + df_mergeH[SUB_LOCATION_COLUMN] + '_' + df_mergeH[
        TRANS_MODE_COLUMN] + '_' + df_mergeH[ITEM_COLUMN]
    df_mergeH[W_Simultaneous_Capacity_Consumption_Association] = 1
    df_mergeH = df_mergeH[
        [VERSION_NAME_COLUMN, LOCATION_COLUMN, Activity1_COLUMN, Activity2_COLUMN, RESOURCE_COLUMN, Activity3_COLUMN,
         RESOURCE_Group_COLUMN,W_Simultaneous_Capacity_Consumption_Association]]
    df_out_ProdCapaSimultaneous = pd.concat([df_mergeF, df_mergeH], axis=0)

    print_df(df_out_ProdCapaSimultaneous, 'df_out_ProdCapaSimultaneous')
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. (1) df_out_ProdCapaConsumeAsn
    #         (2) df_out_ProdCapaSimultaneous 기준 중복 삭제
    #         (3) df_out_ProdCapaConsumeAsn 컬럼 순서 설정
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    df_out_ProdCapaConsumeAsn = df_out_ProdCapaSimultaneous.drop_duplicates(
        subset=[VERSION_NAME_COLUMN, LOCATION_COLUMN, Activity1_COLUMN, Activity2_COLUMN, RESOURCE_COLUMN,
                Activity3_COLUMN])
    df_out_ProdCapaConsumeAsn[W_Input_Resource_Priority] = 1
    df_out_ProdCapaConsumeAsn[W_Resource_Category] = 'O'
    df_out_ProdCapaConsumeAsn[W_Resource_Consumed_Quantity_Per] = 1
    df_out_ProdCapaConsumeAsn[W_Resource_Consumption_Association] = 1

    df_out_ProdCapaConsumeAsn = df_out_ProdCapaConsumeAsn[
        [VERSION_NAME_COLUMN, LOCATION_COLUMN, Activity1_COLUMN, Activity2_COLUMN, RESOURCE_COLUMN, Activity3_COLUMN,
         W_Input_Resource_Priority, W_Resource_Category, W_Resource_Consumed_Quantity_Per,
         W_Resource_Consumption_Association]]

    print_df(df_out_ProdCapaConsumeAsn, 'df_out_ProdCapaConsumeAsn')
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 5. (1) 최종 Out_Put Save
    ################################################################################################################

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_InputsCapacity, 'df_out_InputsCapacity')
        save_csv_file(df_out_ProdCapaSimultaneous, 'df_out_ProdCapaSimultaneous')
        save_csv_file(df_out_ProdCapaConsumeAsn, 'df_out_ProdCapaConsumeAsn')

    row_count, col_count = df_out_InputsCapacity.shape
    note(f'=====> Final df_out_InputsCapacity rows : {row_count} , Columns : {col_count}')
    row_count, col_count = df_out_ProdCapaSimultaneous.shape
    note(f'=====> Final df_out_ProdCapaSimultaneous rows : {row_count} , Columns : {col_count}')
    row_count, col_count = df_out_ProdCapaConsumeAsn.shape
    note(f'=====> Final df_out_ProdCapaConsumeAsn rows : {row_count} , Columns : {col_count}')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    raise Exception(e)

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(800, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()