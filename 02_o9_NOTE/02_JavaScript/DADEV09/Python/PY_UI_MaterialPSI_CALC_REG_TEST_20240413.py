"""
* 프로그램명
    - PY_UI_MaterialPSI_CALC_REG

* 내용
    -
* 변경이력
    - 2025.12.24 / Miss Lee / Create

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를 결정하는 파라미터

* Input Tables
    - in_Material_Master :
        Select (
                  [Sub Location].[Sub Location]
                * [Item Raw Material].[Item Raw Material]
                ) on row,
                ({
                  Measure.[Mat Master_Constraint]
                , Measure.[Mat Master_Constraint (Filter)]
                , Measure.[Mat Master_Group1]
                , Measure.[Mat Master_Group1 (Filter)]
                , Measure.[Mat Master_Group2]
                , Measure.[Mat Master_Group2 (Filter)]
                , Measure.[Mat Master_Constraint Period]
                , Measure.[Mat Master_PO LT]}) on column
        where { Association(Measure.[Mat PSI W_Requirement]>=0),
                [Version].[Version Name].[CWV_MP]};

    - in_Material_PSI_W:
        Select (
                  [Sub Location].[Sub Location]
                * [Time].[Week]
                * [Item Raw Material].[Item Raw Material]
                ) on row,
                ({
                  Measure.[Mat PSI W_BG Signal]
                , Measure.[Mat PSI W_Inventory]
                , Measure.[Mat PSI W_Overdue]
                , Measure.[Mat PSI W_PO Arrival]
                , Measure.[Mat PSI W_PO BOH]
                , Measure.[Mat PSI W_PO Balance]
                , Measure.[Mat PSI W_PO EOH]
                , Measure.[Mat PSI W_PO Remain]
                , Measure.[Mat PSI W_PO Short Material]
                , Measure.[Mat PSI W_PO Supply Material]
                , Measure.[Mat PSI W_Requirement]
                , Measure.[Mat PSI W_Requirement Material]
                , Measure.[Mat PSI W_SN Arrival]
                , Measure.[Mat PSI W_SN BOH]
                , Measure.[Mat PSI W_SN Balance]
                , Measure.[Mat PSI W_SN EOH]
                , Measure.[Mat PSI W_SN Short Material]
                , Measure.[Mat PSI W_SN Supply Material]
                , Measure.[Mat PSI W_Unplanned]
               }) on column
        where {[Version].[Version Name].[CWV_MP]};

    - in_Material_PSI_Sub:
        Select (
                  [Sub Location].[Sub Location]
                * [Item Raw Material].[Item Raw Material]
                ) on row,
              ({
                  Measure.[Mat PSI Sub_Constraint]
                , Measure.[Mat PSI Sub_Constraint (Filter)]
                , Measure.[Mat PSI Sub_Group1]
                , Measure.[Mat PSI Sub_Group1 (Filter)]
                , Measure.[Mat PSI Sub_Group2]
                , Measure.[Mat PSI Sub_Group2 (Filter)]
              }) on column
        where {[Version].[Version Name].[CWV_MP]};

    - in_Version :
    select ([Version].[Version Name]) on row
    include memberproperties {[Version].[Version Name], [DisplayName], [Plan Week]};

    - in_Time :
    Select (
            &AllWeeks.Filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-51).Key
                            && #.Key <= &CurrentWeek.element(0).LeadOffset(51).Key)
            ) on row;

* Output Tables
    - out_Material_PSI_W:
        Select (
                  [Version].[Version Name].[CWV_MP]
                * [Sub Location].[Sub Location]
                * [Time].[Week]
                * [Item Raw Material].[Item Raw Material]
                ) on row,
                ({
                  Measure.[Mat PSI W_BG Signal]
                , Measure.[Mat PSI W_Inventory]
                , Measure.[Mat PSI W_Overdue]
                , Measure.[Mat PSI W_PO Arrival]
                , Measure.[Mat PSI W_PO BOH]
                , Measure.[Mat PSI W_PO Balance]
                , Measure.[Mat PSI W_PO EOH]
                , Measure.[Mat PSI W_PO Remain]
                , Measure.[Mat PSI W_PO Short Material]
                , Measure.[Mat PSI W_PO Supply Material]
                , Measure.[Mat PSI W_Requirement]
                , Measure.[Mat PSI W_Requirement Material]
                , Measure.[Mat PSI W_SN Arrival]
                , Measure.[Mat PSI W_SN BOH]
                , Measure.[Mat PSI W_SN Balance]
                , Measure.[Mat PSI W_SN EOH]
                , Measure.[Mat PSI W_SN Short Material]
                , Measure.[Mat PSI W_SN Supply Material]
                , Measure.[Mat PSI W_Unplanned]
                }) on column;

    - out_Material_PSI_Sub:
        Select (
                  [Version].[Version Name].[CWV_MP]
                * [Sub Location].[Sub Location]
                * [Item Raw Material].[Item Raw Material]
                ) on row,
                ({
                  Measure.[Mat PSI Sub_Constraint]
                , Measure.[Mat PSI Sub_Constraint (Filter)]
                , Measure.[Mat PSI Sub_Group1]
                , Measure.[Mat PSI Sub_Group1 (Filter)]
                , Measure.[Mat PSI Sub_Group2]
                , Measure.[Mat PSI Sub_Group2 (Filter)]
                }) on column;

* Flow Summary


* Validation :

* Execution :
    1. 기존 메저 데이터 삭제(nullify)
        Scope:([Version].[Version Name].CWV_MP);
              Measure.[Mat PSI W_BG Signal]=null;
              Measure.[Mat PSI W_Inventory]=null;
              Measure.[Mat PSI W_Overdue]=null;
              Measure.[Mat PSI W_PO Arrival]=null;
              Measure.[Mat PSI W_PO BOH]=null;
              Measure.[Mat PSI W_PO Balance]=null;
              Measure.[Mat PSI W_PO EOH]=null;
              Measure.[Mat PSI W_PO Remain]=null;
              Measure.[Mat PSI W_PO Short Material]=null;
              Measure.[Mat PSI W_PO Supply Material]=null;
              Measure.[Mat PSI W_Requirement]=null;
              Measure.[Mat PSI W_Requirement Material]=null;
              Measure.[Mat PSI W_SN Arrival]=null;
              Measure.[Mat PSI W_SN BOH]=null;
              Measure.[Mat PSI W_SN Balance]=null;
              Measure.[Mat PSI W_SN EOH]=null;
              Measure.[Mat PSI W_SN Short Material]=null;
              Measure.[Mat PSI W_SN Supply Material]=null;
              Measure.[Mat PSI W_Unplanned]=null;
        end scope;

        delete data for model [Material PSI Sub] where { &CWV_MP };

    2. Plugin Call하여 신규 MG 생성
    1) LightWeight
        EXEC plugin instance [PY_UI_MaterialPSI_CALC_REG]
            for measures { [Mat PSI W_Requirement Material]}
               using scope ([Version].[Version Name].[CWV_MP])
               using arguments {(ExecutionMode, "LightWeight")
                             , (Param_OUT_VERSION, "CWV_MP")
                             , (MaxSliceTableCells, 200000000)
                             , (MaxConcurrency, 1 )
                             , (IncludeNullRows, False)
                             , ([Param.o9_sys_log_level], "DEBUG")
                             };

    2) MediumWeight
        EXEC plugin instance [PY_UI_MaterialPSI_CALC_REG]
            for measures { [Mat PSI W_Requirement Material]}
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

from itertools import accumulate
from NSCMCommon import NSCMCommon as common


########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_MaterialPSI_CALC_REG"
str_input_dir = "Input/UIMaterialPSICALCREG"
str_output_dir = "Output/UIMaterialPSICALCREG"
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
def fn_preprocess(df_p_source: pd.DataFrame, df_p_time:pd.DataFrame) -> pd.DataFrame:
    """
        Version의 Plan Week에 해당하는 Time.[Week]를 찾아 해당 주차 포함하여 34주차 Time 테이블 생성한다.
    :param df_p_source: in_Version
    :param df_p_time: in_Time
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있을때 빈 테이블 반환한다.
    if df_p_source.empty or df_p_time.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source or df_p_time)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # Plan Week에 해당하는 주차 조건
    list_where = df_p_time['Time.[Week]'] == df_p_source.iloc[0]['Version.[Plan Week]']
    
    # 해당 인덱스
    inx = df_p_time[list_where].index[0]

    # 34주차 만큼 생성
    df_return = df_p_time.loc[inx:inx+33, 'Time.[Week]'].to_frame().reset_index(drop=True)
    
    # 형변환
    df_return['Time.[Week]'] = df_return['Time.[Week]'].astype(str)

    return df_return


