"""
* 프로그램명
    - PY_UI_ProdPrice_Threshold

* 내용
    - 입력된 값 초과하는 Price를 표기하기 위한 Price별 Threshold 값 계산 (Product Price (EW) 화면 내 Threshold 기능에 사용할 Base 값)

* 변경이력
    - 2025.12.12 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_RRPPrice : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_RRP]}) on column where {[Version].[Version Name]};
    - df_in_DPrice   : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_D Price]}) on column where {[Version].[Version Name]};
    - df_in_NPrice   : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_N Price]}) on column where {[Version].[Version Name]};
    - df_in_POPrice  : Select ([Location].[Location] * [Item].[Item] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row, ({Measure.[Product Price M_PO Price]}) on column where {[Version].[Version Name]};

* Flow Summary
    - STEP1. RRP Price 기준 산출
    - STEP2. D Price 기준 산출
    - STEP3. N Price 기준 산출
    - STEP4. PO Price 기준 산출
    - STEP5. Measure Update

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ThresholdResult

* 데이타 초기화
    - DELETE DATA FOR MODEL [Product Price M] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ProdPrice_Threshold] for measures {[Product Price M_Threshold RRP],[Product Price M_Threshold D Price], [Product Price M_Threshold N Price], [Product Price M_Threshold PO Price]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Item].[Item] * [Location].[Location] * [Time].[Planning Month] * [Sub Location].[Sub Location] ) on row,
        ({Measure.[Product Price M_Threshold RRP], Measure.[Product Price M_Threshold D Price], Measure.[Product Price M_Threshold N Price], Measure.[Product Price M_Threshold PO Price]}) on column;

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
str_instance = 'PY_UI_ProdPrice_Threshold'
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
            df_in_RRPPrice = read_csv_file("df_in_RRPPrice")
            df_in_DPrice = read_csv_file("df_in_DPrice")
            df_in_NPrice = read_csv_file("df_in_NPrice")
            df_in_POPrice = read_csv_file("df_in_POPrice")


        dataframes = {
            'df_in_RRPPrice': df_in_RRPPrice,
            'df_in_DPrice': df_in_DPrice,
            'df_in_NPrice': df_in_NPrice,
            'df_in_POPrice': df_in_POPrice,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1(End) : Check memory usage & runtime')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2(Start) : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'

        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_PLANNING_MONTH_COLUMN = 'Time.[Planning Month]'

        PRODUCT_PRICE_M_D_PRICE_COLUMN = 'Product Price M_D Price'
        PRODUCT_PRICE_M_N_PRICE_COLUMN = 'Product Price M_N Price'
        PRODUCT_PRICE_M_PO_PRICE_COLUMN = 'Product Price M_PO Price'
        PRODUCT_PRICE_M_RRP_COLUMN = 'Product Price M_RRP'

        PRODUCT_PRICE_M_THRESHOLD_RRP_COLUMN = 'Product Price M_Threshold RRP'
        PRODUCT_PRICE_M_THRESHOLD_D_PRICE_COLUMN = 'Product Price M_Threshold D Price'
        PRODUCT_PRICE_M_THRESHOLD_N_PRICE_COLUMN = 'Product Price M_Threshold N Price'
        PRODUCT_PRICE_M_THRESHOLD_PO_PRICE_COLUMN = 'Product Price M_Threshold PO Price'

        df_version_columns = [VERSION_NAME_COLUMN]

        df_key_columns = [ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TIME_PLANNING_MONTH_COLUMN]

        df_threshold_result_columns = [
            PRODUCT_PRICE_M_THRESHOLD_RRP_COLUMN, PRODUCT_PRICE_M_THRESHOLD_D_PRICE_COLUMN,
            PRODUCT_PRICE_M_THRESHOLD_N_PRICE_COLUMN, PRODUCT_PRICE_M_THRESHOLD_PO_PRICE_COLUMN,
        ]

        df_fn_threshold_result_columns = df_version_columns + df_key_columns +  df_threshold_result_columns

        step('=====> STEP 2(End) : Check memory usage & runtime')

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')


        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_BODAll = df_in_BODAll[
        #     (df_in_BODAll[LOCATION_COLUMN] == 'S348WD20') & (df_in_BODAll[ITEM_COLUMN] == 'QN65QN90DAFXZA')
        # ].copy()
        # print_df(df_in_BODAll, 'STEP3 by 1.1 ____ df_in_BODAll .... filter', True)
        #
        # df_in_BODItemW = df_in_BODItemW[
        #     (df_in_BODItemW[ITEM_COLUMN] == 'QN65QN90DAFXZA') &  (df_in_BODItemW[SUB_LOCATION_COLUMN] == 'S348WD20')
        # ].copy()
        # print_df(df_in_BODItemW, 'STEP3 by 1.2 ____ df_in_BODItemW .... filter', True)
        # ------------------ 테스트 디버깅용 ------------------ end



        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : 이전 달의 각 Price와 당월의 Price 간 산식 기준 비율을 구하여 Threshold에 결과값 Update')
        if not df_in_RRPPrice.empty:
            # 1) 정렬 (LAG는 순서가 중요)
            df_in_RRPPrice = df_in_RRPPrice.sort_values(df_key_columns)

            # 2) LAG 구현: 그룹별 지난달 가격
            group_keys = [LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN]
            df_in_RRPPrice["current_month_price"] = df_in_RRPPrice[PRODUCT_PRICE_M_RRP_COLUMN]
            df_in_RRPPrice["prev_month_price"] = df_in_RRPPrice.groupby(group_keys)["current_month_price"].shift(1)

            den = df_in_RRPPrice["current_month_price"].replace(0, np.nan)  # 0 나눗셈 방지
            df_in_RRPPrice["rrp_threshold"] = (
                (df_in_RRPPrice["prev_month_price"] - df_in_RRPPrice["current_month_price"]).abs()
                .div(den)
                .mul(100)
                .round(0)
            )

            # 4) 최종 SELECT 컬럼만 추려내기
            df_RRPPrice = df_in_RRPPrice[df_key_columns + ["rrp_threshold"]]
        else:
            df_RRPPrice = pd.DataFrame(columns=df_key_columns + ["rrp_threshold"])

        print_df(df_RRPPrice, 'STEP4 by 1.1  ____ df_RRPPrice .... create')
        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : D Price 기준 산출')
        if not df_in_DPrice.empty:
            # 1) 정렬 (LAG는 순서가 중요)
            df_in_DPrice = df_in_DPrice.sort_values(df_key_columns)

            # 2) LAG 구현: 그룹별 지난달 가격
            group_keys = [LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN]
            df_in_DPrice["current_month_price"] = df_in_DPrice[PRODUCT_PRICE_M_D_PRICE_COLUMN]
            df_in_DPrice["prev_month_price"] = df_in_DPrice.groupby(group_keys)["current_month_price"].shift(1)

            # 3) d_threshold 계산
            #    round(abs(prev-current)/current*100, 0)
            den = df_in_DPrice["current_month_price"].replace(0, np.nan)  # 0으로 나누기 방지
            df_in_DPrice["d_threshold"] = (
                (df_in_DPrice["prev_month_price"] - df_in_DPrice["current_month_price"]).abs()
                .div(den)
                .mul(100)
                .round(0)
            )

            # 4) 최종 SELECT 컬럼만 추려내기
            df_DPrice = df_in_DPrice[df_key_columns + ["d_threshold"]]
        else:
            df_DPrice = pd.DataFrame(columns=df_key_columns + ["d_threshold"])

        print_df(df_DPrice, 'STEP4 by 2.1  ____ df_DPrice .... create')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : N Price 기준 산출')
        if not df_in_NPrice.empty:
            # 1) 정렬 (LAG는 순서가 중요)
            df_in_NPrice = df_in_NPrice.sort_values(df_key_columns)

            # 2) LAG 구현: 그룹별 지난달 가격
            group_keys = [LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN]
            df_in_NPrice["current_month_price"] = df_in_NPrice[PRODUCT_PRICE_M_N_PRICE_COLUMN]
            df_in_NPrice["prev_month_price"] = df_in_NPrice.groupby(group_keys)["current_month_price"].shift(1)

            # 3) n_threshold 계산
            #    round(abs(prev-current)/current*100, 0)
            den = df_in_NPrice["current_month_price"].replace(0, np.nan)  # 0으로 나누기 방지
            df_in_NPrice["n_threshold"] = (
                (df_in_NPrice["prev_month_price"] - df_in_NPrice["current_month_price"]).abs()
                .div(den)
                .mul(100)
                .round(0)
            )

            # 4) 최종 SELECT 컬럼만 추려내기
            df_NPrice = df_in_NPrice[df_key_columns + ["n_threshold"]]
        else:
            df_NPrice = pd.DataFrame(columns=df_key_columns + ["n_threshold"])

        print_df(df_NPrice, 'STEP4 by 3.1  ____ df_NPrice .... create')
        step('=====> STEP4 by 3 End')



        step('=====> STEP4 by 4 Start : PO Price 기준 산출')
        if not df_in_POPrice.empty:
            # 1) 정렬 (LAG는 순서가 중요)
            df_in_POPrice = df_in_POPrice.sort_values(df_key_columns)

            # 2) LAG 구현: 그룹별 지난달 가격
            group_keys = [LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN]
            df_in_POPrice["current_month_price"] = df_in_POPrice[PRODUCT_PRICE_M_PO_PRICE_COLUMN]
            df_in_POPrice["prev_month_price"] = df_in_POPrice.groupby(group_keys)["current_month_price"].shift(1)

            # 3) po_threshold 계산
            #    round(abs(prev-current)/current*100, 0)
            den = df_in_POPrice["current_month_price"].replace(0, np.nan)  # 0으로 나누기 방지
            df_in_POPrice["po_threshold"] = (
                (df_in_POPrice["prev_month_price"] - df_in_POPrice["current_month_price"]).abs()
                .div(den)
                .mul(100)
                .round(0)
            )

            # 4) 최종 SELECT 컬럼만 추려내기
            df_POPrice = df_in_POPrice[df_key_columns + ["po_threshold"]]
        else:
            df_POPrice = pd.DataFrame(columns=df_key_columns + ["po_threshold"])

        print_df(df_POPrice, 'STEP4 by 4.1  ____ df_POPrice .... create')
        step('=====> STEP4 by 4 End')



        step('=====> STEP4 by 5 Start : 데이터프레임 합치기 -> Measure Update')
        df_ThresholdResult = pd.concat([df_RRPPrice, df_DPrice, df_NPrice, df_POPrice], ignore_index=True).drop_duplicates()
        print_df(df_ThresholdResult, 'STEP4 by 5.1  ____ df_ThresholdResult .... create')

        df_ThresholdResult.rename(columns={
            'rrp_threshold': PRODUCT_PRICE_M_THRESHOLD_RRP_COLUMN,
            'd_threshold': PRODUCT_PRICE_M_THRESHOLD_D_PRICE_COLUMN,
            'n_threshold': PRODUCT_PRICE_M_THRESHOLD_N_PRICE_COLUMN,
            'po_threshold': PRODUCT_PRICE_M_THRESHOLD_PO_PRICE_COLUMN,
        }, inplace=True)

        int_columns = [
            PRODUCT_PRICE_M_THRESHOLD_RRP_COLUMN, PRODUCT_PRICE_M_THRESHOLD_D_PRICE_COLUMN,
            PRODUCT_PRICE_M_THRESHOLD_N_PRICE_COLUMN, PRODUCT_PRICE_M_THRESHOLD_PO_PRICE_COLUMN,
        ]
        df_ThresholdResult[int_columns] = df_ThresholdResult[int_columns].fillna(0).astype(int)

        df_ThresholdResult[TIME_PLANNING_MONTH_COLUMN] = df_ThresholdResult[TIME_PLANNING_MONTH_COLUMN].astype(str)
        groupby_columns = df_key_columns
        sum_columns = int_columns
        agg_dict = {col: 'sum' for col in sum_columns}
        df_ThresholdResult = df_ThresholdResult.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_ThresholdResult, 'STEP4 by 5.2  ____ df_ThresholdResult .... sum')
        df_ThresholdResult[TIME_PLANNING_MONTH_COLUMN] = df_ThresholdResult[TIME_PLANNING_MONTH_COLUMN].astype(int)
        step('=====> STEP4 by 5 End')



        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_ThresholdResult = rename_and_delete_df(df_ThresholdResult)

        # 최종 아웃풋 컬럼 설정
        df_out_ThresholdResult[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ThresholdResult = df_out_ThresholdResult[df_fn_threshold_result_columns]
        df_out_ThresholdResult = df_out_ThresholdResult.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None, 0: None})

        dataframes = {
            'df_out_ThresholdResult': df_out_ThresholdResult,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ThresholdResult = pd.DataFrame(columns=df_fn_threshold_result_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ThresholdResult = pd.DataFrame(columns=df_fn_threshold_result_columns)
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