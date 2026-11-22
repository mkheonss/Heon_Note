"""
* 프로그램명
    - PY_UI_POProcessSplit_REG.py

* 내용
    -
* 변경이력
    - 2025.11.04 / Miss Lee / Create

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를
                             결정하는 파라미터
    - Param_Step : 엔진 수행 타입 ( P, M )

* Input Tables
    - in_POProcess :
      1) [Sub MF Site Std1].[MF],  [Shipment Type] in {"DIR_D", "INDIR"} -> simulation split 대상
      2)CWV_MP기준(Time.[Week] 기준으로 한 주차만 있어야 함)
     Select (
              [Version].[Version Name].CWV_MP
            * [Sub Location].[Sub MF Site Std1].[MF].relatedmembers([Sub Location])
            * [Item].[Item]
            * [Location].[Location].filter(#.[Shipment Type] in {"DIR_D", "INDIR"})
            * [Time].[Week]
            * [SOP Week].[SOP Week]
            * [Delivery Week].[Delivery Week]
            * [MFG Week].[MFG Week]
            ) on row,
            ({
              Measure.[PO Process_POP Qty(M)]
            , Measure.[PO Process_POP Qty(P)]
            , Measure.[PO Process_Short Qty(M)]
            , Measure.[PO Process_Short Qty(P)]
            , Measure.[PO Process_DMD ETA 4Week Sum Qty]
            , Measure.[PO Process_Last Step]            // Po건의 마지막 상태여부
            }) on column
    include memberproperties{[Location].[Location], [Shipment Type]};

    - in_LoadingDirOrderMgmt: LoadingDirOrderMgmt 직선적 데이터 ( CWV_MP 기준 전주차 Sync 데이터 )
    Select (
              [Version].[Version Name].filter(
              #.[Plan Type]=="MP Sync Plan" && #.[Plan Week] == &CurrentWeek.element(0).LeadOffset(-1).Name
              )
            * [Sub Location].[Sub Location]
            * [Seq].[Seq]
            * [Item].[Item]
            * [Location].[Location].filter(#.[Shipment Type] == "DIR_D")
            * [Sales Domain].[Ship To]
            * [Time].[Week]
            ) on row,
          ({
              Measure.[Loading Dir Order Mgmt_Adj Prod Week]
            , Measure.[Loading Dir Order Mgmt_Chk Qty]
            , Measure.[Loading Dir Order Mgmt_Loading Qty]
            , Measure.[Loading Dir Order Mgmt_Ship To]
            , Measure.[Loading Dir Order Mgmt_Created By]
            }) on column;

    - in_POProcessDetail : P Step의 최종 POProcessDetail
    Select (
              [Version].[Version Name].CWV_MP
            * [Sub Location].[Sub Location]
            * [Seq].[Seq]
            * [Item].[Item]
            * [Location].[Location]
            * [Time].[Week]
            * [MFG Week].[MFG Week]
            ) on row,
            ({
               Measure.[PO Process Detail_Account]
             , Measure.[PO Process Detail_Ship To]
             , Measure.[PO Process Detail_SOP ETD Week]
             , Measure.[PO Process Detail_Order Mgmt Qty(P)]
             , Measure.[PO Process Detail_POP Qty(P)]
             , Measure.[PO Process Detail_Check Qty(P)]
             , Measure.[PO Process Detail_Short Qty(P)]
             , Measure.[PO Process Detail_Created by]
             , Measure.[PO Process Detail_Creation time]
             , Measure.[PO Process Detail_Block]
             , Measure.[PO Process Detail_Last Step]
             , Measure.[PO Process Detail_DMD ETA 4Week Sum Qty]
             }) on column
    where { Measure.[PO Process Detail_Chk Last Step(P)] == "Y"}; //P step 'Y'

    - in_BodLaneItem :
    Select (
              [Version].[Version Name].CWV_MP
            * [BOD].[BOD Name]
            * [Item].[Item]
            ) on row,
            ({
              Measure.[BOD Lane Item_Priority]
            , Measure.[BOD Lane Item_Shipping Leadtime]
            }) on column;

    - in_Time : 주차 테이블
    select (Time.[Week]) on row;

* Output Tables
    - out_POProcessDetail:
        Select (
                  [Version].[Version Name]
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Seq].[Seq]
                * [Item].[Item]
                * [Time].[Week]
                * [MFG Week].[MFG Week]
                ) on row,
                ({
                  Measure.[PO Process Detail_Created by]
                , Measure.[PO Process Detail_Creation time]
                , Measure.[PO Process Detail_Updated by]
                , Measure.[PO Process Detail_Update time]
                , Measure.[PO Process Detail_POP Qty(M)]
                , Measure.[PO Process Detail_POP Qty(P)]
                , Measure.[PO Process Detail_Order Mgmt Qty(M)]
                , Measure.[PO Process Detail_Order Mgmt Qty(P)]
                , Measure.[PO Process Detail_SOP ETD Week]
        }) on column;

        - out_POProcess:
        Select (
                  [Version].[Version Name]
                * [Sub Location].[Sub Location]
                * [Location].[Location]
                * [Seq].[Seq]
                * [Item].[Item]
                * [Time].[Week]
                * [MFG Week].[MFG Week]
                * [Delivery Week].[Delivery Week]
                ) on row,
                ({
                  Measure.[PO Process Detail_Created by]
                , Measure.[PO Process Detail_Creation time]
                , Measure.[PO Process_POP Qty(P)]
                , Measure.[PO Process_POP Qty(M)]
                , Measure.[PO Process_Data Source]
        }) on column;

* Flow Summary
<==========================================================================================================
    ※ Po Process Detail 추출 대상 기준.
        예시) A_ : A경로라고 하자. (경로: Prod Week + From + To ,  Item : 1,2,3.. )
          DIR             | PO
          ------------------------------------------------
          직선적(A_1)     | 창고향
          직선적(A_3)     | 직선적(A_1)
          직선적(C)       | 직선적(A_2)
                          | 직선적(B)
          ------------------------------------------------
        > Po Process Detail 대상 : 창고향, 직선적(A_1), 직선적(A_2), 직선적(B), 직선적(A_3) 해당됨
          (Po Process데이터 전부와, Po Process의 직선적의 경로에 해당되는 Dir 데이터의 합집합 )
==========================================================================================================>
    STEP 0. 전처리
        STEP 0-1) in_POProcess, in_LoadingDirOrderMgmt prefix 제거
                  → df_poProcess, df_loadingDirOrderMgmt
        STEP 0-2) df_poProcess 테이블을 Prod Week + From + To + Item 기준으로 Aggregation.
                  (POP_PO : sum, 나머지 칼럼 : first) → df_aggregated_poProcess
                  df_loadingDirOrderMgmt 테이블을 Prod Week + From + To + Account + ShipTo + Item 기준으로
                  Aggregation. (Loading Qty:sum, 나머지 칼럼 : first) → df_aggregated_loadingDirOrderMgmt

    STEP 1. df_aggregated_poProcess의 Prod Week + From + To 기준 으로 df_aggregated_loadingDirOrderMgmt
            존재하는 데이터를 Po Process Detail 직선적 PO의 동일경로 DIR 대상으로 추출하여 df1 생성 한다.
            ( df1 : 직선적(A_1), 직선적(A_3) 이 대상 )
            df_aggregated_loadingDirOrderMgmt의 Simul Qty(or Confirm Qty(추후에 dir mgmt에서 생성))를
            copy하여 Order Mgmt Qty 칼럼 생성 한다.

    STEP 2. df1 과 PO 테이블(df_aggregated_poProcess)을 outer join 하여 Po Process Detail의 전체 대상인
            df3를 생성 한다.( 창고향, 직선적 데이터 모두 Po Process Detail에 담기 )
            Prod Week + From + To + Item 기준으로 [Order Mgmt Qty].transform(sum) 하여
            MgmtQty_TOT 로 칼럼 생성 한다.
            Split 로직을 반영 한다.

            ※ Split 로직. ( df3 POP 할당 방법 )
            1) left_only  : POP = 0 ( ▶ dir에만 존재할 경우 0 )
            2) right_only : POP = POP_PO  ( ▶ po에만 존재할 경우 POP_PO )
            3) both ( ▶ POP_PO 양만큼 분배 )
              i)  MgmtQty_TOT == POP_PO → POP = Order Mgmt Qty.
              ii) POP_PO > MgmtQty_TOT  → POP = Order Mgmt Qty 해주고,
                  (POP_PO - MgmtQty_TOT = GAP_POP => POP) 만큼
                  Prod Week + From + To + Account(NULL) + Ship To(NULL) + Item + GAP_POP 한줄 추가.
                  ( ▶ POP_PO > dir 일 경우에는 한줄 추가해서 POP_PO만큼 꽉! 채워 준다.)
              iii) POP_PO < MgmtQty_TOT (Split case)
              → a) Prod Week + From + To + Account + Ship To + Order Mgmt Qty(큰 순) 순으로 SORT.
                b) Order Mgmt Qty를 CumSum하여 CUM_SUM_QTY로 칼럼 생성.
                   POP_PO - CUM_SUM_QTY >= 0 → POP = Order Mgmt Qty
                   POP_PO - CUM_SUM_QTY < 0  → POP = Order Mgmt Qty + (POP_PO - CUM_SUM_QTY) = RESULT
                                                     : RESULT > 0  → RESULT
                                                     : RESULT <= 0 → RESULT = 0
                  ( ▶ POP_PO < dir 일 경우에는 sort해서 POP_PO만큼 딱! 잘라서 나눠준다.)

            ※ Split 로직 (Short Qty 할당 방법 )
            -  Block in ('INDIR', 'DIR_PO') : Detail에 한줄 추가로 Short Qty 반영됨
            - Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 경우
             Prod Week + From + To + Account(Null) + Ship To(Null) 로 한줄 생성하여 Short Qty 반영해준다.

            1) Short Qty 반영 ( Short Qty > 0 )
              Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 건을
              ['Week', 'From', 'To Site', 'Item','Short_PO', 'Block','Org_Time.[Week]','SOP Week.[SOP Week]',
              'Delivery Week.[Delivery Week]'] 별로 Short Qty 발췌 : df_return_both_append
            2) df_return_both 에서 Block == 'DIR_BOTH' 인 건 Short Qty = 0 처리
            3) df_return_both , df_return_both_append concat 후,
               ['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item'] 별로 groupby sum()

    STEP 3. Step 3-1. Step별로 후처리 로직을 반영 한다.
            1) Step 'P' : Created by, Creation time, Chk Last Step(P), Last Step 칼럼 반영.
                          Prod Week + From + To + Item 별로 Seq 채번 생성.
            2) Step 'M' : in_POProcessDetail(P의 최종 POProcessDetail) 과
                          df3(M단계 Detail 데이터)을  Prod Week + From + To + Account + Ship To + Item 별로
                          outer join 함.
                          i) 중복되면 Updated by, Updated time 신규건이면 Created by, Creation time 반영.
                          ii) Seq :  key기준으로 P에 있는 경우는 P의 seq를 사용하고,
                          신규건은 P의 max(seq) +1 을 초기값으로 하여 seq = 초기값 + (key별 seq 채번)
                          iii) SOP ETD Week, Block, Last Step : M 단계 값으로 수정

            Step 3-2. ETD Week 생성한다. (ETD Week 존재하지 않을 경우)
              :  BOD Lane Item 의 shipment L/T 을 Production Week 에 더해서 ETD 산출
              ( ETD Week = Production Week + round(BOD Lane Item_Shipping Leadtime/ 7, 0) )

            Step 3-3. Dir에만 존재하는 경우 상단 추가. (Week + From + To 존재하나 Item이 다른 경우)
             : detail을 상단 key기준으로 grouping 하여 POP = 0(SUM) , Data Source(2 : 'P' , 3: 'M' )
             구분자로 PO Process 메저 한줄 추가

* Validation :

* Execution :
    1. 기존 메저 데이터 초기화
        delete data for model [PO Process Detail] where { &CWV_MP };

    2. Plugin Call하여 신규 MG 생성
    1) LightWeight
        EXEC plugin instance [PY_UI_POProcessSplit_REG]
            for measures { [PO Process Detail_POP Qty(M)]
                          ,[PO Process Detail_POP Qty(P)]
                          ,[PO Process Detail_Order Mgmt Qty(M)]
                          ,[PO Process Detail_Order Mgmt Qty(P)]
                          ,[PO Process Detail_SOP ETD Week]
                        }
               using arguments {(ExecutionMode, "LightWeight")
                             , (Param_OUT_VERSION, "CWV_MP")
                             , (Param_Step, "P")
                             , (MaxSliceTableCells, 200000000)
                             , (MaxConcurrency, 1 )
                             , (IncludeNullRows, False)
                             , ([Param.o9_sys_log_level], "DEBUG")
                             };

    2) MediumWeight
        EXEC plugin instance [PY_UI_POProcessSplit_REG]
             for measures { [PO Process Detail_POP Qty(M)]
                           ,[PO Process Detail_POP Qty(P)]
                           ,[PO Process Detail_Order Mgmt Qty(M)]
                           ,[PO Process Detail_Order Mgmt Qty(P)]
                           ,[PO Process Detail_SOP ETD Week]
                        }
               using arguments {(ExecutionMode, "MediumWeight")
                             , (Param_OUT_VERSION, "CWV_MP")
                             , (Param_Step, "P")
                             , (MaxSliceTableCells, 200000000)
                             , (MaxConcurrency, 1 )
                             , (IncludeNullRows, False)
                             , ([Param.o9_sys_log_level], "DEBUG")
                             };

"""
import decimal
import inspect
import os.path
import time
from datetime import datetime

