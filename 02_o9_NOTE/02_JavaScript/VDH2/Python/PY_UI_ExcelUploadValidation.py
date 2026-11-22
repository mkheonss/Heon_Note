"""

df_in_config : Select ([Version].[Version Name] * [Sequence].[Sequence] * [Layout].[Layout] ) on row, ({Measure.[Excel Header Cfg_Desc], Measure.[Excel Header Cfg_Dim1], Measure.[Excel Header Cfg_Dim2], Measure.[Excel Header Cfg_Dim3], Measure.[Excel Header Cfg_Filter1], Measure.[Excel Header Cfg_Filter2], Measure.[Excel Header Cfg_Filter3], Measure.[Excel Header Cfg_Header], Measure.[Excel Header Cfg_Map], Measure.[Excel Header Cfg_Mea1], Measure.[Excel Header Cfg_Mea2], Measure.[Excel Header Cfg_Mea3], Measure.[Excel Header Cfg_Shift Column1], Measure.[Excel Header Cfg_Shift Column2], Measure.[Excel Header Cfg_Shift Column3], Measure.[Excel Header Cfg_Type], Measure.[Excel Header Cfg_Valid], Measure.[Excel Header Cfg_Week Idx]}) on column;
df_in_valid : Select ([Version].[Version Name] * [Header].[Header] * [Sequence].[Sequence] ) on row, ({Measure.[Excel Valid_Value]}) on column;
df_in_map : Select ([Version].[Version Name] * [Sequence].[Sequence] * [Header].[Header] ) on row, ({Measure.[Excel Map_Value Conv], Measure.[Excel Map_Value Org]}) on column;
df_in_excelupload : Select ([Version].[Version Name] * [Layout].[Layout] * [Personnel].[Email] * [Seg].[Seg] * [Seq].[Seq] ) on row, ({Measure.[Base], Measure.[Data type], Measure.[LT], Measure.[Material], Measure.[Notify], Measure.[Plant], Measure.[Validation], Measure.[Vendor], Measure.[W00], Measure.[W01], Measure.[W02], Measure.[W03], Measure.[W04], Measure.[W05], Measure.[W06], Measure.[W07], Measure.[W08], Measure.[W09], Measure.[W10], Measure.[W11], Measure.[W12], Measure.[W13], Measure.[W14], Measure.[W15], Measure.[W16], Measure.[W17], Measure.[W18], Measure.[W19], Measure.[W20], Measure.[W21], Measure.[W22], Measure.[W23], Measure.[W24], Measure.[W25]}) on column;
df_in_item : Select ([Item].[Item]) on row, () on column;
df_in_itemMaterial : Select ([Item Material].[Item Material]) on row, () on column;

df_out_excelupload

EXEC plugin instance [PY_UI_ExcelUploadValidation] for measures {[Validation]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Layout].[Layout].[Standard] * [Personnel].[Email].[sungmin0.lim@partner.samsung.com] ) using arguments {(RunID, "Run_01"),(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
EXEC plugin instance [PY_UI_ExcelUploadValidation] for measures {[Validation]} using scope ( &CWV * [Layout].[Layout].[{{fbLayout}}] * [Personnel].[Email].[{{fbEmail}}] ) using arguments {(RunID, "Run_01"),(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


"""

import numpy as np
import pandas as pd
import os
import traceback
import warnings
import NSCMCommon as common
import math

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ExcelUploadValidation'
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
saveDf_idx = 1
def saveDf(_df, _csvName):
    if is_local:
        global saveDf_idx
        _df.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_{saveDf_idx}_{_csvName}.csv", index=False)
        saveDf_idx = saveDf_idx + 1

    logger.PrintDF(p_df=_df, p_df_name=_csvName, p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)



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


logger.Step(p_step_desc='plugin Execution Start')

pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
warnings.simplefilter(action='ignore', category=FutureWarning)

if is_local:
    df_in_config = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_config.csv", encoding="UTF-8")
    df_in_valid = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_valid.csv", encoding="UTF-8")
    df_in_map = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_map.csv", encoding="UTF-8")
    df_in_excelupload = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_excelupload.csv", encoding="UTF-8")
    df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_item.csv", encoding="UTF-8")
    df_in_itemMaterial = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_itemMaterial.csv", encoding="UTF-8")

