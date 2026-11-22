"""
* 프로그램명
    - PY_UI_ECPMaster_Init

* 내용
    - ECP Master UI에 값을 채워주는 Logic

* 변경이력
    - 2025.12.17 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_DimMtrl     : Select ([Item Material].[Item Material] * [Item Material].[MSL3]) on row;
    - df_in_ItemSiteAss : Select ([Item].[Item] * [Location].[Site Stage].filter(#.Name in {"MF", "MF_SET"}).relatedmembers([Location]).filter(#.[Location Valid Flag] == True)) on row, ({Measure.[Item Site Asn_Actual Flag], Measure.[Dummy]}) on column where {[Version].[Version Name], Measure.[Item Site Asn_Cur Status] in {"ACTIVE", "PLANNED"}};

* Flow Summary
    - STEP1. Item Material과 Item Site Association을 이용해 대응되는 Item Material과 Location 결합.
    - STEP2. MSL3, Location 기준으로 중복되는 열 제거
    - STEP3. ECP Flag = 'N'와 Air LT = 0로 초기화
    - STEP4. Copy 후 필드 제거, ECP Mst Popup 생성
    - STEP5. Copy 후 필드 제거, ECP Master Mail Mgmt 생성

* Output Table
    - df_out_log
    - df_out_logDetail
    - df_out_ECP_Mst_Lv3
    - df_out_ECP_Mst_LT
    - df_out_ECP_Mst_Mail

* 데이타 초기화
    - DELETE DATA FOR MODEL [ECP Master Lv3] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};
    - DELETE DATA FOR MODEL [ECP Master Popup] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};
    - DELETE DATA FOR MODEL [ECP Master Mail Mgmt] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_ECPMaster_Init] for measures {[ECP Mst Lv3_ECP Flag]} using scope ([Version].[Version Name].[CWV_MP])
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Location].[Location] * [Item Material].[MSL3] ) on row, ({Measure.[ECP Mst Lv3_Air LT], Measure.[ECP Mst Lv3_ECP Flag] }) on column;
    - Select (&MPV * [Location].[Location] ) on row, ({Measure.[ECP Mst Pop_ECP LT]}) on column;
    - Select (&MPV * [Location].[Location] * [Seq].[Seq] ) on row, ({Measure.[ECP Mst Mail Mgmt_Category]}) on column;

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
str_instance = 'PY_UI_ECPMaster_Init'
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
            df_in_DimMtrl = read_csv_file("df_in_DimMtrl")
            df_in_ItemSiteAss = read_csv_file("df_in_ItemSiteAss")


        dataframes = {
            'df_in_DimMtrl': df_in_DimMtrl,
            'df_in_ItemSiteAss': df_in_ItemSiteAss,
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
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        MSL3_COLUMN = 'Item Material.[MSL3]'
        SEQ_COLUMN = 'Seq.[Seq]'

        ITEM_SITE_ASN_CREATED_BY_COLUMN = 'Item Site Asn_Created By'
        ITEM_SITE_ASN_CREATION_TIME_COLUMN = 'Item Site Asn_Creation Time'
        ITEM_SITE_ASN_DCF_INTREACT_EXPLOSION_COLUMN = 'Item Site Asn_Daily Change Flag_Interact Explosion'

        ECP_MST_LV3_AIR_LT_COLUMN = 'ECP Mst Lv3_Air LT'
        ECP_MST_LV3_ECP_FLAG_COLUMN = 'ECP Mst Lv3_ECP Flag'
        ECP_MST_POP_ECP_LT_COLUMN = 'ECP Mst Pop_ECP LT'
        ECP_MST_MAIL_MGMT_CATEGORY_COLUMN = 'ECP Mst Mail Mgmt_Category'

        version_columns = [VERSION_NAME_COLUMN]
        key_columns = [LOCATION_COLUMN, MSL3_COLUMN]
        key_columns1 = [LOCATION_COLUMN]
        key_columns2 = [LOCATION_COLUMN, SEQ_COLUMN]

        ecp_mst_lv3_columns = [
            ECP_MST_LV3_AIR_LT_COLUMN, ECP_MST_LV3_ECP_FLAG_COLUMN,
        ]

        ecp_mst_lt_column = [ECP_MST_POP_ECP_LT_COLUMN]

        ecp_mst_mail_column = [ECP_MST_MAIL_MGMT_CATEGORY_COLUMN]

        fn_ecp_mst_lv3_columns = version_columns + key_columns + ecp_mst_lv3_columns
        fn_ecp_mst_lt_column = version_columns + key_columns1 + ecp_mst_lt_column
        fn_ecp_mst_mail_column = version_columns + key_columns2 + ecp_mst_mail_column

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
        if df_in_ItemSiteAss.empty:
            raise CustomException("STEP3 by 0 ____ df_in_ItemSiteAss 값이 없습니다.")


        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : df_in_ItemSiteAss을 기준으로 Item에 따라 df_in_DimMtrl의 MSL3을 Merge.')
        df_ItemSiteAss = pd.merge(df_in_ItemSiteAss, df_in_DimMtrl, how='inner',
                                  left_on=[ITEM_COLUMN],
                                  right_on=[ITEM_METERIAL_COLUMN])
        print_df(df_ItemSiteAss, 'STEP4 by 1.1  ____ df_ItemSiteAss .... merge')
        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : df_ItemSiteAss 에서 MSL3이 Null인 값을 제거, 불필요 컬럼 제거')
        df_ItemSiteAss = df_ItemSiteAss[df_ItemSiteAss[MSL3_COLUMN].notna()]
        df_ItemSiteAss.drop(columns=[
            ITEM_COLUMN, ITEM_METERIAL_COLUMN,
        ], inplace=True)
        df_ItemSiteAss = df_ItemSiteAss.drop_duplicates().reset_index(drop=True)
        print_df(df_ItemSiteAss, 'STEP4 by 2.1  ____ df_ItemSiteAss .... column drop')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : df_ItemSiteAss 에서 모든 row에 다음 두 필드를 추가(항상 0 값을 갖는 [ECP Mst Lv3_Air LT], 항상 N 값을 갖는 [ECP Mst Lv3_ECP Flag]')
        df_ItemSiteAss[ECP_MST_LV3_AIR_LT_COLUMN] = 0
        df_ItemSiteAss[ECP_MST_LV3_ECP_FLAG_COLUMN] = 'N'
        print_df(df_ItemSiteAss, 'STEP4 by 3.1  ____ df_ItemSiteAss .... column add')
        step('=====> STEP4 by 3 End')



        step('=====> STEP4 by 4 Start : df_ItemSiteAss를 copy한 후 항상 0 값을 갖는 필드 [ECP Mst Pop_ECP LT] 추가. 불필요 컬럼 제거. 중복 row 제거')
        df_ECP_Mst_LT = df_ItemSiteAss.copy()
        df_ECP_Mst_LT[ECP_MST_POP_ECP_LT_COLUMN] = 0

        df_ECP_Mst_LT.drop(columns=[
            MSL3_COLUMN, ECP_MST_LV3_AIR_LT_COLUMN, ECP_MST_LV3_ECP_FLAG_COLUMN,
        ], inplace=True)

        df_ECP_Mst_LT = df_ECP_Mst_LT.drop_duplicates().reset_index(drop=True)

        print_df(df_ECP_Mst_LT, 'STEP4 by 4  ____ df_ECP_Mst_LT .... create')
        step('=====> STEP4 by 4 End')




        step('=====> STEP4 by 5 Start : df_ItemSiteAss를 copy한 후 항상 Default 값을 갖는 필드 [ECP Mst Mail Mgmt_Category] 추가. 불필요 컬럼 제거. 중복 row 제거')
        df_ECP_Mst_Mail = df_ItemSiteAss.copy()
        df_ECP_Mst_Mail[ECP_MST_MAIL_MGMT_CATEGORY_COLUMN] = 'Default'
        df_ECP_Mst_Mail[SEQ_COLUMN] = 1

        df_ECP_Mst_Mail.drop(columns=[
            MSL3_COLUMN, ECP_MST_LV3_AIR_LT_COLUMN, ECP_MST_LV3_ECP_FLAG_COLUMN,
        ], inplace=True)

        df_ECP_Mst_Mail = df_ECP_Mst_Mail.drop_duplicates().reset_index(drop=True)

        print_df(df_ECP_Mst_Mail, 'STEP4 by 5  ____ df_ECP_Mst_Mail_Mgmt .... create')
        step('=====> STEP4 by 5 End')


        step('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_ECP_Mst_Lv3 = rename_and_delete_df(df_ItemSiteAss)

        df_out_ECP_Mst_Lv3[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ECP_Mst_Lv3 = df_out_ECP_Mst_Lv3[fn_ecp_mst_lv3_columns]
        df_out_ECP_Mst_Lv3 = df_out_ECP_Mst_Lv3.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        df_out_ECP_Mst_LT = rename_and_delete_df(df_ECP_Mst_LT)
        df_out_ECP_Mst_LT[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ECP_Mst_LT = df_out_ECP_Mst_LT[fn_ecp_mst_lt_column]

        df_out_ECP_Mst_Mail = rename_and_delete_df(df_ECP_Mst_Mail)
        df_out_ECP_Mst_Mail[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ECP_Mst_Mail = df_out_ECP_Mst_Mail[fn_ecp_mst_mail_column]

        dataframes = {
            'df_out_ECP_Mst_Lv3': df_out_ECP_Mst_Lv3,
            'df_out_ECP_Mst_LT': df_out_ECP_Mst_LT,
            'df_out_ECP_Mst_Mail': df_out_ECP_Mst_Mail,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ECP_Mst_Lv3 = pd.DataFrame(columns=fn_ecp_mst_lv3_columns)
        df_out_ECP_Mst_LT = pd.DataFrame(columns=fn_ecp_mst_lt_column)
        df_out_ECP_Mst_Mail = pd.DataFrame(columns=fn_ecp_mst_mail_column)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ECP_Mst_Lv3 = pd.DataFrame(columns=fn_ecp_mst_lv3_columns)
        df_out_ECP_Mst_LT = pd.DataFrame(columns=fn_ecp_mst_lt_column)
        df_out_ECP_Mst_Mail = pd.DataFrame(columns=fn_ecp_mst_mail_column)
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
