"""
* 프로그램명
    - PY_UI_POProcessNoneSKU_REG

* 내용
    - Validation 된 PO 데이터에 대해 주어진 로직(휴리스틱)에 따라 컨테이너 배정 시뮬레이션 작업을 수행한다.

* 변경이력
    - 2025.11.19 / Miss Lee, Kang Gyeonghun / Create
    - 2025.12.16 / Miss Lee / Update
      : 창고향 Adjust Max Profit 로직 추가
    - 2026.01.02 / Kang Gyeonghun / Update
      : Cntr No 생성 로직 오류 수정
    - 2026.01.08 / Kang Gyeonghun / Update
      : Adj Min Qty 계산 로직 수정
    - 2026.01.09 / Kang Gyeonghun / Update
      : Split 시 Adj Item FR 재계산 로직 추가
    - 2026.01.13 / Miss Lee / Update
      : Adjust 예외로직 추가
        Mix Container Planning FTL 판별 여부 추가
    - 2026.01.16 / Kang Gyeonghun / Update
      : Cntr Planning FTL/LTL 판단 로직 오류 수정
    - 2026.01.16 / Miss Lee / Update
      : 창고향 Adjust Min Item Change 로직 추가
    - 2026.01.19 / Miss Lee / Update
      : Adjust LTL 로직 추가 (Adjust 후 LTL로 나온 건들에 대한 Adjust 처리)
    - 2026.01.21 / Miss Lee / Update
      : Adjust 예외로직 ( Last Mix Group 이 모두 Null 일 경우 key에러, transform 구문 에러 발생 ) 오류 수정
    - 2026.01.22 / Kang Gyeonghun / Update
      : 혼적 시 Split 되었으나 Split 후 Split된 2개의 행이 모두 LTL된 경우에 대해 원복하는 로직 추가
    - 2026.01.26 / Miss Lee / Update
      : 창고향 Adjust Option1 추가

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.
    - Param_Exception_Flag : S/N, 파이썬 모듈 실행 시 발생하는 Exception들을 무시하고 정상 종료할 것인지를 결정하는 파라미터
    - Param_Adjust_Option1 : MIN/MAX, 합계 F/R 결정 시 Min F/R에 가깝게 할 것인지, Max F/R에 가깝게 할 것인지를 지정하는 파라미터
    - Param_Adjust_Option2 : Min Item Change/Max Profit, Adjust 시 조정 대상 아이템을 결정하는 파라미터
    - Param_User_Name : 파이썬 모듈 실행자
    - Param_Step : 시뮬레이션 대상 단계, P, M, ADJ1, ADJ2, ADJ3, FINAL
    - Param_Check_Qty : Current # Current - Check Qty(Step), POPOnly - POP(Step), POPShort - POP(Step) + Short(Step)

* Input Tables
    - in_POProcess
        Select ([MFG Week].[MFG Week] * [Location].[Location] * &NSFromSiteMF * [Item].[Item]
             * [Time].[Week] * [SOP Week].[SOP Week] * [Delivery Week].[Delivery Week]) on row
             , ({Measure.[PO Process_Data Source], Measure.[PO Process_Created By]}) on column
         where {[Version].[Version Name]}
        ;

    - in_POProcessDetail
        Select ([MFG Week].[MFG Week] * [Location].[Location] * [Sub Location].[Sub Location] * [Item].[Item]
             * [Item].[Product Group] * [Item].[Product] * [Item].[Project] * [Seq].[Seq]) on row
             , ({Measure.[PO Process Detail_Block], Measure.[PO Process Detail_Account]
             , Measure.[PO Process Detail_Ship To], Measure.[PO Process Detail_SOP ETD Week]
             , Measure.[PO Process Detail_POP Qty(P)], Measure.[PO Process Detail_Short Qty(P)]
             , Measure.[PO Process Detail_Chk Last Step(P)], Measure.[PO Process Detail_Check Qty(P)]
             , Measure.[PO Process Detail_Max Qty(P)], Measure.[PO Process Detail_Loading Status(P)]
             , Measure.[PO Process Detail_Loading Qty(P)], Measure.[PO Process Detail_Diff Qty(P)]
             , Measure.[PO Process Detail_Item FR(P)], Measure.[PO Process Detail_CNTR FR(P)]
             , Measure.[PO Process Detail_POP Qty(M)], Measure.[PO Process Detail_Short Qty(M)]
             , Measure.[PO Process Detail_Check Qty(M)], Measure.[PO Process Detail_Max Qty(M)]
             , Measure.[PO Process Detail_Loading Status(M)], Measure.[PO Process Detail_Loading Qty(M)]
             , Measure.[PO Process Detail_Diff Qty(M)], Measure.[PO Process Detail_Item FR(M)]
             , Measure.[PO Process Detail_CNTR FR(M)], Measure.[PO Process Detail_Check Qty(ADJ1)]
             , Measure.[PO Process Detail_Max Qty(ADJ1)], Measure.[PO Process Detail_Loading Status(ADJ1)]
             , Measure.[PO Process Detail_Loading Qty(ADJ1)], Measure.[PO Process Detail_Diff Qty(ADJ1)]
             , Measure.[PO Process Detail_Item FR(ADJ1)], Measure.[PO Process Detail_CNTR FR(ADJ1)]
             , Measure.[PO Process Detail_Check Qty(ADJ2)], Measure.[PO Process Detail_Max Qty(ADJ2)]
             , Measure.[PO Process Detail_Loading Status(ADJ2)], Measure.[PO Process Detail_Loading Qty(ADJ2)]
             , Measure.[PO Process Detail_Diff Qty(ADJ2)], Measure.[PO Process Detail_Item FR(ADJ2)]
             , Measure.[PO Process Detail_CNTR FR(ADJ2)], Measure.[PO Process Detail_Check Qty(ADJ3)]
             , Measure.[PO Process Detail_Max Qty(ADJ3)], Measure.[PO Process Detail_Loading Status(ADJ3)]
             , Measure.[PO Process Detail_Loading Qty(ADJ3)], Measure.[PO Process Detail_Diff Qty(ADJ3)]
             , Measure.[PO Process Detail_Item FR(ADJ3)], Measure.[PO Process Detail_CNTR FR(ADJ3)]
             , Measure.[PO Process Detail_Check Qty(FINAL)], Measure.[PO Process Detail_Max Qty(FINAL)]
             , Measure.[PO Process Detail_Loading Status(FINAL)], Measure.[PO Process Detail_Loading Qty(FINAL)]
             , Measure.[PO Process Detail_Diff Qty(FINAL)], Measure.[PO Process Detail_Item FR(FINAL)]
             , Measure.[PO Process Detail_CNTR FR(FINAL)], Measure.[PO Process Detail_Simulated By]
             , Measure.[PO Process Detail_Simulation Time]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(P)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(P)]
             , Measure.[PO Process Detail_Valid Fail Reason(P)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(M)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(M)]
             , Measure.[PO Process Detail_Valid Fail Reason(M)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ1)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ1)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ2)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ2)]
             , Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ3)]
             , Measure.[PO Process Detail_Valid Fail Reason(ADJ3)]
             , Measure.[PO Process Detail_DMD ETA 4Week Sum Qty]
             , Measure.[Loading PO Cal Master_JIG] , Measure.[Loading PO Cal Master_JIG Line]
             , Measure.[Loading PO Cal Master_Line], Measure.[Loading PO Cal Master_Item Height]
             , Measure.[Loading PO Cal Master_Item Width], Measure.[Loading PO Cal Master_Item Depth]
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
             , Measure.[Loading PO Cal Master_SKU Per Cntr]}) on column
        include memberproperties
                { [Sub Location].[Sub Location], [DisplayName] }
                { [Location].[Location], [DisplayName], [Shipment Type] }
         where {[Version].[Version Name]}
        ;

    - in_LoadingPOCntrPlan
        Select ([Location].[Location] * [Sub Location].[Sub Location] * [Item].[Item] * [Seq].[Seq]
             * [Time].[Week]) on row
             , ({Measure.[Loading PO Cntr Plan_Block], Measure.[Loading PO Cntr Plan_Account]
             , Measure.[Loading PO Cntr Plan_Cntr No], Measure.[Loading PO Cntr Plan_Group Id]
             , Measure.[Loading PO Cntr Plan_Item], Measure.[Loading PO Cntr Plan_Loading Qty]
             , Measure.[Loading PO Cntr Plan_Loading Status], Measure.[Loading PO Cntr Plan_Match Line]
             , Measure.[Loading PO Cntr Plan_Plan Type], Measure.[Loading PO Cntr Plan_Remark]
             , Measure.[Loading PO Cntr Plan_Result Sort], Measure.[Loading PO Cntr Plan_Ship To]
             , Measure.[Loading PO Cntr Plan_Simulated By]}) on column
         where {[Version].[Version Name]}
        ;

    - in_LoadingPOCntrPlanSeqInfo
        Select ([Time].[Week]) on row
             , ({Measure.[Loading PO Cntr Plan_Cntr No]}) on column
         where {[Version].[Version Name], Measure.[Loading PO Cntr Plan_Simulated By] == CurrentUser().[User Name]}
        ;

* Output Tables
    - out_POProcess
        Select ([Version].[Version Name] * [MFG Week].[MFG Week] * [Location].[Location] * [Sub Location].[Sub Location]
             * [Item].[Item] * [Time].[Week] * [SOP Week].[SOP Week] * [Delivery Week].[Delivery Week]) on row
             , ({Measure.[PO Process_Loading Status(P)], Measure.[PO Process_Loading Qty(P)]
             , Measure.[PO Process_Diff Qty(P)], Measure.[PO Process_Item FR(P)], Measure.[PO Process_CNTR FR(P)]
             , Measure.[PO Process_Loading Status(M)], Measure.[PO Process_Loading Qty(M)]
             , Measure.[PO Process_Diff Qty(M)], Measure.[PO Process_Item FR(M)], Measure.[PO Process_CNTR FR(M)]
             , Measure.[PO Process_Loading Status(ADJ1)], Measure.[PO Process_Loading Qty(ADJ1)]
             , Measure.[PO Process_Diff Qty(ADJ1)], Measure.[PO Process_Item FR(ADJ1)]
             , Measure.[PO Process_CNTR FR(ADJ1)], Measure.[PO Process_Loading Status(ADJ2)]
             , Measure.[PO Process_Loading Qty(ADJ2)], Measure.[PO Process_Diff Qty(ADJ2)]
             , Measure.[PO Process_Item FR(ADJ2)], Measure.[PO Process_CNTR FR(ADJ2)]
             , Measure.[PO Process_Loading Status(ADJ3)], Measure.[PO Process_Loading Qty(ADJ3)]
             , Measure.[PO Process_Diff Qty(ADJ3)], Measure.[PO Process_Item FR(ADJ3)]
             , Measure.[PO Process_CNTR FR(ADJ3)], Measure.[PO Process_Loading Status(FINAL)]
             , Measure.[PO Process_Loading Qty(FINAL)], Measure.[PO Process_Diff Qty(FINAL)]
             , Measure.[PO Process_Item FR(FINAL)], Measure.[PO Process_CNTR FR(FINAL)]
             , Measure.[PO Process_Simulated By], Measure.[PO Process_Simulation Time]}) on column
        ;

    - out_POProcessDetail
        Select ([Version].[Version Name] * [MFG Week].[MFG Week] * [Location].[Location] * [Sub Location].[Sub Location]
             * [Item].[Item] * [Seq].[Seq] * [Time].[Week]) on row
             , ({Measure.[PO Process Detail_Last Step]
             , Measure.[PO Process Detail_Loading Status(P)], Measure.[PO Process Detail_Loading Qty(P)]
             , Measure.[PO Process Detail_Diff Qty(P)], Measure.[PO Process Detail_Item FR(P)]
             , Measure.[PO Process Detail_CNTR FR(P)]
             , Measure.[PO Process Detail_Loading Status(M)], Measure.[PO Process Detail_Loading Qty(M)]
             , Measure.[PO Process Detail_Diff Qty(M)], Measure.[PO Process Detail_Item FR(M)]
             , Measure.[PO Process Detail_CNTR FR(M)]
             , Measure.[PO Process Detail_Loading Status(ADJ1)], Measure.[PO Process Detail_Loading Qty(ADJ1)]
             , Measure.[PO Process Detail_Diff Qty(ADJ1)], Measure.[PO Process Detail_Item FR(ADJ1)]
             , Measure.[PO Process Detail_CNTR FR(ADJ1)]
             , Measure.[PO Process Detail_Loading Status(ADJ2)], Measure.[PO Process Detail_Loading Qty(ADJ2)]
             , Measure.[PO Process Detail_Diff Qty(ADJ2)], Measure.[PO Process Detail_Item FR(ADJ2)]
             , Measure.[PO Process Detail_CNTR FR(ADJ2)]
             , Measure.[PO Process Detail_Loading Status(ADJ3)], Measure.[PO Process Detail_Loading Qty(ADJ3)]
             , Measure.[PO Process Detail_Diff Qty(ADJ3)], Measure.[PO Process Detail_Item FR(ADJ3)]
             , Measure.[PO Process Detail_CNTR FR(ADJ3)]
             , Measure.[PO Process Detail_Loading Status(FINAL)], Measure.[PO Process Detail_Loading Qty(FINAL)]
             , Measure.[PO Process Detail_Diff Qty(FINAL)], Measure.[PO Process Detail_Item FR(FINAL)]
             , Measure.[PO Process Detail_CNTR FR(FINAL)]
             , Measure.[PO Process Detail_Simulated By], Measure.[PO Process Detail_Simulation Time]}) on column
        ;

    - out_LoadingPOCntrPlan
        Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item]
             * [Location].[Location] * [Time].[Week]) on row
             , ({Measure.[Loading PO Cntr Plan_Account], Measure.[Loading PO Cntr Plan_Ship To]
             , Measure.[Loading PO Cntr Plan_Block], Measure.[Loading PO Cntr Plan_Group Id]
             , Measure.[Loading PO Cntr Plan_Cntr No], Measure.[Loading PO Cntr Plan_Item]
             , Measure.[Loading PO Cntr Plan_Loading Status], Measure.[Loading PO Cntr Plan_Loading Qty]
             , Measure.[Loading PO Cntr Plan_Match Line], Measure.[Loading PO Cntr Plan_Plan Type]
             , Measure.[Loading PO Cntr Plan_Remark], Measure.[Loading PO Cntr Plan_Result Sort]
             , Measure.[Loading PO Cntr Plan_Simulated By]}) on column
        ;

* Flow Summary
    STEP 0. Container Planning 전 필요 작업 수행
        Step 0-1. 전처리
        : 로직 구동 시 예외 사항이 발생하는 특정 컬럼들에 대해 전처리 작업 수행
        Step 0-2. Aggreagtion
        : in_LoadingDirOrderMgmt 테이블에 대해
          "Prod Week-From Site-To Site-Account-Ship To-Item-Loading Type-Cntr Type"을 기준으로
          Aggregation 한다.
        Step 0-3. 전처리
        : Container Planning 시에 필요한 컬럼 생성 작업 등 수행
    STEP 1. Container Planning for Single Item
        Step 1-1. Single Item 기준으로 Container Planning 시에 필요한 계산 작업 및 저장 작업을 수행한다.
        Step 1-2. Single Item 기준으로 Container Planning을 수행한다.
        : Step 1-1.에서 FTL로 계산된 행을 대상으로 컨테이너 댓수 -1 만큼 행을 복사하여 각 행에 대해 Container 1대를 할당하여
          Planning을 수행한다.
          Step 1-2.에서 Container 댓수가 1대 이상으로 계산되었으면서, FTL이 아닌 행을 대상으로 컨테이너스 댓수 -1 만큼 행을 복사하여
          마지막 행을 제외한 각 행에 대해 Container 1대를 할당하여 Planning을 수행한다.
    STEP 2. Container Planning for Mixed Loading
        Step 2-1. Single Item 처리 후 'LTL'로 분류된 데이터 중 단계별 Mix 기준('1st Mix', '2nd Mix', '3rd Mix')이 정의된 데이터를
                  추출한다.
        Step 2-2. Step 2-1.의 데이터를 단계별 Mix 기준에 맞춰 그룹핑한다.
        Step 2-3. Step 2-2의 그룹 기준으로 M/L Qty와 Multiple이 동일하고, M/L Qty가 Multiple의 배수가 아닌 데이터를 대상으로
                  Multiple 보정없는 Req만으로 Planning을 한다.
        : Req를 M/L Qty만큼 합산하여 컨테이너에 할당한다. 할당 후 나머지는 LTL로 분류한다.
        Step 2-4. Step 2-3. 처리 후 할당되지 않는 데이터를 대상으로 Req에 대해
                  Multiple로 보정한 수량(Round(Req/Multipel)*Multiple)을 계산한다.
        Step 2-5. Multiple로 보정된 Req를 기준으로 컨테이너 할당 작업을 수행한다.
        : Adjut Option1에 따라 F/R 비율을 계산한다.(Min F/R<=합산 F/R<=Max F/R 범위 수량 중,
          MIN이면 Min F/R에 가깝게, MAX이면 Max F/R에 가깝게)
        : 최초 적재량 할당은 Minimum 수량만큼 한다. 이후 적재량 할당은 Muliple 수량만큼 한다.
        : 잔여 수량이 Minimum 보다 적은 경우는 현재 할당 대상에서 제외한다.
        : Mulitple 보정 Req가 0인 경우는 할당하지 않는다.
        : 그룹 전체 아이템에 대해 할당을 완료하면 다음 그룹에 대해 할당 작업을 진행한다.
        : 최대 1st Mix, 2nd Mix, 3rd Mix까지 반복 수행한다.
    STEP 3. 1st ~ 3rd Mix 수행 후에도 할당되지 않는 아이템에 대해서 할당 작업을 수행
        Step 3-1. 가장 마지막으로 수행된 Mix Group 기준으로 미할당 아이템을 추출한다.
        Step 3-2. 동일 그룹 내에 LTL인 상태의 컨테이너가 있는 경우 미할당 아이템을 해당 컨테이너에 할당해 본다.
        : 할당 후 Max F/R 이하인 경우 다음 아이템에 대해 할당 작업을 진행한다.
        : 할당 후 Max F/R을 초과하면 다른 LTL 컨테이너에 대해 할당 작업을 진행한다.
        : 모든 LTL 컨테이너에 대해 할당 작업을 진행 후 할당이 되지 않는 아이템들은 새로운 컨테이너에 할당한다.
    STEP 4. LTL 상태의 컨테이너에 대해서 조정작업을 수행
        Step 4-1. LTL 상태의 데이터를 추출한다.
        Step 4-2. Single Item 기준 처리 대상을 추출한다.
        : 남은 잔량을 Single Item의 CUT/ADD 기준과 비교한다.
        : CUT 기준 미만이면 컨테이너에 할당하지 않는다.
        : ADD 기준 이상이면 M/L Qty만큼 할당한다.
        Step 4-3. Mixed Item 기준 처리 대상을 추출한다.
        : 마지막 Mix Group 및 최종 컨테이너 블럭 기준으로 처리 대상을 추출한다.
        : 컨테이너 블럭의 적재량과 Mixed Item의 CUT/ADD 기준과 비교한다.
        : CUT 기준 미만이면 컨테이너에 할당하지 않는다.
        : ADD 기준 이상이면 Adjust Option2에 따라 조정작업을 진행한다.
        : Adjust Option2가 Min Item Change이면 컨테이너 블럭 내 전체 아이템에 대해서 하나씩 순회하면서
          Multiple만큼을 순차적으로 할당한다.
        : Adjust Option2가 Max Profit이면 컨테이너 블랙 내 아이템 중 Profit Grade가 가장 높은 아이템을 대상으로 하나씩 순회하면서
          Multiple만큼을 순차적으로 할당한다.
        : 할당 시 Adjust Option1에 따라 FTL 여부를 계산한다.(Min F/R<=합산 F/R<=Max F/R 범위 수량 중,
          MIN이면 Min F/R에 가깝게, MAX이면 Max F/R에 가깝게)
    STEP 5. Container Numbering
        Step 5-1. Prod Week와 Lane(From Site-To Site-Account-Ship To) 기준으로 Grouping하여 Numbering한다.
    STEP 6. 시뮬레이션 결과를 Order에 맵핑한다.
        Step 6-1. 컨테이너 할당 결과를 입력 Order에 맵핑한다.
    STEP 7. Output 생성
        Step 7-1. 시뮬레이션 결과를 Output 형태에 맞춰 가공하여
                  Output 테이블(out_LoadingDirOrderMgmt, out_ContainerPlan)을 생성한다.

* Validation :

* Execution :
    EXEC plugin instance [PY_UI_POProcessNoneSKU_REG]
        for measures { [PO Process Detail_Simulated By] }
           using scope ([Version].[Version Name].[CWV_MP])
           using arguments {(ExecutionMode, "MediumWeight")
                         , (Param_OUT_VERSION, "CWV_MP")
                         , (Param_Adjust_Option1, "MAX")
                         , (Param_Adjust_Option2 , "Max Profit")
                         , (Param_User_Name , "gyeongh.kang")
                         , (Param_Step , "P")
                         , (Param_Check_Qty, "Current")
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
import datetime
from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_POProcessNoneSKU_REG"
str_input_dir = "Input/UIPOProcessNoneSKUREG"
str_output_dir = "Output/UIPOProcessNoneSKUREG"
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


def fn_get_multiple_values(int_init_val: int, int_multiple: int, int_max_val: int) -> list:
    """
    초기값, 배수, 최대값을 가지고 초기값에 n배수를 더하여 최대깞과 같아질 때까의 n배수의 목록을 리터하는 함수
    :param int_init_val: 초기값
    :param int_multiple: 배수
    :param int_max_val: 최대값
    :return: list_return
    """
    list_return = []

    # 최대값이 초기값보다 커야만 함.
    if int_max_val > int_init_val:
        int_multiplier = 1
        while (int_init_val + int_multiple * int_multiplier) <= int_max_val:
            list_return.append(int_init_val + int_multiple * int_multiplier)
            int_multiplier += 1

    return list_return


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

    # 대상건 테이블이 비어 있는 경우 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"] = (
        df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"].astype("object"))
    # Valid Fail Reason 컬럼에 대해 nan인 경우 None 값 적용
    df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"] = (
        df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"].
        where(df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"].notnull(), None))
    # Master, Method 모두 정상이면서, 다른 오류가 없는 경우만 추출하여 복사
    list_where_master_valid = (df_return[f"PO Process Detail_Item Unit Load Mix Match Chk({Param_Step})"] == "Y")
    list_where_method_valid = (df_return[f"PO Process Detail_Lane Load Mix Match Chk({Param_Step})"] == "Y")
    list_where_no_reason = (df_return[f"PO Process Detail_Valid Fail Reason({Param_Step})"].isnull())
    list_where_check_qty = None
    if Param_Check_Qty == "Current":
        # Check Qty가 0이거나 Min Qty보다 적은 경우는 시뮬레이션 대상에서 제외
        list_where_check_qty = (
                (df_return[f"PO Process Detail_Check Qty({Param_Step})"].fillna(0) == 0) |
                (df_return[f"PO Process Detail_Check Qty({Param_Step})"].fillna(0) < df_return["Loading PO Cal Master_Min Qty"].fillna(0)))
    elif Param_Check_Qty == "POPOnly":
        # POP Qty가 0이거나 Min Qty보다 적은 경우는 시뮬레이션 대상에서 제외
        list_where_check_qty = (
                (df_return[f"PO Process Detail_POP Qty({Param_Step})"].fillna(0) == 0) |
                (df_return[f"PO Process Detail_POP Qty({Param_Step})"].fillna(0) <
                 df_return["Loading PO Cal Master_Min Qty"].fillna(0)))
    elif Param_Check_Qty == "POPShort":
        # Check Qty가 0이거나 Min Qty보다 적은 경우는 시뮬레이션 대상에서 제외
        list_where_check_qty = (
                ((df_return[f"PO Process Detail_POP Qty({Param_Step})"].fillna(0) +
                  df_return[f"PO Process Detail_Short Qty({Param_Step})"].fillna(0)) == 0) |
                ((df_return[f"PO Process Detail_POP Qty({Param_Step})"] +
                  df_return[f"PO Process Detail_Short Qty({Param_Step})"].fillna(0)) <
                 df_return["Loading PO Cal Master_Min Qty"]))
    list_where = list_where_master_valid & list_where_method_valid & list_where_no_reason & ~list_where_check_qty
    df_return = df_return[list_where].copy(deep=True)

    # DisplayName의 경우 서버와 로컬이 명칭이 달라 상황에 맞게 변경할 수 있도록 변수에 저장
    if is_local:
        str_location_name = "Location.[DisplayName]"
        str_sub_location_name = "Sub Location.[DisplayName]"
    else:
        str_location_name = "Location.[Location$DisplayName]"
        str_sub_location_name = "Sub Location.[Sub Location$DisplayName]"

    # 로직에서 사용할 컬럼만 추출
    if Param_Step == "P" or Param_Step == "M":
        df_return = df_return[[
            "MFG Week.[MFG Week]", "Location.[Location]", str_location_name, "Location.[Shipment Type]",
            "Sub Location.[Sub Location]", str_sub_location_name, "Item.[Item]", "Item.[Product Group]",
            "Item.[Product]", "Item.[Project]",
            "Seq.[Seq]", "PO Process Detail_Block", "PO Process Detail_Account", "PO Process Detail_Ship To",
            "PO Process Detail_SOP ETD Week", "PO Process Detail_Chk Last Step(P)",
            f"PO Process Detail_POP Qty({Param_Step})", f"PO Process Detail_Short Qty({Param_Step})",
            f"PO Process Detail_Check Qty({Param_Step})", f"PO Process Detail_Max Qty({Param_Step})",
            "PO Process Detail_Simulated By", "PO Process Detail_Simulation Time", "PO Process Detail_DMD ETA 4Week Sum Qty",
            "Loading PO Cal Master_JIG",
            "Loading PO Cal Master_JIG Line", "Loading PO Cal Master_Line", "Loading PO Cal Master_Item Height",
            "Loading PO Cal Master_Item Width", "Loading PO Cal Master_Item Depth", "Loading PO Cal Master_Profit Grade",
            "Loading PO Cal Master_Profit Grade Priority", "Loading PO Cal Master_Loading Type",
            "Loading PO Cal Master_Cntr Type", "Loading PO Cal Master_Max Load Qty", "Loading PO Cal Master_LDM Qty",
            "Loading PO Cal Master_Multiple", "Loading PO Cal Master_Min Qty", "Loading PO Cal Master_Single FR Type",
            "Loading PO Cal Master_Single Min FR", "Loading PO Cal Master_Single Max FR",
            "Loading PO Cal Master_Single Min FTL", "Loading PO Cal Master_Single Max FTL",
            "Loading PO Cal Master_Single Cut Add", "Loading PO Cal Master_Mix FR Type", "Loading PO Cal Master_Mix Min FR",
            "Loading PO Cal Master_Mix Max FR", "Loading PO Cal Master_Mix Min FTL", "Loading PO Cal Master_Mix Max FTL",
            "Loading PO Cal Master_Mix Cut Add", "Loading PO Cal Master_1st Mix", "Loading PO Cal Master_2nd Mix",
            "Loading PO Cal Master_3rd Mix", "Loading PO Cal Master_Item Mix Group", "Loading PO Cal Master_SKU Per Cntr"
        ]].copy(deep=True)
    else:
        df_return = df_return[[
            "MFG Week.[MFG Week]", "Location.[Location]", str_location_name, "Location.[Shipment Type]",
            "Sub Location.[Sub Location]", str_sub_location_name, "Item.[Item]", "Item.[Product Group]",
            "Item.[Product]", "Item.[Project]",
            "Seq.[Seq]", "PO Process Detail_Block", "PO Process Detail_Account", "PO Process Detail_Ship To",
            "PO Process Detail_SOP ETD Week", "PO Process Detail_Chk Last Step(P)",
            f"PO Process Detail_Check Qty({Param_Step})", f"PO Process Detail_Max Qty({Param_Step})",
            "PO Process Detail_Simulated By", "PO Process Detail_Simulation Time", "PO Process Detail_DMD ETA 4Week Sum Qty",
            "Loading PO Cal Master_JIG",
            "Loading PO Cal Master_JIG Line", "Loading PO Cal Master_Line", "Loading PO Cal Master_Item Height",
            "Loading PO Cal Master_Item Width", "Loading PO Cal Master_Item Depth",
            "Loading PO Cal Master_Profit Grade",
            "Loading PO Cal Master_Profit Grade Priority", "Loading PO Cal Master_Loading Type",
            "Loading PO Cal Master_Cntr Type", "Loading PO Cal Master_Max Load Qty", "Loading PO Cal Master_LDM Qty",
            "Loading PO Cal Master_Multiple", "Loading PO Cal Master_Min Qty", "Loading PO Cal Master_Single FR Type",
            "Loading PO Cal Master_Single Min FR", "Loading PO Cal Master_Single Max FR",
            "Loading PO Cal Master_Single Min FTL", "Loading PO Cal Master_Single Max FTL",
            "Loading PO Cal Master_Single Cut Add", "Loading PO Cal Master_Mix FR Type",
            "Loading PO Cal Master_Mix Min FR",
            "Loading PO Cal Master_Mix Max FR", "Loading PO Cal Master_Mix Min FTL",
            "Loading PO Cal Master_Mix Max FTL",
            "Loading PO Cal Master_Mix Cut Add", "Loading PO Cal Master_1st Mix", "Loading PO Cal Master_2nd Mix",
            "Loading PO Cal Master_3rd Mix", "Loading PO Cal Master_Item Mix Group",
            "Loading PO Cal Master_SKU Per Cntr"
        ]].copy(deep=True)

    # 로직에서 사용하는 명칭으로 Rename
    df_return = df_return.rename(columns={
        "MFG Week.[MFG Week]": "Time.[Week]",
        "Location.[Location]": "To Site",
        "Sub Location.[Sub Location]": "Location.[Location]",
        "Item.[Item]": "Item",
        "Item.[Product Group]": "Product Group",
        "Item.[Product]": "Product",
        "Item.[Project]": "Project",
        "Location.[Shipment Type]": "Shipment Type",
        "Time.[Week]": "Org_Time.[Week]",
        "Seq.[Seq]": "Org_Seq"
    })

    # 칼럼 prefix 없애기
    str_po_process_detail = "PO Process Detail_"
    str_cal_master = "Loading PO Cal Master_"

    # 칼럼 str_pre_fix 를 다 없애고
    list_columns = df_return.columns
    list_columns_new = []
    for col in list_columns:
        new_col = col.replace(str_po_process_detail, "").replace(str_cal_master, "")
        list_columns_new.append(new_col)
    df_return.columns = list_columns_new

    # Param_Check_Qty 옵션에 따라 Chk Qty를 다르게 지정
    # Current - Check Qty(Step), POPOnly - POP(Step), POPShort - POP(Step) + Short(Step)
    # Param_Step이 "P"와 "M"일 때만 POPOnyl, POPShourt 선택 가능
    if Param_Step == "P" or Param_Step == "M":
        if Param_Check_Qty == "POPOnly":
            df_return["Chk Qty"] = df_return[f"POP Qty({Param_Step})"].fillna(0).astype(int)
        elif Param_Check_Qty == "POPShort":
            df_return["Chk Qty"] = (df_return[f"POP Qty({Param_Step})"].fillna(0).astype(int) +
                                    df_return[f"Short Qty({Param_Step})"].fillna(0).astype(int))
        else:
            df_return["Chk Qty"] = df_return[f"Check Qty({Param_Step})"].fillna(0).astype(int)
    else:
        df_return["Chk Qty"] = df_return[f"Check Qty({Param_Step})"].fillna(0).astype(int)

    # Account와 Ship To에 대해서 Null을 '-'로 채운다.
    df_return['Account'] = df_return['Account'].replace(r'^\s*$', np.nan, regex=True).fillna('-')
    df_return['Ship To'] = df_return['Ship To'].replace(r'^\s*$', np.nan, regex=True).fillna('-')

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return['Max Load Qty'] = df_return['Max Load Qty'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    df_return['LDM Qty'] = df_return['LDM Qty'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)

    # boolean 형식의 칼럼 중 비어 있는 값은 False로 채운다.
    df_return['JIG Line'] = df_return['JIG Line'].replace(r'^\s*$', np.nan, regex=True).fillna(False).astype(bool)

    # String 형식 칼럼 중 비어 있는 값은 '' 채운다.
    df_return[['JIG','Line']] = df_return[['JIG','Line']].replace(r'^\s*$', np.nan, regex=True).fillna('').astype(str)

    # Jig Line Value 값 생성
    df_return['JIG Line Value'] =  np.where(df_return['JIG Line'], df_return['JIG'] + df_return['Line'], '')
    df_return['JIG Line Value Key'] = np.where(df_return['JIG Line'], df_return['JIG Line Value'], 'N')

    # Aggr Grouping  Key 생성
    str_grouping_key = (
            df_return['Time.[Week]'].astype(str) + "_" +
            df_return['Location.[Location]'].astype(str) + "_" +
            df_return['To Site'].astype(str) + "_" +
            df_return['Account'].astype(str) + "_" +
            df_return['Ship To'].astype(str) + "_" +
            df_return['Item'].astype(str)  + "_" +
            df_return['Loading Type'].astype(str) + "_" +
            df_return['Cntr Type'].astype(str) + "_" +
            df_return['JIG Line Value Key']
    )
    df_return['Aggr Grouping Key'] = str_grouping_key

    df_return['1st Mix'] = df_return['1st Mix'].fillna("None").astype("object")
    df_return['2nd Mix'] = df_return['2nd Mix'].fillna("None").astype("object")
    df_return['3rd Mix'] = df_return['3rd Mix'].fillna("None").astype("object")

    # 전체 범위에서 유일한 키를 Seq.[Seq]로 추가함.
    df_return["Seq.[Seq]"] = range(1, len(df_return) + 1)
    df_return["Seq.[Seq]"] = df_return["Seq.[Seq]"].astype(str)

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
def fn_preprocess_for_container_planning(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Container Planning에 필요한 사전 처리를 수행한다.
    - 필요 철럼 생성 및 컬럼 타입 지정, 초기값 설정 등
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
    # Cntr Planning에 필요한 컬럼 추가
    df_return = df_return.assign(**{
        'Use Single Max Load Qty': np.where(df_return['Single FR Type'] == 'LDM',
                                            df_return['LDM Qty'], df_return['Max Load Qty']),
        'Use Mix Max Load Qty': np.where(df_return['Mix FR Type'] == 'LDM',
                                         df_return['LDM Qty'], df_return['Max Load Qty']),
        'Split Qty List': np.nan,
        'Cum Sum of Mixed Item FR': np.nan,
        'cntr_seq': np.nan,
        'cntr_block': np.nan,
        'Loading Qty Per Cntr': np.nan,
        'Plan Type': np.nan,
        'Cntr No': np.nan,
        'Plan Group Key': df_return['Time.[Week]'].astype(str) + '_' +
                          df_return['Location.[Location]'].astype(str) + '_' +
                          np.where(df_return['JIG Line Value'] != '', df_return['JIG Line Value'] + '_',  '' ) +
                          df_return['To Site'].astype(str) + '_' +
                          df_return['Account'].astype(str) + '_' +
                          df_return['Ship To'].astype(str),
        'Adj Chk Qty': np.nan,
        'Adj Min Qty': np.nan,
        'Adj Item FR': np.nan,
        'Cum Sum Adj Item FR': np.nan,
        'Planned Flag': np.nan,
        'Initial Qty': np.nan,
        'Multiple Qty': np.nan,
        'Loaded FR': np.nan,
        'Sum of Loaded FR': np.nan,
        'Mixed Rest Qty': np.nan,
        'Adj Mixed Rest Qty': np.nan,
        'Assigned Qty': np.nan,
        'Unassigned Qty': np.nan,
        'Last Mix Group' : np.nan,
        'Last Loading Qty': np.nan,
        '1st Mix Group' : np.nan,
        '1st Mix Group FTL Chk': np.nan,
        '2nd Mix Group': np.nan,
        '2nd Mix Group FTL Chk': np.nan,
        '3rd Mix Group': np.nan,
        '3rd Mix Group FTL Chk': np.nan,
    })
    df_return['cntr_block'] = df_return['cntr_block'].astype('object')
    df_return['Cntr No'] = df_return['Cntr No'].astype('object')
    df_return['Seq.[Seq]'] = df_return['Seq.[Seq]'].astype(str)

    df_return['1st Mix Group FTL Chk'] = df_return['1st Mix Group FTL Chk'].astype("object")
    df_return['2nd Mix Group FTL Chk'] = df_return['2nd Mix Group FTL Chk'].astype("object")
    df_return['3rd Mix Group FTL Chk'] = df_return['3rd Mix Group FTL Chk'].astype("object")


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
                                                    &  (df_return['Single Item Mod FR'] <= df_return['Single Max FR'])
                                                )
        ),
        'Single Item FTL',
        'LTL'
    )

    # 6) Single Item Complete Qty
    df_return['Single Item Complete Qty'] = np.where(
        df_return['Single Item Cntr Status'] =='Single Item FTL',
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

    return df_return


@_decoration_
def fn_container_planning_single_action(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
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
            df_return.groupby(by=['Time.[Week]', 'Location.[Location]', 'To Site', 'Account', 'Ship To', 'Seq.[Seq]'], dropna=False).cumcount() + 1)
    # Cntr Block을 기록 - sigle은 모두 자체로 블럭이므로 전부 1로 기록
    df_return['cntr_block'] = 1
    if str_p_cond == '0':
        # Cntr Planning 종류 구분 컬럼 - Single FTL - SF
        df_return['Plan Type'] = '01.SF'
    if str_p_cond == '1':
        # Cntr Planning 종류 구분 컬럼 - Single Complete - SC
        list_where_single_complete = df_return['cntr_seq'] <= df_return['Single Item FTL Count']
        df_return.loc[list_where_single_complete, 'Plan Type'] = '02.SC'
        df_return.loc[list_where_single_complete, 'Single Item Cntr Status'] = 'Single Complete FTL'
        # Single Complete의 마지막 행은 LTL로 처리되어야 하므로 컨테이너 번호 및 컨테이너 적재 수량, 컨테이너 블럭 초기화
        list_where_last = df_return['cntr_seq'] > df_return['Single Item FTL Count']
        df_return.loc[list_where_last, 'Loading Qty Per Cntr'] = np.nan
        df_return.loc[list_where_last, 'cntr_block'] = np.nan
        df_return.loc[list_where_last, 'cntr_seq'] = np.nan

    # 최종 싣는 Last Loading Qty에 넣기
    df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']

    return df_return


@_decoration_
def fn_container_planning_single(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """

    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # Single FTL, Single Complete 대상 Container Planning
    list_where_single_ftl = df_p_source['Single Item Cntr Status'] == 'Single Item FTL'
    list_where_single_complete_with_ltl = ~list_where_single_ftl & (df_p_source['Single Item FTL Count'] > 0)
    list_where_single_planning_target_not = ~list_where_single_ftl & (df_p_source['Single Item FTL Count'] == 0)
    # single FTL
    df_single_ftl = df_p_source[list_where_single_ftl].copy()
    # single Complete
    df_single_complete_with_ltl = df_p_source[list_where_single_complete_with_ltl].copy()
    # single_planning_target이 아닌 것
    df_single_planning_target_not = df_p_source[list_where_single_planning_target_not].copy()

    # single containter planning
    df_single_ftl = fn_container_planning_single_action(df_single_ftl, '0')
    df_single_complete_with_ltl = fn_container_planning_single_action(df_single_complete_with_ltl, '1')

    df_return = (
        pd.concat([df_single_ftl, df_single_complete_with_ltl, df_single_planning_target_not]).reset_index(drop=True)
    )

    # 최종 status에 넣기.
    df_return['Mixed Item Cntr Status'] = df_return['Single Item Cntr Status']

    return df_return


