
import pandas as pd
import numpy as np
import logging
import datetime
import platform
import os
import tabulate
import traceback
import time


################################# 나중에 라이브러리로 빼야함 ##############################################
# 로거 세팅
logging.basicConfig(level=logging.DEBUG)
comm_logger = logging.getLogger("o9_logger")
startTime = datetime.datetime.now()

# Log 포맷 함수
def getLogger(_pluginName, _log_level=logging.DEBUG, _log_fileName="log"):
    global pluginName
    pluginName = _pluginName

    # 로컬이면 파일로 저장
    if platform.system() == 'Windows':
        comm_logger.setLevel(_log_level)
        # 일반 핸들러, 포매터 세팅
        formatter = logging.Formatter("%(asctime)s %(levelname)s : %(message)s")
        handler = logging.FileHandler(os.path.dirname(__file__) + "\\" + _log_fileName + ".log", encoding="UTF8")
        handler.setLevel(_log_level)
        handler.setFormatter(formatter)
        # 각 핸들러를 로거에 추가
        comm_logger.addHandler(handler)

    return comm_logger

def logPrefix():
    elapsed = datetime.datetime.now() - startTime
    return f"{pluginName} : {elapsed} sec : "

def log(_func, _msg, _dfName=""):
    if isinstance(_msg, pd.DataFrame):
        if platform.system() == 'Windows':
            head_row = 3
            if "__Fix" in _dfName:   # df name 에 '__Fix' 이름이 포함될 경우 head row 20로 정함
                head_row = 20
                # print('%%%%%%%%%%%%%%%   head_row' + str(head_row) + ' :: _dfName : ' + _dfName)

            _func(logPrefix() + "*" * 30 + f" {_dfName} : {len(_msg.columns)} Column, {str(len(_msg.index))} Rows " + "*" * 30 +
                f"\n" + tabulate.tabulate(_msg.head(head_row), headers="keys", tablefmt="fancy_grid"))
            _func(_msg.dtypes)
        else:
            _func(logPrefix() + "*"*30 + f" {_dfName} : {len(_msg.columns)} Column, {str(len(_msg.index))} Rows " + "*"*30)
            _func(logPrefix() + "Columns ==> " + "\t".join(_msg.columns))

            maxCnt = 3 if len(_msg.index) > 3 else len(_msg.index)
            for i in range(0,maxCnt):
                # _func(logPrefix() + str(i) + " ==> " + _msg.to_string(header=False, index=False, index_names=False).split('\n')[i])
                _func(logPrefix() + str(i) + " ==> " + ', '.join(_msg.iloc[i].astype(str)))
            # 컬럼 및 Type 출력
            colInfo = "Column Info ==> "
            for i in _msg.dtypes.keys():
                colInfo = colInfo + f"{i} ({_msg.dtypes[i]})\t*\t"
            _func(logPrefix() + colInfo)
    else:
        _func(logPrefix() + _msg)

def isLocal():
    if platform.system() == 'Windows':
        return True
    else:
        return False

def saveDf(_df, _csvName):
    if isLocal():
        _df.to_csv(os.path.dirname(__file__) + "\\" + f"{programName}_out_{_csvName}.csv", index=False)

def convert_date_string(date_string):
    # 24-Mar-24 포맷형식을 yyyy-mm-dd 형식으로 리턴
    return datetime.strptime(date_string, '%d-%b-%y').strftime('%Y-%m-%d')
    # return datetime.strptime(pd.to_datetime(date_string, format='%d-%b-%y'), '%d-%b-%y').strftime('%Y-%m-%d')
######################################### 서버 반영시 주석 처리 ########################################
# Version Name 세팅
# param_outVersion = "CWV_MP"
######################################################################################################
programName = "PYConstraintGroupApply"
logger = getLogger(programName)

log(logger.info, 'plugin Execution Start')

log(logger.info, df_in_constGroupDetailW_lockInfo )





# 변수 선언
versionName = 'Version.[Version Name]'

#inputbackup=df_in_constGroup.copy()

# 데이터 파일 읽기

tm_StartMain = time.time()
try:
    df_out_constGroupDetail   = df_in_constGroup

except Exception as e:
    log(logger.error, traceback.format_exc())
    #raise Exception(e)
finally:
    tm_EndMain = time.time()
    log(logger.info, f'END : Total time is {tm_EndMain - tm_StartMain:5f} sec.')
    log(logger.info, 'plugin Execution End')
