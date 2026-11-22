"""
* 프로그램명
    - PY_UI_WHMapping_REG

* 내용
    - [Location].[Location] 기준으로 전체 Location에 대해 WH Mapping에 없는 것만 WH Mapping에 insert

* 변경이력
    - 2025.12.31 / Kang Gyeonghun / Create
    - 2026.01.22 / Kang Gyeonghun / Update
      : 설계 변경점 적용
      - Input 쿼리 변경
      - Location을 필터링하고 해당 Location에 대해서만 로직 적용

* Script Params
    - Param_OUT_VERSION: 기본값 : CWV_MP, 호출 시에, 결과 데이터의 Version Name을 별도로 지정하는 데에 사용.
    - Param_Exception_Flag: 기본값: N, 파이썬 모듈 실행 시 발생하는 Exception을 무시한 것인지를 정하는 데에 사용.

* Input Tables
    - in_Location
        Select ([Location].[Location].filter(#.[Location Valid Flag] == True)
             * [Location].[Location Type] * [Location].[Site Group3]) on row
        include memberproperties
              { [Location].[Location], [Shipment Type], [DisplayName] }
              { [Location].[Site Group3], [Site Group3 Valid Flag] }
        ;

    - in_WHMapping
        Select ([Location].[Location]) on row
             , ({Measure.[WH Mapping_Map Status]}) on column
         where {[Version].[Version Name]}
        ;

* Output Tables
    - out_WHMapping
        Select ([Version].[Version Name] * [Location].[Location]) on row
             , ({Measure.[WH Mapping_Map Status], Measure.[WH Mapping_Valid Flag]
             , Measure.[WH Mapping_Creation Time], Measure.[WH Mapping_Created By]}) on column
        ;

* Flow Summary
    Step 0.
        (1) in_Location에서 아래의 조건으로 데이터를 추출한다.
        Location.[Site Group3 Valid Flag] == true & Location.[Shipment Type] == "INDIR" &
        Location.[Location Type] == "DC" & Location.[Location Valid Flag] == true
        (2) in_Location에서 위의 조건에 속하지 않은 데이터 중에서
        Location.[DisplayName]이 "_SS"로 끝나거나 "_SS("를 포함하는 데이터를 추출하여 (1)의 데이터에 병합한다.

    Step 1. in_Location에 in_WHMapping 테이블을 Left Join한 후 in_Location에만 있는 데이터를 추출하여 df_WHMapping를 만든다.

    Step 2. df_WHMapping에 대해 아래와 같이 설정한다.
        WH Mapping_Map Status = 'REQ'
        WH Mapping_Valid Flag = 'N'
        WH Mapping_Creation Time = SYSDATE
        WH Mapping_Created By = PYTHON 명

    Step 3. out_WHMapping 형식에 맞도록 구성한다.

* Validation :

* Execution
    EXEC plugin instance [PY_UI_WHMapping_REG]
         for measures {[WH Mapping_Map Status]}
         using scope ([Version].[Version Name].[CWV_MP])
         using arguments {(ExecutionMode, "MediumWeight")
                       , (Param_OUT_VERSION, "CWV_MP")
                       , (Param_Exception_Flag, "N")
                       , (MaxSliceTableCells, 200000000)
                       , (MaxConcurrency, 1)
                       , (IncludeNullRows, False)
                       , ([Param.o9_sys_log_level], "DEBUG")
         }
    ;

    // 데이터 삭제

* Where Used

* 결과 검증
"""
import os
import time
import inspect
import traceback
import pandas as pd
import datetime
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_WHMapping_REG'
str_input_dir = "Input/UIWHMappingREG"
str_output_dir = "Output/UIWHMappingREG"
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
    # out_WHMapping
    df_return = pd.DataFrame(columns=[{
        "Version.[Version Name]": [], "Location.[Location]": [], "WH Mapping_Map Status": [],
        "WH Mapping_Valid Flag": [], "WH Mapping_Creation Time": [], "WH Mapping_Created By": []
    }])

    return df_return