@_decoration_
def fn_set_group(df_p_source: pd.DataFrame, str_p_column: str) -> pd.DataFrame:# 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    df_return = df_p_source.copy(deep=True)
    str_col_measure = str_p_column

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

    # Mix Group Base Grouping Key
    # Adj Prod Week /FROM /To /Account /Ship To/ Shipment Type/ Cntr Type/ Loading Type / method Key / JigLine_Value
    # 2025015_P410_0003185680_AAA_SSS_DIR_40FT_FRONT_N ( All remain )
    # 2025015_P410_0003185680_AAA_SSS_DIR_40FT_FRONT_60_N ( JigLine이 체크 되어 있지 않을때 )
    # 2025015_P410_0003185680_AAA_SSS_DIR_20FT_FRONT_60_aa01 ( JigLine이 체크 되어 있고 값이 있을때 )
    # df_return['JIG Line Value Key'] = np.where(df_return['JIG Line'], df_return['JIG Line Value'], 'N')
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
            + df_return['JIG Line Value Key']
    )

    # Group Key 구분
    # 2) Item Mix Group 의 경우 KEY 설정
    # Mix Type이 Item Mix Group으로 지정되었으나, 해당 아이템에 Item Mix Group이 지정되지 않은 경우는 이전 단계 결과를 그대로 유지
    list_where = (df_return[str_col_measure] == 'Item Mix Group') & (df_return['Item Mix Group'].notnull())
    df_return.loc[list_where, 'Mix Group Base Grouping Key'] = (
            df_return['Time.[Week]'].astype(str)
            + '_'
            + df_return['Item Mix Group']
            + '_'
            + df_return['JIG Line Value Key']
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

    # 1st Mix Group
    df_return[str_col_measure + ' Group'] = df_return['Last Mix Group']

    return df_return


def fn_container_planning_except(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        2.2.2 Same Max Loading Qty FTL Check
        Grouping 된 Item 의 M/L Qty & Multiple 동일 하고, M/L Qty 가 Multiple 의 배수가 아닌 케이스 대상
        →  Multiple 보정없이 CNTR Planning
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
        return df_p_source

    # DF 복사
    df_return = df_p_source.copy(deep=True)

    # int_container_count : 실제 싣는 컨테이너 대수
    int_ml_qty = df_return.iloc[0]['Max Load Qty']
    int_chk_qty_sum = df_return.iloc[0]['Chk Qty Sum']

    # 전체 FR
    int_container_count_tot = int_chk_qty_sum / int_ml_qty
    # 실제 실어야 할 컨테이너 수
    int_container_count = int_chk_qty_sum // int_ml_qty
    # row 별로 cumsum
    df_return['CumSum Qty'] = df_return['Mixed Rest Qty'].cumsum()

    if int_container_count_tot > 1:
        # Split 되는 경우( 나머지 < rest qty )는 나머지를 아니면 Mixed Rest Qty → Remain 넣기
        df_return['Remain'] = np.where(
            df_return['CumSum Qty'] % int_ml_qty < df_return['Mixed Rest Qty'],
            df_return['CumSum Qty'] % int_ml_qty,
            df_return['Mixed Rest Qty']
        )

        # Remain Diff
        df_return['Remain Diff'] = df_return['Mixed Rest Qty'] - df_return['Remain']

        # list 순서 : [Remain Diff, Remain] Remain Diff 먼저
        df_return['Last Loading Qty'] = (
            df_return.apply(lambda row: ([row['Remain Diff']] if row['Remain Diff'] != 0 else [])
                                     +  ([row['Remain']] if row['Remain'] != 0 else []), axis=1)
        )

        # Container Planning ( Split )
        df_return = df_return.explode('Last Loading Qty').reset_index(drop=True)

        # cntr_block을 위한 계산 ( Split 후에 cumsum과 나머지, 몫으로 cntr_block 네이밍 )
        df_return['CumSum Qty'] = df_return['Last Loading Qty'].cumsum()
        df_return['Remain'] = df_return['CumSum Qty'] % int_ml_qty
        df_return['Quotient'] = df_return['CumSum Qty'] // int_ml_qty

        # ltl 인 건 ( 나머지건 ltl로 처리 )
        list_where_ltl = df_return['CumSum Qty'] > (int_ml_qty * int_container_count)
        df_return.loc[list_where_ltl, 'Loading Qty Per Cntr'] = np.nan
        df_return.loc[list_where_ltl, 'cntr_block'] = np.nan
        df_return.loc[list_where_ltl, 'Plan Type'] = np.nan
        # Mixed Rest Qty에 Last Loading Qty를 넣고 난 후 ltl건이므로 Last Loading Qty는 np.nan 처리
        df_return.loc[list_where_ltl, 'Mixed Rest Qty'] = df_return['Last Loading Qty']
        df_return.loc[list_where_ltl, 'Last Loading Qty'] = np.nan
        # ftl인건 cntr_block 세팅
        list_where_remain = df_return['Remain'] == 0
        df_return.loc[~list_where_ltl & list_where_remain,'cntr_block'] = df_return['Quotient']
        df_return.loc[~list_where_ltl & ~list_where_remain, 'cntr_block'] = df_return['Quotient'] +1
        df_return.loc[~list_where_ltl,'Plan Type'] = '03.MF.E'
        # cntr_seq
        df_return.loc[~list_where_ltl,'cntr_seq'] = (
            df_return[~list_where_ltl].groupby('Mix Group Base Grouping Key').cumcount() + 1
        )

    elif int_container_count_tot == 1:
        df_return['Last Loading Qty'] = df_return['Mixed Rest Qty']
        df_return['cntr_block'] = 1
        df_return['Plan Type'] = '03.MF.E'
        # cntr_seq
        df_return['cntr_seq'] = df_return.groupby('Mix Group Base Grouping Key').cumcount() + 1

    else:
        df_return['Loading Qty Per Cntr'] = np.nan
        df_return['cntr_block'] = np.nan
        df_return['Plan Type'] = np.nan
        df_return['Last Loading Qty'] = np.nan

    # Loading Qty Per Cntr 반영
    df_return['Loading Qty Per Cntr'] = df_return['Last Loading Qty']

    return df_return


@_decoration_
def fn_container_planning_mixed_common(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Container Planning 중 Mixed 처리에 필요한 공통 사항 처리
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

    # 데이터 수정 전 원본 DF 복사
    df_return = df_p_source.copy(deep=True)

    list_where_mixed_target = (df_return['Plan Type'].isna()) & (df_return['1st Mix'] != 'None')
    # Mixed 작업 전 공통 값 셋팅
    df_return.loc[list_where_mixed_target, 'Mixed Rest Qty'] = (
        df_return.loc)[list_where_mixed_target]['Single Item Rest Qty']
    df_return.loc[list_where_mixed_target, 'Planned Flag'] = False

    # Min Qty 예외 처리 - Min Qty가 0이면 Multiple 값을 Min Qty에 배정, 아니면 Multiple로 보정한 값을 배정
    if len(df_return.loc[list_where_mixed_target]) > 0:
        df_return.loc[list_where_mixed_target, 'Adj Min Qty'] = (
            np.where(
                df_return.loc[list_where_mixed_target]['Min Qty'] == 0,
                df_return.loc[list_where_mixed_target]['Multiple'],
                df_return.loc[list_where_mixed_target].apply(
                    lambda row:
                    int(common.gfn_get_round(row['Min Qty'] / row['Multiple'], 0)) * row['Multiple']
                    if int(common.gfn_get_round(row['Min Qty'] / row['Multiple'], 0)) > 0 else row['Multiple'],
                    axis=1
                )
            )
        )

    return df_return


def fn_container_planning_rearrange(df_p_target: pd.DataFrame, df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Split된 데이터에 대해 복원 대상 여부 확인 후 복원
    :param df_p_target:
    :param df_p_source:
    :return:
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_target.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_target)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_target

    # Split 원본행 추출
    list_where_parent = (df_p_target["Split Parent"] == True)
    df_parent = df_p_target[list_where_parent].copy(deep=True)
    # LTL인 행 추출
    list_where_parent_ltl = (df_parent["Mixed Item Cntr Status"] == "LTL")
    df_parent_ltl = df_parent[list_where_parent_ltl].copy(deep=True)
    # 원본행에 LTL인 행이 있으면 사본행 검사
    if not df_parent_ltl.empty and len(df_parent_ltl) > 0:
        # Split 사본행 추출
        list_where_child = (df_p_target["Split Child"] == True)
        df_child = df_p_target[list_where_child].copy(deep=True)
        # LTL인 행 추출
        list_where_child_ltl = (df_child["Mixed Item Cntr Status"] == "LTL")
        df_child_ltl = df_child[list_where_child_ltl].copy(deep=True)
        # 사본행에 LTL인 행이 있으면 사본행 검사
        if not df_child_ltl.empty and len(df_child_ltl) > 0:
            # LTL인 원본행을 루프로 순회하면서 사본행이 LTL인지 확인
            for inx in range(len(df_parent_ltl)):
                # 컨테이너 블럭번호를 추출한다.
                str_cntr_block = df_parent_ltl.iloc[inx]['cntr_block']
                # 원본행 Seq를 추출한다.
                str_parent_inx = df_parent_ltl.iloc[inx]['Seq.[Seq]']
                # 사본행 Seq를 만든다.
                str_child_inx = str_parent_inx + "-1"
                # LTL 원본행에서 파생된 LTL 사본행을 찾는다.
                list_where_child_target = (df_child_ltl["Seq.[Seq]"] == str_child_inx)
                df_child_target = df_child_ltl[list_where_child_target].copy(deep=True)
                if not df_child_target.empty and len(df_child_target) > 0:
                    # LTL 원본행에서 파생된 LTL 사본행이 있다면 해당 행을 지우고, LTL 원본행을 Splite 전 상태로 복원한다.
                    df_p_target = df_p_target[df_p_target["Seq.[Seq]"] != str_child_inx].copy(deep=True)
                    num_rest_qty = df_p_source[df_p_source["Seq.[Seq]"] == str_parent_inx].iloc[0]["Mixed Rest Qty"]
                    df_p_target.loc[df_p_target["Seq.[Seq]"] == str_parent_inx, "Mixed Rest Qty"] = num_rest_qty
                else:
                    # LTL 원본행에서 파생된 LTL 사본행이 없다면 다음으로 넘어간다.
                    continue
            df_return = df_p_target.copy(deep=True)
        else:
            # 원본행에 LTL이 있더라도 사본행에 LTL인 행이 없으면 Split 상태 유지
            df_return = df_p_target.copy(deep=True)
    else:
        # 원본행에 LTL인 행이 없으면 Split 상태 유지
        df_return = df_p_target.copy(deep=True)

    return df_return


def fn_container_planning(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    Mixed Container Planning 세부 로직을 수행한다.
    :param df_p_source:
    :param str_p_cond:
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

    # 데이터 변경 전 원본 DF 복사
    df_return = df_p_source.copy(deep=True)
    df_return = df_return.sort_values(by=['Profit Grade Priority', 'Use Mix Max Load Qty', 'Adj Chk Qty'],
                                      ascending=[True, True, False]).reset_index(drop=True)

    # Next Mix 존재 여부
    flag_next_mix = True
    str_step = ""
    if str_p_cond == "1st":
        str_step = df_return["2nd Mix"].iloc[0]
    elif str_p_cond == "2nd":
        str_step = df_return["3rd Mix"].iloc[0]
    elif str_p_cond == "3rd":
        str_step = "None"
    if str_step == "None":
        flag_next_mix = False
    else:
        flag_next_mix = True

    # Plan 여부 플래그 초기화
    df_return['Planned Flag'] = False
    # cntr_block, cntr_seq 초기화
    df_return['cntr_block'] = np.nan
    df_return['cntr_seq'] = np.nan
    # Split 관련 플래그를 초기화한다.
    flag_split = False
    # Split 시 원본 상태에서 처리되는 행 판별 플래그
    df_return["Split Parent"] = False
    # Split 시 원본에서 복사되어 처리되는 행 판별 플래그
    df_return["Split Child"] = False
    # Planning할 컨테이너 댓수 계산
    num_sum_fr = df_return['Adj Item FR'].sum()
    # if math.isinf(num_sum_fr):
    #     logger.Note(p_note='현재 Container Block의 F/R 합계가 무한수가 되어 계산이 불가능합니다.', p_log_level=LOG_LEVEL.warning())
    #     num_sum_fr = 0
    int_cntr_cnt = int(num_sum_fr) + 1 if num_sum_fr % 1 != 0 else int(num_sum_fr)
    # Max F/R
    num_basis_max_fr = df_return['Mix Max FR'].iloc[0]
    # Min F/R
    num_basis_min_fr = df_return['Mix Min FR'].iloc[0]
    # 컨테이너 댓수만큼 루프 순환
    for i in range(0, int_cntr_cnt):
        int_cntr_seq = 0
        # FTL flag를 초기화한다.
        ftl_flag = False
        # Cntr Block 내 전체 아이템 FR 합계
        num_sum_fr = 0
        # 그룹 내에서 Cntr에 담기지 않는 행만 추출
        df_loop = df_return[~df_return['Planned Flag']].reset_index(drop=True).copy(deep=True)
        # Cntr에 담기지 않는 행에 대해서 루프 순환
        for inx in range(len(df_loop)):
            # Planning 대상 행 추출 조건을 설정한다.
            list_where_planning_target = df_return['Seq.[Seq]'] == df_loop.iloc[inx]['Seq.[Seq]']
            # if i == 4:
            #     print('DEBUG')
            # FTL flag를 초기화한다.
            # 현재 행에 대한 적재 수행 여부 플래그
            load_flag = False
            # 현재 행의 잔량 전체에 대한 적재 수행 여부 플래그
            full_load_flag = False
            if df_loop.iloc[inx]['Adj Chk Qty'] == 0:
                # Multiple을 기준으로 보정한 Chk Qty가 0인 경우는 컨테이너 할당에서 제외한다. '05.NP'
                df_return.loc[list_where_planning_target, 'Planned Flag'] = False
                df_return.loc[list_where_planning_target, 'Plan Type'] = '05.NP'
                df_return.loc[list_where_planning_target, 'Adjust Cut Add'] = 'CUT'
                df_return.loc[list_where_planning_target, 'Last Loading Qty'] = np.nan
                df_return.loc[list_where_planning_target, 'Loading Qty Per Cntr'] = np.nan
                df_return.loc[list_where_planning_target, 'cntr_block'] = np.nan
                df_return.loc[list_where_planning_target, 'cntr_seq'] = np.nan
                continue
            else:
                # 최초 적재 수량 : Min Qty 만큼을 최초 적재 수량을 지정한다.
                int_init_qty = df_loop.iloc[inx]['Adj Min Qty']
                # Multiple 기준 적재 수량
                int_multiple_qty = 0
                if int_init_qty > df_loop.iloc[inx]['Adj Mixed Rest Qty']:
                    # 잔량이 Min Qty 미만이어서 최초 적재가 불가능한 경우는 다음 행으로 이동
                    continue
                if (num_sum_fr + df_loop.iloc[inx]['Adj Item FR']) < num_basis_min_fr:
                    # 현재 행의 남은 잔여 Qty 전체를 Cntr에 넣어도 Min F/R 보다 적은 경우 Cntr Planning 값을 저장한다.
                    int_multiple_qty = df_loop.iloc[inx]['Adj Chk Qty'] - int_init_qty
                    # 잔량을 전부 적재하였으므로 적재 플래그를 조정한다.
                    load_flag = True
                    full_load_flag = True
                else:
                    # 현재 행의 남은 잔여 Qty 전체를 Cntr에 넣어서 Min F/R 이상이 된 경우
                    if (num_sum_fr + (int_init_qty / df_loop.iloc[inx]['Use Mix Max Load Qty'])) > num_basis_max_fr:
                        # Initial Qty(Min Qty)만 채웠으나 Max F/R을 초과한 경우는 다음 행 탐색
                        continue
                    else:
                        # 최초 적재만 수행한 후의 F/R 합계가 Min F/R 이상인 경우
                        if (num_sum_fr + (int_init_qty / df_loop.iloc[inx]['Use Mix Max Load Qty'])) >= num_basis_min_fr:
                            # 해당 Container Block에 대해서 FTL을 만족하는 것으로 한다.
                            ftl_flag = True
                            # 현재 행이 적재된 것으로 한다.
                            load_flag = True
                        # 최소량부터 잔량까지 multiple만큼씩 증가하는 리스트 구성
                        list_load_qty = fn_get_multiple_values(int_init_qty, df_loop.iloc[inx]['Multiple'],
                                                               df_loop.iloc[inx]['Adj Chk Qty'])
                        if len(list_load_qty) > 0:
                            # multiple만큼을 더하면서 F/R 기준을 만족하는지 체크하는 루프 순회
                            for qtyInx in range(len(list_load_qty)):
                                # 현재 적재량에 대한 F/R를 구한다.
                                num_curr_fr = list_load_qty[qtyInx] / df_loop.iloc[inx]['Use Mix Max Load Qty']
                                # 현재 적재량까지의 F/R 합계를 계산한다.
                                num_curr_sum_fr = num_sum_fr + num_curr_fr
                                if num_curr_sum_fr <= num_basis_max_fr:
                                    # 현재 적재량 합계가 Max F/R 이하인 경우
                                    if Param_Adjust_Option1 == 'MIN':
                                        # Adjust Option1이 'MIN'이면 현재 상태에서 FTL 처리하고 적재량 순회 루프 종료
                                        int_multiple_qty = list_load_qty[qtyInx] - int_init_qty
                                        ftl_flag = True
                                        load_flag = True
                                        break
                                    elif Param_Adjust_Option1 == 'MAX':
                                        # Adjust Option1이 'MAX'면 다음번 적재량을 더한 합산 F/R을 계산한다.
                                        if qtyInx + 1 < len(list_load_qty):
                                            num_next_sum_fr = (
                                                    num_sum_fr +
                                                    (list_load_qty[qtyInx + 1] /
                                                     df_loop.iloc[inx]['Use Mix Max Load Qty']))
                                        else:
                                            # 이미 적재가 완료되었다면 기준 이상인 적재량을 할당한다.
                                            num_next_sum_fr = 1000
                                        # Adjust Option1이 'MAX'면 다음 적재량에 대해서도 확인
                                        if num_next_sum_fr <= num_basis_max_fr:
                                            # 다음번 적재량도 Max F/R 이하이므로 다음 적재량으로 이동
                                            continue
                                        else:
                                            int_multiple_qty = list_load_qty[qtyInx] - int_init_qty
                                            # 다음번 적재량이 Max F/R 초과이므로 현재 적재량으로 판단
                                            if num_curr_sum_fr >= num_basis_min_fr:
                                                # 현재 상태에서 FTL 처리하고 적재량 순회 루프 종료
                                                ftl_flag = True
                                                load_flag = True
                                                break
                                            else:
                                                # 현재 상태에서 적재 처리 하고 적재량 순회 루프 종료
                                                load_flag = True
                                                break
                                else:
                                    break

                if load_flag:
                    # 현재 행이 포함되어야 함으로 Cntr Seq를 증가시킨다.
                    int_cntr_seq += 1
                    # Min Qty를 Initial Qty에 넣는다.
                    df_return.loc[list_where_planning_target, 'Initial Qty'] = int_init_qty
                    # Multiple Qty를 넣는다.
                    df_return.loc[list_where_planning_target, 'Multiple Qty'] = int_multiple_qty
                    # 총 적재량을 계산한다.
                    int_loaded_qty = int_init_qty + int_multiple_qty
                    # 적재량 기준으로 현재 행의 F/R을 계산하여 추가
                    num_loaded_fr = int_loaded_qty / df_loop.iloc[inx]['Use Mix Max Load Qty']
                    df_return.loc[list_where_planning_target, 'Loaded FR'] = num_loaded_fr
                    # 위에서 계산한 F/R로 Sum F/R을 계산한다.
                    num_sum_fr += num_loaded_fr
                    df_return.loc[list_where_planning_target, 'Sum of Loaded FR'] = num_sum_fr
                    # 적재량을 제외한 잔량을 계산하여 저장한다.
                    int_rest_qty = df_loop.iloc[inx]['Adj Mixed Rest Qty'] - int_loaded_qty
                    df_return.loc[list_where_planning_target, 'Adj Mixed Rest Qty'] = int_rest_qty
                    # 적재량을 저장한다.
                    df_return.loc[list_where_planning_target, 'Assigned Qty'] = int_loaded_qty
                    # 원본 Qty와 현재 적재량 차를 미할당량에 저장한다.
                    df_return.loc[list_where_planning_target, 'Unassigned Qty'] = (
                            df_loop.iloc[inx]['Chk Qty'] - df_loop.iloc[inx]['Single Item Complete Qty'] - int_loaded_qty)
                    # 현재 행이 Cntr에 적재되었으므로 플래그를 true 저장한다.
                    df_return.loc[list_where_planning_target, 'Planned Flag'] = True
                    # Cntr 블럭 내 일련번호를 넣어준다.
                    df_return.loc[list_where_planning_target, 'cntr_seq'] = int_cntr_seq
                    # Cntr 블럭 번호를 넣어준다.
                    df_return.loc[list_where_planning_target, 'cntr_block'] = i + 1
                    if not full_load_flag and int_rest_qty > 0:
                        # 현재 행에 대해서 일부만 적재된 경우
                        # 현재 행을 Split하기 위해 현재 행을 복사하여 새로운 행을 만든다.
                        df_new = df_return[list_where_planning_target].copy(deep=True)
                        # 새로운 행의 값들을 초기화한다.
                        df_new = df_new.assign(**{
                            'Initial Qty': np.nan,
                            'Multiple Qty': np.nan,
                            'Loaded FR': np.nan,
                            'Sum of Loaded FR': np.nan,
                            'Assigned Qty': np.nan,
                            'Unassigned Qty': np.nan,
                            'Planned Flag': False,
                            'cntr_seq': np.nan,
                            'cntr_block': np.nan,
                        })
                        # 원본 DF의 조정 후 잔량을 0으로 설정한다. - 새로운 행에 잔량을 설정하기 때문에 원본행의 잔량은 0이 되어야 한다.
                        df_return.loc[list_where_planning_target, 'Adj Mixed Rest Qty'] = 0
                        df_return.loc[list_where_planning_target, 'Mixed Rest Qty'] = 0
                        df_return.loc[list_where_planning_target, 'Adj Chk Qty'] = int_loaded_qty
                        # Split 관련 부모 플래그를 설정한다.
                        df_return.loc[list_where_planning_target, 'Split Parent'] = True
                        # 새로운 행의 Seq를 Unique하게 만들기 위해 기존 Seq에 '-1'를 추가한 문자열로 설정한다.
                        df_new['Seq.[Seq]'] = df_loop.iloc[inx]['Seq.[Seq]'] + '-1'
                        # 새로운 행의 잔량을 루프 행의 잔량에서 전체 적재량을 뺀 값으로 저장한다.
                        df_new['Adj Mixed Rest Qty'] = df_loop.iloc[inx]['Adj Mixed Rest Qty'] - int_loaded_qty
                        # 새로운 행의 Multiple 반경 qty도 잔량으로 조정된 잔량으로 변경 저장한다.
                        df_new['Adj Chk Qty'] = df_new['Adj Mixed Rest Qty']
                        df_new['Mixed Rest Qty'] = df_new['Adj Mixed Rest Qty']
                        # 새로운 행의 Adj Item FR을 변경된 Qty로 재설정한다.
                        df_new["Adj Item FR"] = df_new['Adj Chk Qty'] / df_new['Use Mix Max Load Qty']
                        # Split 관련 자식 플래그를 설정한다.
                        df_new["Split Child"] = True
                        flag_split = True
                        # 루프 행의 Seq를 추출한다.
                        str_target_seq = df_loop.iloc[inx]['Seq.[Seq]']
                        # 원본 DF에서 루프 행의 Seq와 동일한 행을 찾아 인덱스를 저장한다.
                        target_index = df_return[df_return['Seq.[Seq]'] == str_target_seq].index[0]
                        # 해당 인덱스를 기준으로 Seq를 포한한 곳까지를 하나의 DF로 구성한다.
                        df_front = df_return.iloc[:target_index+1]
                        # 나머지를 다른 하나의 DF로 구성한다.
                        df_back = df_return[target_index+1:]
                        # 분리한 DF 사이에 신규 행을 넣어서 하나의 DF로 구성한다.
                        df_return = pd.concat([df_front, df_new, df_back])
                        # 인덱스를 초기화한다.
                        df_return = df_return.reset_index(drop=True)
                    if ftl_flag:
                        # 현재 상태가 FTL이면
                        # FTL 문구를 만든다.
                        str_ftl = df_loop.iloc[inx][str_p_cond + ' Mix'] + ' FTL'
                        # 현재 Container Block을 가진 모든 행에 대해서 FTL 문구를 채운다.
                        df_return.loc[df_return['cntr_block'] == i + 1, str_p_cond + ' Mix Group FTL Chk'] = str_ftl
                        df_return.loc[df_return['cntr_block'] == i + 1, 'Mixed Item Cntr Status'] = str_ftl
                        # 현재 Container Block을 가진 모든 행에 대해서 Plan Type을 03.MF(Mixed FTL)로 채운다.
                        df_return.loc[df_return['cntr_block'] == i + 1, 'Plan Type'] = '03.MF'
                        # 현재 Container Block을 가진 모든 행에 대해서 컨테이너당 적재량을 저장한다.
                        df_return.loc[df_return['cntr_block'] == i + 1, 'Loading Qty Per Cntr'] = (
                            df_return.loc)[df_return['cntr_block'] == i + 1]['Assigned Qty']
                        # 현재 Container Block을 가진 모든 행에 대해서 최종 적재량을 저장한다.
                        df_return.loc[df_return['cntr_block'] == i + 1, 'Last Loading Qty'] = (
                            df_return.loc)[df_return['cntr_block'] == i + 1]['Assigned Qty']
                        break
                    else:
                        # 현재 Container Block을 가진 모든 행에 대해서 LTL 문구를 채운다.
                        df_return.loc[df_return['cntr_block'] == i + 1, str_p_cond + ' Mix Group FTL Chk'] = 'LTL'
                        df_return.loc[df_return['cntr_block'] == i + 1, 'Mixed Item Cntr Status'] = 'LTL'

    if flag_split and flag_next_mix:
        df_return = fn_container_planning_rearrange(df_return, df_p_source)

    return df_return


@_decoration_
def fn_container_planning_mixed(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    Item Mixed Planning을 수행한다.
    :param df_p_source:
    :param str_p_cond:
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

    # 데이터 가공 전 원본 DF 복사
    df_return = df_p_source.copy(deep=True)
    df_return[str_p_cond + ' Mix'] = df_return[str_p_cond + ' Mix'].astype('object')
    # 대상건 : Mix 타입이 None이 아니고, LTL인 ROW 만 대상으로 한다. 선처리로 Plan Type이 지정되어 있는 경우도 제외한다.
    list_where = (
            (df_return[str_p_cond + ' Mix'] != 'None')
            & (df_return['Mixed Item Cntr Status'] == 'LTL')
            & (df_return['Plan Type'].isna())
    )

    if str_p_cond == '1st':
        list_where_item_mix_group_notna = (
                (df_return[str_p_cond + ' Mix'] != 'Item Mix Group') |
                ((df_return[str_p_cond + ' Mix'] == 'Item Mix Group') & (df_return['Item Mix Group'].notna()))
        )
        list_where = list_where & list_where_item_mix_group_notna

    # 발췌 대상건에 대해서만 계산.
    df_return_not_target = df_return[~list_where].copy(deep=True)
    df_return = df_return[list_where].copy(deep=True)

    if not df_return.empty and len(df_return) > 0:
        # Mix Group 기준 Grouping: Single FTL Case 제외 Rest Qty 기준 Grouping
        df_return = fn_set_group(df_return, str_p_cond + ' Mix')

        # Same Max Loading Qty FTL Check
        # Grouping 된 Item의 M/L Qty & Multiple 동일하고, M/L Qty 가 Multiple 의 배수가 아닌 케이스 대상
        # : Multiple 보정없이 CNTR Planning
        df_return[['Max Load Qty Unique', 'Multiple Unique']] = (
            df_return.groupby('Mix Group Base Grouping Key')[['Max Load Qty','Multiple' ]].transform('nunique')
        )
        df_return['Chk Qty Sum'] = df_return.groupby('Mix Group Base Grouping Key')['Mixed Rest Qty'].transform('sum')
        # M/L Qty & Multiple 동일
        list_where_except_unique = (df_return['Max Load Qty Unique'] == 1) & (df_return['Multiple Unique'] == 1)
        # M/L Qty 가 Multiple 의 배수가 아니고
        list_where_except_multiple_not = df_return['Max Load Qty'] % df_return['Multiple'] > 0
        list_where_except = list_where_except_unique & list_where_except_multiple_not
        # 예외 Container Planning
        df_return_except = df_return[list_where_except]
        if not df_return_except.empty and len(df_return_except) > 0:
            # sort 기준( Mix Group Base Grouping Key, Max Load Qty, P/G, Mixed Rest Qty )
            df_return_except = (
                df_return_except
                .sort_values(by=['Mix Group Base Grouping Key', 'Profit Grade Priority', 'Max Load Qty',
                                 'Mixed Rest Qty'], ascending=[True, True, True, False])
                .groupby('Mix Group Base Grouping Key', group_keys=True)
                .apply(fn_container_planning_except)
                .reset_index(drop=True)
            )
            # 예외 Container Planning FTL/LTL 판별 여부 ( 1st Mix Group FTL Chk, Mixed Item Cntr Status )
            list_where_except_ltl = df_return_except['Plan Type'].isna()
            df_return_except[str_p_cond + ' Mix Group FTL Chk'] = (
                np.where(~list_where_except_ltl,
                         df_return_except[str_p_cond + ' Mix'] +' FTL',
                         'LTL')
            )
            # Mixed Item Cntr Status
            df_return_except['Mixed Item Cntr Status'] = df_return_except[str_p_cond + ' Mix Group FTL Chk']

        # 예외 처리 대상에 대해 Container 할당 후 남은 부분에 대해서 추출
        list_where_except_ltl = df_return_except['Plan Type'].isna()
        # 예외 처리된 대상을 제외한 나머지 DF를 concat한 후 해당 DF를 대상으로 Mixed Container Planning을 수행한다.
        df_return = (
            pd.concat([df_return_except[list_where_except_ltl], df_return[~list_where_except]]).reset_index(drop=True))
        if not df_return.empty:
            # Check Qty Multiple 반영: round [(Checkqty/Mutiple),0] * Multiple
            df_return['Adj Chk Qty'] = df_return.apply(
                lambda row:
                int(common.gfn_get_round(row['Mixed Rest Qty'] / row['Multiple'], 0)) * row['Multiple'], axis=1
            )
            # Multiple 반영 수량을 복사하여 저장한다.
            df_return['Adj Mixed Rest Qty'] = df_return['Adj Chk Qty']
            # 개별 Item별 F/R 계산
            df_return['Adj Item FR'] = df_return['Adj Chk Qty'] / df_return['Use Mix Max Load Qty']
            # Mix Group 기준 CNTR Planning.
            df_return = (df_return.groupby(by=str_p_cond + ' Mix Group').
                         apply(lambda group: fn_container_planning(group, str_p_cond)))

        # 반환을 위해 작업대상 DF와 비대상 DF concat
        df_return = (
            pd.concat([df_return_not_target, df_return, df_return_except[~list_where_except_ltl]], ignore_index=True))
    else:
        df_return = df_return_not_target.copy(deep=True)

    ####################################################################################################################
    # Debugging을 위해 필요한 컬럼만 추출
    if is_local and not df_return.empty and len(df_return) > 0:
        list_column = ['Seq.[Seq]', 'Item', 'Max Load Qty', 'Min Qty', 'Multiple', 'Profit Grade',
                       'Profit Grade Priority', 'Chk Qty', 'cntr_seq', 'cntr_block',
                       'Loading Qty Per Cntr', 'Plan Type', 'Adj Chk Qty', 'Adj Item FR', 'Planned Flag', 'Adj Min Qty',
                       'Initial Qty', 'Multiple Qty', 'Loaded FR', 'Sum of Loaded FR', 'Mixed Rest Qty',
                       'Adj Mixed Rest Qty', 'Assigned Qty', 'Unassigned Qty', 'Last Loading Qty',
                       'Mixed Item Cntr Status', 'Last Mix Group'
                       ]
        list_1st = ['1st Mix Group', '1st Mix Group FTL Chk']
        list_2nd = ['2nd Mix Group', '2nd Mix Group FTL Chk']
        list_3rd = ['3rd Mix Group', '3rd Mix Group FTL Chk']

        if str_p_cond == '1st':
            list_column = list_column + list_1st
        elif str_p_cond == '2nd':
            list_column = list_column + list_1st + list_2nd
        elif str_p_cond == '3rd':
            list_column = list_column + list_1st + list_2nd + list_3rd

        df_return_debug = df_return[list_column]
        fn_log_dataframe(df_return_debug, 'df_return_debug_' + str_p_cond)
    ####################################################################################################################

    return df_return


def fn_cntr_plan_inter_process_detail(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 데이터 가공 전 원본 DF 복사
    df_return = df_p_source.copy(deep=True)

    # 현재 처리 그룹 내에서 컨테이너 할당 데이터 중 FTL, LTL 데이터와 미할당 데이터를 분리한다.
    list_where_cntr_not_planned = df_return['cntr_block'].isna()
    df_not_planned = df_return[list_where_cntr_not_planned].copy(deep=True)
    # 미할당 데이터가 있는 경우만 처리.
    list_del_taget_inx = []
    if not df_not_planned.empty and len(df_not_planned) > 0:
        df_planned = df_return[~list_where_cntr_not_planned].copy(deep=True)
        list_where_ltl = df_planned['Mixed Item Cntr Status'] == 'LTL'
        df_planned_ltl = df_planned[list_where_ltl].copy(deep=True)
        df_planned_ftl = df_planned[~list_where_ltl].copy(deep=True)
        if not df_planned_ltl.empty and len(df_planned_ltl) > 0:
            # Max F/R
            num_basis_max_fr = df_planned_ltl.iloc[0]['Mix Max FR']
            if not df_planned_ltl.empty and len(df_planned_ltl) > 0:
                # ltl 컨테이너가 있는 경우에는 기존 컨테이너에 미할당 데이터를 할당하는 로직 먼저 수행
                # 현재 그룹에 속한 컨테이너 블럭을 리스트에 저장한다.
                list_cntr_block = df_planned_ltl['cntr_block'].sort_values().drop_duplicates().tolist()
                for cntr_block in list_cntr_block:
                    for inx in range(len(df_not_planned)):
                        list_where_cntr_block = df_planned_ltl['cntr_block'] == cntr_block
                        # 기할당 아이템 적재량의 F/R 합을 추출한다.
                        num_sum_fr = df_planned_ltl[list_where_cntr_block]['Loaded FR'].sum()
                        # 미할당 데이터(잔량이 Min Qty보다 적은 아이템) 순환 루프
                        num_fr = df_not_planned.iloc[inx]['Adj Min Qty'] / df_not_planned.iloc[inx]['Use Mix Max Load Qty']
                        if num_sum_fr + num_fr <= num_basis_max_fr:
                            num_sum_fr += num_fr
                            # 미할당 데이터를 현재 컨테이너 블럭에 추가하고 미할당 데이터에서 삭제함.
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Planned Flag')] = True
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Initial Qty')] = (
                                df_not_planned.iloc)[inx]['Adj Min Qty']
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Multiple Qty')] = 0
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Assigned Qty')] = (
                                df_not_planned.iloc)[inx]['Adj Min Qty']
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Unassigned Qty')] = (
                                    df_not_planned.iloc[inx]['Mixed Rest Qty'] - df_not_planned.iloc[inx]['Adj Min Qty'])
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Adj Mixed Rest Qty')] = 0
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Loaded FR')] = num_fr
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('cntr_block')] = cntr_block
                            new_cntr_seq = df_planned_ltl.loc[list_where_cntr_block]['cntr_seq'].max() + 1
                            df_not_planned.iloc[inx, df_not_planned.columns.get_loc('cntr_seq')] = new_cntr_seq
                            df_planned_ltl = pd.concat([df_planned_ltl, df_not_planned.iloc[[inx]]], ignore_index=True)
                            list_del_taget_inx.append(df_not_planned.iloc[inx].name)
                    if len(list_del_taget_inx) > 0 :
                        df_not_planned.drop(list_del_taget_inx, inplace=True)
                        list_del_taget_inx = []

            if not df_not_planned.empty and len(df_not_planned) > 0:
                # ltl 컨테이너가 없거나 할당 로직을 거친 후에도 미할당 데이터가 남은 경우 신규 컨테이너에 할당
                # 신규 컨테이너 할당을 위해 현재 그룹에서 가장 큰 컨테이너 블럭을 추출한다.
                max_cntr_block = df_planned['cntr_block'].max()
                # 미할당 데이터에 대해서 전부 적재량을 Min Qty로 설정하고 F/R과 Sum F/R을 구한다.
                num_sum_fr = 0
                int_cntr_seq = 0
                int_cntr_block = int(max_cntr_block) + 1
                for inx in range(len(df_not_planned)):
                    num_fr = df_not_planned.iloc[inx]['Adj Min Qty'] / df_not_planned.iloc[inx]['Use Mix Max Load Qty']
                    if num_sum_fr + num_fr <= num_basis_max_fr:
                        int_cntr_seq += 1
                        num_sum_fr += num_fr
                    else:
                        int_cntr_block += 1
                        int_cntr_seq = 1
                        num_sum_fr = num_fr

                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Planned Flag')] = True
                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Initial Qty')] = (
                        df_not_planned.iloc)[inx]['Adj Min Qty']
                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Assigned Qty')] = (
                        df_not_planned.iloc)[inx]['Adj Min Qty']
                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Unassigned Qty')] = (
                            df_not_planned.iloc[inx]['Mixed Rest Qty'] - df_not_planned.iloc[inx]['Adj Min Qty'])
                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Adj Mixed Rest Qty')] = 0
                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('Loaded FR')] = num_fr
                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('cntr_block')] = int_cntr_block
                    df_not_planned.iloc[inx, df_not_planned.columns.get_loc('cntr_seq')] = int_cntr_seq

        df_return = pd.concat([df_planned_ftl, df_planned_ltl, df_not_planned], ignore_index=True)

    return df_return


