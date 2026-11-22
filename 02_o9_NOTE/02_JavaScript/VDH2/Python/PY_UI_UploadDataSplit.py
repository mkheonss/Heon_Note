"""
df_in_h : Select ([Seq1].[Seq1] ) on row, ({Measure.[Upload Header_Dimension], Measure.[Upload Header_Measure]}) on column where { [Personnel].[Email], [Version].[Version Name] };
df_in_d : Select ([Seq1].[Seq1] * [Seq].[Seq]) on row, ({Measure.[Upload Data_Data]}) on column where { [Personnel].[Email], [Version].[Version Name] };

df_out

EXEC plugin instance [PY_UI_UploadDataSplit]
for Measures {[Upload Data_Data]}
using scope (&CWVUI * [Personnel].[Email].[] * [Seq1].[Seq1].[1])
using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
str_instance = 'PY_UI_UploadDataSplit'

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
        df_in_h = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_h.csv", encoding="UTF-8")
        df_in_d = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_d.csv", encoding="UTF-8")

    vdCommon.gfn_saveDf(df_in_h, "in header", True)
    vdCommon.gfn_saveDf(df_in_d, "in data", True)

    df_out = df_in_d[["Upload Data_Data"]].copy()

    # 데이타 분해
    df_out = df_out["Upload Data_Data"].str.split("^", expand=True)

    # 컬럼명 변경
    dimension = df_in_h.at[0, "Upload Header_Dimension"]
    measure = df_in_h.at[0, "Upload Header_Measure"]
    df_out.columns = dimension.split("^") + measure.split("^")
    
    # out 출력
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




