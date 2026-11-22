"""
* 프로그램명
    - PY_MG_BODStructure

* 내용

* 변경이력
    - 2024.07.19 / 권태우 / Create
    - 2024.09.03 / 권태우 / 로직변경(BOM Master, BOM Component SET, KD, LCM 구성 요건 변경)
    - 2024.09.06 / 권태우 / 로직변경
                                Step4 : SET_BOM에서 SET_BOM.KD_CODE가 Null 인것은 자체적으로 Insert(Left Join 개념)
                                Step9 : 삭제
                                Step5 : Left-join 으로 변경
                                Step10 : Step5.2 변경 (Inner Join만 유지, SET_KD_LCM_BOD.LCM Code = NULL 유지)
    - 2024.09.09 / 권태우 / 로직변경
                                Step8 : Left join 으로 변경
                                최종아웃풋 생성시
                                    Location].[Location] = Hub Site
                                    [Sequence].[Sequence] = SET Code, Hub Site 별로 유효한것만 Sequencing
    - 2026.02.18 / 임채수 / LCM Mapping 조건 추가

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_Item         : Select ([Item].[Item] * [Item].[ProductType] * [Item].[Item Stage].filter(#.Name in {"SET", "KD", "LCM", "OPEN_CELL", "PANEL"})) on row where {Version.[Version Name], Measure.[Item Site Asn_Cur Status] in {"ACTIVE", "PLANNED"}};
    - df_in_BOMMaster    : Select ([Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column where {Version.[Version Name]};
    - df_in_BOMComponent : Select ([Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate], Measure.[BOM Comp_Valid Flag]}) on column where {Version.[Version Name]};
    - df_in_BODItemMtrl  : Select ([Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lock Flag], Measure.[BOD Item Mtrl_Lot Size], Measure.[BOD Item Mtrl_Lot Type]}) on column where {Version.[Version Name]};
    - df_in_BODItem      : Select ([Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Dummy], Measure.[BOD Item_BOD Frozen]}) on column where {Version.[Version Name]};

* Flow Summary
    - STEP1. SET BOM create
    - STEP2. KD BOM create
    - STEP3. LCM BOM create
    - STEP4. SET_KD_BOD create
    - STEP5. SET_KD_LCM_BOD create
    - STEP5.2. LCM Code 기준으로 LCM Site → KD Site BOD를 구성함
    - STEP6. SET_KD_LCM_OCELL_BOD create
    - STEP7. Hub_SET_KD_LCM_OCELL_BOD create
    - STEP8. ALL_BOD create

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BODStructure

* 데이타 초기화
    - DELETE DATA FOR MODEL [BOD Structure] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_BODStructure] for measures {[BOD Structure_DC Site]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] ) on row, ({Measure.[BOD Structure_DC Site], Measure.[BOD Structure_Hub Site], Measure.[BOD Structure_KD Code], Measure.[BOD Structure_KD Site], Measure.[BOD Structure_LCM Code], Measure.[BOD Structure_LCM Site], Measure.[BOD Structure_OCell Code], Measure.[BOD Structure_OCell Site], Measure.[BOD Structure_SET BOM Version], Measure.[BOD Structure_SET Site]}) on column;

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
import pytz
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_BODStructure'
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
    if elapsed < 60:  # 1분 미만
        return f"{round(elapsed)} seconds"
    elif elapsed < 3600:  # 1시간 미만
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes} minute {seconds} second"
    else:  # 1시간 이상
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours} hour {minutes} minute {seconds} second"


def get_current_date_str(tz: str | None = None) -> str:
    """
    현재 시각을 'YYYY-MM-DD HH:MM:SS' 형식 문자열로 반환.
    tz 인자로 'UTC', 'KST' 등의 타임존을 지정 가능.
    - 'UTC': UTC 기준
    - 'KST' 또는 'Asia/Seoul': 한국 시간 기준
    - None 또는 기타: 로컬 타임존 기준
    """
    if isinstance(tz, str):
        tz_upper = tz.upper()
        if tz_upper == "UTC":
            now = datetime.datetime.now(datetime.timezone.utc)
        elif tz_upper == "KST" or tz == "Asia/Seoul":
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.datetime.now(kst)
        else:
            now = datetime.datetime.now()
    else:
        now = datetime.datetime.now()

    return now.strftime("%Y-%m-%d %H:%M:%S")


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
            df_in_Item = read_csv_file("df_in_Item")
            df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
            df_in_BOMComponent = read_csv_file("df_in_BOMComponent")
            df_in_BODItem = read_csv_file("df_in_BODItem")
            df_in_BODItemMtrl = read_csv_file("df_in_BODItemMtrl")


        dataframes = {
            'df_in_Item': df_in_Item,
            'df_in_BOMMaster': df_in_BOMMaster,
            'df_in_BOMComponent': df_in_BOMComponent,
            'df_in_BODItem': df_in_BODItem,
            'df_in_BODItemMtrl': df_in_BODItemMtrl,
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
        ITEM_X_COLUMN = 'Item.[Item]_x'
        ITEM_Y_COLUMN = 'Item.[Item]_y'
        ITEM_STAGE_COLUMN = 'Item.[Item Stage]'
        ITEM_STAGE_X_COLUMN = 'Item.[Item Stage]_x'
        ITEM_STAGE_Y_COLUMN = 'Item.[Item Stage]_y'
        ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
        ITEM_PRODUCT_TYPE_COLUMN = 'Item.[ProductType]'
        ITEM_PRODUCT_TYPE_X_COLUMN = 'Item.[ProductType]_x'
        ITEM_PRODUCT_TYPE_Y_COLUMN = 'Item.[ProductType]_y'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        GT_NAME_FIX_COLUMN = 'Global Top.[GT Name Fix]'

        BOM_ID_COLUMN = 'BOM Info.[BOM ID]'
        BOM_ID_X_COLUMN = 'BOM Info.[BOM ID]_x'
        BOM_ID_Y_COLUMN = 'BOM Info.[BOM ID]_y'
        BOM_MASTER_ID_COLUMN = 'BOM Master_BOM ID'
        BOM_MASTER_ID_X_COLUMN = 'BOM Master_BOM ID_x'
        BOM_MASTER_ID_Y_COLUMN = 'BOM Master_BOM ID_y'
        BOM_MASTER_PERIORITY_COLUMN = 'BOM Master_Priority'
        BOM_MASTER_STATUS_COLUMN = 'BOM Master_Status'
        BOM_MASTER_EFF_ENDDATE_COLUMN = 'BOM Master_Eff Enddate'
        BOM_MASTER_EFF_STARTDATE_COLUMN = 'BOM Master_Eff Startdate'

        BOM_COMP_CONSUME_QTY_COLUMN = 'BOM Comp_Consume Qty'
        BOM_COMP_VAILD_FLAG_COLUMN = 'BOM Comp_Valid Flag'
        BOM_COMP_EFF_ENDDATE_COLUMN = 'BOM Comp_Eff Enddate'
        BOM_COMP_EFF_ENDDATE_X_COLUMN = 'BOM Comp_Eff Enddate_x'
        BOM_COMP_EFF_ENDDATE_Y_COLUMN = 'BOM Comp_Eff Enddate_y'
        BOM_COMP_EFF_STARTDATE_COLUMN = 'BOM Comp_Eff Startdate'

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

        SKU_VALUE = 'SKU'
        SET_VALUE = 'SET'
        LCM_VALUE = 'LCM'
        PANEL_VALUE = 'PANEL'
        OCELL_VALUE = 'OPEN_CELL'
        KD_VALUE = 'KD'

        NOR_VALUE = 'NOR'
        OPT_VALUE = 'OPT'
        CKD_VALUE = 'CKD'
        SKD_VALUE = 'SKD'

        MAX_YEAR_VALUE = '9999'
        PROC_YEAR_LIMIT_VALUE = '2262'

        varif = 'N'

        version_columns = [VERSION_NAME_COLUMN]

        bod_all_columns = [
            ITEM_COLUMN, LOCATION_COLUMN, SEQUENCE_COLUMN,
            BOD_STRUCTURE_DC_SITE_COLUMN, BOD_STRUCTURE_HUB_SITE_COLUMN,
            BOD_STRUCTURE_KD_CODE_COLUMN, BOD_STRUCTURE_KD_SITE_COLUMN,
            BOD_STRUCTURE_LCM_CODE_COLUMN, BOD_STRUCTURE_LCM_SITE_COLUMN,
            BOD_STRUCTURE_OCELL_CODE_COLUMN, BOD_STRUCTURE_OCELL_SITE_COLUMN,
            BOD_STRUCTURE_SET_SITE_COLUMN, BOD_STRUCTURE_SET_BOM_VERSION_COLUMN,
        ]

        fn_bod_all_columns = version_columns + bod_all_columns

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_Item = df_in_Item.loc[
        #     (df_in_Item[ITEM_COLUMN] == 'QN100QN80FFXZA') |
        #     (df_in_Item[ITEM_COLUMN] == 'QN100QN80HDXZA')
        # ].copy()
        # df_in_BOMMaster = df_in_BOMMaster.loc[
        #     (df_in_BOMMaster[BOM_MASTER_ID_COLUMN] == 'QN100QN80FFXZA') |
        #     (df_in_BOMMaster[BOM_MASTER_ID_COLUMN] == 'QN100QN80HDXZA')
        # ].copy()
        #
        # print_df(df_in_BOMMaster, 'STEP3 by 0.1 ____ df_in_BOMMaster .... filter', True)

        # df_in_BOMMaster = df_in_BOMMaster[df_in_BOMMaster[BOM_MASTER_ID_COLUMN].isin(['BN95-11854B','UN32F6000FFXZA'])].copy()
        # ------------------ 테스트 디버깅용 ------------------ end



        # ====================> Prework
        #   오늘날짜 가져와서 yyyy-mm-dd 형식으로 변환
        # today = dt.date.today()
        # formatted_today = today.strftime("%Y-%m-%d")
        # note(f'=====> formatted today : {formatted_today}')

        #   Pandas 에서 9999년 처리를 하지 못함. 판다스 처리년한 년도인 2262년으로 변경
        # df_in_BOMComponent[BOM_COMP_EFF_ENDDATE_COLUMN] = df_in_BOMComponent[BOM_COMP_EFF_ENDDATE_COLUMN].replace(
        #     {MAX_YEAR_VALUE: PROC_YEAR_LIMIT_VALUE}, regex=True)

        # 여러 날짜 형식을 지원 하는 `pd.to_datetime`으로 벡터화 연산을 통해 변환
        # df_in_BOMComponent[BOM_COMP_EFF_ENDDATE_COLUMN] = datetime_check_series(
        #     df_in_BOMComponent[BOM_COMP_EFF_ENDDATE_COLUMN])
        # df_in_BOMComponent[BOM_COMP_EFF_ENDDATE_COLUMN] = (df_in_BOMComponent[BOM_COMP_EFF_ENDDATE_COLUMN].
        #                                                    dt.strftime('%Y-%m-%d'))

        #   필요컬럼 발췌
        df_in_BOMMaster = df_in_BOMMaster[[LOCATION_COLUMN, BOM_ID_COLUMN, BOM_MASTER_ID_COLUMN]].drop_duplicates()
        df_in_BOMComponent = df_in_BOMComponent[[ITEM_COLUMN, LOCATION_COLUMN, BOM_ID_COLUMN, BOM_COMP_EFF_ENDDATE_COLUMN]].drop_duplicates()
        df_in_BODItem = df_in_BODItem[[ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN]].drop_duplicates()
        df_in_BODItemMtrl = df_in_BODItemMtrl[[LOCATION_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN]].drop_duplicates()



        #   bom_master buf create
        df_buf_bom_master = pd.merge(
            df_in_BOMMaster, df_in_Item,
            how='inner',
            left_on=[BOM_MASTER_ID_COLUMN],
            right_on=[ITEM_COLUMN],
        )
        print_df(df_buf_bom_master, 'STEP3 by 0.1 ____ df_buf_bom_master .... create')


        #   bom_component buf create
        df_buf_bom_component = pd.merge(
            df_in_BOMComponent, df_in_Item,
            how='inner',
            on=[ITEM_COLUMN],
        )
        print_df(df_buf_bom_component, 'STEP3 by 0.2 ____ df_buf_bom_component .... create')




        # ====================> Prework : BOM Data(SET, KD, LCM) create
        # 1.BOM (SET) create
        #   1.1 BOM Master(SET) create
        #       1.1.1 df_buf_bom_master 에서 Item State 및 Product Type 값에 맞게 filter
        df_bom_master_set = df_buf_bom_master[
            (df_buf_bom_master[ITEM_STAGE_COLUMN] == SET_VALUE) &
            (df_buf_bom_master[ITEM_PRODUCT_TYPE_COLUMN].isin([NOR_VALUE, OPT_VALUE, CKD_VALUE, SKD_VALUE]))
        ].copy()
        print_df(df_bom_master_set, 'STEP3 by 1.1.1 ____ df_bom_master_set .... create')

        #   1.2 BOM Component(SET) create
        #       1.2.1 df_buf_bom_component 에서 Item State 및 Product Type 값에 맞게 filter
        df_buf_bom_component_set = df_buf_bom_component[
            (
                    (df_buf_bom_component[ITEM_STAGE_COLUMN] == SET_VALUE) &
                    (df_buf_bom_component[ITEM_PRODUCT_TYPE_COLUMN].isin([NOR_VALUE, OPT_VALUE, CKD_VALUE, SKD_VALUE]))
            ) |
            (df_buf_bom_component[ITEM_STAGE_COLUMN].isin([LCM_VALUE, PANEL_VALUE]))
        ].copy()
        print_df(df_buf_bom_component_set, 'STEP3 by 1.2.1 ____ df_buf_bom_component_set .... filter')

        #       1.2.2 df_bom_component_set create / bom_eff_enddate > today 큰 값 copy 및
        df_bom_component_set = df_buf_bom_component_set.copy()
        print_df(df_bom_component_set, 'STEP3 by 1.2.2 ____ df_bom_component_set .... create')



        # 2. BOM (KD) create
        #   2.1 BOM Master(KD) create
        #       2.1.1 df_buf_bom_master 에서 Item State 및 Product Type 값에 맞게 filter
        df_bom_master_kd = df_buf_bom_master[
            (df_buf_bom_master[ITEM_STAGE_COLUMN] == SET_VALUE) &
            (df_buf_bom_master[ITEM_PRODUCT_TYPE_COLUMN].isin([NOR_VALUE, OPT_VALUE, CKD_VALUE, SKD_VALUE]))
        ].copy()
        print_df(df_bom_master_kd, 'STEP3 by 2.1.1 ____ df_bom_master_kd .... create')

        #   2.2 BOM Component(KD) create
        #       2.2.1 df_buf_bom_component 에서 Item State 및 Product Type 값에 맞게 filter
        df_buf_bom_component_kd = (
            df_buf_bom_component[df_buf_bom_component[ITEM_STAGE_COLUMN].isin([LCM_VALUE, PANEL_VALUE])].copy()
        )
        print_df(df_buf_bom_component_kd, 'STEP3 by 2.2.1 ____ df_buf_bom_component_kd .... filter')

        #       2.2.2 bom_eff_enddate > today 큰 값 copy 및 df_bom_component_set create
        df_bom_component_kd = df_buf_bom_component_kd.copy()
        print_df(df_bom_component_kd, 'STEP3 by 2.2.2 ____ df_bom_component_kd .... create')



        # 3. BOM (LCM) create
        #   3.1 BOM Master(LCM) create
        #       3.1.1 df_buf_bom_master 에서 Item State 및 Product Type 값에 맞게 filter
        df_bom_master_lcm = df_buf_bom_master[(df_buf_bom_master[ITEM_STAGE_COLUMN] == LCM_VALUE)].copy()
        print_df(df_bom_master_lcm, 'STEP3 by 3.1.1 ____ df_bom_master_lcm .... create')

        #   3.2 BOM Component(LCM) create
        #       3.2.1 df_buf_bom_component 에서 Item State 및 Product Type 값에 맞게 filter
        df_bom_component_lcm = (df_buf_bom_component[df_buf_bom_component[ITEM_STAGE_COLUMN] == OCELL_VALUE].copy())
        print_df(df_bom_component_lcm, 'STEP3 by 3.2.1 ____ df_bom_component_lcm .... create')





        # ====================> Prework : BOD Data(HUB, SET, KD, LCM, OPEN_CELL) create
        # 4.1. Item.[item stage] filter & item dataframe create
        #   4.1.1 item set create
        df_set_item = df_in_Item[df_in_Item[ITEM_STAGE_COLUMN] == SET_VALUE].copy()
        print_df(df_set_item, 'STEP3 by 4.1.1 ____ df_set_item .... create')

        #   4.1.2 item lcm create
        df_lcm_item = df_in_Item[df_in_Item[ITEM_STAGE_COLUMN] == LCM_VALUE].copy()
        print_df(df_lcm_item, 'STEP3 by 4.1.2 ____ df_lcm_item .... create')

        #   4.1.3 item opencell create
        df_ocell_item = df_in_Item[df_in_Item[ITEM_STAGE_COLUMN] == OCELL_VALUE].copy()
        print_df(df_ocell_item, 'STEP3 by 4.1.3 ____ df_ocell_item .... create')

        #   4.1.4 item lcm_set_panel create
        df_lcm_set_panel_item = df_in_Item[df_in_Item[ITEM_STAGE_COLUMN].isin([LCM_VALUE, SET_VALUE, PANEL_VALUE])].copy()
        print_df(df_lcm_set_panel_item, 'STEP3 by 4.1.4 ____ df_lcm_set_panel_item .... create')


        # 4.2. bod_item create
        #   4.2.1 bod_item hub create
        df_bod_item_hub = pd.merge(df_in_BODItem, df_set_item, how='inner', on=[ITEM_COLUMN])
        print_df(df_bod_item_hub, 'STEP3 by 4.2.1 ____ df_bod_item_hub .... create')

        #   4.2.2 bod_item set create
        df_bod_item_set = pd.merge(df_in_BODItem, df_set_item, how='inner', on=[ITEM_COLUMN])
        print_df(df_bod_item_set, 'STEP3 by 4.2.2 ____ df_bod_item_set .... create')

        #   4.2.3 bod_item kd create
        df_bod_item_kd = pd.merge(df_in_BODItem, df_lcm_set_panel_item, how='inner', on=[ITEM_COLUMN])
        print_df(df_bod_item_kd, 'STEP3 by 4.2.3 ____ df_bod_item_kd .... create')

        #   4.2.4 bod_item lcm create
        df_bod_item_lcm = pd.merge(df_in_BODItem, df_lcm_item, how='inner', on=[ITEM_COLUMN])
        print_df(df_bod_item_lcm, 'STEP3 by 4.2.4 ____ df_bod_item_lcm .... create')

        #   4.2.5 bod_item open_cell create
        df_bod_item_mtrl_ocell = pd.merge(
            df_in_BODItemMtrl, df_ocell_item,
            how='inner',
            left_on=[ITEM_METERIAL_COLUMN],
            right_on=[ITEM_COLUMN],
        )
        print_df(df_bod_item_mtrl_ocell, 'STEP3 by 4.2.5 ____ df_bod_item_mtrl_ocell .... create')

        step('=====> STEP3 End')




        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_bom_master_set.empty:
            raise CustomException(".... df_bom_master_set 값이 없습니다.")



        # ====================> STEP 1 : KD가 없는 SET BOM일 경우에는 SET BOM components에 SET Code를 추가하여 가상의 SET BOM을 구성함
        #                                   - Component Item Stage = SET -> BOM Component Item
        #                                                            LCM, PANEL -> SET Code
        #                                                            NULL -> IF KD Code = NULL & BOM Master(SET).BOM ID LIKE '%DUMMY' then
        #                                                                       NULL 로 입력
        #                                                                    ELSE SKIP
        # 1.1 SET BOM create
        df_set_bom = pd.merge(
            df_bom_master_set, df_bom_component_set, how='left',
            on=[BOM_ID_COLUMN, LOCATION_COLUMN],
        )
        print_df(df_set_bom, 'STEP4 by 1.1 ____ df_set_bom .... merge[df_bom_master_set, df_bom_component_set]')

        # 1.2 KD Code 설정
        #   1.2.1 조건식 설정
        conditions = [
            (df_set_bom[ITEM_STAGE_Y_COLUMN] == SET_VALUE),  # 조건 1
            (df_set_bom[ITEM_STAGE_Y_COLUMN].isin([LCM_VALUE, PANEL_VALUE]))
        ]

        #   1.2.2 각 조건에 대응하는 값
        choices = [
            df_set_bom[ITEM_Y_COLUMN],  # 조건 1: df_bom_component_set Item
            df_set_bom[ITEM_X_COLUMN],  # 조건 2: df_bom_master_set Item
        ]

        #   1.2.3 조건에 맞는 값 설정
        df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN] = np.select(conditions, choices, default=np.nan)

        # 1.3 컬럼설정
        df_set_bom.rename(columns={
            ITEM_X_COLUMN: BOD_STRUCTURE_SET_CODE_COLUMN,
            BOM_ID_COLUMN: BOD_STRUCTURE_SET_BOM_VERSION_COLUMN,
            LOCATION_COLUMN: BOD_STRUCTURE_SET_SITE_COLUMN
        }, inplace=True)
        df_set_bom = df_set_bom[[
            BOD_STRUCTURE_SET_SITE_COLUMN, BOD_STRUCTURE_SET_BOM_VERSION_COLUMN,
            BOM_MASTER_ID_COLUMN, BOD_STRUCTURE_SET_CODE_COLUMN, BOD_STRUCTURE_KD_CODE_COLUMN,
        ]].drop_duplicates()

        # 1.4 'BOD Structure_SET BOM Version' 값에 `_DUMMY` 키워드가 없는 행의 인덱스와 `BOD Structure_KD Code` 값이 null인 인덱스를 찾는다.
        # indexes_to_drop = df_set_bom[(df_set_bom[BOD_STRUCTURE_SET_BOM_VERSION_COLUMN].str.contains('_DUMMY', regex=True))
        #                              &
        #                              (df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN].isnull())].index
        #
        # #   1.4.1 해당 인덱스의 행을 삭제한다.
        # df_set_bom.drop(indexes_to_drop, inplace=True)

        df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN] = np.where(
            (
                    (df_set_bom[BOD_STRUCTURE_SET_BOM_VERSION_COLUMN].str.contains('_DUMMY', regex=True)) &
                    (df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN].notna())
            ),
            None,
            df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN]
        )
        print_df(df_set_bom, 'STEP4 by 1.4 ____ df_set_bom .... final')





        # ====================> STEP 2 : KD가 없는 KD BOM일 경우에는 KD BOM Master에 SET Code를 추가하여 가상의 KD BOM을 구성함
        #                                   - KD 없음 : LCM Code → SET Code
        #                                   - KD 있음 : LCM Code → KD Code
        # 2.1 KD BOM create
        df_kd_bom = pd.merge(
            df_bom_master_kd, df_bom_component_kd, how='inner',
            on=[BOM_ID_COLUMN, LOCATION_COLUMN],
        )
        print_df(df_kd_bom, 'STEP4 by 2.1 ____ df_kd_bom ..... merge[df_bom_master_kd, df_bom_component_kd]')

        # 2.2 컬럼설정
        df_kd_bom.rename(columns={
            ITEM_X_COLUMN: BOD_STRUCTURE_KD_CODE_COLUMN,
            LOCATION_COLUMN: BOD_STRUCTURE_KD_SITE_COLUMN,
            ITEM_Y_COLUMN: BOD_STRUCTURE_LCM_CODE_COLUMN,
        }, inplace=True)
        df_kd_bom[BOD_STRUCTURE_SET_BOM_VERSION_COLUMN] = df_kd_bom[BOM_ID_COLUMN]
        df_kd_bom[BOD_STRUCTURE_KD_BOM_VERSION_COLUMN] = df_kd_bom[BOM_ID_COLUMN]
        df_kd_bom = df_kd_bom[[
            BOD_STRUCTURE_KD_SITE_COLUMN, BOM_ID_COLUMN, BOM_MASTER_ID_COLUMN,
            BOD_STRUCTURE_KD_CODE_COLUMN, BOD_STRUCTURE_LCM_CODE_COLUMN,
            BOD_STRUCTURE_SET_BOM_VERSION_COLUMN, BOD_STRUCTURE_KD_BOM_VERSION_COLUMN,
        ]].drop_duplicates()
        print_df(df_kd_bom, 'STEP4 by 2.2 ____ df_kd_bom ..... final')





        # ====================> STEP 3 : OCell Code → LCM Code
        # 3.1 LCM BOM create
        df_lcm_bom = pd.merge(
            df_bom_master_lcm, df_bom_component_lcm, how='inner',
            on=[BOM_ID_COLUMN, LOCATION_COLUMN],
        )
        print_df(df_lcm_bom, 'STEP4 by 3.1 ____ df_lcm_bom .... merge[df_bom_master_lcm, df_bom_component_lcm]')

        # 3.2 컬럼설정
        df_lcm_bom.rename(columns={
            ITEM_X_COLUMN: BOD_STRUCTURE_LCM_CODE_COLUMN,
            LOCATION_COLUMN: BOD_STRUCTURE_LCM_SITE_COLUMN,
            ITEM_Y_COLUMN: BOD_STRUCTURE_OCELL_CODE_COLUMN,
        }, inplace=True)
        df_lcm_bom = df_lcm_bom[[
            BOD_STRUCTURE_LCM_SITE_COLUMN, BOM_ID_COLUMN, BOM_MASTER_ID_COLUMN,
            BOD_STRUCTURE_LCM_CODE_COLUMN, BOD_STRUCTURE_OCELL_CODE_COLUMN,
        ]].drop_duplicates()
        print_df(df_lcm_bom, 'STEP4 by 3.2 ____ df_lcm_bom ..... final')





        # ====================> STEP 4 : KD Code 기준으로 KD Site → SET Site BOD를 구성함
        # 4.1 SET KD BOD create
        #   IF SET_BOM.SET Code = SET_BOM.KD Code
        #       SET_BOM.KD Code = KD_BOM.KD Code &&
        #       SET_BOM.BOM Version = KD_BOM.BOM Version &&
        #       SET_BOM.SET Site = KD_BOM.KD Site)
        #
        #   IF SET_BOM.SET Code != SET_BOM.KD Code
        #       SET_SET.KD Code = KD_BOM.KD Code

        #   4.1.1 SET_BOM.SET Code = SET_BOM.KD Code
        df_set_bom_qu = (
            df_set_bom[df_set_bom[BOD_STRUCTURE_SET_CODE_COLUMN] == df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN]].copy()
        )
        print_df(df_set_bom_qu, 'STEP4 by 4.1.1 ____ df_set_bom_qu .... df_set_bom copy')

        #   4.1.2 SET_BOM.SET Code != SET_BOM.KD Code
        df_set_bom_not_qu = (
            df_set_bom[df_set_bom[BOD_STRUCTURE_SET_CODE_COLUMN] != df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN]].copy()
        )

        print_df(df_set_bom_not_qu, 'STEP4 by 4.1.2 ____ df_set_bom_not_qu .... df_set_bom copy')

        #   4.1.3 'BOD Structure_KD Code' null Copy
        df_set_bom_kd_null = df_set_bom[df_set_bom[BOD_STRUCTURE_KD_CODE_COLUMN].isnull()].copy()
        df_set_bom_kd_null[[
            BOD_STRUCTURE_KD_SITE_COLUMN,
            BOM_ID_COLUMN,
            BOD_STRUCTURE_LCM_CODE_COLUMN,
            BOD_STRUCTURE_KD_BOM_VERSION_COLUMN
        ]] = None
        print_df(df_set_bom_kd_null, 'STEP4 by 4.1.3 ____ df_set_bom_kd_null .... BOD Structure_KD Code null copy')


        #   4.1.4 df_set_bom_qu, df_kd_bom join
        df_buf_set_kd_bod_1 = pd.merge(
            df_set_bom_qu, df_kd_bom,
            how='inner',
            left_on=[BOD_STRUCTURE_KD_CODE_COLUMN, BOD_STRUCTURE_SET_BOM_VERSION_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN],
            right_on=[BOD_STRUCTURE_KD_CODE_COLUMN, BOD_STRUCTURE_SET_BOM_VERSION_COLUMN, BOD_STRUCTURE_KD_SITE_COLUMN],
        )
        df_buf_set_kd_bod_1.rename(columns={
            "BOM Master_BOM ID_x": BOM_MASTER_ID_COLUMN,
        }, inplace=True)
        df_buf_set_kd_bod_1.drop(columns=[BOM_MASTER_ID_Y_COLUMN], inplace=True)
        print_df(df_buf_set_kd_bod_1, 'STEP4 by 4.1.4 ____ df_buf_set_kd_bod_1 .... merged')

        #   4.1.5 df_set_bom_not_qu, df_kd_bom join
        df_buf_set_kd_bod_2 = pd.merge(
            df_set_bom_not_qu, df_kd_bom, how='inner',
            on=[BOD_STRUCTURE_KD_CODE_COLUMN],
        )
        print_df(df_buf_set_kd_bod_2, 'STEP4 by 4.1.5 ____ df_buf_set_kd_bod_2 .... merge[df_set_bom_not_qu, df_kd_bom]')

        df_buf_set_kd_bod_2.rename(columns={
            "BOD Structure_SET BOM Version_x": BOD_STRUCTURE_SET_BOM_VERSION_COLUMN,
            BOM_MASTER_ID_X_COLUMN: BOM_MASTER_ID_COLUMN,
        },inplace=True)
        df_buf_set_kd_bod_2.drop(columns=[
            BOM_MASTER_ID_Y_COLUMN, "BOD Structure_SET BOM Version_y",
        ], inplace=True)

        #   4.1.6 df_buf_set_kd_bod_1, df_buf_set_kd_bod_2 합치기
        df_set_kd_bod = pd.concat([df_buf_set_kd_bod_1, df_buf_set_kd_bod_2, df_set_bom_kd_null]).drop_duplicates()
        print_df(df_set_kd_bod, 'STEP4 by 4.1.6 ____ df_set_kd_bod .... final')





        # ====================> STEP 5 : LCM Code 기준으로 LCM Site → KD Site BOD를 구성함
        # 5-1.1 KD_LCM_BOD Create
        df_set_kd_lcm_bod = pd.merge(
            df_set_kd_bod, df_lcm_bom, how='left',
            on=[BOD_STRUCTURE_LCM_CODE_COLUMN],
        )
        print_df(df_set_kd_lcm_bod, 'STEP4 by 5-1.1 ____ df_set_kd_lcm_bod .... merged')

        # 5.2 컬럼설장
        df_set_kd_lcm_bod.rename(columns={
            BOM_MASTER_ID_X_COLUMN: BOM_MASTER_ID_COLUMN,
        }, inplace=True)
        df_set_kd_lcm_bod.drop(columns=[
            BOM_ID_X_COLUMN, BOM_ID_Y_COLUMN, BOM_MASTER_ID_Y_COLUMN,
        ], inplace=True)
        print_df(df_set_kd_lcm_bod, 'STEP4 by 5-1.2 ____ df_set_kd_lcm_bod ..... final')






        # ====================> STEP 5-2 : LCM Code 기준으로 LCM Site → KD Site BOD를 구성함
        # 5-2.1 Step5에서 생성된 df_set_kd_lcm_bod 과 df_in_Item 을 join 하여 Item Stage를 재구성
        df_buf_set_kd_lcm_bod = pd.merge(
            df_set_kd_lcm_bod, df_in_Item, how='left',
            left_on=[BOD_STRUCTURE_LCM_CODE_COLUMN],
            right_on=[ITEM_COLUMN],
        )
        print_df(df_buf_set_kd_lcm_bod, 'STEP4 by 5-2.1 ____ df_buf_set_kd_lcm_bod .... merge[df_set_kd_lcm_bod, df_in_Item]')

        #   5-2.1.1 LCM 컬럼이 Null 이거나 Item State 가 PANEL 인 값 Copy
        df_set_lcm_null = df_buf_set_kd_lcm_bod[
            (df_buf_set_kd_lcm_bod[BOD_STRUCTURE_LCM_CODE_COLUMN].isnull()) |
            (df_buf_set_kd_lcm_bod[ITEM_STAGE_COLUMN] == PANEL_VALUE)
        ].copy()
        df_set_lcm_null
        df_set_lcm_null[[
            ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN
        ]] = None
        print_df(df_set_lcm_null, 'STEP4 by 5-2.1.1 ____ df_set_lcm_null .... create')

        # 5-2.2 KD_LCM_REFINE_BOD Create
        df_buf_set_kd_lcm_refine_bod = pd.merge(
            df_set_kd_lcm_bod, df_bod_item_lcm, how='inner',
            left_on=[BOD_STRUCTURE_LCM_CODE_COLUMN, BOD_STRUCTURE_LCM_SITE_COLUMN, BOD_STRUCTURE_KD_SITE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN],
        )
        print_df(df_buf_set_kd_lcm_refine_bod, 'STEP4 by 5-2.2 ____ df_buf_set_kd_lcm_refine_bod .... merge[df_set_kd_lcm_bod, df_bod_item_lcm]')



        # 5-2.3 df concat
        df_set_kd_lcm_refine_bod = pd.concat([df_buf_set_kd_lcm_refine_bod, df_set_lcm_null]).drop_duplicates()
        print_df(df_set_kd_lcm_refine_bod, 'STEP4 by 5-2.3 ____ df_set_kd_lcm_refine_bod ..... concat final')





        # ====================> STEP 6 : OCell Code 기준으로 OCell Site → LCM Site BOD를 구성함
        # 6.1.1.1 SET_KD_LCM_OCell_BOD create ( O/Cell to SET )
        df_set_kd_lcm_ocell_bod = pd.merge(
            df_set_kd_lcm_refine_bod, df_bod_item_mtrl_ocell, how='left',
            left_on=[BOD_STRUCTURE_OCELL_CODE_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN],
            right_on=[ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN],
        )
        print_df(df_set_kd_lcm_ocell_bod, 'STEP4 by 6.1.1.1 ____ df_set_kd_lcm_ocell_bod .... merge[df_set_kd_lcm_refine_bod, df_bod_item_mtrl_ocell]')

        # 6.1.1.2 컬럼설정
        df_set_kd_lcm_ocell_bod.rename(columns={
            LOCATION_Y_COLUMN: BOD_STRUCTURE_OCELL_SITE_COLUMN,
            BOM_ID_X_COLUMN: BOM_ID_COLUMN,
        }, inplace=True)
        df_set_kd_lcm_ocell_bod.drop(columns=[
            ITEM_X_COLUMN, SUB_LOCATION_X_COLUMN, ITEM_PRODUCT_TYPE_X_COLUMN, ITEM_STAGE_X_COLUMN,
            LOCATION_X_COLUMN, ITEM_Y_COLUMN, ITEM_METERIAL_COLUMN, ITEM_PRODUCT_TYPE_Y_COLUMN,
            ITEM_STAGE_Y_COLUMN, SUB_LOCATION_Y_COLUMN,
        ], inplace=True)
        print_df(df_set_kd_lcm_ocell_bod, 'STEP4 by 6.1.1.2 ____ df_set_kd_lcm_ocell_bod ..... final')



        # 6.1.2.1 SET_KD_LCM_OCell_BOD create ( O/Cell to LCM ) - Added by LCS at 2026.02.18 ( G2914376(O/C) > P82A(LCM) > P81A(SET) > S821 )
        df_set_kd_lcm_ocell_bod1 = pd.merge(
            df_set_kd_lcm_ocell_bod, df_bod_item_mtrl_ocell, how='left',
            left_on=[BOD_STRUCTURE_OCELL_CODE_COLUMN, BOD_STRUCTURE_LCM_SITE_COLUMN],
            right_on=[ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN],
        )
        print_df(df_set_kd_lcm_ocell_bod1, 'STEP4 by 6.1.2.1 ____ df_set_kd_lcm_ocell_bod1 .... merge[df_set_kd_lcm_ocell_bod, df_bod_item_mtrl_ocell]')

        # 6.1.2.2 컬럼설정
        mask = df_set_kd_lcm_ocell_bod1[LOCATION_COLUMN].notnull()
        df_set_kd_lcm_ocell_bod1.loc[mask, BOD_STRUCTURE_OCELL_SITE_COLUMN] = df_set_kd_lcm_ocell_bod1.loc[mask, LOCATION_COLUMN]
        df_set_kd_lcm_ocell_bod1.drop(columns=[
            ITEM_METERIAL_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_STAGE_COLUMN, ITEM_PRODUCT_TYPE_COLUMN,ITEM_COLUMN,
        ], inplace=True)
        print_df(df_set_kd_lcm_ocell_bod1, 'STEP4 by 6.1.2.2 ____ df_set_kd_lcm_ocell_bod1 ..... final')





        # ====================> STEP 6-2 : OCell Code 기준으로 OCell Site → LCM Site BOD를 구성함
        # 6-2.1 SET_KD_LCM_OCell_BOD create
        df_set_kd_lcm_ocell_bod2 = pd.merge(
            df_set_kd_lcm_ocell_bod1, df_bod_item_mtrl_ocell,
            how='left',
            left_on=[BOD_STRUCTURE_LCM_CODE_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN],
            right_on=[ITEM_METERIAL_COLUMN, LOCATION_COLUMN],
        )
        print_df(df_set_kd_lcm_ocell_bod2, 'STEP4 by 6-2.1 ____ df_set_kd_lcm_ocell_bod2 .... merge[df_set_kd_lcm_ocell_bod, df_bod_item_mtrl_ocell]')

        # 6-2.2 컬럼설정
        mask = df_set_kd_lcm_ocell_bod2[LOCATION_COLUMN].notnull()
        df_set_kd_lcm_ocell_bod2.loc[mask, BOD_STRUCTURE_OCELL_SITE_COLUMN] = (
            df_set_kd_lcm_ocell_bod2.loc[mask, LOCATION_COLUMN].to_numpy()
        )

        df_set_kd_lcm_ocell_bod2.drop(columns=[
            ITEM_METERIAL_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_STAGE_COLUMN, ITEM_PRODUCT_TYPE_COLUMN, ITEM_COLUMN,
        ], inplace=True)
        print_df(df_set_kd_lcm_ocell_bod2, 'STEP4 by 6-2.2 ____ df_set_kd_lcm_ocell_bod2 ..... final')






        # ====================> STEP 7 : SET Code, SET Site 기준으로 SET Site → Hub Site BOD를 구성함
        # 7.1 Hub_SET_KD_LCM_OCell_BOD create
        df_hub_set_kd_lcm_ocell_bod = pd.merge(
            df_set_kd_lcm_ocell_bod2, df_bod_item_set, how='inner',
            left_on=[BOD_STRUCTURE_SET_CODE_COLUMN, BOD_STRUCTURE_SET_SITE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN],
        )
        print_df(df_hub_set_kd_lcm_ocell_bod, 'STEP4 by 7.1 ____ df_hub_set_kd_lcm_ocell_bod .... merge[df_set_kd_lcm_ocell_bod2, df_bod_item_set]')

        # 7.2 컬럼명 변경
        df_hub_set_kd_lcm_ocell_bod.rename(columns={
            SUB_LOCATION_COLUMN: BOD_STRUCTURE_HUB_SITE_COLUMN,
        }, inplace=True)
        df_hub_set_kd_lcm_ocell_bod.drop(columns=[
            ITEM_COLUMN, LOCATION_COLUMN, ITEM_PRODUCT_TYPE_COLUMN, ITEM_STAGE_COLUMN,
        ], inplace=True)
        print_df(df_hub_set_kd_lcm_ocell_bod, 'STEP4 by 7.2 ____ df_hub_set_kd_lcm_ocell_bod ..... final')





        # ====================> STEP 8 : SET Code, Hub Site 기준으로 Hub Site → DC Site BOD를 구성 및 최종 아웃풋 생성
        # 8.1 ALL_BOD create
        df_all_bod = pd.merge(
            df_hub_set_kd_lcm_ocell_bod, df_bod_item_hub, how='left',
            left_on=[BOD_STRUCTURE_SET_CODE_COLUMN, BOD_STRUCTURE_HUB_SITE_COLUMN],
            right_on=[ITEM_COLUMN, LOCATION_COLUMN],
        )
        print_df(df_all_bod, 'STEP4 by 8.1 ____ df_all_bod .... merge[df_hub_set_kd_lcm_ocell_bod, df_bod_item_hub]')

        # 8.2 컬럼설정
        df_all_bod.rename(columns={SUB_LOCATION_COLUMN: BOD_STRUCTURE_DC_SITE_COLUMN}, inplace=True)

        # Location Column을 Hub Site로 채움
        df_all_bod[LOCATION_COLUMN] = df_all_bod[BOD_STRUCTURE_HUB_SITE_COLUMN]

        # Location Column을 DC Site가 있는 경우 DC Site로 채움
        df_all_bod.loc[~df_all_bod[BOD_STRUCTURE_DC_SITE_COLUMN].isna(), LOCATION_COLUMN] = df_all_bod[BOD_STRUCTURE_DC_SITE_COLUMN]

        # Item은 SET Item으로 채움
        df_all_bod[ITEM_COLUMN] = df_all_bod[BOD_STRUCTURE_SET_CODE_COLUMN]


        # 8.3 Sequence make (SET Code, Hub Site 별로 유효한것만 Sequencing)
        # df_all_bod = df_all_bod[bod_all_columns].drop_duplicates()
        # df_all_bod[SEQUENCE_COLUMN] = df_all_bod.groupby(
        #     [BOD_STRUCTURE_HUB_SITE_COLUMN, BOD_STRUCTURE_SET_CODE_COLUMN], sort=False, as_index=False).cumcount() + 1

        # 8.3 Sequence make (SET Code, Hub Site 별로 유효한것만 Sequencing)
        df_all_bod.drop_duplicates()
        df_all_bod[SEQUENCE_COLUMN] = df_all_bod.groupby([LOCATION_COLUMN, ITEM_COLUMN], sort=False, as_index=False).cumcount() + 1
        df_all_bod = df_all_bod[bod_all_columns]


        # 8.5 버전 처리

        print_df(df_all_bod, 'STEP4 by 8.5 ____ df_all_bod .... final')

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_BODStructure = rename_and_delete_df(df_all_bod)
        df_out_BODStructure[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_BODStructure = df_out_BODStructure[fn_bod_all_columns]

        dataframes = {
            'df_out_BODStructure': df_out_BODStructure,
        }

        df_out_BODStructure = ultra_fast_replace_to_none(df_out_BODStructure)

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODStructure = pd.DataFrame(columns=fn_bod_all_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BODStructure = pd.DataFrame(columns=fn_bod_all_columns)
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