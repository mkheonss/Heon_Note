"""
* 프로그램명
    - PY_UI_CapaSimulationUpdate

* 내용
    - CapaSimulation UI를 Update하면, Item과 Line 우선순위에 따라서 SOP 배분.

* 변경이력
    - 2025.12.04 / 김신 / Create
    - 2026.01.20 / 김신 / 수정 4개 Meausre 추가
      - Measure.[Capa Simul_Base Capa Sec]
      - Measure.[Capa Simul_OT Sat Sec]
      - Measure.[Capa Simul_Capa Sec Total]
      - Measure.[Capa Simul_2nd Shift Sec]

* Input
    - df_in_LineModelList
      Select ([Location].[Location] * [Item].[Item] * [Item].[Inch] * [Time].[Week] * [Line].[Line] ) on row,
             ({Measure.[Line Model List_Qty], Measure.[Line Model List_Tact Time]}) on column
       where {[Version].[Version Name]};
       ※ 파이선 플러그인 호출시, paramOutVersion으로 Call

    - df_in_CapaSimul
     Select ([Location].[Location] * [Time].[Week] * [Line].[Line] * [Category].[Category] * [Group].[Group ID] ) on row,
            ({Measure.[Capa Simul_Capa Sec Total], Measure.[Capa Simul_Base Capa Mins], Measure.[Capa Simul_Open Line], Measure.[Capa Simul_OT Mins], Measure.[Capa Simul_Sat Mins], Measure.[Capa Simul_2nd Shift Mins], Measure.[Capa Simul_2nd Shift Eff]}) on column
      where {[Version].[Version Name]};
       ※ 파이선 플러그인 호출시, paramOutVersion으로 Call

    - df_in_TactTime
      Select ([Location].[Location] * [Item].[Item] * [Line].[Line] ) on row, ({Measure.[Tact Time_Time]}) on column where {[Version].[Version Name], [Item].[Item Stage].[SET], Measure.[Tact Time_Valid Asn] == TRUE};
      ※ 파이선 플러그인 호출시, paramOutVersion으로 Call

    - df_in_LineEff
      Select ([Location].[Location] * [Line].[Line] ) on row,
             ({Measure.[Line Eff Sub_IsUserEntry], Measure.[Line Eff Sub_IsAuto]}) on column
      where {[Version].[Version Name]};
      ※ 파이선 플러그인 호출시, paramOutVersion으로 Call

* Flow Summary
    STEP1. Location, Week별 Item 총량 계산.
    STEP2. Location, Week별 Line Capa 계산결과 Merge.
    STEP3. Location, Week별 Line 우선순위 결정.
    STEP4. Location, Week별 Item을 Line 우선순위에 따라 배분.

* Output Table
    - df_out_Capa_Simul_Update
      Select ([Version].[Version Name] * [Location].[Location] * [Group].[Group ID] * [Time].[Week] * [Category].[Category] * [Line].[Line] ) on row, 
            ({Measure.[Capa Simul_SOP Sec Total], Measure.[Capa Simul_SOP Pcs Total]}) on column;

* Execution
    - EXEC plugin instance [PY_UI_CapaSimulationUpdate]
      for measures {[Capa Simul_SOP Sec Total], [Capa Simul_SOP Pcs Total]}
      using scope ([Version].[Version Name].filter(#.Name == "{{fb_Version}}") * [Time].[Week].filter(#.Name == "{{fb_Week}}") * [Location].[Location].filter(#.Name == "{{fb_Location}}"))
      using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "{{fb_Version}}"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

"""
import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_CapaSimulationUpdate'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

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
log_level_info = LOG_LEVEL.info()
log_level_debug = LOG_LEVEL.debug()
logger.debug(f'[START] {str_instance}')
logger.Start()


########################################################################################################################
# local function
########################################################################################################################
class CustomException(Exception):
    pass


def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)

def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def step(string):
    vdCommon.gfn_stepLog(string)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, logger, is_local, log_path)

