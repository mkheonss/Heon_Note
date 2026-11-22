"""
* 프로그램명
    - PY_UI_LoadingDirOrderMgmtValidCal_REG.py
* 내용
    - DIr Order Mgmt UI(Upload)화면에서 Validation chk 버튼을 클릭했을때 실행되는 모듈
* 변경이력
    - 2025.05.14 / YUN TAE UN / Create

* Flow Summary
    Step1.
* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
* Input Tables
    - in_Loading_Dir_Order_Mgmt
        ㄴ o9 upload용
        Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Sales Domain].[Ship To] * [Item].[Item] * [Time].[Week] * [Seq].[Seq]) on row,({Measure.[Loading Dir Order Mgmt_SO Item], Measure.[Loading Dir Order Mgmt_Adj Prod Week], Measure.[Loading Dir Order Mgmt_Ship To], Measure.[Loading Dir Order Mgmt_Ship To Name], Measure.[Loading Dir Order Mgmt_Loading Type], Measure.[Loading Dir Order Mgmt_Cntr Type], Measure.[Loading Dir Order Mgmt_Origin Qty], Measure.[Loading Dir Order Mgmt_Chk Qty]}) on column where{Measure.[Loading Dir Order Mgmt_Chk Flag] == "Y"};
        ㄴ 개발 직관용
        Select (
            [Version].[Version Name].CWV_MP
            * [Sub Location].[Sub Location]
            * [Location].[Location]
            * [Sales Domain].[Ship To]
            * [Item].[Item]
            * [Time].[Week]
            * [Seq].[Seq]
        ) on row
        ,
        ({
            Measure.[Loading Dir Order Mgmt_SO Item]
            , Measure.[Loading Dir Order Mgmt_Adj Prod Week]
            , Measure.[Loading Dir Order Mgmt_Ship To]
            , Measure.[Loading Dir Order Mgmt_Ship To Name]
            , Measure.[Loading Dir Order Mgmt_Loading Type]
            , Measure.[Loading Dir Order Mgmt_Cntr Type]
            , Measure.[Loading Dir Order Mgmt_Origin Qty]
            , Measure.[Loading Dir Order Mgmt_Chk Qty]
        }) on column
        where{Measure.[Loading Dir Order Mgmt_Chk Flag] == "Y"};

    ########## chk를 위한 input ########################################################################################
    - in_Loading_Master_Ship_To
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Sub Location].[Sub Location]  * [Location].[Location] * [Sales Domain].[Ship To] * [Item].[Item]  * [Container].[ContainerID]  * [Loading Type].[Loading Type]  * [Seq].[Seq] ) on row, ({Measure.[Loading Master Ship To_Ship To], Measure.[Loading Master Ship To_JIG], Measure.[Loading Master Ship To_Line], Measure.[Loading Master Ship To_Max Load Qty], Measure.[Loading Master Ship To_Min Qty], Measure.[Loading Master Ship To_Multiple], Measure.[Loading Master Ship To_Depth], Measure.[Loading Master Ship To_Height], Measure.[Loading Master Ship To_Width], Measure.[Loading Master Ship To_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name]
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Sales Domain].[Ship To]
                * [Item].[Item]
                * [Container].[ContainerID]
                * [Loading Type].[Loading Type]
                * [Seq].[Seq]
            ) on row
            , ({
                Measure.[Loading Master Ship To_Ship To]
                , Measure.[Loading Master Ship To_JIG]
                , Measure.[Loading Master Ship To_Line]
                , Measure.[Loading Master Ship To_Max Load Qty]
                , Measure.[Loading Master Ship To_Min Qty]
                , Measure.[Loading Master Ship To_Multiple]
                , Measure.[Loading Master Ship To_Depth]
                , Measure.[Loading Master Ship To_Height]
                , Measure.[Loading Master Ship To_Width]
                , Measure.[Loading Master Ship To_Valid Flag]
            }) on column;
    - in_Loading_Master_Account
        ㄴ o9 upload용
             Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Item].[Item] * [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To]) on row, ({Measure.[Loading Master Account_JIG], Measure.[Loading Master Account_Line], Measure.[Loading Master Account_Max Load Qty], Measure.[Loading Master Account_Min Qty], Measure.[Loading Master Account_Multiple], Measure.[Loading Master Account_Depth], Measure.[Loading Master Account_Height], Measure.[Loading Master Account_Width], Measure.[Loading Master Account_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name].CWV_MP
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Sales Domain].[Ship To]
                * [Item].[Item]
                * [Container].[ContainerID]
                * [Loading Type].[Loading Type]
            ) on row
            , ({
                Measure.[Loading Master Account_JIG]
                , Measure.[Loading Master Account_Line]
                , Measure.[Loading Master Account_Max Load Qty]
                , Measure.[Loading Master Account_Min Qty]
                , Measure.[Loading Master Account_Multiple]
                , Measure.[Loading Master Account_Depth]
                , Measure.[Loading Master Account_Height]
                , Measure.[Loading Master Account_Width]
                , Measure.[Loading Master Account_Valid Flag]
            }) on column;
    - in_Loading_Master_To_Site
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Item].[Item] * [Location].[Location] * [Container].[ContainerID] ) on row, ({Measure.[Loading Master To Site_JIG], Measure.[Loading Master To Site_Line], Measure.[Loading Master To Site_Max Load Qty], Measure.[Loading Master To Site_Min Qty], Measure.[Loading Master To Site_Multiple], Measure.[Loading Master To Site_Depth], Measure.[Loading Master To Site_Height], Measure.[Loading Master To Site_Width], Measure.[Loading Master To Site_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name].CWV_MP
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Item].[Item]
                * [Container].[ContainerID]
                * [Loading Type].[Loading Type]
            ) on row
            , ({
                Measure.[Loading Master To Site_JIG]
                , Measure.[Loading Master To Site_Line]
                , Measure.[Loading Master To Site_Max Load Qty]
                , Measure.[Loading Master To Site_Min Qty]
                , Measure.[Loading Master To Site_Multiple]
                , Measure.[Loading Master To Site_Depth]
                , Measure.[Loading Master To Site_Height]
                , Measure.[Loading Master To Site_Width]
                , Measure.[Loading Master To Site_Valid Flag]
            }) on column;
    - in_Loading_Master_From_Site
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Item].[Item] * [Container].[ContainerID] ) on row, ({Measure.[Loading Master From Site_JIG], Measure.[Loading Master From Site_Line], Measure.[Loading Master From Site_Max Load Qty], Measure.[Loading Master From Site_Min Qty], Measure.[Loading Master From Site_Multiple], Measure.[Loading Master From Site_Depth], Measure.[Loading Master From Site_Height], Measure.[Loading Master From Site_Width], Measure.[Loading Master From Site_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name].CWV_MP
                * [Sub Location].[Sub Location]
                * [Item].[Item]
                * [Container].[ContainerID]
                * [Loading Type].[Loading Type]
            ) on row
            , ({
                Measure.[Loading Master From Site_JIG]
                , Measure.[Loading Master From Site_Line]
                , Measure.[Loading Master From Site_Max Load Qty]
                , Measure.[Loading Master From Site_Min Qty]
                , Measure.[Loading Master From Site_Multiple]
                , Measure.[Loading Master From Site_Depth]
                , Measure.[Loading Master From Site_Height]
                , Measure.[Loading Master From Site_Width]
                , Measure.[Loading Master From Site_Valid Flag]
            }) on column;
    - in_Loading_Method_Ship_To
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Sales Domain].[Ship To] * [Container].[ContainerID] * [Loading Type].[Loading Type] * [Seq].[Seq] ) on row, ({Measure.[Loading Method Ship To_Ship To], Measure.[Loading Method Ship To_1st Mix], Measure.[Loading Method Ship To_2nd Mix], Measure.[Loading Method Ship To_3rd Mix], Measure.[Loading Method Ship To_Default], Measure.[Loading Method Ship To_JIG Line], Measure.[Loading Method Ship To_Mix Cut Add], Measure.[Loading Method Ship To_Mix FR Type], Measure.[Loading Method Ship To_Mix Max FR], Measure.[Loading Method Ship To_Mix Min FR], Measure.[Loading Method Ship To_SKU Per Cntr], Measure.[Loading Method Ship To_Single Cut Add], Measure.[Loading Method Ship To_Single FR Type], Measure.[Loading Method Ship To_Single Max FR], Measure.[Loading Method Ship To_Single Min FR], Measure.[Loading Method Ship To_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name]
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Sales Domain].[Ship To]
                * [Container].[ContainerID]
                * [Loading Type].[Loading Type]
                * [Seq].[Seq]
            ) on row
                , ({
                    Measure.[Loading Method Ship To_Ship To]
                    , Measure.[Loading Method Ship To_1st Mix]
                    , Measure.[Loading Method Ship To_2nd Mix]
                    , Measure.[Loading Method Ship To_3rd Mix]
                    , Measure.[Loading Method Ship To_Default]
                    , Measure.[Loading Method Ship To_JIG Line]
                    , Measure.[Loading Method Ship To_Mix Cut Add]
                    , Measure.[Loading Method Ship To_Mix FR Type]
                    , Measure.[Loading Method Ship To_Mix Max FR]
                    , Measure.[Loading Method Ship To_Mix Min FR]
                    , Measure.[Loading Method Ship To_SKU Per Cntr]
                    , Measure.[Loading Method Ship To_Single Cut Add]
                    , Measure.[Loading Method Ship To_Single FR Type]
                    , Measure.[Loading Method Ship To_Single Max FR]
                    , Measure.[Loading Method Ship To_Single Min FR]
                    , Measure.[Loading Method Ship To_Valid Flag]
                }) on column;
    - in_Loading_Method_Account
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To] ) on row, ({Measure.[Loading Method Account_1st Mix], Measure.[Loading Method Account_2nd Mix], Measure.[Loading Method Account_3rd Mix], Measure.[Loading Method Account_Default], Measure.[Loading Method Account_JIG Line], Measure.[Loading Method Account_Mix Cut Add], Measure.[Loading Method Account_Mix FR Type], Measure.[Loading Method Account_Mix Max FR], Measure.[Loading Method Account_Mix Min FR], Measure.[Loading Method Account_SKU Per Cntr], Measure.[Loading Method Account_Single Cut Add], Measure.[Loading Method Account_Single FR Type], Measure.[Loading Method Account_Single Max FR], Measure.[Loading Method Account_Single Min FR], Measure.[Loading Method Account_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name].CWV_MP
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Sales Domain].[Ship To]
                * [Container].[ContainerID]
                * [Loading Type].[Loading Type]
            ) on row
            , ({
                Measure.[Loading Method Account_1st Mix]
                , Measure.[Loading Method Account_2nd Mix]
                , Measure.[Loading Method Account_3rd Mix]
                , Measure.[Loading Method Account_Default]
                , Measure.[Loading Method Account_JIG Line]
                , Measure.[Loading Method Account_Mix Cut Add]
                , Measure.[Loading Method Account_Mix FR Type]
                , Measure.[Loading Method Account_Mix Max FR]
                , Measure.[Loading Method Account_Mix Min FR]
                , Measure.[Loading Method Account_SKU Per Cntr]
                , Measure.[Loading Method Account_Single Cut Add]
                , Measure.[Loading Method Account_Single FR Type]
                , Measure.[Loading Method Account_Single Max FR]
                , Measure.[Loading Method Account_Single Min FR]
                , Measure.[Loading Method Account_Valid Flag]
            }) on column;
    - in_Loading_Method_To_Site
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] ) on row, ({Measure.[Loading Method To Site_1st Mix], Measure.[Loading Method To Site_2nd Mix], Measure.[Loading Method To Site_3rd Mix], Measure.[Loading Method To Site_Default], Measure.[Loading Method To Site_JIG Line], Measure.[Loading Method To Site_Mix Cut Add], Measure.[Loading Method To Site_Mix FR Type], Measure.[Loading Method To Site_Mix Max FR], Measure.[Loading Method To Site_Mix Min FR], Measure.[Loading Method To Site_SKU Per Cntr], Measure.[Loading Method To Site_Single Cut Add], Measure.[Loading Method To Site_Single FR Type], Measure.[Loading Method To Site_Single Max FR], Measure.[Loading Method To Site_Single Min FR], Measure.[Loading Method To Site_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name].CWV_MP
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Container].[ContainerID]
                * [Loading Type].[Loading Type]
            ) on row
            , ({
                Measure.[Loading Method To Site_1st Mix]
                , Measure.[Loading Method To Site_2nd Mix]
                , Measure.[Loading Method To Site_3rd Mix]
                , Measure.[Loading Method To Site_Default]
                , Measure.[Loading Method To Site_JIG Line]
                , Measure.[Loading Method To Site_Mix Cut Add]
                , Measure.[Loading Method To Site_Mix FR Type]
                , Measure.[Loading Method To Site_Mix Max FR]
                , Measure.[Loading Method To Site_Mix Min FR]
                , Measure.[Loading Method To Site_SKU Per Cntr]
                , Measure.[Loading Method To Site_Single Cut Add]
                , Measure.[Loading Method To Site_Single FR Type]
                , Measure.[Loading Method To Site_Single Max FR]
                , Measure.[Loading Method To Site_Single Min FR]
                , Measure.[Loading Method To Site_Valid Flag]
            }) on column;
    - in_Loading_Method_From_Site
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Shipment Type].[Shipment Type] * [Sub Location].[Sub Location] * [Container].[ContainerID] ) on row, ({Measure.[Loading Method From Site_1st Mix], Measure.[Loading Method From Site_2nd Mix], Measure.[Loading Method From Site_3rd Mix], Measure.[Loading Method From Site_Default], Measure.[Loading Method From Site_JIG Line], Measure.[Loading Method From Site_Mix Cut Add], Measure.[Loading Method From Site_Mix FR Type], Measure.[Loading Method From Site_Mix Max FR], Measure.[Loading Method From Site_Mix Min FR], Measure.[Loading Method From Site_SKU Per Cntr], Measure.[Loading Method From Site_Single Cut Add], Measure.[Loading Method From Site_Single FR Type], Measure.[Loading Method From Site_Single Max FR], Measure.[Loading Method From Site_Single Min FR], Measure.[Loading Method From Site_Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name]
                * [Loading Type].[Loading Type]
                * [Shipment Type].[Shipment Type]
                * [Sub Location].[Sub Location]
                * [Container].[ContainerID]
            ) on row
            , ({
                Measure.[Loading Method From Site_1st Mix]
                , Measure.[Loading Method From Site_2nd Mix]
                , Measure.[Loading Method From Site_3rd Mix]
                , Measure.[Loading Method From Site_Default]
                , Measure.[Loading Method From Site_JIG Line]
                , Measure.[Loading Method From Site_Mix Cut Add]
                , Measure.[Loading Method From Site_Mix FR Type]
                , Measure.[Loading Method From Site_Mix Max FR]
                , Measure.[Loading Method From Site_Mix Min FR]
                , Measure.[Loading Method From Site_SKU Per Cntr]
                , Measure.[Loading Method From Site_Single Cut Add]
                , Measure.[Loading Method From Site_Single FR Type]
                , Measure.[Loading Method From Site_Single Max FR]
                , Measure.[Loading Method From Site_Single Min FR]
                , Measure.[Loading Method From Site_Valid Flag]
            }) on column;
    - in_profit_grade
        ㄴ o9 upload용
            Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] ) on row, ({Measure.[Loading Profit Grade_Profit Grade], Measure.[Loading Profit Grade_Profit Grade Priority], Measure.[Loading Profit Grade_Profit Grade Valid Flag]}) on column;
        ㄴ 개발 직관용
            Select (
                [Version].[Version Name].CWV_MP
                * [Sub Location].[Sub Location]
                * [Item].[Item]
            ) on row
            , ({
                Measure.[Loading Profit Grade_Profit Grade]
                , Measure.[Loading Profit Grade_Profit Grade Priority]
                , Measure.[Loading Profit Grade_Profit Grade Valid Flag]
            }) on column;
    - in_Item_ULD
    ㄴ o9 upload용
        Select ([Version].[Version Name] * [Item].[Item] ) on row, ({Measure.[Item ULD_Depth], Measure.[Item ULD_Height], Measure.[Item ULD_Width]}) on column;
    ㄴ 개발 직관용
        Select (
            [Version].[Version Name].CWV_MP
            * [Item].[Item]
        ) on row,
        ({
            Measure.[Item ULD_Depth]
            , Measure.[Item ULD_Height]
            , Measure.[Item ULD_Width]

        }) on column;
    - in_ship_to_mix_group
    ㄴ o9 upload용
        Select ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Location].[Location] * [Item].[Item] * [Seq].[Seq]) on row,({Measure.[Loading Method Mix Ship To_Ship To], Measure.[Loading Method Mix Ship To_Item Mix Group], Measure.[Loading Method Mix Ship To_Cntr Type], Measure.[Loading Method Mix Ship To_Loading Type], Measure.[Loading Method Mix Ship To Detail_Valid Flag]}) on column;
    ㄴ 개발 직관용
        Select (
              [Version].[Version Name].[CWV_MP]
            * [Sub Location].[Sub Location]
            * [Location].[Location]
            * [Item].[Item]
            * [Seq].[Seq]
        ) on row,
        ({
            Measure.[Loading Method Mix Ship To_Ship To]
            , Measure.[Loading Method Mix Ship To_Item Mix Group]
            , Measure.[Loading Method Mix Ship To_Cntr Type]
            , Measure.[Loading Method Mix Ship To_Loading Type]
            , Measure.[Loading Method Mix Ship To Detail_Valid Flag]
        }) on column;
    - in_to_site_mix_group
        ㄴ o9 upload용
        Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Item].[Item] * [Seq].[Seq]) on row,({Measure.[Loading Method Mix To Site_Cntr Type], Measure.[Loading Method Mix To Site_Loading Type], Measure.[Loading Method Mix To Site_Item Mix Group], Measure.[Loading Method Mix To Site Detail_Valid Flag]}) on column;
        ㄴ 개발 직관용
        Select (
                  [Version].[Version Name].[CWV_MP]
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Item].[Item]
                * [Seq].[Seq]
            ) on row,
            ({
                  Measure.[Loading Method Mix To Site_Cntr Type]
                , Measure.[Loading Method Mix To Site_Loading Type]
                , Measure.[Loading Method Mix To Site_Item Mix Group]
                , Measure.[Loading Method Mix To Site Detail_Valid Flag]
            }) on column;
    - in_container_info
    Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Container].[ContainerID] ) on row,  ({Measure.[Loading Cntr Master_Created By], Measure.[Loading Cntr Master_Height], Measure.[Loading Cntr Master_Length], Measure.[Loading Cntr Master_Remark], Measure.[Loading Cntr Master_Valid Flag], Measure.[Loading Cntr Master_Width]}) on column;

* Output Tables
    - 1. out_Loading_Dir_Order_Mgmt_Valid
        Select (
            [Version].[Version Name].CWV_MP
            * [Sub Location].[Sub Location]
            * [Location].[Location]
            * [Sales Domain].[Ship To]
            * [Item].[Item]
            * [Time].[Week]
            * [Seq].[Seq]
        ) on row,
        ({
            Measure.[Loading Dir Order Mgmt_Loading Master Match]
            , Measure.[Loading Dir Order Mgmt_Loading Master Match Chk]
            , Measure.[Loading Dir Order Mgmt_Loading Method Match]
            , Measure.[Loading Dir Order Mgmt_Loading Method Match Chk]
            , Measure.[Loading Dir Order Mgmt_Valid Fail Reason]
        }) on column;
    - 2. out_Loading_Dir_Order_Cal_Master
        Select (
            [Version].[Version Name].CWV_MP
            * [Sub Location].[Sub Location]
            * [Location].[Location]
            * [Sales Domain].[Ship To]
            * [Item].[Item]
            * [Time].[Week]
            * [Seq].[Seq]
        ) on row,
        ({
            Measure.[Loading Dir Order Cal Master_Min Qty]
            , Measure.[Loading Dir Order Cal Master_Multiple]
            , Measure.[Loading Dir Order Cal Master_Max Load Qty]
            , Measure.[Loading Dir Order Cal Master_JIG Line]
            , Measure.[Loading Dir Order Cal Master_Single FR Type]
            , Measure.[Loading Dir Order Cal Master_Single Min FR]
            , Measure.[Loading Dir Order Cal Master_Single Max FR]
            , Measure.[Loading Dir Order Cal Master_Single Cut Add]
            , Measure.[Loading Dir Order Cal Master_Mix FR Type]
            , Measure.[Loading Dir Order Cal Master_Mix Min FR]
            , Measure.[Loading Dir Order Cal Master_Mix Max FR]
            , Measure.[Loading Dir Order Cal Master_Mix Cut Add]
            , Measure.[Loading Dir Order Cal Master_SKU Per Cntr]
            , Measure.[Loading Dir Order Cal Master_1st Mix]
            , Measure.[Loading Dir Order Cal Master_2nd Mix]
            , Measure.[Loading Dir Order Cal Master_3rd Mix]
            , Measure.[Loading Dir Order Cal Master_Item Height]
            , Measure.[Loading Dir Order Cal Master_Item Width]
            , Measure.[Loading Dir Order Cal Master_Item Depth]
            , Measure.[Loading Dir Order Cal Master_Profit Grade]
            , Measure.[Loading Dir Order Cal Master_Profit Grade Priority]
        }) on column;
    3. out_Item_Unit_Load
    select (
        Version.[Version Name].CWV_MP
        * [Sub Location].[Sub Location]
        * Item.[Item]
        * Container.[ContainerID]
        * [Loading Type].[Loading Type]
    ) on row
    , ({
        Measure.[Loading Master From Site_Created By]
        , Measure.[Loading Master From Site_Creation Time]
        , Measure.[Loading Master From Site_Valid Flag]
    }) on column;

* Execution :
1. 기존 메저 데이터 삭제(nullify)
    1-1.
    Scope: (
        [Version].[Version Name].[CWV_MP]
    );
        Measure.[Loading Dir Order Mgmt_Loading Master Match] = null;
        Measure.[Loading Dir Order Mgmt_Loading Master Match Chk] = null;
        Measure.[Loading Dir Order Mgmt_Loading Method Match] = null;
        Measure.[Loading Dir Order Mgmt_Loading Method Match Chk] = null;
        Measure.[Loading Dir Order Mgmt_Valid Fail Reason] = null;
        Measure.[Loading Dir Order Cal Master_Min Qty] = null;
        Measure.[Loading Dir Order Cal Master_Multiple] = null;
        Measure.[Loading Dir Order Cal Master_Max Load Qty] = null;
        Measure.[Loading Dir Order Cal Master_JIG Line] = null;
        Measure.[Loading Dir Order Cal Master_Single FR Type] = null;
        Measure.[Loading Dir Order Cal Master_Single Min FR] = null;
        Measure.[Loading Dir Order Cal Master_Single Max FR] = null;
        Measure.[Loading Dir Order Cal Master_Single Cut Add] = null;
        Measure.[Loading Dir Order Cal Master_Mix FR Type] = null;
        Measure.[Loading Dir Order Cal Master_Mix Min FR] = null;
        Measure.[Loading Dir Order Cal Master_Mix Max FR] = null;
        Measure.[Loading Dir Order Cal Master_Mix Cut Add] = null;
        Measure.[Loading Dir Order Cal Master_SKU Per Cntr] = null;
        Measure.[Loading Dir Order Cal Master_1st Mix] = null;
        Measure.[Loading Dir Order Cal Master_2nd Mix] = null;
        Measure.[Loading Dir Order Cal Master_3rd Mix] = null;
        Measure.[Loading Dir Order Cal Master_Item Height] = null;
        Measure.[Loading Dir Order Cal Master_Item Width] = null;
        Measure.[Loading Dir Order Cal Master_Item Depth] = null;
        Measure.[Loading Dir Order Cal Master_Profit Grade] = null;
        Measure.[Loading Dir Order Cal Master_Profit Grade Priority] = null;
    end scope;

    2.
    EXEC plugin instance [PY_UI_LoadingDirOrderMgmtValidCal_REG]
    for measures {
                    [Loading Dir Order Mgmt_Loading Master Match]
                }
    using scope (
                    [Version].[Version Name].[CWV_MP]
                )
    using arguments {
        (ExecutionMode, "MediumWeight")
        , (Param_OUT_VERSION, "CWV_MP")
        , (MaxSliceTableCells, 200000000)
        , (MaxConcurrency, 1 )
        , (IncludeNullRows, False)
        , ([Param.o9_sys_log_level], "DEBUG")
    };
"""
import os.path
import time
from typing import Tuple, List, Union, Any
import pandas as pd
import traceback
import numpy as np
import inspect
import datetime
import re