@_decoration_
def fn_cntr_plan_inter_process(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Last Mix 기준으로 LTL 컨테이터 추가 할당 로직 수행
    1. Last Mix 이후 LTL 및 컨테이너 미할당 아이템을 대상으로 로직 수행
    2. 기 할당된 컨테이너를 기준으로 작업 진행
    3. 미할당 아이텡의 경우 먼저 기 할당된 컨테이너에 추가 하여 Max F/R을 넘지 않는 범위라면 해당 컨테이너에 할당
    4. 미할당 아이템을 기 할당된 LTL 컨테이너 중 할당가능한 컨테이너가 없는 경우 새로운 컨테이너로 할당
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

    # Single Item 처리된 행을 분리
    list_where_no_group = df_p_source['Last Mix Group'].isna()
    # Single Item
    df_no_target = df_p_source[list_where_no_group].copy(deep=True)
    # Mixed Item
    df_target = df_p_source[~list_where_no_group].copy(deep=True)

    # 마지막 Mix Group 별로 처리
    # Last Mix 이후 LTL 및 컨테이너 할당 안 된 전체를 모아 로직 수행
    if not df_target.empty and len(df_target) > 0:
        df_target = (df_target.groupby(by=['Last Mix Group'], group_keys=True)
                     .apply(lambda group: fn_cntr_plan_inter_process_detail(group)))

    df_return = pd.concat([df_target, df_no_target], ignore_index=True)

    return df_return


def fn_adjust_by_max_profit(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Option2: Max Profit인 경우의 adjust 처리
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

    num_sum_fr = df_return['Loaded FR'].sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']
    max_profit_priority = df_return['Profit Grade Priority'].min()
    flag_ftl = False
    str_status = 'LTL'
    df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
    df_return['Adjust Item FR'] = df_return['Loaded FR']
    flag_break = False
    while not flag_break:
        for inx in range(len(df_return)):
            if df_return.iloc[inx]['Profit Grade Priority'] == max_profit_priority:
                flag_add = False
                num_fr = df_return.iloc[inx]['Multiple'] / df_return.iloc[inx]['Use Mix Max Load Qty']
                int_add_cnt = (
                    np.where(df_return.iloc[inx]['Adjust Add Cnt'] == np.nan, 1, df_return.iloc[inx]['Adjust Add Cnt'] + 1))
                if num_sum_fr + num_fr > num_max_fr:
                    flag_break = True
                    if num_sum_fr >= num_min_fr:
                        flag_ftl = True
                    else:
                        flag_ftl = False
                else:
                    flag_add = True

                if flag_add:
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Add Cnt')] = int_add_cnt
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Assigned Qty')] = (
                            df_return.iloc[inx]['Assigned Qty'] + (int_add_cnt * df_return.iloc[inx]['Multiple']))
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Item FR')] = (
                            df_return.iloc[inx]['Adjust Assigned Qty'] / df_return.iloc[inx]['Use Mix Max Load Qty'])
                    num_sum_fr = df_return['Adjust Item FR'].sum()
                    df_return['Adjust Sum FR'] = num_sum_fr

                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

                if flag_break:
                    break

    df_return['Mixed Item Cntr Status'] = str_status
    df_return['Loading Qty Per Cntr'] = (
        np.where(df_return['Adjust Assigned Qty'].isna(),
                 df_return['Assigned Qty'], df_return['Adjust Assigned Qty']))
    df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']

    return df_return


