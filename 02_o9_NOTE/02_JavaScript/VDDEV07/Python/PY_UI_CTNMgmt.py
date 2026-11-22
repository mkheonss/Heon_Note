

"""

* 프로그램명
    - PY_UI_CTNMgmt

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.01.31 / ybest7.park (박병훈) / Create
- 2025.04.01 수정
- 2025.05.08 PY_UI_CTNItemConst program 분기
-.2025.05.14 SRA Date, EOP Date등등 처리 (By ys5236.kang)
-.2025.06.12 Wilde 입력 데이타 처리 부분 수정 (By ys5236.kang)
-.2025.06.12 BOD Item Location 조건 추가 (By ys5236.kang)
-.2025.09.10 Item 속성 중 Product, Marketing Name, CTN 등등 추가
-.2025.09.12
   (1) BOD Item 메져그룹에서 Item 속성을 조회하도록 수정함. (df_in_BODItem)
   (2) df_in_SalesItem에서 Item 속성 조회 삭제함.
-. 2025.11.12
   applyCheck 추가
-. 2025.11.14
   (1) Item, Exception Item 처리 로직 수정
   데이타 중 'All'이 있는 경우 All만 적용되도록 함.
-. 2025.11.17
   입력된 항목중 All인 경우 All로 적용되도록 함.
   ex) Inch input : All^55^66^75 => All 값으로 처리함.
-. 2025.12.04
   메져 변경 부분 수정
   Measure.[CTN Grp Const_GC ID] => Measure.[CTN Grp Const_GC Code]
   Measure.[CTN Grp Const_AP2 ID] => Measure.[CTN Grp Const_AP2 Code]
-. 2026.01.19 (by ys5236.kang)
  <CTN Grp Const>, <CTN Grp Const Ecp> 메져그룹 디멘젼 변경:   [Sequence].[Sequence] 삭제됨.
-. 2026.01.23 (ybest7.park)
    CTN Grp Const_Apply Flag = 'N" 으로 인풋 시  (CTN_Grp_Const_Frozen_Week, CTN_Grp_Const_Start_Week,
    CTN_Grp_Const_Frozen_SOP_Qty,CTN_Grp_Const_End_Week,CTN_Grp_Const_Frozen_SOP_Override_Qty,
    CTN_Grp_Const_Frozen_SOP_Diff_Qty ) Null로 설정
    CTN_Grp_Const_End_Week 데이터 CTN_Grp_Const_EOP_MAX 로 변경
-. 2026.03.11
    - CTN Grp Const_End Week 생성되는 부분 삭제
    - input Query 수정 후 전처리 과정에서 불필요한 컬럼 삭제
-.2026.03.19
    - CTN Grp Const_Except Item 값 True로 설정 추가
    - CTN Grp Const_Frozen SOP Override Qty null로 설정하는 것 변경
-.2026.03.24
    - df_in_BODItem 1차 필터 후 df_in_CTNGrpConst 값 찾는 방법으로 속도 개선
    - df_in_SalesPlanAP2 input Query 수정 및 df_in_SalesActualAP2 삭제 (df_in_SalesPlanAP2로 통합)




* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary


* Input Table
   - df_in_CTNGrpConst = Select ([Version].[Version Name] * [Group].[Group ID].filter(#.Name startswith "MCT_") ) on row,({Measure.[CTN Grp Const_From Site ID], Measure.[CTN Grp Const_GC Code], Measure.[CTN Grp Const_AP2 Code], Measure.[CTN Grp Const_Product Grp], Measure.[CTN Grp Const_Product], Measure.[CTN Grp Const_Project], Measure.[CTN Grp Const_Series], Measure.[CTN Grp Const_MKT Name], Measure.[CTN Grp Const_Inch], Measure.[CTN Grp Const_Item CTN Attr], Measure.[CTN Grp Const_Year], Measure.[CTN Grp Const_Item], Measure.[CTN Grp Const_Except Item], Measure.[CTN Grp Const_Frozen Week], Measure.[CTN Grp Const_Start Week], Measure.[CTN Grp Const_End Week], Measure.[CTN Grp Const_Apply Flag], Measure.[CTN Grp Const_DP Qty from W0], Measure.[CTN Grp Const_Frozen SOP Qty],Measure.[CTN Grp Const_Frozen SOP DP Diff Qty],Measure.[CTN Grp Const_EOH at PSI], Measure.[CTN Grp Const_Prod Result Qty before W0],Measure.[CTN Grp Const_Frozen SOP Diff Qty],Measure.[CTN Grp Const_Frozen SOP Override Qty], Measure.[Dummy] }) on column;
   - df_in_BODItem = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Sub Location].[Sub Location] * [Sub Location].[Sub Location GC] *[Sub Location].[Sub Location Rep AP2]* [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Asn], Measure.[Dummy]}) on column Where {Measure.[BOD Item_asn] >-1};
   - df_in_SalesItem = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Sales Domain].[GC] * [Sales Domain].[AP2] ) on row,({Measure.[Sales Item Asn_Valid Flag]}) on column Where {Measure.[Sales Item Asn_Valid Flag] == "true"};
   - df_in_PLCMfg =  Select ([Version].[Version Name] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Location].[Location] ) on row, ({Measure.[PLC Mfg_EOP Cur Date],Measure.[PLC Mfg_SRA Com Date] , Measure.[Dummy]}) on column;
   - df_in_SalesPlanAP2 =  Select ([Version].[Version Name] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales PSI AP2 W_Shipment], Measure.[Sales PSI AP2 W_Dmd], Measure.[Sales PSI AP2 W_Short], Measure.[Sales PSI AP2 W_EOH], Measure.[Sales PSI AP2 W_Prod], Measure.[Dummy]}) on column ;
   # - df_in_SalesActualAP2 =  Select ([Version].[Version Name] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales PSI AP2 W_Prod], Measure.[Dummy]}) on column;
   - df_in_CurrentDay = Select (&CurrentDay);
   - df_in_TimeWeek = select ([Time].[Day] * [Time].[Week] );
   # - df_in_CTNItemConst = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Apply Flag], Measure.[CTN Item Const_Created By], Measure.[CTN Item Const_Creation Time], Measure.[CTN Item Const_DP Qty from W0], Measure.[CTN Item Const_EOH at PSI], Measure.[CTN Item Const_End Week], Measure.[CTN Item Const_Frozen SOP DP Diff Qty], Measure.[CTN Item Const_Frozen SOP Diff Qty], Measure.[CTN Item Const_Frozen SOP Override Qty], Measure.[CTN Item Const_Frozen SOP Override Reason], Measure.[CTN Item Const_Frozen SOP Override Remain Qty], Measure.[CTN Item Const_Frozen SOP Qty], Measure.[CTN Item Const_Frozen Week], Measure.[CTN Item Const_Prod Result Qty before W0], Measure.[CTN Item Const_Start Week], Measure.[CTN Item Const_Update Time], Measure.[CTN Item Const_Updated By], Measure.[Dummy]}) on column;
   # - df_in_ItemBuyer = Select([Item].[Item]*[Item].[Buyer]) ;

* 데이터 삭제
    DELETE DATA FOR MODEL [CTN Grp Const Ecp] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [CTN Grp Const Ecp] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_CTNGroupConstraintDetail = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] * [Sequence].[Sequence] * [Group].[Group ID].[MCT_00001] ) on row, ({Measure.[CTN Grp Const Ecp_Created By], Measure.[CTN Grp Const Ecp_Creation Time], Measure.[CTN Grp Const Ecp_DP Qty from W0], Measure.[CTN Grp Const Ecp_EOH at PSI], Measure.[CTN Grp Const Ecp_Ecp Flag], Measure.[CTN Grp Const Ecp_End Week], Measure.[CTN Grp Const Ecp_PLC EOP Curr Week], Measure.[CTN Grp Const Ecp_PLC SRA Curr Week], Measure.[CTN Grp Const Ecp_Prod Result Qty before W0], Measure.[CTN Grp Const Ecp_Start Week], Measure.[CTN Grp Const Ecp_Total SOP DP Diff Qty], Measure.[CTN Grp Const Ecp_Total SOP Qty from W0], Measure.[CTN Grp Const Ecp_Update Time], Measure.[CTN Grp Const Ecp_Updated By]}) on column;
    - df_out_CTNGroupConstraint = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Apply Flag], Measure.[CTN Item Const_Created By], Measure.[CTN Item Const_Creation Time], Measure.[CTN Item Const_DP Qty from W0], Measure.[CTN Item Const_EOH at PSI], Measure.[CTN Item Const_End Week], Measure.[CTN Item Const_Frozen SOP DP Diff Qty], Measure.[CTN Item Const_Frozen SOP Diff Qty], Measure.[CTN Item Const_Frozen SOP Override Qty], Measure.[CTN Item Const_Frozen SOP Override Reason], Measure.[CTN Item Const_Frozen SOP Override Remain Qty], Measure.[CTN Item Const_Frozen SOP Qty], Measure.[CTN Item Const_Frozen Week], Measure.[CTN Item Const_Prod Result Qty before W0], Measure.[CTN Item Const_Start Week], Measure.[CTN Item Const_Update Time], Measure.[CTN Item Const_Updated By]}) on column;
    # - df_out_CTNItemConst = Select ([Version].[Version Name].[CWV_MP] * [Group].[Group ID]) on row, ({Measure.[CTN Grp Const_Frozen Week],Measure.[CTN Grp Const_Start Week],Measure.[CTN Grp Const_End Week],Measure.[CTN Grp Const_Frozen SOP Qty],Measure.[CTN Grp Const_Frozen SOP Override Qty],Measure.[CTN Grp Const_Frozen SOP Diff Qty]}) on column;
    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    EXEC plugin instance [PY_UI_CTNMgmt] for measures {[CTN Grp Const_From Site]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


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
str_instance = 'PY_UI_CTNMgmt'
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
    try:
        file_path = f"{file_name}.csv"
        if not os.path.exists(file_path):
            step(f"=====> 파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame()  # 빈 DataFrame 반환
        return pd.read_csv(file_path, low_memory=False, encoding="UTF-8")

    except Exception as e:
        step(f"=====> CSV 파일 읽기 실패: {file_name}, 오류: {str(e)}")
        return pd.DataFrame()  # 에러 발생시 빈 DataFrame 반환


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')

# def vd_log_start():
#     log_path = os.path.dirname(__file__) if is_local else ""
#     vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, Logger, is_local, log_path)


def vd_log_end():
    vdCommon.gfn_pyLog_end()


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

def applyCheck(row):
    timeDay = row[Time_Day_COLUMN]
    eopCurDate = row[PLC_Mfg_EOP_Cur_Date]
    dayGap = (timeDay - eopCurDate).days
    if(row[CTN_Grp_Const_Apply_Flag] ==  "N"):
        return "N"
    else:
        if((row[PLC_Mfg_EOP_Cur_Date] != None) & (dayGap > 90)):
            return "Out of Date"
        else:
            return "Y"

# print_df = vdCommon.print_df

Logger.debug(f'[START] {str_instance}')
Logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')
tracemalloc.start()

if __name__ == '__main__':

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
        # PARAM_OUTVERSION_VALUE = "CWV_MP"

        # 데이터 파일 읽기
        if is_local:
            # 로컬일 경우 버전 처리
            # paramOutVersion = PARAM_OUTVERSION_VALUE

            df_in_CTNGrpConst = read_csv_file('df_in_CTNGrpConst_EX')
            df_in_BODItem = read_csv_file('df_in_BODItem_EX')
            df_in_SalesItem = read_csv_file('df_in_SalesItem_EX')
            df_in_PLCMfg = read_csv_file('df_in_PLCMfg_EX')
            df_in_SalesPlanAP2 = read_csv_file('df_in_SalesPlanAP2_EX')
            # df_in_SalesActualAP2 = read_csv_file('df_in_SalesActualAP2_EX')
            df_in_CurrentDay = read_csv_file('df_in_CurrentDay')
            df_in_TimeWeek = read_csv_file('df_in_TimeWeek')

        print_df(df_in_CTNGrpConst, 'df_in_CTNGrpConst',True)
        print_df(df_in_BODItem, 'df_in_BODItem',False)
        print_df(df_in_SalesItem, 'df_in_SalesItem',False)
        print_df(df_in_PLCMfg, 'df_in_PLCMfg',False)
        print_df(df_in_SalesPlanAP2, 'df_in_SalesPlanAP2',False)
        # print_df(df_in_SalesActualAP2, 'df_in_SalesActualAP2',False)
        print_df(df_in_CurrentDay, 'df_in_CurrentDay',False)
        print_df(df_in_TimeWeek, 'df_in_TimeWeek',False)

        step(100, '=====> STEP 1(End) : Check memory usage & runtime')
        ################################################################################################################
        # DataFrame Column 변수 처리
        ################################################################################################################
        step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

        Version_COLUMN = 'Version.[Version Name]'
        GroupID_COLUM = 'Group.[Group ID]'
        Sequence_COLUMN = 'Sequence.[Sequence]'
        Item_COLUMN = 'Item.[Item]'
        Item_Product_GROUP_COLUMN = 'Item.[Product Group]'
        Item_Product_COLUMN = 'Item.[Product]'
        Item_Project_COLUMN = 'Item.[Project]'
        Item_Series_COLUM = 'Item.[Series]'
        Item_Series_Name_COLUM = 'Item.[Series Name]'
        Item_Marketing_Name_COLUM = 'Item.[Marketing Name]'
        Item_Inch_COLUM = 'Item.[Inch]'
        Item_CTN_COLUM = 'Item.[CTN]'
        Item_Year_COLUMN = 'Item.[Year]'
        Time_Week_COLUMN = 'Time.[Week]'
        Time_Day_COLUMN = 'Time.[Day]'
        Sales_Domain_AP2_COLUMN = 'Sales Domain.[AP2]'
        Sales_Domain_GC_COLUMN = 'Sales Domain.[GC]'
        Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
        Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
        Location_COLUMN = 'Location.[Location]'
        Sub_Location_GC_COLUMN = 'Sub Location.[Sub Location GC]'
        # note(f"========================================={Sub_Location_GC_COLUMN}")
        Sub_Location_Rep_AP2_COLUMN = 'Sub Location.[Sub Location Rep AP2]'
        # note(f"========================================={Sub_Location_Rep_AP2_COLUMN}")

        Key_on = 'key_on'

        CTN_Grp_Const_From_Site = 'CTN Grp Const_From Site'
        CTN_Grp_Const_From_Site_ID = 'CTN Grp Const_From Site ID'
        CTN_Grp_Const_Product_Grp = 'CTN Grp Const_Product Grp'
        CTN_Grp_Const_Product = 'CTN Grp Const_Product'
        CTN_Grp_Const_Project = 'CTN Grp Const_Project'
        # Series Name 데이타가 들어감.
        CTN_Grp_Const_Series = 'CTN Grp Const_Series'
        CTN_Grp_Const_MKT_Name = 'CTN Grp Const_MKT Name'
        CTN_Grp_Const_Inch = 'CTN Grp Const_Inch'
        CTN_Grp_Const_CTN_Attr = 'CTN Grp Const_Item CTN Attr'
        CTN_Grp_Const_Year = 'CTN Grp Const_Year'
        CTN_Grp_Const_Item = 'CTN Grp Const_Item'
        CTN_Grp_Const_Frozen_Week = 'CTN Grp Const_Frozen Week'
        CTN_Grp_Const_Start_Week = 'CTN Grp Const_Start Week'
        CTN_Grp_Const_AP2 = 'CTN Grp Const_AP2'
        CTN_Grp_Const_AP2_CODE = 'CTN Grp Const_AP2 Code'
        CTN_Grp_Const_GC_CODE = 'CTN Grp Const_GC Code'
        CTN_Grp_Const_Apply_Flag = 'CTN Grp Const_Apply Flag'
        CTN_Grp_Const_End_Week = 'CTN Grp Const_End Week'
        CTN_Grp_Const_Frozen_SOP_Qty = 'CTN Grp Const_Frozen SOP Qty'
        CTN_Grp_Const_Prod_Result_Qty_before_W0 = 'CTN Grp Const_Prod Result Qty before W0'
        CTN_Grp_Const_DP_Qty_from_W0 = 'CTN Grp Const_DP Qty from W0'
        CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty = 'CTN Grp Const_Frozen SOP DP Diff Qty'
        CTN_Grp_Const_EOH_at_PSI = 'CTN Grp Const_EOH at PSI'
        CTN_Grp_Const_Except_Item = 'CTN Grp Const_Except Item'
        CTN_Grp_Const_Ecp_Start_Week = 'CTN Grp Const Ecp_Start Week'
        CTN_Grp_Const_Frozen_SOP_Override_Qty = 'CTN Grp Const_Frozen SOP Override Qty'
        CTN_Grp_Const_Frozen_SOP_Diff_Qty = 'CTN Grp Const_Frozen SOP Diff Qty'
        CTN_Grp_Const_EOP_MAX = 'CTN Grp Const_EOP MAX'
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정 : 2025-05-14
        CTN_Grp_Const_Ecp_PLC_EOP_CURR_WEEK = 'CTN Grp Const Ecp_PLC EOP Curr Week'
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        CTN_Grp_Const_ECP_Flag = 'CTN Grp Const Ecp_Ecp Flag'
        CTN_Grp_Const_Ecp_Total_SOP_Qty_from_W0 = 'CTN Grp Const Ecp_Total SOP Qty from W0'
        CTN_Grp_Const_Ecp_Total_SOP_DP_Diff_Qty = 'CTN Grp Const Ecp_Total SOP DP Diff Qty'
        CTN_Grp_Const_Ecp_Prod_Result_Qty_before_W0 = 'CTN Grp Const Ecp_Prod Result Qty before W0'
        CTN_Grp_Const_Ecp_DP_Qty_from_W0 = 'CTN Grp Const Ecp_DP Qty from W0'
        CTN_Grp_Const_Ecp_EOH_at_PSI = 'CTN Grp Const Ecp_EOH at PSI'
        CTN_Grp_Const_Ecp_PLC_SRA_Curr_Week = 'CTN Grp Const Ecp_PLC SRA Curr Week'
        CTN_Grp_Const_Insert_Flag = 'CTN Grp Const_Insert Flag'
        CTN_Grp_Const_Ecp_End_Week = 'CTN Grp Const Ecp_End Week'

        PLC_Mfg_EOP_Cur_Date = 'PLC Mfg_EOP Cur Date'
        PLC_Mfg_SRA_Com_Date = 'PLC Mfg_SRA Com Date'

        # Sales_Plan_AP2_Shipment = 'Sales Plan AP2_Shipment'
        # Sales_Plan_AP2_Dmd = 'Sales Plan AP2_Dmd'
        # Sales_Plan_AP2_Short = 'Sales Plan AP2_Short'
        # Sales_Plan_AP2_EOH = 'Sales Plan AP2_EOH'

        Sales_PSI_AP2_W_Shipment = 'Sales PSI AP2 W_Shipment'
        Sales_PSI_AP2_W_Dmd = 'Sales PSI AP2 W_Dmd'
        Sales_PSI_AP2_W_Short = 'Sales PSI AP2 W_Short'
        Sales_PSI_AP2_W_EOH = 'Sales PSI AP2 W_EOH'

        # Sales_Actual_AP2_Prod = 'Sales Actual AP2_Prod'

        Sales_PSI_AP2_W_Prod = 'Sales PSI AP2 W_Prod'

        step(200, '=====> STEP 2(End) : Check memory usage & runtime')

        ################################################################################################################
        # Step 3 (1) 날짜 데이터 설정을 위한 전처리 → 현재 Sever Error 발생
        ################################################################################################################
        step(300, '=====> STEP 3(Start) ')

        ############################################## 2026.03.11 (ybest7.park 수정) ###################################
        # 불필요한 컬럼 지정
        drop_cols = [Item_Product_GROUP_COLUMN, Item_Product_COLUMN,Item_Project_COLUMN,Item_Series_Name_COLUM,
                     Item_Marketing_Name_COLUM,Item_Inch_COLUM,Item_CTN_COLUM,Item_Year_COLUMN]

        # 데이터 프레임 drop_cols 삭제
        for df in [df_in_SalesItem, df_in_PLCMfg,  df_in_SalesPlanAP2] :
            df.drop(columns=drop_cols, errors='ignore', axis=1, inplace=True)

        df_in_SalesActualAP2 = df_in_SalesPlanAP2.copy()

        ############################################## 2026.03.11 (ybest7.park 수정 완료) #################################


        # df_in_CTNGrpConst = df_in_CTNGrpConst.head(0)

        # df_in_BODItem 중복 제거 및 필터링
        df_in_BODItem_temp = df_in_BODItem[
            [Version_COLUMN, Item_COLUMN, Item_Product_GROUP_COLUMN, Item_Product_COLUMN, Item_Project_COLUMN,
             Item_Series_Name_COLUM,
             Item_Marketing_Name_COLUM, Item_Inch_COLUM, Item_CTN_COLUM, Item_Year_COLUMN, Location_COLUMN,
             Sub_Location_GC_COLUMN,
             Sub_Location_Rep_AP2_COLUMN]].drop_duplicates().copy()

        # df_in_BODItem & df_in_SalesItem 과 merge를 위한 컬럼명 변경
        df_in_BODItem_temp = df_in_BODItem_temp.rename(
            columns={Sub_Location_GC_COLUMN: Sales_Domain_GC_COLUMN, Sub_Location_Rep_AP2_COLUMN: Sales_Domain_AP2_COLUMN})

        # 데이터 프레임 형 변환 (int → str)
        # str columns 설정
        str_cols = [Sales_Domain_AP2_COLUMN, Sales_Domain_GC_COLUMN]
        # 데이터 타입 변환이 필요한 데이터 프레임 리스트로 변환
        str_frames = [df_in_BODItem_temp, df_in_SalesItem]
        # 반복문을 통한 데이터 프레임 형 변환
        for df in str_frames:
            for col in str_cols:
                df[col] = df[col].astype(str)

        # Merge를 위한 중복 삭제 (수정 2025-05-09 수정)
        df_in_SalesItem = df_in_SalesItem[
            df_in_SalesItem.columns[~df_in_SalesItem.columns.isin(
                [Location_COLUMN, "Dummy", "Sales Item Asn_Valid Flag"])]].drop_duplicates()

        # df_in_BODItem & df_in_SalesItem merge
        df_in_BODItem_temp = df_in_BODItem_temp.merge(
            df_in_SalesItem, on=[
                Version_COLUMN, Sales_Domain_AP2_COLUMN, Item_COLUMN, Sales_Domain_GC_COLUMN],
            how='left')

        # df_in_BODItem_temp Data 형 변환
        grainValue_col = list(dict.fromkeys([
            Item_Product_GROUP_COLUMN, Item_Product_COLUMN, Item_Project_COLUMN, Item_Series_Name_COLUM,
            Item_Marketing_Name_COLUM, Item_Inch_COLUM, Item_CTN_COLUM, Item_Year_COLUMN]))

        df_in_BODItem_temp.loc[:, grainValue_col] = df_in_BODItem_temp[grainValue_col].fillna('-').astype(str)



        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # All 입력시 All 데이타로 모두 변경함.(by 2025,11.17)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        const_col_item_list = [
            CTN_Grp_Const_Item, CTN_Grp_Const_Except_Item, CTN_Grp_Const_From_Site_ID, CTN_Grp_Const_GC_CODE,
            CTN_Grp_Const_AP2_CODE, CTN_Grp_Const_Product_Grp, CTN_Grp_Const_Product, CTN_Grp_Const_Project,
            CTN_Grp_Const_Series, CTN_Grp_Const_MKT_Name, CTN_Grp_Const_Inch, CTN_Grp_Const_CTN_Attr, CTN_Grp_Const_Year]

        # 전처리를 위해 df_in_CTNGrpConst Data Frame 복사
        df_in_CTNGrpConst_temp = df_in_CTNGrpConst.copy()
        print_df(df_in_CTNGrpConst_temp, "df_in_CTNGrpConst_temp(전)",True)
        results = []
        for _, cond_row in df_in_CTNGrpConst_temp.iterrows():
            # print(f'DATA CHECK(전)::: {cond_row}')
            for col in const_col_item_list:
                cond_val = str(cond_row[col]).split("^")
                all_list = [i for i in cond_val if i == 'All']
                # print(f'{len(cond_val)},{cond_val}, All_list{len(all_list)},{all_list}')
                if (len(all_list) > 0):
                    cond_row[col] = "All"
            # print(f'DATA CHECK(후)::: {cond_row}')
            results.append(cond_row)

        final_results = pd.concat(results, ignore_index=True) if results else df_in_CTNGrpConst_temp.head(0).copy()

        # df_in_CTNGrpConst_temp = pd.DataFrame(results)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Item filter를 위한 df_in_CTNGrpConst 의 Columns Rename
        rename_col = {CTN_Grp_Const_AP2_CODE: Sales_Domain_AP2_COLUMN,
                      CTN_Grp_Const_GC_CODE: Sales_Domain_GC_COLUMN,
                      CTN_Grp_Const_From_Site_ID: Location_COLUMN,
                      CTN_Grp_Const_Item: Item_COLUMN,
                      CTN_Grp_Const_Product_Grp: Item_Product_GROUP_COLUMN,
                      CTN_Grp_Const_Product: Item_Product_COLUMN,
                      CTN_Grp_Const_Project: Item_Project_COLUMN,
                      CTN_Grp_Const_Series: Item_Series_Name_COLUM,
                      CTN_Grp_Const_MKT_Name: Item_Marketing_Name_COLUM,
                      CTN_Grp_Const_Inch: Item_Inch_COLUM,
                      CTN_Grp_Const_CTN_Attr: Item_CTN_COLUM,
                      CTN_Grp_Const_Year: Item_Year_COLUMN}

        df_in_CTNGrpConst_temp = df_in_CTNGrpConst_temp.rename(columns=rename_col)

        # 필터를 위한 데이터 프레임 중복 제거
        df_in_BODItem_temp = df_in_BODItem_temp.drop_duplicates(ignore_index=True)

        step(300, '=====> STEP 3(End) : Check memory usage & runtime')

        ################################################################################################################
        # Step 4 (1) Global Top 기준 pivot Test
        ###############################################################################################################
        step(400, '=====> STEP 4(Start) : output data machining')

        # 와이드 카드 분리를 위한 데이터 프레임 복사
        df_in_CTNGrpConst_temp_wide_all = df_in_CTNGrpConst_temp.copy()
        # 와이드 카드 포함 여부를 가지고 is_wildcard 열 생성
        df_in_CTNGrpConst_temp_wide_all['is_wildcard'] = np.where(
            df_in_CTNGrpConst_temp[Item_COLUMN].str.contains('%', na=False), 'Y', 'N')
        df_in_CTNGrpConst_temp_wide_all['is_item_all'] = np.where(
            df_in_CTNGrpConst_temp_wide_all[Item_COLUMN].str.contains('All', na=False), 'Y', 'N')
        # __________________________________________________________________________________________________________
        # 조건을 찾기 위한 컬럼 설정
        # Location_COLUMN 추가함.(2025-06-12)
        condition_columns = [
            Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, Sales_Domain_GC_COLUMN, Location_COLUMN,
            Item_Product_GROUP_COLUMN, Item_Product_COLUMN, Item_Project_COLUMN, Item_Series_Name_COLUM,
            Item_Marketing_Name_COLUM, Item_Inch_COLUM, Item_CTN_COLUM, Item_Year_COLUMN]
        # 조건의 멀티 값 확장을 위한 리스트로 변환
        # 2025.06.12(by Kang) : Wild 입력시 구분자(^)을 코마(,)로 대체함.
        # 2025.09.10(by Kang Y.S) : 화면 EW 전환시 구분자 ^로만 들어옴.
        # df_in_CTNGrpConst_temp_wide_all[Item_COLUMN] = df_in_CTNGrpConst_temp_wide_all[Item_COLUMN].str.replace("^",",")
        df_in_CTNGrpConst_temp_wide_all[condition_columns] = df_in_CTNGrpConst_temp_wide_all[condition_columns].applymap(
            lambda x: re.split(r'\s*[,^]\s*',x) if isinstance(x,str) else x)
        # Item column의 개수를 확인
        df_in_CTNGrpConst_temp_wide_all['col_len'] = df_in_CTNGrpConst_temp_wide_all[Item_COLUMN].apply(
            lambda x: len(x) if isinstance(x, list) else 0)

        ######################################### by : ybest7.park df_in_BODItem_temp 1차 필터 ##########################
        # 필터된 데이터 프레임 확장
        for col in df_in_CTNGrpConst_temp_wide_all[condition_columns]:
            df_in_CTNGrpConst_temp_wide_all = df_in_CTNGrpConst_temp_wide_all.explode(col)

        src_df = df_in_CTNGrpConst_temp_wide_all.copy()

        src_df = src_df.reset_index(drop=True)

        src = (
            src_df[Item_COLUMN]
            .fillna('')
            .astype(str)
            .str.strip()
        )

        all_mask = src.str.upper().eq('ALL').to_numpy()
        wild_mask = src.str.contains('%', regex=False).to_numpy() & (~all_mask)
        exact_mask = src.ne('').to_numpy() & (~all_mask) & (~wild_mask)

        df_item_all = src_df.iloc[all_mask].copy()
        df_item_wild = src_df.iloc[wild_mask].copy()
        df_item_exact = src_df.iloc[exact_mask].copy()

        src_df = src_df.drop_duplicates()

        exact_items = set(src[exact_mask])
        wild_items = src[wild_mask].drop_duplicates().tolist()

        df_in_BODItem_temp[condition_columns] = df_in_BODItem_temp[condition_columns].astype(str)
        target = df_in_BODItem_temp.copy()
        target['_item_norm'] = (
            target[Item_COLUMN]
            .fillna('')
            .astype(str)
            .str.strip()
        )

        mask_exact = target['_item_norm'].isin(exact_items)
        target_exact = target.loc[mask_exact].copy()

        tokens = []

        for x in wild_items:
            parts = [p.strip() for p in x.split('%') if p.strip()]
            if parts:
                token = max(parts, key=len)
                tokens.append(token)

        tokens = sorted(set(tokens))

        if tokens:
            pattern = '|'.join(re.escape(t) for t in tokens)
            mask_wild_candidate = target['_item_norm'].str.contains(pattern, na=False, regex=True)
            target_wild_candidate = target.loc[mask_wild_candidate].copy()
        else:
            target_wild_candidate = pd.DataFrame(columns=target.columns)

        target_candidate = (
            pd.concat([target_exact, target_wild_candidate], ignore_index=True)
        )


        def is_all(x):
            if pd.isna(x):
                return True
            return str(x).strip().upper() in {'', 'ALL'}


        attr_cols = [col for col in condition_columns if col != [Version_COLUMN, Item_COLUMN]]


        def build_attr_mask(df_target, key_row, attr_cols):
            mask = pd.Series(True, index=df_target.index)

            for col in attr_cols:
                val = key_row[col]

                if not is_all(val):
                    val = str(val).strip()
                    mask = mask & df_target[col].fillna('').astype(str).str.strip().eq(val)

            return mask


        s = df_in_BODItem_temp[Item_COLUMN].fillna('').astype(str).str.strip()

        all_rows_result = []

        for _, key_row in df_item_all.iterrows():
            attr_mask = build_attr_mask(df_in_BODItem_temp, key_row, attr_cols)
            matched = df_in_BODItem_temp.loc[attr_mask].copy()

            if not matched.empty:
                all_rows_result.append(matched)

        if all_rows_result:
            df_all_reduced = pd.concat(all_rows_result, ignore_index=True).drop_duplicates()
        else:
            df_all_reduced = pd.DataFrame(columns=df_in_BODItem_temp.columns)

        df_final_filtered = (
            pd.concat([target_candidate, df_all_reduced], ignore_index=True).drop(columns='_item_norm')
            .drop_duplicates()
        )

        print_df(df_final_filtered, 'df_final_filtered_필터확인',True )
        ######################################## 1차 필터 완료 2026.03.24##################################################

        # 와이드 카드 조건(and) 조건을 나누기 위한 데이터 프레임 필터링
        df_in_CTNGrpConst_temp_wide = df_in_CTNGrpConst_temp_wide_all[
            (df_in_CTNGrpConst_temp_wide_all['is_wildcard'] == "Y") & (df_in_CTNGrpConst_temp_wide_all['col_len'] >= 1)]

        # 필터된 데이터 프레임 확장
        for col in df_in_CTNGrpConst_temp_wide[condition_columns]:
            df_in_CTNGrpConst_temp_wide = df_in_CTNGrpConst_temp_wide.explode(col)
        # 다시 And 조건을 나누기 위한 is_wildcard 컬럼 설정
        df_in_CTNGrpConst_temp_wide['is_wildcard'] = np.where(
            df_in_CTNGrpConst_temp_wide[Item_COLUMN].str.contains('%'), 'Y', 'N')

        # 조건 필터 및 머지를 위한 데이터 타입 변경
        # df_in_BODItem_temp[CTN_Grp_Const_Except_Item] = np.nan
        df_in_BODItem_temp[condition_columns] = df_in_BODItem_temp[condition_columns].astype(str)
        df_in_CTNGrpConst_temp_wide[condition_columns] = df_in_CTNGrpConst_temp_wide[condition_columns].astype(str)

        # is_wildcard == 'N' 조건만 (전체 조건을 찾기 위한 데이터 프레임 필터)
        filter_mask = (df_in_CTNGrpConst_temp_wide['is_wildcard'] == 'N') & (
                    df_in_CTNGrpConst_temp_wide['is_item_all'] == "Y")
        df_in_CTNGrpConst_temp_wide_filtered = df_in_CTNGrpConst_temp_wide[filter_mask]

        # 필터를 담기 위한 변수 지정
        results = []
        # 조건 행 하나씩 순회
        for _, cond_row in df_in_CTNGrpConst_temp_wide_filtered.iterrows():
            df_filtered = df_final_filtered.copy()

            for col in condition_columns:
                cond_val = cond_row[col]
                # print(f'DATA CHECK::: {col}{cond_val}')

                if pd.isna(cond_val) or str(cond_val).strip().lower() == 'all' or str(cond_val).strip() == '':
                    continue  # 조건이 없거나 All 인 경우 조건 없음
                else:
                    df_filtered = df_filtered[df_filtered[col] == cond_val]
                    # print_df(df_filtered, "df_filtered(For)",True)

            if not df_filtered.empty:  # 조건이 필터된 경우
                df_filtered[GroupID_COLUM] = cond_row[GroupID_COLUM]
                results.append(df_filtered)

        if results:
            final_results = pd.concat(results, ignore_index=True).drop_duplicates()
        else:  # 조건이 빈 데이터 인 경우 컬럼 지정
            final_results = pd.DataFrame(columns=condition_columns)

        print_df(final_results, '와이드 카드 처리 과정 출력')

        # is_wildcard == 'Y' 조건만 필터되어야 하는 데이터 프레임 (제외되어야 하는 데이터 프레임 설정)
        df_in_CTNGrpConst_temp_wide_filtered_exception = df_in_CTNGrpConst_temp_wide[~filter_mask]

        # 중복 삭제 Group_id, Sequence
        wildcard_group_keys = df_in_CTNGrpConst_temp_wide_filtered_exception[
            [GroupID_COLUM]].drop_duplicates()

        # 값을 담기 위한 변수 지정
        wildcard_results = []
        for _, key_row in wildcard_group_keys.iterrows():
            gid = key_row[GroupID_COLUM]

            # 해당 그릅 조건만 추림
            group_conditions = df_in_CTNGrpConst_temp_wide_filtered_exception[
                (df_in_CTNGrpConst_temp_wide_filtered_exception[GroupID_COLUM] == gid)]

            # 각 조건 row에 대해 필터 → set 수집
            for _, cond_row in group_conditions.iterrows():
                df_exception = df_in_BODItem_temp.copy()
                condition_sets = []
                for col in condition_columns:
                    v = cond_row[col]
                    cond_val = "" if pd.isna(v) else str(v).strip()

                    if not cond_val:
                        continue

                    # '%' 포함 여부를 체크함.
                    startChar = cond_val[0:1] if cond_val else ""
                    endChar = cond_val[-1] if cond_val else ""
                    # print(f'##456-COND:::{col},{cond_val},{startChar},{endChar}')
                    if cond_val.lower() in ['all', '', 'nan']:
                        continue

                    if (startChar == "%" and endChar == "%"):
                        prefix = cond_val.replace('%', '')
                        df_exception = df_exception[df_exception[col].str.contains(prefix)]
                    elif startChar == "%":
                        prefix = cond_val.replace('%', '')
                        df_exception = df_exception[df_exception[col].str.endswith(prefix)]
                    elif endChar == "%":
                        prefix = cond_val.replace('%', '')
                        df_exception = df_exception[df_exception[col].str.startswith(prefix)]
                    else:
                        df_exception = df_exception[df_exception[col] == cond_val]
                    # print(f'471-COND:::{col},{cond_val}')

                if not df_exception.empty:
                    condition_sets.append(set(df_exception.index))
                    if condition_sets:
                        common_idx = set.intersection(*condition_sets)
                        matched = df_in_BODItem_temp.loc[list(common_idx)].copy()
                        matched[GroupID_COLUM] = gid
                        wildcard_results.append(matched)
                        # print(f'except;;{wildcard_results}')

        if wildcard_results:
            df_wildcard_results = pd.concat(wildcard_results, ignore_index=True).drop_duplicates()
        else:
            df_wildcard_results = pd.DataFrame(columns=condition_columns)

        print_df(df_wildcard_results, 'All 인 조건 처리 과정 ')

        ######################################## wild Card 가 없는 경우 ################################################
        df_in_CTNGrpConst_temp_normalize = df_in_CTNGrpConst_temp_wide_all.copy().reset_index(drop=True)

        item_s = df_in_CTNGrpConst_temp_wide_all[Item_COLUMN].fillna('').astype(str).str.strip()
        wide_s = df_in_CTNGrpConst_temp_wide_all['is_wildcard'].fillna('').astype(str).str.strip()

        normalize_mask = (
                item_s.ne('')
                & ~item_s.eq('All')
                & ~item_s.str.contains('%', regex=False)
                & wide_s.eq('N')).to_numpy()

        df_in_CTNGrpConst_temp_normalize = df_in_CTNGrpConst_temp_normalize[normalize_mask].copy()

        df_in_CTNGrpConst_temp_normalize = df_in_CTNGrpConst_temp_normalize[
            [Version_COLUMN, Item_COLUMN, GroupID_COLUM]]

        df_in_CTNGrpConst_temp_normalize = df_in_CTNGrpConst_temp_normalize.merge(
            df_final_filtered, on=[Version_COLUMN,Item_COLUMN], how='left')

        print_df(df_in_CTNGrpConst_temp_normalize, 'df_in_CTNGrpConst_temp_normalize_데이터 확인')

        # And 조건 Inner 조인 실행
        # 2025.06.12 수정(by Kang)
        # df_in_CTNGrpConst_temp_wide = final_results.merge(df_wildcard_results, on=condition_columns, how='inner')
        df_in_CTNGrpConst_temp_wide = pd.concat([final_results, df_wildcard_results,df_in_CTNGrpConst_temp_normalize], ignore_index=True)

        print_df(df_in_CTNGrpConst_temp_wide , 'df_in_CTNGrpConst_temp_wide___확인')

        # And 조건을 진행할 데이터 프레임 설정을 위해 인덱스 설정
        key_cols = [GroupID_COLUM]
        if not df_in_CTNGrpConst_temp_wide.empty and all(col in df_in_CTNGrpConst_temp_wide.columns for col in key_cols):
            df_in_CTNGrpConst_temp_wide[key_cols] = df_in_CTNGrpConst_temp_wide[key_cols].astype(str)

        if not df_in_CTNGrpConst_temp_wide_all.empty and all(
                col in df_in_CTNGrpConst_temp_wide_all.columns for col in key_cols):
            df_in_CTNGrpConst_temp_wide_all[key_cols] = df_in_CTNGrpConst_temp_wide_all[key_cols].astype(str)

        if not df_in_CTNGrpConst_temp_wide.empty and all(col in df_in_CTNGrpConst_temp_wide.columns for col in key_cols):
            intersect_keys = set(df_in_CTNGrpConst_temp_wide.set_index(key_cols).index)
        else:
            intersect_keys = set()

        # 와이드 카드 조건에 없는 데이터 프레임만 필터
        df_in_CTNGrpConst_temp_exception = df_in_CTNGrpConst_temp_wide_all[
            ~df_in_CTNGrpConst_temp_wide_all.set_index(key_cols).index.isin(intersect_keys)].copy()

        # 반복을 통해 확장
        for col in df_in_CTNGrpConst_temp_exception[condition_columns]:
            df_in_CTNGrpConst_temp_exception = df_in_CTNGrpConst_temp_exception.explode(col)

        # 머지 및 필터를 위해 데이터 타입 변경
        df_in_CTNGrpConst_temp_exception[condition_columns] = df_in_CTNGrpConst_temp_exception[condition_columns].astype(
            str)
        # 필터 값을 담기 위한 변수 선언
        results_all = []

        for _, cond_row in df_in_CTNGrpConst_temp_exception.iterrows():
            temp_df = df_final_filtered.copy()

            for col in condition_columns:
                cond_val = cond_row[col].strip().lower()

                if cond_val in ['all', '', 'nan']:
                    continue
                temp_df = temp_df[temp_df[col].str.lower() == cond_val]

            if not temp_df.empty:
                temp_df[GroupID_COLUM] = cond_row[GroupID_COLUM]
                results_all.append(temp_df)

        if results_all:
            final_results_all = pd.concat(results_all, ignore_index=True).drop_duplicates()
        else:
            final_results_all = pd.DataFrame(columns=condition_columns)

        df_filtered = pd.concat([final_results_all, df_in_CTNGrpConst_temp_wide], ignore_index=True).drop_duplicates()
        # df_filtered.drop_duplicates(subset=[Version_COLUMN,Item_COLUMN,GroupID_COLUM], ignore_index=True, inplace=True)
        print_df(df_filtered , 'df_filtered  확인1' , True)

        step(400, '=====> STEP 4(End) : Check memory usage & runtime')
        ################################################################################################################
        # Step 5  Except Item 처리
        ###############################################################################################################
        # Except Item에 대한 처리(25.11.14 Kang YS)
        # All 입력된 경우 나머지 입력 조건은 무시하고 All만 처리함.
        ###############################################################################################################
        step(500, '=====> STEP 5(Start) : output data machining')
        df_exception_Item = df_in_CTNGrpConst[
            df_in_CTNGrpConst[
                CTN_Grp_Const_Except_Item].fillna('').astype(str).str.strip().ne('')].copy()
        df_exception_Item = df_exception_Item.rename(columns={CTN_Grp_Const_Except_Item: Item_COLUMN})
        # 아이템 컬럼의 리스트 화
        df_exception_Item[Item_COLUMN] = df_exception_Item[Item_COLUMN].fillna('').astype(str).str.replace("^", ",")
        df_exception_Item[Item_COLUMN] = df_exception_Item[Item_COLUMN].apply(
            lambda x: x.split(',') if isinstance(x, str) else x)
        # 아이템 컬럼의 개수 확인
        df_exception_Item['col_len'] = df_exception_Item[Item_COLUMN].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df_exception_Item_list = df_exception_Item.explode(Item_COLUMN)

        # 와이드 카드 , 'All' 여부를 체크함.
        df_exception_Item_list['is_wildcard'] = np.where(
            df_exception_Item_list[Item_COLUMN].astype(str).str.contains('%', na=False), 'Y', 'N')
        df_exception_Item_list['is_all'] = np.where(
            df_exception_Item_list[Item_COLUMN].astype(str).str.contains('All', na=False), 'Y', 'N')


        print_df(df_exception_Item_list, "[STEP 5]df_exception_Item_list", True)

        ########################### 2026.03.23 ybest7.park 수정 ########################################################

        mask_all = df_exception_Item_list['is_all'].eq('Y')
        mask_item = df_exception_Item_list['is_all'].eq('N') & df_exception_Item_list['col_len'].ge(1)

        df_exception_item_all = df_exception_Item_list[mask_all].copy()
        df_exception_item_wildcard = df_exception_Item_list[mask_item].copy()

        merge_keys = [Version_COLUMN, GroupID_COLUM, Item_COLUMN]
        exclude_rows = []

        if df_exception_item_all.empty and df_exception_item_wildcard.empty:
            final_filtered_wide = pd.DataFrame(columns=df_filtered.columns)
        else:
            # all 인 경우
            if not df_exception_item_all.empty:
                for _, key_row in df_exception_item_all.iterrows():
                    version = key_row[Version_COLUMN]
                    gid = key_row[GroupID_COLUM]

                    mask = (
                            df_filtered[Version_COLUMN].eq(version)
                            & df_filtered[GroupID_COLUM].eq(gid)
                    )

                    matched = df_filtered.loc[mask].copy()

                    if not matched.empty:
                        exclude_rows.append(matched)

            # WildCard
            if not df_exception_item_wildcard.empty:
                s = df_filtered[Item_COLUMN].fillna('').astype(str).str.strip()

                for _, key_row in df_exception_item_wildcard.iterrows():
                    item_value = str(key_row[Item_COLUMN]).strip()
                    version = key_row[Version_COLUMN]
                    gid = key_row[GroupID_COLUM]

                    if not item_value:
                        continue

                    if item_value.startswith('%') and item_value.endswith('%'):
                        token = item_value.strip('%').strip()
                        if not token:
                            continue
                        item_mask = s.str.contains(token, na=False, regex=False)

                    elif item_value.startswith('%'):
                        token = item_value[1:].strip()
                        if not token:
                            continue
                        item_mask = s.str.startswith(token, na=False)

                    elif item_value.endswith('%'):
                        token = item_value[:-1].strip()
                        if not token:
                            continue
                        item_mask = s.str.startswith(token, na=False)

                    else:
                        item_mask = s.eq(item_value)

                    mask = (
                            item_mask
                            & df_filtered[Version_COLUMN].eq(version)
                            & df_filtered[GroupID_COLUM].eq(gid)
                    )

                    matched = df_filtered.loc[mask].copy()

                    if not matched.empty:
                        exclude_rows.append(matched)
            if exclude_rows:
                final_filtered_wide = (
                    pd.concat(exclude_rows, ignore_index=True)
                ).drop_duplicates()
            else:
                final_filtered_wide = pd.DataFrame(columns=df_filtered.columns)

        ########################### 2026.03.23 ybest7.park 수정 ########################################################

        df_exception_Item = final_filtered_wide.copy()

        merge_keys = [Version_COLUMN, GroupID_COLUM, Item_COLUMN]
        # 불필요한 컬럼 정리
        for col in merge_keys:
            if col not in df_exception_Item.columns:
                df_exception_Item[col] = np.nan

        df_exception_Item = df_exception_Item[merge_keys].drop_duplicates()
        df_exception_Item[CTN_Grp_Const_ECP_Flag] = 'True'

        print_df(df_exception_Item , 'df_exception_Item --------------- 확인', True)

        if all(col in df_filtered.columns for col in merge_keys) and all(
                col in df_exception_Item.columns for col in merge_keys):
            df_filtered = df_filtered.merge(df_exception_Item, on=merge_keys, how='left')
        else:
            for col in df_exception_Item.columns:
                if col not in df_filtered.columns:
                    df_filtered[col] = np.nan

        df_filtered[CTN_Grp_Const_ECP_Flag] = df_filtered[CTN_Grp_Const_ECP_Flag].fillna('False')

        df_in_CTNGrpConst_temp_measure = df_in_CTNGrpConst[
            [Version_COLUMN, GroupID_COLUM, CTN_Grp_Const_Apply_Flag, CTN_Grp_Const_Start_Week, CTN_Grp_Const_End_Week,
             CTN_Grp_Const_Frozen_SOP_Qty, CTN_Grp_Const_DP_Qty_from_W0, CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty,
             CTN_Grp_Const_EOH_at_PSI, CTN_Grp_Const_Prod_Result_Qty_before_W0,CTN_Grp_Const_Frozen_Week,
             CTN_Grp_Const_Frozen_SOP_Diff_Qty,CTN_Grp_Const_Frozen_SOP_Override_Qty]]

        measure_merge_keys = [Version_COLUMN, GroupID_COLUM]
        # print_df(df_in_CTNGrpConst_temp_measure, 'df_in_CTNGrpConst_temp_measure ------------> 확인')
        # print_df(df_filtered, 'df_filtered ------------> 확인')

        df_filtered.loc[:,GroupID_COLUM] = df_filtered[GroupID_COLUM].astype(str) # 2026-01-23 merge를 위해 타입 변경 (벤 데이터 프레임 시 ...)

        if all(col in df_filtered.columns for col in measure_merge_keys) and all(
                col in df_in_CTNGrpConst_temp_measure.columns for col in measure_merge_keys):
            df_filtered = df_filtered.merge(df_in_CTNGrpConst_temp_measure, on=measure_merge_keys, how='left')
        else:
            for col in df_in_CTNGrpConst_temp_measure.columns:
                if col not in df_filtered.columns:
                    df_filtered[col] = np.nan

        print_df(df_filtered, "df_filtered 확인 2" , True)
        step(500, '=====> STEP 5(End) : Check memory usage & runtime')
        ################################################################################################################
        # Step 6 (1) Global Top 기준 pivot Test
        ###############################################################################################################
        step(600, '=====> STEP 6(Start) : output data machining')

        # 마지막 생산 실적 비교를 위한 데이터 merge
        PLCMfg_merge_keys = [Version_COLUMN, Item_COLUMN, Location_COLUMN]
        if all(col in df_filtered.columns for col in PLCMfg_merge_keys) and all(
                col in df_in_PLCMfg.columns for col in PLCMfg_merge_keys):
            df_filtered = df_filtered.merge(df_in_PLCMfg, on=PLCMfg_merge_keys, how='left')
        else:
            for col in df_in_PLCMfg.columns:
                if col not in df_filtered.columns:
                    df_filtered[col] = np.nan


        def convert_date_format(date_str):
            if pd.isna(date_str) or str(date_str).lower() == 'nan' or date_str == '':
                return None

            if isinstance(date_str, float) and date_str.is_integer():
                date_str = str(int(date_str))

            if not isinstance(date_str, str):
                date_str = str(date_str)

            date_str = date_str.replace('/', '-').replace('.', '-')

            date_formats = [
                '%Y-%m-%d',  # 2025-03-24
                '%Y%m%d',  # 20250324
                '%m/%d/%Y',  # 03/24/2025
                '%m-%d-%Y',  # 03-24-2025
                '%m-%d-%Y %H:%M:%S',  # 03-24-2025 12:00:00
                '%m/%d/%Y %I:%M:%S %p',  # 03/24/2025 00:00:00 PM
                '%m/%d/%Y %H:%M:%S %p',  # 03/24/2025 00:00:00 PM
            ]
            for fmt in date_formats:
                try:
                    return pd.to_datetime(date_str, format=fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            try:
                return pd.to_datetime(date_str, errors='coerce').strftime('%Y-%m-%d')
            except Exception:
                return date_str


        df_filtered[PLC_Mfg_EOP_Cur_Date] = df_filtered[PLC_Mfg_EOP_Cur_Date].apply(convert_date_format)
        df_filtered[PLC_Mfg_SRA_Com_Date] = df_filtered[PLC_Mfg_SRA_Com_Date].apply(convert_date_format)

        # df_filtered = df_filtered.merge(df_in_PLCMfg, on=[Version_COLUMN, Item_COLUMN, Location_COLUMN], how='left').drop(
        #     columns='Dummy', axis=1)
        df_filtered[PLC_Mfg_EOP_Cur_Date] = pd.to_datetime(df_filtered[PLC_Mfg_EOP_Cur_Date], format='%Y-%m-%d',
                                                           errors='coerce')

        df_filtered[CTN_Grp_Const_Ecp_PLC_SRA_Curr_Week] = pd.to_datetime(df_filtered[PLC_Mfg_SRA_Com_Date],
                                                                          format='%Y-%m-%d',
                                                                          errors='coerce')
        # 기간 비교를 위한 CurrentDay 설정
        df_filtered[Time_Day_COLUMN] = pd.to_datetime(df_in_CurrentDay[Time_Day_COLUMN].iloc[0], errors='coerce')
        # CTN_Grp_Const_Apply_Flag 값 설정
        # 2025.11.12 Apply Flag 체크
        if not df_filtered.empty:
            df_filtered[CTN_Grp_Const_Apply_Flag] = df_filtered.apply(applyCheck, axis=1)

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 주차 정보 딕션어리로 만들기
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정 2025-05-14 (by Kang)
        # df_in_TimeWeek 데이타프레임 컬럼 정리 ,형변환 후 to_dict
        df_in_TimeWeek = df_in_TimeWeek[[Time_Day_COLUMN, Time_Week_COLUMN]].drop_duplicates()
        df_in_TimeWeek[Time_Week_COLUMN] = df_in_TimeWeek[Time_Week_COLUMN].astype(str)
        weed_dict = df_in_TimeWeek.set_index(Time_Day_COLUMN)[Time_Week_COLUMN].to_dict()
        # 딕션어리 주차를 가지고 CTN_Grp_Const_End_Week 생성
        df_filtered[CTN_Grp_Const_End_Week] = df_filtered[PLC_Mfg_EOP_Cur_Date].astype(str).map(weed_dict).fillna(
            '-').astype(str)
        df_filtered[CTN_Grp_Const_Ecp_PLC_SRA_Curr_Week] = df_filtered[PLC_Mfg_SRA_Com_Date].astype(str).map(
            weed_dict).fillna('-').astype(str)
        df_filtered[CTN_Grp_Const_Ecp_PLC_EOP_CURR_WEEK] = df_filtered[PLC_Mfg_EOP_Cur_Date].astype(str).map(
            weed_dict).fillna('-').astype(str)
        # 데이타 정비
        df_in_SalesPlanAP2.drop(columns=Location_COLUMN, inplace=True)
        df_in_SalesPlanAP2.rename(columns={Sub_Location_COLUMN: Location_COLUMN}, inplace=True)

        # df_in_SalesPlanAP2 데이타 집계
        key_column = [Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, Location_COLUMN]
        sum_columns = [Sales_PSI_AP2_W_Shipment, Sales_PSI_AP2_W_Dmd, Sales_PSI_AP2_W_Short, Sales_PSI_AP2_W_EOH]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_SalesPlanAP2 = df_in_SalesPlanAP2.groupby(by=key_column).agg(agg_dict, skipna=True).reset_index()
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # merge를 위한 AP2 Columns Type 변경
        print_df(df_filtered, "df_filtered(715)" , True)
        df_filtered[Sales_Domain_AP2_COLUMN] = df_filtered[Sales_Domain_AP2_COLUMN].astype(str)
        df_in_SalesPlanAP2[Sales_Domain_AP2_COLUMN] = df_in_SalesPlanAP2[Sales_Domain_AP2_COLUMN].astype(str)
        df_in_SalesActualAP2[Sales_Domain_AP2_COLUMN] = df_in_SalesActualAP2[Sales_Domain_AP2_COLUMN].astype(str)

        df_filtered = df_filtered.merge(df_in_SalesPlanAP2.drop(columns=Location_COLUMN, axis=1),
                                        on=[Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN],
                                        how='left')
        df_filtered = df_filtered.drop_duplicates()

        df_filtered[CTN_Grp_Const_Frozen_SOP_Qty] = df_filtered[Sales_PSI_AP2_W_Shipment].fillna(0).astype(int)
        df_filtered[CTN_Grp_Const_DP_Qty_from_W0] = df_filtered[Sales_PSI_AP2_W_Dmd]
        df_filtered[CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty] = df_filtered[Sales_PSI_AP2_W_Short]
        df_filtered[CTN_Grp_Const_EOH_at_PSI] = df_filtered[Sales_PSI_AP2_W_EOH]
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정 : 2025-05-14
        key_column = [Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN]
        sum_columns = [Sales_PSI_AP2_W_Prod]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_SalesActualAP2 = df_in_SalesActualAP2[
            [Version_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, Sales_PSI_AP2_W_Prod]]
        df_in_SalesActualAP2 = df_in_SalesActualAP2.groupby(by=key_column).agg(agg_dict, skipna=True).reset_index()
        df_filtered = df_filtered.merge(df_in_SalesActualAP2, on=key_column, how='left')
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        df_filtered[CTN_Grp_Const_Prod_Result_Qty_before_W0] = df_filtered[Sales_PSI_AP2_W_Prod]
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정 : 2025-05-14 (by Kang)
        df_filtered[CTN_Grp_Const_End_Week] = df_filtered[CTN_Grp_Const_End_Week].fillna('-').astype(str)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        return_col = {Location_COLUMN: CTN_Grp_Const_From_Site, Item_Project_COLUMN: CTN_Grp_Const_Project,
                      Item_Product_GROUP_COLUMN: CTN_Grp_Const_Product_Grp, Item_COLUMN: CTN_Grp_Const_Item,
                      Item_Series_COLUM: CTN_Grp_Const_Series, Item_Inch_COLUM: CTN_Grp_Const_Inch,
                      Item_Year_COLUMN: CTN_Grp_Const_Year}

        df_out_CTNGroupConstraintDetail = df_filtered.copy()
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_Start_Week] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Start_Week].fillna('-').astype(str)
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_End_Week] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_End_Week]
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_Total_SOP_Qty_from_W0] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Frozen_SOP_Qty].fillna(0).astype(int)
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_DP_Qty_from_W0] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_DP_Qty_from_W0].fillna(0).astype(int)
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_Total_SOP_DP_Diff_Qty] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty].fillna(0).astype(int)
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_EOH_at_PSI] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_EOH_at_PSI]
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_Prod_Result_Qty_before_W0] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Prod_Result_Qty_before_W0].fillna(0).astype(int)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정: 2025-05-14 (by Kang)
        df_out_CTNGroupConstraintDetail = df_out_CTNGroupConstraintDetail[
            [Version_COLUMN, GroupID_COLUM, Location_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN,
             CTN_Grp_Const_Ecp_Start_Week, CTN_Grp_Const_Ecp_End_Week,
             CTN_Grp_Const_Ecp_PLC_SRA_Curr_Week, CTN_Grp_Const_Ecp_PLC_EOP_CURR_WEEK,
             CTN_Grp_Const_Ecp_Total_SOP_Qty_from_W0, CTN_Grp_Const_Ecp_DP_Qty_from_W0,
             CTN_Grp_Const_Ecp_Total_SOP_DP_Diff_Qty, CTN_Grp_Const_Ecp_EOH_at_PSI,
             CTN_Grp_Const_Ecp_Prod_Result_Qty_before_W0, CTN_Grp_Const_ECP_Flag]]
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        mg_cols = [CTN_Grp_Const_Ecp_Total_SOP_Qty_from_W0, CTN_Grp_Const_Ecp_DP_Qty_from_W0,
                   CTN_Grp_Const_Ecp_Total_SOP_DP_Diff_Qty, CTN_Grp_Const_Ecp_EOH_at_PSI,
                   CTN_Grp_Const_Ecp_Prod_Result_Qty_before_W0]

        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_Start_Week] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Ecp_Start_Week].fillna("-").astype(str)

        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_End_Week] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Ecp_End_Week].fillna("-").astype(str)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정: 2025-05-14 (by Kang)
        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_PLC_SRA_Curr_Week] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Ecp_PLC_SRA_Curr_Week].fillna("-").astype(str)

        df_out_CTNGroupConstraintDetail[CTN_Grp_Const_Ecp_PLC_EOP_CURR_WEEK] = df_out_CTNGroupConstraintDetail[
            CTN_Grp_Const_Ecp_PLC_EOP_CURR_WEEK].fillna("-").astype(str)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        for col in mg_cols:
            df_out_CTNGroupConstraintDetail[col] = df_out_CTNGroupConstraintDetail[col].fillna(0).astype(int)

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정: 2025-05-14 (by Kang)
        df_out_CTNGroupConstraintDetail = df_out_CTNGroupConstraintDetail.groupby(
            [Version_COLUMN, GroupID_COLUM, Location_COLUMN, Item_COLUMN,
             CTN_Grp_Const_Ecp_Start_Week, CTN_Grp_Const_Ecp_End_Week, CTN_Grp_Const_ECP_Flag,
             CTN_Grp_Const_Ecp_PLC_SRA_Curr_Week, CTN_Grp_Const_Ecp_PLC_EOP_CURR_WEEK])[mg_cols].sum().reset_index()
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # df_out_CTNGroupConstraintDetail.loc[:,CTN_Grp_Const_Except_Item] = True # 2026-03.19 by best7.park (CTN_Grp_Const_Except_Item 값 설정 추가)

        print_df(df_out_CTNGroupConstraintDetail, "df_out_CTNGroupConstraintDetail =================> 확인")
        step(600, '=====> STEP 6(End) : Check memory usage & runtime')

        ################################################################################################################
        # Step 7 (1) Global Top 기준 pivot Test
        ###############################################################################################################
        step(700, '=====> STEP 7(Start) : output data machining')
        df_filtered_temp = df_filtered[df_filtered[CTN_Grp_Const_ECP_Flag] != 'Y']
        # df_filtered_temp[CTN_Grp_Const_EOP_MAX] = df_filtered_temp[CTN_Grp_Const_End_Week]
        print_df(df_filtered_temp, "df_filtered_temp ----- 임시확인",True)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정: 2025-05-14 (by Kang) - 2026.03.11 CTN Grp Const_End Week 삭제 (by ybest7)
        key_column = [Version_COLUMN, GroupID_COLUM]
        sum_columns = [Sales_PSI_AP2_W_Prod,]
        agg_dict = {CTN_Grp_Const_Start_Week: 'max',
                    CTN_Grp_Const_DP_Qty_from_W0: 'sum',
                    CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty: 'sum',
                    CTN_Grp_Const_EOH_at_PSI: 'sum',
                    CTN_Grp_Const_Prod_Result_Qty_before_W0: 'sum',
                    CTN_Grp_Const_Frozen_SOP_Qty: 'sum',
                    CTN_Grp_Const_Apply_Flag: 'max',
                    CTN_Grp_Const_Frozen_Week : 'max',
                    CTN_Grp_Const_Frozen_SOP_Diff_Qty :'sum',
                    CTN_Grp_Const_Frozen_SOP_Override_Qty : 'max'}
        df_out_CTNGroupConstraint = df_filtered_temp.groupby(by=key_column).agg(agg_dict, skipna=True).reset_index()

        # print_df(df_out_CTNGroupConstraint, 'df_out_CTNGroupConstraint_데이터 확인',True)

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 추가 : 2026-01-22 (by : ybest7.park(박병훈))
        # df_out_CTNGroupConstraint[CTN_Grp_Const_EOP_MAX] = df_out_CTNGroupConstraint[CTN_Grp_Const_End_Week]
        # flag가 'N' 이면 Null로 값 설정
        null_cols = [
            CTN_Grp_Const_Frozen_Week,
            CTN_Grp_Const_Start_Week,
            CTN_Grp_Const_Frozen_SOP_Qty,
            CTN_Grp_Const_Frozen_SOP_Diff_Qty,
            CTN_Grp_Const_Frozen_SOP_Override_Qty]

        # mask 설정
        m = df_out_CTNGroupConstraint[CTN_Grp_Const_Apply_Flag].eq('N')
        # CTN_Grp_Const_Apply_Flag 값이 'N" 이면 null_cols는 모두 null로 변환, 아니면 기존 값 유지
        df_out_CTNGroupConstraint.loc[m, null_cols] = pd.NA

        print_df(df_out_CTNGroupConstraint, "df_out_CTNGroupConstraint ================ 확인", True)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        step(700, '=====> STEP 7(End) : Check memory usage & runtime')
        ################################################################################################################
        # Step 8. (1) 최종 Out_Put Save
        ################################################################################################################
        step(800, '=====> STEP 8(Start) : output data machining')

        row_count, col_count = df_out_CTNGroupConstraintDetail.shape
        note(f'=====> Final df_out_CTNGroupConstraintDetail rows : {row_count} , Columns : {col_count}')
        row_count, col_count = df_out_CTNGroupConstraint.shape
        note(f'=====> Final df_out_CTNGroupConstraint rows : {row_count} , Columns : {col_count}')
        print_df(df_out_CTNGroupConstraintDetail, 'df_out_CTNGroupConstraintDetail_last', True)
        print_df(df_out_CTNGroupConstraint, 'df_out_CTNGroupConstraint_last', True)

        # row_count, col_count = df_out_CTNItemConst.shape
        # note(f'=====> Final df_out_CTNItemConst rows : {row_count} , Columns : {col_count}')
        if is_local:
            note(f'=====> <Local>Final output table create')
            # 수정 : 2025-05-14
            save_csv_file(df_out_CTNGroupConstraint, 'Fact.df_out_CTNGroupConstraint_Last')
            save_csv_file(df_out_CTNGroupConstraintDetail, 'Fact.df_out_CTNGroupConstraintDetail_Last')
            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        step(800, '=====> STEP 8(End) : Check memory usage & runtime')

    except Exception as e:
        trace_msg = traceback.format_exc()
        note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
        Logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        df_out_CTNGroupConstraintDetail = pd.DataFrame([], columns=[])
        df_out_CTNGroupConstraint = pd.DataFrame([], columns=[])
        # df_out_CTNItemConst = pd.DataFrame([], columns=[])
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
