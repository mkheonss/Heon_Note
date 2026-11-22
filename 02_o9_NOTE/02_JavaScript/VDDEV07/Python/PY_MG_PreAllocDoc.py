"""
* 프로그램명 
    - PY_MG_PreAllocDoc

* 내용
    - Pre-alloc.Constraint 용 가용성 Document 생성을 위한 Buffer 구성

* 변경이력
    - 2024.10.08 / 양희영 / Create
    - 2025.06.30 / 양희영 / Update

* Input
  - 자재/업체/Plant 간 공급비율 설정을 위한 Resource Grouping
  - From ResourceGroup to To Resource Group 간 Quota(공급배분율) 설정
  
* Flow Summary
    STEP1. Pre-alloc.Constraint 용 가용성 Document 생성을 위한 Buffer 구성
    
* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_PreAllocItem : MG : Pre Alloc Const by Item
                           Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const by Item_Creation Time]}) on column;
	   - df_in_PreAllocDetailW : MG : Pre Alloc Const Detail W
                             Select ([Version].[Version Name] * &PlanningHorizon * [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Pre Alloc Const Detail W_Const Qty] }) on column;
* Output Tables
    - df_out_PACDoc : MG : MP Batch_Document Bulk Member Creation
                     Select ([Version].[Version Name] * [MP Batch_Sequence].[MP Batch_Sequence_ID] ) on row, ({Measure.[MP Batch_Document_Document Type], Measure.[MP Batch_Document_OrderlineID]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_PreAllocDoc] for measures {[MP Batch_Document_OrderlineID]} using scope (&MPV) 
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
str_instance = 'PY_MG_PreAllocDoc'
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
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-1 : DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName                  = 'Version.[Version Name]'
    groupGroupID                        = 'Group.[Group ID]'
    locationLocation                    = 'Location.[Location]'
    mPBatch_SequenceMPBatch_Sequence_ID = 'MP Batch_Sequence.[MP Batch_Sequence_ID]'
    
    mPBatch_Document_DocumentType = 'MP Batch_Document_Document Type'
    mPBatch_Document_OrderlineID  = 'MP Batch_Document_OrderlineID'
    
    vdCommon.gfn_stepLog('=====> STEP 0-2 : DataFrame Column : 변수 처리 End')
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-3 : Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE

        df_in_PreAllocItem     = read_csv_file("df_in_PreAllocItem")
        df_in_PreAllocDetailW  = read_csv_file("df_in_PreAllocDetailW")
        
    #if df_in_PreAllocDetailW.empty:
    #    raise Exception("=====> raise Exception: df_in_PreAllocDetailW is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    vdCommon.gfn_saveDf(df_in_PreAllocItem, 'df_in_PreAllocItem',False)
    vdCommon.gfn_saveDf(df_in_PreAllocDetailW, 'df_in_PreAllocDetailW',False)
    
    vdCommon.gfn_stepLog('=====> STEP 0-4 : Input table load End')
    
    ################################################################################################################
    # STEP 1 : ItemMtrl Set 구성 및 MP Batch_Item Mtrl Bulk Member Creation 에 입력 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 : ItemMtrl Set create')
    
    # distinct Group.[Group ID], Location.[Location]: df_in_PreAllocItem
    df_PreAllocItem = df_in_PreAllocItem[[versionVersionName,groupGroupID,locationLocation]].copy()
    del df_in_PreAllocItem
    df_PreAllocItem.drop_duplicates(inplace=True)
    df_PreAllocItem['check_value'] = 1
    vdCommon.gfn_saveDf(df_PreAllocItem, 'df_PreAllocItem',False)
    
    # Merge : df_in_PreAllocDetailW & df_PreAllocItem
    df_PACDoc = df_in_PreAllocDetailW.merge(df_PreAllocItem, on=[versionVersionName,groupGroupID,locationLocation], how='left')
    del df_in_PreAllocDetailW
    del df_PreAllocItem
    df_PACDoc = df_PACDoc.loc[df_PACDoc['check_value'].isna()]
    df_PACDoc[mPBatch_Document_OrderlineID] =  'PAC_' + df_PACDoc[groupGroupID] + '@' + df_PACDoc[locationLocation]
    
    #칼럼 정리
    df_PACDoc = df_PACDoc[[versionVersionName, mPBatch_Document_OrderlineID]]
    df_PACDoc.drop_duplicates(inplace=True)
    
    df_PACDoc[mPBatch_Document_DocumentType]       = 'Scheduled Receipts'
    df_PACDoc[mPBatch_SequenceMPBatch_Sequence_ID] = df_PACDoc.reset_index().index + 1
    
    #save_csv_file(df_PACDoc, 'df_PACDoc')
    vdCommon.gfn_saveDf(df_PACDoc, 'df_PACDoc',False)
    vdCommon.gfn_stepLog('=====> STEP 1-1 : ItemMtrl Set create End')
    
    ################################################################################################################
    # STEP 2 : output table create
    ################################################################################################################
    
    vdCommon.gfn_stepLog('=====> STEP 2 : Final output table create')
    
    # out Data 생성 
    df_out_PACDoc = df_PACDoc.copy()
    del df_PACDoc
    
    # 버전 처리
    #df_out_PACDoc[versionVersionName] = paramOutVersion
    
    # out 칼럼 설정
    df_out_PACDoc = df_out_PACDoc[[versionVersionName,
                                   mPBatch_SequenceMPBatch_Sequence_ID,
                                   mPBatch_Document_DocumentType,
                                   mPBatch_Document_OrderlineID]]
    
    vdCommon.gfn_saveDf(df_out_PACDoc, 'df_out_PACDoc',False)
    vdCommon.gfn_stepLog('=====> STEP 2-1 : Final output table create End')
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_PACDoc, 'df_out_PACDoc')
        
    row_count, col_count = df_out_PACDoc.shape
    note(f'=====> Final df_out_PACDoc rows : {row_count}, column : {col_count}')
    
    vdCommon.gfn_stepLog('=====> STEP 2-2 : End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_PACDoc = pd.DataFrame([], columns=[])

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