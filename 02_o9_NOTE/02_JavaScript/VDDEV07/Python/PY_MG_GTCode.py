"""
* 프로그램명 
    - PY_MG_GTCode

* 내용
    - 신규 GT Code 입수내역에 대해 GT Code 메저 구성
    - Location 멤버 생성을 위한 Buffer Measure 구성 
      * PR_DIM_Location 에서 호출

* 변경이력
    - 2024.11.13 / 양희영 / Create
    - 2025.06.27 / 양희영 / Update

* Flow Summary
    STEP1. 신규 GT Code 입수내역에 대해 GT Code 메저 구성
    STEP2. Location 멤버 생성을 위한 Buffer 메저 구성 
    
* Execution 

* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
    
* Input Tables
    - df_in_GTCode : Dimension : Global Top
                    Select ([Global Top].[GT Code] * [Global Top].[GT Name]);
    - df_in_GTFixName : Global Top Code Measure Group : MG : Global Top
                       Select ([Version].[Version Name] * [Global Top].[GT Code]) on row, 
                       ({ Measure.[GT_Fix Name], Measure.[GT_Fix Name_Order], Measure.[GT_Fix Name_Validation], Measure.[GT_Priority]}) on column;

                   
* Output Tables
    - df_out_GTCode : MG : Global Top
                     Select ([Version].[Version Name] * [Global Top].[GT Code] ) on row, 
                     ({Measure.[GT_Fix Name], Measure.[GT_Fix Name_Order], Measure.[GT_Fix Name_Validation], Measure.[GT_Priority]}) on column;
    - df_out_Location : MG : MP Batch_Location Bulk Member Creation
                      Select ([Version].[Version Name] * [Global Top].[GT Code] ) on row, 
                      ({Measure.[MP Batch_Location Bulk Member Creation_GT Code], Measure.[MP Batch_Location Bulk Member Creation_GT Name Fix]}) on column;


* 테스트 스크립트
    EXEC plugin instance [PY_MG_GTCode] for measures {[MP Batch_Location Bulk Member Creation_GT Code]} using scope (&MPV) 
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};

"""

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import os
import pandas as pd
import numpy as np
import datetime
import traceback
import gc
import tracemalloc

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_GTCode'
is_local = common.gfn_get_isLocal()
COMMON_SOURCE_VERSION = common.G_SourceVersion

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

#def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
#    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


#def step(no, string):
#    logger.Step(p_step_no=no, p_step_desc=f'{string}')

