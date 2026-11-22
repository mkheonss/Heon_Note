"""
df_in_itemGroup : Select ([Version].[Version Name] * [Group].[Group ID] ) on row, ({Measure.[Build Ahead Group_From Site], Measure.[Build Ahead Group_To Site], Measure.[Build Ahead Group_Item], Measure.[Build Ahead Group_Product Group], Measure.[Build Ahead Group_Project], Measure.[Build Ahead Group_Definition], Measure.[Build Ahead Group_Inch], Measure.[Build Ahead Group_MKT Name], Measure.[Build Ahead Group_Year]}) on column;
df_in_item : Select (Item.[Product Group] * Item.[Definition] * Item.[Project] * Item.[Marketing Name] * Item.[Inch] * Item.[Year] * &SETItem) on row, () on column;
df_in_bodItem : Select ([Version].[Version Name] * &SETItem * &MFStageSETLocation * [Sub Location].[Sub Location] ) on row, ({Measure.[BOD Item_BOD LT], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Eff Enddate], Measure.[Dummy]}) on column where {coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()};
df_in_ecp : Select ([Version].[Version Name] * [Item].[Item] * [Group].[Group ID] ) on row, ({Measure.[Build Ahead Group Ecp_Flag]}) on column;

df_out :

EXEC plugin instance [PY_UI_BuildAheadMaster]
for measures {[Build Ahead Group Ecp_Flag]}
using scope ( &CWVUI )
using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* 수정 사항
25-11-19 : MG 를 "Build Ahead Item" 에서 "Build Ahead Group" 로 변경
25-12-10 : 비교를 배열로 하기 위해서 로직을 apply 로 변경
25-02-05 : Item 은 정규식으로 안하고 멀티로 입력 받기로함
26-03-18 : Item 비교가 잘못되어서 수정
"""

import pandas as pd
import os
import traceback
import warnings
import datetime
import re
import gc
import numpy as np
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BuildAheadMaster'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 공통 함수 정의
########################################################################################################################


########################################################################################################################
# 함수 정의
########################################################################################################################
class NoData(Exception):
    pass

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

# def fn_convertReg(df:pd.DataFrame, columnName:str):
#     df['first Str'] = df[columnName].str[0:1]
#     df['last Str'] = df[columnName].str[-1:]
#     df[columnName] = df[columnName].str.replace("%", ".*")
#     df.loc[(df['first Str'] == "%") & ~(df['last Str'] == "%"), columnName] = df[columnName] + "$"
#     df.loc[~(df['first Str'] == "%") & (df['last Str'] == "%"), columnName] = "^" + df[columnName]
#     df.loc[~(df['first Str'] == "%") & ~(df['last Str'] == "%"), columnName] = "^" + df[columnName] + "$"
#     df.drop(columns=["first Str", "last Str"], axis=1, inplace=True)

# def fn_regCompare(row):
#     if row["Build Ahead Group_Item"] == "^" + "All" + "$":
#         return True
#     elif re.search(row["Build Ahead Group_Item"], row["Item.[Item]"]) == None:
#         return False
#     else:
#         return True