import numpy as np
import pandas as pd
import traceback
import re
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_POProcessSplit_REG"
str_input_dir = "Input/UIPOProcessSplitREG"
str_output_dir = "Output/UIPOProcessSplitREG"
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
            df_p_source.to_csv(str_output_dir + "/" + str_p_source_name + ".csv", encoding="UTF8", index=False)
    else:
        # 최종 Output 테이블인 경우에는 무조건 로그 출력
        if is_output:
            logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
            if is_local and not df_p_source is None and not df_p_source.empty:
                # 로컬 Debugging 시 csv 파일 출력
                df_p_source.to_csv(str_output_dir + "/" + str_p_source_name + ".csv", encoding="UTF8", index=False)


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
def fn_preprocess(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    parameter 에 따라, POP(P), POP(M)으로 넘어 오는 값을 POP Qty(' + Param_Step + ') 변수로 생성한다.
    in_LoadingDirOrderMgmt의 Time.[Week] → Rdd Week 변수로 생성한다.
    :param df_p_source: in_POProcess, in_LoadingDirOrderMgmt
    :param str_p_cond: '0' - in_POProcess, '1' - in_LoadingDirOrderMgmt
    :return: DataFrame
    """
    # DataFrame 복사
    df_return = df_p_source.copy(deep=True)

    # Rename
    df_return.rename(columns={
        'MFG Week.[MFG Week]': 'Week',
        'Sub Location.[Sub Location]': 'From',
        'Location.[Location]': 'To Site',
        'Sales Domain.[Ship To]': 'Account',
        'Item.[Item]': 'Item',
        'Time.[Week]': 'Org_Time.[Week]',
        'Location.[Shipment Type]': 'Shipment Type',
        'Loading Dir Order Mgmt_Adj Prod Week': 'Week',
    }, inplace=True)

    # 칼럼 prefix 없애기
    str_pre_fix_mgmt = 'Loading Dir Order Mgmt_'
    str_pre_fix_po = 'PO Process_'

    # 칼럼 str_pre_fix 를 다 없애고
    list_columns = df_return.columns
    list_columns_new = []
    for col in list_columns:
        new_col = col.replace(str_pre_fix_mgmt, "").replace(str_pre_fix_po, "")
        list_columns_new.append(new_col)
    df_return.columns = list_columns_new

    if str_p_cond == '0':
        df_return['POP_PO'] = df_return['POP Qty(' + Param_Step + ')']
        df_return['Short_PO'] = df_return['Short Qty(' + Param_Step + ')']
        # Shipment Type == 'INDIR'인 경우에만 DMD ETA 4Week Sum Qty값 넣기
        df_return['DMD ETA 4Week Sum Qty'] = (
            np.where(df_return['Shipment Type'] == 'INDIR', df_return['DMD ETA 4Week Sum Qty'], 0)
        )

        # 대상건 추출 : 스텝별로 아래 메저 조건만 Po Process 대상임.
        #               PO Process_Last Step == null => P, PO Process_Last Step == 'M'
        df_return['Last Step'] = df_return['Last Step'].replace(r'^\s*$', np.nan, regex=True).fillna('P').astype(str)
        list_where = df_return['Last Step'] == Param_Step
        df_return = df_return[list_where].drop(columns='Last Step')

    else:
        df_return.rename(columns={'Org_Time.[Week]': 'Rdd Week'}, inplace=True)

    return df_return


@_decoration_
def fn_aggregation(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
        STEP 0-3. df_poProcess 테이블을 Prod Week + From + To + Item 기준으로 Aggregation.
                  (POP_PO : sum, 나머지 칼럼 : first)
        STEP 0-4. df_loadingDirOrderMgmt 테이블을 Prod Week + From + To + Account + ShipTo + Item 기준으로
                  Aggregation. (Loading Qty:sum, 나머지 칼럼 : first)
    :param df_p_source: df_poProcess, df_loadingDirOrderMgmt
    :param str_p_cond: '0' - df_poProcess, '1' - df_loadingDirOrderMgmt
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]

    # 입력 DataFrame 이 빈 테이블일 경우 해당 DataFrame을 반환한다.
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    if str_p_cond == '0':
        list_col = ['Week', 'From', 'To Site', 'Item']

        # Prod Week + From + To Site + Item 기준으로 POP_PO, Short_PO, DMD ETA 4Week Sum Qty 를 sum한다.
        # (나머지 칼럼들은 first)
        df_return = df_p_source.groupby(list_col).agg({
            'Org_Time.[Week]': 'first',
            'SOP Week.[SOP Week]': 'first',
            'Delivery Week.[Delivery Week]': 'first',
            'Shipment Type': 'first',
            'POP_PO': 'sum',
            'Short_PO': 'sum',
            'DMD ETA 4Week Sum Qty': 'sum',
        }).reset_index()

        # 칼럼 정리
        df_return = df_return[['Week', 'From', 'To Site', 'Item', 'Org_Time.[Week]', 'SOP Week.[SOP Week]',
                               'Delivery Week.[Delivery Week]', 'Shipment Type', 'POP_PO', 'Short_PO',
                               'DMD ETA 4Week Sum Qty']]
    else:
        list_col = ['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item']

        # Prod Week + From + To Site + Account + Ship To + Item 기준으로 Loading Qty  sum한다. (나머지는  first 값)
        df_return = df_p_source.groupby(list_col).agg({'Loading Qty': 'sum', 'Rdd Week': 'first'}).reset_index()

        # 칼럼 정리
        df_return = df_return[['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item', 'Loading Qty', 'Rdd Week']]

    return df_return


@_decoration_
def fn_merge_loadingDirOrderMgmt_pop(df_p_source: pd.DataFrame, df_p_poprocess: pd.DataFrame) -> pd.DataFrame:
    """
    예시) A_ : A경로라고 하자. (경로: Prod Week + From + To ,  ITEM : 1,2,3.. )
     DIR             | PO
     ------------------------------------------------
     직선적(A_1)     | 창고향
     직선적(A_3)     | 직선적(A_1)
     직선적(C)       | 직선적(A_2)
                     | 직선적(B)
     ------------------------------------------------
   => Po Process Detail 대상 : 창고향, 직선적(A_1), 직선적(A_2), 직선적(B), 직선적(A_3) 해당됨
     (Po Process데이터 전부와, Po Process의 직선적의 경로에 해당되는 Dir 데이터의 합집합 )

    STEP 1. df_aggregated_POProcess의 Prod Week + From + To 기준 으로 df_aggregated_loadingDirOrderMgmt
            존재하는 데이터를 Po Process Detail 직선적 PO의 동일경로 DIR 대상으로 추출하여 df1 생성 한다.
            ( df1 : 직선적(A_1), 직선적(A_3) 이 대상 )
            df_aggregated_loadingDirOrderMgmt의 Simul Qty(or Confirm Qty(추후에 dir mgmt에서 생성))를
            copy하여 Order Mgmt Qty 칼럼 생성 한다.

    :param df_p_source: df_aggregated_loadingDirOrderMgmt
    :param df_p_poprocess:  df_aggregated_poProcess
    :return: DataFrame
   """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # df_aggregated_poProcess 비어 있을 경우 빈 테이블을 반환한다.
    if df_p_poprocess.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_poprocess)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    df_po_route = df_p_poprocess[['Week', 'From', 'To Site']].drop_duplicates().copy(deep=True)
    df_return = df_p_source.merge(df_po_route, how='inner', on=['Week', 'From', 'To Site'])

    #  Loading Qty → Order Mgmt Qty 생성 (추후에 dirOrderMgmt 에 Confirm Qty 생성 되면 Confirm Qty → Order Mgmt Qty 로 변경 )
    df_return['Order Mgmt Qty'] = df_return['Loading Qty']

    # 칼럼 정리
    df_return = df_return[['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item', 'Order Mgmt Qty', 'Rdd Week']]

    return df_return


@_decoration_
def fn_split(df_p_source: pd.DataFrame, df_p_poprocess: pd.DataFrame) -> pd.DataFrame:
    """
      STEP 2. df1 과 PO 테이블(df_aggregated_poProcess)을 outer join 하여 Po Process Detail의 전체 대상인
        df3를 생성 한다.( 창고향, 직선적 데이터 모두 Po Process Detail에 담기 )
        Prod Week + From + To + Item 기준으로 [Order Mgmt Qty].transform(sum) 하여
        MgmtQty_TOT 로 칼럼 생성 한다. Split 로직을 반영 한다.

        ※ Split 로직. ( df3 POP 할당 방법 )
          1) left_only  : POP = 0 ( ▶ dir에만 존재할 경우 0 )
          2) right_only : POP = POP_PO  ( ▶ po에만 존재할 경우 POP_PO )
          3) both ( ▶ POP_PO 양만큼 분배 )
            i)  MgmtQty_TOT == POP_PO → POP = Order Mgmt Qty.
            ii) POP_PO > MgmtQty_TOT  → POP = Order Mgmt Qty 해주고,
                (POP_PO - MgmtQty_TOT = GAP_POP => POP) 만큼
                Prod Week + From + To + Account(NULL) + Ship To(NULL) + Item + GAP_POP 한줄 추가.
                ( ▶ POP_PO > dir 일 경우에는 한줄 추가해서 POP_PO만큼 꽉! 채워 준다.)
            iii) POP_PO < MgmtQty_TOT (Split case)
            → a) Prod Week + From + To + Account + Ship To + Order Mgmt Qty(큰 순) 순으로 SORT.
              b) Order Mgmt Qty를 CumSum하여 CUM_SUM_QTY로 칼럼 생성.
                 POP_PO - CUM_SUM_QTY >= 0 → POP = Order Mgmt Qty
                 POP_PO - CUM_SUM_QTY < 0  → POP = Order Mgmt Qty + (POP_PO - CUM_SUM_QTY) = RESULT
                                                   : RESULT > 0  → RESULT
                                                   : RESULT <= 0 → RESULT = 0
                ( ▶ POP_PO < dir 일 경우에는 sort해서 POP_PO만큼 딱! 잘라서 나눠준다.)

        ※ Split 로직 (Short Qty 할당 방법 )
        -  Block in ('INDIR', 'DIR_PO') : Detail에 한줄 추가로 Short Qty 반영됨
        - Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 경우
         Prod Week + From + To + Account(Null) + Ship To(Null) 로 한줄 생성하여 Short Qty 반영해준다.

        1) Short Qty 반영 ( Short Qty > 0 )
          Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 건을
          ['Week', 'From', 'To Site', 'Item','Short_PO', 'Block','Org_Time.[Week]','SOP Week.[SOP Week]',
          'Delivery Week.[Delivery Week]'] 별로 Short Qty 발췌 : df_return_both_append
        2) df_return_both 에서 Block == 'DIR_BOTH' 인 건 Short Qty = 0 처리
        3) df_return_both , df_return_both_append concat 후,
           ['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item'] 별로 groupby sum()

    :param df_p_source: df_dirOrderMgmt_merged
    :param df_p_poprocess: df_aggregated_poProcess
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # df_aggregated_POProcess 비어 있을 경우 빈 테이블을 반환한다.
    if df_p_poprocess.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_poprocess)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # KEY 기준
    list_col = ['Week', 'From', 'To Site', 'Item']
    # outer join
    df_return = df_p_source.merge(df_p_poprocess, how='outer', on=list_col, indicator=True)

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return[['Order Mgmt Qty', 'POP_PO', 'DMD ETA 4Week Sum Qty']] = (
        df_return[['Order Mgmt Qty', 'POP_PO', 'DMD ETA 4Week Sum Qty']]
        .replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    )

    # MgmtQty_TOT 칼럼 생성
    df_return['MgmtQty_TOT'] = df_return.groupby(list_col)['Order Mgmt Qty'].transform('sum')

    #  POP 생성 기준
    ####################################################################################################################
    #  ※ Split 로직. ( df3 POP 할당 방법 )
    #  1) left_only  : POP = 0 ( ▶ dir에만 존재할 경우 0 )
    #  2) right_only : POP = POP_PO  ( ▶ po에만 존재할 경우 POP_PO )
    #  3) both ( ▶ POP_PO 양만큼 분배 )
    #    i)  MgmtQty_TOT == POP_PO → POP = Order Mgmt Qty.
    #    ii) POP_PO > MgmtQty_TOT  → POP = Order Mgmt Qty 해주고,
    #        (POP_PO - MgmtQty_TOT = GAP_POP => POP) 만큼
    #        Prod Week + From + To + Account(NULL) + Ship To(NULL) + Item + GAP_POP 한줄 추가.
    #        ( ▶ POP_PO > dir 일 경우에는 한줄 추가해서 POP_PO만큼 꽉! 채워 준다.)
    #    iii) POP_PO < MgmtQty_TOT (Split case)
    #        → a) Prod Week + From + To + Account + Ship To +Order Mgmt Qty(큰 순) 순으로 SORT.
    #          b) Order Mgmt Qty를 CumSum하여 CUM_SUM_QTY로 칼럼 생성.
    #             POP_PO - CUM_SUM_QTY >= 0 → POP = Order Mgmt Qty
    #             POP_PO - CUM_SUM_QTY < 0  → POP = Order Mgmt Qty + (POP - CUM_SUM_QTY) = RESULT
    #                                               : RESULT > 0  → RESULT
    #                                               : RESULT <= 0 → RESULT = 0
    #            ( ▶ POP_PO < dir 일 경우에는 sort해서 POP_PO만큼 딱! 잘라서 나눠준다.)
    #
    #  ※ Split 로직 (Short Qty 할당 방법 )
    #  - Block in ('INDIR', 'DIR_PO') : Detail에 한줄 추가로 Short Qty 반영 됨
    #  - Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 경우
    #    Prod Week + From + To + Account(Null) + Ship To(Null) 로 한줄 생성하여 Short Qty 반영해준다.
    #
    #  1) Short Qty 반영 ( Short Qty > 0 )
    #    Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 건을
    #    ['Week', 'From', 'To Site', 'Item','Short_PO', 'Block','Org_Time.[Week]','SOP Week.[SOP Week]',
    #    'Delivery Week.[Delivery Week]'] 별로 Short Qty 발췌 : df_return_both_append
    #  2) df_return_both 에서 Block == 'DIR_BOTH' 인 건 Short Qty = 0 처리
    #  3) df_return_both , df_return_both_append concat 후,
    #     ['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item'] 별로 groupby sum()
    ####################################################################################################################
    # Block 설정
    # in_DirLoadingMgmt에만 있는 경우
    list_where_left_only = df_return['_merge'] == 'left_only'
    df_return.loc[list_where_left_only, 'POP'] = 0
    # Dir에만 있는 경우 상단 추가를 위한 key값 반영 (mgmt Rdd Week → Delivery Week) , 구분자 추가
    df_return.loc[list_where_left_only, 'Delivery Week.[Delivery Week]'] = df_return.loc[list_where_left_only, 'Rdd Week']
    # Block 구분자 ( Dir에만 존재하는 경우 : DIR_ONLY )
    df_return.loc[list_where_left_only, 'Block'] = STR_DIR_ONLY

    # in_poProcess에만 있는 경우
    list_where_right_only = df_return['_merge'] == 'right_only'
    df_return.loc[list_where_right_only, 'POP'] = df_return['POP_PO']
    # Block 구분자  ( PO 에만 존재하는 경우 : INDIR, DIR_PO )
    list_where_dir = df_return['Shipment Type'] == 'DIR_D'
    df_return.loc[list_where_right_only & list_where_dir, 'Block'] = STR_DIR_PO
    df_return.loc[list_where_right_only & ~list_where_dir, 'Block'] = STR_INDIR

    # 둘다 있는 경우
    # 1) MgmtQty_TOT == POP_PO
    list_where_both = df_return['_merge'] == 'both'
    # Block 구분자 ( PO , DIR 존재하는 경우 : DIR_BOTH )
    df_return.loc[list_where_both, 'Block'] = STR_DIR_BOTH
    list_where_same_qty = df_return['MgmtQty_TOT'] == df_return['POP_PO']
    list_where = list_where_both & list_where_same_qty
    df_return_same = df_return[list_where].copy()
    df_return_same['POP'] = df_return_same['Order Mgmt Qty']

    # 2) POP_PO > MgmtQty_TOT
    list_where_over_poppo = df_return['MgmtQty_TOT'] < df_return['POP_PO']
    list_where = list_where_both & list_where_over_poppo
    df_return_over_pop = df_return[list_where].copy()

    df_return_over_pop['ngroup'] = df_return_over_pop.groupby(list_col).ngroup()
    df_return_over_pop['rank'] = df_return_over_pop.groupby('ngroup').cumcount() + 1
    list_where_group_first = df_return_over_pop['rank'] == 1
    df_return_over_pop['POP'] = df_return_over_pop['Order Mgmt Qty']
    df_return_over_pop_append = df_return_over_pop[list_where_group_first].copy()
    df_return_over_pop_append[['Account', 'Ship To', 'Order Mgmt Qty']] = [np.nan, np.nan, 0]
    df_return_over_pop_append['POP'] = df_return_over_pop_append['POP_PO'] - df_return_over_pop_append['MgmtQty_TOT']

    df_return_over_pop = pd.concat([df_return_over_pop, df_return_over_pop_append], ignore_index=True)

    # 3) POP_PO < MgmtQty_TOT
    list_where_over_dir = df_return['MgmtQty_TOT'] > df_return['POP_PO']
    list_where = list_where_both & list_where_over_dir
    df_return_over_dir = df_return[list_where].copy()

    # Prod Week + From + To + Account + Ship To +Order Mgmt Qty(큰 순) 순으로 정렬
    df_return_over_dir.sort_values(by=['Week', 'From', 'To Site', 'Item', 'Order Mgmt Qty'],
                                   ascending=[True, True, True, True, False], inplace=True)

    # POP_PO 할당 되도록 Split.
    df_return_over_dir['MgmtQty_CUMSUM'] = df_return_over_dir.groupby(list_col)['Order Mgmt Qty'].cumsum()
    list_where_over_pop_cumsum = df_return_over_dir['POP_PO'] >= df_return_over_dir['MgmtQty_CUMSUM']
    df_return_over_dir.loc[list_where_over_pop_cumsum, 'POP'] = df_return_over_dir['Order Mgmt Qty']
    df_return_over_dir.loc[~list_where_over_pop_cumsum, 'POP'] = (
            df_return_over_dir['Order Mgmt Qty'] + (df_return_over_dir['POP_PO'] - df_return_over_dir['MgmtQty_CUMSUM'])
    )
    # 0보다 작으면 0
    df_return_over_dir.loc[df_return_over_dir['POP'] < 0, 'POP'] = 0

    df_return_both = pd.concat([df_return_same, df_return_over_pop, df_return_over_dir], ignore_index=True)

    # Short Qty 반영 ( Short Qty > 0 )
    # 1) df_return_both에서 Short Qty > 0 이고 Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해
    # ['Week', 'From', 'To Site', 'Item','Short_PO', 'Block','Org_Time.[Week]','SOP Week.[SOP Week]',
    # 'Delivery Week.[Delivery Week]'] 별로 Short Qty 발췌 : df_return_both_append
    # 2) df_return_both 에서 Block == 'DIR_BOTH' 인 건 Short Qty = 0 처리
    # 3) df_return_both , df_return_both_append concat 후,
    #   ['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item'] 별로 groupby sum()
    # 1) df_return_both_append 생성
    list_where_short_qty_is = df_return_both['Short_PO'] > 0
    df_return_both_append = (
        df_return_both.loc[list_where_short_qty_is, ['Week', 'From', 'To Site', 'Item','Short_PO', 'Block',
                                                     'Org_Time.[Week]','SOP Week.[SOP Week]', 'Delivery Week.[Delivery Week]']
        ].drop_duplicates().copy()
    )
    if not df_return_both_append.empty:
        # 2) Short Qty = 0 처리
        df_return_both['Short_PO'] = 0

        # 3) concat 후 groupby sum
        df_return_both = pd.concat([df_return_both, df_return_both_append], ignore_index=True)
        df_return_both = (
            df_return_both
            .groupby(['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item'], dropna=False)
            .agg({
                'Order Mgmt Qty' : 'sum',
                'POP' : 'sum',
                'DMD ETA 4Week Sum Qty' : 'sum',
                'Short_PO' : 'sum',
                'Block' : 'first',
                'Org_Time.[Week]' : 'first',
                'SOP Week.[SOP Week]' : 'first',
                'Delivery Week.[Delivery Week]' : 'first'
            }).reset_index()
        )

    # concat
    df_return = pd.concat([df_return[~list_where_both], df_return_both], ignore_index=True)

    # 칼럼 정리
    df_return = df_return[['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item',
                           'Order Mgmt Qty', 'POP', 'Block', 'DMD ETA 4Week Sum Qty', 'Short_PO',
                           'Org_Time.[Week]', 'SOP Week.[SOP Week]', 'Delivery Week.[Delivery Week]']]
    return df_return


