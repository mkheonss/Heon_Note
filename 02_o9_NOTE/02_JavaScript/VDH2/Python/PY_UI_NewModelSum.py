

"""

* 프로그램명
    - PY_UI_NewModelSum

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.01.10 / ybest7.park (박병훈) / Create
- 2025.02.05 : New Model Sum_PVR Plan 외 15개 measure 및 New Model Sum Stauts_LCM From Site 추가
- 2025.05.19 : AllWeek & UntilCurWeek  measure 삭제 (주석처리)
- 2026.01.30 : ybest7.park (박병훈)
    - df_in_Sublocation 추가 → 서브로케이션 설정
    - New Model_RUN/DROP 추가
- 2026.02.24 : ybest7.park df_in_NewModel input query 수정 및 input date 필터 조건 추가

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
    - df_in_NewModel = Select ([Version].[Version Name] * [Location].[Location] * [Sales Domain].[AP2] * [Category].[Category] * [Item New Model].[Item] ) on row, ({Measure.[New Model_Dev PVR],Measure.[New Model_BOM HQ Status],Measure.[New Model_Dev PRA],Measure.[New Model_SET SRP-S],Measure.[New Model_SET SRP-F],Measure.[New Model_SR Date],Measure.[New Model_SET MP],Measure.[New Model_Sales RTS],Measure.[New Model_LCM From Site],Measure.[New Model_Year],Measure.[New Model_RUN/DROP],Measure.[Dummy]}) on column where {Measure.[New Model_RUN/DROP] == "RUN" && ~isnull(Measure.[New Model_Year])};
    - df_in_CurrentWeek = select (&PastWeeksofCurYear.unionwith(&CurrentWeek) *Time.[Day]);
    - df_in_MKTNameAndProduct = select ([Item].[Item] * [Item].[Marketing Name] * [Item].[Product]);
    - df_in_TimeWeek = select ([Time].[Day] * [Time].[Week] );
    - df_in_Sublocation = select (&MFStageLCMLocation) on row, () on column include memberproperties {[Location].[Location], [DisplayName]};
    - df_in_CurrentDay = Select(&CurrentDay);


* 데이터 삭제
     DELETE DATA FOR MODEL [New Model Sum] where {Version.[Version Name].[CWV_MP]};
     DELETE DATA FOR MODEL [New Model Sum Status] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_NewModelSum = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Marketing Name] * [Time].[Week] * [Sales Domain].[AP2] * [Item New Model].[Item] * [Product].[Product] ) on row, ({Measure.[New Model Sum_BOM HQ Actual], Measure.[New Model Sum_BOM HQ Plan], Measure.[New Model Sum_MP Actual], Measure.[New Model Sum_MP Plan],  Measure.[New Model Sum_PRA Actual],  Measure.[New Model Sum_PRA Plan], Measure.[New Model Sum_PVR Actual], Measure.[New Model Sum_PVR Plan],  Measure.[New Model Sum_RTS Actual], Measure.[New Model Sum_RTS Plan], Measure.[New Model Sum_SR Date Actual],  Measure.[New Model Sum_SR Date Plan], Measure.[New Model Sum_SRP-F Actual],  Measure.[New Model Sum_SRP-F Plan], Measure.[New Model Sum_SRP-S Actual],  Measure.[New Model Sum_SRP-S Plan],Measure.[New Model Sum_Year]}) on column;
    - df_out_NewModelSumStatus = Select ([Version].[Version Name].[CWV_MP] * [Item].[Marketing Name] * [Location].[Location] * [Sales Domain].[AP2] * [Item New Model].[Item] * [Product].[Product] * [Sub Location].[Sub Location]) on row, ({Measure.[New Model Sum Status_PVR Plan],  Measure.[New Model Sum Status_PVR Actual], Measure.[New Model Sum Status_PVR Completion Flag], Measure.[New Model Sum Status_BOM HQ Plan],  Measure.[New Model Sum Status_BOM HQ Actual], Measure.[New Model Sum Status_BOM HQ Completion Flag], Measure.[New Model Sum Status_PRA Plan],Measure.[New Model Sum Status_PRA Actual], Measure.[New Model Sum Status_PRA Completion Flag],  Measure.[New Model Sum Status_SRP-S Plan], Measure.[New Model Sum Status_SRP-S Actual], Measure.[New Model Sum Status_SRP-S Completion Flag], Measure.[New Model Sum Status_SRP-F Plan], Measure.[New Model Sum Status_SRP-F Actual], Measure.[New Model Sum Status_SRP-F Completion Flag], Measure.[New Model Sum Status_SR Date Plan], Measure.[New Model Sum Status_SR Date Actual], Measure.[New Model Sum Status_SR Completion Flag], Measure.[New Model Sum Status_MP Plan],Measure.[New Model Sum Status_MP Actual], Measure.[New Model Sum Status_MP Completion Flag],Measure.[New Model Sum Status_RTS Plan],Measure.[New Model Sum Status_RTS Actual], Measure.[New Model Sum Status_RTS Completion Flag] }) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_NewModelSum] for measures {[New Model Sum_MP Actual]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;

"""


########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
from NSCMCommon import VDCommon as vdCommon
import os.path
import time
from datetime import datetime
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

warnings.filterwarnings("ignore")
########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_NewModelSum'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level
paramOutVersion = 'CWV_MP'
########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')


def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, Logger, is_local, log_path)


def vd_log_end():
    vdCommon.gfn_pyLog_end()


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(target_df):
    new_df = target_df
    delete_dfs(target_df)
    return new_df


def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
        return df[column_name].values[0]
    return None  # 기본값 반환


