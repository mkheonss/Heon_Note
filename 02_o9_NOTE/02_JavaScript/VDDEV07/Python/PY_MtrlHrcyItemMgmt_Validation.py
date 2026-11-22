"""
df_in_item : Select ([Version].[Version Name] * [Item Material].[Item Material] * [Hrcy Type].[Hrcy Type] ) on row, ({Measure.[Mtrl Hrchy Item_L1 Name], Measure.[Mtrl Hrchy Item_L1 NameApply], Measure.[Mtrl Hrchy Item_L1 NameOrder], Measure.[Mtrl Hrchy Item_L1 NameOrg], Measure.[Mtrl Hrchy Item_L2 Name], Measure.[Mtrl Hrchy Item_L2 NameApply], Measure.[Mtrl Hrchy Item_L2 NameOrder], Measure.[Mtrl Hrchy Item_L2 NameOrg], Measure.[Mtrl Hrchy Item_L3 Name], Measure.[Mtrl Hrchy Item_L3 NameApply], Measure.[Mtrl Hrchy Item_L3 NameOrder], Measure.[Mtrl Hrchy Item_L3 NameOrg], Measure.[Mtrl Hrchy Item_L4 Name], Measure.[Mtrl Hrchy Item_L4 NameApply], Measure.[Mtrl Hrchy Item_L4 NameApply_Name], Measure.[Mtrl Hrchy Item_L4 NameOrder], Measure.[Mtrl Hrchy Item_L4 NameOrg], Measure.[Mtrl Hrchy Item_L5 Name], Measure.[Mtrl Hrchy Item_L5 NameApply], Measure.[Mtrl Hrchy Item_L5 NameApply_Name], Measure.[Mtrl Hrchy Item_L5 NameOrder], Measure.[Mtrl Hrchy Item_L5 NameOrg], Measure.[Mtrl Hrchy Item_Mapping Rule], Measure.[Mtrl Hrchy Item_Validation]}) on column;
df_in_rule : Select ([Version].[Version Name] * [Hrcy Type].[Hrcy Type] * [Rule].[Rule No] ) on row,  ({Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L1 Order], Measure.[Mtrl Hrchy_L2 Name], Measure.[Mtrl Hrchy_L2 Order], Measure.[Mtrl Hrchy_L3 Name], Measure.[Mtrl Hrchy_L3 Order],  Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L4 Order], Measure.[Mtrl Hrchy_L5 Name], Measure.[Mtrl Hrchy_L5 Order], Measure.[Mtrl Hrchy_L1 Rule], Measure.[Mtrl Hrchy_L2 Rule], Measure.[Mtrl Hrchy_L3 Rule], Measure.[Mtrl Hrchy_L4 Rule], Measure.[Mtrl Hrchy_L5 Rule]}) on column where { coalesce(Measure.[Mtrl Hrchy_Delete Flag], "N") == "N"};
df_out_item


Select ([Version].[Version Name].[CurrentWorkingView] * [Item Material].[Item Material] * [Hrcy Type].[Hrcy Type].[Mtrl Standard] ) on row,
({Measure.[Mtrl Hrchy Item_L1 Name], Measure.[Mtrl Hrchy Item_L1 NameApply], Measure.[Mtrl Hrchy Item_L1 NameOrder], Measure.[Mtrl Hrchy Item_L1 NameOrg], Measure.[Mtrl Hrchy Item_L2 Name], Measure.[Mtrl Hrchy Item_L2 NameApply], Measure.[Mtrl Hrchy Item_L2 NameOrder], Measure.[Mtrl Hrchy Item_L2 NameOrg], Measure.[Mtrl Hrchy Item_L3 Name], Measure.[Mtrl Hrchy Item_L3 NameApply], Measure.[Mtrl Hrchy Item_L3 NameOrder], Measure.[Mtrl Hrchy Item_L3 NameOrg], Measure.[Mtrl Hrchy Item_L4 Name], Measure.[Mtrl Hrchy Item_L4 NameApply], Measure.[Mtrl Hrchy Item_L4 NameApply_Name], Measure.[Mtrl Hrchy Item_L4 NameOrder], Measure.[Mtrl Hrchy Item_L4 NameOrg], Measure.[Mtrl Hrchy Item_L5 Name], Measure.[Mtrl Hrchy Item_L5 NameApply], Measure.[Mtrl Hrchy Item_L5 NameApply_Name], Measure.[Mtrl Hrchy Item_L5 NameOrder], Measure.[Mtrl Hrchy Item_L5 NameOrg], Measure.[Mtrl Hrchy Item_Mapping Rule], Measure.[Mtrl Hrchy Item_Validation]}) on column;
Select ([Version].[Version Name].[CurrentWorkingView] * [Hrcy Type].[Hrcy Type].[Mtrl Standard] * [Rule].[Rule No] ) on row,  ({Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L1 Order], Measure.[Mtrl Hrchy_L2 Name], Measure.[Mtrl Hrchy_L2 Order], Measure.[Mtrl Hrchy_L3 Name], Measure.[Mtrl Hrchy_L3 Order],  Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L4 Order], Measure.[Mtrl Hrchy_L5 Name], Measure.[Mtrl Hrchy_L5 Order], Measure.[Mtrl Hrchy_L1 Rule], Measure.[Mtrl Hrchy_L2 Rule], Measure.[Mtrl Hrchy_L3 Rule], Measure.[Mtrl Hrchy_L4 Rule], Measure.[Mtrl Hrchy_L5 Rule]}) on column where { coalesce(Measure.[Mtrl Hrchy_Delete Flag], "N") == "N"};


.[CurrentWorkingView]
EXEC plugin instance [PY_MtrlHrchyItemMgmt_Validation] for measures {[Mtrl Hrchy Item_L1 Name]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Hrcy Type].[Hrcy Type].[Mtrl Standard] ) using arguments { (RunID, "Run_1"),(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};



"""


