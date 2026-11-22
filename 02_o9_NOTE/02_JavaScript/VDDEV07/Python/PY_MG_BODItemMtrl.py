

"""

* 프로그램명
    - PY_MG_BODItemMtrl

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.09.27 / ybest7.park (박병훈) / Create

* 내용
  - 자재 BOD 집계 ( UI에서는 MSL3 레벨에서 Header관리 / 예외 사항만 Detail 레벨로 관리 )
  - 자재 BOD Header 기준  멤버 생성용 메저 입력


* Input Table
     - df_in_ItemMtrl : Select ( [Item Material].[MSL3] * [Item Material].[Item Material] ) ;
     - df_in_MtrlAttb :  Select ([Version].[Version Name] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Attr_Pallet], Measure.[Dummy]}) on column where{~isnull(Measure.[Mtrl Attr_Pallet])};
     - df_in_BODListMtrl : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,({Measure.[BOD List Mtrl_EFF Enddate], Measure.[BOD List Mtrl_EFF Startdate],Measure.[Dummy]}) on column.filter((isnull(Measure.[BOD List Mtrl_EFF Enddate])||Measure.[BOD List Mtrl_EFF Enddate]> Measure.[W Plan Start Date]) &&(isnull(Measure.[BOD List Mtrl_EFF Startdate])||Measure.[BOD List Mtrl_EFF Startdate]< Measure.[W Plan End Date])) ;
     - df_in_BODItemMtrl : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lot Size],Measure.[Dummy]}) on column.filter((isnull(Measure.[BOD Item Mtrl_EFF Enddate])||Measure.[BOD Item Mtrl_EFF Enddate]> Measure.[W Plan Start Date]) &&(isnull(Measure.[BOD Item Mtrl_EFF Startdate])||Measure.[BOD Item Mtrl_EFF Startdate]< Measure.[W Plan End Date])) ;

* 데이터 삭제
     DELETE DATA FOR MODEL [BOD Item Mtrl Full] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_MtrlFull = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_Lot Size], Measure.[BOD Item Mtrl Full_MSL3]}) on column;
    - df_out_BODMtrl = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[MP Batch_BODMtrl Bulk Member Creation_BOD Name], Measure.[MP Batch_BODMtrl Bulk Member Creation_From Site ID], Measure.[MP Batch_BODMtrl Bulk Member Creation_To Site ID]}) on column;

* 테스트를 위한 데이터 삭제

* 테스트 스크립트
    EXEC plugin instance [PY_MG_BODItemMtrl] for measures {[BOD Item Mtrl Full_EFF Startdate]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(paramOutVersion , "CWV_MP"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;

"""


