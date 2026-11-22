"""

df_in_item : select (&LCMItem.relatedmembers([Item]) * Item.[Product Group] * Item.[Product] * Item.[Class Category] * Item.[Product Code] * Item.[Project] * Item.[SCM Type] * Item.[Model Name] * Item.[Buyer]) on row, () on column include memberproperties {Item.[Item], [Init Date]};
df_in_itemCis : Select ([Version].[Version Name] * &LCMItem.relatedmembers([Item]) ) on row, ({Measure.[Lcm Item CIS Attr_Attr_Values]}) on column;
df_in_attrMap : Select ([Version].[Version Name] * [Item].[Class Category] * [Sequence].[Sequence] * [Product].[Product] * [Attr No].[Attr No] ) on row, ({Measure.[Lcm Item Attr Map_CIS Attr Id], Measure.[Lcm Item Attr Map_Condition01], Measure.[Lcm Item Attr Map_Condition02], Measure.[Lcm Item Attr Map_Condition03], Measure.[Lcm Item Attr Map_Condition04], Measure.[Lcm Item Attr Map_Condition05], Measure.[Lcm Item Attr Map_Field01], Measure.[Lcm Item Attr Map_Field02], Measure.[Lcm Item Attr Map_Field03], Measure.[Lcm Item Attr Map_Field04], Measure.[Lcm Item Attr Map_Field05], Measure.[Lcm Item Attr Map_Fix], Measure.[Lcm Item Attr Map_Logic], Measure.[Lcm Item Attr Map_Rule Seq], Measure.[Lcm Item Attr Map_RuleNo], Measure.[Lcm Item Attr Map_Valid], Measure.[Lcm Item Attr Map_Value01], Measure.[Lcm Item Attr Map_Value02], Measure.[Lcm Item Attr Map_Value03], Measure.[Lcm Item Attr Map_Value04], Measure.[Lcm Item Attr Map_Value05]}) on column;
df_in_itemEtc : Select ([Version].[Version Name] * &LCMItem.relatedmembers([Item]) ) on row, ({Measure.[Lcm Item Attr Ref_ETC01], Measure.[Lcm Item Attr Ref_ETC02], Measure.[Lcm Item Attr Ref_ETC03], Measure.[Lcm Item Attr Ref_ETC04], Measure.[Lcm Item Attr Ref_ETC05], Measure.[Lcm Item Attr Ref_ETC06], Measure.[Lcm Item Attr Ref_ETC07], Measure.[Lcm Item Attr Ref_ETC08], Measure.[Lcm Item Attr Ref_ETC09], Measure.[Lcm Item Attr Ref_ETC10], Measure.[Lcm Item Attr Ref_ETC11], Measure.[Lcm Item Attr Ref_ETC12], Measure.[Lcm Item Attr Ref_ETC13], Measure.[Lcm Item Attr Ref_ETC14], Measure.[Lcm Item Attr Ref_ETC15]}) on column;
df_in_itemRef  : Select ([Version].[Version Name] * &LCMItem.relatedmembers([Item]) ) on row, ({Measure.[Lcm Item Attr Ref_3in1], Measure.[Lcm Item Attr Ref_Boding], Measure.[Lcm Item Attr Ref_CY Code], Measure.[Lcm Item Attr Ref_Cell Vendor], Measure.[Lcm Item Attr Ref_DP Code], Measure.[Lcm Item Attr Ref_Definition], Measure.[Lcm Item Attr Ref_Inch], Measure.[Lcm Item Attr Ref_Mini Led], Measure.[Lcm Item Attr Ref_Open Cell], Measure.[Lcm Item Attr Ref_Project], Measure.[Lcm Item Attr Ref_Series], Measure.[Lcm Item Attr Ref_Set Item], Measure.[Lcm Item Attr Ref_Hz], Measure.[Lcm Item Attr Ref_Init Year], Measure.[Lcm Item Attr Ref_Strategy]}) on column;
df_in_itemAttr  : Select ([Version].[Version Name] * [Product].[Product] * [Attr No].[Attr No] ) on row, ({Measure.[Lcm Prod Attr_Attr Name]}) on column;
df_in_org : Select ([Version].[Version Name] * [Item].[Item] ) on row, ({Measure.[Lcm Item Attr_Attr01], Measure.[Lcm Item Attr_Attr02], Measure.[Lcm Item Attr_Attr03], Measure.[Lcm Item Attr_Attr04], Measure.[Lcm Item Attr_Attr05], Measure.[Lcm Item Attr_Attr06], Measure.[Lcm Item Attr_Attr07], Measure.[Lcm Item Attr_Attr08], Measure.[Lcm Item Attr_Attr09], Measure.[Lcm Item Attr_Attr10], Measure.[Lcm Item Attr_Attr11], Measure.[Lcm Item Attr_Attr12], Measure.[Lcm Item Attr_Attr13], Measure.[Lcm Item Attr_Attr14], Measure.[Lcm Item Attr_Attr15]}) on column;

df_out

pDetailLogFlag = "N"
outVersionName = "CWV_MP"

EXEC plugin instance [PY_UI_LcmItemAttrMap]
for measures {[Lcm Item Attr Ref_Inch]}
using scope ( &CWVUI * [Item].[Class Category].[95DZ] )
using arguments {(outVersionName, "CWV_MP"),(pDetailLogFlag, "N"),(RunID, "Run_01"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

, ([Param.o9_sys_log_level], "DEBUG")

"""

