"""
* 프로그램명
    - PY_UI_SOPAdjustInitial

* 내용
    - Raw Data 검증용

* 변경이력
    - 2024.09.19 / 권태우 / Create

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CodeMap : Select ([Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] ) on row, ({Measure.[Code Map LCM_Created By], Measure.[Code Map LCM_Creation Time], Measure.[Code Map LCM_Map Status], Measure.[Code Map LCM_Prod Item], Measure.[Code Map LCM_Update Time], Measure.[Code Map LCM_Updated By], Measure.[Code Map LCM_Valid Flag]}) on column WHERE {[Version].[Version Name].[CurrentWorkingView]}.filter(Measure.[Code Map LCM_Valid Flag] == "Y" && Measure.[Code Map LCM_Map Status] == "COM" && Measure.[Code Map LCM_Prod Item] <> "-");
    - df_in_SETShipmentSETProd : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"SET"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location]) * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1 Flow Type].[SET to DC BOD].relatedmembers([Activity1]) * TO.[Location].[Site Stage].[DC].relatedmembers([Location]) * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETShipmentLCMBOH  : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1].filter(#.Name in {"ExpectedReceiptActivity","BOHActivity"}) * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location]) * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1 Flow Type].[SET to DC BOD].relatedmembers([Activity1]) * TO.[Location].[Site Stage].[DC].relatedmembers([Location]) * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({ Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETShipmentLCMCons : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1 Flow Type].[SET to DC BOD].relatedmembers([Activity1]) * TO.[Location].[Site Stage].[DC].relatedmembers([Location]) * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETShipmentLCMProd : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2].filter(#.Name startswith "RT") * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location]) * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1 Flow Type].[SET to DC BOD].relatedmembers([Activity1]) * TO.[Location].[Site Stage].[DC].relatedmembers([Location]) * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETShipmentOCCons  : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"OPEN_CELL"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location]) * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1 Flow Type].[SET to DC BOD].relatedmembers([Activity1]) * TO.[Location].[Site Stage].[DC].relatedmembers([Location]) * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};

    - df_in_HubShipmentSETProd : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"SET"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentLCMBOH  : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1].filter(#.Name in {"ExpectedReceiptActivity","BOHActivity"})  * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentLCMCons : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM"}).relatedmembers([To Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentLCMProd : Select (Version.[Version Name].[CurrentWorkingView] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2].filter(#.Name startswith "RT") * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};

* Flow Summary

* Output Table
    - df_out_SOPAdjustInitial

* 데이타 초기화
    - DELETE DATA FOR MODEL [SOP Pegging] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SOPAdjustInitial] for measures {[SOP Pegging_From Activity1]}
        using scope (&CWV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPAdjustPegging / MG:  SOP Pegging
        Select ([Version].[Version Name].[CWV_MP]* [Item].[Item] * [Time].[Week] * [Location].[Location] * [Sequence].[Sequence] ) on row,
        ({Measure.[SOP Pegging_Cons To Cons Demand Qty], Measure.[SOP Pegging_Consumer To Consumer From], Measure.[SOP Pegging_Consumer To Consumer To],
            Measure.[SOP Pegging_From Activity1], Measure.[SOP Pegging_From Activity2], Measure.[SOP Pegging_From Activity3], Measure.[SOP Pegging_From Item],
            Measure.[SOP Pegging_From Location], Measure.[SOP Pegging_From OrderlineID], Measure.[SOP Pegging_From Week], Measure.[SOP Pegging_Prod To Cons Demand Qty],
            Measure.[SOP Pegging_Producer To Consumer From], Measure.[SOP Pegging_Producer To Consumer To], Measure.[SOP Pegging_To Activity1], Measure.[SOP Pegging_To Activity2],
            Measure.[SOP Pegging_To Activity3], Measure.[SOP Pegging_To CusTomer Group], Measure.[SOP Pegging_To Demand Type], Measure.[SOP Pegging_To DemandID], Measure.[SOP Pegging_To Item],
            Measure.[SOP Pegging_To Location], Measure.[SOP Pegging_To OrderlineID], Measure.[SOP Pegging_To To Item], Measure.[SOP Pegging_To To Location], Measure.[SOP Pegging_To To Week],
            Measure.[SOP Pegging_To Week], Measure.[SOP Pegging_Type]}) on column limit 100;


"""
import gc
import traceback
from datetime import datetime

