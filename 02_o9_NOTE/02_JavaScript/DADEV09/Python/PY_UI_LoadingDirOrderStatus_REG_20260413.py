"""
* 프로그램명
    - PY_UI_LoadingDirOrderStatus_REG.py
* 내용
    - 입력에 대한 해당 정보를 Loading Order Mgmt화면 값으로 입력해줌
    - 단 이 시점에서, From Site ID와, PROD WK값을 계산해서 넣어주고,
      옆의 로직을 통해 계산된 결과값을 아래 메저에 반영해줌
      1. From Site(Loading Order Upload_From Site)
      2. 화면 컨셉변경으로 Upload화면에서 Prod WK는 삭제하고, Adj Prod Wk가 됩니다. 같게 반영함
        PROD WK(Loading Order Upload_Prod Week)
        Adj PROD WK(Loading Order Upload_Adj Prod Week)
    - Org Qty=Adj Chk Qty는 같게 반영
        Org Qty(Loading Order Upload_Org Qty)
        Adj Chk Qty(Loading Order Upload_Chk Qty)
* 변경이력
    - 2025.05.10 / soonupjee / Create
    - 2025.05.20 / soonupjee / Modified
                 Order Status의 grain에서 Seq.[Seq] 없애고 Ship To.[Ship To]로 변경
    - 2025.05.23 / soonupjee / Modified
                 Order Status의 grain에서 Ship To.[Ship To]를 Ship To.[Ship To Party]로 재변경
                 ( Row 선택시 동일한 Attribute Name으로 인한 오류발생 )
    - 2025.06.18 / soonupjee / Modified
                 in_BOD_Lane_Item 에서  조건절의 Measure.[BOD Lane Item_Priority] == 1 를 제거하고,
                 내부로직에서  tot_leadTime이  작고, priority가 높은( 숫자로는 낮음 ) 것을 선택한다.
    - 2025.06.19 / soonupjee / Modified
                 To_Site_ID와  Item으로  From_Site_ID 구할경우, 중복이 발생하여,
                 in_Location을 추가하여  Location.[Location].filter(#.[FDC Site Flag]!=True)) 조건의
                 in_BOD_Lane_Item 만 구한다.
    - 2025.06.24 / soonupjee / Modified
                 in_BOD_Lane_Item 로직에서 From Site 중복이 발생하여,  From Site는  제외하고
                                         To Site와 Item 만으로 계산하도록 수정함.
    - 2025.06.26 / soonupjee / Modified
                 in_BOD_Lane_Item유효한 값이 없을경우, 날짜를 무시하고
* Flow Summary
    Step1.
        'Loading Order Status_RDD DATE'를 통해  BOD를 계산하여 Prod WK 산출하여 반영함(조건은 python 로직내 기술함)
        'Prod WK' => '최종 MGMT' Dimension의 'Time.[Week]'

        Step1-1 Order Status의  Item.[Item], Location.[Location] 과
                BODLaneItem의   Item.[Item], BOD.[To Site ID] 로    From Site ID 와 Total LeadTime 구함.
        Step1-2 out_LoadingDirMgmt 의  [Loading Order Status_RDD Date]와
                inTime                Time.[Day]  로    prod week 구함.
    Step2.
        Step2-1 out_LoadingDirMgmt 의  Loading Dir Order Mgmt_Cntr Type 채우기
        Step2-2 out_LoadingDirMgmt 의  Loading Dir Order Mgmt_Loading Type 채우기

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
- in_Loading_Order_Status
    Select ([Version].[Version Name] * [Ship To].[Ship To Party] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Ship To] * [Time].[Week] ) on row, ({Measure.[Loading Order Status_Org Qty], Measure.[Loading Order Status_RDD Date], Measure.[Loading Order Status_Sales Order], Measure.[Loading Order Status_SO Item]}) on column include memberproperties { [Ship To].[Ship To Party], [DisplayName]} where {Measure.[Loading Order Status_Chk Flag]=="Y",~isnull(Measure.[Loading Order Status_Confirmed By]),CurrentUser().[Name] startswith (Measure.[Loading Order Status_Confirmed By] + "@")};
    Select ([Version].[Version Name].[CWV_MP] *
            [Ship To].[Ship To Party] *
            [Item].[Item] * [Location].[Location] *
            [Sales Domain].[Ship To] *
            [Time].[Week]
    ) on row,
    ({
            Measure.[Loading Order Status_Org Qty],
            Measure.[Loading Order Status_RDD Date],
            Measure.[Loading Order Status_Sales Order],
            Measure.[Loading Order Status_SO Item]
    }) on column
    include memberproperties { [Ship To].[Ship To Party], [DisplayName]}
    where {Measure.[Loading Order Status_Chk Flag]=="Y",
           ~isnull(Measure.[Loading Order Status_Confirmed By]),
           CurrentUser().[Name] startswith (Measure.[Loading Order Status_Confirmed By] + "@")};

- in_BOD_Lane_Item
    Select ([Version].[Version Name] * [BOD].[From Site ID].filter(#.[From Site ID Type]=="MF") * [BOD].[To Site ID] * [Item].[Item] * [BOD].[BOD Name]) on row, ({ Measure.[BOD Lane Item_Eff Startdate] , Measure.[BOD Lane Item_Eff Enddate] , Measure.[BOD Lane Item_Priority] , Measure.[BOD Lane Item_Shipping Leadtime] , Measure.[BOD Lane Item_Transit Time]}) on column where { (isNull(Measure.[BOD Lane Item_Eff Startdate]) || Measure.[BOD Lane Item_Eff Startdate] <= dateadd(Now(), 9, "hour")) && (isNull(Measure.[BOD Lane Item_Eff Enddate]) || Measure.[BOD Lane Item_Eff Enddate] >= dateadd(dateadd(Now(), 9, "hour"), 7*4, "day"))} orderby Measure.[BOD Lane Item_Eff Startdate];
    Select ([Version].[Version Name].[CWV_MP] *
            [BOD].[From Site ID].filter(#.[From Site ID Type]=="MF") * [BOD].[To Site ID] *
            [Item].[Item] * [BOD].[BOD Name]) on row,
           ({ Measure.[BOD Lane Item_Eff Startdate] , Measure.[BOD Lane Item_Eff Enddate] ,
              Measure.[BOD Lane Item_Priority] , Measure.[BOD Lane Item_Shipping Leadtime] ,
              Measure.[BOD Lane Item_Transit Time]}) on column
    where { (isNull(Measure.[BOD Lane Item_Eff Startdate]) || Measure.[BOD Lane Item_Eff Startdate] <= dateadd(Now(), 9, "hour")) &&
            (isNull(Measure.[BOD Lane Item_Eff Enddate]) || Measure.[BOD Lane Item_Eff Enddate] >= dateadd(dateadd(Now(), 9, "hour"), 7*4, "day"))}
    orderby Measure.[BOD Lane Item_Eff Startdate];

- in_BOD_Lane_Item_Invalid
    Select ([Version].[Version Name] * [BOD].[From Site ID].filter(#.[From Site ID Type]=="MF") * [BOD].[To Site ID] * [Item].[Item] * [BOD].[BOD Name]) on row, ({ Measure.[BOD Lane Item_Eff Startdate] , Measure.[BOD Lane Item_Eff Enddate] , Measure.[BOD Lane Item_Priority] , Measure.[BOD Lane Item_Shipping Leadtime] , Measure.[BOD Lane Item_Transit Time]}) on column where { ~((isNull(Measure.[BOD Lane Item_Eff Startdate]) || Measure.[BOD Lane Item_Eff Startdate] <= dateadd(Now(), 9, "hour")) && (isNull(Measure.[BOD Lane Item_Eff Enddate]) || Measure.[BOD Lane Item_Eff Enddate] >= dateadd(dateadd(Now(), 9, "hour"), 7*4, "day")))} orderby Measure.[BOD Lane Item_Eff Startdate];
    Select ([Version].[Version Name].[CWV_MP] *
            [BOD].[From Site ID].filter(#.[From Site ID Type]=="MF") * [BOD].[To Site ID] *
            [Item].[Item] * [BOD].[BOD Name]) on row,
           ({ Measure.[BOD Lane Item_Eff Startdate] , Measure.[BOD Lane Item_Eff Enddate] ,
              Measure.[BOD Lane Item_Priority] , Measure.[BOD Lane Item_Shipping Leadtime] ,
              Measure.[BOD Lane Item_Transit Time]}) on column
    where { ~((isNull(Measure.[BOD Lane Item_Eff Startdate]) || Measure.[BOD Lane Item_Eff Startdate] <= dateadd(Now(), 9, "hour")) &&
              (isNull(Measure.[BOD Lane Item_Eff Enddate]) || Measure.[BOD Lane Item_Eff Enddate] >= dateadd(dateadd(Now(), 9, "hour"), 7*4, "day")))}
    orderby Measure.[BOD Lane Item_Eff Startdate];

- in_Location
    SELECT  ([Location].[Location].filter(#.[FDC Site Flag]!=True) ) WHERE { [Location].[Location Type].[MF]};

########## Loading Type & Cntr Type을 위한 Method 마스터 테이블 input ##################################################
- in_Loading_Method_Ship_To
    Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Seq].[Seq] * [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To]) on row, ({Measure.[Loading Method Ship To_Ship To],Measure.[Loading Method Ship To_Default],Measure.[Loading Method Ship To_Valid Flag]}) on column;
    Select ([Version].[Version Name].[CWV_MP] *
            [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Seq].[Seq] *
            [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To]) on row,
           ({Measure.[Loading Method Ship To_Ship To],Measure.[Loading Method Ship To_Default],
             Measure.[Loading Method Ship To_Valid Flag]}) on column;

- in_Loading_Method_Account
    Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To] ) on row, ({Measure.[Loading Method Account_Default], Measure.[Loading Method Account_Valid Flag]}) on column;
    Select ([Version].[Version Name].[CWV_MP] *
            [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Location].[Location] *
            [Container].[ContainerID] * [Sales Domain].[Ship To] ) on row,
           ({Measure.[Loading Method Account_Default], Measure.[Loading Method Account_Valid Flag]}) on column;

- in_Loading_Method_To_Site
    Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] * [Loading Type].[Loading Type]) on row, ({Measure.[Loading Method To Site_Default], Measure.[Loading Method To Site_Valid Flag]}) on column;
    Select ([Version].[Version Name].[CWV_MP] *
            [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] *
            [Loading Type].[Loading Type]) on row,
           ({Measure.[Loading Method To Site_Default], Measure.[Loading Method To Site_Valid Flag]}) on column;

- in_Loading_Method_From
    Select ([Version].[Version Name]* [Loading Type].[Loading Type] * [Shipment Type].[Shipment Type] * [Sub Location].[Sub Location] * [Container].[ContainerID] ) on row, ({Measure.[Loading Method From Site_Default],  Measure.[Loading Method From Site_Valid Flag]}) on column;
    Select ([Version].[Version Name].[CWV_MP] *
            [Loading Type].[Loading Type] * [Shipment Type].[Shipment Type] * [Sub Location].[Sub Location] *
            [Container].[ContainerID] ) on row,
           ({Measure.[Loading Method From Site_Default],  Measure.[Loading Method From Site_Valid Flag]}) on column;

- in_Time
    Select ([Version].[Version Name] * [Time].[Week] * [Time].[Day]) on row, ({Measure.[Tact Time W_Tact Time]}) on column include memberproperties {[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};
    Select ([Version].[Version Name].[CWV_MP] *
            [Time].[Week] * [Time].[Day]) on row,
           ({Measure.[Tact Time W_Tact Time]}) on column
    include memberproperties {[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};

-in_Loading_Dir_Order_Mgmt
    Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item] * [Location].[Location] * [Sales Domain].[Account] * [Time].[Week] ) on row,({Measure.[Loading Dir Order Mgmt_Sales Order]}) on column orderby [Seq].[Seq].Key Desc limit 1;
    Select ([Version].[Version Name].[CWV_MP] *
            [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item] * [Location].[Location] *
            [Sales Domain].[Account] * [Time].[Week] ) on row,
           ({Measure.[Loading Dir Order Mgmt_Sales Order]}) on column
    orderby [Seq].[Seq].Key Desc limit 1;

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
EXEC plugin instance [PY_UI_LoadingDirOrderStatus_REG_Tst]
            for measures {[Loading Dir Order Mgmt_Sales Order]}
        using scope (&CWV_MP)
        using arguments {
                            (ExecutionMode, "MediumWeight")
                            , (Param_OUT_VERSION, "CWV_MP")
                            , (Param_User_Name, "{{fb_Param_User_Name}}")
                            , (MaxSliceTableCells, 200000000)
                            , (MaxConcurrency, 1 )
                            , (IncludeNullRows, False)
                            , ([Param.o9_sys_log_level], "DEBUG")
                        };

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
str_instance = "PY_UI_LoadingDirOrderStatus_REG"
str_input_dir = "Input/UILoadingDirOrderStatusREG"
str_output_dir = "Output/UILoadingDirOrderStatusREG"
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

@_decoration_
def fn_merge_inner_join(df_p_left: pd.DataFrame, df_p_right: pd.DataFrame, str_p_cond: str) -> pd.DataFrame:
    """
    merge 5 in_BOD_Lane_Item ['BOD.[From Site ID]과 in_Location ['Location.[Location]'] 기준 inner
    merge 1-1 in_loading_Order_Status과 in_BOD_Lane_Item을         Item.[Item], Location.[Location] 기준으로 Left Join, (데이터 필수)
          1-2 in_loading_Order_Status과 in_BOD_Lane_Item_Invalid을 Item.[Item], Location.[Location] 기준으로 Left Join, (데이터 필수)
    merge 2 merge 1-1의 'Prod Date'과 in_Time의 'Time.[Day]'기준 inner
   :param df_p_left: in_loading_Order_Status
   :param df_p_right: in_BOD_Lane_Item
   :param str_p_cond: merge  type
   :return: DataFrame
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]

    # Return 변수
    df_return = pd.DataFrame()

    # 입력으로 받은 테이블이 모두 비어 있는 경우 오류 처리
    if df_p_left.empty and df_p_right.empty:
        logger.Note(p_note=f'[{str_my_name}] 2개의 입력 테이블이 모두 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        raise Exception(f'Exception: 2개의 입력 테이블이 모두 비어 있습니다. : {str_my_name}')

    # 입력으로 받은 테이블 중 하나만 비어 있는 경우 데이터가 있는 입력 테이블을 반환
    if df_p_left.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_left)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
    if df_p_right.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_right)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())

    # 입력으로 받은 파라미터가 잘못된 경우 기본값으로 설정한다.
    if str_p_cond is None or str_p_cond.strip() == '':
        str_p_cond = '0'



    # Merge 기준 컬럼 설정
    if str_p_cond == '1':
        list_left_on = ['Item.[Item]', 'Location.[Location]']
        list_right_on = ['Item.[Item]', 'BOD.[To Site ID]']
        str_how = 'left'
    elif str_p_cond == '2':
        # Prod Date o9 DateTime이기때문에 Time.[Day] object타입과 join 오류 발생
