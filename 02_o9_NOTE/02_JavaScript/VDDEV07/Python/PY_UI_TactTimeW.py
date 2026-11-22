"""

* 프로그램명
    - PY_UI_TactTimeW

* 프로그램 수정일 : 2024/11/14

* 내용
     - Tact Time에 있는 Location*Line*Item 중에 Tact Time W에 없는 Location*Line*Item 추가

* 변경이력
- 2024.08.12 / ybest7.park (박병훈) / Create
- 2026.01.14 / ybest7.park (박병훈) / input query 수정 및 로직 수정
- 2026.02.05 / ybest7.park (박병훈) / input query null 입력 시 에러가 발생하는 것 수정

* Input
- df_in_ProductionConstraint = pd.read_csv('ProductionConstraint.csv')


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CWV_MP, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Table
   - df_in_FPTactTime = Select ( [Version].[Version Name]* [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time_Lock Flag], Measure.[Tact Time_Time], Measure.[Dummy] })on column where {Measure.[Tact Time_Valid Asn]== true};
   # - df_in_TactTimeW = Select ( &MPV * [Item].[Item]  * &PlanningHorizon * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time W_Lock Flag], Measure.[Tact Time W_Time], Measure.[Tact Time W_Time Override], Measure.[Tact Time W_Time Sys]}) on column ;
   - df_in_PlanWeek  = Select ( &PlanningHorizon ) on row, () on column include memberproperties{[Time].[Week], Key, [W Solver Current Bucket], [W Solver Start Bucket], [W Solver End Bucket]};
   - df_in_MPTactRule = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Marketing Name] * [Sequence].[Sequence] * [Project].[Project] * [Product].[Product Group] * [Line].[Line] * [Definition].[Definition] ) on row, ({Measure.[Prod Model_From Inch], Measure.[Prod Model_From Inch Actual], Measure.[Prod Model_Line Priority], Measure.[Prod Model_Tact Time], Measure.[Prod Model_Tact Time Actual], Measure.[Prod Model_To Inch], Measure.[Prod Model_To Inch Actual],Measure.[Dummy]}) on column;
   - df_in_Item = Select ([Item].[Item Stage].filter(#.Name =="SET").relatedmembers([Item])  * [Item].[Marketing Name] * [Item].[Inch] * [Item].[Definition] * [Item].[Product Group] *[Item].[Project]* [Item].[Plan Group].filter(#.Name == 1) * [Item].[ProductType].filter(#.Name == "NOR"));
   # - df_in_Demand =  Select ( &MPV *  [Item].[Item] * &PlanningHorizon * [Location].[Location] * [Sales Domain].[Ship To] * [Demand Type].[Demand Type] * [Demand].[DemandID] ) on row, ({Measure.[Dmd W_BAL], Measure.[Dmd W_Cust Rank], Measure.[Dmd W_Dmd Rank], Measure.[Dmd W_Global Prty], Measure.[Dmd W_ID], Measure.[Dmd W_Leadtime Due], Measure.[Dmd W_Local Prty],Measure.[Dmd W_Measure Rank], Measure.[Dmd W_No Plan], Measure.[Dmd W_Plan ID], Measure.[Dmd W_Preference],Measure.[Dmd W_Prod Rank], Measure.[Dmd W_Prty], Measure.[Dmd W_Prty Seq], Measure.[Dmd W_Qty], Measure.[Dmd W_Week Rank]}) on column;
   # - df_in_SyncLine = Select ( &MPV * [Location].[Location] * [To Line].[To Line] * [Line].[Line] ) on row, ({Measure.[Sync Line_Enddate], Measure.[Sync Line_Flag], Measure.[Sync Line_Startdate]}) on column.filter(  Measure.[Sync Line_Flag] =="Y");
   # - df_in_BOMMaster = Select ( &MPV * [Location].[Location] * [BOM Info].[BOM ID] ) on row, ({Measure.[BOM Master_BOM ID] }) on column;
   # - df_in_BOMComponent = Select ( &MPV * &LCMItem * [Location].[Location] * [BOM Info].[BOM ID] ) on row,({Measure.[BOM Comp_Consume Qty] }) on column ;
    -  df_in_ItemSiteAsn  = Select (Version.[Version Name]* [Item].[Item] * Location.[Location]) on row, ({Measure.[Item Site Asn_Cur Status],Measure.[Dummy]}) on column  where {Item.[Item Stage].[SET], Item.[Plan Group].[1], Item.[ProductType].[NOR],  Measure.[Item Site Asn_Cur Status] in {"PLANNED","ACTIVE"}};

* Output Table
    - df_out_TactTimeW =  Select (&MPV] * [Item].[Item] * [Time].[Week] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time W_Lock Flag], Measure.[Tact Time W_Time], Measure.[Tact Time W_Time Override], Measure.[Tact Time W_Time Sys]}) on column;
    - df_out_TactTimeWSub =  Select (&MPV * [Item].[Item] * [Location].[Location] * [Line].[Line] ) on row, ({Measure.[Tact Time W Sub_Flag]}) on column;

* 데이터 삭제
    DELETE DATA FOR MODEL [Tact Time W] where {Version.[Version Name].[CWV_MP]};
    DELETE DATA FOR MODEL [Tact Time W Sub] where {Version.[Version Name].[CWV_MP]};

* 테스트 스크립트
    EXEC plugin instance [PY_UI_TactTimeW] for measures {[Tact Time W_Time]} using scope ([Version].[Version Name].filter(#.Name in {"CWV_MP"}) * &PlanningHorizon) using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG"),(paramOutVersion, "CWV_MP")} ;




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
import pytz

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_TactTimeW'
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
# logic start
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
        step(f"=====> 로그 처리 중 오류 발생: {str(e)}")
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
            df_in_FPTactTime = read_csv_file("df_in_FPTactTime")
            # df_in_TactTimeW = read_csv_file("df_in_TactTimeW")
            df_in_PlanWeek = read_csv_file("df_in_PlanWeek")
            df_in_MPTactRule = read_csv_file("df_in_MPTactRule")
            df_in_Item = read_csv_file("df_in_Item")
            # df_in_Demand = read_csv_file("df_in_Demand")
            # df_in_SyncLine = read_csv_file("df_in_SyncLine")
            # df_in_BOMMaster	= read_csv_file("df_in_BOMMaster")
            # df_in_BOMComponent = read_csv_file("df_in_BOMComponent")
            df_in_ItemSiteAsn = read_csv_file("df_in_ItemSiteAsn")

        dataframes = {
            'df_in_FPTactTime':        df_in_FPTactTime,
            'df_in_PlanWeek':          df_in_PlanWeek,
            'df_in_MPTactRule':        df_in_MPTactRule,
            'df_in_Item':              df_in_Item,
            'df_in_ItemSiteAsn':       df_in_ItemSiteAsn
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################

        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        # 컬럼 변수설정
        Version_COLUMN = 'Version.[Version Name]'
        Item_COLUMN = 'Item.[Item]'
        Location_COLUMN = 'Location.[Location]'
        LINE_COLUMN = 'Line.[Line]'
        ITEM_Marketing_COLUMN = 'Item.[Marketing Name]'
        Definition_COLUMN = 'Definition.[Definition]'
        Product_Group_COLUMN = 'Product.[Product Group]'
        Sequence_COLUMN = 'Sequence.[Sequence]'
        Item_Inch_COLUM = 'Item.[Inch]'
        Item_Definition_COLUMN = 'Item.[Definition]'
        Item_Product_GROUP_COLUMN = 'Item.[Product Group]'
        Item_Project_COLUMN = 'Item.[Project]'
        Sales_Domain_ShipTO_COLUMN = 'Sales Domain.[Ship To]'
        Demand_Type_COLUMN = 'Demand Type.[Demand Type]'
        Demand_ID_COLUMN = 'Demand.[DemandID]'
        TimeWeek_COLUMN = 'Time.[Week]'
        BOM_INFO_ID_COLUMN = 'BOM Info.[BOM ID]'
        TO_Line_COLUMN = 'To Line.[To Line]'
        Project_COLUMN = 'Project.[Project]'

        Tact_Time_Time = 'Tact Time_Time'
        Tact_Time_W_Lock_Flag = 'Tact Time W_Lock Flag'
        Tact_Time_W_Time = 'Tact Time W_Time'
        Tact_Time_W_Time_Override = 'Tact Time W_Time Override'
        Tact_Time_W_Time_Sys = 'Tact Time W_Time Sys'

        Tact_Time_W_Sub_Flag = 'Tact Time W Sub_Flag'

        Prod_Model_From_Inch = 'Prod Model_From Inch'
        Prod_Model_To_Inch = 'Prod Model_To Inch'
        Prod_Model_Line_Priority = 'Prod Model_Line Priority'
        Prod_Model_Tact_Time = 'Prod Model_Tact Time'

        Key_on = 'Key On'

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')
 
        # df_in_Item 의 unique 한 아이템만 리스트로 만들기 (df_in_FPTactTime 에서 필터를 하기 위한 준비)
        df_in_Item_list = df_in_Item[Item_COLUMN].tolist()
        # df_in_FPTactTime 에서 df_in_Item 에 있는 아이템 (df_in_Item_list) 만 추출
        df_in_FPTactTime_temp = df_in_FPTactTime[df_in_FPTactTime[Item_COLUMN].isin(df_in_Item_list)]

        # df_in_ItemSiteAsn 에서 존재하는 Item/Location만 추출하기 위한 준비
        # df_in_ItemSiteAsn 의 Item/Location 추출하여 중복 제거 index로 만들기
        df_in_ItemSiteAsn_index = df_in_ItemSiteAsn[[Item_COLUMN, Location_COLUMN]].drop_duplicates().set_index(
            [Item_COLUMN, Location_COLUMN], drop=True).index
        df_in_FPTactTime_index = df_in_FPTactTime_temp.set_index([Item_COLUMN, Location_COLUMN]).index
        # Item/Location 기준으로 df_in_ItemSiteAsn 에 있는 것을을 df_in_FPTactTime 에서 추출하기 index 사용
        df_in_FPTactTime_temp = df_in_FPTactTime_temp[df_in_FPTactTime_index.isin(df_in_ItemSiteAsn_index)]

        print_df(df_in_FPTactTime_temp, "df_in_FPTactTime_temp 임시 확인", )

        # df_in_ItemSiteAsn 에 있는  Item 필터 df_in_Item 기준 → All 확장 전 모수를 줄임 (필터 전 축소)
        df_in_ItemSiteAsn_ItemList = df_in_ItemSiteAsn[Item_COLUMN].tolist()
        df_in_Item_temp = df_in_Item[df_in_Item[Item_COLUMN].isin(df_in_ItemSiteAsn_ItemList)]

        # All 부분을 확장하기 위한 리스트 생성
        Item_MarketingName_list = df_in_Item_temp[
            ITEM_Marketing_COLUMN].unique().tolist()  # Item Marketing 기준  (Ex : Q6,Serif, QN70 ...)
        Item_Definition_list = df_in_Item_temp[
            Item_Definition_COLUMN].unique().tolist()  # Item Definition 기준 (Ex : 'UHD', 'FHD', 'HD' ...)
        Item_ProductGROUP_list = df_in_Item_temp[
            Item_Product_GROUP_COLUMN].unique().tolist()  # Item Product 기준    (Ex : 'TV', 'MONITOR', '-' ...)
        Item_Project_list = df_in_Item_temp[
            Item_Project_COLUMN].unique().tolist()  # Item Projct 기준     (Ex : 'Q60CJ', 'Q60DG', 'QTQ60F' ...)

        # ITEM_Marketing_COLUMN 기준으로 All 인 경우 Item_MarketingName_list 로 확장
        mkt_all = df_in_MPTactRule[ITEM_Marketing_COLUMN].astype(str).eq('All')
        mkt_idx = df_in_MPTactRule.index[mkt_all]
        df_in_MPTactRule.loc[mkt_idx, ITEM_Marketing_COLUMN] = pd.Series([Item_MarketingName_list] * len(mkt_idx),
                                                                         index=mkt_idx)
        df_in_MPTactRule = df_in_MPTactRule.explode(ITEM_Marketing_COLUMN, ignore_index=True)

        # Definition_COLUMN 기준으로 All 인 경우 Item_Definition_list 로 확장
        definition_all = df_in_MPTactRule[Definition_COLUMN].astype(str).eq('All')
        def_idx = df_in_MPTactRule.index[definition_all]
        df_in_MPTactRule.loc[def_idx, Definition_COLUMN] = pd.Series([Item_Definition_list] * len(def_idx),
                                                                     index=def_idx)
        df_in_MPTactRule = df_in_MPTactRule.explode(Definition_COLUMN, ignore_index=True)

        # Product_Group_COLUMN 기준으로 All 인 경우 Item_ProductGROUP_list 로 확장
        product_all = df_in_MPTactRule[Product_Group_COLUMN].astype(str).eq('All')
        product_idx = df_in_MPTactRule.index[product_all]
        df_in_MPTactRule.loc[product_idx, Product_Group_COLUMN] = pd.Series([Item_ProductGROUP_list] * len(product_idx),
                                                                            index=product_idx)
        df_in_MPTactRule = df_in_MPTactRule.explode(Product_Group_COLUMN, ignore_index=True)

        # Project_COLUMN 기준으로 All 인 경우 Item_Project_list 로 확장
        project_all = df_in_MPTactRule[Project_COLUMN].astype(str).eq('All')
        project_idx = df_in_MPTactRule.index[project_all]
        df_in_MPTactRule.loc[project_idx, Project_COLUMN] = pd.Series([Item_Project_list] * len(project_idx),
                                                                      index=project_idx)
        df_in_MPTactRule = df_in_MPTactRule.explode(Project_COLUMN, ignore_index=True)

        print_df(df_in_MPTactRule, "df_in_MPTactRule 임시 확인", )

        #  merge를 위한 df_in_Item column 변경
        df_in_Item = df_in_Item.rename(
            columns={
                Item_Definition_COLUMN: Definition_COLUMN,
                Item_Product_GROUP_COLUMN: Product_Group_COLUMN,
                Item_Project_COLUMN: Project_COLUMN})

        # merge를 위한 key 설정
        merge_key = [ITEM_Marketing_COLUMN, Definition_COLUMN,
                     Product_Group_COLUMN, Project_COLUMN]

        # df_in_MPTactRule 에 Item을 찾기 위한 Merge
        df_in_MPTactRule_temp = df_in_MPTactRule.drop(columns='Dummy', axis=1).merge(
            df_in_Item, on=merge_key, how='inner')

        #  Item_COLUMN 이 null 이건 것 제외
        df_in_MPTactRule_temp = df_in_MPTactRule_temp[~df_in_MPTactRule_temp[Item_COLUMN].isnull()]
        # Item_Inch_COLUM 비교를 위한 데이터 타입 변경
        df_in_MPTactRule_temp[Item_Inch_COLUM] = pd.to_numeric(df_in_MPTactRule_temp[Item_Inch_COLUM], errors='coerce')
        df_in_MPTactRule_temp[Prod_Model_From_Inch] = df_in_MPTactRule_temp[Prod_Model_From_Inch].astype(int)
        df_in_MPTactRule[Prod_Model_To_Inch] = df_in_MPTactRule[Prod_Model_To_Inch].astype(int)
        # Prod_Model_From_Inch 와 Prod_Model_To_Inch 사이에 있는 Item_Inch_COLUM 것만 마스크
        inch_mask = (df_in_MPTactRule_temp[Item_Inch_COLUM].between(
            df_in_MPTactRule_temp[Prod_Model_From_Inch], df_in_MPTactRule_temp[Prod_Model_To_Inch]))
        # df_in_MPTactRule_temp 에 inch_mask 적용해서 filter
        df_in_MPTactRule_temp = df_in_MPTactRule_temp.loc[inch_mask]

        # df_in_MPTactRule_temp 기준 df_in_ItemSiteAsn 에 포함된 (Item 과 Location 기준 Filter)
        df_in_MPTactRule_temp_index = df_in_MPTactRule_temp.set_index([Item_COLUMN, Location_COLUMN]).index
        # Item/Location 기준으로 df_in_ItemSiteAsn 에 있는 것을을 df_in_MPTactRule_temp_index 에서 추출하기 index 사용
        df_in_MPTactRule_temp = df_in_MPTactRule_temp[df_in_MPTactRule_temp_index.isin(df_in_ItemSiteAsn_index)]

        print_df(df_in_MPTactRule_temp, "df_in_MPTactRule_temp 1차 결과 확인", )

        step('=====> STEP 3 End')
        ################################################################################################################
        # STEP 4 :  input data machining
        ################################################################################################################
        step('=====> STEP 4 Start : input data machining')
        # Tact Time W Sub_Flag = ‘N’ 처리를 위한 전처리
        # df_in_FPTactTime 기준으로 df_in_MPTactRule_temp 없는 것을을 Tact Time W Sub_Flag 에 'N" 처리
        # -----> 2026.02.05 Null로 데이터 입력시 에러 나는 부분 수정
        index_cols = [Version_COLUMN, Item_COLUMN, Location_COLUMN, LINE_COLUMN]
        df_out_TactTimeWSub = df_in_MPTactRule_temp[index_cols].copy()
        print_df(df_out_TactTimeWSub, 'df_out_TactTimeWSub -- 임시확인', False)
        df_out_TactTimeWSub.loc[:, Tact_Time_W_Sub_Flag] = pd.Series(
            ['Y'] * len(df_out_TactTimeWSub),index=df_out_TactTimeWSub.index, dtype='string')
        # Tact Time W Sub_Flag = ‘N’ 처리를 위한 전처리
        # df_in_FPTactTime 기준으로 df_in_MPTactRule_temp 없는 것을을 Tact Time W Sub_Flag 에 'N" 처리
        df_in_FPTactTime_temp_index = df_in_FPTactTime_temp.set_index(index_cols).index
        df_in_MPTactRule_temp_index = df_in_MPTactRule_temp.set_index(index_cols).index
        # df_out_TactTimeWSub 생성
        df_out_TactTimeWSub_Temp = df_in_FPTactTime_temp[
            ~df_in_FPTactTime_temp_index.isin(df_in_MPTactRule_temp_index)]
        print_df(df_out_TactTimeWSub_Temp, 'df_out_TactTimeWSub_Temp -- 임시확인', False)
        # df_out_TactTimeWSub Out Put 설정
        df_out_TactTimeWSub_Temp = df_out_TactTimeWSub_Temp[index_cols]
        # Tact Time W Sub_Flag "N" 처리 -----> 2026.02.05 Null로 데이터 입력시 에러 나는 부분 수정
        df_out_TactTimeWSub_Temp.loc[:, Tact_Time_W_Sub_Flag] = pd.Series(
            ["N"] * len(df_out_TactTimeWSub_Temp), index=df_out_TactTimeWSub_Temp.index, dtype='string')
        # # 'N" 이 아닌 것들은 'Y'로 처리
        # df_out_TactTimeWSub = df_in_FPTactTime_temp[
        #     df_in_FPTactTime_temp_index.isin(ddf_in_MPTactRule_temp_index)]
        # df_out_TactTimeWSub = df_out_TactTimeWSub[index_cols]
        # df_out_TactTimeWSub.loc[:,Tact_Time_W_Sub_Flag] = 'Y'

        df_out_TactTimeWSub = pd.concat([df_out_TactTimeWSub, df_out_TactTimeWSub_Temp], axis=0, ignore_index=True)
        # TactTimeWSub columns 설정 --> 빈 데이터 프레임 발생 시 컬럼 지정 2026.02.05
        TactTimeWSub = {
            Version_COLUMN: 'object', Item_COLUMN : 'object' ,
            Location_COLUMN: 'object', LINE_COLUMN: 'object', Tact_Time_W_Sub_Flag : 'object'}

        if df_out_TactTimeWSub.empty:
            df_out_TactTimeWSub = df_out_TactTimeWSub.reindex(
                columns = TactTimeWSub.keys())
            for c, t in TactTimeWSub.items():
                df_out_TactTimeWSub[c] = pd.Series(index=df_out_TactTimeWSub.index, dtype=t)

        print_df(df_out_TactTimeWSub, "df_out_TactTimeWSub 확인", True)

        step('=====> STEP 4 End')

        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP 5 Start : input data machining')
        # 그룹바이를 하기 위한 키 설정
        groupby_cols = [Version_COLUMN, Location_COLUMN, Item_COLUMN, LINE_COLUMN]
        # 전처리를 위한 평균 및 최소값 구함
        df_in_MPTactRule_temp[Prod_Model_Tact_Time] = pd.to_numeric(df_in_MPTactRule_temp[Prod_Model_Tact_Time],
                                                                    errors='coerce').fillna(0)
        df_out_MpTactRuleNew = df_in_MPTactRule_temp.groupby(groupby_cols).agg(
            Tact_Priority=(Prod_Model_Line_Priority, 'min'),
            Tact_Time_Avg=(Prod_Model_Tact_Time, 'mean')).reset_index()
        df_out_MpTactRuleNew['Tact_Time_W_Time_Min'] = 5
        df_out_MpTactRuleNew['Tact_Time_W_Time_Max'] = df_out_MpTactRuleNew['Tact_Time_Avg'] * 3

        print_df(df_out_MpTactRuleNew, 'df_out_MpTactRuleNew 확인')

        # out put 설정을 위한 merge
        df_out_TactTimeW = df_out_MpTactRuleNew.merge(
            df_in_FPTactTime_temp.drop(columns='Dummy'),
            on=groupby_cols, how='outer')

        # Tact Time을 MP의 평균 Tact Time으로 추가
        df_out_TactTimeW[Tact_Time_W_Time] = df_out_TactTimeW['Tact_Time_Avg']
        print_df(df_out_TactTimeW, 'df_out_TactTimeW 의 Tact_Time_W_Time AVG 확인 ', True)
        # FP의 Tact Time이 있는 경우 FP의 Tact Time으로 반영
        df_out_TactTimeW[Tact_Time_W_Time] = np.where(
            df_out_TactTimeW[Tact_Time_Time].notna(),
            df_out_TactTimeW[Tact_Time_Time],
            df_out_TactTimeW[Tact_Time_W_Time])
        print_df(df_out_TactTimeW, 'df_out_TactTimeW 의 Tact_Time_W_Time FP 적용 확인 ', True)
        # FP의 Tact Time이 Time_Min보다 작으면 Min으로 설정
        df_out_TactTimeW[Tact_Time_W_Time] = np.where(
            df_out_TactTimeW[Tact_Time_W_Time] < df_out_TactTimeW['Tact_Time_W_Time_Min'],
            df_out_TactTimeW['Tact_Time_W_Time_Min'],
            df_out_TactTimeW[Tact_Time_W_Time])
        print_df(df_out_TactTimeW, 'df_out_TactTimeW 의 Tact_Time_W_Time Min 적용 ', True)

        # FP의 Tact Time이 Time_Max보다 크면 Avg로 설정 단 max가 0 인 경우는 제외
        df_out_TactTimeW[Tact_Time_W_Time] = np.where(
            (df_out_TactTimeW['Tact_Time_W_Time_Max'].ne(0)) &
            (df_out_TactTimeW[Tact_Time_W_Time].gt(df_out_TactTimeW['Tact_Time_W_Time_Max'])),
            df_out_TactTimeW['Tact_Time_W_Time_Max'],
            df_out_TactTimeW[Tact_Time_W_Time])

        print_df(df_out_TactTimeW, 'df_out_TactTimeW 의 Tact_Time_W_Time 확정 전 확인', True)

        # 기존 로직에 대한 설정값 반영
        # Tact_Time_W_Time_Sys , Tact_Time_W_Lock_Flag , Tact_Time_W_Time_Override 값 설정
        df_out_TactTimeW.loc[:, Tact_Time_W_Time_Sys] = df_out_TactTimeW[Tact_Time_W_Time].copy()
        # -----> 2026.02.05 Null로 데이터 입력시 에러 나는 부분 수정
        df_out_TactTimeW.loc[:, Tact_Time_W_Lock_Flag] = pd.Series(
            [''] * len(df_out_TactTimeW), index = df_out_TactTimeW.index, dtype = 'string')
        df_out_TactTimeW.loc[:, Tact_Time_W_Time_Override] = pd.Series(
            [''] * len(df_out_TactTimeW), index = df_out_TactTimeW.index, dtype = 'string')

        # df_out_TactTimeW columns 설정
        df_out_TactTimeW = df_out_TactTimeW[[
            Version_COLUMN, Location_COLUMN, Item_COLUMN, LINE_COLUMN,
            Tact_Time_W_Lock_Flag, Tact_Time_W_Time, Tact_Time_W_Time_Override, Tact_Time_W_Time_Sys]]

        # df_out_TactTimeW week 설정을 위한 컬럼 설정  -----> 2026.02.05 Null로 데이터 입력시 에러 나는 부분 수정
        df_out_TactTimeW.loc[:, Key_on] =  pd.Series(
            ['1'] * len(df_out_TactTimeW), index = df_out_TactTimeW.index, dtype = 'string')
        df_in_PlanWeek = df_in_PlanWeek[[TimeWeek_COLUMN]].copy()
        df_in_PlanWeek.loc[:, Key_on] = '1'

        # df_out_TactTimeW을 TimeWeek_COLUMN로 확장
        df_out_TactTimeW = df_out_TactTimeW.merge(
            df_in_PlanWeek, on=Key_on, how='left').drop(columns=Key_on, axis=1)

        # df_out_TactTimeW columns 설정 (TimeWeek_COLUMN 추가)
        df_out_TactTimeW = df_out_TactTimeW[[
            Version_COLUMN, Location_COLUMN, TimeWeek_COLUMN, Item_COLUMN, LINE_COLUMN,
            Tact_Time_W_Lock_Flag, Tact_Time_W_Time, Tact_Time_W_Time_Override, Tact_Time_W_Time_Sys]]

        TactTimeW_cols = {
            Version_COLUMN: 'object', Location_COLUMN : 'object', TimeWeek_COLUMN:'object',Item_COLUMN:'object',
            LINE_COLUMN: 'object' ,Tact_Time_W_Lock_Flag : 'object' , Tact_Time_W_Time:'Float64',
            Tact_Time_W_Time_Override : 'object', Tact_Time_W_Time_Sys : 'Float64'}

        if df_out_TactTimeW.empty:
            df_out_TactTimeW = df_out_TactTimeW.reindex(
                columns = TactTimeW_cols.keys())
            for c , t in TactTimeW_cols.items():
                df_out_TactTimeW[c] = pd.Series(index=df_out_TactTimeW.index, dtype=t)

        print_df(df_out_TactTimeW, 'df_out_TactTimeW 확인')

        step('=====> STEP 5 End')

        ################################################################################################################
        # STEP 6 :  input data machining
        ################################################################################################################

        step('=====> STEP 6 Start : input data machining')

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_TactTimeWSub, 'df_out_TactTimeWSub', True)
            print_df(df_out_TactTimeW, 'df_out_TactTimeW', True)

        print_df(df_out_TactTimeWSub, 'df_out_TactTimeWSub', True)
        print_df(df_out_TactTimeW, 'df_out_TactTimeW', True)


        row_count, col_count = df_out_TactTimeWSub.shape
        note(f'=====> Final df_out_TactTimeWSub rows : {row_count} , Columns : {col_count}')

        row_count, col_count = df_out_TactTimeW.shape
        note(f'=====> Final df_out_TactTimeW rows : {row_count} , Columns : {col_count}')


    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_TactTimeWSub = pd.DataFrame([], columns=[])
        df_out_TactTimeW = pd.DataFrame([], columns=[])


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(
            f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
        step(f'===================== plugin Execution End ({get_formatted_time(time.time())}) =====================')

        df_out_log, df_out_logDetail = vd_log_end()
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