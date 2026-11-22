"""
* 프로그램명 
    - PY_UI_MtrlConstraintType

* 내용
    - Constraint Type UI L3 레벨 초기 데이타 구성 
    - 엔진 대상을 올려주는게 아니라 관리할 대상을 전체 올려주어야 함.

* 변경이력
- 2024.09.11 / 양희영 / Create
- 2025.06.30 / 양희영 / Update

* Flow Summary
    STEP1.   MSL3(자재 Level3) 신규대상에 대해 자재제약 Type을 관리할 수 있도록 기본 마스터 Insert  
    STEP2.   STEP1 기준으로 Time Phased 자재제약 Type Default Data Setting 

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_RelativeW : Select ([Relative Week].[Relative Week]);
    - df_in_MSL3 : Select ([Version].[Version Name] * [Item Material].[MSL3]);
    - df_in_MtrlConstType : Select ([Version].[Version Name] * [Item Material].[MSL3] ) on row, 
                            ({Measure.[Mtrl Const Type L3_Created By], Measure.[Mtrl Const Type L3_Creation Time], Measure.[Mtrl Const Type L3_Time Varying Flag]}) on column;
    - df_in_MtrlConstTypeW : Select ([Version].[Version Name] * [Item Material].[MSL3] * [Relative Week].[Relative Week] ) on row, ({Measure.[Mtrl Const Type L3 W_Type]}) on column;

* Output Tables
    - df_out_MtrlConstType : MG : Mtrl Const Type L3
                             Select ([Version].[Version Name] * [Item Material].[MSL3] ) on row, 
                             ({Measure.[Mtrl Const Type L3_Created By], Measure.[Mtrl Const Type L3_Creation Time], Measure.[Mtrl Const Type L3_Time Varying Flag]}) on column;
    - df_out_MtrlConstTypeW : MG : Mtrl Const Type L3 W
                              Select ([Version].[Version Name] * [Item Material].[MSL3] * [Relative Week].[Relative Week] ) on row, 
                               ({  Measure.[Mtrl Const Type L3 W_Type]}) on column;
    
* 테스트 스크립트
    EXEC plugin instance [PY_UI_MtrlConstraintType] for measures {[Mtrl Const Type L3 W_Type]} using scope (&MPV) 
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
str_instance = 'PY_UI_MtrlConstraintType'
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
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName         = 'Version.[Version Name]'
    itemMaterialMSL3           = 'Item Material.[MSL3]'
    relativeWeekRelativeWeek   = 'Relative Week.[Relative Week]'
    
    mtrlConstTypeL3_CreatedBy       = 'Mtrl Const Type L3_Created By'
    mtrlConstTypeL3_CreationTime    = 'Mtrl Const Type L3_Creation Time'
    mtrlConstTypeL3_TimeVaryingFlag = 'Mtrl Const Type L3_Time Varying Flag'
    mtrlConstTypeL3W_Type           = 'Mtrl Const Type L3 W_Type'
    
    
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_RelativeW      = read_csv_file("df_in_RelativeW")
        df_in_MSL3           = read_csv_file("df_in_MSL3")
        df_in_MtrlConstType  = read_csv_file("df_in_MtrlConstType")
        df_in_MtrlConstTypeW = read_csv_file("df_in_MtrlConstTypeW")
    
    #if df_in_RelativeW.empty:
    #    raise Exception("=====> raise Exception: df_in_RelativeW is empty")
    
    #if df_in_MSL3.empty:
    #    raise Exception("=====> raise Exception: df_in_MSL3 is empty")
            
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_RelativeW, 'df_in_RelativeW', False) 
    vdCommon.gfn_saveDf(df_in_MSL3, 'df_in_MSL3', False)
    vdCommon.gfn_saveDf(df_in_MtrlConstType, 'df_in_MtrlConstType', False)
    vdCommon.gfn_saveDf(df_in_MtrlConstTypeW, 'df_in_MtrlConstTypeW', False)
    vdCommon.gfn_stepLog('=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : df_MSL3Set 구성 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 : df_MSL3Set create')
    
    # STEP1-1 - df_in_MtrlConstType : distinct MSL3
    CT_MSL3_series = df_in_MtrlConstType[itemMaterialMSL3].unique()
    del df_in_MtrlConstType
    
    df_MSL3Set = df_in_MSL3.loc[~(df_in_MSL3[itemMaterialMSL3].isin(CT_MSL3_series))].copy()
    df_MSL3Set[mtrlConstTypeL3_CreatedBy]       = 'System'
    df_MSL3Set[mtrlConstTypeL3_TimeVaryingFlag] = 'N'
    df_MSL3Set[mtrlConstTypeL3_CreationTime] = datetime.datetime.now()
    del df_in_MSL3
    
    vdCommon.gfn_saveDf(df_MSL3Set, 'df_MSL3Set', False)
    #vdCommon.gfn_stepLog('=====> STEP 1-1 : df_MSL3Set create End')
    
    ################################################################################################################
    # STEP 2 : MtrlConstTypeW data 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 : MtrlConstTypeW data create')
    
    # 2-1 df_in_RelativeW Merge
    df_MSL3Set['joinKey']      = 1
    df_in_RelativeW['joinKey'] = 1
    df_MtrlConstTypeW = df_MSL3Set.merge(df_in_RelativeW, on=['joinKey'], how='inner')
    df_MSL3Set.drop(columns=['joinKey'], inplace=True)
    del df_in_RelativeW
    
    #칼럼정리
    df_MtrlConstTypeW = df_MtrlConstTypeW[[versionVersionName,itemMaterialMSL3,relativeWeekRelativeWeek]]
    
    # df_in_MtrlConstTypeW Merge
    df_MtrlConstTypeW = df_MtrlConstTypeW.merge(df_in_MtrlConstTypeW, on=[versionVersionName, itemMaterialMSL3, relativeWeekRelativeWeek], how='left')
    df_MtrlConstTypeW.fillna({mtrlConstTypeL3W_Type:'Un'}, inplace=True)
    
    vdCommon.gfn_saveDf(df_MtrlConstTypeW, 'df_MtrlConstTypeW', False)
    #vdCommon.gfn_stepLog('=====> STEP 2-1 : MtrlConstTypeW data create End')
    
    ################################################################################################################
    # STEP 9 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 9 : Final output table create')
    
    # out Data 생성    
    df_out_MtrlConstType  = df_MSL3Set.copy()
    df_out_MtrlConstTypeW = df_MtrlConstTypeW.copy()
    
    # 버전 처리 :
    #df_out_MtrlConstType[versionVersionName]  = paramOutVersion
    #df_out_MtrlConstTypeW[versionVersionName] = paramOutVersion
    

    row_count, col_count = df_out_MtrlConstType.shape
    note(f'=====> df_out_MtrlConstType rows : {row_count}, column : {col_count}')
    vdCommon.gfn_saveDf(df_out_MtrlConstType, 'df_out_MtrlConstType', False)
    
    row_count, col_count = df_out_MtrlConstTypeW.shape
    note(f'=====> df_out_MtrlConstTypeW rows : {row_count}, column : {col_count}')
    vdCommon.gfn_saveDf(df_out_MtrlConstTypeW, 'df_out_MtrlConstTypeW', False)
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_MtrlConstType, 'df_out_MtrlConstType')
        save_csv_file(df_out_MtrlConstTypeW, 'df_out_MtrlConstTypeW')
        
    
    vdCommon.gfn_stepLog('=====> STEP 9-1 : Final output table create End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_MtrlConstType = pd.DataFrame([], columns=[])
    df_out_MtrlConstTypeW = pd.DataFrame([], columns=[])
    
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