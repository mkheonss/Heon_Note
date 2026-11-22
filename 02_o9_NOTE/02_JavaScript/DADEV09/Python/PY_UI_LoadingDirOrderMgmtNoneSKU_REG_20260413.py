"""
* 프로그램명
    - PY_UI_LoadingDirOrderMgmtNoneSKU_REG

* 내용
    -
* 변경이력
    - 2025.03.28 / Miss Lee / Create

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_LD, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
    - in_LoadingDirOrderMgmt :
        Select (
                  [Version].[Version Name]
                * [Sub Location].[Sub Location]
                * [Seq].[Seq]
                * [Item].[Item]
                * [Item].[Product Group]
                * [Item].[Product]
                * [Item].[Project]
                * [Location].[Location]
                * [Sales Domain].[Ship To]
                * [Time].[Week] ) on row,
                ({
                   Measure.[Loading Dir Order Cal Master_1st Mix]
                 , Measure.[Loading Dir Order Cal Master_2nd Mix]
                 , Measure.[Loading Dir Order Cal Master_3rd Mix]
                 , Measure.[Loading Dir Order Cal Master_Item Depth]
                 , Measure.[Loading Dir Order Cal Master_Item Height]
                 , Measure.[Loading Dir Order Cal Master_Item Mix Group]
                 , Measure.[Loading Dir Order Cal Master_Item Width]
                 , Measure.[Loading Dir Order Cal Master_JIG]
                 , Measure.[Loading Dir Order Cal Master_JIG Line]
                 , Measure.[Loading Dir Order Cal Master_Line]
                 , Measure.[Loading Dir Order Cal Master_Max Load Qty]
                 , Measure.[Loading Dir Order Cal Master_Min Qty]
                 , Measure.[Loading Dir Order Cal Master_Mix Cut Add]
                 , Measure.[Loading Dir Order Cal Master_Mix FR Type]
                 , Measure.[Loading Dir Order Cal Master_Mix Max FR]
                 , Measure.[Loading Dir Order Cal Master_Mix Max FTL]
                 , Measure.[Loading Dir Order Cal Master_Mix Min FR]
                 , Measure.[Loading Dir Order Cal Master_Mix Min FTL]
                 , Measure.[Loading Dir Order Cal Master_Multiple]
                 , Measure.[Loading Dir Order Cal Master_Profit Grade]
                 , Measure.[Loading Dir Order Cal Master_Profit Grade Priority]
                 , Measure.[Loading Dir Order Cal Master_SKU Per Cntr]
                 , Measure.[Loading Dir Order Cal Master_Single Cut Add]
                 , Measure.[Loading Dir Order Cal Master_Single FR Type]
                 , Measure.[Loading Dir Order Cal Master_Single Max FR]
                 , Measure.[Loading Dir Order Cal Master_Single Max FTL]
                 , Measure.[Loading Dir Order Cal Master_Single Min FR]
                 , Measure.[Loading Dir Order Cal Master_Single Min FTL]
                 , Measure.[Loading Dir Order Mgmt_Adj Prod Week]
                 , Measure.[Loading Dir Order Mgmt_CNTR FR]
                 , Measure.[Loading Dir Order Mgmt_Chk Flag]
                 , Measure.[Loading Dir Order Mgmt_Chk Qty]
                 , Measure.[Loading Dir Order Mgmt_Cntr Type]
                 , Measure.[Loading Dir Order Mgmt_Created By]
                 , Measure.[Loading Dir Order Mgmt_Creation Time]
                 , Measure.[Loading Dir Order Mgmt_Item FR]
                 , Measure.[Loading Dir Order Mgmt_Loading Master Match]
                 , Measure.[Loading Dir Order Mgmt_Loading Master Match Chk]
                 , Measure.[Loading Dir Order Mgmt_Loading Method Match]
                 , Measure.[Loading Dir Order Mgmt_Loading Method Match Chk]
                 , Measure.[Loading Dir Order Mgmt_Loading Qty]
                 , Measure.[Loading Dir Order Mgmt_Loading Status]
                 , Measure.[Loading Dir Order Mgmt_Loading Type]
                 , Measure.[Loading Dir Order Mgmt_Origin Qty]
                 , Measure.[Loading Dir Order Mgmt_SO Item]
                 , Measure.[Loading Dir Order Mgmt_Sales Order]
                 , Measure.[Loading Dir Order Mgmt_Ship To]
                 , Measure.[Loading Dir Order Mgmt_Ship To Name]
                 , Measure.[Loading Dir Order Mgmt_Simulated By]
                 , Measure.[Loading Dir Order Mgmt_Simulation Time]
                 , Measure.[Loading Dir Order Mgmt_UnAssinged Qty]
                 , Measure.[Loading Dir Order Mgmt_Update Time]
                 , Measure.[Loading Dir Order Mgmt_Updated By]
                 , Measure.[Loading Dir Order Mgmt_Valid Fail Reason]
        }) on column
       include memberproperties
              { [Sub Location].[Sub Location], [$DisplayName] }
              { [Location].[Location], [DisplayName], [Shipment Type] }
              { [Sales Domain].[Ship To], [DisplayName] }
              ;

    - in_Container :
        Select ([Container].[ContainerID]) on row
        include memberproperties {[Container].[ContainerID],
                                  [Container Length],
                                  [Container Height],
                                  [Container Width]};

* Output Tables
    - out_LoadingDirOrderMgmt:
        Select ([Version].[Version Name]
             * [Sub Location].[Sub Location]
             * [Seq].[Seq]
             * [Item].[Item]
             * [Location].[Location]
             * [Sales Domain].[Ship To]
             * [Time].[Week] ) on row
             , ({Measure.[Loading Dir Order Mgmt_Adj Prod Week]
             , Measure.[Loading Dir Order Mgmt_Chk Flag]
             , Measure.[Loading Dir Order Mgmt_Chk Qty]
             , Measure.[Loading Dir Order Mgmt_Cntr Type]
             , Measure.[Loading Dir Order Mgmt_Loading Master Match]
             , Measure.[Loading Dir Order Mgmt_Loading Master Match Chk]
             , Measure.[Loading Dir Order Mgmt_Loading Method Match]
             , Measure.[Loading Dir Order Mgmt_Loading Method Match Chk]
             , Measure.[Loading Dir Order Mgmt_Loading Qty]
             , Measure.[Loading Dir Order Mgmt_Loading Status]
             , Measure.[Loading Dir Order Mgmt_Loading Type]
             , Measure.[Loading Dir Order Mgmt_Origin Qty]
             , Measure.[Loading Dir Order Mgmt_SO Item]
             , Measure.[Loading Dir Order Mgmt_Sales Order]
             , Measure.[Loading Dir Order Mgmt_Ship To]
             , Measure.[Loading Dir Order Mgmt_Ship To Name]
             , Measure.[Loading Dir Order Mgmt_UnAssinged Qty]
             , Measure.[Loading Dir Order Mgmt_Valid Fail Reason]
             , Measure.[Loading Dir Order Mgmt_Simulated By]
             , Measure.[Loading Dir Order Mgmt_Simulation Time]
             }) on column
        ;

    - out_LoadingDirOrderMgmtAggr
        Select ([Version].[Version Name]
             * [Sub Location].[Sub Location]
             * [Seq].[Seq]
             * [Item].[Item]
             * [Location].[Location]
             * [Sales Domain].[Ship To]
             * [Time].[Week]) on row
             ,({Measure.[Loading Dir Order Mgmt Aggr_1st Mix Aggr FR]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix Aggr Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix Cntr Per SKU]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix FTL Chk FR]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix FTL Cntr]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix FTL Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix Group]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix Group FTL Chk]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix Mod FR]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix Quotient]
             , Measure.[Loading Dir Order Mgmt Aggr_1st Mix Rest FR]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Aggr FR]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Aggr Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Cntr Per SKU]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix FTL Chk FR]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix FTL Cntr]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix FTL Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Group]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Group FTL Chk]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Mod FR]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Quotient]
             , Measure.[Loading Dir Order Mgmt Aggr_2nd Mix Rest FR]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Aggr FR]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Aggr Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Cntr Per SKU]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix FTL Chk FR]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix FTL Cntr]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix FTL Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Group]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Group FTL Chk]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Mod FR]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Quotient]
             , Measure.[Loading Dir Order Mgmt Aggr_3rd Mix Rest FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Add Cnt]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Add Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Cut Add]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Cut Cnt]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Cut Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Diff Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust FTL Cntr]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust LTL Group]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust LTL Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust LTL Sum FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Loading Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Loading Qty FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Loading Qty Sum FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust MOD]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust MOD FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Multiple]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Option1]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Option2]
             , Measure.[Loading Dir Order Mgmt Aggr_Adjust Sum FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Aggr Chk Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Cntr Type]
             , Measure.[Loading Dir Order Mgmt Aggr_Diff]
             , Measure.[Loading Dir Order Mgmt Aggr_Last LTL Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Last Loading Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Last Mix Group]
             , Measure.[Loading Dir Order Mgmt Aggr_Loading Type]
             , Measure.[Loading Dir Order Mgmt Aggr_Mixed Item Cntr FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Mixed Item Cntr Status]
             , Measure.[Loading Dir Order Mgmt Aggr_Mixed Item FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Mixed Item Loading Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_SKU Constraints]
             , Measure.[Loading Dir Order Mgmt Aggr_Ship To]
             , Measure.[Loading Dir Order Mgmt Aggr_Ship To Name]
             , Measure.[Loading Dir Order Mgmt Aggr_Simulated By]
             , Measure.[Loading Dir Order Mgmt Aggr_Simulation Time]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item Cntr Status]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item Complete Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item FTL Count]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item Mod FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item Quotient]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item Rest FR]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item Rest Qty]
             , Measure.[Loading Dir Order Mgmt Aggr_Single Item SKU Count]
             , Measure.[Loading Dir Order Cal Aggr_1st Mix]
             , Measure.[Loading Dir Order Cal Aggr_2nd Mix]
             , Measure.[Loading Dir Order Cal Aggr_3rd Mix]
             , Measure.[Loading Dir Order Cal Aggr_Item Depth]
             , Measure.[Loading Dir Order Cal Aggr_Item Height]
             , Measure.[Loading Dir Order Cal Aggr_Item Mix Group]
             , Measure.[Loading Dir Order Cal Aggr_Item Width]
             , Measure.[Loading Dir Order Cal Aggr_JIG]
             , Measure.[Loading Dir Order Cal Aggr_JIG Line]
             , Measure.[Loading Dir Order Cal Aggr_Line]
             , Measure.[Loading Dir Order Cal Aggr_Max Load Qty]
             , Measure.[Loading Dir Order Cal Aggr_Min Qty]
             , Measure.[Loading Dir Order Cal Aggr_Mix Cut Add]
             , Measure.[Loading Dir Order Cal Aggr_Mix FR Type]
             , Measure.[Loading Dir Order Cal Aggr_Mix Max FR]
             , Measure.[Loading Dir Order Cal Aggr_Mix Min FR]
             , Measure.[Loading Dir Order Cal Aggr_Multiple]
             , Measure.[Loading Dir Order Cal Aggr_Profit Grade]
             , Measure.[Loading Dir Order Cal Aggr_Profit Grade Priority]
             , Measure.[Loading Dir Order Cal Aggr_SKU Per Cntr]
             , Measure.[Loading Dir Order Cal Aggr_Single Cut Add]
             , Measure.[Loading Dir Order Cal Aggr_Single FR Type]
             , Measure.[Loading Dir Order Cal Aggr_Single Max FR]
             , Measure.[Loading Dir Order Cal Aggr_Single Max FTL]
             , Measure.[Loading Dir Order Cal Aggr_Single Min FR]
             , Measure.[Loading Dir Order Cal Aggr_Single Min FTL]
               }) on column
        ;

    - out_ContainerPlan
        Select (Version.[Version Name]
             * Sub Location.[Sub Location]
             * Location.[Location]
             * Sales Domain.[Ship To]
             * Seq.[Seq]
             * Time.[Week]
             * Item.[Item]) on row
             , ({Measure.[Loading Dir Container Plan_Ship To]
             , Measure.[Loading Dir Container Plan_Loading Status]
             , Measure.[Loading Dir Container Plan_Remark]
             . Measure.[Loading Dir Container Plan_Loading Qty]
             , Measuer.[Loading Dir Container Plan_Group Id]
             , Measure.[Loading Dir Container Plan_Cntr No]}) on column
        ;

* Flow Summary
        STEP 0. Aggregation
        STEP 1. Mgmt, Cal, Container input을 Merge한다.
        STEP 2. Single Loading 시뮬레이션 계산한다.
        STEP 3. Mix Loading 계산한다.
        STEP 4. Mix 최종 칼럼 계산한다.
        STEP 5. Adjust
        STEP 6. Container Planning
        STEP 7. Assign the loading qty to the order.
        STEP 8. Mgmt 메저그룹 칼럼 원복

* Validation :


* Execution :
    1. 기존 메저 데이터 삭제(nullify)
        delete data for model [Mix Load Master]
            where { [Version].[Version Name].[CWV_LD] }

    2. Plugin Call하여 신규 MG 생성
    1) LightWeight
    EXEC plugin instance [PY_UI_LoadingDirOrderMgmtNoneSKU_REG]
        for measures { [Loading Dir Order Mgmt_Simulated By] }
           using scope ([Version].[Version Name].[${params.fb_Version}])
           using arguments {(ExecutionMode, "LightWeight")
                         , (Param_OUT_VERSION, "${params.fb_Version}")
                         , (Param_SKU_Constraints, "${params.fb_SKU_Constraints}")
                         , (Param_Adjust_Option1, "${params.fb_Adjust_Option1}")
                         , (Param_Adjust_Option2 , "${params.fb_Adjust_Option2}")
                         , (Param_User_Name , "${params.fb_User_Name}")
                         , (MaxSliceTableCells, 200000000)
                         , (MaxConcurrency, 1 )
                         , (IncludeNullRows, False)
                         , ([Param.o9_sys_log_level], "DEBUG")
                         }
    ;

    2) MediumWeight
    EXEC plugin instance [PY_UI_LoadingDirOrderMgmtNoneSKU_REG]
        for measures { [Loading Dir Order Mgmt_Simulated By] }
           using scope ([Version].[Version Name].[${params.fb_Version}])
           using arguments {(ExecutionMode, "MediumWeight")
                         , (Param_OUT_VERSION, "${params.fb_Version}")
                         , (Param_SKU_Constraints, "${params.fb_SKU_Constraints}")
                         , (Param_Adjust_Option1, "${params.fb_Adjust_Option1}")
                         , (Param_Adjust_Option2 , "${params.fb_Adjust_Option2}")
                         , (Param_User_Name , "${params.fb_User_Name}")
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
import datetime
from NSCMCommon import NSCMCommon as common
from decimal import Decimal

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_LoadingDirOrderMgmtNoneSKU_REG"
str_input_dir = "Input/UILoadingDirOrderMgmtNoneSKUREG"
str_output_dir = "Output/UILoadingDirOrderMgmtNoneSKUREG"
is_local = common.gfn_get_isLocal()
is_print = True
flag_csv = True
flag_exception = True

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 400)

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
            df_p_source.to_csv(str_output_dir + "/" + str_p_source_name + ".csv", encoding="UTF8", index=False)
    else:
        # 최종 Output 테이블인 경우에는 무조건 로그 출력
        if is_output:
            logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
            if is_local and not df_p_source.empty:
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
def fn_preprocess(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        1.내가 체크한 항목에 대한 input 대상 추출
        2.메저 그룹 내 메저명 _기준으로 뒷 부분만 남기기
    :param df_p_source: in_LoadingDirOrder
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 대상건 추출 : Simulated By == session 사용자
    # list_where = df_p_source['Loading Dir Order Mgmt_Simulated By'] == Param_User_Id
    # df_p_source = df_p_source[list_where]
    # 대상건 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    df_return = df_return.rename(columns={
        'Location.[Location]': 'To Site',
        'Sub Location.[Sub Location]': 'Location.[Location]',
        'Sales Domain.[Ship To]': 'Account',
        'Time.[Week]': 'Org_Time.[Week]',
        'Item.[Item]': 'Item',
        'Item.[Product Group]': 'Product Group',
        'Item.[Product]': 'Product',
        'Item.[Project]': 'Project',
        'Location.[Shipment Type]': 'Shipment Type',
        'Loading Dir Order Mgmt_Adj Prod Week': 'Time.[Week]'
    })

    # 칼럼 prefix 없애기
    str_pre_fix_mgmt = "Loading Dir Order Mgmt_"
    str_pre_fix_cal = 'Loading Dir Order Cal Master_'

    # 칼럼 str_pre_fix 를 다 없애고
    list_columns = df_return.columns
    list_columns_new = []
    for col in list_columns:
        new_col = col.replace(str_pre_fix_mgmt, "").replace(str_pre_fix_cal, "")
        list_columns_new.append(new_col)
    df_return.columns = list_columns_new

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return[['Item Width', 'Item Depth', 'Max Load Qty']] = (
        df_return[['Item Width', 'Item Depth', 'Max Load Qty']].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(
            float)
    )

    # Aggr Grouping  Key 생성
    str_grouping_key = (
            df_return['Time.[Week]'].astype(str) + "_" +
            df_return['Location.[Location]'].astype(str) + "_" +
            df_return['To Site'].astype(str) + "_" +
            df_return['Account'].astype(str) + "_" +
            df_return['Ship To'].astype(str) + "_" +
            df_return['Item'].astype(str) + "_" +
            df_return['Loading Type'].astype(str) + "_" +
            df_return['Cntr Type'].astype(str)
    )
    df_return['Aggr Grouping Key'] = str_grouping_key

    # 결과 리턴
    return df_return


@_decoration_
def fn_aggregation(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 0. Prod Week-From Site-To Site-Account-Ship To-Item을 기준으로 Aggregation
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

    # Prod Week-From Site-To Site-Account-Ship To-Item을 기준으로 Aggregation Key 생성
    # Chk Qty는 sum으로 나머지 컬럼은 모두 first로 group by
    agg_funcs = \
        {col: 'sum' if col == 'Chk Qty' else 'first' for col in df_p_source.columns if col != 'Aggr Grouping Key'}

    df_return = df_p_source.groupby(by='Aggr Grouping Key').agg(agg_funcs).reset_index()

    return df_return


@_decoration_
def fn_mgmt_merge_cal(df_p_source: pd.DataFrame, df_in_container: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 1. Mgmt, Cal, Container input을 Merge한다.
            1. df_in_LoadingDirOrderMgmt, in_Container merge한다.
            2. FR Type 별 ML Qty/ LDM Qty 계산을 위해 필요 칼럼 생성한다.
                - Use Single Max Load Qty, Use Mix Max Load Qty
    :param df_in_container: in_Container
    :param df_p_source: df_in_LoadingDirOrderMgmt
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

    # Merge Key
    df_return = pd.merge(
        df_p_source, df_in_container, how='left', left_on=['Cntr Type'], right_on=['Container.[ContainerID]']
    )

    # Single FR Type, Mix FR Type 에 따른 M/L QTY 사용칼럼 변경
    # LDM일 경우 LDM_QTY( M/L QTY 대신, LDM QTY 사용)
    list_where_side = df_return['Loading Type'] == 'SIDE'
    list_where_front = df_return['Loading Type'] == 'FRONT'

    df_return.loc[list_where_side, 'LDM Qty'] = np.where(
        df_return[list_where_side]['Item Width'] == 0,
        0,
        (df_return[list_where_side]['Multiple'] * df_return[list_where_side]['Container.[Container Length]'])
        / df_return[list_where_side]['Item Width']
    )

    df_return.loc[list_where_front, 'LDM Qty'] = np.where(
        df_return[list_where_front]['Item Depth'] == 0,
        0,
        (df_return[list_where_front]['Multiple'] * df_return[list_where_front]['Container.[Container Length]'])
        / df_return[list_where_front]['Item Depth']
    )

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return['LDM Qty'] = df_return['LDM Qty'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)

    # 1) Use Single Max Load Qty 칼럼 생성 : Single FR Type에 따라 M/L Qty, LDM Qty 구분 사용
    df_return['Use Single Max Load Qty'] = np.where(
        df_return['Single FR Type'] == 'LDM',
        df_return['LDM Qty'],
        df_return['Max Load Qty']
    )

    # 2) Use Mix Max Load Qty 칼럼 생성 : Mix FR Type에 따라 M/L Qty, LDM Qty 구분 사용
    df_return['Use Mix Max Load Qty'] = np.where(
        df_return['Mix FR Type'] == 'LDM',
        df_return['LDM Qty'],
        df_return['Max Load Qty']
    )

    return df_return


@_decoration_
def fn_mgmt_calculate_single_item(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 2. single 계산
    :param df_p_source: df_mgmtCal_Merged
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

    # 데이터 복사
    df_return = df_p_source.copy(deep=True)

    # F/R 계산 Logic - Singe Item F/R Type 고려하여 F/R 계산
    # 1. M/L Qty : "Qty" ÷ "Loading Type 별 M/L Qty 값"
    # 2. LDM - Side: ["Qty" ÷ Multiple] * Width / [CNTR type 별 길이 (CNTR Dept)]
    # 3. LDM - Front: ["Qty" ÷ Multiple] * Depth / [CNTR type 별 길이 (CNTR Dept)]

    df_return['Single Item FR'] = np.where(
        df_return['Use Single Max Load Qty'] == 0,
        0,
        df_return['Chk Qty'] / df_return['Use Single Max Load Qty']
    )

    # 2) Single Item Quotient
    df_return['Single Item Quotient'] = np.where(
        df_return['Use Single Max Load Qty'] == 0,
        0,
        df_return['Chk Qty'] // df_return['Use Single Max Load Qty']
    )

    # 3) Single Item Mod FR
    df_return['Single Item Mod FR'] = df_return['Single Item FR'] - df_return['Single Item Quotient']

    # 4) Single Item FTL Count
    df_return['Single Item FTL Count'] = np.where(
        df_return['Single Item Mod FR'] > df_return['Single Min FR'],
        df_return['Single Item Quotient'] + 1,
        df_return['Single Item Quotient']
    )

    # 5) Single Item Cntr Status 계산
    df_return['Single Item Cntr Status'] = np.where(
        (df_return['Use Single Max Load Qty'] != 0) & (
                (df_return['Single Item Mod FR'] == 0) | (
                (df_return['Single Min FR'] <= df_return['Single Item Mod FR'])
                & (df_return['Single Item Mod FR'] <= df_return['Single Max FR'])
        )
        ),
        'Single Item FTL',
        'LTL'
    )

    # 최종 status에 넣기.
    df_return['Mixed Item Cntr Status'] = df_return['Single Item Cntr Status']

    # 6) Single Item Complete Qty
    df_return['Single Item Complete Qty'] = np.where(
        df_return['Single Item Cntr Status'] == 'Single Item FTL',
        df_return['Chk Qty'],
        df_return['Use Single Max Load Qty'] * df_return['Single Item FTL Count']
    )

    # 7) Single Item Rest Qty
    df_return['Single Item Rest Qty'] = np.where(
        df_return['Single Item Cntr Status'] == 'Single Item FTL',
        0,
        df_return['Chk Qty'] - df_return['Use Single Max Load Qty'] * df_return['Single Item FTL Count']
    )

    # 8) Single Item Rest FR
    df_return['Single Item Rest FR'] = np.where(
        df_return['Use Single Max Load Qty'] == 0,
        0,
        df_return['Single Item Rest Qty'] / df_return['Use Single Max Load Qty']
    )

    # 9) Single Item SKU Count ( default 1 )
    df_return['Single Item SKU Count'] = df_return['SKU Per Cntr']

    return df_return


@_decoration_
def fn_mgmt_calculate_mix_item(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    STEP 3. Mix 계산.
    :param str_p_cond: '1' - '1st' , '2' - '2nd' , '3' - '3rd'
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

    # 데이터 복사
    df_return = df_p_source.copy(deep=True)

    dict_col = {
        '1': '1st',
        '2': '2nd',
        '3': '3rd'
    }
    str_col_measure = dict_col[str_p_cond] + ' Mix'

    # 대상건 : Mix 타입이 None이 아니고, LTL인 ROW 만 대상
    list_where = (df_return[str_col_measure] != 'None') & (df_p_source['Mixed Item Cntr Status'] == 'LTL')

    # 발췌 대상건에 대해서만 계산.
    df_return_not_target = df_return[~list_where]
    df_return = df_return[list_where]

    # Group Key 구분
    # 1) M/L Qty, PJT, P/G, All Remain
    list_conditions = [
        df_return[str_col_measure] == 'M/L Qty',
        df_return[str_col_measure] == 'PJT',
        df_return[str_col_measure] == 'P/G',
        df_return[str_col_measure] == 'All Remain'
    ]

    list_choice = [
        df_return['Max Load Qty'].astype(dtype='int64').astype(str),
        df_return['Project'],
        df_return['Product Group'],
        'All Remain'
    ]

    # Mix Group Base Key
    # Adj Prod Week /FROM /To /Account /Ship To/ Shipment Type/ Cntr Type/ Loading Type / method Key / JigLine_YN
    # 2025015_P410_0003185680_DIR_40FT_FRONT_N
    # 2025015_P410_0003185680_DIR_20FT_FRONT_60_N
    df_return['Shipment Type Flag'] = np.where(df_return['Shipment Type'] == 'DIR', 'N', 'Y')
    df_return['Mix Group Base Grouping Key'] = (
            df_return['Time.[Week]'].astype(str)
            + '_'
            + df_return['Location.[Location]']
            + '_'
            + df_return['To Site']
            + '_'
            + df_return['Account'].astype(str)
            + '_'
            + df_return['Ship To'].astype(str)
            + '_'
            + df_return['Shipment Type']
            + '_'
            + df_return['Cntr Type']
            + '_'
            + df_return['Loading Type']
            + '_'
            + np.select(list_conditions, list_choice, default='None')
            + '_'
            + df_return['Shipment Type Flag']
    )

    # Group Key 구분
    # 2) Item Mix Group 의 경우 KEY 설정
    list_where = df_return[str_col_measure] == 'Item Mix Group'
    df_return.loc[list_where, 'Mix Group Base Grouping Key'] = (
            df_return['Time.[Week]'].astype(str)
            + '_'
            + df_return['Item Mix Group']
            + '_'
            + df_return['Shipment Type Flag']
    )

    # 1) All Remain 의 경우엔 2025015_P410_0003185680_N 로 표기
    # 2) ship to가 -로 들어오거나 null인 경우 _로 표기
    df_return['Mix Group Base Grouping Key'] = (
        df_return['Mix Group Base Grouping Key']
        .str.replace('_All Remain', '')
        .str.replace('_-_', '_')
        .str.replace('__', '_')
    )

    # 칼럼 생성
    # Last Mix Group
    df_return['Last Mix Group'] = df_return['Mix Group Base Grouping Key']

    # Single Item FTL Count Aggr ( assign 시에 필요 )
    df_return['Single Item FTL Count Aggr'] = (
        df_return.groupby('Mix Group Base Grouping Key')['Single Item FTL Count'].transform('sum')
    )

    # 1st Mix Group
    df_return[str_col_measure + ' Group'] = df_return['Last Mix Group']

    # 1st Mix Cntr Per SKU
    df_return[str_col_measure + ' Cntr Per SKU'] = (
        df_return.groupby('Mix Group Base Grouping Key')['SKU Per Cntr'].transform('sum')
    )

    # 1st Mix Aggr Qty
    df_return[str_col_measure + ' Aggr Qty'] = (
        df_return.groupby('Mix Group Base Grouping Key')['Single Item Rest Qty'].transform('sum')
    )

    # 1st Mix Aggr FR ( 각각 ROW별로  SUM(Single Item Rest Qty/ Use Mix Max Load Qty) : ML/LDM QTY 구분)
    df_return['Single Item Rest FR2'] = np.where(
        df_return['Use Mix Max Load Qty'] == 0,
        0,
        df_return['Single Item Rest Qty'] / df_return['Use Mix Max Load Qty']
    )

    df_return[str_col_measure + ' Aggr FR'] = (
        df_return.groupby('Mix Group Base Grouping Key')['Single Item Rest FR2'].transform('sum')
    )

    # 1st Mix Quotient
    df_return[str_col_measure + ' Quotient'] = (
            df_return[str_col_measure + ' Aggr FR'] // 1
    )

    # 1st Mix Mod FR
    df_return[str_col_measure + ' Mod FR'] = (
            df_return[str_col_measure + ' Aggr FR'] - df_return[str_col_measure + ' Quotient']
    )

    # 1st Mix FTL Chk FR
    df_return[str_col_measure + ' FTL Chk FR'] = np.where(
        df_return[str_col_measure + ' Quotient'] == 0,
        df_return[str_col_measure + ' Mod FR'],
        df_return[str_col_measure + ' Mod FR'] + 1
    )

    # 1st Mix Group FTL Chk ( FTL/ LTL 판별 )
    df_return[str_col_measure + ' Group FTL Chk'] = np.where(
        df_return['Mix Min FR'] <= df_return[str_col_measure + ' Mod FR'],
        np.where(df_return[str_col_measure + ' Mod FR'] <= df_return['Mix Max FR'],
                 df_return[str_col_measure] + ' FTL',
                 'LTL'),
        np.where(df_return['Mix Min FR'] <= df_return[str_col_measure + ' FTL Chk FR'],
                 np.where(df_return[str_col_measure + ' FTL Chk FR'] <= df_return['Mix Max FR'],
                          df_return[str_col_measure] + ' FTL',
                          'LTL'),
                 'LTL')
    )

    # 1st Mix FTL Qty
    df_return[str_col_measure + ' FTL Qty'] = np.where(
        df_return[str_col_measure + ' Group FTL Chk'] == 'LTL',
        0,
        df_return[str_col_measure + ' Aggr Qty']
    )

    # 1st Mix FTL Cntr
    df_return[str_col_measure + ' FTL Cntr'] = np.where(
        df_return[str_col_measure + ' Group FTL Chk'] == 'LTL',
        0,
        np.where(df_return[str_col_measure + ' Mod FR'] > df_return['Mix Min FR'],
                 df_return[str_col_measure + ' Quotient'] + 1,
                 df_return[str_col_measure + ' Quotient']
                 )
    )

    # 1st Mix Rest FR
    df_return[str_col_measure + ' Rest FR'] = np.where(
        df_return[str_col_measure + ' Group FTL Chk'] == 'LTL',
        df_return[str_col_measure + ' Aggr FR'],
        0
    )

    # 최종 결과 칼럼들 정리

    # Mixed Item Cntr Status
    df_return['Mixed Item Cntr Status'] = df_return[str_col_measure + ' Group FTL Chk']

    # Mixed Item FR
    df_return['Mixed Item FR'] = df_return['Single Item Rest FR']

    # Mixed Item Cntr FR
    df_return['Mixed Item Cntr FR'] = df_return[str_col_measure + ' Aggr FR']

    # return concat
    df_return = pd.concat([df_return_not_target, df_return], ignore_index=True)

    return df_return


@_decoration_
def fn_mixed_correct_multiple(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        Mixed FTL의 경우 Multiple 의 값으로 아래 항목 보정 및 칼럼 정리한다.
        -  Mixed Item Loading Qty, Diff, Last Loading Qty, Mixed Item FR, Mixed Item Cntr FR, Last LTL Qty
    :param df_p_source: df_mgmtCal_mixItem_step_three
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

    # 데이터 복사
    df_return = df_p_source.copy(deep=True)

    # Mixed FTL의 경우 Mixed Item Loading Qty를 multiple로 보정
    # Mixed Item FR, Mixed Item Cntr FR,  Diff, Last Loading Qty 재계산

    # Mixed Item Loading Qty
    df_return['Mixed Item Loading Qty'] = np.where(
        df_return['Mixed Item Cntr Status'] != 'LTL',
        df_return['Single Item Rest Qty'],
        0
    )

    # 대상 추출 (Mixed FTL)
    list_where = df_return['Mixed Item Cntr Status'].isin(['Single Item FTL', 'LTL'])
    df_return_not_target = df_return[list_where]
    df_return_target = df_return[~list_where].copy(deep=True)

    # Mixed FTL 대상이 있는 경우 에만 실행
    if len(df_return_target) > 0:
        # Adj Qty
        df_return_target['Adj Qty'] = df_return_target.apply(
            lambda row: int(common.gfn_get_round(row['Mixed Item Loading Qty'] / row['Multiple'], 0)) * row['Multiple'],
            axis=1
        )

        # Adj FR
        df_return_target['Adj FR'] = np.where(
            df_return_target['Use Mix Max Load Qty'] == 0,
            0,
            df_return_target['Adj Qty'] / df_return_target['Use Mix Max Load Qty']
        )

        # Adj Aggr FR
        df_return_target['Adj Aggr FR'] = (
            df_return_target.groupby('Mix Group Base Grouping Key')['Adj FR'].transform('sum')
        )

        # Adj Quotient
        df_return_target['Adj Quotient'] = df_return_target['Adj Aggr FR'] // 1

        # Adj Mod FR
        df_return_target['Adj Mod FR'] = df_return_target['Adj Aggr FR'] - df_return_target['Adj Quotient']

        # Adj FTL Chk FR
        df_return_target['Adj FTL Chk FR'] = np.where(
            df_return_target['Adj Quotient'] == 0,
            df_return_target['Adj Mod FR'],
            df_return_target['Adj Mod FR'] + 1
        )

        # Adj Max FTL Chk (FTL 판별)
        df_return_target['Adj Max FTL Chk'] = np.where(
            df_return_target['Mix Min FR'] <= df_return_target['Adj Mod FR'],
            np.where(df_return_target['Adj Mod FR'] <= df_return_target['Mix Max FR'], 'Y', 'N'),
            np.where(df_return_target['Mix Min FR'] <= df_return_target['Adj FTL Chk FR'],
                     np.where(df_return_target['Adj FTL Chk FR'] <= df_return_target['Mix Max FR'], 'Y', 'N'),
                     'N'
                     )
        )

        # FTL → LTL Cut/Add 대상
        list_where = df_return_target['Adj Max FTL Chk'] == 'Y'
        df_return_target_ftl = df_return_target[list_where]
        df_return_target_ltl = df_return_target[~list_where].copy(deep=True)

        # CUT/ADD 여부 확인( 기존 Aggr FR('Mixed Item Cntr FR') 보다 커졌으면 CUT 아니면 ADD )
        df_return_target_ltl['Mixed FTL Adj Cut Add'] = np.where(
            df_return_target_ltl['Adj Aggr FR'] > df_return_target_ltl['Mixed Item Cntr FR'], 'CUT', 'ADD'
        )

        # LTL Cut/Add 대상에 대해 Adj Qty 다시 계산
        df_return_target_ltl = (
            df_return_target_ltl.groupby('Mix Group Base Grouping Key').apply(fn_adjust_mixed_ftl).reset_index(
                drop=True)
        )

        # Concat
        df_return_target = pd.concat([df_return_target_ftl, df_return_target_ltl])

        # 기존 Mixed FTL 건에 대해 1), 2) 작업 후 보정 값으로 최종  Mixed Item Loading Qty 반영
        # 1) Mixed FTL Multiple 보정
        # 2) 1)이후 LTL이 된 group에 대해 cut/add 작업으로 Multiple 보정
        df_return_target['Mixed Item Loading Qty'] = df_return_target['Adj Qty']

        # Concat
        df_return = pd.concat([df_return_not_target, df_return_target])

    # Mixed Item FR, Mixed Item Cntr FR,  Diff, Last Loading Qty, Last LTL Qty 정리
    # Mixed Item FR
    df_return['Mixed Item FR'] = np.where(
        df_return['Use Mix Max Load Qty'] == 0,
        0,
        df_return['Mixed Item Loading Qty'] / df_return['Use Mix Max Load Qty']
    )

    # Mixed Item Cntr FR
    df_return['Mixed Item Cntr FR'] = (
        df_return.groupby('Mix Group Base Grouping Key')['Mixed Item FR'].transform('sum')
    )

    # Last Loading Qty
    df_return['Last Loading Qty'] = df_return['Single Item Complete Qty'] + df_return['Mixed Item Loading Qty']

    # Diff
    df_return['Diff'] = df_return['Last Loading Qty'] - df_return['Chk Qty']

    # Last LTL Qty
    df_return['Last LTL Qty'] = np.where(
        df_return['Mixed Item Cntr Status'] == 'LTL',
        df_return['Single Item Rest Qty'],
        0
    )

    return df_return


def fn_adjust_mixed_ftl(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        Mixed FTL 인 건이 Multiple보정 후 LTL로 된 경우,
        Mix Group Base Grouping Key 기준으로 CUT/ADD 작업을 1회 한다.
        Step 1 이후에도 FTL 구성 실패 시 Check Qty (조정 전 값)
    :param df_p_source: df_return_target_ftl grouping된 값
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = df_p_source.copy(deep=True)

    # Cut, Add 기준값
    str_cut_add_flag = df_return['Mixed FTL Adj Cut Add'].iloc[0]

    if str_cut_add_flag == 'CUT':
        # Cut 조정의 경우 Profit Grade의 Priority에 대해 내림차순(순위가 낮은 것부터 조정) 정렬
        df_return.sort_values(by=['Profit Grade Priority'], ascending=False, inplace=True)
    elif str_cut_add_flag == 'ADD':
        # Add 조정의 경우 Profit Grade의 Priority에 대해 올림차순(순위가 높은 것부터 조정) 정렬
        df_return.sort_values(by=['Profit Grade Priority'], ascending=True, inplace=True)
    # Mix 시의 FTL 여부를 판단하기 위한 Fill Rate의 최소 조건
    float_min_fr = df_return['Mix Min FR'].iloc[0]
    # Mix 시의 FTL 여부를 판단하기 위한 Fill Rate의 최대 조건
    float_max_fr = df_return['Mix Max FR'].iloc[0]
    # origin Adj Aggr FR
    float_adj_aggr_fr = df_return['Adj Aggr FR'].iloc[0]
    # 최종 ftl 여부
    ftl_final_flag = False

    for i, row in df_return.iterrows():
        # origin Adj FR
        float_adj_fr = row['Adj FR']

        if str_cut_add_flag == 'CUT':
            df_return.loc[i, 'Adj Qty'] = row['Adj Qty'] - row['Multiple']
        else:
            df_return.loc[i, 'Adj Qty'] = row['Adj Qty'] + row['Multiple']

        # Item FR, Cntr FR 재계산
        df_return.loc[i, 'Adj FR'] = np.where(
            row['Use Mix Max Load Qty'] == 0,
            0,
            df_return.loc[i, 'Adj Qty'] / row['Use Mix Max Load Qty']
        )

        # Adj Aggr FR (재산정)
        float_new_adj_aggr_fr = float_adj_aggr_fr - float_adj_fr + df_return.loc[i, 'Adj FR']

        ################################################################################################################
        # 현재의 SUM(F/R)이 FTL인지 확인하기 위해, Sum(Fill Rate)를 1로 나눈 나머지와, 해당 나머지에 1을 더한 값을 구한다.
        float_tmp_sum_fr_min, float_tmp_sum_fr_max = fn_make_temporary_sum(float_new_adj_aggr_fr)
        # FTL 여부에 대한 플래그
        ftl_flag = fn_is_ftl(float_tmp_sum_fr_min, float_tmp_sum_fr_max, float_min_fr, float_max_fr)
        ################################################################################################################

        if ftl_flag:
            ftl_final_flag = True
            break
        else:
            continue

    # Step 1 이후에도 FTL 구성 실패 시 Check Qty (조정 전 값 : Mixed Item Loading Qty)
    if not ftl_final_flag:
        df_return['Adj Qty'] = df_return['Mixed Item Loading Qty']

    return df_return


def fn_make_temporary_sum(org_num: float) -> tuple:
    """
    현재의 SUM(F/R)이 FTL인지 확인하기 위해, Sum(Fill Rate)를 1로 나눈 나머지와, 해당 나머지에 1을 더한 값을 구한다.
    :param org_num: Adjust Loading Qty Sum FR
    :return: Sum(Fill Rate)를 1로 나눈 나머지, 해당 나머지에 1을 더한 값
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    float_return_min = 0.0
    float_return_max = 0.0

    if org_num > 1:
        float_return_min = org_num % 1
        float_return_max = float_return_min + 1
    else:
        float_return_min = org_num

    return float_return_min, float_return_max