def vd_log_end() -> tuple:
    """
    로그 처리를 종료하고 로그 데이터프레임들을 반환하는 공통 함수

    Returns:
        tuple: (df_out_log, df_out_logDetail) 형태의 튜플
    """
    try:
        # 로그 종료 처리
        vdCommon.gfn_pyLog_end()

        # 로그 데이터프레임 가져오기
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()

        return df_out_log, df_out_logDetail

    except Exception as e:
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(target_df):
    new_df = target_df
    delete_dfs(target_df)
    return new_df


def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
        return df[column_name].values[0]
    return None  # 기본값 반환


def get_formatted_time(timestamp):
    """타임스탬프를 사람이 읽을 수 있는 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def format_size(size_in_bytes):
    """바이트 단위를 적절히 MB 또는 GB로 변환하여 문자열 반환"""
    if size_in_bytes >= 1024 ** 3:  # 1GB 이상일 때
        return f"{size_in_bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{size_in_bytes / 1024 ** 2:.1f} MB"


def run_time_minutes(start_time):
    """실행 시간을 계산하고, 소수점 2자리로 반환."""
    return str(round((time.time() - start_time) / 60, 2)) + " minutes"


########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # Batch 시작
    vd_log_start()

    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_LineModelList = read_csv_file("df_in_LineModelList")
            df_in_CapaSimul = read_csv_file("df_in_CapaSimul")
            df_in_TactTime = read_csv_file("df_in_TactTime")
            df_in_LineEff = read_csv_file("df_in_LineEff")

        print_df(df_in_LineModelList, 'STEP 1 - Input table load .... df_in_LineModelList')
        print_df(df_in_CapaSimul, 'STEP 1 - Input table load .... df_in_CapaSimul')
        print_df(df_in_TactTime, 'STEP 1 - Input table load .... df_in_TactTime')
        print_df(df_in_LineEff, 'STEP 1 - Input table load .... df_in_LineEff')
        step('=====> 전처리 End')

        ################################################################################################################
        # DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> DataFrame Column 변수 처리')
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        ITEM_COLUMN = 'Item.[Item]'
        ITEM_INCH_COLUMN = 'Item.[Inch]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        LINE_COLUMN = 'Line.[Line]'
        CATEGORY_COLUMN = 'Category.[Category]'
        GROUP_ID_COLUMN = 'Group.[Group ID]'
        LINE_MODEL_LIST_QTY_COLUMN = 'Line Model List_Qty'
        LINE_MODEL_LIST_TACT_TIME_COLUMN = 'Line Model List_Tact Time'
        CAPA_SIMUL_CAPA_SEC_TOTAL_COLUMN = 'Capa Simul_Capa Sec Total'
        CAPA_SIMUL_BASE_CAPA_MINS_COLUMN = 'Capa Simul_Base Capa Mins'
        CAPA_SIMUL_OPEN_LINE_COLUMN = 'Capa Simul_Open Line'
        CAPA_SIMUL_OT_MINS_COLUMN = 'Capa Simul_OT Mins'
        CAPA_SIMUL_SAT_MINS_COLUMN = 'Capa Simul_Sat Mins'
        CAPA_SIMUL_2ND_SHIFT_MINS_COLUMN = 'Capa Simul_2nd Shift Mins'
        CAPA_SIMUL_2ND_SHIFT_EFF_COLUMN = 'Capa Simul_2nd Shift Eff'
        TACT_TIME_TIME_COLUMN = 'Tact Time_Time'
        LINE_EFF_SUB_ISUSERENTRY_COLUMN = 'Line Eff Sub_IsUserEntry'
        LINE_EFF_SUB_ISAUTO_COLUMN = 'Line Eff Sub_IsAuto'

        step('=====> Column 변수 처리 End')

        ################################################################################################################
        # Step 1
        # df_in_LineModelList을 Location, Week, Item에 따라 [Line Model List_Qty]을 sum aggregation하여, df_ItemQty로 저장한다.
        # df_ItemQty의 [Line Model List_Qty] 칼럼 이름을 [Item Qty]로 정의한다.
        ################################################################################################################
        step('=====> STEP 1 Start : df_in_LineModelList을 Location, Week, Item에 따라 [Line Model List_Qty]을 '
             'sum aggregation하여, df_ItemQty로 저장한다.')
        df_ItemQty = df_in_LineModelList.copy()

        groupby_columns = [LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_COLUMN]
        sum_columns = [LINE_MODEL_LIST_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_ItemQty = df_ItemQty.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)

        df_ItemQty.rename(columns={LINE_MODEL_LIST_QTY_COLUMN: 'Item Qty',}, inplace=True)

        print_df(df_ItemQty, 'df_ItemQty', True)
        step('=====> STEP 1 End')
        ################################################################################################################
        # Step 2
        # df_in_TactTime에 모든 row에 대해 항상 1값을 갖는 [Line Count] 칼럼을 추가한다.
        ################################################################################################################
        step('=====> STEP 2(Start) : df_in_TactTime에 모든 row에 대해 항상 1값을 갖는 [Line Count] 칼럼을 추가한다.')
        df_TactTime_Work = df_in_TactTime.copy()
        df_TactTime_Work['Line Count'] = 1

        print_df(df_TactTime_Work, 'df_TactTime_Work', True)
        step('=====> STEP 2 End')
        ################################################################################################################
        # Step 3
        # df_in_TactTime을 Location, Item에 따라 [Line Count]을 sum aggregation한다.
        ################################################################################################################
        step('=====> STEP 3(Start) : df_in_TactTime을 Location, Item에 따라 [Line Count]을 sum aggregation한다.')
        groupby_columns = [LOCATION_COLUMN, ITEM_COLUMN]
        sum_columns = ['Line Count']
        agg_dict = {col: 'sum' for col in sum_columns}
        df_TactTime_Work = df_TactTime_Work.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)

        print_df(df_TactTime_Work, 'df_TactTime_Work', True)
        step('=====> STEP 3 End')
        ################################################################################################################
        # Step 4
        # df_in_LineModelList을 기준으로 Location, Item에 따라 df_in_TactTime의 [Line Count]를 Merge한다.
        # Line Count = 1 이면 1, Line Count > 1 이면 2인 값을 갖는 Line Group 필드를 추가
        ################################################################################################################
        step('=====> STEP 4(Start) : =====> STEP4(Start) : df_in_LineModelList을 기준으로 Location, Item에 따라 '
             'df_in_TactTime의 [Line Count]를 Merge한다.')
        df_LineModelList_Work = df_in_LineModelList.copy()

        df_LineModelList_Work = df_LineModelList_Work.merge(
            df_TactTime_Work[[LOCATION_COLUMN, ITEM_COLUMN, 'Line Count']],
            how='left',
            on=[LOCATION_COLUMN, ITEM_COLUMN])

        df_LineModelList_Work['Line Group'] = np.where(df_LineModelList_Work['Line Count'] == 1, 1, 2)

        print_df(df_LineModelList_Work, 'df_LineModelList_Work', True)
        step('=====> STEP 4 End')
        ################################################################################################################
        # Step 5
        # df_in_LineModelList을 기준으로 Location, Line에 따라 df_in_LineEff의 [Line Eff Sub_IsAuto]를 Merge한다.
        ################################################################################################################
        step('=====> STEP 5(Start) : df_in_LineModelList을 기준으로 Location, Line에 따라 df_in_LineEff의 '
             '[Line Eff Sub_IsAuto]를 Merge한다.')

        df_LineModelList_Work = df_LineModelList_Work.merge(
            df_in_LineEff[[LOCATION_COLUMN, LINE_COLUMN, LINE_EFF_SUB_ISAUTO_COLUMN]],
            how='left',
            on=[LOCATION_COLUMN, LINE_COLUMN])

        print_df(df_LineModelList_Work, 'df_LineModelList_Work', True)
        step('=====> STEP 5 End')
        ################################################################################################################
        # Step 6
        # df_in_LineModelList의 모든 row에 대해[Line Model List_]
        # df_in_LineModelList을 Location, Week, Line Count, Line Eff Sub_IsAuto, Line Model List_Tact Time, Inch,Line 순서대로 정렬한다.
        # [Location].[Location], [Time].[Week] ASC, Line Group ASC, [Line Eff Sub_IsAuto] DESC, [Line Model List_Tact Time] ASC,
        # [Item].[Inch] DESC, [Line].[Line]
        ################################################################################################################
        step('=====> STEP 6(Start) : df_in_LineModelList을 순서대로 정렬한다.')

        cList_temp = [LOCATION_COLUMN, TIME_WEEK_COLUMN, 'Line Group', LINE_EFF_SUB_ISAUTO_COLUMN,
                      LINE_MODEL_LIST_TACT_TIME_COLUMN, ITEM_INCH_COLUMN, LINE_COLUMN]

        df_LineModelList_Work = df_LineModelList_Work.sort_values(by=cList_temp,
                                                                  ascending=[True, True, True, False, True, False,
                                                                             True]).reset_index(drop=True)

        print_df(df_LineModelList_Work, 'df_LineModelList_Work', True)
        step('=====> STEP 6 End')
        ################################################################################################################
        # Step 7
        # df_in_CapaSimul에 모든 row에 대해 0 값을 갖는 새로운 칼럼 [Capa Simul_SOP Sec Total], [Capa Simul_SOP Pcs Total]을 추가한다.
        # Measure.[Capa Simul_Base Capa Sec]
        # Measure.[Capa Simul_OT Sat Sec]
        # Measure.[Capa Simul_2nd Shift Sec]
        # Measure.[Capa Simul_Capa Sec Total] 추가한다.
        ################################################################################################################
        step('=====> STEP 7(Start) : df_in_CapaSimul에 모든 row에 대해 0 값을 갖는 새로운 칼럼 '
             '[Capa Simul_SOP Sec Total], [Capa Simul_SOP Pcs Total]을 추가한다.')
        df_CapaSimul_Work = df_in_CapaSimul.copy()
        df_CapaSimul_Work.insert(0, VERSION_NAME_COLUMN, paramOutVersion)

        df_CapaSimul_Work[['Capa Simul_SOP Sec Total', 'Capa Simul_SOP Pcs Total']] = 0

        #df_CapaSimul_Work['Capa Simul_Base Capa Sec'] = df_CapaSimul_Work[CAPA_SIMUL_BASE_CAPA_MINS_COLUMN] * df_CapaSimul_Work[CAPA_SIMUL_OPEN_LINE_COLUMN] * 60
        #df_CapaSimul_Work['Capa Simul_OT Sat Sec'] = df_CapaSimul_Work[CAPA_SIMUL_OT_MINS_COLUMN] * 60 + df_CapaSimul_Work[CAPA_SIMUL_SAT_MINS_COLUMN] * 60
        #df_CapaSimul_Work[CAPA_SIMUL_2ND_SHIFT_EFF_COLUMN] = df_CapaSimul_Work[CAPA_SIMUL_2ND_SHIFT_EFF_COLUMN].fillna(1)
        #df_CapaSimul_Work['Capa Simul_2nd Shift Sec'] = df_CapaSimul_Work[CAPA_SIMUL_2ND_SHIFT_EFF_COLUMN] * df_CapaSimul_Work[CAPA_SIMUL_2ND_SHIFT_MINS_COLUMN] * 60
        #df_CapaSimul_Work['Capa Simul_Capa Sec Total'] = df_CapaSimul_Work['Capa Simul_Base Capa Sec'] + df_CapaSimul_Work['Capa Simul_OT Sat Sec'] + df_CapaSimul_Work['Capa Simul_2nd Shift Sec']

        print_df(df_CapaSimul_Work, 'df_CapaSimul_Work', True)
        step('=====> STEP 7 End')
        ################################################################################################################
        # Step 8
        # df_in_LineModelList을 맨 위 row부터 순서대로 아래 작업을 반복하여 수행한다.
        # df_in_LineModelList의 각 row는 [Location].[Location], [Time].[Week], [Item].[Item], [Line].[Line] 에 따라 Unique하게 정의.
        # 해당하는 row와 동일한 [Location].[Location], [Time].[Week], [Item].[Item]을 갖는 df_ItemQty의 [Item Qty] 참고.
        # 해당하는 row와 동일한 [Location].[Location], [Time].[Week], [Line].[Line]을 갖는 df_in_CapaSimul의 [Capa Simul_Capa Sec Total] 참고.
        #     Case1. [Item_Qty] <= ([Capa Simul_Capa Sec Total]  / [Line Model List_Tact Time])인 경우
        #            [Capa Simul_Capa Sec Total] = [Capa Simul_Capa Sec Total] - [Item Qty] * [Line Model List_Tact Time]
        #            [Capa Simul_SOP Sec Total] = [Capa Simul_SOP Sec Total] + [Item Qty] * [Line Model List_Tact Time]
        #            [Capa Simul_SOP Pcs Total] = [Capa Simul_SOP Pcs Total] + [Item Qty]
        #            [Item Qty] = 0
        #     Case2. [Item_Qty] > ([Capa Simul_Capa Sec Total]  / [Line Model List_Tact Time])인 경우
        #            Temp Qty = [Capa Simul_Capa Sec Total]  / [Line Model List_Tact Time]의 내림값.
        #            [Capa Simul_Capa Sec Total] = [Capa Simul_Capa Sec Total] - [Temp Qty] * [Line Model List_Tact Time]
        #            [Capa Simul_SOP Sec Total] = [Capa Simul_SOP Sec Total] + [Temp Qty] * [Line Model List_Tact Time]
        #            [Capa Simul_SOP Pcs Total] = [Capa Simul_SOP Pcs Total] + [Temp Qty]
        #            [Item Qty] = [Item Qty] - [Temp Qty]
        # ['Capa Simul_Capa Sec Total'] = ['Capa Simul_Base Capa Sec'] + ['Capa Simul_OT Sat Sec'] + ['Capa Simul_2nd Shift Sec'] 추가
        ################################################################################################################
        step('=====> STEP 8(Start) : df_in_LineModelList을 순서대로 아래 작업을 반복하여 수행한다')
        for idx, row in df_LineModelList_Work.iterrows():
            location = row[LOCATION_COLUMN]
            week = row[TIME_WEEK_COLUMN]
            item = row[ITEM_COLUMN]
            line = row[LINE_COLUMN]
            tact_time = row[LINE_MODEL_LIST_TACT_TIME_COLUMN]

            # 해당 row와 동일한 조건을 갖는 Item Qty 찾기
            item_mask = (
                    (df_ItemQty[LOCATION_COLUMN] == location) &
                    (df_ItemQty[TIME_WEEK_COLUMN] == week) &
                    (df_ItemQty[ITEM_COLUMN] == item)
            )

            # 해당 row와 동일한 조건을 갖는 Capa Simul_Sop 찾기
            capa_mask = (
                    (df_CapaSimul_Work[LOCATION_COLUMN] == location) &
                    (df_CapaSimul_Work[TIME_WEEK_COLUMN] == week) &
                    (df_CapaSimul_Work[LINE_COLUMN] == line)
            )

            if not item_mask.any() or not capa_mask.any():
                continue  # 해당 조건이 없으면 skip

            item_qty = df_ItemQty.loc[item_mask, 'Item Qty'].values[0]
            capa_sec_total = df_CapaSimul_Work.loc[capa_mask, CAPA_SIMUL_CAPA_SEC_TOTAL_COLUMN].values[0]
            sop_sec_total = df_CapaSimul_Work.loc[capa_mask, 'Capa Simul_SOP Sec Total'].values[0]
            sop_pcs_total = df_CapaSimul_Work.loc[capa_mask, 'Capa Simul_SOP Pcs Total'].values[0]

            # Case1
            if item_qty <= (capa_sec_total / tact_time):
                df_CapaSimul_Work.loc[
                    capa_mask, CAPA_SIMUL_CAPA_SEC_TOTAL_COLUMN] = capa_sec_total - item_qty * tact_time
                df_CapaSimul_Work.loc[capa_mask, 'Capa Simul_SOP Sec Total'] = sop_sec_total + item_qty * tact_time
                df_CapaSimul_Work.loc[capa_mask, 'Capa Simul_SOP Pcs Total'] = sop_pcs_total + item_qty
                df_ItemQty.loc[item_mask, 'Item Qty'] = 0
            # Case2
            if item_qty > (capa_sec_total / tact_time):
                temp_qty = int(np.floor(capa_sec_total / tact_time))
                df_CapaSimul_Work.loc[
                    capa_mask, CAPA_SIMUL_CAPA_SEC_TOTAL_COLUMN] = capa_sec_total - temp_qty * tact_time
                df_CapaSimul_Work.loc[capa_mask, 'Capa Simul_SOP Sec Total'] = sop_sec_total + temp_qty * tact_time
                df_CapaSimul_Work.loc[capa_mask, 'Capa Simul_SOP Pcs Total'] = sop_pcs_total + temp_qty
                df_ItemQty.loc[item_mask, 'Item Qty'] = item_qty - temp_qty
        # for end -------------------------------------------------------------------------
        #df_CapaSimul_Work['Capa Simul_Capa Sec Total'] = df_CapaSimul_Work['Capa Simul_Base Capa Sec'] + df_CapaSimul_Work['Capa Simul_OT Sat Sec'] + df_CapaSimul_Work['Capa Simul_2nd Shift Sec']

        df_CapaSimul_Work['Capa Simul_SOP Sec Total'] = df_CapaSimul_Work['Capa Simul_SOP Sec Total'].fillna(0).astype(float)
        df_CapaSimul_Work['Capa Simul_SOP Pcs Total'] = df_CapaSimul_Work['Capa Simul_SOP Pcs Total'].fillna(0).astype('Int64')

        print_df(df_CapaSimul_Work, 'df_CapaSimul_Work', True)
        step('=====> STEP 8 End')
        ################################################################################################################
        # STEP 9 : output table create
        ################################################################################################################
        step('=====> STEP 9 : Final output table create')

        #df_out_Capa_Simul_Update = df_CapaSimul_Work[
        #    [VERSION_NAME_COLUMN,LOCATION_COLUMN,TIME_WEEK_COLUMN,LINE_COLUMN,CATEGORY_COLUMN,GROUP_ID_COLUMN,
        #     'Capa Simul_Capa Sec Total', 'Capa Simul_SOP Sec Total', 'Capa Simul_SOP Pcs Total',
        #     'Capa Simul_Base Capa Sec', 'Capa Simul_OT Sat Sec', 'Capa Simul_2nd Shift Sec']]

        df_out_Capa_Simul_Update = df_CapaSimul_Work[
            [VERSION_NAME_COLUMN,LOCATION_COLUMN,TIME_WEEK_COLUMN,LINE_COLUMN,CATEGORY_COLUMN,GROUP_ID_COLUMN,
             'Capa Simul_SOP Sec Total', 'Capa Simul_SOP Pcs Total']]



        print_df(df_out_Capa_Simul_Update, 'df_out_Capa_Simul_Update', True)

        if is_local:
            step('=====> Output csv create')
            save_csv_file(df_out_Capa_Simul_Update, 'df_out_Capa_Simul_Update')
        step('=====> STEP 9 End')
        step('==============================================')
        step('==============================================')
        step('==============================================')
    except Exception as e:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        df_out_Capa_Simul_Update = pd.DataFrame([], columns=[])

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()