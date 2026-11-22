"""

* 프로그램명
    - PY_UI_ProductionConstValid

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
    - 2024.11.22 / syif1380.lee / 로직 변경
    - 2025.03.12 / syif1380.lee / vdCommon 공통 로그 작업
    - 2025.03.13 / syif1380.lee / df_in_constGroup : [Sequence].[Sequence] 을 &Sequence 로 변경 (속도영향)

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table

  - df_in_constGroup :
    Select ([Version].[Version Name] * &Sequence * [Group].[Group ID] ) on row,({Measure.[Const Grp_Startdate],Measure.[Const Grp_Enddate],Measure.[Const Grp_Need Check],Measure.[Const Grp_Refer Time]}) on column;

* Output Table :
   - df_out_constGroup :


* 테스트 스크립트

EXEC plugin instance [PY_UI_ProductionConstValid] for measures {[Const Grp_From Site]} using scope ( &CWVUI ) using arguments {
      (ExecutionMode, "MediumWeight")
    , (pDetailLogFlag, "N")
    // , (paramOutVersion , "CurrentWorkingView")
    , (MaxSliceTableCells, 200000000)
    , (MaxConcurrency, 1 )
    , ([Param.o9_sys_log_level], "DEBUG")
};

"""

########################################################################################################################
# NSCMCommon - start
########################################################################################################################
import datetime
import traceback
import pandas as pd
import os.path
import numpy as np
import gc
import time
import traceback
import warnings
import tracemalloc
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
########################################################################################################################
# NSCMCommon - end
########################################################################################################################


########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ProductionConstValid'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 공통 함수 정의
########################################################################################################################
def fn_get_str(val):
    try:
        if (type(val) is str):
            return val
        elif (type(val) is float):
            if (pd.isna(val)):
                return ""
            else:
                return str(val)
        elif (type(val) is bool):
            if val:
                return "True"
            else:
                return "False"
        elif pd.isna(val):
            return ""
        else:
            return str(val)
    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    return ""

def fn_nvl(val1:str, val2:str):
    if "".__eq__(val1) or pd.isna(val1) :
        return val2
    else:
        return val1

def fn_getCisValue(cisAttrValues: str, cisId: str):
    cisAttbs = cisAttrValues.split("^")

    for i in range(len(cisAttbs)):
        cisAttb = cisAttbs[i].split("::")
        if (cisId.__eq__(cisAttb[0])):
            return cisAttb[1]

    return ""

def fn_note(note:str):
    if "Y".__eq__(pDetailLogFlag):
        logger.Note(p_note="====================> " + note, p_log_level=common.G_log_level.debug())

def fn_concat(value1:str, value2:str):
    if value1 == np.nan or "".__eq__(value1):
        return value2
    else:
        return value1 + "," + value2