def fn_is_ftl(float_p_sum_fr_min: float, float_p_sum_fr_max: float, float_p_min: float, float_p_max: float) -> bool:
    """
    Sum(Fill Rate)를 1로 나눈 나머지 값이 FTL 기준을 만족하는 경우 True 리턴
    Sum(Fill Rate)를 1로 나눈 나머지 값이 FTL 최소 기준보다 적고,
    Sum(Fill Rate)를 1로 나눈 나머지에 1을 더한 값이 FTL 기준을 만족하는 경우 True 리턴
    :param float_p_sum_fr_min: Sum(Fill Rate)를 1로 나눈 나머지 값(ex : 199%(1.99) -> 99%(0.99), 299%(2.99) - 99%(0.99))
    :param float_p_sum_fr_max: Sum(Fill Rate)를 1로 나눈 나머지 값에 1을 더한 값(ex : 1%(0.01), -> 101%(1.01), 201)
    :param float_p_min:
    :param float_p_max:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    bool_return = False

    if float_p_min <= float_p_sum_fr_min <= float_p_max:
        # 100% 미만(소수점 뒤만 차용)으로 환산 후이면서 FTL인 경우
        # ex : 299% : 2.99 -> 99% : 0.99
        bool_return = True
    elif (float_p_sum_fr_min < float_p_min) and (float_p_min <= float_p_sum_fr_max <= float_p_max):
        # 100% 미만(소수점 뒤만 차용)으로 환산 후 FTL이 아닌 경우, 100을 더한 후(소수에 1을 더한 후) FLT인 경우
        # ex : 1% : 0.01, -> 101% : 1.01
        bool_return = True

    return bool_return


def fn_adjust_row(df_p_source: pd.DataFrame, row: any, index: any, str_cut_add_flag: str, int_add_cut_cnt: int) \
        -> pd.DataFrame:
    """
    Row별로 Adjust 값 처리
    :param df_p_source: 전체 DF
    :param row: 처리 대상 Row
    :param index: 처리 대상 Row의 index
    :param str_cut_add_flag: Adjust 처리 구분(CUT / ADD)
    :param int_add_cut_cnt: Adjust할 수치
    :return: 조정된 데이터프레임
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    df_return = df_p_source.copy(deep=True)
    # ADD인 경우 Add Cnt에 1 증가
    df_return.at[index, 'Adjust Add Cnt'] = np.where(str_cut_add_flag == 'CUT', 0, int_add_cut_cnt)
    # CUT이면서 조정된 Loading Qty가 0 이상이면서 FTL이 아닌 경우이면, Cut Cnt에 1 증가
    df_return.at[index, 'Adjust Cut Cnt'] = np.where(str_cut_add_flag == 'CUT', int_add_cut_cnt, 0)
    # Add Qty = Add Cnt * Multiple
    df_return.at[index, 'Adjust Add Qty'] = df_return.at[index, 'Adjust Add Cnt'] * row['Multiple']
    # Cut Qty = Cut Cnt * Multiple
    df_return.at[index, 'Adjust Cut Qty'] = df_return.at[index, 'Adjust Cut Cnt'] * row['Multiple']
    # Adjust Loading Qty = Adjust Multiple + Adjust Add Qty - Adjust Cut Qty
    df_return.at[index, 'Adjust Loading Qty'] = (
            row['Adjust Multiple'] + df_return.at[index, 'Adjust Add Qty'] -
            df_return.at[index, 'Adjust Cut Qty'])
    # Adjust Loading Qty FR = Adjust Loading Qty / Max Load Qty
    df_return.at[index, 'Adjust Loading Qty FR'] = (
            df_return.at[index, 'Adjust Loading Qty'] / df_return.at[index, 'Max Load Qty'])
    # Adjust Loading Qty Sum FR = SUM(Adjust Loading Qty FR)
    df_return['Adjust Loading Qty Sum FR'] = df_return['Adjust Loading Qty FR'].fillna(0.0).astype(float).sum()

    return df_return


