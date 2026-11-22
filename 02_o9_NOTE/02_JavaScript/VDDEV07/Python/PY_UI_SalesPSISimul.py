"""
* 프로그램명
    - PY_UI_SalesPSISimul

* 내용
    - PSI 수령 SOP 반영

* 변경이력
    - 2026.01.27 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_MDMHorizon   : Select (&MDMHorizon);
    - df_in_SalesPSIAP2W : Select ([Location].[Location] * [Sales Domain].[AP2] * &MDMHorizon * [Item].[Item] * [Sub Location].[Sub Location].[-] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Sales PSI AP2 W_Arrival], Measure.[Sales PSI AP2 W_BOH], Measure.[Sales PSI AP2 W_Dmd], Measure.[Sales PSI AP2 W_EOH], Measure.[Sales PSI AP2 W_RTF], Measure.[Sales PSI AP2 W_Shipment], Measure.[Sales PSI AP2 W_Short]}) on column where {[Version].[Version Name]};
    - df_in_BODItem      : Select ([Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_BOD LT], Measure.[BOD Item_Shipment LT]}) on column where {[Version].[Version Name]};
    - df_in_SOPW         : Select ([Location].[Location] * [To Location].[To Location] * [To Item].[To Item] * [Time].[Week] * [To Time].[To Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key && #.Key < &CurrentWeek.element(0).LeadOffset(35).Key)  * [Item].[Item] * [Sequence].[Sequence] * [Sub Location].[Sub Location] * [Item Material].[Item Material] * [Week2].[Week2] * [Item Component].[Item Component] * [To Trans Mode].[To Trans Mode] * [Week1].[Week1] * [Trans Mode].[Trans Mode] * [BOM Info].[BOM Version] ) on row, ({Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM Plant BOH Qty], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP ID], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET SOP Adj Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty]}) on column where {[Version].[Version Name]};

* Flow Summary
    - STEP1.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_SalesPSISimul
    - df_out_SalesPSIUpdateTime

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SalesPSISimul] for measures {[Sales PSI AP2 W_Simul Shipment]} using scope (Version.[Version Name].filter(#.Name in {"CWV_MP"}))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Location].[Location] * [Sales Domain].[AP2] * &MDMHorizon * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[Sales PSI AP2 W_Arrival], Measure.[Sales PSI AP2 W_BOH], Measure.[Sales PSI AP2 W_Dmd], Measure.[Sales PSI AP2 W_EOH], Measure.[Sales PSI AP2 W_RTF], Measure.[Sales PSI AP2 W_Shipment], Measure.[Sales PSI AP2 W_Short], Measure.[Sales PSI AP2 W_Simul Arrival], Measure.[Sales PSI AP2 W_Simul BOH], Measure.[Sales PSI AP2 W_Simul EOH], Measure.[Sales PSI AP2 W_Simul RTF], Measure.[Sales PSI AP2 W_Simul Shipment], Measure.[Sales PSI AP2 W_Simul Short]}) on column where {[Version].[Version Name].[CWV_MP]} ;

"""
# from __future__ import annotations
import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
from numba import njit
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SalesPSISimul'
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
    tz 인자로 'UTC' (대소문자 무관)를 주면 UTC 기준, 그 외에는 로컬 타임존 기준.
    """
    if isinstance(tz, str) and tz.upper() == "UTC":
        now = datetime.datetime.now(datetime.timezone.utc)
    else:
        # now = datetime.datetime.now().astimezone()
        now = datetime.datetime.now()

    return now.strftime("%Y-%m-%d %H:%M:%S")


def ultra_fast_replace_to_none(df):
    """NumPy 기반 초고속 변환"""
    df = df.copy()

    # object 컬럼과 숫자 컬럼 분리
    obj_cols = df.select_dtypes(include=['object']).columns
    num_cols = df.select_dtypes(include=['number']).columns

    # 문자열 컬럼 일괄 처리
    if len(obj_cols) > 0:
        obj_data = df[obj_cols].values
        # 조건 마스크 생성
        mask = (
            (obj_data == 'nan') |
            (obj_data == '<NA>') |
            (obj_data == '0') |
            pd.isna(obj_data)
        )
        df.loc[:, obj_cols] = df.loc[:, obj_cols].mask(mask, None)

    # 숫자 컬럼: NaN → None (object 변환 필요)
    for col in num_cols:
        if df[col].isna().any():
            df[col] = df[col].astype(object).where(df[col].notna(), None)

    # 숫자 컬럼: NaN → None (object 변환 필요) -> 숫자컬럼많고 행이 수십만일경우 적용
    # if len(num_cols) > 0:
    #     num_data = df[num_cols].to_numpy(dtype=object, copy=True)
    #     mask = pd.isna(num_data)
    #     num_data[mask] = None
    #     df[num_cols] = num_data

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
            df_in_MDMHorizon = read_csv_file("df_in_MDMHorizon")
            df_in_SalesPSIAP2W = read_csv_file("df_in_SalesPSIAP2W")
            df_in_BODItem = read_csv_file("df_in_BODItem")
            df_in_SOPW = read_csv_file("df_in_SOPW")

        dataframes = {
            'df_in_MDMHorizon': df_in_MDMHorizon,
            'df_in_SalesPSIAP2W': df_in_SalesPSIAP2W,
            'df_in_BODItem': df_in_BODItem,
            'df_in_SOPW': df_in_SOPW,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        ITEM_COLUMN = 'Item.[Item]'

        SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'

        TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_ITEM_COLUMN = 'To Item.[To Item]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        ITEM_MATERIAL_COLUMN = 'Item Material.[Item Material]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        BOM_INFO_COLUMN = 'BOM Info.[BOM Version]'

        BOD_ITEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
        BOD_ITEM_SHIPMENT_LT_COLUMN = 'BOD Item_Shipment LT'

        SALES_PSI_AP2_W_AGING_OVER_30DAYS_COLUMN = 'Sales PSI AP2 W_Aging Over 30days'
        SALES_PSI_AP2_W_AGING_OVER_60DAYS_COLUMN = 'Sales PSI AP2 W_Aging Over 60days'
        SALES_PSI_AP2_W_AGING_RATE_OVER_30DAYS_COLUMN = 'Sales PSI AP2 W_Aging Rate Over 30days'
        SALES_PSI_AP2_W_AGING_RATE_OVER_60DAYS_COLUMN = 'Sales PSI AP2 W_Aging Rate Over 60days'
        SALES_PSI_AP2_W_ARRIVAL_COLUMN = 'Sales PSI AP2 W_Arrival'
        SALES_PSI_AP2_W_ARRIVAL_DETAIL_COLUMN = 'Sales PSI AP2 W_Arrival Detail'
        SALES_PSI_AP2_W_BOH_COLUMN = 'Sales PSI AP2 W_BOH'
        SALES_PSI_AP2_W_BUILD_AHEAD_COLUMN = 'Sales PSI AP2 W_Build Ahead'
        SALES_PSI_AP2_W_CONSENSUS_RTF_COLUMN = 'Sales PSI AP2 W_Consensus RTF'
        SALES_PSI_AP2_W_DELAYED_RTF_COLUMN = 'Sales PSI AP2 W_Delayed RTF'
        SALES_PSI_AP2_W_DMD_COLUMN = 'Sales PSI AP2 W_Dmd'
        SALES_PSI_AP2_W_DMD_FILL_RATE_COLUMN = 'Sales PSI AP2 W_Dmd Fill Rate'
        SALES_PSI_AP2_W_DMD_GI_COLUMN = 'Sales PSI AP2 W_Dmd GI'
        SALES_PSI_AP2_W_EOH_COLUMN = 'Sales PSI AP2 W_EOH'
        SALES_PSI_AP2_W_EOH_ADJ_COLUMN = 'Sales PSI AP2 W_EOH Adj'
        SALES_PSI_AP2_W_EOH_AMT_KRW_COLUMN = 'Sales PSI AP2 W_EOH Amt KRW'
        SALES_PSI_AP2_W_EOH_AMT_USD_COLUMN = 'Sales PSI AP2 W_EOH Amt USD'
        SALES_PSI_AP2_W_EOH_PLANT_COLUMN = 'Sales PSI AP2 W_EOH Plant'
        SALES_PSI_AP2_W_EOH_W_COLUMN = 'Sales PSI AP2 W_EOH W'
        SALES_PSI_AP2_W_FCST_RDD_AP1_COLUMN = 'Sales PSI AP2 W_Fcst RDD AP1'
        SALES_PSI_AP2_W_FCST_RDD_AP2_COLUMN = 'Sales PSI AP2 W_Fcst RDD AP2'
        SALES_PSI_AP2_W_GI_AMT_KRW_COLUMN = 'Sales PSI AP2 W_GI Amt KRW'
        SALES_PSI_AP2_W_GI_AMT_USD_COLUMN = 'Sales PSI AP2 W_GI Amt USD'
        SALES_PSI_AP2_W_GI_QTY_COLUMN = 'Sales PSI AP2 W_GI Qty'
        SALES_PSI_AP2_W_GI_RTF_AVG_COLUMN = 'Sales PSI AP2 W_GI_RTF Avg'
        SALES_PSI_AP2_W_INTRANSIT_COLUMN = 'Sales PSI AP2 W_Intransit'
        SALES_PSI_AP2_W_INV_DEL_DIR_COLUMN = 'Sales PSI AP2 W_Inv Del DIR'
        SALES_PSI_AP2_W_INVENTORY_COLUMN = 'Sales PSI AP2 W_Inventory'
        SALES_PSI_AP2_W_PROD_DETAIL_COLUMN = 'Sales PSI AP2 W_Prod Detail'
        SALES_PSI_AP2_W_RTF_COLUMN = 'Sales PSI AP2 W_RTF'
        SALES_PSI_AP2_W_RTF_RDD_COLUMN = 'Sales PSI AP2 W_RTF RDD'
        SALES_PSI_AP2_W_SS_ARRIVAL_COLUMN = 'Sales PSI AP2 W_SS Arrival'
        SALES_PSI_AP2_W_SS_ARRIVAL_BUILD_AHEAD_COLUMN = 'Sales PSI AP2 W_SS Arrival Build Ahead'
        SALES_PSI_AP2_W_SS_ARRIVAL_JIT_COLUMN = 'Sales PSI AP2 W_SS Arrival JIT'
        SALES_PSI_AP2_W_SS_SHIPMENT_COLUMN = 'Sales PSI AP2 W_SS Shipment'
        SALES_PSI_AP2_W_SS_SHIPMENT_BUILD_AHEAD_COLUMN = 'Sales PSI AP2 W_SS Shipment Build Ahead'
        SALES_PSI_AP2_W_SS_SHIPMENT_JIT_COLUMN = 'Sales PSI AP2 W_SS Shipment JIT'
        SALES_PSI_AP2_W_SAFETY_STOCK_COLUMN = 'Sales PSI AP2 W_Safety Stock'
        SALES_PSI_AP2_W_SALES_COLUMN = 'Sales PSI AP2 W_Sales'
        SALES_PSI_AP2_W_SHIPMENT_COLUMN = 'Sales PSI AP2 W_Shipment'
        SALES_PSI_AP2_W_SHIPMENT_DETAIL_COLUMN = 'Sales PSI AP2 W_Shipment Detail'
        SALES_PSI_AP2_W_SHORT_COLUMN = 'Sales PSI AP2 W_Short'
        SALES_PSI_AP2_W_SIMUL_SHIPMENT_COLUMN = 'Sales PSI AP2 W_Simul Shipment'

        SOP_W_SET_SOP_ADJ_QTY_COLUMN = 'SOP W_SET SOP Adj Qty'
        SOP_W_LCM_BOH_QTY_COLUMN = 'SOP W_LCM BOH Qty'
        SOP_W_LCM_MFG_ADJ_QTY_COLUMN = 'SOP W_LCM MFG Adj Qty'
        SOP_W_LCM_MFG_CHG_QTY_COLUMN = 'SOP W_LCM MFG Chg Qty'
        SOP_W_LCM_MFG_QTY_COLUMN = 'SOP W_LCM MFG Qty'
        SOP_W_LCM_PLANT_BOH_QTY_COLUMN = 'SOP W_LCM Plant BOH Qty'
        SOP_W_LCM_SOP_ADJ_QTY_COLUMN = 'SOP W_LCM SOP Adj Qty'
        SOP_W_LCM_SOP_ID_COLUMN = 'SOP W_LCM SOP ID'
        SOP_W_LCM_SOP_QTY_COLUMN = 'SOP W_LCM SOP Qty'
        SOP_W_NEW_MODEL_MP_COLUMN = 'SOP W_New Model MP'
        SOP_W_NEW_MODEL_RTS_COLUMN = 'SOP W_New Model RTS'
        SOP_W_NEW_MODEL_SR_COLUMN = 'SOP W_New Model SR'
        SOP_W_PB_QTY_COLUMN = 'SOP W_PB Qty'
        SOP_W_PY_QTY_COLUMN = 'SOP W_PY Qty'
        SOP_W_SET_BOH_QTY_COLUMN = 'SOP W_SET BOH Qty'
        SOP_W_SET_MFG_ADJ_QTY_COLUMN = 'SOP W_SET MFG Adj Qty'
        SOP_W_SET_MFG_CHG_QTY_COLUMN = 'SOP W_SET MFG Chg Qty'
        SOP_W_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'
        SOP_W_SET_SOP_QTY_COLUMN = 'SOP W_SET SOP Qty'
        SOP_W_SOP_ID_COLUMN = 'SOP W_SOP ID'
        SOP_W_SS_COLUMN = 'SOP W_SS'
        SOP_W_SHT_QTY_COLUMN = 'SOP W_Sht Qty'
        SOP_W_SHT_REASON_COLUMN = 'SOP W_Sht Reason'

        SALES_PSI_AP2_W_SIMUL_RTF_COLUMN = 'Sales PSI AP2 W_Simul RTF'
        SALES_PSI_AP2_W_SIMUL_SHORT_COLUMN = 'Sales PSI AP2 W_Simul Short'
        SALES_PSI_AP2_W_SIMUL_BOH_COLUMN = 'Sales PSI AP2 W_Simul BOH'
        SALES_PSI_AP2_W_SIMUL_EOH_COLUMN = 'Sales PSI AP2 W_Simul EOH'
        SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN = 'Sales PSI AP2 W_Simul Arrival'
        SALES_PSI_AP2_W_SIMUL_SHIPMENT_COLUMN = 'Sales PSI AP2 W_Simul Shipment'

        VERSION_INFO_SALES_PSI_UPDATE_TIME_COLUMN = 'VersionInfo_Sales PSI Update Time'

        version_column = [VERSION_NAME_COLUMN]

        sales_psi_ap2w_key_column = [
            LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            SALES_PSI_AP2_W_DMD_COLUMN, SALES_PSI_AP2_W_RTF_COLUMN, SALES_PSI_AP2_W_SHORT_COLUMN,
            SALES_PSI_AP2_W_BOH_COLUMN, SALES_PSI_AP2_W_EOH_COLUMN,
            SALES_PSI_AP2_W_ARRIVAL_COLUMN, SALES_PSI_AP2_W_SHIPMENT_COLUMN,
        ]
        sales_psi_ap2w_key2_column = [
            LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
        ]

        # sopw_key_column = [
        #     LOCATION_COLUMN, TO_LOCATION_COLUMN, TO_ITEM_COLUMN, TIME_WEEK_COLUMN, TO_TIME_TO_WEEK_COLUMN, ITEM_COLUMN, SEQUENCE_COLUMN,
        #     SUB_LOCATION_COLUMN, ITEM_MATERIAL_COLUMN, WEEK1_COLUMN, WEEK2_COLUMN, ITEM_COMPONENT_COLUMN, TO_TRANS_MODE_COLUMN,
        #     TRANS_MODE_COLUMN, BOM_INFO_COLUMN,
        #     SOP_W_SET_SOP_QTY_COLUMN,
        # ]
        sopw_key_column = [
            LOCATION_COLUMN, TO_LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN, SOP_W_SET_SOP_ADJ_QTY_COLUMN,
        ]

        make_column = [
            SALES_PSI_AP2_W_SIMUL_RTF_COLUMN, SALES_PSI_AP2_W_SIMUL_SHORT_COLUMN, SALES_PSI_AP2_W_SIMUL_BOH_COLUMN,
            SALES_PSI_AP2_W_SIMUL_EOH_COLUMN, SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN, SALES_PSI_AP2_W_SIMUL_SHIPMENT_COLUMN,
        ]

        fn_sales_psi_simul_columns = version_column + sales_psi_ap2w_key2_column + make_column

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # # df_in_SalesPSIAP2W = df_in_SalesPSIAP2W[df_in_SalesPSIAP2W[ITEM_COLUMN].isin(['HW-B650F/EN', 'HW-B650F/EN', 'HW-B650F/EN', 'HW-B650F/EN'])]
        # # df_in_SalesPSIAP2W = df_in_SalesPSIAP2W[
        # #     df_in_SalesPSIAP2W[ITEM_COLUMN].isin(['TU27F6005FKXXC']) &
        # #     df_in_SalesPSIAP2W[LOCATION_COLUMN].isin(['S406'])
        # # ].copy()
        # print_df(df_in_SalesPSIAP2W, 'STEP3 by 0.0.0  ____ df_in_SalesPSIAP2W .... filter', True)
        #
        # # df_in_SalesPSIAP2W = df_in_SalesPSIAP2W[
        # #     (df_in_SalesPSIAP2W[ITEM_COLUMN] == 'LS24D300GAUXEN') &
        # #     (df_in_SalesPSIAP2W[LOCATION_COLUMN] == 'L401') &
        # #     (df_in_SalesPSIAP2W[SUB_LOCATION_COLUMN] == 'P551')
        # # ].copy()
        # # print_df(df_in_SalesPSIAP2W, 'STEP3 by 0.0.1  ____ df_in_SalesPSIAP2W .... filter', True)
        #
        # df_in_SOPW = df_in_SOPW[df_in_SOPW[ITEM_COLUMN].isin(['HW-B650F/EN'])]
        # print_df(df_in_SOPW, 'STEP3 by 0.0.2  ____ df_in_SOPW .... filter', True)
        # ------------------ 테스트 디버깅용 ------------------ end


        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_SalesPSIAP2W.empty :
            raise CustomException("STEP3 by 0.1 ____ df_in_SalesPSIAP2W 값이 없습니다.")


        # 1. df_in_MDMHorizon 정렬 및 필요컬럼만 발췌
        df_in_MDMHorizon = (
            df_in_MDMHorizon[[TIME_WEEK_COLUMN]]
            .drop_duplicates()
            .sort_values(TIME_WEEK_COLUMN)  # 오름차순
            .reset_index(drop=True)
            .copy()
        )
        df_in_MDMHorizon.loc[:, TIME_WEEK_COLUMN] = df_in_MDMHorizon[TIME_WEEK_COLUMN].astype("int64")
        print_df(df_in_MDMHorizon, 'STEP3 by 1.1  ____ df_in_MDMHorizon .... week uniqe')



        start_week = int(df_in_MDMHorizon[TIME_WEEK_COLUMN].values[0])
        next_week = int(df_in_MDMHorizon[TIME_WEEK_COLUMN].values[1])
        step(f'=====> start_week : {start_week}, next_week : {next_week}')



        # 2. df_in_SalesPSIAP2W 가공
        #   2.1 필요컬럼 발췌
        df_in_SalesPSIAP2W = df_in_SalesPSIAP2W[sales_psi_ap2w_key_column].copy()
        df_in_SalesPSIAP2W[TIME_WEEK_COLUMN] = df_in_SalesPSIAP2W[TIME_WEEK_COLUMN].fillna(0).astype('int64')

        #   2.2 df_in_SalesPSIAP2W 에 수량 컬럼 0으로 채우기 및 int64로 변환
        inc_columns = [
            SALES_PSI_AP2_W_DMD_COLUMN, SALES_PSI_AP2_W_RTF_COLUMN, SALES_PSI_AP2_W_SHORT_COLUMN,
            SALES_PSI_AP2_W_BOH_COLUMN, SALES_PSI_AP2_W_EOH_COLUMN,
            SALES_PSI_AP2_W_ARRIVAL_COLUMN, SALES_PSI_AP2_W_SHIPMENT_COLUMN,
        ]
        df_in_SalesPSIAP2W[inc_columns] = df_in_SalesPSIAP2W[inc_columns].fillna(0).astype('int64')
        print_df(df_in_SalesPSIAP2W, 'STEP3 by 2.2  ____ df_in_SalesPSIAP2W .... column select')

        #   2.3 df_in_SalesPSIAP2W 에 빈주차 생성
        key_columns = [LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        df_missing_rows = set_unique_combinations(df_in_SalesPSIAP2W, df_in_MDMHorizon, key_columns)
        print_df(df_missing_rows, 'STEP3 by 2.3  ____ df_missing_rows .... set_unique_combinations')

        df_in_SalesPSIAP2W = pd.concat([df_in_SalesPSIAP2W, df_missing_rows], ignore_index=True).drop_duplicates()

        col = SALES_DOMAIN_AP2_COLUMN
        mask = df_in_SalesPSIAP2W[col].isna()
        df_in_SalesPSIAP2W.loc[mask, col] = '-'
        print_df(df_in_SalesPSIAP2W, 'STEP3 by 2.4  ____ df_in_SalesPSIAP2W .... merge with df_in_MDMHorizon', True)



        # 3. df_in_SOPW 가공
        if not df_in_SOPW.empty :
            #   3.1 불필요 컬럼 삭제 및 수량 Sum
            df_in_SOPW = df_in_SOPW[sopw_key_column].copy()
            df_in_SOPW.rename(columns={
                TO_TIME_TO_WEEK_COLUMN: TIME_WEEK_COLUMN,
            }, inplace=True)
            s = df_in_SOPW[TIME_WEEK_COLUMN]
            df_in_SOPW[TIME_WEEK_COLUMN] = (
                s.replace([np.inf, -np.inf], np.nan).fillna(0).astype("int64")  # inf가 있을 수도 있으니 방어
            )
            groupby_columns = [LOCATION_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, TRANS_MODE_COLUMN]
            sum_columns = [SOP_W_SET_SOP_ADJ_QTY_COLUMN]
            agg_dict = {col: 'sum' for col in sum_columns}
            df_in_SOPW = df_in_SOPW.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
            print_df(df_in_SOPW, 'STEP3 by 3.1  ____ df_in_SOPW .... groupby')

            #   3.1.1 'To Location.[To Location]' 에 @  가 있는경우 Location 과 AP2 로 분리
            #           @ 가 없으면 AP2 를 '-' 로 생성
            arr = df_in_SOPW[TO_LOCATION_COLUMN].to_numpy(dtype=str)
            left, sep, right = np.char.partition(arr, '@').T
            df_in_SOPW[TO_LOCATION_COLUMN] = left
            df_in_SOPW[SALES_DOMAIN_AP2_COLUMN] = np.where(sep == '@', right, '')
            print_df(df_in_SOPW, 'STEP3 by 3.1.1  ____ df_in_SOPW .... TO_LOCATION_COLUMN split @')


            #   3.2 SOPW 에 LT 추가
            df_in_SOPW = df_in_SOPW.merge(
                df_in_BODItem, how='left',
                left_on=[LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, TRANS_MODE_COLUMN],
                right_on=[LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
            )
            print_df(df_in_SOPW, 'STEP3 by 3.2.1  ____ df_in_SOPW .... merge with df_in_BODItem')

            groupby_columns = [TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN, SALES_DOMAIN_AP2_COLUMN]
            sum_columns = [SOP_W_SET_SOP_ADJ_QTY_COLUMN]
            max_columns = [BOD_ITEM_BOD_LT_COLUMN, BOD_ITEM_SHIPMENT_LT_COLUMN]
            agg_dict = {col: 'sum' for col in sum_columns}
            agg_dict.update({col: 'max' for col in max_columns})
            df_in_SOPW = df_in_SOPW.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
            print_df(df_in_SOPW, 'STEP3 by 3.2.2  ____ df_in_SOPW .... groupby')

            values = df_in_SOPW[BOD_ITEM_BOD_LT_COLUMN].to_numpy()
            values = np.nan_to_num(values, nan=0).astype('int64')
            df_in_SOPW[BOD_ITEM_BOD_LT_COLUMN] = (values + 6) // 7
            print_df(df_in_SOPW, 'STEP3 by 3.2.3  ____ df_in_SOPW .... LT trans')


            #   3.3 SOPW 를 AP2 가 있는것과 없는것으로 분리
            col = df_in_SOPW[SALES_DOMAIN_AP2_COLUMN]
            mask_has_value = col.notna() & col.ne('')
            df_in_SOPW_1 = df_in_SOPW.loc[mask_has_value]
            df_in_SOPW_2 = df_in_SOPW.loc[~mask_has_value].copy()
            df_in_SOPW_2.drop(columns=[SALES_DOMAIN_AP2_COLUMN], inplace=True)


            #   3.3 df_in_SalesPSIAP2W 에 sop 추가
            #       3.3.1 AP2 존재 모델 merge
            df_in_SalesPSIAP2W = df_in_SalesPSIAP2W.merge(
                df_in_SOPW_1, how='left',
                left_on=[SALES_DOMAIN_AP2_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN],
                right_on=[SALES_DOMAIN_AP2_COLUMN, TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN],
            )
            print_df(df_in_SalesPSIAP2W, 'STEP3 by 3.3.1.1  ____ df_in_SalesPSIAP2W .... merge with df_in_SOPW_1')

            df_in_SalesPSIAP2W.drop(columns=[TO_LOCATION_COLUMN], inplace=True)
            print_df(df_in_SalesPSIAP2W, 'STEP3 by 3.3.1.2  ____ df_in_SalesPSIAP2W .... drop TO_LOCATION_COLUMN')

            #       3.3.2 AP2 미존재 모델 merge
            df_in_SalesPSIAP2W = df_in_SalesPSIAP2W.merge(
                df_in_SOPW_2, how='left',
                left_on=[LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN],
                right_on=[TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN],
            )
            print_df(df_in_SalesPSIAP2W, 'STEP3 by 3.3.2.1  ____ df_in_SalesPSIAP2W .... merge with df_in_SOPW_2')

            df_in_SalesPSIAP2W.drop(columns=[TO_LOCATION_COLUMN], inplace=True)
            print_df(df_in_SalesPSIAP2W, 'STEP3 by 3.3.2.2  ____ df_in_SalesPSIAP2W .... drop TO_LOCATION_COLUMN')

            target_columns = [
                SOP_W_SET_SOP_ADJ_QTY_COLUMN,
                BOD_ITEM_BOD_LT_COLUMN,
                BOD_ITEM_SHIPMENT_LT_COLUMN,
            ]

            for col in target_columns:
                x_col = f"{col}_x"
                y_col = f"{col}_y"

                df_in_SalesPSIAP2W[x_col] = (
                    df_in_SalesPSIAP2W[x_col]
                    .replace("", pd.NA)
                    .fillna(df_in_SalesPSIAP2W[y_col])
                )

            df_in_SalesPSIAP2W = df_in_SalesPSIAP2W.drop(columns=[f"{col}_y" for col in target_columns])

            df_in_SalesPSIAP2W = df_in_SalesPSIAP2W.rename(
                columns={f"{col}_x": col for col in target_columns}
            )
            print_df(df_in_SalesPSIAP2W, 'STEP3 by 3.3.2.3  ____ df_in_SalesPSIAP2W .... rename')
        else:
            target_columns = [
                SOP_W_SET_SOP_ADJ_QTY_COLUMN,
                BOD_ITEM_BOD_LT_COLUMN,
                BOD_ITEM_SHIPMENT_LT_COLUMN,
            ]
            for col in target_columns:
                df_in_SalesPSIAP2W[col] = None

            print_df(df_in_SalesPSIAP2W, 'STEP3 by 3.1  ____ df_in_SalesPSIAP2W .... column create')


        #   3.4 df_in_SalesPSIAP2W 에 컬럼 rename 및 불필요컬럼 삭제, 수량 컬럼 0으로 채우기 및 int64로 변환
        s = df_in_SalesPSIAP2W[SOP_W_SET_SOP_ADJ_QTY_COLUMN]
        df_in_SalesPSIAP2W[SOP_W_SET_SOP_ADJ_QTY_COLUMN] = (
            s.replace([np.inf, -np.inf], np.nan).fillna(0).astype("int64")  # inf가 있을 수도 있으니 방어
        )
        print_df(df_in_SalesPSIAP2W, 'STEP3 by 3.4  ____ df_in_SalesPSIAP2W .... rename')


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : 이전 주차의 EOH 및 SOP 값 설정')

        # df_in_SalesPSIAP2W 키컬럼으로 sort
        group_col = [LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        df_in_SalesPSIAP2W = df_in_SalesPSIAP2W.sort_values(group_col + [TIME_WEEK_COLUMN])
        print_df(df_in_SalesPSIAP2W, f'STEP4 by 1.1  ____ df_in_SalesPSIAP2W .... sort by')

        # start_week 주 값을 simul 관련 컬럼 업데이트
        src_cols = [
            SALES_PSI_AP2_W_RTF_COLUMN, SALES_PSI_AP2_W_SHORT_COLUMN,
            SALES_PSI_AP2_W_BOH_COLUMN, SALES_PSI_AP2_W_EOH_COLUMN,
        ]
        dst_cols = [
            SALES_PSI_AP2_W_SIMUL_RTF_COLUMN, SALES_PSI_AP2_W_SIMUL_SHORT_COLUMN,
            SALES_PSI_AP2_W_SIMUL_BOH_COLUMN, SALES_PSI_AP2_W_SIMUL_EOH_COLUMN,
        ]
        mask = df_in_SalesPSIAP2W[TIME_WEEK_COLUMN].eq(start_week)
        df_in_SalesPSIAP2W.loc[mask, dst_cols] = df_in_SalesPSIAP2W.loc[mask, src_cols].to_numpy()
        print_df(df_in_SalesPSIAP2W, 'STEP4 by 1.1  ____ df_in_SalesPSIAP2W .... start_week update')

        df_in_SalesPSIAP2W.loc[:, SALES_PSI_AP2_W_SIMUL_SHIPMENT_COLUMN] = df_in_SalesPSIAP2W.loc[:, SOP_W_SET_SOP_ADJ_QTY_COLUMN]
        print_df(df_in_SalesPSIAP2W, 'STEP4 by 1.2  ____ df_in_SalesPSIAP2W .... merge with curent_data')

        # Sales PSI AP2 W_Simul Arrival' 설정
        #   전체 데이터에서 week 순번 부여
        df_in_SalesPSIAP2W['week_rank'] = df_in_SalesPSIAP2W.groupby(group_col)[TIME_WEEK_COLUMN].rank(method='dense').astype(int) - 1

        #   모든 sop > 0 인 행에서 도착 위치 계산
        df_sop = df_in_SalesPSIAP2W[
            df_in_SalesPSIAP2W[SALES_PSI_AP2_W_SIMUL_SHIPMENT_COLUMN] > 0
        ][group_col + ['week_rank', TIME_WEEK_COLUMN, BOD_ITEM_BOD_LT_COLUMN, SALES_PSI_AP2_W_SIMUL_SHIPMENT_COLUMN]].copy()
        df_sop['target_rank'] = df_sop['week_rank'] + df_sop[BOD_ITEM_BOD_LT_COLUMN]

        #   target week 계산을 위해 week_rank <-> week 매핑 테이블 생성
        week_map = df_in_SalesPSIAP2W[group_col + ['week_rank', TIME_WEEK_COLUMN]].drop_duplicates()
        week_map.columns = group_col + ['target_rank', 'target_week']

        #   target_rank로 target_week 찾기
        df_sop = df_sop.merge(week_map, on=group_col +['target_rank'], how='left')

        #   next_week 주차 이상에 도착하는 것만 필터링
        df_sop = df_sop[df_sop['target_week'] >= next_week]

        #   target_rank 기준으로 그룹화하여 arrv 합산
        df_arrv = df_sop.groupby(group_col + ['target_rank'])[SALES_PSI_AP2_W_SIMUL_SHIPMENT_COLUMN].sum().reset_index()
        df_arrv.columns = group_col + ['week_rank', SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN]

        #   원본에 merge
        df_result = df_in_SalesPSIAP2W.merge(df_arrv, on=group_col + ['week_rank'], how='left')
        df_result[SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN] = df_result[SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN].fillna(0).astype(int)

        #   next_week 이전 주차는 arrv = 0
        df_result.loc[df_result[TIME_WEEK_COLUMN] < next_week, SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN] = 0

        df_result = df_result.drop(columns='week_rank').reset_index(drop=True)
        print_df(df_result, 'STEP4 by 1.4  ____ df_result .... Sales PSI AP2 W_Simul Arrival update')

        # 인덱스 재설정
        df_result = df_result.sort_values(group_col + [TIME_WEEK_COLUMN])
        step('=====> STEP4 by 1 End')




        step('=====> STEP4 by 2 Start : BOH 및 EOH 계산')

        @njit(cache=False)
        def _scan_inventory_numba(week_arr, grp_code, start_week_arr, dmd_arr, arrival_arr, short_arr,
                                  boh_in, eoh_in, rtf_in, short_in):

            n = len(week_arr)

            # (1) 출력 배열 - 입력값으로 초기화
            boh_out = np.empty(n, dtype=np.float64)
            rtf_out = np.empty(n, dtype=np.float64)
            eoh_out = np.empty(n, dtype=np.float64)
            short_out = np.empty(n, dtype=np.float64)

            for idx in range(n):
                boh_out[idx] = boh_in[idx]
                rtf_out[idx] = rtf_in[idx]
                eoh_out[idx] = eoh_in[idx]
                short_out[idx] = short_in[idx]

            # (2) 그룹 구간을 “연속 구간”으로 잡음
            i = 0
            while i < n:
                gcode = grp_code[i]

                # 그룹 구간 [i, j)
                j = i + 1
                while j < n and grp_code[j] == gcode:
                    j += 1

                # (3) 그룹별 “재계산 시작 주차” 찾기
                sw = start_week_arr[i]  # 항상 baseWeek (202548) 가져옴

                start_idx = i
                while start_idx < j and week_arr[start_idx] < sw:
                    start_idx += 1  # sw(202548) 미만인 주차는 skip

                if start_idx >= j:
                    i = j
                    continue

                # (4) 초기 prev_eoh 설정(가장 중요한 설계 포인트 중 하나).
                if start_idx > i:   # base_week 가 202548 이고 202547 이 있으면 start_idx > i
                    prev_eoh = eoh_in[start_idx - 1]  # 202547 의 EOH를 가져옴 (이전 주차의 EOH 사용)
                    # NaN 체크
                    if prev_eoh != prev_eoh:  # NaN check in Numba
                        prev_eoh = 0.0
                else:
                    prev_eoh = boh_in[start_idx]    # 해당 주차의 BOH 사용
                    if prev_eoh != prev_eoh:
                        prev_eoh = 0.0

                # (5) 주차별 계산
                k = start_idx
                while k < j:
                    # BOH 계산: 전주 EOH >= 0 이면 EOH, 아니면 0
                    if prev_eoh >= 0.0:
                        boh = prev_eoh
                    else:
                        boh = 0.0

                    dmd = dmd_arr[k]        # 당주필수 Dmd
                    nshort = short_arr[k]   # 당주필수 SHORT
                    arr = arrival_arr[k]

                    # NaN 체크 추가
                    dmd_is_nan = dmd != dmd
                    nshort_is_nan = nshort != nshort

                    # Dmd가 NaN이면 RTF도 0 (또는 NaN 유지)
                    if dmd_is_nan:
                        rtf = 0.0
                        short = 0.0
                        eoh = prev_eoh  # 이전 EOH 유지
                    else:
                        # RTF 계산: 당주필수SHORT 기준
                        # if
                        #   당주필수 SHORT >= 0 이면 Min(당주DEMAND - 당주필수 SHORT, BOH + ARRIVAL)
                        # else
                        #   당주필수SHORT < 0 이면 BOH + ARRIVAL
                        supply = boh + arr
                        if nshort_is_nan or nshort < 0.0:
                            # nshort가 NaN이거나 음수면 supply 사용
                            rtf = supply
                        else:
                            # 당주필수 SHORT >= 0 이면 Min(당주DEMAND - 당주필수 SHORT, BOH + ARRIVAL)
                            rtf = min(dmd - nshort, supply)

                        # short 계산: 당주필수SHORT 기준
                        # if
                        #   당주필수 SHORT=0 이면 당주 DEMAND - 당주 RTF
                        # else
                        #   만약 당주 RTF < 당주필수 SHORT 이면, 당주 DEMAND - 당주RTF
                        # else
                        #   당주 DEMAND - 당주 RTF
                        if nshort_is_nan or nshort == 0:
                            short = dmd - rtf
                        elif rtf < nshort:
                            short = dmd - rtf
                        else:
                            short = max(dmd - rtf, 0)  # 음수 방지

                    eoh = max(boh + arr - rtf, 0.0)  # 음수 방지
                    boh_out[k] = boh
                    rtf_out[k] = rtf
                    eoh_out[k] = eoh
                    short_out[k] = short
                    prev_eoh = eoh  # 다음 주차를 위해 업데이트

                    k += 1

                i = j

            return boh_out, rtf_out, eoh_out, short_out


        def calculate_inventory_numba(df: pd.DataFrame, group_cols: list[str],
                                      week_col: str, dmd_col: str, boh_col: str, eoh_col: str,
                                      n_short_col: str, short_col: str, rtf_col: str, arrival_col: str,
                                      base_week: int) -> pd.DataFrame:

            # (1) 정렬 (필수) - 같은 그룹이 연속으로 배치됨
            df = df.sort_values(group_cols + [week_col]).reset_index(drop=True)

            # (2) 그룹별 start_week 계산 - base_week 부터 시작
            start_week = np.full(len(df), base_week, dtype=df[week_col].dtype)

            # (3) Numba 입력 배열 준비(dtypes 고정이 성능/정확도에 중요)
            week_arr = df[week_col].to_numpy()
            if not np.issubdtype(week_arr.dtype, np.number):
                raise TypeError(f"{week_col}은(는) 숫자형 dtype 이어야 합니다. 현재 dtype={week_arr.dtype}")

            start_week_arr = np.asarray(start_week, dtype=week_arr.dtype)  # 날짜그룹의 시작은 항상 start_week 로 시작

            dmd_arr = df[dmd_col].to_numpy(dtype=np.float64, copy=False)
            arrival_arr = df[arrival_col].to_numpy(dtype=np.float64, copy=False)
            short_arr = df[n_short_col].to_numpy(dtype=np.float64, copy=False)

            # (4) 그룹 코드 생성 (pd.factorize로 각 그룹 조합에 고유 정수 부여)
            grp_code = pd.factorize(pd.MultiIndex.from_frame(df[group_cols]))[0].astype(np.int64)

            # (5) Numba 스캔 호출
            boh_in = df[boh_col].to_numpy(dtype=np.float64, copy=False)
            eoh_in = df[eoh_col].to_numpy(dtype=np.float64, copy=False)
            rtf_in = df[rtf_col].to_numpy(dtype=np.float64, copy=False)
            short_in = df[short_col].to_numpy(dtype=np.float64, copy=False)

            boh_out, rtf_out, eoh_out, short_out = _scan_inventory_numba(
                week_arr.astype(week_arr.dtype, copy=False),
                grp_code,
                start_week_arr,
                dmd_arr,
                arrival_arr,
                short_arr,
                boh_in,
                eoh_in,
                rtf_in,
                short_in,
            )

            # (7) 결과를 df에 반영
            df[boh_col] = boh_out
            df[rtf_col] = rtf_out
            df[eoh_col] = eoh_out
            df[short_col] = short_out

            return df



        # 그룹 컬럼 정의
        group_cols = [LOCATION_COLUMN, SALES_DOMAIN_AP2_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]

        # BOH, EOH, RTF 계산 호출
        df_SalesPSISimul = calculate_inventory_numba(
            df=df_result,
            group_cols=group_cols,
            week_col=TIME_WEEK_COLUMN,
            dmd_col=SALES_PSI_AP2_W_DMD_COLUMN,
            boh_col=SALES_PSI_AP2_W_SIMUL_BOH_COLUMN,
            eoh_col=SALES_PSI_AP2_W_SIMUL_EOH_COLUMN,
            n_short_col=SALES_PSI_AP2_W_SHORT_COLUMN,
            short_col=SALES_PSI_AP2_W_SIMUL_SHORT_COLUMN,
            rtf_col=SALES_PSI_AP2_W_SIMUL_RTF_COLUMN,
            arrival_col=SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN,
            base_week=next_week,
        )

        # 수량컬럼 정의
        int_cols = [
            SALES_PSI_AP2_W_SIMUL_BOH_COLUMN, SALES_PSI_AP2_W_SIMUL_EOH_COLUMN, SALES_PSI_AP2_W_SIMUL_RTF_COLUMN,
            SALES_PSI_AP2_W_SIMUL_SHORT_COLUMN, SALES_PSI_AP2_W_SIMUL_ARRIVAL_COLUMN,
        ]
        df_SalesPSISimul[int_cols] = df_SalesPSISimul[int_cols].fillna(0).astype(int)
        print_df(df_SalesPSISimul, 'STEP4 by 1.2  ____ df_SalesPSISimul .... calculate_inventory', True)

        step('=====> STEP4 by 2 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_SalesPSISimul = rename_and_delete_df(df_SalesPSISimul)

        df_out_SalesPSISimul[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SalesPSISimul = df_out_SalesPSISimul[fn_sales_psi_simul_columns]
        df_out_SalesPSISimul = ultra_fast_replace_to_none(df_out_SalesPSISimul)

        df_out_SalesPSIUpdateTime = pd.DataFrame({
            VERSION_NAME_COLUMN: [paramOutVersion],
            VERSION_INFO_SALES_PSI_UPDATE_TIME_COLUMN: [get_current_date_str()]
        })

        dataframes = {
            'df_out_SalesPSISimul': df_out_SalesPSISimul,
            'df_out_SalesPSIUpdateTime': df_out_SalesPSIUpdateTime,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SalesPSISimul = pd.DataFrame(columns=fn_sales_psi_simul_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SalesPSISimul = pd.DataFrame(columns=fn_sales_psi_simul_columns)
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
