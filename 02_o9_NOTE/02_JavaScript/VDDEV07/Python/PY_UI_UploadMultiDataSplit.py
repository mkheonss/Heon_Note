"""
df_in_h : Select ([Seq1].[Seq1] ) on row, ({Measure.[Upload Header_Dimension], Measure.[Upload Header_Measure]}) on column where { [Personnel].[Email], [Version].[Version Name] };
df_in_d : Select ([Seq1].[Seq1] * [Seq].[Seq]) on row, ({Measure.[Upload Data_Data1], Measure.[Upload Data_Data2], Measure.[Upload Data_Data3], Measure.[Upload Data_Data4], Measure.[Upload Data_Data5], Measure.[Upload Data_Data6], Measure.[Upload Data_Data7], Measure.[Upload Data_Data8], Measure.[Upload Data_Data9], Measure.[Upload Data_Data10], Measure.[Upload Data_Data11], Measure.[Upload Data_Data12], Measure.[Upload Data_Data13], Measure.[Upload Data_Data14], Measure.[Upload Data_Data15], Measure.[Upload Data_Data16], Measure.[Upload Data_Data17], Measure.[Upload Data_Data18], Measure.[Upload Data_Data19], Measure.[Upload Data_Data20]}) on column where { [Personnel].[Email], [Version].[Version Name] };

df_out

EXEC plugin instance [PY_UI_UploadMultiDataSplit]
for Measures {[Upload Data_Data1]}
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
str_instance = 'PY_UI_UploadMultiDataSplit'

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

    # 10개 컬럼을 한개로 합친다.
    df_out = df_in_d[["Upload Data_Data1"]].copy()
    df_out.rename(columns={"Upload Data_Data1": "Upload Data_Data"}, inplace=True)
    for idx in range(2, 21):
        df_w_out = df_in_d[["Upload Data_Data" + str(idx)]].copy()
        df_w_out.rename(columns={"Upload Data_Data" + str(idx) : "Upload Data_Data"}, inplace=True)
        df_out = pd.concat([df_out, df_w_out]).reset_index(drop=True)

    # 빈 문자열이 있는 데이타 삭제
    df_out["Upload Data_Data"] = df_out["Upload Data_Data"].replace('', np.nan)
    df_out = df_out.dropna(subset=["Upload Data_Data"])
    vdCommon.gfn_saveDf(df_out, "all data", True)

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




