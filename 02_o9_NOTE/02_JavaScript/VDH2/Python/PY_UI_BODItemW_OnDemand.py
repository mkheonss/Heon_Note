"""

* 프로그램명
    - PY_UI_BODItemW_OnDemand

* 프로그램 등록일 : 2025/12/09

* 내용

    - 현재는 확정생산계획만 대상(생산라인)
    - 2025/12/09 → df_in_BODItemW에서 복사하여 df_out_BODItem 생성


* 변경이력
- 2025/12/09 / ybest7.park (박병훈) / Create
- 2025/12/16 / ybest7.park (박병훈) df_out_BODItemWSub 생성 조건 변경에 딸 로직 순서 변경
- 2026.03.27 / ybest7.park (박병훈) : df_in_BODItemRunFlag 데이터 중 df_in_BODItemWRunFlag 없는 것만 업데이트 하던 내용 중 이제는 input data 모두 업데이트 하는 로직으로 변경 미 fillna 부분 수정

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
     - df_in_BODItemRunFlag = Select ([Version].[Version Name] * [Item].[Item] * Location.[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Priority],Measure.[BOD Item_Shipment LT],Measure.[BOD Item_BOD LT], Measure.[BOD Item_Eff Startweek],Measure.[BOD Item_Eff Endweek], Measure.[Dummy]}) on column where { Measure.[BOD Item_PyRunFlag]==1, Measure.[BOD Item_BOD Valid] == "Y" } ;
    -  df_in_MDMHorizon = select (&MDMHorizon * [Time].[Day]);
    - df_in_BODItemWRunFlag = Select ([Version].[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item W_Prty], Measure.[BOD Item W_Shipment LT], Measure.[BOD Item W_BOD LT],Measure.[Dummy]}) on column   where { Measure.[BOD Item W_PyRunFlag] == 1 &&  (~isnull(Measure.[BOD Item W_Prty]) ||~isnull(Measure.[BOD Item W_Shipment LT]) ||  ~isnull(Measure.[BOD Item W_BOD LT]) ) };
    - df_in_TimeWeek = select([Time].[Week] * [Time].[Day]);
* 데이터 삭제

Cartesian scope: (
    [Version].[Version Name].[CWV_MP] *
    [Item].[Item] *
    &LCMLocation.unionwith(&NSUILocationPlant).[P306] *
    &NSUISubLocationDC.unionwith(&NSUISubLocationPlant).[S602] *
    [Trans Mode].[Trans Mode]);
    Measure.[BOD Item_PyRunFlag] = 1;
end scope;


    DELETE DATA FOR MODEL [BOD Item] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [BOD Item W] where {Version.[Version Name].[CWV_MP]};


* Output Table
    - df_out_BODItemW = Select ([Version].[Version Name].[CWV_MP] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item W_Prty], Measure.[BOD Item W_Shipment LT], Measure.[BOD Item W_BOD LT], Measure.[BOD Item W_PyRunFlag]}) on column;
    - df_out_BODItem = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_PyRunFlag]}) on column;
    df_out_BODItemWSub = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location]. * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item W Sub_BOD LT Endweek], Measure.[BOD Item W Sub_BOD LT Startweek], Measure.[BOD Item W Sub_BOD Valid], Measure.[BOD Item W Sub_Endweek], Measure.[BOD Item W Sub_Priority Endweek], Measure.[BOD Item W Sub_Priority Startweek], Measure.[BOD Item W Sub_Shipment LT Endweek], Measure.[BOD Item W Sub_Shipment LT Startweek], Measure.[BOD Item W Sub_Startweek]}) on column;
    - df_out_log
    - df_out_logDetail

* 실행구문
    // 1.BOD Item W (SET) 생성
    EXEC plugin instance [PY_UI_BODItemW_OnDemand] for measures {[BOD Item_Priority]} using scope ( &CWVUI * &NSUILocationDC.unionwith(&MFStageSETLocation) * &NSUISubLocationDC * &SETItem )
    using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };

    // 2.BOD Item W (LCM) 생성
    EXEC plugin instance [PY_UI_BODItemW_OnDemand] for measures {[BOD Item_Priority]} using scope ( &CWVUI * &MFStageLCMLocation * &MFStageSETSubLocation * &LCMItem )
    using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };

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
str_instance = 'PY_UI_BODItemW_OnDemand'
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
            df_in_BODItemRunFlag = read_csv_file('df_in_BODItemRunFlag_H2')
            df_in_MDMHorizon = read_csv_file('df_in_MDMHorizon_H2')
            df_in_BODItemWRunFlag = read_csv_file('df_in_BODItemWRunFlag_H2')
            df_in_TimeWeek = read_csv_file('df_in_TimeWeek_H2')

        dataframes = {
            'df_in_BODItemRunFlag': df_in_BODItemRunFlag,
            'df_in_MDMHorizon': df_in_MDMHorizon,
            'df_in_BODItemWRunFlag': df_in_BODItemWRunFlag,
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
        Item_COLUMNS = 'Item.[Item]'
        Location_COLUMNS = 'Location.[Location]'
        Sub_Location_COLUMNS = 'Sub Location.[Sub Location]'
        Trans_Mode_COLUMNS = 'Trans Mode.[Trans Mode]'

        Time_WeekKey_COLUMNS = 'Time.[WeekKey]'
        Time_Week_COLUMNS = 'Time.[Week]'
        Time_DayKey_COLUMNS = 'Time.[DayKey]'
        Time_Day_COLUMNS = 'Time.[Day]'

        BOD_Item_Priority = 'BOD Item_Priority'
        BOD_Item_Shipment_LT = 'BOD Item_Shipment LT'
        BOD_Item_BOD_LT = 'BOD Item_BOD LT'
        BOD_Item_Eff_Startdate = 'BOD Item_Eff Startdate'
        BOD_Item_Eff_Enddate = 'BOD Item_Eff Enddate'
        BOD_Item_Eff_Startweek = 'BOD Item_Eff Startweek'
        BOD_Item_Eff_Endweek = 'BOD Item_Eff Endweek'
        BOD_Item_PyRunFlag = 'BOD Item_PyRunFlag'
        BOD_Item_BOD_Valid = 'BOD Item_BOD Valid'

        BOD_Item_W_Prty = 'BOD Item W_Prty'
        BOD_Item_W_Shipment_LT = 'BOD Item W_Shipment LT'
        BOD_Item_W_BOD_LT = 'BOD Item W_BOD LT'
        BOD_Item_W_PyRunFlag = 'BOD Item W_PyRunFlag'

        BOD_Item_W_Sub_Enddate = 'BOD Item W Sub_Enddate'
        BOD_Item_W_Sub_Endweek = 'BOD Item W Sub_Endweek'
        BOD_Item_W_Sub_Startdate = 'BOD Item W Sub_Startdate'
        BOD_Item_W_Sub_Startweek = 'BOD Item W Sub_Startweek'

        BOD_Item_W_Sub_Priority_Startweek = 'BOD Item W Sub_Priority Startweek'
        BOD_Item_W_Sub_BOD_LT_Startweek = 'BOD Item W Sub_BOD LT Startweek'
        BOD_Item_W_Sub_Shipment_LT_Startweek = 'BOD Item W Sub_Shipment LT Startweek'

        BOD_Item_W_Sub_Priority_Endweek = 'BOD Item W Sub_Priority Endweek'
        BOD_Item_W_Sub_BOD_LT_Endweek = 'BOD Item W Sub_BOD LT Endweek'
        BOD_Item_W_Sub_Shipment_LT_Endweek = 'BOD Item W Sub_Shipment LT Endweek'
        BOD_Item_W_Sub_BOD_Valid = 'BOD Item W Sub_BOD Valid'

        Dummy = 'Dummy'

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # df_in_BODItemW에 없는 df_in_BODItem 추가하기 위한 필터링 전단계
        # 공통 Grain column 설정
        Grain_column = [Version_Name_COLUMNS, Location_COLUMNS, Item_COLUMNS, Sub_Location_COLUMNS, Trans_Mode_COLUMNS]

        # df_in_BODItemW 의 Grain 별로 중복 삭제
        df_in_BODItemW_temp = df_in_BODItemWRunFlag[Grain_column].drop_duplicates()
        # df_in_BODItem 의 Grain 별로 중복 삭제
        df_in_BODItem_temp = df_in_BODItemRunFlag[Grain_column].drop_duplicates()
        ############### 2025-12-16 로직 순서 뒤로 변경 조건 필터 데이터 생성 후 실행  ##########################################
        # # df_in_BODItemW index 설정
        # df_in_BODItemW_index = df_in_BODItemW_temp.set_index(Grain_column).index
        # # df_in_BODItem index 설정
        # df_in_BODItem_index = df_in_BODItem_temp.set_index(Grain_column).index
        # # 필터링
        # df_in_BODItem_temp = df_in_BODItem_temp[~df_in_BODItem_index.isin(df_in_BODItemW_index)]

        # 필터링 된 데이터 프레임을 원본 df_in_BODItem에서 필터
        df_in_BODItem_temp = df_in_BODItemRunFlag.merge(
            df_in_BODItem_temp,
            on = Grain_column,
            how ='inner'
        )


        # df_in_BODItem_temp = df_in_BODItemRunFlag[
        #     df_in_BODItemRunFlag[Grain_column].apply(tuple, axis=1).isin(df_in_BODItem_temp.apply(tuple, axis=1))]

        print_df(df_in_BODItem_temp, "df_in_BODItem_temp data", True)

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

        note(f"MDM_start_date: {MDM_start_date}, MDM_end_date: {MDM_end_date}")
        note(f"MDM_start_week: {MDM_start_week}, MDM_end_week: {MDM_end_week}")

        # TimeWeek & TimdDay Dic으로 만들기
        weekday_dic = dict(zip(df_in_TimeWeek[Time_Week_COLUMNS], df_in_TimeWeek[Time_Day_COLUMNS]))
        # Weeks Dict
        weeks_dic = dict(zip(df_in_TimeWeek[Time_Day_COLUMNS], df_in_TimeWeek[Time_Week_COLUMNS]))

        # vdCommon.gfn_saveDf(df_in_BODItem_temp, "df_in_BODItem_temp data - 날짜 변환 전 ", True)

        df_in_BODItem_temp = df_in_BODItem_temp.copy()

        # # 주차를 날짜로 변경
        df_in_BODItem_temp[BOD_Item_Eff_Startdate] = df_in_BODItem_temp[BOD_Item_Eff_Startweek].map(weekday_dic)
        df_in_BODItem_temp[BOD_Item_Eff_Enddate] = df_in_BODItem_temp[BOD_Item_Eff_Endweek].map(weekday_dic)
        df_in_BODItem_temp[BOD_Item_Eff_Startdate] = df_in_BODItem_temp[BOD_Item_Eff_Startdate].fillna(MDM_start_date)
        df_in_BODItem_temp[BOD_Item_Eff_Enddate] = df_in_BODItem_temp[BOD_Item_Eff_Enddate].fillna(MDM_end_date)

        # vdCommon.gfn_saveDf(df_in_BODItem_temp, "df_in_BODItem_temp data - 날짜 변환 후  ", True)

        # 2026.03.27 fillna 부분 수정
        df_in_BODItem_temp[BOD_Item_Eff_Startweek] = df_in_BODItem_temp[BOD_Item_Eff_Startweek]
        df_in_BODItem_temp[BOD_Item_Eff_Endweek] = df_in_BODItem_temp[BOD_Item_Eff_Endweek]

        # BOD_Item_Eff_Startdate / BOD_Item_Eff_Enddate NaN 값 채우기
        # df_in_BODItem_temp[BOD_Item_Eff_Startweek] = df_in_BODItem_temp[BOD_Item_Eff_Startweek].fillna(MDM_start_week)
        # df_in_BODItem_temp[BOD_Item_Eff_Endweek] = df_in_BODItem_temp[BOD_Item_Eff_Endweek].fillna(MDM_end_week)

        # vdCommon.gfn_saveDf(df_in_BODItem_temp, "df_in_BODItem_temp data - 주차 변환 후  ", True)

        # 날짜 타입 변경을 위한 함수 및 변경
        # def covert_to_date(str):
        #     return pd.to_datetime(str, errors='coerce').strftime('%Y-%m-%d')

        df_in_BODItem_temp[BOD_Item_Eff_Startdate] = pd.to_datetime(df_in_BODItem_temp[BOD_Item_Eff_Startdate],
                                                                    errors='coerce').dt.strftime('%Y-%m-%d')
        df_in_BODItem_temp[BOD_Item_Eff_Enddate] = pd.to_datetime(df_in_BODItem_temp[BOD_Item_Eff_Enddate],
                                                                  errors='coerce').dt.strftime('%Y-%m-%d')

        ############################################### 2025-08-10  추가 및 수정 #########################################
        # df_out_BODItemWSub 설정을 위한 데이터 프레임 복사
        df_out_BODItemWSub = df_in_BODItem_temp.copy()
        # 필요한 컬럼 설정 및 중복삭제
        df_out_BODItemWSub = df_out_BODItemWSub[[
            Version_Name_COLUMNS, Location_COLUMNS, Item_COLUMNS, Sub_Location_COLUMNS, Trans_Mode_COLUMNS,
            BOD_Item_Eff_Startweek, BOD_Item_Eff_Endweek]].drop_duplicates()

        ############################################### 2025-08-19  추가 및 수정 #########################################

        df_out_BODItemWSub[BOD_Item_W_Sub_Priority_Startweek] = df_out_BODItemWSub[BOD_Item_Eff_Startweek].fillna(
            'null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_out_BODItemWSub[BOD_Item_W_Sub_BOD_LT_Startweek] = df_out_BODItemWSub[BOD_Item_Eff_Startweek].fillna(
            'null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_out_BODItemWSub[BOD_Item_W_Sub_Shipment_LT_Startweek] = df_out_BODItemWSub[BOD_Item_Eff_Startweek].fillna(
            'null').astype(str).str.replace(r'\.0$', '', regex=True)
        # df_out_BODItemWSub[BOD_Item_W_Sub_Startweek] = df_out_BODItemWSub[BOD_Item_Eff_Startweek].astype(str)

        df_out_BODItemWSub[BOD_Item_W_Sub_Priority_Endweek] = df_out_BODItemWSub[BOD_Item_Eff_Endweek].fillna(
            'null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_out_BODItemWSub[BOD_Item_W_Sub_BOD_LT_Endweek] = df_out_BODItemWSub[BOD_Item_Eff_Endweek].fillna(
            'null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_out_BODItemWSub[BOD_Item_W_Sub_Shipment_LT_Endweek] = df_out_BODItemWSub[BOD_Item_Eff_Endweek].fillna(
            'null').astype(str).str.replace(r'\.0$', '', regex=True)

        # df_out_BODItemWSub[BOD_Item_W_Sub_Endweek] = df_out_BODItemWSub[BOD_Item_Eff_Endweek].astype(str)

        df_out_BODItemWSub[BOD_Item_W_Sub_BOD_Valid] = 'Y'

        df_out_BODItemWSub = df_out_BODItemWSub[
            [Version_Name_COLUMNS, Location_COLUMNS, Item_COLUMNS, Sub_Location_COLUMNS, Trans_Mode_COLUMNS,
             BOD_Item_W_Sub_BOD_LT_Endweek, BOD_Item_W_Sub_BOD_LT_Startweek, BOD_Item_W_Sub_BOD_Valid,
             BOD_Item_W_Sub_Priority_Endweek, BOD_Item_W_Sub_Priority_Startweek, BOD_Item_W_Sub_Shipment_LT_Endweek,
             BOD_Item_W_Sub_Shipment_LT_Startweek]]

        df_out_BODItemWSub = df_out_BODItemWSub.drop_duplicates()

        df_out_BODItemWSub = df_out_BODItemWSub.reset_index(drop=True)

        print_df(df_out_BODItemWSub, "df_out_BODItemWSub data - 확인", True)

        ####################################### 2025-12-16 필터 순서 변경 (추가) ##########################################
        # df_in_BODItem_temp = df_in_BODItem_temp[
        #     ~df_in_BODItem_temp.set_index(Grain_column).index.isin(
        #         df_in_BODItemWRunFlag[Grain_column].drop_duplicates().set_index(Grain_column).index)]


        # # 날짜를 주차로 변경
        # df_in_BODItem_temp[BOD_Item_Eff_Startweek] = df_in_BODItem_temp[BOD_Item_Eff_Startdate].map(weeks_dic)
        # df_in_BODItem_temp[BOD_Item_Eff_Endweek] = df_in_BODItem_temp[BOD_Item_Eff_Enddate].map(weeks_dic)

        df_in_MDMHorizon['Key_on'] = "1"
        df_in_BODItem_temp['Key_on'] = "1"


        df_in_BODItem_temp = df_in_BODItem_temp.merge(
            df_in_MDMHorizon[[Time_Week_COLUMNS, 'Key_on']].drop_duplicates(),
            on='Key_on',
            how='left').drop(columns='Key_on', axis=1)

        # week_unique_list = df_in_MDMHorizon[Time_Week_COLUMNS].unique().tolist()
        #
        # note(f"df_in_BODItem_temp 예상 컬럼 수 : {len(df_in_BODItem_temp) * len(week_unique_list)}")
        # # week list로 확장하기 위해 컬럼 설정
        # df_in_BODItem_temp[Time_Week_COLUMNS] = df_in_BODItem_temp.apply(lambda x: week_unique_list, axis=1)
        # # 설정된 리스트 확장
        # df_in_BODItem_temp = df_in_BODItem_temp.explode(Time_Week_COLUMNS)
        # note('test 중 Error 찾기 2')
        # print_df(df_in_BODItem_temp, "df_in_BODItem_temp data - 임시-1", True)

        # weeks = pd.DataFrame({'Week' : df_in_MDMHorizon[Time_Week_COLUMNS].drop_duplicates()})
        # weeks['key'] = 1
        #
        # chunk = 20_000
        # for i in range(0, len(df_in_BODItem_temp), chunk):
        #     t = df_in_BODItem_temp.iloc[i:i+chunk].copy()
        #     t['key'] = 1
        #     out = t.merge(weeks, on='key', how='inner').drop(columns='key')
        #     out.to_parquet(f"out/part_{i//chunk:05d}.parquet", index=False)

        df_out_BODItem = df_in_BODItemRunFlag[df_in_BODItemRunFlag.columns[:5]].copy()
        df_out_BODItem[BOD_Item_PyRunFlag] = 0
        # df_out_BODItem[BOD_Item_BOD_Valid] = 'Y'

        print_df(df_out_BODItem, 'df_out_BODItem 확인')

        del df_in_BODItemRunFlag, df_in_MDMHorizon, df_in_TimeWeek
        del df_in_BODItemWRunFlag
        ################################################################################################################

        #################################################################################################################
        # MDMHorizon 기간에 걸리지 않는 값들 0으로 처리

        df_in_BODItem_temp[BOD_Item_Priority] = np.where(
            ((df_in_BODItem_temp[Time_Week_COLUMNS] >= df_in_BODItem_temp[BOD_Item_Eff_Startweek]) &
             (df_in_BODItem_temp[Time_Week_COLUMNS] <= df_in_BODItem_temp[BOD_Item_Eff_Endweek])),
            df_in_BODItem_temp[BOD_Item_Priority], df_in_BODItem_temp[BOD_Item_Priority])

        df_in_BODItem_temp[BOD_Item_Shipment_LT] = np.where(
            ((df_in_BODItem_temp[Time_Week_COLUMNS] >= df_in_BODItem_temp[BOD_Item_Eff_Startweek]) &
             (df_in_BODItem_temp[Time_Week_COLUMNS] <= df_in_BODItem_temp[BOD_Item_Eff_Endweek])),
            df_in_BODItem_temp[BOD_Item_Shipment_LT], df_in_BODItem_temp[BOD_Item_Shipment_LT])

        df_in_BODItem_temp[BOD_Item_BOD_LT] = np.where(
            ((df_in_BODItem_temp[Time_Week_COLUMNS] >= df_in_BODItem_temp[BOD_Item_Eff_Startweek]) &
             (df_in_BODItem_temp[Time_Week_COLUMNS] <= df_in_BODItem_temp[BOD_Item_Eff_Endweek])),
            df_in_BODItem_temp[BOD_Item_BOD_LT], df_in_BODItem_temp[BOD_Item_BOD_LT])


        # output 설정을 위한 컬럼 설정
        df_in_BODItem_temp[BOD_Item_W_Prty] = df_in_BODItem_temp[BOD_Item_Priority]
        df_in_BODItem_temp[BOD_Item_W_Shipment_LT] = df_in_BODItem_temp[BOD_Item_Shipment_LT]
        df_in_BODItem_temp[BOD_Item_W_BOD_LT] = df_in_BODItem_temp[BOD_Item_BOD_LT]
        df_in_BODItem_temp[BOD_Item_W_PyRunFlag] = 0
        # df_in_BODItem_temp[BOD_Item_W_Sub_BOD_Valid] = 'Y'

        # df_in_BODItem_temp BOD Item W_PyRunFlag 추가

        df_in_BODItem_temp = df_in_BODItem_temp.reset_index(drop=True)

        print_df(df_in_BODItem_temp, "df_in_BODItem_temp data - 임시-2", True)

        step('=====> STEP4 End')
    ################################################################################################################
    # STEP 5 :  input data machining
    ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        # output DataFrame 복사
        df_out_BODItemW = df_in_BODItem_temp.copy()
        # df_out_BODItemW 순서 설정
        df_out_BODItemW = df_out_BODItemW[
            [Version_Name_COLUMNS, Location_COLUMNS, Item_COLUMNS, Time_Week_COLUMNS, Sub_Location_COLUMNS,
             Trans_Mode_COLUMNS,BOD_Item_W_Prty, BOD_Item_W_Shipment_LT, BOD_Item_W_BOD_LT,BOD_Item_W_PyRunFlag]]


        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_BODItemW, 'df_out_BODItemW', True)
            print_df(df_out_BODItem, 'df_out_BODItem', True)
            print_df(df_out_BODItemWSub, 'df_out_BODItemWSub', True)

        print_df(df_out_BODItemW, 'df_out_BODItemW', True)
        print_df(df_out_BODItem, 'df_out_BODItem', True)
        print_df(df_out_BODItemWSub, 'df_out_BODItemWSub', True)

        row_count, col_count = df_out_BODItemW.shape
        note(f'=====> Final df_out_BODItemW rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_BODItem.shape
        note(f'=====> Final df_out_BODItem rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_BODItemWSub.shape
        note(f'=====> Final df_out_BODItemWSub rows : {row_count} , Columns : {col_count}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ProductSetW = pd.DataFrame([], columns=[])
        df_out_ProductSetWSub = pd.DataFrame([], columns=[])
        df_out_BODItemW = pd.DataFrame([], columns=[])

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
