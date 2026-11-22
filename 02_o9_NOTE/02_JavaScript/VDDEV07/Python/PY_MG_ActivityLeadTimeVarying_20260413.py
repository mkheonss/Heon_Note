"""
* 프로그램명
    - PY_MG_ActivityLeadTimeVarying

* 내용
    - [Basic Input] MP Engine 수행을 위한 Distribution Network Data Input
    - MP Plan Batch Procedure에서 Call 하는 Program
    - ITEM, BODLane(Transport Mode) 기준 Time Varying Priority, Transit Time, Shipping Lead Time 정보 반영
    - 기존 메저는 Batch Procedure에서 Delete

* 변경이력
    - 2024.08.20 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemSiteAsn  : Select (Version.[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) on column.filter(Measure.[Item Site Asn_Engine Flag] == true);
    - df_in_BODItemW     : Select (Version.[Version Name] * [Item].[Item] * &PlanningHorizon * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item W_Prty], Measure.[BOD Item W_Shipment LT], Measure.[BOD Item W_BOD LT]}) on column;
    - df_in_BODListMtrlW : Select (Version.[Version Name] * &PlanningHorizon * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl W_Total LT]}) on column.filter(Measure.[BOD List Mtrl W_Total LT] > 0);
    - df_in_BODItemMtrlW : Select (Version.[Version Name] * &PlanningHorizon * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl W_Total LT]}) on column.filter(Measure.[BOD Item Mtrl W_Total LT] > 0);
    - df_in_BODItemMtrlFull : Select (Version.[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_MSL3]}) on column;

* Flow Summary
    - STEP1. Plan 대상 SET / LCM BOD Time Phased Transit Time 정보 Insert
    - STEP2. Plan 대상 Material Time Phased Transit Time 정보 Insert

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_LeadTimeVarying

* 데이타 초기화
    - DELETE DATA FOR MODEL [001.49W Activity Lead Time Time Varying] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - exec plugin instance [PY_MG_ActivityLeadTimeVarying] for Measures{[W Activity Lead Time Time Varying]} using scope (&MPV * &PlanningHorizon * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3]) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - Select (&MPV * [Time].[Week] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Lead Time Time Varying]}) on column;

;

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
str_instance = 'PY_MG_ActivityLeadTimeVarying'
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
            df_in_BODItemW = read_csv_file("df_in_BODItemW")
            df_in_BODListMtrlW = read_csv_file("df_in_BODListMtrlW")
            df_in_BODItemMtrlW = read_csv_file("df_in_BODItemMtrlW")
            df_in_BODItemMtrlFull = read_csv_file("df_in_BODItemMtrlFull")
    
    
        print_df(df_in_ItemSiteAsn, 'input table load .... df_in_ItemSiteAsn')
        print_df(df_in_BODItemW, 'input table load .... df_in_BODItemW')
        print_df(df_in_BODListMtrlW, 'input table load .... df_in_BODListMtrlW')
        print_df(df_in_BODItemMtrlW, 'input table load .... df_in_BODItemMtrlW')
        print_df(df_in_BODItemMtrlFull, 'input table load .... df_in_BODItemMtrlFull')

        step('=====> STEP1 End')


    
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')
    
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
    
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        ITEM_COLUMN = 'Item.[Item]'
    
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        MSL3_COLUMN = 'Item Material.[MSL3]'
    
        BOD_ITEM_W_PRTY_COLUMN = 'BOD Item W_Prty'
        BOD_ITEM_W_SHIPMENT_LT_COLUMN = 'BOD Item W_Shipment LT'
        BOD_ITEM_W_BOD_LT_COLUMN = 'BOD Item W_BOD LT'
    
        ACTIVITY1_COLUMN = 'Activity1.[Activity1]'
        ACTIVITY2_COLUMN = 'Activity2.[Activity2]'
        ACTIVITY3_COLUMN = 'Activity3.[Activity3]'
        W_ACTIVITY_LEAD_TIME_VARYING_COLUMN = 'W Activity Lead Time Time Varying'
        W_ACTIVITY_MANDATORY_OFFSET_TIME_VARYING_COLUMN = 'W Activity Mandatory Offset Time Varying'
    
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN = 'BOD Item Mtrl W_Factory Out'
        BOD_ITEM_MTRL_W_GR_LT_COLUMN = 'BOD Item Mtrl W_GR LT'
        BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN = 'BOD Item Mtrl W_Intransit LT'
        BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN = 'BOD Item Mtrl W_Port To Port'
        BOD_ITEM_MTRL_W_SUPPLIER_COLUMN = 'BOD Item Mtrl W_Supplier'
        BOD_ITEM_MTRL_W_TOTAL_LT_COLUMN = 'BOD Item Mtrl W_Total LT'
        BOD_ITEM_DETAIL_W_FACTORY_OUT_COLUMN = 'Mtrl BOD Detail W_Factory Out'
        BOD_ITEM_DETAIL_W_GR_LT_COLUMN = 'Mtrl BOD Detail W_GR LT'
        BOD_ITEM_DETAIL_W_INTRANSIT_LT_COLUMN = 'Mtrl BOD Detail W_Intransit LT'
        BOD_ITEM_DETAIL_W_PORT_TO_PORT_COLUMN = 'Mtrl BOD Detail W_Port To Port'
        BOD_ITEM_DETAIL_W_SUPPLIER_COLUMN = 'Mtrl BOD Detail W_Supplier'
        BOD_ITEM_DETAIL_W_TOTAL_LT_COLUMN = 'Mtrl BOD Detail W_Total LT'
    
        BOD_LIST_MTRL_W_TOTAL_LT_COLUMN = 'BOD List Mtrl W_Total LT'
        BOD_ITEM_MTRL_FULL_EFF_ENDDATE_COLUMN = 'BOD Item Mtrl Full_EFF Enddate'
        BOD_ITEM_MTRL_FULL_EFF_STARTDATE_COLUMN = 'BOD Item Mtrl Full_EFF Startdate'
        BOD_ITEM_MTRL_FULL_FLAG_COLUMN = 'BOD Item Mtrl Full_Flag'
        BOD_ITEM_MTRL_FULL_MSL3_COLUMN = 'BOD Item Mtrl Full_MSL3'

        df_BODItem_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN,
            W_ACTIVITY_LEAD_TIME_VARYING_COLUMN, W_ACTIVITY_MANDATORY_OFFSET_TIME_VARYING_COLUMN
        ]

        df_BODItemMtrl_columns = [
            VERSION_NAME_COLUMN, TIME_WEEK_COLUMN, ACTIVITY1_COLUMN, ACTIVITY2_COLUMN, ACTIVITY3_COLUMN,
            W_ACTIVITY_LEAD_TIME_VARYING_COLUMN
        ]
    
        step('=====> STEP2 End')



    
        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
    
        # Location 만 발췌, 중복값 삭제(Location Distinct) 및 미사용 컬럼 삭제
        drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [LOCATION_COLUMN]]
        df_ItemSiteAsnLocation = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[LOCATION_COLUMN], keep='first')
    
        # Item 만 발췌, 중복값 삭제(Item Distinct) 및 미사용 컬럼 삭제
        drop_column = [col for col in list(df_in_ItemSiteAsn.columns) if col not in [ITEM_COLUMN]]
        df_ItemSiteAsnItem = df_in_ItemSiteAsn.drop(labels=drop_column, axis=1, inplace=False).drop_duplicates(
            subset=[ITEM_COLUMN], keep='first')
    

        # ====================> STEP3 by 1 (Start) -> SET / LCM BOD Time Phased Transit Time 정보 구성
        #   1.1 ItemSiteAsn 의 Location 이 df_in_BODItemW 의 Location 또는 Sub Location 에 속하는 데이터 추출
        df_BODLocation = df_in_BODItemW[df_in_BODItemW[LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN]) |
                                        df_in_BODItemW[SUB_LOCATION_COLUMN].isin(df_ItemSiteAsnLocation[LOCATION_COLUMN])]
        print_df(df_BODLocation, 'STEP3 by 1.1 _____ df_BODLocation .... filter')
    
        #   1.2 ItemSiteAsn 의 Item 이 df_BODLocation 의 Item 에 속하는 데이터 추출
        df_BODItem = df_BODLocation[df_BODLocation[ITEM_COLUMN].isin(df_ItemSiteAsnItem[ITEM_COLUMN])]
        print_df(df_BODItem, 'STEP3 by 1.2 _____ df_BODItem .... filter')

        #   1.3 BODItem 설정
        #       1.3.1 Activity1 설정
        df_BODItem = df_BODItem.copy()  # 복사본 생성
        try:
            df_BODItem[ACTIVITY1_COLUMN] = (
                    df_BODItem[LOCATION_COLUMN] + "_" +
                    df_BODItem[SUB_LOCATION_COLUMN] + "_" +
                    df_BODItem[TRANS_MODE_COLUMN]
            )
        except Exception as ex:
            df_BODItem[ACTIVITY1_COLUMN] = None


        #       1.3.2 컬럼명 변경
        df_BODItem.rename(columns={
            TRANS_MODE_COLUMN: ACTIVITY2_COLUMN,
            ITEM_COLUMN: ACTIVITY3_COLUMN,
            BOD_ITEM_W_BOD_LT_COLUMN: W_ACTIVITY_LEAD_TIME_VARYING_COLUMN,
            BOD_ITEM_W_SHIPMENT_LT_COLUMN: W_ACTIVITY_MANDATORY_OFFSET_TIME_VARYING_COLUMN,
        }, inplace=True)

        #       1.3.3 필요컬럼 발췌
        df_BODItem = df_BODItem[df_BODItem_columns]
        print_df(df_BODItem, 'STEP3 by 1.3.3 _____ df_BODItem .... filter')

        # ====================> STEP3 by 1 (End)
    
    
    
        # ====================> STEP3 by 2 (Start) -> Material Time Phased Transit Time 정보 Insert

        # 2.1 df_in_BODItemMtrlFull > 'BOD Item Mtrl Full_Flag'  값이 'Header','Detail' 인 데이터 copy
        df_BODItemMtrlFullHeader = df_in_BODItemMtrlFull[df_in_BODItemMtrlFull[BOD_ITEM_MTRL_FULL_FLAG_COLUMN] == 'Header'].copy()
        df_BODItemMtrlFullDetail = df_in_BODItemMtrlFull[df_in_BODItemMtrlFull[BOD_ITEM_MTRL_FULL_FLAG_COLUMN] == 'Detail'].copy()
    
        # 2.2 df_BODItemMtrlFullHeader, df_in_BODListMtrlW join
        df_buf_BODItemMtrl1 = pd.merge(df_BODItemMtrlFullHeader, df_in_BODListMtrlW, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, BOD_ITEM_MTRL_FULL_MSL3_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, MSL3_COLUMN])
        print_df(df_buf_BODItemMtrl1, 'STEP3 by 2.2 _____ df_buf_BODItemMtrl1 .... mrege[df_BODItemMtrlFullHeader, df_in_BODListMtrlW]')
    
        # 2.3 df_BODItemMtrlFullDetail, df_in_BODItemMtrlW join
        df_buf_BODItemMtrl2 = pd.merge(df_BODItemMtrlFullDetail, df_in_BODItemMtrlW, how='inner',
                                       left_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN],
                                       right_on=[VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN])
        print_df(df_buf_BODItemMtrl2, 'STEP3 by 2.3 _____ df_buf_BODItemMtrl2 .... merge[df_BODItemMtrlFullDetail, df_in_BODItemMtrlW]')
    
        # 2.4 df_buf_BODItem create
        df_BODItemMtrl = pd.concat([df_buf_BODItemMtrl1, df_buf_BODItemMtrl2], axis=0, ignore_index=True).drop_duplicates()
        print_df(df_BODItemMtrl, 'STEP3 by 2.4 _____ df_BODItemMtrl')

        #   2.4.1 Activity1 설정
        df_BODItemMtrl = df_BODItemMtrl.copy()  # 복사본 생성
        try:
            df_BODItemMtrl[ACTIVITY1_COLUMN] = (
                    df_BODItemMtrl[LOCATION_COLUMN] + "_" +
                    df_BODItemMtrl[SUB_LOCATION_COLUMN] + "_" +
                    df_BODItemMtrl[TRANS_MODE_COLUMN]
            )
        except Exception as ex:
            df_BODItem[ACTIVITY1_COLUMN] = None

        #   2.4.2 컬럼명 변경
        df_BODItemMtrl.rename(columns={
            TRANS_MODE_COLUMN: ACTIVITY2_COLUMN,
            ITEM_METERIAL_COLUMN: ACTIVITY3_COLUMN,
            BOD_LIST_MTRL_W_TOTAL_LT_COLUMN: W_ACTIVITY_LEAD_TIME_VARYING_COLUMN,
        }, inplace=True)

        #   2.4.3 필요컬럼 발췌
        df_BODItemMtrl = df_BODItemMtrl[df_BODItemMtrl_columns]
        print_df(df_BODItemMtrl, 'STEP3 by 2.4.3 _____ df_BODItemMtrl .... filter')

        # ====================> STEP3 by 2 (End)

        step('=====> STEP3 End')


    
        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        df_out_LeadTimeVarying = pd.concat([df_BODItem, df_BODItemMtrl], axis=0, ignore_index=True).drop_duplicates()
        df_out_LeadTimeVarying[VERSION_NAME_COLUMN] = paramOutVersion
    
        step('=====> STEP4 End')


    
        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        print_df(df_out_LeadTimeVarying, 'output table create .... df_out_LeadTimeVarying', True)
        
        step('=====> STEP5 End')

        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
        tracemalloc.stop()

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_LeadTimeVarying = pd.DataFrame(columns=df_BODItem_columns)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_LeadTimeVarying = pd.DataFrame(columns=df_BODItem_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        vd_log_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()
        step('=====> Batch end')
