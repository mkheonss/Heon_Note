"""
* 프로그램명
    - PY_MG_Capacity_WorkCalendar

* 내용
    - 라인 Calendar, Simultaneous Association, FlexCapacity insert
    - MP Plan Batch Procedure에서 Call 하는 Program
    - Work Calendar UI 에서 Capa 계산을 통해 최종 라인 - Week별 Working Calendar가 집계됨.
    - 단, UI에서는 Capa(Simul) 계산을 위해 DataSet(사용자 Version)을 관리
    - 이에 DataSet 중 &DataSetMP 대상만 최종 엔진에 반영

* 변경이력
    - 2024.06.26 / 권태우 / Create
    - 2024.09.02 / 권태우 / Step3, Step4 추가

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_WorkingCalendarLine : Select (Version.[Version Name] * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Line].[Line] * &DataSetMP ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column.filter(Measure.[Work Cal Line_Time] > 0);
    - df_in_Lineutil    : Select (Version.[Version Name] * &PlanningHorizon  * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Line Eff W] }) on column;
    - df_in_ItemSiteAsn : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_Time        : Select ([Time].[Week] * [Time].[Day]) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};
    - df_in_BOMMaster   : Select (Version.[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column;
    - df_in_TactTime    : Select (Version.[Version Name]  * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Plan Flag], Measure.[Tact Time_Prty], Measure.[Tact Time_Time], Measure.[Tact Time_UOM], Measure.[Tact Time_Valid Asn]}) on column  where {  Measure.[Tact Time_Valid Asn] == true };
    - df_in_WorkType    : Select ( [Work Type].[Work Type] * [Work Type].[Work Type Abbr]  * [Work Type].[Work Type Layer]);
    - df_PlanStartEndWeek : Select (Version.[Version Name]) on row, ({Measure.[MP Plan End Week], Measure.[MP Plan Start Week]}) on column;

* Flow Summary
    - STEP1. Plan 대상 MF Site 대상으로 LINE Calendar 집계 ( Group by )
    - STEP2. STEP1  기준 Measure Insert

* 주요 Logic ( Data 처리 )
    - STEP1 : Plan 대상 MF Site 대상으로 LINE Calendar 집계 ( Group by )
    - STEP2 : STEP1  기준 Measure Insert
                Measure Group : 001.022W Solver Inputs Capacity
    - STEP3. Simultaneous Association Insert
    - STEP4. FlexCapacity insert
    
* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_LineWorkCalendar
    - df_out_SimultaneousAsn
    - df_out_FlexCapacity

* 데이타 초기화
    - DELETE DATA FOR MODEL [001.022W Solver Inputs Capacity] where {Version.[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [001.005W Solver Inputs Resource Group Consumption Association] where {Version.[Version Name].[CWV_MP]};
    - DELETE DATA FOR MODEL [001.48W LP Solver Flex Capacity Input] where {Version.[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_Capacity_WorkCalendar] for Measures {[W Resource Base Capacity]}
        using scope (&MPV * &PlanningHorizon * &MFLocation * &DataSetMP)
        using arguments {
            (ExecutionMode, "MediumWeight"),
            ("IncludeNullRows", "False"),
            (paramOutVersion , "CWV_MP"),
            (MaxSliceTableCells, 200000000), (MaxConcurrency, 1),
            ([Param.o9_sys_log_level], "DEBUG")
        };

* Output Query
    - df_out_LineWorkCalendar / Measure Group : 001.022W Solver Inputs Capacity
        Select ([Version].[Version Name].[CWV_MP] * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row,
            ({Measure.[W Flex Capacity Band1], Measure.[W Flex Capacity Band2], Measure.[W Resource Base Capacity] }) on column;

    - df_out_SimultaneousAsn / Measure Group : 001.005W Solver Inputs Resource Group Consumption Association
        Select ([Version].[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] * [Resource Group].[Resource Group] ) on row,
            ({Measure.[W Simultaneous Capacity Consumption Association]}) on column;

    - df_out_FlexCapacity / Measure Group : 001.48W LP Solver Flex Capacity Input
        Select ([Version].[Version Name] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [Time].[Week] * [Location].[Location] * [Resource].[Resource] ) on row,
            ({Measure.[W LP Flex Capacity]}) on column;

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
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_Capacity_WorkCalendar'
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
            df_in_WorkingCalendarLine = read_csv_file("df_in_WorkingCalendarLine")
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_Time = read_csv_file("df_in_Time")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_TactTime = read_csv_file("df_in_TactTime")
            df_in_WorkType = read_csv_file("df_in_WorkType")
            df_in_Lineutil = read_csv_file("df_in_Lineutil")
            df_PlanStartEndWeek = read_csv_file("df_PlanStartEndWeek")
    
    
        print_df(df_in_WorkingCalendarLine, 'input table load .... df_in_WorkingCalendarLine')
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_Time, 'input table load .... df_in_Time')
        print_df(df_in_BOMMaster, 'input table load .... df_in_BOMMaster')
        print_df(df_in_TactTime, 'input table load .... df_in_TactTime')
        print_df(df_in_WorkType, 'input table load .... df_in_WorkType')
        print_df(df_in_Lineutil, 'input table load .... df_in_Lineutil')
        print_df(df_PlanStartEndWeek, 'input table load .... df_PlanStartEndWeek')
    
    
        step('=====> STEP1 End')
        
        
    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2(Start) : DataFrame Column 변수 처리')
    
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'
        LINE_COLUMN = 'Line.[Line]'
        LINE_EFF_W_COLUMN = 'Line Eff W'
    
        ITEM_SITE_ASN_CUR_STATUS_COLUMN = 'Item Site Asn_Cur Status'
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'
        ITEM_SITE_ASN_ITEM_GRP_COLUMN = 'Item Site Asn_Item Grp'
        ITEM_SITE_ASN_SALES_PROD_ASN_COLUMN = 'Item Site Asn_Sales Prod Asn'
        ITEM_SITE_ASN_STAGE_COLUMN = 'Item Site Asn_Stage'
    
        WORK_TYPE_COLUMN = 'Work Type.[Work Type]'
        WORK_TYPE_ABBR_COLUMN = 'Work Type.[Work Type Abbr]'
        WORK_TYPE_LAYER_COLUMN = 'Work Type.[Work Type Layer]'
        DATA_SET_COLUMN = 'Data Set.[Data Set]'
        WORK_CAL_LINE_LOCK_FLAG_COLUMN = 'Work Cal Line_Lock Flag'
        WORK_CAL_LINE_TIME_COLUMN = 'Work Cal Line_Time'
    
        W_FLEX_CAPACITY_BAND1_COLUMN = 'W Flex Capacity Band1'
        W_FLEX_CAPACITY_BAND2_COLUMN = 'W Flex Capacity Band2'
        W_RESOURCE_BASE_CPACITY_COLUMN = 'W Resource Base Capacity'
    
        RESOURCE_COLUMN = 'Resource.[Resource]'
        RESOURCE_GROUP_COLUMN = '[Resource Group].[Resource Group]'
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
        GRAPHCUBEDIM_SEQUENCE_COLUMN = 'GraphCubeDim_Sequence.[GraphCubeAttr_Sequence]'
    
        TIME_DAY_COLUMN = 'Time.[Day]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAYKEY_COLUMN = 'Time.[DayKey]'
        TIME_WEEKKEY_COLUMN = 'Time.[WeekKey]'
        TIME_W_SOLVER_CURRENT_BUCKET_COLUMN = 'Time.[W Solver Current Bucket]'
        TIME_W_SOLVER_START_BUCKET_COLUMN = 'Time.[W Solver Start Bucket]'
        TIME_W_SOLVER_END_BUCKET_COLUMN = 'Time.[W Solver End Bucket]'
    
        BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'
        BOM_MASTER_PRIORITY_COLUMN = 'BOM Master_Priority'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'
    
        W_PRODUCTION_HOLIDAY_COLUMN = 'W Production Holiday'
        W_SIMULTANEOUS_CCA_COLUMN = 'W Simultaneous Capacity Consumption Association'
        W_LP_FLEX_CAPACITY_COLUMN = 'W LP Flex Capacity'
    
        MP_PLAN_END_WEEK_COLUMN = 'MP Plan End Week'
        MP_PLAN_START_WEEK_COLUMN = 'MP Plan Start Week'

        df_WorkCalendarSet_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN, TIME_WEEK_COLUMN, WORK_TYPE_COLUMN, LINE_COLUMN, WORK_CAL_LINE_TIME_COLUMN,
            W_FLEX_CAPACITY_BAND1_COLUMN, W_FLEX_CAPACITY_BAND2_COLUMN
        ]

        df_LineWorkCalendar_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, RESOURCE_COLUMN, LINE_COLUMN, W_RESOURCE_BASE_CPACITY_COLUMN, W_FLEX_CAPACITY_BAND1_COLUMN, W_FLEX_CAPACITY_BAND2_COLUMN
        ]

        df_SimultaneousAsn_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN, RESOURCE_COLUMN, RESOURCE_GROUP_COLUMN, W_SIMULTANEOUS_CCA_COLUMN
        ]

        df_FlexCapacity_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, RESOURCE_COLUMN, TIME_WEEK_COLUMN, LINE_COLUMN, GRAPHCUBEDIM_SEQUENCE_COLUMN, W_LP_FLEX_CAPACITY_COLUMN
        ]

        step('=====> STEP2 End')


    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # location 만 발췌, 중복값 삭제(Location Distinct) 및 미사용 컬럼 삭제 및 df_in_ItemSiteAsn remake
        drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [LOCATION_COLUMN]]
        df_ItemSiteAsn = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[LOCATION_COLUMN], keep='first')
    
        # week 만 발췌, 중복값 삭제(Week Distinct) 및 미사용 컬럼 삭제 및 df_in_Time remake
        drop_column = [col for col in list(df_in_Time.columns) if col not in [TIME_WEEK_COLUMN]]
        df_in_Time = df_in_Time.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[TIME_WEEK_COLUMN], keep='first')
    
    
        # ====================> STEP3 by 0 (Start) -> df_in_SETShipmentSETProd (SET Shipment / SET Prod)
        
        # 0.2 현재 week 가져오기
        mp_plan_start_week = get_first_value(df_PlanStartEndWeek, MP_PLAN_START_WEEK_COLUMN)
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')

        mp_plan_end_week = get_first_value(df_PlanStartEndWeek, MP_PLAN_END_WEEK_COLUMN)
        step(f'=====> mp_plan_end_week : {mp_plan_end_week}')
        
        # ====================> STEP3 by 0 (End)
    
    
        # ====================> STEP3 by 1 : Plan 대상 MF Site 대상으로 df_WorkCalendarSet 집계 ( Group by )
        
        # 1.1 df_week_calendar_line create
        df_week_calendar_line = pd.merge(df_in_WorkingCalendarLine, df_in_Time, on=TIME_WEEK_COLUMN, how='inner')
        print_df(df_week_calendar_line, 'STEP3 by 1.1 ____ df_week_calendar_line .... merge[df_in_WorkingCalendarLine, df_in_Time]')
    
        if not df_week_calendar_line.empty:
            # 1.2 df_in_WorkingCalendarLine 의 location 이 df_ItemSiteAsn 의 location 에 속한 행만 선택
            df_WorkCalendarSet = df_week_calendar_line[df_week_calendar_line[LOCATION_COLUMN].isin(df_ItemSiteAsn[LOCATION_COLUMN])]

            df_WorkCalendarSet = pd.merge(df_week_calendar_line, df_in_Lineutil, how='left', on=[LINE_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN])
            print_df(df_WorkCalendarSet, 'STEP3 by 1.1 ____ df_WorkCalendarSet .... merge[df_week_calendar_line, df_in_Lineutil]')

            df_WorkCalendarSet.rename(columns={VERSION_NAME_COLUMN+'_x': VERSION_NAME_COLUMN}, inplace=True)
    
            df_WorkCalendarSet[RESOURCE_COLUMN] = ('LR_' + df_WorkCalendarSet[LINE_COLUMN].fillna('') + '@' + df_WorkCalendarSet[LOCATION_COLUMN].fillna(''))
            df_WorkCalendarSet[W_FLEX_CAPACITY_BAND1_COLUMN] = 0
            df_WorkCalendarSet[W_FLEX_CAPACITY_BAND2_COLUMN] = 0
    
            df_WorkCalendarSet[LINE_EFF_W_COLUMN] = df_WorkCalendarSet[LINE_EFF_W_COLUMN].fillna(1)
            df_WorkCalendarSet[WORK_CAL_LINE_TIME_COLUMN] = (df_WorkCalendarSet[LINE_EFF_W_COLUMN] * df_WorkCalendarSet[WORK_CAL_LINE_TIME_COLUMN])
    
            df_WorkCalendarSet = df_WorkCalendarSet[df_WorkCalendarSet_columns]
            print_df(df_WorkCalendarSet, 'STEP3 by 1.1 ____ df_WorkCalendarSet .... final')
    
        else:
            df_WorkCalendarSet = pd.DataFrame(columns=df_WorkCalendarSet_columns)
    
    
    
    
        # ====================> STEP3 by 2 : df_WorkCalendarSet 를 기준으로 GROUP BY 하여 df_CalendarSet 구성
        
        # 2.1 df_WorkCalendarSet, df_in_WorkType join
        df_CalendarSetTemp = pd.merge(df_WorkCalendarSet, df_in_WorkType, on=WORK_TYPE_COLUMN, how='inner')
        print_df(df_CalendarSetTemp, 'STEP3 by 2.1 ____ df_CalendarSetTemp .... merge')
    
        if not df_CalendarSetTemp.empty:
            df_CalendarSet = df_CalendarSetTemp.groupby(
                [VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, RESOURCE_COLUMN, LINE_COLUMN]).agg(
                W_Resource_Base_Capacity=pd.NamedAgg(
                    column=WORK_CAL_LINE_TIME_COLUMN, aggfunc=lambda x: np.sum(x[df_CalendarSetTemp[WORK_TYPE_ABBR_COLUMN] == 'NRT'])
                ),
                W_Flex_Capacity_Band1=pd.NamedAgg(
                    column=WORK_CAL_LINE_TIME_COLUMN, aggfunc=lambda x: np.sum(x[df_CalendarSetTemp[WORK_TYPE_ABBR_COLUMN] == 'NOT'])
                ),
                W_Flex_Capacity_Band2=pd.NamedAgg(
                    column=WORK_CAL_LINE_TIME_COLUMN, aggfunc=lambda x: np.sum(x[df_CalendarSetTemp[WORK_TYPE_ABBR_COLUMN].isin(['TOT', 'SOT'])])
                )
            ).reset_index()
            print_df(df_CalendarSetTemp, 'STEP3 by 2.1 ____ df_CalendarSetTemp .... final')
    
        else:
            columns = [VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, RESOURCE_COLUMN, LINE_COLUMN,
                       'W_Resource_Base_Capacity', 'W_Flex_Capacity_Band1', 'W_Flex_Capacity_Band2']
            df_CalendarSet = pd.DataFrame(columns=columns)
    
    
    
    
        # ====================> STEP3 by 3 : df_SimultaneousAsn > Measure Insert, LINE Calendar도 Simultaneous 에 반영
        #                               df_CalendarSet  은 라인의 calendar이므로 item이 아닌 해당 라인에 대한 tact정보를 가지고 와서
        #                               대상 item을 가지고 bom이랑 매칭
        # 3.1         df_buf_SimultaneousAsn1 = pd.merge(df_CalendarSet, df_in_TactTime, how='inner', on=[VERSION_NAME_COLUMN, LINE_COLUMN, LOCATION_COLUMN]) create
        df_buf_SimultaneousAsn1 = pd.merge(df_CalendarSet, df_in_TactTime, how='inner', on=[VERSION_NAME_COLUMN, LINE_COLUMN, LOCATION_COLUMN])
        print_df(df_buf_SimultaneousAsn1, 'STEP3 by 3.1 ____ df_buf_SimultaneousAsn1 .... merge[df_CalendarSet, df_in_TactTime]')
    
        if not df_buf_SimultaneousAsn1.empty:
            # 3.2 df_buf_SimultaneousAsn2 create
            df_buf_SimultaneousAsn2 = pd.merge(df_buf_SimultaneousAsn1, df_in_BOMMaster, how='inner',
                                               left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN],
                                               right_on=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN, LOCATION_COLUMN])
            print_df(df_buf_SimultaneousAsn2, 'STEP3 by 3.2 ____ df_buf_SimultaneousAsn2 .... merge[df_buf_SimultaneousAsn1, df_in_BOMMaster]')
    
            df_SimultaneousAsn = pd.merge(df_buf_SimultaneousAsn2, df_in_ItemSiteAsn, how='inner', on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN])
    
            # 3.3 Resource 및 Activity 컬럼 make
            df_SimultaneousAsn[ACTIVITY2_COLUMN] = (
                    'RT_' + df_SimultaneousAsn[BOM_ID_COLUMN].fillna('') + '@' + df_SimultaneousAsn[LOCATION_COLUMN].fillna('')
            )
            df_SimultaneousAsn[RESOURCE_GROUP_COLUMN] = (
                    'RT_' + df_SimultaneousAsn[BOM_ID_COLUMN].fillna('') + '@' +
                    df_SimultaneousAsn[LOCATION_COLUMN].fillna('') + '_' +
                    df_SimultaneousAsn[LINE_COLUMN].fillna('')
            )
            df_SimultaneousAsn[W_SIMULTANEOUS_CCA_COLUMN] = 1
    
            # 3.4 컬럼명 변경
            df_SimultaneousAsn.rename(columns={
                BOM_ID_COLUMN: ACTIVITY1_COLUMN,
                ITEM_COLUMN: ACTIVITY3_COLUMN
            }, inplace=True)
    
            # 3.5 필요컬럼 발췌
            df_SimultaneousAsn = df_SimultaneousAsn[df_SimultaneousAsn_columns]
            print_df(df_SimultaneousAsn, 'STEP3 by 3.5 ____ df_SimultaneousAsn .... final')
    
        else:
            df_SimultaneousAsn = pd.DataFrame(columns=df_SimultaneousAsn_columns)
    
    
    
    
        # ====================> STEP3 by 4 : df_SimultaneousAsn > Measure Insert, LINE Calendar도 Simultaneous 에 반영
        # 4.1 df_FlexCapacity  Measure Insert
        df_buf_FlexCapacity = pd.merge(df_WorkCalendarSet, df_in_WorkType, on=WORK_TYPE_COLUMN, how='inner')
        print_df(df_buf_FlexCapacity, 'STEP3 by 4.1 ____ df_buf_FlexCapacity .... merge[df_WorkCalendarSet, df_in_WorkType]')
    
        df_FlexCapacity = df_buf_FlexCapacity[df_buf_FlexCapacity[WORK_TYPE_ABBR_COLUMN] == 'NRT'].copy()
    
        if not df_FlexCapacity.empty:
            # 4.2 컬럼명 변경
            df_FlexCapacity.rename(columns={
                WORK_CAL_LINE_TIME_COLUMN: GRAPHCUBEDIM_SEQUENCE_COLUMN,
                WORK_TYPE_LAYER_COLUMN: W_LP_FLEX_CAPACITY_COLUMN
            }, inplace=True)
    
            # 4.3 필요컬럼 발췌
            df_FlexCapacity = df_FlexCapacity[df_FlexCapacity_columns]
            print_df(df_FlexCapacity, 'STEP3 by 4.3 ____ df_FlexCapacity .... final')
    
        else:
            df_FlexCapacity = pd.DataFrame(columns=df_FlexCapacity_columns)
    
    
        step('=====> STEP3 End')
        
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        df_out_LineWorkCalendar = rename_and_delete_df(df_CalendarSet)
        df_out_SimultaneousAsn = rename_and_delete_df(df_SimultaneousAsn)
        df_out_FlexCapacity = rename_and_delete_df(df_FlexCapacity)
        
        df_out_LineWorkCalendar[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SimultaneousAsn[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_FlexCapacity[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_LineWorkCalendar, 'output table create .... df_out_LineWorkCalendar', True)
        print_df(df_out_SimultaneousAsn, 'output table create .... df_out_SimultaneousAsn', True)
        print_df(df_out_FlexCapacity, 'output table create .... df_out_FlexCapacity', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_LineWorkCalendar = pd.DataFrame(columns=df_LineWorkCalendar_columns)
        df_out_SimultaneousAsn = pd.DataFrame(columns=df_SimultaneousAsn_columns)
        df_out_FlexCapacity = pd.DataFrame(columns=df_FlexCapacity_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_LineWorkCalendar = pd.DataFrame(columns=df_LineWorkCalendar_columns)
        df_out_SimultaneousAsn = pd.DataFrame(columns=df_SimultaneousAsn_columns)
        df_out_FlexCapacity = pd.DataFrame(columns=df_FlexCapacity_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
