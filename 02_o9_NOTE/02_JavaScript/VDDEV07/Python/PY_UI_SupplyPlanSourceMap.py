"""

* 프로그램명
    - PY_UI_SupplyPlanSourceMap

* 내용
     - 자재별 공급 관리 형태를 고려한 공급계획 반영 설정 할 수 있는 UI
    - "Configuration (Material)" 화면에서 설정값을 반영할 수 있도록 Material Level5단위로 리스트를 구성해 주는 기능

* 변경이력
- 2024.08.05 / ybest7.park (박병훈) / Create

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_MtrlHrchyL5Name : Select ([Version].[Version Name].[CWV_MP] * [Rule].[Rule No] * [Hrcy Type].[Hrcy Type] ) on row , ({Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L2 Name],Measure.[Mtrl Hrchy_L3 Name],Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L5 Name]}) on column where {(Measure.[Mtrl Hrchy_SCM Material] == True), (Measure.[Mtrl Hrchy_Delete Flag] != "Y")};
                            (Select ([Version].[Version Name] * [Rule].[Rule No] * [Hrcy Type].[Hrcy Type] ) on row, ({Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L2 Name],Measure.[Mtrl Hrchy_L3 Name],Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L5 Name]}) on column where {(Measure.[Mtrl Hrchy_SCM Material] == True), (Measure.[Mtrl Hrchy_Delete Flag] != "Y")};)
   - df_in_SupplyPlanSourceMap : Select ([Version].[Version Name].[CWV_MP] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map_CMI Flag], Measure.[Supply Plan Source Map_Excel Flag], Measure.[Supply Plan Source Map_Global RTF Flag], Measure.[Supply Plan Source Map_Open PO Flag], Measure.[Supply Plan Source Map_RTF Flag], Measure.[Supply Plan Source Map_RTP Flag], Measure.[Supply Plan Source Map_Source], Measure.[Supply Plan Source Map_UI Alloc], Measure.[Supply Plan Source Map_Update Time], Measure.[Supply Plan Source Map_Updated By]}) on column;
                                (Select ([Version].[Version Name] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map_CMI Flag], Measure.[Supply Plan Source Map_Excel Flag], Measure.[Supply Plan Source Map_Global RTF Flag], Measure.[Supply Plan Source Map_Open PO Flag], Measure.[Supply Plan Source Map_RTF Flag], Measure.[Supply Plan Source Map_RTP Flag], Measure.[Supply Plan Source Map_Source], Measure.[Supply Plan Source Map_UI Alloc], Measure.[Supply Plan Source Map_Update Time], Measure.[Supply Plan Source Map_Updated By]}) on column;)

* Output Table
    - df_out_SupplyPlanSourceMap = Select ([Version].[Version Name].[CWV_MP] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map_CMI Flag], Measure.[Supply Plan Source Map_Excel Flag], Measure.[Supply Plan Source Map_Global RTF Flag], Measure.[Supply Plan Source Map_Open PO Flag], Measure.[Supply Plan Source Map_RTF Flag], Measure.[Supply Plan Source Map_RTP Flag], Measure.[Supply Plan Source Map_Source], Measure.[Supply Plan Source Map_UI Alloc], Measure.[Supply Plan Source Map_Update Time], Measure.[Supply Plan Source Map_Updated By]}) on column;
                                   (Select ([Version].[Version Name] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map_CMI Flag], Measure.[Supply Plan Source Map_Excel Flag], Measure.[Supply Plan Source Map_Global RTF Flag], Measure.[Supply Plan Source Map_Open PO Flag], Measure.[Supply Plan Source Map_RTF Flag], Measure.[Supply Plan Source Map_RTP Flag], Measure.[Supply Plan Source Map_Source], Measure.[Supply Plan Source Map_UI Alloc], Measure.[Supply Plan Source Map_Update Time], Measure.[Supply Plan Source Map_Updated By]}) on column;)

* 데이터 삭제
    DELETE DATA FOR MODEL [] where {Version.[Version Name].[CWV_MP]};


* 테스트 스크립트
    EXEC plugin instance [PY_UI_SupplyPlanSourceMap] for measures {[Supply Plan Source Map_Global RTF Flag]} using scope (Version.[Version Name].filter(#.Name in {"CWV_MP"})) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


* 데이터 수정


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
str_instance = 'PY_UI_SupplyPlanSourceMap'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",  low_memory=False)


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

        df_in_MtrlHrchyL5Name = read_csv_file("df_in_MtrlHrchyL5Name")
        df_in_SupplyPlanSourceMap = read_csv_file('df_in_SupplyPlanSourceMap')
        df_in_MSL5 = read_csv_file('df_in_MSL5')

    # if df_in_MtrlHrchyL5Name.empty:
    #     raise Exception("Exception: df_in_ItemSiteAsn is empty")
    #
    # if df_in_SupplyPlanSourceMap.empty:
    #     raise Exception("Exception: df_in_BOD is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_MtrlHrchyL5Name, 'df_in_MtrlHrchyL5Name')
    print_df(df_in_SupplyPlanSourceMap, 'df_in_SupplyPlanSourceMap')
    print_df(df_in_MSL5, 'df_in_MSL5')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    Item_Material_MSL5 = 'Item Material.[MSL5]'
    CMI_Flag = 'Supply Plan Source Map_CMI Flag'
    Excel_Flag = 'Supply Plan Source Map_Excel Flag'
    Global_RTF_Flag = 'Supply Plan Source Map_Global RTF Flag'
    Open_PO_Flag = 'Supply Plan Source Map_Open PO Flag'
    RTF_Flag = 'Supply Plan Source Map_RTF Flag'
    RTP_Flag = 'Supply Plan Source Map_RTP Flag'
    Source = 'Supply Plan Source Map_Source'
    UI_Alloc = 'Supply Plan Source Map_UI Alloc'
    Update_Time = 'Supply Plan Source Map_Update Time'
    Updated_By = 'Supply Plan Source Map_Updated By'

    Key_list = 'key_list'
    Mtrl_Hrchy_L1 = 'Mtrl Hrchy_L1 Name'
    Mtrl_Hrchy_L2 = 'Mtrl Hrchy_L2 Name'
    Mtrl_Hrchy_L3 = 'Mtrl Hrchy_L3 Name'
    Mtrl_Hrchy_L4 = 'Mtrl Hrchy_L4 Name'
    Mtrl_Hrchy_L5 = 'Mtrl Hrchy_L5 Name'

    # CWV = 'CurrentWorkingView'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3. (1) Version Name 이 CWV_MP인 데이터 기준 df_in_MtrlHrchyL5Name 의 Key_list 생성
    #         (2) df_in_SupplyPlanSourceMap의 CWV Version 기준  df_in_MtrlHrchyL5Name 의 unique 한 값 찾기
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    # df_in_MtrlHrchyL5Name = df_in_MtrlHrchyL5Name[
    #     df_in_MtrlHrchyL5Name[VERSION_NAME_COLUMN] == PARAM_OUTVERSION_VALUE]

    # df_in_MtrlHrchyL5Name.fillna("", inplace=True)

    df_in_MtrlHrchyL5Name[Mtrl_Hrchy_L4] = df_in_MtrlHrchyL5Name[Mtrl_Hrchy_L4].fillna(' ')
    df_in_MtrlHrchyL5Name[Mtrl_Hrchy_L5] = df_in_MtrlHrchyL5Name[Mtrl_Hrchy_L5].fillna(' ')

    df_in_MtrlHrchyL5Name[Key_list] = df_in_MtrlHrchyL5Name[Mtrl_Hrchy_L1] + "_" + df_in_MtrlHrchyL5Name[
        Mtrl_Hrchy_L2] + "_" + df_in_MtrlHrchyL5Name[Mtrl_Hrchy_L3] + "_" + df_in_MtrlHrchyL5Name[
                                          Mtrl_Hrchy_L4] + "_" + df_in_MtrlHrchyL5Name[Mtrl_Hrchy_L5]

    print_df(df_in_MtrlHrchyL5Name, 'df_in_MtrlHrchyL5Name')
    #
    # df_in_SupplyPlanSourceMap = df_in_SupplyPlanSourceMap[df_in_SupplyPlanSourceMap[VERSION_NAME_COLUMN]==CWV]

    row_count, col_count = df_in_SupplyPlanSourceMap.shape
    note(f'=====> df_in_SupplyPlanSourceMap rows : {row_count} , Columns : {col_count}')

    unique_list = [x for x in df_in_MtrlHrchyL5Name[Key_list].unique() if
                   x not in df_in_SupplyPlanSourceMap[Item_Material_MSL5].unique()]

    # Key_list_unique = df_in_MtrlHrchyL5Name[Key_list].unique()
    # MSL5_unique = df_in_SupplyPlanSourceMap[Item_Material_MSL5].unique()
    #
    # unique_list =[]
    #
    # if MSL5_unique.size == 0:
    #     unique_list = list(Key_list_unique)
    # else:
    #     for x in Key_list_unique:
    #         if x not in MSL5_unique:
    #             unique_list.append(x)


    print_df(unique_list, 'unique_list')
    df_in_MSL5 = df_in_MSL5[df_in_MSL5[Item_Material_MSL5].isin(unique_list)]

    print_df(df_in_MSL5, 'df_in_MSL5')

    # print_df(df_in_MtrlHrchyL5Name, 'df_in_MtrlHrchyL5Name')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. Unique 한 Date Frame 생성
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # 신규 프레임 생성
    df_unique = df_in_MSL5.copy()
    # df_unique[Item_Material_MSL5] = unique_list
    df_unique[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE
    df_unique[CMI_Flag] = False
    df_unique[Source] = ''
    df_unique[Open_PO_Flag] = False
    df_unique[RTF_Flag] = False
    df_unique[Global_RTF_Flag] = False
    df_unique[RTP_Flag] = False
    df_unique[Excel_Flag] = False
    df_unique[UI_Alloc] = False
    df_unique[Updated_By] = 'System'
    df_unique[Update_Time] = datetime.datetime.today()
    # df_unique[Update_Time] = pd.to_datetime(df_unique[Update_Time], format='%Y-%m-%d')
    # df_unique[Update_Time] = df_unique[Update_Time].astype(str)
    # df_unique[Update_Time] = df_unique[Update_Time].str.split(" ", expand=True).iloc[:, 0].astype(str)
    df_unique = df_unique[[VERSION_NAME_COLUMN, Item_Material_MSL5,CMI_Flag, Excel_Flag, Global_RTF_Flag,
                           Open_PO_Flag,RTF_Flag, RTP_Flag, Source, UI_Alloc, Update_Time, Updated_By]]
    df_unique.dropna(axis=0, inplace=True)

    print_df(df_unique, 'df_unique')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) df_out_SupplyPlanSourceMap   & df_unique  concat
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    df_in_SupplyPlanSourceMap[VERSION_NAME_COLUMN] = PARAM_OUTVERSION_VALUE
    dfs = [df_unique, df_in_SupplyPlanSourceMap]
    dfs = [df for df in dfs if not df.empty]
    df_out_SupplyPlanSourceMap = pd.concat(dfs, axis=0)

    df_out_SupplyPlanSourceMap.reset_index(drop=True, inplace=True)

    print_df(df_out_SupplyPlanSourceMap, 'df_out_SupplyPlanSourceMap')
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 6. (1) 최종 Out_Put Save
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    row_count, col_count = df_out_SupplyPlanSourceMap.shape
    note(f'=====> Final df_out_SupplyPlanSourceMap rows : {row_count} , Columns : {col_count}')
    print_df(df_out_SupplyPlanSourceMap, 'df_out_SupplyPlanSourceMap')

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_SupplyPlanSourceMap, 'df_out_SupplyPlanSourceMap')

    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

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
    step(700, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()