import numpy as np
import pandas as pd
import tracemalloc

from NSCMCommon import NSCMCommon as common

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SOPAdjustInitial'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
COMMON_SOURCE_VERSION = common.G_SourceVersion


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", low_memory=False, encoding="UTF-8")


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(f"{file_name}.csv", index=False)


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def is_null_or_all(series):
    return series.isnull() | (series == 'ALL')


def is_all(series):
    return series.isnull() | (series == 'ALL')


def is_not_all(series):
    filled_series = series.fillna('ALL')
    return filled_series != 'ALL'


def replace_year(date_string, new_year):
    try:
        date_object = datetime.strptime(date_string, '%m/%d/%Y %I:%M:%S %p')
    except Exception as e1:
        try:
            date_object = datetime.strptime(date_string, '%Y/%m/%d %I:%M:%S %p')
        except Exception as e2:
            date_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    modified_date_object = date_object.replace(year=new_year)
    return modified_date_object.strftime('%Y-%m-%d')


def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)


def step(no, string):
    logger.Step(p_step_no=no, p_step_desc=f'{string}')


# 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
tracemalloc.start()

logger.debug(f'[START] {str_instance}')
logger.Start()
note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
step(0, '===================== plugin Execution Start =====================')

try:
    ################################################################################################################
    # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
    ################################################################################################################
    step(100, '=====> STEP 1(Start) : 전처리 - 모듈 내에서 사용될 input table load')

    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE

        # csv 파일 이름과 변수명을 매핑한 딕셔너리 생성
        file_mappings = {
            'df_in_CodeMap': 'df_in_CodeMap',
            'df_in_SETShipmentSETProd': 'df_in_SETShipmentSETProd',
            'df_in_SETShipmentLCMBOH': 'df_in_SETShipmentLCMBOH',
            'df_in_SETShipmentLCMCons': 'df_in_SETShipmentLCMCons',
            'df_in_SETShipmentLCMProd': 'df_in_SETShipmentLCMProd',
            'df_in_SETShipmentOCCons': 'df_in_SETShipmentOCCons',
            'df_in_HubShipmentSETProd': 'df_in_HubShipmentSETProd',
            'df_in_HubShipmentLCMCons': 'df_in_HubShipmentLCMCons',
            'df_in_HubShipmentLCMProd': 'df_in_HubShipmentLCMProd',
        }

        # 각 파일을 읽어서 변수에 할당
        for var_name, file_name in file_mappings.items():
            globals()[var_name] = read_csv_file(file_name)


    dataframes = {
        'df_in_CodeMap': df_in_CodeMap,
        'df_in_SETShipmentSETProd': df_in_SETShipmentSETProd,
        'df_in_SETShipmentLCMBOH': df_in_SETShipmentLCMBOH,
        'df_in_SETShipmentLCMCons': df_in_SETShipmentLCMCons,
        'df_in_SETShipmentLCMProd': df_in_SETShipmentLCMProd,
        'df_in_SETShipmentOCCons': df_in_SETShipmentOCCons,
        'df_in_HubShipmentSETProd': df_in_HubShipmentSETProd,
        'df_in_HubShipmentLCMCons': df_in_HubShipmentLCMCons,
        'df_in_HubShipmentLCMProd': df_in_HubShipmentLCMProd,
    }

    skip_names = ['df_in_HubShipmentSETProd', 'df_in_HubShipmentLCMCons', 'df_in_HubShipmentLCMProd']
    for name, df in dataframes.items():
        if name in skip_names:
            continue

        if df.empty:
            raise Exception(f"=====> raise Exception: {name} is empty")


    # 입력 변수 확인
    if paramOutVersion is None or paramOutVersion.strip() == '':
        paramOutVersion = PARAM_OUTVERSION_VALUE

    # input dataframe 확인용 로그
    note(f'=====> paramOutVersion : {paramOutVersion}')

    # 데이터프레임 출력
    for name, df in dataframes.items():
        print_df(df, name)


    step(100, '=====> STEP 1(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 2 : DataFrame Column 변수 처리
    ################################################################################################################
    step(200, '=====> STEP 2(Start) : DataFrame Column 변수 처리')

    # 컬럼 변수 선언
    SEQUENCE_COLUMN = 'Sequence.[Sequence]'
    VERSION_NAME_COLUMN = 'Version.[Version Name]'
    CODE_MAP_LCM_PROD_ITEM_COLUMN = 'Code Map LCM_Prod Item'
    ITEM_COLUMN = 'Item.[Item]'
    TIME_WEEK_COLUMN = 'Time.[Week]'
    LOCATION_COLUMN = 'Location.[Location]'
    TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
    TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
    TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
    SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
    SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
    BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
    SOP_ID_COLUMN = 'SOP ID.[SOP ID]'
    TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
    TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
    WEEK1_COLUMN = 'Week1.[Week1]'
    WEEK2_COLUMN = 'Week2.[Week2]'
    SOP_W_BOM_CFM_W_COLUMN = 'SOP W_BOM Cfm W'
    SOP_W_BOM_STATUS_COLUMN = 'SOP W_BOM Status'
    SOP_W_CHG_QTY_COLUMN = 'SOP W_Chg Qty'
    SOP_W_CHG_REASON_COLUMN = 'SOP W_Chg Reason'
    SOP_W_ITEM_MTRL_COLUMN = 'SOP W_Item Mtrl'
    SOP_W_LCM_PLANT_COLUMN = 'SOP W_LCM Plant'
    SOP_W_PRD_ITEM_COLUMN = 'SOP W_Prd Item'
    SOP_W_SOP_ADJ_QTY_COLUMN = 'SOP W_SOP Adj Qty'
    SOP_W_SOP_QTY_COLUMN = 'SOP W_SOP Qty'
    SOP_W_SHT_QTY_COLUMN = 'SOP W_Sht Qty'
    SOP_W_SHT_REASON_COLUMN = 'SOP W_Sht Reason'

    FROM_TIME_WEEK_COLUMN = 'from.[Time].[Week]'
    FROM_ACTIVITY3_COLUMN = 'from.[Activity3].[Activity3]'
    FROM_ITEM_COLUMN = 'from.[Item].[Item]'
    FROM_ACTIVITY1_COLUMN = 'from.[Activity1].[Activity1]'
    FROM_LOCATION_COLUMN = 'from.[Location].[Location]'
    FROM_ACTIVITY2_COLUMN = 'from.[Activity2].[Activity2]'
    FROM_ORDERLINE_ID_COLUMN = 'from.[Documents].[OrderlineID]'

    TO_TO_TIME_TO_WEEK_COLUMN = 'to.[To Time].[To Week]'
    TO_TO_LOCATION_TO_LOCATION_COLUMN = 'to.[To Location].[To Location]'
    TO_ORDERLINE_ID_COLUMN = 'to.[Documents].[OrderlineID]'
    TO_TIME_WEEK_COLUMN = 'to.[Time].[Week]'
    TO_TO_ITEM_TO_ITEM_COLUMN = 'to.[To Item].[To Item]'
    TO_ITEM_COLUMN = 'to.[Item].[Item]'
    TO_ACTIVITY1_COLUMN = 'to.[Activity1].[Activity1]'
    TO_LOCATION_COLUMN = 'to.[Location].[Location]'
    TO_ACTIVITY3_COLUMN = 'to.[Activity3].[Activity3]'
    TO_DEMAND_ID_COLUMN = 'to.[Demand].[DemandID]'
    TO_CUSTOMER_GROUP_COLUMN = 'to.[Sales Domain].[Customer Group]'
    TO_DEMAND_TYPE_COLUMN = 'to.[Demand Type].[Demand Type]'
    TO_ACTIVITY2_COLUMN = 'to.[Activity2].[Activity2]'
    SOP_BUP_PRODUCER_TO_CFP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]'
    SOP_BUP_CONSUMER_TO_CFP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]'
    SOP_BUP_PRODUCER_TO_CTP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer To Pegged]'
    SOP_BUP_PROD_TO_CDP_QTY_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Prod to Cons Demand Pegged Qty]'

    SOP_BUP_CONSUMER_TO_CTP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer To Pegged]'
    SOP_BUP_CONS_TO_CDP_QTY_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Cons to Cons Demand Pegged Qty]'

    SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN = 'SOP Pegging_Cons To Cons Demand Qty'
    SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN = 'SOP Pegging_Consumer To Consumer From'
    SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN = 'SOP Pegging_Consumer To Consumer To'

    SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN = 'SOP Pegging_Prod To Cons Demand Qty'
    SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN = 'SOP Pegging_Producer To Consumer From'
    SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN = 'SOP Pegging_Producer To Consumer To'

    SOP_PEGGING_FROM_ACTIVITY1_COLUMN = 'SOP Pegging_From Activity1'
    SOP_PEGGING_FROM_ACTIVITY2_COLUMN = 'SOP Pegging_From Activity2'
    SOP_PEGGING_FROM_ACTIVITY3_COLUMN = 'SOP Pegging_From Activity3'
    SOP_PEGGING_FROM_ITEM_COLUMN = 'SOP Pegging_From Item'
    SOP_PEGGING_FROM_LOCATION_COLUMN = 'SOP Pegging_From Location'
    SOP_PEGGING_FROM_ORDERLINEID_COLUMN = 'SOP Pegging_From OrderlineID'
    SOP_PEGGING_FROM_WEEK_COLUMN = 'SOP Pegging_From Week'

    SOP_PEGGING_TO_ACTIVITY1_COLUMN = 'SOP Pegging_To Activity1'
    SOP_PEGGING_TO_ACTIVITY2_COLUMN = 'SOP Pegging_To Activity2'
    SOP_PEGGING_TO_ACTIVITY3_COLUMN = 'SOP Pegging_To Activity3'
    SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN = 'SOP Pegging_To CusTomer Group'
    SOP_PEGGING_TO_DEMAND_TYPE_COLUMN = 'SOP Pegging_To Demand Type'
    SOP_PEGGING_TO_DEMANDID_COLUMN = 'SOP Pegging_To DemandID'
    SOP_PEGGING_TO_ITEM_COLUMN = 'SOP Pegging_To Item'
    SOP_PEGGING_TO_LOCATION_COLUMN = 'SOP Pegging_To Location'
    SOP_PEGGING_TO_ORDERLINEID_COLUMN = 'SOP Pegging_To OrderlineID'
    SOP_PEGGING_TO_TO_ITEM_COLUMN = 'SOP Pegging_To To Item'
    SOP_PEGGING_TO_TO_LOCATION_COLUMN = 'SOP Pegging_To To Location'
    SOP_PEGGING_TO_TO_WEEK_COLUMN = 'SOP Pegging_To To Week'
    SOP_PEGGING_TO_WEEK_COLUMN = 'SOP Pegging_To Week'

    SOP_PEGGING_TYPE_COLUMN = 'SOP Pegging_Type'


    step(200, '=====> STEP 2(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 3 :  데이터 선 가공
    ################################################################################################################
    step(300, '=====> STEP 3(Start) : input data machining')

    # df_in_CodeMap 필요한 컬럼만 발췌
    df_in_CodeMap = df_in_CodeMap[[ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, CODE_MAP_LCM_PROD_ITEM_COLUMN]]


    # ====================> Step 1 (Start) > df_in_SETShipmentSETProd (SET Shipment / SET Prod)
    # 1.1 df_SETShipmentSETProd create
    df_SETShipmentSETProd = df_in_SETShipmentSETProd.copy()
    delete_dfs(df_in_SETShipmentSETProd)
    print_df(df_SETShipmentSETProd, 'Step1 > df_SETShipmentSETProd ..... original')

    SOPPegging1_1 = df_SETShipmentSETProd.copy()
    SOPPegging1_1[ITEM_COLUMN] = SOPPegging1_1[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging1_1[TIME_WEEK_COLUMN] = SOPPegging1_1[FROM_TIME_WEEK_COLUMN]
    SOPPegging1_1[LOCATION_COLUMN] = SOPPegging1_1[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging1_1.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_PROD_TO_CDP_QTY_COLUMN: SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN,
                 SOP_BUP_PRODUCER_TO_CFP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_PRODUCER_TO_CTP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging1_1[SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN] = None
    SOPPegging1_1[SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging1_1[SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging1_1[SOP_PEGGING_TYPE_COLUMN] = '1_1_Plant SET Prod'
    print_df(SOPPegging1_1, 'Step1 > SOPPegging1_1 ..... rename')

    print_df(df_SETShipmentSETProd, 'Step1 > df_SETShipmentSETProd')
    # ====================> Step 1 (End)





    # ====================> Step 2 (Start) > df_in_SETShipmentLCMBOH (SET Shipment / LCM BOH or Arrival at SET Plant)
    # 2.1 df_SETShipmentSETProd create
    df_SETShipmentLCMBOH = df_in_SETShipmentLCMBOH.copy()
    delete_dfs(df_in_SETShipmentLCMBOH)
    print_df(df_SETShipmentLCMBOH, 'Step2 > df_SETShipmentLCMBOH ..... original')

    SOPPegging1_2 = df_SETShipmentLCMBOH.copy()
    SOPPegging1_2[ITEM_COLUMN] = SOPPegging1_2[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging1_2[TIME_WEEK_COLUMN] = SOPPegging1_2[TO_TIME_WEEK_COLUMN]
    SOPPegging1_2[LOCATION_COLUMN] = SOPPegging1_2[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging1_2.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_PROD_TO_CDP_QTY_COLUMN: SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN,
                 SOP_BUP_PRODUCER_TO_CFP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_PRODUCER_TO_CTP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging1_2[SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN] = None
    SOPPegging1_2[SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging1_2[SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging1_2[SOP_PEGGING_TYPE_COLUMN] = '1_2_Plant LCM BOH'
    print_df(SOPPegging1_2, 'Step2 > SOPPegging1_2 ..... rename')
    # ====================> Step 2 (End)





    # ====================> Step 3 (Start) > df_in_SETShipmentLCMCons (SET Shipment / LCM Plant cons)
    # 3.1 df_SETShipmentSETProd create
    df_SETShipmentLCMCons = df_in_SETShipmentLCMCons.copy()
    delete_dfs(df_in_SETShipmentLCMCons)
    print_df(df_SETShipmentLCMCons, 'Step3 > df_SETShipmentLCMCons ..... original')

    SOPPegging1_3 = df_SETShipmentLCMCons.copy()
    SOPPegging1_3[ITEM_COLUMN] = SOPPegging1_3[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging1_3[TIME_WEEK_COLUMN] = SOPPegging1_3[TO_TIME_WEEK_COLUMN]
    SOPPegging1_3[LOCATION_COLUMN] = SOPPegging1_3[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging1_3.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_CONS_TO_CDP_QTY_COLUMN: SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN,
                 SOP_BUP_CONSUMER_TO_CFP_COLUMN: SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_CONSUMER_TO_CTP_COLUMN: SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging1_3[SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN] = None
    SOPPegging1_3[SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging1_3[SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging1_3[SOP_PEGGING_TYPE_COLUMN] = '1_3_Plant LCM Plant Cons'
    print_df(SOPPegging1_3, 'Step3 > SOPPegging1_3 ..... rename')
# ====================> Step 3 (End)




    # ====================> Step 4 (Start) > df_in_SETShipmentLCMProd (SET Shipment / LCM Plant Prod)
    # 4.1 df_SETShipmentSETProd create
    df_SETShipmentLCMProd = df_in_SETShipmentLCMProd.copy()
    delete_dfs(df_in_SETShipmentLCMProd)
    print_df(df_SETShipmentLCMProd, 'Step4 > df_SETShipmentLCMProd ..... original')

    SOPPegging1_4 = df_SETShipmentLCMProd.copy()
    SOPPegging1_4[ITEM_COLUMN] = SOPPegging1_4[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging1_4[TIME_WEEK_COLUMN] = SOPPegging1_4[TO_TIME_WEEK_COLUMN]
    SOPPegging1_4[LOCATION_COLUMN] = SOPPegging1_4[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging1_4.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_PROD_TO_CDP_QTY_COLUMN: SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN,
                 SOP_BUP_PRODUCER_TO_CFP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_PRODUCER_TO_CTP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging1_4[SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN] = None
    SOPPegging1_4[SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging1_4[SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging1_4[SOP_PEGGING_TYPE_COLUMN] = '1_4_Plant LCM Prod'
    print_df(SOPPegging1_4, 'Step4 > SOPPegging1_4 ..... rename')
    # ====================> Step 4 (End)




    # ====================> Step 5 (Start) > df_SETShipmentOCCons (SET Shipment / Open Cell cons at LCM Plant)
    # 5.1 df_SETShipmentSETProd create
    df_SETShipmentOCCons = df_in_SETShipmentOCCons.copy()
    delete_dfs(df_in_SETShipmentOCCons)
    print_df(df_SETShipmentOCCons, 'Step5 > df_SETShipmentOCCons ..... original')

    SOPPegging1_5 = df_SETShipmentOCCons.copy()
    SOPPegging1_5[ITEM_COLUMN] = SOPPegging1_5[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging1_5[TIME_WEEK_COLUMN] = SOPPegging1_5[TO_TIME_WEEK_COLUMN]
    SOPPegging1_5[LOCATION_COLUMN] = SOPPegging1_5[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging1_5.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_CONS_TO_CDP_QTY_COLUMN: SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN,
                 SOP_BUP_CONSUMER_TO_CFP_COLUMN: SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_CONSUMER_TO_CTP_COLUMN: SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging1_5[SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN] = None
    SOPPegging1_5[SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging1_5[SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging1_5[SOP_PEGGING_TYPE_COLUMN] = '1_5_Plant OC Cons'
    print_df(SOPPegging1_5, 'Step5 > SOPPegging1_5 ..... rename')

    # ====================> Step 5 (End)




    # ====================> Step 6 (Start) > df_in_HubShipmentSETProd / MC Hub Cons / SET Prod
    # 6.1 df_HubShipmentSETProd create
    df_HubShipmentSETProd = df_in_HubShipmentSETProd.copy()
    delete_dfs(df_in_HubShipmentSETProd)
    print_df(df_HubShipmentSETProd, 'Step6 > df_HubShipmentSETProd ..... original')

    SOPPegging2_1 = df_SETShipmentSETProd.copy()
    SOPPegging2_1[ITEM_COLUMN] = SOPPegging2_1[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging2_1[TIME_WEEK_COLUMN] = SOPPegging2_1[FROM_TIME_WEEK_COLUMN]
    SOPPegging2_1[LOCATION_COLUMN] = SOPPegging2_1[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging2_1.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_PROD_TO_CDP_QTY_COLUMN: SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN,
                 SOP_BUP_PRODUCER_TO_CFP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_PRODUCER_TO_CTP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging2_1[SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN] = None
    SOPPegging2_1[SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging2_1[SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging2_1[SOP_PEGGING_TYPE_COLUMN] = '2_1_Plant SET Prod'
    print_df(SOPPegging2_1, 'Step6 > SOPPegging2_1 ..... rename')

    # ====================> Step 6 (End)






    # ====================> Step 8 (Start) > df_in_HubShipmentLCMCons / MC Hub Cons / LCM Plant cons
    # 8.1 df_SETShipmentSETProd create
    df_HubShipmentLCMCons = df_in_HubShipmentLCMCons.copy()
    delete_dfs(df_in_HubShipmentLCMCons)
    print_df(df_HubShipmentLCMCons, 'Step8 > df_HubShipmentLCMCons ..... original')

    SOPPegging2_3 = df_SETShipmentLCMCons.copy()
    SOPPegging2_3[ITEM_COLUMN] = SOPPegging2_3[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging2_3[TIME_WEEK_COLUMN] = SOPPegging2_3[TO_TIME_WEEK_COLUMN]
    SOPPegging2_3[LOCATION_COLUMN] = SOPPegging2_3[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging2_3.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_CONS_TO_CDP_QTY_COLUMN: SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN,
                 SOP_BUP_CONSUMER_TO_CFP_COLUMN: SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_CONSUMER_TO_CTP_COLUMN: SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging2_3[SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN] = None
    SOPPegging2_3[SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging2_3[SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging2_3[SOP_PEGGING_TYPE_COLUMN] = '2_3_Plant LCM Plant cons'
    print_df(SOPPegging2_3, 'Step8 > SOPPegging2_3 ..... rename')

    # ====================> Step 8 (End)



    # ====================> Step 9 (Start) > df_in_HubShipmentLCMProd / MC Hub Cons / LCM Plant Prod
    # 4.1 df_SETShipmentSETProd create
    df_HubShipmentLCMProd = df_in_HubShipmentLCMProd.copy()
    delete_dfs(df_in_HubShipmentLCMProd)
    print_df(df_HubShipmentLCMProd, 'Step9 > df_HubShipmentLCMProd ..... original')

    SOPPegging2_4 = df_HubShipmentLCMProd.copy()
    SOPPegging2_4[ITEM_COLUMN] = SOPPegging2_4[TO_TO_ITEM_TO_ITEM_COLUMN]
    SOPPegging2_4[TIME_WEEK_COLUMN] = SOPPegging2_4[TO_TIME_WEEK_COLUMN]
    SOPPegging2_4[LOCATION_COLUMN] = SOPPegging2_4[TO_TO_LOCATION_TO_LOCATION_COLUMN]
    SOPPegging2_4.rename(
        columns={FROM_TIME_WEEK_COLUMN: SOP_PEGGING_FROM_WEEK_COLUMN,
                 FROM_ACTIVITY1_COLUMN: SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
                 FROM_ITEM_COLUMN: SOP_PEGGING_FROM_ITEM_COLUMN,
                 FROM_ACTIVITY2_COLUMN: SOP_PEGGING_FROM_ACTIVITY2_COLUMN,
                 FROM_ACTIVITY3_COLUMN: SOP_PEGGING_FROM_ACTIVITY3_COLUMN,
                 FROM_LOCATION_COLUMN: SOP_PEGGING_FROM_LOCATION_COLUMN,
                 FROM_ORDERLINE_ID_COLUMN: SOP_PEGGING_FROM_ORDERLINEID_COLUMN,
                 TO_TO_TIME_TO_WEEK_COLUMN: SOP_PEGGING_TO_TO_WEEK_COLUMN,
                 TO_LOCATION_COLUMN: SOP_PEGGING_TO_LOCATION_COLUMN,
                 TO_ORDERLINE_ID_COLUMN: SOP_PEGGING_TO_ORDERLINEID_COLUMN,
                 TO_TIME_WEEK_COLUMN: SOP_PEGGING_TO_WEEK_COLUMN,
                 TO_TO_ITEM_TO_ITEM_COLUMN: SOP_PEGGING_TO_TO_ITEM_COLUMN,
                 TO_ACTIVITY1_COLUMN: SOP_PEGGING_TO_ACTIVITY1_COLUMN,
                 TO_ACTIVITY2_COLUMN: SOP_PEGGING_TO_ACTIVITY2_COLUMN,
                 TO_ACTIVITY3_COLUMN: SOP_PEGGING_TO_ACTIVITY3_COLUMN,
                 TO_DEMAND_ID_COLUMN: SOP_PEGGING_TO_DEMANDID_COLUMN,
                 TO_CUSTOMER_GROUP_COLUMN: SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN,
                 TO_DEMAND_TYPE_COLUMN: SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
                 SOP_BUP_PROD_TO_CDP_QTY_COLUMN: SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN,
                 SOP_BUP_PRODUCER_TO_CFP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN,
                 SOP_BUP_PRODUCER_TO_CTP_COLUMN: SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN},
        inplace=True)
    SOPPegging2_4[SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN] = None
    SOPPegging2_4[SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN] = None
    SOPPegging2_4[SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN] = None
    SOPPegging2_4[SOP_PEGGING_TYPE_COLUMN] = '2_4_LCM Plant Prod'
    print_df(SOPPegging2_4, 'Step9 > SOPPegging2_4 ..... rename')

    # ====================> Step 9 (End)


    step(300, '=====> STEP 3(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 4 : output data machining
    ################################################################################################################
    step(400, '=====> STEP 4(Start) : output data machining')

    SOPPegging = pd.concat([SOPPegging1_1, SOPPegging1_2, SOPPegging1_3, SOPPegging1_4, SOPPegging1_5,
                            SOPPegging2_1, SOPPegging2_3, SOPPegging2_4])

    SOPPegging[SEQUENCE_COLUMN] = None

    SOPPegging = SOPPegging[
        [VERSION_NAME_COLUMN, SEQUENCE_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN,
         SOP_PEGGING_FROM_WEEK_COLUMN, SOP_PEGGING_FROM_ITEM_COLUMN, SOP_PEGGING_FROM_ACTIVITY1_COLUMN,
         SOP_PEGGING_FROM_ACTIVITY2_COLUMN, SOP_PEGGING_FROM_ACTIVITY3_COLUMN, SOP_PEGGING_FROM_LOCATION_COLUMN,
         SOP_PEGGING_FROM_ORDERLINEID_COLUMN, SOP_PEGGING_TO_TO_WEEK_COLUMN, SOP_PEGGING_TO_LOCATION_COLUMN,
         SOP_PEGGING_TO_ORDERLINEID_COLUMN, SOP_PEGGING_TO_WEEK_COLUMN, SOP_PEGGING_TO_TO_ITEM_COLUMN,
         SOP_PEGGING_TO_ACTIVITY1_COLUMN, SOP_PEGGING_TO_ACTIVITY2_COLUMN, SOP_PEGGING_TO_ACTIVITY3_COLUMN,
         SOP_PEGGING_TO_DEMANDID_COLUMN, SOP_PEGGING_TO_CUSTOMER_GROUP_COLUMN, SOP_PEGGING_TO_DEMAND_TYPE_COLUMN,
         SOP_PEGGING_CONSTOCONS_DENAMD_QTY_COLUMN, SOP_PEGGING_CONSUMER_TO_CONSUMER_FROM_COLUMN,
         SOP_PEGGING_CONSUMER_TO_CONSUMER_TO_COLUMN, SOP_PEGGING_PROD_TO_CONS_DEMAND_QTY_COLUMN,
         SOP_PEGGING_PRODUCER_TO_CONSUMER_FROM_COLUMN, SOP_PEGGING_PRODUCER_TO_CONSUMER_TO_COLUMN,
         SOP_PEGGING_TYPE_COLUMN]].drop_duplicates()
    SOPPegging[SEQUENCE_COLUMN] = SOPPegging.groupby([ITEM_COLUMN]).cumcount() + 1

    # 사용된 df 삭제
    delete_dfs(df_SETShipmentSETProd, df_SETShipmentLCMBOH, df_SETShipmentLCMCons, df_SETShipmentLCMProd,
               df_SETShipmentOCCons)

    # 버전 처리
    SOPPegging[VERSION_NAME_COLUMN] = paramOutVersion

    step(400, '=====> STEP 4(End) : Check memory usage & runtime')

    ################################################################################################################
    # STEP 5 : output table create
    ################################################################################################################
    step(500, '=====> STEP 5(Start) : Final output table create')

    df_out_SOPAdjustInitial = SOPPegging.copy()

    # 사용된 df 삭제
    delete_dfs(SOPPegging)

    note(f'=====> Final output table create')
    save_csv_file(df_out_SOPAdjustInitial, 'df_out_SOPAdjustInitial')

    row_count, col_count = df_out_SOPAdjustInitial.shape
    note(f'=====> Final df_out_SOPAdjustInitial rows : {row_count}, column : {col_count}')

    step(500, '=====> STEP 5(End) : Check memory usage & runtime')

except Exception as e:
    trace_msg = traceback.format_exc()
    note(f'=====> try Exception : {trace_msg}', LOG_LEVEL.info())
    logger.Error()
    raise Exception(e)

else:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    note(f'=====> Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB')
    step(600, '===================== plugin Execution End =====================')

finally:
    logger.Finish()
