"""
* 프로그램명
    - PY_UI_BodList_Inherit_BodProdSet

* 내용
    - BOD List 의 데이터를 BOD Prod SET 에 데이터를 상속한다
    - df_in_BodList(Grain: versionName, Location, Sub Location, TP Mode) 의 MG 값들(BOD Lt, Shipment Lt, startDate, enddate, startWeek, endWeek) 을
       df_in_BodProdSet(Grain : versionName, Location, Sub Location, TP Mode, Item.Product Group) 의 (BOD Lt, Shipment Lt, startDate, enddate, startWeek, endWeek) 메저로 상속(덮어쓰기) 한다.
    - 상속 조건
      df_in_BodList 의 Measure.[BOD List_Product TV] / Measure.[BOD List_Product MNT] / Measure.[BOD List_Product AV] 플래그가 True인 경우에만,
      df_in_BodProdSet 의 [Item].[Product Group] ("TV"/"MONITOR"/"AV) 행에 매핑하여 내려준다.
    - 타입 Null 처리 원칙
      df_in_BodList 의 mg 값은 정수/날짜/문자 등 혼합 타입일 수 있다.
      df_in_BodList 의 mg 값이 모두 null 이여도 "그대로 null"을  df_in_BodProdSet 에 덮어 쓴다.(즉, 매칭되는 행이면 df_in_BodList 값을 그대로 복사 = 상속, 값이 NA 여도 넢어씀)
      df_in_BodProdSet 에서 (BOD Lt, Shipment Lt, startDate, enddate, startWeek, endWeek) 컬럼이 없으면 생성한다.
    - 전제
      df_in_BodList 은 (versionName, Location, Sub Location, TP Mode) Grain이 unique(중복 없음)
* 변경이력
    - 2026.02.10 / 이숙영 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_BodList     : Select ([Version].[Version Name] * &NSUILocationDC.unionwith(&MFStageSETLocation) * &NSUISubLocationDC * [Trans Mode].[Trans Mode] ) on row,
                        ({Measure.[BOD List_Product TV],Measure.[BOD List_Product MNT],Measure.[BOD List_Product AV],Measure.[BOD List_BOD LT],Measure.[BOD List_Shipment LT],Measure.[BOD List_Eff Startdate],Measure.[BOD List_Eff Enddate],Measure.[BOD List_Eff Startweek],Measure.[BOD List_Eff Endweek]}) on column;
    - df_in_BodProdSet     : Select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Item].[Product Group] * [Trans Mode].[Trans Mode] ) on row,
({Measure.[BOD Prod SET_BOD LT],Measure.[BOD Prod SET_Shipment LT],Measure.[BOD Prod SET_Eff Startdate],Measure.[BOD Prod SET_Eff Enddate],Measure.[BOD Prod SET_Eff Startweek],Measure.[BOD Prod SET_Eff Endweek],Measure.[Dummy]}) on column;

* Flow Summary
        1) df_in_BodList 타입 정리 (Null 안전)
        2) df_in_BodProdSet 타입 정리 + mg 컬럼 없으면 생성
        3) df_in_BodList -> df1_long (product_group Grain 으로 확장)
        4) merge 시 컬럼명 안정화 (중요)
        5)  df_in_BodProdSet + df1_long merge
        6)  상속(덮어쓰기) 로직 : "매칭되면 df_in_BodList 값으로 덮어쓰기(Null 포함)"
        7) 정리 : 보조 컬럼 제거
        8) dtype 재고정 (np.where가 object로 흔들 수 있음)
        결과 저장

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BodProdSet

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_BodList_Inherit_BodProdSet] for measures {[BOD Prod SET_BOD Valid]}
    using scope ( &CWVUI )
    using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
    - Select (&cwvui * &NSUILocationDC.unionwith(&MFStageSETLocation).filter(#.Name == "P306") * [Item].[Product Group] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
({Measure.[BOD Prod SET_BOD LT],Measure.[BOD Prod SET_Shipment LT],Measure.[BOD Prod SET_Eff Startdate],Measure.[BOD Prod SET_Eff Enddate],Measure.[BOD Prod SET_Eff Startweek],Measure.[BOD Prod SET_Eff Endweek],Measure.[Dummy]}) on column limit 100;

"""
# from __future__ import annotations
import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
from numba import njit
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BodList_Inherit_BodProdSet'
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