def fn_adjust_by_max_profit_with_option1(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Option2: Max Profit인 경우의 adjust 처리
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

    if "202605_P410_L40PWD28_-_DIR_D_42GP_SIDE_N" == df_p_source["Last Mix Group"].iloc[0]:
        print("DEBUG")

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # FTL 판별용 변수 모음 Dictionary
    dic_ftl_vars = {
        # 최상위 Profit Grade
        "MAX_PROFIT_GRADE_PRIORITY": df_return['Profit Grade Priority'].min(),
        # 조정 로직으로 ADD한 횟수(아이템의 Multiple을 기준으로 ADD한 횟수를 의미한다)
        "ADD_CNT": 0,
        # 현재 Cntr에 적재된 아이템의 FR의 합
        "SUM_FR": df_return['Loaded FR'].sum(),
        # 현재 Cntr에 적재된 각 아이템의 Multiple 적재 시의 FR
        "MULTIPLE_FR": 0,
        # 다음 대상 아이템의 Multiple 적재 시의 FR
        "MULTIPLE_FR_NEXT": 0,
        # MAX FR 기준
        "BASIS_MAX_FR": df_return.iloc[0]['Mix Max FR'],
        # MIN FR 기준
        "BASIS_MIN_FR": df_return.iloc[0]['Mix Min FR'],
        # 아이템 적재 상태 문구
        "STATUS": "LTL",
        # FTL 여부
        "FLAG_FTL": False,
        # 아이템 적재 여부 플래그
        "FLAG_ADD": False,
        # 전체 루프에 대한 break 여부 플래그
        "FLAG_BREAK": False,
    }

    # 조정 시에 사용할 적재량
    df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
    # 조정된 아이템별 적재 비율
    df_return['Adjust Item FR'] = df_return['Loaded FR']
    # 전체 루프: FTL이 되거나 더이상 루프를 수행할 수 없는 경우에 루프를 종료한다.
    while not dic_ftl_vars["FLAG_BREAK"]:
        # 아이템별 루프: 전달된 Cntr 내에 포함된 아이템 전체에 대한 루프
        for inx in range(len(df_return)):
            # Max Profit의 경우 최상위 Profit Grade를 가진 아이템 적재 대상으로 한다.
            if df_return.iloc[inx]['Profit Grade Priority'] == dic_ftl_vars["MAX_PROFIT_GRADE_PRIORITY"]:
                # 적재 여부를 False로 초기화한다.
                dic_ftl_vars["FLAG_ADD"] = False
                # 현재 아이템에 대해 Multiple만큼 적재했을 때의 FR
                dic_ftl_vars["MULTIPLE_FR"] = df_return.iloc[inx]['Multiple'] / df_return.iloc[inx]['Use Mix Max Load Qty']
                dic_ftl_vars["ADD_CNT"] = (
                    np.where(df_return.iloc[inx]['Adjust Add Cnt'] == np.nan, 1,
                             df_return.iloc[inx]['Adjust Add Cnt'] + 1))
                if dic_ftl_vars["SUM_FR"] + dic_ftl_vars["MULTIPLE_FR"] < dic_ftl_vars["BASIS_MIN_FR"]:
                    dic_ftl_vars["FLAG_ADD"] = True
                elif dic_ftl_vars["SUM_FR"] + dic_ftl_vars["MULTIPLE_FR"] > dic_ftl_vars["BASIS_MAX_FR"]:
                    dic_ftl_vars["FLAG_BREAK"] = True
                    break
                else:
                    dic_ftl_vars["FLAG_ADD"] = True
                    dic_ftl_vars["FLAG_FTL"] = True
                    dic_ftl_vars["FLAG_BREAK"] = True
                    if Param_Adjust_Option1 == "MAX":
                        for inx2 in range(inx+1, len(df_return)):
                            if df_return.iloc[inx2]['Profit Grade Priority'] == dic_ftl_vars["MAX_PROFIT_GRADE_PRIORITY"]:
                                # 다음 대상 아이템에 대해 Multiple만큼 적재했을 때의 FR
                                dic_ftl_vars["MULTIPLE_FR_NEXT"] = df_return.iloc[inx2]['Multiple'] / df_return.iloc[inx2]['Use Mix Max Load Qty']
                                if dic_ftl_vars["SUM_FR"] + dic_ftl_vars["MULTIPLE_FR"] + dic_ftl_vars["MULTIPLE_FR_NEXT"] <= dic_ftl_vars["BASIS_MAX_FR"]:
                                    dic_ftl_vars["FLAG_FTL"] = False
                                    dic_ftl_vars["FLAG_BREAK"] = False
                                break

                if dic_ftl_vars["FLAG_ADD"]:
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Add Cnt')] = dic_ftl_vars["ADD_CNT"]
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Assigned Qty')] = (
                            df_return.iloc[inx]['Assigned Qty'] + (
                                dic_ftl_vars["ADD_CNT"] * df_return.iloc[inx]['Multiple']))
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Item FR')] = (
                            df_return.iloc[inx]['Adjust Assigned Qty'] / df_return.iloc[inx]['Use Mix Max Load Qty'])
                    dic_ftl_vars["SUM_FR"] = df_return['Adjust Item FR'].sum()
                    df_return['Adjust Sum FR'] = dic_ftl_vars["SUM_FR"]
                if dic_ftl_vars["FLAG_FTL"]:
                    dic_ftl_vars["STATUS"] = "Adjust FTL"
                    break

    df_return['Mixed Item Cntr Status'] = dic_ftl_vars["STATUS"]
    df_return['Loading Qty Per Cntr'] = (
        np.where(df_return['Adjust Assigned Qty'].isna(),
                 df_return['Assigned Qty'], df_return['Adjust Assigned Qty']))
    df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']

    return df_return


def fn_adjust_by_min_item_change(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Option2: Min Item Change에 대한 adjust
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

    # 데이터 수정 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    num_sum_fr = df_return['Loaded FR'].sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']

    str_status = 'LTL'
    if num_min_fr <= num_sum_fr:
        str_status = 'Adjust FTL'
    else:
        df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
        df_return['Adjust Item FR'] = df_return['Loaded FR']
        flag_ftl = False
        flag_break = False
        while not flag_break:
            for inx in range(len(df_return)):
                flag_add = False
                num_fr = df_return.iloc[inx]['Multiple'] / df_return.iloc[inx]['Use Mix Max Load Qty']
                int_add_cnt = (
                    np.where(df_return.iloc[inx]['Adjust Add Cnt'] == np.nan, 1, df_return.iloc[inx]['Adjust Add Cnt'] + 1))
                if num_sum_fr + num_fr < num_min_fr:
                    flag_add = True
                elif num_sum_fr + num_fr > num_max_fr:
                    flag_break = True
                    break
                else:
                    flag_add = True
                    flag_ftl = True

                if flag_add:
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Add Cnt')] = int_add_cnt
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Assigned Qty')] = (
                            df_return.iloc[inx]['Assigned Qty'] + (int_add_cnt * df_return.iloc[inx]['Multiple']))
                    df_return.iloc[inx, df_return.columns.get_loc('Adjust Item FR')] = (
                            df_return.iloc[inx]['Adjust Assigned Qty'] / df_return.iloc[inx]['Use Mix Max Load Qty'])
                    num_sum_fr = df_return['Adjust Item FR'].sum()
                    df_return['Adjust Sum FR'] = num_sum_fr
                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

    df_return['Mixed Item Cntr Status'] = str_status
    df_return['Loading Qty Per Cntr'] = (
        np.where(df_return['Adjust Assigned Qty'].isna(),
                 df_return['Assigned Qty'], df_return['Adjust Assigned Qty']))
    df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']

    return df_return


def fn_adjust_by_min_item_change_with_option1(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Option2: Min Item Change에 대한 adjust
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

    # 데이터 수정 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    # FTL 판별용 변수 모음 Dictionary
    dic_ftl_vars = {
        # 조정 로직으로 ADD한 횟수(아이템의 Multiple을 기준으로 ADD한 횟수를 의미한다)
        "ADD_CNT": 0,
        # 현재 Cntr에 적재된 아이템의 FR의 합
        "SUM_FR": df_return['Loaded FR'].sum(),
        # 현재 Cntr에 적재된 각 아이템의 Multiple 적재 시의 FR
        "MULTIPLE_FR": 0,
        # 다음 대상 아이템의 Multiple 적재 시의 FR
        "MULTIPLE_FR_NEXT": 0,
        # MAX FR 기준
        "BASIS_MAX_FR": df_return.iloc[0]['Mix Max FR'],
        # MIN FR 기준
        "BASIS_MIN_FR": df_return.iloc[0]['Mix Min FR'],
        # 아이템 적재 상태 문구
        "STATUS": "LTL",
        # FTL 여부
        "FLAG_FTL": False,
        # 아이템 적재 여부 플래그
        "FLAG_ADD": False,
        # 전체 루프에 대한 break 여부 플래그
        "FLAG_BREAK": False,
    }

    # 조정 시에 사용할 적재량
    df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
    # 조정된 아이템별 적재 비율
    df_return['Adjust Item FR'] = df_return['Loaded FR']
    # 전체 루프: FTL이 되거나 더이상 루프를 수행할 수 없는 경우에 루프를 종료한다.
    while not dic_ftl_vars["FLAG_BREAK"]:
        # 아이템별 루프: 전달된 Cntr 내에 포함된 아이템 전체에 대한 루프
        for inx in range(len(df_return)):
            # 적재 여부를 False로 초기화한다.
            dic_ftl_vars["FLAG_ADD"] = False
            # 현재 아이템에 대해 Multiple만큼 적재했을 때의 FR
            dic_ftl_vars["MULTIPLE_FR"] = df_return.iloc[inx]['Multiple'] / df_return.iloc[inx]['Use Mix Max Load Qty']
            dic_ftl_vars["ADD_CNT"] = (
                np.where(df_return.iloc[inx]['Adjust Add Cnt'] == np.nan, 1,
                         df_return.iloc[inx]['Adjust Add Cnt'] + 1))
            if dic_ftl_vars["SUM_FR"] + dic_ftl_vars["MULTIPLE_FR"] < dic_ftl_vars["BASIS_MIN_FR"]:
                dic_ftl_vars["FLAG_ADD"] = True
            elif dic_ftl_vars["SUM_FR"] + dic_ftl_vars["MULTIPLE_FR"] > dic_ftl_vars["BASIS_MAX_FR"]:
                dic_ftl_vars["FLAG_BREAK"] = True
                break
            else:
                dic_ftl_vars["FLAG_ADD"] = True
                dic_ftl_vars["FLAG_FTL"] = True
                dic_ftl_vars["FLAG_BREAK"] = True
                if Param_Adjust_Option1 == "MAX":
                    inx2 = inx + 1
                    if inx2 < len(df_return):
                        # 다음 대상 아이템에 대해 Multiple만큼 적재했을 때의 FR
                        dic_ftl_vars["MULTIPLE_FR_NEXT"] = df_return.iloc[inx2]['Multiple'] / df_return.iloc[inx2]['Use Mix Max Load Qty']
                        if dic_ftl_vars["SUM_FR"] + dic_ftl_vars["MULTIPLE_FR"] + dic_ftl_vars["MULTIPLE_FR_NEXT"] <= dic_ftl_vars["BASIS_MAX_FR"]:
                            dic_ftl_vars["FLAG_FTL"] = False
                            dic_ftl_vars["FLAG_BREAK"] = False

            if dic_ftl_vars["FLAG_ADD"]:
                df_return.iloc[inx, df_return.columns.get_loc('Adjust Add Cnt')] = dic_ftl_vars["ADD_CNT"]
                df_return.iloc[inx, df_return.columns.get_loc('Adjust Assigned Qty')] = (
                        df_return.iloc[inx]['Assigned Qty'] + (
                        dic_ftl_vars["ADD_CNT"] * df_return.iloc[inx]['Multiple']))
                df_return.iloc[inx, df_return.columns.get_loc('Adjust Item FR')] = (
                        df_return.iloc[inx]['Adjust Assigned Qty'] / df_return.iloc[inx]['Use Mix Max Load Qty'])
                dic_ftl_vars["SUM_FR"] = df_return['Adjust Item FR'].sum()
                df_return['Adjust Sum FR'] = dic_ftl_vars["SUM_FR"]
            if dic_ftl_vars["FLAG_FTL"]:
                dic_ftl_vars["STATUS"] = "Adjust FTL"
                break

    df_return['Mixed Item Cntr Status'] = dic_ftl_vars["STATUS"]
    df_return['Loading Qty Per Cntr'] = (
        np.where(df_return['Adjust Assigned Qty'].isna(),
                 df_return['Assigned Qty'], df_return['Adjust Assigned Qty']))
    df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']

    return df_return


def fn_adjust_by_indir_profit_demand(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    창고향의 ADD 로직 처리
     1. Profit Grade 높은 Item A 부터 Demand 한도 내 FTL 만족 시 까지 증량
        ( ITEM별 DMD ETA 4Week Sum Qty 한도 내 에서 증량 )
        모든 한도 증량 FTL 편성 실패 시 다음 아이템 선정 및 증량
     2. Profit Grade 동일한 경우 각 Item 별 Multiple 배수 만큼 순차적 증감
     3. 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시 P/G 제일 높은 아이템 기준
        Multiple 고려하여 증량 (Demand는 고려 안함)
        (Multiple 기준 증량 시 FTL 초과 하는 경우 해당 증량 취소 후 다음 아이템 기준 증량 ,
        Profit Grade 가 동일한 리스트가 있다면  Multiple 고려 순차적 증가

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

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    num_sum_fr = df_return['Loaded FR'].sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']
    flag_ftl = False
    str_status = 'LTL'

    # 마지막 그룹 찾기
    df_return['group no'] = df_return.groupby('Profit Grade Priority').ngroup()
    group_no = 0
    # 마지막 그룹
    df_return.loc[df_return['group no'] == df_return['group no'].max(), 'group tot last'] = 1

    # Ajust Assinged Qty, Adjust Item FR 초기값
    df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
    df_return['Adjust Item FR'] = df_return['Loaded FR']

    # Demand 가능 여부 flag (True: 불가능)
    df_return['demand yn'] = False
    list_where = df_return['Multiple'] > df_return['DMD ETA 4Week Sum Qty']
    df_return.loc[list_where, 'demand yn'] = True

    # flag_break(ftl/ltl로 최종 결정되어 나올때 flag), flag_demand(demand 불가능 flag),
    #  overLtl yn(load 불가능 flag: 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우)
    flag_break = False
    flag_demand = False
    df_return['overLtl yn'] = False

    # Demand 가능 여부가 모두 안되면 return
    if list_where.all():
        return fn_adjust_make_status(df_return, str_status)

    # itertuples용 index
    loc_multiple = df_return.columns.get_loc('Multiple') + 1
    loc_demand_qty = df_return.columns.get_loc('DMD ETA 4Week Sum Qty') + 1
    loc_max_load_qty = df_return.columns.get_loc('Use Mix Max Load Qty') + 1
    loc_group_tot_last = df_return.columns.get_loc('group tot last') + 1
    loc_overLtl_yn = df_return.columns.get_loc('overLtl yn') + 1

    while not flag_break:
        # 동일한 Profit Grade끼리 수행
        for row in df_return[df_return['group no'] == group_no].itertuples():
            # inx 설정
            inx = row.Index
            flag_add = False

            ############################################################################################################
            # 1) ~ 4) case의 경우 continue와 break 작업 수행
            # ▶ demand yn = True : Multiple > demand Qty
            # ▶ overLtl yn = True : 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우
            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우 (demand yn ==  True 또는 overLtl yn == True)
            # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
            # 3) group no 이동 case1 :  마지막 그룹이 아니고 + 해당 그룹이 더이상 ftl 되지 않는 경우
            # 4) group no 이동 case2 :  마지막 그룹이 아니고 + 해당 그룹이 demand qty 불가능(Multiple > demand Qty)
            ############################################################################################################

            # Demand Qty 가능여부 체크
            if row[loc_multiple] > row[loc_demand_qty]:
                df_return.loc[inx, 'demand yn'] = True
                # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
                if df_return['demand yn'].all():
                    flag_demand = True
                # 4) group no 이동 case2 : 마지막 그룹이 아니고 + 해당그룹이 demand Qty 불가능(Multiple > demand Qty)
                elif (
                        np.isnan(row[loc_group_tot_last])
                        and (df_return[df_return['group no'] == group_no]['demand yn'].all())):
                    group_no += 1
                    continue
                else:
                    continue

            num_fr = row[loc_multiple] / row[loc_max_load_qty]
            int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                    df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                           )
            if flag_demand:
                flag_break = True
                if num_sum_fr >= num_min_fr:
                    flag_ftl = True
                else:
                    break
            elif num_sum_fr + num_fr > num_max_fr:
                if num_sum_fr >= num_min_fr:
                    flag_break = True
                    flag_ftl = True
                else:
                    flag_ftl = False
                    # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                    df_return.loc[inx, 'overLtl yn'] = True
            else:
                flag_add = True

            if flag_add:
                df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                df_return.loc[inx, 'Adjust Assigned Qty'] = (
                        df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                )
                df_return.loc[inx, 'Adjust Item FR'] = (
                        df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                )
                num_sum_fr = df_return['Adjust Item FR'].sum()
                df_return['Adjust Sum FR'] = num_sum_fr
                # DMD 4Week Sum Qty 재계산
                df_return.loc[inx, 'DMD ETA 4Week Sum Qty'] -= df_return.loc[inx, 'Multiple']

            if flag_ftl:
                str_status = 'Adjust FTL'
                break

            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우
            if (df_return['demand yn'] | df_return['overLtl yn']).all():
                flag_break = True
                break
            # 3) group no 이동 case1 : 마지막 그룹이 아니고 + 해당 그룹이 더이상 ftl 되지 않는 경우
            elif (
                    np.isnan(row[loc_group_tot_last])
                    and (df_return[df_return['group no'] == group_no]['demand yn']
                         | df_return[df_return['group no'] == group_no]['overLtl yn']).all()):
                group_no += 1

    # 최종 status, qty정리
    df_return = fn_adjust_make_status(df_return, str_status)

    # ftl이거나 demand 고려하지 않고도 ftl이 되지 않을 때(하나를 추가하면 max를 넘고,추가 하지 않으면 min을 못넘는 경우)
    if flag_ftl or df_return['overLtl yn'].all():
        return df_return
    # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패시
    else:
        # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시 P/G 제일 높은 아이템 기준
        # Multiple 고려하여 증량 (Demand는 고려 안함)
        # Multiple 기준 증량 시 FTL 초과 하는 경우 해당 증량 취소 후 다음 아이템 기준 증량 ,
        # Profit Grade 가 동일한 리스트가 있다면  Multiple 고려 순차적 증가
        # flag_break, group_no 초기화
        flag_break = False
        group_no = 0

        while not flag_break:
            # 동일한 Profit Grade끼리 수행
            for row in df_return[df_return['group no'] == group_no].itertuples():
                # inx 설정
                inx = row.Index
                flag_add = False

                num_fr = row[loc_multiple] / row[loc_max_load_qty]
                int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                        df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                               )
                if num_sum_fr + num_fr > num_max_fr:
                    if num_sum_fr >= num_min_fr:
                        flag_break = True
                        flag_ftl = True
                    else:
                        flag_ftl = False
                        # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                        df_return.loc[inx, 'overLtl yn'] = True
                else:
                    flag_add = True

                if flag_add:
                    df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                    df_return.loc[inx, 'Adjust Assigned Qty'] = (
                            df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                    )
                    df_return.loc[inx, 'Adjust Item FR'] = (
                            df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                    )
                    num_sum_fr = df_return['Adjust Item FR'].sum()
                    df_return['Adjust Sum FR'] = num_sum_fr

                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

                # 전체가 더이상 ftl 되지 않는 경우
                if df_return['overLtl yn'].all():
                    flag_break = True
                    break
                # group no 이동 : 마지막 그룹이 아니고 + 해당그룹이 더이상 ftl 되지 않는 경우
                elif (
                        np.isnan(row[loc_group_tot_last])
                        and (df_return[df_return['group no'] == group_no]['overLtl yn']).all()):
                    group_no += 1

        # 최종 status, qty정리
        df_return = fn_adjust_make_status(df_return, str_status)

        return df_return


def fn_adjust_make_status(df_p_source:pd.DataFrame, str_status:str) -> pd.DataFrame:
    """
        adjust 최종 칼럼 반영 ( Mixed Item Cntr Status, Loading Qty Per Cntr, Last Loading Qty )
    :param df_p_source:
    :param str_status:
    :return:
    """
    df_p_source['Mixed Item Cntr Status'] = str_status
    df_p_source['Loading Qty Per Cntr'] = (
        np.where(df_p_source['Adjust Assigned Qty'].isna(),
                 df_p_source['Assigned Qty'], df_p_source['Adjust Assigned Qty']))
    df_p_source['Last Loading Qty'] = df_p_source['Loading Qty Per Cntr']

    return df_p_source


def fn_adjust_by_indir_min_item_change(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    창고향의 ADD 로직 처리
     1. Profit Grade 높은 Item 부터 Demand 한도 내 FTL 만족 시 까지 순차적으로 증량
        ( ITEM별 DMD ETA 4Week Sum Qty 한도 내 에서 증량 )
     3. 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시 순차적으로
        Multiple 고려하여 증량 (Demand는 고려 안함)
        (Multiple 기준 증량 시 FTL 초과 하는 경우 해당 증량 취소 후 다음 아이템 기준 증량 )

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

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    num_sum_fr = df_return['Loaded FR'].sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']
    flag_ftl = False
    str_status = 'LTL'

    # Ajust Assinged Qty, Adjust Item FR 초기값
    df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
    df_return['Adjust Item FR'] = df_return['Loaded FR']

    # Demand 가능 여부 flag (True: 불가능)
    df_return['demand yn'] = False
    list_where = df_return['Multiple'] > df_return['DMD ETA 4Week Sum Qty']
    df_return.loc[list_where, 'demand yn'] = True

    # flag_break(ftl/ltl로 최종 결정되어 나올때 flag), flag_demand(demand 불가능 flag),
    #  overLtl yn(load 불가능 flag: 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우)
    flag_break = False
    flag_demand = False
    df_return['overLtl yn'] = False

    # itertuples용 index
    loc_multiple = df_return.columns.get_loc('Multiple') + 1
    loc_demand_qty = df_return.columns.get_loc('DMD ETA 4Week Sum Qty') + 1
    loc_max_load_qty = df_return.columns.get_loc('Use Mix Max Load Qty') + 1
    loc_overLtl_yn = df_return.columns.get_loc('overLtl yn') + 1

    # Demand 가능 여부가 모두 안되면 return
    if list_where.all():
        return fn_adjust_make_status(df_return, str_status)

    while not flag_break:
        # Profit Grade 순서대로 순차적으로만 실행
        for row in df_return.itertuples():
            # inx 설정
            inx = row.Index
            flag_add = False

            ############################################################################################################
            # 1) ~ 2) case의 경우 continue와 break 작업 수행
            # ▶ demand yn = True : Multiple > demand Qty
            # ▶ overLtl yn = True : 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우
            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우 (demand yn ==  True 또는 overLtl yn == True)
            # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
            ############################################################################################################

            # Demand Qty 가능여부 체크
            if row[loc_multiple] > row[loc_demand_qty]:
                df_return.loc[inx, 'demand yn'] = True
                # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
                if df_return['demand yn'].all():
                    flag_demand = True
                else:
                    continue

            num_fr = row[loc_multiple] / row[loc_max_load_qty]
            int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                    df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                           )
            # MAX 판별기준
            if flag_demand:
                flag_break = True
                if num_sum_fr >= num_min_fr:
                    flag_ftl = True
                else:
                    break
            elif num_sum_fr + num_fr > num_max_fr:
                if num_sum_fr >= num_min_fr:
                    flag_break = True
                    flag_ftl = True
                else:
                    flag_ftl = False
                    # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                    df_return.loc[inx, 'overLtl yn'] = True
            else:
                flag_add = True

            if flag_add:
                df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                df_return.loc[inx, 'Adjust Assigned Qty'] = (
                        df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                )
                df_return.loc[inx, 'Adjust Item FR'] = (
                        df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                )
                num_sum_fr = df_return['Adjust Item FR'].sum()
                df_return['Adjust Sum FR'] = num_sum_fr
                # DMD 4Week Sum Qty 재계산
                df_return.loc[inx, 'DMD ETA 4Week Sum Qty'] -= df_return.loc[inx, 'Multiple']

            if flag_ftl:
                str_status = 'Adjust FTL'
                break

            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우
            if (df_return['demand yn'] | df_return['overLtl yn']).all():
                flag_break = True
                break

    # 최종 status, qty정리
    df_return = fn_adjust_make_status(df_return, str_status)

    # ftl이거나 demand 고려하지 않고도 ftl이 되지 않을 때(하나를 추가하면 max를 넘고,추가 하지 않으면 min을 못넘는 경우)
    if flag_ftl or df_return['overLtl yn'].all():
        return df_return
    # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패시
    else:
        # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시
        # flag_break, group_no 초기화
        flag_break = False
        group_no = 0

        while not flag_break:
            # Profit Grade 순서대로 순차적으로 실행
            for row in df_return.itertuples():
                # inx 설정
                inx = row.Index
                flag_add = False

                num_fr = row[loc_multiple] / row[loc_max_load_qty]
                int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                        df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                               )
                # MAX 판별기준
                if num_sum_fr + num_fr > num_max_fr:
                    if num_sum_fr >= num_min_fr:
                        flag_break = True
                        flag_ftl = True
                    else:
                        flag_ftl = False
                        # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                        df_return.loc[inx, 'overLtl yn'] = True
                else:
                    flag_add = True

                if flag_add:
                    df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                    df_return.loc[inx, 'Adjust Assigned Qty'] = (
                            df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                    )
                    df_return.loc[inx, 'Adjust Item FR'] = (
                            df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                    )
                    num_sum_fr = df_return['Adjust Item FR'].sum()
                    df_return['Adjust Sum FR'] = num_sum_fr

                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

                # 전체가 더이상 ftl 되지 않는 경우
                if df_return['overLtl yn'].all():
                    flag_break = True
                    break

        # 최종 status, qty정리
        df_return = fn_adjust_make_status(df_return, str_status)

        return df_return


