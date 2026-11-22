

"""

* 프로그램명
    - PY_MG_AmendSOPLotSize

* 내용
     - Documents.[OrderlineID] '%SCS_LOT%' 작업대상
       그외는  W Material Consumption Quantity Plan Output 작업없이 저장


* 변경이력
- 2024.11.18 / de0413.shin (신동언) / Create
- 2025.04.10 / 신동언 / Update
- 2025.05.30 / 신동언 / Update
- 2026.01.06 / 박병훈 / Update
- 2026.02.02 / 박병훈 / Update




* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.


* Input Table
   - df_in_MPCurrWeek       = Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
   # - df_in_AllWeek          = Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
   - df_in_PlanOrgQty     = Select ([Version].[Version Name] * [Item].[Plan Group] * [Item].[Item Stage].[SET].relatedmembers("Item") * [Time].[Week] * [Location].[Site Stage].filter(#.Name in {"MF","MF_KD","MF_SET"}).relatedmembers("Location") * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2].filter(~(#.Name Startswith ("RT_"))) * [Activity3].[Activity3] ) on row,({Measure.[W Material Consumption Quantity Plan Output], Measure.[W Frozen Window LotSize],Measure.[W LotSize Period],Measure.[W LotSize Remain Config], Measure.[Dummy]}) on column;
   - df_in_WSoftLotSize    = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item Stage].[SET].relatedmembers("Item") * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W LotSize Increment], Measure.[Dummy]}) on column;
   - df_in_WResourceConsum = Select ([Version].[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Resource].[Resource] * [Resource].[Resource Type].filter(#.Name in {"MCT","SCT","MFT","SRT"}) * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,({Measure.[W Resource Consumption Association], Measure.[Dummy]}) on column;
   - df_in_WResourceCapa   = Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Resource].[Resource Type].filter(#.Name in {"MFT"}).relatedmembers([Resource])) on row,({ Measure.[W Coarser Maximum Utilization Quantity],Measure.[W Coarser Minimum Utilization Quantity],Measure.[Dummy]}) on column where { Measure.[W Coarser Minimum Utilization Quantity] > 0};
   - df_in_ShipmentLT      = Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Mandatory Offset], Measure.[Dummy]}) on column;
   - df_in_Location         = Select ([Location].[Location] *[Location].[Location Type].[DC] * [Location].[Shipment Type] * [Location].[Site Stage]) on row;
   - df_in_WSolverLotSizeOption = Select ([Version].[Version Name]) on row, ({Measure.[W Solver Lotsize Option], Measure.[Dummy]}) on column;

* Output Table
    - df_out_AmendSOPMfgSOPQty = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Activity1].[Activity1] * [Documents].[OrderlineID] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,
                                     ({Measure.[Amend SOP_MfgSOP Qty], Measure.[Amend SOP_ORG SOP Qty], Measure.[Amend SOP_SOP Qty]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_AmendSOPLotSize] for measures {[Amend SOP_SOP Qty]} using scope ([Version].[Version Name].[CurrentWorkingView])
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CurrentWorkingView"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};




실행 전 프로시져를 통해 MF Site 삭제  필요

"""