########################################################################################################################
# logic start
########################################################################################################################
try:

    # Batch 시작
    if common.gfn_get_isLocal():
        vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), os.path.dirname(__file__))
    else:
        vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), "")

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    ################################################################################################################
    # # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    # tracemalloc.start()
    # start_time = time.time()
    # formatted_date_time = datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
    # vdCommon.gfn_stepLog(f'===================== plugin Execution Start ({formatted_date_time}) =====================')
    ################################################################################################################

    # 로컬일 경우 버전 처리
    # 데이터 파일 읽기
    if common.gfn_get_isLocal():
        df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_constGroup.csv", encoding="UTF-8")
        pDetailLogFlag = "N"

    # if df_in_constGroup.empty:
    #     raise Exception("Exception: df_in_constGroup is empty")

    # 입력 변수 확인용 로그
    vdCommon.gfn_saveDf(df_in_constGroup, "df_in_constGroup", True)

    ################################################################################################################
    # input Table log
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP1 Start')

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    VersionName = 'Version.[Version Name]'
    GroupID = 'Group.[Group ID]'
    Sequence = 'Sequence.[Sequence]'
    ConstGrp_Startdate = 'Const Grp_Startdate'
    ConstGrp_Enddate = 'Const Grp_Enddate'
    ConstGrp_ReferTime = 'Const Grp_Refer Time'
    ConstGrp_NeedCheck = 'Const Grp_Need Check'

    df_constGroup = df_in_constGroup.copy()

    # astype(int) 는 NaN과 문자열을 처리하지 못하므로 오류 발생
    # pd.to_numeric(errors="coerce") 를 사용해 문자열을 숫자로 변환하거나, 처리할 수 없는 값을 NaN으로 바꿔줌
    # 1.숫자가 아닌 값을 NaN으로 변환
    df_constGroup[ConstGrp_Startdate] = pd.to_numeric(df_constGroup[ConstGrp_Startdate], errors="coerce").astype("Int64")
    df_constGroup[ConstGrp_Enddate] = pd.to_numeric(df_constGroup[ConstGrp_Enddate], errors="coerce").astype("Int64")

    # 2. 결측값이 있는 경우 (NaN을) 처리하며 정수형으로 변환
    df_constGroup[ConstGrp_Startdate] = df_constGroup[ConstGrp_Startdate].astype("Int64")
    df_constGroup[ConstGrp_Enddate] = df_constGroup[ConstGrp_Enddate].astype("Int64")

    # check 로직 수행
    def check_overlap_numpy(group):
        valid_rows = group[ConstGrp_Startdate].notna() & group[ConstGrp_Enddate].notna()
        sWeek = group.loc[valid_rows, ConstGrp_Startdate].to_numpy()
        eWeek = group.loc[valid_rows, ConstGrp_Enddate].to_numpy()

        # 겹치는 여부를 확인할 행렬 생성
        start_matrix = sWeek[:, None]
        end_matrix = eWeek[:, None]

        overlap_matrix = ~((end_matrix < sWeek) | (start_matrix > eWeek))  # 겹치지 않는 조건의 부정
        np.fill_diagonal(overlap_matrix, False)  # 자기 자신은 제외

        check_values = overlap_matrix.any(axis=1)
        group.loc[valid_rows, "check"] = check_values
        group["check"] = group["check"].fillna(False)   # null 일 경우 False
        return group

    # GroupID 별 그룹화 후 처리
    df_constGroup = df_constGroup.groupby(GroupID, group_keys=False).apply(check_overlap_numpy)

    # Measure.[Const Grp_Need Check] 에 data 생성 (GroupID_Sequence + " Check"
    df_constGroup[ConstGrp_NeedCheck] = np.where(df_constGroup["check"], df_constGroup[GroupID] + "[" +df_constGroup[Sequence].astype(str) + "] Check", np.nan)

    df_out_constGroup = df_constGroup.copy()
    df_out_constGroup = df_out_constGroup[[VersionName, GroupID, Sequence, ConstGrp_NeedCheck]]

    ################################################################################################################
    # 최종 Output 테이블 만들기
    ################################################################################################################
    vdCommon.gfn_saveDf(df_out_constGroup, "df_out_constGroup", True)

    ####################################################################################################################
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    ####################################################################################################################
    # current, peak = tracemalloc.get_traced_memory()
    # end_time = time.time()
    # run_time_seconds = end_time - start_time
    # run_time_minutes = run_time_seconds / 60
    # formatted_date_time = datetime.datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S")
    # vdCommon.gfn_stepLog(
    #     f'=====> current: {current / 1024 / 1024:.2f} MB, peak: {peak / 1024 / 1024:.2f} MB, execution time: {run_time_minutes:.4f} minutes')
    # vdCommon.gfn_stepLog(f'===================== plugin Execution End ({formatted_date_time}) =====================')
    # tracemalloc.stop()
    ####################################################################################################################
    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    # ouput Table 선언
    df_out_constGroup = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    vdCommon.gfn_stepLog('=====> Batch end')