########################################################################################################################
# common - start
########################################################################################################################
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
str_instance = 'PY_MG_BODItemMtrl'
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

        df_in_ItemMtrl = read_csv_file('df_in_ItemMtrl')
        df_in_MtrlAttb = read_csv_file('df_in_MtrlAttb')
        df_in_BODListMtrl = read_csv_file('df_in_BODListMtrl')
        df_in_BODItemMtrl = read_csv_file('df_in_BODItemMtrl')


    # if df_in_ItemMtrl.empty:
    #     raise Exception("Exception: df_in_ItemMtrl is empty")
    #
    # # if df_in_MtrlAttb.empty:
    # #     raise Exception("Exception: df_in_MtrlAttb is empty")
    #
    # if df_in_BODListMtrl.empty:
    #     raise Exception("Exception: df_in_BODListMtrl is empty")
    #
    # if df_in_BODItemMtrl.empty:
    #     raise Exception("Exception: df_in_BODItemMtrl is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ItemMtrl, 'df_in_ItemMtrl',True)
    print_df(df_in_MtrlAttb, 'df_in_MtrlAttb',True)
    print_df(df_in_BODListMtrl, 'df_in_BODListMtrl',True)
    print_df(df_in_BODItemMtrl, 'df_in_BODItemMtrl',True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    LOCATION_COLUMN = 'Location.[Location]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
    ITEM_MATERIAL_COLUMN = 'Item Material.[Item Material]'
    ITEM_MATERIAL_MSL3_COLUMN = 'Item Material.[MSL3]'
    ITEM_MATERIAL_COLUMN_C = 'Item Material.[Item Material]_C'

    BOD_List_Mtrl_EFF_Startdate = 'BOD List Mtrl_EFF Startdate'
    BOD_List_Mtrl_EFF_Enddate = 'BOD List Mtrl_EFF Enddate'
    BOD_Item_Mtrl_EFF_Startdate = 'BOD Item Mtrl_EFF Startdate'
    BOD_Item_Mtrl_EFF_Enddate = 'BOD Item Mtrl_EFF Enddate'
    BOD_Item_Mtrl_Lot_Size = 'BOD Item Mtrl_Lot Size'
    BOD_Item_Mtrl_Full_EFF_Startdate = 'BOD Item Mtrl Full_EFF Startdate'
    BOD_Item_Mtrl_Full_EFF_Enddate = 'BOD Item Mtrl Full_EFF Enddate'
    BOD_Item_Mtrl_Full_Flag = 'BOD Item Mtrl Full_Flag'
    BOD_Item_Mtrl_Full_Lot_Size = 'BOD Item Mtrl Full_Lot Size'
    BOD_Item_Mtrl_Full_MSL3 = 'BOD Item Mtrl Full_MSL3'
    Mtrl_Attr_Pallet = 'Mtrl Attr_Pallet'

    MP_Batch_BODMtrl_Bulk_Member_Creation_BOD_Name = 'MP Batch_BODMtrl Bulk Member Creation_BOD Name'
    MP_Batch_BODMtrl_Bulk_Member_Creation_From_Site_ID = 'MP Batch_BODMtrl Bulk Member Creation_From Site ID'
    MP_Batch_BODMtrl_Bulk_Member_Creation_To_Site_ID = 'MP Batch_BODMtrl Bulk Member Creation_To Site ID'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) Item Material.[Item Material] 기준으로 df_in_ItemMtrl 과 df_in_BODItemMtrl & df_in_MtrlAttb merge
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')
    # df_in_BODListMtrl 과 df_in_ItemMtrl 을 MSL3 기준으로 merge
    df_in_BODListMtrl_temp = df_in_BODListMtrl.merge(
        df_in_ItemMtrl,
        on=ITEM_MATERIAL_MSL3_COLUMN,
        how='inner').drop(["Dummy"], axis=1)

    print_df(df_in_BODListMtrl_temp, 'df_in_BODListMtrl_temp', True)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. (1) 'Version.[Version Name]', 'Location.[Location]', 'Sub Location.[Sub Location]',
    #             'Trans Mode.[Trans Mode]' 기준 Merge
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # df_in_BODItemMtrl의 Item material 의 unique 한 값 리스트로 생성
    item_material_list = df_in_ItemMtrl[ITEM_MATERIAL_COLUMN].unique()
    # df_in_ItemMtrl Item material 중 df_in_BODItemMtrl 에 있는 것들만 추출
    df_in_BODItemMtrl = df_in_BODItemMtrl[df_in_BODItemMtrl[ITEM_MATERIAL_COLUMN].isin(item_material_list)]
    # df_in_ItemMtrl Item material 중 df_in_BODItemMtrl 에 있는 것들만 추출
    df_in_MtrlAttb = df_in_MtrlAttb[df_in_MtrlAttb[ITEM_MATERIAL_COLUMN].isin(item_material_list)]

    # df_in_BODListMtrl_temp & df_in_BODItemMtrl merge (key = Location, SubLocation,TransMode)
    df_in_BODListMtrl_temp = df_in_BODListMtrl_temp.merge(
        df_in_BODItemMtrl,
        on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
        how='left').drop("Dummy", axis=1)

    # 컬럼명 변경
    df_in_BODListMtrl_temp.rename(
        columns={
            'Item Material.[Item Material]_x': ITEM_MATERIAL_COLUMN,
            'Item Material.[Item Material]_y': ITEM_MATERIAL_COLUMN_C},
        inplace=True)

    df_in_BODListMtrl_temp = df_in_BODListMtrl_temp.merge(
        df_in_MtrlAttb,
        on=[VERSION_NAME_COLUMN, ITEM_MATERIAL_COLUMN],
        how='left')

    print_df(df_in_BODListMtrl_temp, 'df_in_BODListMtrl_temp',True)
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) df_out_MtrlFull 생성
    #         (2) df_in_BODListMtrl 기준 df_mergeA 와 merge
    #         (3) df_out_MtrlFull Columns 설정
    #         (4) df_out_MtrlFull 순서 설정
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    df_out_MtrlFull = df_in_BODListMtrl_temp.copy()
    df_out_MtrlFull[BOD_Item_Mtrl_Full_EFF_Startdate] = np.where(df_out_MtrlFull[ITEM_MATERIAL_COLUMN_C].isna(),
                                                                 df_out_MtrlFull[BOD_List_Mtrl_EFF_Startdate],
                                                                 df_out_MtrlFull[BOD_Item_Mtrl_EFF_Startdate])
    df_out_MtrlFull[BOD_Item_Mtrl_Full_EFF_Enddate] = np.where(df_out_MtrlFull[ITEM_MATERIAL_COLUMN_C].isna(),
                                                               df_out_MtrlFull[BOD_List_Mtrl_EFF_Enddate],
                                                               df_out_MtrlFull[BOD_Item_Mtrl_EFF_Enddate])
    df_out_MtrlFull[BOD_Item_Mtrl_Full_Flag] = np.where(df_out_MtrlFull[ITEM_MATERIAL_COLUMN_C].isna(), 'Header',
                                                        'Detail')
    df_out_MtrlFull[BOD_Item_Mtrl_Full_Lot_Size] = np.where(df_out_MtrlFull[ITEM_MATERIAL_COLUMN_C].isna(),
                                                            df_out_MtrlFull[Mtrl_Attr_Pallet],
                                                            df_out_MtrlFull[BOD_Item_Mtrl_Lot_Size])
    df_out_MtrlFull[BOD_Item_Mtrl_Full_MSL3] = df_out_MtrlFull[ITEM_MATERIAL_MSL3_COLUMN]

    df_out_MtrlFull = df_out_MtrlFull[
        [VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_MATERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
         BOD_Item_Mtrl_Full_EFF_Enddate, BOD_Item_Mtrl_Full_EFF_Startdate, BOD_Item_Mtrl_Full_Flag,
         BOD_Item_Mtrl_Full_Lot_Size, BOD_Item_Mtrl_Full_MSL3]]

    delete_dfs(df_in_BODListMtrl_temp)
    print_df(df_out_MtrlFull, 'df_out_MtrlFull', True)
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 6. (1) df_out_BODMtrl 생성
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    df_out_BODMtrl = df_out_MtrlFull.copy()
    df_out_BODMtrl[MP_Batch_BODMtrl_Bulk_Member_Creation_BOD_Name] = df_out_BODMtrl[LOCATION_COLUMN] + '_' + \
                                                                     df_out_BODMtrl[SUB_LOCATION_COLUMN] + '_' + \
                                                                     df_out_BODMtrl[TRANS_MODE_COLUMN]
    df_out_BODMtrl[MP_Batch_BODMtrl_Bulk_Member_Creation_From_Site_ID] = ''
    df_out_BODMtrl[MP_Batch_BODMtrl_Bulk_Member_Creation_To_Site_ID] =''

    df_out_BODMtrl = df_out_BODMtrl[[VERSION_NAME_COLUMN,LOCATION_COLUMN,SUB_LOCATION_COLUMN,TRANS_MODE_COLUMN,
                                     MP_Batch_BODMtrl_Bulk_Member_Creation_BOD_Name,
                                     MP_Batch_BODMtrl_Bulk_Member_Creation_From_Site_ID,
                                     MP_Batch_BODMtrl_Bulk_Member_Creation_To_Site_ID]]

    print_df(df_out_BODMtrl, 'df_out_BODMtrl', True)
    step(600, '=====> STEP 6(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 5. (1) 최종 Out_Put Save
    ################################################################################################################
    step(700, '=====> STEP 7(Start) : output data machining')

    row_count, col_count = df_out_MtrlFull.shape
    note(f'=====> Final df_out_MtrlFull rows : {row_count} , Columns : {col_count}')
    print_df(df_out_MtrlFull, 'df_out_MtrlFull',True)

    row_count, col_count = df_out_BODMtrl.shape
    note(f'=====> Final df_out_BODMtrl rows : {row_count} , Columns : {col_count}')
    print_df(df_out_BODMtrl, 'df_out_BODMtrl',True)


    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_MtrlFull, 'df_out_MtrlFull')
        save_csv_file(df_out_BODMtrl, 'df_out_BODMtrl')

    step(700, '=====> STEP 7(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_MtrlFull = pd.DataFrame([], columns=[])
    df_out_BODMtrl = pd.DataFrame([], columns=[])


else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(700, '===================== plugin Execution End =====================')

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