from pandas import DataFrame

from NSCMCommon import NSCMCommon as common

# Local 개발 시에 필요한 공통 변수 선언
# o9에 저장된 instanceName
str_instance = "PY_UI_LoadingDirOrderMgmtValidCal_REG"
str_input_dir = "Input/UILoadingDirOrderMgmtValidCalSHIPTOREG"
str_output_dir = "Output/UILoadingDirOrderMgmtValidCalSHIPTOREG"
is_local = common.gfn_get_isLocal()
is_print = True
flag_csv = True
flag_exception = True

# log 설정 : PROGRAM file_name
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level


def fn_log_dataframe(df_p_source: pd.DataFrame, str_p_source_name: str) -> None:
    """
    Dataframe 로그 출력 조건 지정 함수
    :param df_p_source: 로그로 찍을 Dataframe
    :param str_p_source_name: 로그로 찍을 Dataframe 명
    :return: None
    """
    is_output = False
    if str_p_source_name.startswith('out_'):
        is_output = True

    if is_print:
        logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
        if is_local and not df_p_source.empty and flag_csv:
            # 로컬 Debugging 시 csv 파일 출력
            df_p_source.to_csv(str_output_dir + "/" + str_p_source_name + ".csv", encoding="UTF8", index=False)
    else:
        # 최종 Output 테이블인 경우에는 무조건 로그 출력
        if is_output:
            logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
            if is_local and not df_p_source.empty:
                # 로컬 Debugging 시 csv 파일 출력
                df_p_source.to_csv(str_output_dir + "/" + str_p_source_name + ".csv", encoding="UTF8", index=False)


