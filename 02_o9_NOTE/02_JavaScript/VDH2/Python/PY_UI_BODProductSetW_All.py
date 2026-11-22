"""

* 프로그램명
    - PY_UI_BODProductSetW

* 내용


* 변경이력
- 2025.02.19 / ybest7.park (박병훈) / Create
- 2025.04.30 / ybest7.park (박병훈) / input query 수정 및 VD Common 적용
- 2025.60.14 /  ybest7.park (박병훈) / Measure 추가 및 로직 변경
- 2025.06.20 / mg 수정
- 2025.08.07 / ybest7.park (박병훈) / input query 수정
- 2025.08.19 / ybest7.park (박병훈) / input query 수정  - (Measure.[LCM BOD List_BOD Vaild] == "Y") 추가
- 2025-09-09 / ybest7.park (박병훈) / 주차 로직 수정
- 2025-09-18 / ybest7.park (박병훈) / 주차 로직 2차 수정 및 Template 수정
- 2025-11-27 / ybest7.park (박병훈) / df_in_BODProdSET_NValid input data 추가 및 df_out_ProductSetWSub 에 데이터 업데이트 하는 로직 추가
- 2025-12-02 / ybest7.park (박병훈) / 로직 추가 및 수정

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_BODProdSET =  Select ([Version].[Version Name] * [Item].[Product Group] * &NSUILocationDC.unionwith(&MFStageSETLocation) * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Prod SET_Eff Endweek],Measure.[BOD Prod SET_Eff Enddate], Measure.[BOD Prod SET_Eff Startweek],Measure.[BOD Prod SET_Eff Startdate], Measure.[BOD Prod SET_Priority], Measure.[BOD Prod SET_Shipment LT], Measure.[BOD Prod SET_BOD LT], Measure.[BOD Prod SET_BOD Valid], Measure.[BOD Prod SET_Time Phased Prty],Measure.[BOD Prod SET_Time Phased BOD LT],Measure.[BOD Prod SET_Time Phased Shipment LT], Measure.[Dummy]}) on column where {~isnull(Measure.[BOD Prod SET_Time Phased Prty]) || ~isnull(Measure.[BOD Prod SET_Time Phased BOD LT]) ||~isnull(Measure.[BOD Prod SET_Time Phased Shipment LT])} ;
   - df_in_ProductSetW = Select ([Version].[Version Name] * [Item].[Product Group] * [Time].[Week] * &NSUILocationDC.unionwith(&MFStageSETLocation) * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Prod SET W_Priority], Measure.[BOD Prod SET W_BOD LT], Measure.[BOD Prod SET W_Shipment LT],Measure.[Dummy] }) on column;
   - df_in_MDMHorizon = select (&MDMHorizon * [Time].[Day]);
   - df_in_TimeWeek = select([Time].[Week] * [Time].[Day]);

* Output Table
    - df_out_ProductSetW = Select ([Version].[Version Name].[CWV_MP] * [Item].[Product] * [Time].[Week] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Prod SET W_Shipment LT], Measure.[BOD Prod SET W_BOD LT]}) on column;
    - df_out_ProductSetWSub = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Product Group] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Prod SET W Sub_BOD LT Endweek], Measure.[BOD Prod SET W Sub_BOD LT Startweek], Measure.[BOD Prod SET W Sub_BOD Valid], Measure.[BOD Prod SET W Sub_Endweek], Measure.[BOD Prod SET W Sub_Priority Endweek], Measure.[BOD Prod SET W Sub_Priority Startweek], Measure.[BOD Prod SET W Sub_Shipment LT Endweek], Measure.[BOD Prod SET W Sub_Shipment LT Startweek], Measure.[BOD Prod SET W Sub_Startweek],Measure.[BOD Prod SET W Sub_Time Phased Prty],Measure.[BOD Prod SET W Sub_Time Phased BOD LT],Measure.[BOD Prod SET W Sub_Time Phased Shipment LT] }) on column;
    - df_out_log
    - df_out_logDetail

* 데이타 초기화
    DELETE DATA FOR MODEL [BOD Product SET W] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [BOD Prod SET W Sub] where {Version.[Version Name].[CWV_MP]};


* RUN 스크립트
    EXEC plugin instance [PY_UI_BODProductSetW] for measures {[BOD Prod SET W_BOD LT]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (paramOutVersion,"CWV_MP"), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


* Output Query

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
str_instance = 'PY_UI_BODProductSetW'
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
            df_in_BODProdSET = read_csv_file('df_in_BODProdSET')
            df_in_ProductSetW = read_csv_file('df_in_ProductSetW_Ver01')
            df_in_MDMHorizon = read_csv_file('df_in_MDMHorizon')
            df_in_TimeWeek = read_csv_file('df_in_TimeWeek')

        dataframes = {
            'df_in_BODProdSET': df_in_BODProdSET,
            'df_in_ProductSetW': df_in_ProductSetW,
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

        Version_COLUMN = 'Version.[Version Name]'
        Item_Product_COLUMN = 'Item.[Product]'
        Item_Product_Group_COKUMN = 'Item.[Product Group]'
        Location_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        Trans_Mode_COLUMN = 'Trans Mode.[Trans Mode]'
        TimeDayKey_COLUMN = 'Time.[DayKey]'
        TimeDay_COLUMN = 'Time.[Day]'
        TimeWeekKey_COLUMN = 'Time.[WeekKey]'
        TimeWeek_COLUMN = 'Time.[Week]'

        BOD_Prod_SET_W_Shipment_LT = 'BOD Prod SET W_Shipment LT'
        BOD_Prod_SET_W_BOD_LT = 'BOD Prod SET W_BOD LT'
        BOD_Prod_SET_W_Priority = 'BOD Prod SET W_Priority'

        BOD_Prod_SET_W_Sub_Enddate = 'BOD Prod SET W Sub_Enddate'
        BOD_Prod_SET_W_Sub_Endweek = 'BOD Prod SET W Sub_Endweek'
        BOD_Prod_SET_W_Sub_Priority_Endweek = 'BOD Prod SET W Sub_Priority Endweek'
        BOD_Prod_SET_W_Sub_BOD_LT_Endweek = 'BOD Prod SET W Sub_BOD LT Endweek'
        BOD_Prod_SET_W_Sub_Shipment_LT_Endweek = 'BOD Prod SET W Sub_Shipment LT Endweek'
        BOD_Prod_SET_W_Sub_Startdate = 'BOD Prod SET W Sub_Startdate'
        BOD_Prod_SET_W_Sub_Startweek = 'BOD Prod SET W Sub_Startweek'
        BOD_Prod_SET_W_Sub_Priority_Startweek = 'BOD Prod SET W Sub_Priority Startweek'
        BOD_Prod_SET_W_Sub_BOD_LT_Startweek = 'BOD Prod SET W Sub_BOD LT Startweek'
        BOD_Prod_SET_W_Sub_Shipment_LT_Startweek = 'BOD Prod SET W Sub_Shipment LT Startweek'
        BOD_Prod_SET_W_Sub_BOD_Valid = 'BOD Prod SET W Sub_BOD Valid'
        BOD_Prod_SET_W_Sub_Time_Phased_Prty = 'BOD Prod SET W Sub_Time Phased Prty'
        BOD_Prod_SET_W_Sub_Time_Phased_BOD_LT = 'BOD Prod SET W Sub_Time Phased BOD LT'
        BOD_Prod_SET_W_Sub_Time_Phased_Shipment_LT = 'BOD Prod SET W Sub_Time Phased Shipment LT'

        BOD_Prod_SET_BOD_LT = 'BOD Prod SET_BOD LT'
        BOD_Prod_SET_BOD_Valid = 'BOD Prod SET_BOD Valid'
        BOD_Prod_SET_Created_By = 'BOD Prod SET_Created By'
        BOD_Prod_SET_Creation_Time = 'BOD Prod SET_Creation Time'
        BOD_Prod_SET_Eff_Enddate = 'BOD Prod SET_Eff Enddate'
        BOD_Prod_SET_Eff_Endweek = 'BOD Prod SET_Eff Endweek'
        BOD_Prod_SET_Eff_Startdate = 'BOD Prod SET_Eff Startdate'
        BOD_Prod_SET_Eff_Startweek = 'BOD Prod SET_Eff Startweek'
        BOD_Prod_SET_Lock_Flag = 'BOD Prod SET_Lock Flag'
        BOD_Prod_SET_Master_Ship_LT = 'BOD Prod SET_Master Ship LT'
        BOD_Prod_SET_Priority = 'BOD Prod SET_Priority'
        BOD_Prod_SET_Shipment_LT = 'BOD Prod SET_Shipment LT'
        BOD_Prod_SET_Time_Phased_BOD_LT = 'BOD Prod SET_Time Phased BOD LT'
        BOD_Prod_SET_Time_Phased_Prty = 'BOD Prod SET_Time Phased Prty'
        BOD_Prod_SET_Time_Phased_Shipment_LT = 'BOD Prod SET_Time Phased Shipment LT'
        BOD_Prod_SET_Update_Time = 'BOD Prod SET_Update Time'
        BOD_Prod_SET_Updated_By = 'BOD Prod SET_Updated By'
        BOD_Prod_Set_Master_Tran_Time = 'BOD Prod Set_Master Tran Time'

        Key_On = 'Key_on'

        fn_columns = [Version_COLUMN, Item_Product_COLUMN]

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # df_in_MDMHorizon 주차 리스트 설정
        TimeWeek_list = df_in_MDMHorizon[TimeWeek_COLUMN].unique().tolist()

        # df_in_BODProdSET 의 df_in_MDMHorizon주차로 확장
        df_in_BODProdSET[TimeWeek_COLUMN] = df_in_BODProdSET.apply(lambda x: TimeWeek_list, axis=1)
        df_in_BODProdSET = df_in_BODProdSET.explode(TimeWeek_COLUMN)

        # 공통 Grain 설정
        Grain_columns = [Version_COLUMN, Item_Product_Group_COKUMN, Location_COLUMN,
                         SUB_LOCATION_COLUMN, Trans_Mode_COLUMN, TimeWeek_COLUMN]

        # df_in_ProductSetW의 중복 삭제
        df_in_ProductSetW_temp = df_in_ProductSetW[Grain_columns].drop_duplicates()

        # df_in_ProductSetW의 Index 설정
        df_in_ProductSetW_index = df_in_ProductSetW_temp.set_index(Grain_columns).index

        # df_in_BODProductSet 의 중복 삭제
        df_in_BODProductSet_index_temp = df_in_BODProdSET[Grain_columns].drop_duplicates()

        # df_in_BODProductSet의 Index 설정
        df_in_BODProductSet_index = df_in_BODProductSet_index_temp[Grain_columns].index

        # 포함되지 않는 데이터 필터링
        df_in_BODProductSet_index_temp = df_in_BODProductSet_index_temp[
            ~df_in_BODProductSet_index.isin(df_in_ProductSetW_index)]

        print_df(df_in_BODProductSet_index_temp, 'df_in_BODProductSet_index_temp Filter 전 ', True)

        # df_in_BODProductSet 에 df_in_BODProductSet_temp 필터링 된 데이터 추출
        df_in_BODProductSet_temp = df_in_BODProdSET[
            df_in_BODProdSET[Grain_columns].apply(tuple, axis=1).isin(
                df_in_BODProductSet_index_temp.apply(tuple, axis=1))]

        print_df(df_in_BODProductSet_temp, 'df_in_BODProductSet_temp Filter 후 ', True)

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP4 Start : input data machining')

        # Start & End 날짜를 설정하기 위해 기간의 min / max 값 찾기
        MDM_start_date = pd.to_datetime(df_in_MDMHorizon[TimeDay_COLUMN].min()).strftime('%Y-%m-%d')
        MDM_end_date = pd.to_datetime(df_in_MDMHorizon[TimeDay_COLUMN].max()).strftime('%Y-%m-%d')
        MDM_start_week = df_in_MDMHorizon[TimeWeek_COLUMN].min()
        MDM_end_week = df_in_MDMHorizon[TimeWeek_COLUMN].max()

        note(f" MDM_start_week : {MDM_start_week}, MDM_end_week : {MDM_end_week}")

        # TimeWeek & TimdDay Dic으로 만들기
        weekday_dic = dict(zip(df_in_TimeWeek[TimeDay_COLUMN], df_in_TimeWeek[TimeWeek_COLUMN]))

        # BOD_Item_Eff_Startdate / BOD_Item_Eff_Enddate NaN 값 채우기
        df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Startdate] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Startdate].fillna(
            MDM_start_date)
        df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Enddate] = df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Enddate].fillna(
            MDM_end_date)

        print_df(df_in_BODProductSet_temp, 'df_in_BODProductSet_temp', True)


        # 날짜 타입 변경을 위한 함수 및 변경
        def covert_to_date(str):
            return pd.to_datetime(str, errors='coerce').strftime('%Y-%m-%d')


        df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Startdate] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Startdate].apply(
            covert_to_date)
        df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Enddate] = df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Enddate].apply(
            covert_to_date)

        print_df(df_in_BODProductSet_temp, 'df_in_BODProductSet_temp', True)

        # df_in_MDMHorizon에 포함된 날짜만 filtering
        df_in_BODProductSet_temp = df_in_BODProductSet_temp[
            (df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Startdate] >= MDM_start_date) | (
                    df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Enddate] <= MDM_end_date)]
        # # BOD_Prod_SET_Eff_Enddate 가 start_date 보다 작은 것 제외
        # df_in_BODProductSet_temp = df_in_BODProductSet_temp[
        #     df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Startdate] >= MDM_start_date]

        # 날짜를 주차로 변경
        df_in_BODProductSet_temp['Start_week'] = df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Startdate].map(weekday_dic)
        df_in_BODProductSet_temp['End_week'] = df_in_BODProductSet_temp[BOD_Prod_SET_Eff_Enddate].map(weekday_dic)

        print_df(df_in_BODProductSet_temp, 'df_in_BODProductSet_temp - 주차로 변환', True)

        # Start_week , End_week NAN 값 채우기
        df_in_BODProductSet_temp['Start_week'] = df_in_BODProductSet_temp['Start_week'].fillna(MDM_start_week)
        df_in_BODProductSet_temp['End_week'] = df_in_BODProductSet_temp['End_week'].fillna(MDM_end_week)

        print_df(df_in_BODProductSet_temp, 'df_in_BODProductSet_temp - 주차 NAN 채우기', True)

        # 기간 설정을 위한 데이터 타입 변경
        df_in_BODProductSet_temp['Start_week'] = df_in_BODProductSet_temp['Start_week'].astype(int)
        df_in_BODProductSet_temp['End_week'] = df_in_BODProductSet_temp['End_week'].astype(int)

        df_in_BODProductSet_temp[TimeWeek_COLUMN] = df_in_BODProductSet_temp[TimeWeek_COLUMN].astype(int)

        # MDMHorizon 기간에 걸리지 않는 값들 0으로 처리
        if df_in_BODProductSet_temp[BOD_Prod_SET_Shipment_LT].empty:
            pass
        else:
            df_in_BODProductSet_temp[BOD_Prod_SET_Shipment_LT] = np.where(
                ((df_in_BODProductSet_temp[TimeWeek_COLUMN] >= df_in_BODProductSet_temp['Start_week']) &
                 (df_in_BODProductSet_temp[TimeWeek_COLUMN] <= df_in_BODProductSet_temp['End_week'])),
                df_in_BODProductSet_temp[BOD_Prod_SET_Shipment_LT], 0)

        if df_in_BODProductSet_temp[BOD_Prod_SET_BOD_LT].empty:
            pass
        else:
            df_in_BODProductSet_temp[BOD_Prod_SET_BOD_LT] = np.where(
                ((df_in_BODProductSet_temp[TimeWeek_COLUMN] >= df_in_BODProductSet_temp['Start_week']) &
                 (df_in_BODProductSet_temp[TimeWeek_COLUMN] <= df_in_BODProductSet_temp['End_week'])),
                df_in_BODProductSet_temp[BOD_Prod_SET_BOD_LT], 0)

        ########################## Default 값 설정 (BOD_Prod_SET_Priority 추가 ) 2025.08.08 , ybest7 ########################
        if df_in_BODProductSet_temp[BOD_Prod_SET_Priority].empty:
            pass
        else:
            df_in_BODProductSet_temp[BOD_Prod_SET_Priority] = np.where(
                ((df_in_BODProductSet_temp[TimeWeek_COLUMN] >= df_in_BODProductSet_temp['Start_week']) &
                 (df_in_BODProductSet_temp[TimeWeek_COLUMN] <= df_in_BODProductSet_temp['End_week'])),
                df_in_BODProductSet_temp[BOD_Prod_SET_Priority], 0)
        #################################################################################################################
        # ########################## Default 값 설정 (UI - Active Rule 사용) 2025.05.14 , ybest7 #######################
        #
        # ########################## Default 값 설정 df_out_ProductSetWSub 추가  2025.08.08 , ybest7 #########################
        #
        # # df_out_ProductSetWSub 추가를 위해 df_in_BODProductSet_temp 복사
        # df_out_ProductSetWSub = df_in_BODProductSet_temp.copy()
        # # 필요한 컬럼 설정
        # df_out_ProductSetWSub = df_out_ProductSetWSub[[
        #     Version_COLUMN, Location_COLUMN, Item_Product_Group_COKUMN, SUB_LOCATION_COLUMN, Trans_Mode_COLUMN,
        #     BOD_Prod_SET_Eff_Endweek, BOD_Prod_SET_Eff_Startweek]]
        # # # column 명 변경
        # # df_out_ProductSetWSub = df_out_ProductSetWSub.rename(columns={
        # #     BOD_Prod_SET_Eff_Enddate : BOD_Prod_SET_W_Sub_Enddate, 'End_week' : BOD_Prod_SET_W_Sub_Endweek,
        # #     BOD_Prod_SET_Eff_Startdate : BOD_Prod_SET_W_Sub_Startdate , 'Start_week' : BOD_Prod_SET_W_Sub_Startweek})
        #
        # ####################################################################### 2025-09-09 ybest7.park 수정 #################
        # ######################################### BOD_Prod_SET_Eff_Endweek & BOD_Prod_SET_Eff_Startweek 값 적용 #############
        # column 데이터 타입 변경
        # column 데이터 타입 변경
        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_Shipment_LT_Endweek] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Endweek].fillna('null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_BOD_LT_Endweek] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Endweek].fillna('null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_Priority_Endweek] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Endweek].fillna('Null').astype(str).str.replace(r'\.0$', '', regex=True)

        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_Priority_Startweek] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Startweek].fillna('Null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_BOD_LT_Startweek] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Startweek].fillna('Null').astype(str).str.replace(r'\.0$', '', regex=True)
        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_Shipment_LT_Startweek] = df_in_BODProductSet_temp[
            BOD_Prod_SET_Eff_Startweek].fillna('Null').astype(str).str.replace(r'\.0$', '', regex=True)

        ############################### 2025-12-02 수정 ################################################################
        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_Time_Phased_Prty] = np.where(
            df_in_BODProductSet_temp[BOD_Prod_SET_Time_Phased_Prty].isnull(), 'N',
            df_in_BODProductSet_temp[BOD_Prod_SET_Time_Phased_Prty])

        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_Time_Phased_BOD_LT] = np.where(
            df_in_BODProductSet_temp[BOD_Prod_SET_Time_Phased_BOD_LT].isnull(), 'N',
            df_in_BODProductSet_temp[BOD_Prod_SET_Time_Phased_BOD_LT])

        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_Time_Phased_Shipment_LT] = np.where(
            df_in_BODProductSet_temp[BOD_Prod_SET_Time_Phased_Shipment_LT].isnull(), 'N',
            df_in_BODProductSet_temp[BOD_Prod_SET_Time_Phased_Shipment_LT])

        df_in_BODProductSet_temp[BOD_Prod_SET_W_Sub_BOD_Valid] = np.where(
            df_in_BODProductSet_temp[BOD_Prod_SET_BOD_Valid].isnull(), 'N',
            df_in_BODProductSet_temp[BOD_Prod_SET_BOD_Valid])

        df_out_BODProductSet_temp = df_in_BODProductSet_temp.copy()

        # 필요한 컬럼 설정
        df_out_BODProductSet_temp = df_out_BODProductSet_temp[[
            Version_COLUMN, Location_COLUMN, Item_Product_Group_COKUMN, SUB_LOCATION_COLUMN, Trans_Mode_COLUMN,
            BOD_Prod_SET_W_Sub_Shipment_LT_Endweek, BOD_Prod_SET_W_Sub_BOD_LT_Endweek,
            BOD_Prod_SET_W_Sub_Priority_Endweek, BOD_Prod_SET_W_Sub_Time_Phased_Prty,
            BOD_Prod_SET_W_Sub_Priority_Startweek, BOD_Prod_SET_W_Sub_BOD_LT_Startweek,
            BOD_Prod_SET_W_Sub_Shipment_LT_Startweek,BOD_Prod_SET_W_Sub_BOD_Valid,
            BOD_Prod_SET_W_Sub_Time_Phased_Prty, BOD_Prod_SET_W_Sub_Time_Phased_BOD_LT,
            BOD_Prod_SET_W_Sub_Time_Phased_Shipment_LT]]

        df_out_BODProductSet_temp = df_out_BODProductSet_temp.drop_duplicates()


        # # 불필요한 컬럼 삭제
        # df_out_ProductSetWSub = df_out_ProductSetWSub.drop(
        #     columns=[BOD_Prod_SET_Eff_Endweek, BOD_Prod_SET_Eff_Startweek], axis=1)

        # df_out_ProductSetWSub 추가를 위해 df_in_BODProductSet_temp 복사
        df_out_ProductSetWSub = df_out_BODProductSet_temp.copy()

        df_out_ProductSetWSub = df_out_ProductSetWSub.drop_duplicates()


        # ############################################ 2025-11-27 ybest7.park 수정 ####################################
        # # df_in_BODProdSETNValid 데이터 테이블을 df_out_ProductSetW 에 업데이트 BOD Prod SET W Sub_BOD Valid 값 'N'으로 설정
        #
        # # Key가 되는 그래인의 중복 삭제
        # df_in_BODProdSETNValid = df_in_BODProdSETNValid[
        #     [Version_COLUMN, Location_COLUMN, Item_Product_Group_COKUMN, SUB_LOCATION_COLUMN,
        #      Trans_Mode_COLUMN]].drop_duplicates()
        # # BOD_Prod_SET_W_Sub_BOD_Valid 값 Update 'N'
        # df_in_BODProdSETNValid[[BOD_Prod_SET_W_Sub_Time_Phased_Prty, BOD_Prod_SET_W_Sub_Time_Phased_BOD_LT,
        #                        BOD_Prod_SET_W_Sub_Time_Phased_Shipment_LT]] = "N"
        #
        # print_df(df_in_BODProdSETNValid, 'df_in_BODProdSETNValid 데이터 확인')
        #
        # df_out_ProductSetWSub = pd.concat([df_out_ProductSetWSub,df_in_BODProdSETNValid], axis=0)
        #
        #
        # print_df(df_out_ProductSetWSub, 'df_out_ProductSetWSub 데이터 확인 ', True)
        #
        # #################################################################################################################
        ########################## Default 값 설정 (UI - Active Rule 사용) 2025.05.14 , ybest7 #######################

        df_in_BODProductSet_temp = df_in_BODProductSet_temp.rename(
            columns={BOD_Prod_SET_Shipment_LT: BOD_Prod_SET_W_Shipment_LT,
                     BOD_Prod_SET_BOD_LT: BOD_Prod_SET_W_BOD_LT,
                     BOD_Prod_SET_Priority: BOD_Prod_SET_W_Priority})  # 2025-08-08 BOD_Prod_SET_W_Priority 추가

        df_in_BODProductSet_temp = df_in_BODProductSet_temp[
            [Version_COLUMN, Item_Product_Group_COKUMN, TimeWeek_COLUMN, Location_COLUMN, SUB_LOCATION_COLUMN,
             Trans_Mode_COLUMN,
             BOD_Prod_SET_W_Priority, BOD_Prod_SET_W_Shipment_LT,
             BOD_Prod_SET_W_BOD_LT]]  # 2025-08-08 BOD_Prod_SET_W_Priority 추가


        df_out_ProductSetW = df_in_BODProductSet_temp.copy()

        print_df(df_out_ProductSetW, 'df_out_ProductSetW 값 변경 후 ', True)

        step('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_ProductSetW, 'df_out_ProductSetW', True)
            print_df(df_out_ProductSetWSub, 'df_out_ProductSetWSub', True)

        print_df(df_out_ProductSetW, 'df_out_ProductSetW', True)
        print_df(df_out_ProductSetWSub, 'df_out_ProductSetWSub', True)

        row_count, col_count = df_out_ProductSetW.shape
        note(f'=====> Final df_out_ProductSetW rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_ProductSetWSub.shape
        note(f'=====> Final df_out_ProductSetWSub rows : {row_count} , Columns : {col_count}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ProductSetW = pd.DataFrame([], columns=[])
        df_out_ProductSetWSub = pd.DataFrame([], columns=[])

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
