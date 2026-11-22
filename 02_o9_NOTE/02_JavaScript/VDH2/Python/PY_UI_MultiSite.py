

"""

* 프로그램명
    - PY_UI_MultiSite

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.01.24 / ybest7.park (박병훈) / Create
- 2025.04.15 / ybest7.park (박병훈) / input Grain 변경
- 2025-06.12 / ybest7.park (박병훈) / 데이터 삭제 스크립트 수정
- 2025-06-17 / ybest7.park (박병훈) / Logic 수정 (df_in_MultiSiteByItem)
- 2025-11-13 /  ybest7.park (박병훈) / df_in_Location input data 추가 Logic 추가
- 2025-11-19 / ybest7.park (박병훈)  / df_in_BODProductSET input data 추가 및  To_Location_COLUMN, Location_COLUMN, SUB_LOCATION_COLUMN 설정 로직 변경
- 2025-11-20 / ybest7.park (박병훈)  / df_in_SiteAP2Map & df_in_Location input data 합치면서 로직 삭제

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary
Select ([Version].[Version Name] * [Item].[Item] * [Item].[Product Group] * [Item].[Product] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[BOD Structure_DC Site], Measure.[BOD Structure_Hub Site], Measure.[Dummy]}) on column.filter(Measure.[BOD Structure_DC Site]!= "-");


* Input Table
   - df_in_BODStructure =   Select ([Version].[Version Name] * [Item].[Item] * [Item].[Product Group] * [Item].[Product] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[BOD Structure_DC Site], Measure.[BOD Structure_Hub Site], Measure.[Dummy]}) on column  where {~IsNull(Measure.[BOD Structure_DC Site]), ~IsNull(Measure.[BOD Structure_Hub Site])};
   - df_in_SiteAP2Map = Select ([Version].[Version Name] * [Location].[Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC","DC_HUB_MC_AP2"}).relatedmembers([Location])) on row, ({Measure.[Site AP2 Map_Ship To], Measure.[Site AP2 Map_Valid Flag] , Measure.[Dummy]}) on column where {(Measure.[Site AP2 Map_Valid Flag] == "Y")};
   - df_in_MultiSite = Select ([Version].[Version Name]* [Location].[Location] * [Item].[Product] * [To Location].[To Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] ) on row, ({Measure.[Multi Site_BOD Valid Flag], Measure.[Dummy]}) on column;
   - df_in_Version = select ([Version].[Version Name]);
   - df_in_APName = select ([Sales Domain].[AP2]) on row, () on column include memberproperties {[Sales Domain].[AP2], [DisplayName]} ;
    df_in_BODProductSET = Select ([Version].[Version Name] * [Location].[Site Stage].filter(#.Name contains "DC_HUB_MC_AP2").relatedmembers([Location]) * [Sub Location].[Sub Site Stage].filter(#.Name contains "DC").relatedmembers([Sub Location])) on row, ({Measure.[BOD Prod SET_BOD Valid], Measure.[Dummy]}) on column where {Measure.[BOD Prod SET_BOD Valid] == "Y"};
   # - df_in_Location  = Select ([Location].[Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC","DC_HUB_MC_AP2"}).relatedmembers([Location]))  on row ,() on column; # 2025-11-20 삭제
   # - df_in_SubLocation = select ([Version].[Version Name] * [Sub Location].[Sub Location Region].filter(#.Name=="EUROPE").relatedmembers([Sub Location])) on row ,() on column;
   # - df_in_ToLocation = select ([Version].[Version Name] * [Sub Location].[Sub Location Region].filter(#.Name=="EUROPE").relatedmembers([Sub Location])) on row ,() on column;


* 데이턱 삭제
    - DELETE DATA FOR MODEL [Multi Site] where {Version.[Version Name].[CWV_MP] , isnull(measure.[Multi Site_Update Time]), isnull(measure.[Multi Site_Updated By])};  # 2025-06-12 수정

* 유의 사항
    - df_in_MultiSite에 신규 데이터 없을 시 프로그램 결과 null값 반영됨

* Output Table
    - df_out_MultiSite = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Product] * [Sales Domain].[AP2] * [To Location].[To Location] * [Sub Location].[Sub Location] ) on row,  ({Measure.[Multi Site_AP2], Measure.[Multi Site_BOD Valid Flag], Measure.[Multi Site_Created By], Measure.[Multi Site_Creation Time], Measure.[Multi Site_PSI Toggle], Measure.[Multi Site_Product], Measure.[Multi Site_Product Grp],Measure.[Multi Site_AP2 Name], Measure.[Multi Site_Update Time], Measure.[Multi Site_Updated By]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_MultiSite] for measures {[Multi Site_BOD Valid Flag]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ),(paramOutVersion , "CWP_MP"), ([Param.o9_sys_log_level], "DEBUG")} ;


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
str_instance = 'PY_UI_MultiSite'
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


def print_df(df, df_name, _localFlag=False):
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

        df_in_BODStructure = read_csv_file('df_in_BODStructure')
        df_in_SiteAP2Map = read_csv_file('df_in_SiteAP2Map')
        df_in_MultiSite = read_csv_file('df_in_MultiSite')
        df_in_Version = read_csv_file('df_in_Version')
        df_in_APName = read_csv_file('df_in_APName')
        df_in_BODProductSET = read_csv_file('df_in_BODProductSET')
        # df_in_SubLocation = read_csv_file('df_in_SubLocation')
        # df_in_ToLocation = read_csv_file('df_in_ToLocation')
        # df_in_Location = read_csv_file('df_in_Location')


    print_df(df_in_BODStructure, 'df_in_BODStructure',True)
    print_df(df_in_SiteAP2Map, 'df_in_SiteAP2Map',True)
    print_df(df_in_MultiSite, 'df_in_MultiSite',True)
    print_df(df_in_Version, 'df_in_Version',True)
    print_df(df_in_APName, 'df_in_APName',True)
    print_df(df_in_BODProductSET, 'df_in_BODProductSET', True)
    # gfn_saveDf(df_in_Location, 'df_in_APName', True)
    # gfn_saveDf(df_in_SubLocation, 'df_in_APName', True)
    # gfn_saveDf(df_in_ToLocation, 'df_in_APName', True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Location_COLUMN = 'Location.[Location]'
    Item_ProductGroup_COLUMN = 'Item.[Product Group]'
    Item_Product_COLUMN = 'Item.[Product]'
    Item_COLUMN = 'Item.[Item]'
    SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    TO_Location_COLUMN = 'To Location.[To Location]'
    SALES_DOMAIN_AP2_Name_COLUMN = 'Sales Domain.[AP2$DisplayName]'  # Local 인 경우는 "Sales Domain.[DisplayName]"로 변경 필요
    Sales_Domain_DisplayName = 'Sales Domain.[DisplayName]'

    BOD_Structure_DC_Site = 'BOD Structure_DC Site'
    Site_AP2_Map_Ship_to = 'Site AP2 Map_Ship To'
    BOD_Structure_Hub_Site = 'BOD Structure_Hub Site'
    Multi_Site_BOD_Valid_Flag = 'Multi Site_BOD Valid Flag'
    Multi_Site_Created_By = 'Multi Site_Created By'
    Multi_Site_Creation_Time = 'Multi Site_Creation Time'
    Multi_Site_PSI_Toggle = 'Multi Site_PSI Toggle'
    Multi_Site_Update_Time = 'Multi Site_Update Time'
    Multi_Site_Updated_By = 'Multi Site_Updated By'

    Multi_Site_AP2 = 'Multi Site_AP2'
    Multi_Site_AP2_Name = 'Multi Site_AP2 Name'
    Multi_Site_Product = 'Multi Site_Product'
    Multi_Site_Product_Grp = 'Multi Site_Product Grp'
    PY_UI_Multi_Site = 'PY_UI_Multi Site'
    REQ = 'REQ'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) Multi_Site_BOD_Valid_Flag 값 초기화
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : Check memory usage & runtime')

    # Local인 경우와 Live Server 의 Columns명 통일
    if SALES_DOMAIN_AP2_Name_COLUMN in df_in_APName.columns:
        df_in_APName.rename(columns={SALES_DOMAIN_AP2_Name_COLUMN: Sales_Domain_DisplayName}, inplace=True)

    # 최신 Version 선택
    Version = df_in_Version.iloc[0, 0]

    # 전처리를 위한 Multi_Site_BOD_Valid_Flag 값 설정 'N'
    df_in_MultiSite[Multi_Site_BOD_Valid_Flag] = 'N'

    ########################################## 2025-11-13 ybest7.park 추가 ##############################################
    # df_in_Location 의 Location 리스트로 만들기 --> BOD_Structure_Hub_Site 필터를 위한 전처리
    # Location_List = df_in_Location[Location_COLUMN].unique().tolist()
    #
    # # df_in_SiteAP2Map 에서 Location이 Location_List 만 필터링
    # df_in_SiteAP2Map = df_in_SiteAP2Map[df_in_SiteAP2Map[Location_COLUMN].isin(Location_List)]
    # df_in_SiteAP2Map[Site_AP2_Map_Ship_to] = df_in_SiteAP2Map[Site_AP2_Map_Ship_to].astype(str).str.replace(".",'')
    # 2025-11-20 Input Query 통합을 통해 로직 삭제

    ########################################## 2025-11-13 ybest7.park 추가 ##############################################
    # df_in_BODStructure Location 정보를 새로이 설정하기 위한 전처리
    # df_in_BODStructure_Temp 임시 테이블 만들고 Location Columns 삭제
    df_in_BODStructure_Temp = df_in_BODStructure.drop(columns=[Location_COLUMN, 'Dummy']).copy()
    # BOD_Structure_DC_Site 가 null이 아닌 경우만 필터링
    df_in_BODStructure_Temp = df_in_BODStructure_Temp[df_in_BODStructure_Temp[BOD_Structure_DC_Site].notnull()]
    # Location 정보와 SALES_DOMAIN_AP2_COLUMN 을 가져 오기 위해  df_in_SiteAP2Map 와 merge
    df_in_BODStructure_Temp = df_in_BODStructure_Temp.merge(df_in_SiteAP2Map,
                                                            left_on=[Version_COLUMN, BOD_Structure_DC_Site],
                                                            right_on=[Version_COLUMN, Location_COLUMN], how='left')
    # SALES_DOMAIN_AP2_COLUMN 컬럼 설정
    df_in_BODStructure_Temp = df_in_BODStructure_Temp.rename(columns={Site_AP2_Map_Ship_to: SALES_DOMAIN_AP2_COLUMN})
    print_df(df_in_BODStructure_Temp, 'df_in_BODStructure_Temp -0', True)
    note(f"================> Item_Product_COLUMN Count : {df_in_BODStructure_Temp[Item_Product_COLUMN].value_counts()}")
    # df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].astype(int)
    # SALES_DOMAIN_AP2_COLUMN null 인 경우 '-' 로 채우기
    df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].fillna(
        '-').astype(str)
    print_df(df_in_BODStructure_Temp, 'df_in_BODStructure_Temp -1')
    # df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].astype(str)
    # df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].str.split('.').str[0]

    # print_df(df_in_BODStructure_Temp, 'df_in_BODStructure_Temp -1')

    # SALES_DOMAIN_AP2_COLUMN 값을 재 설정하기 위한 전 처리
    # merge 를 위해 SALES_DOMAIN_AP2_COLUMN 데이터 타입 변경 (혹시 int 인 경우 방어 코딩 )
    df_in_APName[SALES_DOMAIN_AP2_COLUMN] = df_in_APName[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].astype(str)

    # df_in_APName 와 df_in_BODStructure_Temp merge (SALES_DOMAIN_AP2_COLUMN 기준) df_in_BODStructure_Temp 중 df_in_APName 에 있는 것만 필터링
    df_in_BODStructure_Temp = df_in_BODStructure_Temp.merge(df_in_APName, on=SALES_DOMAIN_AP2_COLUMN, how='left')
    # SALES_DOMAIN_AP2_COLUMN 이 빈 값인 경우 'ALL'로 설정
    df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = np.where(
        df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].isna(),
        'ALL', df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN])

    # SALES_DOMAIN_AP2_COLUMN 값 변경하기
    # df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_in_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].str.replace(".",
    #                                                                                                                 '')
    #  Out put 설정을 위한 데이터 프레임 생성
    df_out_BODStructure_Temp = df_in_BODStructure_Temp.copy()

    print_df(df_out_BODStructure_Temp, 'df_out_BODStructure_Temp -2', True)

    # TO_Location_COLUMN 설정 BOD_Structure_Hub_Site 값으로 적용
    df_out_BODStructure_Temp[TO_Location_COLUMN] = df_out_BODStructure_Temp[BOD_Structure_Hub_Site]
    ########################### 2025-11-19 로직 수정 ###################################################################
    df_out_BODStructure_Temp[Location_COLUMN] = df_out_BODStructure_Temp[BOD_Structure_DC_Site]
    # Location_COLUMN 값 설정 BOD_Structure_DC_Site 에 '@' 가 있지 않으면  '-' 로 변경
    # df_out_BODStructure_Temp[Location_COLUMN] = np.where(
    #     ~df_out_BODStructure_Temp[BOD_Structure_DC_Site].str.contains("@"), "-",
    #     df_out_BODStructure_Temp[BOD_Structure_DC_Site])
    # # SUB_LOCATION_COLUMN 값 설정 BOD_Structure_DC_Site 에 '@' 가 있으면  '-' 로 변경
    # df_out_BODStructure_Temp[SUB_LOCATION_COLUMN] = np.where(
    #     df_out_BODStructure_Temp[BOD_Structure_DC_Site].str.contains("@"), "-",
    #     df_out_BODStructure_Temp[BOD_Structure_DC_Site])

    df_out_BODStructure_Temp = df_out_BODStructure_Temp.merge(df_in_BODProductSET[
                                                                  [Version_COLUMN, Location_COLUMN,
                                                                   SUB_LOCATION_COLUMN]],
                                                              on = [Version_COLUMN,Location_COLUMN], how='left')

    # 임시로 데이터가 NAN 인 경우를 대비하여 Fillna 적용 ############ 2025-11-19 ybest7.park(박병훈)##########################
    df_out_BODStructure_Temp[SUB_LOCATION_COLUMN] = df_out_BODStructure_Temp[SUB_LOCATION_COLUMN].fillna('-')

    ########################### 2025-11-19 로직 수정 ###################################################################

    # # SALES_DOMAIN_AP2_COLUMN 값 변경
    df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = np.where(
        df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] == "-",
        df_out_BODStructure_Temp[Location_COLUMN].str.split("@").str[1],
        df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN])
    # df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = np.where(
    #     df_out_BODStructure_Temp[Location_COLUMN].str.contains('@'),
    #     df_out_BODStructure_Temp[Location_COLUMN].str.split("@").str[1],
    #     df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN])
    # Multi_Site_AP2  와 Multi_Site_AP2_Name 값 설정  (SALES_DOMAIN_AP2_Name_COLUMN 적용)

    # df_out_BODStructure_Temp & df_in_SiteAP2Map 데이터 타입 변경
    df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_in_APName[SALES_DOMAIN_AP2_COLUMN] = df_in_APName[SALES_DOMAIN_AP2_COLUMN].astype(str)

    df_out_BODStructure_Temp[Multi_Site_AP2] = df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].map(
        df_in_APName.set_index(SALES_DOMAIN_AP2_COLUMN)[Sales_Domain_DisplayName])
    # 기타 mg 값 설정
    df_out_BODStructure_Temp[Multi_Site_BOD_Valid_Flag] = REQ
    df_out_BODStructure_Temp[Multi_Site_Created_By] = PY_UI_Multi_Site
    df_out_BODStructure_Temp[Multi_Site_Creation_Time] = datetime.datetime.now().strftime('%Y-%m-%d')
    df_out_BODStructure_Temp[Multi_Site_PSI_Toggle] = 'Y'
    df_out_BODStructure_Temp[Multi_Site_Product] = df_out_BODStructure_Temp[Item_Product_COLUMN]
    df_out_BODStructure_Temp[Multi_Site_Product_Grp] = df_out_BODStructure_Temp[Item_ProductGroup_COLUMN]
    df_out_BODStructure_Temp[Multi_Site_Update_Time] = ''
    df_out_BODStructure_Temp[Multi_Site_Updated_By] = ''
    # Multi_Site_AP2  와 Multi_Site_AP2_Name 값 설정  (SALES_DOMAIN_AP2_Name_COLUMN 적용)
    # df_out_BODStructure_Temp[Multi_Site_AP2] = df_out_BODStructure_Temp[SALES_DOMAIN_AP2_Name_COLUMN]
    df_out_BODStructure_Temp[Multi_Site_AP2_Name] = df_out_BODStructure_Temp[Multi_Site_AP2]
    note(f"------------> Multi Site_AP2 Name unique : {df_out_BODStructure_Temp['Multi Site_AP2 Name'].unique()}")

    # df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = np.where(
    #     df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] == "-",
    #     df_out_BODStructure_Temp[Location_COLUMN].str.split("@").str[1],
    #     df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN])


    print_df(df_out_BODStructure_Temp, 'df_out_BODStructure_Temp',True)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4 (1) Out Put 설정
    ###############################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # save_csv_file(df_in_MultiSite, 'df_in_MultiSite_임시')
    # save_csv_file(df_out_BODStructure_Temp, 'df_out_BODStructure_Temp_임시')

    # df_in_MultiSite = df_in_MultiSite.rename()
    #
    # 인덱스 기준 Grain col 설정
    grain_col = [Location_COLUMN, Item_Product_COLUMN,
                 SUB_LOCATION_COLUMN,TO_Location_COLUMN,SALES_DOMAIN_AP2_COLUMN]
    # print_df(df_in_MultiSite[grain_col], 'df_in_MultiSite')
    # print_df(df_out_BODStructure_Temp[grain_col], 'df_out_BODStructure_Temp')

    # df_in_MultiSite & df_out_BODStructure_Temp 의 SALES_DOMAIN_AP2_COLUMN Type 변경
    df_in_MultiSite[SALES_DOMAIN_AP2_COLUMN] = df_in_MultiSite[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN] = df_out_BODStructure_Temp[SALES_DOMAIN_AP2_COLUMN].astype(str)

    # df_in_MultiSite & df_out_BODStructure_Temp Index 설정
    df_in_MultiSite_index = df_in_MultiSite.set_index(grain_col).index
    # note(f"df_in_MultiSite_index_Valus{df_in_MultiSite_index}")
    df_out_MultiSite_index = df_out_BODStructure_Temp.set_index(grain_col).index
    # note(f"df_out_MultiSite_index{df_out_MultiSite_index}")
    # df_out_BODStructure_Temp 에 있는 것 중 df_in_MultiSite 없는 것 추출
    df_out_BODStructure_Temp = df_out_BODStructure_Temp[~df_out_MultiSite_index.isin(df_in_MultiSite_index)]

    df_out_MultiSite = df_out_BODStructure_Temp.copy()

    # df_out_MultiSite[SALES_DOMAIN_AP2_COLUMN] = np.where(
    #     df_out_MultiSite[SALES_DOMAIN_AP2_COLUMN] == "-",
    #     df_out_MultiSite[Location_COLUMN].str.split("@").str[1],
    #     df_out_MultiSite[SALES_DOMAIN_AP2_COLUMN])

    print_df(df_out_MultiSite, 'df_out_MultiSite')

    # Version 설정 및 데이터 프레임 순서 지정
    df_out_MultiSite[Version_COLUMN] = Version
    df_out_MultiSite = df_out_MultiSite[
        [Version_COLUMN,TO_Location_COLUMN,Location_COLUMN,SUB_LOCATION_COLUMN, Item_Product_COLUMN,
         SALES_DOMAIN_AP2_COLUMN,Multi_Site_AP2,
         Multi_Site_BOD_Valid_Flag, Multi_Site_Created_By, Multi_Site_Creation_Time,
         Multi_Site_PSI_Toggle, Multi_Site_Product, Multi_Site_Product_Grp, Multi_Site_AP2_Name,
         Multi_Site_Update_Time,Multi_Site_Updated_By]]

    df_out_MultiSite = df_out_MultiSite.drop_duplicates().reset_index(drop=True)

    # # Location 컬럼으로 변경
    # df_in_SubLocation = df_in_SubLocation.rename(columns={SUB_LOCATION_COLUMN : Location_COLUMN})
    # df_in_ToLocation = df_in_ToLocation.rename(columns={TO_Location_COLUMN: Location_COLUMN})
    #
    # # Location List 만들기
    # locations_list = pd.concat([df_in_Location, df_in_SubLocation, df_in_ToLocation])[Location_COLUMN].drop_duplicates().tolist()
    # note(f"=============================> locations_list 의 갯수 : {len(locations_list)}")
    #
    # # 유럽 Location 필터링
    # df_out_MultiSite = df_out_MultiSite[df_out_MultiSite[Location_COLUMN].isin(locations_list)]

    note(f" ===================> df_out_MultiSite Item_Product_COLUMN conut : {df_out_MultiSite[Item_Product_COLUMN].value_counts()} ")
    print_df(df_out_MultiSite, 'df_out_MultiSite',True)
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) 최종 Out_Put Save
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    row_count, col_count = df_out_MultiSite.shape
    note(f'=====> Final df_out_MultiSite rows : {row_count} , Columns : {col_count}')

    if is_local:
        note(f'=====> Final output table create')
        print_df(df_out_MultiSite, 'df_out_MultiSite',True)

    print_df(df_out_MultiSite, 'df_out_MultiSite_최종확인', True)

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_MultiSite = pd.DataFrame([], columns=[])

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
