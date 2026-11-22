"""
* 프로그램명
    - PY_UI_LED_ModuleEcpProdMaster

* 내용
    - Module Ecp Prod Master LED Data Generation

* 변경이력
    - 2025.03.31 / 황수혁 / Create
    - 2025.04.14 / 김교승 / Update
    - 2025.05.23 / 김교승 / Update
    - 2026.02.09 / 김교승 / Update / MF Site Stage -> Site Stage 로 변경

* Flow Summary
     Module Ecp Prod Master LED Data 생성

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP

* Input Tables
    - df_in_Item_Site_Association : Select ([Version].[Version Name] * [Location].[Location] * &LEDStrategy * [Item].[Project] * [Item].[Pitch]) on row, ({Measure.[Item Site Asn_Actual Flag], Measure.[Dummy]})  on column where {[Location].[Site Stage].filter(#.Name contains "SET"), [Location].[Location Type].[MF]};
    - df_in_Week : Select (&MPHorizon);
    - df_in_ModuleEcpProdMaster: Select ([Version].[Version Name] * [Location].[Location] * &MPHorizon * [To Item].[To Item Pitch] * [Project].[Project] * [Item].[LED Strategy] ) on row, ({Measure.[Module Ecp Prod Master LED_Defect Rate], Measure.[Module Ecp Prod Master LED_SVC Rate]}) on column;

* Output Tables :
    - df_out_ModuleEcpProdMaster

* 테스트 스크립트
    - EXEC plugin instance [PY_UI_LED_ModuleEcpProdMaster] for Measures {[Module Ecp Prod Master LED_SVC Rate]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_ModuleEcpProdMaster : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Time].[Week] * [To Item].[To Item Pitch] * [Project].[Project] * [Item].[LED Strategy] ) on row, ({Measure.[Module Ecp Prod Master LED_Defect Rate], Measure.[Module Ecp Prod Master LED_SVC Rate]}) on column;


"""
import time
import traceback
import datetime
import os
import warnings
import numpy as np
import pandas as pd
import tracemalloc

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon


########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_LED_ModuleEcpProdMaster'
is_local = common.gfn_get_isLocal()

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"
SEQ_VALUE = 1

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level

COMMON_SOURCE_VERSION = common.G_SourceVersion

########################################################################################################################
# local function
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")

