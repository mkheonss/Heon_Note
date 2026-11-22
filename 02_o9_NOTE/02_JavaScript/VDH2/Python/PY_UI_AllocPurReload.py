"""
* 프로그램명
    - PY_UI_AllocPurReload

* 내용
    - Alloc Pur 화면에서 Reload 버튼 클릭 시 변경된 SOP W를 참조하여 SOP_Fixed, SOP_UnFixed 수량 재계산.

* 변경이력
    - 2026.04.16 / 조재연 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_SOPW            : Select ([Location].[Location] * [To Item].[To Item] * [Item].[Item] * [To Location].[To Location] * [Time].[Week] * [Sequence].[Sequence] * [To Time].[To Week] * [Item Material].[Item Material] * [Item Component].[Item Component] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] * [Week1].[Week1] * [Week2].[Week2] * [To Trans Mode].[To Trans Mode] * [BOM Info].[BOM Version] ) on row, ({Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_SET MFG Qty]}) on column where {[Version].[Version Name]};
    - df_in_FullBOM_Fixed   : Select ( [Location].[Location] * [To Item].[To Item] * [Item].[Item] * [To Location].[To Location] * [Item Material].[Item Material] * [BOM Status].[BOM Status].[Fixed] * [BOM Type].[BOM Type] * [BOM Info].[BOM Version] * [Status].[Status] ) on row, ({Measure.[Full BOM_Base Qty]}) on column where {[Version].[Version Name], [Item Material].[MSL1].[Panel]};
    - df_in_FullBOM_UnFixed : Select ( [Location].[Location] * [To Item].[To Item] * [Item].[Item] * [To Location].[To Location] * [Item Material].[Item Material] * [BOM Status].[BOM Status].filter(~(#.Name in {"MPI_L", "Fixed"})) * [BOM Type].[BOM Type] * [BOM Info].[BOM Version] * [Status].[Status] ) on row, ({Measure.[Full BOM_Base Qty]}) on column where {[Version].[Version Name], [Item Material].[MSL1].[Panel]};

* Flow Summary
    - STEP1. SOP W의 SET MFG Qty 계산
    - STEP2. SOP W의 LCM MFG Qty 계산
    - STEP3. Full BOM과 병합하여 SOP Fixed Qty, SOP UnFixed Qty 계산

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_AllocPur

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_AllocPurReload] for measures {[Alloc Pur_SOP Fix]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] ) on row, ({Measure.[Alloc Pur_SOP Fix], Measure.[Alloc Pur_SOP unFix]}) on column;

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
str_instance = 'PY_UI_AllocPurReload'
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


def get_next_week(df, time_column, base_week, offset_weeks=4):
    if time_column not in df.columns:
        raise ValueError(f"컬럼이 없습니다: {time_column}")

    # time 컬럼과 base_week 모두 '정수'로 강제
    s = pd.to_numeric(df[time_column], errors="coerce")
    if s.isna().any():
        bad = df.loc[s.isna(), time_column].head(5).tolist()
        raise ValueError(f"{time_column}에 숫자로 바꿀 수 없는 값이 있습니다. 예: {bad}")

    base_week = int(base_week)

    # 주차 기준 정렬 후, 위치 기반으로 이동
    tmp = df.copy()
    tmp[time_column] = s.astype(int)
    tmp = tmp.sort_values(time_column).reset_index(drop=True)

    matches = tmp.index[tmp[time_column] == base_week].tolist()
    if not matches:
        raise ValueError(f"타겟 주({base_week})가 데이터프레임에 존재하지 않습니다.")

    start_pos = matches[0]
    target_pos = start_pos + int(offset_weeks)

    if target_pos >= len(tmp):
        raise IndexError(
            f"요청한 offset({offset_weeks})가 범위를 벗어났습니다. "
            f"start_pos={start_pos}, len={len(tmp)}"
        )

    return int(tmp.loc[target_pos, time_column])


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
            df_in_SOPW = read_csv_file("df_in_SOPW")
            df_in_FullBOM_Fixed = read_csv_file("df_in_FullBOM_Fixed")
            df_in_FullBOM_UnFixed = read_csv_file("df_in_FullBOM_UnFixed")


        dataframes = {
            'df_in_SOPW': df_in_SOPW,
            'df_in_FullBOM_Fixed': df_in_FullBOM_Fixed,
            'df_in_FullBOM_UnFixed': df_in_FullBOM_UnFixed
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
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_MATERIAL_COLUMN = 'Item Material.[Item Material]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'

        TO_ITEM_COLUMN = 'To Item.[To Item]'
        ITEM_COLUMN = 'Item.[Item]'
        TO_LOCATION_COLUMN = 'To Location.[To Location]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'

        BOM_STATUS_COLUMN = 'BOM Status.[BOM Status]'
        BOM_TYPE_COLUMN = 'BOM Type.[BOM Type]'
        STATUS_COLUMN = 'Status.[Status]'

        ALLOC_PUR_SOP_FIX_COLUMN = 'Alloc Pur_SOP Fix'
        ALLOC_PUR_SOP_UNFIX_COLUMN = 'Alloc Pur_SOP unFix'

        SOP_W_LCM_MFG_QTY_COLUMN = 'SOP W_LCM MFG Qty'
        SOP_W_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'

        FULL_BOM_BASE_QTY_COLUMN = 'Full BOM_Base Qty'

        version_columns = [VERSION_NAME_COLUMN]

        alloc_pur_columns = [
            LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_MATERIAL_COLUMN, TRANS_MODE_COLUMN, SUB_LOCATION_COLUMN,
            ALLOC_PUR_SOP_FIX_COLUMN, ALLOC_PUR_SOP_UNFIX_COLUMN
        ]

        fn_alloc_pur_columns = version_columns + alloc_pur_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_SOPW.empty & df_in_FullBOM_Fixed.empty & df_in_FullBOM_UnFixed.empty:
            raise CustomException("STEP3 by 0 ____ df_in_SOPW, df_in_FullBOM_Fixed, df_in_FullBOM_UnFixed 값이 없습니다.")

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_SETSOP 구성')
        df_SETSOP = df_in_SOPW.copy()

        groupby_columns = [LOCATION_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, TIME_WEEK_COLUMN]

        sum_columns = [SOP_W_SET_MFG_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_SETSOP = df_SETSOP.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        print_df(df_SETSOP, 'STEP4 by 1  ____ df_SETSOP .... groupby', True)
        step('=====> STEP4 by 1 End')


        step('=====> STEP4 by 2 Start : df_LCMSOP 구성')
        df_LCMSOP = df_in_SOPW.copy()
        df_LCMSOP[SUB_LOCATION_COLUMN] = df_LCMSOP[SUB_LOCATION_COLUMN].str.replace('LCD$','',regex=True)

        groupby_columns = [SUB_LOCATION_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, WEEK1_COLUMN]

        sum_columns = [SOP_W_LCM_MFG_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_LCMSOP = df_LCMSOP.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        print_df(df_LCMSOP, 'STEP4 by 2  ____ df_LCMSOP .... groupby', True)
        step('=====> STEP4 by 2 End')


        step('=====> STEP4 by 3 Start : Full BOM 병합')
        df_SETSOP_Fixed = df_SETSOP.merge(
            df_in_FullBOM_Fixed[
                [LOCATION_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_MATERIAL_COLUMN, FULL_BOM_BASE_QTY_COLUMN]],
            how='inner',
            left_on=[LOCATION_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN],
            right_on=[LOCATION_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        )

        df_SETSOP_Fixed[SOP_W_SET_MFG_QTY_COLUMN] = df_SETSOP_Fixed[SOP_W_SET_MFG_QTY_COLUMN].fillna(0).astype('float64')
        df_SETSOP_Fixed[FULL_BOM_BASE_QTY_COLUMN] = df_SETSOP_Fixed[FULL_BOM_BASE_QTY_COLUMN].fillna(0).astype('float64')

        df_SETSOP_Fixed[ALLOC_PUR_SOP_FIX_COLUMN] = df_SETSOP_Fixed[SOP_W_SET_MFG_QTY_COLUMN] * df_SETSOP_Fixed[FULL_BOM_BASE_QTY_COLUMN]

        print_df(df_SETSOP_Fixed, 'STEP4 by 3.1  ____ df_SETSOP .... FullBOM_Fixed Merge', True)


        df_SETSOP_UnFixed = df_SETSOP.merge(
            df_in_FullBOM_UnFixed[
                [LOCATION_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_MATERIAL_COLUMN, FULL_BOM_BASE_QTY_COLUMN]],
            how='inner',
            left_on=[LOCATION_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN],
            right_on=[LOCATION_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        )

        df_SETSOP_UnFixed[SOP_W_SET_MFG_QTY_COLUMN] = df_SETSOP_UnFixed[SOP_W_SET_MFG_QTY_COLUMN].fillna(0).astype('float64')
        df_SETSOP_UnFixed[FULL_BOM_BASE_QTY_COLUMN] = df_SETSOP_UnFixed[FULL_BOM_BASE_QTY_COLUMN].fillna(0).astype('float64')

        df_SETSOP_UnFixed[ALLOC_PUR_SOP_UNFIX_COLUMN] = df_SETSOP_UnFixed[SOP_W_SET_MFG_QTY_COLUMN] * df_SETSOP_UnFixed[FULL_BOM_BASE_QTY_COLUMN]

        print_df(df_SETSOP_UnFixed, 'STEP4 by 3.2  ____ df_SETSOP .... FullBOM_UnFixed Merge', True)


        df_in_FullBOM_Fixed[TO_LOCATION_COLUMN] = df_in_FullBOM_Fixed[TO_LOCATION_COLUMN].str.replace('LCD$', '', regex=True)
        df_LCMSOP_Fixed = df_LCMSOP.merge(
            df_in_FullBOM_Fixed[
                [TO_LOCATION_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_MATERIAL_COLUMN, FULL_BOM_BASE_QTY_COLUMN]],
            how='inner',
            left_on=[SUB_LOCATION_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN],
            right_on=[TO_LOCATION_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        )

        df_LCMSOP_Fixed[SOP_W_LCM_MFG_QTY_COLUMN] = df_LCMSOP_Fixed[SOP_W_LCM_MFG_QTY_COLUMN].fillna(0).astype('float64')
        df_LCMSOP_Fixed[FULL_BOM_BASE_QTY_COLUMN] = df_LCMSOP_Fixed[FULL_BOM_BASE_QTY_COLUMN].fillna(0).astype('float64')

        df_LCMSOP_Fixed[ALLOC_PUR_SOP_FIX_COLUMN] = df_LCMSOP_Fixed[SOP_W_LCM_MFG_QTY_COLUMN] * df_LCMSOP_Fixed[FULL_BOM_BASE_QTY_COLUMN]
        df_LCMSOP_Fixed.rename(columns={
            SUB_LOCATION_COLUMN: LOCATION_COLUMN,
            WEEK1_COLUMN: TIME_WEEK_COLUMN
        }, inplace=True)

        print_df(df_LCMSOP_Fixed, 'STEP4 by 3.3  ____ df_LCMSOP .... FullBOM_Fixed Merge', True)


        df_in_FullBOM_UnFixed[TO_LOCATION_COLUMN] = df_in_FullBOM_UnFixed[TO_LOCATION_COLUMN].str.replace('LCD$', '', regex=True)
        df_LCMSOP_UnFixed = df_LCMSOP.merge(
            df_in_FullBOM_UnFixed[
                [TO_LOCATION_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_MATERIAL_COLUMN, FULL_BOM_BASE_QTY_COLUMN]],
            how='inner',
            left_on=[SUB_LOCATION_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN],
            right_on=[TO_LOCATION_COLUMN, ITEM_COLUMN, TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        )

        df_LCMSOP_UnFixed[SOP_W_LCM_MFG_QTY_COLUMN] = df_LCMSOP_UnFixed[SOP_W_LCM_MFG_QTY_COLUMN].fillna(0).astype('float64')
        df_LCMSOP_UnFixed[FULL_BOM_BASE_QTY_COLUMN] = df_LCMSOP_UnFixed[FULL_BOM_BASE_QTY_COLUMN].fillna(0).astype('float64')

        df_LCMSOP_UnFixed[ALLOC_PUR_SOP_FIX_COLUMN] = df_LCMSOP_UnFixed[SOP_W_LCM_MFG_QTY_COLUMN] * df_LCMSOP_UnFixed[FULL_BOM_BASE_QTY_COLUMN]
        df_LCMSOP_UnFixed.rename(columns={
            SUB_LOCATION_COLUMN: LOCATION_COLUMN,
            WEEK1_COLUMN: TIME_WEEK_COLUMN
        }, inplace=True)

        print_df(df_LCMSOP_UnFixed, 'STEP4 by 3.4  ____ df_LCMSOP .... FullBOM_UnFixed Merge', True)

        step('=====> STEP4 by 3 End')


        step('=====> STEP4 by 4 Start : SETSOP Concatenation')

        df_AllocPur = pd.concat(
            [df_SETSOP_Fixed, df_SETSOP_UnFixed, df_LCMSOP_Fixed, df_LCMSOP_UnFixed],
            ignore_index=True
        )

        df_AllocPur[SUB_LOCATION_COLUMN] = "-"
        df_AllocPur[TRANS_MODE_COLUMN] = "-"
        df_AllocPur[ALLOC_PUR_SOP_FIX_COLUMN] = df_AllocPur[ALLOC_PUR_SOP_FIX_COLUMN].fillna(0).astype('float64')
        df_AllocPur[ALLOC_PUR_SOP_UNFIX_COLUMN] = df_AllocPur[ALLOC_PUR_SOP_UNFIX_COLUMN].fillna(0).astype('float64')

        print_df(df_AllocPur, 'STEP4 by 4  ____ df_AllocPur .... Concate', True)

        step('=====> STEP4 by 4 End')

        step('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_AllocPur = rename_and_delete_df(df_AllocPur)
        df_out_AllocPur[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AllocPur = df_out_AllocPur[fn_alloc_pur_columns]
        df_out_AllocPur = df_out_AllocPur.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_AllocPur': df_out_AllocPur
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_AllocPur = pd.DataFrame(columns=fn_alloc_pur_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_AllocPur = pd.DataFrame(columns=fn_alloc_pur_columns)
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