def fn_adjust_by_indir_profit_demand_with_option1(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    창고향의 ADD 로직 처리
     1. Profit Grade 높은 Item A 부터 Demand 한도 내 FTL 만족 시 까지 증량
        ( ITEM별 DMD ETA 4Week Sum Qty 한도 내 에서 증량 )
        모든 한도 증량 FTL 편성 실패 시 다음 아이템 선정 및 증량
     2. Profit Grade 동일한 경우 각 Item 별 Multiple 배수 만큼 순차적 증감
     3. 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시 P/G 제일 높은 아이템 기준
        Multiple 고려하여 증량 (Demand는 고려 안함)
        (Multiple 기준 증량 시 FTL 초과 하는 경우 해당 증량 취소 후 다음 아이템 기준 증량 ,
        Profit Grade 가 동일한 리스트가 있다면  Multiple 고려 순차적 증가

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

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    num_sum_fr = df_return['Loaded FR'].sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']
    flag_ftl = False
    str_status = 'LTL'

    # 마지막 그룹 찾기
    df_return['group no'] = df_return.groupby('Profit Grade Priority').ngroup()
    group_no = 0
    # 마지막 그룹
    df_return.loc[df_return['group no'] == df_return['group no'].max(), 'group tot last'] = 1

    # Ajust Assinged Qty, Adjust Item FR 초기값
    df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
    df_return['Adjust Item FR'] = df_return['Loaded FR']

    # Demand 가능 여부 flag (True: 불가능)
    df_return['demand yn'] = False
    list_where = df_return['Multiple'] > df_return['DMD ETA 4Week Sum Qty']
    df_return.loc[list_where, 'demand yn'] = True

    # Option1 처리를 위한 flag처리
    df_return['ftl_flag'] = False

    # flag_break(ftl/ltl로 최종 결정되어 나올때 flag), flag_demand(demand 불가능 flag),
    #  overLtl yn(load 불가능 flag: 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우)
    flag_break = False
    flag_demand = False
    df_return['overLtl yn'] = False

    # itertuples용 index
    loc_multiple = df_return.columns.get_loc('Multiple') + 1
    loc_demand_qty = df_return.columns.get_loc('DMD ETA 4Week Sum Qty') + 1
    loc_max_load_qty = df_return.columns.get_loc('Use Mix Max Load Qty') + 1
    loc_group_tot_last = df_return.columns.get_loc('group tot last') + 1
    loc_overLtl_yn = df_return.columns.get_loc('overLtl yn') + 1

    while not flag_break:
        # 동일한 Profit Grade끼리 수행
        for row in df_return[df_return['group no'] == group_no].itertuples():
            # inx 설정
            inx = row.Index
            flag_add = False

            ############################################################################################################
            # 1) ~ 4) case의 경우 continue와 break 작업 수행
            # ▶ demand yn = True : Multiple > demand Qty
            # ▶ overLtl yn = True : 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우
            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우 (demand yn ==  True 또는 overLtl yn == True)
            # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
            # 3) group no 이동 case1 :  마지막 그룹이 아니고 + 해당 그룹이 더이상 ftl 되지 않는 경우
            # 4) group no 이동 case2 :  마지막 그룹이 아니고 + 해당 그룹이 demand qty 불가능(Multiple > demand Qty)
            ############################################################################################################

            # Demand Qty 가능여부 체크
            if row[loc_multiple] > row[loc_demand_qty]:
                df_return.loc[inx, 'demand yn'] = True
                # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
                if df_return['demand yn'].all():
                    flag_demand = True
                # 4) group no 이동 case2 : 마지막 그룹이 아니고 + 해당그룹이 demand Qty 불가능(Multiple > demand Qty)
                elif (
                        np.isnan(row[loc_group_tot_last])
                        and (df_return[df_return['group no'] == group_no]['demand yn'].all())
                ):
                    if num_min_fr <= num_sum_fr <= num_max_fr: # FTL 판별
                        flag_break = True
                        flag_ftl = True
                    else:
                        group_no += 1
                        continue
                else:
                    continue

            num_fr = row[loc_multiple] / row[loc_max_load_qty]
            int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                    df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                           )
            # Option1 별로 FTL 판별
            if flag_demand:
                flag_break = True
                if num_min_fr <= num_sum_fr <= num_max_fr:
                    flag_ftl = True
                else:
                    break
            elif Param_Adjust_Option1 == 'MAX':
                if num_sum_fr == num_max_fr:  # max면 ftl로 종료
                    flag_break = True
                    flag_ftl = True
                elif num_sum_fr + num_fr > num_max_fr:
                    if num_sum_fr < num_min_fr:
                        flag_ftl = False
                        # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                        df_return.loc[inx, 'overLtl yn'] = True
                    else:  # FTL
                        # Max에 가까운 값을 찾자
                        # 돌면서 ftl일 경우 해당 row의  ftl_flag 처리
                        df_return.loc[inx, 'ftl_flag'] = True
                        # 종료시점 : 현재 group_no 안에서
                        # overLtl yn이 False이고(ftl불가능건이 아닌 건들) demand yn이 False(디멘드 부족이 아닌건)에 한하여
                        # ( ftl 가능 대상 ) ftl_flag가 모두 True일때 (모두 순회) 그 시점에 ftl로 나오기
                        list_where = (
                                  (df_return['group no'] == group_no)
                                & (df_return['overLtl yn'] == False)
                                & (df_return['demand yn'] == False)
                        )
                        if (len(df_return[list_where]) > 0) and (df_return.loc[list_where, 'ftl_flag']).all():
                            flag_break = True
                            flag_ftl = True
                else:
                    flag_add = True
            elif Param_Adjust_Option1 == 'MIN':
                if num_min_fr <= num_sum_fr <= num_max_fr:
                    flag_break = True
                    flag_ftl = True
                elif num_sum_fr + num_fr > num_max_fr:
                    if num_sum_fr < num_min_fr:
                        # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                        df_return.loc[inx, 'overLtl yn'] = True
                else:
                    flag_add = True

            if flag_add:
                df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                df_return.loc[inx, 'Adjust Assigned Qty'] = (
                        df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                )
                df_return.loc[inx, 'Adjust Item FR'] = (
                        df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                )
                num_sum_fr = df_return['Adjust Item FR'].sum()
                df_return['Adjust Sum FR'] = num_sum_fr
                # DMD 4Week Sum Qty 재계산
                df_return.loc[inx, 'DMD ETA 4Week Sum Qty'] -= df_return.loc[inx, 'Multiple']

            if flag_ftl:
                str_status = 'Adjust FTL'
                break

            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우
            if (df_return['demand yn'] | df_return['overLtl yn']).all():
                flag_break = True
                break
            # 3) group no 이동 case1 : 마지막 그룹이 아니고 + 해당 그룹이 더이상 ftl 되지 않는 경우
            elif (
                    np.isnan(row[loc_group_tot_last])
                    and (df_return[df_return['group no'] == group_no]['demand yn']
                         | df_return[df_return['group no'] == group_no]['overLtl yn']).all()
            ):
                if num_min_fr <= num_sum_fr <= num_max_fr:  # FTL 판별
                    flag_break = True
                    flag_ftl = True
                else:
                    group_no += 1

    # 최종 status, qty정리
    df_return = fn_adjust_make_status(df_return, str_status)

    # ftl이거나 demand 고려하지 않고도 ftl이 되지 않을 때(하나를 추가하면 max를 넘고,추가 하지 않으면 min을 못넘는 경우)
    if flag_ftl or df_return['overLtl yn'].all():
        return df_return
    # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패시
    else:
        # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시 P/G 제일 높은 아이템 기준
        # Multiple 고려하여 증량 (Demand는 고려 안함)
        # Multiple 기준 증량 시 FTL 초과 하는 경우 해당 증량 취소 후 다음 아이템 기준 증량 ,
        # Profit Grade 가 동일한 리스트가 있다면  Multiple 고려 순차적 증가
        # flag_break, group_no 초기화
        flag_break = False
        group_no = 0

        while not flag_break:
            # 동일한 Profit Grade끼리 수행
            for row in df_return[df_return['group no'] == group_no].itertuples():
                # inx 설정
                inx = row.Index
                flag_add = False

                num_fr = row[loc_multiple] / row[loc_max_load_qty]
                int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                        df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                               )
                # Option1 별로 FTL 판별
                if Param_Adjust_Option1 == 'MAX':
                    if num_sum_fr == num_max_fr:  # max면 ftl로 종료
                        flag_break = True
                        flag_ftl = True
                    elif num_sum_fr + num_fr > num_max_fr:
                        if num_sum_fr < num_min_fr:
                            flag_ftl = False
                            # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                            df_return.loc[inx, 'overLtl yn'] = True
                        else:  # FTL
                            # Max에 가까운 값을 찾자
                            # 돌면서 ftl일 경우 해당 row의  ftl_flag 처리
                            df_return.loc[inx, 'ftl_flag'] = True
                            # 종료시점 : 현재 group_no 안에서
                            # overLtl yn이 False이고(ftl불가능건이 아닌 건들)에 한하여
                            # ( ftl 가능 대상 ) ftl_flag가 모두 True일때 (모두 순회) 그 시점에 ftl로 나오기
                            list_where = (df_return['group no'] == group_no) & (df_return['overLtl yn'] == False)
                            if (len(df_return[list_where]) > 0) and (df_return.loc[list_where, 'ftl_flag']).all():
                                flag_break = True
                                flag_ftl = True
                    else:
                        flag_add = True
                elif Param_Adjust_Option1 == 'MIN':
                    if num_min_fr <= num_sum_fr <= num_max_fr:
                        flag_break = True
                        flag_ftl = True
                    elif num_sum_fr + num_fr > num_max_fr:
                        if num_sum_fr < num_min_fr:
                            flag_ftl = False
                            # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                            df_return.loc[inx, 'overLtl yn'] = True
                    else:
                        flag_add = True

                if flag_add:
                    df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                    df_return.loc[inx, 'Adjust Assigned Qty'] = (
                            df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                    )
                    df_return.loc[inx, 'Adjust Item FR'] = (
                            df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                    )
                    num_sum_fr = df_return['Adjust Item FR'].sum()
                    df_return['Adjust Sum FR'] = num_sum_fr

                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

                # 전체가 더이상 ftl 되지 않는 경우
                if df_return['overLtl yn'].all():
                    flag_break = True
                    break
                # group no 이동 : 마지막 그룹이 아니고 + 해당그룹이 더이상 ftl 되지 않는 경우
                elif (
                        np.isnan(row[loc_group_tot_last])
                        and (df_return[df_return['group no'] == group_no]['overLtl yn']).all()
                ):
                    if num_min_fr <= num_sum_fr <= num_max_fr: # FTL 판별
                        flag_break = True
                        flag_ftl = True
                    else:
                        group_no += 1

        # 최종 status, qty정리
        df_return = fn_adjust_make_status(df_return, str_status)

        return df_return


def fn_adjust_by_indir_min_item_change_with_option1(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    창고향의 ADD 로직 처리
     1. Profit Grade 높은 Item 부터 Demand 한도 내 FTL 만족 시 까지 순차적으로 증량
        ( ITEM별 DMD ETA 4Week Sum Qty 한도 내 에서 증량 )
     3. 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시 순차적으로
        Multiple 고려하여 증량 (Demand는 고려 안함)
        (Multiple 기준 증량 시 FTL 초과 하는 경우 해당 증량 취소 후 다음 아이템 기준 증량 )

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

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)

    num_sum_fr = df_return['Loaded FR'].sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']
    flag_ftl = False
    str_status = 'LTL'

    # Ajust Assinged Qty, Adjust Item FR 초기값
    df_return['Adjust Assigned Qty'] = df_return['Assigned Qty']
    df_return['Adjust Item FR'] = df_return['Loaded FR']

    # Demand 가능 여부 flag (True: 불가능)
    df_return['demand yn'] = False
    list_where = df_return['Multiple'] > df_return['DMD ETA 4Week Sum Qty']
    df_return.loc[list_where, 'demand yn'] = True

    # Option1 처리를 위한 flag처리
    df_return['ftl_flag'] = False

    # flag_break(ftl/ltl로 최종 결정되어 나올때 flag), flag_demand(demand 불가능 flag),
    #  overLtl yn(load 불가능 flag: 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우)
    flag_break = False
    flag_demand = False
    df_return['overLtl yn'] = False

    # itertuples용 index
    loc_multiple = df_return.columns.get_loc('Multiple') + 1
    loc_demand_qty = df_return.columns.get_loc('DMD ETA 4Week Sum Qty') + 1
    loc_max_load_qty = df_return.columns.get_loc('Use Mix Max Load Qty') + 1
    loc_overLtl_yn = df_return.columns.get_loc('overLtl yn') + 1

    while not flag_break:
        # Profit Grade 순서대로 순차적으로만 실행
        for row in df_return.itertuples():
            # inx 설정
            inx = row.Index
            flag_add = False

            ############################################################################################################
            # 1) ~ 2) case의 경우 continue와 break 작업 수행
            # ▶ demand yn = True : Multiple > demand Qty
            # ▶ overLtl yn = True : 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우
            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우 (demand yn ==  True 또는 overLtl yn == True)
            # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
            ############################################################################################################

            # Demand Qty 가능여부 체크
            if row[loc_multiple] > row[loc_demand_qty]:
                df_return.loc[inx, 'demand yn'] = True
                # 2) 불가능 case2 : 전체가 demand qty 불가능(Multiple > demand Qty)
                if df_return['demand yn'].all():
                    flag_demand = True
                else:
                    continue

            num_fr = row[loc_multiple] / row[loc_max_load_qty]
            int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                    df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                           )
            if flag_demand:
                flag_break = True
                if num_min_fr <= num_sum_fr <= num_max_fr:
                    flag_ftl = True
                else:
                    break
            # Option1 별로 FTL 판별
            elif Param_Adjust_Option1 == 'MAX':
                if num_sum_fr == num_max_fr:  # max면 ftl로 종료
                    flag_break = True
                    flag_ftl = True
                elif num_sum_fr + num_fr > num_max_fr:
                    if num_sum_fr < num_min_fr:
                        flag_ftl = False
                        # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                        df_return.loc[inx, 'overLtl yn'] = True
                    else:  # FTL
                        # Max에 가까운 값을 찾자
                        # 돌면서 ftl일 경우 해당 row의  ftl_flag 처리
                        df_return.loc[inx, 'ftl_flag'] = True
                        # 종료시점 : overLtl yn이 False이고(ftl불가능건이 아닌 건들) demand yn이 False(디멘드 부족이 아닌건)에 한하여
                        # ( ftl 가능 대상 ) ftl_flag가 모두 True일때 (모두 순회) 그 시점에 ftl로 나오기
                        list_where = (df_return['overLtl yn'] == False) & (df_return['demand yn'] == False)
                        if (len(df_return[list_where]) > 0) and (df_return.loc[list_where, 'ftl_flag']).all():
                            flag_break = True
                            flag_ftl = True
                else:
                    flag_add = True
            elif Param_Adjust_Option1 == 'MIN':
                if num_min_fr <= num_sum_fr <= num_max_fr:
                    flag_break = True
                    flag_ftl = True
                elif num_sum_fr + num_fr > num_max_fr:
                    if num_sum_fr < num_min_fr:
                        flag_ftl = False
                        # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                        df_return.loc[inx, 'overLtl yn'] = True
                else:
                    flag_add = True

            if flag_add:
                df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                df_return.loc[inx, 'Adjust Assigned Qty'] = (
                        df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                )
                df_return.loc[inx, 'Adjust Item FR'] = (
                        df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                )
                num_sum_fr = df_return['Adjust Item FR'].sum()
                df_return['Adjust Sum FR'] = num_sum_fr
                # DMD 4Week Sum Qty 재계산
                df_return.loc[inx, 'DMD ETA 4Week Sum Qty'] -= df_return.loc[inx, 'Multiple']

            if flag_ftl:
                str_status = 'Adjust FTL'
                break

            # 1) 불가능 case1 : 전체가 더이상 ftl 되지 않는 경우
            if (df_return['demand yn'] | df_return['overLtl yn']).all():
                flag_break = True
                break

    # 최종 status, qty정리
    df_return = fn_adjust_make_status(df_return, str_status)

    # ftl이거나 demand 고려하지 않고도 ftl이 되지 않을 때(하나를 추가하면 max를 넘고,추가 하지 않으면 min을 못넘는 경우)
    if flag_ftl or df_return['overLtl yn'].all():
        return df_return
    # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패시
    else:
        # 모든 아이템에 대해 Demand 한도 내 증량 후 FTL 구성 실패 시
        # flag_break 초기화
        flag_break = False

        while not flag_break:
            # Profit Grade 순서대로 순차적으로 실행
            for row in df_return.itertuples():
                # inx 설정
                inx = row.Index
                flag_add = False

                num_fr = row[loc_multiple] / row[loc_max_load_qty]
                int_add_cnt = (np.where(df_return.loc[inx, 'Adjust Add Cnt'] == np.nan, 1,
                                        df_return.loc[inx, 'Adjust Add Cnt'] + 1)
                               )
                # Option1 별로 FTL 판별
                if Param_Adjust_Option1 == 'MAX':
                    if num_sum_fr == num_max_fr:  # max면 ftl로 종료
                        flag_break = True
                        flag_ftl = True
                    elif num_sum_fr + num_fr > num_max_fr:
                        if num_sum_fr < num_min_fr:
                            flag_ftl = False
                            # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                            df_return.loc[inx, 'overLtl yn'] = True
                        else:  # FTL
                            # Max에 가까운 값을 찾자
                            # 돌면서 ftl일 경우 해당 row의  ftl_flag 처리
                            df_return.loc[inx, 'ftl_flag'] = True
                            # 종료시점 : overLtl yn이 False이고(ftl불가능건이 아닌 건들)에 한하여
                            # ( ftl 가능 대상 ) ftl_flag가 모두 True일때 (모두 순회) 그 시점에 ftl로 나오기
                            list_where = df_return['overLtl yn'] == False
                            if (len(df_return[list_where]) > 0) and (df_return.loc[list_where, 'ftl_flag']).all():
                                flag_break = True
                                flag_ftl = True
                    else:
                        flag_add = True
                elif Param_Adjust_Option1 == 'MIN':
                    if num_min_fr <= num_sum_fr <= num_max_fr:
                        flag_break = True
                        flag_ftl = True
                    elif num_sum_fr + num_fr > num_max_fr:
                        if num_sum_fr < num_min_fr:
                            flag_ftl = False
                            # 하나를 더 실으면 max를 넘기고, 안 실으면 min을 넘지 못하는 경우 flag처리
                            df_return.loc[inx, 'overLtl yn'] = True
                    else:
                        flag_add = True

                if flag_add:
                    df_return.loc[inx, 'Adjust Add Cnt'] = int_add_cnt
                    df_return.loc[inx, 'Adjust Assigned Qty'] = (
                            df_return.loc[inx, 'Assigned Qty'] + (int_add_cnt * df_return.loc[inx, 'Multiple'])
                    )
                    df_return.loc[inx, 'Adjust Item FR'] = (
                            df_return.loc[inx, 'Adjust Assigned Qty'] / df_return.loc[inx, 'Use Mix Max Load Qty']
                    )
                    num_sum_fr = df_return['Adjust Item FR'].sum()
                    df_return['Adjust Sum FR'] = num_sum_fr

                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

                # 전체가 더이상 ftl 되지 않는 경우
                if df_return['overLtl yn'].all():
                    flag_break = True
                    break

        # 최종 status, qty정리
        df_return = fn_adjust_make_status(df_return, str_status)

        return df_return


