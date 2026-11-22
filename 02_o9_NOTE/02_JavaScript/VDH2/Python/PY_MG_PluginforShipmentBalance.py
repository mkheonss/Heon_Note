"""
* 프로그램명
    - PY_MG_PluginforShipmentBalance

* 내용
    - Production Pegging - SourceVersion의 자재 Shipment의 production 잔량 산출
    - Consumption Pegging - SourceVersion의 자재 Shipment의 Consumption 잔량 산출, infinite vendo로부터의 shipment 제외

* 변경이력
    - 2025.11.20 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek    : Select (&CurrentWeek);
    - df_in_AddPaneGrpMst : Select ([Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({Measure.[Add Panel Grp Mst_Created by], Measure.[Add Panel Grp Mst_Creation time], Measure.[Add Panel Grp Mst_POP W], Measure.[Add Panel Grp Mst_Sum LT], Measure.[Add Panel Grp Mst_Total LT], Measure.[Add Panel Grp Mst_Update time], Measure.[Add Panel Grp Mst_Updated by]}) on column where {[Version].[Version Name]};
    - df_in_AllWeek     : Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
    - df_in_ProductionPegging  : Select (FROM.[Location].[Location] * FROM.[Item].[Item Stage].filter(#.Name in {"OPEN_CELL", "PANEL"}).relatedmembers([Item]) * FROM.[Time].[Week] * FROM.[Documents].[Document Type].[Shipment Schedule].relatedMembers([OrderlineID]) * FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * TO.[To Location].[To Location] * TO.[To Item].[To Item] * TO.[To Time].[To Week] * TO.[Location].[Location] * TO.[Item].[Item] * TO.[Time].[Week] * TO.[Documents].[OrderlineID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph], Version.[Version Name]};
    - df_in_ConsumptionPegging : Select (FROM.[Location].[Location] * FROM.[Item].[Item Stage].filter(#.Name in {"OPEN_CELL", "PANEL"}).relatedmembers([Item]) * FROM.[Time].[Week] * FROM.[Documents].[Document Type].[Shipment Schedule].relatedMembers([OrderlineID]) * FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * TO.[To Location].[To Location] * TO.[To Item].[To Item] * TO.[To Time].[To Week] * TO.[Location].[Location] * TO.[Item].[Item] * TO.[Time].[Week] * TO.[Documents].[OrderlineID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer From Pegged]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph], Version.[Version Name]};

* Flow Summary
    - STEP1. PluginforShipmentBalance
                Production Pegging의 From node와 To node가 동일한 경우만 선택(FROM.[Item].[Item] == TO.[Item].[Item] and FROM.[Location].[Location] == TO.[Location].[Location])
                Production Pegging, Consumption Pegging의 FROM.[Documents].[OrderlineID], FROM.[Activity1].[Activity1], FROM.[Activity2].[Activity2], FROM.[Activity3].[Activity3], TO.[Time].[Week], TO.[Item].[Item], TO.[Location].[Location]이 모두 동일해야 함


* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_PluginforProductionBalance
    - df_out_PluginforConsumptionBalance

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_MG_PluginforShipmentBalance] for measures {[W WIP Material Consumption Quantity]} using scope (&MPV)
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
str_instance = 'PY_MG_PluginforShipmentBalance'
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
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_AddPaneGrpMst = read_csv_file("df_in_AddPaneGrpMst")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_ProductionPegging = read_csv_file("df_in_ProductionPegging")
            df_in_ConsumptionPegging = read_csv_file("df_in_ConsumptionPegging")


        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_AddPaneGrpMst': df_in_AddPaneGrpMst,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_ProductionPegging': df_in_ProductionPegging,
            'df_in_ConsumptionPegging': df_in_ConsumptionPegging,
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
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_STAGE_COLUMN = 'Item.[Item]'
        DOCUMENTS_ORDERLINEID_COLUMN = '[Documents].[OrderlineID]'
        ACTIVITY1_COLUMN = '[Activity1].[Activity1]'
        ACTIVITY2_COLUMN = '[Activity2].[Activity2]'
        ACTIVITY3_COLUMN = '[Activity3].[Activity3]'
        FROM_ACTIVITY1_COLUMN = 'from.[Activity1].[Activity1]'
        FROM_ACTIVITY2_COLUMN = 'from.[Activity2].[Activity2]'
        FROM_ACTIVITY3_COLUMN = 'from.[Activity3].[Activity3]'
        TARGET_WEEK_COLUMN = 'targe_week'

        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'
        ADD_PANEL_GRP_MST_SUM_LT_COLUMN = 'Add Panel Grp Mst_Sum LT'

        FROM_ITEM_COLUMN = 'from.[Item].[Item]'
        FROM_DOCUMENTS_ORDERLINEID_COLUMN = 'from.[Documents].[OrderlineID]'
        FROM_TIME_WEEK_COLUMN = 'from.[Time].[Week]'
        FROM_LOCATION_COLUMN = 'from.[Location].[Location]'

        TO_TIME_WEEK_COLUMN = 'to.[Time].[Week]'
        TO_ITEM_COLUMN = 'to.[Item].[Item]'
        TO_LOCATION_COLUMN = 'to.[Location].[Location]'
        TO_DEMAND_TYPE_COLUMN = 'to.[Demand Type].[Demand Type]'

        TO_TO_LOCATION_COLUMN = 'to.[To Location].[To Location]'
        TO_TO_ITEM_COLUMN = 'to.[To Item].[To Item]'
        TO_TO_TIME_WEEK_COLUMN = 'to.[To Time].[To Week]'

        SOP_BUP_PRODUCER_TO_CONSUMER_FROM_PEGGED_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]'
        SOP_BUP_CONSUMER_TO_CONSUMER_FROM_PEGGED_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]'

        W_WIP_METERIAL_PRODUCTION_QUANTITY_COLUMN = 'W WIP Material Production Quantity'
        W_WIP_METERIAL_CONSUMPTION_QUANTITY_COLUMN = 'W WIP Material Consumption Quantity'
        W_WIP_PEGGING_ID_COLUMN = 'W WIP Pegging ID'

        version_columns = [VERSION_NAME_COLUMN]
        key_columns = [ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN]

        pluginfor_production_balance_columns = [
            W_WIP_METERIAL_PRODUCTION_QUANTITY_COLUMN, W_WIP_PEGGING_ID_COLUMN,
        ]

        pluginfor_consumption_balance_columns = [
            W_WIP_METERIAL_CONSUMPTION_QUANTITY_COLUMN, W_WIP_PEGGING_ID_COLUMN,
        ]

        fn_pluginfor_production_balance_columns = version_columns + key_columns + pluginfor_production_balance_columns
        fn_pluginfor_consumption_balance_columns = version_columns + key_columns + pluginfor_consumption_balance_columns

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
        if df_in_ProductionPegging.empty & df_in_ConsumptionPegging.empty :
            raise CustomException("STEP3 by 0 ____ df_in_ProductionPegging 과 df_in_ConsumptionPegging 값이 없습니다.")


        # 현재 주차 가져오기
        current_week = get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN)
        step(f'=====> current_week : {current_week}')

        # df_in_AllWeek 필요컬럼 설정
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN]].drop_duplicates().reset_index(drop=True)
        print_df(df_in_AllWeek, 'STEP3 by 0.1  ____ df_in_AllWeek .... week uniqe')

        df_in_ProductionPegging[TO_TIME_WEEK_COLUMN] = df_in_ProductionPegging[TO_TIME_WEEK_COLUMN].astype(int)
        df_in_ConsumptionPegging[TO_TIME_WEEK_COLUMN] = df_in_ConsumptionPegging[TO_TIME_WEEK_COLUMN].astype(int)

        df_in_AddPaneGrpMst = df_in_AddPaneGrpMst[[
            LOCATION_COLUMN, ITEM_METERIAL_COLUMN, ADD_PANEL_GRP_MST_SUM_LT_COLUMN
        ]].drop_duplicates()

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 0 Start : df_in_AddPaneGrpMst 와 Merge 한 후 target week 설정')
        df_in_ProductionPegging = df_in_ProductionPegging.merge(
            df_in_AddPaneGrpMst, how='left',
            left_on=[FROM_LOCATION_COLUMN, FROM_ITEM_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN],
        )
        df_in_ProductionPegging.drop(columns=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN], inplace=True)
        df_in_ProductionPegging[ADD_PANEL_GRP_MST_SUM_LT_COLUMN] = df_in_ProductionPegging[ADD_PANEL_GRP_MST_SUM_LT_COLUMN].fillna(0).astype(int)
        print_df(df_in_ProductionPegging, 'STEP4 by 0.1  ____ df_in_ProductionPegging .... merge')

        def map_target_weeks(df_all_week: pd.DataFrame, df_plugin: pd.DataFrame, current_week: int, time_week_col: str,
                             lt_col: str, target_week_col: str) -> pd.DataFrame:
            """
            df_all_week에서 current_week의 위치를 찾아 df_plugin의 LT(리드타임)만큼 offset된 주차 정보를 매핑.
            """

            # 1. 기준 주차의 시작 인덱스 확인
            matching_indices = df_all_week.index[df_all_week[time_week_col] == current_week].tolist()
            if not matching_indices:
                raise ValueError(f"current_week {current_week}이(가) df_all_week에 존재하지 않습니다.")

            start_idx = matching_indices[0]

            # 2. 벡터화 연산: LT를 더해 타겟 인덱스 계산
            # .values를 사용하여 넘파이 배열로 처리함으로써 성능 최적화
            target_indices = df_plugin[lt_col].values + start_idx

            # 3. 인덱스 범위 유효성 검사 (Clip 대신 유효 마스크 생성)
            max_idx = len(df_all_week) - 1
            valid_mask = (target_indices >= 0) & (target_indices <= max_idx)

            # 4. 결과 배열 초기화 및 매핑
            # iloc으로 접근하기 위해 numpy array를 활용
            results = np.full(len(df_plugin), np.nan)

            # 유효한 인덱스에 대해서만 df_all_week의 첫 번째 컬럼(주차 정보) 값을 가져옴
            # .iloc[indices, 0]는 해당 위치의 주차 컬럼 값을 의미함
            results[valid_mask] = df_all_week.iloc[target_indices[valid_mask], 0].values

            # 5. 데이터프레임에 적용 및 타입 변환
            df_plugin[target_week_col] = results
            df_plugin[target_week_col] = df_plugin[target_week_col].astype('Int64')

            return df_plugin

        df_in_ProductionPegging = map_target_weeks(
            df_all_week=df_in_AllWeek,
            df_plugin=df_in_ProductionPegging,
            current_week=current_week,
            time_week_col=TIME_WEEK_COLUMN,
            lt_col=ADD_PANEL_GRP_MST_SUM_LT_COLUMN,
            target_week_col=TARGET_WEEK_COLUMN
        )
        print_df(df_in_ProductionPegging, 'STEP4 by 0.2  ____ df_in_ProductionPegging .... target_week')
        step('=====> STEP4 by 0 End')



        step('=====> STEP4 by 1 Start : Shipment Prod 에서 From node와 To node가 동일한 경우만 선택')
        df_in_ProductionPegging_1 = df_in_ProductionPegging[
            (df_in_ProductionPegging[FROM_ITEM_COLUMN] == df_in_ProductionPegging[TO_TO_ITEM_COLUMN]) &
            (df_in_ProductionPegging[FROM_LOCATION_COLUMN] == df_in_ProductionPegging[TO_TO_LOCATION_COLUMN])
        ].copy()
        print_df(df_in_ProductionPegging_1, 'STEP4 by 1.1  ____ df_in_ProductionPegging_1 .... filter')
        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : Shipment Prod 에서 From node와 demand node가 동일한 경우만 선택하거나(사용되지 않은 경우) 해당 자재의 패널 확정구간 이후에 사용되는 경우만 포함')
        # target_week = int(get_next_week(df_in_AllWeek, TIME_WEEK_COLUMN, int(SolverCurrentBucket), int(PanelFrozenWindow)))
        # step(f'=====> target_week : {target_week}')

        df_in_ProductionPegging_2 = df_in_ProductionPegging[
            (df_in_ProductionPegging[FROM_ITEM_COLUMN] == df_in_ProductionPegging[TO_ITEM_COLUMN]) &
            (df_in_ProductionPegging[FROM_LOCATION_COLUMN] == df_in_ProductionPegging[TO_LOCATION_COLUMN]) &
            (
                    (df_in_ProductionPegging[TO_DEMAND_TYPE_COLUMN] == 'InventoryDemand') |
                    (df_in_ProductionPegging[TO_TIME_WEEK_COLUMN] >= df_in_ProductionPegging[TARGET_WEEK_COLUMN])
            )
        ].copy()
        print_df(df_in_ProductionPegging_2, 'STEP4 by 2.1  ____ df_in_ProductionPegging_2 .... filter')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : Shipment Prod 와 Mtrl BU Shipment Cons 의 FROM.[Documents].[OrderlineID], FROM.[Activity1].[Activity1], FROM.[Activity2].[Activity2], FROM.[Activity3].[Activity3], TO.[To Item].[To Item], TO.[To Location].[To Location], TO.[To Time].[To Week], TO.[Demand].[DemandID]가 모두 동일해야 함')
        df_in_ProductionPegging = pd.concat([df_in_ProductionPegging_1, df_in_ProductionPegging_2], ignore_index=True).drop_duplicates()

        df_PluginforShipmentBalance = pd.merge(
            df_in_ProductionPegging, df_in_ConsumptionPegging, how='inner',
            left_on=[
                TO_TIME_WEEK_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
                FROM_DOCUMENTS_ORDERLINEID_COLUMN, FROM_ACTIVITY1_COLUMN, FROM_ACTIVITY2_COLUMN, FROM_ACTIVITY3_COLUMN,
            ],
            right_on=[
                TO_TIME_WEEK_COLUMN, TO_ITEM_COLUMN, TO_LOCATION_COLUMN,
                FROM_DOCUMENTS_ORDERLINEID_COLUMN, FROM_ACTIVITY1_COLUMN, FROM_ACTIVITY2_COLUMN, FROM_ACTIVITY3_COLUMN,
            ]
        )
        print_df(df_PluginforShipmentBalance, 'STEP4 by 3.1  ____ df_PluginforShipmentBalance .... merge')
        step('=====> STEP4 by 3 End')



        step('=====> STEP4 by 4 Start : Production Pegging 구성')
        df_ProductionPegging = df_PluginforShipmentBalance[[
            FROM_ITEM_COLUMN+'_x',
            FROM_LOCATION_COLUMN+'_x',
            FROM_TIME_WEEK_COLUMN+'_x',
            FROM_DOCUMENTS_ORDERLINEID_COLUMN,
            FROM_ACTIVITY1_COLUMN,
            FROM_ACTIVITY2_COLUMN,
            FROM_ACTIVITY3_COLUMN,
            SOP_BUP_PRODUCER_TO_CONSUMER_FROM_PEGGED_COLUMN,
        ]].copy().drop_duplicates()

        df_ProductionPegging.rename(columns={
            FROM_ITEM_COLUMN+'_x': ITEM_COLUMN,
            FROM_LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            FROM_TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
            FROM_DOCUMENTS_ORDERLINEID_COLUMN: DOCUMENTS_ORDERLINEID_COLUMN,
            FROM_ACTIVITY1_COLUMN: ACTIVITY1_COLUMN,
            FROM_ACTIVITY2_COLUMN: ACTIVITY2_COLUMN,
            FROM_ACTIVITY3_COLUMN: ACTIVITY3_COLUMN,
        }, inplace=True)
        print_df(df_ProductionPegging, 'STEP4 by 4.1  ____ df_ProductionPegging .... column modify')

        df_ProductionPegging[TIME_WEEK_COLUMN] = df_ProductionPegging[TIME_WEEK_COLUMN].astype(str)
        grouped_colunm = [
            ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN,
            ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN,
        ]
        df_ProductionPegging[W_WIP_METERIAL_PRODUCTION_QUANTITY_COLUMN] = (
            df_ProductionPegging.groupby(grouped_colunm)[SOP_BUP_PRODUCER_TO_CONSUMER_FROM_PEGGED_COLUMN].transform('sum')
        )
        df_ProductionPegging[W_WIP_PEGGING_ID_COLUMN] = 3
        df_ProductionPegging[TIME_WEEK_COLUMN] = df_ProductionPegging[TIME_WEEK_COLUMN].astype(int)
        print_df(df_ProductionPegging, 'STEP4 by 4.2  ____ df_ProductionPegging .... recreate')
        step('=====> STEP4 by 4 End')



        step('=====> STEP4 by 5 Start : Consumption Pegging 구성')
        df_ConsumptionPegging = df_PluginforShipmentBalance[[
            FROM_ITEM_COLUMN+'_y',
            FROM_LOCATION_COLUMN+'_y',
            FROM_TIME_WEEK_COLUMN+'_y',
            FROM_DOCUMENTS_ORDERLINEID_COLUMN,
            FROM_ACTIVITY1_COLUMN,
            FROM_ACTIVITY2_COLUMN,
            FROM_ACTIVITY3_COLUMN,
            SOP_BUP_CONSUMER_TO_CONSUMER_FROM_PEGGED_COLUMN,
        ]].copy().drop_duplicates()

        df_ConsumptionPegging.rename(columns={
            FROM_ITEM_COLUMN+'_y': ITEM_COLUMN,
            FROM_LOCATION_COLUMN+'_y': LOCATION_COLUMN,
            FROM_TIME_WEEK_COLUMN+'_y': TIME_WEEK_COLUMN,
            FROM_DOCUMENTS_ORDERLINEID_COLUMN: DOCUMENTS_ORDERLINEID_COLUMN,
            FROM_ACTIVITY1_COLUMN: ACTIVITY1_COLUMN,
            FROM_ACTIVITY2_COLUMN: ACTIVITY2_COLUMN,
            FROM_ACTIVITY3_COLUMN: ACTIVITY3_COLUMN,
        }, inplace=True)
        print_df(df_ConsumptionPegging, 'STEP4 by 5.1  ____ df_ConsumptionPegging .... column modify')

        df_ConsumptionPegging[TIME_WEEK_COLUMN] = df_ConsumptionPegging[TIME_WEEK_COLUMN].astype(str)
        grouped_colunm = [
            ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, DOCUMENTS_ORDERLINEID_COLUMN,
            ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN,
        ]
        df_ConsumptionPegging[W_WIP_METERIAL_CONSUMPTION_QUANTITY_COLUMN] = (
            df_ConsumptionPegging.groupby(grouped_colunm)[SOP_BUP_CONSUMER_TO_CONSUMER_FROM_PEGGED_COLUMN].transform('sum')
        )
        df_ConsumptionPegging[W_WIP_PEGGING_ID_COLUMN] = 3
        df_ConsumptionPegging[TIME_WEEK_COLUMN] = df_ConsumptionPegging[TIME_WEEK_COLUMN].astype(int)
        print_df(df_ConsumptionPegging, 'STEP4 by 5.2  ____ df_ConsumptionPegging .... recreate')
        step('=====> STEP4 by 5 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_PluginforProductionBalance = rename_and_delete_df(df_ProductionPegging)
        df_out_PluginforProductionBalance[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_PluginforProductionBalance = df_out_PluginforProductionBalance[fn_pluginfor_production_balance_columns]
        df_out_PluginforProductionBalance = df_out_PluginforProductionBalance.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        df_out_PluginforConsumptionBalance = rename_and_delete_df(df_ConsumptionPegging)
        df_out_PluginforConsumptionBalance[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_PluginforConsumptionBalance = df_out_PluginforConsumptionBalance[fn_pluginfor_consumption_balance_columns]
        df_out_PluginforConsumptionBalance = df_out_PluginforConsumptionBalance.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_PluginforProductionBalance': df_out_PluginforProductionBalance,
            'df_out_PluginforConsumptionBalance': df_out_PluginforConsumptionBalance,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_PluginforProductionBalance = pd.DataFrame(columns=fn_pluginfor_production_balance_columns)
        df_out_PluginforConsumptionBalance = pd.DataFrame(columns=fn_pluginfor_consumption_balance_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_PluginforProductionBalance = pd.DataFrame(columns=fn_pluginfor_production_balance_columns)
        df_out_PluginforConsumptionBalance = pd.DataFrame(columns=fn_pluginfor_consumption_balance_columns)
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
