"""

* 프로그램명
    - PY_UI_FCSTRTFHist

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.03.19 / ybest7.park (박병훈) / Create
- 2025.03.27 / ybest7.park (박병훈) / 수정
- 2025.04.16 / ybest7.park (박병훈) / 수정
- 2025-07-01 / ybest7.park (박병훈) / 수정 Step 8 추가
- 2025-07-10 / ybest7.park (박병훈) / 수정 df_in_FCSTRTFHistW 범위 수정
- 2025-07-25 / ybest7.park (박병훈) / 수정 df_in_RTFHistW MG 수정
- 2025-07-28 / ybest7.park (박병훈) / 수정 df_in_RTFHistW MG 수정
- 2025-07-30 / ybest7.park (박병훈) /  Input Data 및 전체적인 프로그램 수정
- 2025-08-28 / ybest7.park (박병훈) /  수정 (Item mapping Logic 삭제 및 Input Data 수정)
- 2025-09-03 / ybest7.park (박병훈) /  수정 이전 주차 Fcst 값이 0 이면 Null로 변경
- 2025-09-09 / ybest7.park (박병훈) /  수정 Week2 설정 로직 변경
- 2025-10-20 / ybest7.park (박병훈) /  수정 Fcst에 input 쿼리 수정 및 처리 로직 추가 (RTF_Hist_W_Global_RTF 전 주 값 반영)
- 2025-10-28 / ybest7.park (박병훈) /  수정 input Query 수정 Week1 에 filter 적용 당주 Plan만 가지고 들어오는 것으로 수정
- 2026-03-19 / ybest7.park (박병훈) /  수정 input Query 수정 CalCurrentWeek → CurrentWeek 로 input Query 수정

* Input
- in_MfgPlan = pd.read_csv(' .csv')

* Flow Summary

* Input Table
    - df_in_MtrlSupplyActual = Select ([Version].[Version Name] * &Last4WeeksAandFuture.filter(#.Key < &CurrentWeek.element(0).Key) * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] ) on row,({Measure.[Mtrl Supply Actual_Qty_All],Measure.[Mtrl Supply Actual_Config Type], Measure.[Dummy]}) on column where{~isnull(Measure.[Mtrl Supply Actual_Qty_All]) && (Measure.[Mtrl Supply Actual_Config Type] in {"Global RTF","RTF"})};
    - df_in_FCSTRTFHistW = Select ([Version].[Version Name]* &Last4WeeksAandFuture.filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-1).Key) * [Location].[Location] * [To Time].[To Week] * [Week1].[Week1].filter(#.Key == &CurrentWeek.element(0).LeadOffset(-1).Key) * [Week2].[Week2] * [Item Material].[Item Material] * [Sub Location].[Sub Location] ) on row, ({Measure.[FCST RTF Hist W_Global Fcst_All], Measure.[FCST RTF Hist W_Global RTF_All], Measure.[FCST RTF Hist W_Global SCM Plan_All], Measure.[FCST RTF Hist W_Fcst_All],Measure.[FCST RTF Hist W_RTF_All], Measure.[FCST RTF Hist W_SCM Plan_All], Measure.[FCST RTF Hist W_Config Type], Measure.[Dummy]}) on column where{(Measure.[Mtrl Supply Actual_Config Type] in {"Global RTF","RTF"})};
    - df_in_TimeWeekRange = select(&Last4WeeksAandFuture);

* 데이턱 샂게
    - DELETE DATA FOR MODEL [RTF Hist W] where {Version.[Version Name].[CWV_MP]};

* 유의 사항
    - df_in_MultiSite에 신규 데이터 없을 시 프로그램 결과 null값 반영됨

     # Scope :([Version].[Version Name].filter(#.Name == "CWV_MP") * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-4).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(12).Key));
     # Measure.[RTF Hist W_Global Fcst]   = null;
     # Measure.[RTF Hist W_Global RTF]   = null;
     # Measure.[RTF Hist W_Global SCM Plan]   = null;
     # Measure.[RTF Hist W_Fcst]   = null;
     # Measure.[RTF Hist W_RTF]   = null;
     # Measure.[RTF Hist W_SCM Plan]   = null;
     # end scope;

* Output Table
    - df_out_RTFHistW = Select (&CWVUI * [Location].[Location] * [Time].[Week] * [To Time].[To Week] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Week2].[Week2] ) on row, ({Measure.[RTF Hist W_Config Type], Measure.[RTF Hist W_FCST], Measure.[RTF Hist W_Global FCST], Measure.[RTF Hist W_Global RTF], Measure.[RTF Hist W_Global SCM Plan], Measure.[RTF Hist W_RTF], Measure.[RTF Hist W_SCM Plan]}) on column;

    - df_out_log
    - df_out_logDetail

* 테스트 스크립트
    EXEC plugin instance [PY_UI_FCSTRTFHist] for measures {[RTF Hist W_Fcst]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"), (ParamOutVersion, "CWV_MP")} ;


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
import pytz
########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_FCSTRTFHist'
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
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP 1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_MtrlSupplyActual    = read_csv_file('df_in_MtrlSupplyActual')
            df_in_FCSTRTFHistW        = read_csv_file('df_in_FCSTRTFHistW')
            df_in_TimeWeekRange       = read_csv_file('df_in_TimeWeekRange')


        dataframes = {
            'df_in_MtrlSupplyActual'  :          df_in_MtrlSupplyActual,
            'df_in_FCSTRTFHistW'      :          df_in_FCSTRTFHistW,
            'df_in_TimeWeekRange'     :          df_in_TimeWeekRange}

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP 1 End')
        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP 2 Start : DataFrame Column 변수 처리')

        Version_Name_COLUMN = 'Version.[Version Name]'
        Time_Week_COLUMN = 'Time.[Week]'
        Location_COLUMN = 'Location.[Location]'
        Item_Material_COLUMN = 'Item Material.[Item Material]'
        Sub_Location_COLUMN = 'Sub Location.[Sub Location]'
        Sequence_COLUMN = 'Sequence.[Sequence]'
        Item_Material_MSL5_COLUMN = 'Item Material.[MSL5]'
        To_Week_COLUMN = 'To Time.[To Week]'
        Week1_COLUMN = 'Week1.[Week1]'
        Week2_COLUMN = 'Week2.[Week2]'

        Mtrl_Supply_Actual_Qty_All = 'Mtrl Supply Actual_Qty_All'
        Mtrl_Supply_Actual_Config_Type = 'Mtrl Supply Actual_Config Type'

        FCST_RTF_Hist_W_Global_Fcst_All = 'FCST RTF Hist W_Global Fcst_All'
        FCST_RTF_Hist_W_Global_RTF_All = 'FCST RTF Hist W_Global RTF_All'
        FCST_RTF_Hist_W_Global_SCM_Plan_All = 'FCST RTF Hist W_Global SCM Plan_All'
        FCST_RTF_Hist_W_Fcst_All = 'FCST RTF Hist W_Fcst_All'
        FCST_RTF_Hist_W_RTF_All = 'FCST RTF Hist W_RTF_All'
        FCST_RTF_Hist_W_SCM_Plan_All = 'FCST RTF Hist W_SCM Plan_All'
        FCST_RTF_Hist_W_Config_Type = 'FCST RTF Hist W_Config Type'

        RTF_Hist_W_Global_Fcst = 'RTF Hist W_Global FCST'
        RTF_Hist_W_Global_RTF = 'RTF Hist W_Global RTF'
        RTF_Hist_W_Global_SCM_Plan = 'RTF Hist W_Global SCM Plan'
        RTF_Hist_W_Fcst = 'RTF Hist W_FCST'
        RTF_Hist_W_RTF = 'RTF Hist W_RTF'
        RTF_Hist_W_SCM_Plan = 'RTF Hist W_SCM Plan'
        RTF_Hist_W_Config_Type = 'RTF Hist W_Config Type'

        step('=====> STEP 2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP 3 Start : input data machining')

        # 당주 설정 다음주 설정
        current_week = df_in_TimeWeekRange[Time_Week_COLUMN].iloc[24]
        next_week = df_in_TimeWeekRange[Time_Week_COLUMN].iloc[25]
        last_week = df_in_TimeWeekRange[Time_Week_COLUMN].iloc[23]
        note(f'current_week :{current_week}')
        note(f'next_week :{next_week}')
        note(f'last_week :{last_week}')

        # FCST Week List 설정
        fcst_weeks = df_in_TimeWeekRange[Time_Week_COLUMN].iloc[24:].to_list()

        ################################### 2025-10-20 추가 ybest7.part(박병훈)##########################################
        # RTF를 포함한 실적은 전주 내용을 반영하기 위한 필터링
        # 전주 FCST 데이터 프레임으로 설정
        # df_in_FCSTRTFHistW[Time_Week_COLUMN] = df_in_FCSTRTFHistW[Time_Week_COLUMN].astype(int)
        df_in_Currentweek = df_in_FCSTRTFHistW[df_in_FCSTRTFHistW[Time_Week_COLUMN] == current_week].copy()
        # 필요한 컬럼만 선택
        df_in_Currentweek = df_in_Currentweek[
            [Version_Name_COLUMN, Time_Week_COLUMN, Location_COLUMN, To_Week_COLUMN, Week1_COLUMN, Week2_COLUMN,
             Item_Material_COLUMN, Sub_Location_COLUMN, FCST_RTF_Hist_W_Global_RTF_All, FCST_RTF_Hist_W_RTF_All]]

        print_df(df_in_Currentweek, 'df_in_Currentweek 학인용 step 01', True)

        # 기존 데이터 로직에 따른 데이터 프레임 설정 (기존 로직 수정을 최소화 하기 위한 데이터 프레임 설정 )
        df_in_FCSTRTFHistW = df_in_FCSTRTFHistW[df_in_FCSTRTFHistW[Time_Week_COLUMN] >= current_week]

        ################################### 2025-10-20 추가 ybest7.part(박병훈)##########################################

        # df_in_FCSTRTFHistW Base Frame 설정
        df_in_FCSTRTFHistW_base = df_in_FCSTRTFHistW[
            [Version_Name_COLUMN, Location_COLUMN, To_Week_COLUMN, Week1_COLUMN, Week2_COLUMN,
             Item_Material_COLUMN, Sub_Location_COLUMN]].drop_duplicates(ignore_index=True)

        # FCST 주차로 확장
        df_in_FCSTRTFHistW_base[Time_Week_COLUMN] = [fcst_weeks] * len(df_in_FCSTRTFHistW_base)
        df_in_FCSTRTFHistW_base = df_in_FCSTRTFHistW_base.explode(Time_Week_COLUMN, ignore_index=True)



        # df_in_FCSTRTFHistW Temp 설정
        df_in_FCSTRTFHistW_temp = df_in_FCSTRTFHistW.copy()

        # output columns 설정
        out_rename_Columns_dict = {
            FCST_RTF_Hist_W_Global_Fcst_All: RTF_Hist_W_Global_Fcst, FCST_RTF_Hist_W_Global_RTF_All: RTF_Hist_W_Global_RTF,
            FCST_RTF_Hist_W_Global_SCM_Plan_All: RTF_Hist_W_Global_SCM_Plan, FCST_RTF_Hist_W_Fcst_All: RTF_Hist_W_Fcst,
            FCST_RTF_Hist_W_RTF_All: RTF_Hist_W_RTF, FCST_RTF_Hist_W_SCM_Plan_All: RTF_Hist_W_SCM_Plan,
            FCST_RTF_Hist_W_Config_Type: RTF_Hist_W_Config_Type
        }

        # columns 변경
        df_in_FCSTRTFHistW_temp = df_in_FCSTRTFHistW_temp.rename(columns=out_rename_Columns_dict)

        print_df(df_in_FCSTRTFHistW_base, 'df_in_FCSTRTFHistW_base 학인용 step 02', True)
        print_df(df_in_FCSTRTFHistW_temp, 'df_in_FCSTRTFHistW_temp 학인용 step 03', True)

        df_in_FCSTRTFHistW_base.loc[:,Time_Week_COLUMN] = df_in_FCSTRTFHistW_base[Time_Week_COLUMN].astype(str)
        df_in_FCSTRTFHistW_temp[Time_Week_COLUMN] = df_in_FCSTRTFHistW_temp[Time_Week_COLUMN].astype(str)

        # merge key 설정
        merge_keys = [Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, To_Week_COLUMN,
                      Week1_COLUMN, Week2_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN]
        # FCST 기본 테을에 FCST 데이터 merge
        df_in_FCSTRTFHistW_base = df_in_FCSTRTFHistW_base.merge(df_in_FCSTRTFHistW_temp, on=merge_keys,
                                                                how='left').drop(columns='Dummy')

        print_df(df_in_FCSTRTFHistW_base, 'df_in_FCSTRTFHistW_base step 02', True)

        step('=====> STEP 3 End')
        ################################################################################################################
        # Step 4. Actual 설정 및 정리
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')

        df_in_MtrlSupplyActual[Mtrl_Supply_Actual_Config_Type] = df_in_MtrlSupplyActual[
            Mtrl_Supply_Actual_Config_Type].fillna('-')
        # 실적 기본 데이터 만들기
        df_in_MtrlSupplyActual_base = df_in_MtrlSupplyActual[
            [Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
             Mtrl_Supply_Actual_Config_Type]].drop_duplicates(
            ignore_index=True)
        # 주차 리스트 만들기
        Actual_week_list = df_in_MtrlSupplyActual[Time_Week_COLUMN].unique().tolist()
        # 확장을 위한 컬럼 생성
        df_in_MtrlSupplyActual_base[Time_Week_COLUMN] = df_in_MtrlSupplyActual_base.apply(lambda x: Actual_week_list,
                                                                                          axis=1)
        # Actual_week_list로 확장
        df_in_MtrlSupplyActual_base = df_in_MtrlSupplyActual_base.explode(Time_Week_COLUMN)
        # Actual_week_list로 이름 변경 및 인덱스 재 설정
        df_in_MtrlSupplyActual_base.reset_index(drop=True, inplace=True)

        print_df(df_in_MtrlSupplyActual, 'df_in_MtrlSupplyActual_base _ df_in_MtrlSupplyActual_base 확인 step 03', True)

        # Merge를 위하 Time_Week_COLUMN 타입 변경
        df_in_MtrlSupplyActual_base[Time_Week_COLUMN] = df_in_MtrlSupplyActual_base[Time_Week_COLUMN].astype(str)
        df_in_MtrlSupplyActual[Time_Week_COLUMN] = df_in_MtrlSupplyActual[Time_Week_COLUMN].astype(str)

        # 'Version.[Version Name]', 'Location.[Location]', 'Item Material.[Item Material]', 'Sub Location.[Sub Location]' 'Time.[Week],Mtrl_Supply_Actual_Config_Type'
        action_merge_keys = [Version_Name_COLUMN, Location_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
                             Time_Week_COLUMN, Mtrl_Supply_Actual_Config_Type]
        note(f"action_merge_keys: {action_merge_keys}")

        # df_in_MtrlSupplyActual_base 와 실적 데이터 merge
        df_in_MtrlSupplyActual_base = df_in_MtrlSupplyActual_base.merge(df_in_MtrlSupplyActual, on=action_merge_keys,
                                                                        how='left').drop(columns='Dummy')

        # Mtrl_Supply_Actual_Qty_All 값 변경
        df_in_MtrlSupplyActual_base[Mtrl_Supply_Actual_Qty_All] = df_in_MtrlSupplyActual_base[
            Mtrl_Supply_Actual_Qty_All].fillna(0).astype(int)
        # df_in_MtrlSupplyActual_base.dropna(subset=[Mtrl_Supply_Actual_Qty_All], inplace=True)

        # Supply_Plan_Source_Map_Source 이 null 인것 필터링
        df_in_MtrlSupplyActual_base = df_in_MtrlSupplyActual_base[
            df_in_MtrlSupplyActual_base[Mtrl_Supply_Actual_Config_Type].notna()]

        # Supply_Plan_Source_Map_Source 이 Global 인 경우 P105로 변환
        df_in_MtrlSupplyActual_base[Sub_Location_COLUMN] = np.where(
            df_in_MtrlSupplyActual_base[Mtrl_Supply_Actual_Config_Type] == 'Global RTF', 'P105',
            df_in_MtrlSupplyActual_base[Sub_Location_COLUMN])

        # To_Week_COLUMN  &  Week1_COLUMN 설정
        df_in_MtrlSupplyActual_base[To_Week_COLUMN] = last_week  # 당주로 설정
        df_in_MtrlSupplyActual_base[Week1_COLUMN] = current_week  # 다음주 설정

        ############################################# 2025-09-10 수정 ######################################################

        # # Week2 설정
        # df_in_MtrlSupplyActual_base['Week2_COLUMN_Actual'] = df_in_MtrlSupplyActual_base[week2_keys_cols].apply(tuple, axis=1).map(
        #     wee2_series)
        # # Week2 타입 변경 및 빈값 처리
        # df_in_MtrlSupplyActual_base['Week2_COLUMN_Actual'] = df_in_MtrlSupplyActual_base['Week2_COLUMN_Actual'].fillna('202001').astype(int)
        ############################################# 2025-09-10 수정 ######################################################

        # Mtrl_Supply_Actual_Qty_All group by를 통한 집계 및 reset_index
        df_in_MtrlSupplyActual = df_in_MtrlSupplyActual_base.groupby(
            [Version_Name_COLUMN, Time_Week_COLUMN, Location_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
             To_Week_COLUMN, Week1_COLUMN, Mtrl_Supply_Actual_Config_Type])[
            Mtrl_Supply_Actual_Qty_All].sum().reset_index()

        # Column 명 변경
        df_in_MtrlSupplyActual = df_in_MtrlSupplyActual.rename(
            columns={Mtrl_Supply_Actual_Config_Type: RTF_Hist_W_Config_Type})

        print_df(df_in_MtrlSupplyActual, 'df_in_MtrlSupplyActual _ step 04', True)

        step('=====> STEP 4 End')

        ################################################################################################################
        # Step 5. Actual 설정 및 정리
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')

        # merge를 위한 주차 설정 타입 변경
        int_col = [Time_Week_COLUMN, Week1_COLUMN, To_Week_COLUMN, Week2_COLUMN]
        # 벡터 연산을 통해 데이터 타입 변경
        # df_in_FCSTRTFHistW_base[int_col] = df_in_FCSTRTFHistW_base[int_col].astype(str)
        # df_in_MtrlSupplyActual[int_col] = df_in_FCSTRTFHistW_base[int_col].astype(str)
        # 반복문을 통해 데이터 타입 변환
        # for df in (df_in_FCSTRTFHistW_base, df_in_MtrlSupplyActual):
        #     cols = df.columns.intersection(int_col)
        #     df.loc[:, cols] = df.loc[:, cols].astype('string')
        # for col in int_col:
        #     df_in_FCSTRTFHistW_base[col] = df_in_FCSTRTFHistW_base[col].astype(str)
        #     df_in_MtrlSupplyActual[col] = df_in_MtrlSupplyActual[col].astype(str)

        for df in (df_in_FCSTRTFHistW_base, df_in_MtrlSupplyActual):
            cols = [col for col in int_col if col in df.columns]
            for col in cols:
                df[col] = df[col].astype('string')

        # 실적과 FCST를 merge 하기 위한 컬럼 설정
        out_merge_keys_col = [Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, To_Week_COLUMN, Week1_COLUMN,
                              Item_Material_COLUMN, Sub_Location_COLUMN, RTF_Hist_W_Config_Type]

        df_out_RTFHistW = df_in_FCSTRTFHistW_base.merge(
            df_in_MtrlSupplyActual, on=out_merge_keys_col, how='outer')

        print_df(df_out_RTFHistW, 'df_out_RTFHistW step 05- 확인용 Week2', True)

        ###################2025-10-28 추가 로직 ########################################################################

        # Week2 설정을 위한 로직 추가 (2025-09-10)
        # FCST를 통해 Week2 설정하기 하기 위한 key 지정
        fcst_merge_col = [Version_Name_COLUMN, Item_Material_COLUMN, Sub_Location_COLUMN,
                          To_Week_COLUMN, Week1_COLUMN]

        # FCST Week2 Type 변경
        df_in_FCSTRTFHistW_base[Week2_COLUMN] = df_in_FCSTRTFHistW_base[Week2_COLUMN].astype('int64')
        # Week2 갑 설정
        fcst_week2_df = df_in_FCSTRTFHistW_base.groupby(fcst_merge_col)[Week2_COLUMN].max().reset_index()

        print_df(fcst_week2_df, 'fcst_week2_df step 06 - 확인용', True)
        # merge 시 중복을 피하기 위한 컬럼명 변경
        fcst_week2_df.rename(columns={Week2_COLUMN: 'fcst_week2_max'}, inplace=True)
        # df_out_RTFHistW 와 merge
        df_out_RTFHistW = df_out_RTFHistW.merge(fcst_week2_df, on=fcst_merge_col, how='left')
        # Week2 값 채우기
        df_out_RTFHistW[Week2_COLUMN] = np.where(df_out_RTFHistW[Week2_COLUMN].isna(),
                                                 df_out_RTFHistW['fcst_week2_max'],
                                                 df_out_RTFHistW[Week2_COLUMN])

        print_df(df_out_RTFHistW, 'df_out_RTFHistW step 07 - 확인용', True)
        note(f"Week2_COLUMN is null 의 합계 : {df_out_RTFHistW[Week2_COLUMN].isna().sum()}")
        df_out_RTFHistW[Week2_COLUMN] = df_out_RTFHistW[Week2_COLUMN].fillna("202001")
        df_out_RTFHistW[Week2_COLUMN] = df_out_RTFHistW[Week2_COLUMN].astype(int).astype(str)

        ############################################# 2025-09-10 수정 완료 ##################################################

        mg_cols = [RTF_Hist_W_Global_Fcst, RTF_Hist_W_Global_RTF, RTF_Hist_W_Global_SCM_Plan,
                   RTF_Hist_W_Fcst, RTF_Hist_W_RTF, RTF_Hist_W_SCM_Plan, Mtrl_Supply_Actual_Qty_All]

        out_global_cols = [RTF_Hist_W_Global_RTF, RTF_Hist_W_Global_SCM_Plan]
        out_rtf_cols = [RTF_Hist_W_RTF, RTF_Hist_W_SCM_Plan]

        print_df(df_out_RTFHistW, 'df_out_RTFHistW step 08- 확인용', True)
        # Measure columns 설정 Data Type 변경
        for col in mg_cols:
            df_out_RTFHistW[col] = df_out_RTFHistW[col].fillna(0).astype(int)

        # Supply_Plan_Source_Map_Source 설정에 따라 Output Data 값 설정
        # GlobalRTF 처리
        mask_global = df_out_RTFHistW[RTF_Hist_W_Config_Type] == 'Global RTF'
        for col in out_global_cols:
            df_out_RTFHistW.loc[mask_global, col] = (
                    df_out_RTFHistW.loc[mask_global, col].fillna(0) +
                    df_out_RTFHistW.loc[mask_global, Mtrl_Supply_Actual_Qty_All].fillna(0))

        # RTF 처리
        mask_rtf = df_out_RTFHistW[RTF_Hist_W_Config_Type] == 'RTF'
        for col in out_rtf_cols:
            df_out_RTFHistW.loc[mask_rtf, col] = (
                    df_out_RTFHistW.loc[mask_rtf, col].fillna(0) +
                    df_out_RTFHistW.loc[mask_rtf, Mtrl_Supply_Actual_Qty_All].fillna(0))

        for col in mg_cols:
            df_out_RTFHistW[col] = df_out_RTFHistW[col].replace('', 0).fillna(0).astype(int)
            # df_out_RTFHistW[col] = df_out_RTFHistW[col].replace('', 0).fillna(0).astype(int).replace(0, np.nan)

        # Columns 지정
        Global_RTF_COL = [RTF_Hist_W_Global_Fcst, RTF_Hist_W_Global_RTF, RTF_Hist_W_Global_SCM_Plan]
        RTF_COL = [RTF_Hist_W_Fcst, RTF_Hist_W_RTF, RTF_Hist_W_SCM_Plan]

        # RTF_Hist_W_Config_Type 타입 마스크
        m_global = df_out_RTFHistW[RTF_Hist_W_Config_Type].eq('Global RTF')
        m_rtf = df_out_RTFHistW[RTF_Hist_W_Config_Type].eq('RTF')

        # 조건에 따라 행당 컬럼들 NAN로
        df_out_RTFHistW.loc[m_global, RTF_COL] = np.nan
        df_out_RTFHistW.loc[m_rtf, Global_RTF_COL] = np.nan

        # # # Mtrl_Supply_Actual_Config_Type 컬럼명 변경
        # # df_out_RTFHistW = df_out_RTFHistW.rename(columns={Mtrl_Supply_Actual_Config_Type: RTF_Hist_W_Config_Type})
        #
        # # RTF_Hist_W_Config_Type null 값 채우기
        # df_out_RTFHistW[RTF_Hist_W_Config_Type] = df_out_RTFHistW[RTF_Hist_W_Config_Type].fillna(
        #     df_out_RTFHistW[Item_Material_COLUMN].map(RTF_Hist_W_Config_Type_dict))

        # for col in mg_cols:
        #     df_out_RTFHistW[col] = df_out_RTFHistW[col].fillna(0).astype("int64")

        df_out_RTFHistW[Time_Week_COLUMN] = df_out_RTFHistW[Time_Week_COLUMN].astype('int64')
        ########################################## 2025-09-03 수정 ########################################################
        # Fcst Col 설정
        fcst_col = [RTF_Hist_W_Global_Fcst, RTF_Hist_W_Fcst]
        # current_week Type 변경
        next_week = int(next_week)

        # 과거 주차 마스크
        m_past = df_out_RTFHistW[Time_Week_COLUMN].astype(int).lt(next_week)
        # note(f"m_past 출력 = {m_past}")
        # 과거 주차 FCST == 0 -> NaN으로 변경
        df_out_RTFHistW.loc[m_past, fcst_col] = df_out_RTFHistW.loc[m_past, fcst_col].mask(
            df_out_RTFHistW.loc[m_past, fcst_col].eq(0), np.nan)

        ########################################## 2025-09-03 수정 ########################################################

        out_put_mg_columns = [
            Version_Name_COLUMN, Location_COLUMN, Time_Week_COLUMN, To_Week_COLUMN, Week1_COLUMN, Week2_COLUMN,
            Item_Material_COLUMN, Sub_Location_COLUMN, RTF_Hist_W_Config_Type, RTF_Hist_W_Global_Fcst,
            RTF_Hist_W_Global_RTF, RTF_Hist_W_Global_SCM_Plan, RTF_Hist_W_Fcst, RTF_Hist_W_RTF, RTF_Hist_W_SCM_Plan]

        df_out_RTFHistW = df_out_RTFHistW[out_put_mg_columns]

        ################################### 2025-10-20 추가 ybest7.part(박병훈)##########################################
        # Week2에 빈 값이 있는 경우 MAX로 채우기 위한 전처리
        current_week2_df = df_in_Currentweek.groupby(fcst_merge_col)[Week2_COLUMN].max().reset_index()
        # merge 시 혼선을 줄이기 위해 week2 컬럼명 변경
        current_week2_df.rename(columns={Week2_COLUMN: 'fcst_week2_max'}, inplace=True)
        # df_in_Currentweek 와 새로이 생성된 Week2 merge
        df_in_Currentweek = df_in_Currentweek.merge(current_week2_df, on=fcst_merge_col, how='left')
        # Week2 값이 빈 값인 경우 Max로 채우기
        df_in_Currentweek[Week2_COLUMN] = np.where(df_in_Currentweek[Week2_COLUMN].isna(),
                                                   df_in_Currentweek['fcst_week2_max'],
                                                   df_in_Currentweek[Week2_COLUMN])
        # 그래도 빈 값인 경우 202001 로 설정
        df_in_Currentweek[Week2_COLUMN] = df_in_Currentweek[Week2_COLUMN].fillna("202001")
        # 데이터 타입 변경
        df_in_Currentweek[Week2_COLUMN] = df_in_Currentweek[Week2_COLUMN].astype(int).astype(str)
        # 불필요한 컬럼 삭제
        df_in_Currentweek.drop(columns='fcst_week2_max', axis=1, inplace=True)
        # df_out_RTFHistW와 merge를 위해 컬럼 속성 변경
        df_in_Currentweek[int_col] = df_in_Currentweek[int_col].astype(str)
        df_out_RTFHistW[Time_Week_COLUMN] = df_out_RTFHistW[Time_Week_COLUMN].astype(str)
        # df_out_RTFHistW 와 df_in_Currentweek merge
        df_out_RTFHistW = df_out_RTFHistW.merge(df_in_Currentweek,
                                                on=fcst_merge_col + [Week2_COLUMN, Time_Week_COLUMN, Location_COLUMN],
                                                how='left')
        # RTF_Hist_W_Global_RTF 값 변경 df_in_Currentweek 에 값이 있으면 치환
        df_out_RTFHistW[RTF_Hist_W_Global_RTF] = np.where(df_out_RTFHistW[FCST_RTF_Hist_W_Global_RTF_All].notna(),
                                                          df_out_RTFHistW[FCST_RTF_Hist_W_Global_RTF_All],
                                                          df_out_RTFHistW[RTF_Hist_W_Global_RTF])

        # RTF_Hist_W_RTF 값 변경 df_in_Currentweek 에 값이 있으면 치환
        df_out_RTFHistW[RTF_Hist_W_RTF] = np.where(df_out_RTFHistW[FCST_RTF_Hist_W_RTF_All].notna(),
                                                   df_out_RTFHistW[FCST_RTF_Hist_W_RTF_All],
                                                   df_out_RTFHistW[RTF_Hist_W_RTF])

        # 불필요한 컬럼 삭제
        df_out_RTFHistW.drop(columns=[FCST_RTF_Hist_W_Global_RTF_All, FCST_RTF_Hist_W_RTF_All], axis=1, inplace=True)

        ################################### 2025-10-20 추가 ybest7.part(박병훈)##########################################

        print_df(df_out_RTFHistW, 'df_out_RTFHistW step 09', True)
        step('=====> STEP5  End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################
        step('=====> STEP 6 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_RTFHistW, 'df_out_RTFHistW', True)

        print_df(df_out_RTFHistW, 'df_out_RTFHistW', True)
        row_count, col_count = df_out_RTFHistW.shape
        note(f'=====> Final df_out_SafetyStockW rows : {row_count} , Columns : {col_count}')

        step('=====> STEP 6 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_RTFHistW = pd.DataFrame([], columns=[])

    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
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
