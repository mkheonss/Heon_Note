"""
* 프로그램명
    - PY_UI_LoadingDirOrderMgmtSKU_REG

* 내용
    -
* 변경이력
    - 2025.03.20 / Miss Lee / Create

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_LD, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
    - in_LoadingDirOrderMgmt :
        select (Version.[Version Name]);

* Output Tables
    -

* Flow Summary


* Validation :


* Execution :
    1. 기존 메저 데이터 삭제(nullify)


    2. Plugin Call하여 신규 MG 생성
    1) LightWeight


    2) MediumWeight
    EXEC plugin instance [PY_UI_LoadingDirOrderMgmtSKU_REG]
        for measures { [Loading Dir Order Mgmt_Single Item Cntr Status] }
    using scope ([Version].[Version Name].[CWV] * [Personnel].[Email].[aaa])
    using arguments {(ExecutionMode, "MediumWeight")
                  , (Param_OUT_VERSION, "CWV_MP")
                  , (Param_SKU_Constraints, "N")
                  , (Param_Adjust_Option1, "MIN")
                  , (Param_Adjust_Option2 , "Min Item Change")
                  , (MaxSliceTableCells, 200000000)
                  , (MaxConcurrency, 1 )
                  , (IncludeNullRows, False)
                  , ([Param.o9_sys_log_level], "DEBUG")
                  }
    ;
"""
import inspect
import os.path
import time
import pandas as pd
import traceback
import numpy as np
from NSCMCommon import NSCMCommon as common


########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_LoadingDirOrderMgmtSKU_REG"
str_input_dir = "Input/UILoadingDirOrderMgmtSKUREG"
str_output_dir = "Output/UILoadingDirOrderMgmtSKUREG"
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
        if is_local and not df_p_source.empty and flag_csv:
            # 로컬 Debugging 시 csv 파일 출력
            df_p_source.to_csv(str_output_dir + "/"+str_p_source_name+".csv", encoding="UTF8", index=False)
    else:
        # 최종 Output 테이블인 경우에는 무조건 로그 출력
        if is_output:
            logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
            if is_local and not df_p_source.empty:
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
def fn_set_header() -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """
    list_col = ['Version.[Version Name]', 'Location.[Location]', 'Item.[Item]', 'Item Site Asn_Stage',
                'Item Site Asn_Item Group']
    df_return = pd.DataFrame(columns=list_col)

    return df_return

if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_LoadingDirOrderMgmt = pd.DataFrame()
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
            Param_SKU_Constraints = 'N'
            Param_Adjust_Option1 = 'MIN'
            Param_Adjust_Option2 = 'Min Item Change'

            in_LoadingDirOrderMgmt = pd.read_csv(str_input_dir + "/in_LoadingDirOrderMgmt.csv", encoding="UTF8")

            # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')

        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        if Param_SKU_Constraints is None or Param_SKU_Constraints.strip() == '':
            Param_SKU_Constraints = 'N'

        if Param_Adjust_Option1 is None or Param_Adjust_Option1.strip() == '':
            Param_Adjust_Option1 = 'MIN'

        if Param_Adjust_Option2 is None or Param_Adjust_Option2.strip() == '':
            Param_Adjust_Option2 = 'Min Item Change'

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())
        
        # python 명 실행
        logger.Note(p_note='★★★★★★★★★★★★★★★★★★★★★★★★★Python name  ::: PY_UI_LoadingDirOrderMgmtSKU_REG', p_log_level=LOG_LEVEL.debug())


    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            raise Exception(e)
        else:
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        logger.Finish()

    finally:
        if out_LoadingDirOrderMgmt.empty:
            out_LoadingDirOrderMgmt = fn_set_header()
            fn_log_dataframe(out_LoadingDirOrderMgmt, 'out_LoadingDirOrderMgmt')
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')
