"""

* 프로그램명
    - PY_MG_ActivityParameters

* 수정일 : 2024/11/12

* 내용
    - BOD/BOM Activity Parameter 반영
    - Effectiveness, BOD Transit Time, Shipping L/T
    - Plan 대상 Item Site Association (Measure Group : Item Site Asn) 에서
      실제 현재 PLAN 대상에 대한 Item - Location Association 만 반영

* 변경이력
- 2024.06.20 / ybest7.park (박병훈) / Create

* Input
- df_in_MaterialProdAsn = pd.read_csv(' .csv')


* Flow Summary
    STEP1. Plan 대상 Item, Location(df_in_ItemSiteAsn) 정보 발췌
    STEP2. Plan 대상 BODLane ITEM (ITEM별 BOD) Filtering
    STEP3. STEP2 에서 구성된 Set을 대상으로 df_out_MaterialProdAsn Measure 정보 Insert

* Input Table
    - df_in_ItemSiteAsn = Select (&MPV  * [Location].[Location] * [Item].[Item] ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
                         [ Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage],Measure.[Dummy]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);]
        ※ DISTINCT [Item].[Item] * [Location].[Location]
    - df_in_BOD_List = Select ( &MPV * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT], Measure.[BOD List_Update Time], Measure.[BOD List_Updated By]}) on column.filter(Measure.[BOD List_BOD Valid] == "Y");
                      [ select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List_BOD Frozen], Measure.[BOD List_BOD LT], Measure.[BOD List_BOD Valid], Measure.[BOD List_Created By], Measure.[BOD List_Creation Time], Measure.[BOD List_Eff Enddate], Measure.[BOD List_Eff Startdate], Measure.[BOD List_Priority], Measure.[BOD List_Shipment LT], Measure.[BOD List_Update Time], Measure.[BOD List_Updated By],Measure.[Dummy] }) on column.filter(Measure.[BOD List_BOD Valid] == "Y") ;]
    - df_in_BOD_Item = Select (&MPV * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT], Measure.[BOD Item_BOD LT_Inherit], Measure.[BOD Item_Created By], Measure.[BOD Item_Creation Time], Measure.[BOD Item_Cur Status], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Master Prty], Measure.[BOD Item_Master Ship LT], Measure.[BOD Item_Master Tran Time], Measure.[BOD Item_Min Lot Qty], Measure.[BOD Item_Multi Lot Qty], Measure.[BOD Item_Need Check], Measure.[BOD Item_Period SET Detail], Measure.[BOD Item_Period1], Measure.[BOD Item_Period2], Measure.[BOD Item_Period3], Measure.[BOD Item_Priority], Measure.[BOD Item_Priority_Inherit], Measure.[BOD Item_Prod Item], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Shipment LT_Inherit], Measure.[BOD Item_Time Phased BOD], Measure.[BOD Item_Time Phased Prty], Measure.[BOD Item_Time Phased Shipment], Measure.[BOD Item_To Item], Measure.[BOD Item_Update Time], Measure.[BOD Item_Updated By]}) on column;
                      [Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT], Measure.[BOD Item_Created By], Measure.[BOD Item_Creation Time], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Min Lot Qty], Measure.[BOD Item_Multi Lot Qty],  Measure.[BOD Item_Period SET Detail], Measure.[BOD Item_Period1], Measure.[BOD Item_Period2], Measure.[BOD Item_Period3], Measure.[BOD Item_Priority], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Time Phased BOD], Measure.[BOD Item_Time Phased Prty], Measure.[BOD Item_Time Phased Shipment], Measure.[BOD Item_To Item], Measure.[BOD Item_Update Time], Measure.[BOD Item_Updated By],Measure.[Dummy]}) on column;]
    - df_in_BODItemMtrlFull =  Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_Lot Size],Measure.[Dummy]}) on column;
    - df_in_BOD_Item_mtrl =  Select (&MPV * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lock Flag], Measure.[BOD Item Mtrl_Lot Size], Measure.[BOD Item Mtrl_Lot Type]}) on column.filter((isnull(Measure.[BOD Item Mtrl_EFF Enddate])||Measure.[BOD Item Mtrl_EFF Enddate]> Measure.[W Plan Start Date])&&(isnull(Measure.[BOD Item Mtrl_EFF Startdate])||Measure.[BOD Item Mtrl_EFF Startdate]< Measure.[W Plan End Date]));
                             [Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lock Flag], Measure.[BOD Item Mtrl_Lot Size], Measure.[BOD Item Mtrl_Lot Type],Measure.[Dummy]}) on column.filter((isnull(Measure.[BOD Item Mtrl_EFF Enddate])||Measure.[BOD Item Mtrl_EFF Enddate]> Measure.[W Plan Start Date])&&(isnull(Measure.[BOD Item Mtrl_EFF Startdate])||Measure.[BOD Item Mtrl_EFF Startdate]< Measure.[W Plan End Date]));]
    - df_in_BOMMaster = Select (&MPV  * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column ;
                       [Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column ;]
    - df_in_BODItem_INF = Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Infinite_EFF Enddate], Measure.[BOD Item Mtrl Infinite_EFF Startdate], Measure.[Dummy]}) on column;
    - df_in_BODItemUnConst = Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl UnConst_EFF Enddate], Measure.[BOD Item Mtrl UnConst_EFF Startdate], Measure.[Dummy]}) on column;


* Output Table
    - df_out_BODActivityParameters =  Select ([Version].[Version Name].[CWV_MP] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Cost Per Unit], Measure.[W Activity End Date], Measure.[W Activity Flow Priority], Measure.[W Activity Lead Time], Measure.[W Activity Lead Time Standard Deviation], Measure.[W Activity Mandatory Offset], Measure.[W Activity ReEntrant], Measure.[W Activity Start Date], Measure.[W Lot Size Penalty Per Unit Qty], Measure.[W Lot Size Priority]}) on column;
    - df_out_BOMActivityParameters =  Select ([Version].[Version Name].[CWV_MP] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Cost Per Unit], Measure.[W Activity End Date], Measure.[W Activity Flow Priority], Measure.[W Activity Lead Time], Measure.[W Activity Lead Time Standard Deviation], Measure.[W Activity Mandatory Offset], Measure.[W Activity ReEntrant], Measure.[W Activity Start Date], Measure.[W Lot Size Penalty Per Unit Qty], Measure.[W Lot Size Priority]}) on column;

* 데이터 삭제
    - DELETE DATA FOR MODEL [001.007W Solver Inputs Activity Parameters] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
    EXEC plugin instance [PY_MG_ActivityParameters] for Measures {[W Item Location Association]} using scope ( &MPV) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};


"""
import gc
from NSCMCommon import NSCMCommon as com
from NSCMCommon import VDCommon as vdCommon
import os.path
import time
import datetime
import decimal
import math
import traceback
import tracemalloc
import warnings

