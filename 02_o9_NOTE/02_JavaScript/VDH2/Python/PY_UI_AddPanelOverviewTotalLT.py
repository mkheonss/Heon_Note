"""
* 프로그램명
    - PY_UI_AddPanelOverviewTotalLT

* 내용
    - ITEM이 완패널/LCM일 경우, 해당 GROUPID, PLANT별 MASTER 하단 SET TTL L/T (메저.[Add Panel Grp Mst_Total LT]
      ITEM이 오픈셀일 경우,  해당 GROUPID, PLANT별 MASTER 하단 MTRL TTL L/T (메저.[Add Panel Grp Mst_Mtrl Total LT])
     이므로 2개 메저의 값이 하나의 메저로 합쳐져야함 (메저.[Add Panel Overview_TTL LT])

* 변경이력
    - 2026.03.12 / 이숙영 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_addPanelGrpMst      : Select ([Version].[Version Name] * [Location].[Location] * [To Location].[To Location] * [Group].[Group ID] * [Item].[Item Stage].filter(#.Name in {"OPEN_CELL", "PANEL", "LCM"}) *[Item].[Item] * [Sub Location].[Sub Location] ) on row,
                                        ({Measure.[Add Panel Grp Mst_Mtrl Total LT], Measure.[Add Panel Grp Mst_Total LT]}) on column;
    - df_in_addPanelOverview    : Select ([Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Item].[Item] ) on row, ({Measure.[Add Panel Overview_TTL LT]}) on column;

    - df_in_addPanelSgstMst     : Select ([Version].[Version Name] * [Group].[Group ID] ) on row, ({Measure.[Add Panel Sgst Mst_SET Total LT]}) on column ;

    - df_in_timeWeek            : select (&MPHorizon);

* Flow Summary
    - STEP1.     BOD Prod Set 발췌 기준으로 Item Site Asn 조합
    - STEP2,3,4. Step1 기준으로 BOD List 조합하여 BOD Item 을 구성한다.
    - STEP5.     Step2, 3, 4와 BOD Item concat 한 목록 비교하여 BOD Item에 이미 존재한 데이터 기준 Measure Update
    - STEP6.     Step2, 3, 4와 BOD Item concat 한 목록 비교하여 BOD Item에 없는 데이터 신규 생성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_addPanelOverview
    - df_out_addPanelOverviewAsn

* 데이타 초기화
    - DELETE DATA FOR MODEL [Add Panel Overview] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};
    - DELETE DATA FOR MODEL [Add Panel Overview Asn] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_AddPanelOverviewTotalLT] for measures {[Add Panel Overview_TTL LT]} using scope (&CWVUI)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&CWVUI * [Location].[Location] * [Group].[Group ID] * [Item].[Item] ) on row, ({Measure.[Add Panel Overview_TTL LT]}) on column limit 100;
    - Select (&CWVUI * &MPHorizon * [Group].[Group ID] ) on row, ({Measure.[Add Panel Overview Asn_Asn]}) on column limit 100;
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
str_instance = 'PY_UI_AddPanelOverviewTotalLT'
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
            df_in_addPanelGrpMst = read_csv_file("df_in_addPanelGrpMst")
            df_in_addPanelOverview = read_csv_file("df_in_addPanelOverview")
            df_in_addPanelSgstMst = read_csv_file("df_in_addPanelSgstMst")
            df_in_timeWeek = read_csv_file("df_in_timeWeek")

        dataframes = {
            'df_in_addPanelGrpMst': df_in_addPanelGrpMst,
            'df_in_addPanelOverview': df_in_addPanelOverview,
            'df_in_addPanelSgstMst': df_in_addPanelSgstMst,
            'df_in_timeWeek': df_in_timeWeek,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VersionName = 'Version.[Version Name]'
        Location = 'Location.[Location]'
        ToLocation = 'To Location.[To Location]'
        SubLocation = 'Sub Location.[Sub Location]'
        GroupID = 'Group.[Group ID]'
        ItemStage = 'Item.[Item Stage]'
        Item = 'Item.[Item]'
        TimeWeek = 'Time.[Week]'

        # df_mst
        TotalLT = 'Add Panel Grp Mst_Total LT'
        Mtrl_TotalLT = 'Add Panel Grp Mst_Mtrl Total LT'

        # df_overview
        Overview_TTLLT = 'Add Panel Overview_TTL LT'

        #-----------------------------------------------------------------------------------#
        # df_sgstMst
        SetTotalLT = 'Add Panel Sgst Mst_SET Total LT'

        # df_overviewAsn
        OverviewAsn_Asn = 'Add Panel Overview Asn_Asn'
        # -----------------------------------------------------------------------------------#

        add_panel_grp_mst_cols = [
            Location, ToLocation, GroupID, ItemStage, Item, SubLocation,
            TotalLT, Mtrl_TotalLT,
        ]

        add_panel_overview_cols = [
            Location, GroupID, Item,
            Overview_TTLLT,
        ]

        add_panel_sgst_mst_cols = [
            GroupID,
            SetTotalLT,
        ]

        add_panel_overview_asn_cols = [
            TimeWeek,
            GroupID,
            OverviewAsn_Asn,
        ]

        # Add Panel Grp Mst : Grain
        add_panel_grp_mst_final_cols = [VersionName] + add_panel_grp_mst_cols

        # Add Panel Overview : Grain
        add_panel_overview_final_cols = [VersionName] + add_panel_overview_cols

        # Add Panel Sgst Mst : Grain
        add_panel_sgst_mst_final_cols = [VersionName] + add_panel_sgst_mst_cols

        # Add Panel Overview Asn : Grain
        add_panel_overview_asn_final_cols = [VersionName] + add_panel_overview_asn_cols

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_addPanelGrpMst.empty:
            raise CustomException("STEP3 by 0 ____ df_in_addPanelGrpMst  값이 없습니다.")

        if df_in_addPanelOverview.empty:
            raise CustomException("STEP3 by 0 ____ df_in_addPanelOverview  값이 없습니다.")

        if df_in_addPanelSgstMst.empty:
            raise CustomException("STEP3 by 0 ____ df_in_addPanelSgstMst  값이 없습니다.")

        if df_in_timeWeek.empty:
            raise CustomException("STEP3 by 0 ____ df_in_timeWeek  값이 없습니다.")

        # 현재 날짜 시간
        # current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        step(f'=====> current_date : {current_date}')

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 : df_mst MG 데이터를 이용해서 df_overview MG Overview_TTLLT 값을 계산한 뒤,
        #          df_overview 기준으로만 결과를 남기는 함수.
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        def build_over_ttl(df_mst:pd.DataFrame, df_overview:pd.DataFrame) -> pd.DataFrame:

            """

            :param df_mst:
            :param df_overview:
            :return:

            df_mst MG 데이터를 이용해서 df_overview MG Overview_TTLLT 값을 계산한 뒤,
            df_overview 기준으로만 결과를 남기는 함수.
            -------------------------------------------------------------------
            [입력 그레인]
            df_mst : [Version].[Version Name] * [Location].[Location] * [To Location].[To Location] * [Group].[Group ID] * [Item].[Item] * [Sub Location].[Sub Location]
            df_overview : [Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Item].[Item]

            [조건]
            - ITEM이 완패널/LCM일 경우 : ItemStage == 'LCM','PANEL' 인 경우 -> Add Panel Grp Mst_Total LT 값을 사용 (TotalLT)
            - ITEM이 오픈셀일 경우     : ItemStage == 'OPEN_CELL'   인 경우 -> Add Panel Grp Mst_Mtrl Total LT 값을 사용 (Mtrl_TotalLT)

            [집계]
            - df_overview 그레인(VersionName, Location, GroupID, Item) 기준으로 MAX 집계

            [출력]
            - df_overview 기준 inner merge 결과만 반환
            - 따라서 df_mst에만 있고 df_overview에 없는 데이터는 결과에서 제외 됨.

            -------------------------------------------------------------------
            :parameters
            ---------------
            df_mst : pd.DataFrame
                df_mst MG 조회 결과 DataFrame
                 필수 컬럼 :
                 - VersionName
                 - Location
                 - GroupID
                 - Item
                 - ItemStage
                 - TotalLT (LCM,PANEL)
                 - Mtrl_TotalLT (OPEN_CELL)

                 참고 :
                 - df_mst 그레인에 ToLocation, SubLocation 이 있더라도 이 함수에서는 사용하지 않음
                 - 최종 집계 기준의 df_overview 그레인이므로 ToLocation, SubLocation 은 제거됨

            df_overview : pd.DataFrame
                df_overview MG 조회 결과 DataFrame
                필수 컬럼 :
                - VersionName
                - Location
                - GroupID
                - Item
                참고 :
                 - df_overview 에 다른 컬럼이 더 있어도 무방함
                 - 결과는 df_overview 의 컬럼 + 계산된 Overview_TTLLT 컬럼 형태가 됨

            Returns
            -------
            pd.DataFrame
                B 기준 결과 DataFrame

                기본 결과 컬럼 예:
                - VersionName
                - Location
                - Group ID
                - Item
                - Overview_TTLLT

                단, df_overview 에 다른 컬럼이 있으면 그 컬럼도 같이 유지 됨.

            """

            ############################################################################################################
            # 1. 입력 컬럼 검증
            ############################################################################################################
            # 필수 컬럼이 없는 상태로 실행되면 나중에 KeyError가 발생해서
            # 원인 파악이 어려워지므로, 초기에 명확하게 체크해준다.
            step('=====> STEP4-1 Start : 1.입력 컬럼 검증----------------------------')

            required_mst_cols = {
                VersionName,Location, ToLocation, GroupID, ItemStage, Item, SubLocation,
                TotalLT, Mtrl_TotalLT,
            }

            required_over_cols = {
                VersionName, Location, GroupID, Item,
                Overview_TTLLT,
            }

            missing_a = required_mst_cols - set(df_mst.columns)
            missing_b = required_over_cols - set(df_overview.columns)

            if missing_a:
                raise ValueError(f"df_mst에 필수 컬럼이 없습니다.: {sorted(missing_a)}")

            if missing_b:
                raise ValueError(f"df_overview에 필수 컬럼이 없습니다.: {sorted(missing_b)}")

            ############################################################################################################
            # 2. Item.[Item Stage] 조건 필터
            ############################################################################################################
            # 성능 관점에서 중요한 포인트:
            # 전체 df_a에 대해 np.where로 새 컬럼을 만드는 것보다,
            # 필요한 조건(cell/lcm)만 먼저 잘라서 처리하는 것이 대용량에서 유리한 경우가 많다.

            step('=====> STEP4-2 Start : 2.Item.[Item Stage] 조건 필터----------------------------')
            # LCM / 완패널
            mask_lcm = df_mst[ItemStage].isin(["LCM", "PANEL"])
            # 오픈셀
            mask_openCell = df_mst[ItemStage].eq("OPEN_CELL")

            ############################################################################################################
            # 3. 완패털/LCM 케이스 : TotalLT -> Overview_TTLLT 로 변환
            ############################################################################################################
            step('=====> STEP4-3 Start : 3.완패털/LCM 케이스 : TotalLT -> Overview_TTLLT 로 변환-----------------------')
            df_lcm = df_mst.loc[
                mask_lcm,
                [VersionName, Location, GroupID, Item, TotalLT]
                ].rename(
                    columns={TotalLT: Overview_TTLLT}
                )

            ############################################################################################################
            # 4. opencell 케이스 : Mtrl_TotalLT -> Overview_TTLLT 로 변환
            ############################################################################################################
            step('=====> STEP4-4 Start : 4.완패털/LCM 케이스 : TotalLT -> Overview_TTLLT 로 변환-----------------------')
            df_openCell = df_mst.loc[
                    mask_openCell,
                    [VersionName, Location, GroupID, Item, Mtrl_TotalLT]
                ].rename(
                    columns={Mtrl_TotalLT: Overview_TTLLT}
                )

            ############################################################################################################
            # 5. 오픈셀 / (lcm,완패널) 결과를 하나로 합침
            ############################################################################################################
            # 이 시점의 df_src는 이미 df_overview 그레인 집계에 필요한 형태로 단순화한 상태다.
            # 컬럼 구조는 다음과 같음:
            # ver, loc, group id, item, over_ttl
            step('=====> STEP4-5 Start : 5.오픈셀 / (lcm,완패널) 결과를 하나로 합침-----------------------')
            df_src = pd.concat([df_openCell, df_lcm], ignore_index=True)

            ############################################################################################################
            # 6. Overview_TTLLT 값이 없는 행 제거 (null 제거)
            ############################################################################################################
            # TotalLT 또는 Mtrl_TotalLT null일 수 있으므로,
            # 실제 집계에 의미 없는 행은 미리 제거한다.
            # 이 단계가 있으면 groupby 대상 행 수가 줄어들어 성능에도 도움된다.
            step('=====> STEP4-6 Start : 6.Overview_TTLLT 값이 없는 행 제거 (null 제거)-----------------------')
            df_src = df_src[df_src[Overview_TTLLT].notna()]

            ############################################################################################################
            # 7. df_mst 데이터를 df_overview 그레인으로 MAX 집계
            ############################################################################################################
            # df_mst MG는 원래 ToLocation, SubLocation 가 더 있는 구조이므로,
            # 같은 (VerionName, Location, GroupID, Item)에 대해 여러 row가 존재할 수 있다.
            # 요구사항에 따라 최종 집계는 MAX 사용,
            # sort=Fals:
            #   groupby시 정렬 비용을 줄이기 위해 사용
            # as_index=False:
            #   결과를 일반 DataFrame 형태로 유지
            step('=====> STEP4-7 Start : 7.df_mst 데이터를 df_overview 그레인으로 MAX 집계-----------------------')
            df_agg = (
                df_src
                .groupby([VersionName, Location, GroupID, Item], sort=False, as_index=False)[Overview_TTLLT]
                .max()
            )
            print_df(df_agg, 'STEP5 by 4.7  ____ df_agg')

            ############################################################################################################
            # 8. df_overview 기준으로만 결과를 남기기 위해 inner meerge
            ############################################################################################################
            # 요구사항:
            #   "ds_mst 는 있고 df_overview 에 없으면 output frame 없음"
            # 따라서 df_overview 를 기준으로 inner merge 한다.
            # 그러면:
            #   - df_overview 에도 있고 df_mst 집계 결과도 있는 것만 남음
            #   - df_mst 에만 있는 건 자동으로 제거됨
            # 결과는 df_overview 의 컬럼 + Overview_TTLLT 형태가 된다.
            step('=====> STEP4-8 Start : 8.df_overview 기준으로만 결과를 남기기 위해 inner meerge---------------------')
            df_overview.drop(columns=[Overview_TTLLT], inplace=True)

            print_df(df_overview, 'STEP5 by 4.8  ____ df_overview 이전')
            df_out = df_overview.merge(
                df_agg,
                on=[VersionName, Location, GroupID, Item],
                how="inner"
            )

            ############################################################################################################
            # 9. 결과 반환
            ############################################################################################################
            step('=====> STEP4-9 Start : 9.결과 반환---------------------')
            return df_out

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP4 Start : ######################## overview TTL LT 계산 함수 시작 ##########################')
        df_out_addPanelOverview = build_over_ttl(df_in_addPanelGrpMst, df_in_addPanelOverview)
        step('=====> STEP4 Start : ######################## overview TTL LT 계산 함수 종료 ##########################')

        step('=====> STEP5 Start : Final output table create')
        print_df(df_out_addPanelOverview, 'STEP5 by 5.1  ____ df_out_addPanelOverview')

        ################################################################################################################
        ################################################################################################################
        def build_overView_asn(df_sgstMst:pd.DataFrame, df_week:pd.DataFrame) -> pd.DataFrame:

            """
            df_sgstMst 와 df_week 를 이용해서 df_out_asn 업로드용 output DataFrame을 생성한다.
            :param df_sgstMst:
            :param df_week:
            :return:

            [입력]
            df_sgstMst : VersionName, GroupID, SetTotalLT
            df_week    : TimeWeek

            [출력]
            df_out_asn : VersionName, TimeWeek, GroupID, OverviewAsn_Asn
            
            [규칙]
            - SetTotalLT 값 만큼 df_week 의 week 를 앞에서 부터 생성
            - 생성되는 모든 row 의 asn = 1
            - SetTotalLT <= 0 이거나 null 이면 생성하지 않음
            - SetTotalLT 가 df_week 개수보다 크면 df_week 의 최대 개수까지만 생성 (&MPHorizon)

            ------------------------------------------------------------------------------------------------------------
            Parameters
            -----------------
            df_sgstMst : pd.DataFrame
                Add Panel Sgst Mst 조회 결과

                필수 컬럼:
                - VersionName, GroupID, SetTotalLT

            df_week : pd.DataFrame
                &MPHorizon 조회 결과

                필수 컬럼:
                - TimeWeek

            Returns
            -----------------
            pd.DataFrame
                df_out_asn 업로드용 결과 DataFrame

                컬럼 :
                - VersionName
                - TimeWeek
                - GroupID
                - OverviewAsn_Asn

            """
            ############################################################################################################
            # 1. 입력 컬럼 검증
            ############################################################################################################
            # 나중에 KeyError로 애매하게 터지지 않도록.
            # 처음부터 필요한 컬럼이 있는지 명확하게 체크한다.

            step('=====> start 1')

            required_sgstMst = {VersionName, GroupID, SetTotalLT}
            required_week = {TimeWeek}

            missing_sgstMst = required_sgstMst - set(df_sgstMst.columns)
            missing_week = required_week - set(df_week.columns)

            if missing_sgstMst:
                raise ValueError(f"df_sgstMst 에 필수 컬럼이 없습니다.: {sorted(missing_sgstMst)}")

            if missing_week:
                raise ValueError(f"df_week 에 필수 컬럼이 없습니다.: {sorted(missing_week)}")

            ############################################################################################################
            # 2. df_sgstMst 에서 필요한 컬럼만 복사
            ############################################################################################################
            # 불필요한 컬럼을 최대한 제거해서 메모리 사용을 줄인다.
            step('=====> start 2')
            df_sgstMst_copy = df_sgstMst[[VersionName, GroupID, SetTotalLT]].copy()

            ############################################################################################################
            # 3. SetTotalLT 을 숫자형으로 변환
            ############################################################################################################
            # 문자열, null, 비정상값 등이 들어올 수 있으므로 숫자형으로 강제 변환
            # 변호나 불가능한 값은 NaN 으로 처리
            step('=====> start 3')
            df_sgstMst_copy[SetTotalLT] = pd.to_numeric(df_sgstMst_copy[SetTotalLT], errors="coerce")

            ############################################################################################################
            # 4. 생성 대상만 남기기
            ############################################################################################################
            # SetTotalLT 가 null 이거나, 0 이하라면 생성 대상이 아니므로 제외
            step('=====> start 4')
            df_sgstMst_copy = df_sgstMst_copy[df_sgstMst_copy[SetTotalLT].notna() & (df_sgstMst_copy[SetTotalLT] >0)].copy()

            # SetTotalLT 를 정수형으로 변환
            # 예: 3.0 -> 3
            df_sgstMst_copy[SetTotalLT] = df_sgstMst_copy[SetTotalLT].astype(int)

            # 만약 생성 대상이 하나도 없으면 빈 DataFrame 반환
            if df_sgstMst_copy.empty:
                return pd.DataFrame(columns=[VersionName, TimeWeek, GroupID, OverviewAsn_Asn])

            ############################################################################################################
            # 5. ds_week 에서 TimeWeek 만 가져와 정렬
            ############################################################################################################
            d = df_week[[TimeWeek]].copy()
            # week 가 숫자처럼 보이는 문자열일 수도 있으므로 정렬용 보조컬럼 생성
            d['week_sort'] = pd.to_numeric(d[TimeWeek], errors="coerce")

            # week 순서대로 정렬
            # week_sort 우선, 같은 값이면 원래 week 기준 안정 정렬
            d = d.sort_values(['week_sort', TimeWeek], kind='stable').reset_index(drop=True)

            # week 순번 부여
            d['week_seq'] = np.arange(1, len(d) + 1)

            # D 가 비어 있으면 생성할 주차가 없으므로 빈 결과 반환
            if d.empty:
                return pd.DataFrame(columns=[VersionName, TimeWeek, GroupID, OverviewAsn_Asn])

            ############################################################################################################
            # 6. SetTotalLT 최대값을 df_week 개수로 제한
            ############################################################################################################
            # 예:
            # df_week week 가 6개인데 SetTotalLT=10 이면 10개 생성할 수 없으므로 6까지만 생성
            step('=====> start 6')
            max_week_cnt = len(d)
            df_sgstMst_copy[SetTotalLT] = np.minimum(df_sgstMst_copy[SetTotalLT], max_week_cnt)

            ############################################################################################################
            # 7. repeat / concatenate 방식으로 필요한 행만 생성
            ############################################################################################################
            # full cross join ( C * D 전체 생성) 을 하면 데이터가 불필요하게 커질 수 있으므로,
            # SetTotalLT 합계 만큼만 row를 생성한다.
            # 예:
            # GroupID TotalLt=3 -> 3행
            # GroupID TotalLt=5 -> 5행
            # 총 8행 생성
            repeats = df_sgstMst_copy[SetTotalLT].to_numpy()
            total_rows = repeats.sum()

            # VersionName 을 SetTotalLT 개수만큼 반복
            # 예:
            # ver1, SetTotalLT=3 -> ver1 3번
            out_ver = np.repeat(df_sgstMst_copy[VersionName].to_numpy(), repeats)
            # GroupID 를 SetTotalLT 개수만큼 반복
            out_groupid = np.repeat(df_sgstMst_copy[GroupID].to_numpy(), repeats)

            # 각 df_sgstMst_copy row 마다 week_seq를 1 - SetTotalLT 까지 생성
            # 예:
            # SetTotalLT =3 -> [1,2,3]
            # SetTotalLT =5 -> [1,2,3,4,5]
            # 전체를 하나로 합치면:
            # [1,2,3, 1,2,3,4,5, ...]
            out_week_seq = np.concatenate([np.arange(1, n+1) for n in repeats])

            ############################################################################################################
            # 8. week_seq 를 실제 week 값으로 변환
            ############################################################################################################
            # week_seq=1 -> 첫번째 week(예:202608)
            # week_seq=2 -> 두번째 week(예:202609)
            step('=====> start 8')
            week_map = d.set_index("week_seq")[TimeWeek]

            out_week = week_map.loc[out_week_seq].to_numpy()

            ############################################################################################################
            # 9. asn 값 생성
            ############################################################################################################
            # 규칙상 생성되는 모든 row의 asn=1
            step('=====> start 9')
            out_asn = np.ones(total_rows,dtype=int)

            ############################################################################################################
            # 10. 최종 E output DataFrame 생성
            ############################################################################################################
            step('=====> start 10')
            df_e = pd.DataFrame({
                VersionName: out_ver,
                TimeWeek: out_week,
                GroupID: out_groupid,
                OverviewAsn_Asn: out_asn
            })

            ############################################################################################################
            # 11. 중복 제거 (필요시)
            ############################################################################################################
            # 일반적으로는 중복이 없어야 하지만,
            # 혹시 입력 데이터 이상으로 같은 Key 가 중복 생성될 가능성을 대비해 제거 할 수 있다.
            # 필요 없으면 이 줄은 주석처리해도 됨.
            step('=====> start 11')
            df_e = df_e.drop_duplicates([VersionName, TimeWeek, GroupID])

            ############################################################################################################
            # 12. 컬럼 순서 정의
            ############################################################################################################
            step('=====> start 12')
            df_e = df_e[[VersionName, TimeWeek, GroupID, OverviewAsn_Asn]]

            return df_e

        ################################################################################################################

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP4 Start : ######################## SET Total LT 에 따른 Week Asn 생성 시작 ##########################')
        df_out_addPanelOverviewAsn = build_overView_asn(df_in_addPanelSgstMst, df_in_timeWeek)
        step('=====> STEP4 Start : ######################## SET Total LT 에 따른 Week Asn 생성 종료 ##########################')

        dataframes = {
            'df_out_addPanelOverview': df_out_addPanelOverview,
            'df_out_addPanelOverviewAsn': df_out_addPanelOverviewAsn,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_addPanelOverview = pd.DataFrame(columns=add_panel_overview_final_cols)
        df_out_addPanelOverviewAsn = pd.DataFrame(columns=add_panel_overview_asn_final_cols)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_addPanelOverview = pd.DataFrame(columns=add_panel_overview_final_cols)
        df_out_addPanelOverviewAsn = pd.DataFrame(columns=add_panel_overview_asn_final_cols)
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
