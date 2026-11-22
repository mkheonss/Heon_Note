"""
* 프로그램명
    - PY_Exp_DeliveryPlan_REG.py

* 내용
    -

* 변경이력
    - 2024.10.11 / Yuntaeun / Create
    - 2024.10.21 / YUN TAE UN / UPDATE
      &CurrentAndFuturePlanningWeeks => [Time].[Week] 변경
    - 2025.04-02 / Yun Tae Un /Modify
     : 현재	04월 02, 2025 08:28
* Script Params
    - Param_OUT_VERSION :

* Input Tables
    - InputGraph :
        Select (
                    [Version].[Version Name]
                    * FROM.[Time].[Week]
                    * TO.[Demand].[DemandID]
                    * TO.[Sales Domain].[Customer Group]
                    * TO.[Time].[Week]
                    * TO.[Location].[Location]
                    * TO.[Item].[Item]
                    * TO.[Demand Type].[Demand Type]
                ) on row
                ,
                (
                    {
                        Edge.[002.001W Solver Outputs Demand Fulfillment Report].[W Demand Fulfillment Quantity]
                    }
                ) on column
        where {
                    RelationshipType.[002.001W Solver Outputs Demand Fulfillment Report]
              };
    - InputMeasure :
        Select (
                    [Version].[Version Name]
                    * [Demand].[DemandID]
                    * [Sales Domain].[Customer Group]
                    * [Time].[Week]
                    * [Location].[Location]
                    * [Item].[Item]
                    * [Demand Type].[Demand Type]
                ) on row
                ,
                (
                    {
                        Measure.[W Demand Quantity]
                        , Measure.[W Demand Priority]
                        , Measure.[Map Original Demand ID]
                    }
                ) on column
        where {
                    Measure.[W Demand Quantity]>0
              };
    - Week_Day
        Select (
                    [Version].[Version Name]
                    * [Time].[Week]
                    * [Time].[Day]
                ) on row
                ,
                (
                    {
                        Measure.[Assortment For Week to First Day]
                    }
                ) on column;

* Output Tables
    - EXP_DELIVERYPLAN:
        Select (
                    [Version].[Version Name]
                    * [Item].[Item]
                    * [Location].[Location]
                    * [Sequence].[Sequence]
                    * [Demand].[DemandID]
                    * [Time].[Day]
                ) on row
                ,
                (
                    {
                        Measure.[Exp Dlv Plan All_Sales order ID] as Transient.SALESORDERID
                        , Measure.[Exp Dlv Plan All_SOLine Num] as Transient.SOLINENUM
                        , Measure.[Exp Dlv Plan All_GBM] as Transient.GBM
                        , Measure.[Exp Dlv Plan All_Qty Open] as Transient.QTYOPEN
                        , Measure.[Exp Dlv Plan All_QTY Planned] as Transient.QTYPLANNED
                        , Measure.[Exp Dlv Plan All_Priority] as Transient.PRIORITY
                        , Measure.[Exp Dlv Plan All_Planned Ship Date] as Transient.PLANNEDSHIPMENTDATE
                    }
                ) on column
        where {
                    isnull(Measure.[Exp Dlv Plan All_Local ID])
              };

* Flow Summary

* Validation :
    존재하지 않으면 Raise Exception

* Execution :
    1. 기존 메저 데이터 삭제(nullify)
    Scope: ([Version].[Version Name].[CWV_MP]);
        Measure.[Exp Dlv Plan All_Sales order ID] =null;
        Measure.[Exp Dlv Plan All_SOLine Num] =null;
        Measure.[Exp Dlv Plan All_GBM] = null;
        Measure.[Exp Dlv Plan All_Qty Open] = null;
        Measure.[Exp Dlv Plan All_QTY Planned] = null;
        Measure.[Exp Dlv Plan All_Priority] = null;
        Measure.[Exp Dlv Plan All_Planned Ship Date] = null;
    end scope;

    2. Plugin Call하여 신규 MG 생성
    EXEC plugin instance [PY_Exp_DeliveryPlan_REG]
        for measures {
                          Measure.[Exp Dlv Plan All_Sales order ID]
                        , Measure.[Exp Dlv Plan All_SOLine Num]
                        , Measure.[Exp Dlv Plan All_GBM]
                        , Measure.[Exp Dlv Plan All_Qty Open]
                        , Measure.[Exp Dlv Plan All_QTY Planned]
                        , Measure.[Exp Dlv Plan All_Priority]
                        , Measure.[Exp Dlv Plan All_Planned Ship Date]
                    }
    using scope ([Version].[Version Name].[CWV_MP] * &PlanningHorizon)
    using arguments {(ExecutionMode, "MediumWeight")
      , (Param_OUT_VERSION, "CWV_MP")
      , (IncludeNullRows, False)
      , (MaxSliceTableCells, 200000000)
      , (MaxConcurrency, 1 )
      , ([FailedExecutionCount], 1)
      , ([FailedExecutionPercent], 0.0)
      , ([ThrowExceptionOnFailure], true)
      , ([Param.o9_sys_log_level], "DEBUG")
      };
"""
import os.path
import pandas as pd
import numpy as np
import traceback
import datetime
import time
from NSCMCommon import NSCMCommon as common
########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_Exp_DeliveryPlan_REG"
str_input_dir = "Input/EXPDeliveryPlan"
str_output_dir = "Output/EXPDeliveryPlan"
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


