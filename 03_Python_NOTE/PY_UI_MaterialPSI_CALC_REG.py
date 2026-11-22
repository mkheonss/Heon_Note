"""
* 프로그램명
    - PY_UI_MaterialPSI_CALC_REG

* 내용
    - Version이 신규 생성[DB에서 전처리 완료]되면 MG [Material PSI W, Material PSI Sub] 의 값을 계산하여 업데이트.
    - Material PSI Sub 기능은 o9의 AOP 필터가 제대로 작동되지 않아서 대안으로 만은 MG임.(향후 o9 필터 기능 정상화되면 관련 기능 삭제될 수 있음.)

* 변경이력
    - 2025.12.30 / Kihong Ju / Create

  

* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과 데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables
    - in_Material_Master
        Select ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Item Raw Material].[Item Raw Material]) on row,
            ({ Measure.[Mat Master_Constraint], Measure.[Mat Master_Constraint (Filter)]
            , Measure.[Mat Master_Group1], Measure.[Mat Master_Group1 (Filter)]
            , Measure.[Mat Master_Group2], Measure.[Mat Master_Group2 (Filter)]
            , Measure.[Mat Master_Constraint Period], Measure.[Mat Master_PO LT]}) on column
        where {Association(Measure.[Mat PSI W_Requirement]>=0)}
        ;

    - in_Material_PSI_W
        Select ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Time].[Week] * [Item Raw Material].[Item Raw Material] ) on row,
            ({Measure.[Mat PSI W_BG Signal], Measure.[Mat PSI W_Inventory], Measure.[Mat PSI W_Overdue], Measure.[Mat PSI W_PO Arrival]
            , Measure.[Mat PSI W_PO BOH], Measure.[Mat PSI W_PO Balance], Measure.[Mat PSI W_PO EOH], Measure.[Mat PSI W_PO Remain]
            , Measure.[Mat PSI W_PO Short Material], Measure.[Mat PSI W_PO Supply Material], Measure.[Mat PSI W_Requirement], Measure.[Mat PSI W_Requirement Material]
            , Measure.[Mat PSI W_SN Arrival], Measure.[Mat PSI W_SN BOH], Measure.[Mat PSI W_SN Balance], Measure.[Mat PSI W_SN EOH]
            , Measure.[Mat PSI W_SN Short Material], Measure.[Mat PSI W_SN Supply Material], Measure.[Mat PSI W_Unplanned]}) on column
        ;   

    - in_Version
        Select ([Version].[Version Name].[CWV_MP]) on row, () on column
        include memberproperties
            {[Version].[Version Name], [DisplayName], [Plan Week]}
        ;


* Output Tables
    - out_Material_PSI_W
        Select ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Time].[Week] * [Item Raw Material].[Item Raw Material] ) on row,
            ({Measure.[Mat PSI W_BG Signal], Measure.[Mat PSI W_Inventory], Measure.[Mat PSI W_Overdue], Measure.[Mat PSI W_PO Arrival]
            , Measure.[Mat PSI W_PO BOH], Measure.[Mat PSI W_PO Balance], Measure.[Mat PSI W_PO EOH], Measure.[Mat PSI W_PO Remain]
            , Measure.[Mat PSI W_PO Short Material], Measure.[Mat PSI W_PO Supply Material], Measure.[Mat PSI W_Requirement]
            , Measure.[Mat PSI W_Requirement Material], Measure.[Mat PSI W_SN Arrival], Measure.[Mat PSI W_SN BOH]
            , Measure.[Mat PSI W_SN Balance], Measure.[Mat PSI W_SN EOH], Measure.[Mat PSI W_SN Short Material]
            , Measure.[Mat PSI W_SN Supply Material], Measure.[Mat PSI W_Unplanned]}) on column
        ;

    - out_Material_PSI_Sub
        Select ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Item Raw Material].[Item Raw Material] ) on row, 
            ({Measure.[Mat PSI Sub_Constraint], Measure.[Mat PSI Sub_Constraint (Filter)]
            , Measure.[Mat PSI Sub_Group1], Measure.[Mat PSI Sub_Group1 (Filter)]
            , Measure.[Mat PSI Sub_Group2], Measure.[Mat PSI Sub_Group2 (Filter)]}) on column
        ;


* Flow Summary
    STEP 0. 전처리: rename 등 로직 전개에 필요한 작업 수행
        STEP 0-0. in_Version 에서 planweek 추출
        STEP 0-1. Sub Location, Item Raw Material별로 Planweek 부터 Planweek 포함 34주차를 데이터 프레임에 추가.
        STEP 0-2. 결측치는 0 으로 처리
        STEP 0-3. Version 컬럼 값 설정 'CWV_MP'
        
    STEP 1. in_Material_PSI_W 의 Requirement(Material) 계산
        Measure.[Mat PSI W_Requirement Material] = Measure.[Mat PSI W_Requirement] + Measure.[Mat PSI W_Unplanned]
             + Measure.[Mat PSI W_Overdue] 

    STEP 2. in_Material_PSI_W 의 BOH 값 계산 (SN, PO 구분)
        Step 2-1. Measure.[Mat PSI W_SN BOH]
            첫 주차(Planweek)인 경우, Measure.[Mat PSI W_Inventory] 값으로 생성하고, 
            이후 주차는 전주의 S/N EOH(Measure.[Mat PSI W_SN EOH]) 값으로 세팅한다.
        Step 2-2. Measure.[Mat PSI W_PO BOH]
            첫 주차(Planweek)인 경우, Measure.[Mat PSI W_Inventory] 값으로 생성하고, 
            이후 주차는 전주의 PO EOH(Measure.[Mat PSI W_PO EOH]) 값으로 세팅한다.

    STEP 3. in_Material_PSI_W 의 Supply Material 값 계산 (SN, PO 구분)
        Step 3-1. Measure.[Mat PSI W_SN Supply Material] 
            Measure.[Mat PSI W_SN BOH] + Measure.[Mat PSI W_SN Arrival] 계산 값이 
            Measure.[Mat PSI W_Requirement Material] 보다 크면 Measure.[Mat PSI W_Requirement Material] 값으로 세팅,
            그렇지 않으면, Measure.[Mat PSI W_SN BOH] + Measure.[Mat PSI W_SN Arrival] 값으로 세팅한다.
        Step 3-2. Measure.[Mat PSI W_PO Supply Material] 
            Measure.[Mat PSI W_PO BOH] + Measure.[Mat PSI W_SN Arrival] + Measure.[Mat PSI W_PO Arrival] 계산 값이 
            Measure.[Mat PSI W_Requirement Material] 보다 크면 Measure.[Mat PSI W_Requirement Material] 값으로 세팅,
            그렇지 않으면, Measure.[Mat PSI W_PO BOH] + Measure.[Mat PSI W_SN Arrival] + Measure.[Mat PSI W_PO Arrival] 값으로 세팅한다.           

    STEP 4. in_Material_PSI_W 의 Supply Material 값 계산 (SN, PO 구분)    
        Step 4-1. Measure.[Mat PSI W_SN Short Material]
            Measure.[Mat PSI W_Requirement Material] - Measure.[Mat PSI W_SN Supply Material] 계산하여 세팅한다.
        Step 4-2. Measure.[Mat PSI W_PO Short Material]
            Measure.[Mat PSI W_Requirement Material] - Measure.[Mat PSI W_PO Supply Material] 계산하여 세팅한다.

    STEP 5. in_Material_PSI_W 의 EOH 값 계산 (SN, PO 구분)   
        Step 5-1. Measure.[Mat PSI W_SN EOH]  
            Measure.[Mat PSI W_SN BOH] - Measure.[Mat PSI W_SN Supply Material] + Measure.[Mat PSI W_SN Arrival] 계산하여 세팅한다.
        Step 5-2. Measure.[Mat PSI W_PO EOH]  
            Measure.[Mat PSI W_PO BOH] - Measure.[Mat PSI W_PO Supply Material] + Measure.[Mat PSI W_SN Arrival] 
            + Measure.[Mat PSI W_PO Arrival] 계산하여 세팅한다.
            
    STEP 6. in_Material_PSI_W 의 Balance 값 계산 (SN, PO 구분)   
        Step 6-1. Measure.[Mat PSI W_SN Balance]   
            첫 주(Planweek)는, Measure.[Mat PSI W_SN BOH] + Measure.[Mat PSI W_SN Arrival] 
            - Measure.[Mat PSI W_Requirement Material] 계산하고,
            이후는, 전주 Measure.[Mat PSI W_SN Balance] + Measure.[Mat PSI W_SN Arrival] 
            - Measure.[Mat PSI W_Requirement Material] 계산하여 세팅한다.
        Step 6-2. Measure.[Mat PSI W_PO Balance] 
            첫 주(Planweek)는, Measure.[Mat PSI W_PO BOH] + Measure.[Mat PSI W_SN Arrival] 
            + Measure.[Mat PSI W_PO Arrival] - Measure.[Mat PSI W_Requirement Material] 계산하고,
            이 후는, 전주 Measure.[Mat PSI W_PO Balance] + Measure.[Mat PSI W_SN Arrival] 
            + Measure.[Mat PSI W_PO Arrival] - Measure.[Mat PSI W_Requirement Material] 계산하여 세팅한다.
            
    STEP 7. in_Material_PSI_W 의 Mat PSI W_BG Signal 값 계산 
        Step 7-0. in_Material_Master 의 PO LT, Constraint Period 값을 in_Material_PSI_W와 동일한 Grain 기준으로 붙여준다. 
        Step 7-1. 시작 주차를 포함하여 Ceiling(Measure.[Mat Master_PO LT] / 7.0 에 해당하는 주차인 경우 LT구간에 해당하여 '2' 값이 된다.
        Step 7-2. 시작 주차를 포함하여 Measure.[Mat Master_Constraint Period] 에 해당하면 Con. Period 구간에 해당함으로 '1' 값을 세팅한다.      


    STEP 8. in_Material_Master 의 컬럼명을 변경하여 Material_PSI_Sub를 생성한다. 
        (Version 별 기존 데이터 삭제 후 재 생성)
        
    STEP 9. Output 정리



* Validation :


* Execution :
     EXEC plugin instance [PY_UI_MaterialPSI_CALC_REG]
             for measures { [Mat PSI W_Requirement Material] }
        using scope ([Version].[Version Name].[CWV_MP])
        using arguments {
            (ExecutionMode, "MediumWeight")
            , (Param_OUT_VERSION, "CWV_MP")
            , ([MaxSliceTableCells],2000000000)
            , (MaxConcurrency, 1 )
            , (IncludeNullRows, False)
            , ([Param.o9_sys_log_level], "DEBUG")
        };

"""