import numpy as np
import pandas as pd
import os
import traceback
import warnings
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_LcmItemAttrMap'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 함수 정의
########################################################################################################################
def gfn_isnull(val):
    # log(logger.info, str(type(val)))
    if ( type(val) is str ):
        if (val == ""):
            return True
        else:
            return False
    elif ( type(val) is float ):
        if (pd.isna(val)):
            return True
        else:
            return False

def gfn_isnotnull(val):
    return not gfn_isnull(val)

# 스트링을 넘겨준다.
def gfn_get_str(val):
    try:
        if (type(val) is str):
            return val
        elif (type(val) is bool):
            if val:
                return "True"
            else:
                return "False"
        elif (type(val) is dict):
            returnStr = ""
            for item in val.items():
                returnStr = returnStr + item.__str__() + " "

            return returnStr
        else:
            if (pd.isna(val)):
                return ""
            else:
                return str(val)
    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    return ""

"""입력된 숫자 또는 문자열 왼쪽에 fillchar 문자로 패딩"""
def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)


"""입력된 숫자 또는 문자열 오른쪽에 fillchar 문자로 패딩"""
def gfn_rpad(val, width, fillchar='0'):
    return str(val).ljust(width, fillchar)

def isLt(val: str, compVal: str):
    return val.__lt__(compVal)
def isLe(val: str, compVal: str):
    return val.__le__(compVal)
def isGt(val: str, compVal: str):
    return val.__gt__(compVal)
def isGe(val: str, compVal: str):
    return val.__ge__(compVal)
def isEq(val: str, compVal: str):
    return val.__eq__(compVal)
def isNe(val: str, compVal: str):
    return val.__ne__(compVal)
def isStartLike(val: str, compVal: str):
    return val.startswith(compVal)
def isNotStartLike(val: str, compVal: str):
    return not val.startswith(compVal)
def isEndLike(val: str, compVal: str):
    return val.endwith(compVal)
def isFind(val: str, compVal: str):
    findIdx = val.find(compVal)
    if findIdx >= 0:
        return True
    else:
        return False
def isNotFind(val: str, compVal: str):
    findIdx = val.find(compVal)
    if findIdx >= 0:
        return False
    else:
        return True
def isNotNull(val: str, compVal: str):
    if val != np.nan and "".__ne__(val):
        return True
    else:
        return False
def isNull(val: str, compVal: str):
    if val == np.nan or "".__eq__(val):
        return True
    else:
        return False
def isIn(val: str, compVal: str):
    # if any(val == s for s in compVal.split("^")):
    #     return True
    # else:
    #     return False
    if ("^" + compVal + "^").find("^" + val + "^") > -1:
        return True
    else:
        return False
def isNotIn(val: str, compVal: str):
    # isExist = False
    # for s in compVal.split("^"):
    #     if val == s:
    #         isExist = True
    #         break
    # return not isExist
    if ("^" + compVal + "^").find("^" + val + "^") > -1:
        return False
    else:
        return True
def inStr(val, separator):
    return val.find(separator)
def isInt(val: str, tempVal: str):
    return str.isdigit(val)
def isNotInt(val: str, tempVal: str):
    return not str.isdigit(val)
def isNumber(val: str, tempVal=""):
    try:
        num = float(val)
    except:
        return False

    return True
def isNotInt(val: str, tempVal: str):
    return not str.isdigit(val)
def isAlpha(val: str, tempVal: str):
    return str.isalpha(val)
def isNotAlpha(val: str, tempVal: str):
    return not str.isalpha(val)
def isIntBetween(val: str, sVal: str, eVal: str):
    try:
        if int(val) >= int(sVal) and int(val) <= int(eVal):
            return True
        else:
            return False
    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
def subStr(val, sPos, ePos=0):
    try:
        if ePos == 0:
            ePos = len(val)

        return val[sPos:ePos]
    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
def length(val):
    return str(len(val))
def nvl(val, replaceVal):
    if (val is None) | ("".__eq__(val)):
        return replaceVal
    else:
        return val
def decode(val:str, compVal:str, falseVal:str):
    if compVal.find("^") > -1:
        compValArr = compVal.split("^")

        for i in range(len(compValArr)):
            compKey = compValArr[i].split(":")[0]
            compValue = compValArr[i].split(":")[1]
            idx = compKey.find("%")
            if idx == 0:
                if val.endswith(compKey.replace("%","")):
                    return compValue
            elif idx == len(compKey) - 1:
                if val.startswith(compKey.replace("%","")):
                    return compValue
            else:
                if val.__eq__(compKey):
                    return compValue
    else:
        compKey = compVal.split(":")[0]
        compValue = compVal.split(":")[1]
        if val.__eq__(compKey):
            return compValue

    return falseVal
def split(val:str, splitStr:str, idx:int, otherIdx=0):
    arr = val.split(splitStr)
    if len(arr) > idx:
        return arr[idx]
    else:
        return arr[otherIdx]
def numberSplit(val:str, idx:int):
    tVal = ""
    isNumber = False
    for i in range(len(val)):
        if "0123456789".find(val[i]) < 0:
            tVal += val[i]
            isNumber = False
        elif "0123456789".find(val[i]) > -1 and isNumber == False:
            tVal += " "
            isNumber = True

    arr = tVal.split(" ")
    if len(arr) > idx:
        return arr[idx]
    else:
        return ""
def digit(val):
    digitStr = ""
    for i in range(len(val)):
        if "0123456789".find(val[i]) > -1:
            digitStr += val[i]
    return digitStr
def alphabet(val):
    alphabetStr = ""
    for i in range(len(val)):
        if "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".find(val[i]) > -1:
            alphabetStr += val[i]
    return alphabetStr
def emptyString():
    return ""
