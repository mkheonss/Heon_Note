"""
* 프로그램명
    - PY_MG_FrozenFence

* 내용
    - Frozen Fence 구성을 위한 프로그램

* 변경이력
    - 2024.11.14 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn     : Select (Version.[Version Name] * &FinishedGoods* &MFLocation * [Item].[Item] * [Item].[Product Group] * [Item].[Product] * [Item].[SCM Type] ) on row, ({Measure.[Item Site Asn_Engine Flag]}) on column.filter(Measure.[Item Site Asn_Engine Flag] == true);
    - df_in_SOPFrozenPeriod : Select (Version.[Version Name] * [Item].[SCM Type] * &MFLocation * [Product].[Product Group] ) on row, ({Measure.[SOP Frozen Period_Smry Copy], Measure.[SOP Frozen Period_Smry Exnd], Measure.[SOP Frozen Period_Smry Item] }) on column;

* Flow Summary
    - STEP1. STEP1. df_out_FrozenFence Measure Group Data Clear
    - STEP2. df_in_sopfrozenPeriod  의  SOP Frozen Period_Smry, SOP Frozen Period_Smry Exnd Copy 값을 itemsite 와 join.

* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_FrozenFence

* 데이타 초기화
    - DELETE DATA FOR MODEL [Frozen Fence] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_FrozenFence] for Measures {Measure.[Frozen Fence_Period], Measure.[Frozen Fence_Extend Period]} using scope (&MPV *[Item].[Item] * [Location].[Location])
        using arguments {(ExecutionMode, "MediumWeight"), (IncludeNullRows, "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
    - Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location]  ) on row, ({Measure.[Frozen Fence_Period], Measure.[Frozen Fence_Extend Period], Measure.[Frozen Fence_Item Period] }) on column;

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
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_FrozenFence'
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


def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
        return df[column_name].values[0]
    return None  # 기본값 반환


def get_formatted_time(timestamp):
    """타임스탬프를 사람이 읽을 수 있는 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def run_time_minutes(start_time):
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"



def decode(column, condition, if_all, alternate_value):
    return np.where(column == condition, if_all, alternate_value)



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
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_SOPFrozenPeriod = read_csv_file("df_in_SOPFrozenPeriod")
    
    
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_SOPFrozenPeriod, 'input table load .... df_in_SOPFrozenPeriod')
    
        step('=====> STEP1 End')


    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
    
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = '[Sub Location].[Sub Location]'
        TO_LOCATION_COLUMN = '[To Location].[To Location]'
    
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_TYPE_COLUMN = 'Item.[Item Type]'
        ITEM_PRODUCT_GROUPL_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_COLUMN = 'Item.[Product]'
        ITEM_SCM_TYPE_COLUMN = 'Item.[SCM Type]'
        ITEM_SCM_TYPE_X_COLUMN = 'Item.[SCM Type]_x'
        ITEM_SCM_TYPE_Y_COLUMN = 'Item.[SCM Type]_y'
        ITEM_A2_COLUMN = 'Item.[A2]'
        ITEM_A9_COLUMN = 'Item.[A9]'
        ITEM_A11_COLUMN = 'Item.[A11]'
        ITEM_A14_COLUMN = 'Item.[A14]'
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'
    
        PRODUCT_GROUP_PRODUCT_GROUP_COLUMN = 'Product Group.[Product Group]'
        PRODUCT_PRODUCT_GROUP_COLUMN = 'Product.[Product Group]'
        CATEGORY_COLUMN = 'Category.[Category]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'
    
        SOP_FROZEN_PERIOD_SMRY_COPY_COLUMN = 'SOP Frozen Period_Smry Copy'
        SOP_FROZEN_PERIOD_SMRY_EXND_COLUMN = 'SOP Frozen Period_Smry Exnd'
        SOP_FROZEN_PERIOD_SMRY_ITEM_COLUMN = 'SOP Frozen Period_Smry Item'
    
        FROZEN_FENCE_PERIOD_COLUMN = 'Frozen Fence_Period'
        FROZEN_FENCE_EXTEND_PERIOD_COLUMN = 'Frozen Fence_Extend Period'
        FROZEN_FENCE_ITEM_PERIOD_COLUMN = 'Frozen Fence_Item Period'

        df_FrozenFence_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN,
            FROZEN_FENCE_PERIOD_COLUMN, FROZEN_FENCE_EXTEND_PERIOD_COLUMN, FROZEN_FENCE_ITEM_PERIOD_COLUMN
        ]
    
        step('=====> STEP2 End')
    
    
    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ====================> STEP3 by 1 (Start) -> df_in_sopfrozenPeriod  의  SOP Frozen Period_Smry, SOP Frozen Period_Smry Exnd Copy 값을 itemsite 와 join

        # 1.1 df_FrozenFence create
        #   1.1.1 df_in_ItemSiteAsn, df_in_SOPFrozenPeriod join
        df_FrozenFence = pd.merge(df_in_SOPFrozenPeriod, df_in_ItemSiteAsn, how='inner',
                                  left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, PRODUCT_PRODUCT_GROUP_COLUMN],
                                  right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_PRODUCT_GROUPL_COLUMN])
        print_df(df_FrozenFence, 'STEP3 by 1.1.1 ____ df_FrozenFence .... merge[df_in_SOPFrozenPeriod, df_in_ItemSiteAsn]')


        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_FrozenFence.empty:
            raise CustomException("df_FrozenFence 값이 없습니다. 첫 번째 값을 확인하세요.")


        df_FrozenFence = df_FrozenFence[
            df_FrozenFence[ITEM_SCM_TYPE_COLUMN+'_y'] == np.where(df_FrozenFence[ITEM_SCM_TYPE_COLUMN+'_x'] == 'All',
                                                                  df_FrozenFence[ITEM_SCM_TYPE_COLUMN+'_y'],
                                                                  df_FrozenFence[ITEM_SCM_TYPE_COLUMN+'_x'])
        ]

        df_FrozenFence.rename(columns={ITEM_SCM_TYPE_COLUMN+'_y' : ITEM_SCM_TYPE_COLUMN,
                                       SOP_FROZEN_PERIOD_SMRY_COPY_COLUMN: FROZEN_FENCE_PERIOD_COLUMN,
                                       SOP_FROZEN_PERIOD_SMRY_EXND_COLUMN: FROZEN_FENCE_EXTEND_PERIOD_COLUMN,
                                       SOP_FROZEN_PERIOD_SMRY_ITEM_COLUMN: FROZEN_FENCE_ITEM_PERIOD_COLUMN,
                                       }, inplace=True)
        print_df(df_FrozenFence, 'STEP3 by 1.1.2 ____ df_FrozenFence .... colunms renamed')

        # 2.1 원하는 컬럼만 선택
        df_FrozenFence = df_FrozenFence[df_FrozenFence_columns].drop_duplicates()
        print_df(df_FrozenFence, 'STEP3 by 2.1 ____ df_FrozenFence .... final')

        # ====================> STEP3 by 1 (End)
    
        step('=====> STEP3 End')


    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_out_FrozenFence = rename_and_delete_df(df_FrozenFence)
        df_out_FrozenFence[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')


    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_FrozenFence, 'output table create .... df_out_FrozenFence', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_FrozenFence = pd.DataFrame(columns=df_FrozenFence_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_FrozenFence = pd.DataFrame(columns=df_FrozenFence_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
