"""

df_in_item : select ( Item.[Item] * Item.[Product Group] * Item.[Product] * Item.[Class Category] ) on row, () on column;
df_in_org : Select ( Item.[Item] * Item.[3in1] * Item.[B2B/B2C] * Item.[Basic Name] * Item.[Bonding] * Item.[Cell Vendor] * Item.[Channel] * Item.[CTN] * Item.[Curved] * Item.[CY Code] * Item.[Definition] * Item.[DP Code] * Item.[Feature] * Item.[Fixed] * Item.[Grade] * Item.[Hz] * Item.[Inch] * Item.[Inch Group] * Item.[Inch(Int)] * Item.[JDM] * Item.[Key Parts] * Item.[KPI] * Item.[Marketing Name] * Item.[Marketing Name2] * Item.[Mini LED] * Item.[Model Name] * Item.[Neo OLED] * Item.[OLED] * Item.[Open Cell] * Item.[Option] * Item.[Panel Type] * Item.[Pet Name] * Item.[Pitch] * Item.[Profit Grade] * Item.[Resolution] * Item.[Series] * Item.[Series Name] * Item.[SET Item] * Item.[Smart] * Item.[Strategy] * Item.[Sub Product] * Item.[Tuner] * Item.[WiFi] * Item.[Year] * Item.[Year Alphabet]) on row, () on column;

df_out

EXEC plugin instance [PY_UI_OtherItem]
for measures {[Other Item Attr_JDM]}
using scope ( &CWVUI )
using arguments {outVersionName, "CWV_MP"), (ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


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
str_instance = 'PY_UI_OtherItem'
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
        df_in_org = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_org.csv", encoding="UTF-8")

        outVersionName = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_org, "df_in_org", True)

    setProductGroup = ["AV","MONITOR","TV"]
    setClassCategory = ["M_C_HAV","M_C_HD","M_C_LFD","M_C_LM","M_C_LSW","M_C_MNC","M_C_MS","M_C_PRJ","M_C_QS","M_C_QT","M_C_UT","M_C_VPA","Monitor Option","TV Option"]
    df_work1 = df_in_item.loc[(df_in_item["Item.[Product Group]"].isin(setProductGroup) & ~df_in_item["Item.[Class Category]"].isin(setClassCategory))].copy()
    vdCommon.gfn_saveDf(df_work1, "df_work1", True)

    lcmProductGroup = ["LCD"]
    lcmProduct = ["LCM-MONITOR", "LCM-TV"]
    lcmClassCategory = ["95DZ"]
    df_work2 = df_in_item.loc[(df_in_item["Item.[Product Group]"].isin(lcmProductGroup) & ~df_in_item["Item.[Product]"].isin(lcmProduct) & ~df_in_item["Item.[Class Category]"].isin(lcmClassCategory))].copy()
    vdCommon.gfn_saveDf(df_work2, "df_work2", True)

    productGroup = ["AV","MONITOR","TV","LCD"]
    df_work3 = df_in_item.loc[(~df_in_item["Item.[Product Group]"].isin(setProductGroup))].copy()
    vdCommon.gfn_saveDf(df_work3, "df_work3", True)

    df_work = pd.concat([df_work1, df_work2, df_work3]).reset_index(drop=True)
    vdCommon.gfn_saveDf(df_work, "df_work", True)

    df_in_org["Exist Flag"] = "-"

    df_out = df_work.merge(df_in_org, how='left', on=["Item.[Item]"])
    df_out["Version.[Version Name]"] = outVersionName
    df_out["Other Item Attr_Default"] = "-"
    df_out["Other Item Attr_Flag Diff"] = "N"

    # 속성이 없는 케이스를 찾기
    df_out.loc[(df_out["Exist Flag"].isna()), "Other Item Attr_Flag Diff"] = "Y"
    df_out = df_out.loc[(df_out["Other Item Attr_Flag Diff"] == "Y")].copy()
    vdCommon.gfn_saveDf(df_out, 'df_out Org Diff', True)

    # out 생성
    df_out = df_out[["Version.[Version Name]", "Item.[Item]", "Other Item Attr_Default", "Other Item Attr_Flag Diff"]].copy()
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


