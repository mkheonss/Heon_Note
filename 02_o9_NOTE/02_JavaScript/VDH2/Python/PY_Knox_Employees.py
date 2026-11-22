"""
df_in_employee : Select ( [Version].[Version Name] * [Personnel].[Email] * [Seq].[Seq] ) on row, ({Measure.[Knox Employee_CompanyName], Measure.[Knox Employee_DepartmentName], Measure.[Knox Employee_Email], Measure.[Knox Employee_UserId], Measure.[Knox Employee_UserName]}) on column ;

EXEC plugin instance [PY_Knox_Employees]
for measures {[Knox Employee_UserId]}
using scope ( &CWVUI * [Personnel].[Email].[sungmin0.lim@partner.samsung.com] )
using arguments {(pVersionName, "CWV_MP"), (pEmail, "sungmin0.lim@partner.samsung.com"), (pField, "name"), (pValue, "임성민")
                    ,(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
"""

import pandas as pd
import os
import traceback
import warnings
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import requests
import json
import socket

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_Knox_Employees'
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
        df_in_employee = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_employee.csv", encoding="UTF-8")

        pVersionName = "CWV_MP"
        pEmail = "sungmin0.lim@partner.samsung.com"
        pField = "userIds"
        pValue = "s00.park,sungmin0.lim"
        # pField = "name"
        # pValue = "임성민"

    # Batch 시작
    vdCommon.gfn_pyLog_start(pVersionName, str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start : " + common.G_SourceVersion + " , " + vdCommon.G_VD_SourceVersion)

    vdCommon.gfn_saveDf(df_in_employee, "df_in_employee", True)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # 임시로 추가 : 호스트 이름, IP 가져오기
    vdCommon.gfn_stepLog('Hostname : ' + socket.gethostname() + ' , Internal IP : ' + socket.gethostbyname(socket.gethostname()))

    knox_url = "https://openapi.stage.samsung.net/employee/api/v2.0/employees?" + pField + "=" + pValue
    header_system_id = 'KCC10REST03476'
    header_authorization = 'Bearer 6ee5aebf-af37-381c-a987-a85214b85e31'

    vdCommon.gfn_stepLog('knox_url : ' + knox_url)

    _headers = {
        'Content-Type': 'application/json'
        , 'Accept': 'application/json'
        , 'System-ID': f'{header_system_id}'
        , 'Authorization': f'{header_authorization}'
    }
    _body = {
        "resultType" :"optional"
        ,"attributes":["emailAddress", "sirName", "givenName", "departmentName", "companyName", "userId"]
    }

    df_out = pd.DataFrame([], columns=[])

    _response = requests.post(knox_url, headers=_headers, data=json.dumps(_body), proxies={"http":None, "https":None})
    if _response.status_code == 200:
        vdCommon.gfn_stepLog("Ok : " + json.dumps(_response.json()))

        rtnJson = _response.json()

        df_out = pd.DataFrame(rtnJson["employees"])

        df_out["Knox Employee_UserName"] = df_out["sirName"] + df_out["givenName"]
        df_out.rename(columns={"userId": "Knox Employee_UserId"
                                ,"companyName": "Knox Employee_CompanyName"
                                ,"departmentName": "Knox Employee_DepartmentName"
                                ,"emailAddress": "Knox Employee_Email"}, inplace=True)
        df_out.insert(loc=0, column='[Version].[Version Name]', value=pVersionName)
        df_out.insert(loc=1, column='[Personnel].[Email]', value=pEmail)
        df_out.insert(loc=2, column='Seq.[Seq]', value="1")
        df_out["Seq.[Seq]"] = list(range(1, len(rtnJson["employees"]) + 1))
        df_out = df_out.astype({"Seq.[Seq]": 'str'}, copy=False)
        df_out.drop(["sirName", "givenName"], axis=1, inplace=True)
    elif _response.status_code == 400 or _response.status_code == 500:
        vdCommon.gfn_stepLog(str(_response.status_code) + " Error : " + json.dumps(_response.json()))
    else:
        vdCommon.gfn_stepLog(str(_response.status_code) + ' Error')

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

    # (중요) LightWeight 모드로 실행시 에러나는 부분 수정
    df_out_log = df_out_log.astype({"Sequence.[Sequence]" : "str"}, errors='ignore', copy=False)
    df_out_logDetail = df_out_logDetail.astype({"Sequence.[Sequence]" : "str"}, errors='ignore', copy=False)
    df_out_logDetail['Python Batch Log Detail_Row'] = df_out_logDetail['Python Batch Log Detail_Row'].replace('', '0')

    # logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    # logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)

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

