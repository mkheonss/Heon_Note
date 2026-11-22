"""

* 프로그램명
    - PY_UI_BODListW_SupplyFilterSET

* 내용
    - SET 전용
    #### BOD Item
    -  To Site * Item 하나에 대해서,
       1.(이원화 공급지)
        1.1 (이원화 공급지) 복수의 From Site Filtering : To Site 와 From Site => 1:N 인 경우
        1.2 (이원화 공급지) To Site 와 From Site => 1:1 , TP Mode 가 복수개일 경우 (2025.11.20 신승호P요청)
       2.(일원화 공급지) 복수의 TP Mode Filtering :   To Site 와 From Site => 1:1 인 경우(TP Mode가 복수)
       결론: From Site가 1개인지, N개인지를 보고, From Site 가 1개이면 일원화 공급지임(TP Mode가 복수개인 것만 Batch 될 것이므로)
    - 하기 상세
      1.Item(AA) * To Site(S701) 의 경우, 일원화 공급지(From Site가 P701 한개, TP Mode 는 복수개)
      2.Item(BB) * To Site(S701) 의 경우, 이원화 공급지(From Site가 P551과 P701로 2개)
      3.Item(CC) * To Site(S701) 의 경우, 이원화 공급지(From Site가 P551과 P701로 2개)

    #### BOD Prod SET
     - To Site * Item.Product Group
     1.(이원화 공급지)
        1.1 (이원화 공급지) 복수의 From Site Filtering : To Site 와 From Site => 1:N 인 경우
        1.2 (이원화 공급지) To Site 와 From Site => 1:1 , TP Mode 가 복수개일 경우 (2025.11.21 신승호P요청)

* Input
    - BOD Prod SET  : df_in_BODProdSET
    - BOD Item  : df_in_BODItem

* Flow Summary
    Step1.
    Step2.
    Step4. Output Table 생성

* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2025.07.25 / syif1380.lee / Create
    - 2025.11.21 / syif1380.lee / 이원화 공급지 내용 변경: to site, from site 가 1:1 이여도 tpmode 가 1개이상일 경우도 이원화
      - BOD Prod SET Prty_Supply Filter , BOD Item Prty_Supply Filter 의 Trans Mode 그레인 추가 됨 (신승호P)
    - 2025.12.10 / syif1380.lee / Input Table 의 [Location].[Location], [Sub Location].[Sub Location] 으로 바꾸고 PY 호출시 Namedset 으로 변경 함
    - 2025.12.19 / syif1380.lee / Input Table : df_in_BODProdSET : BOD Prod SET W => BOD Prod SET W SUB 대상MG 변경
                                                df_in_BODItem : BOD Item W => BOD Item W SUB 대상MG 변경
    - 2026.01.27 / syif1380.lee / Input Table 데이터 없을 경우 Header 생성하여 오류 방지

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table
 - df_in_BODProdSET
    #  2025.12.19 변경 이전
    #  Select ([Version].[Version Name] * [Location].[Location] * [Item].[Product Group] * &MDMHorizon * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    # ({Measure.[BOD Prod SET W_BOD LT], Measure.[BOD Prod SET W_Priority], Measure.[BOD Prod SET W_Shipment LT]}) on column;

    #  2025.12.19 변경 (Input Table)
     Select ([Version].[Version Name] * [Location].[Location] * [Item].[Product Group] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    ({ Measure.[BOD Prod SET W Sub_BOD Valid] }) on column where {Measure.[BOD Prod SET W Sub_BOD Valid] == "Y"};

    # IBPL Query
    # Select ( &CWVUI * &NSUILocationDC.unionwith(&MFStageSETLocation) * [Item].[Product Group] * &NSUISubLocationDC * [Trans Mode].[Trans Mode] ) on row,
    # ({ Measure.[BOD Prod SET W Sub_BOD Valid]}) on column where {Measure.[BOD Prod SET W Sub_BOD Valid] == "Y"};

 - df_in_BODItem
    #  2025.12.19 변경 이전
    # Select ([Version].[Version Name] * &SETItem * &MDMHorizon * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    # ({Measure.[BOD Item W_Prty], Measure.[BOD Item W_BOD LT], Measure.[BOD Item W_Shipment LT]}) on column;

    #  2025.12.19 변경 (Input Table)
    Select ([Version].[Version Name] * &SETItem * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    ({ Measure.[BOD Item W Sub_BOD Valid] }) on column where { Measure.[BOD Item W Sub_BOD Valid] == "Y" };

    # IBPL Query
    # Select ( &CWVUI * &SETItem  * &NSUILocationDC.unionwith(&MFStageSETLocation) * &NSUISubLocationDC * [Trans Mode].[Trans Mode] ) on row,
    # ({Measure.[BOD Item W Sub_BOD Valid]}) on column
    # where { Measure.[BOD Item W Sub_BOD Valid] == "Y" };

* Data 삭제
    delete data for model [BOD Product SET Prty] where {&CWVUI};
    delete data for model [BOD Item Prty] where {&CWVUI * &SETItem};

* Output Table :
   - df_out_BODProdSET :
   Select ( &CWVUI * [Location].[Location].[P306] * [Item].[Product Group] * [Sub Location].[Sub Location].[S623]  ) on row, ({Measure.[BOD Prod SET Prty_Supply Filter]}) on column limit 1000;

   - df_out_BODItem  :
    Select ( &CWVUI * [Location].[Location].[P306] * [Item].[Item] * [Sub Location].[Sub Location].[S623] ) on row, ({Measure.[BOD Item Prty_Supply Filter]}) on column limit 1000;

* RUN 스크립트

    ## 실행 (SET)
    - EXEC plugin instance [PY_UI_BODListW_SupplyFilterSET] for measures {[BOD Item Prty_Supply Filter]}
        using scope ( &CWVUI * &MFStageSETLocation.unionwith(&NSUILocationDC) * &NSUISubLocationDC )
        using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

"""
########################################################################################################################
# NSCMCommon - start
########################################################################################################################
import traceback
import pandas as pd
import os.path
import numpy as np
import warnings
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
########################################################################################################################
# NSCMCommon - end
########################################################################################################################

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BODListW_SupplyFilterSET'

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

    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

    # 로컬일 경우 버전 처리
    # 데이터 파일 읽기
    if common.gfn_get_isLocal():
        # 로컬일 경우 버전 처리
        paramOutVersion = PARAM_OUTVERSION_VALUE
        df_in_BODProdSET = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_BODProdSET.csv", encoding="UTF-8")
        df_in_BODItem = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_BODItem.csv", encoding="UTF-8")
        pDetailLogFlag = "N"

    ################################################################################################################
    # input Table log
    ################################################################################################################
    # 입력 변수 확인용 로그
    vdCommon.gfn_saveDf(df_in_BODProdSET, "df_in_BODProdSET", True)
    vdCommon.gfn_saveDf(df_in_BODItem, "df_in_BODItem", True)

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수 선언 - Dimension
    VersionName = 'Version.[Version Name]'
    ItemItem = 'Item.[Item]'
    Location = 'Location.[Location]'
    SubLocation = 'Sub Location.[Sub Location]'
    TransMode = 'Trans Mode.[Trans Mode]'
    ItemProductGroup = 'Item.[Product Group]'
    BodItemPrty_SupplyFilter = 'BOD Item Prty_Supply Filter'      # BOD Item
    BodProdSetPrty_SupplyFilter = 'BOD Prod SET Prty_Supply Filter' # BOD Prod SET

    ################################################################################################################
    # STEP 1 : To Site * Item.Item 하나에 대해서 (BOD Item) , To Site * Item.Product Group
    # 1.(이원화 공급지) 복수의 From Site Filtering : To Site 와 From Site = 1:N 인 경우 or 1:1 이여도 TPMode 가 1개이상인 경우
    # 2.(일원화 공급지) 복수의 TP MOde Filtering   : To Site 와 From Site = 1:1 인 경우
    # 결론 : From Site가 1개인지, N개인지를 보고, From Site가 1개이면 일원화 공급지임 & From Site 1개여도 TPMode가 1개일 경우
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 Start')
    ####################################################################################################################
    # STEP 1 : Bod Prod SET : 중복 제거된 기준 데이터 , 고유 Location 기준 개수 계산, 고유 Tp Mode 기준 개수 계산
    ####################################################################################################################
    if not df_in_BODProdSET.empty:
        # STEP 1-1 : Bod Prod SET : 중복 제거된 기준 데이터
        df_bodProdSetUnique = df_in_BODProdSET[[VersionName, Location, SubLocation, TransMode, ItemProductGroup]].drop_duplicates()
        # STEP 1-2 : Bod Prod SET : 고유 Location 기준 개수 계산
        bodProdSet_loc_counts = df_bodProdSetUnique.groupby([VersionName, SubLocation, ItemProductGroup])[
            Location].nunique().reset_index(name='loc_count')
        # STEP 1-3 : Bod Prod SET : 고유 Tp Mode 기준 개수 계산
        bodProdSet_tpmode_counts = df_bodProdSetUnique.groupby([VersionName, Location, SubLocation, ItemProductGroup])[
            TransMode].nunique().reset_index(name='tpmode_count')
        # STEP 1-4 : Bod Prod SET : loc_count, tpmode_count 머지
        df_out_BODProdSET = (
            df_bodProdSetUnique.merge(bodProdSet_loc_counts[[VersionName, SubLocation, ItemProductGroup, 'loc_count']]
                                      , on=[VersionName, SubLocation, ItemProductGroup], how='left')
            .merge(bodProdSet_tpmode_counts[[VersionName, SubLocation, Location, ItemProductGroup, 'tpmode_count']]
                   , on=[VersionName, SubLocation, Location, ItemProductGroup], how='left')
        )
        vdCommon.gfn_saveDf(df_out_BODProdSET, "df_out_BODProdSET_count_Merge", True)

        # --------------------------------------------------------------------------------------------------------------
        # # STEP 1-5  : supplyFilter  컬럼 생성
        # 조건 : BOD Prod SET
        # - 같은 (VersionName, SubLocation, ItemProductGroup) 에서 Location 이 2개 이상이거나
        # - 같은 (VersionName, SubLocation, ItemProductGroup, Location) 에서 TransMode 가 2개이상이면 multi
        # --------------------------------------------------------------------------------------------------------------
        # BOD Prod SET : 메모리 효율 향상 변경 (2025.12.22)
        df_out_BODProdSET[BodProdSetPrty_SupplyFilter] = "Single Supply"
        maskProd = (df_out_BODProdSET['loc_count'] > 1) | (df_out_BODProdSET['tpmode_count'] > 1)
        df_out_BODProdSET.loc[maskProd, BodProdSetPrty_SupplyFilter] = "Multi Supply"
        df_out_BODProdSET[BodProdSetPrty_SupplyFilter] = df_out_BODProdSET[BodProdSetPrty_SupplyFilter].astype("category")

        df_out_BODProdSET = df_out_BODProdSET[
            [VersionName, Location, SubLocation, ItemProductGroup, TransMode, BodProdSetPrty_SupplyFilter]]
    else:
        df_out_BODProdSET = pd.DataFrame(columns=[VersionName, Location, SubLocation, ItemProductGroup, TransMode, BodProdSetPrty_SupplyFilter])

    vdCommon.gfn_stepLog('=====> STEP 1 End')
    ####################################################################################################################
    # STEP 2 : Bod Item : 중복 제거된 기준 데이터 , 고유 Location 기준 개수 계산, 고유 Tp Mode 기준 개수 계산
    ####################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 Start')
    if not df_in_BODItem.empty:
        # STEP 2-1 : Bod Item : 중복 제거된 기준 데이터
        df_bodItemUnique = df_in_BODItem[[VersionName, Location, SubLocation, TransMode, ItemItem]].drop_duplicates()
        # STEP 2-2 : Bod Item : 고유 Location 기준 개수 계산
        bodItem_loc_counts = df_bodItemUnique.groupby([VersionName, SubLocation, ItemItem])[Location].nunique().reset_index(name='loc_count')
        # STEP 2-3 : Bod Item : 고유 Tp Mode 기준 개수 계산
        bodItem_tpmode_counts = df_bodItemUnique.groupby([VersionName, Location, SubLocation, ItemItem])[
            TransMode].nunique().reset_index(name='tpmode_count')
        # STEP 2-4 : Bod Item : loc_count, tpmode_count 머지
        df_out_BODItem = (
            df_bodItemUnique.merge(bodItem_loc_counts[[VersionName, SubLocation, ItemItem, 'loc_count']]
                                   , on=[VersionName, SubLocation, ItemItem], how='left')
            .merge(bodItem_tpmode_counts[[VersionName, SubLocation, Location, ItemItem, 'tpmode_count']]
                   , on=[VersionName, SubLocation, Location, ItemItem], how='left')
        )

        # --------------------------------------------------------------------------------------------------------------
        # # STEP 2-5 : supplyFilter  컬럼 생성
        # 조건 : BOD Item
        # - 같은 (VersionName, SubLocation, ItemItem) 에서 Location 이 2개 이상이거나
        # - 같은 (VersionName, SubLocation, ItemItem, Location) 에서 TransMode 가 2개이상이면 multi
        # --------------------------------------------------------------------------------------------------------------
        # BOD Item : 메모리 효율 향상 변경 (2025.12.22)
        df_out_BODItem[BodItemPrty_SupplyFilter] = "Single Supply"
        maskItem = (df_out_BODItem['loc_count'] > 1) | (df_out_BODItem['tpmode_count'] > 1)
        df_out_BODItem.loc[maskItem, BodItemPrty_SupplyFilter] = "Multi Supply"
        df_out_BODItem[BodItemPrty_SupplyFilter] = df_out_BODItem[BodItemPrty_SupplyFilter].astype("category")

        df_out_BODItem = df_out_BODItem[
            [VersionName, Location, SubLocation, ItemItem, TransMode, BodItemPrty_SupplyFilter]]
    else:
        df_out_BODItem = pd.DataFrame(
            columns=[VersionName, Location, SubLocation, ItemItem, TransMode, BodItemPrty_SupplyFilter])

    vdCommon.gfn_stepLog('=====> STEP 2 End')

    ################################################################################################################
    # 최종 Output 테이블 만들기
    ################################################################################################################
    vdCommon.gfn_saveDf(df_out_BODProdSET, "df_out_BODProdSET", True)
    vdCommon.gfn_saveDf(df_out_BODItem, "df_out_BODItem", True)

    vdCommon.gfn_stepLog('=====> STEP End')

except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    # ouput Table 선언
    df_out_BODItem = pd.DataFrame([], columns=[])
    df_out_BODProdSET = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    vdCommon.gfn_stepLog('=====> Batch end')
