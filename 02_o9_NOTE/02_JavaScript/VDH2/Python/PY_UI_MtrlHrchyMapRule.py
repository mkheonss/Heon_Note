"""
df_in_item : Select ([Item].[Item] ) on row,() on column;
df_in_itemMaterial : Select ([Item Material].[Item Material] * [Item Material].[MSL1] * [Item Material].[MSL2] * [Item Material].[MSL3] * [Item Material].[MSL4] * [Item Material].[MSL5] ) on row,() on column;
df_in_itemSpec : Select ([Version].[Version Name] * [Item Material Spec].[Item Material Spec] ) on row,({Measure.[Item Material Spec_Long Desc], Measure.[Item Material Spec_Mtrl Desc], Measure.[Item Material Spec_Mtrl Group]}) on column where { Measure.[Item Material Spec_Create Target Flag] == 1 };
df_in_rule : Select ([Version].[Version Name] * [Rule].[Rule No] * [Group].[Group ID] * [Hrcy Type].[Hrcy Type] ) on row, ({Measure.[Mtrl Hrchy Map Rule_Code], Measure.[Mtrl Hrchy Map Rule_Desc], Measure.[Mtrl Hrchy Map Rule_Long Desc], Measure.[Mtrl Hrchy Map Rule_Grp], Measure.[Mtrl Hrchy Map Rule_Priority]}) on column;
df_in_attr : Select ([Version].[Version Name] * [Item Material Spec].[Item Material Spec] ) on row, ({Measure.[Item Material_C01_Apply], Measure.[Item Material_C02_Apply], Measure.[Item Material_C03_Apply], Measure.[Item Material_C04_Apply], Measure.[Item Material_C05_Apply], Measure.[Item Material_C06_Apply], Measure.[Item Material_C07_Apply], Measure.[Item Material_C08_Apply], Measure.[Item Material_C09_Apply], Measure.[Item Material_C10_Apply], Measure.[Item Material_MSL1], Measure.[Item Material_MSL2], Measure.[Item Material_MSL3], Measure.[Item Material_MSL4], Measure.[Item Material_MSL5], Measure.[Item Material_Represent Vendor], Measure.[Item Material_S01_Apply], Measure.[Item Material_S02_Apply], Measure.[Item Material_S03_Apply], Measure.[Item Material_S04_Apply], Measure.[Item Material_S05_Apply], Measure.[Item Material_S06_Apply], Measure.[Item Material_S07_Apply], Measure.[Item Material_S08_Apply], Measure.[Item Material_S09_Apply], Measure.[Item Material_S10_Apply], Measure.[Item Material_S11_Apply], Measure.[Item Material_S12_Apply], Measure.[Item Material_S13_Apply], Measure.[Item Material_S14_Apply], Measure.[Item Material_S15_Apply], Measure.[Item Material_Valid]}) on column;
df_in_hrchy : Select ([Version].[Version Name] * [Rule].[Rule No] * [Hrcy Type].[Hrcy Type] ) on row, ({Measure.[Mtrl Hrchy_Attb Make Level], Measure.[Mtrl Hrchy_L1 Name], Measure.[Mtrl Hrchy_L1 Order], Measure.[Mtrl Hrchy_L1 Rule], Measure.[Mtrl Hrchy_L1 Type], Measure.[Mtrl Hrchy_L2 Name], Measure.[Mtrl Hrchy_L2 Order], Measure.[Mtrl Hrchy_L2 Rule], Measure.[Mtrl Hrchy_L2 Type], Measure.[Mtrl Hrchy_L3 Name], Measure.[Mtrl Hrchy_L3 Order], Measure.[Mtrl Hrchy_L3 Rule], Measure.[Mtrl Hrchy_L3 Type], Measure.[Mtrl Hrchy_L4 Name], Measure.[Mtrl Hrchy_L4 Order], Measure.[Mtrl Hrchy_L4 Rule], Measure.[Mtrl Hrchy_L4 Type], Measure.[Mtrl Hrchy_L5 Name], Measure.[Mtrl Hrchy_L5 Order], Measure.[Mtrl Hrchy_L5 Rule], Measure.[Mtrl Hrchy_L5 Type], Measure.[Mtrl Hrchy_L1 Display], Measure.[Mtrl Hrchy_L2 Display], Measure.[Mtrl Hrchy_L3 Display], Measure.[Mtrl Hrchy_L4 Display], Measure.[Mtrl Hrchy_L5 Display], Measure.[Mtrl Hrchy_SCM Material]}) on column where { coalesce(Measure.[Mtrl Hrchy_Validation], "") == "", Measure.[Mtrl Hrchy_Delete Flag] != "Y"};
df_in_itemOvr : Select ([Version].[Version Name] * [Item Material Spec].[Item Material Spec] ) on row,({Measure.[Item Material_MSL1_Ovr], Measure.[Item Material_MSL2_Ovr], Measure.[Item Material_MSL3_Ovr], Measure.[Item Material_MSL4_Ovr], Measure.[Item Material_MSL5_Ovr]}) on column;
df_in_org : Select ([Version].[Version Name] * [Item Material Spec].[Item Material Spec] ) on row, ({Measure.[Item Material_MSL1_Apply], Measure.[Item Material_MSL2_Apply], Measure.[Item Material_MSL3_Apply], Measure.[Item Material_MSL4_Apply], Measure.[Item Material_MSL5_Apply], Measure.[Item Material_Const Type]}) on column;
df_in_constType : Select ([Item].[Item] * [Item].[Const Type]) on row,() on column;

pDetailLogFlag = "N"

EXEC plugin instance [PY_UI_MtrlHrchyMapRule]
for measures {[Item Material_MSL1]}
using scope ( Version.[Version Name].[CWV_MP] * [Hrcy Type].[Hrcy Type].[Mtrl Standard] )
using arguments {(RunID, "Run_1"), (pDetailLogFlag, "N"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


# 2025.3.4
#   Define Hierarchy 에서 Name 에 Display 를 추가하여 매핑 룰에도 Display를 적용하도록 수정

"""


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
str_instance = 'PY_UI_MtrlHrchyMapRule'

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
    if "" == val1 or pd.isna(val1) :
        return val2
    else:
        return val1

