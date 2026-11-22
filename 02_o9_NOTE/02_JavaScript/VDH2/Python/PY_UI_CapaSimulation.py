"""
* 프로그램명
    - PY_UI_CapaSimulation

* 내용
    - Location, Line, Week별 Capa와 SOP 계산.

* 변경이력
    - 2025.12.03 / 김신 / Create
    - 2026.01.20 / 김신 / 수정 4개 Meausre 추가
      - Measure.[Capa Simul_Base Capa Sec]
      - Measure.[Capa Simul_OT Sat Sec]
      - Measure.[Capa Simul_Capa Sec Total]
      - Measure.[Capa Simul_2nd Shift Sec]

* Input
    - df_in_LineModelList
      Select ([Location].[Location] * &MDMHorizon * [Line].[Line] ) on row,
             ({Measure.[Line Model List_Comsume Capa], Measure.[Line Model List_Qty]}) on column
       where {[Version].[Version Name]};
    - df_in_WorkHrsAnnual
      Select ([Location].[Location] ) on row,
             ({Measure.[Work Hrs Annual_Total Work Mins Per Day w/ Off Time], Measure.[Work Hrs Annual_Work Mins Ratio], Measure.[Work Hrs Annual_2nd Shift Work Mins Per Day]}) on column
       where {[Version].[Version Name]};
    - df_in_WorkCalAnnual
     Select ([Location].[Location] * &MDMHorizon ) on row,
            ({Measure.[Work Cal Annual_Week Work Days]}) on column
      where {[Version].[Version Name]};
    - df_in_WorkCalLine
     Select ([Location].[Location] * &MDMHorizon * [Line].[Line] ) on row,
            ({Measure.[Work Cal Line_Time]}) on column
      where {[Version].[Version Name]};
    - df_in_SOPQty
     Select (FROM.[Time].[Week] * FROM.[Item].[Item Stage].[SET].relatedmembers([Item]) * FROM.[Location].[Location Type].[MF].relatedmembers([Location]) * FROM.[Activity1].[Activity Type1].[Manufacturing].relatedmembers([Activity1]) * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * FROM.[Documents].[OrderlineID] ) on row,
            ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged]}) on column
      where {RelationshipType.[SOP Bottom Up Pegging Output Graph], Version.[Version Name]};
    - df_in_Cons
     Select ([Location].[Location] * &MDMHorizon * [Activity1].[Activity1] * [Resource].[Resource].filter(#.Name startswith "MLC") * [Documents].[OrderlineID] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,
            ({Measure.[W Capacity Consumption Quantity Plan Output]}) on column
      where {[Version].[Version Name]};
    - df_in_LineEff
      Select ( [Location].[Location] * [Line].[Line] ) on row,
             ({Measure.[Line Eff Sub_IsAuto], Measure.[Line Eff Sub_IsValid]}) on column
       where { [Version].[Version Name]};
      ※ 파이선 플러그인 호출시, paramOutVersion으로 Call
   - df_in_LineGrpMap
     Select ( [Location].[Location] * [Group].[Group ID] * [Line].[Line] ) on row,
            ({ Measure.[Line Grp Map_Flag] }) on column
      where {[Version].[Version Name]};
      ※ 파이선 플러그인 호출시, paramOutVersion으로 Call
* Output Table
    - df_out_Capa_Simul
      Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Line].[Line]) on row,
             ({Measure.[Capa Simul_SOP], Measure.[Capa Simul_Capa Sec Total Org], Measure.[Capa Simul_Capa Sec Total], Measure.[Capa Simul_Base Capa Sec], Measure.[Capa Simul_OT Sat Sec], Measure.[Capa Simul_2nd Shift Sec], Measure.[Capa Simul_SOP Sec Total], Measure.[Capa Simul_SOP Pcs Total], Measure.[Capa Simul_Working Days], Measure.[Capa Simul_Setup Line], Measure.[Capa Simul_Open Line], Measure.[Capa Simul_Base Capa Mins],  Measure.[Capa Simul_OT Mins], Measure.[Capa Simul_Sat Mins], Measure.[Capa Simul_2nd Shift Mins], Measure.[Capa Simul_2nd Shift Eff]}) on column;
* Execution
    EXEC plugin instance [PY_UI_CapaSimulation]
    for measures {[Capa Simul_SOP]}
    using scope ([Version].[Version Name].filter(#.Name == "{{fb_Version}}"))
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "{{fb_Version}}"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

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
str_instance = 'PY_UI_CapaSimulation'
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

def vd_log_end() -> tuple:
    """
    로그 처리를 종료하고 로그 데이터프레임들을 반환하는 공통 함수

    Returns:
        tuple: (df_out_log, df_out_logDetail) 형태의 튜플
    """
    try:
        # 로그 종료 처리
        vdCommon.gfn_pyLog_end()

        # 로그 데이터프레임 가져오기
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()

        return df_out_log, df_out_logDetail

    except Exception as e:
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


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
        # 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_LineModelList = read_csv_file("df_in_LineModelList")
            df_in_WorkHrsAnnual = read_csv_file("df_in_WorkHrsAnnual")
            df_in_WorkCalAnnual = read_csv_file("df_in_WorkCalAnnual")
            df_in_WorkCalLine = read_csv_file("df_in_WorkCalLine")
            df_in_SOPQty = read_csv_file("df_in_SOPQty")
            df_in_Cons = read_csv_file("df_in_Cons")
            df_in_LineEff = read_csv_file("df_in_LineEff")
            df_in_LineGrpMap = read_csv_file("df_in_LineGrpMap")

        print_df(df_in_LineModelList, 'STEP 1 - Input table load .... df_in_LineModelList')
        print_df(df_in_WorkHrsAnnual, 'STEP 1 - Input table load .... df_in_WorkHrsAnnual')
        print_df(df_in_WorkCalAnnual, 'STEP 1 - Input table load .... df_in_WorkCalAnnual')
        print_df(df_in_WorkCalLine, 'STEP 1 - Input table load .... df_in_WorkCalLine')
        print_df(df_in_SOPQty, 'STEP 1 - Input table load .... df_in_SOPQty')
        print_df(df_in_Cons, 'STEP 1 - Input table load .... df_in_Cons')
        print_df(df_in_LineEff, 'STEP 1 - Input table load .... df_in_LineEff')
        print_df(df_in_LineGrpMap, 'STEP 1 - Input table load .... df_in_LineGrpMap')

        step('=====> 전처리 End')

        ################################################################################################################
        # DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        LINE_COLUMN = 'Line.[Line]'
        LINE_MODEL_LIST_COMSUME_CAPA_COLUMN = 'Line Model List_Comsume Capa'
        LINE_MODEL_LIST_QTY_COLUMN = 'Line Model List_Qty'
        WORK_HRS_ANNUAL_TOTAL_WORK_MINS_PER_DAY_W_OFF_TIME_COLUMN = 'Work Hrs Annual_Total Work Mins Per Day w/ Off Time'
        WORK_HRS_ANNUAL_WORK_MINS_RATIO_COLUMN = 'Work Hrs Annual_Work Mins Ratio'
        WORK_HRS_ANNUAL_2ND_SHIFT_WORK_MINS_PER_DAY_COLUMN = 'Work Hrs Annual_2nd Shift Work Mins Per Day'
        WORK_CAL_ANNUAL_WEEK_WORK_DAYS_COLUMN = 'Work Cal Annual_Week Work Days'
        WORK_CAL_LINE_TIME_COLUMN = 'Work Cal Line_Time'
        FROM_TIME_WEEK_COLUMN = 'from.[Time].[Week]'
        FROM_ITEM_COLUMN = 'from.[Item].[Item]'
        FROM_LOCATION_COLUMN = 'from.[Location].[Location]'
        FROM_ACTIVITY1_COLUMN = 'from.[Activity1].[Activity1]'
        FROM_ACTIVITY2_COLUMN = 'from.[Activity2].[Activity2]'
        FROM_ACTIVITY3_COLUMN = 'from.[Activity3].[Activity3]'
        FROM_DOCUMENTS_ORDERLINEID_COLUMN = 'from.[Documents].[OrderlineID]'
        SOP_BOTTOM_UP_PEGGING_OUTPUT_GRAPH_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]'
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        RESOURCE_COLUMN = 'Resource.[Resource]'
        DOCUMENTS_ORDERLINEID_COLUMN = 'Documents.[OrderlineID]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
        W_CAPACITY_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN = 'W Capacity Consumption Quantity Plan Output'
        CATEGORY_COLUMN = '[Category].[Category]'
        LINE_EFF_SUB_ISAUTO_COLUMN = 'Line Eff Sub_IsAuto'
        LINE_EFF_SUB_ISVALID_COLUMN = 'Line Eff Sub_IsValid'
        GROUP_ID_COLUMN = 'Group.[Group ID]'

        step('=====> Column 변수 처리 End')

        ################################################################################################################
        # Step 1
        # df_in_LineModelList의 칼럼이름을 다음과 같이 수정한다.
        #    [Line Model List_Comsume Capa] → [Capa Simul_SOP Sec Total]
        #    [Line Model List_Qty] → [Capa Simul_SOP Pcs Total]
        # df_in_LineModelList를 기준으로 Location에 따라 df_in_WorkHrsAnnual을 Merge한다.
        # df_in_LineModelList를 기준으로 Location, Week에 따라 df_in_WorkCalAnnual을 Merge한다.
        ################################################################################################################
        step('=====> STEP1 Start : df_in_LineModelList 사전처리')
        df_LineModelList_Work = df_in_LineModelList.copy()
        df_WorkCalAnnual_Work = df_in_WorkCalAnnual.copy()

        df_LineModelList_Work[TIME_WEEK_COLUMN] = df_LineModelList_Work[TIME_WEEK_COLUMN].astype(str)
        df_WorkCalAnnual_Work[TIME_WEEK_COLUMN] = df_WorkCalAnnual_Work[TIME_WEEK_COLUMN].astype(str)

        df_LineModelList_Work.rename(columns={
            'Line Model List_Comsume Capa': 'Capa Simul_SOP Sec Total',
            'Line Model List_Qty': 'Capa Simul_SOP Pcs Total'
        }, inplace=True)

        df_LineModelList_Work = df_LineModelList_Work.merge(df_in_WorkHrsAnnual, how='left',
                                                            on=[LOCATION_COLUMN])

        df_LineModelList_Work = df_LineModelList_Work.merge(df_WorkCalAnnual_Work, how='left',
                                                            on=[LOCATION_COLUMN, TIME_WEEK_COLUMN])

        print_df(df_LineModelList_Work, 'df_LineModelList_Work')
        step('=====> STEP1 End')
        ################################################################################################################
        # Step 2
        # df_in_LineModelList에서 Location, Week, Line별 [Capa Simul_Base Capa Sec]을 다음과 같이 계산한다.
        # [Capa Simul_Base Capa Mins] = [Work Hrs Annual_Total Work Mins Per Day w/ Off Time] * [Work Cal Annual_Week Work Days]
        # [Capa Simul_Base Capa Sec] = [Capa Simul_Base Capa Mins] * [Capa Simul_Open Line] * 60
        # [Capa Simul_2nd Shift Mins] = [Work Hrs Annual_2nd Shift Work Mins Per Day] * [Work Hrs Annual_2nd Shift Work Mins Per Day]
        # [Capa Simul_2nd Shift Sec] = [Capa Simul_2nd Shift Mins] * Coalesce ([Work Hrs Annual_Work Mins Ratio Column], 1) * 60
        # [Capa Simul_Working Days] = [Work Cal Annual_Week Work Days]
        ################################################################################################################
        step(
            '=====> STEP 2(Start) : df_in_LineModelList Location, Week, Line별 [Capa Simul_Base Capa Sec]을 다음과 같이 계산한다.')

        df_LineModelList_Work['Capa Simul_Base Capa Mins'] = df_LineModelList_Work[WORK_HRS_ANNUAL_TOTAL_WORK_MINS_PER_DAY_W_OFF_TIME_COLUMN] * df_LineModelList_Work[WORK_CAL_ANNUAL_WEEK_WORK_DAYS_COLUMN]

        df_LineModelList_Work = df_LineModelList_Work.merge(df_in_LineEff, how='left', on=[LOCATION_COLUMN, LINE_COLUMN])
        df_LineModelList_Work['Capa Simul_Base Capa Sec'] = np.where (df_LineModelList_Work[LINE_EFF_SUB_ISVALID_COLUMN] == 'Y', df_LineModelList_Work['Capa Simul_Base Capa Mins'] * 60, 0)
        df_LineModelList_Work.drop(columns=[
            LINE_EFF_SUB_ISVALID_COLUMN, LINE_EFF_SUB_ISAUTO_COLUMN
        ], inplace=True)

        df_LineModelList_Work[WORK_HRS_ANNUAL_WORK_MINS_RATIO_COLUMN] = df_LineModelList_Work[WORK_HRS_ANNUAL_WORK_MINS_RATIO_COLUMN].fillna(1)
        df_LineModelList_Work['Capa Simul_2nd Shift Mins'] = df_LineModelList_Work[WORK_HRS_ANNUAL_2ND_SHIFT_WORK_MINS_PER_DAY_COLUMN].fillna(0) * df_LineModelList_Work[WORK_CAL_ANNUAL_WEEK_WORK_DAYS_COLUMN]
        df_LineModelList_Work['Capa Simul_2nd Shift Sec'] = df_LineModelList_Work['Capa Simul_2nd Shift Mins'] * df_LineModelList_Work[WORK_HRS_ANNUAL_WORK_MINS_RATIO_COLUMN] * 60

        df_LineModelList_Work['Capa Simul_Working Days'] = df_LineModelList_Work[WORK_CAL_ANNUAL_WEEK_WORK_DAYS_COLUMN]

        step('=====> STEP2 End')
        ################################################################################################################
        # Step 3
        # df_in_LineModelList를 기준으로 Location, Week, Line에 따라 df_in_WorkCalLine을 Merge한다.
        # df_in_LineModelLIst에서 Location, Week, Line별 [Capa Simul_OT Sat Sec]을 다음과 같이 계산한다.
        # [Capa Simul_OT Sat Sec] = [Work Cal Line_Time] * 3600
        ################################################################################################################
        step('=====> STEP 3(Start) : df_in_LineModelList를 기준으로 Location, Week, Line에 별 [Capa Simul_OT Sat Sec] 계산한다.')
        df_WorkCalLine_Work = df_in_WorkCalLine.copy()
        df_WorkCalLine_Work[TIME_WEEK_COLUMN] = df_WorkCalLine_Work[TIME_WEEK_COLUMN].astype(str)

        df_LineModelList_Work = df_LineModelList_Work.merge(df_WorkCalLine_Work, how='left',
                                                            on=[LOCATION_COLUMN, TIME_WEEK_COLUMN, LINE_COLUMN])

        df_LineModelList_Work['Capa Simul_OT Sat Sec'] = df_LineModelList_Work[WORK_CAL_LINE_TIME_COLUMN] * 3600

        print_df(df_LineModelList_Work, 'df_LineModelList_Work')
        step('=====> STEP3 End')
        ################################################################################################################
        # Step 4
        # df_in_LineModelList에서 Location, Week, Line별[Capa Simul_Capa Sec Total], [Capa Simul_Capa Sec Total Org] 을
        # 다음과 같이 계산한다.
        #    [Capa Simul_Capa Sec Total] = [Capa Simul_Base Capa Sec] + [Capa Simul_OT Sat Sec] + [Capa Simul_2nd Shift Sec]
        #    [Capa Simul_Capa Sec Total Org] = [Capa Simul_Base Capa Sec] + [Capa Simul_OT Sat Sec] + [Capa Simul_2nd Shift Sec]
        ################################################################################################################
        step('=====> STEP4(Start) : =====> STEP4(Start) : df_in_LineModelList에서 Location, Week, Line별 '
             '[Capa Simul_Capa Sec Total], [Capa Simul_Capa Sec Total Org] 계산한다.')

        df_LineModelList_Work['Capa Simul_Capa Sec Total'] = df_LineModelList_Work['Capa Simul_Base Capa Sec'] + df_LineModelList_Work['Capa Simul_OT Sat Sec'] + df_LineModelList_Work['Capa Simul_2nd Shift Sec']
        df_LineModelList_Work['Capa Simul_Capa Sec Total Org'] = df_LineModelList_Work['Capa Simul_Capa Sec Total']

        print_df(df_LineModelList_Work, 'df_LineModelList_Work')
        step('=====> STEP4 End')
        ################################################################################################################
        # Step 5
        # df_in_Cons의 Resource 값에서 '_'와 '@' 사이에 있는 값만을 발췌한다.
        # df_in_Cons의 Resource 칼럼 이름을 [Line].[Line]으로 수정한다.
        ################################################################################################################
        step('=====> STEP5(Start) : df_in_Cons의 Resource 값에서 _와 @ 사이에 있는 값만을 발췌 해 컬럼이름 수정')
        df_Cons_Work = df_in_Cons.copy()

        df_Cons_Work[RESOURCE_COLUMN] = df_Cons_Work[RESOURCE_COLUMN].str.extract(r'_([^@]+)@')

        df_Cons_Work.rename(columns={
            RESOURCE_COLUMN: LINE_COLUMN
        }, inplace=True)

        print_df(df_Cons_Work, 'df_Cons_Work')
        step('=====> STEP5 End')
        ################################################################################################################
        # Step 6
        # df_in_SOPQty를 기준으로 Location, Week, Item, OrderlineID에 따라 df_in_Cons의 [Line].[Line]를 Merge한다.
        # df_in_SOPQty의 칼럼 Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged]의
        #     칼럼이름을 [Capa Simul_SOP]로 수정한다.
        ################################################################################################################
        step(
            '=====> STEP6(Start) : f_in_SOPQty를 기준으로 Location, Week, Item, OrderlineID에 따라 df_in_Cons의 [Line].[Line]를 Merge')
        df_SOPQty_Work = df_in_SOPQty.copy()

        df_Cons_Work[TIME_WEEK_COLUMN] = df_Cons_Work[TIME_WEEK_COLUMN].astype(str)
        df_SOPQty_Work[FROM_TIME_WEEK_COLUMN] = df_SOPQty_Work[FROM_TIME_WEEK_COLUMN].astype(str)

        df_SOPQty_Work = df_SOPQty_Work.merge(df_Cons_Work[[LOCATION_COLUMN, TIME_WEEK_COLUMN, ACTIVITY3_COLUMN,
                                                            DOCUMENTS_ORDERLINEID_COLUMN, LINE_COLUMN]],
                                              how='left',
                                              left_on=[FROM_LOCATION_COLUMN, FROM_TIME_WEEK_COLUMN, FROM_ITEM_COLUMN,
                                                       FROM_DOCUMENTS_ORDERLINEID_COLUMN],
                                              right_on=[LOCATION_COLUMN, TIME_WEEK_COLUMN, ACTIVITY3_COLUMN,
                                                        DOCUMENTS_ORDERLINEID_COLUMN])

        df_SOPQty_Work.rename(columns={
            SOP_BOTTOM_UP_PEGGING_OUTPUT_GRAPH_COLUMN: 'Capa Simul_SOP'
        }, inplace=True)

        print_df(df_SOPQty_Work, 'df_SOPQty_Work')
        step('=====> STEP6 End')
        ################################################################################################################
        # Step 7
        # df_in_SOPQty를 Location, Week, Line에 따라 [Capa Simul_SOP]을 Sum Aggregation을 한다.
        ################################################################################################################
        step('=====> STEP7(Start) : df_in_SOPQty를 Location, Week, Line에 따라 [Capa Simul_SOP]을 Sum Aggregation을 한다.')

        df_SOPQty_Work = df_SOPQty_Work.groupby([LOCATION_COLUMN, TIME_WEEK_COLUMN, LINE_COLUMN],
                                                as_index=False).agg({'Capa Simul_SOP': "sum"},skipna=True).copy()

        print_df(df_SOPQty_Work, 'df_SOPQty_Work')
        step('=====> STEP7 End')
        ################################################################################################################
        # Step 8
        # df_in_SOPQty를 기준으로 Location, Week, Line에 따라 df_in_LineModelList의 [Capa Simul_SOP Sec Total], [Capa Simul_SOP Pcs Total],
        #     [Capa Simul_Base Capa Sec], [Capa Simul_OT Sat Sec], [Capa Simul_Capa Sec Total], [Capa Simul_Capa Sec Total Org]을 Merge한다.
        ################################################################################################################
        step('=====> STEP8(Start) : df_SOPQty_Work와  df_LineModelList_Work를 Merge한다.')

        df_SOPQty_Work = df_SOPQty_Work.merge(df_LineModelList_Work, how='left',
                                              on=[LOCATION_COLUMN, TIME_WEEK_COLUMN, LINE_COLUMN])

        df_SOPQty_Work.insert(0, VERSION_NAME_COLUMN, PARAM_OUTVERSION_VALUE)

        print_df(df_SOPQty_Work, 'df_SOPQty_Work')
        step('=====> STEP8 End')
        ################################################################################################################
        # Step 9
        # df_in_SOPQty를 기준으로 Location, Line에 따라 df_in_LineEff의[LineEffSub_IsAuto]를 Merge한다.
        # df_in_SOPQty를 기준으로 Location, Line에 따라 df_in_LineGrpMap의[Group].[GroupID]를 Merge한다.
        # [Line Eff Sub_IsAuto] == "N" 이면 "Normal", [Line Eff Sub_IsAuto] <> "N" 이면 "Auto", Null이면 Category = Auto로
        #    값을 갖는 필드[Category].[Category] 추가한다.
        # 필드명을 다음과 같이 수정한다.
        #    FROM.[Time].[Week]  →  [Time].[Week]
        #    FROM.[Location].[Location] → [Location].[Location]
        ################################################################################################################
        step('=====> STEP9(Start) : [Category].[Category],[Group].[GroupID] 추가한다.')

        df_SOPQty_Work = df_SOPQty_Work.merge(df_in_LineEff, how='left',
                                              on=[LOCATION_COLUMN, LINE_COLUMN])

        df_SOPQty_Work = df_SOPQty_Work.merge(df_in_LineGrpMap, how='left',
                                              on=[LOCATION_COLUMN, LINE_COLUMN])

        df_SOPQty_Work[CATEGORY_COLUMN] = np.where(df_SOPQty_Work[LINE_EFF_SUB_ISAUTO_COLUMN].isna(),'Auto',
                                          np.where(df_SOPQty_Work[LINE_EFF_SUB_ISAUTO_COLUMN] == 'N', 'Normal','Auto'))

        df_SOPQty_Work['Capa Simul_Setup Line'] = np.where(df_SOPQty_Work[LINE_EFF_SUB_ISVALID_COLUMN] == 'Y', 1, 0)
        df_SOPQty_Work['Capa Simul_Open Line'] = np.where(df_SOPQty_Work[LINE_EFF_SUB_ISVALID_COLUMN] == 'Y', 1, 0)
        df_SOPQty_Work['Capa Simul_OT Mins'] = 0
        df_SOPQty_Work['Capa Simul_Sat Mins'] = 0
        df_SOPQty_Work['Capa Simul_2nd Shift Eff'] = 1

        print_df(df_SOPQty_Work, 'df_SOPQty_Work')
        step('=====> STEP9 End')
        ################################################################################################################
        # STEP 10 : output table create
        ################################################################################################################
        step('=====> STEP10 : Final output table create')
        df_SOPQty_Work[TIME_WEEK_COLUMN] = df_SOPQty_Work[TIME_WEEK_COLUMN].astype('int64')

        df_out_Capa_Simul = df_SOPQty_Work[
            [VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, GROUP_ID_COLUMN, CATEGORY_COLUMN, LINE_COLUMN,
             'Capa Simul_SOP', 'Capa Simul_Capa Sec Total Org', 'Capa Simul_Capa Sec Total', 'Capa Simul_Base Capa Sec',
             'Capa Simul_OT Sat Sec', 'Capa Simul_2nd Shift Sec', 'Capa Simul_SOP Sec Total', 'Capa Simul_SOP Pcs Total',
             'Capa Simul_Working Days', 'Capa Simul_Setup Line', 'Capa Simul_Open Line', 'Capa Simul_Base Capa Mins',
             'Capa Simul_OT Mins', 'Capa Simul_Sat Mins', 'Capa Simul_2nd Shift Mins', 'Capa Simul_2nd Shift Eff']]

        if is_local:
            step('=====> Output csv create')
            save_csv_file(df_out_Capa_Simul, 'df_out_Capa_Simul')
        print_df(df_out_Capa_Simul, 'df_out_Capa_Simul', True)
        step('=====> STEP10 End')
        step('==============================================')
        step('==============================================')
        step('==============================================')

    except Exception as e:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        df_out_Capa_Simul = pd.DataFrame([], columns=[])

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()