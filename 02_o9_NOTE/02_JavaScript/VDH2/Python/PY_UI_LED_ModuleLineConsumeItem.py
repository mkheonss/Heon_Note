"""
* 프로그램명
    - PY_UI_LED_ModuleLineConsumeItem

* 내용
    - Module Line Capa Master LED_Capa Consume Item Data Generation

* 변경이력
    - 2025.03.19 / 황수혁 / Create
    - 2025.04.15 / 김교승 / Update
    - 2026.02.09 / 김교승 / Update / MF Site Stage -> Site Stage 로 변경

* Flow Summary
    - Module Line Capa Master LED_Capa Consume Item Measure Data 생성

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP

* Input Tables
    - df_in_Module_LED_Capa_Consume_Grp : Select ([Version].[Version Name] * [To Item].[To Item Pitch] * [Project].[Project] * [Item].[LED Strategy] * [Product Type].[Product Type] * [Type F].[Type F]) on row, ({Measure.[Module Line Capa Master LED_Capa Consume Grp]}) on column;
    - df_in_Item_Site_Association : Select ([Version].[Version Name] * [Location].[Location]  * [Item].[Item] * &LEDStrategy * [Item].[Project] * [Item].[Pitch] * [Item].[ProductType] * [Item].[Model Name]) on row, ({Measure.[Item Site Asn_Actual Flag], Measure.[Dummy]})  on column where {[Location].[Site Stage].filter(#.Name contains "SET"), [Location].[Location Type].[MF]};
    - df_in_ModuleLineConsumeItem: Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item]) on row, ({Measure.[Module Line Capa Master LED_Capa Consume Item], Measure.[Module Line Capa Master LED_Capa Consume Item_Lock Flag]}) on column;

* Output Tables :
    - df_out_ModuleLineConsumeItem

* 테스트 스크립트
    - EXEC plugin instance [PY_UI_LED_ModuleLineConsumeItem] for Measures {[Module Line Capa Master LED_Capa Consume Item]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_ModuleLineConsumeItem : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Item].[Item]) on row, ({Measure.[Module Line Capa Master LED_Capa Consume Item], Measure.[Module Line Capa Master LED_Capa Consume Item_Lock Flag]}) on column;


"""
import time
import traceback
import datetime
import os
import warnings
import pandas as pd
import tracemalloc

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon


########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_LED_ModuleLineConsumeItem'
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

def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    memory_using = str(round(df.memory_usage(deep=True).sum() / (1024**2), 2)) + " MB"
    row_count, col_count = df.shape

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
            df_in_Module_LED_Capa_Consume_Grp = read_csv_file("df_in_Module_LED_Capa_Consume_Grp")
            df_in_Item_Site_Association = read_csv_file("df_in_Item_Site_Association")
            df_in_ModuleLineConsumeItem = read_csv_file("df_in_ModuleLineConsumeItem")

        vdCommon.gfn_saveDf(df_in_Module_LED_Capa_Consume_Grp, 'df_in_Module_LED_Capa_Consume_Grp')
        vdCommon.gfn_saveDf(df_in_Item_Site_Association, 'df_in_Item_Site_Association')
        vdCommon.gfn_saveDf(df_in_ModuleLineConsumeItem, 'df_in_ModuleLineConsumeItem')

        vdCommon.gfn_stepLog('=====> STEP (End) : 모듈 내에서 사용될 input table load')


        ################################################################################################################
        # STEP : 데이터 선 가공
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP (Start) : 데이터 선 가공')

        df_in_Item_Site_Association = df_in_Item_Site_Association.drop(['Item Site Asn_Actual Flag', 'Dummy'], axis=1, errors='ignore')
        df_in_Item_Site_Association.rename(
            columns={'Item.[Pitch]': 'To Item.[To Item Pitch]', 'Item.[Project]': 'Project.[Project]',
                     'Item.[ProductType]': 'Product Type.[Product Type]'}, inplace=True)
        df_in_Item_Site_Association['Type F.[Type F]'] = df_in_Item_Site_Association['Item.[Model Name]'].apply(
            lambda x: 'F' if x.endswith('-F') else '-')
        df_in_Item_Site_Association = df_in_Item_Site_Association.drop('Item.[Model Name]', axis=1, errors='ignore')

        df_ModuleLineConsumeItem = pd.merge(df_in_Item_Site_Association, df_in_Module_LED_Capa_Consume_Grp
                                            , on=['Version.[Version Name]', 'To Item.[To Item Pitch]',
                                                  'Project.[Project]', 'Item.[LED Strategy]',
                                                  'Product Type.[Product Type]', 'Type F.[Type F]']
                                            , how='inner')
        df_ModuleLineConsumeItem.drop(['To Item.[To Item Pitch]', 'Project.[Project]', 'Item.[LED Strategy]', 'Product Type.[Product Type]', 'Type F.[Type F]'], axis=1, inplace=True)
        vdCommon.gfn_saveDf(df_ModuleLineConsumeItem, 'df_ModuleLineConsumeItem')

        vdCommon.gfn_stepLog('=====> STEP (End) : 데이터 선 가공')

        ################################################################################################################
        # STEP : 변수 처리
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP (Start) : 변수 처리')

        vdCommon.gfn_stepLog('=====> STEP (End) : 변수 처리')

        ################################################################################################################
        # STEP 1.0 : df_out_ModuleLineConsumeItem 데이터 처리
        ##########################################################################n######################################
        vdCommon.gfn_stepLog('=====> STEP 1.0 (Start) : df_out_Module_Lie_Capa_LED 데이터 처리')
        df_out_ModuleLineConsumeItem = pd.merge(df_ModuleLineConsumeItem, df_in_ModuleLineConsumeItem
                                              , on=['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]']
                                              , how='left')
        vdCommon.gfn_saveDf(df_out_ModuleLineConsumeItem, 'df_out_ModuleLineConsumeItem')

        del_idx = df_out_ModuleLineConsumeItem[(df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Item_Lock Flag'] == True) |
                                               (df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Grp'] ==
                                                df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Item'])].index

        df_out_ModuleLineConsumeItem.drop(del_idx, inplace=True)
        df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Item'] = df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Item'].astype(float)
        df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Item_Lock Flag'] = df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Item_Lock Flag'].astype(bool)
        df_out_ModuleLineConsumeItem['Module Line Capa Master LED_Capa Consume Item_Lock Flag'] = False

        df_out_ModuleLineConsumeItem = df_out_ModuleLineConsumeItem.drop('Module Line Capa Master LED_Capa Consume Item', axis=1, errors='ignore')
        df_out_ModuleLineConsumeItem.rename(columns={'Module Line Capa Master LED_Capa Consume Grp': 'Module Line Capa Master LED_Capa Consume Item'}, inplace=True)
        df_out_ModuleLineConsumeItem = df_out_ModuleLineConsumeItem[['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]', 'Module Line Capa Master LED_Capa Consume Item', 'Module Line Capa Master LED_Capa Consume Item_Lock Flag']]
        note('--------------------> 3')

        vdCommon.gfn_stepLog('=====> STEP 1.0 (End) : df_out_Module_Lie_Capa_LED 데이터 처리')

        vdCommon.gfn_saveDf(df_out_ModuleLineConsumeItem, 'df_out_ModuleLineConsumeItem', True)

    except Exception as ex:
        note(f'=====> try exception : {traceback.format_exc()}')
        note(f'An exception occurred: {ex}')

        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        # ouput Table 선언
        df_out_ModuleLineConsumeItem = pd.DataFrame([], columns=[])

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
