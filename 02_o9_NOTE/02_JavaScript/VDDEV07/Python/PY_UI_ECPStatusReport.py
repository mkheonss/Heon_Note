"""
* 프로그램명
    - PY_UI_ECPStatusReport

* 내용
    - ECPStructure을 가공해서 ECP Status Report를 만든다.

* 변경이력
    - 2026.02.24 / 조재연 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ECPStructureSETRTF   : Select ( [Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq].filter(#.Name in {"2", "5"}) ) on row, ({Measure.[ECP Structure_MFG Week], Measure.[ECP Structure_Demand Qty], Measure.[ECP Structure_Due Week], Measure.[ECP Structure_ECP Status], Measure.[ECP Structure_ETA Week], Measure.[ECP Structure_ETD Week], Measure.[ECP Structure_MFG Qty], Measure.[ECP Structure_DemandID], Measure.[ECP Structure_Base Qty] }) on column where {[Version].[Version Name], Measure.[ECP Structure_BOM Type] == "SET"};
    - df_in_ECPStructureLCMRTF   : Select ( [Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq].filter(#.Name in {"2", "5"}) ) on row, ({Measure.[ECP Structure_MFG Week], Measure.[ECP Structure_Demand Qty], Measure.[ECP Structure_Due Week], Measure.[ECP Structure_ECP Status], Measure.[ECP Structure_ETA Week], Measure.[ECP Structure_ETD Week], Measure.[ECP Structure_MFG Qty], Measure.[ECP Structure_DemandID], Measure.[ECP Structure_Base Qty] }) on column where {[Version].[Version Name], Measure.[ECP Structure_BOM Type] == "SOP Assy"};
    - df_in_ECPStructureSETShort : Select ( [Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq].filter(#.Name in {"1", "3", "4"}) ) on row, ({Measure.[ECP Structure_DP MFG Week], Measure.[ECP Structure_Demand Qty], Measure.[ECP Structure_Due Week], Measure.[ECP Structure_ECP Status], Measure.[ECP Structure_MFG Qty], Measure.[ECP Structure_DemandID], Measure.[ECP Structure_Base Qty] }) on column where {[Version].[Version Name], Measure.[ECP Structure_BOM Type] == "SET"};
    - df_in_ECPStructureLCMShort : Select ( [Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq].filter(#.Name in {"1", "3", "4"}) ) on row, ({Measure.[ECP Structure_DP MFG Week], Measure.[ECP Structure_Demand Qty], Measure.[ECP Structure_Due Week], Measure.[ECP Structure_ECP Status], Measure.[ECP Structure_MFG Qty], Measure.[ECP Structure_DemandID], Measure.[ECP Structure_Base Qty] }) on column where {[Version].[Version Name], Measure.[ECP Structure_BOM Type] == "SOP Assy"};

* Flow Summary
    -

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ECPStatusReport

* 데이타 초기화
    - DELETE DATA FOR MODEL [ECP Status Report] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ECPStatusReport] for measures {[ECP Status Report_ECP Status]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Seq].[Seq] * [BOM Info].[BOM Version] ) on row,
({Measure.[ECP Status Report_ECP Status], Measure.[ECP Status Report_ETA W], Measure.[ECP Status Report_ETD Qty], Measure.[ECP Status Report_ETD W], Measure.[ECP Status Report_Qty], Measure.[ECP Status Report_SOP W]}) on column;
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
str_instance = 'PY_UI_ECPStatusReport'
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
            df_in_ECPStructureSETRTF = read_csv_file("df_in_ECPStructureSETRTF")
            df_in_ECPStructureLCMRTF = read_csv_file("df_in_ECPStructureLCMRTF")
            df_in_ECPStructureSETShort = read_csv_file("df_in_ECPStructureSETShort")
            df_in_ECPStructureLCMShort = read_csv_file("df_in_ECPStructureLCMShort")


        dataframes = {
            'df_in_ECPStructureSETRTF': df_in_ECPStructureSETRTF,
            'df_in_ECPStructureLCMRTF': df_in_ECPStructureLCMRTF,
            'df_in_ECPStructureSETShort': df_in_ECPStructureSETShort,
            'df_in_ECPStructureLCMShort': df_in_ECPStructureLCMShort,
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
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SEQ_COLUMN = 'Seq.[Seq]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'

        ECP_STRUCTURE_MFG_WEEK_COLUMN = 'ECP Structure_MFG Week'
        ECP_STRUCTURE_DEMAND_QTY_COLUMN = 'ECP Structure_Demand Qty'
        ECP_STRUCTURE_DUE_WEEK_COLUMN = 'ECP Structure_Due Week'
        ECP_STRUCTURE_ECP_STATUS_COLUMN = 'ECP Structure_ECP Status'
        ECP_STRUCTURE_ETA_WEEK_COLUMN = 'ECP Structure_ETA Week'
        ECP_STRUCTURE_ETD_WEEK_COLUMN = 'ECP Structure_ETD Week'
        ECP_STRUCTURE_MFG_QTY_COLUMN = 'ECP Structure_MFG Qty'
        ECP_STRUCTURE_DEMAND_ID_COLUMN = 'ECP Structure_DemandID'
        ECP_STRUCTURE_BASE_QTY = 'ECP Structure_Base Qty'
        ECP_STRUCTURE_DP_MFG_WEEK_COLUMN = 'ECP Structure_DP MFG Week'

        ECP_STATUS_REPORT_ECP_STATUS_COLUMN = 'ECP Status Report_ECP Status'
        ECP_STATUS_REPORT_ETA_W_COLUMN = 'ECP Status Report_ETA W'
        ECP_STATUS_REPORT_ETD_QTY_COLUMN = 'ECP Status Report_ETD Qty'
        ECP_STATUS_REPORT_ETD_W_COLUMN = 'ECP Status Report_ETD W'
        ECP_STATUS_REPORT_QTY_COLUMN = 'ECP Status Report_Qty'
        ECP_STATUS_REPORT_SOP_W_COLUMN = 'ECP Status Report_SOP W'

        version_columns = [VERSION_NAME_COLUMN]

        key_columns = [
            LOCATION_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, SEQ_COLUMN,
        ]

        ecp_status_report_columns = [
            ECP_STATUS_REPORT_ECP_STATUS_COLUMN, ECP_STATUS_REPORT_ETA_W_COLUMN, ECP_STATUS_REPORT_ETD_QTY_COLUMN,
            ECP_STATUS_REPORT_ETD_W_COLUMN, ECP_STATUS_REPORT_QTY_COLUMN, ECP_STATUS_REPORT_SOP_W_COLUMN,
        ]

        fn_ecp_status_report_columns = version_columns + key_columns + ecp_status_report_columns

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
        # if df_in_ECPRequestList.empty & df_in_ECPSimulationPSI.empty :
        #     raise CustomException("STEP3 by 0 ____ df_in_ECPRequestList 와 df_in_ECPSimulationPSI 값이 없습니다.")


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_in_ECPStructureSETRTF, df_in_ECPStructureLCMRTF 의 필드명을 다음과 같이 수정한다.')
        # [ECP Structure_MFG Week]  →  [ECP Status Report_SOP W]
        # [ECP Structure_Demand Qty]  →  [ECP Status Report_Qty]
        # [ECP Structure_ETA Week]  →  [ECP Status Report_ETA W]
        # [ECP Structure_ETD Week]  →  [ECP Status Report_ETD W]
        # [ECP Structure_MFG Qty]  →  [ECP Status Report_ETD Qty]

        # df_in_ECPStructureSETRTF,    df_in_ECPStructureLCMRTF에 필드값이 [Seq].[Seq]인 필드를 다음과 같이 추가한다.
        #       [ECP Status Report_ECP Status]

        df_in_ECPStructureSETRTF.rename(columns={
            ECP_STRUCTURE_MFG_WEEK_COLUMN: ECP_STATUS_REPORT_SOP_W_COLUMN,
            ECP_STRUCTURE_DEMAND_QTY_COLUMN: ECP_STATUS_REPORT_QTY_COLUMN,
            ECP_STRUCTURE_ETA_WEEK_COLUMN: ECP_STATUS_REPORT_ETA_W_COLUMN,
            ECP_STRUCTURE_ETD_WEEK_COLUMN: ECP_STATUS_REPORT_ETD_W_COLUMN,
            ECP_STRUCTURE_MFG_QTY_COLUMN: ECP_STATUS_REPORT_ETD_QTY_COLUMN,
        }, inplace=True)
        print_df(df_in_ECPStructureSETRTF, 'STEP4 by 1.1.1  ____ df_in_ECPStructureSETRTF .... rename')

        df_in_ECPStructureSETRTF[ECP_STATUS_REPORT_ECP_STATUS_COLUMN] = df_in_ECPStructureSETRTF[SEQ_COLUMN]
        print_df(df_in_ECPStructureSETRTF, 'STEP4 by 1.1.2  ____ df_in_ECPStructureSETRTF .... add column')

        df_in_ECPStructureLCMRTF.rename(columns={
            ECP_STRUCTURE_MFG_WEEK_COLUMN: ECP_STATUS_REPORT_SOP_W_COLUMN,
            ECP_STRUCTURE_DEMAND_QTY_COLUMN: ECP_STATUS_REPORT_QTY_COLUMN,
            ECP_STRUCTURE_ETA_WEEK_COLUMN: ECP_STATUS_REPORT_ETA_W_COLUMN,
            ECP_STRUCTURE_ETD_WEEK_COLUMN: ECP_STATUS_REPORT_ETD_W_COLUMN,
            ECP_STRUCTURE_MFG_QTY_COLUMN: ECP_STATUS_REPORT_ETD_QTY_COLUMN,
        }, inplace=True)
        print_df(df_in_ECPStructureLCMRTF, 'STEP4 by 1.2.1  ____ df_in_ECPStructureLCMRTF .... rename')

        df_in_ECPStructureLCMRTF[ECP_STATUS_REPORT_ECP_STATUS_COLUMN] = df_in_ECPStructureLCMRTF[SEQ_COLUMN]
        print_df(df_in_ECPStructureLCMRTF, 'STEP4 by 1.2.2  ____ df_in_ECPStructureLCMRTF .... add column')

        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : df_in_ECPStructureSETShort, df_in_ECPStructureLCMShort 의 필드명을 다음과 같이 수정한다')
        # [ECP Structure_DP MFG Week]  →  [ECP Req List_SOP W]
        # [ECP Structure_Demand Qty]  →  [ECP Req List_Qty]
        # [ECP Structure_MFG Qty]  →  [ECP Req List_ETD Qty]

        # df_in_ECPStructureSETShort,    df_in_ECPStructureLCMShort에 필드값이 Null인 필드를 다음과 같이 추가한다
        #       [ECP Req List_ETA W], [ECP Req List_ETD W]

        # df_in_ECPStructureSETShort,    df_in_ECPStructureLCMShort에 필드값이 [Seq].[Seq]인 필드를 다음과 같이 추가한다.
        #       [ECP Status Report_ECP Status]

        df_in_ECPStructureSETShort.rename(columns={
            ECP_STRUCTURE_MFG_WEEK_COLUMN: ECP_STATUS_REPORT_SOP_W_COLUMN,
            ECP_STRUCTURE_DEMAND_QTY_COLUMN: ECP_STATUS_REPORT_QTY_COLUMN,
            ECP_STRUCTURE_MFG_QTY_COLUMN: ECP_STATUS_REPORT_ETD_QTY_COLUMN,
        }, inplace=True)
        print_df(df_in_ECPStructureSETShort, 'STEP4 by 2.1.1  ____ df_in_ECPStructureSETShort .... rename')

        df_in_ECPStructureSETShort[ECP_STATUS_REPORT_ETA_W_COLUMN] = None
        df_in_ECPStructureSETShort[ECP_STATUS_REPORT_ETD_W_COLUMN] = None
        df_in_ECPStructureSETShort[ECP_STATUS_REPORT_ECP_STATUS_COLUMN] = df_in_ECPStructureSETShort[SEQ_COLUMN]
        print_df(df_in_ECPStructureSETShort, 'STEP4 by 2.1.2  ____ df_in_ECPStructureSETShort .... add column')

        df_in_ECPStructureLCMShort.rename(columns={
            ECP_STRUCTURE_MFG_WEEK_COLUMN: ECP_STATUS_REPORT_SOP_W_COLUMN,
            ECP_STRUCTURE_DEMAND_QTY_COLUMN: ECP_STATUS_REPORT_QTY_COLUMN,
            ECP_STRUCTURE_MFG_QTY_COLUMN: ECP_STATUS_REPORT_ETD_QTY_COLUMN,
        }, inplace=True)
        print_df(df_in_ECPStructureLCMShort, 'STEP4 by 2.2.1  ____ df_in_ECPStructureLCMShort .... rename')

        df_in_ECPStructureLCMShort[ECP_STATUS_REPORT_ETA_W_COLUMN] = None
        df_in_ECPStructureLCMShort[ECP_STATUS_REPORT_ETD_W_COLUMN] = None
        df_in_ECPStructureLCMShort[ECP_STATUS_REPORT_ECP_STATUS_COLUMN] = df_in_ECPStructureLCMShort[SEQ_COLUMN]
        print_df(df_in_ECPStructureLCMShort, 'STEP4 by 2.2.2  ____ df_in_ECPStructureLCMShort .... add column')
        step('=====> STEP4 by 2 End')


        step('=====> STEP4 by 3 Start : df_in_ECPStructureSETRTF, df_in_ECPStructureLCMRTF, df_in_ECPStructureSETShort, df_in_ECPStructureLCMShort 를 concat하여 새로운 테이블을 만들고 이를 df_ECPStructure 이라고 한다.')
        df_ECPStructure = pd.concat(
            [df_in_ECPStructureSETRTF, df_in_ECPStructureLCMRTF, df_in_ECPStructureSETShort, df_in_ECPStructureLCMShort],
            ignore_index=True
        )
        print_df(df_ECPStructure, 'STEP4 by 3.1  ____ df_ECPStructure .... concat')

        # [Location].[Location]의 끝이 LCD면 LCD를 제거하고 저장한다.
        #       예를 들어 [Location].[Location] = 'P306LCD'이면, [Location].[Location] = 'P306'으로 저장한다.
        df_ECPStructure[LOCATION_COLUMN] = df_ECPStructure[LOCATION_COLUMN].str.replace('LCD$', '', regex=True)

        # [Location].[Location], [Item].[Item], [Item Material].[Item Material], [BOM Info].[BOM Version], [Seq].[Seq]에 따라 aggregation한다.
        #       [ECP Status Report_SOP W], [ECP Status Report_Qty], [ECP Status Report_ECP Status]는 max aggregation
        #       [ECP Status Report_ETA W], [ECP Status Report_ETD W]는 min aggregation  (null 제외)
        #       [ECP Status Report_ETD Qty]는 sum aggregation

        groupby_columns = [
            LOCATION_COLUMN, ITEM_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, SEQ_COLUMN,
        ]
        sum_columns = [ECP_STATUS_REPORT_ETD_QTY_COLUMN]
        max_columns = [ECP_STATUS_REPORT_SOP_W_COLUMN, ECP_STATUS_REPORT_QTY_COLUMN, ECP_STATUS_REPORT_ECP_STATUS_COLUMN]
        min_columns = [ECP_STATUS_REPORT_ETA_W_COLUMN, ECP_STATUS_REPORT_ETD_W_COLUMN]
        agg_dict = {col: 'max' for col in max_columns}
        agg_dict.update({col: 'sum' for col in sum_columns})
        agg_dict.update({col: 'min' for col in min_columns})
        df_ECPStructure = df_ECPStructure.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_ECPStructure, 'STEP4 by 3.2  ____ df_ECPStructure .... aggregation')
        step('=====> STEP4 by 3 End')


        step('=====> STEP4 by 4 Start : df_ECPStructure의 ECP_Status를 수정한다.')
        df_ECPStructure[ECP_STATUS_REPORT_ECP_STATUS_COLUMN] = np.where(
            df_ECPStructure[ECP_STATUS_REPORT_ECP_STATUS_COLUMN] == '1',
            '7', df_ECPStructure[ECP_STATUS_REPORT_ECP_STATUS_COLUMN]
        )

        print_df(df_ECPStructure, 'STEP4 by 4  ____ df_ECPStructure .... transform ECP_Status')
        step('=====> STEP4 by 4 End')

        step('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_ECPStatusReport = rename_and_delete_df(df_ECPStructure)
        df_out_ECPStatusReport[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ECPStatusReport = df_out_ECPStatusReport[fn_ecp_status_report_columns]
        df_out_ECPStatusReport = df_out_ECPStatusReport.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_ECPStatusReport': df_out_ECPStatusReport,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ECPStatusReport = pd.DataFrame(columns=fn_ecp_status_report_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ECPStatusReport = pd.DataFrame(columns=fn_ecp_status_report_columns)
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
