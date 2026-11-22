"""
* 프로그램명
    - PY_UI_POProcessValidNLoad_REG

* 내용
    - PO Process에 등록된 데이터에 대해 Loading Simulation을 실행하기 위해 데이터 정합성을 체크한다.
    - 데이터 정합성이 검증된 행에 대해서는 Loading Simulation에 필요한 마스터 데이터를 로드한다.
    - 주의사항: 소스 내에 포함된 IBPL로 Input을 만들지 않는 경우 컬럼의 순서가 달라 오류 또는 원하지 않는 결과가 발생할 수 있다.

* 변경이력
    - 2025.11.05 / Kang, Gyeoinghun / Create
    - 2025.12.29 / Kang, Gyeoinghun / Update
      : in_POProcess IBPL에서 사용되던 NamedSet(&NSFromSiteMF)을 삭제하고 직접 필터링하여 처리
        [Sub Location].[Sub Location Type].[MF].relatedmembers([Sub Location])
      : 상단 블럭의 Check Qty 복사하는 범위에서 DIR_PO 제외, 하단 블럭에서 상단 블럭을 Check Qty 복사하는 로직 추가
    - 2026.01.20 / Kang, Gyeoinghun / Update
      : fn_aggregation_po 함수 내 오류 수정

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를 결정하는 파라미터
    - Param_Step : 시뮬레이션 대상 단계, P, M, ADJ1, ADJ2, ADJ3, FINAL
    - Param_Check_Qty : "Current"  # Current-Check Qty(Step), POPOnly-POP(Step), POPShort-POP(Step) + Short(Step)

* Input Tables
    - in_POProcess
        Select ([MFG Week].[MFG Week] * [Sub Location].[Sub Location Type].[MF].relatedmembers([Sub Location])
             * [Location].[Location] * [Item].[Item] * [Time].[Week] * [SOP Week].[SOP Week]
             * [Delivery Week].[Delivery Week]) on row
             , ({Measure.[PO Process_Data Source], Measure.[PO Process_Check Qty(P)]
             , Measure.[PO Process_Check Qty(M)], Measure.[PO Process_Check Qty(ADJ1)]
             , Measure.[PO Process_Check Qty(ADJ2)], Measure.[PO Process_Check Qty(ADJ3)]
             , Measure.[PO Process_Check Qty(FINAL)]}) on column
         where {[Version].[Version Name]}
        ;

    - in_POProcessDetail
        Select ([MFG Week].[MFG Week] * [Sub Location].[Sub Location] * [Location].[Location] * [Item].[Item]
             * [Seq].[Seq] * [Time].[Week]) on row
             , ({Measure.[PO Process Detail_SOP ETD Week], Measure.[PO Process Detail_Account]
             , Measure.[PO Process Detail_Ship To], Measure.[PO Process Detail_Block]
             , Measure.[PO Process Detail_Last Step]
             , Measure.[PO Process Detail_POP Qty(P)], Measure.[PO Process Detail_Short Qty(P)]
             , Measure.[PO Process Detail_Check Qty(P)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(P)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(P)]
             , Measure.[PO Process Detail_Lane Load Mix Match(P)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(P)]
             , Measure.[PO Process Detail_Valid Fail Reason(P)]
             , Measure.[PO Process Detail_POP Qty(M)], Measure.[PO Process Detail_Short Qty(M)]
             , Measure.[PO Process Detail_Check Qty(M)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(M)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(M)]
             , Measure.[PO Process Detail_Lane Load Mix Match(M)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(M)]
             , Measure.[PO Process Detail_Valid Fail Reason(M)]
             , Measure.[PO Process Detail_Check Qty(ADJ1)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ1)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process Detail_Lane Load Mix Match(ADJ1)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ1)]
             , Measure.[PO Process Detail_Check Qty(ADJ2)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ2)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process Detail_Lane Load Mix Match(ADJ2)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ2)]
             , Measure.[PO Process Detail_Check Qty(ADJ3)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ3)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process Detail_Lane Load Mix Match(ADJ3)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ3)]
             , Measure.[PO Process Detail_Check Qty(FINAL)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)]
             , Measure.[PO Process Detail_Lane Load Mix Match(FINAL)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)]
             , Measure.[PO Process Detail_Valid Fail Reason(FINAL)]}) on column
        include memberproperties
                { [Location].[Location], [Shipment Type] }
         where {[Version].[Version Name]}
        ;

    - in_LoadingMasterFromSite
        Select ([Sub Location].[Sub Location] * [Item].[Item] * [Loading Type].[Loading Type]
             * [Container].[ContainerID]) on row
             , ({Measure.[Loading Master From Site_JIG], Measure.[Loading Master From Site_Line]
             , Measure.[Loading Master From Site_Max Load Qty], Measure.[Loading Master From Site_LDM Qty]
             , Measure.[Loading Master From Site_Multiple], Measure.[Loading Master From Site_Min Qty]
             , Measure.[Loading Master From Site_CBM], Measure.[Loading Master From Site_Height]
             , Measure.[Loading Master From Site_Width], Measure.[Loading Master From Site_Depth]
             , Measure.[Loading Master From Site_Valid Flag]}) on column
         where {[Version].[Version Name]}
        ;

    - in_LoadingMasterToSite
        Select ([Sub Location].[Sub Location] * [Location].[Location] * [Item].[Item]
             * [Loading Type].[Loading Type] * [Container].[ContainerID]) on row
             , ({Measure.[Loading Master To Site_JIG], Measure.[Loading Master To Site_Line]
             , Measure.[Loading Master To Site_Max Load Qty], Measure.[Loading Master To Site_LDM Qty]
             , Measure.[Loading Master To Site_Multiple], Measure.[Loading Master To Site_Min Qty]
             , Measure.[Loading Master To Site_CBM], Measure.[Loading Master To Site_Height]
             , Measure.[Loading Master To Site_Width], Measure.[Loading Master To Site_Depth]}) on column
         where {[Version].[Version Name], Measure.[Loading Master To Site_Valid Flag] == "Y"}
        ;

    - in_LoadingMasterAccount
        Select ([Sub Location].[Sub Location] * [Location].[Location]
             * [Sales Domain].[Ship To] * [Item].[Item] * [Loading Type].[Loading Type]
             * [Container].[ContainerID]) on row
             , ({Measure.[Loading Master Account_JIG], Measure.[Loading Master Account_Line]
             , Measure.[Loading Master Account_Max Load Qty], Measure.[Loading Master Account_LDM Qty]
             , Measure.[Loading Master Account_Multiple], Measure.[Loading Master Account_Min Qty]
             , Measure.[Loading Master Account_CBM], Measure.[Loading Master Account_Height]
             , Measure.[Loading Master Account_Width], Measure.[Loading Master Account_Depth]}) on column
         where {[Version].[Version Name], Measure.[Loading Master Account_Valid Flag] == "Y"}
        ;

    - in_LoadingMasterShipTo
        Select ([Sub Location].[Sub Location] * [Location].[Location]
             * [Sales Domain].[Ship To] * [Seq].[Seq] * [Item].[Item] * [Loading Type].[Loading Type]
             * [Container].[ContainerID]) on row
             , ({Measure.[Loading Master Ship To_Ship To], Measure.[Loading Master Ship To_JIG]
             , Measure.[Loading Master Ship To_Line], Measure.[Loading Master Ship To_Max Load Qty]
             , Measure.[Loading Master Ship To_LDM Qty], Measure.[Loading Master Ship To_Multiple]
             , Measure.[Loading Master Ship To_Min Qty], Measure.[Loading Master Ship To_CBM]
             , Measure.[Loading Master Ship To_Height], Measure.[Loading Master Ship To_Width]
             , Measure.[Loading Master Ship To_Depth]}) on column
         where {[Version].[Version Name], Measure.[Loading Master Ship To_Valid Flag] == "Y"}
        ;

    - in_LoadingMethodFromSite
        Select ([Sub Location].[Sub Location] * [Shipment Type].[Shipment Type]
             * [Loading Type].[Loading Type] * [Container].[ContainerID]) on row
             , ({Measure.[Loading Method From Site_Default], Measure.[Loading Method From Site_JIG Line]
             , Measure.[Loading Method From Site_1st Mix], Measure.[Loading Method From Site_2nd Mix]
             , Measure.[Loading Method From Site_3rd Mix], Measure.[Loading Method From Site_Single FR Type]
             , Measure.[Loading Method From Site_Single Min FR], Measure.[Loading Method From Site_Single Max FR]
             , Measure.[Loading Method From Site_Single Cut Add], Measure.[Loading Method From Site_Mix FR Type]
             , Measure.[Loading Method From Site_Mix Min FR], Measure.[Loading Method From Site_Mix Max FR]
             , Measure.[Loading Method From Site_Mix Cut Add]
             , Measure.[Loading Method From Site_SKU Per Cntr]}) on column
         where {[Version].[Version Name], Measure.[Loading Method From Site_Valid Flag] == "Y"}
        ;

    - in_LoadingMethodToSite
        Select ([Sub Location].[Sub Location] * [Location].[Location]
             * [Loading Type].[Loading Type] * [Container].[ContainerID]) on row
             , ({Measure.[Loading Method To Site_Default], Measure.[Loading Method To Site_JIG Line]
             , Measure.[Loading Method To Site_1st Mix], Measure.[Loading Method To Site_2nd Mix]
             , Measure.[Loading Method To Site_3rd Mix], Measure.[Loading Method To Site_Single FR Type]
             , Measure.[Loading Method To Site_Single Min FR], Measure.[Loading Method To Site_Single Max FR]
             , Measure.[Loading Method To Site_Single Cut Add], Measure.[Loading Method To Site_Mix FR Type]
             , Measure.[Loading Method To Site_Mix Min FR], Measure.[Loading Method To Site_Mix Max FR]
             , Measure.[Loading Method To Site_Mix Cut Add], Measure.[Loading Method To Site_SKU Per Cntr]}) on column
         where {[Version].[Version Name], Measure.[Loading Method To Site_Valid Flag] == "Y"}
        ;

    - in_LoadingMethodAccount
        Select ([Sub Location].[Sub Location] * [Location].[Location]
             * [Sales Domain].[Ship To] * [Loading Type].[Loading Type] * [Container].[ContainerID]) on row
             , ({Measure.[Loading Method Account_Default], Measure.[Loading Method Account_JIG Line]
             , Measure.[Loading Method Account_1st Mix], Measure.[Loading Method Account_2nd Mix]
             , Measure.[Loading Method Account_3rd Mix], Measure.[Loading Method Account_Single FR Type]
             , Measure.[Loading Method Account_Single Min FR], Measure.[Loading Method Account_Single Max FR]
             , Measure.[Loading Method Account_Single Cut Add], Measure.[Loading Method Account_Mix FR Type]
             , Measure.[Loading Method Account_Mix Min FR], Measure.[Loading Method Account_Mix Max FR]
             , Measure.[Loading Method Account_Mix Cut Add], Measure.[Loading Method Account_SKU Per Cntr]}) on column
         where {[Version].[Version Name], Measure.[Loading Method Account_Valid Flag] == "Y"}
        ;

    - in_LoadingMethodShipTo
        Select ([Sub Location].[Sub Location] * [Location].[Location]
             * [Sales Domain].[Ship To] * [Seq].[Seq] * [Loading Type].[Loading Type]
             * [Container].[ContainerID]) on row
             , ({Measure.[Loading Method Ship To_Ship To], Measure.[Loading Method Ship To_Default]
             , Measure.[Loading Method Ship To_JIG Line], Measure.[Loading Method Ship To_1st Mix]
             , Measure.[Loading Method Ship To_2nd Mix], Measure.[Loading Method Ship To_3rd Mix]
             , Measure.[Loading Method Ship To_Single FR Type], Measure.[Loading Method Ship To_Single Min FR]
             , Measure.[Loading Method Ship To_Single Max FR], Measure.[Loading Method Ship To_Single Cut Add]
             , Measure.[Loading Method Ship To_Mix FR Type], Measure.[Loading Method Ship To_Mix Min FR]
             , Measure.[Loading Method Ship To_Mix Max FR], Measure.[Loading Method Ship To_Mix Cut Add]
             , Measure.[Loading Method Ship To_SKU Per Cntr]}) on column
         where {[Version].[Version Name], Measure.[Loading Method Ship To_Valid Flag] == "Y"}
        ;

    - in_LoadingMethodMixToSite
        Select ([Sub Location].[Sub Location] * [Location].[Location] * [Seq].[Seq]
             * [Item].[Item]) on row
             , ({Measure.[Loading Method Mix To Site_Item Mix Group], Measure.[Loading Method Mix To Site_Group Id]
             , Measure.[Loading Method Mix To Site_Loading Type], Measure.[Loading Method Mix To Site_Cntr Type]
             , Measure.[Loading Method Mix To Site Detail_Valid Flag]}) on column
         where {[Version].[Version Name], Measure.[Loading Method Mix To Site Detail_Valid Flag] == "Y"}
        ;

    - in_LoadingMethodMixShipTo
        Select ([Sub Location].[Sub Location] * [Location].[Location] * [Seq].[Seq]
             * [Item].[Item]) on row
             , ({Measure.[Loading Method Mix Ship To_Ship To], Measure.[Loading Method Mix Ship To_Item Mix Group]
             , Measure.[Loading Method Mix Ship To_Group Id], Measure.[Loading Method Mix Ship To_Loading Type]
             , Measure.[Loading Method Mix Ship To_Cntr Type]
             , Measure.[Loading Method Mix Ship To Detail_Valid Flag]}) on column
         where {[Version].[Version Name], Measure.[Loading Method Mix Ship To Detail_Valid Flag] == "Y"}
        ;

    - in_LoadingProfitGrade
        Select ([Location].[Location] * [Item].[Item]) on row
             , ({Measure.[Loading Profit Grade_Profit Grade]
             , Measure.[Loading Profit Grade_Profit Grade Priority]}) on column
         where {[Version].[Version Name], Measure.[Loading Profit Grade_Profit Grade Valid Flag] == TRUE}
        ;

    - in_ItemULD
        Select ([Item].[Item]) on row
             , ({Measure.[Item ULD_CBM], Measure.[Item ULD_Height], Measure.[Item ULD_Width]
             , Measure.[Item ULD_Depth]}) on column
         where {[Version].[Version Name]}
        ;

* Output Tables
    - out_POProcess
        Select ([Version].[Version Name] * [MFG Week].[MFG Week] * [Sub Location].[Sub Location] * [Location].[Location]
             * [Item].[Item] * [Seq].[Seq] * [Time].[Week] * [SOP Week].[SOP Week]
             * [Delivery Week].[Delivery Week]) on row
             , ({Measure.[PO Process_Item Unit Load Mix Match(P)]
             , Measure.[PO Process_Item Unit Load Mix Match Chk(P)]
             , Measure.[PO Process_Lane Load Mix Match(P)]
             , Measure.[PO Process_Lane Load Mix Match Chk(P)], Measure.[PO Process_Valid Fail Reason(P)]
             , Measure.[PO Process_Item Unit Load Mix Match(M)]
             , Measure.[PO Process_Item Unit Load Mix Match Chk(M)]
             , Measure.[PO Process_Lane Load Mix Match(M)]
             , Measure.[PO Process_Lane Load Mix Match Chk(M)], Measure.[PO Process_Valid Fail Reason(M)]
             , Measure.[PO Process_Item Unit Load Mix Match(ADJ1)]
             , Measure.[PO Process_Item Unit Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process_Lane Load Mix Match(ADJ1)]
             , Measure.[PO Process_Lane Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process_Valid Fail Reason(ADJ1)]
             , Measure.[PO Process_Item Unit Load Mix Match(ADJ2)]
             , Measure.[PO Process_Item Unit Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process_Lane Load Mix Match(ADJ2)]
             , Measure.[PO Process_Lane Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process_Valid Fail Reason(ADJ2)]
             , Measure.[PO Process_Item Unit Load Mix Match(ADJ3)]
             , Measure.[PO Process_Item Unit Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process_Lane Load Mix Match(ADJ3)]
             , Measure.[PO Process_Lane Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process_Valid Fail Reason(ADJ3)]
             , Measure.[PO Process_Item Unit Load Mix Match(FINAL)]
             , Measure.[PO Process_Item Unit Load Mix Match Chk(FINAL)]
             , Measure.[PO Process_Lane Load Mix Match(FINAL)]
             , Measure.[PO Process_Lane Load Mix Match Chk(FINAL)]
             , Measure.[PO Process_Valid Fail Reason(FINAL)]}) on column
        ;

    - out_POProcessDetail
        Select ([Version].[Version Name] * [MFG Week].[MFG Week] * [Sub Location].[Sub Location] * [Location].[Location]
             * [Item].[Item] * [Seq].[Seq] * [Time].[Week] * [SOP Week].[SOP Week]) on row
             , ({Measure.[PO Process Detail_Item Unit Load Mix Match(P)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(P)]
             , Measure.[PO Process Detail_Lane Load Mix Match(P)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(P)], Measure.[PO Process Detail_Valid Fail Reason(P)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(M)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(M)]
             , Measure.[PO Process Detail_Lane Load Mix Match(M)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(M)], Measure.[PO Process Detail_Valid Fail Reason(M)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ1)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process Detail_Lane Load Mix Match(ADJ1)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ1)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ2)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process Detail_Lane Load Mix Match(ADJ2)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ2)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ3)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process Detail_Lane Load Mix Match(ADJ3)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ3)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)]
             , Measure.[PO Process Detail_Lane Load Mix Match(FINAL)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)]
             , Measure.[PO Process Detail_Valid Fail Reason(FINAL)]}) on column
        ;

    - out_LoadingPOCalMaster
        Select ([Version].[Version Name] * [Time].[Week] * [Sub Location].[Sub Location] * [Location].[Location]
             * [Item].[Item] * [Seq].[Seq]) on row
             , ({Measure.[Loading PO Cal Master_Block], Measure.[Loading PO Cal Master_JIG]
             , Measure.[Loading PO Cal Master_JIG Line], Measure.[Loading PO Cal Master_Line]
             , Measure.[Loading PO Cal Master_Profit Grade], Measure.[Loading PO Cal Master_Profit Grade Priority]
             , Measure.[Loading PO Cal Master_Loading Type], Measure.[Loading PO Cal Master_Cntr Type]
             , Measure.[Loading PO Cal Master_Max Load Qty], Measure.[Loading PO Cal Master_LDM Qty]
             , Measure.[Loading PO Cal Master_Multiple], Measure.[Loading PO Cal Master_Min Qty]
             , Measure.[Loading PO Cal Master_Single FR Type], Measure.[Loading PO Cal Master_Single Min FR]
             , Measure.[Loading PO Cal Master_Single Max FR], Measure.[Loading PO Cal Master_Single Min FTL]
             , Measure.[Loading PO Cal Master_Single Max FTL], Measure.[Loading PO Cal Master_Single Cut Add]
             , Measure.[Loading PO Cal Master_Mix FR Type], Measure.[Loading PO Cal Master_Mix Min FR]
             , Measure.[Loading PO Cal Master_Mix Max FR], Measure.[Loading PO Cal Master_Mix Min FTL]
             , Measure.[Loading PO Cal Master_Mix Max FTL], Measure.[Loading PO Cal Master_Mix Cut Add]
             , Measure.[Loading PO Cal Master_1st Mix], Measure.[Loading PO Cal Master_2nd Mix]
             , Measure.[Loading PO Cal Master_3rd Mix], Measure.[Loading PO Cal Master_Item Mix Group]
             , Measure.[Loading PO Cal Master_Item Height], Measure.[Loading PO Cal Master_Item Width]
             , Measure.[Loading PO Cal Master_Item Depth], Measure.[Loading PO Cal Master_SKU Per Cntr]}) on column
        ;

    - out_LoadingMasterFromSiteNew
        Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Item].[Item] * [Loading Type].[Loading Type]
             * [Container].[ContainerID]) on row
             , (Measure.[Loading Master From Site_CBM], Measure.[Loading Master From Site_Height]
             , Measure.[Loading Master From Site_Width], Measure.[Loading Master From Site_Depth]
             , Measure.[Loading Master From Site_Valid Flag], Measure.[Loading Master From Site_Created By]
             , Measure.[Loading Master From Site_Creation Time]}) on column
        ;

* Flow Summary
    Step 0. 전처리
        - 수행 단계에 따라 데이터 범위를 정한다.
        P : 무조건 전체 수행
        M : Last Step이 2인 행만 수행(PO Process Detail_Last Step)
        ADJ1: 최초 수행 시 Last Step이 2인 행만 수행 후, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 3으로 없데이트,
              2번째 이후부터 Last Step 2와 3인 건들에 대해서 수행
        ADJ1: 최초 수행 시 Last Step이 3인 행만 수행 후, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 4로 없데이트,
              2번째 이후부터 Last Step 3과 4인 건들에 대해서 수행
        ADJ1: 최초 수행 시 Last Step이 4인 행만 수행 후, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 5로 없데이트,
              2번째 이후부터 Last Step 4와 5인 건들에 대해서 수행
        - 수행에 편리하도록 컬럼명을 줄여서 Rename 한다.
        - 수행 시 오류가 발생하는 컬럼들에 대해서 Data Type을 지정해준다.

    Step 1.

* Validation :

* Execution :
    EXEC plugin instance [PY_UI_POProcessValidNLoad_REG]
         for measures { [PO Process_Valid Fail Reason(P)] }
         using scope ([Version].[Version Name].[CWV_MP])
         using arguments {(ExecutionMode, "MediumWeight")
                       , (Param_OUT_VERSION, "CWV_MP")
                       , (Param_Exception_Flag, "N")
                       , (Param_Step, "P")
                       , (Param_Check_Qty, "Current")
                       , (MaxSliceTableCells, 200000000)
                       , (MaxConcurrency, 1)
                       , (IncludeNullRows, False)
                       , ([Param.o9_sys_log_level], "DEBUG")
         }
    ;

    - 기존 데이터 삭제
    Delete data for model [Loading PO Cal Master] where {[Version].[Version Name].[CWV_MP]};

    Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item]
         * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week] * [Delivery Week].[Delivery Week] );
        Measure.[PO Process_Item Unit Load Mix Match Chk(P)] = null;
        Measure.[PO Process_Item Unit Load Mix Match(P)] = null;
        Measure.[PO Process_Lane Load Mix Match Chk(P)] = null;
        Measure.[PO Process_Lane Load Mix Match(P)] = null;
        Measure.[PO Process_Valid Fail Reason(P)] = null;
    end scope;

    Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item]
         * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week] );
        Measure.[PO Process Detail_Item Unit Load Mix Match Chk(P)] = null;
        Measure.[PO Process Detail_Item Unit Load Mix Match(P)] = null;
        Measure.[PO Process Detail_Lane Load Mix Match Chk(P)] = null;
        Measure.[PO Process Detail_Lane Load Mix Match(P)] = null;
        Measure.[PO Process Detail_Valid Fail Reason(P)] = null;
    end scope;

"""
import inspect
import os.path
import time
import datetime
import pandas as pd
import numpy as np
import traceback
import re
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_POProcessValidNLoad_REG"
str_input_dir = "Input/UIPOProcessValidNLoadREG"
str_output_dir = "Output/UIPOProcessValidNLoadREG"
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
def fn_set_target(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Validation 수행단계 따라 수행 범위 설정
    P: 무조건 전체 수행(Last Step 1)
    M: Last Step이 2인 행만 수행(PO Process Detail_Last Step)
    ADJ1: Last Step 2와 3인 건들에 대해서 수행, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 3으로 없데이트
    ADJ1: Last Step 3과 4인 건들에 대해서 수행, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 4로 없데이트
    ADJ1: Last Step 4와 5인 건들에 대해서 수행, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 5로 없데이트
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

    # 각 Step별 대상 Last Step 지정
    int_last_step = [0]
    if Param_Step == "P":
        int_last_step = [1]
    elif Param_Step == "M":
        int_last_step = [2]
    elif Param_Step == "ADJ1":
        int_last_step = [2, 3]
    elif Param_Step == "ADJ2":
        int_last_step = [3, 4]
    elif Param_Step == "ADJ3":
        int_last_step = [4, 5]

    int_inx = 0
    for int_step in int_last_step:
        if int_inx == 0:
            int_inx = int_inx + 1
            list_where = (df_p_source["M.Last_Step"] == int_step)
        else:
            int_inx = int_inx + 1
            list_where = list_where | (df_p_source["M.Last_Step"] == int_step)

    # 대상 데이터만 복사
    df_return = df_p_source.loc[list_where].copy(deep=True)

    return df_return


@_decoration_
def fn_preprocess(df_p_source: pd.DataFrame, list_p_measure_group: list, int_p_inx: int) -> pd.DataFrame:
    """
        Step 0. 전처리
        - 수행 단계에 따라 데이터 범위를 정한다.
            P : 무조건 전체 수행
            M : Last Step이 2인 행만 수행(PO Process Detail_Last Step)
            ADJ1: Last Step 2와 3인 건들에 대해서 수행, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 3으로 없데이트
            ADJ1: Last Step 3과 4인 건들에 대해서 수행, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 4로 없데이트
            ADJ1: Last Step 4와 5인 건들에 대해서 수행, 시뮬레이션 종료 후 해당 건들에 대해 Last Step을 5로 없데이트
        - 수행에 편리하도록 컬럼명을 줄여서 Rename 한다.
        - 수행 시 오류가 발생하는 컬럼들에 대해서 Data Type을 지정해준다.
    :param df_p_source:
    :param list_p_measure_group: 전처리 대상 Measure Group 정보
    :param int_p_inx: 현재 전처리 수행 요청된 Measure Group의 index
    :return: 전처리된 DataFrame
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

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # Dimension을 대상으로 Rename
    df_return.rename(columns={
        "Sub Location.[Sub Location]": "D.FromSite",
        "Shipment Type.[Shipment Type]": "D.ShipmentType",
        "Location.[Location]": "D.ToSite",
        "Location.[Shipment Type]": "D.ShipmentType",
        "Sales Domain.[Ship To]": "D.Account",
        "Seq.[Seq]": "D.Seq",
        "Item.[Item]": "D.Item",
        "Loading Type.[Loading Type]": "D.LoadingType",
        "Container.[ContainerID]": "D.CntrType",
        "MFG Week.[MFG Week]": "Time.[Week]",
        "Time.[Week]": "D.POWeek",
        "SOP Week.[SOP Week]": "D.SOPWeek",
        "Delivery Week.[Delivery Week]": "D.DlvrWeek"
    }, inplace=True)
    if int_p_inx == 12:
        # Measure를 대상으로 Rename
        # Cntr Master의 경우 Item ULD와 Measure명이 충돌하여 C를 추가로 부여함.
        df_return.rename(
            columns=lambda x: x.replace(f"{list_p_measure_group[int_p_inx]}_", "M.C").replace(" ", "_"), inplace=True)
    else:
        # Measure를 대상으로 Rename
        df_return.rename(
            columns=lambda x: x.replace(f"{list_p_measure_group[int_p_inx]}_", "M.").replace(" ", "_"), inplace=True)
    if int_p_inx < 13:
        # Master, Method의 경우에는 Measure Group 명을 데이터프레임에 추가함.
        df_return["MeasureGroup"] = list_p_measure_group[int_p_inx]
        # Seq의 경우 로직에 사용되지 않으므로 Drop
        if "D.Seq" in df_return.columns:
            df_return.drop(columns="D.Seq", axis=0, inplace=True)

    # Account와 Ship To에 대해 Object로 형 변환
    if "D.Account" in df_return.columns:
        df_return["D.Account"] = df_return["D.Account"].astype("object")
    if "M.Account" in df_return.columns:
        df_return["M.Account"] = df_return["M.Account"].fillna("-").astype("object")
    if "M.Ship_To" in df_return.columns:
        df_return["M.Ship_To"] = df_return["M.Ship_To"].fillna("-").astype("object")

    if int_p_inx == 8 or int_p_inx == 9:
        # Loading Method Mix To/Ship To 중복 제거 기준
        list_base_duplication = ["D.FromSite", "D.ToSite", "D.Item", "M.Ship_To", "M.Loading_Type", "M.Cntr_Type"]
        # 불필요 컬럼 삭제
        if int_p_inx == 8:
            df_return.drop(columns=["M.Group_Id", "Loading_Method_Mix_Ship_To_Detail_Valid_Flag"], axis=1, inplace=True)
        elif int_p_inx == 9:
            list_base_duplication = ["D.FromSite", "D.ToSite", "D.Item", "M.Loading_Type", "M.Cntr_Type"]
            df_return.drop(columns=["M.Group_Id", "Loading_Method_Mix_To_Site_Detail_Valid_Flag"], axis=1, inplace=True)
        df_return.drop_duplicates(subset=list_base_duplication, keep="first", inplace=True)
    elif int_p_inx == 13:
        # PO Process - Block 1
        # 로직 수행에 필요한 컬럼만 추출
        df_return = df_return[[
            "Time.[Week]", "D.FromSite", "D.ToSite", "D.Item", "D.POWeek", "D.SOPWeek",
            "M.Data_Source", f"M.Check_Qty({Param_Step})"
        ]]
        # 각 컬럼의 Data Type 변경 및 초기값 설정
        # df_return[f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = (
        #     df_return[f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"].astype("object"))
        # df_return[f"M.Lane_Load_Mix_Match_Chk({Param_Step})"] = (
        #     df_return[f"M.Lane_Load_Mix_Match_Chk({Param_Step})"].astype("object"))
        # df_return[f"M.Valid_Fail_Reason({Param_Step})"] = (
        #     df_return[f"M.Valid_Fail_Reason({Param_Step})"].astype("object"))
        # df_return[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] = STR_NOT_DEFINED
        # df_return[f"M.Lane_Load_Mix_Match({Param_Step})"] = STR_NOT_DEFINED
    elif int_p_inx == 14:
        # PO Process Detail - Block 2
        df_return = fn_set_target(df_return)
        if Param_Step == "P" or Param_Step == "M":
            df_return = df_return[[
                "Time.[Week]", "D.FromSite", "D.ToSite", "D.ShipmentType", "D.Item", "D.Seq", "D.POWeek", "M.SOP_ETD_Week",
                "M.Account", "M.Ship_To", "M.Block", "M.Last_Step", f"M.POP_Qty({Param_Step})",
                f"M.Short_Qty({Param_Step})", f"M.Check_Qty({Param_Step})", f"M.Item_Unit_Load_Mix_Match({Param_Step})",
                f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})", f"M.Lane_Load_Mix_Match({Param_Step})",
                f"M.Lane_Load_Mix_Match_Chk({Param_Step})", f"M.Valid_Fail_Reason({Param_Step})",
            ]]
        else:
            df_return = df_return[[
                "Time.[Week]", "D.FromSite", "D.ToSite", "D.ShipmentType", "D.Item", "D.Seq", "D.POWeek",
                "M.SOP_ETD_Week",
                "M.Account", "M.Ship_To", "M.Block", "M.Last_Step", f"M.Check_Qty({Param_Step})",
                f"M.Item_Unit_Load_Mix_Match({Param_Step})", f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})",
                f"M.Lane_Load_Mix_Match({Param_Step})", f"M.Lane_Load_Mix_Match_Chk({Param_Step})",
                f"M.Valid_Fail_Reason({Param_Step})",
            ]]
        df_return[f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = (
            df_return[f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"].astype("object"))
        df_return[f"M.Lane_Load_Mix_Match_Chk({Param_Step})"] = (
            df_return[f"M.Lane_Load_Mix_Match_Chk({Param_Step})"].astype("object"))
        df_return[f"M.Valid_Fail_Reason({Param_Step})"] = (
            df_return[f"M.Valid_Fail_Reason({Param_Step})"].astype("object"))
        df_return[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] = STR_NOT_DEFINED
        df_return[f"M.Lane_Load_Mix_Match({Param_Step})"] = STR_NOT_DEFINED
    
    return df_return


@_decoration_
def fn_set_method_default(df_p_source: pd.DataFrame, df_p_method: pd.DataFrame, list_p_measure_group: list,
                          int_p_inx: int) -> pd.DataFrame:
    """
    Method 테이블에 Default가 "Y"인 행을 찾아 해당 행의 Loading Type, Contaniner Type을 검증 대상 테이블에 적재한다.
    :param df_p_source:
    :param df_p_method: Loading Method From Site/To Site/Account/Ship To
    :param list_p_measure_group: 처리 대상 Measure Group 정보
    :param int_p_inx: 현재 처리 수행 요청된 Measure Group의 index
    :return: Default Loading Type, Container Type이 적재된 DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty or df_p_method.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source or df_p_method)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # Method에서 Default가 "Y"로 설정된 행만 추출
    list_where_default = (df_p_method["M.Default"] == "Y")
    df_method_default = df_p_method[list_where_default].copy(deep=True)

    # Default "Y"로 설정된 데이터가 없는 경우 오류 메시지를 출력한다.
    if df_method_default.empty or len(df_method_default) == 0:
        logger.Note(p_note=f'[{str_my_name}] Loading Method{list_p_measure_group[int_p_inx]}에 '
                           f'Default가 설정되어 있지 않습니다.',
                    p_log_level=LOG_LEVEL.error())
        return df_p_source

    # PO Process 데이터와 Method 테이블을 Left Joint 하기 위한 기준 컬럼 설정 - Method
    list_left_on = ["D.FromSite", "D.ToSite", "M.Account", "M.Ship_To"]
    list_right_on = ["D.FromSite", "D.ToSite", "D.Account", "M.Ship_To"]
    # 이전 단계에서 값이 채워진 행 제외

    df_return_checked = pd.DataFrame()
    if int_p_inx > 4:
        # Method 기준 Loading Type, Container Type 설정을 1번 이상 수행한 경우
        # Loading Type과 Container Type이 모두 Null인 행을 추출한다.
        if "D.LoadingType" not in df_p_source.columns:
            df_p_source["D.LoadingType"] = None
        if "D.CntrType" not in df_p_source.columns:
            df_p_source["D.CntrType"] = None
        list_where_checked = (df_p_source["D.LoadingType"].isnull()) & (df_p_source["D.CntrType"].isnull())
        df_return_checked = df_p_source[~list_where_checked].copy(deep=True)
        df_return_nchecked = df_p_source[list_where_checked].copy(deep=True)
        df_return_nchecked.drop(columns=["D.LoadingType", "D.CntrType"], inplace=True)
    else:
        # Method 기준 Loading Type, Container Type 설정을 최초로 하는 경우
        df_return_nchecked = df_p_source.copy(deep=True)

    # Join 하기 전 Join 기준 변경 처리 - 리스트 뒤에서부터 불필요한 컬럼 삭제
    del list_left_on[len(list_left_on) - (int_p_inx - 4):]
    del list_right_on[len(list_right_on) - (int_p_inx - 4):]

    # Loading Type과 Container Type이 모두 Null인 행이 있는 경우 Method와 Merge 수행
    if not df_return_nchecked.empty or len(df_return_nchecked) > 0:
        # 대상 데이터와 Method 데이터 Merge
        df_return_nchecked = (
            df_return_nchecked.merge(df_method_default, how="left",
                                     left_on=list_left_on, right_on=list_right_on,
                                     suffixes=("_X", "_Y"), indicator=True))
        df_return_nchecked.drop(columns=["_merge"], inplace=True)
        str_delete_base_column = "M.Default"
        int_delete_index = df_return_nchecked.columns.get_loc(str_delete_base_column)
        # str_delete_base_column = "M.Default" 이후의 컬럼 삭제
        df_return_nchecked = df_return_nchecked.iloc[:, :int_delete_index]

        # Master/Method Account/Ship To인 경우 Dimension에 있는 Account 삭제
        if (int_p_inx % 4) <= 1:
            # Dimension인 Account가 있는 경우에는 해당 컬럼 삭제
            df_return_nchecked.drop(columns="D.Account", axis=0, inplace=True)

    # 기설정된 데이터와 새로 설정한 데이터를 병합한다.
    df_return = pd.concat([df_return_checked, df_return_nchecked])

    return df_return


