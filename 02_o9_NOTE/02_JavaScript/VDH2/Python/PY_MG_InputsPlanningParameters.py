"""
* 프로그램명 
    - PY_MG_InputsPlanningParameters

* 내용
    - MP Engine 수행을 위한 Parameter 입력 
      . 기본 전략은 필요시 UI에서 변경하도록 함. 
      . Rolling 필요 날짜만 Update 
 
    - 대상 Measure   
      . W Plan Current Bucket    -- W Solver Current Bucket 
      . W Plan Start Bucket      -- W Solver Start Bucket 
      . W Plan End Bucket        -- W Solver End Bucket 
      . W Plan Start Date        -- W Plan Start Bucket Start Date
      . W Plan End Date          -- W Plan End Bucket 의 End Date   


       * Time Rolling / .Js
         W Solver Current Bucket     1로 업데이트    / 이전주는 NULL 
         W Solver Start Bucket       1로 업데이트    / 이전주는 NULL 
         W Solver End Bucket         1로 업데이트    / 이전주는 NULL 

* 변경이력
    - 2024.08.30 / 양희영 / Create
    - 2025.06.27 / 양희영 / Update


* Flow Summary

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_PlanningHorizon : Select (&PlanningHorizon * [Time].[Day]) on row, 
                              () on column include memberproperties{[Time].[Week], Key,  [W Solver Start Bucket], [W Solver End Bucket]};
    - df_in_CurrentWeek : Select (&MPCurrentWeek * [Time].[Day]);
    - df_in_VersionName : SELECT ([Version].[Version Name]);

* Output Tables
    - df_out_InputsPlanningParameters : 001.001W Solver Inputs Planning Parameters : Granularity ( Version Name )
          Select ([Version].[Version Name].[CWV_MP] ) on row, 
          ({Measure.[W Plan Start Bucket], Measure.[W Plan End Bucket], Measure.[W Plan Start Date], Measure.[W Plan End Date], Measure.[W Capacity Constrained],
           Measure.[W Global Demand Build Ahead Limit], Measure.[W Global Demand Build Late Limit], Measure.[W LP Solver Name], Measure.[W Late Plan Strategy],
           Measure.[W Material Constrained], Measure.[W Min Time Hard Peg], Measure.[W Plan Date Hard Peg], Measure.[W Skip SS For Unviable Buckets],  
           Measure.[W Solver Delete Data], Measure.[W Solver Demand Slice Factor], Measure.[W Solver Demand Slice Threshold], Measure.[W Solver Flag Allow NOH], 
           Measure.[W Solver Flag Expedite WIP], Measure.[W Solver Flag Inventory Plan Policy], Measure.[W Solver Flag Inventory Plan Strategy], 
           Measure.[W Solver Flag Inventory Plan Type], Measure.[W Solver Flag Minimize Inventory Build Ahead], Measure.[W Solver Flag Minimize No Carry Violations], 
           Measure.[W Solver Flag No Peggings], Measure.[W Solver Flag Respect Freeze Window For WIPs], Measure.[W Solver Flag Shelf Life Plan], 
           Measure.[W Solver Flag SupplyCode Plan], Measure.[W Solver Flag Try Material Reallocation In RCA], Measure.[W Solver Inventory Plan Bands], 
           Measure.[W Solver SS Build Ahead Limit], Measure.[W Storage Constrained]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_InputsPlanningParameters] for measures {[W Plan Start Bucket]} using scope (&MPV) 
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
str_instance = 'PY_MG_InputsPlanningParameters'
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )

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
    vdCommon.gfn_stepLog('=====> DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    col_VersionVersionName = 'Version.[Version Name]'
    col_TimeWeek           = 'Time.[Week]'
    col_TimeDay            = 'Time.[Day]'    
    
    col_WPlanStartBucket                        = 'W Plan Start Bucket'
    col_WPlanEndBucket                          = 'W Plan End Bucket'
    col_WPlanStartDate                          = 'W Plan Start Date'
    col_WPlanEndDate                            = 'W Plan End Date'
    col_WPlanCurrentBucket                      = 'W Plan Current Bucket'
    col_WPlanCurrentDate                        = 'W Plan Current Date'
    col_WPlanDateHardPeg                        = 'W Plan Date Hard Peg'
    col_WCapacityConstrained                    = 'W Capacity Constrained'
    col_WGlobalDemandBuildAheadLimit            = 'W Global Demand Build Ahead Limit'
    col_WGlobalDemandBuildLateLimit             = 'W Global Demand Build Late Limit'
    col_WLPSolverName                           = 'W LP Solver Name'
    col_WLatePlanStrategy                       = 'W Late Plan Strategy'
    col_WMaterialConstrained                    = 'W Material Constrained'
    col_WMinTimeHardPeg                         = 'W Min Time Hard Peg'
    col_WSkipSSForUnviableBuckets               = 'W Skip SS For Unviable Buckets'
    col_WSolverDeleteData                       = 'W Solver Delete Data'
    col_WSolverDemandSliceFactor                = 'W Solver Demand Slice Factor'
    col_WSolverDemandSliceThreshold             = 'W Solver Demand Slice Threshold'
    col_WSolverFlagAllowNOH                     = 'W Solver Flag Allow NOH'
    col_WSolverFlagExpediteWIP                  = 'W Solver Flag Expedite WIP'
    col_WSolverFlagInventoryPlanPolicy          = 'W Solver Flag Inventory Plan Policy'
    col_WSolverFlagInventoryPlanStrategy        = 'W Solver Flag Inventory Plan Strategy'
    col_WSolverFlagInventoryPlanType            = 'W Solver Flag Inventory Plan Type'
    col_WSolverFlagMinimizeInventoryBuildAhead  = 'W Solver Flag Minimize Inventory Build Ahead'
    col_WSolverFlagMinimizeNoCarryViolations    = 'W Solver Flag Minimize No Carry Violations'
    col_WSolverFlagNoPeggings                   = 'W Solver Flag No Peggings'
    col_WSolverFlagRespectFreezeWindowForWIPs   = 'W Solver Flag Respect Freeze Window For WIPs'
    col_WSolverFlagShelfLifePlan                = 'W Solver Flag Shelf Life Plan'
    col_WSolverFlagSupplyCodePlan               = 'W Solver Flag SupplyCode Plan'
    col_WSolverFlagTryMaterialReallocationInRCA = 'W Solver Flag Try Material Reallocation In RCA'
    col_WSolverInventoryPlanBands               = 'W Solver Inventory Plan Bands'
    col_WSolverSSBuildAheadLimit                = 'W Solver SS Build Ahead Limit'
    col_WStorageConstrained                     = 'W Storage Constrained'
    
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

        df_in_PlanningHorizon = read_csv_file("df_in_PlanningHorizon")
        df_in_CurrentWeek     = read_csv_file("df_in_CurrentWeek")
        df_in_VersionName     = read_csv_file("df_in_VersionName")
            
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    df_in_PlanningHorizon = df_in_PlanningHorizon.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_PlanningHorizon[col_TimeDay] = pd.to_datetime(df_in_PlanningHorizon[col_TimeDay], format='%Y-%m-%d')
    
    df_in_CurrentWeek = df_in_CurrentWeek.astype({col_TimeWeek: 'str'}, copy=True)
    df_in_CurrentWeek[col_TimeDay] = pd.to_datetime(df_in_CurrentWeek[col_TimeDay], format='%Y-%m-%d')
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    vdCommon.gfn_saveDf(df_in_PlanningHorizon, 'df_in_PlanningHorizon',False)
    vdCommon.gfn_saveDf(df_in_CurrentWeek, 'df_in_CurrentWeek',False)
    vdCommon.gfn_saveDf(df_in_VersionName, 'df_in_VersionName',False)
    
    vdCommon.gfn_stepLog('=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : week(min, max), day(min, max) df 구성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 : week(min, max), day(min, max) data create')
    # Version Name 값 Setting
    VERSION_VALUE = df_in_VersionName.loc[0, col_VersionVersionName]
    
    # &PlanningHorizon 처리-------
    df_in_PlanningHorizon[col_VersionVersionName] = VERSION_VALUE #paramOutVersion
    df_in_PlanningHorizon[col_WPlanEndBucket]     = df_in_PlanningHorizon[col_TimeWeek]
    df_in_PlanningHorizon[col_WPlanEndDate]       = df_in_PlanningHorizon[col_TimeDay]
    
    df_out_InputsPlanningParameters = df_in_PlanningHorizon.groupby([col_VersionVersionName],
                                       as_index=False).agg({col_TimeWeek:"min", col_WPlanEndBucket:"max",
                                                            col_TimeDay:"min", col_WPlanEndDate:"max"})
    df_out_InputsPlanningParameters.rename(columns={col_TimeWeek:col_WPlanStartBucket, col_TimeDay:col_WPlanStartDate}, inplace=True)
    # min(week)  -1  : W Plan Start Bucket
    df_out_InputsPlanningParameters[col_WPlanStartBucket] = df_out_InputsPlanningParameters[col_WPlanStartBucket].apply(lambda x : common.gfn_add_week(x, -1))
    # min(day)   -7  : W Plan Start Date
    df_out_InputsPlanningParameters[col_WPlanStartDate] = (df_out_InputsPlanningParameters[col_WPlanStartDate] - datetime.timedelta(days=7))
    del df_in_PlanningHorizon
    
    # &MPCurrentWeek 처리------ 
    df_in_CurrentWeek[col_VersionVersionName] = VERSION_VALUE #paramOutVersion
    df_in_CurrentWeek[col_WPlanCurrentBucket] = df_in_CurrentWeek[col_TimeWeek]
    df_in_CurrentWeek[col_WPlanCurrentDate]   = df_in_CurrentWeek[col_TimeDay]
    
    df_CurrentWeek = df_in_CurrentWeek.groupby([col_VersionVersionName, col_WPlanCurrentBucket], as_index=False).agg({col_WPlanCurrentDate:"min"})
    #vdCommon.gfn_saveDf(df_CurrentWeek, 'df_CurrentWeek',False)
    
    # Merge : df_out_InputsPlanningParameters
    df_out_InputsPlanningParameters = df_out_InputsPlanningParameters.merge(df_CurrentWeek, on=[col_VersionVersionName], how='inner')
    #vdCommon.gfn_saveDf(df_out_InputsPlanningParameters, 'df_out_InputsPlanningParameters',False)
    
    vdCommon.gfn_stepLog('=====> STEP 1-1 : week(min, max), day(min, max) create End')
    
    ################################################################################################################
    # STEP 2 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 : Final output table create')
    
    # out Data 생성 
    # W Plan Start Bucket : String, W Plan Start Date : Datetime
    # W Plan End Bucket   : String, W Plan End Date   : Datetime
    df_out_InputsPlanningParameters[col_WCapacityConstrained]                    = 'TRUE' #'W Capacity Constrained"' String
    df_out_InputsPlanningParameters[col_WGlobalDemandBuildAheadLimit]            = 0 #'W Global Demand Build Ahead Limit' #Integer
    df_out_InputsPlanningParameters[col_WGlobalDemandBuildLateLimit]             = 0 #'W Global Demand Build Late Limit' #Integer
    df_out_InputsPlanningParameters[col_WLPSolverName]                           = 'GurobiSolver' #'W LP Solver Name' #Picklist
    df_out_InputsPlanningParameters[col_WLatePlanStrategy]                       = 'LINEAR' #'W Late Plan Strategy' #String
    df_out_InputsPlanningParameters[col_WMaterialConstrained]                    = 'TRUE' #'W Material Constrained' #String
    df_out_InputsPlanningParameters[col_WMinTimeHardPeg]                         = 'FALSE' #'W Min Time Hard Peg' #String
    df_out_InputsPlanningParameters[col_WPlanDateHardPeg]                        = 'FALSE' #'W Plan Date Hard Peg' #String
    df_out_InputsPlanningParameters[col_WSkipSSForUnviableBuckets]               = 'FALSE' #'W Skip SS For Unviable Buckets' #String
    df_out_InputsPlanningParameters[col_WSolverDeleteData]                       = 'TRUE' #'W Solver Delete Data' #String
    df_out_InputsPlanningParameters[col_WSolverDemandSliceFactor]                = 5 #'W Solver Demand Slice Factor' #Number
    df_out_InputsPlanningParameters[col_WSolverDemandSliceThreshold]             = 100 #'W Solver Demand Slice Threshold' #Number
    df_out_InputsPlanningParameters[col_WSolverFlagAllowNOH]                     = False #'W Solver Flag Allow NOH'    #Boolean
    df_out_InputsPlanningParameters[col_WSolverFlagExpediteWIP]                  = '' #np.nan #'W Solver Flag Expedite WIP' #Boolean : Null
    df_out_InputsPlanningParameters[col_WSolverFlagInventoryPlanPolicy]          = 'TARGET_LEVEL' #'W Solver Flag Inventory Plan Policy' #Picklist
    df_out_InputsPlanningParameters[col_WSolverFlagInventoryPlanStrategy]        = 'MOVE_IN' #'W Solver Flag Inventory Plan Strategy' #Picklist
    df_out_InputsPlanningParameters[col_WSolverFlagInventoryPlanType]            = 'QUANTITY_WOS' #'W Solver Flag Inventory Plan Type' #Picklist
    df_out_InputsPlanningParameters[col_WSolverFlagMinimizeInventoryBuildAhead]  = 'FALSE' #'W Solver Flag Minimize Inventory Build Ahead' #String
    df_out_InputsPlanningParameters[col_WSolverFlagMinimizeNoCarryViolations]    = True #'W Solver Flag Minimize No Carry Violations' #Boolean
    df_out_InputsPlanningParameters[col_WSolverFlagNoPeggings]                   = 'FALSE' #'W Solver Flag No Peggings' #String
    df_out_InputsPlanningParameters[col_WSolverFlagRespectFreezeWindowForWIPs]   = True #'W Solver Flag Respect Freeze Window For WIPs' #Boolean
    df_out_InputsPlanningParameters[col_WSolverFlagShelfLifePlan]                = 'FALSE' #'W Solver Flag Shelf Life Plan' #String
    df_out_InputsPlanningParameters[col_WSolverFlagSupplyCodePlan]               = 'FALSE' #'W Solver Flag SupplyCode Plan' #String
    df_out_InputsPlanningParameters[col_WSolverFlagTryMaterialReallocationInRCA] = True #'W Solver Flag Try Material Reallocation In RCA' #Boolean
    df_out_InputsPlanningParameters[col_WSolverInventoryPlanBands]               = 0 #'W Solver Inventory Plan Bands' #Number
    df_out_InputsPlanningParameters[col_WSolverSSBuildAheadLimit]                = 0 #'W Solver SS Build Ahead Limit' #Number
    df_out_InputsPlanningParameters[col_WStorageConstrained]                     = 'FALSE' #'W Storage Constrained' #String
    
    # 버전 처리 : 위에서 입력됨.    

    row_count, col_count = df_out_InputsPlanningParameters.shape
    note(f'=====> df_out_InputsPlanningParameters rows : {row_count}, column : {col_count}')
    
    vdCommon.gfn_saveDf(df_out_InputsPlanningParameters, 'df_out_InputsPlanningParameters',False)
    vdCommon.gfn_stepLog('=====> STEP 2-1 : Final output table create End')
    
    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_InputsPlanningParameters, 'df_out_InputsPlanningParameters')
        
    vdCommon.gfn_stepLog('=====> STEP 2-2 : End')
    
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_InputsPlanningParameters = pd.DataFrame([], columns=[])

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