"""
df_in_approval : Select ([Personnel].[Email] * [Version].[Version Name] * [Time].[Day] * [Time Seq].[Time Seq] ) on row, ({Measure.[Knox Approval_ApInfId], Measure.[Knox Approval_Status]}) on column where { Measure.[Knox Approval_Status] in {"1"}} ;

df_out :

EXEC plugin instance [PY_Knox_ApprovalStatus]
for measures {[Knox Approval_Status]}
using scope ( &CWVUI )
using arguments {(pVersionName, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


"""

import pandas as pd
import os
import traceback
import warnings
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import requests
import json

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_Knox_ApprovalStatus'
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

try:
    if is_local:
        df_in_approval = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_approval.csv", encoding="UTF-8")

        pVersionName = "CWV_MP"

    # Batch 시작
    vdCommon.gfn_pyLog_start(pVersionName, str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion + " , " + vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    df_in_approval = df_in_approval.astype({"Time Seq.[Time Seq]": 'str'}, copy=False)

    vdCommon.gfn_saveDf(df_in_approval, "df_in_approval", True)

    knox_url = "https://openapi.stage.samsung.net/approval/api/v2.0/approvals/status"
    header_system_id = 'KCC10REST03476'
    header_authorization = 'Bearer 6ee5aebf-af37-381c-a987-a85214b85e31'

    _headers = {
        'Content-Type': 'application/json'
        , 'Accept': 'application/json'
        , 'System-ID': f'{header_system_id}'
        , 'Authorization': f'{header_authorization}'
    }

    _data = []
    for rowIdx in df_in_approval.index:
        _data.append( { "apinfid" : df_in_approval.loc[rowIdx, "Knox Approval_ApInfId"] } )

    df_out = df_in_approval[["Version.[Version Name]", "Personnel.[Email]", "Time.[Day]", "Time Seq.[Time Seq]", "Knox Approval_Status", "Knox Approval_ApInfId"]]

    _response = requests.post(knox_url, headers=_headers, data=json.dumps(_data), proxies={"http":None, "https":None})
    if _response.status_code == 200:
        rtnJson = _response.json()

        vdCommon.gfn_stepLog("Ok : " + str(len(rtnJson["data"])) + " 건, " + json.dumps(rtnJson["data"][:1]))

        # HashMap 을 만든다.
        hm = {}
        for idx in range(0, len(rtnJson["data"])):
            data = rtnJson["data"][idx]
            hm[data["apInfId"]] = data["status"]

        # 상태를 구한다.
        for rowIdx, row in df_out.iterrows():
            apInfId = row["Knox Approval_ApInfId"]
            data = hm.get(apInfId)
            if data != None:
                row["Knox Approval_Status"] = data

        df_out["Knox Approval_Error Code"] = ""
        df_out["Knox Approval_Error Message"] = ""
    elif _response.status_code == 400:
        vdCommon.gfn_stepLog(str(_response.status_code) + " Error : " + json.dumps(_response.json()))

        rtnJson = _response.json()

        df_out["Knox Approval_Error Code"] = rtnJson["errorCode"]
        df_out["Knox Approval_Error Message"] = rtnJson["errorMessage"]
    else:
        vdCommon.gfn_stepLog(str(_response.status_code) + ' Error')

        df_out["Knox Approval_Error Code"] = str(_response.status_code)
        df_out["Knox Approval_Error Message"] = "Server Error"

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