def fn_adjust_rollback(df_p_source: pd.DataFrame, row: any, index: any, str_cut_add_flag: str, int_add_cut_cnt: int) \
        -> pd.DataFrame:
    """
    Row 별로 조정했던 수치를 이전 상태로 복원함.
    :param df_p_source: 전체 DF
    :param row: 처리 대상 Row
    :param index: 처리 대상 Row의 index
    :param str_cut_add_flag: Adjust 처리 구분(CUT / ADD)
    :param int_add_cut_cnt: Adjust했던 수치
    :return: 조정된 데이터프레임
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    df_return = df_p_source.copy(deep=True)
    # ADD인 경우 Add Cnt에 1 증가
    df_return.at[index, 'Adjust Add Cnt'] = np.where(str_cut_add_flag == 'CUT', 0, int_add_cut_cnt - 1)
    # CUT이면서 조정된 Loading Qty가 0 이상이면서 FTL이 아닌 경우이면, Cut Cnt에 1 증가
    df_return.at[index, 'Adjust Cut Cnt'] = np.where(str_cut_add_flag == 'CUT', int_add_cut_cnt - 1, 0)
    # Add Qty = Add Cnt * Multiple
    df_return.at[index, 'Adjust Add Qty'] = df_return.at[index, 'Adjust Add Cnt'] * row['Multiple']
    # Cut Qty = Cut Cnt * Multiple
    df_return.at[index, 'Adjust Cut Qty'] = df_return.at[index, 'Adjust Cut Cnt'] * row['Multiple']
    # Adjust Loading Qty = Adjust Multiple + Adjust Add Qty - Adjust Cut Qty
    df_return.at[index, 'Adjust Loading Qty'] = (
            row['Adjust Multiple'] + df_return.at[index, 'Adjust Add Qty'] -
            df_return.at[index, 'Adjust Cut Qty'])
    # Adjust Loading Qty FR = Adjust Loading Qty / Max Load Qty
    df_return.at[index, 'Adjust Loading Qty FR'] = (
            df_return.at[index, 'Adjust Loading Qty'] / df_return.at[index, 'Max Load Qty'])
    # Adjust Loading Qty Sum FR = SUM(Adjust Loading Qty FR)
    df_return['Adjust Loading Qty Sum FR'] = df_return['Adjust Loading Qty FR'].fillna(0.0).astype(float).sum()

    return df_return


def fn_adjust_by_max_profit(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Option2: Max Profit인 경우의 simulation 처리
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # 현재 그룹에 대한 조정이 Cut인지 Add인지 확인하기 위한 플래그
    str_cut_add_flag = df_return['Adjust Cut Add'].iloc[0]
    # Profit Grade 기준 루프를 만들기 위한 DF
    # Cut 조정 시 각 그룹의 아이템 전체에 대해 균등 조정이 되었는지를 확인하기 위해 Profit Grade 그룹에 대한 사이즈를 추가함.
    df_profit_grade = df_return.groupby(by=['Profit Grade', 'Profit Grade Priority']).size().reset_index(name='Size')
    if str_cut_add_flag == 'CUT':
        # Cut 조정의 경우 Profit Grade의 Priority에 대해 내림차순(순위가 낮은 것부터 조정) 정렬
        df_profit_grade.sort_values(by=['Profit Grade Priority'], ascending=False, inplace=True)
    elif str_cut_add_flag == 'ADD':
        # Add 조정의 경우 Profit Grade의 Priority에 대해 올림차순(순위가 높은 것부터 조정) 정렬
        df_profit_grade.sort_values(by=['Profit Grade Priority'], ascending=True, inplace=True)
    # Mix 시의 FTL 여부를 판단하기 위한 Fill Rate의 최소 조건
    float_min_fr = df_return['Mix Min FR'].iloc[0]
    # Mix 시의 FTL 여부를 판단하기 위한 Fill Rate의 최대 조건
    float_max_fr = df_return['Mix Max FR'].iloc[0]
    # 조정 대상이 되는 Sum(Fill Rate)에 대해 조정 전 값의 몫을 기록하여
    # 조정 시 해당 값의 몫이 달라지는 경우 조정을 종료한다.
    int_add_cut_basis = np.trunc(df_return['Adjust Loading Qty Sum FR'].iloc[0])

    # Profit Grade 기준 루프
    for pgI, pgRow in df_profit_grade.iterrows():
        # 현재 루프 대상인 Profit Grade
        str_profit_grade = pgRow['Profit Grade']
        # Add/Cut 조정 시에 Cnt로 넣어줄 값
        int_add_cut_cnt = 0
        # 전체 조정 대상에 대한 조정이 완료되었는지에 대한 플래그
        complete_flag = False
        # Profit Grade 그룹에 대한 조정이 완료되었는지에 대한 플래그
        grade_break_flag = False
        # 현재 Profit Grade 그룹의 아이템 갯수
        int_grade_group_size = pgRow['Size']
        # 현재 Profit Grade 그룹 조정 후 조정 수치가 0이 된 아이템 갯수
        int_grade_group_zero_count = 0
        while True:
            # Add/Cut 조정 시에 Cnt로 넣어줄 값을 1 증가시킨다.
            int_add_cut_cnt += 1
            # 현재 루프 대상인 Profit Grade에 속한 아이템을 대상으로 조정 루프를 수행한다.
            for index, row in df_return.loc[df_return['Profit Grade'] == str_profit_grade].iterrows():
                # Debug 용 코드
                # if row['Seq.[Seq]'] == 121:
                #     print(f'index:{index}, Grade:{str_profit_grade}')
                # print(f'index:{index}, Grade:{str_profit_grade}, Seq:{row["Seq.[Seq]"]}')
                ########################################################################################################
                # 현재의 SUM(F/R)이 FTL인지 확인하기 위해, Sum(Fill Rate)를 1로 나눈 나머지와, 해당 나머지에 1을 더한 값을 구한다.
                float_tmp_sum_fr_min, float_tmp_sum_fr_max = (
                    fn_make_temporary_sum(df_return.at[index, 'Adjust Loading Qty Sum FR']))
                # 이전 단계 또는 조정 전 단계에서의 FTL 여부에 대한 플래그
                before_ftl_flag = fn_is_ftl(float_tmp_sum_fr_min, float_tmp_sum_fr_max, float_min_fr, float_max_fr)

                ########################################################################################################
                # CUT이면서 현재가 FTL이면 전체 조정 완료
                if str_cut_add_flag == 'CUT':
                    if df_return.at[index, 'Adjust Loading Qty'] <= 0:
                        # CUT이면서 조정된 Loading Qty가 0 이하이면 현재 건은 조정 안 함.
                        continue
                    if Param_Adjust_Option1 == 'MAX' and before_ftl_flag:
                        # adjust option 1이 MAX FTL일 때, 조정이 CUT이면서 FTL이면 전체 조정 완료
                        complete_flag = True
                        break
                elif str_cut_add_flag == 'ADD':
                    if Param_Adjust_Option1 == 'MIN' and before_ftl_flag:
                        # adjust option 1이 MIN FTL일 때, 조정이 ADD이면서 FTL이면 전체 조정 완료
                        complete_flag = True
                        break

                ########################################################################################################
                # 조정
                # Cut 조정 시 조정 후 0이 되는 값을 찾기 위해 조정 전 수치를 기록
                int_before_adjust_qty = df_return.at[index, 'Adjust Loading Qty']
                df_return = fn_adjust_row(df_return, row, index, str_cut_add_flag, int_add_cut_cnt)
                # Cut 조정 시 조정 후 0이 되는 값을 찾기 위해 조정 후 수치를 기록
                int_after_adjust_qty = df_return.at[index, 'Adjust Loading Qty']
                # 조정 전 수치가 조정 후 수치보다 크면서(Cut 조정), 조정 후 수치가 0인 경우
                if (int_before_adjust_qty > int_after_adjust_qty) and (int_after_adjust_qty == 0):
                    # 현재 Profit Grade 그룹의 수치가 0이 된 아이템의 갯수를 1 증가
                    int_grade_group_zero_count += 1
                    if int_grade_group_zero_count == int_grade_group_size:
                        # 현재 Profit Grade 그룹의 수치가 0이 된 아이템의 갯수가 Profit Grade 그룹 전체 아이템 갯수와 동일하면
                        # 현재 Profit Grade 그룹 루프 종료
                        grade_break_flag = True
                        break
                # 조정 후의 Sum(Fill Rate)를 기록
                float_tmp_max_sum_fr = df_return.at[index, 'Adjust Loading Qty Sum FR']

                ########################################################################################################
                # 조정된 수치가 FTL 기준에 부합하는지 확인
                float_tmp_sum_fr_min, float_tmp_sum_fr_max = fn_make_temporary_sum(float_tmp_max_sum_fr)
                ftl_flag = fn_is_ftl(float_tmp_sum_fr_min, float_tmp_sum_fr_max, float_min_fr, float_max_fr)

                # 조정된 SUM(F/R)의 100 단위가 변경되었는지 확인
                # ex add : 150%(1.5) -> 200%(2.0), 95%(0.95) -> 102%(1.02)
                # ex cut : 204%(2.04) -> 199%(1.99), 103%(1.03) -> 99%(0.99)
                if np.trunc(float_tmp_max_sum_fr) != int_add_cut_basis:
                    if ftl_flag:
                        # 조정된 수치가 FTL이면 MAX에 근젒한 값을 찾기 위해 바로 다음 아이템으로 넘어간다.
                        continue
                    else:
                        if before_ftl_flag:
                            # 조정 전에 이미 FTL이면서 CUT인 경우는 위에서 루프를 나가기 때문에 이 곳에서는 ADD인 경우만 들어 옴.
                            if not ftl_flag:
                                # 조정 전에 FTL이었으나 조정 후 FTL이 아니면 조정 수치 복원
                                # 조정된 수치가 Max를 초과했기 때문에 조정된 수치를 이전 수치로 복원함.
                                df_return = fn_adjust_rollback(df_return, row, index, str_cut_add_flag, int_add_cut_cnt)
                                # 현재 그룹에서는 조정이 완료되었기 때문에 조정 종료
                                complete_flag = True
                                break

                # 조정 후 FTL이 아닌 경우
                if not ftl_flag:
                    if before_ftl_flag:
                        # 조정 전에 FTL이었으나 조정 후 FTL이 아니면 조정 수치 복원
                        # 조정된 수치가 Max를 초과했기 때문에 조정된 수치를 이전 수치로 복원함.
                        df_return = fn_adjust_rollback(df_return, row, index, str_cut_add_flag, int_add_cut_cnt)
                        # 현재 그룹에서는 조정이 완료되었기 때문에 조정 종료
                        complete_flag = True
                        break
                    else:
                        # 조정 전이나 조정 후 모두 FTL이 아니기 때문에 다음 아이템으로 넘어 감.
                        continue
            # 조정 종료 또는 현재 Profit Grade 그룹 종료
            if complete_flag or grade_break_flag:
                break
        # 전체 조정 종료
        if complete_flag:
            break

    return df_return


def fn_adjust_by_min_item_change(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Option2: Min Item Change에 대한 Simulation
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 현재 그룹에 대한 조정이 Cut인지 Add인지 확인하기 위한 플래그
    str_cut_add_flag = df_p_source['Adjust Cut Add'].iloc[0]
    if str_cut_add_flag == 'CUT':
        # Cut 조정의 경우 Profit Grade의 Priority에 대해 내림차순(순위가 낮은 것부터 조정) 정렬
        df_return = df_p_source.sort_values(by=['Profit Grade Priority', 'Seq.[Seq]'], ascending=[False, True])
    elif str_cut_add_flag == 'ADD':
        # Add 조정의 경우 Profit Grade의 Priority에 대해 올림차순(순위가 높은 것부터 조정) 정렬
        df_return = df_p_source.sort_values(by=['Profit Grade Priority', 'Seq.[Seq]'], ascending=[True, True])
    # Mix 시의 FTL 여부를 판단하기 위한 Fill Rate의 최소 조건
    float_min_fr = df_return['Mix Min FR'].iloc[0]
    # Mix 시의 FTL 여부를 판단하기 위한 Fill Rate의 최대 조건
    float_max_fr = df_return['Mix Max FR'].iloc[0]
    # 조정 대상이 되는 Sum(Fill Rate)에 대해 조정 전 값의 몫을 기록하여
    # 조정 시 해당 값의 몫이 달라지는 경우 조정을 종료한다.
    int_add_cut_basis = np.trunc(df_return['Adjust Loading Qty Sum FR'].iloc[0])

    # Add/Cut 조정 시에 Cnt로 넣어줄 값
    int_add_cut_cnt = 0
    # 전체 조정 대상에 대한 조정이 완료되었는지에 대한 플래그
    complete_flag = False
    # 조정 대상 아이템 갯수
    int_adjust_size = len(df_return)
    # 조정 후 조정 수치가 0이 된 아이템 갯수
    int_adjust_zero_count = 0
    while True:
        # Add/Cut 조정 시에 Cnt로 넣어줄 값을 1 증가시킨다.
        int_add_cut_cnt += 1
        # 조정 루프
        for index, row in df_return.iterrows():
            # Debug 용 코드
            # if row['Seq.[Seq]'] == 84:
            #     print(f'index:{index}, Seq:{row["Seq.[Seq]"]}')
            # print(f'index:{index}, Seq:{row["Seq.[Seq]"]}')
            ########################################################################################################
            # 현재의 SUM(F/R)이 FTL인지 확인하기 위해, Sum(Fill Rate)를 1로 나눈 나머지와, 해당 나머지에 1을 더한 값을 구한다.
            float_tmp_sum_fr_min, float_tmp_sum_fr_max = (
                fn_make_temporary_sum(df_return.at[index, 'Adjust Loading Qty Sum FR']))
            # 이전 단계 또는 조정 전 단계에서의 FTL 여부에 대한 플래그
            before_ftl_flag = fn_is_ftl(float_tmp_sum_fr_min, float_tmp_sum_fr_max, float_min_fr, float_max_fr)

            ########################################################################################################
            # CUT이면서 현재가 FTL이면 전체 조정 완료
            if str_cut_add_flag == 'CUT':
                if df_return.at[index, 'Adjust Loading Qty'] <= 0:
                    # CUT이면서 조정된 Loading Qty가 0 이하이면 현재 건은 조정 안 함.
                    continue
                if Param_Adjust_Option1 == 'MAX' and before_ftl_flag:
                    # adjust option 1이 MAX FTL일 때, 조정이 CUT이면서 FTL이면 전체 조정 완료
                    complete_flag = True
                    break
            elif str_cut_add_flag == 'ADD':
                if Param_Adjust_Option1 == 'MIN' and before_ftl_flag:
                    # adjust option 1이 MIN FTL일 때, 조정이 ADD이면서 FTL이면 전체 조정 완료
                    complete_flag = True
                    break

            ########################################################################################################
            # 조정
            # Cut 조정 시 조정 후 0이 되는 값을 찾기 위해 조정 전 수치를 기록
            int_before_adjust_qty = df_return.at[index, 'Adjust Loading Qty']
            df_return = fn_adjust_row(df_return, row, index, str_cut_add_flag, int_add_cut_cnt)
            # Cut 조정 시 조정 후 0이 되는 값을 찾기 위해 조정 후 수치를 기록
            int_after_adjust_qty = df_return.at[index, 'Adjust Loading Qty']
            # 조정 전 수치가 조정 후 수치보다 크면서(Cut 조정), 조정 후 수치가 0인 경우
            if (int_before_adjust_qty > int_after_adjust_qty) and (int_after_adjust_qty == 0):
                # 조정 수치가 0이 된 아이템의 갯수를 1 증가
                int_adjust_zero_count += 1
                if int_adjust_zero_count == int_adjust_size:
                    # 조정 수치가 0이 된 아이템의 갯수가 전체 아이템 갯수와 동일하면 조정 종료
                    complete_flag = True
                    break
            # 조정 후의 Sum(Fill Rate)를 기록
            float_tmp_max_sum_fr = df_return.at[index, 'Adjust Loading Qty Sum FR']

            ########################################################################################################
            # 조정된 수치가 FTL 기준에 부합하는지 확인
            float_tmp_sum_fr_min, float_tmp_sum_fr_max = fn_make_temporary_sum(float_tmp_max_sum_fr)
            ftl_flag = fn_is_ftl(float_tmp_sum_fr_min, float_tmp_sum_fr_max, float_min_fr, float_max_fr)

            # 조정된 SUM(F/R)의 100 단위가 변경되었는지 확인
            # ex add : 150%(1.5) -> 200%(2.0), 95%(0.95) -> 102%(1.02)
            # ex cut : 204%(2.04) -> 199%(1.99), 103%(1.03) -> 99%(0.99)
            if np.trunc(float_tmp_max_sum_fr) != int_add_cut_basis:
                if ftl_flag:
                    # 조정된 수치가 FTL이면 Max에 근접한 값을 찾기 위해 바로 다음 아이템으로 넘어간다.
                    continue
                else:
                    if before_ftl_flag:
                        # 조정 전에 이미 FTL이면서 CUT인 경우는 위에서 루프를 나가기 때문에 이 곳에서는 ADD인 경우만 들어 옴.
                        if not ftl_flag:
                            # 조정 전에 FTL이었으나 조정 후 FTL이 아니면 조정 수치 복원
                            # 조정된 수치가 Min를 벗어났기 때문에 조정된 수치를 이전 수치로 복원함.
                            df_return = fn_adjust_rollback(df_return, row, index, str_cut_add_flag, int_add_cut_cnt)
                            # 현재 그룹에서는 조정이 완료되었기 때문에 조정 종료
                            complete_flag = True
                            break

            # 조정 후 FTL이 아닌 경우
            if not ftl_flag:
                if before_ftl_flag:
                    # 조정 전에 FTL이었으나 조정 후 FTL이 아니면 조정 수치 복원
                    # 조정된 수치가 Max를 초과했기 때문에 조정된 수치를 이전 수치로 복원함.
                    df_return = fn_adjust_rollback(df_return, row, index, str_cut_add_flag, int_add_cut_cnt)
                    # 현재 그룹에서는 조정이 완료되었기 때문에 조정 종료
                    complete_flag = True
                    break
                else:
                    # 조정 전이나 조정 후 모두 FTL이 아니기 때문에 다음 아이템으로 넘어 감.
                    continue
        # 전체 조정 종료
        if complete_flag:
            break

    return df_return


@_decoration_
def fn_adjust(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 5. Adjust
    0) 직전 단계의 [FTL 여부]가 "LTL"인 것을 대상으로 하며, Aggregation 기준은 직전 단계의 Group 기준으로 한다.
       단 Mix 없이 Single Item 계산이 최종인 경우, Aggregation 없이 각 Item별로 M/L Qty와의 차이로 계산한다.
    1) [Loading Dir Order Mgmt_Adjust LTL Qty]
       [Rest Qty] = Single Item.[FTL 제외 아이템 수]
    2) [Loading Dir Order Mgmt_Adjust LTL Group]
       [Group CD] = 마지막 Mix 시의 그룹, Mix 과정이 없었다면 그룹 없음.
    3) [Loading Dir Order Mgmt_Adjust LTL Sum FR]
       [Sum F/R] = Sum(Group.[Rest F/R])
    4) [Loading Dir Order Mgmt_Adjust MOD]
       [Mod] = Reminder(Single Item.[FTL 제외 아이템 수] / [Multiple])
    5) [Loading Dir Order Mgmt_Adjust Multiple]
       [Adjust Rest Qty] = Round(Single Item.[FTL 제외 아이템 수] / [Multiple], 0) * [Multiple]
    6) [Loading Dir Order Mgmt_Adjust FR]
       [Adjust F/R] = ([Adjust Rest Qty] / [M/L Qty]) * 100%
    7) [Loading Dir Order Mgmt_Adjust Sum FR]
       [Sum of Adjust F/R] = Sum([Adjust F/R])
    8) [Loading Dir Order Mgmt_Adjust MOD FR]
       [Mod of Sum of Adjust F/R] = Reminder([Sum of Adjust F/R])
    9) [Loading Dir Order Mgmt_Adjust Add Cnt]
       [Add Cnt] = 더하여 조정할 숫자(이후 Multiple을 곱하여 더할 아이템 수를 구함)
    10) [Loading Dir Order Mgmt_Adjust Cut Cnt]
        [Cut Cnt] = 감하여 조정할 숫자(이후 Multiple을 곱하여 감할 아이템 수를 구함)
    11) [Loading Dir Order Mgmt_Adjust Add Qty]
        [Add Qty] = [Add Cnt] * [Multiple]
    12) [Loading Dir Order Mgmt_Adjust Cut Qty]
        [Cut Qty] = [Cut Cnt] * [Multiple]
    13) [Loading Dir Order Mgmt_Adjust Diff Qty]
        [Diff Qty] = [Loading Qty] - [Rest Qty]
    14) [Loading Dir Order Mgmt_Adjust Loading Qty]
        [Adjust Loading Qty] = [Adjust Rest Qty] + [Add Qty] - [Cut Qty]
    15) [Loading Dir Order Mgmt_Adjust Loading Qty FR]
        [Adjust Loading Qty F/R] = ([Adjust Loading Qty] / [M/L Qty]) * 100%
    16) [Loading Dir Order Mgmt_Adjust Loading Qty Sum FR]
        [Adjust Sum F/R] = Sum(Group.[Adjust Loading Qty F/R])
    17) [Loading Dir Order Mgmt_Adjust FTL Cntr]
        [FTL Cntr] = Round([Adjust Sum F/R])
    18) [Loading Dir Order Mgmt_Last Loading Qty]
        [Last Loading Qty] = [Single Item Complete Qty] + [Mixed Item Loading Qty] + [Adjust Loading Qty]
    19) [Loading Dir Order Mgmt_Diff]
        [Diff] = [Last Loading Qty] - [Chk Qty]
    20) [Loading Order Mgmt_Mixed Item FR]
        [Mixed Item FR] =
    :param df_p_source:
    :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # 0) 직전 단계의 [FTL 여부]가 "LTL"인 것을 대상으로 하며, Aggregation 기준은 직전 단계의 Group 기준으로 한다.
    #    단 Mix 없이 Single Item 계산이 최종인 경우, Aggregation 없이 각 Item별로 M/L Qty와의 차이로 계산한다.
    # -> 1st Mix가 None인 경우를 먼저 처리한 후 그 이외의 경우를 처리한다.
    list_where_adjust_target = df_return['Mixed Item Cntr Status'] == 'LTL'
    # Add Cnt, Cut Cnt 초기화
    df_return.loc[list_where_adjust_target, 'Adjust Add Cnt'] = 0
    df_return.loc[list_where_adjust_target, 'Adjust Cut Cnt'] = 0
    list_where_adjust_target_single = list_where_adjust_target & (df_return['1st Mix'] == 'None')
    list_where_adjust_target_mix = list_where_adjust_target & (df_return['1st Mix'] != 'None')

    ####################################################################################################################
    # Single Item - Adjust 처리
    df_adjust_single = df_return[list_where_adjust_target & list_where_adjust_target_single].copy(deep=True)
    if not df_adjust_single.empty and len(df_adjust_single) > 0:
        # 1) [Loading Dir Order Mgmt_Adjust LTL Qty]
        #    [Rest Qty] = Single Item.[FTL 제외 아이템 수]
        df_adjust_single['Adjust LTL Qty'] = df_adjust_single['Single Item Rest Qty']
        # 4) [Loading Dir Order Mgmt_Adjust MOD]
        #    [Mod] = Reminder(Single Item.[FTL 제외 아이템 수] / [Multiple])
        df_adjust_single['Adjust MOD'] = df_adjust_single['Single Item Rest Qty'] % df_adjust_single['Multiple']
        # 5) [Loading Dir Order Mgmt_Adjust Multiple]
        #    [Adjust Rest Qty] = Round(Single Item.[FTL 제외 아이템 수] / [Multiple], 0) * [Multiple]
        df_adjust_single['Adjust Multiple'] = df_adjust_single.apply(
            lambda row:
            int(common.gfn_get_round(row['Single Item Rest Qty'] / row['Multiple'], 0)) * row['Multiple'],
            axis=1)
        # 6) [Loading Dir Order Mgmt_Adjust FR]
        #    [Adjust F/R] = ([Adjust Rest Qty] / [M/L Qty]) * 100%
        df_adjust_single['Adjust FR'] = df_adjust_single['Adjust Multiple'] / df_adjust_single['Max Load Qty']
        # 7) [Loading Dir Order Mgmt_Adjust Sum FR]
        #    [Sum of Adjust F/R] = Sum([Adjust F/R])
        df_adjust_single['Adjust Sum FR'] = df_adjust_single['Adjust FR']
        # 8) [Loading Dir Order Mgmt_Adjust MOD FR]
        #    [Mod of Sum of Adjust F/R] = Reminder([Sum of Adjust F/R])
        df_adjust_single['Adjust MOD FR'] = df_adjust_single['Adjust Sum FR'] % 1
        # CUT/ADD 여부 확인
        df_adjust_single['Adjust Cut Add'] = (
            np.where(df_adjust_single['Adjust MOD FR'] > df_adjust_single['Mix Cut Add'], 'ADD', 'CUT'))
        # 9) [Loading Dir Order Mgmt_Adjust Add Cnt] - 초기화
        #    [Add Cnt] = 더하여 조정할 숫자(이후 Multiple을 곱하여 더할 아이템 수를 구함)
        df_adjust_single['Adjust Add Cnt'] = 0
        # 10) [Loading Dir Order Mgmt_Adjust Cut Cnt] - 초기화
        #     [Cut Cnt] = 감하여 조정할 숫자(이후 Multiple을 곱하여 감할 아이템 수를 구함)
        df_adjust_single['Adjust Cut Cnt'] = 0
        # 11) [Loading Dir Order Mgmt_Adjust Add Qty] - 초기화
        #     [Add Qty] = [Add Cnt] * [Multiple]
        df_adjust_single['Adjust Add Qty'] = 0
        # 12) [Loading Dir Order Mgmt_Adjust Cut Qty] - 초기화
        #     [Cut Qty] = [Cut Cnt] * [Multiple]
        df_adjust_single['Adjust Cut Qty'] = 0
        # 14) [Loading Dir Order Mgmt_Adjust Loading Qty] - adjust 전 초기값
        #     [Adjust Loading Qty] = [Adjust Rest Qty] + [Add Qty] - [Cut Qty]
        df_adjust_single['Adjust Loading Qty'] = df_adjust_single['Adjust Multiple']
        # 15) [Loading Dir Order Mgmt_Adjust Loading Qty FR] - adjust 전 초기값
        #     [Adjust Loading Qty F/R] = ([Adjust Loading Qty] / [M/L Qty]) * 100%
        df_adjust_single['Adjust Loading Qty FR'] = df_adjust_single['Adjust FR']
        # 16) [Loading Dir Order Mgmt_Adjust Loading Qty Sum FR] - adjust 전 초기값
        #     [Adjust Sum F/R] = Sum(Group.[Adjust Loading Qty F/R])
        df_adjust_single['Adjust Loading Qty Sum FR'] = df_adjust_single['Adjust Loading Qty FR']
        # 18) [Loading Dir Order Mgmt_Last Loading Qty]
        #     [Last Loading Qty] = [Single Item Complete Qty] + [Mixed Item Loading Qty] + [Adjust Loading Qty]
        df_adjust_single['Last Loading Qty'] = (df_adjust_single['Single Item Complete Qty'] +
                                                df_adjust_single['Mixed Item Loading Qty'] +
                                                df_adjust_single['Adjust Loading Qty'])
        # 19) [Loading Dir Order Mgmt_Diff]
        #     [Diff] = [Last Loading Qty] - [Chk Qty]
        df_adjust_single['Diff'] = df_adjust_single['Last Loading Qty'] - df_adjust_single['Chk Qty']

    # fn_log_dataframe(df_adjust_single, 'df_adjust_single')

    ####################################################################################################################
    # Mixed - Adjust 처리
    df_adjust_mix = df_return[list_where_adjust_target & list_where_adjust_target_mix].copy(deep=True)
    if not df_adjust_mix.empty and len(df_adjust_mix) > 0:
        # 1) [Loading Dir Order Mgmt_Adjust LTL Qty]
        #    [Rest Qty] = Single Item.[FTL 제외 아이템 수]
        df_adjust_mix['Adjust LTL Qty'] = df_adjust_mix['Single Item Rest Qty']
        # 2) [Loading Dir Order Mgmt_Adjust LTL Group]
        #    [Group CD] = 마지막 Mix 시의 그룹, Mix 과정이 없었다면 그룹 없음.
        df_adjust_mix['Adjust LTL Group'] = df_adjust_mix['Last Mix Group']
        # 3) [Loading Dir Order Mgmt_Adjust LTL Sum FR]
        #    [Sum F/R] = Sum(Group.[Rest F/R])
        df_adjust_mix['Adjust LTL Sum FR'] = (
            df_adjust_mix.groupby(by=['Mix Group Base Grouping Key'])['Single Item Rest FR'].transform('sum'))
        # 4) [Loading Dir Order Mgmt_Adjust MOD]
        #    [Mod] = Reminder(Single Item.[FTL 제외 아이템 수] / [Multiple])
        df_adjust_mix['Adjust MOD'] = df_adjust_mix['Single Item Rest Qty'] % df_adjust_mix['Multiple']
        # 5) [Loading Dir Order Mgmt_Adjust Multiple]
        #    [Adjust Rest Qty] = Round(Single Item.[FTL 제외 아이템 수] / [Multiple], 0) * [Multiple]
        df_adjust_mix['Adjust Multiple'] = df_adjust_mix.apply(
            lambda row:
            int(common.gfn_get_round(row['Single Item Rest Qty'] / row['Multiple'], 0)) * row['Multiple'],
            axis=1)
        # 6) [Loading Dir Order Mgmt_Adjust FR]
        #    [Adjust F/R] = ([Adjust Rest Qty] / [M/L Qty]) * 100%
        df_adjust_mix['Adjust FR'] = df_adjust_mix['Adjust Multiple'] / df_adjust_mix['Max Load Qty']
        # 7) [Loading Dir Order Mgmt_Adjust Sum FR]
        #    [Sum of Adjust F/R] = Sum([Adjust F/R])
        df_adjust_mix['Adjust Sum FR'] = df_adjust_mix.groupby(by=['Mix Group Base Grouping Key'])[
            'Adjust FR'].transform('sum')
        # 8) [Loading Dir Order Mgmt_Adjust MOD FR]
        #    [Mod of Sum of Adjust F/R] = Reminder([Sum of Adjust F/R])
        df_adjust_mix['Adjust MOD FR'] = df_adjust_mix['Adjust Sum FR'] % 1
        # CUT/ADD 여부 확인
        df_adjust_mix['Adjust Cut Add'] = (
            np.where(df_adjust_mix['Adjust MOD FR'] > df_adjust_mix['Mix Cut Add'], 'ADD', 'CUT'))
        # 9) [Loading Dir Order Mgmt_Adjust Add Cnt] - 초기화
        #    [Add Cnt] = 더하여 조정할 숫자(이후 Multiple을 곱하여 더할 아이템 수를 구함)
        df_adjust_mix['Adjust Add Cnt'] = 0
        # 10) [Loading Dir Order Mgmt_Adjust Cut Cnt] - 초기화
        #     [Cut Cnt] = 감하여 조정할 숫자(이후 Multiple을 곱하여 감할 아이템 수를 구함)
        df_adjust_mix['Adjust Cut Cnt'] = 0
        # 11) [Loading Dir Order Mgmt_Adjust Add Qty] - 초기화
        #     [Add Qty] = [Add Cnt] * [Multiple]
        df_adjust_mix['Adjust Add Qty'] = 0
        # 12) [Loading Dir Order Mgmt_Adjust Cut Qty] - 초기화
        #     [Cut Qty] = [Cut Cnt] * [Multiple]
        df_adjust_mix['Adjust Cut Qty'] = 0
        # 14) [Loading Dir Order Mgmt_Adjust Loading Qty] - adjust 전 초기값
        #     [Adjust Loading Qty] = [Adjust Rest Qty] + [Add Qty] - [Cut Qty]
        df_adjust_mix['Adjust Loading Qty'] = df_adjust_mix['Adjust Multiple']
        # 15) [Loading Dir Order Mgmt_Adjust Loading Qty FR] - adjust 전 초기값
        #     [Adjust Loading Qty F/R] = ([Adjust Loading Qty] / [M/L Qty]) * 100%
        df_adjust_mix['Adjust Loading Qty FR'] = df_adjust_mix['Adjust FR']
        # 16) [Loading Dir Order Mgmt_Adjust Loading Qty Sum FR] - adjust 전 초기값
        #     [Adjust Sum F/R] = Sum(Group.[Adjust Loading Qty F/R])
        df_adjust_mix['Adjust Loading Qty Sum FR'] = (
            df_adjust_mix.groupby(by=['Mix Group Base Grouping Key'])['Adjust Loading Qty FR'].transform('sum'))
        # fn_log_dataframe(df_adjust_mix, 'df_adjust_mix')
        # Adjust Option2에 따라 분기
        if Param_Adjust_Option2 == 'Max Profit':
            df_adjust_mix = df_adjust_mix.groupby(by=['Mix Group Base Grouping Key']).apply(fn_adjust_by_max_profit)
        elif Param_Adjust_Option2 == 'Min Item Change':
            df_adjust_mix = df_adjust_mix.groupby(by=['Mix Group Base Grouping Key']).apply(
                fn_adjust_by_min_item_change)
        # 13) [Loading Dir Order Mgmt_Adjust Diff Qty]
        #     [Diff Qty] = [Loading Qty] - [Rest Qty]
        df_adjust_mix['Adjust Diff Qty'] = (
                df_adjust_mix['Adjust Loading Qty'] - df_adjust_mix['Single Item Rest Qty'])
        # 17) [Loading Dir Order Mgmt_Adjust FTL Cntr]
        #     [FTL Cntr] = Round([Adjust Sum F/R])
        df_adjust_mix['Adjust FTL Cntr'] = df_adjust_mix.apply(
            lambda row: int(common.gfn_get_round(row['Adjust Loading Qty Sum FR'], 0)), axis=1)
        # [Loading Order Mgmt_Last LTL Qty]
        # [Last LTL Qty] = [Adjust Loading Qty]
        df_adjust_mix['Last LTL Qty'] = df_adjust_mix['Adjust Loading Qty']
        # 18) [Loading Dir Order Mgmt_Last Loading Qty]
        #     [Last Loading Qty] = [Single Item Complete Qty] + [Mixed Item Loading Qty] + [Adjust Loading Qty]
        df_adjust_mix['Last Loading Qty'] = (df_adjust_mix['Single Item Complete Qty'] +
                                             df_adjust_mix['Mixed Item Loading Qty'] +
                                             df_adjust_mix['Adjust Loading Qty'])
        # 19) [Loading Dir Order Mgmt_Diff]
        #     [Diff] = [Last Loading Qty] - [Chk Qty]
        df_adjust_mix['Diff'] = df_adjust_mix['Last Loading Qty'] - df_adjust_mix['Chk Qty']

    # adjust 비대상
    df_no_target = df_return[~list_where_adjust_target]
    if not df_no_target.empty and len(df_no_target) > 0:
        # 1) [Loading Dir Order Mgmt_Adjust LTL Qty]
        #    [Rest Qty] = Single Item.[FTL 제외 아이템 수]
        df_no_target['Adjust LTL Qty'] = np.nan
        # 2) [Loading Dir Order Mgmt_Adjust LTL Group]
        #    [Group CD] = 마지막 Mix 시의 그룹, Mix 과정이 없었다면 그룹 없음.
        df_no_target['Adjust LTL Group'] = np.nan
        # 3) [Loading Dir Order Mgmt_Adjust LTL Sum FR]
        #    [Sum F/R] = Sum(Group.[Rest F/R])
        df_no_target['Adjust LTL Sum FR'] = np.nan
        # 4) [Loading Dir Order Mgmt_Adjust MOD]
        #    [Mod] = Reminder(Single Item.[FTL 제외 아이템 수] / [Multiple])
        df_no_target['Adjust MOD'] = np.nan
        # 5) [Loading Dir Order Mgmt_Adjust Multiple]
        #    [Adjust Rest Qty] = Round(Single Item.[FTL 제외 아이템 수] / [Multiple], 0) * [Multiple]
        df_no_target['Adjust Multiple'] = np.nan
        # 6) [Loading Dir Order Mgmt_Adjust FR]
        #    [Adjust F/R] = ([Adjust Rest Qty] / [M/L Qty]) * 100%
        df_no_target['Adjust FR'] = np.nan
        # 7) [Loading Dir Order Mgmt_Adjust Sum FR]
        #    [Sum of Adjust F/R] = Sum([Adjust F/R])
        df_no_target['Adjust Sum FR'] = np.nan
        # 8) [Loading Dir Order Mgmt_Adjust MOD FR]
        #    [Mod of Sum of Adjust F/R] = Reminder([Sum of Adjust F/R])
        df_no_target['Adjust MOD FR'] = np.nan
        # CUT/ADD 여부 확인
        df_no_target['Adjust Cut Add'] = np.nan
        # 9) [Loading Dir Order Mgmt_Adjust Add Cnt] - 초기화
        #    [Add Cnt] = 더하여 조정할 숫자(이후 Multiple을 곱하여 더할 아이템 수를 구함)
        df_no_target['Adjust Add Cnt'] = np.nan
        # 10) [Loading Dir Order Mgmt_Adjust Cut Cnt] - 초기화
        #     [Cut Cnt] = 감하여 조정할 숫자(이후 Multiple을 곱하여 감할 아이템 수를 구함)
        df_no_target['Adjust Cut Cnt'] = np.nan
        # 11) [Loading Dir Order Mgmt_Adjust Add Qty] - 초기화
        #     [Add Qty] = [Add Cnt] * [Multiple]
        df_no_target['Adjust Add Qty'] = np.nan
        # 12) [Loading Dir Order Mgmt_Adjust Cut Qty] - 초기화
        #     [Cut Qty] = [Cut Cnt] * [Multiple]
        df_no_target['Adjust Cut Qty'] = np.nan
        # 14) [Loading Dir Order Mgmt_Adjust Loading Qty] - adjust 전 초기값
        #     [Adjust Loading Qty] = [Adjust Rest Qty] + [Add Qty] - [Cut Qty]
        df_no_target['Adjust Loading Qty'] = np.nan
        # 15) [Loading Dir Order Mgmt_Adjust Loading Qty FR] - adjust 전 초기값
        #     [Adjust Loading Qty F/R] = ([Adjust Loading Qty] / [M/L Qty]) * 100%
        df_no_target['Adjust Loading Qty FR'] = np.nan
        # 16) [Loading Dir Order Mgmt_Adjust Loading Qty Sum FR] - adjust 전 초기값
        #     [Adjust Sum F/R] = Sum(Group.[Adjust Loading Qty F/R])
        df_no_target['Adjust Loading Qty Sum FR'] = np.nan
        # fn_log_dataframe(df_adjust_mix, 'df_adjust_mix')
        # Adjust Option2에 따라 분기

        # 13) [Loading Dir Order Mgmt_Adjust Diff Qty]
        #     [Diff Qty] = [Loading Qty] - [Rest Qty]
        df_no_target['Adjust Diff Qty'] = np.nan
        # 17) [Loading Dir Order Mgmt_Adjust FTL Cntr]
        #     [FTL Cntr] = Round([Adjust Sum F/R])
        df_no_target['Adjust FTL Cntr'] = np.nan
        # [Loading Order Mgmt_Last LTL Qty]
        # [Last LTL Qty] = [Adjust Loading Qty]
        df_no_target['Last LTL Qty'] = np.nan

    df_return = pd.concat([df_no_target, df_adjust_single, df_adjust_mix], ignore_index=True)
    df_return.sort_values(by=['Seq.[Seq]'], inplace=True)

    df_debug_adjust = df_return[[
        'Seq.[Seq]',
        'Location.[Location]',
        'Time.[Week]',
        'Item',
        'Chk Qty',
        'Max Load Qty',
        'Multiple',
        'Mixed Item Cntr Status',
        'Adjust LTL Group',
        'Mix Group Base Grouping Key',
        'Profit Grade',
        'Profit Grade Priority',
        'Mix Cut Add',
        'Adjust Add Cnt',
        'Adjust Add Qty',
        'Adjust Cut Add',
        'Adjust Cut Cnt',
        'Adjust Cut Qty',
        'Adjust Loading Qty',
        'Adjust Diff Qty',
        'Adjust Loading Qty FR',
        'Mix Max FR',
        'Mix Min FR',
        'Adjust Loading Qty Sum FR',
        'Adjust FTL Cntr',
        'Last LTL Qty',
        'Last Mix Group',
        'Last Loading Qty',
        'Diff'
    ]].copy(deep=True)
    fn_log_dataframe(df_debug_adjust, 'df_debug_adjust')

    return df_return


@_decoration_
def fn_container_planning_single(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    Single container planning function
    0. Single FTL
    1. Single Complete
    :param df_p_source:
    :param str_p_cond: 0. Single FTL, 1. Single Complete
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    if str_p_cond == '0':
        # Single FTL의 경우 컨테이너 숫자만큼 행 복사하기
        df_return = (
            df_p_source.loc[df_p_source.index.repeat(df_p_source['Single Item FTL Count'])].reset_index(drop=True))
    elif str_p_cond == '1':
        # Single Complete의 경우 컨테이너 숫자 + 1만큼 행 복사하기
        df_return = (
            df_p_source.loc[df_p_source.index.repeat(df_p_source['Single Item FTL Count'] + 1)].reset_index(drop=True))

    # 컨테이너 당 적재 수량 넣기
    df_return['Loading Qty Per Cntr'] = (
        (df_return['Single Item Complete Qty'] / df_return['Single Item FTL Count']).astype(int))
    # Cntr Planning 순서를 기록
    df_return['cntr_seq'] = (
            df_return.groupby(by=['Time.[Week]', 'Location.[Location]', 'To Site', 'Account', 'Ship To', 'Seq.[Seq]']).
            cumcount() + 1).astype(int)
    # Cntr Block을 기록 - sigle은 모두 자체로 블럭이므로 전부 1로 기록
    df_return['cntr_block'] = 1
    if str_p_cond == '0':
        # Cntr Planning 종류 구분 컬럼 - Single FTL - SF
        df_return['Plan Type'] = '01.SF'
    if str_p_cond == '1':
        # Cntr Planning 종류 구분 컬럼 - Single Complete - SC
        list_where_single_complete = df_return['cntr_seq'] <= df_return['Single Item FTL Count']
        df_return.loc[list_where_single_complete, 'Plan Type'] = '02.SC'
        # Single Complete의 마지막 행은 LTL로 처리되어야 하므로 컨테이너 번호 및 컨테이너 적재 수량, 컨테이너 블럭 초기화
        list_where_last = df_return['cntr_seq'] > df_return['Single Item FTL Count']
        df_return.loc[list_where_last, 'Loading Qty Per Cntr'] = np.nan
        df_return.loc[list_where_last, 'cntr_block'] = np.nan

    return df_return


def fn_container_planning_mixed(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # debug용 코드
    # df_tmp = df_p_source[df_p_source['Seq.[Seq]'] == 564]
    # if not df_tmp.empty and len(df_tmp) > 0:
    #     print('DEBUG')
    # M/L Qty 내림차순으로 정렬
    df_return = df_p_source.sort_values(by=['Max Load Qty'], ascending=[False]).copy(deep=True)

    int_container_count = 0
    if str_p_cond == '0':
        # Mixed FTL의 경우
        # 적재 수량 조정 시 splite 여부 확인 등을 위한 기준 Fill Rate의 누적 합을 계산
        df_return['Cum Sum of Mixed Item FR'] = df_return['Mixed Item FR'].cumsum()
        # 할당할 Cntr 댓수 계산
        num_cntr_fr = df_return.iloc[0]['Mixed Item Cntr FR']
        int_container_count = int(num_cntr_fr) + 1 if num_cntr_fr % 1 != 0 else int(num_cntr_fr)
    elif str_p_cond == '1':
        # Mixed LTL의 경우
        # 적재 수량 조정 시 splite 여부 확인 등을 위한 기준 Fill Rate의 누적 합을 계산
        df_return['Cum Sum of Mixed Item FR'] = df_return['Adjust Loading Qty FR'].cumsum()
        # 할당할 Cntr 댓수 계산
        int_container_count = df_return.iloc[0]['Adjust FTL Cntr'].astype(int)

    # 컨테이너 댓수를 배열로 생성
    list_container_count = list(range(1, int_container_count + 1))
    # 컨테이너 댓수 배열 루프
    prev_item = 0
    blocked_inx = []
    for item in list_container_count:
        # 현재 처리 대상인 이전 처리했던 블럭의 다음 블럭을 추출한다. - n번(item)째 컨테이너 처리
        list_where = ((df_return['Cum Sum of Mixed Item FR'] > prev_item) &
                      (df_return['Cum Sum of Mixed Item FR'] <= item))
        df_current_block = df_return.loc[list_where]
        # Cntr block을 설정한다.
        df_return.loc[list_where, 'cntr_block'] = int(item)
        if blocked_inx:
            # split 되어야 하는 행의 경우에는 이전 루프에서 설정한 인덱스를 이용하여 값을 업데이트한다.
            df_return.at[blocked_inx[0], 'cntr_block'] = [int(item - 1), int(item)]
            # 참조한 인덱스를 초기화한다.
            blocked_inx = []
        # 현재 블럭의 가장 마지막 행에서 Mixed Item FR의 누적 Sum을 추출한다.
        cur_max_cumsum = df_current_block['Cum Sum of Mixed Item FR'].iloc[-1]
        prev_item = item
        # 누적 Sum n번째 컨테이너 댓수보다 작은 경우(cumsum < 1(or n)
        if cur_max_cumsum < item:
            # 그룹 전체에서 n번째 컨테이너 댓수보다 큰 cumsum이 있는 데이터(현재 처리 블럭의 다음 블럭)를 추출한다.
            list_where = df_return['Cum Sum of Mixed Item FR'] > item
            df_next_block = df_return.loc[list_where]
            if df_next_block.empty or len(df_next_block) == 0:
                # 다음 블럭이 없다면 처리 대상이 없으므로 루프를 종료한다.
                break
            # 이후 Split 대상이 될 행을 찾기 위해 다음 블럭의 첫번째 행의 Seq.[Seq]를 찾는다.
            cur_row_seq = (df_return.loc[list_where]).iloc[0]['Seq.[Seq]']
            list_where = df_return['Seq.[Seq]'] == cur_row_seq
            # Split을 처리를 위한 변수를 할당한다.
            # Split 대상 행의 M/L Qty에 대한 Multiple의 Fill Rate를 구한다.
            num_base_multiple = (df_return.loc[list_where]).iloc[0]['Multiple Loading Rate']
            # Split 대상 행의 Multiple을 구한다.
            num_multiple = (df_return.loc[list_where]).iloc[0]['Multiple']
            # Split 대상 행의 조정 전 적재 대상 수량을 구한다.
            cur_loading_qty = 0
            if str_p_cond == '0':
                # Mixed FTL의 경우
                cur_loading_qty = (df_return.loc[list_where]).iloc[0]['Mixed Item Loading Qty']
            elif str_p_cond == '1':
                # Mixed LTL의 경우
                cur_loading_qty = (df_return.loc[list_where]).iloc[0]['Adjust Loading Qty']
            # n번째 컨테이너 댓수에서 cumsum의 차를 구하여 Split 대상 행에서 Split할 적재 수량을 구할 때 사용한다.
            diff_max_cumsum_to_item = item - cur_max_cumsum
            # Multiple 기준 Fill Rate가 n번째 컨테이너 댓수에서 cumsum의 차 이상인 경우
            # Multiple 기준으로 Split 해야 하나 가능한 수량이 Multiple을 초과하면 Split이 블가능하기 때문에 Split 처리 없이 다음 진행
            if diff_max_cumsum_to_item >= num_base_multiple:
                # 부동 소수점 처리 오류로 인해 모든 숫자는 Decimal로 처리함.
                decimal_base_multiple = Decimal(str(num_base_multiple))
                decimal_diff_max_cumsum_to_item = Decimal(str(diff_max_cumsum_to_item))
                # Multiple 의 배수 중 컨테이너를 채울 수 있는 가장 큰 배수를 구한다.
                num_max_multiple = decimal_diff_max_cumsum_to_item // decimal_base_multiple
                # 최대 Multiple의 배수를 Multiple에 곱하여 Split하여 위의 컨테이너에 더할 적재 수량을 구한다.
                int_split_upper_qty = int(num_max_multiple) * int(num_multiple)
                # 현재 행의 적제 수량에서 Split할 적재 수량의 차를 구하여 다음 컨테이너에 더할 적재 수량을 구한다.
                int_split_lower_qty = int(cur_loading_qty) - int(int_split_upper_qty)
                # Split 대상 행의 인덱스츨 핮는다.
                inx = df_return.index[list_where].to_list()
                if inx:
                    # 해당 행에 Split할 적재 수량을 리스트로 적재한다.
                    df_return.at[inx[0], 'Split Qty List'] = [int_split_upper_qty, int_split_lower_qty]
                    # Split 시에 이전 블록과 다음 블럭을 구분할 리스트를 적재한다.
                    df_return.at[inx[0], 'cntr_block'] = [int(item), int(item + 1)]
                    blocked_inx = [inx[0]]
            else:
                continue
        else:
            continue

    # Cntr Planning 순서를 기록
    df_return['cntr_seq'] = (
            df_return.groupby(by=['Time.[Week]', 'Location.[Location]', 'To Site', 'Account', 'Ship To']).
            cumcount() + 1).astype(int)
    df_return = df_return.reset_index(drop=True)
    # debug용 코드
    # if df_return.loc[0, 'Seq.[Seq]'] == 564:
    #     print('a')
    # Split List를 이용하여 Row를 Split 처리
    # df_return = df_return.explode('Split Qty List').reset_index(drop=True).explode('cntr_block').reset_index(drop=True)
    df_return = df_return.apply(pd.Series.explode).reset_index()
    # Split Qty를 최종 Loading Qty로 반영
    df_return['Loading Qty Per Cntr'] = df_return['Split Qty List']
    if str_p_cond == '0':
        # Mixed FTL의 경우
        # 작업 유형을 MF(Mixed FTL)로 설정
        df_return['Plan Type'] = '03.MF'
    elif str_p_cond == '1':
        # Mixed LTL의 경우
        # 작업 유형을 MF(Mixed LTL)로 설정
        df_return['Plan Type'] = '04.ML'

    return df_return


def fn_cntr_numbering_by_group(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 데이터 가공 전 원본 DF 복사
    df_return = df_p_source.sort_values(by=['Plan Type', 'Last Mix Group', 'cntr_seq', 'cntr_block'],
                                        ascending=[True, True, True, True]).copy(deep=True)

    int_current_block = 0
    int_check_block = 0
    int_cntr_seq = 0
    for inx, row in df_return.iterrows():
        if row['Plan Type'] == '01.SF' or row['Plan Type'] == '02.SC':
            int_cntr_seq += 1
            df_return.at[inx, 'Cntr No'] = row['Plan Group Key'] + '_' + str(int_cntr_seq).zfill(5)
        elif row['Plan Type'] == '03.MF' or row['Plan Type'] == '04.ML':
            int_current_block = row['cntr_block']
            if int_current_block != int_check_block:
                int_cntr_seq += 1
                int_check_block = int_current_block
            df_return.at[inx, 'Cntr No'] = row['Plan Group Key'] + '_' + str(int_cntr_seq).zfill(5)

    return df_return


@_decoration_
def fn_cntr_numbering_main(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # NP(No Planning) - Adjust Qty가 0인 경우는 Numbering 대상에서 제외
    list_where_no_planning = df_p_source['Plan Type'] == '05.NP'
    df_no_target = df_p_source[list_where_no_planning]
    df_target = df_p_source[~list_where_no_planning]
    # 출발-도착지 기준(Prod Week-From-To-Account-Ship To) 기준으로 그룹핑하여 넘버링 작업함.
    df_target = df_target.groupby('Plan Group Key').apply(fn_cntr_numbering_by_group)
    df_return = pd.concat([df_target, df_no_target], ignore_index=True)

    return df_return


@_decoration_
def fn_container_planning(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 6. Container Planning
        1. Single FTL CNTR 할당
        2. LTL 중 Single Complete CNTR 할당
        3. 1st. Mix FTL CNTR 할당
        4. 2nd. Mix FTL CNTR 할당
        5. 3rd. Mix FTL CNTR 할당
        6. 출도착지 별 LTL ADJ M/L Qty 작은 순 정렬
        7. LTL ADJ CNTR 할당
        8. Cntr Numbering
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 0. Mixed Item의 Cntr Planning에 필요한 컬럼 추가
    # Plan Type 지정
    df_p_source = df_p_source.assign(**{
        'Multiple Loading Rate': df_p_source['Multiple'] / df_p_source['Max Load Qty'],
        'Split Qty List': np.where(df_p_source['Mixed Item Cntr Status'] == 'LTL',
                                   df_p_source['Adjust Loading Qty'].astype('object'),
                                   df_p_source['Mixed Item Loading Qty'].astype('object')),
        'Cum Sum of Mixed Item FR': np.nan,
        'cntr_seq': np.nan,
        'cntr_block': np.nan,
        'Loading Qty Per Cntr': np.nan,
        'Plan Type': np.nan,
        'Cntr No': np.nan,
        'Plan Group Key': df_p_source['Time.[Week]'].astype(str) + '_' +
                          df_p_source['Location.[Location]'].astype(str) + '_' +
                          df_p_source['To Site'].astype(str) + '_' +
                          df_p_source['Account'].astype(str) + '_' +
                          df_p_source['Ship To'].astype(str)
    })
    df_p_source['cntr_block'] = df_p_source['cntr_block'].astype('object')
    df_p_source['Cntr No'] = df_p_source['Cntr No'].astype('object')

    # 1. Single FTL - Cntr 할당
    list_where_single_ftl = df_p_source['Single Item Cntr Status'] != 'LTL'
    df_single_ftl = fn_container_planning_single(df_p_source[list_where_single_ftl], '0')
    # fn_log_dataframe(df_single_ftl, 'df_single_ftl')

    # 2. Single Complete - Cntr 할당
    list_where_single_complete = ((df_p_source['Single Item Cntr Status'] == 'LTL') &
                                  (df_p_source['Single Item FTL Count'] > 0))
    df_single_complete_with_ltl = fn_container_planning_single(df_p_source[list_where_single_complete], '1')
    # fn_log_dataframe(df_single_complete_with_ltl, 'df_single_complete_with_ltl')
    # Single Complete 대상 Row 중 Container Full 된 행만 추출
    df_single_complete = df_single_complete_with_ltl[df_single_complete_with_ltl['Plan Type'] == '02.SC'].copy(
        deep=True)
    # fn_log_dataframe(df_single_complete, 'df_single_complete')
    # Single Complete 대상 Row 중 Container Full이 아닌 잔여 분량에 대한 행만 추출
    df_single_complete_ltl = df_single_complete_with_ltl[df_single_complete_with_ltl['Plan Type'].isna()].copy(
        deep=True)
    fn_log_dataframe(df_single_complete_ltl, 'df_single_complete_ltl')
    # Single FTL도 아니고, Single Complete 대상도 아닌 Single 기준 LTL 행만 추출
    list_where_single_ltl = ((df_p_source['Single Item Cntr Status'] == 'LTL') &
                             (df_p_source['Single Item FTL Count'] == 0))
    df_single_ltl = df_p_source[list_where_single_ltl].copy(deep=True)
    # fn_log_dataframe(df_single_ltl, 'df_single_ltl')
    # Single Complete 처리에서 Split된 잔여 분량 행 + Single 기준 Container 대수를 1대도 채우지 못한 LTL 분량 행을 concat
    df_single_ltl_all = pd.concat([df_single_complete_ltl, df_single_ltl])
    # fn_log_dataframe(df_single_ltl_all, 'df_single_ltl_all')

    # 3. Mixed FTL - Cntr 할당
    list_where_mixed_ftl = ((df_single_ltl_all['Mixed Item Cntr Status'] != 'LTL') &
                            (df_single_ltl_all['Plan Type'].isna()))
    df_mixed_ftl = df_single_ltl_all[list_where_mixed_ftl].copy(deep=True)
    # fn_log_dataframe(df_mixed_ftl, 'df_mixed_ftl_before')
    df_mixed_ftl = (
        df_mixed_ftl.groupby(by='Last Mix Group').apply(lambda group: fn_container_planning_mixed(group, '0')))
    # fn_log_dataframe(df_mixed_ftl, 'df_mixed_ftl')

    # 4. Mixed LTL - Cntr 할당
    # Simulation 로직에서 Adjust 결과로 Cut되어 0이 된 경우는 Cntr Planning에서 제외한다.
    list_where_no_cntr_planning = ((df_single_ltl_all['Mixed Item Cntr Status'] == 'LTL') &
                                   (df_single_ltl_all['Plan Type'].isna()) &
                                   (df_single_ltl_all['Adjust Loading Qty'].notna()) &
                                   (df_single_ltl_all['Adjust Loading Qty'] == 0))
    # Cntr Planning 작업 유형을 NP(No Planning)로 지정한다.
    df_single_ltl_all.loc[list_where_no_cntr_planning, 'Plan Type'] = '05.NP'
    df_no_container_planning = df_single_ltl_all[df_single_ltl_all['Plan Type'] == '05.NP'].copy(deep=True)
    # fn_log_dataframe(df_no_container_planning, 'df_no_container_planning')
    # fn_log_dataframe(df_single_ltl_all, 'df_single_ltl_all')
    # 잔여 대상 전체를 처리한다. - Simulation 처리 시 Adjust 로직에서 기준으로 삼은 마지막 그룹을 기준으로 처리한다.
    df_single_ltl_all = df_single_ltl_all.reset_index(drop=True)
    list_where_mixed_ltl = ((df_single_ltl_all['Mixed Item Cntr Status'] == 'LTL') &
                            (df_single_ltl_all['Plan Type'].isna()))
    df_mixed_ltl = df_single_ltl_all.loc[list_where_mixed_ltl].copy(deep=True)
    df_mixed_ltl = (
        df_mixed_ltl.groupby(by='Last Mix Group').apply(
            lambda group: fn_container_planning_mixed(group, '1')))

    # 컨테이너 할당 결과를 모두 concat
    df_concat = pd.concat(
        [df_single_ftl, df_single_complete, df_mixed_ftl, df_mixed_ltl, df_no_container_planning],
        ignore_index=True)

    # 컨테이너 넘버링
    df_return = fn_cntr_numbering_main(df_concat)
    df_return['Last Loading Qty'] = df_return['Split Qty List']

    # Seq.[Seq] 순서로 정렬
    df_return = df_return.sort_values(by=['Seq.[Seq]'], ascending=True).copy(deep=True)
    df_return['Inx'] = df_return.reset_index(drop=True).index

    return df_return


@_decoration_
def fn_output_formatter_container_plan(df_p_source: pd.DataFrame, df_p_match: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    df_match = df_p_match[['Inx', 'Match Line']].copy(deep=True)

    df_return = pd.merge(df_p_source, df_match, on=['Inx'], how='left')

    df_return = df_return.assign(**{
        'Version.[Version Name]': np.nan,
        'Sub Location.[Sub Location]': df_return['Location.[Location]'],
        'Location.[Location]': df_return['To Site'],
        'Sales Domain.[Ship To]': df_return['Account'],
        'Seq.[Seq]': np.nan,
        'Time.[Week]': df_return['Time.[Week]'],
        'Item.[Item]': df_return['Item'],
        'Loading Dir Cntr Plan_Ship To': df_return['Ship To'],
        'Loading Dir Cntr Plan_Loading Status': df_return['Mixed Item Cntr Status'],
        'Loading Dir Cntr Plan_Remark': np.nan,
        'Loading Dir Cntr Plan_Loading Qty': df_return['Last Loading Qty'],
        'Loading Dir Cntr Plan_Group Id': df_return['Plan Group Key'],
        'Loading Dir Cntr Plan_Cntr No': df_return['Cntr No'],
        'Loading Dir Cntr Plan_Match Line': df_return['Match Line']
    })
    df_return['Version.[Version Name]'] = Param_OUT_VERSION
    df_return['Seq.[Seq]'] = np.arange(1, len(df_return) + 1)

    df_return = df_return[[
        'Version.[Version Name]',
        'Seq.[Seq]',
        'Time.[Week]',
        'Sub Location.[Sub Location]',
        'Location.[Location]',
        'Sales Domain.[Ship To]',
        'Item.[Item]',
        'Loading Dir Cntr Plan_Ship To',
        'Loading Dir Cntr Plan_Loading Status',
        'Loading Dir Cntr Plan_Remark',
        'Loading Dir Cntr Plan_Loading Qty',
        'Loading Dir Cntr Plan_Group Id',
        'Loading Dir Cntr Plan_Cntr No',
        'Loading Dir Cntr Plan_Match Line'
    ]]

    return df_return


def fn_assign_match_line(group: pd.DataFrame) -> pd.DataFrame:
    """
        CNTR Planning Table 에서 해당 경로에 해당하는 Order Table 탐색 후 "Loading Qty - UnAssinged Qty" 의
        Gap 이 가장 적은 라인에 Matching
        ex) CNTR Table 상 5번 라인의 경우 Order Table 상 8번과 11번에 해당하며
           그 중 Gap 이 적은 8번 라인 선택
      * Unassinged Qty 경우 [Check Qty - Matched 수량의 Sum] 로 계산
    :param group: grouping 된 CNTR Planning Table
    :return: DataFrame
    """
    # 테이블 복사
    group_df = group.copy()

    # KEY 추출
    str_key = group_df.iloc[0]['Aggr Grouping Key']

    # Order Table내 같은 KEY 대상 추출
    group_df_origin = df_in_LoadingDirOrderMgmt[df_in_LoadingDirOrderMgmt['Aggr Grouping Key'] == str_key]

    # 1) Order Table 건수가 1건이면 해당 Seq → Match Line 반영
    # 2) Order Table의 UnAssigned(초기 Chk Qty 복사) 와 Planning Table의 Loading Qty 의 Gap을 찾아
    #    Gap이 적은 Order Table의 Seq → Match Line 반영
    ####################################################################################################################
    # EX) 같은 Aggr Grouping Key 일때
    # group_df_origin                                             group_df
    # Seq   | Chk Qty  | UnAssigned                               index | Last Loading Qty | Match Line
    # 11    |   100    | 100  → -5                                  1   | 105              |  11
    # 12    |    10    |  10  → -5                                  2   |  55              |  15
    # 13    |    20    |  20                                        3   |  7               |  14
    # 14    |     5    |   5  → -2  → -5                            4   |  3               |  14
    # 15    |    50    |  50  → -5                                  5   |  15              |  12
    ####################################################################################################################

    # Chk Qty 를 UnAssigned 칼럼으로 복사 후 진행
    group_df_origin['UnAssigned'] = group_df_origin['Chk Qty']
    # Match Line 초기화
    group_df['Match Line'] = np.nan

    if len(group_df_origin) == 1:
        group_df['Match Line'] = group_df_origin.iloc[0]['Seq.[Seq]']
    elif len(group_df_origin) > 1:
        for i in range(len(group_df)):
            # gap을 찾아서 Chk Qty Gap에 절대값 반영
            num_gap = group_df_origin['UnAssigned'] - group_df.iloc[i]['Last Loading Qty']
            group_df_origin['Chk Qty Gap'] = abs(num_gap)
            # Chk Qty Gap의 최소값인 idx 찾기
            idx_min_gap = group_df_origin['Chk Qty Gap'].idxmin()
            # idx_min_gap의 Seq → Match Line 반영
            group_df.loc[group_df.index[i], 'Match Line'] = group_df_origin.loc[idx_min_gap, 'Seq.[Seq]']
            # Match Line 을 반영한 idx값의 UnAssigned는 할당된 Last Loading Qty를 빼줌(gap을 UnAssigned에 반영)
            group_df_origin.loc[idx_min_gap, 'UnAssigned'] -= group_df.iloc[i]['Last Loading Qty']

    return group_df


@_decoration_
def fn_assign(df_p_source: pd.DataFrame, df_p_adjust: pd.DataFrame) -> tuple:
    """
    CNTR Planning Qty. ▶ Order line 별 할당 Logic
    1. Order Table 상 Loading Status "FTL" 일 경우 변경 없이 Check Qty 그대로 Loaing Qty 배정
    2. Loading Status LTL Loading Qty 큰 순으로 정렬
    3. CNTR Planning Table 에서 해당 경로에 해당하는 Order Table 탐색 후 "Loading Qty - UnAssinged Qty" 의
       Gap 이 가장 적은 라인에 Matching
       ex) CNTR Table 상 5번 라인의 경우 Order Table 상 8번과 11번에 해당하며
          그 중 Gap 이 적은 8번 라인 선택
      * Unassinged Qty 경우 [Check Qty - Matched 수량의 Sum] 로 계산
    4. 라인 Matching 후 Unassigned Qty Update
    5. CNTR Planning Table 상 모든 LTL 에 대한 Matching 작업 후 [Check Qty - Unassinged Qty] 통해
       Order Table 상 Loading Qty 계산
    6.df_assign_plan 에 아래 항목 추가
    - Measure.[Loading Dir Order Mgmt_Item FR]
    - Measure.[Loading Dir Order Mgmt_CNTR FR]
    - Measure.[Loading Dir Order Mgmt_Diff]
    - Measure.[Loading Dir Order Mgmt_LTL Qty]
    - Measure.[Loading Dir Order Mgmt_Last Mix Group]
    - Measure.[Loading Dir Order Mgmt_Loading Qty]
    - Measure.[Loading Dir Order Mgmt_Loading Status]
    - Measure.[Loading Dir Order Mgmt_UnAssinged Qty]

    :param df_p_source: df_container_plan
    :param df_p_adjust: df_adjust

    :return: tuple
    """

    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return, df_return

    # 데이터 프레임 복사
    df_return_container = df_p_source.copy(deep=True)

    # assign 대상
    # Match Line : KEY(Aggr Grouping Key) 기준으로 Loading Qty Per Cntr 과 원본 Chk Qty 차이가 적은 Seq 매핑
    # assign 대상을 추출 하여 Match Line 을 찾는다.
    # 1.assign 대상 : LTL + container planning 대상
    df_return_container['Last Loading Qty'] = df_return_container['Loading Qty Per Cntr']
    list_where_target = df_return_container['Plan Type'] != '05.NP'
    list_where_ltl = df_return_container['Mixed Item Cntr Status'] == 'LTL'
    list_where = list_where_ltl & list_where_target
    # 2.Loading Status LTL Loading Qty 큰 순으로 정렬
    df_return_ltl = df_return_container[list_where].sort_values(by=['Last Loading Qty'], ascending=[False])

    if len(df_return_ltl) > 0:
        # 3.Match Line 찾기
        df_return = (
            df_return_ltl.groupby('Aggr Grouping Key').apply(fn_assign_match_line)
            .reset_index(drop=True)
            .sort_values(by=['Last Loading Qty', 'Aggr Grouping Key'], ascending=[False, True])
        )

        df_retun_cntr = df_return.copy(deep=True)

        # 4.Match Line 별 SumQty 생성
        df_return_match = df_return.groupby('Match Line').agg({'Last Loading Qty': 'sum'}).reset_index()

        # 5.S/O INPUT 테이블에 Loading Qty 칼럼 추가
        df_return = (
            df_in_LoadingDirOrderMgmt
            .merge(df_return_match, left_on='Seq.[Seq]', right_on='Match Line', how='left', indicator=True)
        )

        # 6.container Planning LTL 대상 여부
        df_return['Is Container Planning'] = 'N'
        list_where = df_return['_merge'] == 'both'
        df_return.loc[list_where, 'Is Container Planning'] = 'Y'  # container planning 중 LTL인건

    else:
        # 모두 FTL일 경우 df_return은 mgmt, df_return_cntr은 df_return_container를 copy한다.
        df_return = df_in_LoadingDirOrderMgmt.copy(deep=True)
        df_return['Match Line'] = np.nan
        df_return['Last Loading Qty'] = 0
        df_return['Is Container Planning'] = 'N'
        df_retun_cntr = df_return_container.copy(deep=True)
        df_retun_cntr['Match Line'] = np.nan

    # df_return 칼럼 생성 : df_adjust 와 merge (aggr 값 반영)
    # 1) row별 생성 : UnAssinged Qty, Loading Qty, Diff, Item FR
    # 2) aggr 값 반영 : CNTR FR, Last Mix Group, Loading Status
    df_p_adjust = df_p_adjust[[
        'Aggr Grouping Key', 'Single Item FR', 'Single Item Cntr Status', 'Single Item FTL Count Aggr',
        'Mixed Item FR', 'Mixed Item Cntr FR', 'Mixed Item Cntr Status',
        'Last Mix Group', 'Adjust Loading Qty Sum FR', 'Diff'
    ]]

    df_return = df_return.merge(df_p_adjust, how='left', on='Aggr Grouping Key')
    # Container planning에 없으나, LTL 이면 Last Loading Qty 0
    list_where_container_planning_is = df_return['Is Container Planning'] == 'Y'
    list_where_loading_status = df_return['Mixed Item Cntr Status'] == 'LTL'
    list_where = ~list_where_container_planning_is & list_where_loading_status
    df_return.loc[list_where, 'Last Loading Qty'] = 0
    # Order Table 상 Loading Status "Single FTL" 일 경우 변경 없이 Check Qty 그대로 Loading Qty 배정 이 되야 하고,
    # Mixed FTL 일 경우 보정된 Qty 가 반영 되면 됩니다.
    # : Mixed FTL의 경우 Chk Qty + Diff(Multiple 보정, 첫번째 row에만 반영)
    df_return['Diff Index'] = df_return.groupby('Aggr Grouping Key').cumcount() + 1
    df_return.loc[df_return['Diff Index'] != 1, 'Diff'] = 0
    df_return['Last Loading Qty'] = np.where(
        df_return['Single Item Cntr Status'] != 'LTL',
        df_return['Chk Qty'],
        np.where(
            df_return['Mixed Item Cntr Status'] != 'LTL',
            df_return['Chk Qty'] + df_return['Diff'],
            df_return['Last Loading Qty']
        )
    )

    # 7.UnAssinged Qty, Loading Qty, Diff, Item FR 칼럼 생성 (row 별로 생성)
    df_return['UnAssinged Qty'] = df_return['Chk Qty'] - df_return['Last Loading Qty']
    df_return['Loading Qty'] = df_return['Last Loading Qty']
    df_return['Diff'] = df_return['Last Loading Qty'] - df_return['Chk Qty']

    # Item FR : LastLoadingQty/MLQty (row별 생성)
    df_return['Item FR'] = np.where(
        df_return['Max Load Qty'] == 0,
        0,
        df_return['Loading Qty'] / df_return['Max Load Qty']
    )

    # CNTR FR, Last Mix Group, Loading Status (aggr 값 반영)
    df_return['CNTR FR'] = np.where(
        df_return['Single Item Cntr Status'] != 'LTL',
        df_return['Single Item FR'],
        df_return['Single Item FTL Count Aggr'] + np.where(
            df_return['Mixed Item Cntr Status'] != 'LTL',
            df_return['Mixed Item Cntr FR'],
            df_return['Adjust Loading Qty Sum FR']
        )
    )

    df_return['Loading Status'] = df_return['Mixed Item Cntr Status']

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return['CNTR FR'] = df_return['CNTR FR'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)

    # 칼럼 정리
    return df_return, df_retun_cntr


@_decoration_
def fn_output_formatter_mix(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 8. Mgmt 메저그룹 칼럼 원복
    :param df_p_source: df_mgmtCal_mixItem_arrange
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

    # 데이터 프레임 복사
    df_return = df_p_source.copy(deep=True)

    # Object Null인 행에 대해서 None 처리 -> None이 아닌 경우 o9 서버에서 오류 발생함.
    df_return.loc[df_return['To Site'].isna(), 'To Site'] = None
    df_return.loc[df_return['Account'].isna(), 'Account'] = None
    df_return.loc[df_return['Ship To'].isna(), 'Ship To'] = None
    df_return.loc[df_return['Item'].isna(), 'Item'] = None
    df_return.loc[df_return['Project'].isna(), 'Project'] = None
    df_return.loc[df_return['Product Group'].isna(), 'Product Group'] = None
    df_return.loc[df_return['Product'].isna(), 'Product'] = None
    df_return.loc[df_return['Shipment Type'].isna(), 'Shipment Type'] = None
    df_return.loc[df_return['Loading Type'].isna(), 'Loading Type'] = None
    df_return.loc[df_return['Cntr Type'].isna(), 'Cntr Type'] = None
    df_return.loc[df_return['Loading Status'].isna(), 'Loading Status'] = None
    df_return.loc[df_return['SO Item'].isna(), 'SO Item'] = None

    # Chk Flag null 로 업데이트 ( 사용자 가 chk한 값 원복 )
    list_where = df_return['Simulated By'] == Param_User_Id
    df_return.loc[list_where, 'Chk Flag'] = np.nan

    df_return = df_return.rename(columns={
        'Time.[Week]': 'Adj Prod Week',
        'Location.[Location]': 'Sub Location.[Sub Location]'
    })
    df_return = df_return.rename(columns={
        'To Site': 'Location.[Location]',
        'Account': 'Sales Domain.[Ship To]',
        'Org_Time.[Week]': 'Time.[Week]',
        'Item': 'Item.[Item]',
        'Product Group': 'Item.[Product Group]',
        'Product': 'Item.[Product]',
        'Project': 'Item.[Project]',
        'Shipment Type': 'Location.[Shipment Type]'
    })
    fn_log_dataframe(df_return, 'df_return')

    # 칼럼 정리 ( Measure 명 원복 )
    list_grain_col = ['Version.[Version Name]', 'Seq.[Seq]', 'Time.[Week]', 'Sub Location.[Sub Location]',
                      'Location.[Location]', 'Sales Domain.[Ship To]', 'Item.[Item]']
    list_measure_col = [
        'SO Item', 'Ship To', 'Sales Order', 'Ship To Name', 'Adj Prod Week', 'Chk Flag',
        'Cntr Type', 'Loading Type', 'Item FR', 'CNTR FR', 'Loading Status',
        'Chk Qty', 'Loading Qty', 'Origin Qty', 'UnAssinged Qty', 'Diff', 'Last Mix Group'
    ]

    # 칼럼 정리
    list_columns_origin = list_grain_col + list_measure_col

    df_return = df_return[list_columns_origin]

    # 메저 칼럼 원래 명으로 원복
    str_pre_fix = "Loading Dir Order Mgmt_"

    list_columns_new = []
    for col in list_measure_col:
        new_col = str_pre_fix + col
        list_columns_new.append(new_col)

    list_grain_col.extend(list_columns_new)

    df_return.columns = list_grain_col

    # 결과 리턴
    return df_return


@_decoration_
def fn_output_formatter_aggregation(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 데이터 프레임 복사
    df_return = df_p_source.copy(deep=True)

    # Object Null인 행에 대해서 None 처리 -> None이 아닌 경우 o9 서버에서 오류 발생함.
    df_return.loc[df_return['To Site'].isna(), 'To Site'] = None
    df_return.loc[df_return['Account'].isna(), 'Account'] = None
    df_return.loc[df_return['Ship To'].isna(), 'Ship To'] = None
    df_return.loc[df_return['Ship To Name'].isna(), 'Ship To Name'] = None
    df_return.loc[df_return['Item'].isna(), 'Item'] = None
    df_return.loc[df_return['Project'].isna(), 'Project'] = None
    df_return.loc[df_return['Product Group'].isna(), 'Product Group'] = None
    df_return.loc[df_return['Product'].isna(), 'Product'] = None
    df_return.loc[df_return['Shipment Type'].isna(), 'Shipment Type'] = None
    df_return.loc[df_return['Loading Type'].isna(), 'Loading Type'] = None
    df_return.loc[df_return['Cntr Type'].isna(), 'Cntr Type'] = None
    df_return.loc[df_return['Single Item Cntr Status'].isna(), 'Single Item Cntr Status'] = None
    df_return.loc[df_return['1st Mix Group'].isna(), '1st Mix Group'] = None
    df_return.loc[df_return['1st Mix Group FTL Chk'].isna(), '1st Mix Group FTL Chk'] = None
    df_return.loc[df_return['2nd Mix Group'].isna(), '2nd Mix Group'] = None
    df_return.loc[df_return['2nd Mix Group FTL Chk'].isna(), '2nd Mix Group FTL Chk'] = None
    df_return.loc[df_return['3rd Mix Group'].isna(), '3rd Mix Group'] = None
    df_return.loc[df_return['3rd Mix Group FTL Chk'].isna(), '3rd Mix Group FTL Chk'] = None
    df_return.loc[df_return['Adjust LTL Group'].isna(), 'Adjust LTL Group'] = None
    df_return.loc[df_return['Adjust Cut Add'].isna(), 'Adjust Cut Add'] = None
    df_return.loc[df_return['Mixed Item Cntr Status'].isna(), 'Mixed Item Cntr Status'] = None
    df_return.loc[df_return['Last Mix Group'].isna(), 'Last Mix Group'] = None

    df_return = df_return.rename(columns={
        'To Site': 'Location.[Location]',
        'Location.[Location]': 'Sub Location.[Sub Location]',
        'Account': 'Sales Domain.[Ship To]',
        'Item': 'Item.[Item]',
        'Product Group': 'Item.[Product Group]',
        'Product': 'Item.[Product]',
        'Project': 'Item.[Project]',
        'Shipment Type': 'Location.[Shipment Type]',
        'Chk Qty': 'Aggr Chk Qty'
    })

    df_return['Adjust Option1'] = Param_Adjust_Option1
    df_return['Adjust Option2'] = Param_Adjust_Option2
    df_return['SKU Constraints'] = 'NoneSKU'

    # 칼럼 정리 ( Measure 명 원복 )
    list_grain_col = ['Version.[Version Name]', 'Seq.[Seq]', 'Time.[Week]', 'Sub Location.[Sub Location]',
                      'Location.[Location]', 'Sales Domain.[Ship To]', 'Item.[Item]']

    list_measure_mgmt_col = [
        'Ship To', 'Ship To Name',
        'Cntr Type', 'Loading Type',
        'Single Item Cntr Status', 'Single Item Complete Qty', 'Single Item FR', 'Single Item FTL Count',
        'Single Item Mod FR', 'Single Item Quotient', 'Single Item Rest FR', 'Single Item Rest Qty',
        'Single Item SKU Count',
        '1st Mix Aggr FR', '1st Mix Aggr Qty', '1st Mix Cntr Per SKU', '1st Mix FTL Chk FR', '1st Mix FTL Cntr',
        '1st Mix FTL Qty', '1st Mix Group', '1st Mix Group FTL Chk', '1st Mix Mod FR', '1st Mix Quotient',
        '1st Mix Rest FR',
        '2nd Mix Aggr FR', '2nd Mix Aggr Qty', '2nd Mix Cntr Per SKU', '2nd Mix FTL Chk FR', '2nd Mix FTL Cntr',
        '2nd Mix FTL Qty', '2nd Mix Group', '2nd Mix Group FTL Chk', '2nd Mix Mod FR', '2nd Mix Quotient',
        '2nd Mix Rest FR',
        '3rd Mix Aggr FR', '3rd Mix Aggr Qty', '3rd Mix Cntr Per SKU', '3rd Mix FTL Chk FR', '3rd Mix FTL Cntr',
        '3rd Mix FTL Qty', '3rd Mix Group', '3rd Mix Group FTL Chk', '3rd Mix Mod FR', '3rd Mix Quotient',
        '3rd Mix Rest FR',
        'Adjust Add Cnt', 'Adjust Add Qty', 'Adjust Cut Add', 'Adjust Cut Cnt', 'Adjust Cut Qty', 'Adjust Diff Qty',
        'Adjust FR', 'Adjust FTL Cntr', 'Adjust LTL Group', 'Adjust LTL Qty', 'Adjust LTL Sum FR', 'Adjust Loading Qty',
        'Adjust Loading Qty FR', 'Adjust Loading Qty Sum FR', 'Adjust MOD', 'Adjust MOD FR', 'Adjust Multiple',
        'Adjust Sum FR',
        'Adjust Option1', 'Adjust Option2', 'SKU Constraints',
        'Aggr Chk Qty', 'Diff', 'Last LTL Qty', 'Last Loading Qty',
        'Last Mix Group', 'Mixed Item Cntr FR', 'Mixed Item Cntr Status', 'Mixed Item FR', 'Mixed Item Loading Qty'
    ]

    list_measure_cal_col = [
        '1st Mix', '2nd Mix', '3rd Mix', 'Item Depth', 'Item Height', 'Item Mix Group', 'Item Width', 'JIG', 'JIG Line',
        'Line', 'Max Load Qty', 'Min Qty', 'Mix Cut Add', 'Mix FR Type', 'Mix Max FR', 'Mix Min FR', 'Multiple',
        'Profit Grade', 'Profit Grade Priority', 'SKU Per Cntr', 'Single Cut Add', 'Single FR Type', 'Single Max FR',
        'Single Max FTL', 'Single Min FR', 'Single Min FTL'
    ]

    # 칼럼 정리
    list_columns_origin = list_grain_col + list_measure_mgmt_col + list_measure_cal_col

    df_return = df_return[list_columns_origin].copy(deep=True)

    # 메저 칼럼 원래 명으로 원복
    str_mgmt_pre_fix = "Loading Dir Order Mgmt Aggr_"
    str_cal_pre_fix = "Loading Dir Order Cal Aggr_"

    list_columns_new = []
    # Mgmt
    for col in list_measure_mgmt_col:
        new_col = str_mgmt_pre_fix + col
        list_columns_new.append(new_col)

    # Cal
    for col in list_measure_cal_col:
        new_col = str_cal_pre_fix + col
        list_columns_new.append(new_col)

    list_grain_col.extend(list_columns_new)

    df_return.columns = list_grain_col
    # Seq 채번 확인해야함.(cleansing 기준과 동일)
    df_return['Seq.[Seq]'] = np.arange(1, len(df_return) + 1)

    return df_return


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
    out_ContainerPlan = pd.DataFrame()
    out_LoadingDirOrderAggr = pd.DataFrame()
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
            Param_Adjust_Option1 = 'MAX'
            Param_Adjust_Option2 = 'Max Profit'
            Param_User_Name = 'woomi01.lee@partner.samsung.com'

            in_LoadingDirOrderMgmt = pd.read_csv(str_input_dir + "/in_LoadingDirOrderMgmt.csv", encoding="UTF8")
            in_Container = pd.read_csv(str_input_dir + "/in_Container.csv", encoding="UTF8")

            # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'

        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        if Param_Adjust_Option1 is None or Param_Adjust_Option1.strip() == '':
            Param_Adjust_Option1 = 'MIN'

        if Param_Adjust_Option2 is None or Param_Adjust_Option2.strip() == '':
            Param_Adjust_Option2 = 'Min Item Change'

        if Param_User_Name is None or Param_User_Name.strip() == '':
            Param_UserName = 'woomi02.lee@partner.samsung.com'

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Adjust_Option1 : {Param_Adjust_Option1}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Adjust_Option2 : {Param_Adjust_Option2}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_User_Name : {Param_User_Name}', p_log_level=LOG_LEVEL.debug())

        # 입력 테이블 점검 및 로그
        # session 사용자
        Param_User_Id = Param_User_Name.split('@')[0]

        fn_check_input_table(in_LoadingDirOrderMgmt, 'in_LoadingDirOrderMgmt', '0')
        fn_check_input_table(in_Container, 'in_Container', '0')

        ################################################################################################################
        # 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 작업 진행함.
        ################################################################################################################
        # 선처리 작업
        dict_log = {
            'p_step_no': 10,
            'p_step_desc': '전처리(in_LoadingDirOrderMgmt): 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 '
                           '작업 진행함.',
            'p_df_name': 'df_in_LoadingDirOrderMgmt'
        }
        df_in_LoadingDirOrderMgmt = fn_preprocess(in_LoadingDirOrderMgmt, **dict_log)

        ################################################################################################################
        # STEP 0. Prod Week-From Site-To Site-Account-Ship To-Item을 기준으로 Aggregation
        ################################################################################################################
        dict_log = {
            'p_step_no': 20,
            'p_step_desc': 'STEP 0. Prod Week-From Site-To Site-Account-Ship To-Item을 기준으로 Aggregation',
            'p_df_name': 'df_aggregated_LoadingDirOrderMgmt'
        }
        df_aggregated_LoadingDirOrderMgmt = fn_aggregation(df_in_LoadingDirOrderMgmt, **dict_log)

        ################################################################################################################
        # STEP 1. Mgmt, Container input을 Merge한다.
        ################################################################################################################
        #  MGMT, CONTAINER MERGE
        dict_log = {
            'p_step_no': 100,
            'p_step_desc': 'STEP1. Mgmt, Container input을 Merge한다.',
            'p_df_name': 'df_mgmtCal_Merged'
        }
        df_mgmtCal_Merged = fn_mgmt_merge_cal(df_aggregated_LoadingDirOrderMgmt, in_Container, **dict_log)

        ################################################################################################################
        # STEP 2. Single Loading 계산한다.
        ################################################################################################################
        # Single 계산
        dict_log = {
            'p_step_no': 200,
            'p_step_desc': 'STEP 2. Single Loading 계산한다.',
            'p_df_name': 'df_mgmtCal_singleItem'
        }
        df_mgmtCal_singleItem = fn_mgmt_calculate_single_item(df_mgmtCal_Merged, **dict_log)

        ################################################################################################################
        # STEP 3. Mix Loading 계산한다.
        ################################################################################################################
        # Mix 계산 - 1st
        dict_log = {
            'p_step_no': 310,
            'p_step_desc': 'STEP 3-1. Mix 계산. - 1st',
            'p_df_name': 'df_mgmtCal_mixItem_step_one'
        }
        df_mgmtCal_mixItem_step_one = fn_mgmt_calculate_mix_item(df_mgmtCal_singleItem, '1', **dict_log)

        # Mix 계산 - 2nd
        dict_log = {
            'p_step_no': 320,
            'p_step_desc': 'STEP 3-2. Mix 계산. - 2nd',
            'p_df_name': 'df_mgmtCal_mixItem_step_two'
        }
        df_mgmtCal_mixItem_step_two = fn_mgmt_calculate_mix_item(df_mgmtCal_mixItem_step_one, '2', **dict_log)

        # Mix 계산 - 3rd
        dict_log = {
            'p_step_no': 330,
            'p_step_desc': 'STEP 3-3. Mix 계산. - 3rd',
            'p_df_name': 'df_mgmtCal_mixItem_step_three'
        }
        df_mgmtCal_mixItem_step_three = fn_mgmt_calculate_mix_item(df_mgmtCal_mixItem_step_two, '3', **dict_log)

        ################################################################################################################
        # STEP 4. Mix FTL에 대해서 Multiple 보정하여 최종 칼럼 계산한다.
        ################################################################################################################
        # Mix 최종 칼럼 계산
        dict_log = {
            'p_step_no': 400,
            'p_step_desc': 'Mix FTL에 대해서 Multiple 보정하여 최종 칼럼 계산한다.',
            'p_df_name': 'df_mgmtCal_mixItem_arrange'
        }
        df_mgmtCal_mixItem_arrange = fn_mixed_correct_multiple(df_mgmtCal_mixItem_step_three, **dict_log)

        ################################################################################################################
        # STEP 5. Adjust
        ################################################################################################################
        # Adjust
        dict_log = {
            'p_step_no': 500,
            'p_step_desc': 'STEP 5. Adjust',
            'p_df_name': 'df_adjust'
        }
        df_adjust = fn_adjust(df_mgmtCal_mixItem_arrange, **dict_log)

        ################################################################################################################
        # STEP 6. Container Planning
        ################################################################################################################
        # Container Planning
        dict_log = {
            'p_step_no': 601,
            'p_step_desc': 'STEP 6. Container Planning',
            'p_df_name': 'df_container_plan'
        }
        df_container_plan = fn_container_planning(df_adjust, **dict_log)

        ################################################################################################################
        # STEP 7. Assign the loading qty to the order.
        ################################################################################################################
        # Assign the loading qty to the order.
        df_assign_plan, df_container_plan_match = fn_assign(df_container_plan, df_adjust)
        logger.Step(p_step_no=700,
                    p_step_desc='STEP 7. Assign the loading qty to the order.')
        fn_log_dataframe(df_assign_plan, 'df_assign_plan')
        fn_log_dataframe(df_container_plan_match, 'df_container_plan_match')

        ################################################################################################################
        # STEP 8. format 정리
        ################################################################################################################
        # STEP 8.Mgmt 메저그룹 칼럼 원복
        dict_log = {
            'p_step_no': 801,
            'p_step_desc': 'STEP 8. Mgmt 메저그룹 칼럼 원복',
            'p_df_name': 'out_LoadingDirOrderMgmt'
        }
        out_LoadingDirOrderMgmt = fn_output_formatter_mix(df_assign_plan, **dict_log)

        # STEP 8. Container Planning - Output 정리
        dict_log = {
            'p_step_no': 802,
            'p_step_desc': 'STEP 8. Container Planning - Output 정리',
            'p_df_name': 'out_ContainerPlan'
        }
        out_ContainerPlan = fn_output_formatter_container_plan(df_container_plan, df_container_plan_match, **dict_log)

        # STEP 8. Aggregation - Output 정리
        dict_log = {
            'p_step_no': 803,
            'p_step_desc': 'STEP 8. Aggregation(mgmt, cal) - Output 정리',
            'p_df_name': 'out_LoadingDirOrderAggr'
        }
        out_LoadingDirOrderAggr = fn_output_formatter_aggregation(df_adjust, **dict_log)

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_LoadingDirOrderMgmt = None
            out_ContainerPlan = None
            out_LoadingDirOrderAggr = None
            raise Exception(e)
        else:
            if out_LoadingDirOrderMgmt.empty:
                out_LoadingDirOrderMgmt = fn_set_header()
            if out_ContainerPlan.empty:
                out_ContainerPlan = fn_set_header()
            if out_LoadingDirOrderAggr.empty:
                out_LoadingDirOrderAggr = fn_set_header()
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_LoadingDirOrderMgmt.empty:
            out_LoadingDirOrderMgmt = fn_set_header()
            fn_log_dataframe(out_LoadingDirOrderMgmt, 'out_LoadingDirOrderMgmt')
        if out_ContainerPlan.empty:
            out_ContainerPlan = fn_set_header()
        if out_LoadingDirOrderAggr.empty:
            out_LoadingDirOrderAggr = fn_set_header()
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')
