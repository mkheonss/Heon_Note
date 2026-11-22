

"""

* 프로그램명
    - PY_UI_OnHandMtrlAll

* 내용
     -  법인 Storage Location별 가용 / 비가용 자재 합계수량 계산



* 변경이력
- 2024.12.18 / de0413.shin (신동언) / Create

* Input
- df_in_Storage_Loc  = pd.read_csv('df_in_Storage_Loc.csv')
- df_in_Onhand_Mtrl  = pd.read_csv('df_in_Onhand_Mtrl.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.


* Input Table
   - df_in_Storage_Loc = select ([Storage Loc].[Storage Loc].[All] * [Storage Loc].[Storage Loc Name]);
   - df_in_Onhand_Mtrl = Select ([Version].[Version Name] * [Time].[Day] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Storage Loc].[Storage Loc].filter(~(#.Name in {"All"})) ) on row,
                                ({Measure.[Onhand Mtrl_Local Update Time], Measure.[Onhand Mtrl_Block], Measure.[Onhand Mtrl_CMI], Measure.[Onhand Mtrl_HALB], Measure.[Onhand Mtrl_Inspection], Measure.[Onhand Mtrl_Return], Measure.[Onhand Mtrl_SVC], Measure.[Onhand Mtrl_Unavail Storage], Measure.[Onhand Mtrl_Unrestricted], Measure.[Onhand Mtrl_Vendor Stock], Measure.[Onhand Mtrl_Total]}) on column;

* Output Table
    - df_out_Onhand_Mtrl = Select ([Version].[Version Name] * [Time].[Day] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Storage Loc].[Storage Loc].filter(~(#.Name in {"CMI","-"})) ) on row,
                                ({Measure.[Onhand Mtrl_Local Update Time], Measure.[Onhand Mtrl_Block], Measure.[Onhand Mtrl_CMI], Measure.[Onhand Mtrl_HALB], Measure.[Onhand Mtrl_Inspection], Measure.[Onhand Mtrl_Return], Measure.[Onhand Mtrl_SVC], Measure.[Onhand Mtrl_Unavail Storage], Measure.[Onhand Mtrl_Unrestricted], Measure.[Onhand Mtrl_Vendor Stock]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_OnHandMtrlAll] for Measures {[Onhand Mtrl_Block]} using scope ([Version].[Version Name].filter(#.Name in {"CWV_MP"})) using arguments {(RunId, "Run_01"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), ("IncludeNullRows", "False")};



실행 전 프로시져를 통해 MF Site 삭제  필요

"""


########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

import os
import time
import datetime
import decimal
import warnings
import math
import traceback
import gc
import tracemalloc

import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_OnHandMtrlAll'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# logic start
########################################################################################################################
def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