import os.path
import time
from datetime import datetime, timedelta
import traceback
import inspect

from NSCMCommon import NSCMCommon as common
import pandas as pd
import numpy as np

from numba import njit      # For 문 실행용, 속도 매우 빠름(C, Fotran 수준)



########################################################################################################################
# o9 Column Class : Measure Name이 변경되는 경우 유연히 대처하기 위함. 
########################################################################################################################
class BaseColumnClass:
    @staticmethod
    def clean_column_name(column_name):
        '''
        컬럼 명을 변환합니다.
        - [].[] 구조: 앞쪽의 []를 제거 (예: '[Version].[Version Name]' -> 'Version.[Version Name]')
        - Measure.[메저명] 구조: 메저명만 추출 (예: 'Measure.[Mat Master_Constraint]' -> 'Mat Master_Constraint')
        - 그 외: 그대로 반환
        '''
        # 1. [].[] 구조 처리
        if column_name.startswith('[') and '].' in column_name:
            bracket_end = column_name.find('].')
            if bracket_end != -1:
                cleaned_prefix = column_name[1:bracket_end]
                remaining = column_name[bracket_end + 2:]  # '].' 이후
                return cleaned_prefix + '.' + remaining
        
        # 2. Measure.[메저명] 구조 처리
        if column_name.startswith('Measure.') and '[' in column_name and ']' in column_name:
            start = column_name.find('[')
            end = column_name.find(']', start)
            if start != -1 and end != -1:
                return column_name[start + 1:end]  # '['와 ']' 사이의 내용만 추출
        
        # 3. 조건에 맞지 않으면 원래 문자열 반환
        return column_name

    @classmethod
    def get_cleaned_columns_dataframe(cls):
        '''
        클래스에 선언된 컬럼명 속성들을 clean_column_name으로 변환하여,
        빈 DataFrame을 생성하여 반환합니다.
        - 대상: 키가 대문자이고 값이 문자열인 속성들 (순서대로).
        - 반환: pd.DataFrame (예: {'Version.[Version Name]': [], ...})
        '''
        cleaned_columns = {}
        for attr_name, attr_value in cls.__dict__.items():
            # 키가 대문자이고 값이 문자열인 속성만 대상
            if attr_name.isupper() and isinstance(attr_value, str):
                cleaned_name = cls.clean_column_name(attr_value)
                cleaned_columns[cleaned_name] = []
        return pd.DataFrame(cleaned_columns)

    @classmethod
    def get_reverse_column_mapping(cls):
        '''
        클래스에 선언된 컬럼명 속성들을 기반으로,
        클린드 컬럼명(키) -> 원본 컬럼명(값)으로 매핑하는 딕셔너리를 반환합니다.
        - 대상: 키가 대문자이고 값이 문자열인 속성들 (순서대로).
        - 반환: dict (예: {'Version.[Version Name]': '[Version].[Version Name]', ...})
        - 용도: DataFrame 컬럼명 변경에 사용 (df.rename(columns=mapping))
        '''
        reverse_mapping = {}
        for attr_name, attr_value in cls.__dict__.items():
            # 키가 대문자이고 값이 문자열인 속성만 대상
            if attr_name.isupper() and isinstance(attr_value, str):
                cleaned_name = cls.clean_column_name(attr_value)
                reverse_mapping[cleaned_name] = attr_value
        return reverse_mapping


# Version: Dimension (BaseColumnClass 상속)
class CL_Version(BaseColumnClass):
    VERSIONNAME = '[Version].[Version Name]'
    DISPLAYNAME = '[Version].[DisplayName]'
    PLANWEEK = '[Version].[Plan Week]'