def fn_findItem(row):
    # 매핑값
    fromSite = fn_get_str(row["Build Ahead Group_From Site"])
    toSite = fn_get_str(row["Build Ahead Group_To Site"])
    productGroup = fn_get_str(row["Build Ahead Group_Product Group"])
    definition = fn_get_str(row["Build Ahead Group_Definition"])
    project = fn_get_str(row["Build Ahead Group_Project"])
    mktName = fn_get_str(row["Build Ahead Group_MKT Name"])
    inch = fn_get_str(row["Build Ahead Group_Inch"])
    year = fn_get_str(row["Build Ahead Group_Year"])
    item = fn_get_str(row["Build Ahead Group_Item"])

    if ((row["Item.[Product Group]"] in productGroup.split("^")) and
            (row["Item.[Definition]"] in definition.split("^")) and
            (row["Item.[Project]"] in project.split("^")) and
            (row["Item.[Marketing Name]"] in mktName.split("^")) and
            (row["Item.[Inch]"] in inch.split("^")) and
            (row["Item.[Year]"] in year.split("^")) and
            ((item == "All") or (item != "All" and row["Item.[Item]"] in item.split("^")))):
        return True
    else:
        return False

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if is_local:
        df_in_itemGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemGroup.csv", encoding="UTF-8")
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_item.csv", encoding="UTF-8")
        df_in_bodItem = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_bodItem.csv", encoding="UTF-8")
        df_in_ecp = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_ecp.csv", encoding="UTF-8")

        # df_in_itemGroup = df_in_itemGroup.loc[(df_in_itemGroup["Group.[Group ID]"].isin(["BAL_00003"]))].copy()

    vdCommon.gfn_saveDf(df_in_itemGroup, "df_in_itemGroup", True)
    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_bodItem, "df_in_bodItem", True)
    vdCommon.gfn_saveDf(df_in_ecp, "df_in_ecp", True)

    if len(df_in_bodItem) == 0:
        raise NoData

    # BOD Item 을 Location.[Location], Sub Location.[Sub Location] 기준으로 Item을 "," 로 합친다.
    df_work_bodItem1 = df_in_bodItem.groupby(["Location.[Location]", "Sub Location.[Sub Location]"])["Item.[Item]"].agg(",".join).reset_index()
    # vdCommon.gfn_saveDf(df_work_bodItem1, "df_work_bodItem1")

    # BOD Item 을 Location.[Location], All 기준으로 Item을 합친다.
    df_in_bodItem['Sub Location.[Sub Location]'] = "All"
    df_work_bodItem2 = df_in_bodItem.groupby(["Location.[Location]", "Sub Location.[Sub Location]"])["Item.[Item]"].agg(",".join).reset_index()
    # vdCommon.gfn_saveDf(df_work_bodItem2, "df_work_bodItem2")

    # 2가지 경우를 합친다.
    df_work_bodItem = pd.concat([df_work_bodItem1, df_work_bodItem2]).reset_index(drop=True)
    vdCommon.gfn_saveDf(df_work_bodItem, "BodItem agg data")

    # 메모리 해제
    del df_work_bodItem1
    del df_work_bodItem2
    gc.collect()

    # df_in_itemGroup 기준으로 df_work_bodItem 를 조인한다.
    df_work_itemGroup = df_in_itemGroup.merge(df_work_bodItem, how='inner', left_on=["Build Ahead Group_From Site", "Build Ahead Group_To Site"], right_on=["Location.[Location]", "Sub Location.[Sub Location]"])
    vdCommon.gfn_saveDf(df_work_itemGroup, "merge Boditem in ItemGroup", True)

    # Item을 여러 행으로 풀어준 후에 Item 과 조인한다.
    df_work_itemGroup["Item.[Item]"] =  df_work_itemGroup["Item.[Item]"].str.split(",")
    df_work_itemGroup = df_work_itemGroup.explode("Item.[Item]")
    df_work_itemGroup = df_work_itemGroup.merge(df_in_item, how='inner', on=["Item.[Item]"])
    vdCommon.gfn_saveDf(df_work_itemGroup, "ItemGroup explode with Item", True)

    if len(df_work_itemGroup) == 0:
        raise NoData

    # Dimension 인 경우  - 는 빈문자열로 치환
    df_work_itemGroup.loc[(df_work_itemGroup["Item.[Product Group]"] == "-"), "Item.[Product Group]"] = ""
    df_work_itemGroup.loc[(df_work_itemGroup["Item.[Definition]"] == "-"), "Item.[Definition]"] = ""
    df_work_itemGroup.loc[(df_work_itemGroup["Item.[Project]"] == "-"), "Item.[Project]"] = ""
    df_work_itemGroup.loc[(df_work_itemGroup["Item.[Marketing Name]"] == "-"), "Item.[Marketing Name]"] = ""
    df_work_itemGroup.loc[(df_work_itemGroup["Item.[Inch]"] == "-"), "Item.[Inch]"] = ""
    df_work_itemGroup.loc[(df_work_itemGroup["Item.[Year]"] == "-"), "Item.[Year]"] = ""
    vdCommon.gfn_stepLog('Dimension 빈문자열 처리')

    # All 표현 단순화
    df_work_itemGroup.loc[df_work_itemGroup["Build Ahead Group_Product Group"] == "All", "Item.[Product Group]"] = "All"
    df_work_itemGroup.loc[df_work_itemGroup["Build Ahead Group_Definition"] == "All", "Item.[Definition]"] = "All"
    df_work_itemGroup.loc[df_work_itemGroup["Build Ahead Group_Project"] == "All", "Item.[Project]"] = "All"
    df_work_itemGroup.loc[df_work_itemGroup["Build Ahead Group_MKT Name"] == "All", "Item.[Marketing Name]"] = "All"
    df_work_itemGroup.loc[df_work_itemGroup["Build Ahead Group_Inch"] == "All", "Item.[Inch]"] = "All"
    df_work_itemGroup.loc[df_work_itemGroup["Build Ahead Group_Year"] == "All", "Item.[Year]"] = "All"
    vdCommon.gfn_stepLog('조건이 All 이면 Dimension 도 All로 변경')
    vdCommon.gfn_saveDf(df_work_itemGroup, "Replace All", True)

    # Item 은 정규식 비교
    # fn_convertReg(df_work_itemGroup, "Build Ahead Group_Item")
    # vdCommon.gfn_stepLog('정규식 변환')

    # df_work_itemGroup["Item Flag"] = df_work_itemGroup.apply(lambda row : fn_regCompare(row), axis=1, result_type='expand')
    # vdCommon.gfn_stepLog('Item 정규식으로 검색')

    # 조건 멀티 검색
    df_work_itemGroup["Find Flag"] = df_work_itemGroup.apply(lambda row: fn_findItem(row), axis=1, result_type='expand')
    vdCommon.gfn_stepLog('조건에 맞는 데이타 찾기')
    df_work_itemGroup = df_work_itemGroup.loc[(df_work_itemGroup["Find Flag"] == True)].copy()
    vdCommon.gfn_saveDf(df_work_itemGroup, "Find mapping", True)

    # 이미 등록된 데이타는 제외한다.
    df_work_itemGroup = df_work_itemGroup.merge(df_in_ecp, how='left', on=["Version.[Version Name]", "Item.[Item]", "Group.[Group ID]"])
    df_work_itemGroup = df_work_itemGroup[df_work_itemGroup["Build Ahead Group Ecp_Flag"].isna()]
    vdCommon.gfn_saveDf(df_work_itemGroup, "Delete exist Data", True)

    # 결과 데이타 생성
    df_out = df_work_itemGroup[["Version.[Version Name]", "Item.[Item]", "Group.[Group ID]", "Build Ahead Group Ecp_Flag"]].copy()
    df_out["Build Ahead Group Ecp_Flag"] = "N"

    vdCommon.gfn_saveDf(df_out, "df_out", True)

    vdCommon.gfn_stepLog('plugin Execution End')
except NoData as e:
    vdCommon.gfn_stepLog('No Data')

    df_out = pd.DataFrame([], columns=[])
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