import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re
import psutil

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_ActivityParameters'
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

def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

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
        df_in_BOD_List = read_csv_file('df_in_BOD_List')
        df_in_BOD_Item = read_csv_file('df_in_BOD_Item')
        df_in_BODItemMtrlFull = read_csv_file('df_in_BODItemMtrlFull')
        df_in_BOD_Item_mtrl = read_csv_file('df_in_BOD_Item_mtrl')
        df_in_BOMMaster = read_csv_file('df_in_BOMMaster')
        df_in_BODItem_INF = read_csv_file('df_in_BODItem_INF')
        df_in_BODItemUnConst = read_csv_file('df_in_BODItemUnConst')

    # if df_in_ItemSiteAsn.empty:
    #     raise Exception("Exception: df_in_ItemSiteAsn is empty")
    #
    # if df_in_BOD_List.empty:
    #     raise Exception("Exception df_in_BOD_List is empty")
    #
    # if df_in_BOD_Item.empty:
    #     raise Exception("Exception df_in_BOD_Item is empty")
    #
    # if df_in_BODItemMtrlFull.empty:
    #     raise Exception("Exception df_in_BODItemMtrlFull is empty")
    #
    # if df_in_BOD_Item_mtrl.empty:
    #     raise Exception("Exception df_in_BOD_Item_mtrl is empty")
    #
    # if df_in_BOMMaster.empty:
    #     raise Exception("Exception df_in_BOMMaster is empty")
    #
    # if df_in_BODItem_INF.empty:
    #     raise Exception("Exception df_in_BODItem_INF is empty")
    #
    # if df_in_BODItemUnConst.empty:
    #     raise Exception("Exception df_in_BODItemUnConst is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',True)
    print_df(df_in_BOD_List, 'df_in_BOD_List',True)
    print_df(df_in_BOD_Item, 'df_in_BOD_Item',True)
    print_df(df_in_BODItemMtrlFull, 'df_in_BODItemMtrlFull',True)
    print_df(df_in_BOD_Item_mtrl, 'df_in_BOD_Item_mtrl',True)
    print_df(df_in_BOMMaster, 'df_in_BOMMaster',True)
    print_df(df_in_BODItem_INF, 'df_in_BODItem_INF',True)
    print_df(df_in_BODItemUnConst, 'df_in_BODItemUnConst',True)


    # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #     paramOutVersion = PARAM_OUTVERSION_VALUE

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
    BOD_Item_EFF_Enddate = 'BOD Item_Eff Enddate'
    BOD_List_EFF_Enddate = 'BOD List_Eff Enddate'
    BOD_List_BOD_LT = 'BOD List_BOD LT'
    BOD_Item_BOD_LT = 'BOD Item_BOD LT'
    BOD_Item_Shipment_LT = 'BOD Item_Shipment LT'
    BOD_List_Shipment_LT = 'BOD List_Shipment LT'
    BOD_Item_EFF_Startdate = 'BOD Item_Eff Startdate'
    BOD_List_Eff_Startdate = 'BOD List_Eff Startdate'
    BOM_Master_Eff_Startdate = 'BOM Master_Eff Startdate'
    BOM_Master_Eff_Enddate = 'BOM Master_Eff Enddate'
    BOM_Master_BOM_ID = 'BOM Master_BOM ID'
    BOD_Item_Mtrl_EFF_Startdate = 'BOD Item Mtrl_EFF Startdate'
    BOD_Item_Mtrl_EFF_Enddate = 'BOD Item Mtrl_EFF Enddate'
    BOD_List_Mtrl_EFF_Startdate = 'BOD List Mtrl_EFF Startdate'
    BOD_List_Mtrl_EFF_Enddate = 'BOD List Mtrl_EFF Enddate'
    BOD_Item_Mtrl_Full_EFF_Startdate = 'BOD Item Mtrl Full_EFF Startdate'
    BOD_Item_Mtrl_Full_EFF_Enddate = 'BOD Item Mtrl Full_EFF Enddate'
    BOD_Item_Mtrl_Infinite_EFF_Startdate = 'BOD Item Mtrl Infinite_EFF Startdate'
    BOD_Item_Mtrl_Infinite_EFF_Enddate = 'BOD Item Mtrl Infinite_EFF Enddate'
    BOD_Item_Mtrl_UnConst_EFF_Enddate = 'BOD Item Mtrl UnConst_EFF Enddate'
    BOD_Item_Mtrl_UnConst_EFF_Startdate = 'BOD Item Mtrl UnConst_EFF Startdate'

    W_Material_Consumption_Association = 'W Material Consumption Association'
    W_Material_Consumption_Quantity_Per = 'W Material Consumption Quantity Per'
    W_Activity_End_Date = 'W Activity End Date'
    W_Activity_Flow_Priority = 'W Activity Flow Priority'
    W_Activity_Lead_Time = 'W Activity Lead Time'
    W_Activity_Mandatory_Offset = 'W Activity Mandatory Offset'
    W_Activity_Start_Date = 'W Activity Start Date'
    W_Activity_Cost_Per_Unit = 'W Activity Cost Per Unit'
    W_Activity_Lead_Time_Standard_Deviation = ' W Activity Lead Time Standard Deviation'
    W_Activity_ReEntrant = 'W Activity ReEntrant'
    W_Lot_Size_Penalty_Per_Unit_Qty = 'W Lot Size Penalty Per Unit Qty'
    W_Lot_Size_Priority = 'W Lot Size Priority'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) df_in_ItemSiteAsn 중복제거 기준 item & Loaction series 생성
    #         (2) Location 조건은 Location & Sub Location은 OR 조건 Item은 And 조건으로 df_in_BOD_Item 필터
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')
    # df_in_ItemSiteAsn의 Unique한 Location values를 series로 생성
    Location_series = df_in_ItemSiteAsn[LOCATION_COLUMN].unique()
    # df_in_ItemSiteAsn의 Unique한 Item values를 series로 생성
    Item_series = df_in_ItemSiteAsn[ITEM_COLUMN].unique()
    # df_in_BOD_Item 조건에서 생성한 series로 필터링
    df_in_BOD_Item = df_in_BOD_Item[(df_in_BOD_Item[LOCATION_COLUMN].isin(Location_series)) | (
        df_in_BOD_Item[SUB_LOCATION_COLUMN].isin(Location_series))]
    df_in_BOD_Item = df_in_BOD_Item[df_in_BOD_Item[ITEM_COLUMN].isin(Item_series)]

    df_in_BOD_Item = df_in_BOD_Item.merge(df_in_BOD_List, on=[VERSION_NAME_COLUMN, LOCATION_COLUMN,
                                                         TRANSPORTMODE_COLUMN, SUB_LOCATION_COLUMN], how='inner')
    df_in_BOD_Item[Activity1_COLUMN] = df_in_BOD_Item[LOCATION_COLUMN] + "_" + df_in_BOD_Item[
        SUB_LOCATION_COLUMN] + '_' + df_in_BOD_Item[
                                           TRANSPORTMODE_COLUMN]
    df_in_BOD_Item[Activity2_COLUMN] = df_in_BOD_Item[TRANSPORTMODE_COLUMN]
    df_in_BOD_Item[Activity3_COLUMN] = df_in_BOD_Item[ITEM_COLUMN]

    df_in_BOD_Item[W_Activity_End_Date] = np.where(df_in_BOD_Item[BOD_Item_EFF_Enddate].isna(),
                                                   df_in_BOD_Item[BOD_List_EFF_Enddate],
                                                   df_in_BOD_Item[BOD_Item_EFF_Enddate] )
    df_in_BOD_Item[W_Activity_Flow_Priority] =''
    df_in_BOD_Item[W_Activity_Mandatory_Offset] = np.where(df_in_BOD_Item[BOD_Item_Shipment_LT].isna(),
                                                           df_in_BOD_Item[BOD_List_Shipment_LT],
                                                           df_in_BOD_Item[BOD_Item_Shipment_LT])
    df_in_BOD_Item[W_Activity_Lead_Time] = np.where(df_in_BOD_Item[BOD_Item_BOD_LT].isna(),
                                                    df_in_BOD_Item[BOD_List_BOD_LT],
                                                    df_in_BOD_Item[BOD_Item_BOD_LT])
    df_in_BOD_Item[W_Activity_Start_Date] = np.where(df_in_BOD_Item[BOD_Item_EFF_Startdate].isna(),
                                                     df_in_BOD_Item[BOD_List_Eff_Startdate],
                                                     df_in_BOD_Item[BOD_Item_EFF_Startdate])

    df_out_BODActivityParameters = df_in_BOD_Item[
        [VERSION_NAME_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN, W_Activity_End_Date,
         W_Activity_Flow_Priority, W_Activity_Lead_Time, W_Activity_Mandatory_Offset, W_Activity_Start_Date]]

    delete_dfs(df_in_BOD_Item)
    print_df(df_out_BODActivityParameters, 'df_out_BODActivityParameters', True)

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) df_in_BOD_Item_mtrl 기준 Location & Item 필터 및 merge data 생성
    #         (2) 생성된 merge data와 df_in_BODItemMtrlFull merge하여 mergeB 생성
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')
    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[(df_in_BODItemMtrlFull[LOCATION_COLUMN].isin(Location_series)) | (
        df_in_BODItemMtrlFull[SUB_LOCATION_COLUMN].isin(Location_series))]
    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[df_in_BODItemMtrlFull[Item_Material_COLUMN].isin(Item_series)]
    df_in_BODItemMtrlFull[Activity1_COLUMN] = df_in_BODItemMtrlFull[LOCATION_COLUMN] + '_' + df_in_BODItemMtrlFull[
        SUB_LOCATION_COLUMN] + '_' + df_in_BODItemMtrlFull[TRANSPORTMODE_COLUMN]
    df_in_BODItemMtrlFull[Activity2_COLUMN] = df_in_BODItemMtrlFull[TRANSPORTMODE_COLUMN]
    df_in_BODItemMtrlFull[Activity3_COLUMN] = df_in_BODItemMtrlFull[Item_Material_COLUMN]
    df_in_BODItemMtrlFull[W_Activity_End_Date] = df_in_BODItemMtrlFull[BOD_Item_Mtrl_Full_EFF_Enddate]
    df_in_BODItemMtrlFull[W_Activity_Flow_Priority] = 1
    df_in_BODItemMtrlFull[W_Activity_Lead_Time] = 0
    df_in_BODItemMtrlFull[W_Activity_Mandatory_Offset] = ''
    df_in_BODItemMtrlFull[W_Activity_Start_Date] = df_in_BODItemMtrlFull[BOD_Item_Mtrl_Full_EFF_Startdate]
    df_in_BODItemMtrlFull = df_in_BODItemMtrlFull[
        [VERSION_NAME_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN, W_Activity_End_Date,
         W_Activity_Flow_Priority, W_Activity_Lead_Time, W_Activity_Mandatory_Offset, W_Activity_Start_Date]]
    df_out_BODActivityParameters = pd.concat([df_out_BODActivityParameters, df_in_BODItemMtrlFull], axis=0)

    delete_dfs(df_in_BODItemMtrlFull)
    print_df(df_out_BODActivityParameters, 'df_out_BODActivityParameters',True)
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 5.  (1) df_in_BOMMaster의 Item & Location 기준으로 df_in_ItemSiteAsn  필터링
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')
    df_in_BOMMaster = df_in_BOMMaster[
        (df_in_BOMMaster[LOCATION_COLUMN].isin(Location_series)) & (df_in_BOMMaster[BOMID_COLUMN].isin(Item_series))]
    df_in_BOMMaster[Activity1_COLUMN] = df_in_BOMMaster[BOMINFOID]
    df_in_BOMMaster[Activity2_COLUMN] = 'RT_' + df_in_BOMMaster[BOMINFOID] + '_@' + df_in_BOMMaster[LOCATION_COLUMN]
    df_in_BOMMaster[Activity3_COLUMN] = df_in_BOMMaster[BOMID_COLUMN]
    df_in_BOMMaster[W_Activity_Start_Date] = df_in_BOMMaster[BOM_Master_Eff_Startdate]
    df_in_BOMMaster[W_Activity_End_Date] = df_in_BOMMaster[BOM_Master_Eff_Enddate]
    df_in_BOMMaster[W_Activity_Flow_Priority] = ''
    df_in_BOMMaster[W_Activity_Mandatory_Offset] = ''
    df_in_BOMMaster[W_Activity_Lead_Time] = ''

    df_out_BOMActivityParameters = df_in_BOMMaster[
        [VERSION_NAME_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN, W_Activity_End_Date,
         W_Activity_Flow_Priority, W_Activity_Lead_Time, W_Activity_Mandatory_Offset, W_Activity_Start_Date]]

    delete_dfs(df_in_BOMMaster)
    print_df(df_out_BOMActivityParameters, 'df_out_BOMActivityParameters',True)
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. (1) 최종 Out_Put Save (df_out_BODActivityParameters & df_out_BOMActivityParameters)
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    df_in_BODItem_INF[Activity1_COLUMN] = df_in_BODItem_INF[LOCATION_COLUMN] + '_' + df_in_BODItem_INF[
        SUB_LOCATION_COLUMN] + '_' + df_in_BODItem_INF[TRANSPORTMODE_COLUMN]
    df_in_BODItem_INF[Activity2_COLUMN] = df_in_BODItem_INF[TRANSPORTMODE_COLUMN]
    df_in_BODItem_INF[Activity3_COLUMN] = df_in_BODItem_INF[Item_Material_COLUMN]
    df_in_BODItem_INF[W_Activity_Start_Date] = df_in_BODItem_INF[BOD_Item_Mtrl_Infinite_EFF_Startdate]
    df_in_BODItem_INF[W_Activity_End_Date] = df_in_BODItem_INF[BOD_Item_Mtrl_Infinite_EFF_Enddate]
    df_in_BODItem_INF[W_Activity_Flow_Priority] = 99999
    df_in_BODItem_INF[W_Activity_Lead_Time] =''
    df_in_BODItem_INF[W_Activity_Mandatory_Offset] =''

    df_in_BODItem_INF = df_in_BODItem_INF[
        [VERSION_NAME_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN, W_Activity_End_Date,
         W_Activity_Flow_Priority, W_Activity_Lead_Time, W_Activity_Mandatory_Offset, W_Activity_Start_Date]]

    print_df(df_in_BODItem_INF, 'df_in_BODItem_INF',True)
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 7. (1) df_in_BODItemUnConst 추가 Input
    ################################################################################################################
    step(700, '=====> STEP 7(Start) : output data machining')
    df_in_BODItemUnConst = df_in_BODItemUnConst.rename(columns={Item_Material_COLUMN:ITEM_COLUMN})
    df_in_BODItemUnConst[Activity1_COLUMN] = df_in_BODItemUnConst[LOCATION_COLUMN] + '_' + df_in_BODItemUnConst[
        SUB_LOCATION_COLUMN] + '_' + df_in_BODItemUnConst[TRANSPORTMODE_COLUMN]
    df_in_BODItemUnConst[Activity2_COLUMN] = df_in_BODItemUnConst[TRANSPORTMODE_COLUMN]
    df_in_BODItemUnConst[Activity3_COLUMN] = df_in_BODItemUnConst[ITEM_COLUMN]
    df_in_BODItemUnConst[W_Activity_Start_Date] = df_in_BODItemUnConst[BOD_Item_Mtrl_UnConst_EFF_Startdate]
    df_in_BODItemUnConst[W_Activity_End_Date] = df_in_BODItemUnConst[BOD_Item_Mtrl_UnConst_EFF_Enddate]
    df_in_BODItemUnConst[W_Activity_Flow_Priority] = 99999
    df_in_BODItemUnConst[W_Activity_Lead_Time] = ' '
    df_in_BODItemUnConst[W_Activity_Mandatory_Offset] = ' '
    df_in_BODItemUnConst = df_in_BODItemUnConst[
        [VERSION_NAME_COLUMN, Activity1_COLUMN, Activity2_COLUMN, Activity3_COLUMN, W_Activity_End_Date,
         W_Activity_Flow_Priority, W_Activity_Lead_Time, W_Activity_Mandatory_Offset, W_Activity_Start_Date]]

    print_df(df_in_BODItemUnConst, 'df_in_BODItemUnConst',True)
    step(700, '=====> STEP 7(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 8. (1) 최종 Out_Put Save (df_out_BODActivityParameters & df_out_BOMActivityParameters)
    ################################################################################################################
    step(800, '=====> STEP 8(Start) : output data machining')

    df_out_BODActivityParameters = pd.concat([df_out_BODActivityParameters, df_in_BODItem_INF, df_in_BODItemUnConst],
                                             ignore_index=True, axis=0)

    print_df(df_out_BODActivityParameters, 'df_out_BODActivityParameters')
    step(800, '=====> STEP 8(End) : Check memory usage & runtime')


    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_BODActivityParameters, 'df_out_BODActivityParameters')
        save_csv_file(df_out_BOMActivityParameters, 'df_out_BOMActivityParameters')

    row_count, col_count = df_out_BODActivityParameters.shape
    note(f'=====> Final df_out_BODActivityParameters rows : {row_count} , Columns : {col_count}')
    row_count, col_count = df_out_BOMActivityParameters.shape
    note(f'=====> Final df_out_BOMActivityParameters rows : {row_count} , Columns : {col_count}')

    step(800, '=====> STEP 8(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_BODActivityParameters = pd.DataFrame([], columns=[])
    df_out_BOMActivityParameters = pd.DataFrame([], columns=[])

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