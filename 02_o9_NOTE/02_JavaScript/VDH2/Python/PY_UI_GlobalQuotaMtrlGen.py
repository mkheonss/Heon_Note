"""
* 프로그램명
    - PY_UI_GlobalQuotaMtrlGen

* 내용
    -

* 변경이력
    - 2026.02.05 / 권태우 / Re-Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_dualmtrlanl      : Select ([Group].[Group ID] * [Item Material].[Item Material] * [Item Material].[Represent Vendor]) on row, ({Measure.[Dual Mtrl Anl Mst_Flag]}) on column where {[Version].[Version Name], [Category].[Category].[Dualized Mtrl Group-Master], [Sub Location].[Sub Location], [Item].[Item], [Location].[Location]};
    - df_in_globalquotamtrlw : Select ([Group].[Group ID] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * &MPHorizon ) on row, ({Measure.[Global Quota Mtrl W_Portion]}) on column where {[Version].[Version Name]};
    - df_in_globalquotamtrl  : Select ([Group].[Group ID] * [Sub Location].[Sub Location] * [Item Material].[Item Material] ) on row, ({Measure.[Global Quota Mtrl_ASN], Measure.[Global Quota Mtrl_InterdepenF], Measure.[Global Quota Mtrl_Plant Mgmt Flag], Measure.[Global Quota Mtrl_Status], Measure.[Global Quota Mtrl_Validation]}) on column where {[Version].[Version Name]};
    - df_in_globalquotamtrlsub : Select ([Group].[Group ID] ) on row, ({Measure.[Global Quota Mtrl Sub_Group Name]}) on column where {[Version].[Version Name]};
    - df_in_planHorizon      : Select (&MDMHorizon);

* Flow Summary
    - STEP1.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out
    - df_out2
    - df_out3

    - df_out_globalquotamtrlw
    - df_out_globalquotamtrlsub
    - df_out_globalquotamtrl

* 데이타 초기화
    - DELETE DATA FOR MODEL [Global Quota Mtrl W] where{[Version].[Version Name].filter(#.Name == "CWV_MP")};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_GlobalQuotaMtrlGen] for measures {[Global Quota Mtrl W_Portion]} using scope ([Version].[Version Name].[CWV_MP])
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
str_instance = 'PY_UI_GlobalQuotaMtrlGen'
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
            df_in_dualmtrlanl = read_csv_file("df_in_dualmtrlanl")
            df_in_globalquotamtrlw = read_csv_file("df_in_globalquotamtrlw")
            df_in_globalquotamtrl = read_csv_file("df_in_globalquotamtrl")
            df_in_globalquotamtrlsub = read_csv_file("df_in_globalquotamtrlsub")
            df_in_planHorizon = read_csv_file("df_in_planHorizon")

        dataframes = {
            'df_in_dualmtrlanl': df_in_dualmtrlanl,
            'df_in_globalquotamtrlw': df_in_globalquotamtrlw,
            'df_in_globalquotamtrl': df_in_globalquotamtrl,
            'df_in_globalquotamtrlsub': df_in_globalquotamtrlsub,
            'df_in_planHorizon': df_in_planHorizon,
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
        TIME_WEEK_COLUMN = 'Time.[Week]'
        EXIST_FLAG_COLUMN = 'Exist Flag'
        
        ITEM_MATERIAL_REPRESENT_VENDOR_COLUMN = 'Item Material.[Represent Vendor]'
        GLOBAL_QUOTA_MTRL_W_PORTION_COLUMN = 'Global Quota Mtrl W_Portion'
        GLOBAL_QUOTA_MTRL_STATUS_COLUMN = 'Global Quota Mtrl_Status'
        GLOBAL_QUOTA_MTRL_SUB_GROUP_NAME_COLUMN = 'Global Quota Mtrl Sub_Group Name'
        
        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start

        # df_in_dualmtrlanl = df_in_dualmtrlanl[df_in_dualmtrlanl[ITEM_METERIAL_COLUMN] == 'BN44-01330B']
        # print_df(df_in_BODProdSET, 'STEP3 by 1.1  ____ df_in_BODProdSET .... filter', True)
        # df_in_BODProdSET = df_in_BODProdSET[df_in_BODProdSET[SUB_LOCATION_COLUMN] == 'L5N0']

        # ------------------ 테스트 디버깅용 ------------------ end



        df_in_planHorizon = (
            df_in_planHorizon[[TIME_WEEK_COLUMN]]
            .drop_duplicates()
            .sort_values(TIME_WEEK_COLUMN)  # 오름차순
            .reset_index(drop=True)
        )
        df_in_planHorizon[TIME_WEEK_COLUMN] = df_in_planHorizon[TIME_WEEK_COLUMN].astype(int)
        df_in_planHorizon["Key"] = "Key"
        print_df(df_in_planHorizon, 'STEP3 by 1.1  ____ df_in_planHorizon .... sort')

        # Rename
        df_in_dualmtrlanl.rename(columns={ITEM_MATERIAL_REPRESENT_VENDOR_COLUMN: SUB_LOCATION_COLUMN}, inplace=True)
        print_df(df_in_dualmtrlanl, 'STEP3 by 1.2  ____ df_in_dualmtrlanl .... rename')


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # df_in_globalquotamtrlw 에서 Week 를 빼고 비교를 위한 데이타 생성
        df_work_globalquotamtrl = df_in_globalquotamtrlw[[GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN]].copy()
        df_work_globalquotamtrl = df_work_globalquotamtrl.drop_duplicates()

        df_work_globalquotamtrl[EXIST_FLAG_COLUMN] = "Y"
        print_df(df_work_globalquotamtrl, 'STEP4 by 1.1  ____ df_work_globalquotamtrl .... sort')

        # Merge
        df_in_dualmtrlanl = df_in_dualmtrlanl.merge(
            df_work_globalquotamtrl, how='left',
            on=[GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN]
        )
        print_df(df_in_dualmtrlanl, 'STEP4 by 1.2  ____ df_in_dualmtrlanl .... merge')

        # Step 1. Global Quota Mtrl W 에 등록되지 않은 데이타를 가져와서 Week 데이타 생성
        df_work1_dualmtrlanl = df_in_dualmtrlanl.loc[(df_in_dualmtrlanl[EXIST_FLAG_COLUMN].isna())].copy()
        print_df(df_work1_dualmtrlanl, 'STEP4 by 1.3  ____ df_work1_dualmtrlanl .... Exist Flag isna filter')

        # Time 와 Merge
        df_work1_dualmtrlanl["Key"] = "Key"
        df_work1_dualmtrlanl = df_work1_dualmtrlanl.merge(df_in_planHorizon, how='left', on=["Key"])
        print_df(df_work1_dualmtrlanl, 'STEP4 by 1.4  ____ df_work1_dualmtrlanl .... merge')

        # Step 2. Global Quota Mtrl W 에 등록된 데이타 가져와서 빠진 Week 데이타 생성
        df_work2_dualmtrlanl = df_in_dualmtrlanl.loc[(~df_in_dualmtrlanl[EXIST_FLAG_COLUMN].isna())].copy()
        print_df(df_work2_dualmtrlanl, 'STEP4 by 1.5  ____ df_work2_dualmtrlanl .... not Exist Flag isna filter')

        # Time 와 Merge
        df_work2_dualmtrlanl["Key"] = "Key"
        df_work2_dualmtrlanl = df_work2_dualmtrlanl.merge(df_in_planHorizon, how='left', on=["Key"])
        print_df(df_work2_dualmtrlanl, 'STEP4 by 1.6  ____ df_work2_dualmtrlanl .... merge')

        # 기존 데이타와 Merge 를 해서 없는 주만 가져온다.
        df_work2_dualmtrlanl = df_work2_dualmtrlanl.merge(
            df_in_globalquotamtrlw, how='left',
            on=[GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN]
        )
        df_work2_dualmtrlanl = df_work2_dualmtrlanl.loc[(df_work2_dualmtrlanl[GLOBAL_QUOTA_MTRL_W_PORTION_COLUMN].isna())].copy()
        print_df(df_work2_dualmtrlanl, 'STEP4 by 1.7  ____ df_work2_dualmtrlanl .... sort')


        # df_out_globalquotamtrlw create ...
        df_out_globalquotamtrlw = pd.concat([df_work1_dualmtrlanl, df_work2_dualmtrlanl], ignore_index=True)
        print_df(df_out_globalquotamtrlw, 'STEP4 by 1.8  ____ df_out_globalquotamtrlw .... create')


        # 2026.02.11 추가
        #   df_in_globalquotamtrl 을 기준으로보고, df_out_globalquotamtrlw 에 있는 조합을 빼고 .. 신규 조합을 생성
        df_globalquotamtrlw = df_out_globalquotamtrlw[[GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN]].copy().drop_duplicates()
        df_in_globalquotamtrl = df_in_globalquotamtrl[[GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN]].drop_duplicates()

        df_out_globalquotamtrlsub = df_globalquotamtrlw.merge(
            df_in_globalquotamtrl, how='left',
            on=[GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN],
            indicator=True
        )
        print_df(df_out_globalquotamtrlsub, 'STEP4 by 1.9.1  ____ df_out_globalquotamtrlsub .... merge')
        df_out_globalquotamtrlsub = df_out_globalquotamtrlsub[df_out_globalquotamtrlsub['_merge'] == 'left_only'].drop(columns=['_merge'])

        df_out_globalquotamtrlsub[GLOBAL_QUOTA_MTRL_STATUS_COLUMN] = "REQ (NEW)"
        print_df(df_out_globalquotamtrlsub, 'STEP4 by 1.9.2  ____ df_out_globalquotamtrlsub .... sort')



        # 2026.02.13 추가
        df_out_globalquotamtrlsub_filter = df_out_globalquotamtrlsub[[GROUP_ID_COLUMN]].copy().drop_duplicates()

        df_out_globalquotamtrl = df_out_globalquotamtrlsub_filter.merge(
            df_in_globalquotamtrlsub, how='left',
            on=[GROUP_ID_COLUMN],
            indicator=True
        )
        df_out_globalquotamtrl = df_out_globalquotamtrl[df_out_globalquotamtrl['_merge'] == 'left_only'].drop(columns=['_merge'])
        df_out_globalquotamtrl[GLOBAL_QUOTA_MTRL_SUB_GROUP_NAME_COLUMN] = "-"


        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_globalquotamtrlw[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_globalquotamtrlw[GLOBAL_QUOTA_MTRL_W_PORTION_COLUMN] = 0

        # out 생성
        df_out_globalquotamtrlw = df_out_globalquotamtrlw[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN,
            TIME_WEEK_COLUMN, GLOBAL_QUOTA_MTRL_W_PORTION_COLUMN,
        ]]
        df_out_globalquotamtrlw[TIME_WEEK_COLUMN] = df_out_globalquotamtrlw[TIME_WEEK_COLUMN].astype('Int64')

        df_out_globalquotamtrlsub[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_globalquotamtrlsub = df_out_globalquotamtrlsub[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN,
            GLOBAL_QUOTA_MTRL_STATUS_COLUMN,
        ]]

        df_out_globalquotamtrl[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_globalquotamtrl = df_out_globalquotamtrl[[
            VERSION_NAME_COLUMN, GROUP_ID_COLUMN, GLOBAL_QUOTA_MTRL_SUB_GROUP_NAME_COLUMN,
        ]]

        dataframes = {
            'df_out_globalquotamtrlw': df_out_globalquotamtrlw,
            'df_out_globalquotamtrlsub': df_out_globalquotamtrlsub,
            'df_out_globalquotamtrl': df_out_globalquotamtrl,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_globalquotamtrlw = pd.DataFrame([], columns=[])
        df_out_globalquotamtrlsub = pd.DataFrame([], columns=[])
        df_out_globalquotamtrl = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_globalquotamtrlw = pd.DataFrame([], columns=[])
        df_out_globalquotamtrlsub = pd.DataFrame([], columns=[])
        df_out_globalquotamtrl = pd.DataFrame([], columns=[])
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
