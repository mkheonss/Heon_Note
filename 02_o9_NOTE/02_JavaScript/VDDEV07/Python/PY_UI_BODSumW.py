"""
* 프로그램명
    - PY_UI_BODSumW

* 내용

* 변경이력
    - 2024.10.04 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_Item         : Select ([Item].[Item] * [Item].[ProductType] * [Item].[Item Stage].filter(#.Name in {"SET", "KD", "LCM", "OPEN_CELL", "PANEL"})) on row where {Version.[Version Name], Measure.[Item Site Asn_Cur Status] in {"ACTIVE", "PLANNED"}};
    - df_in_BODAll       : Select ([Location].[Location] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({Measure.[BOD All_DC Site], Measure.[BOD All_Hub BOD LT], Measure.[BOD All_Hub Ship LT], Measure.[BOD All_Hub Site], Measure.[BOD All_Hub Total LT], Measure.[BOD All_Hub Trans Mode], Measure.[BOD All_KD BOD LT], Measure.[BOD All_KD Code], Measure.[BOD All_KD Ship LT], Measure.[BOD All_KD Site], Measure.[BOD All_KD Total LT], Measure.[BOD All_KD Trans Mode], Measure.[BOD All_LCM BOD LT], Measure.[BOD All_LCM Code], Measure.[BOD All_LCM Ship LT], Measure.[BOD All_LCM Site], Measure.[BOD All_LCM Total LT], Measure.[BOD All_LCM Trans Mode], Measure.[BOD All_OCell BOD LT], Measure.[BOD All_OCell Code], Measure.[BOD All_OCell Ship LT], Measure.[BOD All_OCell Site], Measure.[BOD All_OCell Total LT], Measure.[BOD All_OCell Trans Mode], Measure.[BOD All_SET BOD LT], Measure.[BOD All_SET Ship LT], Measure.[BOD All_SET Site], Measure.[BOD All_SET Total LT], Measure.[BOD All_SET Trans Mode]}) on column where {Version.[Version Name], Measure.[BOD All_BOD Prty] == 1};
    - df_in_BODItemW     : Select ([Item].[Item] * &MDMHorizon * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item W_Prty], Measure.[BOD Item W_Shipment LT], Measure.[BOD Item W_BOD LT]}) on column where{Version.[Version Name]};
    - df_in_BODItemMtrlW : Select (&MDMHorizon * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl W_Factory Out], Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Intransit LT], Measure.[BOD Item Mtrl W_Port To Port], Measure.[BOD Item Mtrl W_Supplier], Measure.[BOD Item Mtrl W_Total LT]}) on column where {Version.[Version Name]};
    - df_in_TimeWeek     : Select ( &MDMHorizon ) on row;

* Flow Summary
    - df_out_BODSumW

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BODSumW

* 데이타 초기화
    - DELETE DATA FOR MODEL [BOD Sum W] where {Version.[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_BODSumW] for measures {[BOD Sum W_DC BOD LT]}
        scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] ) on row, ({Measure.[BOD Sum W_DC BOD LT], Measure.[BOD Sum W_DC Ship LT], Measure.[BOD Sum W_DC Trans Time],
        Measure.[BOD Sum W_Hub BOD LT], Measure.[BOD Sum W_Hub Ship LT], Measure.[BOD Sum W_Hub Trans Time], Measure.[BOD Sum W_KD BOD LT], Measure.[BOD Sum W_KD Ship LT], Measure.[BOD Sum W_KD Trans Time],
        Measure.[BOD Sum W_LCM BOD LT], Measure.[BOD Sum W_LCM Ship LT], Measure.[BOD Sum W_LCM Trans Time], Measure.[BOD Sum W_OCell BOD LT], Measure.[BOD Sum W_OCell Ship LT], Measure.[BOD Sum W_OCell Trans Time],
        Measure.[BOD Sum W_SET BOD LT], Measure.[BOD Sum W_SET Ship LT], Measure.[BOD Sum W_SET Trans Time], Measure.[BOD Sum W_Tot BOD LT], Measure.[BOD Sum W_Tot Ship LT], Measure.[BOD Sum W_Tot Trans Time]}) on column;

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
str_instance = 'PY_UI_BODSumW'
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
            df_in_Item = read_csv_file("df_in_Item")
            df_in_BODAll = read_csv_file("df_in_BODAll")
            df_in_BODItemW = read_csv_file("df_in_BODItemW")
            df_in_BODItemMtrlW = read_csv_file("df_in_BODItemMtrlW")
            df_in_TimeWeek = read_csv_file("df_in_TimeWeek")


        dataframes = {
            'df_in_Item': df_in_Item,
            'df_in_BODAll': df_in_BODAll,
            'df_in_BODItemW': df_in_BODItemW,
            'df_in_BODItemMtrlW': df_in_BODItemMtrlW,
            'df_in_TimeWeek': df_in_TimeWeek,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1(End) : Check memory usage & runtime')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2(Start) : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'

        LOCATION_COLUMN = 'Location.[Location]'
        LOCATION_X_COLUMN = 'Location.[Location]_x'
        LOCATION_Y_COLUMN = 'Location.[Location]_y'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_X_COLUMN = 'Item.[Item]_x'
        ITEM_Y_COLUMN = 'Item.[Item]_y'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_TYPE_COLUMN = 'Item.[ProductType]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TIME_WEEK_COLUMN = 'Time.[Week]'

        BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN = 'BOD Item Mtrl W_Factory Out'
        BOD_ITEM_MTRL_W_GR_LT_COLUMN = 'BOD Item Mtrl W_GR LT'
        BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN = 'BOD Item Mtrl W_Intransit LT'
        BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN = 'BOD Item Mtrl W_Port To Port'
        BOD_ITEM_MTRL_W_SUPPLIER_COLUMN = 'BOD Item Mtrl W_Supplier'
        BOD_ITEM_MTRL_W_TOTAL_LT_COLUMN = 'BOD Item Mtrl W_Total LT'

        BOD_ITEM_BOD_FROZEN_COLUMN = 'BOD Item_BOD Frozen'
        BOD_ITEM_BOD_LT_COLUMN = 'BOD Item_BOD LT'
        BOD_ITEM_BOD_LT_INHERIT_COLUMN = 'BOD Item_BOD LT_Inherit'
        BOD_ITEM_CUR_STATUS_COLUMN = 'BOD Item_Cur Status'
        BOD_ITEM_EFF_ENDDATE_COLUMN = 'BOD Item_Eff Enddate'
        BOD_ITEM_EFF_STARTDATE_COLUMN = 'BOD Item_Eff Startdate'
        BOD_ITEM_MIN_LOT_UOM_COLUMN = 'BOD Item_Min Lot UOM'
        BOD_ITEM_MULTI_LOT_QTY_COLUMN = 'BOD Item_Multi Lot Qty'
        BOD_ITEM_NEED_CHECK_COLUMN = 'BOD Item_Need Check'
        BOD_ITEM_PERIOD_SET_DETAIL_COLUMN = 'BOD Item_Period SET Detail'
        BOD_ITEM_PERIOD1_COLUMN = 'BOD Item_Period1'
        BOD_ITEM_PERIOD2_COLUMN = 'BOD Item_Period2'
        BOD_ITEM_PERIOD3_COLUMN = 'BOD Item_Period3'
        BOD_ITEM_PERIORITY_COLUMN = 'BOD Item_Priority'
        BOD_ITEM_PERIORITY_INHERIT_COLUMN = 'BOD Item_Priority_Inherit'
        BOD_ITEM_PROD_ITEM_COLUMN = 'BOD Item_Prod Item'
        BOD_ITEM_SHIPMENT_LT_COLUMN = 'BOD Item_Shipment LT'
        BOD_ITEM_SHIPMENT_LT_INHERIT_COLUMN = 'BOD Item_Shipment LT_Inherit'
        BOD_ITEM_TIME_PHASED_BOD_COLUMN = 'BOD Item_Time Phased BOD'
        BOD_ITEM_TIME_PHASED_PRTY_COLUMN = 'BOD Item_Time Phased Prty'
        BOD_ITEM_TIME_PHASED_SHIPMENT_COLUMN = 'BOD Item_Time Phased Shipment'
        BOD_ITEM_TO_ITEM_COLUMN = 'BOD Item_To Item'

        BOD_ITEM_W_PRTY_COLUMN = 'BOD Item W_Prty'
        BOD_ITEM_W_SHIPMENT_LT_COLUMN = 'BOD Item W_Shipment LT'
        BOD_ITEM_W_BOD_LT_COLUMN = 'BOD Item W_BOD LT'
        BOD_ITEM_W_TOTAL_LT_COLUMN = 'BOD Item W_Total LT'

        BOD_ALL_BOD_PRTY_COLUMN = 'BOD All_BOD Prty'

        BOD_ALL_DC_BOD_LT_COLUMN = 'BOD All_DC BOD LT'
        BOD_ALL_DC_BOD_PRTY_COLUMN = 'BOD All_DC BOD Prty'
        BOD_ALL_DC_SHIP_LT_COLUMN = 'BOD All_DC Ship LT'
        BOD_ALL_DC_SITE_COLUMN = 'BOD All_DC Site'
        BOD_ALL_DC_TRANS_MODE_COLUMN = 'BOD All_DC Trans Mode'
        BOD_ALL_DC_TOTAL_LT_COLUMN = 'BOD All_DC Total LT'

        BOD_ALL_HUB_BOD_LT_COLUMN = 'BOD All_Hub BOD LT'
        BOD_ALL_HUB_BOD_PRTY_COLUMN = 'BOD All_Hub BOD Prty'
        BOD_ALL_HUB_SHIP_LT_COLUMN = 'BOD All_Hub Ship LT'
        BOD_ALL_HUB_SITE_COLUMN = 'BOD All_Hub Site'
        BOD_ALL_HUB_TRANS_MODE_COLUMN = 'BOD All_Hub Trans Mode'
        BOD_ALL_HUB_TOTAL_LT_COLUMN = 'BOD All_Hub Total LT'

        BOD_ALL_KD_BOD_LT_COLUMN = 'BOD All_KD BOD LT'
        BOD_ALL_KD_BOD_PRTY_COLUMN = 'BOD All_KD BOD Prty'
        BOD_ALL_KD_CODE_COLUMN = 'BOD All_KD Code'
        BOD_ALL_KD_SHIP_LT_COLUMN = 'BOD All_KD Ship LT'
        BOD_ALL_KD_SITE_COLUMN = 'BOD All_KD Site'
        BOD_ALL_KD_TRANS_MODE_COLUMN = 'BOD All_KD Trans Mode'
        BOD_ALL_KD_TOTAL_LT_COLUMN = 'BOD All_KD Total LT'

        BOD_ALL_LCM_BOD_LT_COLUMN = 'BOD All_LCM BOD LT'
        BOD_ALL_LCM_BOD_PRTY_COLUMN = 'BOD All_LCM BOD Prty'
        BOD_ALL_LCM_CODE_COLUMN = 'BOD All_LCM Code'
        BOD_ALL_LCM_SHIP_LT_COLUMN = 'BOD All_LCM Ship LT'
        BOD_ALL_LCM_SITE_COLUMN = 'BOD All_LCM Site'
        BOD_ALL_LCM_TRANS_MODE_COLUMN = 'BOD All_LCM Trans Mode'
        BOD_ALL_LCM_TOTAL_LT_COLUMN = 'BOD All_LCM Total LT'

        BOD_ALL_MIN_LT_FLAG_COLUMN = 'BOD All_Min LT Flag'

        BOD_ALL_OCELL_BOD_LT_COLUMN = 'BOD All_OCell BOD LT'
        BOD_ALL_OCELL_BOD_PRTY_COLUMN = 'BOD All_OCell BOD Prty'
        BOD_ALL_OCELL_CODE_COLUMN = 'BOD All_OCell Code'
        BOD_ALL_OCELL_SHIP_LT_COLUMN = 'BOD All_OCell Ship LT'
        BOD_ALL_OCELL_SITE_COLUMN = 'BOD All_OCell Site'
        BOD_ALL_OCELL_TRANS_MODE_COLUMN = 'BOD All_OCell Trans Mode'
        BOD_ALL_OCELL_TOTAL_LT_COLUMN = 'BOD All_OCell Total LT'

        BOD_ALL_SET_BOD_LT_COLUMN = 'BOD All_SET BOD LT'
        BOD_ALL_SET_BOD_PRTY_COLUMN = 'BOD All_SET BOD Prty'
        BOD_ALL_SET_BOM_VERSION_COLUMN = 'BOD All_SET BOM Version'
        BOD_ALL_SET_SOP_COLUMN = 'BOD All_SET SOP'
        BOD_ALL_SET_SHIP_LT_COLUMN = 'BOD All_SET Ship LT'
        BOD_ALL_SET_SITE_COLUMN = 'BOD All_SET Site'
        BOD_ALL_SET_TRANS_MODE_COLUMN = 'BOD All_SET Trans Mode'
        BOD_ALL_SET_TOTAL_LT_COLUMN = 'BOD All_SET Total LT'

        BOD_ALL_TOT_BOD_LT_COLUMN = 'BOD All_Tot BOD LT'
        BOD_ALL_TOT_SHIP_LT_COLUMN = 'BOD All_Tot Ship LT'

        BOD_SUM_W_DC_BOD_LT_COLUMN = 'BOD Sum W_DC BOD LT'
        BOD_SUM_W_DC_SHIP_LT_COLUMN = 'BOD Sum W_DC Ship LT'
        BOD_SUM_W_DC_TOTAL_LT_COLUMN = 'BOD Sum W_DC Total LT'

        BOD_SUM_W_HUB_BOD_LT_COLUMN = 'BOD Sum W_Hub BOD LT'
        BOD_SUM_W_HUB_SHIP_LT_COLUMN = 'BOD Sum W_Hub Ship LT'
        BOD_SUM_W_HUB_TOTAL_LT_COLUMN = 'BOD Sum W_Hub Total LT'

        BOD_SUM_W_KD_BOD_LT_COLUMN = 'BOD Sum W_KD BOD LT'
        BOD_SUM_W_KD_SHIP_LT_COLUMN = 'BOD Sum W_KD Ship LT'
        BOD_SUM_W_KD_TOTAL_LT_COLUMN = 'BOD Sum W_KD Total LT'

        BOD_SUM_W_LCM_BOD_LT_COLUMN = 'BOD Sum W_LCM BOD LT'
        BOD_SUM_W_LCM_SHIP_LT_COLUMN = 'BOD Sum W_LCM Ship LT'
        BOD_SUM_W_LCM_TOTAL_LT_COLUMN = 'BOD Sum W_LCM Total LT'

        BOD_SUM_W_OCELL_BOD_LT_COLUMN = 'BOD Sum W_OCell BOD LT'
        BOD_SUM_W_OCELL_SHIP_LT_COLUMN = 'BOD Sum W_OCell Ship LT'
        BOD_SUM_W_OCELL_TOTAL_LT_COLUMN = 'BOD Sum W_OCell Total LT'

        BOD_SUM_W_SET_BOD_LT_COLUMN = 'BOD Sum W_SET BOD LT'
        BOD_SUM_W_SET_SHIP_LT_COLUMN = 'BOD Sum W_SET Ship LT'
        BOD_SUM_W_SET_TOTAL_LT_COLUMN = 'BOD Sum W_SET Total LT'

        SET_VALUE = 'SET'
        LCM_VALUE = 'LCM'

        df_version_columns = [VERSION_NAME_COLUMN]

        df_bod_sumw_columns = [
            TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_COLUMN,
            BOD_SUM_W_HUB_BOD_LT_COLUMN, BOD_SUM_W_HUB_SHIP_LT_COLUMN, BOD_SUM_W_HUB_TOTAL_LT_COLUMN,
            BOD_SUM_W_KD_BOD_LT_COLUMN, BOD_SUM_W_KD_SHIP_LT_COLUMN, BOD_SUM_W_KD_TOTAL_LT_COLUMN,
            BOD_SUM_W_OCELL_BOD_LT_COLUMN, BOD_SUM_W_OCELL_SHIP_LT_COLUMN, BOD_SUM_W_OCELL_TOTAL_LT_COLUMN,
            BOD_SUM_W_SET_BOD_LT_COLUMN, BOD_SUM_W_SET_SHIP_LT_COLUMN, BOD_SUM_W_SET_TOTAL_LT_COLUMN,
            BOD_SUM_W_LCM_BOD_LT_COLUMN, BOD_SUM_W_LCM_SHIP_LT_COLUMN, BOD_SUM_W_LCM_TOTAL_LT_COLUMN,
        ]

        df_fn_bod_sumw_columns = df_version_columns + df_bod_sumw_columns

        step('=====> STEP 2(End) : Check memory usage & runtime')

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')


        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_BODAll = df_in_BODAll[
        #     (df_in_BODAll[LOCATION_COLUMN] == 'S348WD20') & (df_in_BODAll[ITEM_COLUMN] == 'QN65QN90DAFXZA')
        # ].copy()
        # print_df(df_in_BODAll, 'STEP3 by 1.1 ____ df_in_BODAll .... filter', True)
        #
        # df_in_BODItemW = df_in_BODItemW[
        #     (df_in_BODItemW[ITEM_COLUMN] == 'QN65QN90DAFXZA') &  (df_in_BODItemW[SUB_LOCATION_COLUMN] == 'S348WD20')
        # ].copy()
        # print_df(df_in_BODItemW, 'STEP3 by 1.2 ____ df_in_BODItemW .... filter', True)
        # ------------------ 테스트 디버깅용 ------------------ end



        df_in_TimeWeek = df_in_TimeWeek[[TIME_WEEK_COLUMN]].drop_duplicates()



        # ====================> Prework (Start) : BOD Data(SET, LCM) create

        # 1. Item.[item stage] filter & item dataframe create
        #   1.1 item set create
        set_SET_item_condition = df_in_Item[ITEM_STAGE_COLUMN].isin([SET_VALUE])
        df_set_item = df_in_Item[set_SET_item_condition].copy()

        #   1.2 item lcm create
        set_LCM_item_condition = df_in_Item[ITEM_STAGE_COLUMN].isin([LCM_VALUE])
        df_lcm_item = df_in_Item[set_LCM_item_condition].copy()



        # 2. bod_item create
        #   2.1
        #       2025.11.21 TRANS_TIME = BOD LT ( Port to Port LT + GR LT ) (SET/LCM BOD List & Item 화면에서의 정의)
        #       BOD LT = TRANS_TIME + SHIPMENT LT (Factory Out) (All BOD, Summary BOD 화면에서의 정의)
        #       2025.12.09
        #       BOD LT = BOD LT ( Port to Port LT + GR LT ) (SET/LCM BOD List & Item 화면에서의 정의)
        #       TOTAL LT = TRANS_TIME + SHIPMENT LT (Factory Out) (All BOD, Summary BOD 화면에서의 정의)
        df_in_BODItemW[BOD_ITEM_W_TOTAL_LT_COLUMN] = np.where(
            df_in_BODItemW[BOD_ITEM_W_BOD_LT_COLUMN].isna() & df_in_BODItemW[BOD_ITEM_W_SHIPMENT_LT_COLUMN].isna(),
            np.nan,
            df_in_BODItemW[BOD_ITEM_W_BOD_LT_COLUMN].fillna(0) + df_in_BODItemW[BOD_ITEM_W_SHIPMENT_LT_COLUMN].fillna(0)
        )
        print_df(df_in_BODItemW, 'STEP3 by 2.1 ____ df_in_BODItemW .... columns add')

        #   2.2 bod_item set create
        df_bod_itemW_set = pd.merge(df_in_BODItemW, df_set_item, on=[ITEM_COLUMN], how='inner')
        print_df(df_bod_itemW_set, 'STEP3 by 2.2 ____ df_bod_itemW_set .... merge[df_in_BODItemW, df_set_item]')


        #   2.3 bod_item lcm create
        df_bod_itemW_lcm = pd.merge(df_in_BODItemW, df_lcm_item, on=[ITEM_COLUMN], how='inner')
        print_df(df_bod_itemW_lcm, 'STEP3 by 2.3 ____ df_bod_itemW_lcm .... merge[df_in_BODItemW, df_lcm_item]')



        # 3. df_in_BODAll Week 생성
        #   3.1 컬럼타입 설정
        columns = [BOD_ALL_OCELL_SITE_COLUMN, BOD_ALL_OCELL_TRANS_MODE_COLUMN,]
        for column in columns:
            df_in_BODAll[column] = df_in_BODAll[column].astype(str)

        df_in_BODAll = df_in_BODAll.assign(key=1)
        df_in_TimeWeek = df_in_TimeWeek.assign(key=1)
        df_in_BODAll = pd.merge(df_in_BODAll, df_in_TimeWeek, how="outer").drop(columns=['key']).drop_duplicates()
        print_df(df_in_BODAll, 'STEP3 by 3.1 ____ df_in_BODAll .... week cartesian')

        # ====================> Prework (End)

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # ====================> STEP4 by 1 (Start)

        # HUB_SITE는 DC_SITE가 Null인 경우 Null처리 (하혜진P요청 - '25.11.17) 복구 후 SET BOD LT 정보 매핑
        df_in_BODAll.loc[df_in_BODAll[BOD_ALL_HUB_SITE_COLUMN].isna(),BOD_ALL_HUB_SITE_COLUMN] = df_in_BODAll[LOCATION_COLUMN]

        # 1.1 BODItemW SET create
        df_in_BODAll = pd.merge(df_in_BODAll, df_bod_itemW_set, how='left',
                                left_on=[ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, BOD_ALL_HUB_SITE_COLUMN,
                                         BOD_ALL_SET_TRANS_MODE_COLUMN, TIME_WEEK_COLUMN],
                                right_on=[ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN,
                                          TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_in_BODAll, 'STEP4 by 1.1 ____ df_in_BODAll .... merged')

        # HUB_SITE는 DC_SITE가 Null인 경우 Null처리 (하혜진P요청 - '25.11.17)
        # df_in_BODAll.loc[df_in_BODAll[BOD_ALL_DC_SITE_COLUMN].isna(),BOD_ALL_HUB_SITE_COLUMN] = np.nan

        #   1.1.1 조건에 따라 컬럼 a 값을 업데이트
        df_in_BODAll[BOD_SUM_W_SET_TOTAL_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN], df_in_BODAll[BOD_ALL_SET_TOTAL_LT_COLUMN])

        df_in_BODAll[BOD_SUM_W_SET_BOD_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_W_BOD_LT_COLUMN], df_in_BODAll[BOD_ALL_SET_BOD_LT_COLUMN])

        df_in_BODAll[BOD_SUM_W_SET_SHIP_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_W_SHIPMENT_LT_COLUMN], df_in_BODAll[BOD_ALL_SET_SHIP_LT_COLUMN])

        #   1.1.2 컬럼 삭제 및 변경, 설정
        df_in_BODAll[BOD_SUM_W_HUB_TOTAL_LT_COLUMN] = df_in_BODAll[BOD_ALL_HUB_TOTAL_LT_COLUMN]
        df_in_BODAll[BOD_SUM_W_HUB_BOD_LT_COLUMN] = df_in_BODAll[BOD_ALL_HUB_BOD_LT_COLUMN]
        df_in_BODAll[BOD_SUM_W_HUB_SHIP_LT_COLUMN] = df_in_BODAll[BOD_ALL_HUB_SHIP_LT_COLUMN]

        df_in_BODAll.rename(columns={LOCATION_X_COLUMN: LOCATION_COLUMN}, inplace=True)
        df_in_BODAll.drop(columns=[
            LOCATION_Y_COLUMN, SUB_LOCATION_COLUMN,TRANS_MODE_COLUMN, ITEM_PRODUCT_TYPE_COLUMN, ITEM_STAGE_COLUMN,
            BOD_ITEM_W_PRTY_COLUMN, BOD_ITEM_W_SHIPMENT_LT_COLUMN, BOD_ITEM_W_BOD_LT_COLUMN, BOD_ITEM_W_TOTAL_LT_COLUMN,
        ], inplace=True)
        print_df(df_in_BODAll, 'STEP4 by 1.1.2 ____ df_in_BODAll .... final')



        # 1.2 BODItemW LCM create
        #   1.2.1
        df_in_BODAll = pd.merge(df_in_BODAll, df_bod_itemW_lcm, how='left',
                                left_on=[BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN,
                                         BOD_ALL_SET_SITE_COLUMN, BOD_ALL_LCM_TRANS_MODE_COLUMN, TIME_WEEK_COLUMN],
                                right_on=[ITEM_COLUMN, LOCATION_COLUMN,
                                          SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_in_BODAll, 'STEP4 by 1.2.1 ____ df_in_BODAll .... merged')


        #   1.2.2 컬럼 삭제 및 변경, 설정
        df_in_BODAll[BOD_SUM_W_LCM_TOTAL_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN], df_in_BODAll[BOD_ALL_LCM_TOTAL_LT_COLUMN])

        df_in_BODAll[BOD_SUM_W_LCM_BOD_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_W_BOD_LT_COLUMN], df_in_BODAll[BOD_ALL_LCM_BOD_LT_COLUMN])

        df_in_BODAll[BOD_SUM_W_LCM_SHIP_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_W_TOTAL_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_W_SHIPMENT_LT_COLUMN], df_in_BODAll[BOD_ALL_LCM_SHIP_LT_COLUMN])

        df_in_BODAll[BOD_SUM_W_KD_TOTAL_LT_COLUMN] = df_in_BODAll[BOD_ALL_KD_TOTAL_LT_COLUMN]
        df_in_BODAll[BOD_SUM_W_KD_BOD_LT_COLUMN] = df_in_BODAll[BOD_ALL_KD_BOD_LT_COLUMN]
        df_in_BODAll[BOD_SUM_W_KD_SHIP_LT_COLUMN] = df_in_BODAll[BOD_ALL_KD_SHIP_LT_COLUMN]

        df_in_BODAll.rename(columns={ITEM_X_COLUMN: ITEM_COLUMN, LOCATION_X_COLUMN: LOCATION_COLUMN,}, inplace=True)
        df_in_BODAll.drop(columns=[
            LOCATION_Y_COLUMN, ITEM_PRODUCT_TYPE_COLUMN, ITEM_STAGE_COLUMN, ITEM_Y_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_W_PRTY_COLUMN, BOD_ITEM_W_SHIPMENT_LT_COLUMN, BOD_ITEM_W_BOD_LT_COLUMN, BOD_ITEM_W_TOTAL_LT_COLUMN,
        ], inplace=True)
        print_df(df_in_BODAll, 'STEP4 by 1.2.2 ____ df_in_BODAll .... final')



        # 1.3 BODItemW OCELL create
        #   1.3.1 ( 2025.11.02 : OCell은 SET공장으로 납품 관리함 )
        df_in_BODAll = pd.merge(df_in_BODAll, df_in_BODItemMtrlW, how='left',
                                left_on=[BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_OCELL_SITE_COLUMN,
                                         BOD_ALL_SET_SITE_COLUMN, BOD_ALL_OCELL_TRANS_MODE_COLUMN, TIME_WEEK_COLUMN],
                                right_on=[ITEM_METERIAL_COLUMN, LOCATION_COLUMN,
                                          SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN])
        print_df(df_in_BODAll, 'STEP4 by 1.3.1 ____ df_in_BODAll .... merged')

        #   1.3.2 컬럼 삭제 및 변경, 설정
        df_in_BODAll[BOD_SUM_W_OCELL_TOTAL_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN], df_in_BODAll[BOD_ALL_OCELL_TOTAL_LT_COLUMN]
        )

        df_in_BODAll[BOD_SUM_W_OCELL_BOD_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN].fillna(0) + df_in_BODAll[BOD_ITEM_MTRL_W_GR_LT_COLUMN].fillna(0),
            df_in_BODAll[BOD_ALL_OCELL_BOD_LT_COLUMN]
        )

        df_in_BODAll[BOD_SUM_W_OCELL_SHIP_LT_COLUMN] = np.where(
            df_in_BODAll[BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN].notna(),
            df_in_BODAll[BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN], df_in_BODAll[BOD_ALL_OCELL_SHIP_LT_COLUMN]
        )

        df_in_BODAll.rename(columns={LOCATION_X_COLUMN: LOCATION_COLUMN}, inplace=True)

        df_in_BODAll = df_in_BODAll[df_bod_sumw_columns].drop_duplicates()
        print_df(df_in_BODAll, 'STEP4 by 1.3.2 ____ df_in_BODAll .... final')

        # ====================> STEP4 by 1 (End)

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_BODSumW = rename_and_delete_df(df_in_BODAll)

        # 최종 아웃풋 컬럼 설정
        df_out_BODSumW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_BODSumW = df_out_BODSumW[df_fn_bod_sumw_columns]
        df_out_BODSumW = df_out_BODSumW.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        refill_columns = [LOCATION_COLUMN, ITEM_COLUMN,]
        for col in refill_columns:
            df_out_BODSumW[col] = df_out_BODSumW[col].fillna('-')

        dataframes = {
            'df_out_BODSumW': df_out_BODSumW,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODSumW = pd.DataFrame(columns=df_fn_bod_sumw_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BODSumW = pd.DataFrame(columns=df_fn_bod_sumw_columns)
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