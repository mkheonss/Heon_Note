"""

df_in_item : Select (Item.[Item] * Item.[Class Category] * Item.[Project] * Item.[Item Stage].filter(#.Name in {"SET","LCM","OPEN_CELL","LED_MODULE"}) * Item.[ProductType].filter(#.Name in {"NOR","OPT","CKD","SKD","ROH"}) * Item.[Definition] * Item.[Series] * Item.[Inch]) on row, () on column include memberproperties {Item.[Item], [Init Date]};
df_in_cycode : Select ([Version].[Version Name] * [Item].[Item] * [Item].[Item Stage].[LCM] * [To Item].[To Item] * [Location].[Location] * [Sub Location].[Sub Location] ) on row, ({Measure.[Code Map LCM_Map Status]}) on column where { Measure.[Code Map LCM_Valid Flag] == "Y" };
df_in_hz : select ([Item Material].[Item Material] * [Item Material].[S06].filter(#.Name != "-")) on row, () on column;
df_in_cellvendor : Select ( [Location].[Location] * [Item Material].[Item Material] * [Vendor].[Vendor] * [Global Top].[GT Code] * [Partner Vendor].[Partner Vendor] ) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column where { [Version].[Version Name] };
df_in_fullbom : Select ([Location].[Location] * [Item].[Item] * [To Location].[To Location] * [To Item].[To Item] * [Item Material].[Item Material] * [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status] ) on row, ({Measure.[Full BOM_Base Qty], Measure.[Full BOM_Category No], Measure.[Dummy]}) on column where { [Version].[Version Name] };
df_in_3in1 : select ([Item Material].[Item Material] * [Item Material].[MSL3 Name].[3IN1]) on row, () on column;
df_in_strategy : select ([Item Material].[Item Material] * [Item Material].[S05].filter(#.Name != "-")) on row, () on column;

df_out

outVersionName = "CWV_MP"

EXEC plugin instance [PY_UI_LcmItemAttrRef]
for measures {[Lcm Item Attr Ref_Inch]}
using scope ( &CWVUI )
using arguments {(RunID, "Run_01"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

exec procedure PR_Job_LcmItem;


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
str_instance = 'PY_UI_LcmItemAttrRef'
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
# 스트링을 넘겨준다.
def fn_get_str(val):
    if (type(val) is str):
        return val
    elif (type(val) is float):
        if (pd.isna(val)):
            return ""
        else:
            return str(val)

def fn_note(note:str):
    if logger.get_level() == common.G_log_level.debug():
        logger.Note(p_note=note, p_log_level=common.G_log_level.debug())

def fn_yearFormat(dt:str):
    if len(dt) == 8:
        return f"{dt[:4]}-{dt[4:6]}-{dt[6:]}"
    else:
        return ""

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
        df_in_fullbom = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_fullbom.csv", encoding="UTF-8")
        df_in_cycode = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_cycode.csv", encoding="UTF-8")
        df_in_hz = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_hz.csv", encoding="UTF-8")
        df_in_cellvendor = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_cellvendor.csv", encoding="UTF-8")
        df_in_3in1 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_3in1.csv", encoding="UTF-8")
        df_in_strategy = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_strategy.csv", encoding="UTF-8")

        outVersionName = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_fullbom, "df_in_fullbom", True)
    vdCommon.gfn_saveDf(df_in_cycode, "df_in_cycode", True)
    vdCommon.gfn_saveDf(df_in_hz, "df_in_hz", True)
    vdCommon.gfn_saveDf(df_in_cellvendor, "df_in_cellvendor", True)
    vdCommon.gfn_saveDf(df_in_3in1, "df_in_3in1", True)
    vdCommon.gfn_saveDf(df_in_strategy, "df_in_strategy", True)

    df_in_set = df_in_item.loc[((df_in_item["Item.[Item Stage]"] == "SET") | (df_in_item["Item.[Item Stage]"] == "LED_MODULE")), ["Item.[Item]", "Item.[Project]", "Item.[Definition]", "Item.[Series]", "Item.[Inch]"]].copy()
    df_in_lcm = df_in_item.loc[((df_in_item["Item.[Item Stage]"] == "LCM") | (df_in_item["Item.[Item Stage]"] == "LED_MODULE")), ["Item.[Item]","Item.[Init Date]"]].copy()
    df_in_opencell = df_in_item.loc[df_in_item["Item.[Item Stage]"] == "OPEN_CELL", ["Item.[Item]"]].copy()

    df_in_fullbom = df_in_fullbom.drop(["To Location.[To Location]", "BOM Info.[BOM Version]", "Status.[Status]", "BOM Type.[BOM Type]",
                                                "BOM Status.[BOM Status]", "Full BOM_Base Qty", "Dummy"], axis=1)

    vdCommon.gfn_saveDf(df_in_set, "df_in_set", True)
    vdCommon.gfn_saveDf(df_in_lcm, "df_in_lcm", True)
    vdCommon.gfn_saveDf(df_in_opencell, "df_in_opencell", True)

    # Out 컬럼 생성
    df_out = df_in_lcm[["Item.[Item]", "Item.[Init Date]"]].copy()
    df_out["[Version].[Version Name]"] = outVersionName

    # 일자 계산을 위해 초기화 및 타입 변경
    df_out["Item.[Init Date]"].fillna(value=0, inplace=True)
    df_out["Item.[Init Date]"] = df_out["Item.[Init Date]"].astype(int).astype(str)
    df_out["Lcm Item Attr Ref_Init Year"] = df_out["Item.[Init Date]"].apply(lambda data : data[:4])
    df_out.drop(labels=["Item.[Init Date]"], axis=1, inplace=True)

    # Item의 idx 를 구한다.
    dict_out_loc = {}
    for idx in df_out.index:
        dict_out_loc[df_out.loc[idx, "Item.[Item]"]] = idx

    # SET Bom (SKU)
    df_in_set.rename(columns={"Item.[Item]" : "To Item.[To Item]"}, inplace=True)
    df_set = df_in_fullbom.merge(df_in_set, how="inner", left_on=["To Item.[To Item]"], right_on=["To Item.[To Item]"])
    df_in_lcm.rename(columns={"Item.[Item]" : "Item Material.[Item Material]"}, inplace=True)
    df_set = df_set.merge(df_in_lcm, how="inner", left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_set.rename(columns={"Item Material.[Item Material]" : "LCM Item.[Item]"}, inplace=True)
    df_set.drop_duplicates(inplace=True)
    vdCommon.gfn_saveDf(df_set, "df_set_bom", True)

    # LCM Bom
    df_in_lcm.rename(columns={"Item Material.[Item Material]" : "To Item.[To Item]"}, inplace=True)
    df_lcm = df_in_fullbom.merge(df_in_lcm, how="inner", left_on=["To Item.[To Item]"], right_on=["To Item.[To Item]"])
    df_in_opencell.rename(columns={"Item.[Item]" : "Item Material.[Item Material]"}, inplace=True)
    df_lcm = df_lcm.merge(df_in_opencell, how="inner", left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_lcm.rename(columns={"To Item.[To Item]" : "LCM Item.[Item]", "Item Material.[Item Material]" : "OPENCELL Item.[Item]"}, inplace=True)
    df_lcm.drop_duplicates(inplace=True)
    vdCommon.gfn_saveDf(df_lcm, "df_lcm_bom", True)

    # Inch
    df_gb = df_set.groupby(["LCM Item.[Item]"])["Item.[Inch]"].min().reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "Item.[Inch]": "Lcm Item Attr Ref_Inch"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Inch", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Series
    df_gb = df_set.groupby(["LCM Item.[Item]"])["Item.[Series]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "Item.[Series]": "Lcm Item Attr Ref_Series"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Series", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Set Item - Sync SOP 는 어떻게 알까?
    df_gb = df_set.groupby(["LCM Item.[Item]"])["Item.[Item]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "Item.[Item]": "Lcm Item Attr Ref_Set Item"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Set Item", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Definition
    df_gb = df_set.groupby(["LCM Item.[Item]"])["Item.[Definition]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "Item.[Definition]": "Lcm Item Attr Ref_Definition"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Definition", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Open Cell
    df_gb = df_lcm.groupby(["LCM Item.[Item]"])["OPENCELL Item.[Item]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "OPENCELL Item.[Item]": "Lcm Item Attr Ref_Open Cell"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Open Cell", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Project
    df_set = df_set.astype({"Item.[Project]": 'str'}, copy=True) # float 오류발생으로 타입 변경
    df_gb = df_set.groupby(["LCM Item.[Item]"])["Item.[Project]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "Item.[Project]": "Lcm Item Attr Ref_Project"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Project", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # cy code
    # 체크 필요 : Code Map LCM_Prod Item 에 데이타가 없어서 오류 발생
    df_in_cycode = df_in_cycode[["Item.[Item]", "To Item.[To Item]"]].copy().drop_duplicates()
    df_gb = df_in_cycode.groupby(["Item.[Item]"])["To Item.[To Item]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"To Item.[To Item]": "Lcm Item Attr Ref_CY Code"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "CY Code", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # HZ
    df_gb = df_lcm.merge(df_in_hz, how="left", left_on=["OPENCELL Item.[Item]"], right_on=["Item Material.[Item Material]"])
    df_gb["Item Material.[S06]"].fillna(value="", inplace=True)
    df_gb = df_gb.astype({"Item Material.[S06]": "str"}, copy=True)
    df_gb = df_gb.groupby(["LCM Item.[Item]"])["Item Material.[S06]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "Item Material.[S06]": "Lcm Item Attr Ref_HZ"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Hz", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Strategy : 2025.11.04 추가
    df_gb = df_lcm.merge(df_in_strategy, how="left", left_on=["OPENCELL Item.[Item]"], right_on=["Item Material.[Item Material]"])
    df_gb["Item Material.[S05]"].fillna(value="", inplace=True)
    df_gb = df_gb.astype({"Item Material.[S05]": "str"}, copy=True)
    df_gb = df_gb.groupby(["LCM Item.[Item]"])["Item Material.[S05]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]": "Item.[Item]", "Item Material.[S05]": "Lcm Item Attr Ref_Strategy"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Strategy", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # LCM 이 있는 Set Bom 을 구한다.
    df_in_lcm.rename(columns={"To Item.[To Item]": "LCM Item.[Item]"}, inplace=True)
    df_gb = df_set.merge(df_in_lcm, how="inner", left_on=["LCM Item.[Item]"], right_on=["LCM Item.[Item]"])
    df_gb = df_gb[["To Item.[To Item]", "LCM Item.[Item]"]].copy().drop_duplicates()
    df_gb.rename(columns={"LCM Item.[Item]": "Group LCM Item.[Item]"}, inplace=True)

    # Mini Led 인 대상을 뽑아서 set 기준으로 조인
    df_gb2 = df_in_fullbom.loc[df_in_fullbom["Full BOM_Category No"] == "95BV", ["Item.[Item]", "To Item.[To Item]"]].copy()
    vdCommon.gfn_saveDf(df_gb2, "Mini Led - 95BV", True)
    df_gb2.rename(columns={"Item.[Item]": "To Item.[To Item]", "To Item.[To Item]": "LCM Item.[Item]"}, inplace=True)
    df_gb3 = df_gb.merge(df_gb2, how="inner", left_on=["To Item.[To Item]"], right_on=["To Item.[To Item]"])
    # 최빈값
    df_gb3 = df_gb3.groupby(["Group LCM Item.[Item]"])["LCM Item.[Item]"].agg(lambda x: x.mode()[0]).reset_index()
    df_gb3.rename(columns={"Group LCM Item.[Item]": "Item.[Item]", "LCM Item.[Item]": "Lcm Item Attr Ref_Mini Led"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb3, "Mini Led", True)
    df_out = df_out.merge(df_gb3, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Boding 인 대상을 뽑는다.
    df_gb4 = df_in_fullbom.loc[df_in_fullbom["Full BOM_Category No"] == "91BE", ["Item.[Item]", "To Item.[To Item]"]].copy()
    vdCommon.gfn_saveDf(df_gb4, "Boding - 91BE", True)
    df_gb4.rename(columns={"Item.[Item]": "To Item.[To Item]", "To Item.[To Item]": "LCM Item.[Item]"}, inplace=True)
    df_gb5 = df_gb.merge(df_gb4, how="inner", left_on=["To Item.[To Item]"], right_on=["To Item.[To Item]"])
    # 최빈값
    df_gb5 = df_gb5.groupby(["Group LCM Item.[Item]"])["LCM Item.[Item]"].agg(lambda x: x.mode()[0]).reset_index()
    df_gb5.rename(columns={"Group LCM Item.[Item]": "Item.[Item]", "LCM Item.[Item]": "Lcm Item Attr Ref_Boding"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb5, "Boding", True)
    df_out = df_out.merge(df_gb5, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Cell Vendor - open cell 데이타임 : 2025.11.05 로직 변경
    # df_in_cellvendor.rename(columns={"Item Material.[Item Material]": "OPENCELL Item.[Item]", "Item Material.[HQ Purchaser]" : "Lcm Item Attr Ref_Cell Vendor"}, inplace=True)
    # df_gb = df_lcm.merge(df_in_cellvendor, how="left", left_on=["OPENCELL Item.[Item]"], right_on=["OPENCELL Item.[Item]"])
    # df_gb = df_gb.groupby(["LCM Item.[Item]"])["Lcm Item Attr Ref_Cell Vendor"].agg(lambda x: ','.join(set(x))).reset_index()
    # df_gb.rename(columns={"LCM Item.[Item]" : "Item.[Item]"}, inplace=True)
    # vdCommon.gfn_saveDf(df_gb, "Cell Vendor", True)
    # df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # Cell Vendor - open cell 데이타임 : 2025.11.05 로직 변경
    df_gb = df_in_cellvendor[["Item Material.[Item Material]", "Vendor.[Vendor]"]].copy().drop_duplicates()
    df_gb = df_gb.groupby(["Item Material.[Item Material]"])["Vendor.[Vendor]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"Item Material.[Item Material]" : "Item.[Item]", "Vendor.[Vendor]" : "Lcm Item Attr Ref_Cell Vendor"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "Cell Vendor", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])
    # Item Material.[Item Material],Vendor.[Vendor]

    # 3in1 : 2025.11.04 로직 변경
    # df_w_fullbom = df_in_fullbom[["To Item.[To Item]", "Item Material.[Item Material]"]].copy().drop_duplicates()
    # # lcm 이 있는 set 을 구한다.
    # df_w1 = df_set.merge(df_in_lcm, how="inner", left_on=["LCM Item.[Item]"], right_on=["LCM Item.[Item]"])
    # df_w1 = df_w1[["To Item.[To Item]"]].copy().drop_duplicates()
    # vdCommon.gfn_saveDf(df_w1, "df_w1", True)
    # # 3in1 이 있는 set 을 구한다.
    # df_w2 = df_w_fullbom.merge(df_in_3in1, how="inner", left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    # df_w2.drop(columns=["Item Material.[Item Material]","Item Material.[MSL3 Name]"], axis=1, inplace=True)
    # vdCommon.gfn_saveDf(df_w2, "df_w2", True)
    # # 둘이 같이 있는 경우를 구한다.
    # df_w3 = df_set.merge(df_w1, how="inner", left_on=["To Item.[To Item]"], right_on=["To Item.[To Item]"])
    # df_w3 = df_w3.merge(df_w2, how="inner", left_on=["To Item.[To Item]"], right_on=["To Item.[To Item]"])
    # vdCommon.gfn_saveDf(df_w3, "df_w3", True)
    # df_gb = df_w3.groupby(["LCM Item.[Item]"])["To Item.[To Item]"].agg(lambda x: ','.join(set(x))).reset_index()
    # df_gb.rename(columns={"LCM Item.[Item]" : "Item.[Item]", "To Item.[To Item]" : "Lcm Item Attr Ref_3in1"}, inplace=True)
    # vdCommon.gfn_saveDf(df_gb, "3in1", True)
    # df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    # 3in1 : lcm 을 가지는 set을 구하고, 3in1 이 있는 set을 구해서, lcm 기준으로 3in1 이 있는 애들을 가져온다.
    # lcm 이 있는 set 을 구한다.
    df_w1 = df_set.merge(df_in_lcm, how="inner", left_on=["LCM Item.[Item]"], right_on=["LCM Item.[Item]"])
    df_w1 = df_w1[["To Item.[To Item]", "LCM Item.[Item]"]].copy().drop_duplicates()
    vdCommon.gfn_saveDf(df_w1, "df_w1", True)
    # 3in1 이 있는 set 을 구한다.
    df_w_fullbom = df_in_fullbom[["To Item.[To Item]", "Item Material.[Item Material]"]].copy().drop_duplicates()
    df_w2 = df_w_fullbom.merge(df_in_3in1, how="inner", left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_w2.drop(columns=["Item Material.[MSL3 Name]"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_w2, "df_w2", True)
    # 둘이 같이 있는 경우를 구한다.
    df_w3 = df_w1.merge(df_w2, how="inner", left_on=["To Item.[To Item]"], right_on=["To Item.[To Item]"])
    vdCommon.gfn_saveDf(df_w3, "df_w3", True)
    df_gb = df_w3.groupby(["LCM Item.[Item]"])["Item Material.[Item Material]"].agg(lambda x: ','.join(set(x))).reset_index()
    df_gb.rename(columns={"LCM Item.[Item]" : "Item.[Item]", "Item Material.[Item Material]" : "Lcm Item Attr Ref_3in1"}, inplace=True)
    vdCommon.gfn_saveDf(df_gb, "3in1", True)
    df_out = df_out.merge(df_gb, how="left", left_on=["Item.[Item]"], right_on=["Item.[Item]"])

    vdCommon.gfn_saveDf(df_out, "df_out", True)

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

