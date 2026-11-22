"""
* 프로그램명
    - PY_UI_BODLaneCal_REG.py

* 내용
    -
* 변경이력
    - 2025.10.27 / Miss Lee / Create

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를 결정하는 파라미터

* Input Tables
    - in_BODPort :
        Select (
                  [Version].[Version Name]
                * &NSFromSiteMF
                * &NSToSiteDC
                * [Activity2].[Activity2]
                * [Loading Port].[Loading Port]
                * [Loading Port].[Loading Logistics Port]
                * [Discharge Port].[Discharge Port]
                * [Discharge Port].[Discharge Logistics Port]
                * [Dest Port].[Dest Port]
                ) on row,
                ({
                    Measure.[BOD Port_Recent Year Volume CNTR (12W)]
                  , Measure.[BOD Port_Recent Year Volume CNTR (4W)]
                  , Measure.[BOD Port_Recent Year Volume CNTR (Y-1 M)]
                  , Measure.[BOD Port_Recent Year Volume CNTR (Y-1)]
                  , Measure.[BOD Port_Valid Flag]
                }) on column
        where { Measure.[BOD Port_Valid Flag] == "Y"  || isnull(Measure.[BOD Port_Valid Flag]) };

    - in_OceanCapa:
        Select (
                  [Version].[Version Name]
                * &CurrentWeek.relatedmembers([Planning Month]) // 당월(&CurrentWeek 기준)
                * [Loading Port].[Loading SCM Port]
                * [Loading Port].[Loading Logistics Port]
                * [Discharge Port].[Discharge SCM Port]
                * [Discharge Port].[Discharge Logistics Port]
                ) on row,
            ({
                Measure.[Ocean Capa W_Capa Qty]
            }) on column;


* Output Tables
    - out_BODPort:
        Select (
                  [Version].[Version Name]
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Activity2].[Activity2]
                * [Loading Port].[Loading Port]
                * [Discharge Port].[Discharge Port]
                * [Dest Port].[Dest Port]
                ) on row,
            ({
                  Measure.[BOD Port_Capa Qty(12W)]
                , Measure.[BOD Port_Capa Qty(4W)]
                , Measure.[BOD Port_Capa Qty(Y-1 M)]
                , Measure.[BOD Port_Capa Qty(Y-1)]
                , Measure.[BOD Port_Ratio(BOD per Port 12W)]
                , Measure.[BOD Port_Ratio(BOD per Port 4W)]
                , Measure.[BOD Port_Ratio(BOD per Port Y-1 M)]
                , Measure.[BOD Port_Ratio(BOD per Port Y-1)]
                , Measure.[BOD Port_Ratio(Port per BOD 4W)]
                , Measure.[BOD Port_Ratio(Port per BOD 12W)]
                , Measure.[BOD Port_Ratio(Port per BOD Y-1 M)]
                , Measure.[BOD Port_Ratio(Port per BOD Y-1)]
            }) on column;


* Flow Summary
    STEP 1.
         Step 1-1)
         Loading Port.[Loading Logistics Port], Discharge Port.[Discharge Logistics Port]별로
         group by 하여 4개 항목 별(4W, 12W, Y-1 M, Y-1) 로 total sum을 구하고
         row 별  recent year volume /total sum 으로 비율을 구하여 BOD per Port Ratio 메저에 반영한다.
         ex) BOD Port_Ratio(BOD per Port 4W) =
         BOD Port_Recent Year Volume CNTR (4W) / total sum(BOD Port_Recent Year Volume CNTR (4W))
                                                 group by(Loading Port.[Loading Logistics Port]
                                                        , Discharge Port.[Discharge Logistics Port])
         Measure.[BOD Port_Recent Year Volume CNTR (4W)]  → Measure.[BOD Port_Ratio(BOD per Port 4W)]
         Measure.[BOD Port_Recent Year Volume CNTR (12W)] → Measure.[BOD Port_Ratio(BOD per Port 12W)]
         Measure.[BOD Port_Recent Year Volume CNTR (Y-1)] → Measure.[BOD Port_Ratio(BOD per Port Y-1)]
         Measure.[BOD Port_Recent Year Volume CNTR (Y-1 M)] → Measure.[BOD Port_Ratio(BOD per Port Y-1 M)]

        Step 1-2)
            BOD 기준으로 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2]별로
            group by 하여 4개 항목 별(4W, 12W, Y-1 M, Y-1)로 total sum을 구하고
            row별 recent year volume /total sum 으로 비율을 구하여 Port per BOD Ratio 메저에 반영한다.
            ex) BOD Port_Ratio(Port per BOD 4W) =
            BOD Port_Recent Year Volume CNTR (4W) / total sum(BOD Port_Recent Year Volume CNTR (4W))
                                                    group by (SubLocation, Location, Activity2)
            메저 생성 1-1)과 동일

    STEP2. STEP1의 df와 in_OceanCapa를
           [Loading Port].[Loading Logistics Port], [Discharge Port].[Discharge Logistics Port] 기준으로
           left join하여
           Ocean Capa W_Capa Qty *  BOD Port_Ratio(4W, 12W, Y1, Y1M) 결과 값을
           BOD Port_Capa Qty(4W), BOD Port_Capa Qty(12W), BOD Port_Capa Qty(Y-1), BOD Port_Capa Qty(Y-1 M)
           메저에 반영 한다.

* Validation :

* Execution :
    1. 기존 메저 데이터 삭제(nullify)
        Scope:([Version].[Version Name].CWV_MP);
          Measure.[BOD Port_Capa Qty(12W)] = null;
          Measure.[BOD Port_Capa Qty(4W)] = null;
          Measure.[BOD Port_Capa Qty(Y-1 M)] = null;
          Measure.[BOD Port_Capa Qty(Y-1)] = null;
          Measure.[BOD Port_Ratio(BOD per Port 12W)] = null;
          Measure.[BOD Port_Ratio(BOD per Port 4W)] = null;
          Measure.[BOD Port_Ratio(BOD per Port Y-1 M)] = null;
          Measure.[BOD Port_Ratio(BOD per Port Y-1)] = null;
          Measure.[BOD Port_Ratio(Port per BOD 4W)] = null;
          Measure.[BOD Port_Ratio(Port per BOD 12W)] = null;
          Measure.[BOD Port_Ratio(Port per BOD Y-1 M)] = null;
          Measure.[BOD Port_Ratio(Port per BOD Y-1)] = null;
        end scope;

    2. Plugin Call하여 신규 MG 생성
    1) LightWeight
        EXEC plugin instance [PY_UI_BODLaneCal_REG]
            for measures { [BOD Port_Capa Qty(12W)]
                         , [BOD Port_Capa Qty(4W)]
                         , [BOD Port_Capa Qty(Y-1 M)]
                         , [BOD Port_Capa Qty(Y-1)]
                         , [BOD Port_Ratio(BOD per Port 12W)]
                         , [BOD Port_Ratio(BOD per Port 4W)]
                         , [BOD Port_Ratio(BOD per Port Y-1 M)]
                         , [BOD Port_Ratio(BOD per Port Y-1)]
                         , [BOD Port_Ratio(Port per BOD 4W)]
                         , [BOD Port_Ratio(Port per BOD 12W)]
                         , [BOD Port_Ratio(Port per BOD Y-1 M)]
                         , [BOD Port_Ratio(Port per BOD Y-1)]
                        }
               using scope ([Version].[Version Name].[CWV_MP])
               using arguments {(ExecutionMode, "LightWeight")
                             , (Param_OUT_VERSION, "CWV_MP")
                             , (MaxSliceTableCells, 200000000)
                             , (MaxConcurrency, 1 )
                             , (IncludeNullRows, False)
                             , ([Param.o9_sys_log_level], "DEBUG")
                             };

    2) MediumWeight
        EXEC plugin instance [PY_UI_BODLaneCal_REG]
            for measures { [BOD Port_Capa Qty(12W)]
                         , [BOD Port_Capa Qty(4W)]
                         , [BOD Port_Capa Qty(Y-1 M)]
                         , [BOD Port_Capa Qty(Y-1)]
                         , [BOD Port_Ratio(BOD per Port 12W)]
                         , [BOD Port_Ratio(BOD per Port 4W)]
                         , [BOD Port_Ratio(BOD per Port Y-1 M)]
                         , [BOD Port_Ratio(BOD per Port Y-1)]
                         , [BOD Port_Ratio(Port per BOD 4W)]
                         , [BOD Port_Ratio(Port per BOD 12W)]
                         , [BOD Port_Ratio(Port per BOD Y-1 M)]
                         , [BOD Port_Ratio(Port per BOD Y-1)]
                        }
               using scope ([Version].[Version Name].[CWV_MP])
               using arguments {(ExecutionMode, "MediumWeight")
                             , (Param_OUT_VERSION, "CWV_MP")
                             , (MaxSliceTableCells, 200000000)
                             , (MaxConcurrency, 1 )
                             , (IncludeNullRows, False)
                             , ([Param.o9_sys_log_level], "DEBUG")
                             };

"""
import inspect
import os.path
import time

