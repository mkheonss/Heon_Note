

"""

* 프로그램명
    - PY_UI_POProposalUpdate

* 내용
     - UI화면에서 처리하는 로직 생성(CurrentWeek 포함 3주간의 데이터만 사용)



* 변경이력
- 2025.01.14 / de0413.shin (신동언) / Create
- 2025-08-27 / ybest7.park (박병훈) / 수정
    - mg 명 변경 및 로직 수정
- 2025-09-05 / ybest7.park (박병훈) / 수정
    - 기존 Panel PO Proposal_Status 의  INI 값의 기존 POP ID 값을 업데이트 시 사용

* Input
- df_in_PanelPOProposal  = pd.read_csv('df_in_PanelPOProposal.csv')

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.


* Input Table
   - df_in_PanelPOProposal = Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [PO Proposal].[POP ID] ) on row, ({Measure.[Panel PO Proposal_ERP Vendor],Measure.[Panel PO Proposal_Incoterms1],Measure.[Panel PO Proposal_Incoterms2], Measure.[Dummy]}) on column  where{~isnull(Measure.[Panel PO Proposal_Incoterms1]) || ~isnull(Measure.[Panel PO Proposal_Incoterms2])};
   - df_in_AllocPur = Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(3).Key) * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Alloc Pur_ETD Plan], Measure.[Dummy]}) on column where{~isnull(Measure.[Alloc Pur_ETD Plan])};
   - df_in_ProposalStatus =  Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [PO Proposal].[POP ID]  ) on row,({Measure.[Panel PO Proposal_Status], Measure.[Dummy]}) on column where {Measure.[Panel PO Proposal_Status]=="INI"};
* Output Table
    - df_out_PanelPOProposal = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [PO Proposal].[POP ID]  ) on row,({Measure.[Panel PO Proposal_Status], Measure.[Panel PO Proposal_ETD QTY], Measure.[Panel PO Proposal_ERP Vendor], Measure.[Panel PO Proposal_Incoterms1], Measure.[Panel PO Proposal_Incoterms2]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_POProposalUpdate] for Measures {[Panel PO Proposal_POP Status]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight") , ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};



실행 전 프로시져를 통해 MF Site 삭제  필요

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

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_POProposalUpdate'
is_local = com.gfn_get_isLocal()
paramOutVersion = "CWV_MP"

COMMON_SOURCE_VERSION = com.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level
log_level_info = LOG_LEVEL.info()
log_level_debug = LOG_LEVEL.debug()
Logger.debug(f'[START] {str_instance}')
Logger.Start()

########################################################################################################################
# logic start
########################################################################################################################

class CustomException(Exception):
    pass

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

def calculate_mode(series):
    modes = series.mode()
    return modes.iloc[0] if not modes.empty else None


Logger.debug(f'[START] {str_instance}')
Logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0,'===================== plugin Execution Start =====================')
tracemalloc.start()

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
    vdCommon.gfn_stepLog(' 100 =====> STEP 1(Start) : Input Date Frame Read')
    # # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_AllocPurETDPlan = read_csv_file('df_in_AllocPurETDPlan')
        df_in_PanelPOProposal = read_csv_file('df_in_PanelPOProposal')
        df_in_ProposalStatus = read_csv_file('df_in_ProposalStatus')


    print_df(df_in_AllocPurETDPlan, 'df_in_AllocPurETDPlan',True)
    print_df(df_in_PanelPOProposal, 'df_in_PanelPOProposal',True)
    print_df(df_in_ProposalStatus, 'df_in_ProposalStatus', True)


    vdCommon.gfn_stepLog(' 100 =====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('200 =====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_Name_COLUMN = 'Version.[Version Name]'
    Location_COLUMN = 'Location.[Location]'
    Item_Material_COLUMN = 'Item Material.[Item Material]'
    SUB_Location_COLUMN = 'Sub Location.[Sub Location]'
    Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'

    PO_Proposal_COLUMN = 'PO Proposal.[POP ID]'

    Alloc_Pur_ETD_Plan = 'Alloc Pur_ETD Plan'
    Panel_PO_Proposal_ERP_Vendor = 'Panel PO Proposal_ERP Vendor'
    Panel_PO_Proposal_Incoterms1 = 'Panel PO Proposal_Incoterms1'
    Panel_PO_Proposal_Incoterms2 = 'Panel PO Proposal_Incoterms2'

    Panel_PO_Proposal_ETD_QTY = 'Panel PO Proposal_ETD QTY'
    Panel_PO_Proposal_Status = 'Panel PO Proposal_Status'

    vdCommon.gfn_stepLog( '200 =====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3 (1) 프로그램 내 사용하는 변수 설정
    ################################################################################################################
    vdCommon.gfn_stepLog( '300 =====> STEP 3(Start) : Check memory usage & runtime')
    # Group by Columns 설정
    groupbycols = [Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, SUB_Location_COLUMN, Trans_Mode_COLUMN]
    # Panel PO Proposal_ETD QTY 를 구하기 위한 그룹바이
    df_in_AllocPurETDPlan_group = df_in_AllocPurETDPlan.groupby(groupbycols)[Alloc_Pur_ETD_Plan].sum().reset_index()

    print_df(df_in_AllocPurETDPlan_group , 'df_in_AllocPurETDPlan_group',True)

    vdCommon.gfn_stepLog('300 =====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 4. FCST 정리 및 진행
    ################################################################################################################
    vdCommon.gfn_stepLog( '400 =====> STEP 4(Start) : output data machining')

    # Panel PO Proposal_ETD QTY 을 위해 df_in_PanelPOProposal과 merge
    df_in_PanelPOProposal = df_in_PanelPOProposal.merge(df_in_AllocPurETDPlan_group, on=groupbycols, how='left')

    # PO_Proposal_COLUMN 와 Panel_PO_Proposal_ERP_Vendor 등의 최빈값 구하기
    df_in_PanelPOProposal = df_in_PanelPOProposal.groupby(groupbycols).agg(
        PO_Proposal_COLUMN=('PO Proposal.[POP ID]', 'max'),
        Panel_PO_Proposal_ERP_Vendor=('Panel PO Proposal_ERP Vendor', calculate_mode),
        Panel_PO_Proposal_Incoterms1=('Panel PO Proposal_Incoterms1', calculate_mode),
        Panel_PO_Proposal_Incoterms2=('Panel PO Proposal_Incoterms2', calculate_mode),
        Panel_PO_Proposal_ETD_QTY=('Alloc Pur_ETD Plan', 'max')
    ).reset_index()

    # 컬럼명 변경
    rename_cols = {
        'PO_Proposal_COLUMN': PO_Proposal_COLUMN, 'Panel_PO_Proposal_ERP_Vendor': Panel_PO_Proposal_ERP_Vendor,
        'Panel_PO_Proposal_Incoterms1': Panel_PO_Proposal_Incoterms1,
        'Panel_PO_Proposal_Incoterms2': Panel_PO_Proposal_Incoterms2,
        'Panel_PO_Proposal_ETD_QTY': Panel_PO_Proposal_ETD_QTY}

    df_in_PanelPOProposal.rename(columns=rename_cols, inplace=True)

    print_df(df_in_PanelPOProposal, 'df_in_PanelPOProposal 중간값 확인', True)

    ############################################# 2025-09-05 수정 #######################################################

    # df_in_ProposalStatus Dummy 삭제 및 중복 삭제
    df_in_ProposalStatus = df_in_ProposalStatus.drop(columns="Dummy").drop_duplicates()

    # 필터를 위한 Index columns 설정
    index_cols = groupbycols # 기존 Key 값 복사
    # index_cols = [Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, SUB_Location_COLUMN, Trans_Mode_COLUMN]
    # column 명 지정
    value_col = 'POID'

    # df_in_ProposalStatus 데이터의 PO_Proposal_COLUMN 값 시리즈로 변환
    POID = df_in_ProposalStatus.set_index(index_cols)[PO_Proposal_COLUMN]
    POID.name = value_col

    # df_in_PanelPOProposal 필터를 위한 Data merge
    df_in_PanelPOProposal = df_in_PanelPOProposal.join(POID, on=index_cols, how='left')
    # 데이터 전처리 전 데이터 타입 변경
    df_in_PanelPOProposal[PO_Proposal_COLUMN] = df_in_PanelPOProposal[PO_Proposal_COLUMN].astype('int64')
    df_in_PanelPOProposal['POID'] = df_in_PanelPOProposal['POID'].fillna(0).astype('int64')

    # PO_Proposal_COLUMN 데이터 처리 : 기존 데이터가 있으면 기존 데이터 아니면 그 후 데이터 처리
    df_in_PanelPOProposal[PO_Proposal_COLUMN] = np.where(
        df_in_PanelPOProposal['POID'] == 0, df_in_PanelPOProposal[PO_Proposal_COLUMN] + 1,
        df_in_PanelPOProposal['POID'])

    # PO_Proposal_COLUMN 데이터 형식 변경
    df_in_PanelPOProposal[PO_Proposal_COLUMN] = df_in_PanelPOProposal[PO_Proposal_COLUMN].astype(str).fillna('-')

    note(f"PO_Proposal_COLUMN unique: {len(df_in_PanelPOProposal[PO_Proposal_COLUMN].unique())} EA")
    #
    # # PO_Proposal_COLUMN 설정 추가 +1 및 값이 없는 경우 "-"로 채우기
    # df_in_PanelPOProposal[PO_Proposal_COLUMN] = np.where(df_in_PanelPOProposal[PO_Proposal_COLUMN].notnull(),
    #                                                      df_in_PanelPOProposal[PO_Proposal_COLUMN].astype("int64") + 1,
    #                                                      "-")

    ################################################### 2025-09-05 수정 완료 ############################################
    # Panel_PO_Proposal_Status 값 설정
    df_in_PanelPOProposal[Panel_PO_Proposal_Status] = "INI"

    # Panel_PO_Proposal_ETD_QTY null 인 경우 0으로 변경
    df_in_PanelPOProposal[Panel_PO_Proposal_ETD_QTY] = df_in_PanelPOProposal[Panel_PO_Proposal_ETD_QTY].fillna(0)

    # out put data 순서 지정
    output_cols = [Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, SUB_Location_COLUMN, Trans_Mode_COLUMN,
                   PO_Proposal_COLUMN, Panel_PO_Proposal_Status, Panel_PO_Proposal_ETD_QTY,
                   Panel_PO_Proposal_ERP_Vendor,
                   Panel_PO_Proposal_Incoterms1, Panel_PO_Proposal_Incoterms2]

    df_out_PanelPOProposal = df_in_PanelPOProposal[output_cols]

    print_df(df_out_PanelPOProposal, 'df_out_PanelPOProposal ', True)
    vdCommon.gfn_stepLog('400 =====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 5. (1) 최종 Out_Put Save
    ################################################################################################################
    vdCommon.gfn_stepLog('500 =====> STEP 5(Start) : output data machining')

    row_count, col_count = df_out_PanelPOProposal.shape
    note(f'=====> Final df_out_PanelPOProposal rows : {row_count} , Columns : {col_count}')

    # row_count, col_count = df_out_FCSTRTFHist.shape
    # note(f'=====> Final df_out_FCSTRTFHist rows : {row_count} , Columns : {col_count}')

    print_df(df_out_PanelPOProposal, 'df_out_PanelPOProposal 최종 ', True)

    if is_local:
        note(f'=====> Final output table create')
        save_csv_file(df_out_PanelPOProposal, 'df_out_PanelPOProposal _ 최종')
        # save_csv_file(df_out_FCSTRTFHist, 'df_out_FCSTRTFHist')

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg,p_log_level=LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_PanelPOProposal = pd.DataFrame([], columns=[])


else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(600, '===================== plugin Execution End =====================')

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