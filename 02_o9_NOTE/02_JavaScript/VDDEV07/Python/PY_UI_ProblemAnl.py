"""
df_in_s : Select ( [Time].[Week] * [Demand].[DemandID] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Customer Group] * [Problem Type].[Problem Reason] * [Sequence].[Sequence] * [Problem Type].[Short Reason]) on row, ({ Measure.[Short Reason_Problem Resource], Measure.[Short Reason_Problem Qty], Measure.[Short Reason_Problem Item], Measure.[Short Reason_Problem Week] }) on column where { [Version].[Version Name] };
df_in_b : Select ( [Location].[Location] * [Item].[Item] * [Sequence].[Sequence] ) on row, ({ Measure.[BOD All_SET Site], Measure.[BOD All_SET Trans Time], Measure.[BOD All_SET Ship LT], Measure.[BOD All_SET Trans Mode], Measure.[BOD All_Hub Trans Time], Measure.[BOD All_Hub Ship LT], Measure.[BOD All_SET BOD Prty], Measure.[BOD All_SET BOD LT] }) on column where { [Version].[Version Name] };
df_in_r : Select ([Time].[Week] * [Item].[Product Group] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand].[DemandID] * [Demand Type].[Demand Type] ) on row, ({Measure.[W Demand Fulfilled Quantity], Measure.[W Demand Quantity To SCS]}) on column where { [Version].[Version Name] } ;
df_in_sp : Select ([Problem Type].[Short Reason] * [Problem Type].[Problem Category1] * [Problem Type].[Problem Category2] ) on row, ({Measure.[Problem Type_Priority]}) on column where { [Version].[Version Name] } ;
df_in_w : select (Time.[Day] * Time.[Day of Week] * Time.[Week]);

df_out
df_out2
df_out3

EXEC plugin instance [PY_UI_ProblemAnl]
for Measures {[Problem Anl_Short Qty]}
using scope (&CWVUI)
using arguments {(paramOutVersion, "CWV_MP"), (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

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
str_instance = 'PY_UI_ProblemAnl'

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
        df_in_s = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_s.csv", encoding="UTF-8")
        df_in_b = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_b.csv", encoding="UTF-8")
        df_in_r = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_r.csv", encoding="UTF-8")
        df_in_sp = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_sp.csv", encoding="UTF-8")
        df_in_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_w.csv", encoding="UTF-8")

        paramOutVersion = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_s, "in short", True)
    vdCommon.gfn_saveDf(df_in_b, "in bodall", True)
    vdCommon.gfn_saveDf(df_in_r, "in rtf", True)
    vdCommon.gfn_saveDf(df_in_sp, "in shortprty", True)
    vdCommon.gfn_saveDf(df_in_w, "in week", True)

    # 값을 입력 받아야 하는데 없어서 임의로 넣어줌
    df_in_sp["Problem Type.[Short Category]"] = "CAPA"
    
    # 주별 일요일을 구한다.
    df_in_w["idx"] = range(0, len(df_in_w))
    df_w_sun = df_in_w.loc[(df_in_w["Time.[Day of Week]"] == "SUN")].copy()
    df_w_sun.drop(columns=["Time.[Day of Week]"], axis=1, inplace=True)

    # TP Order 기준으로 정렬을 해서 한건만 가져온다.
    df_in_b.loc[((df_in_b["BOD All_SET Trans Mode"] == "TRUCK")), "TP Order"] = 1
    df_in_b.loc[((df_in_b["BOD All_SET Trans Mode"] == "VESSEL")), "TP Order"] = 2
    df_in_b.loc[((df_in_b["BOD All_SET Trans Mode"] == "AIR")), "TP Order"] = 3
    df_in_b.loc[((df_in_b["BOD All_SET Trans Mode"] == "VSLEXP")), "TP Order"] = 4
    df_in_b.loc[((df_in_b["BOD All_SET Trans Mode"] == "AIREX")), "TP Order"] = 5
    df_in_b['TP Order Rank'] = df_in_b.groupby(["Location.[Location]", "Item.[Item]"])["TP Order"].rank(method="first", ascending=True)
    df_work_b = df_in_b.loc[(df_in_b["TP Order Rank"] == 1)].copy()
    vdCommon.gfn_saveDf(df_work_b, "bod filter", True)

    df_work_s = df_in_s[["Time.[Week]", "Demand.[DemandID]", "Item.[Item]", "Location.[Location]", "Sales Domain.[Customer Group]", "Problem Type.[Short Reason]", "Short Reason_Problem Week", "Short Reason_Problem Qty", "Short Reason_Problem Resource", "Short Reason_Problem Item"]].copy()
    vdCommon.gfn_saveDf(df_work_s, "short main", True)

    # rtf 계산
    df_work_r = df_in_r.copy()
    df_work_r["W Demand Quantity to SCS"].fillna(value=0, inplace=True)
    df_work_r["W Demand Fulfilled Quantity"].fillna(value=0, inplace=True)
    df_work_r["W Demand Short Quantity"] = df_work_r["W Demand Quantity to SCS"] - df_work_r["W Demand Fulfilled Quantity"]
    # 필요없는 컬럼 삭제
    df_work_r.drop(columns=["Time.[Week]", "Item.[Item]", "Location.[Location]", "Sales Domain.[Customer Group]", "Demand Type.[Demand Type]"], axis=1, inplace=True)

    df_work_s = df_work_s.merge(df_work_r, how='inner', left_on=["Demand.[DemandID]"], right_on=["Demand.[DemandID]"])
    df_work_s.drop(columns=["W Demand Fulfilled Quantity", "W Demand Quantity to SCS"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_work_s, "plus rtf", True)

    df_work_s = df_work_s.merge(df_work_b, how='inner', left_on=["Item.[Item]", "Location.[Location]"], right_on=["Item.[Item]", "Location.[Location]"])
    df_work_s = df_work_s.merge(df_w_sun, how='left', left_on=["Time.[Week]"], right_on=["Time.[Week]"])
    df_work_s["BOD All_SET Trans Time"].fillna(value=0, inplace=True)
    df_work_s["BOD All_SET Ship LT"].fillna(value=0, inplace=True)
    df_work_s["BOD All_Hub Trans Time"].fillna(value=0, inplace=True)
    df_work_s["BOD All_Hub Ship LT"].fillna(value=0, inplace=True)
    df_work_s["MFG Week Calc"] = 0 - df_work_s["BOD All_SET Trans Time"] - df_work_s["BOD All_SET Ship LT"] - df_work_s["BOD All_Hub Trans Time"] - df_work_s["BOD All_Hub Ship LT"]
    df_work_s["SOP Week Calc"] = 0 - df_work_s["BOD All_SET Trans Time"] - df_work_s["BOD All_Hub Trans Time"] - df_work_s["BOD All_Hub Ship LT"]
    df_work_s["MFG Week Idx"] = df_work_s["idx"] + df_work_s["MFG Week Calc"]
    df_work_s["SOP Week Idx"] = df_work_s["idx"] + df_work_s["SOP Week Calc"]
    df_work_s["MFG Week"] = df_work_s["MFG Week Idx"].apply(lambda idx: df_in_w.loc[int(idx), "Time.[Week]"])
    df_work_s["SOP Week"] = df_work_s["SOP Week Idx"].apply(lambda idx: df_in_w.loc[int(idx), "Time.[Week]"])
    vdCommon.gfn_saveDf(df_in_s, "plus bod", True)

    df_work_s = df_work_s.merge(df_in_sp, how='inner', left_on=["Problem Type.[Short Reason]"], right_on=["Problem Type.[Short Reason]"])
    df_work_s['Seq1.[Seq1]'] = df_work_s.groupby(["Demand.[DemandID]"])["Problem Type_Priority"].rank(method="first", ascending=False)
    # Demand.[DemandID] 로 rank 를 구할시 에러 발생 - Demand.[DemandID]_code 로 숫자형 데이타를 만들어서 rank를 구함
    df_work_s['Demand.[DemandID]_code'] = df_work_s['Demand.[DemandID]'].astype('category').cat.codes
    df_work_s['Seq2.[Seq2]'] = df_work_s.groupby(["Time.[Week]","Item.[Item]","Location.[Location]","Sales Domain.[Customer Group]"])["Demand.[DemandID]_code"].rank(method="first", ascending=False)
    vdCommon.gfn_saveDf(df_work_s, "plus short", True)

    df_out = df_work_s[["Time.[Week]","Item.[Item]","Location.[Location]","Sales Domain.[Customer Group]","Problem Type.[Short Reason]","Seq1.[Seq1]",
                        "Seq2.[Seq2]","Short Reason_Problem Week","BOD All_SET Site","Problem Type.[Problem Category1]","Problem Type.[Problem Category2]",
                        "W Demand Short Quantity","MFG Week","SOP Week","Short Reason_Problem Resource","Short Reason_Problem Qty","Short Reason_Problem Item"]].copy()
    df_out.rename(columns={"Location.[Location]": "Sub Location.[Sub Location]"}, inplace=True)
    df_out.rename(columns={"BOD All_SET Site": "Location.[Location]", "Short Reason_Problem Week" : "To Time.[To Week]",
                           "W Demand Short Quantity" : "Problem Anl_Short Qty", "Short Reason_Problem Resource" : "Problem Anl_Resouce Name",
                           "MFG Week" : "Problem Anl_MFG Week", "SOP Week" : "Problem Anl_SOP Week",
                           "Short Reason_Problem Qty" : "Problem Anl_Needed Qty", "Problem Type.[Problem Category1]" : "Problem Anl_Short Group",
                           "Problem Type.[Problem Category2]" : "Problem Anl_Short Type", "Short Reason_Problem Item" : "Problem Anl_Related Item"}, inplace=True)
    df_out.insert(0, "Version.[Version Name]", paramOutVersion)
    df_out['Seq1.[Seq1]'] = df_out['Seq1.[Seq1]'].astype(int)
    df_out['Seq2.[Seq2]'] = df_out['Seq2.[Seq2]'].astype(int)
    vdCommon.gfn_saveDf(df_out, 'df_out', True)

    ####################################################################################################
    ###################################### Problem List 데이타 생성 ######################################
    ####################################################################################################
    df_work2_r = df_in_r.merge(df_in_b, how='inner', left_on=["Item.[Item]", "Location.[Location]"], right_on=["Item.[Item]", "Location.[Location]"])
    df_work2_r["W Demand Short Quantity"] = df_work2_r["W Demand Quantity to SCS"] - df_work2_r["W Demand Fulfilled Quantity"]
    vdCommon.gfn_saveDf(df_work2_r, "work2 plus bod", True)

    df_work2_r['BOD All_SET BOD Prty Rank'] = df_work2_r.groupby(["Location.[Location]", "Item.[Item]"])["BOD All_SET BOD Prty"].rank(method="first", ascending=False)
    df_work2_r = df_work2_r.loc[(df_work2_r["BOD All_SET BOD Prty Rank"] == 1)].copy()
    vdCommon.gfn_saveDf(df_work2_r, "work2 bod rank filter", True)

    df_out2 = df_work2_r[["Time.[Week]","Item.[Item]","Location.[Location]","Sales Domain.[Customer Group]","BOD All_SET Site","BOD All_SET Trans Mode",
                        "W Demand Short Quantity","W Demand Quantity to SCS","W Demand Fulfilled Quantity"]].copy()
    df_out2.rename(columns={"Location.[Location]": "Sub Location.[Sub Location]"}, inplace=True)
    df_out2.rename(columns={"BOD All_SET Site" : "Location.[Location]", "BOD All_SET Trans Mode" : "Trans Mode.[Trans Mode]",
                            "W Demand Quantity to SCS" : "Problem List_DMD",
                            "W Demand Fulfilled Quantity" : "Problem List_RTF",
                            "W Demand Short Quantity" : "Problem List_DMD Short"}, inplace=True)
    df_out2.insert(0, "Version.[Version Name]", paramOutVersion)
    vdCommon.gfn_saveDf(df_out2, "df_out2", True)

    ####################################################################################################
    ###################################### Problem List Sub 데이타 생성 ######################################
    ####################################################################################################
    df_out3 = df_work2_r[["Time.[Week]","Item.[Product Group]","Location.[Location]","Sales Domain.[Customer Group]","BOD All_SET Site","BOD All_SET Trans Mode",
                        "BOD All_SET BOD LT"]].copy()
    df_out3.rename(columns={"Location.[Location]": "Sub Location.[Sub Location]"}, inplace=True)
    df_out3.rename(columns={"BOD All_SET Site" : "Location.[Location]", "BOD All_SET Trans Mode" : "Trans Mode.[Trans Mode]",
                           "BOD All_SET BOD LT" : "Problem List Sub_DMD LT", }, inplace=True)
    df_out3 = df_out3.groupby(["Item.[Product Group]","Location.[Location]","Sales Domain.[Customer Group]","Sub Location.[Sub Location]","Trans Mode.[Trans Mode]"], as_index=False)["Problem List Sub_DMD LT"].max()
    df_out3.insert(0, "Version.[Version Name]", paramOutVersion)
    vdCommon.gfn_saveDf(df_out3, "df_out3", True)

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