import numpy as np
import pandas as pd
import traceback
import re
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_BODLaneCal_REG"
str_input_dir = "Input/UIBODLaneCalREG"
str_output_dir = "Output/UIBODLaneCalREG"
is_local = common.gfn_get_isLocal()
is_print = True
flag_csv = True
flag_exception = True

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
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
        if is_local and not df_p_source is None and not df_p_source.empty and flag_csv:
            # 로컬 Debugging 시 csv 파일 출력
            df_p_source.to_csv(str_output_dir + "/"+str_p_source_name+".csv", encoding="UTF8", index=False)
    else:
        # 최종 Output 테이블인 경우에는 무조건 로그 출력
        if is_output:
            logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
            if is_local and not df_p_source is None and not df_p_source.empty:
                # 로컬 Debugging 시 csv 파일 출력
                df_p_source.to_csv(str_output_dir + "/"+str_p_source_name+".csv", encoding="UTF8", index=False)


def _decoration_(func):
    """
    1. 소스 내 함수 실행 시 반복되는 코드를 데코레이터로 변형하여 소스 라인을 줄일 수 있도록 함.
    2. 각 Step을 함수로 실행하는 경우 해당 함수에 뒤따르는 Step log 및 DF 로그, DF 로컬 출력을 데코레이터로 항상 출력하게 함.
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        # 함수 시작 시각
        tm_start = time.time()
        # 함수 실행
        result = func(*args)
        # 함수 종료 시각
        tm_end = time.time()
        # 함수 실행 시간 로그
        logger.Note(p_note=f'[{func.__name__}] Total time is {tm_end - tm_start:.5f} sec.',
                    p_log_level=LOG_LEVEL.debug())
        # Step log 및 DF 로컬 출력 등을 위한 Keywords 변수 확인
        # Step No
        _step_no = kwargs.get('p_step_no')
        _step_desc = kwargs.get('p_step_desc')
        _df_name = kwargs.get('p_df_name')
        _warn_desc = kwargs.get('p_warn_desc')
        _exception_flag = kwargs.get('p_exception_flag')
        # Step log 관련 변수가 입력된 경우 Step log 출력
        if _step_no is not None and _step_desc is not None:
            logger.Step(p_step_no=_step_no, p_step_desc=_step_desc)
        # Warning 메시지가 있는 경우
        if _warn_desc is not None:
            # 함수 실행 결과가 DF이면서 해당 DF가 비어 있는 경우
            if type(result) == pd.DataFrame and result.empty:
                # Exception flag가 확인되고
                if _exception_flag is not None:
                    # Exception flag가 0이면 Warning 로그 출력, 1이면 Exception 발생시킴
                    if _exception_flag == 0:
                        logger.Note(p_note=_warn_desc, p_log_level=LOG_LEVEL.warning())
                    elif _exception_flag == 1:
                        raise Exception(_warn_desc)
        # DF 명이 있는 경우 로그 및 로컬 출력
        if _df_name is not None:
            fn_log_dataframe(result, _df_name)
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
def fn_preprocess(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        결과 칼럼 초기 생성( 0값 반영 ),
        숫자값 칼럼 빈값일 경우 0으로 변환,
        비어 있는 값을 'Y'로 변환
    :param df_p_source: in_BODPort
    :return: DataFrame
    """
    
    # DataFrame 복사
    df_return = df_p_source.copy(deep=True)

    # 결과 칼럼 초기 생성 ( 초기값 0 )
    df_return = df_return.assign(**{
        'BOD Port_Capa Qty(4W)' : 0,
        'BOD Port_Capa Qty(12W)' : 0,
        'BOD Port_Capa Qty(Y-1)' : 0,
        'BOD Port_Capa Qty(Y-1 M)' : 0,
        'BOD Port_Ratio(BOD per Port 12W)' : 0,
        'BOD Port_Ratio(BOD per Port 4W)' : 0,
        'BOD Port_Ratio(BOD per Port Y-1 M)' : 0,
        'BOD Port_Ratio(BOD per Port Y-1)' : 0
    })

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return[
        ['BOD Port_Recent Year Volume CNTR (4W)', 'BOD Port_Recent Year Volume CNTR (12W)',
         'BOD Port_Recent Year Volume CNTR (Y-1)' , 'BOD Port_Recent Year Volume CNTR (Y-1 M)']
    ] = (
        df_return[
            ['BOD Port_Recent Year Volume CNTR (4W)', 'BOD Port_Recent Year Volume CNTR (12W)',
             'BOD Port_Recent Year Volume CNTR (Y-1)' , 'BOD Port_Recent Year Volume CNTR (Y-1 M)']
        ].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    )
    
    # BOD Port_Valid Flag : 비어 있는 값( 대상 ) 을 'Y'로 변환한다.
    df_return['BOD Port_Valid Flag'] = (
        df_return['BOD Port_Valid Flag'].replace(r'^\s*$', np.nan, regex=True).fillna('Y').astype(str)
    )

    return df_return

