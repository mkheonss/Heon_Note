"""
* 프로그램명
    - PY_MG_SOPSync

* 내용
    -

* 변경이력
    - 2025.05.05 / 양희영 / Create
    - 2026.01.26 / 양희영 / Update
    - 2026.02.23 / 양희영 / Update

* Flow Summary
    1. Data Scope : select ([Location].[Location]*[Location].[MF Site Stage].[SET]);
                [Item].[Item Stage].[SET]
    2. MG : Lot Size, MfgSOP-SOP 동기화 관련 MG은 한개 입니다.
      - MG : Amend SOP (DEV18에 생성 완료)
        Select ([Version].[Version Name] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,
        ({Measure.[Amend SOP_MfgSOP Qty], Measure.[Amend SOP_SOP Qty]}) on column;
      - Amend SOP_SOP Qty : Lot Size 처리 후 생성 Measure
      - Amend SOP_MfgSOP Qty : 동기화 처리 후 생성 Measure
      - 동기화 처리는 %SCS% 만 적용, 나머지는 그대로 유지
    3. 프로그램 명
      - MfgSOP-SOP : PY_MG_SOPSync

* Execution

* Script Parameter
    -- paramCallSeq : 0   : ( 0~ 4) 프로시처에서 프로그램 호출 순번

* Input Tables
    - df_in_Mfg
      Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Item Stage].[SET] * [Item].[Plan Group] * [Time].[Week] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2].filter(#.Name Startswith "RT_") * [Activity3].[Activity3] ) on row, ({Measure.[W Material Production Quantity Plan Output]}) on column;

      df_in_AmendSOP
      Select ([Version].[Version Name] * [Location].[Location] * [Location].[Site Stage] * [Item].[Item] * [Item].[Item Stage].[SET] * [Item].[Plan Group] * [Time].[Week] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[Amend SOP_SOP Qty]}) on column;

      df_in_ShipmentLT
      Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Mandatory Offset]}) on column;

      df_in_CurrentWeek
      Select (&CurrentWeek);

      df_in_WFrozen
      Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Frozen Window], Measure.[W Frozen Window Apply At]}) on column;

      df_in_WOnHand
      Select ([Version].[Version Name] * [Location].[Location] * [Location].[Site Stage].filter(#.Name StartsWith("MF")) * [Item].[Item] * [Item].[Item Stage].[SET] * [Item].[Plan Group] * [Time].[Week] * [Documents].[OrderlineID] ) on row, ({Measure.[W OnHand Quantity]}) on column;

      df_in_Intransit
      Select ([Version].[Version Name] * [Location].[Location] * [Location].[Site Stage].filter(#.Name StartsWith("MF")) * [Item].[Item] * [Item].[Item Stage].[SET] * [Item].[Plan Group] * [Time].[Week] * [Documents].[OrderlineID] ) on row, ({Measure.[W Expected Receipts]}) on column;

      df_in_WWAcptLot
      Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Item].[Item Stage].[SET] * [Item].[Plan Group] * [Time].[Week] * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W WIP Acceptable Lot]}) on column;

      df_in_WLotSplyCodeMap
      Select (Version.[Version Name] * FROM.[Documents].[OrderlineID] * TO.[Documents].[OrderlineID].Filter(#.Name != "SetSupplyCode")) on row, ({Edge.[001.007W Solver Inputs Supply Code Mapping].[W Lot Supply Code Map]}) on column where {RelationshipType.[001.007W Solver Inputs Supply Code Mapping]};

      -- sungmin.lim(25.5.26)  : 정의가 안되 있어서 추가
      df_in_MfLocation
      Select ([To Location].[To Location] * [To Location].[To Site Stage].filter(#.Name StartsWith("MF")));

      -- sungmin.lim(25.5.26)  : df 추가
      df_in_WActivityEndDate
      Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity End Date]}) on column;
      
      --heeyoung.yang(25.7.11)  : df 추가
      df_in_TimeWeek : Mfg Plan 계획일 을 구하기 위해 추가(2025.07.11)
                       Select ([Time].[Week] * [Time].[Day] * [Time].[Day of Week].[MON]);
      
      --heeyoung.yang(26.2.23)  : df 추가
      df_in_WActivityPrtTmV
      Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Activity1].[Activity1] * [Item].[Item] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Priority Time Varying], Measure.[W Activity Share]}) on column;


* Output Tables
    - df_out_SOPSync : Select (Version.[Version Name] * FROM.[Item].[Item] * FROM.[Location].[Location] * FROM.[Time].[Week] * FROM.[Activity1].[Activity1] * FROM.[Activity2].[Activity2] * FROM.[Activity3].[Activity3] * FROM.[Documents].[OrderlineID] * TO.[Location].[Location] * TO.[Time].[Week] * TO.[Activity1].[Activity1] * TO.[Activity2].[Activity2] * TO.[Activity3].[Activity3] * TO.[Documents].[OrderlineID]) on row, ({Edge.[SOP Sync].[SOP Sync_SOP Qty] , Edge.[SOP Sync].[SOP Sync_Mfg OrderlineID] , Edge.[SOP Sync].[SOP Sync_SOP OrderlineID] , Edge.[SOP Sync].[SOP Sync_Mfg OrderlineName] , Edge.[SOP Sync].[SOP Sync_SOP OrderlineName]}) on column where {RelationshipType.[SOP Sync]};

* 테스트 스크립트
    -병렬수행 호출 : exec procedure PR_MG_SOPSync{"Version":"CWV_MP", "PlanGroup":"1"};
    
    -전체실행 : EXEC plugin instance [PY_MG_SOPSync] for measures {[SOP Sync].[SOP Sync_SOP Qty]} using scope (&MPV * [Item].[Plan Group].filter(#.Name == "1")) 
                using arguments {("IncludeNullRows", "False"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};


"""

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import os
import pandas as pd
import numpy as np
import datetime as dt
import traceback
import gc
import tracemalloc
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_SOPSync'
is_local = common.gfn_get_isLocal()
COMMON_SOURCE_VERSION = common.G_SourceVersion

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level


########################################################################################################################
# logic start
########################################################################################################################
def read_csv_file(file_name):
    return pd.read_csv(f"{file_name}.csv", encoding="UTF-8", low_memory=False)

def save_csv_file(df, file_name):
    df.to_csv(f"{file_name}.csv", index=False)

#def print_df(df, df_name, p_log_level=LOG_LEVEL.debug(), p_format=1):
#    logger.PrintDF(p_df=df, p_df_name=df_name, p_log_level=p_log_level, p_format=p_format)

def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

#def step(no, string):
#    logger.Step(p_step_no=no, p_step_desc=f'{string}')


#logger.debug(f'[START] {str_instance}')
#logger.Start()
#note(f'=====> Common SourceVersion : {COMMON_SOURCE_VERSION}')
#step(0, '===================== plugin Execution Start =====================')
#tracemalloc.start()

