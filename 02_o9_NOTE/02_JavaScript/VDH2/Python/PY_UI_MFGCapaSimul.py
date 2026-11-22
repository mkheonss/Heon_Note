"""
* 프로그램명
    - PY_UI_MFGCapaSimul

* 내용
    - MFG Capa Simul 생성

* 변경이력
    - 2024.07.19 / 신동언 / Create
    - 2024.11.20 / 양희영 / Update
    - 2025.02.19 / 신동언 / Update

* Inpu
- df_in_Table = pd.read_csv(' .csv')

* Flow Summary
    STEP1. MFG Capa Simul Line
    STEP1. MFG Capa Simul Line
    STEP2. MFG Capa Simul LineSub


* Execution
* Script Parameter
    - paramDataSet : MP
* Input Tables
    - df_in_VersionName : Select (&CWVUI) on row include memberproperties {[Version].[Version Name], [Prev Sync Version Name]};
    - df_in_WorkCalAnnual : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location Category].[SET].relatedmembers([Location]) ) on row, ({Measure.[Work Cal Annual_Lock Flag], Measure.[Work Cal Annual_Week Work Days]}) on column;
    - df_in_WorkCalLine : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location Category].[SET].relatedmembers([Location]) * [Work Type].[Work Type] * [Line].[Line] * [Data Set].[Data Set].[MP] ) on row, ({Measure.[Work Cal Line_Lock Flag], Measure.[Work Cal Line_Time]}) on column;
    - df_in_ProdModel : Select ([Version].[Version Name] * [Location].[Location] * [Line].[Line] * [Product].[Product Group] * [Definition].[Definition] * [Item].[Marketing Name]  * [Sequence].[Sequence].[1] ) on row,
                                  ({Measure.[Prod Model_Line Priority], Measure.[Prod Model_From Inch], Measure.[Prod Model_To Inch]}) on column where {(Measure.[Prod Model_Line Priority] == "1")} ;
    - df_in_MtrlProductionPlan : Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location Category].[SET].relatedmembers([Location]) * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,
                                 ({Measure.[W Material Production Quantity Plan Output]}) on column;
    - df_in_CapaConsumptionPlan : Select ([Version].[Version Name] * [Location].[Location Category].[SET].relatedmembers([Location]) * [Time].[Week] * [Resource].[Resource] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,
                                        ({Measure.[W Capacity Consumption Quantity Plan Output]}) on column;
    - df_in_MtrlProduction : Select ([Version].[Version Name] * [Location].[Location Category].[SET].relatedmembers([Location]) * [Activity1].[Activity1] * [Activity2].[Activity2] * [Resource].[Resource] * [Activity3].[Activity3] ) on row,
                                        ({Measure.[W Input Resource Priority], Measure.[W Resource Category], Measure.[W Resource Consumed Quantity Per], Measure.[W Resource Consumption Association]}) on column;
    - df_in_LineGrpMap : Select ([Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Line].[Line] ) on row, ({Measure.[Line Grp Map_Enddate], Measure.[Line Grp Map_Flag], Measure.[Line Grp Map_Startdate]}) on column where {Measure.[Line Grp Map_Flag]=="Y"};
    - df_in_WorkHrsoffAnnual : Select ([Version].[Version Name] * [Location].[Location Category].[SET].relatedmembers([Location]) ) on row,
                             ({Measure.[Work Hrs Annual_Off Time Mins], Measure.[Work Hrs Annual_Total Work Mins Per Day w/ Off Time], Measure.[Work Hrs Annual_Work Hrs Per Day], Measure.[Work Hrs Annual_Work Mins Per Day]}) on column;
    - df_in_Resource   : SELECT ([Resource].[Resource] *[Resource].[Resource Line]);

* Output Tables
    - df_out_MFGCapaSimulLine : Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Line].[Line] * [Data Set].[Data Set] ) on row,
                               ({Measure.[MFG Capa Simul Line_Week Work Days], Measure.[MFG Capa Simul Line_Week Work Hours], Measure.[MFG Capa Simul Line_Curr SOP Qty], Measure.[MFG Capa Simul Line_Curr SOP Time], Measure.[MFG Capa Simul Line_Prev SOP Qty], Measure.[MFG Capa Simul Line_Prev SOP Time],
                                 Measure.[MFG Capa Simul Line_Avail Line Cnt], Measure.[MFG Capa Simul Line_Oper Line Cnt], Measure.[MFG Capa Simul Line_Week Capa Qty], Measure.[MFG Capa Simul Line_Week Capa Time], Measure.[MFG Capa Simul Line_Day Capa Qty], Measure.[MFG Capa Simul Line_Hour Capa Qty]}) on column;
    - df_out_MFGCapaSimulLineSub : Select ([Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Line].[Line] * [Data Set].[Data Set] ) on row,
                                           ({Measure.[MFG Capa Simul Line Sub_Inch]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_MFGCapaSimul] for Measures {[MFG Capa Simul Line_Week Work Hours]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView", "prevVersion"}))
    using arguments {(ExecutionMode, "MediumWeight"), (paramDataSet , "MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
"""
import math
import os
import pandas as pd
import numpy as np
import datetime
import traceback
import gc
import warnings
import tracemalloc
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_MFGCapaSimul'
is_local = common.gfn_get_isLocal()
COMMON_SOURCE_VERSION = common.G_SourceVersion

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
logger.Start()


