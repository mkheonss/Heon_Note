"""
* 프로그램명
    - PY_UI_SOPAdjustPegging

* 내용
    - 자원점검 보정을 위해 Solver 실행 후 SET선적 기준 구간별 정보를 Pegging 데이터로 연결

* 변경이력
    - 2024.09.19 / 권태우 / Create
    - 2025.01.07 / 권태우 / Input 변경
    - 2025.08.01 / 권태우 / Input 변경
        2-1.SET Prod / LCM BOH or Arrival at LCM Plant 반영 여부 확인 필요.

* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
    - df_in_CodeMap  : Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] ) on row, ({Measure.[Code Map LCM_Map Status], Measure.[Code Map LCM_Prod Item], Measure.[Code Map LCM_Valid Flag]}) on column WHERE {Measure.[Code Map LCM_Valid Flag] == "Y" && Measure.[Code Map LCM_Map Status] == "COM" && Measure.[Code Map LCM_Prod Item] <> "-"};
    - df_in_CurrWeek : Select (&CurrentWeek);
    - df_in_MDMHorizon: Select (&MDMHorizon);
    - df_in_FullBOM  : Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * &LCMToLocation * &LCMToItem * [Item Material].[MSL1].[Panel].relatedmembers([Item Material]) * [BOM Info].[BOM Version] * [Status].[Status] * [BOM Type].[BOM Type] * [BOM Status].[BOM Status]) on row, ({Measure.[Full BOM_BOM Date], Measure.[Full BOM_Creation Time]}) on column;
    - df_in_AllWeek  : Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));

    - df_in_SETShipmentSETProd : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"SET"}).relatedmembers([Item]) * FROM.[Activity1].[Activity Type1].[Manufacturing].relatedmembers([Activity1]) * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETShipmentSETProdBOH : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"SET"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1].filter(#.Name in  {"BOHActivity","ExpectedReceiptActivity"}) * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETProdLCMBOH    : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity Type1].filter(#.Name in {"Distribution","Internal"}).relatedmembers([Activity1])  * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity Type1].[Manufacturing].relatedmembers([Activity1]) * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Prod Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETProdLCMCons   : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity Type1].filter(#.Name =="Distribution").relatedmembers([Activity1])  * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM_EX","MF_LCM"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity Type1].[Manufacturing].relatedmembers([Activity1]) * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Prod Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETProdLCMProd   : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM_EX","MF_LCM"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2].filter(#.Name startswith "RT") * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET","LCM"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Prod Demand Pegged Qty] }) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETProdOCCons    : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"OPEN_CELL"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Prod Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    # - df_in_SETProdOCProd    : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"OPEN_CELL"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Prod Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_SETProdPanelCons : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"PANEL"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name contains "MF").relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID] * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Prod Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};

    - df_in_HubShipmentSETProd : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"SET"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentSETProdBOH : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"SET"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1].filter(#.Name in  {"BOHActivity","ExpectedReceiptActivity"}) * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged],Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged],Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentLCMBOH  : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1].filter(#.Name in {"ExpectedReceiptActivity","BOHActivity"})  * FROM.[Location].[Site Stage].filter(#.Name in {"MF_KD","MF_SET","MF"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentLCMCons : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM"}).relatedmembers([To Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentLCMProd : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"LCM"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2].filter(#.Name startswith "RT") * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer From Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Consumer To Pegged], Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Prod to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_HubShipmentOCCons  : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].filter(#.Name in {"OPEN_CELL"}).relatedmembers([Item]) * FROM.[Activity1].[Activity1] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM","MF_LCM_EX"}).relatedmembers([Location]) * FROM.[Activity2].[Activity2] * FROM.[Documents].[OrderlineID]* TO.[To Time].[To Week] * TO.[To Location].[To Site Stage].filter(#.Name in {"DC_HUB","DC_HUB_MC"}).relatedmembers([To Location])  * TO.[Documents].[OrderlineID] * TO.[Time].[Week] * TO.[To Item].[To Item Stage].filter(#.Name in {"SET"}).relatedmembers([To Item]) * TO.[Item].[Item] * TO.[Activity1].[Activity1] * TO.[Location].[Location] * TO.[Activity3].[Activity3] * TO.[Demand].[DemandID].filter(#.Name !="InventoryDemand") * TO.[Sales Domain].[Customer Group] * TO.[Demand Type].[Demand Type] * TO.[Activity2].[Activity2]) on row, ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer From Pegged],Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Consumer To Pegged],Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Cons to Cons Demand Pegged Qty]}) on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};

* Flow Summary
    - STEP1. Plant 기준으로 Input Table 반영 - 5가지 데이터 셋
             SET Shipment 기준으로 각 단계별 데이터 셋 반영
    - STEP2. Hub 기준으로 Input Table 반영 - 4가지 데이터 셋
             SET Shipment 기준으로 각 단계별 데이터 셋 반영

* Output Table
    - df_out_log
    - df_out_logDetail

    - df_out_SOP
    - df_out_SOPW
    - df_out_SOPAdjustmentSETW
    - df_out_SOPAdjustmentSETWAdj
    - df_out_SOPAdjustmentSET
    - df_out_SOPAdjustmentLCMW
    - df_out_SOPAdjustmentLCMWAdj
    - df_out_SOPDemandW

* 데이타 초기화
    - DELETE DATA FOR MODEL [SOP W] WHERE  {[Version].[Version Name].[CWV_MP]};

* RUN 스크립트
    - EXEC plugin instance [PY_UI_SOPAdjustPegging] for measures {[SOP W_SOP ID]} using scope (&MPV)
        using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};

* Output Query
    - df_out_SOPAdjustPegging / MG:  SOP W
        Select (&MPV * * [Location].[Location] * [Item].[Item] * [Time].[Week] * [To Location].[To Location] * [To Item].[To Item] * [To Time].[To Week] * [Sequence].[Sequence] * [Week1].[Week1] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Item Component].[Item Component] * [BOM Info].[BOM Version] * [Week2].[Week2] * [Trans Mode].[Trans Mode] * [To Trans Mode].[To Trans Mode] ) on row, ({
            Measure.[SOP W_BOM Cfm W], Measure.[SOP W_BOM Status], Measure.[SOP W_Chg Reason], Measure.[SOP W_LCM BOH Qty], Measure.[SOP W_LCM MFG Adj Qty], Measure.[SOP W_LCM MFG Chg Qty], Measure.[SOP W_LCM MFG Qty],
            Measure.[SOP W_LCM Plant], Measure.[SOP W_LCM SOP Adj Qty], Measure.[SOP W_LCM SOP ID], Measure.[SOP W_LCM SOP Qty], Measure.[SOP W_SET BOH Qty], Measure.[SOP W_SET MFG Adj Qty], Measure.[SOP W_SET MFG Chg Qty],
            Measure.[SOP W_SET MFG Qty], Measure.[SOP W_SET SOP Qty], Measure.[SOP W_SOP ID], Measure.[SOP W_Sht Qty], Measure.[SOP W_Sht Reason]}) on column limit 100;


"""
import gc
import traceback
import datetime
import numpy as np
import pandas as pd
import tracemalloc
import re
import time
import os
# from joblib import Parallel, delayed
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_SOPAdjustPegging'
is_local = common.gfn_get_isLocal()

# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# value 변수 선언
PARAM_OUTVERSION_VALUE = "CWV_MP"

# input variable 확인
paramOutVersion = (
    PARAM_OUTVERSION_VALUE
    if is_local or not paramOutVersion or not paramOutVersion.strip()
    else paramOutVersion
)


########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level
log_level_info = LOG_LEVEL.info()
log_level_debug = LOG_LEVEL.debug()
logger.debug(f'[START] {str_instance}')
logger.Start()


########################################################################################################################
# local function
########################################################################################################################
class CustomException(Exception):
    pass


def read_csv_file(file_name):
    try:
        file_path = f"{file_name}.csv"
        if not os.path.exists(file_path):
            step(f"=====> 파일이 존재하지 않습니다: {file_path}")
            return pd.DataFrame()  # 빈 DataFrame 반환
        return pd.read_csv(file_path, low_memory=False, encoding="UTF-8")

    except Exception as e:
        step(f"=====> CSV 파일 읽기 실패: {file_name}, 오류: {str(e)}")
        return pd.DataFrame()  # 에러 발생시 빈 DataFrame 반환


def save_csv_file(df, file_name):
    if is_local:
        df.to_csv(os.path.dirname(__file__) + "\\" + f"{file_name}.csv", index=False)


def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)


def step(string):
    vdCommon.gfn_stepLog(string)


def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)



def vd_log_start():
    log_path = os.path.dirname(__file__) if is_local else ""
    vdCommon.gfn_pyLog_start(paramOutVersion, str_instance, logger, is_local, log_path)


def vd_log_end() -> tuple:
    """
    로그 처리를 종료하고 로그 데이터프레임들을 반환하는 공통 함수

    Returns:
        tuple: (df_out_log, df_out_logDetail) 형태의 튜플
    """
    try:
        # 로그 종료 처리
        vdCommon.gfn_pyLog_end()

        # 로그 데이터프레임 가져오기
        df_out_log = vdCommon.gfn_getLog()
        df_out_logDetail = vdCommon.gfn_getLogDetail()

        return df_out_log, df_out_logDetail

    except Exception as e:
        setp(f"=====> 로그 처리 중 오류 발생: {str(e)}")
        return None, None


def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()


