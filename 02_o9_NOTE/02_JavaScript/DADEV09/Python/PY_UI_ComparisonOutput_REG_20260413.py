"""
* 프로그램명
    - PY_UI_ComparisonOutput_REG

* 내용
    -
* 변경이력
    - 2025.08.19 / Kang Gyeonghun / Create

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를 결정하는 파라미터

* Input Tables
    - in_OBOCapacityRCA
        Select (Version.[Version Name] * FROM.[RootCause].[Problem Type] * FROM.[Time].[Week]
             * FROM.[Location].[Location] * FROM.[Resource].[Resource] * FROM.[Activity1].[Activity1]
             * FROM.[Activity2].[Activity Type2] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3]
             * TO.[Demand].[DemandID] * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Item].[Item]) on row
             , ({Edge.[002.009W Solver Outputs OBO Capacity RCA].[W OBO Capacity Constraint Quantity]
               , Edge.[002.009W Solver Outputs OBO Capacity RCA].[W MP RCA Type OBO Capacity]}) on column
         where {RelationshipType.[002.009W Solver Outputs OBO Capacity RCA]}
        ;

    - in_OBOMaterialRCA
        Select (Version.[Version Name] * FROM.[RootCause].[Problem Type] * FROM.[Time].[Week]
             * FROM.[Location].[Location] * FROM.[Item].[Item] * FROM.[Activity1].[Activity1]
             * FROM.[Activity2].[Activity Type2] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3]
             * TO.[Demand].[DemandID] * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Item].[Item]) on row
             , ({Edge.[002.008W Solver Outputs OBO Material RCA].[W OBO Material Constraint Quantity]
               ,Edge.[002.008W Solver Outputs OBO Material RCA].[W MP RCA Type OBO Material]}
             * {Measure.[W Activity Lead Time]@(FROM.[Activity1].[Activity1]
               , FROM.[Activity2].[Activity2],FROM.[Activity3].[Activity3])}
             * {Measure.[W Activity Mandatory Offset]@(FROM.[Activity1].[Activity1]
               , FROM.[Activity2].[Activity2]
               , FROM.[Activity3].[Activity3])}) on column
         where {RelationshipType.[002.008W Solver Outputs OBO Material RCA]}
        ;

    - in_Demand
        Select ([Version].[Version Name] * [Item].[Item]*[Item].[ItemSet]*[Item].[ItemSetIn]*[Item].[ItemSetOut]
             * [Location].[Location] * [Sales Domain].[Customer Group] * [Demand Type].[Demand Type] * [Time].[Week]
             * [Demand].[DemandID]) on row
             , ({Measure.[W Demand Quantity], Measure.[W Demand Short Code], Measure.[W Total Met On Time Quantity]
             , Measure.[Item Site Sales Price_USD Price]}) on column
         where {Association(Measure.[W Demand Quantity]>0)}
        ;

    - in_CurrentWeek
        select (&CurrentWeek)
        ;

    - in_Shipment
        Select ([Version].[Version Name] * [Item].[Item] * [Activity1].[To Location] * [Time].[Week]) on row
             , ({Measure.[W Material Consumption Quantity Plan Output]}) on column
        where {Location.[Location Type].[MF]}
        ;

    - in_Arrival
        Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Time].[Week]) on row
             , ({Measure.[W Material Production Quantity Plan Output]}) on column
         where {[Activity1].[From Location].filter(#.Name Startswith("P"))}
        ;

    - in_intr
        Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location]
             * [Documents].[OrderlineID].filter(#.Name startswith("INT")) * [Time].[Week]) on row
             , ({Measure.[W Material Production Quantity Plan Output]}) on column
        ;

    - in_intr_fromsite
        Select ([Version].[Version Name] * [Documents].[OrderlineID]) on row
             , ({Measure.[Intr_From Site ID]}) on column
         where {Measure.[Intr_From Site ID] startswith("P")}
        ;

    - in_PSI
        Select ([Version].[Version Name] * [Item].[Item] * [Item].[ItemSet] * [Item].[ItemSetIn] * [Item].[ItemSetOut]
             * [Location].[Location Type].[DC].relatedmembers([Location])*[Time].[Week]) on row
             , ({Measure.[W Ending On Hand], Measure.[W Beginning On Hand]}) on column
        ;

    - in_WeekDay
        Select ([Version].[Version Name] * &CurrentAndFuturePlanningWeeks * [Time].[Day]) on row
             , ({Measure.[Assortment For Week to First Day]}) on column
        ;

* Output Tables
    - out_Sales
        Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Customer Group]
             * [Time].[Week]) on row
             , ({Measure.[Comparison Output UI_Demand], Measure.[Comparison Output UI_GI]
             , Measure.[Comparison Output UI_RTF], Measure.[Comparison Output UI_Sales]
             , Measure.[Comparison Output UI_Short]}) on column
        ;

    - out_PSI
        Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Time].[Week]) on row
             , ({Measure.[Comparison PSI UI_Arrival], Measure.[Comparison PSI UI_BOH], Measure.[Comparison PSI UI_EOH]
             , Measure.[Comparison PSI UI_Shipment]}) on column
        ;

    - out_RCA
        Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Customer Group]
             * [Demand Type].[Demand Type] * [Time].[Week] * [Demand].[DemandID]) on row
             , ({Measure.[BOD_EFFECTIVENESS], Measure.[BOM_EFFECTIVENESS], Measure.[CH_CONSTRAINT]
             , Measure.[Capacity TTL], Measure.[EOL], Measure.[FLUCTUATION], Measure.[FROZEN], Measure.[HOLIDAY]
             , Measure.[INV_RISK_AP2], Measure.[LINE], Measure.[MATERIAL], Measure.[Material TTL], Measure.[NO_BOD]
             , Measure.[NO_BOM], Measure.[NPI], Measure.[Others], Measure.[PBC], Measure.[TOOL]
             , Measure.[Comparison RCA UI_Demand], Measure.[Comparison RCA UI_RTF]
             , Measure.[Comparison RCA UI_Short]}) on column
        ;

* Flow Summary
    Step 1-1. in_Demand에서 W Demand Short Code 값이 "FLUCTUATION" 일경우 행 삭제, W Total Met On Time Quantity값을 fillna(0)
    Step 1-2. [Item].[Item]이 'IO-'로 시작하는 경우, 해당 행을 2개의 행으로 분리,
        - 기존 IO-로 시작하는 Item이 있는 행의 Item 값을 Item.ItemSetIn/Item.ItemSetOut으로 분리하여 2개의 행 생성
        - 기존 IO-로 시작하는 Item이 있는 행은 삭제

    Step 2. Step 1의 df로 부터, Item.[Item], Location.[Location], Sales Domain.[Customer Group],
            Time.[Week]으로 Group By하여 아래처럼 계산하여 out_Sales 정리
        Comparison Output UI_Demand = Sum(W Demand Quantity)
        Comparison Output UI_GI = Sum(W Total Met On Time Quantity)
        Comparison Output UI_Sales =  Sum(W Total Met On Time Quantity)
        Comparison Output UI_RTF = Sum(W Total Met On Time Quantity)
        Comparison Output UI_Short = Sum(W Demand Quantity-W Total Met On Time Quantity])

    Step 3-1.in_PSI의 column명을 다음과 같이 변경
        Measure.[Comparison PSI UI_BOH] = Measure.[W Beginning On Hand];
        Measure.[Comparison PSI UI_EOH] = Measure.[W Ending On Hand];
    Step 3-2. in_Shipment의 [Activity1].[To Location]을 Location.[Location]으로 컬럼명 변경하여
              Item Location Week에 대하여 Comparison PSI UI_Shipment = Material Consumption Quantity Plan Output
    Step 3-3. in_intr과 in_intr_fromsite를 Documents.[OrderlineID]으로 inner join 후,
              Item, Location, Week으로 Group By Sum(W Material Production Quantity Plan Output) as IntrQty
              위의 df를 in_Arrival의 Item Location Week와 full outer join 하고 IntrQty,
              W Material Production Quantity Plan Output를 fillna(0),
              Comparison PSI UI_Arrival = W Material Production Quantity Plan Output+IntrQty
    Step 3-4. 3-1을 기준으로, 3-2, 3-3 df를 ITem, Location, Week으로 Left join하여 out_PSI 정리
             그 이후 [Item].[Item]이 'IO-'로 시작하는 경우, 해당 행을 2개의 행으로 분리,
        -  기존 Item.Item의 값 대신 Item.ItemSetIn/Item.ItemSetOut으로 쪼개줌
        - 기존 데이터는 삭제

    Step 4-1. OBOMaterialRCA 의 Shortreason이 NO_BOD, BOM_EFFECTIVENESS 이거나,
              Activity2.[Activity Type2]` == "Distribution" 인 경우
              From Time은 최소값,
              002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material](short QTY)를 sum하여 Group by하고,
              From Time(Problem dttm)이 실제 To.[Time].[Week]보다 클 경우, From Time을 To.[Time].[Week]으로 변경
    Step 4-2. Step 4-1 df에서 Activity2.[Activity Type2]` == "Distribution"인 경우,
              (From.[Time].[Week]-002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]
              -002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset]) < CurrentWeek 이라면,
              002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]를 'PBC'로 값 변경, 아니면 그대로 둠
    Step 4-3. OBOCapacityRCA와  Step4-2의 df를 아래와 같이 column명 변경후, "to.[Demand].[DemandID]"와 Orgproblem Type만 남김
        "002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]": "Orgproblem Type",
        "002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]": "Orgproblem Type",
    Step 4-4. "to.[Demand].[DemandID]" 별로 Orgproblem Type를 아래와 같이 정렬후, 맨 위의 값만 남기고 삭제
            list_sort_order = [
                'NO_BOM',
                'NO_BOD',
                'BOD_EFFECTIVENESS',
                'BOM_EFFECTIVENESS',
                'FROZEN',
                'PBC',
                'EOL',
                'MATERIAL',
                'TOOL',
                'LINE'
            ]
    Step 4-5. Step1.의 df의 demandID 별로 step4-4를 Left Join,
              W Demand Quantity-W Total Met On Time Quantity > 0인 데이터 중
              orgproblem type이 없으면 Measure.[W Demand Short Code] 값을 넣어줌
    Step 4-6. 4-5 df에서 각 orgproblem type이  컬럼명으로, W Demand Quantity-W Total Met On Time Quantity값을 넣어주어 out_RCA 정리
        EOL, TOOL, LINE일 경우 Capacity TTL에도 W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        NO_BOD, BOD_EFFECTIVENESS, NO_BOM, BOM_EFFECTIVENESS, FROZEN, PBC, MATERIAL일 경우,
        Material TTL에도 W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        CH_CONSTRAINT, INV_RISK_AP2일 경우, W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        아래 3개 컬럼은 전체 행에 대하여 계산
        W Demand Quantity==> Comparison RCA UI_Demand
        W Total Met On Time Quantity==> Comparison RCA UI_RTF
        W Demand Quantity-W Total Met On Time Quantity==> Comparison RCA UI_Short

* Validation :

* Execution :
    1. 기존 메저 데이터 삭제(nullify)
        delete data for model [Mix Load Master]
            where { [Version].[Version Name].[CWV_LD] }

    2. Plugin Call하여 신규 MG 생성
    1) LightWeight
    EXEC plugin instance [PY_UI_ComparisonOutput_REG]
        for measures { [Comparison Output UI_Demand] }
           using scope ([Version].[Version Name].[CWV_MP])
           using arguments {(ExecutionMode, "LightWeight")
                         , (Param_OUT_VERSION, "CWV_MP")
                         , (MaxSliceTableCells, 200000000)
                         , (MaxConcurrency, 1 )
                         , (IncludeNullRows, False)
                         , ([Param.o9_sys_log_level], "DEBUG")
                         }
    ;

    2) MediumWeight
    EXEC plugin instance [PY_UI_ComparisonOutput_REG]
        for measures { [Comparison Output UI_Demand] }
           using scope ([Version].[Version Name].[CWV_MP])
           using arguments {(ExecutionMode, "MediumWeight")
                         , (Param_OUT_VERSION, "CWV_MP")
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
str_instance = "PY_UI_ComparisonOutput_REG"
str_input_dir = "Input/UIComparisonOutputREG"
str_output_dir = "Output/UIComparisonOutputREG"
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
def fn_delete_fluctuation_from_demand(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1-1. in_Demand에서 W Demand Short Code 값이 "FLUCTUATION" 일경우 행 삭제,
              W Total Met On Time Quantity값을 fillna(0)
    :param df_p_source: in_Demand
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
        return df_return

    # W Demand Short Code 값이 "FLUCTUATION"이 아닌 조건으로 필터링하여 DF 복사
    list_where_fluctuation = df_p_source['W Demand Short Code'] == 'FLUCTUATION'
    df_return = df_p_source[~list_where_fluctuation].copy()
    df_return['W Total Met On Time Quantity'] = df_return['W Total Met On Time Quantity'].fillna(0)

    return df_return


@_decoration_
def fn_divide_io(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1-2. [Item].[Item]이 'IO-'로 시작하는 경우, 해당 행을 2개의 행으로 분리,
        - 기존 IO-로 시작하는 Item이 있는 행의 Item 값을 Item.ItemSetIn/Item.ItemSetOut으로 분리하여 2개의 행 생성
        - 기존 IO-로 시작하는 Item이 있는 행은 삭제
    Step 3-4. (2) 그 이후 [Item].[Item]이 "IO-"로 시작하는 경우, 해당 행을 2개의 행으로 분리,
        - 기존 Item.Item의 값 대신 Item.ItemSetIn/Item.ItemSetOut으로 쪼개줌
        - 기존 데이터는 삭제
    :param df_p_source: in_Demand
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
        return df_return

    # demand 테이블을 아이템이 "IO-"로 시작하는 테이블과 아닌 테이블로 분리
    list_where_io = df_p_source['Item.[Item]'].str.startswith('IO-')
    df_not_io = df_p_source[~list_where_io].copy(deep=True)
    df_io_setin = df_p_source[list_where_io].copy(deep=True)
    df_io_setout = df_p_source[list_where_io].copy(deep=True)


    # Set In 생성
    df_io_setin['Item.[Item]'] = df_io_setin['Item.[ItemSetIn]']
    # Set Out 생성
    df_io_setout['Item.[Item]'] = df_io_setout['Item.[ItemSetOut]']

    df_return = pd.concat([df_not_io, df_io_setin, df_io_setout], axis=0)

    return df_return


@_decoration_
def fn_make_out_sales(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 2. Step 1의 df로 부터, Item.[Item], Location.[Location], Sales Domain.[Customer Group],
            Time.[Week]으로 Group By하여 아래처럼 계산하여 out_Sales 정리
        Comparison Output UI_Demand = Sum(W Demand Quantity)
        Comparison Output UI_GI = Sum(W Total Met On Time Quantity)
        Comparison Output UI_Sales = Sum(W Total Met On Time Quantity)
        Comparison Output UI_RTF = Sum(W Total Met On Time Quantity)
        Comparison Output UI_Short = Sum(W Demand Quantity-W Total Met On Time Quantity])
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
        return df_return

    # 데이터 조정 전 원본 DF 복사
    df_return = df_p_source.copy(deep=True)
    # group by 전에 계산 컬럼 생성
    df_return['Short'] = df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity']
    # group by 후 합계 처리
    df_return = df_return.groupby(by=['Item.[Item]', 'Location.[Location]', 'Sales Domain.[Customer Group]',
                                      'Time.[Week]']).agg({
            'Version.[Version Name]': 'first',
            'W Demand Quantity': 'sum',
            'W Total Met On Time Quantity': 'sum',
            'Short': 'sum'
        }
    ).reset_index()

    df_return = df_return.rename(columns={
        'W Demand Quantity': 'Comparison Output UI_Demand',
        'W Total Met On Time Quantity': 'Comparison Output UI_GI',
        'Short': 'Comparison Output UI_Short'
    })
    df_return['Comparison Output UI_Sales'] = df_return['Comparison Output UI_GI']
    df_return['Comparison Output UI_RTF'] = df_return['Comparison Output UI_GI']

    list_cols = [
        'Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Sales Domain.[Customer Group]', 'Time.[Week]',
        'Comparison Output UI_Demand', 'Comparison Output UI_GI', 'Comparison Output UI_RTF',
        'Comparison Output UI_Short', 'Comparison Output UI_Sales'
    ]
    df_return = df_return[list_cols]

    return df_return


@_decoration_
def fn_rename_psi(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3-1. in_PSI의 column명을 다음과 같이 변경
        Measure.[Comparison PSI UI_BOH] = Measure.[W Beginning On Hand];
        Measure.[Comparison PSI UI_EOH] = Measure.[W Ending On Hand];
    :param df_p_source: in_PSI
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
        return df_return

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # rename
    df_return = df_return.rename(columns={
        'W Beginning On Hand': 'Comparison PSI UI_BOH',
        'W Ending On Hand': 'Comparison PSI UI_EOH'
    })

    return df_return


@_decoration_
def fn_make_psi_shipment(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3-2. in_Shipment의 [Activity1].[To Location]을 Location.[Location]으로 컬럼명 변경하여
              Item Location Week에 대하여 Comparison PSI UI_Shipment = Material Consumption Quantity Plan Output
    :param df_p_source: in_Shipment의
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
        return df_return

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # rename
    df_return = df_return.rename(columns={
        'Activity1.[To Location]': 'Location.[Location]',
        'W Material Consumption Quantity Plan Output': 'Comparison PSI UI_Shipment'
    })
    df_return.drop('Version.[Version Name]', axis=1, inplace=True)

    return df_return


@_decoration_
def fn_make_psi_arrival(df_p_intr: pd.DataFrame, df_p_intr_fromsite: pd.DataFrame, df_p_arrival: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3-3. in_intr과 in_intr_fromsite를 Documents.[OrderlineID]으로 inner join 후,
              Item, Location, Week으로 Group By Sum(W Material Production Quantity Plan Output) as IntrQty
              위의 df를 in_Arrival의 Item Location Week와 full outer join 하고 IntrQty,
              W Material Production Quantity Plan Output를 fillna(0),
              Comparison PSI UI_Arrival = W Material Production Quantity Plan Output+IntrQty
    :param df_p_intr:
    :param df_p_intr_fromsite:
    :param df_p_arrival:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_intr.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_intr)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_intr_fromsite.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_intr_fromsite)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # in_intr과 in_intr_fromsite를 Documents.[OrderlineID]으로 inner join 후,
    df_p_intr_fromsite.drop('Version.[Version Name]', axis=1, inplace=True)
    df_base = df_p_intr.merge(df_p_intr_fromsite, how='inner', on='Documents.[OrderlineID]')
    # Item, Location, Week으로 Group By Sum(W Material Production Quantity Plan Output) as IntrQty
    df_return = df_base.groupby(by=['Item.[Item]', 'Location.[Location]', 'Time.[Week]']).agg(
        {
            'Version.[Version Name]': 'first',
            'W Material Production Quantity Plan Output': 'sum'
        }
    )
    df_return = df_return.rename(columns={'W Material Production Quantity Plan Output': 'IntrQty'})

    # in_Arrival의 Item Location Week와 full outer join 하고
    df_p_arrival.drop('Version.[Version Name]', axis=1, inplace=True)
    df_return = df_return.merge(df_p_arrival, how='outer', on=['Item.[Item]', 'Location.[Location]', 'Time.[Week]'])
    # W Material Production Quantity Plan Output를 fillna(0),
    # Comparison PSI UI_Arrival = W Material Production Quantity Plan Output+IntrQty
    df_return['Comparison PSI UI_Arrival'] = (
            df_return['W Material Production Quantity Plan Output'].fillna(0).astype('Int64') +
            df_return['IntrQty'].fillna(0))
    # print(f'1:{df_return["W Material Production Quantity Plan Output"].fillna(0).astype("Int64").sum()}')
    # print(f'2:{df_return["IntrQty"].fillna(0).sum()}')
    # print(f'3:{df_return["Comparison PSI UI_Arrival"].sum()}')
    list_cols = ['Item.[Item]', 'Location.[Location]', 'Time.[Week]', 'Comparison PSI UI_Arrival']
    df_return = df_return[list_cols]

    return df_return


@_decoration_
def fn_make_out_psi(df_p_source: pd.DataFrame, df_p_shipment: pd.DataFrame, df_p_arrival: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3-4. (1) 3-1을 기준으로, 3-2, 3-3 df를 ITem, Location, Week으로 Left join하여 out_PSI 정리
    :param df_p_source: in_PSI
    :param df_p_shipment: in_Shipment
    :param df_p_arrival: in_Arrival
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
        return df_return

    if df_p_shipment.empty:
        df_p_shipment = (
            pd.DataFrame(columns=['Item.[Item]', 'Location.[Location]', 'Time.[Week]', 'Comparison PSI UI_Shipment']))

    if df_p_arrival.empty:
        df_p_arrival = (
            pd.DataFrame(columns=['Item.[Item]', 'Location.[Location]', 'Time.[Week]', 'Comparison PSI UI_Arrival']))

    df_return = df_p_source.merge(df_p_shipment, how='left', on=['Item.[Item]', 'Location.[Location]', 'Time.[Week]'])
    df_return = df_return.merge(df_p_arrival, how='left', on=['Item.[Item]', 'Location.[Location]', 'Time.[Week]'])

    return df_return


@_decoration_
def fn_obo_material_rcs_process_first(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4-1. OBOMaterialRCA 의 Shortreason이 NO_BOD, BOM_EFFECTIVENESS 이거나,
              Activity2.[Activity Type2]` == "Distribution" 인 경우
              From Time은 최소값,
              002.008W Solver Outputs OBO Material RCA.[W OBO Material Constraint Quantity](short QTY)를
              sum하여 Group by하고,
              From Time(Problem dttm)이 실제 To.[Time].[Week]보다 클 경우, From Time을 To.[Time].[Week]으로 변경
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
        return df_return

    # OBOMaterialRCA의 Shortreason이 NO_BOD, BOM_EFFECTIVENESS이거나, Activity2.[Activity Type2]` == "Distribution"인 경우
    list_where_short_reason = (
        df_p_source['002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]']
        .isin(['NO_BOD', 'BOM_EFFECTIVENESS']))
    list_where_activity_type2 = df_p_source['Activity2.[Activity Type2]'] == 'Distribution'
    list_where = list_where_short_reason | list_where_activity_type2
    df_target = df_p_source[list_where].copy(deep=True)
    # 처리 대상 외  DF
    df_not_target = df_p_source.loc[~list_where].copy(deep=True)

    df_target = df_target.fillna(0)
    # From Time은 최소값, 002.008W Solver Outputs OBO Material RCA.[W OBO Material Constraint Quantity](short QTY)를
    # sum하여 Group by하고,
    df_target = df_target.groupby(by=[
        'Version.[Version Name]', 'from.[RootCause].[Problem Type]', 'from.[Location].[Location]', 'from.[Item].[Item]',
        'from.[Activity1].[Activity1]', 'Activity2.[Activity Type2]', 'from.[Activity2].[Activity2]',
        'from.[Activity3].[Activity3]', 'to.[Demand].[DemandID]', 'to.[Time].[Week]', 'to.[Location].[Location]',
        'to.[Item].[Item]', '002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]',
        '002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]',
        '002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset]'
    ]).agg({
        'from.[Time].[Week]': 'min',
        '002.008W Solver Outputs OBO Material RCA.[W OBO Material Constraint Quantity]': 'sum'
    }).reset_index()

    # From Time(Problem dttm)이 실제 To.[Time].[Week]보다 클 경우, From Time을 To.[Time].[Week]으로 변경
    df_target['from.[Time].[Week]'] = (
        df_target.apply(lambda x: x['to.[Time].[Week]']
        if x['from.[Time].[Week]'] > x['to.[Time].[Week]']
        else x['from.[Time].[Week]'], axis=1))

    # 처리 대상 외 DF와 합치기
    df_return = pd.concat([df_not_target, df_target], axis=0, ignore_index=True)

    return df_return


@_decoration_
def fn_obo_material_rcs_process_second(df_p_source: pd.DataFrame, df_p_weekday: pd.DataFrame,
                                       int_p_current_week: int) -> pd.DataFrame:
    """
    Step 4-2. Step 4-1 df에서 Activity2.[Activity Type2]` == "Distribution"인 경우,
              (From.[Time].[Week]-002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]
              -002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset]) < CurrentWeek 이라면,
              002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]를 'PBC'로 값 변경, 아니면 그대로 둠
    :param df_p_source: in_OBOMaterialRCA
    :param df_p_weekday: in_WeekDay
    :param int_p_current_week: in_CurrentWeek['Time.[Week]'][0]
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
        return df_return

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # week 테이블에서 week를 dictionary로 구성
    dict_week = {row['Time.[Week]']: row.name for _, row in df_p_weekday.iterrows()}
    # week와 'from.[Time].[Week]'의 맵핑 리스트 구성
    list_week_row = df_return['from.[Time].[Week]'].map(dict_week)
    # (From.[Time].[Week]-002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]
    # - 002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset])를 계산하여 리스트로 구성한다.
    list_adjusted_week = (
            list_week_row -
            df_return['002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]'].fillna(0).astype(int) -
            df_return['002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset]'].fillna(0).astype(int)
    )
    # 계산 리스트의 범위가 정상적인지를 체크하는 리스트를 구성한다.
    list_validation = (list_adjusted_week >= 0) & (list_adjusted_week < len(df_p_weekday))
    # 정상 범위라면 week 테이블의 week를 사용하고, 그렇지 않은 경우는 'from.[Time].[Week]'을 사용하는 변경 주차 리스트를 구성한다.
    list_check_week = (
        np.where(list_validation, df_p_weekday.iloc[list_adjusted_week]['Time.[Week]'].values,
                 df_return['from.[Time].[Week]']))
    # Activity2.[Activity Type2]` == "Distribution" 조건
    list_where_distribution = df_return['Activity2.[Activity Type2]'] == 'Distribution'
    # Activity2.[Activity Type2]` == "Distribution" 조건에 부합하면 변경 주차 리스트를 그렇지 않은 경우라면 원본 주차를 저장한다.
    df_return['Chk Week'] = (
        np.where(list_where_distribution, list_check_week, df_return['from.[Time].[Week]']))
    # (From.[Time].[Week]-002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]
    # -002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset]) < CurrentWeek 조건
    list_where_week = df_return['from.[Time].[Week]'].astype(int) < int_p_current_week
    # 2개 조건에 부합하면 002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]에 'PBC' 할당하고
    # 아니면 원본 유지
    df_return['002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]'] = (
        np.where(list_where_distribution & list_where_week,
                 'PBC',
                 df_return['002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]'])
    )

    return df_return