# MG: Material Master (BaseColumnClass 상속)
class CL_Mat_Master(BaseColumnClass):
    VERSION = '[Version].[Version Name]'
    SUB_LOCATION = '[Sub Location].[Sub Location]'
    ITEM_RAW_MATERIAL = '[Item Raw Material].[Item Raw Material]'
    CONSTRAINT = 'Measure.[Mat Master_Constraint]'
    CONSTRAINT_FILTER = 'Measure.[Mat Master_Constraint (Filter)]'    
    CONSTRAINT_PERIOD = 'Measure.[Mat Master_Constraint Period]' 
    MASTER_GROUP1 = 'Measure.[Mat Master_Group1]' 
    MASTER_GROUP1_FILTER = 'Measure.[Mat Master_Group1 (Filter)]'
    MASTER_GROUP2 = 'Measure.[Mat Master_Group2]'
    MASTER_GROUP2_FILTER = 'Measure.[Mat Master_Group2 (Filter)]'
    MASTER_POLT = 'Measure.[Mat Master_PO LT]'


# MG: Material PSI Sub (BaseColumnClass 상속)
class CL_Mat_PSI_Sub(BaseColumnClass):
    VERSION = '[Version].[Version Name]'
    SUB_LOCATION = '[Sub Location].[Sub Location]'
    ITEM_RAW_MATERIAL = '[Item Raw Material].[Item Raw Material]'
    CONSTRAINT = 'Measure.[Mat PSI Sub_Constraint]'
    CONSTRAINT_FILTER = 'Measure.[Mat PSI Sub_Constraint (Filter)]'     
    MASTER_GROUP1 = 'Measure.[Mat PSI Sub_Group1]' 
    MASTER_GROUP1_FILTER = 'Measure.[Mat PSI Sub_Group1 (Filter)]'
    MASTER_GROUP2 = 'Measure.[Mat PSI Sub_Group2]'
    MASTER_GROUP2_FILTER = 'Measure.[Mat PSI Sub_Group2 (Filter)]'


# MG: Material PSI W (BaseColumnClass 상속)
class CL_Mat_PSI_W(BaseColumnClass):
    VERSION = '[Version].[Version Name]'
    SUB_LOCATION = '[Sub Location].[Sub Location]'
    ITEM_RAW_MATERIAL = '[Item Raw Material].[Item Raw Material]'
    WEEK = '[Time].[Week]'
    BG_SIGNAL = 'Measure.[Mat PSI W_BG Signal]' 
    INVENTORY ='Measure.[Mat PSI W_Inventory]' 
    OVERSDUE = 'Measure.[Mat PSI W_Overdue]' 
    PO_ARRIVAL = 'Measure.[Mat PSI W_PO Arrival]'
    PO_BOH = 'Measure.[Mat PSI W_PO BOH]' 
    PO_BALANCE = 'Measure.[Mat PSI W_PO Balance]'
    PO_EOH = 'Measure.[Mat PSI W_PO EOH]' 
    PO_REMAIN = 'Measure.[Mat PSI W_PO Remain]'
    PO_SHORT_MATERIAL = 'Measure.[Mat PSI W_PO Short Material]' 
    PO_SUPPLY_MATERIAL = 'Measure.[Mat PSI W_PO Supply Material]'
    REQUIREMENT = 'Measure.[Mat PSI W_Requirement]'
    REQUIREMENT_MATERIAL = 'Measure.[Mat PSI W_Requirement Material]'
    SN_ARRIVAL = 'Measure.[Mat PSI W_SN Arrival]'
    SN_BOH = 'Measure.[Mat PSI W_SN BOH]'
    SN_BALANCE ='Measure.[Mat PSI W_SN Balance]'
    SN_EOH = 'Measure.[Mat PSI W_SN EOH]'
    SN_SHORT_MATERIAL = 'Measure.[Mat PSI W_SN Short Material]'
    SN_SUPPLY_MATERIAL = 'Measure.[Mat PSI W_SN Supply Material]'
    UNPLANNED = 'Measure.[Mat PSI W_Unplanned]'




########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_MaterialPSI_CALC_REG"
str_input_dir = "Input/MasterPSI_CALC_REG"
str_output_dir = "Output/MasterPSI_CALC_REG"
is_local = common.gfn_get_isLocal()
is_print = True
flag_csv = True
flag_exception = True


########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level


def fn_log_dataframe(df_p_source: pd.DataFrame, str_p_source_name: str) -> None:
    """
    Dataframe 로그 출력 조건 지정 함수
    :param df_p_source: 로그로 찍을 Dataframe
    :param str_p_source_name: 로그로 찍을 Dataframe 명
    :return: None
    """
    is_output = False
    if str_p_source_name.startswith('out_'):
        is_output = True

    if is_print:
        logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
        if is_local and not df_p_source.empty and flag_csv:
            # 로컬 Debugging 시 csv 파일 출력
            df_p_source.to_csv(str_output_dir + "/" + str_p_source_name + ".csv", encoding="UTF8", index=False)
    else:
        # 최종 Output 테이블인 경우에는 무조건 로그 출력
        if is_output:
            logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)
            if is_local and not df_p_source.empty:
                # 로컬 Debugging 시 csv 파일 출력
                df_p_source.to_csv(str_output_dir + "/" + str_p_source_name + ".csv", encoding="UTF8", index=False)