@_decoration_
def fn_arrange_po_process_column(df_p_source: pd.DataFrame, df_p_po_process: pd.DataFrame) -> pd.DataFrame:
    """
    STEP 0-19. PO Process 컬럼 정리 - Step별로 필요한 컬럼만 추출
    PO Process에서 Check Qty 복사
    :param df_p_source: PO Process
    :return: 필요 컬럼만 추출된 PO Process DataFrame
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

    if df_p_po_process.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # 로직 수행에 필요한 컬럼만 추출
    if Param_Step == "P" or Param_Step == "M":
        df_return = df_return[[
            "Time.[Week]", "D.FromSite", "D.ToSite", "D.ShipmentType", "D.Item", "D.LoadingType", "D.CntrType", "D.Seq",
            "D.POWeek", "M.SOP_ETD_Week", "M.Account", "M.Ship_To", "M.Block", f"M.POP_Qty({Param_Step})",
            f"M.Short_Qty({Param_Step})", f"M.Check_Qty({Param_Step})",
            f"M.Item_Unit_Load_Mix_Match({Param_Step})", f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})",
            f"M.Lane_Load_Mix_Match({Param_Step})", f"M.Lane_Load_Mix_Match_Chk({Param_Step})",
            f"M.Valid_Fail_Reason({Param_Step})",
        ]]
    else:
        df_return = df_return[[
            "Time.[Week]", "D.FromSite", "D.ToSite", "D.ShipmentType", "D.Item", "D.LoadingType", "D.CntrType", "D.Seq",
            "D.POWeek", "M.SOP_ETD_Week", "M.Account", "M.Ship_To", "M.Block", f"M.Check_Qty({Param_Step})",
            f"M.Item_Unit_Load_Mix_Match({Param_Step})", f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})",
            f"M.Lane_Load_Mix_Match({Param_Step})", f"M.Lane_Load_Mix_Match_Chk({Param_Step})",
            f"M.Valid_Fail_Reason({Param_Step})",
        ]]

    # PO Process의 Check Qty를 복사하기 위해 Split과 관계없는 행(INDIR) 추출
    # DIR_PO는 하단에서 수정 가능하기 때문에 제외
    # list_where_po_only = (df_return["M.Block"] == "INDIR") | (df_return["M.Block"] == "DIR_PO")
    list_where_po_only = (df_return["M.Block"] == "INDIR")
    df_return_po_only = df_return[list_where_po_only].copy(deep=True)
    df_return_both = df_return[~list_where_po_only].copy(deep=True)

    # 추출한 데이터를 PO Process Detail에 Left Join
    if not df_return_po_only.empty and len(df_return_po_only) > 0:
        df_return_merged = df_return_po_only.merge(
            df_p_po_process,
            how="left",
            left_on=["Time.[Week]", "D.FromSite", "D.ToSite", "D.Item", "D.POWeek", "M.SOP_ETD_Week"],
            right_on=["Time.[Week]", "D.FromSite", "D.ToSite", "D.Item", "D.POWeek", "D.SOPWeek"],
            suffixes=("_x", "_y"), indicator=True)

        list_where_both = (df_return_merged["_merge"] == "both")
        df_return_merged_both = df_return_merged[list_where_both].copy(deep=True)
        df_return_merged_left = df_return_merged[~list_where_both].copy(deep=True)
        if not df_return_merged_both.empty or len(df_return_merged_both) > 0:
            df_return_merged_both[f"M.Check_Qty({Param_Step})_x"] = df_return_merged_both[f"M.Check_Qty({Param_Step})_y"]

        df_return_po_only = pd.concat([df_return_merged_left, df_return_merged_both])
        df_return_po_only = fn_merge_after(df_return_po_only)
        df_return_po_only.drop(columns=["D.SOPWeek", "M.Data_Source", "_merge"], inplace=True)

    df_return = pd.concat([df_return_both, df_return_po_only])

    return df_return


@_decoration_
def fn_merge_master_n_method(
        df_p_source: pd.DataFrame, df_p_master: pd.DataFrame, list_p_measure_group: list, int_p_inx: int,
        str_p_cond: str = '0'
) -> pd.DataFrame:
    """
    Master/Method 데이터를 검증 대상 테이블에 적재한다.
    :param df_p_source: PO Process Detail
    :param df_p_master: Loading Master From Site/To Site/Account/Ship To
                        Loading Method From Site/To Site/Account/Ship To
    :param list_p_measure_group: 처리 대상 Measure Group 정보
    :param int_p_inx: 현재 처리 수행 요청된 Measure Group의 index
    :param str_p_cond: 0: Method From Site의 경우 Shipment Type을 제외하고 From, Loading Type, Cntr Type으로 중복이 있는 경우,
                          Default가 "Y"인 것을 남기고 나머지 제거
                       1: Method From Site의 경우 Shipment Type을 Join 기준에 추가
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty or df_p_master.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source or df_p_master)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # PO Process 데이터와 Master/Method 테이블을 Left Join 하기 위한 기준 컬럼 설정 - Master
    list_left_on = ["D.FromSite", "D.Item", "D.LoadingType", "D.CntrType", "D.ToSite", "M.Account", "M.Ship_To"]
    list_right_on = ["D.FromSite", "D.Item", "D.LoadingType", "D.CntrType", "D.ToSite", "D.Account", "M.Ship_To"]
    # 컬럼 삭제 시 삭제 시점 보정값
    int_correction_value = 0
    # Master에서 조회되어 이미 값이 채워진 행
    list_where_checked = df_p_source[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] != STR_NOT_DEFINED
    # Join 이후 컬럼 삭제 기준
    str_delete_base_column = f"M.Valid_Fail_Reason({Param_Step})"
    if int_p_inx >= 4:
        # PO Process 데이터와 Master/Method 테이블을 Left Join 하기 위한 기준 컬럼 설정 - Method
        list_left_on = ["D.FromSite", "D.LoadingType", "D.CntrType", "D.ToSite", "M.Account", "M.Ship_To"]
        list_right_on = ["D.FromSite", "D.LoadingType", "D.CntrType", "D.ToSite", "D.Account", "M.Ship_To"]
        # 컬럼 삭제 시 삭제 시점 보정값
        int_correction_value = 4
        # Method에서 조회되어 이미 값이 채워진 행
        list_where_checked = df_p_source[f"M.Lane_Load_Mix_Match({Param_Step})"] != STR_NOT_DEFINED
        # Join 이후 테이블 정리 시 컬럼 삭제 기준
        str_delete_base_column = "M.Depth"
    # Master/Method가 이미 채워진 행
    df_return_checked = df_p_source[list_where_checked].copy(deep=True)
    # Master/Method가 채워지지 않은 행
    df_return = df_p_source[~list_where_checked].copy(deep=True)

    # Join 하기 전 컬럼 삭제
    int_delete_index = df_return.columns.get_loc(str_delete_base_column)
    df_return = df_return.iloc[:, :int_delete_index + 1]

    # Join 하기 전 Join 기준 변경 처리 - 리스트 뒤에서부터 불필요한 컬럼 삭제
    del list_left_on[len(list_left_on) - (int_p_inx - int_correction_value):]
    del list_right_on[len(list_right_on) - (int_p_inx - int_correction_value):]

    if int_p_inx == 7:
        if str_p_cond == "0":
            # Method From Site의 경우 Shipment Type을 제외하고 From, Loading Type, Cntr Type으로 중복이 있는 경우,
            # Default가 "Y"인 것을 남기고 나머지 제거
            df_p_master.sort_values(by=["D.FromSite", "D.LoadingType", "D.CntrType", "M.Default"],
                                    ascending=[True, True, True, False], inplace=True)
            df_p_master = df_p_master.drop_duplicates(
                subset=["D.FromSite", "D.LoadingType", "D.CntrType"], keep="first")
        else:
            # Method From Site의 경우 Shipment Type을 Join 기준에 추가
            list_left_on.append("D.ShipmentType")
            list_right_on.append("D.ShipmentType")
    # PO Process와 Master/Method를 Left Join
    df_return = df_return.merge(
        df_p_master, how="left", left_on=list_left_on, right_on=list_right_on, suffixes=("_x", "_y"), indicator=True)

    df_return_filled = pd.DataFrame()
    # Join 후처리
    if "_merge" in df_return.columns:
        # Master/Method가 채워진 경우
        list_where_filled = df_return["_merge"] == "both"
        # Master/Method가 채워진 테이블
        df_return_filled = df_return[list_where_filled].copy(deep=True)
        # Master/Method가 채워지지 않은 테이블
        df_return = df_return[~list_where_filled].copy(deep=True)

        # Master/Method가 채워진 테이블에 데이터가 존재하는 경우
        if not df_return_filled.empty:
            if int_p_inx < 4:
                # Master 관련 후처리
                # MeasureGroup을 이용하여 Mix Match에 어느 Master인지를 업데이트
                df_return_filled[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] = (
                    df_return_filled["MeasureGroup"].str.replace("Loading Master ", ""))
            else:
                # Method 관련 후처리
                # MeasureGroup을 이용하여 Mix Match에 어느 Method인지를 업데이트
                df_return_filled[f"M.Lane_Load_Mix_Match({Param_Step})"] = (
                    df_return_filled["MeasureGroup"].str.replace("Loading Method ", ""))

    # 분리된 데이터를 모두 병합
    df_return = pd.concat([df_return_checked, df_return_filled, df_return])

    # 불필요 컬럼 삭제
    str_delete_base_column = "MeasureGroup"
    if int_p_inx == 3:
        str_delete_base_column = "M.Valid_Flag"
    int_delete_index = df_return.columns.get_loc(str_delete_base_column)
    df_return = df_return.iloc[:, :int_delete_index]

    # Master/Method Account/Ship To인 경우 Dimension에 있는 Account 삭제
    if (int_p_inx % 4) <= 1:
        # Dimension인 Account가 있는 경우에는 해당 컬럼 삭제
        df_return.drop(columns="D.Account", axis=0, inplace=True)

    return df_return


