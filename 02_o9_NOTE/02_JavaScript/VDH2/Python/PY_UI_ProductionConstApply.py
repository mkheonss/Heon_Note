"""

* 프로그램명
    - PY_UI_ProductionConstApply

* 내용
    - BOD Capa는 선복 기준 물류 Capa 제약 UI이나 현재 생산 제약용으로 사용중으로 당초 목적에 맞도록 선복 CAPA를 BOD Capa 를 운영하도록 하고,
      생산 관리용 신규 별도 UI 추가하고 관련 Short name을 BOD capa가 아닌 Original 사유로 발생되도록 운영
    - Production Constraint : Apply 액션버튼 수행
    - 상단 입력 row기준 Apply > 하단 report Week별 data분기
    - Group ID별 BOD Item 의 Item 을 Location 는 equal, Sub Location , Item 을 equal or like or All 로 Item 매핑데이타를 가져 옴

* Input
    - df_in_week : select ( [Time].[Month] * [Time].[Day] * [Time].[Week]);
    - df_in_constGroup : Constraint Group
    - df_in_item

* Flow Summary
    Step1. Constraint Group Detail(Measure Group) 생성
    Step2. Constraint Group Detail W (Measure Group) 생성
    Step3. Constraint Group Ecp (Measure Group) 생성

* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2024.06.03 / syif1380.lee / Create
    - 2024.11.14 / syif1380.lee / input : Time.Week 에 &MasterDataMgmtHorizon 적용
    - 2024.11.21 / syif1380.lee / Item attb 필터링 하여 Item 정보를 세팅하는 방법 적용
    - 2025.03.12 / syif1380.lee / vdCommon 공통 로그 작업
    - 2025.03.13 / syif1380.lee / df_in_constGroup : [Sequence].[Sequence] 을 &Sequence 로 변경 (속도영향)
    - 2025.04.25 / syif1380.lee / 무한대 설정 999999 => np.nan (null) 로 변경 (노보람p 요청)

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table
  - df_in_week : // select ( [Time].[Month] * [Time].[Day] * [Time].[Week]);
                // 2024.09.04 수정
                //select ( [Time].[Month] * [Time].[Day] * [Time].[Week] ) on row, () on column where {&CWVUI,Measure.[isMPHorizonFlag]==true};

                // 2024.11.14
                select ( [Time].[Month] * [Time].[Planning Month] * [Time].[Day]  * &MasterDataMgmtHorizon ) on row, () on column ;

                // 2025.01.03
                select ( [Time].[Month] * [Time].[Planning Month] * [Time].[Day]  * &MPHorizon ) on row, () on column ;

  - df_in_constGroup :
    # Select ([Version].[Version Name] * &Sequence * [Group].[Group ID] ) on row,
    #         ({Measure.[Const Grp_Build Ahead],
    #           Measure.[Const Grp_Definition],
    #           Measure.[Const Grp_Desc],
    #           Measure.[Const Grp_Enddate],
    #           Measure.[Const Grp_From Site],
    #           Measure.[Const Grp_From Site Name],
    #           Measure.[Const Grp_Inch],
    #           Measure.[Const Grp_Item],
    #           Measure.[Const Grp_Mkt Name],
    #           Measure.[Const Grp_Need Check],
    #           Measure.[Const Grp_Prod Qty],
    #           Measure.[Const Grp_Product Group],
    #           Measure.[Const Grp_Project],
    #           Measure.[Const Grp_Reason],
    #           Measure.[Const Grp_Refer Time],
    #           Measure.[Const Grp_Startdate],
    #           Measure.[Const Grp_To Site],
    #           Measure.[Const Grp_To Site Name],
    #           Measure.[Const Grp_Year]}) on column;

    ## 2025.03.13 수정
    Select ([Version].[Version Name] * &Sequence * [Group].[Group ID] ) on row, ({Measure.[Const Grp_Build Ahead], Measure.[Const Grp_Definition], Measure.[Const Grp_Desc], Measure.[Const Grp_Enddate], Measure.[Const Grp_From Site], Measure.[Const Grp_From Site Name], Measure.[Const Grp_Inch], Measure.[Const Grp_Item], Measure.[Const Grp_Mkt Name], Measure.[Const Grp_Need Check], Measure.[Const Grp_Prod Qty], Measure.[Const Grp_Product Group], Measure.[Const Grp_Project], Measure.[Const Grp_Reason], Measure.[Const Grp_Refer Time], Measure.[Const Grp_Startdate], Measure.[Const Grp_To Site], Measure.[Const Grp_To Site Name], Measure.[Const Grp_Year]}) on column;

  - df_in_item :
        -- 변경 2024.09.06
        -- input Query : 변경 2024.11.13
        Select ( [Version].[Version Name]
        * [Item].[Product Group]
        * [Item].[Definition]
        * [Item].[Project]
        * [Item].[Marketing Name]
        * [Item].[Inch]
        * [Item].[Year]
        * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[BOD Item_Asn],Measure.[BOD Item_Cur Status],Measure.[BOD Item_Eff Enddate],Measure.[BOD Item_Eff Startdate],Measure.[BOD Item_BOD LT],Measure.[BOD Item_Priority],Measure.[BOD Item_Shipment LT]}) on column
        where {Measure.[BOD Item_Asn] == 1, coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()};

        -- IBPL쿼리(테스트 실행) : (SET) 변경 2024.11.14
        Select ( &CWVUI
        * [Item].[Product Group]
        * [Item].[Definition]
        * [Item].[Project]
        * [Item].[Marketing Name]
        * [Item].[Inch]
        * [Item].[Year]
        * &SETItem * &MFStageSETLocation * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[BOD Item_Asn],Measure.[BOD Item_Cur Status],Measure.[BOD Item_Eff Enddate],Measure.[BOD Item_Eff Startdate],Measure.[BOD Item_BOD LT],Measure.[BOD Item_Priority],Measure.[BOD Item_Shipment LT]}) on column
        where {coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()};

        -- IBPL쿼리(테스트 실행) : (LCM) 변경 2024.11.14 추가
        Select ( &CWVUI * &LCMItem * &MFStageLCMLocation * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
        ({Measure.[BOD Item_Asn],Measure.[BOD Item_Cur Status],Measure.[BOD Item_Eff Enddate],Measure.[BOD Item_Eff Startdate],Measure.[BOD Item_BOD LT],Measure.[BOD Item_Priority],Measure.[BOD Item_Shipment LT]}) on column
        where {coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()};

* Output Table :
   - df_out_constGroupDetail :
   - df_out_constGroupDetail_W :
   - df_out_constGroupEcp :

* 테스트 스크립트
    EXEC plugin instance [PY_UI_ProductionConstApply] for measures {[Constraint Group Detail} using scope ( Version.[Version Name].[CurrentWorkingView] ) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

    * 실행되는지 테스트 필요 {fbVersion}}
    EXEC plugin instance [PY_UI_ProductionConstApply] for measures {[Constraint Group Detail} using scope ( &CWVUI ) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

    * /* APPLY 호출 (PY_UI_ProductionConstApply) */
    EXEC plugin instance [PY_UI_ProductionConstApply] for measures {[Const Grp Detail_From Site]} using scope ( Version.[Version Name]"{{fbVersion}}" * [Group].[Group ID].filter(#.[Name]=="{{fbGroupId}}")) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
    EXEC plugin instance [PY_UI_ProductionConstApply] for measures {[Const Grp Detail_From Site]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Group].[Group ID].filter(#.[Name]=="G1")) using arguments {(ExecutionMode, "LightWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

    /* APPLY 호출 (PY_UI_ProductionConstApply) */
    // group id 여러개 실행 (delete 버튼시 여러건 삭제) {{#filter fbGroupId}}  => .filter(#.[Name] in{"Group1","Group2","Group3"}
    - Measure.[Const Grp Detail W_Qty.Lock] 같이 Measure 의 속성을 input select 할때는 파이썬 실행 구문에서 "LightWeight" => "MediumWeight" 로 사용해야 함.
    EXEC plugin instance [PY_UI_ProductionConstApply] for measures {[Const Grp Detail_From Site]} using scope ( Version.[Version Name].[CurrentWorkingView] * [Group].[Group ID]{{#filter fbGroupId}}) using arguments {
      (ExecutionMode, "MediumWeight")
    , ("IncludeNullRows", "False")
    , (paramOutVersion , "CurrentWorkingView")
    , (MaxSliceTableCells, 200000000)
    , (MaxConcurrency, 1 )
    , ([Param.o9_sys_log_level], "DEBUG")
};
    // JS 에서 호출시
    EXEC plugin instance [PY_UI_ProductionConstApply] for measures {[Const Grp Detail_From Site]}using scope ( Version.[Version Name].Filter(#.Name in { "'+ fbVersion +'" }) * [Group].[Group ID].Filter(#.Name in { '+ fbGroupId_arr +' }) )
    using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };

    // IBPL 실행구문
    EXEC plugin instance [PY_UI_ProductionConstApply] for measures {[Const Grp Detail_From Site]} using scope ( Version.[Version Name].Filter(#.Name in { "CurrentWorkingView" }) * [Group].[Group ID].Filter(#.Name in { "MFC_S_00002","MFC_S_00003" }) ) using arguments {
      (ExecutionMode, "MediumWeight")
    , ("IncludeNullRows", "False")
    // , (paramOutVersion , "CurrentWorkingView")
    , (MaxSliceTableCells, 200000000)
    , (MaxConcurrency, 1 )
    , ([Param.o9_sys_log_level], "DEBUG")
};

"""
########################################################################################################################
# NSCMCommon - start
########################################################################################################################
import datetime
import pandas as pd
import numpy as np
import os
import time
import traceback
import warnings
import tracemalloc
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
########################################################################################################################
# NSCMCommon - end
########################################################################################################################

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_ProductionConstApply'

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 공통 함수 정의
########################################################################################################################
def fn_get_str(val):
    try:
        if (type(val) is str):
            return val
        elif (type(val) is float):
            if (pd.isna(val)):
                return ""
            else:
                return str(val)
        elif (type(val) is bool):
            if val:
                return "True"
            else:
                return "False"
        elif pd.isna(val):
            return ""
        else:
            return str(val)
    except Exception as e:
        logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    return ""

