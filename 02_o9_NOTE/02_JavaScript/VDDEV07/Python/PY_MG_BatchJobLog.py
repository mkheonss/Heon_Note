"""
df_in_bj : select ( [Batch Job].[Job] ) on row, ({Measure.[Batch Job_Parent Job]}) on column;
df_in_pyLog : Select ( [Sequence].[Sequence] * [Python Batch].[Python Name] ) on row, ({Measure.[Python Batch Log_Elasped Time], Measure.[Python Batch Log_End Time], Measure.[Python Batch Log_Error Message], Measure.[Python Batch Log_Start Time]}) on column where { [Version].[Version Name], [Time].[Day] };


df_out :

EXEC plugin instance [PY_MG_BatchJobLog]
for measures {[Batch Job Log_Start Time]}
using scope ( &CWVUI )
using arguments {(outVersionName, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

"""

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
str_instance = 'PY_MG_BatchJobLog'
is_local = common.gfn_get_isLocal()

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
class NoData(Exception):
    pass

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if is_local:
        df_in_bj = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_bj.csv", encoding="UTF-8")
        df_in_pyLog = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_pyLog.csv", encoding="UTF-8")
        outVersionName = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_bj, "df_in_bj", True)
    vdCommon.gfn_saveDf(df_in_pyLog, "df_in_pyLog", True)

    # 파이썬 로그중에 가장 최근 데이타만 가져온다.
    df_in_pyLog['rank'] = df_in_pyLog.groupby(["Python Batch.[Python Name]"])["Sequence.[Sequence]"].rank(method='first')
    df_in_pyLog = df_in_pyLog.loc[(df_in_pyLog["rank"] == 1)]

    # 이름 변경
    df_in_pyLog.rename(columns={"Python Batch.[Python Name]" : "Batch Job.[Job]"
                                ,"Python Batch Log_Start Time" : "Batch Job Log_Start Time"
                                ,"Python Batch Log_End Time" : "Batch Job Log_End Time"
                                ,"Python Batch Log_Elasped Time": "Batch Job Log_Elasped Time"
                                ,"Python Batch Log_Error Message" : "Batch Job Log_Error Message"}, inplace=True)
    vdCommon.gfn_saveDf(df_in_pyLog, "df_in_pyLog rank", True)

    # 마스터화 Merge 한다.
    df_out = df_in_bj.merge(df_in_pyLog, how='left', left_on=["Batch Job.[Job]"], right_on=["Batch Job.[Job]"])

    # 필요없는 컬럼 삭제
    df_out.drop(columns=["Sequence.[Sequence]", "rank"], inplace=True)

    df_out["Batch Job Log_Error Message"] = df_out["Batch Job Log_Error Message"].str.replace(r'\r\n', ' ', regex=True)

    # Null 일경우 데이타가 생성이 안되서 fillna 처리해서 공백을 하나 넣는다.
    df_out["Batch Job Log_Start Time"].fillna(value="-", inplace=True)
    df_out["Batch Job Log_End Time"].fillna(value=" ", inplace=True)
    df_out["Batch Job Log_Elasped Time"].fillna(value=" ", inplace=True)
    df_out["Batch Job Log_Error Message"].fillna(value=" ", inplace=True)

    # ,Python Batch Log_Elasped Time,,,
    df_out.insert(0, "Version.[Version Name]", outVersionName)

    vdCommon.gfn_saveDf(df_out, "df_out", True)

    vdCommon.gfn_stepLog('plugin Execution End')
except NoData as e:
    vdCommon.gfn_stepLog('No Data')

    df_out = pd.DataFrame([], columns=[])
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