def fn_math(val1,val2):
    return math.trunc(val1 / val2) * val2

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    vdCommon.gfn_stepLog('STEP 1(Start) : Input Date Frame Read')

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if common.gfn_get_isLocal():
        df_in_Storage_Loc = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_Storage_Loc.csv", encoding="UTF-8")
        df_in_Onhand_Mtrl = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_Onhand_Mtrl.csv", encoding="UTF-8")
        paramOutVersion = "CWV_MP"

    # Input 출력
    vdCommon.gfn_saveDf(df_in_Storage_Loc, "df_in_Storage_Loc", True)
    vdCommon.gfn_saveDf(df_in_Onhand_Mtrl, "df_in_Onhand_Mtrl", True)

    vdCommon.gfn_stepLog('STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 2 (1) 데이터 프레임 변수 지정 및 이름 변경
    ################################################################################################################
    vdCommon.gfn_stepLog('STEP 2(Start) : DataFrame Column 변수 처리')

    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    STORAGE_LOC = 'Storage Loc.[Storage Loc]'
    LOCATION_LOCATION = 'Location.[Location]'
    SUB_LOCATION = 'Sub Location.[Sub Location]'
    ITEM_MATERIAL = 'Item Material.[Item Material]'
    TIME_DAY = 'Time.[Day]'

    Mtrl_Local_Update_Time = 'Onhand Mtrl_Local Update Time'
    Mtrl_Block             = 'Onhand Mtrl_Block'
    Mtrl_CMI               = 'Onhand Mtrl_CMI'
    Mtrl_HALB              = 'Onhand Mtrl_HALB'
    Mtrl_Inspection        = 'Onhand Mtrl_Inspection'
    Mtrl_Return            = 'Onhand Mtrl_Return'
    Mtrl_SVC               = 'Onhand Mtrl_SVC'
    Mtrl_Unavail_Storage   = 'Onhand Mtrl_Unavail Storage'
    Mtrl_Unrestricted      = 'Onhand Mtrl_Unrestricted'
    Mtrl_Vendor_Stock      = 'Onhand Mtrl_Vendor Stock'
    Mtrl_Total             = 'Onhand Mtrl_Total'

    vdCommon.gfn_stepLog('STEP 2(End) : Check memory usage & runtime')
    ################################################################################################################
    # Step 3 out 데이터 프레임 크기 확인 및 저장
    ###############################################################################################################
    vdCommon.gfn_stepLog('STEP 3(Start) : input data machining')

    col_list = [VERSION_NAME_COLUMN, TIME_DAY, LOCATION_LOCATION, ITEM_MATERIAL, SUB_LOCATION, STORAGE_LOC, Mtrl_Local_Update_Time, Mtrl_Block, Mtrl_CMI,
                Mtrl_HALB, Mtrl_Inspection, Mtrl_Return, Mtrl_SVC, Mtrl_Unavail_Storage, Mtrl_Unrestricted, Mtrl_Vendor_Stock, Mtrl_Total]

    df_in_Plan = df_in_Onhand_Mtrl[col_list]
    # LOCATION_LOCATION, SUB_LOCATION, ITEM_MATERIAL, TIME_DAY별로 All데이터 생성
    df_in_Plan = df_in_Plan.groupby([VERSION_NAME_COLUMN, LOCATION_LOCATION, SUB_LOCATION, ITEM_MATERIAL, TIME_DAY], as_index=False).agg(Max_Time=(Mtrl_Local_Update_Time, 'max'),
                                                                                                                                         Sum_Mtrl_Block =(Mtrl_Block,'sum'),
                                                                                                                                         Sum_Mtrl_CMI   =(Mtrl_CMI,'sum'),
                                                                                                                                         Sum_Mtrl_HALB  =(Mtrl_HALB,'sum'),
                                                                                                                                         Sum_Mtrl_Inspection =(Mtrl_Inspection,'sum'),
                                                                                                                                         Sum_Mtrl_Return =(Mtrl_Return,'sum'),
                                                                                                                                         Sum_Mtrl_SVC =(Mtrl_SVC,'sum'),
                                                                                                                                         Sum_Mtrl_Unavail_Storage = (Mtrl_Unavail_Storage,'sum'),
                                                                                                                                         Sum_Mtrl_Unrestricted = (Mtrl_Unrestricted,'sum'),
                                                                                                                                         sum_Mtrl_Vendor_Stock = (Mtrl_Vendor_Stock,'sum'))

    df_in_Plan = df_in_Plan.rename(columns={'Max_Time': Mtrl_Local_Update_Time})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_Block': Mtrl_Block})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_CMI': Mtrl_CMI})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_HALB': Mtrl_HALB})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_Inspection': Mtrl_Inspection})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_Return': Mtrl_Return})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_SVC': Mtrl_SVC})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_Unavail_Storage': Mtrl_Unavail_Storage})
    df_in_Plan = df_in_Plan.rename(columns={'Sum_Mtrl_Unrestricted': Mtrl_Unrestricted})
    df_in_Plan = df_in_Plan.rename(columns={'sum_Mtrl_Vendor_Stock': Mtrl_Vendor_Stock})
    df_in_Plan['Storage Loc.[Storage Loc]'] = 'All'
    df_in_Plan[Mtrl_Total] = 0

    col_list = [VERSION_NAME_COLUMN, TIME_DAY, LOCATION_LOCATION, ITEM_MATERIAL, SUB_LOCATION, 'Storage Loc.[Storage Loc]',
                Mtrl_Local_Update_Time, Mtrl_Block, Mtrl_CMI,
                Mtrl_HALB, Mtrl_Inspection, Mtrl_Return, Mtrl_SVC, Mtrl_Unavail_Storage, Mtrl_Unrestricted,
                Mtrl_Vendor_Stock, Mtrl_Total]

    df_in_Plan = df_in_Plan[col_list]

    vdCommon.gfn_saveDf(df_in_Plan, "df_in_Plan", True)

    df_out_Onhand_Mtrl = df_in_Plan

    del df_in_Plan

    row_count, col_count = df_out_Onhand_Mtrl.shape

    vdCommon.gfn_saveDf(df_out_Onhand_Mtrl, "df_out_Onhand_Mtrl", True)
    vdCommon.gfn_stepLog('STEP 3-2 : Final output table create End')

    ################################################################################################################
    # Step 3. 종료
    ################################################################################################################
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_Onhand_Mtrl = pd.DataFrame([], columns=[])

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