def rangeValue(val:str, rangeVal:str):
    if isNumber(val):
        iVal = float(val)

        rvs = rangeVal.split("^")
        for i in range(len(rvs)):
            arr = rvs[i].split(":")

            start = float(arr[0]) if arr[0] != "" else 0
            end = float(arr[1]) if arr[1] != "" else 9999999

            if ( iVal >= start and iVal <= end):
                return arr[2]

    return ""
def betweenStr(val:str, startStr:str, endStr:str):
    sIdx = val.find(startStr)
    eIdx = val.rfind(endStr)

    if sIdx > -1 and eIdx > -1:
        return val[sIdx+1:eIdx]
    else:
        return val

# Logic Value 식을 가져와서 필드를 값으로 치환해서 구문을 넘겨준다.
# def get_logic_value(logic_value:str, df:pd.DataFrame, out_item_row, rowIdx=0):
#     while logic_value.find("{") > -1:
#         sPos = logic_value.find("{")
#         ePos = logic_value.find("}")
#         fieldStr = logic_value[sPos+1:ePos]
#         fn_note("fieldStr : " + fieldStr)
#         if fieldStr.startswith("Lcm Item Attr_Attr"):
#             logic_value = logic_value.replace("{" + fieldStr + "}", "'" + gfn_get_str(df_out_ItemAttbValue.loc[out_item_row, fieldStr]) + "'")
#         else:
#             if fn_isCodeField(fieldStr):
#                 logic_value = logic_value.replace("{" + fieldStr + "}", "'" + gfn_get_str(fn_getCodeData(fieldStr, df.loc[0, fieldStr[0:-5]], rowIdx)) + "'")
#             else:
#                 logic_value = logic_value.replace("{" + fieldStr + "}", "'" + gfn_get_str(df.loc[0, fieldStr]) + "'")
#
#         # log(logger.error, "logic_value : " + logic_value)
#     return logic_value
# def fn_getFirstCodeField(logic_value:str):
#     firstCodeFile = ""
#     if logic_value.find("{") > -1:
#         sPos = logic_value.find("{")
#         ePos = logic_value.find("}")
#         fieldStr = logic_value[sPos+1:ePos]
#
#         if fn_isCodeField(fieldStr):
#             firstCodeFile = fieldStr[0:-5]
#
#     return firstCodeFile
# def fn_isCodeField(fieldStr:str):
#     rightStr = fieldStr[-5:]
#     if ".GRP1.GRP2.GRP3.GRP4.NUM1.NUM2.NUM3.NUM4".find(rightStr) > -1:
#         return True
#     else:
#         return False
# def fn_getCodeData(fieldStr:str, codeValues, rowIdx):
#     rightStr = fieldStr[-4:]
#     codeInfo = {"GRP1" : 0, "GRP2" : 1, "GRP3" : 2, "GRP4" : 3, "NUM1" : 4, "NUM2" : 5, "NUM3" : 6, "NUM4" : 7}
#     if "".__eq__(gfn_get_str(codeValues)):
#         return ""
#     elif codeValues.find("^") > -1:
#         rowArr = codeValues.split("^")
#         row = rowArr[rowIdx]
#         colArr = row.split(",")
#         return colArr[codeInfo[rightStr]]
#     else:
#         colArr = codeValues.split(",")
#         return colArr[codeInfo[rightStr]]

def fn_getSingleQuotation(value:str):
    if value.startswith("'"):
        return value
    else:
        return "'" + value + "'"

def fn_chgCodeName(value:str):
    if value.endwith(".GRP1}"):
        value.replace(".GRP1}", "[0]")

def fn_concat(value1:str, value2:str):
    if value1 == np.nan or "".__eq__(value1):
        return value2
    else:
        return value1 + "," + value2

def fn_getCisValue(item:str, attbId:str):
    # log(logger.debug, "item : " + item + " , attbId : " + attbId)
    cisInfo = dict_cis.get(item)
    if cisInfo != None:
        cisAttbs = cisInfo.split("^")

        for i in range(len(cisAttbs)):
            cisAttb = cisAttbs[i].split("::")
            if ( attbId.__eq__(cisAttb[0]) ):
                # log(logger.debug, "cisAttb value : " + cisAttb[2])
                return cisAttb[1]

        return ""
    else:
        return ""

def fn_note(note:str):
    if "Y".__eq__(pDetailLogFlag):
        logger.Note(p_note=note, p_log_level=common.G_log_level.debug())

