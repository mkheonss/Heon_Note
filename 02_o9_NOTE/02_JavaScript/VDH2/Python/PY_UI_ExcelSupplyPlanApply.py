"""

df_in_excelupload : Select ([Version].[Version Name] * [Layout].[Layout] * [Personnel].[Email] * [Seg].[Seg] * [Seq].[Seq] ) on row, ({Measure.[Base], Measure.[Data type], Measure.[LT], Measure.[Material], Measure.[Notify], Measure.[Plant_Code], Measure.[Validation], Measure.[Vendor_Code], Measure.[W01], Measure.[W02], Measure.[W03], Measure.[W04], Measure.[W05], Measure.[W06], Measure.[W07], Measure.[W08], Measure.[W09], Measure.[W10], Measure.[W11], Measure.[W12], Measure.[W13], Measure.[W14], Measure.[W15], Measure.[W16], Measure.[W17], Measure.[W18], Measure.[W19], Measure.[W20], Measure.[W21], Measure.[W22], Measure.[W23], Measure.[W24]}) on column;
df_in_week : Select ([Time].[Week]) on row, () on column;

df_out_case1
df_out_case2
df_out_case1_u
df_out_case2_u


EXEC plugin instance [PY_UI_ExcelSupplyPlanApply]
for measures {[Validation]}
using scope ( &VD * [Layout].[Layout].[{{fbLayout}}] * [Personnel].[Email].[{{fbEmail}}] * [Seg].[Seg].[{{fbSeg}}] )
using arguments {(param_version, "CWV_MP"), (param_seg, "{{fbSeg}}"), (param_user, CurrentUser().[User Name]), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

26.04.07 : LT 값이 - 이면 빈문자열로 변경
26.04.09 : Version 을 파라미터로 받음
26.04.14 : Plant, Vendor 는 _Code 를 사용하도록 수정
"""

import numpy as np
import pandas as pd
import os
import traceback
import warnings
import math
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ExcelSupplyPlanApply'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 함수 정의
########################################################################################################################
def fn_isNull(val: str):
    if val == np.nan or "".__eq__(val):
        return True
    else:
        return False

def fn_isNotNull(val: str):
    if val != np.nan and "".__ne__(val):
        return True
    else:
        return False

def fn_concat(value1:str, value2:str):
    if value1 == np.nan or "".__eq__(value1):
        return value2
    else:
        return value1 + "," + value2

def fn_isDigit(type:str, val: str):
    try:
        if type == "int":
            num = float(val.replace(",",""))
        elif type == "float":
            num = float(val.replace(",", ""))
    except:
        return False

    return True

def fn_get_str(val):
    try:
        if type(val) is str:
            return val
        elif val == np.nan or math.isnan(val):
            return ""
        else:
            return str(val)
    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    return ""

def fn_info(note:str):
    # if logger.get_level() >= common.G_log_level.info():
    logger.Note(p_note=note, p_log_level=common.G_log_level.info())

def fn_debug(note:str):
    if logger.get_level() >= common.G_log_level.debug():
        logger.Note(p_note=note, p_log_level=common.G_log_level.debug())


