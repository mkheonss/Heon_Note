

"""

* 프로그램명
    - PY_UI_ProductProfitAve

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2024.11.15 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
     - df_in_ProductProfit = Select ([Version].[Version Name] * [Item].[Item].filter(#.relatedmembers([Item Stage]).element(0).Name == "SET") * [Time].[Month] * [Sales Domain].[AP2] * [Data Set].[Data Set] * [Item].[Product Group].filter(#.Name in {"TV", "MONITOR","AV"}) * [Item].[KPI] * [Item].[Series] * [Item].[Marketing Name] * [Item].[Inch] *[Item].[Strategy] ) on row, ({Measure.[Product Profit_C Profit], Measure.[Product Profit_C Profit Rate], Measure.[Product Profit_C Profit Rate Ave], Measure.[Product Profit_C Profit Rate F], Measure.[Product Profit_N Price], Measure.[Product Profit_N Price Ave], Measure.[Product Profit_N Price Currency], Measure.[Product Profit_Product Grade], Measure.[Product Profit_Profit Grade], Measure.[Product Profit_Profit Rank], Measure.[Product Profit_Rank], Measure.[Product_Profit_Sales Qty],Measure.[Dummy]}) on column;
     - df_in_Planning_Month = select (&PriceHorizon.relatedmembers([Planning Month]));


* 데이터 삭제
     DELETE DATA FOR MODEL [Product Profit] where {Version.[Version Name].[CurrentWorkingView]};


* Output Table
    - df_out_ProductProfit = Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item] * [Time].[Month] * [Sales Domain].[AP2] * [Data Set].[Data Set] ) on row, ({Measure.[Product Profit_C Profit], Measure.[Product Profit_C Profit Rate], Measure.[Product Profit_C Profit Rate Ave], Measure.[Product Profit_C Profit Rate F], Measure.[Product Profit_N Price], Measure.[Product Profit_N Price Ave], Measure.[Product Profit_N Price Currency], Measure.[Product Profit_Product Grade], Measure.[Product Profit_Profit Grade], Measure.[Product Profit_Profit Rank], Measure.[Product Profit_Rank], Measure.[Product_Profit_Sales Qty]}) on column;


* 테스트 스크립트
    EXEC plugin instance [PY_UI_ProductProfitAve] for Measures {[Product Profit_C Profit Rate]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), (paramDataSet ,"20240723_S1"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};

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
import warnings
import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re

from dateutil import parser as date_parser
from typing import Union
from pandas.tseries.offsets import MonthEnd

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ProductProfitAve'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion
paramOutVersion = 'CWV_MP'
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
    paramDataSet_VALUE = '20240723_S1'

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE
        paramDataSet = paramDataSet_VALUE

        df_in_ProductProfit = read_csv_file('df_in_ProductProfit')
        df_in_Planning_Month = read_csv_file('df_in_Planning_Month')


    # if df_in_ProductProfit.empty:
    #     raise Exception("Exception: df_in_ProductProfit is empty")
    #
    # if df_in_Planning_Month.empty:
    #     raise Exception("Exception: df_in_Planning_Month is empty")


    # if df_in_ProductProfit.empty:
    #     raise Exception("Exception: df_in_ProductProfit is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ProductProfit, 'df_in_ProductProfit',True)
    print_df(df_in_Planning_Month, 'df_in_Planning_Month',True)

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Item_COLUMN = 'Item.[Item]'
    TimeMonth_COLUMN = 'Time.[Month]'
    Data_Set_COLUMN = 'Data Set.[Data Set]'
    Sales_Domain_AP_COLUMN = 'Sales Domain.[AP2]'
    Item_Product_Group_COLUMN = 'Item.[Product Group]'
    Item_KPI_COLUMN = 'Item.[KPI]'
    Item_Series_COLUMN = 'Item.[Series]'
    Item_Marketing_Name_COLUMN = 'Item.[Marketing Name]'
    Item_Inch_COLUMN = 'Item.[Inch]'
    Item_Strategy_COLUMN = 'Item.[Strategy]'

    TV = 'TV'
    MONITOR = 'MONITOR'
    AV = 'AV'
    key_on = 'key_on'

    Product_Profit_C_Profit = 'Product Profit_C Profit'
    Product_Profit_C_Profit_Rate = 'Product Profit_C Profit Rate'
    Product_Profit_C_Profit_Rate_Ave = 'Product Profit_C Profit Rate Ave'
    Product_Profit_C_Profit_Rate_F = 'Product Profit_C Profit Rate F'
    Product_Profit_N_Price = 'Product Profit_N Price'
    Product_Profit_N_Price_Ave = 'Product Profit_N Price Ave'
    Product_Profit_N_Price_Currency = 'Product Profit_N Price Currency'
    Product_Profit_Product_Grade = 'Product Profit_Product Grade'
    Product_Profit_Profit_Grade = 'Product Profit_Profit Grade'
    Product_Profit_Profit_Rank = 'Product Profit_Profit Rank'
    Product_Profit_Rank = 'Product Profit_Rank'
    Product_Profit_Sales_Qty = 'Product_Profit_Sales Qty'

    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3 (1) Input Data Frame 전처리
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    df_in_Planning_Month = df_in_Planning_Month.rename(columns={'Time.[Planning Month]': TimeMonth_COLUMN})


    df_in_ProductProfit = df_in_ProductProfit[
        df_in_ProductProfit[TimeMonth_COLUMN].isin(df_in_Planning_Month[TimeMonth_COLUMN].unique())]
    df_in_ProductProfit[Product_Profit_C_Profit_Rate_F] = np.where(
        df_in_ProductProfit[Product_Profit_C_Profit_Rate].isna() | (
                    df_in_ProductProfit[Product_Profit_C_Profit_Rate] == 0), 1,
        df_in_ProductProfit[Product_Profit_C_Profit_Rate])

    print_df(df_in_ProductProfit, 'df_in_ProductProfit Step-3-1',True)
    df_in_ProductProfit_temp = df_in_ProductProfit.copy()
    df_in_ProductProfit = df_in_ProductProfit[df_in_ProductProfit[Product_Profit_C_Profit_Rate_F] != 1]

    df_in_ProductProfit_temp = df_in_ProductProfit_temp[df_in_ProductProfit_temp[Product_Profit_C_Profit_Rate_F] == 1]
    df_in_ProductProfit_temp = df_in_ProductProfit_temp[
        [Version_COLUMN, Item_COLUMN, Sales_Domain_AP_COLUMN, Item_Product_Group_COLUMN, Item_Inch_COLUMN,
         Item_Marketing_Name_COLUMN, Item_KPI_COLUMN, Item_Series_COLUMN, Item_Strategy_COLUMN, Product_Profit_N_Price,
         Product_Profit_Sales_Qty, Product_Profit_N_Price_Ave, Product_Profit_C_Profit,
         Product_Profit_C_Profit_Rate_Ave]]
    df_in_ProductProfit_temp = df_in_ProductProfit_temp.fillna(0)

    print_df(df_in_ProductProfit_temp, 'df_in_ProductProfit_temp Step-3-2',True)

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 4. (1) Out put 처리를 위한 전처리 및 Month의 범의 값 확인
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : input data machining')


    def conditional_group_sum(df):
        # Group_by 고정 Column 정의
        fixed_columns = [Version_COLUMN, Item_COLUMN, Sales_Domain_AP_COLUMN, Item_Product_Group_COLUMN]
        # 조건에 따라 그룹화 기준 설정
        group_by_dict = {
            TV: [Item_Marketing_Name_COLUMN, Item_Inch_COLUMN],
            MONITOR: [Item_KPI_COLUMN, Item_Inch_COLUMN],
            AV: [Item_Strategy_COLUMN, Item_Series_COLUMN]
        }

        # 조건에 따른 역순 적용
        remove_order_dict = {
            TV: [Item_Inch_COLUMN, Item_Marketing_Name_COLUMN],
            MONITOR: [Item_Inch_COLUMN, Item_KPI_COLUMN],
            AV: [Item_Series_COLUMN, Item_Strategy_COLUMN]
        }

        result_list = []

        # 각 Product_groupd에 따른 처리
        for product_group, initial_group_cols in group_by_dict.items():
            df_filtered = df[df[Item_Product_Group_COLUMN] == product_group]
            if df_filtered.empty:
                continue
            # 그롭화 조건을 역순으로 줄이면서 합계 계산
            for i in range(len(initial_group_cols) + 1):
                # 필터링된 prodect_group 설정
                current_group = fixed_columns + initial_group_cols[:len(initial_group_cols) - i]
                # 그룹화 후 합계 계산
                grouped = df_filtered.groupby(current_group, as_index=False).sum(numeric_only=False)

                # 조건을 만족하는 결과 있으면 저장하고 중단
                if grouped[Product_Profit_N_Price].sum() != 0:
                    # 가격의 합계 계산
                    grouped[Product_Profit_Sales_Qty] = df_filtered.groupby(current_group)[
                        Product_Profit_Sales_Qty].sum().values
                    # 수량의 합계 계산
                    grouped[Product_Profit_N_Price_Ave] = round(
                        grouped[Product_Profit_N_Price] / grouped[Product_Profit_Sales_Qty], 3)
                    # 평균 단가 계산
                    grouped[Product_Profit_C_Profit] = df_filtered.groupby(current_group)[
                        Product_Profit_C_Profit].sum().values
                    # 영업 이익 합계 계산
                    grouped[Product_Profit_C_Profit_Rate] = round(
                        grouped[Product_Profit_C_Profit] / grouped[Product_Profit_N_Price_Ave], 3)
                    # 평균 영업 이익 계산
                    grouped["CProfitAve"] = df_filtered.groupby(current_group)[Product_Profit_C_Profit].mean().values
                    # 영업 이익 평균 계산
                    grouped[Product_Profit_C_Profit_Rate_Ave] = round(
                        grouped["CProfitAve"] / grouped[Product_Profit_N_Price_Ave], 3)
                    # 평균 영억 이익 계산

                    result_list.append(grouped)
                    break

        if result_list:
            result = pd.concat(result_list, ignore_index=True)
        else:
            result = pd.DataFrame(
                columns=fixed_columns + [Product_Profit_N_Price, Product_Profit_Sales_Qty, Product_Profit_N_Price_Ave,
                                         Product_Profit_C_Profit,Product_Profit_C_Profit_Rate,
                                         Product_Profit_C_Profit_Rate_Ave,Item_Inch_COLUMN,Item_Marketing_Name_COLUMN,
                                         Item_KPI_COLUMN, Item_Series_COLUMN, Item_Strategy_COLUMN])
        return result


    df_in_ProductProfit_temp = conditional_group_sum(df_in_ProductProfit_temp)

    def set_null(df, columns):
        for column in columns:
            if df[column].isna().all() or df[column].empty:
                df[column] = ''
        return df

    col_list = [Item_Inch_COLUMN,Item_Marketing_Name_COLUMN, Item_KPI_COLUMN, Item_Series_COLUMN, Item_Strategy_COLUMN]

    df_in_ProductProfit_temp = set_null(df_in_ProductProfit_temp, col_list)

    print_df(df_in_ProductProfit_temp, 'df_in_ProductProfit_temp Step 4-2',True)

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) 주차 기간으로 설정된 부분의 빈 주차에 대해서 단가 정보 입력 (단가 데이블 생성)
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : input data machining')

    df_in_ProductProfit_temp[key_on] = 1
    df_in_Planning_Month[key_on] = 1
    df_in_ProductProfit_temp = df_in_ProductProfit_temp.merge(df_in_Planning_Month[[TimeMonth_COLUMN, key_on]],
                                                              on=key_on, how='inner')
    print_df(df_in_ProductProfit_temp, 'df_in_ProductProfit_temp Step 5-1',True)
    # df_in_ProductProfit_temp = df_in_ProductProfit_temp.rename(columns={'Time.[Planning Month]': TimeMonth_COLUMN})
    print_df(df_in_ProductProfit_temp, 'df_in_ProductProfit_temp Step 5-2',True)
    df_out_ProductProfit = df_in_ProductProfit_temp[~df_in_ProductProfit_temp.set_index(
        [Version_COLUMN, Item_COLUMN, TimeMonth_COLUMN, Sales_Domain_AP_COLUMN, Item_Product_Group_COLUMN,
         ]).index.isin(df_in_ProductProfit.set_index(
        [Version_COLUMN, Item_COLUMN, TimeMonth_COLUMN, Sales_Domain_AP_COLUMN, Item_Product_Group_COLUMN,
         ]).index)]


    df_out_ProductProfit.loc[:, [Data_Set_COLUMN]] = paramDataSet_VALUE
    df_out_ProductProfit.loc[:, [Product_Profit_C_Profit_Rate_F]] = ''
    df_out_ProductProfit.loc[:, [Product_Profit_N_Price_Currency]] = ''
    df_out_ProductProfit.loc[:, [Product_Profit_Profit_Grade]] = ''
    df_out_ProductProfit.loc[:, [Product_Profit_Profit_Rank]] = ''
    df_out_ProductProfit.loc[:, [Product_Profit_Rank]] = ''
    df_out_ProductProfit.loc[:, [Product_Profit_Product_Grade]] = ''

    print_df(df_out_ProductProfit, 'df_out_ProductProfit Step 5-3',True)

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 6. (1) 최종 데이터 추출을 위한 값 설정
    ################################################################################################################
    step(600, '=====> STEP 6(Start) : input data machining')
    filter_columns = [Version_COLUMN, Item_COLUMN, TimeMonth_COLUMN, Sales_Domain_AP_COLUMN, Data_Set_COLUMN,
                      Product_Profit_C_Profit,
                      Product_Profit_C_Profit_Rate, Product_Profit_C_Profit_Rate_Ave, Product_Profit_C_Profit_Rate_F,
                      Product_Profit_N_Price, Product_Profit_N_Price_Ave, Product_Profit_N_Price_Currency,
                      Product_Profit_Product_Grade, Product_Profit_Profit_Grade, Product_Profit_Profit_Rank,
                      Product_Profit_Rank,
                      Product_Profit_Sales_Qty]

    df_out_ProductProfit = df_out_ProductProfit[filter_columns]
    df_in_ProductProfit = df_in_ProductProfit[filter_columns]

    print_df(df_in_ProductProfit, 'df_in_ProductProfit')
    print_df(df_out_ProductProfit, 'df_out_ProductProfit')

    df_out_ProductProfit = pd.concat([df_in_ProductProfit, df_out_ProductProfit], axis=0)

    print_df(df_out_ProductProfit, 'df_out_ProductProfit',True)

    step(600, '=====> STEP 6(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 7. (1) 최종 Out_Put Save
    ################################################################################################################
    step(700, '=====> STEP 7(Start) : input data machining')

    row_count, col_count = df_out_ProductProfit.shape
    note(f'=====> Final df_out_ProductProfit rows : {row_count} , Columns : {col_count}')

    if is_local:
        note(f'=====> Final output table create')
        print_df(df_out_ProductProfit, 'df_out_ProductProfit',True)

    print_df(df_out_ProductProfit, 'df_out_ProductProfit',True)

    step(700, '=====> STEP 7(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg,p_log_level=LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_ProductProfit = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(800, '===================== plugin Execution End =====================')

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