########################################################################################################################
# common - start
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
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_AmendSOPLotSizeNew'
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
        step(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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
        # STEP 1 : input table load
        ################################################################################################################
        step('=====> STEP 1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_MPCurrWeek = read_csv_file('df_in_MPCurrWeek_VD04')
            # df_in_AllWeek = read_csv_file('df_in_AllWeek')
            df_in_PlanOrgQty = read_csv_file('df_in_PlanOrgQty_VD04')
            df_in_WSoftLotSize = read_csv_file('df_in_WSoftLotSize_VD04')
            df_in_WResourceConsum = read_csv_file('df_in_WResourceConsum_VD04')
            df_in_WResourceCapa = read_csv_file('df_in_WResourceCapa_VD04')
            df_in_ShipmentLT = read_csv_file('df_in_ShipmentLT_VD04')
            df_in_Location = read_csv_file('df_in_Location_VD04')
            df_in_WSolverLotSizeOption = read_csv_file('df_in_WSolverLotSizeOption_VD04')

        dataframes = {
            'df_in_MPCurrWeek': df_in_MPCurrWeek,
            # 'df_in_AllWeek': df_in_AllWeek,
            'df_in_PlanOrgQty': df_in_PlanOrgQty,
            'df_in_WSoftLotSize': df_in_WSoftLotSize,
            'df_in_WResourceConsum': df_in_WResourceConsum,
            'df_in_WResourceCapa': df_in_WResourceCapa,
            'df_in_ShipmentLT': df_in_ShipmentLT,
            'df_in_Location': df_in_Location,
            'df_in_WSolverLotSizeOption': df_in_WSolverLotSizeOption,}

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1 End')
        ################################################################################################################
        # Step 2 (1) 데이터 프레임 변수 지정 및 이름 변경
        ################################################################################################################
        step('=====> STEP 2 Start : DataFrame Column 변수 처리')

        Version_Name_COLUMN = 'Version.[Version Name]'
        Time_Week_COLUMN = 'Time.[Week]'
        Time_Day_COLUM = 'Time.[Day]'
        Time_Day_of_Week_COLUMN = 'Time.[Day of Week]'
        Location_COLUMN = 'Location.[Location]'
        Location_Location_Type_COLUMN = 'Location.[Location Type]'
        Location_Shipment_Type_COLUMN = 'Location.[Shipment Type]'
        Location_Site_Stage_COLUMN = 'Location.[Site Stage]'
        Item_Column = 'Item.[Item]'
        Documents_OrderlineID_COLUMN = 'Documents.[OrderlineID]'
        Activity1_Activity1_COLUMN = 'Activity1.[Activity1]'
        Activity2_Activity2_COLUMN = 'Activity2.[Activity2]'
        Activity3_Activity3_COLUMN = 'Activity3.[Activity3]'
        Resource_Resource_Type_COLUMN = 'Resource.[Resource Type]'
        Resource_Resource_COLUMN = 'Resource.[Resource]'

        W_Material_Consumption_Quantity_Plan_Output = 'W Material Consumption Quantity Plan Output'
        W_Frozen_Window_LotSize = 'W Frozen Window LotSize'
        W_LotSize_Increment = 'W LotSize Increment'
        W_Activity_Mandatory_Offset = 'W Activity Mandatory Offset'
        W_LotSize_Period = 'W LotSize Period'
        W_LotSize_Remain_Config = 'W LotSize Remain Config'
        W_SolverLotsize_Option = 'W Solver Lotsize Option'
        Dummy = 'Dummy'

        Amend_SOP_ORG_SOP_Qty = 'Amend SOP_ORG SOP Qty'
        Amend_SOP_SOP_Qty = 'Amend SOP_SOP Qty'

        Sequence = 'Sequence'
        MFT = 'MFT'
        MCT = 'MCT'
        SCS = 'SCS'
        DIR_S = 'DIR_S'
        DIR_D = 'DIR_D'
        Down = 'Down'
        Keep = 'Keep'
        Plan_cumsum = 'Plan_cumsum'
        Plan_MaxWeek = 'Plan_MaxWeek'
        floor_qty = 'floor_qty'
        New_qty = 'New_qty'
        New_qty_1 = 'New_qty_1'
        flag = 'flag'
        Rank = 'Rank'
        both = 'both'
        left_only = 'left_only'
        _merge = '_merge'
        key_col = 'key_col'

        step('=====> STEP 2 End')

        ################################################################################################################
        # Step 3 out 데이터 프레임 기초 데이터 셋팅
        ################################################################################################################
        step('=====> STEP 3 Start : input data machining')

        # current_week 설정
        current_week = pd.to_numeric(df_in_MPCurrWeek[Time_Week_COLUMN][0])
        note(f"current_week 확인 =============================> {current_week, type(current_week)}")

        # 신규 로직 진행 여부를 결정하기 위한 Flag 설정
        v = df_in_WSolverLotSizeOption[W_SolverLotsize_Option].iat[0]
        flag = "Y" if str(v).strip() == "2" else "N"
        note(f"flag data 확인 =============================> {flag}")

        # df_in_Plan_Org_Qty : 엔진에서 나온 계획 결과(수량)
        df_in_PlanOrgQty = df_in_PlanOrgQty.drop(columns=Dummy)  # Dummy 삭제

        # W_LotSize_Remain_Config 값이 Null 인 경우 Keep을 반영 추후 변경될 수도 있음.....
        df_in_PlanOrgQty[W_LotSize_Remain_Config] = df_in_PlanOrgQty[W_LotSize_Remain_Config].astype(str)
        df_in_PlanOrgQty[W_LotSize_Remain_Config] = df_in_PlanOrgQty[W_LotSize_Remain_Config].str.strip().mask(
            df_in_PlanOrgQty[W_LotSize_Remain_Config].isna() | (df_in_PlanOrgQty[W_LotSize_Remain_Config] == ""),
            Keep)

        df_in_PlanOrgQty.loc[:, W_LotSize_Remain_Config] = df_in_PlanOrgQty[W_LotSize_Remain_Config].str.strip()
        df_in_PlanOrgQty.loc[:, W_LotSize_Period] = df_in_PlanOrgQty[W_LotSize_Period].fillna(0).astype(int)

        # Number Columns 숫자형 변환
        num_cols = [W_Material_Consumption_Quantity_Plan_Output, W_Frozen_Window_LotSize, W_LotSize_Period]
        df_in_PlanOrgQty[num_cols] = df_in_PlanOrgQty[num_cols].fillna(0).astype(int)

        # current_week 타입변경
        df_in_MPCurrWeek[Time_Week_COLUMN] = df_in_MPCurrWeek[Time_Week_COLUMN].astype(int)

        # 주차 소트하여 인덱스 재설정처리
        df_in_MPCurrWeek = df_in_MPCurrWeek.reset_index(drop='true')
        df_in_MPCurrWeek[Sequence] = df_in_MPCurrWeek.index
        df_in_MPCurrWeek.loc[:, Sequence] = df_in_MPCurrWeek[Sequence].astype(int)

        # Resource_Resource_Type_COLUMN 이 MCT 인 것들의 Activity3_Activity3_COLUMN 리스트로 만들기
        MCT_List = df_in_WResourceConsum[df_in_WResourceConsum[Resource_Resource_Type_COLUMN] == MCT][
            Activity3_Activity3_COLUMN].unique()

        # df_in_WResource_Consum2와 동일한 결과
        df_in_WResourceConsum_temp = df_in_WResourceConsum[
            (df_in_WResourceConsum[Resource_Resource_Type_COLUMN] == MFT) &
            (~df_in_WResourceConsum[Activity3_Activity3_COLUMN].isin(MCT_List))]

        df_in_PlanOrgQty[Time_Week_COLUMN] = df_in_PlanOrgQty[Time_Week_COLUMN].astype(int)
        # df_in_PlanOrgQty 에 Sequence 값 업데이트
        df_in_PlanOrgQty[Sequence] = df_in_PlanOrgQty[Time_Week_COLUMN].map(
            df_in_MPCurrWeek.set_index(Time_Week_COLUMN)[Sequence])
        # Sequence 가 NA 인 열 삭제
        df_in_PlanOrgQty = df_in_PlanOrgQty.dropna(subset=[Sequence], axis=0)

        # df_in_PlanOrgQty 의 Time_Week_COLUMN 타입 변경
        df_in_PlanOrgQty[Time_Week_COLUMN] = df_in_PlanOrgQty[Time_Week_COLUMN].astype(int)
        print_df(df_in_PlanOrgQty, "df_in_PlanOrgQty 임시확인 1 ", False)

        # 작업대상 구분 (W_Frozen_Window_LotSize <= Sequence) & (Documents_OrderlineID_COLUMN 에 SCS가 포함된 것들만 필터)
        SCSB_filter = (
              df_in_PlanOrgQty[W_Frozen_Window_LotSize]
              <= df_in_PlanOrgQty[Sequence]) & (
              df_in_PlanOrgQty[Documents_OrderlineID_COLUMN].str.contains(SCS) & (
              df_in_PlanOrgQty[Time_Week_COLUMN] >= current_week))

        # SCSB_filter 를 통해 데이터 프레임 필터
        df_in_PlanSCSB = df_in_PlanOrgQty[SCSB_filter]

        # W_Material_Consumption_Quantity_Plan_Output 를 구하기 위한 그룹바이 컬럼 지정
        groupby_cols = [
            Version_Name_COLUMN, Item_Column, Time_Week_COLUMN, Documents_OrderlineID_COLUMN,
            Location_COLUMN, Activity1_Activity1_COLUMN, Activity2_Activity2_COLUMN, Activity3_Activity3_COLUMN,
            W_Frozen_Window_LotSize, W_LotSize_Period, W_LotSize_Remain_Config, Sequence]

        # 작업 대상 데이터 프레임에 그룹바이 진행
        df_in_PlanSCSB = df_in_PlanSCSB.groupby(groupby_cols)[
            W_Material_Consumption_Quantity_Plan_Output].sum().reset_index()

        # 로직 수행을 위해 필요한 컬럼 지정
        filter_cols = [
            Version_Name_COLUMN, Item_Column, Time_Week_COLUMN, Documents_OrderlineID_COLUMN, Location_COLUMN,
            Activity1_Activity1_COLUMN, Activity2_Activity2_COLUMN, Activity3_Activity3_COLUMN, Amend_SOP_ORG_SOP_Qty,
            Amend_SOP_SOP_Qty]

        # 작업대상이 아닌 데이터 프레임 필터
        # W_Frozen_Window_LotSize 가 Sequence 보다 큰것
        df_in_PlanNSCS_temp = df_in_PlanOrgQty[df_in_PlanOrgQty[W_Frozen_Window_LotSize] > df_in_PlanOrgQty[Sequence]]
        # W_Frozen_Window_LotSize 가 Sequence 보다 작거나 같은 것 중 SCS을 포함하지 않는 데이터 프레임
        df_in_PlanNSCS = df_in_PlanOrgQty[df_in_PlanOrgQty[W_Frozen_Window_LotSize]<=df_in_PlanOrgQty[Sequence]]
        df_in_PlanNSCS = df_in_PlanNSCS[~df_in_PlanNSCS[Documents_OrderlineID_COLUMN].str.contains(SCS)]
        print_df(df_in_PlanNSCS_temp, "df_in_PlanNSCS_temp 임시확인 1 ", False)
        print_df(df_in_PlanNSCS, "df_in_PlanNSCS 초기 데이터 임시확인 1", False)

        # 비 작업 대상 두 데이터 프레임 합치기
        df_in_PlanNSCS = pd.concat([df_in_PlanNSCS,df_in_PlanNSCS_temp], axis=0, ignore_index=True)

        # 작업 대상이 아닌 데이터 프레임의 그룹 바이 진행
        df_in_PlanNSCS = df_in_PlanNSCS.groupby(groupby_cols)[
            W_Material_Consumption_Quantity_Plan_Output].sum().reset_index()
        df_in_PlanNSCS = df_in_PlanNSCS.rename(
            columns={W_Material_Consumption_Quantity_Plan_Output : Amend_SOP_ORG_SOP_Qty})
        df_in_PlanNSCS.loc[:,Amend_SOP_SOP_Qty] = df_in_PlanNSCS[Amend_SOP_ORG_SOP_Qty]
        df_in_PlanNSCS = df_in_PlanNSCS[filter_cols]

        print_df(df_in_PlanSCSB, "df_in_PlanSCSB 초기 데이터 확인", True)
        print_df(df_in_PlanNSCS, "df_in_PlanNSCS 초기 데이터 확인", True)
        # if 1=0
        # df_in_Plan_SCSB New_구간 설정
        ####################################################################################################################
        # 데이터 타입 변경
        numeric_cols = [
            W_Frozen_Window_LotSize, W_LotSize_Period, Sequence, Time_Week_COLUMN]

        df_in_PlanSCSB.loc[:,numeric_cols] = df_in_PlanSCSB[numeric_cols].astype(int)

        # 신규 데이터 프레임 생성
        df_in_PlanSCSB_new = pd.DataFrame()  # 신규 빈 데이터 프레임 생성

        # flag가 Y 이면 신규 로직 수행
        if flag == 'Y':
            df_in_PlanSCSB_new_temp = df_in_PlanSCSB.copy()  # 작업 대상의 데이터 프레임 복사
            print_df(df_in_PlanSCSB_new_temp , 'df_in_PlanSCSB_new_temp 초기 데이터 확인', False) # 작업 대상 복사한 내용 확인
            # W_Frozen_Window_LotSize , W_LotSize_Period, W_LotSize_Remain_Config 값 설정을 위한 데이터 프레임 정리
            # W_Frozen_Window_LotSize : min , W_LotSize_Period : min , W_LotSize_Remain_Config : max
            df_in_PlanSCSB_group = df_in_PlanSCSB_new_temp.groupby(
                [Version_Name_COLUMN, Item_Column], as_index=False).agg(
                W_Frozen_Window_LotSize=(W_Frozen_Window_LotSize, 'min'),
                W_LotSize_Period=(W_LotSize_Period, 'min'),
                W_LotSize_Remain_Config=(W_LotSize_Remain_Config, 'max')).rename(columns={
                'W_Frozen_Window_LotSize': W_Frozen_Window_LotSize, 'W_LotSize_Period': W_LotSize_Period,
                'W_LotSize_Remain_Config': W_LotSize_Remain_Config})

            # 작업 대상에 그룹바이한 데이터 프레임 붙임을 통해 W_Frozen_Window_LotSize , W_LotSize_Period, W_LotSize_Remain_Config 설정
            df_in_PlanSCSB_new_temp = df_in_PlanSCSB_new_temp.drop(
                columns=[W_Frozen_Window_LotSize, W_LotSize_Period, W_LotSize_Remain_Config], axis=1).merge(
                df_in_PlanSCSB_group, on=[Version_Name_COLUMN, Item_Column], how='left')
            print_df(df_in_PlanSCSB_new_temp, 'df_in_PlanSCSB_new_temp _ df_in_PlanSCSB_group 와 merge 데이터', False)
            # 데이터 타입 재 설정 및 변경
            df_in_PlanSCSB_new_temp.loc[:, numeric_cols] = df_in_PlanSCSB_new_temp[numeric_cols].astype(int)
            # 작업 대상에서도 신규 로직을 수행할 조건 수립
            m_window = (
                    (df_in_PlanSCSB_new_temp[Sequence] >= df_in_PlanSCSB_new_temp[W_Frozen_Window_LotSize]) &
                    (df_in_PlanSCSB_new_temp[Sequence] < df_in_PlanSCSB_new_temp[W_Frozen_Window_LotSize]
                     + df_in_PlanSCSB_new_temp[W_LotSize_Period]))

            # 조건에 포함되는 데이터 프레임만 필터링
            df_in_PlanSCSB_new_m = df_in_PlanSCSB_new_temp.loc[m_window].copy()
            print_df(df_in_PlanSCSB_new_m, 'df_in_PlanSCSB_new_m _ 데이터 확인', False)
            # 작업 대상이지만 로직 조건을 수행하지 않는 데이터 프레임 필터
            df_in_PlanSCSB_new_temp = df_in_PlanSCSB_new_temp.loc[~m_window].copy()
            print_df(df_in_PlanSCSB_new_temp, 'df_in_PlanSCSB_new_temp _ 데이터 확인', False)

            # Note를 통해 데이터 프레임 갯수 확인
            note(
                f"== df_in_PlanSCSB_new_합계 =====> 비 작업대상 : {df_in_PlanSCSB_new_temp.shape[0]}  +  작업대상 : {df_in_PlanSCSB_new_m.shape[0]} = {df_in_PlanSCSB_new_temp.shape[0] + df_in_PlanSCSB_new_m.shape[0]}")

            # Lot size를 구하기 위한 Key_값 설정을 위한 파생 컬럼 생성
            df_in_PlanSCSB_new_m[key_col] = df_in_PlanSCSB_new_m[Activity1_Activity1_COLUMN] + "_" + \
                                            df_in_PlanSCSB_new_m[Activity3_Activity3_COLUMN]
            df_in_WSoftLotSize[key_col] = df_in_WSoftLotSize[Activity1_Activity1_COLUMN] + "_" + df_in_WSoftLotSize[
                Activity3_Activity3_COLUMN]

            # 생성한 Key_col을 가지고 Lot Size 값을 데이터 프레임에 merge
            df_in_PlanSCSB_new_m = df_in_PlanSCSB_new_m.merge(
                df_in_WSoftLotSize[[key_col, W_LotSize_Increment]],
                on=key_col, how='left').drop(columns=key_col, axis=1)  # merge 후 key_col 삭제.....

            # Merge 후 데이터 프레임 크리 확인
            note(f"=====================================> {df_in_PlanSCSB_new_m.shape} 두번째")

            # df_in_Location 과 Activity1_Activity1_COLUMN 과 merge
            # df_in_PlanSCSB_new_m 에 To_location 으로 파생 컬럼 생성
            df_in_PlanSCSB_new_m['To_location'] = df_in_PlanSCSB_new_m[Activity1_Activity1_COLUMN].str.split('_').str[1]
            # df_in_Location 의 Location_COLUMN 을 To_location 으로 변경 후 데이터 merge
            df_in_PlanSCSB_new_m = df_in_PlanSCSB_new_m.merge(
                df_in_Location.rename(columns={Location_COLUMN: 'To_location'}),
                on='To_location', how='left')
            # Merge 후 데이터 프레임 크리 확인
            note(f"=====================================> {df_in_PlanSCSB_new_m.shape} 세번째")
            # Merge 후 W_LotSize_Increment 의 빈값 채우고 데이터 형태를 int 형으로 변환
            df_in_PlanSCSB_new_m.loc[:, W_LotSize_Increment] = df_in_PlanSCSB_new_m[W_LotSize_Increment].fillna(
                0).astype(int)

            # 우선 순위 정하기
            # 1) Location_Shipment_Type_COLUMN 우선순위
            # DIR_S 1순위, DIR_D 2 순위 , 그 외 = 99
            df_in_PlanSCSB_new_m['p_ship'] = np.select(
                [df_in_PlanSCSB_new_m[Location_Shipment_Type_COLUMN].eq(DIR_S),
                 df_in_PlanSCSB_new_m[Location_Shipment_Type_COLUMN].eq(DIR_D)],
                [1, 2], default=99)
            # 2) Location_Site_Stage_COLUMN 의 순서 지정
            df_in_PlanSCSB_new_m['p_site'] = np.where(
                df_in_PlanSCSB_new_m[Location_Site_Stage_COLUMN].astype(str).str.contains('HUB', na=False),
                3, 4)
            # 3) 정렬 순서
            #  1. Week 오름차순
            #  2. Item 오름차순
            #  3. To_Location  오름차순
            #  4. Location_Shipment_Type_COLUMN, Location_Site_Stage_COLUMN, W_LotSize_Increment 순서 ....

            df_in_PlanSCSB_new_m = df_in_PlanSCSB_new_m.sort_values(
                by=[Item_Column, Time_Week_COLUMN, 'p_ship', 'p_site', W_LotSize_Increment, 'To_location'],
                ascending=[True, True, True, True, False, True],
                kind='mergesort').drop(columns=['p_ship', 'p_site'], axis=1)

            df_in_PlanSCSB_new_m[W_LotSize_Increment] = df_in_PlanSCSB_new_m[W_LotSize_Increment].fillna(0).astype(int)
            df_in_PlanSCSB_new_m.reset_index(drop=True, inplace=True)

            # 작업이 필요한 컬럼과 그렇지 않은 컬럼으로 구분
            df_in_PlanSCSB_new_m_cal = df_in_PlanSCSB_new_m[df_in_PlanSCSB_new_m[W_LotSize_Increment] > 1].copy()
            df_in_PlanSCSB_new_m = df_in_PlanSCSB_new_m[df_in_PlanSCSB_new_m[W_LotSize_Increment] <= 1].copy()

            note(
                f"==========  df_in_PlanSCSB_new_m    =====> {df_in_PlanSCSB_new_m_cal.shape[0] + df_in_PlanSCSB_new_m.shape[0]}")
            # Lot Size 계산 (초기 할당분)
            df_in_PlanSCSB_new_m_cal['Lot_Size'] = (df_in_PlanSCSB_new_m_cal[
                                                        W_Material_Consumption_Quantity_Plan_Output] /
                                                    df_in_PlanSCSB_new_m_cal[
                                                        W_LotSize_Increment]).astype(int) * df_in_PlanSCSB_new_m_cal[
                                                       W_LotSize_Increment]
            # 초기 할당 후 나머지 구함
            df_in_PlanSCSB_new_m_cal['rem'] = df_in_PlanSCSB_new_m_cal[W_Material_Consumption_Quantity_Plan_Output] % \
                                              df_in_PlanSCSB_new_m_cal[
                                                  W_LotSize_Increment]
            # 나머지들의 주차별 합계 구함
            df_in_PlanSCSB_new_m_cal['rem_cumsum'] = df_in_PlanSCSB_new_m_cal.groupby(
                [Version_Name_COLUMN, Time_Week_COLUMN, Item_Column])['rem'].transform('sum')

            # 반복문 실행을 하기 위한 초기 변수값 할당
            df_in_PlanSCSB_new_m_cal['realloc'] = 0  # 반복 라운드 lot 재할당 결과
            df_in_PlanSCSB_new_m_cal['carry_out'] = 0  # 주차 종료 후 남은 pool (= 다음 주 carry)
            df_in_PlanSCSB_new_m_cal['keep_force_add'] = 0  # keep 강제 소진한 수량
            df_in_PlanSCSB_new_m_cal['keep_priority'] = 0  # keep 강제 전 absdiff 차이 구함
            df_in_PlanSCSB_new_m_cal['final_qty'] = 0  # 최종 할당 값 설정

            df_in_PlanSCSB_new_m_cal['keep_selected'] = False  # Keep / Down 값에 설정에 따른 설정
            df_in_PlanSCSB_new_m_cal['keep_rank'] = 0  # 할상에 대한 우선 순위 결정
            df_in_PlanSCSB_new_m_cal['carry_in'] = 0  # 검증을 위해 할당 된 수량
            df_in_PlanSCSB_new_m_cal['pool_in'] = 0  # 검증을 위해 남은 수량
            df_in_PlanSCSB_new_m_cal['pool_after_realloc'] = 0  # 할당 후 남은 수량
            df_in_PlanSCSB_new_m_cal['pool_after_keep'] = 0  # 할당 후 Keep 한 수량
            df_in_PlanSCSB_new_m_cal['rounds'] = 0  # 할당 한 횟수

            # keep 조건 변경 'DIR_S', 'DIR_D' 이면 keep 이어도 down으로 변경 (반복문 실행 전 변경)
            # W_LotSize_Remain_Config == 'Keep' 이면서 Location_Shipment_Type_COLUMN 가 'DIR_S', 'DIR_D' 이면 Down 으로 변경
            # 변경될 조건 설정
            mask = df_in_PlanSCSB_new_m_cal[W_LotSize_Remain_Config].eq(Keep) & df_in_PlanSCSB_new_m_cal[
                Location_Shipment_Type_COLUMN].isin([DIR_S, DIR_D])
            # Down으로 값 변경
            df_in_PlanSCSB_new_m_cal.loc[mask, W_LotSize_Remain_Config] = Down
            # 반복문 실행을 위해 데이터 컬럼 형 변경
            df_in_PlanSCSB_new_m_cal[Time_Week_COLUMN] = df_in_PlanSCSB_new_m_cal[Time_Week_COLUMN].astype(int)
            print_df(df_in_PlanSCSB_new_m_cal, "df_in_PlanSCSB_new_m_cal _ 반복문 전 데이터 타입 확인", False)

            # Version, Item, Week로 찾기 위한 인덱스 설정 -> 기준이 되는 컴럼
            idx_map = {(Version_Name_COLUMN, Item_Column, Time_Week_COLUMN): g.index.to_numpy()
                       for (Version_Name_COLUMN, Item_Column, Time_Week_COLUMN), g in df_in_PlanSCSB_new_m_cal.groupby(
                    [Version_Name_COLUMN, Item_Column, Time_Week_COLUMN], sort=False)}

            # Item 별 주차를 순회하기 위한 인덱스 설적
            weeks_map = (df_in_PlanSCSB_new_m_cal.groupby(
                [Version_Name_COLUMN, Item_Column])[Time_Week_COLUMN].apply(
                lambda s: sorted([int(x) for x in s.dropna().unique().tolist()])).to_dict())

            # 반복문 시작
            for (v, it), week_list in weeks_map.items():

                carry = 0  # 조기 수량 0으로 설정

                for wk in week_list:
                    rows = idx_map.get((v, it, wk))

                    if rows is None or len(rows) == 0:
                        continue

                    # pool = carry + sum(rem) 금주 수량
                    rem_sum = df_in_PlanSCSB_new_m_cal.loc[rows, 'rem'].sum()  # 검증을 위한 나머지 누적 수량
                    pool = pd.to_numeric(carry + rem_sum)  # 남은 수량에 나머지 더함

                    # 검증이 필요한 컬럼 생성
                    df_in_PlanSCSB_new_m_cal.loc[rows, 'carry_in'] = carry
                    df_in_PlanSCSB_new_m_cal.loc[rows, 'pool_in'] = pool

                    if pool <= 0:
                        df_in_PlanSCSB_new_m_cal.loc[
                            rows, ['pool_after_realloc', 'pool_after_keep', 'rounds']] = 0
                        df_in_PlanSCSB_new_m_cal.loc[rows, 'carry_out'] = 0
                        carry = 0
                        continue

                    rounds = 0
                    while True:
                        rounds += 1
                        allocated_any = False

                        for j in rows:
                            lot = int(df_in_PlanSCSB_new_m_cal.at[j, W_LotSize_Increment])
                            if lot <= 0:
                                continue

                            if pool >= lot:
                                df_in_PlanSCSB_new_m_cal.at[j, 'realloc'] += lot
                                pool -= lot
                                allocated_any = True

                                if pool == 0:
                                    break

                        if pool == 0 or (not allocated_any):
                            break

                    df_in_PlanSCSB_new_m_cal.loc[rows, 'rounds'] = pd.to_numeric(rounds, errors='coerce')
                    df_in_PlanSCSB_new_m_cal.loc[rows, 'pool_after_realloc'] = pd.to_numeric(pool, errors='coerce')

                    if pool >= 0:
                        keep_rows = [
                            j for j in rows if str(df_in_PlanSCSB_new_m_cal.at[j, W_LotSize_Remain_Config]) == 'Keep']
                        if keep_rows:
                            base_before_force = df_in_PlanSCSB_new_m_cal.loc[keep_rows, "Lot_Size"] + \
                                                df_in_PlanSCSB_new_m_cal.loc[keep_rows, 'realloc']
                            priority = (df_in_PlanSCSB_new_m_cal.loc[
                                            keep_rows, W_Material_Consumption_Quantity_Plan_Output] - base_before_force).abs()

                            df_in_PlanSCSB_new_m_cal.loc[keep_rows, 'keep_priority'] = priority.values
                            df_in_PlanSCSB_new_m_cal.loc[keep_rows, 'keep_rank'] = priority.rank(method='first',
                                                                                                 ascending=False).values

                            j_keep = priority.idxmax()
                            df_in_PlanSCSB_new_m_cal.at[j_keep, 'keep_selected'] = True

                            df_in_PlanSCSB_new_m_cal.at[j_keep, 'keep_force_add'] += pool
                            pool = 0
                    df_in_PlanSCSB_new_m_cal.loc[rows, 'pool_after_keep'] = pool
                    df_in_PlanSCSB_new_m_cal.loc[rows, 'carry_out'] = pool
                    carry = pool

            # 최정 할당 수량 구함
            df_in_PlanSCSB_new_m_cal['final_qty'] = (
                    df_in_PlanSCSB_new_m_cal['Lot_Size']
                    + df_in_PlanSCSB_new_m_cal['realloc']
                    + df_in_PlanSCSB_new_m_cal['keep_force_add'])

            # df_in_Plan_SCSB_new_m_cal 컬럼명 변경
            df_in_PlanSCSB_new_m_cal = df_in_PlanSCSB_new_m_cal.rename(
                columns={W_Material_Consumption_Quantity_Plan_Output: Amend_SOP_ORG_SOP_Qty,
                         'final_qty': Amend_SOP_SOP_Qty})

            print_df(df_in_PlanSCSB_new_m_cal, "df_in_Plan_SCSB_new_m_cal_중간 데이터 확인", True)

            # 데이터 프레임 필터링
            df_in_PlanSCSB_new_m_cal = df_in_PlanSCSB_new_m_cal[filter_cols]

            note(f"===========  df_in_Plan_SCSB_new_m_cal =====================> {df_in_PlanSCSB_new_m_cal.shape} 최종확인")

            # 필터가 되지 않은 데이터 프레임 처리
            df_in_PlanSCSB_new_m = df_in_PlanSCSB_new_m.groupby(
                [Version_Name_COLUMN, Item_Column, Time_Week_COLUMN, Documents_OrderlineID_COLUMN, Location_COLUMN,
                 Activity1_Activity1_COLUMN, Activity2_Activity2_COLUMN, Activity3_Activity3_COLUMN],
                as_index=False).agg(
                W_Material_Consumption_Quantity_Plan_Output=(
                W_Material_Consumption_Quantity_Plan_Output, 'sum')).rename(
                columns={'W_Material_Consumption_Quantity_Plan_Output': Amend_SOP_SOP_Qty})

            df_in_PlanSCSB_new_m.loc[:, Amend_SOP_ORG_SOP_Qty] = df_in_PlanSCSB_new_m[Amend_SOP_SOP_Qty].copy()

            df_in_PlanSCSB_new_m = df_in_PlanSCSB_new_m[filter_cols]

            # 최종 out_put 설정
            df_in_PlanSCSB_new = pd.concat([df_in_PlanSCSB_new_m, df_in_PlanSCSB_new_m_cal])
            df_in_PlanSCSB_new = df_in_PlanSCSB_new.loc[
                ~df_in_PlanSCSB_new[Activity2_Activity2_COLUMN].str.contains('RT_')].copy()

            df_in_PlanSCSB = df_in_PlanSCSB_new_temp[
                [Version_Name_COLUMN, Item_Column, Time_Week_COLUMN, Documents_OrderlineID_COLUMN, Location_COLUMN,
                 Activity1_Activity1_COLUMN, Activity2_Activity2_COLUMN, Activity3_Activity3_COLUMN,
                 W_Material_Consumption_Quantity_Plan_Output]].copy()
            print_df(df_in_PlanSCSB, 'df_in_PlanSCSB _ 분리된 데이터 프레임 확인', False)
            print_df(df_in_PlanSCSB_new, 'df_in_PlanSCSB_new _ 분리되고 로직이 진행된 데이터 프레임 확인', False)
            note(
                f"== df_in_PlanSCSB_new_합계 =====> 비 작업대상 : {df_in_PlanSCSB.shape[0]}  +  "
                f"작업대상 : {df_in_PlanSCSB_new.shape[0]} = {df_in_PlanSCSB.shape[0] + df_in_PlanSCSB_new.shape[0]}")
        else:
            df_in_PlanSCSB_new = pd.DataFrame(columns=filter_cols)

        print_df(df_in_PlanSCSB_new, "df_in_PlanSCSB_new", True)

        step('=====> STEP 3 End')
        ################################################################################################################
        # Step 4 1차 Mfg Sop Qty을 구하기 위한 step
        ###############################################################################################################
        step('=====> STEP 4 Start : input data machining')
        # 기준이 되는 키 설정
        mg_group_cols = [Version_Name_COLUMN, Item_Column, Activity1_Activity1_COLUMN]

        # if를 진행하지 않을 시 Drop 되는 컬럼의 키 값 에러 방지
        if key_col not in df_in_WSoftLotSize.columns:
            df_in_WSoftLotSize[key_col] = pd.Series(index=df_in_WSoftLotSize.index, dtype='string')

        # df_in_Plan_SCSB 에 다시 Lot Size 수량 (W LotSize Increment) 를 merte 하여 구한다
        df_in_PlanSCSB = df_in_PlanSCSB.merge(
            df_in_WSoftLotSize.drop(
                columns=[Dummy, Location_COLUMN, Activity2_Activity2_COLUMN, Activity3_Activity3_COLUMN, key_col],
                axis=1),
            on=mg_group_cols, how='left')

        # lotSize컬럼이 (null일경우 1, 0일떄 1)으로 치환한다
        df_in_PlanSCSB[W_LotSize_Increment] = np.where(
            (df_in_PlanSCSB[W_LotSize_Increment].isna()) |
            (df_in_PlanSCSB[W_LotSize_Increment].eq(0)), 1,
            df_in_PlanSCSB[W_LotSize_Increment])

        df_in_PlanSCSB[Plan_cumsum] = df_in_PlanSCSB.groupby(mg_group_cols, as_index=False)[
            W_Material_Consumption_Quantity_Plan_Output].cumsum()
        df_in_PlanSCSB[Plan_MaxWeek] = df_in_PlanSCSB.groupby(mg_group_cols, as_index=False)[
            Time_Week_COLUMN].transform('max').astype(int)
        # cum_sum구할떄 소수점을 버림처리
        df_in_PlanSCSB[floor_qty] = (df_in_PlanSCSB[Plan_cumsum] // df_in_PlanSCSB[W_LotSize_Increment]) * \
                                    df_in_PlanSCSB[W_LotSize_Increment]
        # VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1 기준으로 데이터 다음 레코드로 복사처리한후 null일떄 0으로 처리
        df_in_PlanSCSB[New_qty] = df_in_PlanSCSB.groupby(mg_group_cols, as_index=False)[floor_qty].shift().fillna(0)

        # df_in_PlanSCSB 에 df_in_WResourceConsum 그래인이 포함된 내용에 Flag 설정 (Version, Location, Activity3 기준)
        keys = [Version_Name_COLUMN, Location_COLUMN, Activity3_Activity3_COLUMN]
        key_set = pd.MultiIndex.from_frame(df_in_WResourceConsum[keys].drop_duplicates())
        # Flat 설정
        df_in_PlanSCSB[flag] = np.where(
            pd.MultiIndex.from_frame(df_in_PlanSCSB[keys]).isin(key_set), 'Y', "N")

        # 할당 수량을 구한다 (조건 Flag가 Y 이고 마지막 주차 이면 Plan_Cumsum - New_qty 아니면 floor_qty - New_qty로 구함
        df_in_PlanSCSB[New_qty_1] = np.where(
            (df_in_PlanSCSB[flag].eq("Y") & df_in_PlanSCSB[Time_Week_COLUMN].eq(df_in_PlanSCSB[Plan_MaxWeek])),
            df_in_PlanSCSB[Plan_cumsum] - df_in_PlanSCSB[New_qty],
            df_in_PlanSCSB[floor_qty] - df_in_PlanSCSB[New_qty])

        print_df(df_in_PlanSCSB, "df_in_PlanSCSB 데이터 확인", True)
        # print_df(df_in_PlanSCSB, "df_in_PlanSCSB ===========> 확인", True)

        step('=====> STEP 4 End')
        ################################################################################################################
        # STEP 5 : Amend_SOP_MfgSOPQty : 1차 Sop Mfg Qty 확정
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')
        # 작업 대상 중 W_LotSize_Increment 1인 경우는 로직에서 제외한다
        df_in_PlanNASCS = df_in_PlanSCSB.loc[
            df_in_PlanSCSB[W_LotSize_Increment].isna() | (df_in_PlanSCSB[W_LotSize_Increment] <= 1)].copy()
        # Amend_SOP_ORG_SOP_Qty 값 설정
        df_in_PlanNASCS = df_in_PlanNASCS.rename(
            columns={W_Material_Consumption_Quantity_Plan_Output: Amend_SOP_ORG_SOP_Qty})
        # Amend_SOP_SOP_Qty 값 설정
        df_in_PlanNASCS.loc[:, Amend_SOP_SOP_Qty] = df_in_PlanNASCS[Amend_SOP_ORG_SOP_Qty]
        # 작업 대상을 필터링 한다
        df_in_PlanNASCS = df_in_PlanNASCS[filter_cols]
        print_df(df_in_PlanNASCS, "df_in_PlanNASCS 중간 데이터 확인", True)

        # 제외된 작업 대상끼리 합한다
        df_in_PlanNSCS = pd.concat([df_in_PlanNSCS, df_in_PlanNASCS], axis=0, ignore_index=True)

        # 다시 한번 '_RT' 가 아닌것을 다시 한번 필터한다
        df_in_PlanNSCS = df_in_PlanNSCS.loc[~df_in_PlanNSCS[Activity2_Activity2_COLUMN].str.contains('RT_')].copy()
        # # 컬럼명 변경
        # df_in_PlanNSCS = df_in_PlanNSCS.rename(columns={'New_qty_1': Amend_SOP_ORG_SOP_Qty})

        # 작업 대상을 다시 설정 한다
        df_in_PlanSCSB = df_in_PlanSCSB.loc[df_in_PlanSCSB[W_LotSize_Increment] > 1].copy()

        print_df(df_in_PlanNSCS, "df_in_PlanNSCS 데이터 확인_값 비교", True)
        print_df(df_in_PlanSCSB, "df_in_PlanSCSB 데이터 확인", True)

        step('=====> STEP 5 End')

        ################################################################################################################
        # STEP 6 : MFT(기획생산)인 대상에 대한 물량만 처리 step
        ################################################################################################################
        step('=====> STEP 6 Start : input data machining')
        #
        # MCT(단종) 관련 설정이 없는 품목기준으로, MFT(기획생산)인 대상에 대한 설정값 MAX 추차를 초과하는 구간이후에 물량중 가장 마지막 주자의 물량에서 LotSize만큼 물량을 제외함 (음수가 나올경우 0처리)
        #
        # 주차컬럼 데이터 형식을 integer로 치환한다
        # 치환하지 않으면 Local에서는 문제가 없지만 O9에서는 에러가 발생되므로 치환한다
        df_in_WResourceCapa.loc[:, Time_Week_COLUMN] = df_in_WResourceCapa[Time_Week_COLUMN].astype(int)

        # df_Resource_Capa : df_in_WResource_Consum2, df_in_WResource_Capa을 inner조건으로 새로운 데이터프레임을 구성한다.(LOCATION_LOCATION, 'Resource.[Resource]')
        df_ResourceCapa = df_in_WResourceConsum_temp.merge(
            df_in_WResourceCapa,
            on=[Version_Name_COLUMN, Location_COLUMN, Resource_Resource_COLUMN],
            how='inner')

        # Resource기준으로 Max(주차) 구한다
        df_ResourceCapa[Rank] = df_ResourceCapa.groupby([
            Resource_Resource_COLUMN, Activity3_Activity3_COLUMN, Location_COLUMN])[Time_Week_COLUMN].rank(
            method="first", ascending=False)
        # df_Resource_Capa에서 Max주차인 데이터만 재정의한다.
        df_ResourceCapa = df_ResourceCapa[df_ResourceCapa[Rank].eq(1)].copy()
        # out put 진행을 위한 컬럼 지정
        col_lists = [
            Version_Name_COLUMN, Resource_Resource_COLUMN, Resource_Resource_Type_COLUMN,
            Location_COLUMN, Time_Week_COLUMN, Activity3_Activity3_COLUMN]
        # out put 설정
        df_ResourceCapa = df_ResourceCapa[col_lists]


        # df_in_PlanSCSB & df_ResourceCapa Outjoin으로 데이터프레임을 구성한다.(LOCATION_LOCATION,ACTIVITY3_ACTIVITY3)
        df_in_PlanSCSB = df_in_PlanSCSB.merge(
            df_ResourceCapa, how='left',
            on=[Version_Name_COLUMN, Location_COLUMN, Activity3_Activity3_COLUMN],
            suffixes=('', '_y'), indicator=True)

        # df_in_PlanSCSB,df_in_WSoft_LotSize(LotSize수량)을 OutJoin으로 데이터프레임 구성한다(ITEM_ITEM, ACTIVITY1_ACTIVITY1)
        df_in_PlanSCSB = df_in_PlanSCSB.merge(
            df_in_WSoftLotSize.drop(columns=[Dummy], axis=1),
            on=mg_group_cols, how='left',
            suffixes=('', '_y'))

        # 각작업대상에 Shipment_LT을 OutJoin으로 추가한다(ACTIVITY1_ACTIVITY1, ACTIVITY3_ACTIVITY3)
        df_in_PlanSCSB = df_in_PlanSCSB.merge(
            df_in_ShipmentLT.drop(columns=[Dummy], axis=1), how='left',
            on=[Version_Name_COLUMN, Activity1_Activity1_COLUMN, Activity3_Activity3_COLUMN])

        df_in_PlanSCSB = df_in_PlanSCSB.rename(columns={New_qty_1: Amend_SOP_ORG_SOP_Qty})

        # 재구성한 df_in_PlanSCSB('both', 'left_only')으로 작업대상을 분리한다.
        df_out_AmendQty1 = df_in_PlanSCSB.loc[df_in_PlanSCSB[_merge].str.contains(both)].copy()
        df_out_AmendQty2 = df_in_PlanSCSB.loc[df_in_PlanSCSB[_merge].str.contains(left_only)].copy()

        print_df(df_out_AmendQty1 , 'df_out_AmendQty1 전처리 전 데이터 확인', True)
        print_df(df_out_AmendQty2,  'df_out_AmendQty2 전처리 전 데이터 확인', True)

        # 각작업대상에 Shipment_LT을 OutJoin으로 추가한다(ACTIVITY1_ACTIVITY1, ACTIVITY3_ACTIVITY3)
        df_out_AmendQty1.loc[:, Time_Week_COLUMN] = df_out_AmendQty1[Time_Week_COLUMN].astype(int)
        df_out_AmendQty1[Rank] = df_out_AmendQty1.groupby(
            [Item_Column, Activity1_Activity1_COLUMN, Activity3_Activity3_COLUMN])[Time_Week_COLUMN].rank(
            method='first', ascending=False)
        df_out_AmendQty1 = df_out_AmendQty1.rename(columns={'Activity2.[Activity2]_x': Activity2_Activity2_COLUMN})
        df_out_AmendQty1['Time.[Week]_x'] = df_out_AmendQty1['Time.[Week]_y'] + df_out_AmendQty1[
            W_Activity_Mandatory_Offset]

        df_out_AmendQty1[Amend_SOP_SOP_Qty] = np.where(
            (df_out_AmendQty1[Time_Week_COLUMN] > df_out_AmendQty1['Time.[Week]_x']) & (df_out_AmendQty1[Rank].eq(1)),
            df_out_AmendQty1[Amend_SOP_ORG_SOP_Qty] - df_out_AmendQty1[W_LotSize_Increment],
            df_out_AmendQty1[Amend_SOP_ORG_SOP_Qty])

        df_out_AmendQty1[Amend_SOP_SOP_Qty] = np.where(
            df_out_AmendQty1[Amend_SOP_SOP_Qty] <= 0, 0,
            df_out_AmendQty1[Amend_SOP_SOP_Qty])

        df_out_AmendQty1[Amend_SOP_ORG_SOP_Qty] = np.where(
            df_out_AmendQty1[Amend_SOP_ORG_SOP_Qty] <= 0, 0,
            df_out_AmendQty1[Amend_SOP_ORG_SOP_Qty])

        print_df(df_out_AmendQty1 , 'df_out_AmendQty1 데이터 확인', True)

        step('=====> STEP 6 End')
        ################################################################################################################
        # STEP 7 : 확정대상 ("MCT","SCT","MFT","SRT") 이 아닌 일반물량 처리 step
        ################################################################################################################
        step('=====> STEP 7 Start : input data machining')
        # 데이터 프레임 컬럼명 변경
        df_out_AmendQty2.rename(columns={'Activity2.[Activity2]_x': Activity2_Activity2_COLUMN}, inplace=True)
        # 데이터 프레임 필터링
        df_out_AmendQty2 = df_out_AmendQty2[[
            Version_Name_COLUMN, Item_Column, Time_Week_COLUMN, Documents_OrderlineID_COLUMN, Location_COLUMN,
            Activity1_Activity1_COLUMN, Activity2_Activity2_COLUMN, Activity3_Activity3_COLUMN, Amend_SOP_ORG_SOP_Qty]]

        df_out_AmendQty2 = df_out_AmendQty2.merge(
            df_in_WResourceConsum[keys].drop_duplicates(),
            how='left', suffixes=('', '_y'), indicator=True)

        df_out_AmendQty2 = df_out_AmendQty2.merge(
            df_in_WSoftLotSize[
                [Version_Name_COLUMN, Item_Column, Activity1_Activity1_COLUMN,
                 Activity3_Activity3_COLUMN, W_LotSize_Increment]], how='left',
            on=[Version_Name_COLUMN, Item_Column, Activity1_Activity1_COLUMN, Activity3_Activity3_COLUMN])

        df_out_AmendQty2.loc[:, W_LotSize_Increment] = np.where(
            df_out_AmendQty2[W_LotSize_Increment].isna() | df_out_AmendQty2[W_LotSize_Increment] == 0, 0,
            df_out_AmendQty2[W_LotSize_Increment])

        df_out_AmendQty2.loc[:, Rank] = df_out_AmendQty2.groupby(
            [Item_Column, Activity1_Activity1_COLUMN])[Time_Week_COLUMN].rank(
            method="first", ascending=False)

        # 가장 마지막 주자의 물량에서 LotSize만큼 물량을 제외한다.
        df_out_AmendQty2.loc[:, Amend_SOP_SOP_Qty] = np.where(
            (df_out_AmendQty2[Rank] == 1) % (df_out_AmendQty2[_merge].str.contains(left_only)),
            df_out_AmendQty2[Amend_SOP_ORG_SOP_Qty] - df_out_AmendQty2[W_LotSize_Increment],
            df_out_AmendQty2[Amend_SOP_ORG_SOP_Qty])
        df_out_AmendQty2.loc[:, Amend_SOP_ORG_SOP_Qty] = np.where(
            df_out_AmendQty2[Amend_SOP_ORG_SOP_Qty] <= 0, 0,
            df_out_AmendQty2[Amend_SOP_ORG_SOP_Qty])

        df_out_AmendQty1 = df_out_AmendQty1[filter_cols]
        df_out_AmendQty2 = df_out_AmendQty2[filter_cols]

        print_df(df_out_AmendQty1 , 'df_out_AmendQty1 ___ 확인', False)
        print_df(df_out_AmendQty2,  'df_out_AmendQty2 ___ 확인', False)

        # 위 작업한 1) 과 2)을 합친다.
        # df_Amend_SOP_MfgSOPQty : MFT(기획생산)인 대상에 대한 물량과 확정대상 ("MCT","SCT","MFT","SRT") 이 아닌 일반물량을 하나의 데이터프레임으로 합친다.
        df_AmendSOPMfgSOPQty = pd.concat([df_out_AmendQty1,df_out_AmendQty2], axis = 0, ignore_index = True)
        print_df(df_AmendSOPMfgSOPQty, 'df_AmendSOPMfgSOPQty ___ 확인', False)

        df_in_PlanNSCS = df_in_PlanNSCS[filter_cols]
        df_in_PlanSCSB_new = df_in_PlanSCSB_new[filter_cols]

        print_df(df_in_PlanNSCS, "df_in_PlanNSCS___최종데이터 확인", True)
        print_df(df_in_PlanSCSB_new, "df_in_PlanSCSB_new___최종데이터 확인", True)
        print_df(df_AmendSOPMfgSOPQty, "df_AmendSOPMfgSOPQty___최종데이터 확인", True)

        #최종적으로 작업한 dataset이랑 비작업대상인 DataSet을 합친다.
        dfs = [df_in_PlanNSCS, df_in_PlanSCSB_new, df_AmendSOPMfgSOPQty]
        dfs = [d.dropna(axis=1, how='all') for d in dfs]
        df_out_AmendSOPMfgSOPQty = pd.concat( dfs, axis=0, ignore_index=True) if dfs else pd.DataFrame()

        df_out_AmendSOPMfgSOPQty[Version_Name_COLUMN] = pd.Series(index=df_out_AmendSOPMfgSOPQty.index, dtype='string')
        df_out_AmendSOPMfgSOPQty[Version_Name_COLUMN] = paramOutVersion

        row_count, col_count = df_out_AmendSOPMfgSOPQty.shape

        print_df(df_out_AmendSOPMfgSOPQty, "df_out_AmendSOPMfgSOPQty____확인", True)

        step('=====> STEP 7 End')

        ################################################################################################################
        # Step 3. 종료
        ################################################################################################################

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_AmendSOPMfgSOPQty, 'df_out_AmendSOPMfgSOPQty', True)

        print_df(df_out_AmendSOPMfgSOPQty, 'df_out_AmendSOPMfgSOPQty', True)

        row_count, col_count = df_out_AmendSOPMfgSOPQty.shape
        note(f'=====> Final df_out_AmendSOPMfgSOPQty rows : {row_count} , Columns : {col_count}')


    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_ProductSetW = pd.DataFrame([], columns=[])
        df_out_ProductSetWSub = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

        df_out_AmendSOPMfgSOPQty = pd.DataFrame([], columns=[])

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