@_decoration_
def fn_merge_method_mix(
        df_p_source: pd.DataFrame, df_p_method_mix: pd.DataFrame, list_p_measure_group: list, int_p_inx: int
) -> pd.DataFrame:
    """
    Loading Method Mix To Site/Ship To 데이터를 검증 대상 테이블에 적재한다.
    :param df_p_source: PO Process Detail
    :param df_p_method_mix: Loading Method Mix To Site/Ship To
    :param list_p_measure_group: 처리 대상 Measure Group 정보
    :param int_p_inx: 현재 처리 수행 요청된 Measure Group의 index
    :return: Loading Method Mix To Site/Ship To 데이터가 적재된 DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty or df_p_method_mix.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source or df_p_method_mix)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 혼적 기준이 Item Mix Group인 데이터 추출
    list_where_1st_mix = (df_p_source["M.1st_Mix"] == "Item Mix Group")
    list_where_2nd_mix = (df_p_source["M.2nd_Mix"] == "Item Mix Group")
    list_where_3rd_mix = (df_p_source["M.3rd_Mix"] == "Item Mix Group")
    list_where_mix_group = list_where_1st_mix | list_where_2nd_mix | list_where_3rd_mix
    if int_p_inx == 9:
        # Loading Method Mix To Site인 경우 혼적 기준이 Item Mix Group이면서 Item Mix Group 컬럼이 Null인 데이터 추출
        if "M.Item_Mix_Group" in df_p_source.columns:
            list_where_item_mix_group = (df_p_source["M.Item_Mix_Group"].isnull())
            list_where_mix_group = ((list_where_1st_mix | list_where_2nd_mix | list_where_3rd_mix) &
                                    list_where_item_mix_group)
    # 혼적 기준이 Item Mix Group인 데이터
    df_return_mix = df_p_source[list_where_mix_group].copy(deep=True)
    # 혼적 기준이 Item Mix Group이 아닌 데이터
    df_return_no_mix = df_p_source[~list_where_mix_group].copy(deep=True)

    # Merger 조건 설정
    list_left_on = ["D.FromSite", "D.ToSite", "D.Item", "D.LoadingType", "D.CntrType", "M.Ship_To"]
    list_right_on = ["D.FromSite", "D.ToSite", "D.Item", "M.Loading_Type", "M.Cntr_Type", "M.Ship_To"]
    if not df_return_mix.empty and len(df_return_mix) > 0:
        if int_p_inx == 9:
            # Loading Method Mix To Site의 경우
            list_left_on = ["D.FromSite", "D.ToSite", "D.Item", "D.LoadingType", "D.CntrType"]
            list_right_on = ["D.FromSite", "D.ToSite", "D.Item", "M.Loading_Type", "M.Cntr_Type"]
            if "M.Item_Mix_Group" in df_return_mix.columns:
                # Item Mix Group 컬럼이 있는 경우 merge 후 컬럼 중복이 발생하기 때문에 삭제 처리
                df_return_mix.drop(columns="M.Item_Mix_Group", axis=0, inplace=True)
        # Loading Method Mix를 Left Join
        df_return_mix = df_return_mix.merge(
            df_p_method_mix, how="left",
            left_on=list_left_on, right_on=list_right_on, suffixes=("_x", "_y"), indicator=True)
        # 불필요 컬럼 삭제
        str_delete_base_column = "M.Loading_Type"
        int_delete_index = df_return_mix.columns.get_loc(str_delete_base_column)
        df_return_mix = df_return_mix.iloc[:, :int_delete_index]

    # 분할된 데이터 병합
    df_return = pd.concat([df_return_no_mix, df_return_mix])

    return df_return


@_decoration_
def fn_validate_min_qty_n_check_qty(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Min Qty와 Check Qty를 비교하여 Check Qty가 Min Qty보다 적은 경우 오류를 기재한다.
    :param df_p_source: 검증 대상 테이블
    :return: 검증 결과가 기재된 DataFrame
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

    str_chech_qty_column = ""
    if Param_Check_Qty == "Current":
        str_chech_qty_column = f"M.Check_Qty({Param_Step})"
    elif Param_Check_Qty == "POPOnly":
        str_chech_qty_column = f"M.POP_Qty({Param_Step})"
    elif Param_Check_Qty == "POPShort":
        df_return["POP N Short Qty"] = (df_return[f"M.POP_Qty({Param_Step})"].fillna(0) +
                                        df_return[f"M.Short_Qty({Param_Step})"].fillna(0))
        str_chech_qty_column = "POP N Short Qty"

    df_return["Valid Chk Qty"] = df_return[str_chech_qty_column].fillna(0).astype(int)
    # Master가 조회된 행만 추출
    list_where_master = df_return[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] != STR_NOT_DEFINED
    # Master가 조회된 데이터
    df_return_master = df_return[list_where_master].copy(deep=True)
    # Master가 조회되지 않은 데이터
    df_return_no_master = df_return[~list_where_master].copy(deep=True)
    if not df_return_master.empty and len(df_return_master) > 0:
        # 동일 Lane, 동일 Loading Type/Cntr Type을 기준으로 Qty Sum을 기록
        df_return_master["Sum of Chk Qty"] = (
            df_return_master.groupby(
                ["D.FromSite", "D.Item", "D.ToSite", "M.Account", "M.Ship_To", "Time.[Week]", "D.LoadingType",
                 "D.CntrType"
                 ])["Valid Chk Qty"].transform("sum"))
        df_return_master["Sum of Chk Qty"] = df_return_master["Sum of Chk Qty"].fillna(0)

        # 위에서 구한 Qty Sum이 Min Qty 미만인 경우 오류로 판단
        list_where_min_qty_chk = df_return_master["Sum of Chk Qty"] < df_return_master["M.Min_Qty"]
        df_return_master.loc[list_where_min_qty_chk, f"M.Valid_Fail_Reason({Param_Step})"] = (
            df_return_master.loc[list_where_min_qty_chk].apply(
                lambda row: row[f"M.Valid_Fail_Reason({Param_Step})"] + ", " + STR_MIN_QTY_ERR1
                if pd.notnull(row[f"M.Valid_Fail_Reason({Param_Step})"]) else STR_MIN_QTY_ERR1, axis=1))
        df_return_master.loc[list_where_min_qty_chk, f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = "N"

    # 분할된 데이터 병합
    df_return = pd.concat([df_return_no_master, df_return_master])

    return df_return


@_decoration_
def fn_validate_min_qty_multiple(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Min Qty, Multiple 검증
    : 0 또는 null인 경우 오류
    :param df_p_source: PO Process Detail
    :return: 검증 결과가 기재된 DataFrame
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

    # Master가 조회된 행만 추출
    list_where = df_p_source[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] != STR_NOT_DEFINED
    # Master가 조회된 테이블
    df_return = df_p_source[list_where].copy(deep=True)
    # Master가 조회되지 않은 테이블
    df_return_no_master = df_p_source[~list_where].copy(deep=True)
    if not df_return.empty and len(df_return) > 0:
        # Min Qty가 없거나 0인 경우
        list_where_min_qty_err = (df_return["M.Min_Qty"].isnull()) | (df_return["M.Min_Qty"] == 0)
        df_return.loc[list_where_min_qty_err, f"M.Valid_Fail_Reason({Param_Step})"] = (
            df_return.loc[list_where_min_qty_err].apply(
                lambda row: row[f"M.Valid_Fail_Reason({Param_Step})"] + ", " + STR_MIN_QTY_ERR2
                if pd.notnull(row[f"M.Valid_Fail_Reason({Param_Step})"]) else STR_MIN_QTY_ERR2, axis=1))
        # Multiple이 없거나 0인 경우
        list_where_multiple_err = (df_return["M.Multiple"].isnull()) | (df_return["M.Multiple"] == 0)
        df_return.loc[list_where_multiple_err, f"M.Valid_Fail_Reason({Param_Step})"] = (
            df_return.loc[list_where_multiple_err].apply(
                lambda row: row[f"M.Valid_Fail_Reason({Param_Step})"] + ", " + STR_MULTIPLE_ERR1
                if pd.notnull(row[f"M.Valid_Fail_Reason({Param_Step})"]) else STR_MULTIPLE_ERR1, axis=1))

        list_where = list_where_min_qty_err | list_where_multiple_err
        df_return.loc[list_where, f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = "N"

    df_return = pd.concat([df_return_no_master, df_return])

    return df_return


@_decoration_
def fn_validate_fill_rate_type(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Fill Rate Type 및 Max Load Qty/LDM Qty 데이터 검증
    : Fill Rate Type이 M/L Qty이면서 Max Load Qty 컬럼이 0 또는 null이면 오류
    : Fill Rate Type이 LDM Qty이면서 LDM Qty 컬럼이 0 또는 null이면 오류
    :param df_p_source: PO Process Detail
    :return: 검증 결과가 기재된 DataFrame
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

    # Master 데이터가 있는 행만 추출
    list_where = df_p_source[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] != STR_NOT_DEFINED
    df_return = df_p_source[list_where].copy(deep=True)
    df_return_no_master = df_p_source[~list_where].copy(deep=True)
    if not df_return.empty and len(df_return) > 0:
        # Single/Mix Fill Rate Type이 M/L Qty이면 Max Load Qty가 없는 경우는 오류 처리한다.
        list_where_ml_qty = (df_return["M.Single_FR_Type"] == "M/L Qty") | (df_return["M.Mix_FR_Type"] == "M/L Qty")
        list_where_ml_qty_err = (df_return["M.Max_Load_Qty"].isnull()) | (df_return["M.Max_Load_Qty"] == 0)
        list_where = list_where_ml_qty & list_where_ml_qty_err
        # Valid Fail Reason에 오류 사유를 기록한다. 기 기록된 내용이 있는 경우 ,로 구분하여 추가 기록한다.
        df_return.loc[list_where, f"M.Valid_Fail_Reason({Param_Step})"] = (
            df_return.loc[list_where].apply(
                lambda row: row[f"M.Valid_Fail_Reason({Param_Step})"] + ", " + STR_MLQTY_ERR1
                if pd.notnull(row[f"M.Valid_Fail_Reason({Param_Step})"]) else STR_MLQTY_ERR1, axis=1))
        # Item Unit Load Mix Match Chk에 "N"을 기록한다.
        df_return.loc[list_where, f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = "N"

        # Single/Mix Fill Rate Type이 LDM Qty이면 LDM Qty가 없는 경우는 오류 처리한다.
        list_where_ml_qty = (df_return["M.Single_FR_Type"] == "LDM") | (df_return["M.Mix_FR_Type"] == "LDM")
        list_where_ml_qty_err = (df_return["M.LDM_Qty"].isnull()) | (df_return["M.LDM_Qty"] == 0)
        list_where = list_where_ml_qty & list_where_ml_qty_err
        # Valid Fail Reason에 오류 사유를 기록한다. 기 기록된 내용이 있는 경우 ,로 구분하여 추가 기록한다.
        df_return.loc[list_where, f"M.Valid_Fail_Reason({Param_Step})"] = (
            df_return.loc[list_where].apply(
                lambda row: row[f"M.Valid_Fail_Reason({Param_Step})"] + ", " + STR_LDMQTY_ERR1
                if pd.notnull(row[f"M.Valid_Fail_Reason({Param_Step})"]) else STR_LDMQTY_ERR1, axis=1))
        # Item Unit Load Mix Match Chk에 "N"을 기록한다.
        df_return.loc[list_where, f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = "N"

    # 분할된 데이터를 병합한다.
    df_return = pd.concat([df_return_no_master, df_return])

    return df_return


@_decoration_
def fn_merge_item_uld(df_p_source: pd.DataFrame, df_p_item_uld: pd.DataFrame) -> pd.DataFrame:
    """
    Item ULD에서 값을 가져와 PO Process에 채운다.
        * LDM 케이스에서 사이즈로 직접 계산하는 로직이 제거되어 이 부분은 필요없음.
    :param df_p_source:
    :param df_p_item_uld:
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

    # Item을 기준으로 PO Process에 Item ULD를 Left Join한다.
    df_return = pd.merge(df_p_source, df_p_item_uld, how='left', left_on='D.Item', right_on='D.Item')

    return df_return


