"""
df_in_s_lv3_set : Select ( [Location].[Location] * [Item Material].[MSL3] ) on row, ({Measure.[SS Mtrl L3_Source], Measure.[SS Mtrl L3_Sub Set]}) on column where { [Version].[Version Name] };
df_in_s_lv3_w : Select ( [Location].[Location] * &MtrlValidiationWeek * [Item Material].[MSL3] ) on row, ( { Measure.[SS Mtrl L3 W_Time] } ) on column where { [Version].[Version Name] };
df_in_s_lv4_w : Select ( [Location].[Location] * &MtrlValidiationWeek * [Item Material].[MSL3] * [Item Material].[MSL4] ) on row, ( { Measure.[SS Mtrl L4 W_Time] } ) on column where { [Version].[Version Name] };
df_in_s_lv5_w : Select ( [Location].[Location] * &MtrlValidiationWeek * [Item Material].[MSL3] * [Item Material].[MSL5] ) on row, ( { Measure.[SS Mtrl L5 W_Time] } ) on column where { [Version].[Version Name] };
df_in_s_item_w : Select ( [Location].[Location] * &MtrlValidiationWeek * [Item Material].[Item Material] ) on row, ( { Measure.[SS Mtrl Item W_Time] } ) on column where { [Version].[Version Name] };

df_in_c_lv3 : Select ([Item Material].[MSL3] ) on row, ({Measure.[Mtrl Const Type L3_ETDETA], Measure.[Mtrl Const Type L3_Sub Set]}) on column where { [Version].[Version Name] };
df_in_c_lv3_w : Select ([Item Material].[MSL3] * &MtrlValidiationRelativeWeek ) on row, ({Measure.[Mtrl Const Type L3 W_Type]}) on column where { [Version].[Version Name] };
df_in_c_lv4 : Select ([Item Material].[MSL3] * [Item Material].[MSL4] ) on row, ({Measure.[Mtrl Const Type L4_ETDETA]}) on column where { [Version].[Version Name] };
df_in_c_lv4_w : Select ([Item Material].[MSL4] * &MtrlValidiationRelativeWeek ) on row, ({Measure.[Mtrl Const Type L4 W_Type]}) on column where { [Version].[Version Name] };
df_in_c_lv5 : Select ([Item Material].[MSL3] * [Item Material].[MSL5] ) on row, ({Measure.[Mtrl Const Type L5_ETDETA]}) on column where { [Version].[Version Name] };
df_in_c_lv5_w : Select ([Item Material].[MSL5] * &MtrlValidiationRelativeWeek ) on row, ({Measure.[Mtrl Const Type L5 W_Type]}) on column where { [Version].[Version Name] };
df_in_c_item : Select ([Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Item_ETDETA]}) on column where { [Version].[Version Name] };
df_in_c_item_w : Select ([Location].[Location] * [Item Material].[Item Material] * &MtrlValidiationRelativeWeek ) on row, ({Measure.[Mtrl Const Type Item W_Type]}) on column where { [Version].[Version Name] };

df_in_m_lv3 : Select ([Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl_EFF Startdate], Measure.[Dummy]}) on column where { [Version].[Version Name] } ;
df_in_m_lv3_w : Select ([Location].[Location] * &MtrlValidiationWeek * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD List Mtrl W_Intransit LT]}) on column where { [Version].[Version Name] } ;
df_in_m_item : Select ([Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl_EFF Startdate], Measure.[Dummy]}) on column where { [Version].[Version Name] } ;
df_in_m_item_w : Select ([Location].[Location] * &MtrlValidiationWeek * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, ({Measure.[BOD Item Mtrl W_Intransit LT]}) on column where { [Version].[Version Name] } ;

df_in_pa : Select ([Location].[Location] * [Item Material].[MSL3] * [Item Material].[MSL4] * [Item Material].[MSL5] * [Item Material].[Item Material]) on row, ( { Measure.[Item Mtrl Site Asn_Cur Status] } ) on column where { [Version].[Version Name], Measure.[Item Mtrl Site Asn_Cur Status] in {"PLANNED", "ACTIVE"} };
df_in_week : select (&MPHroizon);

df_out :

EXEC plugin instance [PY_UI_Dashboard_MaterialPlant]
for measures {[Valid Mtrl Item Plant_SS]}
using scope ( &CWVUI )
using arguments {(paramOutVersion, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


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
str_instance = 'PY_UI_Dashboard_MaterialPlant'

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

# def fn_s_find_week(row):
#     l3 = row["SS Mtrl L3 W_Time"]
#     l4 = row["SS Mtrl L4 W_Time"]
#     l5 = row["SS Mtrl L5 W_Time"]
#     item = row["SS Mtrl Item W_Time"]
#
#     w_time = 0
#
#     if ~np.isnan(item):
#         w_time = item
#     elif ~np.isnan(l5):
#         w_time = l5
#     elif ~np.isnan(l4):
#         w_time = l4
#     else:
#         w_time = l3
#
#     return [w_time]

# def fn_c_find_week(row):
#     l3_type = gfn_get_str(row["Mtrl Const Type L3 W_Type"])
#     l4_type = gfn_get_str(row["Mtrl Const Type L4 W_Type"])
#     l5_type = gfn_get_str(row["Mtrl Const Type L5 W_Type"])
#     item_type = gfn_get_str(row["Mtrl Const Type Item W_Type"])
#
#     l3_etdeta = gfn_get_str(row["Mtrl Const Type L3_ETDETA"])
#     l4_etdeta = gfn_get_str(row["Mtrl Const Type L4_ETDETA"])
#     l5_etdeta = gfn_get_str(row["Mtrl Const Type L5_ETDETA"])
#     item_etdeta = gfn_get_str(row["Mtrl Const Type Item_ETDETA"])
#
#     w_type = ""
#     w_etdeta = ""
#
#     if item_etdeta != "":
#         w_type = item_type
#         w_etdeta = item_etdeta
#     elif l5_etdeta != "":
#         w_type = l5_type
#         w_etdeta = l5_etdeta
#     elif l4_etdeta != "":
#         w_type = l4_type
#         w_etdeta = l4_etdeta
#     else:
#         w_type = l3_type
#         w_etdeta = l3_etdeta
#
#     # print(l3_type + " : " + l4_type + " : " + l5_type + " : " + item_type + " : " + l3_etdeta + " : " + l4_etdeta + " : " + l5_etdeta + " : " + item_etdeta + " : " + w_type + " : " + w_etdeta)
#
#     return [w_etdeta, w_type]

# def fn_m_find_week(row):
#     l3 = row["BOD List Mtrl W_Intransit LT"]
#     item = row["BOD Item Mtrl W_Intransit LT"]
#
#     w_time = 0
#
#     if ~np.isnan(item):
#         w_time = item
#     else:
#         w_time = l3
#
#     return [w_time]

def fn_measure_name(data):
    category = ""
    if data == "AIR":
        category = "Valid Mtrl Item Plant_BOD LT AIR"
    elif data == "AIREX":
        category = "Valid Mtrl Item Plant_BOD LT AIREX"
    elif data == "TRUCK":
        category = "Valid Mtrl Item Plant_BOD LT Truck"
    elif data == "VESSEL":
        category = "Valid Mtrl Item Plant_BOD LT VSL"
    elif data == "VSLEXP":
        category = "Valid Mtrl Item Plant_BOD LT VSLEXP"

    return category

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_s_lv3_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv3_w.csv", encoding="UTF-8")
        df_in_s_lv4_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv4_w.csv", encoding="UTF-8")
        df_in_s_lv5_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv5_w.csv", encoding="UTF-8")
        df_in_s_item_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_item_w.csv", encoding="UTF-8")
        df_in_s_lv3_set = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s_lv3_set.csv", encoding="UTF-8")
        df_in_c_lv3 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv3.csv", encoding="UTF-8")
        df_in_c_lv3_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv3_w.csv", encoding="UTF-8")
        df_in_c_lv4 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv4.csv", encoding="UTF-8")
        df_in_c_lv4_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv4_w.csv", encoding="UTF-8")
        df_in_c_lv5 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv5.csv", encoding="UTF-8")
        df_in_c_lv5_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv5_w.csv", encoding="UTF-8")
        df_in_c_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_item.csv", encoding="UTF-8")
        df_in_c_item_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_item_w.csv", encoding="UTF-8")
        df_in_m_lv3 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_m_lv3.csv", encoding="UTF-8")
        df_in_m_lv3_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_m_lv3_w.csv", encoding="UTF-8")
        df_in_m_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_m_item.csv", encoding="UTF-8")
        df_in_m_item_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_m_item_w.csv", encoding="UTF-8")
        df_in_pa = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_pa.csv", encoding="UTF-8")
        df_in_week = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_week.csv", encoding="UTF-8")

        paramOutVersion = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_s_lv3_set, "df_in_s_lv3_set", True)
    vdCommon.gfn_saveDf(df_in_s_lv3_w, "df_in_s_lv3_w", True)
    vdCommon.gfn_saveDf(df_in_s_lv4_w, "df_in_s_lv4_w", True)
    vdCommon.gfn_saveDf(df_in_s_lv5_w, "df_in_s_lv5_w", True)
    vdCommon.gfn_saveDf(df_in_s_item_w, "df_in_s_item_w", True)
    vdCommon.gfn_saveDf(df_in_c_lv3, "df_in_c_lv3", True)
    vdCommon.gfn_saveDf(df_in_c_lv3_w, "df_in_c_lv3_w", True)
    vdCommon.gfn_saveDf(df_in_c_lv4, "df_in_c_lv4", True)
    vdCommon.gfn_saveDf(df_in_c_lv4_w, "df_in_c_lv4_w", True)
    vdCommon.gfn_saveDf(df_in_c_lv5, "df_in_c_lv5", True)
    vdCommon.gfn_saveDf(df_in_c_lv5_w, "df_in_c_lv5_w", True)
    vdCommon.gfn_saveDf(df_in_c_item, "df_in_c_item", True)
    vdCommon.gfn_saveDf(df_in_c_item_w, "df_in_c_item_w", True)
    vdCommon.gfn_saveDf(df_in_m_lv3, "df_in_m_lv3", True)
    vdCommon.gfn_saveDf(df_in_m_lv3_w, "df_in_m_lv3_w", True)
    vdCommon.gfn_saveDf(df_in_m_item, "df_in_m_item", True)
    vdCommon.gfn_saveDf(df_in_m_item_w, "df_in_m_item_w", True)
    vdCommon.gfn_saveDf(df_in_pa, "df_in_pa", True)

    df_in_week["Relative Week.[Relative Week]"] = ""
    for idx in df_in_week.index:
        df_in_week.loc[idx, "Relative Week.[Relative Week]"] = "W" + gfn_lpad(idx + 1, 2)
    vdCommon.gfn_saveDf(df_in_week, "df_in_week", True)

    df_in_pa.drop(["Item Mtrl Site Asn_Cur Status"], axis=1, inplace=True)

    ####################################################################################################################
    # Safety Stock
    ####################################################################################################################
    # 4 Level 데이타를 구한다.
    df_in_s_lv4_w = df_in_s_lv4_w.merge(df_in_s_lv3_set, how='left', left_on=["Item Material.[MSL3]", "Location.[Location]"], right_on=["Item Material.[MSL3]", "Location.[Location]"])
    df_in_s_lv4_w = df_in_s_lv4_w.loc[(df_in_s_lv4_w["SS Mtrl L3_Sub Set"] == 'Lv4')].copy()
    df_in_s_lv4_w = df_in_s_lv4_w.drop(["SS Mtrl L3_Source", "SS Mtrl L3_Sub Set"], axis=1)
    vdCommon.gfn_saveDf(df_in_s_lv4_w, "lv4 Master", True)

    # 5 Level 데이타를 구한다.
    df_in_s_lv5_w = df_in_s_lv5_w.merge(df_in_s_lv3_set, how='left', left_on=["Item Material.[MSL3]", "Location.[Location]"], right_on=["Item Material.[MSL3]", "Location.[Location]"])
    df_in_s_lv5_w = df_in_s_lv5_w.loc[(df_in_s_lv5_w["SS Mtrl L3_Sub Set"] == 'Lv5')].copy()
    df_in_s_lv5_w = df_in_s_lv5_w.drop(["SS Mtrl L3_Source", "SS Mtrl L3_Sub Set"], axis=1)
    vdCommon.gfn_saveDf(df_in_s_lv5_w, "lv5 Master", True)

    df_s_work_pa = df_in_pa.copy()
    
    # lv3 이랑 merge 해서 대상만 뽑음
    df_s_work_pa = df_s_work_pa.merge(df_in_s_lv3_set, how='inner', left_on=["Item Material.[MSL3]", "Location.[Location]"], right_on=["Item Material.[MSL3]", "Location.[Location]"])
    df_s_work_pa.drop(["SS Mtrl L3_Source", "SS Mtrl L3_Sub Set"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_s_work_pa, "pa Master", True)

    # 전체를 합친다.
    df_in_s_lv4_w.drop(["Item Material.[MSL3]"], axis=1, inplace=True)
    df_in_s_lv5_w.drop(["Item Material.[MSL3]"], axis=1, inplace=True)
    df_s_work_pa = df_s_work_pa.merge(df_in_s_lv3_w, how='left', left_on=["Item Material.[MSL3]", "Location.[Location]"], right_on=["Item Material.[MSL3]", "Location.[Location]"])
    df_s_work_pa = df_s_work_pa.merge(df_in_s_lv4_w, how='left', left_on=["Item Material.[MSL4]", "Location.[Location]", "Time.[Week]"], right_on=["Item Material.[MSL4]", "Location.[Location]", "Time.[Week]"])
    df_s_work_pa = df_s_work_pa.merge(df_in_s_lv5_w, how='left', left_on=["Item Material.[MSL5]", "Location.[Location]", "Time.[Week]"], right_on=["Item Material.[MSL5]", "Location.[Location]", "Time.[Week]"])
    df_s_work_pa = df_s_work_pa.merge(df_in_s_item_w, how='left', left_on=["Item Material.[Item Material]", "Location.[Location]", "Time.[Week]"], right_on=["Item Material.[Item Material]", "Location.[Location]", "Time.[Week]"])
    df_s_work_pa["Result W"] = 0
    vdCommon.gfn_notelog("safety merge")

    # 맞는 주차 찾기
    # df_s_work_pa[["Result W"]] = df_s_work_pa.apply(lambda row: fn_s_find_week(row), axis=1, result_type='expand')
    df_s_work_pa["Result W"] = df_s_work_pa["SS Mtrl L3 W_Time"]
    df_s_work_pa.loc[~np.isnan(df_s_work_pa["SS Mtrl L4 W_Time"]), "Result W"] = df_s_work_pa["SS Mtrl L4 W_Time"]
    df_s_work_pa.loc[~np.isnan(df_s_work_pa["SS Mtrl L5 W_Time"]), "Result W"] = df_s_work_pa["SS Mtrl L5 W_Time"]
    df_s_work_pa.loc[~np.isnan(df_s_work_pa["SS Mtrl Item W_Time"]), "Result W"] = df_s_work_pa["SS Mtrl Item W_Time"]
    df_s_work_pa["Category"] = "Valid Mtrl Item Plant_SS"
    vdCommon.gfn_notelog("safety calc")

    vdCommon.gfn_saveDf(df_s_work_pa, "safety find week data", True)

    # 필요없는 컬럼 삭제
    df_s_work_pa.drop(["Item Material.[MSL3]", "Item Material.[MSL4]", "Item Material.[MSL5]", "SS Mtrl L3 W_Time", "SS Mtrl L4 W_Time", "SS Mtrl L5 W_Time", "SS Mtrl Item W_Time"], axis=1, inplace=True)
    # df_s_work_pa = df_s_work_pa[["Item Material.[Item Material]", "Location.[Location]", "Category", "Time.[Week]", "Result W"]].copy()

    ####################################################################################################################
    # Constraint Type
    ####################################################################################################################
    # 4 Level 데이타를 구한다.
    df_in_c_lv4 = df_in_c_lv4.merge(df_in_c_lv3, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_c_lv4 = df_in_c_lv4.merge(df_in_c_lv4_w, how='left', left_on=["Item Material.[MSL4]"], right_on=["Item Material.[MSL4]"])
    df_in_c_lv4 = df_in_c_lv4.loc[(df_in_c_lv4["Mtrl Const Type L3_Sub Set"] == 'LV4')].copy()
    df_in_c_lv4.drop(["Item Material.[MSL3]", "Mtrl Const Type L3_Sub Set", "Mtrl Const Type L3_ETDETA"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_in_c_lv4, "lv4 Master", True)

    # 5 Level 데이타를 구한다.
    df_in_c_lv5 = df_in_c_lv5.merge(df_in_c_lv3, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_c_lv5 = df_in_c_lv5.merge(df_in_c_lv5_w, how='left', left_on=["Item Material.[MSL5]"], right_on=["Item Material.[MSL5]"])
    df_in_c_lv5 = df_in_c_lv5.loc[(df_in_c_lv5["Mtrl Const Type L3_Sub Set"] == 'LV5')].copy()
    df_in_c_lv5.drop(["Item Material.[MSL3]", "Mtrl Const Type L3_Sub Set", "Mtrl Const Type L3_ETDETA"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_in_c_lv5, "lv5 Master", True)

    # Item 데이타를 구한다.
    df_in_c_item = df_in_c_item.merge(df_in_c_item_w, how='left', left_on=["Item Material.[Item Material]", "Location.[Location]"], right_on=["Item Material.[Item Material]", "Location.[Location]"])
    vdCommon.gfn_saveDf(df_in_c_item, "item Master", True)

    df_c_work_pa = df_in_pa.copy()

    # lv3 이랑 merge 해서 대상만 뽑음
    df_c_work_pa = df_c_work_pa.merge(df_in_c_lv3, how='inner', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_c_work_pa.drop(["Mtrl Const Type L3_Sub Set", "Mtrl Const Type L3_ETDETA"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_c_work_pa, "pa Master", True)

    # 전체를 합친다.
    df_c_work_pa = df_c_work_pa.merge(df_in_c_lv3, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_c_work_pa = df_c_work_pa.merge(df_in_c_lv3_w, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_c_work_pa.drop(["Mtrl Const Type L3_Sub Set"], axis=1, inplace=True)
    df_c_work_pa = df_c_work_pa.merge(df_in_c_lv4, how='left', left_on=["Item Material.[MSL4]", "Relative Week.[Relative Week]"], right_on=["Item Material.[MSL4]", "Relative Week.[Relative Week]"])
    df_c_work_pa = df_c_work_pa.merge(df_in_c_lv5, how='left', left_on=["Item Material.[MSL5]", "Relative Week.[Relative Week]"], right_on=["Item Material.[MSL5]", "Relative Week.[Relative Week]"])
    df_c_work_pa = df_c_work_pa.merge(df_in_c_item, how='left', left_on=["Item Material.[Item Material]", "Location.[Location]", "Relative Week.[Relative Week]"], right_on=["Item Material.[Item Material]", "Location.[Location]", "Relative Week.[Relative Week]"])
    df_c_work_pa = df_c_work_pa.merge(df_in_week, how='left', left_on=["Relative Week.[Relative Week]"], right_on=["Relative Week.[Relative Week]"])
    df_c_work_pa["Result W"] = ""
    vdCommon.gfn_notelog("constraint merge")

    # 맞는 주차 찾기
    # df_c_work_pa[["Result ETDETA", "Result W"]] = df_c_work_pa.apply(lambda row: fn_c_find_week(row), axis=1, result_type='expand')
    df_c_work_pa["Result W"] = df_c_work_pa["Mtrl Const Type L3 W_Type"]
    df_c_work_pa.loc[(df_c_work_pa["Mtrl Const Type L4 W_Type"].notna()), "Result W"] = df_c_work_pa["Mtrl Const Type L4 W_Type"]
    df_c_work_pa.loc[(df_c_work_pa["Mtrl Const Type L5 W_Type"].notna()), "Result W"] = df_c_work_pa["Mtrl Const Type L5 W_Type"]
    df_c_work_pa.loc[(df_c_work_pa["Mtrl Const Type Item W_Type"].notna()), "Result W"] = df_c_work_pa["Mtrl Const Type Item W_Type"]
    df_c_work_pa["Result ETDETA"] = df_c_work_pa["Mtrl Const Type L3_ETDETA"]
    df_c_work_pa.loc[(df_c_work_pa["Mtrl Const Type L4_ETDETA"].notna()), "Result ETDETA"] = df_c_work_pa["Mtrl Const Type L4_ETDETA"]
    df_c_work_pa.loc[(df_c_work_pa["Mtrl Const Type L5_ETDETA"].notna()), "Result ETDETA"] = df_c_work_pa["Mtrl Const Type L5_ETDETA"]
    df_c_work_pa.loc[(df_c_work_pa["Mtrl Const Type Item_ETDETA"].notna()), "Result ETDETA"] = df_c_work_pa["Mtrl Const Type Item_ETDETA"]
    df_c_work_pa["Category"] = df_c_work_pa["Result ETDETA"].apply(lambda data : "Valid Mtrl Item Plant_Constraint ETD" if data == "ETD" else "Valid Mtrl Item Plant_Constraint ETA VSL")
    vdCommon.gfn_notelog("constraint calc")

    vdCommon.gfn_saveDf(df_c_work_pa, "constraint find week data", True)

    # 필요없는 컬럼 삭제
    df_c_work_pa.drop(["Item Material.[MSL3]", "Item Material.[MSL4]", "Item Material.[MSL5]",
                       "Mtrl Const Type L3_ETDETA", "Mtrl Const Type L4_ETDETA", "Mtrl Const Type L5_ETDETA", "Mtrl Const Type Item_ETDETA",
                       "Mtrl Const Type L3 W_Type", "Mtrl Const Type L4 W_Type", "Mtrl Const Type L5 W_Type", "Mtrl Const Type Item W_Type",
                       "Relative Week.[Relative Week]", "Result ETDETA"], axis=1, inplace=True)
    # df_c_work_pa = df_c_work_pa[["Item Material.[Item Material]", "Location.[Location]", "Category", "Time.[Week]", "Result W"]].copy()

    ####################################################################################################################
    # Mtrl Bom
    ####################################################################################################################
    # df_in_m_lv3['rank'] = df_in_m_lv3.groupby(["Sub Location.[Sub Location]", "Item Material.[MSL3]", "Trans Mode.[Trans Mode]"])["Location.[Location]"].rank(method='first') => 스트링 컬럼을 rank 하면 서버에서 오류 발생
    df_in_m_lv3['temp_rank'] = df_in_m_lv3["Location.[Location]"].argsort().argsort() + 1
    df_in_m_lv3['rank'] = df_in_m_lv3.groupby(["Sub Location.[Sub Location]", "Item Material.[MSL3]", "Trans Mode.[Trans Mode]"])["temp_rank"].rank(method='first')
    df_in_m_lv3 = df_in_m_lv3.loc[((df_in_m_lv3["rank"] == 1)), ["Sub Location.[Sub Location]", "Item Material.[MSL3]", "Trans Mode.[Trans Mode]"]].copy()
    df_in_m_lv3.rename(columns={'Sub Location.[Sub Location]': 'Location.[Location]'}, inplace=True)
    vdCommon.gfn_saveDf(df_in_m_lv3, "lv3 remove dup", True)

    # df_in_m_item['rank'] = df_in_m_item.groupby(["Sub Location.[Sub Location]", "Item Material.[Item Material]", "Trans Mode.[Trans Mode]"])["Location.[Location]"].rank(method='first')
    df_in_m_item['temp_rank'] = df_in_m_item["Location.[Location]"].argsort().argsort() + 1
    df_in_m_item['rank'] = df_in_m_item.groupby(["Sub Location.[Sub Location]", "Item Material.[Item Material]", "Trans Mode.[Trans Mode]"])["temp_rank"].rank(method='first')
    df_in_m_item = df_in_m_item.loc[(df_in_m_item["rank"] == 1), ["Sub Location.[Sub Location]", "Item Material.[Item Material]", "Trans Mode.[Trans Mode]"]].copy()
    df_in_m_item.rename(columns={'Sub Location.[Sub Location]': 'Location.[Location]'}, inplace=True)
    vdCommon.gfn_saveDf(df_in_m_item, "item remove dup", True)

    df_in_m_lv3_w.drop(["Location.[Location]"], axis=1, inplace=True)
    df_in_m_lv3_w.rename(columns={'Sub Location.[Sub Location]': 'Location.[Location]'}, inplace=True)
    df_in_m_item_w.drop(["Location.[Location]"], axis=1, inplace=True)
    df_in_m_item_w.rename(columns={'Sub Location.[Sub Location]': 'Location.[Location]'}, inplace=True)

    df_m_work_pa = df_in_pa.copy()

    # 전체를 합친다.
    df_m_work_pa = df_m_work_pa.merge(df_in_m_lv3, how='inner', left_on=["Item Material.[MSL3]", "Location.[Location]"],
                                      right_on=["Item Material.[MSL3]", "Location.[Location]"])
    df_m_work_pa = df_m_work_pa.merge(df_in_m_lv3_w, how='left', left_on=["Item Material.[MSL3]", "Location.[Location]", "Trans Mode.[Trans Mode]"],
                                      right_on=["Item Material.[MSL3]", "Location.[Location]", "Trans Mode.[Trans Mode]"])
    df_m_work_pa = df_m_work_pa.merge(df_in_m_item, how='left', left_on=["Item Material.[Item Material]", "Location.[Location]", "Trans Mode.[Trans Mode]"],
                                      right_on=["Item Material.[Item Material]", "Location.[Location]", "Trans Mode.[Trans Mode]"])
    df_m_work_pa = df_m_work_pa.merge(df_in_m_item_w, how='left', left_on=["Item Material.[Item Material]", "Location.[Location]", "Trans Mode.[Trans Mode]", "Time.[Week]"],
                                      right_on=["Item Material.[Item Material]", "Location.[Location]", "Trans Mode.[Trans Mode]", "Time.[Week]"])
    df_m_work_pa["Result W"] = ""
    vdCommon.gfn_notelog("matl merge")

    # 맞는 주차 찾기
    # df_m_work_pa[["Result W"]] = df_m_work_pa.apply(lambda row: fn_m_find_week(row), axis=1, result_type='expand')
    df_m_work_pa["Result W"] = df_m_work_pa["BOD List Mtrl W_Intransit LT"]
    df_m_work_pa.loc[~np.isnan(df_m_work_pa["BOD Item Mtrl W_Intransit LT"]), "Result W"] = df_m_work_pa["BOD Item Mtrl W_Intransit LT"]
    df_m_work_pa["Category"] = df_m_work_pa["Trans Mode.[Trans Mode]"].apply(lambda data : fn_measure_name(data))
    vdCommon.gfn_notelog("matl calc")

    vdCommon.gfn_saveDf(df_m_work_pa, "matl find week data", True)

    # 필요없는 컬럼 삭제
    df_m_work_pa.drop(["Item Material.[MSL3]", "Item Material.[MSL4]", "Item Material.[MSL5]",
                       "Trans Mode.[Trans Mode]", "BOD List Mtrl W_Intransit LT", "BOD Item Mtrl W_Intransit LT"], axis=1, inplace=True)

    df_concat = pd.concat([df_s_work_pa, df_c_work_pa, df_m_work_pa]).reset_index(drop=True)
    vdCommon.gfn_saveDf(df_concat, "df_concat", True)

    # pivot 을 한다.
    df_out = df_concat.pivot_table(index=["Item Material.[Item Material]", "Location.[Location]", "Time.[Week]"], columns="Category", values="Result W", aggfunc="max").reset_index()
    # version 추가
    df_out.insert(0, "Version.[Version Name]", paramOutVersion)
    df_out["Time.[Week]"] = df_out["Time.[Week]"].astype(int).astype(str)
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

