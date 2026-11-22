"""
* 프로그램명
    - PY_UI_LoadingMasterSOPItemFlag

* 내용
    - SOP는 있는데 Loading Master MG에는 없는 Location / Item 신규 생성

* 변경이력
    - 2025.09.11 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_loadingmaster : Select ([Location].[Location] * [Item].[Item] ) on row, ({Measure.[Loading Master To Site_Valid]}) on column where {[Version].[Version Name]};
    - df_in_sopw          : Select ([Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Trans Mode].[Trans Mode].[VESSEL]) on row, ({Measure.[SOP W_SET MFG Qty]}) on column where {[Version].[Version Name], [Item].[Plan Group].[2]};

* Flow Summary
    - 1. Location/Item 기준으로 Loading Master와 SOPW를 비교하여 SOPW에만 있는 Location/Item을 Loading Master에 Insert


* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_loadingmaster

* 데이타 초기화
    - Delete data for model [Loading Master To Site] where{[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_LoadingMasterSOPItemFlag] for measures {[Loading Master To Site_SOP Item Flag]}
        using scope (Version.[Version Name].filter(#.Name in {"CWV_MP"}))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[Loading Master To Site_1st Container], Measure.[Loading Master To Site_20FT Minimum Lot], Measure.[Loading Master To Site_20FT Multiple Lot], Measure.[Loading Master To Site_20FT Qty], Measure.[Loading Master To Site_20FT Qty Override], Measure.[Loading Master To Site_2nd Container], Measure.[Loading Master To Site_40FT Qty], Measure.[Loading Master To Site_40FT Qty Override], Measure.[Loading Master To Site_40HC Minimum Lot], Measure.[Loading Master To Site_40HC Multiple Lot], Measure.[Loading Master To Site_40HC Qty], Measure.[Loading Master To Site_40HC Qty Override], Measure.[Loading Master To Site_45FT Qty], Measure.[Loading Master To Site_45FT Qty Override], Measure.[Loading Master To Site_53FT Qty], Measure.[Loading Master To Site_53FT Qty Override], Measure.[Loading Master To Site_BOX D], Measure.[Loading Master To Site_BOX H], Measure.[Loading Master To Site_BOX W], Measure.[Loading Master To Site_Build Ahead Period], Measure.[Loading Master To Site_CBM], Measure.[Loading Master To Site_FCL], Measure.[Loading Master To Site_FCL Item Flag],  Measure.[Loading Master To Site_Gross Weight], Measure.[Loading Master To Site_IF info By], Measure.[Loading Master To Site_IF info Dttm], Measure.[Loading Master To Site_Init By], Measure.[Loading Master To Site_Init Dttm], Measure.[Loading Master To Site_Item Site Cur Status_PL], Measure.[Loading Master To Site_LastW Item Flag], Measure.[Loading Master To Site_Minimum Lot], Measure.[Loading Master To Site_Multiple Lot], Measure.[Loading Master To Site_Net Weight], Measure.[Loading Master To Site_SOP Item Flag], Measure.[Loading Master To Site_TLB MAX Loading Rate], Measure.[Loading Master To Site_TLB MAX Loading Rate Override], Measure.[Loading Master To Site_TLB MIN Loading Rate], Measure.[Loading Master To Site_TLB MIN Loading Rate Override], Measure.[Loading Master To Site_Valid]}) on column limit 100;
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
str_instance = 'PY_UI_LoadingMasterSOPItemFlag'
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
            df_in_loadingmaster = read_csv_file("df_in_loadingmaster")
            df_in_sopw = read_csv_file("df_in_sopw")


        dataframes = {
            'df_in_loadingmaster': df_in_loadingmaster,
            'df_in_sopw': df_in_sopw,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_COLUMN = 'Item.[Item]'
        LOCATION_COLUMN = 'Location.[Location]'
        LOADING_MASTER_TO_SITE_VAILD_COLUMN = 'Loading Master To Site_Valid'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        SOP_W_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'

        LOADING_MASTER_TO_SITE_1ST_CONTAINER_COLUMN = 'Loading Master To Site_1st Container'
        LOADING_MASTER_TO_SITE_20FT_MINIMUN_LOT_COLUMN = 'Loading Master To Site_20FT Minimum Lot'
        LOADING_MASTER_TO_SITE_20FT_MULTIPLE_LOT_COLUMN = 'Loading Master To Site_20FT Multiple Lot'
        LOADING_MASTER_TO_SITE_20FT_QTY_COLUMN = 'Loading Master To Site_20FT Qty'
        LOADING_MASTER_TO_SITE_20FT_QTY_OVERRIDE_COLUMN = 'Loading Master To Site_20FT Qty Override'
        LOADING_MASTER_TO_SITE_2ND_CONTAINER_COLUMN = 'Loading Master To Site_2nd Container'
        LOADING_MASTER_TO_SITE_40FT_QTY_COLUMN = 'Loading Master To Site_40FT Qty'
        LOADING_MASTER_TO_SITE_40FT_QTY_OVERRIDE_COLUMN = 'Loading Master To Site_40FT Qty Override'
        LOADING_MASTER_TO_SITE_40HC_MINIMUN_LOT_COLUMN = 'Loading Master To Site_40HC Minimum Lot'
        LOADING_MASTER_TO_SITE_40HC_MULTIPLE_LOT_COLUMN = 'Loading Master To Site_40HC Multiple Lot'
        LOADING_MASTER_TO_SITE_40HC_QTY_COLUMN = 'Loading Master To Site_40HC Qty'
        LOADING_MASTER_TO_SITE_40HC_QTY_OVERRIDE_COLUMN = 'Loading Master To Site_40HC Qty Override'
        LOADING_MASTER_TO_SITE_45FT_QTY_COLUMN = 'Loading Master To Site_45FT Qty'
        LOADING_MASTER_TO_SITE_45FT_QTY_OVERRIDE_COLUMN = 'Loading Master To Site_45FT Qty Override'
        LOADING_MASTER_TO_SITE_53FT_QTY_COLUMN = 'Loading Master To Site_53FT Qty'
        LOADING_MASTER_TO_SITE_53FT_QTY_OVERRIDE_COLUMN = 'Loading Master To Site_53FT Qty Override'
        LOADING_MASTER_TO_SITE_BOX_D_COLUMN = 'Loading Master To Site_BOX D'
        LOADING_MASTER_TO_SITE_BOX_H_COLUMN = 'Loading Master To Site_BOX H'
        LOADING_MASTER_TO_SITE_BOX_W_COLUMN = 'Loading Master To Site_BOX W'
        LOADING_MASTER_TO_SITE_BUILD_AHEAD_PERIOD_COLUMN = 'Loading Master To Site_Build Ahead Period'
        LOADING_MASTER_TO_SITE_CBM_COLUMN = 'Loading Master To Site_CBM'
        LOADING_MASTER_TO_SITE_FCL_COLUMN = 'Loading Master To Site_FCL'
        LOADING_MASTER_TO_SITE_FCL_ITEM_FLAG_COLUMN = 'Loading Master To Site_FCL Item Flag'
        LOADING_MASTER_TO_SITE_GROSS_WEIGHT_COLUMN = 'Loading Master To Site_Gross Weight'
        LOADING_MASTER_TO_SITE_IF_INFO_BY_COLUMN = 'Loading Master To Site_IF info By'
        LOADING_MASTER_TO_SITE_IF_INFO_DTTM_COLUMN = 'Loading Master To Site_IF info Dttm'
        LOADING_MASTER_TO_SITE_INIT_BY_COLUMN = 'Loading Master To Site_Init By'
        LOADING_MASTER_TO_SITE_IMIT_DTTM_COLUMN = 'Loading Master To Site_Init Dttm'
        LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN = 'Loading Master To Site_Minimum Lot'
        LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN = 'Loading Master To Site_Multiple Lot'
        LOADING_MASTER_TO_SITE_NET_WEIGHT_COLUMN = 'Loading Master To Site_Net Weight'
        LOADING_MASTER_TO_SITE_SOP_ITEM_FLAG_COLUMN = 'Loading Master To Site_SOP Item Flag'
        LOADING_MASTER_TO_SITE_TLB_MAX_LOADING_RATE_COLUMN = 'Loading Master To Site_TLB MAX Loading Rate'
        LOADING_MASTER_TO_SITE_TLB_MAX_LOADING_RATE_OVERRIDE_COLUMN = 'Loading Master To Site_TLB MAX Loading Rate Override'
        LOADING_MASTER_TO_SITE_TLB_MIN_LOADING_RATE_COLUMN = 'Loading Master To Site_TLB MIN Loading Rate'
        LOADING_MASTER_TO_SITE_TLB_MIN_LOADING_RATE_OVERRIDE_COLUMN = 'Loading Master To Site_TLB MIN Loading Rate Override'
        LOADING_MASTER_TO_SITE_VAILD_COLUMN = 'Loading Master To Site_Valid'

        df_loadingmaster_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            LOADING_MASTER_TO_SITE_1ST_CONTAINER_COLUMN,
            LOADING_MASTER_TO_SITE_20FT_MINIMUN_LOT_COLUMN, LOADING_MASTER_TO_SITE_20FT_MULTIPLE_LOT_COLUMN,
            LOADING_MASTER_TO_SITE_20FT_QTY_COLUMN, LOADING_MASTER_TO_SITE_20FT_QTY_OVERRIDE_COLUMN,
            LOADING_MASTER_TO_SITE_2ND_CONTAINER_COLUMN,
            LOADING_MASTER_TO_SITE_40FT_QTY_COLUMN, LOADING_MASTER_TO_SITE_40FT_QTY_OVERRIDE_COLUMN,
            LOADING_MASTER_TO_SITE_40HC_MINIMUN_LOT_COLUMN, LOADING_MASTER_TO_SITE_40HC_MULTIPLE_LOT_COLUMN,
            LOADING_MASTER_TO_SITE_40HC_QTY_COLUMN, LOADING_MASTER_TO_SITE_40HC_QTY_OVERRIDE_COLUMN,
            LOADING_MASTER_TO_SITE_45FT_QTY_COLUMN, LOADING_MASTER_TO_SITE_45FT_QTY_OVERRIDE_COLUMN,
            LOADING_MASTER_TO_SITE_53FT_QTY_COLUMN, LOADING_MASTER_TO_SITE_53FT_QTY_OVERRIDE_COLUMN,
            LOADING_MASTER_TO_SITE_BOX_D_COLUMN, LOADING_MASTER_TO_SITE_BOX_H_COLUMN,
            LOADING_MASTER_TO_SITE_BOX_W_COLUMN, LOADING_MASTER_TO_SITE_BUILD_AHEAD_PERIOD_COLUMN,
            LOADING_MASTER_TO_SITE_CBM_COLUMN, LOADING_MASTER_TO_SITE_FCL_COLUMN, LOADING_MASTER_TO_SITE_FCL_ITEM_FLAG_COLUMN,
            LOADING_MASTER_TO_SITE_GROSS_WEIGHT_COLUMN, LOADING_MASTER_TO_SITE_IF_INFO_BY_COLUMN,
            LOADING_MASTER_TO_SITE_IF_INFO_DTTM_COLUMN, LOADING_MASTER_TO_SITE_INIT_BY_COLUMN, LOADING_MASTER_TO_SITE_IMIT_DTTM_COLUMN,
            LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN, LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN,
            LOADING_MASTER_TO_SITE_NET_WEIGHT_COLUMN, LOADING_MASTER_TO_SITE_SOP_ITEM_FLAG_COLUMN,
            LOADING_MASTER_TO_SITE_TLB_MAX_LOADING_RATE_COLUMN, LOADING_MASTER_TO_SITE_TLB_MAX_LOADING_RATE_OVERRIDE_COLUMN,
            LOADING_MASTER_TO_SITE_TLB_MIN_LOADING_RATE_COLUMN, LOADING_MASTER_TO_SITE_TLB_MIN_LOADING_RATE_OVERRIDE_COLUMN,
            LOADING_MASTER_TO_SITE_VAILD_COLUMN,
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        if df_in_sopw.empty:
            raise CustomException(".... df_in_sopw 값이 없습니다.")

        df_in_sopw.rename(columns={
            TO_LOCATION_COLUMN: SUB_LOCATION_COLUMN,
        }, inplace=True)

        step('=====> STEP3 End')




        # ################################################################################################################
        # # STEP 4 : output data machining
        # ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # 1. 필요한 컬럼만 선택하여 조인 조건을 위한 데이터프레임 생성
        sopw_keys = df_in_sopw[[LOCATION_COLUMN, ITEM_COLUMN]]
        loadingmaster_keys = df_in_loadingmaster[[LOCATION_COLUMN, ITEM_COLUMN]]

        # 2. anti-join 수행 (SQL의 NOT EXISTS와 동일) / 두 데이터프레임의 키 기준으로 병합하고 오른쪽에 해당하는 값이 없는 행만 필터링
        df_key_merged = pd.merge(
            sopw_keys,
            loadingmaster_keys,
            how='left',
            left_on=[LOCATION_COLUMN, ITEM_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_COLUMN],
            indicator=True
        )
        print_df(df_key_merged, 'STEP4 by 2.1 ____ df_key_merged .... create')

        anti_join_filter = df_key_merged['_merge'] == 'left_only'
        df_filtered_keys = df_key_merged[anti_join_filter].drop('_merge', axis=1).drop_duplicates()
        print_df(df_filtered_keys, 'STEP4 by 2.2 ____ df_filtered_keys .... filtered_keys, _merge drop')


        # 3. 원본 데이터프레임에서 필터링된 키에 해당하는 행 선택
        df_result = pd.merge(
            df_in_sopw,
            df_filtered_keys,
            on=[LOCATION_COLUMN, ITEM_COLUMN]
        )
        print_df(df_result, 'STEP4 by 3.1 ____ df_result .... create')


        # 4. SELECT 문에서 요청한 컬럼들과 상수값을 포함한 최종 결과 생성
        #   Measure.[Loading Master To Site_1st Container], Measure.[Loading Master To Site_20FT Minimum Lot], Measure.[Loading Master To Site_20FT Multiple Lot], Measure.[Loading Master To Site_20FT Qty], Measure.[Loading Master To Site_20FT Qty Override], Measure.[Loading Master To Site_2nd Container], Measure.[Loading Master To Site_40FT Qty], Measure.[Loading Master To Site_40FT Qty Override], Measure.[Loading Master To Site_40HC Minimum Lot], Measure.[Loading Master To Site_40HC Multiple Lot], Measure.[Loading Master To Site_40HC Qty], Measure.[Loading Master To Site_40HC Qty Override], Measure.[Loading Master To Site_45FT Qty], Measure.[Loading Master To Site_45FT Qty Override], Measure.[Loading Master To Site_53FT Qty], Measure.[Loading Master To Site_53FT Qty Override], Measure.[Loading Master To Site_BOX D], Measure.[Loading Master To Site_BOX H], Measure.[Loading Master To Site_BOX W], Measure.[Loading Master To Site_Build Ahead Period], Measure.[Loading Master To Site_CBM], Measure.[Loading Master To Site_FCL], Measure.[Loading Master To Site_FCL Item Flag], Measure.[Loading Master To Site_Gross Weight], Measure.[Loading Master To Site_IF info By], Measure.[Loading Master To Site_IF info Dttm], Measure.[Loading Master To Site_Init By], Measure.[Loading Master To Site_Init Dttm], Measure.[Loading Master To Site_Minimum Lot], Measure.[Loading Master To Site_Multiple Lot], Measure.[Loading Master To Site_Net Weight],  Measure.[Loading Master To Site_SOP Item Flag], Measure.[Loading Master To Site_TLB MAX Loading Rate], Measure.[Loading Master To Site_TLB MAX Loading Rate Override], Measure.[Loading Master To Site_TLB MIN Loading Rate], Measure.[Loading Master To Site_TLB MIN Loading Rate Override], Measure.[Loading Master To Site_Valid]
        #   "N", "1", "1", "0", "0", "N", "0", "0", "1", "1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "2", "0","N", "N", "0", "PY BATCH", SYSDATE(), , "PY BATCH", SYSDATE(), "1", "1", "0", "1", "0", "0", "0", "0", "True"
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df_loadingmaster = pd.DataFrame({
            VERSION_NAME_COLUMN: paramOutVersion,
            ITEM_COLUMN: df_result[ITEM_COLUMN],
            LOCATION_COLUMN: df_result[LOCATION_COLUMN],
            SUB_LOCATION_COLUMN: df_result[SUB_LOCATION_COLUMN],
            TRANS_MODE_COLUMN: df_result[TRANS_MODE_COLUMN],
            LOADING_MASTER_TO_SITE_1ST_CONTAINER_COLUMN : 'N',
            LOADING_MASTER_TO_SITE_20FT_MINIMUN_LOT_COLUMN : '1',
            LOADING_MASTER_TO_SITE_20FT_MULTIPLE_LOT_COLUMN : '1',
            LOADING_MASTER_TO_SITE_20FT_QTY_COLUMN : '0',
            LOADING_MASTER_TO_SITE_20FT_QTY_OVERRIDE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_2ND_CONTAINER_COLUMN : 'N',
            LOADING_MASTER_TO_SITE_40FT_QTY_COLUMN : '0',
            LOADING_MASTER_TO_SITE_40FT_QTY_OVERRIDE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_40HC_MINIMUN_LOT_COLUMN : '1',
            LOADING_MASTER_TO_SITE_40HC_MULTIPLE_LOT_COLUMN : '1',
            LOADING_MASTER_TO_SITE_40HC_QTY_COLUMN : '0',
            LOADING_MASTER_TO_SITE_40HC_QTY_OVERRIDE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_45FT_QTY_COLUMN : '0',
            LOADING_MASTER_TO_SITE_45FT_QTY_OVERRIDE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_53FT_QTY_COLUMN : '0',
            LOADING_MASTER_TO_SITE_53FT_QTY_OVERRIDE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_BOX_D_COLUMN : '0',
            LOADING_MASTER_TO_SITE_BOX_H_COLUMN : '0',
            LOADING_MASTER_TO_SITE_BOX_W_COLUMN : '0',
            LOADING_MASTER_TO_SITE_BUILD_AHEAD_PERIOD_COLUMN : '2',
            LOADING_MASTER_TO_SITE_CBM_COLUMN : '0',
            LOADING_MASTER_TO_SITE_FCL_COLUMN : 'N',
            LOADING_MASTER_TO_SITE_FCL_ITEM_FLAG_COLUMN : 'N',
            LOADING_MASTER_TO_SITE_GROSS_WEIGHT_COLUMN : '0',
            LOADING_MASTER_TO_SITE_IF_INFO_BY_COLUMN : 'PY BATCH',
            LOADING_MASTER_TO_SITE_IF_INFO_DTTM_COLUMN : current_date,
            LOADING_MASTER_TO_SITE_INIT_BY_COLUMN : 'PY BATCH',
            LOADING_MASTER_TO_SITE_IMIT_DTTM_COLUMN : current_date,
            LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN : '1',
            LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN : '1',
            LOADING_MASTER_TO_SITE_NET_WEIGHT_COLUMN : '0',
            LOADING_MASTER_TO_SITE_SOP_ITEM_FLAG_COLUMN : 1,
            LOADING_MASTER_TO_SITE_TLB_MAX_LOADING_RATE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_TLB_MAX_LOADING_RATE_OVERRIDE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_TLB_MIN_LOADING_RATE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_TLB_MIN_LOADING_RATE_OVERRIDE_COLUMN : '0',
            LOADING_MASTER_TO_SITE_VAILD_COLUMN : 'True',
        })
        df_loadingmaster = df_loadingmaster[df_loadingmaster_columns]
        print_df(df_loadingmaster, 'STEP4 by 4.1 ____ df_loadingmaster .... column create')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_loadingmaster = rename_and_delete_df(df_loadingmaster)

        dataframes = {
            'df_out_loadingmaster': df_out_loadingmaster,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_loadingmaster = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_loadingmaster = pd.DataFrame([], columns=[])
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
