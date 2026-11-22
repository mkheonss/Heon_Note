

"""

* 프로그램명
    - PY_MNG_MtrlSiteAsn

* 수정일 : 20204-12-03

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.11.18 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_ItemSiteAsn_Site = Select ( &MPV * &SPLocation * [Item].[Item] ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column ;
   - df_in_ItemSiteAsn_Item = Select ( &MPV * [Location].[Location] * &RawMtrl ) on row,({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column;


* Output Table
    - df_out_ItemSiteAsn =  Select (&MPV  * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Item Mtrl Site Asn_Cur Status], Measure.[Item Mtrl Site Asn_Engine Flag]}) on column;


* 테스트 스크립트
    EXEC plugin instance [PY_MNG_MtrlSiteAsn] for Measures {[Item Mtrl Site Asn_Cur Status]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView", "CWV_MP"})) using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion ,"CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};



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
str_instance = 'PY_MNG_MtrlSiteAsn'
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

        df_in_ItemSiteAsn_Site = read_csv_file('df_in_ItemSiteAsn_Site')
        df_in_ItemSiteAsn_Item = read_csv_file('df_in_ItemSiteAsn_Item')


    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    CWV = 'CurrentWorkingView'


    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ItemSiteAsn_Site, 'df_in_ItemSiteAsn_Site')
    print_df(df_in_ItemSiteAsn_Item, 'df_in_ItemSiteAsn_Item')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2 (1) 데이터 프레임 변수 지정 및 이름 변경
    ################################################################################################################

    step(200, '=====> STEP 2(Start) : input data machining')

    Version_COLUMN = 'Version.[Version Name]'
    Location_COLUMN = 'Location.[Location]'
    Item_COLUMN = 'Item.[Item]'
    ItemMaterial_COILUM = 'Item Material.[Item Material]'

    Item_Site_Asn_Cur_Status = 'Item Site Asn_Cur Status'
    Item_Site_Asn_Engine_Flag = 'Item Site Asn_Engine Flag'
    Item_Site_Asn_Item_Grp = 'Item Site Asn_Item Grp'
    Item_Site_Asn_Sales_Prod_Asn = 'Item Site Asn_Sales Prod Asn'
    Item_Site_Asn_Stage = 'Item Site Asn_Stage'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3 out 데이터 프레임 크기 확인 및 저장 (Live Server 특성상 반복문 사용 불가 - out Frame 설정 필요
    ###############################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    df_out_ItemSiteAsn = pd.concat([df_in_ItemSiteAsn_Site, df_in_ItemSiteAsn_Item], axis=0)
    # df_out_ItemSiteAsn = df_out_ItemSiteAsn.rename(columns={Item_COLUMN : ItemMaterial_COILUM})
    df_out_ItemSiteAsn = df_out_ItemSiteAsn[[Version_COLUMN, Location_COLUMN, Item_COLUMN,
                                             Item_Site_Asn_Cur_Status, Item_Site_Asn_Engine_Flag ]]

    print_df(df_out_ItemSiteAsn, 'df_out_ItemSiteAsn')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. 종료
    ################################################################################################################
    step(400, '=====> STEP 5(Start) : output data machining')
    print_df(df_out_ItemSiteAsn, 'df_out_MultiSite')

    row_count, col_count = df_out_ItemSiteAsn.shape
    note(f'=====> Final df_out_MultiSite rows : {row_count} , Columns : {col_count}')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_ItemSiteAsn, 'df_out_MultiSite')

    step(400, '=====> STEP 5(End) : Check memory usage & runtime')

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
    step(500, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()
