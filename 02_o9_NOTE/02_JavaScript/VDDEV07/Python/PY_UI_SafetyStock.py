"""

* 프로그램명
    - PY_UI_SafetyStock

* 내용
     - Item Site Association에 Location 과 Item 중 Safety_Stock에 없는 것을 추가

* 변경이력
- 2025.03.06 / ybest7.park (박병훈) / Create
- 2025.03.14 / ybest7.park (박병훈)
    -> common 추가 / input query 수정
- 2025.04.22 / ybest7.park (박병훈) 수정
    -> df_in_MFLocation Input data 추가
- 2025.04.24 SS_Type 값 수정
- 2025.0.28 measure.[SS_SS Type]  값 수정
- 2025-06.16 measure 이름 변경
    ( SS_Must Flag Final 로 되어 있는 메져이름을 SS_Must Flag Override 로 변경)
- 2025-06-24 SS_Must_Flag, SS_Must_Flag_Override, SS_SS_Type, SS_Valid_Flag 값 변경
- 2025-09-10 df_in_MFLocation input query 수정 (Location 조건 추가 )
- 2025-09-29 로직 순서 변경 / df_out_SafetyStockPrty 순서를 3번에서 1번 실행으로 변경
- 2025-10-01 로직 순서 변경 / df_in_SafetyStock 와 생성된 df_in_SafetyStockPrty 와 필터 후 주차 확장 하는 것으로 변경
- 2025-10-16 df_in_SafetyStock 에 SS_SS Type Override mg input date 추가 및 out data 로직 추가
- 2025-10-21 df_in_Nest52Week input query 수정
- 2025-10-29 df_in_SafeStockLastWeek input query 추가 및 input Query 반영하는 로직 추가
- 2025-11-18 df_in_SafeStockLastWeek 필터하는 로직 추가 반영
- 2025-11-25 df_in_SafeStockLastWeek 데이터 삭제 로 로직 조건 변경 (df_in_SafeStockLastWeek → df_out_SafetyStockPrty_temp 조건 변경)
             df_in_MFLocation input query 변경 및 df_in_SafeStockLastWeek 삭제에 따라 프로시져 수정
- 2025-12-24 df_in_BuildAheadCal 삭제 하고 df_in_BuildAhead 통합
- 2026-01-07 df_in_ItemSiteAsnMF Query 수정 Measure.[Item Site Asn_Actual Flag] -> Measure.[Item Site Asn_Cur Status] 변경


* Flow Summary
    - 1. SS W 에 생성
        1.1 Item Site Association 에서 SS W에 없는 값을 update
        조건 1 : Measure.[Item Site Asn_Cur Status] in {"ACTIVE", "PLANNED"}
        조건 2 : [Location].[Location Type].filter(#.Name in {"DC","MF"}
        조건 3 : [Location].[Site Stage] 이 'MF_LCM' 인 경우
        1.2 필터 조건을 (Next52Weeks) 주차로 확장
        1.3 SS W 값 생성 Default 0으로 설정 (기존
        1.4 SS Week 및 중복 삭제 후 기존 Program에서 기존 Default 값 설정 후 SS 값 업데이트 (기존 SS 값은 유지)
        1.5 SS W 기준으로 SS Prty 값 설정 (기존 SS Prty 유지)


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsnMF :  Select (Version.[Version Name] * [Item].[Item] * [Location].[Site Stage].filter(#.Name in {"MF", "MF_SET"}).relatedmembers([Location]).filter(#.[Location Valid Flag] == True)) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Dummy]}) on column where {Measure.[Item Site Asn_Cur Status] in {"ACTIVE", "PLANNED"}};
    - df_in_SafetyStockW :  Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[AP2] ) on row, ({Measure.[SS W_SS Target], Measure.[Dummy]}) on column;
    - df_in_SafetyStock : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] ) on row, ({Measure.[SS_Must Flag], Measure.[SS_SS Type], Measure.[SS_SS Type Override], Measure.[SS_Valid Flag] , Measure.[Dummy]}) on column ;
    - df_in_SafetyStockPrty =  Select ([Version].[Version Name] * [Location].[Location] ) on row, ({Measure.[SS Prty_Created By], Measure.[SS Prty_Creation Time], Measure.[SS Prty_Must Flag], Measure.[SS Prty_Prty], Measure.[SS Prty_Update Time], Measure.[SS Prty_Updated By], Measure.[Dummy]}) on column;
    - df_in_SiteAP2 = Select ([Version].[Version Name] * [Location].[Location] ) on row, ({Measure.[Site AP2 Map_Ship To] , Measure.[Dummy]}) on column;
    - df_in_Nest52Week = Select (&LastPastWeek.unionwith(&Next52Weeks));
    - df_in_BuildAhead = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] ) on row, ({Measure.[Build Ahead Item_3160 Qty], Measure.[Build Ahead Item_61 Qty], Measure.[Build Ahead Item_Adj WOS], Measure.[Build Ahead Item_Demand], Measure.[Build Ahead Item_EOH Week],Measure.[Build Ahead Item_Target WOS],  Measure.[Build Ahead Item_Target EOH], Measure.[Dummy]}) on column;
    # - df_in_BuildAheadCal = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] ) on row, ({Measure.[Build Ahead Cal_Target EOH],Measure.[Dummy]}) on column;
    # - df_in_ItemSiteASNCURStatus = Select ([Version].[Version Name] * [Item].[Item]) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Dummy]}) on column Where {Measure.[Item Site Asn_Cur Status] in {"ACTIVE", "PLANNED"}};
    - df_in_ItemSiteAsnSalesProdFlag = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Item Site Asn_Sales Prod Flag], Measure.[Dummy]}) on column Where {Measure.[Item Site Asn_Sales Prod Flag]==TRUE};
    - df_in_MFLocation = Select ([Location].[Site Stage].filter(#.Name in {"MF", "MF_SET"}).relatedmembers([Location]).filter(#.[Location Valid Flag] == True));
    # - df_in_SafeStockLastWeek = Select (&LastSyncVersion * [Location].[Location] * [Item].[Item] * &LastPastWeek * [Sales Domain].[AP2]) on row, ({Measure.[SS W_SS Target], Measure.[Dummy]}) on column ;

* Output Table
    - df_out_SafetyStockW = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Sales Domain].[AP2] ) on row, ({Measure.[SS W_SS Target]}) on column;
    - df_out_SafetyStock = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item] * [Sales Domain].[AP2] ) on row, ({Measure.[SS_3160 Qty], Measure.[SS_61 Qty], Measure.[SS_Adj WOS], Measure.[SS_Demand], Measure.[SS_EOH Week], Measure.[SS_Must Flag], Measure.[SS_Must Flag Override],  Measure.[SS_SS Target], Measure.[SS_SS Type], Measure.[SS_Target EOH], Measure.[SS_Target WOS], Measure.[SS_Valid Flag]}) on column;
    - df_out_SafetyStockPrty = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] ) on row, ({Measure.[SS Prty_Created By], Measure.[SS Prty_Creation Time], Measure.[SS Prty_Must Flag], Measure.[SS Prty_Prty], Measure.[SS Prty_Update Time], Measure.[SS Prty_Updated By]}) on column;
    - df_out_log
    - df_out_logDetail
* 데이터 삭제
    DELETE DATA FOR MODEL [SS] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [SS W] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [SS Prty] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
    EXEC plugin instance [PY_UI_SafetyStock] for measures {[SS_Valid Flag]} using scope (&MPV * &LastPastWeek.unionwith(&Next52Weeks)) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (paramOutVersion ,"CWV_MP")} ;


* 데이터 확인
    Select ([Version].[Version Name].[CWV_MP] * [Item].[Item].[BN07-01304C] * [Location].[Location].[P637LCD] ) on row, ({Measure.[SS_3160 Qty], Measure.[SS_61 Qty], Measure.[SS_EOH Week], Measure.[SS_Must Flag], Measure.[SS_Pattern], Measure.[SS_SS Type], Measure.[SS_Valid Flag]}) on column;


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
import pytz

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SafetyStock'
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
        step(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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
            df_in_ItemSiteAsnMF = read_csv_file('df_in_ItemSiteAsnMF')
            df_in_SafetyStockW = read_csv_file('df_in_SafetyStockW')
            df_in_SafetyStock = read_csv_file('df_in_SafetyStock')
            df_in_SafetyStockPrty = read_csv_file('df_in_SafetyStockPrty')
            df_in_SiteAP2 = read_csv_file('df_in_SiteAP2')
            df_in_Nest52Week = read_csv_file('df_in_Nest52Week')
            df_in_BuildAhead = read_csv_file('df_in_BuildAhead')
            # df_in_BuildAheadCal = read_csv_file('df_in_BuildAheadCal')
            df_in_ItemSiteAsnSalesProdFlag = read_csv_file('df_in_ItemSiteAsnSalesProdFlag')
            df_in_MFLocation = read_csv_file('df_in_MFLocation')
            # df_in_SafeStockLastWeek         = read_csv_file('df_in_SafeStockLastWeek')

        dataframes = {
            'df_in_ItemSiteAsnMF':        df_in_ItemSiteAsnMF,
            'df_in_SafetyStockW':               df_in_SafetyStockW,
            'df_in_SafetyStock':                df_in_SafetyStock,
            'df_in_SafetyStockPrty':            df_in_SafetyStockPrty,
            'df_in_SiteAP2':                    df_in_SiteAP2,
            'df_in_Nest52Week':                 df_in_Nest52Week,
            'df_in_BuildAhead':                 df_in_BuildAhead,
            # 'df_in_BuildAheadCal':              df_in_BuildAheadCal,
            'df_in_ItemSiteAsnSalesProdFlag':   df_in_ItemSiteAsnSalesProdFlag,
            'df_in_MFLocation':                 df_in_MFLocation,
            # 'df_in_SafeStockLastWeek'   :       df_in_SafeStockLastWeek
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수설정
        Version_Name_COLUMN = 'Version.[Version Name]'
        Item_COLUMN = 'Item.[Item]'
        Item_Class_Category_COLUMN = 'Item.[Class Category]'
        Location_COLUMN = 'Location.[Location]'
        Site_Stage_COLUMN = 'Location.[Site Stage]'
        Location_Type_COLUMN = 'Location.[Location Type]'
        Time_WeekKey_COLUMN = 'Time.[WeekKey]'
        Time_Week_COLUMN = 'Time.[Week]'
        Sales_Domain_AP2_COLUMN = 'Sales Domain.[AP2]'

        Item_Site_Asn_Actual_Flag = 'Item Site Asn_Actual Flag'
        Dummy = 'Dummy'
        SS_W_SS_Target = 'SS W_SS Target'
        SS_Must_Flag = 'SS_Must Flag'
        SS_SS_Type = 'SS_SS Type'
        SS_Valid_Flag = 'SS_Valid Flag'
        SS_Prty_Created_By = 'SS Prty_Created By'
        SS_Prty_Creation_Time = 'SS Prty_Creation Time'
        SS_Prty_Must_Flag = 'SS Prty_Must Flag'
        SS_Prty_Prty = 'SS Prty_Prty'
        SS_Prty_Update_Time = 'SS Prty_Update Time'
        SS_Prty_Updated_By = 'SS Prty_Updated By'
        SS_SS_Type_Override = 'SS_SS Type Override'  # 2025-10-16 추가
        Site_AP2_Map_Ship_To = 'Site AP2 Map_Ship To'

        DC = "DC"
        MF_LCM = 'MF_LCM'
        Week_Explode = 'Week_Explode'

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        ######################################### 2025-09-29 로직 순서 변경 3번째에서 1번째로 변경 ##########################
        # df_in_ItemSiteASNCURStatus 과 df_in_ItemSiteAsnSalesProdFlag merge

        # Item 기준으로 Merge
        df_out_SafetyStockPrty_temp = df_in_ItemSiteAsnMF.drop(
            columns=['Dummy', Location_COLUMN], axis=1).merge(
            df_in_ItemSiteAsnSalesProdFlag.drop(
                columns='Dummy', axis=1),
            on=[Version_Name_COLUMN, Item_COLUMN], how='inner')

        # Version, Item, Location 기준 중복 삭제
        df_ItemSiteAsnDC = df_out_SafetyStockPrty_temp[
            [Version_Name_COLUMN, Item_COLUMN, Location_COLUMN]].drop_duplicates(keep='first')

        print_df(df_ItemSiteAsnDC, 'df_ItemSiteAsnDC 확인 01')

        # df_out_SafetyStockPrty_temp Location 기준으로 중복 제거
        df_out_SafetyStockPrty_temp = df_out_SafetyStockPrty_temp[
            [Version_Name_COLUMN, Location_COLUMN]].drop_duplicates(keep='first')

        # Merge를 위한 df_in_MFLocation 데이터 프레임 전 처리
        df_in_MFLocation[Version_Name_COLUMN] = paramOutVersion  # Version 값 처리
        # df_in_MFLocation = df_in_MFLocation.drop(columns=Site_Stage_COLUMN, axis=1)  # Site_Stage_COLUMN 삭제

        # 기 생성된 df_out_SafetyStockPrty_temp 과 df_in_MFLocation 합치기 기본 Data Frame 생성
        df_out_SafetyStockPrty_temp = pd.concat(
            [df_out_SafetyStockPrty_temp, df_in_MFLocation], axis=0, ignore_index=True)

        # index 컬럼 설정
        SafetyStockPrty_index_col = [Version_Name_COLUMN, Location_COLUMN]

        # index 설정 후 df_in_SafetyStock에 없는 것만 값 채우기
        df_out_SafetyStockPrty_index = df_out_SafetyStockPrty_temp.set_index(SafetyStockPrty_index_col).index
        note(f"df_out_SafetyStockPrty_index ============> {df_out_SafetyStockPrty_index.value_counts()}")
        df_in_SafetyStockPrty_index = df_in_SafetyStockPrty.set_index(SafetyStockPrty_index_col).index
        note(f"df_in_SafetyStockPrty_index ============> {df_in_SafetyStockPrty_index.value_counts()}")
        df_out_SafetyStockPrty = df_out_SafetyStockPrty_temp.loc[
            ~df_out_SafetyStockPrty_index.isin(df_in_SafetyStockPrty_index)]

        row_count, col_count = df_out_SafetyStockPrty.shape
        note(f' =========> df_out_SafetyStockPrty  rows : {row_count} , Columns : {col_count}')

        df_out_SafetyStockPrty = df_out_SafetyStockPrty.copy()
        kst = pytz.timezone('Asia/Seoul')
        today_kst = datetime.datetime.now(kst).date()
        # 컬럼명 설정 (out put 값 설정)
        df_out_SafetyStockPrty[SS_Prty_Must_Flag] = 'N'
        df_out_SafetyStockPrty[SS_Prty_Prty] = 999
        df_out_SafetyStockPrty[SS_Prty_Created_By] = 'PY_MG_SafetyStockPrty'
        df_out_SafetyStockPrty[SS_Prty_Creation_Time] = today_kst

        print_df(df_out_SafetyStockPrty, "df_out_SafetyStockPrty 최종 확인", )

        step('=====> STEP 3 End')
        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')
        # 중복 삭제 및 Grain 설정 (기본 Key Columns 설정)
        Grain_Columns = [Version_Name_COLUMN, Item_COLUMN, Location_COLUMN]
        # df_in_ItemSiteAssociation_temp 를  df_ItemSiteAsnDC 과 df_in_ItemSiteAsnMF concat.
        df_ItemSiteAsnDC = pd.concat(
            [df_in_ItemSiteAsnMF[Grain_Columns],df_ItemSiteAsnDC[Grain_Columns]], axis=0, ignore_index=True)
        # df_in_ItemSiteAssociation & df_out_SafetyStockPrty 의 Grain_Columns 기준 중복 삭제
        df_in_ItemSiteAssociation_temp = df_ItemSiteAsnDC[Grain_Columns].drop_duplicates()
        df_in_SafetyStockPrty_temp = df_in_SafetyStockPrty[SafetyStockPrty_index_col].drop_duplicates()
        df_out_SafetyStockPrty_temp = df_out_SafetyStockPrty[SafetyStockPrty_index_col].drop_duplicates()

        print_df(df_out_SafetyStockPrty_temp, "df_out_SafetyStockPrty_temp _ 확인")

        ######################################### 2025-09-29 로직 추가 df_out_SafetyStockPrty  ##########################
        # df_in_ItemSiteAssociation_temp & df_out_SafetyStockPrty_temp 합치고 중복 삭제
        df_in_SafetyStockPrty_temp = pd.concat([df_in_SafetyStockPrty_temp, df_out_SafetyStockPrty_temp], axis=0,
                                               ignore_index=True)
        df_in_SafetyStockPrty_temp = df_in_SafetyStockPrty_temp.drop_duplicates(keep='first')

        df_in_ItemSiteAssociation_temp = df_in_ItemSiteAssociation_temp.merge(df_in_SafetyStockPrty_temp,
                                                                              on=[Version_Name_COLUMN, Location_COLUMN],
                                                                              how='inner')

        print_df(df_in_ItemSiteAssociation_temp, "df_in_ItemSiteAssociation_temp 임시 확인 1")

        ######################################## 2025-10-01 로직 순서 변경 (ybest7.park###################################

        # df_in_SiteAP2 데이터 타입 변경
        df_in_SiteAP2[Site_AP2_Map_Ship_To] = df_in_SiteAP2[Site_AP2_Map_Ship_To].astype(str)

        # Site_AP2 Dic으로 변환
        Site_AP2_dict = dict(zip(df_in_SiteAP2[Location_COLUMN], df_in_SiteAP2[Site_AP2_Map_Ship_To]))
        # Site_AP2 columns 추가 및 데이터 타입
        df_in_ItemSiteAssociation_temp[Sales_Domain_AP2_COLUMN] = df_in_ItemSiteAssociation_temp[Location_COLUMN].map(
            Site_AP2_dict)
        # note(
        #     f' =========> Sales_Domain_AP2_COLUMN value_counts : \n'
        #     f' {df_in_ItemSiteAssociation_temp[Sales_Domain_AP2_COLUMN].value_counts()}')
        df_in_ItemSiteAssociation_temp[Sales_Domain_AP2_COLUMN] = df_in_ItemSiteAssociation_temp[
            Sales_Domain_AP2_COLUMN].fillna('-')
        # note(
        #     f' =========> Sales_Domain_AP2_COLUMN value_counts : \n'
        #     f' {df_in_ItemSiteAssociation_temp[Sales_Domain_AP2_COLUMN].value_counts()}')
        # df_in_ItemSiteAssociation_temp[Sales_Domain_AP2_COLUMN] = df_in_ItemSiteAssociation_temp[
        #     Sales_Domain_AP2_COLUMN].astype(str).str.replace('.0$', '', regex=True)
        note(
            f' =========> Sales_Domain_AP2_COLUMN value_counts : \n'
            f' {df_in_ItemSiteAssociation_temp[Sales_Domain_AP2_COLUMN].value_counts()}')

        # 데이터 프레임 비교를 위한 index 컬럼 설정
        index_col = list(set(df_in_ItemSiteAssociation_temp.columns) & set(
            df_in_SafetyStockW.columns))  # Version, Item, Location, AP2  컬럼으로 설정 됨
        # index_col.remove(Time_Week_COLUMN) # 2025-10-01 week 컬럼 index에서 삭제
        note(f' =========> index_col columns :  {index_col}')

        # df_in_ItemSiteAssociation_temp & df_in_SafetyStockW 인덱스 설정 후 df_in_SafetyStockW 기본 값 유지 \n
        # (df_in_ItemSiteAssociation_temp 값에만 있는 것 필터링)
        df_in_ItemSiteAssociation_index = df_in_ItemSiteAssociation_temp.set_index(index_col).index
        df_in_SafetyStockW_index = df_in_SafetyStockW.set_index(index_col).index
        df_in_ItemSiteAssociation_temp = df_in_ItemSiteAssociation_temp[
            ~df_in_ItemSiteAssociation_index.isin(df_in_SafetyStockW_index)]
        row_count, col_count = df_in_ItemSiteAssociation_temp.shape
        note(f' =========> df_in_ItemSiteAssociation_temp rows : {row_count} , Columns : {col_count}')

        df_in_ItemSiteAssociation_temp = df_in_ItemSiteAssociation_temp.drop_duplicates()
        print_df(df_in_ItemSiteAssociation_temp, 'df_in_ItemSiteAssociation_temp 임시 확인 2')
        ######################################## 2025-10-01 로직 순서 변경 (ybest7.park###################################
        # 중복 제거 된 df_in_ItemSiteAssociation_temp 과 Week로 확장
        # df_in_Nest52Week 주차를 List로 변경 (범위 설정)
        # Week_Explode_list = df_in_Nest52Week[Time_Week_COLUMN].to_list()
        #
        # # note(f' =========> Columns Length : {len(Week_Explode_list)}')
        # # row_count, col_count = df_in_ItemSiteAssociation_temp.shape
        # # note(f' =========> df_in_ItemSiteAssociation_temp rows : {row_count} , Columns : {col_count}')
        # # note(
        # #     f' =========> 주차 확정 시 row_count 예측 Week_Explode_list_len (주차갯수) : \n'
        # #     f'  {len(Week_Explode_list)} , columns : {row_count}  = {len(Week_Explode_list) * row_count}')
        #
        # # 확장될 주차 리스트를 Week_Explode column 에 담기
        # df_in_ItemSiteAssociation_temp[Time_Week_COLUMN] = df_in_ItemSiteAssociation_temp.apply(lambda x: Week_Explode_list,
        #                                                                                         axis=1)

        # 주차 확장 방법 변경
        df_in_Nest52Week['key_on'] = 1
        df_in_ItemSiteAssociation_temp['key_on'] = 1

        df_in_ItemSiteAssociation_temp = df_in_ItemSiteAssociation_temp.merge(
            df_in_Nest52Week[[Time_Week_COLUMN, 'key_on']].drop_duplicates(),
            on = 'key_on', how='left'
        ).drop(columns='key_on', axis=1)
        #
        # # df_in_ItemSiteAssociation_temp 주차로 확장
        # df_in_ItemSiteAssociation_temp = df_in_ItemSiteAssociation_temp.explode(Time_Week_COLUMN)

        # output 설정
        df_out_SafetyStockW = df_in_ItemSiteAssociation_temp.copy()
        df_out_SafetyStockW[SS_W_SS_Target] = 0

        ##################################### 2025-11-18 ybest7.park(박병훈) 추가 로직 반영 ################################
        ##################################### 2025-11-25 ybest7.park(박병훈) 로직 변경 ####################################
        #################################### df_in_SafeStockLastWeek → df_out_SafetyStockPrty_temp 조건 변경 ############

        # 전주 filter를 진행하기 위한 인텍스 컬럼 설정
        location_list = df_out_SafetyStockPrty_temp[Location_COLUMN].unique().tolist()
        # df_in_SafeStockLastWeek 필터를 위한 인덱스 설정
        df_in_SafeStockLastWeek = df_out_SafetyStockPrty_temp[df_out_SafetyStockPrty_temp[Location_COLUMN].isin(location_list)]

        print_df(df_in_SafeStockLastWeek, "df_in_SafeStockLastWeek_필터 확인")

        ##################################### 2025-10-29 ybest7.park(박병훈) 추가 로직 반영 ################################
        # 전주 Safe_Stock 을 out put에 concat 진행
        df_in_SafeStockLastWeek[Version_Name_COLUMN] = paramOutVersion
        df_out_SafetyStockW = pd.concat([df_out_SafetyStockW, df_in_SafeStockLastWeek], axis=0,
                                        ignore_index=True)

        # df_out_SafetyStockW = df_out_SafetyStockW[df_out_SafetyStockW[Sales_Domain_AP2_COLUMN] != "-"]
        row_count, col_count = df_out_SafetyStockW.shape
        # note(f' =========> df_out_SafetyStockW rows : {row_count} , Columns : {col_count}')
        print_df(df_out_SafetyStockW, 'df_out_SafetyStockW 최종 확인 !!!!', True)
        note(f"Sales_Domain_AP2_COLUMN value_counts : \n"
             f' {df_out_SafetyStockW[Sales_Domain_AP2_COLUMN].value_counts()}')

        step('=====> STEP 4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')
        # 빈 데이터 프레임 Error를 위한 방어 코딩
        group_keys = [Version_Name_COLUMN, Location_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN]
        agg_col = [SS_W_SS_Target]

        # 전체 컬럼 목록
        all_columns = group_keys + agg_col

        # 데이터 프레임이 비어 있는 경우
        if df_in_SafetyStockW.empty:
            df_in_SafetyStockW = pd.DataFrame(columns=all_columns)
            for col in all_columns:
                df_in_SafetyStockW[col] = pd.Series(dtype=str if col in group_keys else None)

        # df_in_SafetyStockW의 SS_W_SS_Target Max 값 설정
        df_in_SafetyStockW_max = df_in_SafetyStockW.groupby(
            group_keys)[SS_W_SS_Target].max().reset_index()

        # df_out_SafetyStock 설정을 위해 df_in_ItemSiteAssociation_temp 값 복사
        df_out_SafetyStock_temp = df_in_ItemSiteAssociation_temp.copy()


        df_out_SafetyStock_temp = df_out_SafetyStock_temp[
            [Version_Name_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, Location_COLUMN]].drop_duplicates(keep='first')

        # index 컬럼 설정
        SafetyStock_index_col = [Version_Name_COLUMN, Item_COLUMN, Sales_Domain_AP2_COLUMN, Location_COLUMN]
        # note(f"===========================SafetyStock_index_col : {SafetyStock_index_col}")

        # index 설정 후 df_in_SafetyStock에 없는 것만 값 채우기
        df_out_SafetyStock_index = df_out_SafetyStock_temp.set_index(SafetyStock_index_col).index
        df_in_SafetyStock_index = df_in_SafetyStock.set_index(SafetyStock_index_col).index
        df_out_SafetyStock = df_out_SafetyStock_temp[~df_out_SafetyStock_index.isin(df_in_SafetyStock_index)]

        # df_in_BuildAhead 추가 데이터 구성
        # Location 정보 mapping
        #
        location_dict = dict(zip(df_in_SiteAP2[Site_AP2_Map_Ship_To], df_in_SiteAP2[Location_COLUMN]))
        df_in_BuildAhead[Location_COLUMN] = df_in_BuildAhead[Sales_Domain_AP2_COLUMN].map(location_dict)
        print_df(df_in_BuildAhead, 'df_in_BuildAhead 확인')
        print_df(df_out_SafetyStock, 'df_out_SafetyStock 확인 ')

        # 중복을 삭제하고 Key 값이 되는 데이터 프레임 구성
        df_out_SafetyStock = pd.concat([df_out_SafetyStock[SafetyStock_index_col],
                                        df_in_BuildAhead[SafetyStock_index_col]], axis=0).drop_duplicates()

        print_df(df_out_SafetyStock, 'df_out_SafetyStock 확인 1')

        df_out_SafetyStock[Sales_Domain_AP2_COLUMN] = df_out_SafetyStock[Sales_Domain_AP2_COLUMN].apply(
            lambda x: ' ' if pd.isna(x) else str(x))

        ########################################### 2025-09-30 추가 ####################################################
        # Sales_Domain_AP2_COLUMN Type 변경
        df_out_SafetyStock[Sales_Domain_AP2_COLUMN] = df_out_SafetyStock[Sales_Domain_AP2_COLUMN].astype(str)
        df_in_SafetyStock[Sales_Domain_AP2_COLUMN] = df_in_SafetyStock[Sales_Domain_AP2_COLUMN].astype(str)

        df_out_SafetyStock = df_out_SafetyStock.merge(
            df_in_SafetyStock,
            on = [Version_Name_COLUMN,Location_COLUMN,Item_COLUMN,Sales_Domain_AP2_COLUMN] ,
            how='left').drop(columns='Dummy')

        ########################################### 2025-09-30 추가 ####################################################

        print_df(df_out_SafetyStock, 'df_out_SafetyStock 확인 2')

        #     df_in_SafetyStockW_max[Sales_Domain_AP2_COLUMN] = pd.Series(dtype='object')
        df_in_SafetyStockW_max[Sales_Domain_AP2_COLUMN] = df_in_SafetyStockW_max[Sales_Domain_AP2_COLUMN].apply(
            lambda x: ' ' if pd.isna(x) else str(x))
        df_in_BuildAhead[Sales_Domain_AP2_COLUMN] = df_in_BuildAhead[Sales_Domain_AP2_COLUMN].apply(
            lambda x: ' ' if pd.isna(x) else str(x))
        # df_in_BuildAheadCal[Sales_Domain_AP2_COLUMN] = df_in_BuildAheadCal[Sales_Domain_AP2_COLUMN].apply(
        #     lambda x: ' ' if pd.isna(x) else str(x))

        df_in_BuildAhead = df_in_BuildAhead.rename(
            columns={'Build Ahead Item_3160 Qty': 'SS_3160 Qty', 'Build Ahead Item_61 Qty': 'SS_61 Qty',
                     'Build Ahead Item_Adj WOS': 'SS_Adj WOS', 'Build Ahead Item_Demand': 'SS_Demand',
                     'Build Ahead Item_EOH Week': 'SS_EOH Week', 'Build Ahead Item_Target WOS': 'SS_Target WOS',
                     'Build Ahead Item_Target EOH': 'SS_Target EOH'}) # Input data 수정에 따른 수정 2025-12-24 y.best7(박병훈)

        # df_in_BuildAheadCal = df_in_BuildAheadCal.rename(columns={'Build Ahead Item_Target EOH': 'SS_Target EOH'})

        # print_df(df_in_BuildAheadCal, 'df_in_BuildAheadCal 확인 1')

        # df_out_SafetyStock 와 merge
        df_out_SafetyStock = df_out_SafetyStock.merge(
            df_in_BuildAhead.drop(columns='Sub Location.[Sub Location]'),
            on=SafetyStock_index_col,
            how='left').drop(columns='Dummy')
        # df_out_SafetyStock = df_out_SafetyStock.merge(df_in_BuildAheadCal.drop(columns='Sub Location.[Sub Location]'),
        #                                               on=SafetyStock_index_col, how='left').drop(columns='Dummy')

        # df_out_SafetyStock_temp 의 SS_W_SS_Target 값 설정
        df_out_SafetyStock = df_out_SafetyStock.merge(df_in_SafetyStockW_max,
                                                      on=[Version_Name_COLUMN, Location_COLUMN, Item_COLUMN,
                                                          Sales_Domain_AP2_COLUMN], how='left')

        df_out_SafetyStock = df_out_SafetyStock.rename(columns={SS_W_SS_Target: 'SS_SS Target'})

        df_out_SafetyStock['SS_SS Target'] = df_out_SafetyStock['SS_SS Target'].fillna(0).astype(int)

        print_df(df_out_SafetyStock, 'df_out_SafetyStock 임시확인')

        # df_out_SafetyStock 값 설정
        nan_col = [SS_Must_Flag, SS_SS_Type, SS_Valid_Flag]
        df_out_SafetyStock[nan_col] = df_out_SafetyStock[nan_col].fillna(pd.NA) # 2025-09-30 수정 /  best7.park
        # df_out_SafetyStock[[SS_Must_Flag,  SS_SS_Type, SS_Valid_Flag]] = np.nan # 2025-06-24 수정 / best7.park
        type_conversioncol = ['SS_3160 Qty', 'SS_61 Qty', 'SS_Adj WOS', 'SS_Demand', 'SS_EOH Week', 'SS_Target WOS',
                              'SS_Target EOH','SS_SS Target']

        df_out_SafetyStock[SS_SS_Type] = "MIN_TIME"  # 2025-04-24 수정 / 2025-04-28 수정 (MIN_ONHAND → MIN_TIME)

        ############################################### 2025-10-16 ybest7.par 추가 #####################################
        df_out_SafetyStock[SS_SS_Type_Override] = np.where(df_out_SafetyStock[SS_SS_Type_Override].isna(),
                                                           df_out_SafetyStock[SS_SS_Type],
                                                           df_out_SafetyStock[SS_SS_Type_Override])
        ############################################### 2025-10-16 ybest7.par 추가 #####################################

        # df_out_SafetyStock.loc[:,type_conversioncol] = df_out_SafetyStock.loc[:,type_conversioncol].fillna(0).astype('int64')

        df_out_SafetyStock[type_conversioncol] = df_out_SafetyStock[type_conversioncol].fillna(0).astype('int64')
        # for col in type_conversioncol:
        #     df_out_SafetyStock[col] = df_out_SafetyStock[col].fillna(0).astype('int64')

        # df_out_SafetyStock = df_out_SafetyStock[df_out_SafetyStock[Sales_Domain_AP2_COLUMN] != '-']

        print_df(df_out_SafetyStock, 'df_out_SafetyStock 최종 확인')

        step('=====> STEP 5 End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################

        step('=====> STEP 6 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_SafetyStockW, 'df_out_SafetyStockW', True)
            print_df(df_out_SafetyStock, 'df_out_SafetyStock', True)
            print_df(df_out_SafetyStockPrty, 'df_out_SafetyStockPrty', True)

        print_df(df_out_SafetyStockW, 'df_out_SafetyStockW', True)
        print_df(df_out_SafetyStock, 'df_out_SafetyStock', True)
        print_df(df_out_SafetyStockPrty, 'df_out_SafetyStockPrty', True)

        row_count, col_count = df_out_SafetyStockW.shape
        note(f'=====> Final df_out_SafetyStockW rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_SafetyStock.shape
        note(f'=====> Final df_out_SafetyStock rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_SafetyStockPrty.shape
        note(f'=====> Final df_out_SafetyStockPrty rows : {row_count} , Columns : {col_count}')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SafetyStockW = pd.DataFrame([], columns=[])
        df_out_SafetyStock = pd.DataFrame([], columns=[])
        df_out_SafetyStockPrty = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')
        logger.Step(p_step_desc=f'plugin Execution End')