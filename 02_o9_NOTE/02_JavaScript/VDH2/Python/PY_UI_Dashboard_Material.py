"""
df_in_c_lv3 : Select ([Item Material].[MSL3] ) on row, ({Measure.[Mtrl Const Type L3_Time Varying Flag], Measure.[Mtrl Const Type L3_Sub Set]}) on column where { [Version].[Version Name] };
df_in_c_lv3_w : Select ([Item Material].[MSL3] * [Relative Week].[Relative Week].[W01] ) on row, ({Measure.[Mtrl Const Type L3 W_Type]}) on column where { [Version].[Version Name] };
df_in_c_lv4 : Select ([Item Material].[MSL3] * [Item Material].[MSL4] ) on row, ({Measure.[Mtrl Const Type L4_Time Varying Flag]}) on column where { [Version].[Version Name] };
df_in_c_lv4_w : Select ([Item Material].[MSL4] * [Relative Week].[Relative Week].[W01] ) on row, ({Measure.[Mtrl Const Type L4 W_Type]}) on column where { [Version].[Version Name] };
df_in_c_lv5 : Select ([Item Material].[MSL3] * [Item Material].[MSL5] ) on row, ({Measure.[Mtrl Const Type L5_Time Varying Flag]}) on column where { [Version].[Version Name] };
df_in_c_lv5_w : Select ([Item Material].[MSL5] * [Relative Week].[Relative Week].[W01] ) on row, ({Measure.[Mtrl Const Type L5 W_Type]}) on column where { [Version].[Version Name] };
df_in_c_item : Select ([Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Item_Time Varying Flag]}) on column where { [Version].[Version Name] };
df_in_c_item_w : Select ([Location].[Location] * [Item Material].[Item Material] * [Relative Week].[Relative Week].[W01] ) on row, ({Measure.[Mtrl Const Type Item W_Type]}) on column where { [Version].[Version Name] };

df_in_f_lv3_w : Select (&CurrentWeek * [Item Material].[MSL3] ) on row, ({Measure.[Supply Frozen Mtrl L3 W_Fix Range]}) on column where { [Version].[Version Name] };
df_in_f_lv5_w : (Select (&CurrentWeek * [Item Material].[MSL5] ) on row, ({Measure.[Supply Frozen Mtrl L5 W_Fix Range]}) on column where { [Version].[Version Name] }).filter(Measure.[Supply Frozen Mtrl L5_Valid]=="Y");
df_in_f_item_w : (Select (&CurrentWeek * [Item Material].[Item Material] * [Location].[Location] ) on row, ({Measure.[Supply Frozen Mtrl Item W_Fix Range]}) on column where { [Version].[Version Name] }).filter(Measure.[Supply Frozen Mtrl Item_Valid]=="Y");

df_in_cm : Select ( [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map_Source]}) on column where { [Version].[Version Name] };
df_in_cme : Select ( [Sequence].[Sequence] * [Item Material].[MSL5] ) on row, ({Measure.[Supply Plan Source Map Ecp_Mtrl Code], Measure.[Supply Plan Source Map Ecp_Source]}) on column where { [Version].[Version Name] };

df_in_pa : Select ([Location].[Location] * [Item Material].[MSL3] * [Item Material].[MSL4] * [Item Material].[MSL5] * [Item Material].[Item Material]) on row, ( { Measure.[Item Mtrl Site Asn_Cur Status] } ) on column where { [Version].[Version Name], Measure.[Item Mtrl Site Asn_Cur Status] in {"PLANNED", "ACTIVE"} };

df_out :

EXEC plugin instance [PY_UI_Dashboard_Material]
for measures {[Valid Mtrl Item_Const Time Varying]}
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
str_instance = 'PY_UI_Dashboard_Material'

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
        df_in_c_lv3 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv3.csv", encoding="UTF-8")
        df_in_c_lv3_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv3_w.csv", encoding="UTF-8")
        df_in_c_lv4 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv4.csv", encoding="UTF-8")
        df_in_c_lv4_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv4_w.csv", encoding="UTF-8")
        df_in_c_lv5 = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv5.csv", encoding="UTF-8")
        df_in_c_lv5_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_lv5_w.csv", encoding="UTF-8")
        df_in_c_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_item.csv", encoding="UTF-8")
        df_in_c_item_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_c_item_w.csv", encoding="UTF-8")

        df_in_f_lv3_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_f_lv3_w.csv", encoding="UTF-8")
        df_in_f_lv5_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_f_lv5_w.csv", encoding="UTF-8")
        df_in_f_item_w = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_f_item_w.csv", encoding="UTF-8")

        df_in_cm = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_cm.csv", encoding="UTF-8")
        df_in_cme = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_cme.csv", encoding="UTF-8")

        df_in_pa = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_pa.csv", encoding="UTF-8")

        paramOutVersion = "CWV_MP"

    vdCommon.gfn_saveDf(df_in_c_lv3, "df_in_c_lv3", True)
    vdCommon.gfn_saveDf(df_in_c_lv3_w, "df_in_c_lv3_w", True)
    vdCommon.gfn_saveDf(df_in_c_lv4, "df_in_c_lv4", True)
    vdCommon.gfn_saveDf(df_in_c_lv4_w, "df_in_c_lv4_w", True)
    vdCommon.gfn_saveDf(df_in_c_lv5, "df_in_c_lv5", True)
    vdCommon.gfn_saveDf(df_in_c_lv5_w, "df_in_c_lv5_w", True)
    vdCommon.gfn_saveDf(df_in_c_item, "df_in_c_item", True)
    vdCommon.gfn_saveDf(df_in_c_item_w, "df_in_c_item_w", True)
    vdCommon.gfn_saveDf(df_in_f_lv3_w, "df_in_f_lv3_w", True)
    vdCommon.gfn_saveDf(df_in_f_lv5_w, "df_in_f_lv5_w", True)
    vdCommon.gfn_saveDf(df_in_f_item_w, "df_in_f_item_w", True)
    vdCommon.gfn_saveDf(df_in_cm, "df_in_cm", True)
    vdCommon.gfn_saveDf(df_in_cme, "df_in_cme", True)
    vdCommon.gfn_saveDf(df_in_pa, "df_in_pa", True)

    # Item 별 데이타 생성
    df_in_pa.drop(["Location.[Location]", "Item Mtrl Site Asn_Cur Status"], axis=1, inplace=True)
    df_in_pa.drop_duplicates(inplace=True)
    vdCommon.gfn_saveDf(df_in_pa, "pa drop_duplicates", True)

    ####################################################################################################################
    # Constraint Type
    ####################################################################################################################
    # 4 Level 데이타를 구한다.(lv3 에 정의된)
    df_in_c_lv4 = df_in_c_lv4.merge(df_in_c_lv3, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_c_lv4 = df_in_c_lv4.merge(df_in_c_lv4_w, how='left', left_on=["Item Material.[MSL4]"], right_on=["Item Material.[MSL4]"])
    df_in_c_lv4 = df_in_c_lv4.loc[(df_in_c_lv4["Mtrl Const Type L3_Sub Set"] == 'LV4')].copy()
    df_in_c_lv4.drop(["Item Material.[MSL3]", "Mtrl Const Type L3_Sub Set", "Mtrl Const Type L3_Time Varying Flag", "Relative Week.[Relative Week]"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_in_c_lv4, "lv4 Master", True)

    # 5 Level 데이타를 구한다.(lv3 에 정의된)
    df_in_c_lv5 = df_in_c_lv5.merge(df_in_c_lv3, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_c_lv5 = df_in_c_lv5.merge(df_in_c_lv5_w, how='left', left_on=["Item Material.[MSL5]"], right_on=["Item Material.[MSL5]"])
    df_in_c_lv5 = df_in_c_lv5.loc[(df_in_c_lv5["Mtrl Const Type L3_Sub Set"] == 'LV5')].copy()
    df_in_c_lv5.drop(["Item Material.[MSL3]", "Mtrl Const Type L3_Sub Set", "Mtrl Const Type L3_Time Varying Flag", "Relative Week.[Relative Week]"], axis=1, inplace=True)
    vdCommon.gfn_saveDf(df_in_c_lv5, "lv5 Master", True)

    # Item 에서 Location 을 제외하고 정렬해서 1건만 가져온다. Time Varying : Y / N
    df_in_c_item.drop(["Location.[Location]"], axis=1, inplace=True)
    df_in_c_item.drop_duplicates(inplace=True)
    df_in_c_item["tRank"] = 1
    df_in_c_item.loc[(df_in_c_item["Mtrl Const Type Item_Time Varying Flag"] == "N"), "tRank"] = 2
    df_in_c_item['rank'] = df_in_c_item.groupby(["Item Material.[Item Material]"])["tRank"].rank(method='first')
    df_in_c_item = df_in_c_item.loc[(df_in_c_item["rank"] == 1), ["Item Material.[Item Material]", "Mtrl Const Type Item_Time Varying Flag"]].copy()
    vdCommon.gfn_saveDf(df_in_c_item, "item rank 1", True)

    # Item 에서 Location 을 제외하고 정렬해서 1건만 가져온다. Type : Hard, Soft, Un, -
    df_in_c_item_w.drop(["Location.[Location]"], axis=1, inplace=True)
    df_in_c_item_w.drop_duplicates(inplace=True)
    df_in_c_item_w["tRank"] = 4
    df_in_c_item_w.loc[(df_in_c_item_w["Mtrl Const Type Item W_Type"] == "Hard"), "tRank"] = 1
    df_in_c_item_w.loc[(df_in_c_item_w["Mtrl Const Type Item W_Type"] == "Soft"), "tRank"] = 2
    df_in_c_item_w.loc[(df_in_c_item_w["Mtrl Const Type Item W_Type"] == "Un"), "tRank"] = 3
    df_in_c_item_w['rank'] = df_in_c_item_w.groupby(["Item Material.[Item Material]"])["tRank"].rank(method='first')
    df_in_c_item_w = df_in_c_item_w.loc[(df_in_c_item_w["rank"] == 1), ["Item Material.[Item Material]", "Mtrl Const Type Item W_Type"]].copy()
    vdCommon.gfn_saveDf(df_in_c_item_w, "item_w rank 1", True)

    # 전체를 합친다.
    df_in_pa = df_in_pa.merge(df_in_c_lv3, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_pa = df_in_pa.merge(df_in_c_lv3_w, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_pa.drop(["Mtrl Const Type L3_Sub Set", "Relative Week.[Relative Week]"], axis=1, inplace=True)
    df_in_pa = df_in_pa.merge(df_in_c_lv4, how='left', left_on=["Item Material.[MSL4]"], right_on=["Item Material.[MSL4]"])
    df_in_pa = df_in_pa.merge(df_in_c_lv5, how='left', left_on=["Item Material.[MSL5]"], right_on=["Item Material.[MSL5]"])
    df_in_pa = df_in_pa.merge(df_in_c_item, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    df_in_pa = df_in_pa.merge(df_in_c_item_w, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    vdCommon.gfn_notelog("constraint merge")

    # 맞는 데이타 찾기
    # Valid Mtrl Item_Const Time Varying
    df_in_pa["Valid Mtrl Item_Const Time Varying"] = df_in_pa["Mtrl Const Type L3_Time Varying Flag"]
    df_in_pa.loc[(df_in_pa["Mtrl Const Type L4_Time Varying Flag"].notna()), "Valid Mtrl Item_Const Time Varying"] = df_in_pa["Mtrl Const Type L4_Time Varying Flag"]
    df_in_pa.loc[(df_in_pa["Mtrl Const Type L5_Time Varying Flag"].notna()), "Valid Mtrl Item_Const Time Varying"] = df_in_pa["Mtrl Const Type L5_Time Varying Flag"]
    df_in_pa.loc[(df_in_pa["Mtrl Const Type Item_Time Varying Flag"].notna()), "Valid Mtrl Item_Const Time Varying"] = df_in_pa["Mtrl Const Type Item_Time Varying Flag"]
    # Valid Mtrl Item_Const Current
    df_in_pa["Valid Mtrl Item_Const Current"] = df_in_pa["Mtrl Const Type L3 W_Type"]
    df_in_pa.loc[(df_in_pa["Mtrl Const Type L4 W_Type"].notna()), "Valid Mtrl Item_Const Current"] = df_in_pa["Mtrl Const Type L4 W_Type"]
    df_in_pa.loc[(df_in_pa["Mtrl Const Type L5 W_Type"].notna()), "Valid Mtrl Item_Const Current"] = df_in_pa["Mtrl Const Type L5 W_Type"]
    df_in_pa.loc[(df_in_pa["Mtrl Const Type Item W_Type"].notna()), "Valid Mtrl Item_Const Current"] = df_in_pa["Mtrl Const Type Item W_Type"]
    # Valid Mtrl Item_Const Exception
    df_in_pa["Valid Mtrl Item_Const Exception"] = "N"
    df_in_pa.loc[(df_in_pa["Mtrl Const Type L4 W_Type"].notna()), "Valid Mtrl Item_Const Exception"] = "Y"
    df_in_pa.loc[(df_in_pa["Mtrl Const Type L5 W_Type"].notna()), "Valid Mtrl Item_Const Exception"] = "Y"
    df_in_pa.loc[(df_in_pa["Mtrl Const Type Item W_Type"].notna()), "Valid Mtrl Item_Const Exception"] = "Y"
    vdCommon.gfn_notelog("constraint calc")

    vdCommon.gfn_saveDf(df_in_pa, "constraint find data", True)

    # 필요없는 컬럼 삭제
    df_in_pa.drop(["Mtrl Const Type L3_Time Varying Flag", "Mtrl Const Type L3 W_Type",
                           "Mtrl Const Type L4_Time Varying Flag", "Mtrl Const Type L4 W_Type",
                           "Mtrl Const Type L5_Time Varying Flag", "Mtrl Const Type L5 W_Type",
                           "Mtrl Const Type Item_Time Varying Flag", "Mtrl Const Type Item W_Type"], axis=1, inplace=True)

    ####################################################################################################################
    # Frozen Horizon (Week)
    ####################################################################################################################
    df_in_f_item_w['temp_rank'] = df_in_f_item_w["Location.[Location]"].rank(method='dense', ascending=True)
    df_in_f_item_w['rank'] = df_in_f_item_w.groupby(["Item Material.[Item Material]"])["temp_rank"].rank(method='first')
    df_in_f_item_w = df_in_f_item_w.loc[((df_in_f_item_w["rank"] == 1)), ["Item Material.[Item Material]", "Supply Frozen Mtrl Item W_Fix Range"]].copy()

    df_in_f_lv3_w.drop(["Time.[Week]"], axis=1, inplace=True)
    df_in_f_lv5_w.drop(["Time.[Week]"], axis=1, inplace=True)

    # 전체를 합친다.
    df_in_pa = df_in_pa.merge(df_in_f_lv3_w, how='left', left_on=["Item Material.[MSL3]"], right_on=["Item Material.[MSL3]"])
    df_in_pa = df_in_pa.merge(df_in_f_lv5_w, how='left', left_on=["Item Material.[MSL5]"], right_on=["Item Material.[MSL5]"])
    df_in_pa = df_in_pa.merge(df_in_f_item_w, how='left', left_on=["Item Material.[Item Material]"], right_on=["Item Material.[Item Material]"])
    vdCommon.gfn_notelog("Frozen merge")

    # 맞는 데이타 찾기
    df_in_pa["Valid Mtrl Item_Frozen Horizon Vendor"] = df_in_pa["Supply Frozen Mtrl L3 W_Fix Range"]
    df_in_pa.loc[(df_in_pa["Supply Frozen Mtrl L5 W_Fix Range"].notna()), "Valid Mtrl Item_Frozen Horizon Vendor"] = df_in_pa["Supply Frozen Mtrl L5 W_Fix Range"]
    df_in_pa.loc[(df_in_pa["Supply Frozen Mtrl Item W_Fix Range"].notna()), "Valid Mtrl Item_Frozen Horizon Vendor"] = df_in_pa["Supply Frozen Mtrl Item W_Fix Range"]
    df_in_pa.drop(["Supply Frozen Mtrl L3 W_Fix Range", "Supply Frozen Mtrl L5 W_Fix Range", "Supply Frozen Mtrl Item W_Fix Range"], axis=1, inplace=True)
    vdCommon.gfn_notelog("Frozen calc")

    vdCommon.gfn_saveDf(df_in_pa, "Frozen find data", True)

    ####################################################################################################################
    # Configuration Material
    ####################################################################################################################
    df_in_cme.drop(["Sequence.[Sequence]", "Item Material.[MSL5]"], axis=1, inplace=True)
    df_in_cme.drop_duplicates(inplace=True)
    df_work_cme = df_in_cme.groupby(["Supply Plan Source Map Ecp_Mtrl Code"])["Supply Plan Source Map Ecp_Source"].agg(lambda x: ','.join(set(x))).reset_index()
    vdCommon.gfn_saveDf(df_work_cme, "item agg", True)

    # 전체를 합친다.
    df_in_pa = df_in_pa.merge(df_in_cm, how='left', left_on=["Item Material.[MSL5]"], right_on=["Item Material.[MSL5]"])
    df_in_pa = df_in_pa.merge(df_work_cme, how='left', left_on=["Item Material.[Item Material]"], right_on=["Supply Plan Source Map Ecp_Mtrl Code"])
    vdCommon.gfn_notelog("Configuration merge")

    # 맞는 데이타 찾기
    df_in_pa["Valid Mtrl Item_Supply Plan Source"] = df_in_pa["Supply Plan Source Map_Source"]
    df_in_pa.loc[(df_in_pa["Supply Plan Source Map Ecp_Source"].notna()), "Valid Mtrl Item_Supply Plan Source"] = df_in_pa["Supply Plan Source Map Ecp_Source"]
    df_in_pa.loc[(df_in_pa["Supply Plan Source Map Ecp_Mtrl Code"].notna()), "Valid Mtrl Item_Supply Plan Ecp"] = "Y"
    df_in_pa.drop(["Supply Plan Source Map_Source", "Supply Plan Source Map Ecp_Mtrl Code", "Supply Plan Source Map Ecp_Source"], axis=1, inplace=True)
    vdCommon.gfn_notelog("Configuration calc")

    vdCommon.gfn_saveDf(df_in_pa, "Configuration find data", True)

    # version 추가
    df_out = df_in_pa
    df_in_pa.drop(["Item Material.[MSL3]", "Item Material.[MSL4]", "Item Material.[MSL5]"], axis=1, inplace=True)
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