def _decoration_(func):
    def wrapper(*args, **kwargs):
        # 함수 시작 시각
        tm_start = time.time()
        result = func(*args)
        # 함수 종료 시각
        tm_end = time.time()
        # 함수 실행 시간 로그
        logger.Note(p_note=f'[{func.__name__}] Total time is {tm_end - tm_start:.5f} sec.',
                    p_log_level=LOG_LEVEL.debug())
        _step_no = kwargs.get('p_step_no')
        _step_desc = kwargs.get('p_step_desc')
        _df_name = kwargs.get('p_df_name')
        _warn_desc = kwargs.get('p_warn_desc')
        if _step_no is not None and _step_desc is not None:
            logger.Step(p_step_no=_step_no, p_step_desc=_step_desc)
        if _warn_desc is not None:
            if type(result) == pd.DataFrame and result.empty:
                logger.Note(p_note=_warn_desc, p_log_level=LOG_LEVEL.warning())
        if _df_name is not None:
            if type(result) == tuple:
                log_result_df = result[0]
            else:
                log_result_df = result
            fn_log_dataframe(log_result_df, _df_name)
        return result

    return wrapper


def fn_check_input_table(df_p_source: pd.DataFrame, str_p_source_name: str, str_p_cond: str) -> None:
    """
    Input Table을 체크한 결과를 로그 또는 Exception으로 표시한다.
    :param df_p_source: Input table
    :param str_p_source_name: Name of Input table
    :param str_p_cond: '0' - Exception, '1' - Warning Log
    :return: None
    """
    # Input Table 로그 출력
    logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)

    if df_p_source.empty:
        if str_p_cond == '0':
            # 테이블이 비어 있는 경우 raise Exception
            raise Exception(f'[Exception] Input table({str_p_source_name}) is empty.')
        else:
            # 테이블이 비어 있는 경우 Warning log
            logger.Note(p_note=f'Input table({str_p_source_name}) is empty.', p_log_level=LOG_LEVEL.warning())


@_decoration_
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :param str_p_cond:
    :return: tuple
    """
    df_return = pd.DataFrame()
    if str_p_cond == '0':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Sales Domain.[Ship To]': [], 'Item.[Item]': [], 'Time.[Week]': [], 'Seq.[Seq]': [],
                'Loading Dir Order Mgmt_Loading Master Match': [], 'Loading Dir Order Mgmt_Loading Master Match Chk': [],
                'Loading Dir Order Mgmt_Loading Method Match': [], 'Loading Dir Order Mgmt_Loading Method Match Chk': []
            }
        )
    elif str_p_cond == '1':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Sales Domain.[Ship To]': [], 'Item.[Item]': [], 'Time.[Week]': [],'Seq.[Seq]': [],
                'Loading Dir Order Cal Master_Min Qty': [], 'Loading Dir Order Cal Master_Multiple': [],
                'Loading Dir Order Cal Master_Max Load Qty': [],
                'Loading Dir Order Cal Master_JIG Line': [], 'Loading Dir Order Cal Master_Single FR Type': [],
                'Loading Dir Order Cal Master_Single Min FR': [], 'Loading Dir Order Cal Master_Single Max FR': [],
                'Loading Dir Order Cal Master_Single Cut Add': [], 'Loading Dir Order Cal Master_Mix FR Type': [],
                'Loading Dir Order Cal Master_Mix Min FR': [], 'Loading Dir Order Cal Master_Mix Max FR': [],
                'Loading Dir Order Cal Master_Mix Cut Add': [], 'Loading Dir Order Cal Master_SKU Per Cntr': [],
                'Loading Dir Order Cal Master_1st Mix': [], 'Loading Dir Order Cal Master_2nd Mix': [],
                'Loading Dir Order Cal Master_3rd Mix': [],
                'Loading Dir Order Cal Master_Item Width': [],
                'Loading Dir Order Cal Master_Item Height': [], 'Loading Dir Order Cal Master_Item Depth': [],
                'Loading Order Cal Master_Profit Grade': [], 'Loading Order Cal Master_Profit Grade Priority': [],
                'Loading Dir Order Cal Master_Item Mix Group': [],
                'Loading Dir Order Cal Master_JIG': [], 'Loading Dir Order Cal Master_Line':[]
            }
        )
    elif str_p_cond == '2':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Item.[Item]': [],
                'Container.[ContainerID]': [], 'Loading Type.[Loading Type]': [],
                'Loading Master From Site_Created By': [], 'Loading Master From Site_Creation Time': [],
                'Loading Master From Site_Valid Flag': []
            }
        )

    return df_return


def fn_preprocess(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Demand_Match Code, Demand_Build Ahead Time 공백 np.nan으로 변경
    :param df_p_source: in_Demand
    :return: DataFrame
    """
    # 함수 시작 시각
    tm_start = time.time()
    # 함수명
    str_my_name = 'fn_preprocess'
    # Return 변수
    df_return = pd.DataFrame()
    # 파라미터 테이블(df_p_source)이 비어 있는 경우 빈 데이터프레임을 리턴하면서함수를 종료한다.
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return
    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # 'Loading Dir Order Upload_Ship To', 'Shipment To.[Shipment To]' 컬럼을 있으면데이타 타입 str 이라 형변환
    for column in df_p_source.columns:
        if column == 'Loading Dir Order Mgmt_Ship To':
            df_return['Loading Dir Order Mgmt_Ship To'] = df_return['Loading Dir Order Mgmt_Ship To'].astype('str')
        elif column == 'Loading Master Ship To_Ship To':
            df_return['Loading Master Ship To_Ship To'] = df_return['Loading Master Ship To_Ship To'].astype('str')
        elif column == 'Loading Method Ship To_Ship To':
            df_return['Loading Method Ship To_Ship To'] = df_return['Loading Method Ship To_Ship To'].astype('str')
        elif column == 'Loading Method Mix Ship To_Ship To':
            df_return['Loading Method Mix Ship To_Ship To'] = df_return['Loading Method Mix Ship To_Ship To'].astype('str')
        # elif column == 'Loading Dir Order Mgmt_Created By':
        #     df_return = df_return[df_return[column] == Param_User_Name.split('@')[0]]
        # Order Stauts 화면에서 'Invalid BOD Date' value로 이미 들어가있는 상태에서 이값만 빼고 모두 초기화시키지 않으면
        # Dir Order Mgmt에 reason이 사라지지 않는 현상이 발생하여 추가
        elif column == 'Loading Dir Order Mgmt_Valid Fail Reason':
            df_return['Loading Dir Order Mgmt_Valid Fail Reason'] = np.where(
                df_return['Loading Dir Order Mgmt_Valid Fail Reason'].astype('str').str.contains('Invalid BOD Date'),
                df_return['Loading Dir Order Mgmt_Valid Fail Reason'].astype('str').str.split(',').str[0],
                np.nan
            )

    # Object 타입의 컬럼을 찾아 그 데이타의 양쪽의 공백이 있을 경우 공백 제거
    df_return[df_return.select_dtypes(['object']).columns] = df_return.select_dtypes(['object']).apply(
        lambda x: x.str.strip()
    )

    # 함수 종료 시각
    tm_end = time.time()
    # 함수 실행 시간 로그
    logger.Note(p_note=f'[{str_my_name}] Total time is {tm_end - tm_start:.5f} sec.', p_log_level=LOG_LEVEL.debug())
    # 결과 리턴
    return df_return


def fn_merge_after(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Merge 후처리
    :Merge 후 postfix '_y'가 붙은 컬럼 삭제, Merge 후 postfix '_x'가 붙은 컬럼에서 '_x' 삭제
    :param df_p_source: Merge 후처리 대상 DataFrame
    :return: DataFrame
    """
    # Merge 후 postfix '_y'가 붙은 컬럼 추출
    list_columns_y = df_p_source.filter(regex='_y$', axis=1).columns
    # Merge 후 postfix '_y'가 붙은 컬럼 삭제
    df_p_source.drop(list_columns_y, axis=1, inplace=True)

    # Merge 후 postfix '_x'가 붙은 컬럼에서 '_x' 삭제
    list_columns_all = df_p_source.columns
    list_columns_all_rename = []
    for col in list_columns_all:
        # list_columns_all_rename.append(col.rstrip('_x'))
        list_columns_all_rename.append(re.sub('_x$', '', col))
    df_p_source.columns = list_columns_all_rename

    return df_p_source


def check_empty_columns(row, list_p_chk_col: list, str_p_chk_step: str):
    """
    필수 컬럼값이 누락된 경우 누락컬럼명을 Display Name 표기,
    :param row: apply 각 row
    :param list_p_chk_col: 누락된 columns 대상
    :param str_p_chk_step: 누락된 columns step
    :return: 필수
    """
    dict_chk_list = {
        'Loading Dir Order Upload_Sales Order': 'So No.',
        'Loading Dir Order Upload_Prod Week': 'Prod WK',
        'Loading Dir Order Upload_Adj Prod Week': 'Adj PRD WK',
        'Loading Dir Order Upload_From Site': 'From Site',
        'Loading Dir Order Upload_To Site': 'To Site',
        'Loading Dir Order Upload_Account': 'Account',
        'Loading Dir Order Upload_Ship To': 'Ship To',
        'Loading Dir Order Upload_Item': 'Item',
        'Loading Dir Order Upload_Shipment Type': 'DIR/INDIR',
        'Loading Dir Order Upload_Org Qty': 'Origin Qty',
        'Loading Dir Order Upload_Loading Type': 'Loading Type',
        'Loading Dir Order Upload_Container Type': 'Container Type',
        'Loading Dir Order Upload_Chk Qty': 'Check Qty'
    }
    list_chk_col = list_p_chk_col
    empty_columns = [col for col in list_chk_col if pd.isna(row[col])]
    # 컬럼명이 길어 Loading Dir Order Upload_ 뒤 명으로 한정
    empty_columns = [dict_chk_list[col] for col in empty_columns]

    return str_p_chk_step + ': ' + ', '.join(empty_columns) if empty_columns else ''


def fn_get_master_list(str_p_master_type: str) -> Tuple[List[Union[str, Any]], List[str]]:
    list_master_columns = [
        'Sub Location.[Sub Location]',
        'Location.[Location]', 'Sales Domain.[Ship To]', 'Loading Master Ship To_Ship To', 'Item.[Item]',
        'Container.[ContainerID]', 'Loading Type.[Loading Type]',
        'Loading Master ' + str_p_master_type + '_Min Qty', 'Loading Master ' + str_p_master_type + '_Multiple',
        'Loading Master ' + str_p_master_type + '_Max Load Qty', 'Loading Master ' + str_p_master_type + '_LDM Qty',
        'Loading Master ' +  str_p_master_type + '_Valid Flag',
        'Loading Master ' + str_p_master_type + '_Depth', 'Loading Master ' + str_p_master_type + '_Height',
        'Loading Master ' + str_p_master_type + '_Width',
        'Loading Master ' + str_p_master_type + '_JIG', 'Loading Master ' + str_p_master_type + '_Line'
    ]

    list_dir_ordermgmt_columns = [
        'Sub Location.[Sub Location]',
        'Location.[Location]', 'Sales Domain.[Ship To]', 'Loading Dir Order Mgmt_Ship To', 'Item.[Item]',
        'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Loading Type'
    ]

    if str_p_master_type == 'Ship To':
        list_master_columns = list_master_columns[:]
        list_dir_ordermgmt_columns = list_dir_ordermgmt_columns[:]
    elif str_p_master_type == 'Account':
        list_master_columns.remove('Loading Master Ship To_Ship To')
        list_dir_ordermgmt_columns.remove('Loading Dir Order Mgmt_Ship To')
    elif str_p_master_type == 'To Site':
        list_master_columns.remove('Loading Master Ship To_Ship To')
        list_master_columns.remove('Sales Domain.[Ship To]')
        list_dir_ordermgmt_columns.remove('Loading Dir Order Mgmt_Ship To')
        list_dir_ordermgmt_columns.remove('Sales Domain.[Ship To]')
    elif str_p_master_type == 'From Site':
        list_master_columns.remove('Loading Master Ship To_Ship To')
        list_master_columns.remove('Sales Domain.[Ship To]')
        list_master_columns.remove('Location.[Location]')
        list_dir_ordermgmt_columns.remove('Loading Dir Order Mgmt_Ship To')
        list_dir_ordermgmt_columns.remove('Sales Domain.[Ship To]')
        list_dir_ordermgmt_columns.remove('Location.[Location]')

    return list_master_columns, list_dir_ordermgmt_columns


def fn_get_method_list(str_p_method_type: str) -> Tuple[List[Union[str, Any]], List[str]]:
    list_method_columns = [
        'Sub Location.[Sub Location]',
        'Location.[Location]', 'Sales Domain.[Ship To]', 'Loading Method Ship To_Ship To',
        'Container.[ContainerID]', 'Loading Type.[Loading Type]',
        'Loading Method ' + str_p_method_type + '_JIG Line',
        'Loading Method ' + str_p_method_type + '_Single FR Type', 'Loading Method ' + str_p_method_type + '_Single Min FR',
        'Loading Method ' + str_p_method_type + '_Single Max FR', 'Loading Method ' + str_p_method_type + '_Single Cut Add',
        'Loading Method ' + str_p_method_type + '_Mix FR Type', 'Loading Method ' + str_p_method_type + '_Mix Min FR',
        'Loading Method ' + str_p_method_type + '_Mix Max FR', 'Loading Method ' + str_p_method_type + '_Mix Cut Add',
        'Loading Method ' + str_p_method_type + '_SKU Per Cntr', 'Loading Method ' + str_p_method_type + '_1st Mix',
        'Loading Method ' + str_p_method_type + '_2nd Mix', 'Loading Method ' + str_p_method_type + '_3rd Mix',
        'Loading Method ' + str_p_method_type + '_Valid Flag', 'Loading Method ' + str_p_method_type + '_Default'
    ]

    list_dir_ordermgmt_columns = [
        'Sub Location.[Sub Location]',
        'Location.[Location]', 'Sales Domain.[Ship To]', 'Loading Dir Order Mgmt_Ship To',
        'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Loading Type'
    ]

    if str_p_method_type == 'Ship To':
        list_method_columns = list_method_columns[:]
        list_dir_ordermgmt_columns = list_dir_ordermgmt_columns[:]
    elif str_p_method_type == 'Account':
        list_method_columns.remove('Loading Method Ship To_Ship To')
        list_dir_ordermgmt_columns.remove('Loading Dir Order Mgmt_Ship To')
    elif str_p_method_type == 'To Site':
        list_method_columns.remove('Loading Method Ship To_Ship To')
        list_method_columns.remove('Sales Domain.[Ship To]')
        list_dir_ordermgmt_columns.remove('Loading Dir Order Mgmt_Ship To')
        list_dir_ordermgmt_columns.remove('Sales Domain.[Ship To]')
    elif str_p_method_type == 'From Site':
        list_method_columns.remove('Loading Method Ship To_Ship To')
        list_method_columns.remove('Sales Domain.[Ship To]')
        list_method_columns.remove('Location.[Location]')
        list_dir_ordermgmt_columns.remove('Loading Dir Order Mgmt_Ship To')
        list_dir_ordermgmt_columns.remove('Sales Domain.[Ship To]')
        list_dir_ordermgmt_columns.remove('Location.[Location]')

    return list_method_columns, list_dir_ordermgmt_columns


@_decoration_
def fn_get_ordermgmt_master_info(
        df_p_ordermgmt: pd.DataFrame, df_p_master_group: pd.DataFrame,
        list_p_ordermgmt_use_col: list, list_p_master_use_col: list, str_p_master_type: str
) -> Tuple[DataFrame, DataFrame]:
    """
    :param df_p_ordermgmt: Loading Mgmt Upload 데이타 프레임
    :param df_p_master_group: Loading Master Ship To ~ From
    :param list_p_ordermgmt_use_col: Loading Mgmt Upload 사용될 col
    :param list_p_master_use_col: Loading Master 사용될 col
    :param str_p_master_type: Ship To ~ From Site까지 구분자
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    # 파라미터 테이블(df_p_source)이 비어 있는 경우 빈 데이터프레임을 리턴하면서 함수를 종료한다.

    if df_p_master_group.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_methods) ' + str_p_master_type + '가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return pd.DataFrame(), df_p_ordermgmt
    df_p_master_group = df_p_master_group[list_p_master_use_col]

    str_query = f'`Loading Master {str_p_master_type}_Valid Flag` == "Y"'
    df_p_master_group = df_p_master_group.query(str_query)

    df_order_mgmt_merge = pd.merge(
        df_p_ordermgmt, df_p_master_group
        , left_on=list_p_ordermgmt_use_col
        , right_on=list_p_master_use_col[:-10]
        , how='left'
        , indicator=True
    )
    # master 메져와 dirOrderMgmt join이 된것들
    df_order_mgmt_master_combine = df_order_mgmt_merge[df_order_mgmt_merge['_merge'] == 'both'].copy()
    df_order_mgmt_master_combine = df_order_mgmt_master_combine.assign(
        **{
            'Loading Dir Order Mgmt_Loading Master Match': str_p_master_type,
            'Loading Dir Order Cal Master_Min Qty': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_Min Qty'],
            'Loading Dir Order Cal Master_Multiple': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_Multiple'],
            'Loading Dir Order Cal Master_Max Load Qty': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_Max Load Qty'],
            # Item Unit Load From ~ Ship To의 LDM Qty 메져그룹에 값을 Cal Master LDM Qty메져에 넣기
            'Loading Dir Order Cal Master_LDM Qty': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_LDM Qty'],
            'Loading Dir Order Cal Master_Item Depth': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_Depth'],
            'Loading Dir Order Cal Master_Item Height': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_Height'],
            'Loading Dir Order Cal Master_Item Width': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_Width'],
            'Loading Dir Order Cal Master_JIG': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_JIG'],
            'Loading Dir Order Cal Master_Line': df_order_mgmt_master_combine['Loading Master ' + str_p_master_type + '_Line']
        }
    )
    df_order_mgmt_master_combine = fn_output_formatter(df_order_mgmt_master_combine, Param_OUT_VERSION, '3')
    # master테이블에 존재하지 않는것들
    df_order_mgmt_master_combine_not = df_order_mgmt_merge[df_order_mgmt_merge['_merge'] == 'left_only'].copy()
    df_order_mgmt_master_combine_not.drop(
        columns=[
            'Loading Master ' + str_p_master_type + '_Min Qty', 'Loading Master ' + str_p_master_type + '_Multiple',
            'Loading Master ' + str_p_master_type + '_Max Load Qty', 'Loading Master ' + str_p_master_type + '_LDM Qty',
            'Loading Master ' + str_p_master_type + '_Valid Flag',
            'Container.[ContainerID]', 'Loading Type.[Loading Type]', '_merge'
        ], axis=1, inplace=True
    )

    return df_order_mgmt_master_combine, df_order_mgmt_master_combine_not


