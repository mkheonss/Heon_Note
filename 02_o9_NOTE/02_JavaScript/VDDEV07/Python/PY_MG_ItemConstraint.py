"""
* 프로그램명
    - PY_MG_ItemConstraint

* 내용
    - PY_MG_ItemConstraint 에서 정의한 Soft Constraint 대상 Item + BOD Item Mtrl + Constraint UI 를 확인하여 Time Varying Soft Constraints 모델링

* 변경이력
    - 2024.09.11 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemMtrl      : Select ([Item Material].[MSL3] * [Item Material].[MSL4] *  [Item Material].[MSL5] * [Item Material].[Item Material] );
    - df_in_ConstTypeL3   : Select (Version.[Version Name] * [Item Material].[MSL3] * [Relative Week].[Relative Week] ) on row, ({Measure.[Mtrl Const Type L3 W_Type]}) on column;
    - df_in_ConstTypeL4   : Select (Version.[Version Name] * [Item Material].[MSL4] * [Relative Week].[Relative Week] ) on row, ({Measure.[Mtrl Const Type L4 W_Type] }) on column;
    - df_in_ConstTypeL5   : Select (Version.[Version Name] * [Item Material].[MSL5] * [Relative Week].[Relative Week] ) on row, ({Measure.[Mtrl Const Type L5 W_Type]}) on column;
    - df_in_ConstTypeItem : Select (Version.[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Relative Week].[Relative Week] ) on row, ({ Measure.[Mtrl Const Type Item W_Type]}) on column;

* Flow Summary
    - STEP1. MSL3, MSL4, MSL5 관계 Set 구성
    - STEP2. Soft Constraint 모델링 대상 Item 발췌 및 저장
    - STEP3. UnConstraint 대상 Item 발췌 및 저장

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_MtrlConstType

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_MG_ItemConstraint] for measures {[Mtrl Const Type Batch_Type]}
        using scope (&MPV * &PlanningHorizon)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPFIXCapacity / MG:  Mtrl Const Type Batch
        Select ([Version].[Version Name] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Batch_Plant], Measure.[Mtrl Const Type Batch_Type]}) on column;


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
str_instance = 'PY_MG_ItemConstraint'
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
            df_in_ItemMtrl = read_csv_file("df_in_ItemMtrl")
            df_in_ConstTypeL3 = read_csv_file("df_in_ConstTypeL3")
            df_in_ConstTypeL4 = read_csv_file("df_in_ConstTypeL4")
            df_in_ConstTypeL5 = read_csv_file("df_in_ConstTypeL5")
            df_in_ConstTypeItem = read_csv_file("df_in_ConstTypeItem")
    
    
        print_df(df_in_ItemMtrl, 'input table load .... df_in_ItemMtrl')
        print_df(df_in_ConstTypeL3, 'input table load .... df_in_ConstTypeL3')
        print_df(df_in_ConstTypeL4, 'input table load .... df_in_ConstTypeL4')
        print_df(df_in_ConstTypeL5, 'input table load .... df_in_ConstTypeL5')
        print_df(df_in_ConstTypeItem, 'input table load .... df_in_ConstTypeItem')
    
        step('=====> STEP1 End')
        
        
        
    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
    
        LOCATION_COLUMN = 'Location.[Location]'
        LOCATION_X_COLUMN = 'Location.[Location]_x'
        LOCATION_Y_COLUMN = 'Location.[Location]_y'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
    
        ITEM_METRIAL_MSL3_COLUMN = 'Item Material.[MSL3]'
        ITEM_METRIAL_MSL4_COLUMN = 'Item Material.[MSL4]'
        ITEM_METRIAL_MSL5_COLUMN = 'Item Material.[MSL5]'
        ITEM_METRIAL_COLUMN = 'Item Material.[Item Material]'
        RELATIVE_WEEK_COLUMN = 'Relative Week.[Relative Week]'
        MTRL_CONSTTYPE_ITEM_W_TYPE_COLUMN = 'Mtrl Const Type Item W_Type'
        MTRL_CONSTTYPE_L3_W_TYPE_COLUMN = 'Mtrl Const Type L3 W_Type'
        MTRL_CONSTTYPE_L4_W_TYPE_COLUMN = 'Mtrl Const Type L4 W_Type'
        MTRL_CONSTTYPE_L5_W_TYPE_COLUMN = 'Mtrl Const Type L5 W_Type'
        MTRL_CONSTTYPE_BATCH_TYPE_COLUMN = 'Mtrl Const Type Batch_Type'
    
        SOFT_CHECK_COLUMN = 'SoftCheck'
        SOFT_ITEM_CHECK_COLUMN = 'SoftItemChk'
        UN_CONSTITEM_CHECK_COLUMN = 'UnconstItemChk'
        UN_CONST_CHECK_COLUMN = 'UnConstCheck'
    
        CONST_COUNT = 'ConstCount'
    
        UN_CONSTRAINT_VALUE_VALUE = 'UnConstraint'
        SOFT_VALUE = 'Soft'
        HARD_VALUE = 'Hard'
        UN_VALUE = 'Un'
        
        df_MtrlConstType_columns = [VERSION_NAME_COLUMN, ITEM_METRIAL_COLUMN, MTRL_CONSTTYPE_BATCH_TYPE_COLUMN]
        
    
        step('=====> STEP2 End')
        
        
        
    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # ====================> STEP3 by 1 (Start) -> df_MSL Set 구성
        
        # 1.1 필요컬럼 발췌
        df_MSL = (df_in_ItemMtrl[[ITEM_METRIAL_MSL3_COLUMN, ITEM_METRIAL_MSL4_COLUMN, ITEM_METRIAL_MSL5_COLUMN]].copy().drop_duplicates())
        print_df(df_MSL, 'STEP3 by 1.1 ____ df_MSL .... select')
        
        # ====================> STEP3 by 1 (End)
    
    
    
    
    
        # ====================> STEP3 by 2 (Start)
        
        # 2.1 df_L3Count Set 생성
        l3_grouped_df = df_in_ConstTypeL3.groupby([ITEM_METRIAL_MSL3_COLUMN, MTRL_CONSTTYPE_L3_W_TYPE_COLUMN]).size().reset_index(name=CONST_COUNT)
    
        #   2.1.1 Filter groups having count >= 1
        df_buf_L3Count = l3_grouped_df[l3_grouped_df[CONST_COUNT] >= 1]
        print_df(df_buf_L3Count, 'STEP3 by 2.1.1 ____ df_buf_L3Count .... filter')
    
    
        # 2.2 df_L4Count Set 생성
        l4_grouped_df = df_in_ConstTypeL4.groupby([ITEM_METRIAL_MSL4_COLUMN, MTRL_CONSTTYPE_L4_W_TYPE_COLUMN]).size().reset_index(name=CONST_COUNT)
    
        #   2.2.1 Filter groups having count >= 1
        df_buf_L4Count = l4_grouped_df[l4_grouped_df[CONST_COUNT] >= 1]
        print_df(df_buf_L4Count, 'STEP3 by 2.2.1 ____ df_buf_L4Count .... filter')
    
    
        # 2.3 df_L5Count Set 생성
        l5_grouped_df = df_in_ConstTypeL5.groupby([ITEM_METRIAL_MSL5_COLUMN, MTRL_CONSTTYPE_L5_W_TYPE_COLUMN]).size().reset_index(name=CONST_COUNT)
    
        #   2.3.1 Filter groups having count >= 1
        df_buf_L5Count = l5_grouped_df[l5_grouped_df[CONST_COUNT] >= 1]
        print_df(df_buf_L5Count, 'STEP3 by 2.3.1 ____ df_buf_L5Count .... filter')
    
    
        # 2.4 df_L5SoftCheckSet 생성
        #   2.4.1 df_MSL create
        #       2.4.1.1 df_MSL3 create
        df_MSL3 = df_buf_L3Count[
            (df_buf_L3Count[MTRL_CONSTTYPE_L3_W_TYPE_COLUMN] == SOFT_VALUE) & (df_buf_L3Count[CONST_COUNT] > 0)
        ].copy()
        df_MSL3 = df_MSL3[[ITEM_METRIAL_MSL3_COLUMN]]
        print_df(df_MSL3, 'STEP3 by 2.4.1.1 ____ df_MSL3 .... filter')
    
        #       2.4.1.2 df_MSL4 create
        df_MSL4 = df_buf_L4Count[
            (df_buf_L4Count[MTRL_CONSTTYPE_L4_W_TYPE_COLUMN].isin([HARD_VALUE, UN_VALUE])) & (df_buf_L4Count[CONST_COUNT] >= 34)
        ].copy()
        df_MSL4 = df_MSL4[[ITEM_METRIAL_MSL4_COLUMN]]
        print_df(df_MSL4, 'STEP3 by 2.4.1.2 ____ df_MSL4 .... filter')
    
        #       2.4.1.3 df_MSL5 create
        df_MSL5 = df_buf_L5Count[
            (df_buf_L5Count[MTRL_CONSTTYPE_L5_W_TYPE_COLUMN].isin([HARD_VALUE, UN_VALUE])) & (df_buf_L5Count[CONST_COUNT] >= 34)
        ].copy()
        df_MSL5 = df_MSL5[[ITEM_METRIAL_MSL5_COLUMN]]
        print_df(df_MSL5, 'STEP3 by 2.4.1.3 ____ df_MSL5 .... filter')
    
    
        #   2.4.2 df_MSL3, df_MSL join
        df_buf_L5SoftCheckSet_1 = pd.merge(df_MSL3, df_MSL, how='inner', on=ITEM_METRIAL_MSL3_COLUMN)
        print_df(df_buf_L5SoftCheckSet_1, 'STEP3 by 2.4.2 ____ df_buf_L5SoftCheckSet_1 .... merge[df_MSL3, df_MSL]')
    
        #   2.4.3 df_buf_L5SoftCheckSet_1, df_MSL4 left join
        df_buf_L5SoftCheckSet_2 = pd.merge(df_buf_L5SoftCheckSet_1, df_MSL4, how='left', on=ITEM_METRIAL_MSL4_COLUMN)
        print_df(df_buf_L5SoftCheckSet_2, 'STEP3 by 2.4.3 ____ df_buf_L5SoftCheckSet_2 .... merge[df_buf_L5SoftCheckSet_1, df_MSL4]')
    
        #   2.4.4 df_buf_L5SoftCheckSet_1, df_MSL5 left join
        df_buf_L5SoftCheckSet_3 = pd.merge(df_buf_L5SoftCheckSet_2, df_MSL5, how='left', on=ITEM_METRIAL_MSL5_COLUMN)
        print_df(df_buf_L5SoftCheckSet_3, 'STEP3 by 2.4.4 ____ df_buf_L5SoftCheckSet_3 .... merge[df_buf_L5SoftCheckSet_2, df_MSL5]')
    
        #   2.4.5 df_L5SoftCheckSet create
        df_L5SoftCheckSet = df_buf_L5SoftCheckSet_3.copy()
    
        df_L5SoftCheckSet = df_L5SoftCheckSet[[ITEM_METRIAL_MSL3_COLUMN, ITEM_METRIAL_MSL4_COLUMN, ITEM_METRIAL_MSL5_COLUMN]].drop_duplicates()
    
        df_L5SoftCheckSet[SOFT_CHECK_COLUMN] = np.where(
            df_L5SoftCheckSet[ITEM_METRIAL_MSL4_COLUMN].notna() | df_L5SoftCheckSet[ITEM_METRIAL_MSL5_COLUMN].notna(), 'N', 'Y'
        )
        print_df(df_L5SoftCheckSet, 'STEP3 by 2.4.5 ____ df_L5SoftCheckSet .... filter')
    
    
    
        # 2.5 df_MtrlConstType_1 에 Soft 대상 입력
        #   2.5.1 filter 'Mtrl Const Type Item W_Type' in ('Hard','Un')
        df_filtered = df_in_ConstTypeItem[df_in_ConstTypeItem[MTRL_CONSTTYPE_ITEM_W_TYPE_COLUMN].isin([HARD_VALUE, UN_VALUE])]
    
        #   2.5.2 Group by 'Item Material' and count, filter groups having count >= 34
        df_constTypeItem = df_filtered.groupby(ITEM_METRIAL_COLUMN).filter(lambda x: len(x) >= 34)
        print_df(df_constTypeItem, 'STEP3 by 2.5.2 ____ df_constTypeItem .... groupby')
    
        #   2.5.3 df_MtrlConstType create
        df_buf_L5SoftCheckY = df_L5SoftCheckSet[df_L5SoftCheckSet[SOFT_CHECK_COLUMN] == 'Y'].copy()
    
        df_buf_MtrlConstType_1 = pd.merge(df_buf_L5SoftCheckY, df_in_ItemMtrl, on=ITEM_METRIAL_MSL5_COLUMN, how='inner')
        print_df(df_buf_MtrlConstType_1, 'STEP3 by 2.5.3 ____ df_buf_MtrlConstType_1 .... merge[df_buf_L5SoftCheckY, df_in_ItemMtrl]')
    
        df_buf_MtrlConstType_2 = pd.merge(df_buf_MtrlConstType_1, df_constTypeItem, on=ITEM_METRIAL_COLUMN, how='inner')
        print_df(df_buf_MtrlConstType_2, 'STEP3 by 2.5.3 ____ df_buf_MtrlConstType_2 .... merge[df_buf_MtrlConstType_1, df_constTypeItem]')
    
        df_buf_MtrlConstType_2[SOFT_ITEM_CHECK_COLUMN] = np.where(df_buf_MtrlConstType_2[ITEM_METRIAL_COLUMN].notna(), 'N', 'Y')
        df_buf_MtrlConstType_2 = df_buf_MtrlConstType_2[[ITEM_METRIAL_COLUMN, SOFT_ITEM_CHECK_COLUMN]]
        print_df(df_buf_MtrlConstType_2, 'STEP3 by 2.5.3 ____ df_buf_MtrlConstType_2 .... filter')
    
        #   2.5.4 df_MtrlConstType1 create
        df_MtrlConstType1 = df_buf_MtrlConstType_2[df_buf_MtrlConstType_2[SOFT_ITEM_CHECK_COLUMN] == 'Y'].copy()
        df_MtrlConstType1[MTRL_CONSTTYPE_BATCH_TYPE_COLUMN] = SOFT_VALUE
        print_df(df_MtrlConstType1, 'STEP3 by 2.5.4 ____ df_MtrlConstType1 .... filter')
    
        # ====================> STEP3 by 2 (End)
    
    
    
    
    
        # ====================> STEP3 by 3 (Start)
        
        # 3.1 df_L5UnConstCheckSet 생성
        #   3.1.1 df_un_MSL create
        #       3.1.1.1 df_un_MSL3 create
        df_un_MSL3 = df_buf_L3Count[(df_buf_L3Count[MTRL_CONSTTYPE_L3_W_TYPE_COLUMN] == UN_VALUE) & (df_buf_L3Count[CONST_COUNT] >= 34)].copy()
        df_un_MSL3 = df_un_MSL3[[ITEM_METRIAL_MSL3_COLUMN]]
        print_df(df_un_MSL3, 'STEP3 by 3.1.1.1 ____ df_un_MSL3 .... filter')
    
        #       3.1.1.2 df_un_MSL4 create
        df_un_MSL4 = df_buf_L4Count[(df_buf_L4Count[MTRL_CONSTTYPE_L4_W_TYPE_COLUMN].isin([HARD_VALUE, SOFT_VALUE])) & (df_buf_L4Count[CONST_COUNT] >= 34)].copy()
        df_un_MSL4 = df_un_MSL4[[ITEM_METRIAL_MSL4_COLUMN]]
        print_df(df_un_MSL4, 'STEP3 by 3.1.1.2 ____ df_un_MSL4 .... filter')
    
        #       3.1.1.3 df_un_MSL5 create
        df_un_MSL5 = df_buf_L5Count[(df_buf_L5Count[MTRL_CONSTTYPE_L5_W_TYPE_COLUMN].isin([HARD_VALUE, SOFT_VALUE])) & (df_buf_L5Count[CONST_COUNT] >= 34)].copy()
        df_un_MSL5 = df_un_MSL5[[ITEM_METRIAL_MSL5_COLUMN]]
        print_df(df_un_MSL5, 'STEP3 by 3.1.1.3 ____ df_un_MSL5 .... filter')
    
    
        #   3.1.2 df_un_MSL3, df_MSL join
        df_buf_L5UnConstCheckSet_1 = pd.merge(df_un_MSL3, df_MSL, how='inner', on=ITEM_METRIAL_MSL3_COLUMN)
        print_df(df_buf_L5UnConstCheckSet_1, 'STEP3 by 3.1.2 ____ df_buf_L5UnConstCheckSet_1 .... merge[df_un_MSL3, df_MSL]')
    
        #   3.1.3 df_buf_L5UnConstCheckSet_1, df_un_MSL4 left join
        df_buf_L5UnConstCheckSet_2 = pd.merge(df_buf_L5UnConstCheckSet_1, df_un_MSL4, how='left', on=ITEM_METRIAL_MSL4_COLUMN)
        print_df(df_buf_L5UnConstCheckSet_2, 'STEP3 by 3.1.3 ____ df_buf_L5UnConstCheckSet_2 .... merge[df_buf_L5UnConstCheckSet_1, df_un_MSL4]')
    
        #   3.1.4 df_buf_L5UnConstCheckSet_2, df_un_MSL5 left join
        df_buf_L5UnConstCheckSet_3 = pd.merge(df_buf_L5UnConstCheckSet_2, df_un_MSL5, how='left', on=ITEM_METRIAL_MSL5_COLUMN)
        print_df(df_buf_L5UnConstCheckSet_3, 'STEP3 by 3.1.3 ____ df_buf_L5UnConstCheckSet_3 .... merge[df_buf_L5UnConstCheckSet_2, df_un_MSL5]')
    
        #   3.1.5 df_L5UnConstCheckSet create
        df_L5UnConstCheckSet = df_buf_L5UnConstCheckSet_3.copy()
    
        df_L5UnConstCheckSet = df_L5UnConstCheckSet[[ITEM_METRIAL_MSL3_COLUMN, ITEM_METRIAL_MSL4_COLUMN, ITEM_METRIAL_MSL5_COLUMN]].drop_duplicates()
    
        df_L5UnConstCheckSet[UN_CONST_CHECK_COLUMN] = np.where(
            df_L5UnConstCheckSet[ITEM_METRIAL_MSL4_COLUMN].notna() | df_L5UnConstCheckSet[ITEM_METRIAL_MSL5_COLUMN].notna(), 'N', 'Y'
        )
        print_df(df_L5UnConstCheckSet, 'STEP3 by 3.1.5 ____ df_L5UnConstCheckSet .... filter')
    
    
    
        # 3.2 df_MtrlConstType 에 UnConstraint 대상 입력
        #   3.2.1 filter 'Mtrl Const Type Item W_Type' in ('Hard','Un')
        df_un_filtered = df_in_ConstTypeItem[df_in_ConstTypeItem[MTRL_CONSTTYPE_ITEM_W_TYPE_COLUMN].isin([UN_VALUE])]
    
        #   3.2.2 Group by 'Item Material' and count, filter groups having count >= 34
        df_un_constTypeItem = df_un_filtered.groupby(ITEM_METRIAL_COLUMN).filter(lambda x: len(x) >= 34)
        print_df(df_un_constTypeItem, 'STEP3 by 3.2.2 ____ df_un_constTypeItem .... groupby')
    
        #   3.2.3 df_MtrlConstType create
        df_buf_L5UnSoftCheckY = df_L5UnConstCheckSet[df_L5UnConstCheckSet[UN_CONST_CHECK_COLUMN] == 'Y'].copy()
    
        df_buf_UnMtrlConstType_1 = pd.merge(df_buf_L5UnSoftCheckY, df_in_ItemMtrl, how='inner', on=ITEM_METRIAL_MSL5_COLUMN)
        print_df(df_buf_UnMtrlConstType_1, 'STEP3 by 3.2.3 ____ df_buf_UnMtrlConstType_1 .... merge[df_buf_L5UnSoftCheckY, df_in_ItemMtrl]')
    
        df_buf_UnMtrlConstType_2 = pd.merge(df_buf_UnMtrlConstType_1, df_un_constTypeItem, how='left', on=ITEM_METRIAL_COLUMN)
        print_df(df_buf_UnMtrlConstType_2, 'STEP3 by 3.2.3 ____ df_buf_UnMtrlConstType_2 .... merge[df_buf_UnMtrlConstType_1, df_un_constTypeItem]')
    
        df_buf_UnMtrlConstType_2[UN_CONSTITEM_CHECK_COLUMN] = np.where(df_buf_MtrlConstType_2[ITEM_METRIAL_COLUMN].notna(), 'N', 'Y')
    
        df_buf_UnMtrlConstType_2 = df_buf_UnMtrlConstType_2[[ITEM_METRIAL_COLUMN, UN_CONSTITEM_CHECK_COLUMN]]
        print_df(df_buf_UnMtrlConstType_2, 'STEP3 by 3.2.3 ____ df_buf_UnMtrlConstType_2 .... filter')
    
        #   3.2.4 df_MtrlConstType2 create
        df_MtrlConstType2 = df_buf_UnMtrlConstType_2[df_buf_UnMtrlConstType_2[UN_CONSTITEM_CHECK_COLUMN] == 'Y'].copy()
        df_MtrlConstType2[MTRL_CONSTTYPE_BATCH_TYPE_COLUMN] = UN_CONSTRAINT_VALUE_VALUE
        print_df(df_MtrlConstType2, 'STEP3 by 3.2.4 ____ df_MtrlConstType2 .... filter')
    
        # ====================> STEP3 by 3 (End)
    
        step('=====> STEP3 End')
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        # df_MtrlConstType concat
        df_out_MtrlConstType = pd.concat([df_MtrlConstType1, df_MtrlConstType1]).drop_duplicates()
        
        df_out_MtrlConstType[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_MtrlConstType = df_out_MtrlConstType[df_MtrlConstType_columns]
    
        step('=====> STEP4 End')
        
        
    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_MtrlConstType, 'output table create .... df_out_MtrlConstType', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_MtrlConstType = pd.DataFrame(columns=df_MtrlConstType_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_MtrlConstType = pd.DataFrame(columns=df_MtrlConstType_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
