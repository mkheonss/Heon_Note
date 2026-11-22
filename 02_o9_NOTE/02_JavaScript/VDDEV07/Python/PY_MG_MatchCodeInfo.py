"""

* 프로그램명
    - PY_MG_MatchCodeInfo

* 내용
     - Production Capacity 정보 Interface
    - 현재는 CAPA 기준 관리만 대상 ( Target은 아님 )

* 변경이력
- 2024.09.05 / ybest7.park (박병훈) / Create

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary
    STEP1. Match Code 대상 OrderLineID Mapping(Original Location Info)정보 Insert
    STEP2~3. Match Code 대상 Location 정보 Insert



* Input Table
    - df_inv_shuffle = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv Shuffle_KRW Amount], Measure.[Inv Shuffle_Org Site ID], Measure.[Inv Shuffle_Plan ID], Measure.[Inv Shuffle_Qty], Measure.[Inv Shuffle_Sales ID], Measure.[Inv Shuffle_To Site], Measure.[Inv Shuffle_USD Amount]} ) on column;
    - df_intransit_shuffle = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Intr Shuffle_BOD Name], Measure.[Intr Shuffle_Billing Doc], Measure.[Intr Shuffle_Billing Item], Measure.[Intr Shuffle_Contaner No], Measure.[Intr Shuffle_DC ETA], Measure.[Intr Shuffle_ETA Date], Measure.[Intr Shuffle_From Site ID], Measure.[Intr Shuffle_ITTS ATA], Measure.[Intr Shuffle_ITTS ETA], Measure.[Intr Shuffle_Invoice Item], Measure.[Intr Shuffle_Invoice No], Measure.[Intr Shuffle_MOD DC ETA],Measure.[Intr Shuffle_Order Line ID], Measure.[Intr Shuffle_Org Site ID], Measure.[Intr Shuffle_Plan ID], Measure.[Intr Shuffle_Po Item], Measure.[Intr Shuffle_Po No], Measure.[Intr Shuffle_Qty], Measure.[Intr Shuffle_Rank No], Measure.[Intr Shuffle_Sales ID]}) on column;
    - df_distorder_shuffle = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Dist Order Shuffle_From Site ID], Measure.[Dist Order Shuffle_Order Line ID], Measure.[Dist Order Shuffle_Org Site ID], Measure.[Dist Order Shuffle_Plan ID], Measure.[Dist Order Shuffle_SS Delivery Date], Measure.[Dist Order Shuffle_SS Qty], Measure.[Dist Order Shuffle_SS Startdate], Measure.[Dist Order Shuffle_Sales ID], Measure.[Dist Order Shuffle_To Site ID]}) on column;
    - df_in_MCLocation = Select ( [Location].[Location] * [Location].[Site Stage].filter(#.Name in { "DC_HUB_MC", "DC_HUB_MC_AP2"  } )) ;


* Output Table
    - df_out_MCMapping = Select ([Version].[Version Name].[CWV_MP] * [Documents].[OrderlineID] ) on row, ({Measure.[W Original Owner Location]}) on column;
    - df_out_MCLocation = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Multi Level SS Association], Measure.[Multi Level SS Hub], Measure.[Preallocation Association], Measure.[Preallocation Hub]}) on column;
* 데이터 삭제
    DELETE DATA FOR MODEL [283.Original Match Code To OrderID Mapping] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
      EXEC plugin instance [PY_MG_MatchCodeInfo] for Measures {[W Original Owner Location]} using scope ( &MPV ) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};

* 데이터 수정
    scope : ([Activity3].[Activity3] * [Activity2].[Activity2] * [Activity1].[Activity1] * [Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item].[Item] );
    Measure.[W Production Holiday] = False;
    end scope;  <- 다시 수정 필요

"""

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
str_instance = 'PY_MG_MatchCodeInfo'
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

        df_inv_shuffle = read_csv_file('df_inv_shuffle')
        df_intransit_shuffle = read_csv_file('df_intransit_shuffle')
        df_distorder_shuffle = read_csv_file('df_distorder_shuffle')
        df_in_MCLocation = read_csv_file('df_in_MCLocation')


    # if df_inv_shuffle.empty:
    #     raise Exception("Exception: df_inv_shuffle is empty")
    #
    # if df_intransit_shuffle.empty:
    #     raise Exception("Exception df_intransit_shuffle is empty")
    #
    # if df_distorder_shuffle.empty:
    #     raise Exception("Exception df_distorder_shuffle is empty")
    #
    # if df_in_MCLocation.empty:
    #     raise Exception("Exception df_in_MCLocation is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_inv_shuffle, 'df_inv_shuffle')
    print_df(df_intransit_shuffle, 'df_intransit_shuffle')
    print_df(df_distorder_shuffle, 'df_distorder_shuffle')
    print_df(df_in_MCLocation, 'df_in_MCLocation')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수설정
    Version_COLUMN = 'Version.[Version Name]'
    Item_COLUMN = 'Item.[Item]'
    Location_COLUMN = 'Location.[Location]'
    Site_Stage_COLUM = 'Location.[Site Stage]'
    OrderLineID_COLUMN = 'Documents.[OrderlineID]'
    TimeWeek_COLUMN = 'Time.[Week]'

    Org_Site_ID = 'Org_Site_ID'
    Inv_Shuffle_Org_Site_ID = 'Inv Shuffle_Org Site ID'
    Intr_Shuffle_Org_Site_ID = 'Intr Shuffle_Org Site ID'
    Dist_Order_Shuffle_Org_Site_ID = 'Dist Order Shuffle_Org Site ID'
    Dist_Order_Shuffle_To_Site_ID = 'Dist Order Shuffle_To Site ID'
    W_Original_Owner_Location = 'W Original Owner Location'
    DC_HUB_MC_AP2 = 'DC_HUB_MC_AP2'
    DC_HUB_MC = 'DC_HUB_MC'
    Multi_Level_SS_Hub = 'Multi Level SS Hub'
    Preallocation_Hub = 'Preallocation Hub'


    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3. (1) df_in_ItemSiteAsn 중복제거 기준 item & Loaction series 생성
    #         (2) Location 조건은 Location & Sub Location은 OR 조건 Item은 And 조건으로 df_in_BOD_Item 필터
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    df_inv_shuffle_mapping = df_inv_shuffle.copy()
    df_inv_shuffle_mapping = df_inv_shuffle_mapping[[Version_COLUMN, OrderLineID_COLUMN, Inv_Shuffle_Org_Site_ID]]
    df_inv_shuffle_mapping[Inv_Shuffle_Org_Site_ID] = df_inv_shuffle_mapping[Inv_Shuffle_Org_Site_ID].astype(str)
    df_inv_shuffle_mapping[Inv_Shuffle_Org_Site_ID] = df_inv_shuffle_mapping[Inv_Shuffle_Org_Site_ID].fillna('-')
    df_inv_shuffle_mapping[Inv_Shuffle_Org_Site_ID] = df_inv_shuffle_mapping[Inv_Shuffle_Org_Site_ID].str.replace('-',
                                                                                                                  '')
    df_inv_shuffle_mapping.drop_duplicates(keep='first', inplace=True)
    df_inv_shuffle_mapping.rename(columns={Inv_Shuffle_Org_Site_ID: W_Original_Owner_Location}, inplace=True)
    df_intransit_shuffle_mapping = df_intransit_shuffle.copy()
    df_intransit_shuffle_mapping = df_intransit_shuffle_mapping[
        [Version_COLUMN, OrderLineID_COLUMN, Intr_Shuffle_Org_Site_ID]]
    df_intransit_shuffle_mapping[Intr_Shuffle_Org_Site_ID] = df_intransit_shuffle_mapping[
        Intr_Shuffle_Org_Site_ID].fillna('')
    df_intransit_shuffle_mapping[Intr_Shuffle_Org_Site_ID] = df_intransit_shuffle_mapping[
        Intr_Shuffle_Org_Site_ID].str.replace('-', '')
    df_intransit_shuffle_mapping.drop_duplicates(keep='first', inplace=True)
    df_intransit_shuffle_mapping.rename(columns={Intr_Shuffle_Org_Site_ID: W_Original_Owner_Location}, inplace=True)
    df_distorder_shuffle_mapping = df_distorder_shuffle.copy()
    df_distorder_shuffle_mapping = df_distorder_shuffle_mapping[
        [Version_COLUMN, OrderLineID_COLUMN, Dist_Order_Shuffle_Org_Site_ID]]
    df_distorder_shuffle_mapping[Dist_Order_Shuffle_Org_Site_ID] = df_distorder_shuffle_mapping[
        Dist_Order_Shuffle_Org_Site_ID].str.replace('-', '')
    df_distorder_shuffle_mapping[Dist_Order_Shuffle_Org_Site_ID] = df_distorder_shuffle_mapping[
        Dist_Order_Shuffle_Org_Site_ID].fillna('')
    df_distorder_shuffle_mapping.drop_duplicates(keep='first', inplace=True)
    df_distorder_shuffle_mapping.rename(columns={Dist_Order_Shuffle_Org_Site_ID: W_Original_Owner_Location},
                                        inplace=True)
    df_out_MCMapping = pd.concat([df_inv_shuffle_mapping, df_intransit_shuffle_mapping, df_distorder_shuffle_mapping],
                                 axis=0)
    df_out_MCMapping[W_Original_Owner_Location] = np.where(df_out_MCMapping[W_Original_Owner_Location] == 'nan', "",
                                                           df_out_MCMapping[W_Original_Owner_Location])
    df_out_MCMapping = df_out_MCMapping.drop_duplicates(keep='first')

    df_out_MCMapping = df_out_MCMapping[df_out_MCMapping[W_Original_Owner_Location] != ''].reset_index(drop=True)

    print_df(df_out_MCMapping, 'df_out_MCMapping')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) df_in_BOD_Item 과 df_in_BOD_List merge하여 1차 Output Data 생성
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    df_inv_shuffle_Site = df_inv_shuffle.copy()
    df_inv_shuffle_Site = df_inv_shuffle_Site[[Version_COLUMN, Item_COLUMN, Location_COLUMN, Inv_Shuffle_Org_Site_ID]]
    df_inv_shuffle_Site[Inv_Shuffle_Org_Site_ID] = df_inv_shuffle_Site[Inv_Shuffle_Org_Site_ID].fillna('')
    df_inv_shuffle_Site[Inv_Shuffle_Org_Site_ID] = df_inv_shuffle_Site[Inv_Shuffle_Org_Site_ID].str.replace('-', '')
    df_inv_shuffle_Site.drop_duplicates(subset=[Version_COLUMN, Item_COLUMN, Location_COLUMN, Inv_Shuffle_Org_Site_ID],
                                        inplace=True)
    df_inv_shuffle_Site.rename(columns={Inv_Shuffle_Org_Site_ID: Org_Site_ID}, inplace=True)
    df_intransit_shuffle_Site = df_intransit_shuffle.copy()
    df_intransit_shuffle_Site = df_intransit_shuffle_Site[
        [Version_COLUMN, Item_COLUMN, Location_COLUMN, Intr_Shuffle_Org_Site_ID]]
    df_intransit_shuffle_Site[Intr_Shuffle_Org_Site_ID] = df_intransit_shuffle_Site[Intr_Shuffle_Org_Site_ID].fillna('')
    df_intransit_shuffle_Site[Intr_Shuffle_Org_Site_ID] = df_intransit_shuffle_Site[
        Intr_Shuffle_Org_Site_ID].str.replace('-', '')
    df_intransit_shuffle_Site.drop_duplicates(
        subset=[Version_COLUMN, Item_COLUMN, Location_COLUMN, Intr_Shuffle_Org_Site_ID], inplace=True)
    df_intransit_shuffle_Site.rename(columns={Intr_Shuffle_Org_Site_ID: Org_Site_ID}, inplace=True)
    df_distorder_shuffle_Site = df_distorder_shuffle.copy()
    df_distorder_shuffle_Site = df_distorder_shuffle_Site[
        [Version_COLUMN, Item_COLUMN, Location_COLUMN, Dist_Order_Shuffle_To_Site_ID]]
    df_distorder_shuffle_Site[Dist_Order_Shuffle_To_Site_ID] = df_distorder_shuffle_Site[
        Dist_Order_Shuffle_To_Site_ID].str.replace('-', '')
    df_distorder_shuffle_Site[Dist_Order_Shuffle_To_Site_ID] = df_distorder_shuffle_Site[
        Dist_Order_Shuffle_To_Site_ID].fillna('')
    df_distorder_shuffle_Site.drop_duplicates(
        subset=[Version_COLUMN, Item_COLUMN, Location_COLUMN, Dist_Order_Shuffle_To_Site_ID], inplace=True)
    df_distorder_shuffle_Site.rename(columns={Dist_Order_Shuffle_To_Site_ID: Org_Site_ID}, inplace=True)
    df_MCItemSite = pd.concat([df_inv_shuffle_Site, df_intransit_shuffle_Site, df_distorder_shuffle_Site], axis=0)
    # df_MCItemSite.drop_duplicates(subset=[Version_COLUMN, Item_COLUMN, Location_COLUMN], inplace=True)

    df_MCItemSite = df_MCItemSite[df_MCItemSite[Org_Site_ID] != '']

    df_MCItemSite = df_MCItemSite[df_MCItemSite[Org_Site_ID] !='']
    print_df(df_MCItemSite, 'df_MCItemSite')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) df_in_BOD_Item_mtrl 기준 Location & Item 필터 및 merge data 생성
    #         (2) 생성된 merge data와 df_in_BOD_List_Mtrl merge하여 mergeB 생성
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    df_in_MCLocation_tempA = df_in_MCLocation[df_in_MCLocation[Site_Stage_COLUM] == DC_HUB_MC_AP2]
    df_MCItemSite_tempA = df_MCItemSite.merge(df_in_MCLocation_tempA, on=Location_COLUMN, how='inner',
                                              suffixes=('_A', '_B'))
    df_in_MCLocation_tempB = df_in_MCLocation[df_in_MCLocation[Site_Stage_COLUM] == DC_HUB_MC]
    df_MCItemSite_tempA = df_MCItemSite_tempA.merge(df_in_MCLocation_tempB, left_on=Org_Site_ID,
                                                    right_on=Location_COLUMN, suffixes=('_A', '_B'))
    df_MCItemSite_tempA[Location_COLUMN] = df_MCItemSite_tempA[Org_Site_ID]
    df_MCItemSite_tempA[Preallocation_Hub] = df_MCItemSite_tempA['Location.[Location]_A']

    df_MCItemSite_tempA = df_MCItemSite_tempA[[Version_COLUMN, Item_COLUMN, Location_COLUMN, Preallocation_Hub]]

    df_MCItemSite_tempB = df_MCItemSite.merge(df_in_MCLocation_tempA, on=Location_COLUMN, how='inner',
                                              suffixes=('_A', '_B'))
    df_MCItemSite_tempB[Preallocation_Hub] = df_MCItemSite_tempB[Location_COLUMN]
    df_MCItemSite_tempB = df_MCItemSite_tempB[[Version_COLUMN, Item_COLUMN, Location_COLUMN, Preallocation_Hub]]
    print_df(df_MCItemSite_tempA, 'df_MCItemSite_tempA')
    print_df(df_MCItemSite_tempB, 'df_MCItemSite_tempB')

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. (1) df_in_BOMComponent 의 Item 중 df_in_ItemSiteAsn 포함된 것 들만 필터링
    #         (2) df_in_BOMComponent 와 df_in_BOMMaster merge 하여 mergeC 생성
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')
    df_out_MCLocation = pd.concat([df_MCItemSite_tempA, df_MCItemSite_tempB], axis=0)
    df_out_MCLocation[Multi_Level_SS_Hub] = 1
    df_out_MCLocation = df_out_MCLocation[
        [Version_COLUMN, Item_COLUMN, Location_COLUMN, Multi_Level_SS_Hub, Preallocation_Hub]]
    print_df(df_out_MCLocation, 'df_out_MCLocation')
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) 최종 Out_Put Save
    ################################################################################################################
    step(700, '=====> STEP 7(Start) : output data machining')

    row_count, col_count = df_out_MCLocation.shape
    note(f'=====> Final df_out_MCLocation rows : {row_count} , Columns : {col_count}')
    print_df(df_out_MCLocation, 'df_out_MCLocation')

    row_count, col_count = df_out_MCMapping.shape
    note(f'=====> Final df_out_MCMapping rows : {row_count} , Columns : {col_count}')
    print_df(df_out_MCMapping, 'df_out_MCMapping')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_MCLocation, 'df_out_MCLocation')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_MCMapping, 'df_out_MCMapping')


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