def rename_and_delete_df(df):
    """데이터프레임 최적화 및 메모리 사용량 감소"""
    if df is None:
        return None

    # 데이터프레임 복사 및 메모리 최적화
    result = df.copy()

    # 숫자형 컬럼의 데이터 타입 최적화
    for col in result.select_dtypes(include=['int', 'float']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')

    # # 범주형 데이터 최적화
    # for col in result.select_dtypes(include=['object']).columns:
    #     if result[col].nunique() / len(result) < 0.5:  # 고유값이 50% 미만일 경우
    #         result[col] = result[col].astype('category')

    delete_dfs(df)
    return result


def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
        return df[column_name].values[0]
    return None  # 기본값 반환



def get_formatted_time(timestamp):
    """타임스탬프를 사람이 읽을 수 있는 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")



def format_size(size_in_bytes):
    """바이트 단위를 적절히 MB 또는 GB로 변환하여 문자열 반환"""
    if size_in_bytes >= 1024 ** 3:  # 1GB 이상일 때
        return f"{size_in_bytes / 1024 ** 3:.1f} GB"
    else:
        return f"{size_in_bytes / 1024 ** 2:.1f} MB"


def run_time_minutes(start_time):
    """실행 시간을 계산하고, 분 또는 초 단위로 반환.
    초 단위가 0일 경우 초로 표시하고, 그 외에는 분으로 표시."""
    elapsed = time.time() - start_time
    if elapsed < 60:  # 1분 미만일 경우
        return str(round(elapsed, 2)) + " seconds"
    else:
        return str(round(elapsed / 60, 2)) + " minutes"



# pattern에 일치되는 문자열 찾아서 occurrence 위치의 문자 적용
def regexp_substr(series, pattern, occurrence):
    def get_match(input_string):
        matches = re.findall(pattern, input_string)
        if len(matches) >= occurrence:
            return matches[occurrence - 1]
        else:
            return None

    return series.apply(get_match)


def extract_bom_version(df, source_column, target_column):
    """
    DataFrame의 특정 열에서 문자열 패턴 추출 후 최종적으로 BOM 버전을 할당하는 함수.

    :param df: pandas DataFrame, 입력 데이터프레임
    :param source_column: str, 추출할 문자열이 있는 소스 컬럼
    :param target_column: str, 결과를 저장할 대상 컬럼
    """
    # 첫 번째 패턴으로 '@' 또는 공백을 제외한 문자열 추출
    first_extract = df[source_column].str.extract(r'([^@ ]+)')
    # '_'로 구분된 세 번째 단어 추출
    third_extract = first_extract[0].str.split('_').str[2]
    # 결과를 새로운 컬럼에 저장
    df[target_column] = third_extract


# Hrizon 주차 채워넣기
def set_unique_combinations(df, df2, columns):
    cols = list(filter(lambda col: col != TIME_WEEK_COLUMN, columns))

    # 데이터의 모든 고유 조합 생성
    unique_combinations = df[cols].copy().drop_duplicates()

    # 주차(TIME_WEEK_COLUMN) 데이터의 모든 조합 산출
    df2 = df2.assign(key=1)
    unique_combinations = unique_combinations.assign(key=1)
    all_possible_combinations = unique_combinations.merge(df2, how="outer").drop(columns=['key']).drop_duplicates()

    # 결측 데이터 찾기 (left join & 필터링)
    missing_rows = all_possible_combinations.merge(
        df[columns], on=columns, how="left", indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    return missing_rows




########################################################################################################################
# logic start
########################################################################################################################
if __name__ == '__main__':
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 시작
    tracemalloc.start()
    start_time = time.time()

    # Batch 시작
    vd_log_start()
    step(f'===================== plugin Execution Start ({get_formatted_time(start_time)}) =====================')
    step(f'=====> NSCMCommon Version check - {COMMON_SOURCE_VERSION}')
    step(f'=====> VDCommon Version check - {VD_SOURCE_VERSION}')
    step(f'=====> input value check - paramOutVersion : {paramOutVersion}')

    try:
        ################################################################################################################
        # STEP 1 : 전처리 - 모듈 내에서 사용될 input table load
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')

        if is_local:
            df_in_CodeMap = read_csv_file("df_in_CodeMap")
            df_in_CurrWeek = read_csv_file("df_in_CurrWeek")
            df_in_MDMHorizon = read_csv_file("df_in_MDMHorizon")
            df_in_FullBOM = read_csv_file("df_in_FullBOM")
            df_in_AllWeek = read_csv_file("df_in_AllWeek")

            df_in_SETShipmentSETProd = read_csv_file("df_in_SETShipmentSETProd")
            df_in_SETShipmentSETProdBOH = read_csv_file("df_in_SETShipmentSETProdBOH")
            df_in_SETProdLCMBOH = read_csv_file("df_in_SETProdLCMBOH")
            df_in_SETProdLCMCons = read_csv_file("df_in_SETProdLCMCons")
            df_in_SETProdLCMProd = read_csv_file("df_in_SETProdLCMProd")
            df_in_SETProdOCCons = read_csv_file("df_in_SETProdOCCons")
            df_in_SETProdOCProd = read_csv_file("df_in_SETProdOCProd")
            df_in_SETProdPanelCons = read_csv_file("df_in_SETProdPanelCons")

        # dataframe dict
        dataframes = {
            'df_in_CodeMap': df_in_CodeMap,
            'df_in_CurrWeek': df_in_CurrWeek,
            'df_in_MDMHorizon': df_in_MDMHorizon,
            'df_in_FullBOM': df_in_FullBOM,
            'df_in_AllWeek': df_in_AllWeek,
            'df_in_SETShipmentSETProd': df_in_SETShipmentSETProd,
            'df_in_SETShipmentSETProdBOH': df_in_SETShipmentSETProdBOH,
            'df_in_SETProdLCMBOH': df_in_SETProdLCMBOH,
            'df_in_SETProdLCMCons': df_in_SETProdLCMCons,
            'df_in_SETProdLCMProd': df_in_SETProdLCMProd,
            'df_in_SETProdOCCons': df_in_SETProdOCCons,
            'df_in_SETProdOCProd': df_in_SETProdOCProd,
            'df_in_SETProdPanelCons': df_in_SETProdPanelCons,
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')



        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        SEQUENCE_COLUMN = 'Sequence.[Sequence]'
        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        CODE_MAP_LCM_PROD_ITEM_COLUMN = 'Code Map LCM_Prod Item'
        ITEM_COLUMN = 'Item.[Item]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        TIME_DAY_WEEK_COLUMN = 'Time.[Day of Week]'
        TIME_DAY_COLUMN = 'Time.[Day]'
        LOCATION_COLUMN = 'Location.[Location]'
        TO_LOCATION_TO_LOCATION_COLUMN = 'To Location.[To Location]'
        TO_TIME_TO_WEEK_COLUMN = 'To Time.[To Week]'
        TO_ITEM_TO_ITEM_COLUMN = 'To Item.[To Item]'
        SUB_LOCATION_COLUMN = 'Sub Location.[Sub Location]'
        SUB_LOCATION_X_COLUMN = 'Sub Location.[Sub Location]_x'
        BOM_INFO_BOM_VERSION_COLUMN = 'BOM Info.[BOM Version]'
        SOP_ID_COLUMN = 'SOP ID.[SOP ID]'
        TRANS_MODE_COLUMN = 'Trans Mode.[Trans Mode]'
        TO_TRANS_MODE_COLUMN = 'To Trans Mode.[To Trans Mode]'
        ITEM_METERIAL_COLUMN = 'Item Material.[Item Material]'
        ITEM_COMPONENT_COLUMN = 'Item Component.[Item Component]'
        WEEK1_COLUMN = 'Week1.[Week1]'
        WEEK2_COLUMN = 'Week2.[Week2]'
        DEMAND_ID_COLUMN = 'Demand.[DemandID]'

        FROM_TIME_WEEK_COLUMN = 'from.[Time].[Week]'
        FROM_ACTIVITY3_COLUMN = 'from.[Activity3].[Activity3]'
        FROM_ITEM_COLUMN = 'from.[Item].[Item]'
        FROM_ACTIVITY1_COLUMN = 'from.[Activity1].[Activity1]'
        FROM_LOCATION_COLUMN = 'from.[Location].[Location]'
        FROM_ORDERLINE_ID_COLUMN = 'from.[Documents].[OrderlineID]'
        FROM_ACTIVITY2_COLUMN = 'from.[Activity2].[Activity2]'
        FROM_DOCUMENT_ORDERLINE_ID_COLUMN = 'from.[Documents].[OrderlineID]'

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
        TO_DOCUMENT_ORDERLINE_ID_COLUMN = 'to.[Documents].[OrderlineID]'

        SOP_BUP_PRODUCER_TO_PFP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Producer From Pegged]'
        SOP_BUP_PRODUCER_TO_CFP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]'
        SOP_BUP_CONSUMER_TO_CFP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]'
        SOP_BUP_PRODUCER_TO_CTP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer To Pegged]'
        SOP_BUP_CONSUMER_TO_PFP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]'
        SOP_BUP_CONSUMER_TO_CTP_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer To Pegged]'
        SOP_BUP_PROD_TO_CDP_QTY_COLUMN = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Prod to Cons Demand Pegged Qty]'
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

        SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN = 'SOP Adjust SET W_SOP Adj Qty'
        SOP_ADJUST_SET_W_SOP_QTY_COLUMN = 'SOP Adjust SET W_SOP Qty'
        SOP_ADJUST_SET_W_CHG_QTY_COLUMN = 'SOP Adjust SET W_Chg Qty'
        SOP_ADJUST_SET_W_SOP_ADJ_SHORT_QTY_COLUMN = 'SOP Adjust SET W_SOP Adj Short Qty'
        SOP_ADJUST_SET_W_SHT_QTY_COLUMN = 'SOP Adjust SET W_Sht Qty'
        SOP_ADJUST_SET_W_CHG_REASON_COLUMN = 'SOP Adjust SET W_Chg Reason'
        SOP_ADJUST_SET_W_LOCK_FLAG_COLUMN = 'SOP Adjust SET W_Lock Flag'
        SOP_ADJUST_SET_W_JIT_COLUMN = 'SOP Adjust SET W_JIT'
        SOP_ADJUST_SET_W_SS_COLUMN = 'SOP Adjust SET W_SS'
        SOP_ADJUST_SET_W_BLD_COLUMN = 'SOP Adjust SET W_BLD'

        SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN = 'SOP Adjust LCM W_SOP Adj Qty'
        SOP_ADJUST_LCM_W_SOP_QTY_COLUMN = 'SOP Adjust LCM W_SOP Qty'
        SOP_ADJUST_LCM_W_CHG_QTY_COLUMN = 'SOP Adjust LCM W_Chg Qty'

        SOP_PEGGING_TYPE_COLUMN = 'SOP Pegging_Type'

        SOP_W_ITEM_MTRL_COLUMN = 'SOP W_Item Mtrl'
        SOP_W_PRD_ITEM_COLUMN = 'SOP W_Prd Item'
        SOP_W_SOP_ID_COLUMN = 'SOP W_SOP ID'
        SOP_W_BOM_CFM_W_COLUMN = 'SOP W_BOM Cfm W'
        SOP_W_BOM_STATUS_COLUMN = 'SOP W_BOM Status'
        SOP_W_SHT_REASON_COLUMN = 'SOP W_Sht Reason'
        SOP_W_CHG_REASON_COLUMN = 'SOP W_Chg Reason'
        SOP_W_LCM_PLANT_COLUMN = 'SOP W_LCM Plant'

        SOP_W_SOP_ADJ_QTY_COLUMN = 'SOP W_SOP Adj Qty'
        SOP_W_SET_MFG_ADJ_QTY_COLUMN = 'SOP W_SET MFG Adj Qty'
        SOP_W_SOP_QTY_COLUMN = 'SOP W_SOP Qty'
        SOP_W_CHG_QTY_COLUMN = 'SOP W_Chg Qty'
        SOP_W_SET_MFG_CHG_QTY_COLUMN = 'SOP W_SET MFG Chg Qty'
        SOP_W_LCM_MFG_ADJ_QTY_COLUMN = 'SOP W_LCM MFG Adj Qty'
        SOP_W_SHT_QTY_COLUMN = 'SOP W_Sht Qty'
        SOP_W_LCM_CHG_QTY_COLUMN = 'SOP W_LCM Chg Qty'
        SOP_W_LCM_SOP_QTY_COLUMN = 'SOP W_LCM SOP Qty'
        SOP_W_LCM_BOH_QTY_COLUMN = 'SOP W_LCM BOH Qty'
        SOP_W_LCM_MFG_QTY_COLUMN = 'SOP W_LCM MFG Qty'
        SOP_W_LCM_MFG_CHG_QTY_COLUMN = 'SOP W_LCM MFG Chg Qty'
        SOP_W_SET_MFG_QTY_COLUMN = 'SOP W_SET MFG Qty'
        SOP_W_SET_SOP_QTY_COLUMN = 'SOP W_SET SOP Qty'
        SOP_W_SET_BOH_QTY_COLUMN = 'SOP W_SET BOH Qty'
        SOP_W_SET_ADJ_QTY_COLUMN = 'SOP W_SOP Adj Qty'
        SOP_W_LCM_SOP_ADJ_QTY_COLUMN = 'SOP W_LCM SOP Adj Qty'
        SOP_W_LCM_SOP_ID_COLUMN = 'SOP W_LCM SOP ID'

        SOP_MIN_LOT_QTY_COLUMN = 'SOP_Min LOT Qty'
        SOP_MULTIPLE_LOT_QTY_COLUMN = 'SOP_Multiple LOT Qty'

        SOP_ADJUST_SET_MIN_LOT_QTY_COLUMN = 'SOP Adjust SET_Min LOT Qty'
        SOP_ADJUST_SET_MULTIPLE_LOT_QTY_COLUMN = 'SOP Adjust SET_Multiple LOT Qty'

        FROM_DEMAND_DEMANDID_COLUMN = 'FROM_DEMAND_DEMANDID'
        TO_DEMAND_DEMANDID_COLUMN = 'TO_DEMAND_DEMANDID'
        LCM_ITEM_COLUMN = 'LCM_ITEM'
        LCM_SITE_COLUMN = 'LCM_SITE'
        LCM_TRANSMODE_COLUMN = 'LCM_TRANSMODE'
        LCM_MFG_WEEK_COLUMN = 'LCM_MFG_WEEK'
        LCM_SOP_WEEK_COLUMN = 'LCM_SOP_WEEK'
        LCM_MFG_QTY_COLUMN = 'LCM_MFG_QTY'
        LCM_SOP_QTY_COLUMN = 'LCM_SOP_QTY'
        LCM_BOH_QTY_COLUMN = 'LCM_BOH_QTY'
        SET_ITEM_COLUMN = 'SET_ITEM'
        SET_SITE_COLUMN = 'SET_SITE'
        SET_TRANSMODE_COLUMN = 'SET_TRANSMODE'
        SET_MFG_WEEK_COLUMN = 'SET_MFG_WEEK'
        SET_SOP_WEEK_COLUMN = 'SET_SOP_WEEK'
        SET_MFG_QTY_COLUMN = 'SET_MFG_QTY'
        SET_SOP_QTY_COLUMN = 'SET_SOP_QTY'
        SET_BOH_QTY_COLUMN = 'SET_BOH_QTY'
        HUB_ITEM_COLUMN = 'HUB_ITEM'
        HUB_SITE_COLUMN = 'HUB_SITE'
        HUB_TRANSMODE_COLUMN = 'HUB_TRANSMODE'
        HUB_MFG_WEEK_COLUMN = 'HUB_MFG_WEEK'
        HUB_SOP_WEEK_COLUMN = 'HUB_SOP_WEEK'
        HUB_MFG_QTY_COLUMN = 'HUB_MFG_QTY'
        HUB_SOP_QTY_COLUMN = 'HUB_SOP_QTY'
        DC_SITE_COLUMN = 'DC_SITE'
        BOM_VERSION_COLUMN = 'BOM_VERSION'
        OC_ITEM_COLUMN = 'OC_ITEM'
        COMPLETE_PANEL_ITEM_COLUMN = 'COMPLETE_PANEL_ITEM'
        HUB_QTY_COLUMN = 'HUB_QTY'
        PTYPE_COLUMN = 'PTYPE'

        BOM_STATUS_BOM_STATUS_COLUMN = 'BOM Status.[BOM Status]'
        FULL_BOM_BOM_DATE_COLUMN = 'Full BOM_BOM Date'
        FULL_BOM_CREATION_TIME_COLUMN = 'Full BOM_Creation Time'

        SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN = 'SOP Adjust LCM W_Before Adj Qty'
        SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN = 'SOP Adjust SET W_Before Adj Qty'

        SOP_DMD_W_LCM_BOH_QTY_COLUMN = 'SOP Dmd W_LCM BOH Qty'
        SOP_DMD_W_LCM_MFG_QTY_COLUMN = 'SOP Dmd W_LCM MFG Qty'
        SOP_DMD_W_LCM_SOP_QTY_COLUMN = 'SOP Dmd W_LCM SOP Qty'
        SOP_DMD_W_SET_BOH_QTY_COLUMN = 'SOP Dmd W_SET BOH Qty'
        SOP_DMD_W_SET_MFG_QTY_COLUMN = 'SOP Dmd W_SET MFG Qty'
        SOP_DMD_W_SET_SOP_QTY_COLUMN = 'SOP Dmd W_SET SOP Qty'

        # Columns 설정
        df_SOP_W_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            WEEK1_COLUMN, WEEK2_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN,
            SEQUENCE_COLUMN,
            SOP_W_BOM_STATUS_COLUMN, SOP_W_BOM_CFM_W_COLUMN,
            SOP_W_LCM_PLANT_COLUMN, SOP_W_SOP_ID_COLUMN, SOP_W_LCM_SOP_ID_COLUMN,
            SOP_W_SET_MFG_QTY_COLUMN, SOP_W_SET_MFG_ADJ_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN, SOP_W_SET_BOH_QTY_COLUMN,
            SOP_W_LCM_MFG_QTY_COLUMN, SOP_W_LCM_SOP_QTY_COLUMN, SOP_W_LCM_BOH_QTY_COLUMN, SOP_W_LCM_MFG_ADJ_QTY_COLUMN,
        ]

        df_SOP_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, SEQUENCE_COLUMN,
            SOP_MIN_LOT_QTY_COLUMN, SOP_MULTIPLE_LOT_QTY_COLUMN,
        ]

        df_SOPAdjustmentSETW_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN,
            SOP_ADJUST_SET_W_SOP_QTY_COLUMN, SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN
        ]

        df_SOPAdjustmentSETWAdj_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN,
            SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN,
        ]

        df_SOPAdjustmentSET_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN,
            SOP_ADJUST_SET_MIN_LOT_QTY_COLUMN, SOP_ADJUST_SET_MULTIPLE_LOT_QTY_COLUMN,
        ]

        df_SOPAdjustmentLCMW_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN,
            SOP_ADJUST_LCM_W_SOP_QTY_COLUMN, SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN,
        ]

        df_SOPAdjustmentLCMWAdj_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN,
        ]

        df_SOPDemandW_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN, TO_TIME_TO_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN,
            TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, WEEK1_COLUMN, WEEK2_COLUMN, TRANS_MODE_COLUMN,
            TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN, SEQUENCE_COLUMN, DEMAND_ID_COLUMN,
            SOP_DMD_W_SET_BOH_QTY_COLUMN, SOP_DMD_W_SET_MFG_QTY_COLUMN, SOP_DMD_W_SET_SOP_QTY_COLUMN,
            SOP_DMD_W_LCM_BOH_QTY_COLUMN, SOP_DMD_W_LCM_MFG_QTY_COLUMN, SOP_DMD_W_LCM_SOP_QTY_COLUMN,
        ]

        step('=====> STEP2 End')



        ################################################################################################################
        # STEP 3 :  데이터 선 가공
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')


        df_in_MDMHorizon = df_in_MDMHorizon[[TIME_WEEK_COLUMN]].drop_duplicates()
        df_in_MDMHorizon[TIME_WEEK_COLUMN] = pd.to_numeric(df_in_MDMHorizon[TIME_WEEK_COLUMN], errors='coerce')


        # ====================> STEP3 by 0 (Start) -> df_in_SETShipmentSETProd (SET Shipment / SET Prod)

        # 0.1 df_in_CodeMap 필요한 컬럼만 발췌
        df_in_CodeMap = df_in_CodeMap[
            [ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, CODE_MAP_LCM_PROD_ITEM_COLUMN]]

        # 0.2 현재 week 가져오기
        mp_plan_start_week = int(get_first_value(df_in_CurrWeek, TIME_WEEK_COLUMN))
        step(f'=====> mp_plan_start_week : {mp_plan_start_week}')

        # 0.3 df_in_AllWeek 필요컬럼 설정
        df_in_AllWeek = df_in_AllWeek[[TIME_WEEK_COLUMN, TIME_DAY_COLUMN, TIME_DAY_WEEK_COLUMN]].drop_duplicates()
        df_in_AllWeek[TIME_DAY_COLUMN] = df_in_AllWeek[TIME_DAY_COLUMN].astype(str)

        # 0.4 FullBOM 의 'Full BOM_Creation Time' 값을 '%Y-%m-%d' 형식으로 변경
        #   pd.to_datetime() 사용하여 여러 형식의 날짜를 자동으로 인식
        df_in_FullBOM[FULL_BOM_CREATION_TIME_COLUMN] = pd.to_datetime(df_in_FullBOM[FULL_BOM_CREATION_TIME_COLUMN], format='mixed', errors='coerce')

        #   원하는 형식으로 변환 ('%Y-%m-%d')
        df_in_FullBOM[FULL_BOM_CREATION_TIME_COLUMN] = df_in_FullBOM[FULL_BOM_CREATION_TIME_COLUMN].dt.strftime('%Y-%m-%d')

        #   nan 값 처리
        df_in_FullBOM[BOM_STATUS_BOM_STATUS_COLUMN] = df_in_FullBOM[BOM_STATUS_BOM_STATUS_COLUMN].fillna('-').astype(str).replace({'-': None})
        df_in_FullBOM[FULL_BOM_CREATION_TIME_COLUMN] = df_in_FullBOM[FULL_BOM_CREATION_TIME_COLUMN].fillna('-').astype(str).replace({'-': None})
        print_df(df_in_FullBOM, 'STEP3 by 0.4 ____ df_in_FullBOM .... Full BOM_Creation Time modify')

        # ====================> STEP3 by 0 (End)







        # ====================> STEP3 by 1 (Start) -> df_in_SETShipmentSETProd modify (SET Shipment / SET Prod / BOM)

        # 1.1 null 컬럼 및 기타 컬럼 설정
        #   1.1.1 'PTYPE' 컬럼 설정
        df_in_SETShipmentSETProd[PTYPE_COLUMN] = '1. SET Shipment SET Prod BOM'

        #   1.1.2 str 컬럼 null 설정
        null_columns = [
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN,
        ]
        df_in_SETShipmentSETProd[null_columns] = '-'

        #   1.1.3 int 컬럼 null 설정
        null_columns = [
            LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_BOH_QTY_COLUMN,
        ]
        df_in_SETShipmentSETProd[null_columns] = 0

        #   1.1.4 컬럼명 변경 및 추가
        df_in_SETShipmentSETProd.rename(columns={
            TO_DEMAND_ID_COLUMN: TO_DEMAND_DEMANDID_COLUMN,
            TO_ORDERLINE_ID_COLUMN: TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            TO_TO_ITEM_TO_ITEM_COLUMN: SET_ITEM_COLUMN,
            TO_TO_LOCATION_TO_LOCATION_COLUMN: SET_SITE_COLUMN,
            TO_LOCATION_COLUMN: DC_SITE_COLUMN,
            TO_ACTIVITY2_COLUMN: SET_TRANSMODE_COLUMN,
            FROM_TIME_WEEK_COLUMN: SET_MFG_WEEK_COLUMN,
            TO_TO_TIME_TO_WEEK_COLUMN: SET_SOP_WEEK_COLUMN,
            SOP_BUP_PRODUCER_TO_CFP_COLUMN: SET_MFG_QTY_COLUMN,
        }, inplace=True)
        df_in_SETShipmentSETProd[SET_SOP_QTY_COLUMN] = df_in_SETShipmentSETProd[SET_MFG_QTY_COLUMN]

        # 1.2 'BOM_VERSION' 컬럼 설정
        pattern = r'[^_ ]+'
        occurrence = 2
        df_in_SETShipmentSETProd[BOM_VERSION_COLUMN] = (
            regexp_substr(df_in_SETShipmentSETProd[FROM_ACTIVITY1_COLUMN], pattern, occurrence))
        print_df(df_in_SETShipmentSETProd, 'STEP3 by 1.1 ____ df_in_SETShipmentSETProd .... modify')

        # 1.3 필요컬럼 발췌
        df_in_SETShipmentSETProd = df_in_SETShipmentSETProd[[
            TO_DEMAND_DEMANDID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, SET_TRANSMODE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN,
            SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
            OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            PTYPE_COLUMN
        ]]

        print_df(df_in_SETShipmentSETProd, 'STEP3 by 1.2 ____ df_in_SETShipmentSETProd')

        # ====================> STEP3 by 1 (End)







        # ====================> STEP3 by 1-1 (Start) -> df_in_SETShipmentSETProdBOH (SET Shipment / SET Prod / BOH / ER)

        # 1-1.1 null 컬럼 및 기타 컬럼 설정
        #   1-1.1.1 'PTYPE' 컬럼 설정
        df_in_SETShipmentSETProdBOH[PTYPE_COLUMN] = '1-1. SET Shipment SET Prod BOH ER'

        null_columns = [
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, BOM_VERSION_COLUMN, OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN,
        ]
        df_in_SETShipmentSETProdBOH[null_columns] = '-'

        null_columns = [
            LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_MFG_QTY_COLUMN,
        ]
        df_in_SETShipmentSETProdBOH[null_columns] = 0

        df_in_SETShipmentSETProdBOH.rename(columns={
            TO_DEMAND_ID_COLUMN: TO_DEMAND_DEMANDID_COLUMN,
            TO_ORDERLINE_ID_COLUMN: TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            TO_TO_ITEM_TO_ITEM_COLUMN: SET_ITEM_COLUMN,
            TO_TO_LOCATION_TO_LOCATION_COLUMN: SET_SITE_COLUMN,
            TO_LOCATION_COLUMN: DC_SITE_COLUMN,
            TO_ACTIVITY2_COLUMN: SET_TRANSMODE_COLUMN,
            FROM_TIME_WEEK_COLUMN: SET_MFG_WEEK_COLUMN,
            TO_TO_TIME_TO_WEEK_COLUMN: SET_SOP_WEEK_COLUMN,
            SOP_BUP_PRODUCER_TO_CFP_COLUMN: SET_SOP_QTY_COLUMN,
        }, inplace=True)
        df_in_SETShipmentSETProdBOH[SET_BOH_QTY_COLUMN] = df_in_SETShipmentSETProdBOH[SET_SOP_QTY_COLUMN]
        print_df(df_in_SETShipmentSETProdBOH, 'STEP3 by 1-1.1 ____ df_in_SETShipmentSETProdBOH .... modify')

        df_in_SETShipmentSETProdBOH = df_in_SETShipmentSETProdBOH[[
            TO_DEMAND_DEMANDID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, SET_TRANSMODE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN,
            SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
            OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            PTYPE_COLUMN
        ]]

        print_df(df_in_SETShipmentSETProdBOH, 'STEP3 by 1-1.2 ____ df_in_SETShipmentSETProdBOH')

        # ====================> STEP3 by 1-1 (End)







        # ====================> STEP3 by 2 (Start) -> df_in_SETProdLCMBOH (SET Prod / LCM BOH or Arrival at SET Plant)

        # 2.1 null 컬럼 및 기타 컬럼 설정
        #   2.1.1 'PTYPE' 컬럼 설정
        df_in_SETProdLCMBOH[PTYPE_COLUMN] = '2.SET Prod LCM BOH or Arrival'

        #   2.1.2 str 컬럼 null 설정
        null_columns = [
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN,
            LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, DC_SITE_COLUMN, SET_TRANSMODE_COLUMN, OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN,
        ]
        df_in_SETProdLCMBOH[null_columns] = '-'

        #   2.1.3 int 컬럼 null 설정
        null_columns = [
            LCM_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
        ]
        df_in_SETProdLCMBOH[null_columns] = 0

        #   2.1.4 컬럼명 변경 및 추가
        df_in_SETProdLCMBOH.rename(columns={
            TO_DEMAND_ID_COLUMN: TO_DEMAND_DEMANDID_COLUMN,
            TO_ORDERLINE_ID_COLUMN: TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            FROM_ITEM_COLUMN: LCM_ITEM_COLUMN,
            FROM_TIME_WEEK_COLUMN: LCM_SOP_WEEK_COLUMN,
            TO_TO_ITEM_TO_ITEM_COLUMN: SET_ITEM_COLUMN,
            TO_TO_LOCATION_TO_LOCATION_COLUMN: SET_SITE_COLUMN,
            TO_TO_TIME_TO_WEEK_COLUMN: SET_MFG_WEEK_COLUMN,
            SOP_BUP_PRODUCER_TO_PFP_COLUMN: LCM_BOH_QTY_COLUMN,
        }, inplace=True)
        df_in_SETProdLCMBOH[SET_SOP_QTY_COLUMN] = df_in_SETProdLCMBOH[SET_MFG_QTY_COLUMN]

        # 2.2 'BOM_VERSION' 컬럼 설정
        extract_bom_version(df_in_SETProdLCMBOH, TO_ACTIVITY2_COLUMN, BOM_VERSION_COLUMN)
        print_df(df_in_SETProdLCMBOH, 'STEP3 by 2.1 ____ df_in_SETProdLCMBOH .... modify')

        # 2.3 필요컬럼 발췌
        df_in_SETProdLCMBOH = df_in_SETProdLCMBOH[[
            TO_DEMAND_DEMANDID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, SET_TRANSMODE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN,
            SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
            OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            PTYPE_COLUMN
        ]]

        print_df(df_in_SETProdLCMBOH, 'STEP3 by 2.2 ____ df_in_SETProdLCMBOH')

        # ====================> STEP3 by 2 (End)







        # ====================> STEP3 by 3 (Start) -> df_in_SETProdLCMCons (SET Prod / LCM Plant cons)

        # 3.1 null 컬럼 및 기타 컬럼 설정
        #   3.1.1 'PTYPE' 컬럼 설정
        df_in_SETProdLCMCons[PTYPE_COLUMN] = '3. SET Prod LCM Plant Cons'

        #   3.1.2 str 컬럼 null 설정
        null_columns = [DC_SITE_COLUMN, SET_TRANSMODE_COLUMN, OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN]
        df_in_SETProdLCMCons[null_columns] = '-'

        #   3.1.3 int 컬럼 null 설정
        null_columns = [
            LCM_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
        ]
        df_in_SETProdLCMCons[null_columns] = 0

        #   3.1.4 컬럼명 변경 및 추가
        df_in_SETProdLCMCons.rename(columns={
            FROM_ORDERLINE_ID_COLUMN: FROM_DOCUMENT_ORDERLINE_ID_COLUMN,
            TO_DEMAND_ID_COLUMN: TO_DEMAND_DEMANDID_COLUMN,
            TO_ORDERLINE_ID_COLUMN: TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            FROM_ITEM_COLUMN: LCM_ITEM_COLUMN,
            FROM_LOCATION_COLUMN: LCM_SITE_COLUMN,
            FROM_ACTIVITY2_COLUMN: LCM_TRANSMODE_COLUMN,
            FROM_TIME_WEEK_COLUMN: LCM_SOP_WEEK_COLUMN,
            TO_TO_ITEM_TO_ITEM_COLUMN: SET_ITEM_COLUMN,
            TO_TO_TIME_TO_WEEK_COLUMN: SET_MFG_WEEK_COLUMN,
            TO_TO_LOCATION_TO_LOCATION_COLUMN: SET_SITE_COLUMN,
            SOP_BUP_CONSUMER_TO_PFP_COLUMN: LCM_SOP_QTY_COLUMN,
        }, inplace=True)

        # 3.2 'BOM_VERSION' 컬럼 설정
        extract_bom_version(df_in_SETProdLCMCons, TO_ACTIVITY2_COLUMN, BOM_VERSION_COLUMN)
        print_df(df_in_SETProdLCMCons, 'STEP3 by 3.1 ____ df_in_SETProdLCMCons .... modify')

        # 3.3 필요컬럼 발췌
        df_in_SETProdLCMCons = df_in_SETProdLCMCons[[
            TO_DEMAND_DEMANDID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, SET_TRANSMODE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN,
            SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
            OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            PTYPE_COLUMN
        ]]

        print_df(df_in_SETProdLCMCons, 'STEP3 by 3.2 ____ df_in_SETProdLCMCons')

        # ====================> STEP3 by 3 (End)








        # ====================> STEP3 by 4 (Start) -> df_in_SETProdLCMProd (SET Prod / LCM Plant Prod)

        # 4.1 null 컬럼 및 기타 컬럼 설정
        #   4.1.1 'PTYPE' 컬럼 설정
        df_in_SETProdLCMProd[PTYPE_COLUMN] = '4. SET Prod LCM Plant Prod'

        #   4.1.2 str 컬럼 null 설정
        null_columns = [
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN,
            LCM_TRANSMODE_COLUMN, DC_SITE_COLUMN, SET_TRANSMODE_COLUMN, OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN,
        ]
        df_in_SETProdLCMProd[null_columns] = '-'

        #   2.1.3 int 컬럼 null 설정
        null_columns = [
            LCM_SOP_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
        ]
        df_in_SETProdLCMProd[null_columns] = 0

        #   4.1.4 컬럼명 변경 및 추가
        df_in_SETProdLCMProd.rename(columns={
            TO_DEMAND_ID_COLUMN: TO_DEMAND_DEMANDID_COLUMN,
            TO_ORDERLINE_ID_COLUMN: TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            FROM_ITEM_COLUMN: LCM_ITEM_COLUMN,
            FROM_LOCATION_COLUMN: LCM_SITE_COLUMN,
            FROM_TIME_WEEK_COLUMN: LCM_MFG_WEEK_COLUMN,
            TO_TO_ITEM_TO_ITEM_COLUMN: SET_ITEM_COLUMN,
            TO_TO_LOCATION_TO_LOCATION_COLUMN: SET_SITE_COLUMN,
            TO_TO_TIME_TO_WEEK_COLUMN: SET_MFG_WEEK_COLUMN,
            SOP_BUP_PRODUCER_TO_PFP_COLUMN: LCM_MFG_QTY_COLUMN,
        }, inplace=True)

        # 4.2 'BOM_VERSION' 컬럼 설정
        extract_bom_version(df_in_SETProdLCMProd, TO_ACTIVITY2_COLUMN, BOM_VERSION_COLUMN)
        print_df(df_in_SETProdLCMProd, 'STEP3 by 4.1 ____ df_in_SETProdLCMProd .... modify')

        # 4.3 필요컬럼 발췌
        df_in_SETProdLCMProd = df_in_SETProdLCMProd[[
            TO_DEMAND_DEMANDID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, SET_TRANSMODE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN,
            SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
            OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            PTYPE_COLUMN
        ]]

        print_df(df_in_SETProdLCMProd, 'STEP3 by 4.2 ____ df_in_SETProdLCMProd')

        # ====================> STEP3 by 4 (End)






        # ====================> STEP3 by 5 (Start) -> df_in_SETProdOCCons (SET Prod / Open Cell cons at LCM Plant)

        # 5.1 null 컬럼 및 기타 컬럼 설정
        #   5.1.1 'PTYPE' 컬럼 설정
        df_in_SETProdOCCons[PTYPE_COLUMN] = '5. SET Prod Open Cell cons at LCM Plant'

        #   5.1.2 str 컬럼 null 설정
        null_columns = [
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN,
            LCM_TRANSMODE_COLUMN, DC_SITE_COLUMN, SET_TRANSMODE_COLUMN, COMPLETE_PANEL_ITEM_COLUMN,
        ]
        df_in_SETProdOCCons[null_columns] = '-'

        #   5.1.3 int 컬럼 null 설정
        null_columns = [
            LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
        ]
        df_in_SETProdOCCons[null_columns] = 0

        #   5.1.4 컬럼명 변경 및 추가
        df_in_SETProdOCCons.rename(columns={
            TO_DEMAND_ID_COLUMN: TO_DEMAND_DEMANDID_COLUMN,
            TO_ORDERLINE_ID_COLUMN: TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            FROM_ACTIVITY3_COLUMN: LCM_ITEM_COLUMN,
            FROM_LOCATION_COLUMN: LCM_SITE_COLUMN,
            TO_TO_ITEM_TO_ITEM_COLUMN: SET_ITEM_COLUMN,
            TO_TO_LOCATION_TO_LOCATION_COLUMN: SET_SITE_COLUMN,
            TO_TO_TIME_TO_WEEK_COLUMN: SET_MFG_WEEK_COLUMN,
            FROM_ITEM_COLUMN: OC_ITEM_COLUMN,
        }, inplace=True)

        # 5.2 'BOM_VERSION' 컬럼 설정
        extract_bom_version(df_in_SETProdOCCons, TO_ACTIVITY2_COLUMN, BOM_VERSION_COLUMN)
        print_df(df_in_SETProdOCCons, 'STEP3 by 5.1 ____ df_in_SETProdOCCons .... modify')

        # 5.3 필요컬럼 발췌
        df_in_SETProdOCCons = df_in_SETProdOCCons[[
            TO_DEMAND_DEMANDID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, SET_TRANSMODE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN,
            SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
            OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            PTYPE_COLUMN
        ]]

        print_df(df_in_SETProdOCCons, 'STEP3 by 5.2 ____ df_in_SETProdOCCons')

        # ====================> STEP3 by 5 (End)





        # ====================> STEP3 by 6 (Start) -> df_in_SETProdOCProd (SET Prod / Open Cell prod at LCM Plant)

        # ====================> STEP3 by 6 (End)





        # ====================> STEP3 by 7 (Start) -> df_in_SETProdPanelCons (SET Prod / PANEL cons at Plant)

        # 7.1 null 컬럼 및 기타 컬럼 설정
        #   7.1.1 'PTYPE' 컬럼 설정
        df_in_SETProdPanelCons[PTYPE_COLUMN] = '7. SET Prod PANEL cons at Plant'

        #   7.1.2 str 컬럼 null 설정
        null_columns = [
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, DC_SITE_COLUMN, SET_TRANSMODE_COLUMN,
        ]
        df_in_SETProdPanelCons[null_columns] = '-'

        #   7.1.3 int 컬럼 null 설정
        null_columns = [
            LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
        ]
        df_in_SETProdPanelCons[null_columns] = 0

        #   7.1.4 컬럼명 변경 및 추가
        df_in_SETProdPanelCons.rename(columns={
            TO_DEMAND_ID_COLUMN: TO_DEMAND_DEMANDID_COLUMN,
            TO_ORDERLINE_ID_COLUMN: TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            TO_TO_ITEM_TO_ITEM_COLUMN: SET_ITEM_COLUMN,
            TO_TO_LOCATION_TO_LOCATION_COLUMN: SET_SITE_COLUMN,
            TO_TO_TIME_TO_WEEK_COLUMN: SET_MFG_WEEK_COLUMN,
            FROM_ITEM_COLUMN: COMPLETE_PANEL_ITEM_COLUMN,
        }, inplace=True)
        df_in_SETProdPanelCons[OC_ITEM_COLUMN] = df_in_SETProdPanelCons[COMPLETE_PANEL_ITEM_COLUMN]

        # 7.2 'BOM_VERSION' 컬럼 설정
        extract_bom_version(df_in_SETProdPanelCons, TO_ACTIVITY2_COLUMN, BOM_VERSION_COLUMN)
        print_df(df_in_SETProdPanelCons, 'STEP3 by 7.1 ____ df_in_SETProdPanelCons .... modify')

        # 7.3 필요컬럼 발췌
        df_in_SETProdPanelCons = df_in_SETProdPanelCons[[
            TO_DEMAND_DEMANDID_COLUMN,
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, SET_TRANSMODE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN,
            LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN,
            SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN,
            OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
            PTYPE_COLUMN
        ]]

        print_df(df_in_SETProdPanelCons, 'STEP3 by 7.2 ____ df_in_SETProdPanelCons')

        # ====================> STEP3 by 7 (End)

        step('=====> STEP3 End')



        # ################################################################################################################
        # # STEP 4 : output data machining
        # ################################################################################################################
        step('=====> STEP4 Start : output data machining')

        # SOPAdjustPegging create -> 필수로 만들어 져야 하는 df
        df_SETSOPAdjustPegging = pd.concat([
            df_in_SETShipmentSETProd, df_in_SETShipmentSETProdBOH, df_in_SETProdLCMBOH, df_in_SETProdLCMCons,
            df_in_SETProdLCMProd, df_in_SETProdOCCons, df_in_SETProdPanelCons
        ])
        print_df(df_SETSOPAdjustPegging, 'STEP4 by 0.0 ____ df_SETSOPAdjustPegging .... input merge', True)



        # ------------------ 테스트 디버깅용 ------------------ start
        # df_SETSOPAdjustPegging = df_SETSOPAdjustPegging[df_SETSOPAdjustPegging[SET_ITEM_COLUMN] == 'LS27D806EANXGO']
        # ------------------ 테스트 디버깅용 ------------------ end



        # 값이 비어있거나 None이면 False로 하고 empty df 를 생성하고 종료
        if df_SETSOPAdjustPegging.empty:
            raise CustomException("STEP4 .... df_SETSOPAdjustPegging 값이 없습니다.")



        # 'PTYPE' 컬럼 삭제
        df_SETSOPAdjustPegging.drop(columns=[PTYPE_COLUMN], inplace=True)



        # 0 df_SETSOPAdjustPegging 컬럼타입 설정
        str_columns = [
            SET_ITEM_COLUMN, LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, DC_SITE_COLUMN, SET_SITE_COLUMN,
            BOM_VERSION_COLUMN, SET_TRANSMODE_COLUMN, OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN,
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
        ]
        df_SETSOPAdjustPegging[str_columns] = df_SETSOPAdjustPegging[str_columns].fillna('-').astype(str)

        int_columns = [LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN]
        # df_SETSOPAdjustPegging[int_columns] = (pd.to_numeric(df_SETSOPAdjustPegging[int_columns], errors='coerce').fillna(0).astype(int))
        df_SETSOPAdjustPegging[int_columns] = df_SETSOPAdjustPegging[int_columns].fillna(0).astype(int)

        week_columns = [LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN, SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN]
        # df_SETSOPAdjustPegging[week_columns] = (pd.to_numeric(df_SETSOPAdjustPegging[week_columns], errors='coerce').fillna(0).astype(int))
        df_SETSOPAdjustPegging[week_columns] = df_SETSOPAdjustPegging[week_columns].fillna(0).astype(int)

        print_df(df_SETSOPAdjustPegging, 'STEP4 by 0.1 ____ df_SETSOPAdjustPegging .... create')





        # ---------------------------------------------------------------------------------------------------------
        # df_SETSOPAdjustPegging modify(groupby) 하기 전, DemandW 를 처리하기 위해서 df_SETSOPAdjustPegging -> df_SOPDemandW 로 copy
        #   Step 7 > SOP Demand W 에서 처리
        df_SOPDemandW = df_SETSOPAdjustPegging.copy()
        # ---------------------------------------------------------------------------------------------------------




        # 1. df_SETSOPAdjustPegging modify
        #   1.1 df_SETSOPAdjustPegging 1차 groupby (최대값 및 합계 계산)
        max_columns = [
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN, DC_SITE_COLUMN,
            SET_TRANSMODE_COLUMN, SET_SOP_WEEK_COLUMN, OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN,
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN,
        ]
        groupby_columns = [TO_DEMAND_DEMANDID_COLUMN, SET_ITEM_COLUMN, SET_SITE_COLUMN, BOM_VERSION_COLUMN, SET_MFG_WEEK_COLUMN]
        sum_columns = [LCM_MFG_QTY_COLUMN, LCM_SOP_QTY_COLUMN, LCM_BOH_QTY_COLUMN, SET_MFG_QTY_COLUMN, SET_SOP_QTY_COLUMN, SET_BOH_QTY_COLUMN]
        agg_dict = {col: 'max' for col in max_columns}
        agg_dict.update({col: 'sum' for col in sum_columns})
        df_SETSOPAdjustPegging = df_SETSOPAdjustPegging.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SETSOPAdjustPegging, 'STEP4 by 1.1 ____ df_SETSOPAdjustPegging .... groupby 1')


        #   1.2 df_SETSOPAdjustPegging 2차 groupby ('TO_DEMAND_DEMANDID' 컬럼을 제외한 최대값 및 합계 계산)
        df_SETSOPAdjustPegging.drop(columns=[TO_DEMAND_DEMANDID_COLUMN], inplace=True)

        max_columns = [OC_ITEM_COLUMN, COMPLETE_PANEL_ITEM_COLUMN, FROM_DOCUMENT_ORDERLINE_ID_COLUMN, TO_DOCUMENT_ORDERLINE_ID_COLUMN]
        groupby_columns = [
            LCM_ITEM_COLUMN, LCM_SITE_COLUMN, LCM_TRANSMODE_COLUMN, LCM_MFG_WEEK_COLUMN, LCM_SOP_WEEK_COLUMN,
            SET_ITEM_COLUMN, SET_SITE_COLUMN, DC_SITE_COLUMN, BOM_VERSION_COLUMN, SET_TRANSMODE_COLUMN,
            SET_MFG_WEEK_COLUMN, SET_SOP_WEEK_COLUMN
        ]
        agg_dict = {col: 'max' for col in max_columns}
        agg_dict.update({col: 'sum' for col in sum_columns})
        df_SETSOPAdjustPegging = df_SETSOPAdjustPegging.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict,skipna=True)
        df_SETSOPAdjustPegging = df_SETSOPAdjustPegging.replace({pd.NA: None, np.nan: None, 'nan': None, '<NA>': None, '0': None})
        print_df(df_SETSOPAdjustPegging, 'STEP4 by 1.2 ____ df_SETSOPAdjustPegging .... groupby 2')





        # 2 SOP W create
        #   2.1 맵핑 및 컬럼설정
        df_SOP_W = df_SETSOPAdjustPegging.copy()
        df_SOP_W.rename(columns={
            LCM_ITEM_COLUMN: TO_ITEM_TO_ITEM_COLUMN,
            LCM_SITE_COLUMN: SUB_LOCATION_COLUMN,
            LCM_TRANSMODE_COLUMN: TO_TRANS_MODE_COLUMN,
            LCM_MFG_WEEK_COLUMN: WEEK1_COLUMN,
            LCM_SOP_WEEK_COLUMN: WEEK2_COLUMN,
            SET_ITEM_COLUMN: ITEM_COLUMN,
            SET_SITE_COLUMN: LOCATION_COLUMN,
            DC_SITE_COLUMN: TO_LOCATION_TO_LOCATION_COLUMN,
            SET_TRANSMODE_COLUMN: TRANS_MODE_COLUMN,
            SET_MFG_WEEK_COLUMN: TIME_WEEK_COLUMN,
            SET_SOP_WEEK_COLUMN: TO_TIME_TO_WEEK_COLUMN,
            BOM_VERSION_COLUMN: BOM_INFO_BOM_VERSION_COLUMN,
            OC_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            LCM_SOP_QTY_COLUMN: SOP_W_LCM_SOP_QTY_COLUMN,
            LCM_BOH_QTY_COLUMN: SOP_W_LCM_BOH_QTY_COLUMN,
            LCM_MFG_QTY_COLUMN: SOP_W_LCM_MFG_QTY_COLUMN,
            SET_MFG_QTY_COLUMN: SOP_W_SET_MFG_QTY_COLUMN,
            SET_SOP_QTY_COLUMN: SOP_W_SET_SOP_QTY_COLUMN,
            SET_BOH_QTY_COLUMN: SOP_W_SET_BOH_QTY_COLUMN,
            FROM_DOCUMENT_ORDERLINE_ID_COLUMN: SOP_W_LCM_SOP_ID_COLUMN,
        }, inplace=True)
        df_SOP_W[SOP_W_LCM_PLANT_COLUMN] = df_SOP_W[SUB_LOCATION_COLUMN]
        df_SOP_W[SOP_W_SOP_ID_COLUMN] = df_SOP_W[TO_DOCUMENT_ORDERLINE_ID_COLUMN]
        df_SOP_W[SOP_W_LCM_MFG_ADJ_QTY_COLUMN] = df_SOP_W[SOP_W_LCM_MFG_QTY_COLUMN]
        df_SOP_W[SOP_W_SET_MFG_ADJ_QTY_COLUMN] = df_SOP_W[SOP_W_SET_MFG_QTY_COLUMN]
        print_df(df_SOP_W, 'STEP4 by 2.1 ____ df_SOP_W .... columns set')

        #   2.2 df_in_CodeMap 조인해서 'Code Map LCM_Prod Item' 값을 'SOP W_Prd Item' 으로 설정
        df_SOP_W = pd.merge(df_SOP_W, df_in_CodeMap, how='left',
                            left_on=[TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN],
                            right_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN], )
        print_df(df_SOP_W, 'STEP4 by 2.2.1 ____ df_SOP_W .... merge[df_SOP_W, df_in_CodeMap]')

        df_SOP_W[ITEM_COMPONENT_COLUMN] = df_SOP_W[CODE_MAP_LCM_PROD_ITEM_COLUMN]
        df_SOP_W[ITEM_COMPONENT_COLUMN] = df_SOP_W[ITEM_COMPONENT_COLUMN].fillna('-').astype(str)
        df_SOP_W.rename(columns={
            'Location.[Location]_x': LOCATION_COLUMN,
            'Sub Location.[Sub Location]_x': SUB_LOCATION_COLUMN,
            'Item.[Item]_x': ITEM_COLUMN,
        },inplace=True)
        print_df(df_SOP_W, 'STEP4 by 2.2.2 ____ df_SOP_W ..... columns rename')


        #   2.3 'SOP W_SOP ID' 설정
        filtered_df_SOP_W = df_SOP_W[df_SOP_W[TO_DOCUMENT_ORDERLINE_ID_COLUMN].str.contains('000SCS_LOT', na=False)]
        df_SOP_W.loc[filtered_df_SOP_W.index, SOP_W_SOP_ID_COLUMN] = [
            str(df_SOP_W[TIME_WEEK_COLUMN].iloc[i]) + '_' + str(i + 1).zfill(7) for i in filtered_df_SOP_W.index
        ]

        filtered_df_SOP_W = df_SOP_W[df_SOP_W[TO_DOCUMENT_ORDERLINE_ID_COLUMN].str.contains('ON_', na=False)]
        df_SOP_W.loc[filtered_df_SOP_W.index, SOP_W_SOP_ID_COLUMN] = [
            'ON_' + str(df_SOP_W[TIME_WEEK_COLUMN].iloc[i]) + '_' + str(i + 1).zfill(7) for i in
            filtered_df_SOP_W.index
        ]

        df_SOP_W = pd.merge(df_SOP_W, df_in_FullBOM, how='left', on=[ITEM_COLUMN, LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN])
        print_df(df_SOP_W, 'STEP4 by 2.3.1 ____ df_SOP_W .... pd.merge[df_SOP_W, df_in_FullBOM]')
        df_SOP_W.rename(columns={
            TO_LOCATION_TO_LOCATION_COLUMN+'_x' : TO_LOCATION_TO_LOCATION_COLUMN,
            ITEM_METERIAL_COLUMN+'_x' : ITEM_METERIAL_COLUMN,
            BOM_INFO_BOM_VERSION_COLUMN+'_x' : BOM_INFO_BOM_VERSION_COLUMN,
            BOM_STATUS_BOM_STATUS_COLUMN: SOP_W_BOM_STATUS_COLUMN,
        }, inplace=True)
        print_df(df_SOP_W, 'STEP4 by 2.3.2 ____ df_SOP_W .... columns rename')

        df_SOP_W = pd.merge(df_SOP_W, df_in_AllWeek, how='left',
                            left_on=[FULL_BOM_CREATION_TIME_COLUMN],
                            right_on=[TIME_DAY_COLUMN])
        print_df(df_SOP_W, 'STEP4 by 2.3.3 ____ df_SOP_W .... pd.merge[df_SOP_W, df_in_AllWeek]')

        df_SOP_W.rename(columns={
            TIME_WEEK_COLUMN+'_x' : TIME_WEEK_COLUMN,
            TIME_WEEK_COLUMN+'_y' : SOP_W_BOM_CFM_W_COLUMN,
        }, inplace=True)
        df_SOP_W[SOP_W_BOM_STATUS_COLUMN] = df_SOP_W[SOP_W_BOM_STATUS_COLUMN].fillna('-').astype(str).replace({'-': None})
        df_SOP_W[SOP_W_BOM_CFM_W_COLUMN] = df_SOP_W[SOP_W_BOM_CFM_W_COLUMN].fillna('-').astype(str).replace({'-': None})
        print_df(df_SOP_W, 'STEP4 by 2.3.5 ____ df_SOP_W .... columns rename')


        #   2.4 최종 output 컬럼 설정
        df_SOP_W[SEQUENCE_COLUMN] = None
        df_SOP_W = df_SOP_W[df_SOP_W_columns].drop_duplicates()

        #       주차 add
        columns = [
            ITEM_COLUMN, TIME_WEEK_COLUMN, LOCATION_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, SUB_LOCATION_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN, ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN,
        ]
        df_missing_rows = set_unique_combinations(df_SOP_W, df_in_MDMHorizon, columns)
        df_SOP_W = pd.concat([df_SOP_W, df_missing_rows], ignore_index=True).drop_duplicates()
        print_df(df_SOP_W, 'STEP4 by 2.4.1 ____ df_SOP_W .... Time Week empty add')

        #       날짜컬럼 설정
        week_columns = [TIME_WEEK_COLUMN, WEEK1_COLUMN, WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN]
        df_SOP_W[week_columns] = df_SOP_W[week_columns].fillna(0).astype('int32')
        mask = df_SOP_W[week_columns] == 0
        df_SOP_W[week_columns] = df_SOP_W[week_columns].mask(mask, mp_plan_start_week).astype('int32')

        print_df(df_SOP_W, 'STEP4 by 2.4.2 ____ df_SOP_W ..... week empty 처리')

        #       시퀸스 설정
        df_SOP_W[SEQUENCE_COLUMN] = range(1000001, 1000001 + len(df_SOP_W))

        #       숫자컬럼설정
        int_columns = [
            SEQUENCE_COLUMN,
            SOP_W_SET_MFG_QTY_COLUMN, SOP_W_SET_MFG_ADJ_QTY_COLUMN, SOP_W_SET_SOP_QTY_COLUMN, SOP_W_SET_BOH_QTY_COLUMN,
            SOP_W_LCM_MFG_QTY_COLUMN, SOP_W_LCM_SOP_QTY_COLUMN, SOP_W_LCM_BOH_QTY_COLUMN, SOP_W_LCM_MFG_ADJ_QTY_COLUMN,
        ]
        df_SOP_W[int_columns] = df_SOP_W[int_columns].fillna(0).astype('int32')

        df_SOP_W[VERSION_NAME_COLUMN] = paramOutVersion
        print_df(df_SOP_W, 'STEP4 by 2.4 ____ df_SOP_W .... final')






        # 3 SOP create
        #   3.1 맵핑 및 컬럼설정
        df_SOP = df_SOP_W.copy()
        df_SOP[SOP_MIN_LOT_QTY_COLUMN] = 0
        df_SOP[SOP_MULTIPLE_LOT_QTY_COLUMN] = 0
        print_df(df_SOP, 'STEP4 by 3.1 ____ df_SOP .... columns set')

        #   3.2 Max 연산을 위한 agg 딕셔니러 생성
        max_columns = [SEQUENCE_COLUMN]
        groupby_columns = [
            VERSION_NAME_COLUMN, ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN,
            TO_LOCATION_TO_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TRANS_MODE_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, ITEM_METERIAL_COLUMN, BOM_INFO_BOM_VERSION_COLUMN, SOP_MIN_LOT_QTY_COLUMN, SOP_MULTIPLE_LOT_QTY_COLUMN,
        ]

        #   3.3 그룹화 및 집계 수행
        agg_dict = {col: 'max' for col in max_columns}
        df_SOP = df_SOP.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)

        #   3.4 최종 output 컬럼 설정
        df_SOP = df_SOP[df_SOP_columns].drop_duplicates()

        print_df(df_SOP, 'STEP4 by 3.4 ____ df_SOP .... final')






        # 4 SOP Adjustment SET W create
        #   4.1 맵핑 및 컬럼설정
        df_SOPAdjustmentSETW = df_SETSOPAdjustPegging.copy()
        df_SOPAdjustmentSETW.rename(columns={
            SET_SITE_COLUMN: LOCATION_COLUMN,
            DC_SITE_COLUMN: TO_LOCATION_TO_LOCATION_COLUMN,
            SET_TRANSMODE_COLUMN: TRANS_MODE_COLUMN,
            SET_ITEM_COLUMN: ITEM_COLUMN,
            SET_MFG_WEEK_COLUMN: TIME_WEEK_COLUMN,
            SET_MFG_QTY_COLUMN: SOP_ADJUST_SET_W_SOP_QTY_COLUMN,
        }, inplace=True)
        print_df(df_SOPAdjustmentSETW, 'STEP4 by 4.1 ____ df_SOPAdjustmentSETW .... create')

        #   4.2 컬럼설정
        df_SOPAdjustmentSETW[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN] = df_SOPAdjustmentSETW[SOP_ADJUST_SET_W_SOP_QTY_COLUMN]
        df_SOPAdjustmentSETW[SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN] = 0
        df_SOPAdjustmentSETW[VERSION_NAME_COLUMN] = paramOutVersion
        print_df(df_SOPAdjustmentSETW, 'STEP4 by 4.2 ____ df_SOPAdjustmentSETW .... columns set')

        #   4.3 최종 output 컬럼 설정
        df_SOPAdjustmentSETW = df_SOPAdjustmentSETW[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TIME_WEEK_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN,
            SOP_ADJUST_SET_W_SOP_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN,
        ]]
        print_df(df_SOPAdjustmentSETW, 'STEP4 by 4.3 ____ df_SOPAdjustmentSETW .... final columns set')

        #   4.4 groupby
        groupby_columns = [VERSION_NAME_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN]
        sum_columns = [SOP_ADJUST_SET_W_SOP_QTY_COLUMN, SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_SOPAdjustmentSETW = df_SOPAdjustmentSETW.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SOPAdjustmentSETW, 'STEP4 by 4.4 ____ df_SOPAdjustmentSETW .... groupby')

        #   4.5 SETW create
        df_SOPAdjustmentSETW = df_SOPAdjustmentSETW[df_SOPAdjustmentSETW_columns].drop_duplicates()
        print_df(df_SOPAdjustmentSETW, 'STEP4 by 4.5 ____ df_SOPAdjustmentSETW .... SETW create')

        #   4.6 주차 채워넣기
        columns = [LOCATION_COLUMN, TIME_WEEK_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN]
        df_missing_rows = set_unique_combinations(df_SOPAdjustmentSETW, df_in_MDMHorizon, columns)
        df_SOPAdjustmentSETW = pd.concat([df_SOPAdjustmentSETW, df_missing_rows], ignore_index=True).drop_duplicates()
        print_df(df_SOPAdjustmentSETW, 'STEP4 by 4.6 ____ df_SOPAdjustmentSETW .... week empty add')

        int_columns = [SOP_ADJUST_SET_W_SOP_QTY_COLUMN, SOP_ADJUST_SET_W_BEFORE_ADJ_QTY_COLUMN]
        df_SOPAdjustmentSETW[int_columns] = df_SOPAdjustmentSETW[int_columns].fillna(0).astype('int32')
        df_SOPAdjustmentSETW[VERSION_NAME_COLUMN] = paramOutVersion
        print_df(df_SOPAdjustmentSETW, 'STEP4 by 4.7 ____ df_SOPAdjustmentSETW .... final')

        #   4.8 SETWAdj create
        df_SOPAdjustmentSETWAdj = df_SOPAdjustmentSETW.copy()
        df_SOPAdjustmentSETWAdj[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN] = df_SOPAdjustmentSETWAdj[SOP_ADJUST_SET_W_SOP_QTY_COLUMN]
        df_SOPAdjustmentSETWAdj[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN] = df_SOPAdjustmentSETWAdj[SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN].astype(int)
        df_SOPAdjustmentSETWAdj = df_SOPAdjustmentSETWAdj[df_SOPAdjustmentSETWAdj_columns]

        groupby_columns = [VERSION_NAME_COLUMN, LOCATION_COLUMN, TO_LOCATION_TO_LOCATION_COLUMN, TRANS_MODE_COLUMN, ITEM_COLUMN, TIME_WEEK_COLUMN]
        sum_columns = [SOP_ADJUST_SET_W_SOP_ADJ_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_SOPAdjustmentSETWAdj = df_SOPAdjustmentSETWAdj.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SOPAdjustmentSETWAdj, 'STEP4 by 4.8 ____ df_SOPAdjustmentSETWAdj .... final')








        # 5 SOP Adjustment SET create
        #   5.1 맵핑 및 컬럼설정
        df_SOPAdjustmentSET = df_SOPAdjustmentSETW.copy()
        df_SOPAdjustmentSET[SOP_ADJUST_SET_MIN_LOT_QTY_COLUMN] = 0
        df_SOPAdjustmentSET[SOP_ADJUST_SET_MULTIPLE_LOT_QTY_COLUMN] = 0

        #   5.2 최종 output 컬럼 설정
        df_SOPAdjustmentSET = df_SOPAdjustmentSET[df_SOPAdjustmentSET_columns].drop_duplicates()
        print_df(df_SOPAdjustmentSET, 'STEP4 by 5.2 ____ df_SOPAdjustmentSET .... final')






        # 6 SOP Adjustment LCM W create
        #   6.1 맵핑 및 컬럼설정
        df_SOPAdjustmentLCMW = df_SETSOPAdjustPegging.copy()
        df_SOPAdjustmentLCMW.rename(columns={
            LCM_SITE_COLUMN: SUB_LOCATION_COLUMN,
            SET_SITE_COLUMN: LOCATION_COLUMN,
            LCM_TRANSMODE_COLUMN: TO_TRANS_MODE_COLUMN,
            OC_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            LCM_ITEM_COLUMN: TO_ITEM_TO_ITEM_COLUMN,
            SET_ITEM_COLUMN: ITEM_COLUMN,
            LCM_MFG_WEEK_COLUMN: WEEK1_COLUMN,
            LCM_MFG_QTY_COLUMN: SOP_ADJUST_LCM_W_SOP_QTY_COLUMN,
        }, inplace=True)
        print_df(df_SOPAdjustmentLCMW, 'STEP4 by 6.1 ____ df_SOPAdjustmentLCMW .... create')

        #   6.2 df_in_CodeMap 조인해서 'Code Map LCM_Prod Item' 값을 'SOP W_Prd Item' 으로 설정
        df_SOPAdjustmentLCMW = pd.merge(df_SOPAdjustmentLCMW, df_in_CodeMap, how='left',
                                        left_on=[TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN],
                                        right_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN], )
        print_df(df_SOPAdjustmentLCMW, 'STEP4 by 6.2 ____ df_SOPAdjustmentLCMW .... df_in_CodeMap merge')

        #   6.3
        df_SOPAdjustmentLCMW.rename(columns={
            CODE_MAP_LCM_PROD_ITEM_COLUMN: ITEM_COMPONENT_COLUMN,
            'Location.[Location]_x': LOCATION_COLUMN,
            'Sub Location.[Sub Location]_x': SUB_LOCATION_COLUMN,
            'Item.[Item]_x': ITEM_COLUMN,
        }, inplace=True)
        df_SOPAdjustmentLCMW[VERSION_NAME_COLUMN] = paramOutVersion
        df_SOPAdjustmentLCMW[ITEM_COMPONENT_COLUMN] = df_SOPAdjustmentLCMW[ITEM_COMPONENT_COLUMN].fillna('-')
        print_df(df_SOPAdjustmentLCMW, 'STEP4 by 6.3 ____ df_SOPAdjustmentLCMW .... columns rename')

        #   6.4 컬럼설정
        df_SOPAdjustmentLCMW[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN] = df_SOPAdjustmentLCMW[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN]
        df_SOPAdjustmentLCMW[SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN] = 0

        week_columns = [WEEK1_COLUMN]
        df_SOPAdjustmentLCMW[week_columns] = df_SOPAdjustmentLCMW[week_columns].astype(str).replace({'0': None})
        df_SOPAdjustmentLCMW[week_columns] = df_SOPAdjustmentLCMW[week_columns].fillna(mp_plan_start_week).astype(int)
        print_df(df_SOPAdjustmentLCMW, 'STEP4 by 6.4 ____ df_SOPAdjustmentLCMW .... columns set')

        #   6.5 최종 output 컬럼 설정
        df_SOPAdjustmentLCMW = df_SOPAdjustmentLCMW[[
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN,
            SOP_ADJUST_LCM_W_SOP_QTY_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN,
        ]]
        print_df(df_SOPAdjustmentLCMW, 'STEP4 by 6.5 ____ df_SOPAdjustmentLCMW .... columns final')

        #   6.6 groupby
        groupby_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN
        ]
        sum_columns = [SOP_ADJUST_LCM_W_SOP_QTY_COLUMN, SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN, SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_SOPAdjustmentLCMW = df_SOPAdjustmentLCMW.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SOPAdjustmentLCMW, 'STEP4 by 6.6 ____ df_SOPAdjustmentLCMW .... groupby')

        #   6.7 LCMW create
        df_SOPAdjustmentLCMW = df_SOPAdjustmentLCMW[df_SOPAdjustmentLCMW_columns].drop_duplicates()

        int_columns = [WEEK1_COLUMN, SOP_ADJUST_LCM_W_SOP_QTY_COLUMN, SOP_ADJUST_LCM_W_BEFORE_ADJ_QTY_COLUMN]
        df_SOPAdjustmentLCMW[int_columns] = df_SOPAdjustmentLCMW[int_columns].astype('int32')
        df_SOPAdjustmentLCMW[VERSION_NAME_COLUMN] = paramOutVersion
        print_df(df_SOPAdjustmentLCMW, 'STEP4 by 6.7 ____ df_SOPAdjustmentLCMW .... final')

        #   6.8 LCMWAdj create
        df_SOPAdjustmentLCMWAdj = df_SOPAdjustmentLCMW.copy()
        df_SOPAdjustmentLCMWAdj[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN] = df_SOPAdjustmentLCMWAdj[SOP_ADJUST_LCM_W_SOP_QTY_COLUMN]
        df_SOPAdjustmentLCMWAdj[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN] = df_SOPAdjustmentLCMWAdj[SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN].astype(int)
        df_SOPAdjustmentLCMWAdj = df_SOPAdjustmentLCMWAdj[df_SOPAdjustmentLCMWAdj_columns]

        groupby_columns = [
            VERSION_NAME_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN, TO_ITEM_TO_ITEM_COLUMN, TO_TRANS_MODE_COLUMN,
            ITEM_COMPONENT_COLUMN, WEEK1_COLUMN, ITEM_METERIAL_COLUMN
        ]
        sum_columns = [SOP_ADJUST_LCM_W_SOP_ADJ_QTY_COLUMN]
        agg_dict = {col: 'sum' for col in sum_columns}
        df_SOPAdjustmentLCMWAdj = df_SOPAdjustmentLCMWAdj.groupby(groupby_columns, sort=False, as_index=False).agg(agg_dict, skipna=True)
        print_df(df_SOPAdjustmentLCMWAdj, 'STEP4 by 6.8 ____ df_SOPAdjustmentLCMWAdj .... final')






        # ................................................................................................

        # 7 > MG : SOP Demand W 처리(groupby 하기전 DemandId 처리)
        #   7.1 df_SOPDemandW create
        df_SOPDemandW.rename(columns={
            LCM_ITEM_COLUMN: TO_ITEM_TO_ITEM_COLUMN,
            LCM_SITE_COLUMN: SUB_LOCATION_COLUMN,
            LCM_TRANSMODE_COLUMN: TO_TRANS_MODE_COLUMN,
            LCM_MFG_WEEK_COLUMN: WEEK1_COLUMN,
            LCM_SOP_WEEK_COLUMN: WEEK2_COLUMN,
            SET_ITEM_COLUMN: ITEM_COLUMN,
            SET_SITE_COLUMN: LOCATION_COLUMN,
            DC_SITE_COLUMN: TO_LOCATION_TO_LOCATION_COLUMN,
            SET_TRANSMODE_COLUMN: TRANS_MODE_COLUMN,
            SET_MFG_WEEK_COLUMN: TIME_WEEK_COLUMN,
            SET_SOP_WEEK_COLUMN: TO_TIME_TO_WEEK_COLUMN,
            BOM_VERSION_COLUMN: BOM_INFO_BOM_VERSION_COLUMN,
            OC_ITEM_COLUMN: ITEM_METERIAL_COLUMN,
            TO_DEMAND_DEMANDID_COLUMN: DEMAND_ID_COLUMN,
            LCM_SOP_QTY_COLUMN: SOP_DMD_W_LCM_SOP_QTY_COLUMN,
            LCM_BOH_QTY_COLUMN: SOP_DMD_W_LCM_BOH_QTY_COLUMN,
            LCM_MFG_QTY_COLUMN: SOP_DMD_W_LCM_MFG_QTY_COLUMN,
            SET_SOP_QTY_COLUMN: SOP_DMD_W_SET_SOP_QTY_COLUMN,
            SET_MFG_QTY_COLUMN: SOP_DMD_W_SET_MFG_QTY_COLUMN,
            SET_BOH_QTY_COLUMN: SOP_DMD_W_SET_BOH_QTY_COLUMN,
        }, inplace=True)

        df_SOPDemandW = pd.merge(df_SOPDemandW, df_in_CodeMap, how='left',
                                 left_on=[TO_ITEM_TO_ITEM_COLUMN, LOCATION_COLUMN, SUB_LOCATION_COLUMN],
                                 right_on=[ITEM_COLUMN, SUB_LOCATION_COLUMN, LOCATION_COLUMN], )
        print_df(df_SOPDemandW, 'STEP4 by 7.1 ____> df_SOPDemandW .... merge[df_SOPDemandW, df_in_CodeMap]')
        
        #   7.2 컬럼설정
        df_SOPDemandW.rename(columns={
            CODE_MAP_LCM_PROD_ITEM_COLUMN: ITEM_COMPONENT_COLUMN,
            'Location.[Location]_x': LOCATION_COLUMN,
            'Sub Location.[Sub Location]_x': SUB_LOCATION_COLUMN,
            'Item.[Item]_x': ITEM_COLUMN,
        }, inplace=True)
        print_df(df_SOPDemandW, 'STEP4 by 7.2 ____ df_SOPDemandW .... columns rename')
        
        refill_columns = [
            SUB_LOCATION_COLUMN, TO_TRANS_MODE_COLUMN, TO_ITEM_TO_ITEM_COLUMN, BOM_INFO_BOM_VERSION_COLUMN,
            ITEM_METERIAL_COLUMN, ITEM_COMPONENT_COLUMN,
        ]
        df_SOPDemandW[refill_columns] = df_SOPDemandW[refill_columns].fillna('-').astype(str)

        week_columns = [TIME_WEEK_COLUMN, WEEK1_COLUMN, WEEK2_COLUMN, TO_TIME_TO_WEEK_COLUMN]
        df_SOPDemandW[week_columns] = df_SOPDemandW[week_columns].astype(str).replace({'0': None})
        df_SOPDemandW[week_columns] = df_SOPDemandW[week_columns].fillna(mp_plan_start_week).astype(int)

        df_SOPDemandW[VERSION_NAME_COLUMN] = paramOutVersion
        print_df(df_SOPDemandW, 'STEP4 by 7.3 ____ df_SOPDemandW .... columns rename final')
        
        #   7.4 최종 output 컬럼설정
        df_SOPDemandW[SEQUENCE_COLUMN] = None
        df_SOPDemandW = df_SOPDemandW[df_SOPDemandW_columns].drop_duplicates()
        df_SOPDemandW[SEQUENCE_COLUMN] = range(1000001, 1000001 + len(df_SOPDemandW))

        int_columns = [
            TIME_WEEK_COLUMN, TO_TIME_TO_WEEK_COLUMN, WEEK1_COLUMN, WEEK2_COLUMN, SEQUENCE_COLUMN,
            SOP_DMD_W_LCM_MFG_QTY_COLUMN, SOP_DMD_W_SET_MFG_QTY_COLUMN, SOP_DMD_W_SET_BOH_QTY_COLUMN,
            SOP_DMD_W_LCM_SOP_QTY_COLUMN, SOP_DMD_W_LCM_BOH_QTY_COLUMN,
        ]
        df_SOPDemandW[int_columns] = df_SOPDemandW[int_columns].astype(int)
        print_df(df_SOPDemandW, 'STEP4 by 7.4 ____ df_SOPDemandW .... final')

        # ................................................................................................

        step('=====> STEP4 End')



        ################################################################################################################
        # STEP 5 : output table create
        ################################################################################################################
        step('=====> STEP5 Start : Final output table create')
        
        df_out_SOPW = rename_and_delete_df(df_SOP_W)
        df_out_SOP = rename_and_delete_df(df_SOP)
        df_out_SOPAdjustmentLCMW = rename_and_delete_df(df_SOPAdjustmentLCMW)
        df_out_SOPAdjustmentSETW = rename_and_delete_df(df_SOPAdjustmentSETW)
        df_out_SOPAdjustmentSET = rename_and_delete_df(df_SOPAdjustmentSET)
        df_out_SOPAdjustmentLCMWAdj = rename_and_delete_df(df_SOPAdjustmentLCMWAdj)
        df_out_SOPAdjustmentSETWAdj = rename_and_delete_df(df_SOPAdjustmentSETWAdj)
        df_out_SOPDemandW = rename_and_delete_df(df_SOPDemandW)

        dataframes = {
            'df_out_SOPW': df_out_SOPW,
            'df_out_SOP': df_out_SOP,
            'df_out_SOPAdjustmentLCMW': df_out_SOPAdjustmentLCMW,
            'df_out_SOPAdjustmentSETW': df_out_SOPAdjustmentSETW,
            'df_out_SOPAdjustmentSET': df_out_SOPAdjustmentSET,
            'df_out_SOPAdjustmentLCMWAdj': df_out_SOPAdjustmentLCMWAdj,
            'df_out_SOPAdjustmentSETWAdj': df_out_SOPAdjustmentSETWAdj,
            'df_out_SOPDemandW': df_out_SOPDemandW,
        }

        for name, df in dataframes.items():
            print_df(df, f'output table create .... {name}', True)

        step('=====> STEP5 End')

    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_SOPW = pd.DataFrame(columns=df_SOP_W_columns)
        df_out_SOP = pd.DataFrame(columns=df_SOP_columns)
        df_out_SOPAdjustmentLCMW = pd.DataFrame(columns=df_SOPAdjustmentSETW_columns)
        df_out_SOPAdjustmentSETW = pd.DataFrame(columns=df_SOPAdjustmentSET_columns)
        df_out_SOPAdjustmentSET = pd.DataFrame(columns=df_SOPAdjustmentLCMW_columns)
        df_out_SOPAdjustmentSETWAdj = pd.DataFrame(columns=df_SOPAdjustmentLCMWAdj_columns)
        df_out_SOPAdjustmentLCMWAdj = pd.DataFrame(columns=df_SOPAdjustmentSETWAdj_columns)
        df_out_SOPDemandW = pd.DataFrame(columns=df_SOPDemandW_columns)


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        df_out_SOPW = pd.DataFrame(columns=df_SOP_W_columns)
        df_out_SOP = pd.DataFrame(columns=df_SOP_columns)
        df_out_SOPAdjustmentLCMW = pd.DataFrame(columns=df_SOPAdjustmentSETW_columns)
        df_out_SOPAdjustmentSETW = pd.DataFrame(columns=df_SOPAdjustmentSET_columns)
        df_out_SOPAdjustmentSET = pd.DataFrame(columns=df_SOPAdjustmentLCMW_columns)
        df_out_SOPAdjustmentSETWAdj = pd.DataFrame(columns=df_SOPAdjustmentLCMWAdj_columns)
        df_out_SOPAdjustmentLCMWAdj = pd.DataFrame(columns=df_SOPAdjustmentSETWAdj_columns)
        df_out_SOPDemandW = pd.DataFrame(columns=df_SOPDemandW_columns)
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())

    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
        logger.Finish()
