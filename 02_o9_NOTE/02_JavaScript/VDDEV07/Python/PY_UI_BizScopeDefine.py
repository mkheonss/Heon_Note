"""

PriorityDef : Select ([Version].[Version Name] * [GraphCubeDim_Sequence].[GraphCubeAttr_Sequence] * [SDX_ObjectiveSequence].[SDX Biz Case Span] * [Plan Type].[Plan Type] * [Group].[Group ID] ) on row, ({Measure.[SDX Biz Case Definition]}) on column where {Measure.[SDX Biz Case Span Association] == 1};
BizCase : Select ([Version].[Version Name] * [Plan Type].[Plan Type] * [DM Rule].[Rule] ) on row,  ({Measure.[Biz Obj Scope Define_Area], Measure.[Biz Obj Scope Define_Scope DisplayName], Measure.[Biz Obj Scope Define_Biz Req], Measure.[Biz Obj Scope Define_Scope], Measure.[ABDM SDX Time Rule]}) on column where {Measure.[Biz Obj Scope Define_Include] == true};
PlanningHorizon : select (&PlanningHorizon);
MPHorizonShort : select (&MPHorizonShort);
MPHorizon4Weeks : select (&MPHorizon4Weeks);

graph_input

EXEC plugin instance [PY_UI_BizScopeDefine]
for measures {[Biz Obj Base_Period]}
using scope ( &CWVUI )
using arguments {(Version, "CWV_MP"), (GroupID, "Regular Plan"), (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

"""



import numpy as np
import pandas as pd
import os
import traceback
import warnings
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BizScopeDefine'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 함수 정의
########################################################################################################################


########################################################################################################################
# Main Logic
########################################################################################################################
try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if is_local:
        PriorityDef = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_df_PriorityDef.csv", encoding="UTF-8")
        BizCase = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_df_BizCase.csv", encoding="UTF-8")
        PlanningHorizon = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_df_PlanningHorizon.csv", encoding="UTF-8")
        MPHorizonShort = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_df_MPHorizonShort.csv", encoding="UTF-8")
        MPHorizon4Weeks = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_df_MPHorizon4Weeks.csv", encoding="UTF-8")

        Version = "CWV_MP"
        GroupID = "Regular Plan"

    # input 출력
    vdCommon.gfn_saveDf(PriorityDef, "PriorityDef", True)
    vdCommon.gfn_saveDf(BizCase, "BizCase", True)
    vdCommon.gfn_saveDf(PlanningHorizon, "PlanningHorizon", True)
    vdCommon.gfn_saveDf(MPHorizonShort, "MPHorizonShort", True)
    vdCommon.gfn_saveDf(MPHorizon4Weeks, "MPHorizon4Weeks", True)

    temp3 = pd.DataFrame(columns=['Version.[Version Name]', 'Sequence.[Sequence]', 'Biz Obj.[Scope]', 'Group.[Group ID]', 'Biz Obj Base_Period'])

    # Check if any Input dfs are empty
    if PriorityDef.empty or BizCase.empty or PlanningHorizon.empty or MPHorizonShort.empty or MPHorizon4Weeks.empty:
        temp3 = pd.DataFrame(columns=['Version.[Version Name]', 'Sequence.[Sequence]', 'Biz Obj.[Scope]', 'Group.[Group ID]', 'Biz Obj Base_Period'])
    else:
        BizCase = BizCase.iloc[:, 2:].dropna(subset=['Biz Obj Scope Define_Area'])
        BizCase['ABDM SDX Time Rule'] = BizCase['ABDM SDX Time Rule'].fillna('PlanningHorizon')  # Null값 대체

        BizCase.loc[BizCase['ABDM SDX Time Rule'] == 'PlanningHorizon', 'Biz Obj Base_Period'] = len(PlanningHorizon)
        BizCase.loc[BizCase['ABDM SDX Time Rule'] == 'MPHorizonShort', 'Biz Obj Base_Period'] = len(MPHorizonShort)
        BizCase.loc[BizCase['ABDM SDX Time Rule'] == 'MPHorizon4Weeks', 'Biz Obj Base_Period'] = len(MPHorizon4Weeks)

        temp = PriorityDef.copy()
        temp = temp.dropna(axis=0)

        temp['SDX_ObjectiveSequence.[SDX Biz Case Span]'] = temp['SDX_ObjectiveSequence.[SDX Biz Case Span]'].astype(str)

        temp.loc[temp['SDX_ObjectiveSequence.[SDX Biz Case Span]'] == '1', 'SDX_ObjectiveSequence.[SDX Biz Case Span]'] = 'Short Term'
        temp.loc[temp['SDX_ObjectiveSequence.[SDX Biz Case Span]'] == '2', 'SDX_ObjectiveSequence.[SDX Biz Case Span]'] = 'Mid Term'
        temp.loc[temp['SDX_ObjectiveSequence.[SDX Biz Case Span]'] == '3', 'SDX_ObjectiveSequence.[SDX Biz Case Span]'] = 'Long Term'

        temp = temp.pivot(
            index='SDX Biz Case Definition',
            columns='SDX_ObjectiveSequence.[SDX Biz Case Span]',
            values='GraphCubeDim_Sequence.[GraphCubeAttr_Sequence]'
        ).sort_values(by='Short Term').reset_index().rename_axis(None, axis=1)

        temp2 = pd.merge(temp, BizCase, left_on='SDX Biz Case Definition', right_on='DM Rule.[Rule]', how='left')
        temp2 = temp2.dropna(subset=['Biz Obj Scope Define_Area']).reset_index(drop=True)
        temp2['Sequence.[Sequence]'] = temp2.index + 1
        temp2['Version.[Version Name]'] = Version
        temp2['Group.[Group ID]'] = GroupID
        temp2['Biz Obj Base_Asn'] = 1

        temp3 = temp2[
            ['Version.[Version Name]', 'Group.[Group ID]', 'Sequence.[Sequence]', 'Biz Obj Scope Define_Scope',
             'Biz Obj Base_Period', 'Short Term', 'Mid Term', 'Long Term', 'Biz Obj Base_Asn']]
        temp3 = temp3.rename(columns={
            'Biz Obj Scope Define_Scope': 'Biz Obj.[Scope]',
            'Short Term': 'Biz Obj Base_Priority Short',
            'Mid Term': 'Biz Obj Base_Priority Mid',
            'Long Term': 'Biz Obj Base_Priority Long'
        })

        for col in ['Biz Obj Base_Period', 'Biz Obj Base_Priority Short', 'Biz Obj Base_Priority Mid',
                    'Biz Obj Base_Priority Long']:
            temp3[col] = pd.to_numeric(temp3[col]).astype('Int64')

    vdCommon.gfn_saveDf(temp3, 'temp3', True)

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out = pd.DataFrame([], columns=[])
finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

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