@_decoration_
def fn_merge_profit_grade(df_p_source: pd.DataFrame, df_p_profit_grage: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4. Loading Profit Grade에서 값을 가져와 검증 대상 데이터에 적재한다.
    :param df_p_source: PO Process
    :param df_p_profit_grage: Profit Grade
    :return: Dataframe
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty or df_p_profit_grage.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source or df_p_profit_grage)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # PO Process와 Profit Grade를 [Location].[Location], [Item].[Item] 기준으로 Left Join한다.
    df_return = pd.merge(df_p_source, df_p_profit_grage, how='left', on=["D.ToSite", "D.Item"])
    # Profit Grade/Profit Grade Priority가 비어 있는 경우에는 C/3으로 통일하여 저장
    df_return["M.Profit_Grade"].fillna("C", inplace=True)
    df_return["M.Profit_Grade_Priority"].fillna(3, inplace=True)
    # MeasureGroup 컬럼 삭제
    df_return.drop(columns="MeasureGroup", inplace=True)

    return df_return


@_decoration_
def fn_validate_item_mix_group(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Item Mix Group 관련 검증
    : 혼적 유형이 Item Mix Group이면서 Item Mix Group 컬럼이 null이면 오류
    :param df_p_source: PO Process Detail
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

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # 혼적 유형이 Item Mix Group인 경우를 추출한다.
    list_where_1st_mix = (df_return["M.1st_Mix"] == "Item Mix Group")
    list_where_2nd_mix = (df_return["M.2nd_Mix"] == "Item Mix Group")
    list_where_3rd_mix = (df_return["M.3rd_Mix"] == "Item Mix Group")
    if not "M.Item_Mix_Group" in df_return.columns:
        # Item Mix Group 컬럼이 없는 경우 컬럼 생성 후 값을 None으로 설정
        df_return["M.Item_Mix_Group"] = None
    # 혼적 유형이 Item Mix Group이면서 Item Mix Group 컬럼에 데이터가 적재되지 않은 행 추출
    list_where_no_mix_group = (df_return["M.Item_Mix_Group"].isnull())
    list_where = (list_where_1st_mix | list_where_2nd_mix | list_where_3rd_mix) & list_where_no_mix_group
    # 오류 사유에 Item Mix Group 오류로 기재
    df_return.loc[list_where, f"M.Valid_Fail_Reason({Param_Step})"] = (
        df_return.loc[list_where].apply(
            lambda row: row[f"M.Valid_Fail_Reason({Param_Step})"] + ", " + STR_MIX_GRP_ERR
            if pd.notnull(row[f"M.Valid_Fail_Reason({Param_Step})"]) else STR_MIX_GRP_ERR, axis=1))

    return df_return


@_decoration_
def fn_validate_profit_grade(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Profit Grade 관련 Default 값 설정
    :param df_p_source: PO Process Detail
    :return: Profit Grade컬럼에 Default 값이 적재된 DataFrame
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
    if not "M.Profit_Grade" in df_return.columns:
        # Profit Grade 컬럼이 없는 경우 컬럼 생성 후 값을 None으로 설정
        df_return["M.Profit_Grade"] = None
        # Profit Grade Priority 컬럼 생성 후 값을 None으로 설정
        df_return["M.Profit_Grade_Priority"] = None
    # Profit Grade 컬럼이 Null인 행 추출
    list_where_profit_grade_none = df_return["M.Profit_Grade"].isnull()
    # Profit Grade에 "C"를 설정
    df_return.loc[list_where_profit_grade_none, "M.Profit_Grade"] = "C"
    # Profit Grade Priority에 "3"을 설정
    df_return.loc[list_where_profit_grade_none, "M.Profit_Grade_Priority"] = "3"

    return df_return


@_decoration_
def fn_validate_master_n_method(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Validation 기준에 따라 데이터 검증 후 검증 결과 정리
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

    # Check Qty가 Min Qty보다 적은 경우를 찾아 오류 사유를 기록한다.
    df_return_chk_qty = fn_validate_min_qty_n_check_qty(df_p_source)

    # Min Qty, Multiple, M/L Qty 점검
    df_return_base = fn_validate_min_qty_multiple(df_return_chk_qty)

    # Fill Rate Type 관련 점검
    df_return_fr = fn_validate_fill_rate_type(df_return_base)

    # Item Mix Group 관련 점검
    df_return_mix_grp = fn_validate_item_mix_group(df_return_fr)

    # Profit Grade 관련 점검
    df_return = fn_validate_profit_grade(df_return_mix_grp)

    list_where_master_chk_null = (df_return[f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"].isnull())
    list_where_method_chk_null = (df_return[f"M.Lane_Load_Mix_Match_Chk({Param_Step})"].isnull())

    # Master Validation 결과 정리
    list_where_valid_master = ((df_return[f"M.Valid_Fail_Reason({Param_Step})"].isnull()) &
                               (df_return[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] != STR_NOT_DEFINED))
    list_where_master_y = list_where_master_chk_null & list_where_valid_master
    list_where_master_n = list_where_master_chk_null & ~list_where_valid_master
    df_return.loc[list_where_master_y, f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = "Y"
    df_return.loc[list_where_master_n, f"M.Item_Unit_Load_Mix_Match_Chk({Param_Step})"] = "N"
    # Method Validation 결과 정리
    list_where_valid_method = ((df_return[f"M.Valid_Fail_Reason({Param_Step})"].isnull()) &
                               (df_return[f"M.Lane_Load_Mix_Match({Param_Step})"] != STR_NOT_DEFINED))
    list_where_method_y = list_where_method_chk_null & list_where_valid_method
    list_where_method_n = list_where_method_chk_null & ~list_where_valid_method
    df_return.loc[list_where_method_y, f"M.Lane_Load_Mix_Match_Chk({Param_Step})"] = "Y"
    df_return.loc[list_where_method_n, f"M.Lane_Load_Mix_Match_Chk({Param_Step})"] = "N"

    return df_return


@_decoration_
def fn_create_loading_master_from_site(
        df_p_source: pd.DataFrame, df_p_from_site_nvalid: pd.DataFrame, df_p_item_uld: pd.DataFrame
) -> pd.DataFrame:
    """
    Master가 적재되지 않은 행에 대해 해당 행의 데이터를 기준으로 Master 내용 생성
    :param df_p_source: PO Process Detail
    :param df_p_from_site_nvalid: Master From Site에서 Valid가 N으로 설정된 데이터
    :param df_p_item_uld: Item ULD
    :return: Dataframe
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

    # Master Match 처리 후 Match되지 않은 건(Not Defined)에 대해서 생성
    list_where = (df_p_source[f"M.Item_Unit_Load_Mix_Match({Param_Step})"] == STR_NOT_DEFINED)
    df_return_n_defined = df_p_source[list_where].copy(deep=True)
    list_on = ["D.FromSite", "D.Item", "D.LoadingType", "D.CntrType"]
    # Not Defined 건에 대해서 Loading Master에서 Valid가 "N"으로 체크된 행과 일치하는 경우가 있는지 확인
    df_return_merged = (
        df_return_n_defined.merge(df_p_from_site_nvalid, how="left", on=list_on, suffixes=("_x", "_y"), indicator=True))
    # Master에 없는 데이터
    list_where_not_in_master = (df_return_merged["_merge"] == "left_only")
    # Loading Type이 Null인 데이터
    list_where_loading_type_null = (df_return_merged["D.LoadingType"].isnull())
    # Cntr Type이 Null인 데이터
    list_where_cntr_type_null = (df_return_merged["D.CntrType"].isnull())
    # Master에 등록되지 않은 데이터이면서 Loading Type도 Cntr Type도 Null이 아닌 데이터
    list_where = list_where_not_in_master & ~list_where_loading_type_null & ~list_where_cntr_type_null
    df_return_po = df_return_merged[list_where].copy(deep=True)

    # Master에 등록할 키를 기준으로 중복 키 삭제
    df_return_po = df_return_po[["D.FromSite", "D.Item", "D.LoadingType", "D.CntrType"]]
    df_return_po.drop_duplicates(inplace=True)

    # Master에 등록할 데이터에 Item ULD 데이터 적재
    df_return = df_return_po.merge(df_p_item_uld, how="left", on="D.Item")
    df_return["Version.[Version Name]"] = Param_OUT_VERSION

    return df_return


@_decoration_
def fn_postprocess(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    전처리를 통해 Rename했던 컬럼들을 원래 명칭으로 복원
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
    # Version 컬럼 추가
    df_return["Version.[Version Name]"] = Param_OUT_VERSION
    df_return = df_return.rename(columns={
        "D.FromSite": "Sub Location.[Sub Location]",
        "D.ShipmentType": "Shipment Type.[Shipment Type]",
        "D.ToSite": "Location.[Location]",
        "D.Account": "Sales Domain.[Ship To]",
        "D.Seq": "Seq.[Seq]",
        "D.Item": "Item.[Item]",
        "D.LoadingType": "Loading Type.[Loading Type]",
        "D.CntrType": "Container.[ContainerID]",
        "Time.[Week]": "MFG Week.[MFG Week]",
        "D.POWeek": "Time.[Week]",
        "D.SOPWeek": "SOP Week.[SOP Week]",
        "D.DlvrWeek": "Delivery Week.[Delivery Week]"
    })
    df_return.rename(columns=lambda x: x.replace("_", " ").replace("M.", "PO Process Detail_"), inplace=True)
    # Valid Fail Reason 컬럼에 대해 nan인 경우 None 값 적용
    df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"] = (
        df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"].
        where(df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"].notnull(), None))

    return df_return


@_decoration_
def fn_output_formatter_po_process_detail(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    PO Process Detail 테이블을 Output 형식에 맞춰 정리
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
        return df_return

    # 필요한 컬럼만 추출
    df_return = df_p_source[[
        "Version.[Version Name]", "MFG Week.[MFG Week]", "Sub Location.[Sub Location]", "Location.[Location]",
        "Item.[Item]", "Seq.[Seq]", "Time.[Week]", "PO Process Detail_SOP ETD Week",
        f"PO Process Detail_Check Qty({Param_Step})", f"PO Process Detail_Item Unit Load Mix Match({Param_Step})",
        f"PO Process Detail_Item Unit Load Mix Match Chk({Param_Step})",
        f"PO Process Detail_Lane Load Mix Match({Param_Step})",
        f"PO Process Detail_Lane Load Mix Match Chk({Param_Step})", f"PO Process Detail_Valid Fail Reason({Param_Step})"
    ]].copy(deep=True)
    df_return = df_return.assign(**{
        "PO Process Detail_Check Qty(FINAL)":
            df_return[f"PO Process Detail_Check Qty({Param_Step})"],
        "PO Process Detail_Item Unit Load Mix Match(FINAL)":
            df_return[f"PO Process Detail_Item Unit Load Mix Match({Param_Step})"],
        "PO Process Detail_Item Unit Load Mix Match Chk(FINAL)":
            df_return[f"PO Process Detail_Item Unit Load Mix Match Chk({Param_Step})"],
        "PO Process Detail_Lane Load Mix Match(FINAL)":
            df_return[f"PO Process Detail_Lane Load Mix Match({Param_Step})"],
        "PO Process Detail_Lane Load Mix Match Chk(FINAL)":
            df_return[f"PO Process Detail_Lane Load Mix Match Chk({Param_Step})"],
        "PO Process Detail_Valid Fail Reason(FINAL)":
            df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"]
    })

    return df_return


def fn_aggregation_po(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    상단 PO 테이블에 적재하기 위해 Detail 테이블 내용 중 특정 컬럼의 값을 Aggregation 형태로 전환함.
    - groupby후 agg()로 하여 ", ".join을 이용하는 경우 서버에서 정상적인 결과가 출력되지 않아 우회 방법으로 구현함.
    :param df_p_source: PO Process Detail
    :return: Dataframe
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # aggregation 대상 데이터가 있는 경우
    if len(df_p_source) > 1:
        # Item Unit Load Mix Match 전체 컬럼값 중 None이 아닌 행의 값에 대해서 리스트 작성
        list_master_match = (
            list(dict.fromkeys([x for x in df_p_source[f"PO Process Detail_Item Unit Load Mix Match({Param_Step})"]
                                if x is not None])))
        # Item Unit Load Mix Match Chk 전체 컬럼값 중 None이 아닌 행의 값에 대해서 리스트 작성
        list_master_match_chk = (
            list(dict.fromkeys([x for x in df_p_source[f"PO Process Detail_Item Unit Load Mix Match Chk({Param_Step})"]
                                if x is not None])))
        # Lane Load Mix Match 전체 컬럼값 중 None이 아닌 행의 값에 대해서 리스트 작성
        list_method_match = (
            list(dict.fromkeys([x for x in df_p_source[f"PO Process Detail_Lane Load Mix Match({Param_Step})"]
                                if x is not None])))
        # Lane Load Mix Match Chk 전체 컬럼값 중 None이 아닌 행의 값에 대해서 리스트 작성
        list_method_match_chk = (
            list(dict.fromkeys([x for x in df_p_source[f"PO Process Detail_Lane Load Mix Match Chk({Param_Step})"]
                                if x is not None])))
        # Valid Fail Reason 전체 컬럼값 중 None이 아닌 행의 값에 대해서 리스트 작성
        list_valid_fail_reason = (
            list(dict.fromkeys([x for x in df_p_source[f"PO Process Detail_Valid Fail Reason({Param_Step})"]
                                if x is not None])))

        # Item Unit Load Mix Match 값 리스트를 ", "로 연결
        if len(list_master_match) > 1:
            str_master_match = ", ".join(list_master_match)
        elif len(list_master_match) == 1:
            str_master_match = list_master_match[0]
        else:
            str_master_match = None
        # Item Unit Load Mix Match Chk 값 리스트를 ", "로 연결
        if len(list_master_match_chk) > 1:
            str_master_match_chk = ", ".join(list_master_match_chk)
        elif len(list_master_match_chk) == 1:
            str_master_match_chk = list_master_match_chk[0]
        else:
            str_master_match_chk = None
        # Lane Load Mix Match 값 리스트를 ", "로 연결
        if len(list_method_match) > 1:
            str_method_match = ", ".join(list_method_match)
        elif len(list_method_match) == 1:
            str_method_match = list_method_match[0]
        else:
            str_method_match = None
        # Lane Load Mix Match Chk 값 리스트를 ", "로 연결
        if len(list_method_match_chk) > 1:
            str_method_match_chk = ", ".join(list_method_match_chk)
        elif len(list_method_match_chk) == 1:
            str_method_match_chk = list_method_match_chk[0]
        else:
            str_method_match_chk = None
        # Valid Fail Reason 값 리스트를 ", "로 연결
        if len(list_valid_fail_reason) > 1:
            str_valid_fail_reason = ", ".join(list_valid_fail_reason)
        elif len(list_valid_fail_reason) == 1:
            str_valid_fail_reason = list_valid_fail_reason[0]
        else:
            str_valid_fail_reason = None

        int_check_qty_sum = df_p_source[f"PO Process Detail_Check Qty({Param_Step})"].sum()
        # 원본 그룹 Dataframe의 첫행만 남김
        df_return = df_p_source.iloc[[0]]
        # ", "로 연결한 값을 각 컬럼에 적재
        df_return = df_return.assign(**{
            f"PO Process Detail_Check Qty({Param_Step})": int_check_qty_sum,
            f"PO Process Detail_Item Unit Load Mix Match({Param_Step})": str_master_match,
            f"PO Process Detail_Item Unit Load Mix Match Chk({Param_Step})": str_master_match_chk,
            f"PO Process Detail_Lane Load Mix Match({Param_Step})": str_method_match,
            f"PO Process Detail_Lane Load Mix Match Chk({Param_Step})": str_method_match_chk,
            f"PO Process Detail_Valid Fail Reason({Param_Step})": str_valid_fail_reason
        })
    else:
        # 행이 1개이므로 원본을 그대로 복사
        df_return = df_p_source.copy(deep=True)

    return df_return


def fn_drop_duplicated_column(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    groupby 후 apply() 적용 시 컬럼 중복 오류가 발생하여 해당 오류를 우회하기 위하여 구현함.
    :param df_p_source: PO Process Detail
    :return: Dataframe
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

    # 중복 컬럼을 마지막 컬럼을 남기고 제거
    df_p_source = df_p_source.drop_duplicates(keep="last")

    return df_p_source

@_decoration_
def fn_output_formatter_po_process(df_p_source: pd.DataFrame, df_p_poprocess: pd.DataFrame) -> pd.DataFrame:
    """
    PO Process Detail의 내용을 PO Process 테이블에 적재한 후 Output 형식에 맞춰 정리
    :param df_p_source: PO Process Detail
    :param df_p_poprocess:
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
        return df_return

    # Aggregation이 필요한 데이터 추출
    list_where_aggr = ((df_p_source["PO Process Detail_Block"] == "DIR_BOTH") |
                       (df_p_source["PO Process Detail_Block"] == "DIR_ONLY") |
                       (df_p_source["PO Process Detail_Block"] == "DIR_PO"))
    # Aggregation이 필요한 데이터
    df_return_aggr = df_p_source[list_where_aggr].copy(deep=True)
    # Aggregation이 필요하지 않은 데이터
    df_return_aggr_n = df_p_source[~list_where_aggr].copy(deep=True)
    # Aggregation 시 사용할 키 묶음
    str_po_group_key = (df_return_aggr["MFG Week.[MFG Week]"].astype(str) + "_" +
                        df_return_aggr["Location.[Location]"] + "_" +
                        df_return_aggr["Sub Location.[Sub Location]"] + "_" +
                        df_return_aggr["Item.[Item]"])
    # Aggregation 시 사용할 컬럼 생성 후 키 배정
    df_return_aggr["PO Group Key"] = str_po_group_key
    fn_log_dataframe(df_return_aggr, "df_return_aggr")
    fn_log_dataframe(df_return_aggr_n, "df_return_aggr_n")
    # Aggragation 수행
    # Mix Match, Mix Match Chk, Valid Fail Reason 컬럼에 대해서는 전체 행의 값을 ", "로 묶음. 그 외 데이터는 첫 행을 취함.
    df_return_aggregated = fn_drop_duplicated_column(df_return_aggr.groupby(by="PO Group Key").apply(fn_aggregation_po))

    # 분리된 데이터 병합
    df_return = pd.concat([df_return_aggregated, df_return_aggr_n], ignore_index=True)
    # 필요 컬럼만 추출
    df_return = df_return[[
        "Version.[Version Name]", "MFG Week.[MFG Week]", "Sub Location.[Sub Location]", "Location.[Location]",
        "Item.[Item]", "Seq.[Seq]", "Time.[Week]", "PO Process Detail_SOP ETD Week",
        f"PO Process Detail_Check Qty({Param_Step})",
        f"PO Process Detail_Item Unit Load Mix Match({Param_Step})",
        f"PO Process Detail_Item Unit Load Mix Match Chk({Param_Step})",
        f"PO Process Detail_Lane Load Mix Match({Param_Step})",
        f"PO Process Detail_Lane Load Mix Match Chk({Param_Step})", f"PO Process Detail_Valid Fail Reason({Param_Step})"
    ]].copy(deep=True)
    # PO Process 명칭으로 변경
    df_return.rename(columns=lambda x: x.replace("PO Process Detail_", "PO Process_"), inplace=True)
    # Input으로 받았던 PO Process 테이블에 Left Join
    df_return = df_p_poprocess.merge(
        df_return, how="left",
        left_on=["MFG Week.[MFG Week]", "Sub Location.[Sub Location]", "Location.[Location]", "Item.[Item]",
                 "Time.[Week]", "SOP Week.[SOP Week]"],
        right_on=["MFG Week.[MFG Week]", "Sub Location.[Sub Location]", "Location.[Location]", "Item.[Item]",
                 "Time.[Week]", "PO Process_SOP ETD Week"],
        indicator=True
    )
    df_return["Version.[Version Name]"] = Param_OUT_VERSION
    fn_log_dataframe(df_return, "df_return_1")
    df_return = df_return.assign(**{
        f"PO Process_Check Qty({Param_Step})":
            np.where(df_return["_merge"] == "both",
                     df_return[f"PO Process_Check Qty({Param_Step})_y"],
                     df_return[f"PO Process_Check Qty({Param_Step})_x"]),
        "PO Process_Item Unit Load Mix Match(FINAL)": df_return[f"PO Process_Item Unit Load Mix Match({Param_Step})"],
        "PO Process_Item Unit Load Mix Match Chk(FINAL)": df_return[f"PO Process_Item Unit Load Mix Match Chk({Param_Step})"],
        f"PO Process_Check Qty(FINAL)":
            np.where(df_return["_merge"] == "both",
                     df_return[f"PO Process_Check Qty({Param_Step})_y"],
                     df_return[f"PO Process_Check Qty({Param_Step})_x"]),
        "PO Process_Lane Load Mix Match(FINAL)": df_return[f"PO Process_Lane Load Mix Match({Param_Step})"],
        "PO Process_Lane Load Mix Match Chk(FINAL)": df_return[f"PO Process_Lane Load Mix Match Chk({Param_Step})"],
        "PO Process_Valid Fail Reason(FINAL)": df_return[f"PO Process_Valid Fail Reason({Param_Step})"]
    })
    # Valid Fail Reason 컬럼에 대해 nan인 경우 None 값 적용
    df_return[f"PO Process_Valid Fail Reason({Param_Step})"] = (
        df_return[f"PO Process_Valid Fail Reason({Param_Step})"].
        where(df_return[f"PO Process_Valid Fail Reason({Param_Step})"].notnull(), None))

    df_return = df_return[[
        "Version.[Version Name]", "MFG Week.[MFG Week]", "Sub Location.[Sub Location]", "Location.[Location]",
        "Item.[Item]", "Time.[Week]", "SOP Week.[SOP Week]", "Delivery Week.[Delivery Week]",
        f"PO Process_Check Qty({Param_Step})",
        f"PO Process_Item Unit Load Mix Match({Param_Step})",
        f"PO Process_Item Unit Load Mix Match Chk({Param_Step})", f"PO Process_Lane Load Mix Match({Param_Step})",
        f"PO Process_Lane Load Mix Match Chk({Param_Step})", f"PO Process_Valid Fail Reason({Param_Step})",
        f"PO Process_Check Qty(FINAL)", f"PO Process_Item Unit Load Mix Match(FINAL)",
        f"PO Process_Item Unit Load Mix Match Chk(FINAL)", f"PO Process_Lane Load Mix Match(FINAL)",
        f"PO Process_Lane Load Mix Match Chk(FINAL)", f"PO Process_Valid Fail Reason(FINAL)"
    ]]

    return df_return


@_decoration_
def fn_output_formatter_loading_po_cal_master(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    df_return = df_p_source[[
        "Version.[Version Name]", "MFG Week.[MFG Week]", "Sub Location.[Sub Location]", "Seq.[Seq]", "Item.[Item]",
        "Location.[Location]", "Time.[Week]", "Loading Type.[Loading Type]", "Container.[ContainerID]",
        "PO Process Detail_JIG", "PO Process Detail_Line", "PO Process Detail_JIG Line",
        "PO Process Detail_Max Load Qty", "PO Process Detail_LDM Qty", "PO Process Detail_Multiple",
        "PO Process Detail_Min Qty", "PO Process Detail_Height", "PO Process Detail_Width",
        "PO Process Detail_Depth", "PO Process Detail_1st Mix", "PO Process Detail_2nd Mix",
        "PO Process Detail_3rd Mix", "PO Process Detail_Single FR Type", "PO Process Detail_Single Min FR",
        "PO Process Detail_Single Max FR", "PO Process Detail_Single Cut Add", "PO Process Detail_Mix FR Type",
        "PO Process Detail_Mix Min FR", "PO Process Detail_Mix Max FR", "PO Process Detail_Mix Cut Add",
        "PO Process Detail_SKU Per Cntr", "PO Process Detail_Item Mix Group", "PO Process Detail_Profit Grade",
        "PO Process Detail_Profit Grade Priority"
    ]].copy(deep=True)

    # Jig Line 컬럼값 정리
    df_return["PO Process Detail_JIG Line"] = (
        df_return["PO Process Detail_JIG Line"].replace(r'^\s*$', np.nan, regex=True).fillna(False).astype(bool))
    # Jig 컬럼값 정리
    df_return["PO Process Detail_JIG"] = (
        df_return["PO Process Detail_JIG"].replace(r'^\s*$', np.nan, regex=True).fillna("").astype(str))
    # Line 컬럼값 정리
    df_return["PO Process Detail_Line"] = (
        df_return["PO Process Detail_Line"].replace(r'^\s*$', np.nan, regex=True).fillna("").astype(str))

    df_return.rename(columns={
        "Loading Type.[Loading Type]": "Loading PO Cal Master_Loading Type",
        "Container.[ContainerID]": "Loading PO Cal Master_Cntr Type",
        "PO Process Detail_Height": "PO Process Detail_Item Height",
        "PO Process Detail_Width": "PO Process Detail_Item Width",
        "PO Process Detail_Depth": "PO Process Detail_Item Depth"
    }, inplace=True)
    df_return.rename(columns=lambda x: x.replace("PO Process Detail_", "Loading PO Cal Master_"), inplace=True)

    return df_return


@_decoration_
def fn_output_formatter_loading_master_from_site(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    df_return = df_p_source[["Version.[Version Name]", "D.FromSite", "D.Item", "D.LoadingType", "D.CntrType", "M.CBM",
                             "M.Height", "M.Width", "M.Depth"]].copy(deep=True)
    df_return = df_return.rename(columns={
        "D.FromSite": "Sub Location.[Sub Location]",
        "D.Item": "Item.[Item]",
        "D.LoadingType": "Loading Type.[Loading Type]",
        "D.CntrType": "Container.[ContainerID]",
        "M.CBM": "Loading Master From Site_CBM",
        "M.Height": "Loading Master From Site_Height",
        "M.Width": "Loading Master From Site_Width",
        "M.Depth": "Loading Master From Site_Depth"
    })
    df_return = df_return.assign(**{
        "Loading Master From Site_CIS Info Update": "Y",
        "Loading Master From Site_Valid Flag": "N",
        "Loading Master From Site_Created By": "System",
        "Loading Master From Site_Creation Time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    return df_return


@_decoration_
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :param str_p_cond:
    :return: DataFrame
    """
    df_return = pd.DataFrame()
    if str_p_cond == "0":
        # out_POProcess
        df_return = pd.DataFrame(columns=[{
            "Version.[Version Name]": [], "MFG Week.[MFG Week]": [], "Sub Location.[Sub Location]": [],
            "Location.[Location]": [], "Item.[Item]": [], "Time.[Week]": [], "SOP Week.[SOP Week]": [],
            "Delivery Week.[Delivery Week]": [], f"PO Process_Item Unit Load Mix Match({Param_Step})": [],
            f"PO Process_Item Unit Load Mix Match Chk({Param_Step})": [],
            f"PO Process_Lane Load Mix Match({Param_Step})": [],
            f"PO Process_Lane Load Mix Match Chk({Param_Step})": [], f"PO Process_Valid Fail Reason({Param_Step})": []
        }])
    elif str_p_cond == "1":
        # out_POProcessDetail
        df_return = pd.DataFrame(
            {
                "Version.[Version Name]": [], "MFG Week.[MFG Week]": [], "Sub Location.[Sub Location]": [],
                "Location.[Location]": [], "Item.[Item]": [], "Seq.[Seq]": [], "Time.[Week]": [],
                "SOP Week.[SOP Week]": [], "PO Process Detail_Chk Grain": [],
                f"PO Process Detail_Item Unit Load Mix Match({Param_Step})": [],
                f"PO Process Detail_Item Unit Load Mix Match Chk({Param_Step})": [],
                f"PO Process Detail_Lane Load Mix Match({Param_Step})": [],
                f"PO Process Detail_Lane Load Mix Match Chk({Param_Step})": [],
                f"PO Process Detail_Valid Fail Reason({Param_Step})": []
            }
        )
    elif str_p_cond == "2":
        # out_LoadingPOCalMaster
        df_return = pd.DataFrame(
            {
                "Version.[Version Name]": [], "Time.[Week]": [], "Sub Location.[Sub Location]": [],
                "Location.[Location]": [], "Item.[Item]": [], "Seq.[Seq]": [], "Loading PO Cal Master_Block": [],
                "Loading PO Cal Master_JIG": [], "Loading PO Cal Master_JIG Line": [], "Loading PO Cal Master_Line": [],
                "Loading PO Cal Master_Profit Grade": [], "Loading PO Cal Master_Profit Grade Priority": [],
                "Loading PO Cal Master_Loading Type": [], "Loading PO Cal Master_Cntr Type": [],
                "Loading PO Cal Master_Max Load Qty": [], "Loading PO Cal Master_LDM Qty": [],
                "Loading PO Cal Master_Multiple": [], "Loading PO Cal Master_Min Qty": [],
                "Loading PO Cal Master_Single FR Type": [], "Loading PO Cal Master_Single Min FR": [],
                "Loading PO Cal Master_Single Max FR": [], "Loading PO Cal Master_Single Min FTL": [],
                "Loading PO Cal Master_Single Max FTL": [], "Loading PO Cal Master_Single Cut Add": [],
                "Loading PO Cal Master_Mix FR Type": [], "Loading PO Cal Master_Mix Min FR": [],
                "Loading PO Cal Master_Mix Max FR": [], "Loading PO Cal Master_Mix Min FTL": [],
                "Loading PO Cal Master_Mix Max FTL": [], "Loading PO Cal Master_Mix Cut Add": [],
                "Loading PO Cal Master_1st Mix": [], "Loading PO Cal Master_2nd Mix": [],
                "Loading PO Cal Master_3rd Mix": [], "Loading PO Cal Master_Item Mix Group": [],
                "Loading PO Cal Master_Item Height": [], "Loading PO Cal Master_Item Width": [],
                "Loading PO Cal Master_Item Depth": [], "Loading PO Cal Master_SKU Per Cntr": []
            }
        )
    elif str_p_cond == "3":
        # out_LoadingMasterFromSiteNew
        df_return = pd.DataFrame(
            {
                "Version.[Version Name]": [], "Sub Location.[Sub Location]": [], "Item.[Item]": [],
                "Loading Type.[Loading Type]": [], "Container.[ContainerID]": [], "Loading Master From Site_CBM": [],
                "Loading Master From Site_Height": [], "Loading Master From Site_Width": [],
                "Loading Master From Site_Depth": [], "Loading Master From Site_Valid Flag": [],
                "Loading Master From Site_Created By": [], "Loading Master From Site_Creation Time": []
            }
        )

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_POProcess = pd.DataFrame()
    out_POProcessDetail = pd.DataFrame()
    out_LoadingPOCalMaster = pd.DataFrame()
    out_LoadingMasterFromSiteNew = pd.DataFrame()
    try:
        ################################################################################################################
        # 모듈 실행 준비 - 로컬 파일 정리, Parameter 확인, 입력 데이터 확인
        ################################################################################################################
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            Param_OUT_VERSION = "CWV_MP"
            Param_Exception_Flag = "N"
            Param_Step = "P" # Step : P, M, ADJ1, ADJ2, ADJ3, FINAL
            Param_Check_Qty = "Current"  # Current-Check Qty(Step), POPOnly-POP(Step), POPShort-POP(Step) + Short(Step)

            in_POProcess = pd.read_csv(str_input_dir + "/in_POProcess.csv", encoding="UTF8")
            in_POProcessDetail = pd.read_csv(str_input_dir + "/in_POProcessDetail.csv", encoding="UTF8")
            in_LoadingMasterFromSite = pd.read_csv(str_input_dir + "/in_LoadingMasterFromSite.csv", encoding="UTF8")
            in_LoadingMasterToSite = pd.read_csv(str_input_dir + "/in_LoadingMasterToSite.csv", encoding="UTF8")
            in_LoadingMasterAccount = pd.read_csv(str_input_dir + "/in_LoadingMasterAccount.csv", encoding="UTF8")
            in_LoadingMasterShipTo = pd.read_csv(str_input_dir + "/in_LoadingMasterShipTo.csv", encoding="UTF8")
            in_LoadingMethodFromSite = pd.read_csv(str_input_dir + "/in_LoadingMethodFromSite.csv", encoding="UTF8")
            in_LoadingMethodToSite = pd.read_csv(str_input_dir + "/in_LoadingMethodToSite.csv", encoding="UTF8")
            in_LoadingMethodAccount = pd.read_csv(str_input_dir + "/in_LoadingMethodAccount.csv", encoding="UTF8")
            in_LoadingMethodShipTo = pd.read_csv(str_input_dir + "/in_LoadingMethodShipTo.csv", encoding="UTF8")
            in_LoadingMethodMixToSite = pd.read_csv(str_input_dir + "/in_LoadingMethodMixToSite.csv", encoding="UTF8")
            in_LoadingMethodMixShipTo = pd.read_csv(str_input_dir + "/in_LoadingMethodMixShipTo.csv", encoding="UTF8")
            in_LoadingProfitGrade = pd.read_csv(str_input_dir + "/in_LoadingProfitGrade.csv", encoding="UTF8")
            in_ItemULD = pd.read_csv(str_input_dir + "/in_ItemULD.csv", encoding="UTF8")
            # in_LoadingCntrMaster = pd.read_csv(str_input_dir + "/in_LoadingCntrMaster.csv", encoding="UTF8")

        # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'

        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        # 입력 변수 확인
        if Param_Step is None or Param_Step.strip() == '':
            logger.Note(p_note=f'[Exception] Param_Step is None.', p_log_level=LOG_LEVEL.error())
            raise Exception(f'[Exception] Param_Step is None.')

        # 입력 변수 확인
        if Param_Check_Qty is None or Param_Check_Qty.strip() == '':
            Param_Check_Qty = 'Current'

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Step : {Param_Step}', p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f'Param_Check_Qty : {Param_Check_Qty}', p_log_level=LOG_LEVEL.debug())

        # 입력 테이블 점검 및 로그
        fn_check_input_table(in_POProcess, "in_POProcess", "1")
        fn_check_input_table(in_POProcessDetail, "in_POProcessDetail", "0")
        fn_check_input_table(in_LoadingMasterFromSite, "in_LoadingMasterFromSite", "1")
        fn_check_input_table(in_LoadingMasterToSite, "in_LoadingMasterToSite", "1")
        fn_check_input_table(in_LoadingMasterAccount, "in_LoadingMasterAccount", "1")
        fn_check_input_table(in_LoadingMasterShipTo, "in_LoadingMasterShipTo", "1")
        fn_check_input_table(in_LoadingMethodFromSite, "in_LoadingMethodFromSite", "1")
        fn_check_input_table(in_LoadingMethodToSite, "in_LoadingMethodToSite", "1")
        fn_check_input_table(in_LoadingMethodAccount, "in_LoadingMethodAccount", "1")
        fn_check_input_table(in_LoadingMethodShipTo, "in_LoadingMethodShipTo", "1")
        fn_check_input_table(in_LoadingMethodMixToSite, "in_LoadingMethodMixToSite", "1")
        fn_check_input_table(in_LoadingMethodMixShipTo, "in_LoadingMethodMixShipTo", "1")
        fn_check_input_table(in_LoadingProfitGrade, "in_LoadingProfitGrade", "1")
        fn_check_input_table(in_ItemULD, "in_ItemULD", "1")
        # fn_check_input_table(in_LoadingCntrMaster, "in_LoadingCntrMaster", "1")

        # Validation 관련 상수
        STR_NOT_DEFINED = "Not Defined"
        STR_MIN_QTY_ERR1 = "The value of Check Qty is Less than the minimum qty for Simulation."
        # STR_MIN_QTY_ERR1 = "Chk Qty Err"
        STR_MIN_QTY_ERR2 = "No Min Qty"
        STR_MULTIPLE_ERR1 = "No Multiple"
        STR_MLQTY_ERR1 = "No Max Load Qty"
        STR_LDMQTY_ERR1 = "No LDM Qty"
        STR_MIX_GRP_ERR = "No Item Mix Group"

        ################################################################################################################
        # Preprocess: 전처리
        ################################################################################################################
        list_measure_groups = ["Loading Master Ship To", "Loading Master Account",
                               "Loading Master To Site", "Loading Master From Site",
                               "Loading Method Ship To", "Loading Method Account",
                               "Loading Method To Site", "Loading Method From Site",
                               "Loading Method Mix Ship To", "Loading Method Mix To Site",
                               "Loading Profit Grade", "Item ULD", "Loading Cntr Master",
                               "PO Process", "PO Process Detail",]

        dict_log = {
            "p_step_no": 0,
            "p_step_desc": "STEP 0-0. 전처리(in_LoadingMasterShipTo): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMasterShipTo"
        }
        df_in_LoadingMasterShipTo = fn_preprocess(in_LoadingMasterShipTo, list_measure_groups, 0, **dict_log)

        dict_log = {
            "p_step_no": 1,
            "p_step_desc": "STEP 0-1. 전처리(in_LoadingMasterAccount): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMasterAccount"
        }
        df_in_LoadingMasterAccount = fn_preprocess(in_LoadingMasterAccount, list_measure_groups, 1, **dict_log)

        dict_log = {
            "p_step_no": 2,
            "p_step_desc": "STEP 0-2. 전처리(in_LoadingMasterToSite): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMasterToSite"
        }
        df_in_LoadingMasterToSite = fn_preprocess(in_LoadingMasterToSite, list_measure_groups, 2, **dict_log)

        dict_log = {
            "p_step_no": 3,
            "p_step_desc": "STEP 0-3. 전처리(in_LoadingMasterFromSite): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMasterFromSite"
        }
        df_in_LoadingMasterFromSite = fn_preprocess(in_LoadingMasterFromSite, list_measure_groups, 3, **dict_log)

        dict_log = {
            "p_step_no": 4,
            "p_step_desc": "STEP 0-4. 전처리(in_LoadingMethodShipTo): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMethodShipTo"
        }
        df_in_LoadingMethodShipTo = fn_preprocess(in_LoadingMethodShipTo, list_measure_groups, 4, **dict_log)

        dict_log = {
            "p_step_no": 5,
            "p_step_desc": "STEP 0-5. 전처리(in_LoadingMethodAccount): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMethodAccount"
        }
        df_in_LoadingMethodAccount = fn_preprocess(in_LoadingMethodAccount, list_measure_groups, 5, **dict_log)

        dict_log = {
            "p_step_no": 6,
            "p_step_desc": "STEP 0-6. 전처리(in_LoadingMethodToSite): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMethodToSite"
        }
        df_in_LoadingMethodToSite = fn_preprocess(in_LoadingMethodToSite, list_measure_groups, 6, **dict_log)

        dict_log = {
            "p_step_no": 7,
            "p_step_desc": "STEP 0-7. 전처리(in_LoadingMethodFromSite): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMethodFromSite"
        }
        df_in_LoadingMethodFromSite = fn_preprocess(in_LoadingMethodFromSite, list_measure_groups, 7, **dict_log)

        dict_log = {
            "p_step_no": 8,
            "p_step_desc": "STEP 0-8. 전처리(in_LoadingMethodMixShipTo): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMethodMixShipTo"
        }
        df_in_LoadingMethodMixShipTo = fn_preprocess(in_LoadingMethodMixShipTo, list_measure_groups, 8, **dict_log)

        dict_log = {
            "p_step_no": 9,
            "p_step_desc": "STEP 0-9. 전처리(in_LoadingMethodMixToSite): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingMethodMixToSite"
        }
        df_in_LoadingMethodMixToSite = fn_preprocess(in_LoadingMethodMixToSite, list_measure_groups, 9, **dict_log)

        dict_log = {
            "p_step_no": 10,
            "p_step_desc": "STEP 0-10. 전처리(in_LoadingProfitGrade): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_LoadingProfitGrade"
        }
        df_in_LoadingProfitGrade = fn_preprocess(in_LoadingProfitGrade, list_measure_groups, 10, **dict_log)

        dict_log = {
            "p_step_no": 11,
            "p_step_desc": "STEP 0-11. 전처리(in_ItemULD): 로직 전개에 편리하도록 컬럼명을 통일하고, "
                           "데이터 유형을 조정함.",
            "p_df_name": "df_in_ItemULD"
        }
        df_in_ItemULD = fn_preprocess(in_ItemULD, list_measure_groups, 11, **dict_log)

        # LDM의 경우 사용하던 container 정보를 사용하지 않게 되어 주석 처리함.
        # dict_log = {
        #     "p_step_no": 12,
        #     "p_step_desc": "STEP 0-12. 전처리(in_LoadingCntrMaster): 로직 전개에 편리하도록 컬럼명을 통일하고, "
        #                    "데이터 유형을 조정함.",
        #     "p_df_name": "df_in_LoadingCntrMaster"
        # }
        # df_in_LoadingCntrMaster = fn_preprocess(in_LoadingCntrMaster, list_measure_groups, 12, **dict_log)

        dict_log = {
            "p_step_no": 13,
            "p_step_desc": "STEP 0-13. 전처리(in_POProcess): 로직 전개에 편리하도록 컬럼명을 통일하고, 데이터 유형을 조정함.",
            "p_df_name": "df_in_POProcess"
        }
        df_in_POProcess = fn_preprocess(in_POProcess, list_measure_groups, 13, **dict_log)

        dict_log = {
            "p_step_no": 14,
            "p_step_desc": "STEP 0-14. 전처리(in_POProcessDetail): Validation 수행 범위를 지정하고, "
                           "로직 전개에 편리하도록 컬럼명을 통일한 후 데이터 유형을 조정함.",
            "p_df_name": "df_in_POProcessDetail"
        }
        df_in_POProcessDetail = fn_preprocess(in_POProcessDetail, list_measure_groups, 14, **dict_log)

        dict_log = {
            "p_step_no": 15,
            "p_step_desc": "STEP 0-15. Loading Method(Ship To)의 Default값을 읽어 Loading Type, Cntr Type을 채운다.",
            "p_df_name": "df_in_POProcessDetailCal1"
        }
        df_in_POProcessDetailCal1 = fn_set_method_default(df_in_POProcessDetail, df_in_LoadingMethodShipTo,
                                                          list_measure_groups, 4, **dict_log)

        dict_log = {
            "p_step_no": 16,
            "p_step_desc": "STEP 0-16. Loading Method(Account)의 Default값을 읽어 Loading Type, Cntr Type을 채운다.",
            "p_df_name": "df_in_POProcessDetailCal2"
        }
        df_in_POProcessDetailCal2 = fn_set_method_default(df_in_POProcessDetailCal1, df_in_LoadingMethodAccount,
                                                          list_measure_groups, 5, **dict_log)

        dict_log = {
            "p_step_no": 17,
            "p_step_desc": "STEP 0-17. Loading Method(To Site)의 Default값을 읽어 Loading Type, Cntr Type을 채운다.",
            "p_df_name": "df_in_POProcessDetailCal3"
        }
        df_in_POProcessDetailCal3 = fn_set_method_default(df_in_POProcessDetailCal2, df_in_LoadingMethodToSite,
                                                          list_measure_groups, 6, **dict_log)

        dict_log = {
            "p_step_no": 18,
            "p_step_desc": "STEP 0-18. Loading Method(From Site)의 Default값을 읽어 Loading Type, Cntr Type을 채운다.",
            "p_df_name": "df_in_POProcessDetailCal4"
        }
        df_in_POProcessDetailCal4 = fn_set_method_default(df_in_POProcessDetailCal3, df_in_LoadingMethodFromSite,
                                                          list_measure_groups, 7, **dict_log)

        dict_log = {
            "p_step_no": 19,
            "p_step_desc": "STEP 0-19. PO Process 컬럼 정리",
            "p_df_name": "df_in_POProcessDetailCal"
        }
        df_in_POProcessDetailCal = fn_arrange_po_process_column(df_in_POProcessDetailCal4, df_in_POProcess, **dict_log)

        ################################################################################################################
        # Step 1. Loading Master에서 값을 가져와 PO Process에 채운다.
        ################################################################################################################
        dict_log = {
            "p_step_no": 1010,
            "p_step_desc": "STEP 1-1. Loading Master(Ship To)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMaster1"
        }
        df_POProcessDetailMaster1 = (
            fn_merge_master_n_method(df_in_POProcessDetailCal, df_in_LoadingMasterShipTo,
                                     list_measure_groups, 0, **dict_log))

        dict_log = {
            "p_step_no": 1020,
            "p_step_desc": "STEP 1-2. Loading Master(Account)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMaster2"
        }
        df_POProcessDetailMaster2 = (
            fn_merge_master_n_method(df_POProcessDetailMaster1, df_in_LoadingMasterAccount,
                                     list_measure_groups, 1, **dict_log))

        dict_log = {
            "p_step_no": 1030,
            "p_step_desc": "STEP 1-3. Loading Master(To Site)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMaster3"
        }
        df_POProcessDetailMaster3 = (
            fn_merge_master_n_method(df_POProcessDetailMaster2, df_in_LoadingMasterToSite,
                                     list_measure_groups, 2, **dict_log))

        # Loading Master From Site의 경우 미등록 데이터에 대한 자동 생성 시 Valid Flag가 "N"인 데이터에 대한 검색을 위해
        # Valid Flag가 "N"인 것도 포함하여 Input으로 가져오기 때문에 조회 전에 Valid Flag가 "Y"인 것만으로 필터링한다.
        list_where_valid = df_in_LoadingMasterFromSite["M.Valid_Flag"] == "Y"
        df_in_LoadingMasterFromSiteValid = df_in_LoadingMasterFromSite[list_where_valid].copy(deep=True)
        df_in_LoadingMasterFromSiteNotValid = df_in_LoadingMasterFromSite[~list_where_valid].copy(deep=True)

        dict_log = {
            "p_step_no": 1040,
            "p_step_desc": "STEP 1-4. Loading Master(From Site)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMaster4"
        }
        df_POProcessDetailMaster4 = (
            fn_merge_master_n_method(df_POProcessDetailMaster3, df_in_LoadingMasterFromSiteValid,
                                     list_measure_groups, 3, **dict_log))

        ################################################################################################################
        # Step 2. Loading Method에서 값을 가져와 PO Process에 채운다.
        ################################################################################################################
        dict_log = {
            "p_step_no": 2010,
            "p_step_desc": "STEP 2-1. Loading Method(Ship To)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMethod1"
        }
        df_POProcessDetailMethod1 = (
            fn_merge_master_n_method(df_POProcessDetailMaster4, df_in_LoadingMethodShipTo,
                                     list_measure_groups, 4, **dict_log))

        dict_log = {
            "p_step_no": 2020,
            "p_step_desc": "STEP 2-2. Loading Method(Account)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMethod2"
        }
        df_POProcessDetailMethod2 = (
            fn_merge_master_n_method(df_POProcessDetailMethod1, df_in_LoadingMethodAccount,
                                     list_measure_groups, 5, **dict_log))

        dict_log = {
            "p_step_no": 2030,
            "p_step_desc": "STEP 2-3. Loading Method(To Site)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMethod3"
        }
        df_POProcessDetailMethod3 = (
            fn_merge_master_n_method(df_POProcessDetailMethod2, df_in_LoadingMethodToSite,
                                     list_measure_groups, 6, **dict_log))

        dict_log = {
            "p_step_no": 2040,
            "p_step_desc": "STEP 2-4. Loading Method(From Site)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMethod4"
        }
        df_POProcessDetailMethod4 = (
            fn_merge_master_n_method(df_POProcessDetailMethod3, df_in_LoadingMethodFromSite,
                                     list_measure_groups, 7, **dict_log))

        ################################################################################################################
        # Step 3. Loading Method Mix에서 값을 가져와 PO Process에 채운다.
        ################################################################################################################
        dict_log = {
            "p_step_no": 3010,
            "p_step_desc": "STEP 3-1. Loading Method Mix(Ship To)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMethodMix1"
        }
        df_POProcessDetailMethodMix1 = (
            fn_merge_method_mix(df_POProcessDetailMethod4, df_in_LoadingMethodMixShipTo,
                                list_measure_groups, 8, **dict_log))

        dict_log = {
            "p_step_no": 3010,
            "p_step_desc": "STEP 3-1. Loading Method Mix(To Site)에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailMethodMix2"
        }
        df_POProcessDetailMethodMix2 = (
            fn_merge_method_mix(df_POProcessDetailMethodMix1, df_in_LoadingMethodMixToSite,
                                list_measure_groups, 9, **dict_log))

        ################################################################################################################
        # Step 4. Loading Profit Grade에서 값을 가져와 PO Process에 채운다.
        ################################################################################################################
        dict_log = {
            "p_step_no": 4000,
            "p_step_desc": "Step 4. Loading Profit Grade에서 값을 가져와 PO Process에 채운다.",
            "p_df_name": "df_POProcessDetailProfitGrade"
        }
        df_POProcessDetailProfitGrade = (
            fn_merge_profit_grade(df_POProcessDetailMethodMix2, df_in_LoadingProfitGrade, **dict_log))

        ################################################################################################################
        # Step 5. Validation 처리 및 관련 값 업데이트
        ################################################################################################################
        dict_log = {
            "p_step_no": 5000,
            "p_step_desc": "STEP 5. Master/Method 조회 종료 후 추가 Validation 처리 및 관련 값 업데이트",
            "p_df_name": "df_POProcessDetailValid"
        }
        df_POProcessDetailValid = fn_validate_master_n_method(df_POProcessDetailProfitGrade, **dict_log)

        ################################################################################################################
        # Step 6. Loading Master Match가 "Not Defined"인 경우에 Item Unit Load를 자동으로 생성한다.
        ################################################################################################################
        dict_log = {
            "p_step_no": 6000,
            "p_step_desc": "STEP 6. Loading Master Match가 'Not Defined'인 경우에 Item Unit Load를 자동으로 생성한다.",
            "p_df_name": "df_out_LoadingMasterFromSite"
        }
        df_out_LoadingMasterFromSite = (
            fn_create_loading_master_from_site(df_POProcessDetailValid, df_in_LoadingMasterFromSiteNotValid,
                                               df_in_ItemULD, **dict_log))

        ################################################################################################################
        # Output 정리
        ################################################################################################################
        dict_log = {
            "p_step_no": 9010,
            "p_step_desc": "STEP 9-1. Postprocess - rename했던 컬럼들을 원본명으로 다시 변경한다.",
            "p_df_name": "df_out_POProcessDetail"
        }
        df_out_POProcessDetail = fn_postprocess(df_POProcessDetailValid, **dict_log)

        dict_log = {
            "p_step_no": 9020,
            "p_step_desc": "STEP 9-2. 로직을 통해 생성된 내용을 Output 형식에 맞게 조정한다(out_POProcessDetail).",
            "p_df_name": "out_POProcessDetail"
        }
        out_POProcessDetail = fn_output_formatter_po_process_detail(df_out_POProcessDetail, **dict_log)

        dict_log = {
            "p_step_no": 9030,
            "p_step_desc": "STEP 9-3. 로직을 통해 생성된 내용을 Output 형식에 맞게 조정한다(out_POProcess).",
            "p_df_name": "out_POProcess"
        }
        out_POProcess = fn_output_formatter_po_process(df_out_POProcessDetail, in_POProcess, **dict_log)

        dict_log = {
            "p_step_no": 9030,
            "p_step_desc": "STEP 9-3. 로직을 통해 생성된 내용을 Output 형식에 맞게 조정한다(out_LoadingPOCalMaster).",
            "p_df_name": "out_LoadingPOCalMaster"
        }
        out_LoadingPOCalMaster = fn_output_formatter_loading_po_cal_master(df_out_POProcessDetail, **dict_log)

        dict_log = {
            "p_step_no": 9040,
            "p_step_desc": "STEP 9-4. 로직을 통해 생성된 내용을 Output 형식에 맞게 조정한다(out_LoadingMasterFromSiteNew).",
            "p_df_name": "out_LoadingMasterFromSiteNew"
        }
        out_LoadingMasterFromSiteNew = (
            fn_output_formatter_loading_master_from_site(df_out_LoadingMasterFromSite, **dict_log))

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_POProcess = None
            out_POProcessDetail = None
            out_LoadingPOCalMaster = None
            out_LoadingMasterFromSiteNew = None
            raise Exception(e)
        else:
            # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
            # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들어 줌.
            if out_POProcess.empty:
                out_POProcess = fn_set_header("1")
                fn_log_dataframe(out_POProcess, 'out_POProcess')
            if out_POProcessDetail.empty:
                out_POProcessDetail = fn_set_header("1")
                fn_log_dataframe(out_POProcessDetail, 'out_POProcessDetail')
            if out_LoadingPOCalMaster.empty:
                out_LoadingPOCalMaster = fn_set_header("2")
                fn_log_dataframe(out_LoadingPOCalMaster, 'out_LoadingPOCalMaster')
            if out_LoadingMasterFromSiteNew.empty:
                out_LoadingMasterFromSiteNew = fn_set_header("3")
                fn_log_dataframe(out_LoadingMasterFromSiteNew, 'out_LoadingMasterFromSiteNew')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
        # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들어 줌.
        if out_POProcess.empty:
            out_POProcess = fn_set_header("1")
            fn_log_dataframe(out_POProcess, 'out_POProcess')
        if out_POProcessDetail.empty:
            out_POProcessDetail = fn_set_header("1")
            fn_log_dataframe(out_POProcessDetail, 'out_POProcessDetail')
        if out_LoadingPOCalMaster.empty:
            out_LoadingPOCalMaster = fn_set_header("2")
            fn_log_dataframe(out_LoadingPOCalMaster, 'out_LoadingPOCalMaster')
        if out_LoadingMasterFromSiteNew.empty:
            out_LoadingMasterFromSiteNew = fn_set_header("3")
            fn_log_dataframe(out_LoadingMasterFromSiteNew, 'out_LoadingMasterFromSiteNew')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')