@_decoration_
def fn_filtered_location(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 0.
    (1) in_Location에서 아래의 조건으로 데이터를 추출한다.
    Location.[Site Group3 Valid Flag] == true & Location.[Shipment Type] == "INDIR" &
    Location.[Location Type] == "DC" & Location.[Location Valid Flag] == true
    (2) in_Location에서 위의 조건에 속하지 않은 데이터 중에서
    Location.[DisplayName]이 "_SS"로 끝나거나 "_SS("를 포함하는 데이터를 추출하여 (1)의 데이터에 병합한다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # (1) in_Location에서 아래의 조건으로 데이터를 추출한다.
    # Location.[Site Group3 Valid Flag] == true & Location.[Shipment Type] == "INDIR" &
    # Location.[Location Type] == "DC" & Location.[Location Valid Flag] == true
    list_where_site_group3_valid = (df_p_source["Location.[Site Group3 Valid Flag]"] == True)
    list_where_indir = (df_p_source["Location.[Shipment Type]"] == "INDIR")
    list_where_dc = (df_p_source["Location.[Location Type]"] == "DC")
    list_where_first = (list_where_site_group3_valid & list_where_indir & list_where_dc)
    df_return_first = df_p_source[list_where_first].copy(deep=True)
    df_return_remain = df_p_source[~list_where_first].copy(deep=True)

    # DisplayName의 경우 서버와 로컬이 명칭이 달라 상황에 맞게 변경할 수 있도록 변수에 저장
    if is_local:
        str_location_name = "Location.[DisplayName]"
    else:
        str_location_name = "Location.[Location$DisplayName]"


    if not df_return_remain.empty and len(df_return_remain) > 0:
        # (2) in_Location에서 위의 조건에 속하지 않은 데이터 중에서
        # Location.[DisplayName]이 "_SS"로 끝나거나 "_SS("를 포함하는 데이터를 추출
        list_where_ss_a = (df_return_remain[str_location_name].str.endswith("_SS"))
        list_where_ss_b = (df_return_remain[str_location_name].str.contains("_SS\("))
        list_where_second = (list_where_ss_a | list_where_ss_b)
        df_return_second = df_return_remain[list_where_second].copy(deep=True)

        # 데이터 병합
        df_return = pd.concat([df_return_first, df_return_second])
    else:
        df_return = df_return_first.copy(deep=True)

    # Debugging용
    fn_log_dataframe(df_return, "df_location")
    # 필요함 컬럼만 남김
    df_return = df_return[["Location.[Location]"]]

    return df_return


@_decoration_
def fn_get_new_data(df_p_source: pd.DataFrame, df_p_wh_mapping: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1. in_Location에 in_WHMapping 테이블을 Left Join 후 in_Location에만 있는 데이터를 추출하여 df_WHMapping를 만든다.
    :param df_p_source: in_Location
    :param df_p_wh_mapping: in_WHMapping
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # in_Location에 in_WHMapping 테이블을 Left Join
    df_return = pd.merge(df_p_source, df_p_wh_mapping, on="Location.[Location]", how="left", indicator=True)
    # in_Location에만 있는 데이터 추출
    list_where_new = (df_return["_merge"] == "left_only")
    df_return = df_return[list_where_new].copy(deep=True)

    df_return.drop(columns=["WH Mapping_Map Status", "_merge"], inplace=True)

    return df_return


@_decoration_
def fn_set_wh_mapping(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 2. df_WHMapping에 대해 아래와 같이 설정한다.
        WH Mapping_Map Status = 'REQ'
        WH Mapping_Valid Flag = 'N'
        WH Mapping_Creation Time = SYSDATE
        WH Mapping_Created By = PYTHON 명
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # Step 2. df_WHMapping에 대해 아래와 같이 설정한다.
    # WH Mapping_Map Status = 'REQ'
    # WH Mapping_Valid Flag = 'N'
    # WH Mapping_Creation Time = SYSDATE
    # WH Mapping_Created By = PYTHON 명
    df_return = df_return.assign(**{
        "Version.[Version Name]": Param_OUT_VERSION,
        "WH Mapping_Map Status": "REQ",
        "WH Mapping_Valid Flag": "N",
        "WH Mapping_Creation Time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "WH Mapping_Created By": "System"
    })

    return df_return


@_decoration_
def fn_output_formatter(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3. out_WHMapping 형식에 맞도록 구성한다.
    :param df_p_source: df_out_WHMapping
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # Output 형식으로 만들기
    df_return = (
        df_p_source)[["Version.[Version Name]", "Location.[Location]", "WH Mapping_Map Status", "WH Mapping_Valid Flag",
                      "WH Mapping_Creation Time", "WH Mapping_Created By"]].copy(deep=True)

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_WHMapping = pd.DataFrame()
    try:
        ################################################################################################################
        # Local 수행 시 필요한 처리
        ################################################################################################################
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = 'N'

            in_Location = pd.read_csv(str_input_dir + "/in_Location.csv", encoding="UTF8")
            in_WHMapping = pd.read_csv(str_input_dir + "/in_WHMapping.csv", encoding="UTF8")

        ################################################################################################################
        # 서버 수행 시 파라미터 및 입력 테이블 확인
        ################################################################################################################
        # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'

        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())

        # 입력 변수 중 데이터가 없는 경우 경고 메시지를 출력한다.
        fn_check_input_table(in_Location, 'in_Location', '0')
        fn_check_input_table(in_WHMapping, 'in_WHMapping', '1')

        ################################################################################################################
        # Step 0.
        #     (1) in_Location에서 아래의 조건으로 데이터를 추출한다.
        #     Location.[Site Group3 Valid Flag] == true & Location.[Shipment Type] == "INDIR" &
        #     Location.[Location Type] == "DC" & Location.[Location Valid Flag] == true
        #     (2) in_Location에서 위의 조건에 속하지 않은 데이터 중에서
        #     Location.[DisplayName]이 "_SS"로 끝나거나 "_SS("를 포함하는 데이터를 추출하여 (1)의 데이터에 병합한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 10,
            'p_step_desc': 'Step 0. (1) in_Location에서 아래의 조건으로 데이터를 추출한다. '
                           'Location.[Site Group3 Valid Flag] == true & Location.[Shipment Type] == "INDIR" & '
                           'Location.[Location Type] == "DC" & Location.[Location Valid Flag] == true '
                           '(2) in_Location에서 위의 조건에 속하지 않은 데이터 중에서 '
                           'Location.[DisplayName]이 "_SS"로 끝나거나 '
                           '"_SS("를 포함하는 데이터를 추출하여 (1)의 데이터에 병합한다.',
            'p_df_name': 'df_location_filtered'
        }
        df_location_filtered = fn_filtered_location(in_Location, **dict_log)

        ################################################################################################################
        # Step 1. in_Location에 in_WHMapping 테이블을 Left Join 후 in_Location에만 있는 데이터를 추출하여 df_WHMapping를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 1000,
            'p_step_desc': 'Step 1. Data 테이블(in_SalesActualWRaw)과 Category 테이블(in_DataCategoryMeasureMap)을 '
                           '데이터 카테고리를 기준으로 inner join한다.',
            'p_df_name': 'df_WHMapping'
        }
        df_WHMapping = fn_get_new_data(df_location_filtered, in_WHMapping, **dict_log)

        ################################################################################################################
        # Step 2. df_WHMapping에 대해 아래와 같이 설정한다.
        #         WH Mapping_Map Status = 'REQ'
        #         WH Mapping_Valid Flag = 'N'
        #         WH Mapping_Creation Time = SYSDATE
        #         WH Mapping_Created By = PYTHON 명
        ################################################################################################################
        dict_log = {
            'p_step_no': 2000,
            'p_step_desc': 'Step 2. df_WHMapping에 대해 아래와 같이 설정한다.' + '\n' +
                           'WH Mapping_Map Status = "REQ", WH Mapping_Valid Flag = "N", ' +
                           'WH Mapping_Creation Time = SYSDATE, WH Mapping_Created By = PYTHON 명',
            'p_df_name': 'df_out_WHMapping'
        }
        df_out_WHMapping = fn_set_wh_mapping(df_WHMapping, **dict_log)

        ################################################################################################################
        # Step 3. out_WHMapping 형식에 맞도록 구성한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 9000,
            'p_step_desc': 'Step 3. out_WHMapping 형식에 맞도록 구성한다.',
            'p_df_name': 'out_WHMapping'
        }
        out_WHMapping = fn_output_formatter(df_out_WHMapping, **dict_log)

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_WHMapping = None
            raise Exception(e)
        else:
            # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
            # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들어 줌.
            if out_WHMapping.empty:
                out_WHMapping = fn_set_header()
                fn_log_dataframe(out_WHMapping, 'out_WHMapping')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    else:
        # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
        # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들어 줌.
        if out_WHMapping.empty:
            out_WHMapping = fn_set_header()
            fn_log_dataframe(out_WHMapping, 'out_WHMapping')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')
