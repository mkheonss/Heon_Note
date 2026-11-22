"""
* 프로그램명
    - PY_UI_AddPanelGroupMaster

* 내용
    - Panel Dualized Group과 BOD All 데이터로 패널 확정구간 정보 구성

* 변경이력
    - 2026.01.08 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_DualMtrlAnlMst : Select ([Location].[Location] * [Group].[Group ID] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Category].[Category].[Local Group-Master] ) on row, ({Measure.[Dual Mtrl Anl Mst_Asn], Measure.[Dual Mtrl Anl Mst_Flag], Measure.[Dual Mtrl Anl Mst_LCM Item]}) on column WHERE {[Version].[Version Name], Measure.[Dual Mtrl Anl Mst_Flag]==true};
    - df_in_OCell_O      : Select ([Location].[Location] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[BOD All_LCM Code], Measure.[BOD All_LCM Site], Measure.[BOD All_LCM Ship LT], Measure.[BOD All_LCM BOD LT], Measure.[BOD All_LCM Total LT], Measure.[BOD All_OCell Code], Measure.[BOD All_OCell BOD LT], Measure.[BOD All_OCell Site], Measure.[BOD All_OCell Ship LT], Measure.[BOD All_OCell Total LT], Measure.[BOD All_SET Site]}) on column where {[Version].[Version Name], (~isnull(Measure.[BOD All_OCell Code]) && ~isnull(Measure.[BOD All_LCM Code])) };
    - df_in_OCell_P      : Select ([Location].[Location] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[BOD All_LCM Code], Measure.[BOD All_LCM Site], Measure.[BOD All_LCM Ship LT], Measure.[BOD All_LCM BOD LT], Measure.[BOD All_LCM Total LT], Measure.[BOD All_OCell Code], Measure.[BOD All_OCell BOD LT], Measure.[BOD All_OCell Site], Measure.[BOD All_OCell Ship LT], Measure.[BOD All_OCell Total LT], Measure.[BOD All_SET Site]}) on column where {[Version].[Version Name], (~isnull(Measure.[BOD All_OCell Code]) && isnull(Measure.[BOD All_LCM Code]))};
    - df_in_LCM          : Select ([Location].[Location] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[BOD All_SET Site], Measure.[BOD All_LCM Code], Measure.[BOD All_OCell Code], Measure.[BOD All_LCM Site], Measure.[BOD All_OCell Site], Measure.[BOD All_LCM Total LT], Measure.[BOD All_LCM BOD LT], Measure.[BOD All_LCM Ship LT], Measure.[BOD All_OCell Total LT], Measure.[BOD All_OCell BOD LT], Measure.[BOD All_OCell Ship LT]}) on column WHERE {[Version].[Version Name], ~isnull(Measure.[BOD All_LCM Code])};
    - df_in_POPW         : Select ([Version].[Version Name]) on row, ({Measure.[Add Panel Master_POP Week]}) on column;

* Flow Summary
    - STEP1.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_AddPanelGroupMaster
    - df_out_AddPanelGroupSGSTMaster

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_AddPanelGroupMaster] for measures {[Add Panel Grp Mst_POP W]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [To Location].[To Location] * [Group].[Group ID] ) on row,
        ({Measure.[Add Panel Grp Mst_Created by], Measure.[Add Panel Grp Mst_Creation time], Measure.[Add Panel Grp Mst_POP W], Measure.[Add Panel Grp Mst_Sum LT], Measure.[Add Panel Grp Mst_Total LT], Measure.[Add Panel Grp Mst_Update time], Measure.[Add Panel Grp Mst_Updated by]}) on column limit 10;

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
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_AddPanelGroupMaster'
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
            df_in_DualMtrlAnlMst = read_csv_file("df_in_DualMtrlAnlMst")
            df_in_OCell_O = read_csv_file("df_in_OCell_O")
            df_in_OCell_P = read_csv_file("df_in_OCell_P")
            df_in_LCM = read_csv_file("df_in_LCM")
            df_in_POPW = read_csv_file("df_in_POPW")

        dataframes = {
            'df_in_DualMtrlAnlMst': df_in_DualMtrlAnlMst,
            'df_in_OCell_O': df_in_OCell_O,
            'df_in_OCell_P': df_in_OCell_P,
            'df_in_LCM': df_in_LCM,
            'df_in_POPW': df_in_POPW,
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
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'
        ITEM_COLUMN = 'Item.[Item]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        CATEGORY_COLUMN = 'Category.[Category]'
        TO_LOCATION_COLUMN = 'To Location.[To Location]'

        DUAL_MTRL_ANL_MST_ASN_COLUMN = 'Dual Mtrl Anl Mst_Asn'
        DUAL_MTRL_ANL_MST_FLAG_COLUMN = 'Dual Mtrl Anl Mst_Flag'
        DUAL_MTRL_ANL_MST_LCM_ITEM_COLUMN = 'Dual Mtrl Anl Mst_LCM Item'

        ADD_PANEL_MASTER_POP_W_COLUMN = 'Add Panel Master_POP Week'

        BOD_ALL_LCM_BOD_LT_COLUMN = 'BOD All_LCM BOD LT'
        BOD_ALL_LCM_SHIP_LT_COLUMN = 'BOD All_LCM Ship LT'
        BOD_ALL_LCM_CODE_COLUMN = 'BOD All_LCM Code'
        BOD_ALL_LCM_SITE_COLUMN = 'BOD All_LCM Site'
        BOD_ALL_LCM_TOTAL_LT_COLUMN = 'BOD All_LCM Total LT'

        BOD_ALL_OCELL_BOD_LT_COLUMN = 'BOD All_OCell BOD LT'
        BOD_ALL_OCELL_SHIP_LT_COLUMN = 'BOD All_OCell Ship LT'
        BOD_ALL_OCELL_CODE_COLUMN = 'BOD All_OCell Code'
        BOD_ALL_OCELL_SITE_COLUMN = 'BOD All_OCell Site'
        BOD_ALL_OCELL_TOTAL_LT_COLUMN = 'BOD All_OCell Total LT'

        BOD_ALL_SET_SITE_COLUMN = 'BOD All_SET Site'

        ADD_PANEL_GRP_MST_CREATED_BY_COLUMN = 'Add Panel Grp Mst_Created by'
        ADD_PANEL_GRP_MST_CREATION_TIME_COLUMN = 'Add Panel Grp Mst_Creation time'
        ADD_PANEL_GRP_MST_UPDATE_TIME_COLUMN = 'Add Panel Grp Mst_Update time'
        ADD_PANEL_GRP_MST_UPDATED_BY_COLUMN = 'Add Panel Grp Mst_Updated by'
        ADD_PANEL_GRP_MST_POP_W_COLUMN = 'Add Panel Grp Mst_POP W'
        ADD_PANEL_GRP_MST_SUM_LT_COLUMN = 'Add Panel Grp Mst_Sum LT'
        ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN = 'Add Panel Grp Mst_Total LT'
        ADD_PANEL_GRP_MST_MTRL_LT_COLUMN = 'Add Panel Grp Mst_Mtrl LT'
        ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN = 'Add Panel Grp Mst_Mtrl Total LT'

        ADD_PANEL_SGST_MST_MTRL_TOTAL_LT_COLUMN = 'Add Panel Sgst Mst_Mtrl Total LT'
        ADD_PANEL_SGST_MST_SET_TOTAL_LT_COLUMN = 'Add Panel Sgst Mst_SET Total LT'
        ADD_PANEL_SGST_MST_MIN_MAX_FLAG_COLUMN = 'Add Panel Sgst Mst_Min Max Flag'
        ADD_PANEL_SGST_MST_VALID_FLAG_COLUMN = 'Add Panel Sgst Mst_Valid Flag'

        version_columns = [VERSION_NAME_COLUMN]

        key_columns = [LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_COLUMN, SUB_LOCATION_COLUMN, GROUP_ID_COLUMN]

        sub_add_panel_gp_mst_columns = [
            LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TO_LOCATION_COLUMN, GROUP_ID_COLUMN,
            ADD_PANEL_GRP_MST_POP_W_COLUMN, ADD_PANEL_GRP_MST_SUM_LT_COLUMN,
            ADD_PANEL_GRP_MST_MTRL_LT_COLUMN, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN, ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN,
        ]

        add_panel_gp_mst_columns = [
            ADD_PANEL_GRP_MST_POP_W_COLUMN, ADD_PANEL_GRP_MST_SUM_LT_COLUMN,
            ADD_PANEL_GRP_MST_MTRL_LT_COLUMN, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN, ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN,
            ADD_PANEL_GRP_MST_CREATED_BY_COLUMN, ADD_PANEL_GRP_MST_CREATION_TIME_COLUMN,
            ADD_PANEL_GRP_MST_UPDATE_TIME_COLUMN, ADD_PANEL_GRP_MST_UPDATED_BY_COLUMN,
        ]

        add_panel_sgst_mst_columns = [
            LOCATION_COLUMN, GROUP_ID_COLUMN,
            ADD_PANEL_SGST_MST_MTRL_TOTAL_LT_COLUMN, ADD_PANEL_SGST_MST_SET_TOTAL_LT_COLUMN,
            ADD_PANEL_SGST_MST_MIN_MAX_FLAG_COLUMN, ADD_PANEL_SGST_MST_VALID_FLAG_COLUMN,
        ]

        fn_add_panel_gp_mst_columns = version_columns + key_columns + add_panel_gp_mst_columns
        fn_add_panel_sgst_mst_columns = version_columns + add_panel_sgst_mst_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start

        # df_in_OCell_O = df_in_OCell_O[
        #     (df_in_OCell_O[ITEM_COLUMN] == 'HG55BU800EUXXU') &
        #     (df_in_OCell_O[BOD_ALL_OCELL_SITE_COLUMN] == 'G1630961') &
        #     (df_in_OCell_O[BOD_ALL_SET_SITE_COLUMN] == 'P401') &
        #     (df_in_OCell_O[LOCATION_COLUMN] == 'L401') &
        #     (df_in_OCell_O[BOD_ALL_OCELL_CODE_COLUMN] == 'BN96-51801A')
        # ]
        # print_df(df_in_OCell_O, 'STEP3 by 0 ____ df_in_OCell_O', True)
        # df_in_OCell_P = df_in_OCell_P[
        #     (df_in_OCell_P[ITEM_COLUMN] == 'HG55BU800EUXXU') &
        #     (df_in_OCell_P[BOD_ALL_OCELL_SITE_COLUMN] == 'G1630961') &
        #     (df_in_OCell_P[BOD_ALL_SET_SITE_COLUMN] == 'P401')
        # ]
        # df_in_LCM = df_in_LCM[
        #     (df_in_LCM[ITEM_COLUMN] == 'HG55BU800EUXXU') &
        #     (df_in_LCM[BOD_ALL_LCM_CODE_COLUMN] == 'BN95-12016A')
        # ]
        # print_df(df_in_LCM, 'STEP3 by 0 ____ df_in_LCM', True)
        # df_in_DualMtrlAnlMst = df_in_DualMtrlAnlMst[
        #     (df_in_DualMtrlAnlMst[ITEM_COLUMN] == 'HG55BU800EUXXU') &
        #     (df_in_DualMtrlAnlMst[GROUP_ID_COLUMN] == 'LPanel0000001')
        # ]

        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_DualMtrlAnlMst.empty :
            raise CustomException("STEP3 by 0 ____ df_in_DualMtrlAnlMst 값이 없습니다.")


        # df_in_DualMtrlAnlMst 가공
        df_in_DualMtrlAnlMst = df_in_DualMtrlAnlMst[[
            LOCATION_COLUMN, GROUP_ID_COLUMN, ITEM_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN,
            DUAL_MTRL_ANL_MST_LCM_ITEM_COLUMN,
        ]].drop_duplicates()
        print_df(df_in_DualMtrlAnlMst, 'STEP3 by 1.1  ____ df_in_DualMtrlAnlMst .... drop_duplicates')


        # df_in_OCell_O 가공
        df_in_OCell_O = df_in_OCell_O.drop(columns=[SEQUENCE_COLUMN], errors='ignore')
        groupby_columns = [
            LOCATION_COLUMN, ITEM_COLUMN, BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN,
            BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_OCELL_SITE_COLUMN, BOD_ALL_SET_SITE_COLUMN,
        ]
        max_columns = [
            BOD_ALL_LCM_TOTAL_LT_COLUMN, BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN,
            BOD_ALL_OCELL_TOTAL_LT_COLUMN, BOD_ALL_OCELL_BOD_LT_COLUMN, BOD_ALL_OCELL_SHIP_LT_COLUMN,
        ]
        agg_dict = {col: 'max' for col in max_columns}
        df_in_OCell_O = df_in_OCell_O.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_in_OCell_O, 'STEP3 by 1.2  ____ df_in_OCell_O .... drop_duplicates')

        columns_to_fill = [
            BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN,
            BOD_ALL_OCELL_BOD_LT_COLUMN, BOD_ALL_OCELL_SHIP_LT_COLUMN,
        ]
        df_in_OCell_O[columns_to_fill] = df_in_OCell_O[columns_to_fill].fillna(0)


        # df_in_OCell_P 가공
        df_in_OCell_P = df_in_OCell_P.drop(columns=[SEQUENCE_COLUMN], errors='ignore')
        groupby_columns = [
            LOCATION_COLUMN, ITEM_COLUMN, BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_SET_SITE_COLUMN,
        ]
        max_columns = [
            BOD_ALL_LCM_TOTAL_LT_COLUMN, BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN,
            BOD_ALL_OCELL_TOTAL_LT_COLUMN, BOD_ALL_OCELL_BOD_LT_COLUMN, BOD_ALL_OCELL_SHIP_LT_COLUMN,
        ]
        agg_dict = {col: 'max' for col in max_columns}
        df_in_OCell_P = df_in_OCell_P.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_in_OCell_P, 'STEP3 by 1.2.1  ____ df_in_OCell_P .... drop_duplicates')

        columns_to_fill = [
            BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN,
            BOD_ALL_OCELL_BOD_LT_COLUMN, BOD_ALL_OCELL_SHIP_LT_COLUMN,
        ]
        df_in_OCell_P[columns_to_fill] = df_in_OCell_P[columns_to_fill].fillna(0)

        columns_to_none = [
            BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN, BOD_ALL_OCELL_SITE_COLUMN
        ]
        df_in_OCell_P[columns_to_none] = None
        print_df(df_in_OCell_P, 'STEP3 by 1.2.2  ____ df_in_OCell_P .... columns_to_none')


        # df_in_LCM 가공
        df_in_LCM = df_in_LCM.drop(columns=[SEQUENCE_COLUMN], errors='ignore')
        groupby_columns = [
            LOCATION_COLUMN, ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN,
            BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_OCELL_SITE_COLUMN,
        ]
        max_columns = [
            BOD_ALL_LCM_TOTAL_LT_COLUMN, BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN,
            BOD_ALL_OCELL_TOTAL_LT_COLUMN, BOD_ALL_OCELL_BOD_LT_COLUMN, BOD_ALL_OCELL_SHIP_LT_COLUMN,
        ]
        agg_dict = {col: 'max' for col in max_columns}
        df_in_LCM = df_in_LCM.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_in_LCM, 'STEP3 by 1.3  ____ df_in_LCM .... drop_duplicates')

        columns_to_fill = [BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN]
        df_in_LCM[columns_to_fill] = df_in_LCM[columns_to_fill].fillna(0)


        # df_in_POPW 가공
        df_in_POPW = df_in_POPW[[ADD_PANEL_MASTER_POP_W_COLUMN]].drop_duplicates()
        if df_in_POPW.empty:
            # 비어있을 때 새로운 행과 함께 컬럼 추가
            df_in_POPW = pd.DataFrame({ADD_PANEL_MASTER_POP_W_COLUMN: [3]})
        else:
            # 기존 데이터가 있다면 모든 행에 3을 할당
            df_in_POPW[ADD_PANEL_MASTER_POP_W_COLUMN] = df_in_POPW[ADD_PANEL_MASTER_POP_W_COLUMN].fillna(3)

        print_df(df_in_POPW, 'STEP3 by 1.4  ____ df_in_POPW .... drop_duplicates')


        current_date = get_current_date_str()          # 로컬 기준
        # current_date_utc = get_current_date_str("UTC") # UTC 기준
        step(f'=====> current_date : {current_date}')

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_in_OCell 와 df_in_DualMtrlAnlMst 을 Merge 한다')
        # 1. OCell
        df_in_OCell_1 = df_in_OCell_O.merge(
            df_in_DualMtrlAnlMst, how='inner',
            left_on=[ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN],
        ).merge(
            df_in_POPW, how='cross'
        )
        print_df(df_in_OCell_1, 'STEP4 by 1.1.1  ____ df_in_OCell_1 .... merge')

        df_in_OCell_1.drop(columns=[
            LOCATION_COLUMN+'_x', ITEM_COLUMN,
            BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_SET_SITE_COLUMN,
        ], inplace=True)
        df_in_OCell_1.rename(columns={
            LOCATION_COLUMN+'_y': LOCATION_COLUMN,
            ADD_PANEL_MASTER_POP_W_COLUMN: ADD_PANEL_GRP_MST_POP_W_COLUMN,
        }, inplace=True)

        df_in_OCell_1.loc[:, ADD_PANEL_GRP_MST_MTRL_LT_COLUMN] = (
                (
                    df_in_OCell_1[BOD_ALL_OCELL_BOD_LT_COLUMN] +
                    df_in_OCell_1[BOD_ALL_OCELL_SHIP_LT_COLUMN]
                ) / 7
        )

        df_in_OCell_1.loc[:, ADD_PANEL_GRP_MST_SUM_LT_COLUMN] = (
                (
                    df_in_OCell_1[BOD_ALL_OCELL_BOD_LT_COLUMN] +
                    df_in_OCell_1[BOD_ALL_OCELL_SHIP_LT_COLUMN] +
                    df_in_OCell_1[BOD_ALL_LCM_BOD_LT_COLUMN] +
                    df_in_OCell_1[BOD_ALL_LCM_SHIP_LT_COLUMN]
                ) / 7
        )

        df_in_OCell_1.loc[:, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN] = (
                df_in_OCell_1[ADD_PANEL_GRP_MST_SUM_LT_COLUMN] +
                df_in_OCell_1[ADD_PANEL_GRP_MST_POP_W_COLUMN]
        )

        df_in_OCell_1.loc[:, ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN] = (
                df_in_OCell_1[ADD_PANEL_GRP_MST_MTRL_LT_COLUMN] +
                df_in_OCell_1[ADD_PANEL_GRP_MST_POP_W_COLUMN]
        )

        df_in_OCell_1.loc[:, TO_LOCATION_COLUMN] = df_in_OCell_1[BOD_ALL_OCELL_SITE_COLUMN]
        df_in_OCell_1 = df_in_OCell_1.drop_duplicates()
        print_df(df_in_OCell_1, 'STEP4 by 1.1.2  ____ df_in_OCell_1 .... LT set')



        # 2. 완 Panel
        df_in_OCell_2 = df_in_OCell_P.merge(
            df_in_DualMtrlAnlMst, how='inner',
            left_on=[ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, BOD_ALL_OCELL_CODE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN],
        ).merge(
            df_in_POPW, how='cross'
        )
        print_df(df_in_OCell_2, 'STEP4 by 1.2.1  ____ df_in_OCell_2 .... merge')

        df_in_OCell_2.drop(columns=[
            LOCATION_COLUMN+'_x', ITEM_COLUMN,
            BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_SET_SITE_COLUMN,
        ], inplace=True)
        df_in_OCell_2.rename(columns={
            LOCATION_COLUMN+'_y': LOCATION_COLUMN,
            ADD_PANEL_MASTER_POP_W_COLUMN: ADD_PANEL_GRP_MST_POP_W_COLUMN,
        }, inplace=True)

        df_in_OCell_2.loc[:, ADD_PANEL_GRP_MST_MTRL_LT_COLUMN] = (
                (
                    df_in_OCell_2[BOD_ALL_OCELL_BOD_LT_COLUMN] +
                    df_in_OCell_2[BOD_ALL_OCELL_SHIP_LT_COLUMN]
                ) / 7
        )

        df_in_OCell_2.loc[:, ADD_PANEL_GRP_MST_SUM_LT_COLUMN] = (
                (
                    df_in_OCell_2[BOD_ALL_OCELL_BOD_LT_COLUMN] +
                    df_in_OCell_2[BOD_ALL_OCELL_SHIP_LT_COLUMN]
                ) / 7
        )

        df_in_OCell_2.loc[:, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN] = (
                df_in_OCell_2[ADD_PANEL_GRP_MST_SUM_LT_COLUMN] +
                df_in_OCell_2[ADD_PANEL_GRP_MST_POP_W_COLUMN]
        )

        df_in_OCell_2.loc[:, ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN] = (
                df_in_OCell_2[ADD_PANEL_GRP_MST_MTRL_LT_COLUMN] +
                df_in_OCell_2[ADD_PANEL_GRP_MST_POP_W_COLUMN]
        )

        df_in_OCell_2.loc[:, TO_LOCATION_COLUMN] = (
            df_in_OCell_2[BOD_ALL_OCELL_SITE_COLUMN]
            .fillna('-')
            .astype(str)
            .str.strip()
            .replace('', '-')
        )
        df_in_OCell_2 = df_in_OCell_2.drop_duplicates()
        print_df(df_in_OCell_2, 'STEP4 by 1.2.2  ____ df_in_OCell_2 .... LT set')


        # Ocell + 완패널 합치기
        df_in_OCell = pd.concat([df_in_OCell_1, df_in_OCell_2], ignore_index=True).drop_duplicates()
        print_df(df_in_OCell, 'STEP4 by 1.2.3  ____ df_in_OCell .... concat')

        df_in_OCell = df_in_OCell[sub_add_panel_gp_mst_columns].drop_duplicates()
        print_df(df_in_OCell, 'STEP4 by 1.2.4  ____ df_in_OCell .... columns select')


        step('=====> STEP4 by 1 End')




        step('=====> STEP4 by 2 Start : df_in_LCM 과 df_in_DualMtrlAnlMst 을 Merge 한다')
        df_in_LCM = df_in_LCM.merge(
            df_in_DualMtrlAnlMst, how='inner',
            left_on=[ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN, DUAL_MTRL_ANL_MST_LCM_ITEM_COLUMN, SUB_LOCATION_COLUMN],
        ).merge(
            df_in_POPW, how='cross'
        )
        print_df(df_in_LCM, 'STEP4 by 2.1  ____ df_in_LCM .... merge')

        df_in_LCM.drop(columns=[
            LOCATION_COLUMN+'_x', ITEM_COLUMN,
            BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_SET_SITE_COLUMN, ITEM_METERIAL_COLUMN,
        ], inplace=True)
        df_in_LCM.rename(columns={
            LOCATION_COLUMN+'_y': LOCATION_COLUMN,
            ADD_PANEL_MASTER_POP_W_COLUMN: ADD_PANEL_GRP_MST_POP_W_COLUMN,
            DUAL_MTRL_ANL_MST_LCM_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
        }, inplace=True)
        print_df(df_in_LCM, 'STEP4 by 2.2  ____ df_in_LCM .... rename')

        df_in_LCM.loc[:, ADD_PANEL_GRP_MST_MTRL_LT_COLUMN] = (
                (
                    df_in_LCM[BOD_ALL_OCELL_BOD_LT_COLUMN] +
                    df_in_LCM[BOD_ALL_OCELL_SHIP_LT_COLUMN]
                ) / 7
        )

        df_in_LCM.loc[:, ADD_PANEL_GRP_MST_SUM_LT_COLUMN] = (
                (
                    df_in_LCM[BOD_ALL_OCELL_BOD_LT_COLUMN] +
                    df_in_LCM[BOD_ALL_OCELL_SHIP_LT_COLUMN] +
                    df_in_LCM[BOD_ALL_LCM_BOD_LT_COLUMN] +
                    df_in_LCM[BOD_ALL_LCM_SHIP_LT_COLUMN]
                ) / 7
        )

        df_in_LCM.loc[:, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN] = (
                df_in_LCM[ADD_PANEL_GRP_MST_SUM_LT_COLUMN] +
                df_in_LCM[ADD_PANEL_GRP_MST_POP_W_COLUMN]
        )

        df_in_LCM.loc[:, ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN] = (
                df_in_LCM[ADD_PANEL_GRP_MST_MTRL_LT_COLUMN] +
                df_in_LCM[ADD_PANEL_GRP_MST_POP_W_COLUMN]
        )

        df_in_LCM.loc[:, TO_LOCATION_COLUMN] = df_in_LCM[BOD_ALL_OCELL_SITE_COLUMN]
        df_in_LCM = df_in_LCM.drop_duplicates()
        print_df(df_in_LCM, 'STEP4 by 2.3  ____ df_in_LCM .... LT set')

        df_in_LCM = df_in_LCM[sub_add_panel_gp_mst_columns].drop_duplicates()
        print_df(df_in_LCM, 'STEP4 by 2.4  ____ df_in_LCM .... columns select')

        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : df_in_OCell, df_in_LCM 를 합친다.')
        df_AddPanelGroupMaster = pd.concat([df_in_OCell, df_in_LCM], ignore_index=True)
        df_AddPanelGroupMaster.rename(columns={ITEM_METERIAL_COLUMN: ITEM_COLUMN}, inplace=True)
        df_AddPanelGroupMaster = df_AddPanelGroupMaster.drop_duplicates()
        print_df(df_AddPanelGroupMaster, 'STEP4 by 3.1  ____ df_AddPanelGroupMaster .... concat')

        columns = [
            ADD_PANEL_GRP_MST_SUM_LT_COLUMN, ADD_PANEL_GRP_MST_MTRL_LT_COLUMN, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN,
            ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN,
        ]
        df_AddPanelGroupMaster[columns] = df_AddPanelGroupMaster[columns].round(0).astype(int)


        groupby_columns = [
            LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TO_LOCATION_COLUMN, GROUP_ID_COLUMN,
        ]
        max_columns = [
            ADD_PANEL_GRP_MST_POP_W_COLUMN, ADD_PANEL_GRP_MST_SUM_LT_COLUMN, ADD_PANEL_GRP_MST_MTRL_LT_COLUMN,
            ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN, ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN,
        ]
        agg_dict = {col: 'max' for col in max_columns}
        df_AddPanelGroupMaster = df_AddPanelGroupMaster.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_AddPanelGroupMaster, 'STEP4 by 3.2  ____ df_AddPanelGroupMaster .... groupby', True)

        step('=====> STEP4 by 3 End')




        step('=====> STEP4 by 4 Start : ADD Pannel Sgst Mst 생성')

        df_AddPanelGroupSGSTMaster = df_AddPanelGroupMaster[[
            LOCATION_COLUMN, GROUP_ID_COLUMN, ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN,
        ]].copy()
        print_df(df_AddPanelGroupSGSTMaster, 'STEP4 by 4.1  ____ df_AddPanelGroupSGSTMaster .... copy')

        groupby_columns = [LOCATION_COLUMN, GROUP_ID_COLUMN]
        max_columns = [ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN, ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN]
        agg_dict = {col: 'max' for col in max_columns}
        df_AddPanelGroupSGSTMaster = df_AddPanelGroupSGSTMaster.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_AddPanelGroupSGSTMaster, 'STEP4 by 4.2  ____ df_AddPanelGroupSGSTMaster .... agg')

        # fn_add_panel_sgst_mst_columns
        df_AddPanelGroupSGSTMaster[ADD_PANEL_SGST_MST_MIN_MAX_FLAG_COLUMN] = "MAX"
        df_AddPanelGroupSGSTMaster[ADD_PANEL_SGST_MST_VALID_FLAG_COLUMN] = "N"

        df_AddPanelGroupSGSTMaster.rename(columns={
            ADD_PANEL_GRP_MST_MTRL_TOTAL_LT_COLUMN: ADD_PANEL_SGST_MST_MTRL_TOTAL_LT_COLUMN,
            ADD_PANEL_GRP_MST_TOTAL_LT_COLUMN: ADD_PANEL_SGST_MST_SET_TOTAL_LT_COLUMN,
        }, inplace=True)

        columns = [
            ADD_PANEL_SGST_MST_MTRL_TOTAL_LT_COLUMN, ADD_PANEL_SGST_MST_SET_TOTAL_LT_COLUMN,
        ]
        df_AddPanelGroupSGSTMaster[columns] = df_AddPanelGroupSGSTMaster[columns].round(0).astype(int)
        print_df(df_AddPanelGroupSGSTMaster, 'STEP4 by 4.3  ____ df_AddPanelGroupSGSTMaster .... rename')

        step('=====> STEP4 by 4 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_AddPanelGroupMaster = rename_and_delete_df(df_AddPanelGroupMaster)

        df_out_AddPanelGroupMaster[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AddPanelGroupMaster[ADD_PANEL_GRP_MST_CREATED_BY_COLUMN] = 'PY_UI_AddPanelGroupMaster'
        df_out_AddPanelGroupMaster[ADD_PANEL_GRP_MST_CREATION_TIME_COLUMN] = current_date
        df_out_AddPanelGroupMaster[ADD_PANEL_GRP_MST_UPDATED_BY_COLUMN] = 'PY_UI_AddPanelGroupMaster'
        df_out_AddPanelGroupMaster[ADD_PANEL_GRP_MST_UPDATE_TIME_COLUMN] = current_date
        df_out_AddPanelGroupMaster = df_out_AddPanelGroupMaster[fn_add_panel_gp_mst_columns]
        df_out_AddPanelGroupMaster = ultra_fast_replace_to_none(df_out_AddPanelGroupMaster)

        df_out_AddPanelGroupSGSTMaster = rename_and_delete_df(df_AddPanelGroupSGSTMaster)
        df_out_AddPanelGroupSGSTMaster[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_AddPanelGroupSGSTMaster = df_out_AddPanelGroupSGSTMaster[fn_add_panel_sgst_mst_columns]
        df_out_AddPanelGroupSGSTMaster = ultra_fast_replace_to_none(df_out_AddPanelGroupSGSTMaster)

        dataframes = {
            'df_out_AddPanelGroupMaster': df_out_AddPanelGroupMaster,
            'df_out_AddPanelGroupSGSTMaster': df_out_AddPanelGroupSGSTMaster,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_AddPanelGroupMaster = pd.DataFrame(columns=fn_add_panel_gp_mst_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_AddPanelGroupMaster = pd.DataFrame(columns=fn_add_panel_gp_mst_columns)
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
