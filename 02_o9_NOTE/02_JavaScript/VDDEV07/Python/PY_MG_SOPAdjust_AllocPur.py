"""
* 프로그램명
    - PY_MG_SOPAdjust_AllocPur

* 내용
    - Tot Supply / Intransit으로 반영 / 001.020W Solver Inputs Inventory Inputs By OrderLine ID
    - ETD Plan -> 확정선적계획으로 반영 / 001.021W Solver Inputs WIP

* 변경이력
    - 2025.12.16 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_AllocPurSum : Select (&MDMHorizon * [Item Material].[Item Material] * [Sub Location].[Sub Location] ) on row, ({Measure.[Alloc Pur Sum_ETD Plan], Measure.[Alloc Pur Sum_ETD Plan Flag], Measure.[Alloc Pur Sum_Tot Supply]}) on column where {[Version].[Version Name]};
    - df_in_AllocPur    : Select ([Location].[Location] * &MDMHorizon * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Alloc Pur_ETD Plan], Measure.[Alloc Pur_ETD Plan Flag], Measure.[Alloc Pur_ETD Plan LT]}) on column where {Measure.[Alloc Pur_ETD Plan] > 0, [Version].[Version Name]};

* Flow Summary
    -

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_output_intransit
    - df_output_distorder

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_MG_SOPAdjust_AllocPur] for measures {[W WIP Material Consumption Quantity]} using scope (&MPV)
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
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_SOPAdjust_AllocPur'
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



def set_unique_combinations(df, df2, columns):
    cols = list(filter(lambda col: col != TIME_WEEK_COLUMN, columns))

    # 데이터의 모든 고유 조합 생성
    unique_combinations = df[cols].copy().drop_duplicates()

    # 주차(TIME_WEEK_COLUMN) 데이터의 모든 조합 산출
    df2 = df2.assign(key=1)
    unique_combinations = unique_combinations.assign(key=1)
    all_possible_combinations = unique_combinations.merge(df2, how="outer").drop(columns=['key']).drop_duplicates()

    # 결측 데이터 찾기 (left join & 필터링)
    missing_rows = all_possible_combinations.merge(
        df[columns], on=columns, how="left", indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return missing_rows




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
            df_in_AllocPurSum = read_csv_file("df_in_AllocPurSum")
            df_in_AllocPur = read_csv_file("df_in_AllocPur")


        dataframes = {
            'df_in_AllocPurSum': df_in_AllocPurSum,
            'df_in_AllocPur': df_in_AllocPur,
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
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_COLUMN = 'Item.[Item]'
        DOCUMENTS_ORDERLINEID_COLUMN = '[Documents].[OrderlineID]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'

        W_WIP_PROPAGATION_UPSTREAM_CONSUMPTION_COLUMN = 'W WIP Propagation Upstream Consumption'
        W_WIP_PEGGING_ID_COLUMN = 'W WIP Pegging ID'
        W_ORDER_TYPE_COLUMN = 'W Order Type'
        W_WIP_TYPE_COLUMN = 'W WIP Type'

        W_WIP_METERIAL_PRODUCTION_QUANTITY_COLUMN = 'W WIP Material Production Quantity'
        W_WIP_METERIAL_CONSUMPTIONN_QUANTITY_COLUMN = 'W WIP Material Consumption Quantity'

        ALLOC_PUR_ETD_PLAN_COLUMN = 'Alloc Pur_ETD Plan'
        ALLOC_PUR_ETD_PLAN_FLAG_COLUMN = 'Alloc Pur_ETD Plan Flag'
        ALLOC_PUR_ETD_PLAN_LT_COLUMN = 'Alloc Pur_ETD Plan LT'

        ALLOC_PUR_SUM_ETD_PLAN_COLUMN = 'Alloc Pur Sum_ETD Plan'
        ALLOC_PUR_SUM_ETD_PLAN_FLAG_COLUMN = 'Alloc Pur Sum_ETD Plan Flag'
        ALLOC_PUR_SUM_TOT_SUPPLY_COLUMN = 'Alloc Pur Sum_Tot Supply'

        W_EXPECTED_RECEIPTS_COLUMN = 'W Expected Receipts'
        W_EXPECTED_RECEIPTS_PEGGING_ID_COLUMN = 'W Expected Receipts Pegging ID'

        version_columns = [VERSION_NAME_COLUMN]

        key_1_columns = [LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN]

        intransit_columns = [
            W_EXPECTED_RECEIPTS_COLUMN, W_EXPECTED_RECEIPTS_PEGGING_ID_COLUMN, W_ORDER_TYPE_COLUMN,
        ]

        fn_intransit_columns = version_columns + key_1_columns + intransit_columns


        key_2_columns = [LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, ACTIVITY1_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN]

        solver_inputs_wip_columns = [
            W_WIP_PROPAGATION_UPSTREAM_CONSUMPTION_COLUMN, W_WIP_PEGGING_ID_COLUMN,
            W_WIP_METERIAL_PRODUCTION_QUANTITY_COLUMN, W_WIP_METERIAL_CONSUMPTIONN_QUANTITY_COLUMN, W_WIP_TYPE_COLUMN,
        ]

        fn_solver_inputs_wip_columns = version_columns + key_2_columns + solver_inputs_wip_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[LOCATION_COLUMN] == 'P306']
        # print_df(df_in_BODProdSET, 'STEP3 by 1.1  ____ df_in_BODProdSET .... filter', True)
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[SUB_LOCATION_COLUMN] == 'L5N0']
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_AllocPurSum.empty:
            raise CustomException("STEP3 by 0 ____ df_in_AllocPurSum 값이 없습니다.")


        # ETD Plan Flag = Frozen 아닌 대상인 ToT Supply 조회
        # df_in_AllocPurSum = df_in_AllocPurSum[df_in_AllocPurSum[ALLOC_PUR_SUM_ETD_PLAN_FLAG_COLUMN].ne("Frozen", fill_value=True)]
        df_in_AllocPurSum = df_in_AllocPurSum[df_in_AllocPurSum[ALLOC_PUR_SUM_ETD_PLAN_FLAG_COLUMN] != "MFGFrozen"].copy()
        print_df(df_in_AllocPurSum, 'STEP3 by 1  ____ df_in_AllocPurSum .... ETD Plan Flag != MFGFrozen filtered')

        df_in_AllocPur = df_in_AllocPur[df_in_AllocPur[ALLOC_PUR_ETD_PLAN_FLAG_COLUMN] == "MFGFrozen"].copy()
        print_df(df_in_AllocPur, 'STEP3 by 1  ____ df_in_AllocPur .... ETD Plan Flag == MFGFrozen filtered')
        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        # -------------------- df_output_intransit
        step('=====> STEP4 by 1-1 Start : df_in_AllocPurSum 에 필드 추가 및 필드 정리')
        df_in_AllocPurSum.rename(columns={
            ITEM_METERIAL_COLUMN: ITEM_COLUMN,
            SUB_LOCATION_COLUMN: LOCATION_COLUMN,
        }, inplace=True)

        df_in_AllocPurSum[W_EXPECTED_RECEIPTS_PEGGING_ID_COLUMN] = 2
        df_in_AllocPurSum[W_EXPECTED_RECEIPTS_COLUMN] = df_in_AllocPurSum[ALLOC_PUR_SUM_TOT_SUPPLY_COLUMN]

        df_in_AllocPurSum.drop(columns=[
            ALLOC_PUR_SUM_ETD_PLAN_FLAG_COLUMN, ALLOC_PUR_SUM_TOT_SUPPLY_COLUMN,
        ], inplace=True)
        print_df(df_in_AllocPurSum, 'STEP4 by 1-1.1  ____ df_in_AllocPurSum .... select')
        step('=====> STEP4 by 1-1 End')



        step('=====> STEP4 by 1-2 Start : df_in_AllocPurSum 에 orderlineid 필드 추가 및 필드 정리')
        col = DOCUMENTS_ORDERLINEID_COLUMN
        prefix = "INV_"
        width = 10

        # 컬럼이 없으면 생성(전부 NA로)
        if col not in df_in_AllocPurSum.columns:
            df_in_AllocPurSum[col] = pd.NA

        # 1) 기존 SUI_########## 형태에서 숫자만 뽑아 MAX 계산 (기존 값 유지 대상 포함)
        existing = df_in_AllocPurSum[col].dropna().astype(str)

        sui_nums = (
            existing[existing.str.startswith(prefix)]
            .str.slice(len(prefix), len(prefix) + width)
            .where(lambda s: s.str.fullmatch(r"\d+"))  # prefix 뒤가 숫자일 때만
            .dropna()
            .astype(int)
        )

        start_seq = (int(sui_nums.max()) + 1) if not sui_nums.empty else 1

        # 2) 채번이 필요한 행(NA 또는 공백)만 골라서 채움
        s = df_in_AllocPurSum[col].astype("string")  # NA-safe 문자열
        need_mask = s.isna() | (s.str.strip() == "")

        k = int(need_mask.sum())
        seqs = pd.RangeIndex(start_seq, start_seq + k)

        df_in_AllocPurSum.loc[need_mask, col] = prefix + seqs.astype(str).str.zfill(width)

        df_in_AllocPurSum[W_ORDER_TYPE_COLUMN] = 'ALLOC_PUR'
        print_df(df_in_AllocPurSum, 'STEP4 by 1-2.1  ____ df_in_AllocPurSum .... OrderlineID create')
        step('=====> STEP4 by 1-2 End')





        # -------------------- df_output_distorder
        step('=====> STEP4 by 2-1 Start : df_in_MtrlSupplyPlan 에 Activity 컬럼 및 W WIP Pegging ID, W WIP Propagation Upstream Consumption 컬럼 추가')
        df_in_AllocPur[ACTIVITY1_COLUMN] = (
                df_in_AllocPur[LOCATION_COLUMN] + '_' +
                df_in_AllocPur[SUB_LOCATION_COLUMN] + '_' +
                df_in_AllocPur[TRANS_MODE_COLUMN]
        )
        df_in_AllocPur[ACTIVITY2_COLUMN] = df_in_AllocPur[TRANS_MODE_COLUMN]
        df_in_AllocPur[ACTIVITY3_COLUMN] = df_in_AllocPur[ITEM_METERIAL_COLUMN]

        df_in_AllocPur[W_WIP_PEGGING_ID_COLUMN] = 2
        df_in_AllocPur[W_WIP_PROPAGATION_UPSTREAM_CONSUMPTION_COLUMN] = 'Constrained_Unconstrained'
        df_in_AllocPur[W_WIP_METERIAL_PRODUCTION_QUANTITY_COLUMN] = df_in_AllocPur[ALLOC_PUR_ETD_PLAN_COLUMN]
        print_df(df_in_AllocPur, 'STEP4 by 2-1.1  ____ df_in_AllocPur .... column add')
        step('=====> STEP4 by 2-1 End')


        step('=====> STEP4 by 2-2 Start : Documents.[OrderlineID] 생성')
        col = DOCUMENTS_ORDERLINEID_COLUMN
        prefix = "INV_"
        width = 10

        # 컬럼이 없으면 생성(전부 NA로)
        if col not in df_in_AllocPur.columns:
            df_in_AllocPur[col] = pd.NA

        # 1) 기존 SUI_########## 형태에서 숫자만 뽑아 MAX 계산 (기존 값 유지 대상 포함)
        existing = df_in_AllocPur[col].dropna().astype(str)

        sui_nums = (
            existing[existing.str.startswith(prefix)]
            .str.slice(len(prefix), len(prefix) + width)
            .where(lambda s: s.str.fullmatch(r"\d+"))  # prefix 뒤가 숫자일 때만
            .dropna()
            .astype(int)
        )

        start_seq = (int(sui_nums.max()) + 1) if not sui_nums.empty else 1

        # 2) 채번이 필요한 행(NA 또는 공백)만 골라서 채움
        s = df_in_AllocPur[col].astype("string")  # NA-safe 문자열
        need_mask = s.isna() | (s.str.strip() == "")

        k = int(need_mask.sum())
        seqs = pd.RangeIndex(start_seq, start_seq + k)

        df_in_AllocPur.loc[need_mask, col] = prefix + seqs.astype(str).str.zfill(width)
        print_df(df_in_AllocPur, 'STEP4 by 3.1  ____ df_in_AllocPur .... OrderlineID create')
        step('=====> STEP4 by 2-2 End')


        step('=====> STEP4 by 2-3 Start : Sub Location.[Sub Location]을 Location.[Location]으로 row 를 추가 구성 및 W WIP Material Consumption Quantity, W WIP Material Production Quantity 필드 추가')
        # 기존 행을 복제
        new_rows = df_in_AllocPur.copy()

        # 새로 추가될 행에 대한 컬럼 설정
        new_rows[LOCATION_COLUMN] = 'EVER@CN'
        new_rows[W_WIP_PROPAGATION_UPSTREAM_CONSUMPTION_COLUMN] = None
        new_rows[W_WIP_METERIAL_CONSUMPTIONN_QUANTITY_COLUMN] = new_rows[ALLOC_PUR_ETD_PLAN_COLUMN]

        # 데이터프레임 합치기
        df_distorder = pd.concat([df_in_AllocPur, new_rows], ignore_index=True)
        print_df(df_distorder, 'STEP4 by 2-3.1  ____ df_distorder .... create')
        step('=====> STEP4 by 2-3 End')


        step('=====> STEP4 by 2-4 Start : output 구성')
        # 불필요컬럼 삭제
        df_distorder.drop(columns=[
            SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            ALLOC_PUR_ETD_PLAN_COLUMN, ALLOC_PUR_ETD_PLAN_FLAG_COLUMN, ALLOC_PUR_ETD_PLAN_LT_COLUMN
        ], inplace=True)

        df_distorder.rename(columns={
            ITEM_METERIAL_COLUMN: ITEM_COLUMN,
        }, inplace=True)

        df_distorder[W_WIP_TYPE_COLUMN] = 'ALLOC_PUR'
        print_df(df_distorder, 'STEP4 by 2-4.1  ____ df_distorder .... recreate')
        step('=====> STEP4 by 2-4 End')





        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_output_intransit = rename_and_delete_df(df_in_AllocPurSum)
        df_output_intransit[VERSION_NAME_COLUMN] = paramOutVersion
        df_output_intransit = df_output_intransit[fn_intransit_columns]
        df_output_intransit = df_output_intransit.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        df_output_distorder = rename_and_delete_df(df_distorder)
        df_output_distorder[VERSION_NAME_COLUMN] = paramOutVersion
        df_output_distorder = df_output_distorder[fn_solver_inputs_wip_columns]
        df_output_distorder = df_output_distorder.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_output_intransit': df_output_intransit,
            'df_output_distorder': df_output_distorder,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_output_intransit = pd.DataFrame(columns=fn_intransit_columns)
        df_output_distorder = pd.DataFrame(columns=fn_solver_inputs_wip_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_output_intransit = pd.DataFrame(columns=fn_intransit_columns)
        df_output_distorder = pd.DataFrame(columns=fn_solver_inputs_wip_columns)
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
