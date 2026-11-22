"""
* 프로그램명
    - PY_UI_MtrlBODItem

* 내용
    - W Demand Build Ahead Limit으로 SP_MGS_MAXSTOCK Logic을 바탕으로 W Quantity Max Target 정보 변형하기

* 변경이력
    - 2025.10.16 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_ItemMeterial  : Select ([Item Material].[Item Material] ) on row, ({Measure.[Mtrl Attr_20FT], Measure.[Mtrl Attr_40FT], Measure.[Mtrl Attr_40FT HC], Measure.[Mtrl Attr_Pallet]}) on column where {[Version].[Version Name]};
    - df_in_BODTOP        : Select ([Item Material].[MSL1] * &NSUILocVendorBODView * &MDMHorizon * &NSUIMtrlMSL3View * &NSUISubLocationMFMtrlView * &NSUITransModeMtrlView ) on row, ({Measure.[BOD List Mtrl W_Factory Out], Measure.[BOD List Mtrl W_GR LT], Measure.[BOD List Mtrl W_Intransit LT], Measure.[BOD List Mtrl W_Port To Port], Measure.[BOD List Mtrl_EFF Startdate], Measure.[BOD List Mtrl_EFF Enddate], Measure.[BOD List Mtrl_Lot Type], Measure.[BOD List Mtrl_Priority], Measure.[BOD List Mtrl_Time Varying Flag]}) on column where {[Version].[Version Name]};
    - df_in_BODItemMap    : Select ([Location].[Location] * [Item Material].[MSL1] * [Item Material].[MSL3] * &NSUIMtrlItemView * [Global Top].[GT Code]) on row, ({Measure.[Vendor Mtrl_GT Name], Measure.[Vendor Mtrl_Master Ecp Flag], Measure.[Vendor Mtrl_Master Flag], Measure.[Vendor Mtrl_Quota], Measure.[Vendor Mtrl_Result Ecp Flag], Measure.[Vendor Mtrl_Result Flag]}) on column where {[Version].[Version Name]};
    - df_in_BODBottoMLock : Select ([Item Material].[MSL1] * [Location].[Location] * [Item Material].[MSL3] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] * [Item Material].[Item Material] ) on row, ({Measure.[BOD Item Mtrl_Lock Flag]}) on column where {[Version].[Version Name].[CWV_MP] , [Location].[Location],Measure.[BOD Item Mtrl_Lock Flag] in {"Y"}};

* Flow Summary
    - STEP1 : BOD_TOP 과 BOD_ITEM_MAP 을 JOIN 하여, 데이터 생성 ( BOD_TOP_ITEM_MERGE)
    - STEP2 : Step 1 에서 생성한 BOD_TOP_ITEM_MERGE 에서 사용자가 Lock 설정한 데이터 삭제
              BOD_TOP_ITEM_MERGE 와 BOD_BOTTOM_LOCK 의 Key가 일치하는 데이터 제외 (BOD_TOP_ITEM_MERGE_MERGE)
    - STEP3 : 결과 저장

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_BODItemMtrlW
    - df_out_BODItemMtrl

* 데이타 초기화
    - DELETE DATA FOR MODEL [BOD Item Mtrl W] WHERE {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};
    - DELETE DATA FOR MODEL [BOD Item Mtrl] WHERE  {[Version].[Version Name].filter(#.Name in {"CWV_MP"})};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_MtrlBODItem] for measures {[BOD Item Mtrl W_Factory Out]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - BOD_ITEM_MTRL_W
        Select (&MPV * [Location].[Location] * [Time].[Week] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
            ({Measure.[BOD Item Mtrl W_Factory Out], Measure.[BOD Item Mtrl W_GR LT], Measure.[BOD Item Mtrl W_Intransit LT], Measure.[BOD Item Mtrl W_Port To Port], Measure.[BOD Item Mtrl W_Supplier], Measure.[BOD Item Mtrl W_Total LT]}) on column limit 100;
    - BOD_ITEM_MTRL
        Select (&MPV * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
            ({Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_Lot Type]}) on column;

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
str_instance = 'PY_UI_MtrlBODItem'
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
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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



def set_unique_combinations(df, df2, columns):
    cols = list(filter(lambda col: col != TIME_WEEK_COLUMN, columns))

    # 데이터의 모든 고유 조합 생성
    unique_combinations = df[cols].copy().drop_duplicates()

    # 주차(TIME_WEEK_COLUMN) 데이터의 모든 조합 산출
    df2 = df2.assign(key=1)
    unique_combinations = unique_combinations.assign(key=1)
    all_possible_combinations = unique_combinations.merge(df2, how="outer").drop(columns=['key']).drop_duplicates()

    # 결측 데이터 찾기 (left join & 필터링)
    missing_rows = all_possible_combinations.merge(
        df[columns], on=columns, how="left", indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return missing_rows


def get_current_date_str(tz: str | None = None) -> str:
    """
    현재 시각을 'YYYY-MM-DD HH:MM:SS' 형식 문자열로 반환.
    tz 인자로 'UTC' (대소문자 무관)를 주면 UTC 기준, 그 외에는 로컬 타임존 기준.
    """
    if isinstance(tz, str) and tz.upper() == "UTC":
        now = datetime.datetime.now(datetime.timezone.utc)
    else:
        # now = datetime.datetime.now().astimezone()
        now = datetime.datetime.now()

    return now.strftime("%Y-%m-%d %H:%M:%S")


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
            df_in_ItemMeterial = read_csv_file("df_in_ItemMeterial")
            df_in_BODTOP = read_csv_file("df_in_BODTOP")
            df_in_BODItemMap = read_csv_file("df_in_BODItemMap")
            df_in_BODBottoMLock = read_csv_file("df_in_BODBottoMLock")


        dataframes = {
            'df_in_ItemMeterial': df_in_ItemMeterial,
            'df_in_BODTOP': df_in_BODTOP,
            'df_in_BODItemMap': df_in_BODItemMap,
            'df_in_BODBottoMLock': df_in_BODBottoMLock,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        LOCATION_COLUMN = 'Location.[Location]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_METERIAL_MSL1_COLUMN = 'Item Material.[MSL1]'
        ITEM_METERIAL_MSL3_COLUMN = 'Item Material.[MSL3]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        GT_CODE_COLUMN = 'Global Top.[GT Code]'
        VENDOR_MTRL_GT_NAME_COLUMN = 'Vendor Mtrl_GT Name'
        VENDOR_MTRL_MASTER_ECP_FLAG_COLUMN = 'Vendor Mtrl_Master Ecp Flag'
        VENDOR_MTRL_MASTER_FLAG_COLUMN = 'Vendor Mtrl_Master Flag'
        VENDOR_MTRL_QUOTA_COLUMN = 'Vendor Mtrl_Quota'
        VENDOR_MTRL_RESULT_ECP_FLAG_COLUMN = 'Vendor Mtrl_Result Ecp Flag'
        VENDOR_MTRL_RESULT_FLAG_COLUMN = 'Vendor Mtrl_Result Flag'

        MTRL_ATTR_20FT_COLUMN = 'Mtrl Attr_20FT'
        MTRL_ATTR_40FT_COLUMN = 'Mtrl Attr_40FT'
        MTRL_ATTR_40FT_HC_COLUMN = 'Mtrl Attr_40FT HC'
        MTRL_ATTR_PALLET_COLUMN = 'Mtrl Attr_Pallet'

        BOD_LIST_MTRL_W_FACTORY_OUT_COLUMN = 'BOD List Mtrl W_Factory Out'
        BOD_LIST_MTRL_W_GR_LT_COLUMN = 'BOD List Mtrl W_GR LT'
        BOD_LIST_MTRL_W_INTRANSIT_LT_COLUMN = 'BOD List Mtrl W_Intransit LT'
        BOD_LIST_MTRL_W_PORT_TO_PORT_COLUMN = 'BOD List Mtrl W_Port To Port'
        BOD_LIST_MTRL_W_EFF_STARTDATE_COLUMN = 'BOD List Mtrl_EFF Startdate'
        BOD_LIST_MTRL_W_EFF_ENDDATE_COLUMN = 'BOD List Mtrl_EFF Enddate'

        BOD_LIST_MTRL_LOT_TYPE_COLUMN = 'BOD List Mtrl_Lot Type'
        BOD_LIST_MTRL_EFF_STARTDATE_COLUMN = 'BOD List Mtrl_EFF Startdate'
        BOD_LIST_MTRL_EFF_ENDDATE_COLUMN = 'BOD List Mtrl_EFF Enddate'
        BOD_LIST_MTRL_PRIORITY_COLUMN = 'BOD List Mtrl_Priority'
        BOD_LIST_MTRL_TIME_VARYING_FLAG_COLUMN = 'BOD List Mtrl_Time Varying Flag'

        BOD_ITEM_MTRL_LOCK_FLAG_COLUMN = 'BOD Item Mtrl_Lock Flag'
        BOD_ITEM_MTRL_EFF_ENDDATE_COLUMN = 'BOD Item Mtrl_EFF Enddate'
        BOD_ITEM_MTRL_EFF_STARTDATE_COLUMN = 'BOD Item Mtrl_EFF Startdate'
        BOD_ITEM_MTRL_LOT_TYPE_COLUMN = 'BOD Item Mtrl_Lot Type'
        BOD_ITEM_MTRL_LOT_SIZE_COLUMN = 'BOD Item Mtrl_Lot Size'
        BOD_ITEM_MTRL_PRIORITY_COLUMN = 'BOD Item Mtrl_Priority'
        BOD_ITEM_MTRL_TIME_VARYING_FLAG_COLUMN = 'BOD Item Mtrl_Time Varying Flag'

        BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN = 'BOD Item Mtrl W_Factory Out'
        BOD_ITEM_MTRL_W_GR_LT_COLUMN = 'BOD Item Mtrl W_GR LT'
        BOD_ITEM_MTRL_W_INTRANSIT_LT_COLUMN = 'BOD Item Mtrl W_Intransit LT'
        BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN = 'BOD Item Mtrl W_Port To Port'
        BOD_ITEM_MTRL_W_SUPPLIER_COLUMN = 'BOD Item Mtrl W_Supplier'
        BOD_ITEM_MTRL_W_TOTAL_LT_COLUMN = 'BOD Item Mtrl W_Total LT'

        BOD_ITEM_MTRL_CREATED_BY_COLUMN = 'BOD Item Mtrl_Created By'
        BOD_ITEM_MTRL_CREATE_TIME_COLUMN = 'BOD Item Mtrl_Created Time'

        df_BODItemMtrlW = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN, BOD_ITEM_MTRL_W_GR_LT_COLUMN, BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN,
        ]

        df_BODItemMtrl = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TIME_WEEK_COLUMN, ITEM_METERIAL_COLUMN, SUB_LOCATION_COLUMN, TRANS_MODE_COLUMN,
            BOD_ITEM_MTRL_EFF_STARTDATE_COLUMN, BOD_ITEM_MTRL_EFF_ENDDATE_COLUMN, BOD_ITEM_MTRL_LOT_TYPE_COLUMN,
            BOD_ITEM_MTRL_LOCK_FLAG_COLUMN, BOD_ITEM_MTRL_LOT_SIZE_COLUMN, BOD_ITEM_MTRL_PRIORITY_COLUMN, BOD_ITEM_MTRL_TIME_VARYING_FLAG_COLUMN,
            BOD_ITEM_MTRL_CREATED_BY_COLUMN, BOD_ITEM_MTRL_CREATE_TIME_COLUMN
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        # ------------------ 테스트 디버깅용 ------------------ start
        # df_in_Demand = df_in_Demand[df_in_Demand[ITEM_COLUMN] == 'QE43LS03DAUXXH']
        # df_in_SetItem = df_in_SetItem[df_in_SetItem[ITEM_COLUMN] == 'QE43LS03DAUXXH']
        # ------------------ 테스트 디버깅용 ------------------ end


        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_in_BODTOP.empty:
            raise CustomException("STEP3 by 0 ____ df_in_BODTOP 값이 없습니다.")


        # 현재 날짜 시간
        # current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # current_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        current_date = get_current_date_str('UTC')
        step(f'=====> current_date : {current_date}')

        step('=====> STEP3 End')



        ################################################################################################################
        # STEP 4 : output data machining
        ################################################################################################################
        step('=====> STEP4 Start : output data machining')


        step('=====> STEP4 by 1 Start : BOD_TOP 과 BOD_ITEM_MAP 을 JOIN 하여, 데이터 생성 (BOD_TOP_ITEM_MERGE)')
        df_bod_top_item = pd.merge(df_in_BODTOP, df_in_BODItemMap, how='inner',
                                   left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_METERIAL_MSL1_COLUMN, ITEM_METERIAL_MSL3_COLUMN],
                                   right_on=[GT_CODE_COLUMN, LOCATION_COLUMN, ITEM_METERIAL_MSL1_COLUMN, ITEM_METERIAL_MSL3_COLUMN],)
        print_df(df_bod_top_item, 'STEP4 by 1.1  ____ df_bod_top_item .... merge[df_in_BODTOP, df_in_BODItemMap]')

        df_bod_top_item.rename(columns={LOCATION_COLUMN+'_x': LOCATION_COLUMN,}, inplace=True)
        df_bod_top_item.drop(columns=[LOCATION_COLUMN+'_y',], inplace=True)
        print_df(df_bod_top_item, 'STEP4 by 1.2  ____ df_bod_top_item .... create')

        step('=====> STEP4 by 1 End')



        step('=====> STEP4 by 2 Start : df_bod_top_item 와 df_in_BODBottoMLock 의 Key가 일치하는 데이터 제외')
        df_merged = pd.merge(df_bod_top_item, df_in_BODBottoMLock, how='outer', indicator=True,
                             left_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TRANS_MODE_COLUMN],
                             right_on=[LOCATION_COLUMN, SUB_LOCATION_COLUMN, ITEM_METERIAL_COLUMN, TRANS_MODE_COLUMN])
        print_df(df_merged, 'STEP4 by 2.1  ____ df_merged .... merge[df_bod_top_item, df_in_BODBottoMLock]')

        # 일치하지 않는 항목만 필터링 (_merge 열이 'left_only' 또는 'right_only'인 행)
        df_non_matching = df_merged[df_merged['_merge'] != 'both']
        df_non_matching.rename(columns={
            ITEM_METERIAL_MSL1_COLUMN+'_x': ITEM_METERIAL_MSL1_COLUMN,
            ITEM_METERIAL_MSL3_COLUMN+'_x': ITEM_METERIAL_MSL3_COLUMN,
        }, inplace=True)
        print_df(df_non_matching, 'STEP4 by 2.2  ____ df_non_matching .... non matching select')
        step('=====> STEP4 by 2 End')



        step('=====> STEP4 by 3 Start : output table modify')
        df_out_BODItemMtrlW = rename_and_delete_df(df_non_matching)
        df_out_BODItemMtrlW.rename(columns={
            BOD_LIST_MTRL_W_FACTORY_OUT_COLUMN: BOD_ITEM_MTRL_W_FACTORY_OUT_COLUMN,
            BOD_LIST_MTRL_W_GR_LT_COLUMN: BOD_ITEM_MTRL_W_GR_LT_COLUMN,
            BOD_LIST_MTRL_W_PORT_TO_PORT_COLUMN: BOD_ITEM_MTRL_W_PORT_TO_PORT_COLUMN,
        }, inplace=True)
        print_df(df_out_BODItemMtrlW, 'STEP4 by 3.1  ____ df_out_BODItemMtrlW .... colum rename')

        df_out_BODItemMtrl = df_out_BODItemMtrlW.copy()
        df_out_BODItemMtrl.rename(columns={
            BOD_LIST_MTRL_EFF_STARTDATE_COLUMN: BOD_ITEM_MTRL_EFF_STARTDATE_COLUMN,
            BOD_LIST_MTRL_EFF_ENDDATE_COLUMN: BOD_ITEM_MTRL_EFF_ENDDATE_COLUMN,
            BOD_LIST_MTRL_LOT_TYPE_COLUMN: BOD_ITEM_MTRL_LOT_TYPE_COLUMN,
            BOD_LIST_MTRL_PRIORITY_COLUMN: BOD_ITEM_MTRL_PRIORITY_COLUMN,
            BOD_LIST_MTRL_TIME_VARYING_FLAG_COLUMN: BOD_ITEM_MTRL_TIME_VARYING_FLAG_COLUMN,
        }, inplace=True)
        df_out_BODItemMtrl[BOD_ITEM_MTRL_LOCK_FLAG_COLUMN] = 'N'
        print_df(df_out_BODItemMtrl, 'STEP4 by 3.2  ____ df_out_BODItemMtrl .... colum rename')

        df_out_BODItemMtrl = pd.merge(df_out_BODItemMtrl, df_in_ItemMeterial, how='left', on=[ITEM_METERIAL_COLUMN])
        print_df(df_out_BODItemMtrl, 'STEP4 by 3.3.1  ____ df_out_BODItemMtrl .... merge[df_in_ItemMeterial]')

        # 조건 리스트 정의
        conditions = [
            df_out_BODItemMtrl[BOD_ITEM_MTRL_LOT_TYPE_COLUMN] == '20FT',
            df_out_BODItemMtrl[BOD_ITEM_MTRL_LOT_TYPE_COLUMN] == '40FT',
            df_out_BODItemMtrl[BOD_ITEM_MTRL_LOT_TYPE_COLUMN] == '40FT HC',
            df_out_BODItemMtrl[BOD_ITEM_MTRL_LOT_TYPE_COLUMN] == 'Pallet',
        ]

        # 각 조건에 해당하는 값 리스트 정의
        choices = [
            df_out_BODItemMtrl[MTRL_ATTR_20FT_COLUMN],
            df_out_BODItemMtrl[MTRL_ATTR_40FT_COLUMN],
            df_out_BODItemMtrl[MTRL_ATTR_40FT_HC_COLUMN],
            df_out_BODItemMtrl[MTRL_ATTR_PALLET_COLUMN],
        ]

        # 조건에 따라 'size' 컬럼 생성
        df_out_BODItemMtrl[BOD_ITEM_MTRL_LOT_SIZE_COLUMN] = np.select(conditions, choices, np.nan)
        print_df(df_out_BODItemMtrl, 'STEP4 by 3.3.2  ____ df_out_BODItemMtrl .... final')

        df_out_BODItemMtrl[BOD_ITEM_MTRL_CREATED_BY_COLUMN] = 'PY_UI_MtrlBODItem'
        df_out_BODItemMtrl[BOD_ITEM_MTRL_CREATE_TIME_COLUMN] = current_date

        step('=====> STEP4 by 3 End')

        step('=====> STEP4 End')




        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')

        df_out_BODItemMtrlW[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_BODItemMtrlW = df_out_BODItemMtrlW[df_BODItemMtrlW]
        df_out_BODItemMtrlW = df_out_BODItemMtrlW.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        df_out_BODItemMtrl[VERSION_NAME_COLUMN] = paramOutVersion
        df_out_BODItemMtrl = df_out_BODItemMtrl[df_BODItemMtrl]
        df_out_BODItemMtrl = df_out_BODItemMtrl.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None})

        dataframes = {
            'df_out_BODItemMtrlW': df_out_BODItemMtrlW,
            'df_out_BODItemMtrl': df_out_BODItemMtrl,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_BODItemMtrl = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_BODItemMtrl = pd.DataFrame([], columns=[])
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
