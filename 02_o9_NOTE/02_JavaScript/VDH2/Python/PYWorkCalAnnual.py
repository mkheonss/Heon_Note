"""
* 프로그램명
    - PYWorkCalAnnual.py

* 내용
    - 화면 경로 : MDM > Working Calendar > Annual Plan
    - Location별 Annula Plan 데이타를 생성함.

* 변경이력
    - 2024.07.04 / ys5236.kang / Create

* Input Table
    - df_in_location : Select ([Location].[Location] );
    - df_in_timeweek : Select ( &CWV *[Time].[Week] );

* Output Table
    - df_out_work_cal_annual

* 데이타 초기화
    - input Data 에 대해서 javaScript에서 삭제 후 호출함.

* RUN 스크립트
    - EXEC plugin instance [PY_WorkCalAnnual] for measures {[Working Calendar Annual_Time]}
    using scope ( Version.[Version Name].filter(#.Name = "fbVersion" * [Location].[Location].filter(#.Name == "fbLocation"))
    using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

* Output Query
Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] ) on row,
({Measure.[Work Cal Annual_Lock Flag], Measure.[Work Cal Annual_Week Work Days]}) on column;

"""
########################################################################################################################
# common - start
########################################################################################################################
import decimal
import time

import numpy as np
import pandas as pd
import logging
import datetime
import platform
import tabulate
import traceback
from datetime import datetime
from common import common

# 전역변수 : datetime 변환용
G_STR_DATE_FORMAT = '%Y-%m-%d'  # date format
G_STR_WEEK_FORMAT = '%YW%W'  # Week format
G_STR_MONTH_FORMAT = '%YM%m'  # Month format

# 전역변수 : local 설정 변수
G_PROGRAM_NAME = None
G_IS_Local = None

# round 설정
G_CONTEXT = decimal.getcontext()
G_CONTEXT.rounding = decimal.ROUND_HALF_UP
G_DECIMAL = decimal.Decimal

tabulate.PRESERVE_WHITESPACE = True
tabulate_args = {
    'headers': 'keys',
    # 'tablefmt': 'grid',  # simple is the default format
    'disable_numparse': True,
    'showindex': True,
}
########################################################################################################################
# Local 처리 함수logic start
# read_csv_file
# save_csv_file
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8")

def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

########################################################################################################################
# Start.....
########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PYWorkCalAnnual'
is_local = common.gfn_get_isLocal()
########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
COMMON_SOURCE_VERSION = common.G_SourceVersion

if __name__ == '__main__':
    try:
        if is_local:
            ############################################################################################################
            df_in_location = read_csv_file("../INPUT/df_in_location")
            df_in_timeweek = read_csv_file("../INPUT/df_in_timeweek")
            ############################################################################################################
        if df_in_location.empty:
            raise Exception("Exception: df_in_location is empty")
        if df_in_timeweek.empty:
            raise Exception("Exception: df_in_timeWeek is empty")

        logger.PrintDF(p_df=df_in_location, p_df_name='df_in_location',
                       p_log_level=common.G_log_level.debug(), p_format=1)

        logger.PrintDF(p_df=df_in_timeweek, p_df_name='df_in_timeweek',
                       p_log_level=common.G_log_level.debug(), p_format=1)
        ################################################################################################################
        # DataFrame Column 변수 정의
        ################################################################################################################
        # 컬럼변수 선언
        COL_VERSION_NAME = 'Version.[Version Name]'
        COL_TIME_WEEK = 'Time.[Week]'
        COL_LOCATION = 'Location.[Location]'
        COL_WORK_CAL_ANNUAL_LOCK_FLAG = 'Work Cal Annual_Lock Flag'
        COL_WORK_CAL_ANNUAL_WEEK_WORK_DAYS = 'Work Cal Annual_Week Work Days'

        df_work_cal_annual = pd.merge(df_in_location.assign(temp_key=1), df_in_timeweek.assign(temp_key=1)
                                          , on='temp_key', how='inner').drop('temp_key', axis=1)
        logger.PrintDF(p_df=df_work_cal_annual, p_df_name='df_work_cal_annual', p_log_level=common.G_log_level.debug(), p_format=1)

        # 컬럼 추출 (필요없는 컬럼 삭제)
        df_work_cal_annual = df_work_cal_annual[[COL_VERSION_NAME, COL_TIME_WEEK, COL_LOCATION]]
        # 컬럼 추가 및 디폴트 세팅 및 Default 값 세팅
        df_work_cal_annual[COL_WORK_CAL_ANNUAL_LOCK_FLAG] = False
        df_work_cal_annual[COL_WORK_CAL_ANNUAL_WEEK_WORK_DAYS] = 5.00

        logger.PrintDF(p_df=df_work_cal_annual, p_df_name='df_work_cal_annual(1)',
                       p_log_level=common.G_log_level.debug(), p_format=1)
        # output DataFrame을 copy 함.
        df_out_work_cal_annual = df_work_cal_annual.copy()
        ################################################################################################################
        # Step Local 인 경우 최종 Output 파일을 Local에 저장함.
        ################################################################################################################
        if is_local:
            logger.Step(p_step_no=300, p_step_desc=f'Final Output Table create')
            save_csv_file(df_out_work_cal_annual, '../OUTPUT/df_out_work_cal_annual')

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=f'=====> try Exception : {trace_msg}', p_log_level=LOG_LEVEL.info())
        logger.Error()
        raise Exception(e)
    finally:
        logger.Step(p_step_no=999, p_step_desc=f'plugin Execution End')
        logger.Finish()