"""
* 프로그램명
    - PY_UI_ETCInvMgmt

* 내용
    - ETC Inv Master Data 생성 관련 Load

* 변경이력
    - 2026.02.09 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_MDMHorizon : Select (&MDMHorizon);
    - df_in_OnHand     : Select ([Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Dummy], Measure.[Onhand Mtrl_Total]}) on column where {[Version].[Version Name], [Item Material].[SCM Flag].filter(#.Name != "N")};
    - df_in_EtcInv     : Select ([Location].[Location] * &MDMHorizon * [Item Material].[Item Material] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[ETC Inv Mst W_Days of Inv], Measure.[Dummy]}) on column where {[Version].[Version Name]};

* Flow Summary
    - STEP1. ONHAND Input 와 MDMHorizon 을 Cross Join 한다
    - STEP2. ETC Input 에 없는 OnHand 추출
    - STEP3. 결과저장


* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_EctInvMstW

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ETCInvMgmt] for measures {[ETC Inv Mst W_Days of Inv]} using scope (Version.[Version Name].filter(#.Name in {"CWV_MP"}))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[ETC Inv Mst W_Days of Inv]}) on column limit 10;

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
str_instance = 'PY_UI_ETCInvMgmt'
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
            df_in_OnHand = read_csv_file("df_in_OnHand")
            df_in_EtcInv = read_csv_file("df_in_EtcInv")

        dataframes = {
            'df_in_MDMHorizon': df_in_MDMHorizon,
            'df_in_OnHand': df_in_OnHand,
            'df_in_EtcInv': df_in_EtcInv,
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
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_MATERIAL_COLUMN = 'Item Material.[Item Material]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        DUMMY_COLUMN = 'Dummy'
        ONHABD_MTRL_TOTAL_COLUMN = 'Onhand Mtrl_Total'
        ETC_INV_MST_W_DAYS_OF_INV_COLUMN = 'ETC Inv Mst W_Days of Inv'

        ETC_INV_MST_W_UPDATED_BY_COLUMN = 'ETC Inv Mst W_Updated By'
        ETC_INV_MST_W_UPDATE_TIME_COLUMN = 'ETC Inv Mst W_Update Time'
        ETC_INV_MST_W_CREATED_BY_COLUMN = 'ETC Inv Mst W_Created By'
        ETC_INV_MST_W_CREATE_TIME_COLUMN = 'ETC Inv Mst W_Creation Time'

        VESSEL_VALUE = 'VESSEL'

        version_column = [VERSION_NAME_COLUMN]

        etc_inv_mst_w_column = [
            LOCATION_COLUMN, ITEM_MATERIAL_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN,
            ETC_INV_MST_W_DAYS_OF_INV_COLUMN,
            ETC_INV_MST_W_CREATED_BY_COLUMN, ETC_INV_MST_W_CREATE_TIME_COLUMN,
        ]

        fn_etc_inv_mst_w_columns = version_column + etc_inv_mst_w_column

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_SalesPSIAP2W = df_in_SalesPSIAP2W[df_in_SalesPSIAP2W[ITEM_COLUMN].isin(['LS24D300GAUXEN', 'LS24D300GAUXEN', 'LS24D300GAUXEN', 'LS24D300GAUXEN'])]
        # df_in_SalesPSIAP2W = df_in_SalesPSIAP2W[
        #     (df_in_SalesPSIAP2W[ITEM_COLUMN] == 'LH85BEDHLGUXEN') &
        #     (df_in_SalesPSIAP2W[SALES_DOMAIN_AP2_COLUMN] == 300132) &
        #     (df_in_SalesPSIAP2W[LOCATION_COLUMN] == 'L401') &
        #     (df_in_SalesPSIAP2W[SUB_LOCATION_COLUMN] == 'P401')
        # ].copy()
        # print_df(df_in_SalesPSIAP2W, 'STEP3 by 0.0.1  ____ df_in_SalesPSIAP2W .... filter')

        # df_in_SOPW = df_in_SOPW[df_in_SOPW[ITEM_COLUMN].isin(['LH75QETEPGCXEN'])]
        # print_df(df_in_SOPW, 'STEP3 by 0.0.2  ____ df_in_SOPW .... filter', True)
        # ------------------ 테스트 디버깅용 ------------------ end


        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_OnHand.empty :
            raise CustomException("STEP3 by 0.1 ____ df_in_OnHand 값이 없습니다.")


        current_date = get_current_date_str('UTC')
        step(f'=====> current_date : {current_date}')


        drop_columns = [DUMMY_COLUMN, ONHABD_MTRL_TOTAL_COLUMN]
        for col in drop_columns:
            df_in_EtcInv.drop(columns=[col], inplace=True, errors='ignore')
            df_in_OnHand.drop(columns=[col], inplace=True, errors='ignore')


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

        df_in_EtcInv.loc[:, TIME_WEEK_COLUMN] = df_in_EtcInv[TIME_WEEK_COLUMN].astype("int64")

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : ONHAND Input 와 MDMHorizon 을 Cross Join 한다')

        df_in_OnHand = pd.merge(df_in_OnHand, df_in_MDMHorizon, how='cross').drop_duplicates()
        df_in_OnHand[TRANS_MODE_COLUMN] = VESSEL_VALUE
        print_df(df_in_OnHand, 'STEP4 by 1.1  ____ df_in_OnHand .... Cross Join')

        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : ETC Input 에 없는 OnHand 추출')

        # df1에 없고 df2에만 있는 행 추출
        if df_in_EtcInv.empty :
            df_EctInvMstW = df_in_OnHand.copy()
            df_EctInvMstW.loc[:, ETC_INV_MST_W_DAYS_OF_INV_COLUMN] = None
            print_df(df_EctInvMstW, 'STEP4 by 2.1  ____ df_EctInvMstW .... empty df_in_EtcInv')

        else :
            df_EctInvMstW = df_in_OnHand.merge(
                df_in_EtcInv, how='left',
                on=[LOCATION_COLUMN, ITEM_MATERIAL_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN],
                indicator=True
            )
            df_EctInvMstW = df_EctInvMstW[df_EctInvMstW['_merge'] == 'left_only'].drop(columns=['_merge'])
            print_df(df_EctInvMstW, 'STEP4 by 2.1  ____ df_EctInvMstW .... left_only')


        df_EctInvMstW[ETC_INV_MST_W_CREATED_BY_COLUMN] = 'PY_UI_ETCInvMgmt'
        df_EctInvMstW[ETC_INV_MST_W_CREATE_TIME_COLUMN] = current_date
        df_EctInvMstW[ETC_INV_MST_W_UPDATED_BY_COLUMN] = 'PY_UI_ETCInvMgmt'
        df_EctInvMstW[ETC_INV_MST_W_UPDATE_TIME_COLUMN] = current_date

        df_EctInvMstW[ETC_INV_MST_W_DAYS_OF_INV_COLUMN] = 0

        step('=====> STEP4 by 2 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_EctInvMstW = rename_and_delete_df(df_EctInvMstW)

        df_out_EctInvMstW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_EctInvMstW = df_out_EctInvMstW[fn_etc_inv_mst_w_columns]
        df_out_EctInvMstW = df_out_EctInvMstW.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_EctInvMstW': df_out_EctInvMstW,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_EctInvMstW = pd.DataFrame(columns=fn_etc_inv_mst_w_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_EctInvMstW = pd.DataFrame(columns=fn_etc_inv_mst_w_columns)
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