#        df_p_left['Prod Date'] = df_p_left['Prod Date'].dt.strftime('%Y-%m-%d')
        # Mfg Plan_Planned Prod Date와 in_Time의 Time.Day를 키로 join 하여Time.[Week] 생성,
        list_left_on = ['Prod Date']
        list_right_on = ['Time.[Day]']
        str_how = 'inner'
    elif str_p_cond == '3':
        df_p_left['Loading Order Status_RDD Date'] = pd.to_datetime(df_p_left['Loading Order Status_RDD Date'])
        df_p_right['Time.[Day]'] = pd.to_datetime(df_p_right['Time.[Day]'])
        # RDD Date와 in_Time의 Time.Day를 키로 join 하여Time.[Week] 생성,
        list_left_on = ['Loading Order Status_RDD Date']
        list_right_on = ['Time.[Day]']
        str_how = 'inner'
    elif str_p_cond == '5':
        list_left_on = ['BOD.[From Site ID]']
        list_right_on = ['Location.[Location]']
        str_how = 'inner'
        df_p_left = df_p_left[ ( (pd.to_datetime(df_p_left['BOD Lane Item_Eff Startdate']) <= pd.Timestamp.today() + pd.Timedelta(hours=9))
                                |(df_p_left['BOD Lane Item_Eff Startdate'].isna() ))
                              &
                               ( (pd.to_datetime(df_p_left['BOD Lane Item_Eff Enddate']) >= pd.Timestamp.today() + pd.Timedelta(hours=9) + pd.Timedelta(days=28))
                                |(df_p_left['BOD Lane Item_Eff Enddate'].isna() ))
                             ]
    elif str_p_cond == '6':
        list_left_on = ['BOD.[From Site ID]']
        list_right_on = ['Location.[Location]']
        str_how = 'inner'
        df_p_left = df_p_left[ ~(( (pd.to_datetime(df_p_left['BOD Lane Item_Eff Startdate']) <= pd.Timestamp.today() + pd.Timedelta(hours=9))
                                |(df_p_left['BOD Lane Item_Eff Startdate'].isna() ))
                              &
                               ( (pd.to_datetime(df_p_left['BOD Lane Item_Eff Enddate']) >= pd.Timestamp.today() + pd.Timedelta(hours=9) + pd.Timedelta(days=28))
                                |(df_p_left['BOD Lane Item_Eff Enddate'].isna() )))
                             ]
    if str_p_cond in ('1') :
        # Merge
        df_return = df_p_left.merge(df_p_right, how=str_how, left_on=list_left_on, right_on=list_right_on,indicator=True )
    elif str_p_cond in ('2','3','5','6') :
        # Merge
        df_return = df_p_left.merge(df_p_right, how=str_how, left_on=list_left_on, right_on=list_right_on )
    else :
        # Merge
        df_return = df_p_left.merge(df_p_right, how=str_how, left_on=list_left_on, right_on=list_right_on,indicator=True)

    if str_p_cond == '1':
        df_return['Seq.[Seq]'] = np.nan
        df_return['Loading Dir Order Mgmt_Loading Type'] = np.nan
        df_return['Loading Dir Order Mgmt_Cntr Type'] = np.nan
        # Total LeadTime , Prod_date 생성
        df_return['Total Leadtime'] = df_return['BOD Lane Item_Shipping Leadtime'].fillna(0).astype(int) + df_return[
            'BOD Lane Item_Transit Time']
        df_return['Prod Date'] = pd.to_datetime(df_return['Loading Order Status_RDD Date']) - pd.to_timedelta(df_return['Total Leadtime'],unit='D')

        df_return['Loading Dir Order Mgmt_Valid Fail Reason'] = ''
        #df_return['Loading Dir Order Mgmt_Valid Fail Reason'] = np.where( df_return['_merge'] == 'left_only', 'Invalid BOD Date','' )

        # 컬럼명 변경 및 필요없는 컬럼 삭제
        df_return.rename(columns={"BOD.[From Site ID]": "Sub Location.[Sub Location]"}, inplace=True)
        df_return.rename(columns={"Loading Order Status_Sales Order": "Loading Dir Order Mgmt_Sales Order"}, inplace=True)
        df_return.rename(columns={"Loading Order Status_SO Item": "Loading Dir Order Mgmt_SO Item"}, inplace=True)
        df_return.rename(columns={"Ship To.[Ship To Party]": "Loading Dir Order Mgmt_Ship To"}, inplace=True)

        if is_local:
            # Local
            df_return.rename(columns={"Ship To.[DisplayName]": "Loading Dir Order Mgmt_Ship To Name"}, inplace=True)
        else:
            # Server
            df_return.rename(columns={"Ship To.[Ship To Party$DisplayName]": "Loading Dir Order Mgmt_Ship To Name"}, inplace=True)

        df_return.rename(columns={"Loading Order Status_Org Qty": "Loading Dir Order Mgmt_Origin Qty"}, inplace=True)
        df_return['Loading Dir Order Mgmt_Chk Qty'] = df_return['Loading Dir Order Mgmt_Origin Qty']

        df_return.rename(columns={"BOD.[From Site ID]": "Sub Location.[Sub Location]"}, inplace=True)
        df_return = df_return.drop('BOD.[To Site ID]', axis=1)
        df_return = df_return.drop('BOD Lane Item_Shipping Leadtime', axis=1)
        df_return = df_return.drop('BOD Lane Item_Transit Time', axis=1)

    elif str_p_cond == '3':
        df_return['Loading Dir Order Mgmt_RDD Week'] = df_return['Time.[Week]_y']

        # 필요없는 컬럼 삭제
        # df_return = df_return.drop('Time.[WeekKey]', axis=1)
        # df_return = df_return.drop('Time.[W Solver Current Bucket]', axis=1)
        # df_return = df_return.drop('Time.[W Solver Start Bucket]', axis=1)
        # df_return = df_return.drop('Time.[W Solver End Bucket]', axis=1)
        df_return = df_return.drop('Time.[Day]', axis=1)
        # df_return = df_return.drop('Tact Time W_Tact Time', axis=1)

    elif str_p_cond == '2':
        df_return['Loading Dir Order Mgmt_Adj Prod Week'] = df_return['Time.[Week]_y']
        df_return['Time.[Week]_x'] = df_return['Time.[Week]_y']
        # 필요없는 컬럼 삭제
        # df_return = df_return.drop('Time.[WeekKey]', axis=1)
        # df_return = df_return.drop('Time.[W Solver Current Bucket]', axis=1)
        # df_return = df_return.drop('Time.[W Solver Start Bucket]', axis=1)
        # df_return = df_return.drop('Time.[W Solver End Bucket]', axis=1)
        df_return = df_return.drop('Time.[Day]', axis=1)
        # df_return = df_return.drop('Tact Time W_Tact Time', axis=1)
        df_return = df_return.drop('Total Leadtime', axis=1)
        df_return = df_return.drop('Prod Date', axis=1)
    elif str_p_cond in ('5','6') :

        df_return['Tot_LeadTime']  = df_return['BOD Lane Item_Shipping Leadtime']+df_return['BOD Lane Item_Transit Time']

        df_return = df_return.sort_values(by=['BOD.[To Site ID]', 'Item.[Item]',
                                              'BOD Lane Item_Eff Enddate', 'BOD Lane Item_Priority', 'Tot_LeadTime'],
                                          ascending =[True,True,False,True,True])

        df_return['Row_Num'] = df_return.groupby(['BOD.[To Site ID]', 'Item.[Item]'])[['BOD Lane Item_Priority']].rank(ascending=False, method='first')

        df_return = df_return[df_return['Row_Num'] == 1]

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

    # 구분자 정의(단계-output 코드)
    p_cond = str_p_cond

    # 결과 테이블에서 필요한 컬럼만을 추출하고 순서를 변경하여 저장한다.

    if p_cond == '0' :
        df_return = df_return[
            ['Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
             'Sales Domain.[Ship To]','Item.[Item]', 'Time.[Week]', 'Seq.[Seq]',
             'Loading Dir Order Mgmt_Sales Order',  'Loading Dir Order Mgmt_SO Item',
             'Loading Dir Order Mgmt_RDD Week',
             'Loading Dir Order Mgmt_Adj Prod Week',
             'Loading Dir Order Mgmt_Ship To', 'Loading Dir Order Mgmt_Ship To Name', 'Loading Dir Order Mgmt_Loading Type',
             'Loading Dir Order Mgmt_Cntr Type', 'Loading Dir Order Mgmt_Origin Qty', 'Loading Dir Order Mgmt_Chk Qty',
             'Loading Dir Order Mgmt_Valid Fail Reason'
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
             'Loading Dir Order Mgmt_Valid Fail Reason',
             'Loading Dir Order Mgmt_Created By', 'Loading Dir Order Mgmt_Creation Time', 'Loading Dir Order Mgmt_Chk Grain'
             ]
        ]
    # 결과 리턴
    return df_return