def fn_container_planning_adjust_detail(df_p_source: pd.DataFrame) -> pd.DataFrame:
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

    num_sum_fr = df_return['Loaded FR'].sum()
    num_cut_basis = df_return.iloc[0]['Mix Cut Add']
    # ADD 로직 분기 - INDIR / DIR_D
    str_shipment_type = df_return.iloc[0]['Shipment Type']

    if num_sum_fr < num_cut_basis:
        # Cut 기준 미만이면 컨테이너 할당 내용을 지운다.
        df_return['Plan Type'] = '05.NP'
        df_return['Adjust Cut Add'] = 'CUT'
        df_return['Last Loading Qty'] = np.nan
        df_return['Loading Qty Per Cntr'] = np.nan
        df_return['cntr_block'] = np.nan
        df_return['cntr_seq'] = np.nan
    else:
        # Cut 기준 이상이면 Adjust Option2에 따른 로직으로 적재수량 조정
        df_return['Plan Type'] = '04.ML'
        df_return['Adjust Cut Add'] = 'ADD'
        # INDIR/ DIR  : Add 로직 분기
        if (str_shipment_type == 'INDIR') and (Param_Adjust_Option2 == 'Max Profit'):
            # df_return = fn_adjust_by_indir_profit_demand(df_return)
            df_return = fn_adjust_by_indir_profit_demand_with_option1(df_return)
        elif (str_shipment_type == 'INDIR') and (Param_Adjust_Option2 == 'Min Item Change'):
            # df_return = fn_adjust_by_indir_min_item_change(df_return)
            df_return = fn_adjust_by_indir_min_item_change_with_option1(df_return)
        elif Param_Adjust_Option2 == 'Min Item Change':
            # df_return = fn_adjust_by_min_item_change(df_return)
            df_return = fn_adjust_by_min_item_change_with_option1(df_return)
        elif Param_Adjust_Option2 == 'Max Profit':
            # df_return = fn_adjust_by_max_profit(df_return)
            df_return = fn_adjust_by_max_profit_with_option1(df_return)

    return df_return


@_decoration_
def fn_container_planning_adjust_single(df_p_source: pd.DataFrame) -> pd.DataFrame:
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

    for inx in range(len(df_return)):
        if df_return.iloc[inx]['Single Cut Add'] < df_return.iloc[inx]['Single Item FR']:
            df_return.iloc[inx, df_return.columns.get_loc('Adjust Cut Add')] = 'ADD'
            df_return.iloc[inx, df_return.columns.get_loc('Plan Type')] = '06.SL'
            df_return.iloc[inx, df_return.columns.get_loc('Last Loading Qty')] = df_return.iloc[inx]['Max Load Qty']
            df_return.iloc[inx, df_return.columns.get_loc('Loading Qty Per Cntr')] = df_return.iloc[inx]['Max Load Qty']
            df_return.iloc[inx, df_return.columns.get_loc('cntr_block')] = 1
            df_return.iloc[inx, df_return.columns.get_loc('cntr_seq')] = 1
            df_return.iloc[inx, df_return.columns.get_loc('Mixed Item Cntr Status')] = 'Adjust Single FTL'
        else:
            df_return.iloc[inx, df_return.columns.get_loc('Adjust Cut Add')] = 'CUT'
            df_return.iloc[inx, df_return.columns.get_loc('Plan Type')] = '05.NP'
            df_return.iloc[inx, df_return.columns.get_loc('Last Loading Qty')] = np.nan
            df_return.iloc[inx, df_return.columns.get_loc('Loading Qty Per Cntr')] = np.nan
            df_return.iloc[inx, df_return.columns.get_loc('cntr_block')] = np.nan
            df_return.iloc[inx, df_return.columns.get_loc('cntr_seq')] = np.nan
            df_return.iloc[inx, df_return.columns.get_loc('Mixed Item Cntr Status')] = 'LTL'

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
    # 출발-도착지 기준(Prod Week-From-To-Account-Ship To) 기준으로 그룹핑 하여 넘버링 작업함.
    # 데이터 정렬
    df_target = (df_target.
                 sort_values(by=['Plan Group Key', 'Plan Type', 'Last Mix Group', 'cntr_block', 'cntr_seq'],
                             ascending=[True, True, True, True, True]).reset_index(drop=True))

    fn_log_dataframe(df_target, "df_cntr_order")
    # Week별 Simulated By의 최대 maxSeq값 가져오기
    # df_target = df_target.merge(in_LoadingPOCntrPlanSeqInfo, how='left', on=['Time.[Week]'])
    # 초기값 maxUserSeq = 0
    # df_target['maxUserSeq'] = (df_target['Loading PO Cntr Plan_Cntr No'].
    #                            replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(int))
    # Merge 후처리
    df_target = fn_merge_after(df_target)

    df_target = df_target.groupby('Time.[Week]', group_keys=True).apply(
        lambda grp: fn_cntr_numbering_by_group(grp, "0")).reset_index(drop=True)
    df_target = df_target.groupby(["Time.[Week]", "Plan Group Key"], group_keys=True).apply(
        lambda grp: fn_cntr_numbering_by_group(grp, "1")).reset_index(drop=True)

    df_return = pd.concat([df_target, df_no_target], ignore_index=True)

    return df_return


