"""

* 프로그램명
    - PY_UI_QuotaAnalysis

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.02.25 / ybest7.park (박병훈) / Create
- 2025-08-21 / ybest7.park (박병훈) / 수정
    df_in_MtrlInfoRecord_temp 의 '확장 범위 설정' 부분 수정 np.range 로 범위 확장 로직 수정 및 Input Query 수정
- 2026-01-28 / ybest7.park (박병훈) / 수정
    input data 중 빈 데이터가 들어오는 경우를 대비하여 코드 수정


* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
    - df_in_GRMtrl = Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week].filter(#.Key < &CurrentWeek.element(0).Key && #.Key >= &CurrentWeek.element(0).LeadOffset(-2).Key) * &ItemMaterialMLS3QuotaMgmt * [Sub Location].[Sub Location].filter(#.DisplayName Startswith "G")) on row, ({Measure.[GR Mtrl_Amt], Measure.[GR Mtrl_Amt KRW], Measure.[GR Mtrl_Amt USD], Measure.[GR Mtrl_Currency], Measure.[GR Mtrl_Qty], Measure.[GR Mtrl_Trans Mode], Measure.[Dummy]}) on column.filter(Measure.[GR Mtrl_Amt]>0 || Measure.[GR Mtrl_Qty]>0);
    - df_in_DualMtrlAnlMst  = Select ([Version].[Version Name]* [Location].[Location] * [Item].[Item]* &ItemMaterialMLS3QuotaMgmt * [Category].[Category].[Dualized Mtrl Group-Master]  * [Group].[Group ID] ) on row, ({Measure.[Dual Mtrl Anl Mst_Flag], Measure.[Dummy]}) on column where {Measure.[Dual Mtrl Anl Mst_Flag] == true} ;
        # df_in_FCSTRFTHistW 삭제
    - df_in_FCSTRFTHistW  = Select ([Version].[Version Name] * [Location].[Location] * &MPHorizon * [To Time].[To Week] * [Week1].[Week1] * &ItemMaterialMLS3QuotaMgmt * [Sub Location].[Sub Location] ) on row, ({Measure.[FCST RTF Hist W_Fcst],Measure.[FCST RTF Hist W_Global Fcst], Measure.[Dummy]}) on column.filter(Measure.[FCST RTF Hist W_Fcst] >0 ||Measure.[FCST RTF Hist W_Global Fcst] >0 );
    - df_in_MtrlPSI = Select ([Version].[Version Name] * [Location].[Location] * &MPHorizon * &ItemMaterialMLS3QuotaMgmt * [Sub Location].[Sub Location].filter(#.DisplayName Startswith "G") * [Trans Mode].[Trans Mode] ) on row,({Measure.[Mtrl PSI_ARRIVAL_CMI],Measure.[Mtrl PSI_ARRIVAL_Excel],Measure.[Mtrl PSI_ARRIVAL_Global RTF],Measure.[Mtrl PSI_ARRIVAL_Open PO],Measure.[Mtrl PSI_ARRIVAL_RTF],Measure.[Mtrl PSI_ARRIVAL_RTP],Measure.[Mtrl PSI_ARRIVAL_SN],Measure.[Mtrl PSI_ARRIVAL_Supply Plan], Measure.[Dummy]}) on column;
    - df_in_MtrlInfoRecord = Select ([Version].[Version Name] * [Location].[Location] * &ItemMaterialMLS3QuotaMgmt * [Sequence].[Sequence] * [Vendor].[Vendor] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Mtrl Info Record_GT Code], Measure.[Mtrl Info Record_Valid From] , Measure.[Mtrl Info Record_Valid From Week], Measure.[Mtrl Info Record_Valid To], Measure.[Mtrl Info Record_Valid To Week],Measure.[Mtrl Info Record_Info Price USD], Measure.[Mtrl Info Record_Price Unit], Measure.[Dummy]}) on column;
    - df_in_GlobalQuotaMtrlW = Select ([Version].[Version Name] * &MPHorizon * &ItemMaterialMLS3QuotaMgmt * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({Measure.[Global Quota Mtrl W_Portion], Measure.[Dummy]}) on column where { Measure.[Global Quota Mtrl W_Portion] <> 0 };
    - df_in_PlantQuotaMtrlW = Select ([Version].[Version Name] * [Location].[Location] * &MPHorizon * &ItemMaterialMLS3QuotaMgmt * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({Measure.[Plant Quota Mtrl W_Portion],Measure.[Dummy]}) on column WHERE { Measure.[Plant Quota Mtrl W_Portion] <> 0 };
    - df_in_PlanningMonth = select([Time].[Week].filter(#.Key >= &MPCurrentWeek.element(0).LeadOffset(-2).Key && #.Key <= &MPHorizon.last.Key) * [Time].[Planning Month]);
    - df_in_TimeWeeks = select([Time].[Week]);

* 데이터 삭제
     DELETE DATA FOR MODEL [Quota Analysis] where {Version.[Version Name].[CWV_MP]};
     DELETE DATA FOR MODEL [Quota Anl] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_QuotaAnalysis = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({Measure.[Quota Anl_Amt], Measure.[Quota Anl_Amt Rate], Measure.[Quota Anl_Currency], Measure.[Quota Anl_Qty], Measure.[Quota Anl_Qty Rate]}) on column;
    - df_out_QuotaAnalysisChart = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Planning Month] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({Measure.[Quota Analysis_Amt], Measure.[Quota Analysis_Amt Rate], Measure.[Quota Analysis_Currency], Measure.[Quota Analysis_ETC Amt], Measure.[Quota Analysis_ETC Amt Rate], Measure.[Quota Analysis_ETC Qty], Measure.[Quota Analysis_ETC Qty Rate], Measure.[Quota Analysis_Qty], Measure.[Quota Analysis_Qty Rate], Measure.[Quota Analysis_Vendor Total Amt], Measure.[Quota Analysis_Vendor Total Qty], Measure.[Quota Analysis_Vendor1 Amt], Measure.[Quota Analysis_Vendor1 Amt Rate], Measure.[Quota Analysis_Vendor1 Qty], Measure.[Quota Analysis_Vendor1 Qty Rate], Measure.[Quota Analysis_Vendor2 Amt], Measure.[Quota Analysis_Vendor2 Amt Rate], Measure.[Quota Analysis_Vendor2 Qty], Measure.[Quota Analysis_Vendor2 Qty Rate], Measure.[Quota Analysis_Vendor3 Amt], Measure.[Quota Analysis_Vendor3 Amt Rate], Measure.[Quota Analysis_Vendor3 Qty], Measure.[Quota Analysis_Vendor3 Qty Rate], Measure.[Quota Analysis_Vendor4 Amt], Measure.[Quota Analysis_Vendor4 Amt Rate], Measure.[Quota Analysis_Vendor4 Qty], Measure.[Quota Analysis_Vendor4 Qty Rate], Measure.[Quota Analysis_Vendor5 Amt], Measure.[Quota Analysis_Vendor5 Amt Rate], Measure.[Quota Analysis_Vendor5 Qty], Measure.[Quota Analysis_Vendor5 Qty Rate]}) on column;
    -

* 테스트 스크립트
    EXEC plugin instance [PY_UI_QuotaAnalysis] for measures {[Quota Anl_Amt]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (paramOutVersion ,"CWV_MP")} ;



#### 추가 로직 변경 사항 #################################################################################################
    1. Vendor Code -> GT Code 맵핑로직 변경, Vendor Code(HQ)로 반영
    (GR실적, FCST, Intransit 데이터)
#######################################################################################################################


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

from dateutil import parser as date_parser
from typing import Union
import warnings

warnings.filterwarnings("ignore")
########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_QuotaAnalysis'
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
    Logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format, p_row_num=5)


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
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, Logger, com.gfn_get_isLocal(), (os.path.dirname(__file__) if com.gfn_get_isLocal() else ""))

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

        df_in_GRMtrl = read_csv_file('df_in_GRMtrl')
        df_in_DualMtrlAnlMst = read_csv_file('df_in_DualMtrlAnlMst')
        # df_in_FCSTRFTHistW = read_csv_file('df_in_FCSTRFTHistW_VD03')
        df_in_MtrlPSI = read_csv_file('df_in_MtrlPSI')
        df_in_MtrlInfoRecord = read_csv_file('df_in_MtrlInfoRecord')
        df_in_GlobalQuotaMtrlW = read_csv_file('df_in_GlobalQuotaMtrlW')
        df_in_PlantQuotaMtrlW = read_csv_file('df_in_PlantQuotaMtrlW')
        df_in_PlanningMonth = read_csv_file('df_in_PlanningMonth')
        df_in_TimeWeeks = read_csv_file('df_in_TimeWeeks')


    print_df(df_in_GRMtrl, 'df_in_GRMtrl')
    print_df(df_in_DualMtrlAnlMst, 'df_in_DualMtrlAnlMst')
    # print_df(df_in_FCSTRFTHistW, 'df_in_FCSTRFTHistW')
    print_df(df_in_MtrlPSI, 'df_in_MtrlPSI')
    print_df(df_in_MtrlInfoRecord, 'df_in_MtrlInfoRecord')
    print_df(df_in_GlobalQuotaMtrlW, 'df_in_GlobalQuotaMtrlW')
    print_df(df_in_PlantQuotaMtrlW, 'df_in_PlantQuotaMtrlW')
    print_df(df_in_PlanningMonth, 'df_in_PlanningMonth')
    print_df(df_in_TimeWeeks, 'df_in_TimeWeeks')


    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_Name_COLUMN = 'Version.[Version Name]'
    Location_COLUMN = 'Location.[Location]'
    Time_Week_COLUMN = 'Time.[Week]'
    Item_Material_COLUMN = 'Item Material.[Item Material]'
    Item_COLUMN = 'Item.[Item]'
    Category_COLUMN = 'Category.[Category]'
    Group_ID_COLUMN = 'Group.[Group ID]'
    Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
    To_Time_To_Week_COLUMN = 'To Time.[To Week]'
    Week1_COLUMN = 'Week1.[Week1]'
    Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
    Sequence_COLUMN = 'Sequence.[Sequence]'
    Vendor_COLUMN = 'Vendor.[Vendor]'
    Partner_Vendor_COLUMN = 'Partner Vendor.[Partner Vendor]'
    Time_Planning_Month_COLUMN = 'Time.[Planning Month]'

    Arrival_Total = "Arrival Total"

    GR_Mtrl_Amt = 'GR Mtrl_Amt'
    GR_Mtrl_Amt_KRW = 'GR Mtrl_Amt KRW'
    GR_Mtrl_Amt_USD = 'GR Mtrl_Amt USD'
    GR_Mtrl_Currency = 'GR Mtrl_Currency'
    GR_Mtrl_Qty = 'GR Mtrl_Qty'
    GR_Mtrl_Trans_Mode = 'GR Mtrl_Trans Mode'

    Dual_Mtrl_Anl_Mst_Flag = 'Dual Mtrl Anl Mst_Flag'

    FCST_RTF_Hist_W_Fcst = 'FCST RTF Hist W_Fcst'

    Mtrl_PSI_ARRIVAL_CMI = 'Mtrl PSI_ARRIVAL_CMI'
    Mtrl_PSI_ARRIVAL_Excel = 'Mtrl PSI_ARRIVAL_Excel'
    Mtrl_PSI_ARRIVAL_Global_RTF = 'Mtrl PSI_ARRIVAL_Global RTF'
    Mtrl_PSI_ARRIVAL_Open_PO = 'Mtrl PSI_ARRIVAL_Open PO'
    Mtrl_PSI_ARRIVAL_RTF = 'Mtrl PSI_ARRIVAL_RTF'
    Mtrl_PSI_ARRIVAL_RTP = 'Mtrl PSI_ARRIVAL_RTP'
    Mtrl_PSI_ARRIVAL_SN = 'Mtrl PSI_ARRIVAL_SN'
    Mtrl_PSI_ARRIVAL_Supply_Plan = 'Mtrl PSI_ARRIVAL_Supply Plan'

    Mtrl_Info_Record_GT_Code = 'Mtrl Info Record_GT Code'
    Mtrl_Info_Record_Valid_From_Week = 'Mtrl Info Record_Valid From Week'
    Mtrl_Info_Record_Valid_To_Week = 'Mtrl Info Record_Valid To Week'
    Mtrl_Info_Record_Info_Price_USD = 'Mtrl Info Record_Info Price USD'
    Mtrl_Info_Record_Price_Unit = 'Mtrl Info Record_Price Unit'

    Global_Quota_Mtrl_W_Portion = 'Global Quota Mtrl W_Portion'
    Plant_Quota_Mtrl_W_Portion = 'Plant Quota Mtrl W_Portion'

    Quota_Anl_Amt = 'Quota Anl_Amt'
    Quota_Anl_Amt_Rate = 'Quota Anl_Amt Rate'
    Quota_Anl_Currency = 'Quota Anl_Currency'
    Quota_Anl_Qty = 'Quota Anl_Qty'
    Quota_Anl_Qty_Rate = 'Quota Anl_Qty Rate'

    Quota_Analysis_Amt = 'Quota Analysis_Amt'
    Quota_Analysis_Amt_Rate = 'Quota Analysis_Amt Rate'
    Quota_Analysis_Currency = 'Quota Analysis_Currency'
    Quota_Analysis_ETC_Amt = 'Quota Analysis_ETC Amt'
    Quota_Analysis_ETC_Amt_Rate = 'Quota Analysis_ETC Amt Rate'
    Quota_Analysis_ETC_Qty = 'Quota Analysis_ETC Qty'
    Quota_Analysis_ETC_Qty_Rate = 'Quota Analysis_ETC Qty Rate'
    Quota_Analysis_Qty = 'Quota Analysis_Qty'
    Quota_Analysis_Qty_Rate = 'Quota Analysis_Qty Rate'
    Quota_Analysis_Vendor_Total_Amt = 'Quota Analysis_Vendor Total Amt'
    Quota_Analysis_Vendor_Total_Qty = 'Quota Analysis_Vendor Total Qty'
    Quota_Analysis_Vendor1_Amt = 'Quota Analysis_Vendor1 Amt'
    Quota_Analysis_Vendor1_Amt_Rate = 'Quota Analysis_Vendor1 Amt Rate'
    Quota_Analysis_Vendor1_Qty = 'Quota Analysis_Vendor1 Qty'
    Quota_Analysis_Vendor1_Qty_Rate = 'Quota Analysis_Vendor1 Qty Rate'
    Quota_Analysis_Vendor2_Amt = 'Quota Analysis_Vendor2 Amt'
    Quota_Analysis_Vendor2_Amt_Rate = 'Quota Analysis_Vendor2 Amt Rate'
    Quota_Analysis_Vendor2_Qty = 'Quota Analysis_Vendor2 Qty'
    Quota_Analysis_Vendor2_Qty_Rate = 'Quota Analysis_Vendor2 Qty Rate'
    Quota_Analysis_Vendor3_Amt = 'Quota Analysis_Vendor3 Amt'
    Quota_Analysis_Vendor3_Amt_Rate = 'Quota Analysis_Vendor3 Amt Rate'
    Quota_Analysis_Vendor3_Qty = 'Quota Analysis_Vendor3 Qty'
    Quota_Analysis_Vendor3_Qty_Rate = 'Quota Analysis_Vendor3 Qty Rate'
    Quota_Analysis_Vendor4_Amt = 'Quota Analysis_Vendor4 Amt'
    Quota_Analysis_Vendor4_Amt_Rate = 'Quota Analysis_Vendor4 Amt Rate'
    Quota_Analysis_Vendor4_Qty = 'Quota Analysis_Vendor4 Qty'
    Quota_Analysis_Vendor4_Qty_Rate = 'Quota Analysis_Vendor4 Qty Rate'
    Quota_Analysis_Vendor5_Amt = 'Quota Analysis_Vendor5 Amt'
    Quota_Analysis_Vendor5_Amt_Rate = 'Quota Analysis_Vendor5 Amt Rate'
    Quota_Analysis_Vendor5_Qty = 'Quota Analysis_Vendor5 Qty'
    Quota_Analysis_Vendor5_Qty_Rate = 'Quota Analysis_Vendor5 Qty Rate'

    Chart_Vendor1 = 'Chart_Vendor1'
    Chart_Vendor2 = 'Chart_Vendor2'
    Chart_Vendor3 = 'Chart_Vendor3'
    Chart_Vendor4 = 'Chart_Vendor4'
    Chart_Vendor5 = 'Chart_Vendor5'
    ETC = '_ETC'
    Quota_Anl_Chart = 'Quota Anl Chart'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) 날짜 데이터 설정을 위한 전처리 → 현재 Sever Error 발생
    ################################################################################################################
    step(300, '=====> STEP 2(End) : Check memory usage & runtime')

    # # df_in_GRMtrl = df_in_GRMtrl.head(0)
    # df_in_DualMtrlAnlMst = df_in_DualMtrlAnlMst.head(0)
    # df_in_MtrlPSI = df_in_MtrlPSI.head(0)
    # df_in_MtrlInfoRecord = df_in_MtrlInfoRecord.head(0)
    # df_in_PlantQuotaMtrlW = df_in_PlantQuotaMtrlW.head(0)


    # Merge를 위하 Columns 명 변경
    rename_dict = {Location_COLUMN: Sub_Location_COLUMN,
                   Sub_Location_COLUMN: Location_COLUMN}  # Location -> Sub Location, Sub Location -> Location
    # df_in_FCSTRFTHistW = df_in_FCSTRFTHistW.rename(columns=rename_dict, errors='raise')

    # 중복 삭제를 위한 Location 정리
    df_in_MtrlPSI[Sub_Location_COLUMN] = df_in_MtrlPSI[Sub_Location_COLUMN].str.split('@').str[0]
    df_in_MtrlPSI[Sub_Location_COLUMN] = df_in_MtrlPSI[Sub_Location_COLUMN].str.split('_').str[0]

    # Input Date 구분
    df_in_GRMtrl["DateFrame_Name"] = 'df_in_GRMtrl'
    # df_in_FCSTRFTHistW["DateFrame_Name"] = 'df_in_FCSTRFTHistW'
    df_in_MtrlPSI["DateFrame_Name"] = 'df_in_MtrlPSI'

    # 기본 테이블 생성을 위한 Grain key 설정 (Version, Location, Item, Sub Location)
    basic_GrainKey = [Version_Name_COLUMN, Location_COLUMN, Sub_Location_COLUMN, Item_Material_COLUMN, "DateFrame_Name"]
    # 중복 삭제 및 기본 데이터 프레임 생성
    df_in_GRMtrl_key = df_in_GRMtrl[basic_GrainKey].drop_duplicates()
    row_count, col_count = df_in_GRMtrl_key.shape
    note(f'====================> df_in_GRMtrl_key rows : {row_count} , Columns : {col_count}')
    # df_in_FCSTRFTHistW_key = df_in_FCSTRFTHistW[basic_GrainKey].drop_duplicates()
    # row_count, col_count = df_in_FCSTRFTHistW_key.shape
    # note(f'====================> df_in_FCSTRFTHistW_key rows : {row_count} , Columns : {col_count}')
    df_in_MtrlPSI_key = df_in_MtrlPSI[basic_GrainKey].drop_duplicates()
    row_count, col_count = df_in_MtrlPSI_key.shape
    note(f'====================> df_in_MtrlPSI_key rows : {row_count} , Columns : {col_count}')

    # 중복 삭제 및 기본 프레임 Concat
    df_out_dataframe_raw_final_temp = pd.concat([df_in_GRMtrl_key,  df_in_MtrlPSI_key],
                                                axis=0).drop_duplicates()
    print_df(df_out_dataframe_raw_final_temp, "df_out_dataframe_raw_final_temp - 중복 삭제 확인")

    # df_in_PlanningMonth[Time_Week_COLUMN] = df_in_PlanningMonth[Time_Week_COLUMN].astype(str)
    # df_in_PlanningMonth 주차 정보 리스트로 만들기
    week_list = df_in_PlanningMonth[Time_Week_COLUMN].to_list()
    # week_list로 확장을 위해 열 만들기
    df_out_dataframe_raw_final_temp[Time_Week_COLUMN] = df_out_dataframe_raw_final_temp.apply(lambda x: week_list,
                                                                                              axis=1)

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -1')
    # Time Week로 확장 하기
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.explode(Time_Week_COLUMN)

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -2')
    # df_in_GRMtrl(실적 Data Merge)

    df_out_dataframe_raw_final_temp[Time_Week_COLUMN] = df_out_dataframe_raw_final_temp[Time_Week_COLUMN].astype(str)
    df_in_GRMtrl[Time_Week_COLUMN] = df_in_GRMtrl[Time_Week_COLUMN].astype(str)
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(
        df_in_GRMtrl.drop(columns=["DateFrame_Name", 'Dummy', GR_Mtrl_Trans_Mode]),
        on=[col for col in basic_GrainKey if col != "DateFrame_Name"] + [Time_Week_COLUMN], how='left')

    # # FSCT 전처리 (정렬 후 중복 제거)
    # df_in_FCSTRFTHistW = df_in_FCSTRFTHistW.sort_values(by=[Week1_COLUMN, To_Time_To_Week_COLUMN, Time_Week_COLUMN],
    #                                                     ascending=[False, False, False]).drop_duplicates(
    #     subset=[Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
    #             "DateFrame_Name"])

    # # df_in_FCSTRFTHistW(FCST Data Merge)
    # df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(
    #     df_in_FCSTRFTHistW[basic_GrainKey + [Time_Week_COLUMN, FCST_RTF_Hist_W_Fcst]].drop(columns=["DateFrame_Name"]),
    #     on=[col for col in basic_GrainKey if col != "DateFrame_Name"] + [Time_Week_COLUMN], how='left')

    # Intransit 실적 정리
    # Arrival Total 을 구하기 위한 Columns 설정
    sum_columns = [Mtrl_PSI_ARRIVAL_CMI, Mtrl_PSI_ARRIVAL_Excel, Mtrl_PSI_ARRIVAL_Global_RTF, Mtrl_PSI_ARRIVAL_Open_PO,
                   Mtrl_PSI_ARRIVAL_RTF, Mtrl_PSI_ARRIVAL_RTP, Mtrl_PSI_ARRIVAL_SN, Mtrl_PSI_ARRIVAL_Supply_Plan]
    # Arrival Total 을 구하기
    df_in_MtrlPSI[Arrival_Total] = df_in_MtrlPSI[sum_columns].sum(axis=1)
    df_in_MtrlPSI = df_in_MtrlPSI.drop(columns=sum_columns + ['Dummy', Trans_Mode_COLUMN], axis=1)

    # df_in_FCSTRFTHistW(df_in_MtrlPSI Data Merge - 이동중인 Data)
    df_out_dataframe_raw_final_temp[Time_Week_COLUMN] = df_out_dataframe_raw_final_temp[Time_Week_COLUMN].astype(str)
    df_in_MtrlPSI[Time_Week_COLUMN] = df_in_MtrlPSI[Time_Week_COLUMN].astype(str)

    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(
        df_in_MtrlPSI.drop(columns='DateFrame_Name'),
        on=[col for col in basic_GrainKey if col != "DateFrame_Name"] + [Time_Week_COLUMN], how='left')

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -3')

    # Group ID Merge
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(
        df_in_DualMtrlAnlMst[[Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, Group_ID_COLUMN]],
        on=[Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN], how='left')

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -4')

    df_out_dataframe_raw_final_temp[Time_Week_COLUMN] = df_out_dataframe_raw_final_temp[Time_Week_COLUMN].astype(str)
    df_in_GlobalQuotaMtrlW[Time_Week_COLUMN] = df_in_GlobalQuotaMtrlW[Time_Week_COLUMN].astype(str)
    df_in_PlantQuotaMtrlW[Time_Week_COLUMN] = df_in_PlantQuotaMtrlW[Time_Week_COLUMN].astype(str)

    # Global Quota W_Protion merge
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(
        df_in_GlobalQuotaMtrlW,
        on=[Version_Name_COLUMN, Time_Week_COLUMN,
            Item_Material_COLUMN,Sub_Location_COLUMN, Group_ID_COLUMN],
        how='left').drop(columns='Dummy', axis=1)

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -5')

    df_in_PlantQuotaMtrlW[Time_Week_COLUMN] = df_in_PlantQuotaMtrlW[Time_Week_COLUMN].astype(str)
    # Plant Quota Mtrl W_Protion merge
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(
        df_in_PlantQuotaMtrlW,
        on=[Version_Name_COLUMN, Time_Week_COLUMN,
            Item_Material_COLUMN,Sub_Location_COLUMN, Group_ID_COLUMN,Location_COLUMN],
        how='left').drop(columns='Dummy', axis=1)

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -6')

    # 주차 확장을 위한 데이터 타입 변환
    df_in_MtrlInfoRecord_temp = df_in_MtrlInfoRecord.copy()
    df_in_MtrlInfoRecord_temp[Mtrl_Info_Record_Valid_To_Week] = df_in_MtrlInfoRecord_temp[
        Mtrl_Info_Record_Valid_To_Week].fillna(0).astype(int)
    df_in_MtrlInfoRecord_temp[Mtrl_Info_Record_Valid_From_Week] = df_in_MtrlInfoRecord_temp[
        Mtrl_Info_Record_Valid_From_Week].fillna(0).astype(int)

    print_df(df_in_MtrlInfoRecord_temp, 'df_in_MtrlInfoRecord_temp -1')

    # Mtrl_Info_Record_GT_Code 설정
    df_in_MtrlInfoRecord_temp[Mtrl_Info_Record_GT_Code] = \
        df_in_MtrlInfoRecord_temp[Mtrl_Info_Record_GT_Code].str.split('@').str[0]
    df_in_MtrlInfoRecord_temp[Mtrl_Info_Record_GT_Code].str.split('_').str[0]
    # Columns 명 변경
    df_in_MtrlInfoRecord_temp.rename(
        columns={Item_COLUMN: Item_Material_COLUMN, Mtrl_Info_Record_GT_Code: Sub_Location_COLUMN}, inplace=True)

    print_df(df_in_MtrlInfoRecord_temp, 'df_in_MtrlInfoRecord_temp -2')

    # df_in_MtrlInfoRecord 정렬 및 중복 삭제
    df_in_MtrlInfoRecord_temp = df_in_MtrlInfoRecord_temp.sort_values(
        by=[Mtrl_Info_Record_Valid_To_Week, Mtrl_Info_Record_Valid_From_Week, Sequence_COLUMN],
        ascending=[False, False, False])
    df_in_MtrlInfoRecord_temp = df_in_MtrlInfoRecord_temp.drop_duplicates(
        subset=[Version_Name_COLUMN, Item_Material_COLUMN, Location_COLUMN, Sub_Location_COLUMN], keep='first')

    df_in_TimeWeeks = df_in_PlanningMonth[[Time_Week_COLUMN]].astype(str)

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -7')

    # 주차 범위를 필터링하기 위한 함수
    def filter_weeks(start, end, timeweek_df):
        return timeweek_df[(timeweek_df[Time_Week_COLUMN] >= start) & (
                timeweek_df[Time_Week_COLUMN] <= end)][Time_Week_COLUMN].tolist()

    # 확장 범위 설정 (2025-08-21 수정)
    df_in_MtrlInfoRecord_temp[Time_Week_COLUMN] = df_in_MtrlInfoRecord_temp.apply(
        lambda x: filter_weeks(x[Mtrl_Info_Record_Valid_From_Week], x[Mtrl_Info_Record_Valid_To_Week],df_in_TimeWeeks)
        if Mtrl_Info_Record_Valid_From_Week in x and Mtrl_Info_Record_Valid_To_Week in x and pd.notnull(
            x[Mtrl_Info_Record_Valid_From_Week]) and pd.notnull(x[Mtrl_Info_Record_Valid_To_Week]) else[], axis=1)

    # df_in_MtrlInfoRecord_temp[Time_Week_COLUMN] = df_in_MtrlInfoRecord_temp.apply(
    #     lambda x: np.arange(x[Mtrl_Info_Record_Valid_From_Week], x[Mtrl_Info_Record_Valid_To_Week] + 1)
    #     if Mtrl_Info_Record_Valid_From_Week in x and Mtrl_Info_Record_Valid_To_Week in x and pd.notnull(
    #         x[Mtrl_Info_Record_Valid_From_Week]) and pd.notnull(x[Mtrl_Info_Record_Valid_To_Week]) else [], axis=1)

    print_df(df_in_MtrlInfoRecord_temp, 'df_in_MtrlInfoRecord_temp -7-1',False)

    df_in_MtrlInfoRecord_temp = df_in_MtrlInfoRecord_temp[
        [Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, Time_Week_COLUMN, Sub_Location_COLUMN,
         Mtrl_Info_Record_Info_Price_USD, Mtrl_Info_Record_Price_Unit]]
    df_in_MtrlInfoRecord_temp['Mtrl Info Record_unitPrice'] = df_in_MtrlInfoRecord_temp[
                                                                  Mtrl_Info_Record_Info_Price_USD] / \
                                                              df_in_MtrlInfoRecord_temp[Mtrl_Info_Record_Price_Unit]

    print_df(df_in_MtrlInfoRecord_temp, 'df_in_MtrlInfoRecord_temp -7-2',False)
    # 주차 확장
    df_in_MtrlInfoRecord_temp = df_in_MtrlInfoRecord_temp.explode(Time_Week_COLUMN)
    # df_in_MtrlInfoRecord_temp 필터

    print_df(df_in_MtrlInfoRecord_temp, 'df_in_MtrlInfoRecord_temp -7-3',False)

    df_in_MtrlInfoRecord_temp[Time_Week_COLUMN] = df_in_MtrlInfoRecord_temp[Time_Week_COLUMN].astype(str)
    # df_out_dataframe_raw_final_temp & df_in_MtrlInfoRecord_temp Merge
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(df_in_MtrlInfoRecord_temp,
                                                                            on=[Version_Name_COLUMN, Location_COLUMN,
                                                                                Sub_Location_COLUMN,
                                                                                Item_Material_COLUMN, Time_Week_COLUMN],
                                                                            how='left')
    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -7-4',False)

    # 빈 단가를 가져 오기 위한 조건
    df_in_MtrlInfoRecord_base = df_in_MtrlInfoRecord_temp[
        [Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
         'Mtrl Info Record_unitPrice']].copy().drop_duplicates().reset_index(drop=True)

    # merge를 위해 columns 명 변경
    df_in_MtrlInfoRecord_base = df_in_MtrlInfoRecord_base.rename(
        columns={'Mtrl Info Record_unitPrice': 'Mtrl Info Record_unitPrice_temp'})


    # 빈 단가 정보를 찾기 위한 merge
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp.merge(df_in_MtrlInfoRecord_base,
                                                                            on=[Version_Name_COLUMN, Location_COLUMN,
                                                                                Item_Material_COLUMN,
                                                                                Sub_Location_COLUMN],
                                                                            how='left')

    print_df(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final_temp -7-5',False)

    # 빈 'Mtrl Info Record_unitPrice' 설정
    df_out_dataframe_raw_final_temp['Mtrl Info Record_unitPrice'] = np.where(
        df_out_dataframe_raw_final_temp['Mtrl Info Record_unitPrice'].isna(),
        df_out_dataframe_raw_final_temp['Mtrl Info Record_unitPrice_temp'],
        df_out_dataframe_raw_final_temp['Mtrl Info Record_unitPrice'])
    # 금액 계산을 위한 NaN 채우기
    df_out_dataframe_raw_final_temp['Mtrl Info Record_unitPrice'] = df_out_dataframe_raw_final_temp[
        'Mtrl Info Record_unitPrice'].fillna(0).astype(float)

    vdCommon.gfn_saveDf(df_out_dataframe_raw_final_temp, "df_out_dataframe_raw_final_temp", True)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4 (1) Global Top 기준 pivot Test
    ###############################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    # df_out_dataframe_raw_final_temp 정리
    df_out_dataframe_raw_final_temp = df_out_dataframe_raw_final_temp[
        [Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
         Group_ID_COLUMN, GR_Mtrl_Qty, GR_Mtrl_Amt, GR_Mtrl_Amt_USD, Arrival_Total,
         'Mtrl Info Record_unitPrice', Global_Quota_Mtrl_W_Portion, Plant_Quota_Mtrl_W_Portion, "DateFrame_Name"]]
    # 계산을 위한 0으로 체우기
    df_out_dataframe_raw_final_temp.fillna(0, inplace=True)

    df_out_dataframe_raw_final_temp["GR_Mtrl_Qty_temp"] = df_out_dataframe_raw_final_temp[Arrival_Total]
    df_out_dataframe_raw_final_temp["GR_Mtrl_Amt_USD_temp"] = df_out_dataframe_raw_final_temp["GR_Mtrl_Qty_temp"] * \
                                                              df_out_dataframe_raw_final_temp[
                                                                  "Mtrl Info Record_unitPrice"]
    df_out_dataframe_raw_final_temp[Quota_Anl_Qty] = df_out_dataframe_raw_final_temp[GR_Mtrl_Qty] + \
                                                     df_out_dataframe_raw_final_temp["GR_Mtrl_Qty_temp"]
    df_out_dataframe_raw_final_temp[Quota_Anl_Amt] = df_out_dataframe_raw_final_temp[GR_Mtrl_Amt_USD] + \
                                                     df_out_dataframe_raw_final_temp["GR_Mtrl_Amt_USD_temp"]

    df_out_dataframe_raw_final_temp[Quota_Anl_Currency] = "USD"

    df_out_dataframe_raw_final_temp[Global_Quota_Mtrl_W_Portion] = df_out_dataframe_raw_final_temp[
        Global_Quota_Mtrl_W_Portion].fillna(0)
    df_out_dataframe_raw_final_temp[Plant_Quota_Mtrl_W_Portion] = df_out_dataframe_raw_final_temp[
        Plant_Quota_Mtrl_W_Portion].fillna(0)

    # 소수점 1 자리로 설정
    df_out_dataframe_raw_final_temp[Quota_Anl_Qty] = (df_out_dataframe_raw_final_temp[Quota_Anl_Qty] * 10) / 10
    df_out_dataframe_raw_final_temp[Quota_Anl_Amt] = (df_out_dataframe_raw_final_temp[Quota_Anl_Amt] * 10) / 10
    df_out_dataframe_raw_final_temp[Global_Quota_Mtrl_W_Portion] = (df_out_dataframe_raw_final_temp[
                                                                        Global_Quota_Mtrl_W_Portion] * 10) / 10
    df_out_dataframe_raw_final_temp[Plant_Quota_Mtrl_W_Portion] = (df_out_dataframe_raw_final_temp[
                                                                       Plant_Quota_Mtrl_W_Portion] * 10) / 10

    # Quota_Anl_Qty_Rate 값 설정 Global_Quota_Mtrl_W_Portion == Plant_Quota_Mtrl_W_Portion, Global_Quota_Mtrl_W_Portion 아니면 Plant_Quota_Mtrl_W_Portion
    df_out_dataframe_raw_final_temp[Quota_Anl_Qty_Rate] = np.where(
        df_out_dataframe_raw_final_temp[Plant_Quota_Mtrl_W_Portion] != 0,
        df_out_dataframe_raw_final_temp[Plant_Quota_Mtrl_W_Portion],
        df_out_dataframe_raw_final_temp[Global_Quota_Mtrl_W_Portion])

    # Quota_Anl_Amt_Rate 값 설정
    df_out_dataframe_raw_final_temp[Quota_Anl_Amt_Rate] = df_out_dataframe_raw_final_temp[Quota_Anl_Qty_Rate].copy()

    df_out_QuotaAnalysis = df_out_dataframe_raw_final_temp.copy()

    print_df(df_out_QuotaAnalysis, 'df_out_QuotaAnalysis___확인', False)

    df_out_QuotaAnalysis.drop(columns='DateFrame_Name', inplace=True)
    df_out_QuotaAnalysis.drop_duplicates(inplace=True)
    df_out_QuotaAnalysis[Quota_Anl_Qty] = df_out_QuotaAnalysis[Quota_Anl_Qty].round(1)
    df_out_QuotaAnalysis[Quota_Anl_Amt] = df_out_QuotaAnalysis[Quota_Anl_Amt].round(1)
    df_out_QuotaAnalysis[Quota_Anl_Qty_Rate] = pd.to_numeric(
        df_out_QuotaAnalysis[Quota_Anl_Qty_Rate], errors='coerce').astype('Float64').round(
        1) if Quota_Anl_Qty_Rate in df_out_QuotaAnalysis.columns else pd.Series(dtype='Float64')
    df_out_QuotaAnalysis[Quota_Anl_Amt_Rate] = pd.to_numeric(
        df_out_QuotaAnalysis[Quota_Anl_Amt_Rate], errors='coerce').astype('Float64').round(
        1) if Quota_Anl_Amt_Rate in df_out_QuotaAnalysis.columns else pd.Series(dtype='Float64')

    df_out_QuotaAnalysis = df_out_QuotaAnalysis[
        [Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
         Group_ID_COLUMN,Quota_Anl_Qty, Quota_Anl_Amt, Quota_Anl_Qty_Rate, Quota_Anl_Amt_Rate, Quota_Anl_Currency]]

    df_out_QuotaAnalysis = df_out_QuotaAnalysis[
        (df_out_QuotaAnalysis[Quota_Anl_Qty] > 0) | (df_out_QuotaAnalysis[Quota_Anl_Amt] > 0)]

    df_out_QuotaAnalysis = df_out_QuotaAnalysis[df_out_QuotaAnalysis[Group_ID_COLUMN] != 0]

    df_out_QuotaAnalysis.reset_index(drop=True, inplace=True)

    QuotaAnalysis_cols = {
        Version_Name_COLUMN:  'object', Location_COLUMN: 'object',  Time_Week_COLUMN: 'object',
        Item_Material_COLUMN: 'object', Sub_Location_COLUMN: 'object', Group_ID_COLUMN: 'object',
        Quota_Anl_Amt  : 'Float64', Quota_Anl_Amt_Rate : 'Float64',
        Quota_Anl_Currency : 'Float64', Quota_Anl_Qty_Rate : 'Float64'}

    if df_out_QuotaAnalysis.empty:
        df_out_QuotaAnalysis = df_out_QuotaAnalysis.reindex(
            columns = QuotaAnalysis_cols.keys())
        for c, t in QuotaAnalysis_cols.items():
            df_out_QuotaAnalysis[c] = pd.Series(index=df_out_QuotaAnalysis.index, dtype = t)

    print_df(df_out_QuotaAnalysis, "df_out_QuotaAnalysis_최종확인", True)
    print_df(df_out_dataframe_raw_final_temp, "df_out_dataframe_raw_final_temp", True)
    # print_df(df_out_QuotaAnalysis, 'df_out_QuotaAnalysis')
    # save_csv_file(df_out_dataframe_raw_final_temp, 'df_out_dataframe_raw_final')
    step(400, '=====> STEP 4(End) : Check memory usage & runtime')


    # ################################################################################################################
    # # Step 5 (1) Global Top 기준 pivot Test
    # ###############################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    # 데이터 프레임 복사
    df_out_QuotaAnalysisChart = df_out_dataframe_raw_final_temp.copy()
    df_out_QuotaAnalysisChart.drop(columns='DateFrame_Name', inplace=True)
    df_out_QuotaAnalysisChart.drop_duplicates(inplace=True)

    df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart[
        (df_out_QuotaAnalysisChart[Quota_Anl_Qty] > 0) | (df_out_QuotaAnalysisChart[Quota_Anl_Amt] > 0)]

    df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart[df_out_QuotaAnalysisChart[Group_ID_COLUMN] != 0]
    # TOP List 설정
    Global_TOP_list = ['G2698624', 'G2902355', 'G1115625', 'G6088657']
    # TOP List 설정 와 Sub Location 과 Sub_Location_COLUMN 비교
    df_out_QuotaAnalysisChart['Global_TOP_List_COLUMN'] = df_out_QuotaAnalysisChart[Sub_Location_COLUMN].apply(
        lambda x: f"_Quota Analysis_Vendor{Global_TOP_list.index(x) + 1}" if x in Global_TOP_list else ETC)
    # Planning_Month_dict month 와 Week dict 생성
    df_in_PlanningMonth[Time_Week_COLUMN] = df_in_PlanningMonth[Time_Week_COLUMN].astype(str)
    Planning_Month_dict = dict(
        zip(df_in_PlanningMonth[Time_Week_COLUMN], df_in_PlanningMonth[Time_Planning_Month_COLUMN]))
    note(f"=================>Planning_Month_dict : {Planning_Month_dict} ========>")
    # week 정보를 month로 변경
    df_out_QuotaAnalysisChart[Time_Planning_Month_COLUMN] = df_out_QuotaAnalysisChart[Time_Week_COLUMN].map(
        Planning_Month_dict)
    # Time_Planning_Month_COLUMN 데이터 타입 변경
    df_out_QuotaAnalysisChart[Time_Planning_Month_COLUMN] = pd.to_numeric(
        df_out_QuotaAnalysisChart[Time_Planning_Month_COLUMN], errors='coerce')

    print_df(df_out_QuotaAnalysisChart, 'df_out_QuotaAnalysisChart')
    note(f" =======================> df_out_QuotaAnalysisChart columns : {df_out_QuotaAnalysisChart.columns}")
    note(f" =======================> Global_TOP_List_COLUMN unique : {df_out_QuotaAnalysisChart['Global_TOP_List_COLUMN'].unique()}")

    # # 월별 전체 수량 및 금액 합계 계산 (비중 계산을 위해)
    # monthly_totals = df_out_QuotaAnalysisChart.groupby(
    #     [Version_Name_COLUMN,Location_COLUMN,Time_Planning_Month_COLUMN])[
    #     [Quota_Anl_Amt, Quota_Anl_Qty]].sum().rename(
    #     columns={Quota_Anl_Amt : 'Quota_Anl_Amt_total', Quota_Anl_Qty:'Quota_Anl_Qty_total'}).reset_index()
    #
    # df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart.merge(monthly_totals, on = [
    #     Version_Name_COLUMN, Location_COLUMN, Time_Planning_Month_COLUMN])
    #
    # df_out_QuotaAnalysisChart[Quota_Anl_Qty_Rate] = df_out_QuotaAnalysisChart[Quota_Anl_Qty] / \
    #                                                 df_out_QuotaAnalysisChart['Quota_Anl_Qty_total'] * 100
    #
    # df_out_QuotaAnalysisChart[Quota_Anl_Amt_Rate] = df_out_QuotaAnalysisChart[Quota_Anl_Amt] / \
    #                                                 df_out_QuotaAnalysisChart['Quota_Anl_Amt_total'] * 100

    vdCommon.gfn_saveDf(df_out_QuotaAnalysisChart, "df_out_QuotaAnalysisChart - 임시 1", True)

    idx = [Version_Name_COLUMN, Location_COLUMN, Time_Planning_Month_COLUMN, Item_Material_COLUMN,
               Sub_Location_COLUMN, Group_ID_COLUMN]
    col = 'Global_TOP_List_COLUMN'
    val = [Quota_Anl_Amt, Quota_Anl_Qty, Quota_Anl_Qty_Rate, Quota_Anl_Amt_Rate]
    note(f" =======================> Step 확인........1")

    need_cols = []
    for x in [idx, col,val]:
        if isinstance(x, (list, tuple)):
            need_cols.extend(x)
        else:
            need_cols.append(x)

    missing = [col for col in need_cols if col not in df_out_QuotaAnalysisChart.columns]

    if df_out_QuotaAnalysisChart.empty or missing:
        df_out_QuotaAnalysisChart = pd.DataFrame(columns=idx)
    else:
        df_out_QuotaAnalysisChart = (
            df_out_QuotaAnalysisChart.pivot_table(index = idx, columns = col, values = val,
                                                  aggfunc={Quota_Anl_Amt : 'sum', Quota_Anl_Qty : 'sum',
                                                           Quota_Anl_Qty_Rate : 'max',
                                                           Quota_Anl_Amt_Rate : 'max' }, margins = True))

    note(f" =======================> Step 확인........2")

    # df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart.pivot_table(
    #     index=[Version_Name_COLUMN, Location_COLUMN, Time_Planning_Month_COLUMN, Item_Material_COLUMN,
    #            Sub_Location_COLUMN, Group_ID_COLUMN],
    #     columns='Global_TOP_List_COLUMN',
    #     values=[Quota_Anl_Amt, Quota_Anl_Qty, Quota_Anl_Qty_Rate, Quota_Anl_Amt_Rate],
    #     aggfunc={Quota_Anl_Amt : 'sum', Quota_Anl_Qty : 'sum',Quota_Anl_Qty_Rate : 'max', Quota_Anl_Amt_Rate : 'max' },
    #     margins=True)

    df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart.reset_index()

    print_df(df_out_QuotaAnalysisChart, "df_out_QuotaAnalysisChart - 임시 2")

    # vdCommon.gfn_saveDf(df_out_QuotaAnalysisChart, "df_out_QuotaAnalysisChart - 임시 2", True)

    if isinstance(df_out_QuotaAnalysisChart.columns, pd.MultiIndex):
        df_out_QuotaAnalysisChart.columns = [
            str(a) if (b is None or str(b).strip() =="") else f"{a}_{b}"
            for (a,b) in df_out_QuotaAnalysisChart.columns.to_list()
        ]
    else:
        df_out_QuotaAnalysisChart.columns = df_out_QuotaAnalysisChart.columns.astype(str)


    print_df(df_out_QuotaAnalysisChart, "df_out_QuotaAnalysisChart - 임시 3")


    rename_col = {'Quota Anl_Amt_Quota Analysis_Vendor1': Quota_Analysis_Vendor1_Amt,
                  'Quota Anl_Amt_Quota Analysis_Vendor2': Quota_Analysis_Vendor2_Amt,
                  'Quota Anl_Amt_Quota Analysis_Vendor3': Quota_Analysis_Vendor3_Amt,
                  'Quota Anl_Amt_Quota Analysis_Vendor4': Quota_Analysis_Vendor4_Amt,
                  'Quota Anl_AmtAll': Quota_Analysis_Amt, 'Quota Anl_Amt_ETC': Quota_Analysis_ETC_Amt,
                  'Quota Anl_Amt Rate_ETC': Quota_Analysis_ETC_Amt_Rate,
                  'Quota Anl_Amt Rate_Quota Analysis_Vendor1': Quota_Analysis_Vendor1_Amt_Rate,
                  'Quota Anl_Amt Rate_Quota Analysis_Vendor2': Quota_Analysis_Vendor2_Amt_Rate,
                  'Quota Anl_Amt Rate_Quota Analysis_Vendor3': Quota_Analysis_Vendor3_Amt_Rate,
                  'Quota Anl_Amt Rate_Quota Analysis_Vendor4': Quota_Analysis_Vendor4_Amt_Rate,
                  'Quota Anl_Amt RateAll': Quota_Analysis_ETC_Amt_Rate, 'Quota Anl_Qty_ETC': Quota_Analysis_ETC_Qty,
                  'Quota Anl_Qty_Quota Analysis_Vendor1': Quota_Analysis_Vendor1_Qty,
                  'Quota Anl_Qty_Quota Analysis_Vendor2': Quota_Analysis_Vendor2_Qty,
                  'Quota Anl_Qty_Quota Analysis_Vendor3': Quota_Analysis_Vendor3_Qty,
                  'Quota Anl_Qty_Quota Analysis_Vendor4': Quota_Analysis_Vendor4_Qty,
                  'Quota Anl_QtyAll': Quota_Analysis_Qty, 'Quota Anl_Qty Rate_ETC': Quota_Analysis_ETC_Qty_Rate,
                  'Quota Anl_Qty Rate_Quota Analysis_Vendor1': Quota_Analysis_Vendor1_Qty_Rate,
                  'Quota Anl_Qty Rate_Quota Analysis_Vendor2': Quota_Analysis_Vendor2_Qty_Rate,
                  'Quota Anl_Qty Rate_Quota Analysis_Vendor3': Quota_Analysis_Vendor3_Qty_Rate,
                  'Quota Anl_Qty Rate_Quota Analysis_Vendor4': Quota_Analysis_Vendor4_Qty_Rate,
                  'Quota Anl_Qty RateAll': Quota_Analysis_Qty_Rate
                  }

    existing_columns = df_out_QuotaAnalysisChart.columns
    filtered_rename_col = {k : v for k, v in rename_col.items() if k in existing_columns}

    note(f"=========================> {filtered_rename_col}")
    note(f"=========================> {existing_columns}")

    df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart.rename(columns=filtered_rename_col)

    print_df(df_out_QuotaAnalysisChart, "df_out_QuotaAnalysisChart - 임시 4")

    for col in filtered_rename_col.values():
        if "Rate" in col:
            df_out_QuotaAnalysisChart[col] = df_out_QuotaAnalysisChart[col].fillna(0).round(1)

    # df_out_QuotaAnalysisChart[Quota_Analysis_ETC_Amt_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_ETC_Amt_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor1_Amt_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor1_Amt_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor2_Amt_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor2_Amt_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor3_Amt_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor3_Amt_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor4_Amt_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor4_Amt_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_ETC_Amt_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_ETC_Amt_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor1_Qty_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor1_Qty_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor2_Qty_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor2_Qty_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor3_Qty_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor3_Qty_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Vendor4_Qty_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Vendor4_Qty_Rate].round(1)
    # df_out_QuotaAnalysisChart[Quota_Analysis_Qty_Rate] = df_out_QuotaAnalysisChart[
    #     Quota_Analysis_Qty_Rate].round(1)

    df_out_QuotaAnalysisChart.fillna(0, inplace=True)

    for col in df_out_QuotaAnalysisChart.columns:
        if col.endswith('Qty'):
            df_out_QuotaAnalysisChart[col] = df_out_QuotaAnalysisChart[col].fillna(0).astype(int)

    for col in df_out_QuotaAnalysisChart.columns:
        if col.endswith('Amt'):
            df_out_QuotaAnalysisChart[col] = df_out_QuotaAnalysisChart[col].fillna(0)

    # df_out_QuotaAnalysisChart.drop_duplicates(keep='first', inplace=True)

    df_out_QuotaAnalysisChart[Quota_Analysis_Currency] = 'USD'

    df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart[df_out_QuotaAnalysisChart[Group_ID_COLUMN] != 0]
    df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart[df_out_QuotaAnalysisChart[Version_Name_COLUMN] != "All"]

    QuotaAnalysisChart_cols = {
        Version_Name_COLUMN : 'object' , Location_COLUMN : 'object' , Time_Planning_Month_COLUMN: 'object' ,
        Item_Material_COLUMN : 'object' , Sub_Location_COLUMN : 'object' , Group_ID_COLUMN : 'object' ,
        Quota_Analysis_Amt : 'Float64' , Quota_Analysis_Amt_Rate : 'Float64' , Quota_Analysis_Currency : 'object' ,
        Quota_Analysis_ETC_Amt : 'Float64', Quota_Analysis_ETC_Amt_Rate : 'Float64', Quota_Analysis_ETC_Qty : 'Float64',
        Quota_Analysis_ETC_Qty_Rate : 'Float64', Quota_Analysis_Qty_Rate : 'Float64',
        Quota_Analysis_Vendor_Total_Amt : 'Float64', Quota_Analysis_Vendor_Total_Qty : 'Float64',
        Quota_Analysis_Vendor1_Amt : 'Float64' , Quota_Analysis_Vendor1_Amt_Rate : 'Float64',
        Quota_Analysis_Vendor1_Qty : 'Float64' , Quota_Analysis_Vendor1_Qty_Rate : 'Float64',
        Quota_Analysis_Vendor2_Amt: 'Float64'  , Quota_Analysis_Vendor2_Amt_Rate: 'Float64',
        Quota_Analysis_Vendor2_Qty: 'Float64'  , Quota_Analysis_Vendor2_Qty_Rate: 'Float64',
        Quota_Analysis_Vendor3_Amt: 'Float64'  , Quota_Analysis_Vendor3_Amt_Rate: 'Float64',
        Quota_Analysis_Vendor3_Qty: 'Float64'  , Quota_Analysis_Vendor3_Qty_Rate: 'Float64',
        Quota_Analysis_Vendor4_Amt: 'Float64'  , Quota_Analysis_Vendor4_Amt_Rate: 'Float64',
        Quota_Analysis_Vendor4_Qty: 'Float64'  , Quota_Analysis_Vendor4_Qty_Rate: 'Float64',
        Quota_Analysis_Vendor5_Amt: 'Float64'  , Quota_Analysis_Vendor5_Amt_Rate: 'Float64',
        Quota_Analysis_Vendor5_Qty: 'Float64'  , Quota_Analysis_Vendor5_Qty_Rate: 'Float64'}

    if df_out_QuotaAnalysisChart.empty:
        df_out_QuotaAnalysisChart = df_out_QuotaAnalysisChart.reindex(
            columns = QuotaAnalysisChart_cols.keys())
        for c, t in QuotaAnalysisChart_cols.items():
            df_out_QuotaAnalysisChart[c] = pd.Series(index=df_out_QuotaAnalysisChart.index, dtype = t)

    print_df(df_out_QuotaAnalysisChart, "df_out_QuotaAnalysisChart", True)
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

    # ################################################################################################################
    # # Step 9. (1) 최종 Out_Put Save
    # ################################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')

    row_count, col_count = df_out_QuotaAnalysis.shape
    note(f'=====> Final df_out_QuotaAnalysis rows : {row_count} , Columns : {col_count}')

    row_count, col_count = df_out_QuotaAnalysisChart.shape
    note(f'=====> Final df_out_QuotaAnalysisChart rows : {row_count} , Columns : {col_count}')


    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_QuotaAnalysis, 'df_out_QuotaAnalysis')
        save_csv_file(df_out_QuotaAnalysisChart, 'df_out_QuotaAnalysisChart')


    step(600, '=====> STEP 8(End) : Check memory usage & runtime')

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
