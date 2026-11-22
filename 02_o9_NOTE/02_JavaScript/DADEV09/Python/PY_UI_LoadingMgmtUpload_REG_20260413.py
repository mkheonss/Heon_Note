"""
* 프로그램명
    - PY_UI_LoadingMgmtUpload_REG.py
* 내용
    - 입력에 대한 해당 정보를 Loading Dir Order Mgmt화면 값으로 입력해줌
* 변경이력
    - 2025.04.29 / YUN TAE UN / Create
* Flow Summary
    Step1.
        'Loading Mgmt Upload_Sales Order' Measure
            입력값이 있는 경우 유지함,
            단 없는 경우 'Manual_작업일자_Seq.[Seq]순으로 작성한다'
            반영 메저 : Loading Dir Order Mgmt (메져그룹) => Loading Dir Order Mgmt_Sales Order(메져)
    Step2.
        'Loading Mgmt Upload_Adj Prod Week' Measure
            입력값이 있는 경우 유지함.
            단 없는 경우, Time.[Week]를 그대로 반영함.
            반영 메저 : Loading Dir Order Mgmt (메져그룹) => Loading Dir Order Mgmt_Adj Prod Week(메져)
    Step3.
    3-1.'Loading Mgmt Upload_From Site' Measure
        (Python Validation내 Attr chk)
        'From Site Name'값을 VALIDATION 이후 반영되는 결과 값이 없으면
            'Not Defined'이라고 표기 후, 붉은 색으로 표기
        Validation이 정상적으로 수행된 경우
            반영 메저 : Loading Dir Order Mgmt (메져그룹) => Sub Location.[Sub Location](디멘져)
    3-2.'Loading Mgmt Upload_From Site Name'
        (Python Validation내 Attr chk)
        EXCEL UPLOAD 필수 attr, Sub Location.[Sub Location$DisplayName]기준으로 조회하여
        , Sub Location.[Sub Location]값 여부 확인 필요
        사용자 입력 값과 실제 Sub Location.[Sub Location$DisplayName]을 조회 할 때, 두 값 모두 upper처리하여 비교함.
    Step4.
    4-1 'Loading Mgmt Upload_To Site' Measure
        (Python Validation내 Attr chk) To Site Name값을 VALIDATION 이후 반영되는 결과 값이 없으면
            'Not Defined'이라고 표기후, 붉은 색으로 표기
        Validation이 정상적으로 수행된 경우
            반영 메저 : Loading Dir Order Mgmt(메저그룹) => Location.[Location](디멘져)
    4-2 'Loading Mgmt Upload_To Site Name' Measure
        (Python Validation내 Attr chk) EXCEL UPLOAD 필수 attr, Location.[ocation$DisplayName]기준으로 조회하여
        , Location.[Location]값 여부 확인 필요
        , 사용자 입력 값과 실제 Sub Location.[Sub Location$DisplayName]을 조회 할 때, 두 값 모두 upper처리하여 비교함.
    Step5.
    5-1 'Loading Mgmt Upload_Shipment Type' Measure
    (Python Validation내 Attr chk)(잘못입력되더라도, Location.[Shipment Type]기준 강제반영)
    , 참고로, Shipment Type은 Attribute가 아닌 Property 값입니다.
    반영 메저 : Loading Dir Order Mgmt(메저그룹) => Loading Dir Order Mgmt_Loading Type(메저)

    Step6.
    6-1 'Loading Mgmt Upload_Account'
        (Python Validation내 Attr chk) EXCEL UPLOAD 필수 attr, Domain.[Account$DisplayName]기준으로 조회하여
        , Sales Domain.[Ship To]값 여부 확인 필요
        Validation이 정상적으로 수행된 경우
            반영 메져 : Loading Dir Order Mgmt(메져그룹) => Sales Domain.[Ship To](디멘져)값으로 반영
    6-2 'Loading Mgmt Upload_Account Name'
        (Python Validation내 Attr chk) Account값을 VALIDATION 이후 반영되는 결과 값이 Not Defined인 경우, 붉은 색으로 표기
    Step7.
    7-1 'Loading Mgmt Upload_Item'
        (Python Validation내 Attr chk) EXCEL UPLOAD 필수 attr, Item.[Item]기준으로 조회하여, Item.[Item]값 여부 확인 필요
        Validation이 정상적으로 수행된 경우
            반영 메져 : Loading Dir Order Mgmt(메져그룹) => Item.[Item](디멘져)값으로 반영
    7-2 'Loading Mgmt Upload_Project'
        VALIDATION 이후 반영되는 결과 값이 Not Defined인 경우, 붉은 색으로 표기함
    7-3 'Loading Mgmt Upload_Product Group'
        VALIDATION 이후 반영되는 결과 값이 Not Defined인 경우, 붉은 색으로 표기함
    7-4 'oading Mgmt Upload_Product'
        VALIDATION 이후 반영되는 결과 값이 Not Defined인 경우, 붉은 색으로 표기함
    Step8. 'Loading Mgmt Upload_Loading Type'
    8-1 (Python Validation내 Attr Chk, 소문자 존재 시 upper처리함) EXCEL UPLOAD 필수 attr
        , LoadingType.[Loading Type]에 존재하는지 chk함.
    8-2 Loading Method (From Site/To Site/Account/Ship To)기준정보에서
        , Loading Type, Cntr Type제외 나머지 From~Ship To까지의 컬럼값을 비교하고
        , 대상값에서 Loading Method (From Site/To Site/Account/Ship To) Valid Flag = 'Y'이면서
        , Loading Method (From Site/To Site/Account/Ship To) Default = 'Y'인 Loading Type, Cntr Type을 반영해줌
    반영 메져 : Loading Dir Order Mgmt(메져그룹) => Loading Dir Order Mgmt_Loading Type(메져)값으로 반영
    Step9. Loading Mgmt Upload_Cntr Type
    9-1 (Python Validation내 Attr Chk, 소문자 존재 시 upper처리함) EXCEL UPLOAD 필수 attr
    , LoadingType.[Loading Type]에 존재하는지 chk함.
    9-2 Loading Method ((From Site/To Site/Account/Ship To)기준정보에서,Loading Type, Cntr Type제외 나머지
        From~Ship To까지의 컬럼값을 비교하고, 대상값에서 Loading Method (From Site/To Site/Account/Ship To) Valid Flag = 'Y'이면서
        , Loading Method (From Site/To Site/Account/Ship To) Default = 'Y'인 Cntr Type을 반영해줌
    반영 메져 : Loading Dir Order Mgmt(메져그룹) => Loading Dir Order Mgmt_Container Type(메져)값으로 반영
    Step10. 'Loading Mgmt Upload_Org Qty
        미 입력시 Not Defined. 붉은 색으로 표기함
        반영 메저 : Loading Dir Order Mgmt(메져그룹) => Loading Dir Order Mgmt_Org Qty(메져)
    Step11. 'Loading Mgmt Upload_Chk Qty'
        누락 시 'Loading Mgmt Upload_Org Qty'값 반영함.
        반영 메저 : Loading Dir Order Mgmt(메져그룹) => Loading Dir Order Mgmt_Chk Qty(메져)
    Step12. 'Loading Mgmt Upload_Valid Flag'
        Validation 문제가 없는 경우 'Y'체크
        'Y'가 아닌 케이스 발생 시에 전체 Validation 점검 후
        Loading Dir Order Mgmt로 넘기지 않고 종료함.

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
- in_Loading_Mgmt_Upload
    ㄴ o9 upload용
    Select ([Personnel].[Email] * [Version].[Version Name] * [Seq].[Seq] * [Time].[Week] ) on row, ({Measure.[Loading Mgmt Upload_Account], Measure.[Loading Mgmt Upload_Account Name], Measure.[Loading Mgmt Upload_Adj Prod Week], Measure.[Loading Mgmt Upload_Chk Qty], Measure.[Loading Mgmt Upload_Cntr Type], Measure.[Loading Mgmt Upload_From Site], Measure.[Loading Mgmt Upload_From Site Name], Measure.[Loading Mgmt Upload_Item], Measure.[Loading Mgmt Upload_Loading Type], Measure.[Loading Mgmt Upload_Org Qty], Measure.[Loading Mgmt Upload_Product], Measure.[Loading Mgmt Upload_Product Group], Measure.[Loading Mgmt Upload_Project], Measure.[Loading Mgmt Upload_RDD Week], Measure.[Loading Mgmt Upload_SO Item],Measure.[Loading Mgmt Upload_Sales Order], Measure.[Loading Mgmt Upload_Ship To], Measure.[Loading Mgmt Upload_Ship To Name], Measure.[Loading Mgmt Upload_Shipment Type], Measure.[Loading Mgmt Upload_To Site], Measure.[Loading Mgmt Upload_To Site Name], Measure.[Loading Mgmt Upload_Valid Flag]}) on column where{Measure.[Loading Mgmt Upload_Chk Flag]=="Y"};
    ㄴ 개발 직관용
    Select (
        * [Version].[Version Name]
        * [Personnel].[Email]
        * [Time].[Week]
        * [Seq].[Seq]
    ) on row
    ,
    ({
        Measure.[Loading Mgmt Upload_From Site]
        , Measure.[Loading Mgmt Upload_From Site Name]
        , Measure.[Loading Mgmt Upload_To Site]
        , Measure.[Loading Mgmt Upload_To Site Name]
        , Measure.[Loading Mgmt Upload_Account]
        , Measure.[Loading Mgmt Upload_Account Name]
        , Measure.[Loading Mgmt Upload_Ship To]
        , Measure.[Loading Mgmt Upload_Ship To Name]
        , Measure.[Loading Mgmt Upload_Item]
        , Measure.[Loading Mgmt Upload_Product]
        , Measure.[Loading Mgmt Upload_Product Group]
        , Measure.[Loading Mgmt Upload_Project]
        , Measure.[Loading Mgmt Upload_Cntr Type]
        , Measure.[Loading Mgmt Upload_Loading Type]
        , Measure.[Loading Mgmt Upload_Shipment Type]
        , Measure.[Loading Mgmt Upload_RDD Week]
        , Measure.[Loading Mgmt Upload_Adj Prod Week]
        , Measure.[Loading Mgmt Upload_Org Qty]
        , Measure.[Loading Mgmt Upload_Chk Qty]
        , Measure.[Loading Mgmt Upload_SO Item]
        , Measure.[Loading Mgmt Upload_Sales Order]
        , Measure.[Loading Mgmt Upload_Valid Flag]
    }) on column
    where{Measure.[Loading Mgmt Upload_Chk Flag]=="Y"};
########## Loading Type & Cntr Type을 위한 Method 마스터 테이블 input ##################################################
- in_Dimension_Item
    ㄴ o9 upload용
    Select (Item.Item * Item.[Project] * Item.[Product Group] * Item.[Product]) on row, () on column;
    ㄴ 개발 직관용
    Select (
        Item.Item
        * Item.[Project]
        * Item.[Product Group]
        * Item.[Product]
    ) on row, () on column;
- in_Dimension_From_Site
    ㄴ o9 upload용
        Select ([Sub Location].[Sub Location]) on row,() on column include memberproperties {[Sub Location].[Sub Location], [DisplayName]};
    ㄴ 개발 직관용
        Select (
            [Sub Location].[Sub Location]
        ) on row
        ,() on column
        include memberproperties {[Sub Location].[Sub Location], [DisplayName]};
- in_Dimension_To_Site
    ㄴ o9 upload용
        Select (Location.Location) on row,() on column include memberproperties {Location.Location, [DisplayName]} {Location.Location, [Shipment Type]};
    ㄴ 개발 직관용
        Select (
            Location.Location
        ) on row
        ,() on column
        include memberproperties {Location.Location, [DisplayName]} {Location.Location, [Shipment Type]};
- in_Dimension_Account
    ㄴ o9 upload용
        Select ([Sales Domain].[Ship To]) on row, () on column include memberproperties {[Sales Domain].[Ship To], [DisplayName]};
    ㄴ 개발 직관용
        Select (
            [Sales Domain].[Ship To]
        ) on row
        , () on column
        include memberproperties {[Sales Domain].[Ship To], [DisplayName]};

########## Loading Type & Cntr Type을 위한 Method 마스터 테이블 input ##################################################
- in_Loading_Method_Ship_To
ㄴ o9 upload용
    Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Sales Domain].[Ship To] * [Ship To].[Ship To Party] * [Container].[ContainerID] * [Loading Type].[Loading Type] * [Seq].[Seq]) on row,({Measure.[Loading Method Ship To_Default], Measure.[Loading Method Ship To_Valid Flag]}) on column;
ㄴ 개발 직관용
    Select (
        [Version].[Version Name]
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Sales Domain].[Ship To]
        * [Ship To].[Ship To Party]
        * [Container].[ContainerID]
        * [Loading Type].[Loading Type]
        * [Seq].[Seq]
    ) on row
    , ({
        Measure.[Loading Method Ship To_Default]
        , Measure.[Loading Method Ship To_Valid Flag]
    }) on column;
- in_Loading_Method_Account
ㄴ o9 upload용
    Select ([Version].[Version Name] * [Loading Type].[Loading Type] * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] * [Sales Domain].[Ship To] ) on row, ({Measure.[Loading Method Account_Default], Measure.[Loading Method Account_Valid Flag]}) on column;
ㄴ 개발 직관용
    Select (
        [Version].[Version Name]
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Sales Domain].[Ship To]
        * [Container].[ContainerID]
        * [Loading Type].[Loading Type]
    ) on row
    , ({
        Measure.[Loading Method Account_Default]
        , Measure.[Loading Method Account_Valid Flag]
    }) on column;
- in_Loading_Method_To_Site
ㄴ o9 upload용
    Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Location].[Location] * [Container].[ContainerID] * [Loading Type].[Loading Type]) on row, ({Measure.[Loading Method To Site_Default], Measure.[Loading Method To Site_Valid Flag]}) on column;
ㄴ 개발 직관용
    Select (
        [Version].[Version Name]
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Container].[ContainerID]
        * [Loading Type].[Loading Type]
    ) on row
    , ({
        Measure.[Loading Method To Site_Default]
        , Measure.[Loading Method To Site_Valid Flag]
    }) on column;
- in_Loading_Method_From_Site
ㄴ o9 upload용
    Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Shipment Type].[Shipment Type] * [Loading Type].[Loading Type] * [Container].[ContainerID]) on row, ({Measure.[Loading Method From Site_Default], Measure.[Loading Method From Site_Valid Flag]}) on column;
ㄴ 개발 직관용
    Select (
        [Version].[Version Name]
        * [Sub Location].[Sub Location]
        * [Container].[ContainerID]
        * [Loading Type].[Loading Type]
        * [Shipment Type].[Shipment Type]
    ) on row
    , ({
        Measure.[Loading Method From Site_Default]
        , Measure.[Loading Method From Site_Valid Flag]
    }) on column;
- in_Site_Sales_Association
ㄴ o9 upload용
    Select ([Version].[Version Name] * [Location].[Location] * [Sales Domain].[Ship To] ) on row, ({Measure.[Site Sales Asn_Max Asn], Measure.[Site Sales Asn_Site Sales Asn]}) on column;
ㄴ 개발 직관용
    Select (
        [Version].[Version Name]
        * [Location].[Location]
        * [Sales Domain].[Ship To]
    ) on row
    , ({
        Measure.[Site Sales Asn_Max Asn]
        , Measure.[Site Sales Asn_Site Sales Asn]
    }) on column;

- in_Loading_Dir_Order_Mgmt
ㄴ o9 upload용
    Select ([Version].[Version Name] * [Sub Location].[Sub Location] * [Seq].[Seq] * [Item].[Item] * [Location].[Location]  * [Sales Domain].[Ship To] * [Time].[Week]) on row,({Measure.[Loading Dir Order Mgmt_Sales Order]}) on column;
ㄴ 개발 직관용
    Select (
        [Version].[Version Name]
        * [Sub Location].[Sub Location]
        * [Location].[Location]
        * [Sales Domain].[Ship To]
        * [Item].[Item]
        * [Time].[Week]
        * [Seq].[Seq]
    ) on row
    ,({
        Measure.[Loading Dir Order Mgmt_Sales Order]
    }) on column;

* Output Tables
    - df_out_Loading_Mgmt_Upload
        Select (
            [Version].[Version Name].CWV_MP
            * [Personnel].[Email]
            * [Time].[Week]
            * [Seq].[Seq]
        ) on row,
        ({
            Measure.[Loading Mgmt Upload_From Site]
            , Measure.[Loading Mgmt Upload_To Site]
            , Measure.[Loading Mgmt Upload_Account]
            , Measure.[Loading Mgmt Upload_Account Name]
            , Measure.[Loading Mgmt Upload_Project]
            , Measure.[Loading Mgmt Upload_Product Group]
            , Measure.[Loading Mgmt Upload_Product]
            , Measure.[Loading Mgmt Upload_Loading Type]
            , Measure.[Loading Mgmt Upload_Cntr Type]
            , Measure.[Loading Mgmt Upload_Org Qty]
            , Measure.[Loading Mgmt Upload_Chk Qty]
            , Measure.[Loading Mgmt Upload_Valid Flag]
        }) on column;

    - df_out_Loading_DirOrder_Mgmt
        Select (
            [Version].[Version Name].CWP_MP
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
        }) on column;

* 기존 메저 데이터 삭제(nullify)
    * Measure 삭제
    Scope: (
        [Version].[Version Name].[CWV_MP]
        * [Personnel].[Email].[soonup92.jee@partner.samsung.com]
    );
        Measure.[Loading Mgmt Upload_From Site] = null;
        Measure.[Loading Mgmt Upload_To Site] = null;
        Measure.[Loading Mgmt Upload_Account] = null;
        Measure.[Loading Mgmt Upload_Account Name] = null;
        Measure.[Loading Mgmt Upload_Project] = null;
        Measure.[Loading Mgmt Upload_Product Group] = null;
        Measure.[Loading Mgmt Upload_Product] = null;
        Measure.[Loading Mgmt Upload_Loading Type] = null;
        Measure.[Loading Mgmt Upload_Cntr Type] = null;
        Measure.[Loading Mgmt Upload_Org Qty] = null;
        Measure.[Loading Mgmt Upload_Chk Qty] = null;
        Measure.[Loading Mgmt Upload_Valid Flag] = null;
    end scope;

* Validation :

* Execution :
1. EXEC 파이썬 모듈 실행
    EXEC plugin instance [PY_UI_LoadingMgmtUpload_REG]
    for measures {
                    [Loading Mgmt Upload_From Site]
                }
    using scope (
                    [Version].[Version Name].[CWV_MP]
                )
    using arguments {
        (ExecutionMode, "MediumWeight")
        , (Param_OUT_VERSION, "CWV_MP")
        , (MaxSliceTableCells, 200000000)
        , (MaxConcurrency, 1 )
        , (IncludeNullRows, False)
        , ([Param.o9_sys_log_level], "DEBUG")
    };
2. out Measure그룹 모든 Measure 데이터 삭제
delete data for model [Loading Dir Order Mgmt] where {[Version].[Version Name].[CWV_MP]};
3. Loading Dir Order Mgmt 해당 measure nullify
Scope: (
    [Version].[Version Name].[CWV_MP]
);
Measure.[Loading Dir Mgmt_Sales Order] = null;
Measure.[Loading Dir Mgmt_Adj Prod Week] = null;
Measure.[Loading Dir Mgmt_RDD Week] = null;
Measure.[Loading Dir Mgmt_Ship To] = null;
Measure.[Loading Dir Mgmt_Ship To Name] = null;
Measure.[Loading Dir Mgmt_Loading Type] = null;
Measure.[Loading Dir Mgmt_Container Type] = null;
Measure.[Loading Dir Mgmt_Org Qty] = null;
Measure.[Loading Dir Mgmt_Chk Qty] = null;
Measure.[Loading Dir Mgmt_InitBy] = null;
Measure.[Loading Dir Mgmt_InitDttm] = null;
end scope;
"""
import os.path
import time
import pandas as pd
import traceback
import re
import numpy as np
import inspect
import datetime
from NSCMCommon import NSCMCommon as common

