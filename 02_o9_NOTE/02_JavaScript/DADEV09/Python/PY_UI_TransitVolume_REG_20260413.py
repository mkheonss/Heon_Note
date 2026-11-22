"""
* 프로그램명
    - PY_UI_TransitVolume_REG

* 내용
    - BOD Sop의 Qty를 기반으로 컨테이너 수량을 계산한다.

* 변경이력
    - 2025.10.23 / Kang Gyeonghun / Create
    - 2025.11.14 / Kang Gyeonghun / Update
      : Flow Summary 기준 Step 4-1부터 추가 구현
    - 2025.12.09 / Kang Gyeonghun / Update
      : 모듈 내 Activity1.Activity1 컬럼 모두 삭제
    - 2025.12.19 / Kang Gyeonghun / Update
      : Max Load Qty 사용 부분을 LDM Qty로 변경
    - 2025.12.26 / Kang Gyeonghun / Update
      : "BOD Sop" Measrue Group을 "SOP W"로 변경
      : 변경된 MG를 in_SOPW로 받은 후, 기존 in_BODSop으로 빈프레임만 만든 DF에 복사하여 로직 진행하도록 변경
    - 2026.01.02 / Kang Gyeonghun / Update
      : in_LoadingMethodFromSite IBPL 조건 삭제(Measure.[Loading Method From Site_Mix FR Type] == "LDM")
    - 2026.01.22 / Kang Gyeonghun / Update
      : Step 6-5 변경: View Code가 "& Baseline"이면 Transit Volume W_Capa에 BOD Port W_Capa Qty를 넣음.
      : 수정 전은 View Cope & 앞 코드에 따라 값을 다르게 넣었음.
    - 2026.01.28 / Kang Gyeonghun / Update
      : 수식 계산 시 fillna(0) 처리 추가
    - 2026.02.02 / Kang Gyeonghun / Update
      : Transit Volume W_Capa 값 수식 변경
      - BOD Port W_Capa Qty에서 대상 주차의 값을 찾고
        해당 row의 SOP cntr qty/(Logistics Port Route값이 같은 SOP cntr qty를 SUM한 값)
      - input 테이블(in_SOPW) 변경 후 SOP W_SCP Qty + SOP W_Chg Qty로 계산되도록 수정

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는 데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를 결정하는 파라미터

* Input Tables
    - in_SOPW
        Select ([Sub Location].[Sub Location] * [Location].[Location]
             * [Activity2].[Activity2] * [Item].[Item] * [Time].[Week]) on row
             , ({Measure.[SOP W_SCP Qty], Measure.[SOP W_Chg Qty]}) on column
         where {[Version].[Version Name]}
        ;

    - in_LoadingMethodFromSite
        Select ([Sub Location].[Sub Location] * [Shipment Type].[Shipment Type]
             * [Container].[ContainerID] * [Loading Type].[Loading Type]) on row
             , ({ Measure.[Loading Method From Site_Default], Measure.[Loading Method From Site_Mix FR Type]}) on column
         where {[Version].[Version Name]
             , Measure.[Loading Method From Site_Default] == "Y"}
        ;

    - in_LoadingMasterFromSite
        Select ([Sub Location].[Sub Location] * [Item].[Item] * [Container].[ContainerID]
             * [Loading Type].[Loading Type]) on row
             , ({Measure.[Loading Master From Site_CBM], Measure.[Loading Master From Site_Depth]
             , Measure.[Loading Master From Site_Height], Measure.[Loading Master From Site_Width]
             , Measure.[Loading Master From Site_LDM Qty]}) on column
         where {[Version].[Version Name]
             , Measure.[Loading Master From Site_Valid Flag] == "Y"}
        ;

    - in_BODPort
        Select ([Sub Location].[Sub Location] * [Location].[Location] * [Activity2].[Activity2]
             * [Loading Port].[Loading Port] * [Discharge Port].[Discharge Port] * [Dest Port].[Dest Port]) on row
             , ({Measure.[BOD Port_Capa Qty(12W)], Measure.[BOD Port_Capa Qty(4W)], Measure.[BOD Port_Capa Qty(Y-1 M)]
             , Measure.[BOD Port_Capa Qty(Y-1)], Measure.[BOD Port_Ratio(Port / BOD)]
             , Measure.[BOD Port_Ratio(Port per BOD 12W)], Measure.[BOD Port_Ratio(Port per BOD 4W)]
             , Measure.[BOD Port_Ratio(Port per BOD Y-1 M)], Measure.[BOD Port_Ratio(Port per BOD Y-1)]}) on column
         where {[Version].[Version Name], Measure.[BOD Port_Valid Flag] == "Y"}
        ;

    - in_BODPortW
        Select ([Sub Location].[Sub Location] * [Location].[Location] * [Time].[Planning Month] * [Time].[Week]
             * [Activity2].[Activity2] * [Loading Port].[Loading Port] * [Loading Port].[Loading SCM Port]
             * [Loading Port].[Loading Logistics Port] * [Discharge Port].[Discharge Port]
             * [Discharge Port].[Discharge SCM Port] * [Discharge Port].[Discharge Logistics Port]
             * [Dest Port].[Dest Port]) on row
             , ({Measure.[BOD Port W_Capa Qty]}) on column
         where {[Version].[Version Name]}
        ;

    - in_OceanCapaW
        Select ([Time].[Planning Month] * [Loading Port].[Loading Logistics Port]
             * [Discharge Port].[Discharge Logistics Port]) on row
             , ({Measure.[Ocean Capa W_Capa Qty]}) on column
         where {[Version].[Version Name]}
        ;

* Output Tables
    - out_BODSop
        Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location]
             * [Activity2].[Activity2] * [Item].[Item] * [Time].[Week]) on row
             , ({Measure.[BOD Sop_Cntr Type], Measure.[BOD Sop_Loading Type], Measure.[BOD Sop_Max Loading Qty]
             , Measure.[BOD Sop_Scp Qty Sum], Measure.[BOD Sop_Sop Cntr Qty]}) on column
        ;

    - out_TransitVolumeView
        Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location]
             * [Activity2].[Activity2] * [Loading Port].[Loading Port] * [Discharge Port].[Discharge Port]
             * [Dest Port].[Dest Port] * [View Code].[View Code]) on row
             , ({Measure.[Transit Volume_Ratio(Port / BOD)]}) on column
        ;

    - out_TransitVolumeViewW
        Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location]
             * [Activity2].[Activity2] * [Time].[Week] * [Loading Port].[Loading Port]
             * [Discharge Port].[Discharge Port] * [Dest Port].[Dest Port] * [View Code].[View Code]) on row
             , ({Measure.[Transit Volume W_Capa], Measure.[Transit Volume W_SOP CNTR Qty]}) on column
        ;

* Flow Summary
    Step 1. in_DF01(in_BODSop)와 in_DF02(in_LoadingMethodFromSite)를 [Sub Location].[Sub Location] 기준으로 Left Join하여
        df_BODSop_LoadingMethod를 만든다.

    Step 2-1. df_BODSop_LoadingMethod와 in_LoadingMasterFromSite를 [Sub Location].[Sub Location],
        [Container].[ContainerID], [Loading Type].[Loading Type], [Item].[Item]을 기준으로 Left Join하여
        df_BODSop_LoadingMaster_default를 만든다.
    Step 2-2. df_BODSop_LoadingMaster_default에서 M/L Qty가 Null인 데이터에 대해서 in_LoadingMasterFromSite를
        [Sub Location].[Sub Location], [Container].[ContainerID], [Item].[Item]을 기준으로 Left Join하여
        df_BODSop_LoadingMaster를 만들고, [Sub Location].[Sub Location], [Container].[ContainerID],
        [Item].[Item], [Activity2].[Activity2], [Time].[Week]를 기준으로 중복행을 찾아
        첫행만 남기고 삭제하여 df_BODSop_LoadingMaster를 만든다.

    Step 3. df_BODSop_LoadingMaster에서 M/L Qty가 Null이 아닌 행에 대해 Sop Cntr Qty = Scp Qty Sum / ML Qty으로 계산하여
        df_BODSop_Cntr를 만든다. 이 때 동일행의 Cntr Type, Loading Type, Max Loading Qty를 Master 기준으로 채운다.
        이 때 계산 결과의 소숫점은 그대로 반영한다.

    Step 4-1. in_BODPort의 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], [Dest Port].[Dest Port] 기준으로
         각 행마다 아래 View Code가 전체 생성되도록 하여 df_TransitVolumeView를 만든다.
         - Baseline & Baseline
         - Baseline & SOP
         - 4Weeks & Baseline
         - 4Weeks & SOP
         - 12Weeks & Baseline
         - 12Weeks & SOP
         - LY & Baseline
         - LY & SOP
         - SMLY & Baseline
         - SMLY & SOP
    Step 4-2. in_TransitVolumeView와의 View Code에 따라 Transit Volume_Raio(Port / BOD)에 아래와 같은 기준으로 값을 채운다.
        - Baseline & : BOD Port_Ratio(Port / BOD)
        - 4Weeks &   : BOD Port_Ratio(Port per BOD 4W)
        - 12Weeks &  : BOD Port_Ratio(Port per BOD 12W)
        - LY &       : BOD Port_Ratio(Port per BOD Y-1)
        - SMLY &     : BOD Port_Ratio(Port per BOD Y-1 M)

    Step 5-1. df_BODSop_Cntr에서 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        [Time].[Week] 기준으로 "BOD Sop_Sop Cntr Qty"를 Sum을 하여 df_BODSop_CntrSum을 만든다.
    Step 5-2. in_BODPortW의 Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], [Dest Port].[Dest Port], [Time].[Week] 기준으로
        각 행마다 아래 View Code가 전체 생성되도록 하여 df_TransitVolumeViewW를 만든다.
         - Baseline & Baseline
         - Baseline & SOP
         - 4Weeks & Baseline
         - 4Weeks & SOP
         - 12Weeks & Baseline
         - 12Weeks & SOP
         - LY & Baseline
         - LY & SOP
         - SMLY & Baseline
         - SMLY & SOP
    Step 5-3. df_TransitVolumeViewW와 df_BODSop_CntrSum을 [Sub Location].[Sub Location], [Location].[Location],
        [Activity2].[Activity2], [Time].[Week] 기준으로 Left Join 하여 df_TransitVolumeViewW를 만든다.
    Step 5-4. df_TransitVolumeViewW에서
        View Code에 해당하는 BOD Port_Ratio(Step 4-2 기준)를 BOD Sop_Sop Cntr Qty Sum에 곱해준 값을
        Transit Volume W_SOP CNTR Qty에 넣는다.

    Step 6-1. df_TransitVolumeViewW에 in_OceanCapaW를 [Time].[Planning Month], [Loading Port].[Loading SCM Port],
        [Discharge Port].[Discharge SCM Port]를 기준으로 Left Join 하여 df_TransitVolumeViewW_capa를 만든다.
    Step 6-2. df_TransitVolumeViewW_capa에서 [Loading Port].[Loading Logistics Port],
        [Discharge Port].[Discharge Logistics Port]를 기준으로 Transit Volume W_SOP CNTR Qty를 Sum하여
        Transit Volume W_SOP CNTR Qty Sum에 넣는다.
    Step 6-3. df_TransitVolumeViewW_capa에서
        (BOD Port W_Capa Qty에서 대상 주차의 값을 찾고
        해당 row의 SOP cntr qty/(Logistics Port Route값이 같은 SOP cntr qty를 SUM한 값)을
        View Code가 & SOP인 행의 Transit Volume W_Capa에 넣는다.
    Step 6-4. df_TransitVolumeViewW_capa에 in_BODPortW를 [Sub Location].[Sub Location], [Location].[Location],
        [Time].[Week], [Activity2].[Activity2], [Loading Port].[Loading Port], [Discharge Port].[Discharge Port],
        [Dest Port].[Dest Port]를 기준으로 Left Join하여 df_TransitVolumeViewW_port를 만든다.
    Step 6-5. df_TransitVolumeViewW_port에서 View Code & Baseline인 행의 Transit Volume W_Capa에
        아래의 기준으로 BOD Port W_Capa Qty를 넣는다.
        - & Baseline: BOD Port W_Capa Qty

    Step 7-1. Step 3의 df_BODSop_Cntr를 정리하여 out_BODSop을 만든다.
    Step 7-2. Step 4-2의 df_TransitVolumeViewW를 정리하여 out_TransitVolumeView를 만든다.
    Step 7-3. Step 6-5의 df_TransitVolumeViewW_capa를 정리하여 out_TransitVolumeViewW를 만든다.

* Validation :

* Execution :
    EXEC plugin instance [PY_UI_TransitVolume_REG] for measures { [BOD Sop_Sop Cntr Qty] }
    using scope ([Version].[Version Name])
    using arguments {(ExecutionMode, "MediumWeight")
                  , (Param_OUT_VERSION, "CWV_MP")
                  , (Param_Exception_Flag, "N")
                  , (MaxSliceTableCells, 200000000)
                  , (MaxConcurrency, 1)
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
import re
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_TransitVolume_REG"
str_input_dir = "Input/UITransitVolumeREG"
str_output_dir = "Output/UITransitVolumeREG"
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


@_decoration_
def fn_set_header() -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :return: DataFrame
    """
    df_return = pd.DataFrame(
        {
            "Version.[Version Name]": [], "Sub Location].[Sub Location]": [], "Location.[Location]": [],
            "Activity2.[Activity2]": [], "Item.[Item]": [], "Time.[Week]": [],
            "BOD Sop_Cntr Type": [], "BOD Sop_Loading Type": [], "BOD Sop_Max Loading Qty": [],
            "BOD Sop_Scp Qty Sum": [], "BOD Sop_Sop Cntr Qty": [],
        }
    )

    return df_return


