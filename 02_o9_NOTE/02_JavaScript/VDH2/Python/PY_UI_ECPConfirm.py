"""
* 프로그램명
    - PY_UI_ECPConfirm

* 내용
    - ECP Simulation PSI UI에서 Confirm 버튼을 누르면 ECP Request List와 ECP Confirm MG의 값을 Update한다.

* 변경이력
    - 2025.12.22 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_AllWeek          : Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
    - df_in_ECPRequestList   : Select ([Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq] ) on row, ({Measure.[ECP Req List_ECP Status], Measure.[ECP Req List_Qty] }) on column where {[Version].[Version Name], Measure.[ECP Req List_ECP Status] == "Air ECP (Request)"};
    - df_in_ECPRequestList2  : Select ([Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] ) on row, ({ Measure.[ECP Req List_Qty] }) on column where { [Version].[Version Name], Measure.[ECP Req List_ECP Status] == "Air ECP (Request)"};
    - df_in_ECPSimulationPSI : Select ([Location].[Location] * &MDMHorizon * [Item Material].[Item Material] ) on row, ({ Measure.[ECP Simulation PSI W_SOP_ETD], Measure.[ECP Simulation PSI W_Air LT] }) on column where {[Version].[Version Name], ~IsNull(Measure.[ECP Simulation PSI W_SOP_ETD])};
    # - df_in_AirCost          :

* Flow Summary
    - STEP1. ECPRequestList와 ECPSimulationPSI로 Item Material, Item 당 자재 소요량 계산
    - STEP2. Item Material, Item당 자재 소요량을 바탕으로 df_out_ECPRequestList 계산
    - STEP3. df_out_ECPRequestList를 aggregation하여 df_out_ECPConfirm 계산.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ECPRequestList
    - df_out_ECPConfirm

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ECPConfirm] for measures {[ECP Req List_ETA W]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_ECPRequestList
        Select (&MPV * [Location].[Location] * [Item].[Item] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Seq].[Seq] ) on row,
        ({Measure.[ECP Req List_ECP Status], Measure.[ECP Req List_Air Cost], Measure.[ECP Req List_ETA W], Measure.[ECP Req List_ETD Qty], Measure.[ECP Req List_ETD W]}) on column limit 100;
    - df_out_ECPConfirm
        Select (&MPV * [Item Material].[Item Material] * [BOM Info].[BOM Version] ) on row,
        ({Measure.[ECP Simulation Confirm_Air Amt], Measure.[ECP Simulation Confirm_Air ETA W], Measure.[ECP Simulation Confirm_Air N Price], Measure.[ECP Simulation Confirm_ETD Qty], Measure.[ECP Simulation Confirm_ETD W]}) on column limit 100;

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
str_instance = 'PY_UI_ECPConfirm'
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
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_ECPRequestList = read_csv_file("df_in_ECPRequestList")
            df_in_ECPRequestList2 = read_csv_file("df_in_ECPRequestList2")
            df_in_ECPSimulationPSI = read_csv_file("df_in_ECPSimulationPSI")
            df_in_AirCost = read_csv_file("df_in_AirCost")


        dataframes = {
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_ECPRequestList': df_in_ECPRequestList,
            'df_in_ECPRequestList2': df_in_ECPRequestList2,
            'df_in_ECPSimulationPSI': df_in_ECPSimulationPSI,
            'df_in_AirCost': df_in_AirCost,
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

        STATUS_COLUMN = 'Status.[Status]'
        BOM_TYPE_COLUMN = 'BOM Type.[BOM Type]'
        BOM_STATUS_COLUMN = 'BOM Status.[BOM Status]'
        FULL_BOM_BASE_QTY_COLUMN = 'Full BOM_Base Qty'

        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        SEQ_COLUMN = 'Seq.[Seq]'

        ECP_REQ_LIST_QTY_COLUMN = 'ECP Req List_Qty'
        ECP_REQ_TOTAL_COLUMN = 'ECP Req Total'
        ECP_REQ_LIST_ECP_STATUS_COLUMN = 'ECP Req List_ECP Status'
        ECP_SIMULATION_PSI_W_SOP_ETD_COLUMN = 'ECP Simulation PSI W_SOP_ETD'
        ECP_SIMULATION_PSI_W_AIR_LT_COLUMN = 'ECP Simulation PSI W_Air LT'

        ECP_REQ_LIST_AIR_COST_COLUMN = 'ECP Req List_Air Cost'
        ECP_REQ_LIST_ETA_W_COLUMN = 'ECP Req List_ETA W'
        ECP_REQ_LIST_ETD_QTY_COLUMN = 'ECP Req List_ETD Qty'
        ECP_REQ_LIST_ETD_W_COLUMN = 'ECP Req List_ETD W'

        ECP_SIMULATION_CONFIRM_AIR_AMT_COLUMN = 'ECP Simulation Confirm_Air Amt'
        ECP_SIMULATION_CONFIRM_AIR_ETA_W_COLUMN = 'ECP Simulation Confirm_Air ETA W'
        ECP_SIMULATION_CONFIRM_AIR_N_PRICW_COLUMN = 'ECP Simulation Confirm_Air N Price'
        ECP_SIMULATION_CONFIRM_ETD_QTY_COLUMN = 'ECP Simulation Confirm_ETD Qty'
        ECP_SIMULATION_CONFIRM_ETD_W_COLUMN = 'ECP Simulation Confirm_ETD W'

        version_columns = [VERSION_NAME_COLUMN]

        key_ecp_req_columns = [LOCATION_COLUMN, ITEM_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, SEQ_COLUMN]
        key_confirm_columns = [ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]

        ecp_req_columns = [
            ECP_REQ_LIST_ECP_STATUS_COLUMN, ECP_REQ_LIST_ETA_W_COLUMN, ECP_REQ_LIST_ETD_QTY_COLUMN, ECP_REQ_LIST_ETD_W_COLUMN,
        ]

        ecp_confirm_columns = [
            ECP_SIMULATION_CONFIRM_AIR_ETA_W_COLUMN, ECP_SIMULATION_CONFIRM_ETD_QTY_COLUMN, ECP_SIMULATION_CONFIRM_ETD_W_COLUMN,
        ]

        fn_ecp_req_columns = version_columns + key_ecp_req_columns + ecp_req_columns
        fn_ecp_confirm_columns = version_columns + key_confirm_columns + ecp_confirm_columns

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
        # if df_in_ECPRequestList.empty & df_in_ECPRequestList2.empty :
        #     raise CustomException("STEP3 by 0 ____ df_in_ECPRequestList 와 df_in_ECPRequestList2 값이 없습니다.")


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_in_ECPRequestList 를 기준으로 Location, Item Material, Sub Location 에 따라 df_in_ECPRequestList2 의 [ECP Req List_Qty] 를 Merge한다. df_in_ECPRequestList2 의 [ECP Req List_Qty] 필드명을 [ECP Req Total] 로 한다')
        df_in_ECPRequestList = df_in_ECPRequestList.merge(
            df_in_ECPRequestList2, how="inner",
            on=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN]
        )
        print_df(df_in_ECPRequestList, 'STEP4 by 1.1  ____ df_in_ECPRequestList .... merge')

        df_in_ECPRequestList.rename(columns={
            ECP_REQ_LIST_QTY_COLUMN+'_y': ECP_REQ_TOTAL_COLUMN,
            ECP_REQ_LIST_QTY_COLUMN+'_x': ECP_REQ_LIST_QTY_COLUMN,
        }, inplace=True)
        print_df(df_in_ECPRequestList, 'STEP4 by 1.2  ____ df_in_ECPRequestList .... rename')
        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : df_in_ECPRequestList 를 기준으로 Location, Item Material 에 따라 df_in_ECPSimulationPSI 의 [Time].[Week], [ECP Simulation PSI W_SOP_ETD], [ECP Simulation PSI W_Air LT] 를 Merge한다.')
        df_in_ECPRequestList = df_in_ECPRequestList.merge(
            df_in_ECPSimulationPSI, how="inner",
            on=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN]
        )
        print_df(df_in_ECPRequestList, 'STEP4 by 2.1  ____ df_in_ECPRequestList .... merge')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : df_in_ECPRequestList QTY 및 컬럼 설정')
        # 1. df_in_ECPRequestList 의 각 row에 대해 아래 방식으로 [ECP Req List_ETA W],  [ECP Req List_ETD Qty] 를 구한다.
        #   [ECP Req List_ETA W] = [Time].[Week] + [ECP Simulation PSI W_Air LT]
        #   [ECP Req List_ETD Qty] = [ECP Simulation PSI W_SOP_ETD] * [ECP Req List_Qty] / [ECP Req Total]
        # 2. df_in_ECPRequestList 의 필드 [Seq].[Seq], [ECP Req List_ECP Status]의 값을 아래와 같이 Update한다.
        #   [ECP Req List_ECP Status]:  "Air ECP (Request)"  →   "Air ECP (Confirm)"
        # 3. df_in_ECPRequestList 의 필드명을 다음과 같이 수정한다.
        #   [Time].[Week] →  [ECP Req List_ETD W]
        # 4. 아래 필드를 제거한다.
        #   [ECP Req List_Qty], [ECP Req Total], [ECP Simulation PSI W_SOP_ETD], [ECP Simulation PSI W_Air LT]

        # 유니크한 주차 리스트 추출
        unique_weeks = df_in_AllWeek[TIME_WEEK_COLUMN].unique()
        week_to_idx = pd.Series(range(len(unique_weeks)), index=unique_weeks)

        # 인덱스 계산
        curr_idx = df_in_ECPRequestList[TIME_WEEK_COLUMN].map(week_to_idx)
        target_idx = curr_idx + df_in_ECPRequestList[ECP_SIMULATION_PSI_W_AIR_LT_COLUMN]

        # 결과값 할당 (범위 체크 포함)
        max_idx = len(unique_weeks) - 1
        valid_mask = target_idx.between(0, max_idx) & target_idx.notnull()

        df_in_ECPRequestList[ECP_REQ_LIST_ETA_W_COLUMN] = np.nan
        df_in_ECPRequestList.loc[valid_mask, ECP_REQ_LIST_ETA_W_COLUMN] = unique_weeks[target_idx[valid_mask].astype(int)]

        df_in_ECPRequestList[ECP_REQ_LIST_ETD_QTY_COLUMN] = (
                df_in_ECPRequestList[ECP_SIMULATION_PSI_W_SOP_ETD_COLUMN] *
                df_in_ECPRequestList[ECP_REQ_LIST_QTY_COLUMN] /
                df_in_ECPRequestList[ECP_REQ_TOTAL_COLUMN]
        )
        print_df(df_in_ECPRequestList, 'STEP4 by 3.1  ____ df_in_ECPRequestList .... columns add')

        df_in_ECPRequestList[ECP_REQ_LIST_ETD_W_COLUMN] = df_in_ECPRequestList[TIME_WEEK_COLUMN]
        df_in_ECPRequestList.drop(columns=[
            ECP_REQ_LIST_QTY_COLUMN, ECP_REQ_TOTAL_COLUMN, ECP_SIMULATION_PSI_W_SOP_ETD_COLUMN, ECP_SIMULATION_PSI_W_AIR_LT_COLUMN,
        ], inplace=True)
        print_df(df_in_ECPRequestList, 'STEP4 by 3.2  ____ df_in_ECPRequestList .... columns drop')

        step('=====> STEP4 by 3 End')



        step('=====> STEP4 by 4 Start : empty')
        step('=====> STEP4 by 4 End')



        step('=====> STEP4 by 5 Start : empty')
        step('=====> STEP4 by 5 End')



        step('=====> STEP4 by 6 Start : df_in_ECPRequestList 를 df_ECPConfirm 으로 복사한다.')
        # 1. df_in_ECPRequestList 를 df_ECPConfirm 으로 복사한다.
        # 2. df_ECPConfirm 을 [Item Material].[Item Material], [BOM Info].[BOM Version] 에 따라 [ECP Req List_ETD Qty], [ECP Req List_Air Cost] 을 sum aggregation, [ECP Req List_ETD W], [ECP Req List_ETA W], [Air Cost] 을 min aggregation 한다.
        # 3. df_ECPConfirm의 필드명을 다음과 같이 수정한다.
        #   [ECP Req List_ETD W]  →  [ECP Simulation Confirm_ETD W]
        #   [ECP Req List_ETA W]  →  [ECP Simulation Confirm_Air ETA W]
        #   [ECP Req List_ETD Qty]  →  [ECP Simulation Confirm_ETD Qty]
        #   [Air Cost]  →  [ECP Simulation Confirm_Air N Price]
        #   [ECP Req List_Air Cost]  →  [ECP Simulation Confirm_Air Amt]

        df_ECPConfirm = rename_and_delete_df(df_in_ECPRequestList)

        # int_columns = [ECP_REQ_LIST_ETD_QTY_COLUMN, ECP_REQ_LIST_AIR_COST_COLUMN]
        int_columns = [ECP_REQ_LIST_ETD_QTY_COLUMN]
        for column in int_columns:
            df_ECPConfirm[column] = df_ECPConfirm[column].fillna(0).astype(int)

        groupby_columns = [ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        sum_columns = int_columns
        min_columns = [ECP_REQ_LIST_ETD_W_COLUMN, ECP_REQ_LIST_ETA_W_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        agg_dict.update({col: 'min' for col in min_columns})
        df_ECPConfirm = df_ECPConfirm.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_ECPConfirm, 'STEP4 by 6.1  ____ df_ECPConfirm .... groupby')

        df_ECPConfirm = df_ECPConfirm.rename(columns={
            ECP_REQ_LIST_ETD_W_COLUMN: ECP_SIMULATION_CONFIRM_ETD_W_COLUMN,
            ECP_REQ_LIST_ETA_W_COLUMN: ECP_SIMULATION_CONFIRM_AIR_ETA_W_COLUMN,
            ECP_REQ_LIST_ETD_QTY_COLUMN: ECP_SIMULATION_CONFIRM_ETD_QTY_COLUMN,
        }, inplace=True)
        step('=====> STEP4 by 6 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_ECPConfirm = rename_and_delete_df(df_ECPConfirm)
        if df_out_ECPConfirm is None:
            df_out_ECPConfirm = pd.DataFrame(columns=fn_ecp_confirm_columns)

        df_out_ECPConfirm[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ECPConfirm = df_out_ECPConfirm[fn_ecp_confirm_columns]
        df_out_ECPConfirm = df_out_ECPConfirm.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        df_out_ECPRequestList = pd.DataFrame(columns=fn_ecp_req_columns)
        df_out_ECPRequestList[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ECPRequestList = df_out_ECPRequestList[fn_ecp_req_columns]
        df_out_ECPRequestList = df_out_ECPRequestList.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_ECPConfirm': df_out_ECPConfirm,
            'df_out_ECPRequestList': df_out_ECPRequestList,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ECPConfirm = pd.DataFrame(columns=fn_ecp_confirm_columns)
        df_out_ECPRequestList = pd.DataFrame(columns=fn_ecp_req_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ECPConfirm = pd.DataFrame(columns=fn_ecp_confirm_columns)
        df_out_ECPRequestList = pd.DataFrame(columns=fn_ecp_req_columns)
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
