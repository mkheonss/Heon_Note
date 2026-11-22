"""

df_in_plant : select ([Sub Location].[Sub Location]) on row, () on column include memberproperties {[Sub Location].[Sub Location], [DisplayName]} ;
df_in_vendor : select ([Location].[Location]) on row, () on column include memberproperties {[Location].[Location], [DisplayName]} ;

df_out_excelValid
df_out_excelMap


EXEC plugin instance [PY_UI_ExcelConfigData]
for measures {[Excel Valid_Value]}
using scope ( &CWVUI )
using arguments {(RunID, "Run_01"),(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
str_instance = 'PY_UI_ExcelConfigData'
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
        df_in_plant = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_plant.csv", encoding="UTF-8")
        df_in_vendor = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_vendor.csv", encoding="UTF-8")

    # df 춮력
    vdCommon.gfn_saveDf(df_in_plant, "df_in_plant", True)
    vdCommon.gfn_saveDf(df_in_vendor, "df_in_vendor", True)

    ########################################## Valid 데이타 생성 #########################################################
    # Plant 데이타 생성
    df_work = df_in_plant[["Sub Location.[Sub Location]"]].copy()
    df_work["Version.[Version Name]"] = "VD"
    df_work["Header.[Header]"] = "Fix Plant"
    df_work["Sequence.[Sequence]"] = 1
    df_work.rename(columns={"Sub Location.[Sub Location]": "Excel Valid_Value"}, inplace=True)

    for row in df_work.index:
        df_work.loc[row, "Sequence.[Sequence]"] = row + 1

    df_out_excelValid = df_work[["Version.[Version Name]","Header.[Header]","Sequence.[Sequence]","Excel Valid_Value"]].copy()

    # Vendor 데이타 생성
    df_work = df_in_vendor[["Location.[Location]"]].copy()
    df_work["Version.[Version Name]"] = "VD"
    df_work["Header.[Header]"] = "Fix Vendor"
    df_work["Sequence.[Sequence]"] = 1
    df_work.rename(columns={"Location.[Location]": "Excel Valid_Value"}, inplace=True)

    for row in df_work.index:
        df_work.loc[row, "Sequence.[Sequence]"] = row + 1

    df_out_excelValid = pd.concat([df_out_excelValid, df_work]).reset_index(drop=True)

    ########################################## Convert 데이타 생성 #########################################################
    # Plant 데이타 생성
    df_work = df_in_plant[["Sub Location.[Sub Location]","Sub Location.[Sub Location$DisplayName]"]].copy()
    df_work["Version.[Version Name]"] = "VD"
    df_work["Header.[Header]"] = "Fix Plant"
    df_work["Sequence.[Sequence]"] = 1
    df_work.rename(columns={"Sub Location.[Sub Location]": "Excel Map_Value Conv", "Sub Location.[Sub Location$DisplayName]": "Excel Map_Value Org"}, inplace=True)

    for row in df_work.index:
        df_work.loc[row, "Sequence.[Sequence]"] = row + 1

    df_out_excelMap = df_work[["Version.[Version Name]","Header.[Header]","Sequence.[Sequence]","Excel Map_Value Org","Excel Map_Value Conv"]].copy()

    # Vendor 데이타 생성
    df_work = df_in_vendor[["Location.[Location]","Location.[Location$DisplayName]"]].copy()
    df_work["Version.[Version Name]"] = "VD"
    df_work["Header.[Header]"] = "Fix Vendor"
    df_work["Sequence.[Sequence]"] = 1
    df_work.rename(columns={"Location.[Location]": "Excel Map_Value Conv", "Location.[Location$DisplayName]": "Excel Map_Value Org"}, inplace=True)

    for row in df_work.index:
        df_work.loc[row, "Sequence.[Sequence]"] = row + 1

    df_out_excelMap = pd.concat([df_out_excelMap, df_work]).reset_index(drop=True)

    # Sequence 가 int 형이여서 서버에서 오류 발생해서 타입변경
    df_out_excelValid = df_out_excelValid.astype( {"Sequence.[Sequence]": 'str'}, copy=True)
    df_out_excelMap = df_out_excelMap.astype( {"Sequence.[Sequence]": 'str'}, copy=True)

    # df 출력
    vdCommon.gfn_saveDf(df_out_excelValid, "df_out_excelValid", True)
    vdCommon.gfn_saveDf(df_out_excelMap, "df_out_excelMap", True)



    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_excelValid = pd.DataFrame([], columns=[])
    df_out_excelMap = pd.DataFrame([], columns=[])
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

