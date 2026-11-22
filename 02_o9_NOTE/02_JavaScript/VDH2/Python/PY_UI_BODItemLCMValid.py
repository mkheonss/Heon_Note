"""

* 프로그램명
    - PY_UI_BODItemLCMValid

* 내용
    - LCM BOD List > BOD Item : Validation 액션버튼 수행
    - Data 전체 Validation 체크 : 중복체크, 동일 구간 To Site-Item 기준 동일한 Priority 가 있을 경우 Measure.[BOD Item_Need Check] 내용 업데이트

* Input
- df_in_bodItem :

* Flow Summary
    Step1.
    Step2.
    Step3.
    Step4.


* Input
    - in_ = pd.read_csv(' .csv')

* 변경이력
    - 2024.07.24 / syif1380.lee / Create
    - 2025.03.14 / syif1380.lee / vdCommon 공통 로그 작업
    - 2025.03.24 / syif1380.lee / input Table where 조건 추가
    - 2026.01.27 / syif1380.lee / Input Table 데이터 없을 경우 Header 생성하여 오류 방지

* Script Parameter
    - param_outVersion : 기본값 :

* Input Table

  - df_in_bodItem :
    # Select ([Version].[Version Name] * [Item].[Item] * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    # ({Measure.[BOD Item_BOD Frozen], Measure.[BOD Item_BOD LT], Measure.[BOD Item_Created By], Measure.[BOD Item_Creation Time], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate]
    # , Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Min Lot Qty], Measure.[BOD Item_Multi Lot Qty], Measure.[BOD Item_Need Check], Measure.[BOD Item_Period SET Detail], Measure.[BOD Item_Period1]
    # , Measure.[BOD Item_Period2], Measure.[BOD Item_Period3], Measure.[BOD Item_Priority], Measure.[BOD Item_Prod Item], Measure.[BOD Item_Shipment LT], Measure.[BOD Item_Time Phased BOD], Measure.[BOD Item_Time Phased Prty]
    # , Measure.[BOD Item_Time Phased Shipment], Measure.[BOD Item_To Item], Measure.[BOD Item_Update Time], Measure.[BOD Item_Updated By]}) on column;

    Select ( [Version].[Version Name] * &LCMItem * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    ({Measure.[BOD Item_Prod Item], Measure.[BOD Item_BOD LT], Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Lock Flag], Measure.[BOD Item_Need Check], Measure.[BOD Item_Priority], Measure.[BOD Item_Shipment LT]}) on column limit 100;

    // 2025.03.24
    Select ( [Version].[Version Name] * &LCMItem * [Location].[Location] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) on row,
    ({Measure.[BOD Item_Prod Item],Measure.[BOD Item_Eff Enddate], Measure.[BOD Item_Eff Startdate], Measure.[BOD Item_Need Check], Measure.[BOD Item_Priority] }) on column
    where {Measure.[BOD Item_Asn] == 1, ~isnull(Measure.[BOD Item_Priority]), DATEDIFF(Measure.[BOD Item_Update Time], DATEADD(Now(),9,"hour"), "Day") <= 0 }; // update날짜가 오늘(0) or 미래날짜(마이너스)일 경우만 데이터 가져옴

* Output Table :
   - df_out_bodItem :


* 테스트 스크립트
/* Validation 호출 (PY_UI_BODItemLCMValid) */
EXEC plugin instance [PY_UI_BODItemLCMValid] for measures {[BOD Item_Eff Startdate]} using scope ( &CWVUI ) using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};

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
str_instance = 'PY_UI_BODItemLCMValid'

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
        df_in_bodItem = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_bodItem.csv", encoding="UTF-8")
        pDetailLogFlag = "N"

    # 입력 변수 확인용 로그
    vdCommon.gfn_saveDf(df_in_bodItem, "df_in_bodItem", True)

    ################################################################################################################
    # DataFrame Column 변수 처리
    ################################################################################################################
    # 컬럼 변수 선언 - Dimension
    VersionName = 'Version.[Version Name]'
    Item = 'Item.[Item]'
    Location = 'Location.[Location]'
    SubLocation = 'Sub Location.[Sub Location]'
    TransMode = 'Trans Mode.[Trans Mode]'

    # 컬럼 변수 선언 - BOD Item (Measure Group)
    # BODItemLockFlag = 'BOD Item_Lock Flag'
    BODItemPriority = 'BOD Item_Priority'
    BODItem_NeedCheck = 'BOD Item_Need Check'
    FromItem = 'BOD Item_Prod Item'
    StartDate = 'BOD Item_Eff Startdate'
    EndDate = 'BOD Item_Eff Enddate'

    # Validation Message
    ValidationMsg = 'Priority 중복'

    vdCommon.gfn_stepLog('=====> STEP1 Start')

    if not df_in_bodItem.empty:

        df_in_bodItem[Item] = df_in_bodItem[Item].astype(str)
        df_in_bodItem[TransMode] = df_in_bodItem[TransMode].astype(str)
        df_in_bodItem[Location] = df_in_bodItem[Location].astype(str)
        df_in_bodItem[SubLocation] = df_in_bodItem[SubLocation].astype(str)

        # null 인 경우 '' 처리
        df_in_bodItem[FromItem] = df_in_bodItem[FromItem].fillna('')
        df_in_bodItem[StartDate] = df_in_bodItem[StartDate].fillna('')
        df_in_bodItem[EndDate] = df_in_bodItem[EndDate].fillna('')

        df_in_bodItem[FromItem] = df_in_bodItem[FromItem].astype(str)
        df_in_bodItem[StartDate] = df_in_bodItem[StartDate].astype(str)
        df_in_bodItem[EndDate] = df_in_bodItem[EndDate].astype(str)

        # Location, Sub Location, Tp Mode, Item  컬럼에 BOD Item_Priority 값이 동일할 경우 Validation Check
        def mark_duplicated(group):
            mask = group[BODItemPriority].notna()
            duplicates = group.loc[mask, BODItemPriority].duplicated(keep=False)
            group.loc[mask & duplicates, 'checkFlag'] = True
            return group

        # FromItem, StartDate, EndDate 가 '' 일 경우에는 Groupby 에서 제외
        filtered_df = df_in_bodItem[(df_in_bodItem[FromItem] != '') & (df_in_bodItem[StartDate] != '') & (df_in_bodItem[EndDate] != '' )]

        filtered_df['checkFlag'] = False
        # Item 이 key 로 중복 데이타가 없음, 아래 로직으로는 중복 발생하지 않음.
        df_in_bodItem_tmp = filtered_df.groupby([Location, SubLocation, TransMode, Item, FromItem, StartDate, EndDate]).apply(mark_duplicated).reset_index(drop=True)
        df_in_bodItem_tmp[BODItem_NeedCheck] = np.where(df_in_bodItem_tmp['checkFlag'] == True, 'Priority중복', '')

        vdCommon.gfn_stepLog('=====> STEP1 End')

        # 컬럼 삭제
        df_out_bodItem = df_in_bodItem_tmp.drop(labels=['checkFlag'], axis=1)

    else:
        df_out_bodItem = pd.DataFrame(columns=[VersionName, Location, SubLocation, TransMode, Item, BODItem_NeedCheck])

    ################################################################################################################
    # 최종 Output 테이블 만들기
    ################################################################################################################
    vdCommon.gfn_saveDf(df_out_bodItem, "df_out_bodItem", True)

    vdCommon.gfn_stepLog('plugin Execution End')

except Exception as e:
    vdCommon.gfn_stepLog(f'=====> try exception : {traceback.format_exc()}')
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.debug())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    # ouput Table 선언
    df_out_bodItem = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()
    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()
    logger.Finish()
    vdCommon.gfn_stepLog('=====> Batch end')