def _decoration_(func):
    """
    1. 소스 내 함수 실행 시 반복되는 코드를 데코레이터로 변형하여 소스 라인을 줄일 수 있도록 함.
    2. 각 Step을 함수로 실행하는 경우 해당 함수에 뒤따르는 Step log 및 DF 로그, DF 로컬 출력을 데코레이터로 항상 출력하게 함.
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        # 함수 시작 시각
        tm_start = time.time()
        # 함수 실행
        result = func(*args)
        # 함수 종료 시각
        tm_end = time.time()
        # 함수 실행 시간 로그
        logger.Note(p_note=f'[{func.__name__}] Total time is {tm_end - tm_start:.5f} sec.',
                    p_log_level=LOG_LEVEL.debug())
        # Step log 및 DF 로컬 출력 등을 위한 Keywords 변수 확인
        # Step No
        _step_no = kwargs.get('p_step_no')
        _step_desc = kwargs.get('p_step_desc')
        _df_name = kwargs.get('p_df_name')
        _warn_desc = kwargs.get('p_warn_desc')

        # Step log 관련 변수가 입력된 경우 Step log 출력
        if _step_no is not None and _step_desc is not None:
            logger.Step(p_step_no=_step_no, p_step_desc=_step_desc)
        # Warning 메시지가 있는 경우
        if _warn_desc is not None:
            # 함수 실행 결과가 DF이면서 해당 DF가 비어 있는 경우
            if type(result) == pd.DataFrame and result.empty:
                logger.Note(p_note=_warn_desc, p_log_level=LOG_LEVEL.warning())
        # DF 명이 있는 경우 로그 및 로컬 출력
        if _df_name is not None:
            fn_log_dataframe(result, _df_name)

        return result

    return wrapper


def fn_check_input_table(df_p_source: pd.DataFrame, str_p_source_name: str, str_p_cond: str) -> None:
    """
    Input Table을 체크한 결과를 로그 또는 Exception으로 표시한다.
    :param df_p_source: Input table
    :param str_p_source_name: Name of Input table
    :param str_p_cond: '0' - Exception, '1' - Warning Log
    :return: None
    """
    # Input Table 로그 출력
    logger.PrintDF(p_df=df_p_source, p_df_name=str_p_source_name, p_log_level=LOG_LEVEL.debug(), p_format=1)

    if not df_p_source is None and df_p_source.empty:
        if str_p_cond == '0':
            # 테이블이 비어 있는 경우 raise Exception
            raise Exception(f'[Exception] Input table({str_p_source_name}) is empty.')
        else:
            # 테이블이 비어 있는 경우 Warning log
            logger.Note(p_note=f'Input table({str_p_source_name}) is empty.', p_log_level=LOG_LEVEL.warning())





@_decoration_
def fn_set_header(str_p_cond: str) -> pd.DataFrame:
    """
    MediumWeight로 실행 시 헤더 없는 Output 테이블이 있는 경우 오류가 발생하므로
    해당 오류를 방지하기 위해 헤더만 있는 DF를 생성함.
    :param str_p_cond: 0 - out_LoadingMasterFromSite,
                       1 - out_LoadingMasterToSite
                       2 - out_LoadingMasterAccount
                       3 - out_LoadingMasterShipTo
    :return: DataFrame
    """

    df_return = pd.DataFrame()
    # df_out_ActivityProdParam

    if str_p_cond == '0':
        df_return = pd.DataFrame(
            {
                'Version.[Version Name]': [], 'Activity1.[Activity1]': [],
                'Activity2.[Activity2]': [], 'Activity3.[Activity3]': [], 'Item.[Item]': [],
                'Location.[Location]': [], 'W Activity Priority': [], 'W LotSize Increment': [],
                'W Material Production Association': [], 'Material Production Association': [],
                'W Material Production Quantity Per': []
            }
        )
    return df_return


def fn_merge_after(df_p_source: pd.DataFrame) -> pd.DataFrame:
    """
    Merge 후처리
    :Merge 후 postfix '_y'가 붙은 컬럼 삭제, Merge 후 postfix '_x'가 붙은 컬럼에서 '_x' 삭제
    :param df_p_source: Merge 후처리 대상 DataFrame
    :return: DataFrame
    """

    # Merge 후 postfix '_y'가 붙은 컬럼 추출
    list_columns_y = df_p_source.filter(regex='_y$', axis=1).columns

    # Merge 후 postfix '_y'가 붙은 컬럼 삭제
    df_p_source.drop(list_columns_y, axis=1, inplace=True)

    # Merge 후 postfix '_x'가 붙은 컬럼에서 '_x' 삭제
    list_columns_all = df_p_source.columns
    list_columns_all_rename = []
    for col in list_columns_all:
        list_columns_all_rename.append(col.rstrip('_x'))

    df_p_source.columns = list_columns_all_rename
    
    return df_p_source # 결과 리턴


def planweek_to_week_list(planweek: int, n_weeks: int = 34) -> pd.Series:
    '''
    planweek(YYYYWW, ISO week)을 포함하여 n_weeks개의 YYYYWW(정수)를 생성
    '''
    s = str(planweek).zfill(6)
    iso_monday = pd.to_datetime(
        s[:4] + "-W" + s[4:] + "-1",
        format="%G-W%V-%u",
        errors="raise",
    )
    mondays = iso_monday + pd.to_timedelta(range(n_weeks), unit="W")
    iso = mondays.isocalendar()
    weeks = (iso["year"].astype(int) * 100 + iso["week"].astype(int)).astype("int64")
    return weeks


@_decoration_
def expand_df_weeks_with_mode(
    df_p_source: pd.DataFrame,
    planweek: int,
    col_sub_loc: str = "Sub Location.[Sub Location]",
    col_item: str = "Item Raw Material.[Item Raw Material]",
    col_week: str = "Time.[Week]",
    n_weeks: int = 34,
    mode: str = "truncate",
    fill_missing_weeks: bool = True,
    add_flag_is_new: bool = True
    ) -> pd.DataFrame:
    '''
    (Sub Location, Item Raw Material)별 Week를 planweek 포함 n_weeks로 확장하되,
    원본에 더 뒤 주차가 있는 경우를 mode로 제어한다.

    mode:
    - "truncate": planweek~planweek+ (n_weeks-1) 범위 밖의 원본 row 삭제
    - "keep":    planweek~범위는 확장으로 채우고, 범위 밖 원본 row는 유지

    fill_missing_weeks:
    - True면 planweek~범위에서 없는 주차 row를 생성
    - False면 생성은 하지 않고(원본 유지/필터만) 모드 동작만 수행

    add_flag_is_new:
    - True면 확장으로 새로 생긴 row에 is_new=True 표시
    '''

    print(f"🟧planweek: {planweek}")

    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame(df_p_source)을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    if mode not in ("truncate", "keep"):
        raise ValueError("mode must be 'truncate' or 'keep'")

    df = df_p_source.copy()

    # Week 정리: 문자열/숫자 혼재 대비
    df[col_week] = df[col_week].astype(str).str.strip()
    df["_week_iw"] = pd.to_numeric(df[col_week], errors="coerce")

    # 주차 파싱 실패 체크(원하면 에러로 바꿔도 됨)
    # 여기서는 NaN은 유지하되, 필터링 비교에서 제외될 수 있음
    # df["_week_iw"].isna().any() -> 필요 시 로깅

    # Planweek 윈도우 생성
    week_list = planweek_to_week_list(planweek=planweek, n_weeks=n_weeks)
    win_min = int(week_list.min())
    win_max = int(week_list.max())

    # 1) truncate면 원본을 윈도우로 자른다
    if mode == "truncate":
        df_base = df[df["_week_iw"].between(win_min, win_max, inclusive="both")].copy()
    else:
        df_base = df

    # 확장 자체를 안 한다면, (truncate/keep)만 적용해서 반환
    if not fill_missing_weeks:
        out = df_base.sort_values([col_sub_loc, col_item, "_week_iw"], kind="mergesort").reset_index(drop=True)
        out[col_week] = out["_week_iw"].astype("Int64").astype(str)
        out = out.drop(columns=["_week_iw"], errors="ignore")
        return out

    # (Sub Location, Item) 유니크 키
    keys = (
        df_base[[col_sub_loc, col_item]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # 키 x (34주) grid 생성
    grid = keys.merge(pd.DataFrame({"_week_iw": week_list}), how="cross")

    # 2) 윈도우 범위(grid)와 원본 결합 -> 누락 주차 row 생성
    out_win = grid.merge(
        df_base,
        on=[col_sub_loc, col_item, "_week_iw"],
        how="left",
        suffixes=("", "_orig"),
        indicator=add_flag_is_new,   # indicator는 True일 때만 생성
    )

    if add_flag_is_new:
        out_win["is_new"] = out_win["_merge"].eq("left_only")
        out_win = out_win.drop(columns=["_merge"], errors="ignore")

    out_win[col_week] = out_win["_week_iw"].astype("int64").astype(str)

    # 3) keep 모드면 윈도우 밖 원본을 다시 붙인다
    if mode == "keep":
        extra = df[df["_week_iw"].gt(win_max)].copy()
        # 윈도우보다 "이전" 주차도 유지할지 여부는 정책에 따라 다름.
        # 필요하면 아래 주석 해제해서 이전 주차도 붙이세요.
        # extra_prev = df[df["_week_iw"].lt(win_min)].copy()
        # extra = pd.concat([extra_prev, extra], ignore_index=True)

        if add_flag_is_new and not extra.empty:
            extra["is_new"] = False
        if not extra.empty:
            extra[col_week] = extra["_week_iw"].astype("Int64").astype(str)

        out = pd.concat([out_win, extra], ignore_index=True, sort=False)
    else:
        out = out_win

    # 정렬 및 정리
    out = out.sort_values([col_sub_loc, col_item, "_week_iw"], kind="mergesort").reset_index(drop=True)

    # 최종적으로 내부키 제거하고 싶으면 제거
    # out = out.drop(columns=["_week_iw"], errors="ignore")
    
    df_return = out.copy()
    return df_return


@njit(cache=False)
def _calc_one_pass_sub_item(
    sub_code: np.ndarray,
    item_code: np.ndarray,
    week: np.ndarray,
    inventory: np.ndarray,
    req: np.ndarray,
    unplanned: np.ndarray,
    overdue: np.ndarray,
    sn_arr: np.ndarray,
    po_arr: np.ndarray,
    first_week: int
):
    n = week.shape[0]
    req_mat = np.empty(n, dtype=np.float64)
    sn_boh  = np.empty(n, dtype=np.float64)
    po_boh  = np.empty(n, dtype=np.float64)
    sn_sup  = np.empty(n, dtype=np.float64)
    po_sup  = np.empty(n, dtype=np.float64)
    sn_short = np.empty(n, dtype=np.float64)
    po_short = np.empty(n, dtype=np.float64)
    sn_eoh  = np.empty(n, dtype=np.float64)
    po_eoh  = np.empty(n, dtype=np.float64)
    sn_bal  = np.empty(n, dtype=np.float64)
    po_bal  = np.empty(n, dtype=np.float64)

    is_first = np.empty(n, dtype=np.float64)    # 계산유무 확인 테스트용용

    prev_sub = -1       # Sub Location
    prev_item = -1      # Item Raw Material

    prev_sn_eoh = 0.0
    prev_po_eoh = 0.0

    group_first_inv = 0.0
    group_has_first_week = False

    for i in range(n):
        s = sub_code[i]
        it = item_code[i]

        is_first[i] = 0

        # (Sub location, Item Raw Material) 그룹 경계 감지
        if (s != prev_sub) or (it != prev_item):
            prev_sub = s
            prev_item = it

            group_has_first_week = False
            group_first_inv = inventory[i]   # 그룹 첫 행 inventory를 기본 first_inv로
            prev_sn_eoh = group_first_inv
            prev_po_eoh = group_first_inv

            # 🟧 [검증용] 그룹 경계 표기 
            # print(f"🟧 index:{i}, sub loc.: {s}, item: {it}, week: {week[i]}, inventory: {inventory[i]}")
            is_first[i] = 1


        # STEP1: Requirement Material
        r = req[i] + unplanned[i] + overdue[i]
        req_mat[i] = r

        # first_week 규칙: 그룹 내에서 Week==first_week를 만나면 그 행 inventory로 리셋
        if (not group_has_first_week) and (week[i] == first_week):
            group_has_first_week = True
            group_first_inv = inventory[i]
            prev_sn_eoh = group_first_inv
            prev_po_eoh = group_first_inv

        # STEP2: BOH = 전주 EOH (첫주차 행은 위에서 prev_eoh를 inventory로 리셋했으므로 동일하게 처리됨)
        sn_boh_i = prev_sn_eoh
        po_boh_i = prev_po_eoh

        sn_boh[i] = sn_boh_i
        po_boh[i] = po_boh_i

        # STEP3: Supply Material
        sn_supply_calc = sn_boh_i + sn_arr[i]
        sn_sup_i = r if r < sn_supply_calc else sn_supply_calc
        sn_sup[i] = sn_sup_i

        po_supply_calc = po_boh_i + sn_arr[i] + po_arr[i]
        po_sup_i = r if r < po_supply_calc else po_supply_calc
        po_sup[i] = po_sup_i

        # STEP4: Short Material
        sn_short_i = r - sn_sup_i
        po_short_i = r - po_sup_i
        sn_short[i] = sn_short_i
        po_short[i] = po_short_i

        # STEP5: EOH
        # sn_eoh_i = max((sn_sup_i - r), 0)
        # po_eoh_i = max((po_sup_i - r), 0)
        sn_eoh_i = sn_boh_i - sn_sup_i + sn_arr[i]
        po_eoh_i = po_boh_i - po_sup_i + sn_arr[i] + po_arr[i]
        sn_eoh[i] = sn_eoh_i
        po_eoh[i] = po_eoh_i

        prev_sn_eoh = sn_eoh_i
        prev_po_eoh = po_eoh_i

        # STEP6: Balance
        # first_week 규칙: 그룹 내에서 Week==first_week를 만나면 당주 값들로 계산, 이 후 주차는 전주의 Balance 값을 참고하여 계산산
        if (group_has_first_week) and (week[i] == first_week):
            group_sn_first_bal = sn_boh_i + sn_arr[i] - r
            group_po_first_bal = po_boh_i + sn_arr[i] + + po_arr[i] - r

            prev_sn_val = group_sn_first_bal
            prev_po_val = group_po_first_bal

            sn_val_i = group_sn_first_bal
            po_val_i = group_po_first_bal

        else:
            sn_val_calc = prev_sn_val + sn_arr[i] - r 
            po_val_calc = prev_po_val + sn_arr[i] + po_arr[i] - r

            sn_val_i = sn_val_calc
            po_val_i = po_val_calc

            prev_sn_val = sn_val_i
            prev_po_val = po_val_i

        sn_bal[i] = sn_val_i
        po_bal[i] = po_val_i

    return (req_mat, sn_boh, po_boh, sn_sup, po_sup, sn_short, po_short, sn_eoh, po_eoh, sn_bal, po_bal, is_first)      # is_first은 계산 테스트용


@_decoration_
def calculate_psi_data(
    df_p_source: pd.DataFrame, 
    first_week: int
    ) -> pd.DataFrame:
    """
    Mat PSI W 테이블의 값 계산
    :param df_p_source: Material PSI W [in_Material_PSI_W]
    :first_week: planweek
    :return: DataFrame
    """

    # 함수명
    str_my_name = inspect.stack()[0][3]
    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame(df_p_source)을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source

    # 0) 컬럼명 선언언
    col_sub_loc = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SUB_LOCATION)     # 'Sub Location.[Sub Location]'
    col_item = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.ITEM_RAW_MATERIAL)   # 'Item Raw Material.[Item Raw Material]'
    col_week = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.WEEK)            #'Time.[Week]'

    col_inv = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.INVENTORY)        # 'Mat PSI W_Inventory'
    col_req = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.REQUIREMENT)      # 'Mat PSI W_Requirement'
    col_upl = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.UNPLANNED)        # 'Mat PSI W_Unplanned'
    col_ovr =  CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.OVERSDUE)        # 'Mat PSI W_Overdue'
    col_sn_arr = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_ARRIVAL)    # 'Mat PSI W_SN Arrival'
    col_po_arr = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_ARRIVAL)    # 'Mat PSI W_PO Arrival'

    col_req_mat = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.REQUIREMENT_MATERIAL)       #'Mat PSI W_Requirement Material'
    col_sn_boh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_BOH)    # 'Mat PSI W_SN BOH'
    col_po_boh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_BOH)    # 'Mat PSI W_PO BOH'
    col_sn_sup = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_SUPPLY_MATERIAL)   # 'Mat PSI W_SN Supply Material'
    col_po_sup = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_SUPPLY_MATERIAL)   # 'Mat PSI W_PO Supply Material

    col_sn_short = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_SHORT_MATERIAL)  # Mat PSI W_SN Short Material'
    col_po_short = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_SHORT_MATERIAL)  # Mat PSI W_PO Short Material'

    col_sn_eoh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_EOH)    # 'Mat PSI W_SN EOH'
    col_po_eoh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_EOH)    # 'Mat PSI W_PO EOH'

    col_sn_bal = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_BALANCE)    # 'Mat PSI W_SN Balance'
    col_po_bal = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_BALANCE)    # 'Mat PSI W_PO Balance'


    # 1) 정렬 필수: Sub location, Item, Week
    df2 = df_p_source.sort_values([col_sub_loc, col_item, col_week], kind="mergesort").reset_index(drop=True)

    # 2) key를 category.codes로 변환 (Numba 호환/속도)
    sub_cat = df2[col_sub_loc].astype("category")
    item_cat = df2[col_item].astype("category")

    sub_code = sub_cat.cat.codes.to_numpy(np.int32, copy=False)
    item_code = item_cat.cat.codes.to_numpy(np.int32, copy=False)

    week = df2[col_week].to_numpy(np.int64, copy=False)

    # 3) 수치 컬럼을 numpy로
    inventory = df2[col_inv].to_numpy(np.float64, copy=False)
    req = df2[col_req].to_numpy(np.float64, copy=False)
    unplanned = df2[col_upl].to_numpy(np.float64, copy=False)
    overdue = df2[col_ovr].to_numpy(np.float64, copy=False)
    sn_arr = df2[col_sn_arr].to_numpy(np.float64, copy=False)
    po_arr = df2[col_po_arr].to_numpy(np.float64, copy=False)

    out = _calc_one_pass_sub_item(
        sub_code, item_code, week,
        inventory, req, unplanned, overdue,
        sn_arr, po_arr,
        int(first_week)
    )

    (req_mat, sn_boh, po_boh, sn_sup, po_sup, sn_short, po_short, sn_eoh, po_eoh, sn_bal, po_bal, is_first) = out       # is_first는 계산확인용

    df2[col_req_mat] = req_mat
    df2[col_sn_boh] = sn_boh
    df2[col_po_boh] = po_boh
    df2[col_sn_sup] = sn_sup
    df2[col_po_sup] = po_sup
    df2[col_sn_short] = sn_short
    df2[col_po_short] = po_short
    df2[col_sn_eoh] = sn_eoh
    df2[col_po_eoh] = po_eoh
    df2[col_sn_bal] = sn_bal
    df2[col_po_bal] = po_bal

    df2['is_first_week'] = is_first 
    df_return = df2

    return df_return


@njit(cache=False)
def _build_bg_signal_const_planweek(
    sub_code: np.ndarray,
    item_code: np.ndarray,
    week: np.ndarray,
    lt_weeks: np.ndarray,
    constraint_weeks: np.ndarray,
    planweek: int
) -> np.ndarray:
    '''
    그룹키: (sub_code, item_code)
    정렬: Sub location, Item, Week (오름차순)
    lt_weeks: ceil(PO_LT/7) (int64)
    constraint_weeks: Mat Master_Constraint Period (int64)
    '''

    n = week.shape[0]
    sig = np.zeros(n, dtype=np.int8)


    prev_sub = -1
    prev_item = -1

    # 그룹 상태
    first_idx = -1
    target_idx = -1
    limit_idx = -1
    found_planweek = False

    for i in range(n):
        s = sub_code[i]
        it = item_code[i]

        # 그룹 시작 감지: (Sub, Item) 둘 중 하나라도 바뀌면 리셋
        if (s != prev_sub) or (it != prev_item):
            prev_sub = s
            prev_item = it

            first_idx = -1
            target_idx = -1
            limit_idx = -1
            found_planweek = False

        # planweek(상수) 행 찾기
        if (not found_planweek) and (week[i] == planweek):
            found_planweek = True
            first_idx = i

            lw = lt_weeks[i]          # 이 그룹의 lt_weeks (그룹 내 동일하다고 가정)
            cw = constraint_weeks[i]  # 이 그룹의 constraint_weeks (그룹 내 동일하다고 가정)

            # 유효성: -1이면 적용 안 함
            target_idx = first_idx + lw -1 if lw >= 0 else -1   # planweek 포함해서 N개 주
            limit_idx = first_idx + cw - 1 if cw >= 0 else -1   # planweek 포함해서 N개 주

        # planweek가 그룹에 존재할 때만 마킹
        if found_planweek:

            # Target week -> 2
            if (target_idx != -1) and (i <= target_idx):
                sig[i] = 2
                # print(f"BG: 2, index: {i}")

            # Constraint range: [first_idx, limit_idx] -> 1
            if (limit_idx != -1) and (i >= first_idx) and (i <= limit_idx):
                sig[i] = 1
                # print(f"BG: 1, index: {i}")

    return sig


@_decoration_
def build_bg_signal_planweek_const(
    df_p_source: pd.DataFrame,
    df_mat_master: pd.DataFrame,
    planweek: int,
    col_sub: str = "Sub location",
    col_item: str = "Item",
    col_week: str = "Week",
    col_po_lt: str = "Mat Master_PO LT",
    col_cp: str = "Mat Master_Constraint Period",
    out_col: str = "Mat PSI W_BG Signal",
    keep_master_cols: bool = False,
) -> pd.DataFrame:
    '''
    df_mat_master: 키(col_sub, col_item) / 값(col_po_lt, col_cp)
    planweek: 상수(예: 202532)


    규칙
    - lt_weeks = ceil(PO_LT/7)
    => (Sub, Item) 그룹에서 Week==planweek인 행을 first_idx로 두고
        first_idx + lt_weeks 위치의 행에 BG Signal=2
    - constraint_weeks = Constraint Period
    => first_idx ~ first_idx+constraint_weeks 구간에 BG Signal=1
    - 우선순위: 2 > 1
    '''

    # 함수명
    str_my_name = inspect.stack()[0][3]

    # Return 변수
    df_return = pd.DataFrame()

    # 입력 파라미터가 비어 있는 경우 비어 있는 DataFrame(df_p_source)을 리턴
    if df_p_source.empty:
        logger.Note(p_note=f'[{str_my_name}] 입력으로 받은 데이터(df_p_source)가 비어 있습니다.',
                    p_log_level=LOG_LEVEL.warning())
        return df_p_source
    
    # 데이터 수정 전 원본 DF 복사
    df_return = df_p_source.copy(deep=True)

    # 1) 필수 컬럼 체크
    req_2 = [col_sub, col_item, col_week]
    miss_2 = [c for c in req_2 if c not in df_return.columns]
    if miss_2:
        raise KeyError(f"df_p_source 필수 컬럼 누락: {miss_2}")

    req_m = [col_sub, col_item, col_po_lt, col_cp]
    miss_m = [c for c in req_m if c not in df_mat_master.columns]
    if miss_m:
        raise KeyError(f"df_mat_master 필수 컬럼 누락: {miss_m}")

    # 2) 마스터 merge (left)
    df_return = df_return.merge(
        df_mat_master[[col_sub, col_item, col_po_lt, col_cp]],
        on=[col_sub, col_item],
        how="left",
        copy=False,
    )

    # 3) 타입 정리
    df_return[col_week] = pd.to_numeric(df_return[col_week], errors="raise").astype(np.int64)

    # 4) lt_weeks = ceil(PO_LT/7), 결측은 -1(적용 안 함)
    po_lt_num = pd.to_numeric(df_return[col_po_lt], errors="coerce").to_numpy(np.float64, copy=False)
    lt_weeks = np.ceil(po_lt_num / 7.0)
    lt_weeks = np.where(np.isfinite(lt_weeks), lt_weeks, -1).astype(np.int64)

    # 5) constraint_weeks, 결측은 -1(적용 안 함)
    cp_num = pd.to_numeric(df_return[col_cp], errors="coerce").to_numpy(np.float64, copy=False)
    constraint_weeks = np.where(np.isfinite(cp_num), cp_num, -1).astype(np.int64)

    # 6) 정렬 (필수)
    df_return = df_return.sort_values([col_sub, col_item, col_week], kind="mergesort").reset_index(drop=True)

    # 7) 그룹 코드
    sub_code = df_return[col_sub].astype("category").cat.codes.to_numpy(np.int32, copy=False)
    item_code = df_return[col_item].astype("category").cat.codes.to_numpy(np.int32, copy=False)
    week = df_return[col_week].to_numpy(np.int64, copy=False)

    # 8) Numba 1-pass
    sig = _build_bg_signal_const_planweek(
        sub_code=sub_code,
        item_code=item_code,
        week=week,
        lt_weeks=lt_weeks,
        constraint_weeks=constraint_weeks,
        planweek=int(planweek),
    )

    df_return[out_col] = sig

    # 9) master 컬럼 제거 옵션
    if not keep_master_cols:
        df_return = df_return.drop(columns=[col_po_lt, col_cp])

    # 컬럼 정렬
    # PSI W 빈 데이터 프레임 생성 [컬럼 리스트 활용용]
    out_psi_w = CL_Mat_PSI_W.get_cleaned_columns_dataframe()

    # df_calculated_BG에서 out_psi_w과 일치하는 컬럼만 필터링
    psi_w_cols = [col for col in df_return.columns if col in out_psi_w]
    df_return = df_return[psi_w_cols]

    # 컬럼순서 재정렬
    df_return = df_return.reindex(columns=out_psi_w.columns)

    return df_return



if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_Material_PSI_W = pd.DataFrame()
    out_Material_PSI_Sub = pd.DataFrame()

    try:

        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
                Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = ''
            Param_PLANTYPE = ''

            in_Material_PSI_W = pd.read_csv(str_input_dir + "/in_Material_PSI_W.csv", encoding="UTF8")
            in_Material_Master = pd.read_csv(str_input_dir + "/in_Material_Master.csv", encoding="UTF8")
            in_Version = pd.read_csv(str_input_dir + "/in_Version.csv", encoding="UTF8")

        # 입력 변수 확인
        if Param_OUT_VERSION is None or Param_OUT_VERSION.strip() == '':
            Param_OUT_VERSION = 'CWV_MP'

        # 입력 변수 확인
        if Param_Exception_Flag is None or Param_Exception_Flag.strip() == '':
            flag_exception = True
        elif Param_Exception_Flag == 'S':
            flag_exception = False

        # 입력 변수 확인용 로그
        logger.Note(p_note=f'Param_OUT_VERSION : {Param_OUT_VERSION}')
        logger.Note(p_note=f'Param_Exception_Flag : {Param_Exception_Flag}', p_log_level=LOG_LEVEL.debug())

        # 입력 테이블 점검 및 로그
        fn_check_input_table(in_Material_PSI_W, 'in_Material_PSI_W', '0')
        fn_check_input_table(in_Material_Master, 'in_Material_Master', '0')
        fn_check_input_table(in_Version, 'in_Version', '0')

        ################################################################################################################
        # STEP 0. 전처리
        ################################################################################################################

        # 컬럼명 선언: Material PSI W
        col_sub_loc = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SUB_LOCATION)     # 'Sub Location.[Sub Location]'
        col_item = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.ITEM_RAW_MATERIAL)   # 'Item Raw Material.[Item Raw Material]'
        col_week = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.WEEK)                #'Time.[Week]'

        col_inv = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.INVENTORY)            # 'Mat PSI W_Inventory'
        col_req = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.REQUIREMENT)          # 'Mat PSI W_Requirement'
        col_upl = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.UNPLANNED)            # 'Mat PSI W_Unplanned'
        col_ovr =  CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.OVERSDUE)            # 'Mat PSI W_Overdue'
        col_sn_arr = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_ARRIVAL)        # 'Mat PSI W_SN Arrival'
        col_po_arr = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_ARRIVAL)        # 'Mat PSI W_PO Arrival'

        col_req_mat = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.REQUIREMENT_MATERIAL)     #'Mat PSI W_Requirement Material'
        col_sn_boh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_BOH)            # 'Mat PSI W_SN BOH'
        col_po_boh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_BOH)            # 'Mat PSI W_PO BOH'
        col_sn_sup = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_SUPPLY_MATERIAL)   # 'Mat PSI W_SN Supply Material'
        col_po_sup = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_SUPPLY_MATERIAL)   # 'Mat PSI W_PO Supply Material

        col_sn_short = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_SHORT_MATERIAL)  # Mat PSI W_SN Short Material'
        col_po_short = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_SHORT_MATERIAL)  # Mat PSI W_PO Short Material'

        col_sn_eoh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_EOH)            # 'Mat PSI W_SN EOH'
        col_po_eoh = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_EOH)            # 'Mat PSI W_PO EOH'

        col_sn_bal = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.SN_BALANCE)        # 'Mat PSI W_SN Balance'
        col_po_bal = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.PO_BALANCE)        # 'Mat PSI W_PO Balance'

        col_bg = CL_Mat_PSI_W.clean_column_name(CL_Mat_PSI_W.BG_SIGNAL)             # 'Mat PSI W_BG Signal'

        # 컬럼명 선언: Material Master
        col_po_lt = CL_Mat_Master.clean_column_name(CL_Mat_Master.MASTER_POLT)      # 'Mat Master_PO LT'
        col_cp = CL_Mat_Master.clean_column_name(CL_Mat_Master.CONSTRAINT_PERIOD)   # 'Mat Master_Constraint Period'


        # STEP 0-0. in_Version 에서 planweek 추출
        v_Planweek = in_Version[CL_Version.clean_column_name(CL_Version.PLANWEEK)][0]
        # print(f"planweek from in_Version: {v_Planweek}")

        ##🟩 로컬 개발시: 하드 코딩 (현재 개발 테넌트의 버전 정보가 불확실실)
        #v_Planweek = 202546
        print(f"🟩 planweek: {v_Planweek}")

        # STEP 0-1. Sub Location, Item Raw Material별로 Planweek 부터 Planweek 포함 34주차를 데이터 프레임에 추가.
        # Sub Loc., Item Raw Mtrl. 별로 Week 정렬렬
        in_Material_PSI_W = in_Material_PSI_W.sort_values([col_sub_loc, col_item, col_week], kind="mergesort").reset_index(drop=True)

        # 주차 결측치 추가 [Planweek 포함 34주 구간]
        dict_log = {
            'p_step_no': 0000,
            'p_step_desc': 'STEP 0. 전처리. 컬럼 클래스 및 planweek 포함 34주차 생성성',
            'p_df_name': 'in_Material_PSI_W_init'
        }
        in_Material_PSI_W_init = expand_df_weeks_with_mode(
            in_Material_PSI_W,
            v_Planweek,
            col_sub_loc=col_sub_loc,
            col_item=col_item,
            col_week=col_week,
            n_weeks=34,
            mode="truncate",
            fill_missing_weeks=True,
            add_flag_is_new=True, **dict_log
        )

        # STEP 0-2. 결측치는 0 으로 처리
        in_Material_PSI_W_init['is_first_week'] = 0
        in_Material_PSI_W_init = in_Material_PSI_W_init.fillna(0)

        # STEP 0-3. Version 컬럼 값 설정 'CWV_MP'
        in_Material_PSI_W_init[CL_Mat_PSI_Sub.clean_column_name(CL_Mat_PSI_Sub.VERSION)] = 'CWV_MP'

        ################################################################################################################
        # STEP 1 ~ STEP 6 : Numba 라이브러리로 1-Pass Loop 실행.
        ################################################################################################################
        dict_log = {
            'p_step_no': 1060,
            'p_step_desc': ' [STEP 1 ~ STEP 6] Numba 라이브러리로 1-Pass Loop 실행(PSI W 계산).',
            'p_df_name': 'df_calculated'
        }
        in_Material_PSI_W_initialized = in_Material_PSI_W_init.copy()
        df_calculated = calculate_psi_data(in_Material_PSI_W_initialized, v_Planweek, **dict_log)


        ################################################################################################################
        # STEP 7. in_Material_PSI_W 의 Mat PSI W_BG Signal 값 계산 
        ################################################################################################################
        dict_log = {
            'p_step_no': 7000,
            'p_step_desc': 'Step 7. in_Material_PSI_W 의 Mat PSI W_BG Signal 값 계산 ',
            'p_df_name': 'out_Material_PSI_W'
        }
        out_Material_PSI_W = build_bg_signal_planweek_const(
            df_calculated,
            in_Material_Master,
            v_Planweek,
            col_sub_loc,
            col_item,
            col_week,
            col_po_lt,
            col_cp,
            col_bg,
            keep_master_cols=False, **dict_log
        )


        ################################################################################################################
        # STEP 8. in_Material_Master 의 컬럼명을 변경하여 Material_PSI_Sub를 생성한다.
        ################################################################################################################
        sub_columns_map = {
            CL_Mat_Master.clean_column_name(CL_Mat_Master.CONSTRAINT) : CL_Mat_PSI_Sub.clean_column_name(CL_Mat_PSI_Sub.CONSTRAINT),
            CL_Mat_Master.clean_column_name(CL_Mat_Master.CONSTRAINT_FILTER) : CL_Mat_PSI_Sub.clean_column_name(CL_Mat_PSI_Sub.CONSTRAINT_FILTER),
            CL_Mat_Master.clean_column_name(CL_Mat_Master.MASTER_GROUP1) : CL_Mat_PSI_Sub.clean_column_name(CL_Mat_PSI_Sub.MASTER_GROUP1),
            CL_Mat_Master.clean_column_name(CL_Mat_Master.MASTER_GROUP1_FILTER) :  CL_Mat_PSI_Sub.clean_column_name(CL_Mat_PSI_Sub.MASTER_GROUP1_FILTER),
            CL_Mat_Master.clean_column_name(CL_Mat_Master.MASTER_GROUP2) : CL_Mat_PSI_Sub.clean_column_name(CL_Mat_PSI_Sub.MASTER_GROUP2),
            CL_Mat_Master.clean_column_name(CL_Mat_Master.MASTER_GROUP2_FILTER) :  CL_Mat_PSI_Sub.clean_column_name(CL_Mat_PSI_Sub.MASTER_GROUP2_FILTER),  
        }

        df_psi_sub = in_Material_Master.rename(columns=sub_columns_map)
        out_psi_sub = CL_Mat_PSI_Sub.get_cleaned_columns_dataframe()

        # df_psi_sub에서 df1_cols_flat과 일치하는 컬럼만 필터링
        common_cols = [col for col in df_psi_sub.columns if col in out_psi_sub]
        out_Material_PSI_Sub = df_psi_sub[common_cols]

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()

        if flag_exception:
            out_Material_PSI_W = None
            out_Material_PSI_Sub = None
            raise Exception(e)
        else:
            if out_Material_PSI_W.empty:
                out_Material_PSI_W = CL_Mat_PSI_W.get_cleaned_columns_dataframe()

            if out_Material_PSI_Sub.empty:
                out_Material_PSI_Sub = CL_Mat_PSI_Sub.get_cleaned_columns_dataframe()
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    else:
        if out_Material_PSI_W.empty:
            out_Material_PSI_W = CL_Mat_PSI_W.get_cleaned_columns_dataframe()
        if out_Material_PSI_Sub.empty:
            out_Material_PSI_Sub = CL_Mat_PSI_Sub.get_cleaned_columns_dataframe()
        logger.Finish()

    finally:
        # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
        # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들어어 줌.

        if out_Material_PSI_W.empty:
            out_Material_PSI_W = CL_Mat_PSI_W.get_cleaned_columns_dataframe()
            fn_log_dataframe(out_Material_PSI_W, 'out_Material_PSI_W')

        if out_Material_PSI_Sub.empty:
            out_Material_PSI_Sub = CL_Mat_PSI_Sub.get_cleaned_columns_dataframe()
            fn_log_dataframe(out_Material_PSI_Sub, 'out_Material_PSI_Sub')

        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')