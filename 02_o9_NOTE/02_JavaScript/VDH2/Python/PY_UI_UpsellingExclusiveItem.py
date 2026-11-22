"""

* 프로그램명
    - PY_UI_UpsellingExclusiveItem

* 내용
     - Demand W,Inventory, Intrasnit을 모수로 하여
       Upselling SEG Prty TV, Upselling SEG Prty AV, Upselling SEG Prty MONITOR
       데이터를 추가(INSERT)

* 변경이력
- 2024.10.21 / de0413.shin (신동언) / Create
- 2025.10.24 / best7.park(박병훈) / 수정 : input Query 최소화 수정  (불필요한 컬럼 삭제)
- 206.01.28 /  best7.park(박병훈) / 수정 : Upselling_Exclusive_Item_Mkt_Prty 데이터 값 L9999 → 9999 로 변경

* Input
- df_in_DemandW = pd.read_csv('df_in_DemandW.csv')
- df_in_inventory = pd.read_csv('df_in_Invenort.csv')
- df_in_Inrransit  = pd.read_csv('df_in_Intransit.csv')

* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.


* Input Table
   - df_in_DemandW = Select ([Version].[Version Name] * [Item].[Item Stage].filter(#.Name == "SET").relatedmembers([Item]) *[Item].[KPI] * [Item].[Product Group].filter(#.Name IN {"TV","AV","MONITOR"}) * [Item].[Strategy] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Channel] * [Time].[Week] * [Location].[Site Stage].filter(#.Name == "DC").relatedmembers([Location])* [Sales Domain].[Ship To] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row,({ Measure.[Dmd W_Qty], Measure.[Dummy]}) on column ;
   - df_in_Inventory = Select ([Version].[Version Name] * [Item].[Item Stage].filter(#.Name == "SET").relatedmembers([Item]) * [Item].[KPI] * [Item].[Product Group].filter(#.Name IN {"TV","AV","MONITOR"}) * [Item].[Strategy] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Channel] * [Time].[Week] * [Location].[Site Stage].filter(#.Name == "DC").relatedmembers([Location])   * [Documents].[OrderlineID] ) on row,({ Measure.[Inv_Qty], Measure.[Dummy]}) on column ;
   - df_in_Intransit = Select ([Version].[Version Name] * [Item].[Item Stage].filter(#.Name == "SET").relatedmembers([Item]) * [Item].[KPI] * [Item].[Product Group].filter(#.Name IN {"TV","AV","MONITOR"}) * [Item].[Strategy] * [Item].[Inch] * [Item].[Marketing Name] * [Item].[Channel] * [Location].[Site Stage].filter(#.Name == "DC").relatedmembers([Location])) on row,({Measure.[Intr_Qty], Measure.[Dummy]}) on column ;
   - df_in_UpsellingSEGPrtyTV = Select ([Version].[Version Name] * [Item].[Marketing Name] * [Product].[Product Group] ) on row, ({Measure.[Upselling SEG Prty TV_Ctg], Measure.[Upselling SEG Prty TV_Prty],Measure.[Dummy]}) on column;
   - df_in_UpsellingSEGPrtyAV = Select ([Version].[Version Name] * [Item].[Strategy] * [Product].[Product Group] ) on row, ({Measure.[Upselling SEG Prty AV_Ctg], Measure.[Upselling SEG Prty AV_Prty],Measure.[Dummy]}) on column;
   - df_in_UpsellingSEGPriorityMontor =  Select ([Version].[Version Name] * [Item].[KPI] * [Product].[Product Group] ) on row, ({Measure.[Upselling SEG Prty MNT_Ctg], Measure.[Upselling SEG Prty MNT_Prty],Measure.[Dummy]}) on column;

* Output Table
    - df_out_UpsellingExclusiveItem = Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Item] * [Location].[Location] ) on row,({Measure.[Upselling Exclusive Item_Ctg], Measure.[Upselling Exclusive Item_Exclu Flag], Measure.[Upselling Exclusive Item_Mkt Prty]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_UpsellingExclusiveItem] for Measures {[Upselling Exclusive Item_Ctg]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), (ParamOutVersion, "CWV_MP"), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};



실행 전 프로시져를 통해 MF Site 삭제  필요

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
str_instance = 'PY_UI_UpsellingExclusiveItem'
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
            df_in_DemandW                       = read_csv_file('df_in_DemandW')
            df_in_Inventory                     = read_csv_file('df_in_Inventory')
            df_in_Intransit                     = read_csv_file('df_in_Intransit_EX')
            df_in_UpsellingSEGPrtyTV            = read_csv_file('df_in_UpsellingSEGPrtyTV')
            df_in_UpsellingSEGPrtyAV            = read_csv_file('df_in_UpsellingSEGPrtyAV')
            df_in_UpsellingSEGPriorityMontor    = read_csv_file('df_in_UpsellingSEGPriorityMontor')

        dataframes = {
            'df_in_DemandW'                     : df_in_DemandW,
            'df_in_Inventory'                   : df_in_Inventory,
            'df_in_Intransit'                   : df_in_Intransit,
            'df_in_UpsellingSEGPrtyTV'          : df_in_UpsellingSEGPrtyTV,
            'df_in_UpsellingSEGPrtyAV'          : df_in_UpsellingSEGPrtyAV,
            'df_in_UpsellingSEGPriorityMontor'  : df_in_UpsellingSEGPriorityMontor,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_ITEM = 'Item.[Item]'
        ITEM_STAGE = 'Item.[Item Stage]'
        ITEM_MARKETING_NAME = 'Item.[Marketing Name]'
        ITEM_PRODUCT_GROUP = 'Item.[Product Group]'
        ITEM_STRATEGY = 'Item.[Strategy]'
        ITEM_KPI = 'Item.[KPI]'
        ITEM_INCH = 'Item.[Inch]'
        ITEM_CHANNEL = 'Item.[Channel]'
        LOCATION_LOCATION = 'Location.[Location]'
        PRODUCT_GROUP = 'Product.[Product Group]'

        Upselling_Exclusive_Item_Ctg = 'Upselling Exclusive Item_Ctg'
        Upselling_Exclusive_Item_Exclu_Flag = 'Upselling Exclusive Item_Exclu Flag'
        Upselling_Exclusive_Item_Mkt_Prty = 'Upselling Exclusive Item_Mkt Prty'
        Upselling_Exclusive_Item_Sub_Ctg = 'Upselling Exclusive Item_Sub Ctg'
        Upselling_SEG_Prty_AV_Prty = 'Upselling SEG Prty AV_Prty'

        Upselling_SEG_Prty_TV_Ctg = 'Upselling SEG Prty TV_Ctg'
        Upselling_SEG_Prty_TV_Prty = 'Upselling SEG Prty TV_Prty'
        Upselling_SEG_Prty_MNT_Prty = 'Upselling SEG Prty MNT_Prty'
        Upselling_SEG_Prty_MNT_Ctg = 'Upselling SEG Prty MNT_Ctg'
        Upselling_SEG_Prty_AV_Ctg = 'Upselling SEG Prty AV_Ctg'

        TV = 'TV'
        AV = 'AV'
        MONITOR = 'MONITOR'

        step('=====> STEP 2 End')
        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 기본 Base 데이터 프레임을 만들기 위한 key 컬럼 설정
        base_cols = [VERSION_NAME_COLUMN, ITEM_ITEM, ITEM_KPI, ITEM_PRODUCT_GROUP,
                     ITEM_STRATEGY, ITEM_INCH, ITEM_MARKETING_NAME, ITEM_CHANNEL, LOCATION_LOCATION]

        # df_in_DemandW & df_in_Inventory & df_in_Intransit 를 base_cols 로 필터 후 중복 삭제
        df_in_DemandW_base = df_in_DemandW[base_cols].copy().drop_duplicates()
        df_in_Inventory_base = df_in_Inventory[base_cols].copy().drop_duplicates()
        df_in_Intransit_base = df_in_Intransit[base_cols].copy().drop_duplicates()

        # df_in_DemandW_base & df_in_Inventory_base & df_in_Intransit_base 하나로 만들고 중복삭제
        df_in_Item = pd.concat([df_in_DemandW_base, df_in_Inventory_base], ignore_index=True, axis=0).drop_duplicates()

        # df_in_Item 을 Product Type에 따라 다른 데이터 프레임으로 나누기
        df_in_Item_TV = df_in_Item[df_in_Item[ITEM_PRODUCT_GROUP] == TV]
        df_in_Item_MNT = df_in_Item[df_in_Item[ITEM_PRODUCT_GROUP] == MONITOR]
        df_in_Item_AV = df_in_Item[df_in_Item[ITEM_PRODUCT_GROUP] == AV]

        print_df(df_in_Item_TV , 'df_in_Item_TV')
        print_df(df_in_Item_MNT, 'df_in_Item_MNT')
        print_df(df_in_Item_AV, 'df_in_Item_AV')

        step('=====> STEP 3 End')

        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP4 Start : input data machining')
        # Out put 컬럼 설정
        outPut_col = [VERSION_NAME_COLUMN, ITEM_ITEM, LOCATION_LOCATION, Upselling_Exclusive_Item_Sub_Ctg,
                      Upselling_Exclusive_Item_Mkt_Prty, Upselling_Exclusive_Item_Ctg,
                      Upselling_Exclusive_Item_Exclu_Flag]

        # Item_inch : '-' 제외 하고 타입 변경
        df_in_Item_TV = df_in_Item_TV[df_in_Item_TV[ITEM_INCH] != '-']
        df_in_Item_TV[ITEM_INCH] = df_in_Item_TV[ITEM_INCH].astype(int)

        # df_in_UpsellingSEGPrtyTV 를 머지 하기 위해 컬럼명 변경
        df_in_UpsellingSEGPrtyTV = df_in_UpsellingSEGPrtyTV.rename(columns={PRODUCT_GROUP: ITEM_PRODUCT_GROUP})

        # df_out_ItemTV 생성을 위해 df_in_UpsellingSEGPrtyTV 와 merge (inner)
        df_out_ItemTV = df_in_Item_TV.merge(df_in_UpsellingSEGPrtyTV.drop(columns='Dummy',axis=1),
                                            on=[VERSION_NAME_COLUMN, ITEM_MARKETING_NAME, ITEM_PRODUCT_GROUP],
                                            how='inner')
        # ITEM_INCH 데이터 타입 변경
        df_out_ItemTV[ITEM_INCH] = df_out_ItemTV[ITEM_INCH].astype('float64')

        # 랭킹을 구하기 위한 그룹바이 진행
        df_out_ItemTV[Upselling_Exclusive_Item_Sub_Ctg] = \
            df_out_ItemTV.groupby(ITEM_MARKETING_NAME)[ITEM_INCH].rank(method='dense', ascending=False)
        # out put mg 설정
        df_out_ItemTV[Upselling_Exclusive_Item_Mkt_Prty] = df_out_ItemTV[Upselling_SEG_Prty_TV_Ctg]
        df_out_ItemTV[Upselling_Exclusive_Item_Ctg] = df_out_ItemTV[Upselling_SEG_Prty_TV_Prty]
        df_out_ItemTV[Upselling_Exclusive_Item_Exclu_Flag] = 'N'
        df_out_ItemTV = df_out_ItemTV[outPut_col]

        print_df(df_out_ItemTV ,'df_out_ItemTV')
        step('=====> STEP 4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')
        # 모니터에서 ITEM_KPI 와 ITEM_INCH '-' 가 아닌것 필터
        df_in_Item_MNT = df_in_Item_MNT[(df_in_Item_MNT[ITEM_KPI] != '-') & (df_in_Item_MNT[ITEM_INCH] != '-')]
        # df_in_UpsellingSEGPriorityMontor 를 머지 하기 위해 컬럼명 변경
        df_in_UpsellingSEGPriorityMontor = df_in_UpsellingSEGPriorityMontor.rename(
            columns={PRODUCT_GROUP: ITEM_PRODUCT_GROUP})
        # df_out_ItemMNT 생성을 위해 df_in_UpsellingSEGPriorityMontor 와 merge (inner)
        df_out_ItemMNT = df_in_Item_MNT.merge(df_in_UpsellingSEGPriorityMontor.drop(columns='Dummy', axis=1),
                                              on=[VERSION_NAME_COLUMN, ITEM_KPI, ITEM_PRODUCT_GROUP],
                                              how='inner')
        # ITEM_INCH 데이터 타입 변경
        df_out_ItemMNT[ITEM_INCH] = df_out_ItemMNT[ITEM_INCH].astype('float64')
        # Monitor Case
        # - 동일 KPI 내 Inch를 고려하여 Rank 처리
        # Inch가 큰것부터 Rank 체번  (30, 35, 40, 45 → 4, 3, 2, 1)
        df_out_ItemMNT[Upselling_Exclusive_Item_Sub_Ctg] = \
            df_out_ItemMNT.groupby(ITEM_KPI)[ITEM_INCH].rank(method='dense', ascending=False)
        df_out_ItemMNT[Upselling_Exclusive_Item_Mkt_Prty] = df_out_ItemMNT[Upselling_SEG_Prty_MNT_Prty]
        df_out_ItemMNT[Upselling_Exclusive_Item_Ctg] = df_out_ItemMNT[Upselling_SEG_Prty_MNT_Ctg]
        df_out_ItemMNT[Upselling_Exclusive_Item_Exclu_Flag] = 'N'
        df_out_ItemMNT = df_out_ItemMNT[outPut_col]
        step('=====> STEP 5 End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################
        step('=====> STEP 6 Start : input data machining')
        # df_in_Item_AV filter ITEM_STRATEGY 의 값 중 '-' 아닌것과 (And) ITEM_CHANNEL 에 '-','OTHERS' 아닌것 필터 링
        df_in_Item_AV = df_in_Item_AV[
            (df_in_Item_AV[ITEM_STRATEGY] != "-") & (~df_in_Item_AV[ITEM_CHANNEL].isin(['-', 'OTHERS']))]
        # df_in_UpsellingSEGPrtyAV 를 머지 하기 위해 컬럼명 변경
        df_in_UpsellingSEGPrtyAV = df_in_UpsellingSEGPrtyAV.rename(columns={PRODUCT_GROUP: ITEM_PRODUCT_GROUP})

        df_out_ItemAV = df_in_Item_AV.merge(df_in_UpsellingSEGPrtyAV.drop(columns='Dummy', axis=1),
                                            on=[VERSION_NAME_COLUMN, ITEM_STRATEGY, ITEM_PRODUCT_GROUP],
                                            how='inner')

        # AV Case
        # - 동일 Strategy 내 Channel을 고려하여 Rank 처리
        #   Channel 큰것부터 Rank 체번  (11.1.4, 9.1.4, 7.1.2, 5.1.2, 3.1.2 → 1, 2, 3, 4, 5)
        #  Channel의 경우 소수점 처리가 중요함 (첫번째 소수점만 의미가 있음)
        #  '-'는 0으로 처리
        df_out_ItemAV["Item.[Channel]_new1"] = df_out_ItemAV[ITEM_CHANNEL].str.split('.').str[0]
        df_out_ItemAV["Item.[Channel]_new2"] = df_out_ItemAV[ITEM_CHANNEL].str.split('.').str[1]
        df_out_ItemAV["Item.[Channel]_new3"] = df_out_ItemAV[ITEM_CHANNEL].str.split('.').str[2]

        df_out_ItemAV["Item.[Channel]_new1"] = df_out_ItemAV["Item.[Channel]_new1"].astype('float64')
        df_out_ItemAV["Item.[Channel]_new2"] = df_out_ItemAV["Item.[Channel]_new2"].fillna(0).astype('float64')
        df_out_ItemAV["Item.[Channel]_new3"] = df_out_ItemAV["Item.[Channel]_new3"].fillna(0).astype('float64')

        df_out_ItemAV["Item.[Channel]_rank1"] = df_out_ItemAV.groupby(ITEM_STRATEGY)["Item.[Channel]_new1"].rank(
            method='dense', ascending=False)
        df_out_ItemAV["Item.[Channel]_rank2"] = df_out_ItemAV.groupby(ITEM_STRATEGY)["Item.[Channel]_new2"].rank(
            method='dense', ascending=False)
        df_out_ItemAV["Item.[Channel]_rank3"] = df_out_ItemAV.groupby(ITEM_STRATEGY)["Item.[Channel]_new3"].rank(
            method='dense', ascending=False)
        df_out_ItemAV["Item.[Channel]_rank1"] = df_out_ItemAV["Item.[Channel]_rank1"].astype('int64')
        df_out_ItemAV["Item.[Channel]_rank2"] = df_out_ItemAV["Item.[Channel]_rank2"].fillna(0).astype('int64')
        df_out_ItemAV["Item.[Channel]_rank3"] = df_out_ItemAV["Item.[Channel]_rank3"].fillna(0).astype('int64')
        df_out_ItemAV["Item.[Channel]_rank"] = df_out_ItemAV["Item.[Channel]_rank1"].astype('str') + df_out_ItemAV[
            "Item.[Channel]_rank2"].astype('str') + df_out_ItemAV["Item.[Channel]_rank3"].astype('str')
        df_out_ItemAV["Item.[Channel]_rank"] = df_out_ItemAV["Item.[Channel]_rank"].astype('int64')
        df_out_ItemAV["Item.[Channel]_Rank"] = df_out_ItemAV.groupby(ITEM_STRATEGY)["Item.[Channel]_rank"].rank(
            method='dense')

        df_out_ItemAV[Upselling_Exclusive_Item_Sub_Ctg] = \
            df_out_ItemAV.groupby(ITEM_STRATEGY)["Item.[Channel]_rank"].rank(method='dense')
        df_out_ItemAV[Upselling_Exclusive_Item_Mkt_Prty] = df_out_ItemAV[Upselling_SEG_Prty_AV_Prty]
        df_out_ItemAV[Upselling_Exclusive_Item_Ctg] = df_out_ItemAV[Upselling_SEG_Prty_AV_Ctg]
        df_out_ItemAV[Upselling_Exclusive_Item_Exclu_Flag] = 'N'
        df_out_ItemAV = df_out_ItemAV[outPut_col]

        print_df(df_out_ItemAV , 'df_out_ItemAV')
        step('=====> STEP 6 End')
        ################################################################################################################
        # STEP 7 :  input data machining
        ################################################################################################################
        step('=====> STEP 7 Start : input data machining')

        df_out_UpsellingExclusiveItem = pd.concat([df_out_ItemTV, df_out_ItemMNT, df_out_ItemAV],axis= 0,
                                                  ignore_index=True)

        df_out_UpsellingExclusiveItem[Upselling_Exclusive_Item_Mkt_Prty] = np.where(
            df_out_UpsellingExclusiveItem[Upselling_Exclusive_Item_Mkt_Prty]=='L99999', 99999,
            df_out_UpsellingExclusiveItem[Upselling_Exclusive_Item_Mkt_Prty])

        df_out_UpsellingExclusiveItem[Upselling_Exclusive_Item_Mkt_Prty] = df_out_UpsellingExclusiveItem[
            Upselling_Exclusive_Item_Mkt_Prty].astype(int)


        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_UpsellingExclusiveItem, 'df_out_UpsellingExclusiveItem_데이터 확인', True)

        print_df(df_out_UpsellingExclusiveItem, 'df_out_UpsellingExclusiveItem', True)
        row_count, col_count = df_out_UpsellingExclusiveItem.shape
        note(f'=====> Final df_out_UpsellingExclusiveItem rows : {row_count} , Columns : {col_count}')

        step('=====> STEP 5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_UpsellingExclusiveItem = pd.DataFrame([], columns=[])


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