def get_formatted_time(timestamp):
    """타임스탬프를 사람이 읽을 수 있는 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def format_size(size_in_bytes):
    """바이트 단위를 적절히 MB 또는 GB로 변환하여 문자열 반환"""
    if size_in_bytes >= 1024 ** 3:  # 1GB 이상일 때
        return f"{size_in_bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{size_in_bytes / 1024 ** 2:.1f} MB"


def run_time_minutes(start_time):
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"


def datetime_check_series(date_series):
    # 가능한 형식들을 순서대로 시도
    date_formats = ['%m/%d/%Y %I:%M:%S %p', '%Y/%m/%d %I:%M:%S %p', '%Y-%m-%d %H:%M:%S']

    # 모든 시도가 실패했을 때 NaT로 초기화
    parsed_dates = pd.Series(pd.NaT, index=date_series.index)

    for fmt in date_formats:
        # 형식을 시도하여 변환하고, NaT 값이 없는 경우에 대해서만 변환을 유지
        new_dates = pd.to_datetime(date_series, format=fmt, errors='coerce')
        parsed_dates = parsed_dates.combine_first(new_dates)

    return parsed_dates



try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, Logger, com.gfn_get_isLocal(), (os.path.dirname(__file__) if com.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(com.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)


# Logger.debug(f'[START] {str_instance}')
# Logger.Start()
# note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
# step(0, '===================== plugin Execution Start =====================')
# tracemalloc.start()

# try:
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################


    step(100, '=====> STEP 1(Start) : Input Date Frame Read')

    # Value 변수 선언
    # PARAM_OUTVERSION_VALUE = "CWV_MP"
    pDetailLogFlag = "N"


    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_NewModel = read_csv_file('df_in_NewModel')
        df_in_MKTNameAndProduct = read_csv_file('df_in_MKTNameAndProduct')
        df_in_CurrentWeek = read_csv_file('df_in_CurrentWeek')
        df_in_TimeWeek = read_csv_file('df_in_TimeWeek')
        df_in_Sublocation = read_csv_file('df_in_Sublocation')
        df_in_CurrentDay = read_csv_file('df_in_CurrentDay')

    # if df_in_NewmodelSet.empty:
    #     raise Exception("Exception: df_in_NewmodelSet is empty")
    #
    # if df_in_CurrentWeek.empty:
    #     raise Exception("Exception: df_in_CurrentWeek is empty")
    #
    # if df_in_MarketingName.empty:
    #     raise Exception("Exception: df_in_MarketingName is empty")

    # note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_NewModel, 'df_in_NewModel', True)
    print_df(df_in_CurrentWeek, 'df_in_CurrentWeek', True)
    print_df(df_in_MKTNameAndProduct, 'df_in_MKTNameAndProduct',True)
    print_df(df_in_TimeWeek, 'df_in_TimeWeek',True)
    print_df(df_in_Sublocation, 'df_in_Sublocation', True)
    print_df(df_in_CurrentDay, 'df_in_CurrentDay', True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Item_COLUMN = 'Item.[Item]'
    Item_New_Model_COLUMN = 'Item New Model.[Item]'
    Item_Product_COLUMN = 'Item.[Product]'
    TimeDay_COLUMN = 'Time.[Day]'
    TimeWeek_COLUMN = 'Time.[Week]'
    TimeDayKey_COLUMN = 'Time.[DayKey]'
    TimeWeekKey_COLUMN = 'Time.[WeekKey]'
    Location_COLUMN = 'Location.[Location]'
    Sub_Location_COLUM = 'Sub Location.[Sub Location]'
    Sales_Domain_AP_COLUMN = 'Sales Domain.[AP2]'
    Sales_Domain_GC_COLUMN = 'Sales Domain.[GC]'
    Category_CLOUMN = 'Category.[Category]'
    Item_Marketing_Name_COLUMN = 'Item.[Marketing Name]'
    Product_COLUMN = 'Product.[Product]'
    Location_DisplyName_COLUM = 'Location.[DisplayName]'
    New_Model_Sales_RTS = 'New Model_Sales RTS'
    Key_COLUMN = 'Key_On'

    New_Model_Dev_PVR_plan = 'New Model_Dev PVR_plan'
    New_Model_Dev_PVR_actual = 'New Model_Dev PVR_actual'
    New_Model_BOM_HQ_Status_plan = 'New Model_BOM HQ Status_plan'
    New_Model_BOM_HQ_Status_actual = 'New Model_BOM HQ Status_actual'
    New_Model_Dev_PRA_plan = 'New Model_Dev PRA_plan'
    New_Model_Dev_PRA_actual = 'New Model_Dev PRA_actual'
    New_Model_SET_SRP_S_plan = 'New Model_SET SRP-S_plan'
    New_Model_SET_SRP_S_actual = 'New Model_SET SRP-S_actual'
    New_Model_SET_SRP_F_plan = 'New Model_SET SRP-F_plan'
    New_Model_SET_SRP_F_actual = 'New Model_SET SRP-F_actual'
    New_Model_SR_Date_plan = 'New Model_SR Date_plan'
    New_Model_SR_Date_actual = 'New Model_SR Date_actual'
    New_Model_SET_MP_plan = 'New Model_SET MP_plan'
    New_Model_SET_MP_actual = 'New Model_SET MP_actual'
    New_Model_Sales_RTS_plan = 'New Model_Sales RTS_plan'
    New_Model_Sales_RTS_actual = 'New Model_Sales RTS_actual'
    New_Model_Dev_PVR_flag = 'New Model_Dev PVR_flag'
    New_Model_BOM_HQ_Status_flag = 'New Model_BOM HQ Status_flag'
    New_Model_Dev_PRA_flag = 'New Model_Dev PRA_flag'
    New_Model_SET_SRP_S_flag = 'New Model_SET SRP-S_flag'
    New_Model_SET_SRP_F_flag = 'New Model_SET SRP-F_flag'
    New_Model_SR_Date_flag = 'New Model_SR Date_flag'
    New_Model_SET_MP_flag = 'New Model_SET MP_flag'
    New_Model_Sales_RTS_flag = 'New Model_Sales RTS_flag'
    New_Model_LCM_From_Site= 'New Model_LCM From Site'
    New_Model_Year = 'New Model_Year'

    plan_New_Model_Dev_PVR = 'plan_New Model_Dev PVR'
    plan_New_Model_Dev_PRA = 'plan_New Model_Dev PRA'
    plan_New_Model_SET_SRP_F = 'plan_New Model_SET SRP-F'
    plan_New_Model_SET_SR = 'plan_New Model_SET SR'
    plan_New_Model_SET_MP = 'plan_New Model_SET MP'
    plan_New_Model_Sales_RTS = 'plan_New Model_Sales RTS'
    actual_New_Model_Dev_PVR = 'actual_New Model_Dev PVR'
    actual_New_Model_Dev_PRA = 'actual_New Model_Dev PRA'
    actual_New_Model_SET_SRP_F = 'actual_New Model_SET SRP-F'
    actual_New_Model_SET_SR = 'actual_New Model_SET SR'
    actual_New_Model_SET_MP = 'actual_New Model_SET MP'
    actual_New_Model_Sales_RTS = 'actual_New Model_Sales RTS'

    New_Model_Sum_PVR_Plan = 'New Model Sum_PVR Plan'
    New_Model_Sum_PVR_Actual = 'New Model Sum_PVR Actual'
    New_Model_Sum_PRA_Plan = 'New Model Sum_PRA Plan'
    New_Model_Sum_PRA_Actual = 'New Model Sum_PRA Actual'
    New_Model_Sum_SRP_F_Plan = 'New Model Sum_SRP-F Plan'
    New_Model_Sum_SRP_F_Actual = 'New Model Sum_SRP-F Actual'
    New_Model_Sum_SR_Plan = 'New Model Sum_SR Plan'
    New_Model_Sum_SR_Actual = 'New Model Sum_SR Actual'
    New_Model_Sum_MP_Plan = 'New Model Sum_MP Plan'
    New_Model_Sum_MP_Actual = 'New Model Sum_MP Actual'
    New_Model_Sum_RTS_Plan = 'New Model Sum_RTS Plan'
    New_Model_Sum_RTS_Actual = 'New Model Sum_RTS Actual'
    New_Model_Sum_Week_Flag = 'New Model Sum_Week Flag'
    New_Model_Sum_Stauts_LCM_From_Site= 'New Model Sum Status_LCM From Site'

    New_Model_Sum_Status_PVR_Plan ='New Model Sum Status_PVR Plan'
    New_Model_Sum_Status_PVR_Actual = 'New Model Sum Status_PVR Actual'


    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) 날짜 데이터 설정을 위한 전처리 → 현재 Sever Error 발생
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : output data machining')
    # currentMonth & currentYear 설정 (2026-02-24 추가 )
    currentMonth = pd.to_numeric(df_in_CurrentDay[TimeDay_COLUMN].str.split('-').str[1], errors='coerce')
    currentYear  = pd.to_numeric(df_in_CurrentDay[TimeDay_COLUMN].str.split('-').str[0], errors='coerce')
    # currentMonth 가 9월 이상이면 currentYear 필터 범위를 내년으로 변경
    currentYear = np.where(currentMonth > 9, currentYear + 1, currentYear)
    currentYear = pd.Series(currentYear, index=df_in_CurrentDay.index)
    # 필터 진행을 위한 데이터 타입 변경
    df_in_NewModel[New_Model_Year] = pd.to_numeric(df_in_NewModel[New_Model_Year], errors='coerce')
    # inputdate 필터 진행
    df_in_NewModel = df_in_NewModel[df_in_NewModel[New_Model_Year].isin(currentYear)]
    print_df(df_in_NewModel, 'df_in_NewModel step -0 전처리 데이터 확인 ', True)

    # 필터를 위한 TimeDay_COLUMN을 series 로 만들기
    td = pd.to_datetime(df_in_TimeWeek[TimeDay_COLUMN], errors='coerce')
    # currentYear 기준으로 startday & endday 날짜 구하기 (범위 설정)
    startday = pd.to_datetime((currentYear - 1).astype(str) + '-06-01', errors='coerce')
    endday = pd.to_datetime((currentYear).astype(str) + '-09-30', errors='coerce')
    note(f'startday: =========> {startday}')
    note(f'endday  : =========> {endday}')
    # 필터를 위한 mask 설정
    maskday = (td.notna().to_numpy()
               & startday.notna().to_numpy()
               & endday.notna().to_numpy()
               & (td.to_numpy() >= startday.to_numpy())
               & (td.to_numpy() <= endday.to_numpy()))

    # df_in_TimeWeek 기간 필터링
    df_in_TimeWeek = df_in_TimeWeek.loc[maskday].copy()
    print_df(df_in_TimeWeek, 'df_in_TimeWeek step -0 전처리 데이터 확인 ', True)
    note(f'df_in_TimeWeek min : =========> {df_in_TimeWeek[TimeDay_COLUMN].min()}')
    note(f'df_in_TimeWeek max : =========> {df_in_TimeWeek[TimeDay_COLUMN].max()}')
    ############################################################ 2026.02.24 수정 끝.. ###################################

    # 계산을 위한 당월 주차값 설정
    currentweek = int(df_in_CurrentWeek[TimeWeek_COLUMN].iloc[-1])

    # 2026-01-29 ybest7.park(박병훈)
    # 'New Model_RUN/DROP' merge하기 위한 데이터 프레임 분리
    df_in_NewModel_run_drop = df_in_NewModel[[
        Version_COLUMN,Location_COLUMN,Sales_Domain_AP_COLUMN,Item_New_Model_COLUMN,'New Model_RUN/DROP']].drop_duplicates()
    # merge을 위한 column 명 변경
    rename_col = {Item_COLUMN: Item_New_Model_COLUMN}
    # New_model과 mkg name 정보를 가져오기 위한 merge
    df_in_NewModel_temp = df_in_NewModel.drop(columns=['New Model_RUN/DROP'], axis=1).merge(
        df_in_MKTNameAndProduct.rename(columns=rename_col),
        on=Item_New_Model_COLUMN, how='left')
    note(f'df_in_NewModel_temp shape : {df_in_NewModel_temp.shape}')
    # plan 과 actual 명으로 데이터 프레임 나누기
    df_plan = df_in_NewModel_temp[df_in_NewModel[Category_CLOUMN] == 'Plan'].drop(columns=[Category_CLOUMN,'Dummy'])
    df_actual = df_in_NewModel_temp[df_in_NewModel[Category_CLOUMN] == 'Actual'].drop(columns=[Category_CLOUMN,'Dummy'])
    front_cols = [Version_COLUMN, Location_COLUMN, Sales_Domain_AP_COLUMN, Item_New_Model_COLUMN,
                  Item_Marketing_Name_COLUMN, Item_Product_COLUMN, New_Model_Year]
    remaining_cols = [col for col in df_plan.columns if col not in front_cols]
    df_plan = df_plan[front_cols + remaining_cols]
    df_actual = df_actual[front_cols + remaining_cols]

    # 나누었던 데이터 프레임 merge

    df_plan.columns = list(df_plan.columns[:7]) + [col for col in df_plan.columns[7:] + '_plan']
    df_actual.columns = list(df_actual.columns[:7]) + [col for col in df_actual.columns[7:] + '_actual']
    df_plan[Key_COLUMN] = 1
    df_actual[Key_COLUMN] = 1
    df_in_NewmodelSet_temp = df_plan.merge(df_actual, on=[*df_plan.columns[:7], Key_COLUMN], how='left').drop(
        columns=[Key_COLUMN])

    # 데이터 프레임 컬럼명 순서 정의
    col_list = df_in_NewmodelSet_temp.columns
    plan_cols = [col for col in col_list if col.endswith('_plan')]
    actual_cols = [col for col in col_list if col.endswith('_actual')]
    paired_cols = [col for pair in zip(plan_cols, actual_cols) for col in pair if
                   pair[0].replace('_plan', '').replace('_actual', '')]

    df_in_NewmodelSet_temp = df_in_NewmodelSet_temp[front_cols + paired_cols]

    # df_in_NewmodelSet_temp = df_in_NewmodelSet_temp.apply(lambda col : col.astype(str) if col.dtype == 'float64' else col)

    df_in_NewmodelSet_temp.drop_duplicates(keep='first', inplace=True)

    print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp step -3', True )
    # save_csv_file(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp step -3')
    step(300, '=====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. (1) From Date & To Date 기준으로 주차 정보 가지고 오기
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

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


    # df_in_NewmodelSet_temp.iloc[:, 7:] = df_in_NewmodelSet_temp.iloc[:, 7:].applymap(convert_date_format)

    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp step - 날자 변환후 ')

    # 데이저 중 가장 작은 날짜와 큰 날짜 추출을 위한 조건 적용을 위한 data column 설정
    not_date_col = ['New Model_BOM HQ Status_actual', 'New Model_LCM From Site_plan',
                    'New Model_LCM From Site_actual']
    data_cols = [col for col in df_in_NewmodelSet_temp.columns[7:] if col != not_date_col]

    df_in_NewmodelSet_temp[data_cols] = df_in_NewmodelSet_temp[data_cols].apply(lambda s: s.map(convert_date_format))
    # all_dates에 null 이 아닌 데이터 Stack
    all_dates = pd.to_datetime(df_in_NewmodelSet_temp[data_cols].stack(), errors='coerce')
    all_dates = all_dates[all_dates.notnull()]
    # all_dates에  0 인 경우 날짜가 1970-01-01로 설정된 내용 필터
    all_dates = all_dates[all_dates > pd.Timestamp('1970-01-01')]
    # all_date 중 최소 / 최대 값 추출
    min_day = all_dates.min()
    max_day = all_dates.max()

    note(f"============================================>{min_day}, {type(min_day)}")
    note(f"============================================>{max_day}, {type(max_day)}")

    # 데이터 프레임에 날짜를 주차 변환을 위한 기준 컬럼 설정
    WeekMapping = df_in_TimeWeek.set_index(TimeDay_COLUMN)[TimeWeek_COLUMN].to_dict()
    # note(f"===========================================>{WeekMapping.keys()}")


    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp step - 주차 변환 전', True)


    # 데이터 프레임 날짜를 주차로 변환
    change_columns_list = df_in_NewmodelSet_temp.columns[7:-2].tolist()
    for col in change_columns_list:
        if col != 'New Model_BOM HQ Status_actual':
            df_in_NewmodelSet_temp[col] = df_in_NewmodelSet_temp[col].apply(lambda x: WeekMapping.get(x, np.nan))
            if col != 'New Model_BOM HQ Status_actual':
                if df_in_NewmodelSet_temp[col].dtype == float:
                    df_in_NewmodelSet_temp[col] = df_in_NewmodelSet_temp[col].fillna(0).astype(int)


    print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp step - 주차 변화 후' )

    # 2번째 output을 위한 데이터 프레임 복사
    df_out_NewModelSumStatus = df_in_NewmodelSet_temp.copy()
    # df_out_NewModelSumStatus = df_out_NewModelSumStatus.drop(
    #     columns=['Dummy_plan', 'Dummy_actual'])

    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus copy 전',True)

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) df_in_GRMtrl 테이블 전 처리
    ###############################################################################################################
    step(500, '=====> STEP 5(Start) : output data machining')

    # Time Week 에서 정보를 최소/최대 범위를 추출하여 데이터 프레임과 merge (주차 정보로 확장)
    df_in_TimeWeek_temp = df_in_TimeWeek.copy()
    df_in_TimeWeek_temp[TimeDay_COLUMN] = pd.to_datetime(df_in_TimeWeek_temp[TimeDay_COLUMN])
    df_in_TimeWeek_temp = df_in_TimeWeek_temp[
        (df_in_TimeWeek_temp[TimeDay_COLUMN] >= min_day) & (df_in_TimeWeek_temp[TimeDay_COLUMN] <= max_day)]
    df_in_TimeWeek_temp = df_in_TimeWeek_temp[
        [TimeDay_COLUMN, TimeWeek_COLUMN]].drop_duplicates(
        subset=TimeWeek_COLUMN, keep='first')
    # 데이터 프레임 주차로 확장
    df_in_NewmodelSet_temp[Key_COLUMN] = 1
    df_in_TimeWeek_temp[Key_COLUMN] = 1
    df_in_TimeWeek_temp = df_in_TimeWeek_temp[[TimeWeek_COLUMN, Key_COLUMN]]
    df_in_NewmodelSet_temp = df_in_NewmodelSet_temp.merge(
        df_in_TimeWeek_temp, on=Key_COLUMN, how='left').drop(
        columns=[Key_COLUMN])

    # 데이터 프레임 순서를 정하기 위한 컬럼 추가
    front_cols.append(TimeWeek_COLUMN)

    # 데이터 프레임 순서 정의
    remaining_cols = [col for col in df_in_NewmodelSet_temp.columns if col not in front_cols]
    df_in_NewmodelSet_temp = df_in_NewmodelSet_temp[front_cols + remaining_cols]

    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet 임시 -1')

    # Plan columns 의 주차 값과 Time Week에 값이 같이면 1로 치환
    for col in plan_cols:
        # if col != "New Model_BOM HQ Status_actual":
        df_in_NewmodelSet_temp[col] = df_in_NewmodelSet_temp.apply(
            lambda row: 1 if row[TimeWeek_COLUMN] == row[col] else ("" if pd.isna(row[col]) else ""), axis=1)

    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet 임시 -2')

    # plan 값을 보고 actual 값 지정을 위해 column 명 나눔 및 제외할 컬러명 설정
    status_col = 'New Model_BOM HQ Status_actual'
    plan_cols = [col for col in df_in_NewmodelSet_temp.columns if col.endswith('_plan') and 'From Site_plan' not in col]
    actual_cols = [col for col in df_in_NewmodelSet_temp.columns if
                   col.endswith('_actual') and 'From Site_actual' not in col]

    # plan column 값의 조건에 따라 Actual column 값 변경
    # 조건 1 : Plan 값이 null 이면 Actual 값 null
    # 조건 2 : plan 값이 1 이고 Actual 가 null이 아니면 1
    # 조건 3 : plan의 값이 1 이고 'OK' ,'LATE' 여도 1
    # 조건 4 : plan의 값이 1 이고 Actual 값이 'NG','-' 이면 0

    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet 임시 -3')
    # note(f"=======================> plan_cols list : {plan_cols} ")
    # note(f"=======================> actual_cols list : {actual_cols} ")

    # for plan_col, actual_col in zip(plan_cols, actual_cols):
    #     df_in_NewmodelSet_temp[actual_col] = df_in_NewmodelSet_temp.apply(
    #         lambda row:
    #         ('' if pd.isna(row[plan_col]) else
    #          1 if row[plan_col] == 1 and pd.notna(row[actual_col]) and row[actual_col] not in['', np.nan] else
    #          1 if row[plan_col] == 1 and pd.notna(row[status_col]) and row[status_col] in ["OK", 'LATE', 'ING'] else
    #          0 if row[plan_col] == 1 and (pd.isna(row[status_col]) or row[status_col] in ["NG", '-', np.nan,0]) else
    #          row[actual_col]),axis=1)

    for plan_col, actual_col in zip(plan_cols, actual_cols):
        df_in_NewmodelSet_temp[actual_col] = df_in_NewmodelSet_temp.apply(
            lambda row: '' if row[plan_col] == '' else
            1 if row[plan_col] == 1 and pd.notna(row[actual_col]) and row[actual_col] not in ['', np.nan] else
            1 if row[plan_col] == 1 and pd.notna(row[status_col]) and row[status_col] in ["OK", 'LATE', 'ING'] else
            0 if row[plan_col] == 1 and pd.notna(row[status_col]) and row[status_col] in ["NG", '-'] else
            row[actual_col], axis=1
        )
    # 계획 컬럼이 숫자 / 문자가 썩여 있으면 1로 판정도 안전하게
    # def is_plan_one(s):
    #     # 1 또는 "1"을 1로 취급
    #     return pd.to_numeric(s, errors='coerce').eq(1)
    #
    # status = df_in_NewmodelSet_temp[status_col].astype(str).str.strip()
    # OK_SET = {'OK', 'LATE', 'ING'}
    # NG_SET = {'NG', '-'}
    #
    # for plan_col, actual_col in zip(plan_cols, actual_cols):
    #     plan1 = pd.to_numeric(df_in_NewmodelSet_temp[plan_col], errors='coerce').eq(1)
    #
    #     # "plan_col1이 공백이면 actual도 공백 " 조건
    #     plan_blank = df_in_NewmodelSet_temp[plan_col].astype(str).str.strip().eq("")
    #
    #     # actual 유효값 존재 조건 (빈문자 / NA 제외)
    #     actual_str = df_in_NewmodelSet_temp[actual_col].astype(str).str.strip()
    #     actual_has_value = actual_str.ne("") & df_in_NewmodelSet_temp[actual_col].notna()
    #
    #     # 조건들 (벡터로 정리...)
    #     c1 = plan_blank
    #     c2 = plan1 & actual_has_value
    #     c3 = plan1 & status.isin(OK_SET)
    #     c4 = plan1 & status.isin(NG_SET)
    #     default = df_in_NewmodelSet_temp[actual_col].astype(str)
    #
    #     # 결과 : 조건 우선순위대로 적용
    #     # - c1 이면 '' 공백
    #     # - c2 / c3 이면 1
    #     # - c4 이면 0
    #     # 그외는 기존 actual 유지
    #     out = np.select(
    #         [c1, c2 | c3, c4],
    #         ["", "1","0"],
    #         default=df_in_NewmodelSet_temp[actual_col]
    #     )
    #
    #     df_in_NewmodelSet_temp[actual_col] = pd.Series(out, index=df_in_NewmodelSet_temp.index, dtype="string")


    # for plan_col, actual_col in zip(plan_cols, actual_cols):
    #     df_in_NewmodelSet_temp[actual_col] = df_in_NewmodelSet_temp.apply(
    #         lambda row: 1 if pd.isna(row[plan_col]) and pd.isna(row[actual_col]) else
    #                     1 if pd.notna(row[plan_col]) and row[plan_col] < currentweek and pd.isna(row[actual_col]) else
    #                     1 if row[plan_col] == 1 and row[actual_col] in ['NG','-'] else
    #                     0 if row[plan_col] == 1 and pd.notna(row[actual_col]) else
    #                     0 if row[plan_col] == 1 and row[actual_col] in ["OK", 'LATE'] else
    #                     row[actual_col], axis=1
    #     )

    # # 원본 plan 컬럼을 백업하고 '_orginal' 컬럼 추가
    # for plan_col in plan_cols:
    #     plan_original_col = plan_col.replace('_plan', '_plan_original')
    #     df_in_NewmodelSet_temp[plan_original_col] = df_in_NewmodelSet_temp[plan_col]
    #
    # # 조건을 결과값 설정
    # for plan_col, actual_col in zip(plan_cols, actual_cols):
    #     plan_original_col = plan_col.replace('_plan', '_plan_original')
    #     # actual_original_col = actual_col.replace('_actual','_actual_original')
    #
    #     df_plan = df_in_NewmodelSet_temp[plan_col]
    #     df_plan_ori = df_in_NewmodelSet_temp[plan_original_col]
    #     df_actual = df_in_NewmodelSet_temp[actual_col]
    #     # df_actual_ori = df_in_NewmodelSet_temp[actual_original_col]
    #
    #     plan_ori_num = pd.to_numeric(df_plan_ori, errors='coerce')
    #     actual_num = pd.to_numeric(df_actual, errors='coerce')
    #
    #     # Status 컬럼 구분
    #     is_status_col = (actual_col == 'New Model_BOM HQ Status_actual')
    #
    #     # invalid_plan_mask = df_plan.astype(str).str.strip()==''
    #
    #     # cond 1
    #     cond1 = (df_plan == '') & (df_actual == '')
    #     # cond2
    #     cond2 = (df_plan == 0) & (plan_ori_num < int(currentweek)) & (df_actual == '')
    #
    #     if is_status_col:
    #         cond3 = (df_plan == 1) & (df_actual.isin(['NG', '-']))
    #         cond4 = (df_plan == 1) & (df_actual.isin(['OK', 'LATE', 'ING']))
    #         cond5 = (df_plan == 1) & (~df_actual.isin(['NG', '-', 'OK', 'LATE', 'ING'])) & (df_actual.notna())
    #     else:
    #         cond3 = cond4 = cond5 = pd.Series(False, index=df_plan.index)
    #
    #     # np.select를 사용해서 최종 결과 적용
    #     df_in_NewmodelSet_temp[actual_col] = np.select(
    #         [cond1, cond2, cond3, cond4, cond5],
    #         [1, 1, 1, 0, 0],
    #         default="")

    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet 임시 -4')

    df_in_NewmodelSet = df_in_NewmodelSet_temp.copy()
    df_in_NewmodelSet = df_in_NewmodelSet[
        [Version_COLUMN,Location_COLUMN,Sales_Domain_AP_COLUMN,Item_New_Model_COLUMN, Item_Marketing_Name_COLUMN,
         Item_Product_COLUMN,TimeWeek_COLUMN, New_Model_Dev_PVR_plan, New_Model_Dev_PVR_actual,
         New_Model_BOM_HQ_Status_plan, New_Model_BOM_HQ_Status_actual, New_Model_Dev_PRA_plan,New_Model_Dev_PRA_actual,
         New_Model_SET_SRP_S_plan, New_Model_SET_SRP_S_actual,New_Model_SET_SRP_F_plan, New_Model_SET_SRP_F_actual,
         New_Model_SR_Date_plan,New_Model_SR_Date_actual, New_Model_SET_MP_plan, New_Model_SET_MP_actual,
         New_Model_Sales_RTS_plan, New_Model_Sales_RTS_actual,'New Model_LCM From Site_plan',
         'New Model_LCM From Site_actual',New_Model_Year]]
    df_in_NewmodelSet = df_in_NewmodelSet.rename(columns={Item_Product_COLUMN :Product_COLUMN})

    for col in df_in_NewmodelSet.columns[7:-2]:
        df_in_NewmodelSet[col] = pd.to_numeric(
            df_in_NewmodelSet[col].replace('',np.nan), errors='coerce'
        )

    print_df(df_in_NewmodelSet, 'df_in_NewmodelSet step -1',True)
    print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp step -5',True)
    step(500, '=====> STEP 5(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 6 (1) 최종 Output Data  설정
    ###############################################################################################################
    step(600, '=====> STEP 6(Start) : output data machining')
    # pd.set_option('future.no_silent_downcasting', True)
    # # 계산을 위한 당월 주차값 설정
    # currentweek = int(df_in_CurrentWeek[TimeWeek_COLUMN].iloc[-1])
    # note(f"curretweek =============================>{currentweek}")
    df_in_NewmodelSet_temp[TimeWeek_COLUMN] = pd.to_numeric(df_in_NewmodelSet_temp[TimeWeek_COLUMN] , errors='coerce')

    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp - 1')

    # 계산을 위한 Column 명 설정
    # col_name = [col for col in df_in_NewmodelSet_temp.columns if col.endswith(('_plan', '_actual')) and "From Site_" not in col]
    # # 그룹별로 계산을 위한 그룹 컬럼 설정
    # group_col = [Version_COLUMN, Location_COLUMN, Item_New_Model_COLUMN, Item_Marketing_Name_COLUMN,
    #              Item_Product_COLUMN, Sales_Domain_AP_COLUMN]
    # # 신규 Column 을 생성하면서 계산 AllWeek 는 전체 sum, unticlCurWeek는 당주까지의 sum -----> 2025.05.19 (주석처리 요청)
    # for col in col_name:
    #     df_in_NewmodelSet_temp[col] = pd.to_numeric(
    #         df_in_NewmodelSet_temp[col].replace('', np.nan), errors='coerce')
    #     df_in_NewmodelSet_temp[f'{col}_AllWeek'] = df_in_NewmodelSet_temp.groupby(group_col)[col].cumsum()
    #     df_in_NewmodelSet_temp[f'{col}_untilCurWeek'] = (
    #         df_in_NewmodelSet_temp.loc[df_in_NewmodelSet_temp[TimeWeek_COLUMN] <= currentweek].groupby(group_col)[
    #             col].transform('cumsum'))

    # print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp - 2')

    # df_out_NewModelSum = df_in_NewmodelSet.merge(df_out_NewModelSum,
    #                                              on=[Version_COLUMN, Location_COLUMN, Sales_Domain_AP_COLUMN,
    #                                                  Item_New_Model_COLUMN, Item_Marketing_Name_COLUMN,
    #                                                  TimeWeek_COLUMN], how='left')

    # # 컬럼명 변경을 위한 딕션어리 설정
    rename_cols = {New_Model_Dev_PVR_plan: New_Model_Sum_PVR_Plan,
                   New_Model_Dev_PVR_actual: New_Model_Sum_PVR_Actual,
                   New_Model_BOM_HQ_Status_plan: 'New Model Sum_BOM HQ Plan',
                   New_Model_BOM_HQ_Status_actual: 'New Model Sum_BOM HQ Actual',
                   New_Model_Dev_PRA_plan: New_Model_Sum_PRA_Plan,
                   New_Model_Dev_PRA_actual: New_Model_Sum_PRA_Actual,
                   New_Model_SET_SRP_S_plan: 'New Model Sum_SRP-S Plan',
                   New_Model_SET_SRP_S_actual: 'New Model Sum_SRP-S Actual',
                   New_Model_SET_SRP_F_plan: New_Model_Sum_SRP_F_Plan,
                   New_Model_SET_SRP_F_actual: New_Model_Sum_SRP_F_Actual,
                   New_Model_SR_Date_plan: 'New Model Sum_SR Date Plan',
                   New_Model_SR_Date_actual: 'New Model Sum_SR Date Actual',
                   New_Model_SET_MP_plan: New_Model_Sum_MP_Plan,
                   New_Model_SET_MP_actual: New_Model_Sum_MP_Actual,
                   New_Model_Sales_RTS_plan: New_Model_Sum_RTS_Plan,
                   New_Model_Sales_RTS_actual: New_Model_Sum_RTS_Actual,
                   # 'New Model_Dev PVR_plan_AllWeek': 'New Model Sum_PVR Plan AllWeek',
                   # 'New Model_Dev PVR_actual_AllWeek': 'New Model Sum_PVR Actual AllWeek',
                   # 'New Model_BOM HQ Status_plan_AllWeek': 'New Model Sum_BOM HQ Plan AllWeek',
                   # 'New Model_BOM HQ Status_actual_AllWeek': 'New Model Sum_BOM HQ Actual AllWeek',
                   # 'New Model_Dev PRA_plan_AllWeek': 'New Model Sum_PRA Plan AllWeek',
                   # 'New Model_Dev PRA_actual_AllWeek': 'New Model Sum_PRA Actual AllWeek',
                   # 'New Model_SET SRP-S_plan_AllWeek': 'New Model Sum_SRP-S Plan AllWeek',
                   # 'New Model_SET SRP-S_actual_AllWeek': 'New Model Sum_SRP-S Actual AllWeek',
                   # 'New Model_SET SRP-F_plan_AllWeek': 'New Model Sum_SRP-F Plan AllWeek',
                   # 'New Model_SET SRP-F_actual_AllWeek': 'New Model Sum_SRP-F Actual AllWeek',
                   # 'New Model_SR Date_plan_AllWeek': 'New Model Sum_SR Date Plan AllWeek',
                   # 'New Model_SR Date_actual_AllWeek': 'New Model Sum_SR Date Actual AllWeek',
                   # 'New Model_SET MP_plan_AllWeek': 'New Model Sum_MP Plan AllWeek',
                   # 'New Model_SET MP_actual_AllWeek': 'New Model Sum_MP Actual AllWeek',
                   # 'New Model_Sales RTS_plan_AllWeek': 'New Model Sum_RTS Plan AllWeek',
                   # 'New Model_Sales RTS_actual_AllWeek': 'New Model Sum_RTS Actual AllWeek',
                   # 'New Model_Dev PVR_plan_untilCurWeek': 'New Model Sum_PVR Plan UntilCurWeek',
                   # 'New Model_Dev PVR_actual_untilCurWeek': 'New Model Sum_PVR Actual UntilCurWeek',
                   # 'New Model_BOM HQ Status_plan_untilCurWeek': 'New Model Sum_BOM HQ Plan UntilCurWeek',
                   # 'New Model_BOM HQ Status_actual_untilCurWeek': 'New Model Sum_BOM HQ Actual UntilCurWeek',
                   # 'New Model_Dev PRA_plan_untilCurWeek': 'New Model Sum_PRA Plan UntilCurWeek',
                   # 'New Model_Dev PRA_actual_untilCurWeek': 'New Model Sum_PRA Actual UntilCurWeek',
                   # 'New Model_SET SRP-S_plan_untilCurWeek': 'New Model Sum_SRP-S Plan UntilCurWeek',
                   # 'New Model_SET SRP-S_actual_untilCurWeek': 'New Model Sum_SRP-S Actual UntilCurWeek',
                   # 'New Model_SET SRP-F_plan_untilCurWeek': 'New Model Sum_SRP-F Plan UntilCurWeek',
                   # 'New Model_SET SRP-F_actual_untilCurWeek': 'New Model Sum_SRP-F Actual UntilCurWeek',
                   # 'New Model_SR Date_plan_untilCurWeek': 'New Model Sum_SR Date Plan UntilCurWeek',
                   # 'New Model_SR Date_actual_untilCurWeek': 'New Model Sum_SR Date Actual UntilCurWeek',
                   # 'New Model_SET MP_plan_untilCurWeek': 'New Model Sum_MP Plan UntilCurWeek',
                   # 'New Model_SET MP_actual_untilCurWeek': 'New Model Sum_MP Actual UntilCurWeek',
                   # 'New Model_Sales RTS_plan_untilCurWeek': 'New Model Sum_RTS Plan UntilCurWeek',
                   # 'New Model_Sales RTS_actual_untilCurWeek': 'New Model Sum_RTS Actual UntilCurWeek', 2025-05-19 주석 처리
                   Item_Product_COLUMN: 'Product.[Product]',New_Model_Year :'New Model Sum_Year' }

    df_out_NewModelSum = df_in_NewmodelSet_temp.rename(columns=rename_cols)
    # df_in_NewmodelSet = df_in_NewmodelSet.rename(columns=rename_cols)


    print_df(df_in_NewmodelSet_temp, 'df_in_NewmodelSet_temp - 임시-3',True)
    # save_csv_file(df_out_NewModelSum, 'df_out_NewModelSum')


    # out put 설정을 위한 필요한 Column 명 수출 및 데이터 프레임 순서 지정
    df_out_NewModelSum = df_out_NewModelSum[
        [Version_COLUMN, Location_COLUMN, Sales_Domain_AP_COLUMN, Item_New_Model_COLUMN, Item_Marketing_Name_COLUMN,
         'Product.[Product]', TimeWeek_COLUMN,New_Model_Sum_PVR_Plan, New_Model_Sum_PVR_Actual,
         New_Model_Sum_PRA_Actual,'New Model Sum_SRP-S Plan', 'New Model Sum_SRP-S Actual',
         New_Model_Sum_SRP_F_Plan, New_Model_Sum_SRP_F_Actual,'New Model Sum_SR Date Plan',
         'New Model Sum_SR Date Actual',New_Model_Sum_MP_Plan,New_Model_Sum_MP_Actual,
         New_Model_Sum_RTS_Plan, New_Model_Sum_RTS_Actual,
         'New Model Sum_BOM HQ Plan', 'New Model Sum_BOM HQ Actual', New_Model_Sum_PRA_Plan,
         # 'New Model Sum_PVR Plan AllWeek', 'New Model Sum_PVR Actual AllWeek', 'New Model Sum_BOM HQ Plan AllWeek',
         # 'New Model Sum_BOM HQ Actual AllWeek','New Model Sum_PRA Plan AllWeek', 'New Model Sum_PRA Actual AllWeek',
         # 'New Model Sum_SRP-S Plan AllWeek','New Model Sum_SRP-S Actual AllWeek','New Model Sum_SRP-F Plan AllWeek',
         # 'New Model Sum_SRP-F Actual AllWeek', 'New Model Sum_SR Date Plan AllWeek',
         # 'New Model Sum_SR Date Actual AllWeek','New Model Sum_MP Plan AllWeek', 'New Model Sum_MP Actual AllWeek',
         # 'New Model Sum_RTS Plan AllWeek','New Model Sum_RTS Actual AllWeek','New Model Sum_PVR Plan UntilCurWeek',
         # 'New Model Sum_PVR Actual UntilCurWeek','New Model Sum_BOM HQ Plan UntilCurWeek',
         # 'New Model Sum_BOM HQ Actual UntilCurWeek','New Model Sum_PRA Plan UntilCurWeek',
         # 'New Model Sum_PRA Actual UntilCurWeek','New Model Sum_SRP-S Plan UntilCurWeek',
         # 'New Model Sum_SRP-S Actual UntilCurWeek','New Model Sum_SR Date Plan UntilCurWeek',
         # 'New Model Sum_SR Date Actual UntilCurWeek','New Model Sum_MP Plan UntilCurWeek',
         # 'New Model Sum_MP Actual UntilCurWeek','New Model Sum_RTS Plan UntilCurWeek',
         # 'New Model Sum_RTS Actual UntilCurWeek',
         'New Model Sum_Year']]

    # df_out_NewModelSum = df_in_NewmodelSet.merge(df_out_NewModelSum,
    #                                              on=[Version_COLUMN, Location_COLUMN, Sales_Domain_AP_COLUMN,
    #                                                  Item_New_Model_COLUMN, Item_Marketing_Name_COLUMN,
    #                                                  'Product.[Product]', TimeWeek_COLUMN], how='left')

    # df_out_NewModelSum = df_out_NewModelSum.dropna(subset=df_out_NewModelSum.select_dtypes(include=['float64']).columns,
    #                                                how='all')

    # save_csv_file(df_out_NewModelSum, 'df_out_NewModelSum 임시 - 1')
    #
    # print_df(df_out_NewModelSum, 'df_out_NewModelSum - 임시-1')

    # df_out_NewModelSum = df_out_NewModelSum.fillna(0)
    # # print_df(df_out_NewModelSum, 'df_out_NewModelSum 임시 - 2')
    # df_out_NewModelSum[
    #     df_out_NewModelSum.select_dtypes(include=['float64']).columns] = df_out_NewModelSum.select_dtypes(
    #     include=['float64']).astype(int)
    #
    # for col in df_out_NewModelSum.columns[7:]:
    #     df_out_NewModelSum[col] = df_out_NewModelSum[col].astype(int)

    # print_df(df_out_NewModelSum, 'df_out_NewModelSum 임시 - 3')

    # 2026-01-29 ybest7.park 추가
    # df_in_NewModel_run_drop 와 df_out_NewModelSum merge를 통해 'New Model_RUN/DROP' 데이터 구함
    df_in_NewModel_run_drop = df_in_NewModel_run_drop.rename(
        columns={'New Model_RUN/DROP' : 'New Model Sum_RUN/DROP'})
    # merge를 위해 데이터 타입 변경
    df_out_NewModelSum[Sales_Domain_AP_COLUMN] = df_out_NewModelSum[Sales_Domain_AP_COLUMN].astype(str)
    df_in_NewModel_run_drop[Sales_Domain_AP_COLUMN] = df_in_NewModel_run_drop[Sales_Domain_AP_COLUMN].astype(str)
    # merge를 통해 데이터 구하기
    df_out_NewModelSum = df_out_NewModelSum.merge(
        df_in_NewModel_run_drop, on = [Version_COLUMN,Location_COLUMN,Sales_Domain_AP_COLUMN,Item_New_Model_COLUMN],
        how='left')


    print_df(df_out_NewModelSum, 'df_out_NewModelSum',True)
    # save_csv_file(df_out_NewModelSum, 'df_out_NewModelSum')

    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 7 (1) 2번째 데이터 프레임 전처리
    ###############################################################################################################
    step(700, '=====> STEP 7(Start) : output data machining')

    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus',True)
    value_columns = [col for col in df_out_NewModelSumStatus.columns[7:-2] if
                     col != not_date_col]

    # note(f" =============================> value_columns list :  {value_columns}")

    status_col = 'New Model_BOM HQ Status_actual'

    # print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시 -0')

    for col in value_columns:
        if col != status_col:
            # note(f"============================> col name : {col}")
            df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col].fillna(0).astype(int)
            # df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col].fillna(0).astype(int)
    #         note(f"============================> col name final : {col}")
    #
    # print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시 -1')

    # note(f"currentweek : =============> {currentweek}, {type(currentweek)}")

    plan_cols = [col for col in df_out_NewModelSumStatus.columns if col.endswith('_plan') and 'From Site' not in col]
    actual_cols = [col for col in df_out_NewModelSumStatus.columns if
                   col.endswith('_actual') and 'From Site' not in col]


    completion_flags = []

    for plan_col, actual_col in zip(plan_cols, actual_cols):
        base_name = plan_col.replace('_plan', '')
        plan = pd.to_numeric(df_out_NewModelSumStatus[plan_col], errors='coerce').fillna(0).astype(int)
        # note(f'plan_col : {plan_col} , {plan.dtype}')
        actual = pd.to_numeric(df_out_NewModelSumStatus[actual_col],errors='coerce')
        # note(f'actual_col : {plan_col} , {actual.dtype}')
        status = df_out_NewModelSumStatus[status_col].astype(str).str.strip().str.upper()

        # 조건 1 : plan == 0 & actual == 0
        cond1 = (plan == 0) & (actual == 0)

        # 조건 2 : plan != 0 & plan < Currentweek & actual == 0
        cond2 = (plan < currentweek) & (actual == 0)
        # note(f"plan ====> {plan} ,actual ====> {actual} ,currentweek ====> {currentweek} , cond2 ====> {(plan < currentweek)}")

        # 조건 3 :
        cond3 = (plan != 0) & status.isin(['NG', '-', ''])

        # 조건 4 : plan !=0 & status in ['ING','LATE','OK']
        cond4 = (plan != 0) & status.isin(['ING', 'LATE', 'OK'])

        # # 조건5
        # cond5 = (plan > currentweek) & ((actual == 0) | (actual > currentweek))


        # 최종 completion Flag
        flag = np.select([cond1, cond2, cond3, cond4],
                         [1,1,1,0], default=np.nan)

        # cond1 = (plan == 0) & (actual == 0)
        # cond2 = (plan != 0) & (actual == 0)
        # cond3 = (plan < currentweek) & (actual == 0)
        # cond4 = (plan != 0) & (actual != 0)
        # cond5 = (plan != 0) & status.isin(['NG', '-', ''])
        # cond6 = (plan != 0) & status.isin(['ING', 'LATE', 'OK' ])
        # cond7 = (plan < currentweek) & (actual < currentweek)
        #
        # flag = np.select(
        #     [cond1, cond2, cond3, cond4, cond5, cond6, cond7],
        #     [0,0,0,0,0,1,1], default=np.nanqk
        # )

        df_out_NewModelSumStatus[f'{base_name}_Completion Flag'] = flag

    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시 -3',True)

    df_out_NewModelSumStatus[value_columns] = df_out_NewModelSumStatus[value_columns].fillna(0)

    for col in value_columns:
        if col != 'New Model_BOM HQ Status_actual':
            df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col].map(
                lambda x: '' if x == 0 else f'W{int(float(x)) % 100:02d}' if pd.notna(x) else '')

    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시 -4')

    # df_out_NewModelSumStatus = df_out_NewModelSumStatus.fillna(0)
    #
    # print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시 -2')
    # for col in value_columns:
    #     if col != "New Model_BOM HQ Status_actual":
    #         df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col].astype(str).fillna(0).astype(int)
    #         # df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col]
    # # df_out_NewModelSumStatus[value_columns] = df_out_NewModelSumStatus[value_columns].fillna(0).astype(int)
    # # df_out_NewModelSumStatus[value_columns] = df_out_NewModelSumStatus[value_columns]
    #
    # print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시 -1')
    #
    # for col in value_columns:
    #     if col != 'New Model_BOM HQ Status_actual':
    #         df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col].map(
    #             lambda x: '' if x == 0 else f'W{int(float(x)) % 100:02d}' if pd.notna(x) else '')
    #
    # print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시 -2')
    #
    # status_col = 'New Model_BOM HQ Status_actual'
    # plan_cols = [col for col in df_out_NewModelSumStatus.columns if col.endswith('_plan') ]
    # actual_cols = [col for col in df_out_NewModelSumStatus.columns if col.endswith('_actual')]
    #
    # # plan column 값의 조건에 따라 Actual column 값 변경
    # # 조건 1 : Plan 값이 null 이면 Actual 값 null
    # # 조건 2 : plan 값이 1 이고 Actual 가 null이 아니면 1
    # # 조건 3 : plan의 값이 1 이고 'OK' ,'LATE' 여도 1
    # # 조건 4 : plan의 값이 1 이고 Actual 값이 'NG','-' 이면 0
    #
    # print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시-3')
    #
    # for p_col in plan_cols:
    #     prefix = p_col.replace('_plan', '')
    #     a_col = f'{prefix}_actual'
    #
    #     if a_col in actual_cols:
    #         flag_col = f'{prefix}_flag'
    #
    #         if a_col == status_col:
    #             df_out_NewModelSumStatus[flag_col] = df_out_NewModelSumStatus.apply(
    #                 lambda row: ''
    #                 if row[p_col] == '' else
    #                 'True' if pd.notna(row[p_col]) and pd.notna(row[a_col]) and row[a_col] in ['OK', 'LATE'] else
    #                 'False' if pd.notna(row[p_col]) and pd.notna(row[a_col]) and row[a_col] in ['NG','-',''] else 'False',
    #                 axis=1
    #             )
    #         else:
    #             df_out_NewModelSumStatus[flag_col] = df_out_NewModelSumStatus.apply(
    #                 lambda row: ''
    #                 if row[p_col] == '' else
    #                 'True' if pd.notna(row[p_col]) and pd.notna(row[a_col]) and str(row[a_col]).strip() !="" else
    #                 'False',
    #                 axis=1
    #             )
    # Completion Flag 컬럼들만 선택
    flag_cols = [col for col in df_out_NewModelSumStatus.columns if col.endswith('_Completion Flag')]

    # 각 컬럼에 대해 조건 반환
    for col in flag_cols:
        df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col].apply(lambda x: True if x == 1 else(False if x == 0 else np.nan))

    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - 임시-4',True)

    rename_cols = {Item_Product_COLUMN : Product_COLUMN,
                   New_Model_Dev_PVR_plan : New_Model_Sum_Status_PVR_Plan,
                   New_Model_Dev_PVR_actual : New_Model_Sum_Status_PVR_Actual,
                   'New Model_Dev PVR_Completion Flag': 'New Model Sum Status_PVR Completion Flag',
                   New_Model_BOM_HQ_Status_plan : 'New Model Sum Status_BOM HQ Plan',
                   New_Model_BOM_HQ_Status_actual : 'New Model Sum Status_BOM HQ Actual',
                   'New Model_BOM HQ Status_Completion Flag' : 'New Model Sum Status_BOM HQ Completion Flag',
                   New_Model_Dev_PRA_plan : 'New Model Sum Status_PRA Plan',
                   New_Model_Dev_PRA_actual : 'New Model Sum Status_PRA Actual',
                   'New Model_Dev PRA_Completion Flag' : 'New Model Sum Status_PRA Completion Flag',
                   New_Model_SET_SRP_S_plan : 'New Model Sum Status_SRP-S Plan',
                   New_Model_SET_SRP_S_actual : 'New Model Sum Status_SRP-S Actual',
                   'New Model_SET SRP-S_Completion Flag' : 'New Model Sum Status_SRP-S Completion Flag',
                   New_Model_SET_SRP_F_plan : 'New Model Sum Status_SRP-F Plan',
                   New_Model_SET_SRP_F_actual : 'New Model Sum Status_SRP-F Actual',
                   'New Model_SET SRP-F_Completion Flag' : 'New Model Sum Status_SRP-F Completion Flag',
                   New_Model_SR_Date_plan : 'New Model Sum Status_SR Date Plan',
                   New_Model_SR_Date_actual : 'New Model Sum Status_SR Date Actual',
                   'New Model_SR Date_Completion Flag' : 'New Model Sum Status_SR Completion Flag',
                   New_Model_SET_MP_plan : 'New Model Sum Status_MP Plan',
                   New_Model_SET_MP_actual : 'New Model Sum Status_MP Actual',
                   'New Model_SET MP_Completion Flag' : 'New Model Sum Status_MP Completion Flag',
                   New_Model_Sales_RTS_plan : 'New Model Sum Status_RTS Plan',
                   New_Model_Sales_RTS_actual : 'New Model Sum Status_RTS Actual',
                   'New Model_Sales RTS_Completion Flag' : 'New Model Sum Status_RTS Completion Flag',
                   'New Model_LCM From Site_actual': New_Model_Sum_Stauts_LCM_From_Site,
                   New_Model_Year :'New Model Sum Status_Year'}

    df_out_NewModelSumStatus = df_out_NewModelSumStatus.rename(columns=rename_cols)

    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus - Rename', True)



    df_out_NewModelSumStatus = df_out_NewModelSumStatus.rename(columns=rename_cols)

    df_out_NewModelSumStatus['New Model Sum Status_BOM HQ Actual'] = np.where(
        df_out_NewModelSumStatus['New Model Sum Status_BOM HQ Actual'].isin (["OK", 'LATE']),
        df_out_NewModelSumStatus['New Model Sum Status_BOM HQ Plan'], np.nan)

    # for col in df_out_NewModelSumStatus.columns[6:]:
    #     df_out_NewModelSumStatus[col] = df_out_NewModelSumStatus[col].astype(int)

    # 2026-01-29 ybest7.park(박병훈)
    df_in_NewModel_run_drop = df_in_NewModel_run_drop.rename(
        columns ={'New Model Sum_RUN/DROP' : 'New Model Sum Status_RUN/DROP'})
    df_out_NewModelSumStatus[Sales_Domain_AP_COLUMN] = df_out_NewModelSumStatus[Sales_Domain_AP_COLUMN].astype(str)
    df_out_NewModelSumStatus = df_out_NewModelSumStatus.merge(
        df_in_NewModel_run_drop, on = [Version_COLUMN,Location_COLUMN,Sales_Domain_AP_COLUMN,Item_New_Model_COLUMN],
        how ='left')

    # Sub_location 값 설정

    if  Location_DisplyName_COLUM not in df_in_Sublocation.columns:
        df_in_Sublocation = df_in_Sublocation.rename(columns={
            'Location.[Location$DisplayName]' : Location_DisplyName_COLUM})

    df_out_NewModelSumStatus[Sub_Location_COLUM] = df_out_NewModelSumStatus['New Model Sum Status_LCM From Site'].map(
        df_in_Sublocation.set_index(Location_DisplyName_COLUM)[Location_COLUMN])

    df_out_NewModelSumStatus.loc[:,Sub_Location_COLUM] = df_out_NewModelSumStatus[Sub_Location_COLUM].fillna('-')

    df_out_NewModelSumStatus = df_out_NewModelSumStatus[
        [Version_COLUMN, Location_COLUMN, Sales_Domain_AP_COLUMN, Item_New_Model_COLUMN, Item_Marketing_Name_COLUMN,
         'Product.[Product]', Sub_Location_COLUM,'New Model Sum Status_PVR Plan',
         'New Model Sum Status_PVR Actual', 'New Model Sum Status_PVR Completion Flag',
         'New Model Sum Status_BOM HQ Plan', 'New Model Sum Status_BOM HQ Actual',
         'New Model Sum Status_BOM HQ Completion Flag', 'New Model Sum Status_PRA Plan',
         'New Model Sum Status_PRA Actual', 'New Model Sum Status_PRA Completion Flag',
         'New Model Sum Status_SRP-S Plan', 'New Model Sum Status_SRP-S Actual',
         'New Model Sum Status_SRP-S Completion Flag', 'New Model Sum Status_SRP-F Plan',
         'New Model Sum Status_SRP-F Actual', 'New Model Sum Status_SRP-F Completion Flag',
         'New Model Sum Status_SR Date Plan', 'New Model Sum Status_SR Date Actual',
         'New Model Sum Status_SR Completion Flag', 'New Model Sum Status_MP Plan',
         'New Model Sum Status_MP Actual', 'New Model Sum Status_MP Completion Flag',
         'New Model Sum Status_RTS Plan', 'New Model Sum Status_RTS Actual',
         'New Model Sum Status_RTS Completion Flag', 'New Model Sum Status_Year', 'New Model Sum Status_RUN/DROP']]

    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus',True)
    step(700, '=====> STEP 7(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 8 (1) 최종 output 설정
    ###############################################################################################################
    step(800, '=====> STEP 7(Start) : output data machining')

    # df_out_NewModelSum = df_in_NewmodelSet_temp.copy()

    print_df(df_out_NewModelSum, 'df_out_NewModelSum',True)
    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus',True)


    step(800, '=====> STEP 7(End) : Check memory usage & runtime')



    ################################################################################################################
    # Step 8. (1) 최종 Out_Put Save
    ################################################################################################################

    row_count, col_count = df_out_NewModelSum.shape
    note(f'=====> Final df_out_NewModelSum rows : {row_count} , Columns : {col_count}')
    print_df(df_out_NewModelSum, 'df_out_NewModelSum')

    row_count, col_count = df_out_NewModelSumStatus.shape
    note(f'=====> Final df_out_NewModelSumStatus rows : {row_count} , Columns : {col_count}')
    print_df(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus')


    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_NewModelSum, 'df_out_NewModelSum')
        vdCommon.gfn_saveDf(df_out_NewModelSum, "df_out_NewModelSum", True)
        save_csv_file(df_out_NewModelSumStatus, 'df_out_NewModelSumStatus')
        vdCommon.gfn_saveDf(df_out_NewModelSumStatus, "df_out_NewModelSumStatus", True)


except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg,p_log_level=LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_NewModelSum = pd.DataFrame([], columns=[])
    df_out_NewModelSumStatus = pd.DataFrame([], columns=[])

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
