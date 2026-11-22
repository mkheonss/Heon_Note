"""
df_in_ct : Select ( [Item Material].[MSL5] * [Item Material].[Item Material] ) on row, ({Measure.[Valid Mtrl Item_Const Time Varying], Measure.[Valid Mtrl Item_Const Current], Measure.[Valid Mtrl Item_Const Exception], Measure.[Valid Mtrl Item_Frozen Horizon Vendor] }) on column where { [Version].[Version Name] };
df_in_lu : Select ( [Item Material].[MSL5] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Attr_Pallet], Measure.[Mtrl Attr_20FT], Measure.[Mtrl Attr_40FT], Measure.[Mtrl Attr_40FT HC] }) on column where { [Version].[Version Name] };
df_in_v : Select ( [Item Material].[MSL5] * [Item Material].[Item Material] ) on row, ({Measure.[Item Material_C01_Ovr] }) on column where { [Version].[Version Name] };

df_in_s_lv3_set : Select ([Item Material].[MSL3] ) on row, ({Measure.[SS Mtrl L3_Sub Set]}) on column where { [Version].[Version Name] };
df_in_s_lv3 : Select ([Location].[Location] * [Item Material].[MSL3] ) on row, ({Measure.[SS Mtrl L3_ECP Flag], Measure.[SS Mtrl L3_Source]}) on column where { [Version].[Version Name] };
df_in_s_lv4 : Select ([Location].[Location] * [Item Material].[MSL3] * [Item Material].[MSL4] ) on row, ({Measure.[SS Mtrl L4_ECP Flag], Measure.[SS Mtrl L4_Source]}) on column where { [Version].[Version Name] };
df_in_s_lv5 : Select ([Location].[Location] * [Item Material].[MSL3] * [Item Material].[MSL5] ) on row, ({Measure.[SS Mtrl L5_ECP Flag], Measure.[SS Mtrl L5_Source]}) on column where { [Version].[Version Name] };
df_in_s_item : Select ([Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[SS Mtrl Item_ECP Flag], Measure.[SS Mtrl Item_Source]}) on column where { [Version].[Version Name] };

df_in_mb_lv3 : Select ([Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl_EFF Startdate], Measure.[Dummy]}) on column where { [Version].[Version Name] };
df_in_mb_lv3_w : Select ([Location].[Location] * &MtrlValidiationWeek * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl W_Intransit LT]}) on column where { [Version].[Version Name] };
df_in_mb_item_w : Select ([Location].[Location] * &MtrlValidiationWeek * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl W_Intransit LT], Measure.[Dummy]}) on column where { [Version].[Version Name] };
df_in_week : select (&MtrlValidiationWeek);

df_in_pa : Select (&NSUILocationMFMtrlView * [Item Material].[MSL3] * [Item Material].[MSL4] * [Item Material].[MSL5] * [Item Material].[Item Material]) on row, ( { Measure.[Item Mtrl Site Asn_Cur Status] } ) on column where { [Version].[Version Name], Measure.[Item Mtrl Site Asn_Cur Status] in {"PLANNED", "ACTIVE"} };

df_out :

EXEC plugin instance [PY_UI_Master_Validation]
for measures {[Valid Mtrl MSL5_Logisitc Pallet_Cnt]}
using scope ( &CWVUI )
using arguments {(paramOutVersion, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

BN96-33736A 로 테스트

"""
   
import pandas as pd
import os
import traceback
import warnings
import numpy as np
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_Master_Validation'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 공통 함수 정의
########################################################################################################################
# 스트링을 넘겨준다.
def gfn_get_str(val):
    if (type(val) is str):
        return val
    elif (type(val) is float):
        if (pd.isna(val)):
            return ""
        else:
            return str(val)

def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)
########################################################################################################################
# 함수 정의
########################################################################################################################


