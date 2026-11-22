

"""

* 프로그램명
    - PY_MNG_VersionCopy

* 수정일 : 20204-11-18

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.11.18 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_TactTime = Select (&CWV * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column;
   - df_in_Inventory = Select ( &CWV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv_KRW Amount], Measure.[Inv_Plan ID], Measure.[Inv_Qty], Measure.[Inv_Sales ID], Measure.[Inv_To Site], Measure.[Inv_USD Amount]}) on column;
   - df_in_Intransit = Select ( &CWV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Intr_BOD Name], Measure.[Intr_Billing Doc], Measure.[Intr_Billing Item], Measure.[Intr_Contaner No], Measure.[Intr_DC ETA], Measure.[Intr_ETA Date], Measure.[Intr_From Site ID], Measure.[Intr_ITTS ATA], Measure.[Intr_ITTS ETA], Measure.[Intr_Invoice Item], Measure.[Intr_Invoice No], Measure.[Intr_MOD DC ETA], Measure.[Intr_Order Line ID], Measure.[Intr_Plan ID], Measure.[Intr_Po Item], Measure.[Intr_Po No], Measure.[Intr_Qty], Measure.[Intr_Rank No]}) on column;
   - df_in_InvShuffle = Select ( &CWV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv Shuffle_KRW Amount], Measure.[Inv Shuffle_Org Site ID], Measure.[Inv Shuffle_Plan ID], Measure.[Inv Shuffle_Qty], Measure.[Inv Shuffle_Sales ID], Measure.[Inv Shuffle_To Site], Measure.[Inv Shuffle_USD Amount]}) on column;
   - df_in_IntrShuffle = Select ( &CWV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Intr Shuffle_BOD Name], Measure.[Intr Shuffle_Billing Doc], Measure.[Intr Shuffle_Billing Item], Measure.[Intr Shuffle_Contaner No], Measure.[Intr Shuffle_DC ETA], Measure.[Intr Shuffle_ETA Date], Measure.[Intr Shuffle_From Site ID], Measure.[Intr Shuffle_ITTS ATA], Measure.[Intr Shuffle_ITTS ETA], Measure.[Intr Shuffle_Invoice Item], Measure.[Intr Shuffle_Invoice No], Measure.[Intr Shuffle_MOD DC ETA], Measure.[Intr Shuffle_Order Line ID], Measure.[Intr Shuffle_Org Site ID], Measure.[Intr Shuffle_Plan ID], Measure.[Intr Shuffle_Po Item], Measure.[Intr Shuffle_Po No], Measure.[Intr Shuffle_Qty], Measure.[Intr Shuffle_Rank No], Measure.[Intr Shuffle_Sales ID]}) on column;
   - df_in_DemandW = Select (&CWV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Ship To] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[Dmd W_BAL], Measure.[Dmd W_Cust Rank], Measure.[Dmd W_Dmd Rank], Measure.[Dmd W_Global Prty], Measure.[Dmd W_ID], Measure.[Dmd W_Leadtime Due], Measure.[Dmd W_Local Prty], Measure.[Dmd W_Measure Rank], Measure.[Dmd W_No Plan], Measure.[Dmd W_Plan ID], Measure.[Dmd W_Preference], Measure.[Dmd W_Prod Rank], Measure.[Dmd W_Prty], Measure.[Dmd W_Prty Seq], Measure.[Dmd W_Qty], Measure.[Dmd W_Week Rank]}) on column;
   - df_in_SiteAP2Map = Select ( &CWV  * [Location].[Location] ) on row, ({Measure.[Site AP2 Map_GC], Measure.[Site AP2 Map_Ship To], Measure.[Site AP2 Map_Status], Measure.[Site AP2 Map_Valid Flag]}) on column;
   - df_in_MfgPlan = Select (&CWV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Finish Date], Measure.[Mfg Plan_Line Name], Measure.[Mfg Plan_Open Qty], Measure.[Mfg Plan_Order Line ID], Measure.[Mfg Plan_Plan ID], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_Rank No], Measure.[Mfg Plan_Status], Measure.[Mfg Plan_To Site ID]}) on column;
   - df_in_DistOrder = Select (&CWV* [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Dist Order_From Site ID], Measure.[Dist Order_Order Line ID], Measure.[Dist Order_Plan ID], Measure.[Dist Order_SS Delivery Date], Measure.[Dist Order_SS Qty], Measure.[Dist Order_SS Startdate], Measure.[Dist Order_Sales ID], Measure.[Dist Order_To Site ID]}) on column;
   - df_in_VendorMtrl = Select (&CWV* [Location].[Location] * [Item Material].[Item Material] * [Vendor].[Vendor] * [Global Top].[GT Code] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Quota]}) on column;
   - df_in_MtrlInfoRecord = Select (&CWV* [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] * [Vendor].[Vendor] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Mtrl Info Record_Category], Measure.[Mtrl Info Record_Country], Measure.[Mtrl Info Record_Currency], Measure.[Mtrl Info Record_Description], Measure.[Mtrl Info Record_Exchange Rate], Measure.[Mtrl Info Record_Info Price USD], Measure.[Mtrl Info Record_Intransit LT], Measure.[Mtrl Info Record_Plan Del Time], Measure.[Mtrl Info Record_Price], Measure.[Mtrl Info Record_Price Unit], Measure.[Mtrl Info Record_Purchase Org], Measure.[Mtrl Info Record_Quota], Measure.[Mtrl Info Record_Ship Instructions], Measure.[Mtrl Info Record_Supplier LT], Measure.[Mtrl Info Record_Valid From], Measure.[Mtrl Info Record_Valid To], Measure.[Mtrl Info Record_Valuation Type], Measure.[Mtrl Info Record_Vendor Schema Grp]}) on column;
   - df_in_SalesItemAsn = Select (&CWV * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column;

* Output Table
    - df_out_TactTime = Select (&MPV * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column;
   - df_out_Inventory = Select ( &MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv_KRW Amount], Measure.[Inv_Plan ID], Measure.[Inv_Qty], Measure.[Inv_Sales ID], Measure.[Inv_To Site], Measure.[Inv_USD Amount]}) on column;
   - df_out_Intransit = Select ( &MPV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Intr_BOD Name], Measure.[Intr_Billing Doc], Measure.[Intr_Billing Item], Measure.[Intr_Contaner No], Measure.[Intr_DC ETA], Measure.[Intr_ETA Date], Measure.[Intr_From Site ID], Measure.[Intr_ITTS ATA], Measure.[Intr_ITTS ETA], Measure.[Intr_Invoice Item], Measure.[Intr_Invoice No], Measure.[Intr_MOD DC ETA], Measure.[Intr_Order Line ID], Measure.[Intr_Plan ID], Measure.[Intr_Po Item], Measure.[Intr_Po No], Measure.[Intr_Qty], Measure.[Intr_Rank No]}) on column;
   - df_out_InvShuffle = Select ( &MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Inv Shuffle_KRW Amount], Measure.[Inv Shuffle_Org Site ID], Measure.[Inv Shuffle_Plan ID], Measure.[Inv Shuffle_Qty], Measure.[Inv Shuffle_Sales ID], Measure.[Inv Shuffle_To Site], Measure.[Inv Shuffle_USD Amount]}) on column;
   - df_out_IntrShuffle = Select ( &MPV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Intr Shuffle_BOD Name], Measure.[Intr Shuffle_Billing Doc], Measure.[Intr Shuffle_Billing Item], Measure.[Intr Shuffle_Contaner No], Measure.[Intr Shuffle_DC ETA], Measure.[Intr Shuffle_ETA Date], Measure.[Intr Shuffle_From Site ID], Measure.[Intr Shuffle_ITTS ATA], Measure.[Intr Shuffle_ITTS ETA], Measure.[Intr Shuffle_Invoice Item], Measure.[Intr Shuffle_Invoice No], Measure.[Intr Shuffle_MOD DC ETA], Measure.[Intr Shuffle_Order Line ID], Measure.[Intr Shuffle_Org Site ID], Measure.[Intr Shuffle_Plan ID], Measure.[Intr Shuffle_Po Item], Measure.[Intr Shuffle_Po No], Measure.[Intr Shuffle_Qty], Measure.[Intr Shuffle_Rank No], Measure.[Intr Shuffle_Sales ID]}) on column;
   - df_out_DemandW = Select (&MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Ship To] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[Dmd W_BAL], Measure.[Dmd W_Cust Rank], Measure.[Dmd W_Dmd Rank], Measure.[Dmd W_Global Prty], Measure.[Dmd W_ID], Measure.[Dmd W_Leadtime Due], Measure.[Dmd W_Local Prty], Measure.[Dmd W_Measure Rank], Measure.[Dmd W_No Plan], Measure.[Dmd W_Plan ID], Measure.[Dmd W_Preference], Measure.[Dmd W_Prod Rank], Measure.[Dmd W_Prty], Measure.[Dmd W_Prty Seq], Measure.[Dmd W_Qty], Measure.[Dmd W_Week Rank]}) on column;
   - df_out_SiteAP2Map = Select ( &MPV  * [Location].[Location] ) on row, ({Measure.[Site AP2 Map_GC], Measure.[Site AP2 Map_Ship To], Measure.[Site AP2 Map_Status], Measure.[Site AP2 Map_Valid Flag]}) on column;
   - df_out_MfgPlan = Select (&MPV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[Mfg Plan_BOM Version], Measure.[Mfg Plan_Finish Date], Measure.[Mfg Plan_Line Name], Measure.[Mfg Plan_Open Qty], Measure.[Mfg Plan_Order Line ID], Measure.[Mfg Plan_Plan ID], Measure.[Mfg Plan_Qty], Measure.[Mfg Plan_Rank No], Measure.[Mfg Plan_Status], Measure.[Mfg Plan_To Site ID]}) on column;
   - df_out_DistOrder = Select (&MPV * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Dist Order_From Site ID], Measure.[Dist Order_Order Line ID], Measure.[Dist Order_Plan ID], Measure.[Dist Order_SS Delivery Date], Measure.[Dist Order_SS Qty], Measure.[Dist Order_SS Startdate], Measure.[Dist Order_Sales ID], Measure.[Dist Order_To Site ID]}) on column;
   - df_out_VendorMtrl = Select (&MPV* [Location].[Location] * [Item Material].[Item Material] * [Vendor].[Vendor] * [Global Top].[GT Code] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Quota]}) on column;
   - df_out_MtrlInfoRecord = Select (&MPV* [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] * [Vendor].[Vendor] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Mtrl Info Record_Category], Measure.[Mtrl Info Record_Country], Measure.[Mtrl Info Record_Currency], Measure.[Mtrl Info Record_Description], Measure.[Mtrl Info Record_Exchange Rate], Measure.[Mtrl Info Record_Info Price USD], Measure.[Mtrl Info Record_Intransit LT], Measure.[Mtrl Info Record_Plan Del Time], Measure.[Mtrl Info Record_Price], Measure.[Mtrl Info Record_Price Unit], Measure.[Mtrl Info Record_Purchase Org], Measure.[Mtrl Info Record_Quota], Measure.[Mtrl Info Record_Ship Instructions], Measure.[Mtrl Info Record_Supplier LT], Measure.[Mtrl Info Record_Valid From], Measure.[Mtrl Info Record_Valid To], Measure.[Mtrl Info Record_Valuation Type], Measure.[Mtrl Info Record_Vendor Schema Grp]}) on column;
   - df_out_SalesItemAsn = Select (&MPV * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[Sales Item Asn_Valid Flag]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MNG_VersionCopy] for Measures {[Tact Time_Lock Flag]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView", "CWV_MP"})) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};



실행 전 프로시져를 통해 MF Site 삭제  필요

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
str_instance = 'PY_MNG_VersionCopy'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

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
    # # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_TactTime = read_csv_file('df_in_TactTime')
        df_in_Inventory = read_csv_file('df_in_Inventory')
        df_in_Intransit = read_csv_file('df_in_Intransit')
        df_in_InvShuffle = read_csv_file('df_in_InvShuffle')
        df_in_IntrShuffle = read_csv_file('df_in_IntrShuffle')
        df_in_DemandW =read_csv_file('df_in_DemandW')
        df_in_SiteAP2Map = read_csv_file('df_in_SiteAP2Map')
        # df_in_fullbom = read_csv_file('df_in_fullbom')
        df_in_MfgPlan = read_csv_file('df_in_MfgPlan')
        df_in_DistOrder = read_csv_file('df_in_DistOrder')
        df_in_VendorMtrl = read_csv_file('df_in_VendorMtrl')
        df_in_MtrlInfoRecord = read_csv_file('df_in_MtrlInfoRecord')
        df_in_SalesItemAsn = read_csv_file('df_in_SalesItemAsn')

    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    CWV = 'CurrentWorkingView'

    # if df_in_TactTime.empty:
    #     raise Exception("Exception: df_in_TactTime is empty")
    # if df_in_Inventory.empty:
    #     raise Exception("Exception: df_in_Inventory is empty")
    # if df_in_Intransit.empty:
    #     raise Exception("Exception: df_in_MF_Site is empty")
    # if df_in_InvShuffle.empty:
    #     raise Exception("Exception: df_in_InvShuffle is empty")
    # if df_in_IntrShuffle.empty:
    #     raise Exception("Exception: df_in_IntrShuffle is empty")
    # if df_in_DemandW.empty:
    #     raise Exception("Exception: df_in_DemandW is empty")
    # if df_in_SiteAP2Map.empty:
    #     raise Exception("Exception: df_in_SiteAP2Map is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    dfs = {'df_in_TactTime': df_in_TactTime, 'df_in_Inventory': df_in_Inventory, 'df_in_Intransit': df_in_Intransit,
           'df_in_InvShuffle': df_in_InvShuffle, 'df_in_IntrShuffle': df_in_IntrShuffle, 'df_in_DemandW': df_in_DemandW,
           'df_in_SiteAP2Map': df_in_SiteAP2Map, 'df_in_MfgPlan' : df_in_MfgPlan,'df_in_DistOrder':df_in_DistOrder,
           'df_in_VendorMtrl' : df_in_VendorMtrl,  'df_in_MtrlInfoRecord':df_in_MtrlInfoRecord,
           'df_in_SalesItemAsn' : df_in_SalesItemAsn}

    for name, df in dfs.items():
        print_df(df, name)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2 (1) 데이터 프레임 변수 지정 및 이름 변경
    ################################################################################################################

    step(200, '=====> STEP 2(Start) : input data machining')

    out_dfs = {}
    for name, df in dfs.items():
        df[df[VERSION_NAME_COLUMN]==CWV].copy()

        if name == 'df_in_TactTime':
            df = df.drop(columns=['Tact Time_Lock Flag'])

        df[VERSION_NAME_COLUMN] = paramOutVersion
        new_name = name.replace('in', 'out')
        out_dfs[new_name] = df

    for name, df in out_dfs.items():
        print_df(df, f'{name}')

    for name, df in out_dfs.items():
        row_count, col_count = df.shape
        note(f'=====> Final {name} rows : {row_count} , Columns : {col_count}')

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3 out 데이터 프레임 크기 확인 및 저장 (Live Server 특성상 반복문 사용 불가 - out Frame 설정 필요
    ###############################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    df_out_TactTime = out_dfs['df_out_TactTime'] if 'df_out_TactTime' in out_dfs else None
    df_out_Inventory = out_dfs['df_out_Inventory'] if 'df_out_Inventory' in out_dfs else None
    df_out_Intransit = out_dfs['df_out_Intransit'] if 'df_out_Intransit' in out_dfs else None
    df_out_InvShuffle = out_dfs['df_out_InvShuffle'] if 'df_out_InvShuffle' in out_dfs else None
    df_out_IntrShuffle = out_dfs['df_out_IntrShuffle'] if 'df_out_IntrShuffle' in out_dfs else None
    df_out_DemandW = out_dfs['df_out_DemandW'] if 'df_out_DemandW' in out_dfs else None
    df_out_SiteAP2Map = out_dfs['df_out_SiteAP2Map'] if 'df_out_SiteAP2Map' in out_dfs else None
    # df_out_fullbom = out_dfs['df_out_fullbom'] if 'df_out_fullbom' in out_dfs else None
    df_out_MfgPlan = out_dfs['df_out_MfgPlan'] if 'df_out_MfgPlan' in out_dfs else None
    df_out_DistOrder = out_dfs['df_out_DistOrder'] if 'df_out_DistOrder' in out_dfs else None
    df_out_VendorMtrl = out_dfs['df_out_VendorMtrl'] if 'df_out_VendorMtrl' in out_dfs else None
    df_out_MtrlInfoRecord = out_dfs['df_out_MtrlInfoRecord'] if 'df_out_MtrlInfoRecord' in out_dfs else None
    df_out_SalesItemAsn = out_dfs['df_out_SalesItemAsn'] if 'df_out_SalesItemAsn' in out_dfs else None

    if is_local:
        note(f'=====> Final output table create')
        for name, df in out_dfs.items():
            if df is not None:
                save_csv_file(df, name)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. 종료
    ################################################################################################################

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
