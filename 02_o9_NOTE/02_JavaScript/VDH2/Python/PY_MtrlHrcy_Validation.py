"""
df_in_main : Select ([Version].[Version Name] * [Hrcy Type].[Hrcy Type] * [Rule].[Rule No] ) on row,  ({Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L1 Order], Measure.[Mtrl Hrchy_L2 Name], Measure.[Mtrl Hrchy_L2 Order], Measure.[Mtrl Hrchy_L3 Name], Measure.[Mtrl Hrchy_L3 Order],  Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L4 Order], Measure.[Mtrl Hrchy_L5 Name], Measure.[Mtrl Hrchy_L5 Order], Measure.[Mtrl Hrchy_L1 Rule], Measure.[Mtrl Hrchy_L2 Rule], Measure.[Mtrl Hrchy_L3 Rule], Measure.[Mtrl Hrchy_L4 Rule], Measure.[Mtrl Hrchy_L5 Rule]}) on column where { coalesce(Measure.[Mtrl Hrchy_Delete Flag], "N") == "N"};
df_out_main

EXEC plugin instance [PY_MtrlHrcy_Validation] for measures {[Mtrl Hrcy_L1 Name]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Hrcy Type].[Hrcy Type].[Mtrl Standard] ) using arguments {(RunID, "Run_019"),(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};



"""


import pandas as pd
import os
import traceback
import common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MtrlHrcy_Validation'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

########################################################################################################################
# 함수 정의
########################################################################################################################
def gfn_existDict(dic:dict, key:str):
    data = dic.get(key)
    if data != None:
        return True
    else:
        return False

def gfn_getDict(dic:dict, key:str):
    data = dic.get(key)
    if data != None:
        return data
    else:
        return None

def gfn_str(val):
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
    except Exception as e:
        # log(logger.error, traceback.format_exc())
        pass
    return ""

def gfn_str_concat(val1:str, val2:str, separator=","):
    if "".__eq__(val1):
        return val2
    else:
        return val1 + separator + val2

def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)

saveDf_idx = 1
def saveDf(_df, _csvName):
    if is_local:
        global saveDf_idx
        _df.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_{saveDf_idx}_{_csvName}.csv", index=False)
        saveDf_idx = saveDf_idx + 1

    logger.PrintDF(p_df=_df, p_df_name=_csvName, p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)

########################################################################################################################
# Main 로직
########################################################################################################################

logger.Start()
stepIdx = 0

stepIdx += 1
logger.Step(p_step_no=stepIdx, p_step_desc=f'plugin Execution Start')

if is_local:
    df_in_main = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_main.csv", encoding="UTF-8")