@_decoration_
def fn_aggregation(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Loading Logistics Port, Discharge Logistics Port 별로 Ocean Capa W_Capa Qty sum() 계산한다.

    :param df_p_source:
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]

    # 입력 파라미터가 비어 있는 경우 비어 있는 입력 DataFrame 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # Loading Logistics Port, Discharge Logistics Port 별로 Ocean Capa W_Capa Qty sum() 계산한다.
    df_return = (
        df_p_source
        .groupby(['Loading Port.[Loading Logistics Port]', 'Discharge Port.[Discharge Logistics Port]'])
        ['Ocean Capa W_Capa Qty']
        .sum()
        .reset_index()
    )
    
    return df_return



@_decoration_
def fn_calculate_ratio_bod_port(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 1.
     Step 1-1)
         Loading Port.[Loading Logistics Port], Discharge Port.[Discharge Logistics Port]별로
         group by 하여 4개 항목 별(4W, 12W, Y-1 M, Y-1) 로 total sum을 구하고
         row 별  recent year volume /total sum 으로 비율을 구하여 BOD per Port Ratio 메저에 반영한다.
         ex) BOD Port_Ratio(BOD per Port 4W) =
         BOD Port_Recent Year Volume CNTR (4W) / total sum(BOD Port_Recent Year Volume CNTR (4W))
                                                 group by(Loading Port.[Loading Logistics Port]
                                                        , Discharge Port.[Discharge Logistics Port])
         Measure.[BOD Port_Recent Year Volume CNTR (4W)]  → Measure.[BOD Port_Ratio(BOD per Port 4W)]
         Measure.[BOD Port_Recent Year Volume CNTR (12W)] → Measure.[BOD Port_Ratio(BOD per Port 12W)]
         Measure.[BOD Port_Recent Year Volume CNTR (Y-1)] → Measure.[BOD Port_Ratio(BOD per Port Y-1)]
         Measure.[BOD Port_Recent Year Volume CNTR (Y-1 M)] → Measure.[BOD Port_Ratio(BOD per Port Y-1 M)]
     Step 1-2)
         BOD 기준으로 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2]별로
         group by 하여 4개 항목 별(4W, 12W, Y-1 M, Y-1)로 total sum을 구하고
         row별 recent year volume /total sum 으로 비율을 구하여 Port per BOD Ratio 메저에 반영한다.
         ex) BOD Port_Ratio(Port per BOD 4W) =
         BOD Port_Recent Year Volume CNTR (4W) / total sum(BOD Port_Recent Year Volume CNTR (4W))
                                                 group by (SubLocation, Location, Activity2)
         메저 생성 1-1)과 동일

    :param df_p_source: df_BODPort
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]

    # 입력 파라미터가 비어 있는 경우 비어 있는 입력 DataFrame 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # DataFrame 복사
    df_return = df_p_source.copy(deep=True)

    # 칼럼 선언
    pre_fix = 'BOD Port_Recent Year Volume CNTR '
    col_recent_year_volume_4W = pre_fix +'(4W)'
    col_recent_year_volume_12W = pre_fix + '(12W)'
    col_recent_year_volume_Y1 = pre_fix + '(Y-1)'
    col_recent_year_volume_Y1M = pre_fix + '(Y-1 M)'

    list_col_volume = [col_recent_year_volume_4W, col_recent_year_volume_12W, col_recent_year_volume_Y1,
                       col_recent_year_volume_Y1M]

    # Loading Logistics Port, Discharge Logistics Port 별로
    # BOD Port_Recent Year Volume CNTR (12W), BOD Port_Recent Year Volume CNTR (4W),
    # BOD Port_Recent Year Volume CNTR (Y-1), BOD Port_Recent Year Volume CNTR (Y-1 M) total sum 값을 구한다.
    df_return[
        ['Tot Port Volume (4W)', 'Tot Port Volume (12W)', 'Tot Port Volume (Y-1)', 'Tot Port Volume (Y-1 M)']
    ] = (
        df_return
        .groupby(
            ['Loading Port.[Loading Logistics Port]', 'Discharge Port.[Discharge Logistics Port]']
        )[list_col_volume]
        .transform('sum')
    )

    # 1-1) BOD per Port Ratio 계산
    df_return['BOD Port_Ratio(BOD per Port 4W)'] = np.where(
        df_return['Tot Port Volume (4W)'] == 0,
        0,
        df_return[col_recent_year_volume_4W] / df_return['Tot Port Volume (4W)']
    )
    df_return['BOD Port_Ratio(BOD per Port 12W)'] = np.where(
        df_return['Tot Port Volume (12W)'] == 0,
        0,
        df_return[col_recent_year_volume_12W] / df_return['Tot Port Volume (12W)']
    )
    df_return['BOD Port_Ratio(BOD per Port Y-1)'] = np.where(
        df_return['Tot Port Volume (Y-1)'] == 0,
        0,
        df_return[col_recent_year_volume_Y1] / df_return['Tot Port Volume (Y-1)']
    )
    df_return['BOD Port_Ratio(BOD per Port Y-1 M)'] = np.where(
        df_return['Tot Port Volume (Y-1 M)'] == 0,
        0,
        df_return[col_recent_year_volume_Y1M] / df_return['Tot Port Volume (Y-1 M)']
    )

    # Sub Location, Location, Activity2 별로
    # BOD Port_Recent Year Volume CNTR (12W), BOD Port_Recent Year Volume CNTR (4W),
    # BOD Port_Recent Year Volume CNTR (Y-1), BOD Port_Recent Year Volume CNTR (Y-1 M) total sum 값을 구한다.
    df_return[
        ['Tot Volume (4W)', 'Tot Volume (12W)', 'Tot Volume (Y-1)', 'Tot Volume (Y-1 M)']
    ] = (
        df_return
        .groupby(
            ['Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]']
        )[list_col_volume]
        .transform('sum')
    )

    # 1-2) Port per BOD Ratio 계산
    df_return['BOD Port_Ratio(Port per BOD 4W)'] = np.where(
        df_return['Tot Volume (4W)'] == 0,
        0,
        df_return[col_recent_year_volume_4W] / df_return['Tot Volume (4W)']
    )
    df_return['BOD Port_Ratio(Port per BOD 12W)'] = np.where(
        df_return['Tot Volume (12W)'] == 0,
        0,
        df_return[col_recent_year_volume_12W] / df_return['Tot Volume (12W)']
    )
    df_return['BOD Port_Ratio(Port per BOD Y-1)'] = np.where(
        df_return['Tot Volume (Y-1)'] == 0,
        0,
        df_return[col_recent_year_volume_Y1] / df_return['Tot Volume (Y-1)']
    )
    df_return['BOD Port_Ratio(Port per BOD Y-1 M)'] = np.where(
        df_return['Tot Volume (Y-1 M)'] == 0,
        0,
        df_return[col_recent_year_volume_Y1M] / df_return['Tot Volume (Y-1 M)']
    )

    return df_return


