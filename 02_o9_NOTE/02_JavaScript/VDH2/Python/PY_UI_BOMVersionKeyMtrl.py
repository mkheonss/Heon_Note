"""
* 프로그램명 
    - PY_UI_BOMVersionKeyMtrl

* 내용
    - BOM Version Key Mtrl summary 데이터 구성

* 변경이력
    - 2024.10.31 / 양희영 / Create
    - 2025.06.30 / 양희영 / Update
    
* Flow Summary
    STEP1. Input 컬럼 변경 및 복수 mtrl값에 대해 seq 추가
    
* Execution 
* Script Parameter
    - paramOutVersion : CurrentWorkingView
    
* Input Tables
    - df_in_BOMVersionPrtyW_Prty : Select ([Version].[Version Name] * [Item].[Item] * [BOM Info].[BOM Version] * [Item Material].[Key Material Group] * [Item Material].[Item Material] ) on row, 
                                   () on column where {[Time].[Week], [Location].[Location], [Item Component].[Item Component],Measure.[BOM Version Prty W_Prty]!="X"};

* Output Tables
    - df_out_BOMVersionPrtyW : Select (&MPV * [Item].[Item] * [Sequence].[Sequence] * [Item Material].[Key Mrtl Grp] * [BOM Info].[BOM Version] ) on row, ({Measure.[BOM Version Key Mtrl_Item]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_BOMVersionKeyMtrl] for Measures {[BOM Version Key Mtrl_Item]} using scope (&MPV) 
     using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};

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
str_instance = 'PY_UI_BOMVersionKeyMtrl'
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

def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

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
    col_VersionVersionName       = 'Version.[Version Name]'
    col_ItemItem                 = 'Item.[Item]'
    col_BOMInfoBOMVersion        = 'BOM Info.[BOM Version]'
    col_ItemMaterialKeyMrtlGrp   = 'Item Material.[Key Material Group]'
    col_ItemMaterialItemMaterial = 'Item Material.[Item Material]'
    col_sequenceSequence         = 'Sequence.[Sequence]'
    
    col_BOMVersionKeyMtrl_Item   = 'BOM Version Key Mtrl_Item'
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    paramOutVersion_VALUE = "CurrentWorkingView"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = paramOutVersion_VALUE
        
        df_in_BOMVersionPrtyW_Prty = read_csv_file("df_in_BOMVersionPrtyW_Prty")
    
    #if df_in_BOMVersionPrtyW_Prty.empty:
    #    raise Exception("=====> raise Exception: df_in_BOMVersionPrtyW_Prty is empty")
    
    # 입력 변수 확인
    if paramOutVersion is None or paramOutVersion.strip() == '':
        paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
        
    # input dataframe 확인용 로그
    note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_BOMVersionPrtyW_Prty, 'df_in_BOMVersionPrtyW_Prty', False)
    
    vdCommon.gfn_stepLog('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    
    ################################################################################################################
    # STEP 1 : df_out_BOMVersionPrtyW 구성 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1-1 : df_out_BOMVersionPrtyW data Create')
    
    df_out_BOMVersionPrtyW = df_in_BOMVersionPrtyW_Prty.copy()
    del df_in_BOMVersionPrtyW_Prty
    
    df_out_BOMVersionPrtyW.rename(columns={col_ItemMaterialItemMaterial:col_BOMVersionKeyMtrl_Item}, inplace=True)
    df_out_BOMVersionPrtyW[col_sequenceSequence] = df_out_BOMVersionPrtyW.groupby([col_VersionVersionName, 
                                                                                   col_ItemItem,
                                                                                   col_ItemMaterialKeyMrtlGrp,
                                                                                   col_BOMInfoBOMVersion]).cumcount() + 1
    
    #칼럼 정리
    df_out_BOMVersionPrtyW = df_out_BOMVersionPrtyW[[col_VersionVersionName, col_ItemItem, col_sequenceSequence,
                                                     col_ItemMaterialKeyMrtlGrp, col_BOMInfoBOMVersion,
                                                     col_BOMVersionKeyMtrl_Item]]
    
    #vdCommon.gfn_saveDf(df_out_BOMVersionPrtyW, 'df_out_BOMVersionPrtyW', False)
    vdCommon.gfn_stepLog('=====> STEP 1-2 : df_out_BOMVersionPrtyW data Create End')
    
    ################################################################################################################
    # STEP 2 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 : Final output table create')
    
    # out Data 생성 :
    #df_out_BOMVersionPrtyW 그대로 사용
    
    # 버전 처리
    df_out_BOMVersionPrtyW[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_BOMVersionPrtyW.shape
    note(f'=====> Final df_out_BOMVersionPrtyW rows : {row_count}, column : {col_count}')    
    vdCommon.gfn_saveDf(df_out_BOMVersionPrtyW, 'df_out_BOMVersionPrtyW', False)
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_BOMVersionPrtyW, 'df_out_BOMVersionPrtyW')
    
    vdCommon.gfn_stepLog('=====> STEP 2-1 : Final output table create End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_BOMVersionPrtyW = pd.DataFrame([], columns=[])
    
finally:
    vdCommon.gfn_stepLog('plugin Execution End ')
    
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    
    #logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    #logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
            
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