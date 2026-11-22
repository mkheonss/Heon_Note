"""
* 프로그램명
    - PY_UI_OrderStatusMFG_REG.py
* 내용
    - 입력에 대한 해당 정보를 Loading Order Mgmt화면 값으로 입력해줌

* 변경이력
    - 2025.09.17 / daeun01.yun / Create

* Flow Summary
    Step1.

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
- in_Order_Status_MFG
    Select ([Version].[Version Name].CurrentWorkingView * [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Ship To] * [Time].[Day] * [Common Code Master].[Master Code] ) on row, ({Measure.[Order Status Mfg Week_RDD Week], Measure.[Order Status Mfg Week_SO], Measure.[Order Status Mfg Week_SO Item], Measure.[Order Status Mfg Week_Mfg Week], Measure.[Order Status Mfg Week_Ship To], Measure.[Order Status Mfg Week_Ship To Name], Measure.[Order Status Mfg Week_Qty], Measure.[Order Status Mfg Week_Confirmed By]}) on column where {Measure.[Order Status Mfg Week_Chk Flag] == "Y", Measure.[Order Status Mfg Week_Confirmed By] == CurrentUser().[User Name]};
    Select (
        [Version].[Version Name].CurrentWorkingView
        * [Sub Location].[Sub Location]
        * [Seq].[Seq]
        * [Item].[Item]
        * [Location].[Location]
        * [Sales Domain].[Ship To]
        * [Time].[Day]
        * [Common Code Master].[Master Code]
    ) on row,
    ({
        Measure.[Order Status Mfg Week_RDD Week]
        , Measure.[Order Status Mfg Week_SO]
        , Measure.[Order Status Mfg Week_SO Item]
        , Measure.[Order Status Mfg Week_Mfg Week]
        , Measure.[Order Status Mfg Week_Ship To]
        , Measure.[Order Status Mfg Week_Ship To Name]
        , Measure.[Order Status Mfg Week_Qty]
        , Measure.[Order Status Mfg Week_Confirmed By]
    }) on column
    where {
        Measure.[Order Status Mfg Week_Chk Flag] == "Y"
        , Measure.[Order Status Mfg Week_Confirmed By] == CurrentUser().[User Name]
    };
########## Loading Type & Cntr Type을 위한 Method 마스터 테이블 input ##################################################
- in_Loading_Method_Ship_To
    Select ([Version].[Version Name].CWV_MP * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Seq].[Seq] * [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To]) on row, ({Measure.[Loading Method Ship To_Ship To],Measure.[Loading Method Ship To_Default],Measure.[Loading Method Ship To_Valid Flag]}) on column;
    Select (
        [Version].[Version Name].CWV_MP
        * [Loading Type].[Loading Type]
        * [Sub Location].[Sub Location]
        * [Seq].[Seq]
        * [Location].[Location]
        * [Container].[ContainerID]
        * [Sales Domain].[Ship To]
    ) on row
    , ({
        Measure.[Loading Method Ship To_Ship To]
        , Measure.[Loading Method Ship To_Default]
        , Measure.[Loading Method Ship To_Valid Flag]
    }) on column;

- in_Loading_Method_Account
    Select ([Version].[Version Name].CWV_MP * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To] ) on row, ({Measure.[Loading Method Account_Default], Measure.[Loading Method Account_Valid Flag]}) on column;
    Select (
        [Version].[Version Name].CWV_MP
        * [Loading Type].[Loading Type]
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Container].[ContainerID]
        * [Sales Domain].[Ship To]
    ) on row
    , ({
        Measure.[Loading Method Account_Default]
        , Measure.[Loading Method Account_Valid Flag]
    }) on column;

- in_Loading_Method_To_Site
    Select ([Version].[Version Name].CWV_MP * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] * [Loading Type].[Loading Type]) on row, ({Measure.[Loading Method To Site_Default], Measure.[Loading Method To Site_Valid Flag]}) on column;
    Select (
        [Version].[Version Name].CWV_MP
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Container].[ContainerID]
        * [Loading Type].[Loading Type]
    ) on row
    , ({
        Measure.[Loading Method To Site_Default]
        , Measure.[Loading Method To Site_Valid Flag]
    }) on column;
- in_Loading_Method_From
    Select ([Version].[Version Name].CWV_MP * [Loading Type].[Loading Type] * [Shipment Type].[Shipment Type] * [Sub Location].[Sub Location] * [Container].[ContainerID] ) on row, ({Measure.[Loading Method From Site_Default],  Measure.[Loading Method From Site_Valid Flag]}) on column;
    Select (
        [Version].[Version Name].CWV_MP
        * [Loading Type].[Loading Type]
        * [Shipment Type].[Shipment Type]
        * [Sub Location].[Sub Location]
        * [Container].[ContainerID]
    ) on row
    , ({
        Measure.[Loading Method From Site_Default]
        ,  Measure.[Loading Method From Site_Valid Flag]
    }) on column;

-in_Loading_Dir_Order_Mgmt
    Select ([Version].[Version Name].CWV_MP * [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Account] * [Time].[Week] ) on row,({Measure.[Loading Dir Order Mgmt_Sales Order]}) on column orderby [Seq].[Seq].Key Desc limit 1;
    Select (
        [Version].[Version Name].CWV_MP
        * [Sub Location].[Sub Location]
        * [Seq].[Seq]
        * [Item].[Item]
        * [Location].[Location]
        * [Sales Domain].[Account]
        * [Time].[Week]
    ) on row
    ,({
        Measure.[Loading Dir Order Mgmt_Sales Order]
    }) on column orderby [Seq].[Seq].Key Desc limit 1;

* Output Tables
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
          Measure.[Loading Dir Order Mgmt_Sales Order]
        , Measure.[Loading Dir Order Mgmt_Adj Prod Week]
        , Measure.[Loading Dir Order Mgmt_Ship To]
        , Measure.[Loading Dir Order Mgmt_Ship To Name]
        , Measure.[Loading Dir Order Mgmt_Loading Type]
        , Measure.[Loading Dir Order Mgmt_Cntr Type]
        , Measure.[Loading Dir Order Mgmt_Origin Qty]
        , Measure.[Loading Dir Order Mgmt_Chk Qty]
        , Measure.[Loading Dir Order Mgmt_Created By]
        , Measure.[Loading Dir Order Mgmt_Creation Time]
    }) on column;

// output 삭제.
Scope: (
    [Version].[Version Name].CWV_MP
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Sales Domain].[Ship To]
        * [Item].[Item]
        * [Time].[Week]
        * [Seq].[Seq]
);
    Measure.[Loading Dir Order Mgmt_Sales Order]= null;
    Measure.[Loading Dir Order Mgmt_Adj Prod Week]= null;
    Measure.[Loading Dir Order Mgmt_Ship To]= null;
    Measure.[Loading Dir Order Mgmt_Ship To Name]= null;
    Measure.[Loading Dir Order Mgmt_Loading Type]= null;
    Measure.[Loading Dir Order Mgmt_Cntr Type]= null;
    Measure.[Loading Dir Order Mgmt_Origin Qty]= null;
    Measure.[Loading Dir Order Mgmt_Chk Qty]= null;
    Measure.[Loading Dir Order Mgmt_Created By]= null;
    Measure.[Loading Dir Order Mgmt_Creation Time]= null;
end scope;

* Flow Summary

* Validation :

* Execution :
1. EXEC 파이썬 모듈 실행
EXEC plugin instance [PY_UI_OrderStatusMFG_REG]
                 for measures { [Order Status Mfg Week_Chk Flag] }
                    using scope ([Version].[Version Name])
                    using arguments {(ExecutionMode, "MediumWeight")
                                  , (Param_OUT_VERSION, "CWV_MP")
                                  , (Param_User_Name , CurrentUser().[User Name])
                                  , (MaxSliceTableCells, 200000000)
                                  , (MaxConcurrency, 1 )
                                  , (IncludeNullRows, False)
                                  , ([Param.o9_sys_log_level], "DEBUG")
                                  }
                    ;

2. out Measure그룹 모든 Measure 데이터 삭제
delete data for model [Loading Dir Order Mgmt] where {[Version].[Version Name].[CWV_MP]};
"""
import os.path
import time
import datetime
import pandas as pd
import numpy as np
import numpy as np
import traceback
import re
import inspect
from NSCMCommon import NSCMCommon as common

