"""
* 프로그램명 
    - PY_MG_ActivityShare

* 내용
    - Time Phased BOM Version Priority 반영
    - 관리 UI - BOM Version Management
    - Priority = -1 로 지정하면 BOM Version을 할당하지 않음.

* 변경이력
    - 2024.08.23 / 양희영 / Create
    - 2025.06.27 / 양희영 / Create

* Input

* Flow Summary
    

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_BOMVersionPrty : Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [BOM Info].[BOM Version] ) on row, 
                             ({Measure.[BOM Version Mgmt W_Priority Result],  Measure.[BOM Version Prty Aggr W_Valid], Measure.[BOM Version Prty Aggr_Prty]}) on column;

    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
                          ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp], Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) 
                          on column.filter(Measure.[Item Site Asn_Engine Flag]== true);

    - df_in_BOMMaster : Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID]) on row, 
                        ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Priority], Measure.[BOM Master_Status]}) on column;

* Output Tables
    - df_out_ActivityShare : 001.008W Solver Inputs Activity Share
          Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, 
                  ({Measure.[W Activity Priority Time Varying], Measure.[W Activity Share]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_ActivityShare] for measures {[W Activity Priority Time Varying]} using scope (&MPV *  &PlanningHorizon * &MFLocation) using arguments {
      (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (ParamOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
      
"""


from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import os
import pandas as pd
import numpy as np
import datetime as dt
import traceback
import gc
import tracemalloc
from datetime import datetime

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_ActivityShare'
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
    vdCommon.gfn_stepLog(f'=====> DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName = 'Version.[Version Name]'
    itemItem           = 'Item.[Item]'
    timeWeek           = 'Time.[Week]'
    locationLocation   = "Location.[Location]"
    activity1activity1 = "Activity1.[Activity1]"
    activity2activity2 = "Activity2.[Activity2]"
    activity3Activity3 = "Activity3.[Activity3]"
    bOMInfoBOMVersion  = 'BOM Info.[BOM Version]'
    bOMInfoBOMID       = 'BOM Info.[BOM ID]'
    
    bOMVersionPrtyAggr_Prty        = 'BOM Version Prty Aggr_Prty'    
    wActivityPriorityTimeVarying   = 'W Activity Priority Time Varying'
    wActivityShare                 = 'W Activity Share'
    
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog(f'=====> Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_BOMVersionPrty = read_csv_file("df_in_BOMVersionPrty")
        df_in_ItemSiteAsn    = read_csv_file("df_in_ItemSiteAsn")
        df_in_BOMMaster      = read_csv_file("df_in_BOMMaster")
        
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    df_in_BOMVersionPrty = df_in_BOMVersionPrty.astype({timeWeek: 'str',
                                                        bOMVersionPrtyAggr_Prty: 'str'}, copy=True)
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    vdCommon.gfn_saveDf(df_in_BOMVersionPrty, 'df_in_BOMVersionPrty',False)
    vdCommon.gfn_saveDf(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',False)
    vdCommon.gfn_saveDf(df_in_BOMMaster, 'df_in_BOMMaster',False)
    
    vdCommon.gfn_stepLog(f'=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 :  Activity Share data Create
    ################################################################################################################
    vdCommon.gfn_stepLog(f'=====> STEP 1 : input data Create')
    # -df_in_ItemSiteAsn distinct 필요없음, Version Name, Itme, Location
    # column 정리
    df_in_ItemSiteAsn = df_in_ItemSiteAsn[[versionVersionName, itemItem, locationLocation]]
    
    df_in_BOMVersionPrty = df_in_BOMVersionPrty.merge(df_in_ItemSiteAsn, on=[versionVersionName,itemItem,locationLocation], how='inner')
    df_in_BOMVersionPrty[bOMInfoBOMID] = df_in_BOMVersionPrty[itemItem] + '_' + df_in_BOMVersionPrty[bOMInfoBOMVersion]
    del df_in_ItemSiteAsn
    vdCommon.gfn_saveDf(df_in_BOMVersionPrty, "df_in_BOMVersionPrty Merge",False)
    vdCommon.gfn_stepLog(f'=====> STEP1-1 : df_in_BOMVersionPrty & df_in_ItemSiteAsn Merge End')
    
    
    df_in_BOMMaster.drop(columns=[locationLocation], inplace=True) # Merge전 중복칼럼 삭제
    df_ActivityShare = df_in_BOMVersionPrty.merge(df_in_BOMMaster, on=[versionVersionName,bOMInfoBOMID], how='inner')
    del [df_in_BOMVersionPrty, df_in_BOMMaster]
    vdCommon.gfn_saveDf(df_ActivityShare, 'df_ActivityShare Merge',False)
    vdCommon.gfn_stepLog(f'=====> STEP1-2 : df_in_BOMVersionPrty & df_in_BOMMaster Merge End')
    
    df_ActivityShare[activity1activity1] = df_ActivityShare[bOMInfoBOMID]
    df_ActivityShare[activity2activity2] = 'RT_' + df_ActivityShare[bOMInfoBOMID] + '@' + df_ActivityShare[locationLocation]
    df_ActivityShare[activity3Activity3] = df_ActivityShare[itemItem]
    df_ActivityShare[wActivityPriorityTimeVarying] = (np.select([(df_ActivityShare[bOMVersionPrtyAggr_Prty] == 'X'),True,],
                                                    [-1, df_ActivityShare[bOMVersionPrtyAggr_Prty]])).astype('int64')
    #df_ActivityShare[wActivityShare] = np.nan
    
    vdCommon.gfn_saveDf(df_ActivityShare, 'df_ActivityShare',False)
    vdCommon.gfn_stepLog(f'=====> STEP 1-9 : input data Create End')
    
    ################################################################################################################
    # STEP 2 : 001.008W Solver Inputs Activity Share : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog(f'=====> STEP 2 : Final output table create')
    
    # out Data 생성 : : df_BOD & df_BOM 통합
    cList_Out = [versionVersionName, itemItem, timeWeek, locationLocation, activity1activity1, activity2activity2,
                 activity3Activity3, wActivityPriorityTimeVarying]
    df_out_ActivityShare = df_ActivityShare[cList_Out].copy()
    del df_ActivityShare
    
    # 버전 처리
    #df_out_ActivityShare[versionVersionName] = paramOutVersion
    #print_df(df_out_ActivityShare, 'df_out_ActivityShare')
    
    row_count, col_count = df_out_ActivityShare.shape
    note(f'=====> Final df_out_ActivityShare rows : {row_count}, column : {col_count}')
    
    vdCommon.gfn_saveDf(df_out_ActivityShare, 'df_out_ActivityShare',False)
    vdCommon.gfn_stepLog(f'=====> STEP 2-1 : Final output table create End')
    
    if is_local:
        vdCommon.gfn_stepLog(f'=====> Output csv create')
        save_csv_file(df_out_ActivityShare, 'df_out_ActivityShare') 

    
    vdCommon.gfn_stepLog(f'=====> STEP 2-2 : End')

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_ActivityShare = pd.DataFrame([], columns=[])
    
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