"""
df_in_itemMaterialOrg : Select ([Item Material].[Item Material] ) on row, ({Measure.[Item Material_MSL1_Apply], Measure.[Item Material_MSL2_Apply], Measure.[Item Material_MSL3_Apply], Measure.[Item Material_MSL4_Apply], Measure.[Item Material_MSL5_Apply], Measure.[Item Material_MSL1_Display], Measure.[Item Material_MSL2_Display], Measure.[Item Material_MSL3_Display], Measure.[Item Material_MSL4_Display], Measure.[Item Material_MSL5_Display], Measure.[Item Material_MSL1_Order], Measure.[Item Material_MSL2_Order], Measure.[Item Material_MSL3_Order], Measure.[Item Material_MSL4_Order], Measure.[Item Material_MSL5_Order], Measure.[Item Material_C01_Apply], Measure.[Item Material_C02_Apply], Measure.[Item Material_C03_Apply], Measure.[Item Material_C04_Apply], Measure.[Item Material_C05_Apply], Measure.[Item Material_C06_Apply], Measure.[Item Material_C07_Apply], Measure.[Item Material_C08_Apply], Measure.[Item Material_C09_Apply], Measure.[Item Material_C10_Apply], Measure.[Item Material_S01_Apply], Measure.[Item Material_S02_Apply], Measure.[Item Material_S03_Apply], Measure.[Item Material_S04_Apply], Measure.[Item Material_S05_Apply], Measure.[Item Material_S06_Apply], Measure.[Item Material_S07_Apply], Measure.[Item Material_S08_Apply], Measure.[Item Material_S09_Apply], Measure.[Item Material_S10_Apply], Measure.[Item Material_S11_Apply], Measure.[Item Material_S12_Apply], Measure.[Item Material_S13_Apply], Measure.[Item Material_S14_Apply], Measure.[Item Material_S15_Apply], Measure.[Item Material_Const Type], Measure.[Item Material_Rule No], Measure.[Item Material_MSL Group ID]}) on column where { [Version].[Version Name] };
df_in_rule : Select ([Rule].[Rule No] * [Group].[Group ID] * [Hrcy Type].[Hrcy Type] ) on row, ({Measure.[Mtrl Hrchy Map Rule_Code], Measure.[Mtrl Hrchy Map Rule_Desc], Measure.[Mtrl Hrchy Map Rule_Long Desc], Measure.[Mtrl Hrchy Map Rule_Grp], Measure.[Mtrl Hrchy Map Rule_Priority]}) on column where { [Version].[Version Name] };

pDetailLogFlag = "N"

EXEC plugin instance [PY_UI_ItemMaterialOrder]
for measures {[Item Material_MSL1]}
using scope ( &CWVUI )
using arguments {(RunID, "Run_1"), (outVersionName, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


* 2025.09.30 : MSL 정렬 기준을 정한다.
* 2025.12.04 : "Completed Panel" 의 경우 "완Panel" 로 변경
* 2026.02.02 : Rule No 별로 갯수를 구하도록 수정
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
str_instance = 'PY_UI_ItemMaterialOrder'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

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
        df_in_itemMaterialOrg = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterialOrg.csv", encoding="UTF-8")
        df_in_rule = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_rule.csv", encoding="UTF-8")

        outVersionName = "CWV_MP"

    if common.gfn_get_isLocal() == False:
        vdCommon.gfn_saveDf(df_in_itemMaterialOrg, "df_in_itemMaterialOrg", True)
        vdCommon.gfn_saveDf(df_in_rule, "df_in_rule", True)

    df_out1 = df_in_itemMaterialOrg[["Item Material_MSL1_Apply", "Item Material_MSL1_Display", "Item Material_MSL1_Order"]].copy()
    df_out1 = df_out1.drop_duplicates()
    df_out1.rename(columns={"Item Material_MSL1_Apply" : "Item Material.[MSL1]",
                            "Item Material_MSL1_Display" : "Item Material MSL1_Display Alias",
                            "Item Material_MSL1_Order" : "Item Material MSL1_Sorting Order"}, inplace=True)
    vdCommon.gfn_saveDf(df_out1, "df_out1", True)

    df_out2 = df_in_itemMaterialOrg[["Item Material_MSL1_Apply", "Item Material_MSL2_Apply", "Item Material_MSL2_Display", "Item Material_MSL2_Order"]].copy()
    df_out2 = df_out2.drop_duplicates()
    # Order 조정
    df_out2['rank'] = df_out2["Item Material_MSL2_Display"].rank(method="dense")
    df_out2["Item Material_MSL2_Order"] = df_out2.apply(lambda row : int(float(row["Item Material_MSL2_Order"])) * 100 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out2 = df_out2.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out2.rename(columns={"Item Material_MSL2_Apply": "Item Material.[MSL2]",
                            "Item Material_MSL2_Display" : "Item Material MSL2_Display Alias",
                            "Item Material_MSL2_Order" : "Item Material MSL2_Sorting Order"}, inplace=True)
    vdCommon.gfn_saveDf(df_out2, "df_out2", True)

    df_out3 = df_in_itemMaterialOrg[["Item Material_MSL1_Apply", "Item Material_MSL3_Apply", "Item Material_MSL3_Display", "Item Material_MSL3_Order"]].copy()
    df_out3 = df_out3.drop_duplicates()
    # Order 조정
    df_out3['rank'] = df_out3["Item Material_MSL3_Display"].rank(method="dense")
    df_out3["Item Material_MSL3_Order"] = df_out3.apply(lambda row : int(float(row["Item Material_MSL3_Order"])) * 100 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out3 = df_out3.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out3.rename(columns={"Item Material_MSL3_Apply": "Item Material.[MSL3]",
                            "Item Material_MSL3_Display" : "Item Material MSL3_Display Alias",
                            "Item Material_MSL3_Order" : "Item Material MSL3_Sorting Order"}, inplace=True)
    # "Completed Panel" 의 경우 "완Panel" 로 변경
    df_out3["Item Material MSL3_Display Alias"] = df_out3["Item Material MSL3_Display Alias"].apply(lambda data : data.replace("Completed Panel", "완Panel"))
    vdCommon.gfn_saveDf(df_out3, "df_out3", True)

    df_out4 = df_in_itemMaterialOrg[["Item Material_MSL1_Apply", "Item Material_MSL4_Apply", "Item Material_MSL4_Display", "Item Material_MSL4_Order"]].copy()
    df_out4 = df_out4.drop_duplicates()
    # Order 조정
    df_out4['rank'] = df_out4["Item Material_MSL4_Display"].rank(method="dense")
    df_out4["Item Material_MSL4_Order"] = df_out4.apply(lambda row : int(float(row["Item Material_MSL4_Order"])) * 100 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out4 = df_out4.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out4.rename(columns={"Item Material_MSL4_Apply": "Item Material.[MSL4]",
                            "Item Material_MSL4_Display" : "Item Material MSL4_Display Alias",
                            "Item Material_MSL4_Order" : "Item Material MSL4_Sorting Order"}, inplace=True)
    vdCommon.gfn_saveDf(df_out4, "df_out4", True)

    df_out5 = df_in_itemMaterialOrg[["Item Material_MSL1_Apply", "Item Material_MSL5_Apply", "Item Material_MSL5_Display", "Item Material_MSL5_Order"]].copy()
    df_out5 = df_out5.drop_duplicates()
    # Order 조정
    df_out5['rank'] = df_out5["Item Material_MSL5_Display"].rank(method="dense")
    df_out5["Item Material_MSL5_Order"] = df_out5.apply(lambda row : int(float(row["Item Material_MSL5_Order"])) * 1000 if row["Item Material_MSL1_Apply"] != "Panel" else row["rank"], axis=1)
    df_out5 = df_out5.drop('Item Material_MSL1_Apply', axis=1).drop('rank', axis=1)
    # Rename
    df_out5.rename(columns={"Item Material_MSL5_Apply": "Item Material.[MSL5]",
                            "Item Material_MSL5_Display" : "Item Material MSL5_Display Alias",
                            "Item Material_MSL5_Order" : "Item Material MSL5_Sorting Order"}, inplace=True)
    vdCommon.gfn_saveDf(df_out5, "df_out5", True)

    # Rule No 별로 갯수를 구한다.
    df_out6 = df_in_rule[["Rule.[Rule No]", "Group.[Group ID]", "Hrcy Type.[Hrcy Type]"]]
    # 카운트 계산
    df_out6_w = df_in_itemMaterialOrg.groupby(["Item Material_MSL Group ID", "Item Material_Rule No"]).size().reset_index(name="Mtrl Hrchy Map Rule_Apply Count")
    df_out6_w.rename(columns={'Item Material_MSL Group ID': 'Group.[Group ID]'
                                ,'Item Material_Rule No': 'Rule.[Rule No]'}, inplace=True)
    df_out6 = df_out6.merge(df_out6_w, how='left', on=["Group.[Group ID]", "Rule.[Rule No]"])
    df_out6["Mtrl Hrchy Map Rule_Apply Count"].fillna(value=0, inplace=True)
    df_out6["Mtrl Hrchy Map Rule_Apply Count"] = df_out6["Mtrl Hrchy Map Rule_Apply Count"].astype(int)
    # 0000 형태로 변경
    df_out6["Rule.[Rule No]"] = df_out6["Rule.[Rule No]"].apply(lambda val : str(int(val)).rjust(4, "0"))
    vdCommon.gfn_saveDf(df_out6, "df_out6", True)

    # Version.[Version Name] 생성
    df_out1.insert(0, "Version.[Version Name]", outVersionName)
    df_out2.insert(0, "Version.[Version Name]", outVersionName)
    df_out3.insert(0, "Version.[Version Name]", outVersionName)
    df_out4.insert(0, "Version.[Version Name]", outVersionName)
    df_out5.insert(0, "Version.[Version Name]", outVersionName)
    df_out6.insert(0, "Version.[Version Name]", outVersionName)

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

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

