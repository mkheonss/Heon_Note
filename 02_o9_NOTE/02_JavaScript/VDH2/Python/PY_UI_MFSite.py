

"""

* 프로그램명
    - PY_UI_MFSite

* 내용

    - 현재는 확정생산계획만 대상(생산라인)

* 변경이력
- 2025.01.07 / ybest7.park (박병훈) / Create
- 2025.02.04 / ybest7.park (박병훈) / 수정
    1) [Location].[Location] 값 "_EX" 가 붙은 Location은 제외부탁드립니다. (Location.[Location$DisplayName]을 적용)
    2) Measure.[MF Site_Country Code] 값 Country Name 값과 동일한 값이 들어가 있는데, Code 명이 들어갈 수 있도록 아래 쿼리 참고 부탁드려요.
    3) 기존 MF Site의 값이 있으면 변경되지 않는 로직 추가
- 2025.09.02 / jaemin.im(임재민)/ 수정
    0) 2단계오픈 및 EW UI개비하면서 NSCM에서 생성하는것으로 DataFlow 변경.
       GSCM에서 신규 생성되는것은 반영해줘야하므로 해당 PY컨셉은 유지하고, 신규 Property들만 추가로 반영하고 기본값 설정
        - KD Flag 추가반영
        - JDM Flag, KD Flag 의 기본값은 "N"

* Input
- in_MfgPlan = pd.read_csv(' .csv')


* Flow Summary



* Input Table
   - df_in_MF_Site = select ([Location].[Location]* [Location].[Country Name] * [Location].[Location Region] *  [Location].[Company]* [Location].[Subsidiary] * [Location].[MF Site Stage] * [Location].[Site Group1] * [Location].[Site Group2] * [Location].[Site Group3]*[Location].[JDM Type]) on row, () on column include memberproperties {[Location].[Country Name], [Country Name$DisplayName]} {[Location].[Company], [Company$DisplayName]} {[Location].[Location], [Country Code]} {[Location].[Location], [Location$DisplayName]};
   - df_in_Version = select ([Version].[Version Name]);
   - df_in_MFSite = Select ([Version].[Version Name] * [Location].[Location] ) on row, ({Measure.[MF Site_Business Type], Measure.[MF Site_Company Code], Measure.[MF Site_Company Desc], Measure.[MF Site_Company Name], Measure.[MF Site_Company Name Override], Measure.[MF Site_Country Code], Measure.[MF Site_Country Name], Measure.[MF Site_Created By], Measure.[MF Site_Creation Time], Measure.[MF Site_GBM], Measure.[MF Site_Group1], Measure.[MF Site_Group2], Measure.[MF Site_Group3], Measure.[MF Site_JDM Flag], Measure.[MF Site_JDM Flag Override], Measure.[MF Site_MF SITE STAGE], Measure.[MF Site_MF SITE STAGE Override], Measure.[MF Site_Region], Measure.[MF Site_Sales Type], Measure.[MF Site_Update Time], Measure.[MF Site_Updated By], Measure.[MF Site_Valid Flag]}) on column;

* 데이터 삭제
    DELETE DATA FOR MODEL [MF Site] where {Version.[Version Name].[CWV_MP]};

* Output Table
    - df_out_MF_Site = Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] ) on row, ({Measure.[MF Site_Business Type], Measure.[MF Site_Company], Measure.[MF Site_Company Code], Measure.[MF Site_Country Code], Measure.[MF Site_Country Name], Measure.[MF Site_Created By], Measure.[MF Site_Creation Time], Measure.[MF Site_GBM], Measure.[MF Site_Group1], Measure.[MF Site_Group2], Measure.[MF Site_Group3], Measure.[MF Site_JDM Flag], Measure.[MF Site_Location], Measure.[MF Site_MF SITE STAGE], Measure.[MF Site_Region], Measure.[MF Site_Sales Type], Measure.[MF Site_Update Time], Measure.[MF Site_Updated By], Measure.[MF Site_Valid Flag]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_MFSite] for measures {[MF Site_Business Type]} using scope (&MPV) using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"),(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;



실행 전 프로시져를 통해 MF Site 삭제  필요

"""


########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as com
from NSCMCommon import VDCommon as vdCommon
import os.path
import time
import datetime
import decimal
import math
import traceback
import tracemalloc
import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re

from dateutil import parser as date_parser
from typing import Union
import warnings
warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_MFSite'
is_local = com.gfn_get_isLocal()
COMMON_SOURCE_VERSION = com.G_SourceVersion
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level
paramOutVersion = 'CWV_MP'
########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8",low_memory=False )


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def note(string, p_log_level=LOG_LEVEL.debug()):
    Logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    Logger.Step(p_step_no=no, p_step_desc=f'{string}')


def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, Logger, is_local, log_path)


def vd_log_end():
    vdCommon.gfn_pyLog_end()


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


