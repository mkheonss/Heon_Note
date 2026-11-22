"""
* 프로그램명 
    - PY_MG_Activity1FlowLayer

* 내용
    - [LPS] Activity1 Flow Layer, Activity1 Flow Type Update를 위한 Buffer 데이타 생성

* 변경이력
    - 2024.11.18 / 양희영 / Create
    - 2025.06.27 / 양희영 / Update

* Flow Summary
    STEP1. BOM Flow Layer & Type Update 
    STEP2. BOD Flow Layer & Type Update 

* Execution 

* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.

* Input Tables
    - df_in_BOM : MG : BOM Master
                 Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, 
                 ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]})  on column;

    - df_in_Item : Dimension : Item
                  Select ( [Item].[Item] * [Item].[Item Stage] ) ;

    - df_in_BODItem: MG: BOD Item 
                    Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                    ({Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate] }) 
                    on column.filter((isnull(Measure.[BOD Item_Eff Enddate])||Measure.[BOD Item_Eff Enddate]> Measure.[W Plan Start Date]) && (isnull(Measure.[BOD Item_Eff Startdate])||Measure.[BOD Item_Eff Startdate]< Measure.[W Plan End Date]));

    - df_in_BODListMtrl : MG : BOD Item Mtrl Full
                     Select ([Version].[Version Name] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                     ({Measure.[BOD Item Mtrl Full_EFF Enddate], Measure.[BOD Item Mtrl Full_EFF Startdate], Measure.[BOD Item Mtrl Full_Flag], Measure.[BOD Item Mtrl Full_Lot Size], Measure.[BOD Item Mtrl Full_MSL3]}) on column;

    - df_in_Location : Dimension : Location
                     Select ([Location].[Location] * [Location].[Site Stage]);

* Output Tables
    - df_out_Activity1Flow : MG : MP Batch_Activity1 Flow
                    Select ([Version].[Version Name] * [Activity1].[Activity1] ) on row, 
                    ({Measure.[MP Batch_Activity1 Flow_Layer], Measure.[MP Batch_Activity1 Flow_Type]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_Activity1FlowLayer] for measures {[MP Batch_Activity1 Flow_Layer]} using scope (&MPV) 
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
str_instance = 'PY_MG_Activity1FlowLayer'
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
    vdCommon.gfn_stepLog('=====> STEP 0-1 DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    col_VersionVersionName     = 'Version.[Version Name]'
    col_ItemItem               = 'Item.[Item]'
    col_ItemItemStage          = 'Item.[Item Stage]'
    col_BOMInfoBOMID           = 'BOM Info.[BOM ID]'
    col_Activity1Activity1     = 'Activity1.[Activity1]'
    col_LocationLocation       = 'Location.[Location]'
    col_SubLocationSubLocation = 'Sub Location.[Sub Location]'
    col_TransModeTransMode     = 'Trans Mode.[Trans Mode]'
    col_LocationSiteStage      = 'Location.[Site Stage]'
    
    col_BOMMaster_BOMID = 'BOM Master_BOM ID'
    
    col_MPBatch_Activity1Flow_Layer = 'MP Batch_Activity1 Flow_Layer'
    col_MPBatch_Activity1Flow_Type  = 'MP Batch_Activity1 Flow_Type'
    
    col_fromsitestage = 'from site stage'
    col_toSiteStage   = 'to Site Stage'
    
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
        
        df_in_BOM = read_csv_file("df_in_BOM")
        df_in_Item = read_csv_file("df_in_Item")
        df_in_BODItem = read_csv_file("df_in_BODItem")
        df_in_BODListMtrl = read_csv_file("df_in_BODListMtrl")
        df_in_Location = read_csv_file("df_in_Location")
    
    #if df_in_GTCode.empty:
    #    raise Exception("=====> raise Exception: df_in_GTCode is empty")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    vdCommon.gfn_saveDf(df_in_BOM, 'df_in_BOM',False)
    vdCommon.gfn_saveDf(df_in_Item, 'df_in_Item',False)
    vdCommon.gfn_saveDf(df_in_BODItem, 'df_in_BODItem',False)
    vdCommon.gfn_saveDf(df_in_BODListMtrl, 'df_in_BODListMtrl',False)
    vdCommon.gfn_saveDf(df_in_Location, 'df_in_Location',False)
    
    vdCommon.gfn_stepLog('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    # vdCommon.gfn_stepLog('=====> STEP 0-4 : 추가 df Create ')        
    # vdCommon.gfn_stepLog('=====> STEP 0-5 : 추가 df Create End')
    ################################################################################################################
    # STEP 1 : BOM Set 구성 
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1-1 : BOM data Create')
    
    # BOM Case 에 대해 MP Batch_Activity1 Flow 에 Insert
    df_BOMStage = df_in_BOM.merge(df_in_Item, left_on=[col_BOMMaster_BOMID], right_on=[col_ItemItem], how='inner')
    del [df_in_BOM, df_in_Item]
    
    conditions_BOM = [
        df_BOMStage[col_ItemItemStage] == 'LCM',
        df_BOMStage[col_ItemItemStage] == 'SET',
        True,
    ] 
    
    choices_BOM_Layer = [
        '2',
        '4',
        '7',  # ELSE
    ]
    
    choices_BOM_Type = [
        'LCM BOM',
        'SET BOM',
        'Others',  # ELSE
    ]
    
    df_BOMStage[col_Activity1Activity1] = df_BOMStage[col_BOMInfoBOMID]
    df_BOMStage[col_MPBatch_Activity1Flow_Layer] = np.select(conditions_BOM, choices_BOM_Layer, default='NA')
    df_BOMStage[col_MPBatch_Activity1Flow_Type] = np.select(conditions_BOM, choices_BOM_Type, default='NA')
    
    # 칼럼정리
    cList_Out = [col_VersionVersionName, col_Activity1Activity1
               , col_MPBatch_Activity1Flow_Layer, col_MPBatch_Activity1Flow_Type]
    df_BOMStage = df_BOMStage[cList_Out]
    df_BOMStage.drop_duplicates(inplace=True)
    
    vdCommon.gfn_saveDf(df_BOMStage, 'df_BOMStage',False)
    vdCommon.gfn_stepLog('=====> STEP 1-2 : BOM data Create End')
    
    ################################################################################################################
    # STEP 2 :  BOD  SET 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2-1-1 : df_BODStage Create 1')
    
    #df_in_BODListMtrl ----------------------------------------
    # from site stage
    df_BODStage_1 = df_in_BODListMtrl.merge(df_in_Location, on=[col_LocationLocation], how='left')
    df_BODStage_1.rename(columns={col_LocationSiteStage:col_fromsitestage}, inplace=True)
    del df_in_BODListMtrl
    
    # to site stage
    df_BODStage_1 = df_BODStage_1.merge(df_in_Location, left_on=[col_SubLocationSubLocation]
                                        , right_on=[col_LocationLocation], how='left', suffixes=('', '_y'))
    df_BODStage_1.rename(columns={col_LocationSiteStage: col_toSiteStage}, inplace=True)
    
    # a.location||'_'||a.sublocation||"_"||a.transport mode activity1, 
    df_BODStage_1[col_Activity1Activity1] = (df_BODStage_1[col_LocationLocation] + '_' +
                                             df_BODStage_1[col_SubLocationSubLocation] + '_' + 
                                             df_BODStage_1[col_TransModeTransMode]) 
    
    # 칼럼정리
    df_BODStage_1 = df_BODStage_1[[col_VersionVersionName, col_Activity1Activity1, col_fromsitestage, col_toSiteStage]]
    df_BODStage_1.drop_duplicates(inplace=True)
    vdCommon.gfn_saveDf(df_BODStage_1, 'df_BODStage_1',False)
    
    # df_in_BODItem ------------------------------------------- 
    # from site stage
    df_BODStage_2 = df_in_BODItem.merge(df_in_Location, on=[col_LocationLocation], how='left')
    df_BODStage_2.rename(columns={col_LocationSiteStage: col_fromsitestage}, inplace=True)
    del df_in_BODItem
    
    # to site stage
    df_BODStage_2 = df_BODStage_2.merge(df_in_Location, left_on=[col_SubLocationSubLocation]
                                        , right_on=[col_LocationLocation], how='left', suffixes=('', '_y'))
    df_BODStage_2.rename(columns={col_LocationSiteStage: col_toSiteStage}, inplace=True)
    
    # a.location||'_'||a.sublocation||"_"||a.transport mode activity1,
    df_BODStage_2[col_Activity1Activity1] = (df_BODStage_2[col_LocationLocation] + '_' +
                                             df_BODStage_2[col_SubLocationSubLocation] + '_' +
                                             df_BODStage_2[col_TransModeTransMode])
    
    # 칼럼정리
    df_BODStage_2 = df_BODStage_2[[col_VersionVersionName, col_Activity1Activity1, col_fromsitestage, col_toSiteStage]]
    df_BODStage_2.drop_duplicates(inplace=True)
    
    vdCommon.gfn_saveDf(df_BODStage_2, 'df_BODStage_2',False)
    
    # concat ------------------------------------------------------
    df_BODStage = pd.concat([df_BODStage_1, df_BODStage_2])
    df_BODStage.drop_duplicates(inplace=True)
    del [df_BODStage_1, df_BODStage_2]
    
    vdCommon.gfn_saveDf(df_BODStage, 'df_BODStage 1',False)
    #save_csv_file(df_BODStage, 'df_BODStage')
    vdCommon.gfn_stepLog('=====> STEP 2-1-2 : df_BODStage Create 1 End')
    #--------------------------------------------------------------------------------------------------------
    
    vdCommon.gfn_stepLog('=====> STEP 2-2-1 : df_BODStage Create 2')
    
    conditions_BOD = [
        df_BODStage[col_fromsitestage].isin(['SP']) & df_BODStage[col_toSiteStage].isin(['MF_SET', 'MF', 'MF_LCM', 'MF_LCM_EX']), #1
        df_BODStage[col_fromsitestage].isin(['MF_LCM', 'MF_LCM_EX']) & df_BODStage[col_toSiteStage].isin(['MF_LCM', 'MF_LCM_EX']), #3
        df_BODStage[col_fromsitestage].isin(['MF_LCM_EX', 'MF_LCM', 'MF_KD']) & df_BODStage[col_toSiteStage].isin(['MF_SET', 'MF']), #3
        df_BODStage[col_fromsitestage].isin(['MF_SET', 'MF', 'MF_KD']) & df_BODStage[col_toSiteStage].isin(['DC_HUB', 'DC_HUB_MC', 'DC_HUB_MC_AP2']), #5
        df_BODStage[col_fromsitestage].isin(['MF', 'MF_SET']) & df_BODStage[col_toSiteStage].isin(['MF', 'MF_SET', 'MF_KD']), #5
        df_BODStage[col_fromsitestage].isin(['MF_SET', 'MF', 'MF_KD']) & df_BODStage[col_toSiteStage].isin(['DC']), #6
        df_BODStage[col_fromsitestage].isin(['DC_HUB', 'DC_HUB_MC', 'DC_HUB_MC_AP2']) & df_BODStage[col_toSiteStage].isin(['DC']), #6
        df_BODStage[col_fromsitestage].isin(['DC']) & df_BODStage[col_toSiteStage].isin(['DC']), #6
        True,
    ]
        
    choices_BOD_Layer = [
        '1',
        '3',
        '3',
        '5',
        '5',
        '6',
        '6',
        '6',
        '7',     # ELSE
    ]
    
    choices_BOD_Type = [
        'Supply to SET BOD', #1
        'LCM to LCM BOD',    #3
        'LCM to SET BOD',    #3
        'SET to HUB BOD',    #5
        'SET to SET BOD',    #5
        'SET to DC BOD',     #6
        'HUB to DC BOD',     #6
        'DC to DC BOD',      #6
        'Others',   # ELSE
    ]
    
    df_BODStage[col_MPBatch_Activity1Flow_Layer] = np.select(conditions_BOD, choices_BOD_Layer, default='NA')
    df_BODStage[col_MPBatch_Activity1Flow_Type] = np.select(conditions_BOD, choices_BOD_Type, default='NA')
    #save_csv_file(df_BODStage, 'df_BODStage')
    # 칼럼정리
    df_BODStage = df_BODStage[cList_Out]
    df_BODStage.drop_duplicates(inplace=True)
    
    vdCommon.gfn_saveDf(df_BODStage, 'df_BODStage',False)
    #save_csv_file(df_BODStage, 'df_BODStage')
    vdCommon.gfn_stepLog('=====> STEP 2-2-2 : df_BODStage Create 2 End')
        
    ################################################################################################################
    # STEP 3 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 3 : Final output table create')
    
    # out Data 생성 :
    df_out_Activity1Flow = pd.concat([df_BOMStage, df_BODStage])
    del [df_BOMStage,df_BODStage]
    
    # 버전 처리
    #df_out_Activity1Flow[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_Activity1Flow.shape
    note(f'=====> Final df_out_Activity1Flow rows : {row_count}, column : {col_count}')
    vdCommon.gfn_saveDf(df_out_Activity1Flow, 'df_out_Activity1Flow',False)
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_Activity1Flow, 'df_out_Activity1Flow')
    
    vdCommon.gfn_stepLog('=====> STEP 3-1 : Final output table create End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_Activity1Flow = pd.DataFrame([], columns=[])
    
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