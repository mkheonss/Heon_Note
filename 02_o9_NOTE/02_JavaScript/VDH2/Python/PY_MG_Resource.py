"""
* 프로그램명 
    - PY_MG_Resource

* 내용
    - Resoruce Member 생성용 메저 Insert

* 변경이력
- 2024.08.28 / 양희영 / Create
- 2024.10.08 : 이름변경 PY_MG_ResourceCreation -> PY_MG_Resource
- 2025.10.16 : 양희영 / update


* Flow Summary

* Execution 
* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.
* Input Tables
    - df_in_ItemSiteAsn : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, 
                          ({Measure.[Item Site Asn_Cur Status], Measure.[Item Site Asn_Engine Flag], Measure.[Item Site Asn_Item Grp],Measure.[Item Site Asn_Sales Prod Asn], Measure.[Item Site Asn_Stage]}) 
                          on column.filter(Measure.[Item Site Asn_Engine Flag]== true);
    - df_in_ConstraintGroupDetail : Select ([Version].[Version Name] * [Group].[Group ID] ) on row, 
                                    ({Measure.[Const Grp Detail_Desc], Measure.[Const Grp Detail_From Site], Measure.[Const Grp Detail_Item], Measure.[Const Grp Detail_Product Group], Measure.[Const Grp Detail_To Site]}) on column;
    - df_in_ConstraintGroupDetailW : Select ([Version].[Version Name] * &PlanningHorizon * [Group].[Group ID] ) on row, 
                                     ({Measure.[Const Grp Detail W_Lock Flag], Measure.[Const Grp Detail W_Qty]}) on column;
    - df_in_CTNGrpConst : Select ([Version].[Version Name] * [Sequence].[Sequence] * [Group].[Group ID] ) on row, 
                          ({Measure.[CTN Grp Const_GC], Measure.[CTN Grp Const_AP2], Measure.[CTN Grp Const_Apply Flag], Measure.[CTN Grp Const_Start Week], Measure.[CTN Grp Const_End Week], 
                          Measure.[CTN Grp Const_From Site],  Measure.[CTN Grp Const_Frozen SOP Override Qty] })  on column.filter(Measure.[CTN Grp Const_Apply Flag]== "Y");
    - df_in_CTNItemConst : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[AP2] ) on row, 
                           ({Measure.[CTN Item Const_Apply Flag], Measure.[CTN Item Const_Start Week], Measure.[CTN Item Const_End Week], Measure.[CTN Item Const_Frozen SOP Override Qty]}) 
                           on column.filter(Measure.[CTN Item Const_Apply Flag] == "Y");
    - df_PlanStartEndWeek : Select ([Version].[Version Name] ) on row, ({Measure.[MP Plan End Week], Measure.[MP Plan Start Week]}) on column;
    - df_in_WorkingCalendarLine : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Work Type].[Work Type] * [Line].[Line] * &DataSetMP ) on row, 
                                  ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column.filter(Measure.[Work Cal Line_Time] > 0);
    - df_in_CapaWeek : MG: Capacity Week
                       Select ([Version].[Version Name] * [Time].[Week] * [Group].[Group ID] ) on row, ({Measure.[Capa Week_Qty]}) on column;
    - df_in_CapaPeriod : MG: Capacity Period
                        Select ([Version].[Version Name] * [Time].[Week] * [To Time].[To Week] * [Group].[Group ID] ) on row, ({Measure.[Capa Period_Qty]}) on column;
    - df_in_CapaItemSite : MG: Capacity Item Site
                           Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Group].[Group ID] ) on row, 
                           ({Measure.[Capa Item Site_Asn]}) on column.filter(Measure.[Capa Item Site_Asn] == "Y");
    - df_in_CapaItemSiteMap : MG: Capacity Item Site Map
                              Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, 
                              ({Measure.[Capa Item Site Map_Asn]}) on column.filter(Measure.[Capa Item Site Map_Asn] == "Y");
    
* Output Tables
    - df_out_Resource : Select ([Version].[Version Name] * [MP Batch_Sequence].[MP Batch_Sequence_ID] ) on row, 
                        ({Measure.[MP Batch_Resource Bulk Member Creation_Group ID], Measure.[MP Batch_Resource Bulk Member Creation_Index], 
                          Measure.[MP Batch_Resource Bulk Member Creation_ResType], Measure.[MP Batch_Resource Bulk Member Creation_Resource]}) on column;
* 테스트 스크립트
    EXEC plugin instance [PY_MG_Resource] for measures {[MP Batch_Resource Bulk Member Creation_Resource]} using scope (&MPV * &MFLocation * &PlanningHorizon) using arguments {
      (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (ParamOutVersion, "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
      
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


########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_Resource'
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

try:################################################################################################################
    # DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====> DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    versionVersionName     = 'Version.[Version Name]'
    groupGroupID           = 'Group.[Group ID]'
    itemItem               = 'Item.[Item]'
    lineLine               = 'Line.[Line]'
    locationLocation       = 'Location.[Location]'
    subLocationSubLocation = 'Sub Location.[Sub Location]'
    resourceResource       = 'Resource.[Resource]'
    timeWeek               = 'Time.[Week]'
    
    constGrpDetail_FromSite = 'Const Grp Detail_From Site'
    constGrpDetail_ToSite   = 'Const Grp Detail_To Site'
    cTNGrpConst_AP2         = 'CTN Grp Const_AP2'
    cTNGrpConst_StartWeek   = 'CTN Grp Const_Start Week'
    cTNGrpConst_EndWeek     = 'CTN Grp Const_End Week'
    cTNGrpConst_GC          = 'CTN Grp Const_GC'
    cTNItemConst_AP2        = 'CTN Item Const_AP2'
    salesDomainAP2          = 'Sales Domain.[AP2]'
    cTNItemConst_StartWeek  = 'CTN Item Const_Start Week'
    cTNItemConst_EndWeek    = 'CTN Item Const_End Week'
    cTNItemConst_GC         = 'CTN Item Const_GC'
    mPPlanStartWeek         = 'MP Plan Start Week'
    mPPlanEndWeek           = 'MP Plan End Week'
    mPBatch_SequenceMPBatch_Sequence_ID         = 'MP Batch_Sequence.[MP Batch_Sequence_ID]'
    mPBatch_ResourceBulkMemberCreation_Index    = 'MP Batch_Resource Bulk Member Creation_Index'
    mPBatch_ResourceBulkMemberCreation_Resource = 'MP Batch_Resource Bulk Member Creation_Resource'
    mPBatch_ResourceBulkMemberCreation_ResType  = 'MP Batch_Resource Bulk Member Creation_ResType'
    resource                = 'resource'
    resourcetype            = 'resourcetype'
    
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step(f'=====> Input table load')

    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_ItemSiteAsn            = read_csv_file("df_in_ItemSiteAsn")
        df_in_ConstraintGroupDetail  = read_csv_file("df_in_ConstraintGroupDetail")
        df_in_ConstraintGroupDetailW = read_csv_file("df_in_ConstraintGroupDetailW")
        df_in_CTNGrpConst            = read_csv_file("df_in_CTNGrpConst")
        df_PlanStartEndWeek          = read_csv_file("df_PlanStartEndWeek")
        df_in_CTNItemConst           = read_csv_file("df_in_CTNItemConst")
        df_in_WorkingCalendarLine    = read_csv_file("df_in_WorkingCalendarLine")
        df_in_CapaWeek               = read_csv_file("df_in_CapaWeek")
        df_in_CapaPeriod             = read_csv_file("df_in_CapaPeriod")
        df_in_CapaItemSite           = read_csv_file("df_in_CapaItemSite")
        df_in_CapaItemSiteMap        = read_csv_file("df_in_CapaItemSiteMap")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # DATA TYPE 설정
    #df_in_CTNGrpConst = df_in_CTNGrpConst.astype({cTNGrpConst_AP2:'str'}, copy=True)
    #df_in_CTNItemConst = df_in_CTNItemConst.astype({cTNItemConst_AP2:'str'}, copy=True)

    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')

    print_df(df_in_ItemSiteAsn, 'df_in_ItemSiteAsn',False)
    print_df(df_in_ConstraintGroupDetail, 'df_in_ConstraintGroupDetail',False)
    print_df(df_in_ConstraintGroupDetailW, 'df_in_ConstraintGroupDetailW',False)
    print_df(df_in_CTNGrpConst, 'df_in_CTNGrpConst',False)
    print_df(df_PlanStartEndWeek, 'df_PlanStartEndWeek',False)
    print_df(df_in_CTNItemConst, 'df_in_CTNItemConst',False)
    print_df(df_in_WorkingCalendarLine, 'df_in_WorkingCalendarLine',False)
    print_df(df_in_CapaWeek, 'df_in_CapaWeek',False)
    print_df(df_in_CapaPeriod, 'df_in_CapaPeriod',False)
    print_df(df_in_CapaItemSite, 'df_in_CapaItemSite',False)
    print_df(df_in_CapaItemSiteMap, 'df_in_CapaItemSiteMap',False)
    
    step('=====> Input table load End')
    
    ################################################################################################################
    # STEP 1 : Resource data 생성
    ################################################################################################################
    step('=====> STEP 1 : Resource Group data create')
    # STEP1-1 -distinct location
    Location_series = df_in_ItemSiteAsn[locationLocation].unique()
    del df_in_ItemSiteAsn
    
    # STEP1-2 Location Filtering
    df_in_ConstraintGroupDetail = df_in_ConstraintGroupDetail[(df_in_ConstraintGroupDetail[constGrpDetail_FromSite].isin(Location_series))]
    print_df(df_in_ConstraintGroupDetail, 'df_in_ConstraintGroupDetail Location Filtering',False)
    
    ###############################################
    # STEP1-3 Resource_1 Merge : Production Capacity 
    df_Resource_1 = df_in_ConstraintGroupDetailW.merge(df_in_ConstraintGroupDetail, on=[versionVersionName, groupGroupID], how='inner')
    del df_in_ConstraintGroupDetailW; del df_in_ConstraintGroupDetail
    
    df_Resource_1.fillna({constGrpDetail_ToSite:'All'}, inplace=True)
    df_Resource_1[resource] = np.select([(df_Resource_1[constGrpDetail_ToSite] == 'All'), True,],
                                        [('MFC@'+df_Resource_1[groupGroupID]), 'SRC@'+df_Resource_1[groupGroupID]])
    df_Resource_1[resourcetype] = np.select([(df_Resource_1[constGrpDetail_ToSite] == 'All'), True, ], ['MFC', 'SRC'])
    
    # 칼럼 정리
    df_Resource_1 = df_Resource_1[[versionVersionName, resource,resourcetype]]
    df_Resource_1.drop_duplicates(inplace=True)
    print_df(df_Resource_1, 'df_Resource_1',False)
    
    ###############################################
    # STEP1-4 Resource_2 Merge : CTN Group
    df_Resource_2 = df_in_CTNGrpConst.merge(df_PlanStartEndWeek, on=[versionVersionName], how='inner')
    del df_in_CTNGrpConst
    
    #df_Resource_2 = df_Resource_2[(df_Resource_2[cTNGrpConst_StartWeek] >= df_Resource_2[mPPlanStartWeek]) &
    #                              (df_Resource_2[cTNGrpConst_EndWeek] <= df_Resource_2[mPPlanEndWeek])]
    df_Resource_2 = df_Resource_2[df_Resource_2[cTNGrpConst_StartWeek].isna() |
                                  (df_Resource_2[cTNGrpConst_StartWeek] >= df_Resource_2[mPPlanStartWeek])]
    df_Resource_2.fillna({cTNGrpConst_GC:'All', cTNGrpConst_AP2:'All'}, inplace=True)
    df_Resource_2 = df_Resource_2.astype({cTNGrpConst_GC: 'str', cTNGrpConst_AP2: 'str'}, copy=True)
    df_Resource_2[resource] = np.select([((df_Resource_2[cTNGrpConst_GC] == 'All') & (df_Resource_2[cTNGrpConst_AP2] == 'All')), True, ],
                                        [('MCT@'+df_Resource_2[groupGroupID]), 'SCT@'+df_Resource_2[groupGroupID]])
    df_Resource_2[resourcetype] = np.select([((df_Resource_2[cTNGrpConst_GC] == 'All') & (df_Resource_2[cTNGrpConst_AP2] == 'All')), True, ],
                                        ['MCT', 'SCT'])
    
    # 칼럼 정리
    df_Resource_2 = df_Resource_2[[versionVersionName, resource, resourcetype]]
    df_Resource_2.drop_duplicates(inplace=True)
    print_df(df_Resource_2, 'df_Resource_2',False)
    
    ###############################################
    # STEP1-4 Resource_3 Merge : CTN Item
    df_Resource_3 = df_in_CTNItemConst.merge(df_PlanStartEndWeek, on=[versionVersionName], how='inner')
    del df_in_CTNItemConst
    
    #df_Resource_3 = df_Resource_3[(df_Resource_3[cTNItemConst_StartWeek] >= df_Resource_3[mPPlanStartWeek]) &
    #                              (df_Resource_3[cTNItemConst_EndWeek] <= df_Resource_3[mPPlanEndWeek])]
    df_Resource_3 = df_Resource_3[df_Resource_3[cTNItemConst_StartWeek].isna() |
                                  (df_Resource_3[cTNItemConst_StartWeek] >= df_Resource_3[mPPlanStartWeek])]
    #df_Resource_3[salesDomainAP2] = np.nan
    df_Resource_3.fillna({salesDomainAP2: 'All'}, inplace=True)
    df_Resource_3 = df_Resource_3.astype({salesDomainAP2: 'str'}, copy=True)
    df_Resource_3[resource] = np.select([(df_Resource_3[salesDomainAP2] == 'All'), True, ],                             
                                        [('MCT@'+df_Resource_3[itemItem]+'_'+df_Resource_3[locationLocation])
                                        , 'SCT@'+df_Resource_3[itemItem]+'_'+df_Resource_3[locationLocation]])
    df_Resource_3[resourcetype] = np.select([(df_Resource_3[salesDomainAP2] == 'All'), True, ], ['MCT', 'SCT'])
    
    # 칼럼 정리
    df_Resource_3 = df_Resource_3[[versionVersionName, resource, resourcetype]]
    df_Resource_3.drop_duplicates(inplace=True)
    print_df(df_Resource_3, 'df_Resource_3',False)
    
    ###############################################
    # STEP1-5 Resource_4 Create : line calendar
    # Location Filtering
    df_in_WorkingCalendarLine = df_in_WorkingCalendarLine[(df_in_WorkingCalendarLine[locationLocation].isin(Location_series))]
    
    #Resource_4 Merge
    df_Resource_4 = df_in_WorkingCalendarLine.merge(df_PlanStartEndWeek, on=[versionVersionName], how='inner')
    del df_in_WorkingCalendarLine; del df_PlanStartEndWeek
    
    df_Resource_4 = df_Resource_4[(df_Resource_4[timeWeek] >= df_Resource_4[mPPlanStartWeek]) &
                                  (df_Resource_4[timeWeek] <= df_Resource_4[mPPlanEndWeek])]
    df_Resource_4[resource] = 'LR_'+df_Resource_4[lineLine]+'@'+df_Resource_4[locationLocation]
    df_Resource_4[resourcetype] = 'MLC'
    
    # 칼럼 정리
    df_Resource_4 = df_Resource_4[[versionVersionName, resource, resourcetype]]
    df_Resource_4.drop_duplicates(inplace=True)
    print_df(df_Resource_4, 'df_Resource_4',False)
    
    ###############################################
    # STEP1-6 Resource_5 Create : SOPFIX Routing 
    # df_in_CapaWeek & df_in_CapaItemSite Merge
    df_Resource_5_1 = df_in_CapaWeek.merge(df_in_CapaItemSite, on=[versionVersionName, groupGroupID], how='inner')
    # DENSE_RANK() OVER ( PARTITION BY '' ORDER BY B.FROMSITEID, B.ITEM ) R : B.FROMSITEID = Location.[Location]
    df_Resource_5_1['R'] = df_Resource_5_1[[locationLocation,itemItem]].apply(tuple, axis=1).rank(method='dense', ascending=True).astype('int64')
    df_Resource_5_1.sort_values('R',inplace=True)
    df_Resource_5_1[resource] = 'MFT_'+ df_Resource_5_1['R'].astype('str')
    df_Resource_5_1[resourcetype] = 'MFC'
    
    # 칼럼 정리
    df_Resource_5_1 = df_Resource_5_1[[versionVersionName, resource, resourcetype]]
    df_Resource_5_1.drop_duplicates(inplace=True)
    #print_df(df_Resource_5_1, 'df_Resource_5_1',False)
    
    # df_in_CapaPeriod & df_in_CapaItemSite Merge
    df_Resource_5_2 = df_in_CapaPeriod.merge(df_in_CapaItemSite, on=[versionVersionName, groupGroupID], how='inner')
    del df_in_CapaItemSite
    
    # DENSE_RANK() OVER ( PARTITION BY '' ORDER BY B.FROMSITEID, B.ITEM ) R : B.FROMSITEID = Location.[Location]
    df_Resource_5_2['R'] = df_Resource_5_2[[locationLocation,itemItem]].apply(tuple, axis=1).rank(method='dense', ascending=True).astype('int64')
    df_Resource_5_2.sort_values('R', inplace=True)
    df_Resource_5_2[resource] = 'MFT_' + df_Resource_5_2['R'].astype('str')
    df_Resource_5_2[resourcetype] = 'MFC'
    
    # 칼럼 정리
    df_Resource_5_2 = df_Resource_5_2[[versionVersionName, resource, resourcetype]]
    df_Resource_5_2.drop_duplicates(inplace=True)
    #print_df(df_Resource_5_2, 'df_Resource_5_2',False)
    
    df_Resource_5 = pd.concat([df_Resource_5_1, df_Resource_5_2])
    df_Resource_5.drop_duplicates(inplace=True)
    del df_Resource_5_1; del df_Resource_5_2
    
    print_df(df_Resource_5, 'df_Resource_5',False)
    
    ###############################################
    # STEP1-7 Resource_6 Create : SOPFIX BOD
    # df_in_CapaWeek & df_in_CapaItemSiteMap Merge
    df_Resource_6_1 = df_in_CapaWeek.merge(df_in_CapaItemSiteMap, on=[versionVersionName, groupGroupID], how='inner')
    del df_in_CapaWeek
    
    #  DENSE_RANK() OVER ( PARTITION BY '' ORDER BY B.location, b.sublocation, B.ITEM ) R 
    df_Resource_6_1['R'] = df_Resource_6_1[[locationLocation, subLocationSubLocation, 
                                            itemItem]].apply(tuple, axis=1).rank(method='dense', ascending=True).astype('int64')
    df_Resource_6_1.sort_values('R', inplace=True)
    df_Resource_6_1[resource] = 'SRT_' + df_Resource_6_1['R'].astype('str')
    df_Resource_6_1[resourcetype] = 'SRT'
    
    # 칼럼 정리
    df_Resource_6_1 = df_Resource_6_1[[versionVersionName, resource, resourcetype]]
    df_Resource_6_1.drop_duplicates(inplace=True)    
    #print_df(df_Resource_6_1, 'df_Resource_6_1',False)
    
    # df_in_CapaPeriod & df_in_CapaItemSiteMap Merge
    df_Resource_6_2 = df_in_CapaPeriod.merge(df_in_CapaItemSiteMap, on=[versionVersionName, groupGroupID], how='inner')
    # DENSE_RANK() OVER ( PARTITION BY '' ORDER BY B.location, b.sublocation, B.ITEM ) R 
    df_Resource_6_2['R'] = df_Resource_6_2[[locationLocation, subLocationSubLocation, 
                                            itemItem]].apply(tuple, axis=1).rank(method='dense', ascending=True).astype('int64')
    df_Resource_6_2.sort_values('R', inplace=True)
    df_Resource_6_2[resource] = 'SRT_' + df_Resource_6_2['R'].astype('str')
    df_Resource_6_2[resourcetype] = 'SRT'
    
    # 칼럼 정리
    df_Resource_6_2 = df_Resource_6_2[[versionVersionName, resource, resourcetype]]
    df_Resource_6_2.drop_duplicates(inplace=True)    
    #print_df(df_Resource_6_2, 'df_Resource_6_2',False)
    
    df_Resource_6 = pd.concat([df_Resource_6_1, df_Resource_6_2])
    df_Resource_6.drop_duplicates(inplace=True)
    del df_Resource_6_1; del df_Resource_6_2
    
    print_df(df_Resource_6, 'df_Resource_6',False)
    
    step('=====> STEP 1-1 : Resource Group data create End')
    ################################################################################################################
    # STEP 2 : output table create
    ################################################################################################################
    step('=====> STEP 2 : Final output table create')
    
    # out Data 생성 
    df_out_Resource = pd.concat([df_Resource_1, df_Resource_2, df_Resource_3, df_Resource_4, df_Resource_5, df_Resource_6])
    df_out_Resource.drop_duplicates(inplace=True)
    del df_Resource_1; del df_Resource_2; del df_Resource_3; del df_Resource_4; del df_Resource_5; del df_Resource_6
    
    df_out_Resource[mPBatch_ResourceBulkMemberCreation_Index] =  df_out_Resource.reset_index().index + 1
    df_out_Resource[mPBatch_SequenceMPBatch_Sequence_ID] = df_out_Resource[mPBatch_ResourceBulkMemberCreation_Index]
    df_out_Resource.rename(columns={resource:mPBatch_ResourceBulkMemberCreation_Resource,
                                    resourcetype:mPBatch_ResourceBulkMemberCreation_ResType}, inplace=True)
    
    # 버전 처리
    #df_out_Resource[versionVersionName] = paramOutVersion
    
    # out 칼럼 설정
    df_out_Resource = df_out_Resource[[versionVersionName, 
                                       mPBatch_SequenceMPBatch_Sequence_ID,
                                       mPBatch_ResourceBulkMemberCreation_Resource,
                                       mPBatch_ResourceBulkMemberCreation_ResType, 
                                       mPBatch_ResourceBulkMemberCreation_Index]]
        
    print_df(df_out_Resource, 'df_out_Resource',False)
    step('=====> STEP 2-1 : Final output table create End')
    
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_Resource, 'df_out_Resource')
        
    row_count, col_count = df_out_Resource.shape
    note(f'=====> Final df_out_Resource rows : {row_count}, column : {col_count}')
    
    step('=====> STEP 2-2 : End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_Resource = pd.DataFrame([], columns=[])

finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()