@_decoration_
def fn_merge_bodPort_oceanCapa(df_p_source:pd.DataFrame, df_ocean_capa:pd.DataFrame) -> pd.DataFrame:
    """
    STEP3. STEP1의 df와 in_OceanCapa를
           Loading Port.[Loading Logistics Port], Discharge Port.[Discharge Logistics Port] 기준으로
           left join하여
           Ocean Capa W_Capa Qty *  BOD Port_Ratio(4W, 12W, Y1, Y1M) 결과값을
           BOD Port_Capa Qty(4W), BOD Port_Capa Qty(12W), BOD Port_Capa Qty(Y-1), BOD Port_Capa Qty(Y-1 M)
           메저에 반영한다.

    :param df_p_source: df_BODPort_cal
    :param df_ocean_capa: in_OceanCapa
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]

    # 왼쪽 또는 오른쪽 DataFrame 비어 있는 경우 왼쪽 DataFrame을 리턴
    if df_p_source.empty or df_ocean_capa.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_ocean_capa)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # df_BODPort, df_OceanCapa Merge
    df_return = (
        df_p_source
        .merge(df_ocean_capa, how='left',
               on=['Loading Port.[Loading Logistics Port]', 'Discharge Port.[Discharge Logistics Port]'],
               indicator=True)
    )
    
    # 없는 주차 Capa Qty 0 처리
    df_return['Ocean Capa W_Capa Qty'] = (
        df_return['Ocean Capa W_Capa Qty'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    )

    # Capa Qty 생성
    # Tp mode 기준으로 vessel 제외건들은 grdate 기준 4w/12w/last year/same month last year 건 쪽에 capa  값 null
    df_return['BOD Port_Capa Qty(4W)'] = (
        np.where(df_return['Activity2.[Activity2]'] == 'VESSEL',
                 df_return['BOD Port_Ratio(BOD per Port 4W)'] * df_return['Ocean Capa W_Capa Qty'],
                 np.nan)
    )
    df_return['BOD Port_Capa Qty(12W)'] = (
        np.where(df_return['Activity2.[Activity2]'] == 'VESSEL',
                 df_return['BOD Port_Ratio(BOD per Port 12W)'] * df_return['Ocean Capa W_Capa Qty'],
                 np.nan)
    )
    df_return['BOD Port_Capa Qty(Y-1)'] = (
        np.where(df_return['Activity2.[Activity2]'] == 'VESSEL',
                 df_return['BOD Port_Ratio(BOD per Port Y-1)'] * df_return['Ocean Capa W_Capa Qty'],
                 np.nan)
    )
    df_return['BOD Port_Capa Qty(Y-1 M)'] = (
        np.where(df_return['Activity2.[Activity2]'] == 'VESSEL',
                 df_return['BOD Port_Ratio(BOD per Port Y-1 M)'] * df_return['Ocean Capa W_Capa Qty'],
                 np.nan)
    )

    return df_return


@_decoration_
def fn_output_formatter(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        최종 Output 정리
    :param df_p_source: df_BODPort_Merged
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # Version 
    df_p_source['Version.[Version Name]'] = Param_OUT_VERSION
    
    # 칼럼 정리
    df_return = df_p_source[OUTPUT_COL]

    return df_return


@_decoration_
def fn_set_header() -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """
    df_return = pd.DataFrame(columns=OUTPUT_COL)

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    pd.set_option('display.width', 400)
    pd.set_option('display.max_columns', None)

    # Output 테이블 선언
    out_BODPort = pd.DataFrame()
    try:
        ################################################################################################################
        # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
        ################################################################################################################
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = 'N'

            in_BODPort = pd.read_csv(str_input_dir + "/in_BODPort.csv", encoding="UTF8")
            in_OceanCapa = pd.read_csv(str_input_dir + "/in_OceanCapa.csv", encoding="UTF8")

            # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'

        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())

        # 입력 테이블 점검 및 로그
        fn_check_input_table(in_BODPort, 'in_BODPort', '1')
        fn_check_input_table(in_OceanCapa, 'in_OceanCapa', '1')

        # OUTPUT column
        OUTPUT_COL = [
            'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
            'Loading Port.[Loading Port]', 'Discharge Port.[Discharge Port]', 'Dest Port.[Dest Port]',
            'BOD Port_Capa Qty(4W)', 'BOD Port_Capa Qty(12W)', 'BOD Port_Capa Qty(Y-1)', 'BOD Port_Capa Qty(Y-1 M)',
            'BOD Port_Ratio(BOD per Port 4W)', 'BOD Port_Ratio(BOD per Port 12W)',
            'BOD Port_Ratio(BOD per Port Y-1)', 'BOD Port_Ratio(BOD per Port Y-1 M)',
            'BOD Port_Ratio(Port per BOD 4W)', 'BOD Port_Ratio(Port per BOD 12W)', 'BOD Port_Ratio(Port per BOD Y-1)',
            'BOD Port_Ratio(Port per BOD Y-1 M)', 'BOD Port_Valid Flag'
        ]

        ################################################################################################################
        # STEP 0. 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 작업 진행함.
        ################################################################################################################
        # 선처리 작업
        dict_log = {
            'p_step_no': 10,
            'p_step_desc': 'STEP 0-1. 전처리(in_LoadingDirOrderMgmt): 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 '
                           '작업 진행함.',
            'p_df_name': 'df_BODPort'
        }
        df_BODPort = fn_preprocess(in_BODPort, **dict_log)

        dict_log = {
            'p_step_no': 20,
            'p_step_desc': 'STEP 0-2. Aggregation(in_OceanCapa): in_OceanCapa Aggregation.',
            'p_df_name': 'df_OceanCapa'
        }
        df_OceanCapa = fn_aggregation(in_OceanCapa, **dict_log)

        ################################################################################################################
        # STEP 1.
        #  Step 1-1)
        #       Loading Port.[Loading Logistics Port], Discharge Port.[Discharge Logistics Port]별로
        #       group by 하여 4개 항목 별(4W, 12W, Y-1 M, Y-1) 로 total sum을 구하고
        #       row 별  recent year volume /total sum 으로 비율을 구하여 BOD per Port Ratio 메저에 반영한다.
        #       ex) BOD Port_Ratio(BOD per Port 4W) =
        #       BOD Port_Recent Year Volume CNTR (4W) / total sum(BOD Port_Recent Year Volume CNTR (4W))
        #                                               group by(Loading Port.[Loading Logistics Port]
        #                                                      , Discharge Port.[Discharge Logistics Port])
        #       Measure.[BOD Port_Recent Year Volume CNTR (4W)]  → Measure.[BOD Port_Ratio(BOD per Port 4W)]
        #       Measure.[BOD Port_Recent Year Volume CNTR (12W)] → Measure.[BOD Port_Ratio(BOD per Port 12W)]
        #       Measure.[BOD Port_Recent Year Volume CNTR (Y-1)] → Measure.[BOD Port_Ratio(BOD per Port Y-1)]
        #       Measure.[BOD Port_Recent Year Volume CNTR (Y-1 M)] → Measure.[BOD Port_Ratio(BOD per Port Y-1 M)]
        #
        #   Step 1-2)
        #       BOD 기준으로 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2]별로
        #       group by 하여 4개 항목 별(4W, 12W, Y-1 M, Y-1)로 total sum을 구하고
        #       row별 recent year volume /total sum 으로 비율을 구하여 Port per BOD Ratio 메저에 반영한다.
        #       ex) BOD Port_Ratio(Port per BOD 4W) =
        #       BOD Port_Recent Year Volume CNTR (4W) / total sum(BOD Port_Recent Year Volume CNTR (4W))
        #                                               group by (SubLocation, Location, Activity2)
        #       메저 생성 1-1)과 동일
        ################################################################################################################
        dict_log = {
            'p_step_no': 100,
            'p_step_desc': 'STEP 1. Step 1-1)Loading Port.[Loading Logistics Port], Discharge Port.[Discharge Logistics Port]'
                           '별로 group by 하여 4개 항목 별로 total sum을 구하고 '
                           'row별 recent year volume /total sum 으로 비율을 구하여 BOD per Port Ratio 메저에 반영 한다. '
                           'Step 1-2) BOD 기준으로 [Sub Location].[Sub Location], [Location].[Location], '
                           '[Activity2].[Activity2]별로 group by 하여 4개 항목 별로 total sum을 구하고'
                           'row별 recent year volume /total sum 으로 비율을 구하여 Port per BOD Ratio 메저에 반영한다.',
            'p_df_name': 'df_BODPort_cal'
        }
        df_BODPort_cal = fn_calculate_ratio_bod_port(df_BODPort,  **dict_log)

        ################################################################################################################
        # STEP2. STEP1의 df와 in_OceanCapa를
        #        Loading Port.[Loading Logistics Port], Discharge Port.[Discharge Logistics Port] 기준으로
        #        left join하여
        #        Ocean Capa W_Capa Qty *  BOD Port_Ratio(4W, 12W, Y1, Y1M) 값을
        #        BOD Port_Capa Qty(4W), BOD Port_Capa Qty(12W), BOD Port_Capa Qty(Y-1), BOD Port_Capa Qty(Y-1 M)
        #        메저에 반영 한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 200,
            'p_step_desc': 'STEP2. STEP1의 df와 df_OceanCapa를 '
                           'Loading Port.[Loading Logistics Port], Discharge Port.[Discharge Logistics Port] 기준으로'
                           'left join하여 '
                           'Ocean Capa W_Capa Qty *  BOD Port_Ratio(4W, 12W, Y1, Y1M) 값을'
                           'BOD Port_Capa Qty(4W), BOD Port_Capa Qty(12W), BOD Port_Capa Qty(Y-1), BOD Port_Capa Qty(Y-1 M)'
                           '메저에 반영한다.',
            'p_df_name': 'df_BODPort_Merged'
        }
        df_BODPort_Merged = fn_merge_bodPort_oceanCapa(df_BODPort_cal, df_OceanCapa, **dict_log)

        ################################################################################################################
        # 최종 Output 정리
        ################################################################################################################
        dict_log = {
            'p_step_no': 777,
            'p_step_desc': '최종 Output 정리.',
            'p_df_name': 'out_BODPort'
        }
        out_BODPort = fn_output_formatter(df_BODPort_Merged, **dict_log)

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_BODPort = None
            raise Exception(e)
        else:
            if out_BODPort.empty:
                out_BODPort = fn_set_header()
                fn_log_dataframe(out_BODPort, 'out_BODPort')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_BODPort.empty:
            out_BODPort = fn_set_header()
            fn_log_dataframe(out_BODPort, 'out_BODPort')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')

