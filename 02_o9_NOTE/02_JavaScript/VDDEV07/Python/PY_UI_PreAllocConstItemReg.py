

"""

* 프로그램명
    - PY_UI_PreAllocConstItemReg.py

* 내용
    - Pre Alloc Cosnt. by Item 등록
* 변경이력
- 2026.01.27 신규 생성 (By ys5236.kang)
* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary


* Input Table
   - df_in_PreAllocConst =
    Select ([Version].[Version Name] * [Group].[Group ID] ) on row,
    ({ Measure.[Pre Alloc Const_From Site ID], Measure.[Pre Alloc Const_GC Code], Measure.[Pre Alloc Const_AP2 Code],
    Measure.[Pre Alloc Const_Item], Measure.[Pre Alloc Const_Exception],Measure.[Pre Alloc Const_Product Grp],
    Measure.[Pre Alloc Const_Project],Measure.[Pre Alloc Const_Inch],Measure.[Pre Alloc Const_MKT Name],Measure.[Pre Alloc Const_Year]}) on column;

   - df_in_BODItem =
    Select([Version].[Version Name]* [Location].[Location] * &SETItemExcludeOPT * [Item].[Product Group] * [Item].[Project]
    * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Year]
    * [Sub Location].[Sub Location GC] *[Sub Location].[Sub Location Rep AP2] ) on row,
    ({Measure.[BOD Item_Asn], Measure.[BOD Item_Cur Status],Measure.[Dummy]}) on column
    Where {[Trans Mode].[Trans Mode] ,&NSUISubLocationDC, Measure.[BOD Item_asn] >-1,
    (Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE"}),
    (coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now())} ;


* 데이터 삭제
    DELETE DATA FOR MODEL [Pre Alloc Const by Item] where {Version.[Version Name].[CWV_MP], [Group].[Group ID]};

* Output Table
    - df_out_PreAllocConstbyItem =
    Select ([Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Item].[Item] ) on row,
    ({Measure.[Pre Alloc Const by Item_BOD Item ToSite], Measure.[Pre Alloc Const by Item_Created By], Measure.[Pre Alloc Const by Item_Creation Time], Measure.[Pre Alloc Const by Item_Flag], Measure.[Pre Alloc Const by Item_PLC Status], Measure.[Pre Alloc Const by Item_Update Time], Measure.[Pre Alloc Const by Item_Updated By]}) on column;
    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    EXEC plugin instance [PY_UI_PreAllocConstItemReg] for measures {[Pre Alloc Const by Item_Flag]}
    using scope ([Version].[Version Name].[' + fbVersion + '] * [Group].[Group ID].[' + fbGroupID + '])
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


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
str_instance = 'PY_UI_PreAllocConstItemReg'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion

# value 변수 선언
# input variable 확인
paramOutVersion = (
    "CWV_MP"
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)

# input variable 확인
paramOutCreatedByUser = (
    "PY_UI_PreAllocConstItemReg"
    if is_local or not paramOutCreatedByUser or not paramOutCreatedByUser.strip()
    else paramOutCreatedByUser
)
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

def get_current_date_str(tz: str | None = None) -> str:
    """
    현재 시각을 'YYYY-MM-DD HH:MM:SS' 형식 문자열로 반환.
    tz 인자로 'UTC' (대소문자 무관)를 주면 UTC 기준, 그 외에는 로컬 타임존 기준.
    """
    if isinstance(tz, str) and tz.upper() == "UTC":
        now = datetime.datetime.now(datetime.timezone.utc)
    else:
        # now = datetime.datetime.now().astimezone()
        now = datetime.datetime.now()

    return now.strftime("%Y-%m-%d %H:%M:%S")

def exception_flag_check(exception, df):
    #df_filter = df.copy()
    results_temp = []
    for index, value in exception.items():
        #print(f"exception_flag_check: {value}")
        if pd.isna(cond_val) or str(cond_val).strip().lower() == 'all' or str(cond_val).strip() == '':
            continue
        else:
            startChar = value[0:1]
            endChar = value[-1]

            if (startChar == "%" and endChar == "%"):
                prefix = value.replace('%', '')
                df_filter = df[df[ITEM_ITEM_COLUMN].astype(str).str.contains(prefix)]
            elif startChar == "%":
                prefix = value.replace('%', '')
                df_filter = df[df[ITEM_ITEM_COLUMN].astype(str).str.endswith(prefix)]
            elif endChar == "%":
                prefix = value.replace('%', '')
                df_filter = df[df[ITEM_ITEM_COLUMN].astype(str).str.startswith(prefix)]
            else:
                df_filter = df[df[ITEM_ITEM_COLUMN].astype(str) == value]
            df_filter[PRE_ALLOC_CONST_BY_ITEM_FLAG] = "true"

            if not df_filter.empty:  # 조건이 필터된 경우
                results_temp.append(df_filter)

    if results_temp:
        df_temp = pd.concat(results_temp, ignore_index=True).drop_duplicates()
    else:  # 조건이 빈 데이터 인 경우 컬럼 지정
        df_temp = pd.DataFrame(columns=[VERSION_NAME_COLUMN,GROUP_GROUP_ID_COLUMN,
                                        LOCATION_LOCATION_COLUMN,ITEM_ITEM_COLUMN,PRE_ALLOC_CONST_BY_ITEM_FLAG])

    df = pd.merge(df, df_temp, on=[VERSION_NAME_COLUMN,GROUP_GROUP_ID_COLUMN,
                                        LOCATION_LOCATION_COLUMN,ITEM_ITEM_COLUMN], how="left")
    df[PRE_ALLOC_CONST_BY_ITEM_FLAG] = df[PRE_ALLOC_CONST_BY_ITEM_FLAG].fillna("false")
    return df

# def() End

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
        # paramOutVersion = PARAM_OUTVERSION_VALUE
        df_in_PreAllocConst = read_csv_file('df_in_PreAllocConst_PAC_77382')
        df_in_BODItem = read_csv_file('df_in_BODItem_260204')
    print_df(df_in_PreAllocConst, 'df_in_CTNGrpConst', True)
    print_df(df_in_BODItem, 'df_in_BODItem', True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')
    # Dimension 변수
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    GROUP_GROUP_ID_COLUMN = 'Group.[Group ID]'

    LOCATION_LOCATION_COLUMN = 'Location.[Location]'
    SALES_DOMAIN_AP2 = 'Sales Domain.[AP2]'
    SUBLOCATION_SUBLOCATION_GC_COLUMN = 'Sub Location.[Sub Location GC]'
    SUBLOCATION_SUBLOCATION_AP2_COLUMN = 'Sub Location.[Sub Location Rep AP2]'
    ITEM_ITEM_COLUMN = 'Item.[Item]'
    ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
    ITEM_PROJECT_COLUMN = 'Item.[Project]'
    ITEM_INCH_COLUMN = 'Item.[Inch]'
    ITEM_MARKETING_NAME_COLUMN = 'Item.[Marketing Name]'
    ITEM_YEAR_COLUMN = 'Item.[Year]'
    ITEM_ITEM_STD1_COLUMN = 'Item.[Item Std1]'

    # Measure변수
    #BOD_ITEM_CUR_STATUS = 'BOD Item_Cur Status'
    PRE_ALLOC_CONST_BY_ITEM_FLAG = 'Pre Alloc Const by Item_Flag'
    #PRE_ALLOC_CONST_BY_ITEM_PLC_STATUS = 'Pre Alloc Const by Item_PLC Status'
    PRE_ALLOC_CONST_BY_ITEM_CREATION_TIME = 'Pre Alloc Const by Item_Creation Time'
    PRE_ALLOC_CONST_BY_ITEM_CREATED_BY = 'Pre Alloc Const by Item_Created By'

    PRE_ALLOC_CONST_SITE_ID = 'Pre Alloc Const_From Site ID'
    PRE_ALLOC_CONST_GC_CODE = 'Pre Alloc Const_GC Code'
    PRE_ALLOC_CONST_AP2_CODE = 'Pre Alloc Const_AP2 Code'
    PRE_ALLOC_CONST_ITEM = 'Pre Alloc Const_Item'
    PRE_ALLOC_CONST_EXCEPTION = 'Pre Alloc Const_Exception'
    PRE_ALLOC_CONST_PRODUCT_GRP = 'Pre Alloc Const_Product Grp'
    PRE_ALLOC_CONST_PROJECT = 'Pre Alloc Const_Project'
    PRE_ALLOC_CONST_INCH = 'Pre Alloc Const_Inch'
    PRE_ALLOC_CONST_MKT_NAME = 'Pre Alloc Const_MKT Name'
    PRE_ALLOC_CONST_YEAR = 'Pre Alloc Const_Year'

    PRE_ALLOC_CONST_FILTER_ASN = 'Pre Alloc Const Filter_Asn'

    # ETC
    ITEM_EXCEPTION = 'Item Exception'

    step(200, '=====> STEP 2(End) : DataFrame Column 변수 처리')
    ################################################################################################################
    # Step 3 (1)
    ################################################################################################################
    step(300, '=====> STEP 3(Start) ')

    condition_columns = [
        LOCATION_LOCATION_COLUMN,
        SUBLOCATION_SUBLOCATION_GC_COLUMN, SUBLOCATION_SUBLOCATION_AP2_COLUMN,
        ITEM_PRODUCT_GROUP_COLUMN, ITEM_PROJECT_COLUMN, ITEM_INCH_COLUMN, ITEM_MARKETING_NAME_COLUMN,
        ITEM_YEAR_COLUMN,PRE_ALLOC_CONST_ITEM, PRE_ALLOC_CONST_EXCEPTION
        ]
    #Rename
    df_in_PreAllocConst_temp = df_in_PreAllocConst.rename(
        columns={PRE_ALLOC_CONST_SITE_ID: LOCATION_LOCATION_COLUMN,
                 PRE_ALLOC_CONST_GC_CODE: SUBLOCATION_SUBLOCATION_GC_COLUMN,
                 PRE_ALLOC_CONST_AP2_CODE: SUBLOCATION_SUBLOCATION_AP2_COLUMN,
                 PRE_ALLOC_CONST_PRODUCT_GRP: ITEM_PRODUCT_GROUP_COLUMN,
                 PRE_ALLOC_CONST_PROJECT: ITEM_PROJECT_COLUMN,
                 PRE_ALLOC_CONST_INCH: ITEM_INCH_COLUMN,
                 PRE_ALLOC_CONST_MKT_NAME: ITEM_MARKETING_NAME_COLUMN,
                 PRE_ALLOC_CONST_YEAR: ITEM_YEAR_COLUMN
                })
    # 형변환
    df_in_BODItem[SUBLOCATION_SUBLOCATION_GC_COLUMN] = df_in_BODItem[SUBLOCATION_SUBLOCATION_GC_COLUMN].astype(str)
    df_in_BODItem[SUBLOCATION_SUBLOCATION_AP2_COLUMN] = df_in_BODItem[SUBLOCATION_SUBLOCATION_AP2_COLUMN].astype(str)
    df_in_PreAllocConst_temp[SUBLOCATION_SUBLOCATION_GC_COLUMN] = df_in_PreAllocConst_temp[SUBLOCATION_SUBLOCATION_GC_COLUMN].astype(str)
    df_in_PreAllocConst_temp[SUBLOCATION_SUBLOCATION_AP2_COLUMN] = df_in_PreAllocConst_temp[SUBLOCATION_SUBLOCATION_AP2_COLUMN].astype(str)
    # Null 값 처리
    df_in_PreAllocConst_temp[PRE_ALLOC_CONST_ITEM] = df_in_PreAllocConst_temp[PRE_ALLOC_CONST_ITEM].fillna('All')
    df_in_PreAllocConst_temp[PRE_ALLOC_CONST_EXCEPTION] = df_in_PreAllocConst_temp[PRE_ALLOC_CONST_EXCEPTION].fillna('')
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Multi Data 분리
    df_in_PreAllocConst_temp[condition_columns] = df_in_PreAllocConst_temp[condition_columns].applymap(
        lambda x: x.split('^') if isinstance(x, str) else x)

    for col in df_in_PreAllocConst_temp[condition_columns]:
        df_in_PreAllocConst_temp = df_in_PreAllocConst_temp.explode(col)

    #excetpion Item 조건
    exceptionfilter = df_in_PreAllocConst_temp[PRE_ALLOC_CONST_EXCEPTION].drop_duplicates()
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Item 데이타 필터링
    results = []
    # 조건 행 하나씩 순회
    for _, cond_row in df_in_PreAllocConst_temp.iterrows():
        df_filtered = df_in_BODItem.copy()

        for col in condition_columns:
            cond_val = cond_row[col]
            #print(f'DATA CHECK::: {cond_row[GROUP_GROUP_ID_COLUMN]}=>{col}={cond_val}')

            if pd.isna(cond_val) or str(cond_val).strip().lower() == 'all' or str(cond_val).strip() == '':
                continue  # 조건이 없거나 All 인 경우 조건 없음
            else:
                if(col == PRE_ALLOC_CONST_ITEM): #Item 필터
                    startChar = cond_val[0:1]
                    endChar = cond_val[-1]
                    if (startChar == "%" and endChar == "%"):
                        prefix = cond_val.replace('%', '')
                        df_filtered = df_filtered[df_filtered[ITEM_ITEM_COLUMN].astype(str).str.contains(prefix)]
                    elif startChar == "%":
                        prefix = cond_val.replace('%', '')
                        df_filtered = df_filtered[df_filtered[ITEM_ITEM_COLUMN].astype(str).str.endswith(prefix)]
                    elif endChar == "%":
                        prefix = cond_val.replace('%', '')
                        df_filtered = df_filtered[df_filtered[ITEM_ITEM_COLUMN].astype(str).str.startswith(prefix)]
                    else:
                        df_filtered = df_filtered[df_filtered[ITEM_ITEM_COLUMN].astype(str) == cond_val]
                else:
                    if(col == PRE_ALLOC_CONST_EXCEPTION):
                        continue
                    df_filtered = df_filtered[df_filtered[col] == cond_val]

        if not df_filtered.empty:  # 조건이 필터된 경우
            df_filtered[GROUP_GROUP_ID_COLUMN] = cond_row[GROUP_GROUP_ID_COLUMN]
            results.append(df_filtered)

    if results:
        final_results = pd.concat(results, ignore_index=True).drop_duplicates()
    else:  # 조건이 빈 데이터 인 경우 컬럼 지정
        final_results = pd.DataFrame(columns=condition_columns)

    #Rename
    df_out_PreAllocConstFilter = final_results.copy()
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #Exception Flag 체크
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    step(301, '=====> STEP 3(Exception Flag Chaek) ')
    df_item = final_results.copy()
    df_item = df_item[[VERSION_NAME_COLUMN,GROUP_GROUP_ID_COLUMN,LOCATION_LOCATION_COLUMN,ITEM_ITEM_COLUMN]].drop_duplicates()
    final_results = exception_flag_check(exceptionfilter, df_item)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    step(300, '=====> STEP 3(End) ')
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    step(400, '=====> STEP 4(Start) ')
    # <Pre Alloc Const by Item> 메저그룹 생성
    final_column =[VERSION_NAME_COLUMN, GROUP_GROUP_ID_COLUMN, LOCATION_LOCATION_COLUMN,
                   ITEM_ITEM_COLUMN,PRE_ALLOC_CONST_BY_ITEM_FLAG]
    df_out_PreAllocConstbyItem = final_results[final_column].drop_duplicates()
    # Create By Time, Create By User 세팅
    current_date = get_current_date_str('UTC')
    df_out_PreAllocConstbyItem[PRE_ALLOC_CONST_BY_ITEM_CREATION_TIME] = current_date
    df_out_PreAllocConstbyItem[PRE_ALLOC_CONST_BY_ITEM_CREATED_BY] = paramOutCreatedByUser
    df_out_PreAllocConstbyItem = df_out_PreAllocConstbyItem.sort_values(PRE_ALLOC_CONST_BY_ITEM_FLAG, ascending=False)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # <Pre Alloc Const Filter> 메저그룹 생성
    df_out_PreAllocConstFilter = df_out_PreAllocConstFilter.rename(
        columns={SUBLOCATION_SUBLOCATION_AP2_COLUMN: SALES_DOMAIN_AP2,
                 ITEM_PRODUCT_GROUP_COLUMN: ITEM_ITEM_STD1_COLUMN})

    final_filter_column =[VERSION_NAME_COLUMN, GROUP_GROUP_ID_COLUMN, LOCATION_LOCATION_COLUMN,SALES_DOMAIN_AP2,
                         ITEM_ITEM_STD1_COLUMN]
    df_out_PreAllocConstFilter = df_out_PreAllocConstFilter[final_filter_column].drop_duplicates()
    df_out_PreAllocConstFilter[PRE_ALLOC_CONST_FILTER_ASN] = "1"

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    if is_local:
        note(f'=====> <Local>Final output table create')
        save_csv_file(df_out_PreAllocConstbyItem, 'Fact.df_out_PreAllocConstbyItem')
        save_csv_file(df_out_PreAllocConstFilter, 'Fact.df_out_PreAllocConstFilter')

    step(400, '=====> STEP 4(End) ')
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_PreAllocConstbyItem = pd.DataFrame([], columns=[])
    df_out_PreAllocConstFilter = pd.DataFrame([], columns=[])
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