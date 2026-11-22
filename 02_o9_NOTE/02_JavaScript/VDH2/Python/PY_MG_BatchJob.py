"""
df_in_bj : Select ([Batch Job].[Job] ) on row, ({Measure.[Batch Job_Order], Measure.[Batch Job_Parent Job]}) on column where { [Version].[Version Name] };

df_out :

EXEC plugin instance [PY_MG_BatchJob]
for measures {[Batch Job_Level 1]}
using scope ( &CWVUI )
using arguments {(outVersionName, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

26.01.30 HashMap 을 사용해서 찾도록 수정
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
str_instance = 'PY_MG_BatchJob'
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

def fn_findLevel(row):
    job = row["Batch Job.[Job]"]

    # 마지막 여부
    leaf = "N"
    val = pjHm.get(job)
    if val == None:
        leaf = "Y"

    last = ""
    level = []
    order = []
    for i in range(0, 7):
        val = jpHm.get(job)
        if val != None :
            last = val

            if val != "Root":
                level.insert(0, val)
            else:
                level.append("-")

            oVal = oHm.get(job)
            if oVal != None:
                order.insert(0, oVal)
        else:
            level.append("-")
            order.append(0)

        job = val

    allOrder = str(order[0]).rjust(2, "0") + str(order[1]) + str(order[2]) + str(order[3]) + str(order[4]) + str(order[5]) + str(order[6])

    if leaf == "Y" and ( last != "Root" or level[0] == "-" ):
        leaf = "N"

    return [level[0], level[1], level[2], level[3], level[4], level[5], level[6]
                ,order[0], order[1], order[2], order[3], order[4], order[5], order[6]
                ,allOrder, leaf, last]

try:
    if is_local:
        df_in_bj = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_bj.csv", encoding="UTF-8")
        outVersionName = "CWV_MP"

    # Batch 시작
    vdCommon.gfn_pyLog_start(outVersionName, str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # Float로 나와서 Int 로 변경
    df_in_bj['Batch Job_Order'] = df_in_bj['Batch Job_Order'].astype(int)

    vdCommon.gfn_saveDf(df_in_bj, "df_in_bj", True)

    # Parent > Job hm 구성, Job > Parent hm 구성
    pjHm = {}
    jpHm = {}
    oHm = {}
    for rowIdx in df_in_bj.index:
        pjHm[df_in_bj.loc[rowIdx, "Batch Job_Parent Job"]] = df_in_bj.loc[rowIdx, "Batch Job.[Job]"]
        jpHm[df_in_bj.loc[rowIdx, "Batch Job.[Job]"]] = df_in_bj.loc[rowIdx, "Batch Job_Parent Job"]
        oHm[df_in_bj.loc[rowIdx, "Batch Job.[Job]"]] = df_in_bj.loc[rowIdx, "Batch Job_Order"]

    # print(pjHm)
    # print(jpHm)
    # print(oHm)

    df_out = df_in_bj[["Batch Job.[Job]"]]

    # Level 데이타를 생성한다.
    df_out[["Batch Job_Level 1", "Batch Job_Level 2", "Batch Job_Level 3", "Batch Job_Level 4"
                ,"Batch Job_Level 5", "Batch Job_Level 6", "Batch Job_Level 7"
                ,"Batch Job_Level 1 Order", "Batch Job_Level 2 Order", "Batch Job_Level 3 Order"
                ,"Batch Job_Level 4 Order" ,"Batch Job_Level 5 Order", "Batch Job_Level 6 Order"
                ,"Batch Job_Level 7 Order"
                ,"Batch Job_All Order", "Batch Job_Leaf", "Batch Job_Last"]] = df_out.apply(lambda row: fn_findLevel(row), axis=1,result_type='expand')

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

