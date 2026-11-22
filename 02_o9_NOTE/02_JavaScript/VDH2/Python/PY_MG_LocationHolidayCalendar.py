"""
* 프로그램명
    - PY_MG_LocationHolidayCalendar

* 내용
    - [Basic Input] MP Engine 수행을 위한 Consumption and Production Holidays Data Input
    - MP Plan Batch Procedure에서 Call 하는 Program
    - 생산 법인 휴무일(라인 Calendar)를 기준으로 비근무일(Holidays) 정보를 Interface

* 변경이력
    - 2024.06.25 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_WorkingCalendarLine : Select (Version.[Version Name] * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Line].[Line] * [Data Set].[Data Set] ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column.filter(Measure.[Work Cal Line_Time] > 0);
    - df_in_Line        : Select ([Line].[Line] *[Line].[Line Type]) on row;
    - df_in_ItemSiteAsn : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_BOMMaster   : Select (Version.[Version Name] * [Activity3].[Activity3] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Location].[Location] * [Item].[Item] ) on row, ({ Measure.[W Material Production Association], Measure.[W Material Production Quantity Per]}) on column;
    - df_in_Time        : Select ([Time].[Week] * [Time].[Day]) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};

* Flow Summary
    - STEP1. Plan 대상 MF Site 대상으로 Week Set 구성
    - STEP2. STEP1 Set 중 실제 Calendar가 존재하지 않는 Routing Set  구성
    - STEP3. STEP2에서 구성된 Set을 대상으로 BOM 정보(Activity)를 참고하여 Output Measure에 넣을 레이아웃으로  Set 구성
    - STEP4. STEP3에서 구성된 Set를 대상으로 Production Holiday Measure 에 Insert

* 주요 Logic ( Data 처리 )
    - STEP1 : (Batch Procedure) 기존 Measure Group Delete
    - STEP2 : Production Capacity 중 Plan 대상 Site만 Filtering
                - df_in_WorkingCalendarLine  중 Plan 대상 Site ID로 Filtering 한  Set 구성
    - STEP3 : STEP2에서 구성된 Set을 대상으로 BOM 정보를 참고하여 Output Measure에 넣을 대상을 Filtering 한 Set 구성
                -  df_in_ProductionHolidays 중 Plan 대상 Site ID로 Filtering 한  Set 구성
                   아니고.. 없는 대상만 off로 넣을것
                   asn이 없어도 off로 넣을것

    - STEP4 : STEP3에서 구성된 Set를 대상으로 Production Holiday Measure 에 Insert
                - Measure Group : 001.012W Solver Inputs Location Holiday Calendar
                                  'True'가 Holiday란 의미임. SET3에 구성된 SET 대상을 Insert하면서, 아래 Measure는 True로 설정 / 'True' > W Production Holiday

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ProductionHolidays

* 데이타 초기화
    - DELETE DATA FOR MODEL [001.012W Solver Inputs Location Holiday Calendar] where {Version.[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_LocationHolidayCalendar] for Measures {[W Production Holiday]} using scope (&MPV * &DataSetMP *  &PlanningHorizon * &MFLocations) using arguments {(paramㅒutVersion , "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG") };

* Output Query
    - Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({ Measure.[W Production Holiday]}) on column;

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
str_instance = 'PY_MG_LocationHolidayCalendar'
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
            df_in_Line = read_csv_file("df_in_Line")
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_Time = read_csv_file("df_in_Time")


        print_df(df_in_WorkingCalendarLine, 'input table load .... df_in_WorkingCalendarLine')
        print_df(df_in_Line, 'input table load .... df_in_Line')
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_BOMMaster, 'input table load .... df_in_BOMMaster')
        print_df(df_in_Time, 'input table load .... df_in_Time')

        step('=====> STEP1 End')
        
        

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'

        STATUS_COLUMN = "status"

        LINE_COLUMN = 'Line.[Line]'
        LINE_TYPE_COLUMN = 'Line.[Line Type]'

        ITEM_SITE_ASN_CUR_STATUS_COLUMN = "Item Site Asn_Cur Status"
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = "Item Site Asn_Engine Flag"
        ITEM_SITE_ASN_ITEM_GRP_COLUMN = "Item Site Asn_Item Grp"
        ITEM_SITE_ASN_SALES_PROD_ASN_COLUMN = "Item Site Asn_Sales Prod Asn"
        ITEM_SITE_ASN_STAGE_COLUMN = "Item Site Asn_Stage"

        WORK_TYPE_COLUMN = "[Work Type].[Work Type]"
        DATA_SET_COLUMN = "[Data Set].[Data Set]"
        WORK_CAL_LINE_LOCK_FLAG_COLUMN = "Work Cal Line_Lock Flag"
        WORK_CAL_LINE_TIME_COLUMN = "Work Cal Line_Time"

        ACTIVITY1_COLUMN = "Activity1.[Activity1]"
        ACTIVITY2_COLUMN = "Activity2.[Activity2]"
        ACTIVITY3_COLUMN = "Activity3.[Activity3]"
        W_METERIAL_PRODUCTION_ASSOCIATION_COLUMN = "W Material Production Association"
        W_METERIAL_PRODUCTION_QUANTITY_PER_COLUMN = "W Material Production Quantity Per"

        BOM_ID_COLUMN = "BOM Info.[BOM ID]"
        BOM_MASTER_ID_COLUMN = "BOM Master_BOM ID"
        BOM_MASTER_EFF_ENDDATE_COLUMN = "BOM Master_Eff Enddate"
        BOM_MASTER_EFF_STARTDATE_COLUMN = "BOM Master_Eff Startdate"
        BOM_MASTER_PRIORITY_COLUMN = "BOM Master_Priority"
        BOM_MASTER_STATUS_COLUMN = "BOM Master_Status"

        TIME_DAY_COLUMN = 'Time.[Day]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAYKEY_COLUMN = 'Time.[DayKey]'
        TIME_WEEKKEY_COLUMN = 'Time.[WeekKey]'
        TIME_W_SOLVER_CURRENT_BUCKET_COLUMN = 'Time.[W Solver Current Bucket]'
        TIME_W_SOLVER_START_BUCKET_COLUMN = 'Time.[W Solver Start Bucket]'
        TIME_W_SOLVER_END_BUCKET_COLUMN = 'Time.[W Solver End Bucket]'

        W_PRODUCTION_HOLIDAY = "W Production Holiday"

        df_ProductionHolidays_columns = [
            VERSION_NAME_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, W_PRODUCTION_HOLIDAY
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # location 만 발췌, 중복값 삭제(Location Distinct) 및 미사용 컬럼 삭제
        #   - df_in_ItemSiteAsn remake
        drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [LOCATION_COLUMN]]
        df_in_ItemSiteAsn = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[LOCATION_COLUMN], keep='first')
        print_df(df_in_ItemSiteAsn, 'STEP3 by 1 ____ df_in_ItemSiteAsn .... select')

        # week 만 발췌, 중복값 삭제(Week Distinct) 및 미사용 컬럼 삭제
        #   - df_in_Time remake
        drop_column = [col for col in list(df_in_Time.columns) if col not in [TIME_WEEK_COLUMN]]
        df_in_Time = df_in_Time.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(subset=[TIME_WEEK_COLUMN], keep='first')
        print_df(df_in_Time, 'STEP3 by 2 ____ df_in_Time .... filter')

        # Plan 대상 MF Site 대상으로 Week Set 구성
        #   - df_in_ItemSiteAsn (Plan 대상 ITEM/SITE) / df_in_Time ( Planning Horzion )
        week_set_df = pd.merge(df_in_ItemSiteAsn.assign(temp_key=1), df_in_Time.assign(temp_key=1),
                               on='temp_key').drop('temp_key', axis=1).drop_duplicates(
            subset=[LOCATION_COLUMN, TIME_WEEK_COLUMN], keep='first')
        print_df(week_set_df, 'STEP3 by 3 ____ week_set_df .... merge')

        # Line Week Set 구성
        #   - df_in_WorkingCalendarLine 과 df_in_Line 에서 line 이 같은 행만 선택
        matched_line_df = pd.merge(df_in_WorkingCalendarLine, df_in_Line, on=LINE_COLUMN, how='inner')
        print_df(matched_line_df, 'STEP3 by 4 ____ matched_line_df .... merge[df_in_WorkingCalendarLine, df_in_Line]')

        # df_in_WorkingCalendarLine 의 location 이 df_in_ItemSiteAsn 의 location 에 속한 행만 선택
        location_filtered_df = matched_line_df[matched_line_df[LOCATION_COLUMN].isin(df_in_ItemSiteAsn[LOCATION_COLUMN])]
        print_df(location_filtered_df, 'STEP3 by 5 ____ location_filtered_df .... filter')

        # location 및 week 별로 line 수를 계산하고 데이터프레임을 재구성
        line_week_set_count_df = location_filtered_df.groupby(
            [LOCATION_COLUMN, TIME_WEEK_COLUMN])[LINE_COLUMN].count().reset_index(name='lineCount')
        print_df(line_week_set_count_df, 'STEP3 by 6 ____ line_week_set_count_df .... groupby')

        line_week_set_df = line_week_set_count_df[line_week_set_count_df['lineCount'] > 1]
        line_week_set_df = line_week_set_df.drop(labels=['lineCount'], axis=1)
        print_df(line_week_set_df, 'STEP3 by 7 ____ line_week_set_df .... filter')

        # Set 중 실제 Calendar가 존재하지 않는 Routing Set  구성
        #   - Merge using left join
        routing_set_df = week_set_df.merge(line_week_set_df, how='left', on=[LOCATION_COLUMN, TIME_WEEK_COLUMN],
                                           indicator=STATUS_COLUMN)

        # 'On' or 'Off' based on not null or null
        routing_set_df[STATUS_COLUMN] = routing_set_df[STATUS_COLUMN].map({'both': 'On', 'left_only': 'Off'})
        print_df(routing_set_df, 'STEP3 by 8 ____ routing_set_df .... filter')

        # status 값이 Off 인 값만 copy
        routing_set_off_df = routing_set_df[routing_set_df[STATUS_COLUMN] == 'Off']
        print_df(routing_set_off_df, 'STEP3 by 9 ____ routing_set_off_df .... final')

        step('=====> STEP3 End')
        
        

        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : Final output table create')

        # 구성된 Routing Set 을 대상으로 BOM 정보(Activity)를 참고하여 Output Measure에 넣을 레이아웃으로  Set 구성
        #   - df_ProductionHolidays 생성
        #       Activity2 : RoutingID와 동일 ,  Activity1 : BOMID와 동일 ,  Activity3 : Item과 동일
        df_out_ProductionHolidays = pd.merge(df_in_BOMMaster, routing_set_off_df, how='inner', on=[LOCATION_COLUMN])

        # 'True'가 Holiday란 의미임. SET3에 구성된 SET 대상을 Insert하면서, 아래 Measure는 True로 설정
        df_out_ProductionHolidays[W_PRODUCTION_HOLIDAY] = True

        # 컬럼 재정렬 및 불필요 컬럼 삭제
        df_out_ProductionHolidays = df_out_ProductionHolidays.drop(labels=[
            STATUS_COLUMN, W_METERIAL_PRODUCTION_ASSOCIATION_COLUMN, W_METERIAL_PRODUCTION_QUANTITY_PER_COLUMN
        ], axis=1)

        df_out_ProductionHolidays[VERSION_NAME_COLUMN] = paramOutVersion

        step('=====> STEP4 End')
        
        
        

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_ProductionHolidays, 'output table create .... df_out_ProductionHolidays', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ProductionHolidays = pd.DataFrame(columns=df_ProductionHolidays_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ProductionHolidays = pd.DataFrame(columns=df_ProductionHolidays_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
