"""
* 프로그램명
    - PY_UI_BODSOPAdjustLoadingInfoApply

* 내용
    - Loading 정보를 BOD Item, SOP Adjust

* 변경이력
    - 2024.07.29 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_loadinginfo          : Select (&SETMFLocation * &SETItem ) on row, ({ Measure.[Loading Master_Minimum Lot], Measure.[Loading Master_Multiple Lot]}) on column where {Version.[Version Name]};
    - df_in_loadingexception     : Select (&SETMFLocation * &SETItem * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({  Measure.[Loading Master To Site_Minimum Lot], Measure.[Loading Master To Site_Multiple Lot], Measure.[Loading Master To Site_Valid]}) on column where {Version.[Version Name], Measure.[Loading Master To Site_Valid]=="Y"};
    - df_in_sopadjustintersection: Select ([Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP Adjust SET W_SOp Qty],Measure.[Dummy]}) on column where {Version.[Version Name],[Time].[Week]};
    - df_in_boditemintersection  : Select ([Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_Asn]}) on column where {Version.[Version Name], [Trans Mode].[Trans Mode]};

* Flow Summary
    - STEP1. exposion / df_in_loadinginfo 을 To Site, TP Mode Exposion. (TP ="VSL"고정 / To Site = BOD Item의 From,To,TP,Item)
    - STEP2. pply exception / step1에 Exception 데이터 적용
    - STEP3-1. BOD Item / BOD Item 메저에 반영 (BOD Item 데이터를 가져올 필요 없음.)
    - STEP3-2. SOP Adjust / SOP ADjust 기생성데이터(input3)에 일치(how=inner)하는 From,To,Item,TP 에 관련메저 값 채움.

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_boditem
    - df_out_sopadjust

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_BODSOPAdjustLoadingInfoApply] for Measures {[BOD Item_Min Lot Qty]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
    - df_out_boditem
        Select (&MPV * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item_20FT Min Lot Qty], Measure.[BOD Item_20FT Multi Lot Qty], Measure.[BOD Item_40HC Min Lot Qty], Measure.[BOD Item_40HC Multi Lot Qty, Measure.[BOD Item_Loading Lock Flag] }) on column limit 100;

    - df_out_sopadjust
        Select (&MPV * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [Trans Mode].[Trans Mode] ) on row,({Measure.[SOP Adjust SET_20FT Min Lot Qty],Measure.[SOP Adjust SET_20FT Multi Lot Qty],Measure.[SOP Adjust SET_40HC Min Lot Qty],Measure.[SOP Adjust SET_20FT Multi Lot Qty]}) on column limit 100;

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
str_instance = 'PY_UI_BODSOPAdjustLoadingInfoApply'
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
            df_in_loadinginfo = read_csv_file("df_in_loadinginfo")
            df_in_loadingexception = read_csv_file("df_in_loadingexception")
            df_in_sopadjustintersection = read_csv_file("df_in_sopadjustintersection")
            df_in_boditemintersection = read_csv_file("df_in_boditemintersection")


        print_df(df_in_loadinginfo, 'input table load .... df_in_loadinginfo')
        print_df(df_in_loadingexception, 'input table load .... df_in_loadingexception')
        print_df(df_in_sopadjustintersection, 'input table load .... df_in_sopadjustintersection')
        print_df(df_in_boditemintersection, 'input table load .... df_in_boditemintersection')


        step('=====> STEP1 End')




        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        ITEM_COLUMN = 'Item.[Item]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'

        BOD_ITEM_ASN_COLUMN = 'BOD Item_Asn'
        DUMMY_COLUMN = 'Dummy'

        LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN = 'Loading Master To Site_Minimum Lot'
        LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN = 'Loading Master To Site_Multiple Lot'
        LOADING_MASTER_TO_SITE_VAILD_COLUMN = 'Loading Master To Site_Valid'

        LOADING_MASTER_MINIMUM_LOT_COLUMN = 'Loading Master_Minimum Lot'
        LOADING_MASTER_MULTIPLE_LOT_COLUMN = 'Loading Master_Multiple Lot'

        SOP_ADJUST_SET_W_SOP_QTY_COLUMN = 'SOP Adjust SET W_SOP Qty'

        BOD_ITEM_MIN_LOT_QTY_COLUMN = 'BOD Item_Min Lot Qty'
        BOD_ITEM_MULTI_LOT_QTY_COLUMN = 'BOD Item_Multi Lot Qty'
        BOD_ITEM_LOADING_LOCK_FLAG_COLUMN = 'BOD Item_Loading Lock Flag'

        SOP_ADJUST_SET_MIN_LOT_QTY_COLUMN = 'SOP Adjust SET_Min Lot Qty'
        SOP_ADJUST_SET_MULTI_LOT_QTY_COLUMN = 'SOP Adjust SET_Multi Lot Qty'

        df_BODItem_columns = [
            VERSION_NAME_COLUMN,
            LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MIN_LOT_QTY_COLUMN, BOD_ITEM_MULTI_LOT_QTY_COLUMN,
            BOD_ITEM_LOADING_LOCK_FLAG_COLUMN,
        ]

        df_SOPAdjust_columns = [
            VERSION_NAME_COLUMN,
            LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            SOP_ADJUST_SET_MIN_LOT_QTY_COLUMN, SOP_ADJUST_SET_MULTI_LOT_QTY_COLUMN,
        ]

        step('=====> STEP2 End')




        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ====================> STEP3 by 0 (Start) -> BOD Item에 있는 Item만 처리
        # 불필요 컬럼 삭제
        df_in_boditemintersection = df_in_boditemintersection.drop(labels=[BOD_ITEM_ASN_COLUMN], axis=1)
        df_in_sopadjustintersection = df_in_sopadjustintersection.drop(labels=[DUMMY_COLUMN], axis=1)
        # ====================> STEP3 by 0 (End)



        # ====================> STEP3 by 1 (Start) -> exposion / df_in_loadinginfo 을 To Site, TP Mode Exposion.
        #                                             (TP ="VSL"고정 / To Site = BOD Item의 From,To,TP,Item)

        df_step1_output = pd.merge(df_in_loadinginfo, df_in_boditemintersection, how='inner', on=[LOCATION_COLUMN, ITEM_COLUMN])
        print_df(df_step1_output, 'SETP3 by 1.1 _____ df_step1_output .... pd.merge[df_in_loadinginfo, df_in_boditemintersection]')

        # ====================> STEP3 by 1 (End)




        # ====================> STEP3 by 2 (Start) -> apply exception / step1에 Exception 데이터 적용
        #                                             ※ qty = NVL(df_in_loadingexception.qty, step1_output.qty) // 둘다 없으면 row 제거.

        df_step2_output = rename_and_delete_df(df_step1_output)
        # df_step2_output.rename(columns={
        #     LOADING_MASTER_MINIMUM_LOT_COLUMN: LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN,
        #     LOADING_MASTER_MULTIPLE_LOT_COLUMN: LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN,
        # }, inplace=True)
        # df_step2_output[LOADING_MASTER_TO_SITE_VAILD_COLUMN] = "Y"

        # columns = [
        #     LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
        #     LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN, LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN, LOADING_MASTER_TO_SITE_VAILD_COLUMN,
        # ]
        # df_step2_output = df_step2_output[columns]
        print_df(df_step2_output, 'SETP3 by 2.1 _____ df_step2_output .... columns modify')

        df_step2_output = pd.merge(df_step2_output, df_in_loadingexception, how='left', on=[LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_step2_output, 'SETP3 by 2.2 _____ df_step2_output .... pd.merge[df_step2_output, df_in_loadingexception]')

        df_step2_output[LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN] = (
            df_step2_output[LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN].fillna(df_step2_output[LOADING_MASTER_MINIMUM_LOT_COLUMN])
        )

        df_step2_output[LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN] = (
            df_step2_output[LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN].fillna(df_step2_output[LOADING_MASTER_MULTIPLE_LOT_COLUMN])
        )

        # 결측치가 있는 행 제거
        df_step2_output = df_step2_output.dropna(subset=[LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN, LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN,])

        columns = [
            LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN, LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN, LOADING_MASTER_TO_SITE_VAILD_COLUMN,
        ]
        df_step2_output = df_step2_output[columns]
        print_df(df_step2_output, 'SETP3 by 2.3 _____ df_step2_output .... final')

        # ====================> STEP3 by 2 (End)




        # ====================> STEP3 by 3-1 (Start) -> BOD Item / BOD Item 메저에 반영 (BOD Item 데이터를 가져올 필요 없음.)

        df_boditem = df_step2_output.copy()
        print_df(df_boditem, 'SETP3 by 3-1.1 _____ df_boditem .... df copy')

        df_boditem.rename(columns={
            LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN: BOD_ITEM_MIN_LOT_QTY_COLUMN,
            LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN: BOD_ITEM_MULTI_LOT_QTY_COLUMN,
            LOADING_MASTER_TO_SITE_VAILD_COLUMN: BOD_ITEM_LOADING_LOCK_FLAG_COLUMN,
        }, inplace=True)
        df_boditem[BOD_ITEM_LOADING_LOCK_FLAG_COLUMN] = "Y"
        print_df(df_boditem, 'SETP3 by 3-1.2 _____ df_boditem .... final')

        # ====================> STEP3 by 3-1 (End)




        # ====================> STEP3 by 3-2 (Start) -> SOP Adjust / SOP ADjust 기생성데이터(input3)에 일치(how=inner)하는 From,To,Item,TP 에 관련메저 값 채움

        df_sopadjust = pd.merge(df_step2_output, df_in_sopadjustintersection, how='inner',
                                left_on=[LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN],
                                right_on=[LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_sopadjust, 'SETP3 by 3-2.1 _____ df_sopadjust .... pd.merge[df_step2_output, df_in_sopadjustintersection]')

        df_sopadjust = df_sopadjust.drop(labels=[SUB_LOCATION_COLUMN], axis=1)
        columns = [
            LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN, LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN,
        ]
        df_sopadjust = df_sopadjust[columns]
        df_sopadjust.rename(columns={
            LOADING_MASTER_TO_SITE_MINIMUM_LOT_COLUMN: SOP_ADJUST_SET_MIN_LOT_QTY_COLUMN,
            LOADING_MASTER_TO_SITE_MULTIPLE_LOT_COLUMN: SOP_ADJUST_SET_MULTI_LOT_QTY_COLUMN,
        }, inplace=True)
        print_df(df_sopadjust, 'SETP3 by 3-2.2 _____ df_sopadjust .... final')

        # ====================> STEP3 by 3-2 (End)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_out_boditem = rename_and_delete_df(df_boditem)
        df_out_boditem[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_boditem = df_out_boditem[df_BODItem_columns]

        df_out_sopadjust = rename_and_delete_df(df_sopadjust)
        df_out_sopadjust[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_sopadjust = df_out_sopadjust[df_SOPAdjust_columns]

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_boditem, 'output table create .... df_out_boditem', True)
        print_df(df_out_sopadjust, 'output table create .... df_out_sopadjust', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_boditem = pd.DataFrame(columns=df_BODItem_columns)
        df_out_sopadjust = pd.DataFrame(columns=df_SOPAdjust_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_boditem = pd.DataFrame(columns=df_BODItem_columns)
        df_out_sopadjust = pd.DataFrame(columns=df_SOPAdjust_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
