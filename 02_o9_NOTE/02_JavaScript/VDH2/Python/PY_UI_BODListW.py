"""

* 프로그램명
    - PY_UI_BODListW

* 프로그램 등록일 : 2025/02/17

* 내용

    - 현재는 확정생산계획만 대상(생산라인)
    - 2025.02.03 → df_in_BODItemW 에 없는 것만 update 하는 것으로 변경
    - 2025.05.14 → 주차 없는 것만 확인하는 로직 추가 및 Measure 추가
    - 2025.06.20 MG  값 수정
    - 2025.08.08 input query 수정 및 로직 추가
    - 2025.08.19 / ybest7.park (박병훈) / input query 수정  - (Measure.[BOD Prod SET_BOD Valid] == "Y") 추가
    - 2025-09-18 / ybest7.park (박병훈) / Template 수정
    - 2025-10-28 / ybest7.park (박병훈) / Template 수정 input Query 수정 df_in_BODList Query 수정 ( LCM BOD List_BOD Vaild → LCM BOD List_BOD Valid  로 변경해주세요 (오타로 인한 메저 변경)
    - 2025-11-27 / ybest7.park (박병훈)  / df_in_BODListNValid iput data 추가 및 df_out_LCMBODListWSub 로직 추가 df_in_BODListNValid('N") 인 데이터 업데이트 하는 로직 추가
    - 2025-12-02 / ybest7.park (박병훈)  / df_in_BODList 삭제되는 데이터 처리 로직 변경


* 변경이력
- 2024.09.23 / ybest7.park (박병훈) / Create

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
    - df_in_BODList =  Select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Item].[Class Category] ) on row, ({Measure.[LCM BOD List_Eff Startweek],Measure.[LCM BOD List_Eff Startdate], Measure.[LCM BOD List_Eff Endweek],Measure.[LCM BOD List_Eff Enddate], Measure.[LCM BOD List_BOD Priority], Measure.[LCM BOD List_Transit Time], Measure.[LCM BOD List_Shipment LT], Measure.[LCM BOD List_BOD Valid],Measure.[LCM BOD List_Time Phased Priority],Measure.[LCM BOD List_Time Phased Transit Time],Measure.[LCM BOD List_Time Phased Shipment LT],Measure.[Dummy]}) on column where {(Measure.[LCM BOD List_Time Phased Priority]=="Y") || (Measure.[LCM BOD List_Time Phased Transit Time] =="Y") ||(Measure.[LCM BOD List_Time Phased Shipment LT] =="Y") && (Measure.[LCM BOD List_BOD Valid] =="Y")};
    - df_in_MDMHorizon = select (&MDMHorizon * [Time].[Day]);
    - df_in_BODListW =   Select ([Version].[Version Name] * [Location].[Location] * [Item].[Class Category] * [Time].[Week] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] ) on row, ({Measure.[LCM BOD List W_BOD LT], Measure.[LCM BOD List W_Priority], Measure.[LCM BOD List W_Shipment LT], Measure.[LCM BOD List W_Update Time], Measure.[LCM BOD List W_Updated By]}) on column where {~isnull(Measure.[LCM BOD List W_BOD LT]) || ~isnull(Measure.[LCM BOD List W_Priority]) ||~isnull(Measure.[LCM BOD List W_Shipment LT])};
    - df_in_TimeWeek = select([Time].[Week] * [Time].[Day]);

* 데이터 삭제
    DELETE DATA FOR MODEL [BOD List W] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_BODListW = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List W_BOD LT], Measure.[BOD List W_Shipment LT]}) on column;
    - df_out_LCMBODListWSub = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item].[Class Category] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[LCM BOD List W Sub_BOD LT Endweek], Measure.[LCM BOD List W Sub_BOD LT Startweek], Measure.[LCM BOD List W Sub_BOD Valid], Measure.[LCM BOD List W Sub_Endweek], Measure.[LCM BOD List W Sub_Priority Endweek], Measure.[LCM BOD List W Sub_Priority Startweek], Measure.[LCM BOD List W Sub_Shipment LT Endweek], Measure.[LCM BOD List W Sub_Shipment LT Startweek], Measure.[LCM BOD List W Sub_Startweek]}) on column;

* 실행구문
    - EXEC plugin instance [PY_UI_BODListW] for measures {[LCM BOD List W_Priority]} using scope ( &CWVUI ) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1),(paramOutVersion,"CWV_MP"), ([Param.o9_sys_log_level], "DEBUG") };

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
str_instance = 'PY_UI_BODListW'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = (
    "CWV_MP"
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
    try:
        file_path = f"{file_name}.csv"
        if not os.path.exists(file_path):
            step(f"=====> 파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame()  # 빈 DataFrame 반환
        return pd.read_csv(file_path, low_memory=False, encoding="UTF-8")

    except Exception as e:
        step(f"=====> CSV 파일 읽기 실패: {file_name}, 오류: {str(e)}")
        return pd.DataFrame()  # 에러 발생시 빈 DataFrame 반환


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
        step(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(df):
    """데이터프레임 최적화 및 메모리 사용량 감소"""
    if df is None:
        return None

    # 데이터프레임 복사 및 메모리 최적화
    result = df.copy()

    # 숫자형 컬럼의 데이터 타입 최적화
    for col in result.select_dtypes(include=['int', 'float']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')

    # # 범주형 데이터 최적화
    # for col in result.select_dtypes(include=['object']).columns:
    #     if result[col].nunique() / len(result) < 0.5:  # 고유값이 50% 미만일 경우
    #         result[col] = result[col].astype('category')

    delete_dfs(df)
    return result


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
    """실행 시간을 계산하고, 분 또는 초 단위로 반환.
    초 단위가 0일 경우 초로 표시하고, 그 외에는 분으로 표시."""
    elapsed = time.time() - start_time
    if elapsed < 60:  # 1분 미만일 경우
        return str(round(elapsed, 2)) + " seconds"
    else:
        return str(round(elapsed / 60, 2)) + " minutes"


########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    # Batch 시작
    vd_log_start()
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
            df_in_BODList = read_csv_file('df_in_BODList_H2')
            df_in_BODListW = read_csv_file('df_in_BODListW_H2')
            df_in_MDMHorizon = read_csv_file('df_in_MDMHorizon_H2')
            df_in_TimeWeek = read_csv_file('df_in_TimeWeek_H2')

        dataframes = {
            'df_in_BODList': df_in_BODList,
            'df_in_BODListW': df_in_BODListW,
            'df_in_MDMHorizon': df_in_MDMHorizon,
            'df_in_TimeWeek': df_in_TimeWeek,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        Version_Name_COLUMNS = 'Version.[Version Name]'
        Location_COLUMNS = 'Location.[Location]'
        Sub_Location_COLUMNS = 'Sub Location.[Sub Location]'
        Trans_Mode_COKUMNS = 'Trans Mode.[Trans Mode]'
        Item_Class_Category_COLUMNS = 'Item.[Class Category]'
        Time_WeekKey_COLUMNS = 'Time.[WeekKey]'
        Time_Week_COLUMNS = 'Time.[Week]'
        Time_DayKey_COLUMNS = 'Time.[DayKey]'
        Time_Day_COLUMNS = 'Time.[Day]'

        LCM_BOD_List_Eff_Startweek = 'LCM BOD List_Eff Startweek'
        LCM_BOD_List_Eff_Startdate = 'LCM BOD List_Eff Startdate'
        LCM_BOD_List_Eff_Endweek = 'LCM BOD List_Eff Endweek'
        LCM_BOD_List_Eff_Enddate = 'LCM BOD List_Eff Enddate'
        LCM_BOD_List_BOD_Priority = 'LCM BOD List_BOD Priority'
        LCM_BOD_List_Transit_Time = 'LCM BOD List_Transit Time'
        LCM_BOD_List_Shipment_LT = 'LCM BOD List_Shipment LT'
        LCM_BOD_List_BOD_Valid = 'LCM BOD List_BOD Valid'
        LCM_BOD_List_Time_Phased_Priority = 'LCM BOD List_Time Phased Priority'
        LCM_BOD_List_Time_Phased_Transit_Time = 'LCM BOD List_Time Phased Transit Time'
        LCM_BOD_List_Time_Phased_Shipment_LT = 'LCM BOD List_Time Phased Shipment LT'
        Dummy = 'Dummy'

        LCM_BOD_List_W_BOD_LT = 'LCM BOD List W_BOD LT'
        LCM_BOD_List_W_Priority = 'LCM BOD List W_Priority'
        LCM_BOD_List_W_Shipment_LT = 'LCM BOD List W_Shipment LT'

        LCM_BOD_List_W_Sub_Enddate = 'LCM BOD List W Sub_Enddate'
        LCM_BOD_List_W_Sub_Endweek = 'LCM BOD List W Sub_Endweek'
        LCM_BOD_List_W_Sub_Startdate = 'LCM BOD List W Sub_Startdate'
        LCM_BOD_List_W_Sub_Startweek = 'LCM BOD List W Sub_Startweek'

        LCM_BOD_List_W_Sub_Priority_Startweek = 'LCM BOD List W Sub_Priority Startweek'
        LCM_BOD_List_W_Sub_BOD_LT_Startweek = 'LCM BOD List W Sub_BOD LT Startweek'
        LCM_BOD_List_W_Sub_Shipment_LT_Startweek = 'LCM BOD List W Sub_Shipment LT Startweek'
        LCM_BOD_List_W_Sub_Priority_Endweek = 'LCM BOD List W Sub_Priority Endweek'
        LCM_BOD_List_W_Sub_BOD_LT_Endweek = 'LCM BOD List W Sub_BOD LT Endweek'
        LCM_BOD_List_W_Sub_Shipment_LT_Endweek = 'LCM BOD List W Sub_Shipment LT Endweek'
        LCM_BOD_List_W_Sub_BOD_Valid = 'LCM BOD List W Sub_BOD Valid'
        LCM_BOD_List_W_Sub_Time_Phased_Prty = 'LCM BOD List W Sub_Time Phased Prty'
        LCM_BOD_List_W_Sub_Time_Phased_BOD_LT = 'LCM BOD List W Sub_Time Phased BOD LT'
        LCM_BOD_List_W_Sub_Time_Phased_Shipment_LT = 'LCM BOD List W Sub_Time Phased Shipment LT'

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # Time Week list 설정
        Week_list = df_in_MDMHorizon[Time_Week_COLUMNS].unique().tolist()
        note(f"Week_list = {Week_list}")

        # df_in_BODList = pd.concat([df_in_BODList, df_in_BODListNValid], axis=0, ignore_index=True)

        # Week List 확장
        df_in_BODList[Time_Week_COLUMNS] = df_in_BODList.apply(lambda x: Week_list, axis=1)
        df_in_BODList = df_in_BODList.explode(Time_Week_COLUMNS)

        print_df(df_in_BODList, "df_in_BODList 확장", False)

        # Week 가 포함된 데이터 프레임 정의
        week_dfs = [df_in_BODList, df_in_BODListW]
        # 반복문으로 Time_Week_COLUMNN 데이터 타입 변경
        for df in week_dfs:
            df[Time_Week_COLUMNS] = df[Time_Week_COLUMNS].astype(str)

        # 공통 Grain column 설정
        Grain_column = [Version_Name_COLUMNS, Location_COLUMNS, Sub_Location_COLUMNS, Trans_Mode_COKUMNS,
                        Item_Class_Category_COLUMNS, Time_Week_COLUMNS]

        # df_in_BODListW 의 Grain 별로 중복 삭제
        df_in_BODListW_temp = df_in_BODListW[Grain_column].drop_duplicates()

        # df_in_BODItem 의 Grain 별로 중복 삭제
        df_in_BODList_index_temp = df_in_BODList[Grain_column].drop_duplicates()

        # df_in_BODItemW index 설정
        if not df_in_BODListW_temp.empty:
            df_in_BODListW_index = df_in_BODListW_temp.set_index(Grain_column).index
        else:
            df_in_BODListW_index = pd.Index([], name='df_in_BODListW_index')
        # df_in_BODItem index 설정
        df_in_BODList_index = df_in_BODList_index_temp.set_index(Grain_column).index

        # df_in_BODList_index = df_in_BODList_index_temp.set_index(Grain_column).index
        # 필터링
        df_in_BODList_index_temp = df_in_BODList_index_temp[~df_in_BODList_index.isin(df_in_BODListW_index)]

        print_df(df_in_BODList, "df_in_BODList_temp filter 전", True)

        # 필터링 된 데이터 프레임을 원본 df_in_BODItem에서 필터
        df_in_BODList_temp = df_in_BODList[
            df_in_BODList[Grain_column].apply(tuple, axis=1).isin(df_in_BODList_index_temp.apply(tuple, axis=1))]

        print_df(df_in_BODList_temp, "df_in_BODList_temp filter 후", True)

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP4 Start : input data machining')

        # Start & End 날짜를 설정하기 위해 기간의 min / max 값 찾기
        MDM_start_date = pd.to_datetime(df_in_MDMHorizon[Time_Day_COLUMNS].min()).strftime('%Y-%m-%d')
        MDM_end_date = pd.to_datetime(df_in_MDMHorizon[Time_Day_COLUMNS].max()).strftime('%Y-%m-%d')
        MDM_start_week = df_in_MDMHorizon[Time_Week_COLUMNS].min()
        MDM_end_week = df_in_MDMHorizon[Time_Week_COLUMNS].max()

        # TimeWeek & TimdDay Dic으로 만들기
        weekday_dic = dict(zip(df_in_TimeWeek[Time_Day_COLUMNS], df_in_TimeWeek[Time_Week_COLUMNS]))

        # BOD_List_Eff_Startdate / BOD_List_Eff_Enddate NaN 값 채우기
        df_in_BODList_temp[LCM_BOD_List_Eff_Startdate] = df_in_BODList_temp[LCM_BOD_List_Eff_Startdate].fillna(
            MDM_start_date)
        df_in_BODList_temp[LCM_BOD_List_Eff_Enddate] = df_in_BODList_temp[LCM_BOD_List_Eff_Enddate].fillna(MDM_end_date)


        # 날짜 타입 변경을 위한 함수 및 변경
        def covert_to_date(str):
            return pd.to_datetime(str, errors='coerce').strftime('%Y-%m-%d')


        df_in_BODList_temp[LCM_BOD_List_Eff_Startdate] = df_in_BODList_temp[LCM_BOD_List_Eff_Startdate].apply(
            covert_to_date)
        df_in_BODList_temp[LCM_BOD_List_Eff_Enddate] = df_in_BODList_temp[LCM_BOD_List_Eff_Enddate].apply(covert_to_date)

        # df_in_MDMHorizon에 포함된 날짜만 filtering
        df_in_BODList_temp = df_in_BODList_temp[
            (df_in_BODList_temp[LCM_BOD_List_Eff_Startdate] >= MDM_start_date) | (
                    df_in_BODList_temp[LCM_BOD_List_Eff_Enddate] <= MDM_end_date)]
        # BOD_Prod_SET_Eff_Enddate 가 start_date 보다 작은 것 제외
        df_in_BODList_temp = df_in_BODList_temp[
            df_in_BODList_temp[LCM_BOD_List_Eff_Enddate] >= MDM_start_date]

        # 날짜를 주차로 변경
        df_in_BODList_temp['Start_week'] = df_in_BODList_temp[LCM_BOD_List_Eff_Startdate].map(weekday_dic)
        df_in_BODList_temp['End_week'] = df_in_BODList_temp[LCM_BOD_List_Eff_Enddate].map(weekday_dic)

        # Start_week , End_week NAN 값 채우기
        df_in_BODList_temp['Start_week'] = df_in_BODList_temp['Start_week'].fillna(MDM_start_week)
        df_in_BODList_temp['End_week'] = df_in_BODList_temp['End_week'].fillna(MDM_end_week)

        # 기간 설정을 위한 데이터 타입 변경
        df_in_BODList_temp['Start_week'] = df_in_BODList_temp['Start_week'].astype(int)
        df_in_BODList_temp['End_week'] = df_in_BODList_temp['End_week'].astype(int)

        # # df_in_BODItem_temp & df_in_MDMHorizon merge 확장
        # df_in_BODList_temp[Key_On] = 1
        # df_in_MDMHorizon[Key_On] = 1

        # output 설정을 위한 컬럼 설정
        df_in_BODList_temp[LCM_BOD_List_W_BOD_LT] = df_in_BODList_temp['LCM BOD List_Transit Time'].fillna(0).astype(int)
        df_in_BODList_temp[LCM_BOD_List_W_Shipment_LT] = df_in_BODList_temp[LCM_BOD_List_Shipment_LT].fillna(0).astype(int)
        df_in_BODList_temp[LCM_BOD_List_W_Priority] = df_in_BODList_temp[LCM_BOD_List_BOD_Priority].fillna(0).astype(int)

        # df_in_MDMHorizon_temp = df_in_MDMHorizon[[TimeWeek_COLUMN, Key_On]].drop_duplicates(subset=TimeWeek_COLUMN)
        #
        # df_in_BODList_temp = df_in_BODList_temp.merge(df_in_MDMHorizon_temp, on=Key_On, how='left').drop(columns=[Key_On],
        #                                                                                                  axis=1)

        df_in_BODList_temp[Time_Week_COLUMNS] = df_in_BODList_temp[Time_Week_COLUMNS].astype(int)

        print_df(df_in_BODList_temp, 'df_in_BODList_temp', True)

        ################################### 2025-08-08 df_out_LCMBODListWSub 설정 ###########################################
        # df_out_LCMBODListWSub 데이터 프레임 설정을 위한 데이터 복사
        df_out_LCMBODListWSub = df_in_BODList_temp.copy()
        # df_out_LCMBODListWSub 필요한 컬럼 설정
        df_out_LCMBODListWSub = df_out_LCMBODListWSub[[
            Version_Name_COLUMNS, Location_COLUMNS, Item_Class_Category_COLUMNS, Sub_Location_COLUMNS,Time_Week_COLUMNS,
            Trans_Mode_COKUMNS, LCM_BOD_List_Eff_Startweek, LCM_BOD_List_Eff_Endweek, LCM_BOD_List_Time_Phased_Priority,
            LCM_BOD_List_BOD_Valid, LCM_BOD_List_Time_Phased_Transit_Time, LCM_BOD_List_Time_Phased_Shipment_LT]]

        df_out_LCMBODListWSub[LCM_BOD_List_Eff_Startweek] = df_out_LCMBODListWSub[LCM_BOD_List_Eff_Startweek].fillna(
            0).astype(int)
        df_out_LCMBODListWSub[LCM_BOD_List_Eff_Endweek] = df_out_LCMBODListWSub[LCM_BOD_List_Eff_Endweek].fillna(
            0).astype(int)

        # # df_out_LCMBODListWSub 컬럼명 변경
        # df_out_LCMBODListWSub = df_out_LCMBODListWSub.rename(
        #     columns={LCM_BOD_List_Eff_Enddate : LCM_BOD_List_W_Sub_Enddate , LCM_BOD_List_Eff_Startdate: LCM_BOD_List_W_Sub_Startdate,
        #             'Start_week' : LCM_BOD_List_W_Sub_Startweek ,  'End_week' : LCM_BOD_List_W_Sub_Endweek})
        #
        # # 데이터 프레임 타입 변경
        # df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Startweek] = df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Startweek].astype(str)
        # df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Endweek] = df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Endweek].astype(str)

        ############################################################2025-09-09 수정 #######################################
        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Priority_Startweek] = df_out_LCMBODListWSub[
            LCM_BOD_List_Eff_Startweek].fillna('null').astype(str).str.replace(r'(?<=\d)\.0+$', '', regex=True).replace('0','Null')
        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_BOD_LT_Startweek] = df_out_LCMBODListWSub[
            LCM_BOD_List_Eff_Startweek].fillna('null').astype(str).str.replace(r'(?<=\d)\.0+$', '', regex=True).replace('0','Null')
        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Shipment_LT_Startweek] = df_out_LCMBODListWSub[
            LCM_BOD_List_Eff_Startweek].fillna('null').astype(str).str.replace(r'(?<=\d)\.0+$', '', regex=True).replace('0','Null')

        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Priority_Endweek] = df_out_LCMBODListWSub[
            LCM_BOD_List_Eff_Endweek].fillna('null').astype(str).str.replace(r'(?<=\d)\.0+$', '', regex=True).replace('0','Null')
        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_BOD_LT_Endweek] = df_out_LCMBODListWSub[
            LCM_BOD_List_Eff_Endweek].fillna('null').astype(str).str.replace(r'(?<=\d)\.0+$', '', regex=True).replace('0','Null')
        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Shipment_LT_Endweek] = df_out_LCMBODListWSub[
            LCM_BOD_List_Eff_Endweek].fillna('null').astype(str).str.replace(r'(?<=\d)\.0+$', '', regex=True).replace('0','Null')

        # df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Time_Phased_Prty] = np.where(df_out_LCMBODListWSub[])
        # df_out_LCMBODListWSub[
        #     [LCM_BOD_List_W_Sub_Time_Phased_Prty,LCM_BOD_List_W_Sub_Time_Phased_BOD_LT,
        #      LCM_BOD_List_W_Sub_Time_Phased_Shipment_LT]] = 'Y'

        ############################################ 2025-12-02 수정 (ybest7.park) #####################################
        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_BOD_Valid] = np.where(
            df_out_LCMBODListWSub[LCM_BOD_List_BOD_Valid].isna(), 'N'
            , df_out_LCMBODListWSub[LCM_BOD_List_BOD_Valid])

        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Time_Phased_Prty] = np.where(
            df_out_LCMBODListWSub[LCM_BOD_List_Time_Phased_Priority].isna(),
            'N', df_out_LCMBODListWSub[LCM_BOD_List_Time_Phased_Priority])

        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Time_Phased_BOD_LT] = np.where(
            df_out_LCMBODListWSub[LCM_BOD_List_Time_Phased_Transit_Time].isna(),
            'N', df_out_LCMBODListWSub[LCM_BOD_List_Time_Phased_Transit_Time])

        df_out_LCMBODListWSub[LCM_BOD_List_W_Sub_Time_Phased_Shipment_LT] = np.where(
            df_out_LCMBODListWSub[LCM_BOD_List_Time_Phased_Shipment_LT].isna(),
            'N', df_out_LCMBODListWSub[LCM_BOD_List_Time_Phased_Shipment_LT])

        df_out_LCMBODListWSub.drop(columns=[LCM_BOD_List_Eff_Startweek, LCM_BOD_List_Eff_Endweek,
                                            LCM_BOD_List_BOD_Valid, LCM_BOD_List_Time_Phased_Priority,
                                            LCM_BOD_List_Time_Phased_Transit_Time,
                                            LCM_BOD_List_Time_Phased_Shipment_LT],
                                   axis=1, inplace=True)


        print_df(df_out_LCMBODListWSub, 'df_out_LCMBODListWSub', True)

        ################################### 2025-08-08 df_out_LCMBODListWSub 설정 완료 #######################################

        # MDMHorizon 기간에 걸리지 않는 값들 0으로 처리
        df_in_BODList_temp['LCM BOD List_Transit Time'] = np.where(
            ((df_in_BODList_temp[Time_Week_COLUMNS] >= df_in_BODList_temp['Start_week']) &
             (df_in_BODList_temp[Time_Week_COLUMNS] <= df_in_BODList_temp['End_week'])),
            df_in_BODList_temp['LCM BOD List_Transit Time'], df_in_BODList_temp['LCM BOD List_Transit Time'])

        df_in_BODList_temp[LCM_BOD_List_Shipment_LT] = np.where(
            ((df_in_BODList_temp[Time_Week_COLUMNS] >= df_in_BODList_temp['Start_week']) &
             (df_in_BODList_temp[Time_Week_COLUMNS] <= df_in_BODList_temp['End_week'])),
            df_in_BODList_temp[LCM_BOD_List_Shipment_LT], df_in_BODList_temp[LCM_BOD_List_Shipment_LT])

        df_in_BODList_temp['LCM BOD List_BOD Priority'] = np.where(
            ((df_in_BODList_temp[Time_Week_COLUMNS] >= df_in_BODList_temp['Start_week']) &
             (df_in_BODList_temp[Time_Week_COLUMNS] <= df_in_BODList_temp['End_week'])),
            df_in_BODList_temp['LCM BOD List_BOD Priority'], df_in_BODList_temp['LCM BOD List_BOD Priority'])



        ########################## Default 값 설정 (UI - Active Rule 사용) 2025.05.14 , ybest7 #######################

        # df_in_BODList_temp[BOD_List_W_Period_Lock_Flag_BOD_LT] = np.where(
        #     ((df_in_BODList_temp[TimeWeek_COLUMN] >= df_in_BODList_temp['Start_week']) &
        #      (df_in_BODList_temp[TimeWeek_COLUMN] <= df_in_BODList_temp['End_week'])),
        #     False, True)
        #
        # df_in_BODList_temp[BOD_List_W_Period_Lock_Flag_Shipment_LT] = np.where(
        #     ((df_in_BODList_temp[TimeWeek_COLUMN] >= df_in_BODList_temp['Start_week']) &
        #      (df_in_BODList_temp[TimeWeek_COLUMN] <= df_in_BODList_temp['End_week'])),
        #     False, True)

        # 순서 지정
        df_in_BODList_temp = df_in_BODList_temp[
            [Version_Name_COLUMNS, Location_COLUMNS, Time_Week_COLUMNS, Sub_Location_COLUMNS, Trans_Mode_COKUMNS,
             Item_Class_Category_COLUMNS, LCM_BOD_List_W_BOD_LT, LCM_BOD_List_W_Priority, LCM_BOD_List_W_Shipment_LT]]

        print_df(df_in_BODList_temp, 'df_in_BODList_temp', True)

        step('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_BODListW = df_in_BODList_temp.copy()

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_BODListW, 'df_out_BODListW', True)
            print_df(df_out_LCMBODListWSub, 'df_out_LCMBODListWSub', True)

        print_df(df_out_BODListW, 'df_out_BODListW', True)
        print_df(df_out_LCMBODListWSub, 'df_out_LCMBODListWSub', True)

        row_count, col_count = df_out_BODListW.shape
        note(f'=====> Final df_out_BODListW rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_LCMBODListWSub.shape
        note(f'=====> Final df_out_LCMBODListWSub rows : {row_count} , Columns : {col_count}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODListW = pd.DataFrame([], columns=[])
        df_out_LCMBODListWSub = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
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