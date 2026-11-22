"""
* 프로그램명
    - PY_MG_BODAll

* 내용

* 변경이력
    - 2024.09.09 / 권태우 / Create
    - 2024.10.02 / 권태우 /
        1. Step 6-2 추가
        2. Rank 추가 (BOD All MG의 BOD All_BOD Prty를 아래 기준으로 Setting)
            2.1 Rank1 = Rank(BOD All_SET BOD Prty, BOD All_SET BOD L/T, BOD All_SET Site)
				        Priority가 작은것 우선, Priority가 동일할 경우 L/T 작은것 우선, Priority와 L/T이 동일할 경우 SET Site 작언것 우선

	        2.2 Rank2 = Rank(BOD All_KD BOD Prty)
                        Priority가 작은것 우선

        	2.3 Rank3 = Rank(BOD All_LCM BOD Prty, BOD All_LCM BOD L/T, BOD All_LCM Site)
                        Priority가 작은것 우선, Priority가 동일할 경우 L/T 작은것 우선, Priority와 L/T이 동일할 경우 SET Site 작언것 우선

            2.4 Rank4 = Rank(BOD All_OCELL BOD Prty, BOD All_OCELL BOD L/T, BOD All_LCM Site)
                        Priority가 작은것 우선, Priority가 동일할 경우 L/T 작은것 우선, Priority와 L/T이 동일할 경우 SET Site 작언것 우선
    - 2026.02.18 / 임채수 / O/Cell 로직 추가

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CurrWeek     : Select (&CurrentWeek);
    - df_in_Item         : Select ([Version].[Version Name] * [Item].[Item] * [Item].[ProductType] * [Item].[Item Stage].filter(#.Name in {"SET", "KD", "LCM", "OPEN_CELL", "PANEL"})) on row where {Measure.[Item Site Asn_Cur Status] in {"ACTIVE", "PLANNED"}};
    - df_in_BODItemMtrlW : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl W_Factory Out], Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Intransit LT], Measure.[BOD Item Mtrl W_Port To Port], Measure.[BOD Item Mtrl W_Supplier], Measure.[BOD Item Mtrl W_Total LT]}) on column;
    - df_in_BODStructure : Select ([Version].[Version Name] * [Item].[Item] * [Item].[Product Group] * [Item].[JDM] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[BOD Structure_DC Site], Measure.[BOD Structure_Hub Site], Measure.[BOD Structure_KD Code], Measure.[BOD Structure_KD Site], Measure.[BOD Structure_LCM Code], Measure.[BOD Structure_LCM Site], Measure.[BOD Structure_OCell Code], Measure.[BOD Structure_OCell Site], Measure.[BOD Structure_SET BOM Version], Measure.[BOD Structure_SET Site]}) on column;
    - df_in_BODItem      : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Dummy], Measure.[BOD Item_BOD LT], Measure.[BOD Item_Priority], Measure.[BOD Item_Shipment LT] }) on column where {Coalesce(Measure.[BOD Item_Eff Enddate],NOW())>DATEADD(NOW(),-7,"Day"), Measure.[BOD Item_BOD Valid]=="Y"};
    - df_in_SOPW         : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [To Location].[To Location] * [To Item].[To Item] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * [To Trans Mode].[To Trans Mode] * [Trans Mode].[Trans Mode]) on row, ({Measure.[SOP W_SET MFG Qty], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET SOP Qty]}) on column;
    - df_in_Meterial     : Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Supply Frozen Mtrl Item W_Fix Range], Measure.[Supply Frozen Mtrl Item W_IsRelativeWeek]}) on column where {Measure.[Supply Frozen Mtrl Item_Valid]=="true", &CurrentWeek};
    - df_in_MSL5         : Select ([Version].[Version Name] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Frozen Mtrl L5 W_Fix Range], Measure.[Supply Frozen Mtrl L5 W_IsRelativeWeek]}) on column where {Measure.[Supply Frozen Mtrl Item_Valid]=="true", &CurrentWeek};
    - df_in_MSL3         : Select ([Version].[Version Name] * [Item Material].[MSL3] ) on row, ({Measure.[Supply Frozen Mtrl L3 W_Fix Range], Measure.[Supply Frozen Mtrl L3 W_IsRelativeWeek]}) on column where {&CurrentWeek};
    - df_in_BODCustomerMode: Select ( [Location].[Location] * [Item].[Product Group] ) on row, ({Measure.[BOD Customer Mode_BOD LT]}) on column where {[Version].[Version Name], Measure.[BOD Customer Mode_Valid Flag] == "Y"};

* Flow Summary
    -

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BODAll
    - df_out_BODSumHeader

* 데이타 초기화
    - Delete data for model [BOD All] where{[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    # - EXEC plugin instance [PY_MG_BODAll] for measures {[BOD All_BOD Prty]} using scope (&MPV.unionwith(&LastWeekSyncVersion))
    - EXEC plugin instance [PY_MG_BODAll] for measures {[BOD All_BOD Prty]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[BOD All_BOD Prty], Measure.[BOD All_DC BOD LT], Measure.[BOD All_DC BOD Prty], Measure.[BOD All_DC Ship LT], Measure.[BOD All_DC Site], Measure.[BOD All_DC Trans Mode], Measure.[BOD All_DC Trans Time], Measure.[BOD All_Hub BOD LT], Measure.[BOD All_Hub BOD Prty], Measure.[BOD All_Hub Ship LT], Measure.[BOD All_Hub Site], Measure.[BOD All_Hub Trans Mode], Measure.[BOD All_Hub Trans Time], Measure.[BOD All_KD BOD LT], Measure.[BOD All_KD BOD Prty], Measure.[BOD All_KD Code], Measure.[BOD All_KD Ship LT], Measure.[BOD All_KD Site], Measure.[BOD All_KD Trans Mode], Measure.[BOD All_KD Trans Time], Measure.[BOD All_LCM BOD LT], Measure.[BOD All_LCM BOD Prty], Measure.[BOD All_LCM Code], Measure.[BOD All_LCM Ship LT], Measure.[BOD All_LCM Site], Measure.[BOD All_LCM Trans Mode], Measure.[BOD All_LCM Trans Time], Measure.[BOD All_Min LT Flag], Measure.[BOD All_OCell BOD LT], Measure.[BOD All_OCell BOD Prty], Measure.[BOD All_OCell Code], Measure.[BOD All_OCell Ship LT], Measure.[BOD All_OCell Site], Measure.[BOD All_OCell Trans Mode], Measure.[BOD All_OCell Trans Time], Measure.[BOD All_SET BOD LT], Measure.[BOD All_SET BOD Prty], Measure.[BOD All_SET BOM Version], Measure.[BOD All_SET SOP], Measure.[BOD All_SET Ship LT], Measure.[BOD All_SET Site], Measure.[BOD All_SET Trans Mode], Measure.[BOD All_SET Trans Time], Measure.[BOD All_Tot BOD LT], Measure.[BOD All_Tot Ship LT], Measure.[BOD All_Tot Trans Time]}) on column;

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
from scipy.stats import mode
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_BODAll'
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
        return df[column_name][0]
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


# pattern에 일치되는 문자열 찾아서 occurrence 위치의 문자 적용
def regexp_substr(series, pattern, occurrence):
    def get_match(input_string):
        matches = re.findall(pattern, input_string)
        if len(matches) >= occurrence:
            return matches[occurrence - 1]
        else:
            return None

    return series.apply(get_match)


def ultra_fast_replace_to_none(df):
    """dtype를 최대한 유지하면서 문자열 결측 표현과 숫자 결측을 정리한다."""
    df = df.copy()

    # object 컬럼과 숫자 컬럼 분리
    obj_cols = df.select_dtypes(include=["object"]).columns
    num_cols = df.select_dtypes(include=["number"]).columns

    # object 컬럼: 문자열 형태의 결측/특정 값만 None으로 치환
    if len(obj_cols) > 0:
        obj_data = df[obj_cols].to_numpy(dtype=object, copy=True)
        mask = (
            (obj_data == "nan") |
            (obj_data == "<NA>") |
            (obj_data == "0") |
            pd.isna(obj_data)
        )
        obj_data[mask] = None
        df[obj_cols] = obj_data

    # 숫자 컬럼:
    # - int 계열은 nullable integer(Int64)로 바꿔서 dtype 유지
    # - float 계열은 nullable float(Float64)로 바꿔서 dtype 유지
    for col in num_cols:
        if not df[col].isna().any():
            continue

        if pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype("Int64")
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype("Float64")
        else:
            # 숫자처럼 보이지만 object로 들어온 경우 대비
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if pd.api.types.is_integer_dtype(df[col]):
                df[col] = df[col].astype("Int64")
            else:
                df[col] = df[col].astype("Float64")

    return df


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
            df_in_Item = read_csv_file("df_in_Item")
            df_in_BODItem = read_csv_file("df_in_BODItem")
            df_in_BODItemMtrlW = read_csv_file("df_in_BODItemMtrlW")
            df_in_BODStructure = read_csv_file("df_in_BODStructure")
            df_in_SOPW = read_csv_file("df_in_SOPW")
            df_in_Meterial = read_csv_file("df_in_Meterial")
            df_in_MSL5 = read_csv_file("df_in_MSL5")
            df_in_MSL3 = read_csv_file("df_in_MSL3")
            df_in_BODCustomerMode = read_csv_file("df_in_BODCustomerMode")

        dataframes = {
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_Item': df_in_Item,
            'df_in_BODItem': df_in_BODItem,
            'df_in_BODItemMtrlW': df_in_BODItemMtrlW,
            'df_in_BODStructure': df_in_BODStructure,
            'df_in_SOPW': df_in_SOPW,
            'df_in_Meterial': df_in_Meterial,
            'df_in_MSL5': df_in_MSL5,
            'df_in_MSL3': df_in_MSL3,
            'df_in_BODCustomerMode': df_in_BODCustomerMode,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        SEQUENCE_COLUMN = 'Sequence.[Sequence]'

        LOCATION_COLUMN = 'Location.[Location]'
        LOCATION_X_COLUMN = 'Location.[Location]_x'
        LOCATION_Y_COLUMN = 'Location.[Location]_y'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_JDM_COLUMN = 'Item.[JDM]'
        ITEM_X_COLUMN = 'Item.[Item]_x'
        ITEM_Y_COLUMN = 'Item.[Item]_y'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_TYPE_COLUMN = 'Item.[ProductType]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_METERIAL_ML5_COLUMN = 'Item Material.[MSL5]'
        ITEM_METERIAL_ML3_COLUMN = 'Item Material.[MSL3]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        DUMMY_COLUMN = 'Dummy'

        TO_LOCAION_COLUMN = 'To Location.[To Location]'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'

        TO_ITEM_COLUMN = 'To Item.[To Item]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'

        SUPPLY_FROZEN_MTRL_ITEM_FIX_RANGE_COLUMN = 'Supply Frozen Mtrl Item W_Fix Range'
        SUPPLY_FROZEN_MTRL_ITEM_IRW_COLUMN = 'Supply Frozen Mtrl Item W_IsRelativeWeek'

        SUPPLY_FROZEN_MTRL_L5_FIX_RANGE_COLUMN = 'Supply Frozen Mtrl L5 W_Fix Range'
        SUPPLY_FROZEN_MTRL_L5_IRW_COLUMN = 'Supply Frozen Mtrl L5 W_IsRelativeWeek'

        SUPPLY_FROZEN_MTRL_L3_FIX_RANGE_COLUMN = 'Supply Frozen Mtrl L3 W_Fix Range'
        SUPPLY_FROZEN_MTRL_L3_IRW_COLUMN = 'Supply Frozen Mtrl L3 W_IsRelativeWeek'

        BOD_CUSTOMER_MODE_BOD_LT_COLUMN = 'BOD Customer Mode_BOD LT'

        BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN = 'BOD Item Mtrl W_Factory Out'
        BOD_ITEM_MTRL_W_GR_LT_COLUMN = 'BOD Item Mtrl W_GR LT'
        BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN = 'BOD Item Mtrl W_Intransit LT'
        BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN = 'BOD Item Mtrl W_Port To Port'
        BOD_ITEM_MTRL_W_SUPPLIER_COLUMN = 'BOD Item Mtrl W_Supplier'
        BOD_ITEM_MTRL_W_TOTAL_LT_COLUMN = 'BOD Item Mtrl W_Total LT'

        BOD_STRUCTURE_SET_CODE_COLUMN = 'BOD Structure_SET Code'
        BOD_STRUCTURE_SET_BOM_VERSION_COLUMN = 'BOD Structure_SET BOM Version'
        BOD_STRUCTURE_KD_BOM_VERSION_COLUMN = 'BOD Structure_KD BOM Version'
        BOD_STRUCTURE_LCM_BOM_VERSION_COLUMN = 'BOD Structure_LCM BOM Version'
        BOD_STRUCTURE_DC_SITE_COLUMN = 'BOD Structure_DC Site'
        BOD_STRUCTURE_HUB_SITE_COLUMN = 'BOD Structure_Hub Site'
        BOD_STRUCTURE_SET_SITE_COLUMN = 'BOD Structure_SET Site'
        BOD_STRUCTURE_KD_SITE_COLUMN = 'BOD Structure_KD Site'
        BOD_STRUCTURE_LCM_SITE_COLUMN = 'BOD Structure_LCM Site'
        BOD_STRUCTURE_OCELL_SITE_COLUMN = 'BOD Structure_OCell Site'
        BOD_STRUCTURE_KD_CODE_COLUMN = 'BOD Structure_KD Code'
        BOD_STRUCTURE_LCM_CODE_COLUMN = 'BOD Structure_LCM Code'
        BOD_STRUCTURE_OCELL_CODE_COLUMN = 'BOD Structure_OCell Code'

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

        SOPW_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'
        SOPW_SET_SOP_QTY_COLUMN = 'SOP W_SET SOP Qty'
        SOPW_LCM_SOP_QTY_COLUMN = 'SOP W_LCM SOP Qty'

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
        BOD_ALL_OCELL_FIX_HORIZEN_COLUMN = 'BOD All_OCell Fix Horizon'
        BOD_ALL_OCELL_TOTAL_LT_COLUMN = 'BOD All_OCell Total LT'

        BOD_ALL_SET_BOD_LT_COLUMN = 'BOD All_SET BOD LT'
        BOD_ALL_SET_BOD_PRTY_COLUMN = 'BOD All_SET BOD Prty'
        BOD_ALL_SET_BOM_VERSION_COLUMN = 'BOD All_SET BOM Version'
        BOD_ALL_SET_SOP_COLUMN = 'BOD All_SET SOP'
        BOD_ALL_SET_SHIP_LT_COLUMN = 'BOD All_SET Ship LT'
        BOD_ALL_SET_SITE_COLUMN = 'BOD All_SET Site'
        BOD_ALL_SET_TRANS_MODE_COLUMN = 'BOD All_SET Trans Mode'
        BOD_ALL_SET_TOTAL_LT_COLUMN = 'BOD All_SET Total LT'

        BOD_ALL_CH_BOD_LT_COLUMN = 'BOD All_CH BOD LT'

        BOD_SUM_HEADER_DC_BOD_LT_COLUMN = 'BOD Sum Header_DC BOD LT'
        BOD_SUM_HEADER_DC_SHIP_LT_COLUMN = 'BOD Sum Header_DC Ship LT'
        BOD_SUM_HEADER_DC_TOTAL_LT_COLUMN = 'BOD Sum Header_DC Total LT'
        BOD_SUM_HEADER_HUB_BOD_LT_COLUMN = 'BOD Sum Header_Hub BOD LT'
        BOD_SUM_HEADER_HUB_SHIP_LT_COLUMN = 'BOD Sum Header_Hub Ship LT'
        BOD_SUM_HEADER_HUB_TOTAL_LT_COLUMN = 'BOD Sum Header_Hub Total LT'
        BOD_SUM_HEADER_KD_BOD_LT_COLUMN = 'BOD Sum Header_KD BOD LT'
        BOD_SUM_HEADER_KD_SHIP_LT_COLUMN = 'BOD Sum Header_KD Ship LT'
        BOD_SUM_HEADER_KD_TOTAL_LT_COLUMN = 'BOD Sum Header_KD Total LT'
        BOD_SUM_HEADER_LCM_BOD_LT_COLUMN = 'BOD Sum Header_LCM BOD LT'
        BOD_SUM_HEADER_LCM_SHIP_LT_COLUMN = 'BOD Sum Header_LCM Ship LT'
        BOD_SUM_HEADER_LCM_TOTAL_LT_COLUMN = 'BOD Sum Header_LCM Total LT'
        BOD_SUM_HEADER_OCELL_BOD_LT_COLUMN = 'BOD Sum Header_OCell BOD LT'
        BOD_SUM_HEADER_OCELL_SHIP_LT_COLUMN = 'BOD Sum Header_OCell Ship LT'
        BOD_SUM_HEADER_OCELL_TOTAL_LT_COLUMN = 'BOD Sum Header_OCell Total LT'
        BOD_SUM_HEADER_OCELL_FIX_HORIZEN_COLUMN = 'BOD Sum Header_OCell Fix Horizon'
        BOD_SUM_HEADER_SET_BOD_LT_COLUMN = 'BOD Sum Header_SET BOD LT'
        BOD_SUM_HEADER_SET_SHIP_LT_COLUMN = 'BOD Sum Header_SET Ship LT'
        BOD_SUM_HEADER_SET_TOTAL_LT_COLUMN = 'BOD Sum Header_SET Total LT'

        RANK1_COLUMN = 'Rank1'
        RANK2_COLUMN = 'Rank2'
        RANK3_COLUMN = 'Rank3'
        RANK4_COLUMN = 'Rank4'

        SET_VALUE = 'SET'
        LCM_VALUE = 'LCM'
        PANEL_VALUE = 'PANEL'
        OCELL_VALUE = 'OPEN_CELL'
        KD_VALUE = 'KD'

        NOR_VALUE = 'NOR'
        OPT_VALUE = 'OPT'
        CKD_VALUE = 'CKD'
        SKD_VALUE = 'SKD'

        # Columns 설정
        version_columns = [VERSION_NAME_COLUMN]

        common_columns = [ITEM_COLUMN, LOCATION_COLUMN, ITEM_JDM_COLUMN, SEQUENCE_COLUMN]

        bod_sum_header_common_columns = [LOCATION_COLUMN, SUB_LOCATION_COLUMN]

        structure_columns = [
            BOD_STRUCTURE_SET_BOM_VERSION_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN, BOD_STRUCTURE_DC_SITE_COLUMN,
            BOD_STRUCTURE_KD_SITE_COLUMN, BOD_STRUCTURE_KD_CODE_COLUMN,
            BOD_STRUCTURE_LCM_SITE_COLUMN, BOD_STRUCTURE_LCM_CODE_COLUMN,
            BOD_STRUCTURE_OCELL_SITE_COLUMN, BOD_STRUCTURE_OCELL_CODE_COLUMN,
            BOD_STRUCTURE_HUB_SITE_COLUMN,
        ]

        ch_columns = [
            BOD_ALL_CH_BOD_LT_COLUMN
        ]

        dc_columns = [
            BOD_ALL_DC_BOD_LT_COLUMN, BOD_ALL_DC_SHIP_LT_COLUMN, BOD_ALL_DC_TRANS_MODE_COLUMN, BOD_ALL_DC_SITE_COLUMN,
            BOD_ALL_DC_BOD_PRTY_COLUMN, BOD_ALL_DC_TOTAL_LT_COLUMN,
        ]

        hub_columns = [
            BOD_ALL_HUB_BOD_LT_COLUMN, BOD_ALL_HUB_SHIP_LT_COLUMN, BOD_ALL_HUB_SITE_COLUMN,
            BOD_ALL_HUB_TRANS_MODE_COLUMN, BOD_ALL_HUB_BOD_PRTY_COLUMN, BOD_ALL_HUB_TOTAL_LT_COLUMN,
        ]

        set_columns = [
            BOD_ALL_SET_BOM_VERSION_COLUMN, BOD_ALL_SET_BOD_LT_COLUMN, BOD_ALL_SET_SHIP_LT_COLUMN, BOD_ALL_SET_SITE_COLUMN,
            BOD_ALL_SET_TRANS_MODE_COLUMN, BOD_ALL_SET_BOD_PRTY_COLUMN, BOD_ALL_SET_TOTAL_LT_COLUMN,
        ]

        kd_columns = [
            BOD_ALL_KD_BOD_LT_COLUMN, BOD_ALL_KD_SHIP_LT_COLUMN, BOD_ALL_KD_SITE_COLUMN, BOD_ALL_KD_TRANS_MODE_COLUMN,
            BOD_ALL_KD_BOD_PRTY_COLUMN, BOD_ALL_KD_CODE_COLUMN, BOD_ALL_KD_TOTAL_LT_COLUMN,
        ]

        lcm_columns = [
            BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN, BOD_ALL_LCM_SITE_COLUMN, BOD_ALL_LCM_TRANS_MODE_COLUMN,
            BOD_ALL_LCM_BOD_PRTY_COLUMN, BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_TOTAL_LT_COLUMN,
        ]

        ocell_columns = [
            BOD_ALL_OCELL_BOD_LT_COLUMN, BOD_ALL_OCELL_SHIP_LT_COLUMN, BOD_ALL_OCELL_SITE_COLUMN,
            BOD_ALL_OCELL_TRANS_MODE_COLUMN, BOD_ALL_OCELL_BOD_PRTY_COLUMN,
            BOD_ALL_OCELL_CODE_COLUMN, BOD_ALL_OCELL_TOTAL_LT_COLUMN,
        ]

        bod_sum_header_columns = [
            BOD_SUM_HEADER_DC_BOD_LT_COLUMN, BOD_SUM_HEADER_DC_SHIP_LT_COLUMN, BOD_SUM_HEADER_DC_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_HUB_BOD_LT_COLUMN, BOD_SUM_HEADER_HUB_SHIP_LT_COLUMN, BOD_SUM_HEADER_HUB_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_KD_BOD_LT_COLUMN, BOD_SUM_HEADER_KD_SHIP_LT_COLUMN, BOD_SUM_HEADER_KD_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_LCM_BOD_LT_COLUMN, BOD_SUM_HEADER_LCM_SHIP_LT_COLUMN, BOD_SUM_HEADER_LCM_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_OCELL_BOD_LT_COLUMN, BOD_SUM_HEADER_OCELL_SHIP_LT_COLUMN, BOD_SUM_HEADER_OCELL_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_SET_BOD_LT_COLUMN, BOD_SUM_HEADER_SET_SHIP_LT_COLUMN, BOD_SUM_HEADER_SET_TOTAL_LT_COLUMN,
        ]

        last_columns = [BOD_ALL_BOD_PRTY_COLUMN, BOD_ALL_MIN_LT_FLAG_COLUMN, BOD_ALL_SET_SOP_COLUMN, BOD_ALL_OCELL_FIX_HORIZEN_COLUMN]

        fn_columns = version_columns + common_columns + ch_columns + dc_columns + hub_columns + set_columns + kd_columns + lcm_columns + ocell_columns + last_columns

        fn_bod_sum_header_columns = version_columns + bod_sum_header_common_columns + bod_sum_header_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_BODItem = df_in_BODItem.loc[(df_in_BODItem[ITEM_COLUMN] == 'LS49DG934SNXGO')].copy()
        # ------------------ 테스트 디버깅용 ------------------ end




        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_BODStructure.empty:
            raise CustomException(".... df_in_BODStructure 값이 없습니다.")




        drop_columns = [VERSION_NAME_COLUMN, DUMMY_COLUMN]
        dataframes = [
            df_in_Item, df_in_BODItem, df_in_BODItemMtrlW, df_in_BODStructure,
            df_in_SOPW, df_in_Meterial, df_in_MSL5, df_in_MSL3
        ]

        for df in dataframes:
            df.drop(columns=drop_columns, inplace=True, errors='ignore')



        # ====================> Prework : BOD Data(HUB, SET, KD, LCM, OPEN_CELL) create

        # fillna 값이 다른 컬럼 분리 처리
        fill_zero_cols = [BOD_ITEM_BOD_LT_COLUMN, BOD_ITEM_SHIPMENT_LT_COLUMN]
        fill_9999_cols = [BOD_ITEM_PERIORITY_COLUMN]

        for col in fill_zero_cols:
            arr = df_in_BODItem[col]
            arr = np.where(np.isnan(arr), 0, arr).astype('int32')
            df_in_BODItem[col] = arr

        for col in fill_9999_cols:
            arr = df_in_BODItem[col]
            arr = np.where(np.isnan(arr), 9999, arr).astype('int32')
            df_in_BODItem[col] = arr


        # 현재 주차 가져오기
        current_week = int(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> current_week : {current_week}')


        # CurrentWeek 에 해당하는 데이터만 가져오기
        df_in_BODItemMtrlW[TIME_WEEK_COLUMN] = df_in_BODItemMtrlW[TIME_WEEK_COLUMN].astype(int)
        df_in_BODItemMtrlW = df_in_BODItemMtrlW.loc[df_in_BODItemMtrlW[TIME_WEEK_COLUMN] >= current_week].reset_index(drop=True)
        print_df(df_in_BODItemMtrlW, 'STEP3 by 0.0 ____ df_in_BODItemMtrlW .... Time.[Week] >= current_week')



        # 1. Item.[item stage] filter & item dataframe create
        #   1.1 item set create
        df_set_item = df_in_Item.loc[df_in_Item[ITEM_STAGE_COLUMN] == SET_VALUE].reset_index(drop=True)

        #   1.2 item lcm create
        df_lcm_item = df_in_Item.loc[df_in_Item[ITEM_STAGE_COLUMN] == LCM_VALUE].reset_index(drop=True)

        #   1.3 item opencell create (Modefied by LCS at 2026.03.01 : PANEL_VALUE추가)
        df_ocell_item = df_in_Item.loc[df_in_Item[ITEM_STAGE_COLUMN].isin([OCELL_VALUE, PANEL_VALUE])].reset_index(drop=True)

        #   1.4 item lcm_set_panel create
        df_lcm_set_panel_item = df_in_Item.loc[df_in_Item[ITEM_STAGE_COLUMN].isin([LCM_VALUE, SET_VALUE, PANEL_VALUE])].reset_index(drop=True)



        # 2. bod_item create
        #   2.1 bod_item hub create
        df_bod_item_hub = pd.merge(df_in_BODItem, df_set_item, on=[ITEM_COLUMN], how='inner')
        print_df(df_bod_item_hub, 'STEP3 by 2.1 ____ df_bod_item_hub .... merge')

        #   2.2 bod_item set create
        df_bod_item_set = pd.merge(df_in_BODItem, df_set_item, on=[ITEM_COLUMN], how='inner')
        print_df(df_bod_item_set, 'STEP3 by 2.2 ____ df_bod_item_set .... merge')

        #   2.3 bod_item kd create
        df_bod_item_kd = pd.merge(df_in_BODItem, df_lcm_set_panel_item, on=[ITEM_COLUMN], how='inner')
        print_df(df_bod_item_kd, 'STEP3 by 2.3 ____ df_bod_item_kd .... merge')

        #   2.4 bod_item lcm create
        df_bod_item_lcm = pd.merge(df_in_BODItem, df_lcm_item, on=[ITEM_COLUMN], how='inner')
        print_df(df_bod_item_lcm, 'STEP3 by 2.4 ____ df_bod_item_lcm .... merge')

        #   2.5 bod_item open_cell create
        left_cols = [
            ITEM_METERIAL_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MTRL_W_GR_LT_COLUMN, BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN,
            BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN, BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN
        ]

        right_cols = [ITEM_COLUMN]

        # 필요한 컬럼만 선택 후 merge
        df_bod_item_ocell = pd.merge(
            df_in_BODItemMtrlW[left_cols].drop_duplicates(),
            df_ocell_item[right_cols].drop_duplicates(),
            left_on=ITEM_METERIAL_COLUMN,
            right_on=ITEM_COLUMN,
            how='inner'
        ).drop_duplicates()
        print_df(df_bod_item_ocell, 'STEP3 by 2.5 ____ df_bod_item_ocell .... merge')

        step('=====> STEP3 End')




        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # ====================> STEP4 by 0 (Start) -> df_in_BODCustomerMode merge
        df_in_BODStructure = df_in_BODStructure.merge(
            df_in_BODCustomerMode,
            how='left',
            on=[LOCATION_COLUMN, ITEM_PRODUCT_GROUP_COLUMN]
        )

        df_in_BODStructure[BOD_ALL_CH_BOD_LT_COLUMN] = df_in_BODStructure[BOD_CUSTOMER_MODE_BOD_LT_COLUMN]
        print_df(df_in_BODStructure, 'STEP4 by 0.0 ____ df_in_BODStructure .... merge[df_in_BODCustomerMode]')
        # ====================> STEP4 by 0 (End)



        # ====================> STEP4 by 1 (Start) -> BOD Hub create

        # 1.1 df_in_BODStructure, df_bod_item_hub Join
        df_hub_bod = pd.merge(df_in_BODStructure, df_bod_item_hub, how='left',
                              left_on=[ITEM_COLUMN, BOD_STRUCTURE_DC_SITE_COLUMN, BOD_STRUCTURE_HUB_SITE_COLUMN],
                              right_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN]).drop_duplicates()
        col = BOD_STRUCTURE_OCELL_SITE_COLUMN
        df_hub_bod[col] = np.where(
            df_hub_bod[col].isna(),
            '',
            df_hub_bod[col].astype(str)
        )
        print_df(df_hub_bod, 'STEP4 by 1.1 ____ df_hub_bod .... merge[df_in_BODStructure, df_bod_item_hub]')

        # 1.2 컬럼설정 및 변경
        #   계산 컬럼
        df_hub_bod[BOD_ALL_HUB_TOTAL_LT_COLUMN] = df_hub_bod[BOD_ITEM_BOD_LT_COLUMN] + df_hub_bod[BOD_ITEM_SHIPMENT_LT_COLUMN]
        #   단순 복사
        df_hub_bod[BOD_ALL_HUB_BOD_LT_COLUMN] = df_hub_bod[BOD_ITEM_BOD_LT_COLUMN]
        df_hub_bod[BOD_ALL_HUB_SITE_COLUMN] = df_hub_bod[BOD_STRUCTURE_HUB_SITE_COLUMN]

        df_hub_bod.rename(columns={
            LOCATION_X_COLUMN: LOCATION_COLUMN,
            BOD_ITEM_SHIPMENT_LT_COLUMN: BOD_ALL_HUB_SHIP_LT_COLUMN,
            TRANS_MODE_COLUMN: BOD_ALL_HUB_TRANS_MODE_COLUMN,
            BOD_ITEM_PERIORITY_COLUMN: BOD_ALL_HUB_BOD_PRTY_COLUMN,
        }, inplace=True)

        # 1.3 필요 컬럼 발췌
        step1_columns = common_columns + structure_columns + ch_columns + hub_columns
        df_hub_bod = df_hub_bod[step1_columns].drop_duplicates(ignore_index=True)
        print_df(df_hub_bod, 'STEP4 by 1.3 ____ df_hub_bod .... final')

        # ====================> STEP4 by 1 (End)




        # ====================> STEP4 by 2 (Start) -> BOD Set create

        # 2.1 df_hub_bod, df_bod_item_hub Join
        df_hub_set_bod = pd.merge(df_hub_bod, df_bod_item_set, how='inner',
                                  left_on=[ITEM_COLUMN, BOD_STRUCTURE_HUB_SITE_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN],
                                  right_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN])
        print_df(df_hub_set_bod, 'STEP4 by 2.1 ____ df_hub_set_bod .... merge[df_hub_bod, df_bod_item_set]')

        # 2.2 컬럼설정 및 변경
        #   계산 컬럼
        df_hub_set_bod[BOD_ALL_SET_TOTAL_LT_COLUMN] = df_hub_set_bod[BOD_ITEM_BOD_LT_COLUMN] + df_hub_set_bod[BOD_ITEM_SHIPMENT_LT_COLUMN]
        #   단순 복사
        df_hub_set_bod[BOD_ALL_SET_BOD_LT_COLUMN] = df_hub_set_bod[BOD_ITEM_BOD_LT_COLUMN]
        df_hub_set_bod[BOD_ALL_SET_SITE_COLUMN] = df_hub_set_bod[BOD_STRUCTURE_SET_SITE_COLUMN]



        # 정규 표현식
        #   `[^_ ]`: 언더스코어(`_`)와 공백(` `) 문자를 제외한 모든 문자를 의미
        #   `+`: 앞의 패턴이 1회 이상 반복됨을 의미
        # pattern = r'[^_ ]+'
        # occurrence = 2
        # df_hub_set_bod[BOD_ALL_SET_BOM_VERSION_COLUMN] = (
        #     regexp_substr(df_hub_set_bod[BOD_STRUCTURE_SET_BOM_VERSION_COLUMN], pattern, occurrence)
        # )

        # 패턴: 언더스코어/공백이 아닌 문자들의 2번째 그룹 추출
        df_hub_set_bod[BOD_ALL_SET_BOM_VERSION_COLUMN] = (
            df_hub_set_bod[BOD_STRUCTURE_SET_BOM_VERSION_COLUMN]
            .str.split(r'[_ ]+')
            .str[1]  # 0-based index, 2번째 occurrence
        )

        df_hub_set_bod.rename(columns={
            LOCATION_X_COLUMN: LOCATION_COLUMN,
            BOD_ITEM_SHIPMENT_LT_COLUMN: BOD_ALL_SET_SHIP_LT_COLUMN,
            TRANS_MODE_COLUMN: BOD_ALL_SET_TRANS_MODE_COLUMN,
            BOD_ITEM_PERIORITY_COLUMN: BOD_ALL_SET_BOD_PRTY_COLUMN,
        },inplace=True)

        # 2.3 필요 컬럼 발췌
        step2_columns = common_columns + structure_columns + ch_columns + hub_columns + set_columns
        df_hub_set_bod = df_hub_set_bod[step2_columns].drop_duplicates(ignore_index=True)
        print_df(df_hub_set_bod, 'STEP4 by 2.3 ____ df_hub_set_bod .... final')

        # ====================> STEP4 by 2 (End)




        # ====================> STEP4 by 3 (Start) -> BOD KD create

        # 3.1 df_hub_set_bod, df_bod_item_hub Join
        df_hub_set_kd_bod = pd.merge(df_hub_set_bod, df_bod_item_kd, how='left',
                                     left_on=[BOD_STRUCTURE_KD_CODE_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN, BOD_STRUCTURE_KD_SITE_COLUMN],
                                     right_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN])
        print_df(df_hub_set_kd_bod, 'STEP4 by 3.1 ____ df_hub_set_kd_bod .... merge[df_hub_set_bod, df_bod_item_kd]')

        # 3.2 컬럼설정 및 변경
        #   계산 컬럼
        df_hub_set_kd_bod[BOD_ALL_KD_TOTAL_LT_COLUMN] = df_hub_set_kd_bod[BOD_ITEM_BOD_LT_COLUMN] + df_hub_set_kd_bod[BOD_ITEM_SHIPMENT_LT_COLUMN]
        #   단순 복사
        df_hub_set_kd_bod[BOD_ALL_KD_BOD_LT_COLUMN] = df_hub_set_kd_bod[BOD_ITEM_BOD_LT_COLUMN]
        df_hub_set_kd_bod[BOD_ALL_KD_SITE_COLUMN] = df_hub_set_kd_bod[BOD_STRUCTURE_KD_SITE_COLUMN]
        df_hub_set_kd_bod[BOD_ALL_KD_CODE_COLUMN] = df_hub_set_kd_bod[BOD_STRUCTURE_KD_CODE_COLUMN]

        df_hub_set_kd_bod.rename(columns={
            ITEM_X_COLUMN: ITEM_COLUMN, LOCATION_X_COLUMN: LOCATION_COLUMN,
            BOD_ITEM_SHIPMENT_LT_COLUMN: BOD_ALL_KD_SHIP_LT_COLUMN,
            TRANS_MODE_COLUMN: BOD_ALL_KD_TRANS_MODE_COLUMN,
            BOD_ITEM_PERIORITY_COLUMN: BOD_ALL_KD_BOD_PRTY_COLUMN,
        }, inplace=True)

        # 3.3 필요 컬럼 발췌
        step3_columns = common_columns + structure_columns + ch_columns + hub_columns + set_columns + kd_columns
        df_hub_set_kd_bod = df_hub_set_kd_bod[step3_columns].drop_duplicates(ignore_index=True)
        print_df(df_hub_set_kd_bod, 'STEP4 by 3.3 ____ df_hub_set_kd_bod .... final')

        # ====================> STEP4 by 3 (End)





        # ====================> STEP4 by 4 (Start) -> BOD LCM create

        # 4.1 df_hub_set_kd_bod, df_bod_item_hub Join
        df_hub_set_kd_lcm_bod = pd.merge(df_hub_set_kd_bod, df_bod_item_kd, how='left',
                                         left_on=[BOD_STRUCTURE_LCM_CODE_COLUMN, BOD_STRUCTURE_KD_SITE_COLUMN, BOD_STRUCTURE_LCM_SITE_COLUMN],
                                         right_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN])
        print_df(df_hub_set_kd_lcm_bod, 'STEP4 by 4.1 ____ df_hub_set_kd_lcm_bod .... merge[df_hub_set_kd_bod, df_bod_item_kd]')

        # 4.2 컬럼설정 및 변경
        #   계산 컬럼
        df_hub_set_kd_lcm_bod[BOD_ALL_LCM_TOTAL_LT_COLUMN] = df_hub_set_kd_lcm_bod[BOD_ITEM_BOD_LT_COLUMN] + df_hub_set_kd_lcm_bod[BOD_ITEM_SHIPMENT_LT_COLUMN]
        #   단순 복사
        df_hub_set_kd_lcm_bod[BOD_ALL_LCM_BOD_LT_COLUMN] = df_hub_set_kd_lcm_bod[BOD_ITEM_BOD_LT_COLUMN]
        df_hub_set_kd_lcm_bod[BOD_ALL_LCM_SITE_COLUMN] = df_hub_set_kd_lcm_bod[BOD_STRUCTURE_LCM_SITE_COLUMN]
        df_hub_set_kd_lcm_bod[BOD_ALL_LCM_CODE_COLUMN] = df_hub_set_kd_lcm_bod[BOD_STRUCTURE_LCM_CODE_COLUMN]

        df_hub_set_kd_lcm_bod.rename(columns={
            ITEM_X_COLUMN: ITEM_COLUMN, LOCATION_X_COLUMN: LOCATION_COLUMN,
            BOD_ITEM_SHIPMENT_LT_COLUMN: BOD_ALL_LCM_SHIP_LT_COLUMN,
            TRANS_MODE_COLUMN: BOD_ALL_LCM_TRANS_MODE_COLUMN,
            BOD_ITEM_PERIORITY_COLUMN: BOD_ALL_LCM_BOD_PRTY_COLUMN,
        }, inplace=True)

        # 4.3 필요 컬럼 발췌
        step4_columns = common_columns + structure_columns + ch_columns + hub_columns + set_columns + kd_columns + lcm_columns
        df_hub_set_kd_lcm_bod = df_hub_set_kd_lcm_bod[step4_columns].drop_duplicates(ignore_index=True)
        print_df(df_hub_set_kd_lcm_bod, 'STEP4 by 4.3 ____ df_hub_set_kd_lcm_bod .... final')

        # ====================> STEP4 by 4 (End)





        # ====================> STEP4 by 5 (Start) -> BOD OPEN_CELL create
        # 5.1 df_hub_set_kd_lcm_bod, df_bod_item_ocell Join
        df_hub_set_kd_lcm_ocell_bod = pd.merge(df_hub_set_kd_lcm_bod, df_bod_item_ocell, how='left',
                                               left_on=[BOD_STRUCTURE_LCM_SITE_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN, BOD_STRUCTURE_LCM_CODE_COLUMN],
                                               right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN])
        print_df(df_hub_set_kd_lcm_ocell_bod, 'STEP4 by 5-0.1 ____ df_hub_set_kd_lcm_ocell_bod .... merge[df_hub_set_kd_lcm_bod, df_bod_item_ocell]')

        # 5.2 컬럼설정 및 변경
        #   단순 복사
        df_hub_set_kd_lcm_ocell_bod[BOD_ALL_OCELL_TOTAL_LT_COLUMN] = df_hub_set_kd_lcm_ocell_bod[BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN]
        df_hub_set_kd_lcm_ocell_bod[BOD_ALL_OCELL_SITE_COLUMN] = df_hub_set_kd_lcm_ocell_bod[BOD_STRUCTURE_OCELL_SITE_COLUMN]
        df_hub_set_kd_lcm_ocell_bod[BOD_ALL_OCELL_CODE_COLUMN] = df_hub_set_kd_lcm_ocell_bod[BOD_STRUCTURE_OCELL_CODE_COLUMN]
        df_hub_set_kd_lcm_ocell_bod[BOD_ALL_OCELL_SHIP_LT_COLUMN] = df_hub_set_kd_lcm_ocell_bod[BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN]
        df_hub_set_kd_lcm_ocell_bod[BOD_ALL_OCELL_TRANS_MODE_COLUMN] = df_hub_set_kd_lcm_ocell_bod[TRANS_MODE_COLUMN]
        #   계산 컬럼
        df_hub_set_kd_lcm_ocell_bod[BOD_ALL_OCELL_BOD_LT_COLUMN] = df_hub_set_kd_lcm_ocell_bod[BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN] + df_hub_set_kd_lcm_ocell_bod[BOD_ITEM_MTRL_W_GR_LT_COLUMN]
        #   상수 할당
        df_hub_set_kd_lcm_ocell_bod[BOD_ALL_OCELL_BOD_PRTY_COLUMN] = 1

        df_hub_set_kd_lcm_ocell_bod.rename(columns={
            ITEM_X_COLUMN: ITEM_COLUMN,
            LOCATION_X_COLUMN: LOCATION_COLUMN,
        }, inplace=True)

        # 5.3 필요 컬럼 발췌
        step5_columns = (common_columns + structure_columns + ch_columns + hub_columns + set_columns + kd_columns + lcm_columns + ocell_columns)
        df_hub_set_kd_lcm_ocell_bod = df_hub_set_kd_lcm_ocell_bod[step5_columns].drop_duplicates(ignore_index=True)
        print_df(df_hub_set_kd_lcm_ocell_bod, 'STEP4 by 5-0.3 ____ df_hub_set_kd_lcm_ocell_bod .... final')
        # ====================> STEP4 by 5 (End)




        # ====================> STEP4 by 5-1 (Start) -> BOD OPEN_CELL create
        # 5-1 Added by LCS at 2026.02.18 ( G2914376(O/C) > P82A(LCM) > P81A(SET) > S821 )
        # 5-1.1 df_hub_set_kd_lcm_bod, df_bod_item_ocell Join
        df_hub_set_kd_lcm_ocell_bod1 = pd.merge(df_hub_set_kd_lcm_ocell_bod, df_bod_item_ocell, how='left',
                                               left_on=[BOD_STRUCTURE_OCELL_SITE_COLUMN, BOD_STRUCTURE_LCM_SITE_COLUMN, BOD_STRUCTURE_OCELL_CODE_COLUMN],
                                               right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN])
        print_df(df_hub_set_kd_lcm_ocell_bod1, 'STEP4 by 5-1.1 ____ df_hub_set_kd_lcm_ocell_bod1 .... merge[df_hub_set_kd_lcm_ocell_bod, df_bod_item_ocell]')

        # 5-1.2 컬럼설정 및 변경
        mask = ~pd.isna(df_hub_set_kd_lcm_ocell_bod1[TRANS_MODE_COLUMN])

        # 단순 복사 컬럼 매핑
        column_mapping = {
            BOD_ALL_OCELL_TOTAL_LT_COLUMN: BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN,
            BOD_ALL_OCELL_SITE_COLUMN: BOD_STRUCTURE_OCELL_SITE_COLUMN,
            BOD_ALL_OCELL_CODE_COLUMN: BOD_STRUCTURE_OCELL_CODE_COLUMN,
            BOD_ALL_OCELL_SHIP_LT_COLUMN: BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN,
            BOD_ALL_OCELL_TRANS_MODE_COLUMN: TRANS_MODE_COLUMN,
        }

        target_cols = list(column_mapping.keys())
        source_cols = list(column_mapping.values())

        # 한 번에 업데이트
        df_hub_set_kd_lcm_ocell_bod1.loc[mask, target_cols] = (
            df_hub_set_kd_lcm_ocell_bod1.loc[mask, source_cols].to_numpy()
        )

        # 계산이 필요한 컬럼
        df_hub_set_kd_lcm_ocell_bod1.loc[mask, BOD_ALL_OCELL_BOD_LT_COLUMN] = (
            df_hub_set_kd_lcm_ocell_bod1.loc[mask, BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN] +
            df_hub_set_kd_lcm_ocell_bod1.loc[mask, BOD_ITEM_MTRL_W_GR_LT_COLUMN]
        )

        # 전체 행 업데이트
        df_hub_set_kd_lcm_ocell_bod1[BOD_ALL_OCELL_BOD_PRTY_COLUMN] = 1

        df_hub_set_kd_lcm_ocell_bod1.rename(columns={
            ITEM_X_COLUMN: ITEM_COLUMN,
            LOCATION_X_COLUMN: LOCATION_COLUMN,
        }, inplace=True)

        # 5-1.3 필요 컬럼 발췌
        step5_columns = (common_columns + structure_columns + ch_columns + hub_columns + set_columns + kd_columns + lcm_columns + ocell_columns)
        df_hub_set_kd_lcm_ocell_bod1 = df_hub_set_kd_lcm_ocell_bod1[step5_columns].drop_duplicates(ignore_index=True)
        print_df(df_hub_set_kd_lcm_ocell_bod1, 'STEP4 by 5-1.3 ____ df_hub_set_kd_lcm_ocell_bod1 .... final')
        # ====================> STEP4 by 5-1 (End)





        # ====================> STEP4 by 5-2 (Start) -> BOD OPEN_CELL create
        # 5-2.1 df_hub_set_kd_lcm_bod, df_bod_item_ocell Join
        df_hub_set_kd_lcm_ocell_bod2 = pd.merge(df_hub_set_kd_lcm_ocell_bod1, df_bod_item_ocell, how='left',
                                               left_on=[BOD_STRUCTURE_OCELL_SITE_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN, BOD_STRUCTURE_OCELL_CODE_COLUMN],
                                               right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_COLUMN])
        print_df(df_hub_set_kd_lcm_ocell_bod2, 'STEP4 by 5-2.1 ____ df_hub_set_kd_lcm_ocell_bod2 .... merge[df_hub_set_kd_lcm_ocell_bod1, df_bod_item_ocell]')

        # 5-2.2 컬럼설정 및 변경
        mask = ~pd.isna(df_hub_set_kd_lcm_ocell_bod2[TRANS_MODE_COLUMN])

        # 단순 복사 컬럼 매핑
        column_mapping = {
            BOD_ALL_OCELL_TOTAL_LT_COLUMN: BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN,
            BOD_ALL_OCELL_SITE_COLUMN: BOD_STRUCTURE_OCELL_SITE_COLUMN,
            BOD_ALL_OCELL_CODE_COLUMN: BOD_STRUCTURE_OCELL_CODE_COLUMN,
            BOD_ALL_OCELL_SHIP_LT_COLUMN: BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN,
            BOD_ALL_OCELL_TRANS_MODE_COLUMN: TRANS_MODE_COLUMN,
        }

        target_cols = list(column_mapping.keys())
        source_cols = list(column_mapping.values())

        # 한 번에 업데이트
        df_hub_set_kd_lcm_ocell_bod2.loc[mask, target_cols] = (
            df_hub_set_kd_lcm_ocell_bod2.loc[mask, source_cols].to_numpy()
        )
        print_df(df_hub_set_kd_lcm_ocell_bod2, 'STEP4 by 5-2.2 ____ df_hub_set_kd_lcm_ocell_bod2 .... update columns')

        # 계산이 필요한 컬럼 (별도 처리)
        df_hub_set_kd_lcm_ocell_bod2.loc[mask, BOD_ALL_OCELL_BOD_LT_COLUMN] = (
            df_hub_set_kd_lcm_ocell_bod2.loc[mask, BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN] +
            df_hub_set_kd_lcm_ocell_bod2.loc[mask, BOD_ITEM_MTRL_W_GR_LT_COLUMN]
        )

        # 전체 행 업데이트 (mask 불필요)
        df_hub_set_kd_lcm_ocell_bod2[BOD_ALL_OCELL_BOD_PRTY_COLUMN] = 1

        df_hub_set_kd_lcm_ocell_bod2.rename(columns={
            ITEM_X_COLUMN: ITEM_COLUMN,
            LOCATION_X_COLUMN: LOCATION_COLUMN,
        }, inplace=True)

        # 5-2.3 필요 컬럼 발췌
        step5_columns = (common_columns + structure_columns + ch_columns + hub_columns + set_columns + kd_columns + lcm_columns + ocell_columns)
        df_hub_set_kd_lcm_ocell_bod2 = df_hub_set_kd_lcm_ocell_bod2[step5_columns].drop_duplicates(ignore_index=True)
        print_df(df_hub_set_kd_lcm_ocell_bod2, 'STEP4 by 5-2.3 ____ df_hub_set_kd_lcm_ocell_bod2 .... final')
        # ====================> STEP4 by 5-2 (End)





        # ====================> STEP4 by 6 (Start) -> BOD Prty 및 BOD LT create

        # 불필요 BOD Structure 컬럼 삭제
        drop_columns = [
            BOD_STRUCTURE_SET_BOM_VERSION_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN,
            BOD_STRUCTURE_KD_SITE_COLUMN, BOD_STRUCTURE_KD_CODE_COLUMN,
            BOD_STRUCTURE_LCM_SITE_COLUMN, BOD_STRUCTURE_LCM_CODE_COLUMN,
            BOD_STRUCTURE_OCELL_SITE_COLUMN, BOD_STRUCTURE_OCELL_CODE_COLUMN,
            BOD_STRUCTURE_HUB_SITE_COLUMN,
        ]
        for col in drop_columns:
            del df_hub_set_kd_lcm_ocell_bod2[col]

        # 6.0 컬럼 create
        #   상수 0 할당
        zero_cols = [
            BOD_ALL_SET_SOP_COLUMN, BOD_ALL_BOD_PRTY_COLUMN,
            BOD_ALL_DC_TOTAL_LT_COLUMN, BOD_ALL_DC_BOD_LT_COLUMN,
            BOD_ALL_DC_SHIP_LT_COLUMN, BOD_ALL_DC_BOD_PRTY_COLUMN,
        ]
        df_hub_set_kd_lcm_ocell_bod2[zero_cols] = 0
        #   나머지
        df_hub_set_kd_lcm_ocell_bod2[BOD_ALL_DC_TRANS_MODE_COLUMN] = '-'
        df_hub_set_kd_lcm_ocell_bod2[BOD_ALL_DC_SITE_COLUMN] = df_hub_set_kd_lcm_ocell_bod2[BOD_STRUCTURE_DC_SITE_COLUMN]


        #   Rank1 규칙 적용 : Rank(BOD All_SET BOD Prty, BOD All_SET BOD L/T, BOD All_SET Site) / Priority가 작은것 우선, Priority가 동일할 경우 L/T 작은것 우선, Priority와 L/T이 동일할 경우 SET Site 작언것 우선
        #   Rank2 규칙 적용 : Rank(BOD All_KD BOD Prty) / Priority가 작은것 우선
        #   Rank3 규칙 적용 : Rank(BOD All_LCM BOD Prty, BOD All_LCM BOD L/T, BOD All_LCM Site) / Priority가 작은것 우선, Priority가 동일할 경우 L/T 작은것 우선, Priority와 L/T이 동일할 경우 SET Site 작언것 우선
        #   Rank4 규칙 적용 : Rank(BOD All_LCM BOD Prty, BOD All_OCELL BOD L/T, BOD All_OCELL Site) / Priority가 작은것 우선, Priority가 동일할 경우 L/T 작은것 우선, Priority와 L/T이 동일할 경우 OCELL Site 작언것 우선
        # 1. 카테고리 타입 변환으로 메모리 절약 및 정렬 속도 향상
        categorical_columns = [
            ITEM_COLUMN, LOCATION_COLUMN, BOD_ALL_SET_SITE_COLUMN, BOD_ALL_LCM_SITE_COLUMN, BOD_ALL_OCELL_SITE_COLUMN,
        ]
        for col in categorical_columns:
            if col in df_hub_set_kd_lcm_ocell_bod2.columns:
                df_hub_set_kd_lcm_ocell_bod2[col] = df_hub_set_kd_lcm_ocell_bod2[col].astype('category')

        df = df_hub_set_kd_lcm_ocell_bod2

        # 2. 그룹 키를 미리 생성 (반복 groupby 비용 절감)
        group_keys = [ITEM_COLUMN, LOCATION_COLUMN]

        # 3. 모든 Rank를 groupby.rank()로 계산 (정렬 없이!)
        def calculate_all_ranks_optimized(df):
            """rank() 메서드로 정렬 없이 순위 계산"""

            # Rank1: SET 기준 복합 키 생성
            df['_rank1_key'] = (
                df[BOD_ALL_SET_BOD_PRTY_COLUMN].fillna(9999).astype(np.float64) * 1e12 +
                df[BOD_ALL_SET_BOD_LT_COLUMN].fillna(9999).astype(np.float64) * 1e6 +
                df[BOD_ALL_SET_SITE_COLUMN].cat.codes.astype(np.float64)
            )

            # Rank2: KD 기준
            df['_rank2_key'] = df[BOD_ALL_KD_BOD_PRTY_COLUMN].fillna(9999).astype(np.float64)

            # Rank3: LCM 기준
            df['_rank3_key'] = (
                df[BOD_ALL_LCM_BOD_PRTY_COLUMN].fillna(9999).astype(np.float64) * 1e12 +
                df[BOD_ALL_LCM_BOD_LT_COLUMN].fillna(9999).astype(np.float64) * 1e6 +
                df[BOD_ALL_LCM_SITE_COLUMN].cat.codes.astype(np.float64)
            )

            # Rank4: OCELL 기준
            df['_rank4_key'] = (
                df[BOD_ALL_LCM_BOD_PRTY_COLUMN].fillna(9999).astype(np.float64) * 1e12 +
                df[BOD_ALL_OCELL_BOD_LT_COLUMN].fillna(9999).astype(np.float64) * 1e6 +
                df[BOD_ALL_OCELL_SITE_COLUMN].cat.codes.astype(np.float64)
            )

            # groupby 객체 재사용
            grouped = df.groupby(group_keys, sort=False, observed=True)

            # 한 번에 모든 rank 계산
            df[RANK1_COLUMN] = grouped['_rank1_key'].rank(method='first').astype(np.int32)
            df[RANK2_COLUMN] = grouped['_rank2_key'].rank(method='first').astype(np.int32)
            df[RANK3_COLUMN] = grouped['_rank3_key'].rank(method='first').astype(np.int32)
            df[RANK4_COLUMN] = grouped['_rank4_key'].rank(method='first').astype(np.int32)

            # 임시 컬럼 삭제
            df.drop(columns=['_rank1_key', '_rank2_key', '_rank3_key', '_rank4_key'], inplace=True)

            return df

        df = calculate_all_ranks_optimized(df)

        # 4. BOD_PRTY_SUM 계산 (동일, 이미 최적화됨)
        df['BOD_PRTY_SUM'] = (
            df[RANK1_COLUMN] * 1000000 +
            df[RANK2_COLUMN] * 10000 +
            df[RANK3_COLUMN] * 100 +
            df[RANK4_COLUMN]
        )

        # 5. BOD All_BOD Prty Rank 계산
        df[BOD_STRUCTURE_DC_SITE_COLUMN] = df[BOD_STRUCTURE_DC_SITE_COLUMN].fillna('-')

        grouped = df.groupby(group_keys, sort=False, observed=True)

        df[BOD_ALL_BOD_PRTY_COLUMN] = grouped['BOD_PRTY_SUM'].rank(method='first').astype(np.int32)

        # 6. LT 계산 - NumPy 벡터 연산
        lt_columns = [
            BOD_ALL_HUB_BOD_LT_COLUMN, BOD_ALL_SET_BOD_LT_COLUMN, BOD_ALL_KD_BOD_LT_COLUMN,
            BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_OCELL_BOD_LT_COLUMN
        ]
        lt_sum = df[lt_columns].fillna(0).sum(axis=1)
        df['LT_SUM'] = np.where(lt_sum == 0, 9999, lt_sum).astype(np.int32)

        df['LT_RANK'] = grouped['LT_SUM'].rank(method='first').astype(np.int32)

        # 7. Min LT Flag - transform 대신 merge 사용 (핵심 최적화!)
        min_lt = df.groupby(group_keys, sort=False, observed=True)['LT_RANK'].min()
        min_lt.name = '_min_lt'
        df = df.join(min_lt, on=group_keys)
        df[BOD_ALL_MIN_LT_FLAG_COLUMN] = np.where(df['LT_RANK'] == df['_min_lt'], 'Y', 'N')
        df.drop(columns=['_min_lt'], inplace=True)

        # 8. Sequence 생성
        df[SEQUENCE_COLUMN] = df.groupby(group_keys, sort=False, observed=True).cumcount() + 1

        df_rank4_sorted = df
        print_df(df_rank4_sorted, 'STEP4 by 6.5 ____ df_rank4_sorted .... final')




        # 6.6 'BOD All_SET SOP' 설정
        #   6.6.1 비교대상2(SET-HUB)
        # df_rank4_sorted = df_rank4_sorted.loc[
        #     (df_rank4_sorted[ITEM_COLUMN] == 'LS32CG550ENXZA') &
        #     (df_rank4_sorted[LOCATION_COLUMN] == 'S356')
        # ].copy()
        df_rank4_sorted = pd.merge(
            df_rank4_sorted, df_in_SOPW, how='left',
            left_on=[ITEM_COLUMN, BOD_ALL_SET_SITE_COLUMN, BOD_ALL_HUB_SITE_COLUMN, BOD_ALL_SET_BOM_VERSION_COLUMN,
                     BOD_ALL_SET_TRANS_MODE_COLUMN, BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN, BOD_ALL_LCM_TRANS_MODE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN, TO_LOCAION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
                      TRANS_MODE_COLUMN, TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN]
        )
        df_rank4_sorted[SOPW_SET_SOP_QTY_COLUMN] = df_rank4_sorted[SOPW_SET_SOP_QTY_COLUMN].fillna(0).astype(np.int32)
        mask = df_rank4_sorted[SOPW_SET_SOP_QTY_COLUMN] > 0
        df_rank4_sorted.loc[mask, BOD_ALL_SET_SOP_COLUMN] = df_rank4_sorted.loc[mask, SOPW_SET_SOP_QTY_COLUMN]

        df_rank4_sorted.rename(columns={LOCATION_X_COLUMN: LOCATION_COLUMN,}, inplace=True)
        drop_columns = [
            SOPW_SET_SOP_QTY_COLUMN, SOPW_LCM_SOP_QTY_COLUMN, LOCATION_Y_COLUMN, TO_LOCAION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, TRANS_MODE_COLUMN, SOPW_SET_MFG_QTY_COLUMN,
            TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN,
        ]
        for col in drop_columns:
            del df_rank4_sorted[col]
        print_df(df_rank4_sorted, 'STEP4 by 6.6.1 ____ df_rank4_sorted .... SET-HUB SOP 설정')

        #   6.6.2 비교대상1(HUB-DC)
        df_rank4_sorted = pd.merge(
            df_rank4_sorted, df_in_SOPW, how='left',
            left_on=[ITEM_COLUMN, BOD_ALL_HUB_SITE_COLUMN, BOD_ALL_DC_SITE_COLUMN, BOD_ALL_SET_BOM_VERSION_COLUMN,
                     BOD_ALL_HUB_TRANS_MODE_COLUMN, BOD_ALL_LCM_CODE_COLUMN, BOD_ALL_LCM_SITE_COLUMN, BOD_ALL_LCM_TRANS_MODE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN, TO_LOCAION_COLUMN,BOM_INFO_BOM_VERSION_COLUMN,
                      TRANS_MODE_COLUMN, TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN]
        )
        df_rank4_sorted[SOPW_SET_SOP_QTY_COLUMN] = df_rank4_sorted[SOPW_SET_SOP_QTY_COLUMN].fillna(0).astype(np.int32)
        mask = df_rank4_sorted[SOPW_SET_SOP_QTY_COLUMN] > 0
        df_rank4_sorted.loc[mask, BOD_ALL_SET_SOP_COLUMN] = df_rank4_sorted.loc[mask, SOPW_SET_SOP_QTY_COLUMN]

        df_rank4_sorted.rename(columns={LOCATION_X_COLUMN: LOCATION_COLUMN,}, inplace=True)
        print_df(df_rank4_sorted, 'STEP4 by 6.6.2 ____ df_rank4_sorted .... HUB-DC SOP 설정')

        # 6.7 BOD All_OCell Fix Horizon 설정(적용우선순위 : Item Material > MSL5 > MSL3)
        #   6.7.1 Item Material
        df_rank4_sorted = pd.merge(
            df_rank4_sorted, df_in_Meterial, how='left',
            left_on=[BOD_ALL_OCELL_SITE_COLUMN, BOD_ALL_OCELL_CODE_COLUMN],
            right_on=[LOCATION_COLUMN, ITEM_METERIAL_COLUMN]
        )
        df_rank4_sorted = pd.merge(
            df_rank4_sorted, df_in_MSL5, how='left',
            left_on=[BOD_ALL_OCELL_CODE_COLUMN],
            right_on=[ITEM_METERIAL_ML5_COLUMN]
        )
        df_rank4_sorted = pd.merge(
            df_rank4_sorted, df_in_MSL3, how='left',
            left_on=[BOD_ALL_OCELL_CODE_COLUMN],
            right_on=[ITEM_METERIAL_ML3_COLUMN]
        )

        df_rank4_sorted.rename(columns={LOCATION_X_COLUMN: LOCATION_COLUMN,}, inplace=True)
        drop_columns = [
            SOPW_SET_SOP_QTY_COLUMN, SOPW_LCM_SOP_QTY_COLUMN, LOCATION_Y_COLUMN, TO_LOCAION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, TRANS_MODE_COLUMN, SOPW_SET_MFG_QTY_COLUMN,
            TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN,
        ]
        for col in drop_columns:
            del df_rank4_sorted[col]

        # 존재하는 값인지 확인하는 함수를 정의 (None, NaN, 빈 문자열 등 처리)
        def has_value(series):
            """값이 있는지 확인 (NaN, 빈 문자열 제외)"""
            return ~series.isna() & (series != '')

        # 마스크를 한 번만 계산
        has_A = has_value(df_rank4_sorted[SUPPLY_FROZEN_MTRL_ITEM_FIX_RANGE_COLUMN])
        has_B = has_value(df_rank4_sorted[SUPPLY_FROZEN_MTRL_L5_FIX_RANGE_COLUMN])
        has_C = has_value(df_rank4_sorted[SUPPLY_FROZEN_MTRL_L3_FIX_RANGE_COLUMN])

        # 우선순위 조건 (먼저 나온 조건이 우선)
        conditions = [
            has_A,                      # 1순위: A 값 있음
            ~has_A & has_B,             # 2순위: A 없고 B 있음
            ~has_A & ~has_B & has_C,    # 3순위: A, B 없고 C 있음
        ]

        choices = [
            df_rank4_sorted[SUPPLY_FROZEN_MTRL_ITEM_FIX_RANGE_COLUMN],
            df_rank4_sorted[SUPPLY_FROZEN_MTRL_L5_FIX_RANGE_COLUMN],
            df_rank4_sorted[SUPPLY_FROZEN_MTRL_L3_FIX_RANGE_COLUMN],
        ]

        # 한 번에 할당 (조건 없으면 np.nan)
        df_rank4_sorted[BOD_ALL_OCELL_FIX_HORIZEN_COLUMN] = np.select(conditions, choices, default=np.nan)
        print_df(df_rank4_sorted, 'STEP4 by 6.7.1 ____ df_rank4_sorted .... Item Material select')

        # HUB_SITE는 DC_SITE가 Null인 경우 Null처리 (하혜진P요청 - '25.11.17) added at '25.12.11
        df_rank4_sorted.loc[df_rank4_sorted[BOD_ALL_DC_SITE_COLUMN].isna(), BOD_ALL_HUB_SITE_COLUMN] = np.nan



        # 6.8 최종 컬럼 정리
        df_rank4_sorted[VERSION_NAME_COLUMN] = paramOutVersion
        df_rank4_sorted = df_rank4_sorted[fn_columns]
        print_df(df_rank4_sorted, 'STEP4 by 6.8 ____ df_rank4_sorted .... final')
        # ====================> STEP4 by 6(End)




        # ====================> STEP4 by 6-2 (Start) -> 2025.12.23 추가
        # 필요한 컬럼 리스트 정의
        lt_columns = [
            BOD_ALL_DC_BOD_LT_COLUMN, BOD_ALL_DC_SHIP_LT_COLUMN, BOD_ALL_DC_TOTAL_LT_COLUMN,
            BOD_ALL_HUB_BOD_LT_COLUMN, BOD_ALL_HUB_SHIP_LT_COLUMN, BOD_ALL_HUB_TOTAL_LT_COLUMN,
            BOD_ALL_KD_BOD_LT_COLUMN, BOD_ALL_KD_SHIP_LT_COLUMN, BOD_ALL_KD_TOTAL_LT_COLUMN,
            BOD_ALL_LCM_BOD_LT_COLUMN, BOD_ALL_LCM_SHIP_LT_COLUMN, BOD_ALL_LCM_TOTAL_LT_COLUMN,
            BOD_ALL_OCELL_BOD_LT_COLUMN, BOD_ALL_OCELL_SHIP_LT_COLUMN, BOD_ALL_OCELL_TOTAL_LT_COLUMN, BOD_ALL_OCELL_FIX_HORIZEN_COLUMN,
            BOD_ALL_SET_BOD_LT_COLUMN, BOD_ALL_SET_SHIP_LT_COLUMN, BOD_ALL_SET_TOTAL_LT_COLUMN,
        ]

        # 필요한 컬럼만 한 번에 복사 (전체 복사 X)
        df_rank4_sorted_cp = df_rank4_sorted[[LOCATION_COLUMN] + lt_columns].copy()
        print_df(df_rank4_sorted_cp, 'STEP4 by 6-2.1 ____ df_rank4_sorted_cp .... columns select')

        # Location별 최빈값 집계
        def fast_mode(series):
            counts = series.value_counts()
            return counts.index[0] if not counts.empty else None

        df_rank4_mode = df_rank4_sorted_cp.groupby(LOCATION_COLUMN)[lt_columns].agg(fast_mode).reset_index()
        print_df(df_rank4_mode, 'STEP4 by 6-2.2 ____ df_rank4_mode .... lt mode', True)


        df_rank4_mode.rename(columns={
            BOD_ALL_DC_BOD_LT_COLUMN: BOD_SUM_HEADER_DC_BOD_LT_COLUMN,
            BOD_ALL_DC_SHIP_LT_COLUMN: BOD_SUM_HEADER_DC_SHIP_LT_COLUMN,
            BOD_ALL_DC_TOTAL_LT_COLUMN: BOD_SUM_HEADER_DC_TOTAL_LT_COLUMN,
            BOD_ALL_HUB_BOD_LT_COLUMN: BOD_SUM_HEADER_HUB_BOD_LT_COLUMN,
            BOD_ALL_HUB_SHIP_LT_COLUMN: BOD_SUM_HEADER_HUB_SHIP_LT_COLUMN,
            BOD_ALL_HUB_TOTAL_LT_COLUMN: BOD_SUM_HEADER_HUB_TOTAL_LT_COLUMN,
            BOD_ALL_KD_BOD_LT_COLUMN: BOD_SUM_HEADER_KD_BOD_LT_COLUMN,
            BOD_ALL_KD_SHIP_LT_COLUMN: BOD_SUM_HEADER_KD_SHIP_LT_COLUMN,
            BOD_ALL_KD_TOTAL_LT_COLUMN: BOD_SUM_HEADER_KD_TOTAL_LT_COLUMN,
            BOD_ALL_LCM_BOD_LT_COLUMN: BOD_SUM_HEADER_LCM_BOD_LT_COLUMN,
            BOD_ALL_LCM_SHIP_LT_COLUMN: BOD_SUM_HEADER_LCM_SHIP_LT_COLUMN,
            BOD_ALL_LCM_TOTAL_LT_COLUMN: BOD_SUM_HEADER_LCM_TOTAL_LT_COLUMN,
            BOD_ALL_OCELL_BOD_LT_COLUMN: BOD_SUM_HEADER_OCELL_BOD_LT_COLUMN,
            BOD_ALL_OCELL_SHIP_LT_COLUMN: BOD_SUM_HEADER_OCELL_SHIP_LT_COLUMN,
            BOD_ALL_OCELL_TOTAL_LT_COLUMN: BOD_SUM_HEADER_OCELL_TOTAL_LT_COLUMN,
            BOD_ALL_OCELL_FIX_HORIZEN_COLUMN: BOD_SUM_HEADER_OCELL_FIX_HORIZEN_COLUMN,
            BOD_ALL_SET_BOD_LT_COLUMN: BOD_SUM_HEADER_SET_BOD_LT_COLUMN,
            BOD_ALL_SET_SHIP_LT_COLUMN: BOD_SUM_HEADER_SET_SHIP_LT_COLUMN,
            BOD_ALL_SET_TOTAL_LT_COLUMN: BOD_SUM_HEADER_SET_TOTAL_LT_COLUMN,
        }, inplace=True)
        print_df(df_rank4_mode, 'STEP4 by 6-2.3 ____ df_rank4_mode .... lt rename')


        # 병합할 컬럼 리스트 정의
        target_measures = [
            LOCATION_COLUMN,
            BOD_SUM_HEADER_LCM_BOD_LT_COLUMN,
            BOD_SUM_HEADER_LCM_SHIP_LT_COLUMN,
            BOD_SUM_HEADER_LCM_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_OCELL_BOD_LT_COLUMN,
            BOD_SUM_HEADER_OCELL_FIX_HORIZEN_COLUMN,
            BOD_SUM_HEADER_OCELL_SHIP_LT_COLUMN,
            BOD_SUM_HEADER_OCELL_TOTAL_LT_COLUMN,
        ]

        # location을 기준으로 merge 수행
        df_rank4_sorted = df_rank4_sorted.merge(
            df_rank4_mode[target_measures],
            on=LOCATION_COLUMN,
            how='left'
        )
        print_df(df_rank4_sorted, 'STEP4 by 6-2.4 ____ df_rank4_sorted .... lt mode merge')


        # 업데이트 조건 설정
        mask = (df_rank4_sorted[BOD_ALL_SET_BOM_VERSION_COLUMN] == 'DUMMY') & (df_rank4_sorted[ITEM_JDM_COLUMN] == '-')

        # 컬럼 매핑 정의 (target <- source) (BOD All 컬럼 < - BOD Sum Header_... 컬럼)
        column_mapping = {
            BOD_ALL_LCM_BOD_LT_COLUMN: BOD_SUM_HEADER_LCM_BOD_LT_COLUMN,
            BOD_ALL_LCM_SHIP_LT_COLUMN: BOD_SUM_HEADER_LCM_SHIP_LT_COLUMN,
            BOD_ALL_LCM_TOTAL_LT_COLUMN: BOD_SUM_HEADER_LCM_TOTAL_LT_COLUMN,
            BOD_ALL_OCELL_BOD_LT_COLUMN: BOD_SUM_HEADER_OCELL_BOD_LT_COLUMN,
            BOD_ALL_OCELL_SHIP_LT_COLUMN: BOD_SUM_HEADER_OCELL_SHIP_LT_COLUMN,
            BOD_ALL_OCELL_TOTAL_LT_COLUMN: BOD_SUM_HEADER_OCELL_TOTAL_LT_COLUMN,
            BOD_ALL_OCELL_FIX_HORIZEN_COLUMN: BOD_SUM_HEADER_OCELL_FIX_HORIZEN_COLUMN,
        }

        # 한 번에 업데이트
        target_cols = list(column_mapping.keys())
        source_cols = list(column_mapping.values())

        df_rank4_sorted.loc[mask, target_cols] = df_rank4_sorted.loc[mask, source_cols]
        print_df(df_rank4_sorted, 'STEP4 by 6-2.5 ____ df_rank4_sorted .... lt mode update')

        drop_columns = [
            BOD_SUM_HEADER_LCM_BOD_LT_COLUMN, BOD_SUM_HEADER_LCM_SHIP_LT_COLUMN, BOD_SUM_HEADER_LCM_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_OCELL_BOD_LT_COLUMN, BOD_SUM_HEADER_OCELL_SHIP_LT_COLUMN, BOD_SUM_HEADER_OCELL_TOTAL_LT_COLUMN,
            BOD_SUM_HEADER_OCELL_FIX_HORIZEN_COLUMN,
        ]
        for col in drop_columns:
            del df_rank4_sorted[col]

        print_df(df_rank4_sorted, 'STEP4 by 6-2.6 ____ df_rank4_sorted .... lt mode drop')

        drop_columns = [BOD_SUM_HEADER_OCELL_FIX_HORIZEN_COLUMN]
        for col in drop_columns:
            del df_rank4_mode[col]

        df_rank4_mode[SUB_LOCATION_COLUMN] = "P306" # 임시설정

        # ====================> STEP4 by 6-2(End)




        # ====================> STEP4 by 7 (Start) -> Product Type이 ('NOR','OPT') 일 경우 KD 관련 컬럼 None

        df_rank4_sorted = pd.merge(df_rank4_sorted, df_in_Item, how='inner', on=ITEM_COLUMN)

        kd_columns = [
            BOD_ALL_KD_TOTAL_LT_COLUMN, BOD_ALL_KD_SHIP_LT_COLUMN, BOD_ALL_KD_SITE_COLUMN,
            BOD_ALL_KD_TRANS_MODE_COLUMN, BOD_ALL_KD_BOD_PRTY_COLUMN, BOD_ALL_KD_CODE_COLUMN
        ]

        # 마스크를 NumPy 배열로 생성
        mask = df_rank4_sorted[ITEM_PRODUCT_TYPE_COLUMN].isin(['NOR', 'OPT'])

        for col in kd_columns:
            df_rank4_sorted[col] = np.where(mask, None, df_rank4_sorted[col])

        df_rank4_sorted.drop(columns=[ITEM_PRODUCT_TYPE_COLUMN, ITEM_STAGE_COLUMN, ITEM_JDM_COLUMN], inplace=True)
        print_df(df_rank4_sorted, 'STEP4 by 7.1 ____ df_rank4_sorted .... columns modify')

        # ====================> STEP4 by 7(End)

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_BODAll = rename_and_delete_df(df_rank4_sorted)

        df_out_BODSumHeader = rename_and_delete_df(df_rank4_mode)
        df_out_BODSumHeader[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_BODSumHeader = df_out_BODSumHeader[fn_bod_sum_header_columns]

        dataframes = {
            'df_out_BODAll': df_out_BODAll,
            'df_out_BODSumHeader': df_out_BODSumHeader,
        }

        df_out_BODAll = ultra_fast_replace_to_none(df_out_BODAll)
        df_out_BODSumHeader = ultra_fast_replace_to_none(df_out_BODSumHeader)

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODAll = pd.DataFrame(columns=fn_columns)
        df_out_BODSumHeader = pd.DataFrame(columns=fn_bod_sum_header_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BODAll = pd.DataFrame(columns=fn_columns)
        df_out_BODSumHeader = pd.DataFrame(columns=fn_bod_sum_header_columns)
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