@_decoration_
def fn_get_ordermgmt_method_info(
        df_p_ordermgmt: pd.DataFrame, df_p_method_group: pd.DataFrame,
        list_p_ordermgmt_use_col: list, list_p_method_use_col: list, str_p_method_type: str
) -> pd.DataFrame:
    """
    :param df_p_ordermgmt: Loading Mgmt Upload 데이타 프레임
    :param df_p_method_group: Loading Master Ship To ~ From
    :param list_p_ordermgmt_use_col: Loading Mgmt Upload 사용될 col
    :param list_p_method_use_col: Loading Master 사용될 col
    :param str_p_method_type: Ship To ~ From Site까지 구분자
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    # 파라미터 테이블(df_p_source)이 비어 있는 경우 빈 데이터프레임을 리턴하면서 함수를 종료한다.
    # if df_p_ordermgmt.empty:
    #     logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_ordermgmt) 가 비어 있습니다.',
    #                 p_log_level=LOG_LEVEL.warning())
    #     return pd.DataFrame(), pd.DataFrame()
    if df_p_method_group.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_methods) ' + df_p_method_group + '가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return pd.DataFrame(), df_p_ordermgmt
    df_p_method_group = df_p_method_group[list_p_method_use_col]

    str_query = f'`Loading Method {str_p_method_type}_Valid Flag` == "Y"'
    df_p_method_group = df_p_method_group.query(str_query)

    df_order_mgmt_merge = pd.merge(
        df_p_ordermgmt, df_p_method_group
        , left_on=list_p_ordermgmt_use_col
        , right_on=list_p_method_use_col[:-15]
        , how='left'
        , indicator=True
    )
    # master 메져와 dirOrderMgmt join이 된것들
    df_order_mgmt_method_combine = df_order_mgmt_merge[df_order_mgmt_merge['_merge'] == 'both'].copy()

    df_order_mgmt_method_combine = df_order_mgmt_method_combine.assign(
        **{
            'Loading Dir Order Mgmt_Loading Method Match': str_p_method_type,
            'Loading Dir Order Cal Master_JIG Line':        df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_JIG Line'],
            'Loading Dir Order Cal Master_Single FR Type':  df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Single FR Type'],
            'Loading Dir Order Cal Master_Single Min FR':   df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Single Min FR'],
            'Loading Dir Order Cal Master_Single Max FR':   df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Single Max FR'],
            'Loading Dir Order Cal Master_Single Cut Add':  df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Single Cut Add'],
            'Loading Dir Order Cal Master_Mix FR Type':     df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Mix FR Type'],
            'Loading Dir Order Cal Master_Mix Min FR':      df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Mix Min FR'],
            'Loading Dir Order Cal Master_Mix Max FR':      df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Mix Max FR'],
            'Loading Dir Order Cal Master_Mix Cut Add':     df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_Mix Cut Add'],
            'Loading Dir Order Cal Master_SKU Per Cntr':    df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_SKU Per Cntr'],
            'Loading Dir Order Cal Master_1st Mix':         df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_1st Mix'],
            'Loading Dir Order Cal Master_2nd Mix':         df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_2nd Mix'],
            'Loading Dir Order Cal Master_3rd Mix':         df_order_mgmt_method_combine['Loading Method ' + str_p_method_type + '_3rd Mix']
        }
    )
    df_order_mgmt_method_combine = fn_output_formatter(df_order_mgmt_method_combine, Param_OUT_VERSION, '4')
    # master테이블에 존재하지 않는것들
    df_order_mgmt_method_combine_not = df_order_mgmt_merge[df_order_mgmt_merge['_merge'] == 'left_only'].copy()
    df_order_mgmt_method_combine_not.drop(
        columns=[
            'Loading Method ' + str_p_method_type + '_JIG Line',
            'Loading Method ' + str_p_method_type + '_Single FR Type',
            'Loading Method ' + str_p_method_type + '_Single Min FR',
            'Loading Method ' + str_p_method_type + '_Single Max FR',
            'Loading Method ' + str_p_method_type + '_Single Cut Add',
            'Loading Method ' + str_p_method_type + '_Mix FR Type',
            'Loading Method ' + str_p_method_type + '_Mix Min FR',
            'Loading Method ' + str_p_method_type + '_Mix Max FR',
            'Loading Method ' + str_p_method_type + '_Mix Cut Add',
            'Loading Method ' + str_p_method_type + '_SKU Per Cntr', 'Loading Method ' + str_p_method_type + '_1st Mix',
            'Loading Method ' + str_p_method_type + '_2nd Mix', 'Loading Method ' + str_p_method_type + '_3rd Mix',
            'Loading Method ' + str_p_method_type + '_Valid Flag', 'Loading Method ' + str_p_method_type + '_Default',
            'Container.[ContainerID]', 'Loading Type.[Loading Type]', '_merge'
        ], axis=1, inplace=True
    )

    return df_order_mgmt_method_combine, df_order_mgmt_method_combine_not


def fn_output_formatter(df_p_source: pd.DataFrame, str_p_out_version: str, str_p_format_type: str) -> pd.DataFrame:
    """
    최종 Output 형태로 가공하기
    :param df_p_source: df_ItemBOMRouting_concat, df_MfgNetwork_concat, df_ItemBODLaneFrozenWindow_concat
    :param str_p_out_version: Param_OUT_VERSION
    :return: DataFrame
    """
    # 함수 시작 시각
    tm_start = time.time()

    # 함수명
    str_my_name = 'fn_output_formatter'

    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터(str_p_out_version)가 비어 있는 경우 오류를 발생시키고 함수를 종료한다.
    if str_p_out_version is None or str_p_out_version.strip() == '':
        raise Exception(f'Exception: Param_OUT_VERSION(str_p_out_version)이 비어 있습니다. : {str_my_name}')

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    if str_p_format_type == '1':
        # boolean 형식의 칼럼 중 비어 있는 값은 False로 채운다.
        df_return['Loading Dir Order Cal Master_JIG Line'] = (
            df_return['Loading Dir Order Cal Master_JIG Line'].replace(r'^\s*$', np.nan, regex=True).fillna(False).astype(bool)
        )
        # String 형식 칼럼 중 비어 있는 값은 '' 채운다.
        df_return[['Loading Dir Order Cal Master_JIG', 'Loading Dir Order Cal Master_Line']] = (
            df_return[['Loading Dir Order Cal Master_JIG', 'Loading Dir Order Cal Master_Line']]
            .replace(r'^\s*$', np.nan, regex=True).fillna('').astype(str)
        )
        # JIG Line Value
        df_return['JIG Line Value'] = (
            np.where(df_return['Loading Dir Order Cal Master_JIG Line'],
                     df_return['Loading Dir Order Cal Master_JIG'] + df_return['Loading Dir Order Cal Master_Line'], '')
        )

        # Loading Dir Order Mgmt_Chk Route :  prod week + from + jigLineValue + to + account + shipTo
        str_route_key = (
            df_return['Loading Dir Order Mgmt_Adj Prod Week'].astype(str) + '_' +
            df_return['Sub Location.[Sub Location]'].astype(str) + '_' +
            np.where(df_return['JIG Line Value'] != '', df_return['JIG Line Value'] + '_', '') +
            df_return['Location.[Location]'].astype(str) + '_' +
            df_return['Sales Domain.[Ship To]'].astype(str) + '_' +
            df_return['Loading Dir Order Mgmt_Ship To'].astype(str)
        )

        df_return['Loading Dir Order Mgmt_Chk Route'] = str_route_key

        df_return = df_return[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
                'Sales Domain.[Ship To]', 'Item.[Item]', 'Time.[Week]', 'Seq.[Seq]',
                'Loading Dir Order Mgmt_Loading Master Match', 'Loading Dir Order Mgmt_Loading Master Match Chk',
                'Loading Dir Order Mgmt_Loading Method Match', 'Loading Dir Order Mgmt_Loading Method Match Chk',
                'Loading Dir Order Mgmt_Valid Fail Reason' , 'Loading Dir Order Mgmt_Chk Route'
            ]
        ]
    elif str_p_format_type == '2':
        # Loading Dir Order Cal Master_Chk Grain :  week + from + to + account + seq + item
        str_grain_key = (
                df_return['Time.[Week]'].astype(str) + '_' +
                df_return['Sub Location.[Sub Location]'].astype(str) + '_' +
                df_return['Location.[Location]'].astype(str) + '_' +
                df_return['Sales Domain.[Ship To]'].astype(str) + '_' +
                df_return['Seq.[Seq]'].astype(str) + '_' +
                df_return['Item.[Item]'].astype(str)
        )

        df_return['Loading Dir Order Cal Master_Chk Grain'] = str_grain_key
        df_return = df_return[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
                'Sales Domain.[Ship To]', 'Item.[Item]', 'Time.[Week]', 'Seq.[Seq]',
                'Loading Dir Order Cal Master_Min Qty', 'Loading Dir Order Cal Master_Multiple',
                'Loading Dir Order Cal Master_Max Load Qty', 'Loading Dir Order Cal Master_JIG Line',
                'Loading Dir Order Cal Master_LDM Qty',
                'Loading Dir Order Cal Master_Single FR Type', 'Loading Dir Order Cal Master_Single Min FR',
                'Loading Dir Order Cal Master_Single Max FR', 'Loading Dir Order Cal Master_Single Cut Add',
                'Loading Dir Order Cal Master_Mix FR Type', 'Loading Dir Order Cal Master_Mix Min FR',
                'Loading Dir Order Cal Master_Mix Max FR', 'Loading Dir Order Cal Master_Mix Cut Add',
                'Loading Dir Order Cal Master_SKU Per Cntr', 'Loading Dir Order Cal Master_1st Mix',
                'Loading Dir Order Cal Master_2nd Mix', 'Loading Dir Order Cal Master_3rd Mix',
                'Loading Dir Order Cal Master_Item Width', 'Loading Dir Order Cal Master_Item Height',
                'Loading Dir Order Cal Master_Item Depth',
                'Loading Dir Order Cal Master_Profit Grade', 'Loading Dir Order Cal Master_Profit Grade Priority',
                'Loading Dir Order Cal Master_Item Mix Group',
                'Loading Dir Order Cal Master_JIG', 'Loading Dir Order Cal Master_Line',
                'Loading Dir Order Cal Master_Chk Grain'
            ]
        ]
    elif str_p_format_type == '3':
        df_return = df_return[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]',
                'Location.[Location]', 'Sales Domain.[Ship To]', 'Item.[Item]',
                'Time.[Week]', 'Seq.[Seq]', 'Loading Dir Order Mgmt_SO Item',
                'Loading Dir Order Mgmt_Adj Prod Week',
                'Loading Dir Order Mgmt_Ship To',
                'Loading Dir Order Mgmt_Ship To Name',
                'Loading Dir Order Mgmt_Loading Type',
                'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Origin Qty',
                'Loading Dir Order Mgmt_Chk Qty',
                'Loading Dir Order Mgmt_Loading Master Match',
                'Loading Dir Order Mgmt_Valid Fail Reason',
                'Loading Dir Order Cal Master_Min Qty',
                'Loading Dir Order Cal Master_Multiple',
                'Loading Dir Order Cal Master_Max Load Qty',
                'Loading Dir Order Cal Master_LDM Qty',
                'Loading Dir Order Cal Master_Item Depth',
                'Loading Dir Order Cal Master_Item Height',
                'Loading Dir Order Cal Master_Item Width',
                'Loading Dir Order Cal Master_JIG',
                'Loading Dir Order Cal Master_Line',
            ]
        ]
    elif str_p_format_type == "4":
        df_return = df_return[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]',
                'Location.[Location]', 'Sales Domain.[Ship To]', 'Item.[Item]',
                'Time.[Week]', 'Seq.[Seq]', 'Loading Dir Order Mgmt_SO Item',
                'Loading Dir Order Mgmt_Adj Prod Week',
                'Loading Dir Order Mgmt_Ship To',
                'Loading Dir Order Mgmt_Ship To Name',
                'Loading Dir Order Mgmt_Loading Type',
                'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Origin Qty',
                'Loading Dir Order Mgmt_Chk Qty',
                'Loading Dir Order Mgmt_Loading Method Match',
                'Loading Dir Order Cal Master_JIG Line',
                'Loading Dir Order Cal Master_Single FR Type',
                'Loading Dir Order Cal Master_Single Min FR',
                'Loading Dir Order Cal Master_Single Max FR',
                'Loading Dir Order Cal Master_Single Cut Add',
                'Loading Dir Order Cal Master_Mix FR Type',
                'Loading Dir Order Cal Master_Mix Min FR',
                'Loading Dir Order Cal Master_Mix Max FR',
                'Loading Dir Order Cal Master_Mix Cut Add',
                'Loading Dir Order Cal Master_SKU Per Cntr',
                'Loading Dir Order Cal Master_1st Mix',
                'Loading Dir Order Cal Master_2nd Mix',
                'Loading Dir Order Cal Master_3rd Mix'
            ]
        ]

    # 함수 종료 시각
    tm_end = time.time()
    # 함수 실행 시간 로그
    logger.Note(p_note=f'[{str_my_name}] Total time is {tm_end - tm_start:.5f} sec.',
                p_log_level=LOG_LEVEL.debug())

    # 결과 리턴
    return df_return


@_decoration_
def fn_update_valid_chk_reason(df_p_upload_valid_chk: pd.DataFrame, df_p_qty: pd.DataFrame) -> pd.DataFrame:
    """
    check Qty수량 Loading Order Cal Master_Min Qty보다 작은 경우에 Valid Fail Reason 표기
    :param df_p_upload_valid_chk: df_p_upload_valid_chk DataFrame
    :param df_p_qty: check qty를 위해 DataFrame
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 파라미터 테이블(df_p_upload_source)이 비어 있는 경우 빈 데이터프레임을 리턴하면서 함수를 종료한다.
    if df_p_upload_valid_chk.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_upload_valid_chk)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_upload_valid_chk
    if df_p_qty.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_qty)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_qty

    df_orderuploadvalid_chk = pd.merge(
        df_p_upload_valid_chk, df_p_qty,
        on='Seq.[Seq]', how='inner'
    )

    # 1~5 Check를 합쳐서 list로 만든다. 'Loading Dir Order Valid Chk_Valid Fail Reason'을 합쳐서 저장한다.
    df_orderuploadvalid_chk['Loading Dir Order Valid Chk_Valid Fail Reason'] = df_orderuploadvalid_chk.apply(
        lambda row: [
            row['first Check'], row['second Check'], row['third Check'], row['forth Check'], row['fifth Check']
        ], axis=1
    )
    # 1~5 Check중 값이 있는 것만 list를 ,구분하여 문자열 구성
    df_orderuploadvalid_chk['Loading Dir Order Valid Chk_Valid Fail Reason'] = df_orderuploadvalid_chk[
        'Loading Dir Order Valid Chk_Valid Fail Reason'
    ].apply(lambda x: ', '.join([item for item in x if item]))
    # out_OrderUploadValid_Chk의 필수 컬럼만
    df_return = df_orderuploadvalid_chk.copy()

    return df_return