# Local 개발 시에 필요한 공통 변수 선언
# o9에 저장된 instanceName
str_instance = "PY_UI_LoadingMgmtUpload_REG"
str_input_dir = "Input/UILoadingMgmtUploadREG"
str_output_dir = "Output/UILoadingMgmtUploadREG"
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
    # df_out_LoadingDirMgmt
    if str_p_cond == '0':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Sales Domain.[Ship To]': [], 'Item.[Item]': [], 'Time.[Week]': [], 'Seq.[Seq]': [],
                'Loading Dir Mgmt_Sales Order': [], 'Loading Dir Mgmt_Adj Prod Week': [],
                'Loading Dir Mgmt_RDD Week': [], 'Loading Dir Mgmt_Ship To': [],
                'Loading Dir Mgmt_Ship To Name': [], 'Loading Dir Mgmt_Loading Type': [],
                'Loading Dir Mgmt_Container Type': [], 'Loading Dir Mgmt_Org Qty': [],
                'Loading Dir Mgmt_Chk Qty': [], 'Loading Mgmt Upload_Confirmed By': [],
                'Loading Mgmt Upload_Confirm Time': []
            }
        )
    else:
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Sub Location.[Sub Location]': [], 'Location.[Location]': [],
                'Sales Domain.[Ship To]': [], 'Item.[Item]': [], 'Time.[Week]': [], 'Seq.[Seq]': [],
                'Loading Dir Order Mgmt_SO Item': [], 'Loading Dir Order Mgmt_Sales Order': [],
                'Loading Dir Order Mgmt_Adj Prod Week': [], 'Loading Dir Order Mgmt_RDD Week': [],
                'Loading Dir Order Mgmt_Ship To': [], 'Loading Dir Order Mgmt_Ship To Name': [],
                'Loading Dir Order Mgmt_Loading Type': [], 'Loading Dir Order Mgmt_Cntr Type': [],
                'Loading Dir Order Mgmt_Origin Qty': [], 'Loading Dir Order Mgmt_Chk Qty': []
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
        if column == 'Loading Dir Order Upload_Ship To':
            df_return['Loading Dir Order Upload_Ship To'] = df_return['Loading Dir Order Upload_Ship To'].astype('str')
        elif column == 'Shipment To.[Shipment To]':
            df_return['Shipment To.[Shipment To]'] = df_return['Shipment To.[Shipment To]'].astype('str')
        elif column == 'Loading Method Ship To_Ship To':
            df_return['Loading Method Ship To_Ship To'] = df_return['Loading Method Ship To_Ship To'].astype('str')
        # elif column == 'Loading Mgmt Upload_Account':
        #     df_return['Loading Mgmt Upload_Account'] = df_return['Loading Mgmt Upload_Account'].astype('str')
        elif column == 'Sales Domain.[Ship To]':
            df_return['Sales Domain.[Ship To]'] = df_return['Sales Domain.[Ship To]'].astype('str')
        elif column == 'Loading Mgmt Upload_Confirmed By':
            df_return = df_return[
                df_return['Loading Mgmt Upload_Confirmed By'] == Param_Upload_Confirmed_BY
            ]

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