def fn_after_step(df_p_source: pd.DataFrame) -> tuple:
    """
    1. Step별로 후처리 로직을 반영 한다.
        1) Step 'P' : Created by, Creation time, Chk Last Step(P), Last Step 칼럼 반영.
                      Prod Week + From + To + Item 별로 Seq 채번 생성.
        2) Step 'M' : in_POProcessDetail(P의 최종 POProcessDetail) 과
                      df3(M단계 Detail 데이터)을  Prod Week + From + To + Account + Ship To + Item 별로
                      outer join 함.
                      i) 중복되면 Updated by, Updated time 신규건이면 Created by, Creation time 반영.
                      ii) Seq :  key기준으로 P에 있는 경우는 P의 seq를 사용하고,
                      신규건은 P의 max(seq) +1 을 초기값으로 하여 seq = 초기값 + (key별 seq 채번)
                      iii) SOP ETD Week, Block, Last Step : M 단계 값으로 수정

    2. ETD Week 생성한다. (ETD Week 존재하지 않을 경우)
      :  BOD Lane Item 의 shipment L/T 을 Production Week 에 더해서 ETD 산출
      ( ETD Week = Production Week + round(BOD Lane Item_Shipping Leadtime/ 7, 0) )

    3. Dir에만 존재하는 경우 상단 추가. (Week + From + To 존재하나 Item이 다른 경우(Dir에만 있는 경우))
     : detail을 상단 key기준으로 grouping 하여 POP = 0(SUM) , Data Source(2 : 'P' , 3: 'M' ) 구분자로
       PO Process 메저 한줄 추가

    :param df_p_source: rename 된 df_poProcess_splited
    :return: tuple
    """
    # DataFrame copy
    df_return = df_p_source.copy(deep=True)

    # 기준 column
    list_col = ['MFG Week.[MFG Week]', 'Sub Location.[Sub Location]', 'Location.[Location]',
                'PO Process Detail_Account', 'PO Process Detail_Ship To', 'Item.[Item]']

    # Seq 채번 Column
    list_col_seq = ['MFG Week.[MFG Week]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Item.[Item]']

    # output Column
    col_output = []

    # 배치 사용자 : 'SYSTEM', 배치 시간 :  datetime.now()
    str_batch_name = 'SYSTEM'
    str_batch_time = datetime.now()

    # 1. Step별 후처리
    # 1-1. Param_Step = 'P' 의 경우
    if Param_Step == 'P':
        # CRE 정보 입력
        df_return['PO Process Detail_Created by'] = str_batch_name
        df_return['PO Process Detail_Creation time'] = str_batch_time

        # PO Process Detail_Chk Last Step(P) = 'Y' 입력
        df_return['PO Process Detail_Chk Last Step(P)'] = 'Y'

        # PO Process Detail_Last Step 입력 (  PO Process Detail 데이터 최종 단계 구분자 )
        #                                   → 1 , 2     : Split 수행시 입력.
        #                                   → 3 , 4 , 5 : Simulation 수행시 입력.
        df_return['PO Process Detail_Last Step'] = 1

        # output column
        col_output = [
            'Version.[Version Name]', 'Time.[Week]', 'MFG Week.[MFG Week]',
            'Sub Location.[Sub Location]', 'Location.[Location]', 'Item.[Item]', 'Seq.[Seq]',
            'PO Process Detail_SOP ETD Week', 'PO Process Detail_Account', 'PO Process Detail_Ship To',
            'PO Process Detail_Order Mgmt Qty(P)',
            'PO Process Detail_POP Qty(P)',
            'PO Process Detail_Short Qty(P)',
            'PO Process Detail_Check Qty(P)',
            'PO Process Detail_Chk Last Step(P)',
            'PO Process Detail_Block',
            'PO Process Detail_Last Step',
            'PO Process Detail_Created by',
            'PO Process Detail_Creation time',
            'PO Process Detail_DMD ETA 4Week Sum Qty'
        ]

        # Seq 생성 : Prod Week + From + To + Item 별로 Seq 채번
        df_return['Seq.[Seq]'] = (
                df_return
                .sort_values(by=list_col)
                .groupby(list_col_seq)['PO Process Detail_Order Mgmt Qty(' + Param_Step + ')'].cumcount() + 1
        ).astype(str)

    # 1-2. Param_Step = 'M' 의 경우 'P'에서 fix 된 데이터와 'M'엔진의 데이터 outer join
    if Param_Step == 'M':
        df_return = in_POProcessDetail.merge(df_return, how='outer', on=list_col, indicator=True)

        # 수정건(P에도 있고, M에도 있고)
        list_where_both = df_return['_merge'] == 'both'
        df_return.loc[list_where_both, 'PO Process Detail_Updated by'] = str_batch_name
        df_return.loc[list_where_both, 'PO Process Detail_Update time'] = str_batch_time
        # 신규건 (M에만 있는 건)
        list_where_right = df_return['_merge'] == 'right_only'
        df_return.loc[list_where_right, 'PO Process Detail_Created by'] = str_batch_name
        df_return.loc[list_where_right, 'PO Process Detail_Creation time'] = str_batch_time

        # Seq 채번 : key기준으로 P에 있는 경우는 P의 seq를 사용하고,
        # 신규건은 P의 max(seq) +1 을 초기값으로 하여 seq = 초기값 + (key별 seq 채번) 으로 순번 매긴다.
        df_return['Seq.[Seq]'] = df_return['Seq.[Seq]'].astype(float)
        df_return.loc[list_where_right, 'group max seq'] = (
            df_return.groupby(list_col_seq, dropna=False)['Seq.[Seq]'].transform('max')
        ).fillna(0)
        df_return.loc[list_where_right, 'Seq.[Seq]'] = (
                df_return.loc[list_where_right, 'group max seq']
                + df_return[list_where_right].groupby(list_col_seq).cumcount() + 1
        ).tolist()

        # 형변환
        df_return['Seq.[Seq]'] = df_return['Seq.[Seq]'].astype(dtype='int64').astype(str)

        # PO Process Detail_SOP ETD Week( M 기준으로 최신 값 반영 )
        df_return['PO Process Detail_SOP ETD Week'] = np.where(
            df_return['_merge'] == 'left_only',
            df_return['PO Process Detail_SOP ETD Week_x'],
            df_return['PO Process Detail_SOP ETD Week_y']
        )

        # PO Process Detail_Block ( P에만 있는 row일 경우는 P의 Block, 이외에는 M 기준으로 최신 Block 구분)
        df_return['PO Process Detail_Block'] = np.where(
            df_return['_merge'] == 'left_only',
            df_return['PO Process Detail_Block_x'],
            df_return['PO Process Detail_Block_y']
        )

        # PO Process Detail_DMD ETA 4Week Sum Qty( M 기준으로 최신 값 반영 )
        df_return['PO Process Detail_DMD ETA 4Week Sum Qty'] = np.where(
            df_return['_merge'] == 'left_only',
            df_return['PO Process Detail_DMD ETA 4Week Sum Qty_x'],
            df_return['PO Process Detail_DMD ETA 4Week Sum Qty_y']
        )

        # PO Process Detail_Last Step 입력 ( PO Process 데이터 최종 단계 구분자 )
        df_return['PO Process Detail_Last Step'] = np.where(
            df_return['_merge'] == 'left_only',
            df_return['PO Process Detail_Last Step'],
            2
        )

        col_output = [
            'Version.[Version Name]', 'Time.[Week]', 'MFG Week.[MFG Week]',
            'Sub Location.[Sub Location]', 'Location.[Location]', 'Item.[Item]', 'Seq.[Seq]',
            'PO Process Detail_SOP ETD Week', 'PO Process Detail_Account', 'PO Process Detail_Ship To',
            'PO Process Detail_Order Mgmt Qty(P)',
            'PO Process Detail_Order Mgmt Qty(M)',
            'PO Process Detail_POP Qty(P)',
            'PO Process Detail_POP Qty(M)',
            'PO Process Detail_Short Qty(P)',
            'PO Process Detail_Short Qty(M)',
            'PO Process Detail_Check Qty(P)',
            'PO Process Detail_Check Qty(M)',
            'PO Process Detail_Block',
            'PO Process Detail_Last Step',
            'PO Process Detail_Created by',
            'PO Process Detail_Creation time',
            'PO Process Detail_Updated by',
            'PO Process Detail_Update time',
            'PO Process Detail_DMD ETA 4Week Sum Qty'
        ]

    # 2. ETD Week 생성. (ETD Week 존재하지 않을 경우)
    #   : BOD Lane Item 의 shipment L/T 을 Production Week 에 더해서 ETD 산출
    #   : ETD Week = Production Week + round(BOD Lane Item_Shipping Leadtime/ 7, 0)
    list_where_etd_null = df_return['PO Process Detail_SOP ETD Week'].isnull()
    df_return_etd_null = df_return[list_where_etd_null].copy()

    if not df_return_etd_null.empty:
        # From/To/Item 기준으로 shipping L/T 중복으로 나올 경우 Priority 가 높은 것 L/T 짧은 것.
        # 대상만 발라서 bodLaneItem 으로 반환
        df_bodLaneItem = df_return_etd_null.merge(in_BodLaneItem, how='inner', on='Item.[Item]')
        df_bodLaneItem = df_bodLaneItem[
            ['BOD.[BOD Name]', 'Item.[Item]', 'BOD Lane Item_Shipping Leadtime', 'BOD Lane Item_Priority']
        ]

        # From/To 칼럼 생성
        df_bodLaneItem['BOD List'] = df_bodLaneItem['BOD.[BOD Name]'].str.split('_')
        df_bodLaneItem['Sub Location.[Sub Location]'] = df_bodLaneItem['BOD List'].str[0]
        df_bodLaneItem['Location.[Location]'] = df_bodLaneItem['BOD List'].str[1]

        # BodLaneItem 중복제거
        df_bodLaneItem_dup = (
            df_bodLaneItem
            .sort_values(by=['Sub Location.[Sub Location]', 'Location.[Location]', 'Item.[Item]',
                             'BOD Lane Item_Priority', 'BOD Lane Item_Shipping Leadtime'],
                         ascending=[True, True, True, False, True])
            .drop_duplicates(subset=['Sub Location.[Sub Location]', 'Location.[Location]', 'Item.[Item]'], keep='first')
        )

        # ETD Week null 인 DataFrame의 bod정보 찾기
        df_return_etd_null = (
            df_return_etd_null
            .merge(df_bodLaneItem_dup, how='left', on=['Sub Location.[Sub Location]', 'Location.[Location]', 'Item.[Item]'])
        )

        # bod shipping l/t 주차로 변환
        # df_return_etd_null['l/t'] = round(df_return_etd_null['BOD Lane Item_Shipping Leadtime'] / 7, 0)
        df_return_etd_null['l/t']  = (
            df_return_etd_null['BOD Lane Item_Shipping Leadtime'].apply(
                lambda x: decimal.Decimal(str(x/7)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP)
            )
        ).astype(float)

        # ETD Week 찾기
        df_return_etd_null['PO Process Detail_SOP ETD Week'] = (
            df_return_etd_null.apply(lambda row: fn_get_etd_week(row), axis=1)
        )

    # concat
    df_return = pd.concat([df_return[~list_where_etd_null], df_return_etd_null], ignore_index=True)

    # Version
    df_return['Version.[Version Name]'] = Param_OUT_VERSION

    # Po Week : df_aggregated_POProcess의 첫번째 행의 'Org_Time.[Week]' 반영
    df_return['Time.[Week]'] = df_aggregated_poProcess.loc[0, 'Org_Time.[Week]']

    # 칼럼 정렬
    df_return = df_return.sort_values(by=list_col_seq)

    # 3. Dir에만 존재하는 경우 상단 추가.
    list_where_dir_only = df_return['PO Process Detail_Block'] == STR_DIR_ONLY
    df_return_dir_only = df_return[list_where_dir_only].copy()
    df_return_po_process = pd.DataFrame()
    if not df_return_dir_only.empty:
        df_return_po_process = (
            df_return_dir_only
            .groupby(['Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Time.[Week]',
                      'MFG Week.[MFG Week]', 'Item.[Item]'])
            .agg({'PO Process Detail_POP Qty(' + Param_Step + ')': 'sum',  # sum 0 나옴. (split 시에 0으로 만들어놔서)
                  'PO Process Detail_SOP ETD Week': 'first',
                  'Delivery Week.[Delivery Week]': 'first'})
            .reset_index()
        )

        df_return_po_process.rename(columns={
            'PO Process Detail_SOP ETD Week': 'SOP Week.[SOP Week]',
            'PO Process Detail_POP Qty(' + Param_Step + ')': 'PO Process_POP Qty(' + Param_Step + ')'}, inplace=True)

        # 하단에서 올라온 값
        # P에서 생성된 값
        if Param_Step == 'P':
            str_data_source = '2'
        # M에서 생성된 값
        else:
            str_data_source = '3'
        df_return_po_process['PO Process_Data Source'] = str_data_source
        df_return_po_process['PO Process_Created by'] = str_batch_name
        df_return_po_process['PO Process_Creation time'] = str_batch_time
        col_output_po = ['Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
                         'Time.[Week]', 'MFG Week.[MFG Week]', 'SOP Week.[SOP Week]', 'Delivery Week.[Delivery Week]',
                         'Item.[Item]', 'PO Process_POP Qty(' + Param_Step + ')', 'PO Process_Data Source',
                         'PO Process_Created by', 'PO Process_Creation time']
        df_return_po_process = df_return_po_process[col_output_po]

    # 칼럼 정리
    df_return = df_return[col_output]

    return df_return, df_return_po_process