def fn_calcValue(valueStr, row):
    # 내장 함수 정의
    # def fn_getCisValue(item: str, cisId: str):
    #     cisInfo = (dict_cis.get(item))
    #     if cisInfo != None:
    #         cisAttbs = cisInfo.split("^")
    #
    #         for i in range(len(cisAttbs)):
    #             cisAttb = cisAttbs[i].split("::")
    #             if (cisId.__eq__(cisAttb[0])):
    #                 return cisAttb[1]
    #
    #         return ""
    #     else:
    #         return ""
    def subStr(val, sPos, ePos=0):
        try:
            if ePos == 0:
                ePos = len(val)

            return val[sPos:ePos]
        except Exception as e:
            logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    def length(val):
        return str(len(val))
    def nvl(val, replaceVal):
        if (val is None) | ("".__eq__(val)):
            return replaceVal
        else:
            return val
    def decode(val: str, compVal: str, falseVal: str):
        if compVal.find("^") > -1:
            compValArr = compVal.split("^")

            for i in range(len(compValArr)):
                compKey = compValArr[i].split(":")[0]
                compValue = compValArr[i].split(":")[1]
                idx = compKey.find("%")
                if idx == 0:
                    if val.endswith(compKey.replace("%", "")):
                        return compValue
                elif idx == len(compKey) - 1:
                    if val.startswith(compKey.replace("%", "")):
                        return compValue
                else:
                    if val.__eq__(compKey):
                        return compValue
        else:
            compKey = compVal.split(":")[0]
            compValue = compVal.split(":")[1]
            if val.__eq__(compKey):
                return compValue

        return falseVal
    def decodeOne(val: str, compVal: str, trueVal: str, falseVal: str):
        if val.__eq__(compVal):
            return trueVal
        else:
            return falseVal
    def split(val: str, splitStr: str, idx: int, otherIdx=0):
        arr = val.split(splitStr)
        if len(arr) > idx:
            return arr[idx]
        else:
            return arr[otherIdx]
    def numberSplit(val: str, idx: int):
        tVal = ""
        isNumber = False
        for i in range(len(val)):
            if "0123456789".find(val[i]) < 0:
                tVal += val[i]
                isNumber = False
            elif "0123456789".find(val[i]) > -1 and isNumber == False:
                tVal += " "
                isNumber = True

        arr = tVal.split(" ")
        if len(arr) > idx:
            return arr[idx]
        else:
            return ""
    def digit(val):
        digitStr = ""
        for i in range(len(val)):
            if "0123456789".find(val[i]) > -1:
                digitStr += val[i]
        return digitStr
    def alphabet(val):
        alphabetStr = ""
        for i in range(len(val)):
            if "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".find(val[i]) > -1:
                alphabetStr += val[i]
        return alphabetStr
    def emptyString():
        return ""
    def rangeValue(val: str, rangeVal: str):
        def isNumber(val: str, tempVal=""):
            try:
                num = float(val)
            except:
                return False
            return True

        if isNumber(val):
            iVal = float(val)

            rvs = rangeVal.split("^")
            for i in range(len(rvs)):
                arr = rvs[i].split(":")

                start = float(arr[0]) if arr[0] != "" else 0
                end = float(arr[1]) if arr[1] != "" else 9999999

                if (iVal >= start and iVal <= end):
                    return arr[2]

        return ""
    def betweenStr(val: str, startStr: str, endStr: str):
        sIdx = val.find(startStr)
        eIdx = val.rfind(endStr)

        if sIdx > -1 and eIdx > -1:
            return val[sIdx + 1:eIdx]
        else:
            return val
    def fn_isCodeField(fieldStr: str):
        rightStr = fieldStr[-5:]
        if ".GRP1.GRP2.GRP3.GRP4.NUM1.NUM2.NUM3.NUM4".find(rightStr) > -1:
            return True
        else:
            return False
    def fn_getCodeData(fieldStr: str, codeValues):
        # fn_note("fn_getCodeData = fieldStr : " + fieldStr + " , codeValues : " + codeValues)
        rightStr = fieldStr[-4:]
        codeInfo = {"GRP1": 0, "GRP2": 1, "GRP3": 2, "GRP4": 3, "NUM1": 4, "NUM2": 5, "NUM3": 6, "NUM4": 7}
        if "".__eq__(codeValues):
            # fn_note("fn_getCodeData = Here 1 ")
            return ""
        else:
            # fn_note("fn_getCodeData = Here 2 ")
            colArr = codeValues.split(",")
            return colArr[codeInfo[rightStr]]

    org_valueStr = valueStr
    while valueStr.find("{") > -1:
        sPos = valueStr.find("{")
        ePos = valueStr.find("}")
        fieldStr = valueStr[sPos + 1:ePos]
        fn_note("fn_calcValue = fieldStr : " + fieldStr)
        # fn_note("fn_calcValue = row[fieldStr] : " + row[fieldStr])
        if fn_isCodeField(fieldStr):
            # fn_note("fn_calcValue = Here 1 ")
            valueStr = valueStr.replace("{" + fieldStr + "}", "'" + gfn_get_str(fn_getCodeData(fieldStr, row[fieldStr[0:-5]])) + "'")
        else:
            # fn_note("fn_calcValue = Here 2 ")
            valueStr = valueStr.replace("{" + fieldStr + "}", "'" + gfn_get_str(row[fieldStr]) + "'")

    fn_note("fn_calcValue - valueStr convert : " + org_valueStr + " => " + valueStr)
    if "".__ne__(valueStr):
        return eval(valueStr)
    else:
        return valueStr

# 필드 값이면 {} 를 넣어준다.
def fn_field(valueStr):
    if "".__eq__(valueStr):
        return ""
    elif valueStr.find("{") < 0 and valueStr.find("(") < 0:
        return "{" + valueStr + "}"
    else:
        return valueStr