def datetime_check_series(date_series):
    # 가능한 형식들을 순서대로 시도
    date_formats = ['%m/%d/%Y %I:%M:%S %p', '%Y/%m/%d %I:%M:%S %p', '%Y-%m-%d %H:%M:%S']

    # 모든 시도가 실패했을 때 NaT로 초기화
    parsed_dates = pd.Series(pd.NaT, index=date_series.index)

    for fmt in date_formats:
        # 형식을 시도하여 변환하고, NaT 값이 없는 경우에 대해서만 변환을 유지
        new_dates = pd.to_datetime(date_series, format=fmt, errors='coerce')
        parsed_dates = parsed_dates.combine_first(new_dates)

    return parsed_dates

# Logger.debug(f'[START] {str_instance}')
# Logger.Start()
# Logger.Step(p_step_no=0, p_step_desc=f'plugin Execution Start')

try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, Logger, com.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if com.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(com.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    step(100, '=====> STEP 1(Start) : Input Date Frame Read')
    # # Value 변수 선언
    # PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = PARAM_OUTVERSION_VALUE

        df_in_MF_Site = read_csv_file('df_in_MF_Site')
        df_in_Version = read_csv_file('df_in_Version')
        df_in_MFSite = read_csv_file('df_in_MFSite')

    #
    # if df_in_MF_Site.empty:
    #     raise Exception("Exception: df_in_MF_Site is empty")

    print_df(df_in_MF_Site, 'df_in_MF_Site',True)
    print_df(df_in_Version, 'df_in_Version',True)
    print_df(df_in_MFSite, 'df_in_MFSite',True)
    step(100, '=====> STEP 1(End) : Check memory usage & runtime')
    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    Version_COLUMN = 'Version.[Version Name]'
    Location_COLUMN = 'Location.[Location]'

    MF_Site_Business_Type = 'MF Site_Business Type'
    MF_Site_Company = 'MF Site_Company'
    MF_Site_Company_Code = 'MF Site_Company Code'
    MF_Site_Country_Name = 'MF Site_Country Name'
    MF_Site_Country_Code = 'MF Site_Country Code'
    MF_Site_Created_By = 'MF Site_Created By'
    MF_Site_Creation_Time = 'MF Site_Creation Time'
    MF_Site_GBM = 'MF Site_GBM'
    MF_Site_Group1 = 'MF Site_Group1'
    MF_Site_Group2 = 'MF Site_Group2'
    MF_Site_Group3 = 'MF Site_Group3'
    MF_Site_JDM_Flag = 'MF Site_JDM Flag'
    MF_Site_KD_Flag  = 'MF Site_KD Flag'    
    MF_Site_Location = 'MF Site_Location'
    #MF_Site_MF_SITE_STAGE = 'MF Site_MF SITE STAGE'
    MF_Site_Region = 'MF Site_Region'
    MF_Site_Sales_Type = 'MF Site_Sales Type'
    MF_Site_Update_Time = 'MF Site_Update Time'
    MF_Site_Updated_By = 'MF Site_Updated By'
    MF_Site_Valid_Flag = 'MF Site_Valid Flag'
    


    step(200, '=====> STEP 2(End) : Check memory usage & runtime')
    # 입력 변수 확인용 로그
    # Logger.Note(p_note=f'paramOutVersion : {paramOutVersion}', p_log_level=Logger_level.debug())

    ################################################################################################################
    # Step 1 (1) 날짜 데이터 설정을 위한 전처리 → 현재 Sever Error 발생
    ################################################################################################################
    step(300, '=====> STEP 3(start) : input data machining')

    df_out_MF_Site = df_in_MF_Site.copy()
    Version = df_in_Version.iloc[0,0]
    df_out_MF_Site[Version_COLUMN] = Version
    df_out_MF_Site[Location_COLUMN] = df_out_MF_Site['Location.[Location$DisplayName]']
    df_out_MF_Site[MF_Site_Location] = df_out_MF_Site[Location_COLUMN]
    df_out_MF_Site[MF_Site_Country_Code] = df_out_MF_Site['Location.[Country Code]']
    df_out_MF_Site[MF_Site_Country_Name] = df_out_MF_Site['Location.[Country Name]']
    df_out_MF_Site[MF_Site_Region] = df_out_MF_Site['Location.[Location Region]']
    df_out_MF_Site[MF_Site_Business_Type] = "PLANT"
    df_out_MF_Site[MF_Site_Sales_Type] = "PLANT"
    df_out_MF_Site[MF_Site_Company_Code] = df_out_MF_Site['Location.[Company]']
    df_out_MF_Site[MF_Site_Company] = df_out_MF_Site['Location.[Company$DisplayName]']
    #250903LJM JDM, KD Flag는 신규값인경우 N처리
    #df_out_MF_Site[MF_Site_JDM_Flag] = df_out_MF_Site['Location.[JDM Type]']
    df_out_MF_Site[MF_Site_JDM_Flag] = "N"
    df_out_MF_Site[MF_Site_KD_Flag]  = "N"
    df_out_MF_Site[MF_Site_GBM] = "VD"
    #df_out_MF_Site[MF_Site_MF_SITE_STAGE] = df_out_MF_Site['Location.[MF Site Stage]']
    df_out_MF_Site[MF_Site_Valid_Flag] = "Y"
    df_out_MF_Site[MF_Site_Group1] = df_out_MF_Site['Location.[Site Group1]']
    df_out_MF_Site[MF_Site_Group2] = df_out_MF_Site['Location.[Site Group2]']
    df_out_MF_Site[MF_Site_Group3] = df_out_MF_Site['Location.[Site Group3]']
    df_out_MF_Site[MF_Site_Created_By] = 'PY_UI_MF Site'
    df_out_MF_Site[MF_Site_Updated_By] = ''
    df_out_MF_Site[MF_Site_Creation_Time] = datetime.datetime.now().strftime('%Y-%m-%d')
    df_out_MF_Site[MF_Site_Update_Time] = ''
    
    df_out_MF_Site[MF_Site_Update_Time] = ''
    df_out_MF_Site[MF_Site_Update_Time] = ''    

    print_df(df_out_MF_Site, 'df_out_MF_Site step =======>  300 - 1')

    df_out_MF_Site[MF_Site_Company] = np.where(df_out_MF_Site[MF_Site_Company].str.contains('C610_EX'), "C100",
                                               df_out_MF_Site[MF_Site_Company])
    df_out_MF_Site[MF_Site_Company_Code] = np.where(df_out_MF_Site[MF_Site_Company_Code].str.contains('C610_EX'), "C100",
                                               df_out_MF_Site[MF_Site_Company_Code])
    df_out_MF_Site[MF_Site_Group2] = df_out_MF_Site[MF_Site_Group2].str.split('_').apply(lambda x: '_'.join(x[1:]))
    df_out_MF_Site[MF_Site_Group3] = df_out_MF_Site[MF_Site_Group3].str.split('_').apply(lambda x: '_'.join(x[-1:]))
    # df_out_MF_Site = df_out_MF_Site[~df_out_MF_Site[Location_COLUMN].str.contains('_EX',na=False)]

    print_df(df_out_MF_Site, 'df_out_MF_Site step =======>  300 - 2')

    df_out_MF_Site = df_out_MF_Site[
        [Version_COLUMN, Location_COLUMN, MF_Site_Business_Type, MF_Site_Company, MF_Site_Company_Code,
         MF_Site_Country_Code, MF_Site_Country_Name, MF_Site_Created_By, MF_Site_Creation_Time, MF_Site_GBM,
         MF_Site_Group1, MF_Site_Group2, MF_Site_Group3, MF_Site_JDM_Flag, MF_Site_KD_Flag, MF_Site_Location, 
         MF_Site_Region, MF_Site_Sales_Type, MF_Site_Update_Time, MF_Site_Updated_By, MF_Site_Valid_Flag]]

    print_df(df_out_MF_Site, 'df_out_MF_Site step =======>  300 - 3')

    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 2 df_out_MF_Site out put 설정
    ###############################################################################################################
    step(400, '=====> STEP 4(start) : output data machining')

    df_out_MF_Site = df_out_MF_Site[
        [Version_COLUMN, Location_COLUMN, MF_Site_Business_Type, MF_Site_Company, MF_Site_Company_Code,
         MF_Site_Country_Code, MF_Site_Country_Name, MF_Site_Created_By, MF_Site_Creation_Time, MF_Site_GBM,
         MF_Site_Group1, MF_Site_Group2, MF_Site_Group3, MF_Site_JDM_Flag, MF_Site_KD_Flag, MF_Site_Location, 
         MF_Site_Region, MF_Site_Sales_Type, MF_Site_Update_Time, MF_Site_Updated_By, MF_Site_Valid_Flag]]

    print_df(df_out_MF_Site, 'df_out_MF_Site step =======> 400 - 1')

    # df_in_MFSite에 없는 값만 필터링
    grain_col = [Version_COLUMN,Location_COLUMN]
    df_in_MFSite_index = df_in_MFSite[grain_col].index
    df_out_MF_Site_index = df_out_MF_Site[grain_col].index

    df_out_MF_Site = df_out_MF_Site[~df_out_MF_Site_index.isin(df_in_MFSite_index)]

    print_df(df_out_MF_Site, 'df_out_MF_Site step =======> 400 - 2' )

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # Step 3. (1) 최종 Out_Put Save
    ################################################################################################################
    step(500, '=====> STEP 5(start) : Final output data frame')


    row_count, col_count = df_out_MF_Site.shape
    Logger.Note(p_note=f'df_out_MultiSite rows : {row_count} , Columns : {col_count}',
                p_log_level=LOG_LEVEL.info())

    if is_local:
        Logger.Step(p_step_no=500, p_step_desc=f'Final Output Tabel create')
        print_df(df_out_MF_Site, 'df_out_MF_Site', True)

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(f'=====> try Exception: {trace_msg}', LOG_LEVEL.info())
    Logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_MF_Site = pd.DataFrame([], columns=[])

else:
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {round(current / 10 ** 6, 2)}MB, '
         f'Peak was {round(peak / 10 ** 6, 2)}MB')
    step(500, '===================== plugin Execution End =====================')

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

    Logger.Finish()
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')
    Logger.Step(p_step_desc=f'plugin Execution End')