@_decoration_
def fn_output_formatter(df_p_source: pd.DataFrame) -> tuple:
    """
    STEP 3. output을 칼럼 정리한다.
            Step별로 후처리 로직을 반영 한다.
    :param df_p_source: df_poProcess_splited
    :return: tuple
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있을때 빈 테이블 반환한다.
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return, df_return

    # 데이터 프레임 복사
    df_return = df_p_source.copy(deep=True)

    # Rename
    df_return.rename(columns={
        'From': 'Sub Location.[Sub Location]',
        'To Site': 'Location.[Location]',
        'Item': 'Item.[Item]',
        'Org_Time.[Week]': 'Time.[Week]',
        'Week': 'MFG Week.[MFG Week]',
        'Account': 'PO Process Detail_Account',
        'Ship To': 'PO Process Detail_Ship To',
        'Order Mgmt Qty': 'PO Process Detail_Order Mgmt Qty(' + Param_Step + ')',
        'POP': 'PO Process Detail_POP Qty(' + Param_Step + ')',
        'Short_PO': 'PO Process Detail_Short Qty(' + Param_Step + ')',
        'SOP Week.[SOP Week]': 'PO Process Detail_SOP ETD Week',
        'Block': 'PO Process Detail_Block',
        'DMD ETA 4Week Sum Qty': 'PO Process Detail_DMD ETA 4Week Sum Qty',
    }, inplace=True)

    # Pop → Chk Qty 반영
    df_return['PO Process Detail_Check Qty(' + Param_Step + ')'] = df_return['PO Process Detail_POP Qty(' + Param_Step + ')']

    # Step별로 후처리
    df_return, df_return_po_process = fn_after_step(df_return)

    return df_return, df_return_po_process


def fn_get_etd_week(df_p_source: pd.Series) -> str:
    """
    ETD Week 존재하지 않을 경우 ETD Week 산출
    : BOD Lane Item 의 shipment L/T 을 Production Week 더하기)
    :param :df_p_source
    :return: str
    """
    # 반환값 설정
    str_return = np.nan
    # in_Time sort
    df_time_sort = in_Time.sort_values('Time.[Week]')

    # L/T 빈값이 아닐 때만 반환
    if not pd.isna(df_p_source['l/t']):
        list_where = df_time_sort['Time.[Week]'] == df_p_source['MFG Week.[MFG Week]']
        # 해당 주차가 in_Time 테이블에 있고
        if len(df_time_sort[list_where]) == 1:
            int_target_idx = df_time_sort[list_where].index + df_p_source['l/t']
            # 주차 인덱스에 gap을 더한 target인덱스가 정상적인 범위내에 있을때
            # ( 최소, 최대 index 포함될 경우 target Time.[Week] 반환)
            if df_time_sort.index.min() <= int_target_idx <= df_time_sort.index.max():
                str_return = df_time_sort.loc[int_target_idx, 'Time.[Week]'].values[0]
    return str_return


@_decoration_
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """

    # OUTPUT column
    if str_p_cond == '0':
        col_output = [
            'Version.[Version Name]', 'Time.[Week]', 'MFG Week.[MFG Week]',
            'Sub Location.[Sub Location]', 'Location.[Location]', 'Item.[Item]', 'Seq.[Seq]',
            'PO Process Detail_SOP ETD Week', 'PO Process Detail_Account', 'PO Process Detail_Ship To',
            'PO Process Detail_Order Mgmt Qty(P)', 'PO Process Detail_Order Mgmt Qty(M)',
            'PO Process Detail_POP Qty(P)', 'PO Process Detail_POP Qty(M)',
            'PO Process Detail_Short Qty(P)', 'PO Process Detail_Short Qty(M)',
            'PO Process Detail_Created by', 'PO Process Detail_Creation time', 'PO Process Detail_Updated by',
            'PO Process Detail_Update time', 'PO Process Detail_Block', 'PO Process Detail_Last Step',
            'PO Process Detail_Check Qty(P)', 'PO Process Detail_Check Qty(M)', 'PO Process Detail_DMD ETA 4Week Sum Qty'
        ]
    else:
        col_output = [
            'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
            'Time.[Week]', 'MFG Week.[MFG Week]', 'SOP Week.[SOP Week]', 'Delivery Week.[Delivery Week]',
            'Item.[Item]', '[Seq].[Seq]', 'PO Process_POP Qty(' + Param_Step + ')', 'PO Process_Data Source']

    df_return = pd.DataFrame(columns=col_output)

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    pd.set_option('display.width', 400)
    pd.set_option('display.max_columns', None)

    # Output 테이블 선언
    out_POProcess = pd.DataFrame()
    out_POProcessDetail = pd.DataFrame()
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
            Param_Step = 'M'

            in_POProcess = pd.read_csv(str_input_dir + "/in_POProcess.csv",
                                       dtype={"Time.[Week]": str,
                                              "SOP Week.[SOP Week]": str,
                                              "Delivery Week.[Delivery Week]": str,
                                              "MFG Week.[MFG Week]": str}, encoding="UTF8")
            in_LoadingDirOrderMgmt = pd.read_csv(str_input_dir + "/in_LoadingDirOrderMgmt.csv",
                                                 dtype={"Time.[Week]": str,
                                                        "Sales Domain.[Ship To]": str,
                                                        "Loading Dir Order Mgmt_Adj Prod Week": str,
                                                        "Loading Dir Order Mgmt_Ship To": str},
                                                 encoding="UTF8")

            in_POProcessDetail = pd.read_csv(str_input_dir + "/in_POProcessDetail.csv",
                                             dtype={"Time.[Week]": str,
                                                    "MFG Week.[MFG Week]": str,
                                                    "PO Process Detail_SOP ETD Week": str,
                                                    "PO Process Detail_Account": str,
                                                    "PO Process Detail_Ship To": str},
                                             encoding="UTF8")

            in_BodLaneItem = pd.read_csv(str_input_dir + "/in_BodLaneItem.csv", encoding="UTF8")
            in_Time = pd.read_csv(str_input_dir + "/in_Time.csv", dtype={"Time.[Week]": str}, encoding="UTF8")

            # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'

        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        if Param_Step is None or Param_Step.strip() == '':
            Param_Step = 'P'

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_POP_TYPE : {Param_Step}', p_log_level=LOG_LEVEL.debug())

        # 입력 테이블 점검 및 로그
        fn_check_input_table(in_POProcess, 'in_POProcess', '1')
        fn_check_input_table(in_LoadingDirOrderMgmt, 'in_LoadingDirOrderMgmt', '1')
        fn_check_input_table(in_POProcessDetail, 'in_POProcessDetail', '1')
        fn_check_input_table(in_BodLaneItem, 'in_BodLaneItem', '1')
        fn_check_input_table(in_Time, 'in_Time', '1')

        # 상수값 선언
        STR_INDIR = 'INDIR'
        STR_DIR_PO = 'DIR_PO'
        STR_DIR_BOTH = 'DIR_BOTH'
        STR_DIR_ONLY = 'DIR_ONLY'
        ################################################################################################################
        # STEP 0-1. 로직 구동 시 예외 사항이 발생 하는 특정 컬럼의 경우 선처리 작업 진행함.
        ################################################################################################################
        # 선처리 작업
        dict_log = {
            'p_step_no': 10,
            'p_step_desc': 'STEP 0-1. 전처리(in_POProcess): 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 '
                           '작업 진행함.',
            'p_df_name': 'df_poProcess'
        }
        df_poProcess = fn_preprocess(in_POProcess, '0', **dict_log)

        dict_log = {
            'p_step_no': 20,
            'p_step_desc': 'STEP 0-2. 전처리(in_LoadingDirOrderMgmt): 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 '
                           '작업 진행함.',
            'p_df_name': 'df_loadingDirOrderMgmt'
        }
        df_loadingDirOrderMgmt = fn_preprocess(in_LoadingDirOrderMgmt, '1', **dict_log)

        ################################################################################################################
        # STEP 0-2. df_poProcess, df_loadingDirOrderMgmt Aggregation
        ################################################################################################################
        dict_log = {
            'p_step_no': 30,
            'p_step_desc': 'STEP 0-3. df_poProcess 테이블을 Prod Week-From-To Site-Item을 기준으로 Aggregation.',
            'p_df_name': 'df_aggregated_poProcess'
        }
        df_aggregated_poProcess = fn_aggregation(df_poProcess, '0', **dict_log)

        dict_log = {
            'p_step_no': 40,
            'p_step_desc': 'STEP 0-4. df_loadingDirOrderMgmt 테이블을 Prod Week-From-To Site-Account-ShipTo-Item을 기'
                           '준으로 Aggregation.',
            'p_df_name': 'df_aggregated_loadingDirOrderMgmt'
        }
        df_aggregated_loadingDirOrderMgmt = fn_aggregation(df_loadingDirOrderMgmt, '1', **dict_log)

        ################################################################################################################
        # STEP 1. df_aggregated_poProcess 의 Prod Week + From + To 기준 으로 df_aggregated_loadingDirOrderMgmt
        # 존재하는 데이터를 Po Process Detail 직선적 PO의 동일경로 DIR 대상으로 추출하여 df1 생성 한다.
        # ( df1 : 직선적(A_1), 직선적(A_3) 이 대상 )
        # df_aggregated_loadingDirOrderMgmt의 Simul Qty(or Confirm Qty(추후에 dir mgmt에서 생성))를 copy하여
        # Order Mgmt Qty 칼럼 생성 한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 100,
            'p_step_desc': 'STEP 1. df_aggregated_poProcess 의 Prod Week + From + To 기준 으로 '
                           'df_aggregated_loadingDirOrderMgmt에 존재하는 데이터를 Po Process Detail 직선적 PO의 동일경로'
                           ' DIR 대상으로 추출하여 df1 생성 한다.( df1 : 직선적(A_1), 직선적(A_3) 이 대상 )'
                           'df_aggregated_loadingDirOrderMgmt의 Simul Qty(or Confirm Qty(추후에 dir mgmt에서 생성))를 '
                           'copy하여 Order Mgmt Qty 칼럼 생성 한다.',
            'p_df_name': 'df_dirOrderMgmt_merged'
        }
        df_dirOrderMgmt_merged = fn_merge_loadingDirOrderMgmt_pop(df_aggregated_loadingDirOrderMgmt,
                                                                  df_aggregated_poProcess, **dict_log)

        ################################################################################################################
        # STEP 2. df1 과 PO 테이블(df_aggregated_poProcess)을 outer join 하여 Po Process Detail의 전체 대상인
        # df3를 생성 한다.( 창고향, 직선적 데이터 모두 Po Process Detail에 담기 )
        # Prod Week + From + To + Item 기준으로 [Order Mgmt Qty].transform(sum) 하여
        # MgmtQty_TOT 로 칼럼 생성 한다. Split 로직을 반영 한다.
        #
        # ※ Split 로직. ( df3 POP 할당 방법 )
        #   1) left_only  : POP = 0 ( ▶ dir에만 존재할 경우 0 )
        #   2) right_only : POP = POP_PO  ( ▶ po에만 존재할 경우 POP_PO )
        #   3) both ( ▶ POP_PO 양만큼 분배 )
        #     i)  MgmtQty_TOT == POP_PO → POP = Order Mgmt Qty.
        #     ii) POP_PO > MgmtQty_TOT  → POP = Order Mgmt Qty 해주고,
        #         (POP_PO - MgmtQty_TOT = GAP_POP => POP) 만큼
        #         Prod Week + From + To + Account(NULL) + Ship To(NULL) + Item + GAP_POP 한줄 추가.
        #         ( ▶ POP_PO > dir 일 경우에는 한줄 추가해서 POP_PO만큼 꽉! 채워 준다.)
        #     iii) POP_PO < MgmtQty_TOT (Split case)
        #     → a) Prod Week + From + To + Account + Ship To + Order Mgmt Qty(큰 순) 순으로 SORT.
        #       b) Order Mgmt Qty를 CumSum하여 CUM_SUM_QTY로 칼럼 생성.
        #          POP_PO - CUM_SUM_QTY >= 0 → POP = Order Mgmt Qty
        #          POP_PO - CUM_SUM_QTY < 0  → POP = Order Mgmt Qty + (POP_PO - CUM_SUM_QTY) = RESULT
        #                                            : RESULT > 0  → RESULT
        #                                            : RESULT <= 0 → RESULT = 0
        #         ( ▶ POP_PO < dir 일 경우에는 sort해서 POP_PO만큼 딱! 잘라서 나눠준다.)
        # ※ Split 로직 (Short Qty 할당 방법 )
        #  -  Block in ('INDIR', 'DIR_PO') : Detail에 한줄 추가로 Short Qty 반영됨
        #  - Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 경우
        #   Prod Week + From + To + Account(Null) + Ship To(Null) 로 한줄 생성하여 Short Qty 반영해준다.
        #
        #  1) Short Qty 반영 ( Short Qty > 0 )
        #    Block == 'DIR_BOTH' 인 건( Dir Split 대상 )에 대해 Short Qty > 0 인 건을
        #    ['Week', 'From', 'To Site', 'Item','Short_PO', 'Block','Org_Time.[Week]','SOP Week.[SOP Week]',
        #    'Delivery Week.[Delivery Week]'] 별로 Short Qty 발췌 : df_return_both_append
        #  2) df_return_both 에서 Block == 'DIR_BOTH' 인 건 Short Qty = 0 처리
        #  3) df_return_both , df_return_both_append concat 후,
        #     ['Week', 'From', 'To Site', 'Account', 'Ship To', 'Item'] 별로 groupby sum()
        ################################################################################################################
        dict_log = {
            'p_step_no': 200,
            'p_step_desc': 'STEP 2. df1 과 PO 테이블(df_aggregated_poProcess)을 outer join 하여 Po Process Detail의 '
                           '전체 대상인 df3를 생성 한다.( 창고향, 직선적 데이터 모두 Po Process Detail에 담기 )'
                           'Prod Week + From + To + Item 기준으로 [Order Mgmt Qty].transform(sum) 하여 MgmtQty_TOT 로 '
                           '칼럼 생성 한다. Split 로직을 반영 한다.',
            'p_df_name': 'df_poProcess_splited'
        }
        df_poProcess_splited = fn_split(df_dirOrderMgmt_merged, df_aggregated_poProcess, **dict_log)

        ################################################################################################################
        # STEP 3.
        #  Step 3-1. Step별로 후처리 로직을 반영 한다.
        #   1) Step 'P' : Created by, Creation time, Chk Last Step(P), Last Step 칼럼 반영.
        #                 Prod Week + From + To + Item 별로 Seq 채번 생성.
        #   2) Step 'M' : in_POProcessDetail(P의 최종 POProcessDetail) 과
        #                 df3(M단계 Detail 데이터)을  Prod Week + From + To + Account + Ship To + Item 별로
        #                 outer join 함.
        #                 i) 중복되면 Updated by, Updated time 신규건이면 Created by, Creation time 반영.
        #                 ii) Seq :  key기준으로 P에 있는 경우는 P의 seq를 사용하고,
        #                 신규건은 P의 max(seq) +1 을 초기값으로 하여 seq = 초기값 + (key별 seq 채번)
        #                 iii) SOP ETD Week, Block, Last Step : M 단계 값으로 수정
        #
        #  Step 3-2. ETD Week 생성한다. (ETD Week 존재하지 않을 경우)
        #    :  BOD Lane Item 의 shipment L/T 을 Production Week 에 더해서 ETD 산출
        #    ( ETD Week = Production Week + round(BOD Lane Item_Shipping Leadtime/ 7, 0) )
        #
        #  Step 3-3. Dir에만 존재하는 경우 상단 추가. (Week + From + To 존재하나 Item이 다른 경우)
        #   : detail을 상단 key기준으로 grouping 하여 POP = 0(SUM) , Data Source(2 : 'P' , 3: 'M' )
        #   구분자로 PO Process 메저 한줄 추가
        ################################################################################################################
        out_POProcessDetail, out_POProcess = fn_output_formatter(df_poProcess_splited)
        logger.Step(p_step_no=777, p_step_desc='최종 Output 정리.')
        fn_log_dataframe(out_POProcessDetail, 'out_POProcessDetail')
        fn_log_dataframe(out_POProcess, 'out_POProcess')

        # out_POProcess : 'SOP Week.[SOP Week]' 빈값일 경우 raise Exception 발생
        if not out_POProcess.empty and len(out_POProcess[out_POProcess['SOP Week.[SOP Week]'].isnull()]) > 0:
            raise Exception('There is no value in SOP Week.[SOP Week].')

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_POProcessDetail = None
            out_POProcess = None
            raise Exception(e)
        else:
            if out_POProcessDetail.empty:
                out_POProcessDetail = fn_set_header('0')
                fn_log_dataframe(out_POProcessDetail, 'out_POProcessDetail')
            if out_POProcess.empty:
                out_POProcess = fn_set_header('1')
                fn_log_dataframe(out_POProcess, 'out_POProcess')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_POProcessDetail.empty:
            out_POProcessDetail = fn_set_header('0')
            fn_log_dataframe(out_POProcessDetail, 'out_POProcessDetail')
        if out_POProcess.empty:
            out_POProcess = fn_set_header('1')
            fn_log_dataframe(out_POProcess, 'out_POProcess')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')

