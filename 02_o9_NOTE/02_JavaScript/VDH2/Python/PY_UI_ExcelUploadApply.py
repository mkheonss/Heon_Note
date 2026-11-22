"""

df_in_config : Select ([Version].[Version Name] * [Sequence].[Sequence] * [Layout].[Layout] ) on row, ({Measure.[Excel Header Cfg_Desc], Measure.[Excel Header Cfg_Dim1], Measure.[Excel Header Cfg_Dim2], Measure.[Excel Header Cfg_Dim3], Measure.[Excel Header Cfg_Filter1], Measure.[Excel Header Cfg_Filter2], Measure.[Excel Header Cfg_Filter3], Measure.[Excel Header Cfg_Header], Measure.[Excel Header Cfg_Map], Measure.[Excel Header Cfg_Mea1], Measure.[Excel Header Cfg_Mea2], Measure.[Excel Header Cfg_Mea3], Measure.[Excel Header Cfg_Shift Column1], Measure.[Excel Header Cfg_Shift Column2], Measure.[Excel Header Cfg_Shift Column3], Measure.[Excel Header Cfg_Type], Measure.[Excel Header Cfg_Valid], Measure.[Excel Header Cfg_Week Idx]}) on column;
df_in_excelupload : Select ([Version].[Version Name] * [Layout].[Layout] * [Personnel].[Email] * [Seg].[Seg] * [Seq].[Seq] ) on row, ({Measure.[Base], Measure.[Data type], Measure.[LT], Measure.[Material], Measure.[Notify], Measure.[Plant], Measure.[Validation], Measure.[Vendor], Measure.[W00], Measure.[W01], Measure.[W02], Measure.[W03], Measure.[W04], Measure.[W05], Measure.[W06], Measure.[W07], Measure.[W08], Measure.[W09], Measure.[W10], Measure.[W11], Measure.[W12], Measure.[W13], Measure.[W14], Measure.[W15], Measure.[W16], Measure.[W17], Measure.[W18], Measure.[W19], Measure.[W20], Measure.[W21], Measure.[W22], Measure.[W23], Measure.[W24], Measure.[W25]}) on column;
df_in_week : Select ([Time].[Week]) on row, () on column;
df_in_createconfig : Select ([Version].[Version Name] * [Layout].[Layout] ) on row, ({Measure.[Excel Header Create Cfg_Case1 Grain], Measure.[Excel Header Create Cfg_Case1 Mg Name], Measure.[Excel Header Create Cfg_Case2 Grain], Measure.[Excel Header Create Cfg_Case2 Mg Name], Measure.[Excel Header Create Cfg_Case3 Grain], Measure.[Excel Header Create Cfg_Case3 Mg Name]}) on column;;

df_out_case1
df_out_case2
df_out_case3
df_out_case1_u


EXEC plugin instance [PY_UI_ExcelUploadApply] for measures {[Validation]} using scope ( &CWV * [Layout].[Layout].[{{fbLayout}}] * [Personnel].[Email].[{{fbEmail}}] * [Seg].[Seg].[{{fbSeg}}] ) using arguments {(RunID, "Run_01"), (param_seg, "{{fbSeg}}"), (param_user, CurrentUser().[User Name]), (ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


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
str_instance = 'PY_UI_ExcelUploadApply'
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

def fn_get_str(val):
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

def fn_info(note:str):
    # if logger.get_level() >= common.G_log_level.info():
    logger.Note(p_note=note, p_log_level=common.G_log_level.info())

def fn_debug(note:str):
    if logger.get_level() >= common.G_log_level.debug():
        logger.Note(p_note=note, p_log_level=common.G_log_level.debug())


########################################################################################################################
# Main Logic
########################################################################################################################


logger.Step(p_step_desc='plugin Execution Start')

pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
warnings.simplefilter(action='ignore', category=FutureWarning)

if is_local:
    df_in_config = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_config.csv", encoding="UTF-8")
    df_in_excelupload = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_excelupload.csv", encoding="UTF-8")
    df_in_week = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_week.csv", encoding="UTF-8")
    df_in_createconfig = pd.read_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_in_createconfig.csv", encoding="UTF-8")
    param_seg = "솔루엠"
    param_user = "sungmin0.lim"

try:
    # df 춮력
    saveDf(df_in_config, "df_in_config")
    saveDf(df_in_excelupload, "df_in_excelupload")
    saveDf(df_in_week, "df_in_week")

    # week 정렬
    df_in_week = df_in_week.sort_values(by="Time.[Week]", ascending=True)

    # Case 별 실행..
    df_out_case1 = pd.DataFrame()
    df_out_case2 = pd.DataFrame()
    df_out_case3 = pd.DataFrame()
    df_out_case1_u = pd.DataFrame()
    df_out_case2_u = pd.DataFrame()
    df_out_case3_u = pd.DataFrame()
    for case_idx in range(3):
        fn_info("case_idx : " + str(case_idx))

        # fillna 실행 : 처음 데이타가 없을 경우 float로 나오는 문제 발생
        df_in_config["Excel Header Cfg_Dim" + str(case_idx + 1)].fillna(value="", inplace=True)
        df_in_config["Excel Header Cfg_Mea" + str(case_idx + 1)].fillna(value="", inplace=True)
        df_in_config["Excel Header Cfg_Filter" + str(case_idx + 1)].fillna(value="", inplace=True)
        df_in_config["Excel Header Cfg_Shift Column" + str(case_idx + 1)].fillna(value="", inplace=True)

        # Base를 기준으로 week 로 데이타를 만들 변수들을 구한다.
        base_idx = -1
        isBase = False
        week_dimension = ""
        week_mesaure = ""
        shiftColumn = ""
        for idx in df_in_config.index:
            header = df_in_config.loc[idx, "Excel Header Cfg_Header"]
            week_dimension = fn_get_str(df_in_config.loc[idx, "Excel Header Cfg_Dim" + str(case_idx + 1)])
            week_mesaure = fn_get_str(df_in_config.loc[idx, "Excel Header Cfg_Mea" + str(case_idx + 1)])
            shiftColumn = fn_get_str(df_in_config.loc[idx, "Excel Header Cfg_Shift Column" + str(case_idx + 1)])
            # fn_info("header : " + header + " , week_dimension : " + week_dimension + " , week_mesaure : " + week_mesaure + " , shiftColumn : " + shiftColumn)

            if "Base".__eq__(header) and "".__ne__(week_dimension):
                isBase = True

                # 년주를 기준으로 idx를 구한다. 나중에 week idx 별 이름을 구하기 위해서 사용한다.
                base = df_in_excelupload.loc[0, "Base"]
                fn_info("base : " + str(base))
                for week_idx in df_in_week.index:
                    if base.__eq__(df_in_week.loc[week_idx, "Time.[Week]"]):
                        base_idx = week_idx
                        break

            # 위에서 찾았으면 For 문 종료
            if base_idx > -1:
                break

        fn_info("isBase : " + str(isBase) + " , base_idx : " + str(base_idx) + " , week_dimension : " + week_dimension + " , week_mesaure : " + week_mesaure + " , shiftColumn : " + shiftColumn)

        # work df 정의
        df_out_work = df_in_excelupload.copy()

        # Filter 처리
        for idx in df_in_config.index:
            header = df_in_config.loc[idx, "Excel Header Cfg_Header"]
            filter = fn_get_str(df_in_config.loc[idx, "Excel Header Cfg_Filter" + str(case_idx + 1)])
            if "".__ne__(filter):
                # fn_info("filter : " + filter)
                df_out_work = df_out_work.loc[(df_out_work[header].isin(filter.split(",")))].copy()
        saveDf(df_out_work, "df_out_work - Filter")

        # shift 처리 - LT
        if "".__ne__(week_dimension) and "".__ne__(shiftColumn):
            # idx 기준으로 Week 이름을 가지는 Map을 구성 = { 1 : "W00", 2 : "W01", ... }
            weekMap = {}
            maxWeekIdx = -1
            for idx in df_in_config.index:
                header = df_in_config.loc[idx, "Excel Header Cfg_Header"]
                idx = fn_get_str(df_in_config.loc[idx, "Excel Header Cfg_Week Idx"])
                if "".__ne__(idx):
                    weekMap[int(float(idx))] = header

                    if int(float(idx)) > maxWeekIdx:
                        maxWeekIdx = int(float(idx))

            fn_info("maxWeekIdx : " + str(maxWeekIdx))
            fn_info(weekMap.__str__())

            for idx in df_out_work.index:
                if "".__ne__(fn_get_str(df_out_work.loc[idx, shiftColumn])):
                    # Shift 컬럼에 데이타가 있으면.... LT 가 있으면..
                    shiftValue = int(float(fn_get_str(df_out_work.loc[idx, shiftColumn])))
                    # fn_info("shiftValue : " + str(shiftValue) + " , Material : " + df_out_work.loc[idx, "Material"])

                    if shiftValue > 0:
                        for week_idx in range(maxWeekIdx - shiftValue, -1, -1):
                            # 역순으로 해서 Shift 하고
                            df_out_work.loc[idx, weekMap[week_idx + shiftValue]] = df_out_work.loc[idx, weekMap[week_idx]]
                            # 원 데이타 초기화
                            df_out_work.loc[idx, weekMap[week_idx]] = 0

            saveDf(df_out_work, "df_out_work - Shift")

        # 필요한 컬럼 목록
        arr_header = ["Version.[Version Name]"]
        # Dimension 목록
        arr_dimension = ["Version.[Version Name]"]
        # Header를 O9 스키마로 변경할 목록
        rename_columns = {}
        # 스트링을 Float로 바꿀 컬럼 목록
        type_chg_columns = {}
        for idx in df_in_config.index:
            header = df_in_config.loc[idx, "Excel Header Cfg_Header"]
            cfgType = df_in_config.loc[idx, "Excel Header Cfg_Type"]
            dimension = df_in_config.loc[idx, "Excel Header Cfg_Dim" + str(case_idx + 1)]
            measure = df_in_config.loc[idx, "Excel Header Cfg_Mea" + str(case_idx + 1)]
            idx = fn_get_str(df_in_config.loc[idx, "Excel Header Cfg_Week Idx"])

            # fn_info("header : " + header + " , dimension : " + dimension + " , measure : " + measure + " , idx : " + idx)

            if "Base".__ne__(header):
                if "".__ne__(week_dimension) and (fn_isNotNull(dimension) or fn_isNotNull(measure) or fn_isNotNull(idx)):
                    # Week 로 풀어야하는 케이스
                    arr_header.append(header)
                    if fn_isNotNull(dimension):
                        arr_dimension.append(dimension)
                        rename_columns[header] = dimension
                elif "".__eq__(week_dimension) and (fn_isNotNull(dimension) or fn_isNotNull(measure)):
                    # Week 와 상관없는 케이스
                    arr_header.append(header)
                    if fn_isNotNull(dimension):
                        arr_dimension.append(dimension)
                    if fn_isNotNull(dimension):
                        rename_columns[header] = dimension
                    if fn_isNotNull(measure):
                        rename_columns[header] = measure
                    if fn_isNotNull(cfgType) and fn_isNotNull(measure):
                        type_chg_columns[measure] = 'float'

            if isBase and fn_isNotNull(idx):
                # W?? -> 년주 로 컬럼 변경하기 위해서...
                rename_columns[header] = df_in_week.loc[base_idx + int(float(idx)), "Time.[Week]"]

        fn_info(arr_header.__str__())
        fn_info(arr_dimension.__str__())
        fn_info(rename_columns.__str__())
        fn_info(type_chg_columns.__str__())

        # 필요한 컬럼만 가져온다.
        df_out_work = df_out_work[arr_header].copy()
        saveDf(df_out_work, "df_out_work - use column")

        # rename을 한다.
        df_out_work.rename(columns=rename_columns, inplace=True)
        saveDf(df_out_work, "df_out_work - rename")

        # isBase 가 있으면 unpivot 을 한다.
        if isBase:
            df_out_work = df_out_work.melt(id_vars=arr_dimension, var_name=week_dimension, value_name=week_mesaure)
            saveDf(df_out_work, "df_out_work - unpivot")

            # Type 변경이 필요
            df_out_work = df_out_work.astype({week_mesaure: 'float'}, copy=True)

            # 전체 정렬을 한다.
            # df_out_work = df_out_work.sort_values(by=arr_dimension, ascending=True)
        else:
            # Type 변경이 필요
            df_out_work = df_out_work.astype(type_chg_columns, copy=True)

        if case_idx == 0:
            df_out_case1 = df_out_work.copy()
        elif case_idx == 1:
            df_out_case2 = df_out_work.copy()
        elif case_idx == 2:
            df_out_case3 = df_out_work.copy()

        # 등록자 정보를 남기는 DF 생성 - Week를 뺀 데이타로 수정 정보를 만든다.
        for idx in range(0, len(arr_dimension)):
            if arr_dimension[idx] == week_dimension:
                del arr_dimension[idx]
        if case_idx == 0:
            df_out_case1_u = df_out_work[arr_dimension].copy()
            df_out_case1_u.drop_duplicates()
            df_out_case1_u[df_in_createconfig.loc[0, "Excel Header Create Cfg_Case1 Mg Name"] + "_Seg"] = param_seg
            df_out_case1_u[df_in_createconfig.loc[0, "Excel Header Create Cfg_Case1 Mg Name"] + "_Created By"] = param_user
        elif case_idx == 1:
            df_out_case2_u = df_out_work[arr_dimension].copy()
            df_out_case2_u.drop_duplicates()
            df_out_case2_u[df_in_createconfig.loc[0, "Excel Header Create Cfg_Case2 Mg Name"] + "_Seg"] = param_seg
            df_out_case2_u[df_in_createconfig.loc[0, "Excel Header Create Cfg_Case2 Mg Name"] + "_Created By"] = param_user
        elif case_idx == 2:
            df_out_case3_u = df_out_work[arr_dimension].copy()
            df_out_case3_u.drop_duplicates()
            df_out_case3_u[df_in_createconfig.loc[0, "Excel Header Create Cfg_Case3 Mg Name"] + "_Seg"] = param_seg
            df_out_case3_u[df_in_createconfig.loc[0, "Excel Header Create Cfg_Case3 Mg Name"] + "_Created By"] = param_user

    saveDf(df_out_case1, "df_out_case1")
    saveDf(df_out_case2, "df_out_case2")
    saveDf(df_out_case3, "df_out_case3")
    saveDf(df_out_case1_u, "df_out_case1_u")
    saveDf(df_out_case2_u, "df_out_case2_u")
    saveDf(df_out_case3_u, "df_out_case3_u")

    # 데이터 파일 저장
    if is_local:
        logger.Step(p_step_desc='csv save')
        df_out_case1.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_case1.csv", index=False)
        df_out_case2.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_case2.csv", index=False)
        df_out_case3.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_case3.csv", index=False)
        df_out_case1_u.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_case1_u.csv", index=False)
        df_out_case2_u.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_case2_u.csv", index=False)
        df_out_case3_u.to_csv(os.path.dirname(__file__) + "\\" + f"{str_instance}_out_case3_u.csv", index=False)
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    raise Exception(e)
finally:
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Step(p_step_desc='plugin Execution End')
    logger.Finish()