def fn_nvl(val1:str, val2:str):
    if "".__eq__(val1) or pd.isna(val1) :
        return val2
    else:
        return val1

def fn_getCisValue(cisAttrValues: str, cisId: str):
    cisAttbs = cisAttrValues.split("^")

    for i in range(len(cisAttbs)):
        cisAttb = cisAttbs[i].split("::")
        if (cisId.__eq__(cisAttb[0])):
            return cisAttb[1]

    return ""

def fn_note(note:str):
    if "Y".__eq__(pDetailLogFlag):
        logger.Note(p_note="====================> " + note, p_log_level=common.G_log_level.debug())

def fn_concat(value1:str, value2:str):
    if value1 == np.nan or "".__eq__(value1):
        return value2
    else:
        return value1 + "," + value2

########################################################################################################################
# logic start
########################################################################################################################
try:

    # Batch 시작
    if common.gfn_get_isLocal():
        vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), os.path.dirname(__file__))
    else:
        vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), "")

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    ################################################################################################################
    # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP1 Start')

    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 로컬일 경우 버전 처리
    # 데이터 파일 읽기
    if common.gfn_get_isLocal():

        df_in_week = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_week.csv", encoding="UTF-8")
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_item.csv", encoding="UTF-8")
        df_in_constGroup = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_constGroup.csv", encoding="UTF-8")

        outVersionName = "CWV_MP"
        pDetailLogFlag = "N"

    # 입력 변수 확인용 로그
    vdCommon.gfn_saveDf(df_in_constGroup, "df_in_constGroup", True)
    vdCommon.gfn_saveDf(df_in_week, "df_in_week", True)
    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)

    vdCommon.gfn_stepLog('=====> STEP2 End')

    ################################################################################################################
    # STEP 2 : DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수 선언 - Dimension
    vdCommon.gfn_stepLog('=====> STEP2 Start')
    VersionName = 'Version.[Version Name]'
    GroupID = 'Group.[Group ID]'
    Seq = 'Sequence.[Sequence]'
    TimeWeek = 'Time.[Week]'
    # TimeMonth = 'Time.[Month]'
    TimeMonth = 'Time.[Planning Month]'                 # 2025.01.03 추가
    TimePartialWeek = 'Time.[Partial Week]'
    Item = 'Item.[Item]'
    ItemProductGroup = 'Item.[Product Group]'
    ItemDefinition = 'Item.[Definition]'
    ItemProject = 'Item.[Project]'
    ItemMarketingName = 'Item.[Marketing Name]'
    ItemInch = 'Item.[Inch]'
    ItemYear = 'Item.[Year]'
    # df_in_item 의 가져오는 Measure Group 변경 2024.09.06
    Location = 'Location.[Location]'  # BODFromSiteID
    SubLocation = 'Sub Location.[Sub Location]' # BODToSiteID
    # 컬럼 변수 선언 - Constraint Group (Measure Group)
    ConstGrpStartdate = 'Const Grp_Startdate'
    ConstGrpEnddate = 'Const Grp_Enddate'
    ConstGrpReferTime = 'Const Grp_Refer Time'
    ConstGrpProdQty = 'Const Grp_Prod Qty'
    ConstGrpFromSite = 'Const Grp_From Site'
    ConstGrpFromSiteName = 'Const Grp_From Site Name'
    ConstGrpToSite = 'Const Grp_To Site'
    ConstGrpToSiteName = 'Const Grp_To Site Name'
    ConstGrpItem = 'Const Grp_Item'
    ConstGrpProductGroup = 'Const Grp_Product Group'
    ConstGrpDesc = 'Const Grp_Desc'
    ConstGrp_Definition = 'Const Grp_Definition'
    ConstGrp_Project = 'Const Grp_Project'
    ConstGrp_MktName = 'Const Grp_Mkt Name'
    ConstGrp_Inch = 'Const Grp_Inch'
    ConstGrp_Year = 'Const Grp_Year'

    # 컬럼 변수 선언 - Constraint Group Detail (Measure Group)
    ConstGrpDetailDesc = 'Const Grp Detail_Desc'
    ConstGrpDetailFromSite = 'Const Grp Detail_From Site'
    ConstGrpDetailFromSiteName = 'Const Grp Detail_From Site Name'  ## 2024.08.27 add
    ConstGrpDetailItem = 'Const Grp Detail_Item'
    ConstGrpDetailProductGroup = 'Const Grp Detail_Product Group'
    ConstGrpDetailToSite = 'Const Grp Detail_To Site'
    ConstGrpDetailToSiteName = 'Const Grp Detail_To Site Name'  ## 2024.08.27 add

    # 컬럼 변수 선언 - Constraint Group Detail W (Measure Group)
    ConstGrpDetailWQty = 'Const Grp Detail W_Qty'
    ConstGrpDetailWLockFlag = 'Const Grp Detail W_Lock Flag'

    # 컬럼 변수 선언 - Constraint Group Ecp (Measure Group)
    ConstGrpEcpFlag = 'Const Grp Ecp_Flag'

    # MPHorizon의 시작주차
    StartWeek = ''
    # MPHorizon의 종료주차
    EndWeek = ''
    # 무한대 수량 999999 InfinityQty = 999999 => 무한대 null 로 변경 2025.04.25 (노보람p 요청)
    InfinityQty = np.nan

    vdCommon.gfn_stepLog('=====> STEP2 End')
    ################################################################################################################
    # STEP 3 :  Constraint Group Detail : Measure Group 을 생성
    #           - Constraint Group : Measure Group 을 가져와 Start/End Date 에 값이 있는것만 Filtering
    #           - Group ID 의 첫번째 행 기준으로 Distinct
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP3 Start')

    ## MPHorizon의 시작주차와 마지막 주차 구하기
    df_findWeek = df_in_week.copy()
    df_findWeek[TimeWeek] = df_findWeek[TimeWeek].astype(int)   # 정수형 변환
    StartWeek = str(df_findWeek[TimeWeek].min())
    EndWeek = str(df_findWeek[TimeWeek].max())

    # null 인 경우 '' 처리 시작주차와 마지막 주차를 넣어준다.
    df_in_constGroup[ConstGrpStartdate] = df_in_constGroup[ConstGrpStartdate].fillna(StartWeek)
    df_in_constGroup[ConstGrpEnddate] = df_in_constGroup[ConstGrpEnddate].fillna(EndWeek)
    # vdCommon.gfn_saveDf(df_in_constGroup, "df_in_constGroup_before", True)

    # start/end Date 컬럼을 object 로 변경
    # NaN 이 포함된 float 값을 정수형 => 문자열로 변환
    df_in_constGroup[ConstGrpStartdate] = df_in_constGroup[ConstGrpStartdate].apply(lambda x: str(int(x)) if pd.notna(x) else '')
    df_in_constGroup[ConstGrpEnddate] = df_in_constGroup[ConstGrpEnddate].apply(lambda x: str(int(x)) if pd.notna(x) else '')

    # vdCommon.gfn_saveDf(df_in_constGroup, "df_in_constGroup_after", True)

    filtered_df = df_in_constGroup.copy()
    # vdCommon.gfn_saveDf(filtered_df, "filtered_df", True)

    # 필터링한 데이타가 있는 경우에만 로직 수행
    # 데이터 없는 경우 처리 로직을 어떻게 할지??
    if not filtered_df.empty:

        df_in_constGroup_copy = filtered_df.copy()
        # Group ID 별로 그룹화
        # Group ID, Prod Qty 를 제외한 나머지 컬럼
        other_columns = df_in_constGroup_copy.columns.difference([GroupID, ConstGrpProdQty])
        # id 별로 qty는 max 하고, 나머지 컬럼은 첫번째 값 유지
        df_in_constGroup_copy = df_in_constGroup_copy.groupby(GroupID).agg({**{col: 'first' for col in other_columns},  # 다른 컬럼들은 첫 번째값 유지
                                        ConstGrpProdQty: 'max'  # prod qty 는 sum,max
                                        }).reset_index()

        # GroupID, Seq 별 data로 각각의 주차 데이터 만들기 위한 Main
        df_in_constGroup_temp = filtered_df.copy()

        df_out_constGroupDetail = df_in_constGroup_copy.copy()
        vdCommon.gfn_saveDf(df_out_constGroupDetail, "df_out_constGroupDetail_groupby", True)

        # sequence가 없이 Group ID 별 DataFrame : Const Ecp 에서 사용
        df_constEcp = df_out_constGroupDetail.copy()

        # 시리즈인 경우 dataFrame 으로 변환
        if isinstance(df_out_constGroupDetail, pd.Series):
            # # data 가 1건일 경우 시리즈를 데이타프레임으로 변환
            df_out_constGroupDetail = pd.DataFrame(df_out_constGroupDetail).transpose()

        # 컬럼명 재정의
        df_out_constGroupDetail.rename(
            columns={ConstGrpDesc: ConstGrpDetailDesc, ConstGrpFromSite: ConstGrpDetailFromSite, ConstGrpFromSiteName: ConstGrpDetailFromSiteName
                    , ConstGrpItem: ConstGrpDetailItem, ConstGrpProductGroup: ConstGrpDetailProductGroup
                    , ConstGrpToSite : ConstGrpDetailToSite , ConstGrpToSiteName : ConstGrpDetailToSiteName},
            inplace=True)

        # output : df_out_constGroupDetail 필요 컬럼 정의
        df_out_constGroupDetail = df_out_constGroupDetail[[GroupID, VersionName, ConstGrpDetailDesc, ConstGrpDetailFromSite, ConstGrpDetailFromSiteName,
                                                           ConstGrpDetailItem, ConstGrpDetailProductGroup, ConstGrpDetailToSite, ConstGrpDetailToSiteName
                                                           ]]
        ################################################################################################################
        # 최종 Output 테이블 만들기 1 : df_out_constGroupDetail
        ################################################################################################################
        vdCommon.gfn_saveDf(df_out_constGroupDetail, "df_out_constGroupDetail", True)

        vdCommon.gfn_stepLog('=====> STEP3 End')

        ################################################################################################################
        # STEP 4 :  df_in_week 에 'week_type' 홀수,짝수 구분 만들어 컬럼 생성
        #                           'month_week' 월별 첫주, 마지막주 구분 만들어 컬럼 생성
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP4 Start')

        # 주차 문자열로 형 변환
        df_in_week[TimeWeek] = df_in_week[TimeWeek].astype(object).astype(str)

        # 홀수, 짝수 주차 구분
        df_in_week['week_type'] = df_in_week[TimeWeek].apply(lambda week: 'odd' if int(week[-2:]) % 2 != 0 else 'even')

        # 월별 첫주차
        first_week = df_in_week.groupby(TimeMonth).first().reset_index()
        # 월별 마지막주차
        last_week = df_in_week.groupby(TimeMonth).last().reset_index()
        first_week_dict = dict(zip(first_week[TimeMonth], first_week[TimeWeek]))
        last_week_dict = dict(zip(last_week[TimeMonth], last_week[TimeWeek]))

        df_in_week['month_week'] = df_in_week.apply( lambda row: 'first' if row[TimeWeek] == first_week_dict[row[TimeMonth]]
                                                                         else ('last' if row[TimeWeek] == last_week_dict[row[TimeMonth]] else None)
                                                     , axis=1)
        df_in_week = df_in_week[[TimeMonth, TimeWeek, 'week_type', 'month_week']]

        # 중복행 제거(일별 => 주차별로)
        df_in_week = df_in_week.drop_duplicates(subset=[TimeMonth, TimeWeek], keep='first', inplace=False).copy()
        # vdCommon.gfn_saveDf(df_in_week, "df_in_week__week", True)
        vdCommon.gfn_stepLog('=====> STEP4 End')
        ################################################################################################################
        # STEP 5 :  Constraint Group Detail W (Measure Group) 생성
        #           - Group ID 별 주차를 만든다. (Constraint Group Detail(Measure Group)과 Time.[Week] 를 merge
        #           - Start/End Date 볌위의 Time.[Week] Filtering
        #           - Constraint Group Detail W 의 Model Store Path(Const Grp Detail W_Qty.Lock) 속성 컬럼을 가져와 N(False) 인 주차의 Qty 만 Filtering
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP5 Start')
        # main df 와 week df key를 만들어 merge 한다.

        # Group ID별(org)
        # df_merge = pd.merge(df_in_constGroup_copy.assign(temp_key=1), df_in_week.assign(temp_key=1), on='temp_key').drop('temp_key', axis=1)
        # start, end date 의 주차만큼 Time.Week 범위를 만든다.

        # Group ID, Seq 별(2025.01.02)  ----------------test
        df_merge = pd.merge(df_in_constGroup_temp.assign(temp_key=1), df_in_week.assign(temp_key=1),
                            on='temp_key').drop('temp_key', axis=1)
        # vdCommon.gfn_saveDf(df_merge, "df_merge_______________________0425", True)
        ################################################################################################################
        # 원 소스 ( 2024.12.18 )
        # df_mergeQuery = df_merge.loc[(df_merge[ConstGrpStartdate] <= df_merge[TimeWeek]) & (df_merge[ConstGrpEnddate] >= df_merge[TimeWeek])].copy()
        ################################################################################################################

        ################################################################################################################
        # - o9버그 해결되면 사용 안해도 됨. ( 2024.12.18 ) # 첫주차 데이터 넣기 위함(임시) 2024.12.18
        # Horizon 의 첫 주차에 Data가 있어야 UI의 MDP 영역에 데이터 조회가 됨 (임시사용)
        df_merge['sMinWeek'] = StartWeek
        # df_merge['flag'] = False
        # df_merge.loc[(df_merge[ConstGrpStartdate] <= df_merge[TimeWeek]) & (df_merge[ConstGrpEnddate] >= df_merge[TimeWeek]), 'flag'] = True
        # df_merge.loc[(~((df_merge[ConstGrpStartdate] <= df_merge[TimeWeek]) & (
        #             df_merge[ConstGrpEnddate] >= df_merge[TimeWeek]))) & (
        #                          df_merge['sMinWeek'] == StartWeek), 'flag'] = False
        # df_mergeQuery = df_merge.loc[
        #     ((df_merge[ConstGrpStartdate] <= df_merge[TimeWeek]) & (df_merge[ConstGrpEnddate] >= df_merge[TimeWeek]))
        #     | (df_merge['flag'] == False)
        #     ].copy()

        df_merge['flag'] = 0
        df_merge['flag'] = np.where(df_merge[TimeWeek] == df_merge['sMinWeek'], 1,0) # start week 와 horizon 의 첫주차 표시
        # vdCommon.gfn_saveDf(df_merge, "df_merge", True)

        df_merge.loc[(df_merge[ConstGrpStartdate] <= df_merge[TimeWeek]) & (df_merge[ConstGrpEnddate] >= df_merge[TimeWeek]), 'flag'] = 2   # start ~ end week 범위안 data
        # df_merge.loc[(~((df_merge[ConstGrpStartdate] <= df_merge[TimeWeek]) & (df_merge[ConstGrpEnddate] >= df_merge[TimeWeek]))) & (df_merge['sMinWeek'] == StartWeek), 'flag'] = 2
        # 첫주차 & start~end 의 주차
        df_mergeQuery = df_merge.loc[(df_merge['flag'] == 1) | (df_merge['flag'] == 2)].copy()
        ################################################################################################################
        # vdCommon.gfn_saveDf(df_mergeQuery, "df_mergeQuery_before", True)
        vdCommon.gfn_stepLog('=====> STEP5 End')
        ################################################################################################################
        # STEP 5-1 :  Ref.Time ( Const Grp_Refer Time ) 에 따른 Qty 세팅
        #           - Even W  (Even Week)  : 짝수주차에만 Production QTY 값 입력. 나머지는 0으로 입력. 엔진은 무한대로 해석
        #           - Odd W   (Odd Week)   : 홀수주차에만 Production QTY 값 입력. 나머지는 0으로 입력. 엔진은 무한대로 해석
        #           - Every W (every week) : start~end 사이 모든주차에 qty 입력
        #           - 1st W   (1st Week)   : 월별 첫번째주차에만 Production QTY 값 입력. start 가 월중 이면, start의 월은 0, 차월의 첫주부터 값~
        #           - Last W  (last Week)  : 1st 와 동일. 월별 마지막주차.
        #           - null       : 사용자 정의 안함 ( 차후 정의 필요 )
        #           ** 월별의 첫주차, 마지막 주차가 겹칠 경우는??  6월의 마지막주차가 7월에 첫주차가 될수 있음 ( Partial )
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP5-1 Start')
        conditions = [
              # (df_mergeQuery['flag'] == False)  # 첫주차 데이터 넣기 위함(임시) 2024.12.18
              (df_mergeQuery['flag'] == 1)  # 첫주차 데이터 넣기 위함(임시) 2024.12.18
            , ((df_mergeQuery[ConstGrpReferTime] == 'Even W') & (df_mergeQuery['week_type'] == 'even'))
            , ((df_mergeQuery[ConstGrpReferTime] == 'Odd W') & (df_mergeQuery['week_type'] == 'odd'))
            , ((df_mergeQuery[ConstGrpReferTime] == '1st W') & (df_mergeQuery['month_week'] == 'first'))
            , ((df_mergeQuery[ConstGrpReferTime] == 'Last W') & (df_mergeQuery['month_week'] == 'last'))
            , (df_mergeQuery[ConstGrpReferTime] == 'Every W')
            ,
        ]

        choices = [
              np.nan    # 첫주차 데이터 넣기 위함(임시) 2024.12.18
            , df_mergeQuery[ConstGrpProdQty]
            , df_mergeQuery[ConstGrpProdQty]
            , df_mergeQuery[ConstGrpProdQty]
            , df_mergeQuery[ConstGrpProdQty]
            , df_mergeQuery[ConstGrpProdQty]
        ]
        # 제약반영 구간(Start~End date) 이외는 무한대 설정
        # 위의 조건이 아닌 경우 999999 (무한대) 로 설정
        df_mergeQuery[ConstGrpProdQty] = np.select(conditions, choices, default = InfinityQty)
        # df_mergeQuery[ConstGrpProdQty] = np.select(conditions, choices) # 2025.04.25 이전, 차후 무한대(숫자) 설정시 사용

        df_Detail_W = df_mergeQuery.copy()
        # 컬럼명 재정의 (Const Qty => Detail W_Qty 로 변경)
        df_Detail_W.rename(columns={ConstGrpProdQty: ConstGrpDetailWQty}, inplace=True)

        # output : df_out_constGroupDetail_W 필요 컬럼 정의
        # df_Detail_W[ConstGrpDetailWLockFlag] = False
        # df_Detail_W = df_Detail_W[[GroupID, VersionName, TimeWeek, ConstGrpDetailWLockFlag, ConstGrpDetailWQty]]

        df_Detail_W = df_Detail_W[[GroupID, VersionName, TimeWeek, ConstGrpDetailWQty, 'flag']]

        # df_Detail_W.groupby([GroupID, VersionName, TimeWeek]).agg(Qty=(ConstGrpDetailWQty, 'sum')).reset_index()  # Qty 컬럼에 sum(ConstGrpDetailWQty)

        # 추가로직 2025.01.02
        # 그룹화 및 집계
        #=====================================> 집계하다가.. null , 0 일 경우
        #=====================================> null 에 999999 -> null 로 변경 2025.04.25
        result = (
            # df_Detail_W.groupby([GroupID, VersionName, TimeWeek], as_index=False).agg(Qty=(ConstGrpDetailWQty,'sum'))   #  Qty 컬럼에 sum(ConstGrpDetailWQty)

            # Qty 컬럼에 sum(ConstGrpDetailWQty) > nan 값을 제외한 값들만 합산 (최소 숫자값이 있는 경우만 sum)
            df_Detail_W.groupby([GroupID, VersionName, TimeWeek], as_index=False).agg(Qty=(ConstGrpDetailWQty, lambda x: x.sum(min_count=1)))
        )
        # vdCommon.gfn_saveDf(result, "result", True)
        # 원래 'flag' 결과 병합
        df_Detail_W = result.merge(df_Detail_W[[GroupID, VersionName, TimeWeek, 'flag']].drop_duplicates(), on=[GroupID, VersionName, TimeWeek], how='left')
        # vdCommon.gfn_saveDf(df_Detail_W, "df_Detail_W_merge_________________0425", True)

        # Horizon 기간 중 기본값 세팅(InfinityQty = 999,999) qty = nan 일 경우
        # df_Detail_W.loc[(df_Detail_W['flag'] == 2) & (df_Detail_W['Qty'].isna()), 'Qty'] = InfinityQty    ## 주석처리 , 무한대 null 로 변경 2025.04.25 (노보람p 요청) - 차후 무한대 설정값 필요시 사용

        # vdCommon.gfn_saveDf(df_Detail_W, "df_Detail_W_InfinityQty________________0425", True)
        df_Detail_W.rename(columns={'Qty': ConstGrpDetailWQty}, inplace=True)   # 컬럼명 변경(Qty=>ConstGrpDetailWQty)
        df_Detail_W[ConstGrpDetailWLockFlag] = False
        df_Detail_W[ConstGrpDetailWQty].astype('Int64')  # 정수형 변환 ( Int64 의 대문자 I 는 NaN 을 허용하는 정수 타입 )

        # vdCommon.gfn_saveDf(df_Detail_W, "df_Detail_W__groupby__sum", True)

        df_out_constGroupDetail_W = df_Detail_W.copy()
        df_out_constGroupDetail_W = df_out_constGroupDetail_W[[GroupID, VersionName, TimeWeek, ConstGrpDetailWLockFlag, ConstGrpDetailWQty]]

        ################################################################################################################
        # 최종 Output 테이블 만들기 2 : df_out_constGroupDetail_W
        ################################################################################################################
        vdCommon.gfn_saveDf(df_out_constGroupDetail_W, "df_out_constGroupDetail_W", True)

        vdCommon.gfn_stepLog('=====> STEP5-2 End')
        ################################################################################################################
        # STEP 6 :  Constraint Group Ecp (Measure Group) 생성
        #           - Group ID 별 Item 생성
        ################################################################################################################
        # 필요한 컬럼만 생성하기
        df_constEcp = df_constEcp.fillna('').astype(str)  # Null 을 공백으로 채우기
        # df_constEcp = df_constEcp.astype(str)
        df_constEcp = df_constEcp[[VersionName, GroupID, ConstGrpFromSite, ConstGrpToSite, ConstGrpProductGroup
            , ConstGrp_Definition, ConstGrp_Project, ConstGrp_MktName, ConstGrp_Inch, ConstGrp_Year, ConstGrpItem]]

        ################################################################################################################
        # STEP 6-1 : Const.Group 의
        # Measure.[Const Grp_Item] == 'All' 이면, From Site ID와 To Site ID 가 동일한 Item 을 모두 가져온다.
        # - From site 는 1건, To Site 는 multi건 존재할수 있음
        # Measure.[Const Grp_Item] == 'WMN%' 이면(문자열 끝에 '%') ,  From Site ID와 To Site ID 가 동일한 Item 중 Like 필터링 하여 가져온다.
        # Measure.[Const Grp_Item] == 'All' 아니고 '%' 도 없으면 From Site ID와 To Site ID 가 동일한 Item 중 equal 로 필터링 하여 가져온다.
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP6-1 Start')
        # 필요한 컬럼만 생성하기
        df_in_item = df_in_item.fillna('').astype(str)
        df_in_item = df_in_item[[VersionName, Location, SubLocation, ItemProductGroup, ItemDefinition, ItemProject, ItemMarketingName, ItemInch, ItemYear, Item]]
        # Item 중복행 제거
        df_in_item = df_in_item.drop_duplicates(subset=[VersionName, Location, SubLocation, ItemProductGroup, ItemDefinition, ItemProject, ItemMarketingName, ItemInch, ItemYear, Item], keep='first',inplace=False).copy()

        # df_constEcp 의 컬럼을 df_in_item 으로 컬럼명을 맞춘다. (Location, Sub Location, Item)
        df_constEcp.rename(columns={ConstGrpFromSite: Location, ConstGrpToSite: SubLocation, ConstGrpItem: Item}, inplace=True)

        # 'Sub Location', 'Item' , 'Item의 Attb' 필터 전처리
        df_constEcp['sub_list'] = df_constEcp[SubLocation].apply(lambda x:None if x.upper() == "ALL" else x.split("^"))
        df_constEcp['item_list'] = df_constEcp[Item].apply(lambda x:None if x.upper() == "ALL" else x.split("^"))
        df_constEcp['productGroup_list'] = df_constEcp[ConstGrpProductGroup].apply(lambda x: None if x.upper() == "ALL" else x.split("^"))
        df_constEcp['Definition_list'] = df_constEcp[ConstGrp_Definition].apply(lambda x: None if x.upper() == "ALL" else x.split("^"))
        df_constEcp['Project_list'] = df_constEcp[ConstGrp_Project].apply(lambda x: None if x.upper() == "ALL" else x.split("^"))
        df_constEcp['Mark_list'] = df_constEcp[ConstGrp_MktName].apply(lambda x: None if x.upper() == "ALL" else x.split("^"))
        df_constEcp['Inch_list'] = df_constEcp[ConstGrp_Inch].apply(lambda x: None if x.upper() == "ALL" else x.split("^"))
        df_constEcp['Year_list'] = df_constEcp[ConstGrp_Year].apply(lambda x: None if x.upper() == "ALL" else x.split("^"))

        # 필터링 함수
        def filter_data(row):
            loc_filter = df_in_item[Location] == row[Location]    # Location 동일한 것만.

            # Sub Location 필터
            if row["sub_list"] is None: # 'ALL'
                sub_filter = np.ones(len(df_in_item), dtype=bool) # 모든 값 포함
            else:
                sub_filter = df_in_item[SubLocation].isin(row["sub_list"])

            # Item.Product Group 필터
            if row["productGroup_list"] is None:  # 'ALL'
                productGroup_filter = np.ones(len(df_in_item), dtype=bool)  # 모든 값 포함
            else:
                productGroup_filter = df_in_item[ItemProductGroup].isin(row["productGroup_list"])

            # Item.Definition 필터
            if row["Definition_list"] is None:  # 'ALL'
                Definition_filter = np.ones(len(df_in_item), dtype=bool)  # 모든 값 포함
            else:
                Definition_filter = df_in_item[ItemDefinition].isin(row["Definition_list"])

            # Item.Project 필터
            if row["Project_list"] is None:  # 'ALL'
                Project_filter = np.ones(len(df_in_item), dtype=bool)  # 모든 값 포함
            else:
                Project_filter = df_in_item[ItemProject].isin(row["Project_list"])

            # Item.Marketing Name 필터
            if row["Mark_list"] is None:  # 'ALL'
                Mark_filter = np.ones(len(df_in_item), dtype=bool)  # 모든 값 포함
            else:
                Mark_filter = df_in_item[ItemMarketingName].isin(row["Mark_list"])

            # Item.Inch Name 필터
            if row["Inch_list"] is None:  # 'ALL'
                Inch_filter = np.ones(len(df_in_item), dtype=bool)  # 모든 값 포함
            else:
                Inch_filter = df_in_item[ItemInch].isin(row["Inch_list"])

            # Item.Year Name 필터
            if row["Year_list"] is None:  # 'ALL'
                Year_filter = np.ones(len(df_in_item), dtype=bool)  # 모든 값 포함
            else:
                Year_filter = df_in_item[ItemYear].isin(row["Year_list"])

            # Item 필터
            if row["item_list"] is None: # 'ALL'
                item_filter = np.ones(len(df_in_item), dtype=bool) # 모든 값 포함
            else:
                pattern = "|".join([item.replace("%", ".").upper() for item in row["item_list"]])
                item_filter = df_in_item[Item].str.contains(pattern, regex=True)

            # 최종 필터 , Group ID 추가
            return df_in_item[loc_filter & sub_filter & productGroup_filter & Definition_filter & item_filter
                                & Project_filter & Mark_filter & Inch_filter & Year_filter].assign(id=row[GroupID]).rename(columns={"id":GroupID})

        # 백터화 적용
        result_df = pd.concat([filter_data(row) for _, row in df_constEcp.iterrows()], ignore_index=True)

        if not result_df.empty:
            # 정렬 : id, loc, sub, item 순으로
            result_df = result_df.sort_values(by=[GroupID, Location, SubLocation, Item]).reset_index(drop=True)
            # 중복 Data 삭제
            result_df = result_df.drop_duplicates(subset=[VersionName, GroupID, Item], keep='first', inplace=False).copy()

        # Const.Group Ecp 컬럼 생성
        df_out_constGroupEcp = result_df.copy()
        df_out_constGroupEcp = df_out_constGroupEcp[[GroupID, VersionName, Item]]

        if not df_out_constGroupEcp.empty:
            df_out_constGroupEcp[ConstGrpEcpFlag] = False

        ################################################################################################################
        # 최종 Output 테이블 만들기 3 : df_out_constGroupEcp
        ################################################################################################################
        vdCommon.gfn_saveDf(df_out_constGroupEcp, "df_out_constGroupEcp", True)

        vdCommon.gfn_stepLog('=====> STEP6-1 End')

    else:
        # 빈 데이터프레임 만들기
        df_out_constGroupDetail = pd.DataFrame(columns=[GroupID, VersionName, ConstGrpDetailDesc, ConstGrpDetailFromSite, ConstGrpDetailFromSiteName, ConstGrpDetailItem, ConstGrpDetailProductGroup, ConstGrpDetailToSite, ConstGrpDetailToSiteName])
        df_out_constGroupDetail_W = pd.DataFrame(columns=[GroupID, VersionName, TimeWeek, ConstGrpDetailWLockFlag, ConstGrpDetailWQty])
        df_out_constGroupEcp = pd.DataFrame(columns=[GroupID, VersionName, Item])
        logger.Step(p_step_no=900, p_step_desc=f'DataFrame Empty Create')

    ################################################################################################################
    # 최종 Output 테이블 만들기
    ################################################################################################################
    # if common.gfn_get_isLocal():
    #     logger.Step(p_step_no=300, p_step_desc=f'Final Output Table create')
    #     vdCommon.gfn_saveDf(df_out_constGroupDetail, "df_out_constGroupDetail", True)
    #     vdCommon.gfn_saveDf(df_out_constGroupDetail_W, "df_out_constGroupDetail_W", True)
    #     vdCommon.gfn_saveDf(df_out_constGroupEcp, "df_out_constGroupEcp", True)

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    # ouput Table 선언
    df_out_constGroupDetail = pd.DataFrame([], columns=[])
    df_out_constGroupDetail_W = pd.DataFrame([], columns=[])
    df_out_constGroupEcp = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    vdCommon.gfn_stepLog('=====> Batch end')