########################################################################################################################
# local function
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )

#def save_csv_file(df, file_name):
#    df.to_csv(f"{file_name}.csv", index=False)

def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)

def fn_note(note:str):
    if "Y".__eq__(pDetailLogFlag):
        logger.Note(p_note="====================> " + note, p_log_level=common.G_log_level.debug())

def step(no, string):
    logger.Step(p_step_no=no, p_step_desc=f'{string}')

########################################################################################################################
# logic start
########################################################################################################################

try:
    ################################################################################################################
    # logic start
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    # Batch 시작
    if common.gfn_get_isLocal():
        vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), os.path.dirname(__file__))
    else:
        vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), "")

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    ################################################################################################################
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP1 Start')
    vdCommon.gfn_stepLog('=====> STEP1 DataFrame Column : 변수 처리')

    # Value 변수 선언
    paramOutVersion_VALUE = "CWV_MP"
    paramDataSet_VALUE    = "MP"
    #vCWV =  "CurrentWorkingView"

    # 컬럼 변수 선언
    versionVersionName         = 'Version.[Version Name]'
    versionPrevSyncVersionName = 'Version.[Prev Sync Version Name]'
    timeWeek                   = "Time.[Week]"
    locationLocation           = "Location.[Location]"
    lineLine                   = "Line.[Line]"
    dataSetDataSet             = "Data Set.[Data Set]"
    groupGroupID               = "Group.[Group ID]"
    Resource_Resource          = "Resource.[Resource]"
    Resource_Line              = "Resource.[Resource Line]"

    workCalAnnual_LockFlag     = "Work Cal Annual_Lock Flag"
    workCalAnnual_WeekWorkDays = "Work Cal Annual_Week Work Days"
    workCalLine_Time           = "Work Cal Line_Time"
    #workCalLineGrp_Time        = "Work Cal LineGrp_Time"


    wMaterialProductionQuantityPlanOutput      = "W Material Production Quantity Plan Output"
    wMaterialProductionQuantityPlanOutputPrev  = "W Material Production Quantity Plan Output Prev"
    wCapacityConsumptionQuantityPlanOutput     = "W Capacity Consumption Quantity Plan Output"
    wCapacityConsumptionQuantityPlanOutputPrev = "W Capacity Consumption Quantity Plan Output Prev"

    WResourceConsumedQuantityPer               = "W Resource Consumed Quantity Per"
    WResourceConsumedQuantityPerPrev           = "W Resource Consumed Quantity Per Prev"

    lineGrpMap_Enddate   = "Line Grp Map_Enddate"
    lineGrpMap_Startdate = "Line Grp Map_Startdate"

    mFGCapaSimulLine_WeekWorkDays  = "MFG Capa Simul Line_Week Work Days"
    mFGCapaSimulLine_WeekWorkHours = "MFG Capa Simul Line_Week Work Hours"
    mFGCapaSimulLine_CurrSOPQty    = "MFG Capa Simul Line_Curr SOP Qty"
    mFGCapaSimulLine_CurrSOPTime   = "MFG Capa Simul Line_Curr SOP Time"
    mFGCapaSimulLine_PrevSOPQty    = "MFG Capa Simul Line_Prev SOP Qty"
    mFGCapaSimulLine_PrevSOPTime   = "MFG Capa Simul Line_Prev SOP Time"
    mFGCapaSimulLine_AvailLineCnt  = "MFG Capa Simul Line_Avail Line Cnt"
    mFGCapaSimulLine_OperLineCnt   = "MFG Capa Simul Line_Oper Line Cnt"
    mFGCapaSimulLine_WeekCapaQty   = "MFG Capa Simul Line_Week Capa Qty"
    mFGCapaSimulLine_WeekCapaTime  = "MFG Capa Simul Line_Week Capa Time"
    mFGCapaSimulLine_DayCapaQty    = "MFG Capa Simul Line_Day Capa Qty"
    mFGCapaSimulLine_HourCapaQty   = "MFG Capa Simul Line_Hour Capa Qty"

    WorkAnnualOffTime = "Work Hrs Annual_Total Work Mins Per Day w/ Off Time"

    mFGCapaSimulLineSub_Inch       =  "MFG Capa Simul Line Sub_Inch"

    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> 전처리 : 모듈 내에서 사용될 input table load')

    # 데이터 파일 읽기
    if common.gfn_get_isLocal():
        # 로컬일 경우 버전 처리
        paramOutVersion = paramOutVersion_VALUE
        paramDataSet    = paramDataSet_VALUE

        df_in_VersionName = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_VersionName.csv", encoding="UTF-8")
        df_in_WorkCalAnnual = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_WorkCalAnnual.csv", encoding="UTF-8")
        df_in_WorkCalLine = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_WorkCalLine.csv", encoding="UTF-8")
        df_in_MtrlProductionPlan = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_MtrlProductionPlan.csv", encoding="UTF-8")
        df_in_CapaConsumptionPlan = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_CapaConsumptionPlan.csv", encoding="UTF-8")
        df_in_WorkHrsoffAnnual = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_WorkHrsoffAnnual.csv", encoding="UTF-8")
        df_in_LineGrpMap = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_LineGrpMap.csv", encoding="UTF-8")
        df_in_ProdModel = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_ProdModel.csv", encoding="UTF-8")
        df_in_MtrlProduction = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_MtrlProduction.csv",encoding="UTF-8")
        df_in_Resource = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_Resource.csv",encoding="UTF-8")

    # 입력 변수 확인
    if paramDataSet is None or paramDataSet.strip() == '':
        paramOutVersion = paramOutVersion_VALUE
        paramDataSet    = paramDataSet_VALUE

    # DATA TYPE 설정
    #df_in_VersionName         = df_in_VersionName.astype({versionPrevSyncVersionName: 'int64'}, copy=True)
    df_in_VersionName         = df_in_VersionName.astype({versionVersionName: 'str', versionPrevSyncVersionName: 'str'}, copy=True)
    df_in_WorkCalAnnual       = df_in_WorkCalAnnual.astype({versionVersionName: 'str', timeWeek: 'str'}, copy=True)
    df_in_WorkCalLine         = df_in_WorkCalLine.astype({versionVersionName: 'str', timeWeek: 'str', workCalLine_Time:'float64'}, copy=True)
    df_in_MtrlProductionPlan = df_in_MtrlProductionPlan.astype({versionVersionName: 'str', timeWeek: 'str'}, copy=True)
    df_in_CapaConsumptionPlan = df_in_CapaConsumptionPlan.astype({versionVersionName: 'str', timeWeek: 'str'},copy=True)
    df_in_LineGrpMap          = df_in_LineGrpMap.astype({versionVersionName: 'str', lineGrpMap_Enddate: 'str', lineGrpMap_Startdate: 'str'}, copy=True)

    vdCommon.gfn_saveDf(df_in_VersionName, "df_in_VersionName", False)
    vdCommon.gfn_saveDf(df_in_WorkCalAnnual, "df_in_WorkCalAnnual", False)
    vdCommon.gfn_saveDf(df_in_WorkCalLine, "df_in_WorkCalLine", False)
    vdCommon.gfn_saveDf(df_in_MtrlProductionPlan, "df_in_MtrlProductionPlan", False)
    vdCommon.gfn_saveDf(df_in_CapaConsumptionPlan, "df_in_CapaConsumptionPlan", False)
    vdCommon.gfn_saveDf(df_in_MtrlProduction, "df_in_MtrlProduction", False)
    vdCommon.gfn_saveDf(df_in_LineGrpMap, "df_in_LineGrpMap", False)
    vdCommon.gfn_saveDf(df_in_ProdModel, "df_in_ProdModel", False)
    vdCommon.gfn_saveDf(df_in_WorkHrsoffAnnual, "df_in_WorkHrsoffAnnual", False)
    vdCommon.gfn_saveDf(df_in_Resource, "df_in_Resource", False)

    # Version 범위 설정
    df_in_VersionName = df_in_VersionName[df_in_VersionName[versionVersionName] == paramOutVersion].copy()
    df_in_WorkCalAnnual = df_in_WorkCalAnnual[df_in_WorkCalAnnual[versionVersionName] == paramOutVersion].copy()
    df_in_WorkCalLine = df_in_WorkCalLine[df_in_WorkCalLine[versionVersionName] == paramOutVersion].copy()
    #df_in_LineEffW = df_in_LineEffW[df_in_LineEffW[versionVersionName] == paramOutVersion].copy()
    df_in_LineGrpMap = df_in_LineGrpMap[df_in_LineGrpMap[versionVersionName] == paramOutVersion].copy()

    ################################################################################################################
    # STEP 1 :  데이터 선 가공
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP3 : input data machining')

    vPrevVrName = df_in_VersionName.loc[df_in_VersionName[versionVersionName] == paramOutVersion, versionPrevSyncVersionName].item()
    #print(type(vPrevVrName))
    if vPrevVrName.find('.0') > 0 :
        vPrevVrName = vPrevVrName.replace('.0','')
        fn_note("vPrevVrName : " + vPrevVrName)

    delete_dfs(df_in_VersionName)

    if not vPrevVrName :
        raise Exception("=====> raise Exception: vPrevVrName is Null")

    col_list = [versionVersionName,timeWeek,locationLocation,lineLine,dataSetDataSet]
    df_in_WorkCalLine = df_in_WorkCalLine[col_list]

    df_WorkCalLine = df_in_WorkCalLine.copy()

    df_WorkCalLine = df_WorkCalLine.merge(df_in_WorkHrsoffAnnual, on=[versionVersionName, locationLocation],how='left')

    col_list = [versionVersionName, timeWeek, locationLocation, lineLine, dataSetDataSet, 'Work Hrs Annual_Total Work Mins Per Day w/ Off Time']
    df_WorkCalLine = df_WorkCalLine[col_list].drop_duplicates()

    vdCommon.gfn_saveDf(df_WorkCalLine, "df_WorkCalLine", False)
    delete_dfs(df_in_WorkCalLine)

    df_in_MtrlProduction = df_in_MtrlProduction.merge(df_in_Resource, on=[Resource_Resource], how='left')
    df_in_MtrlProduction.rename(columns={Resource_Line: lineLine}, inplace=True)
    vdCommon.gfn_saveDf(df_in_MtrlProduction, "df_in_MtrlProduction", False)

    # MtrlProductionPlan current_version
    df_MtrlProductionPlan_CWV = df_in_MtrlProductionPlan.loc[(df_in_MtrlProductionPlan[versionVersionName] == paramOutVersion)].copy()
    df_MtrlProductionPlan_CWV = df_MtrlProductionPlan_CWV.groupby([versionVersionName, timeWeek, locationLocation], as_index=False)[wMaterialProductionQuantityPlanOutput].sum()
    vdCommon.gfn_saveDf(df_MtrlProductionPlan_CWV, "df_MtrlProductionPlan_CWV", False)

    # MtrlProduction current_version
    df_MtrlProduction_CWV = df_in_MtrlProduction.loc[(df_in_MtrlProduction[versionVersionName] == paramOutVersion)].copy()
    df_MtrlProduction_CWV = df_MtrlProduction_CWV.groupby([versionVersionName, locationLocation, lineLine], as_index=False)[WResourceConsumedQuantityPer].sum()
    vdCommon.gfn_saveDf(df_MtrlProduction_CWV, "df_MtrlProduction_CWV", False)

    # MtrlProductionPlan Prev_version
    df_MtrlProductionPlan_PREV = df_in_MtrlProductionPlan.loc[(df_in_MtrlProductionPlan[versionVersionName] == vPrevVrName)].copy()
    df_MtrlProductionPlan_PREV = df_MtrlProductionPlan_PREV.groupby([versionVersionName, timeWeek, locationLocation], as_index=False)[wMaterialProductionQuantityPlanOutput].sum()
    df_MtrlProductionPlan_PREV.rename(columns={wMaterialProductionQuantityPlanOutput: wMaterialProductionQuantityPlanOutputPrev}, inplace=True)
    df_MtrlProductionPlan_PREV.drop(columns=[versionVersionName], inplace=True)
    vdCommon.gfn_saveDf(df_MtrlProductionPlan_PREV, "df_MtrlProductionPlan_PREV", False)
    delete_dfs(df_in_MtrlProductionPlan)

    # MtrlProduction Prev_version
    df_MtrlProduction_PREV = df_in_MtrlProduction.loc[(df_in_MtrlProduction[versionVersionName] == vPrevVrName)].copy()
    df_MtrlProduction_PREV = df_MtrlProduction_PREV.groupby([versionVersionName, locationLocation, lineLine], as_index=False)[WResourceConsumedQuantityPer].sum()
    df_MtrlProduction_PREV.rename(columns={WResourceConsumedQuantityPer: WResourceConsumedQuantityPerPrev}, inplace=True)
    df_MtrlProduction_PREV.drop(columns=[versionVersionName], inplace=True)
    vdCommon.gfn_saveDf(df_MtrlProduction_PREV, "df_MtrlProduction_PREV", False)
    delete_dfs(df_in_MtrlProduction)

    # df_in_CapaConsumptionPlan
    # df_CapaConsumptionPlan_CWV,df_in_Resource Merge(Resource_Resource)
    df_CapaConsumptionPlan_CWV = df_in_CapaConsumptionPlan.loc[(df_in_CapaConsumptionPlan[versionVersionName] == paramOutVersion)].copy()
    df_CapaConsumptionPlan_CWV = df_CapaConsumptionPlan_CWV.merge(df_in_Resource, on=[Resource_Resource], how='left')
    df_CapaConsumptionPlan_CWV = df_CapaConsumptionPlan_CWV.groupby([versionVersionName, timeWeek, locationLocation,Resource_Line], as_index=False)[wCapacityConsumptionQuantityPlanOutput].sum()
    df_CapaConsumptionPlan_CWV.rename(columns={Resource_Line: lineLine}, inplace=True)
    vdCommon.gfn_saveDf(df_CapaConsumptionPlan_CWV, "df_CapaConsumptionPlan_CWV", False)

    # df_CapaConsumptionPlan_PREV,df_in_Resource Merge(Resource_Resource)
    df_CapaConsumptionPlan_PREV = df_in_CapaConsumptionPlan.loc[(df_in_CapaConsumptionPlan[versionVersionName] == vPrevVrName)].copy()
    df_CapaConsumptionPlan_PREV = df_CapaConsumptionPlan_PREV.merge(df_in_Resource, on=[Resource_Resource], how='left')
    df_CapaConsumptionPlan_PREV = df_CapaConsumptionPlan_PREV.groupby([versionVersionName, timeWeek, locationLocation,Resource_Line], as_index=False)[wCapacityConsumptionQuantityPlanOutput].sum()
    df_CapaConsumptionPlan_PREV.rename(columns={wCapacityConsumptionQuantityPlanOutput: wCapacityConsumptionQuantityPlanOutputPrev}, inplace=True)
    df_CapaConsumptionPlan_PREV.rename(columns={Resource_Line: lineLine}, inplace=True)
    df_CapaConsumptionPlan_PREV.drop(columns=[versionVersionName], inplace=True)
    vdCommon.gfn_saveDf(df_CapaConsumptionPlan_PREV, "df_CapaConsumptionPlan_PREV", False)
    delete_dfs(df_in_CapaConsumptionPlan)

    ################################################################################################################
    # STEP 2 : MFG Capa Simul Line 데이터 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP2 Start')

    #df_MFGCapaSimulLine = df_WorkCalLine.groupby([versionVersionName, timeWeek, locationLocation, lineLine, dataSetDataSet], as_index=False)[workCalLine_Time].sum()
    df_MFGCapaSimulLine = df_WorkCalLine.copy()
    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_in_WorkCalAnnual, on=[versionVersionName, timeWeek, locationLocation], how='left')
    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_MtrlProductionPlan_CWV, on=[versionVersionName, timeWeek, locationLocation], how='left')
    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_MtrlProductionPlan_PREV, on=[timeWeek, locationLocation], how='left')
    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_CapaConsumptionPlan_CWV, on=[versionVersionName, timeWeek, locationLocation, lineLine], how='left')
    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_CapaConsumptionPlan_PREV, on=[timeWeek, locationLocation, lineLine], how='left')
    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_MtrlProduction_CWV,on=[versionVersionName, locationLocation, lineLine], how='left')
    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_MtrlProduction_PREV, on=[locationLocation, lineLine],how='left')
    #df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_in_LineEffW,on=[versionVersionName, timeWeek, locationLocation, lineLine],how='left')

    df_MFGCapaSimulLine = df_MFGCapaSimulLine.merge(df_in_LineGrpMap,on=[versionVersionName, locationLocation, lineLine], how='inner')

    vdCommon.gfn_saveDf(df_MFGCapaSimulLine, "df_MFGCapaSimulLine00", False)

    col_list = [versionVersionName,timeWeek,locationLocation,lineLine,dataSetDataSet, workCalAnnual_WeekWorkDays, wMaterialProductionQuantityPlanOutput,wMaterialProductionQuantityPlanOutputPrev,wCapacityConsumptionQuantityPlanOutput,wCapacityConsumptionQuantityPlanOutputPrev,groupGroupID,
                WResourceConsumedQuantityPer, WResourceConsumedQuantityPerPrev,WorkAnnualOffTime]

    df_MFGCapaSimulLine = df_MFGCapaSimulLine[col_list]

    vdCommon.gfn_saveDf(df_MFGCapaSimulLine, "df_MFGCapaSimulLine01", False)

    # To Measure 칼럼 생성
    # MFG Capa Simul Line_Week Work Days : 주별 근무일
    df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkDays] = df_MFGCapaSimulLine[workCalAnnual_WeekWorkDays].fillna(0).astype('float64')
    # MFG Capa Simul Line_Week Work Hours : 주별 근무 시간
    df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours] = df_MFGCapaSimulLine['Work Hrs Annual_Total Work Mins Per Day w/ Off Time']/ 60
    df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours] = df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours].fillna(0).astype('float64')
    # MFG Capa Simul Line_Curr SOP Qty : 생산 수량
    df_MFGCapaSimulLine[mFGCapaSimulLine_CurrSOPQty] = np.ceil(df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutput]/ df_MFGCapaSimulLine[WResourceConsumedQuantityPer])
    df_MFGCapaSimulLine[mFGCapaSimulLine_CurrSOPQty] = df_MFGCapaSimulLine[mFGCapaSimulLine_CurrSOPQty].fillna(0).astype('float64')

    #MFG Capa Simul Line_Prev SOP Qty : [이전계획] 생산수량
    df_MFGCapaSimulLine[mFGCapaSimulLine_PrevSOPQty] = np.ceil(df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutputPrev] / df_MFGCapaSimulLine[WResourceConsumedQuantityPerPrev])
    df_MFGCapaSimulLine[mFGCapaSimulLine_PrevSOPQty] = df_MFGCapaSimulLine[mFGCapaSimulLine_PrevSOPQty].fillna(0).astype('float64')

    # MFG Capa Simul Line_Curr SOP Time : 생산할때 소요된 시간
    df_MFGCapaSimulLine[mFGCapaSimulLine_CurrSOPTime]   = df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutput].fillna(0).astype('float64')
    # MFG Capa Simul LineGrp_Prev SOP Time : [이전계획] 생산수량 생산할때 소요된 시간
    df_MFGCapaSimulLine[mFGCapaSimulLine_PrevSOPTime]   = df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutputPrev].fillna(0).astype('float64')
    # MFG Capa Simul_Avail Line Cnt : 라인 수(1 Setting)
    df_MFGCapaSimulLine[mFGCapaSimulLine_AvailLineCnt]  = 1

    #df_MFGCapaSimulLine[mFGCapaSimulLine_WeekCapaQty] = ((df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours] * 60 * 60) /
    #                                                     (df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutput] / df_MFGCapaSimulLine[wMaterialProductionQuantityPlanOutput])).fillna(0).astype('int64')
    #df_MFGCapaSimulLine[mFGCapaSimulLine_WeekCapaQty] = ((df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkDays] * df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours] * 60 * 60) /
    #                                                       (df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutput] /
    #                                                        df_MFGCapaSimulLine[wMaterialProductionQuantityPlanOutput])).fillna(0).astype('float64')
    #MFG Capa Simul Line_Week Capa Qty : Week Capa 수량
    df_MFGCapaSimulLine[mFGCapaSimulLine_WeekCapaQty] = ((df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours] * 60 * 60) /
                                                           (df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutput] /
                                                            df_MFGCapaSimulLine[wMaterialProductionQuantityPlanOutput])).fillna(0).astype('float64')

    # Week Capa Minute
    df_MFGCapaSimulLine[mFGCapaSimulLine_WeekCapaTime] = (df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours] * 60 * 60).astype('float64')

    vdCommon.gfn_saveDf(df_MFGCapaSimulLine, "df_MFGCapaSimulLine02", False)

    #20250327 김보은프로 요청으로 적용
    #df_MFGCapaSimulLine[mFGCapaSimulLine_DayCapaQty]   = (df_MFGCapaSimulLine[mFGCapaSimulLine_WeekCapaQty] / df_MFGCapaSimulLine[workCalAnnual_WeekWorkDays]).fillna(0)

    #df_MFGCapaSimulLine[mFGCapaSimulLine_DayCapaQty]  = ((60 * 60) * df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours]/ (df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutput] /
    #                                                      df_MFGCapaSimulLine[wMaterialProductionQuantityPlanOutput])).fillna(0).astype('int64')
    # Day Capa 수량
    df_MFGCapaSimulLine[mFGCapaSimulLine_DayCapaQty] =  df_MFGCapaSimulLine[mFGCapaSimulLine_WeekCapaQty] / df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkDays]


    #df_MFGCapaSimulLine[mFGCapaSimulLine_HourCapaQty] = ((60 * 60) / (df_MFGCapaSimulLine[wCapacityConsumptionQuantityPlanOutput] / df_MFGCapaSimulLine[wMaterialProductionQuantityPlanOutput])).fillna(0).astype('int64')
    # Hour Capa 수량
    df_MFGCapaSimulLine[mFGCapaSimulLine_HourCapaQty] = df_MFGCapaSimulLine[mFGCapaSimulLine_DayCapaQty] / df_MFGCapaSimulLine[mFGCapaSimulLine_WeekWorkHours]

    #From Measure 칼럼 삭제
    df_MFGCapaSimulLine.drop(columns=[workCalAnnual_WeekWorkDays,WorkAnnualOffTime,WResourceConsumedQuantityPer,WResourceConsumedQuantityPerPrev,
                                      wMaterialProductionQuantityPlanOutput, wCapacityConsumptionQuantityPlanOutput,
                                      wMaterialProductionQuantityPlanOutputPrev, wCapacityConsumptionQuantityPlanOutputPrev], inplace=True)

    vdCommon.gfn_saveDf(df_MFGCapaSimulLine, "df_MFGCapaSimulLine03", False)

    vdCommon.gfn_stepLog('=====> STEP2 End')
    ################################################################################################################
    # STEP 3 : MFG Capa Simul Line Sub 데이터 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP3 Start')

    df_in_ProdModel['Temp_Inch_Concat'] = df_in_ProdModel['Prod Model_From Inch'].astype(int).astype(str) +'~'+df_in_ProdModel['Prod Model_To Inch'].astype(int).astype(str)

    df_in_ProdModel = df_in_ProdModel[['Version.[Version Name]', 'Location.[Location]', 'Line.[Line]', 'Temp_Inch_Concat']]

    df_MFGCapaSimulLineSub = df_MFGCapaSimulLine.copy()
    df_MFGCapaSimulLineSub = df_MFGCapaSimulLineSub[[versionVersionName, locationLocation, lineLine, dataSetDataSet, 'Group.[Group ID]']]

    df_MFGCapaSimulLineSub = pd.merge(df_MFGCapaSimulLineSub,df_in_ProdModel, how='left', on=['Version.[Version Name]', 'Location.[Location]', 'Line.[Line]'], indicator=True)

    df_MFGCapaSimulLineSub = df_MFGCapaSimulLineSub[[versionVersionName, locationLocation, lineLine, dataSetDataSet, 'Group.[Group ID]', 'Temp_Inch_Concat']]

    df_MFGCapaSimulLineSub.rename(columns={'Temp_Inch_Concat': 'MFG Capa Simul Line Sub_Inch'}, inplace=True)

    vdCommon.gfn_stepLog('=====> STEP3 End')
    ################################################################################################################
    # STEP 4 : : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP4 Start')

    # out Data 생성 : : df_BOD & df_BOM 통합
    df_out_MFGCapaSimulLine = df_MFGCapaSimulLine.copy()
    df_out_MFGCapaSimulLineSub = df_MFGCapaSimulLineSub.copy()

    vdCommon.gfn_saveDf(df_out_MFGCapaSimulLine, "df_out_MFGCapaSimulLine", True)
    vdCommon.gfn_saveDf(df_out_MFGCapaSimulLineSub, "df_out_MFGCapaSimulLineSub", True)

    vdCommon.gfn_stepLog('plugin Execution End')

    del df_WorkCalLine
    del df_MtrlProductionPlan_CWV,   df_MtrlProduction_CWV
    del df_MtrlProductionPlan_PREV,  df_MtrlProduction_PREV
    del df_CapaConsumptionPlan_CWV,  df_CapaConsumptionPlan_PREV
    del df_MFGCapaSimulLine

except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_MFGCapaSimulLine    = pd.DataFrame([], columns=[])
    df_MFGCapaSimulLineSub = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
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
