"""
* 프로그램명
    - PY_UI_StockpileForeCastApply_REG

* 내용
    - Stockpile Forecast상단 Apply버튼 클릭시 동작

* 변경이력
    - 2025-11-27 12:54적용 daeun01.yun
    - 2026-01-07 kihong9.ju  | 해당 메저[Stockpile FCST W_Simulated Demand, Stockpile FCST W_G/R]가 공백일 경우 처리 로직 추가!

* Flow Summary
    Step1.
* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
* Input Tables
    -
* Output Tables
    -
* Flow Summary

* Validation :

* Execution :
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
str_instance = "PY_UI_StockpileForeCastApply_REG"
str_input_dir = "Input/UIStockpileForeCastApplyREG"
str_output_dir = "Output/UIStockpileForeCastApplyREG"
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
                'Version.[Version Name]': [], 'Sales Domain.[Sales Std2]': [], 'Item.[Item]': [], 'Time.[Week]': [],
                'Stockpile FCST Detail W_Simulated Demand': []
            }
        )

    elif str_p_cond == '1':
        # out_LoadingMasterToSite
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sales Domain.[Sales Std2]': [], 'Item.[Product Group]': [], 
                'SCM Type.[SCM Type]': [], 'Time.[Week]': [],
                'Stockpile FCST W_G/R':[], 'Stockpile FCST W_Simulated Demand':[],
                'Stockpile FCST W_Simulated G/R':[], 'Stockpile FCST W_Source Demand':[]
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
    out_StockpileForecastDetail = pd.DataFrame()
    out_StockpileForcast = pd.DataFrame()

    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = ''
            Param_PLANTYPE = ''
            in_StockpileForcastW = pd.read_csv(str_input_dir + "/in_StockpileForcastW.csv", encoding="UTF8")
            in_StockpileForcast_DetailW = pd.read_csv(str_input_dir + "/in_StockpileForcast_DetailW.csv", encoding="UTF8")

        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')

        fn_check_input_table(in_StockpileForcastW, 'in_StockpileForcastW', '0')
        fn_check_input_table(in_StockpileForcast_DetailW, 'in_StockpileForcast_DetailW', '0')

        df_StockpileForcast_merge = pd.merge(
            in_StockpileForcastW
            , in_StockpileForcast_DetailW
            , left_on=['Sales Domain.[Sales Std2]', 'Item.[Product Group]', 'SCM Type.[SCM Type]', 'Time.[Week]']
            , right_on=['Sales Domain.[Sales Std2]', 'Item.[Product Group]', 'Item.[SCM Type]', 'Time.[Week]']
            , how='inner'
        )
        # merge후 중복 컬럼으로 _x, _y제거
        df_StockpileForcast_merge = fn_merge_after(df_StockpileForcast_merge)

        df_StockpileForcast_merge['Stockpile FCST Detail W_Simulated Demand'] = (
                round(df_StockpileForcast_merge['Stockpile FCST Detail W_Demand'] * df_StockpileForcast_merge['Stockpile FCST W_G/R'])
        )

        # 그룹별 처리
        for (key, group) in df_StockpileForcast_merge.groupby(
                ['Sales Domain.[Sales Std2]', 'Item.[Product Group]', 'SCM Type.[SCM Type]', 'Time.[Week]']
        ):
            WDetailSimDemandSum = group['Stockpile FCST Detail W_Simulated Demand'].sum()
            WSimDemand = group['Stockpile FCST W_Simulated Demand'].iloc[0]  # 그룹 내 모든 D의 값은 동일

            # 🟧 추가 로직: WSimDemand가 NaN이면 그룹 내 'Stockpile FCST Detail W_Simulated Demand'를 모두 NaN으로 설정
            if pd.isna(WSimDemand):
                df_StockpileForcast_merge.loc[group.index, 'Stockpile FCST Detail W_Simulated Demand'] = np.nan
                # print(f"🟧 key: {key}, WDetailSimDemandSum: {WDetailSimDemandSum}, WSimDemand: {WSimDemand}")
                continue  # 공백 처리 후, 기존 조정 로직 스킵

            if WDetailSimDemandSum != WSimDemand:
                DemandDiff = WSimDemand - WDetailSimDemandSum
                WDetailSimDemandMax = group['Stockpile FCST Detail W_Simulated Demand'].idxmax()  # 그룹 내 최대값의 인덱스
                df_StockpileForcast_merge.at[WDetailSimDemandMax, 'Stockpile FCST Detail W_Simulated Demand'] += DemandDiff  # 최대값 조정

        out_StockpileForecastDetail = df_StockpileForcast_merge[
            [
                'Version.[Version Name]', 'Sales Domain.[Sales Std2]', 'Item.[Item]', 'Time.[Week]',
                'Stockpile FCST Detail W_Simulated Demand'
            ]
        ]

        # 🟧 추가 로직: 
        out_StockpileForcast  = in_StockpileForcastW.copy() 

        # 조건: 'Stockpile FCST W_Simulated Demand'와 'Stockpile FCST W_G/R'가 모두 NaN인 행
        mask = out_StockpileForcast['Stockpile FCST W_Simulated Demand'].isna() & out_StockpileForcast['Stockpile FCST W_G/R'].isna()

        # 해당 행의 'Stockpile FCST W_Simulated G/R' 컬럼을 NaN으로 변경
        out_StockpileForcast.loc[mask, 'Stockpile FCST W_Simulated G/R'] = np.nan

        fn_log_dataframe(out_StockpileForecastDetail, 'out_StockpileForecastDetail')
        fn_log_dataframe(out_StockpileForcast, 'out_StockpileForcast')

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
        if out_StockpileForecastDetail.empty:
            out_StockpileForecastDetail = fn_set_header('0')
            fn_log_dataframe(out_StockpileForecastDetail, 'out_StockpileForecastDetail')

        if out_StockpileForcast.empty:
            out_StockpileForcast = fn_set_header('1')
            fn_log_dataframe(out_StockpileForcast, 'out_StockpileForecast')
