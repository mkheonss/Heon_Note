"""
df_in_mail : Select ([Personnel].[Email] * [Version].[Version Name] * [Time].[Day] * [Time Seq].[Time Seq] ) on row, ({Measure.[Knox Mail_Contents], Measure.[Knox Mail_Recipients], Measure.[Knox Mail_RecipientsEmail], Measure.[Knox Mail_Subject], Measure.[Knox Mail_UserId], Measure.[Knox Mail_Sender], Measure.[Knox Mail_Attachment Text]}) on column;

df_out :

EXEC plugin instance [PY_Knox_Mail]
for measures {[Knox Mail_Status]}
using scope ( &CWVUI * [Personnel].[Email].[sungmin0.lim] * [Time].[Day].[2026-02-09] * [Time Seq].[Time Seq].[001231] )
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
import socket
import xlsxwriter
import io

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_Knox_Mail'
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
        df_in_mail = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_mail.csv", encoding="UTF-8")

        pVersionName = "CWV_MP"

    # Batch 시작
    vdCommon.gfn_pyLog_start(pVersionName, str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion + " , " + vdCommon.G_VD_SourceVersion)

    vdCommon.gfn_saveDf(df_in_mail, "df_in_mail", True)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    userId = df_in_mail.loc[0, "Knox Mail_UserId"]
    subject = df_in_mail.loc[0, "Knox Mail_Subject"]
    contents = df_in_mail.loc[0, "Knox Mail_Contents"]
    recipientsEmail = df_in_mail.loc[0, "Knox Mail_RecipientsEmail"]
    sender = df_in_mail.loc[0, "Knox Mail_Sender"]
    df_in_mail["Knox Mail_Attachment Text"].fillna(value="", inplace=True)
    attachmentText = df_in_mail.loc[0, "Knox Mail_Attachment Text"]

    # 환경에 따른 Config 가져오기
    knox_url = "https://openapi.stage.samsung.net/mail/api/v2.0/mails/send?userId=" + userId
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

    vdCommon.gfn_stepLog('knox_url : ' + knox_url)

    _headers = {
        'Content-Type': f"multipart/form-data; boundary={_boundary};"
        , 'Accept': 'application/json'
        , 'System-ID': f'{header_system_id}'
        , 'Authorization': f'{header_authorization}'
    }

    _json = {"subject" : subject
                ,"contents" : contents
                ,"contentType" : "html"
                ,"docSecuType" : "PERSONAL"
                ,"sender" : { "emailAddress" : sender }
                ,"recipients" : []}
    recipients = recipientsEmail.split(",")
    for idx in range(0, len(recipients)):
        arr = recipients[idx].split("^")
        _json["recipients"].append( { "emailAddress": arr[0], "recipientType": arr[1] } )
    _jsonStr = json.dumps(_json)
    # print(_json)

    _data = f"--{_boundary}\r\n".encode("utf-8")
    _data = _data + f'Content-Disposition: form-data; name="mail"\r\n\r\n'.encode("utf-8")
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

    _data = _data + f"--{_boundary}--\r\n".encode("utf-8")

    df_out = df_in_mail[["Version.[Version Name]", "Personnel.[Email]", "Time.[Day]", "Time Seq.[Time Seq]"]]

    # 보안으로 데이타 초기화
    # df_out["Knox Mail_RecipientsEmail"] = ""

    _response = requests.post(knox_url, headers=_headers, data=_data, proxies={"http":None, "https":None})
    if _response.status_code == 200:
        vdCommon.gfn_stepLog("Ok : " + json.dumps(_response.json()))

        rtnJson = _response.json()

        df_out["Knox Mail_Status"] = rtnJson["result"]
        df_out["Knox Mail_MailId"] = rtnJson["mailId"]
    elif _response.status_code == 400 or _response.status_code == 403:
        vdCommon.gfn_stepLog(str(_response.status_code) + " Error : " + json.dumps(_response.json()))

        rtnJson = _response.json()

        df_out["Knox Mail_Error Code"] = rtnJson["errorCode"]
        df_out["Knox Mail_Error Message"] = rtnJson["errorMessage"]
    else:
        vdCommon.gfn_stepLog(str(_response.status_code) + ' Error')

        df_out["Knox Mail_Error Code"] = str(_response.status_code)
        df_out["Knox Mail_Error Message"] = "Server Error"

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