"""입력된 숫자 또는 문자열 왼쪽에 fillchar 문자로 패딩"""
def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)

def fn_note(note:str):
    if "Y" == pDetailLogFlag:
        logger.Note(p_note=note, p_log_level=common.G_log_level.debug())

def fn_calcValue(valueStr, row):
    org_valueStr = valueStr
    fn_note("fn_calcValue = valueStr : " + valueStr)
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

    fn_note("fn_calcValue - valueStr convert : " + org_valueStr + " => " + valueStr)
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

        # Panel 일때 속성으로 값을 구한다.
        if msl1Temp == "Panel":
            # Panel 일때는 속성값으로 변수가 필요해서 넣어줌
            row["Item Material_MSL1"] = msl1Temp
            if msl2Temp.find("{") > -1:
                msl2Temp = fn_calcValue(msl2Temp, row).strip()
            if msl3Temp.find("{") > -1:
                msl3Temp = fn_calcValue(msl3Temp, row).strip()
            if msl4Temp.find("{") > -1:
                msl4Temp = fn_calcValue(msl4Temp, row).strip()
            if msl5Temp.find("{") > -1:
                msl5Temp = fn_calcValue(msl5Temp, row).strip()

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

    fn_note("fn_calcVfn_mslalue : " + str(msl1) + " , " + str(msl2) + " , " + str(msl3) + " , " + str(msl4) + " , " + str(msl5) + " / " +
            str(msl1Order) + " , " + str(msl2Order) + " , " + str(msl3Order) + " , " + str(msl4Order) + " , " + str(msl5Order) + " / " +
            str(msl1Apply) + " , " + str(msl2Apply) + " , " + str(msl3Apply) + " , " + str(msl4Apply) + " , " + str(msl5Apply) + " / " +
            str(msl1Display) + " , " + str(msl2Display) + " , " + str(msl3Display) + " , " + str(msl4Display) + " , " + str(msl5Display))
    return [msl1, msl2, msl3, msl4, msl5,
                msl1Order, msl2Order, msl3Order, msl4Order, msl5Order,
                msl1Apply, msl2Apply, msl3Apply, msl4Apply, msl5Apply,
                msl1Display, msl2Display, msl3Display, msl4Display, msl5Display,
                mslValidation]

