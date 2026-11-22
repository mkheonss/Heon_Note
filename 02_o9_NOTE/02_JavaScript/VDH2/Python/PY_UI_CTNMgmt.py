

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
-. 2026.03.31
    - df_in_BODItem input Query 수정
-. 2026.04.01
    - 전체적인 수정 (검색조건 수정)
-. 2026.04.03
    - CTN Grp Const Ecp_PLC EOP Curr Week 의 Max를 CTN Grp Const_EOP MAX 로 생성
-. 2026.04.13
   - AP2, GC 관련 데이터 삭제 df_in_SalesItem ,df_in_PLCMfg ,df_in_CurrentDay,df_in_TimeWeek 데이터 프레임 삭제




* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary


* Input Table
   - df_in_CTNGrpConst = Select ([Version].[Version Name] * [Group].[Group ID].filter(#.Name startswith "MCT_") ) on row,({Measure.[CTN Grp Const_From Site ID], Measure.[CTN Grp Const_GC Code], Measure.[CTN Grp Const_AP2 Code], Measure.[CTN Grp Const_Product Grp], Measure.[CTN Grp Const_Product], Measure.[CTN Grp Const_Project], Measure.[CTN Grp Const_Series], Measure.[CTN Grp Const_MKT Name], Measure.[CTN Grp Const_Inch], Measure.[CTN Grp Const_Item CTN Attr], Measure.[CTN Grp Const_Year], Measure.[CTN Grp Const_Item], Measure.[CTN Grp Const_Except Item], Measure.[CTN Grp Const_Frozen Week], Measure.[CTN Grp Const_Start Week], Measure.[CTN Grp Const_End Week], Measure.[CTN Grp Const_Apply Flag], Measure.[CTN Grp Const_DP Qty from W0], Measure.[CTN Grp Const_Frozen SOP Qty],Measure.[CTN Grp Const_Frozen SOP DP Diff Qty],Measure.[CTN Grp Const_EOH at PSI], Measure.[CTN Grp Const_Prod Result Qty before W0],Measure.[CTN Grp Const_Frozen SOP Diff Qty],Measure.[CTN Grp Const_Frozen SOP Override Qty], Measure.[Dummy] }) on column;
   - df_in_BODItem = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Sub Location].[Sub Location] * [Sub Location].[Sub Location GC] *[Sub Location].[Sub Location Rep AP2]* [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Asn], Measure.[Dummy]}) on column Where {Measure.[BOD Item_asn] == 1 ,(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE"}),(coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now())};
   # - df_in_SalesItem = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Sales Domain].[GC] * [Sales Domain].[AP2] ) on row,({Measure.[Sales Item Asn_Valid Flag]}) on column Where {Measure.[Sales Item Asn_Valid Flag] == "true"};
   # - df_in_PLCMfg =  Select ([Version].[Version Name] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Location].[Location] ) on row, ({Measure.[PLC Mfg_EOP Cur Date],Measure.[PLC Mfg_SRA Com Date] , Measure.[Dummy]}) on column;
   - df_in_SalesPlanAP2 =  Select ([Version].[Version Name] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales PSI AP2 W_Shipment], Measure.[Sales PSI AP2 W_Dmd], Measure.[Sales PSI AP2 W_Short], Measure.[Sales PSI AP2 W_EOH], Measure.[Sales PSI AP2 W_Prod], Measure.[Dummy]}) on column ;
   # - df_in_SalesActualAP2 =  Select ([Version].[Version Name] * [Item].[Item] * [Item].[Year] * [Item].[CTN] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Series Name]* [Item].[Project] * [Item].[Product] * [Item].[Product Group] * [Time].[Week] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales PSI AP2 W_Prod], Measure.[Dummy]}) on column;
   # - df_in_CurrentDay = Select (&CurrentDay);
   # - df_in_TimeWeek = select ([Time].[Day] * [Time].[Week] );
   # - df_in_CTNItemConst = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Apply Flag], Measure.[CTN Item Const_Created By], Measure.[CTN Item Const_Creation Time], Measure.[CTN Item Const_DP Qty from W0], Measure.[CTN Item Const_EOH at PSI], Measure.[CTN Item Const_End Week], Measure.[CTN Item Const_Frozen SOP DP Diff Qty], Measure.[CTN Item Const_Frozen SOP Diff Qty], Measure.[CTN Item Const_Frozen SOP Override Qty], Measure.[CTN Item Const_Frozen SOP Override Reason], Measure.[CTN Item Const_Frozen SOP Override Remain Qty], Measure.[CTN Item Const_Frozen SOP Qty], Measure.[CTN Item Const_Frozen Week], Measure.[CTN Item Const_Prod Result Qty before W0], Measure.[CTN Item Const_Start Week], Measure.[CTN Item Const_Update Time], Measure.[CTN Item Const_Updated By], Measure.[Dummy]}) on column;
   # - df_in_ItemBuyer = Select([Item].[Item]*[Item].[Buyer]) ;

