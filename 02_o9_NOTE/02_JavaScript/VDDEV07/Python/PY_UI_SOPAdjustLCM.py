"""
* 프로그램명
    - PY_UI_SOPAdjustLCM

* 내용
    - SET, LCM제품 및 BOM Version 기준으로 SOP Adjsut 수량 할당

* 변경이력
    - 2024.10.22 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek             : Select (&CurrentWeek);
    - df_in_SOP_W_Max            : Select (Version.[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [To Time].[To Week] * [To Location].[To Location] * [Sequence].[Sequence] * [To Item].[To Item] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Week2].[Week2] * [Item Component].[Item Component] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row, ({Measure.[SOP W_BOM Cfm W], Measure.[SOP W_BOM Status], Measure.[SOP W_Chg Reason], Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID], Measure.[SOP W_Sht Qty], Measure.[SOP W_Sht Reason]}) on column orderby [Sequence].[Sequence].Name desc Limit 1;
    - df_in_SOPAdjustmentLCMWInc : Select (Version.[Version Name] * [To Item].[To Item] * [Location].[Location] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [To Trans Mode].[To Trans Mode] ) on row,  ({Measure.[SOP Adjust LCM W_Chg Qty], Measure.[SOP Adjust LCM W_SOP Adj Qty], Measure.[SOP Adjust LCM W_SOP Qty], Measure.[SOP Adjust LCM W_Before Adj Qty]}) on column.filter((Measure.[SOP Adjust LCM W_SOP Adj Qty] != Measure.[SOP Adjust LCM W_Before Adj Qty]) && Measure.[SOP Adjust LCM W_SOP Qty] > 0 && Measure.[SOP Adjust LCM W_Chg Qty] > 0);
    - df_in_SOPAdjustmentLCMWDec : Select (Version.[Version Name] * [To Item].[To Item] * [Location].[Location] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [To Trans Mode].[To Trans Mode] ) on row,  ({Measure.[SOP Adjust LCM W_Chg Qty], Measure.[SOP Adjust LCM W_SOP Adj Qty], Measure.[SOP Adjust LCM W_SOP Qty], Measure.[SOP Adjust LCM W_Before Adj Qty]}) on column.filter((Measure.[SOP Adjust LCM W_SOP Adj Qty] != Measure.[SOP Adjust LCM W_Before Adj Qty]) && Measure.[SOP Adjust LCM W_SOP Qty] > 0 && Measure.[SOP Adjust LCM W_Chg Qty] < 0);
    - df_in_SOPAdjustmentLCMWReg : Select (Version.[Version Name] * [To Item].[To Item] * [Location].[Location] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [To Trans Mode].[To Trans Mode] ) on row,  ({Measure.[SOP Adjust LCM W_Chg Qty], Measure.[SOP Adjust LCM W_SOP Adj Qty], Measure.[SOP Adjust LCM W_SOP Qty], Measure.[SOP Adjust LCM W_Before Adj Qty]}) on column.filter((Measure.[SOP Adjust LCM W_Chg Qty] == Measure.[SOP Adjust LCM W_SOP Adj Qty]) && Measure.[SOP Adjust LCM W_SOP Qty] == 0 && Measure.[SOP Adjust LCM W_Before Adj Qty] == 0  && Measure.[SOP Adjust LCM W_SOP Adj Qty] > 0);

* Flow Summary
    - 1. LCM SOP Adjustr 수량을 SOP W MG에 데이터 할당
    - 2. Version별로 데이터 처리


* Output Table
    - df_out_log
    - df_out_logDetail
    
    - df_out_SOPW
    - df_out_LCMW

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SOPAdjustLCM] for measures {[SOP W_SET MFG Qty]}
        using scope (Version.[Version Name].filter(#.Name in {"CWV_MP"}))
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPW / MG:  SOP W
        Select (&MPV * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [Location].[Location] * [To Time].[To Week] * [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Item Component].[Item Component] * [Week2].[Week2] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row,
        ({Measure.[SOP W_BOM Cfm W], Measure.[SOP W_BOM Status], Measure.[SOP W_Chg Reason], Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty], Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty], Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID], Measure.[SOP W_Sht Qty], Measure.[SOP W_Sht Reason]}) on column;

    - df_out_LCMW / MG:  SOP Adjustment LCM W
        Select (&MPV * [To Item].[To Item] * [Location].[Location] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [To Trans Mode].[To Trans Mode] ) on row,
        ({Measure.[SOP Adjust LCM W_Before Adj Qty], Measure.[SOP Adjust LCM W_Chg Qty], Measure.[SOP Adjust LCM W_SOP Adj Qty], Measure.[SOP Adjust LCM W_SOP Qty]}) on column;
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
str_instance = 'PY_UI_SOPAdjustLCM'
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
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_SOP_W_Max = read_csv_file("df_in_SOP_W_Max")
            df_in_SOPAdjustmentLCMWInc = read_csv_file("df_in_SOPAdjustmentLCMWInc")
            df_in_SOPAdjustmentLCMWDec = read_csv_file("df_in_SOPAdjustmentLCMWDec")
            df_in_SOPAdjustmentLCMWReg = read_csv_file("df_in_SOPAdjustmentLCMWReg")
    
    
        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_SOP_W_Max': df_in_SOP_W_Max,
            'df_in_SOPAdjustmentLCMWInc': df_in_SOPAdjustmentLCMWInc,
            'df_in_SOPAdjustmentLCMWDec': df_in_SOPAdjustmentLCMWDec,
            'df_in_SOPAdjustmentLCMWReg': df_in_SOPAdjustmentLCMWReg,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')


    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
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
    
        SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN = 'SOP Adjust LCM W_SOP Adj Qty'
        SOP_ADJUST_LCM_W_SOP_QTY_COLUMN = 'SOP Adjust LCM W_SOP Qty'
        SOP_ADJUST_LCM_W_CHG_QTY_COLUMN = 'SOP Adjust LCM W_Chg Qty'
        SOP_ADJUST_LCM_W_COLUMN = 'SOP Adjustment LCM W'
        SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN = 'SOP Adjust LCM W_Before Adj Qty'
    
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

        df_sop_w_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            WEEK1_COLUMN, WEEK2_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN,
            SEQUENCE_COLUMN,
            SOP_W_LCM_MFG_ADJ_QTY_COLUMN, SOP_W_LCM_MFG_CHG_QTY_COLUMN, SOP_W_LCM_SOP_QTY_COLUMN,
        ]

        df_lcm_w_columns = [
            VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN,
            ITEM_COMPONENT_COLUMN, TO_TRANS_MODE_COLUMN, SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN
        ]
    
        step('=====> STEP2 End')


    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # ====================> STEP3 by 0 (Start)
        # 0.1 현재 week 가져오기
        mp_plan_start_week = str(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')

    
        # 0.2 'Sequence.[Sequence]' 컬럼의 최대값 구하기
        max_sequence_value = str(get_first_value(df_in_SOP_W_Max, SEQUENCE_COLUMN))
        step(f'=====> max_sequence_value : {max_sequence_value}')
        # ====================> STEP3 by 0 (End)
    
    
    
    
        # ====================> STEP3 by 1 (Start)
        # 1.1 컬럼 설정, qty 컬럼 숫자 타입으로
        int_columns = [
            SOP_ADJUST_LCM_W_CHG_QTY_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_LCM_W_SOP_QTY_COLUMN,
            SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN,
        ]
        for col in int_columns:
            df_in_SOPAdjustmentLCMWInc[col] = df_in_SOPAdjustmentLCMWInc[col].fillna(0).astype('Int64')
            df_in_SOPAdjustmentLCMWDec[col] = df_in_SOPAdjustmentLCMWDec[col].fillna(0).astype('Int64')
            df_in_SOPAdjustmentLCMWReg[col] = df_in_SOPAdjustmentLCMWReg[col].fillna(0).astype('Int64')

        print_df(df_in_SOPAdjustmentLCMWInc, 'STEP3 by 1.1.1 ____ df_in_SOPAdjustmentLCMWInc .... columns type change')
        print_df(df_in_SOPAdjustmentLCMWDec, 'STEP3 by 1.1.2 ____ df_in_SOPAdjustmentLCMWDec .... columns type change')
        print_df(df_in_SOPAdjustmentLCMWReg, 'STEP3 by 1.1.3 ____ df_in_SOPAdjustmentLCMWReg .... columns type change')
        # ====================> STEP3 by 1 (End)
    
    
    
    


        step('=====> STEP3 End')


    
    
        # ################################################################################################################
        # # STEP 4 : output data machining
        # ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_sop_w = pd.concat([df_in_SOPAdjustmentLCMWInc, df_in_SOPAdjustmentLCMWDec, df_in_SOPAdjustmentLCMWReg])
        print_df(df_sop_w, 'STEP4 by 1.1 ____ df_sop_w .... pd.concat[df_in_SOPAdjustmentLCMWInc, df_in_SOPAdjustmentLCMWDec]')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_sop_w.empty:
            raise CustomException(".... df_sop_w (증량 및 감량) 값이 없습니다.")


        # 2.1 SOP W
        df_sop_w[TIME_WEEK_COLUMN] = df_sop_w[WEEK1_COLUMN]

        columns = [TO_TIME_TO_WEEK_COLUMN, WEEK2_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN]
        for col in columns:
            df_sop_w[col] = None

        df_sop_w.rename(columns={SOP_ADJUST_LCM_W_CHG_QTY_COLUMN: SOP_W_LCM_MFG_CHG_QTY_COLUMN}, inplace=True)

        week_curr_columns = [TIME_WEEK_COLUMN, TO_TIME_TO_WEEK_COLUMN, WEEK2_COLUMN,]
        for col in week_curr_columns:
            df_sop_w[col] = mp_plan_start_week
            df_sop_w[col] = df_sop_w[col].fillna(mp_plan_start_week)


        dummy_columns = [TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,]
        for col in dummy_columns:
            df_sop_w[col] = df_sop_w[col].fillna('Dummy')


        df_sop_w[SOP_W_LCM_MFG_ADJ_QTY_COLUMN] = df_sop_w[SOP_W_LCM_MFG_CHG_QTY_COLUMN]
        df_sop_w[SOP_W_LCM_SOP_QTY_COLUMN] = 0
        print_df(df_sop_w, 'STEP4 by 2.1.1 ____ df_sop_w .... modify')

        max_sequence_value = int(max_sequence_value) + 1
        df_sop_w[SEQUENCE_COLUMN] = range(int(max_sequence_value), int(max_sequence_value) + len(df_sop_w))
        print_df(df_sop_w, 'STEP4 by 2.1.2 ____ df_sop_w .... final')



        # 2.2 LCM W
        df_lcm_w = df_sop_w.copy()
        df_lcm_w[SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN] = df_lcm_w[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN]
        print_df(df_lcm_w, 'STEP4 by 2.2.1 ____ df_lcm_w .... final')



    
        df_sop_w = df_sop_w[df_sop_w_columns].drop_duplicates()
        df_lcm_w = df_lcm_w[df_lcm_w_columns].drop_duplicates()
    
        df_out_SOPW = rename_and_delete_df(df_sop_w)
        df_out_LCMW = rename_and_delete_df(df_lcm_w)

        df_out_SOPW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_LCMW[VERSION_NAME_COLUMN] = paramOutVersion

        step('=====> STEP4 End')


    
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        dataframes = {
            'df_out_SOPW': df_out_SOPW,
            'df_out_LCMW': df_out_LCMW,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')
    
        step('=====> STEP5 End')
        
    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPW = pd.DataFrame(columns=df_sop_w_columns)
        df_out_LCMW = pd.DataFrame(columns=df_lcm_w_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SOPW = pd.DataFrame(columns=df_sop_w_columns)
        df_out_LCMW = pd.DataFrame(columns=df_lcm_w_columns)
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