import numpy as np
import pandas as pd
import datetime
import logging
import platform
import os
import tabulate
import traceback
import warnings
import re

programName = "PY_MtrlHrcyItemMgmt_Validation"

################################# 나중에 라이브러리로 빼야함 ##############################################
# 로거 세팅
logging.basicConfig(level=logging.DEBUG)
comm_logger = logging.getLogger("o9_logger")
startTime = datetime.datetime.now()

log_level = "info"
def gfn_getLogLevel(str):
    if str == "debug":
        return 1
    elif str == "info":
        return 2
    elif str == "warn":
        return 3
    elif str == "error":
        return 4
    else:
        return 5


# Log 포맷 함수
def getLogger(_pluginName, _log_level=logging.DEBUG, _log_fileName="log"):
    global pluginName
    pluginName = _pluginName

    # 로컬이면 파일로 저장
    if platform.system() == 'Windows':
        comm_logger.setLevel(_log_level)
        # 일반 핸들러, 포매터 세팅
        formatter = logging.Formatter("%(asctime)s %(levelname)s : %(message)s")
        handler = logging.FileHandler(os.path.dirname(__file__) + "\\" + programName + ".log", encoding="UTF8")
        handler.setLevel(_log_level)
        handler.setFormatter(formatter)
        # 각 핸들러를 로거에 추가
        comm_logger.addHandler(handler)

    return comm_logger

def logPrefix():
    elapsed = datetime.datetime.now() - startTime
    return f"{pluginName} : {elapsed} sec : "

def log(_func, _msg, _dfName="", _print_row=3):
    if gfn_getLogLevel(_func.__name__) < gfn_getLogLevel(log_level):
        return

    if isinstance(_msg, pd.DataFrame):
        if platform.system() == 'Windows':
            _func(logPrefix() + "*" * 30 + f" {_dfName} : {len(_msg.columns)} Column, {str(len(_msg.index))} Rows " + "*" * 30 +
                f"\n" + tabulate.tabulate(_msg.head(3), headers="keys", tablefmt="fancy_grid"))
            _func(_msg.dtypes)
        else:
            _func(logPrefix() + "*"*30 + f" {_dfName} : {len(_msg.columns)} Column, {str(len(_msg.index))} Rows " + "*"*30)
            _func(logPrefix() + "Columns ==> " + "\t".join(_msg.columns))

            # 리스트 로그는 역순으로 찍어준다.
            maxCnt = len(_msg.index)
            if _print_row != 0:
                maxCnt = _print_row if len(_msg.index) > _print_row else len(_msg.index)
            for i in range(maxCnt - 1, -1, -1):
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

saveDf_idx = 1
def saveDf(_df, _csvName, _print_row=3):
    if isLocal():
        global saveDf_idx
        _df.to_csv(os.path.dirname(__file__) + "\\" + f"{programName}_out_{saveDf_idx}_{_csvName}.csv", index=False)
        saveDf_idx = saveDf_idx + 1
    else:
        log(logger.info, _df, _dfName=_csvName, _print_row=_print_row)
################################# 나중에 라이브러리로 빼야함 ##############################################



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
        elif (pd.isna(val)):
            return ""
    except Exception as e:
        log(logger.error, traceback.format_exc())
    return ""