def fn_convertRegFormat(patternVal: str):
    pResult = patternVal

    if patternVal.find("*") > -1:
        firstChar = patternVal[0:1]
        lastChar = patternVal[-1:]

        patternVal = patternVal.replace("*", ".*")

        if "*".__eq__(firstChar) and "*".__ne__(lastChar):
            pResult = patternVal + "$"
        elif "*".__ne__(firstChar) and "*".__eq__(lastChar):
            pResult = "^" + patternVal
        elif "*".__ne__(firstChar) and "*".__ne__(lastChar):
            # fn_note("fn_isEq - pattern 4")
            pResult = "^" + patternVal + "$"

    return patternVal

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


try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_hrchy = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_hrchy.csv", encoding="UTF-8")
        df_in_rule = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_rule.csv", encoding="UTF-8")
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_item.csv", encoding="UTF-8")
        df_in_itemMaterial = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterial.csv", encoding="UTF-8")
        df_in_itemSpec = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemSpec.csv", encoding="UTF-8")
        df_in_attr = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_attr.csv", encoding="UTF-8")
        df_in_itemOvr = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemOvr.csv", encoding="UTF-8")
        df_in_org = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_org.csv", encoding="UTF-8")
        df_in_constType = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_constType.csv", encoding="UTF-8")

        pDetailLogFlag = "N"

        HrcyType = "Mtrl Standard"

    df_in_item.rename(columns={"Item.[Item]": "Item Material Spec.[Item Material Spec]"}, inplace=True)
    df_in_constType.rename(columns={"Item.[Item]": "Item Material Spec.[Item Material Spec]"}, inplace=True)
    df_in_itemMaterial.rename(columns={"Item Material.[Item Material]": "Item Material Spec.[Item Material Spec]"}, inplace=True)
    df_in_item["Exist Flag"] = "Y"

    # Override 된 Apply 를 rename
    df_in_attr.rename(columns={"Item Material_C01_Apply" : "Item Material_C01",
                                "Item Material_C02_Apply" : "Item Material_C02",
                                "Item Material_C03_Apply" : "Item Material_C03",
                                "Item Material_C04_Apply" : "Item Material_C04",
                                "Item Material_C05_Apply" : "Item Material_C05",
                                "Item Material_C06_Apply" : "Item Material_C06",
                                "Item Material_C07_Apply" : "Item Material_C07",
                                "Item Material_C08_Apply" : "Item Material_C08",
                                "Item Material_C09_Apply" : "Item Material_C09",
                                "Item Material_C10_Apply" : "Item Material_C10",
                                "Item Material_S01_Apply" : "Item Material_S01",
                                "Item Material_S02_Apply" : "Item Material_S02",
                                "Item Material_S03_Apply" : "Item Material_S03",
                                "Item Material_S04_Apply" : "Item Material_S04",
                                "Item Material_S05_Apply" : "Item Material_S05",
                                "Item Material_S06_Apply" : "Item Material_S06",
                                "Item Material_S07_Apply" : "Item Material_S07",
                                "Item Material_S08_Apply" : "Item Material_S08",
                                "Item Material_S09_Apply" : "Item Material_S09",
                                "Item Material_S10_Apply" : "Item Material_S10",
                                "Item Material_S11_Apply" : "Item Material_S11",
                                "Item Material_S12_Apply" : "Item Material_S12",
                                "Item Material_S13_Apply" : "Item Material_S13",
                                "Item Material_S14_Apply" : "Item Material_S14",
                                "Item Material_S15_Apply" : "Item Material_S15"}, inplace=True)

    # S07 에 Inch가 들어 있는데 .0 이 붙어서 변경
    df_in_attr["Item Material_S07"] = df_in_attr["Item Material_S07"].apply(lambda val: str(val).replace(".0", ""))

    vdCommon.gfn_saveDf(df_in_hrchy, "df_in_hrchy", True)
    vdCommon.gfn_saveDf(df_in_rule, "df_in_rule", True)
    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_itemMaterial, "df_in_itemMaterial", True)
    vdCommon.gfn_saveDf(df_in_itemSpec, "df_in_itemSpec", True)
    vdCommon.gfn_saveDf(df_in_attr, "df_in_attr", True)
    vdCommon.gfn_saveDf(df_in_itemOvr, "df_in_itemOvr", True)
    vdCommon.gfn_saveDf(df_in_org, "df_in_org", True)
    vdCommon.gfn_saveDf(df_in_constType, "df_in_constType", True)

    # 매핑 정보 가지는 컬럼 생성
    df_in_itemSpec["Find Group ID"] = ""
    df_in_itemSpec["Find Rule No"] = ""
    df_in_itemSpec.astype({"Find Rule No" : "str"})

    # Priority 로 정렬
    df_in_rule = df_in_rule.sort_values(by=["Mtrl Hrchy Map Rule_Priority", "Rule.[Rule No]", "Group.[Group ID]"], ascending=[True, True, True])
    # vdCommon.gfn_saveDf(df_in_rule, "df_in_rule", True)

    # 정규식으로 변경
    df_in_rule["Convert Mtrl Hrchy Map Rule_Code"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Code"])), axis=1, )
    df_in_rule["Convert Mtrl Hrchy Map Rule_Desc"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Desc"])), axis=1, )
    df_in_rule["Convert Mtrl Hrchy Map Rule_Long Desc"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Long Desc"])), axis=1, )
    df_in_rule["Convert Mtrl Hrchy Map Rule_Grp"] = df_in_rule.apply(lambda row : fn_convertRegFormat(fn_get_str(row["Mtrl Hrchy Map Rule_Grp"])), axis=1, )
    # vdCommon.gfn_saveDf(df_in_rule, "df_in_rule", True)

    # Mapping 에 맞는 Group ID를 찾는다.
    df_in_rule.reset_index(inplace=True)
    for rowIdx in df_in_rule.index:
        logger.Step(p_step_desc="Main : " + "Rule No = " + str(df_in_rule.loc[rowIdx, "Rule.[Rule No]"]) + 
                                " , Group ID = " + str(df_in_rule.loc[rowIdx, "Group.[Group ID]"]) + 
                                " , Ratio = " + str(round((rowIdx / len(df_in_rule)) * 100, 0)) + " %")

        df_in_itemSpec.loc[((df_in_itemSpec["Find Group ID"] == "") &
                            (df_in_itemSpec["Item Material Spec.[Item Material Spec]"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Code"])) &
                            (df_in_itemSpec["Item Material Spec_Mtrl Desc"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Desc"])) &
                            (df_in_itemSpec["Item Material Spec_Long Desc"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Long Desc"])) &
                            (df_in_itemSpec["Item Material Spec_Mtrl Group"].str.contains(df_in_rule.loc[rowIdx, "Convert Mtrl Hrchy Map Rule_Grp"]))), ["Find Group ID", "Find Rule No"]] = [df_in_rule.loc[rowIdx, "Group.[Group ID]"], df_in_rule.loc[rowIdx, "Rule.[Rule No]"]]

    df_in_itemSpec["Find Group ID"].fillna(value="", inplace=True)
    df_in_itemSpec["Find Rule No"].fillna(value="", inplace=True)
    # df_in_itemSpec = df_in_itemSpec.loc[(df_in_itemSpec["Find Group ID"] != "")].copy()
    vdCommon.gfn_saveDf(df_in_itemSpec, "df_in_itemSpec Find Rule No", True)

    # Rule 정보 연결
    df_in_itemSpec = df_in_itemSpec.merge(df_in_hrchy, how='left', left_on=["Version.[Version Name]", "Find Rule No"], right_on=["Version.[Version Name]", "Rule.[Rule No]"])
    # 속성 정보 연결
    df_in_itemSpec = df_in_itemSpec.merge(df_in_attr, how='left', on=["Version.[Version Name]", "Item Material Spec.[Item Material Spec]"])
    # 수정 내역 연결
    df_in_itemSpec = df_in_itemSpec.merge(df_in_itemOvr, how='left', on=["Version.[Version Name]", "Item Material Spec.[Item Material Spec]"])
    # Item 연결 - 신규를 찾기 위해
    df_in_itemSpec = df_in_itemSpec.merge(df_in_item, how='left', on=["Item Material Spec.[Item Material Spec]"])
    # Item Material 연결 - 속성 비교를 위해
    df_in_itemSpec = df_in_itemSpec.merge(df_in_itemMaterial, how='left', on=["Item Material Spec.[Item Material Spec]"])
    # Item Const Type 연결
    df_in_itemSpec = df_in_itemSpec.merge(df_in_constType, how='left', on=["Item Material Spec.[Item Material Spec]"])
    df_in_itemSpec["Item.[Const Type]"].fillna(value="-", inplace=True)
    df_in_itemSpec["Item Material_Const Type"] = df_in_itemSpec["Item.[Const Type]"]

    vdCommon.gfn_saveDf(df_in_itemSpec, "df_in_itemSpec Group Info", True)

    # Hrchy 정보가 있거나 이미 Item Material 에 등록된 대상만 뽑아낸다.
    # df_in_item["Exist Flag"].fillna(value="", inplace=True)
    # df_in_item = df_in_item.loc[(df_in_item["Exist Flag"] == "Y") | (~df_in_item["Find Rule No"].isna())].copy()
    # vdCommon.gfn_saveDf(df_in_item, "df_in_item Only", True)

    # MSL 1 ~ 5 까지 세팅
    df_in_itemSpec[["Item Material_MSL1", "Item Material_MSL2", "Item Material_MSL3", "Item Material_MSL4", "Item Material_MSL5",
                    "Item Material_MSL1_Order", "Item Material_MSL2_Order", "Item Material_MSL3_Order", "Item Material_MSL4_Order", "Item Material_MSL5_Order",
                    "Item Material_MSL1_Apply", "Item Material_MSL2_Apply", "Item Material_MSL3_Apply","Item Material_MSL4_Apply", "Item Material_MSL5_Apply",
                    "Item Material_MSL1_Display", "Item Material_MSL2_Display", "Item Material_MSL3_Display", "Item Material_MSL4_Display", "Item Material_MSL5_Display",
                    "Item Material_MSL Validation"]] = df_in_itemSpec.apply(lambda row: fn_msl(row), axis=1, result_type='expand')
    vdCommon.gfn_saveDf(df_in_itemSpec, "df_in_itemSpec Find MSL", True)

    # MSL1 ~ MSL5 까지를 구하기 위해서 복사본을 만든다.
    df_find_msl = df_in_itemSpec.copy()

    # 기존값과 차이가 있는 데이타만 가져온다.
    df_in_org.rename(columns={"Item Material_MSL1_Apply" : "Org_Item Material_MSL1_Apply",
                                "Item Material_MSL2_Apply" : "Org_Item Material_MSL2_Apply",
                                "Item Material_MSL3_Apply" : "Org_Item Material_MSL3_Apply",
                                "Item Material_MSL4_Apply" : "Org_Item Material_MSL4_Apply",
                                "Item Material_MSL5_Apply" : "Org_Item Material_MSL5_Apply",
                                "Item Material_Const Type" : "Org_Item Material_Const Type"}, inplace=True)
    df_in_itemSpec["Org Diff"] = "N"
    df_in_itemSpec = df_in_itemSpec.merge(df_in_org, how='left', on=["Version.[Version Name]","Item Material Spec.[Item Material Spec]"])
    df_in_itemSpec.loc[((df_in_itemSpec["Item Material_MSL1_Apply"] != df_in_itemSpec["Org_Item Material_MSL1_Apply"]) |
                        (df_in_itemSpec["Item Material_MSL2_Apply"] != df_in_itemSpec["Org_Item Material_MSL2_Apply"]) |
                        (df_in_itemSpec["Item Material_MSL3_Apply"] != df_in_itemSpec["Org_Item Material_MSL3_Apply"]) |
                        (df_in_itemSpec["Item Material_MSL4_Apply"] != df_in_itemSpec["Org_Item Material_MSL4_Apply"]) |
                        (df_in_itemSpec["Item Material_MSL5_Apply"] != df_in_itemSpec["Org_Item Material_MSL5_Apply"]) |
                        (df_in_itemSpec["Item Material_Const Type"] != df_in_itemSpec["Org_Item Material_Const Type"])),
                                "Org Diff"] = "Y"
    df_in_itemSpec = df_in_itemSpec.loc[(df_in_itemSpec["Org Diff"] == "Y")].copy()
    vdCommon.gfn_saveDf(df_in_itemSpec, 'df_in_itemSpec Org Diff', True)

    # 신규 Item 찾기
    df_in_itemSpec["Item Material_Flag New Item"] = ""
    df_in_itemSpec.loc[(df_in_itemSpec["Exist Flag"].isna()), "Item Material_Flag New Item"] = "Y"

    # 차이가 있는 Item Material 찾기
    df_in_itemSpec["Item Material_Flag MSL Diff"] = "N"
    df_in_itemSpec.loc[((df_in_itemSpec["Item Material_MSL1_Apply"] != df_in_itemSpec["Item Material.[MSL1]"]) |
                        (df_in_itemSpec["Item Material_MSL2_Apply"] != df_in_itemSpec["Item Material.[MSL2]"]) |
                        (df_in_itemSpec["Item Material_MSL3_Apply"] != df_in_itemSpec["Item Material.[MSL3]"]) |
                        (df_in_itemSpec["Item Material_MSL4_Apply"] != df_in_itemSpec["Item Material.[MSL4]"]) |
                        (df_in_itemSpec["Item Material_MSL5_Apply"] != df_in_itemSpec["Item Material.[MSL5]"]) |
                        (df_in_itemSpec["Item Material_Const Type"] != df_in_itemSpec["Item.[Const Type]"])),
                        "Item Material_Flag MSL Diff"] = "Y"

    # 이름 변경
    df_in_itemSpec.rename(columns={"Find Group ID" : "Item Material_MSL Group ID",
                                   "Rule.[Rule No]" : "Item Material_Rule No",
                                   "Item Material Spec_Mtrl Desc": "Item Material_Description",
                                   "Item Material Spec_Long Desc": "Item Material_Long Description",
                                   "Item Material Spec_Mtrl Group": "Item Material_Material Group" }, inplace=True)

    # out 생성
    df_out = df_in_itemSpec[["Version.[Version Name]", "Item Material Spec.[Item Material Spec]",
                             "Item Material_MSL1", "Item Material_MSL2", "Item Material_MSL3", "Item Material_MSL4", "Item Material_MSL5",
                             "Item Material_MSL1_Order", "Item Material_MSL2_Order", "Item Material_MSL3_Order", "Item Material_MSL4_Order", "Item Material_MSL5_Order",
                             "Item Material_MSL1_Apply", "Item Material_MSL2_Apply", "Item Material_MSL3_Apply", "Item Material_MSL4_Apply", "Item Material_MSL5_Apply",
                             "Item Material_MSL1_Display", "Item Material_MSL2_Display", "Item Material_MSL3_Display", "Item Material_MSL4_Display", "Item Material_MSL5_Display",
                             "Item Material_MSL Validation", "Item Material_MSL Group ID", "Item Material_Flag MSL Diff", "Item Material_Flag New Item",
                             "Item Material_Rule No", "Item Material_Description", "Item Material_Long Description", "Item Material_Material Group",
                             "Item Material_Const Type"]].copy()
    vdCommon.gfn_saveDf(df_out, "df_out", True)

    # SCM Material 체크를 위한 데이타 생성 : Count, SCM Count 가 동일하면 View 를 False 처리한다.
    df_hrchy = pd.DataFrame([], columns=["MSL", "Count", "SCM Count"])
    for idx in df_in_hrchy.index:
        l1 = fn_get_str(df_in_hrchy.loc[idx, "Mtrl Hrchy_L1 Name"])
        l2 = fn_get_str(df_in_hrchy.loc[idx, "Mtrl Hrchy_L2 Name"])
        l3 = fn_get_str(df_in_hrchy.loc[idx, "Mtrl Hrchy_L3 Name"])
        l4 = fn_nvl(fn_get_str(df_in_hrchy.loc[idx, "Mtrl Hrchy_L4 Name"]), "*")
        l5 = fn_nvl(fn_get_str(df_in_hrchy.loc[idx, "Mtrl Hrchy_L5 Name"]), "*")
        scmMaterial = df_in_hrchy.loc[idx, "Mtrl Hrchy_SCM Material"]

        # 데이타가 없으면 생성
        if (df_hrchy["MSL"] == l1).sum() == 0:
            df_hrchy.loc[len(df_hrchy)] = [l1, 0, 0]
        if (df_hrchy["MSL"] == l1 + ">" + l2).sum() == 0:
            df_hrchy.loc[len(df_hrchy)] = [l1 + ">" + l2, 0, 0]
        if (df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3).sum() == 0:
            df_hrchy.loc[len(df_hrchy)] = [l1 + ">" + l2 + ">" + l3, 0, 0]
        if (df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3 + ">" + l4).sum() == 0:
            df_hrchy.loc[len(df_hrchy)] = [l1 + ">" + l2 + ">" + l3 + ">" + l4, 0, 0]
        if (df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3 + ">" + l4 + ">" + l5).sum() == 0:
            df_hrchy.loc[len(df_hrchy)] = [l1 + ">" + l2 + ">" + l3 + ">" + l4 + ">" + l5, 0, 0]

        # Count 생성
        df_hrchy.loc[(df_hrchy["MSL"] == l1), "Count"] +=1
        df_hrchy.loc[(df_hrchy["MSL"] == l1 + ">" + l2), "Count"] +=1
        df_hrchy.loc[(df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3), "Count"] +=1
        df_hrchy.loc[(df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3 + ">" + l4), "Count"] +=1
        df_hrchy.loc[(df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3 + ">" + l4 + ">" + l5), "Count"] +=1

        # SCM Count 생성
        df_hrchy.loc[((scmMaterial != True) & (df_hrchy["MSL"] == l1)), "SCM Count"] +=1
        df_hrchy.loc[((scmMaterial != True) & (df_hrchy["MSL"] == l1 + ">" + l2)), "SCM Count"] +=1
        df_hrchy.loc[((scmMaterial != True) & (df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3)), "SCM Count"] +=1
        df_hrchy.loc[((scmMaterial != True) & (df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3 + ">" + l4)), "SCM Count"] +=1
        df_hrchy.loc[((scmMaterial != True) & (df_hrchy["MSL"] == l1 + ">" + l2 + ">" + l3 + ">" + l4 + ">" + l5)), "SCM Count"] +=1
    
    # 서버에서는 Type 이 Object 로 잡혀서 조건체크를 못해서 형변환 해줌
    df_hrchy = df_hrchy.astype({"Count" : "int", "SCM Count" : "int"}, copy=True)
    vdCommon.gfn_saveDf(df_hrchy, "df_hrchy", True)

    df_out1 = df_find_msl[["Version.[Version Name]", "Item Material_MSL1_Apply", "Item Material_MSL1_Display", "Item Material_MSL1_Order"]].copy()
    df_out1 = df_out1.drop_duplicates()
    df_out1.rename(columns={"Item Material_MSL1_Apply" : "Item Material.[MSL1]",
                            "Item Material_MSL1_Display" : "Item Material MSL1_Display Alias",
                            "Item Material_MSL1_Order" : "Item Material MSL1_Sorting Order"}, inplace=True)
    df_out1["Item Material MSL1_View Flag"] = df_out1.apply(lambda row: fn_viewFlag(row, "Item Material.[MSL1]", df_hrchy), axis=1)
    vdCommon.gfn_saveDf(df_out1, "df_out1", True)

    df_out2 = df_find_msl[["Version.[Version Name]", "Item Material_MSL1_Apply", "Item Material_MSL2_Apply", "Item Material_MSL2_Display", "Item Material_MSL2_Order"]].copy()
    df_out2 = df_out2.drop_duplicates()
    # Order 조정
    df_out2['rank'] = df_out2["Item Material_MSL2_Apply"].rank()
    df_out2["Item Material_MSL2_Order"] = df_out2.apply(lambda row : int(float(row["Item Material_MSL2_Order"])) * 100 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out2 = df_out2.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out2.rename(columns={"Item Material_MSL2_Apply": "Item Material.[MSL2]",
                            "Item Material_MSL2_Display" : "Item Material MSL2_Display Alias",
                            "Item Material_MSL2_Order" : "Item Material MSL2_Sorting Order"}, inplace=True)
    df_out2["Item Material MSL2_View Flag"] = df_out2.apply(lambda row: fn_viewFlag(row, "Item Material.[MSL2]", df_hrchy), axis=1)
    vdCommon.gfn_saveDf(df_out2, "df_out2", True)

    df_out3 = df_find_msl[["Version.[Version Name]", "Item Material_MSL1_Apply", "Item Material_MSL3_Apply", "Item Material_MSL3_Display", "Item Material_MSL3_Order"]].copy()
    df_out3 = df_out3.drop_duplicates()
    # Order 조정
    df_out3['rank'] = df_out3["Item Material_MSL3_Apply"].rank()
    df_out3["Item Material_MSL3_Order"] = df_out3.apply(lambda row : int(float(row["Item Material_MSL3_Order"])) * 100 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out3 = df_out3.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out3.rename(columns={"Item Material_MSL3_Apply": "Item Material.[MSL3]",
                            "Item Material_MSL3_Display" : "Item Material MSL3_Display Alias",
                            "Item Material_MSL3_Order" : "Item Material MSL3_Sorting Order"}, inplace=True)
    df_out3["Item Material MSL3_View Flag"] = df_out3.apply(lambda row: fn_viewFlag(row, "Item Material.[MSL3]", df_hrchy), axis=1)
    vdCommon.gfn_saveDf(df_out3, "df_out3", True)

    df_out4 = df_find_msl[["Version.[Version Name]", "Item Material_MSL1_Apply", "Item Material_MSL4_Apply", "Item Material_MSL4_Display", "Item Material_MSL4_Order"]].copy()
    df_out4 = df_out4.drop_duplicates()
    # Order 조정
    df_out4['rank'] = df_out4["Item Material_MSL4_Apply"].rank()
    df_out4["Item Material_MSL4_Order"] = df_out4.apply(lambda row : int(float(row["Item Material_MSL4_Order"])) * 100 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out4 = df_out4.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out4.rename(columns={"Item Material_MSL4_Apply": "Item Material.[MSL4]",
                            "Item Material_MSL4_Display" : "Item Material MSL4_Display Alias",
                            "Item Material_MSL4_Order" : "Item Material MSL4_Sorting Order"}, inplace=True)
    df_out4["Item Material MSL4_View Flag"] = df_out4.apply(lambda row: fn_viewFlag(row, "Item Material.[MSL4]", df_hrchy), axis=1)
    vdCommon.gfn_saveDf(df_out4, "df_out4", True)

    df_out5 = df_find_msl[["Version.[Version Name]", "Item Material_MSL1_Apply", "Item Material_MSL5_Apply", "Item Material_MSL5_Display", "Item Material_MSL5_Order"]].copy()
    df_out5 = df_out5.drop_duplicates()
    # Order 조정
    df_out5['rank'] = df_out5["Item Material_MSL5_Apply"].rank()
    df_out5["Item Material_MSL5_Order"] = df_out5.apply(lambda row : int(float(row["Item Material_MSL5_Order"])) * 1000 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out5 = df_out5.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out5.rename(columns={"Item Material_MSL5_Apply": "Item Material.[MSL5]",
                            "Item Material_MSL5_Display" : "Item Material MSL5_Display Alias",
                            "Item Material_MSL5_Order" : "Item Material MSL5_Sorting Order"}, inplace=True)
    df_out5["Item Material MSL5_View Flag"] = df_out5.apply(lambda row: fn_viewFlag(row, "Item Material.[MSL5]", df_hrchy), axis=1)
    vdCommon.gfn_saveDf(df_out5, "df_out5", True)

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out = pd.DataFrame([], columns=[])
    df_out1 = pd.DataFrame([], columns=[])
    df_out2 = pd.DataFrame([], columns=[])
    df_out3 = pd.DataFrame([], columns=[])
    df_out4 = pd.DataFrame([], columns=[])
    df_out5 = pd.DataFrame([], columns=[])
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