def fn_output_formatter(df_p_source: pd.DataFrame, str_p_out_version: str, str_p_format_type: str) -> pd.DataFrame:
    """
    최종 Output 형태로 가공하기
    :param df_p_source: df_ItemBOMRouting_concat, df_MfgNetwork_concat, df_ItemBODLaneFrozenWindow_concat
    :param str_p_out_version: Param_OUT_VERSION
    :return: DataFrame
    """
    # 함수 시작 시각
    tm_start = time.time()

    # 함수명
    str_my_name = 'fn_output_formatter'

    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터(str_p_out_version)가 비어 있는 경우 오류를 발생시키고 함수를 종료한다.
    if str_p_out_version is None or str_p_out_version.strip() == '':
        raise Exception(f'Exception: Param_OUT_VERSION(str_p_out_version)이 비어 있습니다. : {str_my_name}')

    # 파라미터 테이블(df_p_source)이 비어 있는 경우 output형태의 header가 존재하는 데이터프레임 생성 한다.
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return

    # 데이터 가공 전 DF 복사
    df_return = df_p_source.copy(deep=True)
    if str_p_format_type == '1':
        df_return = df_return[
            [
                'Version.[Version Name]', 'Personnel.[Email]', 'Seq.[Seq]', 'Time.[Week]',
                'Loading Mgmt Upload_Sales Order', 'Loading Mgmt Upload_RDD Week', 'Loading Mgmt Upload_Adj Prod Week',
                'Loading Mgmt Upload_From Site', 'Loading Mgmt Upload_To Site',
                'Loading Mgmt Upload_Account', 'Loading Mgmt Upload_Account Name',
                'Loading Mgmt Upload_Ship To', 'Loading Mgmt Upload_Ship To Name', 'Loading Mgmt Upload_Item',
                'Loading Mgmt Upload_Project', 'Loading Mgmt Upload_Product Group', 'Loading Mgmt Upload_Product',
                'Loading Mgmt Upload_Shipment Type', 'Loading Mgmt Upload_Loading Type',
                'Loading Mgmt Upload_Cntr Type',
                'Loading Mgmt Upload_Org Qty', 'Loading Mgmt Upload_Chk Qty', 'Loading Mgmt Upload_Valid Flag',
                'Loading Mgmt Upload_Confirmed By', 'Loading Mgmt Upload_Confirm Time'
            ]
        ]
    elif str_p_format_type == '2':
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
            [
                'Version.[Version Name]', 'Sub Location.[Sub Location]', 'Location.[Location]',
                'Sales Domain.[Ship To]', 'Item.[Item]', 'Time.[Week]', 'Seq.[Seq]',
                'Loading Dir Order Mgmt_SO Item', 'Loading Dir Order Mgmt_Sales Order',
                'Loading Dir Order Mgmt_Adj Prod Week', 'Loading Dir Order Mgmt_Prod Week',
                'Loading Dir Order Mgmt_Ship To', 'Loading Dir Order Mgmt_Ship To Name',
                'Loading Dir Order Mgmt_Loading Type', 'Loading Dir Order Mgmt_Cntr Type',
                'Loading Dir Order Mgmt_Origin Qty', 'Loading Dir Order Mgmt_Chk Qty',
                'Loading Dir Order Mgmt_Creation Time', 'Loading Dir Order Mgmt_Created By',
                'Loading Dir Order Mgmt_Chk Grain'
            ]
        ]

    # 함수 종료 시각
    tm_end = time.time()
    # 함수 실행 시간 로그
    logger.Note(p_note=f'[{str_my_name}] Total time is {tm_end - tm_start:.5f} sec.',
                p_log_level=LOG_LEVEL.debug())

    # 결과 리턴
    return df_return