@_decoration_
def fn_update_empty_loadingtype_containerid(
        df_p_dir_order_status: pd.DataFrame, df_p_loading_methods: pd.DataFrame,
        list_p_dir_order_status_columns: list, list_p_loading_methods_columns: list,
        str_method_type: str, str_measure_type: str
) -> pd.DataFrame:
    """
    :param df_p_dir_order_status: Mgmt Upload 데이타프레임
    :param df_p_loading_methods: from ~ ship to Methods 데이타프레임
    :param list_p_dir_order_status_columns: Mgmt Upload 사용될 columns List
    :param list_p_loading_methods_columns: methods 사용될 columns List
    :param str_method_type: 타입별 Method
    :param str_measure_type: 대상 measure
    :return: df_return
    """
    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 파라미터 테이블(df_p_source)이 비어 있는 경우 빈 데이터프레임을 리턴하면서 함수를 종료한다.
    if df_p_dir_order_status.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_mgmt_upload)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return
    if df_p_loading_methods.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_methods) ' + str_method_type + '가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_dir_order_status

    # Loading Dir Order Mgmt_Cntr Type NaN인 데이타 프레임만 선별한다.
    df_p_dir_order_status_undefined_loadingtype = df_p_dir_order_status.loc[
        df_p_dir_order_status[str_measure_type].isna(),
        list_p_dir_order_status_columns
    ]
    query_string = f'`Loading Method {str_method_type}_Valid Flag` == "Y"'
    # Method from~Ship To에서 Loading Type 가져오기
    df_p_loading_methods_default_valid_y = df_p_loading_methods.query(query_string)

    # 로컬이면서 'Loading Dir Order Mgmt_Ship To' 컬럼이 존재 하면 타입때문에 에러나는 부분 발생으로 추가
    if is_local & ('Loading Dir Order Mgmt_Ship To' in df_p_dir_order_status_undefined_loadingtype.columns):
        df_p_dir_order_status_undefined_loadingtype['Loading Dir Order Mgmt_Ship To'] = df_p_dir_order_status_undefined_loadingtype['Loading Dir Order Mgmt_Ship To'].astype('str')

    df_p_dir_order_status_undefind_loadingtype = pd.merge(
        df_p_dir_order_status_undefined_loadingtype, df_p_loading_methods_default_valid_y,
        left_on=list_p_dir_order_status_columns[1:], right_on=list_p_loading_methods_columns,
        how='inner'
    )
    # 컬럼중복제거
    df_p_dir_order_status_undefind_loadingtype = fn_merge_after(df_p_dir_order_status_undefind_loadingtype)
    df_p_dir_order_status_undefind_loadingtype = df_p_dir_order_status_undefind_loadingtype[
        [
            'Seq.[Seq]',
            'Container.[ContainerID]' if str_measure_type == 'Loading Dir Order Mgmt_Cntr Type' else
            'Loading Type.[Loading Type]'
        ]
    ]
    # unique한 Seq.[Seq]가 나왔다는건 Loading Method from ~ Ship To unique하지 않을수 있다는것이므로 첫번째거 하나만
    df_p_dir_order_status_undefind_loadingtype = df_p_dir_order_status_undefind_loadingtype.drop_duplicates(
        subset='Seq.[Seq]', keep='first'
    )
    # loadingType&ContainerID가 누락된 loading_mgmt_upload에 from ~ Ship To Method에서 가져와서 넣어주기위해merge
    df_return = pd.merge(
        df_p_dir_order_status, df_p_dir_order_status_undefind_loadingtype,
        on='Seq.[Seq]', how='left', indicator=True
    )
    # undefined있는 Seq.[Seq]와 upload Loading Mgmt Seq.[Seq]를 merge하여 Loding Type과 Container ID update
    df_return.loc[
        df_return['_merge'] == 'both', str_measure_type
    ] = df_return[
        'Container.[ContainerID]' if str_measure_type == 'Loading Dir Order Mgmt_Cntr Type' else
        'Loading Type.[Loading Type]'
    ]
    # _merge & merge로 인한 계속 생성되어 오류를 일으키는 컬럼 삭제
    df_return.drop([
        '_merge',
        'Container.[ContainerID]' if str_measure_type == 'Loading Dir Order Mgmt_Cntr Type' else
         'Loading Type.[Loading Type]'
    ], axis=1, inplace=True)

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()
    # Output 테이블 선언
    out_LoadingDirMgmt = pd.DataFrame()
    out_LoadingOrderStatus = pd.DataFrame()

    out_BOD_Lane_Item = pd.DataFrame()
    out_BOD_Lane_Item_Invalid = pd.DataFrame()
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = ''
            Param_PLANTYPE = ''
            Param_User_Name = 'SOONUP JEE'#'daeun01.yun'
            in_Loading_Order_Status = pd.read_csv(str_input_dir + "/in_Loading_Order_Status.csv", encoding="UTF8")
            in_BOD_Lane_Item = pd.read_csv(str_input_dir + "/in_BOD_Lane_Item.csv", encoding="UTF8")
