"""
* 프로그램명
    - PY_UI_SOPAdjustSET

* 내용
    - SET제품 기준 SOP Adjust 후 LCM/BOM Version 기준으로 데이터 할당하는 로직 반영 (자재가용량 점검, 확정구간에서 처리 등)


* 변경이력
    - 2024.10.29 / 권태우 / Create
    - 2024.12.16 / 권태우 / 보정 프로세스 재설계

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek              : Select (&CurrentWeek);
    - df_in_SOP_W_Max             : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [To Time].[To Week] * [To Location].[To Location] * [Sequence].[Sequence] * [To Item].[To Item] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Week2].[Week2] * [Item Component].[Item Component] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row, ({Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID]}) on column orderby [Sequence].[Sequence].Name desc Limit 1;
    - df_in_SOPW                  : Select (Version.[Version Name] * [Item].[Item] * &MDMHorizon * [To Location].[To Location] * [To Item].[To Item] * [Location].[Location] * [To Time].[To Week] * [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Item Component].[Item Component] * [Week2].[Week2] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row, ({Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID]}) on column;
    - df_in_SOPAdjustSETRemainMtrl: Select (Version.[Version Name] * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[SOP Adjust SET Remain Mtrl_Adj Used Qty], Measure.[SOP Adjust SET Remain Mtrl_Create Time], Measure.[SOP Adjust SET Remain Mtrl_Created By], Measure.[SOP Adjust SET Remain Mtrl_Cur Remain Qty], Measure.[SOP Adjust SET Remain Mtrl_Init Remain Supply Qty], Measure.[SOP Adjust SET Remain Mtrl_Update Time], Measure.[SOP Adjust SET Remain Mtrl_Updated By]}) on column;
    - df_in_SOPAdjustmentSETWInc  : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [Location].[Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP Adjust SET W_Chg Qty], Measure.[SOP Adjust SET W_SOP Adj Qty], Measure.[SOP Adjust SET W_SOP Qty], Measure.[SOP Adjust SET W_Before Adj Qty]}) on column.filter(((Measure.[SOP Adjust SET W_SOP Adj Qty] != Measure.[SOP Adjust SET W_Before Adj Qty])) && Measure.[SOP Adjust SET W_SOP Adj Qty] > 0 && Measure.[SOP Adjust SET W_Chg Qty] > 0);
    - df_in_SOPAdjustmentSETWDec  : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [Location].[Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP Adjust SET W_Chg Qty], Measure.[SOP Adjust SET W_SOP Adj Qty], Measure.[SOP Adjust SET W_SOP Qty], Measure.[SOP Adjust SET W_Before Adj Qty]}) on column.filter(((Measure.[SOP Adjust SET W_SOP Adj Qty] != Measure.[SOP Adjust SET W_Before Adj Qty])) && Measure.[SOP Adjust SET W_SOP Adj Qty] > 0 && Measure.[SOP Adjust SET W_Chg Qty] < 0);
    - df_in_SOPAdjustmentSETWReg  : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [Location].[Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[SOP Adjust SET W_Chg Qty], Measure.[SOP Adjust SET W_SOP Adj Qty], Measure.[SOP Adjust SET W_SOP Qty], Measure.[SOP Adjust SET W_Before Adj Qty]}) on column.filter((Measure.[SOP Adjust SET W_Chg Qty] == Measure.[SOP Adjust SET W_SOP Adj Qty]) && Measure.[SOP Adjust SET W_SOP Qty] == 0 && (Measure.[SOP Adjust SET W_Before Adj Qty] == 0 || isnull(Measure.[SOP Adjust SET W_Before Adj Qty])) && Measure.[SOP Adjust SET W_Chg Qty] > 0);
    - df_in_BOMVersionPrtyW       : Select (Version.[Version Name] * &SETItem * &MPHorizon * &SETLocation * &ItemMtrlOpenCell * [BOM Info].[BOM Version] * [Item Component].[Item Component] ) on row, ({Measure.[BOM Version Prty W_Prty]}) on column;
    - df_in_SOPLCMW               : Select (Version.[Version Name] * [To Item].[To Item] * [Location].[Location] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [To Trans Mode].[To Trans Mode] ) on row,  ({Measure.[SOP Adjust LCM W_Chg Qty], Measure.[SOP Adjust LCM W_SOP Adj Qty], Measure.[SOP Adjust LCM W_SOP Qty], Measure.[SOP Adjust LCM W_Before Adj Qty]}) on column;

* Flow Summary
    - 1. SET SOP Adjustr 수량을 SOP W MG에 데이터 할당
    - 2. Version별로 데이터 처리


* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_SOPWQtyClean
    - df_out_SOPW
    - df_out_SOPAdjustSETW
    - df_out_SOPAdjustSETRemainMtrl
    - df_out_SOPAdjustLCMW
    - df_out_SOPAdjustLCMWAdj

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SOPAdjustSET] for measures {[SOP W_SET MFG Qty]}
        using scope (Version.[Version Name].filter(#.Name in {"CWV_MP"}))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPW / MG:  SOP W
        Select (&MPV * [Item].[Item] * [Time].[Week] * [Location].[Location] * [To Time].[To Week] * [To Location].[To Location] * [Sequence].[Sequence] * [To Item].[To Item] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Week2].[Week2] * [Item Component].[Item Component] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row,
        ({Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM SOP Qty]}) on column;
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
str_instance = 'PY_UI_SOPAdjustSET'
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
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_SOP_W_Max = read_csv_file("df_in_SOP_W_Max")
            df_in_SOPW = read_csv_file("df_in_SOPW")
            df_in_SOPAdjustmentSETWInc = read_csv_file("df_in_SOPAdjustmentSETWInc")
            df_in_SOPAdjustmentSETWDec = read_csv_file("df_in_SOPAdjustmentSETWDec")
            df_in_SOPAdjustmentSETWReg = read_csv_file("df_in_SOPAdjustmentSETWReg")
            df_in_SOPAdjustSETRemainMtrl = read_csv_file("df_in_SOPAdjustSETRemainMtrl")
            df_in_BOMVersionPrtyW = read_csv_file("df_in_BOMVersionPrtyW")
            df_in_SOPLCMW = read_csv_file("df_in_SOPLCMW")


        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_SOP_W_Max': df_in_SOP_W_Max,
            'df_in_SOPW': df_in_SOPW,
            'df_in_SOPAdjustmentSETWInc': df_in_SOPAdjustmentSETWInc,
            'df_in_SOPAdjustmentSETWDec': df_in_SOPAdjustmentSETWDec,
            'df_in_SOPAdjustmentSETWReg': df_in_SOPAdjustmentSETWReg,
            'df_in_SOPAdjustSETRemainMtrl': df_in_SOPAdjustSETRemainMtrl,
            'df_in_BOMVersionPrtyW': df_in_BOMVersionPrtyW,
            'df_in_SOPLCMW': df_in_SOPLCMW,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        CODE_MAP_LCM_PROD_ITEM_COLUMN = 'Code Map LCM_Prod Item'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        LOCATION_COLUMN = 'Location.[Location]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        SOP_ID_COLUMN = 'SOP ID.[SOP ID]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        BOM_VERSION_PRTY_W_PRTY_COLUMN = 'BOM Version Prty W_Prty'

        BOM_INFO_BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_BOM_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_EFF_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'
        BOM_MASTER_PERIORITY_COLUMN = 'BOM Master_Priority'
        BOM_MASTER_PRTY_COLUMN = 'BOM Master_Prty'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'

        TO_TO_TIME_TO_WEEK_COLUMN = 'to.[To Time].[To Week]'
        TO_TO_LOCATION_TO_LOCATION_COLUMN = 'to.[To Location].[To Location]'
        TO_ORDERLINE_ID_COLUMN = 'to.[Documents].[OrderlineID]'
        TO_TIME_WEEK_COLUMN = 'to.[Time].[Week]'
        TO_TO_ITEM_TO_ITEM_COLUMN = 'to.[To Item].[To Item]'
        TO_ITEM_COLUMN = 'to.[Item].[Item]'
        TO_ACTIVITY1_COLUMN = 'to.[Activity1].[Activity1]'
        TO_LOCATION_COLUMN = 'to.[Location].[Location]'
        TO_ACTIVITY3_COLUMN = 'to.[Activity3].[Activity3]'
        TO_DEMAND_ID_COLUMN = 'to.[Demand].[DemandID]'
        TO_CUSTOMER_GROUP_COLUMN = 'to.[Sales Domain].[Customer Group]'
        TO_DEMAND_TYPE_COLUMN = 'to.[Demand Type].[Demand Type]'
        TO_ACTIVITY2_COLUMN = 'to.[Activity2].[Activity2]'

        SOP_W_ITEM_MTRL_COLUMN = 'SOP W_Item Mtrl'
        SOP_W_PRD_ITEM_COLUMN = 'SOP W_Prd Item'
        SOP_W_SOP_ID_COLUMN = 'SOP W_SOP ID'
        SOP_W_BOM_CFM_W_COLUMN = 'SOP W_BOM Cfm W'
        SOP_W_BOM_STATUS_COLUMN = 'SOP W_BOM Status'
        SOP_W_SHT_REASON_COLUMN = 'SOP W_Sht Reason'
        SOP_W_CHG_REASON_COLUMN = 'SOP W_Chg Reason'
        SOP_W_LCM_PLANT_COLUMN = 'SOP W_LCM Plant'

        SOP_W_SOP_ADJ_QTY_COLUMN = 'SOP W_SOP Adj Qty'
        SOP_W_SET_MFG_ADJ_QTY_COLUMN = 'SOP W_SET MFG Adj Qty'
        SOP_W_SOP_QTY_COLUMN = 'SOP W_SOP Qty'
        SOP_W_CHG_QTY_COLUMN = 'SOP W_Chg Qty'
        SOP_W_SET_MFG_CHG_QTY_COLUMN = 'SOP W_SET MFG Chg Qty'
        SOP_W_LCM_MFG_ADJ_QTY_COLUMN = 'SOP W_LCM MFG Adj Qty'
        SOP_W_SHT_QTY_COLUMN = 'SOP W_Sht Qty'
        SOP_W_LCM_CHG_QTY_COLUMN = 'SOP W_LCM Chg Qty'
        SOP_W_LCM_SOP_QTY_COLUMN = 'SOP W_LCM SOP Qty'
        SOP_W_LCM_BOH_QTY_COLUMN = 'SOP W_LCM BOH Qty'
        SOP_W_LCM_MFG_QTY_COLUMN = 'SOP W_LCM MFG Qty'
        SOP_W_LCM_MFG_CHG_QTY_COLUMN = 'SOP W_LCM MFG Chg Qty'
        SOP_W_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'
        SOP_W_SET_SOP_QTY_COLUMN = 'SOP W_SET SOP Qty'
        SOP_W_SET_BOH_QTY_COLUMN = 'SOP W_SET BOH Qty'
        SOP_W_SET_ADJ_QTY_COLUMN = 'SOP W_SOP Adj Qty'
        SOP_W_LCM_SOP_ADJ_QTY_COLUMN = 'SOP W_LCM SOP Adj Qty'

        FROM_ITEM_COLUMN = 'from.[Item].[Item]'
        FROM_ACTIVITY1_COLUMN = 'from.[Activity1].[Activity1]'
        FROM_ACTIVITY2_COLUMN = 'from.[Activity2].[Activity2]'
        FROM_ACTIVITY3_COLUMN = 'from.[Activity3].[Activity3]'
        FROM_ORDERLINE_ID_COLUMN = 'from.[Documents].[OrderlineID]'
        FROM_TIME_WEEK_COLUMN = 'from.[Time].[Week]'
        FROM_LOCATION_COLUMN = 'from.[Location].[Location]'

        SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN = 'SOP Adjust SET Remain Mtrl_Init Remain Supply Qty'  # 최초수량
        SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN = 'SOP Adjust SET Remain Mtrl_Adj Used Qty'  # 수정수량
        SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN = 'SOP Adjust SET Remain Mtrl_Cur Remain Qty'  # 잔여수량

        SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN = 'SOP Adjust LCM W_SOP Adj Qty'
        SOP_ADJUST_LCM_W_SOP_QTY_COLUMN = 'SOP Adjust LCM W_SOP Qty'
        SOP_ADJUST_LCM_W_CHG_QTY_COLUMN = 'SOP Adjust LCM W_Chg Qty'
        SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN = 'SOP Adjust LCM W_Before Adj Qty'

        SOP_ADJUST_SET_W_LOCK_FLAG_COLUMN = 'SOP Adjust SET W_Lock Flag'
        SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN = 'SOP Adjust SET W_SOP Adj Qty'
        SOP_ADJUST_SET_W_SOP_ADJ_SHORT_QTY_COLUMN = 'SOP Adjust SET W_SOP Adj Short Qty'
        SOP_ADJUST_SET_W_SHT_QTY_COLUMN = 'SOP Adjust SET W_Sht Qty'
        SOP_ADJUST_SET_W_SOP_QTY_COLUMN = 'SOP Adjust SET W_SOP Qty'
        SOP_ADJUST_SET_W_CHG_QTY_COLUMN = 'SOP Adjust SET W_Chg Qty'
        SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN = 'SOP Adjust SET W_Before Adj Qty'

        RANK_COLUMN = 'rank'

        df_BOMVersionPrtyW_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            ITEM_COMPONENT_COLUMN, BOM_VERSION_PRTY_W_PRTY_COLUMN
        ]

        adjust_setw_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_COMPONENT_COLUMN,
            WEEK2_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, SEQUENCE_COLUMN,
            SOP_W_LCM_BOH_QTY_COLUMN, SOP_W_LCM_MFG_ADJ_QTY_COLUMN, SOP_W_LCM_MFG_CHG_QTY_COLUMN, SOP_W_LCM_MFG_QTY_COLUMN, SOP_W_LCM_SOP_ADJ_QTY_COLUMN,
            SOP_W_LCM_SOP_QTY_COLUMN, SOP_W_SET_BOH_QTY_COLUMN, SOP_W_SET_MFG_ADJ_QTY_COLUMN, SOP_W_SET_MFG_CHG_QTY_COLUMN, SOP_W_SET_MFG_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN,
            SOP_W_SOP_ID_COLUMN,
            SOP_ADJUST_SET_W_CHG_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN,
            SOP_ADJUST_SET_W_SOP_QTY_COLUMN,
            BOM_VERSION_PRTY_W_PRTY_COLUMN
        ]

        sopw_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_COMPONENT_COLUMN,
            WEEK2_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, SEQUENCE_COLUMN,
            SOP_W_LCM_BOH_QTY_COLUMN, SOP_W_LCM_MFG_ADJ_QTY_COLUMN, SOP_W_LCM_MFG_CHG_QTY_COLUMN, SOP_W_LCM_MFG_QTY_COLUMN, SOP_W_LCM_SOP_ADJ_QTY_COLUMN, SOP_W_LCM_SOP_QTY_COLUMN,
            SOP_W_SET_MFG_ADJ_QTY_COLUMN, SOP_W_SET_MFG_CHG_QTY_COLUMN, SOP_W_SET_MFG_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN,
            SOP_W_SOP_ID_COLUMN, SOP_ADJUST_SET_W_CHG_QTY_COLUMN
        ]

        df_SOPAdjustSETRemainMtrl_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN,
            SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN
        ]


        df_SOPAdjustmentSETW_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN,
            SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN
        ]

        df_SOPAdjustLCMW_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN
        ]

        df_SOPAdjustLCMWAdj_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN
        ]

        df_SOPRemainSETMtrlReg_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN,
            SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 1.1 현재 week 가져오기 및 'Sequence.[Sequence]' 컬럼의 최대값 구하기
        mp_plan_start_week = str(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')

        max_sequence_value = str(get_first_value(df_in_SOP_W_Max, SEQUENCE_COLUMN))
        step(f'=====> max_sequence_value : {max_sequence_value}')



        # 1.2 컬럼타입 변경
        str_columns = [
            VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN,
            SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TO_TRANS_MODE_COLUMN,
        ]
        df_in_SOPLCMW[str_columns] = df_in_SOPLCMW[str_columns].fillna('-').astype(str)

        str_columns = [TO_LOCATION_TO_LOCATION_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN]
        df_in_SOPW[str_columns] = df_in_SOPW[str_columns].astype(str)
        df_in_SOPAdjustmentSETWInc[str_columns] = df_in_SOPAdjustmentSETWInc[str_columns].astype(str)
        df_in_SOPAdjustmentSETWDec[str_columns] = df_in_SOPAdjustmentSETWDec[str_columns].astype(str)
        df_in_SOPAdjustmentSETWReg[str_columns] = df_in_SOPAdjustmentSETWReg[str_columns].astype(str)


        week_columns = [TIME_WEEK_COLUMN]
        df_in_SOPAdjustSETRemainMtrl[week_columns] = df_in_SOPAdjustSETRemainMtrl[week_columns].astype(str)
        df_in_BOMVersionPrtyW[week_columns] = df_in_BOMVersionPrtyW[week_columns].astype(str)
        df_in_SOPW[week_columns] = df_in_SOPW[week_columns].astype(str)
        df_in_SOPAdjustmentSETWInc[week_columns] = df_in_SOPAdjustmentSETWInc[week_columns].astype(str)
        df_in_SOPAdjustmentSETWDec[week_columns] = df_in_SOPAdjustmentSETWDec[week_columns].astype(str)
        df_in_SOPAdjustmentSETWReg[week_columns] = df_in_SOPAdjustmentSETWReg[week_columns].astype(str)


        week_columns = [WEEK1_COLUMN, WEEK2_COLUMN]
        df_in_SOPW[week_columns] = df_in_SOPW[week_columns].astype(str)


        # 1.3 가용자재 필요컬럼 발췌 및 Rank 설정
        df_in_SOPAdjustSETRemainMtrl = df_in_SOPAdjustSETRemainMtrl[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN,
            SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN
        ]].drop_duplicates()

        df_in_SOPAdjustSETRemainMtrl[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN] = pd.to_numeric(
            df_in_SOPAdjustSETRemainMtrl[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN], errors='coerce').fillna(0).astype('int64')

        group_by_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN]
        df_in_SOPAdjustSETRemainMtrl[RANK_COLUMN] = df_in_SOPAdjustSETRemainMtrl.groupby(
            group_by_columns, sort=False, as_index=False)[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN].rank(method='dense', ascending=False)

        int_columns = [
            SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN,
            SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN, RANK_COLUMN
        ]
        df_in_SOPAdjustSETRemainMtrl[int_columns] = df_in_SOPAdjustSETRemainMtrl[int_columns].fillna(0).astype('int64')

        print_df(df_in_SOPAdjustSETRemainMtrl, 'STEP3 by 1.3 ____ df_in_SOPAdjustSETRemainMtrl .... rank')




        # 1.4 Full BOM > group_by_columns 로 그룹화하여 'Full BOM_Prty' 의 최대값 및 최소값을 구함
        if not df_in_BOMVersionPrtyW.empty:
            #   1.4.1 BOM Version Prty W_Prty modify
            #       1.4.1.1 'BOM Version Prty W_Prty'의 값이 'X'로 시작하지 않는 데이터만 남기기
            df_in_BOMVersionPrtyW[BOM_VERSION_PRTY_W_PRTY_COLUMN] = df_in_BOMVersionPrtyW[BOM_VERSION_PRTY_W_PRTY_COLUMN].astype(str)
            df_in_BOMVersionPrtyW = df_in_BOMVersionPrtyW[~df_in_BOMVersionPrtyW[BOM_VERSION_PRTY_W_PRTY_COLUMN].str.lower().str.startswith('x')]
            print_df(df_in_BOMVersionPrtyW, 'STEP3 by 1.4.1 ____ df_in_BOMVersionPrtyW .... Prty = x 제외')



            #   1.4.2 'BOM Version Prty W_Prty' 우선순의 filter
            group_by_columns = [VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN]

            #       1.4.2.1 우선순의 높은 것
            df_BOMVersionPrtyWMax = df_in_BOMVersionPrtyW.groupby(group_by_columns, sort=False, as_index=False)[BOM_VERSION_PRTY_W_PRTY_COLUMN].min()
            print_df(df_BOMVersionPrtyWMax, 'STEP3 by 1.4.2.1 ____ df_BOMVersionPrtyWMax .... Prty = 1 (우선순의 높은 것)')

            df_BOMVersionPrtyWMax = df_BOMVersionPrtyWMax.merge(df_in_BOMVersionPrtyW, how='inner',
                                                                on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, BOM_VERSION_PRTY_W_PRTY_COLUMN])
            print_df(df_BOMVersionPrtyWMax, 'STEP3 by 1.4.2.1 ____ df_BOMVersionPrtyWMax .... Prty = 1 (우선순의 높은 것) full')

            #       1.4.2.2 선순의 낮은 것
            df_BOMVersionPrtyWMin = df_in_BOMVersionPrtyW.groupby(group_by_columns, sort=False, as_index=False)[BOM_VERSION_PRTY_W_PRTY_COLUMN].max()
            print_df(df_BOMVersionPrtyWMin, 'STEP3 by 1.4.2.2 ____ df_BOMVersionPrtyWMin .... Prty = 999 (우선순의 낮은 것)')

            df_BOMVersionPrtyWMin = df_BOMVersionPrtyWMin.merge(df_in_BOMVersionPrtyW, how='inner',
                                                                on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, BOM_VERSION_PRTY_W_PRTY_COLUMN])
            print_df(df_BOMVersionPrtyWMin, 'STEP3 by 1.4.2.2 ____ df_BOMVersionPrtyWMin .... Prty = 999 (우선순의 낮은 것) full')



            #   1.4.3 증량/감량/Add
            #       1.4.3.1 증량 dataset create / Full BOM merge ('BOM_Prty' 높은순위 우선)
            df_SOPAdjustSETWInc = pd.merge(df_in_SOPAdjustmentSETWInc, df_BOMVersionPrtyWMax, how='inner',
                                           on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN]).drop_duplicates()

            str_columns = [ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
            df_SOPAdjustSETWInc[str_columns] = df_SOPAdjustSETWInc[str_columns].fillna('-').astype(str)
            print_df(df_SOPAdjustSETWInc, 'STEP3 by 1.4.3.1 ____ df_SOPAdjustSETWInc .... BOMVersion merge (Prty = 1 (우선순의 높은 것))')


            #       0.4.3.2 감량 dataset create / Full BOM merge ('BOM_Prty' 낮은순위 우선)
            df_SOPAdjustSETWDec = pd.merge(df_in_SOPAdjustmentSETWDec, df_BOMVersionPrtyWMin, how='inner',
                                           on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN]).drop_duplicates()

            str_columns = [ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
            df_SOPAdjustSETWDec[str_columns] = df_SOPAdjustSETWDec[str_columns].fillna('-').astype(str)
            print_df(df_SOPAdjustSETWDec, 'STEP3 by 1.4.3.2 ____ df_SOPAdjustSETWDec .... BOMVersion merge (Prty = 999 (우선순의 낮은 것))')


            #       0.4.3.3 Add dataset create / Full BOM merge ('BOM_Prty' 높은순위 우선)
            df_SOPAdjustSETWReg = pd.merge(df_in_SOPAdjustmentSETWReg, df_BOMVersionPrtyWMax, how='inner',
                                           on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN]).drop_duplicates()

            str_columns = [ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
            df_SOPAdjustSETWReg[str_columns] = df_SOPAdjustSETWReg[str_columns].fillna('-').astype(str)
            print_df(df_SOPAdjustSETWReg, 'STEP3 by 1.4.3.3 ____ df_SOPAdjustSETWReg .... BOMVersion merge (Prty = 1 (우선순의 높은 것))')

        else:
            df_in_BOMVersionPrtyW = pd.DataFrame(columns=df_BOMVersionPrtyW_columns)


        step('=====> STEP3 End')





        # ################################################################################################################
        # # STEP 4 : output data machining
        # ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        step('=====> STEP4 by 1 Start : 감량 처리')
        if not df_in_SOPAdjustmentSETWDec.empty:
            # 1.1 가용재고(Remain Mtrl) merge
            df_buf_SOPAdjustSETWDec = pd.merge(df_SOPAdjustSETWDec, df_in_SOPAdjustSETRemainMtrl, how='inner',
                                               on=[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN])
            print_df(df_buf_SOPAdjustSETWDec, 'STEP4 by 1.1.1 ____ df_buf_SOPAdjustSETWDec .... RemainMtrl merge 1')

            if not df_buf_SOPAdjustSETWDec.empty:
                #   1.1.1 감량 + 가용재고 merge
                set_sort_by_columns = [
                    ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_METERIAL_COLUMN, RANK_COLUMN,
                ]
                df_buf_SOPAdjustSETWDec = df_buf_SOPAdjustSETWDec.sort_values(by=set_sort_by_columns, ascending=[True, True, True, True, True, True])
                print_df(df_buf_SOPAdjustSETWDec, 'STEP4 by 1.1.1 ____ df_buf_SOPAdjustSETWDec .... RemainMtrl merge 2')

                #   1.1.2 감량건수만큼 각 행에 대해 반복
                df_result = pd.DataFrame()  # 결과를 저장할 DataFrame
                # df_dec_remain_result = pd.DataFrame()  # 감량 수량이 over 할때, 결과를 저장할 DataFrame
                for _, row in df_in_SOPAdjustmentSETWDec.iterrows():
                    remaining_q = abs(row[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])  # df_in_SOPAdjustmentSETWDec['SOP Adjust SET W_Chg Qty'] 값 가져오기

                    # df_buf_SOPAdjustSETWDec 에서 조건에 맞는 값 필터링
                    filtered = df_buf_SOPAdjustSETWDec[
                        (df_buf_SOPAdjustSETWDec[ITEM_COLUMN] == row[ITEM_COLUMN]) &
                        (df_buf_SOPAdjustSETWDec[LOCATION_COLUMN] == row[LOCATION_COLUMN]) &
                        (df_buf_SOPAdjustSETWDec[TIME_WEEK_COLUMN] == row[TIME_WEEK_COLUMN])
                    ]

                    if not filtered.empty:
                        last_idx = filtered.index[-1]  # filtered 데이터프레임의 마지막
                        for idx, f_row in filtered.iterrows():
                            deducted_q = min(# 남은 SOP Adjust SET W_Chg Qty 와 df_buf_SOPAdjustSETWDec 의 SOP Adjust SET Remain Mtrl_Cur Remain Qty 중 작은 값
                                remaining_q,
                                f_row[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] if pd.notna(f_row[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN]) else 0
                            )
                            remaining_q -= deducted_q  # remaining_q에서 차감
                            new_row = f_row.copy()  # 기존 행 복사
                            new_row['REMAIN_QTY'] = deducted_q  # 새로운 'REMAIN_QTY' 열에 차감된 값 저장
                            df_result = pd.concat([df_result, new_row.to_frame().T], ignore_index=True)  # df_result 에 추가
                            # df_dec_remain_result = df_result.copy()

                            if idx == last_idx and remaining_q > 0:  # 마지막 루프 여부 확인 + remaining_q > 0인 경우
                                # 새로운 row를 생성 (기존 row 정보 + remaining_q)
                                # leftover_row = f_row.copy()
                                # leftover_row[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] = 0
                                # leftover_row['REMAIN_QTY'] = remaining_q  # 남은 remaining_q 값 추가
                                # df_dec_remain_result = pd.concat([df_result, leftover_row.to_frame().T], ignore_index=True)
                                remaining_q = 0  # 모든 값을 처리했으니 remaining_q 초기화

                            if remaining_q <= 0:  # 남은 값이 0이면 중단
                                break


                df_result['ORIGIN_VALUE'] = df_result[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN].astype('float64')
                print_df(df_result, 'STEP4 by 1.1.2 ____ df_result .... dec qty modify')

            else:
                df_result = df_SOPAdjustSETWDec.copy()
                print_df(df_result, 'STEP4 by 1.1.2 ____ df_result .... df copy')

                df_result[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN] = 0
                df_result['REMAIN_QTY'] = df_result[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                df_result['ORIGIN_VALUE'] = 0
                print_df(df_result, 'STEP4 by 1.1.2 ____ df_result .... df rebuild')

                df_buf_SOPAdjustSETWDec = df_SOPAdjustSETWDec.copy()
                print_df(df_buf_SOPAdjustSETWDec, 'STEP4 by 1.1.2 ____ df_buf_SOPAdjustSETWDec .... df rebuild')



            # 1.2 Remain Mtrl 감량 설정
            df_SOPAdjustSETRemainMtrlDec = df_result.copy()
            df_SOPAdjustSETRemainMtrlDec[SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN] = -df_SOPAdjustSETRemainMtrlDec['REMAIN_QTY']
            df_SOPAdjustSETRemainMtrlDec[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] = (
                    abs(df_SOPAdjustSETRemainMtrlDec[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN].fillna(0)) +
                    abs(df_SOPAdjustSETRemainMtrlDec[SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN].fillna(0))
            )
            df_SOPAdjustSETRemainMtrlDec = df_SOPAdjustSETRemainMtrlDec[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN,
                SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN,
                SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN
            ]]
            print_df(df_SOPAdjustSETRemainMtrlDec, 'STEP4 by 1.2 ____ df_SOPAdjustSETRemainMtrlDec .... final')



            # 1.3 df_SOPAdjustSETWDec create
            #   1.3.1 SOPW merge
            df_SOPAdjustSETWDec = pd.merge(df_buf_SOPAdjustSETWDec, df_in_SOPW, how='inner',
                                           on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN,
                                               TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, BOM_INFO_BOM_VERSION_COLUMN])
            print_df(df_SOPAdjustSETWDec, 'STEP4 by 1.3.1 ____ df_SOPAdjustSETWDec .... SOPW merge')

            df_SOPAdjustSETWDec.rename(columns={
                BOM_INFO_BOM_VERSION_COLUMN+'_y': BOM_INFO_BOM_VERSION_COLUMN,
                ITEM_METERIAL_COLUMN+'_y': ITEM_METERIAL_COLUMN,
                ITEM_COMPONENT_COLUMN+'_y': ITEM_COMPONENT_COLUMN,
            }, inplace=True)

            #   1.3.2 컬럼설정
            int_columns = [
                SOP_ADJUST_SET_W_CHG_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN,
                SOP_W_LCM_MFG_ADJ_QTY_COLUMN, SOP_W_LCM_MFG_CHG_QTY_COLUMN, SOP_W_SET_MFG_CHG_QTY_COLUMN
            ]
            df_SOPAdjustSETWDec[int_columns] = df_SOPAdjustSETWDec[int_columns].fillna(0).astype('Int64')


            str_columns = [SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN]
            df_SOPAdjustSETWDec[str_columns] = df_SOPAdjustSETWDec[str_columns].fillna('-').astype(str)


            week_columns = [WEEK1_COLUMN]
            df_SOPAdjustSETWDec[week_columns] = df_SOPAdjustSETWDec[week_columns].fillna(mp_plan_start_week).astype(str)


            df_SOPAdjustSETWDec = df_SOPAdjustSETWDec[adjust_setw_columns]
            df_SOPAdjustSETWDec = df_SOPAdjustSETWDec.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None, '0': None})

            # for idx, group in df_in_SOPAdjustmentSETWDec.groupby([ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, LOCATION_COLUMN, TRANS_MODE_COLUMN]):
            #     # 조건에 맞는 df2 행 찾기
            #     matching_indices = df_SOPAdjustSETWDec[(df_SOPAdjustSETWDec[ITEM_COLUMN] == idx[1]) &
            #                                            (df_SOPAdjustSETWDec[TIME_WEEK_COLUMN] == idx[2]) &
            #                                            (df_SOPAdjustSETWDec[TO_LOCATION_TO_LOCATION_COLUMN] == idx[3]) &
            #                                            (df_SOPAdjustSETWDec[LOCATION_COLUMN] == idx[4]) &
            #                                            (df_SOPAdjustSETWDec[TRANS_MODE_COLUMN] == idx[5])].index
            #
            #     # 첫 번째 결과를 유지한 후 나머지 q2를 0으로 설정
            #     if len(matching_indices) > 1:
            #         df_SOPAdjustSETWDec.loc[matching_indices[1:], SOP_ADJUST_SET_W_CHG_QTY_COLUMN] = 0


            # for loop를 사용하여 SEQUENCE_COLUMN 설정
            # max_sequence_value = int(max_sequence_value) + 1
            # sequences = []
            # for i in range(len(df_SOPAdjustSETWDec)):
            #     sequences.append(max_sequence_value)
            #     max_sequence_value += 1

            # df_SOPWReg의 SEQUENCE_COLUMN에 값 설정
            # df_SOPAdjustSETWDec[SEQUENCE_COLUMN] = sequences

            df_SOPAdjustSETWDec[WEEK1_COLUMN] = df_SOPAdjustSETWDec[WEEK1_COLUMN].astype(str)

            print_df(df_SOPAdjustSETWDec, 'STEP4 by 1.3.2 ____ df_SOPAdjustSETWDec .... columns setting')




            # 1.4 SOP W 감량 설정 초기화
            df_SOPWQtyCleanDec = df_SOPAdjustSETWDec.copy()

            df_SOPWQtyCleanDec[SOP_W_SET_MFG_ADJ_QTY_COLUMN] = 0  # 수량 초기화
            df_SOPWQtyCleanDec[SOP_W_SET_MFG_CHG_QTY_COLUMN] = 0  # 수량 초기화
            df_SOPWQtyCleanDec[SOP_W_SET_SOP_QTY_COLUMN] = 0

            df_SOPWQtyCleanDec = df_SOPWQtyCleanDec[sopw_columns]

            #   디맨전 컬럼 null 시  '-' 처리
            refill_columns = [
                SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, TO_ITEM_TO_ITEM_COLUMN,
                TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            ]
            df_SOPWQtyCleanDec[refill_columns] = df_SOPWQtyCleanDec[refill_columns].fillna('Dummy').astype('str')


            #   Week null 시 현재 주차 설정
            week_columns = [WEEK1_COLUMN, WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN]
            df_SOPWQtyCleanDec[week_columns] = df_SOPWQtyCleanDec[week_columns].fillna(mp_plan_start_week).astype('str')
            print_df(df_SOPWQtyCleanDec, 'STEP4 by 1.4 ____ df_SOPWQtyCleanDec .... final')



            # 1.5 SOP W 감량 설정
            df_SOPWDec = df_SOPAdjustSETWDec.copy()
            # 원수량    : SOP Adjust SET W_SOP Qty
            # 변경후수량 : SOP Adjust SET W_SOP Adj Qty

            df_SOPWDec[SOP_W_SET_MFG_ADJ_QTY_COLUMN] = df_SOPWDec[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWDec[SOP_W_LCM_SOP_ADJ_QTY_COLUMN] = df_SOPWDec[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWDec[SOP_W_SET_SOP_QTY_COLUMN] = df_SOPWDec[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]      # 변경후
            df_SOPWDec[SOP_W_SET_MFG_CHG_QTY_COLUMN] = df_SOPWDec[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            df_SOPWDec[SOP_W_LCM_MFG_CHG_QTY_COLUMN] = df_SOPWDec[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            # df_SOPWDec[SOP_W_LCM_MFG_ADJ_QTY_COLUMN] = df_SOPWDec[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]

            df_SOPWDec = df_SOPWDec[sopw_columns].drop_duplicates()

            #   디맨전 컬럼 null 시  '-' 처리
            refill_columns = [
                SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, TO_ITEM_TO_ITEM_COLUMN,
                TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            ]
            df_SOPWDec[refill_columns] = df_SOPWDec[refill_columns].fillna('Dummy').astype('str')

            #   Week null 시 현재 주차 설정
            week_columns = [WEEK1_COLUMN, WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN]
            df_SOPWDec[week_columns] = df_SOPWDec[week_columns].fillna(mp_plan_start_week)

            for _, row in df_in_SOPAdjustmentSETWDec.iterrows():
                remaining_q = abs(row[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])  # df_in_SOPAdjustmentSETWDec['SOP Adjust SET W_Chg Qty'] 값 가져오기

                # df_buf_SOPAdjustSETWDec 에서 조건에 맞는 값 필터링
                filtered = df_SOPWDec[
                    (df_SOPWDec[ITEM_COLUMN] == row[ITEM_COLUMN]) &
                    (df_SOPWDec[TIME_WEEK_COLUMN] == row[TIME_WEEK_COLUMN]) &
                    (df_SOPWDec[TO_LOCATION_TO_LOCATION_COLUMN] == row[TO_LOCATION_TO_LOCATION_COLUMN]) &
                    (df_SOPWDec[LOCATION_COLUMN] == row[LOCATION_COLUMN]) &
                    (df_SOPWDec[TRANS_MODE_COLUMN] == row[TRANS_MODE_COLUMN])
                ]

                if filtered.empty:
                    last_idx = 0  # 기본값 처리
                else:
                    last_idx = filtered.index[-1]  # filtered 데이터프레임의 마지막
                    for idx, f_row in filtered.iterrows():
                        deducted_q = min(remaining_q, f_row[SOP_W_SET_MFG_ADJ_QTY_COLUMN])  # 남은 q와 df_SOPWDec 의 q 중 작은 값
                        # note(f' remaining_q : SOP W_SET MFG Adj Qty : deducted_q .... {remaining_q} : {f_row[SOP_W_SET_MFG_ADJ_QTY_COLUMN]} : {deducted_q} ')
                        remaining_q -= deducted_q  # remaining_q에서 차감

                        # df_SOPWDec.loc[idx, SOP_ADJUST_SET_W_CHG_QTY_COLUMN] = -deducted_q  # 원본2에 값을 업데이트
                        # df_SOPWDec.loc[idx, SOP_W_SET_MFG_CHG_QTY_COLUMN] = -deducted_q

                        if idx == last_idx and remaining_q > 0:  # 마지막 루프 여부 확인 + remaining_q > 0인 경우
                            break

            print_df(df_SOPWDec, 'STEP4 by 1.5 ____ df_SOPWDec .... final')



            # 1.6 SET W 감량 설정
            # df_SOPAdjustmentSETWDec = df_in_SOPAdjustmentSETWDec.copy()
            df_SOPAdjustmentSETWDec = df_SOPAdjustSETWDec.copy()
            df_SOPAdjustmentSETWDec[SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN] = df_SOPAdjustmentSETWDec[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPAdjustmentSETWDec = df_SOPAdjustmentSETWDec[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN,
                SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN
            ]]
            print_df(df_SOPAdjustmentSETWDec, 'STEP4 by 1.6 ____ df_SOPAdjustmentSETWDec .... final')



            # 1.7 LCM W 감량 설정
            #   1.7.1 LCM W
            df_SOPAdjustLCMWDec = df_SOPAdjustSETWDec.copy()
            df_SOPAdjustLCMWDec = pd.merge(df_SOPAdjustLCMWDec, df_in_SOPLCMW, how='inner',
                                           on=[VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, WEEK1_COLUMN,
                                               ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TO_TRANS_MODE_COLUMN])
            print_df(df_SOPAdjustLCMWDec, 'STEP4 by 1.7.1 ____ df_SOPAdjustLCMWDec .... merge')


            if not df_SOPAdjustLCMWDec.empty:
                df_SOPAdjustLCMWDec[SOP_ADJUST_LCM_W_CHG_QTY_COLUMN] = df_SOPAdjustLCMWDec[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                df_SOPAdjustLCMWDec[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN] = (
                        df_SOPAdjustLCMWDec[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN] - abs(df_SOPAdjustLCMWDec[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])
                )
                df_SOPAdjustLCMWDec[SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN] = df_SOPAdjustLCMWDec[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN]
                df_SOPAdjustLCMWDec[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN] = df_SOPAdjustLCMWDec[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                print_df(df_SOPAdjustLCMWDec, 'STEP4 by 1.7.1 ____ df_SOPAdjustLCMWDec .... merge 2')

                df_SOPAdjustLCMWAdjDec = df_SOPAdjustLCMWDec.copy() # df_SOPAdjustLCMWAdjDec 사전 copy

                df_SOPAdjustLCMWDec = df_SOPAdjustLCMWDec[[
                    VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN,
                    SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN
                ]]
                print_df(df_SOPAdjustLCMWDec, 'STEP4 by 1.7.1 ____ df_SOPAdjustLCMWDec .... final')

                #   1.7.2 LCM W > ADJ Qty
                df_SOPAdjustLCMWAdjDec = df_SOPAdjustLCMWAdjDec[[
                    VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
                    ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN
                ]]

                print_df(df_SOPAdjustLCMWAdjDec, 'STEP4 by 1.7.2 ____ df_SOPAdjustLCMWAdjDec .... final')

            else:
                df_SOPAdjustLCMWDec = pd.DataFrame(columns=df_SOPAdjustLCMW_columns)
                df_SOPAdjustLCMWAdjDec = pd.DataFrame(columns=df_SOPAdjustLCMWAdj_columns)

        else:
            df_SOPWQtyCleanDec = pd.DataFrame(columns=sopw_columns)
            df_SOPWDec = pd.DataFrame(columns=sopw_columns)
            df_SOPAdjustSETRemainMtrlDec = pd.DataFrame(columns=df_SOPAdjustSETRemainMtrl_columns)
            df_SOPAdjustmentSETWDec = pd.DataFrame(columns=df_SOPAdjustmentSETW_columns)
            df_SOPAdjustLCMWDec = pd.DataFrame(columns=df_SOPAdjustLCMW_columns)
            df_SOPAdjustLCMWAdjDec = pd.DataFrame(columns=df_SOPAdjustLCMWAdj_columns)

        step('=====> STEP4 by 1 End')




        step('=====> STEP4 by 2 Start : 증량 처리')
        if not df_in_SOPAdjustmentSETWInc.empty:
            # 2.1 가용재고(Remain Mtrl) merge
            df_buf_SOPAdjustSETWInc = pd.merge(df_SOPAdjustSETWInc, df_in_SOPAdjustSETRemainMtrl, how='inner',
                                               on=[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN])
            print_df(df_buf_SOPAdjustSETWInc, 'STEP4 by 2.1.1 ____ df_buf_SOPAdjustSETWInc .... RemainMtrl merge 1')

            if not df_buf_SOPAdjustSETWInc.empty:
                #   2.1.1 증량 + 가용재고 merge
                set_sort_by_columns = [
                    ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, ITEM_METERIAL_COLUMN, RANK_COLUMN,
                ]
                df_buf_SOPAdjustSETWInc = df_buf_SOPAdjustSETWInc.sort_values(by=set_sort_by_columns, ascending=[True, True, True, True, True, True])
                print_df(df_buf_SOPAdjustSETWInc, 'STEP4 by 2.1.1 ____ df_buf_SOPAdjustSETWInc .... RemainMtrl merge 2')



                #   2.1.2 증량건수만큼 각 행에 대해 반복
                df_result = pd.DataFrame()  # 결과를 저장할 DataFrame
                for _, row in df_in_SOPAdjustmentSETWInc.iterrows():
                    remaining_q = 0  # df_in_SOPAdjustmentSETWInc['SOP Adjust SET W_Chg Qty'] 를 누적시킬 변수 (더해 나감)
                    target_q = abs(row[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])  # 목표 'SOP Adjust SET W_Chg Qty' 값

                    # df_buf_SOPAdjustSETWInc 에서 조건에 맞는 값 필터링
                    filtered = df_buf_SOPAdjustSETWInc[
                        (df_buf_SOPAdjustSETWInc[ITEM_COLUMN] == row[ITEM_COLUMN]) &
                        (df_buf_SOPAdjustSETWInc[LOCATION_COLUMN] == row[LOCATION_COLUMN]) &
                        (df_buf_SOPAdjustSETWInc[TIME_WEEK_COLUMN] == row[TIME_WEEK_COLUMN])
                    ]

                    if not filtered.empty:
                        last_idx = filtered.index[-1]  # filtered 데이터프레임의 마지막 index
                        for idx, f_row in filtered.iterrows():
                            if idx == last_idx:  # 마지막 index일 경우
                                added_q = target_q - remaining_q  # 마지막 남은 수량을 전부 적용
                                remaining_q = target_q  # 목표를 충족했다고 가정
                            else:
                                added_q = min(target_q - remaining_q, f_row[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])  # 누적되지 않은 수량 계산
                                remaining_q += added_q  # `remaining_q`에 추가

                            new_row = f_row.copy()  # 기존 행 복사
                            new_row['REMAIN_QTY'] = added_q  # 새로운 'REMAIN_QTY' 열에 추가한 수량 저장
                            df_result = pd.concat([df_result, new_row.to_frame().T], ignore_index=True)  # df_result 에 추가

                            if remaining_q >= target_q:  # 목표 'SOP Adjust SET W_Chg Qty' 값에 도달하면 중단
                                break


                df_result['ORIGIN_VALUE'] = df_result[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN].astype('float64')
                print_df(df_result, 'STEP4 by 2.1.2 ____ df_result .... inc qty modify')

            else:
                df_result = df_SOPAdjustSETWInc.copy()
                print_df(df_result, 'STEP4 by 2.1.2 ____ df_result .... df copy')

                df_result[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN] = 0
                df_result['REMAIN_QTY'] = df_result[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                df_result['ORIGIN_VALUE'] = 0
                print_df(df_result, 'STEP4 by 2.1.2 ____ df_result .... df rebuild')

                df_buf_SOPAdjustSETWInc = df_SOPAdjustSETWInc.copy()
                print_df(df_buf_SOPAdjustSETWInc, 'STEP4 by 2.1.2 ____ df_buf_SOPAdjustSETWInc .... df rebuild')



            # 2.2 Remain Mtrl 증량 설정
            df_SOPAdjustSETRemainMtrlInc = df_result.copy()
            #   기본 계산
            df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN] = df_SOPAdjustSETRemainMtrlInc['REMAIN_QTY']
            df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] = (
                    (df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN]) -
                    (df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN])
            )

            #   조건에 따라 음수로 처리
            df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] = np.where(
                (df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] > 0) & (df_SOPAdjustSETRemainMtrlInc['ORIGIN_VALUE'] < 0),  # 원래 값이 음수이고 결과가 0보다 큰 경우
                -df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN],  # 음수로 변환
                df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN]  # 그대로 유지
            )

            df_SOPAdjustSETRemainMtrlInc = df_SOPAdjustSETRemainMtrlInc[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN,
                SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN
            ]]
            print_df(df_SOPAdjustSETRemainMtrlInc, 'STEP4 by 2.2 ____ df_SOPAdjustSETRemainMtrlInc .... final')




            # 2.3 df_SOPAdjustSETWInc create
            #   2.3.1 SOPW merge
            df_SOPAdjustSETWInc = pd.merge(df_buf_SOPAdjustSETWInc, df_in_SOPW, how='inner',
                                           on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,
                                               TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN])

            df_SOPAdjustSETWInc.rename(columns={ITEM_COMPONENT_COLUMN+'_x': ITEM_COMPONENT_COLUMN}, inplace=True)
            print_df(df_SOPAdjustSETWInc, 'STEP4 by 2.3.1 ____ df_SOPAdjustSETWInc .... SOPW merge')


            #   2.3.2 컬럼설정
            int_columns = [
                SOP_ADJUST_SET_W_CHG_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN,
                SOP_W_LCM_MFG_ADJ_QTY_COLUMN, SOP_W_LCM_MFG_CHG_QTY_COLUMN, SOP_W_SET_MFG_CHG_QTY_COLUMN
            ]
            df_SOPAdjustSETWInc[int_columns] = df_SOPAdjustSETWInc[int_columns].fillna(0).astype('Int64')


            str_columns = [SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN]
            df_SOPAdjustSETWInc[str_columns] = df_SOPAdjustSETWInc[str_columns].fillna('-').astype(str)

            week_columns = [WEEK1_COLUMN]
            df_SOPAdjustSETWInc[week_columns] = df_SOPAdjustSETWInc[week_columns].fillna(mp_plan_start_week).astype(str)


            df_SOPAdjustSETWInc = df_SOPAdjustSETWInc[adjust_setw_columns]
            df_SOPAdjustSETWInc = df_SOPAdjustSETWInc.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None, '0': None})

            # for loop를 사용하여 SEQUENCE_COLUMN 설정
            # max_sequence_value = int(max_sequence_value) + 1
            # sequences = []
            # for i in range(len(df_SOPAdjustSETWDec)):
            #     sequences.append(max_sequence_value)
            #     max_sequence_value += 1

            # df_SOPWReg의 SEQUENCE_COLUMN에 값 설정
            # df_SOPAdjustSETWInc[SEQUENCE_COLUMN] = sequences

            df_SOPAdjustSETWInc[WEEK1_COLUMN] = df_SOPAdjustSETWInc[WEEK1_COLUMN].astype(str)

            print_df(df_SOPAdjustSETWInc, 'STEP4 by 2.3.2 ____ df_SOPAdjustSETWInc .... columns setting')




            # 2.4 SOP W 증량 설정 초기화
            df_SOPWQtyCleanInc = df_SOPAdjustSETWInc.copy()

            df_SOPWQtyCleanDec[SOP_W_SET_MFG_ADJ_QTY_COLUMN] = 0  # 수량 초기화
            df_SOPWQtyCleanDec[SOP_W_SET_MFG_CHG_QTY_COLUMN] = 0  # 수량 초기화
            df_SOPWQtyCleanDec[SOP_W_SET_SOP_QTY_COLUMN] = 0

            df_SOPWQtyCleanInc = df_SOPWQtyCleanInc[sopw_columns]


            #   디맨전 컬럼 null 시  '-' 처리
            refill_columns = [
                SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, TO_ITEM_TO_ITEM_COLUMN,
                TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            ]
            df_SOPWQtyCleanInc[refill_columns] = df_SOPWQtyCleanInc[refill_columns].fillna('Dummy').astype('str')


            #   Week null 시 현재 주차 설정
            week_columns = [WEEK1_COLUMN, WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN]
            df_SOPWQtyCleanInc[week_columns] = df_SOPWQtyCleanInc[week_columns].fillna(mp_plan_start_week)
            print_df(df_SOPWQtyCleanInc, 'STEP4 by 2.4 ____ df_SOPWQtyCleanInc .... final')




            # 2.5 SOP W 증량 설정
            df_SOPWInc = df_SOPAdjustSETWInc.copy()

            # 원수량    : SOP Adjust SET W_SOP Qty
            # 변경후수량 : SOP Adjust SET W_SOP Adj Qty

            df_SOPWInc[SOP_W_SET_MFG_ADJ_QTY_COLUMN] = df_SOPWInc[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWInc[SOP_W_LCM_SOP_ADJ_QTY_COLUMN] = df_SOPWInc[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWInc[SOP_W_SET_SOP_QTY_COLUMN] = df_SOPWInc[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]      # 변경후
            df_SOPWInc[SOP_W_SET_MFG_CHG_QTY_COLUMN] = df_SOPWInc[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            df_SOPWInc[SOP_W_LCM_MFG_CHG_QTY_COLUMN] = df_SOPWInc[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            # df_SOPWInc[SOP_W_LCM_MFG_ADJ_QTY_COLUMN] = df_SOPWInc[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]

            df_SOPWInc = df_SOPWInc[sopw_columns].drop_duplicates()

            #   디맨전 컬럼 null 시  '-' 처리
            refill_columns = [
                SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, TO_ITEM_TO_ITEM_COLUMN,
                TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            ]
            df_SOPWInc[refill_columns] = df_SOPWInc[refill_columns].fillna('Dummy').astype('str')


            #   Week null 시 현재 주차 설정
            week_columns = [WEEK1_COLUMN, WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN]
            df_SOPWInc[week_columns] = df_SOPWInc[week_columns].fillna(mp_plan_start_week).astype('str')


            for _, row in df_in_SOPAdjustmentSETWInc.iterrows():
                remaining_q = abs(row[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])  # df_in_SOPAdjustmentSETWDec['SOP Adjust SET W_Chg Qty'] 값 가져오기

                # df_buf_SOPAdjustSETWDec 에서 조건에 맞는 값 필터링
                filtered = df_SOPWInc[
                    (df_SOPWInc[ITEM_COLUMN] == row[ITEM_COLUMN]) &
                    (df_SOPWInc[TIME_WEEK_COLUMN] == row[TIME_WEEK_COLUMN]) &
                    (df_SOPWInc[TO_LOCATION_TO_LOCATION_COLUMN] == row[TO_LOCATION_TO_LOCATION_COLUMN]) &
                    (df_SOPWInc[LOCATION_COLUMN] == row[LOCATION_COLUMN]) & (df_SOPWInc[TRANS_MODE_COLUMN] == row[TRANS_MODE_COLUMN])
                ]

                if filtered.empty:
                    last_idx = 0  # 기본값 처리
                else:
                    last_idx = filtered.index[-1]  # filtered 데이터프레임의 마지막
                    for idx, f_row in filtered.iterrows():
                        deducted_q = min(remaining_q, f_row[SOP_W_SET_MFG_ADJ_QTY_COLUMN])  # 남은 q와 df_SOPWInc 의 q 중 작은 값
                        remaining_q -= deducted_q  # remaining_q에서 차감

                        # df_SOPWInc.loc[idx, SOP_ADJUST_SET_W_CHG_QTY_COLUMN] = deducted_q  # 원본에 값을 업데이트
                        # df_SOPWInc.loc[idx, SOP_W_SET_MFG_CHG_QTY_COLUMN] = -deducted_q

                        if idx == last_idx and remaining_q > 0:  # 마지막 루프 여부 확인 + remaining_q > 0인 경우
                            break


            print_df(df_SOPWInc, 'STEP4 by 2.5 ____ df_SOPWInc .... final')




            # 2.6 SET W 증량 설정
            # df_SOPAdjustmentSETWInc = df_in_SOPAdjustmentSETWInc.copy()
            df_SOPAdjustmentSETWInc = df_SOPAdjustSETWInc.copy()
            df_SOPAdjustmentSETWInc[SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN] = df_SOPAdjustmentSETWInc[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPAdjustmentSETWInc = df_SOPAdjustmentSETWInc[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN,
                SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN
            ]]
            print_df(df_SOPAdjustmentSETWInc, 'STEP4 by 2.6 ____ df_SOPAdjustmentSETWInc .... final')




            # 2.7 LCM W 증량 설정
            #   2.7.1 LCM W
            df_SOPAdjustLCMWInc = df_SOPAdjustSETWInc.copy()
            df_in_SOPLCMW[WEEK1_COLUMN] = df_in_SOPLCMW[WEEK1_COLUMN].astype(str)
            df_SOPAdjustLCMWInc = pd.merge(df_SOPAdjustLCMWInc, df_in_SOPLCMW, how='inner',
                                           on=[VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, WEEK1_COLUMN,
                                               ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TO_TRANS_MODE_COLUMN,])
            print_df(df_SOPAdjustLCMWInc, 'STEP4 by 2.7.1 ____ df_SOPAdjustLCMWInc .... merge')

            if not df_SOPAdjustLCMWInc.empty:
                df_SOPAdjustLCMWInc[SOP_ADJUST_LCM_W_CHG_QTY_COLUMN] = df_SOPAdjustLCMWInc[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                df_SOPAdjustLCMWInc[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN] = (
                        df_SOPAdjustLCMWInc[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN] + abs(df_SOPAdjustLCMWInc[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])
                )
                df_SOPAdjustLCMWInc[SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN] = df_SOPAdjustLCMWInc[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN]
                df_SOPAdjustLCMWInc[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN] = df_SOPAdjustLCMWInc[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
                print_df(df_SOPAdjustLCMWInc, 'STEP4 by 2.7.1 ____ df_SOPAdjustLCMWInc .... merge 2')

                df_SOPAdjustLCMWAdjInc = df_SOPAdjustLCMWInc.copy() # df_SOPAdjustLCMWAdjInc 사전 copy

                df_SOPAdjustLCMWInc = df_SOPAdjustLCMWInc[[
                    VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN,
                    SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN
                ]]
                print_df(df_SOPAdjustLCMWInc, 'STEP4 by 2.7.1 ____ df_SOPAdjustLCMWInc .... final')

                #   2.7.2 LCM W > ADJ Qty
                df_SOPAdjustLCMWAdjInc = df_SOPAdjustLCMWAdjInc[[
                    VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
                    ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN
                ]]

                print_df(df_SOPAdjustLCMWAdjInc, 'STEP4 by 2.7.2 ____ df_SOPAdjustLCMWAdjInc .... final')

            else:
                df_SOPAdjustLCMWInc = pd.DataFrame(columns=df_SOPAdjustLCMW_columns)
                df_SOPAdjustLCMWAdjInc = pd.DataFrame(columns=df_SOPAdjustLCMWAdj_columns)

        else:
            df_SOPWQtyCleanInc = pd.DataFrame(columns=sopw_columns)
            df_SOPWInc = pd.DataFrame(columns=sopw_columns)
            df_SOPAdjustSETRemainMtrlInc = pd.DataFrame(columns=df_SOPAdjustSETRemainMtrl_columns)
            df_SOPAdjustmentSETWInc = pd.DataFrame(columns=df_SOPAdjustmentSETW_columns)
            df_SOPAdjustLCMWInc = pd.DataFrame(columns=df_SOPAdjustLCMW_columns)
            df_SOPAdjustLCMWAdjInc = pd.DataFrame(columns=df_SOPAdjustLCMWAdj_columns)

        step('=====> STEP4 by 2 End')




        step('=====> STEP4 by 3 Start : ADD 처리')
        if not df_in_SOPAdjustmentSETWReg.empty and not df_SOPAdjustSETWReg.empty:
            # 3.1 SOPW merge
            df_SOPAdjustSETWReg = pd.merge(df_SOPAdjustSETWReg, df_in_SOPW, how='left',
                                           left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,
                                                    TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, BOM_INFO_BOM_VERSION_COLUMN],
                                           right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,
                                                     TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, BOM_INFO_BOM_VERSION_COLUMN])
            print_df(df_SOPAdjustSETWReg, 'STEP4 by 3.1 ____ df_SOPAdjustSETWReg .... SOPW merge')


            # 3.2 가용재고(Remain Mtrl) merge
            df_SOPAdjustSETWReg = df_SOPAdjustSETWReg.merge(df_in_SOPAdjustSETRemainMtrl, how='left',
                                                            left_on=[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN,],
                                                            right_on=[VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN],)
            print_df(df_SOPAdjustSETWReg, 'STEP4 by 3.2 ____ df_SOPAdjustSETWReg .... RemainMtrl merge')


            # 3.3 df_SOPRemainSETMtrlReg create
            df_SOPRemainSETMtrlReg = df_SOPAdjustSETWReg.copy()

            #   기본 계산
            df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN] = (abs(df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]))
            df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] = (
                    (df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN]) -
                    (df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN])
            )

            #   조건에 따라 음수로 처리
            df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] = np.where(
                (df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] > 0) & (df_SOPAdjustSETRemainMtrlInc[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN] < 0),  # 원래 값이 음수이고 결과가 0보다 큰 경우
                -df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN],  # 음수로 변환
                df_SOPRemainSETMtrlReg[SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN]  # 그대로 유지
            )

            df_SOPRemainSETMtrlReg = df_SOPRemainSETMtrlReg[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN,
                SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN
            ]]

            df_SOPRemainSETMtrlReg = df_SOPRemainSETMtrlReg[df_SOPRemainSETMtrlReg_columns]
            print_df(df_SOPRemainSETMtrlReg, 'STEP4 by 3.3 ____ df_SOPRemainSETMtrlReg .... RemainMtrl final')



            # 3.4 sop w add
            df_SOPWReg = df_SOPAdjustSETWReg.copy()
            df_SOPWReg[SOP_W_SET_MFG_ADJ_QTY_COLUMN] = df_SOPWReg[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWReg[SOP_W_SET_MFG_QTY_COLUMN] = df_SOPWReg[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWReg[SOP_W_SET_SOP_QTY_COLUMN] = df_SOPWReg[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWReg[SOP_W_LCM_SOP_QTY_COLUMN] = df_SOPWReg[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPWReg = df_SOPWReg[sopw_columns]

            #   3.4.1 디맨전 컬럼 null 시  '-' 처리
            refill_columns = [
                SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, TO_ITEM_TO_ITEM_COLUMN,
                TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            ]
            df_SOPWReg[refill_columns] = df_SOPWReg[refill_columns].fillna('Dummy').astype('str')


            #   3.4.2 Week null 시 현재 주차 설정
            week_columns = [WEEK1_COLUMN, WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN]
            df_SOPWReg[week_columns] = df_SOPWReg[week_columns].fillna(mp_plan_start_week)


            #   3.4.3 'Sequence.[Sequence]' 처리
            max_sequence_value = int(max_sequence_value) + 1
            df_SOPWReg[SEQUENCE_COLUMN] = range(int(max_sequence_value), int(max_sequence_value) + len(df_SOPWReg))

            print_df(df_SOPWReg, 'STEP4 by 3.4 ____ df_SOPWReg .... final')




            # 3.5 SET W 증량 설정
            df_SOPAdjustmentSETWReg = df_SOPAdjustSETWReg.copy()
            df_SOPAdjustmentSETWReg[SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN] = df_SOPAdjustmentSETWReg[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
            df_SOPAdjustmentSETWReg = df_SOPAdjustmentSETWReg[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, TIME_WEEK_COLUMN,
                SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN
            ]]
            print_df(df_SOPAdjustmentSETWReg, 'STEP4 by 3.5 ____ df_SOPAdjustmentSETWReg .... final')




            # 3.6 LCM W 증량 설정
            #   3.6.1 LCM W
            df_SOPAdjustLCMWReg = df_SOPAdjustSETWReg.copy()
            df_SOPAdjustLCMWReg = pd.merge(df_SOPAdjustLCMWReg, df_in_SOPLCMW, how='inner',
                                           on=[VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, WEEK1_COLUMN,
                                               ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN, TO_TRANS_MODE_COLUMN,])
            print_df(df_SOPAdjustLCMWReg, 'STEP4 by 3.6.1.1 ____ df_SOPAdjustLCMWReg .... merge')

            df_SOPAdjustLCMWReg[SOP_ADJUST_LCM_W_CHG_QTY_COLUMN] = df_SOPAdjustLCMWReg[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            df_SOPAdjustLCMWReg[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN] = (
                    df_SOPAdjustLCMWReg[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN] + abs(df_SOPAdjustLCMWReg[SOP_ADJUST_SET_W_CHG_QTY_COLUMN])
            )
            df_SOPAdjustLCMWReg[SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN] = df_SOPAdjustLCMWReg[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN]
            df_SOPAdjustLCMWReg[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN] = df_SOPAdjustLCMWReg[SOP_ADJUST_SET_W_CHG_QTY_COLUMN]
            print_df(df_SOPAdjustLCMWReg, 'STEP4 by 3.6.1.2 ____ df_SOPAdjustLCMWReg .... merge 2')

            df_SOPAdjustLCMWAdjReg = df_SOPAdjustLCMWReg.copy() # df_SOPAdjustLCMWAdjReg 사전 copy

            df_SOPAdjustLCMWReg = df_SOPAdjustLCMWReg[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN,
                SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN
            ]]
            print_df(df_SOPAdjustLCMWReg, 'STEP4 by 3.6.1.3 ____ df_SOPAdjustLCMWReg .... final')

            #   3.6.2 LCM W > ADJ Qty
            df_SOPAdjustLCMWAdjReg = df_SOPAdjustLCMWAdjReg[[
                VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
                ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN
            ]]
            print_df(df_SOPAdjustLCMWAdjReg, 'STEP4 by 3.6.2 ____ df_SOPAdjustLCMWAdjReg .... final')

        else:
            df_SOPWReg = pd.DataFrame(columns=sopw_columns)
            df_SOPRemainSETMtrlReg = pd.DataFrame(columns=df_SOPRemainSETMtrlReg_columns)
            df_SOPAdjustmentSETWReg = pd.DataFrame(columns=df_SOPAdjustmentSETW_columns)
            df_SOPAdjustLCMWReg = pd.DataFrame(columns=df_SOPAdjustLCMW_columns)
            df_SOPAdjustLCMWAdjReg = pd.DataFrame(columns=df_SOPAdjustLCMWAdj_columns)

        step('=====> STEP4 by 3 End')



        step('=====> STEP4 by 4 Start : output create')
        # 데이터프레임 결합
        df_SOPWQtyClean = pd.concat([df_SOPWQtyCleanDec, df_SOPWQtyCleanInc], ignore_index=True).drop_duplicates()


        df_SOPW = pd.concat([df_SOPWQtyClean, df_SOPWDec, df_SOPWInc, df_SOPWReg], ignore_index=True).drop_duplicates()
        int_columns = [
            SOP_W_LCM_BOH_QTY_COLUMN, SOP_W_LCM_MFG_ADJ_QTY_COLUMN, SOP_W_LCM_MFG_CHG_QTY_COLUMN, SOP_W_LCM_MFG_QTY_COLUMN,
            SOP_W_LCM_SOP_ADJ_QTY_COLUMN, SOP_W_LCM_SOP_QTY_COLUMN,
            SOP_W_SET_MFG_ADJ_QTY_COLUMN, SOP_W_SET_MFG_CHG_QTY_COLUMN, SOP_W_SET_MFG_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN,
        ]
        df_SOPW[int_columns] = df_SOPW[int_columns].fillna(0).astype('Int32')
        df_SOPW = df_SOPW.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})
        print_df(df_SOPW, 'STEP4 by 4.1 ____ df_SOPW .... final')


        df_SOPAdjustSETW = pd.concat([df_SOPAdjustmentSETWDec, df_SOPAdjustmentSETWInc, df_SOPAdjustmentSETWReg], ignore_index=True).drop_duplicates()
        print_df(df_SOPAdjustSETW, 'STEP4 by 4.2 ____ df_SOPAdjustSETW .... final')


        df_SOPAdjustSETRemainMtrl = pd.concat([df_SOPAdjustSETRemainMtrlDec, df_SOPAdjustSETRemainMtrlInc, df_SOPRemainSETMtrlReg], ignore_index=True).drop_duplicates()
        str_columns = [LOCATION_COLUMN]
        df_SOPAdjustSETRemainMtrl[str_columns] = df_SOPAdjustSETRemainMtrl[str_columns].fillna('-').astype('str')
        print_df(df_SOPAdjustSETRemainMtrl, 'STEP4 by 4.3 ____ df_SOPAdjustSETRemainMtrl .... final')

        int_columns = [
            SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN,
            SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN,
        ]
        df_SOPAdjustSETRemainMtrl[int_columns] = df_SOPAdjustSETRemainMtrl[int_columns].fillna(0).astype(int)
        groupby_columns = [VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN]
        mean_columns = [SOP_ADJUST_SET_REMAIN_MTRL_INIT_REMAIN_SUPPLY_QTY_COLUMN]
        sum_columns = [SOP_ADJUST_SET_REMAIN_MTRL_ADJ_USED_QTY_COLUMN, SOP_ADJUST_SET_REMAIN_MTRL_CUR_REMAIN_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        agg_dict.update({col: 'mean' for col in mean_columns})
        df_SOPAdjustSETRemainMtrl = df_SOPAdjustSETRemainMtrl.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SOPAdjustSETRemainMtrl, 'STEP4 by 4.4 ____ df_SOPAdjustSETRemainMtrl .... groupby')


        df_SOPAdjustLCMW = pd.concat([df_SOPAdjustLCMWDec, df_SOPAdjustLCMWInc, df_SOPAdjustLCMWReg], ignore_index=True).drop_duplicates()
        groupby_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, TO_ITEM_TO_ITEM_COLUMN,
            TO_TRANS_MODE_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN,
        ]
        sum_columns = [SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_SOPAdjustLCMW = df_SOPAdjustLCMW.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SOPAdjustLCMW, 'STEP4 by 4.5 ____ df_SOPAdjustLCMW .... final')


        df_SOPAdjustLCMWAdj = pd.concat([df_SOPAdjustLCMWAdjDec, df_SOPAdjustLCMWAdjInc, df_SOPAdjustLCMWAdjReg], ignore_index=True).drop_duplicates()
        sum_columns = [SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_SOPAdjustLCMWAdj = df_SOPAdjustLCMWAdj.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SOPAdjustLCMWAdj, 'STEP4 by 4.6 ____ df_SOPAdjustLCMWAdj .... final')


        # df_out_SOPWQtyClean = rename_and_delete_df(df_SOPWQtyClean)
        df_out_SOPW = rename_and_delete_df(df_SOPW)
        df_out_SOPAdjustSETW = rename_and_delete_df(df_SOPAdjustSETW)
        df_out_SOPAdjustSETRemainMtrl = rename_and_delete_df(df_SOPAdjustSETRemainMtrl)
        df_out_SOPAdjustLCMW = rename_and_delete_df(df_SOPAdjustLCMW)
        df_out_SOPAdjustLCMWAdj = rename_and_delete_df(df_SOPAdjustLCMWAdj)

        # df_out_SOPWQtyClean[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPAdjustSETW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPAdjustSETRemainMtrl[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPAdjustLCMW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_SOPAdjustLCMWAdj[VERSION_NAME_COLUMN] = paramOutVersion
        step('=====> STEP4 by 4 End')

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        dataframes = {
            'df_out_SOPW': df_out_SOPW,
            'df_out_SOPAdjustSETW': df_out_SOPAdjustSETW,
            'df_out_SOPAdjustSETRemainMtrl': df_out_SOPAdjustSETRemainMtrl,
            'df_out_SOPAdjustLCMW': df_out_SOPAdjustLCMW,
            'df_out_SOPAdjustLCMWAdj': df_out_SOPAdjustLCMWAdj,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPW = pd.DataFrame(columns=sopw_columns)
        df_out_SOPAdjustSETW = pd.DataFrame(columns=df_SOPAdjustmentSETW_columns)
        df_out_SOPAdjustSETRemainMtrl = pd.DataFrame(columns=df_SOPAdjustSETRemainMtrl_columns)
        df_out_SOPAdjustLCMW = pd.DataFrame(columns=df_SOPAdjustLCMW_columns)
        df_out_SOPAdjustLCMWAdj = pd.DataFrame(columns=df_SOPAdjustLCMWAdj_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SOPW = pd.DataFrame(columns=sopw_columns)
        df_out_SOPAdjustSETW = pd.DataFrame(columns=df_SOPAdjustmentSETW_columns)
        df_out_SOPAdjustSETRemainMtrl = pd.DataFrame(columns=df_SOPAdjustSETRemainMtrl_columns)
        df_out_SOPAdjustLCMW = pd.DataFrame(columns=df_SOPAdjustLCMW_columns)
        df_out_SOPAdjustLCMWAdj = pd.DataFrame(columns=df_SOPAdjustLCMWAdj_columns)
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