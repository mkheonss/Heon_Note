"""
df_in_l : Select ([Personnel].[Email] * [Version].[Version Name] * [Sequence ID].[Sequence ID] * [Time].[Day] * [Sequence].[Sequence] ) on row, ({Measure.[Javascript Run Log_Full]}) on column where { coalesce(Measure.[Javascript Run Log_Full], "") != "" };
df_in_el : Select ([Personnel].[Email] * [Version].[Version Name] * [Sequence ID].[Sequence ID] * [Time].[Day] * [Sequence].[Sequence] ) on row, ({Measure.[Javascript Error Log_Full]}) on column where { coalesce(Measure.[Javascript Error Log_Full], "") != "" };

df_out

EXEC plugin instance [PY_JavascriptLog]
for Measures {[Javascript Run Log_Full]}
using scope ([Version].[Version Name].[CurrentWorkingView])
using arguments {(pVersionName, "CurrentWorkingView"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
str_instance = 'PY_JavascriptLog'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 공통 함수 정의
########################################################################################################################

########################################################################################################################
# 함수 정의
########################################################################################################################


try:
    if common.gfn_get_isLocal():
        df_in_l = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_l.csv", encoding="UTF-8")
        df_in_el = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_el.csv", encoding="UTF-8")

        pVersionName = "CurrentWorkingView"

    # Batch 시작
    vdCommon.gfn_pyLog_start(pVersionName, str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    vdCommon.gfn_saveDf(df_in_l, "df_in_l", True)
    vdCommon.gfn_saveDf(df_in_el, "df_in_el", True)

    dimension = "Version.[Version Name]^Personnel.[Email]^Time.[Day]^Sequence.[Sequence]^Sequence ID.[Sequence ID]"
    measure = ("Javascript Run Log_EwMenuName^" +
               "Javascript Run Log_EwReportName^" +
               "Javascript Run Log_Program^" +
               "Javascript Run Log_Function^" +
               "Javascript Run Log_EwFuncName^" +
               "Javascript Run Log_EwParams^" +
               "Javascript Run Log_EwFilters^" +
               "Javascript Run Log_EwGridRows^" +
               "Javascript Run Log_Params^" +
               "Javascript Run Log_RunTime")
    _columns = dimension.split("^") + measure.split("^")
    if len(df_in_l) > 0:
        df_out1 = df_in_l["Javascript Run Log_Full"].str.split('^J:S:L^', expand=True, regex=False)

        df_out1.columns = _columns
        df_out1["Javascript Run Log_Full"] = ""
    else:
        df_out1 = pd.DataFrame([], columns=_columns)

    dimension = "Version.[Version Name]^Personnel.[Email]^Time.[Day]^Sequence.[Sequence]^Sequence ID.[Sequence ID]"
    measure = ("Javascript Error Log_EwMenuName^" +
               "Javascript Error Log_EwReportName^" +
               "Javascript Error Log_Program^" +
               "Javascript Error Log_Function^" +
               "Javascript Error Log_EwFuncName^" +
               "Javascript Error Log_EwParams^" +
               "Javascript Error Log_EwFilters^" +
               "Javascript Error Log_EwGridRows^" +
               "Javascript Error Log_Params^" +
               "Javascript Error Log_RunTime^" +
               "Javascript Error Log_ErrorMsg")
    _columns = dimension.split("^") + measure.split("^")
    if len(df_in_el) > 0:
        df_out2 = df_in_el["Javascript Error Log_Full"].str.split("^J:S:L^", expand=True, regex=False)

        df_out2.columns = _columns
        df_out2["Javascript Error Log_Full"] = ""
    else:
        df_out2 = pd.DataFrame([], columns=_columns)

    # out 출력
    vdCommon.gfn_saveDf(df_out1, "df_out1", True)
    vdCommon.gfn_saveDf(df_out2, "df_out2", True)

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
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