@_decoration_
def fn_get_cal_master_item_mix_group(
        df_p_cal_master_mix_exists: pd.DataFrame, df_p_method_mix: pd.DataFrame, str_p_mix_group_type: str
) -> Tuple[DataFrame, DataFrame]:
    """
    :param df_p_cal_master_mix_exists: 1st Mix, 2nd Mix, 3rd Mix값에 Item Mix Group값이 들어있는 cal master
    :param df_p_method_mix: ship To & To Site Mix Group 데이타프레임
    :param str_p_mix_group_type: mix group 구분 문자 값
    :return:
    """
    # 함수 시작 시각
    tm_start = time.time()

    # 함수명
    str_my_name = inspect.stack()[0][3]

    if df_p_cal_master_mix_exists.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_cal_master_mix_exists) 가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return pd.DataFrame(), pd.DataFrame()

    if df_p_method_mix.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_method_mix) ' + str_p_mix_group_type + '가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return pd.DataFrame(), df_p_cal_master_mix_exists

    list_cal_master_columns = [
        'Sub Location.[Sub Location]','Location.[Location]', 'Loading Dir Order Mgmt_Ship To', 'Item.[Item]',
        'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Loading Type'
    ]
    list_method_mix_columns = [
        'Sub Location.[Sub Location]', 'Location.[Location]', 'Loading Method Mix Ship To_Ship To', 'Item.[Item]',
        'Loading Method Mix ' + str_p_mix_group_type + '_Cntr Type',
        'Loading Method Mix ' + str_p_mix_group_type + '_Loading Type'
    ]
    if str_p_mix_group_type == 'Ship To':
        list_cal_master_columns = list_cal_master_columns[:]
        list_method_mix_columns = list_method_mix_columns[:]
    elif str_p_mix_group_type == 'To Site':
        list_cal_master_columns.remove('Loading Dir Order Mgmt_Ship To')
        list_method_mix_columns.remove('Loading Method Mix Ship To_Ship To')


    # Valid Flag가 Y인것만
    str_query = f'`Loading Method Mix {str_p_mix_group_type} Detail_Valid Flag` == "Y"'
    df_p_method_mix = df_p_method_mix.query(str_query).copy()
    # method mix 아래 컬럼 중복있는 row만 가져오기
    df_p_method_mix['mix duplicated'] = df_p_method_mix.duplicated(
        subset=list_method_mix_columns, keep=False
    )
    # 중복 col중에 첫번째 row만 유지
    df_p_method_mix.drop_duplicates(
        subset=list_method_mix_columns, keep='first', inplace=True, ignore_index=True
    )
    # df_p_method_mix와 join
    df_cal_mst_mix_exists_merge = pd.merge(
        df_p_cal_master_mix_exists, df_p_method_mix,
        left_on=list_cal_master_columns, right_on=list_method_mix_columns,
        how='left', indicator=True
    )
    # 중복 col 제거 및 _merge컬럼 제거
    df_cal_mst_mix_exists_merge = fn_merge_after(df_cal_mst_mix_exists_merge)
    df_cal_mst_mix_exists_combine = df_cal_mst_mix_exists_merge[df_cal_mst_mix_exists_merge['_merge'] == 'both'].copy()

    df_cal_mst_mix_exists_combine['Loading Dir Order Cal Master_Item Mix Group'] = df_cal_mst_mix_exists_combine['Loading Method Mix ' + str_p_mix_group_type + '_Item Mix Group']
    df_cal_mst_mix_exists_combine = df_cal_mst_mix_exists_combine[
        [
            'Seq.[Seq]', 'Loading Dir Order Cal Master_Item Mix Group'
        ]
    ]
    # master테이블에 존재하지 않는것들
    df_cal_mst_mix_exists_combine_none = df_cal_mst_mix_exists_merge[df_cal_mst_mix_exists_merge['_merge'] == 'left_only'].copy()
    # 필요없는 columns 제거
    df_cal_mst_mix_exists_combine_none.drop(
        columns=[
            'Loading Method Mix ' + str_p_mix_group_type + '_Item Mix Group',
            'Loading Method Mix ' + str_p_mix_group_type + '_Cntr Type',
            'Loading Method Mix ' + str_p_mix_group_type + '_Loading Type',
            'Loading Method Mix ' + str_p_mix_group_type + ' Detail_Valid Flag',
            'mix duplicated', '_merge'
        ], axis=1, inplace=True
    )

    # 함수 종료 시각
    tm_end = time.time()
    # 함수 실행 시간 로그
    logger.Note(p_note=f'[{str_my_name}] Total time is {tm_end - tm_start:.5f} sec.',
                p_log_level=LOG_LEVEL.debug())

    return df_cal_mst_mix_exists_combine, df_cal_mst_mix_exists_combine_none


