"""
* 프로그램명 
    - PY_MG_MasterValidationWeekly2

* 내용
    - Master Validation Data 구성

* 변경이력
    - 2026.02.06 / 양희영 / Create
    - 2026.03.10 / 양희영 / Update

* Flow Summary
    
* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함
    
* Input Tables
    - df_in_MasterValidation : Dimension : Master Validation
                               select ([Master Validation].[Validation Batch Type].[W_AFTER_PLAN] * [Master Validation].[Validation Stage] * [Master Validation].[Validation Grp01] * [Master Validation].[Validation Grp02] * 
                               [Master Validation].[Validation Type] * [Master Validation].[Validation Owner] * [Master Validation].[Validation ID] * [Master Validation].[Validation Name]) on row 
                               include memberproperties  {[Master Validation].[Validation ID],[Validation ID Desc]} {[Master Validation].[Validation Name],[Validation Name Desc]};
    - df_in_SOPWTempBOM : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [BOM Info].[BOM Version]) on row, ({Measure.[SOP W_BOM Status], Measure.[Dummy]}) on column 
                          where {Location.[Location Type].filter(#.Name == "MF"), Item.[Item Stage].[SET], Time.[Week].filter(#.Key <= &CurrentWeek.element(0).LeadOffset(3).Key), ~(Measure.[SOP W_BOM Status] in {"Fixed","Export","MPI_L"}), 
                          ~(IsNull(Measure.[SOP W_BOM Status]))};
    - df_in_VersionName : SELECT (&CWVUI);                        
    - df_in_RTF_TTL : Select (&LastSyncVersion.unionWith(&CWVUI)) on row, 
                      ({Measure.[Sales PSI AP2 W_Dmd], Measure.[Sales PSI AP2 W_RTF], Measure.[Sales PSI AP2 W_Short]}) on column include memberproperties {[Version].[Version Name], [Version Name$DisplayName]};
    - df_in_RTF_ProdGrp : Select (&LastSyncVersion.unionWith(&CWVUI) * [Item].[Product Group]) on row, 
                          ({Measure.[Sales PSI AP2 W_Dmd], Measure.[Sales PSI AP2 W_RTF] , Measure.[Sales PSI AP2 W_Short]}) on column include memberproperties {[Version].[Version Name], [Version Name$DisplayName]};
    
* Output Tables
    - df_out_MstValidResult : MG : Mst Valid Result
                          Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] * [Sub Location].[Sub Location] * [BOM Info].[BOM Version] * 
                          [Master Validation].[Validation ID] * [Line].[Line] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[Mst Valid Result_Validation Factor]}) on column;

* 테스트 스크립트 :
    EXEC plugin instance [PY_MG_MasterValidationWeekly2] for Measures {[Mst Valid Result_Validation Factor]} using scope (&CWVUI) 
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
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
import warnings
warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_MasterValidationWeekly2'
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
    col_VersionVersionName           = 'Version.[Version Name]'
    col_ItemItem                     = 'Item.[Item]'
    col_ItemItemStage                = 'Item.[Item Stage]'
    col_LocationLocation             = 'Location.[Location]'
    col_SubLocationSubLocation       = 'Sub Location.[Sub Location]'
    col_TransModeTransMode           = 'Trans Mode.[Trans Mode]'
    col_MasterValidationValidationID = 'Master Validation.[Validation ID]'
    col_LineLine                     = 'Line.[Line]'
    col_SalesDomainAP2               = 'Sales Domain.[AP2]'
    col_BOMInfoBOMVersion            = 'BOM Info.[BOM Version]'
    col_TimeWeek                     = 'Time.[Week]'
    col_ValidationFactor             = "Mst Valid Result_Validation Factor"
    col_SOPW_BOMStatus               = 'SOP W_BOM Status'
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP" # CWV_MP
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion  = paramOutVersion_VALUE
        
        df_in_MasterValidation = read_csv_file("df_in_MasterValidation")
        df_in_SOPWTempBOM      = read_csv_file("df_in_SOPWTempBOM")
        df_in_VersionName      = read_csv_file("df_in_VersionName")
        df_in_RTF_TTL          = read_csv_file("df_in_RTF_TTL")
        df_in_RTF_ProdGrp      = read_csv_file("df_in_RTF_ProdGrp")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # MP Plan End Date     MP Plan Start Date
    # input dataframe 확인용 로그
    
    print_df(df_in_MasterValidation, 'df_in_MasterValidation',False)
    print_df(df_in_SOPWTempBOM, 'df_in_SOPWTempBOM',False)
    print_df(df_in_VersionName, 'df_in_VersionName',False)
    print_df(df_in_RTF_TTL, 'df_in_RTF_TTL',False)
    print_df(df_in_RTF_ProdGrp, 'df_in_RTF_ProdGrp',False)
    
    # DATA TYPE 설정
    
    # -------------------------------------------------------------------------------------    
        
    step('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    step('=====> STEP 0-4 : 추가 df Create ')
    # Version Name 값 Setting
    MASK_VERSION = df_in_VersionName.loc[0, col_VersionVersionName]
    
    # SET, LCM 분리 ---------------------------------------------------
    
    # Version 분리 : VERSION_VALUE 용, LastVersion 용 ---------------------
    # LastVersion : LastVersion 먼저처리----------------------------------------------------------

    # ----------------------------------------------------------------------------
    
    # VERSION_VALUE -----------------------------------------------------------
        
    # 여러번 사용하는 Set 구성 -----------------------------------------------
    
    #------------------------------------------------------------------------
    step('=====> STEP 0-5 : 추가 df Create End')
    ################################################################################################################
    # STEP 1 : Validate data Create
    ################################################################################################################
    step('=====> STEP 1-1 : Validate data Create')
    
    # 칼럼설정
    clist_all   = [col_VersionVersionName, col_MasterValidationValidationID, col_ItemItem, col_LocationLocation,
                      col_SubLocationSubLocation, col_TransModeTransMode, col_BOMInfoBOMVersion,
                      col_LineLine, col_SalesDomainAP2, col_ValidationFactor]
    
    #임시 --------------------------------------------------
    #df_in_MasterValidation = df_in_MasterValidation[df_in_MasterValidation[col_MasterValidationValidationID] == '(SET)PLAN_RESULT']
    #------------------------------------------------------
    
    note(f'=====> for Strt ======================================================= ')
    df_Vld_Result_All = pd.DataFrame(columns=clist_all) #빈 dataframe
    
    for idx, row in df_in_MasterValidation.iterrows():
        #note(f'=====> Validation ID : {row[col_MasterValidationValidationID]}')
        df_Vld_Result_TMP = pd.DataFrame(columns=clist_all) #빈 dataframe
        CHK_I = 0
        #note(f'=====> Validation ID : {row[col_MasterValidationValidationID]} ----Start----')
        
        if row[col_MasterValidationValidationID] == '(SET)PLAN_RESULT':  # ----------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            df_RTF_TTL_N = df_in_RTF_TTL[df_in_RTF_TTL[col_VersionVersionName] != MASK_VERSION]
            df_RTF_TTL_Y = df_in_RTF_TTL[df_in_RTF_TTL[col_VersionVersionName] == MASK_VERSION]
            
            #빈 로루 추가
            if df_RTF_TTL_N.empty :
                df_RTF_TTL_N.loc[len(df_RTF_TTL_N)] = [np.nan] * len(df_RTF_TTL_N.columns)
                
                # 빈 로루 추가
            if df_RTF_TTL_Y.empty:
                df_RTF_TTL_Y.loc[len(df_RTF_TTL_Y)] = [np.nan] * len(df_RTF_TTL_Y.columns)
                    
            #print_df(df_RTF_TTL_N, 'df_RTF_TTL_N', False)
            #print_df(df_RTF_TTL_Y, 'df_RTF_TTL_Y', False)
            
            df_RTF_TTL = df_RTF_TTL_Y.merge(df_RTF_TTL_N, how='cross', suffixes=('_y', '_n'))
            del [df_in_RTF_TTL, df_RTF_TTL_N, df_RTF_TTL_Y]
            
            df_RTF_TTL[col_ValidationFactor] = ( 
                                      "TOTAL Plan | " + df_RTF_TTL[col_VersionVersionName+'_n'].astype('str') +
                                      " | DEMAND | " + df_RTF_TTL['Sales PSI AP2 W_Dmd_n'].astype('str') + 
                                      " | RTF | " + df_RTF_TTL['Sales PSI AP2 W_RTF_n'].astype('str') + 
                                      " | SHORT | " + df_RTF_TTL['Sales PSI AP2 W_Short_n'].astype('str') + 
                                      " | Plan | " + df_RTF_TTL[col_VersionVersionName+'_y'].astype('str') +
                                      " | DEMAND | " + df_RTF_TTL['Sales PSI AP2 W_Dmd_y'].astype('str') + 
                                      " | RTF | " + df_RTF_TTL['Sales PSI AP2 W_RTF_y'].astype('str') + 
                                      " | SHORT | " + df_RTF_TTL['Sales PSI AP2 W_Short_y'].astype('str') + " | "
            )
            
            df_RTF_TTL[col_VersionVersionName] =  df_RTF_TTL[col_VersionVersionName+'_y']
            #print_df(df_RTF_TTL, 'df_RTF_TTL', False)
            
            df_RTF_ProdGrp_N = df_in_RTF_ProdGrp[df_in_RTF_ProdGrp[col_VersionVersionName] != MASK_VERSION]
            df_RTF_ProdGrp_Y = df_in_RTF_ProdGrp[df_in_RTF_ProdGrp[col_VersionVersionName] == MASK_VERSION]
            
            # 빈 로루 추가
            if df_RTF_ProdGrp_N.empty:
                #df_RTF_ProdGrp_N.loc[len(df_RTF_ProdGrp_N)] = [np.nan] * len(df_RTF_ProdGrp_N.columns)
                df_RTF_ProdGrp_N.loc[0, 'Item.[Product Group]'] = 'TV'
                df_RTF_ProdGrp_N.loc[1, 'Item.[Product Group]'] = 'MONITOR'
                df_RTF_ProdGrp_N.loc[2, 'Item.[Product Group]'] = 'AV'
            
            if df_RTF_ProdGrp_Y.empty:
                #df_RTF_TTL_Y.loc[len(df_RTF_TTL_Y)] = [np.nan] * len(df_RTF_TTL_Y.columns)
                df_RTF_ProdGrp_Y.loc[0, 'Item.[Product Group]'] = 'TV'
                df_RTF_ProdGrp_Y.loc[1, 'Item.[Product Group]'] = 'MONITOR'
                df_RTF_ProdGrp_Y.loc[2, 'Item.[Product Group]'] = 'AV'
                
            #print_df(df_RTF_ProdGrp_N, 'df_RTF_ProdGrp_N', False)
            #print_df(df_RTF_ProdGrp_Y, 'df_RTF_ProdGrp_Y', False)
            
            df_RTF_ProdGrp = df_RTF_ProdGrp_Y.merge(df_RTF_ProdGrp_N, on=['Item.[Product Group]'], how='left',
                                                    suffixes=('_y', '_n'))
            del [df_in_RTF_ProdGrp, df_RTF_ProdGrp_Y, df_RTF_ProdGrp_N]
            
            df_RTF_ProdGrp[col_ValidationFactor] = (
                 df_RTF_ProdGrp['Item.[Product Group]'] + 
                " | Plan | " + df_RTF_ProdGrp['Version.[Version Name$DisplayName]_n'].astype('str') +
                " | DEMAND | " + df_RTF_ProdGrp['Sales PSI AP2 W_Dmd_n'].astype('str') +
                " | RTF | " + df_RTF_ProdGrp['Sales PSI AP2 W_RTF_n'].astype('str') +
                " | SHORT | " + df_RTF_ProdGrp['Sales PSI AP2 W_Short_n'].astype('str') +
                " | Plan | " + df_RTF_ProdGrp['Version.[Version Name$DisplayName]_y'].astype('str') +
                " | DEMAND | " + df_RTF_ProdGrp['Sales PSI AP2 W_Dmd_y'].astype('str') +
                " | RTF | " + df_RTF_ProdGrp['Sales PSI AP2 W_RTF_y'].astype('str') +
                " | SHORT | " + df_RTF_ProdGrp['Sales PSI AP2 W_Short_y'].astype('str') + " | "
            )
            
            df_RTF_ProdGrp[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_RTF_ProdGrp = df_RTF_ProdGrp.groupby([col_MasterValidationValidationID],
                                                 as_index=False)[col_ValidationFactor].agg(lambda x: ';'.join(set(x)))
            #print_df(df_RTF_ProdGrp, 'df_RTF_ProdGrp', False)
            
            df_Ext_Data = df_RTF_TTL.copy()
            
            df_Ext_Data[col_VersionVersionName] = np.where(df_Ext_Data[col_VersionVersionName].isna(), MASK_VERSION,
                                                           df_Ext_Data[col_VersionVersionName])
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            df_Ext_Data[col_ItemItem] = '-'
            df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'
            
            df_Ext_Data = df_Ext_Data.merge(df_RTF_ProdGrp, on=[col_MasterValidationValidationID], how='inner',
                                            suffixes=('', '_y'))
            
            df_Ext_Data[col_ValidationFactor] = df_Ext_Data[col_ValidationFactor] + df_Ext_Data[col_ValidationFactor+'_y']
            
            #print_df(df_Ext_Data, 'df_Ext_Data', False)
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
        elif row[col_MasterValidationValidationID] == '(SET)TEMP_BOM':  # ----------------------------
            CHK_I = 1
            note(f'=====> {row[col_MasterValidationValidationID]} : -- START --   ')
            
            #차차차주 SOP가 임시봄으로 떨어진 경우
            df_Ext_Data = df_in_SOPWTempBOM.copy()
            df_Ext_Data[col_SOPW_BOMStatus] = df_Ext_Data[col_SOPW_BOMStatus].fillna("") #np.nan 제거
            
            df_Ext_Data[col_MasterValidationValidationID] = row[col_MasterValidationValidationID]
            # df_Ext_Data[col_ItemItem] = '-'
            # df_Ext_Data[col_LocationLocation] = '-'
            df_Ext_Data[col_SubLocationSubLocation] = '-'
            df_Ext_Data[col_TransModeTransMode] = '-'
            #df_Ext_Data[col_BOMInfoBOMVersion] = '-'
            df_Ext_Data[col_LineLine] = '-'
            df_Ext_Data[col_SalesDomainAP2] = '-'            
            # ※ Validation Factor = Item.[Item] +”[“ + [BOM Info].[BOM Version] + “] : “ + Measure.[SOP W_BOM Status] #2026.02.19 수정
            df_Ext_Data[col_ValidationFactor] = (df_Ext_Data[col_ItemItem] + "[" + df_Ext_Data[col_BOMInfoBOMVersion] + 
                                                 "] : " + df_Ext_Data[col_SOPW_BOMStatus])
            
            #print_df(df_Ext_Data, 'df_Ext_Data', False)
            
            # 칼럼정리
            df_Ext_Data = df_Ext_Data[clist_all]
            df_Ext_Data.drop_duplicates(inplace=True)
            
            df_Vld_Result_TMP = df_Ext_Data.copy()
            del df_Ext_Data
            # print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)
            
            # if End -------------------------------------------------------------------------------------------------
        
        #row_count, col_count = df_Vld_Result_TMP.shape
        #note(f'=====> {row[col_MasterValidationValidationID]} : rows : {row_count}   ')
        
        #처리 대상 ValidationID 만 결과건수 출력
        if CHK_I == 1 :
            row_count, col_count = df_Vld_Result_TMP.shape
            note(f'=====> {row[col_MasterValidationValidationID]} : rows : {row_count}   ')
        
        if df_Vld_Result_TMP.empty :
            None 
        else :
            #print_df(df_Vld_Result_TMP, 'df_Vld_Result_TMP',False)            
            if df_Vld_Result_All.empty:
                df_Vld_Result_All = df_Vld_Result_TMP.copy()
            else :
                df_Vld_Result_All = pd.concat([df_Vld_Result_All, df_Vld_Result_TMP])
                
        del df_Vld_Result_TMP
    
    del [df_in_MasterValidation, df_in_SOPWTempBOM]
    note(f'=====> for End ======================================================= ')
        
    #print_df(df_Vld_Result_All, 'df_Vld_Result_All',False)
    step('=====> STEP 1-2 : Validate data Create End')
    
    ################################################################################################################
    # STEP 2 : MG: [Mst Valid Result] : output table create
    ################################################################################################################
    step('=====> STEP 2 : Final output table create')
    
    # out Data 생성 :
    df_out_MstValidResult = df_Vld_Result_All.copy()
    df_out_MstValidResult.drop_duplicates(inplace=True)
    del df_Vld_Result_All
    
    # 버전 처리 :
    #df_out_MstValidResult[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_MstValidResult.shape
    note(f'=====> Final df_out_MstValidResult rows : {row_count}, column : {col_count}')    
    print_df(df_out_MstValidResult, 'df_out_MstValidResult',False)
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_MstValidResult, 'df_out_MstValidResult')
    
    step('=====> STEP 2-1 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_MstValidResult = pd.DataFrame([], columns=[])
    
finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()