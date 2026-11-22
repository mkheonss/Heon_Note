"""
* 프로그램명
    - PY_UI_SeasonalDelayBOD_REG.py
* 내용
    -
* 변경이력
    - 
* Flow Summary
    Step1.
* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
* Input Tables
    - in_BODLane_valid_Y
    : Select (
        [Version].[Version Name].[CWV_MP]
        * [Sub Location].[Sub Location].[P171]
        * [Location].[Location].[S367]
        * [Activity2].[Activity2].[VESSEL]
        * [Loading Port].[Loading Port]
        * [Discharge Port].[Discharge Port]
        * [Dest Port].[Dest Port]
    ) on row,
    ({
        Measure.[BOD Port_Ratio(Port per BOD 4W)]
        , Measure.[BOD Port_Ratio(Port per BOD 12W)]
        , Measure.[BOD Port_Ratio(Port per BOD Y-1)]
        , Measure.[BOD Port_Ratio(Port per BOD Y-1 M)]
        , Measure.[BOD Port_Valid Flag]
    }) on column
    where{Measure.[BOD Port_Valid Flag] == "Y"};
    : Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Activity2].[Activity2] * [Loading Port].[Loading Port] * [Discharge Port].[Discharge Port] * [Dest Port].[Dest Port]) on row, ({Measure.[BOD Port_Ratio(Port per BOD 4W)], Measure.[BOD Port_Ratio(Port per BOD 12W)], Measure.[BOD Port_Ratio(Port per BOD Y-1)]
, Measure.[BOD Port_Ratio(Port per BOD Y-1 M)], Measure.[BOD Port_Valid Flag]}) on column where{Measure.[BOD Port_Valid Flag] == "Y"};
    - in_SeasonalDelayAnalysis
    : Select (
        [Version].[Version Name].[CWV_MP]
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Time].[Week Name]
        * [Activity2].[Activity2]
        * [Logistics Section].[Logistics Section]
        * [Horizon].[Horizon]
        * [Node].[Node]* [To Node].[To Node]
    ) on row,
    ({
        Measure.[Seasonal Delay Analysis W_Valid Flag]
        , Measure.[Seasonal Delay Analysis W_Weight Avg Gap]
    }) on column;
    : Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Time].[Week Name] * [Activity2].[Activity2] * [Logistics Section].[Logistics Section] * [Horizon].[Horizon] * [Node].[Node]* [To Node].[To Node]) on row, ({Measure.[Seasonal Delay Analysis W_Valid Flag], Measure.[Seasonal Delay Analysis W_Weight Avg Gap]}) on column;
* Output Tables
    -
* Flow Summary

* Validation :

* Execution :
1. EXEC 파이썬 모듈 실행
EXEC plugin instance [PY_UI_SeasonalDelayBOD_REG]
            for measures {[Seasonal Delay Analysis W_Valid Flag]}
        using scope (&CWV_MP)
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
import pandas as pd
import traceback
import numpy as np
import inspect
import datetime
from NSCMCommon import NSCMCommon as common

# Local 개발 시에 필요한 공통 변수 선언
# o9에 저장된 instanceName
str_instance = "PY_UI_SeasonalDelayBOD_REG"
str_input_dir = "Input/UISeasonalDelayBODREG"
str_output_dir = "Output/UISeasonalDelayBODREG"
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
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :param str_p_cond: 
    :return: tuple
    """
    df_return = pd.DataFrame()
    # df_out_ActivityProdParam
    if str_p_cond == '0':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Time.[Week Name]': [], 'Activity2.[Activity2]': [], 'Logistics Section.[Logistics Section]': [],
                'Horizon.[Horizon]': [], 'Node.[Node]': [], 'To Node.[To Node]': [],
                'Seasonal Delay Analysis W_Valid Flag': [], 'Seasonal Delay Analysis W_Weight Avg Gap': []
            }
        )
    if str_p_cond == '1':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Activity2.[Activity2]': [], 'Horizon.[Horizon]': [], 'Time.[Week Name]': [],
                'Seasonal Delay Analysis W_Weight Avg Gap': []
            }
        )
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
        list_columns_all_rename.append(col.rstrip('_x'))
    df_p_source.columns = list_columns_all_rename
    # 결과 리턴
    return df_p_source

