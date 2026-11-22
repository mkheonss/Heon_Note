"""

* 프로그램명
    - PY_UI_PanelDualProgress3IN1

* 내용
    - 이원화 제안 정보 반영 이원화 PANEL 공급 수량 고려 RTF 연결 (모델, 공장 일정)
    -

* Input
- df_in_BOMversion :
- df_in_PanelItem :
- df_in_PanelDualProgress :
-

* Flow Summary
    Step1. df_in_BOMversion : Full BOM에서 Key Material Group = 3IN1이 있는 Item(SETcode), BOM Version을 발췌한다
                              3IN1이 포함되어있는 Item, BOM Version 기준으로 df_in_BOMVersion 데이터프레임을 필터링해서 새로운 데이터프레임 df_BOMVersion_3IN1을 생성
    Step2. df_in_PanelItem  : 완패널Item정보를 df_BOMVersion_3IN1의 To Item 필드와 비교해서 있다면 완Panel여부(PanelFlag)에 True로 체크
    Step3. df_in_PanelDualProgress : df_BOMVersion_3IN1 & df_in_PanelDualProgress 데이터프레임을 merge 해서 완Panel여부 필드를 추가
    Step4. df_BOMVersion_3IN1 & df_in_PanelDualProgress 데이터프레임을 merge 해서 OpenCell여부 필드를 추가
    Step5. 완Panel여부, OpenCell여부 중 하나라도 Y인 경우, 3IN1 Exists 필드를 새로 만들어서 Y로 체크
    Step6. 최종 output을 위한 필드 정리
    Step7. 3IN1 Exist == "N" 이면  Measure.[Panel Dual Progress_3IN1 New Code.Lock] = true

* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2025.06.09 / syif1380.lee / Create
    - 2025.06.17 / syif1380.lee / df_in_PanelDualProgress : [Region].[Region] (Grain) 추가
    - 2025.06.19 / syif1380.lee / ds_in_PanelDualOld 추가, 로직 변경
    - 2025.09.08 / syif1380.lee / df_in_BOMVersion IBPL Query 변경
    - 2025.09.25 / syif1380.lee / 재생성
    - 2025.09.26 / syif1380.lee / OpenCellFlag 로직 변경
    - 2025.10.14 / syif1380.lee / Measure.[Panel Dual Progress_3IN1 New Code.Lock]  세팅
    - 2026.01.27 / syif1380.lee / Input Table 데이터 없을 경우
    - 2026.01.28 / syif1380.lee / df_in_PanelItem ibpl 변경 "완Panel" > "Completed" 변경
    - 2026.01.29 / syif1380.lee / NaN 이 있을 경우 오류 발생으로 처리 (2026.01.29)

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table
    [2025.09.24 수정]
    - df_in_BOMversion :
    Select (  [Item].[Item]
        * [BOM Info].[BOM Version]
        * [To Item].[To Item]
        * [Item Material].[Item Material]
        * [Item Material].[Key Material Group].filter(#.Name != "-") ) on row,
        ({ Measure.[Full BOM_Flag] }) on column
        where {&CWVUI
        , &NSUIMtrlMSL5View
        , [Location].[Location]
        , [To Location].[To Location]
        , [Status].[Status]
        , [BOM Type].[BOM Type]
        , [BOM Status].[BOM Status]
        , Measure.[Full BOM_Flag] in {"True","TRUE"}
        } ;

    - df_in_PanelItem :
    // select ([Item Material].[Item Material]) where { &NSUIMtrlMSL3View.filter(#.Name contains "완Panel") };
    select ([Item Material].[Item Material]) where { &NSUIMtrlMSL3View.filter(#.Name contains "Completed") };
    // "완Panel" > "Completed" 변경 2026.01.28

    - df_in_PanelDualProgress :
    Select ( &CWVUI
        //* [To Item].[To Item].[GU43U8079FUXZG] /* SET Code */
        * [To Item].[To Item]                  /* SET Code */
        * [Item].[Item]                        /* Old Panel Code*/
        * [Region].[Region]
        * [Item Material].[Item Material]
        * [Dash No].[Dash No]
        * [Change Request].[CR No] ) on row,
        ({ Measure.[Panel Dual Old_Open Cell],  /* Old OpenCell Code*/
        Measure.[Panel Dual Progress_3IN1 Exist]}) on column where {isnull(Measure.[Panel Dual Progress_3IN1 Exist])};

  ########################################################################################################################################################################
  # - ds_in_PanelDualOld : add 2025.06.19 syif1380.lee
  #   Select ([Item].[Item] * [To Item].[To Item] * [Region].[Region] * &CWVUI * [Dash No].[Dash No] ) on row,
  #   ({Measure.[Panel Dual Old_Open Cell]}) on column;
  #
  # ## BOM Version 메져에는 Open Cell, Panel 데이터만 구성되어, 3IN1 같은 자재그룹 대상은 구성이 안됨.  3IN1 Exist 정보 구성하는 부분이 보완이 필요
  # # - df_in_BOMVersion :
  # #   Select ([Item].[Item]                       /* << (Row의 Model Code) [To Item].[To Item] */
  # #   * [BOM Info].[BOM Version]
  # #   * [Item Material].[Item Material]           /* << (Row의 Old O/C Code) Measure.[Panel Dual Old_Open Cell]*/
  # #   * [Item Material].[Key Material Group]) on row,
  # #   ({Measure.[BOM Version_Fix Flag], Measure.[Dummy]}) on column
  # #    where {&CWVUI,[Location].[Location],[Item Component].[Item Component] };
  #
  # ## BOM Version 메져에는 Open Cell, Panel 데이터만 구성되어, 3IN1 같은 자재그룹 대상은 구성이 안됨.  3IN1 Exist 정보 구성하는 부분이 보완이 필요
  # ## Full BOM에서 데이터를 발췌하는 것으로 수정 (513,866 건). 2025.09.08 (박상현P요청)
  # - df_in_BOMVersion :
  #       Select (  [Item].[Item]
  #       * [BOM Info].[BOM Version]
  #       * [Item Material].[Item Material]
  #       * [Item Material].[Key Material Group].filter(#.Name != "-") ) on row,
  #       ({ Measure.[Full BOM_Flag] }) on column
  #       where {&CWVUI
  #       , &NSUIMtrlMSL5View
  #       , [Location].[Location]
  #       , [To Location].[To Location]
  #       , [To Item].[To Item]
  #       , [Status].[Status]
  #       , [BOM Type].[BOM Type]
  #       , [BOM Status].[BOM Status]
  #       , Measure.[Full BOM_Flag] in {"True","TRUE"}
  #       } limit 1000;
  #
  # - df_in_BOMVersion : copy [Item Material].[Key Material Group] == '3IN1' 필터링한 df
  #
  # - df_in_PanelDualProgress
  #   Select ( &CWVUI * [Item].[Item] * [To Item].[To Item] * [Region].[Region] * [Item Material].[Item Material] * [Dash No].[Dash No] * [Change Request].[CR No] ) on row,
  #   ({ Measure.[Panel Dual Progress_3IN1 Exist], Measure.[Panel Dual Progress_Plant] }) on column where {isnull(Measure.[Panel Dual Progress_3IN1 Exist])};
  ########################################################################################################################################################################

* Output Table :
   - df_out_PanelDualProgress
   - df_out_log
   - df_out_logDetail

* 테스트 Update scope
    scope : ( &CWVUI * [Item].[Item] * [To Item].[To Item] * [Region].[Region] * [Item Material].[Item Material] * [Dash No].[Dash No] * [Change Request].[CR No] ) ;
    Measure.[Panel Dual Progress_3IN1 Exist] = null;
    Measure.[Panel Dual Progress_3IN1 New Code.Lock] = null;
    end scope;

* 테스트 스크립트
 /* 호출 (PY_UI_PanelDualProgress3IN1) */
 EXEC plugin instance [PY_UI_PanelDualProgress3IN1] for measures {[Panel Dual Progress_3IN1 Exist]}
 using scope ( &CWVUI )
 using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
str_instance = 'PY_UI_PanelDualProgress3IN1'

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

def print_df(df, df_name, _localFlag=False):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)

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
        df_in_BOMversion =pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_BOMversion.csv", encoding="UTF-8")
        df_in_PanelItem = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_PanelItem.csv", encoding="UTF-8")
        df_in_PanelDualProgress = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_PanelDualProgress.csv", encoding="UTF-8")
        pDetailLogFlag = "N"

    # 입력 변수 확인용 로그
    vdCommon.gfn_saveDf(df_in_BOMversion, "df_in_BOMVersion", True)
    vdCommon.gfn_saveDf(df_in_PanelItem, "df_in_PanelItem", True)
    vdCommon.gfn_saveDf(df_in_PanelDualProgress, "df_in_PanelDualProgress", True)

    dataframes = {
        'df_in_BOMversion': df_in_BOMversion,
        'df_in_PanelItem': df_in_PanelItem,
        'df_in_PanelDualProgress': df_in_PanelDualProgress,
    }

    for name, df in dataframes.items():
        print_df(df, f'input table load .... {name}')

    if df_in_BOMversion.empty or df_in_PanelItem.empty or df_in_PanelDualProgress.empty :
        vdCommon.gfn_stepLog('=====> 입력 데이터가 비어 있어 처리할 수 없습니다.')
        raise Exception("Cannot proceed because the input data is empty.")  # 입력 데이터가 비어 있어 처리할 수 없습니다

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수 선언 - Dimension
    VersionName = 'Version.[Version Name]'
    Item = 'Item.[Item]'
    ToItem = 'To Item.[To Item]'
    ItemMaterial = 'Item Material.[Item Material]'
    DashNo = 'Dash No.[Dash No]'
    CRNo = 'Change Request.[CR No]'
    Region = 'Region.[Region]'

    # add 2025.06.19
    BOMVersion = 'BOM Info.[BOM Version]'
    KeyMaterialGroup = 'Item Material.[Key Material Group]'
    PanelDualOld_OpenCell = 'Panel Dual Old_Open Cell'

    # 컬럼 변수 선언 - BOD List (Measure Group)
    PanelDualProgress_3IN1Exist = 'Panel Dual Progress_3IN1 Exist'
    PanelDualProgress_Plant = 'Panel Dual Progress_Plant'

    ################################################################################################################
    # STEP 1 :
    # BOM Version Data : Full BOM에서 Key Material Group = 3IN1이 있는 Item(SETcode), BOM Version을 발췌한다
    # df_in_BOMversion 을 Item.[Item] , BOM Info.[BOM Version] 로 그룹핑
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 1 Start ============== [ 1 ] ===================')

    has_3in1 = df_in_BOMversion[KeyMaterialGroup].eq("3IN1").groupby([df_in_BOMversion[Item], df_in_BOMversion[BOMVersion]]).transform("any")

    ## Nan 이 있는 것만 담아서 출력.. 테스트용
    # df_na = df_in_BOMversion.loc[has_3in1.isna(), [Item, BOMVersion, KeyMaterialGroup]]
    # print(df_na.head(20))

    # NaN 이 있을 경우 오류 발생으로 처리 (2026.01.29)
    # Nan 을 bool type False 로 대체 함 (빼면 안돼는 이유는 "3in1" 이 한개라도 있으면 그룹전체 포함)
    mask = has_3in1.to_numpy(dtype=bool, na_value=False)
    df_BOMVersion_3IN1 = df_in_BOMversion[mask]

    vdCommon.gfn_stepLog('=====> STEP 2 Start ============== [ 2 ] ===================')
    # 필요컬럼만 남김
    df_BOMVersion_3IN1_org = df_BOMVersion_3IN1[[Item, BOMVersion, ToItem, ItemMaterial]]
    df_BOMVersion_3IN1 = df_BOMVersion_3IN1_org.copy()

    vdCommon.gfn_saveDf(df_BOMVersion_3IN1, "df_BOMVersion_3IN1", True)

    ################################################################################################################
    # STEP 2 : 완패널Item정보를 df_BOMVersion_3IN1의 To Item 필드와 비교해서 있다면 완Panel여부(PanelFlag)에 True로 체크
    #
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 2 Start ============== [ 3 ] ===================')
    df_PanelItem = df_in_PanelItem[[ItemMaterial]]

    # vdCommon.gfn_saveDf(df_PanelItem, "df_PanelItem", True)

    # set()을 사용해 lookup 속도 향상
    matl_set = set(df_PanelItem[ItemMaterial])

    # 백터화된 방식으로 apply 없이 boolean 배열 생성 후 map
    df_BOMVersion_3IN1['PanelFlag'] = df_BOMVersion_3IN1[ToItem].isin(matl_set).map({True:'Y', False:'N'})
    vdCommon.gfn_saveDf(df_BOMVersion_3IN1, "df_BOMVersion_3IN1_panelFlag", True)

    ################################################################################################################
    # STEP 3 : df_BOMVersion_3IN1 & df_in_PanelDualProgress 데이터프레임을 merge 해서 완Panel여부 필드를 추가
    #
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 3 Start ============== [ 3 ] ===================')
    df_panelDualProgress_merge = pd.merge(df_in_PanelDualProgress, df_BOMVersion_3IN1
                                   , left_on=[ToItem, Item]
                                   , right_on=[Item, ToItem], how='left')

    df_panelDualProgress_merge.rename(columns={ToItem+'_x': ToItem, Item+'_x': Item, ItemMaterial+'_x':ItemMaterial}, inplace=True)
    df_panelDualProgress_merge = df_panelDualProgress_merge[[VersionName, ToItem, Item, ItemMaterial, Region, DashNo, CRNo, PanelDualOld_OpenCell, 'PanelFlag']].drop_duplicates()
    # vdCommon.gfn_saveDf(df_bomVersion_merge, "df_bomVersion_merge____1", True)

    ################################################################################################################
    # STEP 4 : df_BOMVersion_3IN1 & df_in_PanelDualProgress 데이터프레임을 merge 해서 OpenCell여부 필드를 추가
    #
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 4 Start ============== [ 4 ] ===================')
    # 고속 비교용 세트 생성
    key_set = set(zip(df_BOMVersion_3IN1_org[Item], df_BOMVersion_3IN1_org[ItemMaterial]))
    # OpenCellFlag 컬럼 생성
    df_panelDualProgress_merge['OpenCellFlag'] = list(zip(df_panelDualProgress_merge[ToItem], df_panelDualProgress_merge[PanelDualOld_OpenCell]))
    df_panelDualProgress_merge['OpenCellFlag'] = df_panelDualProgress_merge['OpenCellFlag'].map(lambda x: 'Y' if x in key_set else 'N')
    vdCommon.gfn_saveDf(df_panelDualProgress_merge, "df_panelDualProgress_merge_openCellFalg", True)

    ################################################################################################################
    # STEP 5 : 완Panel여부, OpenCell여부 중 하나라도 Y인 경우, 3IN1 Exists 필드를 새로 만들어서 Y로 체크
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> STEP 5 Start ============== [ 5 ] ===================')
    df_panelDualProgress_merge['3IN1 Exist'] = ((df_panelDualProgress_merge['PanelFlag'] == 'Y') | (df_panelDualProgress_merge['OpenCellFlag'] == 'Y')).map({True:'Y', False:'N'})
    # vdCommon.gfn_saveDf(df_panelDualProgress_merge, "ddf_bomVersion_merge_____3IN1Exist", True)

    ################################################################################################################
    # STEP 6 : 최종 output을 위한 필드 정리
    ################################################################################################################
    df_panelDualProgress_merge.rename(columns={ToItem + '_x': ToItem, Item + '_x': Item, ItemMaterial + '_x': ItemMaterial, '3IN1 Exist':PanelDualProgress_3IN1Exist}, inplace=True)
    df_out_PanelDualProgress = df_panelDualProgress_merge[[VersionName, ToItem, Item, ItemMaterial, Region, DashNo, CRNo, PanelDualProgress_3IN1Exist]].drop_duplicates()

    ################################################################################################################
    # STEP 7 : 3IN1 Exist == "N" 이면  Measure.[Panel Dual Progress_3IN1 New Code.Lock] = true
    ################################################################################################################
    df_out_PanelDualProgress['Panel Dual Progress_3IN1 New Code.Lock'] = df_out_PanelDualProgress[PanelDualProgress_3IN1Exist] == "N"   # true/false

    vdCommon.gfn_saveDf(df_out_PanelDualProgress, "df_out_PanelDualProgress", True)

    vdCommon.gfn_stepLog('plugin Execution End')

except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    # ouput Table 선언
    df_out_PanelDualProgress = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    vdCommon.gfn_stepLog('=====> Batch end')