def fn_findAttrValue(row, mapRow, orgAttr, orgRule):
    # 내장 함수 정의
    def isLt(val: str, compVal: str):
        return val.__lt__(compVal)
    def isLe(val: str, compVal: str):
        return val.__le__(compVal)
    def isGt(val: str, compVal: str):
        return val.__gt__(compVal)
    def isGe(val: str, compVal: str):
        return val.__ge__(compVal)
    def isEq(val: str, compVal: str):
        return val.__eq__(compVal)
    def isNe(val: str, compVal: str):
        return val.__ne__(compVal)
    def isStartLike(val: str, compVal: str):
        return val.startswith(compVal)
    def isNotStartLike(val: str, compVal: str):
        return not val.startswith(compVal)
    def isEndLike(val: str, compVal: str):
        return val.endwith(compVal)
    def isFind(val: str, compVal: str):
        findIdx = val.find(compVal)
        if findIdx >= 0:
            return True
        else:
            return False
    def isNotFind(val: str, compVal: str):
        findIdx = val.find(compVal)
        if findIdx >= 0:
            return False
        else:
            return True
    def isNotNull(val: str, compVal: str):
        if val != np.nan and "".__ne__(val):
            return True
        else:
            return False
    def isNull(val: str, compVal: str):
        if val == np.nan or "".__eq__(val):
            return True
        else:
            return False
    def isIn(val: str, compVal: str):
        if ("^" + compVal + "^").find("^" + val + "^") > -1:
            return True
        else:
            return False
    def isNotIn(val: str, compVal: str):
        if ("^" + compVal + "^").find("^" + val + "^") > -1:
            return False
        else:
            return True
    def inStr(val, separator):
        return val.find(separator)
    def isInt(val: str, tempVal: str):
        return str.isdigit(val)
    def isNotInt(val: str, tempVal: str):
        return not str.isdigit(val)
    def isNumber(val: str, tempVal=""):
        try:
            num = float(val)
        except:
            return False
        return True
    def isNotInt(val: str, tempVal: str):
        return not str.isdigit(val)
    def isAlpha(val: str, tempVal: str):
        return str.isalpha(val)
    def isNotAlpha(val: str, tempVal: str):
        return not str.isalpha(val)
    def isIntBetween(val: str, sVal: str, eVal: str):
        try:
            if int(val) >= int(sVal) and int(val) <= int(eVal):
                return True
            else:
                return False
        except Exception as e:
            logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())

    ruleNo = mapRow["Lcm Item Attr Map_RuleNo"]
    attrNo = mapRow["Attr No.[Attr No]"]

    attrRuleNo = ""
    attrValue = ""
    attrValid = gfn_get_str(row["Lcm Item Attr_Valid"])

    try:
        # 조건 판단
        field1 = gfn_get_str(mapRow["Lcm Item Attr Map_Field01"])
        condi1 = gfn_get_str(mapRow["Lcm Item Attr Map_Condition01"])
        value1 = gfn_get_str(mapRow["Lcm Item Attr Map_Value01"])
        field2 = gfn_get_str(mapRow["Lcm Item Attr Map_Field02"])
        condi2 = gfn_get_str(mapRow["Lcm Item Attr Map_Condition02"])
        value2 = gfn_get_str(mapRow["Lcm Item Attr Map_Value02"])
        field3 = gfn_get_str(mapRow["Lcm Item Attr Map_Field03"])
        condi3 = gfn_get_str(mapRow["Lcm Item Attr Map_Condition03"])
        value3 = gfn_get_str(mapRow["Lcm Item Attr Map_Value03"])
        field4 = gfn_get_str(mapRow["Lcm Item Attr Map_Field04"])
        condi4 = gfn_get_str(mapRow["Lcm Item Attr Map_Condition04"])
        value4 = gfn_get_str(mapRow["Lcm Item Attr Map_Value04"])
        field5 = gfn_get_str(mapRow["Lcm Item Attr Map_Field05"])
        condi5 = gfn_get_str(mapRow["Lcm Item Attr Map_Condition05"])
        value5 = gfn_get_str(mapRow["Lcm Item Attr Map_Value05"])

        # 필드값을 Bind 후의 값을 구한다.
        field1_value = fn_calcValue(fn_field(field1), row)
        field2_value = fn_calcValue(fn_field(field2), row)
        field3_value = fn_calcValue(fn_field(field3), row)
        field4_value = fn_calcValue(fn_field(field4), row)
        field5_value = fn_calcValue(fn_field(field5), row)
        fn_note("fn_findAttrValue - field_value : " + field1_value + " , " + field2_value + " , " + field3_value + " , " + field4_value + " , " + field5_value)

        if "".__eq__(field1):
            field1_value = ""
            condi1 = "isEq"
            value1 = ""
        if "".__eq__(field2):
            field2_value = ""
            condi2 = "isEq"
            value2 = ""
        if "".__eq__(field3):
            field3_value = ""
            condi3 = "isEq"
            value3 = ""
        if "".__eq__(field4):
            field4_value = ""
            condi4 = "isEq"
            value4 = ""
        if "".__eq__(field5):
            field5_value = ""
            condi5 = "isEq"
            value5 = ""

        fn_note("fn_findAttrValue - Condition = " + field1_value + " / " + condi1 + " / " + value1 + " , " +
                field2_value + " / " + condi2 + " / " + value2 + " , " +
                field3_value + " / " + condi3 + " / " + value3 + " , " +
                field4_value + " / " + condi4 + " / " + value4 + " , " +
                field5_value + " / " + condi5 + " / " + value5)

        if (eval(condi1 + "(" + fn_getSingleQuotation(field1_value) + "," + fn_getSingleQuotation(value1) + ")") and
                eval(condi2 + "(" + fn_getSingleQuotation(field2_value) + "," + fn_getSingleQuotation(value2) + ")") and
                eval(condi3 + "(" + fn_getSingleQuotation(field3_value) + "," + fn_getSingleQuotation(value3) + ")") and
                eval(condi4 + "(" + fn_getSingleQuotation(field4_value) + "," + fn_getSingleQuotation(value4) + ")") and
                eval(condi5 + "(" + fn_getSingleQuotation(field5_value) + "," + fn_getSingleQuotation(value5) + ")")):
            fn_note("fn_findAttrValue - Condition Yes")

            if "".__eq__(gfn_get_str(mapRow["Lcm Item Attr Map_CIS Attr Id"])):
                # Cis 정보가 없으면
                if (not gfn_isnull(mapRow["Lcm Item Attr Map_Fix"])):
                    # Fix 값이 있으면
                    fn_note("fn_findAttrValue - Condition Yes - Fix")
                    attrValue = mapRow["Lcm Item Attr Map_Fix"]
                else:
                    # Logic 값이 있으면
                    fn_note("fn_findAttrValue - Condition Yes - Logic")
                    logic = gfn_get_str(mapRow["Lcm Item Attr Map_Logic"])
                    if ("".__ne__(logic)):
                        attrValue = fn_calcValue(logic, row)
            else:
                # Cis 정보가 있으면
                fn_note("fn_findAttrValue - Condition Yes - Cis")
                attrValue = fn_getCisValue(row["Item.[Item]"], gfn_get_str(mapRow["Lcm Item Attr Map_CIS Attr Id"]))

                # Logic 가 있으면
                logic_value = gfn_get_str(mapRow["Lcm Item Attr Map_Logic"])
                if "".__ne__(logic_value):
                    logic_value = logic_value.replace("{CIS Value}", "'" + attrValue + "'")
                    attrValue = fn_calcValue(logic_value, row)
            if "".__ne__(attrValue):
                attrRuleNo = fn_concat(orgRule, ruleNo)
        else:
            attrRuleNo = orgRule
            attrValue = orgAttr
    except Exception as e:
        attrValue = "# Error #"
        attrRuleNo = ruleNo + " => " + traceback.format_exc()
        if "-".__eq__(attrValid):
            attrValid = attrRuleNo
        else:
            attrValid = fn_concat(attrValid, attrRuleNo)

        print(traceback.format_exc())

    fn_note("fn_findAttrValue - return : " + " attrValue : "  + str(attrValue) + " , attrRuleNo : "  + attrRuleNo)

    return [attrValue, attrRuleNo, attrValid]
