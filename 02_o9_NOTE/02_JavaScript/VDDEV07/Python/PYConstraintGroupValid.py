"""

* 프로그램명
    - PYConstraintGroupValid

* 내용
    - Production Constraint : Validation 액션버튼 수행
    - Data 전체 Validation 체크 : Group ID 별 Start Date, End Date 중복구간이 있는지 체크하여 Measure.[Const Grp_Need Check] 에 'Group ID' + 'seq' + 'Check'

* Input
- df_in_ConstGroup : Constraint Group

* Flow Summary
    Step1.
    Step2.
    Step3.
    Step4.


* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2024.06.05 / syif1380.lee / Create

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table

  - df_in_constGroup :
    Select ([Version].[Version Name] * [Sequence].[Sequence] * [Group].[Group ID] ) on row,
            ({Measure.[Const Grp_Build Ahead],
              Measure.[Const Grp_Definition],
              Measure.[Const Grp_Desc],
              Measure.[Const Grp_Enddate],
              Measure.[Const Grp_From Site],
              Measure.[Const Grp_Inch],
              Measure.[Const Grp_Item],
              Measure.[Const Grp_Mkt Name],
              Measure.[Const Grp_Need Check],
              Measure.[Const Grp_Prod Qty],
              Measure.[Const Grp_Product Group],
              Measure.[Const Grp_Project],
              Measure.[Const Grp_Reason],
              Measure.[Const Grp_Refer Time],
              Measure.[Const Grp_Startdate],
              Measure.[Const Grp_To Site],
              Measure.[Const Grp_Update Time],
              Measure.[Const Grp_Updated By],
              Measure.[Const Grp_Year]}) on column;

* Output Table :
   - df_out_constGroup :


* 테스트 스크립트

EXEC plugin instance [PYConstraintGroupValid] for measures {[Const Grp_From Site]} using scope ( Version.[Version Name].[CurrentWorkingView]) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


"""
import pandas as pd
import numpy as np
import logging
import datetime
import platform
import os
import tabulate
import traceback
import time

from sqlalchemy import true, false

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
programName = "PYConstraintGroupValid"
logger = getLogger(programName)

log(logger.info, 'plugin Execution Start')

# 데이터 파일 읽기
if isLocal():
    # df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_constGroup.csv", encoding="UTF-8") # scope로 필터링된 데이타 Group ID 1개,seq n개
    df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + "df_in_constGroupAll.csv", encoding="UTF-8") # All Data ( 테스트용 )

tm_StartMain = time.time()
try:

    if df_in_constGroup.empty:
        raise Exception("df_in_constGroup No Data")

    log(logger.info, df_in_constGroup, _dfName="df_in_constGroup")

    df_in_constGroup_copy = df_in_constGroup.copy()

    # Group ID 별로 그룹화
    df_grouped = df_in_constGroup_copy.groupby('Group.[Group ID]')

    # 결과물 저장할 리스트
    results = []

    # 각 그룹에 대해 처리
    for name, group in df_grouped:
        group = group.sort_values(by='Group.[Group ID]').reset_index(drop=True)
        group['prev_s'] = group['Const Grp_Startdate'].shift(+1)
        group['prev_e'] = group['Const Grp_Enddate'].shift(+1)

        # 현재 행의 's'와 'e'사이에 다음 행의 's'와 'e'값이 겹쳐지는지 확인
        group['is_prev_s_in_range'] = (group['Const Grp_Startdate'] != '') & (group['prev_s'] >= group['Const Grp_Startdate']) & (group['prev_s'] <= group['Const Grp_Enddate'])
        group['is_prev_e_in_range'] = (group['Const Grp_Enddate'] != '') & (group['prev_e'] >= group['Const Grp_Startdate']) & (group['prev_e'] <= group['Const Grp_Enddate'])

        # 최종적으로 하나라도 겹치는지 확인
        group['is_any_overlap'] = group['is_prev_s_in_range'] | group['is_prev_e_in_range']
        results.append(group)

    # 모든 그룹의 결과를 다시 합침
    df_out_constGroup = pd.concat(results).reset_index(drop=True)

    # Validation 체크
    # 점검 필요 항목에 : Group ID + Seq + "Check" 입력
    # Const Grp_Need Check = Group.[Group ID] + " " + Sequence.[Sequence] + " " + "Check"
    df_out_constGroup['Const Grp_Need Check'] = np.where(df_out_constGroup['is_any_overlap'] == 1,
                                                 df_out_constGroup['Group.[Group ID]'] +" " + df_out_constGroup['Sequence.[Sequence]'].astype(str) + " Check",
                                                 "")

    # 컬럼 삭제
    df_out_constGroup = df_out_constGroup.drop(labels=['prev_s', 'prev_e', 'is_prev_s_in_range', 'is_prev_e_in_range', 'is_any_overlap'], axis=1)

    log(logger.info, df_out_constGroup, _dfName="df_out_constGroup")
    saveDf(df_out_constGroup, 'df_out_constGroup')

    # 데이터 파일 저장
    if isLocal():
        log(logger.info, '3. csv save')
        df_out_constGroup.to_csv(os.path.dirname(__file__) + "\\" + f"{programName}_out.csv", index=False)
except Exception as e:
    log(logger.error, traceback.format_exc())
    #raise Exception(e)
finally:
    tm_EndMain = time.time()
    log(logger.info, f'END : Total time is {tm_EndMain - tm_StartMain:5f} sec.')
    log(logger.info, 'plugin Execution End')
