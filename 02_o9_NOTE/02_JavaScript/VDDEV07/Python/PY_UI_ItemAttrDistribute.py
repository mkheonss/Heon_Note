"""

df_in_item : select (&SETItem.relatedmembers([Item]) * Item.[Product Group] * Item.[Product] * Item.[Class Category] * Item.[A1] * Item.[A2] * Item.[A3] * Item.[A4] * Item.[A5] * Item.[A6] * Item.[A7] * Item.[A8] * Item.[A9] * Item.[A10] * Item.[A11] * Item.[A12] * Item.[A13] * Item.[A14] * Item.[A15]) on row, () on column;
df_in_itemAttr  : Select ([Version].[Version Name] * [Product].[Product] * [Attr No].[Attr No] ) on row, ({Measure.[Prod Attr_Attr Name]}) on column;
df_in_org : Select (&SETItem.relatedmembers([Item]) * Item.[B2B/B2C] * Item.[Basic Name] * Item.[Channel] * Item.[CTN] * Item.[Curved] * Item.[Definition] * Item.[Feature] * Item.[Fixed] * Item.[Grade] * Item.[Inch] * Item.[Inch Group] * Item.[Inch(Int)] * Item.[JDM] * Item.[Key Parts] * Item.[KPI] * Item.[Marketing Name] * Item.[Marketing Name2] * Item.[Model Name] * Item.[Neo OLED] * Item.[OLED] * Item.[Option] * Item.[Pet Name] * Item.[Pitch] * Item.[Resolution] * Item.[Series] * Item.[Series Name] * Item.[Smart] * Item.[Strategy] * Item.[Sub Product] * Item.[Tuner] * Item.[WiFi] * Item.[Year] * Item.[Year Alphabet] * Item.[Bonding]) on row, () on column;

df_out

createdBy = "sungmin0.lim"
outVersionName = "CWV_MP"

EXEC plugin instance [PY_UI_ItemAttrDistribute]
for measures {[Item Attr_JDM]}
using scope ( &CWVUI * [Item].[Class Category].filter(#.Name in {"M_C_HAV","M_C_HD","M_C_LFD","M_C_LM","M_C_LSW","M_C_MNC","M_C_MS","M_C_PRJ","M_C_QS","M_C_QT","M_C_UT","M_C_VPA","Monitor Option","TV Option"}) )
using arguments {(RunID, "Run_01"),(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* 변경
- loc을 써서 Attribute 에 넣어주는게 속도가 오래 걸려서 DataFrame 내에서 Product에 맞는 A?? 을 각 Attribute에 넣어주도록 로직을 변경
- 2025.09.01 : A1~A15 의 값을 기록으로 남기기로 함
- 2025.09.03 : "Item Attr" MG 를  "Item Attr Dist" MG 로 변경
"""

import numpy as np
import pandas as pd
import os
import traceback
import warnings
import datetime
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ItemAttrDistribute'
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
"""입력된 숫자 또는 문자열 왼쪽에 fillchar 문자로 패딩"""
def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)

def fn_nvl(val1:str, val2:str):
    if "" == val1 or pd.isna(val1) :
        return val2
    else:
        return val1


########################################################################################################################
# Main Logic
########################################################################################################################


