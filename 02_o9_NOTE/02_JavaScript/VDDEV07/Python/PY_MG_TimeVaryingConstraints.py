"""
* 프로그램명
    - PY_MG_TimeVaryingConstraints

* 내용
    - Const UI 에서 관리한 데이타 기준으로 Soft Constraint 모델링 대상 및 UnConstraint 대상 발췌

* 변경이력
    - 2024.09.19 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_MtrlConstType : Select (Version.[Version Name] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Batch_Type]})  on column.filter(Measure.[Mtrl Const Type Batch_Type]== "Soft");
    - df_in_ItemMtrl      : Select ([Item Material].[MSL3] * [Item Material].[MSL4] *  [Item Material].[MSL5] * [Item Material].[Item Material] );
    - df_in_BOD_Item_Mtrl : Select (Version.[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lock Flag], Measure.[BOD Item Mtrl_Lot Size], Measure.[BOD Item Mtrl_Lot Type]}) on column.filter( (isnull(Measure.[BOD Item Mtrl_EFF Enddate])||Measure.[BOD Item Mtrl_EFF Enddate]> Measure.[W Plan Start Date]) &&(isnull(Measure.[BOD Item Mtrl_EFF Startdate])||Measure.[BOD Item Mtrl_EFF Startdate]< Measure.[W Plan End Date]));
    - df_in_ConstTypeL3   : Select (Version.[Version Name] * [Item Material].[MSL3] * [Relative Week].[Relative Week] ) on row, ({Measure.[Mtrl Const Type L3 W_Type]}) on column;
    - df_in_ConstTypeL4   : Select (Version.[Version Name] * [Item Material].[MSL4] * [Relative Week].[Relative Week] ) on row, ({Measure.[Mtrl Const Type L4 W_Type] }) on column;
    - df_in_ConstTypeL5   : Select (Version.[Version Name] * [Item Material].[MSL5] * [Relative Week].[Relative Week] ) on row, ({Measure.[Mtrl Const Type L5 W_Type]}) on column;
    - df_in_ConstTypeItem : Select (Version.[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Relative Week].[Relative Week] ) on row, ({ Measure.[Mtrl Const Type Item W_Type]}) on column;
    - df_in_PlanningWeek  : Select ([Time].[Day] * &PlanningHorizon);

* Flow Summary
    - STEP1. Soft Constraint 모델링 대상 ITEM을 가져와서 현재 ITEM BOD와 매핑
    - STEP2. Soft Constraint 주차와 매핑
    - STEP3~4. Soft Constraint ITEM BOD Set 구성

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BODInfinite

* 데이타 초기화
    - DELETE DATA FOR MODEL [BOD Item Mtrl Infinite] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_TimeVaryingConstraints] for measures {[BOD Item Mtrl Infinite_EFF Startdate]}
        using scope (&MPV * &PlanningHorizon)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPFIXCapacity / MG:  BOD Item Mtrl Infinite
        Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
            ({Measure.[BOD Item Mtrl Infinite_EFF Enddate], Measure.[BOD Item Mtrl Infinite_EFF Startdate]}) on column;


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
str_instance = 'PY_MG_TimeVaryingConstraints'
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
            df_in_MtrlConstType = read_csv_file("df_in_MtrlConstType")
            df_in_ItemMtrl = read_csv_file("df_in_ItemMtrl")
            df_in_BOD_Item_Mtrl = read_csv_file("df_in_BOD_Item_Mtrl")
            df_in_ConstTypeL3 = read_csv_file("df_in_ConstTypeL3")
            df_in_ConstTypeL4 = read_csv_file("df_in_ConstTypeL4")
            df_in_ConstTypeL5 = read_csv_file("df_in_ConstTypeL5")
            df_in_ConstTypeItem = read_csv_file("df_in_ConstTypeItem")
            df_in_PlanningWeek = read_csv_file("df_in_PlanningWeek")


        print_df(df_in_MtrlConstType, 'input table load .... df_in_MtrlConstType')
        print_df(df_in_ItemMtrl, 'input table load .... df_in_ItemMtrl')
        print_df(df_in_BOD_Item_Mtrl, 'input table load .... df_in_BOD_Item_Mtrl')
        print_df(df_in_ConstTypeL3, 'input table load .... df_in_ConstTypeL3')
        print_df(df_in_ConstTypeL4, 'input table load .... df_in_ConstTypeL4')
        print_df(df_in_ConstTypeL5, 'input table load .... df_in_ConstTypeL5')
        print_df(df_in_ConstTypeItem, 'input table load .... df_in_ConstTypeItem')
        print_df(df_in_PlanningWeek, 'input table load .... df_in_PlanningWeek')

        step('=====> STEP 1(End) : Check memory usage & runtime')
        
        
        

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2(Start) : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'

        LOCATION_COLUMN = 'Location.[Location]'
        LOCATION_X_COLUMN = 'Location.[Location]_x'
        LOCATION_Y_COLUMN = 'Location.[Location]_y'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        SUB_LOCATION_Y_COLUMN = 'Sub Location.[Sub Location]_y'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'

        ITEM_METRIAL_MSL3_COLUMN = 'Item Material.[MSL3]'
        ITEM_METRIAL_MSL4_COLUMN = 'Item Material.[MSL4]'
        ITEM_METRIAL_MSL5_COLUMN = 'Item Material.[MSL5]'
        ITEM_METRIAL_COLUMN = 'Item Material.[Item Material]'
        RELATICE_WEEK_COLUMN = 'Relative Week.[Relative Week]'
        MTRL_CONSTTYPE_ITEM_W_TYPE_COLUMN = 'Mtrl Const Type Item W_Type'
        MTRL_CONSTTYPE_L3_W_TYPE_COLUMN = 'Mtrl Const Type L3 W_Type'
        MTRL_CONSTTYPE_L4_W_TYPE_COLUMN = 'Mtrl Const Type L4 W_Type'
        MTRL_CONSTTYPE_L5_W_TYPE_COLUMN = 'Mtrl Const Type L5 W_Type'
        MTRL_CONSTTYPE_BATCH_TYPE_COLUMN = 'Mtrl Const Type Batch_Type'

        BOD_ITEM_MTRL_EFF_ENDDATE_COLUMN = 'BOD Item Mtrl_EFF Enddate'
        BOD_ITEM_MTRL_EFF_STARTDATE_COLUMN = 'BOD Item Mtrl_EFF Startdate'

        BOD_ITEM_MTRL_INFINITE_EFF_ENDDATE_COLUMN = 'BOD Item Mtrl Infinite_EFF Enddate'
        BOD_ITEM_MTRL_INFINITE_EFF_STARTDATE_COLUMN = 'BOD Item Mtrl Infinite_EFF Startdate'

        SOFT_START_WEEK_COLUMN = 'Soft_Start_Week'
        EFFECTIVE_START_DAY_COLUMN = 'effective_start_day'
        PLAN_END_DAY_COLUMN = 'plan_end_day'
        RELATIVE_WEEK_COLUMN = 'Relative_Week'

        INF_LOCATION_COLUMN = 'inf_location'
        MIN_WEEK_COLUMN = 'MinWeek'
        TIME_DAY_COLUMN = 'Time.[Day]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        MIN_WEEK_ITEM_COLUMN = 'MinWeekItem'
        MIN_WEEK_MSL5_COLUMN = 'MinWeekMSL5'
        MIN_WEEK_MSL4_COLUMN = 'MinWeekMSL4'
        MIN_WEEK_MSL3_COLUMN = 'MinWeekMSL3'

        UN_CONSTRAINT_VALUE_VALUE = 'UnConstraint'
        SOFT_VALUE = 'Soft'
        HARD_VALUE = 'Hard'
        UN_VALUE = 'Un'
        MIN_VALUE = 'min'

        df_BODInfinite_columns = [
            VERSION_NAME_COLUMN, ITEM_METRIAL_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MTRL_EFF_STARTDATE_COLUMN, BOD_ITEM_MTRL_EFF_ENDDATE_COLUMN,
        ]

        step('=====> STEP2 End')
        
        
        

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ====================> STEP3 by 1 (Start) > df_SoftItemBOD  Set 구성
        # 1.1 df_in_MtrlConstType, df_in_ItemMtrl join > df_SoftItemBOD create
        df_SoftItemBOD = pd.merge(df_in_MtrlConstType, df_in_ItemMtrl, how='inner', on=[ITEM_METRIAL_COLUMN])
        print_df(df_SoftItemBOD, 'Step3 by 1.1 ____ df_SoftItemBOD .... merge[df_in_MtrlConstType, df_in_ItemMtrl]')

        # 1.2 df_SoftItemBOD, df_in_BOD_Item_Mtrl join
        df_SoftItemBOD = pd.merge(df_SoftItemBOD, df_in_BOD_Item_Mtrl, how='inner', on=[VERSION_NAME_COLUMN, ITEM_METRIAL_COLUMN])
        print_df(df_SoftItemBOD, 'Step3 by 1.2 ____ df_SoftItemBOD .... merge[df_SoftItemBOD, df_in_BOD_Item_Mtrl]')

        # 1.3 필요컬럼 발췌
        df_SoftItemBOD = df_SoftItemBOD[[
            VERSION_NAME_COLUMN, ITEM_METRIAL_COLUMN, ITEM_METRIAL_MSL3_COLUMN, ITEM_METRIAL_MSL4_COLUMN,
            ITEM_METRIAL_MSL5_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN
        ]].drop_duplicates()
        print_df(df_SoftItemBOD, 'Step3 by 1.3 ____ df_SoftItemBOD .... final')
        # ====================> STEP3 by 1 (End)





        # ====================> STEP3 by 2 (Start) > df_SoftStartWeek  Set 구성
        # 2.1 df_ConstTypeItem create
        df_ConstTypeItem = df_in_ConstTypeItem[df_in_ConstTypeItem[MTRL_CONSTTYPE_ITEM_W_TYPE_COLUMN] == SOFT_VALUE].groupby(
            ITEM_METRIAL_COLUMN, as_index=False).agg(MinWeekItem=(RELATICE_WEEK_COLUMN, MIN_VALUE))
        print_df(df_ConstTypeItem, 'Step3 by 2.1 ____ df_ConstTypeItem')

        # 2.2 df_ConstTypeL5 create
        df_ConstTypeL5 = df_in_ConstTypeL5[df_in_ConstTypeL5[MTRL_CONSTTYPE_L5_W_TYPE_COLUMN] == SOFT_VALUE].groupby(
            ITEM_METRIAL_MSL5_COLUMN, as_index=False).agg(MinWeekMSL5=(RELATICE_WEEK_COLUMN, MIN_VALUE))
        print_df(df_ConstTypeL5, 'Step3 by 2.2 ____ df_ConstTypeL5')

        # 2.3 df_ConstTypeL4 create
        df_ConstTypeL4 = df_in_ConstTypeL4[df_in_ConstTypeL4[MTRL_CONSTTYPE_L4_W_TYPE_COLUMN] == SOFT_VALUE].groupby(
            ITEM_METRIAL_MSL4_COLUMN, as_index=False).agg(MinWeekMSL4=(RELATICE_WEEK_COLUMN, MIN_VALUE))
        print_df(df_ConstTypeL4, 'Step3 by 2.3 ____ df_ConstTypeL4')

        # 2.4 df_ConstTypeL3 create
        df_ConstTypeL3 = df_in_ConstTypeL3[df_in_ConstTypeL3[MTRL_CONSTTYPE_L3_W_TYPE_COLUMN] == SOFT_VALUE].groupby(
            ITEM_METRIAL_MSL3_COLUMN, as_index=False).agg(MinWeekMSL3=(RELATICE_WEEK_COLUMN, MIN_VALUE))
        print_df(df_ConstTypeL3, 'Step3 by 2.4 ____ df_ConstTypeL3')

        # 2.5 df_buf_SoftStartWeek create
        df_buf_SoftStartWeek = pd.merge(df_SoftItemBOD, df_ConstTypeItem, how='left', on=[ITEM_METRIAL_COLUMN])
        print_df(df_buf_SoftStartWeek, 'Step3 by 2.5 ____ df_buf_SoftStartWeek .... merge 1')

        df_buf_SoftStartWeek = df_buf_SoftStartWeek.merge(df_ConstTypeL5, how='left', on=[ITEM_METRIAL_MSL5_COLUMN])
        print_df(df_buf_SoftStartWeek, 'Step3 by 2.5 ____ df_buf_SoftStartWeek .... merge 2')

        df_buf_SoftStartWeek = df_buf_SoftStartWeek.merge(df_ConstTypeL4, how='left', on=[ITEM_METRIAL_MSL4_COLUMN])
        print_df(df_buf_SoftStartWeek, 'Step3 by 2.5 ____ df_buf_SoftStartWeek .... merge 3')

        df_buf_SoftStartWeek = df_buf_SoftStartWeek.merge(df_ConstTypeL3, how='left', on=[ITEM_METRIAL_MSL3_COLUMN])
        print_df(df_buf_SoftStartWeek, 'Step3 by 2.5 ____ df_buf_SoftStartWeek .... merge 4')

        # 2.6 df_SoftStartWeek create
        df_SoftStartWeek = df_buf_SoftStartWeek.copy()
        df_SoftStartWeek[INF_LOCATION_COLUMN] = df_SoftStartWeek[LOCATION_COLUMN] + '@INF'

        # 조건에 따라 soft_start_week 설정
        df_SoftStartWeek.loc[df_SoftStartWeek[ITEM_METRIAL_COLUMN].notnull(), SOFT_START_WEEK_COLUMN] = (df_SoftStartWeek)[MIN_WEEK_ITEM_COLUMN]
        df_SoftStartWeek.loc[df_SoftStartWeek[ITEM_METRIAL_MSL5_COLUMN].notnull() & df_SoftStartWeek[
            SOFT_START_WEEK_COLUMN].isnull(), SOFT_START_WEEK_COLUMN] = df_SoftStartWeek[MIN_WEEK_MSL5_COLUMN]
        df_SoftStartWeek.loc[df_SoftStartWeek[ITEM_METRIAL_MSL4_COLUMN].notnull() & df_SoftStartWeek[
            SOFT_START_WEEK_COLUMN].isnull(), SOFT_START_WEEK_COLUMN] = df_SoftStartWeek[MIN_WEEK_MSL4_COLUMN]
        print_df(df_SoftStartWeek, 'Step3 by 2.6 ____ df_SoftStartWeek')

        df_SoftStartWeek = df_SoftStartWeek[[
            VERSION_NAME_COLUMN, ITEM_METRIAL_COLUMN, LOCATION_COLUMN, INF_LOCATION_COLUMN, SUB_LOCATION_COLUMN,
            TRANS_MODE_COLUMN, SOFT_START_WEEK_COLUMN
        ]].drop_duplicates()

        df_SoftStartWeek = df_SoftStartWeek[df_SoftStartWeek[SOFT_START_WEEK_COLUMN].notnull()].copy()
        print_df(df_SoftStartWeek, 'Step3 by 2.6 ____ df_SoftStartWeek .... final')

        # ====================> STEP3 by 2 (End)





        # ====================> STEP3 by 3 (Start) > df_SoftFinal  Set 구성
        df_in_PlanningWeek[TIME_DAY_COLUMN] = pd.to_datetime(df_in_PlanningWeek[TIME_DAY_COLUMN])

        # 3.1 Week by min day
        df_plan_week = df_in_PlanningWeek.groupby(TIME_WEEK_COLUMN)[TIME_DAY_COLUMN].min().reset_index()
        df_plan_week[TIME_DAY_COLUMN] = pd.to_datetime(df_plan_week[TIME_DAY_COLUMN]).dt.strftime("%Y-%m-%d")
        print_df(df_plan_week, 'Step3 by 3.1 ____ df_plan_week .... groupby')

        #   3.1.1 컬럼명 변경
        df_plan_week.rename(columns={TIME_DAY_COLUMN: BOD_ITEM_MTRL_INFINITE_EFF_STARTDATE_COLUMN}, inplace=True)

        #   3.1.2 rank 계산 및 결과 생성
        df_plan_week[TIME_WEEK_COLUMN] = pd.to_numeric(df_plan_week[TIME_WEEK_COLUMN], errors='coerce')
        df_plan_week[RELATIVE_WEEK_COLUMN] = (
                'W' + df_plan_week[TIME_WEEK_COLUMN].rank(method='first').astype(int).astype(str).str.zfill(2)
        )
        print_df(df_plan_week, 'Step3 by 3.1 ____ df_plan_week .... rank result')

        # 3.2 max day
        plan_max_day = df_in_PlanningWeek[TIME_DAY_COLUMN].max()
        note(f'=====> plan_max_day : {plan_max_day}')

        # 3.3 df_SoftFinal create
        df_SoftFinal = pd.merge(df_SoftStartWeek, df_plan_week, how='inner',
                                left_on=[SOFT_START_WEEK_COLUMN], right_on=[RELATIVE_WEEK_COLUMN])
        df_SoftFinal[BOD_ITEM_MTRL_INFINITE_EFF_ENDDATE_COLUMN] = plan_max_day

        df_SoftFinal = df_SoftFinal[[
            VERSION_NAME_COLUMN, ITEM_METRIAL_COLUMN, INF_LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MTRL_INFINITE_EFF_STARTDATE_COLUMN, BOD_ITEM_MTRL_INFINITE_EFF_ENDDATE_COLUMN
        ]].drop_duplicates()


        df_SoftFinal.rename(columns={INF_LOCATION_COLUMN: LOCATION_COLUMN}, inplace=True)
        print_df(df_SoftFinal, 'STEP3 by 3.3 ____ df_SoftFinal .... colunms rename')

        # ====================> STEP3 by 3 (End)

        step('=====> STEP3 End')
        
        
        

        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_out_BODInfinite = rename_and_delete_df(df_SoftFinal)
        df_out_BODInfinite[VERSION_NAME_COLUMN] = paramOutVersion

        step('=====> STEP4 End')
        
        
        

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_BODInfinite, 'output table create .... df_out_BODInfinite', True)

        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODInfinite = pd.DataFrame(columns=df_BODInfinite_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BODInfinite = pd.DataFrame(columns=df_BODInfinite_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')

