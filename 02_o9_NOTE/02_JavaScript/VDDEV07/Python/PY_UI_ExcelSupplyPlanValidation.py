"""

df_in_excelupload : Select ([Version].[Version Name] * [Layout].[Layout] * [Personnel].[Email] * [Seg].[Seg] * [Seq].[Seq] ) on row, ({Measure.[Base], Measure.[Data type], Measure.[LT], Measure.[Material], Measure.[Notify], Measure.[Plant], Measure.[Validation], Measure.[Vendor], Measure.[W00], Measure.[W01], Measure.[W02], Measure.[W03], Measure.[W04], Measure.[W05], Measure.[W06], Measure.[W07], Measure.[W08], Measure.[W09], Measure.[W10], Measure.[W11], Measure.[W12], Measure.[W13], Measure.[W14], Measure.[W15], Measure.[W16], Measure.[W17], Measure.[W18], Measure.[W19], Measure.[W20], Measure.[W21], Measure.[W22], Measure.[W23], Measure.[W24], Measure.[W25]}) on column;
df_in_valid : Select ([Version].[Version Name] * [Header].[Header] * [Sequence].[Sequence] ) on row, ({Measure.[Excel Valid_Value]}) on column;
df_in_map : Select ([Version].[Version Name] * [Sequence].[Sequence] * [Header].[Header] ) on row, ({Measure.[Excel Map_Value Conv], Measure.[Excel Map_Value Org]}) on column where {coalesce(Measure.[Excel Map_Value Status], "-") != "NEW"};
df_in_item : Select ([Item].[Item]) on row, () on column;
df_in_itemMaterial : Select ([Item Material].[Item Material]) on row, () on column;
df_in_location : select ([Location].[Location])  on row,  () on column include memberproperties {[Location].[Location], [DisplayName]};

df_out
df_out_1

EXEC plugin instance [PY_UI_ExcelSupplyPlanValidation]
for measures {[Validation]}
using scope ( &VD * [Layout].[Layout].[Standard] * [Personnel].[Email].[sungmin0.lim@partner.samsung.com] )
using arguments {(RunID, "Run_01"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


"""

import numpy as np
import pandas as pd
import os
import traceback
import warnings
import math
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ExcelSupplyPlanValidation'
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
def fn_isNull(val: str):
    if val == np.nan or "".__eq__(val):
        return True
    else:
        return False

def fn_isNotNull(val: str):
    if val != np.nan and "".__ne__(val):
        return True
    else:
        return False

def fn_concat(value1:str, value2:str):
    if value1 == np.nan or "".__eq__(value1):
        return value2
    else:
        return value1 + "," + value2

def fn_isDigit(type:str, val: str):
    try:
        if type == "int":
            num = float(val.replace(",",""))
        elif type == "float":
            num = float(val.replace(",", ""))
    except:
        return False

    return True

def fn_convertDigit(type:str, val: str):
    try:
        if type == "int":
            return int(float(val.replace(",","")))
        elif type == "float":
            return float(val.replace(",", ""))
    except:
        return 0

    return 0

