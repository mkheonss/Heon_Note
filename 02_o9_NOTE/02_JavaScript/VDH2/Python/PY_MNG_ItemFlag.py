"""
* 프로그램명 
    - PY_MNG_ItemFlag

* 내용
    - Item 기준으로 관리되는 Flag 반영

* 변경이력
- 2024.07.26 / 양희영 / Create
- 2025.06.30 / 양희영 / update :  ENGINE FLAG 주석처리(박명화프로요청)
- 2025.10.16 / 양희영 / update

* Input
- df_in_Table = pd.read_csv(' .csv') 

* Flow Summary
    &CWV
    1. GSCM 에서 I/F 받은 Demand 정보를 참조하여 Version/Item별 DMD_Flag 정보를 Update 함
    2. GSCM 에서 I/F 받은 Inventory, Intransit 정보를 참조하여 Version/Item별 INV_Flag 정보를 Update 함
    3. GSCM 에서 I/F 받은 WIP 정보를 참조하여 Version/Item별 WIP_Flag 정보를 Update 함
    4. GSCM 에서 I/F 받은 GR/GI 정보를 참조하여 Version/Item별 Actual Flag 정보를 Update 함
    &MPV
    5. NSCM 에서 관리하는 BOM, BOD 정보를 참조하여 Version/Item별 Prod Flag 정보를 Update 함
    6. NSCM 에서 관리하는 BOM, BOD 정보를 참조하여 Version/Item별 Cons Flag 정보를 Update 함
    7. NSCM 에서 관리하는 Safety Stock 정보를 참조하여 Version/Item별 SS Flag 정보를 Update 함
    8. NSCM 에서 관리하는 구매입고예정 정보를 참조하여 Version/Item별 Supply Plan Flag 정보를 Update 함
    9. DMD_Flag, INV_Flag, WIP_flag, Prod/Cons Flag, SS Flag, Supply Plan Flag 정보를 참조하여 Version/Item별 Engine Flag 정보를 Update 함

* Execution 
* Script Parameter
    - paramOutVersion  : CWV_MP
    - paramCWVersion : CurrentWorkingView
* Input Tables
    - df_in_ItemCWV : Select ([Version].[Version Name] * [Item].[Item]) on row, ({Measure.[Dmd W_ID], Measure.[Inv_Plan ID], Measure.[Intr_BOD Name], Measure.[Dist Order_From Site ID]}) on column;
    - df_in_ItemMPV : Select ([Version].[Version Name] * [Item].[Item]) on row, ({Measure.[New Model Map BOM_BOM Type], Measure.[BOD Item_Priority], Measure.[SS_EOH Week]}) on column;
    - df_in_ItemPlanGroup : select (Item.[Item] * Item.[Plan Group]);

* Output Tables
    - df_out_ItemValidation : Select ([Version].[Version Name] * [Item].[Item] ) on row, 
      ({Measure.[Item Valid_Dmd Flag], Measure.[Item Valid_Inv Flag], Measure.[Item Valid_WIP Flag], Measure.[Item Valid_Actual Flag], Measure.[Item Valid_Prod Flag], Measure.[Item Valid_Cons Flag], 
        Measure.[Item Valid_SS Flag], Measure.[Item Valid_Supply Plan Flag], Measure.[Item Valid_Engine Flag]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MNG_ItemFlag] for Measures {[Item Valid_Actual Flag]} using scope (Version.[Version Name].filter(#.Name in {"CurrentWorkingView", "CWV_MP"})) 
     using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False") , (paramOutVersion , "CWV_MP"), (paramCWVersion , "CurrentWorkingView") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
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
import warnings
warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MNG_ItemFlag'
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
    # DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====> DataFrame Column : 변수 처리')
    # Value 변수 선언
    paramOutVersion_VALUE   = "CWV_MP"
    paramCWVersion_VALUE  = "CurrentWorkingView"
    #vCWV = "CurrentWorkingView"
    
    # 컬럼 변수 선언
    col_VersionVersionName = 'Version.[Version Name]'
    col_ItemItem           = 'Item.[Item]'
    col_ItemPlanGroup      = 'Item.[Plan Group]'
    
    col_DmdW_ID = "Dmd W_ID"
    col_Inv_PlanID = "Inv_Plan ID"
    col_Intr_BODName = "Intr_BOD Name"
    col_DistOrder_FromSiteID = "Dist Order_From Site ID"
    col_NewModelMapBOM_BOMType = "New Model Map BOM_BOM Type"
    col_BODItem_Priority = "BOD Item_Priority"
    col_SS_EOHWeek = 'SS_EOH Week'
    
    col_ItemValid_DmdFlag        = "Item Valid_Dmd Flag"
    col_ItemValid_InvFlag        = "Item Valid_Inv Flag"
    col_ItemValid_WIPFlag        = "Item Valid_WIP Flag"
    col_ItemValid_ActualFlag     = "Item Valid_Actual Flag"
    col_ItemValid_ProdFlag       = "Item Valid_Prod Flag"
    col_ItemValid_ConsFlag       = "Item Valid_Cons Flag"
    col_ItemValid_SSFlag         = "Item Valid_SS Flag"
    col_ItemValid_SupplyPlanFlag = "Item Valid_Supply Plan Flag"
    col_ItemValid_EngineFlag     = "Item Valid_Engine Flag"
    col_ItemValid_PlanGroup      = 'Item Valid_Plan Group'
    
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> 전처리 : 모듈 내에서 사용될 input table load')
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = paramOutVersion_VALUE
        paramCWVersion = paramCWVersion_VALUE
        
        df_in_ItemCWV = read_csv_file("df_in_ItemCWV")
        df_in_ItemMPV = read_csv_file("df_in_ItemMPV")
        df_in_ItemPlanGroup = read_csv_file("df_in_ItemPlanGroup")
    
    # if df_in_ItemCWV.empty:
    #    raise Exception("=====> raise Exception: df_in_ItemCWV is empty")
    
    # if df_in_ItemMPV.empty:
    #    raise Exception("=====> raise Exception: df_in_ItemMPV is empty")
    
    # if df_in_ItemPlanGroup.empty:
    #    raise Exception("=====> raise Exception: df_in_ItemPlanGroup is empty")
    
    # 입력 변수 확인
    if paramOutVersion is None or paramOutVersion.strip() == '':
        paramOutVersion = paramOutVersion_VALUE
        
    if paramCWVersion is None or paramCWVersion.strip() == '':
        paramCWVersion = paramCWVersion_VALUE
        
    # DATA TYPE 설정
    df_in_ItemPlanGroup = df_in_ItemPlanGroup.astype({col_ItemPlanGroup: 'str'}, copy=True)
    
    # input dataframe 확인용 로그
    note(f'=====> paramOutVersion : {paramOutVersion}')
    note(f'=====> paramCWVersion : {paramCWVersion}')
    
    print_df(df_in_ItemCWV, 'df_in_ItemCWV', False)
    print_df(df_in_ItemMPV, 'df_in_ItemMPV', False)
    print_df(df_in_ItemPlanGroup, 'df_in_ItemPlanGroup', False)
    
    step('=====> 전처리 : Input table load End')
    
    ################################################################################################################
    # STEP 0-2 : 추가 df 생성
    ################################################################################################################
    step('=====> STEP 0-2 : 추가 df Create ')
    # Version 분리 : paramCWVersion 용, paramOutVersion 용 ---------------------
    # paramCWVersion -----------------------------------------------------------
    df_in_ItemCWV = df_in_ItemCWV[df_in_ItemCWV[col_VersionVersionName] == paramCWVersion]
    print_df(df_in_ItemCWV, 'df_in_ItemCWV 2', False)
    
    # paramOutVersion -----------------------------------------------------------
    df_in_ItemMPV = df_in_ItemMPV[df_in_ItemMPV[col_VersionVersionName] == paramOutVersion]
    print_df(df_in_ItemMPV, 'df_in_ItemMPV 2', False)
    
    step('=====> STEP 0-3 : 추가 df Create End')
    
    ##############################################################################################################
    # STEP 1 :  CWV Flag 데이터 생성
    ################################################################################################################
    step('=====> STEP 1 : CWV Flag Data Create')
    
    df_CWV_ItemFlag = df_in_ItemCWV.copy()
    del df_in_ItemCWV
    
    df_CWV_ItemFlag[col_ItemValid_DmdFlag] = df_CWV_ItemFlag[col_DmdW_ID].notnull()
    df_CWV_ItemFlag[col_ItemValid_InvFlag] = (df_CWV_ItemFlag[col_Inv_PlanID].notnull() | df_CWV_ItemFlag[col_Intr_BODName].notnull())
    df_CWV_ItemFlag[col_ItemValid_WIPFlag] = df_CWV_ItemFlag[col_DistOrder_FromSiteID].notnull()
    df_CWV_ItemFlag[col_ItemValid_ActualFlag] = False  # GR/GI 정보, 추후개발

    # From Measure 칼럼 삭제
    df_CWV_ItemFlag.drop(columns=[col_DmdW_ID, col_Inv_PlanID, col_Intr_BODName, col_DistOrder_FromSiteID], inplace=True)
    
    print_df(df_CWV_ItemFlag, 'df_CWV_ItemFlag 3', False)
    step('=====> STEP 1-1 : CWV Flag Data Create End')
    
    ################################################################################################################
    # STEP 2 :  MPV Flag 데이터 생성
    ################################################################################################################
    step('=====> STEP 2 : MPV Flag Data Create')
    
    df_MPV_ItemFlag = df_in_ItemMPV.copy()
    del df_in_ItemMPV
    
    df_MPV_ItemFlag[col_ItemValid_ProdFlag] = (df_MPV_ItemFlag[col_NewModelMapBOM_BOMType].notnull() | df_MPV_ItemFlag[col_BODItem_Priority].notnull())
    df_MPV_ItemFlag[col_ItemValid_ConsFlag] = (df_MPV_ItemFlag[col_NewModelMapBOM_BOMType].notnull() | df_MPV_ItemFlag[col_BODItem_Priority].notnull())
    df_MPV_ItemFlag[col_ItemValid_SSFlag]   = df_MPV_ItemFlag[col_SS_EOHWeek].notnull()
    df_MPV_ItemFlag[col_ItemValid_SupplyPlanFlag] = False  # 구매입고예정정보, 추후개발
    
    # From Measure 칼럼 삭제
    df_MPV_ItemFlag.drop(columns=[col_NewModelMapBOM_BOMType, col_BODItem_Priority, col_SS_EOHWeek], inplace=True)
    
    print_df(df_MPV_ItemFlag, 'df_MPV_ItemFlag', False)
    step('=====> STEP 2-1 : MPV Flag Data Create End')    
    
    ################################################################################################################
    # STEP 3 : 전체 Item Flag 데이터 생성
    ################################################################################################################
    step('=====> STEP 3 : 전체 Item Flag Data Create')
    
    # 버전 처리
    df_CWV_ItemFlag[col_VersionVersionName] = paramOutVersion
    df_ALL_ItemFlag = df_CWV_ItemFlag.merge(df_MPV_ItemFlag, on=[col_VersionVersionName, col_ItemItem], how='outer')
    
    df_ALL_ItemFlag.fillna(False, inplace=True)
    '''
    2024.11.13 : 임시막음(박명화프로요청)
    df_ALL_ItemFlag[itemValid_EngineFlag] = (df_ALL_ItemFlag[col_ItemValid_DmdFlag] |
                                             df_ALL_ItemFlag[col_ItemValid_InvFlag] |
                                             df_ALL_ItemFlag[col_ItemValid_WIPFlag] |
                                             df_ALL_ItemFlag[col_ItemValid_ActualFlag] |
                                             df_ALL_ItemFlag[col_ItemValid_ProdFlag] |
                                             df_ALL_ItemFlag[col_ItemValid_ConsFlag] |
                                             df_ALL_ItemFlag[col_ItemValid_SSFlag] |
                                             df_ALL_ItemFlag[col_ItemValid_SupplyPlanFlag]
                                             )
    '''
    # df_ALL_ItemFlag & df_in_ItemPlanGroup Merge
    df_ALL_ItemFlag = df_ALL_ItemFlag.merge(df_in_ItemPlanGroup, on=[col_ItemItem], how='left')
    df_ALL_ItemFlag.rename(columns={col_ItemPlanGroup: col_ItemValid_PlanGroup}, inplace=True)
    
    print_df(df_ALL_ItemFlag, 'df_ALL_ItemFlag', False)
    step('=====> STEP 3-1 : 전체 Item Flag Data Create End')
    del [df_CWV_ItemFlag, df_MPV_ItemFlag]
    
    ################################################################################################################
    # STEP 4 : : output table create
    ################################################################################################################
    step('=====> STEP 4 : Final output table create')
    
    # out Data 생성 :
    #df_out_ItemValidation = df_ALL_ItemFlag.loc[(df_ALL_ItemFlag[itemValid_EngineFlag] == True)].copy()
    df_out_ItemValidation = df_ALL_ItemFlag.copy()
    del df_ALL_ItemFlag
    

    row_count, col_count = df_out_ItemValidation.shape
    note(f'=====> Final df_out_ItemValidation rows : {row_count}, column : {col_count}')
    
    print_df(df_out_ItemValidation, 'df_out_ItemValidation', False)
    step('=====> STEP 4-1 : Final output table create End')
    
    if is_local:
        step('=====> Output CSV create')
        save_csv_file(df_out_ItemValidation, 'df_out_ItemValidation')
            
    step('=====> STEP 4-2 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_ItemValidation = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()