@_decoration_
def fn_make_short_reason(df_p_material_rca: pd.DataFrame, df_p_capacity_rca: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4-3. OBOCapacityRCA와 Step4-2의 df를 아래와 같이 column명 변경후, "to.[Demand].[DemandID]"와 Orgproblem Type만 남김
        "002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]": "Orgproblem Type",
        "002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]": "Orgproblem Type",
    :param df_p_material_rca: in_OBOMaterialRCA
    :param df_p_capacity_rca: in_OBOCapacityRCA
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 로그 출력 및 빈 데이터프레임 생성
    if df_p_material_rca.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_material_rca)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        df_p_material_rca = pd.DataFrame({
            'to.[Demand].[DemandID]': [], '002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]': []
        })

    # 입력 파라미터가 비어 있는 경우 로그 출력 및 빈 데이터프레임 생성
    if df_p_capacity_rca.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_capacity_rca)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        df_p_capacity_rca = pd.DataFrame({
            'to.[Demand].[DemandID]': [], '002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]': []
        })

    # "to.[Demand].[DemandID]"와 Orgproblem Type만 남김
    df_material = (
        df_p_material_rca[['to.[Demand].[DemandID]',
                           '002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]']]).copy(deep=True)
    # "to.[Demand].[DemandID]"와 Orgproblem Type만 남김
    df_capacity = (
        df_p_capacity_rca[['to.[Demand].[DemandID]',
                           '002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]']]).copy(deep=True)
    # rename "002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]": "Orgproblem Type"
    df_material = df_material.rename(columns={
        '002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]': 'Orgproblem Type'
    })
    # rename "002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]": "Orgproblem Type",
    df_capacity = df_capacity.rename(columns={
        '002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]': 'Orgproblem Type'
    })

    # outer로 merge
    df_return = pd.merge(df_material, df_capacity, how='outer')

    return df_return


