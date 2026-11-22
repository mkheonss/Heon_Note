

"""

* 프로그램명
    - PY_UI_MultiSitebyItem

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.02.03 / ybest7.park (박병훈) / Create
- 2025.04.25 / ybest7.park (박병훈) / 수정
- 2025-06.12 / ybest7.park (박병훈) / 데이터 삭제 스크립트 수정
- 2025-06-17 / ybest7.park (박병훈) / df_in_MutiSite input data 추가
- 2025-11-13 /  ybest7.park (박병훈) / ddf_in_Location input data 추가 Logic 추가
- 2025-11-20 / ybest7.park (박병훈)  / df_in_SiteAP2Map & df_in_Location input data 합치면서 로직 삭제
- 2025-11-26 / ybest7.park (박병훈) / df_in_BODStructure & df_in_SiteAP2Map input Query 삭제 및 Input Data Query 변경
- 2026-02-11 /  ybest7.park (박병훈) / merge 조건 및 컬럼명 변경 내용 수정 

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_MultiSite = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Product] * [Sales Domain].[AP2] * [To Location].[To Location] * [Category].[Category].filter(#.Name in {"SOPDCDEF", "SELLERMAP","MULTILEVEL"}) * [Sub Location].[Sub Location] ) on row, ({Measure.[Multi Site_AP2 Name], Measure.[Multi Site_BOD Valid Flag], Measure.[Dummy]}) on column ;
   - df_in_BODItem = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Product] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD Valid], Measure.[Dummy]}) on column where {(Measure.[BOD Item_BOD Valid]) == "Y"};
   - df_In_MultiSitebyItem = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] ) on row, ({Measure.[Multi Site by Item_Updated By], Measure.[Dummy]}) on column;
   - df_in_APName = select ([Sales Domain].[AP2]) on row, () on column include memberproperties {[Sales Domain].[AP2], [DisplayName]} ;


   # - df_in_SiteAP2Map = Select ([Version].[Version Name] * [Location].[Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC","DC_HUB_MC_AP2"}).relatedmembers([Location])) on row, ({Measure.[Site AP2 Map_Ship To], Measure.[Site AP2 Map_Valid Flag] , Measure.[Dummy]}) on column where {(Measure.[Site AP2 Map_Valid Flag] == "Y"),(~IsNull(Measure.[Site AP2 Map_Ship To]))};
   # - df_in_BODStructure = Select ([Version].[Version Name] * [Item].[Item] * [Item].[Product Group] * [Item].[Product] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[BOD Structure_DC Site], Measure.[BOD Structure_Hub Site], Measure.[Dummy]}) on column  where {~IsNull(Measure.[BOD Structure_DC Site]), ~IsNull(Measure.[BOD Structure_Hub Site])};
   # - df_in_Location  = Select ([Location].[Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC","DC_HUB_MC_AP2"}).relatedmembers([Location]))  on row ,() on column; # 2025-11-20 삭제
   # - df_in_Location = select ([Version].[Version Name] * [Location].[Region].filter(#.Name=="EUROPE").relatedmembers([Location])) on row ,() on column;
   # - df_in_ToLocaton = select ([Version].[Version Name] * [To Location].[To Location Region].filter(#.Name=="EUROPE").relatedmembers([To Location])) on row ,() on column;
   # - df_in_SubLocation = select ([Version].[Version Name] * [Sub Location].[Sub Location Region].filter(#.Name=="EUROPE").relatedmembers([Sub Location])) on row ,() on column;


* 데이턱 샂게
    - DELETE DATA FOR MODEL [Multi Site by Item] where {Version.[Version Name].[CWV_MP], isnull(measure.[Multi Site by Item_Update Time]), isnull(measure.[Multi Site by Item_Updated By])};

* Output Table
    - df_out_MultiSiteByItem = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] ) on row, ({Measure.[Multi Site by Item_AP2 Name], Measure.[Multi Site by Item_Created By], Measure.[Multi Site by Item_Creation Time], Measure.[Multi Site by Item_Update Time], Measure.[Multi Site by Item_Updated By]}) on column;
    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    EXEC plugin instance [PY_UI_MultiSitebyItem] for measures {[Multi Site by Item_Created By]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), (paramOutVersion , "CWP_MP"),([Param.o9_sys_log_level], "DEBUG")} ;


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
warnings.filterwarnings("ignore")

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_MultiSitebyItem'
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

def print_df(df, df_name, _localFlag=True):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)

def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)

def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')

gfn_saveDf = vdCommon.gfn_saveDf

Logger.debug(f'[START] {str_instance}')
Logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')
tracemalloc.start()

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
    # # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_MultiSite = read_csv_file('df_in_MultiSite')
        df_in_BODItem = read_csv_file('df_in_BODItem')
        df_in_APName = read_csv_file('df_in_APName')
        df_In_MultiSitebyItem = read_csv_file('df_In_MultiSitebyItem')


    print_df(df_in_MultiSite, "df_in_MultiSite ", True)
    print_df(df_in_BODItem, "df_in_BODItem", True)
    print_df(df_in_APName, "df_in_APName", True)
    print_df(df_In_MultiSitebyItem, "df_In_MultiSitebyItem", True)


    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Location_COLUMN = 'Location.[Location]'
    TO_Location_COLUMN = 'To Location.[To Location]'
    SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    Item_Product_COLUMN = 'Item.[Product]'
    Item_COLUMN = 'Item.[Item]'
    Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
    Category_COLUMN = 'Category.[Category]'

    SALES_DOMAIN_AP2_Name_COLUMN = 'Sales Domain.[AP2$DisplayName]'
    Sales_Domain_DisplayName = 'Sales Domain.[DisplayName]'
    SOPDCDEF = 'SOPDCDEF'
    SELLERMAP = 'SELLERMAP'
    MULTILEVEL = 'MULTILEVEL'
    Multi_Site_AP2_Name = 'Multi Site_AP2 Name'

    Multi_Site_by_Item_Created_By = 'Multi Site by Item_Created By'
    Multi_Site_by_Item_Creation_Time = 'Multi Site by Item_Creation Time'
    Multi_Site_by_Item_Update_Time = 'Multi Site by Item_Update Time'
    Multi_Site_by_Item_Updated_By = 'Multi Site by Item_Updated By'
    Multi_Site_by_Item_AP2_Name = 'Multi Site by Item_AP2 Name'

    Dummy = 'Dummy'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3 (1) 날짜 데이터 설정을 위한 전처리 → 현재 Sever Error 발생
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')

    # Local인 경우와 Live Server 의 Columns명 통일
    if SALES_DOMAIN_AP2_Name_COLUMN in df_in_APName.columns:
        df_in_APName.rename(columns={SALES_DOMAIN_AP2_Name_COLUMN: Sales_Domain_DisplayName}, inplace=True)

    # 전처리 단계
    # BOM Item 전처리를 위한 설정
    # BOD Item grain columns 설정
    grain_cols = [Version_COLUMN, Location_COLUMN, SUB_LOCATION_COLUMN, Item_COLUMN, Item_Product_COLUMN]
    # 중복 삭제 후 기본 데이터 프레임 생성
    df_in_BODItem_base = df_in_BODItem[grain_cols].drop_duplicates(keep='first')

    # Category_COLUMN 값 확인 (틀린 경우 Error 발생)
    # assert df_in_MultiSite[Category_COLUMN].unique().tolist() == [SOPDCDEF, SELLERMAP, MULTILEVEL]

    # Category_COLUMN 에 따른 Data Frame 설정
    # Category_COLUMN 가 SOPDCDEF 인 경우
    df_in_MultiSite_SOPDCDEF = df_in_MultiSite[df_in_MultiSite[Category_COLUMN] == SOPDCDEF].drop(
        columns=[Dummy, SUB_LOCATION_COLUMN], axis=1)
    # 2026-02-11 ybest7.park(수정)------------------------------------------------------------------------------------
    # df_in_MultiSite_SOPDCDEF = df_in_MultiSite[df_in_MultiSite[Category_COLUMN] == SOPDCDEF].drop(
    #     columns=[Dummy, SUB_LOCATION_COLUMN], axis=1).rename(
    #     columns={TO_Location_COLUMN: Location_COLUMN, Location_COLUMN: TO_Location_COLUMN})
    # 2026-02-11 ybest7.park(수정)------------------------------------------------------------------------------------
    # Category_COLUMN 가 MULTILEVEL 인 경우
    df_in_MultiSite_MULTILEVEL = df_in_MultiSite[df_in_MultiSite[Category_COLUMN] == MULTILEVEL].drop(
        columns=Dummy,axis=1)
    # Category_COLUMN 가 SELLERMAP 인 경우
    df_in_MultiSite_SELLERMAP = df_in_MultiSite[df_in_MultiSite[Category_COLUMN] == SELLERMAP].drop(
        columns=Dummy,axis=1)

    # 조건에 따른 데이터 프레임 Merge
    # df_in_MultiSite_SOPDCDEF 인 경우
    df_in_MultiSite_SOPDCDEF = df_in_MultiSite_SOPDCDEF.merge(
        df_in_BODItem_base.rename(columns={SUB_LOCATION_COLUMN:TO_Location_COLUMN}),
        on=[Version_COLUMN, Location_COLUMN, TO_Location_COLUMN, Item_Product_COLUMN],
        how='left')
    # 2026-02-11 ybest7.park(수정)------------------------------------------------------------------------------------
    # df_in_MultiSite_SOPDCDEF = df_in_MultiSite_SOPDCDEF.rename(
    #     columns={TO_Location_COLUMN:Location_COLUMN,
    #              Location_COLUMN :TO_Location_COLUMN})
    # 2026-02-11 ybest7.park(수정)------------------------------------------------------------------------------------
    print_df(df_in_MultiSite_SOPDCDEF, "df_in_MultiSite_SOPDCDEF 확인 ")

    # df_in_MultiSite_MULTILEVEL 인 경우
    df_in_MultiSite_MULTILEVEL = df_in_MultiSite_MULTILEVEL.merge(
        df_in_BODItem_base.rename(columns={Location_COLUMN: TO_Location_COLUMN}),
        on=[Version_COLUMN, TO_Location_COLUMN, SUB_LOCATION_COLUMN, Item_Product_COLUMN],
        how='left')
    print_df(df_in_MultiSite_MULTILEVEL, "df_in_MultiSite_MULTILEVEL 확인 ")

    # df_in_MultiSite_SELLERMAP 인 경우
    df_in_MultiSite_SELLERMAP = df_in_MultiSite_SELLERMAP.merge(
        df_in_BODItem_base[[Version_COLUMN, SUB_LOCATION_COLUMN, Item_Product_COLUMN, Item_COLUMN]].rename(
            columns={SUB_LOCATION_COLUMN: TO_Location_COLUMN}),
        on=[Version_COLUMN, TO_Location_COLUMN, Item_Product_COLUMN],
        how='left')
    print_df(df_in_MultiSite_SELLERMAP, "df_in_MultiSite_SELLERMAP 확인 ")

    # Data Frome 합치기
    df_out_MultiSite_Temp = pd.concat(
        [df_in_MultiSite_SOPDCDEF, df_in_MultiSite_MULTILEVEL, df_in_MultiSite_SELLERMAP],
        axis=0)
    # 기존의 없는 것 들만 Update 하기 위한 전처리
    # 필털를 위한 Index columns 설정
    index_cols = [Version_COLUMN, Location_COLUMN, Item_COLUMN, SALES_DOMAIN_AP2_COLUMN,
                  TO_Location_COLUMN,SUB_LOCATION_COLUMN]
    # SALES_DOMAIN_AP2_COLUMN 데이터 타입 변경
    df_out_MultiSite_Temp[SALES_DOMAIN_AP2_COLUMN] = df_out_MultiSite_Temp[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_In_MultiSitebyItem[SALES_DOMAIN_AP2_COLUMN] = df_In_MultiSitebyItem[SALES_DOMAIN_AP2_COLUMN].astype(str)

    # TO_Location_COLUMN 값 및 SUB_LOCATION_COLUMN 값 설정
    df_out_MultiSite_Temp[TO_Location_COLUMN] = df_out_MultiSite_Temp[TO_Location_COLUMN].fillna('-')
    df_out_MultiSite_Temp[SUB_LOCATION_COLUMN] = df_out_MultiSite_Temp[SUB_LOCATION_COLUMN].fillna('-')

    # 만들어진 데이터 프레임의 필터를 위한 설정
    df_out_MultiSite_Temp = df_out_MultiSite_Temp[index_cols]
    df_out_MultiSite_Temp_index = df_out_MultiSite_Temp.set_index(index_cols).index
    # 기존 Input Data 필터링 설정
    df_In_MultiSitebyItem_index = df_In_MultiSitebyItem.set_index(index_cols).index
    # 최종 Out put 설정
    df_out_MultiSiteByItem = df_out_MultiSite_Temp[~df_out_MultiSite_Temp_index.isin(df_In_MultiSitebyItem_index)]


    # 기타 MG 값 설정
    # Multi_Site_by_Item_AP2_Name 설정을 위한 데이터 타입 변경
    df_out_MultiSiteByItem[SALES_DOMAIN_AP2_COLUMN] = df_out_MultiSiteByItem[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_in_APName[SALES_DOMAIN_AP2_COLUMN] = df_in_APName[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_out_MultiSiteByItem[Multi_Site_by_Item_AP2_Name] = df_out_MultiSiteByItem[SALES_DOMAIN_AP2_COLUMN].map(
        df_in_APName.set_index(SALES_DOMAIN_AP2_COLUMN)[Sales_Domain_DisplayName])

    df_out_MultiSiteByItem[Multi_Site_by_Item_Created_By] = 'PY_UI_Multi Site by Item'
    df_out_MultiSiteByItem[Multi_Site_by_Item_Creation_Time] = datetime.datetime.now().strftime('%Y-%m-%d')
    df_out_MultiSiteByItem[Multi_Site_by_Item_Updated_By] = ''
    df_out_MultiSiteByItem[Multi_Site_by_Item_Update_Time] = ''

    print_df(df_out_MultiSiteByItem, 'df_out_MultiSiteByItem out put 확인 ', True)

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4 (1) Global Top 기준 pivot Test
    ###############################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    print_df(df_out_MultiSiteByItem, 'df_Out_MultiSitebyItem', True)


    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5 (1) 최종 Out_Put Save
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    row_count, col_count = df_out_MultiSiteByItem.shape
    note(f'=====> Final df_Out_MultiSitebyItem rows : {row_count} , Columns : {col_count}')
    print_df(df_out_MultiSiteByItem, 'df_Out_MultiSitebyItem')

    if is_local:
        note(f'=====> Final output table create')
        print_df(df_out_MultiSiteByItem, 'df_Out_MultiSitebyItem', True)

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_Out_MultiSitebyItem = pd.DataFrame([], columns=[])

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