# def set_unique_combinations(df: pd.DataFrame,
#                             weeks_df: pd.DataFrame,
#                             columns: list[str]) -> pd.DataFrame:
#     """
#     df: 실제 데이터
#     weeks_df: TIME_WEEK_COLUMN 값(주차) 목록을 가진 데이터프레임(최소 TIME_WEEK_COLUMN 컬럼 필요)
#     columns: df에서 완전성 체크할 컬럼들 (TIME_WEEK_COLUMN 포함)
#     return: df에 존재하지 않는 (조합×주차) 행들
#     """
#     if TIME_WEEK_COLUMN not in columns:
#         raise ValueError(f"`columns`에는 {TIME_WEEK_COLUMN}가 포함되어야 합니다.")
#
#     dims = [c for c in columns if c != TIME_WEEK_COLUMN]
#
#     # dims 고유 조합 (관측된 조합만 유지)
#     unique_dims = df.loc[:, dims].drop_duplicates(ignore_index=True)
#
#     # 주차 고유값
#     weeks = (
#         weeks_df.loc[:, [TIME_WEEK_COLUMN]]
#                 .drop_duplicates()[TIME_WEEK_COLUMN]
#                 .to_numpy()
#     )
#
#     n = len(unique_dims)
#     m = len(weeks)
#
#     if n == 0 or m == 0:
#         return df.loc[:, columns].head(0).copy()
#
#     # (dims 고유조합) × (weeks) 전체 조합 생성
#     all_possible = unique_dims.loc[unique_dims.index.repeat(m)].reset_index(drop=True)
#     all_possible[TIME_WEEK_COLUMN] = np.tile(weeks, n)
#
#     # df에 실제 존재하는 조합
#     existing = df.loc[:, columns].drop_duplicates(ignore_index=True)
#
#     # anti-join: all_possible 중 df에 없는 것만
#     out = all_possible.merge(existing, on=columns, how="left", indicator=True)
#     out = out.loc[out["_merge"].eq("left_only"), columns].reset_index(drop=True)
#
#     return out


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
            df_in_BodList = read_csv_file("df_in_BodList")
            df_in_BodProdSet = read_csv_file("df_in_BodProdSet")

        dataframes = {
            'df_in_BodList': df_in_BodList,
            'df_in_BodProdSet': df_in_BodProdSet,
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
        SubLocation = 'Sub Location.[Sub Location]'
        ItemProductGroup = 'Item.[Product Group]'
        TransMode = 'Trans Mode.[Trans Mode]'
        DUMMY_COLUMN = 'Dummy'

        BODListProductTV = 'BOD List_Product TV'
        BODListProductMNT = 'BOD List_Product MNT'
        BODListProductAV = 'BOD List_Product AV'
        BODList_BODLT = 'BOD List_BOD LT'
        BODList_ShipmentLT = 'BOD List_Shipment LT'
        BODList_EffStartdate = 'BOD List_Eff Startdate'
        BODList_EffEnddate = 'BOD List_Eff Enddate'
        BODList_EffStartweek = 'BOD List_Eff Startweek'
        BODList_EffEndweek = 'BOD List_Eff Endweek'

        BODProdSET_BODLT = 'BOD Prod SET_BOD LT'
        BODProdSET_ShipmentLT = 'BOD Prod SET_Shipment LT'
        BODProdSET_EffStartdate = 'BOD Prod SET_Eff Startdate'
        BODProdSET_EffEnddate = 'BOD Prod SET_Eff Enddate'
        BODProdSET_EffStartweek = 'BOD Prod SET_Eff Startweek'
        BODProdSET_EffEndweek = 'BOD Prod SET_Eff Endweek'

        version_column = [VersionName]

        # Grain 의 dtype = string 으로 먼저 세팅 (000012345(원본) -> 12345 (숫자형으로 인식해 앞자리 0 사라지는 현상 대비)
        for col in [VersionName, Location, SubLocation, TransMode]:
            df_in_BodList[col] = df_in_BodList[col].astype("string")
            df_in_BodProdSet[col] = df_in_BodProdSet[col].astype("string")

        df_in_BodProdSet[ItemProductGroup] = df_in_BodProdSet[ItemProductGroup].astype("string")

        bodList_column = [
            Location, SubLocation, TransMode,
            BODListProductTV, BODListProductMNT, BODListProductAV,
            BODList_BODLT, BODList_ShipmentLT,
            BODList_EffStartdate, BODList_EffEnddate,
            BODList_EffStartweek, BODList_EffEndweek,
        ]
        fn_bodList_column = version_column + bodList_column

        bodProdSet_column = [
            Location, SubLocation, TransMode, ItemProductGroup,
            BODProdSET_BODLT, BODProdSET_ShipmentLT,
            BODProdSET_EffStartdate, BODProdSET_EffEnddate,
            BODProdSET_EffStartweek, BODProdSET_EffEndweek,
        ]

        fn_bodProdSet_column = version_column + bodProdSet_column

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_BodList.empty :
            raise CustomException("STEP3 by 0.1 ____ df_in_BodList 값이 없습니다.")

        current_date = get_current_date_str('UTC')
        step(f'=====> current_date : {current_date}')

        ################################################################################################################
        # STEP 4 :  BOD List => BOD Prod SET data 상속 함수 로직
        ################################################################################################################
        step('=====> STEP4 Start : 상속 함수 로직')
        def inherit_bodList_mg_to_bodProdSet_unique(df1:pd.DataFrame, df2:pd.DataFrame) -> pd.DataFrame:

            step('=====> STEP4 inherit Start ')
            # 0) 키/매핑 정의
            keys = [VersionName, Location, SubLocation, TransMode]

            # df_in_BodList 의 불린 플래그 컬럼 -> df_in_BodProdSet 의 Item.Product Group 값 매핑
            # Measure.[BOD List_Product TV]=True -> Item.Product Group="TV"
            # Measure.[BOD List_Product MNT]=True -> Item.Product Group="MONITOR"
            # Measure.[BOD List_Product AV]=True -> Item.Product Group="AV"
            pg_map = {BODListProductTV:"TV", BODListProductMNT:"MONITOR", BODListProductAV:"AV"}

            # df_in_BodList 에서 df_in_BodProdSet 로 내려보낼 "원본" mg 컬럼들 (혼합 타입 가능)
            payload_cols = [BODList_BODLT, BODList_ShipmentLT, BODList_EffStartdate, BODList_EffEnddate, BODList_EffStartweek, BODList_EffEndweek]

            # df_in_BodProdSet 의 "대상" mg 컬럼명 -> df_in_BodList 의 원본 payload 컬럼명
            col_map = {
                BODProdSET_BODLT:BODList_BODLT,                 # 정수(nullable)
                BODProdSET_ShipmentLT:BODList_ShipmentLT,       # 정수(nullable)
                BODProdSET_EffStartdate:BODList_EffStartdate,   # 날짜(datetime)
                BODProdSET_EffEnddate:BODList_EffEnddate,       # 날짜(datetime)
                BODProdSET_EffStartweek:BODList_EffStartweek,   # 문자열(string)
                BODProdSET_EffEndweek:BODList_EffEndweek,       # 문자열(string)
            }

            # 원본 DataFrame 변형 방지 : 복사본에서 작업
            df_in_BodList = df1.copy()
            df_in_BodProdSet = df2.copy()
            step('=====> STEP4 inherit > 0 ')

            ############################################################################################################
            # 1) df_in_BodList 타입 정리 (Null 안전)
            ############################################################################################################
            # BOD LT / Shipment LT : 숫자로 변환 불가하면 NaN -> Int64(Nullable Int)로 변환하여 <NA> 허용
            df_in_BodList[BODList_BODLT] = pd.to_numeric(df_in_BodList[BODList_BODLT], errors="coerce").astype("Int64")
            df_in_BodList[BODList_ShipmentLT] = pd.to_numeric(df_in_BodList[BODList_ShipmentLT], errors="coerce").astype("Int64")

            # EffStartdate / EffEnddate : datetime 변환 불가하면 NaT (Null 날짜)
            df_in_BodList[BODList_EffStartdate] = pd.to_datetime(df_in_BodList[BODList_EffStartdate], errors="coerce")
            df_in_BodList[BODList_EffEnddate] = pd.to_datetime(df_in_BodList[BODList_EffEnddate], errors="coerce")

            # EffStartweek / EffEndweek : pandas string dtype로 통일(Null은 <NA>로 유지)
            df_in_BodList[BODList_EffStartweek] = df_in_BodList[BODList_EffStartweek].astype("string")
            df_in_BodList[BODList_EffEndweek] = df_in_BodList[BODList_EffEndweek].astype("string")
            step('=====> STEP4 inherit > 1 ')

            ############################################################################################################
            # 2) df_in_BodProdSet 타입 정리 + mg 컬럼 없으면 생성
            ############################################################################################################
            # df_in_BodProdSet 에 대상 컬럼이 없으면 "결측" 으로 새로 만들고,
            # 있으면 타입을 우리가 원하는 형태로 정리해둔다.
            if BODProdSET_BODLT not in df_in_BodProdSet.columns:
                df_in_BodProdSet[BODProdSET_BODLT] = pd.Series(pd.array([pd.NA] * len(df_in_BodProdSet), dtype="Int64"), index=df_in_BodProdSet.index)
            else:
                df_in_BodProdSet[BODProdSET_BODLT] = pd.to_numeric(df_in_BodProdSet[BODProdSET_BODLT], errors="coerce").astype("Int64")

            if BODProdSET_ShipmentLT not in df_in_BodProdSet.columns:
                df_in_BodProdSet[BODProdSET_ShipmentLT] = pd.Series(pd.array([pd.NA] * len(df_in_BodProdSet), dtype="Int64"), index=df_in_BodProdSet.index)
            else:
                df_in_BodProdSet[BODProdSET_ShipmentLT] = pd.to_numeric(df_in_BodProdSet[BODProdSET_ShipmentLT], errors="coerce").astype("Int64")

            if BODProdSET_EffStartdate not in df_in_BodProdSet.columns:
                df_in_BodProdSet[BODProdSET_EffStartdate] = pd.Series([pd.NA] * len(df_in_BodProdSet), index=df_in_BodProdSet.index)
            else:
                df_in_BodProdSet[BODProdSET_EffStartdate] = pd.to_datetime(df_in_BodProdSet[BODProdSET_EffStartdate], errors="coerce")

            if BODProdSET_EffEnddate not in df_in_BodProdSet.columns:
                df_in_BodProdSet[BODProdSET_EffEnddate] = pd.Series([pd.NA] * len(df_in_BodProdSet), index=df_in_BodProdSet.index)
            else:
                df_in_BodProdSet[BODProdSET_EffEnddate] = pd.to_datetime(df_in_BodProdSet[BODProdSET_EffEnddate], errors="coerce")

            if BODProdSET_EffStartweek not in df_in_BodProdSet.columns:
                df_in_BodProdSet[BODProdSET_EffStartweek] = pd.Series(pd.array([pd.NA] * len(df_in_BodProdSet), dtype="string"), index=df_in_BodProdSet.index)
            else:
                df_in_BodProdSet[BODProdSET_EffStartweek] = df_in_BodProdSet[BODProdSET_EffStartweek].astype("string")

            if BODProdSET_EffEndweek not in df_in_BodProdSet.columns:
                df_in_BodProdSet[BODProdSET_EffEndweek] = pd.Series(pd.array([pd.NA] * len(df_in_BodProdSet), dtype="string"), index=df_in_BodProdSet.index)
            else:
                df_in_BodProdSet[BODProdSET_EffEndweek] = df_in_BodProdSet[BODProdSET_EffEndweek].astype("string")
            step('=====> STEP4 inherit > 2 ')

            ############################################################################################################
            # 3) df_in_BodList -> df1_long (product_group Grain 으로 확장)
            # 유니크라 drop_duplicates 불필요
            ############################################################################################################
            # df_in_BodList 의 (versionName, Location, Sub Location, TP Mode) 행을
            # - Measure.[BOD List_Product TV]=True 인 행은 Item.Product Group="TV" 로 복제
            # - Measure.[BOD List_Product MNT]=True 인 행은 Item.Product Group="MONITOR" 로 복제
            # - Measure.[BOD List_Product AV]=True 인 행은 Item.Product Group="AV" 로 복제
            # 이렇게 해서 df_in_BodProdSet 와 동일한 Grain (versionName, Location, Sub Location, TP Mode, Item.Product Group) 으로 맞춘다.
            base = df_in_BodList[keys + list(pg_map.keys()) + payload_cols]

            parts = []
            for flag_col, pg in pg_map.items():
                # 불린 플래그는 Null 이 있을 수 있으므로 fillna(False) 처리
                mask = base[flag_col].fillna(False).to_numpy(dtype=bool)

                # True인 행만 추출하여 product_group 컬럼을 부여
                if mask.any():
                    tmp = base.loc[mask, keys + payload_cols].assign(product_group=pg)
                    parts.append(tmp)

            # True 가 하나도 없으면 비어있는 df1_long 생성(merge가 꺠지지 않도록)
            df1_long = (pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=keys + ["product_group"] + payload_cols))

            print_df(df1_long, 'SETP3-1___df1_long')

            # "product_group" 을 Grain 명칭으로 변경 [Item].[Product Group]
            df1_long.rename(columns={"product_group":ItemProductGroup}, inplace=True)

            print_df(df1_long, 'SETP3-2___df1_long')

            step('=====> STEP4 inherit > 3 ')
            ############################################################################################################
            # 4) merge 시 컬럼명 안정화 (중요)
            ############################################################################################################
            # merge 전에 df1_long payload 컬럼을 강제 rename
            # 항상 고정된 컬럼명을 보장한다.
            rename_payload = {c: f"{c}__from_df1" for c in payload_cols}
            df1_long = df1_long.rename(columns=rename_payload)
            step('=====> STEP4 inherit > 4 ')

            ############################################################################################################
            # 5)  df_in_BodProdSet + df1_long merge
            ############################################################################################################
            # indicator=True 로 매칭 여부를 '_merge'에 기록:
            # - both : df1_long 과 매칭 성공(상속 대상)
            # - left_only : df_in_BodProdSet 에만 있음 (상속 대상 아님)
            merged = df_in_BodProdSet.merge(
                df1_long[keys + [ItemProductGroup] + list(rename_payload.values())],
                on=keys + [ItemProductGroup],
                how="left",
                indicator=True,
                sort=False,
                copy=False
            )

            # 매칭된 행단 True로 마스크 생성
            # df2에 merge해서 df1 값 붙이기 + 매칭된 row만 "덮어쓰기(Null 포함)"
            matched = (merged["_merge"] == "both").to_numpy()
            step('=====> STEP4 inherit > 5 ')

            ############################################################################################################
            # 6)  상속(덮어쓰기) 로직 : "매칭되면 df_in_BodList 값으로 덮어쓰기(Null 포함)"
            ############################################################################################################
            # 핵심 :
            # - matched == True 인 행은 df_in_BodList 에서 온 값을 그대로 df_in_BodProdSet 의 mg 에 대입
            # - df_in_BodList 값이 <NA>/NaT라도 그대로 덮어쓴다 (상속 개념)
            # - 매칭되지 않은 행은 df_in_BodProdSet 기존값 유지
            for dst, src in col_map.items():
                src_col = f"{src}__from_df1"
                # 매칭되면 df1 값으로 덮어쓰기 (df1값이 NA여도 그대로 덮음)
                merged[dst] = np.where(matched, merged[src_col], merged[dst])

            step('=====> STEP4 inherit > 6 ')
            ############################################################################################################
            # 7) 정리 : 보조 컬럼 제거
            ############################################################################################################
            # merged.drop(columns=["_merge"] + [f"{c}__from_df1" for c in payload_cols], inplace=True, errors="ignore")
            merged.drop(
                columns=["_merge"] + list(rename_payload.values()),
                inplace=True,
                errors="ignore"
            )

            step('=====> STEP4 inherit > 7 ')
            ############################################################################################################
            # 8) dtype 재고정 (np.where가 object로 흔들 수 있음)
            ############################################################################################################
            # np.where 때문에 dtype 흔들릴 수 있어 최종 고정
            merged[BODProdSET_BODLT] = pd.to_numeric(merged[BODProdSET_BODLT], errors="coerce").astype("Int64")
            merged[BODProdSET_ShipmentLT] = pd.to_numeric(merged[BODProdSET_ShipmentLT], errors="coerce").astype("Int64")
            merged[BODProdSET_EffStartdate] = pd.to_datetime(merged[BODProdSET_EffStartdate], errors="coerce")
            merged[BODProdSET_EffEnddate] = pd.to_datetime(merged[BODProdSET_EffEnddate], errors="coerce")
            merged[BODProdSET_EffStartweek] = merged[BODProdSET_EffStartweek].astype("string")
            merged[BODProdSET_EffEndweek] = merged[BODProdSET_EffEndweek].astype("string")
            step('=====> STEP4 inherit > 8 ')

            merged = merged[fn_bodProdSet_column]
            step('=====> STEP4 inherit > 9 종료 ')
            return merged

        df2_out = inherit_bodList_mg_to_bodProdSet_unique(df_in_BodList, df_in_BodProdSet)
        step('=====> STEP4 End : 상속 함수 로직')

        print_df(df2_out,'SETP4 by 1.1 _____ df2_out .... pd.merge[df_in_BodList, df_in_BodProdSet]')

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5')

        df_out_BodProdSet = df2_out

        dataframes = {
            'df_out_BodProdSet': df_out_BodProdSet,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BodProdSet = pd.DataFrame(columns=fn_bodProdSet_column)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BodProdSet = pd.DataFrame(columns=fn_bodProdSet_column)
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