try:
    # df 춮력
    saveDf(df_in_config, "df_in_config")
    saveDf(df_in_valid, "df_in_valid")
    saveDf(df_in_map, "df_in_map")
    saveDf(df_in_excelupload, "df_in_excelupload")
    saveDf(df_in_item, "df_in_item")
    saveDf(df_in_itemMaterial, "df_in_itemMaterial")

    # 처음 데이타가 없을 경우 float로 나오는 문제 발생
    df_in_config["Excel Header Cfg_Header"].fillna(value="", inplace=True)
    df_in_config["Excel Header Cfg_Type"].fillna(value="", inplace=True)
    df_in_config["Excel Header Cfg_Valid"].fillna(value="", inplace=True)
    df_in_config["Excel Header Cfg_Map"].fillna(value="", inplace=True)

    dict_valid = {}
    for idx in df_in_valid.index:
        dict_valid[df_in_valid.loc[idx, "Header.[Header]"] + "_" + df_in_valid.loc[idx, "Excel Valid_Value"]] = "Y"
    for idx in df_in_item.index:
        dict_valid["Item_" + df_in_item.loc[idx, "Item.[Item]"]] = "Y"
    for idx in df_in_itemMaterial.index:
        dict_valid["ItemMaterial_" + df_in_itemMaterial.loc[idx, "Item Material.[Item Material]"]] = "Y"

    dict_map = {}
    for idx in df_in_map.index:
        dict_map[df_in_map.loc[idx, "Header.[Header]"] + "_" + df_in_map.loc[idx, "Excel Map_Value Org"]] = df_in_map.loc[idx, "Excel Map_Value Conv"]

    logger.Step(p_step_desc='For Start')
    df_out_excelupload = df_in_excelupload.copy()
    for idx in df_out_excelupload.index:
        validation = ""
        notify = ""

        for c_idx in df_in_config.index:
            header = df_in_config.loc[c_idx, "Excel Header Cfg_Header"]
            valueType = df_in_config.loc[c_idx, "Excel Header Cfg_Type"]
            valid = df_in_config.loc[c_idx, "Excel Header Cfg_Valid"]
            map = df_in_config.loc[c_idx, "Excel Header Cfg_Map"]

            if fn_isNotNull(header):
                if not df_out_excelupload.columns.__contains__(header):
                    validation = fn_concat(validation, header + "(Column Error)")
                    continue

            value = gfn_get_str(df_out_excelupload.loc[idx, header])
            # print(header + " : " + valueType + " : " + valid + " : " + map + " : " + value)

            # 변환할 데이타가 있으면 변환
            if fn_isNotNull(map):
                arr = map.split(",")

                for a_idx in range(0, len(arr)):
                    data = dict_map.get(arr[a_idx] + "_" + value)
                    if data != None:
                        value = data
                        df_out_excelupload.loc[idx, header] = value
                        notify = fn_concat(notify, header + " Convert")

            # 유효성 검사
            if fn_isNotNull(valid):
                data = dict_valid.get(valid + "_" + value)
                if data == None:
                    validation = fn_concat(validation, header + "(" + valid + " valid Error)")

            # Type 검사 : int, float
            if fn_isNotNull(valueType):
                # 업로드 데이타가 없는 경우 nan이 들어가서 0로 변경
                if "nan".__eq__(value) or "".__eq__(value):
                    value = "0"
                    df_out_excelupload.loc[idx, header] = value

                if not fn_isDigit(valueType, value):
                    validation = fn_concat(validation, header + "(Type Error)")
                else:
                    df_out_excelupload.loc[idx, header] = fn_convertDigit(valueType, value)

        if validation.__eq__(""):
            validation = "-"
        if notify.__eq__(""):
            notify = "-"

        df_out_excelupload.loc[idx, "Validation"] = validation
        df_out_excelupload.loc[idx, "Notify"] = notify

    logger.Step(p_step_desc='For End')

    # 모든 타입을 스트링으로 변경
    df_out_excelupload = df_out_excelupload.astype(dtype='str', copy=True)

    saveDf(df_out_excelupload, "df_out_excelupload")
    
    # 전체 로그가 잘 안남아서 더 넣어줌
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')
    logger.Step(p_step_desc='temp log ...')

    # 데이터 파일 저장
    if is_local:
        logger.Step(p_step_desc='csv save')
        df_out_excelupload.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_excelupload.csv", index=False)
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    raise Exception(e)
finally:
    logger.Step(p_step_desc='plugin Execution End')
    logger.Finish()