def fn_isEq(val: str, compVal: str):
    if "".__eq__(compVal):
        return True
    else:
        firstChar = compVal[0:1]
        lastChar = compVal[-1:]
        compVal = compVal.replace("*", "")

        if "*".__eq__(firstChar) and "*".__eq__(lastChar):
            findIdx = val.find(compVal)
            if findIdx >= 0:
                return True
            else:
                return False
        elif "*".__eq__(firstChar) and "*".__ne__(lastChar):
            return val.endswith(compVal)
        elif "*".__ne__(firstChar) and "*".__eq__(lastChar):
            return val.startswith(compVal)
        elif "*".__ne__(firstChar) and "*".__ne__(lastChar):
            if val.__eq__(compVal):
                return True
            else:
                return False

def fn_concat(val1:str, val2:str, separator=","):
    if "".__eq__(val1):
        return val2
    else:
        return val1 + separator + val2

def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)

def fn_existDict(key:str):
    data = dict_dup.get(key)
    if data != None:
        return True
    else:
        return False

def fn_getDict(key:str):
    data = dict_dup.get(key)
    if data != None:
        return data
    else:
        return ""

def fn_nvl(val1:str, val2:str):
    if "".__eq__(val1) or pd.isna(val1) :
        return val2
    else:
        return val1


logger = getLogger(programName)

log(logger.info, 'plugin Execution Start')

pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
warnings.simplefilter(action='ignore', category=FutureWarning)

if isLocal():
    df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{programName}_in_item.csv", encoding="UTF-8")
    df_in_rule = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{programName}_in_rule.csv", encoding="UTF-8")

