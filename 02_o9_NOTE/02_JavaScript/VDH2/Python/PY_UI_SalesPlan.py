"""
* 프로그램명
    - PY_UI_SalesPlan

* 내용
    - Sales PSI Data 생성

* 변경이력
    - 2024.09.23 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_LastSyncVersion : Select (&LastSyncVersion);
    - df_in_ProductLocation : Select ([Location].[Location] * [Location].[Location Type].[MF]);
    - df_in_HubLocation : Select ([Hub Location].[Hub Location]);
    - df_in_Demand     : Select (Version.[Version Name] * [Item].[Item]  * Location.[Location] * &MDMHorizon ) on row,  ({Measure.[W Demand Quantity to SCS],Measure.[W Demand Fulfilled Quantity],Measure.[W Total Short Quantity],Measure.[W OnHand Quantity],Measure.[W Beginning On Hand],Measure.[W Material Production Quantity Plan Output],Measure.[W Material Consumption Quantity Plan Output], Measure.[W Expected Receipts],Measure.[W Ending On Hand],Measure.[W Target Inventory],Measure.[W Infinite Material Node]}) on column orderby Time.Week.Name;
    - df_in_Intransit   : Select (Version.[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Documents].[OrderlineID] ) on row, ({Measure.[W Expected Receipts], Measure.[W Expected Receipts Backup], Measure.[W Expected Receipts Pegging ID], Measure.[W OnHand Dedication Policy], Measure.[W OnHand Pegging ID], Measure.[W OnHand Quantity], Measure.[W OnHand Quantity Backup], Measure.[W OnHand Quantity Increment %], Measure.[W OnHand Quantity Input], Measure.[W OnHand Quantity Override]}) on column;
    - df_in_SiteAP2Map  : Select (Version.[Version Name] * [Location].[Location] ) on row, ({Measure.[Site AP2 Map_GC], Measure.[Site AP2 Map_Ship To], Measure.[Site AP2 Map_Status], Measure.[Site AP2 Map_Valid Flag]}) on column;
    - df_in_SSMonitor   : Select (Version.[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SS Monitor_Shipment BuildAhead], Measure.[SS Monitor_SS Target Qty], Measure.[SS Monitor_SS Target Time], Measure.[SS Monitor_Shipment SS], Measure.[SS Monitor_Arrival SS]}) on column;
    - df_in_ShotMst     : Select (Version.[Version Name] * [Problem Type].[Short Reason] ) on row, ({Measure.[Problem Type_Report Category]}) on column;
    - df_in_ShortSolver : Select (Version.[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Sales Domain].[Customer Group] * [Problem Type].[Short Reason] ) on row, ({Measure.[Short Reason_Problem Qty]}) on column;

* Flow Summary
    -

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_SalesPlan

* 데이타 초기화
    - DELETE DATA FOR MODEL [Sales Plan] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SalesPlan] for measures {[Sales Plan_GI Qty]}
        using scope (&MPV.unionwith(&LastSyncVersion))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SalesPlan / MG:  Sales Plan
        Select (&MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sales Domain].[Ship To] ) on row, ({Measure.[Sales Plan_Dmd], Measure.[Sales Plan_RTF]
        , Measure.[Sales Plan_GI Qty], Measure.[Sales Plan_Sales], Measure.[Sales Plan_Short], Measure.[Sales Plan_Shipment], Measure.[Sales Plan_Short by ORG]
        , Measure.[Sales Plan_Dmd Up], Measure.[Sales Plan_Dmd Down], Measure.[Sales Plan_RTF UP], Measure.[Sales Plan_RTF DOWN], Measure.[Sales Plan_Short UP]
        , Measure.[Sales Plan_Short Down], Measure.[Sales Plan_Build Ahead], Measure.[Sales Plan_SS Target W], Measure.[Sales Plan_SS Target Q], Measure.[Sales Plan_SS Target Vio]}) on column;;
"""
import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SalesPlan'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)