@_decoration_
def fn_create_item_unit_load(df_p_master_notdefined: pd.DataFrame, dict_p_dims: dict) -> pd.DataFrame:
    """
    :param df_p_master_notdefined: master not match 된 df
    :param dict_p_dims: in_Loading_Master_From_Site & df_p_item_uld dict
    :return: Loading Master From Site 에 등록될 df
    """
    # 함수 시작 시각
    tm_start = time.time()
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # return df
    df_return_itemunitload = pd.DataFrame()

    df_p_master_from_site = dict_p_dims.get('in_Loading_Master_From_Site')
    df_p_item_uld = dict_p_dims.get('in_Item_ULD')

    if df_p_master_notdefined.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_master_notdefined) 가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return_itemunitload

    # 함수 종료 시각
    tm_end = time.time()
    # 본문
    df_p_master_notdefined.rename(
        columns={
            'Loading Dir Order Mgmt_Cntr Type': 'Container.[ContainerID]',
            'Loading Dir Order Mgmt_Loading Type': 'Loading Type.[Loading Type]'
        }, inplace=True
    )
    # in_Loading_Master_From_Site 에 Valid 'N'이 존재하는 확인을 위해 merge
    df_p_master_notdefined_merge = pd.merge(
        df_p_master_notdefined, df_p_master_from_site,
        on=[
            'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Item.[Item]',
            'Container.[ContainerID]', 'Loading Type.[Loading Type]'
        ], how='left', indicator=True
    )
    df_return_itemunitload = df_p_master_notdefined_merge[df_p_master_notdefined_merge['_merge'] == 'left_only']
    # merge indicator로 생긴 _merge컬럼 제거
    df_return_itemunitload = df_return_itemunitload.drop(columns='_merge', axis=1)
    if not df_return_itemunitload.empty:
        # Item에 대한 Item ULD_Width, Item ULD_Height, Item ULD_Depth을 구해
        # Loading Master From Site_Width, Loading Master From Site_Height, Loading Master From Site_Depth insert
        df_return_itemunitload = pd.merge(
            df_return_itemunitload, df_p_item_uld,
            on=['Item.[Item]'], how='left', indicator=True
        )
        # 중복 컬럼 제거
        df_return_itemunitload = fn_merge_after(df_return_itemunitload)
        # 컬럼 할당
        df_return_itemunitload = df_return_itemunitload.assign(
            **{
                'Loading Master From Site_Width': df_return_itemunitload['Item ULD_Width'],
                'Loading Master From Site_Height': df_return_itemunitload['Item ULD_Height'],
                'Loading Master From Site_Depth': df_return_itemunitload['Item ULD_Depth'],
                'Loading Master From Site_Created By': 'System',
                'Loading Master From Site_Creation Time': (
                        datetime.datetime.now() + datetime.timedelta(hours=9)
                ).strftime('%Y-%m-%d %H:%M:%S') if not is_local else datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S'),
                'Loading Master From Site_Valid Flag': 'N',
                'Loading Master From Site_CIS Info Update': 'Y'
            }
        )
        # 필요 컬럼만
        df_return_itemunitload = df_return_itemunitload[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Item.[Item]',
                'Container.[ContainerID]', 'Loading Type.[Loading Type]',
                'Loading Master From Site_Width', 'Loading Master From Site_Height', 'Loading Master From Site_Depth',
                'Loading Master From Site_Created By',
                'Loading Master From Site_Creation Time', 'Loading Master From Site_Valid Flag',
                'Loading Master From Site_CIS Info Update'
            ]
        ]
        # Container.[ContainerID], Loading Type.[Loading Type] 디멘져이므로 na인건 제외하고 return
        df_return_itemunitload = df_return_itemunitload.query('`Container.[ContainerID]`.notna() & `Loading Type.[Loading Type]`.notna()')

    # 함수 실행 시간 로그
    logger.Note(p_note=f'[{str_my_name}] Total time is {tm_end - tm_start:.5f} sec.',
                p_log_level=LOG_LEVEL.debug())
    return df_return_itemunitload


@_decoration_
def fn_insert_mix_group(df_p_mst_mix_exists: pd.DataFrame, df_p_master_method_cal: pd.DataFrame) -> pd.DataFrame:
    """
    :param df_p_mst_mix_exists: master not match 된 df
    :param df_p_master_method_cal: in_Loading_Master_From_Site
    :return: df_p_master_method_cal
    """
    # 함수 시작 시각
    tm_start = time.time()
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # return df
    df_return_master_method_cal = pd.DataFrame()
    # 데이터 가공 전 DF 복사
    # df_return_master_method_cal = df_p_master_method_cal.copy(deep=True)

    if df_p_mst_mix_exists.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_mst_mix_exists) 가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_master_method_cal

    df_return_master_method_cal = pd.merge(
        df_p_master_method_cal, df_p_mst_mix_exists,
        on='Seq.[Seq]', how='left', indicator=True
    )
    df_return_master_method_cal.drop('_merge', axis=1, inplace=True)
    # 함수 종료 시각
    tm_end = time.time()
    # 함수 실행 시간 로그
    logger.Note(p_note=f'[{str_my_name}] Total time is {tm_end - tm_start:.5f} sec.',
                p_log_level=LOG_LEVEL.debug())

    return df_return_master_method_cal


