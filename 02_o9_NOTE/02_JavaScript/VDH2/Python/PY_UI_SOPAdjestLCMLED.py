"""
* 프로그램명
    - PY_UI_SOPAdjestLCMLED

* 내용
    - LED LCM SOP Adjsut 수량 할당

* 변경이력
    - 2026.03.18 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek        : Select (&CurrentWeek);
    - df_in_AllWeek         : Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
    - df_in_SOPWLED         : Select ([BOM Info].[BOM Version] * [Belongings].[Belongings] * [Item].[Item] * [Item Component].[Item Component] * [Item Material].[Item Material] * [LED Black Rank].[LED Black Rank] * [LED Rank].[LED Rank] * [Location].[Location] * [Sales Domain].[Ship To] * [Sequence].[Sequence] * [Sub Location].[Sub Location] * [Time].[Week] * [To Time].[To Week] * [To Item].[To Item] * [To Location].[To Location] * [To Trans Mode].[To Trans Mode] * [Trans Mode].[Trans Mode] * [Week1].[Week1] * [Week2].[Week2] ) on row, ({Measure.[SOP W LED_SET SOP Adj Qty], Measure.[SOP W LED_SET SOP Chg Qty], Measure.[SOP W LED_LCM MFG Qty], Measure.[SOP W LED_LCM SOP Adj Qty], Measure.[SOP W LED_LCM SOP ID], Measure.[SOP W LED_LCM SOP Qty], Measure.[SOP W LED_SET MFG Qty], Measure.[SOP W LED_SET SOP Qty], Measure.[SOP W LED_SOP ID]}) on column where {[Version].[Version Name]};
    - df_in_ModuleSOPAdjustCabinetLED : Select ([BOM Info].[BOM Version] * [Item].[Item] * [LED Black Rank].[LED Black Rank] * [LED Rank].[LED Rank] * [Location].[Location] * [Sales Domain].[Ship To] * [Sequence].[Sequence] * [Time].[Week] * [Trans Mode].[Trans Mode] * [To Location].[To Location] * [To Time].[To Week] ) on row, ({Measure.[Module SOP Adjust Cabinet LED_SHT Qty], Measure.[Module SOP Adjust Cabinet LED_SOP Qty]}) on column where {[Version].[Version Name]};
    - df_in_SETModuleConsumeRateLED : Select ([BOM Info].[BOM Version] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Time].[Week] * [To Item].[To Item] * [To Location].[To Location] * [To Time].[To Week] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SET Module Consume Rate LED_Module BOD LT], Measure.[SET Module Consume Rate LED_Module MFG LT], Measure.[SET Module Consume Rate LED_Module Needed Qty], Measure.[SET Module Consume Rate LED_Module Yield], Measure.[SET Module Consume Rate LED_SET MFG LT], Measure.[SET Module Consume Rate LED_SET Service Rate]}) on column where {[Version].[Version Name]};
    - df_in_ModuleSOPAdjustLED : Select ([Location].[Location] * [To Location].[To Location] * [Sales Domain].[Ship To] * [To Item].[To Item] * [Sequence].[Sequence] * [Item].[Item] * [Sub Location].[Sub Location] * [Belongings].[Belongings] * [LED Black Rank].[LED Black Rank] * [Trans Mode].[Trans Mode] * [BOM Info].[BOM Version] * [LED Rank].[LED Rank] ) on row, ({Measure.[Module SOP Adjust LED_CHG Qty], Measure.[Module SOP Adjust LED_Defect], Measure.[Module SOP Adjust LED_MFG Week], Measure.[Module SOP Adjust LED_SOP ID], Measure.[Module SOP Adjust LED_SOP Week], Measure.[Module SOP Adjust LED_Safety Stock], Measure.[Module SOP Adjust LED_Sales], Measure.[Module SOP Adjust LED_Service], Measure.[Module SOP Adjust LED_Total SOP]}) on column where {[Version].[Version Name]};


* Flow Summary
    - 1.


* Output Table
    - df_out_log
    - df_out_logDetail
    - df_out_sopw_led
    - df_out_module_sop_adjust_cabinet_led
    - df_out_module_sop_adjust_led


* 데이타 초기화
    -

* RUN 스크립트
    - exec procedure PR_UI_SOPAdjestLCMLED {"Version":"CWV_MP"};

    - EXEC plugin instance [PY_UI_SOPAdjestLCMLED] for measures {[SOP W LED_LCM SOP Adj Qty]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    -
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
import pytz
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SOPAdjestLCMLED'
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


def filter_dataframe(dataframe, version_column, time_week_column, pre_version, plan_horizon):
    return dataframe.loc[
        (dataframe[version_column] != pre_version) &
        (dataframe[time_week_column].isin(plan_horizon[time_week_column]))
    ].copy()



def set_unique_combinations(df: pd.DataFrame,
                            weeks_df: pd.DataFrame,
                            columns: list[str]) -> pd.DataFrame:
    """
    df: 실제 데이터
    weeks_df: TIME_WEEK_COLUMN 값(주차) 목록을 가진 데이터프레임(최소 TIME_WEEK_COLUMN 컬럼 필요)
    columns: df에서 완전성 체크할 컬럼들 (TIME_WEEK_COLUMN 포함)
    return: df에 존재하지 않는 (조합×주차) 행들
    """
    if TIME_WEEK_COLUMN not in columns:
        raise ValueError(f"`columns`에는 {TIME_WEEK_COLUMN}가 포함되어야 합니다.")

    dims = [c for c in columns if c != TIME_WEEK_COLUMN]

    # dims 고유 조합 (관측된 조합만 유지)
    unique_dims = df.loc[:, dims].drop_duplicates(ignore_index=True)

    # 주차 고유값
    weeks = (weeks_df.loc[:, [TIME_WEEK_COLUMN]].drop_duplicates()[TIME_WEEK_COLUMN].to_numpy())

    n = len(unique_dims)
    m = len(weeks)

    if n == 0 or m == 0:
        return df.loc[:, columns].head(0).copy()

    # (dims 고유조합) × (weeks) 전체 조합 생성
    all_possible = unique_dims.loc[unique_dims.index.repeat(m)].reset_index(drop=True)
    all_possible[TIME_WEEK_COLUMN] = np.tile(weeks, n)

    # df에 실제 존재하는 조합
    existing = df.loc[:, columns].drop_duplicates(ignore_index=True)

    # anti-join: all_possible 중 df에 없는 것만
    out = all_possible.merge(existing, on=columns, how="left", indicator=True)
    out = out.loc[out["_merge"].eq("left_only"), columns].reset_index(drop=True)

    return out


def get_current_date_str(tz: str | None = None) -> str:
    """
    현재 시각을 'YYYY-MM-DD HH:MM:SS' 형식 문자열로 반환.
    tz 인자로 'UTC', 'KST' 등의 타임존을 지정 가능.
    - 'UTC': UTC 기준
    - 'KST' 또는 'Asia/Seoul': 한국 시간 기준
    - None 또는 기타: 로컬 타임존 기준
    """
    if isinstance(tz, str):
        tz_upper = tz.upper()
        if tz_upper == "UTC":
            now = datetime.datetime.now(datetime.timezone.utc)
        elif tz_upper == "KST" or tz == "Asia/Seoul":
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.datetime.now(kst)
        else:
            now = datetime.datetime.now()
    else:
        now = datetime.datetime.now()

    return now.strftime("%Y-%m-%d %H:%M:%S")


def apply_sop_week_mapping(df_AllWeek: pd.DataFrame,
                           target_df: pd.DataFrame,
                           time_week_col: str,
                           week_col: str,
                           lt_col: str,
                           make_week_col: str):
    """
    target_df 의 lt_col 컬럼 값을 기준으로 week_col 컬럼의 값을 수정하여 make_week_col 컬럼에 설정.
    """
    week_to_idx = dict(zip(df_AllWeek[time_week_col], df_AllWeek.index))
    idx_to_week = dict(zip(df_AllWeek.index, df_AllWeek[time_week_col]))

    base_idx = target_df[week_col].map(week_to_idx)
    target_idx = base_idx + target_df[lt_col]
    max_idx = len(df_AllWeek) - 1
    valid_mask = target_idx.between(0, max_idx)

    target_df[make_week_col] = None
    target_df.loc[valid_mask, make_week_col] = target_idx[valid_mask].map(idx_to_week)

    return target_df


def cleanup_merged_columns(df, columns, keep='x', drop='y'):
    """
    Merge 후 생성된 _x, _y suffix 컬럼 정리

    Args:
        df: 정리할 DataFrame
        columns: 정리할 컬럼 이름 리스트
        keep: 유지할 suffix (기본값: 'x')
        drop: 삭제할 suffix (기본값: 'y')
        inplace: 원본 수정 여부 (기본값: True)

    Returns:
        정리된 DataFrame (inplace=False일 경우)
    """
    rename_dict = {f'{col}_{keep}': col for col in columns}
    columns_to_drop = [f'{col}_{drop}' for col in columns]

    df.rename(columns=rename_dict, inplace=True)
    df.drop(columns=columns_to_drop, inplace=True)


def ultra_fast_replace_to_none(df):
    """dtype를 최대한 유지하면서 문자열 결측 표현과 숫자 결측을 정리한다."""
    df = df.copy()

    # object 컬럼과 숫자 컬럼 분리
    obj_cols = df.select_dtypes(include=["object"]).columns
    num_cols = df.select_dtypes(include=["number"]).columns

    # object 컬럼: 문자열 형태의 결측/특정 값만 None으로 치환
    if len(obj_cols) > 0:
        obj_data = df[obj_cols].to_numpy(dtype=object, copy=True)
        mask = (
            (obj_data == "nan") |
            (obj_data == "<NA>") |
            (obj_data == "0") |
            pd.isna(obj_data)
        )
        obj_data[mask] = None
        df[obj_cols] = obj_data

    # 숫자 컬럼:
    # - int 계열은 nullable integer(Int64)로 바꿔서 dtype 유지
    # - float 계열은 nullable float(Float64)로 바꿔서 dtype 유지
    for col in num_cols:
        if not df[col].isna().any():
            continue

        if pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype("Int64")
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype("Float64")
        else:
            # 숫자처럼 보이지만 object로 들어온 경우 대비
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if pd.api.types.is_integer_dtype(df[col]):
                df[col] = df[col].astype("Int64")
            else:
                df[col] = df[col].astype("Float64")

    return df




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
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_SOPWLED = read_csv_file("df_in_SOPWLED")
            df_in_ModuleSOPAdjustCabinetLED = read_csv_file("df_in_ModuleSOPAdjustCabinetLED")
            df_in_SETModuleConsumeRateLED = read_csv_file("df_in_SETModuleConsumeRateLED")
            df_in_ModuleSOPAdjustLED = read_csv_file("df_in_ModuleSOPAdjustLED")


        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_SOPWLED': df_in_SOPWLED,
            'df_in_ModuleSOPAdjustCabinetLED': df_in_ModuleSOPAdjustCabinetLED,
            'df_in_SETModuleConsumeRateLED': df_in_SETModuleConsumeRateLED,
            'df_in_ModuleSOPAdjustLED': df_in_ModuleSOPAdjustLED,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        LOCATION_COLUMN = 'Location.[Location]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SALES_DOMAIN_SHIP_TO_COLUMN = 'Sales Domain.[Ship To]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        SOP_ID_COLUMN = 'SOP ID.[SOP ID]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        BELONGINGS_COLUMN = 'Belongings.[Belongings]'
        LED_BLACK_RANK_COLUMN = 'LED Black Rank.[LED Black Rank]'
        LED_RANK_COLUMN = 'LED Rank.[LED Rank]'

        SOP_W_LED_BOD_NAME_COLUMN = 'SOP W LED_BOD Name'
        SOP_W_LED_LCM_MFG_QTY_COLUMN = 'SOP W LED_LCM MFG Qty'
        SOP_W_LED_LCM_SOP_ADJ_QTY_COLUMN = 'SOP W LED_LCM SOP Adj Qty'
        SOP_W_LED_LCM_SOP_ID_COLUMN = 'SOP W LED_LCM SOP ID'
        SOP_W_LED_LCM_SOP_QTY_COLUMN = 'SOP W LED_LCM SOP Qty'
        SOP_W_LED_SET_MFG_QTY_COLUMN = 'SOP W LED_SET MFG Qty'
        SOP_W_LED_SET_SOP_QTY_COLUMN = 'SOP W LED_SET SOP Qty'
        SOP_W_LED_SOP_ID_COLUMN = 'SOP W LED_SOP ID'
        SOP_W_LED_SET_SOP_ADJ_QTY_COLUMN = 'SOP W LED_SET SOP Adj Qty'
        SOP_W_LED_SET_SOP_CHG_QTY_COLUMN = 'SOP W LED_SET SOP Chg Qty'

        MODULE_SOP_ADJUST_CABINET_LED_SHT_QTY_COLUMN = 'Module SOP Adjust Cabinet LED_SHT Qty'
        MODULE_SOP_ADJUST_CABINET_LED_SOP_QTY_COLUMN = 'Module SOP Adjust Cabinet LED_SOP Qty'
        MODULE_SOP_ADJUST_CABINET_LED_SHORT_QTY_COLUMN = 'Module SOP Adjust Cabinet LED_SHORT Qty'

        SET_MODULE_CONSUME_RATE_LED_MODULE_BOD_LT_COLUMN = 'SET Module Consume Rate LED_Module BOD LT'
        SET_MODULE_CONSUME_RATE_LED_MODULE_MFG_LT_COLUMN = 'SET Module Consume Rate LED_Module MFG LT'
        SET_MODULE_CONSUME_RATE_LED_MODULE_NEEDED_QTY_COLUMN = 'SET Module Consume Rate LED_Module Needed Qty'
        SET_MODULE_CONSUME_RATE_LED_MODULE_YIELD_COLUMN = 'SET Module Consume Rate LED_Module Yield'
        SET_MODULE_CONSUME_RATE_LED_SET_MFG_LT_COLUMN = 'SET Module Consume Rate LED_SET MFG LT'
        SET_MODULE_CONSUME_RATE_LED_SET_SERVICE_RATE_COLUMN = 'SET Module Consume Rate LED_SET Service Rate'

        MODULE_SOP_ADJUST_LED_BOD_NAME_COLUMN = 'Module SOP Adjust LED_BOD Name'
        MODULE_SOP_ADJUST_LED_CHG_QTY_COLUMN = 'Module SOP Adjust LED_CHG Qty'
        MODULE_SOP_ADJUST_LED_DEFECT_COLUMN = 'Module SOP Adjust LED_Defect'
        MODULE_SOP_ADJUST_LED_MFG_WEEK_COLUMN = 'Module SOP Adjust LED_MFG Week'
        MODULE_SOP_ADJUST_LED_SOP_ID_COLUMN = 'Module SOP Adjust LED_SOP ID'
        MODULE_SOP_ADJUST_LED_SOP_WEEK_COLUMN = 'Module SOP Adjust LED_SOP Week'
        MODULE_SOP_ADJUST_LED_SAFETY_STOCK_COLUMN = 'Module SOP Adjust LED_Safety Stock'
        MODULE_SOP_ADJUST_LED_SALES_COLUMN = 'Module SOP Adjust LED_Sales'
        MODULE_SOP_ADJUST_LED_SERVICE_COLUMN = 'Module SOP Adjust LED_Service'
        MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN = 'Module SOP Adjust LED_Total SOP'

        SOP_ADJUST_SET_W_LED_SOP_ADJ_SHORT_QTY_COLUMN = 'SOP Adjust SET W LED_SOP Adj Short Qty'
        SOP_ADJUST_SET_W_LED_SOP_WEEK_COLUMN = 'SOP Adjust SET W LED_SOP Week'
        SOP_ADJUST_SET_W_LED_CHG_QTY_COLUMN = 'SOP Adjust SET W LED_Chg Qty'
        SOP_ADJUST_SET_W_LED_SOP_ADJ_QTY_COLUMN = 'SOP Adjust SET W LED_SOP Adj Qty'
        SOP_ADJUST_SET_W_LED_SOP_QTY_COLUMN = 'SOP Adjust SET W LED_SOP Qty'

        version_columns = [VERSION_NAME_COLUMN]

        # SOP W LED
        df_sopw_key_columns = [
            BOM_INFO_BOM_VERSION_COLUMN, BELONGINGS_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN,
            LED_BLACK_RANK_COLUMN, LED_RANK_COLUMN, LOCATION_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, SEQUENCE_COLUMN,
            SUB_LOCATION_COLUMN, TIME_WEEK_COLUMN, TO_TIME_TO_WEEK_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,
            TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, WEEK1_COLUMN, WEEK2_COLUMN,
        ]
        df_sopw_qty_columns = [
            SOP_W_LED_SET_SOP_ADJ_QTY_COLUMN, SOP_W_LED_SET_SOP_CHG_QTY_COLUMN,
            SOP_W_LED_LCM_SOP_QTY_COLUMN, SOP_W_LED_LCM_SOP_ADJ_QTY_COLUMN,
            SOP_W_LED_LCM_MFG_QTY_COLUMN, SOP_W_LED_SET_MFG_QTY_COLUMN, SOP_W_LED_SET_SOP_QTY_COLUMN
        ]

        # Module SOP Adjustment Cabinet LED
        df_module_cabinet_key_columns = [
            BOM_INFO_BOM_VERSION_COLUMN, ITEM_COLUMN, LED_BLACK_RANK_COLUMN, LED_RANK_COLUMN, LOCATION_COLUMN,
            SALES_DOMAIN_SHIP_TO_COLUMN, SEQUENCE_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,
            TO_TIME_TO_WEEK_COLUMN,
        ]
        df_module_cabinet_qty_columns = [
            MODULE_SOP_ADJUST_CABINET_LED_SOP_QTY_COLUMN,
        ]

        # Module SOP Adjustment LED
        df_module_sop_adj_key_columns = [
            LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, SALES_DOMAIN_SHIP_TO_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SEQUENCE_COLUMN,
            ITEM_COLUMN, SUB_LOCATION_COLUMN, BELONGINGS_COLUMN, LED_BLACK_RANK_COLUMN, TRANS_MODE_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            LED_RANK_COLUMN,
        ]
        df_module_sop_adj_qty_columns = [
            MODULE_SOP_ADJUST_LED_CHG_QTY_COLUMN, MODULE_SOP_ADJUST_LED_DEFECT_COLUMN, MODULE_SOP_ADJUST_LED_SALES_COLUMN,
            MODULE_SOP_ADJUST_LED_SERVICE_COLUMN, MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN,
        ]


        fn_sopw_columns = version_columns + df_sopw_key_columns + df_sopw_qty_columns
        fn_module_cabinet_columns = version_columns + df_module_cabinet_key_columns + df_module_cabinet_qty_columns
        fn_module_sop_adj_columns = version_columns + df_module_sop_adj_key_columns + df_module_sop_adj_qty_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # SOPW_LED 와 Module SOP Adjustment LED 를 조인하여 증량,감량,Add 추출
        df_temp = pd.merge(
            df_in_SOPWLED,
            df_in_ModuleSOPAdjustLED,
            how='inner',
            on=SEQUENCE_COLUMN,
        )
        print_df(df_temp, 'STEP3 by 1.0.1  ____ df_temp .... merge[df_in_SOPWLED, df_in_SOPAdjustSETWLED]')

        columns_to_rename = [
            BOM_INFO_BOM_VERSION_COLUMN,
            BELONGINGS_COLUMN,
            ITEM_COLUMN,
            LED_BLACK_RANK_COLUMN,
            LED_RANK_COLUMN,
            LOCATION_COLUMN,
            SALES_DOMAIN_SHIP_TO_COLUMN,
            SUB_LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN,
            TRANS_MODE_COLUMN,
        ]
        cleanup_merged_columns(df_temp, columns_to_rename)
        print_df(df_temp, 'STEP3 by 1.0.2  ____ df_temp .... rename')

        int_columns = [
            MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN, SOP_W_LED_LCM_SOP_ADJ_QTY_COLUMN,
        ]
        df_temp[int_columns] = df_temp[int_columns].astype('Int64').fillna(0)

        # 증량, 감량 추출
        qty_chg = df_temp[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN] - df_temp[SOP_W_LED_LCM_SOP_ADJ_QTY_COLUMN]
        mask = qty_chg != 0
        df_temp.loc[:, 'qty_chg'] = qty_chg
        df_qty_chg = df_temp.loc[mask].copy()
        print_df(df_qty_chg, 'STEP3 by 1.0.3  ____ df_qty_chg .... qty_chg != 0')



        # Add 추출
        seq_col = df_in_ModuleSOPAdjustLED[SEQUENCE_COLUMN].astype("string").str.strip()
        df_qty_add = df_in_ModuleSOPAdjustLED[seq_col.isna() | seq_col.isin(["", "-"])].copy()
        print_df(df_qty_add, 'STEP3 by 1.0.4  ____ df_qty_add .... seq_col.isna() | seq_col.isin(["", "-"])')




        if df_qty_chg.empty and df_qty_add.empty:
            raise CustomException(".... df_qty_chg, df_qty_add 값이 없습니다.")


        current_date = get_current_date_str('UTC')


         # 현재 week 가져오기
        mp_plan_start_week = int(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')


        # 'Sequence.[Sequence]' 컬럼의 최대값 구하기
        max_sequence_value = int(df_in_SOPWLED[SEQUENCE_COLUMN].max())
        step(f'=====> max_sequence_value : {max_sequence_value}')


        # df_in_AllWeek 필요컬럼 설정
        df_in_AllWeek[TIME_WEEK_COLUMN] = df_in_AllWeek[TIME_WEEK_COLUMN].astype(int)
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        print_df(df_in_AllWeek, 'STEP3 by 1.1  ____ df_in_AllWeek .... week uniqe')


        # SET Module Consume Rate LED Module Needed Qty 와 SET Module Consume Rate LED_SET Service Rate, SET Module Consume Rate LED_Module Yield 컬럼설정
        # SET Module Consume Rate LED Module MFG LT : 1 (Module 생산 Lead Time)
        # SET Module Consume Rate LED_SET Service Rate : 1 (서비스율)
        # SET Module Consume Rate LED_Module Yield : 1 (수율)
        defaults_1 = {
            SET_MODULE_CONSUME_RATE_LED_SET_MFG_LT_COLUMN: 0,
            SET_MODULE_CONSUME_RATE_LED_MODULE_BOD_LT_COLUMN: 0,
            SET_MODULE_CONSUME_RATE_LED_MODULE_MFG_LT_COLUMN: 1,
            SET_MODULE_CONSUME_RATE_LED_SET_SERVICE_RATE_COLUMN: 1,
            SET_MODULE_CONSUME_RATE_LED_MODULE_YIELD_COLUMN: 1,
            SET_MODULE_CONSUME_RATE_LED_MODULE_NEEDED_QTY_COLUMN: 1,
        }

        step('=====> STEP3 End')




        # ##############################################################################################################
        # # STEP 4 : output data machining
        # ##############################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : 증량, 감량 처리')

        if not df_qty_chg.empty:
            df_sopw_led_data = []
            df_module_sop_adjust_cabinet_led_data = []
            df_module_sop_adjust_led_data = []

            # Location.[Location], Item.[Item], Module SOP Adjust LED_MFG Week, To Item.[To Item],  Sub Location.[Sub Location], Trans Mode.[Trans Mode] BOM Info.[BOM Version], 으로
            #   'SET Module Consume Rate LED' 의 SET Module Consume Rate LED Module Needed Qty 와  SET Module Consume Rate LED SET Service Rate를 찾아준다
            target_df = df_qty_chg.merge(
                df_in_SETModuleConsumeRateLED,
                how='left',
                left_on=[
                    LOCATION_COLUMN, ITEM_COLUMN, MODULE_SOP_ADJUST_LED_MFG_WEEK_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN,
                    TRANS_MODE_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
                ],
                right_on=[
                    LOCATION_COLUMN, ITEM_COLUMN, TO_TIME_TO_WEEK_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN,
                    TRANS_MODE_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
                ]
            )
            print_df(target_df, 'STEP4 by 1.2.1  ____ target_df .... merge[df_in_SETModuleConsumeRateLED]')

            target_df.rename(columns={
                TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
                TO_TIME_TO_WEEK_COLUMN+'_x': TO_TIME_TO_WEEK_COLUMN,
                TO_LOCATION_TO_LOCATION_COLUMN+'_x': TO_LOCATION_TO_LOCATION_COLUMN,
            }, inplace=True)
            target_df.drop(columns=[
                TIME_WEEK_COLUMN+'_y', TO_TIME_TO_WEEK_COLUMN+'_y', TO_LOCATION_TO_LOCATION_COLUMN+'_y'
            ], inplace=True)
            print_df(target_df, 'STEP4 by 1.2.2  ____ target_df .... rename[TO_LOCATION_TO_LOCATION_COLUMN]')

            for column, default_value in defaults_1.items():
                if column in target_df.columns:
                    target_df[column] = target_df[column].fillna(default_value)
                else:
                    target_df[column] = default_value

            print_df(target_df, 'STEP4 by 1.2.3  ____ target_df .... defaults_1')

            # Module SOP Adjust LED_SOP Week = Module SOP Adjust LED_MFG Week + SET Module Consume Rate LED Module MFG LT  = 202614 + 1 = 202615
            # Module SOP Adjust LED_Defect = Module SOP Adjust LED_Total SOP * (1 - 수율 ) - 0
            # Module SOP Adjust LED_Service = Module SOP Adjust LED_Total SOP * (1 - 서비스율 ) - 0
            # Module SOP Adjust LED_Sales = Module SOP Adjust LED_Total SOP - Module SOP Adjust LED_Defect  - Module SOP Adjust LED_Service = 300
            target_df = apply_sop_week_mapping(
                df_AllWeek=df_in_AllWeek,
                target_df=target_df,
                time_week_col=TIME_WEEK_COLUMN,
                week_col=MODULE_SOP_ADJUST_LED_MFG_WEEK_COLUMN,
                lt_col=SET_MODULE_CONSUME_RATE_LED_MODULE_MFG_LT_COLUMN,
                make_week_col=MODULE_SOP_ADJUST_LED_SOP_WEEK_COLUMN,
            )
            print_df(target_df, 'STEP4 by 1.2.4  ____ target_df .... apply_sop_week_mapping')

            target_df[MODULE_SOP_ADJUST_LED_DEFECT_COLUMN] = (
                    target_df[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN] *
                    (1 - target_df[SET_MODULE_CONSUME_RATE_LED_MODULE_YIELD_COLUMN]) - 0
            ).round().astype(int)

            target_df[MODULE_SOP_ADJUST_LED_SERVICE_COLUMN] = (
                    target_df[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN] *
                    (1 - target_df[SET_MODULE_CONSUME_RATE_LED_SET_SERVICE_RATE_COLUMN]) - 0
            ).round().astype(int)

            target_df[MODULE_SOP_ADJUST_LED_SALES_COLUMN] = (
                    target_df[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN] -
                    target_df[MODULE_SOP_ADJUST_LED_DEFECT_COLUMN] -
                    target_df[MODULE_SOP_ADJUST_LED_SERVICE_COLUMN]
            )
            print_df(target_df, 'STEP4 by 1.2.5  ____ target_df .... apply_sop_week_mapping 및 컬럼설정')



            # SOP W LED 증,감량 구성
            #   SOP 변경수량 -> Module SOP Adjust LED_CHG Qty
            #   SOP 수량 -> Module SOP Adjust LED_Total SOP
            df_sopw_led = target_df.copy()
            df_sopw_led[WEEK2_COLUMN] = df_sopw_led[MODULE_SOP_ADJUST_LED_SOP_WEEK_COLUMN]
            df_sopw_led[WEEK1_COLUMN] = df_sopw_led[MODULE_SOP_ADJUST_LED_MFG_WEEK_COLUMN]
            df_sopw_led[SOP_W_LED_LCM_SOP_ADJ_QTY_COLUMN] = df_sopw_led[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN]
            df_sopw_led[SOP_W_LED_SET_SOP_CHG_QTY_COLUMN] = df_sopw_led[MODULE_SOP_ADJUST_LED_CHG_QTY_COLUMN].astype('Int64')
            df_sopw_led_data.append(df_sopw_led)
            print_df(df_sopw_led, 'STEP4 by 1.4  ____ df_sopw_led .... sopw led')


            # Module SOP Adjustment Cabinet LED 증,감량 구성
            df_module_sop_adjust_cabinet_led= target_df.copy()
            df_module_sop_adjust_cabinet_led[MODULE_SOP_ADJUST_CABINET_LED_SOP_QTY_COLUMN] = df_module_sop_adjust_cabinet_led[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN]
            df_module_sop_adjust_cabinet_led_data.append(df_module_sop_adjust_cabinet_led)
            print_df(df_module_sop_adjust_cabinet_led, 'STEP4 by 1.5  ____ df_module_sop_adjust_cabinet_led .... module sop adjust cabinet led')


            # Module SOP Adjustment LED 증,감량 구성
            df_module_sop_adjust_led = target_df.copy()
            df_module_sop_adjust_led_data.append(df_module_sop_adjust_led)
            print_df(df_module_sop_adjust_led, 'STEP4 by 1.6  ____ df_module_sop_adjust_led .... module sop adjust led')



            # 결과 합치기
            #   SOPW_LED
            df_sopw_led_result_1 = pd.concat(df_sopw_led_data, ignore_index=True) #if df_sopw_led_data else pd.DataFrame()
            print_df(df_sopw_led_result_1, 'STEP4 by 1.7.1  ____ df_sopw_led_result_1 ..... create')

            #   Module SOP Adjustment Cabinet LED
            df_module_sop_adjust_cabinet_led_result_1 = pd.concat(df_module_sop_adjust_cabinet_led_data, ignore_index=True)
            print_df(df_module_sop_adjust_cabinet_led_result_1, 'STEP4 by 1.7.2  ____ df_module_sop_adjust_cabinet_led_result_1 ..... create')

            #   Module SOP Adjustment LED
            df_module_sop_adjust_led_result_1 = pd.concat(df_module_sop_adjust_led_data, ignore_index=True)
            print_df(df_module_sop_adjust_led_result_1, 'STEP4 by 1.7.3  ____ df_module_sop_adjust_led_result_1 ..... create')

        else:
            df_sopw_led_result_1 = pd.DataFrame(columns=fn_sopw_columns)
            df_module_sop_adjust_cabinet_led_result_1 = pd.DataFrame(columns=fn_module_cabinet_columns)
            df_module_sop_adjust_led_result_1 = pd.DataFrame(columns=fn_module_sop_adj_columns)

        step('=====> STEP4 by 1 End')





        step('=====> STEP4 by 2 Start : Add 처리')

        if not df_qty_add.empty :
            df_sopw_led_data = []
            df_module_sop_adjust_cabinet_led_data = []
            df_module_sop_adjust_led_data = []

            # Location.[Location], To Location.[To Location], Time.[Week], To Time.[To Week], Item.[Item], Trans Mode.[Trans Mode], BOM Info.[BOM Version]
            #  -> 해당 정보를 바탕으로 SET Module Consume Rate LED 에서 TRANS MODE, BOM VERSION 우선순위가 가장 높은 것을 찾아준다 (우선순위값 추가 예정)
            target_df = df_qty_add.merge(
                df_in_SETModuleConsumeRateLED,
                how='left',
                left_on=[
                    LOCATION_COLUMN, ITEM_COLUMN, MODULE_SOP_ADJUST_LED_MFG_WEEK_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN,
                    TRANS_MODE_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
                ],
                right_on=[
                    LOCATION_COLUMN, ITEM_COLUMN, TO_TIME_TO_WEEK_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN,
                    TRANS_MODE_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
                ]
            )
            target_df[SEQUENCE_COLUMN] = max_sequence_value + 1
            print_df(target_df, 'STEP4 by 2.1.1  ____ target_df .... merge[df_in_SETModuleConsumeRateLED]')

            target_df.rename(columns={
                TO_LOCATION_TO_LOCATION_COLUMN+'_x': TO_LOCATION_TO_LOCATION_COLUMN,
            }, inplace=True)
            target_df.drop(columns=[
                TO_LOCATION_TO_LOCATION_COLUMN+'_y',
            ], inplace=True)
            print_df(target_df, 'STEP4 by 2.1.2  ____ target_df .... rename[TO_LOCATION_TO_LOCATION_COLUMN]')

            target_df = apply_sop_week_mapping(
                df_AllWeek=df_in_AllWeek,
                target_df=target_df,
                time_week_col=TIME_WEEK_COLUMN,
                week_col=MODULE_SOP_ADJUST_LED_MFG_WEEK_COLUMN,
                lt_col=SET_MODULE_CONSUME_RATE_LED_MODULE_MFG_LT_COLUMN,
                make_week_col=MODULE_SOP_ADJUST_LED_SOP_WEEK_COLUMN,
            )
            print_df(target_df, 'STEP4 by 2.1.3  ____ target_df .... apply_sop_week_mapping')

            target_df[MODULE_SOP_ADJUST_LED_DEFECT_COLUMN] = (
                    target_df[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN] *
                    (1 - target_df[SET_MODULE_CONSUME_RATE_LED_MODULE_YIELD_COLUMN]) - 0
            )

            target_df[MODULE_SOP_ADJUST_LED_SERVICE_COLUMN] = (
                    target_df[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN] *
                    (1 - target_df[SET_MODULE_CONSUME_RATE_LED_SET_SERVICE_RATE_COLUMN]) - 0
            )

            target_df[MODULE_SOP_ADJUST_LED_SALES_COLUMN] = (
                    target_df[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN] -
                    target_df[MODULE_SOP_ADJUST_LED_DEFECT_COLUMN] -
                    target_df[MODULE_SOP_ADJUST_LED_SERVICE_COLUMN]
            )

            for column, default_value in defaults_1.items():
                if column in target_df.columns:
                    target_df[column] = target_df[column].fillna(default_value)
                else:
                    target_df[column] = default_value

            print_df(target_df, 'STEP4 by 2.1.4  ____ target_df .... defaults_1')


            # Module SOP Adjustment Cabinet LED 구성
            df_module_sop_adjust_cabinet_led = target_df.copy()
            df_module_sop_adjust_cabinet_led[MODULE_SOP_ADJUST_CABINET_LED_SOP_QTY_COLUMN] = 0
            df_module_sop_adjust_cabinet_led[MODULE_SOP_ADJUST_CABINET_LED_SHORT_QTY_COLUMN] = 0
            df_module_sop_adjust_cabinet_led_data.append(df_module_sop_adjust_cabinet_led)
            print_df(df_module_sop_adjust_cabinet_led, 'STEP4 by 2.2  ____ df_module_sop_adjust_cabinet_led .... module sop adjust cabinet led')


            # Module SOP Adjustment LED 구성
            df_module_sop_adjust_led = target_df.copy()
            df_module_sop_adjust_led_data.append(df_module_sop_adjust_led)
            print_df(df_module_sop_adjust_led, 'STEP4 by 2.3  ____ df_module_sop_adjust_led .... module sop adjust led')


            # SOP W LED 구성
            df_sopw_led = target_df.copy()
            df_sopw_led[ITEM_COMPONENT_COLUMN] = '-'
            df_sopw_led[ITEM_METERIAL_COLUMN] = '-'
            df_sopw_led[TO_TRANS_MODE_COLUMN] = df_sopw_led[TRANS_MODE_COLUMN].fillna('-')
            df_sopw_led[SUB_LOCATION_COLUMN] = df_sopw_led[SUB_LOCATION_COLUMN].fillna('-')
            df_sopw_led[WEEK2_COLUMN] = df_sopw_led[MODULE_SOP_ADJUST_LED_SOP_WEEK_COLUMN]
            df_sopw_led[WEEK1_COLUMN] = df_sopw_led[MODULE_SOP_ADJUST_LED_MFG_WEEK_COLUMN]
            df_sopw_led[SOP_W_LED_LCM_SOP_ADJ_QTY_COLUMN] = df_sopw_led[MODULE_SOP_ADJUST_LED_TOTAL_SOP_COLUMN]
            df_sopw_led[SOP_W_LED_LCM_SOP_QTY_COLUMN] = 0
            df_sopw_led[SOP_W_LED_LCM_MFG_QTY_COLUMN] = 0
            df_sopw_led[SOP_W_LED_SET_MFG_QTY_COLUMN] = 0
            df_sopw_led[SOP_W_LED_SET_SOP_QTY_COLUMN] = 0
            df_sopw_led_data.append(df_sopw_led)
            print_df(df_sopw_led, 'STEP4 by 2.4  ____ df_sopw_led .... sopw led')



            # 결과 합치기
            #   SOPW_LED
            df_sopw_led_result_2 = pd.concat(df_sopw_led_data, ignore_index=True) #if df_sopw_led_data else pd.DataFrame()
            print_df(df_sopw_led_result_2, 'STEP4 by 2.5.1  ____ df_sopw_led_result_2 ..... create')

            #   Module SOP Adjustment Cabinet LED
            df_module_sop_adjust_cabinet_led_result_2 = pd.concat(df_module_sop_adjust_cabinet_led_data, ignore_index=True)
            print_df(df_module_sop_adjust_cabinet_led_result_2, 'STEP4 by 2.5.2  ____ df_module_sop_adjust_cabinet_led_result_2 ..... create')

            #   Module SOP Adjustment LED
            df_module_sop_adjust_led_result_2 = pd.concat(df_module_sop_adjust_led_data, ignore_index=True)
            print_df(df_module_sop_adjust_led_result_2, 'STEP4 by 2.5.3  ____ df_module_sop_adjust_led_result_2 ..... create')

        else:
            df_sopw_led_result_2 = pd.DataFrame(columns=fn_sopw_columns)
            df_module_sop_adjust_cabinet_led_result_2 = pd.DataFrame(columns=fn_module_cabinet_columns)
            df_module_sop_adjust_led_result_2 = pd.DataFrame(columns=fn_module_sop_adj_columns)

        step('=====> STEP4 by 2 End')





        step('=====> STEP4 by 3 Start : 감량, 증량, Add 합치기')

        df_out_sopw_led = pd.concat([df_sopw_led_result_1, df_sopw_led_result_2], ignore_index=True)
        print_df(df_out_sopw_led, 'STEP4 by 3.1  ____ df_out_sopw_led .... create')

        df_out_module_sop_adjust_cabinet_led = pd.concat([df_module_sop_adjust_cabinet_led_result_1, df_module_sop_adjust_cabinet_led_result_2], ignore_index=True)
        print_df(df_out_module_sop_adjust_cabinet_led, 'STEP4 by 3.2  ____ df_out_module_sop_adjust_cabinet_led .... create')

        df_out_module_sop_adjust_led = pd.concat([df_module_sop_adjust_led_result_1, df_module_sop_adjust_led_result_2], ignore_index=True)
        print_df(df_out_module_sop_adjust_led, 'STEP4 by 3.3  ____ df_out_module_sop_adjust_led .... create')

        step('=====> STEP4 by 3 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_sopw_led[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_sopw_led = df_out_sopw_led[fn_sopw_columns].drop_duplicates()
        df_out_sopw_led = ultra_fast_replace_to_none(df_out_sopw_led)

        df_out_module_sop_adjust_cabinet_led[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_module_sop_adjust_cabinet_led = df_out_module_sop_adjust_cabinet_led[fn_module_cabinet_columns].drop_duplicates()
        df_out_module_sop_adjust_cabinet_led = ultra_fast_replace_to_none(df_out_module_sop_adjust_cabinet_led)

        df_out_module_sop_adjust_led[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_module_sop_adjust_led = df_out_module_sop_adjust_led[fn_module_sop_adj_columns].drop_duplicates()
        df_out_module_sop_adjust_led = ultra_fast_replace_to_none(df_out_module_sop_adjust_led)

        dataframes = {
            'df_out_sopw_led': df_out_sopw_led,
            'df_out_module_sop_adjust_cabinet_led': df_out_module_sop_adjust_cabinet_led,
            'df_out_module_sop_adjust_led': df_out_module_sop_adjust_led,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_sopw_led = pd.DataFrame(columns=fn_sopw_columns)
        df_out_module_sop_adjust_cabinet_led = pd.DataFrame(columns=fn_module_cabinet_columns)
        df_out_module_sop_adjust_led = pd.DataFrame(columns=fn_module_sop_adj_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_sopw_led = pd.DataFrame(columns=fn_sopw_columns)
        df_out_module_sop_adjust_cabinet_led = pd.DataFrame(columns=fn_module_cabinet_columns)
        df_out_module_sop_adjust_led = pd.DataFrame(columns=fn_module_sop_adj_columns)
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
