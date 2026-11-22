"""
* 프로그램명
    - PY_UI_SSMonitor.py
* 내용
    - Safety Stock Monitoring 화면 조회용 데이타 생성

* 변경이력
    - 2025.03.21 /  강유숙 / 재생성
    - 2025.04.01 /  강유숙/ BOD LT 감소 추이 일때 계산 로직 변경
    - 2025.04.14 / 강유숙/ BOD LT Input Data 변경
        L/T 디폴트 메져그룹 :001.007W Solver Inputs Activity Parameters 추가함.
        변경된 주차의 L/T 메져그룹: 001.49W Activity Lead Time Time Varying
    - 2025.05.23 / 강유숙 / BOD LT Input Data 처리 로직 수정
       Measure.[W Activity Lead Time Time Varying], Measure.[W Activity Lead Time] 데이타를 일자로 변환함.
    - 2025.05.27/ 강유숙 / 소수점 2자리까지 처리함.
    - 2025.05.29/강유숙 / LastSyncVersion 버젼의 LastPastWeek 주차를 조회하여 실적으로 처리함.
    - 2025.06.19/강유숙 / SHIPMENT-Buildahead 메져 계산 로직 수정
        df_in_EOH_SAFETYSTOCK,  df_in_Demand_GI_SHORT 개별적으로 조회하도록 수정함.
    - 2025.10.02 /강유숙 / df_in_SS_Prty_Location 추가함.
    - 2026.02.03 safetyStock_CreateDictionary() STOCK_WEEK >= 0 변경함.
    - 2026.02.27 df_in_SAFETYSTOCK InputData Where 조건 수정
    - 2026.02.27 df_temp_week_safetystock 형변환
    - 2026.03.26 df_in_GI 메져그룹 변경됨 : 001.003W Demand Analytics => Sales PSI AP2 W 베져그룹의  Measure.[Sales PSI AP2 W_GI Qty]
    - 2026.04.16 Exception 표준 처리

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_SS_Prty_Location
      (1) SS Prty
      (2) 조회된  Location 기준으로 데이타 산출
        Select (&CWVUI * [Location].[Location].filter(#.[Location Valid Flag]==true) ) on row,
        ({Measure.[SS Prty_Must Flag], Measure.[SS Prty_Must Flag Override], Measure.[SS Prty_Prty],
         Measure.[SS Prty_Prty Override]}) on column;

    - df_in_Demand
      (1) Demand : 001.018W Solver Inputs Demand Time Granularity
      (2) Location(SubLocation) + Item + Week + Sales Domain(AP2) 별  Measure.[W Demand Quantity to SCS]값을 집계함.
       //Demand Qty
        Select ( &CWVUI * [Location].[Location].filter(#.[Location Valid Flag]==true) * [Item].[Item] * &MDMHorizon * [Sales Domain].[AP2]) on row,
        ({Measure.[W Demand Quantity to SCS]}) on column
        Where {[Sales Domain].[Customer Group], [Demand Type].[Demand Type], [Demand].[DemandID]} ;

    - df_in_GI (2026.03.26 변경함.)
      (1) GI     : Sales PSI AP2 W
      (2) Location(SubLocation) + Item + Week + Sales Domain(AP2) 별  Measure.[Sales PSI AP2 W_GI Qty] 값을 집계함.
       //GI Qty
        Select (&CWVUI * [Sales Domain].[AP2] * [Location].[Location] * [Item].[Item] * [Time].[Week] ) on row,
        ({Measure.[Sales PSI AP2 W_GI Qty]}) on column
        Where{[Trans Mode].[Trans Mode], [Sub Location].[Sub Location] } limit 100;

    - df_in_SHORT
      (1) SHORT  : 002.001W Solver Ouputs Delivery Plan
      (2) Location(SubLocation) + Item + Week + Sales Domain(AP2) 별  Measure.[W Demand Quantity to SCS]값을 집계함.
       //SHORT QTY
        Select ( &CWVUI * [Location].[Location].filter(#.[Location Valid Flag]==true) * [Item].[Item] * &MDMHorizon* [Sales Domain].[AP2]) on row,
        ({Measure.[W Total Short Quantity]}) on column
        Where {[Sales Domain].[Customer Group], [Demand Type].[Demand Type], [Demand].[DemandID]} ;

    - df_in_EOH
        (1) EOH   : 002.005W Solver Outputs Inventory Plan
        (2) Location Type DC(?)인 경우만..
        Select (&CWVUI * [Location].[Location].filter(#.[Location Valid Flag]==true) * [Item].[Item] * &MDMHorizon) on row,
        ({Measure.[W Ending On Hand]}) on column
        Where{[Location].[Location Type].filter(#.Name == "DC")};

    - df_in_SAFETYSTOCK
        (1) SAFETY SOTCK : 001.019W Solver Inputs Inventory Inputs
        (2) Location Type DC(?)인 경우만..
        Select (&CWVUI * [Location].[Location].filter(#.[Location Valid Flag]==true) * [Item].[Item] * &MDMHorizon) on row,
        ({Measure.[W Quantity Min Target], Measure.[W Target Inventory],Measure.[W WOS Target]}) on column
        Where{[Location].[Location Type].filter(#.Name == "DC"), association(~Isnull(Measure.[W Target Inventory]))};

    - df_in_Buildhead_Setting
     * MG Name : 001.011W Solver Inputs Inventory Node Parameters
       Select (&CWVUI * [Item].[Item] * [Location].[Location].filter(#.[Location Valid Flag]==true) ) on row,
       ({Measure.[W SS Build Ahead Limit]}) on column;

    - df_in_SubLocation
        (1) Sub Location 정보 조회
        Select ([Sub Location].[Sub Location] * [Sub Location].[Sub Location Rep AP2].filter(~(#.Name in {"All", "-"})));

    - df_in_Arrival
        (1) Arrival : 002.003W Solver Outputs Material Production Plan
        (2) Activity1.[Activity1] 값 FromLocation _SubLocation_TransMode
         Select ( &CWVUI * [Item].[Item] * &MDMHorizon * [Location].[Location].filter(#.[Location Valid Flag]==true)
        * &AllBODLanes ) on row,
        ({Measure.[W Material Production Quantity Plan Output]}) on column
        Where {[Documents].[OrderlineID],[Activity2].[Activity2], [Activity3].[Activity3] };

    - df_in_Shipment
        (1) Shipment : 002.002W Solver Outputs Material Consumption Plan
        (2) Activity1.[Activity1] 값 FromLocation _SubLocation_TransMode
        Location.[Location] : Sub Location.[Sub Location]
        Select ( &CWVUI * [Item].[Item] *
                &MDMHorizon * [Location].[Location].filter(#.[Location Valid Flag]==true) *  &AllBODLanes ) on row,
        ({Measure.[W Material Consumption Quantity Plan Output]}) on column
        Where {[Documents].[OrderlineID],[Activity2].[Activity2], [Activity3].[Activity3] };

    - df_in_BOD_ITEM_LT
        * MG Name : 001.007W Solver Inputs Activity Parameters
        Select (&CWVUI * &AllBODLanes * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Lead Time]}) on column;

    - df_in_BOD_ITEM_LT_W
        * MG Name : 001.49W Activity Lead Time Time Varying
        Select (&CWVUI * &MDMHorizon * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Lead Time Time Varying]}) on column;

    - df_in_Time
        Select (&MDMHorizon. unionwith(&LastPastWeek) * Time.[Day] * Time.[Day of Week].[MON]) ;

    - df_in_Pre_SS_Monitor_SUM
    Select (&LastSyncVersion * [Location].[Location].[-] * [Item].[Item] * &LastPastWeek * [Sales Domain].[AP2]
        * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode].[-] ) on row,
    ({Measure.[SS Monitor_Arrival], Measure.[SS Monitor_Arrival BuildAhead], Measure.[SS Monitor_Arrival BuildAhead 1W],
    Measure.[SS Monitor_Arrival BuildAhead 2W], Measure.[SS Monitor_Arrival BuildAhead 3W~],
    Measure.[SS Monitor_Arrival JIT], Measure.[SS Monitor_Arrival SS], Measure.[SS Monitor_Arrival SS 1W],
    Measure.[SS Monitor_Arrival SS 2W], Measure.[SS Monitor_Arrival SS 3W~], Measure.[SS Monitor_BuildAhead Limit],
    Measure.[SS Monitor_Demand], Measure.[SS Monitor_EOH], Measure.[SS Monitor_GI], Measure.[SS Monitor_Item BOD LT],
    Measure.[SS Monitor_SS], Measure.[SS Monitor_SS Short], Measure.[SS Monitor_SS Target Qty],
    Measure.[SS Monitor_SS Target Time], Measure.[SS Monitor_Shipment], Measure.[SS Monitor_Shipment BuildAhead],
    Measure.[SS Monitor_Shipment BuildAhead 1W], Measure.[SS Monitor_Shipment BuildAhead 2W],
    Measure.[SS Monitor_Shipment BuildAhead 3W~], Measure.[SS Monitor_Shipment JIT], Measure.[SS Monitor_Shipment SS],
    Measure.[SS Monitor_Shipment SS 1W], Measure.[SS Monitor_Shipment SS 2W], Measure.[SS Monitor_Shipment SS 3W~],
    Measure.[SS Monitor_Short]}) on column;

    - df_in_Pre_SS_Monitor_ROW
    Select (&LastSyncVersion * [Location].[Location].filter(~(#.Name == "-")) * [Item].[Item] * &LastPastWeek * [Sales Domain].[AP2]
        * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode].filter(~(#.Name == "-"))  ) on row,
    ({Measure.[SS Monitor_Arrival], Measure.[SS Monitor_Arrival BuildAhead], Measure.[SS Monitor_Arrival BuildAhead 1W],
    Measure.[SS Monitor_Arrival BuildAhead 2W], Measure.[SS Monitor_Arrival BuildAhead 3W~],
    Measure.[SS Monitor_Arrival JIT], Measure.[SS Monitor_Arrival SS], Measure.[SS Monitor_Arrival SS 1W],
    Measure.[SS Monitor_Arrival SS 2W], Measure.[SS Monitor_Arrival SS 3W~], Measure.[SS Monitor_BuildAhead Limit],
    Measure.[SS Monitor_Demand], Measure.[SS Monitor_EOH], Measure.[SS Monitor_GI], Measure.[SS Monitor_Item BOD LT],
    Measure.[SS Monitor_SS], Measure.[SS Monitor_SS Short], Measure.[SS Monitor_SS Target Qty],
    Measure.[SS Monitor_SS Target Time], Measure.[SS Monitor_Shipment], Measure.[SS Monitor_Shipment BuildAhead],
    Measure.[SS Monitor_Shipment BuildAhead 1W], Measure.[SS Monitor_Shipment BuildAhead 2W],
    Measure.[SS Monitor_Shipment BuildAhead 3W~], Measure.[SS Monitor_Shipment JIT], Measure.[SS Monitor_Shipment SS],
    Measure.[SS Monitor_Shipment SS 1W], Measure.[SS Monitor_Shipment SS 2W], Measure.[SS Monitor_Shipment SS 3W~],
    Measure.[SS Monitor_Short]}) on column;

* Flow Summary
    -
* Output Table
    df_out_SS_Monitor_SUM
    df_out_SS_Monitor_ROW
* 데이타 초기화

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SSMonitor] for Measures {[SS Monitor_Arrival]}
    using scope([Sales Domain].[AP2].filter(~(#.Name in {"All", "-"})))
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),
    (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000),
    (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    (Select (&CWVUI * [Location].[Location] * [Item].[Item]* [Time].[Week] * [Sales Domain].[AP2]
        * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    ({Measure.[SS Monitor_Arrival], Measure.[SS Monitor_Arrival BuildAhead], Measure.[SS Monitor_Arrival BuildAhead 1W],
     Measure.[SS Monitor_Arrival BuildAhead 2W], Measure.[SS Monitor_Arrival BuildAhead 3W~],
     Measure.[SS Monitor_Arrival JIT], Measure.[SS Monitor_Arrival SS], Measure.[SS Monitor_Arrival SS 1W],
     Measure.[SS Monitor_Arrival SS 2W], Measure.[SS Monitor_Arrival SS 3W~], Measure.[SS Monitor_BuildAhead Limit],
     Measure.[SS Monitor_Demand], Measure.[SS Monitor_EOH], Measure.[SS Monitor_GI], Measure.[SS Monitor_Item BOD LT],
     Measure.[SS Monitor_SS], Measure.[SS Monitor_SS Short], Measure.[SS Monitor_SS Target Qty],
     Measure.[SS Monitor_SS Target Time], Measure.[SS Monitor_Shipment], Measure.[SS Monitor_Shipment BuildAhead],
     Measure.[SS Monitor_Shipment BuildAhead 1W], Measure.[SS Monitor_Shipment BuildAhead 2W],
     Measure.[SS Monitor_Shipment BuildAhead 3W~], Measure.[SS Monitor_Shipment JIT], Measure.[SS Monitor_Shipment SS],
     Measure.[SS Monitor_Shipment SS 1W], Measure.[SS Monitor_Shipment SS 2W], Measure.[SS Monitor_Shipment SS 3W~],
     Measure.[SS Monitor_Short]}) on column).count;

"""

