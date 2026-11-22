"""
* 프로그램명
    - PY_UI_SOPAdjustSET

* 내용
    - SET, LCM제품 및 BOM Version 기준으로 SOP Adjsut 수량 할당

* 변경이력
    - 2026.04.16 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek      : Select (&CurrentWeek);
    - df_in_AllWeek       : Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
    - df_in_BODItemW      : Select ([Location].[Location] * [Item].[Item] * &AllPlanningWeeks * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] * [Item].[Item Stage].filter(#.Name in {"SET"}) ) on row, ({Measure.[BOD Item W_BOD LT], Measure.[BOD Item W_Shipment LT]}) on column where {[Version].[Version Name]};
    - df_in_SOPW          : Select ([Location].[Location] * [To Location].[To Location] * [To Item].[To Item] * [Time].[Week] * [To Time].[To Week] * [Sequence].[Sequence] * [Item].[Item] * [Sub Location].[Sub Location] * [Item Material].[Item Material] * [Week2].[Week2] * [Item Component].[Item Component] * [To Trans Mode].[To Trans Mode] * [Week1].[Week1] * [Trans Mode].[Trans Mode] * [BOM Info].[BOM Version] ) on row, ({Measure.[Dummy], Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty]}) on column where {[Version].[Version Name]};
    - df_in_SOPAdjSETWReg : Select ([Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Time].[Week] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP Adjust SET W_Chg Qty], Measure.[SOP Adjust SET W_SOP Adj Qty], Measure.[SOP Adjust SET W_SOP Qty], Measure.[SOP Adjust SET W_Apply Flag]}) on column where {[Version].[Version Name], (Measure.[SOP Adjust SET W_Apply Flag]=="N" || Measure.[SOP Adjust SET W_Apply Flag]=="A")};


* Flow Summary
    - 1. LCM SOP Adjustr 수량을 SOP W MG에 데이터 할당


* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_SETW
    - df_out_SOPW

* 데이타 초기화
    -

* RUN 스크립트
    - exec procedure PR_UI_SOPAdjestSET {"Version":"CWV_MP"};

    - EXEC plugin instance [PY_UI_SOPAdjustSET] for measures {[SOP W_SET MFG Qty]} using scope (Version.[Version Name].filter(#.Name in {"CWV_MP"}))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPW / MG:  SOP W
        Select (&MPV * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [Location].[Location] * [To Time].[To Week] * [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Item Component].[Item Component] * [Week2].[Week2] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row,
        ({Measure.[SOP W_BOM Cfm W], Measure.[SOP W_BOM Status], Measure.[SOP W_Chg Reason], Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID], Measure.[SOP W_Sht Qty], Measure.[SOP W_Sht Reason]}) on column;

    - df_out_SETW / MG:  SOP Adjustment SET W
        Select (&MPV * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Time].[Week] * [Trans Mode].[Trans Mode]) on row,
        ({Measure.[SOP Adjust SET W_Chg Qty], Measure.[SOP Adjust SET W_SOP Adj Qty], Measure.[SOP Adjust SET W_SOP Qty]}) on column;
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
str_instance = 'PY_UI_SOPAdjustSET'
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
    if elapsed < 60:  # 1분 미만
        return f"{round(elapsed)} seconds"
    elif elapsed < 3600:  # 1시간 미만
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes} minute {seconds} second"
    else:  # 1시간 이상
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours} hour {minutes} minute {seconds} second"



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
    weeks = (
        weeks_df.loc[:, [TIME_WEEK_COLUMN]]
                .drop_duplicates()[TIME_WEEK_COLUMN]
                .to_numpy()
    )

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
            df_in_BODItemW = read_csv_file("df_in_BODItemW")
            df_in_SOPW = read_csv_file("df_in_SOPW")
            df_in_SOPAdjSETWReg = read_csv_file("df_in_SOPAdjSETWReg")


        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_BODItemW': df_in_BODItemW,
            'df_in_SOPW': df_in_SOPW,
            'df_in_SOPAdjSETWReg': df_in_SOPAdjSETWReg,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        LOCATION_COLUMN = 'Location.[Location]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        BOM_VERSION_PRTY_W_PRTY_COLUMN = 'BOM Version Prty W_Prty'

        BOD_ITEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
        BOD_ITEM_PRIORITY_COLUMN = 'BOD Item_Priority'
        BOD_ITEM_SHIPMENT_LT_COLUMN = 'BOD Item_Shipment LT'
        BOD_ITEM_W_BOD_LT_COLUMN = 'BOD Item W_BOD LT'
        BOD_ITEM_W_SHIPMENT_LT_COLUMN = 'BOD Item W_Shipment LT'

        SOP_W_LCM_MFG_ADJ_QTY_COLUMN = 'SOP W_LCM MFG Adj Qty'
        SOP_W_LCM_CHG_QTY_COLUMN = 'SOP W_LCM Chg Qty'
        SOP_W_LCM_SOP_QTY_COLUMN = 'SOP W_LCM SOP Qty'
        SOP_W_LCM_APPLY_FLAG_COLUMN = 'SOP W_LCM Apply Flag'
        SOP_W_LCM_SOP_CHG_QTY_COLUMN = 'SOP W_LCM SOP Chg Qty'
        SOP_W_LCM_MFG_QTY_COLUMN = 'SOP W_LCM MFG Qty'
        SOP_W_LCM_SOP_ADJ_QTY_COLUMN = 'SOP W_LCM SOP Adj Qty'

        SOP_W_SET_MFG_ADJ_QTY_COLUMN = 'SOP W_SET MFG Adj Qty'
        SOP_W_SET_CHG_QTY_COLUMN = 'SOP W_SET Chg Qty'
        SOP_W_SET_SOP_QTY_COLUMN = 'SOP W_SET SOP Qty'
        SOP_W_SET_APPLY_FLAG_COLUMN = 'SOP W_SET Apply Flag'
        SOP_W_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'
        SOP_W_SET_SOP_CHG_QTY_COLUMN = 'SOP W_SET SOP Chg Qty'
        SOP_W_SET_SOP_ADJ_QTY_COLUMN = 'SOP W_SET SOP Adj Qty'
        SOP_W_SET_DATA_ADD_FLAG_COLUMN = 'SOP W_SET Data Add Flag'

        SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN = 'SOP Adjust SET W_SOP Adj Qty'
        SOP_ADJUST_SET_W_SOP_QTY_COLUMN = 'SOP Adjust SET W_SOP Qty'
        SOP_ADJUST_SET_W_CHG_QTY_COLUMN = 'SOP Adjust SET W_Chg Qty'
        SOP_ADJUST_SET_W_CHG_REASON_COLUMN = 'SOP Adjust SET W_Chg Reason'
        SOP_ADJUST_SET_W_UPDATE_TIME_COLUMN = 'SOP Adjust SET W_Update Time'
        SOP_ADJUST_SET_W_UPDATED_BY_COLUMN = 'SOP Adjust SET W_Updated By'
        SOP_ADJUST_SET_W_APPLY_FLAG_COLUMN = 'SOP Adjust SET W_Apply Flag'

        version_columns = [VERSION_NAME_COLUMN]
        sequence_columns = [SEQUENCE_COLUMN]

        df_sopw_key_columns = [
            ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            WEEK1_COLUMN, WEEK2_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN,
        ]

        df_sopw_columns = [
            SOP_W_SET_SOP_ADJ_QTY_COLUMN, SOP_W_SET_SOP_CHG_QTY_COLUMN, SOP_W_SET_DATA_ADD_FLAG_COLUMN,
        ]

        df_setw_key_columns = [
            LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN,
        ]

        df_setw_columns = [
            SOP_ADJUST_SET_W_UPDATE_TIME_COLUMN, SOP_ADJUST_SET_W_UPDATED_BY_COLUMN, SOP_ADJUST_SET_W_APPLY_FLAG_COLUMN
        ]

        fn_sopw_columns = version_columns + df_sopw_key_columns + sequence_columns + df_sopw_columns
        fn_bk_sopw_columns = df_sopw_key_columns + df_sopw_columns
        fn_setw_columns = version_columns + df_setw_key_columns + df_setw_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        if df_in_SOPAdjSETWReg.empty:
            raise CustomException(".... df_in_SOPAdjSETWReg 값이 없습니다.")


         # 현재 week 가져오기
        mp_plan_start_week = str(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')


        # 'Sequence.[Sequence]' 컬럼의 최대값 구하기
        max_sequence_value = int(df_in_SOPW[SEQUENCE_COLUMN].max())
        step(f'=====> max_sequence_value : {max_sequence_value}')


        current_date = get_current_date_str('UTC')


        # df_in_AllWeek 필요컬럼 설정
        df_in_AllWeek[TIME_WEEK_COLUMN] = df_in_AllWeek[TIME_WEEK_COLUMN].astype(int)
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        print_df(df_in_AllWeek, 'STEP3 by 1.1  ____ df_in_AllWeek .... week uniqe')



        # # BOD LT 를 가져온다.
        def merge_and_convert_leadtime(df_sop, df_bod_itemw):
            """SOPAdj 데이터프레임과 BODItem을 merge하고 리드타임을 주 단위로 변환"""
            df_merged = df_sop.merge(
                df_bod_itemw,
                how='left',
                left_on=[LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN],
                right_on=[LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN],
            )

            # 리드타임 컬럼을 주 단위로 일괄 변환 (일 -> 주)
            leadtime_columns = [BOD_ITEM_W_SHIPMENT_LT_COLUMN, BOD_ITEM_W_BOD_LT_COLUMN]
            df_merged[leadtime_columns] = df_merged[leadtime_columns].apply(
                pd.to_numeric, errors='coerce', downcast='integer'
            ).fillna(0) / 7

            for col in leadtime_columns:
                df_merged[col] = df_merged[col].astype('Int64')

            # 컬럼정리
            # columns_to_rename = [
            #     LOCATION_COLUMN,
            #     SUB_LOCATION_COLUMN,
            # ]
            # cleanup_merged_columns(df_merged, columns_to_rename)

            return df_merged

        df_in_SOPAdjSETWReg = merge_and_convert_leadtime(df_in_SOPAdjSETWReg, df_in_BODItemW)
        df_in_SOPAdjSETWReg.drop(columns=[SUB_LOCATION_COLUMN], inplace=True)
        print_df(df_in_SOPAdjSETWReg, 'STEP3 by 1.2  ____ df_in_SOPAdjSETWReg .... merge')



        # 컬럼 설정, qty 컬럼 숫자 타입으로
        int_columns = [
            SOP_ADJUST_SET_W_CHG_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_QTY_COLUMN,
        ]
        df_in_SOPAdjSETWReg[int_columns] = df_in_SOPAdjSETWReg[int_columns].fillna(0).astype('Int64')


        df_sop_adj_reg = df_in_SOPAdjSETWReg[df_in_SOPAdjSETWReg[SOP_ADJUST_SET_W_APPLY_FLAG_COLUMN] == 'N'].copy()
        print_df(df_sop_adj_reg, 'STEP3 by 1.3  ____ df_sop_adj_reg .... apply flag')

        df_sop_adj_add = df_in_SOPAdjSETWReg[df_in_SOPAdjSETWReg[SOP_ADJUST_SET_W_APPLY_FLAG_COLUMN] == 'A'].copy()
        print_df(df_sop_adj_add, 'STEP3 by 1.4  ____ df_sop_adj_add .... apply flag')

        step('=====> STEP3 End')




        # ##############################################################################################################
        # # STEP 4 : output data machining
        # ##############################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : SET W 처리')

        # 1 SET W
        df_setw = rename_and_delete_df(df_in_SOPAdjSETWReg)
        df_setw[SOP_ADJUST_SET_W_UPDATE_TIME_COLUMN] = get_current_date_str('KST')
        df_setw[SOP_ADJUST_SET_W_UPDATED_BY_COLUMN] = "SET Adjust Data Sync"
        df_setw[SOP_ADJUST_SET_W_APPLY_FLAG_COLUMN] = 'Y'
        print_df(df_setw, 'STEP4 by 1.1 ____ df_setw .... final')

        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : SOP W 처리')
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

            target_df[week_col] = target_df[week_col].astype('Int64')
            base_idx = target_df[week_col].map(week_to_idx)
            target_idx = base_idx + target_df[lt_col]
            max_idx = len(df_AllWeek) - 1
            valid_mask = target_idx.between(0, max_idx)

            target_df[make_week_col] = None
            target_df.loc[valid_mask, make_week_col] = (target_idx[valid_mask].map(idx_to_week))
            target_df[make_week_col] = target_df[make_week_col].astype('Int64')

            return target_df

        def make_sopw_mask(df_sopw, adj_row):
            return (
                (df_sopw[ITEM_COLUMN] == adj_row[ITEM_COLUMN]) &
                (df_sopw[LOCATION_COLUMN] == adj_row[LOCATION_COLUMN]) &
                (df_sopw[TO_LOCATION_TO_LOCATION_COLUMN] == adj_row[TO_LOCATION_TO_LOCATION_COLUMN]) &
                (df_sopw[TRANS_MODE_COLUMN] == adj_row[TRANS_MODE_COLUMN]) &
                (df_sopw[TIME_WEEK_COLUMN] == adj_row[TIME_WEEK_COLUMN])
            )


        #   2.1 SOPW 증량,감량 처리
        if not df_sop_adj_reg.empty:
            # result_dfs = []
            #
            # for _, adj_row in df_sop_adj_reg.iterrows():
            #     mask = make_sopw_mask(df_in_SOPW, adj_row)
            #     target_df = df_in_SOPW.loc[mask].copy()
            #     target_df[SOP_W_SET_APPLY_FLAG_COLUMN] = adj_row[SOP_ADJUST_SET_W_APPLY_FLAG_COLUMN]
            #     target_df[SOP_W_SET_CHG_QTY_COLUMN] = adj_row[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            #     target_df[SOP_W_SET_SOP_ADJ_QTY_COLUMN] = adj_row[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            #     target_df[SOP_W_SET_SOP_QTY_COLUMN] = adj_row[SOP_ADJUST_SET_W_SOP_QTY_COLUMN]
            #     target_df[SOP_W_SET_DATA_ADD_FLAG_COLUMN] = 'Y'
            #     # print_df(target_df, 'STEP4 by 2.1.0 ____ target_df .... modify')
            #     result_dfs.append(target_df)
            #
            # df_sopw_reg = pd.concat(result_dfs, ignore_index=True)
            # print_df(df_sopw_reg, 'STEP4 by 2.1.0 ____ df_sopw_reg .... merge')

            remain_data = []

            for _, adj_row in df_sop_adj_reg.iterrows():
                adj_row[WEEK1_COLUMN] = mp_plan_start_week
                adj_row[WEEK2_COLUMN] = mp_plan_start_week
                remain_data.append({
                    **adj_row.to_dict(),
                })

            df_sopw_reg = pd.DataFrame(remain_data).drop_duplicates()
            columns = [TIME_WEEK_COLUMN]
            for col in columns:
                df_sopw_reg[col] = df_sopw_reg[col].astype('Int64')
            print_df(df_sopw_reg, 'STEP4 by 2.1.1 ____ df_sopw_reg .... modify')

            if not df_sopw_reg.empty:
                # Time Week 기준으로 BOD ShipLT 더한만큼 To Time_To Week 설정
                df_sopw_reg = apply_sop_week_mapping(
                    df_AllWeek=df_in_AllWeek,
                    target_df=df_sopw_reg,
                    time_week_col=TIME_WEEK_COLUMN,
                    week_col=TIME_WEEK_COLUMN,
                    lt_col=BOD_ITEM_W_SHIPMENT_LT_COLUMN,
                    make_week_col=TO_TIME_TO_WEEK_COLUMN,
                )
                print_df(df_sopw_reg, 'STEP4 by 2.1.2 ____ df_sopw_reg .... week mapping')

                # Dummy 생성
                dummy_columns = [
                    SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, TO_ITEM_TO_ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN,
                    BOM_INFO_BOM_VERSION_COLUMN,
                ]
                # df_sopw_reg[dummy_columns] = 'Dummy'
                for col in dummy_columns:
                    if col in df_sopw_reg.columns:
                        df_sopw_reg[col] = df_sopw_reg[col].fillna('Dummy')
                    else:
                        df_sopw_reg[col] = 'Dummy'

                df_sopw_reg = df_sopw_reg.drop_duplicates()
                print_df(df_sopw_reg, 'STEP4 by 2.1.3 ____ df_sopw_reg .... recreate')

                # 수량설정
                df_sopw_reg[SOP_W_SET_SOP_CHG_QTY_COLUMN] = df_sopw_reg[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                df_sopw_reg[SOP_W_SET_SOP_ADJ_QTY_COLUMN] = df_sopw_reg[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                df_sopw_reg[SOP_W_SET_DATA_ADD_FLAG_COLUMN] = 'Y'
                print_df(df_sopw_reg, 'STEP4 by 2.1.4 ____ df_sopw_reg .... final')

            else:
                df_sopw_reg = pd.DataFrame(columns=fn_sopw_columns)

        else:
            df_sopw_reg = pd.DataFrame(columns=fn_bk_sopw_columns)





        # 2.2 SOPW Add 처리
        if not df_sop_adj_add.empty:
            columns = [TIME_WEEK_COLUMN]
            for col in columns:
                df_sop_adj_add[col] = df_sop_adj_add[col].astype('Int64')
            print_df(df_sop_adj_add, 'STEP4 by 2.2.1 ____ df_sop_adj_add .... modify')

            # Week1 기준으로 BOD ShipLT 더한만큼 Week2 설정 및 기타 Week 설정
            df_sop_adj_add = apply_sop_week_mapping(
                df_AllWeek=df_in_AllWeek,
                target_df=df_sop_adj_add,
                time_week_col=TIME_WEEK_COLUMN,
                week_col=TIME_WEEK_COLUMN,
                lt_col=BOD_ITEM_W_SHIPMENT_LT_COLUMN,
                make_week_col=TO_TIME_TO_WEEK_COLUMN,
            )

            week_curr_columns = [WEEK1_COLUMN, WEEK2_COLUMN,]
            for col in week_curr_columns:
                df_sop_adj_add[col] = mp_plan_start_week
                df_sop_adj_add[col] = df_sop_adj_add[col].fillna(mp_plan_start_week)
            print_df(df_sop_adj_add, 'STEP4 by 2.2.2 ____ df_sop_adj_add .... apply_sop_week_mapping')

            # 컬럼정리(Dummy 생성)
            dummy_columns = [
                SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, TO_ITEM_TO_ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN,
                BOM_INFO_BOM_VERSION_COLUMN,
            ]
            for col in dummy_columns:
                if col in df_sop_adj_add.columns:
                    df_sop_adj_add[col] = df_sop_adj_add[col].fillna('Dummy')
                else:
                    df_sop_adj_add[col] = 'Dummy'

            df_sop_adj_add = df_sop_adj_add.drop_duplicates()
            print_df(df_sop_adj_add, 'STEP4 by 2.2.3 ____ df_sop_adj_add .... recreate')

            # 수량설정
            df_sop_adj_add[SOP_W_SET_SOP_CHG_QTY_COLUMN] = df_sop_adj_add[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            df_sop_adj_add[SOP_W_SET_SOP_ADJ_QTY_COLUMN] = df_sop_adj_add[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            df_sop_adj_add[SOP_W_SET_DATA_ADD_FLAG_COLUMN] = 'Y'
            print_df(df_sop_adj_add, 'STEP4 by 2.2.4 ____ df_sop_adj_add .... final')

        else:
            df_sop_adj_add = pd.DataFrame(columns=fn_bk_sopw_columns)




        # 3 SOPW concat
        df_sopw = pd.concat([df_sopw_reg, df_sop_adj_add], ignore_index=True).drop_duplicates()

        df_sopw[SEQUENCE_COLUMN] = range(max_sequence_value + 1, max_sequence_value + 1 + len(df_sopw))
        print_df(df_sopw, 'STEP4 by 3 ____ df_sopw .... concat', True)

        step('=====> STEP4 End')


    
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_SETW = rename_and_delete_df(df_setw)
        df_out_SOPW = rename_and_delete_df(df_sopw)

        df_out_SETW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SETW = df_out_SETW[fn_setw_columns].drop_duplicates()
        df_out_SETW = ultra_fast_replace_to_none(df_out_SETW)

        df_out_SOPW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPW = df_out_SOPW[fn_sopw_columns].drop_duplicates()
        df_out_SOPW = ultra_fast_replace_to_none(df_out_SOPW)

        dataframes = {
            'df_out_SETW': df_out_SETW,
            'df_out_SOPW': df_out_SOPW,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)
    
        step('=====> STEP5 End')
        
    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SETW = pd.DataFrame(columns=fn_setw_columns)
        df_out_SOPW = pd.DataFrame(columns=fn_sopw_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SETW = pd.DataFrame(columns=fn_setw_columns)
        df_out_SOPW = pd.DataFrame(columns=fn_sopw_columns)
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