try:
    log_level = "debug"

    df_in_item["Mtrl Hrchy Item_Validation"].fillna(value="", inplace=True)
    df_in_item["Mtrl Hrchy Item_L1 NameApply"] = ""
    df_in_item["Mtrl Hrchy Item_L2 NameApply"] = ""
    df_in_item["Mtrl Hrchy Item_L3 NameApply"] = ""
    df_in_item["Mtrl Hrchy Item_L4 NameApply"] = ""
    df_in_item["Mtrl Hrchy Item_L5 NameApply"] = ""
    df_in_item["Mtrl Hrchy Item_L4 NameApply_Name"] = ""
    df_in_item["Mtrl Hrchy Item_L5 NameApply_Name"] = ""

    saveDf(df_in_item, "df_in_item")
    saveDf(df_in_rule, "df_in_rule")

    dict_dup = {}
    dict_order = {}

    # 데이타 유형 변경 : 숫자만 있어서 0001 이 정수 1로 바뀌여서 변경해줌
    df_in_rule["Rule.[Rule No]"] = df_in_rule["Rule.[Rule No]"].apply(gfn_lpad, args=(4, "0"))

    log(logger.info, 'make rule dictionary')
    for rowIdx in df_in_rule.index:
        hierarchy_1 = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L1 Name"])
        hierarchy_2 = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L2 Name"])
        hierarchy_3 = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L3 Name"])
        hierarchy_4 = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L4 Name"])
        hierarchy_5 = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L5 Name"])

        # Level 1 처리
        if not fn_existDict(hierarchy_1):
            dict_dup[hierarchy_1] = "Root"

        # Level 2 처리
        if not fn_existDict("2_" + hierarchy_2):
            dict_dup["2_" + hierarchy_2] = hierarchy_1

        # Level 3 처리
        if not fn_existDict("3_" + hierarchy_3):
            dict_dup["3_" + hierarchy_3] = hierarchy_1 + "-" + hierarchy_2

        # Level 4 처리
        if "".__ne__(hierarchy_4) and "-".__ne__(hierarchy_4):
            if not fn_existDict("4_" + hierarchy_4):
                dict_dup["4_" + hierarchy_4] = hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3

        # Level 5 처리
        if "".__ne__(hierarchy_5) and "-".__ne__(hierarchy_5):
            if not fn_existDict("5_" + hierarchy_5):
                dict_dup["5_" + hierarchy_5] = hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3 + "-" + hierarchy_4

    log(logger.info, 'validation from Item')
    for rowIdx in df_in_item.index:
        hierarchy_1 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L1 Name"])
        hierarchy_2 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L2 Name"])
        hierarchy_3 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L3 Name"])
        hierarchy_4 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L4 Name"])
        hierarchy_5 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L5 Name"])
        mappingRule = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_Mapping Rule"])

        if "".__ne__(hierarchy_1) or "".__ne__(hierarchy_2) or "".__ne__(hierarchy_3) or "".__ne__(hierarchy_4) or "".__ne__(hierarchy_5):
            hierarchyOrg_1 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L1 NameOrg"])
            hierarchyOrg_2 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L2 NameOrg"])
            hierarchyOrg_3 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L3 NameOrg"])
            hierarchyOrg_4 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L4 NameOrg"])
            hierarchyOrg_5 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L5 NameOrg"])

            hierarchy_1 = fn_nvl(hierarchy_1, hierarchyOrg_1)
            hierarchy_2 = fn_nvl(hierarchy_2, hierarchyOrg_2)
            hierarchy_3 = fn_nvl(hierarchy_3, hierarchyOrg_3)
            hierarchy_4 = fn_nvl(fn_nvl(hierarchy_4, hierarchyOrg_4), "*")
            hierarchy_5 = fn_nvl(fn_nvl(hierarchy_5, hierarchyOrg_5), "*")
            # log(logger.debug, 'hierarchy_1 : ' + hierarchy_1 + ' , hierarchy_2 : ' + hierarchy_2 + ' , hierarchy_3 : ' + hierarchy_3 + ' , hierarchy_4 : ' + hierarchy_4 + ' , hierarchy_5 : ' + hierarchy_5)

            valid = ""

            # Level 2 처리
            if fn_existDict("2_" + hierarchy_2):
                dictValue = fn_getDict("2_" + hierarchy_2)
                if hierarchy_1.__ne__(dictValue):
                    valid = fn_concat(valid, f"{hierarchy_2} (2 Level) is already registered in {dictValue}")

            # Level 3 처리
            if fn_existDict("3_" + hierarchy_3):
                dictValue = fn_getDict("3_" + hierarchy_3)
                if (hierarchy_1 + "-" + hierarchy_2).__ne__(dictValue):
                    valid = fn_concat(valid, f"{hierarchy_3} (3 Level) is already registered in {dictValue}")

            # Level 4 처리
            if "".__ne__(hierarchy_4) and "-".__ne__(hierarchy_4):
                if fn_existDict("4_" + hierarchy_4):
                    dictValue = fn_getDict(hierarchy_4)
                    if (hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3).__ne__(dictValue):
                        valid = fn_concat(valid, f"{hierarchy_4} (4 Level) is already registered in {dictValue}")

            # Level 5 처리
            if "".__ne__(hierarchy_5) and "-".__ne__(hierarchy_5):
                if fn_existDict("5_" + hierarchy_5):
                    dictValue = fn_getDict("5_" + hierarchy_5)
                    if (hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3 + "-" + hierarchy_4).__ne__(dictValue):
                        valid = fn_concat(valid, f"{hierarchy_5} (5 Level) is already registered in {dictValue}")

            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_Validation"] = valid
        else:
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_Validation"] = ""

            hierarchy_1 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L1 NameOrg"])
            hierarchy_2 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L2 NameOrg"])
            hierarchy_3 = fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L3 NameOrg"])
            hierarchy_4 = fn_nvl(fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L4 NameOrg"]), "*")
            hierarchy_5 = fn_nvl(fn_get_str(df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L5 NameOrg"]), "*")

        if "-".__ne__(mappingRule):
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L1 NameApply"] = hierarchy_1
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L2 NameApply"] = hierarchy_2
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L3 NameApply"] = hierarchy_3
            if "".__ne__(hierarchy_4):
                df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L4 NameApply"] = hierarchy_4 + "(" + hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3 + ")"
                df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L5 NameApply"] = hierarchy_5 + "(" + hierarchy_1 + "-" + hierarchy_2 + "-" + hierarchy_3 + "-" + hierarchy_4 + ")"
            if "".__ne__(hierarchy_5):
                df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L4 NameApply_Name"] = hierarchy_4
                df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L5 NameApply_Name"] = hierarchy_5
        else:
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L1 NameApply"] = ""
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L2 NameApply"] = ""
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L3 NameApply"] = ""
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L4 NameApply"] = ""
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L5 NameApply"] = ""
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L4 NameApply_Name"] = ""
            df_in_item.loc[rowIdx, "Mtrl Hrchy Item_L5 NameApply_Name"] = ""

    df_out_item = df_in_item.copy()
    saveDf(df_out_item, "df_out_item")

    # 데이터 파일 저장
    if isLocal():
        log(logger.info, 'csv save')
        df_out_item.to_csv(os.path.dirname(__file__) + "\\" + f"{programName}_out_item.csv", index=False)
except Exception as e:
    log(logger.error, traceback.format_exc())
    #raise Exception(e)
finally:
    log(logger.info, 'plugin Execution End')