import gc
import math
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
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SSMonitor'
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
# 공통 함수 정의
########################################################################################################################
# DF를 출력하는 함수
saveDf_idx = 1
def saveDf(_df, _csvName):
    if common.gfn_get_isLocal():
        global saveDf_idx
        _df.to_csv(os.path.dirname(__file__) + "\\" + f"out_{saveDf_idx}_{_csvName}.csv", index=False)
        saveDf_idx = saveDf_idx + 1

    dfMemory = format(round(_df.memory_usage(deep=True).sum() / (1024 ** 2), 2), ",")
    dfDetailInfo = " ( " + format(_df.shape[0], ",") + " Row * " + str(_df.shape[1]) + " Column, " + dfMemory + " Mb )"

    logger.PrintDF(p_df=_df, p_df_name=_csvName + dfDetailInfo, p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    vdCommon.gfn_pyLog_detail(_csvName, _df)

# Step 로그를 남긴다.
def batchLogStep(log):
    logger.Step(p_step_desc=log)
    # MG 로그를 남긴다.
    vdCommon.gfn_pyLog_detail(log)

########################################################################################################################
# local function
########################################################################################################################
def read_csv_file_converter(file_name, convert):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8", converters = convert)

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

def findDayWeek(row):
    target_date = row[TIME_DAY_COLUMN]
    if(row['STOCK_DAY'] > 0):
        weeknum = row['STOCK_WEEK'] + 1
        new_date = target_date + datetime.timedelta(weeks=weeknum + 1)
        time_week = new_date.strftime("%Y%W")
        return time_week
    else:
        return '-'

def findLTWeek(row):
    target_date = row[TIME_DAY_COLUMN]
    rowTimeWeek = row[TIME_WEEK_COLUMN]
    if(row[SS_ITEM_BOD_LT_COLUMN] > 0):
        weeknum = (row[SS_ITEM_BOD_LT_COLUMN]/7)
        new_date = target_date + datetime.timedelta(weeks=weeknum + 1)
        time_week = new_date.strftime("%Y%W")
        #if((rowTimeWeek == "202508") & (row[ITEM_COLUMN] == "LS32B304NWNXGO")):
        #if (row[SS_ITEM_BOD_LT_COLUMN] > 7):
        #    print(f'{rowTimeWeek}/{row[SS_ITEM_BOD_LT_COLUMN]}/{weeknum}/{time_week}')
        return time_week
    else:
        return rowTimeWeek

def safetyStock_CreateDictionary(row):
    target_date = row[TIME_DAY_COLUMN]
    weeknum = row["STOCK_WEEK"]
    if(row["STOCK_WEEK"] >= 0):
        for i in range(weeknum):
            new_date = target_date + datetime.timedelta(weeks=i + 2)
            time_week = new_date.strftime("%Y%W")
            #TEMP_SAFETYSTOCK DataFrame Create
            TEMP_SAFETYSTOCK[VERSION_NAME_COLUMN].append(row[VERSION_NAME_COLUMN])
            TEMP_SAFETYSTOCK[SUB_LOCATION_COLUMN].append(row[SUB_LOCATION_COLUMN])
            TEMP_SAFETYSTOCK[ITEM_COLUMN].append(row[ITEM_COLUMN])
            TEMP_SAFETYSTOCK[TIME_WEEK_COLUMN].append(row[TIME_WEEK_COLUMN])
            TEMP_SAFETYSTOCK["STOCK_TIME_WEEK"].append(time_week)
    return "Y"

def dataFloor_dataframe(df, columns):
    for i in range(len(columns)):
        column_name = columns[i]
        df[column_name] = np.floor(df[column_name])
    return df

def dataframe_cleaning(df, columns):
    for i in range(len(columns)):
        column_name = columns[i]
        df[column_name] = np.round(df[column_name], 2)
    return df
def drop_dataframe(df, columns):
    df = df.drop(columns, axis=1)
    return df

# L/T 감소되는 구간에 대한 계산 함수
def calculate_LT_Down_Shipment(df):
    shipment_ss = 0
    shipment_buildahead = 0
    jit_cumsum_qty = 0
    ss_cumsum_qty = 0
    buildahead_cumsum_qty = 0
    for index, row in df.iterrows():
        ltCheck = row['LT_CHECK']
        if (row['LT_CHECK'] == "START"):
            # SHIPMENT-JIT 계산
            jit_cumsum_qty = 0
            jit_left_value = row[SS_SHIPMENT_JIT_COLUMN + '_ORG'] # Lead Time 감안된 Arrival JIT 데이타
            jit_right_value = row[SS_SHIPMENT_COLUMN + '_ORG']
            if(jit_left_value > jit_right_value):
                shipment_jit = jit_right_value
            else:
                shipment_jit = jit_left_value
            #if(row[ITEM_COLUMN] == "UE32T5300CEXXN"):
            #    print(f'JIT[{ltCheck}], {row[TIME_WEEK_COLUMN]}=>,[Cal]{shipment_jit} = MIN({jit_left_value},{jit_right_value})')
            # 누적값 계산
            jit_cumsum_qty = shipment_jit
            #print(f'JIT [{ltCheck}] 누적값 : {jit_cumsum_qty}')

            # SHIPMENT-SS 계산
            ss_cumsum_qty = 0
            tempValueLeft = row[SS_SHIPMENT_SS_COLUMN + '_ORG']
            ss_left_value = (row[SS_SHIPMENT_SS_COLUMN + '_ORG'] - ss_cumsum_qty)
            #ss_right_value = (row[SS_SHIPMENT_COLUMN + '_ORG'] - row[SS_SHIPMENT_JIT_COLUMN + '_ORG'])
            tempValueRight = row[SS_SHIPMENT_COLUMN + '_ORG']
            ss_right_value = (row[SS_SHIPMENT_COLUMN + '_ORG'] - shipment_jit)
            # MAX 테스트
            if(ss_left_value > ss_right_value):
                shipment_ss = ss_right_value
            else:
                shipment_ss = ss_left_value
            #if(row[ITEM_COLUMN] == "UE32T5300CEXXN"):
            #    print(f'SS[{ltCheck}], {row[TIME_WEEK_COLUMN]}=>,[Cal]{shipment_ss} = MIN({ss_left_value}({tempValueLeft}),{ss_right_value}({tempValueRight} - {shipment_jit}))')
            # 누적값 계산
            ss_cumsum_qty = shipment_ss
            #print(f'SS [{ltCheck}] 누적값 : {ss_cumsum_qty}')
            # SHIPMENT-Buildahead 계산
            buildahead_cumsum_qty = 0
            buildahead_left_value = (row[SS_SHIPMENT_BUILDAHEAD_COLUMN + '_ORG'] - buildahead_cumsum_qty)
            buildahead_right_value = (row[SS_SHIPMENT_COLUMN + '_ORG'] - row[SS_SHIPMENT_JIT_COLUMN + '_ORG'] - shipment_ss)
            if(buildahead_left_value > buildahead_right_value):
                shipment_buildahead = buildahead_right_value
            else:
                shipment_buildahead = buildahead_left_value
            buildahead_cumsum_qty = shipment_buildahead
            #if (row[ITEM_COLUMN] == "UE32T5300CEXXN"):
            #    print(f'buildahead[{ltCheck}], {row[TIME_WEEK_COLUMN]}=>,[Cal]{shipment_buildahead} = MIN({buildahead_left_value},{buildahead_right_value})')
        else:
           if ((row['LT_CHECK'] == "KEEP") | (row['LT_CHECK'] == "END")):
               # SHIPMENT-JIT 게산
               tempValue = row[SS_SHIPMENT_JIT_COLUMN +'_ORG']
               jit_left_value = (row[SS_SHIPMENT_JIT_COLUMN +'_ORG'] - jit_cumsum_qty)
               tempValueRight = row[SS_SHIPMENT_COLUMN + '_ORG']
               jit_right_value = row[SS_SHIPMENT_COLUMN + '_ORG']
               if (jit_left_value > jit_right_value):
                   shipment_jit = jit_right_value
               else:
                   shipment_jit = jit_left_value
               #print(
               #    f'JIT[{ltCheck}] {row[TIME_WEEK_COLUMN]}=>,[Cal]{shipment_jit} = MIN(({tempValue} - {jit_cumsum_qty}),{jit_right_value}({tempValueRight}))')
               # 누적값 계산
               jit_cumsum_qty += shipment_jit
               #print(f'JIT {ltCheck}, 누적값 : {jit_cumsum_qty}')
               # SHIPMENT-SS 계산
               tempValueLeft = row[SS_SHIPMENT_SS_COLUMN + '_ORG']
               ss_left_value = (row[SS_SHIPMENT_SS_COLUMN +'_ORG'] - ss_cumsum_qty)
               tempValueRight = row[SS_SHIPMENT_COLUMN + '_ORG']
               ss_right_value = (row[SS_SHIPMENT_COLUMN + '_ORG'] - shipment_jit)
               if (ss_left_value > ss_right_value):
                   shipment_ss = ss_right_value
               else:
                   shipment_ss = ss_left_value
               #print(
               #    f'SS[{ltCheck}] {row[TIME_WEEK_COLUMN]}=>,
               #    [Cal]{shipment_ss} = MIN({ss_left_value}({tempValueLeft} - {ss_cumsum_qty}),{ss_right_value}({tempValueRight} - {shipment_jit}))')

               # 누적값 계산
               ss_cumsum_qty += shipment_ss
               # SHIPMENT-Buildahead 계산
               buildahead_left_value = (row[SS_SHIPMENT_BUILDAHEAD_COLUMN +'_ORG'] - buildahead_cumsum_qty)
               buildahead_left_value_temp1 = row[SS_SHIPMENT_BUILDAHEAD_COLUMN +'_ORG']
               buildahead_left_value_temp2 = buildahead_cumsum_qty
               buildahead_right_value = (row[SS_SHIPMENT_COLUMN +'_ORG'] - shipment_jit - shipment_ss)
               buildahead_right_valueNew = (row[SS_SHIPMENT_COLUMN +'_ORG'] - shipment_jit - shipment_ss)
               buildahead_right_value_temp1 = row[SS_SHIPMENT_COLUMN +'_ORG']
               buildahead_right_value_temp2 = row[SS_SHIPMENT_JIT_COLUMN +'_ORG']
               buildahead_right_value_temp2_1 = shipment_jit
               buildahead_right_value_temp3 = shipment_ss
               if(buildahead_left_value > buildahead_right_value):
                   shipment_buildahead = buildahead_right_value
               else:
                   shipment_buildahead = buildahead_left_value
               buildahead_cumsum_qty += shipment_buildahead #누적값 계산
               #if (row[ITEM_COLUMN] == "UE32T5300CEXXN"):
               #     print(f'buildahead-[{ltCheck}], {row[TIME_WEEK_COLUMN]}=>,[Cal]{shipment_buildahead} = MIN({buildahead_left_value}[{buildahead_left_value_temp1} - {buildahead_left_value_temp2}],{buildahead_right_value})')
               #     print(f'buildhead-[New]=>{shipment_buildahead}, {buildahead_right_valueNew}')
               #     print(f"buildhead-[New]=>{buildahead_right_value_temp1},{buildahead_right_value_temp2},{buildahead_right_value_temp2_1},{buildahead_right_value_temp3}")

        # Shipment JIT 관련
        df.at[index, SS_SHIPMENT_JIT_COLUMN] = shipment_jit
        # Shipment SS 관련
        df.at[index, SS_SHIPMENT_SS_COLUMN] = (shipment_ss)
        shipment_ss_1w = min(shipment_ss, row[SS_SHIPMENT_SS_COLUMN +'_ORG'])
        df.at[index, SS_SHIPMENT_SS_1W_COLUMN] = (shipment_ss_1w)
        shipment_ss_2w = min((shipment_ss - shipment_ss_1w), row[SS_SHIPMENT_SS_2W_COLUMN +'_ORG'])
        df.at[index, SS_SHIPMENT_SS_2W_COLUMN] = (shipment_ss_2w)
        shipment_ss_3w = min((shipment_ss - shipment_ss_1w - shipment_ss_2w), row[SS_SHIPMENT_SS_3W_COLUMN +'_ORG'])
        df.at[index, SS_SHIPMENT_SS_3W_COLUMN] = (shipment_ss_3w)
        # Shipment buildahead 관련
        df.at[index, SS_SHIPMENT_BUILDAHEAD_COLUMN] = (shipment_buildahead)
        shipment_buildahead_1w = min(shipment_ss, row[SS_SHIPMENT_BUILDAHEAD_COLUMN +'_ORG'])
        df.at[index, SS_SHIPMENT_BUILDAHEAD_1W_COLUMN] = (shipment_buildahead_1w)
        shipment_buildahead_2w = min((shipment_ss - shipment_ss_1w), row[SS_SHIPMENT_SS_2W_COLUMN +'_ORG'])
        df.at[index, SS_SHIPMENT_BUILDAHEAD_2W_COLUMN] = (shipment_buildahead_2w)
        shipment_buildahead_3w = min((shipment_ss - shipment_ss_1w - shipment_ss_2w), row[SS_SHIPMENT_SS_3W_COLUMN +'_ORG'])
        df.at[index, SS_SHIPMENT_BUILDAHEAD_3W_COLUMN] = (shipment_buildahead_3w)
    return df

#유니크한 데이타와 주차 채우기
def make_combinations(df_time, df, unique_key):
    df_time = df_time.assign(key=1)
    df_time['key'] = df_time['key'].astype(int)
    #unique_key = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN]
    unique_combinations = df[unique_key].drop_duplicates()
    unique_combinations = unique_combinations.assign(key=1)
    unique_combinations['key'] = unique_combinations['key'].astype(int)
    all_possible_combinations = (pd.merge(unique_combinations, df_time, how="outer", on='key')
                                 .drop(columns=['key', TIME_DAY_COLUMN]).drop_duplicates())
    return all_possible_combinations
########################################################################################################################
# logic start
########################################################################################################################
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
    # STEP 1 : input table load
    ################################################################################################################
    step('=====> STEP1 Start : input table load')
    if is_local:
        outVersionName = "CWV_MP"
        df_in_Arrival = read_csv_file("df_in_Arrival_QA")
        df_in_BOD_ITEM_LT = read_csv_file("df_in_BOD_Item_LT_QA")
        df_in_BOD_ITEM_LT_W = read_csv_file("df_in_BOD_Item_LT_W_QA")
        df_in_Buildhead_Setting = read_csv_file("df_in_Buildhead_Setting_QA")
        df_in_Demand = read_csv_file("df_in_Demand_QA")
        df_in_EOH = read_csv_file("df_in_EOH_QA")
        df_in_GI = read_csv_file("df_in_GI_QA")
        df_in_Pre_SS_Monitor_ROW = read_csv_file("df_in_Pre_SS_Monitor_ROW_QA")
        df_in_Pre_SS_Monitor_SUM = read_csv_file("df_in_Pre_SS_Monitor_SUM_QA")
        df_in_SAFETYSTOCK = read_csv_file("df_in_SAFETYSTOCK_QA")
        df_in_Shipment = read_csv_file("df_in_Shipment_QA")
        df_in_SHORT = read_csv_file("df_in_SHORT_QA")
        df_in_SubLocation = read_csv_file("df_in_SubLocation_DEV16")
        df_in_Time = read_csv_file("df_in_Time_QA")
        df_in_SS_Prty_Location = read_csv_file("df_in_SS_Prty_Location_QA")

    print_df(df_in_SS_Prty_Location, 'input table load .... df_in_SS_Prty_Location')
    print_df(df_in_Demand, 'input table load .... df_in_Demand')
    print_df(df_in_GI, 'input table load .... df_in_GI')
    print_df(df_in_SHORT, 'input table load .... df_in_SHORT')
    print_df(df_in_EOH, 'input table load .... df_in_EOH')
    print_df(df_in_SAFETYSTOCK, 'input table load .... df_in_SAFETYSTOCK')
    print_df(df_in_Buildhead_Setting, 'input table load .... df_in_Buildhead_Setting')
    print_df(df_in_SubLocation, 'input table load .... df_in_SubLocation')
    print_df(df_in_Arrival, 'input table load .... df_in_Arrival')
    print_df(df_in_Shipment, 'input table load .... df_in_Shipment')
    print_df(df_in_BOD_ITEM_LT, 'input table load .... df_in_BOD_ITEM_LT')
    print_df(df_in_BOD_ITEM_LT_W, 'input table load .... df_in_BOD_ITEM_LT_W')
    print_df(df_in_Time, 'input table load .... df_in_Time')
    print_df(df_in_Pre_SS_Monitor_SUM, 'input table load .... df_in_Pre_SS_Monitor_SUM')
    print_df(df_in_Pre_SS_Monitor_ROW, 'input table load .... df_in_Pre_SS_Monitor_ROW')
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
    # df_in_EOH_SAFETYSTOCK 데이타 기준으로 데이타를 생성하므로 없는 경우 데이타 종료시킴.
    if df_in_SAFETYSTOCK.empty:
        raise CustomException(".... df_in_SAFETYSTOCK 값이 없습니다.")
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    step('=====> STEP1 End')
    ################################################################################################################
    # STEP 2 : DataFrame Column 변수 처리
    ################################################################################################################
    step('=====> STEP2 Start : DataFrame Column 변수 처리')
    # 컬럼 변수 선언
    VERSION_NAME_COLUMN = "Version.[Version Name]"
    ITEM_COLUMN = "Item.[Item]"
    LOCATION_COLUMN = 'Location.[Location]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    TIME_WEEK_COLUMN = 'Time.[Week]'
    TIME_DAY_COLUMN = "Time.[Day]"
    SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
    SUB_LOCATION_REP_AP2_COLUMN = 'Sub Location.[Sub Location Rep AP2]'
    TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
    ACTIVITY1_ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
    ACTIVITY2_ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
    ACTIVITY3_ACTIVITY3_COLUMN = 'Activity3.[Activity3]'

    W_DEMAND_QUANTITY_TO_SCS_COLUMN = 'W Demand Quantity to SCS'
    W_DEMAND_SUPPLY_QUANTITY_COLUMN = 'W Demand Supply Quantity'
    SALES_PSI_AP2_W_GI_QTY_COLUMN = 'Sales PSI AP2 W_GI Qty'
    W_TOTAL_SHORT_QUANTITY_COLUMN = 'W Total Short Quantity'
    W_ENDING_ON_HAND_COLUMN = 'W Ending On Hand'
    W_TARGET_INVENTORY_COLUMN = 'W Target Inventory'
    W_SS_BUILD_AHEAD_LIMIT = "W SS Build Ahead Limit"
    W_WOS_TARGET_COLUMN = 'W WOS Target'
    W_ACTIVITY_LEAD_TIME = 'W Activity Lead Time'
    W_ACTIVITY_LEAD_TIME_TIME_VARYING = 'W Activity Lead Time Time Varying'
    #Arrival
    W_MATERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN= 'W Material Production Quantity Plan Output'
    #Shipment
    W_MATERIAL_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN= 'W Material Consumption Quantity Plan Output'
    BOD_ITEM_LT = 'BOD Item_BOD LT'

    #Output 관련 컬럼
    SS_ARRIVAL_COLUMN = 'SS Monitor_Arrival'
    SS_ARRIVAL_BUILDAHEAD_COLUMN = 'SS Monitor_Arrival BuildAhead'
    SS_ARRIVAL_BUILDAHEAD_1W_COLUMN = 'SS Monitor_Arrival BuildAhead 1W'
    SS_ARRIVAL_BUILDAHEAD_2W_COLUMN = 'SS Monitor_Arrival BuildAhead 2W'
    SS_ARRIVAL_BUILDAHEAD_3W_COLUMN = 'SS Monitor_Arrival BuildAhead 3W~'
    SS_ARRIVAL_JIT_COLUMN = 'SS Monitor_Arrival JIT'
    SS_ARRIVAL_SS_COLUMN = 'SS Monitor_Arrival SS'
    SS_ARRIVAL_SS_1W_COLUMN = 'SS Monitor_Arrival SS 1W'
    SS_ARRIVAL_SS_2W_COLUMN = 'SS Monitor_Arrival SS 2W'
    SS_ARRIVAL_SS_3W_COLUMN = 'SS Monitor_Arrival SS 3W~'
    SS_BUILDAHEAD_LIMIT_COLUMN = 'SS Monitor_BuildAhead Limit'
    SS_DEMAND_COLUMN = 'SS Monitor_Demand'
    SS_EOH_COLUMN = 'SS Monitor_EOH'
    SS_GI_COLUMN = 'SS Monitor_GI'
    SS_ITEM_BOD_LT_COLUMN = 'SS Monitor_Item BOD LT'
    # SAFETYSTOCK
    SS_SS_COLUMN = 'SS Monitor_SS'
    SS_SS_SHORT_COLUMN = 'SS Monitor_SS Short'
    SS_SS_TARGET_QTY_COLUMN = 'SS Monitor_SS Target Qty'
    SS_SS_TARGET_TIME_COLUMN = 'SS Monitor_SS Target Time'
    SS_SHIPMENT_COLUMN = 'SS Monitor_Shipment'
    SS_SHIPMENT_BUILDAHEAD_COLUMN = 'SS Monitor_Shipment BuildAhead'
    SS_SHIPMENT_BUILDAHEAD_1W_COLUMN = 'SS Monitor_Shipment BuildAhead 1W'
    SS_SHIPMENT_BUILDAHEAD_2W_COLUMN = 'SS Monitor_Shipment BuildAhead 2W'
    SS_SHIPMENT_BUILDAHEAD_3W_COLUMN = 'SS Monitor_Shipment BuildAhead 3W~'
    SS_SHIPMENT_JIT_COLUMN = 'SS Monitor_Shipment JIT'
    SS_SHIPMENT_SS_COLUMN = 'SS Monitor_Shipment SS'
    SS_SHIPMENT_SS_1W_COLUMN = 'SS Monitor_Shipment SS 1W'
    SS_SHIPMENT_SS_2W_COLUMN = 'SS Monitor_Shipment SS 2W'
    SS_SHIPMENT_SS_3W_COLUMN = 'SS Monitor_Shipment SS 3W~'
    SS_SHORT_COLUMN = 'SS Monitor_Short'

    TEMP_SAFETYSTOCK = {VERSION_NAME_COLUMN: [], SUB_LOCATION_COLUMN: [], ITEM_COLUMN: [],
                        TIME_WEEK_COLUMN: [], "STOCK_TIME_WEEK": []}

    join_column = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN]
    join_column_ap2 = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN]
    join_column_row = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN]
    join_column_row2 = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN,
                       SALES_DOMAIN_AP2_COLUMN, TRANS_MODE_COLUMN]
    #열재배열 rearrangement
    ss_monitor_Arrival_column =[VERSION_NAME_COLUMN, SALES_DOMAIN_AP2_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                                LOCATION_COLUMN, TRANS_MODE_COLUMN,TIME_WEEK_COLUMN,
                                SS_DEMAND_COLUMN,SS_GI_COLUMN,SS_SHORT_COLUMN,SS_EOH_COLUMN,SS_SS_COLUMN,
                                SS_SS_TARGET_TIME_COLUMN, SS_SS_TARGET_QTY_COLUMN,SS_SS_SHORT_COLUMN,
                                SS_ARRIVAL_COLUMN,SS_ARRIVAL_JIT_COLUMN,SS_ARRIVAL_SS_COLUMN,SS_ARRIVAL_SS_1W_COLUMN,
                                SS_ARRIVAL_SS_2W_COLUMN,SS_ARRIVAL_SS_3W_COLUMN,SS_ARRIVAL_BUILDAHEAD_COLUMN,
                                SS_ARRIVAL_BUILDAHEAD_1W_COLUMN,SS_ARRIVAL_BUILDAHEAD_2W_COLUMN,SS_ARRIVAL_BUILDAHEAD_3W_COLUMN]
    #LOCATION_COLUMN, TRANS_MODE_COLUMN,
    ss_monitor_Shipment_column =[VERSION_NAME_COLUMN, SALES_DOMAIN_AP2_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                                TIME_WEEK_COLUMN, SS_SHIPMENT_COLUMN, SS_SHIPMENT_JIT_COLUMN, SS_SHIPMENT_SS_COLUMN,
                                SS_SHIPMENT_SS_1W_COLUMN, SS_SHIPMENT_SS_2W_COLUMN, SS_SHIPMENT_SS_3W_COLUMN,
                                SS_SHIPMENT_BUILDAHEAD_COLUMN, SS_SHIPMENT_BUILDAHEAD_1W_COLUMN,
                                SS_SHIPMENT_BUILDAHEAD_2W_COLUMN, SS_SHIPMENT_BUILDAHEAD_3W_COLUMN]

    ss_monitor_column_sum =[VERSION_NAME_COLUMN, SALES_DOMAIN_AP2_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                            LOCATION_COLUMN, TRANS_MODE_COLUMN,TIME_WEEK_COLUMN,
                            SS_DEMAND_COLUMN,SS_GI_COLUMN,SS_SHORT_COLUMN,SS_EOH_COLUMN,SS_SS_COLUMN,
                            SS_SS_TARGET_TIME_COLUMN, SS_SS_TARGET_QTY_COLUMN,SS_SS_SHORT_COLUMN,
                            SS_BUILDAHEAD_LIMIT_COLUMN,SS_ARRIVAL_COLUMN,SS_ARRIVAL_JIT_COLUMN,SS_ARRIVAL_SS_COLUMN,
                            SS_ARRIVAL_SS_1W_COLUMN,SS_ARRIVAL_SS_2W_COLUMN,SS_ARRIVAL_SS_3W_COLUMN,
                            SS_ARRIVAL_BUILDAHEAD_COLUMN,SS_ARRIVAL_BUILDAHEAD_1W_COLUMN,SS_ARRIVAL_BUILDAHEAD_2W_COLUMN,
                            SS_ARRIVAL_BUILDAHEAD_3W_COLUMN,SS_SHIPMENT_COLUMN,SS_SHIPMENT_JIT_COLUMN,
                            SS_SHIPMENT_SS_COLUMN,SS_SHIPMENT_SS_1W_COLUMN,SS_SHIPMENT_SS_2W_COLUMN,
                            SS_SHIPMENT_SS_3W_COLUMN,SS_SHIPMENT_BUILDAHEAD_COLUMN,SS_SHIPMENT_BUILDAHEAD_1W_COLUMN,
                            SS_SHIPMENT_BUILDAHEAD_2W_COLUMN,SS_SHIPMENT_BUILDAHEAD_3W_COLUMN]
    ss_monitor_column_row =[VERSION_NAME_COLUMN, SALES_DOMAIN_AP2_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                            LOCATION_COLUMN, TRANS_MODE_COLUMN,TIME_WEEK_COLUMN,
                            SS_SS_COLUMN, SS_ARRIVAL_COLUMN,SS_ARRIVAL_JIT_COLUMN, SS_ARRIVAL_SS_COLUMN,
                            SS_ARRIVAL_SS_1W_COLUMN, SS_ARRIVAL_SS_2W_COLUMN,SS_ARRIVAL_SS_3W_COLUMN,
                            SS_ARRIVAL_BUILDAHEAD_COLUMN, SS_ARRIVAL_BUILDAHEAD_1W_COLUMN,
                            SS_ARRIVAL_BUILDAHEAD_2W_COLUMN,SS_ARRIVAL_BUILDAHEAD_3W_COLUMN,
                            SS_SHIPMENT_COLUMN,SS_SHIPMENT_JIT_COLUMN,SS_SHIPMENT_SS_COLUMN,SS_SHIPMENT_SS_1W_COLUMN,
                            SS_SHIPMENT_SS_2W_COLUMN,SS_SHIPMENT_SS_3W_COLUMN,
                            SS_SHIPMENT_BUILDAHEAD_COLUMN,SS_SHIPMENT_BUILDAHEAD_1W_COLUMN,
                            SS_SHIPMENT_BUILDAHEAD_2W_COLUMN,SS_SHIPMENT_BUILDAHEAD_3W_COLUMN, SS_ITEM_BOD_LT_COLUMN]
    step('=====> STEP2 End')
    ################################################################################################################
    # STEP 3 :  DataFrame Data 가공
    ################################################################################################################
    step('=====> STEP3 Start : DataFrame Data 가공')
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # 25/10/01 임채수 프로 요청
    # df_in_SS_Prty_Location 해당되는 Location만 추출함.
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    df_in_SS_Prty_Location = df_in_SS_Prty_Location[[VERSION_NAME_COLUMN,LOCATION_COLUMN]]
    df_in_SS_Prty_Location.drop_duplicates(inplace=True)
    #print_df(df_in_SS_Prty_Location, "df_in_SS_Prty_Location")
    #df_in_SAFETYSTOCK
    df_in_SAFETYSTOCK = pd.merge(df_in_SAFETYSTOCK, df_in_SS_Prty_Location,
                                 on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    # Null값 처리
    df_in_SAFETYSTOCK[W_TARGET_INVENTORY_COLUMN] = df_in_SAFETYSTOCK[W_TARGET_INVENTORY_COLUMN].fillna(0)
    df_in_SAFETYSTOCK[W_WOS_TARGET_COLUMN] = df_in_SAFETYSTOCK[W_WOS_TARGET_COLUMN].fillna(0)

    #print_df(df_in_SAFETYSTOCK, "df_in_SAFETYSTOCK(Location)")
    #df_in_EOH
    df_in_EOH = pd.merge(df_in_EOH, df_in_SS_Prty_Location,
                        on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    #print_df(df_in_EOH, "df_in_EOH(Location)")
    #df_in_Demand
    df_in_Demand = pd.merge(df_in_Demand, df_in_SS_Prty_Location,
                                 on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    #df_in_GI
    df_in_GI = pd.merge(df_in_GI, df_in_SS_Prty_Location,
                                 on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    # df_in_SHORT
    df_in_SHORT = pd.merge(df_in_SHORT, df_in_SS_Prty_Location,
                                 on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    #df_in_Buildhead_Setting
    df_in_Buildhead_Setting = pd.merge(df_in_Buildhead_Setting, df_in_SS_Prty_Location,
                                 on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    #df_in_Arrival
    df_in_Arrival = pd.merge(df_in_Arrival, df_in_SS_Prty_Location,
                                 on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    #df_in_Shipment
    df_in_Shipment = pd.merge(df_in_Shipment, df_in_SS_Prty_Location,
                                 on=[VERSION_NAME_COLUMN,LOCATION_COLUMN], how="inner")
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # df_in_EOH_SAFETYSTOCK = df_in_EOH & df_in_SAFETYSTOCK
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    join_column_temp = [VERSION_NAME_COLUMN,LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN]
    for col in join_column_temp:
        df_in_SAFETYSTOCK[col] = df_in_SAFETYSTOCK[col].astype(str)
        df_in_EOH[col] = df_in_EOH[col].astype(str)
    df_in_EOH_SAFETYSTOCK = pd.merge(df_in_SAFETYSTOCK, df_in_EOH, on=join_column_temp, how="left")
    print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK_MERGE_718")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # df_in_Demand_GI_SHORT = df_in_Demand & df_in_GI & df_in_Short
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    join_column_temp = [VERSION_NAME_COLUMN,LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN,SALES_DOMAIN_AP2_COLUMN]
    for col in join_column_temp:
        df_in_SHORT[col] = df_in_SHORT[col].astype(str)
        df_in_Demand[col] = df_in_Demand[col].astype(str)
        df_in_GI[col] = df_in_GI[col].astype(str)
    df_in_Demand_GI_SHORT = pd.merge(df_in_Demand, df_in_GI, on=join_column_temp, how="outer")
    #print_df(df_in_Demand_GI_SHORT, "MERGE_df_in_Demand_GI")
    df_in_Demand_GI_SHORT = pd.merge(df_in_Demand_GI_SHORT, df_in_SHORT, on=join_column_temp, how="outer")
    #print_df(df_in_Demand_GI_SHORT, "MERGE_df_in_Demand_GI_SHORT")
    df_in_Demand_GI_SHORT = df_in_Demand_GI_SHORT[[VERSION_NAME_COLUMN,LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN,
                                                   SALES_DOMAIN_AP2_COLUMN,W_DEMAND_QUANTITY_TO_SCS_COLUMN,
                                                   SALES_PSI_AP2_W_GI_QTY_COLUMN,W_TOTAL_SHORT_QUANTITY_COLUMN]]
    # Null 값처리
    df_in_Demand_GI_SHORT[W_DEMAND_QUANTITY_TO_SCS_COLUMN] = df_in_Demand_GI_SHORT[W_DEMAND_QUANTITY_TO_SCS_COLUMN].fillna(0)
    df_in_Demand_GI_SHORT[SALES_PSI_AP2_W_GI_QTY_COLUMN] = df_in_Demand_GI_SHORT[SALES_PSI_AP2_W_GI_QTY_COLUMN].fillna(0)
    df_in_Demand_GI_SHORT[W_TOTAL_SHORT_QUANTITY_COLUMN] = df_in_Demand_GI_SHORT[W_TOTAL_SHORT_QUANTITY_COLUMN].fillna(0)
    #print_df(df_in_Demand_GI_SHORT, "df_in_Demand_GI_SHORT_MERGE")
    #save_csv_file(df_in_Demand_GI_SHORT, "TEMP_Demand_GI_SHORT")
    #불필요한 DataFrame 삭제
    # ++++++++++++++++++++++++++++++++++++
    # df_in_Pre_SS_Monitor_SUM (int --> String)
    # ++++++++++++++++++++++++++++++++++++
    df_in_Pre_SS_Monitor_SUM[TIME_WEEK_COLUMN] = df_in_Pre_SS_Monitor_SUM[TIME_WEEK_COLUMN].astype(str)
    df_in_Pre_SS_Monitor_SUM[SALES_DOMAIN_AP2_COLUMN] = df_in_Pre_SS_Monitor_SUM[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_in_Pre_SS_Monitor_SUM[VERSION_NAME_COLUMN] = paramOutVersion
    # ++++++++++++++++++++++++++++++++++++
    # df_in_Pre_SS_Monitor_ROW (int --> String)
    # ++++++++++++++++++++++++++++++++++++
    df_in_Pre_SS_Monitor_ROW[TIME_WEEK_COLUMN] = df_in_Pre_SS_Monitor_ROW[TIME_WEEK_COLUMN].astype(str)
    df_in_Pre_SS_Monitor_ROW[SALES_DOMAIN_AP2_COLUMN] = df_in_Pre_SS_Monitor_ROW[SALES_DOMAIN_AP2_COLUMN].astype(str)
    df_in_Pre_SS_Monitor_ROW[VERSION_NAME_COLUMN] = paramOutVersion
    # ++++++++++++++++++++++++++++++++++++
    # df_in_Time (int --> String)
    # ++++++++++++++++++++++++++++++++++++
    # 0. 형변환
    step('=====> STEP3-1 Start : DataFrame df_in_Time')
    df_in_Time[TIME_WEEK_COLUMN] = df_in_Time[TIME_WEEK_COLUMN].astype(str)
    df_in_Time[TIME_DAY_COLUMN] = pd.to_datetime(df_in_Time[TIME_DAY_COLUMN])
    df_in_Time_3W = df_in_Time.copy()
    df_in_Time_3W['1w_week'] = df_in_Time_3W[TIME_WEEK_COLUMN].shift(-1)
    df_in_Time_3W['2w_week'] = df_in_Time_3W[TIME_WEEK_COLUMN].shift(-2)
    df_in_Time_3W['3w_week'] = df_in_Time_3W[TIME_WEEK_COLUMN].shift(-3)
    df_in_Time_3W = df_in_Time_3W[[TIME_WEEK_COLUMN, '1w_week', '2w_week', '3w_week']]
    #print_df(df_in_Time_3W, "df_in_Time_3W")
    # 주차(TIME_WEEK_COLUMN) 데이터의 모든 조합 산출
    df_planningWeek = df_in_Time.copy()
    df_planningWeek = df_planningWeek.drop(columns=[TIME_DAY_COLUMN], axis=1)
    df_planningWeek = df_planningWeek.assign(key=1)
    df_planningWeek['key'] = df_planningWeek['key'].astype(int)
    step('=====> STEP3-1 End : DataFrame df_in_Time')
    # ++++++++++++++++++++++++++++++++++++
    # df_in_SubLocation
    # ++++++++++++++++++++++++++++++++++++
    # 0. 형변환
    df_in_SubLocation[SUB_LOCATION_COLUMN] = df_in_SubLocation[SUB_LOCATION_COLUMN].astype(str)
    df_in_SubLocation[SUB_LOCATION_REP_AP2_COLUMN] = df_in_SubLocation[SUB_LOCATION_REP_AP2_COLUMN].astype(str)
    df_in_SubLocation.rename(columns={SUB_LOCATION_REP_AP2_COLUMN: SALES_DOMAIN_AP2_COLUMN}, inplace=True)
    step('=====> STEP3-2 End : DataFrame df_in_SubLocation')

    # df_in_Buildhead_Setting 프레임 가공
    # 형변환
    # 데이타프레임 LayOut 정리
    df_in_Buildhead_Setting.rename(
        columns={LOCATION_COLUMN: SUB_LOCATION_COLUMN, W_SS_BUILD_AHEAD_LIMIT: SS_BUILDAHEAD_LIMIT_COLUMN},
        inplace=True)
    #추자
    unique_key = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN]
    unique_combinations = make_combinations(df_in_Time, df_in_Buildhead_Setting,unique_key )
    df_in_Buildhead_Setting = pd.merge( df_in_Buildhead_Setting, unique_combinations, how='inner', on=unique_key)

    # ++++++++++++++++++++++++++++++++++++
    # df_in_EOH_SAFETYSTOCK
    # ++++++++++++++++++++++++++++++++++++
    # 0. 형변환
    df_in_EOH_SAFETYSTOCK[TIME_WEEK_COLUMN] = df_in_EOH_SAFETYSTOCK[TIME_WEEK_COLUMN].astype(str)
    df_in_Arrival[LOCATION_COLUMN] = df_in_Arrival[LOCATION_COLUMN].astype(str)
    # 1. Data Frame 컬럼 rename
    df_in_EOH_SAFETYSTOCK.rename(columns={LOCATION_COLUMN: SUB_LOCATION_COLUMN,
                                          W_ENDING_ON_HAND_COLUMN: SS_EOH_COLUMN,
                                          W_TARGET_INVENTORY_COLUMN: SS_SS_TARGET_QTY_COLUMN,
                                          W_WOS_TARGET_COLUMN: SS_SS_TARGET_TIME_COLUMN}, inplace=True)
    # 1.1 Sub Location AP2 데이타 매핑
    df_in_EOH_SAFETYSTOCK = pd.merge(df_in_EOH_SAFETYSTOCK, df_in_SubLocation, how="inner", on=[SUB_LOCATION_COLUMN]) #left=>inner
    print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK_806")
    # 2. nan 값 0 처리
    fillna_int_columns = [SS_EOH_COLUMN, SS_SS_TARGET_QTY_COLUMN, SS_SS_TARGET_TIME_COLUMN]
    for col in fillna_int_columns:
        df_in_EOH_SAFETYSTOCK[col] = df_in_EOH_SAFETYSTOCK[col].fillna(0)
    # 3. 주차의 기준일자를 mapping
    df_in_EOH_SAFETYSTOCK = pd.merge(df_in_EOH_SAFETYSTOCK, df_in_Time, how='left', on=[TIME_WEEK_COLUMN])
    #save_csv_file(df_in_EOH_SAFETYSTOCK, "TEMP_EOH_SAFETYSTOCK")
    print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK_814")
    step('=====> STEP3-4 End : DataFrame df_in_EOH_SAFETYSTOCK')

    # ++++++++++++++++++++++++++++++++++++
    # df_in_Demand_GI_SHORT
    # ++++++++++++++++++++++++++++++++++++
    # 0. 형변환
    df_in_Demand_GI_SHORT[TIME_WEEK_COLUMN] = df_in_Demand_GI_SHORT[TIME_WEEK_COLUMN].astype(str)
    df_in_Arrival[LOCATION_COLUMN] = df_in_Arrival[LOCATION_COLUMN].astype(str)
    df_in_Demand_GI_SHORT[SALES_DOMAIN_AP2_COLUMN] = df_in_Demand_GI_SHORT[SALES_DOMAIN_AP2_COLUMN].astype(str)

    # 1. Data Frame 컬럼 rename
    df_in_Demand_GI_SHORT.rename(columns={LOCATION_COLUMN: SUB_LOCATION_COLUMN,
                                          W_DEMAND_QUANTITY_TO_SCS_COLUMN: SS_DEMAND_COLUMN,
                                          SALES_PSI_AP2_W_GI_QTY_COLUMN: SS_GI_COLUMN,
                                          W_TOTAL_SHORT_QUANTITY_COLUMN: SS_SHORT_COLUMN},inplace=True)
    # 2. nan 값 0 처리
    fillna_int_columns = [SS_DEMAND_COLUMN, SS_GI_COLUMN, SS_SHORT_COLUMN]
    for col in fillna_int_columns:
        df_in_Demand_GI_SHORT[col] = df_in_Demand_GI_SHORT[col].fillna(0)
    step('=====> STEP3-5 End : DataFrame df_in_EOH_SAFETYSTOCK')
    # ++++++++++++++++++++++++++++++++++++
    # df_in_Arrival DataFrame
    # ++++++++++++++++++++++++++++++++++++
    # 0. 형변환
    df_in_Arrival[TIME_WEEK_COLUMN] = df_in_Arrival[TIME_WEEK_COLUMN].astype(str)
    df_in_Arrival[LOCATION_COLUMN] = df_in_Arrival[LOCATION_COLUMN].astype(str)
    # 1. Data Frame 컬럼 rename
    df_in_Arrival.rename(columns={LOCATION_COLUMN: SUB_LOCATION_COLUMN,
                                  W_MATERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN: SS_ARRIVAL_COLUMN},
                         inplace=True)
    # 2. nan 값 0 처리
    fillna_int_columns = [SS_ARRIVAL_COLUMN]
    for col in fillna_int_columns:
        df_in_Arrival[col] = df_in_Arrival[col].fillna(0)

    # 3. ACTIVITY1_ACTIVITY1_COLUMN Split 처리
    splited_list = df_in_Arrival[ACTIVITY1_ACTIVITY1_COLUMN].str.split("_")
    df_in_Arrival[LOCATION_COLUMN] = splited_list.str.get(0)  # FROM Location
    df_in_Arrival[TRANS_MODE_COLUMN] = splited_list.str.get(2)  # Trans Mode

    step('=====> STEP3-6 End : DataFrame df_in_Arrival')
    # ++++++++++++++++++++++++++++++++++++
    # df_in_Shipment DataFrame
    # ++++++++++++++++++++++++++++++++++++
    # 0. 형변환
    df_in_Shipment[TIME_WEEK_COLUMN] = df_in_Shipment[TIME_WEEK_COLUMN].astype(str)
    # 1. Data Frame 컬럼 rename
    df_in_Shipment.rename(columns={W_MATERIAL_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN: SS_SHIPMENT_COLUMN},
                         inplace=True)
    # 2. nan 값 0 처리
    fillna_int_columns = [SS_SHIPMENT_COLUMN]
    for col in fillna_int_columns:
        df_in_Shipment[col] = df_in_Shipment[col].fillna(0)
    # 3. ACTIVITY1_ACTIVITY1_COLUMN Split 처리
    splited_list = df_in_Shipment[ACTIVITY1_ACTIVITY1_COLUMN].str.split("_")
    df_in_Shipment[SUB_LOCATION_COLUMN] = splited_list.str.get(1)  # Sub Location
    df_in_Shipment[TRANS_MODE_COLUMN] = splited_list.str.get(2)  # Trans Mode
    step('=====> STEP3-7 End : DataFrame df_in_Shipment')

    # ++++++++++++++++++++++++++++++++++++
    # df_in_BOD_ITEM_LT_W
    # ++++++++++++++++++++++++++++++++++++
    # 0. 형변환
    df_in_BOD_ITEM_LT_W[TIME_WEEK_COLUMN] = df_in_BOD_ITEM_LT_W[TIME_WEEK_COLUMN].astype(str)
    # 1.ACTIVITY1_ACTIVITY1_COLUMN Split  처리
    splited_list = df_in_BOD_ITEM_LT_W[ACTIVITY1_ACTIVITY1_COLUMN].str.split("_")
    df_in_BOD_ITEM_LT_W[LOCATION_COLUMN] = splited_list.str.get(0)  # FROM Location
    df_in_BOD_ITEM_LT_W[SUB_LOCATION_COLUMN] = splited_list.str.get(1)  # Sub Location
    df_in_BOD_ITEM_LT_W[TRANS_MODE_COLUMN] = splited_list.str.get(2)  # Trans Mode
    #주단위 => 일자로 계산
    df_in_BOD_ITEM_LT_W[W_ACTIVITY_LEAD_TIME_TIME_VARYING] = df_in_BOD_ITEM_LT_W[W_ACTIVITY_LEAD_TIME_TIME_VARYING] * 7

    # 2. Data Frame 컬럼 rename
    df_in_BOD_ITEM_LT_W.rename(columns={ACTIVITY3_ACTIVITY3_COLUMN:ITEM_COLUMN,
                                      W_ACTIVITY_LEAD_TIME_TIME_VARYING:BOD_ITEM_LT}, inplace=True)
    df_in_BOD_ITEM_LT_W = df_in_BOD_ITEM_LT_W.drop(columns=[ACTIVITY1_ACTIVITY1_COLUMN, ACTIVITY2_ACTIVITY2_COLUMN], axis=1)
    # ++++++++++++++++++++++++++++++++++++
    # df_in_BOD_ITEM_LT
    # ++++++++++++++++++++++++++++++++++++
    # 1.ACTIVITY1_ACTIVITY1_COLUMN Split  처리
    splited_list = df_in_BOD_ITEM_LT[ACTIVITY1_ACTIVITY1_COLUMN].str.split("_")
    df_in_BOD_ITEM_LT[LOCATION_COLUMN] = splited_list.str.get(0)  # FROM Location
    df_in_BOD_ITEM_LT[SUB_LOCATION_COLUMN] = splited_list.str.get(1)  # Sub Location
    df_in_BOD_ITEM_LT[TRANS_MODE_COLUMN] = splited_list.str.get(2)  # Trans Mode
    # W_ACTIVITY_LEAD_TIME 주단위 => 일자로 계산
    df_in_BOD_ITEM_LT[W_ACTIVITY_LEAD_TIME] = df_in_BOD_ITEM_LT[W_ACTIVITY_LEAD_TIME] * 7

    # 2. Data Frame 컬럼 rename
    df_in_BOD_ITEM_LT.rename(columns={ACTIVITY3_ACTIVITY3_COLUMN:ITEM_COLUMN,
                                      W_ACTIVITY_LEAD_TIME: BOD_ITEM_LT}, inplace=True)
    df_in_BOD_ITEM_LT = df_in_BOD_ITEM_LT.drop(columns=[ACTIVITY1_ACTIVITY1_COLUMN, ACTIVITY2_ACTIVITY2_COLUMN], axis=1)

    # 3. BOD 대상 데이타 만들기
    # 3-1. BOD ITEM unique 값 체크
    df_unique_BOD_ITEM_LT = df_in_BOD_ITEM_LT.copy()
    df_unique_BOD_ITEM_LT = df_unique_BOD_ITEM_LT.sort_values(by=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,
                                                                  ITEM_COLUMN, LOCATION_COLUMN,TRANS_MODE_COLUMN])
    df_unique_BOD_ITEM_LT = df_unique_BOD_ITEM_LT[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN, ITEM_COLUMN, LOCATION_COLUMN,
                                           TRANS_MODE_COLUMN]]
    df_unique_BOD_ITEM_LT.drop_duplicates(inplace=True)
    df_unique_BOD_ITEM_LT.reset_index(drop=True, inplace=True)

    # 3-2. Shipment 대상 데이타 추출
    df_unique_Shipment = df_in_Shipment.copy()
    df_unique_Shipment = df_unique_Shipment[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,
                                                 ITEM_COLUMN, LOCATION_COLUMN,TRANS_MODE_COLUMN]]
    df_unique_Shipment = df_unique_Shipment.sort_values(by=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN,
                                                            ITEM_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN])
    df_unique_Shipment.drop_duplicates(inplace=True)
    df_unique_Shipment.reset_index(drop=True, inplace=True)
    #print_df(df_unique_Shipment, "Temp... df_unique_Shipment DataFrame")
    df_unique_BOD_ITEM_LT = pd.merge(df_unique_Shipment, df_unique_BOD_ITEM_LT, how='left',
                                     on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN,
                                         ITEM_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN])

    # 주차 채우기
    df_unique_BOD_ITEM_LT['key'] = "1"
    df_in_Time['key'] = "1"
    df_unique_BOD_ITEM_LT = pd.merge( df_in_Time, df_unique_BOD_ITEM_LT, how="left", on="key")

    df_in_BOD_ITEM_LT = pd.merge(df_unique_BOD_ITEM_LT, df_in_BOD_ITEM_LT, how='left',
                                 on=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,
                                     ITEM_COLUMN, LOCATION_COLUMN,TRANS_MODE_COLUMN]).drop(columns=['key'])
    df_in_BOD_ITEM_LT[BOD_ITEM_LT] = df_in_BOD_ITEM_LT[BOD_ITEM_LT].fillna(0)
    df_in_BOD_ITEM_LT = pd.merge(df_in_BOD_ITEM_LT, df_in_BOD_ITEM_LT_W, how='outer',
                                 on=[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, SUB_LOCATION_COLUMN,
                                     ITEM_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN])
    df_in_BOD_ITEM_LT[BOD_ITEM_LT] = np.where(df_in_BOD_ITEM_LT[BOD_ITEM_LT + '_y'].isnull(),
                                             df_in_BOD_ITEM_LT[BOD_ITEM_LT + '_x'], df_in_BOD_ITEM_LT[BOD_ITEM_LT + '_y'])
    df_in_BOD_ITEM_LT = df_in_BOD_ITEM_LT.drop(columns=[BOD_ITEM_LT +'_x', BOD_ITEM_LT +'_y'])

    # BOD L/T추이 체크
    # (1) Sorting
    df_in_BOD_ITEM_LT = df_in_BOD_ITEM_LT[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN, ITEM_COLUMN, LOCATION_COLUMN,
                                           TRANS_MODE_COLUMN, TIME_WEEK_COLUMN, BOD_ITEM_LT, TIME_DAY_COLUMN]]
    df_in_BOD_ITEM_LT = df_in_BOD_ITEM_LT.sort_values(by=[SUB_LOCATION_COLUMN, ITEM_COLUMN, LOCATION_COLUMN,
                                                          TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
    df_in_BOD_ITEM_LT.reset_index(drop=True, inplace=True)
    # (2) 빈값 채우기
    df_in_BOD_ITEM_LT[BOD_ITEM_LT] = df_in_BOD_ITEM_LT[BOD_ITEM_LT].fillna(0)
    # (3) 추이 기준으로 Groupby
    groupby_columns = [SUB_LOCATION_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN]
    # (4) 전주 - 당주 차이
    df_in_BOD_ITEM_LT['LT_DIFF'] = df_in_BOD_ITEM_LT.groupby(groupby_columns)[BOD_ITEM_LT].diff().fillna(0)
    # (5) 당주 - 차주 차이
    df_in_BOD_ITEM_LT['LT_DIFF_SHIFT_1'] = df_in_BOD_ITEM_LT['LT_DIFF'].shift(-1, fill_value=0)
    # (6) <전주 - 당주 차이>, <당주 - 차주 차이> 비교하여 L/T 감소 추이를 체크함.
    df_in_BOD_ITEM_LT['LT_CHECK'] = np.select(
        [
            (df_in_BOD_ITEM_LT['LT_DIFF'] >= 0) & (df_in_BOD_ITEM_LT['LT_DIFF_SHIFT_1'] < 0),
            (df_in_BOD_ITEM_LT['LT_DIFF'] < 0) & (df_in_BOD_ITEM_LT['LT_DIFF_SHIFT_1'] >= 0)
        ],
        ['START', 'END'],
        default='KEEP'
    )
    df_in_BOD_ITEM_LT['LT_STATUS'] = np.select(
        [
            (df_in_BOD_ITEM_LT['LT_DIFF'] >= 0) & (df_in_BOD_ITEM_LT['LT_DIFF_SHIFT_1'] < 0),
            (df_in_BOD_ITEM_LT['LT_DIFF'] < 0) & (df_in_BOD_ITEM_LT['LT_DIFF_SHIFT_1'] >= 0),
            (df_in_BOD_ITEM_LT['LT_DIFF'] < 0) & (df_in_BOD_ITEM_LT['LT_DIFF_SHIFT_1'] < 0),
        ],
        ['DOWN', 'DOWN', 'DOWN'],
        default='KEEP'
    )
    #save_csv_file(df_in_BOD_ITEM_LT, "TEMP_df_in_BOD_ITEM_LT_967")
    step('=====> STEP3-8 End : DataFrame df_in_BOD_ITEM_LT')
    step('=====> STEP3 End')

    ################################################################################################################
    # STEP 4 :  데이타 게산
    ################################################################################################################
    step('=====> STEP4 Start : 데이타 계산')
    step('=====> STEP4-1 Start : SAFETYSTOCK 수량 데이타 계산')
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # (1) <SAFETYSTOCK> 수량 계산
    #  1-1 df_in_EOH_SAFETYSTOCK 에서 <Safety Stock Target_TIME> 일자를 Week, Day로 계산함.
    #  1-2 Week 기간 만큼의 GI 수량 합계 + (Day 속한 주차의 GI 수량 * (Day/7))
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #  0. <Safety Stock Target_TIME> 데이타로 Week, Day로 계산함.
    df_in_EOH_SAFETYSTOCK['STOCK_WEEK'] = (df_in_EOH_SAFETYSTOCK[SS_SS_TARGET_TIME_COLUMN] //7).astype(dtype='int32', errors='ignore')
    df_in_EOH_SAFETYSTOCK['STOCK_DAY'] = (df_in_EOH_SAFETYSTOCK[SS_SS_TARGET_TIME_COLUMN] % 7).astype(dtype='int32', errors='ignore')
    #  1. <SAFETYSTOCK> 재고 구함.
    #  1. 1 Day에 해당되는 GI 수량 계산
    df_in_GI_DATA = df_in_Demand_GI_SHORT[
        [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, SS_GI_COLUMN]]
    #print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK_1000")
    df_in_EOH_SAFETYSTOCK['STOCK_DAY_WEEK'] = df_in_EOH_SAFETYSTOCK.apply(findDayWeek, axis=1)
    #print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK_1002")
    df_temp_SAFETYSTOCK_DAY = df_in_EOH_SAFETYSTOCK.copy()
    df_temp_SAFETYSTOCK_DAY =df_temp_SAFETYSTOCK_DAY[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,
                                                      TIME_WEEK_COLUMN,'STOCK_DAY','STOCK_DAY_WEEK']]
    # 1.1.1 Day 속한 주차의 GI 수량 찾기 위해 Join 주차를 변경함.
    #print_df(df_temp_SAFETYSTOCK_DAY, "df_temp_SAFETYSTOCK_DAY_1005")
    #print_df(df_in_GI_DATA, "df_in_GI_DATA_1006")
    df_temp_SAFETYSTOCK_DAY.rename(columns={TIME_WEEK_COLUMN :'Time.[Week]_ORG', 'STOCK_DAY_WEEK':TIME_WEEK_COLUMN}, inplace=True)
    df_temp_SAFETYSTOCK_DAY = pd.merge(df_temp_SAFETYSTOCK_DAY, df_in_GI_DATA, how='left',
                                     on=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN])
    df_temp_SAFETYSTOCK_DAY[SS_GI_COLUMN] = df_temp_SAFETYSTOCK_DAY[SS_GI_COLUMN].fillna(0)
    df_temp_SAFETYSTOCK_DAY[SS_GI_COLUMN] = (df_temp_SAFETYSTOCK_DAY[SS_GI_COLUMN] * (df_temp_SAFETYSTOCK_DAY['STOCK_DAY']/7))
    # 1.1.2 TIME_WEEK 열이름 원상복구 및 필요없는 열 삭제
    df_temp_SAFETYSTOCK_DAY.rename(columns={'Time.[Week]_ORG':TIME_WEEK_COLUMN, TIME_WEEK_COLUMN:'STOCK_DAY_WEEK',
                                            SS_GI_COLUMN:'STOCK_DAY_QTY'}, inplace=True)

    df_temp_SAFETYSTOCK_DAY = drop_dataframe(df_temp_SAFETYSTOCK_DAY, ['STOCK_DAY','STOCK_DAY_WEEK'])
    # 1.1.3 Input DataFrame에 STOCK_DAY_QTY (Day 속한 주차의 GI 수량 * (Day/7)) 을 Merge 함.
    df_in_EOH_SAFETYSTOCK = pd.merge(df_in_EOH_SAFETYSTOCK,df_temp_SAFETYSTOCK_DAY, how="left", on=join_column)
    df_in_EOH_SAFETYSTOCK['STOCK_DAY_QTY'] = df_in_EOH_SAFETYSTOCK['STOCK_DAY_QTY'].fillna(0)
    #print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK")
    step('=====> STEP4-1 End : GI 수량 찾기')
    # 1.2 Week 기간 만큼의 GI 수량 합계
    # 1.2.1 safetyStock_CreateDictionary 함수 => TEMP_SAFETYSTOCK Dictionary 생성
    df_in_EOH_SAFETYSTOCK['CALL_FLAG'] = df_in_EOH_SAFETYSTOCK.apply(safetyStock_CreateDictionary, axis=1)
    step('=====> STEP4-1 End: CALL_FLAG')

    df_temp_week_safetystock = pd.DataFrame(TEMP_SAFETYSTOCK)
    df_temp_week_safetystock.rename(columns={TIME_WEEK_COLUMN : 'Time.[Week]_ORG', 'STOCK_TIME_WEEK':TIME_WEEK_COLUMN}, inplace=True)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #형변환(2026.02.27 추가)
    column_type = [VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN, 'Time.[Week]_ORG']
    for col in column_type:
        df_temp_week_safetystock[col] = df_temp_week_safetystock[col].astype(str)
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    print_df(df_temp_week_safetystock, "df_temp_week_safetystock")
    print_df(df_in_GI_DATA, "df_in_GI_DATA")
    df_temp_week_safetystock = pd.merge(df_temp_week_safetystock, df_in_GI_DATA, how='left', on=join_column)
    print_df(df_temp_week_safetystock, "df_temp_week_safetystock_rename전_TEST")
    df_temp_week_safetystock.rename(columns={'Time.[Week]_ORG':TIME_WEEK_COLUMN, TIME_WEEK_COLUMN:'STOCK_TIME_WEEK', SS_GI_COLUMN:"STOCK_WEEK_QTY"}, inplace=True)
    print_df(df_temp_week_safetystock, "df_temp_week_safetystock_rename후_TEST")

    df_temp_week_safetystock['STOCK_WEEK_QTY']=df_temp_week_safetystock['STOCK_WEEK_QTY'].astype(float)
    step('=====>Debug Merge -> Rename')
    # 1.2.2 Sub Location + Item + Time_Week 기준으로 GroupBy함.
    df_temp_week_safetystock = df_temp_week_safetystock.groupby(by=join_column).sum().reset_index()
    step('=====>Debug Merge -> Rename(1)')
    print_df(df_temp_week_safetystock, "df_temp_week_safetystock_groupby")
    print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK_STOCK_WEEK_QTY")
    df_in_EOH_SAFETYSTOCK = pd.merge(df_in_EOH_SAFETYSTOCK,df_temp_week_safetystock, how="left", on=join_column)
    step('=====>Debug Merge -> Rename(2)')
    print_df(df_in_EOH_SAFETYSTOCK, "df_in_EOH_SAFETYSTOCK_STOCK_WEEK_QTY_MERGE")
    df_in_EOH_SAFETYSTOCK['STOCK_WEEK_QTY'] = df_in_EOH_SAFETYSTOCK['STOCK_WEEK_QTY'].fillna(0)

    step('=====> STEP4-1 End :Group By STOCK_WEEK_QTY 구하기')

    # 1.3.1 <SAFETYSTOCK> 수량 계산 = STOCK_WEEK_QTY + STOCK_DAY_QTY + SS_SS_TARGET_QTY_COLUMN
    #----------------------------------------------------------------------------------------
    df_in_EOH_SAFETYSTOCK[SS_SS_COLUMN] = (df_in_EOH_SAFETYSTOCK['STOCK_WEEK_QTY']
                                           + df_in_EOH_SAFETYSTOCK['STOCK_DAY_QTY']
                                           + df_in_EOH_SAFETYSTOCK[SS_SS_TARGET_QTY_COLUMN])
    step('=====> STEP4-1 End : STOCK QTY 구하기')
    # 1.3.2 컬럼 삭제
    dropColumns = [TIME_DAY_COLUMN, 'CALL_FLAG','STOCK_DAY_WEEK','STOCK_WEEK','STOCK_DAY','STOCK_WEEK_QTY','STOCK_DAY_QTY']
    df_in_EOH_SAFETYSTOCK = drop_dataframe(df_in_EOH_SAFETYSTOCK, dropColumns)
    step('=====> STEP4-1 End : SAFETYSTOCK 수량 데이타 계산')
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # (2) Safety Stock Monitoring SUM 에 해당되는 데이타 생성
    # <SAFETYSTOCK> 데이타 기준으로  유니크한 데이타프레임 한판 생성
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    step('=====> STEP4-2-1 Start : Safety Stock Monitoring SUM 에 해당되는 데이타 생성')
    # 빈 주차 채워넣기
    #  데이터의 모든 고유 조합 생성
    unique_key = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN]
    unique_combinations = make_combinations(df_in_Time, df_in_EOH_SAFETYSTOCK,unique_key )

    df_in_EOH_SAFETYSTOCK = pd.merge(unique_combinations, df_in_EOH_SAFETYSTOCK, how='left', on=join_column_ap2)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #unique Data 추출
    unique_combinations = unique_combinations[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,
                                               SALES_DOMAIN_AP2_COLUMN,TIME_WEEK_COLUMN]]
    step('=====> STEP4-2-2 Start :df_in_Arrival  EOH_SAFETYSTOCK 데이타 기준으로  데이타 join')
    # df_in_Arrival  EOH_SAFETYSTOCK 데이타 기준으로  데이타 join
    df_in_Arrival_key = df_in_Arrival[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,
                                       LOCATION_COLUMN,TRANS_MODE_COLUMN]].drop_duplicates()
    df_in_Arrival_key = pd.merge(unique_combinations, df_in_Arrival_key, how="left",
                             on=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN])
    df_in_Arrival = pd.merge(df_in_Arrival_key, df_in_Arrival, how="left",
                             on=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN,
                                 LOCATION_COLUMN,TRANS_MODE_COLUMN]).drop(columns=[ACTIVITY1_ACTIVITY1_COLUMN])
    df_in_Arrival[SS_ARRIVAL_COLUMN] = df_in_Arrival[SS_ARRIVAL_COLUMN].fillna(0)
    step('=====> STEP4-2-3 Start :df_in_Shipment  EOH_SAFETYSTOCK 데이타 기준으로  데이타 join')
    # df_in_Shipment  EOH_SAFETYSTOCK 데이타 기준으로  데이타 join
    df_in_Shipment_key = df_in_Arrival[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,
                                       LOCATION_COLUMN,TRANS_MODE_COLUMN]].drop_duplicates()
    df_in_Shipment_key = pd.merge(unique_combinations, df_in_Shipment_key, how="left",
                             on=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN])
    df_in_Shipment = pd.merge(df_in_Shipment_key, df_in_Shipment, how="left",
                             on=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN,
                                 LOCATION_COLUMN,TRANS_MODE_COLUMN]).drop(columns=[ACTIVITY1_ACTIVITY1_COLUMN])
    step('=====> STEP4-2-4 Start :Shipment LT 타입 추가')
    # Shipment LT 타입 추가
    # Lead Time 정보를 Join 함.
    df_in_Shipment = pd.merge( df_in_Shipment, df_in_BOD_ITEM_LT, how="left",
                              on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                                  LOCATION_COLUMN,TRANS_MODE_COLUMN,TIME_WEEK_COLUMN])
    df_in_Shipment[BOD_ITEM_LT] = df_in_Shipment[BOD_ITEM_LT].fillna(0)
    df_in_Shipment.rename(columns={BOD_ITEM_LT:SS_ITEM_BOD_LT_COLUMN}, inplace=True)
    step('=====> STEP4-2-5 Start :LT에 해당되는 주차 찾기')
    # LT에 해당되는 주차 찾기
    df_in_Shipment = df_in_Shipment.sort_values(by=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN,
                                                    ITEM_COLUMN, LOCATION_COLUMN,TRANS_MODE_COLUMN,TIME_WEEK_COLUMN])
    df_in_Shipment['BOD_LT_ENDWEEK'] = df_in_Shipment.apply(findLTWeek, axis=1)
    df_in_Shipment[SS_SHIPMENT_COLUMN] = df_in_Shipment[SS_SHIPMENT_COLUMN].fillna(0)
    #print_df(df_in_Shipment, "Merge.... df_in_Shipment")
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    step('=====> STEP4-2-6 Start :df_in_EOH_SAFETYSTOCK 기준으로 df_in_Demand_GI_SHORT 데이타 merge함.')
    # df_in_EOH_SAFETYSTOCK 기준으로 df_in_Demand_GI_SHORT 데이타 merge함.
    df_out_SS_Monitor_SUM = pd.merge( df_in_EOH_SAFETYSTOCK, df_in_Demand_GI_SHORT, how="left", on=join_column_ap2)

    # Null 데이타 0으로 채움
    fillna_int_columns = [SS_DEMAND_COLUMN, SS_GI_COLUMN, SS_SHORT_COLUMN, SS_EOH_COLUMN,
                          SS_SS_TARGET_TIME_COLUMN, SS_SS_TARGET_QTY_COLUMN, SS_SS_COLUMN]
    for col in fillna_int_columns:
        df_out_SS_Monitor_SUM[col] = df_out_SS_Monitor_SUM[col].fillna(0)

    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    step('=====> STEP4-2-7 Start :SS Monitor_SS Short 계산')
    # 2.1 <SS Monitor_SS Short> = MAX( SAFETYSTOCK-EOH , 0 )
    df_out_SS_Monitor_SUM[SS_SS_SHORT_COLUMN] = np.where(
        df_out_SS_Monitor_SUM[SS_SS_COLUMN] - df_out_SS_Monitor_SUM[SS_EOH_COLUMN] > 0,
        df_out_SS_Monitor_SUM[SS_SS_COLUMN] - df_out_SS_Monitor_SUM[SS_EOH_COLUMN], 0)
    step('=====> STEP4-2-8 Start :SS Monitor_Arrival 계산')
    # 2.2 <SS Monitor_Arrival> Sum을 계산함
    # Sub Location + Sales Domain AP2 + ITEM + Time_Week 별 GroupBy
    sum_columns = [SS_ARRIVAL_COLUMN]
    agg_dict = {col: 'sum' for col in sum_columns}
    df_temp_Arrival_Sum = df_in_Arrival.groupby(by=join_column_ap2).agg(agg_dict,skipna=True).reset_index()

    df_out_SS_Monitor_SUM = pd.merge(df_out_SS_Monitor_SUM, df_temp_Arrival_Sum, how="left", on=join_column_ap2)
    df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN] = df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN].fillna(0)
    step('=====> STEP4-2-9 Start :SS_MONITOR_ARRIVAL_JIT 계산')
    # 2.3 <SS_MONITOR_ARRIVAL_JIT> 계산
    # SS_MONITOR_ARRIVAL_JIT = MAX( Arrival-EOH , 0 )
    df_out_SS_Monitor_SUM[SS_ARRIVAL_JIT_COLUMN] = np.where(
        df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN] - df_out_SS_Monitor_SUM[SS_EOH_COLUMN] > 0,
        df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN] - df_out_SS_Monitor_SUM[SS_EOH_COLUMN], 0)
    step('=====> STEP4-2-10 Start :SS Monitor_Arrival SS 계산')
    # 2.4 <SS Monitor_Arrival SS> 계산
    # SS Monitor_Arrival SS = MIN( EOH, SAFETYSTOCK, Arrival)
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN] = np.where(
        df_out_SS_Monitor_SUM[SS_EOH_COLUMN] <= df_out_SS_Monitor_SUM[SS_SS_COLUMN],
        df_out_SS_Monitor_SUM[SS_EOH_COLUMN], df_out_SS_Monitor_SUM[SS_SS_COLUMN])
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN] = np.where(
        df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN] <= df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN],
        df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN],df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN])

    step('=====> STEP4-2-11 Start :GI 1W, 2W 계산')
    # 2.5 <SS Monitor_Arrival SS 1W> 계산
    # GI 1W 데이타를 먼저 구함.
    step('=====>GI 1W ')
    df_temp_gi = df_out_SS_Monitor_SUM[[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, SS_GI_COLUMN]]
    df_temp_gi.sort_values(by=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN], axis=0)
    #save_csv_file(df_temp_gi, "df_temp_gi");
    #save_csv_file(df_in_Time_3W, "df_in_Time_3W")
    df_temp_gi = df_temp_gi.loc[df_temp_gi[SS_GI_COLUMN] > 0]  #테스트(26.02.02)
    #print_df(df_temp_gi, "df_temp_gi")
    df_temp_gi_org = df_temp_gi.copy()
    df_temp_gi = pd.merge(df_temp_gi,df_in_Time_3W, how="left", on=[TIME_WEEK_COLUMN])
    df_temp_gi['STOCK_WEEK'] = 1
    step('=====>df_temp_gi 체크')
    df_temp_gi.rename(columns={TIME_WEEK_COLUMN: TIME_WEEK_COLUMN+'_ORG','1w_week':TIME_WEEK_COLUMN, SS_GI_COLUMN:SS_GI_COLUMN+'_ORG'}, inplace=True)
    df_temp_gi = df_temp_gi[[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN,TIME_WEEK_COLUMN+'_ORG',SS_GI_COLUMN+'_ORG','2w_week','3w_week','STOCK_WEEK']]
    #print_df(df_temp_gi, "df_temp_gi")
    #print_df(df_temp_gi_org, "df_temp_gi_org")
    step('=====>df_temp_gi 체크(1)')
    df_temp_gi = pd.merge(df_temp_gi, df_temp_gi_org, how="left", on=[VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN])
    df_temp_gi.rename(columns={TIME_WEEK_COLUMN + '_ORG':TIME_WEEK_COLUMN, TIME_WEEK_COLUMN :'1w_week',
                               SS_GI_COLUMN:'gi_1w_qty' }, inplace=True)
    #print_df(df_temp_gi, "df_temp_gi")
    step('=====>GI 2W ')
    # GI 2W 데이타를 먼저 구함.
    df_temp_gi['STOCK_WEEK'] = 2
    df_temp_gi.rename(columns={TIME_WEEK_COLUMN: TIME_WEEK_COLUMN + '_ORG', '2w_week': TIME_WEEK_COLUMN}, inplace=True)
    df_temp_gi = pd.merge(df_temp_gi, df_temp_gi_org, how="left",
                          on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN])
    df_temp_gi.rename(columns={TIME_WEEK_COLUMN + '_ORG': TIME_WEEK_COLUMN, TIME_WEEK_COLUMN: '2w_week',
                               SS_GI_COLUMN: 'gi_2w_qty', SS_GI_COLUMN+'_ORG':SS_GI_COLUMN}, inplace=True)
    #save_csv_file(df_temp_gi, "df_temp_gi_data")
    #불필요한 열 삭제
    #print_df(df_temp_gi, "df_temp_gi")
    #drop_column=[SS_GI_COLUMN, TIME_DAY_COLUMN, 'STOCK_WEEK','1w_week','2w_week']
    drop_column = [SS_GI_COLUMN,  'STOCK_WEEK', '1w_week', '2w_week']
    df_temp_gi = drop_dataframe(df_temp_gi, drop_column)
    df_out_SS_Monitor_SUM = pd.merge(df_out_SS_Monitor_SUM, df_temp_gi, how="left", on=join_column)
    step('=====> STEP4-2-12 Start :SS Monitor_Arrival SS 1W 계산')
    # <SS Monitor_Arrival SS 1W> 계산
    # <SS Monitor_Arrival SS 1W> = MIN( Arrival SS, MAX(GI_1W_QTY, 0))
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_1W_COLUMN] = np.where(df_out_SS_Monitor_SUM['gi_1w_qty'] > 0,
                                                                      df_out_SS_Monitor_SUM['gi_1w_qty'], 0)
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_1W_COLUMN] = np.where(
        df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_1W_COLUMN] > df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN],
        df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN], df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_1W_COLUMN])
    step('=====> STEP4-2-13 Start :SS Monitor_Arrival SS 2W 계산')
    # <SS Monitor_Arrival SS 2W> 계산
    # <SS Monitor_Arrival SS 2W> = MIN( Arrival SS - Arrival SS 1W, MAX(GI_2W_QTY, 0))
    # <SS Monitor_Arrival SS 2W> = MIN( Arrival SS - Arrival SS 1W, MAX(GI_2W_QTY, 0))
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_2W_COLUMN] = np.where(
        df_out_SS_Monitor_SUM['gi_2w_qty'] > 0,df_out_SS_Monitor_SUM['gi_2w_qty'], 0)
    df_out_SS_Monitor_SUM['temp'] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN] - df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_1W_COLUMN])
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_2W_COLUMN] = np.where(
        df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_2W_COLUMN] > df_out_SS_Monitor_SUM['temp'],
        df_out_SS_Monitor_SUM['temp'], df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_2W_COLUMN])
    step('=====> STEP4-2-14 Start :SS Monitor_Arrival SS 3W 계산')
    # <SS Monitor_Arrival SS 3W> 계산
    # <SS Monitor_Arrival SS 3W> = Arrival SS - SUM( Arrival SS 1W, Arrival SS 2W )
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_3W_COLUMN] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_1W_COLUMN] + df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_2W_COLUMN])
    df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_3W_COLUMN] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN] - df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_3W_COLUMN])
    step('=====> STEP4-2-15 Start :SS Monitor_Arrival SS 3W 계산')
    # <SS Monitor_Arrival BuildAhead> 계산
    # <SS Monitor_Arrival BuildAhead> = Arrival - Arrival JIT - Arrival SS
    df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_COLUMN] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN] -  df_out_SS_Monitor_SUM[SS_ARRIVAL_JIT_COLUMN])
    df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_COLUMN] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_COLUMN] - df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN])
    # <SS Monitor_Arrival BuildAhead 1W> 계산
    # <SS Monitor_Arrival BuildAhead 1W> = MIN( Arrival BuildAhead, MAX(GI@(Time.#.LeadOffset(1)) - Arrival SS 1W,0) )
    df_out_SS_Monitor_SUM['temp'] = df_out_SS_Monitor_SUM['gi_1w_qty'] - df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN]
    df_out_SS_Monitor_SUM['temp'] = np.where(df_out_SS_Monitor_SUM['temp'] > 0, df_out_SS_Monitor_SUM['temp'], 0)
    df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_1W_COLUMN] = np.where(
        df_out_SS_Monitor_SUM['temp'] > df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_COLUMN],
        df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_COLUMN],df_out_SS_Monitor_SUM['temp'])
    # <SS Monitor_Arrival BuildAhead 2W> 계산
    # <SS Monitor_Arrival BuildAhead 2W> =
    #   MIN( Arrival BuildAhead-SS Monitor_Arrival BuildAhead 1W, MAX( GI@(Time.#.LeadOffset(2))- Arrival SS 1W,0) )
    # 2025.05.27 계산 공식 변경
    # <SS Monitor_Arrival BuildAhead 2W> = MIN( Arrival - Arrival_JIT - Arrival_SS - SS Monitor_Arrival BuildAhead 1W ,
    #                                            MAX( GI@(Time.#.LeadOffset(2))- Arrival SS 1W,0) )
    # 2025.05.29 수정
    #df_out_SS_Monitor_SUM['temp_OLD'] = df_out_SS_Monitor_SUM['gi_2w_qty'] - df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_1W_COLUMN]
    #df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN+'_OLD'] = (
    #        df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_COLUMN] - df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_1W_COLUMN])

    df_out_SS_Monitor_SUM['temp'] = df_out_SS_Monitor_SUM['gi_2w_qty'] - df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_2W_COLUMN]
    df_out_SS_Monitor_SUM['temp'] = np.where(df_out_SS_Monitor_SUM['temp'] > 0, df_out_SS_Monitor_SUM['temp'], 0)
    df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_COLUMN] - df_out_SS_Monitor_SUM[SS_ARRIVAL_JIT_COLUMN]
            - df_out_SS_Monitor_SUM[SS_ARRIVAL_SS_COLUMN] - df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_1W_COLUMN])

    df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN] = np.where(
        df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN] > df_out_SS_Monitor_SUM['temp'],
        df_out_SS_Monitor_SUM['temp'],df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN])

    # <SS Monitor_Arrival BuildAhead 3W> 계산
    # <SS Monitor_Arrival BuildAhead 3W> = Arrival BuildAhead - SUM( Arrival BuildAhead 1W, Arrival BuildAhead 2W )
    df_out_SS_Monitor_SUM['temp'] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_1W_COLUMN] + df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN])
    df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_3W_COLUMN] = (
            df_out_SS_Monitor_SUM[SS_ARRIVAL_BUILDAHEAD_COLUMN] - df_out_SS_Monitor_SUM['temp'])
    #
    df_out_SS_Monitor_SUM[LOCATION_COLUMN] = '-'
    df_out_SS_Monitor_SUM[TRANS_MODE_COLUMN] = '-'
    #데이타 프레임 열재배열
    df_out_SS_Monitor_SUM = df_out_SS_Monitor_SUM[ss_monitor_Arrival_column]
    # 오래 걸림.. (ㅠ.ㅠ)
    step('=====> STEP4-2 End : SUM 데이타 계산')
    step('=====> STEP4-3 Arrival(ROW) Start')

    join_arrival_column = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN]
    # Row 단위별 Arrival 데이타를 계산하기 위해
    df_in_Arrival_SUM = df_out_SS_Monitor_SUM.copy()
    df_in_Arrival_SUM = df_in_Arrival_SUM[[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN,
                                           SS_SS_COLUMN,SS_ARRIVAL_COLUMN, SS_ARRIVAL_JIT_COLUMN, SS_ARRIVAL_SS_COLUMN,
                                           SS_ARRIVAL_SS_1W_COLUMN, SS_ARRIVAL_SS_2W_COLUMN, SS_ARRIVAL_SS_3W_COLUMN,
                                           SS_ARRIVAL_BUILDAHEAD_COLUMN, SS_ARRIVAL_BUILDAHEAD_1W_COLUMN,
                                           SS_ARRIVAL_BUILDAHEAD_2W_COLUMN, SS_ARRIVAL_BUILDAHEAD_3W_COLUMN]]
    df_in_Arrival_SUM.rename(columns={SS_SS_COLUMN:SS_SS_COLUMN +'_SUM',
                                      SS_ARRIVAL_COLUMN:SS_ARRIVAL_COLUMN +'_SUM',
                                      SS_ARRIVAL_JIT_COLUMN:SS_ARRIVAL_JIT_COLUMN +'_SUM',
                                      SS_ARRIVAL_SS_COLUMN:SS_ARRIVAL_SS_COLUMN +'_SUM',
                                      SS_ARRIVAL_SS_1W_COLUMN:SS_ARRIVAL_SS_1W_COLUMN +'_SUM',
                                      SS_ARRIVAL_SS_2W_COLUMN:SS_ARRIVAL_SS_2W_COLUMN +'_SUM',
                                      SS_ARRIVAL_SS_3W_COLUMN:SS_ARRIVAL_SS_3W_COLUMN +'_SUM',
                                      SS_ARRIVAL_BUILDAHEAD_COLUMN:SS_ARRIVAL_BUILDAHEAD_COLUMN +'_SUM',
                                      SS_ARRIVAL_BUILDAHEAD_1W_COLUMN:SS_ARRIVAL_BUILDAHEAD_1W_COLUMN +'_SUM',
                                      SS_ARRIVAL_BUILDAHEAD_2W_COLUMN:SS_ARRIVAL_BUILDAHEAD_2W_COLUMN +'_SUM',
                                      SS_ARRIVAL_BUILDAHEAD_3W_COLUMN:SS_ARRIVAL_BUILDAHEAD_3W_COLUMN +'_SUM'},
                             inplace=True)
    df_in_Arrival = pd.merge(df_in_Arrival_SUM,df_in_Arrival, how="left", on=join_arrival_column)

    # Arrival ROW 단위 계산
    # <SS Monitor_SS> = 해당 열의 Arrival/SUM(Arrival)* 전체 SAFETYSTOCK
    df_in_Arrival[SS_SS_COLUMN]= ((df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM'])
                                    * df_in_Arrival[SS_SS_COLUMN +'_SUM'])
    # <SS Monitor_Arrival JIT> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival JIT
    df_in_Arrival[SS_ARRIVAL_JIT_COLUMN]= ((df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM'])
                                            * df_in_Arrival[SS_ARRIVAL_JIT_COLUMN +'_SUM'])
    # <SS Monitor_Arrival SS> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival SS
    df_in_Arrival[SS_ARRIVAL_SS_COLUMN]= ((df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM'])
                                           * df_in_Arrival[SS_ARRIVAL_SS_COLUMN +'_SUM'])
    # <SS Monitor_Arrival SS 1W> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival SS 1W
    df_in_Arrival[SS_ARRIVAL_SS_1W_COLUMN]= ((df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM'])
                                              * df_in_Arrival[SS_ARRIVAL_SS_1W_COLUMN +'_SUM'])
    # <SS Monitor_Arrival SS 2W> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival SS 2W
    df_in_Arrival[SS_ARRIVAL_SS_2W_COLUMN]=((df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM'])
                                              * df_in_Arrival[SS_ARRIVAL_SS_2W_COLUMN +'_SUM'])
    # <SS Monitor_Arrival SS 3W> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival SS 3W
    df_in_Arrival[SS_ARRIVAL_SS_3W_COLUMN]= (df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM']
                                             * df_in_Arrival[SS_ARRIVAL_SS_3W_COLUMN +'_SUM'])
    # <SS Monitor_Arrival BuildAhead> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival BuildAhead
    df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_COLUMN]= (df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM']
                                                  * df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_COLUMN +'_SUM'])
    # <SS Monitor_Arrival BuildAhead 1W> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival BuildAhead 1W
    df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_1W_COLUMN]= (df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM']
                                                     * df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_1W_COLUMN +'_SUM'])
    # <SS Monitor_Arrival BuildAhead 2W> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival BuildAhead 2W
    df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN]= (df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM']
                                                     * df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN +'_SUM'])
    # <SS Monitor_Arrival BuildAhead 3W> = 해당 열의 Arrival/전체 Arrival * 전체 Arrival BuildAhead 3W
    df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_3W_COLUMN]= (df_in_Arrival[SS_ARRIVAL_COLUMN] / df_in_Arrival[SS_ARRIVAL_COLUMN +'_SUM']
                                                     * df_in_Arrival[SS_ARRIVAL_BUILDAHEAD_3W_COLUMN +'_SUM'])

    #열 삭제
    drop_column=[SS_SS_COLUMN +'_SUM',SS_ARRIVAL_COLUMN +'_SUM',SS_ARRIVAL_JIT_COLUMN +'_SUM',SS_ARRIVAL_SS_COLUMN +'_SUM',
                 SS_ARRIVAL_SS_1W_COLUMN +'_SUM',SS_ARRIVAL_SS_2W_COLUMN +'_SUM',SS_ARRIVAL_SS_3W_COLUMN +'_SUM',
                 SS_ARRIVAL_BUILDAHEAD_COLUMN +'_SUM',SS_ARRIVAL_BUILDAHEAD_1W_COLUMN +'_SUM',
                 SS_ARRIVAL_BUILDAHEAD_2W_COLUMN +'_SUM',SS_ARRIVAL_BUILDAHEAD_3W_COLUMN +'_SUM']
    df_in_Arrival = drop_dataframe(df_in_Arrival, drop_column)

    step('=====> STEP4-3 Arrival(ROW) End')
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Merge : df_in_Shipment +  df_in_Arrival
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    step('=====> STEP4-3 df_in_Shipment_LT Start')
    # L/T 감안한 Shipment 데이타프레임 df_in_Shipment_LT 생성
    df_in_Shipment_LT = df_in_Shipment.copy()
    df_in_Shipment_LT.rename(columns={TIME_WEEK_COLUMN:TIME_WEEK_COLUMN+"_ORG", "BOD_LT_ENDWEEK":TIME_WEEK_COLUMN},
                             inplace=True)
    # 계산한 Arrival DF 와 Shipment DF Merge 함.
    df_in_Shipment_LT = pd.merge(df_in_Shipment_LT, df_in_Arrival, how="left", on=join_column_row2)

    fillna_int_columns = [SS_ARRIVAL_JIT_COLUMN, SS_ARRIVAL_SS_COLUMN,SS_ARRIVAL_SS_1W_COLUMN,SS_ARRIVAL_SS_2W_COLUMN,
                          SS_ARRIVAL_SS_3W_COLUMN,SS_ARRIVAL_BUILDAHEAD_COLUMN, SS_ARRIVAL_BUILDAHEAD_1W_COLUMN,
                          SS_ARRIVAL_BUILDAHEAD_2W_COLUMN, SS_ARRIVAL_BUILDAHEAD_3W_COLUMN]
    for col in fillna_int_columns:
        df_in_Shipment_LT[col] = df_in_Shipment_LT[col].fillna(0)

    df_in_Shipment_LT[SS_SHIPMENT_JIT_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_JIT_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_SS_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_SS_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_SS_1W_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_SS_1W_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_SS_2W_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_SS_2W_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_SS_3W_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_SS_3W_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_BUILDAHEAD_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_1W_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_BUILDAHEAD_1W_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_2W_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_BUILDAHEAD_2W_COLUMN]
    df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_3W_COLUMN] = df_in_Shipment_LT[SS_ARRIVAL_BUILDAHEAD_3W_COLUMN]
    df_in_Shipment_LT.rename(columns={TIME_WEEK_COLUMN + "_ORG" :TIME_WEEK_COLUMN, TIME_WEEK_COLUMN:"BOD_LT_ENDWEEK"},
                             inplace=True)
    #save_csv_file(df_in_Shipment_LT, "df_in_Shipment_LT_감안_Data")
    #컬럼 삭제
    drop_column=[SS_ARRIVAL_COLUMN, SS_ARRIVAL_JIT_COLUMN, SS_ARRIVAL_SS_COLUMN,SS_ARRIVAL_SS_1W_COLUMN,
                 SS_ARRIVAL_SS_2W_COLUMN, SS_ARRIVAL_SS_3W_COLUMN,SS_ARRIVAL_BUILDAHEAD_COLUMN,
                 SS_ARRIVAL_BUILDAHEAD_1W_COLUMN, SS_ARRIVAL_BUILDAHEAD_2W_COLUMN, SS_ARRIVAL_BUILDAHEAD_3W_COLUMN,
                 TIME_DAY_COLUMN]
    df_in_Shipment_LT = drop_dataframe(df_in_Shipment_LT, drop_column)

    # L/T Down 데이타 체크
    df_down_Shipment = df_in_Shipment_LT.loc[df_in_Shipment_LT['LT_STATUS'] == 'DOWN']
    if (df_down_Shipment.empty == False):
        df_down_Shipment = df_down_Shipment.sort_values(
            by=[VERSION_NAME_COLUMN, SALES_DOMAIN_AP2_COLUMN, SUB_LOCATION_COLUMN,
                ITEM_COLUMN,LOCATION_COLUMN,TRANS_MODE_COLUMN,TIME_WEEK_COLUMN])
        df_down_Shipment.reset_index(drop=True, inplace=True)
        df_down_Shipment.rename(columns={SS_SHIPMENT_COLUMN : SS_SHIPMENT_COLUMN + '_ORG',
                                         SS_SHIPMENT_JIT_COLUMN: SS_SHIPMENT_JIT_COLUMN + '_ORG',
                                         SS_SHIPMENT_SS_COLUMN: SS_SHIPMENT_SS_COLUMN + '_ORG',
                                         SS_SHIPMENT_SS_1W_COLUMN: SS_SHIPMENT_SS_1W_COLUMN + '_ORG',
                                         SS_SHIPMENT_SS_2W_COLUMN: SS_SHIPMENT_SS_2W_COLUMN + '_ORG',
                                         SS_SHIPMENT_SS_3W_COLUMN: SS_SHIPMENT_SS_3W_COLUMN + '_ORG',
                                         SS_SHIPMENT_BUILDAHEAD_COLUMN:SS_SHIPMENT_BUILDAHEAD_COLUMN +'_ORG',
                                         SS_SHIPMENT_BUILDAHEAD_1W_COLUMN: SS_SHIPMENT_BUILDAHEAD_1W_COLUMN + '_ORG',
                                         SS_SHIPMENT_BUILDAHEAD_2W_COLUMN: SS_SHIPMENT_BUILDAHEAD_2W_COLUMN + '_ORG',
                                         SS_SHIPMENT_BUILDAHEAD_3W_COLUMN: SS_SHIPMENT_BUILDAHEAD_3W_COLUMN + '_ORG'
                                         }, inplace=True)
        df_down_Shipment = calculate_LT_Down_Shipment(df_down_Shipment)
        df_down_Shipment.drop(columns=[SS_SHIPMENT_COLUMN +'_ORG',SS_SHIPMENT_JIT_COLUMN +'_ORG',
                                       SS_SHIPMENT_SS_COLUMN +'_ORG',SS_SHIPMENT_SS_1W_COLUMN +'_ORG',
                                       SS_SHIPMENT_SS_2W_COLUMN +'_ORG',SS_SHIPMENT_SS_3W_COLUMN +'_ORG',
                                       SS_SHIPMENT_BUILDAHEAD_COLUMN + '_ORG',SS_SHIPMENT_BUILDAHEAD_1W_COLUMN +'_ORG',
                                       SS_SHIPMENT_BUILDAHEAD_2W_COLUMN +'_ORG',SS_SHIPMENT_BUILDAHEAD_3W_COLUMN +'_ORG',
                                       SALES_DOMAIN_AP2_COLUMN, 'LT_DIFF', 'LT_DIFF_SHIFT_1', 'LT_CHECK', 'LT_STATUS' ],
                              inplace=True)
        df_in_Shipment_LT = pd.merge(df_in_Shipment_LT, df_down_Shipment, how='left',
                                     on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                                         LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
        df_in_Shipment_LT.rename(columns={SS_SHIPMENT_JIT_COLUMN +'_x' : SS_SHIPMENT_JIT_COLUMN,
                                          SS_SHIPMENT_SS_COLUMN +'_x' : SS_SHIPMENT_SS_COLUMN,
                                          SS_SHIPMENT_SS_1W_COLUMN +'_x' : SS_SHIPMENT_SS_1W_COLUMN,
                                          SS_SHIPMENT_SS_2W_COLUMN +'_x' : SS_SHIPMENT_SS_2W_COLUMN,
                                          SS_SHIPMENT_SS_3W_COLUMN +'_x' : SS_SHIPMENT_SS_3W_COLUMN,
                                          SS_SHIPMENT_BUILDAHEAD_COLUMN +'_x' :SS_SHIPMENT_BUILDAHEAD_COLUMN,
                                          SS_SHIPMENT_BUILDAHEAD_1W_COLUMN +'_x' : SS_SHIPMENT_BUILDAHEAD_1W_COLUMN,
                                          SS_SHIPMENT_BUILDAHEAD_2W_COLUMN +'_x' : SS_SHIPMENT_BUILDAHEAD_2W_COLUMN,
                                          SS_SHIPMENT_BUILDAHEAD_3W_COLUMN +'_x' : SS_SHIPMENT_BUILDAHEAD_3W_COLUMN,
                                          SS_ITEM_BOD_LT_COLUMN + '_x' : SS_ITEM_BOD_LT_COLUMN},
                                 inplace=True)
        df_in_Shipment_LT[SS_SHIPMENT_JIT_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_JIT_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_JIT_COLUMN])
        df_in_Shipment_LT[SS_SHIPMENT_SS_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_COLUMN])
        df_in_Shipment_LT[SS_SHIPMENT_SS_1W_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_1W_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_1W_COLUMN])
        df_in_Shipment_LT[SS_SHIPMENT_SS_2W_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_2W_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_2W_COLUMN])
        df_in_Shipment_LT[SS_SHIPMENT_SS_3W_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_3W_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_SS_3W_COLUMN])

        df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_COLUMN])
        df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_1W_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_1W_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_1W_COLUMN])
        df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_2W_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_2W_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_2W_COLUMN])
        df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_3W_COLUMN] = np.where(df_in_Shipment_LT['LT_STATUS'] == 'DOWN',
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_3W_COLUMN+'_y'],
                                                            df_in_Shipment_LT[SS_SHIPMENT_BUILDAHEAD_3W_COLUMN])

    df_in_Shipment_LT = df_in_Shipment_LT[[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN,
                                           SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN,
                                           TRANS_MODE_COLUMN, SS_ITEM_BOD_LT_COLUMN,
                                           SS_SHIPMENT_COLUMN, SS_SHIPMENT_JIT_COLUMN,
                                           SS_SHIPMENT_SS_COLUMN, SS_SHIPMENT_SS_1W_COLUMN, SS_SHIPMENT_SS_2W_COLUMN,
                                           SS_SHIPMENT_SS_3W_COLUMN, SS_SHIPMENT_BUILDAHEAD_COLUMN,
                                           SS_SHIPMENT_BUILDAHEAD_1W_COLUMN, SS_SHIPMENT_BUILDAHEAD_2W_COLUMN,
                                           SS_SHIPMENT_BUILDAHEAD_3W_COLUMN]]

    df_in_Shipment_LT[SS_ITEM_BOD_LT_COLUMN] = df_in_Shipment_LT[SS_ITEM_BOD_LT_COLUMN].fillna(0)

    # SHIPMENT Summary
    sum_columns = [SS_SHIPMENT_COLUMN, SS_SHIPMENT_JIT_COLUMN, SS_SHIPMENT_SS_COLUMN, SS_SHIPMENT_SS_1W_COLUMN,
                   SS_SHIPMENT_SS_2W_COLUMN, SS_SHIPMENT_SS_3W_COLUMN, SS_SHIPMENT_BUILDAHEAD_COLUMN,
                   SS_SHIPMENT_BUILDAHEAD_1W_COLUMN, SS_SHIPMENT_BUILDAHEAD_2W_COLUMN, SS_SHIPMENT_BUILDAHEAD_3W_COLUMN]
    agg_dict = {col: 'sum' for col in sum_columns}
    df_temp_Shipment_Sum = df_in_Shipment_LT.groupby(by=join_column_ap2).agg(agg_dict,skipna=True).reset_index()
    df_temp_Shipment_Sum = df_temp_Shipment_Sum[ss_monitor_Shipment_column]

    df_out_SS_Monitor_SUM = pd.merge(df_out_SS_Monitor_SUM, df_temp_Shipment_Sum, how="left", on=join_column_ap2)
    # _BuildAhead Limit 채우기
    df_out_SS_Monitor_SUM = pd.merge(df_out_SS_Monitor_SUM, df_in_Buildhead_Setting, how="left", on=join_column)

    #SUM 쪽 결측 데이타 채우기
    ## Unique한 데이타 조회
    unique_key = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN,
                  LOCATION_COLUMN, TRANS_MODE_COLUMN]
    df_unique_ss_monitor_sum = df_out_SS_Monitor_SUM[unique_key].drop_duplicates()
    df_unique_ss_monitor_sum = df_unique_ss_monitor_sum.assign(key=1)
    df_unique_ss_monitor_sum['key'] = df_unique_ss_monitor_sum['key'].astype(int)
    df_ss_monitor_sum_key = (df_unique_ss_monitor_sum.merge(df_planningWeek, how="outer")
                             .drop(columns=['key']).drop_duplicates())

    df_out_SS_Monitor_SUM = pd.merge(df_ss_monitor_sum_key, df_out_SS_Monitor_SUM, how="left",
                                     on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN,
                                         ITEM_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
    #컬럼 삭제
    df_out_SS_Monitor_ROW = pd.merge(df_in_Arrival, df_in_Shipment_LT, how="outer",
                                     on=[VERSION_NAME_COLUMN,SALES_DOMAIN_AP2_COLUMN,SUB_LOCATION_COLUMN,ITEM_COLUMN,
                                         LOCATION_COLUMN,TRANS_MODE_COLUMN,TIME_WEEK_COLUMN])

    ## Unique한 데이타 조회
    df_unique_ss_monitor_row = df_out_SS_Monitor_ROW[unique_key].drop_duplicates()
    df_unique_ss_monitor_row = df_unique_ss_monitor_row.assign(key=1)
    df_unique_ss_monitor_row['key'] = df_unique_ss_monitor_row['key'].astype(int)
    df_ss_monitor_row_key = (df_unique_ss_monitor_row.merge(df_planningWeek, how="outer")
                             .drop(columns=['key']).drop_duplicates())
    df_out_SS_Monitor_ROW = pd.merge(df_ss_monitor_row_key, df_out_SS_Monitor_ROW, how="left",
                                     on=[VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN,
                                         ITEM_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    df_out_SS_Monitor_ROW = df_out_SS_Monitor_ROW[ss_monitor_column_row]
    df_out_SS_Monitor_SUM = df_out_SS_Monitor_SUM[ss_monitor_column_sum]

    step('=====> STEP4-4 전주 데이타 Merge Start')
    pk_key = [VERSION_NAME_COLUMN, SALES_DOMAIN_AP2_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, LOCATION_COLUMN,
              TRANS_MODE_COLUMN]

    step('=====> STEP4-4-1  SUM 데이타 Merge Start')
    df_in_Pre_SS_Monitor_SUM_PK = df_in_Pre_SS_Monitor_SUM[pk_key].drop_duplicates()
    df_in_Pre_SS_Monitor_SUM = pd.merge(df_in_Pre_SS_Monitor_SUM, df_in_Pre_SS_Monitor_SUM_PK, on=pk_key, how="inner")
    df_in_Pre_SS_Monitor_SUM = df_in_Pre_SS_Monitor_SUM[ss_monitor_column_sum]
    if not df_in_Pre_SS_Monitor_SUM.empty :
        df_out_SS_Monitor_SUM = pd.concat([df_in_Pre_SS_Monitor_SUM, df_out_SS_Monitor_SUM], ignore_index=True)

    step('=====> STEP4-4-2  ROW 데이타 Merge Start')
    df_out_SS_Monitor_ROW_PK = df_out_SS_Monitor_ROW[pk_key].drop_duplicates()
    df_in_Pre_SS_Monitor_ROW = pd.merge(df_in_Pre_SS_Monitor_ROW, df_out_SS_Monitor_ROW_PK, on=pk_key, how="inner")
    df_in_Pre_SS_Monitor_ROW = df_in_Pre_SS_Monitor_ROW[ss_monitor_column_row]
    if not df_in_Pre_SS_Monitor_ROW.empty :
        df_out_SS_Monitor_ROW = pd.concat([df_in_Pre_SS_Monitor_ROW, df_out_SS_Monitor_ROW], ignore_index=True)
    step('=====> STEP4-4 전주 데이타 Merge End')
    ################################################################################################################
    # STEP 5 :  최종 Output DataFrame 생성
    ################################################################################################################
    step('=====> STEP5 Start')
    # 소수점 절사 처리
    step('=====> STEP5 Dataframe_cleaning Start')
    df_out_SS_Monitor_SUM[VERSION_NAME_COLUMN] = paramOutVersion
    df_out_SS_Monitor_ROW[VERSION_NAME_COLUMN] = paramOutVersion

    groupby_columns = [VERSION_NAME_COLUMN, SUB_LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN,
                       LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN]
    clean_column_sum = [SS_DEMAND_COLUMN,SS_GI_COLUMN,SS_SHORT_COLUMN,SS_EOH_COLUMN,SS_SS_COLUMN,
                        SS_SS_TARGET_TIME_COLUMN, SS_SS_TARGET_QTY_COLUMN,SS_SS_SHORT_COLUMN,SS_BUILDAHEAD_LIMIT_COLUMN,
                        SS_ARRIVAL_COLUMN,SS_ARRIVAL_JIT_COLUMN,SS_ARRIVAL_SS_COLUMN,SS_ARRIVAL_SS_1W_COLUMN,
                        SS_ARRIVAL_SS_2W_COLUMN,SS_ARRIVAL_SS_3W_COLUMN,SS_ARRIVAL_BUILDAHEAD_COLUMN,
                        SS_ARRIVAL_BUILDAHEAD_1W_COLUMN,SS_ARRIVAL_BUILDAHEAD_2W_COLUMN,SS_ARRIVAL_BUILDAHEAD_3W_COLUMN,
                        SS_SHIPMENT_COLUMN,SS_SHIPMENT_JIT_COLUMN,SS_SHIPMENT_SS_COLUMN,SS_SHIPMENT_SS_1W_COLUMN,
                        SS_SHIPMENT_SS_2W_COLUMN,SS_SHIPMENT_SS_3W_COLUMN,
                        SS_SHIPMENT_BUILDAHEAD_COLUMN,SS_SHIPMENT_BUILDAHEAD_1W_COLUMN,SS_SHIPMENT_BUILDAHEAD_2W_COLUMN,
                        SS_SHIPMENT_BUILDAHEAD_3W_COLUMN]
    clean_column_row = [SS_SS_COLUMN,SS_ARRIVAL_COLUMN,SS_ARRIVAL_JIT_COLUMN,SS_ARRIVAL_SS_COLUMN,
                        SS_ARRIVAL_SS_1W_COLUMN,SS_ARRIVAL_SS_2W_COLUMN,SS_ARRIVAL_SS_3W_COLUMN,
                        SS_ARRIVAL_BUILDAHEAD_COLUMN,SS_ARRIVAL_BUILDAHEAD_1W_COLUMN,SS_ARRIVAL_BUILDAHEAD_2W_COLUMN,
                        SS_ARRIVAL_BUILDAHEAD_3W_COLUMN, SS_SHIPMENT_COLUMN,SS_SHIPMENT_JIT_COLUMN,
                        SS_SHIPMENT_SS_COLUMN,SS_SHIPMENT_SS_1W_COLUMN,SS_SHIPMENT_SS_2W_COLUMN,
                        SS_SHIPMENT_SS_3W_COLUMN,SS_SHIPMENT_BUILDAHEAD_COLUMN,SS_SHIPMENT_BUILDAHEAD_1W_COLUMN,
                        SS_SHIPMENT_BUILDAHEAD_2W_COLUMN,SS_SHIPMENT_BUILDAHEAD_3W_COLUMN,SS_ITEM_BOD_LT_COLUMN]

    # 결측 데이타 채우기 nan 값 0 처리
    for col in clean_column_sum:
        df_out_SS_Monitor_SUM[col] = df_out_SS_Monitor_SUM[col].fillna(0)

    for col in clean_column_row:
        df_out_SS_Monitor_ROW[col] = df_out_SS_Monitor_ROW[col].fillna(0)

    # 전체가 0인 데이타 삭제하기
    #temp_pk_key = [VERSION_NAME_COLUMN,SUB_LOCATION_COLUMN,SALES_DOMAIN_AP2_COLUMN,ITEM_COLUMN,TIME_WEEK_COLUMN]
    #df_out_SS_Monitor_SUM = pd.merge(df_out_SS_Monitor_SUM,df_out_SS_Monitor_ROW, on=temp_pk_key, how="inner" )

    #print_df(df_out_SS_Monitor_ROW, "df_out_SS_Monitor_ROW")
    step('=====> STEP5-2 SS Monitor SUM Group-By')
    agg_dict_sum = {col: 'sum' for col in clean_column_sum}
    df_out_SS_Monitor_SUM = df_out_SS_Monitor_SUM.groupby(groupby_columns, sort=False).agg(agg_dict_sum,
                                                                                     skipna=True).reset_index()
    step('=====> STEP5-3 SS Monitor ROW Group-By')
    agg_dict_row = {col: 'sum' for col in clean_column_row}
    df_out_SS_Monitor_ROW = df_out_SS_Monitor_ROW.groupby(groupby_columns, sort=False).agg(agg_dict_row,
                                                                                     skipna=True).reset_index()

    df_out_SS_Monitor_SUM = dataframe_cleaning(df_out_SS_Monitor_SUM,clean_column_sum)
    df_out_SS_Monitor_ROW = dataframe_cleaning(df_out_SS_Monitor_ROW,clean_column_row)
    #print_df(df_out_SS_Monitor_ROW, "df_out_SS_Monitor_ROW")
    #print_df(df_out_SS_Monitor_SUM, "df_out_SS_Monitor_SUM")
    step('=====> STEP5 Dataframe_cleaning End')


    ################################################################################################################
    # Step Local 인 경우 최종 Output 파일을 Local에 저장함.
    ################################################################################################################
    if is_local:
        save_csv_file(df_out_SS_Monitor_SUM, "Fact.df_out_SS_Monitor_SUM")
        save_csv_file(df_out_SS_Monitor_ROW, "Fact.df_out_SS_Monitor_ROW")
        step('=====> STEP6 Local Save End')

    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    step(f'=====> current: {format_size(current)}, '
        f'peak: {format_size(peak)}, '
        f'execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    tracemalloc.stop()
except CustomException as e:
    step(f'=====> CustomException : {e}')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out = pd.DataFrame([], columns=[])
finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    logger.Finish()
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
