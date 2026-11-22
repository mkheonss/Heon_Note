"""
df_in_item : Select ([Item].[Item] ) on row,() on column;
df_in_itemMaterial : Select ([Item Material].[Item Material] * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3] * [Item Material].[MSL4] * [Item Material].[MSL5] * [Item Material].[C01] * [Item Material].[C02] * [Item Material].[C03] * [Item Material].[C04] * [Item Material].[C05] * [Item Material].[C06] * [Item Material].[C07] * [Item Material].[C08] * [Item Material].[C09] * [Item Material].[C10] * [Item Material].[S01] * [Item Material].[S02] * [Item Material].[S03] * [Item Material].[S04] * [Item Material].[S05] * [Item Material].[S06] * [Item Material].[S07] * [Item Material].[S08] * [Item Material].[S09] * [Item Material].[S10] * [Item Material].[S11] * [Item Material].[S12] * [Item Material].[S13] * [Item Material].[S14] * [Item Material].[S15] ) on row,() on column;
df_in_itemMaterialSpec : Select ([Item Material].[Item Material] ) on row,({Measure.[Item Material Spec_CIS Attr Values], Measure.[Item Material Spec_GSCM Attr Values], Measure.[Item Material Spec_Long Desc], Measure.[Item Material Spec_Mtrl Desc], Measure.[Item Material Spec_Mtrl Group], Measure.[Item Material Spec_Mtrl Type], Measure.[Item Material Spec_Mtrl Group Desc], Measure.[Item Material Spec_UOM], Measure.[Item Material Spec_Creation Time], Measure.[Item Material Spec_Update Time] }) on column where { [Version].[Version Name] };
//df_in_c1 : Select ([Item Material].[Item Material] * [Global Top].[GT Code] ) on row, ({Measure.[Vendor Mtrl_GT Name]}) on column where { [Version].[Version Name], [Item Material].[MSL3].filter(#.Name contains "SMPS"), Measure.[Vendor Mtrl_Quota] != 0, Measure.[Vendor Mtrl_GT Name] != "SAMSUNG ELECTRONICS", coalesce(Measure.[Vendor Mtrl_Valid Flag], "N") =="Y" };
df_in_c1 : Select ([Item Material].[Item Material] * [Global Top].[GT Code] ) on row, ({Measure.[Vendor Mtrl_GT Name]}) on column where { [Version].[Version Name], /*[Item Material].[MSL3].filter(#.Name contains "SMPS"),*/ Measure.[Vendor Mtrl_Quota] != 0, Measure.[Vendor Mtrl_GT Name] != "SAMSUNG ELECTRONICS", coalesce(Measure.[Vendor Mtrl_Valid Flag], "N") =="Y" };
df_in_c2 : Select ([Item Material].[Item Material] ) on row, ({Measure.[Item Material Spec Plant_Purchaser ID]}) on column where { [Version].[Version Name], [Location].[Location]} ;
df_in_c3 : select ([Item Material].[Item Material]) on row, ({Measure.[Item Material PLC Status]})on column where { [Version].[Version Name] };
df_in_gtCode : Select ([Global Top].[GT Code] ) on row, ({Measure.[GT Code Map_CIS00494]}) on column where { [Version].[Version Name] };
df_in_gtCodeName : Select ([Global Top].[GT Code] ) on row, ({Measure.[GT_Fix Name]}) on column where { [Version].[Version Name] };
df_in_itemMaterialAttrMap : Select ([Sequence].[Sequence] * [Attr No].[Attr No] * [Hrcy Level Data].[Hrcy Level] * [Hrcy Level Data].[Hrcy Level Data] ) on row, ({Measure.[Item Material Attr Map_CIS Attr ID], Measure.[Item Material Attr Map_Condition01], Measure.[Item Material Attr Map_Condition02], Measure.[Item Material Attr Map_Condition03], Measure.[Item Material Attr Map_Field01], Measure.[Item Material Attr Map_Field02], Measure.[Item Material Attr Map_Field03], Measure.[Item Material Attr Map_Fix], Measure.[Item Material Attr Map_Logic], Measure.[Item Material Attr Map_Rule Seq], Measure.[Item Material Attr Map_RuleNo], Measure.[Item Material Attr Map_Value01], Measure.[Item Material Attr Map_Value02], Measure.[Item Material Attr Map_Value03]}) on column where { [Version].[Version Name] };
df_in_hrchy : Select ([Rule].[Rule No] * [Hrcy Type].[Hrcy Type].[Mtrl Standard] ) on row, ({Measure.[Mtrl Hrchy_Attb Make Level], Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L1 Order], Measure.[Mtrl Hrchy_L1 Rule], Measure.[Mtrl Hrchy_L1 Type], Measure.[Mtrl Hrchy_L2 Name], Measure.[Mtrl Hrchy_L2 Order], Measure.[Mtrl Hrchy_L2 Rule], Measure.[Mtrl Hrchy_L2 Type], Measure.[Mtrl Hrchy_L3 Name], Measure.[Mtrl Hrchy_L3 Order], Measure.[Mtrl Hrchy_L3 Rule], Measure.[Mtrl Hrchy_L3 Type], Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L4 Order], Measure.[Mtrl Hrchy_L4 Rule], Measure.[Mtrl Hrchy_L4 Type], Measure.[Mtrl Hrchy_L5 Name], Measure.[Mtrl Hrchy_L5 Order], Measure.[Mtrl Hrchy_L5 Rule], Measure.[Mtrl Hrchy_L5 Type], Measure.[Mtrl Hrchy_L1 Display], Measure.[Mtrl Hrchy_L2 Display], Measure.[Mtrl Hrchy_L3 Display], Measure.[Mtrl Hrchy_L4 Display], Measure.[Mtrl Hrchy_L5 Display], Measure.[Mtrl Hrchy_L1 Key Material Group Flag], Measure.[Mtrl Hrchy_L2 Key Material Group Flag], Measure.[Mtrl Hrchy_L3 Key Material Group Flag], Measure.[Mtrl Hrchy_L4 Key Material Group Flag], Measure.[Mtrl Hrchy_L5 Key Material Group Flag], Measure.[Mtrl Hrchy_Plan Group], Measure.[Mtrl Hrchy_SCM Material]}) on column where { [Version].[Version Name], coalesce(Measure.[Mtrl Hrchy_Validation], "") == "", coalesce(Measure.[Mtrl Hrchy_Delete Flag], "N") != "Y"};
df_in_rule : Select ([Rule].[Rule No] * [Group].[Group ID] * [Hrcy Type].[Hrcy Type] ) on row, ({Measure.[Mtrl Hrchy Map Rule_Code], Measure.[Mtrl Hrchy Map Rule_Desc], Measure.[Mtrl Hrchy Map Rule_Long Desc], Measure.[Mtrl Hrchy Map Rule_Grp], Measure.[Mtrl Hrchy Map Rule_Priority]}) on column where { [Version].[Version Name] };
df_in_constType : Select ([Item].[Item] * [Item].[Const Type]) on row,() on column;
df_in_location : select ([Location].[Location])  on row, () on column include memberproperties {[Location].[Location], [DisplayName]};
df_in_itemMaterialOvr : Select ([Item Material].[Item Material] ) on row,({Measure.[Item Material_MSL1_Ovr], Measure.[Item Material_MSL2_Ovr], Measure.[Item Material_MSL3_Ovr], Measure.[Item Material_MSL4_Ovr], Measure.[Item Material_MSL5_Ovr], Measure.[Item Material_C01_Ovr], Measure.[Item Material_C02_Ovr], Measure.[Item Material_C03_Ovr], Measure.[Item Material_C04_Ovr], Measure.[Item Material_C05_Ovr], Measure.[Item Material_C06_Ovr], Measure.[Item Material_C07_Ovr], Measure.[Item Material_C08_Ovr], Measure.[Item Material_C09_Ovr], Measure.[Item Material_C10_Ovr], Measure.[Item Material_S01_Ovr], Measure.[Item Material_S02_Ovr], Measure.[Item Material_S03_Ovr], Measure.[Item Material_S04_Ovr], Measure.[Item Material_S05_Ovr], Measure.[Item Material_S06_Ovr], Measure.[Item Material_S07_Ovr], Measure.[Item Material_S08_Ovr], Measure.[Item Material_S09_Ovr], Measure.[Item Material_S10_Ovr], Measure.[Item Material_S11_Ovr], Measure.[Item Material_S12_Ovr], Measure.[Item Material_S13_Ovr], Measure.[Item Material_S14_Ovr], Measure.[Item Material_S15_Ovr], Measure.[Item Material_C01_Ovr.lock], Measure.[Item Material_C02_Ovr.lock], Measure.[Item Material_C03_Ovr.lock], Measure.[Item Material_C04_Ovr.lock], Measure.[Item Material_C05_Ovr.lock], Measure.[Item Material_C06_Ovr.lock], Measure.[Item Material_C07_Ovr.lock], Measure.[Item Material_C08_Ovr.lock], Measure.[Item Material_C09_Ovr.lock], Measure.[Item Material_C10_Ovr.lock], Measure.[Item Material_S01_Ovr.lock], Measure.[Item Material_S02_Ovr.lock], Measure.[Item Material_S03_Ovr.lock], Measure.[Item Material_S04_Ovr.lock], Measure.[Item Material_S05_Ovr.lock], Measure.[Item Material_S06_Ovr.lock], Measure.[Item Material_S07_Ovr.lock], Measure.[Item Material_S08_Ovr.lock], Measure.[Item Material_S09_Ovr.lock], Measure.[Item Material_S10_Ovr.lock], Measure.[Item Material_S11_Ovr.lock], Measure.[Item Material_S12_Ovr.lock], Measure.[Item Material_S13_Ovr.lock], Measure.[Item Material_S14_Ovr.lock], Measure.[Item Material_S15_Ovr.lock]}) on column where { [Version].[Version Name] };
df_in_itemMaterialOrg : Select ([Item Material].[Item Material] ) on row, ({Measure.[Item Material_MSL1_Apply], Measure.[Item Material_MSL2_Apply], Measure.[Item Material_MSL3_Apply], Measure.[Item Material_MSL4_Apply], Measure.[Item Material_MSL5_Apply], Measure.[Item Material_C01_Apply], Measure.[Item Material_C02_Apply], Measure.[Item Material_C03_Apply], Measure.[Item Material_C04_Apply], Measure.[Item Material_C05_Apply], Measure.[Item Material_C06_Apply], Measure.[Item Material_C07_Apply], Measure.[Item Material_C08_Apply], Measure.[Item Material_C09_Apply], Measure.[Item Material_C10_Apply], Measure.[Item Material_S01_Apply], Measure.[Item Material_S02_Apply], Measure.[Item Material_S03_Apply], Measure.[Item Material_S04_Apply], Measure.[Item Material_S05_Apply], Measure.[Item Material_S06_Apply], Measure.[Item Material_S07_Apply], Measure.[Item Material_S08_Apply], Measure.[Item Material_S09_Apply], Measure.[Item Material_S10_Apply], Measure.[Item Material_S11_Apply], Measure.[Item Material_S12_Apply], Measure.[Item Material_S13_Apply], Measure.[Item Material_S14_Apply], Measure.[Item Material_S15_Apply], Measure.[Item Material_Const Type]}) on column where { [Version].[Version Name] };
df_in_itemMaterialRefOrg : Select ([Item Material].[Item Material] ) on row, ({Measure.[Item Material Ref_HQ Purchaser], Measure.[Item Material Ref_Key Material], Measure.[Item Material Ref_PLC Status], Measure.[Item Material Ref_Unit], Measure.[Item Material Ref_Vendor(HQ)], Measure.[Item Material Ref_Class Category], Measure.[Item Material Ref_Plan Group] }) on column where {[Version].[Version Name]};
df_in_day : select (&AllDays.Filter(#.Key == &CurrentDay.element(0).LeadOffset(-7).Key));

- MSL 데이타 초기화
scope:([Version].[Version Name].[CWV_MP]);
Measure.[Item Material_MSL1_Ovr] = "";
Measure.[Item Material_MSL2_Ovr] = "";
Measure.[Item Material_MSL3_Ovr] = "";
Measure.[Item Material_MSL4_Ovr] = "";
Measure.[Item Material_MSL5_Ovr] = "";
end scope;

EXEC plugin instance [PY_UI_ItemMaterialAttr]
for measures {[Item Material_MSL1]}
using scope ( &CWVUI  * [Hrcy Type].[Hrcy Type].[Mtrl Standard]
    * [Item Material].[Item Material].[BN96-62917A]
    * [Item Material].[MSL1].[Elec.]
 ) using arguments {(RunID, "Run_1"), (pDetailLogFlag, "N"), (outVersionName, "CWV_MP"), (pAll, "N"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

exec procedure PR_Job_ItemMaterialAttr;

createmember( [Python Batch].[Python Name]={,"PY_UI_ItemMaterialAttr"} );


* 2025.08.01 : 3개 프로시져를 한나로 만듬
    - Rule 적용 - MSL1 ~ MSL5 까지 찾음
    - Ref 적용
    - LV 가 있는 애들만 Mapping 적용 LV1  ~ LV3 까지 적용
    - LV 가 Panel 인 애들만 MSL 다시 적용
    - Ref C5 적용
    - common mapping 적용
* 2025.09.01 : Spec 조건 변경
    Measure.[Item Material Spec_Create Target Flag] == 1
        => Measure.[Item Material Spec_Creation Time] >= DATEADD(Now(),-7,"Day") || Measure.[Item Material Spec_Update Time] >= DATEADD(Now(),-7,"Day")
* 2025.09.02
    Spec 조건 변경으로 데이타 없을 경우에 대한 처리 추가
    MSL1 ~ MSL5 의 View Flag 세팅로직 제거
* 2025.12.24
    pAll 조건을 추가해서
        Measure.[Item Material Spec_Creation Time] >= DATEADD(Now(),-7,"Day") || Measure.[Item Material Spec_Update Time] >= DATEADD(Now(),-7,"Day")
        조건을 사용할지 안할지는 정한다.
* 2025.12.26
    Category 로직 추가
* 2025.12.30
    fn_getCisValue 함수에서  dict_cis 를 사용해서 속성을 찾도록 수정
* 2026.01.14
    Represent Vendor의 Display 업데이트를 위한 데이타 만드는거 삭제
* 26.01.30
    fn_c1 에서 코드 외 이름도 넘기도록 수정
* 26.04.01
    fn_convertRegFormat 에서 정규식 변환을 하는데 중간 결과값을 넘기면서 포함으로만 비교가 되고 있었음. patternVal -> pResult 로 변경

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
str_instance = 'PY_UI_ItemMaterialAttr'

class NoData(Exception):
    pass

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 함수 정의
########################################################################################################################
def fn_get_str(val):
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

def fn_nvl(val1:str, val2:str):
    if "" == val1 or pd.isna(val1) :
        return val2
    else:
        return val1

"""입력된 숫자 또는 문자열 왼쪽에 fillchar 문자로 패딩"""
def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)

def fn_getSingleQuotation(value:str):
    if value.startswith("'"):
        return value
    else:
        return "'" + value + "'"

def fn_note(note:str):
    if "Y" == pDetailLogFlag:
        logger.Note(p_note=note, p_log_level=common.G_log_level.debug())

def fn_concat(value1:str, value2:str):
    if value1 == np.nan or "" == value1:
        return value2
    else:
        return value1 + "," + value2

def fn_getCisValue(item: str, cisId: str):
    cisInfo = (dict_cis.get(item))
    if cisInfo != None:
        cisAttbs = cisInfo.split("^")

        for i in range(len(cisAttbs)):
            cisAttb = cisAttbs[i].split("::")
            if (cisId == cisAttb[0]):
                return cisAttb[1]

    return ""

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

def fn_calcValue(valueStr, row):
    # 내장 함수 정의
    def fn_getCisValue(item: str, cisId: str):
        cisInfo = (dict_cis.get(item))
        if cisInfo != None:
            cisAttbs = cisInfo.split("^")

            for i in range(len(cisAttbs)):
                cisAttb = cisAttbs[i].split("::")
                if (cisId.__eq__(cisAttb[0])):
                    return cisAttb[1]

            return ""
        else:
            return ""

    def fn_getCisValueForAttb4(item: str):
        x = fn_getCisValue(item, "C_02277")
        y = fn_getCisValue(item, "C_03974")

        if x != "" and y != "":
            return str(int(float(x)) * int(float(y)))
        else:
            return ""

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

    if "" == valueStr:
        return ""
    else:
        org_valueStr = valueStr
        while valueStr.find("{") > -1:
            sPos = valueStr.find("{")
            ePos = valueStr.find("}")
            fieldStr = valueStr[sPos + 1:ePos]
            # fn_note("fn_calcValue = fieldStr : " + fieldStr)
            # fn_note("fn_calcValue = row[fieldStr] : " + row[fieldStr])
            fieldValue = fn_get_str(row[fieldStr])
            if fieldValue == "-":
                fieldValue = ""
            valueStr = valueStr.replace("{" + fieldStr + "}", "\"" + fieldValue + "\"")

        fn_note("fn_calcValue - convert : " + org_valueStr + " => " + valueStr)

        return eval(valueStr)

def fn_mslCalcValue(valueStr, row):
    if "" == valueStr:
        return ""
    else:
        org_valueStr = valueStr
        while valueStr.find("{") > -1:
            sPos = valueStr.find("{")
            ePos = valueStr.find("}")
            fieldStr = valueStr[sPos + 1:ePos]
            # fn_note("fn_calcValue = fieldStr : " + fieldStr)
            # fn_note("fn_calcValue = row[fieldStr] : " + row[fieldStr])
            fieldValue = fn_get_str(row[fieldStr])
            if fieldValue == "-":
                fieldValue = ""
            valueStr = valueStr.replace("{" + fieldStr + "}", fieldValue)

        fn_note("fn_mslCalcValue - valueStr convert : " + org_valueStr + " => " + valueStr)
        return valueStr

def fn_msl(row):
    msl1Temp = ""
    msl2Temp = ""
    msl3Temp = ""
    msl4Temp = ""
    msl5Temp = ""
    msl1 = "*"
    msl2 = "*"
    msl3 = "*"
    msl4 = "*"
    msl5 = "*"
    msl1Display = "*"
    msl2Display = "*"
    msl3Display = "*"
    msl4Display = "*"
    msl5Display = "*"
    msl1Order = "1"
    msl2Order = "1"
    msl3Order = "1"
    msl4Order = "1"
    msl5Order = "1"
    msl1Apply = "*"
    msl2Apply = "*>*"
    msl3Apply = "*>*>*"
    msl4Apply = "*>*>*>*"
    msl5Apply = "*>*>*>*>*"
    mslValidation = "-"

    findGroupId = fn_get_str(row["Find Group ID"])
    findRuleNo = fn_get_str(row["Find Rule No"])

    if findGroupId.__ne__("") & findRuleNo.__ne__(""):
        msl1Order = row["Mtrl Hrchy_L1 Order"]
        msl2Order = fn_nvl(fn_get_str(row["Mtrl Hrchy_L2 Order"]), "1")
        msl3Order = fn_nvl(fn_get_str(row["Mtrl Hrchy_L3 Order"]), "1")
        msl4Order = fn_nvl(fn_get_str(row["Mtrl Hrchy_L4 Order"]), "1")
        msl5Order = fn_nvl(fn_get_str(row["Mtrl Hrchy_L5 Order"]), "1")

        msl1Temp = row["Mtrl Hrchy_L1 Name"]
        msl2Temp = fn_nvl(fn_get_str(row["Mtrl Hrchy_L2 Name"]), fn_get_str(row["Mtrl Hrchy_L2 Rule"]))
        msl3Temp = fn_nvl(fn_get_str(row["Mtrl Hrchy_L3 Name"]), fn_get_str(row["Mtrl Hrchy_L3 Rule"]))
        msl4Temp = fn_nvl(fn_get_str(row["Mtrl Hrchy_L4 Name"]), fn_get_str(row["Mtrl Hrchy_L4 Rule"]))
        msl5Temp = fn_nvl(fn_get_str(row["Mtrl Hrchy_L5 Name"]), fn_get_str(row["Mtrl Hrchy_L5 Rule"]))
        fn_note("fn_msl : " + str(msl1Temp) + " , " + str(msl2Temp) + " , " + str(msl3Temp) + " , " + str(msl4Temp) + " , " + str(msl5Temp))

        # Panel 일때 속성으로 값을 구한다.
        if msl1Temp == "Panel":
            # Panel 일때는 속성값으로 변수가 필요해서 넣어줌
            row["Item Material_MSL1"] = msl1Temp
            if msl2Temp.find("{") > -1:
                msl2Temp = fn_mslCalcValue(msl2Temp, row).strip()
            if msl3Temp.find("{") > -1:
                msl3Temp = fn_mslCalcValue(msl3Temp, row).strip()
            if msl4Temp.find("{") > -1:
                msl4Temp = fn_mslCalcValue(msl4Temp, row).strip()
            if msl5Temp.find("{") > -1:
                msl5Temp = fn_mslCalcValue(msl5Temp, row).strip()

            # 찾는게 없으면 Undefined 으로 세팅
            if msl2Temp == "":
                msl2Temp = "Undefined"
            if msl3Temp == "":
                msl3Temp = "Undefined"
            if msl4Temp == "":
                msl4Temp = "Undefined"
            if msl5Temp == "":
                msl5Temp = "Undefined"

        # 없으면 * 로 세팅
        msl1 = fn_nvl(msl1Temp, "*")
        msl2 = fn_nvl(msl2Temp, "*")
        msl3 = fn_nvl(msl3Temp, "*")
        msl4 = fn_nvl(msl4Temp, "*")
        msl5 = fn_nvl(msl5Temp, "*")

        # Display 적용
        msl1Display = fn_nvl(fn_get_str(row["Mtrl Hrchy_L1 Display"]), msl1)
        msl2Display = fn_nvl(fn_get_str(row["Mtrl Hrchy_L2 Display"]), msl2)
        msl3Display = fn_nvl(fn_get_str(row["Mtrl Hrchy_L3 Display"]), msl3)
        msl4Display = fn_nvl(fn_get_str(row["Mtrl Hrchy_L4 Display"]), msl4)
        msl5Display = fn_nvl(fn_get_str(row["Mtrl Hrchy_L5 Display"]), msl5)

        # Ovr 값이 있으면 반영
        if "".__ne__(fn_get_str(row["Item Material_MSL1_Ovr"])):
            msl1 = fn_get_str(row["Item Material_MSL1_Ovr"])
            msl1Display = msl1
        if "".__ne__(fn_get_str(row["Item Material_MSL2_Ovr"])):
            msl2 = fn_get_str(row["Item Material_MSL2_Ovr"])
            msl2Display = msl2
        if "".__ne__(fn_get_str(row["Item Material_MSL3_Ovr"])):
            msl3 = fn_get_str(row["Item Material_MSL3_Ovr"])
            msl3Display = msl3
        if "".__ne__(fn_get_str(row["Item Material_MSL4_Ovr"])):
            msl4 = fn_get_str(row["Item Material_MSL4_Ovr"])
            msl4Display = msl4
        if "".__ne__(fn_get_str(row["Item Material_MSL5_Ovr"])):
            msl5 = fn_get_str(row["Item Material_MSL5_Ovr"])
            msl5Display = msl5

        # hrchy 구성
        msl1Apply = msl1
        msl2Apply = msl1 + ">" + msl2
        msl3Apply = msl1 + ">" + msl2 + ">" + msl3
        msl4Apply = msl1 + ">" + msl2 + ">" + msl3 + ">" + msl4
        msl5Apply = msl1 + ">" + msl2 + ">" + msl3 + ">" + msl4 + ">" + msl5
    else:
        mslValidation = "No Mapping"

    fn_note("fn_msl : " + str(msl1) + " , " + str(msl2) + " , " + str(msl3) + " , " + str(msl4) + " , " + str(msl5) + " / " +
            str(msl1Order) + " , " + str(msl2Order) + " , " + str(msl3Order) + " , " + str(msl4Order) + " , " + str(msl5Order) + " / " +
            str(msl1Apply) + " , " + str(msl2Apply) + " , " + str(msl3Apply) + " , " + str(msl4Apply) + " , " + str(msl5Apply) + " / " +
            str(msl1Display) + " , " + str(msl2Display) + " , " + str(msl3Display) + " , " + str(msl4Display) + " , " + str(msl5Display))
    return [msl1, msl2, msl3, msl4, msl5,
                msl1Order, msl2Order, msl3Order, msl4Order, msl5Order,
                msl1Apply, msl2Apply, msl3Apply, msl4Apply, msl5Apply,
                msl1Display, msl2Display, msl3Display, msl4Display, msl5Display,
                mslValidation]

def fn_convertRegFormat(patternVal: str):
    pResult = ""

    if patternVal == "":
        pResult = ""
    elif patternVal.find("*") > -1:
        firstChar = patternVal[0:1]
        lastChar = patternVal[-1:]

        patternVal = patternVal.replace("*", ".*")

        if "*".__eq__(firstChar) and "*".__ne__(lastChar):
            pResult = patternVal + "$"
        elif "*".__ne__(firstChar) and "*".__eq__(lastChar):
            pResult = "^" + patternVal
        else:
            pResult = patternVal
    else:
        pResult = "^" + patternVal + "$"

    return pResult

# Member 를 보여줄지를 체크한다.
def fn_viewFlag(_row, _field, _df):
    r_count_df = _df.loc[_df["MSL"] == _row[_field], "Count"]
    r_scmCount_df = _df.loc[_df["MSL"] == _row[_field], "SCM Count"]

    if len(r_count_df) > 0:
        if r_count_df.iloc[0] == r_scmCount_df.iloc[0]:
            return False
        else:
            return True
    else:
        return True


def fn_c1(row):
    msl5 = fn_get_str(row["Item Material_MSL5_Apply"])
    msl5Arr = msl5.split(">")

    result1 = ""
    # 코드가 들어갈 경우 이름 용으로 만듬
    result2 = ""

    if msl5Arr[0] == "Panel":
        cis00494 = fn_getCisValue(row["Item Material.[Item Material]"], "C_00494")

        gtCode = (dict_gtCode.get(cis00494))
        if gtCode != None:
            if gtCode.split(":")[1] != "":
                result1 = gtCode.split(":")[1]
            else:
                result1 = gtCode.split(":")[0]

            result2 = result1
    else:
        if row["C1_Count"] == 1:
            result1 = row["C1_CODE_Max"]
            result2 = row["C1_Max"]
        elif row["C1_Count"] > 1:
            result1 = "Multi(" + str(int(row["C1_Count"])) + ")"
            result2 = result1

    return [result1, result2]

def fn_c5(row):
    msl5 = fn_get_str(row["Item Material_MSL5_Apply"])
    result = ""

    if msl5.__ne__(""):
        msl5Arr = msl5.split(">")

        if ( row["Mtrl Hrchy_L1 Key Material Group Flag"] == True ):
            result = msl5Arr[0]
        if ( row["Mtrl Hrchy_L2 Key Material Group Flag"] == True ):
            result = fn_concat(result, msl5Arr[1])
        if ( row["Mtrl Hrchy_L3 Key Material Group Flag"] == True ):
            result = fn_concat(result, msl5Arr[2])
        if ( row["Mtrl Hrchy_L4 Key Material Group Flag"] == True ):
            result = fn_concat(result, msl5Arr[3])
        if ( row["Mtrl Hrchy_L5 Key Material Group Flag"] == True ):
            result = fn_concat(result, msl5Arr[4])

    fn_note("result : " + result + " , msl5 : " + msl5)

    return [result]

def fn_findAttrValue(row, mapIdx, orgAttr, orgRule, col1, col2, col3, col4):
    fn_note("fn_findAttrValue : " + str(orgAttr) + "," + str(orgRule))

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
    def isIntEq(val: str, compVal: str):
        if val == "" or compVal == "":
            return False

        if int(val) == int(float(compVal)):
            return True
        else:
            return False
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
            fn_note("isIntBetween : " + val + " , " + sVal + " , " + eVal)
            if val == "" or sVal == "" or eVal == "":
                return False

            if int(val) >= int(sVal) and int(val) <= int(eVal):
                return True
            else:
                return False
        except Exception as e:
            logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())

    ruleNo = df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_RuleNo"]
    levelData = df_in_itemMaterialAttrMap.loc[mapIdx, "Hrcy Level Data.[Hrcy Level Data]"]

    attrLevelData = levelData
    attrRuleNo = ""
    attrValue = ""
    attrValid = fn_get_str(row["Item Material_Valid"])

    if "" == fn_nvl(orgAttr, ""):
        try:
            # 조건 판단
            field1 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Field01"])
            condi1 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Condition01"])
            value1 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Value01"])
            field2 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Field02"])
            condi2 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Condition02"])
            value2 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Value02"])
            field3 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Field03"])
            condi3 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Condition03"])
            value3 = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Value03"])

            # 필드값을 Bind 후의 값을 구한다.
            field1_value = fn_calcValue(fn_field(field1), row)
            field2_value = fn_calcValue(fn_field(field2), row)
            field3_value = fn_calcValue(fn_field(field3), row)
            fn_note("fn_findAttrValue - field_value : " + field1_value + " , " + field2_value + " , " + field3_value)

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

            fn_note("fn_findAttrValue - Condition = " + field1_value + " / " + condi1 + " / " + value1 + " , " + field2_value + " / " + condi2 + " / " + value2 + " , " + field3_value + " / " + condi3 + " / " + value3)

            # fn_note(condi1 + "(" + fn_getSingleQuotation(field1_value) + "," + fn_getSingleQuotation(value1) + ")")
            # fn_note(condi2 + "(" + fn_getSingleQuotation(field2_value) + "," + fn_getSingleQuotation(value2) + ")")
            # fn_note(condi3 + "(" + fn_getSingleQuotation(field3_value) + "," + fn_getSingleQuotation(value3) + ")")
            if (eval(condi1 + "(" + fn_getSingleQuotation(field1_value) + "," + fn_getSingleQuotation(value1) + ")") and
                    eval(condi2 + "(" + fn_getSingleQuotation(field2_value) + "," + fn_getSingleQuotation(value2) + ")") and
                    eval(condi3 + "(" + fn_getSingleQuotation(field3_value) + "," + fn_getSingleQuotation(value3) + ")")):
                fn_note("fn_findAttrValue - Condition Yes")

                if "".__eq__(fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_CIS Attr ID"])):
                    # Cis 정보가 없으면
                    if (not gfn_isnull(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Fix"])):
                        # Fix 값이 있으면
                        fn_note("fn_findAttrValue - Condition Yes - Fix")
                        attrValue = df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Fix"]
                    else:
                        # Logic 값이 있으면
                        fn_note("fn_findAttrValue - Condition Yes - Logic")
                        logic = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Logic"])
                        if ("".__ne__(logic)):
                            attrValue = fn_calcValue(logic, row)
                else:
                    # Cis 정보가 있으면
                    fn_note("fn_findAttrValue - Condition Yes - Cis : " + row["Item Material.[Item Material]"] + " , " + df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_CIS Attr ID"])
                    attrValue = fn_getCisValue(row["Item Material.[Item Material]"], fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_CIS Attr ID"]))

                    # Logic 가 있으면
                    logic_value = fn_get_str(df_in_itemMaterialAttrMap.loc[mapIdx, "Item Material Attr Map_Logic"])
                    if "".__ne__(logic_value):
                        logic_value = logic_value.replace("{CIS Value}", "'" + attrValue + "'")
                        attrValue = eval(logic_value)

                if "".__ne__(attrValue):
                    attrLevelData = levelData
                    attrRuleNo = ruleNo
        except Exception as e:
            attrValue = "# Error #"
            attrRuleNo = ruleNo + " => " + traceback.format_exc()
            attrLevelData = levelData

            if "-".__eq__(attrValid):
                attrValid = attrRuleNo
            else:
                attrValid = fn_concat(attrValid, attrRuleNo)

            print(traceback.format_exc())
    else:
        attrRuleNo = orgRule
        attrValue = orgAttr
        attrValid = "-"

    fn_note("fn_findAttrValue - return : " + " attrValue : "  + str(attrValue) + " , attrLevelData : "  + str(attrLevelData) + " , attrRuleNo : "  + str(attrRuleNo) + " , attrValid : "  + str(attrValid))

    # if "".__eq__(attrValue):
    #     attrValue = "-"

    # (주의) apply 할때 조건을 걸어서 함수를 호출하면 return 할때 Series로 넘겨줘야 컬럼이 매핑되어 들어간다. 조건이 없으면 그냥 배열로 매핑되어 들어간다.
    # return [str(attrValue), attrRuleNo, attrValid, attrLevelData]
    return pd.Series({col1 : str(attrValue), col2 : attrRuleNo, col3 : attrValid, col4 : attrLevelData })

# 필드 값이면 {} 를 넣어준다.
def fn_field(valueStr):
    if "".__eq__(valueStr):
        return ""
    elif valueStr.find("{") < 0 and valueStr.find("(") < 0:
        return "{" + valueStr + "}"
    else:
        return valueStr

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_item.csv", encoding="UTF-8")
        df_in_itemMaterial = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterial.csv", encoding="UTF-8")
        df_in_itemMaterialSpec = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterialSpec.csv", encoding="UTF-8")
        df_in_c1 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_c1.csv", encoding="UTF-8")
        df_in_c2 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_c2.csv", encoding="UTF-8")
        df_in_c3 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_c3.csv", encoding="UTF-8")
        df_in_gtCode = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_gtCode.csv", encoding="UTF-8")
        df_in_gtCodeName = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_gtCodeName.csv", encoding="UTF-8")
        df_in_itemMaterialAttrMap = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterialAttrMap.csv", encoding="UTF-8")
        df_in_hrchy = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_hrchy.csv", encoding="UTF-8")
        df_in_rule = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_rule.csv", encoding="UTF-8")
        df_in_constType = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_constType.csv", encoding="UTF-8")
        df_in_location = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_location.csv", encoding="UTF-8")
        df_in_itemMaterialOvr = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterialOvr.csv", encoding="UTF-8")
        df_in_itemMaterialOrg = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterialOrg.csv", encoding="UTF-8")
        df_in_itemMaterialRefOrg = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterialRefOrg.csv", encoding="UTF-8")
        df_in_day = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_day.csv", encoding="UTF-8")

        pDetailLogFlag = "N"
        outVersionName = "CWV_MP"
        pAll = "Y"

        # 테스트 0 - Class Category
        # df_in_itemMaterialSpec = df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec["Item Material.[Item Material]"].isin(["AA63-00466A"]))].copy()

        # 테스트 1
        # df_in_hrchy = df_in_hrchy.loc[(df_in_hrchy["Rule.[Rule No]"].isin([104]))].copy()
        # df_in_rule = df_in_rule.loc[(df_in_rule["Rule.[Rule No]"].isin([104]))].copy()
        # df_in_itemMaterialSpec = df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec["Item Material.[Item Material]"].isin(["AA63-00466A"]))].copy()
        # df_in_itemMaterialOrg = df_in_itemMaterialOrg.iloc[0:0]

        # 테스트 2 : Plan Group 테스트
        # df_in_hrchy = df_in_hrchy.loc[(df_in_hrchy["Rule.[Rule No]"].isin([1, 5]))].copy()
        # df_in_rule = df_in_rule.loc[(df_in_rule["Rule.[Rule No]"].isin([1, 5]))].copy()
        # df_in_itemMaterialSpec = df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec["Item Material.[Item Material]"].isin(["BN96-54349A", "BN96-58179A"]))].copy()
        # df_in_itemMaterialOrg = df_in_itemMaterialOrg.iloc[0:0]


    # Item Material.[Item Material] 로 이름 통일
    df_in_item.rename(columns={"Item.[Item]": "Item Material.[Item Material]"}, inplace=True)
    df_in_constType.rename(columns={"Item.[Item]": "Item Material.[Item Material]"}, inplace=True)
    df_in_item["Exist Flag"] = "Y"

    # 타입변경
    df_in_hrchy["Mtrl Hrchy_SCM Material"] = df_in_hrchy["Mtrl Hrchy_SCM Material"].apply(lambda data : "Y" if data == True else "N")
    df_in_hrchy["Mtrl Hrchy_Plan Group"] = df_in_hrchy["Mtrl Hrchy_Plan Group"].fillna(0).astype(int).astype(str)
    vdCommon.gfn_saveDf(df_in_hrchy, "df_in_hrchy", True)

    if common.gfn_get_isLocal() == False:
        vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
        vdCommon.gfn_saveDf(df_in_itemMaterial, "df_in_itemMaterial", True)
        vdCommon.gfn_saveDf(df_in_itemMaterialSpec, "df_in_itemMaterialSpec", True)
        vdCommon.gfn_saveDf(df_in_c1, "df_in_c1", True)
        vdCommon.gfn_saveDf(df_in_c2, "df_in_c2", True)
        vdCommon.gfn_saveDf(df_in_c3, "df_in_c3", True)
        vdCommon.gfn_saveDf(df_in_gtCode, "df_in_gtCode", True)
        vdCommon.gfn_saveDf(df_in_gtCodeName, "df_in_gtCodeName", True)
        vdCommon.gfn_saveDf(df_in_itemMaterialAttrMap, "df_in_itemMaterialAttrMap", True)
        vdCommon.gfn_saveDf(df_in_hrchy, "df_in_hrchy", True)
        vdCommon.gfn_saveDf(df_in_rule, "df_in_rule", True)
        vdCommon.gfn_saveDf(df_in_constType, "df_in_constType", True)
        vdCommon.gfn_saveDf(df_in_location, "df_in_location", True)
        vdCommon.gfn_saveDf(df_in_itemMaterialOvr, "df_in_itemMaterialOvr", True)
        vdCommon.gfn_saveDf(df_in_itemMaterialOrg, "df_in_itemMaterialOrg", True)
        vdCommon.gfn_saveDf(df_in_itemMaterialRefOrg, "df_in_itemMaterialRefOrg", True)
        vdCommon.gfn_saveDf(df_in_day, "df_in_day", True)

    # 25.12.24 일자를 비교해서 데이타를 줄인다.
    if pAll == "N":
        # 일자타입 변경
        df_in_day['Time.[Day]'] = pd.to_datetime(df_in_day['Time.[Day]'])
        
        # 조건을 걸기 위해서 merge
        df_in_itemMaterialSpec["JoinKey"] = "Key"
        df_in_day["JoinKey"] = "Key"
        df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_day, how='inner', on=["JoinKey"])
        
        # 일자비교
        df_in_itemMaterialSpec = df_in_itemMaterialSpec.loc[((df_in_itemMaterialSpec["Item Material Spec_Creation Time"] >= df_in_itemMaterialSpec["Time.[Day]"]) |
                                                             (df_in_itemMaterialSpec["Item Material Spec_Update Time"] >= df_in_itemMaterialSpec["Time.[Day]"]))].copy()
        vdCommon.gfn_saveDf(df_in_itemMaterialSpec, "df_in_itemMaterialSpec Day Check", False)

    if len(df_in_itemMaterialSpec) == 0:
        raise NoData

    # 25.11.5 df_in_itemMaterialOvr 에서 lock 이 True가 아니면 각 데이타를 빈 문자열로 초기화 하는 로직 추가
    # 초기값 세팅
    for idx in range(10):
        fieldName = "Item Material_C" + gfn_lpad(idx + 1, 2) + "_Ovr.Lock"
        df_in_itemMaterialOvr[fieldName].fillna(value=False, inplace=True)
    for idx in range(15):
        fieldName = "Item Material_S" + gfn_lpad(idx + 1, 2) + "_Ovr.Lock"
        df_in_itemMaterialOvr[fieldName].fillna(value=False, inplace=True)
    # Lock 이 True 가 있는 것만 가져온다.
    df_in_itemMaterialOvr = df_in_itemMaterialOvr.loc[((df_in_itemMaterialOvr["Item Material_C01_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C02_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C03_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C04_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C05_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C06_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C07_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C08_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C09_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_C10_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S01_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S02_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S03_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S04_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S05_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S06_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S07_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S08_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S09_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S10_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S11_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S12_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S13_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S14_Ovr.Lock"] == True) |
                                                       (df_in_itemMaterialOvr["Item Material_S15_Ovr.Lock"] == True))].copy()
    # vdCommon.gfn_saveDf(df_in_itemMaterialOvr, "df_in_itemMaterialOvr", True)
    # Lock 이 False 이면 데이타 초기화
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C01_Ovr.Lock'] == False, 'Item Material_C01_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C02_Ovr.Lock'] == False, 'Item Material_C02_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C03_Ovr.Lock'] == False, 'Item Material_C03_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C04_Ovr.Lock'] == False, 'Item Material_C04_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C05_Ovr.Lock'] == False, 'Item Material_C05_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C06_Ovr.Lock'] == False, 'Item Material_C06_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C07_Ovr.Lock'] == False, 'Item Material_C07_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C08_Ovr.Lock'] == False, 'Item Material_C08_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C09_Ovr.Lock'] == False, 'Item Material_C09_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_C10_Ovr.Lock'] == False, 'Item Material_C10_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S01_Ovr.Lock'] == False, 'Item Material_S01_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S02_Ovr.Lock'] == False, 'Item Material_S02_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S03_Ovr.Lock'] == False, 'Item Material_S03_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S04_Ovr.Lock'] == False, 'Item Material_S04_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S05_Ovr.Lock'] == False, 'Item Material_S05_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S06_Ovr.Lock'] == False, 'Item Material_S06_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S07_Ovr.Lock'] == False, 'Item Material_S07_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S08_Ovr.Lock'] == False, 'Item Material_S08_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S09_Ovr.Lock'] == False, 'Item Material_S09_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S10_Ovr.Lock'] == False, 'Item Material_S10_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S11_Ovr.Lock'] == False, 'Item Material_S11_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S12_Ovr.Lock'] == False, 'Item Material_S12_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S13_Ovr.Lock'] == False, 'Item Material_S13_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S14_Ovr.Lock'] == False, 'Item Material_S14_Ovr'] = None
    df_in_itemMaterialOvr.loc[df_in_itemMaterialOvr['Item Material_S15_Ovr.Lock'] == False, 'Item Material_S15_Ovr'] = None
    vdCommon.gfn_saveDf(df_in_itemMaterialOvr, "df_in_itemMaterialOvr", True)

    # 매핑 정보 가지는 컬럼 생성
    df_in_itemMaterialSpec["Find Group ID"] = ""
    df_in_itemMaterialSpec["Find Rule No"] = ""
    df_in_itemMaterialSpec.astype({"Find Rule No" : "str"})

    ####################################################################################################################
    # MSL 속성 찾기
    ####################################################################################################################
    # Priority 로 정렬
    # 서버에서는 Object로 인식을 해서 int 로 변경
    df_in_rule = df_in_rule.astype({"Mtrl Hrchy Map Rule_Priority" : 'int'}, copy=True)
    df_in_rule = df_in_rule.sort_values(by=["Mtrl Hrchy Map Rule_Priority", "Rule.[Rule No]", "Group.[Group ID]"], ascending=[True, True, True])
    vdCommon.gfn_saveDf(df_in_rule, "df_in_rule sort", True)

    # 비교를 위해서 정규식으로 변경
    df_in_rule["Convert Mtrl Hrchy Map Rule_Code"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Code"])), axis=1 )
    df_in_rule["Convert Mtrl Hrchy Map Rule_Desc"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Desc"])), axis=1 )
    df_in_rule["Convert Mtrl Hrchy Map Rule_Long Desc"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Long Desc"])), axis=1 )
    df_in_rule["Convert Mtrl Hrchy Map Rule_Grp"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Grp"])), axis=1 )
    vdCommon.gfn_saveDf(df_in_rule, "df_in_rule", True)

    # Mapping 에 맞는 Group ID를 찾는다.
    df_in_rule.reset_index(inplace=True)
    ratio = -1
    for rowIdx in df_in_rule.index:
        vdCommon.gfn_stepLog("Main : " + "Rule No = " + str(df_in_rule.loc[rowIdx, "Rule.[Rule No]"]) +
                             " , Group ID = " + str(df_in_rule.loc[rowIdx, "Group.[Group ID]"])  +
                             " , Cod = " + str(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Code"])  +
                             " , Desc = " + str(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Desc"])  +
                             " , Long Desc = " + str(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Long Desc"]) +
                             " , Grp = " + str(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Grp"]) )

        if ratio != round((rowIdx / len(df_in_rule)) * 100, 0):
            ratio = round((rowIdx / len(df_in_rule)) * 100, 0)
            vdCommon.gfn_stepLog(" Ratio = " + str(ratio) + " %")

        df_in_itemMaterialSpec.loc[((df_in_itemMaterialSpec["Find Group ID"] == "") &
                                    (df_in_itemMaterialSpec["Item Material.[Item Material]"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Code"])) &
                                    (df_in_itemMaterialSpec["Item Material Spec_Mtrl Desc"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Desc"])) &
                                    (df_in_itemMaterialSpec["Item Material Spec_Long Desc"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Long Desc"])) &
                                    (df_in_itemMaterialSpec["Item Material Spec_Mtrl Group"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Grp"]))), ["Find Group ID", "Find Rule No"]] = [df_in_rule.loc[rowIdx, "Group.[Group ID]"], df_in_rule.loc[rowIdx, "Rule.[Rule No]"]]

    df_in_itemMaterialSpec["Find Group ID"].fillna(value="", inplace=True)
    df_in_itemMaterialSpec["Find Rule No"].fillna(value="", inplace=True)
    # df_in_itemSpec = df_in_itemSpec.loc[(df_in_itemSpec["Find Group ID"] != "")].copy()
    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, "Find Rule No", False)

    # Rule 정보 연결
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_hrchy, how='left', left_on=["Find Rule No"], right_on=["Rule.[Rule No]"])
    logger.Step(p_step_desc='df_in_hrchy merge')
    del df_in_hrchy
    # 수정 내역 연결
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_itemMaterialOvr, how='left', on=["Item Material.[Item Material]"])
    logger.Step(p_step_desc='df_in_itemMaterialOvr merge')
    del df_in_itemMaterialOvr
    # Item 연결 - 신규를 찾기 위해
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_item, how='left', on=["Item Material.[Item Material]"])
    logger.Step(p_step_desc='df_in_item merge')
    del df_in_item
    # Item Const Type 연결
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_constType, how='left', on=["Item Material.[Item Material]"])
    logger.Step(p_step_desc='df_in_constType merge')
    del df_in_constType
    df_in_itemMaterialSpec["Item.[Const Type]"].fillna(value="-", inplace=True)
    df_in_itemMaterialSpec["Item Material_Const Type"] = df_in_itemMaterialSpec["Item.[Const Type]"]

    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, "all merge", False)

    # Attr Measure 생성
    for idx in range(10):
        df_in_itemMaterialSpec["Item Material_C" + gfn_lpad(idx + 1, 2)] = ""
        df_in_itemMaterialSpec["Item Material_C" + gfn_lpad(idx + 1, 2) + "_Apply"] = ""
        df_in_itemMaterialSpec["Item Material_RuleNo C" + gfn_lpad(idx + 1, 2)] = ""
    for idx in range(15):
        df_in_itemMaterialSpec["Item Material_S" + gfn_lpad(idx + 1, 2)] = ""
        df_in_itemMaterialSpec["Item Material_S" + gfn_lpad(idx + 1, 2) + "_Apply"] = ""
        df_in_itemMaterialSpec["Item Material_RuleNo S" + gfn_lpad(idx + 1, 2)] = ""
    df_in_itemMaterialSpec["Item Material_Valid"] = "-"

    # MSL 1 ~ 5 까지 세팅
    df_in_itemMaterialSpec[["Item Material_MSL1", "Item Material_MSL2", "Item Material_MSL3", "Item Material_MSL4", "Item Material_MSL5",
                            "Item Material_MSL1_Order", "Item Material_MSL2_Order", "Item Material_MSL3_Order", "Item Material_MSL4_Order", "Item Material_MSL5_Order",
                            "Item Material_MSL1_Apply", "Item Material_MSL2_Apply", "Item Material_MSL3_Apply","Item Material_MSL4_Apply", "Item Material_MSL5_Apply",
                            "Item Material_MSL1_Display", "Item Material_MSL2_Display", "Item Material_MSL3_Display", "Item Material_MSL4_Display", "Item Material_MSL5_Display",
                            "Item Material_MSL Validation"]] = df_in_itemMaterialSpec.apply(lambda row: fn_msl(row), axis=1, result_type='expand')
    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, "Find MSL", False)

    ####################################################################################################################
    # Ref 찾기
    ####################################################################################################################
    logger.Step(p_step_desc='Ref 찾기')

    # dict_cis 생성 : Item 별 CIS, GSCM 속성 정보를 가진다.
    dict_cis = {}
    df_in_itemMaterialSpec["Item Material Spec_CIS Attr Values"].fillna(value="", inplace=True)
    df_in_itemMaterialSpec["Item Material Spec_GSCM Attr Values"].fillna(value="", inplace=True)
    # 26.1.14 속도 개선으로 로직 변경
    # for cis_row in df_in_itemMaterialSpec.index:
    #     dict_cis[df_in_itemMaterialSpec.loc[cis_row, "Item Material.[Item Material]"]] = (
    #             df_in_itemMaterialSpec.loc[cis_row, "Item Material Spec_CIS Attr Values"] + "^" + df_in_itemMaterialSpec.loc[cis_row, "Item Material Spec_GSCM Attr Values"])
    # logger.Step(p_step_desc='dict_cis 생성')
    dict_cis = dict(zip(df_in_itemMaterialSpec["Item Material.[Item Material]"], df_in_itemMaterialSpec["Item Material Spec_CIS Attr Values"] + "^" + df_in_itemMaterialSpec["Item Material Spec_GSCM Attr Values"]))
    logger.Step(p_step_desc='dict_cis 생성')

    # df_in_c1은 groupby 를 한다.
    df_in_c1_work = df_in_c1.groupby(["Item Material.[Item Material]"], as_index=False).agg(
        C1_Count=("Global Top.[GT Code]", "count"),
        C1_Max=("Vendor Mtrl_GT Name", "max"),
        C1_CODE_Max=("Global Top.[GT Code]", "max") )
    vdCommon.gfn_saveDf(df_in_c1_work, "df_in_c1_work", True)

    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_c1_work, how='left', on=["Item Material.[Item Material]"])
    logger.Step(p_step_desc='df_in_c1_work merge')
    del df_in_c1_work
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_c2, how='left', on=["Item Material.[Item Material]"])
    logger.Step(p_step_desc='df_in_c2 merge')
    del df_in_c2
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_c3, how='left', on=["Item Material.[Item Material]"])
    logger.Step(p_step_desc='df_in_c3 merge')
    del df_in_c3

    # gtCode Dict 생성
    df_in_gtCode = df_in_gtCode.merge(df_in_gtCodeName, how='inner', on=["Global Top.[GT Code]"])
    df_in_gtCode["GT_Fix Name"].fillna(value="", inplace=True)
    dict_gtCode = {}
    for row in df_in_gtCode.index:
        dict_gtCode[df_in_gtCode.loc[row, "GT Code Map_CIS00494"]] = df_in_gtCode.loc[row, "Global Top.[GT Code]"] + ":" + df_in_gtCode.loc[row, "GT_Fix Name"]
    del df_in_gtCode
    logger.Step(p_step_desc='gtCode Dict 생성')

    # C1 계산
    df_in_itemMaterialSpec["C1_Count"].fillna(value=0, inplace=True)
    df_in_itemMaterialSpec[["Item Material Ref_Vendor(HQ)", "Item Material Ref_Vendor(HQ) Display"]] = df_in_itemMaterialSpec.apply(lambda row: fn_c1(row), axis=1, result_type='expand')
    logger.Step(p_step_desc='C1 계산')

    # 기타 Rename
    df_in_itemMaterialSpec.rename(columns={"Item Material Spec Plant_Purchaser ID" : "Item Material Ref_HQ Purchaser"
                                            ,"Item Material PLC Status" : "Item Material Ref_PLC Status"
                                            ,"Item Material Spec_UOM" : "Item Material Ref_Unit"}, inplace=True)

    df_in_itemMaterialSpec["Item Material Ref_HQ Purchaser"].fillna(value="", inplace=True)
    df_in_itemMaterialSpec["Item Material Ref_PLC Status"].fillna(value="New", inplace=True)
    df_in_itemMaterialSpec["Item Material Ref_Unit"].fillna(value="", inplace=True)
    logger.Step(p_step_desc='기타 Rename')

    # 25.12.26 Category 로직 추가
    df_in_itemMaterialSpec["Item Material Ref_Class Category"] = df_in_itemMaterialSpec.apply(lambda row : fn_nvl(fn_getCisValue(row["Item Material.[Item Material]"], "Category"), "-"), axis=1)
    vdCommon.gfn_stepLog("Category 로직 종료")

    # 26.1.14 Plan Group, SCM Flag 속성 찾기
    df_in_itemMaterialSpec.rename(columns={'Mtrl Hrchy_Plan Group': 'Item Material_Plan Group', 'Mtrl Hrchy_SCM Material': 'Item Material_SCM Flag'}, inplace=True)
    df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec["Item Material_Plan Group"] == "0"), "Item Material_Plan Group"] = "-"
    df_in_itemMaterialSpec["Item Material_Plan Group"].fillna(value="-", inplace=True)
    df_in_itemMaterialSpec["Item Material_SCM Flag"].fillna(value="-", inplace=True)
    vdCommon.gfn_stepLog("Plan Group, SCM Flag 속성 찾기")

    # 26.1.16 C08 을 위한 ref 생성 : MSL1 = Panel & S09_Ovr = LED 이면 3 아니면 Plan Group
    df_in_itemMaterialSpec["Item Material Ref_Plan Group"] = df_in_itemMaterialSpec.apply(lambda row: "3" if row["Item Material_MSL1_Apply"] == "Panel" and row["Item Material_S09_Ovr"] == "LED" else row["Item Material_Plan Group"], axis=1)
    vdCommon.gfn_stepLog("C08 을 위한 ref 생성")

    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, "merge ref", False)

    ####################################################################################################################
    # Attr 속성 찾기
    ####################################################################################################################
    logger.Step(p_step_desc='Attr 속성 찾기')
    # 타입 변경
    df_in_itemMaterialAttrMap = df_in_itemMaterialAttrMap.astype(
        {"Item Material Attr Map_Field01" : 'object', "Item Material Attr Map_Condition01": 'object', "Item Material Attr Map_Value01": 'object',
                "Item Material Attr Map_Field01" : 'object', "Item Material Attr Map_Condition02": 'object', "Item Material Attr Map_Value02": 'object',
                "Item Material Attr Map_Field03" : 'object', "Item Material Attr Map_Condition03": 'object', "Item Material Attr Map_Value03": 'object',
                "Item Material Attr Map_Rule Seq" : "int" }, errors='ignore', copy=True)

    # 처음 데이타가 없을 경우 float로 나오는 문제 발생
    df_in_itemMaterialAttrMap["Item Material Attr Map_Fix"].fillna(value="", inplace=True)
    df_in_itemMaterialAttrMap["Item Material Attr Map_CIS Attr ID"].fillna(value="", inplace=True)

    # df_in_itemMaterialAttrMap 에서 의미없는 데이타 제거. Item Material Attr Map_Rule Seq 이 0 이면 사용 안하는 것임
    df_in_itemMaterialAttrMap = df_in_itemMaterialAttrMap.loc[(df_in_itemMaterialAttrMap["Item Material Attr Map_Rule Seq"] > 0)].copy()

    # 실행 순서로 정렬
    df_in_itemMaterialAttrMap = df_in_itemMaterialAttrMap.sort_values(by=["Item Material Attr Map_Rule Seq", "Attr No.[Attr No]"], ascending=[True, True])
    df_in_itemMaterialAttrMap.reset_index(inplace=True)

    # 먼저 초기화를 한다.
    df_in_itemMaterialSpec["Item Material_Level Data"] = ""

    logger.Step(p_step_desc='Attr 속성 찾기 - Common 이 아닌 경우')
    ##### Attr 속성 찾기 - Common 이 아닌 경우에, Attr Map 을 기준으로 전체 Item을 호출해서 처리한다.
    for mapping_row in df_in_itemMaterialAttrMap.index:
        # Common 이면 스킵
        if "Common" == df_in_itemMaterialAttrMap.loc[mapping_row, "Hrcy Level Data.[Hrcy Level Data]"]:
            continue

        vdCommon.gfn_stepLog("Main : " + "ruleNo = " + df_in_itemMaterialAttrMap.loc[mapping_row, "Item Material Attr Map_RuleNo"])

        curAttbNo = fn_get_str(df_in_itemMaterialAttrMap.loc[mapping_row, "Attr No.[Attr No]"])
        attb_no = curAttbNo[-2:]
        attb_measure_code = "S"
        if "C_ATTB".__eq__(curAttbNo[0:-2]):
            attb_measure_code = "C"

        # fn_note("main - Attr Code : " + attb_measure_code + attb_no)

        # Item 별 Attr 별 속성값을 구한다.
        attrNo = "Item Material_" + attb_measure_code + attb_no
        ruleNo = "Item Material_RuleNo " + attb_measure_code + attb_no

        # Level 별로 분기
        level = fn_get_str(df_in_itemMaterialAttrMap.loc[mapping_row, "Hrcy Level Data.[Hrcy Level]"])
        levelData = fn_get_str(df_in_itemMaterialAttrMap.loc[mapping_row, "Hrcy Level Data.[Hrcy Level Data]"])
        fn_note("level : " + attrNo + " , " + level + " , " + levelData)

        if level == "LV1":
            df_in_itemMaterialSpec.loc[df_in_itemMaterialSpec["Item Material_MSL1_Apply"] == levelData, [attrNo, ruleNo, "Item Material_Valid", "Item Material_Level Data"]] = (
                df_in_itemMaterialSpec[df_in_itemMaterialSpec["Item Material_MSL1_Apply"] == levelData].apply(lambda row: fn_findAttrValue(row, mapping_row, row[attrNo], row[ruleNo], attrNo, ruleNo, "Item Material_Valid", "Item Material_Level Data"), axis=1, result_type='expand'))
        elif level == "LV2":
            df_in_itemMaterialSpec.loc[df_in_itemMaterialSpec["Item Material_MSL2_Apply"] == levelData, [attrNo, ruleNo, "Item Material_Valid", "Item Material_Level Data"]] = (
                df_in_itemMaterialSpec[df_in_itemMaterialSpec["Item Material_MSL2_Apply"] == levelData].apply(lambda row: fn_findAttrValue(row, mapping_row, row[attrNo], row[ruleNo], attrNo, ruleNo, "Item Material_Valid", "Item Material_Level Data"), axis=1, result_type='expand'))
        elif level == "LV3":
            df_in_itemMaterialSpec.loc[df_in_itemMaterialSpec["Item Material_MSL3_Apply"] == levelData, [attrNo, ruleNo, "Item Material_Valid", "Item Material_Level Data"]] = (
                df_in_itemMaterialSpec[df_in_itemMaterialSpec["Item Material_MSL3_Apply"] == levelData].apply(lambda row: fn_findAttrValue(row, mapping_row, row[attrNo], row[ruleNo], attrNo, ruleNo, "Item Material_Valid", "Item Material_Level Data"), axis=1, result_type='expand'))

    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, 'Find Attr - Not Common', False)

    # 참조값 C5 계산
    df_in_itemMaterialSpec[["Item Material Ref_Key Material"]] = df_in_itemMaterialSpec.apply(lambda row: fn_c5(row), axis=1, result_type='expand')
    df_in_itemMaterialSpec["Item Material Ref_Key Material"].fillna(value="", inplace=True)

    logger.Step(p_step_desc='Attr 속성 찾기 - Common 인 경우')
    ##### Attr 속성 찾기 - Common 인 경우
    # Common 에 대해서는 속성을 처리한다.
    for mapping_row in df_in_itemMaterialAttrMap.index:
        # Common 이 아니면 스킵
        if "Common" != df_in_itemMaterialAttrMap.loc[mapping_row, "Hrcy Level Data.[Hrcy Level Data]"]:
            continue

        ruleNo = df_in_itemMaterialAttrMap.loc[mapping_row, "Item Material Attr Map_RuleNo"]
        vdCommon.gfn_stepLog("Main : " + "ruleNo = " + ruleNo)

        curAttbNo = fn_get_str(df_in_itemMaterialAttrMap.loc[mapping_row, "Attr No.[Attr No]"])
        attb_no = curAttbNo[-2:]
        attb_measure_code = "C"

        # Item 별 Attr 별 속성값을 구한다.
        attrNo = "Item Material_" + attb_measure_code + attb_no
        ruleNo = "Item Material_RuleNo " + attb_measure_code + attb_no

        # Ref 필드를 필드에 복사한다.
        logic = fn_get_str(df_in_itemMaterialAttrMap.loc[mapping_row, "Item Material Attr Map_Logic"])
        logic = logic.replace("{", "").replace("}", "")

        df_in_itemMaterialSpec[attrNo] = df_in_itemMaterialSpec[logic]
        df_in_itemMaterialSpec.loc[(~df_in_itemMaterialSpec[attrNo].isna()), ruleNo] = ruleNo

    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, 'Find Attr - Common', False)

    ##### Attr 속성 찾기 - Apply 계산
    # 타입이 Int 로 나와서 Str 으로 변경
    df_in_itemMaterialSpec["Item Material_S07"].fillna(value="", inplace=True)
    df_in_itemMaterialSpec["Item Material_S07"] = df_in_itemMaterialSpec["Item Material_S07"].apply(lambda val: str(val))

    # Ovr 값을 반영해서 Apply 값을 구한다.
    for idx in range(10):
        fieldName = "Item Material_C" + gfn_lpad(idx + 1, 2)
        df_in_itemMaterialSpec[fieldName + "_Apply"] = df_in_itemMaterialSpec[fieldName + "_Ovr"]
        df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec[fieldName + "_Apply"].isna()), fieldName + "_Apply"] = df_in_itemMaterialSpec[fieldName]
        df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec[fieldName + "_Apply"] == ""), fieldName + "_Apply"] = "-"
        # 기존값을 _Apply 값으로 다시 바꿈 : Ovr 로 반영 여부를 확인 할 수 없음
        df_in_itemMaterialSpec[fieldName] = df_in_itemMaterialSpec[fieldName + "_Apply"]

    for idx in range(15):
        # df_in_itemMaterialSpec["Item Material_S" + gfn_lpad(idx + 1, 2) + "_Apply"] = df_in_itemMaterialSpec.apply(lambda row: fn_nvl(fn_nvl(row["Item Material_S" + gfn_lpad(idx + 1, 2) + "_Ovr"], row["Item Material_S" + gfn_lpad(idx + 1, 2)]), "-"), axis=1)
        fieldName = "Item Material_S" + gfn_lpad(idx + 1, 2)
        df_in_itemMaterialSpec[fieldName + "_Apply"] = df_in_itemMaterialSpec[fieldName + "_Ovr"]
        df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec[fieldName + "_Apply"].isna()), fieldName + "_Apply"] = df_in_itemMaterialSpec[fieldName]
        df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec[fieldName + "_Apply"] == ""), fieldName + "_Apply"] = "-"
        # 기존값을 _Apply 값으로 다시 바꿈 : Ovr 로 반영 여부를 확인 할 수 없음
        df_in_itemMaterialSpec[fieldName] = df_in_itemMaterialSpec[fieldName + "_Apply"]

    # Attr 속성 찾기를 한후에 다시 MSL 1 ~ 5 까지 세팅 (Ovr 까지 반영을 한 후에 다시 계산)
    df_in_itemMaterialSpec[["Item Material_MSL1", "Item Material_MSL2", "Item Material_MSL3", "Item Material_MSL4", "Item Material_MSL5",
                            "Item Material_MSL1_Order", "Item Material_MSL2_Order", "Item Material_MSL3_Order", "Item Material_MSL4_Order", "Item Material_MSL5_Order",
                            "Item Material_MSL1_Apply", "Item Material_MSL2_Apply", "Item Material_MSL3_Apply","Item Material_MSL4_Apply", "Item Material_MSL5_Apply",
                            "Item Material_MSL1_Display", "Item Material_MSL2_Display", "Item Material_MSL3_Display", "Item Material_MSL4_Display", "Item Material_MSL5_Display",
                            "Item Material_MSL Validation"]] = df_in_itemMaterialSpec.apply(lambda row: fn_msl(row), axis=1, result_type='expand')
    fn_note("Attr 속성 찾기를 한후에 다시 MSL 1 ~ 5 까지 세팅")

    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, 'Calc Apply', False)

    # 25.2.11 Override 데이타 생성
    df_out_ovr = df_in_itemMaterialSpec[['Item Material.[Item Material]',
                                         'Item Material_C01_Apply', 'Item Material_C02_Apply', 'Item Material_C03_Apply', 'Item Material_C04_Apply', 'Item Material_C05_Apply',
                                         'Item Material_C06_Apply', 'Item Material_C07_Apply', 'Item Material_C08_Apply', 'Item Material_C09_Apply', 'Item Material_C10_Apply',
                                         'Item Material_S01_Apply', 'Item Material_S02_Apply', 'Item Material_S03_Apply', 'Item Material_S04_Apply', 'Item Material_S05_Apply',
                                         'Item Material_S06_Apply', 'Item Material_S07_Apply', 'Item Material_S08_Apply', 'Item Material_S09_Apply', 'Item Material_S10_Apply',
                                         'Item Material_S11_Apply', 'Item Material_S12_Apply', 'Item Material_S13_Apply', 'Item Material_S14_Apply', 'Item Material_S15_Apply',
                                         'Item Material_MSL1_Display', 'Item Material_MSL2_Display', 'Item Material_MSL3_Display',
                                         'Item Material_MSL4_Display', 'Item Material_MSL5_Display']].copy()
    df_out_ovr.rename(
        columns={'Item Material_C01_Apply': 'Item Material_C01_Ovr', 'Item Material_C02_Apply': 'Item Material_C02_Ovr',
                 'Item Material_C03_Apply': 'Item Material_C03_Ovr', 'Item Material_C04_Apply': 'Item Material_C04_Ovr',
                 'Item Material_C05_Apply': 'Item Material_C05_Ovr',
                 'Item Material_C06_Apply': 'Item Material_C06_Ovr', 'Item Material_C07_Apply': 'Item Material_C07_Ovr',
                 'Item Material_C08_Apply': 'Item Material_C08_Ovr', 'Item Material_C09_Apply': 'Item Material_C09_Ovr',
                 'Item Material_C10_Apply': 'Item Material_C10_Ovr',
                 'Item Material_S01_Apply': 'Item Material_S01_Ovr', 'Item Material_S02_Apply': 'Item Material_S02_Ovr',
                 'Item Material_S03_Apply': 'Item Material_S03_Ovr', 'Item Material_S04_Apply': 'Item Material_S04_Ovr',
                 'Item Material_S05_Apply': 'Item Material_S05_Ovr',
                 'Item Material_S06_Apply': 'Item Material_S06_Ovr', 'Item Material_S07_Apply': 'Item Material_S07_Ovr',
                 'Item Material_S08_Apply': 'Item Material_S08_Ovr', 'Item Material_S09_Apply': 'Item Material_S09_Ovr',
                 'Item Material_S10_Apply': 'Item Material_S10_Ovr',
                 'Item Material_S11_Apply': 'Item Material_S11_Ovr', 'Item Material_S12_Apply': 'Item Material_S12_Ovr',
                 'Item Material_S13_Apply': 'Item Material_S13_Ovr', 'Item Material_S14_Apply': 'Item Material_S14_Ovr',
                 'Item Material_S15_Apply': 'Item Material_S15_Ovr',
                 'Item Material_MSL1_Display' : 'Item Material_MSL1_Ovr', 'Item Material_MSL2_Display' : 'Item Material_MSL2_Ovr',
                 'Item Material_MSL3_Display' : 'Item Material_MSL3_Ovr', 'Item Material_MSL4_Display' : 'Item Material_MSL4_Ovr',
                 'Item Material_MSL5_Display' : 'Item Material_MSL5_Ovr' }, inplace=True)

    # Ref out 생성
    ##### Ref 데이타 복사 - copy() 제거
    df_work_ref = df_in_itemMaterialSpec[["Item Material.[Item Material]"
                                            ,"Item Material Ref_Vendor(HQ)", "Item Material Ref_HQ Purchaser", "Item Material Ref_PLC Status"
                                            ,"Item Material Ref_Unit", "Item Material Ref_Key Material", "Item Material Ref_Class Category"
                                            ,"Item Material Ref_Plan Group", "Item Material Ref_Vendor(HQ) Display"]]

    ##### Ref Org 이름 변경
    df_in_itemMaterialRefOrg.rename(columns={"Item Material Ref_Vendor(HQ)": "org_Item Material Ref_Vendor(HQ)"}, inplace=True)
    df_in_itemMaterialRefOrg.rename(columns={"Item Material Ref_HQ Purchaser": "org_Item Material Ref_HQ Purchaser"}, inplace=True)
    df_in_itemMaterialRefOrg.rename(columns={"Item Material Ref_PLC Status": "org_Item Material Ref_PLC Status"}, inplace=True)
    df_in_itemMaterialRefOrg.rename(columns={"Item Material Ref_Unit": "org_Item Material Ref_Unit"}, inplace=True)
    df_in_itemMaterialRefOrg.rename(columns={"Item Material Ref_Key Material": "org_Item Material Ref_Key Material"}, inplace=True)
    df_in_itemMaterialRefOrg.rename(columns={"Item Material Ref_Class Category": "org_Item Material Ref_Class Category"}, inplace=True)
    df_in_itemMaterialRefOrg.rename(columns={"Item Material Ref_Plan Group": "org_Item Material Ref_Plan Group"}, inplace=True)

    ##### Org와 차이가 있는 데이타만 찾는다.
    df_work_ref = df_work_ref.merge(df_in_itemMaterialRefOrg, how='left', on=["Item Material.[Item Material]"])
    del df_in_itemMaterialRefOrg
    vdCommon.gfn_stepLog('df_in_itemMaterialRefOrg merge')
    # copy() 제거
    df_work_ref = df_work_ref.loc[((df_work_ref["Item Material Ref_Vendor(HQ)"] != df_work_ref["org_Item Material Ref_Vendor(HQ)"]) |
                                     (df_work_ref["Item Material Ref_HQ Purchaser"] != df_work_ref["org_Item Material Ref_HQ Purchaser"]) |
                                     (df_work_ref["Item Material Ref_PLC Status"] != df_work_ref["org_Item Material Ref_PLC Status"]) |
                                     (df_work_ref["Item Material Ref_Unit"] != df_work_ref["org_Item Material Ref_Unit"]) |
                                     (df_work_ref["Item Material Ref_Key Material"] != df_work_ref["org_Item Material Ref_Key Material"]) |
                                     (df_work_ref["Item Material Ref_Class Category"] != df_work_ref["org_Item Material Ref_Class Category"]) |
                                     (df_work_ref["Item Material Ref_Plan Group"] != df_work_ref["org_Item Material Ref_Plan Group"]))]
    vdCommon.gfn_stepLog('Ref 차이점만 가져오기')

    ##### ref out 생성 - copy() 제거
    df_out_ref = df_work_ref[["Item Material.[Item Material]"
                                ,"Item Material Ref_Vendor(HQ)", "Item Material Ref_HQ Purchaser", "Item Material Ref_PLC Status"
                                ,"Item Material Ref_Unit", "Item Material Ref_Key Material", "Item Material Ref_Class Category"
                                ,"Item Material Ref_Plan Group", "Item Material Ref_Vendor(HQ) Display"]]

    ####################################################################################################################
    # 데이타 비교
    ####################################################################################################################
    logger.Step(p_step_desc='데이타 비교')
    # Org 이름 변경
    df_in_itemMaterialOrg.rename(columns={"Item Material_MSL1_Apply" : "Org_Item Material_MSL1_Apply",
                                            "Item Material_MSL2_Apply" : "Org_Item Material_MSL2_Apply",
                                            "Item Material_MSL3_Apply" : "Org_Item Material_MSL3_Apply",
                                            "Item Material_MSL4_Apply" : "Org_Item Material_MSL4_Apply",
                                            "Item Material_MSL5_Apply" : "Org_Item Material_MSL5_Apply",
                                            "Item Material_C01_Apply" : "Org_Item Material_C01_Apply",
                                            "Item Material_C02_Apply" : "Org_Item Material_C02_Apply",
                                            "Item Material_C03_Apply" : "Org_Item Material_C03_Apply",
                                            "Item Material_C04_Apply" : "Org_Item Material_C04_Apply",
                                            "Item Material_C05_Apply" : "Org_Item Material_C05_Apply",
                                            "Item Material_C06_Apply" : "Org_Item Material_C06_Apply",
                                            "Item Material_C07_Apply" : "Org_Item Material_C07_Apply",
                                            "Item Material_C08_Apply" : "Org_Item Material_C08_Apply",
                                            "Item Material_C09_Apply" : "Org_Item Material_C09_Apply",
                                            "Item Material_C10_Apply" : "Org_Item Material_C10_Apply",
                                            "Item Material_S01_Apply" : "Org_Item Material_S01_Apply",
                                            "Item Material_S02_Apply" : "Org_Item Material_S02_Apply",
                                            "Item Material_S03_Apply" : "Org_Item Material_S03_Apply",
                                            "Item Material_S04_Apply" : "Org_Item Material_S04_Apply",
                                            "Item Material_S05_Apply" : "Org_Item Material_S05_Apply",
                                            "Item Material_S06_Apply" : "Org_Item Material_S06_Apply",
                                            "Item Material_S07_Apply" : "Org_Item Material_S07_Apply",
                                            "Item Material_S08_Apply" : "Org_Item Material_S08_Apply",
                                            "Item Material_S09_Apply" : "Org_Item Material_S09_Apply",
                                            "Item Material_S10_Apply" : "Org_Item Material_S10_Apply",
                                            "Item Material_S11_Apply" : "Org_Item Material_S11_Apply",
                                            "Item Material_S12_Apply" : "Org_Item Material_S12_Apply",
                                            "Item Material_S13_Apply" : "Org_Item Material_S13_Apply",
                                            "Item Material_S14_Apply" : "Org_Item Material_S14_Apply",
                                            "Item Material_S15_Apply" : "Org_Item Material_S15_Apply",
                                            "Item Material_Const Type" : "Org_Item Material_Const Type"}, inplace=True)
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_itemMaterialOrg, how='left', on=["Item Material.[Item Material]"])
    del df_in_itemMaterialOrg
    df_in_itemMaterialSpec["Org Diff"] = "N"
    vdCommon.gfn_stepLog('df_in_itemMaterialOrg merge')

    # Org 와 차이가 있는 데이타를 찾는다.
    df_in_itemMaterialSpec.loc[((df_in_itemMaterialSpec["Item Material_MSL1_Apply"] != df_in_itemMaterialSpec["Org_Item Material_MSL1_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL2_Apply"] != df_in_itemMaterialSpec["Org_Item Material_MSL2_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL3_Apply"] != df_in_itemMaterialSpec["Org_Item Material_MSL3_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL4_Apply"] != df_in_itemMaterialSpec["Org_Item Material_MSL4_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL5_Apply"] != df_in_itemMaterialSpec["Org_Item Material_MSL5_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C01_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C01_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C02_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C02_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C03_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C03_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C04_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C04_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C05_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C05_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C06_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C06_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C07_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C07_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C08_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C08_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C09_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C09_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_C10_Apply"] != df_in_itemMaterialSpec["Org_Item Material_C10_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S01_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S01_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S02_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S02_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S03_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S03_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S04_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S04_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S05_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S05_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S06_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S06_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S07_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S07_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S08_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S08_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S09_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S09_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S10_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S10_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S11_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S11_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S12_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S12_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S13_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S13_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S14_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S14_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_S15_Apply"] != df_in_itemMaterialSpec["Org_Item Material_S15_Apply"]) |
                                (df_in_itemMaterialSpec["Item Material_Const Type"] != df_in_itemMaterialSpec["Org_Item Material_Const Type"])),
                                        "Org Diff"] = "Y"
    vdCommon.gfn_stepLog('Org 차이첨 비교')
    # 26.1.28 전체를 돌릴 케이스가 없기에 차이점만 남기는 로직을 제거 : 이 로직 때문에 자꾸 빠지는 케이스가 발생
    # df_in_itemMaterialSpec = df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec["Org Diff"] == "Y")]
    vdCommon.gfn_saveDf(df_in_itemMaterialSpec, 'Org Diff', False)

    # 신규 Item 찾기
    df_in_itemMaterialSpec["Item Material_Flag New Item"] = ""
    df_in_itemMaterialSpec.loc[(df_in_itemMaterialSpec["Exist Flag"].isna()), "Item Material_Flag New Item"] = "Y"
    vdCommon.gfn_stepLog('신규 Item 찾기')

    # Item Material 연결 - 속성 비교를 위해
    df_in_itemMaterialSpec = df_in_itemMaterialSpec.merge(df_in_itemMaterial, how='left', on=["Item Material.[Item Material]"])
    del df_in_itemMaterial

    # Dimension 과 차이가 있는 데이타를 찾는다.
    df_in_itemMaterialSpec["Item Material_Flag MSL Diff"] = "N"
    df_in_itemMaterialSpec.loc[((df_in_itemMaterialSpec["Item Material_MSL1_Apply"] != df_in_itemMaterialSpec["Item Material.[MSL1]"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL2_Apply"] != df_in_itemMaterialSpec["Item Material.[MSL2]"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL3_Apply"] != df_in_itemMaterialSpec["Item Material.[MSL3]"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL4_Apply"] != df_in_itemMaterialSpec["Item Material.[MSL4]"]) |
                                (df_in_itemMaterialSpec["Item Material_MSL5_Apply"] != df_in_itemMaterialSpec["Item Material.[MSL5]"]) |
                                (df_in_itemMaterialSpec["Item Material_Const Type"] != df_in_itemMaterialSpec["Item.[Const Type]"])),
                                "Item Material_Flag MSL Diff"] = "Y"

    df_in_itemMaterialSpec["Item Material_Flag Attr Diff"] = "N"
    df_in_itemMaterialSpec.loc[((df_in_itemMaterialSpec["Item Material_C01_Apply"] != df_in_itemMaterialSpec["Item Material.[C01]"]) |
                                (df_in_itemMaterialSpec["Item Material_C02_Apply"] != df_in_itemMaterialSpec["Item Material.[C02]"]) |
                                (df_in_itemMaterialSpec["Item Material_C03_Apply"] != df_in_itemMaterialSpec["Item Material.[C03]"]) |
                                (df_in_itemMaterialSpec["Item Material_C04_Apply"] != df_in_itemMaterialSpec["Item Material.[C04]"]) |
                                (df_in_itemMaterialSpec["Item Material_C05_Apply"] != df_in_itemMaterialSpec["Item Material.[C05]"]) |
                                (df_in_itemMaterialSpec["Item Material_C06_Apply"] != df_in_itemMaterialSpec["Item Material.[C06]"]) |
                                (df_in_itemMaterialSpec["Item Material_C07_Apply"] != df_in_itemMaterialSpec["Item Material.[C07]"]) |
                                (df_in_itemMaterialSpec["Item Material_C08_Apply"] != df_in_itemMaterialSpec["Item Material.[C08]"]) |
                                (df_in_itemMaterialSpec["Item Material_C09_Apply"] != df_in_itemMaterialSpec["Item Material.[C09]"]) |
                                (df_in_itemMaterialSpec["Item Material_C10_Apply"] != df_in_itemMaterialSpec["Item Material.[C10]"]) |
                                (df_in_itemMaterialSpec["Item Material_S01_Apply"] != df_in_itemMaterialSpec["Item Material.[S01]"]) |
                                (df_in_itemMaterialSpec["Item Material_S02_Apply"] != df_in_itemMaterialSpec["Item Material.[S02]"]) |
                                (df_in_itemMaterialSpec["Item Material_S03_Apply"] != df_in_itemMaterialSpec["Item Material.[S03]"]) |
                                (df_in_itemMaterialSpec["Item Material_S04_Apply"] != df_in_itemMaterialSpec["Item Material.[S04]"]) |
                                (df_in_itemMaterialSpec["Item Material_S05_Apply"] != df_in_itemMaterialSpec["Item Material.[S05]"]) |
                                (df_in_itemMaterialSpec["Item Material_S06_Apply"] != df_in_itemMaterialSpec["Item Material.[S06]"]) |
                                (df_in_itemMaterialSpec["Item Material_S07_Apply"] != df_in_itemMaterialSpec["Item Material.[S07]"]) |
                                (df_in_itemMaterialSpec["Item Material_S08_Apply"] != df_in_itemMaterialSpec["Item Material.[S08]"]) |
                                (df_in_itemMaterialSpec["Item Material_S09_Apply"] != df_in_itemMaterialSpec["Item Material.[S09]"]) |
                                (df_in_itemMaterialSpec["Item Material_S10_Apply"] != df_in_itemMaterialSpec["Item Material.[S10]"]) |
                                (df_in_itemMaterialSpec["Item Material_S11_Apply"] != df_in_itemMaterialSpec["Item Material.[S11]"]) |
                                (df_in_itemMaterialSpec["Item Material_S12_Apply"] != df_in_itemMaterialSpec["Item Material.[S12]"]) |
                                (df_in_itemMaterialSpec["Item Material_S13_Apply"] != df_in_itemMaterialSpec["Item Material.[S13]"]) |
                                (df_in_itemMaterialSpec["Item Material_S14_Apply"] != df_in_itemMaterialSpec["Item Material.[S14]"]) |
                                (df_in_itemMaterialSpec["Item Material_S15_Apply"] != df_in_itemMaterialSpec["Item Material.[S15]"])),
                                "Item Material_Flag Attr Diff"] = "Y"
    vdCommon.gfn_stepLog('dimension 과 차이점 비교')

    # 이름 변경
    df_in_itemMaterialSpec.rename(columns={"Find Group ID" : "Item Material_MSL Group ID",
                                           "Rule.[Rule No]" : "Item Material_Rule No",
                                           "Item Material Spec_Mtrl Desc": "Item Material_Description",
                                           "Item Material Spec_Long Desc": "Item Material_Long Description",
                                           "Item Material Spec_Mtrl Group": "Item Material_Material Group" }, inplace=True)

    # out 생성
    df_out = df_in_itemMaterialSpec[["Item Material.[Item Material]",
                                     "Item Material_MSL1", "Item Material_MSL2", "Item Material_MSL3", "Item Material_MSL4", "Item Material_MSL5",
                                     "Item Material_MSL1_Order", "Item Material_MSL2_Order", "Item Material_MSL3_Order", "Item Material_MSL4_Order", "Item Material_MSL5_Order",
                                     "Item Material_MSL1_Apply", "Item Material_MSL2_Apply", "Item Material_MSL3_Apply", "Item Material_MSL4_Apply", "Item Material_MSL5_Apply",
                                     "Item Material_MSL1_Display", "Item Material_MSL2_Display", "Item Material_MSL3_Display", "Item Material_MSL4_Display", "Item Material_MSL5_Display",
                                     "Item Material_MSL Validation", "Item Material_MSL Group ID", "Item Material_Flag MSL Diff", "Item Material_Flag New Item",
                                     "Item Material_Rule No", "Item Material_Description", "Item Material_Long Description", "Item Material_Material Group", "Item Material_Const Type",
                                     "Item Material_C01", "Item Material_C02", "Item Material_C03", "Item Material_C04", "Item Material_C05",
                                     "Item Material_C06", "Item Material_C07", "Item Material_C08", "Item Material_C09", "Item Material_C10",
                                     "Item Material_S01", "Item Material_S02", "Item Material_S03", "Item Material_S04", "Item Material_S05",
                                     "Item Material_S06", "Item Material_S07", "Item Material_S08", "Item Material_S09", "Item Material_S10",
                                     "Item Material_S11", "Item Material_S12", "Item Material_S13", "Item Material_S14", "Item Material_S15",
                                     "Item Material_RuleNo C01", "Item Material_RuleNo C02", "Item Material_RuleNo C03", "Item Material_RuleNo C04", "Item Material_RuleNo C05",
                                     "Item Material_RuleNo C06", "Item Material_RuleNo C07", "Item Material_RuleNo C08", "Item Material_RuleNo C09", "Item Material_RuleNo C10",
                                     "Item Material_RuleNo S01", "Item Material_RuleNo S02", "Item Material_RuleNo S03", "Item Material_RuleNo S04", "Item Material_RuleNo S05",
                                     "Item Material_RuleNo S06", "Item Material_RuleNo S07", "Item Material_RuleNo S08", "Item Material_RuleNo S09", "Item Material_RuleNo S10",
                                     "Item Material_RuleNo S11", "Item Material_RuleNo S12", "Item Material_RuleNo S13", "Item Material_RuleNo S14", "Item Material_RuleNo S15",
                                     "Item Material_C01_Apply", "Item Material_C02_Apply", "Item Material_C03_Apply", "Item Material_C04_Apply", "Item Material_C05_Apply",
                                     "Item Material_C06_Apply", "Item Material_C07_Apply", "Item Material_C08_Apply", "Item Material_C09_Apply", "Item Material_C10_Apply",
                                     "Item Material_S01_Apply", "Item Material_S02_Apply", "Item Material_S03_Apply", "Item Material_S04_Apply", "Item Material_S05_Apply",
                                     "Item Material_S06_Apply", "Item Material_S07_Apply", "Item Material_S08_Apply", "Item Material_S09_Apply", "Item Material_S10_Apply",
                                     "Item Material_S11_Apply", "Item Material_S12_Apply", "Item Material_S13_Apply", "Item Material_S14_Apply", "Item Material_S15_Apply",
                                     "Item Material_Valid", "Item Material_Level Data", "Item Material_Flag Attr Diff",
                                     "Item Material_Plan Group", "Item Material_SCM Flag"]]

    # str 로 변환시 nan 으로 치환되기 때문에 초기화 해줌
    for idx in range(10):
        df_out["Item Material_C" + gfn_lpad(idx + 1, 2)].fillna(value="-", inplace=True)
    for idx in range(15):
        df_out["Item Material_S" + gfn_lpad(idx + 1, 2)].fillna(value="-", inplace=True)

    # Attr 속성 Measure 가 없을 경우  - 로 초기화
    df_out["Item Material_Description"].fillna(value="-", inplace=True)
    df_out["Item Material_Material Group"].fillna(value="-", inplace=True)
    df_out["Item Material_Long Description"].fillna(value="-", inplace=True)
    df_out["Item Material_Const Type"].fillna(value="-", inplace=True)

    df_out = df_out.astype({"Item Material_C01": 'str', "Item Material_C02": 'str', "Item Material_C03": 'str', "Item Material_C04": 'str', "Item Material_C05": 'str',
                            "Item Material_C06": 'str', "Item Material_C07": 'str', "Item Material_C08": 'str', "Item Material_C09": 'str', "Item Material_C10": 'str',
                            "Item Material_S01": 'str', "Item Material_S02": 'str', "Item Material_S03": 'str', "Item Material_S04": 'str', "Item Material_S05": 'str',
                            "Item Material_S06": 'str', "Item Material_S07": 'str', "Item Material_S08": 'str', "Item Material_S09": 'str', "Item Material_S10": 'str',
                            "Item Material_S11": 'str', "Item Material_S12": 'str', "Item Material_S13": 'str', "Item Material_S14": 'str', "Item Material_S15": 'str',
                            "Item Material_C01_Apply": 'str', "Item Material_C02_Apply": 'str', "Item Material_C03_Apply": 'str', "Item Material_C04_Apply": 'str', "Item Material_C05_Apply": 'str',
                            "Item Material_C06_Apply": 'str', "Item Material_C07_Apply": 'str', "Item Material_C08_Apply": 'str', "Item Material_C09_Apply": 'str', "Item Material_C10_Apply": 'str',
                            "Item Material_S01_Apply": 'str', "Item Material_S02_Apply": 'str', "Item Material_S03_Apply": 'str', "Item Material_S04_Apply": 'str', "Item Material_S05_Apply": 'str',
                            "Item Material_S06_Apply": 'str', "Item Material_S07_Apply": 'str', "Item Material_S08_Apply": 'str', "Item Material_S09_Apply": 'str', "Item Material_S10_Apply": 'str',
                            "Item Material_S11_Apply": 'str', "Item Material_S12_Apply": 'str', "Item Material_S13_Apply": 'str', "Item Material_S14_Apply": 'str', "Item Material_S15_Apply": 'str'},
                           copy=True)

    # Version.[Version Name] 생성
    df_out.insert(0, "Version.[Version Name]", outVersionName)
    df_out_ref.insert(0, "Version.[Version Name]", outVersionName)
    df_out_ovr.insert(0, "Version.[Version Name]", outVersionName)

    vdCommon.gfn_saveDf(df_out, "df_out", True)
    vdCommon.gfn_saveDf(df_out_ref, "df_out_ref", True)
    vdCommon.gfn_saveDf(df_out_ovr, 'df_out_ovr', True)

    vdCommon.gfn_stepLog('plugin Execution End')
except NoData as e:
    vdCommon.gfn_stepLog('No Data')

    df_out = pd.DataFrame([], columns=[])
    df_out_ref = pd.DataFrame([], columns=[])
    df_out_ovr = pd.DataFrame([], columns=[])
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out = pd.DataFrame([], columns=[])
    df_out_ref = pd.DataFrame([], columns=[])
    df_out_ovr = pd.DataFrame([], columns=[])
finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    # df_out_log.to_csv(os.path.dirname(__file__) + "\\" + f"out_log.csv", index=False)
    # df_out_logDetail.to_csv(os.path.dirname(__file__) + "\\" + f"out_logDetail.csv", index=False)

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