try:
    dict_dup = {}

    # 데이타 유형 변경 : 숫자만 있어서 0001 이 정수 1로 바뀌여서 변경해줌
    df_in_main["Rule.[Rule No]"] = df_in_main["Rule.[Rule No]"].apply(gfn_lpad, args=(4, "0"))

    for rowIdx in df_in_main.index:
        hierarchy_1 = gfn_str(df_in_main.loc[rowIdx, "Mtrl Hrchy_L1 Name"])
        hierarchy_2 = gfn_str(df_in_main.loc[rowIdx, "Mtrl Hrchy_L2 Name"])
        hierarchy_3 = gfn_str(df_in_main.loc[rowIdx, "Mtrl Hrchy_L3 Name"])
        hierarchy_4 = gfn_str(df_in_main.loc[rowIdx, "Mtrl Hrchy_L4 Name"])
        hierarchy_5 = gfn_str(df_in_main.loc[rowIdx, "Mtrl Hrchy_L5 Name"])
        hierarchyRule_4 = gfn_str(df_in_main.loc[rowIdx, "Mtrl Hrchy_L4 Rule"])
        hierarchyRule_5 = gfn_str(df_in_main.loc[rowIdx, "Mtrl Hrchy_L5 Rule"])
        valid = ""

        if "".__eq__(hierarchy_1) and "".__ne__(hierarchy_2):
            valid = gfn_str_concat(valid, f"There is no level 1 data.")
        if "".__eq__(hierarchy_2) and "".__ne__(hierarchy_3):
            valid = gfn_str_concat(valid, f"There is no level 2 data.")
        if "".__eq__(hierarchy_3) and "".__ne__(hierarchy_4):
            valid = gfn_str_concat(valid, f"There is no level 3 data.")
        if "".__eq__(hierarchy_4) and "".__ne__(hierarchy_5):
            valid = gfn_str_concat(valid, f"There is no level 4 data.")

        # Level 1 처리
        if not gfn_existDict(dict_dup, hierarchy_1):
            dict_dup[hierarchy_1] = { "level" : "Root", "idx" : rowIdx }

        # Level 2 체크
        if gfn_existDict(dict_dup, "2_" + hierarchy_2):
            dictValue = gfn_getDict(dict_dup, "2_" + hierarchy_2)
            if dictValue != None and hierarchy_1.__ne__(dictValue["level"]):
                valid = gfn_str_concat(valid, f"{hierarchy_2} (2 Level) is already registered in {dictValue['level']}")

                oValid = gfn_str_concat(df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"],f"{hierarchy_2} (3 Level) is already registered in {hierarchy_1}")
                df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"] = oValid
        else:
            dict_dup["2_" + hierarchy_2] = { "level" : hierarchy_1, "idx" : rowIdx }

        # Level 3 체크
        if gfn_existDict(dict_dup, "3_" + hierarchy_3):
            dictValue = gfn_getDict(dict_dup, "3_" + hierarchy_3)
            if dictValue != None and (hierarchy_1 + "-" + hierarchy_2).__ne__(dictValue["level"]):
                valid = gfn_str_concat(valid, f"{hierarchy_3} (3 Level) is already registered in {dictValue['level']}")

                oValid = gfn_str_concat(df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"], f"{hierarchy_3} (3 Level) is already registered in {hierarchy_1 + '-' + hierarchy_2}")
                df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"] = oValid
        else:
            dict_dup["3_" + hierarchy_3] = { "level" : hierarchy_1 + "-" + hierarchy_2, "idx" : rowIdx }

        # Level 4 체크
        if "".__ne__(hierarchy_4) and "-".__ne__(hierarchy_4):
            if gfn_existDict(dict_dup, "4_" + hierarchy_4):
                dictValue = gfn_getDict(dict_dup, hierarchy_4)
                if dictValue != None and (hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3).__ne__(dictValue["level"]):
                    valid = gfn_str_concat(valid, f"{hierarchy_4} (4 Level) is already registered in {dictValue['level']}")

                    oValid = gfn_str_concat(df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"],f"{hierarchy_4} (3 Level) is already registered in {hierarchy_1 + '-' + hierarchy_2 + '-' + hierarchy_3}")
                    df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"] = oValid
            else:
                dict_dup["4_" + hierarchy_4] = { "level" : hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3, "idx" : rowIdx }

        # Level 5 체크
        if "".__ne__(hierarchy_5) and "-".__ne__(hierarchy_5):
            if gfn_existDict(dict_dup, "5_" + hierarchy_5):
                dictValue = gfn_getDict(dict_dup, "5_" + hierarchy_5)
                if dictValue != None and (hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3 + "-" + hierarchy_4).__ne__(dictValue["level"]):
                    valid = gfn_str_concat(valid, f"{hierarchy_5} (5 Level) is already registered in {dictValue['level']}")

                    oValid = gfn_str_concat(df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"],f"{hierarchy_5} (3 Level) is already registered in {hierarchy_1 + '-' + hierarchy_2 + '-' + hierarchy_3 + '-' + hierarchy_4}")
                    df_in_main.loc[dictValue['idx'], "Mtrl Hrchy_Validation"] = oValid
            else:
                dict_dup["5_" + hierarchy_5] = { "level" : hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3 + "-" + hierarchy_4, "idx" : rowIdx }

        # Name, Rule 체크
        if "".__ne__(hierarchy_4) and "-".__ne__(hierarchy_4) and "".__ne__(hierarchyRule_4):
            valid = gfn_str_concat(valid, f"{hierarchy_4} and {hierarchyRule_4} cannot be registered together.")
        if "".__ne__(hierarchy_5) and "-".__ne__(hierarchy_5) and "".__ne__(hierarchyRule_5):
            valid = gfn_str_concat(valid, f"{hierarchy_5} and {hierarchyRule_5} cannot be registered together.")

        df_in_main.loc[rowIdx, "Mtrl Hrchy_Validation"] = valid

    saveDf(df_in_main, 'df_in_main')

    df_out_main = df_in_main.copy()

    # 데이터 파일 저장
    if is_local:
        stepIdx += 1
        logger.Step(p_step_no=stepIdx, p_step_desc=f'Final Output Table create')
        df_out_main.to_csv(f"{str_instance}_out_main.csv", index=False)
except Exception as e:
    trace_msg = traceback.format_exc()
    logger.Note(p_note=trace_msg, p_log_level=common.G_log_level.debug())
    logger.Error()
    raise Exception(e)
finally:
    stepIdx += 1
    logger.Step(p_step_no=stepIdx, p_step_desc=f'plugin Execution End')
    logger.Finish()