@_decoration_
def fn_copy_sop_w_to_bod_sop(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # in_SOPW의 내용을 in_BODSop으로 복사
    df_return = df_return.assign(**{
        "Sub Location.[Sub Location]": df_p_source["Sub Location.[Sub Location]"],
        "Location.[Location]": df_p_source["Location.[Location]"],
        "Activity2.[Activity2]": df_p_source["Activity2.[Activity2]"],
        "Item.[Item]": df_p_source["Item.[Item]"],
        "Time.[Week]": df_p_source["Time.[Week]"],
        "BOD Sop_Cntr Type": None,
        "BOD Sop_Loading Type": None,
        "BOD Sop_Max Loading Qty": None,
        "BOD Sop_Scp Qty Sum": df_p_source["SOP W_SCP Qty"].fillna(0) + df_p_source["SOP W_Chg Qty"].fillna(0),
        "BOD Sop_Sop Cntr Qty": None,
    })

    return df_return


@_decoration_
def fn_rename(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    df_return = df_p_source.rename(
        columns={
            "Activity2.[Activity2]": "Activity2",
            "Container.[ContainerID]": "CntrType",
            "Dest Port.[Dest Port]": "DestPort",
            "Discharge Port.[Discharge Logistics Port]": "DischargeLogisticsPort",
            "Discharge Port.[Discharge Port]": "DischargePort",
            "Discharge Port.[Discharge SCM Port]": "DischargeSCMPort",
            "Item.[Item]": "Item",
            "Loading Port.[Loading Logistics Port]": "LoadingLogisticsPort",
            "Loading Port.[Loading Port]": "LoadingPort",
            "Loading Port.[Loading SCM Port]": "LoadingSCMPort",
            "Loading Type.[Loading Type]": "LoadingType",
            "Location.[Location]": "ToSite",
            "Shipment Type.[Shipment Type]": "ShipmentType",
            "Sub Location.[Sub Location]": "FromSite",
            "Time.[Planning Month]": "PlanningMonth",
            "Time.[Week]": "Week",
            "View Code.[View Code]": "ViewCode",
            "BOD Port W_Capa Qty": "BODPortWCapaQty",
            "BOD Port_Capa Qty(12W)": "BODPortCapaQty(12W)",
            "BOD Port_Capa Qty(4W)": "BODPortCapaQty(4W)",
            "BOD Port_Capa Qty(Y-1 M)": "BODPortCapaQty(Y-1M)",
            "BOD Port_Capa Qty(Y-1)": "BODPortCapaQty(Y-1)",
            "BOD Port_Ratio(Port / BOD)": "BODPortRatio(Port/BOD)",
            "BOD Port_Ratio(Port per BOD 12W)": "BODPortRatio(PortperBOD12W)",
            "BOD Port_Ratio(Port per BOD 4W)": "BODPortRatio(PortperBOD4W)",
            "BOD Port_Ratio(Port per BOD Y-1 M)": "BODPortRatio(PortperBODY-1M)",
            "BOD Port_Ratio(Port per BOD Y-1)": "BODPortRatio(PortperBODY-1)",
            "BOD Sop_Cntr Type": "BODSopCntrType",
            "BOD Sop_Loading Type": "BODSopLoadingType",
            "BOD Sop_Max Loading Qty": "BODSopMaxLoadingQty",
            "BOD Sop_Scp Qty Sum": "BODSopScpQtySum",
            "BOD Sop_Sop Cntr Qty": "BODSopSopCntrQty",
            "Loading Master From Site_CBM": "LoadingMasterFromSiteCBM",
            "Loading Master From Site_Depth": "LoadingMasterFromSiteDepth",
            "Loading Master From Site_Height": "LoadingMasterFromSiteHeight",
            "Loading Master From Site_LDM Qty": "LoadingMasterFromSiteLDMQty",
            "Loading Master From Site_Valid Flag": "LoadingMasterFromSiteValidFlag",
            "Loading Master From Site_Width": "LoadingMasterFromSiteWidth",
            "Loading Method From Site_Default": "LoadingMethodFromSiteDefault",
            "Loading Method From Site_Mix FR Type": "LoadingMethodFromSiteMixFRType",
            "Ocean Capa W_Capa Qty": "OceanCapaWCapaQty",
            "Transit Volume W_Capa": "TransitVolumeWCapa",
            "Transit Volume W_SOP CNTR Qty": "TransitVolumeWSOPCNTRQty",
            "Transit Volume_Ratio(Port / BOD)": "TransitVolumeRatio(Port/BOD)",
        }
    )

    return df_return


@_decoration_
def fn_set_cntr_type_loading_type_to_bod_sop(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # Loading Method에서 BOD Sop으로 데이터 복사
    df_return = df_return.assign(**{
        "BODSopCntrType": df_return["CntrType"],
        "BODSopLoadingType": df_return["LoadingType"]
    })

    return df_return


@_decoration_
def fn_merge(df_p_left: pd.DataFrame, df_p_right: pd.DataFrame,
             str_p_how: str, list_p_left_on: list, list_p_right_on: list) -> pd.DataFrame:
    """
    Step 1. in_DF01(in_BODSop)와 in_DF02(in_LoadingMethodFromSite)를 [Sub Location].[Sub Location] 기준으로 Left Join하여
        df_BODSop_LoadingMethod를 만든다.
    Step 2-1. df_BODSop_LoadingMethod와 in_LoadingMasterFromSite를 [Sub Location].[Sub Location],
        [Container].[ContainerID], [Loading Type].[Loading Type], [Item].[Item]을 기준으로 Left Join하여
        df_BODSop_LoadingMaster_default를 만든다.
    Step 2-2. df_BODSop_LoadingMaster_default에서 M/L Qyt가 Null인 데이터에 대해서 in_LoadingMasterFromSite를
        [Sub Location].[Sub Location], [Container].[ContainerID], [Item].[Item]을 기준으로 Left Join하여
        df_BODSop_LoadingMaster를 만들고
    Step 5-3. df_TransitVolumeViewW_merged와 df_BODSop_CntrSum을 [Sub Location].[Sub Location], [Location].[Location],
        [Activity2].[Activity2], [Time].[Week] 기준으로 Left Join 하여 df_TransitVolumeViewW를 만든다.
    Step 6-1. df_TransitVolumeViewW에 in_OceanCapaW를 [Time].[Planning Month], [Loading Port].[Loading SCM Port],
        [Discharge Port].[Discharge SCM Port]를 기준으로 Left Join 하여 df_TransitVolumeViewW_capa를 만든다.
    Step 6-4. df_TransitVolumeViewW_capa에 in_BODPortW를 [Sub Location].[Sub Location], [Location].[Location],
        [Time].[Week], [Activity2].[Activity2], [Loading Port].[Loading Port], [Discharge Port].[Discharge Port],
        [Dest Port].[Dest Port]를 기준으로 Left Join하여 df_TransitVolumeViewW_port를 만든다.
    :param df_p_left:
    :param df_p_right:
    :param str_p_how:
    :param list_p_left_on:
    :param list_p_right_on:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_left.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_left)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_left

    if df_p_right.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_right)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_left

    df_return = pd.merge(df_p_left, df_p_right, how=str_p_how, left_on=list_p_left_on, right_on=list_p_right_on)

    return df_return


@_decoration_
def fn_loading_master_process(df_p_source: pd.DataFrame, df_p_loading_master: pd.DataFrame) -> pd.DataFrame:
    """
    Step 2-2. df_BODSop_LoadingMaster_default에서 M/L Qyt가 Null인 데이터에 대해서 in_LoadingMasterFromSite를
        [Sub Location].[Sub Location], [Container].[ContainerID], [Item].[Item]을 기준으로 Left Join하여
        df_BODSop_LoadingMaster를 만들고, [Sub Location].[Sub Location], [Container].[ContainerID],
        [Item].[Item], [Activity2].[Activity2], [Time].[Week]를 기준으로 중복행을 찾아
        첫행만 남기고 삭제하여 df_BODSop_LoadingMaster를 만든다.
    :param df_p_source:
    :param df_p_loading_master:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    if df_p_loading_master.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_master)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    if 'LoadingMasterFromSiteMaxLoadQty' not in df_p_source.columns:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터를 처리할 수 없습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # Loading Method에 데이터가 없음
    list_where_loading_method_is_null = (df_p_source['LoadingMethodFromSiteMixFRType'].isnull())
    # Loading Method 기준으로 일치하는 데이터가 없는 경우
    df_loading_method_is_null = df_p_source.loc[list_where_loading_method_is_null].copy(deep=True)
    fn_log_dataframe(df_loading_method_is_null, 'df_loading_method_is_null')
    # Loading Master에 데이터가 없음
    list_where_mlqty_is_null = (df_p_source['LoadingMasterFromSiteMaxLoadQty'].isnull())
    # Loading Method 및 Loading Master 모두에 데이터가 있는 경우
    df_mlqty_is_not_null = (
        df_p_source.loc[~list_where_loading_method_is_null & ~list_where_mlqty_is_null].copy(deep=True))
    # Loading Method 기준으로 데이터가 있지만 Loading Master 기준([Sub Location].[Sub Location], [Container].[ContainerID],
    # [Loading Type].[Loading Type], [Item].[Item])으로 데이터가 없는 경우
    df_mlqty_is_null = df_p_source.loc[~list_where_loading_method_is_null & list_where_mlqty_is_null].copy(deep=True)

    # df_BODSop_LoadingMaster_default에서 M/L Qty가 Null인 데이터에 대해서 in_LoadingMasterFromSite를
    # [Sub Location].[Sub Location], [Container].[ContainerID], [Item].[Item]을 기준으로 Left Join
    df_return = pd.merge(df_mlqty_is_null, df_p_loading_master,
                         how='left',
                         left_on=['FromSite', 'CntrType', 'Item'],
                         right_on=['FromSite', 'CntrType', 'Item'])
    fn_log_dataframe(df_return, 'df_BODSop_LoadingMaster_ndefault')

    # Merge 하지 않은 데이터와 concat
    df_return = pd.concat([df_loading_method_is_null, df_mlqty_is_not_null, df_return], axis=0)
    fn_log_dataframe(df_return, 'df_BODSop_LoadingMaster_ndefault2')
    # [Sub Location].[Sub Location], [Container].[ContainerID], [Item].[Item],
    # [Activity2].[Activity2], [Time].[Week]를 기준으로 중복행을 찾아 첫행만 남기고 삭제
    df_return = df_return.sort_values(by=['FromSite', 'ToSite', 'Activity2', 'Item', 'Week', 'CntrType',
                                          'LoadingType'])
    df_return = (
        df_return.drop_duplicates(subset=['FromSite', 'ToSite', 'Activity2', 'Item', 'Week', 'CntrType',
                                          'LoadingType'], keep='first')
        .reset_index(drop=True)).copy(deep=True)

    return df_return


@_decoration_
def fn_container_calculate(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3. df_BODSop_LoadingMaster에서 M/L Qty가 Null이 아닌 행에 대해 Sop Cntr Qty = Scp Qty Sum / ML Qty으로 계산하여
       df_BODSop_Cntr를 만든다. 이 때 동일행의 Cntr Type, Loading Type, Max Loading Qty를 Master 기준으로 채운다.
       이 때 계산 결과의 소숫점은 그대로 반영한다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    if 'LoadingMasterFromSiteLDMQty' not in df_p_source.columns:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터를 처리할 수 없습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # df_BODSop_LoadingMaster에서 M/L Qty가 Null이 아닌 행에 대해
    list_where_mlqty_is_null = df_p_source['LoadingMasterFromSiteLDMQty'].isnull()
    df_mlqty_is_not_null = df_p_source.loc[~list_where_mlqty_is_null].copy(deep=True)
    df_mlqty_is_null = df_p_source.loc[list_where_mlqty_is_null].copy(deep=True)

    # df_BODSop_LoadingMaster에서 M/L Qty가 Null이 아닌 행에 대해 Sop Cntr Qty = Scp Qty Sum / ML Qty으로 계산하여
    # df_BODSop_Cntr를 만든다. 이 때 동일행의 Cntr Type, Loading Type, Max Loading Qty를 Master 기준으로 채운다.
    df_mlqty_is_not_null['BODSopSopCntrQty'] = (
            df_mlqty_is_not_null['BODSopScpQtySum'].fillna(0) / df_mlqty_is_not_null['LoadingMasterFromSiteLDMQty'].fillna(0))
    df_mlqty_is_not_null['BODSopCntrType'] = df_mlqty_is_not_null['CntrType']
    df_mlqty_is_not_null['BODSopLoadingType'] = df_mlqty_is_not_null['LoadingType']
    df_mlqty_is_not_null['BODSopMaxLoadingQty'] = df_mlqty_is_not_null['LoadingMasterFromSiteLDMQty']

    # M/L Qty가 Null인 데이터와 concat
    df_return = pd.concat([df_mlqty_is_null, df_mlqty_is_not_null], axis=0)

    # 이후 로직 처리에 관련된 컬럼만 남김
    df_return = df_return[['FromSite', 'ToSite', 'Activity2', 'Item', 'Week',
                           'BODSopCntrType', 'BODSopLoadingType', 'BODSopMaxLoadingQty', 'BODSopScpQtySum',
                           'BODSopSopCntrQty']]

    return df_return


@_decoration_
def fn_make_transit_volume(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    Step 4-1. in_BODPort의 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], [Dest Port].[Dest Port] 기준으로
         각 행마다 아래 View Code가 전체 생성되도록 하여 df_TransitVolumeView를 만든다.
         - Baseline & Baseline
         - Baseline & SOP
         - 4Weeks & Baseline
         - 4Weeks & SOP
         - 12Weeks & Baseline
         - 12Weeks & SOP
         - LY & Baseline
         - LY & SOP
         - SMLY & Baseline
         - SMLY & SOP
    Step 5-2. in_BODPortW의 Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], [Dest Port].[Dest Port], [Time].[Week] 기준으로
        각 행마다 아래 View Code가 전체 생성되도록 하여 df_TransitVolumeViewW를 만든다.
         - Baseline & Baseline
         - Baseline & SOP
         - 4Weeks & Baseline
         - 4Weeks & SOP
         - 12Weeks & Baseline
         - 12Weeks & SOP
         - LY & Baseline
         - LY & SOP
         - SMLY & Baseline
         - SMLY & SOP
    :param df_p_source:
    :param str_p_cond:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    list_view_code = ["Baseline & Baseline", "Baseline & SOP", "4Weeks & Baseline", "4Weeks & SOP",
                      "12Weeks & Baseline", "12Weeks & SOP", "LY & Baseline", "LY & SOP", "SMLY & Baseline",
                      "SMLY & SOP"]

    df_return1 = df_p_source.copy(deep=True)
    df_return1["ViewCode"] = list_view_code[0]
    df_return2 = df_p_source.copy(deep=True)
    df_return2["ViewCode"] = list_view_code[1]
    df_return3 = df_p_source.copy(deep=True)
    df_return3["ViewCode"] = list_view_code[2]
    df_return4 = df_p_source.copy(deep=True)
    df_return4["ViewCode"] = list_view_code[3]
    df_return5 = df_p_source.copy(deep=True)
    df_return5["ViewCode"] = list_view_code[4]
    df_return6 = df_p_source.copy(deep=True)
    df_return6["ViewCode"] = list_view_code[5]
    df_return7 = df_p_source.copy(deep=True)
    df_return7["ViewCode"] = list_view_code[6]
    df_return8 = df_p_source.copy(deep=True)
    df_return8["ViewCode"] = list_view_code[7]
    df_return9 = df_p_source.copy(deep=True)
    df_return9["ViewCode"] = list_view_code[8]
    df_return10 = df_p_source.copy(deep=True)
    df_return10["ViewCode"] = list_view_code[9]

    df_return = pd.concat([df_return1, df_return2, df_return3, df_return4, df_return5,
                           df_return6, df_return7, df_return8, df_return9, df_return10], axis=0)
    if str_p_cond == "0":
        df_return["TransitVolumeRatio(Port/BOD)"] = None
    elif str_p_cond == "1":
        df_return["TransitVolumeWCapa"] = None
        df_return["TransitVolumeWSOPCNTRQty"] = None

    return df_return


@_decoration_
def fn_set_transit_volume_ratio_port_per_bod(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4-2. in_TransitVolumeView와의 View Code에 따라 Transit Volume_Ratio(Port / BOD)에 아래와 같은 기준으로 값을 채운다.
        - Baseline & : BOD Port_Ratio(Port / BOD)
        - 4Weeks &   : BOD Port_Ratio(Port per BOD 4W)
        - 12Weeks &  : BOD Port_Ratio(Port per BOD 12W)
        - LY &       : BOD Port_Ratio(Port per BOD Y-1)
        - SMLY &     : BOD Port_Ratio(Port per BOD Y-1 M)
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # Baseline & : BOD Port_Ratio(Port / BOD)
    list_where_baseline = df_return["ViewCode"].str.startswith("Baseline &")
    df_return.loc[list_where_baseline, "TransitVolumeRatio(Port/BOD)"] = (
        df_return.loc[list_where_baseline]["BODPortRatio(Port/BOD)"])
    # 4Weeks & : BOD Port_Ratio(Port per BOD 4W)
    list_where_4weeks = df_return["ViewCode"].str.startswith("4Weeks &")
    df_return.loc[list_where_4weeks, "TransitVolumeRatio(Port/BOD)"] = (
        df_return.loc[list_where_4weeks]["BODPortRatio(PortperBOD4W)"])
    # 12Weeks & : BOD Port_Ratio(Port per BOD 12W)
    list_where_12weeks = df_return["ViewCode"].str.startswith("12Weeks &")
    df_return.loc[list_where_12weeks, "TransitVolumeRatio(Port/BOD)"] = (
        df_return.loc[list_where_12weeks]["BODPortRatio(PortperBOD12W)"])
    # LY & : BOD Port_Ratio(Port per BOD Y-1)
    list_where_ly = df_return["ViewCode"].str.startswith("LY &")
    df_return.loc[list_where_ly, "TransitVolumeRatio(Port/BOD)"] = (
        df_return.loc[list_where_ly]["BODPortRatio(PortperBODY-1)"])
    # SMLY & : BOD Port_Ratio(Port per BOD Y-1 M)
    list_where_smly = df_return["ViewCode"].str.startswith("SMLY &")
    df_return.loc[list_where_smly, "TransitVolumeRatio(Port/BOD)"] = (
        df_return.loc[list_where_smly]["BODPortRatio(PortperBODY-1M)"])

    # df_return = df_return[
    #     ["FromSite", "ToSite", "Activity2", "LoadingPort", "DischargePort", "DestPort", "ViewCode",
    #      "TransitVolumeRatio(Port/BOD)"]]

    return df_return


@_decoration_
def fn_container_sum(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 5-1. df_BODSop_Cntr에서 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        [Time].[Week] 기준으로 "BOD Sop_Sop Cntr Qty"를 Sum을 하여 df_BODSop_CntrSum을 만든다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    df_return = (
        df_p_source.groupby(["FromSite", "ToSite", "Activity2", "Week"]).agg({"BODSopSopCntrQty": "sum"}).reset_index())

    return df_return


@_decoration_
def fn_set_transit_volume_w_sop_cntr_qty(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 5-4. df_TransitVolumeViewW를 만든 후
        View Code에 해당하는 BOD Port_Ratio(Step 4-2 기준)를 BOD Sop_Sop Cntr Qty Sum에 곱해준 값을
        Transit Volume W_SOP CNTR Qty에 넣는다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    df_return["TransitVolumeWSOPCNTRQty"] = (
            df_return["TransitVolumeRatio(Port/BOD)"].fillna(0) * df_return["BODSopSopCntrQty"].fillna(0))

    return df_return


@_decoration_
def fn_container_sum2(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 6-2. df_TransitVolumeViewW_capa에서 [Loading Port].[Loading Logistics Port],
        [Discharge Port].[Discharge Logistics Port]를 기준으로 Transit Volume W_SOP CNTR Qty를 Sum하여
        Transit Volume W_SOP CNTR Qty Sum에 넣는다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # [Loading Port].[Loading Logistics Port], [Discharge Port].[Discharge Logistics Port]를 기준으로
    # Transit Volume W_SOP CNTR Qty를 Sum하여 Transit Volume W_SOP CNTR Qty Sum에 넣는다.
    df_return["TransitVolumeWSOPCNTRQtySum"] = (
        df_return.groupby(by=["Week", "ViewCode", "LoadingLogisticsPort", "DischargeLogisticsPort"])["TransitVolumeWSOPCNTRQty"].
        transform("sum"))

    return df_return


@_decoration_
def fn_set_transit_volume_w_capa(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    Step 6-3. df_TransitVolumeViewW_capa에서
        (BOD Port W_Capa Qty에서 대상 주차의 값을 찾고
        해당 row의 SOP cntr qty/(Logistics Port Route값이 같은 SOP cntr qty를 SUM한 값)을
        View Code가 & SOP인 행의 Transit Volume W_Capa에 넣는다.
    Step 6-5. df_TransitVolumeViewW_port에서 View Code & Baseline인 행의 Transit Volume W_Capa에
        아래의 기준으로 BOD Port W_Capa Qty를 넣는다.
        - Baseline & Baseline: BOD Port W_Capa Qty
        - 4Weeks & Baseline  : BOD Port W_Capa Qty(O) BOD Port_Capa Qty(4W)(X)
        - 12Weeks & Baseline : BOD Port W_Capa Qty(O) BOD Port_Capa Qty(12W)(X)
        - LY & Baseline      : BOD Port W_Capa Qty(O) BOD Port_Capa Qty(Y-1)(X)
        - SMLY & Baseline    : BOD Port W_Capa Qty(O) BOD Port_Capa Qty(Y-1 M)(X)
    :param df_p_source:
    :param str_p_cond: 0 - Veiw Code가 & SOP로 끝난 경우, 1 - Veiw Code가 & Baseline으로 끝난 경우
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 변경 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    if "TransitVolumeWCapa" not in df_return.columns:
        df_return["TransitVolumeWCapa"] = None


    if str_p_cond == "0":
        list_where_capa = df_return["ViewCode"].str.endswith("& SOP")
        df_return_capa = df_return.loc[list_where_capa].copy(deep=True)
        df_return_ncapa = df_return.loc[~list_where_capa].copy(deep=True)
        if not df_return_capa.empty and len(df_return_capa) > 0:
            df_return_capa["TransitVolumeWCapa"] = (
                    (df_return_capa["TransitVolumeWSOPCNTRQty"].fillna(0) /
                     df_return_capa["TransitVolumeWSOPCNTRQtySum"].fillna(0)))
    elif str_p_cond == "1":
        list_where_capa = (df_return["ViewCode"].str.endswith("& Baseline"))
        # list_where_baseline = (df_return["ViewCode"] == "Baseline & Baseline")
        # list_where_4weeks = (df_return["ViewCode"] == "4Weeks & Baseline")
        # list_where_12weeks = (df_return["ViewCode"] == "12Weeks & Baseline")
        # list_where_ly = (df_return["ViewCode"] == "LY & Baseline")
        # list_where_smly = (df_return["ViewCode"] == "SMLY & Baseline")
        df_return_capa = df_return.loc[list_where_capa].copy(deep=True)
        df_return_ncapa = df_return.loc[~list_where_capa].copy(deep=True)
        if not df_return_capa.empty and len(df_return_capa) > 0:
            df_return_capa["TransitVolumeWCapa"] = df_return_capa["BODPortWCapaQty"]
            # df_return_capa.loc[list_where_4weeks, "TransitVolumeWCapa"] = (
            #     df_return_capa.loc)[list_where_4weeks]["BODPortCapaQty(4W)"]
            # df_return_capa.loc[list_where_12weeks, "TransitVolumeWCapa"] = (
            #     df_return_capa.loc)[list_where_12weeks]["BODPortCapaQty(12W)"]
            # df_return_capa.loc[list_where_ly, "TransitVolumeWCapa"] = (
            #     df_return_capa.loc)[list_where_ly]["BODPortCapaQty(Y-1)"]
            # df_return_capa.loc[list_where_smly, "TransitVolumeWCapa"] = (
            #     df_return_capa.loc)[list_where_smly]["BODPortCapaQty(Y-1M)"]

    df_return = pd.concat([df_return_ncapa, df_return_capa], axis=0)

    return df_return


@_decoration_
def fn_output_formatter_bod_sop(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 7-1. Step 3의 df_BODSop_Cntr를 정리하여 out_BODSop을 만든다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    df_return = df_p_source.copy(deep=True)
    df_return['Version.[Version Name]'] = Param_OUT_VERSION
    df_return = (
        df_return)[['Version.[Version Name]', 'FromSite', 'ToSite', 'Activity2', 'Item', 'Week',
                    'BODSopCntrType', 'BODSopLoadingType', 'BODSopMaxLoadingQty', 'BODSopScpQtySum', 'BODSopSopCntrQty']]
    df_return = df_return.rename(columns={
        'FromSite': 'Sub Location.[Sub Location]',
        'ToSite': 'Location.[Location]',
        'Activity2': 'Activity2.[Activity2]',
        'Item': 'Item.[Item]',
        'Week': 'Time.[Week]',
        'BODSopCntrType': 'BOD Sop_Cntr Type',
        'BODSopLoadingType': 'BOD Sop_Loading Type',
        'BODSopMaxLoadingQty': 'BOD Sop_Max Loading Qty',
        'BODSopScpQtySum': 'BOD Sop_Scp Qty Sum',
        'BODSopSopCntrQty': 'BOD Sop_Sop Cntr Qty'
    })

    return df_return


@_decoration_
def fn_output_formatter_transit_view(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 7-2. Step 4-2의 df_TransitVolumeViewW를 정리하여 out_TransitVolumeView를 만든다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    df_return = df_p_source.copy(deep=True)
    df_return['Version.[Version Name]'] = Param_OUT_VERSION
    df_return = df_return[
        ["Version.[Version Name]", "FromSite", "ToSite", "Activity2", "LoadingPort", "DischargePort", "DestPort",
         "ViewCode", "TransitVolumeRatio(Port/BOD)"]]
    df_return = df_return.rename(columns={
        "FromSite": "Sub Location.[Sub Location]",
        "ToSite": "Location.[Location]",
        "Activity2": "Activity2.[Activity2]",
        "LoadingPort": "Loading Port.[Loading Port]",
        "DischargePort": "Discharge Port.[Discharge Port]",
        "DestPort": "Dest Port.[Dest Port]",
        "ViewCode": "View Code.[View Code]",
        "TransitVolumeRatio(Port/BOD)": "Transit Volume_Ratio(Port / BOD)"
    })

    return df_return


@_decoration_
def fn_output_formatter_transit_view_w(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Step 7-3. Step 6-5의 df_TransitVolumeViewW_capa를 정리하여 out_TransitVolumeViewW를 만든다.
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    df_return = df_p_source.copy(deep=True)
    df_return['Version.[Version Name]'] = Param_OUT_VERSION
    df_return = df_return[
        ["Version.[Version Name]", "FromSite", "ToSite", "Activity2", "Week", "LoadingPort", "DischargePort",
         "DestPort", "ViewCode", "TransitVolumeWCapa", "TransitVolumeWSOPCNTRQty"]]
    df_return = df_return.rename(columns={
        "FromSite": "Sub Location.[Sub Location]",
        "ToSite": "Location.[Location]",
        "Activity2": "Activity2.[Activity2]",
        "Week": "Time.[Week]",
        "LoadingPort": "Loading Port.[Loading Port]",
        "DischargePort": "Discharge Port.[Discharge Port]",
        "DestPort": "Dest Port.[Dest Port]",
        "ViewCode": "View Code.[View Code]",
        "TransitVolumeWCapa": "Transit Volume W_Capa",
        "TransitVolumeWSOPCNTRQty": "Transit Volume W_SOP CNTR Qty"
    })

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_BODSop = pd.DataFrame()
    try:
        ################################################################################################################
        # 모듈 실행 준비 - 로컬 파일 정리, Parameter 확인, 입력 데이터 확인
        ################################################################################################################
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = 'N'

            in_SOPW = pd.read_csv(str_input_dir + "/in_SOPW.csv", encoding="UTF8")
            in_LoadingMethodFromSite = pd.read_csv(str_input_dir + "/in_LoadingMethodFromSite.csv", encoding="UTF8")
            in_LoadingMasterFromSite = pd.read_csv(str_input_dir + "/in_LoadingMasterFromSite.csv", encoding="UTF8")
            in_BODPort = pd.read_csv(str_input_dir + "/in_BODPort.csv", encoding="UTF8")
            in_BODPortW = pd.read_csv(str_input_dir + "/in_BODPortW.csv", encoding="UTF8")
            in_OceanCapaW = pd.read_csv(str_input_dir + "/in_OceanCapaW.csv", encoding="UTF8")

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
        fn_check_input_table(in_SOPW, 'in_SOPW', '0')
        fn_check_input_table(in_LoadingMethodFromSite, 'in_LoadingMethodFromSite', '1')
        fn_check_input_table(in_LoadingMasterFromSite, 'in_LoadingMasterFromSite', '1')
        fn_check_input_table(in_BODPort, 'in_BODPort', '1')
        fn_check_input_table(in_BODPortW, 'in_BODPortW', '1')
        fn_check_input_table(in_OceanCapaW, 'in_OceanCapaW', '1')

        ################################################################################################################
        # Step 0. Preprocess: Input Table의 컬럼명을 변경한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 0,
            'p_step_desc': 'Step 0-0. SOP W를 복사하여 BOD Sop을 생성한다.',
            'p_df_name': 'df_BODSop'
        }
        in_BODSop = fn_copy_sop_w_to_bod_sop(in_SOPW, **dict_log)

        dict_log = {
            'p_step_no': 10,
            'p_step_desc': 'Step 0-1. Preprocess: Input Table(in_BODSop)의 컬럼명을 변경한다.',
            'p_df_name': 'df_BODSop'
        }
        df_BODSop = fn_rename(in_BODSop, **dict_log)

        dict_log = {
            'p_step_no': 20,
            'p_step_desc': 'Step 0-2. Preprocess: Input Table(in_LoadingMethodFromSite)의 컬럼명을 변경한다.',
            'p_df_name': 'df_LoadingMethodFromSite'
        }
        df_LoadingMethodFromSite = fn_rename(in_LoadingMethodFromSite, **dict_log)

        dict_log = {
            'p_step_no': 30,
            'p_step_desc': 'Step 0-3. Preprocess: Input Table(in_LoadingMasterFromSite)의 컬럼명을 변경한다.',
            'p_df_name': 'df_LoadingMasterFromSite'
        }
        df_LoadingMasterFromSite = fn_rename(in_LoadingMasterFromSite, **dict_log)

        dict_log = {
            'p_step_no': 40,
            'p_step_desc': 'Step 0-4. Preprocess: Input Table(in_BODPort)의 컬럼명을 변경한다.',
            'p_df_name': 'df_BODPort'
        }
        df_BODPort = fn_rename(in_BODPort, **dict_log)

        dict_log = {
            'p_step_no': 50,
            'p_step_desc': 'Step 0-5. Preprocess: Input Table(in_BODPortW)의 컬럼명을 변경한다.',
            'p_df_name': 'df_BODPortW'
        }
        df_BODPortW = fn_rename(in_BODPortW, **dict_log)

        dict_log = {
            'p_step_no': 60,
            'p_step_desc': 'Step 0-6. Preprocess: Input Table(in_OceanCapaW)의 컬럼명을 변경한다.',
            'p_df_name': 'df_OceanCapaW'
        }
        df_OceanCapaW = fn_rename(in_OceanCapaW, **dict_log)

        ################################################################################################################
        # Step 1. in_BODSop와 in_LoadingMethodFromSite를 [Sub Location].[Sub Location] 기준으로 Left Join하여
        #         df_BODSop_LoadingMethod를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 1010,
            'p_step_desc': 'STEP 1-1. in_BODSop와 in_LoadingMethodFromSite를 [Sub Location].[Sub Location] 기준으로 '
                           'Left Join하여 df_BODSop_LoadingMethod를 만든다.',
            'p_df_name': 'df_BODSop_LoadingMethod_merged'
        }
        df_BODSop_LoadingMethod_merged = (
            fn_merge(df_BODSop, df_LoadingMethodFromSite,
                     'left',
                     'FromSite',
                     'FromSite',
                     **dict_log))

        ################################################################################################################
        # Step 2-1. df_BODSop_LoadingMethod와 in_LoadingMasterFromSite를 [Sub Location].[Sub Location],
        #           [Container].[ContainerID], [Loading Type].[Loading Type], [Item].[Item]을 기준으로 Left Join하여
        #           df_BODSop_LoadingMaster_default를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 2100,
            'p_step_desc': 'Step 2-1. df_BODSop_LoadingMethod와 in_LoadingMasterFromSite를 [Sub Location].[Sub Location],'
                           '[Container].[ContainerID], [Loading Type].[Loading Type], [Item].[Item]을 기준으로 '
                           'Left Join하여 df_BODSop_LoadingMaster_default를 만든다.',
            'p_df_name': 'df_BODSop_LoadingMaster_merged'
        }
        df_BODSop_LoadingMaster_merged = (
            fn_merge(df_BODSop_LoadingMethod_merged, df_LoadingMasterFromSite,
                     'left',
                     ['FromSite', 'CntrType', 'LoadingType', 'Item'],
                     ['FromSite', 'CntrType', 'LoadingType', 'Item'],
                     **dict_log))

        ################################################################################################################
        # Step 2-2. df_BODSop_LoadingMaster_default에서 M/L Qyt가 Null인 데이터에 대해서 in_LoadingMasterFromSite를
        #           [Sub Location].[Sub Location], [Container].[ContainerID], [Item].[Item]을 기준으로 Left Join하여
        #           df_BODSop_LoadingMaster를 만들고, [Sub Location].[Sub Location], [Container].[ContainerID],
        #           [Item].[Item], [Activity2].[Activity2], [Time].[Week]를 기준으로 중복행을 찾아
        #           첫행만 남기고 삭제하여 df_BODSop_LoadingMaster를 만든다.
        ################################################################################################################
        # dict_log = {
        #     'p_step_no': 2200,
        #     'p_step_desc': 'Step 2-2. df_BODSop_LoadingMaster_default에서 M/L Qyt가 Null인 데이터에 대해서 '
        #                    'in_LoadingMasterFromSite를 [Sub Location].[Sub Location], [Container].[ContainerID], '
        #                    '[Item].[Item]을 기준으로 Left Join하여 df_BODSop_LoadingMaster를 만들고, '
        #                    '[Sub Location].[Sub Location], [Container].[ContainerID], [Item].[Item], '
        #                    '[Activity2].[Activity2], [Time].[Week]를 기준으로 중복행을 찾아 '
        #                    '[Container].[ContainerID], [Loading Type].[Loading Type], [Item].[Item]을 기준으로 '
        #                    '첫행만 남기고 삭제하여 df_BODSop_LoadingMaster를 만든다.',
        #     'p_df_name': 'df_BODSop_LoadingMaster'
        # }
        # df_BODSop_LoadingMaster = (
        #     fn_loading_master_process(df_BODSop_LoadingMaster_default, df_LoadingMasterFromSite, **dict_log))

        ################################################################################################################
        # Step 3. df_BODSop_LoadingMaster에서 M/L Qty가 Null이 아닌 행에 대해 Sop Cntr Qty = Scp Qty Sum / ML Qty으로 계산하여
        #         df_BODSop_Cntr를 만든다. 이 때 동일행의 Cntr Type, Loading Type, Max Loading Qty를 Master 기준으로 채운다.
        #         이 때 계산 결과의 소숫점은 그대로 반영한다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 3000,
            'p_step_desc': 'Step 3. df_BODSop_LoadingMaster에서 M/L Qty가 Null이 아닌 행에 대해 '
                           'Sop Cntr Qty = Scp Qty Sum / ML Qty으로 계산하여 df_BODSop_Cntr를 만든다. '
                           '이 때 동일행의 Cntr Type, Loading Type, Max Loading Qty를 Master 기준으로 채운다. '
                           '이 때 계산 결과의 소숫점은 그대로 반영한다.',
            'p_df_name': 'df_BODSop_Cntr'
        }
        df_BODSop_Cntr = fn_container_calculate(df_BODSop_LoadingMaster_merged, **dict_log)

        ################################################################################################################
        # Step 4-1. in_BODPort의 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        #         [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], [Dest Port].[Dest Port] 기준으로
        #          각 행마다 아래 View Code가 전체 생성되도록 하여 df_TransitVolumeView를 만든다.
        #          - Baseline & Baseline
        #          - Baseline & SOP
        #          - 4Weeks & Baseline
        #          - 4Weeks & SOP
        #          - 12Weeks & Baseline
        #          - 12Weeks & SOP
        #          - LY & Baseline
        #          - LY & SOP
        #          - SMLY & Baseline
        #          - SMLY & SOP
        ################################################################################################################
        dict_log = {
            'p_step_no': 4010,
            'p_step_desc': 'Step 4-1. in_BODPort의 [Sub Location].[Sub Location], [Location].[Location], '
                           '[Activity2].[Activity2], [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], '
                           '[Dest Port].[Dest Port] 기준으로 각 행마다 아래 View Code가 전체 생성되도록 하여 '
                           'df_TransitVolumeView를 만든다.',
            'p_df_name': 'df_TransitVolumeView1'
        }
        df_TransitVolumeView1 = fn_make_transit_volume(df_BODPort, "0", **dict_log)

        ################################################################################################################
        # Step 4-2. in_TransitVolumeView와의 View Code에 따라 Transit Volume_Ratio(Port / BOD)에
        #           아래와 같은 기준으로 값을 채운다.
        #           - Baseline & : BOD Port_Ratio(Port / BOD)
        #           - 4Weeks &   : BOD Port_Ratio(Port per BOD 4W)
        #           - 12Weeks &  : BOD Port_Ratio(Port per BOD 12W)
        #           - LY &       : BOD Port_Ratio(Port per BOD Y-1)
        #           - SMLY &     : BOD Port_Ratio(Port per BOD Y-1 M)
        ################################################################################################################
        dict_log = {
            'p_step_no': 4020,
            'p_step_desc': 'Step 4-2. in_TransitVolumeView와의 View Code에 따라 Transit Volume_Ratio(Port / BOD)에 ' +
                           '아래와 같은 기준으로 값을 채운다.' + '\n' +
                           '- Baseline & : BOD Port_Ratio(Port / BOD)' + '\n' +
                           '- 4Weeks &   : BOD Port_Ratio(Port per BOD 4W)' + '\n' +
                           '- 12Weeks &  : BOD Port_Ratio(Port per BOD 12W)' + '\n' +
                           '- LY &       : BOD Port_Ratio(Port per BOD Y-1)' + '\n' +
                           '- SMLY &     : BOD Port_Ratio(Port per BOD Y-1 M)',
            'p_df_name': 'df_TransitVolumeView2'
        }
        df_TransitVolumeView2 = fn_set_transit_volume_ratio_port_per_bod(df_TransitVolumeView1, **dict_log)

        ################################################################################################################
        # Step 5-1. df_BODSop_Cntr에서 [Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        #           [Time].[Week] 기준으로 "BOD Sop_Sop Cntr Qty"를 Sum을 하여 df_BODSop_CntrSum을 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 5010,
            'p_step_desc': 'Step 5-1. df_BODSop_Cntr에서 [Sub Location].[Sub Location], [Location].[Location], '
                           '[Activity2].[Activity2], [Time].[Week] 기준으로 "BOD Sop_Sop Cntr Qty"를 Sum을 하여 '
                           'df_BODSop_CntrSum을 만든다.',
            'p_df_name': 'df_BODSop_CntrSum'
        }
        df_BODSop_CntrSum = fn_container_sum(df_BODSop_Cntr, **dict_log)

        ################################################################################################################
        # Step 5-2. in_BODPortW의 Sub Location].[Sub Location], [Location].[Location], [Activity2].[Activity2],
        #           [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], [Dest Port].[Dest Port],
        #           [Time].[Week] 기준으로 각 행마다 아래 View Code가 전체 생성되도록 하여 df_TransitVolumeViewW를 만든다.
        #          - Baseline & Baseline
        #          - Baseline & SOP
        #          - 4Weeks & Baseline
        #          - 4Weeks & SOP
        #          - 12Weeks & Baseline
        #          - 12Weeks & SOP
        #          - LY & Baseline
        #          - LY & SOP
        #          - SMLY & Baseline
        #          - SMLY & SOP
        ################################################################################################################
        dict_log = {
            'p_step_no': 5020,
            'p_step_desc': 'Step 5-2. in_BODPortW의 Sub Location].[Sub Location], [Location].[Location], '
                           '[Activity2].[Activity2], [Loading Port].[Loading Port], [Discharge Port].[Discharge Port], '
                           '[Dest Port].[Dest Port], [Time].[Week] 기준으로 각 행마다 아래 View Code가 전체 생성되도록 하여 '
                           'df_TransitVolumeViewW를 만든다.',
            'p_df_name': 'df_TransitVolumeViewW1'
        }
        df_TransitVolumeViewW1 = fn_make_transit_volume(df_BODPortW, "0", **dict_log)

        ################################################################################################################
        # Step 5-2. in_TransitVolumeViewW에 df_TransitVolumeView를 Left Join 하여 df_TransitVolumeViewW_merged를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 5020,
            'p_step_desc': 'Step 5-2. in_TransitVolumeViewW에 df_TransitVolumeView를 Left Join 하여 '
                           'df_TransitVolumeViewW_merged를 만든다.',
            'p_df_name': 'df_TransitVolumeViewW_merged'
        }
        df_TransitVolumeViewW_merged = (
            fn_merge(df_TransitVolumeViewW1, df_TransitVolumeView2, "left",
                     ["FromSite", "ToSite", "Activity2", "LoadingPort", "DischargePort", "DestPort", "ViewCode"],
                     ["FromSite", "ToSite", "Activity2", "LoadingPort", "DischargePort", "DestPort", "ViewCode"],
                     **dict_log))
        if "TransitVolumeRatio(Port/BOD)_x" in df_TransitVolumeViewW_merged.columns:
            # Merge 후처리
            df_TransitVolumeViewW_merged.drop(["TransitVolumeRatio(Port/BOD)_x"], axis=1, inplace=True)
            df_TransitVolumeViewW_merged = df_TransitVolumeViewW_merged.rename(
                columns={"TransitVolumeRatio(Port/BOD)_y": "TransitVolumeRatio(Port/BOD)"})
            fn_log_dataframe(df_TransitVolumeViewW_merged, "df_TransitVolumeViewW_merged")

        ################################################################################################################
        # Step 5-3. df_TransitVolumeViewW와 df_BODSop_CntrSum을 [Sub Location].[Sub Location],
        #           [Location].[Location], [Activity2].[Activity2], [Time].[Week] 기준으로 Left Join 하여
        #           df_TransitVolumeViewW를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 5030,
            'p_step_desc': 'Step 5-3. df_TransitVolumeViewW와 df_BODSop_CntrSum을 [Sub Location].[Sub Location], '
                           '[Location].[Location], [Activity2].[Activity2], [Time].[Week] 기준으로 Left Join 하여 '
                           'df_TransitVolumeViewW를 만든다.',
            'p_df_name': 'df_TransitVolumeViewW2'
        }
        df_TransitVolumeViewW2 = fn_merge(df_TransitVolumeViewW_merged, df_BODSop_CntrSum, "left",
                                         ["FromSite", "ToSite", "Activity2", "Week"],
                                         ["FromSite", "ToSite", "Activity2", "Week"], **dict_log)

        ################################################################################################################
        # Step 5-4. df_TransitVolumeViewW에서
        #           View Code에 해당하는 BOD Port_Ratio(Step 4-2 기준)를 BOD Sop_Sop Cntr Qty Sum에 곱해준 값을
        #           Transit Volume W_SOP CNTR Qty에 넣는다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 5040,
            'p_step_desc': 'Step 5-4. df_TransitVolumeViewW에서  '
                           'View Code에 해당하는 BOD Port_Ratio(Step 4-2 기준)를 BOD Sop_Sop Cntr Qty Sum에 곱해준 값을 '
                           'Transit Volume W_SOP CNTR Qty에 넣는다.',
            'p_df_name': 'df_TransitVolumeViewW3'
        }
        df_TransitVolumeViewW3 = fn_set_transit_volume_w_sop_cntr_qty(df_TransitVolumeViewW2, **dict_log)

        ################################################################################################################
        # Step 6-1. df_TransitVolumeViewW에 in_OceanCapaW를 [Time].[Planning Month], [Loading Port].[Loading Logistics Port],
        #           [Discharge Port].[Discharge Logistics Port]를 기준으로 Left Join 하여 df_TransitVolumeViewW_capa를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 6010,
            'p_step_desc': 'Step 6-1. df_TransitVolumeViewW에 in_OceanCapaW를 [Time].[Planning Month], '
                           '[Loading Port].[Loading Logistics Port], [Discharge Port].[Discharge Logistics Port]를 기준으로 '
                           'Left Join 하여 df_TransitVolumeViewW_capa를 만든다.',
            'p_df_name': 'df_TransitVolumeViewW_capa1'
        }
        df_TransitVolumeViewW_capa1 = (
            fn_merge(df_TransitVolumeViewW3, df_OceanCapaW, "left",
                     ["PlanningMonth", "LoadingLogisticsPort", "DischargeLogisticsPort"],
                     ["PlanningMonth", "LoadingLogisticsPort", "DischargeLogisticsPort"], **dict_log))

        ################################################################################################################
        # Step 6-2. df_TransitVolumeViewW_capa에서 [Loading Port].[Loading Logistics Port],
        #           [Discharge Port].[Discharge Logistics Port]를 기준으로 Transit Volume W_SOP CNTR Qty를 Sum하여
        #           Transit Volume W_SOP CNTR Qty Sum에 넣는다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 6020,
            'p_step_desc': 'Step 6-2. df_TransitVolumeViewW_capa에서 [Loading Port].[Loading Logistics Port], '
                           '[Discharge Port].[Discharge Logistics Port]를 기준으로 '
                           'Transit Volume W_SOP CNTR Qty를 Sum하여 Transit Volume W_SOP CNTR Qty Sum에 넣는다.',
            'p_df_name': 'df_TransitVolumeViewW_capa2'
        }
        df_TransitVolumeViewW_capa2 = fn_container_sum2(df_TransitVolumeViewW_capa1, **dict_log)

        ################################################################################################################
        # Step 6-3. df_TransitVolumeViewW_capa에서
        #           (BOD Port W_Capa Qty에서 대상 주차의 값을 찾고
        #           해당 row의 SOP cntr qty/(Logistics Port Route값이 같은 SOP cntr qty를 SUM한 값)을
        #           View Code가 & SOP인 행의 Transit Volume W_Capa에 넣는다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 6030,
            'p_step_desc': 'Step 6-3. df_TransitVolumeViewW_capa에서 '
                           '(BOD Port W_Capa Qty에서 대상 주차의 값을 찾고 '
                           '해당 row의 SOP cntr qty/(Logistics Port Route값이 같은 SOP cntr qty를 SUM한 값)을 '
                           'View Code가 & SOP인 행의 Transit Volume W_Capa에 넣는다.',
            'p_df_name': 'df_TransitVolumeViewW_capa3'
        }
        df_TransitVolumeViewW_capa3 = fn_set_transit_volume_w_capa(df_TransitVolumeViewW_capa2, "0", **dict_log)

        ################################################################################################################
        # Step 6-4. df_TransitVolumeViewW_capa에 in_BODPortW를 [Sub Location].[Sub Location], [Location].[Location],
        #           [Time].[Week], [Activity2].[Activity2], [Loading Port].[Loading Port],
        #           [Discharge Port].[Discharge Port], [Dest Port].[Dest Port]를 기준으로 Left Join하여
        #           df_TransitVolumeViewW_port를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 6040,
            'p_step_desc': 'Step 6-4. df_TransitVolumeViewW_capa에 in_BODPortW를 [Sub Location].[Sub Location], '
                           '[Location].[Location], [Activity2].[Activity2], [Time].[Week], [Loading Port].[Loading Port], '
                           '[Discharge Port].[Discharge Port], [Dest Port].[Dest Port]를 기준으로 Left Join하여 '
                           'df_TransitVolumeViewW_port를 만든다.',
            'p_df_name': 'df_TransitVolumeViewW_port'
        }
        df_TransitVolumeViewW_port = (
            fn_merge(df_TransitVolumeViewW_capa3, df_BODPortW, "left",
                     ["FromSite", "ToSite", "Activity2", "Week", "LoadingPort", "DischargePort", "DestPort"],
                     ["FromSite", "ToSite", "Activity2", "Week", "LoadingPort", "DischargePort", "DestPort"],
                     **dict_log))

        df_TransitVolumeViewW_port = fn_merge_after(df_TransitVolumeViewW_port)

        ################################################################################################################
        # Step 6-5. df_TransitVolumeViewW_port에서 View Code & Baseline인 행의 Transit Volume W_Capa에
        #           아래의 기준으로 값을 넣는다.
        #           - & Baseline: BOD Port W_Capa Qty
        ################################################################################################################
        dict_log = {
            'p_step_no': 6050,
            'p_step_desc': 'Step 6-5. df_TransitVolumeViewW_port에서 View Code & Baseline인 행의 Transit Volume W_Capa에 ' +
                           '아래의 기준으로 값을 넣는다.' + '\n' +
                           '- & Baseline: BOD Port W_Capa Qty',
            'p_df_name': 'df_TransitVolumeViewW_capa'
        }
        df_TransitVolumeViewW_capa = fn_set_transit_volume_w_capa(df_TransitVolumeViewW_port, "1", **dict_log)

        ################################################################################################################
        # Output 정리
        # - Step 3의 df_BODSop_Cntr를 정리하여 out_BODSop을 만든다.
        # - Step 4-2의 df_TransitVolumeView를 정리하여 out_TransitVolumeView를 만든다.
        # - Step 6-5의 df_TransitVolumeViewW_capa를 정리하여 out_TransitVolumeViewW를 만든다.
        ################################################################################################################
        dict_log = {
            'p_step_no': 9010,
            'p_step_desc': 'Output 정리 - Step 3의 df_BODSop_Cntr를 정리하여 out_BODSop을 만든다.',
            'p_df_name': 'out_BODSop'
        }
        out_BODSop = fn_output_formatter_bod_sop(df_BODSop_Cntr, **dict_log)

        dict_log = {
            'p_step_no': 9030,
            'p_step_desc': 'Output 정리 - Step 4-2의 df_TransitVolumeView를 정리하여 out_TransitVolumeView를 만든다.',
            'p_df_name': 'out_TransitVolumeView'
        }
        out_TransitVolumeView = fn_output_formatter_transit_view(df_TransitVolumeViewW3, **dict_log)

        dict_log = {
            'p_step_no': 9030,
            'p_step_desc': 'Output 정리 - Step 6-5의 df_TransitVolumeViewW_capa를 정리하여 out_TransitVolumeViewW를 만든다.',
            'p_df_name': 'out_TransitVolumeViewW'
        }
        out_TransitVolumeViewW = fn_output_formatter_transit_view_w(df_TransitVolumeViewW_capa, **dict_log)

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_BODSop = None
            raise Exception(e)
        else:
            if out_BODSop.empty:
                out_BODSop = fn_set_header()
                fn_log_dataframe(out_BODSop, 'out_BODSop')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_BODSop.empty:
            out_BODSop = fn_set_header()
            fn_log_dataframe(out_BODSop, 'out_BODSop')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')
