"""

* 프로그램명
    - PY_UI_CodeMapLCMCreateBOD

* 내용
    - LCM BOD & Product Copy > Create BOD
    - code Map LCM 의 데이타로 BOD List의 TP mode 만큼 확장 row 생성, 생성 data 와 BOD Item 에 없는  data 생성 하는 로직

* Input
- df_in_lcmBodList :
- df_in_codeMapLCM :
- df_in_bodItem :

* Flow Summary
          1) df_codeMapLcm 를 메인으로 df_lcmBolList 와(version, Location, Sub Location) 기준 inner merge
            -> df_lcmBolList 와 df_codeMapLcm 양쪽에 모두 존재하는 Key 만 남김
            -> df_lcmBolList 에서 TP Mode 를 가져와 df_merge 생성
          2) df_merge 와 df_bodItem 를 (version, Location, Sub Location, TP Mode, Item) 기준으로 비교
          3) df_bodItem 에 동일 Key 가 없는 df_merge 행만 df_out 으로 생성

* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2025.05.15 / syif1380.lee / Create
    - 2025.05.16 / syif1380.lee / [Trans Mode].[Trans Mode] => &NSUITransModeView 네임셋으로 변경 LCM BOD List 에서 Tp mode 를 네임셋으로 사용 함
    - 2026.01.27 / syif1380.lee / Input Table 데이터 없을 경우 Header 생성하여 오류 방지, _Inherit (삭제된 메저 정리)
    - 2026.03.25 / syif1380.lee / df_in_bodList -> df_in_lcmBodList 변경 및 Grain 변경 소스 전체 정리
    - 2026.04.09 / syif1380.lee / df_in_lcmBodList : 업데이트용 메저 추가 ( df_in_lcmBodList -> df_in_bodItem )
                                - Measure.[LCM BOD List_BOD Name], Measure.[LCM BOD List_Time Phased Priority], Measure.[LCM BOD List_Time Phased Shipment LT], Measure.[LCM BOD List_Time Phased Transit Time]
    - 2026.04.10 / Sangyub Lee  / df_out[BODItem_LockFlag] False -> N 으로변경

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table

    --------------------------------------------------------------------------------------------------------------------
    ## 2026.03.25 : BOD List -> LCM BOD List 로 MG 변경
    --------------------------------------------------------------------------------------------------------------------
    - df_in_lcmBodList : UI 에서 Row 선택한 Location, Sub Location

        ### Input Table ###
        Select ( [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Item].[Class Category] ) on row,
        ({Measure.[LCM BOD List_BOD Priority], Measure.[LCM BOD List_Shipment LT], Measure.[LCM BOD List_Transit Time],Measure.[LCM BOD List_BOD Valid],Measure.[LCM BOD List_Eff Enddate],Measure.[LCM BOD List_Eff Startdate],Measure.[LCM BOD List_Eff Endweek],Measure.[LCM BOD List_Eff Startweek]
         ,Measure.[LCM BOD List_BOD Name], Measure.[LCM BOD List_Time Phased Priority], Measure.[LCM BOD List_Time Phased Shipment LT], Measure.[LCM BOD List_Time Phased Transit Time]}) on column
        where { [Version].[Version Name] ,Measure.[LCM BOD List_BOD Valid] == "Y" ,coalesce(Measure.[LCM BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() ,coalesce(Measure.[LCM BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now() };

        ### 테스트 쿼리 ###
        Select ( [Location].[Location].[P105LCD] * [Item].[Class Category]
        * [Trans Mode].[Trans Mode] * [Sub Location].[Sub Location].[P105] ) on row,
        ({Measure.[LCM BOD List_BOD Priority], Measure.[LCM BOD List_Shipment LT], Measure.[LCM BOD List_Transit Time]
        ,Measure.[LCM BOD List_BOD Valid]
        ,Measure.[LCM BOD List_Eff Enddate]
        ,Measure.[LCM BOD List_Eff Startdate]
        ,Measure.[LCM BOD List_Eff Endweek]
        ,Measure.[LCM BOD List_Eff Startweek]
        ,Measure.[LCM BOD List_BOD Name], Measure.[LCM BOD List_Time Phased Priority], Measure.[LCM BOD List_Time Phased Shipment LT], Measure.[LCM BOD List_Time Phased Transit Time]  // 2026.04.09 메저 추가
        }) on column
        where {
        &cwvui
        ,Measure.[LCM BOD List_BOD Valid] == "Y"
        ,coalesce(Measure.[LCM BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now()
        ,coalesce(Measure.[LCM BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()
        };

    --------------------------------------------------------------------------------------------------------------------
    ** 2026.03.25
    --------------------------------------------------------------------------------------------------------------------
    - df_in_codeMapLCM : UI 에서 Row 선택한 Location, Sub Location, Item

        ### Input Table ###
        Select ([Version].[Version Name] * [Location].[Location] * [Sub Location].[Sub Location] * [Item].[Class Category]  * [Item].[Item] * [To Item].[To Item] ) on row,
        ({ Measure.[Code Map LCM_Create BOD_Target Flag] }) on column where { Measure.[Code Map LCM_Create BOD_Target Flag] == true };

        ### 테스트 쿼리 ###
        Select (&cwvui * [Location].[Location].[P105LCD] * [Sub Location].[Sub Location].[P105] * [To Item].[To Item]
        * [Item].[Item]
        // * [Item].[Item].filter(#.Name in {"BN90-12360C","BN90-12731A"})
        * [Item].[Class Category] ) on row,
        ({ Measure.[Code Map LCM_Create BOD_Target Flag]
        }) on column
        where {
        Measure.[Code Map LCM_Create BOD_Target Flag] == true
        };

    --------------------------------------------------------------------------------------------------------------------
    ** 2026.03.25
    --------------------------------------------------------------------------------------------------------------------
    - df_in_bodItem : UI 에서 Row 선택한 Location, Sub Location, Item

        ### Input Table ###
        Select ([Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Item].[Item]  ) on row,
        ({ Measure.[BOD Item_Asn],Measure.[BOD Item_BOD Valid]}) on column where { [Version].[Version Name] } limit 1000;

        ### 테스트 쿼리 ###
        Select ([Location].[Location].[P105LCD] * [Sub Location].[Sub Location].[P105]
        * [Trans Mode].[Trans Mode]
        * [Item].[Item]
         ) on row,
        ({ Measure.[BOD Item_Asn],Measure.[BOD Item_BOD Valid]}) on column
        where { &cwvui } limit 100;
    --------------------------------------------------------------------------------------------------------------------

* Output Table :
   - df_out_bodItem :

* 테스트 스크립트
     /* Validation 호출 (PY_UI_CodeMapLCMCreateBOD) */
 EXEC plugin instance [PY_UI_CodeMapLCMCreateBOD] for measures {[Code Map LCM_Create BOD_Target Flag]}
 using scope ( &CWVUI * [Location].[Location].[P105LCD] * [Sub Location].[Sub Location].[P105]
 * [Item].[Item].filter(#.Name in {"BN95-03201C", "BN95-02600B"}) )
 using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

"""

