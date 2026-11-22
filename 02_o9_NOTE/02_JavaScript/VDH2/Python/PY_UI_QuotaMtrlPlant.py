"""
df_in_gqm : Select ( [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({Measure.[Global Quota Mtrl W_Portion]}) on column where { [Version].[Version Name] };
df_in_gqmp : Select ( [Location].[Location] * [Group].[Group ID] ) on row, ({Measure.[Global Quota Mtrl Plant_ASN]}) on column  where  { [Version].[Version Name] };
df_in_imsa : Select (&NSUILocationMFMtrlView * [Item Material].[Item Material]) on row, ( { Measure.[Item Mtrl Site Asn_Cur Status] } ) on column where { [Version].[Version Name], Measure.[Item Mtrl Site Asn_Cur Status] in {"PLANNED", "ACTIVE"} };
df_in_org : Select ( [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Group].[Group ID] ) on row, ({Measure.[Plant Quota Mtrl W_Portion]}) on column where { [Version].[Version Name] };

df_out :

EXEC plugin instance [PY_UI_QuotaMtrlPlant]
for measures {[Plant Quota Mtrl W_Portion]}
using scope ( &CWVUI )
using arguments {(paramOutVersion, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

BN96-33736A 로 테스트

"""

import pandas as pd
import os
import traceback
import warnings
import numpy as np
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_QuotaMtrlPlant'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 공통 함수 정의
########################################################################################################################
# 스트링을 넘겨준다.
def gfn_get_str(val):
    if (type(val) is str):
        return val
    elif (type(val) is float):
        if (pd.isna(val)):
            return ""
        else:
            return str(val)

def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)
########################################################################################################################
# 함수 정의
########################################################################################################################


try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_gqm = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_gqm.csv", encoding="UTF-8")
        df_in_gqmp = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_gqmp.csv", encoding="UTF-8")
        df_in_imsa = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_imsa.csv", encoding="UTF-8")
        df_in_org = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_org.csv", encoding="UTF-8")

        paramOutVersion = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_gqm, "df_in_gqm", True)
    vdCommon.gfn_saveDf(df_in_gqmp, "df_in_gqmp", True)
    vdCommon.gfn_saveDf(df_in_imsa, "df_in_imsa", True)
    vdCommon.gfn_saveDf(df_in_org, "df_in_org", True)

    # 필요없는 컬럼 삭제
    df_in_gqmp.drop(["Global Quota Mtrl Plant_ASN"], axis=1, inplace=True)
    df_in_imsa.drop(["Item Mtrl Site Asn_Cur Status"], axis=1, inplace=True)


    df_in_gqm_work = df_in_gqm.merge(df_in_gqmp, how='inner', on=["Group.[Group ID]"])
    vdCommon.gfn_saveDf(df_in_gqm_work, "full data", True)
    df_in_gqm_work = df_in_gqm_work.merge(df_in_imsa, how='inner', on=["Item Material.[Item Material]", "Location.[Location]"])
    vdCommon.gfn_saveDf(df_in_gqm_work, "data in imsa", True)
    df_in_gqm_work = df_in_gqm_work.merge(df_in_org, how='left', on=["Item Material.[Item Material]", "Sub Location.[Sub Location]", "Group.[Group ID]", "Time.[Week]", "Location.[Location]"])
    vdCommon.gfn_saveDf(df_in_gqm_work, "all merge", True)

    df_out = df_in_gqm_work.loc[(df_in_gqm_work["Plant Quota Mtrl W_Portion"].isna())].copy()
    # version 추가
    df_out.insert(0, "Version.[Version Name]", paramOutVersion)
    df_out["Plant Quota Mtrl W_Portion"] = df_out["Global Quota Mtrl W_Portion"]
    df_out.drop(labels=["Global Quota Mtrl W_Portion"], axis=1, inplace=True)

    vdCommon.gfn_saveDf(df_out, "df_out", True)

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

