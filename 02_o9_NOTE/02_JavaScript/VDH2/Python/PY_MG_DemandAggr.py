

"""

* 프로그램명
    - PY_MG_DemandAggr

* 내용
     -



* 변경이력
- 2024.11.28 / de0413.shin (신동언) / Create

* Input
- df_in_PlanStartWeek  = pd.read_csv('df_in_PlanStartWeek.csv')
- df_in_DemandAggrRule = pd.read_csv('df_in_DemandAggrRule.csv')
- df_in_DemandQuantityAggr = pd.read_csv('df_in_DemandQuantityAggr.csv')
- df_in_SalesDomain  = pd.read_csv('df_in_SalesDomain.csv')

* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.


* Input Table
   - df_in_PlanStartWeek = Select ([Version].[Version Name]) on row,
                                   ({Measure.[MP Plan Current Week], Measure.[MP Plan End Date], Measure.[MP Plan End Week], Measure.[MP Plan Start Date], Measure.[MP Plan Start Week]}) on column;
   - df_in_DemandAggrRule = Select ([Version].[Version Name] * [Sequence].[Sequence] ) on row, ({Measure.[Dmd Aggr Rule_Aggr Ctg], Measure.[Dmd Aggr Rule_Aggr End Week], Measure.[Dmd Aggr Rule_Aggr Level], Measure.[Dmd Aggr Rule_Aggr Start Week]}) on column;
   - df_in_DemandQuantityAggr = Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row,
                                       ({Measure.[W Demand Quantity Aggr], Measure.[W Demand Quantity to SCS], Measure.[W Demand Build Ahead Limit],  Measure.[W Demand Build Late Limit],
                                         Measure.[W Demand Fulfilment Policy], Measure.[W Demand Layer], Measure.[W Demand Leadtime Due],  Measure.[W Demand Plan Date Offset],
                                         Measure.[W Demand Priority], Measure.[W Demand Priority to Final SCS],  Measure.[W Demand SS PreBuild],  Measure.[W Demand Short Code],
                                            Measure.[W Demand Split]}) on column where { Measure.[W Demand Quantity to SCS] > 0 };
   - df_in_SalesDomain = Select ([Sales Domain].[AP1] * [Sales Domain].[AP2] * [Sales Domain].[Customer Group]);
   - df_in_Location  = select ([Location].[Location] * [Location].[Rep Location]);

* Output Table
    - df_out_DemandQuantityAggr = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row,
                                   ({Measure.[W Demand Quantity Aggr]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_DemandAggr] for Measures {[W Demand Quantity Aggr]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView"})) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};



실행 전 프로시져를 통해 MF Site 삭제  필요

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
str_instance = 'PY_MG_DemandAggr'
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

def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    Logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')

def fn_math(val1,val2):
    return math.trunc(val1 / val2) * val2


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

        df_in_PlanStartWeek  = read_csv_file("df_in_PlanStartWeek")

        df_in_DemandAggrRule = read_csv_file('df_in_DemandAggrRule')

        df_in_DemandQuantityAggr = read_csv_file('df_in_DemandQuantityAggr')

        df_in_SalesDomain = read_csv_file('df_in_SalesDomain')

        df_in_Location = read_csv_file('df_in_Location')

    if df_in_PlanStartWeek.empty:
        raise Exception("Exception: df_in_PlanStartWeek.empty is empty")
    if df_in_DemandAggrRule.empty:
        raise Exception("Exception: df_in_DemandAggrRule is empty")
    if df_in_DemandQuantityAggr.empty:
        raise Exception("Exception: df_in_DemandQuantityAggr is empty")
    if df_in_SalesDomain.empty:
        raise Exception("Exception: df_in_SalesDomain is empty")
    if df_in_Location.empty:
        raise Exception("Exception: df_in_Location is empty")

    note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_PlanStartWeek, 'df_in_PlanStartWeek')
    print_df(df_in_DemandAggrRule, 'df_in_DemandAggrRule')
    print_df(df_in_DemandQuantityAggr, 'df_in_DemandQuantityAggr')
    print_df(df_in_SalesDomain,'df_in_SalesDomain')
    print_df(df_in_Location,'df_in_Location')

    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2 (1) 데이터 프레임 변수 지정 및 이름 변경
    ################################################################################################################

    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')
    print_df(df_in_Location, 'df_in_Location200')
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    SEQUENCE_SEQUENCE = 'Sequence.[Sequence]'
    PLAN_START_WEEK   = 'MP Plan Start Week'

    Rule_Aggr_Ctg   = 'Dmd Aggr Rule_Aggr Ctg'
    Rule_Aggr_Level = 'Dmd Aggr Rule_Aggr Level'
    Rule_Aggr_Start_Week = 'Dmd Aggr Rule_Aggr Start Week'

    SALES_DOMAIN_GROUP =  'Sales Domain.[Customer Group]'
    SALES_DOMAIN_AP1 = 'Sales Domain.[AP1]'
    SALES_DOMAIN_AP2 = 'Sales Domain.[AP2]'
    print_df(df_in_Location, 'df_in_Location200 End')
    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 out 데이터 프레임 크기 확인 및 저장
    ###############################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    print_df(df_in_Location, 'df_in_Location300 Start')
    col_list = [VERSION_NAME_COLUMN, 'Item.[Item]', 'Time.[Week]', 'Location.[Location]', SALES_DOMAIN_GROUP, 'Demand Type.[Demand Type]', 'Demand.[DemandID]', 'W Demand Quantity Aggr', 'W Demand Quantity to SCS',
                'W Demand Build Ahead Limit', 'W Demand Build Late Limit', 'W Demand Fulfilment Policy', 'W Demand Layer', 'W Demand Leadtime Due', 'W Demand Plan Date Offset', 'W Demand Priority', 'W Demand Priority to Final SCS',
                'W Demand SS PreBuild', 'W Demand Short Code', 'W Demand Split']

    vWeek = df_in_DemandAggrRule.loc[df_in_DemandAggrRule[Rule_Aggr_Ctg] == 'Sales Level', Rule_Aggr_Start_Week].item()

    df_in_PlanStartWeek = df_in_PlanStartWeek.astype({PLAN_START_WEEK: 'str'}, copy=True)

    df_in_DemandQuantityAggr['vNextWeek'] = df_in_PlanStartWeek[PLAN_START_WEEK].apply(lambda x: com.gfn_add_week(x, (int(vWeek) - 1)))

    vNextWeek = df_in_DemandQuantityAggr.loc[0, "vNextWeek"]

    print(vNextWeek)

    df_in_DemandQuantityAggr["Time.[Week]"] = df_in_DemandQuantityAggr["Time.[Week]"].astype('int')

    df_in_plan_prev = df_in_DemandQuantityAggr.loc[(df_in_DemandQuantityAggr["Time.[Week]"] < int(vNextWeek))].copy()
    df_in_plan = df_in_DemandQuantityAggr.loc[(df_in_DemandQuantityAggr["Time.[Week]"] >= int(vNextWeek))].copy()

    df_in_plan = df_in_plan.astype({SALES_DOMAIN_GROUP: 'str'}, copy=True)

    df_in_plan = df_in_plan.merge(df_in_SalesDomain,on=[SALES_DOMAIN_GROUP], how='inner')

    df_in_plan[SALES_DOMAIN_GROUP] = df_in_plan[SALES_DOMAIN_AP2]

    df_in_Plan_prev = df_in_plan_prev[col_list]
    df_out_plan = pd.concat([df_in_plan_prev, df_in_plan], axis=0)

    df_out_sales  = df_out_plan[col_list]

    print_df(df_out_sales, 'df_out_sales')

    del vWeek, vNextWeek
    del df_in_plan,df_in_plan_prev,df_out_plan

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4 out 데이터 프레임 크기 확인 및 저장
    ###############################################################################################################
    step(400, '=====> STEP 4(Start) : input data machining')

    col_list = [VERSION_NAME_COLUMN, 'Item.[Item]', 'Time.[Week]', 'Location.[Location]', SALES_DOMAIN_GROUP, 'Demand Type.[Demand Type]', 'Demand.[DemandID]', 'W Demand Quantity Aggr', 'W Demand Quantity to SCS',
                'W Demand Build Ahead Limit', 'W Demand Build Late Limit', 'W Demand Fulfilment Policy',
                'W Demand Layer', 'W Demand Leadtime Due', 'W Demand Plan Date Offset', 'W Demand Priority',
                'W Demand Priority to Final SCS','W Demand SS PreBuild', 'W Demand Short Code', 'W Demand Split']

    vWeek = df_in_DemandAggrRule.loc[df_in_DemandAggrRule[Rule_Aggr_Ctg] == 'Demand Type Level', Rule_Aggr_Start_Week].item()
    vLevel = df_in_DemandAggrRule.loc[df_in_DemandAggrRule[Rule_Aggr_Ctg] == 'Demand Type Level', Rule_Aggr_Level].item()

    note('410 Start')
    note(vWeek)
    note(vLevel)

    df_in_PlanStartWeek = df_in_PlanStartWeek.astype({PLAN_START_WEEK: 'str'}, copy=True)
    df_out_sales['vNextWeek'] = df_in_PlanStartWeek[PLAN_START_WEEK].apply(lambda x: com.gfn_add_week(x, (int(vWeek) - 1)))

    print_df(df_out_sales, 'df_out_sales')

    vNextWeek = df_out_sales["vNextWeek"][0].unique()

    df_in_plan_prev = df_out_sales.loc[(df_out_sales["Time.[Week]"] < int(vNextWeek))].copy()

    df_in_plan = df_out_sales.loc[(df_out_sales["Time.[Week]"] >= int(vNextWeek))].copy()

    df_in_plan["Demand Type.[Demand Type]"] = vLevel

    df_in_Plan_prev = df_in_plan_prev[col_list]

    df_out_plan = pd.concat([df_in_plan_prev, df_in_plan], axis=0)

    df_out_Demand = df_out_plan[col_list]

    print_df(df_out_Demand, 'df_out_Demand')

    del vWeek, vNextWeek
    del df_in_plan, df_in_plan_prev, df_out_plan

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5 out 데이터 프레임 크기 확인 및 저장
    ###############################################################################################################
    step(500, '=====> STEP 5(Start) : input data machining')

    col_list = [VERSION_NAME_COLUMN, 'Item.[Item]', 'Time.[Week]', 'Location.[Location]', SALES_DOMAIN_GROUP,
                'Demand Type.[Demand Type]', 'Demand.[DemandID]', 'W Demand Quantity Aggr', 'W Demand Quantity to SCS',
                'W Demand Build Ahead Limit', 'W Demand Build Late Limit', 'W Demand Fulfilment Policy',
                'W Demand Layer', 'W Demand Leadtime Due', 'W Demand Plan Date Offset', 'W Demand Priority',
                'W Demand Priority to Final SCS',
                'W Demand SS PreBuild', 'W Demand Short Code', 'W Demand Split']

    df_out_Site = df_out_Demand[col_list]

    vWeek = df_in_DemandAggrRule.loc[df_in_DemandAggrRule[Rule_Aggr_Ctg] == 'Site Level', Rule_Aggr_Start_Week].item()

    note('510 Start')
    note(vWeek)

    df_in_PlanStartWeek = df_in_PlanStartWeek.astype({PLAN_START_WEEK: 'str'}, copy=True)

    df_out_Site['vNextWeek'] = df_in_PlanStartWeek[PLAN_START_WEEK].apply(lambda x: com.gfn_add_week(x, (int(vWeek) - 1)))

    print_df(df_out_Site, 'df_out_Site')

    vNextWeek = df_out_Site["vNextWeek"][0].unique()

    df_in_plan_prev = df_out_Site.loc[(df_out_Site["Time.[Week]"] < int(vNextWeek))].copy()

    df_in_plan = df_out_Site.loc[(df_out_Site["Time.[Week]"] >= int(vNextWeek))].copy()

    df_in_plan = pd.merge(df_in_plan, df_in_Location, how='left', on='Location.[Location]',  indicator=True)

    df_in_plan['Location.[Location]'] = np.where(df_in_plan['Location.[Rep Location]'].str.contains('both'),df_in_plan['Location.[Location]'] , df_in_plan['Location.[Rep Location]'])

    df_in_plan = df_in_plan[col_list]

    df_in_Plan_prev = df_in_plan_prev[col_list]

    df_out_plan = pd.concat([df_in_plan_prev, df_in_plan], axis=0)

    df_out_Location = df_out_plan[col_list]

    print_df(df_out_Location, 'df_out_Location')
    note('520 Start')
    df_out_DemandQuantity1 = df_out_Location.copy()
    df_out_DemandQuantity2 = df_out_Location.copy()

    print_df(df_out_DemandQuantity1, 'df_out_DemandQuantity1')

    note('530 Start')
    df_out_DemandQuantity1 = df_out_DemandQuantity1.groupby([VERSION_NAME_COLUMN, 'Item.[Item]', 'Time.[Week]', 'Location.[Location]','Sales Domain.[Customer Group]', 'Demand Type.[Demand Type]'], as_index=False).agg(Sum_qty=('W Demand Quantity to SCS', 'sum'),
                                                                                                                                                                                                                         Min_Demand=('Demand.[DemandID]','min'),
                                                                                                                                                                                                                         Min_W_Demand_Build_Ahead_Limit = ('W Demand Build Ahead Limit','min'),
                                                                                                                                                                                                                         Min_W_Demand_Build_Late_Limit  = ('W Demand Build Late Limit','min'),
                                                                                                                                                                                                                         Min_W_Demand_Fulfilment_Policy = ('W Demand Fulfilment Policy','min'),
                                                                                                                                                                                                                         Min_W_Demand_Layer = ('W Demand Layer','min'),
                                                                                                                                                                                                                         Min_W_Demand_Leadtime_Due = ('W Demand Leadtime Due', 'min'),
                                                                                                                                                                                                                         Min_W_Demand_Plan_Date_Offset = ('W Demand Plan Date Offset','min'),
                                                                                                                                                                                                                         Min_W_Demand_Priority = ('W Demand Priority','min'),
                                                                                                                                                                                                                         Min_W_Demand_Priority_to_Final_SCS = ('W Demand Priority to Final SCS','min'),
                                                                                                                                                                                                                         Min_W_Demand_SS_PreBuild = ('W Demand SS PreBuild','min'),
                                                                                                                                                                                                                         Min_W_Demand_Short_Code = ('W Demand Short Code', 'min'),
                                                                                                                                                                                                                         Min_W_Demand_Split = ('W Demand Split','min'))

    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_Demand' : 'Demand.[DemandID]'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Build_Ahead_Limit' : 'W Demand Build Ahead Limit'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Build_Late_Limit' : 'W Demand Build Late Limit'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Fulfilment_Policy' : 'W Demand Fulfilment Policy'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Layer' : 'W Demand Layer'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Leadtime_Due' : 'W Demand Leadtime Due'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Plan_Date_Offset' : 'W Demand Plan Date Offset'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Priority' : 'W Demand Priority'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Priority_to_Final_SCS' : 'W Demand Priority to Final SCS'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_SS_PreBuild' : 'W Demand SS PreBuild'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Short_Code' : 'W Demand Short Code'})
    df_out_DemandQuantity1 = df_out_DemandQuantity1.rename(columns={'Min_W_Demand_Split' : 'W Demand Split'})

    print_df(df_out_DemandQuantity1, 'df_out_DemandQuantity1')

    note('550 Start')
    df_out_DemandQuantityAggr = df_out_DemandQuantity1

    df_out_DemandQuantityAggr['W Demand Quantity Aggr'] =  df_out_DemandQuantityAggr['Sum_qty']
    df_out_DemandQuantityAggr = df_out_DemandQuantityAggr[[VERSION_NAME_COLUMN, 'Item.[Item]', 'Time.[Week]', 'Location.[Location]','Sales Domain.[Customer Group]', 'Demand Type.[Demand Type]','Demand.[DemandID]','W Demand Quantity Aggr',
                                                           'W Demand Build Ahead Limit', 'W Demand Build Late Limit',
                                                           'W Demand Fulfilment Policy',
                                                           'W Demand Layer', 'W Demand Leadtime Due',
                                                           'W Demand Plan Date Offset', 'W Demand Priority',
                                                           'W Demand Priority to Final SCS',
                                                           'W Demand SS PreBuild', 'W Demand Short Code',
                                                           'W Demand Split']]

    print_df(df_out_DemandQuantityAggr, 'df_out_DemandQuantityAggr')

    if is_local:
        step(511, '=====> Output csv create')
        save_csv_file(df_out_DemandQuantityAggr, 'df_out_DemandQuantityAggr')

    del vWeek, vNextWeek
    del df_in_plan, df_in_plan_prev, df_out_plan
    del df_out_DemandQuantity1,  df_out_Site, df_out_Demand, df_out_sales

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')
    step(509, '=====> STEP 5(End) : Check memory usage & runtime')

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
    step(800, '===================== plugin Execution End =====================')

finally:
    Logger.Finish()