def gfn_get_str(val):
    try:
        if type(val) is str:
            return val
        elif val == np.nan or math.isnan(val):
            return ""
        else:
            return str(val)
    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
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
        df_in_excelupload = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_excelupload.csv", encoding="UTF-8")
        df_in_valid = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_valid.csv", encoding="UTF-8")
        df_in_map = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_map.csv", encoding="UTF-8")
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_item.csv", encoding="UTF-8")
        df_in_itemMaterial = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_itemMaterial.csv", encoding="UTF-8")
        df_in_location = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_location.csv", encoding="UTF-8")

    # 데이타 복사
    df_in_excelupload["Data Type_Code"] = df_in_excelupload["Data type"].copy()
    df_in_excelupload["Vendor_Code"] = df_in_excelupload["Vendor"].copy()
    df_in_excelupload["Plant_Code"] = df_in_excelupload["Plant"].copy()

    # df 춮력
    vdCommon.gfn_saveDf(df_in_excelupload, "df_in_excelupload", True)
    vdCommon.gfn_saveDf(df_in_valid, "df_in_valid", True)
    vdCommon.gfn_saveDf(df_in_map, "df_in_map", True)
    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_itemMaterial, "df_in_itemMaterial", True)
    vdCommon.gfn_saveDf(df_in_location, "df_in_location", True)

    # Valid 체크할 데이타를 Map 으로 구성
    dict_valid = {}
    for idx in df_in_valid.index:
        dict_valid[df_in_valid.loc[idx, "Header.[Header]"] + "_" + df_in_valid.loc[idx, "Excel Valid_Value"]] = "Y"
    for idx in df_in_item.index:
        dict_valid["Item_" + df_in_item.loc[idx, "Item.[Item]"]] = "Y"
    for idx in df_in_itemMaterial.index:
        dict_valid["ItemMaterial_" + df_in_itemMaterial.loc[idx, "Item Material.[Item Material]"]] = "Y"

    # 변경할 정보를 Map 으로 구성
    dict_map = {}
    for idx in df_in_map.index:
        dict_map[df_in_map.loc[idx, "Header.[Header]"] + "_" + df_in_map.loc[idx, "Excel Map_Value Org"]] = df_in_map.loc[idx, "Excel Map_Value Conv"]

    df_out = df_in_excelupload.copy()
    df_out["Excel Map_New Plant"] = ""
    df_out["Excel Map_New Vendor"] = ""
    df_out["Excel Map_New Data type"] = ""
    df_out["Apply Flag"] = ""

    for s_idx in range(1, 25):
        df_out["W" + str(s_idx).rjust(2, "0")].fillna(value=0, inplace=True)
    df_out["LT"].fillna(value=0, inplace=True)
    df_out["Validation"].fillna(value="", inplace=True)

    for idx in df_out.index:
        validation = ""
        notify = ""

        # Data Type 데이타 변환
        value = gfn_get_str(df_out.loc[idx, "Data Type_Code"])
        data = dict_map.get("Data type" + "_" + value)
        if data != None:
            df_out.loc[idx, "Data Type_Code"] = data
            notify = "Data Type_Code" + " Convert"
        else:
            df_out.loc[idx, "Excel Map_New Data type"] = value

        # Mapping 후의 Data Type 값이 AIR, VSL 인 경우만 Validation을 체크한다.
        value = gfn_get_str(df_out.loc[idx, "Data Type_Code"])
        if value.__ne__("AIR") & value.__ne__("VSL"):
            df_out.loc[idx, "Apply Flag"] = ""
            continue
        else:
            df_out.loc[idx, "Apply Flag"] = "Y"

        # 데이타 변환
        mArr = ["Vendor_Code", "Plant_Code"]
        cArr = ["Fix Vendor,Vendor", "Fix Plant,Plant"]
        for s_idx in range(0, len(mArr)):
            value = gfn_get_str(df_out.loc[idx, mArr[s_idx]])
            s_cArr = cArr[s_idx].split(",")
            for s2_idx in range(0, len(s_cArr)):
                data = dict_map.get(s_cArr[s2_idx] + "_" + value)
                if data != None:
                    df_out.loc[idx, mArr[s_idx]] = data
                    notify = fn_concat(notify, mArr[s_idx] + " Convert")
                else:
                    if "Data type".__eq__(s_cArr[s2_idx]):
                        df_out.loc[idx, "Excel Map_New Data type"] = value

        # 유효성 검사
        mArr = ["Plant_Code", "Material", "Vendor_Code"]
        cArr = ["Fix Plant", "ItemMaterial", "Fix Vendor"]
        for s_idx in range(0, len(mArr)):
            value = gfn_get_str(df_out.loc[idx, mArr[s_idx]])
            data = dict_valid.get(cArr[s_idx] + "_" + value)
            if data == None:
                validation = fn_concat(validation, mArr[s_idx] + "(" + cArr[s_idx] + " valid Error)")

                # 신규로 등록할 Excel Map을 구한다.
                if "Fix Plant".__eq__(cArr[s_idx]):
                    df_out.loc[idx, "Excel Map_New Plant"] = value
                if "Fix Vendor".__eq__(cArr[s_idx]):
                    df_out.loc[idx, "Excel Map_New Vendor"] = value

        # 정수 컬럼 Check
        mArr = ["LT"]
        for s_idx in range(0, len(mArr)):
            value = gfn_get_str(df_out.loc[idx, mArr[s_idx]])

            # nan 이거나 없을때 0로 변경
            if "nan".__eq__(value) or "".__eq__(value):
                df_out.loc[idx, mArr[s_idx]] = "0"
            elif not fn_isDigit("int", value):
                validation = fn_concat(validation, mArr[s_idx] + " (Type Error)")
            else:
                df_out.loc[idx, mArr[s_idx]] = fn_convertDigit("int", value)

        # 주차 수량 Check
        for s_idx in range(1, 25):
            measureName = "W" + str(s_idx).rjust(2, "0")
            value = gfn_get_str(df_out.loc[idx, measureName])

            # nan 이거나 없을때 0로 변경
            if "nan".__eq__(value) or "".__eq__(value):
                df_out.loc[idx, measureName] = "0"
            elif not fn_isDigit("int", value):
                validation = fn_concat(validation, measureName + "(Type Error)")
            else:
                df_out.loc[idx, measureName] = fn_convertDigit("int", value)

        if validation.__eq__(""):
            validation = "-"
        if notify.__eq__(""):
            notify = "-"

        df_out.loc[idx, "Validation"] = validation
        df_out.loc[idx, "Notify"] = notify

        if idx % 100 == 0:
            logger.Step(p_step_desc="row " + str(idx))

    # Vendor Name 을 구한다.
    df_in_location.rename(columns={"Location.[Location]" : "Vendor_Code", "Location.[Location$DisplayName]" : "Vendor_Name"}, inplace=True)
    df_out = df_out.merge(df_in_location, how='left', on=["Vendor_Code"])

    # 모든 타입을 스트링으로 변경
    df_out = df_out.astype(dtype='str', copy=True)

    # 신규로 등록할 Excel Map Out을 만든다.
    df_out_1 = pd.DataFrame([], columns=["Version.[Version Name]", "Sequence.[Sequence]", "Header.[Header]", "Excel Map_Value Conv", "Excel Map_Value Org", "Excel Map_Value Status"])

    # Sequence.[Sequence] 의 Max 구하기
    # Type 이 Object 이면 Max 구하는데 문제가 발생하여 Type 변경
    df_in_map = df_in_map.astype({"Sequence.[Sequence]" : "int"}, errors='ignore', copy=True)
    df_max_map = df_in_map.groupby("Header.[Header]", as_index=False)["Sequence.[Sequence]"].max()
    vdCommon.gfn_saveDf(df_max_map, "df_max_map", True)

    vendorSeq = 0
    plantSeq = 0
    dataTypeSeq = 0
    for idx in df_max_map.index:
        if "Vendor".__eq__(df_max_map.loc[idx, "Header.[Header]"]):
            vendorSeq = int(df_max_map.loc[idx, "Sequence.[Sequence]"])
        if "Data type".__eq__(df_max_map.loc[idx, "Header.[Header]"]):
            dataTypeSeq = int(df_max_map.loc[idx, "Sequence.[Sequence]"])
        if "Plant".__eq__(df_max_map.loc[idx, "Header.[Header]"]):
            plantSeq = int(df_max_map.loc[idx, "Sequence.[Sequence]"])

    # Plant 처리
    df_work_map = df_out[["Version.[Version Name]", "Excel Map_New Plant"]].copy()
    df_work_map = df_work_map.drop_duplicates()
    for idx in df_work_map.index:
        value = gfn_get_str(df_work_map.loc[idx, "Excel Map_New Plant"])
        if "".__ne__(value):
            plantSeq = plantSeq + 1
            df_out_1.loc[len(df_out_1)] = ["VD", plantSeq, "Plant", "-", value, "New"]

    # Vendor 처리
    df_work_map = df_out[["Version.[Version Name]", "Excel Map_New Vendor"]].copy()
    df_work_map = df_work_map.drop_duplicates()
    for idx in df_work_map.index:
        value = gfn_get_str(df_work_map.loc[idx, "Excel Map_New Vendor"])
        if "".__ne__(value):
            vendorSeq = vendorSeq + 1
            df_out_1.loc[len(df_out_1)] = ["VD", vendorSeq, "Vendor", "-", value, "New"]

    # Data type 처리
    df_work_map = df_out[["Version.[Version Name]", "Excel Map_New Data type"]].copy()
    df_work_map = df_work_map.drop_duplicates()
    for idx in df_work_map.index:
        value = gfn_get_str(df_work_map.loc[idx, "Excel Map_New Data type"])
        if "".__ne__(value):
            dataTypeSeq = dataTypeSeq + 1
            df_out_1.loc[len(df_out_1)] = ["VD", dataTypeSeq, "Data type", "-", value, "New"]

    vdCommon.gfn_saveDf(df_out_1, "Excel Map DF", True)

    df_out.drop(columns=["Excel Map_New Plant", "Excel Map_New Vendor", "Excel Map_New Data type"], inplace=True)
    vdCommon.gfn_saveDf(df_out, "df_out", True)

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out = pd.DataFrame([], columns=[])
    df_out_1 = pd.DataFrame([], columns=[])
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