########################################################################################################################
# Main Logic
########################################################################################################################

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if is_local:
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_item.csv", encoding="UTF-8")
        df_in_attrMap = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_attrMap.csv", encoding="UTF-8")
        df_in_itemCis = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemCis.csv", encoding="UTF-8")
        df_in_itemEtc = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemEtc.csv", encoding="UTF-8")
        df_in_itemRef = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemRef.csv", encoding="UTF-8")
        df_in_itemAttr = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemAttr.csv", encoding="UTF-8")
        df_in_org = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_org.csv", encoding="UTF-8")

        pDetailLogFlag = "N"
        outVersionName = "CWV_MP"

    # df 춮력
    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_attrMap, "df_in_attrMap", True)
    vdCommon.gfn_saveDf(df_in_itemCis, "df_in_itemCis", True)
    vdCommon.gfn_saveDf(df_in_itemEtc, "df_in_itemEtc", True)
    vdCommon.gfn_saveDf(df_in_itemRef, "df_in_itemRef", True)
    vdCommon.gfn_saveDf(df_in_itemAttr, "df_in_itemAttr", True)
    vdCommon.gfn_saveDf(df_in_org, "df_in_org", True)

    dict_cis = {}
    for cis_row in df_in_itemCis.index:
        dict_cis[df_in_itemCis.loc[cis_row, "Item.[Item]"]] = df_in_itemCis.loc[cis_row, "Lcm Item CIS Attr_Attr_Values"]
    logger.Step(p_step_desc='Cis Dict 생성')

    df_in_item["Version.[Version Name]"] = outVersionName

    # 타입 변경
    df_in_attrMap = df_in_attrMap.astype({"Lcm Item Attr Map_Field01" : 'object', "Lcm Item Attr Map_Condition01": 'object', "Lcm Item Attr Map_Value01": 'object',
        "Lcm Item Attr Map_Field02" : 'object', "Lcm Item Attr Map_Condition02": 'object', "Lcm Item Attr Map_Value02": 'object',
        "Lcm Item Attr Map_Field03" : 'object', "Lcm Item Attr Map_Condition03": 'object', "Lcm Item Attr Map_Value03": 'object',
        "Lcm Item Attr Map_Field04" : 'object', "Lcm Item Attr Map_Condition04": 'object', "Lcm Item Attr Map_Value04": 'object',
        "Lcm Item Attr Map_Field05" : 'object', "Lcm Item Attr Map_Condition05": 'object', "Lcm Item Attr Map_Value05": 'object',
        "Lcm Item Attr Map_Rule Seq" : "int", "Lcm Item Attr Map_Fix" : "object" }, errors='ignore', copy=True)

    # 처음 데이타가 없을 경우 float로 나오는 문제 발생
    df_in_attrMap["Lcm Item Attr Map_Fix"].fillna(value="", inplace=True)
    df_in_attrMap["Lcm Item Attr Map_CIS Attr Id"].fillna(value="", inplace=True)
    for idx in range(5):
        df_in_attrMap["Lcm Item Attr Map_Field" + gfn_lpad(idx + 1, 2)].fillna(value="", inplace=True)
        df_in_attrMap["Lcm Item Attr Map_Condition" + gfn_lpad(idx + 1, 2)].fillna(value="", inplace=True)
        df_in_attrMap["Lcm Item Attr Map_Value" + gfn_lpad(idx + 1, 2)].fillna(value="", inplace=True)

    # 전체 데이타 Merge
    df_in_item["Version.[Version Name]"] = outVersionName
    df_in_item = df_in_item.merge(df_in_itemCis, how='left', on=["Version.[Version Name]", "Item.[Item]"])
    df_in_item = df_in_item.merge(df_in_itemRef, how='left', on=["Version.[Version Name]", "Item.[Item]"])
    df_in_item = df_in_item.merge(df_in_itemEtc, how='left', on=["Version.[Version Name]", "Item.[Item]"])
    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)

    for idx in range(15):
        df_in_item["Lcm Item Attr_Attr" + gfn_lpad(idx + 1, 2)] = ""
        df_in_item["Lcm Item Attr_RuleNo" + gfn_lpad(idx + 1, 2)] = ""
    df_in_item["Lcm Item Attr_Valid"] = "-"

    # Product_Attr No 로 Map 구성
    dict_AttbName = {}
    for idx in df_in_itemAttr.index:
        dict_AttbName[df_in_itemAttr.loc[idx, "Product.[Product]"] + "_" + df_in_itemAttr.loc[idx, "Attr No.[Attr No]"]] = "Lcm Item Attr_" + df_in_itemAttr.loc[idx, "Lcm Prod Attr_Attr Name"]

    # Attr 이름만 구해서 필드 생성
    df_AttrName = df_in_itemAttr[["Lcm Prod Attr_Attr Name"]].copy()
    df_AttrName = df_AttrName.drop_duplicates()
    vdCommon.gfn_saveDf(df_AttrName, "df_AttrName", True)
    for idx in df_AttrName.index:
        if "-".__ne__(df_AttrName.loc[idx, "Lcm Prod Attr_Attr Name"]):
            df_in_item["Lcm Item Attr_" + df_AttrName.loc[idx, "Lcm Prod Attr_Attr Name"]] = "-"

    # df_in_attrMap 에서 의미없는 데이타 제거
    df_in_attrMap = df_in_attrMap.loc[(df_in_attrMap["Lcm Item Attr Map_Rule Seq"] > 0)].copy()

    df_in_attrMap = df_in_attrMap.sort_values(by=["Item.[Class Category]", "Lcm Item Attr Map_Rule Seq", "Attr No.[Attr No]"], ascending=[True, True, True])
    df_in_attrMap.reset_index(inplace=True)
    vdCommon.gfn_saveDf(df_in_attrMap, "df_in_attrMap", True)

    # Class Category 를 가져온다.
    df_classCategory = df_in_attrMap[["Item.[Class Category]", "Product.[Product]"]].copy()
    df_classCategory = df_classCategory.drop_duplicates()

    df_result_item = pd.DataFrame

    # Class Category 별로 For 를 돌린다.
    for idx in df_classCategory.index:
        product = df_classCategory.loc[idx, "Product.[Product]"]
        classCategory = df_classCategory.loc[idx, "Item.[Class Category]"]
        vdCommon.gfn_stepLog("For 1 : " + "product = " + product + " , Class Category = " + classCategory)

        df_work_attrMap = df_in_attrMap[((df_in_attrMap["Product.[Product]"] == product) & (df_in_attrMap["Item.[Class Category]"] == classCategory))].copy()
        df_work_item = df_in_item[((df_in_item["Item.[Product]"] == product) & (df_in_item["Item.[Class Category]"] == classCategory))].copy()

        vdCommon.gfn_saveDf(df_work_attrMap, "df_work_attrMap", True)
        vdCommon.gfn_saveDf(df_work_item, "df_work_item", True)

        if df_work_item.shape[0] == 0:
            vdCommon.gfn_stepLog("Item Count is 0")
            continue

        for idx2 in df_work_attrMap.index:
            vdCommon.gfn_stepLog("For 2 : " + "RuleNo = " + str(df_work_attrMap.loc[idx2, "Lcm Item Attr Map_RuleNo"]))

            curAttbNo = gfn_get_str(df_work_attrMap.loc[idx2, "Attr No.[Attr No]"])
            attb_no = curAttbNo[-2:]

            attrNo = "Lcm Item Attr_Attr" + attb_no
            ruleNo = "Lcm Item Attr_RuleNo" + attb_no
            df_work_item[[attrNo, ruleNo, "Lcm Item Attr_Valid"]] = df_work_item.apply(lambda row: fn_findAttrValue(row, df_work_attrMap.loc[idx2], row[attrNo], row[ruleNo]), axis=1, result_type='expand')

            # vdCommon.gfn_saveDf(df_work_item, "df_work_item rule", True)

        # 데이타가 없으면 - 으로 세팅
        for idx in range(15):
            attb_no = gfn_lpad(str(idx + 1), 2)

            df_work_item["Lcm Item Attr_Attr" + attb_no] = df_work_item.apply(lambda row : row["Lcm Item Attr_Attr" + attb_no] if "".__ne__(row["Lcm Item Attr_Attr" + attb_no]) else "-", axis=1)

        vdCommon.gfn_saveDf(df_work_item, "df_work_item middle result", True)

        # Item A1 ~ A15를 각 속성(35) 컬럼에 넣어준다.
        for idx in range(15):
            attb_no = gfn_lpad(str(idx + 1), 2)
            dict_key = product + "_ATTB" + gfn_lpad(str(idx + 1), 2)
            if dict_AttbName.get(dict_key) != None:
                df_work_item[dict_AttbName.get(dict_key)] = df_work_item["Lcm Item Attr_Attr" + attb_no]

        vdCommon.gfn_saveDf(df_work_item, "df_work_item result", True)

        if df_result_item.empty:
            df_result_item = df_work_item.copy()
        else:
            df_result_item = pd.concat([df_result_item, df_work_item])

    vdCommon.gfn_saveDf(df_result_item, 'df_result_item', True)

    # 기존값과 차이가 있는 데이타만 가져온다.
    df_in_org.rename(columns={"Lcm Item Attr_Attr01": "Org_Lcm Item Attr_Attr01",
                                  "Lcm Item Attr_Attr02": "Org_Lcm Item Attr_Attr02",
                                  "Lcm Item Attr_Attr03": "Org_Lcm Item Attr_Attr03",
                                  "Lcm Item Attr_Attr04": "Org_Lcm Item Attr_Attr04",
                                  "Lcm Item Attr_Attr05": "Org_Lcm Item Attr_Attr05",
                                  "Lcm Item Attr_Attr06": "Org_Lcm Item Attr_Attr06",
                                  "Lcm Item Attr_Attr07": "Org_Lcm Item Attr_Attr07",
                                  "Lcm Item Attr_Attr08": "Org_Lcm Item Attr_Attr08",
                                  "Lcm Item Attr_Attr09": "Org_Lcm Item Attr_Attr09",
                                  "Lcm Item Attr_Attr10": "Org_Lcm Item Attr_Attr10",
                                  "Lcm Item Attr_Attr11": "Org_Lcm Item Attr_Attr11",
                                  "Lcm Item Attr_Attr12": "Org_Lcm Item Attr_Attr12",
                                  "Lcm Item Attr_Attr13": "Org_Lcm Item Attr_Attr13",
                                  "Lcm Item Attr_Attr14": "Org_Lcm Item Attr_Attr14",
                                  "Lcm Item Attr_Attr15": "Org_Lcm Item Attr_Attr15"}, inplace=True)
    df_result_item["Lcm Item Attr_Flag Diff"] = "N"
    df_result_item = df_result_item.merge(df_in_org, how='left', on=["Version.[Version Name]", "Item.[Item]"])
    df_result_item.loc[((df_result_item["Lcm Item Attr_Attr01"] != df_result_item["Org_Lcm Item Attr_Attr01"]) |
                        (df_result_item["Lcm Item Attr_Attr02"] != df_result_item["Org_Lcm Item Attr_Attr02"]) |
                        (df_result_item["Lcm Item Attr_Attr03"] != df_result_item["Org_Lcm Item Attr_Attr03"]) |
                        (df_result_item["Lcm Item Attr_Attr04"] != df_result_item["Org_Lcm Item Attr_Attr04"]) |
                        (df_result_item["Lcm Item Attr_Attr05"] != df_result_item["Org_Lcm Item Attr_Attr05"]) |
                        (df_result_item["Lcm Item Attr_Attr06"] != df_result_item["Org_Lcm Item Attr_Attr06"]) |
                        (df_result_item["Lcm Item Attr_Attr07"] != df_result_item["Org_Lcm Item Attr_Attr07"]) |
                        (df_result_item["Lcm Item Attr_Attr08"] != df_result_item["Org_Lcm Item Attr_Attr08"]) |
                        (df_result_item["Lcm Item Attr_Attr09"] != df_result_item["Org_Lcm Item Attr_Attr09"]) |
                        (df_result_item["Lcm Item Attr_Attr10"] != df_result_item["Org_Lcm Item Attr_Attr10"]) |
                        (df_result_item["Lcm Item Attr_Attr11"] != df_result_item["Org_Lcm Item Attr_Attr11"]) |
                        (df_result_item["Lcm Item Attr_Attr12"] != df_result_item["Org_Lcm Item Attr_Attr12"]) |
                        (df_result_item["Lcm Item Attr_Attr13"] != df_result_item["Org_Lcm Item Attr_Attr13"]) |
                        (df_result_item["Lcm Item Attr_Attr14"] != df_result_item["Org_Lcm Item Attr_Attr14"]) |
                        (df_result_item["Lcm Item Attr_Attr15"] != df_result_item["Org_Lcm Item Attr_Attr15"])), "Lcm Item Attr_Flag Diff"] = "Y"
    df_result_item = df_result_item.loc[(df_result_item["Lcm Item Attr_Flag Diff"] == "Y")].copy()
    vdCommon.gfn_saveDf(df_result_item, 'df_result_item Org Diff', True)

    # copy 할 Measure 세팅
    fields = []
    fields.append("Version.[Version Name]")
    fields.append("Item.[Item]")
    for idx in range(15):
        fields.append("Lcm Item Attr_Attr" + gfn_lpad(idx + 1, 2))
        fields.append("Lcm Item Attr_RuleNo" + gfn_lpad(idx + 1, 2))
    fields.append("Lcm Item Attr_Valid")
    fields.append("Lcm Item Attr_Flag Diff")
    for idx in df_AttrName.index:
        if "-".__ne__(df_AttrName.loc[idx, "Lcm Prod Attr_Attr Name"]):
            fields.append("Lcm Item Attr_" + df_AttrName.loc[idx, "Lcm Prod Attr_Attr Name"])

    # out 생성
    df_out = df_result_item[fields].astype(
        {"Lcm Item Attr_Attr01": 'str', "Lcm Item Attr_Attr02": 'str', "Lcm Item Attr_Attr03": 'str',
         "Lcm Item Attr_Attr04": 'str', "Lcm Item Attr_Attr05": 'str', "Lcm Item Attr_Attr06": 'str',
         "Lcm Item Attr_Attr07": 'str', "Lcm Item Attr_Attr08": 'str', "Lcm Item Attr_Attr09": 'str',
         "Lcm Item Attr_Attr10": 'str', "Lcm Item Attr_Attr11": 'str', "Lcm Item Attr_Attr12": 'str',
         "Lcm Item Attr_Attr13": 'str', "Lcm Item Attr_Attr14": 'str', "Lcm Item Attr_Attr15": 'str', }, copy=True)

    df_out["Lcm Item Attr_Asn"] = 1

    vdCommon.gfn_saveDf(df_out, 'df_out', True)

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