@_decoration_
def fn_insert_displayname_iteminfo_loading_upload_order(
        df_p_source: pd.DataFrame, dict_p_dims: dict, str_p_division
) -> pd.DataFrame:
    """
    누락된 From, To Site, Account, Ship To Name을 넣기
    :param df_p_source: df_Odr_Upd를 param으로 받은 DataFrame
    :param dict_p_dims: check를 위한 Dimension DataFrame dict
    :param str_p_division: 누락된 Account를 넣은뒤 Account Name을 넣기 위해 구분 param
    :return:
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

    df_return = df_p_source.copy()

    if str_p_division == 'TOTAL':
        # Loading Order Upload Check를 위한 Dimension꺼내기
        df_dimension_from_site = dict_p_dims.get('in_Dimension_From_Site')
        df_dimension_to_site = dict_p_dims.get('in_Dimension_To_Site')
        df_dimension_account = dict_p_dims.get('in_Dimension_Account')
        df_dimension_item = dict_p_dims.get('in_Dimension_Item')

        # Insert Loading Mgmt Upload_From Site  *****
        # Display Name 수기 입력으로 인한 소문자에 대한 merge 누락 대비
        df_return['Loading Mgmt Upload_From Site Name Upper'] = df_return['Loading Mgmt Upload_From Site Name'].fillna('').str.upper()
        df_dimension_from_site['From Site Name Upper'] = df_dimension_from_site[str_sub_location_display].str.upper()
        df_return = pd.merge(
            df_return, df_dimension_from_site
            , left_on='Loading Mgmt Upload_From Site Name Upper', right_on='From Site Name Upper'
            , how='left', indicator=True
        )
        df_return['Loading Mgmt Upload_From Site'] = np.where(
            df_return['_merge'] == 'both'
            , df_return['Sub Location.[Sub Location]']
            , 'Not Defined'
        )
        df_return.drop(
            ['_merge', 'Loading Mgmt Upload_From Site Name Upper', 'From Site Name Upper'], axis=1, inplace=True
        )
        # Insert Loading Dir Order Upload_To Site Name &  Shipment Type*****
        # Display Name 수기 입력으로 인한 소문자에 대한 merge 누락 대비
        df_return['Loading Mgmt Upload_To Site Name Upper'] = df_return['Loading Mgmt Upload_To Site Name'].fillna('').str.upper()
        df_dimension_to_site['To Site Name Upper'] = df_dimension_to_site[str_location_display].str.upper()
        df_return = pd.merge(
            df_return, df_dimension_to_site
            , left_on='Loading Mgmt Upload_To Site Name Upper', right_on='To Site Name Upper'
            , how='left', indicator=True
        )
        df_return['Loading Mgmt Upload_To Site'] = np.where(
            df_return['_merge'] == 'both'
            , df_return['Location.[Location]']
            , 'Not Defined'
        )
        df_return['Loading Mgmt Upload_Shipment Type'] = np.where(
            df_return['_merge'] == 'both'
            , df_return['Location.[Shipment Type]']
            , 'Not Defined'
        )
        df_return.drop(
            ['_merge', 'Loading Mgmt Upload_To Site Name Upper', 'To Site Name Upper'], axis=1, inplace=True
        )
        # Insert Loading Dir Order Upload_Account Name *****
        # 만약 Account가 누락된 경우 왼쪽하단의 분홍색 상자 기준으로 로직구현 부탁드리니다.
        # ASSOCIATION(가칭)이라는 MG을 생성할예정이고, 여기에 SITEID와 ACCOUNT정보간의 관계가 정의됩니다.
        df_return['Loading Mgmt Upload_Account'] = np.where(
            df_return['Loading Mgmt Upload_Account'].isna(),
            '',
            df_return['Loading Mgmt Upload_Account']
        )
        # Loading Mgmt Upload_Account Object이지만 Sales Domain.[Ship To]와 merge가 안되서 형변환
        df_return['Loading Mgmt Upload_Account'] = df_return['Loading Mgmt Upload_Account'].astype('str')
        df_return = pd.merge(
            df_return, df_dimension_account
            , left_on='Loading Mgmt Upload_Account', right_on='Sales Domain.[Ship To]'
            , how='left', indicator=True
        )
        df_return['Loading Mgmt Upload_Account Name'] = np.where(
            df_return['_merge'] == 'both'
            , df_return[str_account_display]
            , 'Not Defined'
        )
        df_return.drop(['_merge', 'Sales Domain.[Ship To]', str_account_display], axis=1, inplace=True)
        # Insert Loading Dir Order Upload_Project, Product Group, Product *****
        df_return['Loading Mgmt Upload_Item'] = np.where(
            df_return['Loading Mgmt Upload_Item'].isna(),
            '',
            df_return['Loading Mgmt Upload_Item']
        )
        df_return = pd.merge(
            df_return, df_dimension_item
            , left_on='Loading Mgmt Upload_Item', right_on='Item.[Item]'
            , how='left', indicator=True
        )
        # Insert Loading Dir Order Upload_Project
        df_return['Loading Mgmt Upload_Project'] = np.where(
            df_return['_merge'] == 'both'
            , df_return['Item.[Project]']
            , 'Not Defined'
        )
        # Insert Loading Dir Order Upload_Product Group
        df_return['Loading Mgmt Upload_Product Group'] = np.where(
            df_return['_merge'] == 'both'
            , df_return['Item.[Product Group]']
            , 'Not Defined'
        )
        # Insert Loading Dir Order Upload_Product
        df_return['Loading Mgmt Upload_Product'] = np.where(
            df_return['_merge'] == 'both'
            , df_return['Item.[Product]']
            , 'Not Defined'
        )
        df_return.drop('_merge', axis=1, inplace=True)
    else:   # 누락되 Account를 구하고 Account Name을 다시 구하기 위해
        df_return['Loading Mgmt Upload_Account'] = np.where(
            df_return['Loading Mgmt Upload_Account'].isna(),
            '',
            df_return['Loading Mgmt Upload_Account']
        )
        # Loading Mgmt Upload_Account Object이지만 Sales Domain.[Ship To]와 merge가 안되서 형변환
        df_return['Loading Mgmt Upload_Account'] = df_return['Loading Mgmt Upload_Account'].astype('str')
        # Loading Order Upload Check를 위한 Dimension꺼내기
        df_dimension_account = dict_p_dims.get('in_Dimension_Account')
        # Insert Loading Dir Order Upload_Account Name *****
        df_return = pd.merge(
            df_return, df_dimension_account
            , left_on='Loading Mgmt Upload_Account', right_on='Sales Domain.[Ship To]'
            , how='left', indicator=True
        )

        df_return = fn_merge_after(df_return)

        df_return['Loading Mgmt Upload_Account Name'] = np.where(
            df_return['_merge'] == 'both'
            , df_return[str_account_display]
            , 'Not Defined'
        )

        df_return.drop('_merge', axis=1, inplace=True)

    return df_return


@_decoration_
def fn_update_empty_loadingtype_containerid(
        df_p_loading_mgmt_upload: pd.DataFrame, df_p_loading_methods: pd.DataFrame,
        list_p_loading_mgmt_columns: list, list_p_loading_methods_columns: list,
        str_method_type: str, str_measure_type: str
) -> pd.DataFrame:
    """
    :param df_p_loading_mgmt_upload: Mgmt Upload 데이타프레임
    :param df_p_loading_methods: from ~ ship to Methods 데이타프레임
    :param list_p_loading_mgmt_columns: Mgmt Upload 사용될 columns List
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
    if df_p_loading_mgmt_upload.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_mgmt_upload)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_return
    if df_p_loading_methods.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_loading_methods) ' + str_method_type + '가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_loading_mgmt_upload

    # Loading Mgmt Upload_Loading Type NaN인 데이타 프레임만 선별한다.
    df_p_loading_mgmt_upload_undefined_loadingtype = df_p_loading_mgmt_upload.loc[
        df_p_loading_mgmt_upload[str_measure_type].isna(),
        list_p_loading_mgmt_columns
    ]
    query_string = f'`Loading Method {str_method_type}_Default` == "Y" & `Loading Method {str_method_type}_Valid Flag` == "Y"'
    # Method from~Ship To에서 Loading Type 가져오기
    df_p_loading_methods_default_valid_y = df_p_loading_methods.query(query_string)

    df_p_loading_mgmt_upload_undefind_loadingtype = pd.merge(
        df_p_loading_mgmt_upload_undefined_loadingtype, df_p_loading_methods_default_valid_y,
        left_on=list_p_loading_mgmt_columns[1:], right_on=list_p_loading_methods_columns,
        how='inner'
    )
    # 컬럼중복제거
    df_p_loading_mgmt_upload_undefind_loadingtype = fn_merge_after(df_p_loading_mgmt_upload_undefind_loadingtype)
    df_p_loading_mgmt_upload_undefind_loadingtype = df_p_loading_mgmt_upload_undefind_loadingtype[
        [
            'Seq.[Seq]',
            'Loading Type.[Loading Type]' if str_measure_type == 'Loading Mgmt Upload_Loading Type' else
            'Container.[ContainerID]'
        ]
    ]
    # unique한 Seq.[Seq]가 나왔다는건 Loading Method from ~ Ship To unique하지 않을수 있다는것이므로 첫번째거 하나만
    df_p_loading_mgmt_upload_undefind_loadingtype = df_p_loading_mgmt_upload_undefind_loadingtype.drop_duplicates(
        subset='Seq.[Seq]', keep='first'
    )
    # loadingType&ContainerID가 누락된 loading_mgmt_upload에 from ~ Ship To Method에서 가져와서 넣어주기위해merge
    df_return = pd.merge(
        df_p_loading_mgmt_upload, df_p_loading_mgmt_upload_undefind_loadingtype,
        on='Seq.[Seq]', how='left', indicator=True
    )
    # undefined있는 Seq.[Seq]와 upload Loading Mgmt Seq.[Seq]를 merge하여 Loding Type과 Container ID update
    df_return.loc[
        df_return['_merge'] == 'both', str_measure_type
    ] = df_return[
        'Loading Type.[Loading Type]' if str_measure_type == 'Loading Mgmt Upload_Loading Type' else
        'Container.[ContainerID]'
    ]
    # _merge & merge로 인한 계속 생성되어 오류를 일으키는 컬럼 삭제
    df_return.drop([
        '_merge',
        'Loading Type.[Loading Type]' if str_measure_type == 'Loading Mgmt Upload_Loading Type' else
        'Container.[ContainerID]'
    ], axis=1, inplace=True)

    return df_return