########################################################################################################################
# NSCMCommon - start
########################################################################################################################
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
str_instance = 'PY_UI_CodeMapLCMCreateBOD'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = (
    "CWV_MP"
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
    try:
        file_path = f"{file_name}.csv"
        if not os.path.exists(file_path):
            step(f"=====> 파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame()  # 빈 DataFrame 반환
        return pd.read_csv(file_path, low_memory=False, encoding="UTF-8")

    except Exception as e:
        step(f"=====> CSV 파일 읽기 실패: {file_name}, 오류: {str(e)}")
        return pd.DataFrame()  # 에러 발생시 빈 DataFrame 반환


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
        # setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(df):
    """데이터프레임 최적화 및 메모리 사용량 감소"""
    if df is None:
        return None

    # 데이터프레임 복사 및 메모리 최적화
    result = df.copy()

    # 숫자형 컬럼의 데이터 타입 최적화
    for col in result.select_dtypes(include=['int', 'float']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')

    # # 범주형 데이터 최적화
    # for col in result.select_dtypes(include=['object']).columns:
    #     if result[col].nunique() / len(result) < 0.5:  # 고유값이 50% 미만일 경우
    #         result[col] = result[col].astype('category')

    delete_dfs(df)
    return result


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
    """실행 시간을 계산하고, 분 또는 초 단위로 반환.
    초 단위가 0일 경우 초로 표시하고, 그 외에는 분으로 표시."""
    elapsed = time.time() - start_time
    if elapsed < 60:  # 1분 미만일 경우
        return str(round(elapsed, 2)) + " seconds"
    else:
        return str(round(elapsed / 60, 2)) + " minutes"


def filter_dataframe(dataframe, version_column, time_week_column, pre_version, plan_horizon):
    return dataframe.loc[
        (dataframe[version_column] != pre_version) &
        (dataframe[time_week_column].isin(plan_horizon[time_week_column]))
        ].copy()


########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    # Batch 시작
    vd_log_start()
    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_lcmBodList = read_csv_file("df_in_lcmBodList")
            df_in_codeMapLCM = read_csv_file("df_in_codeMapLCM")
            df_in_bodItem = read_csv_file("df_in_bodItem")

        dataframes = {
            'df_in_lcmBodList': df_in_lcmBodList,
            'df_in_codeMapLCM': df_in_codeMapLCM,
            'df_in_bodItem': df_in_bodItem,
        }

        for name, df in dataframes.items():
            if df is None:
                step(f'=====> input table : None')
            elif df.empty:
                step(f'=====> input table : empty DataFrame : {name}')
            else:
                print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수 선언 - Dimension
        VersionName = 'Version.[Version Name]'
        Location = 'Location.[Location]'
        SubLocation = 'Sub Location.[Sub Location]'
        TPMode = 'Trans Mode.[Trans Mode]'
        Item = 'Item.[Item]'
        ToItem = 'To Item.[To Item]'
        ItemCategory = 'Item.[Class Category]'          # LCM BOD List (Grain), Code Map LCM 에는 참조용으로 사용(Grain X)

        # 컬럼 변수 선언 - BOD List (Measure Group)
        BODList_BODLT = 'LCM BOD List_Transit Time'
        BODList_Priority = 'LCM BOD List_BOD Priority'
        BODList_ShipmentLT = 'LCM BOD List_Shipment LT'
        BODList_EffStartdate = 'LCM BOD List_Eff Startdate'
        BODList_EffEnddate = 'LCM BOD List_Eff Enddate'
        BODList_EffStartweek = 'LCM BOD List_Eff Startweek'
        BODList_EffEndweek = 'LCM BOD List_Eff Endweek'
        # 2026.04.09 메저 추가
        BODList_BODName = 'LCM BOD List_BOD Name'
        BODList_TimePhasedPriority = 'LCM BOD List_Time Phased Priority'
        BODList_TimePhasedShipmentLT = 'LCM BOD List_Time Phased Shipment LT'
        BODList_TimePhasedTransitTime = 'LCM BOD List_Time Phased Transit Time'

        # 컬럼 변수 선언 - Code Map LCM (Measure Group)
        CodeMapLCM_ProdItem = 'Code Map LCM_Prod Item'

        # 컬럼 변수 선언 - BOD Item (Measure Group)
        BODItem_Asn = 'BOD Item_Asn'
        BODItem_CurStatus = 'BOD Item_Cur Status'
        BODItem_LockFlag = 'BOD Item_Lock Flag'
        BODItem_ProdItem = 'BOD Item_Prod Item'
        BODItem_BODLT = 'BOD Item_BOD LT'
        BODItem_Priority = 'BOD Item_Priority'
        BODItem_ShipmentLT = 'BOD Item_Shipment LT'
        BODItem_EffEnddate = 'BOD Item_Eff Enddate'
        BODItem_EffStartdate = 'BOD Item_Eff Startdate'
        BODItem_EffEndweek = 'BOD Item_Eff Endweek'
        BODItem_EffStartweek = 'BOD Item_Eff Startweek'
        BODItem_UpdatedBy = 'BOD Item_Updated By'
        # 2026.04.09 메저 추가
        BODItem_BODName = 'BOD Item_BOD Name'
        BODItem_TimePhasedPrty= 'BOD Item_Time Phased Prty'
        BODItem_TimePhasedShipment= 'BOD Item_Time Phased Shipment'
        BODItem_TimePhasedBOD= 'BOD Item_Time Phased BOD'
        BODItem_BODValid= 'BOD Item_BOD Valid'
        BODItem_MaterialGroup= 'BOD Item_Material Group'

        lcm_bod_list_cols = [
            Location, SubLocation, TPMode, ItemCategory,
            BODList_EffStartdate, BODList_EffEnddate, BODList_EffStartweek, BODList_EffEndweek,
            BODList_BODLT, BODList_Priority, BODList_ShipmentLT,
            BODList_BODName, BODList_TimePhasedPriority, BODList_TimePhasedShipmentLT, BODList_TimePhasedTransitTime,
        ]

        code_map_lcm_cols = [
            Location, SubLocation, Item, ToItem, ItemCategory,
        ]

        bod_item_cols = [
            Location, SubLocation, TPMode, Item,
            BODItem_ProdItem, BODItem_Asn, BODItem_CurStatus, BODItem_LockFlag,
            BODItem_EffEnddate, BODItem_EffStartdate, BODItem_EffEndweek, BODItem_EffStartweek,
            BODItem_BODLT, BODItem_Priority, BODItem_ShipmentLT,
            BODItem_UpdatedBy,
            BODItem_BODName, BODItem_TimePhasedPrty, BODItem_TimePhasedShipment, BODItem_TimePhasedBOD,
            BODItem_BODValid, BODItem_MaterialGroup,
        ]

        # LCM BOD List : Grain
        lcm_bod_list_final_cols = [VersionName] + lcm_bod_list_cols

        # Code Map LCM : Grain
        code_map_lcm_final_cols = [VersionName] + code_map_lcm_cols

        # BOD Item : Grain
        bod_item_final_cols = [VersionName] + bod_item_cols

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_lcmBodList.empty:
            raise CustomException("STEP3 by 0 ____ df_in_lcmBodList  값이 없습니다.")

        if df_in_codeMapLCM.empty:
            raise CustomException("STEP3 by 0 ____ df_in_codeMapLCM  값이 없습니다.")

        # 현재 날짜 시간
        # current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        step(f'=====> current_date : {current_date}')

        step('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 : LCM BOD List , Code Map LCM : mgerge (inner join)
        # 처리 순서
        #             1) df_in_codeMapLCM 를 메인으로 df_in_lcmBodList 와(version, Location, Sub Location) 기준 inner merge
        #                 -> df_in_lcmBodList 와 df_in_codeMapLCM 양쪽에 모두 존재하는 Key 만 남김
        #                 -> df_in_lcmBodList 에서 TP Mode 를 가져와 df_merge 생성
        #             2) df_merge 와 df_in_bodItem 를 (version, Location, Sub Location, TP Mode, Item) 기준으로 비교
        #             3) df_in_bodItem 에 동일 Key 가 없는 df_merge 행만 df_out 으로 생성
        ################################################################################################################
        #     df_in_lcmBodList : version, Location, Sub Location, TP Mode, Class Category
        #     df_in_codeMapLCM : version, Location, Sub Location, Class Category, Item, To Item
        #     df_in_bodItem    : version, Location, Sub Location, TP Mode, Item
        ################################################################################################################

        ############################################################################################################
        # 1. 머지에 사용할 key 정의
        ############################################################################################################
        key_com = [Location, SubLocation, ItemCategory]
        key_item = [Location, SubLocation, TPMode, Item]

        ############################################################################################################
        # 2. df_in_lcmBodList 에서 필요한 컬럼만 추출
        #   - df_in_codeMapLCM 와 머지할 때 TPMode 만 가져오면 되므로
        #     불필요한 Measure 는 제거 가능
        ############################################################################################################
        df_list_key = df_in_lcmBodList[lcm_bod_list_cols].copy()

        ############################################################################################################
        # 3. df_in_lcmBodList 의 measure 타입 정리
        #   - 날짜형 유지
        #   - 문자열 유지
        #   - nullable integer 로 유지
        ############################################################################################################
        # df_list_key[BODList_EffStartdate] = pd.to_datetime(df_list_key[BODList_EffStartdate],
        #                                                    errors="coerce").astype("string")
        # df_list_key[BODList_EffEnddate] = pd.to_datetime(df_list_key[BODList_EffEnddate],
        #                                                    errors="coerce").astype("string")

        # df_list_key[BODList_EffStartdate] = df_list_key[BODList_EffStartdate].astype("object")
        # df_list_key[BODList_EffEnddate] = df_list_key[BODList_EffEnddate].astype("object")

        # 문자열
        df_list_key[BODList_EffStartweek] = df_list_key[BODList_EffStartweek].astype("string")
        df_list_key[BODList_EffEndweek] = df_list_key[BODList_EffEndweek].astype("string")

        # integer
        df_list_key[BODList_BODLT] = df_list_key[BODList_BODLT].astype("Int64")
        df_list_key[BODList_Priority] = df_list_key[BODList_Priority].astype("Int64")
        df_list_key[BODList_ShipmentLT] = df_list_key[BODList_ShipmentLT].astype("Int64")

        print_df(df_list_key, 'STEP5 by 4.2  ____ df_list_key')

        ############################################################################################################
        # 4. df_in_codeMapLCM 를 메인으로 df_in_lcmBodList 와 inner merge
        #   - inner 이므로 df_in_lcmBodList, df_in_codeMapLCM 양쪽에 모두 key 가 있어야만 남음
        #   - 결과  df_merge 에 TPMode 컬럼이 추가 됨
        ############################################################################################################
        df_merge = pd.merge(
            df_in_codeMapLCM,
            df_list_key,
            how='inner',
            on=key_com
        )
        print_df(df_merge, 'STEP5 by 4.3  ____ df_merge')

        if df_merge.empty:
            raise CustomException("STEP3 by 4 ____ df_merge : LCM BOD List, Code Map LCM 매핑 데이터 없음.")

        ############################################################################################################
        # 5. df_bodItem 와 비교할 때는 df_bodItem 쪽 key만 있으면 되므로
        #   중복 제거 후 비교용 key DataFrame 생성
        ############################################################################################################
        df_bodItem_key = df_in_bodItem[key_item].drop_duplicates().copy()

        ############################################################################################################
        # 7. df_merge 와 df_bodItem 를 left merge 하여
        #   df_bodItem 에 존재 여부를 _merge 컬럼으로 확인
        ############################################################################################################
        df_check = pd.merge(
            df_merge,
            df_bodItem_key,
            how='left',
            on=key_item,
            indicator=True
        )
        print_df(df_check, 'STEP5 by 4.5  ____ df_check')
        ############################################################################################################
        # 6. _df_merge == 'left_only'
        #   -> df_merge 에는 있고 df_bodItem 에는 없는 key
        #   -> 즉, 원하는 df_out
        ############################################################################################################
        df_out = df_check[df_check['_merge'] == 'left_only'].copy()
        print_df(df_out, 'STEP5 by 4.6  ____ df_out')

        ############################################################################################################
        # 7. 컬럼명 기본값 세팅 및 Rename
        ############################################################################################################
        if not df_out.empty:

            df_out[BODList_EffStartdate] = pd.to_datetime(df_out[BODList_EffStartdate],
                                                          format='%Y-%m-%d', errors="coerce")
            df_out[BODList_EffEnddate] = pd.to_datetime(df_out[BODList_EffEnddate],
                                                          format='%Y-%m-%d', errors="coerce")

            # 필수 컬럼 추가
            df_out[BODItem_Asn] = 1
            df_out[BODItem_LockFlag] = "N"  # data 상속 flag # 2026.04.10 수정
            df_out[BODItem_CurStatus] = "ACTIVE"
            df_out[BODItem_UpdatedBy] = str_instance    # PY_UI_CodeMapLCMCreateBOD
            df_out[BODItem_BODValid] = "Y"  # 2026.04.09 추가

            # 컬럼명 변경
            # 2026.04.09 추가
            # BODList_BODName , BODList_TimePhasedPriority, BODList_TimePhasedShipmentLT, BODList_TimePhasedTransitTime, BODItem_MaterialGroup
            df_out.rename(
                columns={BODList_BODLT: BODItem_BODLT
                    , BODList_Priority: BODItem_Priority
                    , BODList_ShipmentLT: BODItem_ShipmentLT
                    , BODList_EffStartdate: BODItem_EffStartdate
                    , BODList_EffEnddate: BODItem_EffEnddate
                    , BODList_EffStartweek: BODItem_EffStartweek
                    , BODList_EffEndweek: BODItem_EffEndweek
                    , ToItem: BODItem_ProdItem
                    , BODList_BODName: BODItem_BODName
                    , BODList_TimePhasedPriority:BODItem_TimePhasedPrty
                    , BODList_TimePhasedShipmentLT:BODItem_TimePhasedShipment
                    , BODList_TimePhasedTransitTime:BODItem_TimePhasedBOD
                    , ItemCategory:BODItem_MaterialGroup
                    },
                inplace=True)

            df_out_bodItem = df_out[bod_item_final_cols].drop_duplicates().copy()
        else:
            df_out_bodItem = pd.DataFrame(columns=[bod_item_final_cols])

        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        print_df(df_out_bodItem, 'STEP5 by 5.1  ____ df_out_bodItem')

        dataframesOut = {
            'df_out_bodItem': df_out_bodItem,
        }

        for name, df in dataframesOut.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_bodItem = pd.DataFrame(columns=bod_item_final_cols)

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_bodItem = pd.DataFrame(columns=bod_item_final_cols)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
