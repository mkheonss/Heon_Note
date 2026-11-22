"""
* 프로그램명
    - PY_UI_WarehouseCapaUsage_REG.py

* 내용
    -
* 변경이력
    - 2025.12.26 / Miss Lee / Create

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를 결정하는 파라미터

* Input Tables
    - in_WHContractCapa :
        Select (
                  [Version].[Version Name]
                * [Time].[Week]
                * [Warehouse].[SCM Warehouse]
                ) on row,
                ({
                    Measure.[WH Contract Capa W_CBM]
                }) on column;

    - in_SalesPSIActual :
        (
            Select (
                      [Version].[Version Name]
                    * [Sub Location].[Sub Location]
                    * [Item].[Item]
                    * [Item].[Product Group]
                    * [Location].[Location]
                    * [Time].[Week]
                    * [Activity2].[Activity2]
                    ) on row,
                    ({
                       Measure.[Sales PSI Actual W_EOH]
                    ,  Measure.[WH Mapping_Map Status]
                    ,  Measure.[WH Mapping_Valid Flag]
                    ,  Measure.[WH Mapping_SCM Warehouse]
                    ,  Measure.[Item ULD_CBM]
                    }) on column
        ).filter(
                   Measure.[WH Mapping_Map Status] == "CON" // warehouse mapping 화면에서 'Confirm'
                && Measure.[WH Mapping_Valid Flag] == "Y"   // valid flag == 'Y'
        );


* Output Tables
    - out_WHCapaUsage:
        Select (
                  [Version].[Version Name]
                * [Item].[Product Group]
                * [Location].[Location]
                * [Time].[Week]
                * [Warehouse].[SCM Warehouse]
                ) on row,
                ({
                  Measure.[Warehouse Capa Usage_EOH]
                , Measure.[Warehouse Capa Usage_EOH CBM]
                , Measure.[Warehouse Capa Usage_Warehouse Capacity]
                }) on column;


* Flow Summary
    STEP 1. Warehouse Capa Usage_Warehouse Capacity
           : warehouse contract화면의 주차별 Capa값 반영하는데,
             Region,Nation,NSCM W/H기준으로 AGRREGATION된 주차별 CAPA를 반영한다(site에 상관없이 동일함)

    STEP2. Warehouse Capa Usage_EOH
          : Sales PSI Actual W_EOH 값을 연계 SITE, Product Group 기준으로 AGGREGATION된 값을 반영한다.
            warehouse mapping 화면에서 Location에 해당하는
            SCM Warehouse(Map Status == 'CON' (confirm), Valid Flag =='Y'인 SCM warehouse 추출) 을 가져온다.

    STEP3. Warehouse Capa Usage_EOH CBM
         : Item ULD에서 Item별 CBM인 Item ULD_CBM을 찾아서,
           Sales PSI Actual W_EOH와 곱한뒤 SITE, Product Group 기준으로 AGGREGATION된 값을 반영한다.

* Validation :

* Execution :
    1. 기존 메저 데이터 삭제(delete)
    delete data for model [Warehouse Capacity Usage] where { &CWV_MP };

    2. Plugin Call하여 신규 MG 생성
    1) LightWeight
        EXEC plugin instance [PY_UI_WarehouseCapaUsage_REG]
            for measures { [Warehouse Capa Usage_EOH]
                         , [Warehouse Capa Usage_EOH CBM]
                         , [Warehouse Capa Usage_Warehouse Capacity]
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
        EXEC plugin instance [PY_UI_WarehouseCapaUsage_REG]
            for measures { [Warehouse Capa Usage_EOH]
                         , [Warehouse Capa Usage_EOH CBM]
                         , [Warehouse Capa Usage_Warehouse Capacity]
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
str_instance = "PY_UI_WarehouseCapaUsage_REG"
str_input_dir = "Input/UIWarehouseCapaUsageREG"
str_output_dir = "Output/UIWarehouseCapaUsageREG"
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
        숫자값 칼럼 빈값일 경우 0으로 변환
        칼럼 rename
    :param df_p_source: in_SalesPSIActual
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

    # DataFrame 복사
    df_return = df_p_source.copy(deep=True)

    # Rename
    df_return = df_return.rename(columns={'WH Mapping_SCM Warehouse' : 'Warehouse.[SCM Warehouse]'})

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return[['Sales PSI Actual W_EOH', 'Item ULD_CBM']] = (
        df_return[['Sales PSI Actual W_EOH', 'Item ULD_CBM']].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    )

    return df_return


@_decoration_
def fn_calculate_eoh_cbm(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 1. in_SalesPSIActual 테이블의
           1) Sales PSI Actual W_EOH * Item ULD_CBM 한 값을
             [Item].[Product Group], [Location].[Location], [Time].[Week], [Warehouse].[SCM Warehouse] 별로 sum() 하여
             Warehouse Capa Usage_EOH CBM 칼럼 생성 한다.
          2) Sales PSI Actual W_EOH 칼럼을
             [Item].[Product Group], [Location].[Location], [Time].[Week], [Warehouse].[SCM Warehouse] 별로 sum() 하여
             Warehouse Capa Usage_EOH 칼럼 생성 반영 한다.

    :param df_p_source: in_SalesPSIActual
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

    # DataFrame Copy
    df_return = df_p_source.copy(deep=True)

    # Warehouse Capa Usage_EOH CBM 칼럼 생성
    df_return['Warehouse Capa Usage_EOH CBM'] = df_return['Sales PSI Actual W_EOH'] * df_return['Item ULD_CBM']

    # Warehouse Capa Usage_EOH 칼럼 생성
    df_return = df_return.rename(columns={'Sales PSI Actual W_EOH' : 'Warehouse Capa Usage_EOH'})

    # Item.[Prod Group] 별로 sum
    list_col = ['Item.[Product Group]', 'Location.[Location]', 'Time.[Week]', 'Warehouse.[SCM Warehouse]']

    df_return = (
        df_return
        .groupby(list_col)
        .agg({'Warehouse Capa Usage_EOH': 'sum','Warehouse Capa Usage_EOH CBM': 'sum'})
        .reset_index()
    )

    return df_return


@_decoration_
def fn_merge_psi_contract_capa(df_p_source: pd.DataFrame, df_contract_capa:pd.DataFrame) -> pd.DataFrame:
    """
    STEP 2. STEP1의 df와 in_WHContractCapa를 [Time].[Week], [Warehouse].[SCM Warehouse]별로 left join 하여
            WH Contract Capa W_CBM 칼럼으로 Warehouse Capa Usage_Warehouse Capacity 생성 한다.

    :param df_p_source: df_SalesPSIActual_cal
    :param df_contract_capa:  in_WHContractCapa
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

    # Merge
    df_return = df_p_source.merge(df_contract_capa, how='left', on=['Time.[Week]', 'Warehouse.[SCM Warehouse]'])

    # Rename
    df_return = df_return.rename(columns={'WH Contract Capa W_CBM': 'Warehouse Capa Usage_Warehouse Capacity'})

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return['Warehouse Capa Usage_Warehouse Capacity'] = (
        df_return['Warehouse Capa Usage_Warehouse Capacity'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
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
    df_return = df_p_source[
        ['Version.[Version Name]', 'Item.[Product Group]', 'Location.[Location]', 'Time.[Week]', 'Warehouse.[SCM Warehouse]',
         'Warehouse Capa Usage_EOH', 'Warehouse Capa Usage_EOH CBM', 'Warehouse Capa Usage_Warehouse Capacity']
    ]

    return df_return


@_decoration_
def fn_set_header() -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """
    col_output = ['Version.[Version Name]', 'Item.[Product Group]', 'Location.[Location]', 'Time.[Week]',
                  'Warehouse.[SCM Warehouse]',
                  'Warehouse Capa Usage_EOH', 'Warehouse Capa Usage_EOH CBM', 'Warehouse Capa Usage_Warehouse Capacity']
    df_return = pd.DataFrame(columns=col_output)

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    pd.set_option('display.width', 400)
    pd.set_option('display.max_columns', None)

    # Output 테이블 선언
    out_WHCapaUsage = pd.DataFrame()
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

            in_WHContractCapa = pd.read_csv(str_input_dir + "/in_WHContractCapa.csv", encoding="UTF8")
            in_SalesPSIActual = pd.read_csv(str_input_dir + "/in_SalesPSIActual.csv", encoding="UTF8")

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
        fn_check_input_table(in_WHContractCapa, 'in_WHContractCapa', '1')
        fn_check_input_table(in_SalesPSIActual, 'in_SalesPSIActual', '1')

        ################################################################################################################
        # STEP 0. 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 작업 진행함.
        ################################################################################################################
        # 선처리 작업
        dict_log = {
            'p_step_no': 10,
            'p_step_desc': 'STEP 0-1. 전처리(in_SalesPSIActual): 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 '
                           '작업 진행함.',
            'p_df_name': 'df_SalesPSIActual'
        }
        df_SalesPSIActual = fn_preprocess(in_SalesPSIActual, **dict_log)

        ################################################################################################################
        # STEP 1. in_SalesPSIActual 테이블의
        # 1) Sales PSI Actual W_EOH * Item ULD_CBM 한 값을
        #    [Item].[Product Group], [Location].[Location], [Time].[Week], [Warehouse].[SCM Warehouse] 별로 sum() 하여
        #    Warehouse Capa Usage_EOH CBM 칼럼 생성 한다.
        # 2) Sales PSI Actual W_EOH 칼럼을
        #    [Item].[Product Group], [Location].[Location], [Time].[Week], [Warehouse].[SCM Warehouse] 별로 sum() 하여
        #    Warehouse Capa Usage_EOH 칼럼 생성 반영 한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 100,
            'p_step_desc': 'STEP 1. in_SalesPSIActual 테이블의 '
                           '1) Sales PSI Actual W_EOH * Item ULD_CBM 한 값을'
                           '[Item].[Product Group], [Location].[Location], [Time].[Week], [Warehouse].[SCM Warehouse] '
                           '별로 sum() 하여  Warehouse Capa Usage_EOH CBM 칼럼 생성한다.'
                           '2) Sales PSI Actual W_EOH 칼럼을'
                           '[Item].[Product Group], [Location].[Location], [Time].[Week], [Warehouse].[SCM Warehouse] '
                           '별로 sum() 하여 Warehouse Capa Usage_EOH 칼럼 생성 반영한다.',
            'p_df_name': 'df_SalesPSIActual_cal'
        }
        df_SalesPSIActual_cal = fn_calculate_eoh_cbm(df_SalesPSIActual, **dict_log)

        ################################################################################################################
        # STEP 2. STEP1의 df와 in_WHContractCapa를 [Time].[Week], [Warehouse].[SCM Warehouse]별로 left join 하여
        #         WH Contract Capa W_CBM 칼럼으로 Warehouse Capa Usage_Warehouse Capacity 생성한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 200,
            'p_step_desc': 'STEP 2. STEP1의 df와 in_WHContractCapa를 [Time].[Week], [Warehouse].[SCM Warehouse]별로 '
                           'left join 하여 WH Contract Capa W_CBM 칼럼으로 Warehouse Capa Usage_Warehouse Capacity 생성한다.',
            'p_df_name': 'df_SalesPSIActual_merged'
        }
        df_SalesPSIActual_merged = fn_merge_psi_contract_capa(df_SalesPSIActual_cal, in_WHContractCapa, **dict_log)

        ################################################################################################################
        # 최종 Output 정리
        ################################################################################################################
        dict_log = {
            'p_step_no': 777,
            'p_step_desc': '최종 Output 정리.',
            'p_df_name': 'out_WHCapaUsage'
        }
        out_WHCapaUsage = fn_output_formatter(df_SalesPSIActual_merged, **dict_log)

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_WHCapaUsage = None
            raise Exception(e)
        else:
            if out_WHCapaUsage.empty:
                out_WHCapaUsage = fn_set_header()
                fn_log_dataframe(out_WHCapaUsage, 'out_WHCapaUsage')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_WHCapaUsage.empty:
            out_WHCapaUsage = fn_set_header()
            fn_log_dataframe(out_WHCapaUsage, 'out_WHCapaUsage')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')

