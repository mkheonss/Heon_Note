"""
* 프로그램명 
    - PY_MG_InfoRecord

* 내용
    - 자재 BOD 생성용 Info Record 집계

* 변경이력
    - 2024.12.11 / 양희영 / Create
    - 2025.09.18 / 양희영 / Uodate

* Flow Summary
    STEP1. Info Record 중 필요한 메저만 집계 

* Execution 

* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.

* Input Tables
    - df_in_InfoRecord : MG : Mtrl Info Record
                         Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sequence].[Sequence] * [Vendor].[Vendor] * [Partner Vendor].[Partner Vendor] ) on row, 
                         ({ Measure.[Mtrl Info Record_Intransit LT], Measure.[Mtrl Info Record_Plan Del Time], Measure.[Mtrl Info Record_Supplier LT], Measure.[Mtrl Info Record_Valid From], 
                         Measure.[Mtrl Info Record_Valid To], Measure.[Mtrl Info Record_GT Code]}) on column;
    - df_in_BOMComponent : Measure Group : BOM Component
                         Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, 
                         ({Measure.[BOM Comp_Consume Qty], Measure.[BOM Comp_Eff Enddate], Measure.[BOM Comp_Eff Startdate],Measure.[BOM Comp_Valid Flag]}) on column;
    - df_in_PlanDate : Select ([Version].[Version Name]) on row, ({Measure.[W Plan Start Date], Measure.[W Plan End Date]} ) on column;

* Output Tables
    - df_out_InfoRecordCS : MG :  Mtrl Info Record Closing
                            Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] ) on row, 
                                   ({Measure.[Mtrl Info Record_Intransit LT CS], Measure.[Mtrl Info Record_Plan Del Time CS], 
                                    Measure.[Mtrl Info Record_Supplier LT CS], Measure.[Mtrl Info Record_Valid From CS],
                                    Measure.[Mtrl Info Record_Valid To CS]}) on column; 


* 테스트 스크립트
    EXEC plugin instance [PY_MG_InfoRecord] for measures {[Mtrl Info Record_Intransit LT CS]} using scope (&MPV) 
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};

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
from datetime import datetime as dt

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_InfoRecord'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)

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
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====>STEP 0-1 DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    col_VersionVersionName     = 'Version.[Version Name]'
    col_ItemItem               = 'Item.[Item]'
    col_LocationLocation       = 'Location.[Location]'
    col_SubLocationSubLocation = 'Sub Location.[Sub Location]'
    
    col_MtrlInfoRecord_IntransitLT = 'Mtrl Info Record_Intransit LT'
    col_MtrlInfoRecord_PlanDelTime = 'Mtrl Info Record_Plan Del Time'
    col_MtrlInfoRecord_SupplierLT  = 'Mtrl Info Record_Supplier LT'
    col_MtrlInfoRecord_GTCode      = 'Mtrl Info Record_GT Code'
    col_MtrlInfoRecord_ValidFrom   = 'Mtrl Info Record_Valid From'
    col_MtrlInfoRecord_ValidTo     = 'Mtrl Info Record_Valid To'
    
    col_MtrlInfoRecord_IntransitLTCS = 'Mtrl Info Record_Intransit LT CS'
    col_MtrlInfoRecord_PlanDelTimeCS = 'Mtrl Info Record_Plan Del Time CS'
    col_MtrlInfoRecord_SupplierLTCS  ='Mtrl Info Record_Supplier LT CS'
    col_MtrlInfoRecord_ValidFromCS   = 'Mtrl Info Record_Valid From CS'
    col_MtrlInfoRecord_ValidToCS     = 'Mtrl Info Record_Valid To CS'
    
    col_WPlanStartDate = 'W Plan Start Date'
    col_WPlanEndDate   = 'W Plan End Date'
    
    # 칼럼 List 설정
    col_list_I_L    = [col_VersionVersionName, col_ItemItem, col_LocationLocation]
    col_list_group  = [col_VersionVersionName, col_ItemItem, col_LocationLocation, col_SubLocationSubLocation]
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_InfoRecord = read_csv_file("df_in_InfoRecord")
        df_in_BOMComponent = read_csv_file("df_in_BOMComponent")
        df_in_PlanDate = read_csv_file("df_in_PlanDate")
    
    # if df_in_InfoRecord.empty:
    #    raise Exception("=====> raise Exception: df_in_InfoRecord is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
       
    # DATA TYPE 설정
    
    # PANDAS 지원되는 일자 : 1697년 9월 21일 ~ 2262년 4월 11일
    def replace_date(date_string, rtn_type):
        max_date = dt.strptime("2262-04-11", '%Y-%m-%d')
        
        date_string = str(date_string)
        
        if date_string != 'nan':
            try:
                date_object = dt.strptime(date_string, '%m/%d/%Y %I:%M:%S %p')
            except Exception as e1:
                try:
                    date_object = dt.strptime(date_string, '%Y-%m-%d')
                except Exception as e2:
                    date_object = dt.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            
            if date_object > max_date:
                return_date = max_date
            else:
                return_date = date_object
            
            return return_date.strftime(rtn_type)
    
    
    # -------------------------------------------------------------------------------------    
    
    print_df(df_in_InfoRecord, 'df_in_InfoRecord org',False)
    
    if df_in_InfoRecord[col_MtrlInfoRecord_ValidFrom].dtype != 'datetime64[ns]':
        df_in_InfoRecord[col_MtrlInfoRecord_ValidFrom] = pd.to_datetime(df_in_InfoRecord[col_MtrlInfoRecord_ValidFrom],
                                                                    format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_InfoRecord[col_MtrlInfoRecord_ValidTo].dtype != 'datetime64[ns]':
        # 2262년 4월 11일 보다 큰일자 2262년 4월 11일 로 치환
        df_in_InfoRecord[col_MtrlInfoRecord_ValidTo] = np.where(df_in_InfoRecord[col_MtrlInfoRecord_ValidTo].isna(),
                    df_in_InfoRecord[col_MtrlInfoRecord_ValidTo],
                    df_in_InfoRecord[col_MtrlInfoRecord_ValidTo].apply(lambda x: replace_date(x, '%m/%d/%Y %I:%M:%S %p'))
                    )
        df_in_InfoRecord[col_MtrlInfoRecord_ValidTo] = pd.to_datetime(df_in_InfoRecord[col_MtrlInfoRecord_ValidTo],
                                                                  format='%m/%d/%Y %I:%M:%S %p')
        
    if df_in_PlanDate[col_WPlanStartDate].dtype != 'datetime64[ns]':
        df_in_PlanDate[col_WPlanStartDate] = pd.to_datetime(df_in_PlanDate[col_WPlanStartDate], format='%m/%d/%Y %I:%M:%S %p')
    
    if df_in_PlanDate[col_WPlanEndDate].dtype != 'datetime64[ns]':
        df_in_PlanDate[col_WPlanEndDate] = pd.to_datetime(df_in_PlanDate[col_WPlanEndDate], format='%m/%d/%Y %I:%M:%S %p')

    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    print_df(df_in_InfoRecord, 'df_in_InfoRecord',False)
    print_df(df_in_BOMComponent, 'df_in_BOMComponent',False)
    print_df(df_in_PlanDate, 'df_in_PlanDate',False)
    
    step('=====> STEP 0-3 : Input table load End')    
        
    ################################################################################################################
    # STEP 1 : df_BOMItem 구성
    ################################################################################################################
    step('=====> STEP 1-1 : df_BOMItem Create')
    
    df_BOMItem = df_in_BOMComponent[col_list_I_L].copy()
    del df_in_BOMComponent
    df_BOMItem.drop_duplicates(inplace=True)
    df_BOMItem.rename(columns={col_LocationLocation:col_SubLocationSubLocation}, inplace=True)
    print_df(df_BOMItem, 'df_BOMItem',False)
    
    step('=====> STEP 1-2 : df_BOMItem Create End')
    
    ################################################################################################################
    # STEP 2 :  유효한 Info Record Set 구성 : df_ValidInfo
    ################################################################################################################
    step('=====> STEP 2-1 : df_ValidInfo Create')

    #df_in_InfoRecord = df_in_InfoRecord.astype({col_MtrlInfoRecord_GTCode: 'str'}, copy=True)    
    df_ValidInfo = df_in_InfoRecord.merge(df_in_PlanDate, on=[col_VersionVersionName], how='inner')
    
    # Location, // To Location                   > [Sub Location].[Sub Location]
    # Mtrl Info Record_GT Code, // From Location > [Location].[Location]
    df_ValidInfo.rename(columns={col_LocationLocation: col_SubLocationSubLocation,
                                 col_MtrlInfoRecord_GTCode: col_LocationLocation}, inplace=True)
    print_df(df_ValidInfo, 'df_ValidInfo 1',False)
    
        
    df_ValidInfo = df_ValidInfo[(df_ValidInfo[col_MtrlInfoRecord_ValidFrom] <= df_ValidInfo[col_WPlanEndDate]) &
                                (df_ValidInfo[col_MtrlInfoRecord_ValidTo] >= df_ValidInfo[col_WPlanStartDate])]
    
    print_df(df_ValidInfo, 'df_ValidInfo 2',False)
    
    df_ValidInfo = df_ValidInfo.groupby(col_list_group, as_index=False).agg({col_MtrlInfoRecord_IntransitLT: "max", 
                                                                              col_MtrlInfoRecord_PlanDelTime: "max",
                                                                              col_MtrlInfoRecord_SupplierLT: "max",
                                                                              col_MtrlInfoRecord_ValidFrom: "max",
                                                                              col_MtrlInfoRecord_ValidTo: "max"
                                                                              }, skipna = True).copy()
   
    df_ValidInfo.rename(columns={col_MtrlInfoRecord_IntransitLT:col_MtrlInfoRecord_IntransitLTCS,
                                  col_MtrlInfoRecord_PlanDelTime:col_MtrlInfoRecord_PlanDelTimeCS,
                                  col_MtrlInfoRecord_SupplierLT:col_MtrlInfoRecord_SupplierLTCS,
                                  col_MtrlInfoRecord_ValidFrom:col_MtrlInfoRecord_ValidFromCS,
                                  col_MtrlInfoRecord_ValidTo:col_MtrlInfoRecord_ValidToCS}, inplace=True)
    
    print_df(df_ValidInfo, 'df_ValidInfo 3',False)
    
    step('=====> STEP 2-2 : df_ValidInfo Create End')
    
    ################################################################################################################
    # STEP 3 :  유효한 Closing Info Set 구성 : df_ValidInfoFinal
    ################################################################################################################
    step('=====> STEP 3-1 : df_ValidInfoFinal Create 1')
    
    df_ValidInfoFinal = df_ValidInfo.merge(df_BOMItem, 
                                           on=[col_VersionVersionName,col_ItemItem,col_SubLocationSubLocation],
                                           how='inner')
    
    print_df(df_ValidInfoFinal, 'df_ValidInfoFinal',False)
    step('=====> STEP 3-2 : df_ValidInfoFinal Create End')
    
    ################################################################################################################
    # STEP 4 :  최종 Final Set 구성
    ################################################################################################################
    step('=====> STEP 4-1 : Final Set Create 1')
    
    # not exists ( select 'x' from df_ValidInfoFinal z where z.item = a.item and a.sublocation = z.sublocation)
    df_unvaliditem  = df_BOMItem[
                               ~df_BOMItem.set_index([col_ItemItem, col_SubLocationSubLocation]).index.isin(
                                df_ValidInfoFinal.set_index([col_ItemItem, col_SubLocationSubLocation]).index)].copy()
    
    print_df(df_unvaliditem, 'df_unvaliditem',False)
        
    # where exist ( select 'x' from unvaliditem z where a.item = z.item and a.location = z.sublocation)
    df_InfoRecordCS = df_in_InfoRecord[
                                df_in_InfoRecord.set_index([col_ItemItem, col_LocationLocation]).index.isin(
                                df_unvaliditem.set_index([col_ItemItem, col_SubLocationSubLocation]).index)].copy()
    
    # Rank() over (partition by a.Item, a.Location,a.Mtrl Info Record_GT Code
    #        order by a.Mtrl Info Record_GT Code, a.Mtrl Info Record_Valid From desc, a.Mtrl Info Record_Valid To desc
    # 정렬 후 groupby 별로 RN 생성
    col_list_I_L_GT = [col_VersionVersionName, col_ItemItem, col_LocationLocation, col_MtrlInfoRecord_GTCode]
    df_InfoRecordCS.sort_values(by=[col_VersionVersionName, 
                                    col_ItemItem, 
                                    col_LocationLocation,
                                    col_MtrlInfoRecord_GTCode, 
                                    col_MtrlInfoRecord_ValidFrom, 
                                    col_MtrlInfoRecord_ValidTo],
                         ascending=[True, True, True, True, False, False], axis=0, inplace=True)
    
    df_InfoRecordCS['RN'] = 1
    df_InfoRecordCS['RN'] = df_InfoRecordCS.groupby(col_list_I_L_GT)['RN'].cumsum()
    
    print_df(df_InfoRecordCS, 'df_InfoRecordCS 1',False)
    
    df_InfoRecordCS = df_InfoRecordCS[df_InfoRecordCS['RN'] == 1]
    
    # Location, // To Location                   > [Sub Location].[Sub Location]
    # Mtrl Info Record_GT Code, // From Location > [Location].[Location]
    df_InfoRecordCS.rename(columns={col_LocationLocation: col_SubLocationSubLocation,
                                    col_MtrlInfoRecord_GTCode:col_LocationLocation,
                                    col_MtrlInfoRecord_IntransitLT: col_MtrlInfoRecord_IntransitLTCS,
                                    col_MtrlInfoRecord_PlanDelTime: col_MtrlInfoRecord_PlanDelTimeCS,
                                    col_MtrlInfoRecord_SupplierLT: col_MtrlInfoRecord_SupplierLTCS,
                                    col_MtrlInfoRecord_ValidFrom: col_MtrlInfoRecord_ValidFromCS,
                                    col_MtrlInfoRecord_ValidTo: col_MtrlInfoRecord_ValidToCS}, inplace=True)
     
    #칼럼정리
    df_InfoRecordCS = df_InfoRecordCS[[col_VersionVersionName,col_ItemItem,col_LocationLocation,col_SubLocationSubLocation,
                                       col_MtrlInfoRecord_IntransitLTCS, col_MtrlInfoRecord_PlanDelTimeCS, col_MtrlInfoRecord_SupplierLTCS, 
                                       col_MtrlInfoRecord_ValidFromCS, col_MtrlInfoRecord_ValidToCS]]
    
    print_df(df_InfoRecordCS, 'df_InfoRecordCS',False)
    
    step('=====> STEP 4-2 : Final Set Create End')
    
    ################################################################################################################
    # STEP 5 : output table create
    ################################################################################################################
    step('=====> STEP 5-1 : Final output table create')
        
    # out Data 생성 :
    df_out_InfoRecordCS = df_InfoRecordCS.copy()
    del df_InfoRecordCS
    
    # 버전 처리
    #df_out_InfoRecordCS[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_InfoRecordCS.shape
    note(f'=====> Final df_out_InfoRecordCS rows : {row_count}, column : {col_count}')
    print_df(df_out_InfoRecordCS, 'df_out_InfoRecordCS',False)
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_InfoRecordCS, 'df_out_InfoRecordCS')
        
    step('=====> STEP 5-2 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_InfoRecordCS = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()