if __name__ == '__main__':
    logger.debug(f'[START] {str_instance}')
    logger.Start()
    # Output 테이블 선언
    df_out_Loading_Mgmt_Upload = pd.DataFrame()
    df_out_Loading_DirOrder_Mgmt = pd.DataFrame()
    # O9 EXEC Medium실행시 DisplayName property명을 key로 인식하므로 선언 로컬에서쓰는 key명 is_local에 선언
    str_location_display = 'Location.[Location$DisplayName]'
    str_location_shipmentType = 'Location.[Shipment Type]'
    str_sub_location_display = 'Sub Location.[Sub Location$DisplayName]'
    str_account_display = 'Sales Domain.[Ship To$DisplayName]'
    str_shipment_to_display = 'Shipment To.[Shipment To$DisplayName]'
    try:
        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = ''
            Param_PLANTYPE = ''
            #  knoxId -> CurrentUser().[User Name] 으로 변경 by Miss.Lee 25.08.22
            Param_Upload_Confirmed_BY = 'daeun01.yun'

            in_Loading_Mgmt_Upload = pd.read_csv(str_input_dir + "/in_Loading_Mgmt_Upload.csv", encoding="UTF8")
            in_Loading_Method_Ship_To = pd.read_csv(str_input_dir + "/in_Loading_Method_Ship_To.csv", encoding="UTF8")
            in_Loading_Method_Account = pd.read_csv(str_input_dir + "/in_Loading_Method_Account.csv", encoding="UTF8")
            in_Loading_Method_To_Site = pd.read_csv(str_input_dir + "/in_Loading_Method_To_Site.csv", encoding="UTF8")
            in_Loading_Method_From_Site = pd.read_csv(str_input_dir + "/in_Loading_Method_From_Site.csv", encoding="UTF8")
            in_Dimension_Item = pd.read_csv(str_input_dir + "/in_Dimension_Item.csv", encoding="UTF8")
            in_Dimension_Account = pd.read_csv(str_input_dir + "/in_Dimension_Account.csv", encoding="UTF8")
            in_Dimension_To_Site = pd.read_csv(str_input_dir + "/in_Dimension_To_Site.csv", encoding="UTF8")
            in_Dimension_From_Site = pd.read_csv(str_input_dir + "/in_Dimension_From_Site.csv", encoding="UTF8")
            in_Site_Sales_Association = pd.read_csv(str_input_dir + "/in_Site_Sales_Association.csv", encoding="UTF8")
            in_Loading_Dir_Order_Mgmt = pd.read_csv(str_input_dir + "/in_Loading_Dir_Order_Mgmt.csv", encoding="UTF8")
            # $DisplayName 로컬일때 처리
            str_location_display = 'Location.[DisplayName]'
            str_sub_location_display = 'Sub Location.[DisplayName]'
            str_account_display = 'Sales Domain.[DisplayName]'
            str_shipment_to_display = 'Shipment To.[DisplayName]'
            in_Dimension_Account = fn_preprocess(in_Dimension_Account)

        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')

        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())

        logger.Note(p_note=f'Param_Upload_Confirmed_BY : {Param_Upload_Confirmed_BY}')

        fn_check_input_table(in_Loading_Mgmt_Upload, 'in_Loading_Mgmt_Upload', '0')
        fn_check_input_table(in_Loading_Method_Ship_To, 'in_Loading_Method_Ship_To', '1')
        fn_check_input_table(in_Loading_Method_Account, 'in_Loading_Method_Account', '1')
        fn_check_input_table(in_Loading_Method_To_Site, 'in_Loading_Method_To_Site', '1')
        fn_check_input_table(in_Loading_Method_From_Site, 'in_Loading_Method_From_Site', '1')
        fn_check_input_table(in_Dimension_Item, 'in_Dimension_Item', '0')
        fn_check_input_table(in_Dimension_Account, 'in_Dimension_Account', '0')
        fn_check_input_table(in_Dimension_To_Site, 'in_Dimension_To_Site', '0')
        fn_check_input_table(in_Dimension_From_Site, 'in_Dimension_From_Site', '0')
        fn_check_input_table(in_Site_Sales_Association, 'in_Site_Sales_Association', '1')
        fn_check_input_table(in_Loading_Dir_Order_Mgmt, 'in_Loading_Dir_Order_Mgmt', '1')

        # in_Loading_Mgmt_Upload DataFrame 컬럼 선처리
        df_Loading_Mgmt_Upload = fn_preprocess(in_Loading_Mgmt_Upload)
        in_Loading_Method_Ship_To = fn_preprocess(in_Loading_Method_Ship_To)
        in_Loading_Method_Account = fn_preprocess(in_Loading_Method_Account)
        # Step 1 #######################################################################################################
        # 'Loading Mgmt Upload_Sales Order' Measure
        # 입력값이 있는 경우 유지함, 단 없는 경우 'Manual_작업일자_Seq.[Seq]순으로 작성한다' 변경되어 아래로직으로
        # 반영 메저 : Loading Dir Order Mgmt (메져그룹) => Loading Dir Order Mgmt_Sales Order
        # df_Loading_Mgmt_Upload.loc[
        #     df_Loading_Mgmt_Upload['Loading Mgmt Upload_Sales Order'].isna(),
        #     'Loading Mgmt Upload_Sales Order'
        # ] = (
        #         'Manual_' +
        #         pd.to_datetime('today').strftime('%Y-%m-%d') +
        #         '_' +
        #         df_Loading_Mgmt_Upload['Seq.[Seq]'].astype('str')
        # )

        df_Loading_Mgmt_Upload['Loading Mgmt Upload_Sales Order'] = np.where(
            df_Loading_Mgmt_Upload['Loading Mgmt Upload_Sales Order'].isna(),
            'Manual',
            df_Loading_Mgmt_Upload['Loading Mgmt Upload_Sales Order']
        )

        # 'Loading Mgmt Upload_Ship To' 값이 없는 경우 '-'로 들어오고 별도 validation chk는 안함
        df_Loading_Mgmt_Upload.loc[
            df_Loading_Mgmt_Upload['Loading Mgmt Upload_Ship To'].isna(),
            'Loading Mgmt Upload_Ship To'
        ] = '-'
        # 'Loading Mgmt Upload_Ship To Name' 값이 없는 경우 '-'로 들어오고 별도 validation chk는 안함
        df_Loading_Mgmt_Upload.loc[
            df_Loading_Mgmt_Upload['Loading Mgmt Upload_Ship To Name'].isna(),
            'Loading Mgmt Upload_Ship To Name'
        ] = '-'
        # Step 2 #######################################################################################################
        # 'Loading Mgmt Upload_Adj Prod Week' Measure
        # 입력값이 있는 경우 유지함.
        # 단 없는 경우, Time.[Week]를 그대로 반영함.
        # 반영 메저 : Loading Dir Order Mgmt (메져그룹) => Loading Dir Order Mgmt_Adj Prod Week(메져)
        df_Loading_Mgmt_Upload.loc[
            df_Loading_Mgmt_Upload['Loading Mgmt Upload_Adj Prod Week'].isna(),
            'Loading Mgmt Upload_Adj Prod Week'
        ] = df_Loading_Mgmt_Upload['Time.[Week]']

        # Step 3 #######################################################################################################
        # 3-1.'Loading Mgmt Upload_From Site' Measure
        # 	(Python Validation내 Attr chk)
        # 	'From Site Name'값을 VALIDATION 이후 반영되는 결과 값이 없으면
        # 		'Not Defined'이라고 표기 후, 붉은 색으로 표기
        # 	Validation이 정상적으로 수행된 경우
        # 		반영 메저 : Loading Dir Order Mgmt (메져그룹) => Sub Location.[Sub Location](디멘져)
        # 3-2.'Loading Mgmt Upload_From Site Name'
        # 	(Python Validation내 Attr chk)
        # 	EXCEL UPLOAD 필수 attr, Sub Location.[Sub Location$DisplayName]기준으로 조회하여
        # 	, Sub Location.[Sub Location]값 여부 확인 필요
        # 	사용자 입력 값과 실제 Sub Location.[Sub Location$DisplayName]을 조회 할 때, 두 값 모두 upper처리하여 비교함.
        # fn_insert_displayname_iteminfo_loading_upload_order 보낼 in dimension을 dict로 묶어서 보냄
        dict_log = {
            'p_step_no': 310,
            'p_step_desc': 'Step3 ~ Step7 From, To Site, Account, Ship to 코드로 들어오는 값을'
                           ' DisplayName 채우기 및 item Info 넣기',
            'p_df_name': 'fn_insert_displayname_iteminfo_loading_upload_order'
        }
        dict_Dims_For_DisplayName_ItemInfo = {
            'in_Dimension_Item': in_Dimension_Item,
            'in_Dimension_From_Site': in_Dimension_From_Site,
            'in_Dimension_To_Site': in_Dimension_To_Site,
            'in_Dimension_Account': in_Dimension_Account
        }
        # 함수호출: fn_insert_displayname_iteminfo_loading_upload_order
        df_Loading_Mgmt_Upload = fn_insert_displayname_iteminfo_loading_upload_order(
            df_Loading_Mgmt_Upload, dict_Dims_For_DisplayName_ItemInfo, 'TOTAL', **dict_log
        )
        # Step 3 #######################################################################################################
        # 만약 Account가 누락된 경우 왼쪽하단의 분홍색 상자 기준으로 로직구현 부탁드리니다.
        # ASSOCIATION(가칭)이라는 MG을 생성할예정이고, 여기에 SITEID와 ACCOUNT정보간의 관계가 정의됩니다.
        # 사용자가 입력한 Site 기준으로 max(Account)를 조회하여 대표값 1개로 일괄 반영으로 반영해 주시면 됩니다.
        if (
                (df_Loading_Mgmt_Upload['Loading Mgmt Upload_Account'].isna()) |
                (df_Loading_Mgmt_Upload['Loading Mgmt Upload_Account'] == '')
        ).any():
            # Loading Mgmt Upload_Account NaN인 데이타 프레임만 선별한다.
            df_Loading_Mgmt_Upload_Undefined_Account = df_Loading_Mgmt_Upload.loc[
                (df_Loading_Mgmt_Upload['Loading Mgmt Upload_Account'] == '') |
                (df_Loading_Mgmt_Upload['Loading Mgmt Upload_Account'].isna()),
                ['Seq.[Seq]', 'Loading Mgmt Upload_To Site']
            ]

            df_Loading_Mgmt_Upload_Undefined_Account = pd.merge(
                df_Loading_Mgmt_Upload_Undefined_Account, in_Site_Sales_Association,
                left_on='Loading Mgmt Upload_To Site', right_on='Location.[Location]',
                how='inner'
            )
            df_Loading_Mgmt_Upload_Undefined_Account = df_Loading_Mgmt_Upload_Undefined_Account.loc[
                df_Loading_Mgmt_Upload_Undefined_Account['Site Sales Asn_Max Asn'].notna(),
                ['Seq.[Seq]', 'Sales Domain.[Ship To]']
            ]

            df_Loading_Mgmt_Upload_Undefined_Account.rename(
                columns={
                    'Sales Domain.[Ship To]': 'Site_Sales_Association_Ship_To',
                }, inplace=True
            )

            df_Loading_Mgmt_Upload = pd.merge(
                df_Loading_Mgmt_Upload, df_Loading_Mgmt_Upload_Undefined_Account,
                on='Seq.[Seq]', how='left', indicator=True
            )

            df_Loading_Mgmt_Upload.loc[
                df_Loading_Mgmt_Upload['_merge'] == 'both',
                'Loading Mgmt Upload_Account'
            ] = df_Loading_Mgmt_Upload['Site_Sales_Association_Ship_To']

            df_Loading_Mgmt_Upload.drop('_merge', axis=1, inplace=True)

            dict_Dims_For_DisplayName_ItemInfo = {
                'in_Dimension_Account': in_Dimension_Account
            }

            df_Loading_Mgmt_Upload = fn_insert_displayname_iteminfo_loading_upload_order(
                df_Loading_Mgmt_Upload, dict_Dims_For_DisplayName_ItemInfo, 'Account', ** dict_log
            )

        # Step8. 'Loading Mgmt Upload_Loading Type'
        # 8-1 (Python Validation내 Attr Chk, 소문자 존재 시 upper처리함) EXCEL UPLOAD 필수 attr
        # 	, LoadingType.[Loading Type]에 존재하는지 chk함.
        # 8-2 Loading Method (From Site/To Site/Account/Ship To)기준정보에서
        # 	, Loading Type, Cntr Type제외 나머지 From~Ship To까지의 컬럼값을 비교하고
        # 	, 대상값에서 Loading Method (From Site/To Site/Account/Ship To) Valid Flag = 'Y'이면서
        # 	, Loading Method (From Site/To Site/Account/Ship To) Default = 'Y'인 Loading Type, Cntr Type을 반영해줌
        # 'Loading Mgmt Upload_Loading Type' 컬럼에 NaN이 존재 하면
        list_mgmt_upload_use_columns = [
            'Seq.[Seq]', 'Loading Mgmt Upload_From Site', 'Loading Mgmt Upload_To Site',
            'Loading Mgmt Upload_Account', 'Loading Mgmt Upload_Ship To'
        ]
        list_loading_methods_use_columns = [
            'Sub Location.[Sub Location]', 'Location.[Location]',
            'Sales Domain.[Ship To]', 'Loading Method Ship To_Ship To'
        ]
        dict_log = {
            'p_step_no': 110,
            'p_step_desc': 'Upload 메져와 Loading Method>Ship To에서 필요 Loading Type measure가져오기',
            'p_df_name': 'df_Loading_Mgmt_Upload_Ship_To'
        }
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Loading Type'].isna().any():
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_Ship_To,
                list_mgmt_upload_use_columns[:], list_loading_methods_use_columns[:],
                'Ship To', 'Loading Mgmt Upload_Loading Type', **dict_log
            )
        dict_log = {
            'p_step_no': 120,
            'p_step_desc': 'Upload 메져와 Loading Method > Account에서 필요 Loading Type measure가져오기',
            'p_df_name': 'df_Loading_Mgmt_Upload_Account'
        }
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Loading Type'].isna().any():
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_Account,
                list_mgmt_upload_use_columns[:4], list_loading_methods_use_columns[:3],
                'Account', 'Loading Mgmt Upload_Loading Type', **dict_log
            )
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Loading Type'].isna().any():
            dict_log = {
                'p_step_no': 130,
                'p_step_desc': 'Upload 메져와 Loading Method > To Site에서 필요 Loading Type measure가져오기',
                'p_df_name': 'df_Loading_Mgmt_Upload_To_Site'
            }
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_To_Site,
                list_mgmt_upload_use_columns[:3], list_loading_methods_use_columns[:2],
                'To Site', 'Loading Mgmt Upload_Loading Type'
            )
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Loading Type'].isna().any():
            dict_log = {
                'p_step_no': 140,
                'p_step_desc': 'Upload 메져와 Loading Method > From Site에서 필요 Loading Type measure가져오기',
                'p_df_name': 'df_Loading_Mgmt_Upload_From_Site'
            }
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_From_Site,
                list_mgmt_upload_use_columns[:2], list_loading_methods_use_columns[:1],
                'From Site', 'Loading Mgmt Upload_Loading Type'
            )
        # From~Ship To Lane Load에 Default 항목에 들어있지 않는 Loading Type일경우 'Default Not Defined' 표시
        df_Loading_Mgmt_Upload.loc[
            df_Loading_Mgmt_Upload['Loading Mgmt Upload_Loading Type'].isna(),
            'Loading Mgmt Upload_Loading Type'
        ] = 'Default Not Defined'
        # Step9. Loading Mgmt Upload_Cntr Type
        # 9-1 (Python Validation내 Attr Chk, 소문자 존재 시 upper처리함) EXCEL UPLOAD 필수 attr
        # , LoadingType.[Loading Type]에 존재하는지 chk함.
        # 9-2 Loading Method ((From Site/To Site/Account/Ship To)기준정보에서,Loading Type, Cntr Type제외 나머지
        # 	From~Ship To까지의 컬럼값을 비교하고, 대상값에서 Loading Method (From Site/To Site/Account/Ship To) Valid Flag = 'Y'이면서
        # 	, Loading Method (From Site/To Site/Account/Ship To) Default = 'Y'인 Cntr Type을 반영해줌
        # 반영 메져 : Loading Dir Order Mgmt(메져그룹) => Loading Dir Order Mgmt_Container Type(메져)값으로 반영
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Cntr Type'].isna().any():
            dict_log = {
                'p_step_no': 210,
                'p_step_desc': 'Upload 메져와 Loading Method > Ship To에서 필요 Cntr Type measure가져오기',
                'p_df_name': 'df_Loading_Mgmt_Upload_Ship_To'
            }
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_Ship_To,
                list_mgmt_upload_use_columns[:], list_loading_methods_use_columns[:],
                'Ship To', 'Loading Mgmt Upload_Cntr Type', **dict_log
            )
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Cntr Type'].isna().any():
            dict_log = {
                'p_step_no': 220,
                'p_step_desc': 'Upload 메져와 Loading Method > Account에서 필요 Cntr Type measure가져오기',
                'p_df_name': 'df_Loading_Mgmt_Upload_Account'
            }
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_Account,
                list_mgmt_upload_use_columns[:4], list_loading_methods_use_columns[:3],
                'Account', 'Loading Mgmt Upload_Cntr Type'
            )

        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Cntr Type'].isna().any():
            dict_log = {
                'p_step_no': 230,
                'p_step_desc': 'Upload 메져와 Loading Method > To Site에서 필요 Cntr Type measure가져오기',
                'p_df_name': 'df_Loading_Mgmt_Upload_To_Site'
            }
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_To_Site,
                list_mgmt_upload_use_columns[:3], list_loading_methods_use_columns[:2],
                'To Site', 'Loading Mgmt Upload_Cntr Type', **dict_log
            )

        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Cntr Type'].isna().any():
            dict_log = {
                'p_step_no': 240,
                'p_step_desc': 'Upload 메져와 Loading Method > From Site에서 필요 Cntr Type measure가져오기',
                'p_df_name': 'df_Loading_Mgmt_Upload_From_Site'
            }
            # 함수 호출
            df_Loading_Mgmt_Upload = fn_update_empty_loadingtype_containerid(
                df_Loading_Mgmt_Upload, in_Loading_Method_From_Site,
                list_mgmt_upload_use_columns[:2], list_loading_methods_use_columns[:1],
                'From Site', 'Loading Mgmt Upload_Cntr Type', **dict_log
            )
        # From~Ship To Lane Load에 Default 항목에 들어있지 않는 Cntr Type일경우 'Default Not Defined' 표시
        df_Loading_Mgmt_Upload.loc[
            df_Loading_Mgmt_Upload['Loading Mgmt Upload_Cntr Type'].isna(),
            'Loading Mgmt Upload_Cntr Type'
        ] = 'Default Not Defined'
        # Step 11. Loading Mgmt Upload_Org Qty
        # 미 입력시 Not Defined. 붉은 색으로 표기함
        # 반영 메저 : Loading Dir Order Mgmt_Org Qty
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Org Qty'].isna().any():
            df_Loading_Mgmt_Upload.loc[
                df_Loading_Mgmt_Upload['Loading Mgmt Upload_Org Qty'].isna(),
                'Loading Mgmt Upload_Org Qty'
            ] = 'Not Defined'
        # Step12. 'Loading Mgmt Upload_Chk Qty'
        # 누락 시 'Loading Mgmt Upload_Org Qty'값 반영함.
        # 반영 메저 : Loading Dir Order Mgmt(메져그룹) => Loading Dir Order Mgmt_Chk Qty(메져)
        if df_Loading_Mgmt_Upload['Loading Mgmt Upload_Chk Qty'].isna().any():
            df_Loading_Mgmt_Upload.loc[
                df_Loading_Mgmt_Upload['Loading Mgmt Upload_Chk Qty'].isna(),
                'Loading Mgmt Upload_Chk Qty'
            ] = df_Loading_Mgmt_Upload['Loading Mgmt Upload_Org Qty']

        # Param_Upload_Confirmed_BY을 param으로 받아서 @앞에 값을 끊어서 넣는다. -> CurrentUser().[User Name] 으로 변경 by Miss.Lee 25.08.22
        df_Loading_Mgmt_Upload['Loading Mgmt Upload_Confirmed By'] = Param_Upload_Confirmed_BY
        # Loading Mgmt Upload_Confirm Time 파이썬 모듈 실행 날짜를 yyyy-MM-dd HH:mm:ss 넣는다.
        df_Loading_Mgmt_Upload['Loading Mgmt Upload_Confirm Time'] = (
                datetime.datetime.now() + datetime.timedelta(hours=9)
        ).strftime('%Y-%m-%d %H:%M:%S') if not is_local else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 'Loading Mgmt Upload_Valid Flag' 컬럼 생성:
        # 아래 컬럼 중 하나라도 'Not Defined'이면 'N', 아니면 'Y'
        df_Loading_Mgmt_Upload['Loading Mgmt Upload_Valid Flag'] = df_Loading_Mgmt_Upload[
            [
                'Loading Mgmt Upload_From Site', 'Loading Mgmt Upload_To Site', 'Loading Mgmt Upload_Account Name',
                'Loading Mgmt Upload_Project', 'Loading Mgmt Upload_Product Group', 'Loading Mgmt Upload_Product',
                'Loading Mgmt Upload_Org Qty', 'Loading Mgmt Upload_Chk Qty',
                'Loading Mgmt Upload_Cntr Type', 'Loading Mgmt Upload_Loading Type'
             ]
        ].apply(lambda row: 'N' if row.str.contains('Not Defined').any() else 'Y', axis=1)
        # Loading Mgmt Upload_Valid Flag 값이 모두 Y가 되어야 Dir_Order_Mgmt out을 생성하고 아니면 빈 컬럼만
        if (df_Loading_Mgmt_Upload['Loading Mgmt Upload_Valid Flag'] == 'Y').all():
            df_out_Loading_DirOrder_Mgmt = df_Loading_Mgmt_Upload.copy()
            df_out_Loading_DirOrder_Mgmt = df_out_Loading_DirOrder_Mgmt[
                [
                    'Version.[Version Name]', 'Time.[Week]',
                    'Loading Mgmt Upload_From Site', 'Loading Mgmt Upload_To Site',
                    'Loading Mgmt Upload_Account', 'Loading Mgmt Upload_Item', 'Loading Mgmt Upload_SO Item',
                    'Loading Mgmt Upload_RDD Week', 'Loading Mgmt Upload_Sales Order',
                    'Loading Mgmt Upload_Adj Prod Week', 'Loading Mgmt Upload_Shipment Type',
                    'Loading Mgmt Upload_Ship To', 'Loading Mgmt Upload_Ship To Name',
                    'Loading Mgmt Upload_Loading Type', 'Loading Mgmt Upload_Cntr Type',
                    'Loading Mgmt Upload_Org Qty', 'Loading Mgmt Upload_Chk Qty'
                ]
            ]

            # 혹시 SO는 입력값 그냥 유지하고, MGMT로 올릴 때, MANUAL_(입력값)
            df_out_Loading_DirOrder_Mgmt['Loading Dir Order Mgmt_Sales Order'] = np.where(
                ~df_Loading_Mgmt_Upload['Loading Mgmt Upload_Sales Order'].str.startswith('Manual'),
                'Manual_' + df_Loading_Mgmt_Upload['Loading Mgmt Upload_Sales Order'],
                df_Loading_Mgmt_Upload['Loading Mgmt Upload_Sales Order']
            )
            # 2025-07-14 윤서정프로 요청
            # Prod Week메저 추가, Adj Prod Week 최초 입력값은 동일.
            df_out_Loading_DirOrder_Mgmt['Loading Dir Order Mgmt_Prod Week'] = df_out_Loading_DirOrder_Mgmt[
                'Loading Mgmt Upload_Adj Prod Week'
            ]
            # 만약에 사용자가 RDD WEEK를안넣으면, PROD WEEK를 Time.[Week]쪽에 반영
            df_out_Loading_DirOrder_Mgmt['Loading Dir Order Mgmt_Adj RDD Week'] = np.where(
                df_out_Loading_DirOrder_Mgmt['Loading Mgmt Upload_RDD Week'].isna(),
                df_out_Loading_DirOrder_Mgmt['Time.[Week]'],
                df_out_Loading_DirOrder_Mgmt['Loading Mgmt Upload_RDD Week']
            )
            df_out_Loading_DirOrder_Mgmt.rename(
                columns={
                    'Loading Mgmt Upload_From Site': 'Sub Location.[Sub Location]',
                    'Loading Mgmt Upload_To Site': 'Location.[Location]',
                    'Loading Mgmt Upload_Account': 'Sales Domain.[Ship To]',
                    'Loading Mgmt Upload_Item': 'Item.[Item]',
                    'Time.[Week]': 'Loading Mgmt Upload_Prod Week',
                    'Loading Dir Order Mgmt_Adj RDD Week': 'Time.[Week]',
                    'Loading Mgmt Upload_Adj Prod Week': 'Loading Dir Order Mgmt_Adj Prod Week',
                    'Loading Mgmt Upload_Ship To': 'Loading Dir Order Mgmt_Ship To',
                    'Loading Mgmt Upload_Ship To Name': 'Loading Dir Order Mgmt_Ship To Name',
                    'Loading Mgmt Upload_Loading Type': 'Loading Dir Order Mgmt_Loading Type',
                    'Loading Mgmt Upload_Cntr Type': 'Loading Dir Order Mgmt_Cntr Type',
                    'Loading Mgmt Upload_Org Qty': 'Loading Dir Order Mgmt_Origin Qty',
                    'Loading Mgmt Upload_Chk Qty': 'Loading Dir Order Mgmt_Chk Qty',
                    'Loading Mgmt Upload_SO Item': 'Loading Dir Order Mgmt_SO Item'
                }, inplace=True
            )
            # Loading Dir Order Mgmt_Creation Time 파이썬 모듈 실행 날짜를 yyyy-MM-dd HH:mm:ss 넣는다.
            df_out_Loading_DirOrder_Mgmt['Loading Dir Order Mgmt_Creation Time'] = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S') if not is_local else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Param_Upload_Confirmed_BY을 param으로 받아서 @앞에 값을 끊어서 넣는다. -> CurrentUser().[User Name] 으로 변경 by Miss.Lee 25.08.22
            df_out_Loading_DirOrder_Mgmt['Loading Dir Order Mgmt_Created By'] = Param_Upload_Confirmed_BY

            int_seq = 1
            if not in_Loading_Dir_Order_Mgmt.empty:
                int_seq = int(
                    in_Loading_Dir_Order_Mgmt[
                        'Seq.[Seq]'
                    ].astype(int).max()
                ) + 1

            df_out_Loading_DirOrder_Mgmt['Seq.[Seq]'] = range(int_seq, int_seq + len(df_out_Loading_DirOrder_Mgmt))
            df_out_Loading_DirOrder_Mgmt = fn_output_formatter(
                df_out_Loading_DirOrder_Mgmt, Param_OUT_VERSION, '2'
            )
        else:
            df_out_Loading_DirOrder_Mgmt = fn_set_header('1')

        df_out_Loading_Mgmt_Upload = fn_output_formatter(
            df_Loading_Mgmt_Upload, Param_OUT_VERSION, '1'
        )
        # Dataframe 확인 로그
        if not df_out_Loading_Mgmt_Upload.empty:
            fn_log_dataframe(df_out_Loading_Mgmt_Upload, 'df_out_Loading_Mgmt_Upload')
        if not df_out_Loading_DirOrder_Mgmt.empty:
            fn_log_dataframe(df_out_Loading_DirOrder_Mgmt, 'df_out_Loading_DirOrder_Mgmt')

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
        if df_out_Loading_Mgmt_Upload.empty:
            df_out_Loading_Mgmt_Upload = fn_set_header('0')
            fn_log_dataframe(df_out_Loading_Mgmt_Upload, 'df_out_Loading_Mgmt_Upload')
        if df_out_Loading_DirOrder_Mgmt.empty:
            df_out_Loading_DirOrder_Mgmt = fn_set_header('1')
            fn_log_dataframe(df_out_Loading_DirOrder_Mgmt, 'df_out_Loading_DirOrder_Mgmt')
