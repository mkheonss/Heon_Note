"""

* 프로그램명
    - PY_UI_Target_Ecp

* 내용
     - Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Product Group] * [Sales Domain].[AP2]),
      where [Item].[Item Stage] = 'SKU' 값을

* 변경이력
- 2024.10.2 / ybest7.park (박병훈) / Create

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_TragetEcpDim = Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Product Group].filter(#.relatedmembers([Item Stage]).element(0).Name == "SKU") * [Sales Domain].[AP2].filter(#.Name != "ALL"));
   - df_in_TargetEcp = Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Product Group] * [Sales Domain].[AP2] ) on row, ({Measure.[Target Ecp Set_Build Ahead Must], Measure.[Target Ecp Set_EOH], Measure.[Target Ecp Set_SS Must], Measure.[Target Ecp Set_WOS]}) on column;

* Output Table
    - df_out_TargetEcp = Select ([Version].[Version Name].[CurrentWorkingView] * [Item].[Product Group] * [Sales Domain].[AP2] ) on row, ({Measure.[Target Ecp Set_Build Ahead Must], Measure.[Target Ecp Set_EOH], Measure.[Target Ecp Set_SS Must], Measure.[Target Ecp Set_WOS]}) on column;


* 데이터 삭제
    DELETE DATA FOR MODEL [Target Ecp Set] where {Version.[Version Name].[CurrentWorkingView]};


* 테스트 스크립트
    EXEC plugin instance [Target Ecp Set] for measures {[Target Ecp Set_Build Ahead Must]} using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView"})) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;


* 데이터 확인


"""

from NSCMCommon import NSCMCommon as com
import os.path
import time
import datetime
import decimal
import math
import traceback

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
str_instance = 'PY_UI_Target_Ecp'
is_local = com.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
Logger = com.G_Logger(p_py_name=str_instance)
com.gfn_set_local_logfile()
LOG_LEVEL = com.G_log_level

########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8")


def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)


# if __name__ == '__main__':
Logger.debug(f'[START] {str_instance}')
Logger.Start()
Logger.Step(p_step_no=0, p_step_desc=f'plugin Execution Start')

try:
    ################################################################################################################
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    # Value 변수 선언
    # PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = 'CurrentWorkingView'

        df_in_TargetEcpDim = read_csv_file("df_in_TargetEcpDim")
        df_in_TargetEcp = read_csv_file('df_in_TargetEcp')


    if df_in_TargetEcpDim.empty:
        raise Exception("Exception: df_in_TragetEcpDim is empty")

    # if df_in_TargetEcp.empty:
    #     raise Exception("Exception: df_in_TragetEcp is empty")


    # # 입력 변수 확인
    # if paramOutVersion is None or paramOutVersion.strip() == '':
    #     paramOutVersion = PARAM_OUTVERSION_VALUE

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수설정
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    ITEM_PRODUCT_GROUP_COLUMN = 'Item.[Product Group]'
    SALES_DOMAIN_AP2_COLUMN = 'Sales Domain.[AP2]'

    Target_Ecp_Set_Build_Ahead_Must = 'Target Ecp Set_Build Ahead Must'
    Target_Ecp_Set_EOH = 'Target Ecp Set_EOH'
    Target_Ecp_Set_SS_Must = 'Target Ecp Set_SS Must'
    Target_Ecp_Set_WOS = 'Target Ecp Set_WOS'

    Logger.Step(p_step_no=100, p_step_desc=f'in Table Log')
    # 입력 변수 확인용 로그
    # Logger.Note(p_note=f'paramOutVersion : {paramOutVersion}',p_log_level=LOG_LEVEL.debug())
    Logger.PrintDF(p_df=df_in_TargetEcpDim, p_df_name='df_in_TragetEcpDim',
                   p_log_level=LOG_LEVEL.debug(), p_format=1)
    Logger.Step(p_step_no=110, p_step_desc=f'df_in_TragetEcpDim Table Log')
    Logger.PrintDF(p_df=df_in_TargetEcp, p_df_name='df_in_TragetEcp',
                   p_log_level=LOG_LEVEL.debug(), p_format=1)
    Logger.Step(p_step_no=120, p_step_desc=f'df_in_TragetEcp Table Log')


    ################################################################################################################
    # Step 1. (1) df_in_TactTime 중복 삭제 및 필터링 (Location_Column, Item_Column,Line_Column)
    ################################################################################################################
    df_out_TargetEcp =df_in_TargetEcpDim[ ~df_in_TargetEcpDim.set_index([VERSION_NAME_COLUMN,ITEM_PRODUCT_GROUP_COLUMN,
                                                     SALES_DOMAIN_AP2_COLUMN]).index.isin(
        df_in_TargetEcp.set_index([VERSION_NAME_COLUMN,ITEM_PRODUCT_GROUP_COLUMN,SALES_DOMAIN_AP2_COLUMN]).index
    )]

    df_out_TargetEcp = pd.concat([df_out_TargetEcp, df_in_TargetEcp]).reset_index(drop=True)
    df_out_TargetEcp[Target_Ecp_Set_Build_Ahead_Must] = np.where(
        df_out_TargetEcp[Target_Ecp_Set_Build_Ahead_Must].isna(),
        'N', df_out_TargetEcp[Target_Ecp_Set_Build_Ahead_Must])
    df_out_TargetEcp[Target_Ecp_Set_EOH] = np.where(
        df_out_TargetEcp[Target_Ecp_Set_EOH].isna(),'100%', df_out_TargetEcp[Target_Ecp_Set_Build_Ahead_Must])
    df_out_TargetEcp[Target_Ecp_Set_SS_Must] = np.where(
        df_out_TargetEcp[Target_Ecp_Set_SS_Must].isna(),'N', df_out_TargetEcp[Target_Ecp_Set_SS_Must])
    df_out_TargetEcp[Target_Ecp_Set_WOS] = np.where(
        df_out_TargetEcp[Target_Ecp_Set_WOS].isna(),'N', df_out_TargetEcp[Target_Ecp_Set_Build_Ahead_Must])

    Logger.PrintDF(p_df=df_out_TargetEcp, p_df_name='df_out_TargetEcp Step 1',
                   p_log_level=LOG_LEVEL.debug(), p_format=1)
    Logger.Step(p_step_no=200, p_step_desc=f'Final Output Tabel create ')

    ################################################################################################################
    # Step 2. (1) 최종 Out_Put Save
    ################################################################################################################

    if is_local:
        Logger.Step(p_step_no=300, p_step_desc=f'Final Output Tabel create ')
        save_csv_file(df_out_TargetEcp, 'df_out_TargetEcp')

    row_count, col_count = df_out_TargetEcp.shape
    Logger.Note(p_note=f'df_out_TargetEcp rows : {row_count} , Columns : {col_count}',
                      p_log_level=LOG_LEVEL.debug())

except Exception as e:
    trace_msg = traceback.format_exc()
    Logger.Note(p_note=trace_msg,p_log_level=LOG_LEVEL.info())
    Logger.Error()
    raise Exception(e)

else:
    Logger.Step(p_step_no=400, p_step_desc=f'===================== plugin Execution End =====================')

finally:
    Logger.Step(p_step_no=500, p_step_desc=f'plugin Execution End')
    Logger.Finish()