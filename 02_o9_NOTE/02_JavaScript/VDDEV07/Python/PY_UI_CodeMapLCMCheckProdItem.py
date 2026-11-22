"""

* 프로그램명
    - PY_UI_CodeMapLCMCheckProdItem

* 내용
    - LCM BOD & Product Copy
    - Code Map LCM 중 Status가 "COM" 이 아닌 것중 LCM Code Map 의 To Item 과 비교 후 Item 이 Prod Item 의 단건, 다건 처리 로직

* Input
- df_in_lcmCodeMap :
- df_in_codeMapLCM_Main :

* Flow Summary
    Step1. df_in_lcmCodeMap 사전 처리
    Step2. df_in_lcmCodeMap, df_in_codeMapLCM_Main 병합
    Step3. 단일 값 세팅
    Step4. 다건 값 세팅

* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2025.05.09 / syif1380.lee / Create
    - 2026.01.27 / syif1380.lee / Input Table 데이터 없을 경우 Header 생성하여 오류 방지

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table

  - df_in_lcmCodeMap :
    Select ( [Version].[Version Name] * [Location].[Location] * [Item].[Item] * [To Item].[To Item] ) where { Measure.[LCM Code MAP_Status] != "COM" };

    (IBPL실행쿼리-sample test data)
    Select ( &CWVUI * [Location].[Location].[P306LCD] * [Item].[Item] * [To Item].[To Item] ) where { Measure.[LCM Code MAP_Status] != "COM" };

  - df_in_codeMapLCM_Main :
   Select ( [Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] ) on row,
    ({Measure.[Code Map LCM_Map Status], Measure.[Code Map LCM_Prod Item], Measure.[Code Map LCM_Prod Item_Sys] ,Measure.[Code Map LCM_Valid Flag]}) on column
    where {Measure.[Code Map LCM_Valid Flag] == "Y" ,Measure.[Code Map LCM_Map Status] != "COM"};

    (IBPL실행쿼리-sample test data)
    Select (&CWVUI * [Location].[Location] * [Item].[Item] * [Sub Location].[Sub Location] ) on row,
    ({Measure.[Code Map LCM_Map Status], Measure.[Code Map LCM_Prod Item], Measure.[Code Map LCM_Prod Item_Sys] ,Measure.[Code Map LCM_Valid Flag]}) on column
    where {Measure.[Code Map LCM_Valid Flag] == "Y" ,Measure.[Code Map LCM_Map Status] != "COM"};

* Output Table :
   - df_out_codeMapLCM :


* 테스트 스크립트
 /* Validation 호출 (PY_UI_CodeMapLCMCheckProdItem) */
 EXEC plugin instance [PY_UI_CodeMapLCMCheckProdItem] for measures {[Code Map LCM_Valid Flag]} using scope ( &CWVUI ) using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

"""

