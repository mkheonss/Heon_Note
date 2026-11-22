"""

* 프로그램명
    - PY_MG_MtrlEOH

* 내용
    - Material PSI EOH Measure 데이터 생성


* 변경이력
    - 2025.04.03  신동언 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

df_in_mp : Select ([Location].[Location] * [Time].[Week] * [Item Material].[Item Material] ) on row, ({ Measure.[Mtrl PSI_EOHDaysCtg_Demand], Measure.[Mtrl PSI_EOHDaysCtg_Demand Fixed], Measure.[Mtrl PSI_EOHDaysCtg_SOP], Measure.[Mtrl PSI_EOHDaysCtg_SOP Fixed] }) on column where { [Version].[Version Name] } ;

df_out :

EXEC plugin instance [PY_UI_MtrlEOH]
for measures {[Mtrl EOH_DP SOP_Short_Cnt]}
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
str_instance = 'PY_MG_MtrlEoh'

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
    ################################################################################################################
    # logic start
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_mp = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_mp.csv", encoding="UTF-8")

        paramOutVersion = "CWV_MP"

    # Input 출력
    vdCommon.gfn_saveDf(df_in_mp, "df_in_mp", True)

    # 0으로 초기화
    df_in_mp["Mtrl EOH_DP SOP_Short_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP_Under DOS Level1_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP_Under DOS Level2_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP_Under DOS Level3_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP_Under DOS Level4_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP_Under DOS Level5_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP_Under DOS Level6_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP_Under DOS Level7_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Short_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Under DOS Level1_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Under DOS Level2_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Under DOS Level3_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Under DOS Level4_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Under DOS Level5_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Under DOS Level6_Cnt"] = 0
    df_in_mp["Mtrl EOH_DP SOP Fixed_Under DOS Level7_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Short_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Under DOS Level1_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Under DOS Level2_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Under DOS Level3_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Under DOS Level4_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Under DOS Level5_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Under DOS Level6_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP_Under DOS Level7_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Short_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Under DOS Level1_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Under DOS Level2_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Under DOS Level3_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Under DOS Level4_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Under DOS Level5_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Under DOS Level6_Cnt"] = 0
    df_in_mp["Mtrl EOH_SOP Fixed_Under DOS Level7_Cnt"] = 0

    # 대상을 1로 세팅
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (Short)"), "Mtrl EOH_DP SOP_Short_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (Short)"), "Mtrl EOH_DP SOP_Under DOS Level1_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (0~7D)"), "Mtrl EOH_DP SOP_Under DOS Level2_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (8~14D)"), "Mtrl EOH_DP SOP_Under DOS Level3_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (15~28D)"), "Mtrl EOH_DP SOP_Under DOS Level4_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (29D~)"), "Mtrl EOH_DP SOP_Under DOS Level5_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (57D~)"), "Mtrl EOH_DP SOP_Under DOS Level6_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand"] == "EOH Week (No Req.)"), "Mtrl EOH_DP SOP_Under DOS Level7_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (Short)"), "Mtrl EOH_DP SOP Fixed_Short_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (Short)"), "Mtrl EOH_DP SOP Fixed_Under DOS Level1_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (0~7D)"), "Mtrl EOH_DP SOP Fixed_Under DOS Level2_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (8~14D)"), "Mtrl EOH_DP SOP Fixed_Under DOS Level3_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (15~28D)"), "Mtrl EOH_DP SOP Fixed_Under DOS Level4_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (29D~)"), "Mtrl EOH_DP SOP Fixed_Under DOS Level5_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (57D~)"), "Mtrl EOH_DP SOP Fixed_Under DOS Level6_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_Demand Fixed"] == "EOH Week (No Req.)"), "Mtrl EOH_DP SOP Fixed_Under DOS Level7_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (Short)"), "Mtrl EOH_SOP_Short_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (Short)"), "Mtrl EOH_SOP_Under DOS Level1_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (0~7D)"), "Mtrl EOH_SOP_Under DOS Level2_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (8~14D)"), "Mtrl EOH_SOP_Under DOS Level3_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (15~28D)"), "Mtrl EOH_SOP_Under DOS Level4_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (29D~)"), "Mtrl EOH_SOP_Under DOS Level5_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (57D~)"), "Mtrl EOH_SOP_Under DOS Level6_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP"] == "EOH Week (No Req.)"), "Mtrl EOH_SOP_Under DOS Level7_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (Short)"), "Mtrl EOH_SOP Fixed_Short_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (Short)"), "Mtrl EOH_SOP Fixed_Under DOS Level1_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (0~7D)"), "Mtrl EOH_SOP Fixed_Under DOS Level2_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (8~14D)"), "Mtrl EOH_SOP Fixed_Under DOS Level3_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (15~28D)"), "Mtrl EOH_SOP Fixed_Under DOS Level4_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (29D~)"), "Mtrl EOH_SOP Fixed_Under DOS Level5_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (57D~)"), "Mtrl EOH_SOP Fixed_Under DOS Level6_Cnt"] = 1
    df_in_mp.loc[(df_in_mp["Mtrl PSI_EOHDaysCtg_SOP Fixed"] == "EOH Week (No Req.)"), "Mtrl EOH_SOP Fixed_Under DOS Level7_Cnt"] = 1

    # 필요없는 컬럼 삭제
    df_in_mp.drop(["Mtrl PSI_EOHDaysCtg_Demand", "Mtrl PSI_EOHDaysCtg_Demand Fixed", "Mtrl PSI_EOHDaysCtg_SOP", "Mtrl PSI_EOHDaysCtg_SOP Fixed"], axis=1, inplace=True)

    # Group By
    df_mp_groupby = df_in_mp.groupby(["Location.[Location]", "Time.[Week]", "Item Material.[Item Material]"], as_index=False).sum()
    vdCommon.gfn_saveDf(df_mp_groupby, "groupby", True)

    # Output 생성 및 출력
    df_out = df_mp_groupby
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

