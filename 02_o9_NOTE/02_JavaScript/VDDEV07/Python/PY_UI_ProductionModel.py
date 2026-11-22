"""
* 프로그램명
    - PY_UI_ProductionModel

* 내용
     - Location, Item, Line별 From Inch, To Inch, Tact Time을 과거 12주 실적을 바탕으로 Compute.

* 변경이력
    - 2025.12.02 / 김신 / Create
    - 2026.03.12 / 김신 / 수정
      -Tact Time Actual은 Consume Capa를 Mfg Qty로 나누어 평균 Tact Time을 계산합니다.
      -Tact_Time이 Null이 아닌 값에 대해서만 Consume Capa 평균값 구해야함.
      -STEP3-1에서 Week별로 sum aggregation하는 구문 추가하면 시간 복잡도 개선 예상.
      -Step 3-1 추가
      -df_final_result['Mfg_Act_Mfg_Qty'] > 0 [Prod Model_Tact Time Actual] = round([Consume Capa] / [Mfg Act_Mfg Qty], 2) 수정
* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_MfgActual
      Select ([Location].[Location] * [Item].[Item] * [Item].[Product Group].filter(#.Name in {"MONITOR", "TV", "AV"}) * [Item].[Definition] * [Item].[Marketing Name] * [Item].[Project] * [Item].[Inch].filter( #.Name contains "0" || #.Name contains "1" || #.Name contains "2" || #.Name contains "3" || #.Name contains "4" || #.Name contains "5" || #.Name contains "6" || #.Name contains "7" || #.Name contains "8" || #.Name contains "9") * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Leadoffset(-12).Key) * [Time].[Day] * [Sequence].[Sequence] * [Sub Location].[Sub Location] ) on row,
             ({Measure.[Mfg Act_Line], Measure.[Mfg Act_Mfg Qty]}) on column
      where {[Version].[Version Name].[CWV_MP], [Item].[Item Stage].[SET], ~IsNull(Measure.[Mfg Act_Line])};
    - df_in_TactTime
      Select ([Version].[Version Name].filter(#.Name == &CurrentWeek.element(0).Leadoffset(-1).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-2).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-3).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-4).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-5).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-6).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-7).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-8).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-9).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-10).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-11).Name || #.Name == &CurrentWeek.element(0).Leadoffset(-12).Name ) * [Location].[Location] * [Item].[Item] * [Line].[Line] ) on row,({Measure.[Tact Time_Time]}) on column        where {[Item].[Item Stage].[SET], Measure.[Tact Time_Valid Asn] == TRUE};
       ※ &NSUILocationPlant = [Location].[Location Type].[MF].relatedmembers([Location])

    - df_in_ProductModel
     Select ([Location].[Location] * [Item].[Marketing Name] * [Sequence].[Sequence] * [Definition].[Definition] * [Product].[Product Group] * [Project].[Project] * [Line].[Line] ) on row,({Measure.[Prod Model_From Inch], Measure.[Prod Model_Tact Time], Measure.[Prod Model_To Inch]} ) on column
      where {[Version].[Version Name].[CWV_MP]};

* 주요 Logic ( Data 처리 )

* Output Table
    - df_out_Prod_Model
      Select ( [Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Marketing Name] * [Sequence].[Sequence] * [Definition].[Definition] * [Product].[Product Group] * [Project].[Project] * [Line].[Line]  ) on row,
             ({ Measure.[Prod Model_To Inch Actual], Measure.[Prod Model_From Inch Actual], Measure.[Prod Model_Tact Time Actual] }) on column;

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ProductionModel]
      for measures {[Prod Model_To Inch Actual]}
      using scope ([Version].[Version Name])
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
str_instance = 'PY_UI_ProductionModel'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
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
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", encoding="utf-8-sig",index=False)

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


def rename_and_delete_df(target_df):
    new_df = target_df
    delete_dfs(target_df)
    return new_df


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
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"

########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # Batch 시작
    vd_log_start()

    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_MfgActual = read_csv_file("df_in_MfgActual")
            df_in_TactTime = read_csv_file("df_in_TactTime")
            df_in_ProductModel = read_csv_file("df_in_ProductModel")

        print_df(df_in_MfgActual, 'STEP 1 - Input table load .... df_in_MfgActual')
        print_df(df_in_TactTime, 'STEP 1 - Input table load .... df_in_TactTime')
        print_df(df_in_ProductModel, 'STEP 1 - Input table load .... df_in_ProductModel')
        step('=====> 전처리 End')

        ################################################################################################################
        # DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        ITEM_DEFINITION_COLUMN = 'Item.[Definition]'
        DEFINITION_COLUMN = 'Definition.[Definition]'
        ITEM_PROJECT_COLUMN = 'Item.[Project]'
        ITEM_INCH_COLUMN = 'Item.[Inch]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAY_COLUMN = 'Time.[Day]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        SUB_LOCATION_SUBLOCATION_COLUMN = 'Sub Location.[Sub Location]'
        MFG_ACT_LINE_COLUMN = 'Mfg Act_Line'
        MFG_ACT_MFGQTY_COLUMN = 'Mfg Act_Mfg Qty'
        LINE_COLUMN = 'Line.[Line]'
        TACT_TIME_COLUMN = 'Tact Time_Time'
        ITEM_MARKETING_NAME_COLUMN = 'Item.[Marketing Name]'
        PRODUCT_GROUP_COLUMN = 'Product.[Product Group]'
        PROJECT_COLUMN = 'Project.[Project]'
        PROD_MODEL_TACT_TIME_UPDATE_COLUMN = 'Prod Model_Tact Time Update'

        step('=====> Column 변수 처리 End')

        ################################################################################################################
        # Step 1
        # df_in_MfgActual을 Location, Item, Product Group, Definition, Marketing Name, Project, Inch, Mfg Act_Line,Week
        # 기준으로 Mfg Act_Mfg Qty를 sum aggregation한다.
        ################################################################################################################

        step(
            '=====> STEP1 Start : df_in_MfgActual을 > Location, Item, Product Group, Definition, Marketing Name, Project, Inch, Mfg Act_Line,'
            ' 기준으로 Mfg Act_Mfg Qty를 sum aggregation')
        df_MfgActual_Work = df_in_MfgActual.copy()

        groupby_columns = [LOCATION_COLUMN, ITEM_COLUMN, ITEM_PRODUCT_GROUP_COLUMN,ITEM_DEFINITION_COLUMN,
                           ITEM_MARKETING_NAME_COLUMN,ITEM_PROJECT_COLUMN, ITEM_INCH_COLUMN, MFG_ACT_LINE_COLUMN, TIME_WEEK_COLUMN]
        sum_columns = [MFG_ACT_MFGQTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}

        df_MfgActual_Work = df_MfgActual_Work.groupby(groupby_columns, sort=False, as_index=False).agg(
            agg_dict, skipna=True).copy()

        print_df(df_MfgActual_Work, 'df_MfgActual_Work')
        step('=====> STEP1 End')
        ################################################################################################################
        # Step 2
        # df_in_MfgActual을 기준으로 Location, Item, Week, Mfg Act_Line에 따라 df_in_TactTime의 Tact Time_Time을 Merge한다.
        ################################################################################################################
        step('=====> STEP 2(Start) : df_in_MfgActual을 기준으로 Location, Item, Week, Mfg Act_Line에 따라 '
             'df_in_TactTime의 Tact Time_Time을 Merge한다.')
        df_TactTime_Work = df_in_TactTime.copy()

        df_MfgActual_Work = df_MfgActual_Work.merge(df_TactTime_Work,
                                                    how='left',
                                                    left_on=[LOCATION_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN,
                                                             MFG_ACT_LINE_COLUMN],
                                                    right_on=[LOCATION_COLUMN, ITEM_COLUMN, VERSION_NAME_COLUMN,
                                                              LINE_COLUMN])

        print_df(df_MfgActual_Work, 'df_MfgActual_Work')
        step('=====> STEP2 End')
        ################################################################################################################
        # Step 3
        # df_in_MfgActual의 row별로 Consume Capa를 아래와 같이 구한다.
        # Tact_Time이 Null이 아닌 값에 대해서만 Consume Capa 평균값 구해야함.
        # [Consume Capa] = [Mfg Act_Mfg Qty] * [Tact Time_Time]
        ################################################################################################################
        step('=====> STEP 3(Start) : df_MfgActual_TactTime의 row별로 Consume Capa를 아래와 같이 구한다.')

        df_MfgActual_Work[MFG_ACT_MFGQTY_COLUMN] = np.where(
            df_MfgActual_Work[TACT_TIME_COLUMN] > 0,
            df_MfgActual_Work[MFG_ACT_MFGQTY_COLUMN],0
        )

        df_MfgActual_Work['Consume Capa'] = df_MfgActual_Work[MFG_ACT_MFGQTY_COLUMN] * df_MfgActual_Work[TACT_TIME_COLUMN]

        print_df(df_MfgActual_Work, 'df_MfgActual_Work')
        step('=====> STEP3 End')
        ################################################################################################################
        # Step 3-1
        # df_in_MfgActual을 sum aggregation한다.
        ################################################################################################################
        step('=====> STEP 3-1(Start) : df_in_MfgActual을 sum aggregation한다.')
        groupby_columns = [LOCATION_COLUMN, ITEM_COLUMN, ITEM_PRODUCT_GROUP_COLUMN, ITEM_DEFINITION_COLUMN,
                          ITEM_MARKETING_NAME_COLUMN, ITEM_PROJECT_COLUMN, ITEM_INCH_COLUMN, MFG_ACT_LINE_COLUMN]
        sum_columns = [MFG_ACT_MFGQTY_COLUMN, TACT_TIME_COLUMN, 'Consume Capa']
        agg_dict = {col: 'sum' for col in sum_columns}

        df_MfgActual_Work = df_MfgActual_Work.groupby(groupby_columns, sort=False, as_index=False).agg(
                           agg_dict, skipna=True).copy()

        print_df(df_MfgActual_Work, 'df_MfgActual_Work')
        step('=====> STEP3-1 End')
        ################################################################################################################
        # Step 4
        # df_in_ProductModel을 기준으로 Location, Marketing Name, Definition, Product Group, Project, Line에 따라
        #     df_in_MfgActual의 Inch, Mfg Qty, Consume Capa을 Aggregation하여 Merge한다.
        #     이때, Aggregation( = Grouping)하는 조건은 아래 기준을 따른다.
        #     Inch를 Max Aggregation한 값을[Prod Model_To Inch Actual] 칼럼에 저장한다.
        #     Inch를 Min Aggregation한 값을[Prod Model_From Inch Actual] 칼럼에 저장한다.
        #     Mfg Act_Mfg Qty, Consume Capa를 Sum Aggregation한다.
        #     df_in_ProductModel의 Location, Marketing Name, Definition, Product Group, Project, Line의 값 중 "All" 은 해당 Field의
        #     전부를 의미함을 고려하여 Aggregation하여 Merge한다.
        ################################################################################################################
        step('=====> STEP 4(Start) : df_in_MfgActual의 row별로 Mfg Act_Mfg Qty, Consume Capa 구한다.')
        df_ProductModel_Work = df_in_ProductModel.copy()

        df_MfgActual_Work.rename(columns={
            ITEM_DEFINITION_COLUMN: DEFINITION_COLUMN,
            ITEM_PRODUCT_GROUP_COLUMN: PRODUCT_GROUP_COLUMN,
            ITEM_PROJECT_COLUMN: PROJECT_COLUMN,
            MFG_ACT_LINE_COLUMN: LINE_COLUMN
        }, inplace=True)

        # 숫자형 컬럼 변환(환경 차이 방지)
        for col in [ITEM_INCH_COLUMN]:
            df_MfgActual_Work[col] = pd.to_numeric(df_MfgActual_Work[col], errors="coerce")

        def aggregate_and_merge(df_ProductModel_Work, df_MfgActual_Work):
            results = []

            for _, row in df_ProductModel_Work.reset_index(drop=True).iterrows():
                # 조건 생성
                cond = pd.Series(True, index=df_MfgActual_Work.index)

                for col in [LOCATION_COLUMN, ITEM_MARKETING_NAME_COLUMN, DEFINITION_COLUMN,
                            PRODUCT_GROUP_COLUMN, PROJECT_COLUMN, LINE_COLUMN]:

                    if row[col] != "All":  # 'All'이면 조건 무시
                       cond &= (df_MfgActual_Work[col] == row[col])

                subset = df_MfgActual_Work[cond]

                if not subset.empty:
                    agg = {
                        "Prod_Model_To_Inch_Actual": subset[ITEM_INCH_COLUMN].max(),
                        "Prod_Model_From_Inch_Actual": subset[ITEM_INCH_COLUMN].min(),
                        "Mfg_Act_Mfg_Qty": subset[MFG_ACT_MFGQTY_COLUMN].sum(),
                        "Consume_Capa": subset["Consume Capa"].sum()
                    }
                else:
                    agg = {
                        "Prod_Model_To_Inch_Actual": 0,
                        "Prod_Model_From_Inch_Actual": 0,
                        "Mfg_Act_Mfg_Qty": 0,
                        "Consume_Capa": 0
                    }

                results.append(agg)

            # 결과 병합
            df_result = pd.concat([df_ProductModel_Work.reset_index(drop=True), pd.DataFrame(results)], axis=1)

            return df_result

        df_final_result = aggregate_and_merge(df_ProductModel_Work, df_MfgActual_Work)

        print_df(df_final_result, 'df_final_result')
        step('=====> STEP4 End')
        ################################################################################################################
        # Step 5
        # df_in_ProductModel의 각 row별로 Prod Model_Tact Time Actual를 아래와 같이 구한다.
        # df_final_result['Mfg_Act_Mfg_Qty'] > 0 [Prod Model_Tact Time Actual] = round([Consume Capa] / [Mfg Act_Mfg Qty], 2)
        ################################################################################################################
        step('=====> STEP 5(Start) : df_in_ProductModel의 각 row별로 Prod Model_Tact Time Actual를 구한다.')

        df_final_result['Prod_Model_To_Inch_Actual'] = df_final_result['Prod_Model_To_Inch_Actual'].fillna(0).astype(
            'int64')
        df_final_result['Prod_Model_From_Inch_Actual'] = df_final_result['Prod_Model_From_Inch_Actual'].fillna(
            0).astype('int64')

        df_final_result['Prod Model_Tact Time Actual'] = np.where(
            df_final_result['Mfg_Act_Mfg_Qty'] > 0,
            round(df_final_result['Consume_Capa'] / df_final_result['Mfg_Act_Mfg_Qty'], 2),0
        )

        df_final_result['Prod Model_Tact Time Actual'] = df_final_result['Prod Model_Tact Time Actual'].fillna(0)

        df_final_result.rename(columns={
            'Prod_Model_To_Inch_Actual': 'Prod Model_To Inch Actual',
            'Prod_Model_From_Inch_Actual': 'Prod Model_From Inch Actual',
            'Mfg_Act_Mfg_Qty': 'Mfg Act_Mfg Qty'
        }, inplace=True)

        if VERSION_NAME_COLUMN not in df_final_result.columns:
            df_final_result.insert(0, VERSION_NAME_COLUMN, PARAM_OUTVERSION_VALUE)

        print_df(df_final_result, 'df_final_result')
        step('=====> STEP5 End')
        ################################################################################################################
        # STEP 6 : output table create
        ################################################################################################################
        step('=====> STEP6 : Final output table create')

        df_out_Prod_Model = df_final_result[
            [VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_MARKETING_NAME_COLUMN, SEQUENCE_COLUMN, DEFINITION_COLUMN,
             PRODUCT_GROUP_COLUMN,
             PROJECT_COLUMN, LINE_COLUMN, 'Prod Model_To Inch Actual', 'Prod Model_From Inch Actual',
             'Prod Model_Tact Time Actual']]

        df_out_Prod_Model = df_out_Prod_Model.replace({0: None})

        if is_local:
            step('=====> Output csv create')
            save_csv_file(df_out_Prod_Model, 'df_out_Prod_Model')

        print_df(df_out_Prod_Model, 'df_out_Prod_Model')
        step('=====> STEP6 End')
        step('==============================================')
        step('==============================================')
        step('==============================================')

    except Exception as e:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        df_out_Prod_Model = pd.DataFrame([], columns=[])

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()