@_decoration_
def fn_merge_psi_week(df_p_source: pd.DataFrame, df_p_time: pd.DataFrame) -> pd.DataFrame:
    """
    in_Material_PSI_W 데이터를 34주차(Version의 Plan Week 기준) 만큼 생성한다
    :param df_p_source: in_Material_PSI_W
    :param df_p_time:  df_Time
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # df_p_source 비어 있을 경우 빈 테이블을 반환한다.
    if df_p_source.empty or df_p_time.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source or df_p_time)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # df_time 기준 34주차 만큼 df_p_source row 생성 한다.
    # 기준 material 테이블
    df_material = (
        df_p_source[['Sub Location.[Sub Location]', 'Item Raw Material.[Item Raw Material]']]
        .drop_duplicates()
        .copy()
    )

    # material key별로 34주차 생성 ( 기준 테이블 )
    # 주차별 index를 week_inx 로 가져옴
    df_time = df_p_time.reset_index(names='week_inx')
    # Cross Join
    df_material['key'] = 0
    df_time['key'] = 0
    df_material = df_material.merge(df_time, on='key').drop(columns='key')
    # df_material = df_material.merge(df_time, how='cross')

    # Merge
    list_col = ['Sub Location.[Sub Location]', 'Item Raw Material.[Item Raw Material]', 'Time.[Week]']
    df_return = df_material.merge(df_p_source, how='left', on=list_col)

    # fillna 0 처리
    df_return.fillna(0, inplace=True)

    return df_return


@_decoration_
def fn_make_material_psi_step(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    [STEP1-1]. Requirement(Material) - Mat PSI W_Requirement Material
    => Mat PSI W_Requirement + Mat PSI W_Unplanned + Mat PSI W_Overdue.

    [STEP2-1]. S/N BOH - Mat PSI W_SN BOH
    => 첫 주차인 경우, Mat PSI W_Inventory,
    이후 주차는 전주의 S/N EOH(Mat PSI W_SN EOH).

    [STEP2-2]. PO BOH - Mat PSI W_PO BOH
    => 첫 주차인 경우, Mat PSI W_Inventory,
    이후 주차는 전주의 PO EOH(Mat PSI W_PO EOH).

    [STEP3-1]. S/N Supply (Material) - Mat PSI W_SN Supply Material
    => Mat PSI W_SN BOH + Mat PSI W_SN Arrival 계산 값이
    Mat PSI W_Requirement Material 보다 크면 Mat PSI W_Requirement Material.
    그렇지 않으면, Mat PSI W_SN BOH + Mat PSI W_SN Arrival.

    [STEP3-2]. PO Supply (Material) - Mat PSI W_PO Supply Material
    => Mat PSI W_PO BOH + Mat PSI W_SN Arrival + Mat PSI W_PO Arrival
    계산 값이 Mat PSI W_Requirement Material 보다 크면 Mat PSI W_Requirement Material.
    그렇지 않으면, Mat PSI W_PO BOH + Mat PSI W_SN Arrival + Mat PSI W_PO Arrival.

    [STEP4-1]. S/N Short (Material) - Mat PSI W_SN Short Material
    => Mat PSI W_Requirement Material - Mat PSI W_SN Supply Material

    [STEP4-2]. PO Short (Material) - Mat PSI W_PO Short Material
    => Mat PSI W_Requirement Material - Mat PSI W_PO Supply Material

    [STEP5-1]. S/N EOH - Mat PSI W_SN EOH
    => Mat PSI W_SN BOH - Mat PSI W_SN Supply Material + Mat PSI W_SN Arrival

    [STEP5-2]. PO EOH - Mat PSI W_PO EOH
    => Mat PSI W_PO BOH - Mat PSI W_PO Supply Material + Mat PSI W_SN Arrival
     + Mat PSI W_PO Arrival

    [STEP6-1]. Balance-S/N - Mat PSI W_SN Balance
    => 첫주는,
    Mat PSI W_SN BOH + Mat PSI W_SN Arrival - Mat PSI W_Requirement Material,
    이후는,
    전주 Mat PSI W_SN Balance] + Mat PSI W_SN Arrival - Mat PSI W_Requirement Material

    [STEP6-2]. Balance-PO - Mat PSI W_PO Balance
      => 첫주는,
      Mat PSI W_PO BOH + Mat PSI W_SN Arrival + Mat PSI W_PO Arrival - Mat PSI W_Requirement Material
      이후는,
      전주 Mat PSI W_PO Balance + Mat PSI W_SN Arrival + Mat PSI W_PO Arrival - Mat PSI W_Requirement Material

    :param df_p_source: df_Material_PSI_W_Time
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # df_p_source 비어 있을 경우 빈 테이블을 반환한다.
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return
    
    # DataFrame 복사
    df_return = df_p_source.copy(deep=True)

    # Mat PSI W_Requirement Material
    df_return['Mat PSI W_Requirement Material'] = (
            df_return['Mat PSI W_Requirement'] + df_return['Mat PSI W_Unplanned'] + df_return['Mat PSI W_Overdue']
    )

    # GROUP BY 전 WEEK별로 SORT
    df_return = (
        df_return
        .sort_values(by=['Sub Location.[Sub Location]', 'Item Raw Material.[Item Raw Material]', 'Time.[Week]']
                     , ascending=[True, True, True])
        .reset_index(drop=True)
    )

    # PSI function 호출( Sub Location / Item Raw Material 별로 실행 )
    df_return = (
        df_return
        .groupby(['Sub Location.[Sub Location]', 'Item Raw Material.[Item Raw Material]'], group_keys=False)
        .apply(fn_calculate_psi)
        .reset_index(drop=True)
    )

    return df_return


def fn_calculate_psi(group: pd.DataFrame) -> pd.DataFrame:
    """
    Sub Location / Item Raw Material 별로
    df_Material_PSI_W : Requirement Material,
                       SN BOH, SN EOH, SN Supply Material, SN Short Material, SN Balance,
                       PO BOH, PO EOH, PO Supply Material, PO Short Material, PO Balance 칼럼 생성.
    :param group: Sub Location / Item Raw Material 별 group
    :return: DataFrame
    """
    group_df = group.copy()
    
    # SN BOH, PO BOH 초기값
    int_init_boh = group_df.iloc[0]['Mat PSI W_Inventory']

    # 순차 로직 (BOH -> EOH)
    def step(prev_boh, current):
        prev_sn_boh, prev_po_boh= prev_boh
        arr, req, po_arr = current
        sn_supplied = min(prev_sn_boh + arr, req)
        sn_eoh = prev_sn_boh + arr - sn_supplied
        po_supplied = min(prev_po_boh + arr + po_arr, req)
        po_eoh = prev_po_boh + arr + po_arr - po_supplied
        return sn_eoh, po_eoh

    # accumulate로 EOH 리스트 생성 (tuple로 반환)
    tuple_init_both = (int_init_boh, int_init_boh)
    combine_list = list(accumulate(zip(group_df['Mat PSI W_SN Arrival']
                                         , group_df['Mat PSI W_Requirement Material']
                                         , group_df['Mat PSI W_PO Arrival']), step,initial=tuple_init_both)
                        )

    # tuple 분리
    sn_eoh_list, po_eoh_list = zip(*combine_list)

    # SN 결과 추가
    # SN BOH
    group_df['Mat PSI W_SN BOH'] = sn_eoh_list[:-1]
    # SN EOH
    group_df['Mat PSI W_SN EOH'] = sn_eoh_list[1:]
    # SN Supply Material
    group_df['Mat PSI W_SN Supply Material'] = (
        np.where(
            group_df['Mat PSI W_SN BOH'] + group_df['Mat PSI W_SN Arrival'] > group_df[
                'Mat PSI W_Requirement Material'],
            group_df['Mat PSI W_Requirement Material'],
            group_df['Mat PSI W_SN BOH'] + group_df['Mat PSI W_SN Arrival']
        )
    )
    # SN Short Material
    group_df['Mat PSI W_SN Short Material'] = (
            group_df['Mat PSI W_Requirement Material'] - group_df['Mat PSI W_SN Supply Material']
    )
    # SN Balance
    group_df['Mat PSI W_SN Balance'] = (
            int_init_boh + group_df['Mat PSI W_SN Arrival'].cumsum() - group_df['Mat PSI W_Requirement Material'].cumsum()
    )

    # PO 결과 추가
    # PO BOH
    group_df['Mat PSI W_PO BOH'] = po_eoh_list[:-1]
    # PO EOH
    group_df['Mat PSI W_PO EOH'] = po_eoh_list[1:]
    # PO Supply Material
    group_df['Mat PSI W_PO Supply Material'] = (
        np.where(
            group_df['Mat PSI W_PO BOH'] + group_df['Mat PSI W_SN Arrival'] + group_df['Mat PSI W_PO Arrival']
            > group_df['Mat PSI W_Requirement Material'],
            group_df['Mat PSI W_Requirement Material'],
            group_df['Mat PSI W_PO BOH'] + group_df['Mat PSI W_SN Arrival'] + group_df['Mat PSI W_PO Arrival']
        )
    )
    # PO Short Material
    group_df['Mat PSI W_PO Short Material'] = (
            group_df['Mat PSI W_Requirement Material'] - group_df['Mat PSI W_PO Supply Material']
    )
    # PO Balance
    group_df['Mat PSI W_PO Balance'] = (
            int_init_boh + (group_df['Mat PSI W_SN Arrival'] + group_df['Mat PSI W_PO Arrival']).cumsum()
            - group_df['Mat PSI W_Requirement Material'].cumsum()
    )
    
    return group_df


@_decoration_
def fn_make_bg_signal(df_p_source: pd.DataFrame, df_p_psi_w: pd.DataFrame) -> pd.DataFrame:
    """
    배경색 구분값 생성(Mat PSI W_BG Signal)
    - Con. Period 구간에 해당하면 '1' 값, LT 구간에 해당하면 '2' 값으로 세팅한다. (Default = null)
    => [STEP7-1] 시작 주차를 포함하여 Ceiling(Measure.[Mat Master_PO LT] / 7.0 에 해당하는 주차인 경우
       LT구간에 해당하여 '2' 값이 된다.
    => [STEP7-2] 위 [STEP7-1]에 해당하며, 시작 주차를 포함하여 Measure.[Mat Master_Constraint Period] 에
    해당하면 Con. Period 구간에 해당함으로 '1' 값을 세팅한다.

    :param df_p_psi_w: df_Material_PSI_W_cal
    :param df_p_source:  in_Material_Master
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # df_p_source 비어 있을 경우 빈 테이블을 반환한다.
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 34개 주차
    int_max_inx = 33
    df_p_source['lt period'] = np.ceil(df_p_source['Mat Master_PO LT'] / 7).clip(upper=int_max_inx)
    df_p_source['con period'] = df_p_source['Mat Master_Constraint Period'].clip(upper=int_max_inx)

    # Merge
    df_return = (
        df_p_psi_w
        .merge(df_p_source, how='left', on=['Sub Location.[Sub Location]', 'Item Raw Material.[Item Raw Material]'])
    )

    # Mat PSI W_BG Signal
    # 초기값 : null
    df_return['Mat PSI W_BG Signal'] = np.nan
    list_where_lt_period = df_return['week_inx'] < df_return['lt period']
    df_return.loc[list_where_lt_period, 'Mat PSI W_BG Signal'] = 2
    list_where_con_period = df_return['week_inx'] < df_return['con period']
    df_return.loc[list_where_lt_period & list_where_con_period, 'Mat PSI W_BG Signal'] = 1

    # Version
    df_return['Version.[Version Name]'] = Param_OUT_VERSION

    #  칼럼 정리
    df_return = df_return[[
        'Version.[Version Name]'
        , 'Sub Location.[Sub Location]'
        , 'Time.[Week]'
        , 'Item Raw Material.[Item Raw Material]'
        , 'Mat PSI W_BG Signal'
        , 'Mat PSI W_Inventory'
        , 'Mat PSI W_Overdue'
        , 'Mat PSI W_PO Arrival'
        , 'Mat PSI W_PO BOH'
        , 'Mat PSI W_PO Balance'
        , 'Mat PSI W_PO EOH'
        , 'Mat PSI W_PO Remain'
        , 'Mat PSI W_PO Short Material'
        , 'Mat PSI W_PO Supply Material'
        , 'Mat PSI W_Requirement'
        , 'Mat PSI W_Requirement Material'
        , 'Mat PSI W_SN Arrival'
        , 'Mat PSI W_SN BOH'
        , 'Mat PSI W_SN Balance'
        , 'Mat PSI W_SN EOH'
        , 'Mat PSI W_SN Short Material'
        , 'Mat PSI W_SN Supply Material'
        , 'Mat PSI W_Unplanned'
    ]]
    return df_return


@_decoration_
def fn_output_formatter(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # Version
    df_p_source['Version.[Version Name]'] = Param_OUT_VERSION

    df_p_source = df_p_source.rename(columns={
                                                 'Mat Master_Constraint' : 'Mat PSI Sub_Constraint'
                                               , 'Mat Master_Constraint (Filter)': 'Mat PSI Sub_Constraint (Filter)'
                                               , 'Mat Master_Group1': 'Mat PSI Sub_Group1'
                                               , 'Mat Master_Group1 (Filter)': 'Mat PSI Sub_Group1 (Filter)'
                                               , 'Mat Master_Group2':'Mat PSI Sub_Group2'
                                               , 'Mat Master_Group2 (Filter)':'Mat PSI Sub_Group2 (Filter)'
                                                })

    df_return = df_p_source[[
                              'Version.[Version Name]'
                            , 'Sub Location.[Sub Location]'
                            , 'Item Raw Material.[Item Raw Material]'
                            , 'Mat PSI Sub_Constraint'
                            , 'Mat PSI Sub_Constraint (Filter)'
                            , 'Mat PSI Sub_Group1'
                            , 'Mat PSI Sub_Group1 (Filter)'
                            , 'Mat PSI Sub_Group2'
                            , 'Mat PSI Sub_Group2 (Filter)'
                        ]]

    return df_return


@_decoration_
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """
    if str_p_cond == '0':
        col_output = [
              'Version.[Version Name]'
            , 'Sub Location.[Sub Location]'
            , 'Time.[Week]'
            , 'Item Raw Material.[Item Raw Material]'
            , 'Mat PSI W_BG Signal'
            , 'Mat PSI W_Inventory'
            , 'Mat PSI W_Overdue'
            , 'Mat PSI W_PO Arrival'
            , 'Mat PSI W_PO BOH'
            , 'Mat PSI W_PO Balance'
            , 'Mat PSI W_PO EOH'
            , 'Mat PSI W_PO Remain'
            , 'Mat PSI W_PO Short Material'
            , 'Mat PSI W_PO Supply Material'
            , 'Mat PSI W_Requirement'
            , 'Mat PSI W_Requirement Material'
            , 'Mat PSI W_SN Arrival'
            , 'Mat PSI W_SN BOH'
            , 'Mat PSI W_SN Balance'
            , 'Mat PSI W_SN EOH'
            , 'Mat PSI W_SN Short Material'
            , 'Mat PSI W_SN Supply Material'
            , 'Mat PSI W_Unplanned'
        ]
    else:
        col_output = [
              'Version.[Version Name]'
            , 'Sub Location.[Sub Location]'
            , 'Item Raw Material.[Item Raw Material]'
            , 'Mat PSI Sub_Constraint'
            , 'Mat PSI Sub_Constraint (Filter)'
            , 'Mat PSI Sub_Group1'
            , 'Mat PSI Sub_Group1 (Filter)'
            , 'Mat PSI Sub_Group2'
            , 'Mat PSI Sub_Group2 (Filter)'

        ]

    df_return = pd.DataFrame(columns=col_output)

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    pd.set_option('display.width', 400)
    pd.set_option('display.max_columns', None)

    # Output 테이블 선언
    out_Material_PSI_W = pd.DataFrame()
    out_Material_PSI_Sub = pd.DataFrame()
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

            in_Material_Master = pd.read_csv(str_input_dir + "/in_Material_Master.csv",   encoding="UTF8")
            in_Material_PSI_W = pd.read_csv(str_input_dir + "/in_Material_PSI_W.csv", dtype={"Time.[Week]": str}, encoding="UTF8")
            # in_Material_PSI_Sub = pd.read_csv(str_input_dir + "/in_Material_PSI_Sub.csv", encoding="UTF8")
            in_Version = pd.read_csv(str_input_dir + "/in_Version.csv", dtype={"Version.[Plan Week]": str}, encoding="UTF8")
            in_Time = pd.read_csv(str_input_dir + "/in_Time.csv", dtype={"Time.[Week]": str}, encoding="UTF8")

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
        fn_check_input_table(in_Material_Master, 'in_Material_Master', '1')
        fn_check_input_table(in_Material_PSI_W, 'in_Material_PSI_W', '1')
        # fn_check_input_table(in_Material_PSI_Sub, 'in_Material_PSI_Sub', '1')
        fn_check_input_table(in_Version, 'in_Version', '1')
        fn_check_input_table(in_Time, 'in_Time', '1')

        # TEST
        # in_Version['Version.[Plan Week]'] = '202546'
        ################################################################################################################
        # STEP 0-1. 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 작업 진행함.
        ################################################################################################################
        # 선처리 작업
        dict_log = {
            'p_step_no': 10,
            'p_step_desc': 'STEP 0. 전처리(in_Version): 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 '
                           '작업 진행함.',
            'p_df_name': 'df_Time'
        }
        df_Time = fn_preprocess(in_Version, in_Time, **dict_log)

        ################################################################################################################
        # STEP 0-2. in_Material_PSI_W 데이터를 34주차(Version의 Plan Week 기준) 만큼 생성한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 20,
            'p_step_desc': 'in_Material_PSI_W 데이터를 34주차 만큼 생성한다.',
            'p_df_name': 'df_Material_PSI_W_Time'
        }
        df_Material_PSI_W_Time= fn_merge_psi_week(in_Material_PSI_W, df_Time, **dict_log)

        ################################################################################################################
        # STEP1~STEP6. df_Material_PSI_W : Requirement Material,
        #              SN BOH, SN EOH, SN Supply Material, SN Short Material, SN Balance,
        #              PO BOH, PO EOH, PO Supply Material, PO Short Material, PO Balance 칼럼 생성한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 100,
            'p_step_desc': 'STEP1~STEP6. df_Material_PSI_W : Requirement Material, '
                           'SN BOH, SN EOH, SN Supply Material, SN Short Material, SN Balance, '
                           'PO BOH, PO EOH, PO Supply Material, PO Short Material, PO Balance 칼럼 생성',
            'p_df_name': 'df_Material_PSI_W_cal'
        }
        df_Material_PSI_W_cal = fn_make_material_psi_step(df_Material_PSI_W_Time, **dict_log)

        ################################################################################################################
        # 배경색 구분값 생성(Mat PSI W_BG Signal)
        # - Con. Period 구간에 해당하면 '1' 값, LT 구간에 해당하면 '2' 값으로 세팅한다. (Default = null)
        # => [STEP7-1] 시작 주차를 포함하여 Ceiling(Measure.[Mat Master_PO LT] / 7.0 에 해당하는 주차인 경우
        #    LT구간에 해당하여 '2' 값이 된다.
        # => [STEP7-2] 위 [STEP7-1]에 해당하며, 시작 주차를 포함하여 Measure.[Mat Master_Constraint Period] 에 해당하면
        # Con. Period 구간에 해당함으로 '1' 값을 세팅한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 200,
            'p_step_desc': '배경색 구분값 생성(Mat PSI W_BG Signal)'
                           '- Con. Period 구간에 해당하면 "1" 값, LT 구간에 해당하면 "2" 값으로 세팅한다. (Default = null)'
                           '=> [STEP7-1] 시작 주차를 포함하여 Ceiling(Measure.[Mat Master_PO LT] / 7.0 에 '
                           '해당하는 주차인 경우 LT구간에 해당하여 "2" 값이 된다.'
                           '=> [STEP7-2] 위 [STEP7-1]에 해당하며, 시작 주차를 포함하여 '
                           'Measure.[Mat Master_Constraint Period] 에 해당하면Con. Period 구간에 해당함으로 "1"  세팅한다.'
                           '하여 최종 out_Material_PSI_W 정리.',
            'p_df_name': 'out_Material_PSI_W'
        }
        out_Material_PSI_W = fn_make_bg_signal(in_Material_Master, df_Material_PSI_W_cal, **dict_log)

        ################################################################################################################
        # 최종 Output 정리
        ################################################################################################################
        out_Material_PSI_Sub = fn_output_formatter(in_Material_Master)
        logger.Step(p_step_no=300, p_step_desc='out_Material_PSI_Sub 생성.')
        fn_log_dataframe(out_Material_PSI_Sub, 'out_Material_PSI_Sub')

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_Material_PSI_W = None
            out_Material_PSI_Sub = None
            raise Exception(e)
        else:
            if out_Material_PSI_W.empty:
                out_Material_PSI_W = fn_set_header('0')
                fn_log_dataframe(out_Material_PSI_W, 'out_Material_PSI_W')
            if out_Material_PSI_Sub.empty:
                out_Material_PSI_Sub = fn_set_header('1')
                fn_log_dataframe(out_Material_PSI_Sub, 'out_Material_PSI_Sub')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_Material_PSI_W.empty:
            out_Material_PSI_W = fn_set_header('0')
            fn_log_dataframe(out_Material_PSI_W, 'out_Material_PSI_W')
        if out_Material_PSI_Sub.empty:
            out_Material_PSI_Sub = fn_set_header('1')
            fn_log_dataframe(out_Material_PSI_Sub, 'out_Material_PSI_Sub')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')