@_decoration_
def fn_output_formatter(df_p_source: pd.DataFrame, str_p_out_version: str, str_p_cond: str) -> pd.DataFrame:
    """
    df_MFG_PLAN_ROUTE_STEP2 테이블을 최종 형태로 가공하기
    :param df_p_source: 필요한 컬럼만을 추출을 위한 DataFrame
    :param str_p_out_version: Param_OUT_VERSION = 'CWV_MP'
    :param str_p_cond: '0' - out_OrderDetail, '1' - out_OriginalMap
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]

    # Return 변수
    df_return = pd.DataFrame()

    # 파라미터 테이블(df_p_source)이 비어 있는 경우 빈 데이터프레임을 리턴하면서 함수를 종료한다.
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 입력 파라미터(str_p_out_version)가 비어 있는 경우 오류를 발생시키고 함수를 종료한다.
    if str_p_out_version is None or str_p_out_version.strip() == '':
        raise Exception(f'[{str_my_name}] Exception: Param_OUT_VERSION(str_p_out_version) is empty.')

    # 입력 파라미터(str_p_cond)가 비어 있는 경우 오류를 발생시키고 함수를 종료한다.
    if str_p_cond is None or str_p_cond.strip() == '':
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 파라메터(str_p_cond)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 가공 전에 입력 테이블을 복사한다.
    df_return = df_p_source.copy(deep=True)

    # 구분자 정의(단계-output 코드)
    p_cond = str_p_cond

    # 결과 테이블에서 필요한 컬럼만을 추출하고 순서를 변경하여 저장한다.
    if p_cond == '0':
        df_return = df_return[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Time.[Week Name]',
                'Activity2.[Activity2]', 'Logistics Section.[Logistics Section]', 'Horizon.[Horizon]',
                'Node.[Node]', 'To Node.[To Node]',
                'Seasonal Delay Analysis W_Valid Flag', 'Seasonal Delay Analysis W_Weight Avg Gap',
                str_PortPerBOD_Measure,
                'W_Weight Avg Gap By Port Ratio'
            ]
        ]
    elif p_cond == '1':
        # Version.[Version Name] 컬럼의 값을 Parameter로 받은 값으로 변경
        df_return.insert(0, 'Version.[Version Name]', str_p_out_version)
        df_return = df_return[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
                'Activity2.[Activity2]', 'Horizon.[Horizon]', 'Time.[Week Name]',
                'Seasonal Delay BOD W_Weight Avg Gap'
            ]
        ]

    # 결과 리턴
    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()
    # Output 테이블 선언
    out_SeasonalDelayAnalysisValidY = pd.DataFrame()
    out_SeasonalDelayBOD = pd.DataFrame()
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            Param_OUT_VERSION = 'CWV_MP'
            Param_MeasureSet = '12W'

            in_BODLane_valid_Y = pd.read_csv(str_input_dir + "/in_BODLane_valid_Y.csv", encoding="UTF8")
            in_SeasonalDelayAnalysis = pd.read_csv(str_input_dir + "/in_SeasonalDelayAnalysis.csv", encoding="UTF8")

        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')
        if Param_MeasureSet is None or Param_MeasureSet.strip() == '':
            Param_MeasureSet = 'LY'
        logger.Note(p_note=f'Param_MeasureSet : {Param_MeasureSet}')

        fn_check_input_table(in_BODLane_valid_Y, 'in_BODLane', '0')
        fn_check_input_table(in_SeasonalDelayAnalysis, 'in_SeasonalDelayAnalysis', '0')

        # Param_MeasureSet에 따른 참고해야할 메져 선택
        str_PortPerBOD_Measure = ''
        if Param_MeasureSet == '4W':
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD 4W)'
        elif Param_MeasureSet == '12W':
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD 12W)'
        elif Param_MeasureSet == 'LY':
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD Y-1)'
        elif Param_MeasureSet == 'SMLY':
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD Y-1 M)'

        # Step 1 ###################################  Seasonal Delay Analysis에 "OInland"  #############################
        # O.inland: Seasonal Delay Anlasis 의 To Node 와 BOD Lane 의 "Loading Port"  동일한 경우의 Port Ratio 값의 Sum
        df_BODLane_LV1 = in_BODLane_valid_Y[
            [
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Loading Port.[Loading Port]', str_PortPerBOD_Measure
            ]
        ].copy()
        # BOD Lane 의 ("Loading Port")  동일한 경우의 Port Ratio 값의 Sum
        df_BODLane_LV1 = df_BODLane_LV1.groupby(
            [
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Loading Port.[Loading Port]'
            ]
        ).agg({str_PortPerBOD_Measure: 'sum'}).reset_index()
        # 중복제거
        df_BODLane_LV1 = df_BODLane_LV1.drop_duplicates()
        # BOD Lane, Seasonal Delay Analysis 같은 BOD Lane에서 출발지 -> Loading Port가 같은 O.inland 찾는다
        df_SeasonalDelayAnalysis_LV1 = pd.merge(
            df_BODLane_LV1, in_SeasonalDelayAnalysis,
            left_on=[
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Sub Location.[Sub Location]', 'Loading Port.[Loading Port]'
            ],
            right_on=[
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Node.[Node]', 'To Node.[To Node]'
            ],
            how='inner'
        )
        # merge후 중복 컬럼으로 _x, _y제거
        df_SeasonalDelayAnalysis_LV1 = fn_merge_after(df_SeasonalDelayAnalysis_LV1)
        # 'Seasonal Delay Analysis W_Valid Flag' 메져 'Y' 입력
        df_SeasonalDelayAnalysis_LV1['Seasonal Delay Analysis W_Valid Flag'] = 'Y'
        # Port Ration 를 곱해서 계산 되야 합니다.
        # - O.inland: Seasonal Delay Anlasis 의 To Node 와 BOD Lane 의 "Loading Port"  동일한 경우의 Port Ratio 값의 Sum
        df_SeasonalDelayAnalysis_LV1['W_Weight Avg Gap By Port Ratio'] = (
                df_SeasonalDelayAnalysis_LV1['Seasonal Delay Analysis W_Weight Avg Gap'] # Seasonal Delay Analysis메져
                * df_SeasonalDelayAnalysis_LV1[str_PortPerBOD_Measure] # BOD Lane port ratio SUM된 메져
        )
        # SeasonalDelayAnalysis 메져그룹에 맞게 필요 column만 구성
        df_SeasonalDelayAnalysis_LV1 = fn_output_formatter(df_SeasonalDelayAnalysis_LV1, Param_OUT_VERSION, '0')

        ####################################  Seasonal Delay Analysis에 "OceanTransit"  ################################
        # Ocean: BOD Lane 의 Loading Port 와 Discharge Port 가 동일한 경우에 대해 사용
        # 같은 BOD Lane에서 Ocean Transit(포트간이동) LV3에 해당하는 SeasonalDelayAnalysis을 찾아서
        df_BODLane_LV3 = in_BODLane_valid_Y[
            [
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Loading Port.[Loading Port]', 'Discharge Port.[Discharge Port]', str_PortPerBOD_Measure
            ]
        ].copy()
        # Ocean: BOD Lane 의 ("Loading Port" 와 "Discharge Port") 가 동일한 경우에 대해 Port Ratio 값의 Sum
        df_BODLane_LV3 = df_BODLane_LV3.groupby(
            [
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Loading Port.[Loading Port]', 'Discharge Port.[Discharge Port]'
            ]
        ).agg({str_PortPerBOD_Measure: 'sum'}).reset_index()
        # 중복제거
        df_BODLane_LV3 = df_BODLane_LV3.drop_duplicates()
        # BOD Lane, Seasonal Delay Analysis 같은 BOD Lane에서 Loading Port -> Discharge Port가 같은 "OceanTransit"찾는다
        df_SeasonalDelayAnalysis_LV3 = pd.merge(
            df_BODLane_LV3, in_SeasonalDelayAnalysis,
            left_on=[
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Loading Port.[Loading Port]', 'Discharge Port.[Discharge Port]'
            ],
            right_on=[
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Node.[Node]', 'To Node.[To Node]'
            ],
            how='inner'
        )
        # merge후 중복 컬럼으로 _x, _y제거
        df_SeasonalDelayAnalysis_LV3 = fn_merge_after(df_SeasonalDelayAnalysis_LV3)
        # 'Seasonal Delay Analysis W_Valid Flag' 메져 'Y' 입력
        df_SeasonalDelayAnalysis_LV3['Seasonal Delay Analysis W_Valid Flag'] = 'Y'
        # Port Ration 를 곱해서 계산 되야 합니다.
        # - Ocean: BOD Lane 의 Loading Port 와 Discharge Port 가 동일한 경우에 대해 사용
        df_SeasonalDelayAnalysis_LV3['W_Weight Avg Gap By Port Ratio'] = (
                df_SeasonalDelayAnalysis_LV3['Seasonal Delay Analysis W_Weight Avg Gap'] # Seasonal Delay Analysis메져
                * df_SeasonalDelayAnalysis_LV3[str_PortPerBOD_Measure] # BOD Lane port ratio SUM된 메져
        )
        # SeasonalDelayAnalysis 메져그룹에 맞게 필요 column만 구성
        df_SeasonalDelayAnalysis_LV3 = fn_output_formatter(df_SeasonalDelayAnalysis_LV3, Param_OUT_VERSION, '0')

        ####################################  Seasonal Delay Analysis에 "DInland"  #####################################
        # 같은 BOD Lane에서 D.Inland (최종항구에서, 목적지도착) LV5에 해당하는 SeasonalDelayAnalysis을 찾아서
        # BOD Lane의 'BOD Port_Valid Flag' 'Y'값을 'Seasonal Delay Analysis W_Valid Flag' 'Y'값으로 update
        df_BODLane_LV5 = in_BODLane_valid_Y[
            [
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Discharge Port.[Discharge Port]', str_PortPerBOD_Measure
            ]
        ].copy()
        # D.inland:   BOD Lane 의 동일한 ("Discharge Port") 를 가진 비율을 Sum 하여 사용
        df_BODLane_LV5 = df_BODLane_LV5.groupby(
            [
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Discharge Port.[Discharge Port]'
            ]
        ).agg({str_PortPerBOD_Measure:'sum'}).reset_index()
        # 필요하면 주석제거하고 OInland, OceanTransit 동일하게 적용필요
        # df_BODLane_LV5[str_PortPerBOD_Measure] = df_BODLane_LV5[str_PortPerBOD_Measure].round(2)
        # 중복제거
        df_BODLane_LV5 = df_BODLane_LV5.drop_duplicates()
        # BOD Lane, Seasonal Delay Analysis 같은 BOD Lane에서 Discharge Port -> Site To가 같은 "D.Inland"찾는다
        df_SeasonalDelayAnalysis_LV5 = pd.merge(
            df_BODLane_LV5, in_SeasonalDelayAnalysis,
            left_on=[
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Discharge Port.[Discharge Port]', 'Location.[Location]'
            ],
            right_on=[
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Node.[Node]', 'To Node.[To Node]'
            ],
            how='inner'
        )
        # merge후 중복 컬럼으로 _x, _y제거
        df_SeasonalDelayAnalysis_LV5 = fn_merge_after(df_SeasonalDelayAnalysis_LV5)
        # 'Seasonal Delay Analysis W_Valid Flag' 메져 'Y' 입력
        df_SeasonalDelayAnalysis_LV5['Seasonal Delay Analysis W_Valid Flag'] = 'Y'
        # Port Ration 를 곱해서 계산 되야 합니다.
        # - Ocean: BOD Lane 의 Loading Port 와 Discharge Port 가 동일한 경우에 대해 사용
        df_SeasonalDelayAnalysis_LV5['W_Weight Avg Gap By Port Ratio'] = (
                df_SeasonalDelayAnalysis_LV5['Seasonal Delay Analysis W_Weight Avg Gap'] # Seasonal Delay Analysis메져
                * df_SeasonalDelayAnalysis_LV5[str_PortPerBOD_Measure] # BOD Lane port ratio SUM된 메져
        )
        # SeasonalDelayAnalysis 메져그룹에 맞게 필요 column만 구성
        df_SeasonalDelayAnalysis_LV5 = fn_output_formatter(df_SeasonalDelayAnalysis_LV5, Param_OUT_VERSION, '0')

        # LV1, LV3, LV5를 합쳐 완전한 데이타를 만든다.
        df_SeasonalDelayAnalysis_Concat = pd.concat(
            [df_SeasonalDelayAnalysis_LV1, df_SeasonalDelayAnalysis_LV3, df_SeasonalDelayAnalysis_LV5],
            ignore_index=True
        )
        # Valid 'Y'를 위한 output
        out_SeasonalDelayAnalysisValidY = df_SeasonalDelayAnalysis_Concat[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Time.[Week Name]',
                'Activity2.[Activity2]', 'Logistics Section.[Logistics Section]', 'Horizon.[Horizon]',
                'Node.[Node]', 'To Node.[To Node]',
                'Seasonal Delay Analysis W_Valid Flag'
            ]
        ]

        # Seasonal Dealy BOD 상단 화면 Site(From), Site(To), TP Mode, View Horizon별 Weight Avg Gap 합산을 위한 group
        df_SeasonalDelayBOD = df_SeasonalDelayAnalysis_Concat.groupby(
            [
                'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]', 'Horizon.[Horizon]',
                'Time.[Week Name]'
            ]
        ).agg({'W_Weight Avg Gap By Port Ratio': 'sum'})
        # Time.[Week] 인덱스를 컬럼으로 변경하고 인덱스는 순번 인덱스로 변경
        # out으로 출력변수 생성
        df_SeasonalDelayBOD = df_SeasonalDelayBOD.reset_index()
        # Seasonal Delay BOD W_Weight Avg Gap 메저에 Seasonal Delay Analysis W_Weight Avg Gap sum값을 넣는다.
        df_SeasonalDelayBOD['Seasonal Delay BOD W_Weight Avg Gap'] = df_SeasonalDelayBOD['W_Weight Avg Gap By Port Ratio']
        out_SeasonalDelayBOD = fn_output_formatter(df_SeasonalDelayBOD, Param_OUT_VERSION, '1')

        # 출력 변수 확인용 로그
        fn_log_dataframe(df_SeasonalDelayAnalysis_LV1, 'df_SeasonalDelayAnalysis_LV1')
        fn_log_dataframe(df_SeasonalDelayAnalysis_LV3, 'df_SeasonalDelayAnalysis_LV3')
        fn_log_dataframe(df_SeasonalDelayAnalysis_LV5, 'df_SeasonalDelayAnalysis_LV5')
        fn_log_dataframe(df_SeasonalDelayAnalysis_Concat, 'df_SeasonalDelayAnalysis_Concat')
        fn_log_dataframe(out_SeasonalDelayAnalysisValidY, 'out_SeasonalDelayAnalysisValidY')
        fn_log_dataframe(out_SeasonalDelayBOD, 'out_SeasonalDelayBOD')
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
        # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
        # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들엊 줌.
        if out_SeasonalDelayAnalysisValidY.empty:
            out_SeasonalDelayAnalysisValidY = fn_set_header('0')
            fn_log_dataframe(out_SeasonalDelayAnalysisValidY, 'out_SeasonalDelayAnalysisValidY')
        if out_SeasonalDelayBOD.empty:
            out_SeasonalDelayBOD = fn_set_header('0')
            fn_log_dataframe(out_SeasonalDelayBOD, 'out_SeasonalDelayBOD')
