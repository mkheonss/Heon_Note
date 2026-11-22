"""
* 프로그램명
    - PY_UI_SOPVolatilityUpdate

* 내용
    - SOP Volatility SET Measure에 Sync Plan Data

* 변경이력
    - 2025.03.09 / 황수혁 / Create

* Flow Summary
    SOP Volatility Set Measure Data 생성

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP

* Input Tables
    - df_in_Week : select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(17).Key) * [Time].[Planning Month]) orderby [Time].[Week].Key ;
    - df_in_Month: select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-10).Key && #.Key < &CurrentWeek.element(0).LeadOffset(27).Key) * [Time].[Planning Month]);

    - df_in_CWVTypeInfo : select (&MPV.relatedmembers([Version Type]));
    - df_in_SOPVolatility : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [Category].[Category] * [Compare With].[Compare With] * [Analysis Object].[Analysis Object] * [Analysis Method].[Analysis Method].[PSI] ) on row, ({Measure.[SOP Volatility SET_Volatility]}) on column;

    - df_in_SOPAdjustSET_SOPW : Select ([Version].[Version Name] * Item.[Item] * Location.[Location] * [To Location].[To Location] * [To Time].[To Week]) on row, ({Measure.[SOP W_SET MFG Chg Qty]}) on column;
    - df_in_SOPAdjustLCM_SOPW : Select ([Version].[Version Name] * [To Item].[To Item] * [Sub Location].[Sub Location] * [Location].[Location] * [Week2].[Week2]) on row, ({Measure.[SOP W_LCM MFG Chg Qty]}) on column;
    - df_in_SOPAdjustSET_MFGW : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [To Location].[To Location] * [Time].[Week]) on row, ({Measure.[SOP Adjust SET W_Chg Qty]}) on column;

* Output Tables :
    -  df_out_SOPVolatility

* 테스트 스크립트
    - EXEC plugin instance [PY_UI_SOPVolatilityUpdate] for Measures {[SOP Volatility SET_Volatility]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
        - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [Category].[Category] * [Compare With].[Compare With] * [Analysis Object].[Analysis Object] * [Analysis Method].[Analysis Method] ) on row,
    ({Measure.[SOP Volatility SET_Volatility]}) on column;

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
str_instance = 'PY_UI_SOPVolatilityUpdate'
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


class NotSync(Exception):
    def __init__(self, message='Sync 버전만 실행 됨'):
        self.message = message


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
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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
    """실행 시간을 계산하고, 분 또는 초 단위로 반환.
    초 단위가 0일 경우 초로 표시하고, 그 외에는 분으로 표시."""
    elapsed = time.time() - start_time
    if elapsed < 60:  # 1분 미만일 경우
        return str(round(elapsed, 2)) + " seconds"
    else:
        return str(round(elapsed / 60, 2)) + " minutes"


def filter_week_range(df, column_name, min_value=0, max_value=16, current_week=None, week_column=None):
    """
    주어진 컬럼의 값이 지정된 범위 내에 있는 데이터를 필터링합니다.

    Args:
        df (pd.DataFrame): 필터링할 데이터프레임
        column_name (str): 필터링 기준 컬럼명
        min_value (int): 최소값 (포함)
        max_value (int): 최대값 (포함)
        current_week (str, optional): 현재 주 기준값
        week_column (str, optional): 주 데이터가 있는 컬럼명

    Returns:
        pd.DataFrame: 필터링된 데이터프레임

    """
    mask = df[column_name].between(min_value, max_value, inclusive='both')
    if current_week is not None and week_column is not None:
        mask &= df[week_column] >= current_week

    return df[mask].copy()


def format_week_rank(week_rank_series):
    """주 순위를 'W-XX' 형식의 문자열로 변환

    Args:
        week_rank_series (pandas.Series): 주 순위 데이터

    Returns:
        pandas.Series: 'W-XX' 형식으로 포맷된 문자열 시리즈
    """
    return 'W-' + week_rank_series.astype(str).str.pad(width=2, side='left', fillchar='0')



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
            df_in_Week = read_csv_file("df_in_Week")
            df_in_2YearAgoWeek = read_csv_file("df_in_2YearAgoWeek")
            df_in_Month = read_csv_file("df_in_Month")

            df_in_CWVTypeInfo = read_csv_file("df_in_CWVTypeInfo")
            df_in_SOPVolatility = read_csv_file("df_in_SOPVolatility")
            df_in_SOPAdjustSET_SOPW = read_csv_file("df_in_SOPAdjustSET_SOPW")
            df_in_SOPAdjustLCM_SOPW = read_csv_file("df_in_SOPAdjustLCM_SOPW")
            df_in_SOPAdjustSET_MFGW = read_csv_file("df_in_SOPAdjustSET_MFGW")

        dataframes = {
            'df_in_Week': df_in_Week,
            'df_in_2YearAgoWeek': df_in_2YearAgoWeek,
            'df_in_Month': df_in_Month,
            'df_in_CWVTypeInfo': df_in_CWVTypeInfo,
            'df_in_SOPVolatility': df_in_SOPVolatility,
            'df_in_SOPAdjustSET_SOPW': df_in_SOPAdjustSET_SOPW,
            'df_in_SOPAdjustLCM_SOPW': df_in_SOPAdjustLCM_SOPW,
            'df_in_SOPAdjustSET_MFGW': df_in_SOPAdjustSET_MFGW,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        VERSION_TYPE_COLUMN = 'Version.[Version Type]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        SOP_W_SET_MFG_CHG_QTY_COLUMN = 'SOP W_SET MFG Chg Qty'
        SOP_W_LCM_MFG_CHG_QTY_COLUMN = 'SOP W_LCM MFG Chg Qty'
        CHG_COLUMN = 'Chg'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_MONTH_COLUMN = 'Time.[Month]'
        TIME_PLANNING_MONTH_COLUMN = 'Time.[Planning Month]'
        CATEGORY_CATEGORY_COLUMN = 'Category.[Category]'
        ANALYSIS_OBJECT_COLUMN = 'Analysis Object.[Analysis Object]'
        ANALYSIS_METHOD_COLUMN = 'Analysis Method.[Analysis Method]'
        COMPARE_WITH_COLUMN = 'Compare With.[Compare With]'
        SOP_VOLATILITY_SET_VOLATILITY_COLUMN = 'SOP Volatility SET_Volatility'
        TO_ITEM_COLUMN = 'To Item.[To Item]'
        ITEM_COLUMN = 'Item.[Item]'
        TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        SOP_ADJUST_SET_W_CHG_QTY_COLUMN = 'SOP Adjust SET W_Chg Qty'

        step('=====> STEP2 End')


        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        VAL_VERSION_TYPE = str(get_first_value(df_in_CWVTypeInfo, VERSION_TYPE_COLUMN) or '')
        step(f'=====> VAL_VERSION_TYPE : {VAL_VERSION_TYPE}')

        if VAL_VERSION_TYPE != 'Sync':
            raise CustomException(f'STEP3 .... Version.[Version Type] 이 Sync 인 경우만 실행 됩니다. 현재값 :{VAL_VERSION_TYPE}')


        df_in_Week['Week Rank'] = (
            df_in_Week[TIME_WEEK_COLUMN]
            .rank(method='first')  # 동일한 값이 있을 경우 먼저 나타나는 순서대로 순위 부여
            .sub(1)                # 1을 빼는 연산
            .astype(int)           # 정수형으로 변환
        )

        columns = [TIME_WEEK_COLUMN, TIME_PLANNING_MONTH_COLUMN]
        df_in_Week[columns] = df_in_Week[columns].astype('str')

        VAL_CURRENTWEEK = str(get_first_value(df_in_Week, TIME_WEEK_COLUMN) or '')
        step(f'=====> VAL_CURRENTWEEK : {VAL_CURRENTWEEK}')

        df_in_Month.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            TIME_PLANNING_MONTH_COLUMN: TIME_MONTH_COLUMN,
        }, inplace=True)
        df_in_Month['Week Rank'] = df_in_Month[TIME_WEEK_COLUMN].rank()
        df_in_Month['FirstWeek'] = df_in_Month.groupby([TIME_MONTH_COLUMN], sort=False, as_index=False)[TIME_WEEK_COLUMN].transform('min').astype('Int64')
        df_in_Month['FirstWeek Rank'] = df_in_Month['FirstWeek'].rank(method='min', ascending=True).astype('Int64')
        df_in_Month['LastWeek'] = df_in_Month.groupby([TIME_MONTH_COLUMN], sort=False, as_index=False)[TIME_WEEK_COLUMN].transform('max').astype('Int64')
        df_in_Month['LastWeek Rank'] = df_in_Month['LastWeek'].rank(method='max', ascending=True).astype('Int64')

        columns = [TIME_WEEK_COLUMN, TIME_MONTH_COLUMN, 'FirstWeek', 'LastWeek']
        df_in_Month[columns] = df_in_Month[columns].astype('str')

        current_week_data = df_in_Month.loc[df_in_Month[TIME_WEEK_COLUMN] == VAL_CURRENTWEEK]
        df_in_Month['Current Week'] = current_week_data[TIME_WEEK_COLUMN].iloc[0]
        df_in_Month['Current Week Rank'] = current_week_data['Week Rank'].iloc[0]
        df_in_Month[['FirstWeekDiff', 'LastWeekDiff']] = df_in_Month[['FirstWeek Rank', 'LastWeek Rank']].sub(
            pd.to_numeric(df_in_Month['Current Week Rank'], errors='coerce').astype('Int64'), axis=0
        )


        colunms = ['FirstWeekDiff', 'LastWeekDiff']
        df_in_Month[colunms] = df_in_Month[colunms].astype('Int64')
        df_in_Month[TIME_WEEK_COLUMN] = df_in_Month[TIME_WEEK_COLUMN].astype('str')


        # 변수 선언
        VAL_2YEARS_AGO_WEEK = str(get_first_value(df_in_2YearAgoWeek, TIME_WEEK_COLUMN))
        step(f'=====> VAL_2YEARS_AGO_WEEK : {VAL_2YEARS_AGO_WEEK}')


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        # STEP 1.0 : df_SOPAdjust 데이터 처리
        step('=====> STEP4 by 1.0 Start : df_SOPAdjust 데이터 처리')

        #--------------------------------------------------------------------------------------------------------------- df_in_SOPAdjustSET_SOPW
        df_SOPAdjust_Temp = df_in_SOPAdjustSET_SOPW[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN, SOP_W_SET_MFG_CHG_QTY_COLUMN,
        ]].copy()
        columns_defaults = {
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
            ANALYSIS_OBJECT_COLUMN: 'SET SOP',
            CATEGORY_CATEGORY_COLUMN: 'SOP WEEK_Actual Result',
        }
        df_SOPAdjust_Temp = df_SOPAdjust_Temp.assign(**columns_defaults)
        df_SOPAdjust_Temp.rename(columns={
            TO_TIME_TO_WEEK_COLUMN: TIME_WEEK_COLUMN,
            SOP_W_SET_MFG_CHG_QTY_COLUMN : CHG_COLUMN,
        }, inplace=True)
        df_SOPAdjust_Temp[TO_ITEM_COLUMN] = df_SOPAdjust_Temp[ITEM_COLUMN]
        print_df(df_SOPAdjust_Temp, 'STEP4 by 1.1.1 ____ df_SOPAdjust_Temp .... select')

        #SOP WEEK_Actual Result
        df_SOPAdjust = df_SOPAdjust_Temp[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN, CATEGORY_CATEGORY_COLUMN,
            TIME_WEEK_COLUMN, CHG_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
        ]].copy()

        #SOP WEEK_Final Plan(복제)
        df_SOPAdjust_Temp[CATEGORY_CATEGORY_COLUMN] = 'SOP WEEK_Final Plan'
        df_SOPAdjust = pd.concat([df_SOPAdjust, df_SOPAdjust_Temp], axis=0)
        print_df(df_SOPAdjust_Temp, 'STEP4 by 1.1.2 ____ df_SOPAdjust_Temp .... create')

        #--------------------------------------------------------------------------------------------------------------- df_in_SOPAdjustLCM_SOPW
        df_SOPAdjust_Temp = df_in_SOPAdjustLCM_SOPW[[
            VERSION_NAME_COLUMN, TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN, WEEK2_COLUMN, SOP_W_LCM_MFG_CHG_QTY_COLUMN,
        ]].copy()
        columns_defaults = {
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
            ANALYSIS_OBJECT_COLUMN: 'LCM SOP',
            CATEGORY_CATEGORY_COLUMN: 'SOP WEEK_Actual Result',
        }
        df_SOPAdjust_Temp = df_SOPAdjust_Temp.assign(**columns_defaults)
        df_SOPAdjust_Temp.rename(columns={
            WEEK2_COLUMN: TIME_WEEK_COLUMN,
            SOP_W_LCM_MFG_CHG_QTY_COLUMN : CHG_COLUMN,
            TO_ITEM_COLUMN: ITEM_COLUMN,
            LOCATION_COLUMN: TO_LOCATION_COLUMN,
            SUB_LOCATION_COLUMN: LOCATION_COLUMN
        }, inplace=True)
        df_SOPAdjust_Temp[TO_ITEM_COLUMN] = df_SOPAdjust_Temp[ITEM_COLUMN]

        df_SOPAdjust_Temp = df_SOPAdjust_Temp[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN, CATEGORY_CATEGORY_COLUMN,
            TIME_WEEK_COLUMN, CHG_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
        ]].copy()
        print_df(df_SOPAdjust_Temp, 'STEP4 by 1.1.3 ____ df_SOPAdjust_Temp .... select')

        #SOP WEEK_Actual Result
        df_SOPAdjust = pd.concat([df_SOPAdjust, df_SOPAdjust_Temp], axis=0)

        #SOP WEEK_Final Plan(복제)
        df_SOPAdjust_Temp[CATEGORY_CATEGORY_COLUMN] = 'SOP WEEK_Final Plan'
        df_SOPAdjust = pd.concat([df_SOPAdjust, df_SOPAdjust_Temp], axis=0)
        print_df(df_SOPAdjust, 'STEP4 by 1.1.4 ____ df_SOPAdjust .... create')


        # --------------------------------------------------------------------------------------------------------------- df_in_SOPAdjustSET_MFGW
        df_SOPAdjust_Temp = df_in_SOPAdjustSET_MFGW[[
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_ADJUST_SET_W_CHG_QTY_COLUMN,
        ]].copy()
        columns_defaults = {
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
            ANALYSIS_OBJECT_COLUMN: 'SET SOP',
            CATEGORY_CATEGORY_COLUMN: 'MFG WEEK_Actual Result',
        }
        df_SOPAdjust_Temp = df_SOPAdjust_Temp.assign(**columns_defaults)
        df_SOPAdjust_Temp.rename(columns={
            SOP_ADJUST_SET_W_CHG_QTY_COLUMN: CHG_COLUMN,
        }, inplace=True)
        df_SOPAdjust_Temp[TO_ITEM_COLUMN] = df_SOPAdjust_Temp[ITEM_COLUMN]

        df_SOPAdjust_Temp = df_SOPAdjust_Temp[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN, CATEGORY_CATEGORY_COLUMN,
            TIME_WEEK_COLUMN, CHG_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
        ]].copy()

        # SOP WEEK_Actual Result
        df_SOPAdjust = pd.concat([df_SOPAdjust, df_SOPAdjust_Temp], axis=0)
        print_df(df_SOPAdjust, 'STEP4 by 1.1.5 ____ df_SOPAdjust .... create')

        # SOP WEEK_Final Plan(복제)
        df_SOPAdjust_Temp[CATEGORY_CATEGORY_COLUMN] = 'MFG WEEK_Final Plan'
        df_SOPAdjust = pd.concat([df_SOPAdjust, df_SOPAdjust_Temp], axis=0)
        df_SOPAdjust[TIME_WEEK_COLUMN] = df_SOPAdjust[TIME_WEEK_COLUMN].astype(str)
        print_df(df_SOPAdjust, 'STEP4 by 1.1.6 ____ df_SOPAdjust .... create')

        step('=====> STEP4 by 1.0 End')



        # STEP 2.0 : df_SOPVolatility 데이터 처리
        step('=====> STEP4 by 2.0 Start : df_SOPVolatility 데이터 처리')

        df_SOPVolatilit = df_in_SOPVolatility[(df_in_SOPVolatility[ANALYSIS_OBJECT_COLUMN].isin(['SET MP', 'LCM MP']) )].copy()
        df_SOPVolatilit[ANALYSIS_OBJECT_COLUMN] = np.where(df_SOPVolatilit[ANALYSIS_OBJECT_COLUMN] == 'SET MP', 'SET SOP', 'LCM SOP')
        df_SOPVolatility = pd.concat([df_in_SOPVolatility, df_SOPVolatilit], axis = 0)

        step('=====> STEP4 by 2.0 End')



        # STEP 5.0 : df_out_SOPVolatility_Weekly 데이터 처리
        step('=====> STEP4 by 5.0 Start : df_out_SOPVolatility_Weekly 데이터 처리')

        df_SOPAdjust_Weekly = df_SOPAdjust.copy()
        df_SOPAdjust_Weekly[ANALYSIS_METHOD_COLUMN] = 'Weekly'
        df_Week  = df_in_Week[[TIME_WEEK_COLUMN, 'Week Rank']].copy()

        df_SOPAdjust_Weekly = pd.merge(df_SOPAdjust_Weekly, df_Week, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_SOPAdjust_Weekly[COMPARE_WITH_COLUMN] = format_week_rank(df_SOPAdjust_Weekly['Week Rank'])

        df_SOPAdjust_Weekly = df_SOPAdjust_Weekly.drop('Week Rank', axis=1, errors='ignore')
        print_df(df_SOPAdjust_Weekly, 'STEP4 by 5.1.1 ____ df_SOPAdjust_Weekly .... create')

        step('=====> STEP4 by 5.0 End')



        # STEP 6.0 : df_out_SOPVolatility_MonthlyF 데이터 처리
        step('=====> STEP4 by 6.0 Start : df_out_SOPVolatility_MonthlyF 데이터 처리')

        df_SOPAdjust_MonthlyF = df_SOPAdjust.copy()
        df_SOPAdjust_MonthlyF[ANALYSIS_METHOD_COLUMN] = 'Monthly_FirstWeek'
        df_SOPAdjust_MonthlyF[TIME_WEEK_COLUMN] = df_SOPAdjust_MonthlyF[TIME_WEEK_COLUMN].astype(str)

        # df_Month = df_in_Month[(df_in_Month['FirstWeekDiff'] >= 0) & (df_in_Month['FirstWeekDiff'] <= 16)].copy()
        df_Month = filter_week_range(
            df=df_in_Month,
            column_name='FirstWeekDiff',
        )
        df_Month = df_Month[[TIME_WEEK_COLUMN, 'FirstWeekDiff']]
        print_df(df_Month, 'STEP4 by 6.1.1 ____ _df_Month_First .... select')

        df_SOPAdjust_MonthlyF = pd.merge(df_SOPAdjust_MonthlyF, df_Month, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_SOPAdjust_MonthlyF[COMPARE_WITH_COLUMN] = format_week_rank(df_SOPAdjust_MonthlyF['FirstWeekDiff'])

        df_SOPAdjust_MonthlyF = df_SOPAdjust_MonthlyF.drop('FirstWeekDiff', axis=1, errors='ignore')
        print_df(df_SOPAdjust_MonthlyF, 'STEP4 by 6.1.2 ____ df_SOPAdjust_MonthlyF .... select')

        step('=====> STEP4 by 6.0 End')


        # STEP 7.0 : df_out_SOPVolatility_MonthlyL 데이터 처리
        step('=====> STEP4 by 7.0 Start : df_out_SOPVolatility_Monthly 데이터 처리')

        df_SOPAdjust_MonthlyL = df_SOPAdjust.copy()
        df_SOPAdjust_MonthlyL[ANALYSIS_METHOD_COLUMN] = 'Monthly_LastWeek'
        df_SOPAdjust_MonthlyL[TIME_WEEK_COLUMN] = df_SOPAdjust_MonthlyL[TIME_WEEK_COLUMN].astype(str)
        print_df(df_SOPAdjust_MonthlyL, 'STEP4 by 7.1.1 ____ df_SOPAdjust_MonthlyL .... create')

        # df_Month = df_in_Month[(df_in_Month['LastWeekDiff'] >= 0) & (df_in_Month['LastWeekDiff'] <= 16) & (df_in_Month[TIME_WEEK_COLUMN] >= VAL_CURRENTWEEK)].copy()
        df_Month = filter_week_range(
            df=df_in_Month,
            column_name='LastWeekDiff',
            current_week=VAL_CURRENTWEEK,
            week_column=TIME_WEEK_COLUMN,
        )
        df_Month = df_Month[[TIME_WEEK_COLUMN, 'LastWeekDiff']]
        print_df(df_Month, 'STEP4 by 7.1.2 ____ _df_Month_Last .... select')

        df_SOPAdjust_MonthlyL = pd.merge(df_SOPAdjust_MonthlyL, df_Month, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_SOPAdjust_MonthlyL[COMPARE_WITH_COLUMN] = format_week_rank(df_SOPAdjust_MonthlyL['LastWeekDiff'])

        df_SOPAdjust_MonthlyL = df_SOPAdjust_MonthlyL.drop('LastWeekDiff', axis=1, errors='ignore')
        print_df(df_SOPAdjust_MonthlyL, 'STEP4 by 7.1.3 ____ df_SOPAdjust_MonthlyL .... select')

        step('=====> STEP4 by 7.0 End')


        # STEP 8.0 : df_out_SOPVolatility 최종 Data 처리
        step('=====> STEP4 by 8.0 Start : df_out_SOPVolatility 최종 Data 처리')

        df_out_SOPAdjust = pd.concat([
            df_SOPAdjust, df_SOPAdjust_Weekly, df_SOPAdjust_MonthlyF, df_SOPAdjust_MonthlyL
        ], axis=0)

        df_SOPVolatility[TIME_WEEK_COLUMN] = df_SOPVolatility[TIME_WEEK_COLUMN].astype(str)
        df_out_SOPAdjust[TIME_WEEK_COLUMN] = df_out_SOPAdjust[TIME_WEEK_COLUMN].astype(str)

        df_out_SOPVolatility = pd.merge(df_SOPVolatility, df_out_SOPAdjust, how='left', suffixes=('', '_y'),
                                        on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_COLUMN,
                                            TO_ITEM_COLUMN, CATEGORY_CATEGORY_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN,
                                            ANALYSIS_METHOD_COLUMN])

        df_out_SOPVolatility.fillna({SOP_VOLATILITY_SET_VOLATILITY_COLUMN: 0, CHG_COLUMN : 0}, inplace=True)
        df_out_SOPVolatility[SOP_VOLATILITY_SET_VOLATILITY_COLUMN] = (df_out_SOPVolatility[SOP_VOLATILITY_SET_VOLATILITY_COLUMN] + df_out_SOPVolatility[CHG_COLUMN])
        df_out_SOPVolatility = df_out_SOPVolatility.drop(CHG_COLUMN, axis=1, errors='ignore')

        df_out_SOPVolatility = df_out_SOPVolatility.groupby([
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_COLUMN, TO_ITEM_COLUMN,
            CATEGORY_CATEGORY_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN, ANALYSIS_METHOD_COLUMN,
        ], sort=False, as_index=False)[SOP_VOLATILITY_SET_VOLATILITY_COLUMN].sum()
        print_df(df_out_SOPVolatility, 'STEP4 by 8.1.1 ____ df_out_SOPVolatility .... create')

        step('=====> STEP4 by 8.0 End')

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        dataframes = {
            'df_out_SOPVolatility': df_out_SOPVolatility,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')


    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPVolatility = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SOPVolatility = pd.DataFrame([], columns=[])
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