# Local 개발 시에 필요한 공통 변수 선언
# o9에 저장된 instanceName
str_instance = "PY_UI_OrderStatusMFG_REG"
str_input_dir = "Input/UIOrderStatusMFGREG"
str_output_dir = "Output/UIOrderStatusMFGREG"
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
    # out_LoadingDirMgmt
    if str_p_cond == '0':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Sales Domain.[Ship To]': [], 'Item.[Item]': [], 'Time.[Week]': [], 'Seq.[Seq]': [],
                'Loading Dir Order Mgmt_Sales Order': [], 'Loading Dir Order Mgmt_SO Item': [],
                'Loading Dir Order Mgmt_RDD Week': [],
                'Loading Dir Order Mgmt_Adj Prod Week': [],
                'Loading Dir Order Mgmt_Ship To': [], 'Loading Dir Order Mgmt_Ship To Name': [],
                'Loading Dir Order Mgmt_Loading Type': [],
                'Loading Dir Order Mgmt_Cntr Type': [], 'Loading Dir Order Mgmt_Origin Qty': [],
                'Loading Dir Order Mgmt_Chk Qty': []
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
        # list_columns_all_rename.append(col.rstrip('_x'))
        list_columns_all_rename.append(re.sub('_x$', '', col))
    df_p_source.columns = list_columns_all_rename

    return df_p_source

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
        if column == 'Ship To.[Ship To Party]':
            df_return['Ship To.[Ship To Party]'] = df_return['Ship To.[Ship To Party]'].astype('str')
        elif column == 'Shipment To.[Shipment To]':
            df_return['Shipment To.[Shipment To]'] = df_return['Shipment To.[Shipment To]'].astype('str')
        elif column == 'Loading Method Ship To_Ship To':
            df_return['Loading Method Ship To_Ship To'] = df_return['Loading Method Ship To_Ship To'].astype('str')
        elif column == 'Loading Dir Order Mgmt_Loading Type':
            df_return['Loading Dir Order Mgmt_Loading Type'] = df_return['Loading Dir Order Mgmt_Loading Type'].astype('str')
        elif column == 'Loading Dir Order Mgmt_Cntr Type':
            df_return['Loading Dir Order Mgmt_Cntr Type'] = df_return['Loading Dir Order Mgmt_Cntr Type'].astype('str')
    # 컬럼 공백문자열일때 np.nan으로 replace
    df_return[df_return.select_dtypes(['object']).columns] = df_return.select_dtypes(['object']).apply(
        lambda x: x.replace(r'^\s*$', np.nan, regex=True)
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

    # Version.[Version Name] 컬럼의 값을 Parameter로 받은 값으로 변경
    df_return.insert(0, 'Version.[Version Name]', str_p_out_version)

    # 구분자 정의(단계-output 코드)
    p_cond = str_p_cond

    # 결과 테이블에서 필요한 컬럼만을 추출하고 순서를 변경하여 저장한다.

    if p_cond == '0' :
        df_return = df_return[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
                'Sales Domain.[Ship To]','Item.[Item]', 'Time.[Week]', 'Seq.[Seq]',
                'Loading Dir Order Mgmt_Sales Order',  'Loading Dir Order Mgmt_SO Item',
                'Loading Dir Order Mgmt_RDD Week',
                'Loading Dir Order Mgmt_Adj Prod Week',
                'Loading Dir Order Mgmt_Ship To', 'Loading Dir Order Mgmt_Ship To Name', 'Loading Dir Order Mgmt_Loading Type',
                'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Origin Qty', 'Loading Dir Order Mgmt_Chk Qty'
            ]
        ]
    elif p_cond == '1':
        # Loading Dir Order Mgmt_Chk Grain :  week + from + to + account + seq + item
        str_grain_key = (
                df_return['Time.[Week]'].astype(str) + '_' +
                df_return['Sub Location.[Sub Location]'].astype(str) + '_' +
                df_return['Location.[Location]'].astype(str) + '_' +
                df_return['Sales Domain.[Ship To]'].astype(str) + '_' +
                df_return['Seq.[Seq]'].astype(str) + '_' +
                df_return['Item.[Item]'].astype(str)
        )

        df_return['Loading Dir Order Mgmt_Chk Grain'] = str_grain_key

        df_return = df_return[
            ['Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
             'Sales Domain.[Ship To]', 'Item.[Item]', 'Time.[Week]', 'Seq.[Seq]',
             'Loading Dir Order Mgmt_Sales Order', 'Loading Dir Order Mgmt_SO Item',
             'Loading Dir Order Mgmt_Prod Week', 'Loading Dir Order Mgmt_Adj Prod Week',
             'Loading Dir Order Mgmt_Ship To', 'Loading Dir Order Mgmt_Ship To Name',
             'Loading Dir Order Mgmt_Loading Type',
             'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Origin Qty', 'Loading Dir Order Mgmt_Chk Qty',
             'Loading Dir Order Mgmt_Created By', 'Loading Dir Order Mgmt_Creation Time',
             # 'Loading Dir Order Mgmt_Valid Fail Reason',
             'Loading Dir Order Mgmt_Chk Grain'
             ]
        ]
    # 결과 리턴
    return df_return

