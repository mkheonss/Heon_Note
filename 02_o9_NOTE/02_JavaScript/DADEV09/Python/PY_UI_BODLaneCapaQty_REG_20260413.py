"""
* 프로그램명
    - PY_UI_BODLaneCapaQty_REG.py
* 내용
    -
* 변경이력
    - 
* Flow Summary
    Step1.
* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
* Input Tables
    - in_BODPort
    Select (
        [Version].[Version Name].CWV_MP
        * &NSFromSiteMF
        * &NSToSiteDC
        * Activity2.Activity2.filter(#.Name in {VESSEL, TRUCK, AIR})
        * [Loading Port].[Loading Service Region Level 1]
        * [Loading Port].[Loading Service Region Level 2]
        * [Loading Port].[Loading Logistics Port]
        * [Loading Port].[Loading SCM Port]
        * [Loading Port].[Loading Port]
        * [Discharge Port].[Discharge Service Region Level 1]
        * [Discharge Port].[Discharge Service Region Level 2]
        * [Discharge Port].[Discharge Logistics Port]
        * [Discharge Port].[Discharge SCM Port]
        * [Discharge Port].[Discharge Port]
        * [Dest Port].[Dest Port]
    ) on row,
    ({
        Measure.[BOD Port_Last Used Date]
        , Measure.[BOD Port_Recent Year Volume CNTR]
        , Measure.[BOD Port_Recent Year Used Count]
        , Measure.[BOD Port_Valid Flag]
        , Measure.[BOD Port_Ratio(Port per BOD 4W)]
        , Measure.[BOD Port_Ratio(BOD per Port 4W)]
        , Measure.[BOD Port_Capa Qty(4W)]
        , Measure.[BOD Port_Recent Year Volume CNTR (4W)]
        , Measure.[BOD Port_Ratio(Port per BOD 12W)]
        , Measure.[BOD Port_Ratio(BOD per Port 12W)]
        , Measure.[BOD Port_Capa Qty(12W)]
        , Measure.[BOD Port_Recent Year Volume CNTR (12W)]
        , Measure.[BOD Port_Ratio(Port per BOD Y-1)]
        , Measure.[BOD Port_Ratio(BOD per Port Y-1)]
        , Measure.[BOD Port_Capa Qty(Y-1)]
        , Measure.[BOD Port_Recent Year Volume CNTR (Y-1)]
        , Measure.[BOD Port_Ratio(Port per BOD Y-1 M)]
        , Measure.[BOD Port_Ratio(BOD per Port Y-1 M)]
        , Measure.[BOD Port_Capa Qty(Y-1 M)]
        , Measure.[BOD Port_Recent Year Volume CNTR (Y-1 M)]
        , Measure.[BOD Port_Ratio(Port / BOD)]
    }) on column;
    - in_Ocean_Contract
    Select (
        [Version].[Version Name]
        * [Loading Port].[Loading Service Region Level 1]
        * [Loading Port].[Loading Service Region Level 2]
        * [Loading Port].[Loading Logistics Port]
        * [Loading Port].[Loading SCM Port]
        * [Discharge Port].[Discharge Service Region Level 1]
        * [Discharge Port].[Discharge Service Region Level 2]
        * [Discharge Port].[Discharge Logistics Port]
        * [Discharge Port].[Discharge SCM Port]
        * between (&CurrentWeek.element(0), &CurrentWeek.element(0).LeadOffset(12))
    ) on row,
    ({
        Measure.[Ocean Capa W_Capa Qty]
    }) on column;
    - in_TimeWeek
    select (between (&CurrentWeek.element(0), &CurrentWeek.element(0).LeadOffset(12)));
* Output Tables
    - df_out_BODCapaWQty
* Flow Summary

* Validation :

* Execution :
    EXEC plugin instance [PY_UI_BODLaneCapaQty_REG]
    for measures {
        [BOD Port W_Capa Qty]
    }
    using scope ([Version].[Version Name].[CWV_MP])
    using arguments {
        (ExecutionMode, "MediumWeight")
        , (Param_OUT_VERSION, "CWV_MP")
        , (Param_MeasureSet, "LY")
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
str_instance = "PY_UI_BODLaneCapaQty_REG"
str_input_dir = "Input/UIBODLaneCapaQtyREG"
str_output_dir = "Output/UIBODLaneCapaQtyREG"
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
                'Activity2.[Activity2]': [], 'Loading Port.[Loading Port]': [], 'Discharge Port.[Discharge Port]': [],
                'Dest Port.[Dest Port]': [], 'Time.[Week]': [],
                'BOD Port W_Capa Qty': []
            }
        )
    elif str_p_cond == '1':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Activity2.[Activity2]': [], 'Loading Port.[Loading Port]': [], 'Discharge Port.[Discharge Port]': [],
                'Dest Port.[Dest Port]': [],
                'BOD Port_Ratio(Port / BOD)': []
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


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()
    # Output 테이블 선언
    df_out_BODPortRatio = pd.DataFrame()
    df_out_BODCapaWQty = pd.DataFrame()
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            Param_OUT_VERSION = 'CWV_MP'
            Param_MeasureSet = '4W'
            Param_User_Name = 'DaeUn Yun'  # 'daeun01.yun'

            in_BODPort = pd.read_csv(str_input_dir + "/in_BODPort.csv", encoding="UTF8")
            in_Ocean_Contract = pd.read_csv(str_input_dir + "/in_Ocean_Contract.csv", encoding="UTF8")
            in_TimeWeek = pd.read_csv(str_input_dir + "/in_TimeWeek.csv", encoding="UTF8")

        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')
        if Param_MeasureSet is None or Param_MeasureSet.strip() == '':
            Param_MeasureSet = 'LY'
        logger.Note(p_note=f'Param_MeasureSet : {Param_MeasureSet}')

        fn_check_input_table(in_BODPort, 'in_BODPort', '0')
        fn_check_input_table(in_Ocean_Contract, 'in_Ocean_Contract', '0')
        fn_check_input_table(in_TimeWeek, 'in_TimeWeek', '0')

        # in_Ocean_Contract Time.[Week]와 in_TimeWeek의 Time.[Week]를 join하여
        # between (&CurrentWeek.element(0), &CurrentWeek.element(0).LeadOffset(12)) 현재 주차부터 12주차까지 데이타만
        # df_Ocean_Contract = pd.merge(in_Ocean_Contract, in_TimeWeek, on='Time.[Week]', how='inner')

        # Param_MeasureSet에 따른 참고해야할 메져 선택
        str_BODPerPortMeasure = ''
        str_PortPerBOD_Measure = ''
        if Param_MeasureSet == '4W':
            str_BODPerPortMeasure = 'BOD Port_Ratio(BOD per Port 4W)'
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD 4W)'
        elif Param_MeasureSet == '12W':
            str_BODPerPortMeasure = 'BOD Port_Ratio(BOD per Port 12W)'
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD 12W)'
        elif Param_MeasureSet == 'LY':
            str_BODPerPortMeasure = 'BOD Port_Ratio(BOD per Port Y-1)'
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD Y-1)'
        elif Param_MeasureSet == 'SMLY':
            str_BODPerPortMeasure = 'BOD Port_Ratio(BOD per Port Y-1 M)'
            str_PortPerBOD_Measure = 'BOD Port_Ratio(Port per BOD Y-1 M)'

        # 원본 in_BODPort를 df_BODPort 복사
        df_BODPort = in_BODPort.copy()
        # 'BOD Port_Valid Flag'가 'Y'가 아니면 아래 메져 np.nan으로 변경
        df_BODPort.loc[
            df_BODPort['BOD Port_Valid Flag'] != 'Y'
            , [
                'BOD Port_Capa Qty(4W)',
                'BOD Port_Capa Qty(12W)',
                'BOD Port_Capa Qty(Y-1)',
                'BOD Port_Capa Qty(Y-1 M)',
                'BOD Port_Ratio(BOD per Port 4W)',
                'BOD Port_Ratio(BOD per Port 12W)',
                'BOD Port_Ratio(BOD per Port Y-1)',
                'BOD Port_Ratio(BOD per Port Y-1 M)',
                'BOD Port_Ratio(Port per BOD 4W)',
                'BOD Port_Ratio(Port per BOD 12W)',
                'BOD Port_Ratio(Port per BOD Y-1)',
                'BOD Port_Ratio(Port per BOD Y-1 M)'
            ]
        ] = np.nan
        # check한 Measure Set에 Port Ratio per BOD[Guideline] 컬럼 값을 Port Ratio per BOD(BOD Port_Ratio(Port / BOD)) 컬럼에 Copy한다.
        df_BODPort['BOD Port_Ratio(Port / BOD)'] = df_BODPort[str_PortPerBOD_Measure]
        df_BODPort['BOD Port_Updated By'] = Param_User_Name
        df_BODPort['BOD Port_Update Time'] = datetime.datetime.now()
        # O9 PortRatio 변경 out을 위한 데이타 프레임
        df_out_BODPortRatio = df_BODPort[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Loading Port.[Loading Port]', 'Discharge Port.[Discharge Port]', 'Dest Port.[Dest Port]',
                'BOD Port_Capa Qty(4W)',
                'BOD Port_Capa Qty(12W)',
                'BOD Port_Capa Qty(Y-1)',
                'BOD Port_Capa Qty(Y-1 M)',
                'BOD Port_Ratio(BOD per Port 4W)',
                'BOD Port_Ratio(BOD per Port 12W)',
                'BOD Port_Ratio(BOD per Port Y-1)',
                'BOD Port_Ratio(BOD per Port Y-1 M)',
                'BOD Port_Ratio(Port per BOD 4W)',
                'BOD Port_Ratio(Port per BOD 12W)',
                'BOD Port_Ratio(Port per BOD Y-1)',
                'BOD Port_Ratio(Port per BOD Y-1 M)',
                'BOD Port_Ratio(Port / BOD)',
                'BOD Port_Updated By',
                'BOD Port_Update Time'
            ]
        ]
        # 2026-01-12 송프로 요청에 의해 groupby하지 않고 202604데이타가 중복으로 발생하여 overwrite되는현상발생하여 합이 적게나오는 현상 발생
        # in_Ocean_Contract의 메져 'Loading Port.[Loading Logistics Port]', 'Discharge Port.[Discharge Logistics Port]'
        # 'Time.[Week]' 으로 group by하여 'Ocean Capa W_Capa Qty' sum한다.
        df_Ocean_Contract = in_Ocean_Contract.groupby(
            ['Loading Port.[Loading Logistics Port]', 'Discharge Port.[Discharge Logistics Port]', 'Time.[Week]']
        ).agg({'Ocean Capa W_Capa Qty': 'sum'}).reset_index()

        df_BODPort = pd.merge(
            in_BODPort, df_Ocean_Contract,
            on=['Loading Port.[Loading Logistics Port]', 'Discharge Port.[Discharge Logistics Port]'],
            how='left', indicator=True
        )
        # 컬럼중복제거
        df_BODPort = fn_merge_after(df_BODPort)
        # Ocean Contract 존재하는
        df_BODPort_OceanCont = df_BODPort[df_BODPort['_merge'] == 'both'].copy()
        # Ocean Contract 존재하지 않는
        df_BODPort_OceanCont_Not = df_BODPort[df_BODPort['_merge'] == 'left_only'].copy()
        df_BODPort_OceanCont_Not['CROSS_KEY'] = 1
        in_TimeWeek['CROSS_KEY'] = 1
        # in_Ocean_Contract merge시 없어도 in_TimeWeek 13주차 대상에 그리드에 표시를 위해 cross join
        df_BODPort_OceanCont_Not = pd.merge(df_BODPort_OceanCont_Not, in_TimeWeek, on='CROSS_KEY', how='inner')
        # 컬럼중복제거
        df_BODPort_OceanCont_Not.drop('Time.[Week]_x', axis=1, inplace=True)
        df_BODPort_OceanCont_Not.rename(columns={'Time.[Week]_y': 'Time.[Week]'}, inplace=True)
        # BODPort에서 OceanContract존재하는것과 존재하지 않아 Time.[Week]를 넣은 df를 합친다.
        df_BODPort_Total = pd.concat([df_BODPort_OceanCont, df_BODPort_OceanCont_Not], ignore_index=True)
        # 컬럼중복제거

        # 선택한 Measure Set에 'BOD Port W_Capa Qty' 값 'Ocean Capa W_Capa Qty' * 'BOD per Port Ratio' 값을 구한다.
        df_BODPort_Total['BOD Port W_Capa Qty'] = df_BODPort_Total['Ocean Capa W_Capa Qty'] * df_BODPort_Total[str_BODPerPortMeasure]
        df_BODPort_Total.loc[df_BODPort_Total['BOD Port W_Capa Qty'].isna(), 'BOD Port W_Capa Qty'] = 0.00
        # O9 out을 위한 데이타 프레임
        df_out_BODCapaWQty = df_BODPort_Total[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Activity2.[Activity2]',
                'Loading Port.[Loading Port]', 'Discharge Port.[Discharge Port]', 'Dest Port.[Dest Port]',
                'Time.[Week]',
                'BOD Port W_Capa Qty'
            ]
        ]

        # 출력 변수 확인용 로그
        fn_log_dataframe(df_out_BODPortRatio, 'df_out_BODPortRatio')
        fn_log_dataframe(df_out_BODCapaWQty, 'df_out_BODCapaWQty')

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
        if df_out_BODCapaWQty.empty:
            df_out_BODPortRatio = fn_set_header('1')
            fn_log_dataframe(df_out_BODPortRatio, 'df_out_BODPortRatio')
            df_out_BODCapaWQty = fn_set_header('0')
            fn_log_dataframe(df_out_BODCapaWQty, 'df_out_BODCapaWQty')