def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()
    formatted_time = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')   # 초 단위를 datetime으로 변환하여 시분초 표시

    logger.debug('[START] {str_instance}')
    logger.Start()

    note(f'===================== plugin Execution Start ({formatted_time}) =====================')
    note(f'=====> Input value checkparamOutVersion : {paramOutVersion}')
    note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')

    try:
        #Batch 시작
        if common.gfn_get_isLocal():
            vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), os.path.dirname(__file__))
        else:
            vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), "")


        vdCommon.gfn_stepLog("plugin Execution Start ")
        vdCommon.gfn_stepLog(common.G_SourceVersion)
        vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

        pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
        warnings.simplefilter(action='ignore', category=FutureWarning)

        ################################################################################################################
        # STEP : 모듈 내에서 사용될 input table load
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP (Start) : 전처리 - 모듈 내에서 사용될 input table load')

        # csv 파일 이름과 변수명을 매핑한 딕셔너리 생성
        if is_local:
            df_in_Item_Site_Association = read_csv_file("df_in_Item_Site_Association")
            df_in_Week = read_csv_file("df_in_Week")
            df_in_ModuleEcpProdMaster = read_csv_file("df_in_ModuleEcpProdMaster")

        vdCommon.gfn_saveDf(df_in_Item_Site_Association, 'df_in_Item_Site_Association')
        vdCommon.gfn_saveDf(df_in_Week, 'df_in_Week')
        vdCommon.gfn_saveDf(df_in_ModuleEcpProdMaster, 'df_in_ModuleEcpProdMaster')

        vdCommon.gfn_stepLog('=====> STEP (End) : 모듈 내에서 사용될 input table load')

        ################################################################################################################
        # STEP : 데이터 선 가공
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP (Start) : 데이터 선 가공')

        df_in_Item_Site_Association = df_in_Item_Site_Association.drop(['Item Site Asn_Actual Flag', 'Dummy'], axis=1, errors='ignore')
        df_in_Week['Version.[Version Name]'] = PARAM_OUTVERSION_VALUE

        df_in_Week['Time.[Week]'] = df_in_Week['Time.[Week]'].astype(str)
        df_in_ModuleEcpProdMaster['Time.[Week]'] = df_in_ModuleEcpProdMaster['Time.[Week]'].astype(str)
        df_in_ModuleEcpProdMaster['To Item.[To Item Pitch]'] = df_in_ModuleEcpProdMaster['To Item.[To Item Pitch]'].astype(str)

        vdCommon.gfn_stepLog('=====> STEP (End) : 데이터 선 가공')

        ################################################################################################################
        # STEP : 변수 처리
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP (Start) : 변수 처리')

        df_in_Week.sort_values(['Time.[Week]'], ascending=True)
        if len(df_in_Week) > 0:
            VAL_FIXWEEK = df_in_Week['Time.[Week]'].apply(lambda x: common.gfn_add_week(x, 1))[0]
        else:
            VAL_FIXWEEK = ''

        note(f'VAL_FIXWEEK      ======================> {VAL_FIXWEEK}')

        vdCommon.gfn_stepLog('=====> STEP (End) : 변수 처리')

        ################################################################################################################
        # STEP 1.0 : df_out_ModuleEcpProdMaster 데이터 처리
        ##########################################################################n######################################
        vdCommon.gfn_stepLog('=====> STEP 1.0 (Start) : df_out_Module_Lie_Capa_LED 데이터 처리')

        df_out_ModuleEcpProdMaster = pd.merge(df_in_Item_Site_Association, df_in_Week, on=['Version.[Version Name]'], how='outer')
        df_out_ModuleEcpProdMaster.rename(columns = {'Item.[Pitch]': 'To Item.[To Item Pitch]', 'Item.[Project]': 'Project.[Project]'}, inplace=True)
        df_out_ModuleEcpProdMaster = df_out_ModuleEcpProdMaster[['Version.[Version Name]', 'Location.[Location]', 'Time.[Week]', 'To Item.[To Item Pitch]', 'Project.[Project]', 'Item.[LED Strategy]']]

        df_out_ModuleEcpProdMaster = pd.merge(df_out_ModuleEcpProdMaster, df_in_ModuleEcpProdMaster
                                             , on=['Version.[Version Name]', 'Location.[Location]', 'Time.[Week]', 'To Item.[To Item Pitch]', 'Project.[Project]', 'Item.[LED Strategy]']
                                             , how='left')

        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_Defect Rate'] = df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_Defect Rate'].ffill()
        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_Defect Rate'] = df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_Defect Rate'].fillna(1)
        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_Defect Rate.Lock'] = ''
        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_Defect Rate.Lock'] = np.where(df_out_ModuleEcpProdMaster['Time.[Week]'] <= VAL_FIXWEEK, 'True', 'False')

        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_SVC Rate'] = df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_SVC Rate'].ffill()
        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_SVC Rate'] = df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_SVC Rate'].fillna(1)
        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_SVC Rate.Lock'] = ''
        df_out_ModuleEcpProdMaster['Module Ecp Prod Master LED_SVC Rate.Lock'] = np.where(df_out_ModuleEcpProdMaster['Time.[Week]'] <= VAL_FIXWEEK, 'True', 'False')


        vdCommon.gfn_stepLog('=====> STEP 1.0 (End) : df_out_Module_Lie_Capa_LED 데이터 처리')

        vdCommon.gfn_saveDf(df_out_ModuleEcpProdMaster, 'df_out_ModuleEcpProdMaster', True)

    except Exception as ex:
        note(f'=====> try exception : {traceback.format_exc()}')
        note(f'An exception occurred: {ex}')

        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        # ouput Table 선언
        df_out_ModuleEcpProdMaster = pd.DataFrame([], columns=[])

    else:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        end_time = time.time()
        run_time_seconds = end_time - start_time
        run_time_minutes = run_time_seconds / 60
        formatted_time = datetime.datetime.fromtimestamp(end_time).strftime('%H:%M:%S')  # 초 단위를 datetime으로 변환하여 시분초 표시
        note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, Peak was {round(peak / 10 ** 6, 2)}MB, Execution time: {run_time_minutes:.4f} minutes')
        note(f'===================== plugin Execution End ({formatted_time}) =====================')

    finally:
        vdCommon.gfn_pyLog_end()
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()
        logger.Finish()

        vdCommon.gfn_stepLog('=====> Batch end')

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