@_decoration_
def fn_frtype_case_master_valid(df_p_param: pd.DataFrame, df_p_cntr_info: pd.DataFrame) -> pd.DataFrame:
    """
    :param df_p_param: df_loading_master_method_cal DataFrame
    :param df_p_cntr_info: in_container_info DataFrame Container Length 0 or NaN 확인을 위한 DataFrame
    :return: df_loading_master_method_cal Master Match, Master Match Check값을 변경된
    """
    # 함수 시작 시각
    tm_start = time.time()
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # return df
    df_return = pd.DataFrame()
    if df_p_param.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_param) 가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_param

    # single F/R type, Mixed F/R Type 둘중에 하나 LDM
    # - M/L Qty 정보 有, Size 정보 無 → "No Size Info"
    df_p_param.loc[
        (
            (df_p_param['Loading Dir Order Mgmt_Loading Master Match'] != 'Not Defined') &
            (
                (df_p_param['Loading Dir Order Cal Master_Single FR Type'] == 'LDM') |
                (df_p_param['Loading Dir Order Cal Master_Mix FR Type'] == 'LDM')
            ) &
            (
                (df_p_param['Loading Dir Order Cal Master_LDM Qty'].isna()) |
                (df_p_param['Loading Dir Order Cal Master_LDM Qty'] == 0)
            )
        ), ['Loading Dir Order Mgmt_Loading Master Match', 'Loading Dir Order Mgmt_Loading Master Match Chk']
    ] = ['No LDM Qty Info', 'N']
    # - M/L Qty 정보 無, Size 정보 有 → "No M/L Qty Info" ,
    df_p_param.loc[
        (
            (df_p_param['Loading Dir Order Mgmt_Loading Master Match'] != 'Not Defined') &
            (
                (df_p_param['Loading Dir Order Cal Master_Single FR Type'] == 'LDM') |
                (df_p_param['Loading Dir Order Cal Master_Mix FR Type'] == 'LDM')
            ) &
            (
                (df_p_param['Loading Dir Order Cal Master_Max Load Qty'].isna()) |
                (df_p_param['Loading Dir Order Cal Master_Max Load Qty'] == 0)
            )
        ), ['Loading Dir Order Mgmt_Loading Master Match', 'Loading Dir Order Mgmt_Loading Master Match Chk']
    ] = ['No M/L Qty Info', 'N']
    # - M/L Qty 정보 無, Size 정보 無 → "No Size & M/L Qty Info"
    df_p_param.loc[
        (
            (df_p_param['Loading Dir Order Mgmt_Loading Master Match'] != 'Not Defined') &
            (
                (df_p_param['Loading Dir Order Cal Master_Single FR Type'] == 'LDM') |
                (df_p_param['Loading Dir Order Cal Master_Mix FR Type'] == 'LDM')
            )
            &
            (
                (df_p_param['Loading Dir Order Cal Master_Max Load Qty'].isna()) |
                (df_p_param['Loading Dir Order Cal Master_Max Load Qty'] == 0)
            ) &
            (
                (df_p_param['Loading Dir Order Cal Master_LDM Qty'].isna()) |
                (df_p_param['Loading Dir Order Cal Master_LDM Qty'] == 0)
            )
        ), ['Loading Dir Order Mgmt_Loading Master Match', 'Loading Dir Order Mgmt_Loading Master Match Chk']
    ] = ['No LDM Qty & M/L Qty Info', 'N']

    # 2) [single F/R type 'M/L Qty' & Mixed F/R Type 'M/L Qty' 케이스]
    #    - M/L Qty 정보 有 → "Y"
    #    - M/L Qty 정보 無 → "No M/L Qty Info"
    df_p_param.loc[
        (
            (df_p_param['Loading Dir Order Mgmt_Loading Master Match'] != 'Not Defined') &
            (df_p_param['Loading Dir Order Cal Master_Single FR Type'] == 'M/L Qty') &
            (df_p_param['Loading Dir Order Cal Master_Mix FR Type'] == 'M/L Qty') &
            (
                (
                    (df_p_param['Loading Dir Order Cal Master_Max Load Qty'].isna()) |
                    (df_p_param['Loading Dir Order Cal Master_Max Load Qty'] == 0)
                )
            )
        ),
        ['Loading Dir Order Mgmt_Loading Master Match', 'Loading Dir Order Mgmt_Loading Master Match Chk']
    ] = ['No M/L Qty Info', 'N']

    # 3) [single F/R type LDM & Mixed F/R Type LDM 케이스
    # - LDM정보 有 → "Y", - LDM 정보 無 → "No M/L Qty Info"
    df_p_param = pd.merge(
        df_p_param, df_p_cntr_info,
        left_on=['Sub Location.[Sub Location]', 'Loading Dir Order Mgmt_Cntr Type'],
        right_on=['Sub Location.[Sub Location]', 'Container.[ContainerID]'],
        how='left', indicator=True
    )
    df_p_param.loc[
        (
            (df_p_param['Loading Dir Order Mgmt_Loading Master Match'] != 'Not Defined') &
            (
                (df_p_param['Loading Dir Order Cal Master_Single FR Type'] == 'LDM') &
                (df_p_param['Loading Dir Order Cal Master_Mix FR Type'] == 'LDM')
            ) &
            (
                (
                    df_p_param['_merge'] == 'left_only'
                )
            )
        ),
        ['Loading Dir Order Mgmt_Loading Master Match', 'Loading Dir Order Mgmt_Loading Master Match Chk']
    ] = ['No M/L Qty Info', 'N']
    df_p_param.drop('_merge', axis=1, inplace=True)
    df_p_param = fn_merge_after(df_p_param)
    df_return = df_p_param.copy()

    # 함수 종료 시각
    tm_end = time.time()
    # 함수 실행 시간 로그
    logger.Note(p_note=f'[{str_my_name}] Total time is {tm_end - tm_start:.5f} sec.',
                p_log_level=LOG_LEVEL.debug())

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()
    # Output 테이블 선언
    out_Loading_Dir_Order_Mgmt_Valid = pd.DataFrame()
    out_Loading_Dir_Order_Cal_Master = pd.DataFrame()
    out_Item_Unit_Load = pd.DataFrame()

    str_location_display = 'Location.[Location$DisplayName]'
    str_sub_location_display = 'Sub Location.[Sub Location$DisplayName]'
    str_account_display = 'Account.[Account$DisplayName]'
    str_shipment_to_display = 'Shipment To.[Shipment To$DisplayName]'
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = ''
            Param_User_Name = 'daeun01.yun@partner.samsung.com'
            Param_PLANTYPE = ''
            # Loading Dir Order Mgmt 메져그룹에 일부 메져를 읽어온 데이타프레임
            in_Loading_Dir_Order_Mgmt = pd.read_csv(str_input_dir + "/in_Loading_Dir_Order_Mgmt.csv", encoding="UTF8")
            # Loading Master Ship To ~ From Site
            in_Loading_Master_Ship_To = pd.read_csv(str_input_dir + "/in_Loading_Master_Ship_To.csv", encoding="UTF8")
            in_Loading_Master_Account = pd.read_csv(str_input_dir + "/in_Loading_Master_Account.csv", encoding="UTF8")
            in_Loading_Master_To_Site = pd.read_csv(str_input_dir + "/in_Loading_Master_To_Site.csv", encoding="UTF8")
            in_Loading_Master_From_Site = pd.read_csv(str_input_dir + "/in_Loading_Master_From_Site.csv", encoding="UTF8")
            # Loading Method Ship To ~ From Site
            in_Loading_Method_Ship_To = pd.read_csv(str_input_dir + "/in_Loading_Method_Ship_To.csv", encoding="UTF8")
            in_Loading_Method_Account = pd.read_csv(str_input_dir + "/in_Loading_Method_Account.csv", encoding="UTF8")
            in_Loading_Method_To_Site = pd.read_csv(str_input_dir + "/in_Loading_Method_To_Site.csv", encoding="UTF8")
            in_Loading_Method_From_Site = pd.read_csv(str_input_dir + "/in_Loading_Method_From_Site.csv", encoding="UTF8")
            # Profit Grade
            in_profit_grade = pd.read_csv(str_input_dir + "/in_profit_grade.csv", encoding="UTF8")
            # in_Item_ULD
            in_Item_ULD = pd.read_csv(str_input_dir + "/in_Item_ULD.csv", encoding="UTF8")
            # mix group
            in_ship_to_mix_group = pd.read_csv(str_input_dir + "/in_ship_to_mix_group.csv", encoding="UTF8")
            in_to_site_mix_group = pd.read_csv(str_input_dir + "/in_to_site_mix_group.csv", encoding="UTF8")
            in_container_info = pd.read_csv(str_input_dir + "/in_container_info.csv", encoding="UTF8")
            # 로컬일때 'Shipment To.[Shipment To]'컬럼 형변환 필요. 안맞추면 merge시 에러
            in_Loading_Dir_Order_Mgmt = fn_preprocess(in_Loading_Dir_Order_Mgmt)
            in_Loading_Master_Ship_To = fn_preprocess(in_Loading_Master_Ship_To)
            in_Loading_Method_Ship_To = fn_preprocess(in_Loading_Method_Ship_To)
            in_ship_to_mix_group = fn_preprocess(in_ship_to_mix_group)

        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')

        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())
        # Loading Dir Order Mgmt 메져그룹에 일부 메져를 읽어온 데이타프레임
        fn_check_input_table(in_Loading_Dir_Order_Mgmt, 'in_Loading_Dir_Order_Mgmt', '0')
        # Loading Master Ship To ~ From Site
        fn_check_input_table(in_Loading_Master_Ship_To, 'in_Loading_Master_Ship_To', '1')
        fn_check_input_table(in_Loading_Master_Account, 'in_Loading_Master_Account', '1')
        fn_check_input_table(in_Loading_Master_To_Site, 'in_Loading_Master_To_Site', '1')
        fn_check_input_table(in_Loading_Master_From_Site, 'in_Loading_Master_From_Site', '1')
        # Loading Method Ship To ~ From Site
        fn_check_input_table(in_Loading_Method_Ship_To, 'in_Loading_Method_Ship_To', '1')
        fn_check_input_table(in_Loading_Method_Account, 'in_Loading_Method_Account', '1')
        fn_check_input_table(in_Loading_Method_To_Site, 'in_Loading_Method_To_Site', '1')
        fn_check_input_table(in_Loading_Method_From_Site, 'in_Loading_Method_From_Site', '1')
        # Profit Grade
        fn_check_input_table(in_profit_grade, 'in_profit_grade', '1')
        # in_Item_ULD
        fn_check_input_table(in_Item_ULD, 'in_Item_ULD', '1')
        # mix group
        fn_check_input_table(in_ship_to_mix_group, 'in_ship_to_mix_group', '1')
        fn_check_input_table(in_to_site_mix_group, 'in_to_site_mix_group', '1')
        fn_check_input_table(in_container_info, 'in_container_info', '1')

        # 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 작업 진행함.
        df_Loading_Dir_Order_Mgmt = fn_preprocess(in_Loading_Dir_Order_Mgmt)

        # Loading *** Master *** 메져그룹에서 Ship To ~ From 필요 커럼 가져오기 ########################################
        dict_log = {
            'p_step_no': 110,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Master > Ship To에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_shipto_combine'
        }
        # Ship TO 사용될 measure 리스트 구해오기
        list_master_use_col, list_ordermgmt_use_col  = fn_get_master_list('Ship To')
        # Ship To 메져를 구해오기 위해 fn_get_ordermgmt_master_info 함수 호출
        df_order_mgmt_shipto_combine, df_order_mgmt_master_combine_none = fn_get_ordermgmt_master_info(
            df_Loading_Dir_Order_Mgmt, in_Loading_Master_Ship_To, list_ordermgmt_use_col, list_master_use_col,
            'Ship To', **dict_log
        )

        dict_log = {
            'p_step_no': 120,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Master > Account에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_account_combine'
        }
        # master 메저그룹 Account
        list_master_use_col, list_ordermgmt_use_col = fn_get_master_list('Account')
        df_order_mgmt_account_combine, df_order_mgmt_master_combine_none = fn_get_ordermgmt_master_info(
            df_order_mgmt_master_combine_none, in_Loading_Master_Account,
            list_ordermgmt_use_col, list_master_use_col, 'Account', **dict_log
        )

        dict_log = {
            'p_step_no': 130,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Master > To Site에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_tosite_combine'
        }
        # master 메저그룹 To Site
        list_master_use_col, list_ordermgmt_use_col = fn_get_master_list('To Site')
        df_order_mgmt_tosite_combine, df_order_mgmt_master_combine_none = fn_get_ordermgmt_master_info(
            df_order_mgmt_master_combine_none, in_Loading_Master_To_Site,
            list_ordermgmt_use_col, list_master_use_col, 'To Site', **dict_log
        )

        dict_log = {
            'p_step_no': 140,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Master > From Site에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_fromsite_combine'
        }
        # master 메저그룹 From Site
        list_master_use_col, list_ordermgmt_use_col = fn_get_master_list('From Site')
        df_order_mgmt_fromsite_combine, df_order_mgmt_master_combine_none = fn_get_ordermgmt_master_info(
            df_order_mgmt_master_combine_none, in_Loading_Master_From_Site,
            list_ordermgmt_use_col, list_master_use_col, 'From Site', **dict_log
        )

        # ShipTo ~ From Site에 없는것들
        # Step Log
        logger.Step(p_step_no=150, p_step_desc=f' => ShipTo ~ From Site에 없는것들')
        if not df_order_mgmt_master_combine_none.empty:
            df_order_mgmt_master_combine_none = df_order_mgmt_master_combine_none.assign(
                **{
                    'Loading Dir Order Mgmt_Loading Master Match': 'Not Defined',
                    'Loading Dir Order Cal Master_Min Qty': np.nan,
                    'Loading Dir Order Cal Master_Multiple': np.nan,
                    'Loading Dir Order Cal Master_Max Load Qty': np.nan,
                    'Loading Dir Order Cal Master_LDM Qty': np.nan,
                    'Loading Dir Order Cal Master_Item Depth': np.nan,
                    'Loading Dir Order Cal Master_Item Height': np.nan,
                    'Loading Dir Order Cal Master_Item Width': np.nan,
                    'Loading Dir Order Cal Master_JIG': np.nan,
                    'Loading Dir Order Cal Master_Line': np.nan
                }
            )

            df_order_mgmt_master_combine_none = fn_output_formatter(
                df_order_mgmt_master_combine_none, Param_OUT_VERSION, '3'
            )
            # log
            logger.PrintDF(p_df=df_order_mgmt_master_combine_none,
                           p_df_name='df_order_mgmt_master_combine_none(Master)', p_log_level=LOG_LEVEL.debug(),
                           p_format=1)
            # Local Debug용 CSV 파일 생성
            if is_local and not df_order_mgmt_master_combine_none.empty:
                df_order_mgmt_master_combine_none.to_csv(str_output_dir + '/df_order_mgmt_master_combine_none.csv', encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=160, p_step_desc=f' => Cal Master measure concat')
        dfs_to_combine_concat = [df_bod_combine for df_bod_combine in [
            df_order_mgmt_shipto_combine, df_order_mgmt_account_combine, df_order_mgmt_tosite_combine,
            df_order_mgmt_fromsite_combine, df_order_mgmt_master_combine_none
        ] if not df_bod_combine.empty]
        # 데이터프레임을 concat
        df_order_mgmt_loading_master_cal = pd.concat(dfs_to_combine_concat, ignore_index=True) if dfs_to_combine_concat else pd.DataFrame()

        # Step Log
        logger.Step(p_step_no=170, p_step_desc=f' => Loading Dir Order Mgmt_Valid Fail Reason')
        # Loading Dir Order Mgmt_Valid Fail Reason
        df_order_mgmt_loading_master_cal['Loading Dir Order Mgmt_Chk Qty Sum'] = df_order_mgmt_loading_master_cal.groupby([
            'Sub Location.[Sub Location]',
            'Location.[Location]', 'Sales Domain.[Ship To]', 'Item.[Item]',
            'Loading Dir Order Mgmt_Ship To', 'Loading Dir Order Mgmt_Adj Prod Week',
            'Loading Dir Order Mgmt_Loading Type', 'Loading Dir Order Mgmt_Cntr Type'
        ])['Loading Dir Order Mgmt_Chk Qty'].transform('sum')

        str_add_reason_value = "The value of 'Chk qty' is  Less than the minimum qty for Simulation."
        str_reason_condition = (
                (
                    df_order_mgmt_loading_master_cal['Loading Dir Order Mgmt_Loading Master Match'] != 'Not Defined'
                ) &
                (
                    df_order_mgmt_loading_master_cal['Loading Dir Order Mgmt_Chk Qty Sum'] < df_order_mgmt_loading_master_cal['Loading Dir Order Cal Master_Min Qty']
                )
        )
        # order status에서 넘어온 'Loading Dir Order Mgmt_Valid Fail Reason'값이 있을수 있기 때문에 concate하는 로직추가
        df_order_mgmt_loading_master_cal.loc[
            str_reason_condition, 'Loading Dir Order Mgmt_Valid Fail Reason'
        ] = df_order_mgmt_loading_master_cal.loc[
            str_reason_condition
        ].apply(
            lambda row: f"{row['Loading Dir Order Mgmt_Valid Fail Reason']}, {str_add_reason_value}" if pd.notnull(row['Loading Dir Order Mgmt_Valid Fail Reason']) else str_add_reason_value, axis=1
        )

        # 각 From Site/To Site/Account/Ship To 기준정보 내에  grain이 맞는 아래 3개의 메저값이
        # null이거나 0인 경우는 무조건 N으로 처리한다.
        # _Min Qty, _Multiple, _Max Load Qty, Fail Reason
        df_order_mgmt_loading_master_cal['Loading Dir Order Mgmt_Loading Master Match Chk'] = np.where(
            (df_order_mgmt_loading_master_cal['Loading Dir Order Cal Master_Min Qty'].isna()) |
            (df_order_mgmt_loading_master_cal['Loading Dir Order Cal Master_Min Qty'] == 0) |
            (df_order_mgmt_loading_master_cal['Loading Dir Order Cal Master_Multiple'].isna()) |
            (df_order_mgmt_loading_master_cal['Loading Dir Order Cal Master_Multiple'] == 0) |
            (df_order_mgmt_loading_master_cal['Loading Dir Order Cal Master_Max Load Qty'] == 0) |
            (df_order_mgmt_loading_master_cal['Loading Dir Order Cal Master_Max Load Qty'].isna()) |
            (df_order_mgmt_loading_master_cal['Loading Dir Order Mgmt_Valid Fail Reason'].notna()),
            'N',
            'Y'
        )
        # Local Debug용 CSV 파일 생성
        if is_local and not df_order_mgmt_loading_master_cal.empty:
            df_order_mgmt_loading_master_cal.to_csv(str_output_dir + '/df_order_mgmt_loading_master_cal.csv',
                                                     encoding='UTF8')

        # Chk & Cal Loading Method #####################################################################################
        dict_log = {
            'p_step_no': 210,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Method > Ship To에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_method_shipto_combine'
        }
        # method 메저그룹 Ship TO
        list_method_use_col, list_ordermgmt_use_col = fn_get_method_list('Ship To')
        df_order_mgmt_method_shipto_combine, df_order_mgmt_method_combine_none = fn_get_ordermgmt_method_info(
            df_Loading_Dir_Order_Mgmt, in_Loading_Method_Ship_To, list_ordermgmt_use_col, list_method_use_col,
            'Ship To', **dict_log
        )

        dict_log = {
            'p_step_no': 220,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Method > Account에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_method_account_combine'
        }
        # method 메저그룹 Account
        list_method_use_col, list_ordermgmt_use_col = fn_get_method_list('Account')
        df_order_mgmt_method_account_combine, df_order_mgmt_method_combine_none = fn_get_ordermgmt_method_info(
            df_order_mgmt_method_combine_none, in_Loading_Method_Account, list_ordermgmt_use_col, list_method_use_col,
            'Account', **dict_log
        )

        dict_log = {
            'p_step_no': 230,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Method > To Site에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_method_tosite_combine'
        }
        # method 메저그룹 To Site
        list_method_use_col, list_ordermgmt_use_col = fn_get_method_list('To Site')
        df_order_mgmt_method_tosite_combine, df_order_mgmt_method_combine_none = fn_get_ordermgmt_method_info(
            df_order_mgmt_method_combine_none, in_Loading_Method_To_Site, list_ordermgmt_use_col, list_method_use_col,
            'To Site', **dict_log
        )

        dict_log = {
            'p_step_no': 240,
            'p_step_desc': 'Loading Mgmt Upload 메져와 Loading Method > From Site에서 필요 measure가져오기',
            'p_df_name': 'df_order_mgmt_method_fromsite_combine'
        }
        # method 메저그룹 From Site
        list_method_use_col, list_ordermgmt_use_col = fn_get_method_list('From Site')
        df_order_mgmt_method_fromsite_combine, df_order_mgmt_method_combine_none = fn_get_ordermgmt_method_info(
            df_order_mgmt_method_combine_none, in_Loading_Method_From_Site, list_ordermgmt_use_col, list_method_use_col,
            'From Site', **dict_log
        )
        # Step Log
        logger.Step(p_step_no=250, p_step_desc=f' => Method ShipTo ~ From Site에 없는것들')
        # ShipTo ~ From Site에 없는것들
        if not df_order_mgmt_method_combine_none.empty:
            df_order_mgmt_method_combine_none = df_order_mgmt_method_combine_none.assign(
                **{
                    'Loading Dir Order Mgmt_Loading Method Match': 'Not Defined',
                    'Loading Dir Order Cal Master_JIG Line': '',
                    'Loading Dir Order Cal Master_Single FR Type': '',
                    'Loading Dir Order Cal Master_Single Min FR': '',
                    'Loading Dir Order Cal Master_Single Max FR': '',
                    'Loading Dir Order Cal Master_Single Cut Add': '',
                    'Loading Dir Order Cal Master_Mix FR Type': '',
                    'Loading Dir Order Cal Master_Mix Min FR': '',
                    'Loading Dir Order Cal Master_Mix Max FR': '',
                    'Loading Dir Order Cal Master_Mix Cut Add': '',
                    'Loading Dir Order Cal Master_SKU Per Cntr': '',
                    'Loading Dir Order Cal Master_1st Mix': '',
                    'Loading Dir Order Cal Master_2nd Mix': '',
                    'Loading Dir Order Cal Master_3rd Mix': ''
                }
            )
            df_order_mgmt_method_combine_none = fn_output_formatter(
                df_order_mgmt_method_combine_none, Param_OUT_VERSION, '4'
            )
            # log
            logger.PrintDF(p_df=df_order_mgmt_method_combine_none,
                           p_df_name='df_order_mgmt_method_combine_none(Master)', p_log_level=LOG_LEVEL.debug(),
                           p_format=1)

        # Step Log
        logger.Step(p_step_no=260, p_step_desc=f' => Cal Master measure concat')
        # method concat 아래 데이타프레임 empty가 아닌것만 concat
        dfs_to_combine_concat = [df_bod_combine for df_bod_combine in [
            df_order_mgmt_method_shipto_combine, df_order_mgmt_method_account_combine,
            df_order_mgmt_method_tosite_combine, df_order_mgmt_method_fromsite_combine,
            df_order_mgmt_method_combine_none
        ] if not df_bod_combine.empty]
        # # 데이터프레임을 concat
        df_order_mgmt_loading_method_cal = pd.concat(dfs_to_combine_concat, ignore_index=True) if dfs_to_combine_concat else pd.DataFrame()

        df_order_mgmt_loading_method_cal['Loading Dir Order Mgmt_Loading Method Match Chk'] = np.where(
            df_order_mgmt_loading_method_cal['Loading Dir Order Mgmt_Loading Method Match'] == 'Not Defined'
            , 'N'
            , 'Y'
        )
        # Local Debug용 CSV 파일 생성
        if is_local and not df_order_mgmt_loading_method_cal.empty:
            df_order_mgmt_loading_method_cal.to_csv(str_output_dir + '/df_order_mgmt_loading_method_cal.csv',
                                                    encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=310, p_step_desc=f' => Method, Master 기준테이블에서 가져와 구성된 데이타프레임을합친다.')
        # Method, Master 기준테이블에서 가져와 구성된 데이타프레임을 합친다.
        df_loading_master_method_cal = pd.merge(
            df_order_mgmt_loading_master_cal, df_order_mgmt_loading_method_cal,
            on='Seq.[Seq]',
            how='inner'
        )
        df_loading_master_method_cal = fn_merge_after(df_loading_master_method_cal)

        dict_log = {
            'p_step_no': 320,
            'p_step_desc': 'ITEM UNIT LOAD 관련 VALIDATION',
            'p_df_name': 'fn_frtype_case_master_valid'
        }
        df_loading_master_method_cal = fn_frtype_case_master_valid(
            df_loading_master_method_cal, in_container_info, **dict_log
        )

        # Item Mix Group Ship To, To Site에 대한 valid check 함수 호출
        # 1st~3rd Mix에 Item MIx Group이 존재하는 경우 다음의 validation을 수행한다.
        df_cal_mst_mix_exists = df_loading_master_method_cal[
            df_loading_master_method_cal[
                [
                    'Loading Dir Order Cal Master_1st Mix', 'Loading Dir Order Cal Master_2nd Mix',
                    'Loading Dir Order Cal Master_3rd Mix'
                ]
            ].apply(lambda row: 'Item Mix Group' in row.values, axis=1)
        ]
        dict_log = {
            'p_step_no': 410,
            'p_step_desc': 'Item Mix Group Ship To valid check 함수 호출',
            'p_df_name': 'fn_get_cal_master_item_mix_group'
        }
        # 함수 fn_get_cal_master_item_mix_group 호출 Mix Group Ship To valid를 위한
        df_cal_mst_mix_exists_shipto_mix_valid_combine, df_cal_mst_mix_exists_mix_valid_combine_none = fn_get_cal_master_item_mix_group(
            df_cal_mst_mix_exists, in_ship_to_mix_group, 'Ship To', **dict_log
        )
        dict_log = {
            'p_step_no': 420,
            'p_step_desc': 'Item Mix Group To Site valid check 함수 호출',
            'p_df_name': 'fn_get_cal_master_item_mix_group'
        }
        # 함수 fn_get_cal_master_item_mix_group 호출 Mix Group To Site valid를 위한
        df_cal_mst_mix_exists_tosite_mix_valid_combine, df_cal_mst_mix_exists_mix_valid_combine_none = fn_get_cal_master_item_mix_group(
            df_cal_mst_mix_exists_mix_valid_combine_none, in_to_site_mix_group, 'To Site', **dict_log
        )
        # 1st~3rd Mix에 Item MIx Group이 존재하는데 Ship To, To Site Mix Group에 존재 하지 않는다면
        if not df_cal_mst_mix_exists_mix_valid_combine_none.empty:
            # Step Log
            logger.Step(p_step_no=430, p_step_desc=f' => Ship TO & To Site Item Mix Group에 있지 않는것들')

            df_cal_mst_mix_exists_mix_valid_combine_none = df_cal_mst_mix_exists_mix_valid_combine_none.assign(
                **{
                    'Loading Dir Order Cal Master_Item Mix Group': np.nan
                }
            )
            df_cal_mst_mix_exists_mix_valid_combine_none = df_cal_mst_mix_exists_mix_valid_combine_none[
                ['Seq.[Seq]', 'Loading Dir Order Cal Master_Item Mix Group']
            ]
        # 데이타가 있는 DataFrame만 리스트를 만들어 concat 대상으로 지정한다.
        dfs_to_combine_concat = [df_bod_combine for df_bod_combine in [
            df_cal_mst_mix_exists_shipto_mix_valid_combine, df_cal_mst_mix_exists_tosite_mix_valid_combine,
            df_cal_mst_mix_exists_mix_valid_combine_none
        ] if not df_bod_combine.empty]

        # 데이터프레임을 concat
        df_cal_mst_mix_exists_result = pd.concat(dfs_to_combine_concat,
                                                 ignore_index=True) if dfs_to_combine_concat else pd.DataFrame()
        logger.PrintDF(p_df=df_cal_mst_mix_exists_result, p_df_name='df_cal_mst_mix_exists_result', p_log_level=LOG_LEVEL.debug(), p_format=1)
        dict_log = {
            'p_step_no': 430,
            'p_step_desc': 'Item Mix Group reason을 기존 reason에 concat하는 함수 호출',
            'p_df_name': 'fn_insert_mix_group_reason'
        }
        df_loading_master_method_cal = fn_insert_mix_group(
            df_cal_mst_mix_exists_result, df_loading_master_method_cal, **dict_log
        )

        # Loading Dir Order Cal Master_Item Mix Group 컬럼이 존재 하지 않을 경우
        # Loading Dir Order Cal Master_Item Mix Group 생성. 하지 않으면 formmat에서 에러 발생
        if 'Loading Dir Order Cal Master_Item Mix Group' not in df_loading_master_method_cal.columns:
            df_loading_master_method_cal['Loading Dir Order Cal Master_Item Mix Group'] = np.nan
        if is_local and not df_loading_master_method_cal.empty:
            df_loading_master_method_cal.to_csv(str_output_dir + '/df_loading_master_method_cal.csv', encoding='UTF8')

        # Step Log
        logger.Step(p_step_no=610, p_step_desc=f' => Profit Grade 메져 구성')
        # 메져그룹 Loading Order Cal Master_Profit Grade에 대한 Profit Grade, Profit Grade Priority 가져오기
        # Loading Profit Grade_Profit Grade Valid Flag가 True인것만
        df_profit_grade = in_profit_grade.query('`Loading Profit Grade_Profit Grade Valid Flag` == True').copy()
        # df_profit_grade DataFrame merge
        df_loading_master_method_cal = pd.merge(
            df_loading_master_method_cal, df_profit_grade,
            on=['Item.[Item]', 'Location.[Location]'],
            how='left', indicator=True
        )
        # 중복 컬럼 제거
        df_loading_master_method_cal = fn_merge_after(df_loading_master_method_cal)
        # Profit Grade df모두 불일치 rows 'C', 3으로 coding
        df_loading_master_method_cal.loc[
            df_loading_master_method_cal['_merge'] == 'left_only',
            ['Loading Profit Grade_Profit Grade', 'Loading Profit Grade_Profit Grade Priority']
        ] = ['C', 3]

        # Profit Grade Priority, Grade Valid Flag를 Cal Master 메져명에 맞게 변경
        df_loading_master_method_cal.rename(
            columns={
                'Loading Profit Grade_Profit Grade': 'Loading Dir Order Cal Master_Profit Grade',
                'Loading Profit Grade_Profit Grade Priority': 'Loading Dir Order Cal Master_Profit Grade Priority'
            }, inplace=True
        )

        # out_Loading_Dir_Order_Mgmt_Valid
        out_Loading_Dir_Order_Mgmt_Valid = fn_output_formatter(df_loading_master_method_cal, Param_OUT_VERSION,
                                                               '1')

        # Loading Dir Order Mgmt_Loading Master Match Chk, Loading Dir Order Mgmt_Loading Method Match Chk 모두 'Y'일때
        # out_Loading_Dir_Order_Cal_Master 생성

        if (
                (df_loading_master_method_cal['Loading Dir Order Mgmt_Loading Master Match Chk'] == 'Y').all() &
                (df_loading_master_method_cal['Loading Dir Order Mgmt_Loading Method Match Chk'] == 'Y').all() &
                (
                    (df_loading_master_method_cal['Loading Dir Order Mgmt_Valid Fail Reason'] == '') |
                    (df_loading_master_method_cal['Loading Dir Order Mgmt_Valid Fail Reason'] == 'nan') |
                    (df_loading_master_method_cal['Loading Dir Order Mgmt_Valid Fail Reason'].isna())
                ).all()
        ):
            out_Loading_Dir_Order_Cal_Master = fn_output_formatter(df_loading_master_method_cal,
                                                                   Param_OUT_VERSION,
                                                                   '2')
        # Loading Dir Order Mgmt_Loading Master Match 컬럼에 'Not Defined'값이 하나라도 있으면
        if (df_loading_master_method_cal['Loading Dir Order Mgmt_Loading Master Match'] == 'Not Defined').any():
            dict_log = {
                'p_step_no': 710,
                'p_step_desc': 'Loading Master Match "Not Defined"이 있으면 Item Unit Load 자동생성을위한 함수 호출',
                'p_df_name': 'fn_create_item_unit_load'
            }
            # Loading Dir Order Mgmt_Loading Master Match 컬럼에 'Not Defined'인 row추출하고 필요 columns만 추려낸다.
            df_Master_Not_Defined = df_loading_master_method_cal.loc[
                df_loading_master_method_cal['Loading Dir Order Mgmt_Loading Master Match'] == 'Not Defined',
                [
                    'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Item.[Item]',
                    'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Loading Type'
                ]
            ]
            # Loading Master From Site 에 등록될 df return 하는 함수 호출
            # dict_Dims_For_DisplayName_ItemInfo
            dict_Dims_For_FromMaster_Create = {
                'in_Loading_Master_From_Site': in_Loading_Master_From_Site,
                'in_Item_ULD': in_Item_ULD
            }
            out_Item_Unit_Load = fn_create_item_unit_load(df_Master_Not_Defined, dict_Dims_For_FromMaster_Create, **dict_log)

        # Dataframe 확인 로그
        if not out_Loading_Dir_Order_Mgmt_Valid.empty:
            fn_log_dataframe(out_Loading_Dir_Order_Mgmt_Valid, 'out_Loading_Dir_Order_Mgmt_Valid')
        if not out_Loading_Dir_Order_Cal_Master.empty:
            fn_log_dataframe(out_Loading_Dir_Order_Cal_Master, 'out_Loading_Dir_Order_Cal_Master')
        if not out_Item_Unit_Load.empty:
            fn_log_dataframe(out_Item_Unit_Load, 'out_Item_Unit_Load')

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_Loading_Dir_Order_Mgmt_Valid = None
            out_Loading_Dir_Order_Cal_Master = None
            out_Item_Unit_Load = None
            raise Exception(e)
        else:
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    finally:
        # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
        # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들어 줌.
        if out_Loading_Dir_Order_Mgmt_Valid.empty:
            out_Loading_Dir_Order_Mgmt_Valid = fn_set_header('0')
            fn_log_dataframe(out_Loading_Dir_Order_Mgmt_Valid, 'out_Loading_Dir_Order_Mgmt_Valid')
        if out_Loading_Dir_Order_Cal_Master.empty:
            out_Loading_Dir_Order_Cal_Master = fn_set_header('1')
            fn_log_dataframe(out_Loading_Dir_Order_Cal_Master, 'out_Loading_Dir_Order_Cal_Master')
        if out_Item_Unit_Load.empty:
            out_Item_Unit_Load = fn_set_header('2')
            fn_log_dataframe(out_Item_Unit_Load, 'out_Item_Unit_Load')