########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
log_level_info = LOG_LEVEL.info()
log_level_debug = LOG_LEVEL.debug()
logger.debug(f'[START] {str_instance}')
logger.Start()


########################################################################################################################
# local function
########################################################################################################################
class CustomException(Exception):
    pass


def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def step(string):
    vdCommon.gfn_stepLog(string)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)



def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, logger, is_local, log_path)


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



def is_null_or_all(series):
    return series.isnull() | (series == 'ALL')


def is_all(series):
    return series.isnull() | (series == 'ALL')


def is_not_all(series):
    filled_series = series.fillna('ALL')
    return filled_series != 'ALL'


def replace_year(date_string, new_year):
    try:
        date_object = datetime.datetime.strptime(date_string, '%m/%d/%Y %I:%M:%S %p')
    except Exception as e1:
        try:
            date_object = datetime.datetime.strptime(date_string, '%Y/%m/%d %I:%M:%S %p')
        except Exception as e2:
            date_object = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    modified_date_object = date_object.replace(year=new_year)
    return modified_date_object.strftime('%Y-%m-%d')



########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # Batch 시작
    vd_log_start()

    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_LastSyncVersion = read_csv_file("df_in_LastSyncVersion")
            df_in_ProductLocation = read_csv_file("df_in_ProductLocation")
            df_in_HubLocation = read_csv_file("df_in_HubLocation")
            df_in_Demand = read_csv_file("df_in_Demand")
            df_in_SiteAP2Map = read_csv_file("df_in_SiteAP2Map")
            df_in_SSMonitor = read_csv_file("df_in_SSMonitor")
            df_in_ShotMst = read_csv_file("df_in_ShotMst")
            df_in_ShortSolver = read_csv_file("df_in_ShortSolver")
            df_in_Intransit = read_csv_file("df_in_Intransit")


        print_df(df_in_LastSyncVersion, 'input table load .... df_in_LastSyncVersion')
        print_df(df_in_ProductLocation, 'input table load .... df_in_ProductLocation')
        print_df(df_in_HubLocation, 'input table load .... df_in_HubLocation')
        print_df(df_in_Demand, 'input table load .... df_in_Demand')
        print_df(df_in_SiteAP2Map,'input table load .... df_in_SiteAP2Map')
        print_df(df_in_SSMonitor, 'input table load .... df_in_SSMonitor')
        print_df(df_in_ShotMst, 'input table load .... df_in_ShotMst')
        print_df(df_in_ShortSolver, 'input table load .... df_in_ShortSolver')
        print_df(df_in_Intransit, 'input table load .... df_in_Intransit')

        step('=====> STEP1 End')
        
        

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        LOCATION_X_COLUMN = 'Location.[Location]_x'
        LOCATION_Y_COLUMN = 'Location.[Location]_y'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_COLUMN = 'Item.[Item]'
        ORDERLINEID_COLUMN = 'Documents.[OrderlineID]'
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'

        DEMAND_TYPE_COLUMN = 'Demand Type.[Demand Type]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'
        W_DEMAND_QUANTITY_TO_SCS_COLUMN = 'W Demand Quantity to SCS'
        W_DEMAND_FULFILLED_QUANTITY_COLUMN = 'W Demand Fulfilled Quantity'
        W_TOTAL_SHORT_QUANTITY_COLUMN = 'W Total Short Quantity'
        W_DEMAND_QUANTITY_COLUMN = 'W Demand Quantity'
        W_BEGINNING_ON_HAND_COLUMN = 'W Beginning On Hand'
        W_ENDDING_ON_HAND_COLUMN = 'W Ending On Hand'
        W_ONHAND_QUANTITY_COLUMN = 'W OnHand Quantity'
        W_ACTIVITY_LEAD_TIME_COLUMN = 'W Activity Lead Time'
        W_TARGET_INVENTORY_COLUMN = 'W Target Inventory'
        W_EXPECTED_RECEIPTS_COLUMN = 'W Expected Receipts'
        W_INFINITE_METERIAL_NODE_COLUMN = 'W Infinite Material Node'
        W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN = 'W Material Production Quantity Plan Output'
        W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN = 'W Material Consumption Quantity Plan Output'
        SALES_DOMAIN_CUSTOMER_GROUP_COLUMN = 'Sales Domain.[Customer Group]'
        SALES_DOMAIN_SHIP_TO_COLUMN = 'Sales Domain.[Ship To]'

        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        SS_MONITOR_SHIPMENT_BUILDAHEAD_COLUMN = 'SS Monitor_Shipment BuildAhead'
        SS_MONITOR_SS_TARGET_QTY_COLUMN = 'SS Monitor_SS Target Qty'
        SS_MONITOR_SS_TARGET_TIME_COLUMN = 'SS Monitor_SS Target Time'
        SS_MONITOR_SHIPMENT_SS_COLUMN = 'SS Monitor_Shipment SS'
        SS_MONITOR_ARRIVAL_SS_COLUMN = 'SS Monitor_Arrival SS'

        SALES_PLAN_DMD_COLUMN = 'Sales Plan_Dmd'
        SALES_PLAN_RTF_COLUMN = 'Sales Plan_RTF'
        SALES_PLAN_GI_QTY_COLUMN = 'Sales Plan_GI Qty'
        SALES_PLAN_SALES_COLUMN = 'Sales Plan_Sales'
        SALES_PLAN_SHORT_COLUMN = 'Sales Plan_Short'
        SALES_PLAN_SHIPMENT_COLUMN = 'Sales Plan_Shipment'
        SALES_PLAN_SHORT_BY_ORG_COLUMN = 'Sales Plan_Short by ORG'
        SALES_PLAN_DMD_UP_COLUMN = 'Sales Plan_Dmd Up'
        SALES_PLAN_DMD_DOWN_COLUMN = 'Sales Plan_Dmd Down'
        SALES_PLAN_RTF_UP_COLUMN = 'Sales Plan_RTF UP'
        SALES_PLAN_RTF_DOWN_COLUMN = 'Sales Plan_RTF DOWN'
        SALES_PLAN_SHORT_UP_COLUMN = 'Sales Plan_Short UP'
        SALES_PLAN_SHORT_DOWN_COLUMN = 'Sales Plan_Short Down'
        SALES_PLAN_BUILD_AHEAD_COLUMN = 'Sales Plan_Build Ahead'
        SALES_PLAN_SS_TARGET_W_COLUMN = 'Sales Plan_SS Target W'
        SALES_PLAN_SS_TARGET_Q_COLUMN = 'Sales Plan_SS Target Q'
        SALES_PLAN_SS_TARGET_VIO_COLUMN = 'Sales Plan_SS Target Vio'
        SALES_PLAN_SHORT_INV_RISK_AP2_COLUMN = 'Sales Plan_Short-Inv Risk AP2'
        SALES_PLAN_SHORT_NO_ROUTE_COLUMN = 'Sales Plan_Short NO_Route'
        SALES_PLAN_SHORT_NO_BOM_COLUMN = 'Sales Plan_Short NO_BOM'
        SALES_PLAN_SHORT_NEW_MODEL_COLUMN = 'Sales Plan_Short New Model'
        SALES_PLAN_SHORT_CH_CONST_COLUMN = 'Sales Plan_Short CH Const'

        PROBLEM_TYPE_SHORT_REASON_COLUMN = 'Problem Type.[Short Reason]'
        PROBLEM_TYPE_REPORT_CATEGORY_COLUMN = 'Problem Type_Report Category'
        SHORT_REASON_PROBLEM_QTY_COLUMN = 'Short Reason_Problem Qty'
        SITE_AP2_MAP_SHIP_TO_COLUMN = 'Site AP2 Map_Ship To'
        
        SOURCE_VERSION = 'CWV_MP'

        df_short_solver_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN,
            PROBLEM_TYPE_SHORT_REASON_COLUMN, SHORT_REASON_PROBLEM_QTY_COLUMN,
        ]

        df_SalesPlan_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN,
            SALES_PLAN_DMD_COLUMN, SALES_PLAN_RTF_COLUMN, SALES_PLAN_GI_QTY_COLUMN, SALES_PLAN_SALES_COLUMN,
            SALES_PLAN_SHORT_COLUMN, SALES_PLAN_SHIPMENT_COLUMN, SALES_PLAN_SHORT_BY_ORG_COLUMN,
            SALES_PLAN_DMD_UP_COLUMN, SALES_PLAN_DMD_DOWN_COLUMN, SALES_PLAN_RTF_UP_COLUMN, SALES_PLAN_RTF_DOWN_COLUMN,
            SALES_PLAN_SHORT_UP_COLUMN, SALES_PLAN_SHORT_DOWN_COLUMN,
            SALES_PLAN_BUILD_AHEAD_COLUMN, SALES_PLAN_SS_TARGET_W_COLUMN, SALES_PLAN_SS_TARGET_Q_COLUMN,
            SALES_PLAN_SHORT_CH_CONST_COLUMN, SALES_PLAN_SHORT_INV_RISK_AP2_COLUMN, SALES_PLAN_SHORT_NEW_MODEL_COLUMN,
            SALES_PLAN_SHORT_NO_BOM_COLUMN, SALES_PLAN_SHORT_NO_ROUTE_COLUMN,
        ]
        
        step('=====> STEP2 End')




        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_Demand = df_in_Demand[df_in_Demand[ITEM_COLUMN] == 'CML400XJ']
        # ------------------ 테스트 디버깅용 ------------------ end



        # 이전버전 추출
        pre_version = str(get_first_value(df_in_LastSyncVersion, VERSION_NAME_COLUMN))
        step(f'=====> pre_version : {pre_version}')


        # pre_version 값이 없거나 None인 경우에 예외 발생
        if not pre_version:  # 값이 비어있거나 None이면 False로 평가됨
            raise CustomException("pre_version 값이 없습니다. 첫 번째 값을 확인하세요.")



        # df_in_SiteAP2Map 필요컬럼 추출
        df_in_SiteAP2Map = df_in_SiteAP2Map[[VERSION_NAME_COLUMN, LOCATION_COLUMN, SITE_AP2_MAP_SHIP_TO_COLUMN]].drop_duplicates()

        # 생산 Location 및 Hub Location concat
        df_ProdHubLocation = pd.concat([df_in_ProductLocation, df_in_HubLocation])
        df_ProdHubLocation = df_ProdHubLocation[[LOCATION_COLUMN]].drop_duplicates()

        if not df_in_ShortSolver.empty:
            set_group_by_columns = [VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, PROBLEM_TYPE_SHORT_REASON_COLUMN, SALES_DOMAIN_CUSTOMER_GROUP_COLUMN]
            set_sum_columns = [SHORT_REASON_PROBLEM_QTY_COLUMN]
            agg_dict = {col: 'sum' for col in set_sum_columns}

            df_short_solver = df_in_ShortSolver.groupby(set_group_by_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
            df_short_solver.rename(columns={SALES_DOMAIN_CUSTOMER_GROUP_COLUMN: SALES_DOMAIN_SHIP_TO_COLUMN},inplace=True)
            df_short_solver[SALES_DOMAIN_SHIP_TO_COLUMN] = df_short_solver[SALES_DOMAIN_SHIP_TO_COLUMN].astype(str)
            print_df(df_short_solver, 'STEP3 by 0.1  ____ df_short_solver .... groupby')

        else:
            df_short_solver = pd.DataFrame(columns=df_short_solver_columns)





        # ====================> df_in_Demand 제외 각 DF -> &LastSyncVersion 제외 filter (Start)
        df_in_SiteAP2Map = df_in_SiteAP2Map[df_in_SiteAP2Map[VERSION_NAME_COLUMN] != pre_version].copy()
        df_in_SSMonitor = df_in_SSMonitor[df_in_SSMonitor[VERSION_NAME_COLUMN] != pre_version].copy()
        df_in_ShotMst = df_in_ShotMst[df_in_ShotMst[VERSION_NAME_COLUMN] != pre_version].copy()
        df_in_ShortSolver = df_in_ShortSolver[df_in_ShortSolver[VERSION_NAME_COLUMN] != pre_version].copy()
        # ====================> df_in_Demand 제외 각 DF -> &LastSyncVersion 제외 filter (End)






        # ====================> STEP3 by 1 (Start) ->  df_in_Demand DataFrame modify

        # 1.1  df_in_Demand Version별 분리
        df_PeggingCurr = df_in_Demand[df_in_Demand[VERSION_NAME_COLUMN] == SOURCE_VERSION].copy()
        print_df(df_PeggingCurr, f'STEP3 by 1.1  ____ df_PeggingCurr .... version : {SOURCE_VERSION}')

        df_PeggingPrev = df_in_Demand[df_in_Demand[VERSION_NAME_COLUMN] == pre_version].copy()
        print_df(df_PeggingPrev, f'STEP3 by 1.2  ____ df_PeggingPrev .... version : {pre_version}')

        df_Pegging = pd.merge(df_PeggingCurr, df_PeggingPrev, how='left', on=[ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_Pegging, 'STEP3 by 1.3  ____ df_Pegging .... version merge[df_PeggingCurr, df_PeggingPrev]')

        int_columns = [W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x', W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x', W_TOTAL_SHORT_QUANTITY_COLUMN+'_x',
                       W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_y', W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_y', W_TOTAL_SHORT_QUANTITY_COLUMN+'_y',]
        for col in int_columns:
            df_Pegging[col] = df_Pegging[col].fillna(0).astype(int)

        print_df(df_Pegging, 'STEP3 by 1.4  ____ df_Pegging .... version merge final')


        # 2 UP, DOWN 설정
        #   2.1 Measure.[Sales Plan AP2_Dmd Up], Measure.[Sales Plan AP2_Dmd Down] 설정
        df_Pegging[SALES_PLAN_DMD_UP_COLUMN] = 0
        df_Pegging[SALES_PLAN_DMD_DOWN_COLUMN] = 0
        df_Pegging['DMD_DIFF'] = (df_Pegging[W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x'] - df_Pegging[W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_y'])

        #   2.2 조건에 따라 값을 설정 및 비교값 컬럼 삭제
        df_Pegging.loc[df_Pegging['DMD_DIFF'] > 0, SALES_PLAN_DMD_UP_COLUMN] = df_Pegging['DMD_DIFF']
        df_Pegging.loc[df_Pegging['DMD_DIFF'] < 0, SALES_PLAN_DMD_DOWN_COLUMN] = df_Pegging['DMD_DIFF']
        df_Pegging = df_Pegging.drop(columns=['DMD_DIFF'])

        #   2.3 Measure.[Sales Plan AP2_RTF UP], Measure.[Sales Plan AP2_RTF DOWN] 설정
        df_Pegging[SALES_PLAN_RTF_UP_COLUMN] = 0
        df_Pegging[SALES_PLAN_RTF_DOWN_COLUMN] = 0
        df_Pegging['RTF_DIFF'] = (df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x'] - df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_y'])

        #   2.4 조건에 따라 값을 설정 및 비교값 컬럼 삭제
        df_Pegging.loc[df_Pegging['RTF_DIFF'] > 0, SALES_PLAN_RTF_UP_COLUMN] = df_Pegging['RTF_DIFF']
        df_Pegging.loc[df_Pegging['RTF_DIFF'] < 0, SALES_PLAN_RTF_DOWN_COLUMN] = df_Pegging['RTF_DIFF']
        df_Pegging = df_Pegging.drop(columns=['RTF_DIFF'])

        #   2.5 Measure.[Sales Plan AP2_Short UP], Measure.[Sales Plan AP2_Short Down] 설정
        df_Pegging[SALES_PLAN_SHORT_UP_COLUMN] = 0
        df_Pegging[SALES_PLAN_SHORT_DOWN_COLUMN] = 0
        df_Pegging['SHORT_DIFF'] = (df_Pegging[W_TOTAL_SHORT_QUANTITY_COLUMN+'_x'] - df_Pegging[W_TOTAL_SHORT_QUANTITY_COLUMN+'_y'])

        #   2.6 조건에 따라 값을 설정 및 비교값 컬럼 삭제
        df_Pegging.loc[df_Pegging['SHORT_DIFF'] > 0, SALES_PLAN_SHORT_UP_COLUMN] = df_Pegging['SHORT_DIFF']
        df_Pegging.loc[df_Pegging['SHORT_DIFF'] < 0, SALES_PLAN_SHORT_DOWN_COLUMN] = df_Pegging['SHORT_DIFF']
        df_Pegging = df_Pegging.drop(columns=['SHORT_DIFF'])

        #   2.7 컬럼명 변경 및 추가
        df_Pegging[SALES_PLAN_DMD_COLUMN] = df_Pegging[W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x']
        df_Pegging[SALES_PLAN_RTF_COLUMN] = df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        df_Pegging[SALES_PLAN_GI_QTY_COLUMN] = df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        df_Pegging[SALES_PLAN_SALES_COLUMN] = df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        df_Pegging[SALES_PLAN_SHORT_COLUMN] = df_Pegging[W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x'] - df_Pegging[W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x']
        df_Pegging[SALES_PLAN_SHORT_BY_ORG_COLUMN] = df_Pegging[SALES_PLAN_SHORT_COLUMN]
        print_df(df_Pegging, 'STEP3 by 2.2 ____ df_Pegging .... column add')

        df_Pegging.rename(columns={
            VERSION_NAME_COLUMN+'_x': VERSION_NAME_COLUMN,
            W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x': W_DEMAND_QUANTITY_TO_SCS_COLUMN,
            W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x': W_DEMAND_FULFILLED_QUANTITY_COLUMN,
            W_TOTAL_SHORT_QUANTITY_COLUMN+'_x': W_TOTAL_SHORT_QUANTITY_COLUMN,
            W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN+'_x': W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN,
            W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN+'_x': W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN,
            W_ONHAND_QUANTITY_COLUMN+'_x': W_ONHAND_QUANTITY_COLUMN,
            W_BEGINNING_ON_HAND_COLUMN+'_x': W_BEGINNING_ON_HAND_COLUMN,
            W_EXPECTED_RECEIPTS_COLUMN+'_x': W_EXPECTED_RECEIPTS_COLUMN,
            W_ENDDING_ON_HAND_COLUMN+'_x': W_ENDDING_ON_HAND_COLUMN,
            W_INFINITE_METERIAL_NODE_COLUMN+'_x': W_INFINITE_METERIAL_NODE_COLUMN,
        }, inplace=True)
        print_df(df_Pegging, 'STEP3 by 2.2 ____ df_Pegging .... column rename')


        df_Pegging = df_Pegging.merge(df_in_Intransit, how='left',
                                      left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN],
                                      right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN])

        df_Pegging.rename(columns={
            W_DEMAND_QUANTITY_TO_SCS_COLUMN+'_x': W_DEMAND_QUANTITY_TO_SCS_COLUMN,
            W_DEMAND_FULFILLED_QUANTITY_COLUMN+'_x': W_DEMAND_FULFILLED_QUANTITY_COLUMN,
            W_TOTAL_SHORT_QUANTITY_COLUMN+'_x': W_TOTAL_SHORT_QUANTITY_COLUMN,
        }, inplace=True)
        print_df(df_Pegging, 'STEP3 by 2.3  ____ df_Pegging .... df_in_Intransit merge')


        # 2.4 df_Pegging final
        df_Pegging = df_Pegging[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ORDERLINEID_COLUMN,
            W_DEMAND_QUANTITY_TO_SCS_COLUMN, W_DEMAND_FULFILLED_QUANTITY_COLUMN, W_TOTAL_SHORT_QUANTITY_COLUMN,
            W_ENDDING_ON_HAND_COLUMN, W_BEGINNING_ON_HAND_COLUMN, W_INFINITE_METERIAL_NODE_COLUMN,
            W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN, W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN,
            SALES_PLAN_GI_QTY_COLUMN, SALES_PLAN_SALES_COLUMN,
            SALES_PLAN_DMD_COLUMN,  SALES_PLAN_DMD_UP_COLUMN, SALES_PLAN_DMD_DOWN_COLUMN,
            SALES_PLAN_SHORT_COLUMN, SALES_PLAN_SHORT_UP_COLUMN, SALES_PLAN_SHORT_DOWN_COLUMN,
            SALES_PLAN_RTF_COLUMN, SALES_PLAN_RTF_UP_COLUMN, SALES_PLAN_RTF_DOWN_COLUMN,
            SALES_PLAN_SHORT_BY_ORG_COLUMN,
        ]].drop_duplicates()

        print_df(df_Pegging, 'STEP3 by 2.4 ____ df_Pegging .... final')
        save_csv_file(df_Pegging, 'STEP3 by 2.4 ____ df_Pegging .... final')

        # ====================> STEP3 by 1 (End)



        # ====================> STEP3 by 2 (Start) -> df_SalesPlan 구성

        # 3.1 df_SalesPlan, df_in_SiteAP2Map join
        df_SalesPlan = pd.merge(df_Pegging, df_in_SiteAP2Map, how='left', on=[VERSION_NAME_COLUMN, LOCATION_COLUMN])
        print_df(df_SalesPlan, 'STEP3 by 3.1 ____ df_SalesPlan .... merge(df_SalesPlan, df_in_SiteAP2Map) 1')

        # df_SalesPlan[SITE_AP2_MAP_SHIP_TO_COLUMN] = df_SalesPlan[SITE_AP2_MAP_SHIP_TO_COLUMN].str.replace(r'\.0$', '', regex=True)

        # 3.2 df_SalesPlan, df_in_SSMonitor join
        df_SalesPlan = pd.merge(df_SalesPlan, df_in_SSMonitor, how='left',
                                left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN],
                                right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN,LOCATION_COLUMN])
        print_df(df_SalesPlan, 'STEP3 by 3.2 ____ df_SalesPlan .... merge')


        # 3.3 컬럼명 변경 및 설정
        #   3.3.1 Measure.[W Material Consumption Quantity Plan Output -> Activity 기준으로 To site 가져와서 Sub Location 에 설정
        df_SalesPlan[SALES_PLAN_SHIPMENT_COLUMN] = df_SalesPlan[W_METERIAL_CONSUMPTION_QUANTIRY_PLAN_OUTPUT_COLUMN]
        df_SalesPlan.rename(columns={
            SITE_AP2_MAP_SHIP_TO_COLUMN: SALES_DOMAIN_SHIP_TO_COLUMN,
            SS_MONITOR_SHIPMENT_BUILDAHEAD_COLUMN: SALES_PLAN_BUILD_AHEAD_COLUMN,
            SS_MONITOR_SS_TARGET_QTY_COLUMN: SALES_PLAN_SS_TARGET_W_COLUMN,
            SS_MONITOR_SS_TARGET_TIME_COLUMN: SALES_PLAN_SS_TARGET_Q_COLUMN,
        }, inplace=True)
        df_SalesPlan = df_SalesPlan.replace({pd.NA: None, np.nan: None, '<NA>': None, 0: None, '0': None})

        str_columns = [LOCATION_COLUMN, ITEM_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN]
        for col in str_columns:
            df_SalesPlan[col] = df_SalesPlan[col].fillna('-').astype(str)

        print_df(df_SalesPlan, 'STEP3 by 3.3 ____ df_SalesPlan .... final')


        # 3.4 Short Reason 설정
        df_SalesPlan = pd.merge(df_SalesPlan, df_short_solver, how='left',
                                on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN])
        print_df(df_SalesPlan, 'STEP3 by 3.4 ____ df_SalesPlan .... df_short_solver merge')

        df_SalesPlan[SALES_PLAN_SHORT_CH_CONST_COLUMN] = 0
        df_SalesPlan[SALES_PLAN_SHORT_INV_RISK_AP2_COLUMN] = 0
        df_SalesPlan[SALES_PLAN_SHORT_NEW_MODEL_COLUMN] = 0
        df_SalesPlan[SALES_PLAN_SHORT_NO_BOM_COLUMN] = 0
        df_SalesPlan[SALES_PLAN_SHORT_NO_ROUTE_COLUMN] = 0

        df_SalesPlan.loc[df_SalesPlan[PROBLEM_TYPE_SHORT_REASON_COLUMN] == 'NO BOM', SALES_PLAN_SHORT_NO_BOM_COLUMN] = df_SalesPlan[SHORT_REASON_PROBLEM_QTY_COLUMN]
        df_SalesPlan.loc[df_SalesPlan[PROBLEM_TYPE_SHORT_REASON_COLUMN] == 'NO_ROUTING', SALES_PLAN_SHORT_NO_ROUTE_COLUMN] = df_SalesPlan[SHORT_REASON_PROBLEM_QTY_COLUMN]
        df_SalesPlan.loc[df_SalesPlan[PROBLEM_TYPE_SHORT_REASON_COLUMN] == 'CH_CONSTRAINT', SALES_PLAN_SHORT_CH_CONST_COLUMN] = df_SalesPlan[SHORT_REASON_PROBLEM_QTY_COLUMN]
        df_SalesPlan.loc[df_SalesPlan[PROBLEM_TYPE_SHORT_REASON_COLUMN] == 'NEW_MODEL', SALES_PLAN_SHORT_NEW_MODEL_COLUMN] = df_SalesPlan[SHORT_REASON_PROBLEM_QTY_COLUMN]
        df_SalesPlan.loc[df_SalesPlan[PROBLEM_TYPE_SHORT_REASON_COLUMN] == 'INV_RISK_AP2', SALES_PLAN_SHORT_INV_RISK_AP2_COLUMN] = df_SalesPlan[SHORT_REASON_PROBLEM_QTY_COLUMN]

        int_columns = [SALES_PLAN_SHORT_CH_CONST_COLUMN, SALES_PLAN_SHORT_INV_RISK_AP2_COLUMN, SALES_PLAN_SHORT_NEW_MODEL_COLUMN,
                       SALES_PLAN_SHORT_NO_BOM_COLUMN, SALES_PLAN_SHORT_NO_ROUTE_COLUMN]
        for col in int_columns:
            df_SalesPlan[col] = df_SalesPlan[col].astype('int64')

        print_df(df_SalesPlan, 'STEP3 by 3.4 ____ df_SalesPlan .... final')

        # ====================> STEP3 by 2 (End)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_out_SalesPlan = rename_and_delete_df(df_SalesPlan)

        # 생산 및 Hub Location 제외
        df_out_SalesPlan = df_out_SalesPlan[~df_out_SalesPlan[LOCATION_COLUMN].isin(df_ProdHubLocation[LOCATION_COLUMN].tolist())].copy()
        df_out_SalesPlan = df_out_SalesPlan[df_SalesPlan_columns].drop_duplicates()

        # 버전 처리
        df_out_SalesPlan[VERSION_NAME_COLUMN] = paramOutVersion
        print_df(df_out_SalesPlan, 'STEP4 ____ df_out_SalesPlan')

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_SalesPlan, 'output table create .... df_out_SalesPlan', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()
        
    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SalesPlan = pd.DataFrame(columns=df_SalesPlan_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SalesPlan = pd.DataFrame(columns=df_SalesPlan_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