def fn_set_header() -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """
    df_return = pd.DataFrame(
        {
            'Version.[Version Name]': [], '[Sequence].[Sequence]': [], 'Demand.[DemandID]': [],
            '[Location].[Location]': [], '[Item].[Item]': [], 'Time.[Day]': [],
            'Exp Dlv Plan All_Planned Ship Date': [], 'Exp Dlv Plan All_Qty Open': [],
            'Exp Dlv Plan All_QTY Planned': [], 'Exp Dlv Plan All_Priority': [],
            'Exp Dlv Plan All_GBM': [], 'Exp Dlv Plan All_SOLine Num': [],
            'Exp Dlv Plan All_Local ID': [], 'Exp Dlv Plan All_Sales order ID': []
        }
    )

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()

    # Output 테이블 선언
    EXP_DELIVERYPLAN = pd.DataFrame()
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = ''
            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            InputGraph = pd.read_csv(str_input_dir + "/InputGraph.csv", encoding="UTF8")
            InputMeasure = pd.read_csv(str_input_dir + "/InputMeasure.csv", encoding="UTF8")
            Week_Day = pd.read_csv(str_input_dir + "/Week_Day.csv", encoding="UTF8")

        # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}', p_log_level=LOG_LEVEL.debug())
        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False
        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())

        # 입력 테이블 점검 및 로그
        fn_check_input_table(InputGraph, 'InputGraph', '0')
        fn_check_input_table(InputMeasure, 'InputMeasure', '0')
        fn_check_input_table(Week_Day, 'Week_Day', '0')

        # Start
        # Merge Demand and Priority(Measure) to Fulfillment(Graph)
        InputMeasure.rename(
            columns={
                "Demand.[DemandID]": "to.[Demand].[DemandID]",
                "Sales Domain.[Customer Group]": "to.[Sales Domain].[Customer Group]",
                "Location.[Location]": "to.[Location].[Location]",
                "Item.[Item]": "to.[Item].[Item]",
                "Time.[Week]": "to.[Time].[Week]",
                "Demand Type.[Demand Type]": "to.[Demand Type].[Demand Type]",
            },
            inplace=True,
        )
        EXP_DELIVERYPLAN = pd.merge(InputGraph, InputMeasure, how="outer")
        # Step Log
        logger.Step(p_step_no=101, p_step_desc='Merge Demand and Priority(Measure) to Fulfillment(Graph)')

        # Fill na with 0 for Fully Short & No Plan demands
        # In case the whole Demand is short InputGraph data is missing, insert 0 to DemandFulfilledQty and insert from week to to week
        EXP_DELIVERYPLAN[
            "002.001W Solver Outputs Demand Fulfillment Report.[W Demand Fulfillment Quantity]"
        ].fillna(0, inplace=True)
        EXP_DELIVERYPLAN["from.[Time].[Week]"].fillna(
            EXP_DELIVERYPLAN["to.[Time].[Week]"], inplace=True
        )
        # Step Log
        logger.Step(p_step_no=102, p_step_desc='Fill na with 0 for Fully Short & No Plan demands')

        # Rename
        EXP_DELIVERYPLAN.rename(
            columns={
                "to.[Demand].[DemandID]": "Demand.[DemandID]",
                "to.[Location].[Location]": "[Location].[Location]",
                "to.[Item].[Item]": "[Item].[Item]",
                "from.[Time].[Week]": "Time.[Week]",
                "to.[Time].[Week]": "EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE_Week",
                "002.001W Solver Outputs Demand Fulfillment Report.[W Demand Fulfillment Quantity]": "EXP_DELIVERYPLAN_QTYPLANNED",
                "W Demand Quantity": "EXP_DELIVERYPLAN_QTYOPEN",
                "W Demand Priority": "EXP_DELIVERYPLAN_PRIORITY",
            },
            inplace=True,
        )
        # Step Log
        logger.Step(p_step_no=103, p_step_desc='EXP_DELIVERYPLAN.rename')

        ############### Sunday of the Week ###############
        # EXP_DELIVERYPLAN["EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE"] = pd.to_datetime(
        #     EXP_DELIVERYPLAN["EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE"].apply(
        #         lambda x: str(x) + "-0"
        #     ),
        #     format="%Y%W-%w",
        # ).dt.strftime("%Y-%m-%d")

        # EXP_DELIVERYPLAN["EXP_DELIVERYPLAN_PROMISEDSHIPPINGDATE"] = pd.to_datetime(
        #     EXP_DELIVERYPLAN["EXP_DELIVERYPLAN_PROMISEDSHIPPINGDATE"].apply(
        #         lambda x: str(x) + "-0"
        #     ),
        #     format="%Y%W-%w",
        # ).dt.strftime("%Y-%m-%d")

        # Make SOLEINENUM from DemandID
        EXP_DELIVERYPLAN["Exp Dlv Plan All_Sales order ID"] = EXP_DELIVERYPLAN["Map Original Demand ID"]
        EXP_DELIVERYPLAN["EXP_DELIVERYPLAN_SOLINENUM"] = EXP_DELIVERYPLAN["Map Original Demand ID"].astype(str).apply(lambda x: x[x.rindex("_")+1:] if "_" in x else "")
        # Step Log
        logger.Step(p_step_no=104, p_step_desc='Make SOLEINENUM from DemandID')

        # SELL
        # LDC to LocalID
        EXP_DELIVERYPLAN["EXP_DELIVERYPLAN_LOCALID"] = EXP_DELIVERYPLAN["[Location].[Location]"].apply(
            lambda x: x.split("@")[0] if "@" in x else "")
        # Remove LocalID
        EXP_DELIVERYPLAN["[Location].[Location]"] = EXP_DELIVERYPLAN["[Location].[Location]"].apply(
            lambda x: x.split("@")[-1] if "@" in x else x)
        # Step Log
        logger.Step(p_step_no=105, p_step_desc='LDC to LocalID')

        # Week to First Day
        Week_Day.drop(
            columns=[
                "Version.[Version Name]",
            ],
            inplace=True,
        )
        EXP_DELIVERYPLAN = pd.merge(EXP_DELIVERYPLAN, Week_Day, on="Time.[Week]", how="left")
        Week_Day.rename(
            columns={
                "Time.[Week]": "EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE_Week",
                "Time.[Day]": "EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE",
            },
            inplace=True,
        )
        EXP_DELIVERYPLAN = pd.merge(EXP_DELIVERYPLAN, Week_Day, on="EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE_Week",
                                    how="left")
        # Step Log
        logger.Step(p_step_no=106, p_step_desc='Week to First Day')

        # GBM
        GBMHardCoding = "SHA"
        EXP_DELIVERYPLAN["EXP_DELIVERYPLAN_GBM"] = GBMHardCoding
        # Sequencing
        EXP_DELIVERYPLAN["[Sequence].[Sequence]"] = EXP_DELIVERYPLAN.index
        EXP_DELIVERYPLAN["[Sequence].[Sequence]"] = EXP_DELIVERYPLAN["[Sequence].[Sequence]"].astype(str)
        # Output DF
        EXP_DELIVERYPLAN = EXP_DELIVERYPLAN[
            [
                "Version.[Version Name]",
                "[Sequence].[Sequence]",
                "Demand.[DemandID]",
                "[Location].[Location]",
                "[Item].[Item]",
                "Time.[Day]",
                "EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE",
                "EXP_DELIVERYPLAN_QTYOPEN",
                "EXP_DELIVERYPLAN_QTYPLANNED",
                "EXP_DELIVERYPLAN_PRIORITY",
                "EXP_DELIVERYPLAN_GBM",
                "EXP_DELIVERYPLAN_SOLINENUM",
                "EXP_DELIVERYPLAN_LOCALID",
                "Exp Dlv Plan All_Sales order ID",
            ]
        ]
        # Rename
        EXP_DELIVERYPLAN.rename(
            columns={
                "EXP_DELIVERYPLAN_PLANNEDSHIPMENTDATE": "Exp Dlv Plan All_Planned Ship Date",
                "EXP_DELIVERYPLAN_QTYOPEN": "Exp Dlv Plan All_Qty Open",
                "EXP_DELIVERYPLAN_QTYPLANNED": "Exp Dlv Plan All_QTY Planned",
                "EXP_DELIVERYPLAN_PRIORITY": "Exp Dlv Plan All_Priority",
                "EXP_DELIVERYPLAN_GBM": "Exp Dlv Plan All_GBM",
                "EXP_DELIVERYPLAN_SOLINENUM": "Exp Dlv Plan All_SOLine Num",
                "EXP_DELIVERYPLAN_LOCALID": "Exp Dlv Plan All_Local ID",
            },
            inplace=True,
        )
        # Step log
        logger.Step(p_step_no=900, p_step_desc='PSI_OUTPUT 최종 output 정리')

        # Dataframe 확인 로그
        fn_log_dataframe(EXP_DELIVERYPLAN, 'EXP_DELIVERYPLAN')

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            EXP_DELIVERYPLAN = None
            raise Exception(e)
        else:
            if EXP_DELIVERYPLAN.empty:
                EXP_DELIVERYPLAN = fn_set_header()
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if EXP_DELIVERYPLAN.empty:
            EXP_DELIVERYPLAN = fn_set_header()
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')