"""

* 프로그램명
    - PY_UI_NewModelMap

* 내용
    - SET 조합(Rule ID)와 Material 간 Mapping List를 생성한다.
    - 위 Mapping List 에 해당하는 SET Code * Material Code의 Mapping Result 를 생성한다.

* Input
    - df_in_buyerGroupMapping
    - df_in_item
    # - df_in_newModelMap_Merge : New Model Map Rule(MG) + New Model Map(MG)
    - df_in_newModelMap : New Model Map(MG)

* Flow Summary
    Step1. df_in_buyerGroupMapping : Item.Buyer, Measure.[Buyer Group Mapping_Buyer Group] 으로 중복제거
    Step2. df_in_item 과 item 속성 값에 따른 Item 구하기
    Step4. Output Table 생성

* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2024.10.31 / syif1380.lee / Create
    - 2024.12.11 / syif1380.lee / df_in_buyerGroupMapping 의 MG 변경
    - 2025.01.20 / syif1380.lee / [Category].[Category].[Buyer Group Default]  추가
    - 2025.03.17 / syif1380.lee / vdCommon 공통 로그 작업
    - 2025.04.02 / syif1380.lee / 성능향상을 위한 로직 변경
    - 2025.06.17 / syif1380.lee / df_in_newModelMap 변경 , df_out_newModelMapBOM : [Rule].[Rule No] Grain 추가
    - 2025.07.01 / syif1380.lee / py 실행 scope 에 [Item Material].[Item Material] 제외 / 신승호p 요청
    - 2025.07.23 / syif1380.lee / BuyerGroup , All 일 경우 처리
    - 2026.01.12 / syif1380.lee / df_out_newModelMapMonitor , df_out_newModelMapBOMMonitor 추가

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table

  - 1.df_in_buyerGroupMapping :
        //Select ([Item].[Buyer] * [Buyer Group].[Buyer Group] ) on row,  () on column where {&CWVUI,Measure.[Buyer Group Map Flag]==True};
        // 변경 2024.12.11 syif1380.lee
        Select ( &CWVUI * [Item].[Buyer] * [Category].[Category].[Buyer Group Default] ) on row, ({Measure.[Buyer Group Mapping_Asn], Measure.[Buyer Group Mapping_Buyer Group]}) on column;

  - 2.df_in_item : Select ( Item.[Project] * Item.[Basic Name] * Item.[Inch] * Item.[Buyer] * &SETItem );
  - 3. df_in_newModelMap -> 2025.06.17 변경
      Select ([Version].[Version Name] * [Item].[Item] * [Project].[Project] * [Item Material].[Item Material] * [Rule].[Rule No] * [Inch].[Inch] * [Buyer Group].[Buyer Group] * [Basic Name].[Basic Name] ) on row,
    ({Measure.[New Model Map_BOM Type], Measure.[New Model Map_Base Qty], Measure.[New Model Map_HQ Dev Purchaser]
    , Measure.[New Model Map_HQ Purchaser], Measure.[New Model Map_User Spec]}) on column;

* Output Table :
   - df_out_newModelMapBOM : (MG) New Model Map BOM
       Select (&CWVUI * [Item].[Item] * [Item Material].[Item Material] * [Rule].[Rule No]) on row,
        ({Measure.[New Model Map BOM_BOM Type],
        Measure.[New Model Map BOM_Base Qty],
        Measure.[New Model Map BOM_HQ Dev Purchaser],
        Measure.[New Model Map BOM_HQ Purchaser],
        Measure.[New Model Map BOM_User Spec]}) on column limit 10;

   -  New Model Map -> New Model Map Monitor (추가 2026.01.12)
   - df_out_newModelMapMonitor : df_in_newModelMap 의 데이터 입력

   - New Model Map BOM -> New Model Map BOM Monitor (추가 2026.01.12)
   - df_out_newModelMapBOMMonitor : df_out_newModelMapBOM 의 데이터 입력

* RUN 스크립트
    EXEC plugin instance [PY_UI_NewModelMap]
    for measures {[New Model Map BOM_BOM Type]}
    using scope (&CWVUI*[Rule].[Rule No]{{#filter Rule}}) /* [Item Material].[Item Material]{{#filter Material}} scope 에서 제외 2025.07.01 신승호P요청 */
    using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};

    # 실행구문
    EXEC plugin instance [PY_UI_NewModelMap]
    for measures {[New Model Map BOM_BOM Type]}
    using scope (&CWVUI*[Rule].[Rule No].[0001])  /* [Item Material].[Item Material].[BN96-32516A] scope 에서 제외 2025.07.01 신승호P요청 */
    using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};


"""
########################################################################################################################
# NSCMCommon - start
########################################################################################################################
# import gc
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
str_instance = 'PY_UI_NewModelMap'

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
    # Value 변수 선언
    PARAM_OUTVERSION_VALUE = "CWV_MP"

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

    # 데이터 파일 읽기
    if common.gfn_get_isLocal():
        df_in_buyerGroupMapping = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_buyerGroupMapping.csv", encoding="UTF-8")
        df_in_item = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_item.csv", encoding="UTF-8")
        # converters={'Rule.[Rule No]': str} >> Rule.[Rule No] 열을 문자열로 변환 2024.12.11 syif1380.lee
        df_in_newModelMap = pd.read_csv("df_in_newModelMap.csv", low_memory=False, encoding="UTF-8",
                                        converters={'Rule.[Rule No]': str})
        pDetailLogFlag = "N"

    ################################################################################################################
    # input Table log
    ################################################################################################################
    # 입력 변수 확인용 로그
    vdCommon.gfn_saveDf(df_in_buyerGroupMapping, "df_in_buyerGroupMapping", True)
    vdCommon.gfn_saveDf(df_in_item, "df_in_item", True)
    vdCommon.gfn_saveDf(df_in_newModelMap, "df_in_newModelMap", True)
    vdCommon.gfn_stepLog('=====> STEP1 Start 0')
    if df_in_buyerGroupMapping.empty:
        raise Exception("Exception: df_in_buyerGroupMapping is empty")

    if df_in_item.empty:
        raise Exception("Exception: df_in_item is empty")

    if df_in_newModelMap.empty:
        raise Exception("Exception: df_in_newModelMap is empty")

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수 선언 - Dimension
    VersionName = 'Version.[Version Name]'
    MappingBuyerGroup = 'Buyer Group Mapping_Buyer Group'      # Buyer Group Master

    RuleNo = 'Rule.[Rule No]'
    ItemMaterial = 'Item Material.[Item Material]'

    ItemInch = 'Item.[Inch]'
    ItemProject = 'Item.[Project]'
    ItemBasic = 'Item.[Basic Name]'
    ItemBuyer = 'Item.[Buyer]'
    ItemItem = 'Item.[Item]'

    ##############################################
    # 2026.06.16 추가
    Project     = 'Project.[Project]'           # RuleProject
    BuyerGroup  = 'Buyer Group.[Buyer Group]'   # RuleBuyerGroup
    Inch        = 'Inch.[Inch]'                 # RuleInch
    BasicName   = 'Basic Name.[Basic Name]'     # RuleBasic
    ###############################################

    NewModelMap_BaseQty = 'New Model Map_Base Qty'
    NewModelMap_BOMType = 'New Model Map_BOM Type'
    NewModelMap_UserSpec = 'New Model Map_User Spec'
    NewModelMap_HQPurchaser = 'New Model Map_HQ Purchaser'
    NewModelMap_HQDevPurchaser = 'New Model Map_HQ Dev Purchaser'

    NewModelMapBOM_BaseQty = 'New Model Map BOM_Base Qty'
    NewModelMapBOM_BOMType = 'New Model Map BOM_BOM Type'
    NewModelMapBOM_UserSpec = 'New Model Map BOM_User Spec'
    NewModelMapBOM_HQPurchaser = 'New Model Map BOM_HQ Purchaser'
    NewModelMapBOM_HQDevPurchaser = 'New Model Map BOM_HQ Dev Purchaser'

    ######################## 2026.01.12 추가 ( New Model Map Monitor , New Model Map BOM Monitor )
    BOMType = 'BOM Type.[BOM Type]'
    NewModelMapMonitor_BaseQty = 'New Model Map Monitor_Base Qty'
    NewModelMapMonitor_UserSpec = 'New Model Map Monitor_User Spec'
    NewModelMapMonitor_Count = 'New Model Map Monitor_Count'
    NewModelMapMonitor_Material = 'New Model Map Monitor_Material'

    NewModelMapBOMMonitor_BaseQty = 'New Model Map BOM Monitor_Base Qty'
    NewModelMapBOMMonitor_UserSpec = 'New Model Map BOM Monitor_User Spec'
    NewModelMapBOMMonitor_Count = 'New Model Map BOM Monitor_Count'
    NewModelMapBOMMonitor_Material = 'New Model Map BOM Monitor_Material'

    # New Model Map Monitor
    new_model_map_monitor_columns = [
        VersionName, RuleNo, ItemItem, Project, Inch, BasicName, ItemMaterial, BuyerGroup, BOMType,
        NewModelMapMonitor_BaseQty, NewModelMapMonitor_UserSpec, NewModelMapMonitor_Count, NewModelMapMonitor_Material,
    ]

    # New Model Map BOM Monitor
    new_model_map_bom_monitor_columns = [
        VersionName, ItemItem, ItemMaterial, RuleNo, BOMType,
        NewModelMapBOMMonitor_BaseQty, NewModelMapBOMMonitor_UserSpec, NewModelMapBOMMonitor_Count, NewModelMapBOMMonitor_Material,
    ]
    ################################################################################################################

    ################################################################################################################
    # STEP 1 : df_in_item 과 item 속성 값에 따른 Item 구하기
    # - 전처리 : null 값 처리, 비교하기 위해 String 변환
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP1 Start')
    df_in_item[ItemInch] = df_in_item[ItemInch].fillna('').astype(str)
    df_in_newModelMap[Inch] = df_in_newModelMap[Inch].fillna('').astype(str)
    df_in_item = df_in_item.fillna('').astype(str)
    df_in_newModelMap[Project] = df_in_newModelMap[Project].fillna('-').astype(str)
    df_in_newModelMap[BasicName] = df_in_newModelMap[BasicName].fillna('-').astype(str)
    df_in_newModelMap[Inch] = df_in_newModelMap[Inch].fillna('-').astype(str)
    df_in_newModelMap[ItemItem] = df_in_newModelMap[ItemItem].fillna('-').astype(str)
    df_in_newModelMap[NewModelMap_HQPurchaser] = df_in_newModelMap[NewModelMap_HQPurchaser].fillna('').astype(str)
    df_in_newModelMap[NewModelMap_HQDevPurchaser] = df_in_newModelMap[NewModelMap_HQDevPurchaser].fillna('').astype(str)
    df_in_newModelMap[RuleNo] = df_in_newModelMap[RuleNo].astype(str)

    ####################################################################################################################
    def map_model_to_items(df_model, df_item, df_buyer):
        vdCommon.gfn_stepLog('=====> map_model_to_items 시작')

        # buyergp → [buyer 리스트] 딕셔너리 생성, 사전 매핑
        buyergp_to_buyers = df_buyer.groupby(MappingBuyerGroup)[ItemBuyer].apply(list).to_dict()

        # print("딕셔너리:",buyergp_to_buyers)

        # 결과 저장할 리스트
        results = []

        # 백터화된 조건 검색을 위한 미리 처리된 DataFrame
        df_item[ItemBuyer] = df_item[ItemBuyer].astype('category')  # 메모리 최적화

        # 필터링 실행
        for _, model_row in df_model.iterrows():

            version = model_row[VersionName]
            mtrl = model_row[ItemMaterial]
            ruleNo = model_row[RuleNo]

            # vdCommon.gfn_stepLog('=====> mtrl : '+mtrl)
            # vdCommon.gfn_stepLog('=====> buyerGroup : ' + buyerGroup)
            # vdCommon.gfn_stepLog('=====> ruleNo : ' + ruleNo)

            ############################################################################################################
            # buyer 필터링
            ############################################################################################################
            buyerGroup_cond = model_row[BuyerGroup]
            if buyerGroup_cond not in ['All', 'ALL', '-']:
                # 사전에서 buyer 리스트 바로 가져오기
                buyers = buyergp_to_buyers.get(model_row[BuyerGroup], [])
                if not buyers:
                    continue
                # buyer group -> buyer 리스트로 필터
                df_item_filtered = df_item[df_item[ItemBuyer].isin(buyers)]
            else:
                df_item_filtered = df_item
            # vdCommon.gfn_saveDf(df_item_filtered, "df_item_filtered_____buyer", True)

            ############################################################################################################
            # Project 필터링
            ############################################################################################################
            project_cond = model_row[Project]
            if project_cond not in ['All', 'ALL', '-']:
                if project_cond.startswith('%') or project_cond.endswith('%'):
                    keyword = project_cond.strip('%')
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemProject].str.contains(keyword, case=False, na=False)]
                else:
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemProject] == project_cond]
            # vdCommon.gfn_saveDf(df_item_filtered, "df_item_filtered_____Project", True)

            ############################################################################################################
            # Inch 필터링
            ############################################################################################################
            inch_cond = model_row[Inch]
            if inch_cond not in ['All', 'ALL', '-']:
                if inch_cond.startswith('%') or inch_cond.endswith('%'):
                    keyword_inch = inch_cond.strip('%')
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemInch].str.contains(keyword_inch, case=False, na=False)]
                else:
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemInch] == inch_cond]
            # vdCommon.gfn_saveDf(df_item_filtered, "df_item_filtered_____Inch", True)

            ############################################################################################################
            # Basic Name 필터링
            ############################################################################################################
            basic_cond = model_row[BasicName]
            if basic_cond not in ['All', 'ALL', '-']:
                if basic_cond.startswith('%') or basic_cond.endswith('%'):
                    keyword_basic = basic_cond.strip('%')
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemBasic].str.contains(keyword_basic, case=False, na=False)]
                else:
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemBasic] == basic_cond]
            # vdCommon.gfn_saveDf(df_item_filtered, "df_item_filtered_____BasicName", True)

            ############################################################################################################
            # Item 필터링
            ############################################################################################################
            item_cond = model_row[ItemItem]
            if item_cond not in ['All', 'ALL', '-']:
                if item_cond.startswith('%') or item_cond.endswith('%'):
                    keyword_item = item_cond.strip('%')
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemItem].str.contains(keyword_item, case=False, na=False)]
                else:
                    df_item_filtered = df_item_filtered[df_item_filtered[ItemItem] == item_cond]
            # vdCommon.gfn_saveDf(df_item_filtered, "df_item_filtered_____Model(item)", True)

            ############################################################################################################
            # 각 item에 대해 Material 값을 기준으로 결과 저장
            ############################################################################################################
            for item in df_item_filtered[ItemItem]:
                results.append({VersionName: version, ItemMaterial:mtrl, ItemItem: item, RuleNo:ruleNo,
                # results.append({VersionName: version, ItemMaterial: mtrl, ItemItem: item,
                                NewModelMap_BaseQty: model_row[NewModelMap_BaseQty],
                                NewModelMap_BOMType: model_row[NewModelMap_BOMType],
                                NewModelMap_UserSpec: model_row[NewModelMap_UserSpec],
                                NewModelMap_HQPurchaser: model_row[NewModelMap_HQPurchaser],
                                NewModelMap_HQDevPurchaser: model_row[NewModelMap_HQDevPurchaser]
                                })

        # 결과 DataFramed 생성
        return pd.DataFrame(results)

    vdCommon.gfn_stepLog('=====> STEP2 End')

    # 함수 호출 및 결과 출력
    vdCommon.gfn_stepLog('=====> def 함수 호출')
    df_result_test = map_model_to_items(df_in_newModelMap, df_in_item, df_in_buyerGroupMapping)

    # 함수 호출 후 결과 df 없을 경우
    if df_result_test.empty:
        raise Exception("Exception: df_result_test is empty")

    vdCommon.gfn_stepLog('=====> def 함수 호출 End')

    vdCommon.gfn_saveDf(df_result_test, "df_result_test", True)
    # 컬럼명 변경
    df_result_test.rename(columns={NewModelMap_BaseQty: NewModelMapBOM_BaseQty,
                              NewModelMap_BOMType: NewModelMapBOM_BOMType,
                              NewModelMap_UserSpec: NewModelMapBOM_UserSpec,
                              NewModelMap_HQPurchaser: NewModelMapBOM_HQPurchaser,
                              NewModelMap_HQDevPurchaser: NewModelMapBOM_HQDevPurchaser
                              }, inplace=True)

    # output : df_result 필요 컬럼 정의
    df_out_newModelMapBOM = df_result_test[
        [VersionName, ItemItem, ItemMaterial, RuleNo, NewModelMapBOM_BaseQty, NewModelMapBOM_BOMType, NewModelMapBOM_UserSpec,
         NewModelMapBOM_HQPurchaser, NewModelMapBOM_HQDevPurchaser]]

    vdCommon.gfn_stepLog('=====> New Model Map BOM 생성')

    ################################  New Model Map Monitor 로직 추가 2026.01.12 #######################################

    ####################################################################################################################
    # output : New Model Map Monitor > df_out_newModelMapMonitor 추가 2026.01.12
    ####################################################################################################################
    if not df_in_newModelMap.empty:
        df_mapMonitor = df_in_newModelMap.copy()
        df_mapMonitor[NewModelMapMonitor_Count] = 1
        df_mapMonitor[NewModelMapMonitor_Material] = df_mapMonitor[ItemMaterial]
        df_mapMonitor.rename(columns={NewModelMap_BOMType: BOMType,
                                      NewModelMap_BaseQty: NewModelMapMonitor_BaseQty,
                                      NewModelMap_UserSpec: NewModelMapMonitor_UserSpec
                                  }, inplace=True)
        df_out_newModelMapMonitor = df_mapMonitor[new_model_map_monitor_columns]
        # vdCommon.gfn_saveDf(df_out_newModelMapMonitor, "df_out_newModelMapMonitor", True)

    vdCommon.gfn_stepLog('=====> New Model Map Monitor 생성')
    ####################################################################################################################
    # output : New Model Map BOM Monitor > df_out_newModelMapBOMMonitor 추가 2026.01.12
    ####################################################################################################################
    if not df_out_newModelMapBOM.empty:
        df_mapBOMMonitor = df_out_newModelMapBOM.copy()
        df_mapBOMMonitor[NewModelMapBOMMonitor_Count] = 1
        df_mapBOMMonitor[NewModelMapBOMMonitor_Material] = df_mapBOMMonitor[ItemMaterial]
        df_mapBOMMonitor.rename(columns={NewModelMapBOM_BOMType: BOMType,
                                      NewModelMapBOM_BaseQty: NewModelMapBOMMonitor_BaseQty,
                                      NewModelMapBOM_UserSpec: NewModelMapBOMMonitor_UserSpec
                                      }, inplace=True)
        df_out_newModelMapBOMMonitor = df_mapBOMMonitor[new_model_map_bom_monitor_columns]
        # vdCommon.gfn_saveDf(df_out_newModelMapBOMMonitor, "df_out_newModelMapBOMMonitor", True)

    vdCommon.gfn_stepLog('=====> New Model Map BOM Monitor 생성')
    ####################################################################################################################

    ####################################################################################################################
    # 최종 Output 테이블 만들기
    ####################################################################################################################
    vdCommon.gfn_saveDf(df_out_newModelMapBOM, "df_out_newModelMapBOM", True)
    vdCommon.gfn_saveDf(df_out_newModelMapMonitor, "df_out_newModelMapMonitor", True)
    vdCommon.gfn_saveDf(df_out_newModelMapBOMMonitor, "df_out_newModelMapBOMMonitor", True)

    vdCommon.gfn_stepLog('plugin Execution End')

except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    # ouput Table 선언
    df_out_newModelMapBOM = pd.DataFrame([], columns=[])
    df_out_newModelMapMonitor = pd.DataFrame([], columns=[])
    df_out_newModelMapBOMMonitor = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    vdCommon.gfn_stepLog('=====> Batch end')
