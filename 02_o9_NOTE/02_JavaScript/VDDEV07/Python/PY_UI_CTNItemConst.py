

"""

* 프로그램명
    - PY_UI_CTNItemConst

* 내용
    - 현재는 확정생산계획만 대상(생산라인)

    - 2025.05.19  수정


* 변경이력
- 2025.05.08 / ybest7.park (박병훈) / Create
- 2025.05.19 / ys5236.kang(강유숙) / 수정
- 2025.11.11 / ys5236.kang / applyCheck() 추가함.

* Flow Summary

* Input Table
   - df_in_BODItem = Select ([Version].[Version Name]* [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Sub Location].[Sub Location GC] *[Sub Location].[Sub Location Rep AP2]* [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Asn], Measure.[Dummy]}) on column Where {Measure.[BOD Item_asn] >-1} ;
   - df_in_PLCMfg =  Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[PLC Mfg_EOP Cur Date], Measure.[Dummy]}) on column;
   - df_in_CurrentDay = Select (&CurrentDay);
   - df_in_CTNItemConst = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Apply Flag], Measure.[CTN Item Const_Created By], Measure.[CTN Item Const_Creation Time], Measure.[CTN Item Const_DP Qty from W0], Measure.[CTN Item Const_EOH at PSI], Measure.[CTN Item Const_End Week], Measure.[CTN Item Const_Frozen SOP DP Diff Qty], Measure.[CTN Item Const_Frozen SOP Diff Qty], Measure.[CTN Item Const_Frozen SOP Override Qty], Measure.[CTN Item Const_Frozen SOP Override Reason], Measure.[CTN Item Const_Frozen SOP Override Remain Qty], Measure.[CTN Item Const_Frozen SOP Qty], Measure.[CTN Item Const_Frozen Week], Measure.[CTN Item Const_Prod Result Qty before W0], Measure.[CTN Item Const_Start Week], Measure.[CTN Item Const_Update Time], Measure.[CTN Item Const_Updated By], Measure.[Dummy]}) on column;
   - df_in_SalesPlanAP2 = Select ([Version].[Version Name] *[Item].[Item] * [Time].[Week] * [Location].[Location] *  [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales Plan AP2_Shipment], Measure.[Sales Plan AP2_Dmd], Measure.[Sales Plan AP2_Short], Measure.[Sales Plan AP2_EOH], Measure.[Dummy]}) on column;
   - df_in_SalesActualAP2 = Select ([Item].[Item] * [Time].[Week] * [Location].[Location] * [Version].[Version Name] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales Actual AP2_Prod], Measure.[Dummy]}) on column;
   - df_in_TimeWeek = select ([Time].[Day] * [Time].[Week] );

* 데이터 삭제
    DELETE DATA FOR MODEL [CTN Item Const] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_CTNItemConst
    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    EXEC plugin instance [PY_UI_CTNItemConst] for measures {[CTN Item Const_End Week]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


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

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_CTNItemConst'
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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 수정 : 2025-05-19 (by Kang)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def convert_date_format(date_str):
        if pd.isna(date_str) or str(date_str).lower() == 'nan' or date_str == '':
            return None

        if isinstance(date_str, float) and date_str.is_integer():
            date_str = str(int(date_str))

        if not isinstance(date_str, str):
            date_str = str(date_str)

        date_str = date_str.replace('/', '-').replace('.','-')

        date_formats = [
            '%Y-%m-%d',  # 2025-03-24
            '%Y%m%d',   # 20250324
            '%m/%d/%Y', # 03/24/2025
            '%m-%d-%Y', # 03-24-2025
            '%m-%d-%Y %H:%M:%S' ,  #03-24-2025 12:00:00
            '%m/%d/%Y %I:%M:%S %p', #03/24/2025 00:00:00 PM
            '%m/%d/%Y %H:%M:%S %p',  # 03/24/2025 00:00:00 PM
        ]
        for fmt in date_formats:
            try:
                return pd.to_datetime(date_str, format = fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        try:
            return pd.to_datetime(date_str, errors='coerce').strftime('%Y-%m-%d')
        except Exception:
            return date_str

def applyCheck(row):
    timeDay = row[Time_Day_COLUMN]
    eopCurDate = row[PLC_Mfg_EOP_Cur_Date]
    dayGap = (timeDay - eopCurDate).days
    if(row[CTN_Item_Const_Apply_Flag] ==  "N"):
        return "N"
    else:
        if((row[PLC_Mfg_EOP_Cur_Date] != None) & (dayGap > 90)):
            return "Out of Date"
        else:
            return "Y"


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
    # PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # 2025-05-16 BOD ITEM 추가함.
        df_in_BODItem = read_csv_file('df_in_BODItem_250516')
        df_in_PLCMfg = read_csv_file('df_in_PLCMfg_250516')
        df_in_SalesPlanAP2 = read_csv_file('df_in_SalesPlanAP2_250516')
        df_in_SalesActualAP2 = read_csv_file('df_in_SalesActualAP2_250516')
        df_in_CurrentDay = read_csv_file('df_in_CurrentDay_250516')
        # 2025.05.19 주차 변환을 위해 데이타가 필요함.
        df_in_TimeWeek = read_csv_file('df_in_TimeWeek_250516')
        df_in_CTNItemConst = read_csv_file('df_in_CTNItemConst_20250520')

    # if df_in_BODStructure.empty:
    #     raise Exception("Exception: df_in_BODStructure is empty")
    #
    # if df_in_SiteAP2Map.empty:
    #     raise Exception("Exception: df_in_SiteAP2Map is empty")
    #
    # if df_in_MultiSite.empty:
    #     raise Exception("Exception: df_in_MultiSite is empty")

    # note(f'=====> paramOutVersion : {paramOutVersion}')


    print_df(df_in_PLCMfg, 'df_in_PLCMfg',True)
    print_df(df_in_SalesPlanAP2, 'df_in_SalesPlanAP2',True)
    print_df(df_in_SalesActualAP2, 'df_in_SalesActualAP2',True)
    print_df(df_in_CurrentDay, 'df_in_CurrentDay',True)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 2025.05.19 Loction, ITem에 해당되는 AP2데이타 조회
    print_df(df_in_BODItem, 'df_in_BODItem',True)
    # 2025.05.19 주차 변환을 위해 데이타가 필요함.
    print_df(df_in_TimeWeek, 'df_in_TimeWeek',True)
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    print_df(df_in_CTNItemConst, 'df_in_CTNItemConst',True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    GroupID_COLUM = 'Group.[Group ID]'
    Sequence_COLUMN = 'Sequence.[Sequence]'
    Item_COLUMN = 'Item.[Item]'
    Item_Project_COLUMN = 'Item.[Project]'
    Item_Product_GROUP_COLUMN = 'Item.[Product Group]'
    Item_Year_COLUMN = 'Item.[Year]'
    Item_Inch_COLUM = 'Item.[Inch]'
    Item_Series_COLUM = 'Item.[Series]'
    Time_Week_COLUMN = 'Time.[Week]'
    Time_Day_COLUMN = 'Time.[Day]'
    Sales_Domain_AP2_COLUMN = 'Sales Domain.[AP2]'
    Sales_Domain_GC_COLUMN = 'Sales Domain.[GC]'
    Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
    Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
    Location_COLUMN = 'Location.[Location]'
    Sub_Location_GC_COLUMN = 'Sub Location.[Sub Location GC]'
    note(f"========================================={Sub_Location_GC_COLUMN}")
    Sub_Location_Rep_AP2_COLUMN = 'Sub Location.[Sub Location Rep AP2]'
    note(f"========================================={Sub_Location_Rep_AP2_COLUMN}")

    Key_on = 'key_on'

    CTN_Grp_Const_From_Site = 'CTN Grp Const_From Site'
    CTN_Grp_Const_From_Site_ID = 'CTN Grp Const_From Site ID'
    CTN_Grp_Const_Product_Grp = 'CTN Grp Const_Product Grp'
    CTN_Grp_Const_Project = 'CTN Grp Const_Project'
    CTN_Grp_Const_Series = 'CTN Grp Const_Series'
    CTN_Grp_Const_Inch = 'CTN Grp Const_Inch'
    CTN_Grp_Const_Year = 'CTN Grp Const_Year'
    CTN_Grp_Const_Item = 'CTN Grp Const_Item'
    CTN_Grp_Const_Frozen_Week = 'CTN Grp Const_Frozen Week'
    CTN_Grp_Const_Start_Week = 'CTN Grp Const_Start Week'
    CTN_Grp_Const_AP2 = 'CTN Grp Const_AP2'
    CTN_Grp_Const_AP2_ID = 'CTN Grp Const_AP2 ID'
    CTN_Grp_Const_GC_ID = 'CTN Grp Const_GC ID'
    CTN_Grp_Const_Apply_Flag = 'CTN Grp Const_Apply Flag'
    CTN_Grp_Const_End_Week = 'CTN Grp Const_End Week'
    CTN_Grp_Const_Frozen_SOP_Qty = 'CTN Grp Const_Frozen SOP Qty'
    CTN_Grp_Const_Prod_Result_Qty_before_W0 = 'CTN Grp Const_Prod Result Qty before W0'
    CTN_Grp_Const_DP_Qty_from_W0 = 'CTN Grp Const_DP Qty from W0'
    CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty = 'CTN Grp Const_Frozen SOP DP Diff Qty'
    CTN_Grp_Const_EOH_at_PSI = 'CTN Grp Const_EOH at PSI'
    CTN_Grp_Const_Except_Item = 'CTN Grp Const_Except Item'
    CTN_Grp_Const_Ecp_Start_Week = 'CTN Grp Const Ecp_Start Week'
    CTN_Grp_Const_ECP_Flag = 'CTN Grp Const_ECP Flag'
    CTN_Grp_Const_Ecp_Total_SOP_Qty_from_W0 = 'CTN Grp Const Ecp_Total SOP Qty from W0'
    CTN_Grp_Const_Ecp_Total_SOP_DP_Diff_Qty = 'CTN Grp Const Ecp_Total SOP DP Diff Qty'
    CTN_Grp_Const_Ecp_Prod_Result_Qty_before_W0 = 'CTN Grp Const Ecp_Prod Result Qty before W0'
    CTN_Grp_Const_Ecp_DP_Qty_from_W0 = 'CTN Grp Const Ecp_DP Qty from W0'
    CTN_Grp_Const_Ecp_EOH_at_PSI = 'CTN Grp Const Ecp_EOH at PSI'
    CTN_Grp_Const_Insert_Flag = 'CTN Grp Const_Insert Flag'

    PLC_Mfg_EOP_Cur_Date = 'PLC Mfg_EOP Cur Date'

    Sales_Plan_AP2_Shipment = 'Sales Plan AP2_Shipment'
    Sales_Plan_AP2_Dmd = 'Sales Plan AP2_Dmd'
    Sales_Plan_AP2_Short = 'Sales Plan AP2_Short'
    Sales_Plan_AP2_EOH = 'Sales Plan AP2_EOH'

    Sales_Actual_AP2_Prod = 'Sales Actual AP2_Prod'

    CTN_Item_Const_Apply_Flag = 'CTN Item Const_Apply Flag'
    CTN_Item_Const_Created_By = 'CTN Item Const_Created By'
    CTN_Item_Const_Creation_Time = 'CTN Item Const_Creation Time'
    CTN_Item_Const_DP_Qty_from_W0 = 'CTN Item Const_DP Qty from W0'
    CTN_Item_Const_EOH_at_PSI = 'CTN Item Const_EOH at PSI'
    CTN_Item_Const_End_Week = 'CTN Item Const_End Week'
    CTN_Grp_Const_Ecp_End_Week = 'CTN Grp Const Ecp_End Week'
    CTN_Item_Const_Frozen_SOP_DP_Diff_Qty = 'CTN Item Const_Frozen SOP DP Diff Qty'
    CTN_Item_Const_Frozen_SOP_Diff_Qty = 'CTN Item Const_Frozen SOP Diff Qty'
    CTN_Item_Const_Frozen_SOP_Override_Qty = 'CTN Item Const_Frozen SOP Override Qty'
    CTN_Item_Const_Frozen_SOP_Override_Reason = 'CTN Item Const_Frozen SOP Override Reason'
    CTN_Item_Const_Frozen_SOP_Override_Remain_Qty = 'CTN Item Const_Frozen SOP Override Remain Qty'
    CTN_Item_Const_Frozen_SOP_Qty = 'CTN Item Const_Frozen SOP Qty'
    CTN_Item_Const_Frozen_Week = 'CTN Item Const_Frozen Week'
    CTN_Item_Const_Prod_Result_Qty_before_W0 = 'CTN Item Const_Prod Result Qty before W0'
    CTN_Item_Const_Start_Week = 'CTN Item Const_Start Week'
    CTN_Item_Const_Update_Time = 'CTN Item Const_Update Time'
    CTN_Item_Const_Updated_By = 'CTN Item Const_Updated By'


    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) 날짜 데이터 설정을 위한 전처리 → 현재 Sever Error 발생
    ################################################################################################################
    step(300, '=====> STEP 2(End) : Check memory usage & runtime')

    # merge를 위한 데이터 타입 변경
    str_data_frame = [df_in_CTNItemConst, df_in_SalesPlanAP2, df_in_SalesActualAP2]
    for df in str_data_frame:
        df[Sales_Domain_AP2_COLUMN] = df[Sales_Domain_AP2_COLUMN].astype(str)

    # # 데이터 프레임 Merge
    # df_in_CTNItemConst_temp = df_in_CTNItemConst.drop(
    #     columns='Dummy', axis=1).merge(df_in_PLCMfg,
    #                                    on=[Version_COLUMN, Item_COLUMN,Location_COLUMN],
    #                                    how='left').drop(columns='Dummy',axis=1)
    #
    # df_in_CTNItemConst_temp = df_in_CTNItemConst_temp.merge(df_in_SalesPlanAP2,
    #                                                         on=[Version_COLUMN, Location_COLUMN, Item_COLUMN,
    #                                                             Sales_Domain_AP2_COLUMN], how='left')
    #
    # df_in_CTNItemConst_temp = df_in_CTNItemConst_temp.drop(
    #     columns=[Time_Week_COLUMN, Sub_Location_COLUMN, Trans_Mode_COLUMN], axis=1)
    # df_in_CTNItemConst_temp = df_in_CTNItemConst_temp.merge(df_in_SalesActualAP2,
    #                                                         on=[Version_COLUMN, Location_COLUMN, Item_COLUMN,
    #                                                             Sales_Domain_AP2_COLUMN], how='left')
    # df_in_CurrentDay[Key_on] = 1
    # df_in_CTNItemConst_temp[Key_on] = 1
    # df_in_CTNItemConst_temp = df_in_CTNItemConst_temp.merge(df_in_CurrentDay, on=Key_on, how='left')

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # df_in_CTNItemConst 데이타에서 <Sales Domain AP2> All에 해당되는 AP2 데이타를 BOD ITEM에서 찾는다.
    # 수정 2025-05-19 (by Kang)
    # df_in_TimeWeek 데이타프레임 컬럼 정리 ,형변환 후 to_dict
    df_in_TimeWeek = df_in_TimeWeek[[Time_Day_COLUMN, Time_Week_COLUMN]].drop_duplicates()
    df_in_TimeWeek[Time_Week_COLUMN] = df_in_TimeWeek[Time_Week_COLUMN].astype(str)
    weed_dict = df_in_TimeWeek.set_index(Time_Day_COLUMN)[Time_Week_COLUMN].to_dict()
    # df_in_CTNItemConst 데이타프레임 필요없는 컬럼 drop
    drop_cololum_list=['Dummy', CTN_Item_Const_Frozen_SOP_Qty,CTN_Item_Const_DP_Qty_from_W0,
                       CTN_Item_Const_Frozen_SOP_DP_Diff_Qty,CTN_Item_Const_EOH_at_PSI,
                       CTN_Item_Const_Prod_Result_Qty_before_W0]
    df_in_CTNItemConst = df_in_CTNItemConst.drop(columns=drop_cololum_list, axis=1)
    # (1) df_in_PLCMfg 데이터 프레임 Merge
    # Measure.[CTN Item Const_End Week] <= df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date]
    df_in_CTNItemConst_temp = df_in_CTNItemConst.merge(df_in_PLCMfg,
                                       on=[Version_COLUMN, Item_COLUMN,Location_COLUMN],
                                       how='left').drop(columns='Dummy',axis=1)
    df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date] = df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date].apply(convert_date_format)
    df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date] = pd.to_datetime(df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date],
                                                                   format='%Y-%m-%d', errors='coerce')
    # 딕션어리 주차를 가지고 CTN_Grp_Const_End_Week 생성
    df_in_CTNItemConst_temp[CTN_Item_Const_End_Week] = df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date].astype(str).map(weed_dict).fillna('-').astype(str)

    step(300, '=====> STEP(END) df_in_CTNItemConst_temp(PLCMfg)')
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # df_in_SalesPlanAP2 AP2가 All인 합계 와 AP2 코드별 합계
    # (1) df_in_BODItem DataFrame ::: MF Loction에 해당되는 AP2 데이타 조회
    df_BODItem_AP2 = df_in_BODItem[[Version_COLUMN, Location_COLUMN, Item_COLUMN, Sub_Location_Rep_AP2_COLUMN]].drop_duplicates()
    #df_in_SalesPlanAP2.rename(columns={Location_COLUMN: Location_COLUMN + '_DC', Sub_Location_COLUMN: Location_COLUMN}, inplace=True)
    # (2) df_in_SalesPlanAP2 집게을 위한 [CTN Item Const] 데이타를 조회함.
    ctn_Itemconst_key =[Version_COLUMN, Location_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, CTN_Item_Const_Start_Week]
    df_CTNItemConst_key = df_in_CTNItemConst[ctn_Itemconst_key].drop_duplicates()

    df_CTNItemConst_key_All = df_CTNItemConst_key[df_CTNItemConst_key[Sales_Domain_AP2_COLUMN] == "All"]
    df_CTNItemConst_key_All = pd.merge(df_CTNItemConst_key_All, df_BODItem_AP2,
                                       on=[Version_COLUMN, Location_COLUMN, Item_COLUMN], how="inner")
    df_CTNItemConst_key_AP2 = df_CTNItemConst_key[df_CTNItemConst_key[Sales_Domain_AP2_COLUMN] != "All"]
    df_CTNItemConst_key_AP2[Sub_Location_Rep_AP2_COLUMN] = df_CTNItemConst_key_AP2[Sales_Domain_AP2_COLUMN]

    step(300, '=====> STEP(END) df_CTNItemConst_key_AP2')
    df_CTNItemConst_key = pd.concat([df_CTNItemConst_key_All, df_CTNItemConst_key_AP2], ignore_index=True)

    df_CTNItemConst_key.rename(columns={Sales_Domain_AP2_COLUMN:Sales_Domain_AP2_COLUMN+'_ORG',
                                        Sub_Location_Rep_AP2_COLUMN:Sales_Domain_AP2_COLUMN}, inplace=True)
    df_CTNItemConst_key = pd.merge(df_CTNItemConst_key, df_in_SalesPlanAP2,
                                   on=[Version_COLUMN, Location_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN],
                                   how="left")
    # CTN_Item_Const_Start_Week 이후의 데이타를 집계함.
    # CTN_Item_Const_Start_Week, Time_Week_COLUMN 데이타Type을 동일하게 처리함.
    df_CTNItemConst_key[CTN_Item_Const_Start_Week] = df_CTNItemConst_key[CTN_Item_Const_Start_Week].astype(str)
    df_CTNItemConst_key[Time_Week_COLUMN] = df_CTNItemConst_key[Time_Week_COLUMN].astype(str)
    df_CTNItemConst_key["FLAG"] = np.select(
        [
            (df_CTNItemConst_key[CTN_Item_Const_Start_Week] <= df_CTNItemConst_key[Time_Week_COLUMN]),
            (df_CTNItemConst_key[CTN_Item_Const_Start_Week] == "-")
        ],["Y","Y"],default="N"
    )

    step(300, '=====> STEP(END) df_CTNItemConst_key_318')
    # 데이타 집계
    df_CTNItemConst_key = df_CTNItemConst_key.loc[df_CTNItemConst_key['FLAG'] == 'Y']
    key_column = [Version_COLUMN, Location_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN+'_ORG' ]
    sum_columns = [Sales_Plan_AP2_Shipment, Sales_Plan_AP2_Dmd, Sales_Plan_AP2_Short, Sales_Plan_AP2_EOH]
    agg_dict = {col: 'sum' for col in sum_columns}
    df_CTNItemConst_SalesPlanAP2 = df_CTNItemConst_key.groupby(by=key_column).agg(agg_dict, skipna=True).reset_index()
    df_CTNItemConst_SalesPlanAP2.rename(columns={Sales_Domain_AP2_COLUMN+'_ORG':Sales_Domain_AP2_COLUMN}, inplace=True)
    df_in_CTNItemConst_temp = pd.merge(df_in_CTNItemConst_temp, df_CTNItemConst_SalesPlanAP2,
                                       on=[Version_COLUMN,Location_COLUMN,Item_COLUMN,Sales_Domain_AP2_COLUMN], how="left")

    step(300, '=====> STEP(END) df_in_CTNItemConst_temp_SalesPlan')
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # SalesActualAP2 데이타 처리
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #df_BODItem_AP2.rename(columns={Sub_Location_Rep_AP2_COLUMN:Sales_Domain_AP2_COLUMN},inplace=True)
    df_BODItem_ITEM_AP2 = df_in_BODItem[[Version_COLUMN, Item_COLUMN, Sub_Location_Rep_AP2_COLUMN]].drop_duplicates()
    df_BODItem_ITEM_AP2.rename(columns={Sub_Location_Rep_AP2_COLUMN:Sales_Domain_AP2_COLUMN}, inplace=True)
    step(300, '=====> STEP(END) df_BODItem_ITEM_AP2')
    if not df_in_SalesActualAP2.empty:
        df_in_SalesActualAP2_All = df_in_SalesActualAP2.copy()
        df_in_SalesActualAP2_All = pd.merge(df_in_SalesActualAP2_All,df_BODItem_ITEM_AP2,
                                            on=[Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN], how="inner")
        df_in_SalesActualAP2_All = df_in_SalesActualAP2_All.groupby(by=[Version_COLUMN,Item_COLUMN]).sum().reset_index()

        df_in_SalesActualAP2_All[Sales_Domain_AP2_COLUMN] = "All"
        df_in_SalesActualAP2_All = df_in_SalesActualAP2_All[[Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, Sales_Actual_AP2_Prod]]

        df_in_SalesActualAP2_AP2 = df_in_SalesActualAP2.copy()
        df_in_SalesActualAP2_AP2 = df_in_SalesActualAP2_AP2.groupby(by=[Version_COLUMN,Item_COLUMN,Sales_Domain_AP2_COLUMN]).sum().reset_index()
        df_in_SalesActualAP2_AP2 = df_in_SalesActualAP2_AP2[[Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, Sales_Actual_AP2_Prod]]
        df_in_SalesActualAP2_SUM = pd.concat([df_in_SalesActualAP2_All, df_in_SalesActualAP2_AP2], ignore_index=True)
        df_in_CTNItemConst_temp = df_in_CTNItemConst_temp.merge(df_in_SalesActualAP2_SUM,
                                                            on=[Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN], how='left')
    else:
        df_in_CTNItemConst_temp[Sales_Actual_AP2_Prod] = None
    step(300, '=====> STEP(END) df_in_CTNItemConst_temp(AP2)')
    df_in_CurrentDay[Key_on] = 1
    df_in_CTNItemConst_temp[Key_on] = 1
    df_in_CTNItemConst_temp = df_in_CTNItemConst_temp.merge(df_in_CurrentDay, on=Key_on, how='left')
    df_in_CTNItemConst_temp[Time_Day_COLUMN] = pd.to_datetime(df_in_CTNItemConst_temp[Time_Day_COLUMN],
                                                              format='%Y-%m-%d', errors='coerce')

    step(300, '=====> STEP(END) df_in_CTNItemConst_temp(Date)')
    # CTN_Item_Const_Apply_Flag 가 "N"인 경우 체크하지 않음.
    #df_in_CTNItemConst_temp[CTN_Item_Const_Apply_Flag] = np.where(
    #    df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date].notna() & (
    #            (df_in_CTNItemConst_temp[Time_Day_COLUMN] - df_in_CTNItemConst_temp[PLC_Mfg_EOP_Cur_Date]).dt.days > 90),
    #    'Out of Date', 'Y')
    df_in_CTNItemConst_temp[CTN_Item_Const_Apply_Flag] = df_in_CTNItemConst_temp.apply(applyCheck, axis=1)
    step(300, '=====> STEP(END) df_in_CTNItemConst_temp')
    df_in_CTNItemConst_temp.rename(columns={Sales_Plan_AP2_Shipment:CTN_Item_Const_Frozen_SOP_Qty,
                                            Sales_Plan_AP2_Dmd:CTN_Item_Const_DP_Qty_from_W0,
                                            Sales_Plan_AP2_Short:CTN_Item_Const_Frozen_SOP_DP_Diff_Qty,
                                            Sales_Plan_AP2_EOH:CTN_Item_Const_EOH_at_PSI,
                                            Sales_Actual_AP2_Prod:CTN_Item_Const_Prod_Result_Qty_before_W0}, inplace=True)

    fillna_int_columns =[CTN_Item_Const_Frozen_SOP_Qty,CTN_Item_Const_DP_Qty_from_W0,
                         CTN_Item_Const_Frozen_SOP_DP_Diff_Qty,CTN_Item_Const_EOH_at_PSI,
                         CTN_Item_Const_Prod_Result_Qty_before_W0]
    for col in fillna_int_columns:
        df_in_CTNItemConst_temp[col] = df_in_CTNItemConst_temp[col].fillna(0)


    df_out_CTNItemConst = df_in_CTNItemConst_temp.copy()
    df_out_CTNItemConst = df_out_CTNItemConst[
        [Version_COLUMN, Item_COLUMN, Location_COLUMN, Sales_Domain_AP2_COLUMN, CTN_Item_Const_End_Week,
         CTN_Item_Const_Frozen_SOP_Qty, CTN_Item_Const_DP_Qty_from_W0, CTN_Item_Const_Frozen_SOP_DP_Diff_Qty,
         CTN_Item_Const_EOH_at_PSI, CTN_Item_Const_Prod_Result_Qty_before_W0, CTN_Item_Const_Apply_Flag
         ]]

    print_df(df_out_CTNItemConst, 'df_out_CTNItemConst', True)
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 8. (1) 최종 Out_Put Save
    ################################################################################################################
    step(400, '=====> STEP 9(Start) : output data machining')


    row_count, col_count = df_out_CTNItemConst.shape
    note(f'=====> Final df_out_CTNItemConst rows : {row_count} , Columns : {col_count}')

    if is_local:
        note(f'=====> Final output table create')
        print_df(df_out_CTNItemConst, 'df_out_CTNItemConst',True)
        save_csv_file(df_out_CTNItemConst, "Fact.CTNItemConst_Last")

    print_df(df_out_CTNItemConst, 'df_out_CTNItemConst', True)

    step(900, '=====> STEP 8(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())


    df_out_CTNItemConst = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(1000, '===================== plugin Execution End =====================')

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