#            in_BOD_Lane_Item_Invalid = pd.read_csv(str_input_dir + "/in_BOD_Lane_Item_Invalid.csv", encoding="UTF8")
            in_Location = pd.read_csv(str_input_dir + "/in_Location.csv", encoding="UTF8")
            in_Loading_Method_Ship_To = pd.read_csv(str_input_dir + "/in_Loading_Method_Ship_To.csv", encoding="UTF8")
            in_Loading_Method_Account = pd.read_csv(str_input_dir + "/in_Loading_Method_Account.csv", encoding="UTF8")
            in_Loading_Method_To_Site = pd.read_csv(str_input_dir + "/in_Loading_Method_To_Site.csv", encoding="UTF8")
            in_Loading_Method_From = pd.read_csv(str_input_dir + "/in_Loading_Method_From.csv", encoding="UTF8")
            in_Time = pd.read_csv(str_input_dir + "/in_Time.csv", encoding="UTF8")
            in_Loading_Dir_Order_Mgmt = pd.read_csv(str_input_dir + "/in_Loading_Dir_Order_Mgmt.csv", encoding="UTF8")

        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')

        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())

        fn_check_input_table(in_Loading_Order_Status, 'in_Loading_Order_Status', '0')

        #  DataFrame 컬럼 선처리
        in_Loading_Method_Ship_To = fn_preprocess(in_Loading_Method_Ship_To)

        ##############################################################################################################
        # Step0-1 in_BOD_Lane_Item 의 [BOD].[From Site ID] 와
        #         in_Location 의 Location.[Location] 로  FDC site를 제거하여 중복을 없애고,
        # Step0-2 in_BOD_Lane_Item 의  Total LeadTime이 작고 priority가 높은  bod를 구함
        ##############################################################################################################
        logger.Step(p_step_no=10,
                    p_step_desc=f'in_BOD_Lane_Item in_Location inner Merge')
        out_BOD_Lane_Item = fn_merge_inner_join(in_BOD_Lane_Item, in_Location, '5')
        # 출력 로그
        logger.PrintDF(p_df=out_BOD_Lane_Item, p_df_name='out_BOD_Lane_Item'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)

        # merge후 중복 컬럼으로 _x, _y제거
        out_BOD_Lane_Item = fn_merge_after(out_BOD_Lane_Item)

        ##############################################################################################################
        # in_BOD_Lane_Item_Invalid 로  무효한 from site 구성
        # Step0-3 in_BOD_Lane_Item_Invalid 의 [BOD].[From Site ID] 와
        #         in_Location 의 Location.[Location] 를 inner join으로  FDC site를 제거하여 중복을 없애고,
        # Step0-4 in_BOD_Lane_Item_Invalid 의  Total LeadTime이 작고 priority가 높은  bod를 구함
        ##############################################################################################################
        logger.Step(p_step_no=20,
                    p_step_desc=f'in_BOD_Lane_Item_Invalid in_Location inner Merge')
        out_BOD_Lane_Item_Invalid = fn_merge_inner_join(in_BOD_Lane_Item, in_Location, '6')
        # 출력 로그
        logger.PrintDF(p_df=out_BOD_Lane_Item_Invalid, p_df_name='out_BOD_Lane_Item_Invalid'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)

        # merge후 중복 컬럼으로 _x, _y제거
        out_BOD_Lane_Item_Invalid = fn_merge_after(out_BOD_Lane_Item_Invalid)

        ##############################################################################################################
        # Step1-1 Order Status의  Item.[Item], Location.[Location] 과
        #         Eff BOD_Lane_Item   Item.[Item], BOD.[To Site ID] 로    From Site ID 와 Total LeadTime 구함.
        #
        ##############################################################################################################
        logger.Step(p_step_no=110,
                    p_step_desc=f'in_Loading_Order_Status out_BOD_Lane_Item inner Merge')
        df_OrderStatus_merged = fn_merge_inner_join(in_Loading_Order_Status, out_BOD_Lane_Item, '1')
        # 출력 로그
        logger.PrintDF(p_df=df_OrderStatus_merged, p_df_name='df_OrderStatus_merged'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)

        # merge후 중복 컬럼으로 _x, _y제거
        df_OrderStatus_merged = fn_merge_after(df_OrderStatus_merged)

        df_OrderStatus_merged = fn_merge_inner_join(df_OrderStatus_merged, in_Time, '3')
        # merge후 중복 컬럼으로 _x, _y제거
        df_OrderStatus_merged = fn_merge_after(df_OrderStatus_merged)
        # 출력 로그
        logger.PrintDF(p_df=df_OrderStatus_merged, p_df_name='df_OrderStatus_merged'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)


        ##############################################################################################################
        # Step1-1-1 무효한 BOD에 해당하는 대상추출
        ##############################################################################################################
        logger.Step(p_step_no=111,
                    p_step_desc=f'df_OrderStatus_merged_combine_not Select')
        df_OrderStatus_merged_combine_not = df_OrderStatus_merged[df_OrderStatus_merged['_merge'] == 'left_only'].copy()
        df_OrderStatus_merged_combine_not = df_OrderStatus_merged_combine_not.drop('_merge', axis=1)
        df_OrderStatus_merged_combine_not = df_OrderStatus_merged_combine_not.drop('Sub Location.[Sub Location]', axis=1)
        # 출력 로그
        logger.PrintDF(p_df=df_OrderStatus_merged_combine_not, p_df_name='df_OrderStatus_merged_combine_not'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)
        ##############################################################################################################
        # Step1-1-2 유효한 BOD에 해당하는 대상추출
        ##############################################################################################################
        logger.Step(p_step_no=112,
                    p_step_desc=f'df_OrderStatus_merged_combine_not Select')
        df_OrderStatus_merged = df_OrderStatus_merged[df_OrderStatus_merged['_merge'] == 'both']
        # 출력 로그
        logger.PrintDF(p_df=df_OrderStatus_merged, p_df_name='df_OrderStatus_merged'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)


        ################################################################################################################
        # Step1-1-3 무효한 BOD로 FromSite 구함
        ################################################################ ################################################
        logger.Step(p_step_no=113,
                    p_step_desc=f'df_OrderStatus_merged_exist Select')
        df_OrderStatus_merged_exist = fn_merge_inner_join(df_OrderStatus_merged_combine_not,
                                                                out_BOD_Lane_Item_Invalid, '1')
        # 출력 로그
        logger.PrintDF(p_df=df_OrderStatus_merged_exist, p_df_name='df_OrderStatus_merged_exist'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)

        # merge후 중복 컬럼으로 _x, _y제거
        df_OrderStatus_merged_exist = fn_merge_after(df_OrderStatus_merged_exist)
        df_OrderStatus_merged_exist['Loading Dir Order Mgmt_Valid Fail Reason'] = 'Invalid BOD Date'
        ################################################################################################################
        # Step1-1-4 무효한 BOD로도 못구한 대상
        ################################################################ ################################################
        df_OrderStatus_merged_exist_not = df_OrderStatus_merged_exist[df_OrderStatus_merged_exist['_merge'] == 'left_only'].copy()
        df_OrderStatus_merged_exist_not['Loading Dir Order Mgmt_Adj Prod Week'] = np.nan

        ################################################################################################################
        # Step1-1-5 무효한 BOD로  구한대상
        ################################################################ ################################################
        # master 메져와 df_OrderStatus_merged join이 된것들
        df_OrderStatus_merged_exist = df_OrderStatus_merged_exist[df_OrderStatus_merged_exist['_merge'] == 'both']
        # prod week
        df_OrderStatus_merged_exist = fn_merge_inner_join(df_OrderStatus_merged_exist, in_Time, '2')
        # merge후 중복 컬럼으로 _x, _y제거
        df_OrderStatus_merged_exist = fn_merge_after(df_OrderStatus_merged_exist)

        df_OrderStatus_merged_exist     = df_OrderStatus_merged_exist.drop('_merge', axis=1)
        df_OrderStatus_merged_exist_not = df_OrderStatus_merged_exist_not.drop('_merge', axis=1)

        df_OrderStatus_merged_exist       = fn_output_formatter(df_OrderStatus_merged_exist,       Param_OUT_VERSION,'0')
        df_OrderStatus_merged_exist_not   = fn_output_formatter(df_OrderStatus_merged_exist_not,   Param_OUT_VERSION,'0')


        # ##############################################################################################################
        # # Step1-2 df_OrderStatus_merged 의  [Loading Order Status_RDD Date]에  과
        # #         inTime                    Time.[Day]  로    prod week 구함.
        # #
        # ##############################################################################################################
        logger.Step(p_step_no=120,
                    p_step_desc=f'df_OrderStatus_merged in_Time inner Merge')
        df_OrderStatus_merged = fn_merge_inner_join(df_OrderStatus_merged, in_Time, '2')
        # 출력 로그
        logger.PrintDF(p_df=df_OrderStatus_merged, p_df_name='df_OrderStatus_merged'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)

        # merge후 중복 컬럼으로 _x, _y제거
        out_LoadingDirMgmt = fn_merge_after(df_OrderStatus_merged)

        out_LoadingDirMgmt = fn_output_formatter(out_LoadingDirMgmt, Param_OUT_VERSION, '0')
        # ##############################################################################################################
        # # Step1-3 out_LoadingDirMgmt 의  Loading Dir Order Mgmt_Cntr Type 채우기
        # ##############################################################################################################
        # 'Loading Dir Order Mgmt_Cntr Type' 컬럼에 NaN이 존재 하면

        list_orderstatus_use_columns = [
            'Seq.[Seq]', 'Sub Location.[Sub Location]', 'Location.[Location]',
            'Sales Domain.[Ship To]', 'Loading Dir Order Mgmt_Ship To'
        ]
        list_loading_methods_use_columns = [
            'Sub Location.[Sub Location]', 'Location.[Location]',
            'Sales Domain.[Ship To]', 'Loading Method Ship To_Ship To'
        ]

        # 출력 로그
        logger.PrintDF(p_df=out_LoadingDirMgmt, p_df_name='out_LoadingDirMgmt'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)

        logger.PrintDF(p_df=in_Loading_Method_Ship_To, p_df_name='in_Loading_Method_Ship_To'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)
        # ###########################################################################################
        # 조인되지 않는 데이타까지 합쳐서 만들기
        # ###########################################################################################
        # method concat 아래 데이타프레임 empty가 아닌것만 concat
        dfs_to_combine_concat = [df_bod_combine for df_bod_combine in [
            out_LoadingDirMgmt, df_OrderStatus_merged_exist, df_OrderStatus_merged_exist_not
        ] if not df_bod_combine.empty]
        # # 데이터프레임을 concat
        out_LoadingDirMgmt = pd.concat(dfs_to_combine_concat,
                                       ignore_index=True) if dfs_to_combine_concat else pd.DataFrame()

        # Container Type, Loading Type을 구하는 로직 시작
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Cntr Type'] = np.nan
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Loading Type'] = np.nan

        if out_LoadingDirMgmt['Loading Dir Order Mgmt_Cntr Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_Ship_To,
                list_orderstatus_use_columns[:], list_loading_methods_use_columns[:],
                'Ship To', 'Loading Dir Order Mgmt_Cntr Type'
            )

        if  out_LoadingDirMgmt['Loading Dir Order Mgmt_Cntr Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_Account,
                list_orderstatus_use_columns[:4], list_loading_methods_use_columns[:3],
                'Account', 'Loading Dir Order Mgmt_Cntr Type'
            )


        if out_LoadingDirMgmt['Loading Dir Order Mgmt_Cntr Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_To_Site,
                list_orderstatus_use_columns[:3], list_loading_methods_use_columns[:2],
                'To Site', 'Loading Dir Order Mgmt_Cntr Type'
            )


        if out_LoadingDirMgmt['Loading Dir Order Mgmt_Cntr Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_From,
                list_orderstatus_use_columns[:2], list_loading_methods_use_columns[:1],
                'From Site', 'Loading Dir Order Mgmt_Cntr Type'
            )

        # ##############################################################################################################
        # # Step1-4  out_LoadingDirMgmt 의  Loading Dir Order Mgmt_Loading Type 채우기
        # ##############################################################################################################
        # Step9. Loading Dir Order Mgmt_Loading Type

        if out_LoadingDirMgmt['Loading Dir Order Mgmt_Loading Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_Ship_To,
                list_orderstatus_use_columns[:], list_loading_methods_use_columns[:],
                'Ship To', 'Loading Dir Order Mgmt_Loading Type'
            )

        if out_LoadingDirMgmt['Loading Dir Order Mgmt_Loading Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_Account,
                list_orderstatus_use_columns[:4], list_loading_methods_use_columns[:3],
                'Account', 'Loading Dir Order Mgmt_Loading Type'
            )

        if out_LoadingDirMgmt['Loading Dir Order Mgmt_Loading Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_To_Site,
                list_orderstatus_use_columns[:3], list_loading_methods_use_columns[:2],
                'To Site', 'Loading Dir Order Mgmt_Loading Type'
            )

        if out_LoadingDirMgmt['Loading Dir Order Mgmt_Loading Type'].isna().any():
            # 함수 호출
            out_LoadingDirMgmt = fn_update_empty_loadingtype_containerid(
                out_LoadingDirMgmt, in_Loading_Method_From,
                list_orderstatus_use_columns[:2], list_loading_methods_use_columns[:1],
                'From Site', 'Loading Dir Order Mgmt_Loading Type'
            )
        # Container Type, Loading Type을 구하는 로직 끝

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

        # Created By, Creation Time 입력 ( 로컬, 서버 시간차이 : + 9 hour)   CurrentUser().[User Name]
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Created By']    = Param_User_Name
        out_LoadingDirMgmt['Loading Dir Order Mgmt_Creation Time'] = datetime.datetime.now()
        if not is_local:
            out_LoadingDirMgmt['Loading Dir Order Mgmt_Creation Time'] =  out_LoadingDirMgmt['Loading Dir Order Mgmt_Creation Time'] + datetime.timedelta(hours=9)

        # 2025-07-14 윤서정 프로요청 Time.[Week] => Prod Week로 Loading Dir Order Mgmt_Adj Prod Week => Time.[Week]로
        out_LoadingDirMgmt.rename(
            columns={
                'Time.[Week]': 'Loading Dir Order Mgmt_Prod Week',
                'Loading Dir Order Mgmt_RDD Week': 'Time.[Week]'
            }, inplace=True
        )

        out_LoadingDirMgmt = fn_output_formatter(out_LoadingDirMgmt, Param_OUT_VERSION, '1')

        # Chk Flag null 로 업데이트 ( 사용자 가 chk한 값 원복 )
        list_where = in_Loading_Order_Status['Loading Order Status_Confirmed By'] == Param_User_Name
        out_LoadingOrderStatus = in_Loading_Order_Status[list_where]
        out_LoadingOrderStatus['Loading Order Status_Chk Flag'] = np.nan
        out_LoadingOrderStatus = out_LoadingOrderStatus[
            [
                'Version.[Version Name]', 'Location.[Location]', 'Sales Domain.[Ship To]', 'Ship To.[Ship To Party]',
                'Item.[Item]', 'Time.[Week]', 'Loading Order Status_Chk Flag'
            ]
        ]
        # 출력 변수 확인용 로그
        logger.PrintDF(p_df=out_LoadingDirMgmt, p_df_name='out_LoadingDirMgmt'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)

        # 출력 변수 확인용 로그
        logger.PrintDF(p_df=out_LoadingOrderStatus, p_df_name='out_LoadingOrderStatus'
                       , p_log_level=LOG_LEVEL.debug(), p_format=1)
        # Step Log
        logger.Step(p_step_no=900, p_step_desc=f'OUTPUT : 최종 Output 테이블 만들기')
        if is_local and not out_LoadingDirMgmt.empty:
            # 로컬 Debugging 시 csv 파일 출력
            out_LoadingDirMgmt.to_csv(str_output_dir + "/out_LoadingDirMgmt.csv", encoding="UTF8")
        if is_local and not out_LoadingDirMgmt.empty:
            # 로컬 Debugging 시 csv 파일 출력
            out_LoadingOrderStatus.to_csv(str_output_dir + "/out_LoadingOrderStatus.csv", encoding="UTF8")

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