try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_ct = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_ct.csv", encoding="UTF-8")
        df_in_lu = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_lu.csv", encoding="UTF-8")
        df_in_v = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_v.csv", encoding="UTF-8")

        df_in_s_lv3_set = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv3_set.csv", encoding="UTF-8")
        df_in_s_lv3 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv3.csv", encoding="UTF-8")
        df_in_s_lv4 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv4.csv", encoding="UTF-8")
        df_in_s_lv5 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv5.csv", encoding="UTF-8")
        df_in_s_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_item.csv", encoding="UTF-8")
        df_in_pa = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_pa.csv", encoding="UTF-8")

        df_in_mb_lv3 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_mb_lv3.csv", encoding="UTF-8")
        df_in_mb_lv3_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_mb_lv3_w.csv", encoding="UTF-8")
        df_in_mb_item_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_mb_item_w.csv", encoding="UTF-8")
        df_in_week = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_week.csv", encoding="UTF-8")

        paramOutVersion = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_ct, "df_in_ct", True)
    vdCommon.gfn_saveDf(df_in_lu, "df_in_lu", True)
    vdCommon.gfn_saveDf(df_in_v, "df_in_v", True)
    vdCommon.gfn_saveDf(df_in_s_lv3_set, "df_in_s_lv3_set", True)
    vdCommon.gfn_saveDf(df_in_s_lv3, "df_in_s_lv3", True)
    vdCommon.gfn_saveDf(df_in_s_lv4, "df_in_s_lv4", True)
    vdCommon.gfn_saveDf(df_in_s_lv5, "df_in_s_lv5", True)
    vdCommon.gfn_saveDf(df_in_s_item, "df_in_s_item", True)
    vdCommon.gfn_saveDf(df_in_mb_lv3, "df_in_mb_lv3", True)
    vdCommon.gfn_saveDf(df_in_mb_lv3_w, "df_in_mb_lv3_w", True)
    vdCommon.gfn_saveDf(df_in_mb_item_w, "df_in_mb_item_w", True)
    vdCommon.gfn_saveDf(df_in_week, "df_in_week", True)
    vdCommon.gfn_saveDf(df_in_pa, "df_in_pa", True)

    df_in_pa.drop(["Item Mtrl Site Asn_Cur Status"], axis=1, inplace=True)

    ####################################################################################################################
    # Safety Stock
    ####################################################################################################################
    df_in_s_lv4 = df_in_s_lv4.merge(df_in_s_lv3_set, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_s_lv4 = df_in_s_lv4.loc[(df_in_s_lv4["SS Mtrl L3_Sub Set"] == 'Lv4')].copy()
    df_in_s_lv4 = df_in_s_lv4.drop(["SS Mtrl L3_Sub Set"], axis=1)
    vdCommon.gfn_saveDf(df_in_s_lv4, "lv4 Master", True)

    df_in_s_lv5 = df_in_s_lv5.merge(df_in_s_lv3_set, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_s_lv5 = df_in_s_lv5.loc[(df_in_s_lv5["SS Mtrl L3_Sub Set"] == 'Lv5')].copy()
    df_in_s_lv5 = df_in_s_lv5.drop(["SS Mtrl L3_Sub Set"], axis=1)
    vdCommon.gfn_saveDf(df_in_s_lv5, "lv5 Master", True)

    df_ss_work_pa = df_in_pa.copy()

    # 전체를 합친다.
    df_in_s_lv4.drop(["Item Material.[MSL3]"], axis=1, inplace=True)
    df_in_s_lv5.drop(["Item Material.[MSL3]"], axis=1, inplace=True)
    df_ss_work_pa = df_ss_work_pa.merge(df_in_s_lv3, how='inner', left_on=["Item Material.[MSL3]", "Location.[Location]"], right_on=["Item Material.[MSL3]", "Location.[Location]"])
    df_ss_work_pa = df_ss_work_pa.merge(df_in_s_lv4, how='left', left_on=["Item Material.[MSL4]", "Location.[Location]"], right_on=["Item Material.[MSL4]", "Location.[Location]"])
    df_ss_work_pa = df_ss_work_pa.merge(df_in_s_lv5, how='left', left_on=["Item Material.[MSL5]", "Location.[Location]"], right_on=["Item Material.[MSL5]", "Location.[Location]"])
    df_ss_work_pa = df_ss_work_pa.merge(df_in_s_item, how='left', left_on=["Item Material.[Item Material]", "Location.[Location]"], right_on=["Item Material.[Item Material]", "Location.[Location]"])
    vdCommon.gfn_saveDf(df_ss_work_pa, "safety merge", True)

    df_ss_work_pa["ECP Flag"] = ""
    df_ss_work_pa["Source"] = ""

    df_ss_work_pa["ECP Flag"] = df_ss_work_pa["SS Mtrl L3_ECP Flag"]
    df_ss_work_pa.loc[(df_ss_work_pa["SS Mtrl L4_ECP Flag"].notna()), "ECP Flag"] = df_ss_work_pa["SS Mtrl L4_ECP Flag"]
    df_ss_work_pa.loc[(df_ss_work_pa["SS Mtrl L5_ECP Flag"].notna()), "ECP Flag"] = df_ss_work_pa["SS Mtrl L5_ECP Flag"]
    df_ss_work_pa.loc[(df_ss_work_pa["SS Mtrl Item_ECP Flag"].notna()), "ECP Flag"] = df_ss_work_pa["SS Mtrl Item_ECP Flag"]
    df_ss_work_pa["Source"] = df_ss_work_pa["SS Mtrl L3_Source"]
    df_ss_work_pa.loc[(df_ss_work_pa["SS Mtrl L4_Source"].notna()), "Source"] = df_ss_work_pa["SS Mtrl L4_Source"]
    df_ss_work_pa.loc[(df_ss_work_pa["SS Mtrl L5_Source"].notna()), "Source"] = df_ss_work_pa["SS Mtrl L5_Source"]
    df_ss_work_pa.loc[(df_ss_work_pa["SS Mtrl Item_Source"].notna()), "Source"] = df_ss_work_pa["SS Mtrl Item_Source"]
    vdCommon.gfn_saveDf(df_ss_work_pa, "safety calc", True)

    df_ss_work_pa["All Cnt"] = 1
    df_ss_work_pa["ECP Flag On Cnt"] = 0
    df_ss_work_pa["ECP Flag Off Cnt"] = 0
    df_ss_work_pa["Source NSCM Cnt"] = 0
    df_ss_work_pa["Source ERP Cnt"] = 0
    df_ss_work_pa.loc[(df_ss_work_pa["ECP Flag"] == "on"), "ECP Flag On Cnt"] = 1
    df_ss_work_pa.loc[(df_ss_work_pa["ECP Flag"] != "on"), "ECP Flag Off Cnt"] = 1
    df_ss_work_pa.loc[(df_ss_work_pa["Source"] == "NSCM"), "Source NSCM Cnt"] = 1
    df_ss_work_pa.loc[(df_ss_work_pa["Source"] == "ERP"), "Source ERP Cnt"] = 1

    df_ss_groupby_pa = df_ss_work_pa.groupby(["Item Material.[MSL5]", "Item Material.[Item Material]"],
            as_index=False)[["All Cnt", "ECP Flag On Cnt", "ECP Flag Off Cnt", "Source NSCM Cnt", "Source ERP Cnt"]].sum()

    df_ss_groupby_pa["Valid Mtrl MSL5_SS ECP On Only_Cnt"] = 0
    df_ss_groupby_pa["Valid Mtrl MSL5_SS ECP Off Only_Cnt"] = 0
    df_ss_groupby_pa["Valid Mtrl MSL5_SS ECP Mixed_Cnt"] = 0
    df_ss_groupby_pa["Valid Mtrl MSL5_SS Source ERP Only_Cnt"] = 0
    df_ss_groupby_pa["Valid Mtrl MSL5_SS Source NSCM Only_Cnt"] = 0
    df_ss_groupby_pa["Valid Mtrl MSL5_SS Source Mixed_Cnt"] = 0
    df_ss_groupby_pa.loc[(df_ss_groupby_pa["All Cnt"] == df_ss_groupby_pa["ECP Flag On Cnt"]), "Valid Mtrl MSL5_SS ECP On Only_Cnt"] = 1
    df_ss_groupby_pa.loc[(df_ss_groupby_pa["All Cnt"] == df_ss_groupby_pa["ECP Flag Off Cnt"]), "Valid Mtrl MSL5_SS ECP Off Only_Cnt"] = 1
    df_ss_groupby_pa.loc[(df_ss_groupby_pa["ECP Flag On Cnt"] > 0) & (df_ss_groupby_pa["ECP Flag Off Cnt"] > 0), "Valid Mtrl MSL5_SS ECP Mixed_Cnt"] = 1
    df_ss_groupby_pa.loc[(df_ss_groupby_pa["All Cnt"] == df_ss_groupby_pa["Source ERP Cnt"]), "Valid Mtrl MSL5_SS Source ERP Only_Cnt"] = 1
    df_ss_groupby_pa.loc[(df_ss_groupby_pa["All Cnt"] == df_ss_groupby_pa["Source NSCM Cnt"]), "Valid Mtrl MSL5_SS Source NSCM Only_Cnt"] = 1
    df_ss_groupby_pa.loc[(df_ss_groupby_pa["Source NSCM Cnt"] > 0) & (df_ss_groupby_pa["Source ERP Cnt"] > 0), "Valid Mtrl MSL5_SS Source Mixed_Cnt"] = 1
    vdCommon.gfn_saveDf(df_ss_groupby_pa, "safety groupby", True)

    df_ss_groupby_pa.drop(["All Cnt", "ECP Flag On Cnt", "ECP Flag Off Cnt", "Source NSCM Cnt", "Source ERP Cnt"], axis=1, inplace=True)

    ####################################################################################################################
    # Matl BOD
    ####################################################################################################################
    df_mb_work_pa = df_in_pa.copy()

    df_in_mb_lv3.rename(columns={"Location.[Location]": "Chg Location.[Chg Location]", "Sub Location.[Sub Location]": "Location.[Location]"}, inplace=True)
    df_in_mb_lv3_w.rename(columns={"Location.[Location]": "Chg Location.[Chg Location]", "Sub Location.[Sub Location]": "Location.[Location]"}, inplace=True)
    df_in_mb_item_w.rename(columns={"Location.[Location]": "Chg Location.[Chg Location]", "Sub Location.[Sub Location]": "Location.[Location]"}, inplace=True)

    # 전체를 합친다.
    df_mb_work_pa = df_mb_work_pa.merge(df_in_mb_lv3, how='inner', left_on=["Item Material.[MSL3]", "Location.[Location]"], right_on=["Item Material.[MSL3]", "Location.[Location]"])
    df_mb_work_pa = df_mb_work_pa.merge(df_in_mb_lv3_w, how='left',
            left_on=["Item Material.[MSL3]", "Location.[Location]", "Chg Location.[Chg Location]", "Trans Mode.[Trans Mode]"],
            right_on=["Item Material.[MSL3]", "Location.[Location]", "Chg Location.[Chg Location]", "Trans Mode.[Trans Mode]"])
    df_mb_work_pa = df_mb_work_pa.merge(df_in_mb_item_w, how='left',
            left_on=["Item Material.[Item Material]", "Location.[Location]", "Time.[Week]", "Chg Location.[Chg Location]", "Trans Mode.[Trans Mode]"],
            right_on=["Item Material.[Item Material]", "Location.[Location]", "Time.[Week]", "Chg Location.[Chg Location]", "Trans Mode.[Trans Mode]"])

    # Intransit LT 를 찾는다.
    df_mb_work_pa["Intransit LT"] = df_mb_work_pa["BOD List Mtrl W_Intransit LT"]
    df_mb_work_pa.loc[~np.isnan(df_mb_work_pa["BOD Item Mtrl W_Intransit LT"]), "Intransit LT"] = df_mb_work_pa["BOD Item Mtrl W_Intransit LT"]
    df_mb_work_pa["Intransit LT"].fillna(value=0, inplace=True)
    vdCommon.gfn_saveDf(df_mb_work_pa, "Matl BOD calc", True)

    # 키로 Groupby를 해서 week 가 다 있는지, LT가 0보다 큰지를 체크한다.
    df_mb_work_pa.loc[(df_mb_work_pa["Intransit LT"] > 0), "LT Cnt"] = 1
    df_mb_work_pa["Cnt"] = 1
    df_mb_work_pa = df_mb_work_pa.groupby(["Item Material.[MSL5]", "Item Material.[Item Material]", "Location.[Location]", "Time.[Week]", "Chg Location.[Chg Location]", "Trans Mode.[Trans Mode]"], as_index=False)[["LT Cnt", "Cnt"]].sum()
    df_mb_work_pa["DF_Cnt"] = 0
    df_mb_work_pa["UNDF_Cnt"] = 0
    week_cnt = len(df_in_week.index)
    df_mb_work_pa.loc[((df_mb_work_pa["Cnt"] == week_cnt) & (df_mb_work_pa["LT Cnt"] > 0)), "DF_Cnt"] = 1
    df_mb_work_pa.loc[(df_mb_work_pa["DF_Cnt"] != 1), "UNDF_Cnt"] = 1
    vdCommon.gfn_saveDf(df_mb_work_pa, "Matl BOD groupby", True)

    df_mb_work_pa = df_mb_work_pa.groupby(["Item Material.[MSL5]", "Item Material.[Item Material]"], as_index=False)[["DF_Cnt", "UNDF_Cnt"]].sum()
    df_mb_work_pa["Valid Mtrl MSL5_BOD DF_Cnt"] = 0
    df_mb_work_pa["Valid Mtrl MSL5_BOD UNDF_Cnt"] = 0
    df_mb_work_pa.loc[(df_mb_work_pa["UNDF_Cnt"] > 0), "Valid Mtrl MSL5_BOD UNDF_Cnt"] = 1
    df_mb_work_pa.loc[(df_mb_work_pa["UNDF_Cnt"] == 0), "Valid Mtrl MSL5_BOD DF_Cnt"] = 1
    vdCommon.gfn_saveDf(df_mb_work_pa, "Matl BOD Item groupby", True)

    ####################################################################################################################
    # 모수를 만든다.
    ####################################################################################################################
    df_m1 = df_in_ct[["Item Material.[MSL5]", "Item Material.[Item Material]"]].copy()
    df_m2 = df_in_lu[["Item Material.[MSL5]", "Item Material.[Item Material]"]].copy()
    df_m3 = df_in_v[["Item Material.[MSL5]", "Item Material.[Item Material]"]].copy()
    df_m4 = df_ss_groupby_pa[["Item Material.[MSL5]", "Item Material.[Item Material]"]].copy()
    df_m5 = df_mb_work_pa[["Item Material.[MSL5]", "Item Material.[Item Material]"]].copy()

    df_m = pd.concat([df_m1, df_m2, df_m3, df_m4, df_m5]).reset_index(drop=True)
    df_m.drop_duplicates(inplace=True)

    df_in_ct.drop(["Item Material.[MSL5]"], axis=1, inplace=True)
    df_in_lu.drop(["Item Material.[MSL5]"], axis=1, inplace=True)
    df_in_v.drop(["Item Material.[MSL5]"], axis=1, inplace=True)
    df_ss_groupby_pa.drop(["Item Material.[MSL5]"], axis=1, inplace=True)
    df_mb_work_pa.drop(["Item Material.[MSL5]"], axis=1, inplace=True)

    # 전체 Merge 한다.
    df_m = df_m.merge(df_in_ct, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_m = df_m.merge(df_in_lu, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_m = df_m.merge(df_in_v, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_m = df_m.merge(df_ss_groupby_pa, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_m = df_m.merge(df_mb_work_pa, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    vdCommon.gfn_saveDf(df_m, "full merge", True)

    # 0으로 초기화
    df_m["Valid Mtrl MSL5_Logisitc Pallet_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Logisitc 20FT_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Logisitc 40FT_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Logisitc 40FTHC_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Const TimeVarying_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Const Hard_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Const Soft_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Const Un_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Const Plant ECP_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Vendor(HQ) UNDF_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Vendor(HQ) Single_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Vendor(HQ) Multi_Cnt"] = 0
    df_m["Valid Mtrl MSL5_Const Plant ECP_Cnt"] = 0

    df_m["Valid Mtrl MSL5_BOD UNDF_Cnt"].fillna(value=0, inplace=True)
    df_m["Valid Mtrl MSL5_BOD DF_Cnt"].fillna(value=0, inplace=True)

    # 대상을 1로 세팅
    df_m.loc[(df_m["Mtrl Attr_Pallet"].notna()), "Valid Mtrl MSL5_Logisitc Pallet_Cnt"] = 1
    df_m.loc[(df_m["Mtrl Attr_20FT"].notna()), "Valid Mtrl MSL5_Logisitc 20FT_Cnt"] = 1
    df_m.loc[(df_m["Mtrl Attr_40FT"].notna()), "Valid Mtrl MSL5_Logisitc 40FT_Cnt"] = 1
    df_m.loc[(df_m["Mtrl Attr_40FT HC"].notna()), "Valid Mtrl MSL5_Logisitc 40FTHC_Cnt"] = 1
    df_m.loc[(df_m["Valid Mtrl Item_Const Time Varying"] == "Y"), "Valid Mtrl MSL5_Const TimeVarying_Cnt"] = 1
    df_m.loc[(df_m["Valid Mtrl Item_Const Current"] == "Hard"), "Valid Mtrl MSL5_Const Hard_Cnt"] = 1
    df_m.loc[(df_m["Valid Mtrl Item_Const Current"] == "Soft"), "Valid Mtrl MSL5_Const Soft_Cnt"] = 1
    df_m.loc[(df_m["Valid Mtrl Item_Const Current"] == "Un"), "Valid Mtrl MSL5_Const Un_Cnt"] = 1
    df_m.loc[(df_m["Valid Mtrl Item_Const Exception"] == "Y"), "Valid Mtrl MSL5_Const Plant ECP_Cnt"] = 1
    df_m["Item Material_C01_Ovr"].fillna(value="", inplace=True)
    df_m.loc[(df_m["Item Material_C01_Ovr"] == "-"), "Valid Mtrl MSL5_Vendor(HQ) UNDF_Cnt"] = 1
    df_m.loc[(df_m["Item Material_C01_Ovr"].str.startswith("Multi")), "Valid Mtrl MSL5_Vendor(HQ) Multi_Cnt"] = 1
    df_m.loc[((df_m["Valid Mtrl MSL5_Vendor(HQ) UNDF_Cnt"] == 0) & (df_m["Valid Mtrl MSL5_Vendor(HQ) Multi_Cnt"] == 0)), "Valid Mtrl MSL5_Vendor(HQ) Single_Cnt"] = 1
    vdCommon.gfn_saveDf(df_m, "find cnt", True)

    df_groupby = df_m.groupby(["Item Material.[MSL5]"], as_index=False)[[
            "Valid Mtrl MSL5_Logisitc Pallet_Cnt", "Valid Mtrl MSL5_Logisitc 20FT_Cnt", "Valid Mtrl MSL5_Logisitc 40FT_Cnt",
            "Valid Mtrl MSL5_Logisitc 40FTHC_Cnt", "Valid Mtrl MSL5_Const TimeVarying_Cnt", "Valid Mtrl MSL5_Const Hard_Cnt",
            "Valid Mtrl MSL5_Const Soft_Cnt", "Valid Mtrl MSL5_Const Un_Cnt", "Valid Mtrl MSL5_Const Plant ECP_Cnt",
            "Valid Mtrl MSL5_Vendor(HQ) UNDF_Cnt", "Valid Mtrl MSL5_Vendor(HQ) Multi_Cnt", "Valid Mtrl MSL5_Vendor(HQ) Single_Cnt",
            "Valid Mtrl MSL5_SS Source ERP Only_Cnt", "Valid Mtrl MSL5_SS Source NSCM Only_Cnt", "Valid Mtrl MSL5_SS Source Mixed_Cnt",
            "Valid Mtrl MSL5_SS ECP On Only_Cnt", "Valid Mtrl MSL5_SS ECP Off Only_Cnt", "Valid Mtrl MSL5_SS ECP Mixed_Cnt",
            "Valid Mtrl MSL5_BOD UNDF_Cnt", "Valid Mtrl MSL5_BOD DF_Cnt"]].sum()
    vdCommon.gfn_saveDf(df_groupby, "groupby", True)

    # Frozen Period 의 max, min 값을 구한다.
    df_m["Valid Mtrl Item_Frozen Horizon Vendor"].fillna(value="0", inplace=True)
    df_m["Valid Mtrl Item_Frozen Horizon Vendor"] = df_m["Valid Mtrl Item_Frozen Horizon Vendor"].astype(float).astype(int)
    df_groupby_other = df_m.groupby(["Item Material.[MSL5]"], as_index=False).agg(
        Vendor_min = ("Valid Mtrl Item_Frozen Horizon Vendor", "min"),
        Vendor_max = ("Valid Mtrl Item_Frozen Horizon Vendor", "max"))
    df_groupby_other.rename(columns={"Vendor_min": "Valid Mtrl MSL5_Frozen Horizon_Min", "Vendor_max": "Valid Mtrl MSL5_Frozen Horizon_Max"}, inplace=True)
    vdCommon.gfn_saveDf(df_groupby_other, "groupby other", True)

    df_groupby = df_groupby.merge(df_groupby_other, how='left', left_on=["Item Material.[MSL5]"], right_on=["Item Material.[MSL5]"])

    df_out = df_groupby
    # version 추가
    df_out.insert(0, "Version.[Version Name]", paramOutVersion)

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

