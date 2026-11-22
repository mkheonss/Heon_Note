"""
* 프로그램명
    - PY_UI_UpsellingItemList

* 내용
     - Upselling Exclusive Item에서 대체제품 순위 생성

* 변경이력
- 2024.10.23 / de0413.shin (신동언) / Create
- 2025.10.24 / best7.park (박병훈) / 수정 → input query 수정 및 불필요한 로직 수정 및 Template 양식 통일
- 2026.01.28 / best7.park (박병훈) / Update -> upsellingExclusiveItem_MktPrty 빈값 input 시 9999로 치환 후 진행

* Input
- df_in_UpsellExclsvItem = pd.read_csv('df_in_UpsellExclsvItem.csv')

* Flow Summary

* Execution
* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
    - df_in_UpsellExclsvItem = Select ([Version].[Version Name] * [Item].[Item Stage].filter(#.Name == "SET").relatedmembers([Item])* [Location].[Location] * [Item].[Product Group].filter(#.Name in {"TV","AV","MONITOR"})* [Item].[Marketing Name] * [Item].[Strategy] * [Item].[KPI] * [Item].[Inch] * [Item].[Channel] ) on row, ({Measure.[Upselling Exclusive Item_Ctg], Measure.[Upselling Exclusive Item_Mkt Prty], Measure.[Upselling Exclusive Item_Sub Ctg], Measure.[Dummy]}) on column where {Measure.[Upselling Exclusive Item_Exclu Flag] == "N"};
* Output Table
    - df_out_UpsellingItemList = Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] ) on row,
                                 ({Measure.[Upselling Item List_Ctg], Measure.[Upselling Item List_Like Ctg], Measure.[Upselling Item List_Like Ctg Name], Measure.[Upselling Item List_Like Item], Measure.[Upselling Item List_Like Rank], Measure.[Upselling Item List_Like Sub Ctg], Measure.[Upselling Item List_Like Sub Ctg Name], Measure.[Upselling Item List_Sub Ctg], Measure.[Upselling Item List_UpsellingYN]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_UpsellingItemList] for measures {[Upselling Item List_Ctg]} using scope (&MPV) using arguments {
      (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (ParamOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};
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
str_instance = 'PY_UI_UpsellingItemList'
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
            df_in_UpsellExclsvItem       = read_csv_file('df_in_UpsellExclsvItem')

        dataframes = {
            'df_in_UpsellExclsvItem':        df_in_UpsellExclsvItem,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수설정
        versionVersionName = 'Version.[Version Name]'
        itemItem = 'Item.[Item]'
        locationLocation = 'Location.[Location]'
        itemProductGroup = 'Item.[Product Group]'
        itemMarketingName = 'Item.[Marketing Name]'
        itemStrategy = 'Item.[Strategy]'
        itemKPI = 'Item.[KPI]'
        itemInch = 'Item.[Inch]'
        itemChannel = 'Item.[Channel]'
        sequenceSequence = '[Sequence].[Sequence]'

        upsellingExclusiveItem_Ctg = 'Upselling Exclusive Item_Ctg'
        upsellingExclusiveItem_SubCtg = 'Upselling Exclusive Item_Sub Ctg'
        upsellingExclusiveItem_MktPrty = 'Upselling Exclusive Item_Mkt Prty'

        upsellingItemList_Ctg = 'Upselling Item List_Ctg'
        upsellingItemList_SubCtg = 'Upselling Item List_Sub Ctg'
        upsellingItemList_LikeItem = 'Upselling Item List_Like Item'
        upsellingItemList_LikeCtgName = 'Upselling Item List_Like Ctg Name'
        upsellingItemList_LikeSubCtgName = 'Upselling Item List_Like Sub Ctg Name'
        upsellingItemList_LikeCtg = 'Upselling Item List_Like Ctg'
        upsellingItemList_LikeSubCtg = 'Upselling Item List_Like Sub Ctg'
        upsellingItemList_LikeRank = 'Upselling Item List_Like Rank'
        upsellingItemList_UpsellingYN = 'Upselling Item List_UpsellingYN'

        likeRank_ABS = 'LikeRank_ABS'
        rownumber = 'rownumber'

        MONITOR = 'MONITOR'
        TV = 'TV'
        AV = 'AV'

        New_Value = 'New_Value'

        step('=====> STEP 2 End')
        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 칼럼 정리 2025-10-24 input query 수정으로 불필요한 내용 삭제
        # df_list = df_in_UpsellExclsvItem[[versionVersionName, itemItem, locationLocation, itemProductGroup,
        #                                               itemMarketingName, itemStrategy, itemKPI,
        #                                               itemInch, itemChannel,
        #                                               upsellingExclusiveItem_Ctg,
        #                                               upsellingExclusiveItem_SubCtg,
        #                                               upsellingExclusiveItem_MktPrty]].copy()
        # df_list['CNT'] = 0
        # del df_in_UpsellExclsvItem

        # df_list[itemInch] = df_list[itemInch].astype('str')

        df_list = df_in_UpsellExclsvItem.drop(columns='Dummy').copy()
        df_list[itemInch] = df_list[itemInch].str.replace('-', '0').astype(str)
        df_list[upsellingExclusiveItem_MktPrty] = df_list[upsellingExclusiveItem_MktPrty].fillna(9999).astype(int)

        # itemProductGroup 에 따른 itemInch 및 itemChannel 구분하여 New_Value 값 지정
        df_list[New_Value] = np.where(df_list[itemProductGroup] == MONITOR,
                                                     df_list[itemInch].str.split(".").str[0],
                                                     np.where(df_list[itemProductGroup] == AV,
                                                              df_list[itemChannel].str.split('.').str[0],
                                                              np.where(df_list[itemProductGroup] == TV,
                                                                       df_list[itemInch], '0')))

        print_df(df_list, 'df_list')

        # df_list_GRP = df_list.groupby([itemProductGroup,itemItem,locationLocation], as_index=False)['CNT'].count()
        df_list_GRP = df_list.groupby([itemProductGroup, locationLocation], as_index=False).size().rename(
            columns={'size': 'CNT'})

        print_df(df_list_GRP, 'df_list_GRP')

        # for start ------------------------------------------------------------------------------------------------------
        i = 0
        for idx, row in df_list_GRP.iterrows():
            # print(idx,row)
            df_list_A_TMP = df_list.loc[(df_list[itemProductGroup] == row[itemProductGroup]) &
                                        (df_list[locationLocation] == row[locationLocation])
                                        ].copy()

            df_list_B_TMP = df_list.loc[(df_list[itemProductGroup] == row[itemProductGroup]) &
                                        (df_list[locationLocation] == row[locationLocation])
                                        ].copy()

            # Merge : df_list_A_TMP & df_list_B_TMP
            df_MG_List_TMP = df_list_A_TMP.merge(df_list_B_TMP, on=[versionVersionName], how='inner',
                                                 suffixes=('', '_B'))



            del df_list_A_TMP
            del df_list_B_TMP

            # A 와 B 연결 조건 적용
            df_MG_List_TMP = df_MG_List_TMP.loc[(df_MG_List_TMP[itemItem] != df_MG_List_TMP[itemItem + '_B']) &
                                                (df_MG_List_TMP[locationLocation] == df_MG_List_TMP[
                                                    locationLocation + '_B']) &
                                                (df_MG_List_TMP[upsellingExclusiveItem_Ctg] == df_MG_List_TMP[
                                                    upsellingExclusiveItem_Ctg + '_B']) &
                                                (df_MG_List_TMP[itemProductGroup] == df_MG_List_TMP[
                                                    itemProductGroup + '_B'])]

            df_MG_List_TMP[upsellingItemList_Ctg] = df_MG_List_TMP[upsellingExclusiveItem_Ctg]
            df_MG_List_TMP[upsellingItemList_SubCtg] = df_MG_List_TMP[upsellingExclusiveItem_SubCtg]
            df_MG_List_TMP[upsellingItemList_LikeItem] = df_MG_List_TMP[itemItem + '_B']
            # vdCommon.gfn_saveDf(df_MG_List_TMP, "df_MG_List_TMP", False)

            # print_df(df_MG_List_TMP, 'df_MG_List_TMP 확인')

            if row[itemProductGroup] == 'TV':
                df_MG_List_TMP[upsellingItemList_LikeCtgName] = df_MG_List_TMP[
                    itemMarketingName + '_B']  # (TV) BList.Marketing Name ([Item].[Marketing Name])
                df_MG_List_TMP[upsellingItemList_LikeSubCtgName] = df_MG_List_TMP[
                    itemInch + '_B']  # (TV) BList.Inch ([Item].[Inch]
            elif row[itemProductGroup] == 'AV':
                df_MG_List_TMP[upsellingItemList_LikeCtgName] = df_MG_List_TMP[
                    itemStrategy + '_B']  # (AV) Upselling Item List_Like Ctg Name = BList.Marketing Name ([Item].[Strategy])
                df_MG_List_TMP[upsellingItemList_LikeSubCtgName] = df_MG_List_TMP[
                    itemChannel + '_B']  # (AV) BList.Inch ([Item].[Channel])
            else:
                df_MG_List_TMP[upsellingItemList_LikeCtgName] = df_MG_List_TMP[
                    itemKPI + '_B']  # (Monitor) Upselling Item List_Like Ctg Name = BList.Marketing Name ([Item].[KPI])
                df_MG_List_TMP[upsellingItemList_LikeSubCtgName] = df_MG_List_TMP[
                    itemInch + '_B']  # (Monotor) BList.Inch ([Item].[Inch]

            df_MG_List_TMP[upsellingItemList_LikeCtg] = df_MG_List_TMP[upsellingExclusiveItem_Ctg + '_B']
            df_MG_List_TMP[upsellingItemList_LikeSubCtg] = df_MG_List_TMP[upsellingExclusiveItem_SubCtg + '_B']

            # df_MG_List_TMP[upsellingItemList_LikeRank] = (((df_MG_List_TMP[upsellingExclusiveItem_MktPrty + '_B'] * 10) +
            #                                                df_MG_List_TMP[upsellingExclusiveItem_SubCtg + '_B'].astype('float64')) -
            #                                             ((df_MG_List_TMP[upsellingExclusiveItem_MktPrty] * 10) +
            #                                               df_MG_List_TMP[upsellingExclusiveItem_SubCtg].astype('float64'))
            #                                             )
            ##2025.04.28 현업요청사항으로 수정
            # df_MG_List_TMP[upsellingItemList_LikeRank] = (((df_MG_List_TMP[upsellingExclusiveItem_MktPrty + '_B']) +
            #                                                df_MG_List_TMP[upsellingExclusiveItem_SubCtg + '_B'].astype('float64') * 10) -
            #                                             ((df_MG_List_TMP[upsellingExclusiveItem_MktPrty] ) +
            #                                               df_MG_List_TMP[upsellingExclusiveItem_SubCtg].astype('float64') * 10)
            #                                             )

            ##2025.06.27 현업요청사항으로 수정
            int_cols = ["New_Value" + '_B' , "New_Value"]
            df_MG_List_TMP[int_cols] = df_MG_List_TMP[int_cols].astype(int)
            df_MG_List_TMP[upsellingItemList_LikeRank] = (((df_MG_List_TMP[upsellingExclusiveItem_MktPrty + '_B']) +
                                                           df_MG_List_TMP["New_Value" + '_B']) -
                                                          ((df_MG_List_TMP[upsellingExclusiveItem_MktPrty]) +
                                                           df_MG_List_TMP["New_Value"])
                                                          )

            df_MG_List_TMP[likeRank_ABS] = abs(df_MG_List_TMP[upsellingItemList_LikeRank])
            # vdCommon.gfn_saveDf(df_MG_List_TMP, "df_MG_List_TMP", True)
            df_MG_List_TMP[upsellingItemList_UpsellingYN] = np.where(df_MG_List_TMP[upsellingItemList_LikeRank] <= 0,
                                                                     'Y', 'N')

            df_MG_List_TMP[rownumber] = \
            df_MG_List_TMP.groupby([versionVersionName, itemProductGroup, itemItem, locationLocation,
                                    upsellingItemList_UpsellingYN], as_index=False)[likeRank_ABS].rank(method='first',
                                                                                                       ascending=True)

            df_MG_List_TMP = df_MG_List_TMP.loc[df_MG_List_TMP[rownumber] <= 10]

            df_MG_List_TMP[sequenceSequence] = np.where((df_MG_List_TMP[upsellingItemList_UpsellingYN] == 'Y'),
                                                        df_MG_List_TMP[rownumber],  # 1 ~ 10
                                                        df_MG_List_TMP[rownumber] + 10  # 11 ~ 20
                                                        )

            # df_MG_List_TMP[sequenceSequence] = df_MG_List_TMP.groupby([versionVersionName, itemProductGroup, itemItem, locationLocation]).cumcount() + 1

            # 칼럼 정리
            df_MG_List_TMP = df_MG_List_TMP[[versionVersionName, itemItem, locationLocation, sequenceSequence,
                                             upsellingItemList_Ctg, upsellingItemList_SubCtg,
                                             upsellingItemList_LikeItem, upsellingItemList_LikeCtgName,
                                             upsellingItemList_LikeSubCtgName,
                                             upsellingItemList_LikeCtg, upsellingItemList_LikeSubCtg,
                                             upsellingItemList_LikeRank, upsellingItemList_UpsellingYN]]

            row_count, col_count = df_MG_List_TMP.shape

            # DATA 취합
            if i == 0:
                df_list_ALL = df_MG_List_TMP.copy()
            else:
                df_list_ALL = pd.concat([df_list_ALL, df_MG_List_TMP])

            i = i + 1
            del df_MG_List_TMP

            # print_df(df_list_ALL, "df_list_ALL", True)

        # for end ------------------------------------------------------------------------------------------------------

        step('=====> STEP 3 End')

        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP4 Start : input data machining')

        # out Data 생성 : : df_BOMFense & df_BODFense & df_MtrlFense 통합
        df_out_UpsellingItemList = df_list_ALL.copy()
        del df_list_ALL

        # 버전 처리
        df_out_UpsellingItemList[versionVersionName] = paramOutVersion

        # 시퀀스 처리
        df_out_UpsellingItemList[sequenceSequence] = df_out_UpsellingItemList[sequenceSequence].astype(int)

        step('=====> STEP 4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_UpsellingItemList, 'df_out_UpsellingItemList', True)

        print_df(df_out_UpsellingItemList, 'df_out_UpsellingItemList', True)
        row_count, col_count = df_out_UpsellingItemList.shape
        note(f'=====> Final df_out_UpsellingItemList rows : {row_count} , Columns : {col_count}')

        step('=====> STEP 5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_UpsellingItemList = pd.DataFrame([], columns=[])


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