try:
    ################################################################################################################
    # Batch 시작
    ################################################################################################################
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(),
                             (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)
    
    if is_local:
        print("datetime :", dt.datetime.now())
        paramCallSeq = '0'
    
    if paramCallSeq is None or paramCallSeq.strip() == '':
        paramCallSeq      = '0'
    
    #note(f'=====> paramCallSeq : {paramCallSeq}')
    #note(f'=====> paramCallSeq : {type(paramCallSeq)}')
    i_CallSeq = int(paramCallSeq)
    note(f'=====> i_CallSeq : {i_CallSeq}')
    ################################################################################################################
    # STEP 0 : DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====>STEP 0-1 DataFrame Column : 변수 처리')

    # 컬럼 변수 선언
    cl_VersionName = 'Version.[Version Name]'
    cl_Item = 'Item.[Item]'
    cl_ItemStage = 'Item.[Item Stage]'
    cl_BOMID = 'BOM Info.[BOM ID]'
    cl_Activity1 = 'Activity1.[Activity1]'
    cl_Activity2 = 'Activity2.[Activity2]'
    cl_Activity3 = 'Activity3.[Activity3]'
    cl_Location = 'Location.[Location]'
    cl_OrderlineID = 'Documents.[OrderlineID]'
    cl_Week = 'Time.[Week]'
    cl_Day = 'Time.[Day]'
    cl_ItemPlanGroup = 'Item.[Plan Group]'
    cl_SiteStage = 'Location.[Site Stage]'
    cl_ToLocationToLocation = 'To Location.[To Location]'
    cl_ToSiteStage = 'To Location.[To Site Stage]'

    cl_fromItem = 'from.[Item].[Item]'
    cl_fromLocation = 'from.[Location].[Location]'
    cl_fromWeek = 'from.[Time].[Week]'
    cl_fromOrderlineID = 'from.[Documents].[OrderlineID]'
    cl_fromActivity1 = 'from.[Activity1].[Activity1]'
    cl_fromActivity2 = 'from.[Activity2].[Activity2]'
    cl_fromActivity3 = 'from.[Activity3].[Activity3]'
    cl_toLocation = 'to.[Location].[Location]'
    cl_toWeek = 'to.[Time].[Week]'
    cl_toActivity1 = 'to.[Activity1].[Activity1]'
    cl_toActivity2 = 'to.[Activity2].[Activity2]'
    cl_toActivity3 = 'to.[Activity3].[Activity3]'
    cl_toOrderlineID = 'to.[Documents].[OrderlineID]'

    cl_SOPSync_SOPQty = 'SOP Sync.[SOP Sync_SOP Qty]'
    cl_SOPSync_MfgOrderlineID = 'SOP Sync.[SOP Sync_Mfg OrderlineID]'
    cl_SOPSync_SOPOrderlineID = 'SOP Sync.[SOP Sync_SOP OrderlineID]'
    cl_SOPSync_MfgOrderlineName = 'SOP Sync.[SOP Sync_Mfg OrderlineName]'
    cl_SOPSync_SOPOrderlineName = 'SOP Sync.[SOP Sync_SOP OrderlineName]'

    cl_WMaterialProductionQuantityPlanOutput = 'W Material Production Quantity Plan Output'
    cl_AmendSOP_SOPQty = 'Amend SOP_SOP Qty'
    # cl_AmendSOP_MfgSOPQty                    = 'Amend SOP_MfgSOP Qty'
    # cl_AmendSOP2_MfgSOPQty                   = 'Amend SOP2_MfgSOP Qty'
    # cl_SOPQty                                = 'SOP Sync_SOP Qty'
    cl_WActivityMandatoryOffset = 'W Activity Mandatory Offset'
    cl_WActivityPriorityTimeVarying = 'W Activity Priority Time Varying'
    cl_WFrozenWindow = 'W Frozen Window'
    cl_WOnHandQuantity = 'W OnHand Quantity'
    cl_WExpectedReceipts = 'W Expected Receipts'

    cl_ShipmentLT = 'ShipmentLT'
    cl_ShipmentLT_Week = 'ShipmentLT_Week'
    cl_rownumber = 'rownumber'
    cl_Frozen_Week = 'Frozen_Week'
    cl_WEEK_RANK = 'WEEK_RANK'
    cl_weekrn = 'week_rn'

    # sungmin.lim(25.5.26)  : 추가
    cl_WActivityEndDate = 'W Activity End Date'

    # 칼럼 List 설정
    cList_L_I = [cl_VersionName, cl_Location, cl_Item]
    cList_L_I_A2 = cList_L_I + [cl_Activity2]
    ################################################################################################################
    # STEP 0 : 전처리 : 모듈 내에서 사용될 input table load
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-2 : Input table load')

    # Value 변수 선언

    # 데이터 파일 읽기
    if is_local:
        df_in_Mfg = read_csv_file("df_in_Mfg")
        df_in_AmendSOP = read_csv_file("df_in_AmendSOP")
        df_in_ShipmentLT = read_csv_file("df_in_ShipmentLT")
        df_in_CurrentWeek = read_csv_file("df_in_CurrentWeek")
        df_in_WFrozen = read_csv_file("df_in_WFrozen")
        df_in_WOnHand = read_csv_file("df_in_WOnHand")
        df_in_Intransit = read_csv_file("df_in_Intransit")
        df_in_WWAcptLot = read_csv_file("df_in_WWAcptLot")
        df_in_WLotSplyCodeMap = read_csv_file("df_in_WLotSplyCodeMap")
        df_in_MfLocation = read_csv_file("df_in_MfLocation")

        # sungmin.lim(25.5.26)  : 추가
        df_in_WActivityEndDate = read_csv_file("df_in_WActivityEndDate")
        
        # heeyoung.yang(25.7.11)  : 추가
        df_in_TimeWeek = read_csv_file("df_in_TimeWeek")
        
        # heeyoung.yang(26.2.23)  : 추가
        df_in_WActivityPrtTmV = read_csv_file("df_in_WActivityPrtTmV")
        

        # # 한건 테스트
        #df_in_Mfg = df_in_Mfg.loc[(df_in_Mfg["Item.[Item]"] == "UA98DU9000KXXD")].copy()
        #df_in_AmendSOP = df_in_AmendSOP.loc[(df_in_AmendSOP["Item.[Item]"] == "UA98DU9000KXXD")].copy()

    # 입력 변수 확인

    # DATA TYPE 설정
    #######################################
    df_in_Mfg[cl_WMaterialProductionQuantityPlanOutput] = df_in_Mfg[cl_WMaterialProductionQuantityPlanOutput].fillna(
        0).astype('float64')
    df_in_Mfg['MFG_QTY'] = df_in_Mfg[cl_WMaterialProductionQuantityPlanOutput]
    df_in_Mfg = df_in_Mfg.astype({cl_Week: 'str'}, copy=True)

    df_in_AmendSOP[cl_AmendSOP_SOPQty] = df_in_AmendSOP[cl_AmendSOP_SOPQty].fillna(0).astype('float64')
    df_in_AmendSOP = df_in_AmendSOP.astype({cl_Week: 'str'}, copy=True)
    df_in_AmendSOP[cl_toWeek] = df_in_AmendSOP[cl_Week]
    df_in_AmendSOP[cl_toLocation] = df_in_AmendSOP[cl_Activity1].str.split('_').str[1]

    df_in_WOnHand[cl_WOnHandQuantity] = df_in_WOnHand[cl_WOnHandQuantity].fillna(0).astype('float64')
    df_in_WOnHand['MFG_QTY'] = df_in_WOnHand[cl_WOnHandQuantity]
    df_in_WOnHand = df_in_WOnHand.astype({cl_Week: 'str'}, copy=True)

    df_in_Intransit[cl_WExpectedReceipts] = df_in_Intransit[cl_WExpectedReceipts].fillna(0).astype('float64')
    df_in_Intransit['MFG_QTY'] = df_in_Intransit[cl_WExpectedReceipts]
    df_in_Intransit = df_in_Intransit.astype({cl_Week: 'str'}, copy=True)

    df_in_CurrentWeek = df_in_CurrentWeek.astype({cl_Week: 'str'}, copy=True)

    df_in_WWAcptLot = df_in_WWAcptLot.astype({cl_Week: 'str'}, copy=True)

    df_in_MfLocation.rename(columns={cl_ToLocationToLocation: cl_toLocation, cl_ToSiteStage: 'toSiteStage'},
                            inplace=True)
    
    # heeyoung.yang(25.7.11)  : 추가
    if df_in_WActivityEndDate[cl_WActivityEndDate].dtype != 'datetime64[ns]':
        df_in_WActivityEndDate[cl_WActivityEndDate] = pd.to_datetime(df_in_WActivityEndDate[cl_WActivityEndDate],
                                                            format='%m/%d/%Y %I:%M:%S %p')
    
    df_in_TimeWeek[cl_Day] = pd.to_datetime(df_in_TimeWeek[cl_Day], format='%Y-%m-%d')
    df_in_TimeWeek = df_in_TimeWeek[[cl_Week, cl_Day]]
    df_in_TimeWeek = df_in_TimeWeek.astype({cl_Week: 'str'}, copy=True)
    
    # input dataframe 확인용 로그

    vdCommon.gfn_saveDf(df_in_Mfg, 'df_in_Mfg',False)
    vdCommon.gfn_saveDf(df_in_AmendSOP, 'df_in_AmendSOP',False)
    vdCommon.gfn_saveDf(df_in_ShipmentLT, 'df_in_ShipmentLT',False)
    vdCommon.gfn_saveDf(df_in_CurrentWeek, 'df_in_CurrentWeek',False)
    vdCommon.gfn_saveDf(df_in_WFrozen, 'df_in_WFrozen',False)
    vdCommon.gfn_saveDf(df_in_WOnHand, 'df_in_WOnHand',False)
    vdCommon.gfn_saveDf(df_in_Intransit, 'df_in_Intransit',False)
    vdCommon.gfn_saveDf(df_in_WWAcptLot, 'df_in_WWAcptLot',False)
    vdCommon.gfn_saveDf(df_in_WLotSplyCodeMap, 'df_in_WLotSplyCodeMap',False)
    vdCommon.gfn_saveDf(df_in_MfLocation, 'df_in_MfLocation',False)

    # sungmin.lim(25.5.26)  : 추가
    vdCommon.gfn_saveDf(df_in_WActivityEndDate, 'df_in_WActivityEndDate',False)
    
    # heeyoung.yang(25.7.11)  : 추가
    vdCommon.gfn_saveDf(df_in_TimeWeek, 'df_in_TimeWeek', False)
    
    # heeyoung.yang(26.2.23)  : 추가
    vdCommon.gfn_saveDf(df_in_WActivityPrtTmV, 'df_in_WActivityPrtTmV', False)
    
    vdCommon.gfn_stepLog('=====> STEP 0-3 : Input table load End')
    
    ################################################################################################################
    # STEP 0-3 : 추가 df 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 0-4 : 추가 df Create ')
    df_in_Mfg.drop(columns=[cl_ItemPlanGroup, cl_ItemStage], inplace=True)
    df_in_AmendSOP.drop(columns=[cl_ItemPlanGroup, cl_ItemStage], inplace=True)
    df_in_WOnHand.drop(columns=[cl_ItemPlanGroup, cl_ItemStage], inplace=True)
    df_in_WFrozen.drop(columns=['W Frozen Window Apply At'], inplace=True)
    df_in_Intransit.drop(columns=[cl_ItemPlanGroup, cl_ItemStage], inplace=True)

    # merge df_in_MfLocation
    df_in_AmendSOP = df_in_AmendSOP.merge(df_in_MfLocation, on=[cl_toLocation], how='left')

    # WFrozen 사용될 DATA 만 추출
    cList_Frozen = [cl_VersionName, cl_Activity1, cl_Activity2, cl_Activity3]
    df_in_WFrozen = df_in_WFrozen[df_in_WFrozen.set_index(cList_Frozen).index.isin(
        df_in_Mfg.set_index(cList_Frozen).index)].copy()

    df_in_CurrentWeek['JOIN'] = 'A'
    df_in_WFrozen['JOIN'] = 'A'
    df_in_WFrozen = df_in_WFrozen.merge(df_in_CurrentWeek, on=['JOIN'], how='inner')

    # WFrozen : W Frozen Window 만큼 주차 조정
    df_in_WFrozen = df_in_WFrozen.astype({cl_Week: 'str'}, copy=True)
    df_in_WFrozen[cl_WFrozenWindow] = df_in_WFrozen[cl_WFrozenWindow].fillna(0).astype('int64')
    #df_in_WFrozen[cl_Frozen_Week] = df_in_WFrozen.apply(lambda x: common.gfn_add_week(x[cl_Week], (x[cl_WFrozenWindow])), axis=1)
    #빈 프레임일 경우 에러발생 : 수정(2026.01.26)
    if df_in_WFrozen.empty:
        df_in_WFrozen[cl_Frozen_Week] = ''
    else :
        df_in_WFrozen[cl_Frozen_Week] = df_in_WFrozen.apply(
                                             lambda x: common.gfn_add_week(x[cl_Week], (x[cl_WFrozenWindow])), axis=1)
    
    df_in_WFrozen.rename(columns={cl_Week: 'CurrentWeek'}, inplace=True)
    vdCommon.gfn_saveDf(df_in_WFrozen, 'df_in_WFrozen',False)
    # save_csv_file(df_in_WFrozen, 'df_in_WFrozen X')

    ################################################################################################################
    # STEP 1 : 총량 비교 및 조정
    # 재고, Intransit, 생산계획(mfgSOP) 총량(by Plant, Item)이 AmendSOP 총량(by Plant, Item) 보다 큰것을 읽어서
    # mfgSOP(000SCS_LOT) 계획 뒤날짜부터 삭제함
    ################################################################################################################
    # 칼럼추가
    df_in_WOnHand[cl_Activity1] = '-'
    df_in_WOnHand[cl_Activity2] = '-'
    df_in_WOnHand[cl_Activity3] = '-'
    df_in_WOnHand[cl_toWeek] = df_in_WOnHand[cl_Week]
    df_in_WOnHand[cl_toLocation] = '-'
    # 칼럼추가
    df_in_Intransit[cl_Activity1] = '-'
    df_in_Intransit[cl_Activity2] = '-'
    df_in_Intransit[cl_Activity3] = '-'
    df_in_Intransit[cl_toWeek] = df_in_Intransit[cl_Week]
    df_in_Intransit[cl_toLocation] = '-'

    cList_Mfg = cList_L_I + [cl_Week, cl_OrderlineID, cl_Activity1, cl_Activity2, cl_Activity3, 'MFG_QTY']

    df_Mfg = df_in_Mfg[cList_Mfg].copy()
    df_WOnHand = df_in_WOnHand[cList_Mfg].copy()
    df_Intransit = df_in_Intransit[cList_Mfg].copy()
    del [df_in_Mfg, df_in_WOnHand, df_in_Intransit]
    # save_csv_file(df_Mfg, 'df_Mfg')

    # 생산 총수량
    df_Mfg_all = pd.concat([df_Mfg, df_WOnHand, df_Intransit])
    df_Mfg_sum = df_Mfg_all.groupby(cList_L_I, as_index=False)['MFG_QTY'].sum()
    # vdCommon.gfn_saveDf(df_Mfg_sum, 'df_Mfg_sum',False)

    # 선적 총수량
    df_SOP_sum = df_in_AmendSOP.groupby(cList_L_I, as_index=False)[cl_AmendSOP_SOPQty].sum()
    # vdCommon.gfn_saveDf(df_SOP_sum, 'df_SOP_sum',False)

    # 차이 비교, merge
    df_Mfg_Sop_MG = df_Mfg_sum.merge(df_SOP_sum, on=cList_L_I, how='inner')
    df_Mfg_Sop_MG['diff_qty'] = df_Mfg_Sop_MG['MFG_QTY'] - df_Mfg_Sop_MG[cl_AmendSOP_SOPQty]
    df_Mfg_Sop_MG = df_Mfg_Sop_MG[df_Mfg_Sop_MG['diff_qty'] > 0]
    vdCommon.gfn_saveDf(df_Mfg_Sop_MG, 'df_Mfg_Sop_MG',False)

    # sungmin.lim(25.5.26)  : W Activity End Date 를 붙이고 Null 일 경우 미래일자(2199-01-01) 세팅
    df_Mfg = df_Mfg.merge(df_in_WActivityEndDate, on=[cl_VersionName, cl_Activity1, cl_Activity2, cl_Activity3], how='left')
    df_Mfg[cl_WActivityEndDate].fillna(pd.to_datetime("2199-01-01"), inplace=True)
    #vdCommon.gfn_saveDf(df_Mfg, 'df_Mfg WActivityEndDate', True)
    # 조정대상 / 비대상 분리
    # df_Mfg_Y = df_Mfg[(df_Mfg[cl_OrderlineID] == '000SCS_LOT') &
    #                  (df_Mfg[cl_Item] == df_Mfg[cl_Activity3])].copy()
    df_Mfg_Y = df_Mfg[~(df_Mfg.set_index([cl_VersionName, cl_OrderlineID]).index.isin(
        df_in_WLotSplyCodeMap.set_index([cl_VersionName, cl_fromOrderlineID]).index))].copy()

    df_Mfg_Y = df_Mfg_Y.astype({'MFG_QTY': 'float64'}, copy=True)
    df_Mfg_Y['Del_YN'] = np.nan
    df_Mfg_Y['Adj_qty'] = np.nan

    # df_Mfg_N = df_Mfg[~((df_Mfg[cl_OrderlineID] == '000SCS_LOT') &
    #                    (df_Mfg[cl_Item] == df_Mfg[cl_Activity3]))].copy()
    df_Mfg_N = df_Mfg[(df_Mfg.set_index([cl_VersionName, cl_OrderlineID]).index.isin(
        df_in_WLotSplyCodeMap.set_index([cl_VersionName, cl_fromOrderlineID]).index))].copy()

    vdCommon.gfn_saveDf(df_Mfg_Y, 'df_Mfg_Y',False)
    vdCommon.gfn_saveDf(df_Mfg_N, 'df_Mfg_N',False)
    # save_csv_file(df_Mfg_Y, 'df_Mfg_Y')
    # 조정대상이 있는 경우만
    df_Adj_SEL = df_Mfg_Sop_MG[df_Mfg_Sop_MG.set_index(cList_L_I).index.isin(
        df_Mfg_Y.set_index(cList_L_I).index)].copy()
    del [df_Mfg_sum, df_SOP_sum, df_Mfg_Sop_MG]
    vdCommon.gfn_saveDf(df_Adj_SEL, 'df_Adj_SEL',False)

    # -------------------------------------------------------------------------------------------
    # sungmin.lim(25.5.26)  : 정렬기준 추가
    # cList_temp = [cl_VersionName, cl_Location, cl_Item, cl_Week, cl_Activity2]
    # df_Mfg_Y = df_Mfg_Y.sort_values(by=cList_temp, ascending=[True, True, True, False, False]).reset_index(drop=True)
    cList_temp = [cl_VersionName, cl_Location, cl_Item, cl_Week, cl_WActivityEndDate, cl_Activity2]
    df_Mfg_Y = df_Mfg_Y.sort_values(by=cList_temp, ascending=[True, True, True, False, False, False]).reset_index(drop=True)

    df_Mfg_Y['MFG_RN'] = 1
    df_Mfg_Y['MFG_RN'] = df_Mfg_Y.groupby(cList_L_I)['MFG_RN'].cumsum()
    vdCommon.gfn_saveDf(df_Mfg_Y, 'df_Mfg_Y',False)
    # df_Mfg_Y 를 기준으로 index 를 가지는 HashMap 구성
    hm_index = {}
    df_MFG_Y_index = df_Mfg_Y.loc[(df_Mfg_Y['MFG_RN'] == 1)].copy()
    for idx in df_MFG_Y_index.index:
        key = (df_MFG_Y_index.loc[idx, cl_Location] + df_MFG_Y_index.loc[idx, cl_Item])
        hm_index[key] = idx

    # vdCommon.gfn_saveDf(df_MFG_Y_index, 'df_MFG_Y_index',False)

    f_idx = -1
    # for start -------------------------------------------------------------------------
    for idx in df_Adj_SEL.index:
        # print(idx)
        # df_Adj_SEL.loc[idx, 'diff_qty'] = 150
        vDiff_qty = df_Adj_SEL.loc[idx, 'diff_qty']  # 차이 수량 초기값
        vDiff_qty_org = vDiff_qty
        # print("vDiff_qty : " + str(vDiff_qty))

        key = (df_Adj_SEL.loc[idx, cl_Location] + df_Adj_SEL.loc[idx, cl_Item])
        keyData = (hm_index.get(key))
        if keyData != None:
            f_idx = keyData
        else:
            f_idx = -1
        # print("f_idx : " + str(f_idx))

        if (f_idx > -1 and f_idx < df_Mfg_Y.shape[0]):
            # while start--------------------------------------------------------------------------------------------
            while (df_Adj_SEL.loc[idx, cl_Location] == df_Mfg_Y.loc[f_idx, cl_Location]
                   and df_Adj_SEL.loc[idx, cl_Item] == df_Mfg_Y.loc[f_idx, cl_Item]):

                vMfg_qty = df_Mfg_Y.loc[f_idx, 'MFG_QTY']
                vDel_yn = 'N'
                vAdj_qty = 0
                # print(f'1=====>vMfg_qty : {vMfg_qty} , vAdj_qty : {vAdj_qty} , vDel_yn : {vDel_yn} ,'
                #      f' vDiff_qty " {vDiff_qty}, f_idx " {f_idx}')
                if vDiff_qty > 0:
                    if vMfg_qty == vDiff_qty:  # Mfg 수량과 차이수량이 같은경우
                        vAdj_qty = 0  # 조정수량 : 소진
                        vDel_yn = 'Y'  # 삭제대상
                        vDiff_qty = 0  # 차이수량 소진

                        df_Mfg_Y.loc[f_idx, 'Adj_qty'] = vAdj_qty  # 조정수량 : 소진
                        df_Mfg_Y.loc[f_idx, 'diff_qty'] = vDiff_qty  # 차이잔량
                        df_Mfg_Y.loc[f_idx, 'Del_YN'] = vDel_yn  # 삭제대상
                        f_idx = f_idx + 1

                    elif vMfg_qty > vDiff_qty:  # Mfg 수량이 차이수량보다 큰경우
                        vAdj_qty = vMfg_qty - vDiff_qty  # 조정수량
                        vDel_yn = 'N'  # 비삭제
                        vDiff_qty = 0  # 차이수량 소진

                        df_Mfg_Y.loc[f_idx, 'Adj_qty'] = vAdj_qty  # 조정수량
                        df_Mfg_Y.loc[f_idx, 'diff_qty'] = vDiff_qty  # 차이수량 소진
                        df_Mfg_Y.loc[f_idx, 'Del_YN'] = vDel_yn  # 비삭제

                    else:  # Mfg 수량이 차이수량보다 작은 경우
                        vAdj_qty = 0  # 조정수량 : 소진
                        vDel_yn = 'Y'  # 삭제대상
                        vDiff_qty = vDiff_qty - vMfg_qty  # 차이잔량

                        df_Mfg_Y.loc[f_idx, 'Adj_qty'] = vAdj_qty  # 조정수량 : 소진
                        df_Mfg_Y.loc[f_idx, 'diff_qty'] = vDiff_qty  # 차이잔량
                        df_Mfg_Y.loc[f_idx, 'Del_YN'] = vDel_yn  # 삭제대상
                        f_idx = f_idx + 1

                    df_Mfg_Y.loc[f_idx, 'diff_qty_org'] = vDiff_qty_org  # 차이 수량 초기값
                    df_Mfg_Y.loc[f_idx, 'MFG_QTY_org'] = vMfg_qty  # 차이 수량 초기값

                # print(f'2=====>vMfg_qty : {vMfg_qty} , vAdj_qty : {vAdj_qty} , vDel_yn : {vDel_yn} ,'
                #      f' vDiff_qty " {vDiff_qty}, f_idx " {f_idx}')

                if vDiff_qty == 0:
                    break

                if f_idx >= df_Mfg_Y.shape[0]:
                    break
            # while end--------------------------------------------------------------------------------------------
    # for end -------------------------------------------------------------------------
    df_Mfg_Y['MFG_QTY'] = np.where(df_Mfg_Y['Del_YN'].isna()
                                   , df_Mfg_Y['MFG_QTY']
                                   , df_Mfg_Y['Adj_qty'])
    df_Mfg_Y = df_Mfg_Y[~(df_Mfg_Y['Del_YN'] == 'Y')]

    # sungmin.lim(25.5.26)  : 정렬컬럼 추가
    cList_Mfg = cList_Mfg + [cl_WActivityEndDate]

    # 칼럼정리
    df_Mfg_Y = df_Mfg_Y[cList_Mfg].copy()

    '''
    # 확인용 생산 총수량
    df_Mfg_all_2 = pd.concat([df_Mfg_Y, df_Mfg_N, df_WOnHand, df_Intransit])
    df_Mfg_sum_2 = df_Mfg_all_2.groupby(cList_L_I, as_index=False)['MFG_QTY'].sum()
    # 확인용 선적 총수량
    df_SOP_sum_2 = df_in_AmendSOP.groupby(cList_L_I, as_index=False)[cl_AmendSOP_SOPQty].sum()

    # 확인용 차이 비교, merge
    df_Mfg_Sop_MG_2 = df_Mfg_sum_2.merge(df_SOP_sum_2, on=cList_L_I, how='inner')
    df_Mfg_Sop_MG_2['diff_qty'] = df_Mfg_Sop_MG_2['MFG_QTY'] - df_Mfg_Sop_MG_2[cl_AmendSOP_SOPQty]
    df_Mfg_Sop_MG_2 = df_Mfg_Sop_MG_2[df_Mfg_Sop_MG_2['diff_qty'] > 0]
    vdCommon.gfn_saveDf(df_Mfg_Sop_MG_2, 'df_Mfg_Sop_MG_2',False)

    df_Mfg_all_2 = df_Mfg_all_2[df_Mfg_all_2.set_index(cList_L_I).index.isin(
                                df_Mfg_Sop_MG_2.set_index(cList_L_I).index)].copy()
    vdCommon.gfn_saveDf(df_Mfg_all_2, 'df_Mfg_all_2',False)
    '''
    # save_csv_file(df_Mfg_Y, 'df_Mfg_Y')
    # df_Mfg = pd.concat([df_Mfg_Y, df_Mfg_N])
    # del [df_Mfg_Y, df_Mfg_N]
    # vdCommon.gfn_saveDf(df_Mfg, 'df_Mfg',False)
    # save_csv_file(df_Mfg, 'df_Mfg')

    ################################################################################################################
    # STEP 2 : Sync 대상 DF 구성
    ################################################################################################################
    # SOP ------------------------------------------------------------------------
    # W WIP Acceptable Lot이 지정된것을 제외
    df_WWAcptLot = df_in_WWAcptLot[df_in_WWAcptLot['W WIP Acceptable Lot'].notna()].copy()
    del df_in_WWAcptLot
    vdCommon.gfn_saveDf(df_WWAcptLot, 'df_WWAcptLot',False)
    # save_csv_file(df_WWAcptLot, 'df_WWAcptLot')

    df_SOP_MF = df_in_AmendSOP[(df_in_AmendSOP[cl_SiteStage].str.startswith('MF') &
                                df_in_AmendSOP['toSiteStage'].str.startswith('MF'))].copy()
    # save_csv_file(df_SOP_MF, 'df_SOP_MF')

    cList_SOP = cList_L_I + [cl_Week, cl_OrderlineID, cl_Activity1, cl_Activity2, cl_Activity3]
    df_SOP = df_in_AmendSOP[~(df_in_AmendSOP.set_index(cList_SOP).index.isin(df_WWAcptLot.set_index(cList_SOP).index))
                            &  # from, to location 이 모두 생산인 경우 제외
                            # ~(df_in_AmendSOP.set_index(cList_L_I).index.isin(df_SOP_MF.set_index(cList_L_I).index))
                            ~(df_in_AmendSOP[cl_SiteStage].str.startswith('MF') & df_in_AmendSOP[
                                'toSiteStage'].str.startswith('MF'))
                            ].copy()
    del df_in_AmendSOP
    vdCommon.gfn_saveDf(df_SOP, 'df_SOP',False)
    # save_csv_file(df_SOP, 'df_SOP 대상')

    # merge : ShipmentLT
    cList_ShipLT = [cl_VersionName, cl_Activity1, cl_Activity2, cl_Activity3]
    df_SOP = df_SOP.merge(df_in_ShipmentLT, on=cList_ShipLT, how='left')
    del df_in_ShipmentLT
    df_SOP.rename(columns={cl_WActivityMandatoryOffset: cl_ShipmentLT}, inplace=True)
    df_SOP[cl_ShipmentLT].fillna(0, inplace=True)
    df_SOP = df_SOP.astype({cl_Week: 'str', cl_ShipmentLT: 'int64'}, copy=True)

    # ShipmentL/T 만큼 주차 조정
    if df_SOP.empty:
        df_SOP[cl_ShipmentLT_Week] = df_SOP[cl_Week]
    else:
        df_SOP[cl_ShipmentLT_Week] = np.where((df_SOP[cl_ShipmentLT] == 0), df_SOP[cl_Week],
                                              df_SOP.apply(
                                                  lambda x: common.gfn_add_week(x[cl_Week], (-1 * x[cl_ShipmentLT])),
                                                  axis=1))
    df_SOP[cl_AmendSOP_SOPQty] = df_SOP[cl_AmendSOP_SOPQty].fillna(0).astype('float64')

    vdCommon.gfn_saveDf(df_SOP, 'df_SOP',False)
    # save_csv_file(df_SOP, 'df_SOP Lot 제외')

    # MFG ------------------------------------------------------------------------
    # AmendSOP 의 from, to location 이 모두 생산인 경우에 해당하는 MFG DATA 도 제외.
    df_Mfg_Y = df_Mfg_Y[~(df_Mfg_Y.set_index(cList_L_I).index.isin(df_SOP_MF.set_index(cList_L_I).index))]
    del df_SOP_MF
    # save_csv_file(df_Mfg_Y, 'df_Mfg_Y MF제외')

    # not exists : 비교대상 AmendSOP 가 없어 그대로
    df_Mfg_Y_NEx = df_Mfg_Y[~df_Mfg_Y.set_index(cList_L_I).index.isin(
        df_SOP.set_index(cList_L_I).index)].copy()

    df_Mfg_Y_NEx.rename(columns={cl_Location: cl_fromLocation, cl_Item: cl_fromItem, cl_Week: cl_fromWeek,
                                 cl_OrderlineID: cl_fromOrderlineID,
                                 cl_Activity1: cl_fromActivity1, cl_Activity2: cl_fromActivity2,
                                 cl_Activity3: cl_fromActivity3}, inplace=True)

    df_Mfg_Y_NEx[cl_SOPSync_SOPQty] = df_Mfg_Y_NEx['MFG_QTY']
    df_Mfg_Y_NEx[cl_toWeek] = df_Mfg_Y_NEx[cl_fromWeek]
    df_Mfg_Y_NEx[cl_toLocation] = '-'
    df_Mfg_Y_NEx[cl_toActivity1] = '-'
    df_Mfg_Y_NEx[cl_toActivity2] = '-'
    df_Mfg_Y_NEx[cl_toActivity3] = '-'
    df_Mfg_Y_NEx[cl_toOrderlineID] = 'INVALID'
    df_Mfg_Y_NEx['MFG_WEEK'] = df_Mfg_Y_NEx[cl_fromWeek]

    vdCommon.gfn_saveDf(df_Mfg_Y_NEx, 'df_Mfg_Y_NEx',False)
    # save_csv_file(df_Mfg_Y_NEx, 'df_Mfg_Y_NEx')

    # exists
    df_Mfg_X = df_Mfg_Y[df_Mfg_Y.set_index(cList_L_I).index.isin(
        df_SOP.set_index(cList_L_I).index)].copy()
    del df_Mfg_Y
    vdCommon.gfn_saveDf(df_Mfg_X, 'df_Mfg_X',False)

    ################################################################################################################
    # STEP 3 : Sync 처리
    ################################################################################################################
    # df_SOP
    # df_Mfg_X
    # df_Mfg_A2
    df_SOP.rename(columns={cl_Activity1: cl_toActivity1, cl_Activity2: cl_toActivity2, cl_Activity3: cl_toActivity3,
                           cl_OrderlineID: cl_toOrderlineID}, inplace=True)

    cList_temp = [cl_VersionName, cl_Location, cl_Item, cl_Activity2]
    df_Mfg_A2 = df_Mfg_X[cList_temp].copy()
    df_Mfg_A2.drop_duplicates(inplace=True)
    df_Mfg_A2['ACT2_RM_QTY'] = 0
    df_Mfg_A2['ACT2_USE_QTY'] = 0

    df_Mfg_A2 = df_Mfg_A2.sort_values(by=cList_temp, ascending=[True, True, True, False]).reset_index(drop=True)
    vdCommon.gfn_saveDf(df_Mfg_A2, 'df_Mfg_A2',False)

    # -------------------------------------------------------------------------------------------
    # sungmin.lim(25.5.26)  : cl_WActivityEndDate 정렬 기준을 추가
    # cList_temp = [cl_VersionName, cl_Location, cl_Item, cl_Week, cl_Activity2]
    # df_Mfg_X = df_Mfg_X.sort_values(by=cList_temp, ascending=[True, True, True, False, False]).reset_index(drop=True)
    cList_temp = [cl_VersionName, cl_Location, cl_Item, cl_Week, cl_WActivityEndDate, cl_Activity2]
    df_Mfg_X = df_Mfg_X.sort_values(by=cList_temp, ascending=[True, True, True, False, False, False]).reset_index(drop=True)

    df_Mfg_X['MFG_RN'] = 1
    df_Mfg_X['MFG_RN'] = df_Mfg_X.groupby(cList_L_I)['MFG_RN'].cumsum()
    df_Mfg_X.rename(columns={cl_Week: 'MFG_WEEK'}, inplace=True)
    df_Mfg_X['MFG_TOTAL'] = df_Mfg_X.groupby(cList_L_I)['MFG_QTY'].transform('sum')
    df_Mfg_X['ACT2_TOTAL'] = df_Mfg_X.groupby(cList_L_I_A2)['MFG_QTY'].transform('sum')
    vdCommon.gfn_saveDf(df_Mfg_X, 'df_Mfg_X',False)
    # save_csv_file(df_Mfg_X, 'df_Mfg_X org')
    # df_Mfg_X 를 기준으로 index 를 가지는 HashMap 구성
    hm_index = {}
    df_MFG_index = df_Mfg_X.loc[(df_Mfg_X['MFG_RN'] == 1)].copy()
    for idx in df_MFG_index.index:
        key = (df_MFG_index.loc[idx, cl_Location] + df_MFG_index.loc[idx, cl_Item])
        hm_index[key] = idx

    # vdCommon.gfn_saveDf(df_MFG_index, 'df_MFG_index',False)
    # print(hm_index)

    # -------------------------------------------------------------------------------------------
    # df_Mfg_A2 를 기준으로 index 를 가지는 HashMap 구성
    hm_A2_index = {}
    for idx in df_Mfg_A2.index:
        A2_key = (df_Mfg_A2.loc[idx, cl_Location] + df_Mfg_A2.loc[idx, cl_Item] + df_Mfg_A2.loc[idx, cl_Activity2])
        hm_A2_index[A2_key] = idx

    # df_Mfg_A2 를 기준으로 index 를 가지는 HashMap 구성
    # 결과를 저장할 리스트
    results = []
    df_result = pd.DataFrame([], columns=[])

    # -------------------------------------------------------------------------------------------
    cList_temp = [cl_VersionName, cl_Location, cl_Item, cl_ShipmentLT_Week, cl_toWeek, cl_toLocation]
    df_SOP = df_SOP.sort_values(by=cList_temp, ascending=[True, True, True, False, False, True]).reset_index(drop=True)

    df_SOP['AMD_RN'] = 1
    df_SOP['AMD_RN'] = df_SOP.groupby(cList_L_I)['AMD_RN'].cumsum()
    df_SOP['SOP_TOTAL'] = df_SOP.groupby(cList_L_I)[cl_AmendSOP_SOPQty].transform('sum')

    vdCommon.gfn_saveDf(df_SOP, 'df_SOP',False)
    # save_csv_file(df_SOP, 'df_SOP org')

    # -------------------------------------------------------------------------------------------
    f_idx = -1
    rate_count = round(df_SOP.shape[0] / 100, 0)
    # for start -------------------------------------------------------------------------
    for idx in df_SOP.index:
        # print(idx)
        # MFG 의 시작위치를 찾는다.
        if df_SOP.loc[idx, "AMD_RN"] == 1:
            # HashMap 에서 index 를 가져옴
            key = (df_SOP.loc[idx, cl_Location] + df_SOP.loc[idx, cl_Item])
            keyData = (hm_index.get(key))
            if keyData != None:
                f_idx = keyData
            else:
                f_idx = -1
            # print("key : " + str(key))

            vVersionName = df_SOP.loc[idx, cl_VersionName]
            vItem = df_SOP.loc[idx, cl_Item]
            vLocation = df_SOP.loc[idx, cl_Location]
            vSOP_TOTAL = df_SOP.loc[idx, 'SOP_TOTAL']
            vACT2_USE_QTY = 0
            vUSE_QTY = 0
            vACT2_RM_QTY = 0

            remaining_SOP = 0
            remaining_MFG = 0
            vAdj_Qty = 0

        # SOP Qty
        SOP_qty = df_SOP.loc[idx, cl_AmendSOP_SOPQty]
        vSOP_QTY_ORG = SOP_qty
        vShipmentLT_Week = df_SOP.loc[idx, cl_ShipmentLT_Week]
        vFromWeek = vShipmentLT_Week

        vtoLocation = df_SOP.loc[idx, cl_toLocation]
        vtoWeek = df_SOP.loc[idx, cl_toWeek]
        vtoActivity1 = df_SOP.loc[idx, cl_toActivity1]
        vtoActivity2 = df_SOP.loc[idx, cl_toActivity2]
        vtoActivity3 = df_SOP.loc[idx, cl_toActivity3]
        vtoOrderlineID = df_SOP.loc[idx, cl_toOrderlineID]

        # print(f'=====>vShipmentLT_Week : {vShipmentLT_Week} , SOP_qty : {SOP_qty} ')

        if (f_idx > -1 and f_idx < df_Mfg_X.shape[0]):
            # print(df_SOP.loc[idx, cl_Item] + " : " + df_SOP.loc[idx, cl_Location] + " : " +
            #       df_SOP.loc[idx, cl_ShipmentLT_Week] + " : " + str(df_SOP.loc[idx, "AMD_RN"]))

            # --------------------------------------------------------------------------------------------------
            while (df_SOP.loc[idx, cl_Location] == df_Mfg_X.loc[f_idx, cl_Location]
                   and df_SOP.loc[idx, cl_Item] == df_Mfg_X.loc[f_idx, cl_Item]):

                vOrderlineID = df_Mfg_X.loc[f_idx, cl_OrderlineID]
                vActivity1 = df_Mfg_X.loc[f_idx, cl_Activity1]
                vActivity2 = df_Mfg_X.loc[f_idx, cl_Activity2]
                vActivity3 = df_Mfg_X.loc[f_idx, cl_Activity3]
                vMFG_WEEK = df_Mfg_X.loc[f_idx, 'MFG_WEEK']
                vMFG_TOTAL = df_Mfg_X.loc[f_idx, 'MFG_TOTAL']
                vACT2_TOTAL = df_Mfg_X.loc[f_idx, 'ACT2_TOTAL']
                vMFG_RN = df_Mfg_X.loc[f_idx, 'MFG_RN']

                # Activity2 참조------------------------------
                A2_key = (df_Mfg_X.loc[f_idx, cl_Location] + df_Mfg_X.loc[f_idx, cl_Item] +
                          df_Mfg_X.loc[f_idx, cl_Activity2])
                A2keyData = (hm_A2_index.get(A2_key))

                if A2keyData != None:
                    A2_idx = A2keyData
                else:
                    A2_idx = -1
                # print("A2_idx : " + str(A2_idx) + " , Activity2 :" + df_Mfg_X.loc[f_idx, cl_Activity2])

                vACT2_RM_QTY = df_Mfg_A2.loc[A2_idx, 'ACT2_RM_QTY']
                vACT2_USE_QTY = df_Mfg_A2.loc[A2_idx, 'ACT2_USE_QTY']

                vMFG_QTY_ORG = df_Mfg_X.loc[f_idx, "MFG_QTY"]
                Mfg_qty = df_Mfg_X.loc[f_idx, "MFG_QTY"] + vACT2_RM_QTY

                if remaining_MFG == 0:
                    remaining_MFG = Mfg_qty
                else:
                    Mfg_qty = remaining_MFG

                # print(f'1=====>SOP_qty : {SOP_qty} , vMFG_QTY_ORG : {vMFG_QTY_ORG},  Mfg_qty : {Mfg_qty} , vACT2_RM_QTY : {vACT2_RM_QTY} ,'
                #      f' vActivity2 " {vActivity2}')

                if SOP_qty == Mfg_qty:
                    vAdj_Qty = SOP_qty
                    remaining_SOP = 0
                    remaining_MFG = 0
                    df_SOP.loc[idx, cl_AmendSOP_SOPQty] = remaining_SOP
                    df_Mfg_X.loc[f_idx, "MFG_QTY"] = remaining_MFG
                    # df_Mfg_A2.loc[A2_idx, 'ACT2_RM_QTY'] = remaining_MFG
                    SOP_qty = remaining_SOP
                    f_idx = f_idx + 1
                    # break

                elif SOP_qty > Mfg_qty:
                    vAdj_Qty = Mfg_qty
                    remaining_SOP = SOP_qty - Mfg_qty
                    remaining_MFG = 0
                    df_SOP.loc[idx, cl_AmendSOP_SOPQty] = remaining_SOP
                    df_Mfg_X.loc[f_idx, "MFG_QTY"] = remaining_MFG
                    # df_Mfg_A2.loc[A2_idx, 'ACT2_RM_QTY'] = remaining_MFG
                    SOP_qty = remaining_SOP

                    f_idx = f_idx + 1
                else:
                    vAdj_Qty = SOP_qty
                    remaining_SOP = 0
                    remaining_MFG = Mfg_qty - SOP_qty
                    df_SOP.loc[idx, cl_AmendSOP_SOPQty] = remaining_SOP
                    df_Mfg_X.loc[f_idx, "MFG_QTY"] = remaining_MFG
                    # df_Mfg_A2.loc[A2_idx, 'ACT2_RM_QTY'] =remaining_MFG
                    SOP_qty = remaining_SOP
                    # break

                vACT2_RM_QTY = remaining_MFG
                vACT2_USE_QTY = vACT2_USE_QTY + vAdj_Qty
                vUSE_QTY = vUSE_QTY + vAdj_Qty

                # print(f'2=====>SOP_qty : {SOP_qty} , Mfg_qty : {Mfg_qty} , vACT2_RM_QTY : {vACT2_RM_QTY} ,'
                #      f' remaining_SOP " {remaining_SOP}, remaining_MFG " {remaining_MFG}')

                # if vOrderlineID.startswith('MFG_'):
                #    vFromWeek = vMFG_WEEK
                # else:
                #    vFromWeek =vShipmentLT_Week
                # print(f'3=====>vOrderlineID : {vOrderlineID} , vShipmentLT_Week : {vShipmentLT_Week} , vFromWeek : {vFromWeek},'
                #      f'vMFG_WEEK : {vMFG_WEEK}')

                results.append({cl_VersionName: vVersionName
                                   , cl_fromLocation: vLocation
                                   , cl_fromItem: vItem
                                   , cl_fromWeek: vShipmentLT_Week
                                   , cl_fromOrderlineID: vOrderlineID
                                   , cl_fromActivity1: vActivity1
                                   , cl_fromActivity2: vActivity2
                                   , cl_fromActivity3: vActivity3
                                   , cl_toLocation: vtoLocation
                                   , cl_toWeek: vtoWeek
                                   , cl_toActivity1: vtoActivity1
                                   , cl_toActivity2: vtoActivity2
                                   , cl_toActivity3: vtoActivity3
                                   , cl_toOrderlineID: vtoOrderlineID
                                   , 'MFG_WEEK': vMFG_WEEK
                                   , 'MFG_QTY': vMFG_QTY_ORG
                                   , 'ADJ_MFG_QTY': Mfg_qty
                                   , 'ORG_SOPQty': vSOP_QTY_ORG
                                   , 'RM_SOP': SOP_qty
                                   , cl_SOPSync_SOPQty: vAdj_Qty
                                   , 'ADJ_QTY': vAdj_Qty
                                   , 'USE_QTY': vUSE_QTY
                                   , 'ROW_ACT2_RM_QTY': vACT2_RM_QTY
                                   , 'ROW_ACT2_USE_QTY': vACT2_USE_QTY
                                   , 'ACT2_RM_QTY': vACT2_RM_QTY
                                   , 'ACT2_USE_QTY': vACT2_USE_QTY
                                   , 'MFG_RN': vMFG_RN
                                   , 'MFG_TOTAL': vMFG_TOTAL
                                   , 'ACT2_TOTAL': vACT2_TOTAL
                                   , 'SOP_TOTAL': vSOP_TOTAL
                                # , 'ACT2_RN': A_row['ACT2_RN']
                                # , 'ACT2_MAX_RN': A_row['ACT2_MAX_RN']
                                # , 'AMD_RN': B_row['AMD_RN']
                                # , 'AMD_MAX_RN': B_row['AMD_MAX_RN']
                                # , 'MFG_MAX_RN': A_row['MFG_MAX_RN']
                                   , 'sync': 'sync'
                                })

                df_Mfg_A2.loc[A2_idx, 'ACT2_RM_QTY'] = vACT2_RM_QTY
                df_Mfg_A2.loc[A2_idx, 'ACT2_USE_QTY'] = vACT2_USE_QTY

                if remaining_SOP == 0:
                    break

                if f_idx >= df_Mfg_X.shape[0]:
                    break
        # elif:

        # if rate_count > 0:
        #    if idx % rate_count == 0:
        #        print("Process Rate : " + str(round(idx * 100 / df_SOP.shape[0])) + "%" + " , idx : " + str(idx))
    # for End ------------------------------------------------------------------------------------
    # save_csv_file(df_Mfg_A2, 'df_Mfg_A2')
    del [df_Mfg_A2, df_MFG_index]
    # save_csv_file(df_SOP, 'df_SOP')
    # save_csv_file(df_Mfg_X, 'df_Mfg_X')

    # SOP 소진되어 Sync 처리 못한 MFG 잔량 : 위에서 총량 조정으로 거의 발생 않함.
    df_Mfg_RM = df_Mfg_X.loc[(df_Mfg_X['MFG_QTY'] > 0)].copy()
    df_Mfg_RM.rename(columns={cl_Location: cl_fromLocation, cl_Item: cl_fromItem, 'MFG_WEEK': cl_fromWeek,
                              cl_OrderlineID: cl_fromOrderlineID,
                              cl_Activity1: cl_fromActivity1, cl_Activity2: cl_fromActivity2,
                              cl_Activity3: cl_fromActivity3}, inplace=True)
    df_Mfg_RM[cl_toLocation] = '-'
    df_Mfg_RM[cl_toWeek] = df_Mfg_RM[cl_fromWeek]
    df_Mfg_RM[cl_toActivity1] = '-'
    df_Mfg_RM[cl_toActivity2] = '-'
    df_Mfg_RM[cl_toActivity3] = '-'
    df_Mfg_RM[cl_toOrderlineID] = 'INVALID'
    df_Mfg_RM['ADJ_QTY'] = df_Mfg_RM['MFG_QTY']
    df_Mfg_RM[cl_SOPSync_SOPQty] = df_Mfg_RM['MFG_QTY']
    df_Mfg_RM['SOP_TOTAL'] = np.nan
    df_Mfg_RM['MFG_WEEK'] = df_Mfg_RM[cl_fromWeek]
    df_Mfg_RM['sync'] = 'No'
    vdCommon.gfn_saveDf(df_Mfg_RM, 'df_Mfg_RM',False)

    # MFG  소진되어 Sync 처리 못한 SOP 잔량
    df_SOP_RM = df_SOP.loc[(df_SOP[cl_AmendSOP_SOPQty] > 0)].copy()
    df_SOP_RM.rename(columns={cl_Location: cl_fromLocation, cl_Item: cl_fromItem}, inplace=True)
    df_SOP_RM[cl_fromWeek] = df_SOP_RM[cl_ShipmentLT_Week]
    df_SOP_RM[cl_fromActivity1] = '-'
    df_SOP_RM[cl_fromActivity2] = '-'
    df_SOP_RM[cl_fromActivity3] = '-'
    df_SOP_RM[cl_fromOrderlineID] = 'INVALID'
    df_SOP_RM['ADJ_QTY'] = df_SOP_RM[cl_AmendSOP_SOPQty]
    df_SOP_RM[cl_SOPSync_SOPQty] = df_SOP_RM[cl_AmendSOP_SOPQty]
    df_SOP_RM['MFG_TOTAL'] = np.nan
    df_SOP_RM['ACT2_TOTAL'] = np.nan
    df_SOP_RM['MFG_WEEK'] = df_Mfg_RM[cl_fromWeek]
    df_SOP_RM['sync'] = 'No'
    vdCommon.gfn_saveDf(df_SOP_RM, 'df_SOP_RM',False)

    cList_OUT = [cl_VersionName, cl_fromLocation, cl_fromItem, cl_fromWeek, cl_fromOrderlineID,
                 cl_fromActivity1, cl_fromActivity2, cl_fromActivity3,
                 cl_toLocation, cl_toWeek, cl_toActivity1, cl_toActivity2, cl_toActivity3, cl_toOrderlineID,
                 cl_SOPSync_SOPQty, 'ADJ_QTY', 'MFG_TOTAL', 'ACT2_TOTAL', 'SOP_TOTAL', 'MFG_WEEK', 'sync']

    if len(results) == 0:
        df_result = pd.DataFrame(columns=cList_OUT)  # 빈 dataframe
    else:
        df_result = pd.DataFrame(results)

    results.clear()

    # 칼럼정리
    df_result = df_result[cList_OUT]
    df_Mfg_RM = df_Mfg_RM[cList_OUT]
    df_SOP_RM = df_SOP_RM[cList_OUT]

    df_result = pd.concat([df_result, df_Mfg_RM, df_SOP_RM])

    cList_temp = [cl_VersionName, cl_fromLocation, cl_fromItem, 'sync', cl_fromWeek, cl_toWeek]
    df_result = df_result.sort_values(by=cList_temp, ascending=[True, True, True, False, False, False]).reset_index(
        drop=True)

    # vdCommon.gfn_saveDf(df_result, 'df_result',False)
    # save_csv_file(df_result, 'df_result 1')

    # df_result['MFG_TOTAL'] = df_result['MFG_TOTAL'].fillna(method='ffill')
    # df_result['SOP_TOTAL'] = df_result['SOP_TOTAL'].fillna(method='ffill')

    cList_form_L_I = [cl_VersionName, cl_fromLocation, cl_fromItem]
    cList_form_L_I_A2 = cList_form_L_I + [cl_fromActivity2]
    df_result['ADJ_SUM1'] = df_result[df_result[cl_fromActivity2] != '-'].groupby(cList_form_L_I)['ADJ_QTY'].transform(
        'sum')
    df_result['ADJ_SUM2'] = df_result[df_result[cl_toActivity1] != '-'].groupby(cList_form_L_I)['ADJ_QTY'].transform(
        'sum')
    df_result['ADJ_SUM_ACT2'] = df_result[df_result[cl_fromActivity2] != '-'].groupby(cList_form_L_I_A2)[
        'ADJ_QTY'].transform('sum')

    df_result['MFG_TOTAL'] = df_result['MFG_TOTAL'].round(4)
    df_result['ADJ_SUM1'] = df_result['ADJ_SUM1'].round(4)

    df_result['SOP_TOTAL'] = df_result['SOP_TOTAL'].round(4)
    df_result['ADJ_SUM2'] = df_result['ADJ_SUM2'].round(4)

    df_result['ACT2_TOTAL'] = df_result['ACT2_TOTAL'].round(4)
    df_result['ADJ_SUM_ACT2'] = df_result['ADJ_SUM_ACT2'].round(4)

    df_result['SUM_CHECK'] = np.where((df_result['MFG_TOTAL'] == df_result['ADJ_SUM1']) |
                                      (df_result[cl_fromActivity2] == '-'), True, False)

    df_result['SUM_CHECK2'] = np.where((df_result['SOP_TOTAL'] == df_result['ADJ_SUM2']) |
                                       (df_result[cl_toActivity1] == '-'), True, False)

    df_result['SUM_CHECK_ACT2'] = np.where((df_result['ACT2_TOTAL'] == df_result['ADJ_SUM_ACT2']) |
                                           (df_result[cl_fromActivity2] == '-'), 0, 1)
    df_result['SUM_CHECK_ACT2_SUM'] = df_result.groupby(cList_form_L_I)['SUM_CHECK_ACT2'].transform('sum')

    df_result['CHECK_3'] = np.where((df_result['ADJ_QTY'] < 0), 1, 0)
    df_result['CHECK_3_SUM'] = df_result.groupby(cList_form_L_I)['CHECK_3'].transform('sum')

    # del [df_SOP, df_Mfg_X]

    vdCommon.gfn_saveDf(df_result, 'df_result',False)
    # save_csv_file(df_result, 'df_result')

    # 수량 조정 결과 확인
    df_result_False = df_result[((df_result['SUM_CHECK'] == False) |
                                 (df_result['SUM_CHECK2'] == False) |
                                 (df_result['SUM_CHECK_ACT2_SUM'] > 0) |
                                 (df_result['CHECK_3_SUM'] > 0))].copy()
    vdCommon.gfn_saveDf(df_result_False, 'df_result_False',False)
    # save_csv_file(df_result_False, 'df_result_False')
    del df_result_False

    # 취합1
    cList_OUT2 = cList_form_L_I + [cl_fromWeek, cl_fromOrderlineID,
                                   cl_fromActivity1, cl_fromActivity2, cl_fromActivity3,
                                   cl_toLocation, cl_toWeek, cl_toActivity1, cl_toActivity2, cl_toActivity3,
                                   cl_toOrderlineID, cl_SOPSync_SOPQty, 'MFG_WEEK']

    # 칼럼정리
    df_result = df_result[cList_OUT2].copy()
    df_Mfg_Y_NEx = df_Mfg_Y_NEx[cList_OUT2].copy()

    df_Mfg_Y = pd.concat([df_result, df_Mfg_Y_NEx])
    del [df_result, df_Mfg_Y_NEx]
    vdCommon.gfn_saveDf(df_Mfg_Y, 'df_Mfg_Y',False)
    # save_csv_file(df_Mfg_Y, 'df_Mfg_Y')

    cList_GRAIN = cList_form_L_I + [cl_fromWeek, cl_fromOrderlineID,
                                    cl_fromActivity1, cl_fromActivity2, cl_fromActivity3,
                                    cl_toLocation, cl_toWeek, cl_toActivity1, cl_toActivity2, cl_toActivity3,
                                    cl_toOrderlineID]

    df_Mfg_Y = df_Mfg_Y.astype({cl_fromWeek: 'str'}, copy=True)

    # Frozen_Week 조정
    cList_Frozen = [cl_VersionName, cl_fromActivity1, cl_fromActivity2, cl_fromActivity3]
    df_in_WFrozen[cl_fromActivity1] = df_in_WFrozen[cl_Activity1]
    df_in_WFrozen[cl_fromActivity2] = df_in_WFrozen[cl_Activity2]
    df_in_WFrozen[cl_fromActivity3] = df_in_WFrozen[cl_Activity3]
    df_Mfg_Y = df_Mfg_Y.merge(df_in_WFrozen, on=cList_Frozen, how='left')
    vdCommon.gfn_saveDf(df_Mfg_Y, 'df_Mfg_Y 1',False)
    # save_csv_file(df_Mfg_Y, 'df_Mfg_Y Frozen')
    # df_frozen_temp = df_Mfg_Y[(df_Mfg_Y[cl_fromWeek] < df_Mfg_Y[cl_Frozen_Week])].copy()
    # vdCommon.gfn_saveDf(df_frozen_temp, 'df_frozen_temp',False)
    del df_in_WFrozen
    df_Mfg_Y[cl_fromWeek] = np.where(df_Mfg_Y[cl_Frozen_Week].notna() &
                                     (df_Mfg_Y[cl_fromWeek] < df_Mfg_Y[cl_Frozen_Week]),
                                     df_Mfg_Y[cl_Frozen_Week],
                                     df_Mfg_Y[cl_fromWeek])

    # OrderlineID 가 MFG_% 인 경우는 MFG_WEEK 적용
    df_Mfg_Y[cl_fromWeek] = np.where(df_Mfg_Y[cl_fromOrderlineID].str.startswith('MFG_'),
                                     df_Mfg_Y['MFG_WEEK'], df_Mfg_Y[cl_fromWeek])

    # 칼럼정리
    df_Mfg_Y = df_Mfg_Y[cList_OUT2].copy()
    # save_csv_file(df_Mfg_Y, 'df_Mfg_Y Sync 1')

    df_Mfg_Y = df_Mfg_Y.groupby(cList_GRAIN, as_index=False)[cl_SOPSync_SOPQty].sum()
    # 반올림(김기복수석 요청. 20250423)
    df_Mfg_Y[cl_SOPSync_SOPQty] = df_Mfg_Y[cl_SOPSync_SOPQty].round(0)
    df_Mfg_Y = df_Mfg_Y[df_Mfg_Y[cl_SOPSync_SOPQty] > 0].copy()
    # vdCommon.gfn_saveDf(df_Mfg_Y, 'df_Mfg_Y',False)
    # save_csv_file(df_Mfg_Y, 'df_Mfg_Y Sync')

    # df_Mfg_N : OUT에 추가 안함.
    # df_WOnHand : OUT에 추가 안함.
    # df_Intransit : OUT에 추가 안함.
    '''
    df_Mfg_N.rename(columns={cl_Location: cl_fromLocation, cl_Item: cl_fromItem, cl_Week: cl_fromWeek,
                              cl_OrderlineID: cl_fromOrderlineID,
                              cl_Activity1: cl_fromActivity1, cl_Activity2: cl_fromActivity2,
                              cl_Activity3: cl_fromActivity3}, inplace=True)
    df_Mfg_N[cl_toLocation] = '-'
    df_Mfg_N[cl_toWeek] = df_Mfg_N[cl_fromWeek]
    df_Mfg_N[cl_toActivity1] = '-'
    df_Mfg_N[cl_toActivity2] = '-'
    df_Mfg_N[cl_toActivity3] = '-'
    df_Mfg_N[cl_toOrderlineID] = 'INVALID'
    df_Mfg_N[cl_SOPSync_SOPQty] = df_Mfg_N['MFG_QTY']
    vdCommon.gfn_saveDf(df_Mfg_N, 'df_Mfg_N',False)

    #칼럼정리
    #df_Mfg_N = df_Mfg_N[cList_OUT3].copy()

    # 취합
    #df_Mfg_All = pd.concat([df_Mfg_Y, df_Mfg_N])
    '''
    del [df_Mfg_N, df_WOnHand, df_Intransit]

    cList_OUT3 = cList_form_L_I + [cl_fromWeek, cl_fromOrderlineID,
                                   cl_fromActivity1, cl_fromActivity2, cl_fromActivity3,
                                   cl_toLocation, cl_toWeek, cl_toActivity1, cl_toActivity2, cl_toActivity3,
                                   cl_toOrderlineID, cl_SOPSync_SOPQty]

    df_Mfg_All = df_Mfg_Y[cList_OUT3].copy()
    del df_Mfg_Y

    df_Mfg_All['OrderlineName'] = (
                df_Mfg_All[cl_fromItem] + '_' + df_Mfg_All[cl_fromActivity1] + '_' + df_Mfg_All[cl_fromLocation] + '_' +
                df_Mfg_All[cl_toLocation] + '_' + df_Mfg_All[cl_fromOrderlineID] + '_' +
                df_Mfg_All[cl_toOrderlineID] + '_' + df_Mfg_All[cl_fromWeek] + '_' +
                df_Mfg_All[cl_toWeek])

    df_Mfg_TEMP = df_Mfg_All[[cl_VersionName, 'OrderlineName']].copy()
    df_Mfg_TEMP.drop_duplicates(inplace=True)

    cList_sort = [cl_VersionName, 'OrderlineName']
    df_Mfg_TEMP.sort_values(by=cList_sort, ascending=[True, True], axis=0, inplace=True)

    df_Mfg_TEMP['seq'] = 1

    df_Mfg_TEMP['seq'] = df_Mfg_TEMP.groupby([cl_VersionName])['seq'].cumsum()
    df_Mfg_TEMP['MAX_SEQ'] = df_Mfg_TEMP.groupby([cl_VersionName])['seq'].transform('max')
    vdCommon.gfn_saveDf(df_Mfg_TEMP, 'df_Mfg_TEMP',False)

    df_Mfg_All = df_Mfg_All.merge(df_Mfg_TEMP, on=[cl_VersionName, 'OrderlineName'], how='left')
    del df_Mfg_TEMP

    #df_Mfg_All['seq'] = np.where((df_Mfg_All[cl_fromLocation] == 'P551'), df_Mfg_All['seq'],
    #                             np.where((df_Mfg_All[cl_fromLocation] == 'P306'), df_Mfg_All['seq'] + 200000,
    #                                      df_Mfg_All['seq'] + 400000))
    #df_Mfg_All['seq'] = df_Mfg_All['seq'] + (i_CallSeq * 200000)
    
    i_AddSeq = i_CallSeq * 100000
    if i_CallSeq > 0:
        i_AddSeq = i_AddSeq + 100000
    
    note(f'=====> i_AddSeq : {i_AddSeq}')
    df_Mfg_All['seq'] = df_Mfg_All['seq'] + i_AddSeq
    
    df_Mfg_All['seq'] = df_Mfg_All['seq'].astype('str')
    df_Mfg_All['seq'] = df_Mfg_All['seq'].str.pad(width=9, side='left', fillchar='0')

    vdCommon.gfn_saveDf(df_Mfg_All, 'df_Mfg_All',False)

    df_Mfg_All[cl_SOPSync_MfgOrderlineName] = np.where((df_Mfg_All[cl_fromOrderlineID] == 'INVALID'), np.nan,
                                                       'LPSM_' + df_Mfg_All['OrderlineName'])
    df_Mfg_All[cl_SOPSync_SOPOrderlineName] = np.where((df_Mfg_All[cl_toOrderlineID] == 'INVALID'), np.nan,
                                                       'LPSS_' + df_Mfg_All['OrderlineName'])

    df_Mfg_All[cl_SOPSync_MfgOrderlineID] = np.where((df_Mfg_All[cl_fromOrderlineID] == 'INVALID'), np.nan,
                                                     np.where((df_Mfg_All[cl_fromOrderlineID] != '000SCS_LOT'),
                                                              df_Mfg_All[cl_fromOrderlineID],
                                                              'LPSM_' + df_Mfg_All['seq'].astype('str'))
                                                     )

    df_Mfg_All[cl_SOPSync_SOPOrderlineID] = np.where((df_Mfg_All[cl_toOrderlineID] == 'INVALID'), np.nan,
                                                     np.where((df_Mfg_All[cl_toOrderlineID] != '000SCS_LOT'),
                                                              df_Mfg_All[cl_toOrderlineID],
                                                              'LPSS_' + df_Mfg_All['seq'].astype('str'))
                                                     )

    vdCommon.gfn_saveDf(df_Mfg_All, 'df_Mfg_All 1',False)
    # save_csv_file(df_Mfg_All, 'df_Mfg_All')
    
    # ================================================================================================================
    # ---------------------------------------------------------------------------------------
    # Mfg Plan 계획일 확인(2025.07.11) 추가----------------------------------------------------
    # 대상 : SOP Sync_Mfg OrderlineID like 'LPSM%' AND SOP Sync_SOP OrderlineID like 'LPSS%'
    # 조건 : BOM Effective (W Activity End Date) 보다 Mfg Plan 계획일이 늦은것들은 삭제, 동기화된 선적계획도 같이 삭제해야 함
    # 시점 : 최종데이타에서 처리
    # Mfg Plan 계획일 : FROM.[Time].[Week] 의 월요일
    # ---------------------------------------------------------------------------------------
    
    # W Activity End Date 조인
    df_in_WActivityEndDate.rename(columns={cl_Activity1:cl_fromActivity1, cl_Activity2:cl_fromActivity2, 
                                           cl_Activity3: cl_fromActivity3}, inplace=True)
    vdCommon.gfn_saveDf(df_in_WActivityEndDate, 'df_in_WActivityEndDate rename', False)
    df_Mfg_All = df_Mfg_All.merge(df_in_WActivityEndDate, 
                                  on=[cl_VersionName, cl_fromActivity1, cl_fromActivity2, cl_fromActivity3],how='left')
    df_Mfg_All[cl_WActivityEndDate].fillna(pd.to_datetime("2199-01-01"), inplace=True)
    
    # from.[Time].[Week] 의 Time.[Day] 조인
    df_in_TimeWeek.rename(columns={cl_Week: cl_fromWeek}, inplace=True)
    df_Mfg_All = df_Mfg_All.astype({cl_fromWeek: 'str'}, copy=True)
    df_Mfg_All = df_Mfg_All.merge(df_in_TimeWeek, on=[cl_fromWeek], how='left')
    del df_in_WActivityEndDate, df_in_TimeWeek
    
    df_Mfg_All["DEL_YN"] = np.where((df_Mfg_All[cl_Day] > df_Mfg_All[cl_WActivityEndDate]) &
                                     df_Mfg_All[cl_SOPSync_MfgOrderlineID].str.startswith('LPSM') &
                                     df_Mfg_All[cl_SOPSync_SOPOrderlineID].str.startswith('LPSS')
                                    , 'Y', 'N')
    vdCommon.gfn_saveDf(df_Mfg_All, 'df_Mfg_All 2', False)
    
    df_Mfg_All_DEL = df_Mfg_All[df_Mfg_All["DEL_YN"] == 'Y'].copy()
    df_Mfg_All     = df_Mfg_All[df_Mfg_All["DEL_YN"] != 'Y'].copy()
    vdCommon.gfn_saveDf(df_Mfg_All_DEL, 'df_Mfg_All_DEL 1', False)
    vdCommon.gfn_saveDf(df_Mfg_All, 'df_Mfg_All 3', False)
    del df_Mfg_All_DEL
    # ================================================================================================================
    # W Activity Priority Time Varying 값이 음수 인경우 삭제
    #Version.[Version Name]    Location.[Location]    Time.[Week]    Activity1.[Activity1]    Item.[Item]     Activity2.[Activity2]        Activity3.[Activity3]
    #Version.[Version Name]    from.[Location].[Location]    from.[Item].[Item]    from.[Time].[Week]     from.[Activity1].[Activity1]    from.[Activity2].[Activity2]    from.[Activity3].[Activity3]
    
    df_in_WActivityPrtTmV = df_in_WActivityPrtTmV.astype({cl_Week: 'str'}, copy=True)
    
    cList_left  = [cl_VersionName,  cl_fromLocation, cl_fromItem, cl_fromWeek, cl_fromActivity1, cl_fromActivity2, cl_fromActivity3]
    cList_Right = [cl_VersionName,  cl_Location,     cl_Item,     cl_Week,     cl_Activity1,     cl_Activity2,     cl_Activity3]
    df_Mfg_All = df_Mfg_All.merge(df_in_WActivityPrtTmV, left_on=cList_left, right_on=cList_Right, how='left')
    
    df_Mfg_All[cl_WActivityPriorityTimeVarying].fillna(value=0, inplace=True)
    df_Mfg_All["DEL_YN2"] = np.where((df_Mfg_All[cl_WActivityPriorityTimeVarying] < 0),'Y', 'N')
    
    df_Mfg_All_DEL = df_Mfg_All[df_Mfg_All["DEL_YN2"] == 'Y'].copy()
    df_Mfg_All     = df_Mfg_All[df_Mfg_All["DEL_YN2"] != 'Y'].copy()
    vdCommon.gfn_saveDf(df_Mfg_All_DEL, 'df_Mfg_All_DEL 2', False)
    vdCommon.gfn_saveDf(df_Mfg_All, 'df_Mfg_All 4', False)
    
    
    # ================================================================================================================
    
    ################################################################################################################
    # STEP 4 : output table create
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 4-1 : Final output table create')
    cList_OUT4 = [cl_VersionName, cl_fromItem, cl_fromLocation, cl_fromActivity1, cl_fromActivity2, cl_fromActivity3,
                  cl_fromWeek, cl_fromOrderlineID, cl_toLocation, cl_toWeek, cl_toActivity1, cl_toActivity2,
                  cl_toActivity3,
                  cl_toOrderlineID, cl_SOPSync_SOPQty,
                  cl_SOPSync_MfgOrderlineName, cl_SOPSync_SOPOrderlineName,
                  cl_SOPSync_MfgOrderlineID, cl_SOPSync_SOPOrderlineID]

    # 칼럼정리
    df_Mfg_All = df_Mfg_All[cList_OUT4].copy()

    # out Data 생성 :
    df_out_SOPSync = df_Mfg_All.copy()
    del df_Mfg_All

    row_count, cl_count = df_out_SOPSync.shape
    note(f'=====> Final df_out_SOPSync rows : {row_count}, column : {cl_count}')
    vdCommon.gfn_saveDf(df_out_SOPSync, 'df_out_SOPSync',False)

    if is_local:
        vdCommon.gfn_stepLog('=====> Output csv create')
        save_csv_file(df_out_SOPSync, 'df_out_SOPSync')
        print("datetime :", dt.datetime.now())

    vdCommon.gfn_stepLog('=====> STEP 4-2 : Final output table create End')
    
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())
    
    df_out_SOPSync = pd.DataFrame([], columns=[])

finally:
    vdCommon.gfn_stepLog('plugin Execution End ')
    
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    
    # logger.PrintDF(p_df=df_out_log, p_df_name="df_out_log", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    # logger.PrintDF(p_df=df_out_logDetail, p_df_name="df_out_logDetail", p_log_level=common.G_log_level.info(), p_format=1, p_row_num=10)
    
    logger.Finish()
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')
    logger.Step(p_step_desc=f'plugin Execution End')