########################################################################################################################
# Main Logic
########################################################################################################################
try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_excelupload = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_excelupload.csv", encoding="UTF-8")
        df_in_week = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_week.csv", encoding="UTF-8")
        param_seg = "솔루엠"
        param_user = "sungmin0.lim"
        param_version = "CWV_MP"

    df_in_excelupload["Version.[Version Name]"] = param_version

    df_in_excelupload.loc[(df_in_excelupload["LT"] == "-"), "LT"] = ""

    # df 춮력
    vdCommon.gfn_saveDf(df_in_excelupload, "df_in_excelupload", True)
    vdCommon.gfn_saveDf(df_in_week, "df_in_week", True)

    # week 정렬
    df_in_week = df_in_week.sort_values(by="Time.[Week]", ascending=True)

    # 기준이 되는 주의 idx 를 구한다.
    base_idx = -1
    base = df_in_excelupload.loc[0, "Base"]
    for idx in df_in_week.index:
        if base.__eq__(df_in_week.loc[idx, "Time.[Week]"]):
            base_idx = idx
            break

    # Week 이름을 가지는 Map을 구성 : Shift 에서 사용
    # { 0 : "W00", 1 : "W01", ... }
    weekMap = {}
    for idx in range(0, 24):
        weekMap[idx] = "W" + str(idx + 1).rjust(2, "0")
    # print(weekMap)

    ####################################################################################################################
    # Case 1 데이타 생성
    ####################################################################################################################
    df_out_case1 = df_in_excelupload.copy()
    # 필터 적용
    df_out_case1 = df_out_case1.loc[(df_out_case1["Data type"].isin("VSL,AIR".split(",")))].copy()
    vdCommon.gfn_saveDf(df_out_case1, "df_out_case1", True)
    # shift 처리 - LT
    for idx in df_out_case1.index:
        if "".__ne__(fn_get_str(df_out_case1.loc[idx, "LT"])):
            shiftValue = int(float(fn_get_str(df_out_case1.loc[idx, "LT"])))
            if shiftValue > 0:
                for week_idx in range(23 - shiftValue, -1, -1):
                    # 역순으로 해서 Shift 하고
                    df_out_case1.loc[idx, weekMap[week_idx + shiftValue]] = df_out_case1.loc[idx, weekMap[week_idx]]
                    # 원 데이타 초기화
                    df_out_case1.loc[idx, weekMap[week_idx]] = 0
    vdCommon.gfn_saveDf(df_out_case1, "df_out_case1", True)

    # 필요한 컬럼만 가져온다.
    arr_header = ["Version.[Version Name]"]
    arr_header.append("Material")
    arr_header.append("Vendor_Code")
    arr_header.append("Plant_Code")
    arr_header.append("Data type")
    for idx in range(0, 24):
        arr_header.append("W" + str(idx + 1).rjust(2, "0"))
    df_out_case1 = df_out_case1[arr_header].copy()

    # rename을 한다.
    rename_columns = {}
    rename_columns["Material"] = "Item Material.[Item Material]"
    rename_columns["Vendor_Code"] = "Location.[Location]"
    rename_columns["Plant_Code"] = "Sub Location.[Sub Location]"
    rename_columns["Data type"] = "Trans Mode.[Trans Mode]"
    for idx in range(0, 24):
        rename_columns["W" + str(idx + 1).rjust(2, "0")] = df_in_week.loc[base_idx + int(float(idx)), "Time.[Week]"]
    df_out_case1.rename(columns=rename_columns, inplace=True)

    # 기록 데이타 생성 : 26.4.14 필요없서 주석처리
    # df_out_case1_u = df_out_case1[["Version.[Version Name]", "Item Material.[Item Material]", "Location.[Location]",
    #              "Sub Location.[Sub Location]", "Trans Mode.[Trans Mode]"]].copy()
    # df_out_case1_u.drop_duplicates()
    # df_out_case1_u["EU U Standard C1_Seg"] = param_seg
    # df_out_case1_u["EU U Standard C1_Created By"] = param_user
    # vdCommon.gfn_saveDf(df_out_case1_u, "df_out_case1_u", True)

    # unpivot 을 한다.
    df_out_case1 = df_out_case1.melt(
        id_vars=["Version.[Version Name]", "Item Material.[Item Material]", "Location.[Location]",
                 "Sub Location.[Sub Location]", "Trans Mode.[Trans Mode]"], var_name="Time.[Week]",
        value_name="Mtrl Supply Plan_ETA Qty Excel")
    df_out_case1["Mtrl Supply Plan_Xls Seg"] = param_user
    df_out_case1["Mtrl Supply Plan_Xls Updated By"] = param_seg
    vdCommon.gfn_saveDf(df_out_case1, "df_out_case1", True)

    ####################################################################################################################
    # Case 2 데이타 생성
    ####################################################################################################################
    df_out_case2 = df_in_excelupload.copy()
    # 필터 적용
    df_out_case2 = df_out_case2.loc[(df_out_case2["Data type"].isin("VSL,AIR".split(",")))].copy()
    # shift 처리 - LT
    for idx in df_out_case2.index:
        if "".__ne__(fn_get_str(df_out_case2.loc[idx, "LT"])):
            shiftValue = int(float(fn_get_str(df_out_case2.loc[idx, "LT"])))
            if shiftValue > 0:
                for week_idx in range(23 - shiftValue, -1, -1):
                    # 역순으로 해서 Shift 하고
                    df_out_case2.loc[idx, weekMap[week_idx + shiftValue]] = df_out_case2.loc[idx, weekMap[week_idx]]
                    # 원 데이타 초기화
                    df_out_case2.loc[idx, weekMap[week_idx]] = 0
    vdCommon.gfn_saveDf(df_out_case2, "df_out_case2", True)

    # 필요한 컬럼만 가져온다.
    arr_header = ["Version.[Version Name]"]
    arr_header.append("Material")
    arr_header.append("Vendor_Code")
    arr_header.append("Plant_Code")
    arr_header.append("Data type")
    arr_header.append("LT")
    df_out_case2 = df_out_case2[arr_header].copy()

    # rename을 한다.
    rename_columns = {}
    rename_columns["Material"] = "Item Material.[Item Material]"
    rename_columns["Vendor_Code"] = "Location.[Location]"
    rename_columns["Plant_Code"] = "Sub Location.[Sub Location]"
    rename_columns["Data type"] = "Trans Mode.[Trans Mode]"
    rename_columns["LT"] = "Mtrl Supply Plan Sub_LT"
    df_out_case2.rename(columns=rename_columns, inplace=True)
    df_out_case2["Mtrl Supply Plan Sub_Xls Seg"] = param_user
    df_out_case2["Mtrl Supply Plan Sub_Xls Updated By"] = param_seg

    vdCommon.gfn_saveDf(df_out_case2, "df_out_case2", True)

    # 기록 데이타 생성 : 26.4.14 필요없서 주석처리
    # df_out_case2_u = df_out_case2[["Version.[Version Name]", "Item Material.[Item Material]", "Location.[Location]",
    #                                 "Sub Location.[Sub Location]", "Trans Mode.[Trans Mode]"]].copy()
    # df_out_case2_u.drop_duplicates()
    # df_out_case2_u["EU U Standard C2_Seg"] = param_seg
    # df_out_case2_u["EU U Standard C2_Created By"] = param_user
    # vdCommon.gfn_saveDf(df_out_case2_u, "df_out_case2_u", True)

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
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')