@_decoration_
def fn_update_empty_loadingtype_containerid(
        df_p_dirOrderStatus: pd.DataFrame, df_p_loadingMethods: pd.DataFrame,
        list_p_dirOrderStatusCol: list, list_p_loadingMethodsCol: list,
        str_method_type: str
) -> pd.DataFrame:
    """
    :param df_p_dirOrderStatus: Mgmt Upload 데이타프레임
    :param df_p_loadingMethods: from ~ ship to Methods 데이타프레임
    :param list_p_dir_order_status_columns: Mgmt Upload 사용될 columns List
    :param list_p_loading_methods_columns: methods 사용될 columns List
    :param str_method_type: ship to ~ from lane load
    :return: df_return
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 파라미터 테이블(df_p_source)이 비어 있는 경우 빈 데이터프레임을 리턴하면서 함수를 종료한다.
    if df_p_dirOrderStatus.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_dirOrderStatus)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return
    if df_p_loadingMethods.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_methods) ' + str_method_type + '가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_dirOrderStatus

    # Valid Flag, Default 모두가 'Y'인 row 가져온 df만 생성
    query_string = f'`Loading Method {str_method_type}_Default` == "Y" & `Loading Method {str_method_type}_Valid Flag` == "Y"'
    df_methods_default_valid_Y = df_p_loadingMethods.query(query_string)

    # 로컬이면서 'Loading Dir Order Mgmt_Ship To' 컬럼이 존재 하면 타입때문에 에러나는 부분 발생으로 추가
    if is_local & ('Loading Dir Order Mgmt_Ship To' in df_p_dirOrderStatus.columns):
        df_p_dirOrderStatus['Loading Dir Order Mgmt_Ship To'] = df_p_dirOrderStatus['Loading Dir Order Mgmt_Ship To'].astype('str')

    df_p_dirOrderStatus = pd.merge(
        df_p_dirOrderStatus, df_methods_default_valid_Y,
        left_on=list_p_dirOrderStatusCol, right_on=list_p_loadingMethodsCol,
        how='left', indicator=True
    )
    # 컬럼중복제거
    df_p_dirOrderStatus = fn_merge_after(df_p_dirOrderStatus)
    df_p_dirOrderStatus.loc[
        (df_p_dirOrderStatus['_merge'] == 'both') &
        (df_p_dirOrderStatus['Loading Dir Order Mgmt_Cntr Type'].isna()) &
        (df_p_dirOrderStatus['Loading Dir Order Mgmt_Loading Type'].isna()),
        ['Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Loading Type']
    ] = df_p_dirOrderStatus.loc[
        (df_p_dirOrderStatus['_merge'] == 'both') &
        (df_p_dirOrderStatus['Loading Dir Order Mgmt_Cntr Type'].isna()) &
        (df_p_dirOrderStatus['Loading Dir Order Mgmt_Loading Type'].isna()),
        ['Container.[ContainerID]', 'Loading Type.[Loading Type]']
    ].values
    # _merge & merge로 인한 계속 생성되어 오류를 일으키는 컬럼 삭제
    list_drop_col = [
        '_merge', 'Version.[Version Name]', 'Container.[ContainerID]', 'Loading Type.[Loading Type]',
        'Loading Method ' + str_method_type + '_Default', 'Loading Method ' + str_method_type + '_Valid Flag'
    ]
    if str_method_type == 'From Site':
        list_drop_col.append('Shipment Type.[Shipment Type]')
    list_drop_col.extend(list_drop_col)
    df_p_dirOrderStatus.drop(list_drop_col, axis=1, inplace=True)

    return df_p_dirOrderStatus


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()
    # Output 테이블 선언
    out_LoadingDirMgmt = pd.DataFrame()
    out_LoadingOrderStatus = pd.DataFrame()
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            Param_OUT_VERSION = 'CWV_MP'
            Param_PLANTYPE = ''
            Param_User_Name = 'DaeUn Yun'
            in_Order_Status_MFG = pd.read_csv(str_input_dir + "/in_Order_Status_MFG.csv", encoding="UTF8")
            in_Loading_Method_Ship_To = pd.read_csv(str_input_dir + "/in_Loading_Method_Ship_To.csv", encoding="UTF8")
            in_Loading_Method_Account = pd.read_csv(str_input_dir + "/in_Loading_Method_Account.csv", encoding="UTF8")
            in_Loading_Method_To_Site = pd.read_csv(str_input_dir + "/in_Loading_Method_To_Site.csv", encoding="UTF8")
            in_Loading_Method_From = pd.read_csv(str_input_dir + "/in_Loading_Method_From.csv", encoding="UTF8")
            in_Loading_Dir_Order_Mgmt = pd.read_csv(str_input_dir + "/in_Loading_Dir_Order_Mgmt.csv", encoding="UTF8")

        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')

        fn_check_input_table(in_Order_Status_MFG, 'in_Order_Status_MFG', '0')

        #  DataFrame 컬럼 선처리
        in_Loading_Method_Ship_To = fn_preprocess(in_Loading_Method_Ship_To)
        # ##############################################################################################################
        # Step-1 out테이블 out_LoadingDirMgmt 구성
        # out테이블 out_LoadingDirMgmt에 필요한 measure를 in테이블 in_Loading_Order_Status에서 가져와 만들기
        # ##############################################################################################################
        out_LoadingDirMgmt = out_LoadingDirMgmt.assign(
            **{
                'Seq.[Seq]': in_Order_Status_MFG['Seq.[Seq]']
                , 'Sub Location.[Sub Location]': in_Order_Status_MFG['Sub Location.[Sub Location]']
                , 'Location.[Location]': in_Order_Status_MFG['Location.[Location]']
                , 'Sales Domain.[Ship To]': in_Order_Status_MFG['Sales Domain.[Ship To]']
                , 'Item.[Item]': in_Order_Status_MFG['Item.[Item]']
                , 'Time.[Week]': in_Order_Status_MFG['Order Status Mfg Week_RDD Week']
                , 'Loading Dir Order Mgmt_Sales Order': in_Order_Status_MFG['Order Status Mfg Week_SO']
                , 'Loading Dir Order Mgmt_SO Item': in_Order_Status_MFG['Order Status Mfg Week_SO Item']
                , 'Loading Dir Order Mgmt_Prod Week': in_Order_Status_MFG['Order Status Mfg Week_Mfg Week']
                , 'Loading Dir Order Mgmt_Adj Prod Week': in_Order_Status_MFG['Order Status Mfg Week_Mfg Week']
                , 'Loading Dir Order Mgmt_Ship To': in_Order_Status_MFG['Order Status Mfg Week_Ship To']
                , 'Loading Dir Order Mgmt_Ship To Name': in_Order_Status_MFG['Order Status Mfg Week_Ship To Name']
                , 'Loading Dir Order Mgmt_Origin Qty': in_Order_Status_MFG['Order Status Mfg Week_Qty']
                , 'Loading Dir Order Mgmt_Chk Qty': in_Order_Status_MFG['Order Status Mfg Week_Qty']
                # , 'Loading Dir Order Mgmt_Valid Fail Reason': in_Order_Status_MFG['Order Status Mfg Week_Order Reason']
            }
        )
        # ##############################################################################################################
        # 'Ship To' ~ 'From' Lane Load Master Measure그룹을 차례대로 merge를 위한 컬럼 list
        # ##############################################################################################################
        list_orderstatus_use_columns = [
            'Sub Location.[Sub Location]', 'Location.[Location]',
            'Sales Domain.[Ship To]', 'Loading Dir Order Mgmt_Ship To'
        ]
        list_loading_methods_use_columns = [
            'Sub Location.[Sub Location]', 'Location.[Location]',
            'Sales Domain.[Ship To]', 'Loading Method Ship To_Ship To'
        ]
        # ##############################################################################################################
        # # # Step1-1 out_LoadingDirMgmt 의  Loading Dir Order Mgmt_Cntr Type 채우기
        # ##############################################################################################################
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Cntr Type'] = np.nan
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Loading Type'] = np.nan
        # 1. Ship To Lane Load Master Measure Group 매칭
        dict_log = {
            'p_step_no': 110,
            'p_step_desc': 'Order Status MFG 메져와 Loading Method>Ship To에서 필요 Loading Type measure가져오기',
            'p_df_name': 'out_LoadingDirMgmt'
        }
        # Method 'Ship To' 함수 호출
        out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
            out_LoadingDirMgmt, in_Loading_Method_Ship_To,
            list_orderstatus_use_columns[:], list_loading_methods_use_columns[:],
            'Ship To', **dict_log
        )
        dict_log = {
            'p_step_no': 120,
            'p_step_desc': 'Order Status MFG 메져와 Loading Method>Account 에서 필요 Loading Type measure가져오기',
            'p_df_name': 'out_LoadingDirMgmt'
        }
        # Method 'Account' 함수 호출
        out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
            out_LoadingDirMgmt, in_Loading_Method_Account,
            list_orderstatus_use_columns[:3], list_loading_methods_use_columns[:3],
            'Account', **dict_log
        )
        dict_log = {
            'p_step_no': 130,
            'p_step_desc': 'Order Status MFG 메져와 Loading Method>To Site 에서 필요 Loading Type measure가져오기',
            'p_df_name': 'out_LoadingDirMgmt'
        }
        # Method 'To Site' 함수 호출
        out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
            out_LoadingDirMgmt, in_Loading_Method_To_Site,
            list_orderstatus_use_columns[:2], list_loading_methods_use_columns[:2],
            'To Site', **dict_log
        )
        dict_log = {
            'p_step_no': 140,
            'p_step_desc': 'Order Status MFG 메져와 Loading Method>From Site 에서 필요 Loading Type measure가져오기',
            'p_df_name': 'out_LoadingDirMgmt'
        }
        # Method 'From Site' 함수 호출
        out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
            out_LoadingDirMgmt, in_Loading_Method_From,
            list_orderstatus_use_columns[:1], list_loading_methods_use_columns[:1],
            'From Site', **dict_log
        )
        # ###########################################################################################
        # 최종seq 만들기
        # ###########################################################################################
        int_seq = 1
        if not in_Loading_Dir_Order_Mgmt.empty:
            int_seq = int(
                in_Loading_Dir_Order_Mgmt[
                    'Seq.[Seq]'
                ].astype(int).max()
            ) + 1
        out_LoadingDirMgmt['Seq.[Seq]'] = range(int_seq, int_seq + len(out_LoadingDirMgmt))
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Created By'] = Param_User_Name
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Creation Time'] = datetime.datetime.now()

        out_LoadingDirMgmt = fn_output_formatter(out_LoadingDirMgmt, Param_OUT_VERSION, '1')

        # Chk Flag null 로 업데이트 ( 사용자 가 chk한 값 원복 )
        list_where = in_Order_Status_MFG['Order Status Mfg Week_Confirmed By'] == Param_User_Name
        out_OrderStatusMFG = in_Order_Status_MFG[list_where]
        out_OrderStatusMFG['Order Status Mfg Week_Chk Flag'] = np.nan
        out_OrderStatusMFG = out_OrderStatusMFG[
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Sales Domain.[Ship To]',
                'Item.[Item]', 'Time.[Day]', 'Common Code Master.[Master Code]', 'Seq.[Seq]', 'Order Status Mfg Week_Chk Flag'
            ]
        ]
        # 출력 변수 확인용 로그
        fn_log_dataframe(out_LoadingDirMgmt, 'out_LoadingDirMgmt')
        fn_log_dataframe(out_OrderStatusMFG, 'out_OrderStatusMFG')

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
        if out_LoadingDirMgmt.empty:
            out_LoadingDirMgmt = fn_set_header('0')
            fn_log_dataframe(out_LoadingDirMgmt, 'out_LoadingDirMgmt')
