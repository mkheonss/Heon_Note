"""
df_in_item : select ([Item Material].[Item Material] * [Item Material].[zzMaterial Code] * [Item Material].[zzMaterial Code Descriptioin] * [Item Material].[zzLong Desc] * [Item Material].[zzMat Group] * [Item Material].[zzSort3] * [Item Material].[zzInch] * [Item Material].[zzInch Group] * [Item Material].[Represent Vendor] );
df_in_rule : Select ([Version].[Version Name] * [Hrcy Type].[Hrcy Type] * [Rule].[Rule No].filter(#.Name != "-") * [Group].[Group ID] ) on row, ({Measure.[Mtrl Hrchy Map Rule_SORT3], Measure.[Mtrl Hrchy Map Rule_Code], Measure.[Mtrl Hrchy Map Rule_Desc], Measure.[Mtrl Hrchy Map Rule_Grp], Measure.[Mtrl Hrchy Map Rule_Long Desc], Measure.[Mtrl Hrchy Map Rule_Priority], Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L2 Name], Measure.[Mtrl Hrchy_L3 Name], Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L5 Name], Measure.[Mtrl Hrchy_L4 Rule], Measure.[Mtrl Hrchy_L5 Rule], Measure.[Mtrl Hrchy_L1 Order], Measure.[Mtrl Hrchy_L2 Order], Measure.[Mtrl Hrchy_L3 Order], Measure.[Mtrl Hrchy_L4 Order], Measure.[Mtrl Hrchy_L5 Order], Measure.[Mtrl Hrchy_Validation], Measure.[Mtrl Hrchy_Delete Flag], Measure.[Mtrl Hrchy_SCM Material], Measure.[Mtrl Hrchy Map Rule_Apply Flag]}) on column where { Measure.[Mtrl Hrchy Map Rule_Apply Flag] == True };
df_in_inch : select ([Item Material].[zzInch]) orderby [Item Material].[zzInch].Name;
df_in_inchGroup : select ([Item Material].[zzInch Group]) orderby [Item Material].[zzInch Group].Name;
df_in_vendor : select ([Item Material].[Represent Vendor]) orderby [Item Material].[Represent Vendor].Name;

df_out_item : Select ([Version].[Version Name] * [Hrcy Type].[Hrcy Type] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Hrchy Item_L1 Name], Measure.[Mtrl Hrchy Item_L1 NameOrg], Measure.[Mtrl Hrchy Item_L2 Name], Measure.[Mtrl Hrchy Item_L2 NameOrg], Measure.[Mtrl Hrchy Item_L3 Name], Measure.[Mtrl Hrchy Item_L3 NameOrg], Measure.[Mtrl Hrchy Item_L4 Name], Measure.[Mtrl Hrchy Item_L4 NameOrg], Measure.[Mtrl Hrchy Item_L5 Name], Measure.[Mtrl Hrchy Item_L5 NameOrg], Measure.[Mtrl Hrchy Item_Lock], Measure.[Mtrl Hrchy Item_Mapping Rule], Measure.[Mtrl Hrchy Item_Status]}) on column;


.[CurrentWorkingView]
EXEC plugin instance [PY_MtrlHrchyMapRule_Approval] for measures {[Mtrl Hrchy Map Rule_Code]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Hrcy Type].[Hrcy Type].[Mtrl Standard] ) using arguments {(HrcyType, "Mtrl Standard"), (RunID, "Run_1"),(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};



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

programName = "PY_MtrlHrchyMapRule_Approval"

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

def fn_nvl(val1:str, val2:str):
    if "".__eq__(val1) or pd.isna(val1) :
        return val2
    else:
        return val1

def fn_getDict(key:str):
    data = dict_order.get(key)
    if data != None:
        return data
    else:
        return ""

logger = getLogger(programName)

log(logger.info, 'plugin Execution Start')

pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
warnings.simplefilter(action='ignore', category=FutureWarning)

if isLocal():
    df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{programName}_in_item.csv", encoding="UTF-8")
    df_in_rule = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{programName}_in_rule.csv", encoding="UTF-8")
    df_in_inch = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{programName}_in_inch.csv", encoding="UTF-8")
    df_in_inchGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{programName}_in_inchGroup.csv", encoding="UTF-8")
    df_in_vendor = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{programName}_in_vendor.csv", encoding="UTF-8")
    HrcyType = "Mtrl Standard"

try:
    log_level = "debug"

    df_in_item["Version.[Version Name]"] = "CurrentWorkingView"
    df_in_item["Hrcy Type.[Hrcy Type]"] = HrcyType
    df_in_item["Mtrl Hrchy Item_Mapping Rule"] = ""
    df_in_item["Mtrl Hrchy Item_L1 NameOrg"] = ""
    df_in_item["Mtrl Hrchy Item_L2 NameOrg"] = ""
    df_in_item["Mtrl Hrchy Item_L3 NameOrg"] = ""
    df_in_item["Mtrl Hrchy Item_L4 NameOrg"] = ""
    df_in_item["Mtrl Hrchy Item_L5 NameOrg"] = ""
    df_in_item["Mtrl Hrchy Item_Validation"] = ""

    df_in_item["Mtrl Hrchy Item_L1 NameOrder"] = np.nan
    df_in_item["Mtrl Hrchy Item_L2 NameOrder"] = np.nan
    df_in_item["Mtrl Hrchy Item_L3 NameOrder"] = np.nan
    df_in_item["Mtrl Hrchy Item_L4 NameOrder"] = np.nan
    df_in_item["Mtrl Hrchy Item_L5 NameOrder"] = np.nan

    df_in_rule["Mtrl Hrchy_Validation"].fillna(value="", inplace=True)
    df_in_rule["Mtrl Hrchy_Delete Flag"].fillna(value="", inplace=True)

    df_in_rule.loc[((df_in_rule["Mtrl Hrchy_Validation"] == ""), 'flag_1')] = True
    df_in_rule.loc[((df_in_rule["Mtrl Hrchy_Delete Flag"] != "Y"), 'flag_2')] = True
    df_in_rule.loc[((df_in_rule["Mtrl Hrchy_SCM Material"] == True), 'flag_3')] = True
    df_in_rule = df_in_rule.loc[(df_in_rule["flag_1"] == True) & (df_in_rule["flag_2"] == True) & (df_in_rule["flag_3"] == True)].copy()

    saveDf(df_in_rule, "df_in_rule")
    saveDf(df_in_inch, "df_in_inch")
    saveDf(df_in_inchGroup, "df_in_inchGroup")
    saveDf(df_in_vendor, "df_in_vendor")

    # Priority 로 정렬
    df_in_rule = df_in_rule.sort_values(by=["Mtrl Hrchy Map Rule_Priority"], ascending=[True])

    dict_order = {}
    for rowIdx in df_in_inch.index:
        dict_order["I_" + fn_get_str(df_in_inch.loc[rowIdx, "Item Material.[zzInch]"])] = rowIdx + 1
    for rowIdx in df_in_inchGroup.index:
        dict_order["IG_" + fn_get_str(df_in_inchGroup.loc[rowIdx, "Item Material.[zzInch Group]"])] = rowIdx + 1
    for rowIdx in df_in_vendor.index:
        dict_order["V_" + fn_get_str(df_in_vendor.loc[rowIdx, "Item Material.[Represent Vendor]"])] = rowIdx + 1

    for rowIdx in df_in_rule.index:
        priority = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy Map Rule_Priority"])
        code = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy Map Rule_Code"])
        desc = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy Map Rule_Desc"])
        longDesc = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy Map Rule_Long Desc"])
        matGroup = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy Map Rule_Grp"])
        sort3 = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy Map Rule_SORT3"])

        log(logger.info, 'code : ' + code + ', desc : ' + desc + ', longDesc : ' + longDesc + ', matGroup : ' + matGroup + ', sort3 : ' + sort3 + ', priority : ' + priority)

        l1Name = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L1 Name"])
        l2Name = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L2 Name"])
        l3Name = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L3 Name"])
        l4Name = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L4 Name"])
        l5Name = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L5 Name"])

        l4Rule = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L4 Rule"])
        l5Rule = fn_get_str(df_in_rule.loc[rowIdx, "Mtrl Hrchy_L5 Rule"])

        l1Order = df_in_rule.loc[rowIdx, "Mtrl Hrchy_L1 Order"]
        l2Order = df_in_rule.loc[rowIdx, "Mtrl Hrchy_L2 Order"]
        l3Order = df_in_rule.loc[rowIdx, "Mtrl Hrchy_L3 Order"]
        l4Order = df_in_rule.loc[rowIdx, "Mtrl Hrchy_L4 Order"]
        l5Order = df_in_rule.loc[rowIdx, "Mtrl Hrchy_L5 Order"]

        # "-" 데이타는 공백처리
        if "-".__eq__(code):
            code = ""
        if "-".__eq__(desc):
            desc = ""
        if "-".__eq__(longDesc):
            longDesc = ""
        if "-".__eq__(matGroup):
            matGroup = ""
        if "-".__eq__(sort3):
            sort3 = ""

        for itemRowIdx in df_in_item.index:
            item = df_in_item.loc[itemRowIdx, "Item Material.[Item Material]"]

            # log(logger.debug, item + " : [" + fn_get_str(df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_Mapping Rule"]) + "]")
            if "-".__eq__(fn_nvl(fn_get_str(df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_Mapping Rule"]), "-")):
                itemCode = fn_get_str(df_in_item.loc[itemRowIdx, "Item Material.[zzMaterial Code]"])
                itemDesc = fn_get_str(df_in_item.loc[itemRowIdx, "Item Material.[zzMaterial Code Descriptioin]"])
                itemLongDesc = fn_get_str(df_in_item.loc[itemRowIdx, "Item Material.[zzLong Desc]"])
                itemMatGroup = fn_get_str(df_in_item.loc[itemRowIdx, "Item Material.[zzMat Group]"])
                itemSort3 = fn_get_str(df_in_item.loc[itemRowIdx, "Item Material.[zzSort3]"])

                if fn_isEq(itemCode, code) & fn_isEq(itemDesc, desc) & fn_isEq(itemLongDesc, longDesc) & fn_isEq(itemMatGroup, matGroup) & fn_isEq(itemSort3, sort3):
                    # log(logger.info, 'itemCode : ' + itemCode + ', itemDesc : ' + itemDesc + ', itemLongDesc : ' + itemLongDesc + ', itemMatGroup : ' + itemMatGroup + ', itemSort3 : ' + itemSort3)
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_Mapping Rule"] = fn_get_str(df_in_rule.loc[rowIdx, "Group.[Group ID]"])

                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L1 NameOrg"] = l1Name
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L2 NameOrg"] = l2Name
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L3 NameOrg"] = l3Name

                    l4NewName = ""
                    if "".__eq__(l4Name) and "".__eq__(l4Rule):
                        l4NewName = "*"
                        l4Order = 1
                    elif "".__ne__(l4Name) and "".__eq__(l4Rule):
                        l4NewName = l4Name
                        l4Order = 1
                    elif "".__eq__(l4Name) and "".__ne__(l4Rule):
                        if "Inch Group".__eq__(l4Rule):
                            l4NewName = df_in_item.loc[itemRowIdx, "Item Material.[zzInch Group]"]
                            l4Order = fn_getDict("IG_" + l4NewName)
                        elif "Inch".__eq__(l4Rule):
                            l4NewName = df_in_item.loc[itemRowIdx, "Item Material.[zzInch]"]
                            l4Order = fn_getDict("I_" + l4NewName)
                        elif "Vendor".__eq__(l4Rule):
                            l4NewName = df_in_item.loc[itemRowIdx, "Item Material.[Represent Vendor]"]
                            l4Order = fn_getDict("V_" + l4NewName)
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L4 NameOrg"] = fn_get_str(l4NewName)

                    l5NewName = ""
                    if "".__eq__(l5Name) and "".__eq__(l5Rule):
                        l5NewName = "*"
                        l5Order = 1
                    elif "".__ne__(l5Name) and "".__eq__(l5Rule):
                        l5NewName = l5Name
                        l5Order = 1
                    elif "".__eq__(l5Name) and "".__ne__(l5Rule):
                        if "Inch Group".__eq__(l5Rule):
                            l5NewName = df_in_item.loc[itemRowIdx, "Item Material.[zzInch Group]"]
                            l5Order = fn_getDict("IG_" + l5NewName)
                        elif "Inch".__eq__(l5Rule):
                            l5NewName = df_in_item.loc[itemRowIdx, "Item Material.[zzInch]"]
                            l5Order = fn_getDict("I_" + fn_get_str(l5NewName))
                        elif "Vendor".__eq__(l5Rule):
                            l5NewName = df_in_item.loc[itemRowIdx, "Item Material.[Represent Vendor]"]
                            l5Order = fn_getDict("V_" + l5NewName)
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L5 NameOrg"] = fn_get_str(l5NewName)

                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L1 NameOrder"] = l1Order
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L2 NameOrder"] = l2Order
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L3 NameOrder"] = l3Order
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L4 NameOrder"] = l4Order
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_L5 NameOrder"] = l5Order
                else:
                    df_in_item.loc[itemRowIdx, "Mtrl Hrchy Item_Mapping Rule"] = "-"

    df_out_item = df_in_item[["Version.[Version Name]", "Hrcy Type.[Hrcy Type]", "Item Material.[Item Material]",
                              "Mtrl Hrchy Item_L1 NameOrg", "Mtrl Hrchy Item_L2 NameOrg", "Mtrl Hrchy Item_L3 NameOrg",
                              "Mtrl Hrchy Item_L4 NameOrg", "Mtrl Hrchy Item_L5 NameOrg", "Mtrl Hrchy Item_Mapping Rule",
                              "Mtrl Hrchy Item_L1 NameOrder", "Mtrl Hrchy Item_L2 NameOrder", "Mtrl Hrchy Item_L3 NameOrder",
                              "Mtrl Hrchy Item_L4 NameOrder", "Mtrl Hrchy Item_L5 NameOrder", "Mtrl Hrchy Item_Validation"]].copy()

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