try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if is_local:
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_item.csv", encoding="UTF-8")
        df_in_itemAttr = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemAttr.csv", encoding="UTF-8")
        df_in_org = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_org.csv", encoding="UTF-8")

        createdBy = "sungmin0.lim"
        outVersionName = "CWV_MP"

        df_in_org = df_in_org.loc[(df_in_org["Item.[Item]"] == "QE98QN990FTXSQ")].copy()

    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_itemAttr, "df_in_itemAttr", True)
    vdCommon.gfn_saveDf(df_in_org, "df_in_org", True)

    df_out = df_in_item.copy()

    # Attr 이름만 구해서 필드 생성
    df_AttrName = df_in_itemAttr[["Prod Attr_Attr Name"]].copy()
    df_AttrName = df_AttrName.drop_duplicates()
    vdCommon.gfn_saveDf(df_AttrName, "df_AttrName", True)

    # Measure 생성 및 "-" 로 초기화
    for idx in df_AttrName.index:
        if "-".__ne__(df_AttrName.loc[idx, "Prod Attr_Attr Name"]):
            df_out["Item Attr Dist_" + df_AttrName.loc[idx, "Prod Attr_Attr Name"]] = "-"
    vdCommon.gfn_saveDf(df_out, 'df_out Reset', True)

    df_out["Item Attr Dist_Created By"] = createdBy
    df_out["Item Attr Dist_Creation Time"] = datetime.datetime.now().strftime("%Y-%m-%d")

    # 데이타중 N/A 값이 있으면 Null 이기에 - 으로 변경
    for idx in range(15):
        df_out["Item.[A" + str(idx + 1) + "]"].fillna(value="-", inplace=True)

    # ATTB01 -> A1 로 변경
    for idx in range(15):
        df_in_itemAttr.loc[((df_in_itemAttr["Attr No.[Attr No]"] == "ATTB" + gfn_lpad(str(idx + 1), 2, "0"))), "Attr No.[Attr No]"] = "Item.[A" + str(idx + 1) + "]"
    vdCommon.gfn_saveDf(df_in_itemAttr, "df_in_itemAttr chg", True)

    # A?? 값을 각 Attribute 에 넣어준다.
    for idx in df_in_itemAttr.index:
        product = df_in_itemAttr.at[idx, "Product.[Product]"]
        attrNo = df_in_itemAttr.at[idx, "Attr No.[Attr No]"]
        attrName = df_in_itemAttr.at[idx, "Prod Attr_Attr Name"]

        if attrName != "-":
            # print(" , product : " + product + " , attrNo : " + attrNo + " , attrName : " + attrName)
            df_out.loc[(df_out["Item.[Product]"] == product), "Item Attr Dist_" + attrName] = df_out[attrNo]

    vdCommon.gfn_saveDf(df_out, 'df_out Find', True)

    # 기존값과 차이가 있는 데이타만 가져온다.
    df_out["Item Attr Dist_Flag Diff"] = "N"
    df_out = df_out.merge(df_in_org, how='left', on=["Item.[Item]"])
    df_out.loc[((df_out["Item Attr Dist_B2B/B2C"] != df_out["Item.[B2B/B2C]"]) |
                (df_out["Item Attr Dist_Basic Name"] != df_out["Item.[Basic Name]"]) |
                (df_out["Item Attr Dist_Channel"] != df_out["Item.[Channel]"]) |
                (df_out["Item Attr Dist_CTN"] != df_out["Item.[CTN]"]) |
                (df_out["Item Attr Dist_Curved"] != df_out["Item.[Curved]"]) |
                (df_out["Item Attr Dist_Definition"] != df_out["Item.[Definition]"]) |
                (df_out["Item Attr Dist_Feature"] != df_out["Item.[Feature]"]) |
                (df_out["Item Attr Dist_Fixed"] != df_out["Item.[Fixed]"]) |
                (df_out["Item Attr Dist_Grade"] != df_out["Item.[Grade]"]) |
                (df_out["Item Attr Dist_Inch"] != df_out["Item.[Inch]"]) |
                (df_out["Item Attr Dist_Inch Group"] != df_out["Item.[Inch Group]"]) |
                (df_out["Item Attr Dist_Inch(Int)"] != df_out["Item.[Inch(Int)]"]) |
                (df_out["Item Attr Dist_JDM"] != df_out["Item.[JDM]"]) |
                (df_out["Item Attr Dist_Key Parts"] != df_out["Item.[Key Parts]"]) |
                (df_out["Item Attr Dist_KPI"] != df_out["Item.[KPI]"]) |
                (df_out["Item Attr Dist_Marketing Name"] != df_out["Item.[Marketing Name]"]) |
                (df_out["Item Attr Dist_Marketing Name2"] != df_out["Item.[Marketing Name2]"]) |
                (df_out["Item Attr Dist_Model Name"] != df_out["Item.[Model Name]"]) |
                (df_out["Item Attr Dist_Neo OLED"] != df_out["Item.[Neo OLED]"]) |
                (df_out["Item Attr Dist_OLED"] != df_out["Item.[OLED]"]) |
                (df_out["Item Attr Dist_Option"] != df_out["Item.[Option]"]) |
                (df_out["Item Attr Dist_Pet Name"] != df_out["Item.[Pet Name]"]) |
                (df_out["Item Attr Dist_Pitch"] != df_out["Item.[Pitch]"]) |
                (df_out["Item Attr Dist_Resolution"] != df_out["Item.[Resolution]"]) |
                (df_out["Item Attr Dist_Series"] != df_out["Item.[Series]"]) |
                (df_out["Item Attr Dist_Series Name"] != df_out["Item.[Series Name]"]) |
                (df_out["Item Attr Dist_Smart"] != df_out["Item.[Smart]"]) |
                (df_out["Item Attr Dist_Strategy"] != df_out["Item.[Strategy]"]) |
                (df_out["Item Attr Dist_Sub Product"] != df_out["Item.[Sub Product]"]) |
                (df_out["Item Attr Dist_Tuner"] != df_out["Item.[Tuner]"]) |
                (df_out["Item Attr Dist_WiFi"] != df_out["Item.[WiFi]"]) |
                (df_out["Item Attr Dist_Year"] != df_out["Item.[Year]"]) |
                (df_out["Item Attr Dist_Year Alphabet"] != df_out["Item.[Year Alphabet]"])), "Item Attr Dist_Flag Diff"] = "Y"
    df_out = df_out.loc[(df_out["Item Attr Dist_Flag Diff"] == "Y")].copy()
    vdCommon.gfn_saveDf(df_out, 'df_out Org Diff', True)

    df_out["Item Attr Dist_Asn"] = 1

    df_out.insert(0, "Version.[Version Name]", outVersionName)

    # out 생성
    df_out = df_out[["Version.[Version Name]", "Item.[Item]",
                        "Item Attr Dist_B2B/B2C", "Item Attr Dist_Basic Name", "Item Attr Dist_Channel", "Item Attr Dist_CTN", "Item Attr Dist_Curved", "Item Attr Dist_Definition",
                        "Item Attr Dist_Feature", "Item Attr Dist_Fixed", "Item Attr Dist_Grade", "Item Attr Dist_Inch", "Item Attr Dist_Inch Group", "Item Attr Dist_Inch(Int)",
                     "Item Attr Dist_JDM", "Item Attr Dist_Key Parts", "Item Attr Dist_KPI", "Item Attr Dist_Marketing Name", "Item Attr Dist_Marketing Name2",
                     "Item Attr Dist_Model Name", "Item Attr Dist_Neo OLED", "Item Attr Dist_OLED", "Item Attr Dist_Option", "Item Attr Dist_Pet Name", "Item Attr Dist_Pitch",
                     "Item Attr Dist_Resolution", "Item Attr Dist_Series", "Item Attr Dist_Series Name", "Item Attr Dist_Smart", "Item Attr Dist_Strategy", "Item Attr Dist_Sub Product",
                     "Item Attr Dist_Tuner", "Item Attr Dist_WiFi", "Item Attr Dist_Year", "Item Attr Dist_Year Alphabet", "Item Attr Dist_Flag Diff", "Item Attr Dist_Asn",
                     "Item Attr Dist_Created By", "Item Attr Dist_Creation Time",
                     "Item.[A1]", "Item.[A2]", "Item.[A3]", "Item.[A4]", "Item.[A5]",
                     "Item.[A6]", "Item.[A7]", "Item.[A8]", "Item.[A9]", "Item.[A10]",
                     "Item.[A11]", "Item.[A12]", "Item.[A13]", "Item.[A14]", "Item.[A15]"]].copy()

    df_out.rename(columns={'Item.[A1]': 'Item Attr Dist_A1', 'Item.[A2]': 'Item Attr Dist_A2', 'Item.[A3]': 'Item Attr Dist_A3'
                            ,'Item.[A4]': 'Item Attr Dist_A4', 'Item.[A5]': 'Item Attr Dist_A5'
                            ,'Item.[A6]': 'Item Attr Dist_A6', 'Item.[A7]': 'Item Attr Dist_A7', 'Item.[A8]': 'Item Attr Dist_A8'
                            ,'Item.[A9]': 'Item Attr Dist_A9', 'Item.[A10]': 'Item Attr Dist_A10'
                            ,'Item.[A11]': 'Item Attr Dist_A11', 'Item.[A12]': 'Item Attr Dist_A12', 'Item.[A13]': 'Item Attr Dist_A13'
                            ,'Item.[A14]': 'Item Attr Dist_A14', 'Item.[A15]': 'Item Attr Dist_A15'}, inplace=True)

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