* 데이터 삭제
    DELETE DATA FOR MODEL [CTN Grp Const Ecp] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [CTN Grp Const Ecp] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_CTNGroupConstraintDetail = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] * [Sequence].[Sequence] * [Group].[Group ID].[MCT_00001] ) on row, ({Measure.[CTN Grp Const Ecp_Created By], Measure.[CTN Grp Const Ecp_Creation Time], Measure.[CTN Grp Const Ecp_DP Qty from W0], Measure.[CTN Grp Const Ecp_EOH at PSI], Measure.[CTN Grp Const Ecp_Ecp Flag], Measure.[CTN Grp Const Ecp_End Week], Measure.[CTN Grp Const Ecp_PLC EOP Curr Week], Measure.[CTN Grp Const Ecp_PLC SRA Curr Week], Measure.[CTN Grp Const Ecp_Prod Result Qty before W0], Measure.[CTN Grp Const Ecp_Start Week], Measure.[CTN Grp Const Ecp_Total SOP DP Diff Qty], Measure.[CTN Grp Const Ecp_Total SOP Qty from W0], Measure.[CTN Grp Const Ecp_Update Time], Measure.[CTN Grp Const Ecp_Updated By]}) on column;
    - df_out_CTNGroupConstraint = Select ([Version].[Version Name].[CWV_MP] * [Group].[Group ID]) on row, ({Measure.[CTN Grp Const_Frozen Week],Measure.[CTN Grp Const_Start Week],Measure.[CTN Grp Const_End Week],Measure.[CTN Grp Const_Frozen SOP Qty],Measure.[CTN Grp Const_Frozen SOP Override Qty],Measure.[CTN Grp Const_Frozen SOP Diff Qty], Measure.[CTN Grp Const_EOP MAX]}) on column;
    # - df_out_CTNItemConst = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] ) on row, ({Measure.[CTN Item Const_Apply Flag], Measure.[CTN Item Const_Created By], Measure.[CTN Item Const_Creation Time], Measure.[CTN Item Const_DP Qty from W0], Measure.[CTN Item Const_EOH at PSI], Measure.[CTN Item Const_End Week], Measure.[CTN Item Const_Frozen SOP DP Diff Qty], Measure.[CTN Item Const_Frozen SOP Diff Qty], Measure.[CTN Item Const_Frozen SOP Override Qty], Measure.[CTN Item Const_Frozen SOP Override Reason], Measure.[CTN Item Const_Frozen SOP Override Remain Qty], Measure.[CTN Item Const_Frozen SOP Qty], Measure.[CTN Item Const_Frozen Week], Measure.[CTN Item Const_Prod Result Qty before W0], Measure.[CTN Item Const_Start Week], Measure.[CTN Item Const_Update Time], Measure.[CTN Item Const_Updated By]}) on column;

    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    {EXEC plugin instance [PY_UI_CTNMgmt] for measures {[CTN Grp Const_From Site]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;}


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

            df_in_CTNGrpConst = read_csv_file('df_in_CTNGrpConst_H2')
            df_in_BODItem = read_csv_file('df_in_BODItem_H2')
            # df_in_SalesItem = read_csv_file('df_in_SalesItem_H2')
            # df_in_PLCMfg = read_csv_file('df_in_PLCMfg_H2')
            df_in_SalesPlanAP2 = read_csv_file('df_in_SalesPlanAP2_H2')
            # df_in_SalesActualAP2 = read_csv_file('df_in_SalesActualAP2_EX')
            # df_in_CurrentDay = read_csv_file('df_in_CurrentDay_H2')
            # df_in_TimeWeek = read_csv_file('df_in_TimeWeek_H2')

        print_df(df_in_CTNGrpConst, 'df_in_CTNGrpConst',True)
        print_df(df_in_BODItem, 'df_in_BODItem',False)
        # print_df(df_in_SalesItem, 'df_in_SalesItem',False)
        # print_df(df_in_PLCMfg, 'df_in_PLCMfg',False)
        print_df(df_in_SalesPlanAP2, 'df_in_SalesPlanAP2',False)
        # print_df(df_in_SalesActualAP2, 'df_in_SalesActualAP2',False)
        # print_df(df_in_CurrentDay, 'df_in_CurrentDay',False)
        # print_df(df_in_TimeWeek, 'df_in_TimeWeek',False)

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
        PLC_Mfg_SRA_Com_Override_Date = 'PLC Mfg_SRA Com Override Date'



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

        # Null로 데이터 프레임이 입력 시 Test
        # df_in_CTNGrpConst = df_in_CTNGrpConst.head(0)
        # df_in_SalesPlanAP2 =  df_in_SalesPlanAP2.head(0)

        ############################################## 2026.03.11 (ybest7.park 수정) ###################################
        # 불필요한 컬럼 지정
        drop_cols = [Item_Product_GROUP_COLUMN, Item_Product_COLUMN,Item_Project_COLUMN,Item_Series_Name_COLUM,
                     Item_Marketing_Name_COLUM,Item_Inch_COLUM,Item_CTN_COLUM,Item_Year_COLUMN]

        # 데이터 프레임 drop_cols 삭제
        for df in [df_in_SalesPlanAP2] :
            df.drop(columns=drop_cols, errors='ignore', axis=1, inplace=True)

        df_in_SalesActualAP2 = df_in_SalesPlanAP2.copy()

        ############################################## 2026.03.11 (ybest7.park 수정 완료) #################################


        # df_in_CTNGrpConst = df_in_CTNGrpConst.head(0)

        # df_in_BODItem 중복 제거 및 필터링
        df_in_BODItem_temp = df_in_BODItem[
            [Version_COLUMN, Item_COLUMN, Item_Product_GROUP_COLUMN, Item_Product_COLUMN, Item_Project_COLUMN,
             Item_Series_Name_COLUM, Item_Marketing_Name_COLUM, Item_Inch_COLUM, Item_CTN_COLUM, Item_Year_COLUMN,
             Location_COLUMN]].drop_duplicates().copy()

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


        step(300, '=====> STEP 3(End) : Check memory usage & runtime')

        ################################################################################################################
        # Step 4 (1) Global Top 기준 pivot Test
        ###############################################################################################################
        step(400, '=====> STEP 4(Start) : output data machining')

        # 조건을 찾기 위한 컬럼 설정
        # Location_COLUMN 추가함.(2025-06-12)
        condition_columns = [
            Version_COLUMN, Item_COLUMN, Location_COLUMN, Item_Product_GROUP_COLUMN, Item_Product_COLUMN,
            Item_Project_COLUMN, Item_Series_Name_COLUM, Item_Marketing_Name_COLUM, Item_Inch_COLUM,
            Item_CTN_COLUM, Item_Year_COLUMN]

        # 와이드 카드 분리를 위한 데이터 프레임 복사
        df_in_CTNGrpConst_temp_wide_all = df_in_CTNGrpConst_temp.copy()

        # 조건의 멀티 값 확장을 위한 리스트로 변환
        # 2025.06.12(by Kang) : Wild 입력시 구분자(^)을 코마(,)로 대체함.
        # 2025.09.10(by Kang Y.S) : 화면 EW 전환시 구분자 ^로만 들어옴.
        # df_in_CTNGrpConst_temp_wide_all[Item_COLUMN] = df_in_CTNGrpConst_temp_wide_all[Item_COLUMN].str.replace("^",",")
        df_in_CTNGrpConst_temp_wide_all[condition_columns] = df_in_CTNGrpConst_temp_wide_all[condition_columns].applymap(
            lambda x: re.split(r'\s*[,^]\s*',x) if isinstance(x,str) else x)
        # Item column의 개수를 확인
        # df_in_CTNGrpConst_temp_wide_all['col_len'] = df_in_CTNGrpConst_temp_wide_all[Item_COLUMN].apply(
        #     lambda x: len(x) if isinstance(x, list) else 0)

        for col in df_in_CTNGrpConst_temp_wide_all[condition_columns]:
            df_in_CTNGrpConst_temp_wide_all = df_in_CTNGrpConst_temp_wide_all.explode(col)

        df_in_CTNGrpConst_temp_wide_all = df_in_CTNGrpConst_temp_wide_all.copy().reset_index(drop=True)

        # 비교 대상에 대한 데이터 정리
        att_work = (
            df_in_CTNGrpConst_temp_wide_all[condition_columns]
            .fillna('')
            .astype(str)
            .apply(lambda s: s.str.strip()))

        # wild Card 가 있는 값
        df_in_CTNGrpConst_temp_wide_all['ATTR_WILD_YN'] = (att_work.apply(
            lambda s : s.str.contains('%', regex=False, na=False))
            .any(axis=1)
            .map({True : 'Y', False : 'N'}))

        # All 이 포함된 것 구분하기
        df_in_CTNGrpConst_temp_wide_all['ATTR_ALL_YN'] = att_work.apply(
            lambda r: 'Y' if r.eq('All').any() else 'N', axis=1)

        # All & Wild Card가 없는 것 분리
        df_in_CTNGrpConst_temp_wide_all['ATTR_EXACT_YN'] = (
            (
                    df_in_CTNGrpConst_temp_wide_all['ATTR_WILD_YN'].eq('N')
                    & df_in_CTNGrpConst_temp_wide_all['ATTR_ALL_YN'].eq('N')
            )
            .map({True: 'Y', False: 'N'})
        )

        print_df(df_in_CTNGrpConst_temp_wide_all, 'df_in_CTNGrpConst_temp_wide_all__확인')

        # merge를 통해 아이템을 찾을 수 있는 데이터 프레임
        df_attr_exact = df_in_CTNGrpConst_temp_wide_all.loc[
            df_in_CTNGrpConst_temp_wide_all['ATTR_EXACT_YN'].eq('Y')].copy()

        print_df(df_attr_exact, 'df_attr_exact_확인' )


        # Wild Card를 통해 찾아야 하는 데이터 프레임
        df_attr_wild = df_in_CTNGrpConst_temp_wide_all.loc[
            df_in_CTNGrpConst_temp_wide_all['ATTR_WILD_YN'].eq('Y')].copy()

        print_df(df_attr_wild, 'df_attr_wildt_확인')


        # All 을 통해 찾아야 하는 데이터 프레임
        df_attr_all = df_in_CTNGrpConst_temp_wide_all.loc[
            (df_in_CTNGrpConst_temp_wide_all['ATTR_WILD_YN'].eq('N'))
            & (df_in_CTNGrpConst_temp_wide_all['ATTR_ALL_YN'].eq('Y'))].copy()

        print_df(df_attr_all, 'df_attr_all_확인')


        ################################################################################################################
        # exact_item item 을 기준으로 Group ID 찾기
        ################################################################################################################
        df_attr_exact = df_attr_exact.copy()

        final_results_exact = (
            df_attr_exact.merge(
                df_in_BODItem_temp, on=list(condition_columns), how='left'
            )
        )

        final_results_exact = final_results_exact[condition_columns + [GroupID_COLUM]].copy()

        print_df(final_results_exact, 'final_results_exact 확인')
        ################################################################################################################
        # widecard item 을 기준으로 Group ID 찾기
        ################################################################################################################

        # Wild Card 만 비교
        result_wildcard = []

        if not df_attr_wild.empty:
            for _, cond_row in df_attr_wild.iterrows():
                temp_df = df_in_BODItem_temp.copy()

                # ----------------------------------------------------------------------------------------
                # 1) Item 조건
                #    -. item 이 All 이면 Skip
                #    -. % 있으면 Wildcard 비교
                #    -. 아니면 Exact 비교
                # ----------------------------------------------------------------------------------------
                if Item_COLUMN in df_attr_wild.columns and Item_COLUMN in temp_df.columns:
                    item_val = str(cond_row[Item_COLUMN]).strip()

                    if item_val not in ['', 'All', 'nan']:
                        item_col = (
                            temp_df[Item_COLUMN]
                            .fillna('')
                            .astype(str)
                            .str.strip()
                        )

                        if item_val.startswith('%') and item_val.endswith('%'):
                            token = item_val.strip('%').strip()
                            if not token:
                                continue
                            temp_df = temp_df.loc[
                                item_col.str.contains(token, na=False, regex=False)
                            ].copy()

                        elif item_val.startswith('%'):
                            token = item_val[1:].strip()
                            if not token:
                                continue
                            temp_df = temp_df.loc[
                                item_col.str.endswith(token, na=False)
                            ].copy()

                        elif item_val.endswith('%'):
                            token = item_val[:-1].strip()
                            if not token:
                                continue
                            temp_df = temp_df.loc[
                                item_col.str.startswith(token, na=False)
                            ].copy()

                        else:
                            temp_df = temp_df.loc[
                                item_col.eq(item_val)
                            ].copy()

                if temp_df.empty:
                    continue

                # ----------------------------------------------------------------------------------------
                # 2) Attribute 조건
                #    -. All 이면 Skip
                #    -. % 있으면 Wildcard 비교
                #    -. 아니면 Exact 비교
                # ----------------------------------------------------------------------------------------
                for col in condition_columns:
                    if col not in df_attr_wild.columns and col not in temp_df.columns:
                        continue

                    cond_val = str(cond_row[col]).strip()

                    if cond_val in ['', 'All', 'nan']:
                        continue

                    temp_col = (
                        temp_df[col]
                        .fillna('')
                        .astype(str)
                        .str.strip())

                    if cond_val.startswith('%') and cond_val.endswith('%'):
                        token = cond_val.strip('%').strip()
                        if not token:
                            continue
                        temp_df = temp_df.loc[
                            temp_col.str.contains(token, na=False, regex=False)
                        ].copy()

                    elif cond_val.startswith('%'):
                        token = cond_val[1:].strip()
                        if not token:
                            continue
                        temp_df = temp_df.loc[
                            temp_col.str.endswith(token, na=False)
                        ].copy()

                    elif cond_val.endswith('%'):
                        token = cond_val[:-1].strip()
                        if not token:
                            continue
                        temp_df = temp_df.loc[
                            temp_col.str.startswith(token, na=False)
                        ].copy()

                    else:
                        temp_df = temp_df.loc[
                            temp_col.eq(cond_val)
                        ].copy()

                    if temp_df.empty:
                        break

                # ----------------------------------------------------------------------------------------
                # 3) Group ID 부여
                #    -. Group_id 는 조건표 (Corn_row)에서만 가져옴
                # ----------------------------------------------------------------------------------------
                if not temp_df.empty:
                    temp_df = temp_df.copy()
                    temp_df[GroupID_COLUM] = cond_row[GroupID_COLUM]
                    result_wildcard.append(temp_df)

        if result_wildcard:
            final_results_wildcard = (
                pd.concat(result_wildcard, ignore_index=True)
                .drop_duplicates()
            )
        else:
            final_results_wildcard = pd.DataFrame(
                columns=list(df_in_BODItem_temp.columns) + [GroupID_COLUM]
            )

        print_df(final_results_wildcard, 'final_results_wildcard 확인')

        ################################################################################################################
        # All 인 item 을 기준으로 Group ID 찾기
        ################################################################################################################
        # All 인 경우 필터링

        result_all = []

        if not df_attr_all.empty:
            for _, cond_row in df_attr_all.iterrows():
                temp_df = df_in_BODItem_temp

                # ----------------------------------------------------------------------------------------
                #    -. item 이 All 이면 Skip
                #    -. % 있으면 Wildcard 비교
                #    -. 아니면 Exact 비교
                # ----------------------------------------------------------------------------------------

                if Item_COLUMN in df_attr_all.columns and Item_COLUMN in temp_df.columns:
                    item_val = str(cond_row[Item_COLUMN]).strip()

                    if item_val in ['', 'All', 'nan']:
                        item_col = (
                            temp_df[Item_COLUMN]
                            .fillna('')
                            .astype(str)
                            .str.strip()
                        )

                        if item_val.startswith('%') and item_val.endswith('%'):
                            token = item_val.strip('%').strip()
                            if not token:
                                continue
                            temp_df = temp_df.loc[
                                item_col.str.contains(token, na=False, regex=False)
                            ].copy()

                        elif item_val.startswith('%'):
                            token = item_val[1:].strip()
                            if not token:
                                continue
                            temp_df = temp_df.loc[
                                item_col.str.endswith(token, na=False)
                            ].copy()

                        elif item_val.endswith('%'):
                            token = item_val[:-1].strip()
                            if not token:
                                continue
                            temp_df = temp_df.loc[
                                item_col.str.startswith(token, na=False)
                            ].copy()

                        else:
                            temp_df = temp_df.loc[
                                item_col.eq(item_val)
                            ].copy()

                if temp_df.empty:
                    continue

                # ----------------------------------------------------------------------------------------
                # 2) Attribute 조건
                #    -. All 이면 Skip
                #    -. % 있으면 Wildcard 비교
                #    -. 아니면 Exact 비교
                # ----------------------------------------------------------------------------------------

                for col in condition_columns:
                    if col not in df_attr_all.columns and col not in temp_df.columns:
                        continue

                    cond_val = str(cond_row[col]).strip()

                    if cond_val in ['', 'All', 'nan']:
                        continue

                    temp_col = (
                        temp_df[col]
                        .fillna('')
                        .astype(str)
                        .str.strip())

                    temp_df = temp_df.loc[
                        temp_col.eq(cond_val)
                    ].copy()

                    if temp_df.empty:
                        break

                # ----------------------------------------------------------------------------------------
                # 3) Group ID 부여
                #    -. Group_id 는 조건표 (Corn_row)에서만 가져옴
                # ----------------------------------------------------------------------------------------
                if not temp_df.empty:
                    temp_df = temp_df.copy()
                    temp_df[GroupID_COLUM] = cond_row[GroupID_COLUM]
                    result_all.append(temp_df)

        if result_all:
            final_results_all = (
                pd.concat(result_all, ignore_index=True)
                .drop_duplicates()
            )
        else:
            final_results_all = pd.DataFrame(
                columns=list(df_in_BODItem_temp.columns) + [GroupID_COLUM]
            )

        print_df(final_results_all, 'final_results_all 확인')

        ################################################################################################################
        # 최종 결과
        ################################################################################################################
        final_results_exclude = (
            pd.concat(
                [final_results_exact, final_results_wildcard, final_results_all],
                ignore_index=True
            ).drop_duplicates()
        )

        df_filtered = final_results_exclude.copy()
        df_filtered = df_filtered[condition_columns + [GroupID_COLUM]]
        print_df(df_filtered, 'df_filtered  확인1', True)

        step(400, '=====> STEP 4(End) : Check memory usage & runtime')
        ################################################################################################################
        # Step 5  Except Item 처리
        ###############################################################################################################
        # Except Item에 대한 처리(25.11.14 Kang YS)
        # All 입력된 경우 나머지 입력 조건은 무시하고 All만 처리함.
        ###############################################################################################################
        step(500, '=====> STEP 5(Start) : output data machining')
        df_exception_Item = df_in_CTNGrpConst_temp_wide_all[
            [Version_COLUMN, GroupID_COLUM, CTN_Grp_Const_Except_Item]].rename(
            columns={CTN_Grp_Const_Except_Item: Item_COLUMN}
        ).drop_duplicates().copy()

        exception_merge_col = [Version_COLUMN, GroupID_COLUM, Item_COLUMN]

        # -------------------------------------------------------------------------------------------
        # 1 exact / wildcard 분리
        # -------------------------------------------------------------------------------------------
        item_s = (df_exception_Item[Item_COLUMN]
                  .fillna('')
                  .astype(str)
                  .str.strip())

        item_exact_mask = (
                item_s.ne('')
                & ~ item_s.str.contains('%', regex=False, na=False)
        )

        item_wildcard_mask = (
                item_s.ne('')
                & item_s.str.contains('%', regex=False).eq(False)
        )

        df_exception_Item_exact = df_exception_Item.loc[item_exact_mask].copy()
        df_exception_Item_wildcard = df_exception_Item.loc[item_wildcard_mask].copy()

        # -------------------------------------------------------------------------------------------
        # 2 exact item 찾기
        # -------------------------------------------------------------------------------------------
        if df_exception_Item_exact.empty:
            final_results_item = pd.DataFrame(columns=exception_merge_col)

        else:
            final_results_item = (
                df_exception_Item_exact.merge(
                    df_filtered[exception_merge_col].drop_duplicates(),
                    on=exception_merge_col, how='left'
                ))

        # -------------------------------------------------------------------------------------------
        # 3 wildcard item 찾기
        # -------------------------------------------------------------------------------------------
        results_wildcard = []

        if not df_exception_Item_wildcard.empty:
            for _, cond_row in df_exception_Item_wildcard.iterrows():

                temp_df = df_filtered.loc[df_filtered[GroupID_COLUM].eq(cond_row[GroupID_COLUM])].copy()
                temp_df = temp_df[exception_merge_col].drop_duplicates().reset_index(drop=True)

                if temp_df.empty:
                    continue

                item_Val = str(cond_row[Item_COLUMN]).strip()

                if item_val.startswith('%') and item_val.endswith('%'):
                    token = item_val.strip('%').strip()
                    if not token:
                        continue

                    temp_df = temp_df.loc[
                        temp_df[Item_COLUMN]
                        .fillna('')
                        .astype(str)
                        .str.strip()
                        .str.contains(token, na=False, regex=False)
                    ].copy()

                elif item_val.startswith('%'):
                    token = item_val[1:].strip()
                    if not token:
                        continue

                    temp_df = temp_df.loc[
                        temp_df[Item_COLUMN]
                        .fillna('')
                        .astype(str)
                        .str.strip()
                        .str.endswith(token, na=False, regex=False)
                    ].copy()

                elif item_val.endswith('%'):
                    token = item_val[:-1].strip()
                    if not token:
                        continue

                    temp_df = temp_df.loc[
                        temp_df[Item_COLUMN]
                        .fillna('')
                        .astype(str)
                        .str.strip()
                        .str.startswith(token, na=False, regex=False)
                    ].copy()

                else:
                    tem_df = temp_df.loc[
                        temp_df[Item_COLUMN]
                        .fillna('')
                        .astype(str)
                        .str.strip()
                        .eq(item_val)
                    ].copy()

                if not temp_df.empty:
                    result_wildcard.append(temp_df)

        if results_wildcard:
            final_results_wildcard = (
                pd.concat(result_wildcard, ignore_index=True)
            )

        else:
            final_results_wildcard = pd.DataFrame(columns=exception_merge_col)

        df_exception_Item = (
            pd.concat([final_results_item, final_results_wildcard], ignore_index=True)
        )

        df_exception_Item[CTN_Grp_Const_ECP_Flag] = 'True'


        #
        # merge_keys = [Version_COLUMN, GroupID_COLUM, Item_COLUMN]
        # # 불필요한 컬럼 정리
        # for col in merge_keys:
        #     if col not in df_exception_Item.columns:
        #         df_exception_Item[col] = np.nan
        #
        # df_exception_Item = df_exception_Item[merge_keys].drop_duplicates()
        # df_exception_Item[CTN_Grp_Const_ECP_Flag] = 'True'

        print_df(df_exception_Item , 'df_exception_Item --------------- 확인', True)

        if all(col in df_filtered.columns for col in exception_merge_col) and all(
                col in df_exception_Item.columns for col in exception_merge_col):
            df_filtered = df_filtered.merge(df_exception_Item, on=exception_merge_col, how='left')
        else:
            for col in df_exception_Item.columns:
                if col not in df_filtered.columns:
                    df_filtered[col] = np.nan

        # print_df(df_exception_Item, 'df_exception_Item --------------- 확인1', True)
        df_filtered[CTN_Grp_Const_ECP_Flag] = df_filtered[CTN_Grp_Const_ECP_Flag].fillna('False')

        df_in_CTNGrpConst_temp_measure = df_in_CTNGrpConst[
            [Version_COLUMN, GroupID_COLUM, CTN_Grp_Const_Apply_Flag, CTN_Grp_Const_Start_Week, CTN_Grp_Const_End_Week,
             CTN_Grp_Const_Frozen_SOP_Qty, CTN_Grp_Const_DP_Qty_from_W0, CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty,
             CTN_Grp_Const_EOH_at_PSI, CTN_Grp_Const_Prod_Result_Qty_before_W0,CTN_Grp_Const_Frozen_Week,
             CTN_Grp_Const_Frozen_SOP_Diff_Qty,CTN_Grp_Const_Frozen_SOP_Override_Qty]]

        measure_merge_keys = [Version_COLUMN, GroupID_COLUM]
        # print_df(df_in_CTNGrpConst_temp_measure, 'df_in_CTNGrpConst_temp_measure ------------ 확인')
        # print_df(df_filtered, 'df_filtered ------------ 확인')

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

        # 데이타 정비
        df_in_SalesPlanAP2.drop(columns=Location_COLUMN, inplace=True)
        df_in_SalesPlanAP2.rename(columns={Sub_Location_COLUMN: Location_COLUMN}, inplace=True)

        # df_in_SalesPlanAP2 데이타 집계
        key_column = [Version_COLUMN, Item_COLUMN, Location_COLUMN]
        sum_columns = [Sales_PSI_AP2_W_Shipment, Sales_PSI_AP2_W_Dmd, Sales_PSI_AP2_W_Short, Sales_PSI_AP2_W_EOH]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_SalesPlanAP2 = df_in_SalesPlanAP2.groupby(by=key_column).agg(agg_dict, skipna=True).reset_index()
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # merge를 위한 AP2 Columns Type 변경
        df_filtered = df_filtered.merge(df_in_SalesPlanAP2.drop(columns=Location_COLUMN, axis=1),
                                        on=[Version_COLUMN, Item_COLUMN],
                                        how='left')
        df_filtered = df_filtered.drop_duplicates()

        df_filtered[CTN_Grp_Const_Frozen_SOP_Qty] = df_filtered[Sales_PSI_AP2_W_Shipment].fillna(0).astype(int)
        df_filtered[CTN_Grp_Const_DP_Qty_from_W0] = df_filtered[Sales_PSI_AP2_W_Dmd]
        df_filtered[CTN_Grp_Const_Frozen_SOP_DP_Diff_Qty] = df_filtered[Sales_PSI_AP2_W_Short]
        df_filtered[CTN_Grp_Const_EOH_at_PSI] = df_filtered[Sales_PSI_AP2_W_EOH]
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정 : 2025-05-14
        key_column = [Version_COLUMN, Item_COLUMN]
        sum_columns = [Sales_PSI_AP2_W_Prod]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_SalesActualAP2 = df_in_SalesActualAP2[
            [Version_COLUMN, Item_COLUMN,  Sales_PSI_AP2_W_Prod]]
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
            [Version_COLUMN, GroupID_COLUM, Location_COLUMN, Item_COLUMN,
             CTN_Grp_Const_Ecp_Start_Week, CTN_Grp_Const_Ecp_End_Week,
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

        for col in mg_cols:
            df_out_CTNGroupConstraintDetail[col] = df_out_CTNGroupConstraintDetail[col].fillna(0).astype(int)

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # 수정: 2025-05-14 (by Kang)
        df_out_CTNGroupConstraintDetail = df_out_CTNGroupConstraintDetail.groupby(
            [Version_COLUMN, GroupID_COLUM, Location_COLUMN, Item_COLUMN,
             CTN_Grp_Const_Ecp_Start_Week, CTN_Grp_Const_Ecp_End_Week, CTN_Grp_Const_ECP_Flag])[mg_cols].sum().reset_index()
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