########################################################################################################################
# NSCMCommon - start
########################################################################################################################
import traceback
import pandas as pd
import numpy as np
import os.path
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
str_instance = 'PY_UI_CodeMapLCMCheckProdItem'

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

    # 로컬일 경우 버전 처리
    # 데이터 파일 읽기
    if common.gfn_get_isLocal():
        df_in_lcmCodeMap = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_lcmCodeMap.csv", encoding="UTF-8")
        df_in_codeMapLCM_Main = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_codeMapLCM_Main.csv", encoding="UTF-8")
        pDetailLogFlag = "N"

    # 입력 변수 확인용 로그
    vdCommon.gfn_saveDf(df_in_lcmCodeMap, "df_in_lcmCodeMap", True)
    vdCommon.gfn_saveDf(df_in_codeMapLCM_Main, "df_in_codeMapLCM_Main", True)

    if df_in_codeMapLCM_Main.empty or df_in_lcmCodeMap.empty :
        vdCommon.gfn_stepLog('=====> 입력 데이터가 비어 있어 처리할 수 없습니다.')
        raise Exception("Cannot proceed because the input data is empty.")  # 입력 데이터가 비어 있어 처리할 수 없습니다

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수 선언 - Dimension
    VersionName = 'Version.[Version Name]'
    Location = 'Location.[Location]'
    SubLocation = 'Sub Location.[Sub Location]'
    Item = 'Item.[Item]'
    ToItem = 'To Item.[To Item]'

    # 컬럼 변수 선언 - Code Map LCM (Measure Group)
    CodeMapLCM_ProdItem = 'Code Map LCM_Prod Item'
    CodeMapLCM_ProdItem_Sys = 'Code Map LCM_Prod Item_Sys'
    CodeMapLCM_ValidFlag = 'Code Map LCM_Valid Flag'
    CodeMapLCM_MapStatus = 'Code Map LCM_Map Status'

    ################################################################################################################
    # STEP 1 :  df_in_lcmCodeMap 사전 처리
    #           - version , Location, To Item 기준으로 Item List 생성
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP1 Start')
    df_in_lcmCodeMap_grouped = (
        df_in_lcmCodeMap.groupby([VersionName, Location, ToItem])[Item]
        .agg(list)
        .reset_index()
        .rename(columns={ToItem:Item, Item : 'Item_list'})
    )
    vdCommon.gfn_stepLog('=====> STEP1 End')
    vdCommon.gfn_saveDf(df_in_lcmCodeMap_grouped, "step1_df_in_lcmCodeMap_grouped", True)

    ################################################################################################################
    # STEP 2 :  df_in_lcmCodeMap, df_in_codeMapLCM_Main 병합
    #           - version , Location, Item 기준으로 df_in_codeMapLCM 에 Item_list 붙이기
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP2 Start')
    df_joined = pd.merge(df_in_codeMapLCM_Main, df_in_lcmCodeMap_grouped, on=[VersionName, Location, Item], how='inner')

    vdCommon.gfn_stepLog('=====> STEP2 End')
    vdCommon.gfn_saveDf(df_joined, "step2_df_joined", True)

    if not df_joined.empty:
        ################################################################################################################
        # STEP 3 :  백터화된 처리로 item_sys, proditem 생성
        #
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP3 Start')

        is_match = df_joined['Item_list'].notna()
        item_lens = df_joined.loc[is_match, 'Item_list'].apply(len)
        vdCommon.gfn_stepLog('=====> STEP3 End')

        # 빈 컬럼 초기화
        df_joined[CodeMapLCM_ProdItem_Sys] = None
        df_joined[CodeMapLCM_ProdItem] = None

        vdCommon.gfn_saveDf(df_joined, "step3_df_joined", True)

        ################################################################################################################
        # STEP 4 :  단일 값 : proditem = item, item_sys = item , status 그대로 유지
        #
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP4 Start')

        single_idx = item_lens[item_lens == 1].index
        df_joined.loc[single_idx, CodeMapLCM_ProdItem_Sys] = df_joined.loc[single_idx, 'Item_list'].apply(lambda x: x[0])
        df_joined.loc[single_idx, CodeMapLCM_ProdItem] = df_joined.loc[single_idx, 'Item_list'].apply(lambda x: x[0])

        vdCommon.gfn_saveDf(df_joined, "step4_df_joined", True)
        vdCommon.gfn_stepLog('=====> STEP4 End')

        ################################################################################################################
        # STEP 5 :  다건 값 : proditem = None, item_sys = "I1,I2,I3", status "Prod Item 확정필요"
        #
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP5 Start')

        multi_idx = item_lens[item_lens > 1].index
        df_joined.loc[multi_idx, CodeMapLCM_ProdItem_Sys] = df_joined.loc[multi_idx, 'Item_list'].apply(lambda x: ','.join(x))
        df_joined.loc[multi_idx, CodeMapLCM_ProdItem] = None
        df_joined.loc[multi_idx, CodeMapLCM_MapStatus] = "PROD"     # "Prod Item 확정필요"

        vdCommon.gfn_saveDf(df_joined, "step5_df_joined", True)
        vdCommon.gfn_stepLog('=====> STEP5 End')

        ################################################################################################################
        # STEP 6 :  필요없는 컬럼 제거
        #           최종 Output 테이블 만들기 : df_out_codeMapLCM
        ################################################################################################################
        vdCommon.gfn_stepLog('=====> STEP6 Start')
        df_out_codeMapLCM = df_joined.drop(columns=['Item_list'])
        df_out_codeMapLCM.astype(object).astype(str)
        # df_out_codeMapLCM = df_result.copy()

        # 결과 확인 (실제 작업시 저장 or 출력)
        vdCommon.gfn_stepLog('=====> STEP6 End')
        vdCommon.gfn_saveDf(df_out_codeMapLCM, "df_out_codeMapLCM", True)
    else:
        # 빈 데이터프레임 만들기
        vdCommon.gfn_stepLog('=====> STEP7 빈 데이터 프레임 생성 --------')
        df_out_codeMapLCM = pd.DataFrame(columns=[VersionName, Location, SubLocation, Item, CodeMapLCM_ValidFlag])
        logger.Step(p_step_no=900, p_step_desc=f'DataFrame Empty Create')

    vdCommon.gfn_stepLog('plugin Execution End')

except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    # ouput Table 선언
    df_out_codeMapLCM = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    vdCommon.gfn_stepLog('=====> Batch end')