

"""

* 프로그램명
    - PY_MG_InventoryInputs

* 수정일 : 2024/11/15

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.10.07 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
     - df_in_SS = Select ( &MPV * [Item].[Item] * [Location].[Location] ) on row, ({ Measure.[SS_SS Type]}) on column.filter(Measure.[SS_Valid Flag] ==  "Y"  )  ;
     - df_in_ItemSiteAsn = Select ( &MPV  * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag],  Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true) ;
     - df_in_SSW = Select (&MPV * [Item].[Item] * &AllPlanningWeeks * [Location].[Location] * [Sales Domain].[AP2] ) on row,({Measure.[SS W_SS Target]}) on column ;
     - df_in_ItemMtrl = Select ([Item Material].[MSL3] * [Item Material].[MSL4] *  [Item Material].[MSL5] * [Item Material].[Item Material] );
     - df_in_Mtrl_L3W = Select (&MPV * &PlanningHorizon * [Location].[Location] * [Item Material].[MSL3] ) on row, ({Measure.[SS Mtrl L3 W_Time]}) on column;
     - df_in_Mtrl_L4W = Select (&MPV * &PlanningHorizon * [Location].[Location] * [Item Material].[MSL4] ) on row, ({Measure.[SS Mtrl L4 W_Time]}) on column;
     - df_in_Mtrl_L5W = Select (&MPV * &PlanningHorizon * [Location].[Location] * [Item Material].[MSL5] ) on row, ({Measure.[SS Mtrl L5 W_Time]}) on column;
     - df_in_Mtrl_ItemW = Select (&MPV * &PlanningHorizon * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[SS Mtrl Item W_Time]}) on column;


* 데이터 삭제
     DELETE DATA FOR MODEL [001.019W Solver Inputs Inventory Inputs] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_InventoryInputs =  Select (&MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] ) on row, ({Measure.[W Quantity Max Target], Measure.[W Target Inventory], Measure.[W WOS Max Target], Measure.[W WOS Target]}) on column ;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_InventoryInputs] for Measures {[W WOS Target]} using scope ( &MPV *  &AllPlanningWeeks ) using arguments {(param_outVersion , "CWV_MP"), (ExecutionMode, "MediumWeight"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ),([Param.o9_sys_log_level], "DEBUG")} ;

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
str_instance = 'PY_MG_InventoryInputs'
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

        df_in_SS = read_csv_file('df_in_SS')
        df_in_SSW = read_csv_file('df_in_SSW')
        df_in_ItemSiteAsn = read_csv_file('df_in_ItemSiteAsn')
        df_in_ItemMtrl = read_csv_file('df_in_ItemMtrl')
        df_in_Mtrl_L3W = read_csv_file('df_in_Mtrl_L3W')
        df_in_Mtrl_L4W = read_csv_file('df_in_Mtrl_L4W')
        df_in_Mtrl_L5W = read_csv_file('df_in_Mtrl_L5W')
        df_in_Mtrl_ItemW = read_csv_file('df_in_Mtrl_ItemW')

    #
    # if df_in_SS.empty:
    #     raise Exception("Exception: df_in_SS is empty")
    #
    # if df_in_SSW.empty:
    #     raise Exception("Exception: df_in_SSW is empty")
    #
    # if df_in_ItemSiteAsn.empty:
    #     raise Exception("Exception: df_in_ItemSiteAsn is empty")
    #
    # if df_in_ItemMtrl.empty:
    #     raise Exception("Exception: df_in_ItemMtrl is empty")
    #
    # if df_in_Mtrl_L3W.empty:
    #     raise Exception("Exception: df_in_Mtrl_L3W is empty")
    #
    # if df_in_Mtrl_L4W.empty:
    #     raise Exception("Exception: df_in_Mtrl_L4W is empty")
    #
    # if df_in_Mtrl_L5W.empty:
    #     raise Exception("Exception: df_in_Mtrl_L5W is empty")
    #
    # if df_in_Mtrl_ItemW.empty:
    #     raise Exception("Exception: df_in_Mtrl_ItemW is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_SS, 'df_in_SS')
    print_df(df_in_SSW, 'df_in_SSW')
    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn')
    print_df(df_in_ItemMtrl, 'df_in_ItemMtrl')
    print_df(df_in_Mtrl_L3W, 'df_in_Mtrl_L3W')
    print_df(df_in_Mtrl_L4W, 'df_in_Mtrl_L4W')
    print_df(df_in_Mtrl_L5W, 'df_in_Mtrl_L5W')
    print_df(df_in_Mtrl_ItemW, 'df_in_Mtrl_ItemW')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Item_COLUMN = 'Item.[Item]'
    Location_COLUMN = 'Location.[Location]'
    TimeWeek_COLUMN = 'Time.[Week]'
    Item_Material_ML3_COLUMN = 'Item Material.[MSL3]'
    Item_Material_ML4_COLUMN = 'Item Material.[MSL4]'
    Item_Material_ML5_COLUMN = 'Item Material.[MSL5]'
    ItemMaterial_COILUM = 'Item Material.[Item Material]'
    Sales_Domain_AP_COLUMN = 'Sales Domain.[AP2]'

    SS_SS_Type = 'SS_SS Type'
    SS_W_SS_Target = 'SS W_SS Target'
    MIN_TIME = 'MIN_TIME'
    MIN_ONHAND = 'MIN_ONHAND'

    W_Target_Inventory = 'W Target Inventory'
    W_Quantity_Max_Target = 'W Quantity Max Target'
    W_WOS_Max_Target = 'W WOS Max Target'
    W_WOS_Target = 'W WOS Target'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3 (1) unique한 Location & Item 추출
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    Location_unique_series = df_in_ItemSiteAsn[Location_COLUMN].unique()
    Item_unique_series = df_in_ItemSiteAsn[Item_COLUMN].unique()
    df_in_SS = df_in_SS[
        (df_in_SS[Location_COLUMN].isin(Location_unique_series) & (df_in_SS[Item_COLUMN].isin(Item_unique_series)))]

    print_df(df_in_SS, 'df_in_SS')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. 안전 재고 일수 정보 Insert
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : input data machining')

    df_in_SS_TempA = df_in_SS[df_in_SS[SS_SS_Type] == MIN_TIME]
    df_in_SS_TempA = df_in_SS_TempA.merge(df_in_SSW, on=[Version_COLUMN, Item_COLUMN, Location_COLUMN], how='inner')
    df_in_SS_TempA = df_in_SS_TempA.groupby([Version_COLUMN, Location_COLUMN, Item_COLUMN, TimeWeek_COLUMN])[
        SS_W_SS_Target].min().reset_index()
    df_in_SS_TempA[W_Quantity_Max_Target] = ''
    df_in_SS_TempA[W_Target_Inventory] = ''
    df_in_SS_TempA[W_WOS_Max_Target] = ''

    df_in_SS_TempA = df_in_SS_TempA[
        [Version_COLUMN, Item_COLUMN, TimeWeek_COLUMN,Location_COLUMN,SS_W_SS_Target]]

    print_df(df_in_SS_TempA, 'df_in_SS_TempA')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5.안전 재고 수량 정보 Insert
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : input data machining')

    df_in_SS_TempB = df_in_SS[df_in_SS[SS_SS_Type] == MIN_ONHAND]
    df_in_SS_TempB = df_in_SS_TempB.merge(df_in_SSW, on=[Version_COLUMN, Item_COLUMN, Location_COLUMN], how='inner')
    df_in_SS_TempB = df_in_SS_TempB.groupby([Version_COLUMN, Location_COLUMN, Item_COLUMN, TimeWeek_COLUMN])[
        SS_W_SS_Target].min().reset_index()
    df_in_SS_TempB[W_Target_Inventory] = df_in_SS_TempB[SS_W_SS_Target]
    df_in_SS_TempB[W_Quantity_Max_Target] = ''
    df_in_SS_TempB[W_WOS_Target] = ''
    df_in_SS_TempB[W_WOS_Max_Target] = ''
    df_in_SS_TempB = df_in_SS_TempB[
        [Version_COLUMN, Item_COLUMN, TimeWeek_COLUMN, Location_COLUMN, W_Quantity_Max_Target, W_Target_Inventory,
         W_WOS_Max_Target, W_WOS_Target]]

    print_df(df_in_SS_TempB, 'df_in_SS_TempB')
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. 최종 Output 설정
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : input data machining')

    df_in_ItemMtrl_Item = df_in_ItemMtrl[df_in_ItemMtrl[ItemMaterial_COILUM].isin(Item_unique_series)]

    df_in_L3_Location = df_in_Mtrl_L3W[df_in_Mtrl_L3W[Location_COLUMN].isin(Location_unique_series)]
    df_in_L3 = df_in_L3_Location.merge(df_in_ItemMtrl_Item, on=Item_Material_ML3_COLUMN, how="inner")
    df_in_L3 = df_in_L3[[ItemMaterial_COILUM, Location_COLUMN, TimeWeek_COLUMN, 'SS Mtrl L3 W_Time']]

    df_in_L4_Location = df_in_Mtrl_L4W[df_in_Mtrl_L4W[Location_COLUMN].isin(Location_unique_series)]
    df_in_L4 = df_in_L4_Location.merge(df_in_ItemMtrl_Item, on=Item_Material_ML4_COLUMN, how="inner")
    df_in_L4 = df_in_L4[[ItemMaterial_COILUM, Location_COLUMN, TimeWeek_COLUMN, 'SS Mtrl L4 W_Time']]

    df_in_L5_Location = df_in_Mtrl_L5W[df_in_Mtrl_L5W[Location_COLUMN].isin(Location_unique_series)]
    df_in_L5 = df_in_L5_Location.merge(df_in_ItemMtrl_Item, on=Item_Material_ML5_COLUMN, how="inner")
    df_in_L5 = df_in_L5[[ItemMaterial_COILUM, Location_COLUMN, TimeWeek_COLUMN, 'SS Mtrl L5 W_Time']]

    del (df_in_L3_Location, df_in_L4_Location, df_in_L5_Location)

    print_df(df_in_L3, 'df_in_L3')
    print_df(df_in_L4, 'df_in_L4')
    print_df(df_in_L5, 'df_in_L5')

    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 7. (1) 최종 Out_Put Save
    ################################################################################################################
    step(700, '=====> STEP 7(Start) : input data machining')

    merge_col = [ItemMaterial_COILUM, Location_COLUMN, TimeWeek_COLUMN]
    df_in_L3 = df_in_L3.merge(df_in_Mtrl_ItemW, on=merge_col, how="inner")
    df_in_L3 = df_in_L3.merge(df_in_L5, on=merge_col, how="inner")
    df_in_L3 = df_in_L3.merge(df_in_L4, on=merge_col, how="inner")

    conditions = [
        ~df_in_L3['SS Mtrl Item W_Time'].isnull(),
        ~df_in_L3['SS Mtrl L5 W_Time'].isnull(),
        ~df_in_L3['SS Mtrl L4 W_Time'].isnull()
    ]

    choices = [
        df_in_L3['SS Mtrl Item W_Time'],
        df_in_L3['SS Mtrl L5 W_Time'],
        df_in_L3['SS Mtrl L4 W_Time']
    ]

    df_in_L3[W_WOS_Target] = np.select(conditions, choices, default=df_in_L3['SS Mtrl L3 W_Time'])

    df_in_L3[W_WOS_Max_Target] = ''
    df_in_L3[W_Target_Inventory] = ''
    df_in_L3[W_Quantity_Max_Target] = ''
    df_in_L3 = df_in_L3.rename(columns={ItemMaterial_COILUM: Item_COLUMN})

    df_in_L3 = df_in_L3[
        [Version_COLUMN, Item_COLUMN, TimeWeek_COLUMN, Location_COLUMN, W_Quantity_Max_Target, W_Target_Inventory,
         W_WOS_Max_Target, W_WOS_Target]]

    print_df(df_in_L3, 'df_in_L3')

    step(700, '=====> STEP 7(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 8. (1) 최종 Out_Put Save
    ################################################################################################################
    step(800, '=====> STEP 8(Start) : input data machining')

    print_df(df_in_SS_TempA, 'df_in_SS_TempA')
    print_df(df_in_SS_TempB, 'df_in_SS_TempB')
    print_df(df_in_L3, 'df_in_L3')
    df_out_InventoryInputs = pd.concat([df_in_SS_TempA, df_in_SS_TempB, df_in_L3], axis=0)

    df_out_InventoryInputs[Version_COLUMN] = PARAM_OUTVERSION_VALUE
    df_out_InventoryInputs = df_out_InventoryInputs[[Version_COLUMN,Item_COLUMN,TimeWeek_COLUMN,Location_COLUMN,
                                                     W_Quantity_Max_Target,W_Target_Inventory,W_WOS_Max_Target,
                                                     W_WOS_Target]]

    print_df(df_out_InventoryInputs, 'df_out_InventoryInputs')

    row_count, col_count = df_out_InventoryInputs.shape
    note(f'=====> Final df_out_InventoryInputs rows : {row_count} , Columns : {col_count}')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_InventoryInputs, 'df_out_InventoryInputs')

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
    step(900, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()



