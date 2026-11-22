"""
* 프로그램명
    - PY_UI_ECPSimulationPSI

* 내용
    - Mtrl_PSI 데이터에 GroupID를 추가하여 ECP Simulation PSI W를 구성한다.

* 변경이력
    - 2025.12.22 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_MtrlPSI                 : Select ([Location].[Location] *  &MDMHorizon * [Item Material].[Item Material] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location]) on row, ({Measure.[Mtrl PSI_ARRIVAL_CMI], Measure.[Mtrl PSI_ARRIVAL_Excel], Measure.[Mtrl PSI_ARRIVAL_Global RTF], Measure.[Mtrl PSI_ARRIVAL_Open PO], Measure.[Mtrl PSI_ARRIVAL_RTF], Measure.[Mtrl PSI_ARRIVAL_RTP], Measure.[Mtrl PSI_ARRIVAL_SN], Measure.[Mtrl PSI_ARRIVAL_Supply Plan], Measure.[Mtrl PSI_ARRIVAL_Total], Measure.[Mtrl PSI_REQ_SOP Status]}) on column where {[Version].[Version Name]};
    - df_in_ECPRequestList          : Select ([Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq]) on row, ({Measure.[ECP Req List_Base Qty] }) on column where {[Version].[Version Name]};
    - df_in_MtrlPSI_Sub             : Select ([Location].[Location] * [Item Material].[Item Material] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location] ) on row, ({Measure.[Mtrl PSI Sub_LT], Measure.[Mtrl PSI Sub_MOQ], Measure.[Mtrl PSI Sub_Roudning Value], Measure.[Mtrl PSI Sub_SS Time], Measure.[Mtrl PSI Sub_Supply LT], Measure.[Mtrl PSI Sub_Transit Time]}) on column where {[Version].[Version Name]};
    - df_in_DualMtrl                : Select ([Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID]) on row, ({Measure.[Dual Mtrl Anl Mst_Flag] }) on column where {[Version].[Version Name], [Category].[Category].[Dualized Mtrl Group-Master], Measure.[Dual Mtrl Anl Mst_Flag] == TRUE};
    - df_in_MtrlPSI_EOH             : Select ([Location].[Location] * &CurrentWeek * [Item Material].[Item Material] * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location]) on row, ({ Measure.[Mtrl PSI_EOH_SOP] }) on column where {[Version].[Version Name]};
    - df_in_ECPRequestList_AirECP   : Select ([Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [To Location].[To Location] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq].filter(#.Name in {"1", "2"})) on row, ({Measure.[ECP Req List_ETD Qty], Measure.[ECP Req List_SOP W]}) on column where {[Version].[Version Name]};
    - df_in_ECPRequestList_ECP      : Select ([Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [To Location].[To Location] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq].filter(#.Name in {"5"})) on row, ({Measure.[ECP Req List_ETD Qty], Measure.[ECP Req List_SOP W]}) on column where {[Version].[Version Name]};
    - df_in_MDMHorizon              : Select (&MDMHorizon) on row, () on column;

* Flow Summary
    - STEP1. ECP Request List 가공 후 Group ID Merge.
    - STEP2. ECP Request List에 Mtrl PSI Merge.
    - STEP3. ECP Request List에 Mtrl PSI Sub Merge
    - STEP4. ECP Request List에 EOH, BOH 계산

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ECP_PSI

* 데이타 초기화
    - DELETE DATA FOR MODEL [ECP Simulation PSI W] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ECPSimulationPSI] for measures {[ECP Simulation PSI W_Arrival_CMI]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select ([Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Time].[Week] * [Item Material].[Item Material] * [BOM Info].[BOM Version] ) on row,
    ({Measure.[ECP Simulation PSI W_AR Type], Measure.[ECP Simulation PSI W_Air LT], Measure.[ECP Simulation PSI W_Arrival_CMI], Measure.[ECP Simulation PSI W_Arrival_Excel], Measure.[ECP Simulation PSI W_Arrival_Global RTF], Measure.[ECP Simulation PSI W_Arrival_Open PO], Measure.[ECP Simulation PSI W_Arrival_RTF], Measure.[ECP Simulation PSI W_Arrival_RTP], Measure.[ECP Simulation PSI W_Arrival_SN], Measure.[ECP Simulation PSI W_Arrival_Supply Plan], Measure.[ECP Simulation PSI W_Arrival_Total], Measure.[ECP Simulation PSI W_BOH], Measure.[ECP Simulation PSI W_BOH_SOP ECP], Measure.[ECP Simulation PSI W_BOH_SOP+Air+Norm], Measure.[ECP Simulation PSI W_Base Qty], Measure.[ECP Simulation PSI W_EOH_SOP+Air], Measure.[ECP Simulation PSI W_EOH_SOP+Air+Norm], Measure.[ECP Simulation PSI W_EOH_SOP_Arrival Total], Measure.[ECP Simulation PSI W_EOH_Stock Level], Measure.[ECP Simulation PSI W_LT], Measure.[ECP Simulation PSI W_MOQ], Measure.[ECP Simulation PSI W_REQ_Air ECP], Measure.[ECP Simulation PSI W_REQ_ECP], Measure.[ECP Simulation PSI W_REQ_SOP], Measure.[ECP Simulation PSI W_Rounding Value], Measure.[ECP Simulation PSI W_Safety Time], Measure.[ECP Simulation PSI W_Ship LT], Measure.[ECP Simulation PSI W_Transit LT]}) on column;
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
str_instance = 'PY_UI_ECPSimulationPSI'
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
            df_in_MtrlPSI = read_csv_file("df_in_MtrlPSI")
            df_in_ECPRequestList = read_csv_file("df_in_ECPRequestList")
            df_in_MtrlPSI_Sub = read_csv_file("df_in_MtrlPSI_Sub")
            df_in_DualMtrl = read_csv_file("df_in_DualMtrl")
            df_in_MtrlPSI_EOH = read_csv_file("df_in_MtrlPSI_EOH")
            df_in_ECPRequestList_AirECP = read_csv_file("df_in_ECPRequestList_AirECP")
            df_in_ECPRequestList_ECP = read_csv_file("df_in_ECPRequestList_ECP")
            df_in_MDMHorizon = read_csv_file("df_in_MDMHorizon")


        dataframes = {
            'df_in_MtrlPSI': df_in_MtrlPSI,
            'df_in_ECPRequestList': df_in_ECPRequestList,
            'df_in_MtrlPSI_Sub': df_in_MtrlPSI_Sub,
            'df_in_DualMtrl': df_in_DualMtrl,
            'df_in_MtrlPSI_EOH': df_in_MtrlPSI_EOH,
            'df_in_ECPRequestList_AirECP': df_in_ECPRequestList_AirECP,
            'df_in_ECPRequestList_ECP': df_in_ECPRequestList_ECP,
            'df_in_MDMHorizon': df_in_MDMHorizon
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
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'

        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        SEQ_COLUMN = 'Seq.[Seq]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'

        DUAL_MTRL_ANL_MST_FLAG_COLUMN = 'Dual Mtrl Anl Mst_Flag'
        ECP_REQ_LIST_ETD_QTY_COLUMN = 'ECP Req List_ETD Qty'
        ECP_REQ_LIST_BASE_QTY_COLUMN = 'ECP Req List_Base Qty'
        ECP_REQ_LIST_SOP_W_COLUMN = 'ECP Req List_SOP W'

        MTRL_PSI_ARRIVAL_CMI_COLUMN = 'Mtrl PSI_ARRIVAL_CMI'
        MTRL_PSI_ARRIVAL_EXCEL_COLUMN = 'Mtrl PSI_ARRIVAL_Excel'
        MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN = 'Mtrl PSI_ARRIVAL_Global RTF'
        MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN = 'Mtrl PSI_ARRIVAL_Open PO'
        MTRL_PSI_ARRIVAL_RTF_COLUMN = 'Mtrl PSI_ARRIVAL_RTF'
        MTRL_PSI_ARRIVAL_RTP_COLUMN = 'Mtrl PSI_ARRIVAL_RTP'
        MTRL_PSI_ARRIVAL_SN_COLUMN = 'Mtrl PSI_ARRIVAL_SN'
        MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN = 'Mtrl PSI_ARRIVAL_Supply Plan'
        MTRL_PSI_ARRIVAL_TOTAL_COLUMN = 'Mtrl PSI_ARRIVAL_Total'
        MTRL_PSI_REQ_SOP_STATUS_COLUMN = 'Mtrl PSI_REQ_SOP Status'
        MTRL_PSI_EOH_SOP_COLUMN = 'Mtrl PSI_EOH_SOP'

        MTRL_PSI_SUB_LT_COLUMN = 'Mtrl PSI Sub_LT'
        MTRL_PSI_SUB_SS_TIME_COLUMN = 'Mtrl PSI Sub_SS Time'
        MTRL_PSI_SUB_SUPPLY_LT_COLUMN = 'Mtrl PSI Sub_Supply LT'
        MTRL_PSI_SUB_TRANSIT_TIME_COLUMN = 'Mtrl PSI Sub_Transit Time'
        MTRL_PSI_SUB_MOQ_COLUMN = 'Mtrl PSI Sub_MOQ'
        MTRL_PSI_SUB_ROUNDING_VALUE_COLUMN = 'Mtrl PSI Sub_Roudning Value'

        ECP_SIMULATION_PSI_W_AR_TYPE_COLUMN = 'ECP Simulation PSI W_AR Type'
        ECP_SIMULATION_PSI_W_ARRIVAL_CMI_COLUMN = 'ECP Simulation PSI W_Arrival_CMI'
        ECP_SIMULATION_PSI_W_ARRIVAL_EXCEL_COLUMN = 'ECP Simulation PSI W_Arrival_Excel'
        ECP_SIMULATION_PSI_W_ARRIVAL_GLOBAL_RTF_COLUMN = 'ECP Simulation PSI W_Arrival_Global RTF'
        ECP_SIMULATION_PSI_W_ARRIVAL_OPEN_PO_COLUMN = 'ECP Simulation PSI W_Arrival_Open PO'
        ECP_SIMULATION_PSI_W_ARRIVAL_RTF_COLUMN = 'ECP Simulation PSI W_Arrival_RTF'
        ECP_SIMULATION_PSI_W_ARRIVAL_RTP_COLUMN = 'ECP Simulation PSI W_Arrival_RTP'
        ECP_SIMULATION_PSI_W_ARRIVAL_SN_COLUMN = 'ECP Simulation PSI W_Arrival_SN'
        ECP_SIMULATION_PSI_W_ARRIVAL_SUPPLY_PLAN_COLUMN = 'ECP Simulation PSI W_Arrival_Supply Plan'
        ECP_SIMULATION_PSI_W_ARRIVAL_TOTAL_COLUMN = 'ECP Simulation PSI W_Arrival_Total'
        ECP_SIMULATION_PSI_W_BOH_COLUMN = 'ECP Simulation PSI W_BOH'
        ECP_SIMULATION_PSI_W_BOH_SOP_ECP_COLUMN = 'ECP Simulation PSI W_BOH_SOP ECP'
        ECP_SIMULATION_PSI_W_BOH_SOP_AIR_NORM_COLUMN = 'ECP Simulation PSI W_BOH_SOP+Air+Norm'
        ECP_SIMULATION_PSI_W_BASE_QTY_COLUMN = 'ECP Simulation PSI W_Base Qty'
        ECP_SIMULATION_PSI_W_EOH_SOP_AIR_COLUMN = 'ECP Simulation PSI W_EOH_SOP+Air'
        ECP_SIMULATION_PSI_W_EOH_SOP_AIR_NORM_COLUMN = 'ECP Simulation PSI W_EOH_SOP+Air+Norm'
        ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN = 'ECP Simulation PSI W_EOH_SOP_Arrival Total'
        ECP_SIMULATION_PSI_W_EOH_STOCK_LEVEL_COLUMN = 'ECP Simulation PSI W_EOH_Stock Level'
        ECP_SIMULATION_PSI_W_LT_COLUMN = 'ECP Simulation PSI W_LT'
        ECP_SIMULATION_PSI_W_MOQ_COLUMN = 'ECP Simulation PSI W_MOQ'
        ECP_SIMULATION_PSI_W_REQ_AIR_ECP_COLUMN = 'ECP Simulation PSI W_REQ_Air ECP'
        ECP_SIMULATION_PSI_W_REQ_ECP_COLUMN = 'ECP Simulation PSI W_REQ_ECP'
        ECP_SIMULATION_PSI_W_REQ_SOP_COLUMN = 'ECP Simulation PSI W_REQ_SOP'
        ECP_SIMULATION_PSI_W_ROUNDING_VALUE_COLUMN = 'ECP Simulation PSI W_Rounding Value'
        ECP_SIMULATION_PSI_W_SAFETY_TIME_COLUMN = 'ECP Simulation PSI W_Safety Time'
        ECP_SIMULATION_PSI_W_SHIP_LT_COLUMN = 'ECP Simulation PSI W_Ship LT'
        ECP_SIMULATION_PSI_W_TRANSIT_LT_COLUMN = 'ECP Simulation PSI W_Transit LT'

        version_columns = [VERSION_NAME_COLUMN]

        key_columns = [LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN, GROUP_ID_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]

        ecp_psi_columns = [
            ECP_SIMULATION_PSI_W_AR_TYPE_COLUMN, ECP_SIMULATION_PSI_W_ARRIVAL_CMI_COLUMN,
            ECP_SIMULATION_PSI_W_ARRIVAL_EXCEL_COLUMN, ECP_SIMULATION_PSI_W_ARRIVAL_GLOBAL_RTF_COLUMN,
            ECP_SIMULATION_PSI_W_ARRIVAL_OPEN_PO_COLUMN, ECP_SIMULATION_PSI_W_ARRIVAL_RTF_COLUMN,
            ECP_SIMULATION_PSI_W_ARRIVAL_RTP_COLUMN, ECP_SIMULATION_PSI_W_ARRIVAL_SN_COLUMN,
            ECP_SIMULATION_PSI_W_ARRIVAL_SUPPLY_PLAN_COLUMN, ECP_SIMULATION_PSI_W_ARRIVAL_TOTAL_COLUMN,
            ECP_SIMULATION_PSI_W_BOH_COLUMN, ECP_SIMULATION_PSI_W_BOH_SOP_ECP_COLUMN,
            ECP_SIMULATION_PSI_W_BOH_SOP_AIR_NORM_COLUMN, ECP_SIMULATION_PSI_W_BASE_QTY_COLUMN,
            ECP_SIMULATION_PSI_W_EOH_SOP_AIR_COLUMN, ECP_SIMULATION_PSI_W_EOH_SOP_AIR_NORM_COLUMN,
            ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN, ECP_SIMULATION_PSI_W_EOH_STOCK_LEVEL_COLUMN,
            ECP_SIMULATION_PSI_W_LT_COLUMN, ECP_SIMULATION_PSI_W_MOQ_COLUMN, ECP_SIMULATION_PSI_W_REQ_AIR_ECP_COLUMN,
            ECP_SIMULATION_PSI_W_REQ_ECP_COLUMN, ECP_SIMULATION_PSI_W_REQ_SOP_COLUMN,
            ECP_SIMULATION_PSI_W_ROUNDING_VALUE_COLUMN, ECP_SIMULATION_PSI_W_SAFETY_TIME_COLUMN,
            ECP_SIMULATION_PSI_W_SHIP_LT_COLUMN, ECP_SIMULATION_PSI_W_TRANSIT_LT_COLUMN
        ]

        fn_ecp_psi_columns_columns = version_columns + key_columns + ecp_psi_columns

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
        # if df_in_MtrlPSI.empty & df_in_ECPRequestList.empty :
        #     raise CustomException("STEP3 by 0 ____ df_in_MtrlPSI 와 df_in_ECPRequestList 값이 없습니다.")


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_in_ECPRequestList을 Location, Item Material, Item, BOM Version 에 따라 ECP Req List_Base Qty를 sum aggregation')
        groupby_columns = [LOCATION_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        sum_columns = [ECP_REQ_LIST_BASE_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_ECPRequestList = df_in_ECPRequestList.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        print_df(df_in_ECPRequestList, 'STEP4 by 1  ____ df_in_ECPRequestList .... groupby')
        step('=====> STEP4 by 1 End')


        step('=====> STEP4 by 2 Start : df_in_ECPRequestList를 기준으로 Location, Item, Item Material 에 따라 df_in_DualMtrl의 Group ID을 Merge한다.')
        # df_in_ECPRequestList를 기준으로 Location, Item, Item Material에 따라 df_in_DualMtrl의 Group ID을 Merge한다.
        df_in_ECPRequestList = df_in_ECPRequestList.merge(
            df_in_DualMtrl[[LOCATION_COLUMN, ITEM_COLUMN, ITEM_METERIAL_COLUMN, GROUP_ID_COLUMN]],
            how='inner',
            on=[LOCATION_COLUMN, ITEM_COLUMN, ITEM_METERIAL_COLUMN]
        )

        print_df(df_in_ECPRequestList, 'STEP4 by 2  ____ df_in_ECPRequestList .... merge')
        step('=====> STEP4 by 2 End')


        step('=====> STEP4 by 3 Start : df_in_ECPRequestList를 기준으로 Location, Item, Group ID 에 따라 df_in_DualMtrl의 Item Material을 Merge한다.')
        # df_in_ECPRequestList를 기준으로 Location, Item, Group ID에 따라 df_in_DualMtrl의 Item Material을 Merge한다.
        df_in_ECPRequestList = df_in_ECPRequestList.merge(
            df_in_DualMtrl[[LOCATION_COLUMN, ITEM_COLUMN, ITEM_METERIAL_COLUMN, GROUP_ID_COLUMN]],
            how='inner',
            on=[LOCATION_COLUMN, ITEM_COLUMN, GROUP_ID_COLUMN]
        )

        df_in_ECPRequestList = df_in_ECPRequestList.drop(columns = [ITEM_METERIAL_COLUMN + '_x'])

        df_in_ECPRequestList.rename(columns={
            ITEM_METERIAL_COLUMN + '_y': ITEM_METERIAL_COLUMN
        }, inplace=True)

        print_df(df_in_ECPRequestList, 'STEP4 by 3  ____ df_in_ECPRequestList .... merge')
        step('=====> STEP4 by 3 End')


        step('=====> STEP4 by 4 Start : df_in_ECPRequestList을 기준으로 Item Material, Location, Week 에 따라 df_in_MtrlPSI을 Merge한다.')
        df_in_ECPRequestList = df_in_ECPRequestList.merge(df_in_MDMHorizon, how='cross')

        df_MtrlPSI = df_in_ECPRequestList.merge(
            df_in_MtrlPSI, how='left', on=[ITEM_METERIAL_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN]
        )

        print_df(df_MtrlPSI, 'STEP4 by 4  ____ df_MtrlPSI .... merge')
        step('=====> STEP4 by 4 End')


        step('=====> STEP4 by 5 Start : df_in_MtrlPSI를 Location, Item Material, Week, BOM Version, Group ID, Base Qty에 따라 sum aggregation한다.')
        groupby_columns = [LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TIME_WEEK_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
                           GROUP_ID_COLUMN, ECP_REQ_LIST_BASE_QTY_COLUMN]
        sum_columns = [MTRL_PSI_ARRIVAL_CMI_COLUMN, MTRL_PSI_ARRIVAL_EXCEL_COLUMN, MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN,
                       MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN, MTRL_PSI_ARRIVAL_RTF_COLUMN, MTRL_PSI_ARRIVAL_RTP_COLUMN, MTRL_PSI_ARRIVAL_SN_COLUMN,
                       MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN, MTRL_PSI_ARRIVAL_TOTAL_COLUMN, MTRL_PSI_REQ_SOP_STATUS_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_MtrlPSI = df_MtrlPSI.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        print_df(df_MtrlPSI, 'STEP4 by 5  ____ df_MtrlPSI .... groupby')
        step('=====> STEP4 by 5 End')


        step('=====> STEP4 by 6 Start : df_MtrlPSI의 필드명 수정 및 AR Type 필드에 SOP(Auto) 추가')
        df_MtrlPSI.rename(columns={
            ECP_REQ_LIST_BASE_QTY_COLUMN: ECP_SIMULATION_PSI_W_BASE_QTY_COLUMN,
            MTRL_PSI_ARRIVAL_CMI_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_CMI_COLUMN,
            MTRL_PSI_ARRIVAL_EXCEL_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_EXCEL_COLUMN,
            MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_GLOBAL_RTF_COLUMN,
            MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_OPEN_PO_COLUMN,
            MTRL_PSI_ARRIVAL_RTF_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_RTF_COLUMN,
            MTRL_PSI_ARRIVAL_RTP_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_RTP_COLUMN,
            MTRL_PSI_ARRIVAL_SN_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_SN_COLUMN,
            MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_SUPPLY_PLAN_COLUMN,
            MTRL_PSI_ARRIVAL_TOTAL_COLUMN: ECP_SIMULATION_PSI_W_ARRIVAL_TOTAL_COLUMN,
            MTRL_PSI_REQ_SOP_STATUS_COLUMN: ECP_SIMULATION_PSI_W_REQ_SOP_COLUMN
        }, inplace=True)

        df_MtrlPSI[ECP_SIMULATION_PSI_W_AR_TYPE_COLUMN] = "SOP (Auto)"

        print_df(df_MtrlPSI, 'STEP4 by 6  ____ df_MtrlPSI .... rename')
        step('=====> STEP4 by 6 End')


        step('=====> STEP4 by 7 Start : df_MtrlPSI을 기준으로 Location, Item Material에 따라 df_in_MtrlPSI_Sub을 Merge한다.')
        groupby_columns = [LOCATION_COLUMN, ITEM_METERIAL_COLUMN]
        sum_columns = [MTRL_PSI_SUB_LT_COLUMN, MTRL_PSI_SUB_SS_TIME_COLUMN, MTRL_PSI_SUB_SUPPLY_LT_COLUMN, MTRL_PSI_SUB_TRANSIT_TIME_COLUMN, MTRL_PSI_SUB_MOQ_COLUMN, MTRL_PSI_SUB_ROUNDING_VALUE_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_MtrlPSI_Sub = df_in_MtrlPSI_Sub.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        df_MtrlPSI = df_MtrlPSI.merge(
            df_in_MtrlPSI_Sub, how='left', on=[ITEM_METERIAL_COLUMN, LOCATION_COLUMN]
        )

        df_MtrlPSI.rename(columns={
            MTRL_PSI_SUB_LT_COLUMN: ECP_SIMULATION_PSI_W_LT_COLUMN,
            MTRL_PSI_SUB_SS_TIME_COLUMN: ECP_SIMULATION_PSI_W_SAFETY_TIME_COLUMN,
            MTRL_PSI_SUB_SUPPLY_LT_COLUMN: ECP_SIMULATION_PSI_W_SHIP_LT_COLUMN,
            MTRL_PSI_SUB_TRANSIT_TIME_COLUMN: ECP_SIMULATION_PSI_W_TRANSIT_LT_COLUMN,
            MTRL_PSI_SUB_MOQ_COLUMN: ECP_SIMULATION_PSI_W_MOQ_COLUMN,
            MTRL_PSI_SUB_ROUNDING_VALUE_COLUMN: ECP_SIMULATION_PSI_W_ROUNDING_VALUE_COLUMN
        }, inplace=True)

        print_df(df_MtrlPSI, 'STEP4 by 7  ____ df_MtrlPSI .... merge')
        step('=====> STEP4 by 7 End')


        step('=====> STEP4 by 8 Start : df_MtrlPSI을 기준으로 Location, Item Material, BOM Version에 따라 df_in_ECPRequestList_AirECP, df_in_ECPRequestList_ECP를 Merge한다.')
        groupby_columns = [LOCATION_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        sum_columns = [ECP_REQ_LIST_ETD_QTY_COLUMN]
        min_columns = [ECP_REQ_LIST_SOP_W_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        agg_dict.update({col: 'min' for col in min_columns})
        df_in_ECPRequestList_AirECP = df_in_ECPRequestList_AirECP.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)
        df_in_ECPRequestList_ECP = df_in_ECPRequestList_ECP.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        df_MtrlPSI = df_MtrlPSI.merge(
            df_in_ECPRequestList_AirECP, how='left',
            on=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        )

        df_MtrlPSI[ECP_SIMULATION_PSI_W_REQ_AIR_ECP_COLUMN] = np.where(
            df_MtrlPSI[TIME_WEEK_COLUMN] == df_MtrlPSI[ECP_REQ_LIST_SOP_W_COLUMN],
            df_MtrlPSI[ECP_REQ_LIST_ETD_QTY_COLUMN],
            0
        )

        df_MtrlPSI = df_MtrlPSI.drop(columns = [ECP_REQ_LIST_ETD_QTY_COLUMN, ECP_REQ_LIST_SOP_W_COLUMN])

        df_MtrlPSI = df_MtrlPSI.merge(
            df_in_ECPRequestList_ECP, how='left', on=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        )

        df_MtrlPSI[ECP_SIMULATION_PSI_W_REQ_ECP_COLUMN] = np.where(
            df_MtrlPSI[TIME_WEEK_COLUMN] == df_MtrlPSI[ECP_REQ_LIST_SOP_W_COLUMN],
            df_MtrlPSI[ECP_REQ_LIST_ETD_QTY_COLUMN],
            0
        )

        df_MtrlPSI = df_MtrlPSI.drop(columns = [ECP_REQ_LIST_ETD_QTY_COLUMN, ECP_REQ_LIST_SOP_W_COLUMN])

        print_df(df_MtrlPSI, 'STEP4 by 8  ____ df_MtrlPSI .... merge', True)
        step('=====> STEP4 by 8 End')


        step('=====> STEP4 by 9 Start : df_MtrlPSI을 기준으로 Location, Week, Item Material에 따라 df_in_MtrlPSI_EOH를 Merge한다.')
        groupby_columns = [LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TIME_WEEK_COLUMN]
        sum_columns = [MTRL_PSI_EOH_SOP_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_MtrlPSI_EOH = df_in_MtrlPSI_EOH.groupby(groupby_columns, sort=False, as_index=False, dropna=False).agg(agg_dict)

        df_MtrlPSI = df_MtrlPSI.merge(
            df_in_MtrlPSI_EOH, how='left', on=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TIME_WEEK_COLUMN]
        )

        df_MtrlPSI.rename(columns={MTRL_PSI_EOH_SOP_COLUMN: ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN}, inplace=True)

        df_MtrlPSI[ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN] = df_MtrlPSI[ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN].fillna(0).astype(float)
        df_MtrlPSI[ECP_SIMULATION_PSI_W_EOH_SOP_AIR_COLUMN] = df_MtrlPSI[ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN]
        df_MtrlPSI[ECP_SIMULATION_PSI_W_EOH_SOP_AIR_NORM_COLUMN] = df_MtrlPSI[ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN]

        print_df(df_MtrlPSI, 'STEP4 by 9  ____ df_MtrlPSI .... merge')
        step('=====> STEP4 by 9 End')


        step('=====> STEP4 by 10 Start : df_MtrlPSI의 EOH, BOH를 계산한다.')
        # 1. Location, Item Material, Week 기준으로 정렬
        # 2. BOH, EOH 계산
        # 3. Stock Level 계산
        cList_temp = [LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TIME_WEEK_COLUMN]

        df_MtrlPSI = df_MtrlPSI.sort_values(by=cList_temp, ascending=[True, True, True]).reset_index(drop=True)

        CurrentWeek = df_in_MDMHorizon.iloc[0][TIME_WEEK_COLUMN]
        LastWeek = df_in_MDMHorizon.iloc[-9][TIME_WEEK_COLUMN]

        for idx, row in df_MtrlPSI.iterrows():
            Week = row[TIME_WEEK_COLUMN]

            if Week != CurrentWeek:
                df_MtrlPSI.loc[idx, ECP_SIMULATION_PSI_W_BOH_COLUMN] = df_MtrlPSI.iloc[idx-1][ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN]
                df_MtrlPSI.loc[idx, ECP_SIMULATION_PSI_W_BOH_SOP_ECP_COLUMN] = df_MtrlPSI.iloc[idx - 1][ECP_SIMULATION_PSI_W_EOH_SOP_AIR_COLUMN]
                df_MtrlPSI.loc[idx, ECP_SIMULATION_PSI_W_BOH_SOP_AIR_NORM_COLUMN] = df_MtrlPSI.iloc[idx - 1][ECP_SIMULATION_PSI_W_EOH_SOP_AIR_NORM_COLUMN]

                df_MtrlPSI.loc[idx, ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN] = (df_MtrlPSI.iloc[idx][ECP_SIMULATION_PSI_W_BOH_COLUMN]
                                                                                          + row[ECP_SIMULATION_PSI_W_ARRIVAL_TOTAL_COLUMN]
                                                                                          - row[ECP_SIMULATION_PSI_W_REQ_SOP_COLUMN])
                df_MtrlPSI.loc[idx, ECP_SIMULATION_PSI_W_EOH_SOP_AIR_COLUMN] = (df_MtrlPSI.iloc[idx][ECP_SIMULATION_PSI_W_BOH_SOP_ECP_COLUMN]
                                                                                + row[ECP_SIMULATION_PSI_W_ARRIVAL_TOTAL_COLUMN]
                                                                                - row[ECP_SIMULATION_PSI_W_REQ_SOP_COLUMN]
                                                                                - row[ECP_SIMULATION_PSI_W_REQ_AIR_ECP_COLUMN])
                df_MtrlPSI.loc[idx, ECP_SIMULATION_PSI_W_EOH_SOP_AIR_NORM_COLUMN] = (df_MtrlPSI.iloc[idx][ECP_SIMULATION_PSI_W_BOH_SOP_AIR_NORM_COLUMN]
                                                                                     + row[ECP_SIMULATION_PSI_W_ARRIVAL_TOTAL_COLUMN]
                                                                                     - row[ECP_SIMULATION_PSI_W_REQ_SOP_COLUMN]
                                                                                     - row[ECP_SIMULATION_PSI_W_REQ_AIR_ECP_COLUMN]
                                                                                     - row[ECP_SIMULATION_PSI_W_REQ_ECP_COLUMN])
            if Week <= LastWeek:
                Total_REQ = 0
                for i in range(8):
                    Total_REQ = Total_REQ + df_MtrlPSI.iloc[idx + i + 1][ECP_SIMULATION_PSI_W_REQ_SOP_COLUMN]
                    Total_REQ = Total_REQ + df_MtrlPSI.iloc[idx + i + 1][ECP_SIMULATION_PSI_W_REQ_AIR_ECP_COLUMN]
                    Total_REQ = Total_REQ + df_MtrlPSI.iloc[idx + i + 1][ECP_SIMULATION_PSI_W_REQ_ECP_COLUMN]

                df_MtrlPSI.loc[idx, ECP_SIMULATION_PSI_W_EOH_STOCK_LEVEL_COLUMN] = np.where(Total_REQ <= 0.1, 0,
                                                                                        round(df_MtrlPSI.iloc[idx][ECP_SIMULATION_PSI_W_EOH_SOP_ARRIVAL_TOTAL_COLUMN] * 8 / Total_REQ, 1))


        print_df(df_MtrlPSI, 'STEP4 by 10  ____ df_MtrlPSI .... Compute EOH, BOH')

        step('=====> STEP4 by 10 End')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_ECP_PSI = rename_and_delete_df(df_MtrlPSI)
        if df_out_ECP_PSI is None:
            df_out_ECP_PSI = pd.DataFrame(columns=fn_ecp_psi_columns_columns)

        df_out_ECP_PSI[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ECP_PSI = df_out_ECP_PSI[fn_ecp_psi_columns_columns]
        df_out_ECP_PSI = df_out_ECP_PSI.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_ECP_PSI': df_out_ECP_PSI
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ECP_PSI = pd.DataFrame(columns=fn_ecp_psi_columns_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ECP_PSI = pd.DataFrame(columns=fn_ecp_psi_columns_columns)
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
