"""
df_in_approval : Select ([Personnel].[Email] * [Version].[Version Name] * [Time].[Day] * [Time Seq].[Time Seq] ) on row, ({Measure.[Knox Approval_ApInfId], Measure.[Knox Approval_Aplns], Measure.[Knox Approval_Contents], Measure.[Knox Approval_Subject], Measure.[Knox Approval_Attachment Text]}) on column;
df_out :

EXEC plugin instance [PY_Knox_Approval]
for measures {[Knox Approval_Status]}
using scope ( &CWVUI * [Personnel].[Email].[sungmin0.lim@partner.samsung.com] * [Time].[Day].[2026-02-09] * [Time Seq].[Time Seq].[001231] )
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
import io
import xlsxwriter
import socket

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_Knox_Approval'
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

    df_in_approval = df_in_approval.astype({"Time Seq.[Time Seq]": 'str'}, copy=False)

    vdCommon.gfn_saveDf(df_in_approval, "df_in_approval", True)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    subject = df_in_approval.loc[0, "Knox Approval_Subject"]
    contents = df_in_approval.loc[0, "Knox Approval_Contents"]
    aplns = df_in_approval.loc[0, "Knox Approval_Aplns"]
    apInfId = df_in_approval.loc[0, "Knox Approval_ApInfId"]
    day = df_in_approval.loc[0, "Time.[Day]"]
    time = df_in_approval.loc[0, "Time Seq.[Time Seq]"]
    df_in_approval["Knox Approval_Attachment Text"].fillna(value="", inplace=True)
    attachmentText = df_in_approval.loc[0, "Knox Approval_Attachment Text"]

    # 환경에 따른 Config 가져오기
    knox_url = "https://openapi.stage.samsung.net/approval/api/v2.0/approvals/submit"
    header_system_id = 'KCC10REST03476'
    header_authorization = 'Bearer 6ee5aebf-af37-381c-a987-a85214b85e31'

    hostname = socket.gethostname()
    if hostname.startswith("scpgp"):
        knox_url = ''
        header_system_id = ''
        header_authorization = ''

        vdCommon.gfn_stepLog("PROD Server")
    elif hostname.startswith("scpgq"):
        vdCommon.gfn_stepLog("QA Server")
    else:
        vdCommon.gfn_stepLog("DEV Server")

    _boundary = "----WebKitFormBoundarykN8w6ehWBLB0YGVD"

    _headers = {
        'Content-Type': f"multipart/form-data; boundary={_boundary};"
        ,'Accept' : 'application/json'
        ,'System-ID' : f'{header_system_id}'
        ,'Authorization' : f'{header_authorization}'
    }

    _json = { "subject" : subject
                ,"contents" : contents
                ,"apInfId" : apInfId
                ,"aplns" : json.loads(aplns)
                ,"sbmDt" : day.replace("-", "") + time.rjust(6, "0")
                ,"contentsType" : "html"
                ,"docMngSaveCode" : "0"
                ,"docSecuType" : "PERSONAL"
                ,"notifyOption" : "0"
                ,"sbmLang" : "ko"
                ,"timeZone" : "GMT+9"
                ,"urgYn" : "N"
            }
    _jsonStr = json.dumps(_json)

    _data = f"--{_boundary}\r\n".encode("utf-8")
    _data = _data + f'Content-Disposition: form-data; name="approval"\r\n\r\n'.encode("utf-8")
    _data = _data + f'{_jsonStr}\r\n'.encode("utf-8")

    # 엑셀 내용 첨부가 있나?
    if attachmentText != "":
        # 1. 첨부 df 를 생성
        arr = attachmentText.split('^^^')
        excelHeader = arr[0].split("^:^")
        excelAlign = arr[1].split("^:^")
        excelWidth = arr[2].split("^:^")
        excelData = arr[0:1] + arr[3:]

        df_excel = pd.DataFrame(excelData, columns=["Data"])
        df_excel = df_excel["Data"].str.split('^:^', expand=True, regex=False)
        df_excel.columns = excelHeader
        vdCommon.gfn_saveDf(df_excel, "df_excel", True)

        # 2. DataFrame을 메모리상의 엑셀 파일(BytesIO)로 변환후에 서식 지정
        # confidential 적용을 위해서 헤더,헤더,데이타들로 엑셀을 만들고 처음 헤더는 머지해서 confidential 을 적용한다.
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_excel.to_excel(writer, index=False, sheet_name='Sheet1')

            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]

            # 스타일 포맷
            f_title = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'font_size' : 12, 'border': 1})
            f_left = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'border': 1})
            f_center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
            f_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'border': 1})
            f_confidential = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, "font_color" : "red", 'border': 1})

            # idx 별 엑셀 컬럼 배열
            excelColumn = "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,XY,Z".split(",")

            # confidential
            worksheet.merge_range("A1:" + excelColumn[len(excelHeader) - 1] + "1", "Confidential", f_confidential)

            # 컬럼 너비 및 정렬 변경
            for idx in range(len(excelWidth)):
                if excelAlign[idx] == "left":
                    worksheet.set_column(excelColumn[idx] + ":" + excelColumn[idx], int(excelWidth[idx]), f_left)
                elif excelAlign[idx] == "center":
                    worksheet.set_column(excelColumn[idx] + ":" + excelColumn[idx], int(excelWidth[idx]), f_center)
                else:
                    worksheet.set_column(excelColumn[idx] + ":" + excelColumn[idx], int(excelWidth[idx]), f_right)

            # Header 를 다시 적용한다.
            for idx in range(len(excelHeader)):
                worksheet.write(excelColumn[idx] + "2", excelHeader[idx], f_title)

        excel_buffer.seek(0)  # 파일 포인터를 처음으로 이동

        # 2. 메모리 데이터를 로컬에 저장
        # with open('local_file.xlsx', 'wb') as f:
        #     f.write(excel_buffer.read())

        _data = _data + f"--{_boundary}\r\n".encode("utf-8")
        _data = _data + f'Content-Disposition: form-data; name="attachments"; filename="excel.xlsx"\r\n'.encode("utf-8")
        _data = _data + f'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n'.encode("utf-8")
        _data = _data + excel_buffer.read()
        _data = _data + f"\r\n".encode("utf-8")

    if "1" == "2":
        # O9 에서 가이드 한 소스
        from o9_common_utils.O9WebApiUtils import O9WebApiUtils

        api_utils = O9WebApiUtils()
        _f_headers = {
            'Accept' : 'application/json, */*;q=0.5'
            ,'accept-encoding' : 'gzip,deflate, br, zstd'
            ,'Accept-Language' : 'ko-KR;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        _f_params = "FileID=s3://1b2Hdq_Gl1Rs42tnBWwSJV7PrEy75eVLv9s41jaVS1_Fc5w_LPYtlLxYDFKx62xj-C5m40COjukAyv4gs2pXM5KJDNAQldD7MBjyL3-5JKJcOTW38x3Hp7evPE7qG0axMNeMktY-ZSd3k-_T2BlopQ2"
        vdCommon.gfn_stepLog("log 1 ")
        _f_response = api_utils.get("/api/Upload/Download", headers=_f_headers, params=_f_params)
        vdCommon.gfn_stepLog("log 2 ")
        vdCommon.gfn_stepLog("log : " + str(_f_response))
        if _f_response.status_code == 200:
            # with open('aaa3.txt', 'wb') as f:
            #     for chunk in _response.iter_content(chunk_size=8192):
            #         f.write(chunk)
            attach = io.BytesIO(_f_response.content)

            _data = _data + f"--{_boundary}\r\n".encode("utf-8")
            _data = _data + f'Content-Disposition: form-data; name="attachments"; filename="excel2.xlsx"\r\n'.encode("utf-8")
            _data = _data + f'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n'.encode("utf-8")
            _data = _data + attach.read()
            _data = _data + f"\r\n".encode("utf-8")

        # _f_headers = {
        #     'Accept': 'application/json, */*;q=0.5'
        #     , 'accept-encoding': 'gzip,deflate, br, zstd'
        #     , 'Accept-Language': 'ko-KR;q=0.9,en-US;q=0.8,en;q=0.7'
        # }
        # _f_params = "FileID=s3://1b2Hdq_Gl1Rs42tnBWwSJV7PrEy75eVLv9s41jaVS184Xool9kh0AcxQDHq6RNBs1CtiC5GPtaXB5jQ7XYC_1T1Tu8c6ZCdyuKn-VyZKyyoiTb9PlR7WaQ4PLonKKqUD0&authToken="
        # api_utils = O9WebApiUtils()
        # _f_response = api_utils.get("https://dev-nscm.sec.samsung.net/api/Upload/Download", headers=_f_headers, params=_f_params)
        # vdCommon.gfn_stepLog("Ok : " + json.dumps(_f_response.json()))

    # 파일 첨부가 있으면
    if "1" == "2":
        # 첨부파일 테스트 - authToken 정보가 필요함
        _f_headers = {
            'Accept' : 'application/json, */*;q=0.5'
            ,'accept-encoding' : 'gzip,deflate, br, zstd'
            ,'Accept-Language' : 'ko-KR;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        _f_params = "FileID=s3://1b2Hdq_Gl1Rs42tnBWwSJV7PrEy75eVLv9s41jaVS1_M8ZcsuFAJRa3OLqEOKnh-qNZxoIDAdhlTR0yROG2TzssayxhOd0-7IUVQ3CNhvjCOFTQzn79Ia0Kn_4ipabmhyZUEdbpcQKWGfWUG6H4uLA2"
        _f_response = requests.get("https://dev-nscm.sec.samsung.net/api/Upload/Download", headers=_f_headers, params=_f_params, stream=True, proxies={"http": None, "https": None})
        vdCommon.gfn_stepLog("Ok : " + str(_f_response.status_code))
        if _f_response.status_code == 200:
            attach = io.BytesIO(_f_response.content)

            _data = _data + f"--{_boundary}\r\n".encode("utf-8")
            _data = _data + f'Content-Disposition: form-data; name="attachments"; filename="excel2.xlsx"\r\n'.encode("utf-8")
            _data = _data + f'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n'.encode("utf-8")
            _data = _data + attach.read()
            _data = _data + f"\r\n".encode("utf-8")

    _data = _data + f"--{_boundary}--\r\n".encode("utf-8")

    # _data = ((
    #     f"--{_boundary}\r\n"
    #     f'Content-Disposition: form-data; name="approval"\r\n\r\n'
    #     f'{_jsonStr}\r\n'
    #     f"--{_boundary}\r\n"
    #     f'Content-Disposition: form-data; name="attachments"; filename="excel.xlsx"\r\n'
    #     f'Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n').encode("utf-8") +
    #          filedata +
    #          f"\r\n--{_boundary}--\r\n".encode("utf-8"))
    # print(_body)

    df_out = df_in_approval[["Version.[Version Name]", "Personnel.[Email]", "Time.[Day]", "Time Seq.[Time Seq]"]]

    _response = requests.post(knox_url, headers=_headers, data=_data, proxies={"http":None, "https":None})
    if _response.status_code == 200:
        vdCommon.gfn_stepLog("Ok : " + json.dumps(_response.json()))

        rtnJson = _response.json()

        df_out["Knox Approval_Error Code"] = "-"
        df_out["Knox Approval_Error Message"] = "-"
    elif _response.status_code == 400 or _response.status_code == 403:
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

