"""
* 프로그램명
    - PY_MG_ItemLocation

* 내용
    - MP Engine 수행을 위한 Item - Location Association I/F
    - Plan 대상 Item Site Association (Measure Group : Item Site Asn) 에서 실제 현재 PLAN 대상에 대한 Item - Location Association 만 반영
    - 가상 Infinite ITEM/Location 반영

* 변경이력
    - 2024.06.18 / 권태우 / Create
    - 2024.09.23 / 권태우 / STEP2 추가

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn  : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_INFSiteAsn : Select (Version.[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Infinite_EFF Enddate], Measure.[BOD Item Mtrl Infinite_EFF Startdate]}) on column;


* 주요 Logic ( Data 처리 )
    - STEP1 : Item Site Asn 에서 Item Site Asn_Engine Flag == true 인 대상만 Item Location Solver Input 반영
              Measure.[W Item Location Association = 1 로 Insert

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_ItemLocation

* 데이타 초기화
    - DELETE DATA FOR MODEL [014.002W Network Intermediate Item Location Details] where {Version.[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_MG_ItemLocation] for measures {[W Item Location Association]} using scope (&CWV) using arguments {(ExecutionMode, "LightWeight"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")

* Output Query
    - Select ([Version].[Version Name].[CWV_MP]  * [Item].[Item] * [Location].[Location] ) on row, ({ Measure.[W Item Location Association]}) on column;

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
str_instance = 'PY_MG_ItemLocation'
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
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")
            df_in_INFSiteAsn = read_csv_file("df_in_INFSiteAsn")
    
    
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_INFSiteAsn, 'input table load .... df_in_INFSiteAsn')
    
        step('=====> STEP1 End')
        
        
    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        ITEM_COLUMN = 'Item.[Item]'
        W_ITEM_LOCATION_ASSOCIATION_COLUMN = 'W Item Location Association'
    
        ITEM_SITE_ASN_CUR_STATUS_COLUMN = 'Item Site Asn_Cur Status'
        ITEM_SITE_ASN_ENGINE_FLAG_COLUMN = 'Item Site Asn_Engine Flag'
        ITEM_SITE_ASN_ITEM_GRP_COLUMN = 'Item Site Asn_Item Grp'
        ITEM_SITE_ASN_SALES_PROD_ASN_COLUMN = 'Item Site Asn_Sales Prod Asn'
        ITEM_SITE_ASN_STAGE_COLUMN = 'Item Site Asn_Stage'
    
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        BOD_ITEM_MTRL_INFINITE_EFF_ENDDATE_COLUMN = 'BOD Item Mtrl Infinite_EFF Enddate'
        BOD_ITEM_MTRL_INFINITE_EFF_STARTDATE_COLUMN = 'BOD Item Mtrl Infinite_EFF Startdate'

        df_ItemLocation_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, ITEM_COLUMN, W_ITEM_LOCATION_ASSOCIATION_COLUMN
        ]

        step('=====> STEP2 End')



    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # ====================> STEP3 by 1 (Start) -> Item Site Asn > Item Location Solver Input 반영

        # 컬럼 설정
        df_in_ItemSiteAsn[W_ITEM_LOCATION_ASSOCIATION_COLUMN] = 1
    
        # 컬럼 재정렬 및 불필요 컬럼 삭제
        df_in_ItemSiteAsn = df_in_ItemSiteAsn.drop(labels=[
            ITEM_SITE_ASN_CUR_STATUS_COLUMN, ITEM_SITE_ASN_ENGINE_FLAG_COLUMN, ITEM_SITE_ASN_ITEM_GRP_COLUMN,
            ITEM_SITE_ASN_SALES_PROD_ASN_COLUMN, ITEM_SITE_ASN_STAGE_COLUMN,
        ], axis=1).drop_duplicates()
        print_df(df_in_ItemSiteAsn, 'STEP3 by 1.1 ____ df_in_ItemSiteAsn .... final')

        # ====================> STEP3 by 1 (End)
    
    
    
    
        # ====================> STEP3 by 2 (Start) -> INF Site Asn > Item Location Solver Input 반영

        # 컬럼 설정
        df_in_INFSiteAsn[W_ITEM_LOCATION_ASSOCIATION_COLUMN] = 1
    
        # 컬럼 재정렬 및 불필요 컬럼 삭제
        df_in_INFSiteAsn = df_in_INFSiteAsn.drop(labels=[
            SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, BOD_ITEM_MTRL_INFINITE_EFF_STARTDATE_COLUMN, BOD_ITEM_MTRL_INFINITE_EFF_ENDDATE_COLUMN,
        ], axis=1).drop_duplicates()
    
        df_in_INFSiteAsn.rename(columns={ITEM_METERIAL_COLUMN: ITEM_COLUMN}, inplace=True)
        print_df(df_in_INFSiteAsn, 'STEP3 by 2.1 ____ df_in_INFSiteAsn .... final')

        # ====================> STEP3 by 2 (End)
    
        step('=====> STEP3 End')



    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')
    
        # df_ItemLocation 생성
        df_out_ItemLocation = pd.concat([df_in_ItemSiteAsn, df_in_INFSiteAsn]).drop_duplicates()
    
        # 버전 처리
        df_out_ItemLocation[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')



    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
    
        print_df(df_out_ItemLocation, 'output table create .... df_out_ItemLocation', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ItemLocation = pd.DataFrame(columns=df_ItemLocation_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_ItemLocation = pd.DataFrame(columns=df_ItemLocation_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