try:
    ################################################################################################################
    # Batch 시작
    ################################################################################################################
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)
    
    ################################################################################################################
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====>STEP 0-1 DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    col_VersionVersionName = 'Version.[Version Name]'
    col_GlobalTopGTCode    = 'Global Top.[GT Code]'
    col_GlobalTopGTName    = 'Global Top.[GT Name]'
    col_GT_FixName_Order   = 'GT_Fix Name_Order'
    col_GT_FixName         = 'GT_Fix Name'
    #col_GT_GTCode          = 'GT_GT Code'
    
    col_MPBatch_LocationBulkMemberCreation_GTCode    = 'MP Batch_Location Bulk Member Creation_GT Code'
    col_MPBatch_LocationBulkMemberCreation_GTNameFix = 'MP Batch_Location Bulk Member Creation_GT Name Fix'
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_VersionName = read_csv_file("df_in_VersionName")
        df_in_GTCode      = read_csv_file("df_in_GTCode")
        df_in_GTFixName   = read_csv_file("df_in_GTFixName")
    
    #if df_in_GTCode.empty:
    #    raise Exception("=====> raise Exception: df_in_GTCode is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_VersionName, 'df_in_VersionName',False)
    vdCommon.gfn_saveDf(df_in_GTCode, 'df_in_GTCode',False)
    vdCommon.gfn_saveDf(df_in_GTFixName, 'df_in_GTFixName',False)
    
    vdCommon.gfn_stepLog('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    #vdCommon.gfn_stepLog('=====> STEP 0-4 : 추가 df Create ')        
    #vdCommon.gfn_stepLog('=====> STEP 0-5 : 추가 df Create End')
    ################################################################################################################
    # STEP 1 : df_GTCodeList Set 구성 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1-1 : df_GTCodeList data Create')
    
    # Version Name 값 Setting
    VERSION_VALUE = df_in_VersionName.loc[0, col_VersionVersionName]
    df_in_GTCode[col_VersionVersionName] = VERSION_VALUE
    vdCommon.gfn_saveDf(df_in_GTCode, 'df_in_GTCode 2',False)
    
    #신규 GT Code 입수내역에 대해 GT Code 메저 구성
    df_GTFixName_NotNUll = df_in_GTFixName[df_in_GTFixName[col_GT_FixName].notna()].copy()
    vdCommon.gfn_saveDf(df_GTFixName_NotNUll, 'df_GTFixName_NotNUll',False)
    
    df_GTCodeList = df_in_GTCode[~df_in_GTCode.set_index([col_GlobalTopGTCode]).index.isin(   
                             df_GTFixName_NotNUll.set_index([col_GlobalTopGTCode]).index)].copy() # not exists
    del df_GTFixName_NotNUll
    
    #df_GTCodeList[col_VersionVersionName] = paramOutVersion
    #df_GTCodeList[col_GT_GTCode]          = df_GTCodeList[col_GlobalTopGTCode]
    df_GTCodeList[col_GT_FixName_Order]   = 1
    df_GTCodeList[col_GT_FixName]         = df_GTCodeList[col_GlobalTopGTName]
    
    vdCommon.gfn_saveDf(df_GTCodeList, 'df_GTCodeList',False)
    
    vdCommon.gfn_stepLog('=====> STEP 1-2 : df_GTCodeList data Create End')
    
    ################################################################################################################
    # STEP 2 :  df_LocationBulkMember  SET 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2-1 : df_LocationBulkMember Create')
    
    #Location 멤버 생성을 위한 Buffer 메저 구성 (MP Batch_Location Bulk Member Creation)
    df_LocationBulkMember = df_in_GTCode.merge(df_in_GTFixName, on=[col_GlobalTopGTCode]
                                              , how='left', suffixes=('','_y')) .copy()
    del df_in_GTCode; del df_in_GTFixName
    
    df_LocationBulkMember[col_MPBatch_LocationBulkMemberCreation_GTCode]    = df_LocationBulkMember[col_GlobalTopGTCode]
    df_LocationBulkMember[col_MPBatch_LocationBulkMemberCreation_GTNameFix] = np.where(df_LocationBulkMember[col_GT_FixName].isna()
                                    ,df_LocationBulkMember[col_GlobalTopGTName], df_LocationBulkMember[col_GT_FixName])
    
    vdCommon.gfn_saveDf(df_LocationBulkMember, 'df_LocationBulkMember',False)
    
    vdCommon.gfn_stepLog('=====> STEP 2-2 : df_LocationBulkMember Create End')
    
    ################################################################################################################
    # STEP 3 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 3 : Final output table create')
    
    # out Data 생성 :
    df_out_GTCode = df_GTCodeList[[col_VersionVersionName, col_GlobalTopGTCode #, col_GT_GTCode
                                 , col_GT_FixName_Order, col_GT_FixName]].copy()
    df_out_Location = df_LocationBulkMember[[col_VersionVersionName, col_GlobalTopGTCode
                                           , col_MPBatch_LocationBulkMemberCreation_GTCode
                                           , col_MPBatch_LocationBulkMemberCreation_GTNameFix]].copy()
    
    del df_GTCodeList; del df_LocationBulkMember
    
    # 버전 처리
    #df_out_GTCode[col_VersionVersionName]   = paramOutVersion
    #df_out_Location[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_GTCode.shape
    note(f'=====> Final df_out_GTCode rows : {row_count}, column : {col_count}')    
    vdCommon.gfn_saveDf(df_out_GTCode, 'df_out_GTCode',False)    

    row_count, col_count = df_out_Location.shape
    note(f'=====> Final df_out_Location rows : {row_count}, column : {col_count}')
    vdCommon.gfn_saveDf(df_out_Location, 'df_out_Location',False)
        
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_GTCode, 'df_out_GTCode')
        save_csv_file(df_out_Location, 'df_out_Location')
        
    vdCommon.gfn_stepLog('=====> STEP 3-1 : Final output table create End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_GTCode   = pd.DataFrame([], columns=[])
    df_out_Location = pd.DataFrame([], columns=[])

finally:
    vdCommon.gfn_stepLog('plugin Execution End ')
    
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    
    # logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    # logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    
    logger.Finish()
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')