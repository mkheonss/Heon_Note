"""
* 프로그램명
    - PY_MNG_PlanGroupUpdate

* 내용
    - SOP Frozen List 구성을 위한 프로그램

* 변경이력
    - 2024.08.19 / 권태우 / Create
    - 2025.02.06 / 권태우 / 내용정리

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_DMDFlag      : Select (Version.[Version Name] * [Item].[Item] ) on row, ({Measure.[Item Valid_Dmd Flag], Measure.[Item Valid_Plan Group] }) on column.filter(Measure.[Item Valid_Dmd Flag] == True);
    - df_in_ItemSiteAsn  : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] ) on row, ({Measure.[Item Site Asn_Actual Flag], Measure.[Item Site Asn_Cons Flag], Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Dmd Flag], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Inv Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Prod Flag], Measure.[Item Site Asn_SS Flag], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Sales Prod Flag], Measure.[Item Site Asn_Stage], Measure.[Item Site Asn_Supply Plan Flag]}) on column where {Measure.[Item Site Asn_Engine Flag] == true};
    - df_in_BOMMaster    : Select (Version.[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column;
    - df_in_BOMComponent : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate], Measure.[BOM Comp_Valid Flag]}) on column;

* Flow Summary
    - STEP1.
    - STEP2.

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_ItemVaild

* 데이타 초기화
    - DELETE DATA FOR MODEL [MP Bach_Plan Group_Define] where {Version.[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - exec plugin instance [PY_MNG_PlanGroupUpdate] for Measures{[MP Bach_Plan Group_Define_Item], [MP Bach_Plan Group_Define_Plan Group]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV) on row, ({Measure.[MP Bach_Plan Group_Define_Item], Measure.[MP Bach_Plan Group_Define_Plan Group]}) on column limit 1000;

;

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
str_instance = 'PY_MNG_PlanGroupUpdate'
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


def vd_log_end():
    vdCommon.gfn_pyLog_end()


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
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_DMDFlag = read_csv_file("df_in_DMDFlag")
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_BOMComponent = read_csv_file("df_in_BOMComponent")


        print_df(df_in_DMDFlag, 'input table load .... df_in_DMDFlag')
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_BOMMaster, 'input table load .... df_in_BOMMaster')
        print_df(df_in_BOMComponent, 'input table load .... df_in_BOMComponent')

        step('=====> STEP1 End : Check memory usage & runtime')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'

        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'

        ITEM_VAILD_DMD_FLAG_COLUMN = 'Item Valid_Dmd Flag'
        ITEM_VAILD_PLAN_GROUP_COLUMN = 'Item Valid_Plan Group'

        BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_ID_COLUMN = 'BOM Master_BOM ID'

        MP_BATCH_PLAN_GROUP_DEFINE_ITEM_COLUMN = 'MP Bach_Plan Group_Define_Item'
        MP_BATCH_PLAN_GROUP_DEFINE_PLAN_GROUP_COLUMN = 'MP Bach_Plan Group_Define_Plan Group'

        df_ItemVaild_columns = [
            VERSION_NAME_COLUMN, SEQUENCE_COLUMN, ITEM_COLUMN, ITEM_VAILD_PLAN_GROUP_COLUMN
        ]

        step('=====> STEP2 End')




        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # item 만 발췌, 중복값 삭제(Item Distinct) 및 미사용 컬럼 삭제
        #   - df_in_ItemSiteAsn remake
        drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [VERSION_NAME_COLUMN,
                                                                                     ITEM_COLUMN]]
        df_in_ItemSiteAsn = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[VERSION_NAME_COLUMN, ITEM_COLUMN], keep='first')
        # print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn')

        # df_in_BOMMaster, df_in_ItemSiteAsn join --> 플랜 대상 BOM Master BOM ID = item 이 같을걸 읽어서 bomid를 가져온다.
        df_BOMMasterItem = pd.merge(df_in_BOMMaster, df_in_ItemSiteAsn, how='inner',
                                    left_on=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN],
                                    right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN],)
        print_df(df_BOMMasterItem, 'STEP3 by 1.1  ____ df_BOMMasterItem ..... merge')
        # delete_dfs(df_in_BOMMaster, df_in_ItemSiteAsn)

        # 필요컬럼 발췌
        df_BOMMasterItem = df_BOMMasterItem[[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN, BOM_ID_COLUMN]]

        # 중복 데이터 삭제
        df_BOMMasterItem = df_BOMMasterItem.drop_duplicates(subset=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN,
                                                                    BOM_ID_COLUMN],
                                                            keep='first')
        print_df(df_BOMMasterItem, 'df_BOMMasterItem')

        # df_BOMMasterItem, df_in_BOMComponent join
        df_BOMMasterComp = pd.merge(df_BOMMasterItem, df_in_BOMComponent,
                                    left_on=[VERSION_NAME_COLUMN, BOM_ID_COLUMN],
                                    right_on=[VERSION_NAME_COLUMN, BOM_ID_COLUMN],
                                    how='inner')
        print_df(df_BOMMasterComp, 'STEP3 by 1.2  ____ df_BOMMasterComp ..... merge')
        # delete_dfs(df_BOMMasterItem, df_in_BOMComponent)

        # 필요컬럼 발췌
        df_BOMMasterComp = df_BOMMasterComp[[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN, BOM_ID_COLUMN, ITEM_COLUMN]]

        # 중복 데이터 삭제
        df_BOMMasterComp = df_BOMMasterComp.drop_duplicates(
            subset=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN, BOM_ID_COLUMN, ITEM_COLUMN], keep='first')
        print_df(df_BOMMasterComp, 'STEP3 by 1.3  ____ df_BOMMasterComp ..... duplicate remove')

        # df_BOMMasterComp, df_in_DMDFlag (df_in_BOMMaster left join)
        df_BOMMasterCompDmdF = pd.merge(df_BOMMasterComp, df_in_DMDFlag,
                                        left_on=[VERSION_NAME_COLUMN, BOM_MASTER_ID_COLUMN],
                                        right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN],
                                        how='left')
        print_df(df_BOMMasterCompDmdF, 'STEP3 by 1.4  ____ df_BOMMasterCompDmdF ..... merge')
        # delete_dfs(df_BOMMasterComp, df_in_DMDFlag)

        # 필요컬럼 발췌
        df_BOMMasterCompDmdF = df_BOMMasterCompDmdF[[VERSION_NAME_COLUMN, 'Item.[Item]_x', BOM_ID_COLUMN,
                                                     BOM_MASTER_ID_COLUMN, ITEM_VAILD_PLAN_GROUP_COLUMN]]

        # 컬럼명 변경
        df_BOMMasterCompDmdF.rename(columns={'Item.[Item]_x': ITEM_COLUMN}, inplace=True)

        # 중복 데이터 삭제
        df_BOMMasterCompDmdF = df_BOMMasterCompDmdF.drop_duplicates(
            subset=[VERSION_NAME_COLUMN, ITEM_COLUMN, BOM_ID_COLUMN, BOM_MASTER_ID_COLUMN, ITEM_VAILD_PLAN_GROUP_COLUMN], keep='first')
        print_df(df_BOMMasterCompDmdF, 'STEP3 by 1.5  ____ df_BOMMasterCompDmdF ..... drop duplicate')

        step('=====> STEP3 End')




        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_BOMMasterCompDmdF = df_BOMMasterCompDmdF[(df_BOMMasterCompDmdF[ITEM_VAILD_PLAN_GROUP_COLUMN].notnull())].copy()

        # sequence 처리
        df_BOMMasterCompDmdF[SEQUENCE_COLUMN] = range(1, len(df_BOMMasterCompDmdF) + 1)

        # 컬럼타입 재정의
        df_BOMMasterCompDmdF[ITEM_VAILD_PLAN_GROUP_COLUMN] = df_BOMMasterCompDmdF[ITEM_VAILD_PLAN_GROUP_COLUMN].astype(int).astype(str)
        print_df(df_BOMMasterCompDmdF, 'STEP4 by 1.1  ____ df_BOMMasterCompDmdF ..... create')

        # 필요컬럼 발췌
        df_BOMMasterCompDmdF = df_BOMMasterCompDmdF[df_ItemVaild_columns]

        # 컬럼명 변경
        df_BOMMasterCompDmdF.rename(columns={ITEM_COLUMN: MP_BATCH_PLAN_GROUP_DEFINE_ITEM_COLUMN,
                                             ITEM_VAILD_PLAN_GROUP_COLUMN: MP_BATCH_PLAN_GROUP_DEFINE_PLAN_GROUP_COLUMN},
                                    inplace=True)
        df_BOMMasterCompDmdF = df_BOMMasterCompDmdF.drop_duplicates()

        # 최종 아웃풋
        df_out_ItemVaild = rename_and_delete_df(df_BOMMasterCompDmdF)
        df_out_ItemVaild[VERSION_NAME_COLUMN] = paramOutVersion

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_ItemVaild, 'output table create .... df_out_ItemVaild', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ItemVaild = pd.DataFrame(columns=df_ItemVaild_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ItemVaild = pd.DataFrame(columns=df_ItemVaild_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
