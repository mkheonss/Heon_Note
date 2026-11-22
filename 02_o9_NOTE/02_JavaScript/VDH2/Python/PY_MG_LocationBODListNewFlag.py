"""
* 프로그램명
    - PY_MG_LocationBODListNewFlag

* 내용
    - BOD Item Measure Group 생성을 위한 Program

* 변경이력
    - 2025.05.07 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_NewBODList  : Select (&MFlocation * &SubLocationDC) on row where {[Version].[Version Name], (Measure.[BOD List_BOD Valid]=="Y" && Measure.[BOD List_is New Flag]==true )};

* Flow Summary

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_NewBODLocation

* 데이타 초기화
    -

* RUN 스크립트
    - EXEC plugin instance [PY_MG_LocationBODListNewFlag] for Measures {[Location_BOD List_is New Flag]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
    - Select (&MPV * [Location].[Location] ) on row, ({Measure.[Location Name], Measure.[Location_BOD List_is New Flag], Measure.[Location_Company Name Override], Measure.[Location_Item Site Asn_Daily Change Flag], Measure.[Location_JDM Type], Measure.[Location_Location Valid Flag Ovr], Measure.[Location_MF Site Stage], Measure.[Location_Vendor HQ Flag], Measure.[Location_isMtrlBODMgmt_Flag]}) on column;

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
str_instance = 'PY_MG_LocationBODListNewFlag'
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
            df_in_NewBODList = read_csv_file("df_in_NewBODList")


        print_df(df_in_NewBODList, 'input table load .... df_in_NewBODList')

        step('=====> STEP1 End')



    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        # 컬럼 변수 선언
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        LOCATION_BOD_LIST_IS_NEW_FLAG_COLUMN = 'Location_BOD List_is New Flag'

        df_LocationBODNewFlagList_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, LOCATION_BOD_LIST_IS_NEW_FLAG_COLUMN,
        ]

        step('=====> STEP2 End')



    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_NewBODList.empty:
            raise CustomException("STEP3 .... df_in_NewBODList 값이 없습니다.")


        # ====================> STEP3 by 1 (Start) -> BOD List 발췌 기준으로 Item Site Asn 조합하여 BOD Item 을 구성한다.

        df_in_NewBODList = df_in_NewBODList[[LOCATION_COLUMN, SUB_LOCATION_COLUMN]].drop_duplicates()
        df_BODNewFlagLocationList = df_in_NewBODList[[LOCATION_COLUMN]].copy().drop_duplicates()
        print_df(df_BODNewFlagLocationList, 'SETP3 by 1.1 _____ df_BODNewFlagLocationList .... final')

        df_BODNewFlagSubLocationList = df_in_NewBODList[[SUB_LOCATION_COLUMN]].copy().drop_duplicates()
        df_BODNewFlagSubLocationList.rename(columns={SUB_LOCATION_COLUMN: LOCATION_COLUMN}, inplace=True)
        print_df(df_BODNewFlagSubLocationList, 'SETP3 by 1.2 _____ df_BODNewFlagSubLocationList .... final')

        # ====================> STEP3 by 1 (End)

        step('=====> STEP3 End')
        
        
    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        df_out_NewBODLocation = pd.concat([df_BODNewFlagLocationList, df_BODNewFlagSubLocationList]).drop_duplicates()
        print_df(df_out_NewBODLocation, 'SETP4 by 1 _____ df_out_NewBODLocation .... df concat')

        df_out_NewBODLocation[LOCATION_BOD_LIST_IS_NEW_FLAG_COLUMN] = True
        df_out_NewBODLocation[VERSION_NAME_COLUMN] = paramOutVersion

        df_out_NewBODLocation = df_out_NewBODLocation[df_LocationBODNewFlagList_columns]

        step('=====> STEP4 End')



    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_NewBODLocation, 'output table create .... df_out_NewBODLocation', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_NewBODLocation = pd.DataFrame(columns=df_LocationBODNewFlagList_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_NewBODLocation = pd.DataFrame(columns=df_LocationBODNewFlagList_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
