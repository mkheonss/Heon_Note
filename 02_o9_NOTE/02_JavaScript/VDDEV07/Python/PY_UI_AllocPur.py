"""
* 프로그램명 
    - PY_UI_AllocPur

* 내용
    - Alloc Pur UI Measure 데이터 생성

* 변경이력
    - 2024.12.18 / 양희영 / Create
    - 2025.02.20 / 양희영 / Update (20250220 : Alloc Pur 로 통합 반영, [Marketing Name].[Marketing Name] 삭제 반영)
    - 2025.09.18 / 양희영 / Update

* Flow Summary
    Alloc Pur 화면에 사용되는 Open Cell의 할당 정보 생성

* Execution 

* Script Parameter
    - paramOutVersion : CWV_MP : 사용안함.

* Input Tables
    - df_in_C2P : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID] * FROM.[Activity2].[Activity2] * FROM.[Activity1].[Activity1] * 
                  FROM.[Location].[Site Stage].[SP].relatedmembers([Location]) * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * 
                  TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * TO.[To Item].[To Item Stage].[OPEN_CELL].relatedmembers([To Item]) * TO.[Activity3].[Activity3] * 
                  TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * TO.[To Location].[To Location Type].[MF].relatedmembers([To Location]) * 
                  TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
                  ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer From Pegged]}) 
                  on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_P2P : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID] * FROM.[Activity2].[Activity2] * FROM.[Activity1].[Activity1] * FROM.[Location].[Location] * 
                  FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * FROM.[Item].[Item Stage] * TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * 
                  TO.[To Item].[To Item Stage].[SET].relatedmembers([To Item]) * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * 
                  TO.[To Location].[To Location Type].[MF].relatedmembers([To Location]) * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row,
                  ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) 
                  on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_BSHUB : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID] * FROM.[Activity2].[Activity2] * FROM.[Activity1].[Activity1] * FROM.[Activity1].[From Location] * 
                    FROM.[Activity1].[To Location] * FROM.[Location].[Location].[P105SP] * FROM.[Location].[Site Stage].[SP] * FROM.[Activity3].[Activity3] * From.[Item].[Item] * FROM.[Item].[Item Stage].[OPEN_CELL] * 
                    TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * TO.[To Item].[To Item] * TO.[To Item].[To Item Stage] * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * 
                    TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * TO.[To Location].[To Location] * TO.[To Location].[To Location Type].[MF] * TO.[Time].[Week] * TO.[Location].[Location] * 
                    TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
                    ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Consumer to Producer From Pegged]}) 
                    on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_OnHand : Select (Version.[Version Name] * FROM.[Time].[Week].filter(#.Name == &CurrentWeek.element(0).Name) * FROM.[Documents].[OrderlineID].filter(#.Name != "000SCS_LOT") * FROM.[Activity2].[Activity2] * 
                     FROM.[Activity1].[Activity1].[BOHActivity] * FROM.[Location].[Location] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item] * FROM.[Item].[Item Stage].[OPEN_CELL] * TO.[Demand Type].[Demand Type] * 
                     TO.[Demand].[DemandID] * TO.[To Item].[To Item] * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * TO.[To Location].[To Location] * 
                     TO.[To Location].[To Location Type].[MF] * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
                     ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) 
                     on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_LT : Select ([Version].[Version Name] * [Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * [Location].[Site Stage].[SP].relatedmembers([Location]) * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row, 
                 ({Measure.[BOD Item_BOD LT]}) on column;
    - df_in_ER : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID].filter(#.Name != "000SCS_LOT") * FROM.[Activity2].[Activity2] * FROM.[Activity1].[Activity1].[ExpectedReceiptActivity] * 
                 FROM.[Location].[Location] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item] * FROM.[Item].[Item Stage].[OPEN_CELL] * TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * TO.[To Item].[To Item] * 
                 TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * TO.[To Location].[To Location] * TO.[To Location].[To Location Type].[MF] * 
                 TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
                 ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) 
                 on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_Short : Select (Version.[Version Name] * FROM.[Activity1].[Activity1] * FROM.[Activity1].[From Location] * FROM.[Activity1].[To Location] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * 
                    FROM.[RootCause].[Problem Type] * FROM.[Location].[Site Stage].filter(#.Name in {"MF_LCM","MF_LCM_EX"}).relatedmembers([Location]) * FROM.[Time].[Week] *  
                    FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * TO.[Demand Type].[Demand Type] * TO.[Sales Domain].[Customer Group] * TO.[Time].[Week] * TO.[Demand].[DemandID] * 
                    TO.[Location].[Location] * TO.[Item].[Item]) on row, ({Edge.[002.005W Solver Outputs Material Root Cause].[W Material Root Cause Quantity]}) 
                    on column where {RelationshipType.[002.005W Solver Outputs Material Root Cause]};
    - df_in_OPO : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID].filter(#.Name != "000SCS_LOT") * FROM.[Activity2].[Activity2] * 
                  FROM.[Activity1].[Activity Type1].[Distribution].relatedmembers([Activity1]) * FROM.[Location].[Location] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item] * FROM.[Item].[Item Stage].[OPEN_CELL] * 
                  TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * TO.[To Item].[To Item] * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * 
                  TO.[To Location].[To Location] * TO.[To Location].[To Location Type].[MF] * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
                  ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) 
                  on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_NOH : Select (Version.[Version Name] * FROM.[Time].[Week] * FROM.[Documents].[OrderlineID].filter(#.Name =="000SCS_LOT" || #.Name startswith "ER") * FROM.[Activity2].[Activity2] * 
                  FROM.[Activity1].[Activity1].[ExpectedReceiptActivity] * FROM.[Location].[Location] * FROM.[Activity3].[Activity3] * FROM.[Item].[Item Stage].[OPEN_CELL].relatedmembers([Item]) * 
                  TO.[Demand Type].[Demand Type] * TO.[Demand].[DemandID] * TO.[To Item].[To Item] * TO.[Activity3].[Activity3] * TO.[Sales Domain].[Customer Group] * TO.[To Time].[To Week] * TO.[Activity1].[Activity1] * 
                  TO.[To Location].[To Location] * TO.[Time].[Week] * TO.[Location].[Location] * TO.[Documents].[OrderlineID] * TO.[Item].[Item] * TO.[Activity2].[Activity2]) on row, 
                  ({Edge.[SOP Bottom Up Pegging Output Graph].[SOP BUP Producer to Producer From Pegged]}) 
                  on column where {RelationshipType.[SOP Bottom Up Pegging Output Graph]};
    - df_in_BOMMaster : Select ([Version].[Version Name] * [Location].[Location] * [BOM Info].[BOM ID] ) on row, 
                        ({Measure.[BOM Master_BOM ID], Measure.[BOM Master_Eff Enddate], Measure.[BOM Master_Eff Startdate], Measure.[BOM Master_Prty], Measure.[BOM Master_Status]}) on column;
    - df_in_Horizon : Select ([Time].[Week] ) on row  where {&CWVUi, Measure.[isMPHorizonFlag]==true};
    
    # 2025.09.08 추가 ------------------------------------------
    - df_in_SupplyFrozenFixRange_Item : Select ([Version].[Version Name] * &CurrentWeek * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Supply Frozen Mtrl Item W_Fix Range]}) on column;

    - df_in_SupplyFrozenFixRange_L5 : Select ([Version].[Version Name] * &CurrentWeek *  [Item Material].[MSL5]) on row, ({Measure.[Supply Frozen Mtrl L5 W_Fix Range]}) on column;
    
    - df_in_SupplyFrozenFixRange_L3 : Select ([Version].[Version Name] * &CurrentWeek *  [Item Material].[MSL3]) on row, ({Measure.[Supply Frozen Mtrl L3 W_Fix Range]}) on column;
    
    - df_in_MtrlConstType_Item : Select ([Version].[Version Name] * [Relative Week].[Relative Week] * [Location].[Location] * [Item Material].[Item Material] ) on row, ({Measure.[Mtrl Const Type Item W_Type]}) on column;
    
    - df_in_MtrlConstType_L5 : Select ([Version].[Version Name] * [Relative Week].[Relative Week] * [Item Material].[MSL5] ) on row, ({Measure.[Mtrl Const Type L5 W_Type]}) on column;
    
    - df_in_MtrlConstType_L4 : Select ([Version].[Version Name] * [Relative Week].[Relative Week] * [Item Material].[MSL4] ) on row, ({Measure.[Mtrl Const Type L4 W_Type]}) on column;
    
    - df_in_MtrlConstType_L3 : Select ([Version].[Version Name] * [Relative Week].[Relative Week] * [Item Material].[MSL3] ) on row, ({Measure.[Mtrl Const Type L3 W_Type]}) on column;
    
    - df_in_ItemMaterial : [Item Material] 의 [MSL3], [MSL4], [MSL5] 정보를 얻기 위해 추가
                          Select ([Item Material].[Item Material] * [Item Material].[MSL3] * [Item Material].[MSL4] * [Item Material].[MSL5]);
    
    - df_in_CurrentWeek : CurrentWeek 정보를 얻기 위해 추가
                          Select (&CurrentWeek);
    - df_in_MDMHorizon : 당주 ~ 34주 구간의 주차를 채우기 위해 추가 : 2025.09.16 추가
                         Select (&MDMHorizon);
* Output Tables
    - df_out_AllocPur : MG :  Alloc Pur
                       Select ([Version].[Version Name] * [Time].[Week] * [Location].[Location] * [Item Material].[Item Material] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]) on row, 
                       ({Measure.[Alloc Pur_EOHWEEK_Deno], Measure.[Alloc Pur_EOHWEEK_Numr], Measure.[Alloc Pur_Exception], Measure.[Alloc Pur_NOH], 
                       Measure.[Alloc Pur_REQ Total], Measure.[Alloc Pur_SOP Fix], Measure.[Alloc Pur_SOP unFix], Measure.[Alloc Pur_Service], 
                       Measure.[Alloc Pur_Short], Measure.[Alloc Pur_ToPlant], Measure.[Alloc Pur_ETD Plan], Measure.[Alloc Pur_ETD Plan Flag], 
                       Measure.[Alloc Pur_ETD Plan LT],Measure.[Alloc Pur_EOHWEEK], Measure.[Alloc Pur_ETA Plan], Measure.[Alloc Pur_ETA Result], 
                       Measure.[Alloc Pur_ONHAND], Measure.[Alloc Pur_Open PO], Measure.[Alloc Pur_Safety Time]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_UI_AllocPur] for measures {[Alloc Pur_SOP Fix]} using scope (&MPV) 
     using arguments {("IncludeNullRows", "False"), (paramOutVersion, "CWV_MP"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_AllocPur'
is_local = common.gfn_get_isLocal()


# 공통 Liblary 버전
COMMON_SOURCE_VERSION = common.G_SourceVersion
VD_SOURCE_VERSION = vdCommon.G_VD_SourceVersion

# input variable 확인
paramOutVersion = (
    "CWV_MP"
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
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)

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


########################################################################################################################
# logic start
########################################################################################################################
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
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    step('=====>STEP 0-1 DataFrame Column : 변수 처리')
    
    # 컬럼 변수 선언
    col_VersionVersionName         = 'Version.[Version Name]'
    col_ItemItem                   = 'Item.[Item]'
    col_LocationLocation           = 'Location.[Location]'
    col_SubLocationSubLocation     = 'Sub Location.[Sub Location]'
    col_BOMInfoBOMID               = 'BOM Info.[BOM ID]'
    col_TimeWeek                   = 'Time.[Week]'
    col_ItemMaterialItemMaterial   = 'Item Material.[Item Material]'
    col_TransModeTransMode         = 'Trans Mode.[Trans Mode]'
    col_MarketingNameMarketingName = 'Marketing Name.[Marketing Name]'
    
    col_fromTimeWeek              = 'from.[Time].[Week]'
    col_fromLocationLocation      = 'from.[Location].[Location]'
    col_fromActivity1FromLocation = 'from.[Activity1].[From Location]'
    col_fromActivity2Activity2    = 'from.[Activity2].[Activity2]'
    col_fromItemItem              = 'from.[Item].[Item]'
    
    col_toActivity1Activity1   = 'to.[Activity1].[Activity1]'
    col_toLocationLocation     = 'to.[Location].[Location]'
    col_toToLocationToLocation = 'to.[To Location].[To Location]'
    col_toTimeWeek             = 'to.[Time].[Week]'
    col_toToTimeToWeek         = 'to.[To Time].[To Week]'
    #---------
    col_RelativeWeek           = 'Relative Week.[Relative Week]'
    col_ItemMaterialMSL5       = 'Item Material.[MSL5]'
    col_ItemMaterialMSL4       = 'Item Material.[MSL4]'
    col_ItemMaterialMSL3       = 'Item Material.[MSL3]'
    
    col_BOMMaster_Status   = 'BOM Master_Status'
    #col_WOnHandQuantity    = 'W OnHand Quantity'
    col_BODItem_BODLT      = 'BOD Item_BOD LT'
    #col_BODItemMtrlFull_LT = 'BOD Item Mtrl Full_LT'
    col_SOPBUPProducertoProducerFromPegged = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Producer From Pegged]'
    col_SOPBUPConsumertoProducerFromPegged = 'SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]'
    col_WMaterialRootCauseQuantity         = '002.005W Solver Outputs Material Root Cause.[W Material Root Cause Quantity]'
    
    col_AllocPur_SOPFix      = 'Alloc Pur_SOP Fix'
    col_AllocPur_SOPunFix    = 'Alloc Pur_SOP unFix'
    col_AllocPur_ToPlant     = 'Alloc Pur_ToPlant'
    col_AllocPur_NOH         = 'Alloc Pur_NOH'
    col_AllocPur_Short       = 'Alloc Pur_Short'
    col_AllocPur_ETDPlan     = 'Alloc Pur_ETD Plan'
    col_AllocPur_ETDPlanFlag = 'Alloc Pur_ETD Plan Flag'
    col_AllocPur_ETDPlanLT   = 'Alloc Pur_ETD Plan LT'
    col_AllocPur_ETAResult   = 'Alloc Pur_ETA Result'
    col_AllocPur_ONHAND      = 'Alloc Pur_ONHAND'
    col_AllocPur_OpenPO      = 'Alloc Pur_Open PO'
    
    col_ItemW_FixRange = 'Supply Frozen Mtrl Item W_Fix Range'
    col_L5W_FixRange   = 'Supply Frozen Mtrl L5 W_Fix Range'
    col_L3W_FixRange   = 'Supply Frozen Mtrl L3 W_Fix Range'
    
    col_ItemW_Type    = 'Mtrl Const Type Item W_Type'
    col_L5W_Type      = 'Mtrl Const Type L5 W_Type'
    col_L4W_Type      = 'Mtrl Const Type L4 W_Type'
    col_L3W_Type      = 'Mtrl Const Type L3 W_Type'
    
    # 칼럼 List 설정
    col_list_GRAIN = [col_VersionVersionName, col_TimeWeek, col_LocationLocation, col_ItemMaterialItemMaterial, 
                      col_SubLocationSubLocation, col_TransModeTransMode] #, col_MarketingNameMarketingName]
    
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    step('=====> STEP 0-2 : Input table load')
    
    # Value 변수 선언
    #paramOutVersion_VALUE = "CWV_MP"
    
    # 데이터 파일 읽기
    if is_local:
        # 로컬일 경우 버전 처리
        #paramOutVersion = paramOutVersion_VALUE
        
        df_in_C2P       = read_csv_file("df_in_C2P")
        df_in_P2P       = read_csv_file("df_in_P2P")
        df_in_BSHUB     = read_csv_file("df_in_BSHUB")
        df_in_OnHand    = read_csv_file("df_in_OnHand")
        df_in_LT        = read_csv_file("df_in_LT")
        df_in_ER        = read_csv_file("df_in_ER")
        df_in_Short     = read_csv_file("df_in_Short")
        df_in_OPO       = read_csv_file("df_in_OPO")
        df_in_NOH       = read_csv_file("df_in_NOH")
        df_in_BOMMaster = read_csv_file("df_in_BOMMaster")
        df_in_Horizon   = read_csv_file("df_in_Horizon")
        #----------------------------------------------
        df_in_SupplyFrozenFixRange_Item = read_csv_file("df_in_SupplyFrozenFixRange_Item")
        df_in_SupplyFrozenFixRange_L5 = read_csv_file("df_in_SupplyFrozenFixRange_L5")
        df_in_SupplyFrozenFixRange_L3 = read_csv_file("df_in_SupplyFrozenFixRange_L3")
        df_in_MtrlConstType_Item = read_csv_file("df_in_MtrlConstType_Item")
        df_in_MtrlConstType_L5 = read_csv_file("df_in_MtrlConstType_L5")
        df_in_MtrlConstType_L4 = read_csv_file("df_in_MtrlConstType_L4")
        df_in_MtrlConstType_L3 = read_csv_file("df_in_MtrlConstType_L3")
        df_in_ItemMaterial = read_csv_file("df_in_ItemMaterial")
        df_in_CurrentWeek = read_csv_file("df_in_CurrentWeek")
        df_in_MDMHorizon = read_csv_file("df_in_MDMHorizon")
    
    # 입력 변수 확인
    #if paramOutVersion is None or paramOutVersion.strip() == '':
    #    paramOutVersion = paramOutVersion_VALUE
    
    # input dataframe 확인용 로그
    #note(f'=====> paramOutVersion : {paramOutVersion}')
    
    print_df(df_in_C2P, 'df_in_C2P', False)
    print_df(df_in_P2P, 'df_in_P2P', False)
    print_df(df_in_BSHUB, 'df_in_BSHUB', False)
    print_df(df_in_OnHand, 'df_in_OnHand', False)
    print_df(df_in_LT, 'df_in_LT', False)
    print_df(df_in_ER, 'df_in_ER', False)
    print_df(df_in_Short, 'df_in_Short', False)
    print_df(df_in_OPO, 'df_in_OPO', False)
    print_df(df_in_NOH, 'df_in_NOH', False)
    print_df(df_in_BOMMaster, 'df_in_BOMMaster', False)
    print_df(df_in_Horizon, 'df_in_Horizon', False)
    # ----------------------------------------------
    print_df(df_in_SupplyFrozenFixRange_Item, 'df_in_SupplyFrozenFixRange_Item', False)
    print_df(df_in_SupplyFrozenFixRange_L5, 'df_in_SupplyFrozenFixRange_L5', False)
    print_df(df_in_SupplyFrozenFixRange_L3, 'df_in_SupplyFrozenFixRange_L3', False)
    print_df(df_in_MtrlConstType_Item, 'df_in_MtrlConstType_Item', False)
    print_df(df_in_MtrlConstType_L5, 'df_in_MtrlConstType_L5', False)
    print_df(df_in_MtrlConstType_L4, 'df_in_MtrlConstType_L4', False)
    print_df(df_in_MtrlConstType_L3, 'df_in_MtrlConstType_L3', False)
    print_df(df_in_ItemMaterial, 'df_in_ItemMaterial', False)
    print_df(df_in_CurrentWeek, 'df_in_CurrentWeek', False)
    print_df(df_in_MDMHorizon, 'df_in_MDMHorizon', False)
    
    # DATA TYPE 설정    
    df_in_C2P = df_in_C2P.astype({col_fromTimeWeek: 'str', col_toTimeWeek: 'str', col_toToTimeToWeek: 'str'}, copy=True)
    print_df(df_in_C2P, 'df_in_C2P-2', False)
    
    df_in_P2P = df_in_P2P.astype({col_fromTimeWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    print_df(df_in_P2P, 'df_in_P2P-2', False)
    
    df_in_BSHUB = df_in_BSHUB.astype({col_fromTimeWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    print_df(df_in_BSHUB, 'df_in_BSHUB-2', False)
    
    df_in_OnHand = df_in_OnHand.astype({col_fromTimeWeek: 'str'}, copy=True)
    print_df(df_in_OnHand, 'df_in_OnHand-2', False)
    
    df_in_ER = df_in_ER.astype({col_toToTimeToWeek: 'str'}, copy=True)
    print_df(df_in_ER, 'df_in_ER-2', False)
    
    df_in_Short = df_in_Short.astype({col_fromTimeWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    print_df(df_in_Short, 'df_in_Short-2', False)
    
    df_in_OPO = df_in_OPO.astype({col_toToTimeToWeek: 'str'}, copy=True)
    print_df(df_in_OPO, 'df_in_OPO-2', False)
    
    df_in_NOH = df_in_NOH.astype({col_fromTimeWeek: 'str', col_toTimeWeek: 'str'}, copy=True)
    print_df(df_in_NOH, 'df_in_NOH-2', False)
    
    df_in_Horizon = df_in_Horizon.astype({col_TimeWeek: 'str'}, copy=True)    
    print_df(df_in_Horizon, 'df_in_Horizon-2', False)
    
    df_in_CurrentWeek = df_in_CurrentWeek[[col_TimeWeek]]
    
    df_in_MDMHorizon = df_in_MDMHorizon[[col_TimeWeek]]
    df_in_MDMHorizon = df_in_MDMHorizon.astype({col_TimeWeek: 'str'}, copy=True)
    
    step('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 1 : Alloc Pur_SOP Fix, Alloc Pur_SOP unFix 생성
    ################################################################################################################
    step('=====> STEP 1-1 : Alloc Pur_SOP Fix, Alloc Pur_SOP unFix Create')
    df_BOMMaster = df_in_BOMMaster[[col_VersionVersionName, col_BOMInfoBOMID, col_BOMMaster_Status]].copy()
    df_BOMMaster.drop_duplicates(inplace=True)
    del df_in_BOMMaster
    print_df(df_BOMMaster, 'df_BOMMaster', False)
    
    # Merge : df_in_P2P & df_in_BOMMaster
    df_P2P_BOMMaster = df_in_P2P.merge(df_BOMMaster, left_on=[col_VersionVersionName, col_toActivity1Activity1],
                                                     right_on=[col_VersionVersionName, col_BOMInfoBOMID], how='inner')
    del df_BOMMaster
    #df_P2P_BOMMaster.drop(columns=[col_LocationLocation], inplace=True)
    df_P2P_BOMMaster.rename(columns={col_fromTimeWeek: col_TimeWeek, col_fromLocationLocation: col_LocationLocation,
                                     col_fromItemItem: col_ItemMaterialItemMaterial}, inplace=True)
    df_P2P_BOMMaster[col_SubLocationSubLocation]     = '-'
    df_P2P_BOMMaster[col_TransModeTransMode]         = '-'
    #df_P2P_BOMMaster[col_MarketingNameMarketingName] = '-'
    
    df_P2P_BOMMaster[col_AllocPur_SOPFix]   = df_P2P_BOMMaster[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_P2P_BOMMaster[col_AllocPur_SOPunFix] = df_P2P_BOMMaster[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    print_df(df_P2P_BOMMaster, 'df_P2P_BOMMaster', False)
    
    # Alloc Pur_SOP Fix
    df_SOPFix = df_P2P_BOMMaster[df_P2P_BOMMaster[col_BOMMaster_Status] == 'Fixed']
    df_SOPFix = df_SOPFix.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_SOPFix].sum()
    print_df(df_SOPFix, 'df_SOPFix', False)
    
    # Alloc Pur_SOP unFix
    df_SOPunFix = df_P2P_BOMMaster[df_P2P_BOMMaster[col_BOMMaster_Status] != 'Fixed']
    df_SOPunFix = df_SOPunFix.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_SOPunFix].sum()
    print_df(df_SOPunFix, 'df_SOPunFix', False)
    
    del df_P2P_BOMMaster
    
    step('=====> STEP 1-2 : Alloc Pur_SOP Fix, Alloc Pur_SOP unFix Create End')
    
    ################################################################################################################
    # STEP 2 :  Alloc Pur_ToPlant 생성
    ################################################################################################################
    step('=====> STEP 2-1 : Alloc Pur_ToPlant Create')
    
    #Substr(FROM.[Location].[Location], 1, 4) != TO.[Location].[Location]
    df_ToPlant_P2P = df_in_P2P[df_in_P2P[col_fromLocationLocation].str.slice(0, 4) != df_in_P2P[col_toLocationLocation]].copy()
    del df_in_P2P
    
    df_ToPlant_P2P.rename(columns={col_fromTimeWeek: col_TimeWeek, col_fromLocationLocation: col_LocationLocation,
                                   col_fromItemItem: col_ItemMaterialItemMaterial}, inplace=True)
    df_ToPlant_P2P[col_SubLocationSubLocation] = '-'
    df_ToPlant_P2P[col_TransModeTransMode] = '-'
    #df_ToPlant_P2P[col_MarketingNameMarketingName] = '-'
    df_ToPlant_P2P[col_AllocPur_ToPlant] = df_ToPlant_P2P[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    print_df(df_ToPlant_P2P, 'df_ToPlant_P2P org', False)
    df_ToPlant_P2P = df_ToPlant_P2P.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_ToPlant].sum()
    
    print_df(df_ToPlant_P2P, 'df_ToPlant_P2P', False)
    
    df_ToPlant_BSHUB = df_in_BSHUB.copy()
    del df_in_BSHUB
    
    df_ToPlant_BSHUB.rename(columns={col_fromTimeWeek: col_TimeWeek, col_fromLocationLocation: col_LocationLocation,
                                     col_fromItemItem: col_ItemMaterialItemMaterial}, inplace=True)
    df_ToPlant_BSHUB[col_SubLocationSubLocation] = '-'
    df_ToPlant_BSHUB[col_TransModeTransMode] = '-'
    #df_ToPlant_BSHUB[col_MarketingNameMarketingName] = '-'
    df_ToPlant_BSHUB[col_AllocPur_ToPlant] = df_ToPlant_BSHUB[col_SOPBUPConsumertoProducerFromPegged].fillna(0).astype('int64')
    df_ToPlant_BSHUB = df_ToPlant_BSHUB.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_ToPlant].sum()
    
    print_df(df_ToPlant_BSHUB, 'df_ToPlant_BSHUB', False)
    
    df_ToPlant = pd.concat([df_ToPlant_P2P, df_ToPlant_BSHUB])
    del [df_ToPlant_P2P, df_ToPlant_BSHUB]
    print_df(df_ToPlant, 'df_ToPlant', False)
    step('=====> STEP 2-2 : Alloc Pur_ToPlant Create End')
    
    ################################################################################################################
    # STEP 3 :  Alloc Pur_NOH 생성
    ################################################################################################################
    step('=====> STEP 3-1 : Alloc Pur_NOH Create')
    
    df_NOH = df_in_NOH.copy()
    del df_in_NOH;
    
    df_NOH.rename(columns={col_fromTimeWeek: col_TimeWeek, col_fromLocationLocation: col_LocationLocation,
                                     col_fromItemItem: col_ItemMaterialItemMaterial}, inplace=True)
    df_NOH[col_SubLocationSubLocation] = '-'
    df_NOH[col_TransModeTransMode] = '-'
    #df_NOH[col_MarketingNameMarketingName] = '-'
    df_NOH[col_AllocPur_NOH] = df_NOH[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_NOH = df_NOH.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_NOH].sum()
    
    print_df(df_NOH, 'df_NOH', False)
    
    step('=====> STEP 3-2 : Alloc Pur_NOH Create End')
    
    ################################################################################################################
    # STEP 4 :  Alloc Pur_Short 생성
    ################################################################################################################
    step('=====> STEP 4-1 : Alloc Pur_Short Create')
    df_Short = df_in_Short.copy()
    del df_in_Short
    
    df_Short.rename(columns={col_fromTimeWeek: col_TimeWeek, col_fromLocationLocation: col_LocationLocation,
                             col_fromItemItem: col_ItemMaterialItemMaterial}, inplace=True)
    df_Short[col_SubLocationSubLocation] = '-'
    df_Short[col_TransModeTransMode] = '-'
    #df_Short[col_MarketingNameMarketingName] = '-'
    df_Short[col_AllocPur_Short] = df_Short[col_WMaterialRootCauseQuantity].fillna(0).astype('int64')
    df_Short = df_Short.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_Short].sum()
    
    print_df(df_Short, 'df_Short', False)
    
    step('=====> STEP 4-2 : Alloc Pur_Short Create End')
    
    ################################################################################################################
    # STEP 5 :  Alloc Pur ETD_ETD Plan & Alloc Pur Dtl_ETA Result 생성
    ################################################################################################################
    step('=====> STEP 5-1 : Alloc Pur ETD_ETD Plan Create')
    
    df_ETDPlan = df_in_C2P.copy() 
    del df_in_C2P
    #df_ETDPlan.rename(columns={col_fromTimeWeek: col_TimeWeek, col_toLocationLocation: col_LocationLocation,
    # col_toLocationLocation : col_toToLocationToLocation 로 변경(2025.03.05)
    df_ETDPlan.rename(columns={col_fromTimeWeek: col_TimeWeek, col_toToLocationToLocation: col_LocationLocation,
                               col_fromItemItem: col_ItemMaterialItemMaterial, 
                               col_fromLocationLocation: col_SubLocationSubLocation,
                               col_fromActivity2Activity2: col_TransModeTransMode
                               }, inplace=True)
    df_ETDPlan[col_AllocPur_ETDPlan] = df_ETDPlan[col_SOPBUPConsumertoProducerFromPegged].fillna(0).astype('int64')
    #df_ETDPlan[col_MarketingNameMarketingName] = '-'
    df_ETDPlan = df_ETDPlan.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_ETDPlan].sum()
    
    print_df(df_ETDPlan, 'df_ETDPlan', False)
    step('=====> STEP 5-2 :Alloc Pur ETD_ETD Plan Create End')
    
    #---------------------------------------------------------------------------------------
    step('=====> STEP 5-3 : Alloc Pur Dtl_ETA Result Create')
    
    df_ETAResult = df_in_ER.copy() #df_in_ER 로 변경(2025.03.10)
    del df_in_ER
    df_ETAResult.rename(columns={col_toToTimeToWeek: col_TimeWeek, col_toToLocationToLocation: col_LocationLocation,
                                 col_fromItemItem: col_ItemMaterialItemMaterial
                                 }, inplace=True)
    df_ETAResult[col_SubLocationSubLocation] = '+'
    df_ETAResult[col_TransModeTransMode] = '+'
    df_ETAResult[col_AllocPur_ETAResult] = df_ETAResult[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    #df_ETAResult[col_MarketingNameMarketingName] = '-'
    df_ETAResult = df_ETAResult.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_ETAResult].sum()
    
    print_df(df_ETAResult, 'df_ETAResult', False)
    
    step('=====> STEP 5-4 : Alloc Pur Dtl_ETA Result Create End')
    
    ################################################################################################################
    # STEP 6 :  Alloc Pur Dtl_ONHAND 생성
    ################################################################################################################
    step('=====> STEP 6-1 : Alloc Pur Dtl_ONHAND Create')
    
    df_ONHAND = df_in_OnHand.copy()
    del df_in_OnHand
    
    df_ONHAND.rename(columns={col_fromTimeWeek: col_TimeWeek, col_toToLocationToLocation: col_LocationLocation,
                              col_fromItemItem: col_ItemMaterialItemMaterial}, inplace=True)
    df_ONHAND[col_SubLocationSubLocation] = '+'
    df_ONHAND[col_TransModeTransMode] = '+'
    #df_ONHAND[col_MarketingNameMarketingName] = '-'
    df_ONHAND[col_AllocPur_ONHAND] = df_ONHAND[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    df_ONHAND = df_ONHAND.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_ONHAND].sum()
    
    print_df(df_ONHAND, 'df_ONHAND', False)
    
    step('=====> STEP 6-2 : Alloc Pur Dtl_ONHAND Create End')
    
    ################################################################################################################
    # STEP 7 :  Alloc Pur Dtl_Open PO 생성
    ################################################################################################################
    step('=====> STEP 7-1 : Alloc Pur Dtl_Open PO Create')
    
    df_OpenPO = df_in_OPO.copy()
    del df_in_OPO
    
    df_OpenPO.rename(columns={col_toToTimeToWeek: col_TimeWeek, col_toToLocationToLocation: col_LocationLocation,
                                 col_fromItemItem: col_ItemMaterialItemMaterial
                                 }, inplace=True)
    df_OpenPO[col_SubLocationSubLocation] = '+'
    df_OpenPO[col_TransModeTransMode] = '+'
    df_OpenPO[col_AllocPur_OpenPO] = df_OpenPO[col_SOPBUPProducertoProducerFromPegged].fillna(0).astype('int64')
    #df_OpenPO[col_MarketingNameMarketingName] = '-'
    df_OpenPO = df_OpenPO.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_OpenPO].sum()
    
    print_df(df_OpenPO, 'df_OpenPO', False)
    
    step('=====> STEP 7-2 : Alloc Pur Dtl_Open PO Create End')
    
    ################################################################################################################
    # STEP 8 :  Alloc Pur ETD_ETD Plan LT 생성
    ################################################################################################################
    step('=====> STEP 8-1 : Alloc Pur ETD_ETD Plan LT Create')

    df_ETDPlanLT = df_in_LT.copy()
    del df_in_LT
    
    df_ETDPlanLT.rename(columns={col_ItemItem: col_ItemMaterialItemMaterial}, inplace=True) #수정(2025.03.06)
    # Location <==> SubLocation 치환 : 수정(2025.03.06)
    df_ETDPlanLT['Location_ORG'] = df_ETDPlanLT[col_LocationLocation]
    df_ETDPlanLT['SubLocation_ORG'] = df_ETDPlanLT[col_SubLocationSubLocation]    
    df_ETDPlanLT[col_LocationLocation]       = df_ETDPlanLT['SubLocation_ORG']
    df_ETDPlanLT[col_SubLocationSubLocation] = df_ETDPlanLT['Location_ORG']
    
    col_list_Exists = [col_LocationLocation, col_ItemMaterialItemMaterial, col_SubLocationSubLocation, col_TransModeTransMode]
    
    print_df(df_ETDPlanLT, 'df_ETDPlanLT ORG', False)
    
    #[Location].[Location]	[Item Material].[Item Material]	[Sub Location].[Sub Location]	[Trans Mode].[Trans Mode]
    #위 칼럼 기준으로 df_ETDPlan 에 있는것만 대상으로 추출
    df_ETDPlanLT = df_ETDPlanLT[df_ETDPlanLT.set_index(col_list_Exists).index.isin(    
                                df_ETDPlan.set_index(col_list_Exists).index)].copy()
    df_ETDPlanLT[col_AllocPur_ETDPlanLT] = df_ETDPlanLT[col_BODItem_BODLT].fillna(0).astype('int64')
    
    df_ETDPlanLT = df_ETDPlanLT.merge(df_in_Horizon, how='cross')
    del df_in_Horizon
    
    #df_ETDPlanLT[col_MarketingNameMarketingName] = '-'
    df_ETDPlanLT = df_ETDPlanLT.groupby(col_list_GRAIN, as_index=False)[col_AllocPur_ETDPlanLT].sum()
        
    print_df(df_ETDPlanLT, 'df_ETDPlanLT', False)
    
    step('=====> STEP 8-2 : Alloc Pur ETD_ETD Plan LT Create End')
    
    ################################################################################################################
    # STEP 9 : output table create
    ################################################################################################################
    step('=====> STEP 5-1 : Final output table create')
    
    df_AllocPur = df_SOPFix.copy()
    df_AllocPur = df_AllocPur.merge(df_SOPunFix, on=col_list_GRAIN, how='outer')
    df_AllocPur = df_AllocPur.merge(df_ToPlant, on=col_list_GRAIN, how='outer')
    df_AllocPur = df_AllocPur.merge(df_NOH, on=col_list_GRAIN, how='outer')
    df_AllocPur = df_AllocPur.merge(df_Short, on=col_list_GRAIN, how='outer')
    
    df_AllocPur = df_AllocPur.merge(df_ETDPlan, on=col_list_GRAIN, how='outer')
    df_AllocPur = df_AllocPur.merge(df_ETDPlanLT, on=col_list_GRAIN, how='outer')
    
    df_AllocPur = df_AllocPur.merge(df_ETAResult, on=col_list_GRAIN, how='outer')
    df_AllocPur = df_AllocPur.merge(df_ONHAND, on=col_list_GRAIN, how='outer')
    df_AllocPur = df_AllocPur.merge(df_OpenPO, on=col_list_GRAIN, how='outer')
    
    del [df_SOPFix, df_SOPunFix, df_ToPlant, df_NOH, df_Short, df_ETDPlan, 
         df_ETAResult, df_ONHAND, df_OpenPO, df_ETDPlanLT]
    
    # DISTINCT  ( Version.[Version Name]		Location.[Location]  Sub Location.[Sub Location]	 Item Material.[Item Material]	Trans Mode.[Trans Mode] )  
    df_AllocPur_dist = df_AllocPur[[col_VersionVersionName, col_LocationLocation, col_SubLocationSubLocation,
                                    col_ItemMaterialItemMaterial, col_TransModeTransMode]].copy()
    df_AllocPur_dist.drop_duplicates(inplace=True)
    
    # Merge df_AllocPur & df_in_MDMHorizon : 당주 ~ 34주 구간의 주차를 채우기 위해 Merge
    df_AllocPur_week = df_AllocPur_dist.merge(df_in_MDMHorizon, how='cross')
    print_df(df_AllocPur_week, 'df_AllocPur_week', False)
    
    # 당주 ~ 34주 구간의 주차를 채운 df_AllocPur_week 와  df_AllocPur outer Merge 
    df_AllocPur = df_AllocPur_week.merge(df_AllocPur, on=col_list_GRAIN, how='outer')
    del [df_in_MDMHorizon, df_AllocPur_week]
    
    #칼럼정리
    col_list_Pur = [col_VersionVersionName, col_TimeWeek, col_LocationLocation, col_ItemMaterialItemMaterial,
                    col_SubLocationSubLocation, col_TransModeTransMode, #col_MarketingNameMarketingName,
                    col_AllocPur_SOPFix, col_AllocPur_SOPunFix, col_AllocPur_ToPlant,col_AllocPur_NOH, col_AllocPur_Short,
                    col_AllocPur_ETDPlan, col_AllocPur_ETDPlanLT,
                    col_AllocPur_ETAResult, col_AllocPur_ONHAND, col_AllocPur_OpenPO
                    ]
    
    df_AllocPur    = df_AllocPur[col_list_Pur]
    print_df(df_AllocPur, 'df_AllocPur 1', False)
    
    #==================================================================================================================
    # [Alloc Pur_ETD Plan Flag] 구하기 : 2025.09.08 추가
    # ==================================================================================================================
    step('=====> STEP 5-2 : [Alloc Pur_ETD Plan Flag] create')
    
    # Merge df_in_ItemMaterial :  Item Material.[MSL3]  Item Material.[MSL4]	Item Material.[MSL5]
    df_AllocPur_dist = df_AllocPur_dist.merge(df_in_ItemMaterial, on=[col_ItemMaterialItemMaterial], how='inner')
    
    # ===============================================================================================================    
    # Merge df_in_SupplyFrozenFixRange_Item
    cList_Merge = [col_VersionVersionName, col_LocationLocation, col_ItemMaterialItemMaterial]
    df_AllocPur_FIX = df_AllocPur_dist.merge(df_in_SupplyFrozenFixRange_Item, on=cList_Merge, how='left')
    del [df_AllocPur_dist, df_in_SupplyFrozenFixRange_Item]
    
    # Merge df_in_SupplyFrozenFixRange_L5
    cList_Merge = [col_VersionVersionName, col_ItemMaterialMSL5]
    df_AllocPur_FIX = df_AllocPur_FIX.merge(df_in_SupplyFrozenFixRange_L5, on=cList_Merge, how='left', suffixes=('', '_L5'))
    del df_in_SupplyFrozenFixRange_L5
    
    # Merge df_in_SupplyFrozenFixRange_L3
    cList_Merge = [col_VersionVersionName, col_ItemMaterialMSL3]
    df_AllocPur_FIX = df_AllocPur_FIX.merge(df_in_SupplyFrozenFixRange_L3, on=cList_Merge, how='left', suffixes=('', '_L3'))
    del df_in_SupplyFrozenFixRange_L3
    
    # Range 취합 : Item range 가 null 이면  L5 range, L5 range도 null 이면  L3 range
    df_AllocPur_FIX['range'] = np.select(
        [df_AllocPur_FIX[col_ItemW_FixRange].notna(),
         df_AllocPur_FIX[col_L5W_FixRange].notna(),
         True
         ],
        [df_AllocPur_FIX[col_ItemW_FixRange],
         df_AllocPur_FIX[col_L5W_FixRange],
         df_AllocPur_FIX[col_L3W_FixRange]
         ]
    )
    
    df_AllocPur_FIX[col_TimeWeek] = np.select(
        [df_AllocPur_FIX[col_TimeWeek].notna(),
         df_AllocPur_FIX[col_TimeWeek+'_L5'].notna(),
         True
         ],
        [df_AllocPur_FIX[col_TimeWeek],
         df_AllocPur_FIX[col_TimeWeek+'_L5'],
         df_AllocPur_FIX[col_TimeWeek+'_L3']
         ]
    )
    df_AllocPur_FIX = df_AllocPur_FIX[df_AllocPur_FIX['range'].notna()]
    df_AllocPur_FIX = df_AllocPur_FIX.astype({'range': 'int64', col_TimeWeek: 'int64'}, copy=True)
    df_AllocPur_FIX[col_AllocPur_ETDPlanFlag] = 'Mfg Frozen'
    
    # 칼럼정리 
    df_AllocPur_FIX = df_AllocPur_FIX[[col_VersionVersionName, col_TimeWeek, col_LocationLocation, col_SubLocationSubLocation,
                                       col_ItemMaterialItemMaterial, col_TransModeTransMode, col_AllocPur_ETDPlanFlag, 'range']].copy()
    
    # range만큼 반복
    df_AllocPur_FIX = df_AllocPur_FIX.loc[df_AllocPur_FIX.index.repeat(df_AllocPur_FIX['range'])].copy()
    df_AllocPur_FIX['offset'] = df_AllocPur_FIX.groupby(level=0).cumcount()
    
    df_AllocPur_FIX = df_AllocPur_FIX.astype({col_TimeWeek: 'str'}, copy=True)
    df_AllocPur_FIX[col_TimeWeek] = df_AllocPur_FIX.apply(lambda x: common.gfn_add_week(x[col_TimeWeek], x['offset']), axis=1)
    
    df_AllocPur_FIX.drop(columns=['range', 'offset'], inplace=True)
    print_df(df_AllocPur_FIX, 'df_AllocPur_FIX', False)
    
    # df_AllocPur, df_AllocPur_FIX 취합
    df_AllocPur = df_AllocPur.merge(df_AllocPur_FIX, on=col_list_GRAIN, how='left')
    del df_AllocPur_FIX
    print_df(df_AllocPur, 'df_AllocPur 2', False)
    
    #===============================================================================================================
    # Merge df_AllocPur & df_in_ItemMaterial
    df_AllocPur_EPF = df_AllocPur.merge(df_in_ItemMaterial, on=[col_ItemMaterialItemMaterial], how='inner')
    del [df_AllocPur, df_in_ItemMaterial]
    
    #---------------
    # Merge df_in_MtrlConstType_Item & df_in_CurrentWeek
    df_CTYPE_Item = df_in_MtrlConstType_Item.merge(df_in_CurrentWeek, how='cross')
    df_CTYPE_Item = df_CTYPE_Item.astype({col_TimeWeek: 'str'}, copy=True)
    del df_in_MtrlConstType_Item
    
    # Item : Relative Week.[Relative Week] 처리
    df_CTYPE_Item['offset'] = (df_CTYPE_Item[col_RelativeWeek].str.replace('W', '').astype('int64') - 1)
    if df_CTYPE_Item.empty :
        None
    else :
        df_CTYPE_Item[col_TimeWeek] = df_CTYPE_Item.apply(lambda x: common.gfn_add_week(x[col_TimeWeek],
                                                                                        x['offset']), axis=1)
    #print_df(df_CTYPE_Item, 'df_CTYPE_Item', False)
    
    # ---------------
    # Merge df_in_MtrlConstType_L5 & df_in_CurrentWeek
    df_CTYPE_L5 = df_in_MtrlConstType_L5.merge(df_in_CurrentWeek, how='cross')
    df_CTYPE_L5 = df_CTYPE_L5.astype({col_TimeWeek: 'str'}, copy=True)
    del df_in_MtrlConstType_L5
    
    # L5 : Relative Week.[Relative Week] 처리
    df_CTYPE_L5['offset'] = (df_CTYPE_L5[col_RelativeWeek].str.replace('W', '').astype('int64') - 1)    
    if df_CTYPE_L5.empty :
        None
    else :
        df_CTYPE_L5[col_TimeWeek] = df_CTYPE_L5.apply(lambda x: common.gfn_add_week(x[col_TimeWeek], x['offset']), axis=1)
    
    #print_df(df_CTYPE_L5, 'df_CTYPE_L5', False)
    
    # ---------------
    # Merge df_in_MtrlConstType_L4 & df_in_CurrentWeek
    df_CTYPE_L4 = df_in_MtrlConstType_L4.merge(df_in_CurrentWeek, how='cross')
    df_CTYPE_L4 = df_CTYPE_L4.astype({col_TimeWeek: 'str'}, copy=True)
    del df_in_MtrlConstType_L4
    
    # L4 : Relative Week.[Relative Week] 처리
    df_CTYPE_L4['offset'] = (df_CTYPE_L4[col_RelativeWeek].str.replace('W', '').astype('int64') - 1)    
    if df_CTYPE_L4.empty :
        None
    else :
        df_CTYPE_L4[col_TimeWeek] = df_CTYPE_L4.apply(lambda x: common.gfn_add_week(x[col_TimeWeek], x['offset']), axis=1)
    
    #print_df(df_CTYPE_L4, 'df_CTYPE_L4', False)
    
    # ---------------
    # Merge df_in_MtrlConstType_L3 & df_in_CurrentWeek
    df_CTYPE_L3 = df_in_MtrlConstType_L3.merge(df_in_CurrentWeek, how='cross')
    df_CTYPE_L3 = df_CTYPE_L3.astype({col_TimeWeek: 'str'}, copy=True)
    del df_in_MtrlConstType_L3
    
    # L3 : Relative Week.[Relative Week] 처리
    df_CTYPE_L3['offset'] = (df_CTYPE_L3[col_RelativeWeek].str.replace('W', '').astype('int64') - 1)    
    if df_CTYPE_L3.empty :
        None
    else :
        df_CTYPE_L3[col_TimeWeek] = df_CTYPE_L3.apply(lambda x: common.gfn_add_week(x[col_TimeWeek], x['offset']), axis=1)
    
    print_df(df_CTYPE_L3, 'df_CTYPE_L3', False)
    
    # Merge df_AllocPur_EPF & df_CTYPE_Item
    cList_Merge = [col_VersionVersionName, col_TimeWeek, col_LocationLocation, col_ItemMaterialItemMaterial]
    df_AllocPur_EPF = df_AllocPur_EPF.merge(df_CTYPE_Item, on=cList_Merge, how='left')
    df_AllocPur_EPF.drop(columns=['offset', col_RelativeWeek], inplace=True)
    del df_CTYPE_Item
    
    # Merge df_AllocPur_EPF & df_CTYPE_L5
    cList_Merge = [col_VersionVersionName, col_TimeWeek, col_ItemMaterialMSL5]
    df_AllocPur_EPF = df_AllocPur_EPF.merge(df_CTYPE_L5, on=cList_Merge, how='left')
    df_AllocPur_EPF.drop(columns=['offset', col_RelativeWeek], inplace=True)
    del df_CTYPE_L5
    
    # Merge df_AllocPur_EPF & df_CTYPE_L4
    cList_Merge = [col_VersionVersionName, col_TimeWeek, col_ItemMaterialMSL4]
    df_AllocPur_EPF = df_AllocPur_EPF.merge(df_CTYPE_L4, on=cList_Merge, how='left')
    df_AllocPur_EPF.drop(columns=['offset', col_RelativeWeek], inplace=True)
    del df_CTYPE_L4
    
    # Merge df_AllocPur_EPF & df_CTYPE_L3
    cList_Merge = [col_VersionVersionName, col_TimeWeek, col_ItemMaterialMSL3]
    df_AllocPur_EPF = df_AllocPur_EPF.merge(df_CTYPE_L3, on=cList_Merge, how='left')
    df_AllocPur_EPF.drop(columns=['offset', col_RelativeWeek], inplace=True)
    del df_CTYPE_L3
    
    # W_Type 취합 : Item W_Type 가 null 이면  L5 W_Type, L5 W_Type도 null 이면  L4W_Type, L4 W_Type도 null 이면  L3W_Type
    df_AllocPur_EPF['W_Type'] = np.select(
        [df_AllocPur_EPF[col_ItemW_Type].notna(),
         df_AllocPur_EPF[col_L5W_Type].notna(),
         df_AllocPur_EPF[col_L4W_Type].notna(),
         True
        ],
        [df_AllocPur_EPF[col_ItemW_Type],
         df_AllocPur_EPF[col_L5W_Type],
         df_AllocPur_EPF[col_L4W_Type],
         df_AllocPur_EPF[col_L3W_Type]
        ]
    )
    
    # ETD_ETD Plan Flag 값이 'Mfg Frozen' 인 경우, 그대로 둔다. 
    df_AllocPur_EPF[col_AllocPur_ETDPlanFlag] = np.where(
        (df_AllocPur_EPF[col_AllocPur_ETDPlanFlag].isna() | (df_AllocPur_EPF[col_AllocPur_ETDPlanFlag] != 'Mfg Frozen')),
        df_AllocPur_EPF['W_Type'], df_AllocPur_EPF[col_AllocPur_ETDPlanFlag]
    )
    df_AllocPur_EPF.drop(columns=[col_ItemMaterialMSL3, col_ItemMaterialMSL4, col_ItemMaterialMSL5, col_ItemW_Type,
                                    col_L5W_Type, col_L4W_Type, col_L3W_Type, 'W_Type'], inplace=True)
    print_df(df_AllocPur_EPF, 'df_AllocPur_EPF', False)
    step('=====> STEP 5-3 : [Alloc Pur_ETD Plan Flag] create End')
    # ===============================================================================================================
    
    # out Data 생성 :
    df_out_AllocPur = df_AllocPur_EPF.copy()
    del df_AllocPur_EPF
    
    # 버전 처리
    #df_out_AllocPur[col_VersionVersionName] = paramOutVersion
    
    row_count, col_count = df_out_AllocPur.shape
    note(f'=====> Final df_out_AllocPur rows : {row_count}, column : {col_count}')
    print_df(df_out_AllocPur, 'df_out_AllocPur', False)
        
    if is_local:
        step('=====> Output csv create')
        save_csv_file(df_out_AllocPur, 'df_out_AllocPur')
    
    step('=====> STEP 5-4 : Final output table create End')
    step('==============================================')
    step('==============================================')
    step('==============================================')

except Exception as e:
    step(f'=====> Exception : {traceback.format_exc()}')
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_AllocPur = pd.DataFrame([], columns=[])
    
finally:
    # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
    step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')
    
    df_out_log, df_out_logDetail = vd_log_end()
    logger.Finish()