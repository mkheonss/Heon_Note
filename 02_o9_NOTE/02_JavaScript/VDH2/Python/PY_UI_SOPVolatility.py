"""
* 프로그램명
    - PY_UI_SOPVolatility

* 내용
    - SOP Volatility SET, SOP Volatility Mtrl Measure Data 생성

* 변경이력
    - 2025.03.04 / 황수혁 / Create

* Flow Summary
    SOP Volatility(Set/Mtrl) Measure Data 생성

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
    - df_in_Week : select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(17).Key)) orderby [Time].[Week].Key ;
    - df_in_2YearAgoWeek : select ([Time].[Week].filter(#.Key == &CurrentWeek.element(0).LeadOffset(-105).Key)) orderby [Time].[Week].Key ;
    - df_in_Month: select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-10).Key && #.Key < &CurrentWeek.element(0).LeadOffset(27).Key) * [Time].[Planning Month]);

    - df_in_SOPVolatility_SET : Select (&LastWeekPlanTypeVersion * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [Category].[Category] * [Compare With].[Compare With] * [Analysis Object].[Analysis Object] * [Analysis Method].[Analysis Method] ) on row, ({Measure.[SOP Volatility SET_Volatility]}) on column;
    - df_in_SOPVolatility_Mtrl : Select (&LastWeekPlanTypeVersion * [Analysis Object].[Analysis Object] * [Analysis Method].[Analysis Method] * [Category].[Category] * [Item Material].[Item Material] * [Location].[Location] * [To Item].[To Item] * [To Location].[To Location] * [Compare With].[Compare With] * [Time].[Week] ) on row, ({Measure.[SOP Volatility Mtrl_Volatility]}) on column;
    - df_in_WMtrlConsQtyPlanOutput : Select (&MPV * [Item].[Item Type] * [Item].[Item] * [Time].[Week] * [Location].[Site Stage] * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity Type2] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,  ({Measure.[W Material Consumption Quantity Plan Output]}) on column;
    - df_in_BUPConsToConsOutput : Select (FROM.[Time].[Week] * FROM.[Item].[Item Type] * FROM.[Item].[Item] * FROM.[Location].[Site Stage] * FROM.[Location].[Location] * FROM.[Activity1].[Activity1] * from.[Activity2].[Activity Type2].[Manufacturing] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * TO.[To Time].[To Week] * TO.[To Item].[To Item Type] * TO.[To Item].[To Item] * TO.[To Location].[To Site Stage] * TO.[To Location].[To Location] * TO.[Activity1].[Activity1] * to.[Activity2].[Activity Type2].[Distribution] * TO.[Activity2].[Activity2] * TO.[Activity3].[Activity3]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer To Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph], &MPV};
    - df_in_BUPProdToConsOutput : Select (FROM.[Time].[Week] * FROM.[Item].[Item Stage].[SET] * FROM.[Item].[Item] * FROM.[Location].[Site Stage].filter(#.Name in {[MF_SET],[MF_KD],[MF]}) * FROM.[Location].[Location] * FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity Type2].[Manufacturing] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * TO.[To Time].[To Week] * TO.[To Item].[To Item Stage].[SET] * TO.[To Location].[To Site Stage].filter(#.Name in {[MF_SET],[MF_KD],[MF]}) * TO.[Activity1].[Activity1] * TO.[Activity2].[Activity Type2].[Distribution] * TO.[Activity2].[Activity2] * TO.[Activity3].[Activity3]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph], Version.[Version Name].[CWV_MP]};

    - df_in_MfgActualMtrl : Select (&MPV * [Item].[Item Type] * [Item].[Item] * [Location].[Location] * [To Item].[To Item] * [To Location].[To Location] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-105).Key && #.Key < &CurrentWeek.element(0).Key) * {Measure.[Mfg Actual Mtrl_Consume Qty]});
    - df_in_CWVTypeInfo : select (&MPV.relatedmembers([Version Type]));

* Output Tables :
    - df_out_log
    - df_out_logDetail

    - df_out_SOPVolatility_SET
    - df_out_SOPVolatility_Mtrl
    - df_out_SOPVolatilityMap

* 테스트 스크립트
    - EXEC plugin instance [PY_UI_SOPVolatility] for Measures {[SOP Volatility SET_Volatility]} using scope (&NSUISiteGrp3View)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [Category].[Category] * [Compare With].[Compare With] * [Analysis Object].[Analysis Object] * [Analysis Method].[Analysis Method] ) on row,
    ({Measure.[SOP Volatility SET_Volatility]}) on column;
    - Select ([Version].[Version Name].[CWV_MP]  * [Location].[Location] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * [Category].[Category] * [Compare With].[Compare With] * [Analysis Object].[Analysis Object] * [Analysis Method].[Analysis Method] ) on row,
    ({Measure.[SOP Volatility Mtrl_Volatility]}) on column;
    - Select ([Version].[Version Name].[CWV_MP] * [Analysis Object].[Analysis Object] ) on row, ({Measure.[SOP Volatility Map_Asn]}) on column;

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
str_instance = 'PY_UI_SOPVolatility'
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


def clean_and_format_month_data(df_Month, compare_field):
    """월별 데이터를 정리하고 포맷팅하는 함수

    Args:
        df_Month (pd.DataFrame): 처리할 월별 데이터프레임

    Returns:
        pd.DataFrame: 정리된 데이터프레임
    """
    # 유효하지 않은 FirstWeekDiff 값을 가진 행 제거
    valid_range_mask = df_Month[compare_field].between(0, 16)
    df_Month = df_Month[valid_range_mask].copy()

    # 주 번호 포맷팅 ('W-XX' 형식으로 변환)
    df_Month[COMPARE_WITH_COLUMN] = (
        'W-' + df_Month[compare_field]
        .astype(str)
        .str.zfill(2)  # pad() 대신 더 명확한 zfill() 사용
    )

    # 불필요한 열 제거
    if compare_field in df_Month.columns:
        df_Month = df_Month.drop(compare_field, axis=1)

    return df_Month


def remove_duplicate_indices(df):
    """데이터프레임에서 중복된 인덱스를 제거하고 첫 번째 발생 항목만 유지합니다.

    Args:
        df (pd.DataFrame): 처리할 데이터프레임

    Returns:
        pd.DataFrame: 중복 인덱스가 제거된 데이터프레임
    """
    return df[~df.index.duplicated(keep='first')]



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

            df_in_SOPVolatility_SET = read_csv_file("df_in_SOPVolatility_SET")
            df_in_SOPVolatility_Mtrl = read_csv_file("df_in_SOPVolatility_Mtrl")
            df_in_WMtrlConsQtyPlanOutput = read_csv_file("df_in_WMtrlConsQtyPlanOutput")
            df_in_BUPConsToConsOutput = read_csv_file("df_in_BUPConsToConsOutput")
            df_in_BUPProdToConsOutput = read_csv_file("df_in_BUPProdToConsOutput")
            df_in_MfgActualMtrl = read_csv_file("df_in_MfgActualMtrl")

            df_in_CWVTypeInfo = read_csv_file("df_in_CWVTypeInfo")

        dataframes = {
            'df_in_Week': df_in_Week,
            'df_in_2YearAgoWeek': df_in_2YearAgoWeek,
            'df_in_Month': df_in_Month,
            'df_in_SOPVolatility_SET': df_in_SOPVolatility_SET,
            'df_in_SOPVolatility_Mtrl': df_in_SOPVolatility_Mtrl,
            'df_in_WMtrlConsQtyPlanOutput': df_in_WMtrlConsQtyPlanOutput,
            'df_in_BUPConsToConsOutput': df_in_BUPConsToConsOutput,
            'df_in_BUPProdToConsOutput': df_in_BUPProdToConsOutput,
            'df_in_MfgActualMtrl': df_in_MfgActualMtrl,
            'df_in_CWVTypeInfo': df_in_CWVTypeInfo,
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
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_MONTH_COLUMN = 'Time.[Month]'
        TIME_PLANNING_MONTH_COLUMN = 'Time.[Planning Month]'
        CATEGORY_CATEGORY_COLUMN = 'Category.[Category]'
        TIME_WEEKKEY_COLUMN = 'Time.[WeekKey]'
        ITEM_TYPE_COLUMN = 'Item.[Item Type]'
        LOCATION_SITE_STAGE_COLUMN = 'Location.[Site Stage]'
        ACTIVITY2_ACTIVITY_TYPE2_COLUMN = 'Activity2.[Activity Type2]'
        ANALYSIS_OBJECT_COLUMN = 'Analysis Object.[Analysis Object]'
        ANALYSIS_METHOD_COLUMN = 'Analysis Method.[Analysis Method]'
        COMPARE_WITH_COLUMN = 'Compare With.[Compare With]'
        W_METERIAL_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN = 'W Material Consumption Quantity Plan Output'
        SOP_VOLATILITY_SET_VOLATILITY_COLUMN = 'SOP Volatility SET_Volatility'
        SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN = 'SOP Volatility Mtrl_Volatility'
        CATEGORY_TYPE_COLUMN = 'Category.[Category Type]'
        CATEGORY_TYPE_01_COLUMN = 'Category.[Category Type_01]'
        CATEGORY_TYPE_02_COLUMN = 'Category.[Category Type_02]'
        TIME_WEEK_01_COLUMN = 'Time.[Week_01]'
        TIME_WEEK_02_COLUMN = 'Time.[Week_02]'
        TO_ITEM_COLUMN = 'To Item.[To Item]'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ACTIVITY3_ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
        TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_LOCATION_TO_SITE_STAGE_COLUMN = 'To Location.[To Site Stage]'
        ACTIVITY1_ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        FROM_ACTIVITY2_ACTIVITY2_TYPE_COLUMN = 'from.[Activity2].[Activity Type2]'
        FROM_ACTIVITY3_ACTIVITY3_COLUMN = 'from.[Activity3].[Activity3]'
        FROM_ITEM_COLUMN = 'from.[Item].[Item]'
        FROM_LOCATION_COLUMN = 'from.[Location].[Location]'
        FROM_TIME_WEEK_COLUMN = 'from.[Time].[Week]'
        TO_ACTIVITY3_ACTIVITY3_COLUMN = 'to.[Activity3].[Activity3]'
        TO_ACTIVITY1_ACTIVITY1_COLUMN = 'to.[Activity1].[Activity1]'
        TO_TO_ITEM_COLUMN = 'to.[To Item].[To Item]'
        TO_TO_LOCATION_COLUMN = 'to.[To Location].[To Location]'
        TO_TO_TIME_TO_WEEK_COLUMN = 'to.[To Time].[To Week]'
        SOP_VOLATILITY_MAP_ASN_COLUMN = 'SOP Volatility Map_Asn'
        SOP_BUP_CTC_TO_PEGGED_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer To Pegged]'
        SOP_BUP_PTC_FROM_PEGGED_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]'

        step('=====> STEP2 End')


        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        VAL_CURRENTWEEK = str(get_first_value(df_in_Week, TIME_WEEK_COLUMN))
        step(f'=====> VAL_CURRENTWEEK : {VAL_CURRENTWEEK}')

        VAL_2YEARS_AGO_WEEK = str(get_first_value(df_in_2YearAgoWeek, TIME_WEEK_COLUMN))
        step(f'=====> VAL_2YEARS_AGO_WEEK : {VAL_2YEARS_AGO_WEEK}')

        df_in_Week[TIME_WEEK_COLUMN] = df_in_Week[TIME_WEEK_COLUMN].astype('str')
        df_in_MfgActualMtrl[TIME_WEEK_COLUMN] = df_in_MfgActualMtrl[TIME_WEEK_COLUMN].astype('str')
        VAL_VERSION_TYPE = df_in_CWVTypeInfo[VERSION_TYPE_COLUMN].astype(str)[0]


        df_in_Week['Week Rank'] = (df_in_Week[TIME_WEEK_COLUMN].rank().astype(int)) - 1
        df_in_Week[TIME_WEEK_COLUMN] = df_in_Week[TIME_WEEK_COLUMN].astype('str')

        df_in_Month.rename(columns={TIME_PLANNING_MONTH_COLUMN: TIME_MONTH_COLUMN}, inplace=True)
        df_in_Month['Week Rank'] = df_in_Month[TIME_WEEK_COLUMN].rank()

        df_in_Month['FirstWeek'] = df_in_Month.groupby([TIME_MONTH_COLUMN], sort=False, as_index=False)[TIME_WEEK_COLUMN].transform('min').astype('Int64')
        df_in_Month['FirstWeek Rank'] = df_in_Month['FirstWeek'].rank(method='min', ascending=True).astype('Int64')

        df_in_Month['LastWeek'] = df_in_Month.groupby([TIME_MONTH_COLUMN], sort=False, as_index=False)[TIME_WEEK_COLUMN].transform('max').astype('Int64')
        df_in_Month['LastWeek Rank'] = df_in_Month['LastWeek'].rank(method='max', ascending=True).astype('Int64')

        colunms = [TIME_WEEK_COLUMN, TIME_MONTH_COLUMN, 'FirstWeek', 'LastWeek']
        df_in_Month[colunms] = df_in_Month[colunms].astype('str')

        current_week_data = df_in_Month.loc[df_in_Month[TIME_WEEK_COLUMN] == VAL_CURRENTWEEK]
        df_in_Month['Current Week'] = current_week_data[TIME_WEEK_COLUMN].iloc[0]
        df_in_Month['Current Week Rank'] = current_week_data['Week Rank'].iloc[0]
        df_in_Month[['FirstWeekDiff', 'LastWeekDiff']] = df_in_Month[['FirstWeek Rank', 'LastWeek Rank']].sub(
            pd.to_numeric(df_in_Month['Current Week Rank'], errors='coerce').astype('Int64'), axis=0
        )


        colunms = ['FirstWeekDiff', 'LastWeekDiff']
        df_in_Month[colunms] = df_in_Month[colunms].astype('Int64')
        df_in_Month = pd.merge(df_in_Month, df_in_Week, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        filtered_row = df_in_Month.loc[df_in_Month[TIME_WEEK_COLUMN] == VAL_CURRENTWEEK, ['FirstWeek', 'LastWeek', 'LastWeekDiff']].iloc[0]
        VAL_FIRSTWEEK, VAL_LASTWEEK, VAL_LASTWEEK_CAP = filtered_row['FirstWeek'], filtered_row['LastWeek'], int(filtered_row['LastWeekDiff'])
        step(f'=====> VAL_FIRSTWEEK : {VAL_FIRSTWEEK}, VAL_LASTWEEK : {VAL_LASTWEEK}, VAL_LASTWEEK_CAP : {VAL_LASTWEEK_CAP}')

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # STEP 1.1 : df_in_WMtrlConsQtyPlanOutput 데이터 처리
        step('=====> STEP4 by 1.1 Start : df_in_WMtrlConsQtyPlanOutput 데이터 처리')

        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_PSI_SET
        conditions = [
            # FinishedGoods 조건
            (
                (df_in_WMtrlConsQtyPlanOutput[ITEM_TYPE_COLUMN] == 'FinishedGoods') &
                (df_in_WMtrlConsQtyPlanOutput[LOCATION_SITE_STAGE_COLUMN].isin(['MF_KD', 'MF_SET', 'MF'])) &
                (df_in_WMtrlConsQtyPlanOutput[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Distribution')
            ),
            # SubAssembly 조건 1
            (
                (df_in_WMtrlConsQtyPlanOutput[ITEM_TYPE_COLUMN] == 'SubAssembly') &
                (df_in_WMtrlConsQtyPlanOutput[LOCATION_SITE_STAGE_COLUMN].isin(['MF_KD', 'MF_SET', 'MF'])) &
                (df_in_WMtrlConsQtyPlanOutput[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Manufacturing')
            ),
            # SubAssembly 조건 2
            (
                (df_in_WMtrlConsQtyPlanOutput[ITEM_TYPE_COLUMN] == 'SubAssembly') &
                (df_in_WMtrlConsQtyPlanOutput[LOCATION_SITE_STAGE_COLUMN].isin(['MF_LCM_EX', 'MF_LCM'])) &
                (df_in_WMtrlConsQtyPlanOutput[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Distribution')
            )
        ]
        mask = conditions[0] | conditions[1] | conditions[2]
        df_CWVUI_PSI_TEMP = df_in_WMtrlConsQtyPlanOutput[mask].copy()


        df_CWVUI_PSI_TEMP[ANALYSIS_METHOD_COLUMN] = "PSI"
        df_CWVUI_PSI_TEMP[COMPARE_WITH_COLUMN] = "W-00"
        columns_defaults = {
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
        }
        df_CWVUI_PSI_TEMP = df_CWVUI_PSI_TEMP.assign(**columns_defaults)

        # 조건과 값을 분리하여 가독성과 유지보수성 향상
        conditions = [
            # FinishedGoods 조건
            (
                (df_CWVUI_PSI_TEMP[ITEM_TYPE_COLUMN] == 'FinishedGoods') &
                (df_CWVUI_PSI_TEMP[LOCATION_SITE_STAGE_COLUMN].isin(['MF_KD','MF_SET', 'MF'])) &
                (df_CWVUI_PSI_TEMP[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Distribution')
            ),
            # SubAssembly 조건 1
            (
                (df_CWVUI_PSI_TEMP[ITEM_TYPE_COLUMN] == 'SubAssembly') &
                (df_CWVUI_PSI_TEMP[LOCATION_SITE_STAGE_COLUMN].isin(['MF_KD', 'MF_SET', 'MF'])) &
                (df_CWVUI_PSI_TEMP[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Manufacturing')
            ),
            # SubAssembly 조건 2
            (
                (df_CWVUI_PSI_TEMP[ITEM_TYPE_COLUMN] == 'SubAssembly') &
                (df_CWVUI_PSI_TEMP[LOCATION_SITE_STAGE_COLUMN].isin(['MF_LCM_EX', 'MF_LCM'])) &
                (df_CWVUI_PSI_TEMP[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Distribution')
            )
        ]
        values = ['SET MP', 'MTRL REQ', 'LCM MP']
        default = '-'
        df_CWVUI_PSI_TEMP[ANALYSIS_OBJECT_COLUMN] = np.select(conditions, values, default)

        category_mapping = {
            'SET MP': 'SOP WEEK',
            'MTRL REQ': 'MFG WEEK',
            'LCM MP': 'SOP WEEK'
        }
        df_CWVUI_PSI_TEMP[CATEGORY_TYPE_COLUMN] = (
            df_CWVUI_PSI_TEMP[ANALYSIS_OBJECT_COLUMN].map(category_mapping).fillna('-')
        )

        df_CWVUI_PSI_TEMP.rename(columns={
            W_METERIAL_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN: SOP_VOLATILITY_SET_VOLATILITY_COLUMN,
        }, inplace=True)

        df_CWVUI_PSI_TEMP[TO_ITEM_COLUMN] = np.where(
            df_CWVUI_PSI_TEMP[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Distribution',
            df_CWVUI_PSI_TEMP[ITEM_COLUMN],
            df_CWVUI_PSI_TEMP[ACTIVITY3_ACTIVITY3_COLUMN]
        )
        df_CWVUI_PSI_TEMP[TO_LOCATION_COLUMN] = np.where(
            df_CWVUI_PSI_TEMP[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Distribution',
            df_CWVUI_PSI_TEMP[ACTIVITY1_ACTIVITY1_COLUMN].str.split('_').str[1],
            df_CWVUI_PSI_TEMP[LOCATION_COLUMN]
        )

        df_CWVUI_PSI_SET = df_CWVUI_PSI_TEMP[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN, CATEGORY_TYPE_COLUMN,
            TIME_WEEK_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN, SOP_VOLATILITY_SET_VOLATILITY_COLUMN,
        ]].copy()
        print_df(df_CWVUI_PSI_SET, 'STEP4 by 1.1.1 ____ df_CWVUI_PSI_SET .... create')



        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_PSI_Mtrl
        df_CWVUI_PSI_TEMP = df_in_WMtrlConsQtyPlanOutput[(
                (df_in_WMtrlConsQtyPlanOutput[ITEM_TYPE_COLUMN] == 'RawMaterials') &
                (df_in_WMtrlConsQtyPlanOutput[LOCATION_SITE_STAGE_COLUMN].isin(['MF_KD', 'MF_LCM_EX', 'MF', 'MF_SET', 'MF_LCM'])) &
                (df_in_WMtrlConsQtyPlanOutput[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Manufacturing')
        )].copy()

        columns_defaults = {
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
            ANALYSIS_OBJECT_COLUMN: 'MTRL REQ',
            CATEGORY_TYPE_COLUMN: 'MFG WEEK'
        }
        df_CWVUI_PSI_TEMP = df_CWVUI_PSI_TEMP.assign(**columns_defaults)

        df_CWVUI_PSI_TEMP.rename(columns={
            W_METERIAL_CONSUMPTION_QUANTITY_PLAN_OUTPUT_COLUMN: SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN,
            ITEM_COLUMN: ITEM_METERIAL_COLUMN,
        }, inplace=True)

        # 조건 마스크를 한 번만 생성
        distribution_mask = df_CWVUI_PSI_TEMP[ACTIVITY2_ACTIVITY_TYPE2_COLUMN] == 'Distribution'

        # 한 번에 여러 열 할당
        df_CWVUI_PSI_TEMP.loc[distribution_mask, TO_ITEM_COLUMN] = df_CWVUI_PSI_TEMP.loc[distribution_mask, ITEM_METERIAL_COLUMN]
        df_CWVUI_PSI_TEMP.loc[~distribution_mask, TO_ITEM_COLUMN] = df_CWVUI_PSI_TEMP.loc[~distribution_mask, ACTIVITY3_ACTIVITY3_COLUMN]

        df_CWVUI_PSI_TEMP.loc[distribution_mask, TO_LOCATION_COLUMN] = df_CWVUI_PSI_TEMP.loc[distribution_mask, ACTIVITY1_ACTIVITY1_COLUMN].str.split('_').str[1]
        df_CWVUI_PSI_TEMP.loc[~distribution_mask, TO_LOCATION_COLUMN] = df_CWVUI_PSI_TEMP.loc[~distribution_mask, LOCATION_COLUMN]

        df_CWVUI_PSI_Mtrl = df_CWVUI_PSI_TEMP[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN,
            ANALYSIS_OBJECT_COLUMN, CATEGORY_TYPE_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN,
            LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN, SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN,
        ]].copy()
        print_df(df_CWVUI_PSI_Mtrl, 'STEP4 by 1.1.2 ____ df_CWVUI_PSI_Mtrl .... create')
        step('=====> STEP4 by 1.1 End')



        # STEP 1.2 : df_in_BUPConsToConsOutput 데이터 처리
        step('=====> STEP4 by 1.2 Start : df_in_BUPConsToConsOutput 데이터 처리')

        # 조건들을 개별적으로 정의하여 가독성 향상
        activity_condition = df_in_BUPConsToConsOutput[FROM_ACTIVITY2_ACTIVITY2_TYPE_COLUMN].isin(['Manufacturing', 'Distribution'])
        same_activity3 = df_in_BUPConsToConsOutput[FROM_ACTIVITY3_ACTIVITY3_COLUMN] == df_in_BUPConsToConsOutput[TO_ACTIVITY3_ACTIVITY3_COLUMN]
        diff_item = df_in_BUPConsToConsOutput[FROM_ITEM_COLUMN] != df_in_BUPConsToConsOutput[TO_TO_ITEM_COLUMN]
        diff_location = df_in_BUPConsToConsOutput[FROM_LOCATION_COLUMN] != df_in_BUPConsToConsOutput[TO_TO_LOCATION_COLUMN]

        # 모든 조건을 결합
        keep_mask = activity_condition & same_activity3 & (diff_item | diff_location)

        # 필터링된 데이터로 직접 할당 (drop 대신)
        df_in_BUPConsToConsOutput = df_in_BUPConsToConsOutput[keep_mask]
        print_df(df_in_BUPConsToConsOutput, 'STEP4 by 1.2.1 ____ df_in_BUPConsToConsOutput .... create')



        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_PSI_SET
        # 상수 정의
        ITEM_TYPE_SUBASSEMBLY = 'SubAssembly'
        MF_SITES = ['MF', 'MF_SET', 'MF_KD']

        # 조건 분리
        is_subassembly = df_in_BUPConsToConsOutput[ITEM_TYPE_COLUMN] == ITEM_TYPE_SUBASSEMBLY
        to_mf_sites = df_in_BUPConsToConsOutput[TO_LOCATION_TO_SITE_STAGE_COLUMN].isin(MF_SITES)
        same_site = (
            df_in_BUPConsToConsOutput[LOCATION_SITE_STAGE_COLUMN] == df_in_BUPConsToConsOutput[TO_LOCATION_TO_SITE_STAGE_COLUMN]
        )

        # 필터링 적용
        df_CWVUI_PSI_TEMP = df_in_BUPConsToConsOutput[is_subassembly & to_mf_sites & same_site].copy()

        columns_defaults = {
            VERSION_NAME_COLUMN: paramOutVersion,
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
            ANALYSIS_OBJECT_COLUMN: 'SET MP',
            CATEGORY_TYPE_01_COLUMN: 'SOP WEEK',
            CATEGORY_TYPE_02_COLUMN: 'MFG WEEK',
            TIME_WEEK_01_COLUMN: df_CWVUI_PSI_TEMP[FROM_TIME_WEEK_COLUMN],
            TIME_WEEK_02_COLUMN: df_CWVUI_PSI_TEMP[TO_TO_TIME_TO_WEEK_COLUMN],
        }
        df_CWVUI_PSI_TEMP = df_CWVUI_PSI_TEMP.assign(**columns_defaults)

        df_CWVUI_PSI_TEMP.rename(columns={
            SOP_BUP_CTC_TO_PEGGED_COLUMN: SOP_VOLATILITY_SET_VOLATILITY_COLUMN,
            FROM_ITEM_COLUMN: ITEM_COLUMN,
            FROM_LOCATION_COLUMN: LOCATION_COLUMN,
            TO_TO_ITEM_COLUMN: TO_ITEM_COLUMN,
        }, inplace=True)
        df_CWVUI_PSI_TEMP[TO_LOCATION_COLUMN] = df_CWVUI_PSI_TEMP[TO_ACTIVITY1_ACTIVITY1_COLUMN].str.split('_').str[1]


        df_CWVUI_PSI_TEMP_01 = df_CWVUI_PSI_TEMP[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN,
            CATEGORY_TYPE_01_COLUMN, TIME_WEEK_01_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
            SOP_VOLATILITY_SET_VOLATILITY_COLUMN,
        ]].copy()
        df_CWVUI_PSI_TEMP_02 = df_CWVUI_PSI_TEMP[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN,
            CATEGORY_TYPE_02_COLUMN, TIME_WEEK_02_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
            SOP_VOLATILITY_SET_VOLATILITY_COLUMN,
        ]].copy()

        df_CWVUI_PSI_TEMP_01.rename(columns={
            CATEGORY_TYPE_01_COLUMN: CATEGORY_TYPE_COLUMN,
            TIME_WEEK_01_COLUMN: TIME_WEEK_COLUMN,
        }, inplace=True)
        df_CWVUI_PSI_TEMP_02.rename(columns={
            CATEGORY_TYPE_02_COLUMN: CATEGORY_TYPE_COLUMN,
            TIME_WEEK_02_COLUMN: TIME_WEEK_COLUMN,
        }, inplace=True)

        df_CWVUI_PSI_SET = pd.concat([df_CWVUI_PSI_SET, df_CWVUI_PSI_TEMP_01, df_CWVUI_PSI_TEMP_02], axis=0)
        print_df(df_CWVUI_PSI_SET, 'STEP4 by 1.2.2 ____ df_CWVUI_PSI_SET .... create')


        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_PSI_Mtrl
        # 상수 정의
        ITEM_TYPE_RAW = 'RawMaterials'
        MF_SITES = ['MF', 'MF_SET', 'MD_KD']
        MF_LCM_SITES = ['MF_LCM', 'MF_SET', 'MF', 'MF_KD', 'MF_LCM_EX']
        LCM_SITES = ['MF_LCM', 'MF_LCM_EX']

        # 공통 조건
        raw_materials = df_in_BUPConsToConsOutput[ITEM_TYPE_COLUMN] == ITEM_TYPE_RAW

        # 첫 번째 조건 세트
        to_mf_sites = df_in_BUPConsToConsOutput[TO_LOCATION_TO_SITE_STAGE_COLUMN].isin(MF_SITES)
        same_site = (
            df_in_BUPConsToConsOutput[LOCATION_SITE_STAGE_COLUMN] == df_in_BUPConsToConsOutput[TO_LOCATION_TO_SITE_STAGE_COLUMN]
        )
        condition1 = raw_materials & to_mf_sites & same_site

        # 두 번째 조건 세트
        from_mf_lcm_sites = df_in_BUPConsToConsOutput[LOCATION_SITE_STAGE_COLUMN].isin(MF_LCM_SITES)
        to_lcm_sites = df_in_BUPConsToConsOutput[TO_LOCATION_TO_SITE_STAGE_COLUMN].isin(LCM_SITES)
        condition2 = raw_materials & from_mf_lcm_sites & to_lcm_sites

        # 최종 필터링
        df_CWVUI_PSI_TEMP = df_in_BUPConsToConsOutput[condition1 | condition2].copy()

        columns_defaults = {
            VERSION_NAME_COLUMN: paramOutVersion,
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
        }
        df_CWVUI_PSI_TEMP = df_CWVUI_PSI_TEMP.assign(**columns_defaults)

        # 상수 정의
        ITEM_TYPE_RAW = 'RawMaterials'
        MF_SITES = ['MF', 'MF_SET', 'MD_KD']
        MF_LCM_SITES = ['MF_LCM', 'MF_SET', 'MF', 'MF_KD', 'MF_LCM_EX']
        LCM_SITES = ['MF_LCM', 'MF_LCM_EX']

        # MP 타입 상수
        MP_SET = 'SET MP'
        MP_LCM = 'LCM MP'
        DEFAULT_VALUE = '-'

        # 기본 조건
        item_raw = df_CWVUI_PSI_TEMP[ITEM_TYPE_COLUMN] == ITEM_TYPE_RAW

        # 첫 번째 조건 세트
        to_mf_sites = df_CWVUI_PSI_TEMP[TO_LOCATION_TO_SITE_STAGE_COLUMN].isin(MF_SITES)
        same_site = df_CWVUI_PSI_TEMP[LOCATION_SITE_STAGE_COLUMN] == df_CWVUI_PSI_TEMP[TO_LOCATION_TO_SITE_STAGE_COLUMN]
        condition1 = item_raw & to_mf_sites & same_site

        # 두 번째 조건 세트
        from_mf_sites = df_CWVUI_PSI_TEMP[LOCATION_SITE_STAGE_COLUMN].isin(MF_LCM_SITES)
        to_lcm_sites = df_CWVUI_PSI_TEMP[TO_LOCATION_TO_SITE_STAGE_COLUMN].isin(LCM_SITES)
        condition2 = item_raw & from_mf_sites & to_lcm_sites

        # 조건들과 결과값을 리스트로 정의
        conditions = [condition1, condition2]
        choices = [MP_SET, MP_LCM]

        # np.select 적용
        df_CWVUI_PSI_TEMP[ANALYSIS_OBJECT_COLUMN] = np.select(conditions, choices, default=DEFAULT_VALUE)

        columns_defaults = {
            CATEGORY_TYPE_01_COLUMN: 'SOP WEEK',
            CATEGORY_TYPE_02_COLUMN: 'MFG WEEK',
            TIME_WEEK_01_COLUMN: df_CWVUI_PSI_TEMP[TO_TO_TIME_TO_WEEK_COLUMN],
            TIME_WEEK_02_COLUMN: df_CWVUI_PSI_TEMP[FROM_TIME_WEEK_COLUMN]
        }
        df_CWVUI_PSI_TEMP = df_CWVUI_PSI_TEMP.assign(**columns_defaults)

        df_CWVUI_PSI_TEMP.rename(columns={
            SOP_BUP_CTC_TO_PEGGED_COLUMN: SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN,
            FROM_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            FROM_LOCATION_COLUMN: LOCATION_COLUMN,
            TO_TO_ITEM_COLUMN: TO_ITEM_COLUMN,
        }, inplace=True)
        df_CWVUI_PSI_TEMP[TO_LOCATION_COLUMN] = df_CWVUI_PSI_TEMP[TO_ACTIVITY1_ACTIVITY1_COLUMN].str.split('_').str[1]

        df_CWVUI_PSI_TEMP_01 = df_CWVUI_PSI_TEMP[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN,
            CATEGORY_TYPE_01_COLUMN, TIME_WEEK_01_COLUMN, ITEM_METERIAL_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN,
            TO_LOCATION_COLUMN, SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN,
        ]].copy()

        df_CWVUI_PSI_TEMP_02 = df_CWVUI_PSI_TEMP[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN,
            CATEGORY_TYPE_02_COLUMN, TIME_WEEK_02_COLUMN, ITEM_METERIAL_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN,
            TO_LOCATION_COLUMN, SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN,
        ]].copy()

        df_CWVUI_PSI_TEMP_01.rename(columns={
            CATEGORY_TYPE_01_COLUMN: CATEGORY_TYPE_COLUMN,
            TIME_WEEK_01_COLUMN: TIME_WEEK_COLUMN,
        }, inplace=True)
        df_CWVUI_PSI_TEMP_02.rename(columns={
            CATEGORY_TYPE_02_COLUMN: CATEGORY_TYPE_COLUMN,
            TIME_WEEK_02_COLUMN: TIME_WEEK_COLUMN,
        }, inplace=True)

        df_CWVUI_PSI_Mtrl = pd.concat([df_CWVUI_PSI_Mtrl, df_CWVUI_PSI_TEMP_01, df_CWVUI_PSI_TEMP_02], axis=0)
        print_df(df_CWVUI_PSI_Mtrl, 'STEP4 by 1.2.3 ____ df_CWVUI_PSI_Mtrl .... create')

        step('=====> STEP4 by 1.2 End')



        # STEP 1.3 : df_in_BUPProdToConsOutput 데이터 처리
        step('=====> STEP4 by 1.3 Start : df_in_BUPProdToConsOutput 데이터 처리')
        # --------------------------------------------------------------------------------------------------------------- df_CWVUI_PSI_SET
        mask = (
            df_in_BUPProdToConsOutput[FROM_ITEM_COLUMN] == df_in_BUPProdToConsOutput[TO_ACTIVITY3_ACTIVITY3_COLUMN]
        )
        df_in_BUPProdToConsOutput = df_in_BUPProdToConsOutput[mask]
        print_df(df_in_BUPProdToConsOutput, 'STEP4 by 1.3.1 ____ df_in_BUPProdToConsOutput .... select')

        df_CWVUI_PSI_TEMP = df_in_BUPProdToConsOutput[[
            FROM_TIME_WEEK_COLUMN, SOP_BUP_PTC_FROM_PEGGED_COLUMN, FROM_ITEM_COLUMN,
            FROM_LOCATION_COLUMN, TO_ACTIVITY1_ACTIVITY1_COLUMN,
        ]].copy()

        columns_defaults = {
            VERSION_NAME_COLUMN: paramOutVersion,
            ANALYSIS_METHOD_COLUMN: 'PSI',
            COMPARE_WITH_COLUMN: 'W-00',
            ANALYSIS_OBJECT_COLUMN: 'SET MP',
            CATEGORY_TYPE_COLUMN: 'MFG WEEK',
        }
        df_CWVUI_PSI_TEMP = df_CWVUI_PSI_TEMP.assign(**columns_defaults)

        df_CWVUI_PSI_TEMP.rename(columns={
            FROM_TIME_WEEK_COLUMN: TIME_WEEK_COLUMN,
            SOP_BUP_PTC_FROM_PEGGED_COLUMN: SOP_VOLATILITY_SET_VOLATILITY_COLUMN,
            FROM_ITEM_COLUMN: ITEM_COLUMN,
            FROM_LOCATION_COLUMN: LOCATION_COLUMN,
        }, inplace=True)
        df_CWVUI_PSI_TEMP[TO_ITEM_COLUMN] = df_CWVUI_PSI_TEMP[ITEM_COLUMN]
        df_CWVUI_PSI_TEMP[TO_LOCATION_COLUMN] = df_CWVUI_PSI_TEMP[TO_ACTIVITY1_ACTIVITY1_COLUMN].str.split('_').str[1]

        df_CWVUI_PSI_TEMP_01 = df_CWVUI_PSI_TEMP[[
            VERSION_NAME_COLUMN, ANALYSIS_METHOD_COLUMN, COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN,
            CATEGORY_TYPE_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
            SOP_VOLATILITY_SET_VOLATILITY_COLUMN,
        ]].copy()

        df_CWVUI_PSI_SET = pd.concat([df_CWVUI_PSI_SET, df_CWVUI_PSI_TEMP_01], axis=0)
        print_df(df_CWVUI_PSI_SET, 'STEP4 by 1.3.2 ____ df_CWVUI_PSI_SET .... create')

        step('=====> STEP4 by 1.3 End')




        # STEP 1.4 : df_CWVUI_PSI_SET, df_CWVUI_PSI_Mtrl Data 후처리
        step('=====> STEP4 by 1.4 Start : df_CWVUI_PSI_SET, df_CWVUI_PSI_Mtrl Data 후처리')

        df_CWVUI_PSI_SET_01 = df_CWVUI_PSI_SET.copy()
        df_CWVUI_PSI_SET_02 = df_CWVUI_PSI_SET.copy()
        df_CWVUI_PSI_SET_01[CATEGORY_TYPE_COLUMN] = df_CWVUI_PSI_SET_01[CATEGORY_TYPE_COLUMN] + '_Actual Result'
        df_CWVUI_PSI_SET_02[CATEGORY_TYPE_COLUMN] = df_CWVUI_PSI_SET_02[CATEGORY_TYPE_COLUMN] + '_Final Plan'

        df_CWVUI_PSI_SET = pd.concat([df_CWVUI_PSI_SET_01, df_CWVUI_PSI_SET_02], axis=0)
        df_CWVUI_PSI_SET.rename(columns={
            CATEGORY_TYPE_COLUMN: CATEGORY_CATEGORY_COLUMN,
        }, inplace=True)
        print_df(df_CWVUI_PSI_SET, 'STEP4 by 1.4.1 ____ df_CWVUI_PSI_SET .... 후처리')

        delete_dfs(df_CWVUI_PSI_SET_01, df_CWVUI_PSI_SET_02)

        df_CWVUI_PSI_Mtrl_01 = df_CWVUI_PSI_Mtrl.copy()
        df_CWVUI_PSI_Mtrl_02 = df_CWVUI_PSI_Mtrl.copy()
        df_CWVUI_PSI_Mtrl_01[CATEGORY_TYPE_COLUMN] = df_CWVUI_PSI_Mtrl_01[CATEGORY_TYPE_COLUMN] + '_Actual Result'
        df_CWVUI_PSI_Mtrl_02[CATEGORY_TYPE_COLUMN] = df_CWVUI_PSI_Mtrl_02[CATEGORY_TYPE_COLUMN] + '_Final Plan'

        df_CWVUI_PSI_Mtrl = pd.concat([df_CWVUI_PSI_Mtrl_01, df_CWVUI_PSI_Mtrl_02], axis=0)
        df_CWVUI_PSI_Mtrl.rename(columns={
            CATEGORY_TYPE_COLUMN: CATEGORY_CATEGORY_COLUMN,
        }, inplace=True)
        print_df(df_CWVUI_PSI_Mtrl, 'STEP4 by 1.4.2 ____ df_CWVUI_PSI_Mtrl .... 후처리')

        delete_dfs(df_CWVUI_PSI_Mtrl_01, df_CWVUI_PSI_Mtrl_02)

        step('=====> STEP4 by 1.4 End')



        # STEP 2.1 : df_in_SOPVolatility_SET, df_in_SOPVolatility_Mtrl 데이터프레임 생성
        step('=====> STEP4 by 2.1 Start : df_in_SOPVolatility_SET, df_in_SOPVolatility_Mtrl 데이터프레임 생성')
        #--------------------------------------------------------------------------------------------------------------- df_in_SOPVolatility_SET
        df_in_SOPVolatility_SET[VERSION_NAME_COLUMN] = paramOutVersion

        df_SOPVolatility_PSI_SET = df_in_SOPVolatility_SET[~(df_in_SOPVolatility_SET[CATEGORY_CATEGORY_COLUMN].str.contains('Actual'))].copy()
        df_SOPVolatility_Weekly_SET = df_SOPVolatility_PSI_SET.copy()
        df_SOPVolatility_MonthlyF_SET = df_SOPVolatility_PSI_SET.copy()
        df_SOPVolatility_MonthlyL_SET = df_SOPVolatility_PSI_SET.copy()

        df_SOPVolatility_Weekly_SET[ANALYSIS_METHOD_COLUMN] = 'Weekly'
        df_SOPVolatility_MonthlyF_SET[ANALYSIS_METHOD_COLUMN] = 'Monthly_FirstWeek'
        df_SOPVolatility_MonthlyL_SET[ANALYSIS_METHOD_COLUMN] = 'Monthly_LastWeek'
        print_df(df_SOPVolatility_MonthlyL_SET, 'STEP4 by 2.1.1 ____ df_SOPVolatility_MonthlyL_SET .... create')


        #--------------------------------------------------------------------------------------------------------------- df_in_SOPVolatility_Mtrl
        df_in_SOPVolatility_Mtrl[VERSION_NAME_COLUMN] = paramOutVersion

        df_SOPVolatility_PSI_Mtrl = df_in_SOPVolatility_Mtrl[~(df_in_SOPVolatility_Mtrl[CATEGORY_CATEGORY_COLUMN].str.contains('Actual'))].copy()
        df_SOPVolatility_Weekly_Mtrl = df_SOPVolatility_PSI_Mtrl.copy()
        df_SOPVolatility_MonthlyF_Mtrl = df_SOPVolatility_PSI_Mtrl.copy()
        df_SOPVolatility_MonthlyL_Mtrl = df_SOPVolatility_PSI_Mtrl.copy()

        df_SOPVolatility_Weekly_Mtrl[ANALYSIS_METHOD_COLUMN] = 'Weekly'
        df_SOPVolatility_MonthlyF_Mtrl[ANALYSIS_METHOD_COLUMN] = 'Monthly_FirstWeek'
        df_SOPVolatility_MonthlyL_Mtrl[ANALYSIS_METHOD_COLUMN] = 'Monthly_LastWeek'
        print_df(df_SOPVolatility_MonthlyL_Mtrl, 'STEP4 by 2.1.2 ____ df_SOPVolatility_MonthlyL_Mtrl .... create')

        step('=====> STEP4 by 2.1 End')



        # STEP 3.1 : 주차 이동 및 데이터 프레임 MERGE
        step('=====> STEP4 by 3.1 Start : 주차 이동 및 데이터 프레임 MERGE')
        # --------------------------------------------------------------------------------------------------------------- df_out_SOPVolatility_PSI_SET
        COMPARE_VALUE = "W-16"
        df_SOPVolatility_PSI_SET = df_SOPVolatility_PSI_SET[
            df_SOPVolatility_PSI_SET[COMPARE_WITH_COLUMN] != COMPARE_VALUE
        ]

        df_SOPVolatility_PSI_SET[COMPARE_WITH_COLUMN] = 'W-' + ((df_SOPVolatility_PSI_SET[COMPARE_WITH_COLUMN].str.split('-').str[1]).astype(int) + 1).astype(str).str.zfill(2)
        print_df(df_SOPVolatility_PSI_SET, 'STEP4 by 3.1.1 ____ df_SOPVolatility_PSI_SET .... create')

        df_out_SOPVolatility_PSI_SET = pd.concat([df_SOPVolatility_PSI_SET, df_CWVUI_PSI_SET], axis=0)
        print_df(df_out_SOPVolatility_PSI_SET, 'STEP4 by 3.1.2 ____ df_out_SOPVolatility_PSI_SET .... create')


        #--------------------------------------------------------------------------------------------------------------- df_out_SOPVolatility_PSI_Mtrl
        COMPARE_VALUE = "W-16"
        df_SOPVolatility_PSI_Mtrl = df_SOPVolatility_PSI_Mtrl[
            df_SOPVolatility_PSI_Mtrl[COMPARE_WITH_COLUMN] != COMPARE_VALUE
        ]

        df_SOPVolatility_PSI_Mtrl[COMPARE_WITH_COLUMN] = (
                'W-' + ((df_SOPVolatility_PSI_Mtrl[COMPARE_WITH_COLUMN].str.split('-').str[1]).astype(int) + 1)
                .astype(str).str.pad(width=2, side='left', fillchar='0')
        )
        print_df(df_SOPVolatility_PSI_Mtrl, 'STEP4 by 3.1.3 ____ df_SOPVolatility_PSI_Mtrl .... create')

        df_out_SOPVolatility_PSI_Mtrl = pd.concat([df_SOPVolatility_PSI_Mtrl, df_CWVUI_PSI_Mtrl], axis=0)
        print_df(df_out_SOPVolatility_PSI_Mtrl, 'STEP4 by 3.1.4 ____ df_out_SOPVolatility_PSI_Mtrl .... create')

        step('=====> STEP4 by 3.1 End')



        # STEP 4.1 : df_out_SOPVolatility_Weekly_SET, df_out_SOPVolatility_Weekly_Mtrl Data 처리
        step('=====> STEP4 by 4.1 Start : df_out_SOPVolatility_Weekly_SET, df_out_SOPVolatility_Weekly_Mtrl Data 처리')

        df_in_Week = df_in_Week.drop([TIME_WEEKKEY_COLUMN], axis=1, errors='ignore')
        df_in_Week['WeekDiff'] = (df_in_Week[TIME_WEEK_COLUMN].rank().astype(int) - 1).astype(str)
        df_in_Week[COMPARE_WITH_COLUMN] = 'W-' + df_in_Week['WeekDiff'].astype(str).str.pad(width=2, side='left', fillchar='0')
        df_in_Week[TIME_WEEK_COLUMN] = df_in_Week[TIME_WEEK_COLUMN].astype(str)

        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_Weekly_SET
        df_CWVUI_Weekly_SET = df_CWVUI_PSI_SET.copy()

        df_CWVUI_Weekly_SET[TIME_WEEK_COLUMN] = df_CWVUI_Weekly_SET[TIME_WEEK_COLUMN].astype(str)
        df_CWVUI_Weekly_SET = pd.merge(df_in_Week, df_CWVUI_Weekly_SET, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_CWVUI_Weekly_SET = df_CWVUI_Weekly_SET.drop(['WeekDiff', COMPARE_WITH_COLUMN+'_y'], axis=1, errors='ignore')
        df_CWVUI_Weekly_SET[ANALYSIS_METHOD_COLUMN] = 'Weekly'

        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_PSI_Mtrl
        df_CWVUI_Weekly_Mtrl = df_CWVUI_PSI_Mtrl.copy()
        df_CWVUI_Weekly_Mtrl[TIME_WEEK_COLUMN] = df_CWVUI_Weekly_Mtrl[TIME_WEEK_COLUMN].astype(str)

        df_CWVUI_Weekly_Mtrl = pd.merge(df_in_Week, df_CWVUI_Weekly_Mtrl, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_CWVUI_Weekly_Mtrl = df_CWVUI_Weekly_Mtrl.drop(['WeekDiff', COMPARE_WITH_COLUMN+'_y'], axis=1, errors='ignore')
        df_CWVUI_Weekly_Mtrl[ANALYSIS_METHOD_COLUMN] = 'Weekly'

        #--------------------------------------------------------------------------------------------------------------- df_SOPVolatility_Weekly : concat
        df_out_SOPVolatility_Weekly_SET = pd.concat([df_SOPVolatility_Weekly_SET, df_CWVUI_Weekly_SET], axis=0)
        df_out_SOPVolatility_Weekly_Mtrl = pd.concat([df_SOPVolatility_Weekly_Mtrl, df_CWVUI_Weekly_Mtrl], axis=0)

        step('=====> STEP4 by 4.1 End')



        # STEP 5.1 : df_out_SOPVolatility_MonthlyF_SET, df_out_SOPVolatility_MonthlyF_Mtrl Data 처리
        step('=====> STEP4 by 5.1 Start : df_out_SOPVolatility_MonthlyF_SET, df_out_SOPVolatility_MonthlyF_Mtrl Data 처리')

        df_Month = df_in_Month[[TIME_WEEK_COLUMN, 'FirstWeekDiff']].copy()
        df_Month = clean_and_format_month_data(df_Month, 'FirstWeekDiff')

        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_MonthlyF_SET
        df_CWVUI_MonthlyF_SET = df_CWVUI_PSI_SET.copy()

        df_CWVUI_MonthlyF_SET[TIME_WEEK_COLUMN] = df_CWVUI_MonthlyF_SET[TIME_WEEK_COLUMN].astype(str)
        df_CWVUI_MonthlyF_SET = pd.merge(df_Month, df_CWVUI_MonthlyF_SET, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))

        df_CWVUI_MonthlyF_SET = df_CWVUI_MonthlyF_SET.drop(COMPARE_WITH_COLUMN+'_y', axis=1, errors='ignore')
        df_CWVUI_MonthlyF_SET[ANALYSIS_METHOD_COLUMN] = 'Monthly_FirstWeek'

        #--------------------------------------------------------------------------------------------------------------- df_CWVUI_MonthlyF_Mtrl
        df_CWVUI_MonthlyF_Mtrl = df_CWVUI_PSI_Mtrl.copy()

        df_CWVUI_MonthlyF_Mtrl[TIME_WEEK_COLUMN] = df_CWVUI_MonthlyF_Mtrl[TIME_WEEK_COLUMN].astype(str)
        df_CWVUI_MonthlyF_Mtrl = pd.merge(df_Month, df_CWVUI_MonthlyF_Mtrl, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_CWVUI_MonthlyF_Mtrl = df_CWVUI_MonthlyF_Mtrl.drop(COMPARE_WITH_COLUMN+'_y', axis=1, errors='ignore')
        df_CWVUI_MonthlyF_Mtrl[ANALYSIS_METHOD_COLUMN] = 'Monthly_FirstWeek'

        #--------------------------------------------------------------------------------------------------------------- df_out_SOPVolatility_MonthlyF : concat
        df_out_SOPVolatility_MonthlyF_SET = pd.concat([df_SOPVolatility_MonthlyF_SET, df_CWVUI_MonthlyF_SET], axis=0)
        df_out_SOPVolatility_MonthlyF_Mtrl = pd.concat([df_SOPVolatility_MonthlyF_Mtrl, df_CWVUI_MonthlyF_Mtrl], axis=0)

        step('=====> STEP4 by 5.1 End')



        # STEP 6.1 : df_out_SOPVolatility_MonthlyL_SET, df_out_SOPVolatility_MonthlyL_Mtrl Data 처리
        step('=====> STEP4 by 6.1 Start : df_out_SOPVolatility_MonthlyL_SET, df_out_SOPVolatility_MonthlyL_Mtrl Data 처리')

        df_Month = df_in_Month[[TIME_WEEK_COLUMN, 'LastWeekDiff']].copy()
        df_Month = clean_and_format_month_data(df_Month, 'LastWeekDiff')

        #--------------------------------------------------------------------------------------------------------------- df_SOPVolatility_MonthlyL_SET
        df_CWVUI_MonthlyL_SET = df_CWVUI_PSI_SET.copy()
        df_CWVUI_MonthlyL_SET[TIME_WEEK_COLUMN] = df_CWVUI_MonthlyL_SET[TIME_WEEK_COLUMN].astype(str)
        df_CWVUI_MonthlyL_SET = pd.merge(df_Month, df_CWVUI_MonthlyL_SET, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_CWVUI_MonthlyL_SET = df_CWVUI_MonthlyL_SET.drop(COMPARE_WITH_COLUMN+'_y', axis=1, errors='ignore')
        df_CWVUI_MonthlyL_SET[ANALYSIS_METHOD_COLUMN] = 'Monthly_LastWeek'

        #--------------------------------------------------------------------------------------------------------------- df_SOPVolatility_MonthlyL_Mtrl
        df_CWVUI_MonthlyL_Mtrl = df_CWVUI_PSI_Mtrl.copy()
        df_CWVUI_MonthlyL_Mtrl[TIME_WEEK_COLUMN] = df_CWVUI_MonthlyL_Mtrl[TIME_WEEK_COLUMN].astype(str)
        df_CWVUI_MonthlyL_Mtrl = pd.merge(df_Month, df_CWVUI_MonthlyL_Mtrl, on=[TIME_WEEK_COLUMN], how='inner', suffixes=('', '_y'))
        df_CWVUI_MonthlyL_Mtrl[ANALYSIS_METHOD_COLUMN] = 'Monthly_LastWeek'

        #--------------------------------------------------------------------------------------------------------------- df_out_SOPVolatility_MonthlyL : concat
        df_out_SOPVolatility_MonthlyL_SET = pd.concat([df_SOPVolatility_MonthlyL_SET, df_CWVUI_MonthlyL_SET], axis=0)
        df_out_SOPVolatility_MonthlyL_Mtrl = pd.concat([df_SOPVolatility_MonthlyL_Mtrl, df_CWVUI_MonthlyL_Mtrl], axis=0)

        step('=====> STEP4 6.1 End')



        # STEP 7.1 : 과거 실적 Data 처리
        step('=====> STEP4 by 7.1 Start : 과거 실적 Data 처리')
        #--------------------------------------------------------------------------------------------------------------- FirstWeek / LastWeek 처리
        df_out_SOPVolatility_PSI_FP_SET = df_out_SOPVolatility_PSI_SET[(df_out_SOPVolatility_PSI_SET[CATEGORY_CATEGORY_COLUMN].str.endswith('Final Plan'))].copy()
        df_out_SOPVolatility_PSI_AR_SET = df_out_SOPVolatility_PSI_SET[(df_out_SOPVolatility_PSI_SET[CATEGORY_CATEGORY_COLUMN].str.endswith('Actual Result'))].copy()
        df_out_SOPVolatility_MonthlyL_FP_SET = df_out_SOPVolatility_MonthlyL_SET[(df_out_SOPVolatility_MonthlyL_SET[CATEGORY_CATEGORY_COLUMN].str.endswith('Final Plan'))].copy()
        df_out_SOPVolatility_MonthlyL_AR_SET = df_out_SOPVolatility_MonthlyL_SET[(df_out_SOPVolatility_MonthlyL_SET[CATEGORY_CATEGORY_COLUMN].str.endswith('Actual Result'))].copy()
        df_out_SOPVolatility_PSI_FP_SET[TIME_WEEK_COLUMN] = df_out_SOPVolatility_PSI_FP_SET[TIME_WEEK_COLUMN].astype(str)
        print_df(df_out_SOPVolatility_PSI_FP_SET, 'STEP4 by 7.1.1 ____ df_out_SOPVolatility_PSI_FP_SET .... create')

        df_out_SOPVolatility_PSI_FP_Mtrl = df_out_SOPVolatility_PSI_Mtrl[(df_out_SOPVolatility_PSI_Mtrl[CATEGORY_CATEGORY_COLUMN].str.endswith('Final Plan'))].copy()
        df_out_SOPVolatility_PSI_AR_Mtrl = df_out_SOPVolatility_PSI_Mtrl[(df_out_SOPVolatility_PSI_Mtrl[CATEGORY_CATEGORY_COLUMN].str.endswith('Actual Result'))].copy()
        df_out_SOPVolatility_MonthlyL_FP_Mtrl = df_out_SOPVolatility_MonthlyL_Mtrl[(df_out_SOPVolatility_MonthlyL_Mtrl[CATEGORY_CATEGORY_COLUMN].str.endswith('Final Plan'))].copy()
        df_out_SOPVolatility_MonthlyL_AR_Mtrl = df_out_SOPVolatility_MonthlyL_Mtrl[(df_out_SOPVolatility_MonthlyL_Mtrl[CATEGORY_CATEGORY_COLUMN].str.endswith('Actual Result'))].copy()
        df_out_SOPVolatility_PSI_FP_Mtrl[TIME_WEEK_COLUMN] = df_out_SOPVolatility_PSI_FP_Mtrl[TIME_WEEK_COLUMN].astype(str)
        print_df(df_out_SOPVolatility_PSI_FP_Mtrl, 'STEP4 by 7.1.2 ____ df_out_SOPVolatility_PSI_FP_Mtrl .... create')

        #--------------------------------------------------------------------------------------------------------------- W-01 처리
        df_out_SOPVolatility_PSI_FP_SET_TEMP = df_out_SOPVolatility_PSI_FP_SET[
            (df_out_SOPVolatility_PSI_FP_SET[COMPARE_WITH_COLUMN] == 'W-01') &
            (df_out_SOPVolatility_PSI_FP_SET[TIME_WEEK_COLUMN] < VAL_CURRENTWEEK)
        ].copy()
        df_out_SOPVolatility_PSI_FP_SET_TEMP[COMPARE_WITH_COLUMN] = 'W-00'
        df_out_SOPVolatility_PSI_FP_SET = pd.concat([df_out_SOPVolatility_PSI_FP_SET, df_out_SOPVolatility_PSI_FP_SET_TEMP], axis=0)
        print_df(df_out_SOPVolatility_PSI_FP_SET, 'STEP4 by 7.1.3 ____ df_out_SOPVolatility_PSI_FP_SET .... create')

        df_out_SOPVolatility_PSI_FP_Mtrl_TEMP = df_out_SOPVolatility_PSI_FP_Mtrl[
            (df_out_SOPVolatility_PSI_FP_Mtrl[COMPARE_WITH_COLUMN] == 'W-01') &
            (df_out_SOPVolatility_PSI_FP_Mtrl[TIME_WEEK_COLUMN] < VAL_CURRENTWEEK)
        ].copy()
        df_out_SOPVolatility_PSI_FP_Mtrl_TEMP[COMPARE_WITH_COLUMN] = 'W-00'
        df_out_SOPVolatility_PSI_FP_Mtrl = pd.concat([df_out_SOPVolatility_PSI_FP_Mtrl, df_out_SOPVolatility_PSI_FP_Mtrl_TEMP], axis=0)
        print_df(df_out_SOPVolatility_PSI_FP_Mtrl, 'STEP4 by 7.1.4 ____ df_out_SOPVolatility_PSI_FP_Mtrl .... create')

        #--------------------------------------------------------------------------------------------------------------- FirstWeek
        if str(VAL_CURRENTWEEK) != str(VAL_FIRSTWEEK):
            val_compare_with = 'W-' + str(VAL_LASTWEEK_CAP + 1).zfill(2)
            note(f'---------------> FirstWeek 진입 : {val_compare_with}')

            df_out_SOPVolatility_MonthlyL_FP_SET[TIME_WEEK_COLUMN] = df_out_SOPVolatility_MonthlyL_FP_SET[TIME_WEEK_COLUMN].astype(str)
            df_out_SOPVolatility_MonthlyL_FP_SET[COMPARE_WITH_COLUMN] = df_out_SOPVolatility_MonthlyL_FP_SET[COMPARE_WITH_COLUMN].astype(str)
            df_out_SOPVolatility_MonthlyL_FP_SET = remove_duplicate_indices(df_out_SOPVolatility_MonthlyL_FP_SET)
            print_df(df_out_SOPVolatility_MonthlyL_FP_SET, 'STEP4 by 7.1.5 ____ df_out_SOPVolatility_MonthlyL_FP_SET .... select')

            df_out_SOPVolatility_MonthlyL_FP_SET_TEMP = df_out_SOPVolatility_MonthlyL_FP_SET[
                (df_out_SOPVolatility_MonthlyL_FP_SET[COMPARE_WITH_COLUMN] == val_compare_with) &
                (df_out_SOPVolatility_MonthlyL_FP_SET[TIME_WEEK_COLUMN] >= VAL_FIRSTWEEK) &
                (df_out_SOPVolatility_MonthlyL_FP_SET[TIME_WEEK_COLUMN] < VAL_CURRENTWEEK)
            ].copy()
            print_df(df_out_SOPVolatility_MonthlyL_FP_SET_TEMP, 'STEP4 by 7.1.6 ____ df_out_SOPVolatility_MonthlyL_FP_SET_TEMP .... select')

            df_out_SOPVolatility_MonthlyL_FP_SET_TEMP['WeekDiff'] = (
                df_out_SOPVolatility_MonthlyL_FP_SET_TEMP[COMPARE_WITH_COLUMN]
                .str.split('-').str[1]
                .astype(int)
                .sub(1)  # 1을 빼기
                .map(lambda x: f'{x:02d}')  # 2자리 숫자로 포맷팅
            )
            df_out_SOPVolatility_MonthlyL_FP_SET_TEMP[COMPARE_WITH_COLUMN] = 'W-' + df_out_SOPVolatility_MonthlyL_FP_SET_TEMP['WeekDiff'].astype(str)
            df_out_SOPVolatility_MonthlyL_FP_SET_TEMP = df_out_SOPVolatility_MonthlyL_FP_SET_TEMP.drop('WeekDiff', axis=1, errors='ignore')
            print_df(df_out_SOPVolatility_MonthlyL_FP_SET_TEMP, 'STEP4 by 7.1.7 ____ df_out_SOPVolatility_MonthlyL_FP_SET_TEMP .... create')

            df_out_SOPVolatility_MonthlyL_FP_SET = pd.concat([df_out_SOPVolatility_MonthlyL_FP_SET, df_out_SOPVolatility_MonthlyL_FP_SET_TEMP], axis=0)
            print_df(df_out_SOPVolatility_MonthlyL_FP_SET, 'STEP4 by 7.1.8 ____ df_out_SOPVolatility_MonthlyL_FP_SET .... create')

            #-----------------------------------------------------------------------------------------------------------
            df_out_SOPVolatility_MonthlyL_FP_Mtrl = remove_duplicate_indices(df_out_SOPVolatility_MonthlyL_FP_Mtrl)
            df_out_SOPVolatility_MonthlyL_FP_Mtrl[TIME_WEEK_COLUMN] = df_out_SOPVolatility_MonthlyL_FP_Mtrl[TIME_WEEK_COLUMN].astype(str)

            df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP = df_out_SOPVolatility_MonthlyL_FP_Mtrl[
                (df_out_SOPVolatility_MonthlyL_FP_Mtrl[COMPARE_WITH_COLUMN] == val_compare_with) &
                (df_out_SOPVolatility_MonthlyL_FP_Mtrl[TIME_WEEK_COLUMN] >= str(VAL_FIRSTWEEK)) &
                (df_out_SOPVolatility_MonthlyL_FP_Mtrl[TIME_WEEK_COLUMN] <  str(VAL_CURRENTWEEK))
            ].copy()
            print_df(df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP, 'STEP4 by 7.1.9 ____ df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP .... select')

            df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP['WeekDiff'] = (
                df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP[COMPARE_WITH_COLUMN]
                .str.split('-').str[1]
                .astype(int)
                .sub(1)  # 1을 빼기
                .map(lambda x: f'{x:02d}')  # 2자리 숫자로 포맷팅
            )
            df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP[COMPARE_WITH_COLUMN] = 'W-' + df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP['WeekDiff'].astype(str)
            df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP = df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP.drop('WeekDiff', axis=1, errors='ignore')
            print_df(df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP, 'STEP4 by 7.1.10 ____ df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP .... modify')

            df_out_SOPVolatility_MonthlyL_FP_Mtrl = pd.concat([df_out_SOPVolatility_MonthlyL_FP_Mtrl, df_out_SOPVolatility_MonthlyL_FP_Mtrl_TEMP], axis=0)
            print_df(df_out_SOPVolatility_MonthlyL_FP_Mtrl, 'STEP4 by 7.1.11 ____ df_out_SOPVolatility_MonthlyL_FP_Mtrl .... create')

        step('=====> STEP4 by 7.1 End')



        # STEP 7.2 : df_in_MfgActualMtrl Data 처리
        step('=====> STEP4 by 7.2 Start : 과거 실적 Data 처리')

        # 7.2.1
        df_PSI_AR = df_in_MfgActualMtrl[(df_in_MfgActualMtrl[ITEM_TYPE_COLUMN] == 'SubAssembly')].copy()
        columns_defaults = {
            ANALYSIS_OBJECT_COLUMN: 'MTRL REQ',
            ANALYSIS_METHOD_COLUMN: 'PSI',
            CATEGORY_CATEGORY_COLUMN: 'MFG WEEK_Actual Result',
            COMPARE_WITH_COLUMN: 'W-00',
        }
        df_PSI_AR = df_PSI_AR.assign(**columns_defaults)

        df_PSI_AR.rename(columns={'Mfg Actual Mtrl_Consume Qty' : SOP_VOLATILITY_SET_VOLATILITY_COLUMN}, inplace=True)

        df_out_SOPVolatility_PSI_AR_SET = pd.concat([df_out_SOPVolatility_PSI_AR_SET, df_PSI_AR], axis=0)
        print_df(df_out_SOPVolatility_PSI_AR_SET, 'STEP4 by 7.2.1.1 ____ df_out_SOPVolatility_PSI_AR_SET .... create')

        df_PSI_AR = df_in_MfgActualMtrl[(df_in_MfgActualMtrl[ITEM_TYPE_COLUMN] == 'RawMaterials')].copy()
        columns_defaults = {
            ANALYSIS_OBJECT_COLUMN: 'MTRL REQ',
            ANALYSIS_METHOD_COLUMN: 'PSI',
            CATEGORY_CATEGORY_COLUMN: 'MFG WEEK_Actual Result',
            COMPARE_WITH_COLUMN: 'W-00',
        }
        df_PSI_AR = df_PSI_AR.assign(**columns_defaults)
        df_PSI_AR.rename(columns={'Mfg Actual Mtrl_Consume Qty' : SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN}, inplace=True)
        print_df(df_out_SOPVolatility_PSI_AR_Mtrl, 'STEP4 by 7.2.1.2 ____ df_out_SOPVolatility_PSI_AR_Mtrl .... select')

        df_out_SOPVolatility_PSI_AR_Mtrl = pd.concat([df_out_SOPVolatility_PSI_AR_Mtrl, df_PSI_AR], axis=0)
        print_df(df_out_SOPVolatility_PSI_AR_Mtrl, 'STEP4 by 7.2.1.3 ____ df_out_SOPVolatility_PSI_AR_Mtrl .... create')

        # 7.2.2
        if str(VAL_CURRENTWEEK) != str(VAL_FIRSTWEEK):
            df_PSI_AR = df_in_MfgActualMtrl[
                (df_in_MfgActualMtrl[TIME_WEEK_COLUMN].astype(str) >= VAL_FIRSTWEEK) &
                (df_in_MfgActualMtrl[TIME_WEEK_COLUMN].astype(str) <  VAL_CURRENTWEEK) &
                (df_in_MfgActualMtrl[ITEM_TYPE_COLUMN] == 'SubAssembly')
            ].copy()
            columns_defaults = {
                ANALYSIS_OBJECT_COLUMN: 'MTRL REQ',
                ANALYSIS_METHOD_COLUMN: 'Monthly_LastWeek',
                CATEGORY_CATEGORY_COLUMN: 'MFG WEEK_Actual Result',
                COMPARE_WITH_COLUMN: 'W-' + str(VAL_LASTWEEK_CAP).zfill(2),
            }
            df_PSI_AR = df_PSI_AR.assign(**columns_defaults)
            df_PSI_AR.rename(columns={'Mfg Actual Mtrl_Consume Qty' : SOP_VOLATILITY_SET_VOLATILITY_COLUMN}, inplace=True)

            df_out_SOPVolatility_PSI_AR_SET = pd.concat([df_out_SOPVolatility_PSI_AR_SET, df_PSI_AR], axis=0)
            print_df(df_out_SOPVolatility_PSI_AR_SET, 'STEP4 by 7.2.2.1 ____ df_out_SOPVolatility_PSI_AR_SET .... create')

            df_PSI_AR = df_in_MfgActualMtrl[
                (df_in_MfgActualMtrl[TIME_WEEK_COLUMN].astype(str) >= VAL_FIRSTWEEK) &
                (df_in_MfgActualMtrl[TIME_WEEK_COLUMN].astype(str) <  VAL_CURRENTWEEK) &
                (df_in_MfgActualMtrl[ITEM_TYPE_COLUMN] == 'RawMaterials')
            ].copy()
            columns_defaults = {
                ANALYSIS_OBJECT_COLUMN: 'MTRL REQ',
                ANALYSIS_METHOD_COLUMN: 'Monthly_LastWeek',
                CATEGORY_CATEGORY_COLUMN: 'SOP WEEK_Actual Result',
                COMPARE_WITH_COLUMN: 'W-' + str(VAL_LASTWEEK_CAP).zfill(2),
            }
            df_PSI_AR = df_PSI_AR.assign(**columns_defaults)
            df_PSI_AR.rename(columns={'Mfg Actual Mtrl_Consume Qty' : SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN}, inplace=True)

            df_out_SOPVolatility_PSI_AR_Mtrl = pd.concat([df_out_SOPVolatility_PSI_AR_Mtrl, df_PSI_AR], axis=0)
            print_df(df_out_SOPVolatility_PSI_AR_Mtrl, 'STEP4 by 7.2.2.2 ____ df_out_SOPVolatility_PSI_AR_Mtrl .... create')

        step('=====> STEP4 by 7.2 End')



        # STEP 8.1 : df_out_SOPVolatility_SET, df_out_SOPVolatility_Mtrl 최종 Data 처리
        step('=====> STEP4 by 8.1 Start : df_out_SOPVolatility_SET, df_out_SOPVolatility_Mtrl 최종 Data 처리')

        df_out_SOPVolatility_SET = pd.concat([
            df_out_SOPVolatility_PSI_FP_SET, df_out_SOPVolatility_PSI_AR_SET, df_out_SOPVolatility_Weekly_SET,
            df_out_SOPVolatility_MonthlyF_SET, df_out_SOPVolatility_MonthlyL_FP_SET, df_out_SOPVolatility_MonthlyL_AR_SET,
        ], axis=0)
        df_out_SOPVolatility_SET[TIME_WEEK_COLUMN] = df_out_SOPVolatility_SET[TIME_WEEK_COLUMN].astype(str)
        df_out_SOPVolatility_SET = df_out_SOPVolatility_SET.groupby([
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN,
            TO_LOCATION_COLUMN, TO_ITEM_COLUMN, CATEGORY_CATEGORY_COLUMN,
            COMPARE_WITH_COLUMN, ANALYSIS_OBJECT_COLUMN, ANALYSIS_METHOD_COLUMN
        ], as_index=False)[SOP_VOLATILITY_SET_VOLATILITY_COLUMN].sum()
        df_out_SOPVolatility_SET = df_out_SOPVolatility_SET[df_out_SOPVolatility_SET[TIME_WEEK_COLUMN] > VAL_2YEARS_AGO_WEEK]
        print_df(df_out_SOPVolatility_SET, 'STEP4 by 8.1.1 ____ df_out_SOPVolatility_SET .... final')


        df_out_SOPVolatility_Mtrl = pd.concat([
            df_out_SOPVolatility_PSI_FP_Mtrl, df_out_SOPVolatility_PSI_AR_Mtrl, df_out_SOPVolatility_Weekly_Mtrl,
            df_out_SOPVolatility_MonthlyF_Mtrl, df_out_SOPVolatility_MonthlyL_FP_Mtrl, df_out_SOPVolatility_MonthlyL_AR_Mtrl,
        ], axis=0)
        df_out_SOPVolatility_Mtrl[TIME_WEEK_COLUMN] = df_out_SOPVolatility_Mtrl[TIME_WEEK_COLUMN].astype(str)
        df_out_SOPVolatility_Mtrl = df_out_SOPVolatility_Mtrl.groupby([
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_COLUMN, TO_ITEM_COLUMN,
            ITEM_METERIAL_COLUMN, CATEGORY_CATEGORY_COLUMN, COMPARE_WITH_COLUMN,
            ANALYSIS_OBJECT_COLUMN, ANALYSIS_METHOD_COLUMN,
        ], as_index=False)[SOP_VOLATILITY_MTRL_VOLATILITY_COLUMN].sum()
        df_out_SOPVolatility_Mtrl = df_out_SOPVolatility_Mtrl[df_out_SOPVolatility_Mtrl[TIME_WEEK_COLUMN] > VAL_2YEARS_AGO_WEEK]
        print_df(df_out_SOPVolatility_Mtrl, 'STEP4 by 8.1.2 ____ df_out_SOPVolatility_Mtrl .... final')

        df_out_SOPVolatilityMap = {ANALYSIS_OBJECT_COLUMN, SOP_VOLATILITY_MAP_ASN_COLUMN}
        if (VAL_VERSION_TYPE in ['Pre', 'Main']):
            df_out_SOPVolatilityMap = pd.DataFrame({
                ANALYSIS_OBJECT_COLUMN: ['SET MP', 'SET SOP', 'LCM MP', 'LCM SOP', 'MTRL REQ'],
                SOP_VOLATILITY_MAP_ASN_COLUMN           : [ 1,         0,        1,        0,         1       ],
            })
        elif (VAL_VERSION_TYPE == 'Sync'):
            df_out_SOPVolatilityMap = pd.DataFrame({
                ANALYSIS_OBJECT_COLUMN: ['SET MP', 'SET SOP', 'LCM MP', 'LCM SOP', 'MTRL REQ'],
                SOP_VOLATILITY_MAP_ASN_COLUMN           : [ 1,        1,         1,        1,         1       ],
            })
        else:
            df_out_SOPVolatilityMap = pd.DataFrame({
                ANALYSIS_OBJECT_COLUMN: ['SET MP', 'SET SOP', 'LCM MP', 'LCM SOP', 'MTRL REQ'],
                SOP_VOLATILITY_MAP_ASN_COLUMN           : [ 0,         0,        0,        0,         0       ],
            })

        df_out_SOPVolatilityMap.insert(0, VERSION_NAME_COLUMN, paramOutVersion)
        step('=====> STEP4 by 8.1 End')

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        dataframes = {
            'df_out_SOPVolatility_SET': df_out_SOPVolatility_SET,
            'df_out_SOPVolatility_Mtrl': df_out_SOPVolatility_Mtrl,
            'df_out_SOPVolatilityMap': df_out_SOPVolatilityMap,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPVolatility_SET = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SOPVolatility_SET = pd.DataFrame([], columns=[])
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