@_decoration_
def fn_arrange_short_reason(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4-4. "to.[Demand].[DemandID]" 별로 Orgproblem Type를 아래와 같이 정렬후, 맨 위의 값만 남기고 삭제
            list_sort_order = [
                'NO_BOM',
                'NO_BOD',
                'BOD_EFFECTIVENESS',
                'BOM_EFFECTIVENESS',
                'FROZEN',
                'PBC',
                'EOL',
                'MATERIAL',
                'TOOL',
                'LINE'
            ]
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
        return df_return

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    list_sort_order = [
        'NO_BOM',
        'NO_BOD',
        'BOD_EFFECTIVENESS',
        'BOM_EFFECTIVENESS',
        'FROZEN',
        'PBC',
        'EOL',
        'MATERIAL',
        'TOOL',
        'LINE',
        'FLUCTUATION',
        'INV_RISK_AP2',
        'CONSENSUS_ERROR',
        'NO_REASON',
        'CH_CONSTRAINT',
        'SELLER_PREALLOC'
    ]
    df_return['Orgproblem Type'] = (
        pd.Categorical(df_return['Orgproblem Type'], categories=list_sort_order, ordered=True))
    df_return.sort_values(by=['Orgproblem Type'], inplace=True)
    df_return.drop_duplicates(subset=['to.[Demand].[DemandID]'], keep='first', inplace=True)

    return df_return


@_decoration_
def fn_add_short_reason_to_demand(df_p_source: pd.DataFrame, df_p_short_reason: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4-5. Step 1.의 df의 demandID 별로 step4-4를 Left Join,
              (W Demand Quantity-W Total Met On Time Quantity) > 0인 데이터 중
              orgproblem type이 없으면 Measure.[W Demand Short Code] 값을 넣어줌
    :param df_p_source:
    :param df_p_short_reason:
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
        return df_return

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # (W Demand Quantity-W Total Met On Time Quantity) 계산 컬럼 추가
    df_return['Chk Qty'] = (
            df_return['W Demand Quantity'].fillna(0) - df_return['W Total Met On Time Quantity'].fillna(0))
    # Step1.의 df에 demandID 별로 step4-4를 Left Join,
    df_return = (
        df_return.merge(df_p_short_reason, how='left', left_on='Demand.[DemandID]', right_on='to.[Demand].[DemandID]'))
    # (W Demand Quantity-W Total Met On Time Quantity) > 0인 데이터 중
    # orgproblem type이 없으면 Measure.[W Demand Short Code] 값을 넣어줌
    list_where_more_than_zero = df_return['Chk Qty'] > 0
    list_where_problem_type_null = df_return['Orgproblem Type'].isnull()
    list_where = list_where_more_than_zero & list_where_problem_type_null
    df_return.loc[list_where, 'Orgproblem Type'] = df_return['W Demand Short Code']

    return df_return


@_decoration_
def fn_make_out_rca(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4-6. 4-5 df에서 각 orgproblem type이  컬럼명으로, W Demand Quantity-W Total Met On Time Quantity값을 넣어주어
              out_RCA 정리
        EOL, TOOL, LINE일 경우 Capacity TTL에도 W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        NO_BOD, BOD_EFFECTIVENESS, NO_BOM, BOM_EFFECTIVENESS, FROZEN, PBC, MATERIAL일 경우,
        Material TTL에도 W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        CH_CONSTRAINT, INV_RISK_AP2일 경우, W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        아래 3개 컬럼은 전체 행에 대하여 계산
        W Demand Quantity==> Comparison RCA UI_Demand
        W Total Met On Time Quantity==> Comparison RCA UI_RTF
        W Demand Quantity-W Total Met On Time Quantity==> Comparison RCA UI_Short
    :param df_p_source: in_Demand + Short Reason
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
        return df_return

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    #각 orgproblem type을 컬럼명으로, W Demand Quantity-W Total Met On Time Quantity값을 넣어주어 out_RCA 정리
    df_return = df_return.assign(**{
        'NO_BOM': np.where(df_return['Orgproblem Type'] == 'NO_BOM',
                           df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'NO_BOD': np.where(df_return['Orgproblem Type'] == 'NO_BOD',
                           df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'BOD_EFFECTIVENESS': np.where(df_return['Orgproblem Type'] == 'BOD_EFFECTIVENESS',
                           df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'BOM_EFFECTIVENESS': np.where(df_return['Orgproblem Type'] == 'BOM_EFFECTIVENESS',
                           df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'FROZEN': np.where(df_return['Orgproblem Type'] == 'FROZEN',
                           df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'PBC': np.where(df_return['Orgproblem Type'] == 'PBC',
                           df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'EOL': np.where(df_return['Orgproblem Type'] == 'EOL',
                        df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'MATERIAL': np.where(df_return['Orgproblem Type'] == 'MATERIAL',
                           df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'TOOL': np.where(df_return['Orgproblem Type'] == 'TOOL',
                         df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'LINE': np.where(df_return['Orgproblem Type'] == 'LINE',
                         df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'Capacity TTL': np.where(df_return['Orgproblem Type'].isin(['EOL', 'TOOL', 'LINE']),
                                 df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'Material TTL': np.where(df_return['Orgproblem Type'].isin(['NO_BOD', 'BOD_EFFECTIVENESS', 'NO_BOM',
                                                                    'BOM_EFFECTIVENESS', 'FROZEN', 'PBC', 'MATERIAL']),
                                 df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'Comparison RCA UI_Demand': df_return['W Demand Quantity'],
        'Comparison RCA UI_RTF': df_return['W Total Met On Time Quantity'],
        'Comparison RCA UI_Short': df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'],
        'CH_CONSTRAINT': np.where(df_return['Orgproblem Type'] == 'CH_CONSTRAINT',
                                  df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'FLUCTUATION': None,
        'HOLIDAY': None,
        'INV_RISK_AP2': np.where(df_return['Orgproblem Type'] == 'INV_RISK_AP2',
                                 df_return['W Demand Quantity'] - df_return['W Total Met On Time Quantity'], None),
        'NPI': None,
        'Others': None
    })

    list_cols = ['Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Sales Domain.[Customer Group]',
                 'Demand Type.[Demand Type]', 'Time.[Week]', 'Demand.[DemandID]', 'BOD_EFFECTIVENESS',
                 'BOM_EFFECTIVENESS', 'CH_CONSTRAINT', 'Capacity TTL', 'EOL', 'FLUCTUATION', 'FROZEN', 'HOLIDAY',
                 'INV_RISK_AP2', 'LINE', 'MATERIAL', 'Material TTL', 'NO_BOD', 'NO_BOM', 'NPI', 'Others', 'PBC',
                 'TOOL', 'Comparison RCA UI_Demand', 'Comparison RCA UI_RTF', 'Comparison RCA UI_Short']
    df_return = df_return[list_cols]

    return df_return


@_decoration_
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    df_return = pd.DataFrame()
    if str_p_cond == '0':
        # out_Sales
        df_return = pd.DataFrame({
            'Version.[Version Name]': [], 'Item.[Item]': [], 'Location.[Location]': [],
            'Sales Domain.[Customer Group]': [], 'Time.[Week]': [], 'Comparison Output UI_Demand': [],
            'Comparison Output UI_GI': [], 'Comparison Output UI_RTF': [], 'Comparison Output UI_Sales': [],
            'Comparison Output UI_Short': []
        })
    elif str_p_cond == '1':
        # out_PSI
        df_return = pd.DataFrame({
            'Version.[Version Name]': [], 'Item.[Item]': [], 'Location.[Location]': [], 'Time.[Week]': [],
            'Comparison PSI UI_Arrival': [], 'Comparison PSI UI_BOH': [], 'Comparison PSI UI_EOH': [],
            'Comparison PSI UI_Shipment': []
        })
    elif str_p_cond == '2':
        # out_RCA
        df_return = pd.DataFrame({
            'Version.[Version Name]': [], 'Item.[Item]': [], 'Location.[Location]': [],
            'Sales Domain.[Customer Group]': [], 'Demand Type.[Demand Type]': [], 'Time.[Week]': [],
            'Demand.[DemandID]': [], 'BOD_EFFECTIVENESS': [], 'BOM_EFFECTIVENESS': [], 'CH_CONSTRAINT': [],
            'Capacity TTL': [], 'EOL': [], 'FLUCTUATION': [], 'FROZEN': [], 'HOLIDAY': [], 'INV_RISK_AP2': [],
            'LINE': [], 'MATERIAL': [], 'Material TTL': [], 'NO_BOD': [], 'NO_BOM': [], 'NPI': [], 'Others': [],
            'PBC': [], 'TOOL': [], 'Comparison RCA UI_Demand': [], 'Comparison RCA UI_RTF':[],
            'Comparison RCA UI_Short': []
        })

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_Sales = pd.DataFrame()
    out_PSI = pd.DataFrame()
    out_RCA = pd.DataFrame()
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

            in_OBOCapacityRCA = pd.read_csv(str_input_dir + "/in_OBOCapacityRCA.csv", encoding="UTF8")
            in_OBOMaterialRCA = pd.read_csv(str_input_dir + "/in_OBOMaterialRCA.csv", encoding="UTF8")
            in_Demand = pd.read_csv(str_input_dir + "/in_Demand.csv", encoding="UTF8")
            in_CurrentWeek = pd.read_csv(str_input_dir + "/in_CurrentWeek.csv", encoding="UTF8")
            in_Shipment = pd.read_csv(str_input_dir + "/in_Shipment.csv", encoding="UTF8")
            in_Arrival = pd.read_csv(str_input_dir + "/in_Arrival.csv", encoding="UTF8")
            in_intr = pd.read_csv(str_input_dir + "/in_intr.csv", encoding="UTF8")
            in_intr_fromsite = pd.read_csv(str_input_dir + "/in_intr_fromsite.csv", encoding="UTF8")
            in_PSI = pd.read_csv(str_input_dir + "/in_PSI.csv", encoding="UTF8")
            in_WeekDay = pd.read_csv(str_input_dir + "/in_WeekDay.csv", encoding="UTF8")

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
        fn_check_input_table(in_OBOCapacityRCA, 'in_OBOCapacityRCA', '1')
        fn_check_input_table(in_OBOMaterialRCA, 'in_OBOMaterialRCA', '1')
        fn_check_input_table(in_Demand, 'in_Demand', '1')
        fn_check_input_table(in_CurrentWeek, 'in_CurrentWeek', '1')
        fn_check_input_table(in_Shipment, 'in_Shipment', '1')
        fn_check_input_table(in_Arrival, 'in_Arrival', '1')
        fn_check_input_table(in_intr, 'in_intr', '1')
        fn_check_input_table(in_intr_fromsite, 'in_intr_fromsite', '1')
        fn_check_input_table(in_PSI, 'in_PSI', '1')

        int_current_week = int(in_CurrentWeek['Time.[Week]'][0])

        print(f'{in_Arrival["W Material Production Quantity Plan Output"].sum()}')
        ################################################################################################################
        # Step 1-1. in_Demand에서 W Demand Short Code 값이 "FLUCTUATION" 일경우 행 삭제,
        #           W Total Met On Time Quantity값을 fillna(0)
        ################################################################################################################
        dict_log = {
            'p_step_no': 1010,
            'p_step_desc': 'Step 1-1. in_Demand에서 W Demand Short Code 값이 "FLUCTUATION" 일경우 행 삭제, '
                           'W Total Met On Time Quantity값을 fillna(0)',
            'p_df_name': 'df_Demand'
        }
        df_Demand = fn_delete_fluctuation_from_demand(in_Demand, **dict_log)

        ################################################################################################################
        # Step 1-2. [Item].[Item]이 'IO-'로 시작하는 경우, 해당 행을 2개의 행으로 분리,
        #   - 기존 IO-로 시작하는 Item이 있는 행의 Item 값을 Item.ItemSetIn/Item.ItemSetOut으로 분리하여 2개의 행 생성
        #   - 기존 IO-로 시작하는 Item이 있는 행은 삭제
        ################################################################################################################
        dict_log = {
            'p_step_no': 1020,
            'p_step_desc': 'Step 1-2. [Item].[Item]이 "IO-"로 시작하는 경우, 해당 행을 2개의 행으로 분리,' + '\n' +
                           '    - 기존 IO-로 시작하는 Item이 있는 행의 Item 값을 Item.ItemSetIn/Item.ItemSetOut으로 분리하여 ' +
                           '2개의 행 생성' + '\n' +
                           '    - 기존 IO-로 시작하는 Item이 있는 행은 삭제',
            'p_df_name': 'df_Demand_divide_io'
        }
        df_Demand_divide_io = fn_divide_io(df_Demand, **dict_log)

        ################################################################################################################
        # Step 2. Step 1의 df로 부터, Item.[Item], Location.[Location], Sales Domain.[Customer Group],
        #         Time.[Week]으로 Group By하여 아래처럼 계산하여 out_Sales 정리
        #     Comparison Output UI_Demand = Sum(W Demand Quantity)
        #     Comparison Output UI_GI = Sum(W Total Met On Time Quantity)
        #     Comparison Output UI_Sales =  Sum(W Total Met On Time Quantity)
        #     Comparison Output UI_RTF = Sum(W Total Met On Time Quantity)
        #     Comparison Output UI_Short = Sum(W Demand Quantity-W Total Met On Time Quantity])
        ################################################################################################################
        dict_log = {
            'p_step_no': 2000,
            'p_step_desc': 'Step 2. Step 1의 df로 부터, Item.[Item], Location.[Location], Sales Domain.[Customer Group], ' +
                           'Time.[Week]으로 Group By하여 아래처럼 계산하여 out_Sales 정리' + '\n' +
                           '    Comparison Output UI_Demand = Sum(W Demand Quantity)' + '\n' +
                           '    Comparison Output UI_GI = Sum(W Total Met On Time Quantity)' + '\n' +
                           '    Comparison Output UI_Sales =  Sum(W Total Met On Time Quantity)' + '\n' +
                           '    Comparison Output UI_RTF = Sum(W Total Met On Time Quantity)' + '\n' +
                           '    Comparison Output UI_Short = Sum(W Demand Quantity-W Total Met On Time Quantity])',
            'p_df_name': 'df_out_sales'
        }
        df_out_sales = fn_make_out_sales(df_Demand_divide_io, **dict_log)

        ################################################################################################################
        # Step 3-1. in_PSI의 column명을 다음과 같이 변경
        #     Measure.[Comparison PSI UI_BOH] = Measure.[W Beginning On Hand];
        #     Measure.[Comparison PSI UI_EOH] = Measure.[W Ending On Hand];
        ################################################################################################################
        dict_log = {
            'p_step_no': 3010,
            'p_step_desc': 'Step 3-1. in_PSI의 column명을 다음과 같이 변경' + '\n' +
                           '    Measure.[Comparison PSI UI_BOH] = Measure.[W Beginning On Hand];' + '\n' +
                           '    Measure.[Comparison PSI UI_EOH] = Measure.[W Ending On Hand];',
            'p_df_name': 'df_PSI_base'
        }
        df_PSI_base = fn_rename_psi(in_PSI, **dict_log)

        ################################################################################################################
        # Step 3-2. in_Shipment의 [Activity1].[To Location]을 Location.[Location]으로 컬럼명 변경하여
        #           Item Location Week에 대하여 Comparison PSI UI_Shipment = Material Consumption Quantity Plan Output
        ################################################################################################################
        dict_log = {
            'p_step_no': 3020,
            'p_step_desc': 'Step 3-2. in_Shipment의 [Activity1].[To Location]을 Location.[Location]으로 컬럼명 변경하여 '
                           'Item Location Week에 대하여 '
                           'Comparison PSI UI_Shipment = Material Consumption Quantity Plan Output',
            'p_df_name': 'df_PSI_Shipment'
        }
        df_PSI_Shipment = fn_make_psi_shipment(in_Shipment, **dict_log)

        ################################################################################################################
        # Step 3-3. in_intr과 in_intr_fromsite를 Documents.[OrderlineID]으로 inner join 후,
        #           Item, Location, Week으로 Group By Sum(W Material Production Quantity Plan Output) as IntrQty
        #           위의 df를 in_Arrival의 Item Location Week와 full outer join 하고 IntrQty,
        #           W Material Production Quantity Plan Output를 fillna(0),
        #           Comparison PSI UI_Arrival = W Material Production Quantity Plan Output+IntrQty
        ################################################################################################################
        dict_log = {
            'p_step_no': 3031,
            'p_step_desc': 'Step 3-3. in_intr과 in_intr_fromsite를 Documents.[OrderlineID]으로 inner join 후, '
                           'Item, Location, Week으로 Group By Sum(W Material Production Quantity Plan Output) as IntrQty '
                           '위의 df를 in_Arrival의 Item Location Week와 full outer join 하고 IntrQty,'
                           'W Material Production Quantity Plan Output를 fillna(0),'
                           'Comparison PSI UI_Arrival = W Material Production Quantity Plan Output+IntrQty',
            'p_df_name': 'df_PSI_Arrival'
        }
        df_PSI_Arrival = fn_make_psi_arrival(in_intr, in_intr_fromsite, in_Arrival, **dict_log)

        ################################################################################################################
        # Step 3-4. 3-1을 기준으로, 3-2, 3-3 df를 ITem, Location, Week으로 Left join하여 out_PSI 정리
        #              그 이후 [Item].[Item]이 'IO-'로 시작하는 경우, 해당 행을 2개의 행으로 분리,
        #         -  기존 Item.Item의 값 대신 Item.ItemSetIn/Item.ItemSetOut으로 쪼개줌
        #         - 기존 데이터는 삭제
        ################################################################################################################
        dict_log = {
            'p_step_no': 3041,
            'p_step_desc': 'Step 3-4. (1) 3-1을 기준으로, 3-2, 3-3 df를 ITem, Location, Week으로 Left join하여 out_PSI 정리',
            'p_df_name': 'df_out_PSI'
        }
        df_out_PSI = fn_make_out_psi(df_PSI_base, df_PSI_Shipment, df_PSI_Arrival, **dict_log)

        dict_log = {
            'p_step_no': 3042,
            'p_step_desc': 'Step 3-4. (2) 그 이후 [Item].[Item]이 "IO-"로 시작하는 경우, 해당 행을 2개의 행으로 분리,' + '\n' +
                           '    - 기존 Item.Item의 값 대신 Item.ItemSetIn/Item.ItemSetOut으로 쪼개줌' + '\n' +
                           '    - 기존 데이터는 삭제',
            'p_df_name': 'df_out_PSI_divide_io'
        }
        df_out_PSI_divide_io = fn_divide_io(df_out_PSI, **dict_log)

        ################################################################################################################
        # Step 4-1. OBOMaterialRCA 의 Shortreason이 NO_BOD, BOM_EFFECTIVENESS 이거나,
        #           Activity2.[Activity Type2]` == "Distribution" 인 경우
        #           From Time은 최소값,
        #           002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material](short QTY)를 sum하여 Group by하고,
        #           From Time(Problem dttm)이 실제 To.[Time].[Week]보다 클 경우, From Time을 To.[Time].[Week]으로 변경
        ################################################################################################################
        dict_log = {
            'p_step_no': 4010,
            'p_step_desc': 'Step 4-1. OBOMaterialRCA 의 Shortreason이 NO_BOD, BOM_EFFECTIVENESS 이거나, '
                           'Activity2.[Activity Type2]` == "Distribution" 인 경우 From Time은 최소값, '
                           '002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material](short QTY)를 sum하여 '
                           'Group by하고, From Time(Problem dttm)이 실제 To.[Time].[Week]보다 클 경우, '
                           'From Time을 To.[Time].[Week]으로 변경',
            'p_df_name': 'df_OBOMaterialRCA_first'
        }
        df_OBOMaterialRCA_first = fn_obo_material_rcs_process_first(in_OBOMaterialRCA, **dict_log)

        ################################################################################################################
        # Step 4-2. Step 4-1 df에서 Activity2.[Activity Type2]` == "Distribution"인 경우,
        #           (From.[Time].[Week]-002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]
        #           -002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset]) < CurrentWeek 이라면,
        #           002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]를 'PBC'로 값 변경, 아니면 그대로 둠
        ################################################################################################################
        dict_log = {
            'p_step_no': 4020,
            'p_step_desc': 'Step 4-2. Step 4-1 df에서 Activity2.[Activity Type2]` == "Distribution"인 경우, '
                           '(From.[Time].[Week]-002.008W Solver Outputs OBO Material RCA.[W Activity Lead Time]'
                           '-002.008W Solver Outputs OBO Material RCA.[W Activity Mandatory Offset]) < CurrentWeek 이라면, '
                           '002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]를 "PBC"로 값 변경, '
                           '아니면 그대로 둠',
            'p_df_name': 'df_OBOMaterialRCA_second'
        }
        df_OBOMaterialRCA_second = (
            fn_obo_material_rcs_process_second(df_OBOMaterialRCA_first, in_WeekDay, int_current_week, **dict_log))

        ################################################################################################################
        # Step 4-3. OBOCapacityRCA와 Step4-2의 df를 아래와 같이 column명 변경 후,
        #           "to.[Demand].[DemandID]"와 Orgproblem Type만 남김
        #     "002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]": "Orgproblem Type",
        #     "002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]": "Orgproblem Type",
        ################################################################################################################
        dict_log = {
            'p_step_no': 4030,
            'p_step_desc': 'Step 4-3. OBOCapacityRCA와 Step4-2의 df를 아래와 같이 column명 변경 후, '
                           '"to.[Demand].[DemandID]"와 Orgproblem Type만 남김 '
                           '"002.009W Solver Outputs OBO Capacity RCA.[W MP RCA Type OBO Capacity]": "Orgproblem Type",'
                           '"002.008W Solver Outputs OBO Material RCA.[W MP RCA Type OBO Material]": "Orgproblem Type",',
            'p_df_name': 'df_short_reason'
        }
        df_short_reason = fn_make_short_reason(df_OBOMaterialRCA_second, in_OBOCapacityRCA, **dict_log)

        ################################################################################################################
        # Step 4-4. "to.[Demand].[DemandID]" 별로 Orgproblem Type를 아래와 같이 정렬후, 맨 위의 값만 남기고 삭제
        #             list_sort_order = [
        #                 'NO_BOM',
        #                 'NO_BOD',
        #                 'BOD_EFFECTIVENESS',
        #                 'BOM_EFFECTIVENESS',
        #                 'FROZEN',
        #                 'PBC',
        #                 'EOL',
        #                 'MATERIAL',
        #                 'TOOL',
        #                 'LINE'
        #             ]
        ################################################################################################################
        dict_log = {
            'p_step_no': 4040,
            'p_step_desc': 'Step 4-4. "to.[Demand].[DemandID]" 별로 Orgproblem Type를 아래와 같이 정렬 후, '
                           '맨 위의 값만 남기고 삭제' + '\n' +
                           'list_sort_order = [NO_BOM, NO_BOD, BOD_EFFECTIVENESS, BOM_EFFECTIVENESS, FROZEN, PBC, '
                           'EOL, MATERIAL, TOOL, LINE]',
            'p_df_name': 'df_short_reason_arranged'
        }
        df_short_reason_arranged = fn_arrange_short_reason(df_short_reason, **dict_log)

        ################################################################################################################
        # Step 4-5. Step1.의 df의 demandID 별로 step4-4를 Left Join,
        #           (W Demand Quantity-W Total Met On Time Quantity) > 0인 데이터중
        #           orgproblem type이 없으면 Measure.[W Demand Short Code] 값을 넣어줌
        ################################################################################################################
        dict_log = {
            'p_step_no': 4050,
            'p_step_desc': 'Step 4-5. Step1.의 df의 demandID 별로 step4-4를 Left Join, '
                           'W Demand Quantity-W Total Met On Time Quantity > 0인 데이터 중 '
                           'orgproblem type이 없으면 Measure.[W Demand Short Code] 값을 넣어 줌',
            'p_df_name': 'df_Demand_short_reason'
        }
        df_Demand_short_reason = fn_add_short_reason_to_demand(df_Demand_divide_io, df_short_reason_arranged,
                                                                 **dict_log)

        ################################################################################################################
        # Step 4-6. 4-5 df에서 각 orgproblem type이  컬럼명으로, W Demand Quantity-W Total Met On Time Quantity값을 넣어주어
        #           out_RCA 정리
        #     EOL, TOOL, LINE일 경우 Capacity TTL에도 W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        #     NO_BOD, BOD_EFFECTIVENESS, NO_BOM, BOM_EFFECTIVENESS, FROZEN, PBC, MATERIAL일 경우,
        #     Material TTL에도 W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        #     CH_CONSTRAINT, INV_RISK_AP2일 경우, W Demand Quantity-W Total Met On Time Quantity값을 넣어줌
        #     아래 3개 컬럼은 전체 행에 대하여 계산
        #     W Demand Quantity==> Comparison RCA UI_Demand
        #     W Total Met On Time Quantity==> Comparison RCA UI_RTF
        #     W Demand Quantity-W Total Met On Time Quantity==> Comparison RCA UI_Short
        ################################################################################################################
        dict_log = {
            'p_step_no': 4060,
            'p_step_desc': 'Step 4-6. 4-5 df에서 각 orgproblem type이  컬럼명으로, ' +
                           'W Demand Quantity-W Total Met On Time Quantity값을 넣어주어 out_RCA 정리' + '\n' +
                           'EOL, TOOL, LINE일 경우 Capacity TTL에도 ' +
                           'W Demand Quantity-W Total Met On Time Quantity값을 넣어줌' + '\n' +
                           'NO_BOD, BOD_EFFECTIVENESS, NO_BOM, BOM_EFFECTIVENESS, FROZEN, PBC, MATERIAL 일경우, ' +
                           'Material TTL에도 W Demand Quantity-W Total Met On Time Quantity값을 넣어줌' + '\n' +
                           'CH_CONSTRAINT, INV_RISK_AP2일 경우, W Demand Quantity-W Total Met On Time Quantity값을 넣어줌' +
                           '아래 3개 컬럼은 전체 행에 대하여 계산' + '\n' +
                           'W Demand Quantity==> Comparison RCA UI_Demand' + '\n' +
                           'W Total Met On Time Quantity==> Comparison RCA UI_RTF' + '\n' +
                           'W Demand Quantity-W Total Met On Time Quantity==> Comparison RCA UI_Short',
            'p_df_name': 'df_out_RCA'
        }
        df_out_RCA = fn_make_out_rca(df_Demand_short_reason, **dict_log)

        ################################################################################################################
        # 최종 Output 정리
        ################################################################################################################
        df_out_sales['Version.[Version Name'] = Param_OUT_VERSION
        df_out_PSI_divide_io['Version.[Version Name'] = Param_OUT_VERSION
        df_out_RCA['Version.[Version Name'] = Param_OUT_VERSION

        out_Sales = df_out_sales[
            ['Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Sales Domain.[Customer Group]',
             'Time.[Week]', 'Comparison Output UI_Demand', 'Comparison Output UI_GI', 'Comparison Output UI_RTF',
             'Comparison Output UI_Sales', 'Comparison Output UI_Short']]

        out_PSI = df_out_PSI_divide_io[
            ['Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Time.[Week]', 'Comparison PSI UI_Arrival',
             'Comparison PSI UI_BOH', 'Comparison PSI UI_EOH', 'Comparison PSI UI_Shipment']]

        out_RCA = df_out_RCA[
            ['Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Sales Domain.[Customer Group]',
             'Demand Type.[Demand Type]', 'Time.[Week]', 'Demand.[DemandID]', 'BOD_EFFECTIVENESS',
             'BOM_EFFECTIVENESS', 'CH_CONSTRAINT', 'Capacity TTL', 'EOL', 'FLUCTUATION', 'FROZEN', 'HOLIDAY',
             'INV_RISK_AP2', 'LINE', 'MATERIAL', 'Material TTL', 'NO_BOD', 'NO_BOM', 'NPI', 'Others', 'PBC', 'TOOL',
             'Comparison RCA UI_Demand', 'Comparison RCA UI_RTF', 'Comparison RCA UI_Short'
             ]]

        fn_log_dataframe(out_Sales, 'out_Sales')
        fn_log_dataframe(out_PSI, 'out_PSI')
        fn_log_dataframe(out_RCA, 'out_RCA')

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_Sales = None
            out_PSI = None
            out_RCA = None
            raise Exception(e)
        else:
            if out_Sales.empty:
                out_Sales = fn_set_header('0')
                fn_log_dataframe(out_Sales, 'out_Sales')
            if out_PSI.empty:
                out_PSI = fn_set_header('1')
                fn_log_dataframe(out_PSI, 'out_PSI')
            if out_RCA.empty:
                out_RCA = fn_set_header('2')
                fn_log_dataframe(out_RCA, 'out_RCA')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_Sales.empty:
            out_Sales = fn_set_header('0')
            fn_log_dataframe(out_Sales, 'out_Sales')
        if out_PSI.empty:
            out_PSI = fn_set_header('1')
            fn_log_dataframe(out_PSI, 'out_PSI')
        if out_RCA.empty:
            out_RCA = fn_set_header('2')
            fn_log_dataframe(out_RCA, 'out_RCA')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')