def fn_cntr_numbering_by_group(df_p_source: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
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
    df_return = df_p_source.copy(deep=True)

    # Plan Type, Last Mix Group, cntr_block별 grouping된 값( 기본 0부터 시작, grouping key가 없으면 -1 )
    df_return['Cntr No Init'] = (
        df_return.groupby(['Plan Group Key', 'Plan Type', 'Last Mix Group', 'cntr_block']).ngroup()
        .replace(r'^\s*$', np.nan, regex=True).fillna(-1).astype(int)
    )
    df_return['Cntr No Init2'] = (
        df_return.groupby(['Plan Type', 'Last Mix Group', 'cntr_block']).ngroup()
        .replace(r'^\s*$', np.nan, regex=True).fillna(-1).astype(int)
    )

    # Single FTL 제외하고 Max 값 구하기
    int_max_cntr_no = df_return['Cntr No Init'].max()
    int_max_cntr_no2 = df_return['Cntr No Init2'].max()

    # Single FTL 경우 Cntr No Init
    for inx, row in df_return.iterrows():
        if row['Plan Type'] == '01.SF' or row['Plan Type'] == '02.SC' or row['Plan Type'] == '06.SL':
            int_max_cntr_no += 1
            int_max_cntr_no2 += 1
            df_return.at[inx, 'Cntr No Init'] = int_max_cntr_no
            df_return.at[inx, 'Cntr No Init2'] = int_max_cntr_no2

    # Cntr No
    # df_return['Cntr No'] = (
    #         df_return['maxUserSeq'] + df_return.groupby(['Plan Group Key', 'Plan Type', 'Cntr No Init']).ngroup() + 1
    # )
    if str_p_cond == "0":
        df_return['Cntr No'] = df_return.groupby(['Plan Group Key', 'Plan Type', 'Cntr No Init2']).ngroup() + 1
    else:
        df_return['Cntr No 2'] = df_return.groupby(['Plan Group Key', 'Plan Type', 'Cntr No Init']).ngroup() + 1

    return df_return


@_decoration_
def fn_container_planning_adjust(df_p_source: pd.DataFrame) -> pd.DataFrame:
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

    df_return = df_return.assign(**{
        'Adjust Cut Add': np.nan,
        'Adjust Add Cnt': 0,
        'Adjust Assigned Qty': np.nan,
        'Adjust Item FR': np.nan,
        'Adjust Sum FR': np.nan,
    })

    # 조정 대상 추출
    list_where_adjust_target = df_return['Plan Type'].isna() & (df_return['Mixed Item Cntr Status'] == 'LTL')
    df_no_adjust = df_return[~list_where_adjust_target].copy(deep=True)
    df_adjust = df_return[list_where_adjust_target].copy(deep=True)

    list_where_adjust_no_group = ((df_adjust['Last Mix Group'].isna()) &
                                  ((df_adjust['1st Mix'] == 'None') | (df_adjust['1st Mix'] == 'Item Mix Group')) &
                                  (df_adjust['2nd Mix'] == 'None') &
                                  (df_adjust['3rd Mix'] == 'None'))
    df_adjust_single_no_group = df_adjust[list_where_adjust_no_group].copy(deep=True)

    # 1) Single Adjust 처리
    if not df_adjust_single_no_group.empty and len(df_adjust_single_no_group) > 0:
        df_adjust_single_no_group = fn_container_planning_adjust_single(df_adjust_single_no_group)

    # Mix 예외처리에서 LTL이 된건이 Adjust까지 온 경우
    # 동일한 Last Mix Group끼리 Max Loading Qty만큼 채워준다.
    # Same Max Loading Qty FTL Check (예외대상 찾기)
    # Grouping 된 Item의 M/L Qty & Multiple 동일하고, M/L Qty 가 Multiple 의 배수가 아닌 케이스 대상
    # : Multiple 보정없이 CNTR Planning
    df_adjust_mixed_except_ltl_group = pd.DataFrame()
    if not (df_adjust['Last Mix Group'].isna()).all():  # Last Mix Group이 모두 np.nan일 경우 transform시 에러 남.
        df_adjust[['Max Load Qty Unique', 'Multiple Unique']] = (
            df_adjust.groupby('Last Mix Group')[['Max Load Qty', 'Multiple']].transform('nunique')
        )
        df_adjust['Chk Qty Sum'] = df_adjust.groupby('Last Mix Group')['Mixed Rest Qty'].transform('sum')
        # M/L Qty & Multiple 동일
        list_where_except_unique = (df_adjust['Max Load Qty Unique'] == 1) & (df_adjust['Multiple Unique'] == 1)
        # M/L Qty 가 Multiple 의 배수가 아니고
        list_where_except_multiple_not = df_adjust['Max Load Qty'] % df_adjust['Multiple'] > 0
        list_where_except = list_where_except_unique & list_where_except_multiple_not
        # 예외 Container Planning
        df_adjust_mixed_except_ltl_group = df_adjust[~list_where_adjust_no_group & list_where_except]
        # 1) 예외 LTL Adjust 처리
        if not df_adjust_mixed_except_ltl_group.empty and len(df_adjust_mixed_except_ltl_group) > 0:
            df_adjust_mixed_except_ltl_group = (
                df_adjust_mixed_except_ltl_group
                .sort_values(by=['Last Mix Group', 'Profit Grade Priority', 'Max Load Qty',
                                 'Mixed Rest Qty'], ascending=[True, True, True, False])
                .groupby('Last Mix Group', group_keys=False)
                .apply(fn_container_planning_adjust_except)
                .reset_index(drop=True)
            )
        df_adjust_mixed = df_adjust[~list_where_adjust_no_group & ~list_where_except].copy(deep=True)
    else:
        df_adjust_mixed = df_adjust[~list_where_adjust_no_group].copy(deep=True)

    # 3) 그 외 Adjust 처리
    if not df_adjust_mixed.empty and len(df_adjust_mixed) > 0:
        df_adjust_mixed = (
            df_adjust_mixed.groupby(by=['Last Mix Group', 'cntr_block'], group_keys=True)
            .apply(lambda group: fn_container_planning_adjust_detail(group)))

    # 조정 비대상 건과 조정 대상 건 합치기
    df_return = pd.concat([df_no_adjust, df_adjust_single_no_group, df_adjust_mixed_except_ltl_group, df_adjust_mixed], ignore_index=True)
    fn_log_dataframe(df_return, "df_cntr_numbering_input")

    # Adjust LTL 처리 : Adjust 조정 후에 LTL인 건에 대한 Adjust 처리
    # 대상 : Plan Type = '04.ML' and Loading Status = 'LTL' 인건 ( Adjust ADD를 탔는데도 최종 LTL로 나온건 )
    list_where_last_ltl_target = (df_return['Plan Type'] == '04.ML') & (df_return['Mixed Item Cntr Status'] == 'LTL')

    df_return_last_ltl = df_return[list_where_last_ltl_target].copy(deep=True)
    if not df_return_last_ltl.empty and len(df_return_last_ltl) > 0:
        df_return_last_ltl = (
            df_return_last_ltl
            .sort_values('Profit Grade Priority', ascending=True)
            .groupby(by=['Last Mix Group', 'cntr_block'], group_keys=True)
            .apply(lambda group: fn_container_planning_last_adjust_detail(group)))
        # 결과 합치기
        df_return = pd.concat([df_return_last_ltl, df_return[~list_where_last_ltl_target]], ignore_index=True)
    # 컨테이너 넘버링
    df_return = fn_cntr_numbering_main(df_return)

    ####################################################################################################################
    # Debugging을 위해 필요한 컬럼만 추출
    if is_local and not df_return.empty and len(df_return) > 0:
        list_column = ['Seq.[Seq]', 'Item', 'Max Load Qty', 'Min Qty', 'Multiple', 'Profit Grade',
                       'Profit Grade Priority', 'Chk Qty', 'cntr_seq', 'cntr_block',
                       'Loading Qty Per Cntr', 'Plan Type', 'Adj Chk Qty', 'Adj Item FR', 'Planned Flag', 'Adj Min Qty',
                       'Initial Qty', 'Multiple Qty', 'Loaded FR', 'Sum of Loaded FR', 'Mixed Rest Qty',
                       'Adj Mixed Rest Qty', 'Assigned Qty', 'Unassigned Qty', 'Last Loading Qty',
                       'Mixed Item Cntr Status', 'Last Mix Group', '1st Mix Group', '1st Mix Group FTL Chk',
                       '2nd Mix Group', '2nd Mix Group FTL Chk', 'Adjust Cut Add', 'Adjust Add Cnt',
                       'Adjust Assigned Qty', 'Adjust Item FR', 'Adjust Sum FR'
                       ]
        df_return_debug = df_return[list_column]
        fn_log_dataframe(df_return_debug, 'df_return_debug_adjust')
    ####################################################################################################################

    return df_return


def fn_container_planning_adjust_except(group: pd.DataFrame) -> pd.DataFrame:
    """
    예외에서 ltl로 빠진건은
    1st, 2nd , 3rd 다 태우고도 ltl이면
    adjust 할때 같은 group으로 max loading qty만큼 채우기 ( 정렬 순서대로 )
    :param group: grouping된 except에서 남은건
    :return: DataFrame
    """
    # 테이블 복사
    group_df = group.copy()

    int_max_load_qty = group_df.iloc[0]['Max Load Qty']
    int_rest_qty_sum = group_df['Mixed Rest Qty'].sum()

    group_df['Adjust Assigned Qty'] = group_df['Mixed Rest Qty']
    if int_rest_qty_sum < int_max_load_qty:
        group_df.loc[group_df.index[0], 'Adjust Assigned Qty'] = (
                group_df.iloc[0]['Mixed Rest Qty'] + (int_max_load_qty - int_rest_qty_sum)
        )

    group_df['Adjust Item FR'] = group_df['Adjust Assigned Qty'] / group_df['Use Mix Max Load Qty']
    group_df['Adjust Sum FR'] = group_df['Adjust Item FR'].sum()

    group_df['Mixed Item Cntr Status'] = 'Adjust Except FTL'
    group_df['Plan Type'] = '07.ML.E'
    group_df['Loading Qty Per Cntr'] = group_df['Adjust Assigned Qty']
    group_df['Last Loading Qty'] = group_df['Loading Qty Per Cntr']
    return group_df


def fn_container_planning_last_adjust_detail(df_p_source: pd.DataFrame) -> pd.DataFrame:
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

    # 종류별로 분기
    df_return['Plan Type'] = '08.ML'
    df_return['Adjust Cut Add'] = 'CUT/ADD'  # 넣을까 말까
    # ADD 로직 분기 - INDIR / DIR_D
    str_shipment_type = df_return.iloc[0]['Shipment Type']

    # INDIR/ DIR  : Add 로직 분기
    if str_shipment_type == 'INDIR':
        df_return = fn_adjust_ltl_indir(df_return)
    elif str_shipment_type == 'DIR_D':
        df_return = fn_adjust_ltl_dir(df_return)

    return df_return


def fn_adjust_ltl_indir(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    inDir의 Adjust LTL : Adjust 후 LTL로 나온 건에 한하여 다시 Adjust LTL 로직을 적용한다.
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
    ####################################################################################################################
    # 1. LOOP 를 나가는 조건 ( 첫번째 loop )
    #   1) FTL
    #   2) LTL - 1.2.1)더이상 CUT 할 수 있는 대상이 없을때. ( 원래 값으로 원복 후 종료 )
    #          - 1.2.2)add를 계속 하다가 demand 부족으로 더이상 add 할 수 없는데 LTL일 경우  ( 원래 값으로 원복 후 종료 )
    #          - 1.2.3)Cut/Add 재선정시 Add 대상이 없을 때 ( 원래 값으로 원복 후 종료 )
    # 2. Cut 대상을 재선정하는 조건 ( 두번째 loop )
    #   1) 하나를 더 실으면 MAX를 넘고, 안실으면 MIN을 못넘기는 경우 : flag_overLtl_yn = True
    # 3. LOOP 돌기전 예외 처리
    #   1) 대상이 1건일 경우 Max Loading Qty로 한대 채워 FTL로 보내기
    #   2) 모든 대상에 대해 Cut 불가능 할 때   ( 원래 값으로 원복 후 종료 : for문을 돌기 전이므로 원래 값임)
    #   3) 모든 대상에 대해 Demand 이유로 Add 불가능 할 때  ( 원래 값으로 원복 후 종료 : for문을 돌기 전이므로 원래 값임)
    ####################################################################################################################

    # 예외-1) 1건일 경우
    if len(df_return) == 1:
        # 결과값 정리
        df_return['Mixed Item Cntr Status'] = 'Adjust FTL'
        df_return['Loading Qty Per Cntr'] = df_return['Max Load Qty']
        df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']
        return df_return

    # 예외-2) 모든 Item에 대해 Cut할 수 없는 경우
    if (df_return['Last Loading Qty'] == 0).all():
        return df_return

    # Const 설정
    num_sum_fr = (df_return['Last Loading Qty'] / df_return['Use Mix Max Load Qty']).sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']
    df_return['Cut Qty'] = 0
    df_return['Add Qty'] = 0
    flag_ftl = False
    str_status = 'LTL'
    flag_break = False

    # Loading Qty -> Temp Qty 복사
    df_return['Temp Qty'] = df_return['Last Loading Qty']
    # DMD ETA 4Week Sum Qty 에서 Last Loading Qty 만큼 차감한 값을 Rest Demand 칼럼으로 생성 ( add시 가능여부 판별 잔여 Demand )
    df_return['Rest Demand'] = df_return['DMD ETA 4Week Sum Qty'] - df_return['Last Loading Qty']
    # 원복용 Origin Rest Demand
    df_return['Origin Rest Demand'] = df_return['Rest Demand']

    # Cut/Add 선정
    df_return = fn_make_cut_add_target_in_dir(df_return)

    # 예외-3) 모든 Item에 대해 Add할 수 없는 경우
    if ((df_return['Rest Demand'] // df_return['Multiple']) <= 0).all() or (df_return['Add Flag'].isna()).all():
        return df_return

    # Cut 조정 반영된 전체 Fr
    num_add_sum_fr = num_sum_fr - df_return['Cut Fr'].sum()

    while not flag_break:
        # FTL 판별여부( row별 Demand 가능여부 )
        df_return['flag_demand_ltl'] = False
        for inx in range(len(df_return)):
            if df_return.iloc[inx]['Add Flag'] == 'Y':
                flag_add = False
                flag_overLtl_yn = False
                num_fr = df_return.iloc[inx]['Multiple'] / df_return.iloc[inx]['Use Mix Max Load Qty']
                if num_add_sum_fr + num_fr > num_max_fr:
                    if num_add_sum_fr >= num_min_fr:
                        flag_ftl = True
                        flag_break = True
                    else:
                        flag_overLtl_yn = True
                else:
                    if df_return.iloc[inx]['Rest Demand'] >= df_return.iloc[inx]['Multiple']:
                        flag_add = True
                    else:
                        df_return.loc[df_return.index[inx], 'flag_demand_ltl'] = True

                if flag_add:
                    df_return.loc[df_return.index[inx], 'Add Qty'] += df_return.iloc[inx]['Multiple']
                    df_return.loc[df_return.index[inx], 'Rest Demand'] -= df_return.iloc[inx]['Multiple']
                    num_add_sum_fr += num_fr

                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

                # Add 대상의 demand부족으로 더 Add할 수 없을 경우 ( 원래 값으로 원복 후 종료 )
                if df_return.loc[df_return['Add Flag'] == 'Y', 'flag_demand_ltl'].all():
                    flag_break = True
                    break

                # Cut 대상 재선정 경우
                # 1) FTL이 안되거나(하나를 더 실으면 max를 넘고, 안실으면 min을 넘지 못하는 경우)
                if flag_overLtl_yn:
                    # 초기화
                    df_return['Cut Flag'] = np.nan
                    df_return['Add Flag'] = np.nan
                    df_return['Add Qty'] = 0
                    df_return['Rest Demand'] = df_return['Origin Rest Demand']

                    # Cut 대상이 없으면 나가기
                    if (df_return['Temp Qty'] == 0).all():
                        flag_break = True
                        break

                    # Cut/Add 선정
                    df_return = fn_make_cut_add_target_in_dir(df_return)

                    # Add 대상이 없으면 나가기 ( 원래 값으로 원복 후 종료 )
                    if (df_return['Add Flag'].isna()).all():
                        flag_break = True
                        break

                    # Cut 조정 반영된 전체 Fr
                    num_add_sum_fr = num_sum_fr - df_return['Cut Fr'].sum()

                    # Cut/Add 재산정했으므로 for문 나가서 처음부터 새로 돌기
                    break

    # 나왔는데 LTL일 경우 원복 (Temp Qty, Cut Qty, Add Qty)
    # 1) add를 계속 하다가 demand 부족으로 더이상 add 대상에 대해 add 할 수 없는데 LTL일 경우
    # 2) cut 대상, add 대상을 선정 해야 하는데 선정 시점에 있어서 add 대상이 없을 경우
    # 3) cut을 다해서 0으로 되었는데 LTL일 경우
    if str_status == 'LTL':
        df_return['Temp Qty'] = df_return['Last Loading Qty']
        df_return['Cut Qty'] = 0
        df_return['Add Qty'] = 0

    # 결과값 정리
    df_return['Mixed Item Cntr Status'] = str_status
    df_return['Loading Qty Per Cntr'] = df_return['Temp Qty'] + df_return['Add Qty']
    df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']

    # Last Loading Qty == 0 Cut 처리:
    list_where_cut_target = df_return['Last Loading Qty'] == 0
    df_return.loc[list_where_cut_target, 'Plan Type'] = '05.NP'
    df_return.loc[list_where_cut_target, 'Adjust Cut Add'] = 'CUT'
    df_return.loc[list_where_cut_target, 'Last Loading Qty'] = np.nan
    df_return.loc[list_where_cut_target, 'Loading Qty Per Cntr'] = np.nan
    df_return.loc[list_where_cut_target, 'cntr_block'] = np.nan
    df_return.loc[list_where_cut_target, 'cntr_seq'] = np.nan
    df_return.loc[list_where_cut_target, 'Mixed Item Cntr Status'] = 'LTL'

    return df_return


def fn_make_cut_add_target_in_dir(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        inDir의 Adjust LTL 처리의 cut/add 대상 찾기
    :param df_p_source:
    :return:
    """
    # DataFrame Copy
    df_return = df_p_source.copy(deep=True)

    # Cut 대상 선정 : Temp Qty > 0 인 건 중에서, P/G 낮은순 정렬, Demand 낮은순 정렬
    list_where_cut_is = df_return['Temp Qty'] > 0
    int_cut_idx = (
        df_return[list_where_cut_is]
        .sort_values(by=['Profit Grade Priority', 'DMD ETA 4Week Sum Qty'], ascending=[False, True])
    ).index[0]
    df_return.loc[int_cut_idx, 'Cut Flag'] = 'Y'

    # Multiple 만큼 감량(Temp Qty) , Cut Qty, Cut Fr 생성
    #  0 < Temp Qty < Multiple 일 경우 Temp Qty만큼 뺀다 (cut이 0이 될때까지 반영한다.)
    if df_return.loc[int_cut_idx, 'Multiple'] > df_return.loc[int_cut_idx, 'Temp Qty']:
        int_cut_qty = df_return.loc[int_cut_idx, 'Temp Qty']
    else:
        int_cut_qty = df_return.loc[int_cut_idx, 'Multiple']
    df_return.loc[int_cut_idx, 'Cut Qty'] += int_cut_qty
    df_return.loc[int_cut_idx, 'Temp Qty'] -= int_cut_qty
    df_return.loc[int_cut_idx, 'Cut Fr'] = (
            df_return.loc[int_cut_idx, 'Cut Qty'] / df_return.loc[int_cut_idx, 'Use Mix Max Load Qty']
    )

    # Add 대상 선정 : Cut선정 Item 제외, Demand 고려 증량 가능 Item, P/G 가장 높은 Item
    if Param_Adjust_Option2 == 'Max Profit':
        list_where_cut_target_except = df_return['Cut Flag'].isna()
        list_where_demand_is = df_return['Rest Demand'] >= df_return['Multiple']
        min_profit_grade = df_return.loc[
            list_where_cut_target_except & list_where_demand_is, 'Profit Grade Priority'].min()
        list_where_min_profit = df_return['Profit Grade Priority'] == min_profit_grade
        list_where = list_where_cut_target_except & list_where_demand_is & list_where_min_profit
    elif Param_Adjust_Option2 == 'Min Item Change':
        list_where_cut_target_except = df_return['Cut Flag'].isna()
        list_where_demand_is = df_return['Rest Demand'] >= df_return['Multiple']
        list_where = list_where_cut_target_except & list_where_demand_is
    else:
        list_where = pd.Series()
    df_return.loc[list_where, 'Add Flag'] = 'Y'

    return df_return


def fn_adjust_ltl_dir(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Dir의 Adjust LTL : Adjust 후 LTL로 나온 건에 한하여 다시 Adjust LTL 로직을 적용한다.

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
    ####################################################################################################################
    # 1. LOOP 를 나가는 조건 ( 첫번째 loop )
    #   1) FTL
    #   2) LTL - 더이상 CUT 할 수 있는 대상이 없을때.  ( 원래 값으로 원복 후 종료 )
    # 2. Cut 대상을 재선정하는 조건 ( 두번째 loop )
    #   1) 하나를 더 실으면 MAX를 넘고, 안실으면 MIN을 못넘기는 경우 : flag_overLtl_yn = True
    # 3. LOOP 돌기전 예외처리
    #   1) 대상이 1건일 경우 Max Loading Qty로 한대 채워 FTL로 보내기
    #   2) 모든 대상에 대해 Cut 불가능 할 때
    ####################################################################################################################

    # 예외-1) 1건일 경우
    if len(df_return) == 1:
        # 결과값 정리
        df_return['Mixed Item Cntr Status'] = 'Adjust FTL'
        df_return['Loading Qty Per Cntr'] = df_return['Max Load Qty']
        df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']
        return df_return

    # 예외-2) 모든 Item에 대해 Cut할 수 없는 경우
    if (df_return['Last Loading Qty'] == 0).all():
        return df_return

    # Const 설정
    num_sum_fr = (df_return['Last Loading Qty'] / df_return['Use Mix Max Load Qty']).sum()
    num_max_fr = df_return.iloc[0]['Mix Max FR']
    num_min_fr = df_return.iloc[0]['Mix Min FR']
    df_return['Cut Qty'] = 0
    df_return['Add Qty'] = 0

    flag_ftl = False
    str_status = 'LTL'
    flag_break = False

    # Loading Qty -> Temp Qty 복사
    df_return['Temp Qty'] = df_return['Last Loading Qty']

    # Cut/Add 대상 선정
    df_return = fn_make_cut_add_target_dir(df_return)

    # Cut 조정 반영된 전체 Fr
    num_add_sum_fr = num_sum_fr - df_return['Cut Fr'].sum()

    while not flag_break:
        for inx in range(len(df_return)):
            if df_return.iloc[inx]['Add Flag'] == 'Y':
                flag_add = False
                flag_overLtl_yn = False
                num_fr = df_return.iloc[inx]['Multiple'] / df_return.iloc[inx]['Use Mix Max Load Qty']
                if num_add_sum_fr + num_fr > num_max_fr:
                    if num_add_sum_fr >= num_min_fr:
                        flag_ftl = True
                        flag_break = True
                    else:
                        flag_overLtl_yn = True
                else:
                    flag_add = True

                if flag_add:
                    df_return.iloc[inx, df_return.columns.get_loc('Add Qty')] += df_return.iloc[inx]['Multiple']
                    num_add_sum_fr += num_fr

                if flag_ftl:
                    str_status = 'Adjust FTL'
                    break

                if flag_overLtl_yn:
                    # 초기화
                    df_return['Cut Flag'] = np.nan
                    df_return['Add Flag'] = np.nan
                    df_return['Add Qty'] = 0

                    # Cut 대상이 없으면 나가기
                    if (df_return['Temp Qty'] == 0).all():
                        flag_break = True
                        break

                    # Cut/Add 대상 선정
                    df_return = fn_make_cut_add_target_dir(df_return)

                    # Cut 조정 반영된 전체 Fr
                    num_add_sum_fr = num_sum_fr - df_return['Cut Fr'].sum()

                    # Cut/Add 재산정했으므로 for문 나가서 처음부터 새로 돌기
                    break

    # 나왔는데 LTL일 경우 원복 (Temp Qty, Cut Qty, Add Qty)
    # 1) cut을 다해서 0으로 되었는데 LTL일 경우
    if str_status == 'LTL':
        df_return['Temp Qty'] = df_return['Last Loading Qty']
        df_return['Cut Qty'] = 0
        df_return['Add Qty'] = 0

    # 결과 정리
    df_return['Mixed Item Cntr Status'] = str_status
    df_return['Loading Qty Per Cntr'] = df_return['Temp Qty'] + df_return['Add Qty']
    df_return['Last Loading Qty'] = df_return['Loading Qty Per Cntr']

    # Last Loading Qty == 0 Cut 처리:
    list_where_cut_target = df_return['Last Loading Qty'] == 0
    df_return.loc[list_where_cut_target, 'Plan Type'] = '05.NP'
    df_return.loc[list_where_cut_target, 'Adjust Cut Add'] = 'CUT'
    df_return.loc[list_where_cut_target, 'Last Loading Qty'] = np.nan
    df_return.loc[list_where_cut_target, 'Loading Qty Per Cntr'] = np.nan
    df_return.loc[list_where_cut_target, 'cntr_block'] = np.nan
    df_return.loc[list_where_cut_target, 'cntr_seq'] = np.nan
    df_return.loc[list_where_cut_target, 'Mixed Item Cntr Status'] = 'LTL'

    return df_return


def fn_make_cut_add_target_dir(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        dir의 Adjust LTL 처리의 cut/add 대상 찾기
    :param df_p_source:
    :return:
    """
    # DataFrame Copy
    df_return = df_p_source.copy(deep=True)

    # Cut 대상 선정 : Temp Qty > 0 인 건 중에서, P/G 낮은순 정렬 했을 때 첫번째 값
    list_where_cut_is = df_return['Temp Qty'] > 0
    int_cut_idx = (df_return[list_where_cut_is].sort_values(by='Profit Grade Priority', ascending=False)).index[0]
    df_return.loc[int_cut_idx, 'Cut Flag'] = 'Y'
    #  0 < Temp Qty < Multiple 일 경우 Temp Qty만큼 뺀다 (cut이 0이 될때까지 반영한다.)
    if df_return.loc[int_cut_idx, 'Multiple'] > df_return.loc[int_cut_idx, 'Temp Qty']:
        int_cut_qty = df_return.loc[int_cut_idx, 'Temp Qty']
    else:
        int_cut_qty = df_return.loc[int_cut_idx, 'Multiple']
    df_return.loc[int_cut_idx, 'Cut Qty'] += int_cut_qty
    df_return.loc[int_cut_idx, 'Temp Qty'] -= int_cut_qty
    df_return.loc[int_cut_idx, 'Cut Fr'] = df_return.loc[int_cut_idx, 'Cut Qty'] / df_return.loc[
        int_cut_idx, 'Use Mix Max Load Qty']

    # Add 대상 선정 : Cut선정 Item 제외 , P/G 가장 높은 Item
    if Param_Adjust_Option2 == 'Max Profit':
        list_where_cut_target_except = df_return['Cut Flag'].isna()
        min_profit_grade = df_return.loc[list_where_cut_target_except, 'Profit Grade Priority'].min()
        list_where_min_profit = df_return['Profit Grade Priority'] == min_profit_grade
        list_where = list_where_cut_target_except & list_where_min_profit
    # Add 대상 선정 : Cut선정 Item 제외
    elif Param_Adjust_Option2 == 'Min Item Change':
        list_where = df_return['Cut Flag'].isna()
    else:
        list_where = pd.Series()
    df_return.loc[list_where, 'Add Flag'] = 'Y'

    return df_return


def fn_assign_match_line(group: pd.DataFrame) -> pd.DataFrame:
    """
        ① Check Qty. 값을 Need Qty.에 복사
        ② Loading Qty. 내림차순 정렬
        ③ (Need - Loading) 값이 큰 쪽에 할당 결정
        ④ Loading Qty. 만큼 Simul. Qty. 증량
        ⑤ Loading Qty. 만큼 차감해서 Need Qty. 값 업데이트
        ⑥ 모든 Loading Qty. 할당할 때까지 ③~⑤ 반복
    :param group: grouping 된 CNTR Planning Table
    :return: DataFrame
    """
    # 테이블 복사
    group_df = group.copy()

    # KEY 추출
    str_key = group_df.iloc[0]['Aggr Grouping Key']

    # Order Table내 같은 KEY 대상 추출
    group_df_origin = df_in_POProcessDetail[df_in_POProcessDetail['Aggr Grouping Key'] == str_key]

    # 1) Order Table 건수가 1건이면 해당 Seq → Match Line 반영
    # 2) Order Table의 UnAssigned(초기 Chk Qty 복사) 와 Planning Table의 Loading Qty 의 Gap을 찾아
    #    Gap이 큰 Order Table의 Seq → Match Line 반영
    ####################################################################################################################
    # EX) 같은 Aggr Grouping Key 일때 , group_df : Loading Qty 내림차순 정렬
    # group_df_origin                                             group_df
    # Seq   | Chk Qty  | UnAssigned                               index | Last Loading Qty | Match Line
    # 11    |   60     | 60                                          1  | 100              |
    # 12    |   80     | 80                                          2  | 90               |
    # 13    |   30     | 30
    # iteration 1)
    # Seq   | Chk Qty  | UnAssigned  | UnAssigned-Loading Qty     index | Last Loading Qty | Match Line
    #  11    |   60    | 60          | -40                          1   | 100              |  12
    #  12    |   80    | 80          | -20
    #  13    |   30    | 30          | -70
    # iteration 2)
    # Seq   | Chk Qty  | UnAssigned  | UnAssigned-Loading Qty     index | Last Loading Qty | Match Line
    #  11    |   60    | 60          | -30                          1   | 100              |  12
    #  12    |   80    | -20         | -110                          2  | 90               |  11
    #  13    |   30    | 30          | -60
    ####################################################################################################################

    # Chk Qty 를 UnAssigned 칼럼으로 복사 후 진행
    group_df_origin['UnAssigned'] = group_df_origin['Chk Qty']
    # Match Line 초기화
    group_df['Match Line'] = np.nan
    # group_df Loading Qty 내림 차순 정렬
    group_df = group_df.sort_values(by=['Last Loading Qty'], ascending=[False])

    if len(group_df_origin) == 1:
        group_df['Match Line'] = group_df_origin.iloc[0]['Seq.[Seq]']
    elif len(group_df_origin) > 1:
        for i in range(len(group_df)):
            # gap을 찾아서 Chk Qty Gap에 반영
            num_gap = group_df_origin['UnAssigned'] - group_df.iloc[i]['Last Loading Qty']
            group_df_origin['Chk Qty Gap'] = num_gap
            # Chk Qty Gap의 최대값인 idx 찾기
            idx_max_gap = group_df_origin['Chk Qty Gap'].idxmax()
            # idx_max_gap의 Seq → Match Line 반영
            group_df.loc[group_df.index[i], 'Match Line'] = group_df_origin.loc[idx_max_gap, 'Seq.[Seq]']
            # Match Line 을 반영한 idx값의 UnAssigned는 할당된 Last Loading Qty를 빼줌(gap을 UnAssigned에 반영)
            group_df_origin.loc[idx_max_gap, 'UnAssigned'] -= group_df.iloc[i]['Last Loading Qty']

    return group_df


@_decoration_
def fn_assign(df_p_source: pd.DataFrame) -> tuple:
    """
    CNTR Planning Qty. ▶ Order line 별 할당 Logic
        1. Order Table 과 CNTR Planning 테이블을 join하여 Mgmt 테이블 결과 반환한다.
        2. df_assign_plan 에 아래 항목 추가
            - Measure.[Loading Dir Order Mgmt_Item FR]
            - Measure.[Loading Dir Order Mgmt_CNTR FR]
            - Measure.[Loading Dir Order Mgmt_Diff]
            - Measure.[Loading Dir Order Mgmt_Last Mix Group]
            - Measure.[Loading Dir Order Mgmt_Loading Qty]
            - Measure.[Loading Dir Order Mgmt_Loading Status]
            - Measure.[Loading Dir Order Mgmt_UnAssinged Qty]

    :param df_p_source: df_container_plan

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
        return df_return, df_return

    # 데이터 프레임 복사
    df_return_container = df_p_source.copy(deep=True)

    # df_return 칼럼 생성 : df_adjust 와 merge (aggr 값 반영)
    # 1) row별 생성 : UnAssinged Qty, Loading Qty, Diff, Item FR
    # 2) aggr 값 반영 : CNTR FR, Last Mix Group, Loading Status
    df_return_container['Seq.[Seq]'] = df_return_container['Seq.[Seq]'].str.split("-").str[0]
    # df_return_cntr
    df_return_cntr = df_return_container.copy(deep=True)

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return_cntr['Last Loading Qty'] = (
        df_return_cntr['Last Loading Qty'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    )

    # Item FR : Single FTL은 M/L Qty.이든 LDM이든 100%로 보여주고,
    # 혼적일 때만 M/L Qty. 또는 LDM으로 정한 기준과 동일하게 CNTR F/R 보여주도록 해주시면 되겠습니다.
    list_where_single_ftl = df_return_cntr['Plan Type'].isin(['01.SF', '02.SC'])
    list_where_except = df_return_cntr['Plan Type'] == '05.NP'
    df_return_cntr['Item FR'] = np.where(
        list_where_except,
        0,
        np.where(
            list_where_single_ftl,
            df_return_cntr['Last Loading Qty'] / df_return_cntr['Use Single Max Load Qty'],
            df_return_cntr['Last Loading Qty'] / df_return_cntr['Use Mix Max Load Qty']
        )
    )

    # 05.NP 아닌 경우에 Match Line 적용.
    df_return_target = df_return_cntr[~list_where_except].copy(deep=True)
    # Match Line 찾기
    if not df_return_target.empty:
        df_return_target = (
            df_return_target.groupby('Aggr Grouping Key', group_keys=True).apply(fn_assign_match_line)
            .reset_index(drop=True)
        )
        df_return_target['Seq.[Seq]'] = df_return_target['Match Line']

    # 05.NP인 경우 Seq -> Match Line 임.
    df_return_cntr.loc[list_where_except, 'Match Line'] = df_return_cntr.loc[list_where_except, 'Seq.[Seq]']

    df_return_cntr = pd.concat([df_return_target, df_return_cntr[list_where_except]]).reset_index(drop=True)

    # grouping key : mgmt Grain
    list_col_key = ['Time.[Week]', 'Location.[Location]', 'To Site', 'Account', 'Item', 'Seq.[Seq]']
    df_containger_grouping = (
        df_return_cntr
        .groupby(list_col_key)
        .agg({'Last Loading Qty': 'sum',
              'Item FR': 'sum',
              'Mixed Item Cntr Status' : list,
              'Last Mix Group' : 'first',
              'Plan Group Key' : 'first'
              })
        .reset_index()
    )

    # list를 str 변환
    df_containger_grouping['Mixed Item Cntr Status'] = (
        df_containger_grouping['Mixed Item Cntr Status']
        .apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else str(x)))

    # Mgmt와 Container Planning 결과 Merge
    df_return = df_in_POProcessDetail.merge(df_containger_grouping, how='left', on=list_col_key)

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return['Last Loading Qty'] = (
        df_return['Last Loading Qty'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    )

    # UnAssinged Qty, Loading Qty, Diff, Item FR 칼럼 생성 (row 별로 생성)
    df_return['UnAssinged Qty'] = df_return['Chk Qty'] - df_return['Last Loading Qty']
    df_return['Loading Qty'] = df_return['Last Loading Qty']
    df_return['Diff'] = df_return['Loading Qty'] - df_return['Chk Qty']

    # CNTR FR ( Plan Group Key 기준으로 Item FR Sum ), Last Mix Group, Loading Status (aggr 값 반영)
    df_return['CNTR FR'] = df_return.groupby('Plan Group Key')['Item FR'].transform('sum')

    df_return['Loading Status'] = df_return['Mixed Item Cntr Status']

    # 숫자형 형식의 컬럼 중 비어 있는 값을 0 으로 채운다.
    df_return[['CNTR FR', 'Item FR']] = (
        df_return[['CNTR FR', 'Item FR']].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(float)
    )

    df_return["Simulated By"] = Param_User_Name
    # df_return["Simulation Time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df_return["Simulation Time"] = datetime.datetime.now().strftime('%Y/%m/%d')


    # 칼럼 정리
    return df_return, df_return_cntr

@_decoration_
def fn_output_formatter_po_process_detail(df_p_source: pd.DataFrame) -> pd.DataFrame:
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
    df_return.loc[df_return['Loading Status'].isna(), 'Loading Status'] = None

    if is_local:
        df_return = df_return.rename(columns={
            'Sub Location.[DisplayName]': 'Sub Location.[Sub Location$DisplayName]',
            'Location.[DisplayName]': 'Location.[Location$DisplayName]',
        })

    # 화면 정렬용 Measure 채우기
    # Prod Week_From Site Name_To Site Name_Account_Ship To_Item
    df_return['Result Sort'] = (df_return['Time.[Week]'].astype(str) + '_' +
                                df_return['Location.[Location$DisplayName]'].astype(str) + '_' +
                                df_return['Sub Location.[Sub Location$DisplayName]'].astype(str) + '_' +
                                df_return['Item'].astype(str) + '_' +
                                # np.where(df_return['JIG Line Value'] != '', df_return['JIG Line Value'] + '_', '') +
                                df_return['Account'].astype(str) + '_' +
                                df_return['Ship To'].astype(str))

    # 추가 컬럼 값 채우기
    df_return = df_return.assign(**{
        "Version.[Version Name]": Param_OUT_VERSION,
        "PO Week": INT_PO_WEEK
    })

    # Output 컬럼만 추출
    df_return = df_return[[
        "Version.[Version Name]", "Time.[Week]", "To Site", "Location.[Location]", "Item", "Org_Seq", "PO Week",
        "Chk Qty", "Last Loading Qty", "Diff", "Loading Status", "Item FR", "CNTR FR", "Simulated By", "Simulation Time"
    ]]

    # Output용으로 컬럼명 변경
    df_return = df_return.rename(columns={
        "Time.[Week]": "MFG Week.[MFG Week]",
        "To Site": "Location.[Location]",
        "Location.[Location]": "Sub Location.[Sub Location]",
        "Item": "Item.[Item]",
        "PO Week": "Time.[Week]",
        "Org_Seq": "Seq.[Seq]",
        "Last Loading Qty": f"PO Process Detail_Loading Qty({Param_Step})",
        "Diff": f"PO Process Detail_Diff Qty({Param_Step})",
        "Loading Status": f"PO Process Detail_Loading Status({Param_Step})",
        "Item FR": f"PO Process Detail_Item FR({Param_Step})",
        "CNTR FR": f"PO Process Detail_CNTR FR({Param_Step})",
        "Simulated By": "PO Process Detail_Simulated By",
        "Simulation Time": "PO Process Detail_Simulation Time"
    })

    # Final에 값 담기
    df_return = df_return.assign(**{
        "PO Process Detail_Check Qty(FINAL)": df_return["Chk Qty"],
        "PO Process Detail_Loading Qty(FINAL)": df_return[f"PO Process Detail_Loading Qty({Param_Step})"],
        "PO Process Detail_Diff Qty(FINAL)": df_return[f"PO Process Detail_Diff Qty({Param_Step})"],
        "PO Process Detail_Loading Status(FINAL)": df_return[f"PO Process Detail_Loading Status({Param_Step})"],
        "PO Process Detail_Item FR(FINAL)": df_return[f"PO Process Detail_Item FR({Param_Step})"],
        "PO Process Detail_CNTR FR(FINAL)": df_return[f"PO Process Detail_CNTR FR({Param_Step})"],
    })
    int_step = LIST_STEP.index(Param_Step)
    if 0 < int_step < 4:
        df_return[f"PO Process Detail_Check Qty({STR_NEXT_STEP})"] = (
            df_return)[f"PO Process Detail_Loading Qty({Param_Step})"]
        if int_step > 1:
            df_return["PO Process Detail_Last Step"] = int_step + 1

    df_return.drop(["Chk Qty"], axis=1, inplace=True)

    return df_return


def fn_join_string(list_p_target: list) -> str:
    list_filtered = [x for x in list_p_target if x != 'nan' and x is not np.nan and x is not None]
    str_return = ', '.join(list_filtered)

    return str_return


@_decoration_
def fn_output_formatter_po_process(df_p_source: pd.DataFrame, df_p_po_process: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or df_p_po_process.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source or df_p_po_process)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # Block 2 데이터 추출
    list_where_block2 = (df_p_source["Block"] == "DIR_BOTH") | (df_p_source["Block"] == "DIR_ONLY")
    df_return_block2 = df_p_source[list_where_block2].copy(deep=True)
    df_return_block1 = df_p_source[~list_where_block2].copy(deep=True)

    # Block1 데이터는 가공없이 Merge, Block2 데이터는 Group by - SUM
    df_return_block2_aggr = (
        df_return_block2.groupby(['Time.[Week]', 'Location.[Location]', 'To Site', 'Item'], group_keys=True).
        agg({"Chk Qty": "sum",
             "Last Loading Qty": "sum",
             "Diff": "sum",
             "Loading Status": list,
             "Item FR": "sum",
             "CNTR FR": "sum",
             "SOP ETD Week": "first",
             "Simulated By": "first",
             "Simulation Time": "first"
             }
            ).reset_index())
    # list를 str 변환
    df_return_block2_aggr['Loading Status'] = df_return_block2_aggr['Loading Status'].apply(fn_join_string)

    df_return_concat = pd.concat([df_return_block1, df_return_block2_aggr]).reset_index(drop=True)

    df_return = (
        df_p_po_process.merge(df_return_concat,
                              how='left',
                              left_on=["MFG Week.[MFG Week]", "Location.[Location]", "Sub Location.[Sub Location]",
                                       "Item.[Item]", "SOP Week.[SOP Week]"],
                              right_on=["Time.[Week]", "To Site", "Location.[Location]", "Item", "SOP ETD Week"]
                              ))
    df_return = df_return.rename(columns={
        "Location.[Location]_x": "Location.[Location]",
        "Time.[Week]_x": "Time.[Week]",
        "Last Loading Qty": f"PO Process_Loading Qty({Param_Step})",
        "Diff": f"PO Process_Diff Qty({Param_Step})",
        "Loading Status": f"PO Process_Loading Status({Param_Step})",
        "Item FR": f"PO Process_Item FR({Param_Step})",
        "CNTR FR": f"PO Process_CNTR FR({Param_Step})",
        "Simulated By": "PO Process_Simulated By",
        "Simulation Time": "PO Process_Simulation Time"
    })

    df_return = df_return[df_return["To Site"].notnull()].copy(deep=True)

    df_return["Version.[Version Name]"] = Param_OUT_VERSION
    df_return = df_return[[
        "Version.[Version Name]", "MFG Week.[MFG Week]", "Location.[Location]", "Sub Location.[Sub Location]",
        "Item.[Item]", "Time.[Week]", "SOP Week.[SOP Week]", "Delivery Week.[Delivery Week]",
        "Chk Qty", f"PO Process_Loading Qty({Param_Step})",
        f"PO Process_Diff Qty({Param_Step})", f"PO Process_Loading Status({Param_Step})",
        f"PO Process_Item FR({Param_Step})", f"PO Process_CNTR FR({Param_Step})",
        "PO Process_Simulated By", "PO Process_Simulation Time"
    ]]

    # Final에 값 담기
    df_return = df_return.assign(**{
        "PO Process_Check Qty(FINAL)": df_return["Chk Qty"],
        "PO Process_Loading Qty(FINAL)": df_return[f"PO Process_Loading Qty({Param_Step})"],
        "PO Process_Diff Qty(FINAL)": df_return[f"PO Process_Diff Qty({Param_Step})"],
        "PO Process_Loading Status(FINAL)": df_return[f"PO Process_Loading Status({Param_Step})"],
        "PO Process_Item FR(FINAL)": df_return[f"PO Process_Item FR({Param_Step})"],
        "PO Process_CNTR FR(FINAL)": df_return[f"PO Process_CNTR FR({Param_Step})"]
    })
    int_step = LIST_STEP.index(Param_Step)
    if 0 < int_step < 4:
        df_return[f"PO Process_Check Qty({STR_NEXT_STEP})"] = (
            df_return)[f"PO Process_Loading Qty({Param_Step})"]

    df_return.drop(["Chk Qty"], axis=1, inplace=True)

    return df_return


def fn_container_planning_seq_numbering(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
        From, To, Account 별 Ship To 묶음으로 Seq를 채번한다.
    :param df_p_source: From, To, Account 별 grouping 된 df
    :return: DataFrame
    """
    # DF 복사
    df_return = df_p_source.copy(deep=True).sort_values(by=['Ship To', 'Cntr No']).reset_index(drop=True)

    # index를 rownum 칼럼으로 변경
    df_return.index.name = 'rownum'
    df_return.reset_index(inplace=True, drop=False)

    # max Seq에 1씩 증가하여 Seq생성
    df_return['Seq.[Seq]'] = df_return['maxSeq'] + df_return['rownum'] + 1

    return df_return


def fn_container_planning_make_seq(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    container planning 메저그룹의 seq를 채번한다.
    Seq 채번: Week + From + To + Account별 max Seq +1 로 채번

    :param df_p_source: container Planning DF
    :return: DataFrame
    """
    # DF 복사
    df_return = df_p_source.copy(deep=True)

    # grouping list
    # list_col = ['Time.[Week]', 'Sub Location.[Sub Location]', 'Location.[Location]', 'Account']
    list_col = ['Time.[Week]', 'Location.[Location]', 'Sub Location.[Sub Location]']
    if len(in_LoadingPOCntrPlan) > 0:
        # Seq.[Seq]를 INT 로 변환 후 max값 구하기
        in_LoadingPOCntrPlan['Seq.[Seq]'] = in_LoadingPOCntrPlan['Seq.[Seq]'].astype(int)
        df_container_planning_agg = in_LoadingPOCntrPlan.groupby(list_col)['Seq.[Seq]'].max().reset_index(name='maxSeq')
        df_return = df_return.merge(df_container_planning_agg, how='left', on=list_col)
        # maxSeq 비어 있는 값 0 처리
        df_return['maxSeq'] = df_return['maxSeq'].replace(r'^\s*$', np.nan, regex=True).fillna(0).astype(int)
    else:
        df_return['maxSeq'] = 0

    df_return = df_return.groupby(list_col).apply(fn_container_planning_seq_numbering).reset_index(drop=True)

    return df_return


@_decoration_
def fn_output_formatter_container_plan(df_p_source: pd.DataFrame) -> pd.DataFrame:
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame을 리턴
    if df_p_source.empty or len(df_p_source) == 0:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 데이터 프레임 복사
    # container No 대상이 아닌 건은 제외
    df_return = df_p_source[df_p_source['Plan Type'] != '05.NP'].copy(deep=True)

    if not df_return.empty:
        if is_local:
            df_return = df_return.rename(columns={
                'Sub Location.[DisplayName]': 'Sub Location.[Sub Location$DisplayName]',
                'Location.[DisplayName]': 'Location.[Location$DisplayName]'
            })

        # 화면 정렬용 Measure 채우기
        # Prod Week_From Site Name_To Site Name_Account_Ship To_Item
        df_return['Result Sort'] = (df_return['Time.[Week]'].astype(str) + '_' +
                                    df_return['Location.[Location$DisplayName]'].astype(str) + '_' +
                                    df_return['Sub Location.[Sub Location$DisplayName]'].astype(str) + '_' +
                                    df_return['Item'].astype(str) + '_' +
                                    # np.where(df_return['JIG Line Value'] != '', df_return['JIG Line Value'] + '_', '') +
                                    df_return['Account'].astype(str) + '_' +
                                    df_return['Ship To'].astype(str))
        df_return = df_return.assign(**{
            "Version.[Version Name]": Param_OUT_VERSION,
            "Plan Step.[Plan Step]": Param_Step,
            "Sub Location.[Sub Location]": df_return["Location.[Location]"],
            "Location.[Location]": df_return["To Site"],
            "Item.[Item]": df_return["Item"],
            "Seq.[Seq]": np.nan,
            "Time.[Week]": df_return["Time.[Week]"],
            "Loading PO Cntr Plan_Account": df_return["Account"],
            "Loading PO Cntr Plan_Ship To": df_return["Ship To"],
            "Loading PO Cntr Plan_Item": df_return["Item"],
            "Loading PO Cntr Plan_Loading Status": df_return["Mixed Item Cntr Status"],
            "Loading PO Cntr Plan_Remark": np.nan,
            "Loading PO Cntr Plan_Loading Qty": df_return["Last Loading Qty"],
            "Loading PO Cntr Plan_Group Id": df_return["Plan Group Key"],
            "Loading PO Cntr Plan_Cntr No": df_return["Cntr No"],
            "Loading PO Cntr Plan_Cntr No 2": df_return["Cntr No 2"],
            # "Loading PO Cntr Plan_Match Line": df_return["Match Line"],
            "Loading PO Cntr Plan_Match Line": df_return["Org_Seq"],
            "Loading PO Cntr Plan_Plan Type": df_return["Plan Type"],
            "Loading PO Cntr Plan_Result Sort": df_return["Result Sort"],
            "Loading PO Cntr Plan_Simulated By": Param_User_Name,
        })

        # Seq 채번
        df_return = fn_container_planning_make_seq(df_return)

        # 칼럼 정리
        df_return = df_return[[
            'Version.[Version Name]',
            'Plan Step.[Plan Step]',
            'Location.[Location]',
            'Sub Location.[Sub Location]',
            'Item.[Item]',
            'Time.[Week]',
            'Seq.[Seq]',
            'Loading PO Cntr Plan_Item',
            'Loading PO Cntr Plan_Account',
            'Loading PO Cntr Plan_Ship To',
            'Loading PO Cntr Plan_Loading Status',
            'Loading PO Cntr Plan_Remark',
            'Loading PO Cntr Plan_Loading Qty',
            'Loading PO Cntr Plan_Group Id',
            'Loading PO Cntr Plan_Cntr No',
            'Loading PO Cntr Plan_Cntr No 2',
            'Loading PO Cntr Plan_Match Line',
            'Loading PO Cntr Plan_Plan Type',
            'Loading PO Cntr Plan_Result Sort',
            'Loading PO Cntr Plan_Simulated By'
        ]]

        df_return_final = df_return.copy(deep=True)
        df_return_final["Plan Step.[Plan Step]"] = "FINAL"

        df_return = pd.concat([df_return, df_return_final])

    return df_return


@_decoration_
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    """
    MediumWeight로 실행 시 발생할 수 있는 Live Server에서의 오류를 방지하기 위해 Header만 있는 Output 테이블을 만든다.
    :param str_p_cond:
    :return: tuple
    """
    df_return = pd.DataFrame()
    if str_p_cond == '0':
        # out_POProcess
        df_return = pd.DataFrame(
            {
                "Version.[Version Name]": [], "MFG Week.[MFG Week]": [], "Location.[Location]": [],
                "Sub Location.[Sub Location]": [],"Item.[Item]": [], "Time.[Week]": [], "SOP Week.[SOP Week]": [],
                "Delivery Week.[Delivery Week]": [], f"PO Process_Loading Status({Param_Step})": [],
                f"PO Process_Loading Qty({Param_Step})": [], f"PO Process_Diff Qty({Param_Step})": [],
                f"PO Process_Item FR({Param_Step})": [], f"PO Process_CNTR FR({Param_Step})": [],
                "PO Process_Simulated By": [], "PO Process_Simulation Time": []
            }
        )
    elif str_p_cond == '1':
        # out_POProcessDetail
        df_return = pd.DataFrame(
            {
                "Version.[Version Name]": [], "MFG Week.[MFG Week]": [], "Location.[Location]": [],
                "Sub Location.[Sub Location]": [], "Item.[Item]": [], "Seq.[Seq]": [], "Time.[Week]": [],
                "PO Process Detail_Last Step": [], f"PO Process Detail_Loading Status({Param_Step})": [],
                f"PO Process Detail_Loading Qty({Param_Step})": [], f"PO Process Detail_Diff Qty({Param_Step})": [],
                f"PO Process Detail_Item FR({Param_Step})": [], f"PO Process Detail_CNTR FR({Param_Step})": [],
                "PO Process Detail_Simulated By": [], "PO Process Detail_Simulation Time": []
            }
        )
    elif str_p_cond == '2':
        # out_LoadingPOCntrPlan
        df_return = pd.DataFrame(
            {
                "Version.[Version Name]": [], "Sub Location.[Sub Location]": [], "Seq.[Seq]": [], "Item.[Item]": [],
                "Location.[Location]": [], "Time.[Week]": [], "Loading PO Cntr Plan_Account": [],
                "Loading PO Cntr Plan_Ship To": [], "Loading PO Cntr Plan_Block": [],
                "Loading PO Cntr Plan_Group Id": [], "Loading PO Cntr Plan_Cntr No": [], "Loading PO Cntr Plan_Item": [],
                "Loading PO Cntr Plan_Loading Status": [], "Loading PO Cntr Plan_Loading Qty": [],
                "Loading PO Cntr Plan_Match Line": [], "Loading PO Cntr Plan_Plan Type": [],
                "Loading PO Cntr Plan_Remark": [], "Loading PO Cntr Plan_Result Sort": [],
                "Loading PO Cntr Plan_Simulated By": []
            }
        )
    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_POProcess = pd.DataFrame()
    out_POProcessDetail = pd.DataFrame()
    out_LoadingPOCntrPlan = pd.DataFrame()
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
            Param_Adjust_Option1 = "MAX"
            # Param_Adjust_Option1 = "MIN"
            Param_Adjust_Option2 = "Max Profit"
            # Param_Adjust_Option2 = "Min Item Change"
            Param_User_Name = "gyeongh.kang"
            Param_Step = "M" # 시뮬레이션 대상 단계, P, M, ADJ1, ADJ2, ADJ3, FINAL
            Param_Check_Qty = "Current"  # Current-Check Qty(Step), POPOnly-POP(Step), POPShort-POP(Step)+Short(Step)

            in_POProcess = pd.read_csv(str_input_dir + "/in_POProcess.csv", encoding="UTF8")
            in_POProcessDetail = pd.read_csv(str_input_dir + "/in_POProcessDetail.csv", encoding="UTF8")
            in_LoadingPOCntrPlan = pd.read_csv(str_input_dir + "/in_LoadingPOCntrPlan.csv", encoding="UTF8")
            # in_LoadingPOCntrPlanSeqInfo = pd.read_csv(str_input_dir + "/in_LoadingPOCntrPlanSeqInfo.csv",
            #                                           encoding="UTF8")

        # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == "":
            Param_OUT_VERSION = "CWV_MP"

        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == "":
            flag_exception = True
        elif Param_Exception_Flag == "S":
            flag_exception = False

        if Param_Adjust_Option1 is None or Param_Adjust_Option1.strip() == "":
            Param_Adjust_Option1 = "Max"

        if Param_Adjust_Option2 is None or Param_Adjust_Option2.strip() == "":
            Param_Adjust_Option2 = "Max Profit"

        if Param_User_Name is None or Param_User_Name.strip() == "":
            Param_UserName = "gyeongh.kang"

        if Param_Step is None or Param_Step.strip() == "":
            logger.Note(p_note='Param_Step이 지정되지 않았습니다.', p_log_level=LOG_LEVEL.error())
            raise Exception("[Exception] Param_Step이 지정되지 않았습니다.")

        if Param_Check_Qty is None or Param_Check_Qty.strip() == '':
            Param_Check_Qty = 'Current'

        # 입력 변수 확인용 로그
        logger.Note(p_note=f"Param_OUT_VERSION : {Param_OUT_VERSION}", p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f"Param_Exception_Flag : {Param_Exception_Flag}", p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f"Param_Adjust_Option1 : {Param_Adjust_Option1}", p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f"Param_Adjust_Option2 : {Param_Adjust_Option2}", p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f"Param_User_Name : {Param_User_Name}", p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f"Param_Step : {Param_Step}", p_log_level=LOG_LEVEL.debug())
        logger.Note(p_note=f"Param_Check_Qty : {Param_Check_Qty}", p_log_level=LOG_LEVEL.debug())

        # session 사용자
        Param_User_Id = Param_User_Name
        # 입력 테이블 점검 및 로그
        fn_check_input_table(in_POProcess, "in_POProcess", "1")
        fn_check_input_table(in_POProcessDetail, "in_POProcessDetail", "0")
        fn_check_input_table(in_LoadingPOCntrPlan, "in_LoadingPOCntrPlan", "1")
        # fn_check_input_table(in_LoadingPOCntrPlanSeqInfo, "in_LoadingPOCntrPlanSeqInfo", "1")

        # PO Process Detail에는 PO Week이 없기 때문에 PO Process에서 PO Week을 가져와서 상수로 지정
        INT_PO_WEEK = in_POProcess["Time.[Week]"].iloc[0]

        # Param_Step 리스트
        LIST_STEP = ['P', 'M', 'ADJ1', 'ADJ2', 'ADJ3', 'FINAL']
        print(LIST_STEP.index(Param_Step))
        STR_NEXT_STEP = (
            LIST_STEP)[LIST_STEP.index(Param_Step) + 1] if LIST_STEP.index(Param_Step) + 1 < len(LIST_STEP) else 'FINAL'
        ################################################################################################################
        # STEP 0-1. 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 작업 진행함.
        ################################################################################################################
        dict_log = {
            "p_step_no": 10,
            "p_step_desc": "STEP 0-1. 전처리(in_LoadingDirOrderMgmt): 로직 구동 시 예외 사항이 발생하는 특정 컬럼의 경우 선처리 "
                           "작업 진행함.",
            "p_df_name": "df_in_POProcessDetail"
        }
        df_in_POProcessDetail = fn_preprocess(in_POProcessDetail, **dict_log)

        ################################################################################################################
        # STEP 0-2. Prod Week-From Site-To Site-Account-Ship To-Item을 기준으로 Aggregation
        ################################################################################################################
        # PO Process의 경우에는 이미 Aggregation된 상태이기 때문에 이 부분은 주석 처리함.
        # dict_log = {
        #     'p_step_no': 20,
        #     'p_step_desc': 'STEP 0-2. Prod Week-From Site-To Site-Account-Ship To-Item을 기준으로 Aggregation',
        #     'p_df_name': 'df_aggregated_POProcessDetail'
        # }
        # df_aggregated_POProcessDetail = fn_aggregation(df_in_POProcessDetail, **dict_log)

        ################################################################################################################
        # STEP 0-3. Preprocess for Cntr Planning
        ################################################################################################################
        dict_log = {
            'p_step_no': 30,
            'p_step_desc': 'STEP 0-3. Preprocess for Cntr Planning',
            'p_df_name': 'df_cntr_plan_base'
        }
        df_cntr_plan_base = fn_preprocess_for_container_planning(df_in_POProcessDetail, **dict_log)

        ################################################################################################################
        # STEP 1-1. Single Loading 계산한다.
        ################################################################################################################
        # Single 계산
        dict_log = {
            'p_step_no': 110,
            'p_step_desc': 'STEP 1-1. Single Loading 계산한다.',
            'p_df_name': 'df_singleItem'
        }
        df_singleItem = fn_mgmt_calculate_single_item(df_cntr_plan_base, **dict_log)

        ################################################################################################################
        # STEP 1-2. Single Item Loading 대상으로 Container Planning 수행
        ################################################################################################################
        dict_log = {
            'p_step_no': 120,
            'p_step_desc': 'STEP 1-2. Single Item Loading 대상으로 Container Planning 수행',
            'p_df_name': 'df_cntr_plan_single'
        }
        df_cntr_plan_single = fn_container_planning_single(df_singleItem, **dict_log)

        ################################################################################################################
        # STEP 2. Mixed Item Loading 대상으로 Container Planning 수행: 최대 3회 수행
        ################################################################################################################
        dict_log = {
            'p_step_no': 210,
            'p_step_desc': 'STEP 2-1. Mixed Planning 공통 처리',
            'p_df_name': 'df_cntr_plan_mixed_base'
        }
        df_cntr_plan_mixed_base = fn_container_planning_mixed_common(df_cntr_plan_single, **dict_log)

        dict_log = {
            'p_step_no': 220,
            'p_step_desc': 'STEP 2-2. 1st Mix Planning',
            'p_df_name': 'df_cntr_plan_mixed_first'
        }
        df_cntr_plan_mixed_first = fn_container_planning_mixed(df_cntr_plan_mixed_base, '1st', **dict_log)

        dict_log = {
            'p_step_no': 230,
            'p_step_desc': 'STEP 2-3. 2nd Mix Planning',
            'p_df_name': 'df_cntr_plan_mixed_second'
        }
        df_cntr_plan_mixed_second = fn_container_planning_mixed(df_cntr_plan_mixed_first, '2nd', **dict_log)

        dict_log = {
            'p_step_no': 240,
            'p_step_desc': 'STEP 2-4. 3rd Mix Planning',
            'p_df_name': 'df_cntr_plan_mixed_third'
        }
        df_cntr_plan_mixed_third = fn_container_planning_mixed(df_cntr_plan_mixed_second, '3rd', **dict_log)

        ################################################################################################################
        # STEP 3. Inter Process : 1st ~ 3rd 이후 LTL 상태의 Cntr을 대상으로 조정 수행
        ################################################################################################################
        # Last Mix 기준으로 LTL 컨테이터 추가 할당 로직 넣어야 함.
        # Last Mix 이후 LTL 및 컨테이너 할당 안 된 전체를 모아 로직 수행
        # 기 할당된 컨테이너 단위로 작업 진행
        # 할당 안 된 아이텡의 경우 먼저 기 할당된 컨테이너 추가 하여 Max F/R을 넘지 않는 범위라면 해당 컨테이너에 할당
        # LTL 컨테이너 전부에 대해 탐해 후에도 할당할 수 있는 컨테이너가 없는 경우에는 새로운 컨테이너로 할당
        dict_log = {
            'p_step_no': 300,
            'p_step_desc': 'STEP 3. Inter Process : 1st ~ 3rd 이후 LTL 상태의 Cntr을 대상으로 조정 수행',
            'p_df_name': 'df_cntr_plan_inter_process'
        }
        df_cntr_plan_inter_process = fn_cntr_plan_inter_process(df_cntr_plan_mixed_third, **dict_log)

        ################################################################################################################
        # STEP 4. Adjust : LTL 상태의 Cntr을 대상으로 조정 수행
        ################################################################################################################
        dict_log = {
            'p_step_no': 400,
            'p_step_desc': 'STEP 4. Adjustment for LTL containers',
            'p_df_name': 'df_cntr_plan_adjust'
        }
        df_cntr_plan_adjust = fn_container_planning_adjust(df_cntr_plan_inter_process, **dict_log)

        ################################################################################################################
        # STEP 5. Assign the loading qty to the order.
        ################################################################################################################
        # Assign the loading qty to the order.
        df_assign_plan, df_container_plan_match = fn_assign(df_cntr_plan_adjust)
        logger.Step(p_step_no=500,
                    p_step_desc='STEP 5. Assign the loading qty to the order.')
        fn_log_dataframe(df_assign_plan, 'df_assign_plan')
        fn_log_dataframe(df_container_plan_match, 'df_container_plan_match')

        ################################################################################################################
        # STEP 6. format 정리
        ################################################################################################################
        dict_log = {
            'p_step_no': 601,
            'p_step_desc': "STEP 6. Output 정리 - PO Process Detail",
            'p_df_name': 'out_POProcessDetail'
        }
        out_POProcessDetail = fn_output_formatter_po_process_detail(df_assign_plan, **dict_log)

        dict_log = {
            'p_step_no': 602,
            'p_step_desc': "STEP 6. Output 정리 - PO Process",
            'p_df_name': 'out_POProcess'
        }
        out_POProcess = fn_output_formatter_po_process(df_assign_plan, in_POProcess, **dict_log)

        dict_log = {
            'p_step_no': 603,
            'p_step_desc': 'STEP 6. Container Planning - Output 정리',
            'p_df_name': 'out_LoadingPOCntrPlan'
        }
        out_LoadingPOCntrPlan = fn_output_formatter_container_plan(df_container_plan_match, **dict_log)

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()
        if flag_exception:
            out_POProcess = None
            out_POProcessDetail = None
            out_LoadingPOCntrPlan = None
            raise Exception(e)
        else:
            if out_POProcess.empty:
                out_POProcess = fn_set_header('0')
                fn_log_dataframe(out_POProcess, 'out_POProcess')
            if out_POProcessDetail.empty:
                out_POProcessDetail = fn_set_header('1')
                fn_log_dataframe(out_POProcessDetail, 'out_POProcessDetail')
            if out_LoadingPOCntrPlan.empty:
                out_LoadingPOCntrPlan = fn_set_header('2')
                fn_log_dataframe(out_LoadingPOCntrPlan, 'out_LoadingPOCntrPlan')
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')

    else:
        if out_POProcess.empty:
            out_POProcess = fn_set_header('0')
            fn_log_dataframe(out_POProcess, 'out_POProcess')
        if out_POProcessDetail.empty:
            out_POProcessDetail = fn_set_header('1')
            fn_log_dataframe(out_POProcessDetail, 'out_POProcessDetail')
        if out_LoadingPOCntrPlan.empty:
            out_LoadingPOCntrPlan = fn_set_header('2')
            fn_log_dataframe(out_LoadingPOCntrPlan, 'out_LoadingPOCntrPlan')
        logger.Finish()

    finally:
        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')
