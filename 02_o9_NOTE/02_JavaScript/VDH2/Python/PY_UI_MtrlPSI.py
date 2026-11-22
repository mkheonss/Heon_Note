"""
* 프로그램명
    - PY_UI_MtrlPSI

* 내용
    - Material PSI 화면의 Measure 데이터 생성


* 변경이력
    - 2024.12.23 / 권태우 / Create
    - 2025.02.19 / 권태우 / 재설계
    - 2025.10.01 / 권태우 / EOH & BOH 계산 수정

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek    : Select (&CurrentWeek);
    - df_in_AllWeek     : Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
    - df_in_MDMHorizon  : Select (&MDMHorizon);
    - df_in_Item        : Select ([Item].[Item].filter(~(#.Name contains "DUMMY")) * [Item].[Item Stage].filter(~(#.Name in {"SET", "LCM"})) * [Item].[Const Type].filter(#.Name in {"Hard"}));
    - df_in_FullBOM     : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, ({Measure.[Full BOM_Consume Qty]}) on column;
    - df_in_SOPDemandW  : Select ([Version].[Version Name] * [Item].[Item] * &MDMHorizon * [To Location].[To Location] * [To Item].[To Item] * [Location].[Location] * [To Time].[To Week] * [Sequence].[Sequence] * [Demand].[DemandID] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [Item Component].[Item Component] * [Week2].[Week2] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row, ({Measure.[SOP Dmd W_LCM BOH Qty], Measure.[SOP Dmd W_LCM MFG Qty], Measure.[SOP Dmd W_LCM SOP Qty], Measure.[SOP Dmd W_SET BOH Qty], Measure.[SOP Dmd W_SET MFG Qty], Measure.[SOP Dmd W_SET SOP Qty]}) on column;
    - df_in_DmdW        : Select ([Version].[Version Name] * [Item].[Item] * &MDMHorizon * [Location].[Location] * [Sales Domain].[Ship To] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[Dmd W_ID]}) on column ;
    - df_in_BODAll      : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[BOD All_BOD Prty], Measure.[BOD All_SET Site], Measure.[BOD All_SET BOD LT], Measure.[BOD All_SET Trans Mode], Measure.[BOD All_LCM Code], Measure.[BOD All_LCM Site], Measure.[BOD All_LCM BOD LT], Measure.[BOD All_LCM Trans Mode]}) on column;
    - df_in_Inventory   : Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].filter(~(#.Name in {"LCM", "SET", "LED_MODULE"})) * [Time].[Week] * [Location].[Location] * [Location].[Site Stage].filter(#.Name != "SP")  ) on row, ({Measure.[Inv_Qty],Measure.[Inv_To Site]}) on column;
    - df_in_DistributionOrder : Select (Version.[Version Name] * [Item].[Item] * [Location].[Location] * [Documents].[OrderlineID] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Dummy], Measure.[Dist Order_SS Delivery Date], Measure.[Dist Order_SS Qty]}) on column;
    - df_in_MtrlProdPlan: Select ([Version].[Version Name] * [Location].[Location] * Location.[Site Stage].filter(#.Name contains "MF") * [Item].[Item] * [Item].[Item Stage].filter(~(#.Name in {"SET", "LCM", "LED_MODULE"})) * [Time].[Week] * [Documents].[OrderlineID] * [Activity1].[Activity1].filter(#.Name != "ExpectedReceiptActivity") * [Activity2].[Activity2] * [Activity3].[Activity3] * [Activity1].[From Location] ) on row, ({Measure.[W Material Production Quantity Plan Output]}) on column;
    - df_in_SOPDmdBOM   : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [BOM Info].[BOM Version]) on row, ({Measure.[SOP Dmd W_SET MFG Qty]}) on column.filter(Measure.[SOP Dmd W_SET MFG Qty] > 0);

* Flow Summary
    -
* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_MtrlPSIStructure
    - df_out_MtrlPSI
    - df_out_ReqQuantity


* 데이타 초기화
    - DELETE DATA FOR MODEL [Mtrl PSI Structure] WHERE {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};
    - DELETE DATA FOR MODEL [Mtrl PSI Req] WHERE {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};
    - DELETE DATA FOR MODEL [Mtrl PSI] WHERE {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_MtrlPSI] for Measures {[Mtrl PSI_REQ_Demand Fixed]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_MtrlPSIStructure / MG : Mtrl PSI Structure
        Select (&MPV * [Location].[Location] * [Item].[Item Stage] * [To Location].[To Location] * [To Item].[To Item] * [To Time].[To Week] * [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Item Component].[Item Component] ) on row, ({
            Measure.[Mtrl PSI Structure_BOM ID], Measure.[Mtrl PSI Structure_BOM Version], Measure.[Mtrl PSI Structure_Cons Item LCM], Measure.[Mtrl PSI Structure_Cons Item SET], Measure.[Mtrl PSI Structure_Dmd W_ID],
            Measure.[Mtrl PSI Structure_LCM Cons Qty], Measure.[Mtrl PSI Structure_LCM Week], Measure.[Mtrl PSI Structure_Set Cons Qty], Measure.[Mtrl PSI Structure_Set Week], Measure.[Mtrl PSI Structure_Status]}) on column;

    - df_out_ReqQuantity / MG : Mtrl PSI Req
        Select (&MPV * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Item Material].[Item Material] * [Category].[Category] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [BOM Status].[BOM Status] ) on row, ({Measure.[Mtrl PSI Req_Quantity]}) on column;

    - df_out_MtrlPSI / MG:  Mtrl PSI
        Select (&MPV * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({
            Measure.[Mtrl PSI_ARRIVAL_CMI], Measure.[Mtrl PSI_ARRIVAL_Excel], Measure.[Mtrl PSI_ARRIVAL_Global RTF], Measure.[Mtrl PSI_ARRIVAL_Open PO], Measure.[Mtrl PSI_ARRIVAL_RTF],
            Measure.[Mtrl PSI_ARRIVAL_RTP], Measure.[Mtrl PSI_ARRIVAL_SN], Measure.[Mtrl PSI_ARRIVAL_Supply Plan], Measure.[Mtrl PSI_ARRIVAL_Total], Measure.[Mtrl PSI_Actual BOH],
            Measure.[Mtrl PSI_Actual EOH], Measure.[Mtrl PSI_Actual GR], Measure.[Mtrl PSI_BOH_Demand], Measure.[Mtrl PSI_BOH_Demand Fixed], Measure.[Mtrl PSI_BOH_Demand_Actual],
            Measure.[Mtrl PSI_BOH_SOP], Measure.[Mtrl PSI_BOH_SOP Export], Measure.[Mtrl PSI_BOH_SOP Fixed], Measure.[Mtrl PSI_BOH_SOP_Actual], Measure.[Mtrl PSI_EOH_Demand],
            Measure.[Mtrl PSI_EOH_Demand Fixed], Measure.[Mtrl PSI_EOH_SOP], Measure.[Mtrl PSI_EOH_SOP EC], Measure.[Mtrl PSI_EOH_SOP Export], Measure.[Mtrl PSI_EOH_SOP FCST HQ],
            Measure.[Mtrl PSI_EOH_SOP FCST Local], Measure.[Mtrl PSI_EOH_SOP Fixed], Measure.[Mtrl PSI_EOH_SOP HQ], Measure.[Mtrl PSI_REQ_Demand], Measure.[Mtrl PSI_REQ_Demand Fixed],
            Measure.[Mtrl PSI_REQ_Demand Unfixed], Measure.[Mtrl PSI_REQ_SOP Export], Measure.[Mtrl PSI_REQ_SOP MPI L], Measure.[Mtrl PSI_REQ_SOP SET], Measure.[Mtrl PSI_REQ_SOP Status],
            Measure.[Mtrl PSI_REQ_SOP Status_Actual], Measure.[Mtrl PSI_REQ_SOP Type], Measure.[Mtrl PSI_REQ_SOP Type_Actual], Measure.[Mtrl PSI_REQ_Status Dash_Dual],
            Measure.[Mtrl PSI_REQ_Status Dash_New], Measure.[Mtrl PSI_REQ_Status EC], Measure.[Mtrl PSI_REQ_Status Fixed], Measure.[Mtrl PSI_REQ_Status Forecast_HQ],
            Measure.[Mtrl PSI_REQ_Status Forecast_Local], Measure.[Mtrl PSI_REQ_Status HQ], Measure.[Mtrl PSI_REQ_Status NSCM], Measure.[Mtrl PSI_REQ_Status Unfixed],
            Measure.[Mtrl PSI_REQ_Type SET], Measure.[Mtrl PSI_REQ_Type SOP Assy]}) on column;
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
str_instance = 'PY_UI_MtrlPSI'
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



def set_unique_combinations(df, df2, columns):
    cols = list(filter(lambda col: col != TIME_WEEK_COLUMN, columns))

    # 데이터의 모든 고유 조합 생성
    unique_combinations = df[cols].copy().drop_duplicates()

    # 주차(TIME_WEEK_COLUMN) 데이터의 모든 조합 산출
    df2 = df2.assign(key=1)
    unique_combinations = unique_combinations.assign(key=1)
    all_possible_combinations = unique_combinations.merge(df2, how="outer").drop(columns=['key']).drop_duplicates()

    # 결측 데이터 찾기 (left join & 필터링)
    missing_rows = all_possible_combinations.merge(
        df[columns], on=columns, how="left", indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return missing_rows




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
        # STEP 1 : input table load
        ################################################################################################################
        step('=====> STEP1 Start : input table load')

        if is_local:
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")
            df_in_MDMHorizon = read_csv_file("df_in_MDMHorizon")
            df_in_FullBOM = read_csv_file("df_in_FullBOM")
            df_in_Item = read_csv_file("df_in_Item")
            df_in_SOPDemandW = read_csv_file("df_in_SOPDemandW")
            df_in_DmdW = read_csv_file("df_in_DmdW")
            df_in_BODAll = read_csv_file("df_in_BODAll")
            df_in_Inventory = read_csv_file("df_in_Inventory")
            df_in_DistributionOrder = read_csv_file("df_in_DistributionOrder")
            df_in_MtrlProdPlan = read_csv_file("df_in_MtrlProdPlan")
            df_in_SOPDmdBOM = read_csv_file("df_in_SOPDmdBOM")

        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_MDMHorizon': df_in_MDMHorizon,
            'df_in_FullBOM': df_in_FullBOM,
            'df_in_Item': df_in_Item,
            'df_in_SOPDemandW': df_in_SOPDemandW,
            'df_in_DmdW': df_in_DmdW,
            'df_in_BODAll': df_in_BODAll,
            'df_in_Inventory': df_in_Inventory,
            'df_in_DistributionOrder': df_in_DistributionOrder,
            'df_in_MtrlProdPlan': df_in_MtrlProdPlan,
            'df_in_SOPDmdBOM': df_in_SOPDmdBOM,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_DAY_KEY_COLUMN = 'Time.[DayKey]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAY_WEEK_COLUMN = 'Time.[Day of Week]'
        TIME_DAY_COLUMN = 'Time.[Day]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'
        BOM_INFO_ITEM_COLUMN = 'BOM Info.[Item]'
        BOM_INFO_SET_ITEM_COLUMN = 'BOM Info.[SET Item]'
        BOM_INFO_LCM_ITEM_COLUMN = 'BOM Info.[LCM Item]'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'
        LOCATION_SITE_STAGE_COLUMN = 'Location.[Site Stage]'
        INV_QTY_COLUMN = 'Inv_Qty'
        INV_TO_SITE_COLUMN = 'Inv_To Site'
        SALES_DOMAIN_SHIP_TO_COLUMN = 'Sales Domain.[Ship To]'
        DEMAND_TYPE__COLUMN = 'Demand Type.[Demand Type]'
        DMD_W_ID_COLUMN = 'Dmd W_ID'
        CONS_ITEM_SET_COLUMN = 'Cons Item SET'
        CONS_ITEM_LCM_COLUMN = 'Cons Item LCM'
        CONS_ITEM_COLUMN = 'Cons Item'
        SET_CONS_QTY_COLUMN = 'Set Cons Qty'
        LCM_CONS_QTY_COLUMN = 'LCM Cons Qty'
        CONS_QTY_COLUMN = 'Cons Qty'
        CONSUME_PER_COLUMN = 'Consume Per'
        BOM_STATUS_COLUMN = 'BOM_Status'
        PSI_LOCATION_COLUMN = 'PSI Location'
        CONST_TYPE_COLUMN = 'Const Type'
        DUE_WEEK_COLUMN = 'DueWeek'
        DUE_DATE_COLUMN = 'DueDate'
        SET_LT_COLUMN = 'Set LT'
        SET_DATE_COLUMN = 'SetDate'
        SET_WEEK_COLUMN = 'SetWeek'
        LCM_LT_COLUMN = 'LCM LT'
        LCM_DATE_COLUMN = 'LCMDate'
        LCM_WEEK_COLUMN = 'LCMWeek'
        CATEGORY_CATEGORY_COLUMN = 'Category.[Category]'

        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY1_FROM_LOCATIONCOLUMN = 'Activity1.[From Location]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
        W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN = 'W Material Production Quantity Plan Output'

        SOP_DMD_W_LCM_BOH_QTY_COLUMN = 'SOP Dmd W_LCM BOH Qty'
        SOP_DMD_W_LCM_MFG_QTY_COLUMN = 'SOP Dmd W_LCM MFG Qty'
        SOP_DMD_W_LCM_SOP_QTY_COLUMN = 'SOP Dmd W_LCM SOP Qty'
        SOP_DMD_W_SET_BOH_QTY_COLUMN = 'SOP Dmd W_SET BOH Qty'
        SOP_DMD_W_SET_MFG_QTY_COLUMN = 'SOP Dmd W_SET MFG Qty'
        SOP_DMD_W_SET_SOP_QTY_COLUMN = 'SOP Dmd W_SET SOP Qty'

        BOM_INFO_BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_MASTER_BOM_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'

        FULL_BOM_CONSUME_QTY_COLUMN = 'Full BOM_Consume Qty'
        STATUS_STATUS_COLUMN = 'Status.[Status]'
        BOM_TYPE_BOM_TYPE_COLUMN = 'BOM Type.[BOM Type]'
        BOM_STATUS_BOM_STATUS_COLUMN = 'BOM Status.[BOM Status]'
        ITEM_CONST_TYPE_COLUMN = 'Item.[Const Type]'

        BOD_ALL_BOD_PRTY_COLUMN = 'BOD All_BOD Prty'
        BOD_ALL_SET_SITE_COLUMN = 'BOD All_SET Site'
        BOD_ALL_SET_BOD_LT_COLUMN = 'BOD All_SET BOD LT'
        BOD_ALL_SET_TRANS_MODE_COLUMN = 'BOD All_SET Trans Mode'
        BOD_ALL_LCM_CODE_COLUMN = 'BOD All_LCM Code'
        BOD_ALL_LCM_SITE_COLUMN = 'BOD All_LCM Site'
        BOD_ALL_LCM_BOD_LT_COLUMN = 'BOD All_LCM BOD LT'
        BOD_ALL_LCM_TRANS_MODE_COLUMN = 'BOD All_LCM Trans Mode'

        DIST_ORDER_SS_DELIVERY_DATE_COLUMN = 'Dist Order_SS Delivery Date'
        DIST_ORDER_SS_QTY_COLUMN = 'Dist Order_SS Qty'

        MTRL_PSI_ARRIVAL_CMI_COLUMN = 'Mtrl PSI_ARRIVAL_CMI'
        MTRL_PSI_ARRIVAL_EXCEL_COLUMN = 'Mtrl PSI_ARRIVAL_Excel'
        MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN = 'Mtrl PSI_ARRIVAL_Global RTF'
        MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN = 'Mtrl PSI_ARRIVAL_Open PO'
        MTRL_PSI_ARRIVAL_RTF_COLUMN = 'Mtrl PSI_ARRIVAL_RTF'
        MTRL_PSI_ARRIVAL_RTP_COLUMN = 'Mtrl PSI_ARRIVAL_RTP'
        MTRL_PSI_ARRIVAL_SN_COLUMN = 'Mtrl PSI_ARRIVAL_SN'
        MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN = 'Mtrl PSI_ARRIVAL_Supply Plan'
        MTRL_PSI_ARRIVAL_TOTAL_COLUMN = 'Mtrl PSI_ARRIVAL_Total'
        MTRL_PSI_ACTUAL_BOH_COLUMN = 'Mtrl PSI_Actual BOH'
        MTRL_PSI_ACTUAL_EOH_COLUMN = 'Mtrl PSI_Actual EOH'
        MTRL_PSI_ACTUAL_GR_COLUMN = 'Mtrl PSI_Actual GR'
        MTRL_PSI_BOH_DEMAND_COLUMN = 'Mtrl PSI_BOH_Demand'
        MTRL_PSI_BOH_DEMAND_FIXED_COLUMN = 'Mtrl PSI_BOH_Demand Fixed'
        MTRL_PSI_BOH_DEMAND_ACTUAL_COLUMN = 'Mtrl PSI_BOH_Demand_Actual'
        MTRL_PSI_BOH_SOP_COLUMN = 'Mtrl PSI_BOH_SOP'
        MTRL_PSI_BOH_SOP_EXPORT_COLUMN = 'Mtrl PSI_BOH_SOP Export'
        MTRL_PSI_BOH_SOP_FIXED_COLUMN = 'Mtrl PSI_BOH_SOP Fixed'
        MTRL_PSI_BOH_SOP_ACTUAL_COLUMN = 'Mtrl PSI_BOH_SOP_Actual'
        MTRL_PSI_EOH_DEMAND_COLUMN = 'Mtrl PSI_EOH_Demand'
        MTRL_PSI_EOH_DEMAND_FIXED_COLUMN = 'Mtrl PSI_EOH_Demand Fixed'
        MTRL_PSI_EOH_SOP_COLUMN = 'Mtrl PSI_EOH_SOP'
        MTRL_PSI_EOH_SOP_EC_COLUMN = 'Mtrl PSI_EOH_SOP EC'
        MTRL_PSI_EOH_SOP_EXPORT_COLUMN = 'Mtrl PSI_EOH_SOP Export'
        MTRL_PSI_EOH_SOP_FCST_HQ_COLUMN = 'Mtrl PSI_EOH_SOP FCST HQ'
        MTRL_PSI_EOH_SOP_FCST_LOCAL_COLUMN = 'Mtrl PSI_EOH_SOP FCST Local'
        MTRL_PSI_EOH_SOP_FIXED_COLUMN = 'Mtrl PSI_EOH_SOP Fixed'
        MTRL_PSI_EOH_HQ_COLUMN = 'Mtrl PSI_EOH_SOP HQ'
        MTRL_PSI_REQ_DEMAND_COLUMN = 'Mtrl PSI_REQ_Demand'
        MTRL_PSI_REQ_DEMAND_FIXED_COLUMN = 'Mtrl PSI_REQ_Demand Fixed'
        MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN = 'Mtrl PSI_REQ_Demand Unfixed'
        MTRL_PSI_REQ_SOP_EXPORT_COLUMN = 'Mtrl PSI_REQ_SOP Export'
        MTRL_PSI_REQ_SOP_MPI_L_COLUMN = 'Mtrl PSI_REQ_SOP MPI L'
        MTRL_PSI_REQ_SOP_SET_COLUMN = 'Mtrl PSI_REQ_SOP SET'
        MTRL_PSI_REQ_SOP_STATUS_COLUMN = 'Mtrl PSI_REQ_SOP Status'
        MTRL_PSI_REQ_SOP_STATUS_ACTUAL_COLUMN = 'Mtrl PSI_REQ_SOP Status_Actual'
        MTRL_PSI_REQ_SOP_TYPE_COLUMN = 'Mtrl PSI_REQ_SOP Type'
        MTRL_PSI_REQ_SOP_TYPE_ACTUAL_COLUMN = 'Mtrl PSI_REQ_SOP Type_Actual'
        MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN = 'Mtrl PSI_REQ_Status Dash_Dual'
        MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN = 'Mtrl PSI_REQ_Status Dash_New'
        MTRL_PSI_REQ_STATUS_EC_COLUMN = 'Mtrl PSI_REQ_Status EC'
        MTRL_PSI_REQ_STATUS_FIXED_COLUMN = 'Mtrl PSI_REQ_Status Fixed'
        MTRL_PSI_REQ_STATUS_FORCAST_HQ_COLUMN = 'Mtrl PSI_REQ_Status Forecast_HQ'
        MTRL_PSI_REQ_STATUS_FORCAST_LOCAL_COLUMN = 'Mtrl PSI_REQ_Status Forecast_Local'
        MTRL_PSI_REQ_STATUS_HQ_COLUMN = 'Mtrl PSI_REQ_Status HQ'
        MTRL_PSI_REQ_STATUS_NSCM_COLUMN = 'Mtrl PSI_REQ_Status NSCM'
        MTRL_PSI_REQ_STATUS_UNFIXED_COLUMN = 'Mtrl PSI_REQ_Status Unfixed'
        MTRL_PSI_REQ_TYPE_SET_COLUMN = 'Mtrl PSI_REQ_Type SET'
        MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN = 'Mtrl PSI_REQ_Type SOP Assy'

        MTRL_PSI_REQ_QUANTITY_COLUMN = 'Mtrl PSI Req_Quantity'

        SET_WEEK_COLUMN = 'Set Week'
        LCM_WEEK_COLUMN = 'LCM Week'

        FIXED_VALUE = 'Fixed'
        HQ_VALUE = 'HQ'
        NSCM_VALUE = 'NSCM'
        DASH_NEW_VALUE = 'Dash_New'
        DASH_DUAL_VALUE = 'Dash_Dual'
        EC_VALUE = 'EC'
        SET_VALUE = 'SET'
        SOP_ASSY_VALUE = 'SOP Assy'
        SOP_STATUS_VALUE = 'SOP_Status'
        DP_SOP_VALUE = 'DP_SOP'

        MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN = 'Mtrl PSI Structure_BOM Type'
        MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN = 'Mtrl PSI Structure_BOM_Status'
        MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN = 'Mtrl PSI Structure_Cons Item'
        MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN = 'Mtrl PSI Structure_Cons Qty'
        MTRL_PSI_STRUCTURE_CONST_TYPE_COLUMN = 'Mtrl PSI Structure_Const Type'
        MTRL_PSI_STRUCTURE_CONSUME_PER_COLUMN = 'Mtrl PSI Structure_Consume Per'
        MTRL_PSI_STRUCTURE_DUE_DATE_COLUMN = 'Mtrl PSI Structure_DueDate'
        MTRL_PSI_STRUCTURE_DUE_WEEK_COLUMN = 'Mtrl PSI Structure_DueWeek'
        MTRL_PSI_STRUCTURE_LCM_LT_COLUMN = 'Mtrl PSI Structure_LCM LT'
        MTRL_PSI_STRUCTURE_LCM_MFG_QTY_COLUMN = 'Mtrl PSI Structure_LCM MFG Qty'
        MTRL_PSI_STRUCTURE_LCM_DATE_COLUMN = 'Mtrl PSI Structure_LCMDate'
        MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN = 'Mtrl PSI Structure_LCMWeek'
        MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN = 'Mtrl PSI Structure_PSI Location'
        MTRL_PSI_STRUCTURE_SET_MFG_QTY_COLUMN = 'Mtrl PSI Structure_SET MFG Qty'
        MTRL_PSI_STRUCTURE_SET_LT_COLUMN = 'Mtrl PSI Structure_Set LT'
        MTRL_PSI_STRUCTURE_SET_DATE_COLUMN = 'Mtrl PSI Structure_SetDate'
        MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN = 'Mtrl PSI Structure_SetWeek'

        df_MtrlPSIStructure_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, WEEK1_COLUMN, SEQUENCE_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, DEMAND_ID_COLUMN,
            MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN, MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN, MTRL_PSI_STRUCTURE_CONST_TYPE_COLUMN, MTRL_PSI_STRUCTURE_CONSUME_PER_COLUMN,
            MTRL_PSI_STRUCTURE_DUE_DATE_COLUMN, MTRL_PSI_STRUCTURE_DUE_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_LCM_LT_COLUMN, MTRL_PSI_STRUCTURE_LCM_MFG_QTY_COLUMN, MTRL_PSI_STRUCTURE_LCM_DATE_COLUMN, MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_SET_LT_COLUMN, MTRL_PSI_STRUCTURE_SET_MFG_QTY_COLUMN, MTRL_PSI_STRUCTURE_SET_DATE_COLUMN, MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN,
        ]

        df_MtrlPSI_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TIME_WEEK_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_DEMAND_FIXED_COLUMN, MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN,
            MTRL_PSI_REQ_SOP_STATUS_COLUMN, MTRL_PSI_REQ_STATUS_FIXED_COLUMN, MTRL_PSI_REQ_STATUS_HQ_COLUMN, MTRL_PSI_REQ_STATUS_NSCM_COLUMN,
            MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN, MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN, MTRL_PSI_REQ_STATUS_EC_COLUMN,
            MTRL_PSI_REQ_SOP_TYPE_COLUMN, MTRL_PSI_REQ_TYPE_SET_COLUMN, MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN, MTRL_PSI_REQ_SOP_EXPORT_COLUMN,
            MTRL_PSI_ARRIVAL_SN_COLUMN, MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN, MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN,
            MTRL_PSI_ARRIVAL_RTP_COLUMN, MTRL_PSI_ARRIVAL_RTF_COLUMN, MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN, MTRL_PSI_ARRIVAL_CMI_COLUMN, MTRL_PSI_ARRIVAL_EXCEL_COLUMN,
            MTRL_PSI_BOH_DEMAND_COLUMN, MTRL_PSI_BOH_DEMAND_FIXED_COLUMN, MTRL_PSI_BOH_SOP_COLUMN, MTRL_PSI_BOH_SOP_FIXED_COLUMN, MTRL_PSI_BOH_SOP_EXPORT_COLUMN,
            MTRL_PSI_EOH_DEMAND_COLUMN, MTRL_PSI_EOH_DEMAND_FIXED_COLUMN, MTRL_PSI_EOH_SOP_COLUMN, MTRL_PSI_EOH_SOP_FIXED_COLUMN, MTRL_PSI_EOH_SOP_EXPORT_COLUMN,
        ]

        df_ReqQuantity_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN,
            ITEM_METERIAL_COLUMN, CATEGORY_CATEGORY_COLUMN, BOM_STATUS_BOM_STATUS_COLUMN, MTRL_PSI_REQ_QUANTITY_COLUMN,
        ]

        int_base_columns = [
            MTRL_PSI_REQ_DEMAND_FIXED_COLUMN, MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN, MTRL_PSI_REQ_SOP_STATUS_COLUMN,
            MTRL_PSI_REQ_STATUS_FIXED_COLUMN, MTRL_PSI_REQ_STATUS_HQ_COLUMN, MTRL_PSI_REQ_STATUS_NSCM_COLUMN, MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN,
            MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN, MTRL_PSI_REQ_STATUS_EC_COLUMN, MTRL_PSI_REQ_SOP_TYPE_COLUMN,
            MTRL_PSI_REQ_TYPE_SET_COLUMN, MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN, MTRL_PSI_REQ_SOP_EXPORT_COLUMN,
            MTRL_PSI_ARRIVAL_SN_COLUMN, MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN, MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN, MTRL_PSI_ARRIVAL_RTP_COLUMN,
            MTRL_PSI_ARRIVAL_RTF_COLUMN, MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN, MTRL_PSI_ARRIVAL_CMI_COLUMN, MTRL_PSI_ARRIVAL_EXCEL_COLUMN,
        ]

        int_boh_columns = [
            MTRL_PSI_BOH_DEMAND_COLUMN, MTRL_PSI_BOH_DEMAND_FIXED_COLUMN, MTRL_PSI_BOH_SOP_COLUMN, MTRL_PSI_BOH_SOP_FIXED_COLUMN, MTRL_PSI_BOH_SOP_EXPORT_COLUMN,
        ]

        int_eoh_columns = [
            MTRL_PSI_EOH_DEMAND_COLUMN, MTRL_PSI_EOH_DEMAND_FIXED_COLUMN, MTRL_PSI_EOH_SOP_COLUMN, MTRL_PSI_EOH_SOP_FIXED_COLUMN, MTRL_PSI_EOH_SOP_EXPORT_COLUMN,
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_SOPDemandW = df_in_SOPDemandW[df_in_SOPDemandW[DEMAND_ID_COLUMN] == 'DMD_0000407284']
        # df_in_FullBOM = df_in_FullBOM[df_in_FullBOM[ITEM_METERIAL_COLUMN] == 'BN96-52526L']
        # df_in_Item = df_in_Item[df_in_Item[ITEM_COLUMN] == 'BN96-52526L']
        # save_csv_file(df_in_SOPDemandW, 'STEP3 by 0.0 ____ df_in_SOPDemandW .... filter')
        # ------------------ 테스트 디버깅용 ------------------ end



        # ====================> STEP3 by 0 (Start)

        # 0.1 컬럼삭제 및 초기값 설정
        drop_columns = ['Dummy', SEQUENCE_COLUMN]
        for col in drop_columns:
            df_in_BODAll.drop(columns=[col], inplace=True, errors='ignore')
            df_in_SOPDemandW.drop(columns=[col], inplace=True, errors='ignore')
            df_in_DistributionOrder.drop(columns=[col], inplace=True, errors='ignore')


        str_columns = [BOD_ALL_SET_SITE_COLUMN, BOD_ALL_SET_TRANS_MODE_COLUMN, BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN, BOD_ALL_LCM_TRANS_MODE_COLUMN]
        for col in str_columns:
            df_in_BODAll[col] = df_in_BODAll[col].fillna('-').astype('str')

        int_columns = [BOD_ALL_SET_BOD_LT_COLUMN, BOD_ALL_LCM_BOD_LT_COLUMN]
        for col in int_columns:
            df_in_BODAll[col] = df_in_BODAll[col].fillna(0)

        week_columns = [TIME_WEEK_COLUMN]
        for col in week_columns:
            df_in_MDMHorizon[col] = df_in_MDMHorizon[col].astype(str)
            df_in_SOPDemandW[col] = df_in_SOPDemandW[col].astype(str)
            df_in_DmdW[col] = df_in_DmdW[col].astype(str)
            df_in_AllWeek[col] = df_in_AllWeek[col].astype(str)
            df_in_Inventory[col] = df_in_Inventory[col].astype(str)


        # 0.2 현재 주차 가져오기
        current_week = int(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> current_week : {current_week}')



        # 0.3 df_in_AllWeek 필요컬럼 설정
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN, TIME_DAY_COLUMN, TIME_DAY_WEEK_COLUMN]].drop_duplicates()
        df_in_AllWeek[TIME_DAY_COLUMN] = df_in_AllWeek[TIME_DAY_COLUMN].astype(str)
        print_df(df_in_AllWeek, 'STEP3 by 0.1  ____ df_in_AllWeek .... remake')



        # 0.4 df_in_DistributionOrder 에 주차 컬럼 생성
        #   날짜 형식 지정 (명확하게 정의)
        formats = [
            '%m/%d/%Y %I:%M:%S %p',  # 11/24/2024 12:00:00 AM
            '%Y-%m-%d %H:%M:%S'  # 2024-11-24 00:00:00
        ]

        def parse_dates(column):
            parsed_dates_1 = pd.to_datetime(df_in_DistributionOrder[column], format=formats[0], errors='coerce')
            parsed_dates_2 = pd.to_datetime(df_in_DistributionOrder[column], format=formats[1], errors='coerce')
            return parsed_dates_1.fillna(parsed_dates_2).dt.date

        df_in_DistributionOrder[DIST_ORDER_SS_DELIVERY_DATE_COLUMN] = parse_dates(DIST_ORDER_SS_DELIVERY_DATE_COLUMN)
        df_in_DistributionOrder[DIST_ORDER_SS_DELIVERY_DATE_COLUMN] = df_in_DistributionOrder[DIST_ORDER_SS_DELIVERY_DATE_COLUMN].astype(str)
        print_df(df_in_DistributionOrder, 'STEP3 by 0.2  ____ df_in_DistributionOrder .... date format changed')

        df_in_DistributionOrder = pd.merge(df_in_DistributionOrder, df_in_AllWeek, how='left',
                                           left_on=[DIST_ORDER_SS_DELIVERY_DATE_COLUMN],
                                           right_on=[TIME_DAY_COLUMN])
        print_df(df_in_DistributionOrder, 'STEP3 by 0.3  ____ df_in_DistributionOrder .... merge[df_in_DistributionOrder, df_in_AllWeek]')

        df_in_DistributionOrder = df_in_DistributionOrder[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, DIST_ORDER_SS_QTY_COLUMN, TIME_WEEK_COLUMN
        ]]
        print_df(df_in_DistributionOrder, 'STEP3 by 0.4  ____ df_in_DistributionOrder .... final')
        
        # ====================> STEP3 by 0 (End)




        # ====================> STEP3 by 1 (Start) > df_in_FullBOM modify

        # 1.1 df_in_FullBOM, df_in_Item merge
        df_in_FullBOM = pd.merge(df_in_FullBOM, df_in_Item, how='inner',
                                 left_on=[ITEM_METERIAL_COLUMN],
                                 right_on=[ITEM_COLUMN]).drop_duplicates()
        print_df(df_in_FullBOM, 'STEP3 by 1.1.1 ____ df_in_FullBOM .... merge[df_in_FullBOM, df_in_Item]')

        df_in_FullBOM.rename(columns={ITEM_COLUMN+'_x': ITEM_COLUMN,}, inplace=True)
        df_in_FullBOM.drop(columns=[ITEM_COLUMN+'_y', ITEM_STAGE_COLUMN], inplace=True)
        print_df(df_in_FullBOM, 'STEP3 by 1.1.2 ____ df_in_FullBOM .... column rename')

        df_in_FullBOM = pd.merge(df_in_FullBOM, df_in_SOPDmdBOM, how='inner', on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN])
        df_in_FullBOM.drop(columns=[SOP_DMD_W_SET_MFG_QTY_COLUMN], inplace=True)

        df_set_FullBOM = df_in_FullBOM[df_in_FullBOM[BOM_TYPE_BOM_TYPE_COLUMN] == SET_VALUE].copy()
        print_df(df_set_FullBOM, 'STEP3 by 1.1.3 ____ df_set_FullBOM .... reselect')

        df_lcm_FullBOM = df_in_FullBOM[df_in_FullBOM[BOM_TYPE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE].copy()
        print_df(df_lcm_FullBOM, 'STEP3 by 1.1.4 ____ df_lcm_FullBOM .... reselect')

        delete_dfs(df_in_FullBOM)

        # ====================> STEP3 by 1 (End)




        # ====================> STEP3 by 2 (Start) > df_bom_sop_dmdw create

        # 2.1 df_set_bom_sop_dmdw create
        #   2.1.1 df_in_SOPDemandW, df_set_FullBOM merge
        df_set_bom_sop_dmdw = pd.merge(df_in_SOPDemandW, df_set_FullBOM, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN])
        print_df(df_set_bom_sop_dmdw, 'STEP3 by 2.1.1 ____ df_set_bom_sop_dmdw .... merge[df_in_SOPDemandW, df_set_FullBOM]')

        #   2.1.2 컬럼명 추가/수정/삭제
        df_set_bom_sop_dmdw.drop(columns=[ITEM_COLUMN+'_y', LOCATION_COLUMN+'_y', TO_ITEM_TO_ITEM_COLUMN+'_x'], inplace=True)

        df_set_bom_sop_dmdw.rename(columns={
            ITEM_COLUMN+'_x': ITEM_COLUMN,
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN+'_y': TO_ITEM_TO_ITEM_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN+'_x': TO_LOCATION_TO_LOCATION_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN+'_y': PSI_LOCATION_COLUMN,
            ITEM_METERIAL_COLUMN+'_x': ITEM_METERIAL_COLUMN,
            ITEM_METERIAL_COLUMN+'_y': CONS_ITEM_COLUMN,
            FULL_BOM_CONSUME_QTY_COLUMN: CONSUME_PER_COLUMN,
            BOM_STATUS_BOM_STATUS_COLUMN: BOM_STATUS_COLUMN,
            ITEM_CONST_TYPE_COLUMN: CONST_TYPE_COLUMN,
        }, inplace=True)
        df_set_bom_sop_dmdw[CONS_QTY_COLUMN] = df_set_bom_sop_dmdw[SOP_DMD_W_SET_MFG_QTY_COLUMN] * df_set_bom_sop_dmdw[CONSUME_PER_COLUMN]
        print_df(df_set_bom_sop_dmdw, 'STEP3 by 2.1.2 ____ df_set_bom_sop_dmdw .... create')



        # 2.2 df_lcm_bom_sop_dmdw create
        #   2.2.1 df_in_SOPDemandW, df_lcm_FullBOM merge
        df_lcm_bom_sop_dmdw = pd.merge(df_in_SOPDemandW, df_lcm_FullBOM, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN])
        print_df(df_lcm_bom_sop_dmdw, 'STEP3 by 2.2.1 ____ df_lcm_bom_sop_dmdw .... merge[df_in_SOPDemandW, df_lcm_FullBOM]')

        #   2.2.2 컬럼명 추가/수정/삭제
        df_lcm_bom_sop_dmdw.rename(columns={
            TO_LOCATION_TO_LOCATION_COLUMN+'_x': TO_LOCATION_TO_LOCATION_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN+'_y': PSI_LOCATION_COLUMN,
            ITEM_METERIAL_COLUMN+'_x': ITEM_METERIAL_COLUMN,
            ITEM_METERIAL_COLUMN+'_y': CONS_ITEM_COLUMN,
            FULL_BOM_CONSUME_QTY_COLUMN: CONSUME_PER_COLUMN,
            BOM_STATUS_BOM_STATUS_COLUMN: BOM_STATUS_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN: PSI_LOCATION_COLUMN,
            ITEM_CONST_TYPE_COLUMN: CONST_TYPE_COLUMN,
        }, inplace=True)
        df_lcm_bom_sop_dmdw[PSI_LOCATION_COLUMN] = df_lcm_bom_sop_dmdw[PSI_LOCATION_COLUMN].str[:4]
        df_lcm_bom_sop_dmdw[CONS_QTY_COLUMN] = df_lcm_bom_sop_dmdw[SOP_DMD_W_LCM_MFG_QTY_COLUMN] * df_lcm_bom_sop_dmdw[CONSUME_PER_COLUMN]
        print_df(df_lcm_bom_sop_dmdw, 'STEP3 by 2.2.2 ____ df_lcm_bom_sop_dmdw .... column rename')


        # 2.3 df_bom_sop_dmdw create
        df_bom_sop_dmdw = pd.concat([df_set_bom_sop_dmdw, df_lcm_bom_sop_dmdw], ignore_index=True)
        print_df(df_bom_sop_dmdw, 'STEP3 by 2.3.1 ____ df_bom_sop_dmdw .... create')


        sum_columns = [
            SOP_DMD_W_LCM_BOH_QTY_COLUMN, SOP_DMD_W_LCM_MFG_QTY_COLUMN, SOP_DMD_W_LCM_SOP_QTY_COLUMN, SOP_DMD_W_SET_BOH_QTY_COLUMN,
            SOP_DMD_W_SET_MFG_QTY_COLUMN, SOP_DMD_W_SET_SOP_QTY_COLUMN, CONS_QTY_COLUMN, CONSUME_PER_COLUMN,
        ]
        for col in sum_columns:
            df_bom_sop_dmdw[col] = df_bom_sop_dmdw[col].fillna(0).astype(int)

        groupby_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, LOCATION_COLUMN,
            TO_TIME_TO_WEEK_COLUMN, DEMAND_ID_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN,
            BOM_INFO_BOM_VERSION_COLUMN, ITEM_COMPONENT_COLUMN, WEEK2_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN,
            PSI_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, CONS_ITEM_COLUMN, STATUS_STATUS_COLUMN, BOM_TYPE_BOM_TYPE_COLUMN,
            BOM_STATUS_COLUMN, CONST_TYPE_COLUMN,
        ]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_bom_sop_dmdw = df_bom_sop_dmdw.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_bom_sop_dmdw, 'STEP3 by 2.3.2 ____ df_bom_sop_dmdw .... groupby')

        # ====================> STEP3 by 2 (End)





        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_bom_sop_dmdw.empty:
            raise CustomException(".... df_bom_sop_dmdw 값이 없습니다.")





        # ====================> STEP3 by 3 (Start) > df_bom_sop_dmdw modify

        # 3.1
        #   3.1.1 df_bom_sop_dmdw, df_in_DmdW merge
        df_bom_sop_dmdw = pd.merge(df_bom_sop_dmdw, df_in_DmdW, how='inner', on=[VERSION_NAME_COLUMN, DEMAND_ID_COLUMN])
        print_df(df_bom_sop_dmdw, 'STEP3 by 3.1.1 ____ df_bom_sop_dmdw .... merge[df_bom_sop_dmdw, df_in_DmdW]')

        #   3.1.2 컬럼명 추가/수정/삭제
        df_bom_sop_dmdw.drop(columns=[
            ITEM_COLUMN+'_y', LOCATION_COLUMN+'_y'
        ], inplace=True)

        df_bom_sop_dmdw.rename(columns={
            ITEM_COLUMN+'_x': ITEM_COLUMN,
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
            TIME_WEEK_COLUMN+'_y': DUE_WEEK_COLUMN,
        }, inplace=True)
        print_df(df_bom_sop_dmdw, 'STEP3 by 3.1.2 ____ df_bom_sop_dmdw .... column rename')

        def duedate_dataframes(df1, df2, t_week, t_day):
            # datetime 형식으로 변환
            df1[TIME_DAY_COLUMN] = pd.to_datetime(df1[TIME_DAY_COLUMN])

            # SUN(일요일)에 해당하는 'day' 값 찾아서 df2['DueDate'] 컬럼에 추가
            sun_days_df = df1[df1[TIME_DAY_WEEK_COLUMN] == 'SUN'][[TIME_WEEK_COLUMN, TIME_DAY_COLUMN]].rename(
                columns={TIME_WEEK_COLUMN: DUE_WEEK_COLUMN, TIME_DAY_COLUMN: 'sun_day'})
            df2 = df2.merge(sun_days_df, on=DUE_WEEK_COLUMN, how='left')
            df2['sun_day'] = pd.to_datetime(df2['sun_day']).dt.strftime('%Y-%m-%d')
            df2.rename(columns={'sun_day': t_day}, inplace=True)
            return df2


        #   3.1.3 DueDate 설정
        df_bom_sop_dmdw = duedate_dataframes(df_in_AllWeek, df_bom_sop_dmdw, DUE_WEEK_COLUMN, DUE_DATE_COLUMN)
        print_df(df_bom_sop_dmdw, 'STEP3 by 3.1.3 ____ df_bom_sop_dmdw .... DueDate Colunms make')

        # ====================> STEP3 by 3 (End)



        # ====================> STEP3 by 4 (Start) > Set BOD & LCM BOD create

        # 4.0 Set date & LCM Date create function
        def calculate_date_info(df1, df2, c_day, t_day, t_week, lt):
            # 날짜 타입으로 변환
            df1[TIME_DAY_COLUMN] = pd.to_datetime(df1[TIME_DAY_COLUMN])
            print_df(df1, 'STEP3 by 4.1.2.2 ____ calculate_date_info > df1 .... select')
            df2[c_day] = pd.to_datetime(df2[c_day])

            # 날짜 계산
            df2['calculated_day'] = df2[c_day] - pd.to_timedelta(df2[lt], unit='d')

            # 매핑하여 t_day 와 t_week 설정
            df2 = df2.merge(df1, left_on='calculated_day', right_on=TIME_DAY_COLUMN, how='left')
            print_df(df2, 'STEP3 by 4.1.2.2 ____ calculate_date_info > df2 .... select 1')

            # 이름 변경
            df2 = df2.rename(columns={
                TIME_DAY_COLUMN: t_day,
                TIME_WEEK_COLUMN+'_x': TIME_WEEK_COLUMN,
                TIME_WEEK_COLUMN+'_y': t_week,
            })

            columns_to_convert = [c_day, t_day]
            for col in columns_to_convert:
                df2[col] = pd.to_datetime(df2[col], errors='coerce').dt.strftime('%Y-%m-%d')

            df2.drop(columns=['calculated_day', TIME_DAY_WEEK_COLUMN], inplace=True)
            print_df(df2, 'STEP3 by 4.1.2.2 ____ calculate_date_info > df2 .... select 3')

            return df2




        # 4.1 Set BOD
        #   4.1.1 df_bom_sop_dmdw, df_in_BODAll merge
        df_bom_sop_dmdw = pd.merge(df_bom_sop_dmdw, df_in_BODAll, how='left',
                                   left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN],
                                   right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, LOCATION_COLUMN, BOD_ALL_SET_TRANS_MODE_COLUMN])
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.1.1 ____ df_bom_sop_dmdw .... merge[df_bom_sop_dmdw, df_in_BODAll]')

        #   4.1.2 컬럼명 추가/수정/삭제
        df_bom_sop_dmdw.drop(columns=[LOCATION_COLUMN+'_y'], inplace=True)
        df_bom_sop_dmdw.rename(columns={
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            BOD_ALL_SET_BOD_LT_COLUMN: SET_LT_COLUMN,
        }, inplace=True)
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.1.2 ____ df_bom_sop_dmdw .... column rename')

        int_columns = [BOD_ALL_BOD_PRTY_COLUMN, SET_LT_COLUMN]
        for col in int_columns:
            df_bom_sop_dmdw[col] = df_bom_sop_dmdw[col].fillna(0)


        #   4.1.3 'SetWeek' & 'SetDate' Colunms make
        df_bom_sop_dmdw = calculate_date_info(df_in_AllWeek, df_bom_sop_dmdw, DUE_DATE_COLUMN, SET_DATE_COLUMN, SET_WEEK_COLUMN, SET_LT_COLUMN)
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.1.3 ____ df_bom_sop_dmdw .... SetWeek_SetDate Colunms make')

        #   4.1.4 복수개의 데이터 있을 경우 BOD All_BOD Prty 작은 것으로 선택
        df_bom_sop_dmdw[TIME_WEEK_COLUMN] = df_bom_sop_dmdw[TIME_WEEK_COLUMN].astype(int)
        groupby_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_DMD_W_SET_MFG_QTY_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            CONS_ITEM_COLUMN, CONSUME_PER_COLUMN, CONS_QTY_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, SOP_DMD_W_LCM_MFG_QTY_COLUMN,
            TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, DEMAND_ID_COLUMN, DUE_WEEK_COLUMN, DUE_DATE_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN,
            WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN, ITEM_METERIAL_COLUMN, BOM_STATUS_COLUMN, CONST_TYPE_COLUMN, PSI_LOCATION_COLUMN,
            SET_LT_COLUMN, SET_DATE_COLUMN, SET_WEEK_COLUMN, BOM_TYPE_BOM_TYPE_COLUMN,
        ]
        df_bom_sop_dmdw = df_bom_sop_dmdw.groupby(groupby_columns, sort=False, as_index=False)[BOD_ALL_BOD_PRTY_COLUMN].min()
        df_bom_sop_dmdw.drop(columns=[BOD_ALL_BOD_PRTY_COLUMN], inplace=True)
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.1.4 ____ df_bom_sop_dmdw .... Set BOD All_BOD Prty min select')



        # 4.2 LCM BOD
        #   4.2.1 df_bom_sop_dmdw, df_in_BODAll merge
        df_bom_sop_dmdw = pd.merge(df_bom_sop_dmdw, df_in_BODAll, how='left',
                                   left_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN,
                                            TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN],
                                   right_on=[VERSION_NAME_COLUMN, ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, LOCATION_COLUMN, BOD_ALL_SET_TRANS_MODE_COLUMN,
                                             BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN, BOD_ALL_LCM_TRANS_MODE_COLUMN])
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.2.1 ____ df_bom_sop_dmdw .... merge[df_bom_sop_dmdw, df_in_BODAll]')

        #   4.2.2 컬럼명 추가/수정/삭제
        df_bom_sop_dmdw.drop(columns=[LOCATION_COLUMN+'_y'], inplace=True)
        df_bom_sop_dmdw.rename(columns={
            LOCATION_COLUMN+'_x': LOCATION_COLUMN,
            BOD_ALL_LCM_BOD_LT_COLUMN: LCM_LT_COLUMN,
        }, inplace=True)
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.2.2 ____ df_bom_sop_dmdw .... column rename')

        int_columns = [BOD_ALL_BOD_PRTY_COLUMN, LCM_LT_COLUMN]
        for col in int_columns:
            df_bom_sop_dmdw[col] = df_bom_sop_dmdw[col].fillna(0)


        #   4.2.3 'LCMWeek' & 'LCMDate' Colunms make
        df_bom_sop_dmdw = calculate_date_info(df_in_AllWeek, df_bom_sop_dmdw, SET_DATE_COLUMN, LCM_DATE_COLUMN, LCM_WEEK_COLUMN, LCM_LT_COLUMN)
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.2.3 ____ df_bom_sop_dmdw .... SetWeek_SetDate Colunms make')

        #   4.2.4 복수개의 데이터 있을 경우 BOD All_BOD Prty 작은 것으로 선택
        df_bom_sop_dmdw[TIME_WEEK_COLUMN] = df_bom_sop_dmdw[TIME_WEEK_COLUMN].astype(int)
        groupby_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, SOP_DMD_W_SET_MFG_QTY_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            CONS_ITEM_COLUMN, CONSUME_PER_COLUMN, CONS_QTY_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, WEEK1_COLUMN, SOP_DMD_W_LCM_MFG_QTY_COLUMN,
            TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, DEMAND_ID_COLUMN, DUE_WEEK_COLUMN, DUE_DATE_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, ITEM_COMPONENT_COLUMN,
            WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN, ITEM_METERIAL_COLUMN, BOM_STATUS_COLUMN, CONST_TYPE_COLUMN, PSI_LOCATION_COLUMN,
            SET_LT_COLUMN, SET_DATE_COLUMN, SET_WEEK_COLUMN, LCM_LT_COLUMN, LCM_DATE_COLUMN, LCM_WEEK_COLUMN, BOM_TYPE_BOM_TYPE_COLUMN,
        ]
        df_bom_sop_dmdw = df_bom_sop_dmdw.groupby(groupby_columns, sort=False, as_index=False)[BOD_ALL_BOD_PRTY_COLUMN].min()
        df_bom_sop_dmdw.drop(columns=[BOD_ALL_BOD_PRTY_COLUMN], inplace=True)
        print_df(df_bom_sop_dmdw, 'STEP3 by 4.2.4 ____ df_bom_sop_dmdw .... LCM BOD All_BOD Prty min select')

        # ====================> STEP3 by 4 (End)




        # ====================> STEP3 by 5 (Start) > 자료 확인 위한 row data create (df_out_MtrlPSIStructure)

        df_out_MtrlPSIStructure = rename_and_delete_df(df_bom_sop_dmdw)
        print_df(df_out_MtrlPSIStructure, 'STEP3 by 5.1.1 ____ df_out_MtrlPSIStructure .... rename and delete')

        df_out_MtrlPSIStructure.rename(columns={
            BOM_TYPE_BOM_TYPE_COLUMN: MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN,
            BOM_STATUS_COLUMN: MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN,
            CONS_ITEM_COLUMN: MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN,
            CONS_QTY_COLUMN: MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN,
            CONST_TYPE_COLUMN: MTRL_PSI_STRUCTURE_CONST_TYPE_COLUMN,
            CONSUME_PER_COLUMN: MTRL_PSI_STRUCTURE_CONSUME_PER_COLUMN,
            DUE_DATE_COLUMN: MTRL_PSI_STRUCTURE_DUE_DATE_COLUMN,
            DUE_WEEK_COLUMN: MTRL_PSI_STRUCTURE_DUE_WEEK_COLUMN,
            LCM_LT_COLUMN: MTRL_PSI_STRUCTURE_LCM_LT_COLUMN,
            SOP_DMD_W_LCM_MFG_QTY_COLUMN: MTRL_PSI_STRUCTURE_LCM_MFG_QTY_COLUMN,
            LCM_DATE_COLUMN: MTRL_PSI_STRUCTURE_LCM_DATE_COLUMN,
            LCM_WEEK_COLUMN: MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN,
            PSI_LOCATION_COLUMN: MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN,
            SET_LT_COLUMN: MTRL_PSI_STRUCTURE_SET_LT_COLUMN,
            SOP_DMD_W_SET_MFG_QTY_COLUMN: MTRL_PSI_STRUCTURE_SET_MFG_QTY_COLUMN,
            SET_DATE_COLUMN: MTRL_PSI_STRUCTURE_SET_DATE_COLUMN,
            SET_WEEK_COLUMN: MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN,
        }, inplace=True)
        print_df(df_out_MtrlPSIStructure, 'STEP3 by 5.1.2 ____ df_out_MtrlPSIStructure .... column rename')

        df_out_MtrlPSIStructure[SEQUENCE_COLUMN] = range(1, len(df_out_MtrlPSIStructure) + 1)
        df_out_MtrlPSIStructure = df_out_MtrlPSIStructure[df_MtrlPSIStructure_columns].reset_index(drop=True)
        df_out_MtrlPSIStructure[VERSION_NAME_COLUMN] = paramOutVersion

        int_columns = [
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN, MTRL_PSI_STRUCTURE_CONSUME_PER_COLUMN, MTRL_PSI_STRUCTURE_LCM_LT_COLUMN,
            MTRL_PSI_STRUCTURE_LCM_MFG_QTY_COLUMN, MTRL_PSI_STRUCTURE_SET_LT_COLUMN, MTRL_PSI_STRUCTURE_SET_MFG_QTY_COLUMN,
        ]
        for column in int_columns:
            df_out_MtrlPSIStructure[column] = df_out_MtrlPSIStructure[column].fillna(0).astype(int)

        df_out_MtrlPSIStructure = df_out_MtrlPSIStructure.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})
        print_df(df_out_MtrlPSIStructure, 'STEP3 by 5.1.3 ____ df_out_MtrlPSIStructure .... create')

        # ====================> STEP3 by 5 (End)

        step('=====> STEP3 End')



        # ################################################################################################################
        # # STEP 4 : output data machining
        # ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # 1 Mtrl PSI Req_Quantity MeasureGrpup 에 들어갈 데이터 구성
        #   1.1
        df_req_quantity_1 = df_out_MtrlPSIStructure[(df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)].copy()
        df_req_quantity_1[CATEGORY_CATEGORY_COLUMN] = SOP_STATUS_VALUE
        groupby_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, LOCATION_COLUMN, ITEM_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN, CATEGORY_CATEGORY_COLUMN,MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN,
        ]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_quantity_1 = df_req_quantity_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_quantity_1, 'STEP4 by 1.1.1 ____ df_req_quantity_1 .... groupby')

        df_req_quantity_1.rename(columns={
            LOCATION_COLUMN: SUB_LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN: ITEM_COMPONENT_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_QUANTITY_COLUMN,
            MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN: BOM_STATUS_BOM_STATUS_COLUMN,
        }, inplace=True)
        print_df(df_req_quantity_1, 'STEP4 by 1.1.2 ____ df_req_quantity_1 .... create')

        #   1.2
        df_req_quantity_2 = df_out_MtrlPSIStructure[(df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)].copy()
        df_req_quantity_2[CATEGORY_CATEGORY_COLUMN] = SOP_STATUS_VALUE
        groupby_columns = [
            VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, LOCATION_COLUMN, ITEM_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN, CATEGORY_CATEGORY_COLUMN,MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN,
        ]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_quantity_2 = df_req_quantity_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_quantity_2, 'STEP4 by 1.2.1 ____ df_req_quantity_2 .... groupby')

        df_req_quantity_2.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            LOCATION_COLUMN: SUB_LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN: ITEM_COMPONENT_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_QUANTITY_COLUMN,
            MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN: BOM_STATUS_BOM_STATUS_COLUMN,
        }, inplace=True)
        print_df(df_req_quantity_2, 'STEP4 by 1.2.2 ____ df_req_quantity_2 .... create')

        #   1.3
        df_req_quantity_3 = df_out_MtrlPSIStructure[(df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)].copy()
        df_req_quantity_3[CATEGORY_CATEGORY_COLUMN] = DP_SOP_VALUE
        groupby_columns = [
            VERSION_NAME_COLUMN, MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, LOCATION_COLUMN, ITEM_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN, CATEGORY_CATEGORY_COLUMN,MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN,
        ]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_quantity_3 = df_req_quantity_3.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_quantity_3, 'STEP4 by 1.3.1 ____ df_req_quantity_3 .... groupby')

        df_req_quantity_3.rename(columns={
            MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN: TIME_WEEK_COLUMN,
            LOCATION_COLUMN: SUB_LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN: ITEM_COMPONENT_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_QUANTITY_COLUMN,
            MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN: BOM_STATUS_BOM_STATUS_COLUMN,
        }, inplace=True)
        print_df(df_req_quantity_3, 'STEP4 by 1.3.2 ____ df_req_quantity_3 .... create')

        #   1.4
        df_req_quantity_4 = df_out_MtrlPSIStructure[(df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)].copy()
        df_req_quantity_4[CATEGORY_CATEGORY_COLUMN] = DP_SOP_VALUE
        groupby_columns = [
            VERSION_NAME_COLUMN, MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, LOCATION_COLUMN, ITEM_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN, CATEGORY_CATEGORY_COLUMN,MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN,
        ]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_quantity_4 = df_req_quantity_4.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_quantity_4, 'STEP4 by 1.4.1 ____ df_req_quantity_4 .... groupby')

        df_req_quantity_4.rename(columns={
            MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN: TIME_WEEK_COLUMN,
            LOCATION_COLUMN: SUB_LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN: ITEM_COMPONENT_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_QUANTITY_COLUMN,
            MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN: BOM_STATUS_BOM_STATUS_COLUMN,
        }, inplace=True)
        print_df(df_req_quantity_4, 'STEP4 by 1.4.2 ____ df_req_quantity_4 .... create')

        #   1.5 dataframe concat
        df_out_ReqQuantity = pd.concat([df_req_quantity_1, df_req_quantity_2, df_req_quantity_3, df_req_quantity_4], ignore_index=True)
        print_df(df_out_ReqQuantity, 'STEP4 by 1.5.1 ____ df_out_ReqQuantity .... dataframe concat')

        int_columns = [MTRL_PSI_REQ_QUANTITY_COLUMN]
        for col in int_columns:
            df_out_ReqQuantity[col] = df_out_ReqQuantity[col].fillna(0).astype(int)

        str_columns = [LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN]
        for col in str_columns:
            df_out_ReqQuantity[col] = df_out_ReqQuantity[col].fillna('-').astype(str)

        groupby_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN, ITEM_COMPONENT_COLUMN,
            ITEM_METERIAL_COLUMN, CATEGORY_CATEGORY_COLUMN, BOM_STATUS_BOM_STATUS_COLUMN,
        ]
        sum_columns = (int_columns)
        agg_dict = {col: 'sum' for col in sum_columns}
        df_out_ReqQuantity = df_out_ReqQuantity.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)

        df_out_ReqQuantity = df_out_ReqQuantity[df_ReqQuantity_columns]
        print_df(df_out_ReqQuantity, 'STEP4 by 1.5.2 ____ df_out_ReqQuantity .... groupby')






        # 2 'Mtrl PSI Structure_BOM_Status' and 'Mtrl PSI Structure_BOM Type' 값에 따른 데이터 copy
        #   2.1 Req. (Demand)
        #       2.1.1 Mtrl PSI_REQ_Demand Fixed
        df_req_denamd_fixed_1 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == FIXED_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_denamd_fixed_2 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == FIXED_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()

        #       2.1.2 Mtrl PSI_REQ_Demand Unfixed
        df_req_denamd_unfixed_1 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] != FIXED_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_denamd_unfixed_2 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] != FIXED_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()


        #   2.2 Req. (SOP/Status)
        #       2.2.1 Mtrl PSI_REQ_Status Fixed
        df_req_sop_stat_fixed_1 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == FIXED_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_sop_stat_fixed_2 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == FIXED_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()

        #       2.2.2 Mtrl PSI_REQ_Status HQ
        df_req_sop_stat_hq_1 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == HQ_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_sop_stat_hq_2 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == HQ_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()

        #       2.2.3 Mtrl PSI_REQ_Status NSCM
        df_req_sop_stat_nscm_1 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN].str.contains(NSCM_VALUE, na=False)) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_sop_stat_nscm_2 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN].str.contains(NSCM_VALUE, na=False)) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()

        #       2.2.4 Mtrl PSI_REQ_Status Dash_New
        df_req_sop_stat_dash_new_1 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == DASH_NEW_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_sop_stat_dash_new_2 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == DASH_NEW_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()

        #       2.2.5 Mtrl PSI_REQ_Status Dash_Dual
        df_req_sop_stat_dash_dual_1 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == DASH_DUAL_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_sop_stat_dash_dual_2 = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN] == DASH_DUAL_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()

        #       2.2.6 Mtrl PSI_REQ_Status EC
        df_req_sop_stat_ec_1 = df_out_MtrlPSIStructure[
            (~df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN].isin([FIXED_VALUE, HQ_VALUE, DASH_NEW_VALUE, DASH_DUAL_VALUE])) &
            (~df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN].str.contains(NSCM_VALUE, na=False)) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)
        ].copy()
        df_req_sop_stat_ec_2 = df_out_MtrlPSIStructure[
            (~df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN].isin([FIXED_VALUE, HQ_VALUE, DASH_NEW_VALUE, DASH_DUAL_VALUE])) &
            (~df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_STATUS_COLUMN].str.contains(NSCM_VALUE, na=False)) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)
        ].copy()


        #   2.3 Req. (SOP/Type)
        #       2.3.1 Mtrl PSI_REQ_Type SET
        df_req_type_set = df_out_MtrlPSIStructure[(df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SET_VALUE)].copy()

        #       2.3.2 Mtrl PSI_REQ_Type SOP Assy
        df_req_type_sop_assy = df_out_MtrlPSIStructure[(df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE)].copy()


        #   2.4 Req. (SOP/Export)
        #       2.4.1 Mtrl PSI_REQ_SOP Export
        df_req_sop_export = df_out_MtrlPSIStructure[
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_BOM_TYPE_COLUMN] == SOP_ASSY_VALUE) &
            (df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN].str[:4] != df_out_MtrlPSIStructure[LOCATION_COLUMN])
        ].copy()




        # 3 Req. (Demand) ================================================================
        #   3.1 Mtrl PSI_REQ_Demand Fixed
        #       3.1.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_denamd_fixed_1 = df_req_denamd_fixed_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_denamd_fixed_1, 'STEP4 by 3.1.1 ____ df_req_denamd_fixed_1 .... groupby')

        df_req_denamd_fixed_1.rename(columns={
            MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_DEMAND_FIXED_COLUMN,
        }, inplace=True)
        df_req_denamd_fixed_1[SUB_LOCATION_COLUMN] = '-'
        df_req_denamd_fixed_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_denamd_fixed_1, 'STEP4 by 3.1.1 ____ df_req_denamd_fixed_1 .... create')

        #       3.1.2 LCM
        groupby_columns = [VERSION_NAME_COLUMN, MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_denamd_fixed_2 = df_req_denamd_fixed_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_denamd_fixed_2, 'STEP4 by 3.1.2 ____ df_req_denamd_fixed_2 .... groupby')

        df_req_denamd_fixed_2.rename(columns={
            MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_DEMAND_FIXED_COLUMN,
        }, inplace=True)
        df_req_denamd_fixed_2[SUB_LOCATION_COLUMN] = '-'
        df_req_denamd_fixed_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_denamd_fixed_2, 'STEP4 by 3.1.2 ____ df_req_denamd_fixed_2 .... create')

        #       3.1.3 dataframe concat
        df_req_denamd_fixed = pd.concat([df_req_denamd_fixed_1, df_req_denamd_fixed_2], ignore_index=True)
        print_df(df_req_denamd_fixed, 'STEP4 by 3.1.3 ____ df_req_denamd_fixed .... final')

        #       3.1.4 groupby
        df_req_denamd_fixed = df_req_denamd_fixed[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_DEMAND_FIXED_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_DEMAND_FIXED_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_denamd_fixed = df_req_denamd_fixed.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_denamd_fixed, 'STEP4 by 3.1.4 ____ df_req_denamd_fixed .... groupby')



        #   3.2 Mtrl PSI_REQ_Demand Unfixed
        #       3.2.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_denamd_unfixed_1 = df_req_denamd_unfixed_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_denamd_unfixed_1, 'STEP4 by 3.2.1 ____ df_req_denamd_unfixed_1 .... groupby')

        df_req_denamd_unfixed_1.rename(columns={
            MTRL_PSI_STRUCTURE_SET_WEEK_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN,
        }, inplace=True)
        df_req_denamd_unfixed_1[SUB_LOCATION_COLUMN] = '-'
        df_req_denamd_unfixed_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_denamd_unfixed_1, 'STEP4 by 3.2.1 ____ df_req_denamd_unfixed_1 .... create')

        #       3.2.2 LCM
        groupby_columns = [VERSION_NAME_COLUMN, MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_denamd_unfixed_2 = df_req_denamd_unfixed_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_denamd_unfixed_2, 'STEP4 by 3.2.2 ____ df_req_denamd_unfixed_2 .... groupby')

        df_req_denamd_unfixed_2.rename(columns={
            MTRL_PSI_STRUCTURE_LCM_WEEK_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN,
        }, inplace=True)
        df_req_denamd_unfixed_2[SUB_LOCATION_COLUMN] = '-'
        df_req_denamd_unfixed_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_denamd_unfixed_2, 'STEP4 by 3.2.2 ____ df_req_denamd_unfixed_2 .... create')

        #       3.2.3 dataframe concat
        df_req_denamd_unfixed = pd.concat([df_req_denamd_unfixed_1, df_req_denamd_unfixed_2], ignore_index=True)
        print_df(df_req_denamd_unfixed, 'STEP4 by 3.2.3 ____ df_req_denamd_unfixed .... final')

        #       3.2.4 groupby
        df_req_denamd_unfixed = df_req_denamd_unfixed[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_denamd_unfixed = df_req_denamd_unfixed.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_denamd_unfixed, 'STEP4 by 3.2.4 ____ df_req_denamd_unfixed .... groupby')



        # 4 Req. (SOP/Status) ================================================================
        #   4.1 Mtrl PSI_REQ_Status Fixed
        #       4.1.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_fixed_1 = df_req_sop_stat_fixed_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_fixed_1, 'STEP4 by 4.1.1 ____ df_req_sop_stat_fixed_1 .... groupby')

        df_req_sop_stat_fixed_1.rename(columns={
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_FIXED_COLUMN,
        }, inplace=True)
        df_req_sop_stat_fixed_1[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_fixed_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_fixed_1, 'STEP4 by 4.1.1 ____ df_req_sop_stat_fixed_1 .... create')

        #       4.1.2 LCM
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_fixed_2 = df_req_sop_stat_fixed_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_fixed_2, 'STEP4 by 4.1.2 ____ df_req_sop_stat_fixed_2 .... groupby')

        df_req_sop_stat_fixed_2.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_FIXED_COLUMN,
        }, inplace=True)
        df_req_sop_stat_fixed_2[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_fixed_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_fixed_2, 'STEP4 by 4.1.2 ____ df_req_sop_stat_fixed_2 .... create')

        #       4.1.3 dataframe concat
        df_req_sop_stat_fixed = pd.concat([df_req_sop_stat_fixed_1, df_req_sop_stat_fixed_2], ignore_index=True)
        print_df(df_req_sop_stat_fixed, 'STEP4 by 4.1.3 ____ df_req_sop_stat_fixed .... final')

        #       4.1.4 groupby
        df_req_sop_stat_fixed = df_req_sop_stat_fixed[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_STATUS_FIXED_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_STATUS_FIXED_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_fixed = df_req_sop_stat_fixed.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_fixed, 'STEP4 by 4.1.4 ____ df_req_sop_stat_fixed .... groupby')



        #   4.2 Mtrl PSI_REQ_Status HQ
        #       4.2.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_hq_1 = df_req_sop_stat_hq_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_hq_1, 'STEP4 by 4.2.1 ____ df_req_sop_stat_hq_1 .... groupby')

        df_req_sop_stat_hq_1.rename(columns={
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_HQ_COLUMN,
        }, inplace=True)
        df_req_sop_stat_hq_1[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_hq_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_hq_1, 'STEP4 by 4.2.1 ____ df_req_sop_stat_hq_1 .... create')

        #       4.2.2 LCM
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_hq_2 = df_req_sop_stat_hq_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_hq_2, 'STEP4 by 4.2.2 ____ df_req_sop_stat_hq_2 .... groupby')

        df_req_sop_stat_hq_2.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_HQ_COLUMN,
        }, inplace=True)
        df_req_sop_stat_hq_2[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_hq_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_hq_2, 'STEP4 by 4.2.2 ____ df_req_sop_stat_hq_2 .... create')

        #       4.2.3 dataframe concat
        df_req_sop_stat_hq = pd.concat([df_req_sop_stat_hq_1, df_req_sop_stat_hq_2], ignore_index=True)
        print_df(df_req_sop_stat_hq, 'STEP4 by 4.2.3 ____ df_req_sop_stat_hq .... final')

        #       4.2.4 groupby
        df_req_sop_stat_hq = df_req_sop_stat_hq[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_STATUS_HQ_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_STATUS_HQ_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_hq = df_req_sop_stat_hq.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_hq, 'STEP4 by 4.2.4 ____ df_req_sop_stat_hq .... groupby')



        #   4.3 Mtrl PSI_REQ_Status NSCM
        #       4.3.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_nscm_1 = df_req_sop_stat_nscm_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_nscm_1, 'STEP4 by 4.3.1 ____ df_req_sop_stat_nscm_1 .... groupby')

        df_req_sop_stat_nscm_1.rename(columns={
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_NSCM_COLUMN,
        }, inplace=True)
        df_req_sop_stat_nscm_1[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_nscm_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_nscm_1, 'STEP4 by 4.3.1 ____ df_req_sop_stat_nscm_1 .... create')

        #       4.3.2 LCM
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_nscm_2 = df_req_sop_stat_nscm_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_nscm_2, 'STEP4 by 4.3.2 ____ df_req_sop_stat_nscm_2 .... groupby')

        df_req_sop_stat_nscm_2.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_NSCM_COLUMN,
        }, inplace=True)
        df_req_sop_stat_nscm_2[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_nscm_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_nscm_2, 'STEP4 by 4.3.2 ____ df_req_sop_stat_nscm_2 .... create')

        #       4.3.3 dataframe concat
        df_req_sop_stat_nscm = pd.concat([df_req_sop_stat_nscm_1, df_req_sop_stat_nscm_2], ignore_index=True)
        print_df(df_req_sop_stat_nscm, 'STEP4 by 4.3.3 ____ df_req_sop_stat_nscm .... final')

        #       4.3.4 groupby
        df_req_sop_stat_nscm = df_req_sop_stat_nscm[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_STATUS_NSCM_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_STATUS_NSCM_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_nscm = df_req_sop_stat_nscm.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_nscm, 'STEP4 by 4.3.4 ____ df_req_sop_stat_nscm .... groupby')



        #   4.4 Mtrl PSI_REQ_Status Dash_New
        #       4.4.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_dash_new_1 = df_req_sop_stat_dash_new_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_dash_new_1, 'STEP4 by 4.4.1 ____ df_req_sop_stat_dash_new_1 .... groupby')

        df_req_sop_stat_dash_new_1.rename(columns={
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN,
        }, inplace=True)
        df_req_sop_stat_dash_new_1[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_dash_new_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_dash_new_1, 'STEP4 by 4.4.1 ____ df_req_sop_stat_dash_new_1 .... create')

        #       4.4.2 LCM
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_dash_new_2 = df_req_sop_stat_dash_new_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_dash_new_2, 'STEP4 by 4.4.2 ____ df_req_sop_stat_dash_new_2 .... groupby')

        df_req_sop_stat_dash_new_2.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN,
        }, inplace=True)
        df_req_sop_stat_dash_new_2[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_dash_new_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_dash_new_2, 'STEP4 by 4.4.2 ____ df_req_sop_stat_dash_new_2 .... create')

        #       4.4.3 dataframe concat
        df_req_sop_stat_dash_new = pd.concat([df_req_sop_stat_dash_new_1, df_req_sop_stat_dash_new_2], ignore_index=True)
        print_df(df_req_sop_stat_dash_new, 'STEP4 by 4.4.3 ____ df_req_sop_stat_dash_new .... final')

        #       4.4.4 groupby
        df_req_sop_stat_dash_new = df_req_sop_stat_dash_new[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_dash_new = df_req_sop_stat_dash_new.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_dash_new, 'STEP4 by 4.4.4 ____ df_req_sop_stat_dash_new .... groupby')



        #   4.5 Mtrl PSI_REQ_Status Dash_Dual
        #       4.5.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_dash_dual_1 = df_req_sop_stat_dash_dual_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_dash_dual_1, 'STEP4 by 4.5.1 ____ df_req_sop_stat_dash_dual_1 .... groupby')

        df_req_sop_stat_dash_dual_1.rename(columns={
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN,
        }, inplace=True)
        df_req_sop_stat_dash_dual_1[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_dash_dual_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_dash_dual_1, 'STEP4 by 4.5.1 ____ df_req_sop_stat_dash_dual_1 .... create')

        #       4.5.2 LCM
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_dash_dual_2 = df_req_sop_stat_dash_dual_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_dash_dual_2, 'STEP4 by 4.5.2 ____ df_req_sop_stat_dash_dual_2 .... groupby')

        df_req_sop_stat_dash_dual_2.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN,
        }, inplace=True)
        df_req_sop_stat_dash_dual_2[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_dash_dual_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_dash_dual_2, 'STEP4 by 4.5.2 ____ df_req_sop_stat_dash_dual_2 .... create')

        #       4.5.3 dataframe concat
        df_req_sop_stat_dash_dual = pd.concat([df_req_sop_stat_dash_dual_1, df_req_sop_stat_dash_dual_2], ignore_index=True)
        print_df(df_req_sop_stat_dash_dual, 'STEP4 by 4.5.3 ____ df_req_sop_stat_dash_dual .... final')

        #       4.5.4 groupby
        df_req_sop_stat_dash_dual = df_req_sop_stat_dash_dual[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_dash_dual = df_req_sop_stat_dash_dual.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_dash_dual, 'STEP4 by 4.5.4 ____ df_req_sop_stat_dash_dual .... groupby')



        #   4.6 Mtrl PSI_REQ_Status EC
        #       4.6.1 Set
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_ec_1 = df_req_sop_stat_ec_1.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_ec_1, 'STEP4 by 4.6.1 ____ df_req_sop_stat_ec_1 .... groupby')

        df_req_sop_stat_ec_1.rename(columns={
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_EC_COLUMN,
        }, inplace=True)
        df_req_sop_stat_ec_1[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_ec_1[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_ec_1, 'STEP4 by 4.6.1 ____ df_req_sop_stat_ec_1 .... create')

        #       4.6.1 LCM
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_ec_2 = df_req_sop_stat_ec_2.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_ec_2, 'STEP4 by 4.6.2 ____ df_req_sop_stat_ec_2 .... groupby')

        df_req_sop_stat_ec_2.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_STATUS_EC_COLUMN,
        }, inplace=True)
        df_req_sop_stat_ec_2[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_stat_ec_2[TRANS_MODE_COLUMN] = '-'
        print_df(df_req_sop_stat_ec_2, 'STEP4 by 4.6.2 ____ df_req_sop_stat_ec_2 .... create')

        #       4.6.3 dataframe concat
        df_req_sop_stat_ec = pd.concat([df_req_sop_stat_ec_1, df_req_sop_stat_ec_2], ignore_index=True)
        print_df(df_req_sop_stat_ec, 'STEP4 by 4.6.3 ____ df_req_sop_stat_ec .... final')

        #       4.6.4 groupby
        df_req_sop_stat_ec = df_req_sop_stat_ec[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_STATUS_EC_COLUMN
        ]]
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_STATUS_EC_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_stat_ec = df_req_sop_stat_ec.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_stat_ec, 'STEP4 by 4.6.4 ____ df_req_sop_stat_ec .... groupby')



        # 5 Req. (SOP/Type) ================================================================
        #   5.1 Mtrl PSI_REQ_Type SET
        #       5.1.1
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_type_set = df_req_type_set.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_type_set, 'STEP4 by 5.1.1 ____ df_req_type_set .... groupby')

        df_req_type_set.rename(columns={
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_TYPE_SET_COLUMN,
        }, inplace=True)
        df_req_type_set[SUB_LOCATION_COLUMN] = '-'
        df_req_type_set[TRANS_MODE_COLUMN] = '-'

        df_req_type_set = df_req_type_set[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_TYPE_SET_COLUMN
        ]]

        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_TYPE_SET_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_type_set = df_req_type_set.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_type_set, 'STEP4 by 5.1.1 ____ df_req_type_set .... create')

        #   5.2 Mtrl PSI_REQ_Type SOP Assy
        #       5.2.1
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_type_sop_assy = df_req_type_sop_assy.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_type_sop_assy, 'STEP4 by 5.2.1 ____ df_req_type_sop_assy .... groupby')

        df_req_type_sop_assy.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN,
        }, inplace=True)
        df_req_type_sop_assy[SUB_LOCATION_COLUMN] = '-'
        df_req_type_sop_assy[TRANS_MODE_COLUMN] = '-'

        df_req_type_sop_assy = df_req_type_sop_assy[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN
        ]]

        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_type_sop_assy = df_req_type_sop_assy.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_type_sop_assy, 'STEP4 by 5.2.1 ____ df_req_type_sop_assy .... create')



        # 6 Req. (SOP/Export) ================================================================
        #   6.1 Mtrl PSI_REQ_SOP Export
        #       6.1.1
        groupby_columns = [VERSION_NAME_COLUMN, WEEK1_COLUMN, MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN, MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN]
        sum_columns = [MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_export = df_req_sop_export.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_export, 'STEP4 by 6.1.1 ____ df_req_sop_export .... groupby')

        df_req_sop_export.rename(columns={
            WEEK1_COLUMN: TIME_WEEK_COLUMN,
            MTRL_PSI_STRUCTURE_PSI_LOCATION_COLUMN: LOCATION_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            MTRL_PSI_STRUCTURE_CONS_QTY_COLUMN: MTRL_PSI_REQ_SOP_EXPORT_COLUMN,
        }, inplace=True)
        df_req_sop_export[SUB_LOCATION_COLUMN] = '-'
        df_req_sop_export[TRANS_MODE_COLUMN] = '-'

        df_req_sop_export = df_req_sop_export[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_REQ_SOP_EXPORT_COLUMN
        ]]

        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_REQ_SOP_EXPORT_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_req_sop_export = df_req_sop_export.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_req_sop_export, 'STEP4 by 6.1.1 ____ df_req_sop_export .... create')



        # 7 df_in_Inventory modify ================================================================
        #   7.1 BOH create
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_COLUMN]
        sum_columns = [INV_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_Inventory = df_in_Inventory.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_inventory = rename_and_delete_df(df_in_Inventory)
        print_df(df_inventory, 'STEP4 by 7.1 ____ df_inventory .... groupby')

        #   7.2 컬럼 설정
        df_inventory.rename(columns={ITEM_COLUMN: ITEM_METERIAL_COLUMN}, inplace=True)
        df_inventory[SUB_LOCATION_COLUMN] = '-'
        df_inventory[TRANS_MODE_COLUMN] = '-'
        df_inventory.loc[df_inventory[TIME_WEEK_COLUMN] == current_week, [
            MTRL_PSI_BOH_DEMAND_COLUMN, MTRL_PSI_BOH_DEMAND_FIXED_COLUMN, MTRL_PSI_BOH_SOP_COLUMN,
            MTRL_PSI_BOH_SOP_FIXED_COLUMN, MTRL_PSI_BOH_SOP_EXPORT_COLUMN
        ]] = df_inventory[INV_QTY_COLUMN]

        df_inventory = df_inventory[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_BOH_DEMAND_COLUMN, MTRL_PSI_BOH_DEMAND_FIXED_COLUMN, MTRL_PSI_BOH_SOP_COLUMN,
            MTRL_PSI_BOH_SOP_FIXED_COLUMN, MTRL_PSI_BOH_SOP_EXPORT_COLUMN
        ]]

        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_BOH_DEMAND_COLUMN, MTRL_PSI_BOH_DEMAND_FIXED_COLUMN, MTRL_PSI_BOH_SOP_COLUMN,MTRL_PSI_BOH_SOP_FIXED_COLUMN, MTRL_PSI_BOH_SOP_EXPORT_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_inventory = df_inventory.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_inventory, 'STEP4 by 7.2 ____ df_inventory .... final')



        # 7-2 df_in_DistributionOrder modify ================================================================
        #   7-2.1 Arrival create
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [DIST_ORDER_SS_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_DistributionOrder = df_in_DistributionOrder.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_distributionOrder = rename_and_delete_df(df_in_DistributionOrder)
        print_df(df_distributionOrder, 'STEP4 by 7-2.1 ____ df_distributionOrder .... groupby')

        df_distributionOrder.rename(columns={ITEM_COLUMN: ITEM_METERIAL_COLUMN}, inplace=True)
        df_distributionOrder[MTRL_PSI_ARRIVAL_SN_COLUMN] = df_distributionOrder[DIST_ORDER_SS_QTY_COLUMN]
        df_distributionOrder[MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN] = df_distributionOrder[DIST_ORDER_SS_QTY_COLUMN]
        df_distributionOrder[MTRL_PSI_ARRIVAL_RTP_COLUMN] = df_distributionOrder[DIST_ORDER_SS_QTY_COLUMN]
        df_distributionOrder[MTRL_PSI_ARRIVAL_RTF_COLUMN] = df_distributionOrder[DIST_ORDER_SS_QTY_COLUMN]
        df_distributionOrder[MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN] = df_distributionOrder[DIST_ORDER_SS_QTY_COLUMN]
        df_distributionOrder[MTRL_PSI_ARRIVAL_CMI_COLUMN] = df_distributionOrder[DIST_ORDER_SS_QTY_COLUMN]
        df_distributionOrder[MTRL_PSI_ARRIVAL_EXCEL_COLUMN] = df_distributionOrder[DIST_ORDER_SS_QTY_COLUMN]

        df_distributionOrder = df_distributionOrder[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_ARRIVAL_SN_COLUMN, MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN, MTRL_PSI_ARRIVAL_RTP_COLUMN, MTRL_PSI_ARRIVAL_RTF_COLUMN,
            MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN, MTRL_PSI_ARRIVAL_CMI_COLUMN, MTRL_PSI_ARRIVAL_EXCEL_COLUMN
        ]]

        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [
            MTRL_PSI_ARRIVAL_SN_COLUMN, MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN, MTRL_PSI_ARRIVAL_RTP_COLUMN, MTRL_PSI_ARRIVAL_RTF_COLUMN,
            MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN, MTRL_PSI_ARRIVAL_CMI_COLUMN, MTRL_PSI_ARRIVAL_EXCEL_COLUMN,
        ]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_distributionOrder = df_distributionOrder.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_distributionOrder, 'STEP4 by 7-2.2 ____ df_distributionOrder .... final')



        # 7-3 df_in_MtrlProdPlan modify ================================================================
        #   7-3.1 Arrival create
        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, ACTIVITY1_FROM_LOCATIONCOLUMN, ACTIVITY2_COLUMN]
        sum_columns = [W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_in_MtrlProdPlan = df_in_MtrlProdPlan.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        df_MtrlProdPlan = rename_and_delete_df(df_in_MtrlProdPlan)
        print_df(df_MtrlProdPlan, 'STEP4 by 7-3.1 ____ df_MtrlProdPlan .... groupby')

        df_MtrlProdPlan.rename(columns={
            ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            ACTIVITY1_FROM_LOCATIONCOLUMN: SUB_LOCATION_COLUMN,
            ACTIVITY2_COLUMN: TRANS_MODE_COLUMN,
        }, inplace=True)
        df_MtrlProdPlan[MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN] = df_MtrlProdPlan[W_METERIAL_PRODUCTION_QUANTITY_PLAN_OUTPUT_COLUMN]

        df_MtrlProdPlan = df_MtrlProdPlan[[
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN
        ]]

        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = [MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_MtrlProdPlan = df_MtrlProdPlan.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_MtrlProdPlan, 'STEP4 by 7-3.2 ____ df_MtrlProdPlan .... final')


        # 8 df_MtrlPSI create ================================================================
        #   8.1 각 데이터프레임 합치기
        df_MtrlPSI = pd.concat([
            df_req_denamd_fixed, df_req_denamd_unfixed,
            df_req_sop_stat_fixed, df_req_sop_stat_hq, df_req_sop_stat_nscm, df_req_sop_stat_dash_new, df_req_sop_stat_dash_dual,
            df_req_sop_stat_ec, df_req_type_set, df_req_type_sop_assy, df_req_sop_export,
            df_inventory, df_distributionOrder, df_MtrlProdPlan
        ], ignore_index=True)
        df_MtrlPSI[TIME_WEEK_COLUMN] = df_MtrlPSI[TIME_WEEK_COLUMN].astype(int)
        df_MtrlPSI[MTRL_PSI_REQ_SOP_STATUS_COLUMN] = 0
        df_MtrlPSI[MTRL_PSI_REQ_SOP_TYPE_COLUMN] = 0

        print_df(df_MtrlPSI, 'STEP4 by 8.1.1 ____ df_MtrlPSI .... df concat')



        # ------------------ 테스트 디버깅용 ------------------ start
        # df_out_MtrlPSIStructure = df_out_MtrlPSIStructure[df_out_MtrlPSIStructure[MTRL_PSI_STRUCTURE_CONS_ITEM_COLUMN] == 'BN96-58278A']
        # df_MtrlPSI = df_MtrlPSI[(df_MtrlPSI[ITEM_METERIAL_COLUMN] == 'BN96-52526L')]
        # save_csv_file(df_MtrlPSI, 'STEP4 by 8.1 ____ df_MtrlPSI .... copy')
        # ------------------ 테스트 디버깅용 ------------------ end



        #   8.2 groupby
        int_columns = int_base_columns + int_boh_columns
        for col in int_columns:
            df_MtrlPSI[col] = df_MtrlPSI[col].fillna(0).astype(int)

        str_columns = [SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        for col in str_columns:
            df_MtrlPSI[col] = df_MtrlPSI[col].fillna('-').astype(str)

        groupby_columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        sum_columns = (int_columns)
        agg_dict = {col: 'sum' for col in sum_columns}
        df_MtrlPSI = df_MtrlPSI.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        # df_MtrlPSI.reset_index(drop=True, inplace=True)
        print_df(df_MtrlPSI, 'STEP4 by 8.2.1 ____ df_MtrlPSI .... groupby after')



        #   8.3 나머지 컬럼 설정
        df_MtrlPSI[MTRL_PSI_REQ_SOP_STATUS_COLUMN] = (
                df_MtrlPSI[MTRL_PSI_REQ_STATUS_FIXED_COLUMN] + df_MtrlPSI[MTRL_PSI_REQ_STATUS_HQ_COLUMN] +
                df_MtrlPSI[MTRL_PSI_REQ_STATUS_NSCM_COLUMN] + df_MtrlPSI[MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN] +
                df_MtrlPSI[MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN] + df_MtrlPSI[MTRL_PSI_REQ_STATUS_EC_COLUMN]
        )
        df_MtrlPSI[MTRL_PSI_REQ_SOP_TYPE_COLUMN] = (df_MtrlPSI[MTRL_PSI_REQ_TYPE_SET_COLUMN] + df_MtrlPSI[MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN])

        df_MtrlPSI[MTRL_PSI_EOH_DEMAND_COLUMN] = 0
        df_MtrlPSI[MTRL_PSI_EOH_DEMAND_FIXED_COLUMN] = 0
        df_MtrlPSI[MTRL_PSI_EOH_SOP_COLUMN] = 0
        df_MtrlPSI[MTRL_PSI_EOH_SOP_FIXED_COLUMN] = 0
        df_MtrlPSI[MTRL_PSI_EOH_SOP_EXPORT_COLUMN] = 0
        df_MtrlPSI = df_MtrlPSI[df_MtrlPSI_columns]
        print_df(df_MtrlPSI, 'STEP4 by 8.3.1 ____ df_MtrlPSI .... colunms add and modify')



        #   8.4 빈 주차 채워넣기
        columns = [VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN]
        df_in_MDMHorizon[TIME_WEEK_COLUMN] = df_in_MDMHorizon[TIME_WEEK_COLUMN].astype(int)
        df_missing_rows = set_unique_combinations(df_MtrlPSI, df_in_MDMHorizon, columns)
        df_MtrlPSI = pd.concat([df_MtrlPSI, df_missing_rows], ignore_index=True).drop_duplicates()
        print_df(df_MtrlPSI, 'STEP4 by 8.4.1 ____ df_MtrlPSI .... week add')

        int_columns = int_base_columns + int_boh_columns + int_eoh_columns
        for col in int_columns:
            df_MtrlPSI[col] = df_MtrlPSI[col].fillna(0).astype(int)

        str_columns = [SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]
        for col in str_columns:
            df_MtrlPSI[col] = df_MtrlPSI[col].fillna('-').astype(str)



        # 9 EOH 및 BOH 설정 ================================================================
        #   9.1 eoh / boh 계산 수행
        #       첫번째 주차 EOH = BOH + Arrival - GI
        #         -> 첫번째 주차의 EOH 는 차주의 BOH로 설정

        #   NumPy group 백터연산
        def compute_group_numpy(group):
            # 주차별 정렬
            group = group.sort_values(by=TIME_WEEK_COLUMN).reset_index(drop=True)

            # NumPy 배열로 계산
            boh_demand = group[MTRL_PSI_BOH_DEMAND_COLUMN].to_numpy()
            boh_demand_fix = group[MTRL_PSI_BOH_DEMAND_FIXED_COLUMN].to_numpy()
            boh_sop = group[MTRL_PSI_BOH_SOP_COLUMN].to_numpy()
            boh_sop_fix = group[MTRL_PSI_BOH_SOP_FIXED_COLUMN].to_numpy()
            boh_sop_export = group[MTRL_PSI_BOH_SOP_EXPORT_COLUMN].to_numpy()

            arrival = group[MTRL_PSI_ARRIVAL_SN_COLUMN].to_numpy()

            gi_demand = (group[MTRL_PSI_REQ_DEMAND_FIXED_COLUMN] - group[MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN]).to_numpy()
            gi_demand_fix = group[MTRL_PSI_REQ_DEMAND_FIXED_COLUMN].to_numpy()
            gi_sop = group[MTRL_PSI_REQ_SOP_STATUS_COLUMN].to_numpy()
            gi_sop_fix = group[MTRL_PSI_REQ_STATUS_FIXED_COLUMN].to_numpy()
            gi_sop_export = (group[MTRL_PSI_REQ_SOP_EXPORT_COLUMN] - group[MTRL_PSI_REQ_SOP_STATUS_COLUMN]).to_numpy()

            eoh_demand = np.zeros_like(boh_demand)
            eoh_demand_fix = np.zeros_like(boh_demand_fix)
            eoh_sop = np.zeros_like(boh_sop)
            eoh_sop_fix = np.zeros_like(boh_sop_fix)
            eoh_sop_export = np.zeros_like(boh_sop_export)

            # 첫 번째 값
            eoh_demand[0] = boh_demand[0] + arrival[0] - gi_demand[0]
            eoh_demand_fix[0] = boh_demand_fix[0] + arrival[0] - gi_demand_fix[0]
            eoh_sop[0] = boh_sop[0] + arrival[0] - gi_sop[0]
            eoh_sop_fix[0] = boh_sop_fix[0] + arrival[0] - gi_sop_fix[0]
            eoh_sop_export[0] = boh_sop_export[0] + arrival[0] - gi_sop_export[0]

            # 이후 값 계산
            for i in range(1, len(boh_demand)):
                boh_demand[i] = eoh_demand[i - 1]
                boh_demand_fix[i] = eoh_demand_fix[i - 1]
                boh_sop[i] = eoh_sop[i - 1]
                boh_sop_fix[i] = eoh_sop_fix[i - 1]
                boh_sop_export[i] = eoh_sop_export[i - 1]

                eoh_demand[i] = boh_demand[i] + arrival[i] - gi_demand[i]
                eoh_demand_fix[i] = boh_demand_fix[i] + arrival[i] - gi_demand_fix[i]
                eoh_sop[i] = boh_sop[i] + arrival[i] - gi_sop[i]
                eoh_sop_fix[i] = boh_sop_fix[i] + arrival[i] - gi_sop_fix[i]
                eoh_sop_export[i] = boh_sop_export[i] + arrival[i] - gi_sop_export[i]

            # 결과를 DataFrame에 반영
            group[MTRL_PSI_BOH_DEMAND_COLUMN] = boh_demand
            group[MTRL_PSI_BOH_DEMAND_FIXED_COLUMN] = boh_demand_fix
            group[MTRL_PSI_BOH_SOP_COLUMN] = boh_sop
            group[MTRL_PSI_BOH_SOP_FIXED_COLUMN] = boh_sop_fix
            group[MTRL_PSI_BOH_SOP_EXPORT_COLUMN] = boh_sop_export

            group[MTRL_PSI_EOH_DEMAND_COLUMN] = eoh_demand
            group[MTRL_PSI_EOH_DEMAND_FIXED_COLUMN] = eoh_demand_fix
            group[MTRL_PSI_EOH_SOP_COLUMN] = eoh_sop
            group[MTRL_PSI_EOH_SOP_FIXED_COLUMN] = eoh_sop_fix
            group[MTRL_PSI_EOH_SOP_EXPORT_COLUMN] = eoh_sop_export

            return group


        #       그룹화 후 벡터화로 처리
        df_MtrlPSICalue = df_MtrlPSI[(df_MtrlPSI[SUB_LOCATION_COLUMN] == '-') & (df_MtrlPSI[TRANS_MODE_COLUMN] == '-')].copy()
        df_MtrlPSICalue = df_MtrlPSICalue.sort_values(by=[TIME_WEEK_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN])
        df_MtrlPSICalue[TIME_WEEK_COLUMN] = df_MtrlPSICalue[TIME_WEEK_COLUMN].astype(str)
        df_MtrlPSICalue = df_MtrlPSICalue.groupby([VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN], as_index=False).apply(compute_group_numpy)
        df_MtrlPSICalue.drop_duplicates(inplace=True)
        print_df(df_MtrlPSICalue, 'STEP4 by 9.1 ____ df_MtrlPSICalue .... eoh & boh')

        df_MtrlPSI[TIME_WEEK_COLUMN] = df_MtrlPSI[TIME_WEEK_COLUMN].astype(str)
        df_MtrlPSI = pd.merge(df_MtrlPSI, df_MtrlPSICalue, how='left',
                              on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TIME_WEEK_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN]).drop_duplicates()
        print_df(df_MtrlPSI, 'STEP4 by 9.2 ____ df_MtrlPSI .... merge[df_MtrlPSI, df_MtrlPSICalue]')

        df_MtrlPSI.rename(columns={
            MTRL_PSI_REQ_DEMAND_FIXED_COLUMN+'_x': MTRL_PSI_REQ_DEMAND_FIXED_COLUMN,
            MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN+'_x': MTRL_PSI_REQ_DEMAND_UNFIXED_COLUMN,
            MTRL_PSI_REQ_SOP_STATUS_COLUMN+'_x': MTRL_PSI_REQ_SOP_STATUS_COLUMN,
            MTRL_PSI_REQ_STATUS_FIXED_COLUMN+'_x': MTRL_PSI_REQ_STATUS_FIXED_COLUMN,
            MTRL_PSI_REQ_STATUS_HQ_COLUMN+'_x': MTRL_PSI_REQ_STATUS_HQ_COLUMN,
            MTRL_PSI_REQ_STATUS_NSCM_COLUMN+'_x': MTRL_PSI_REQ_STATUS_NSCM_COLUMN,
            MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN+'_x': MTRL_PSI_REQ_STATUS_DASH_NEW_COLUMN,
            MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN+'_x': MTRL_PSI_REQ_STATUS_DASH_DUAL_COLUMN,
            MTRL_PSI_REQ_STATUS_EC_COLUMN+'_x': MTRL_PSI_REQ_STATUS_EC_COLUMN,
            MTRL_PSI_REQ_SOP_TYPE_COLUMN+'_x': MTRL_PSI_REQ_SOP_TYPE_COLUMN,
            MTRL_PSI_REQ_TYPE_SET_COLUMN+'_x': MTRL_PSI_REQ_TYPE_SET_COLUMN,
            MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN+'_x': MTRL_PSI_REQ_TYPE_SOP_ASSY_COLUMN,
            MTRL_PSI_REQ_SOP_EXPORT_COLUMN+'_x': MTRL_PSI_REQ_SOP_EXPORT_COLUMN,
            MTRL_PSI_ARRIVAL_SN_COLUMN+'_x': MTRL_PSI_ARRIVAL_SN_COLUMN,
            MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN+'_x': MTRL_PSI_ARRIVAL_SUPPLY_PLAN_COLUMN,
            MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN+'_x': MTRL_PSI_ARRIVAL_OPEN_PO_COLUMN,
            MTRL_PSI_ARRIVAL_RTP_COLUMN+'_x': MTRL_PSI_ARRIVAL_RTP_COLUMN,
            MTRL_PSI_ARRIVAL_RTF_COLUMN+'_x': MTRL_PSI_ARRIVAL_RTF_COLUMN,
            MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN+'_x': MTRL_PSI_ARRIVAL_GLOBAL_RTF_COLUMN,
            MTRL_PSI_ARRIVAL_CMI_COLUMN+'_x': MTRL_PSI_ARRIVAL_CMI_COLUMN,
            MTRL_PSI_ARRIVAL_EXCEL_COLUMN+'_x': MTRL_PSI_ARRIVAL_EXCEL_COLUMN,
            MTRL_PSI_BOH_DEMAND_COLUMN+'_y': MTRL_PSI_BOH_DEMAND_COLUMN,
            MTRL_PSI_BOH_DEMAND_FIXED_COLUMN+'_y': MTRL_PSI_BOH_DEMAND_FIXED_COLUMN,
            MTRL_PSI_BOH_SOP_COLUMN+'_y': MTRL_PSI_BOH_SOP_COLUMN,
            MTRL_PSI_BOH_SOP_FIXED_COLUMN+'_y': MTRL_PSI_BOH_SOP_FIXED_COLUMN,
            MTRL_PSI_BOH_SOP_EXPORT_COLUMN+'_y': MTRL_PSI_BOH_SOP_EXPORT_COLUMN,
            MTRL_PSI_EOH_DEMAND_COLUMN+'_y': MTRL_PSI_EOH_DEMAND_COLUMN,
            MTRL_PSI_EOH_DEMAND_FIXED_COLUMN+'_y': MTRL_PSI_EOH_DEMAND_FIXED_COLUMN,
            MTRL_PSI_EOH_SOP_COLUMN+'_y': MTRL_PSI_EOH_SOP_COLUMN,
            MTRL_PSI_EOH_SOP_FIXED_COLUMN+'_y': MTRL_PSI_EOH_SOP_FIXED_COLUMN,
            MTRL_PSI_EOH_SOP_EXPORT_COLUMN+'_y': MTRL_PSI_EOH_SOP_EXPORT_COLUMN,
        }, inplace=True)
        print_df(df_MtrlPSI, 'STEP4 by 9.3 ____ df_MtrlPSI .... column rename')

        df_MtrlPSI = df_MtrlPSI[df_MtrlPSI_columns]
        print_df(df_MtrlPSI, 'STEP4 by 9.4 ____ df_MtrlPSI .... final')


        # 최종 아웃풋
        df_out_MtrlPSI = rename_and_delete_df(df_MtrlPSI)

        step('=====> STEP4 End')


        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : output table create')

        df_out_MtrlPSIStructure[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_ReqQuantity[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_MtrlPSI[VERSION_NAME_COLUMN] = paramOutVersion

        dataframes = {
            'df_out_MtrlPSIStructure': df_out_MtrlPSIStructure,
            'df_out_ReqQuantity': df_out_ReqQuantity,
            'df_out_MtrlPSI': df_out_MtrlPSI,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}')

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_MtrlPSIStructure = pd.DataFrame(columns=df_MtrlPSIStructure_columns)
        df_out_ReqQuantity = pd.DataFrame(columns=df_MtrlPSIStructure_columns)
        df_out_MtrlPSI = pd.DataFrame(columns=df_MtrlPSIStructure_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_MtrlPSIStructure = pd.DataFrame(columns=df_MtrlPSIStructure_columns)
        df_out_ReqQuantity = pd.DataFrame(columns=df_MtrlPSIStructure_columns)
        df_out_MtrlPSI = pd.DataFrame(columns=df_MtrlPSIStructure_columns)
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


