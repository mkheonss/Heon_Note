"""
* 프로그램명
    - PY_UI_MaterialShortAnalysis_REG

* 내용
    - Version이 신규 생성[DB에서 전처리 완료]되면 MG [Material Short Analysis W] 의 누락 주차를 생성하고 초기값을 적용하여 업데이트.

* 변경이력
    - 2026.01.09 / Kihong Ju / Create


* Script Params
    - Param_OUT_VERSION : 기본값 : CWV_MP, 호출시에, 결과 데이터를 Version Name을 별도로 지정하는데에 사용.

* Input Tables  
    - in_Material_Short_Analysis_W
        Select ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Time].[Week] * [Item Raw Material].[Item Raw Material]) on row,
            ({Measure.[Mat Short Analysis W_Is Short Analysis Data]
            , Measure.[Mat Short Analysis W_Resolving]
            , Measure.[Mat Short Analysis W_Short]}) on column
        ;

    - in_Version
        Select ([Version].[Version Name].[CWV_MP]) on row, () on column
        include memberproperties
            {[Version].[Version Name], [DisplayName], [Plan Week]}
        ;

* Output Tables
    - out_Material_Short_Analysis_W
        Select ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Time].[Week] * [Item Raw Material].[Item Raw Material]) on row,
            ({Measure.[Mat Short Analysis W_Is Short Analysis Data]
            , Measure.[Mat Short Analysis W_Resolving]
            , Measure.[Mat Short Analysis W_Short]}) on column
        ;


* Flow Summary
    STEP 0. 전처리: rename 등 로직 전개에 필요한 작업 수행
        STEP 0-0. in_Version 에서 planweek 추출
        STEP 0-1. Sub Location, Item Raw Material별로 Planweek 부터 Planweek 포함 34주차를 데이터 프레임에 추가.
        STEP 0-2. 추가된 주차의 데이터 및 결측치는 아래 값으로 처리 
            Measure.[Mat Short Analysis W_Short] = 0
            Measure.[Mat Short Analysis W_Is Short Analysis Data] = "Y"
        STEP 0-3. Version 컬럼 값 설정 'CWV_MP'
        
    STEP 1. in_Material_PSI_W 의 Requirement(Material) 계산
        Measure.[Mat PSI W_Requirement Material] = Measure.[Mat PSI W_Requirement] + Measure.[Mat PSI W_Unplanned]
             + Measure.[Mat PSI W_Overdue] 


        
    STEP 9. Output 정리



* Validation :


* Execution :
     EXEC plugin instance [PY_UI_MaterialShortAnalysis_REG]
            for measures { [Mat Short Analysis W_Is Short Analysis Data] }
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


# MG: Material PSI W (BaseColumnClass 상속)
class CL_Mat_Short_Analysis_W(BaseColumnClass):
    VERSION = '[Version].[Version Name]'
    SUB_LOCATION = '[Sub Location].[Sub Location]'
    ITEM_RAW_MATERIAL = '[Item Raw Material].[Item Raw Material]'
    WEEK = '[Time].[Week]'
    IS_SHORT = 'Measure.[Mat Short Analysis W_Is Short Analysis Data]'
    RESOLVING = 'Measure.[Mat Short Analysis W_Resolving]'
    SHORT = 'Measure.[Mat Short Analysis W_Short]'



########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = "PY_UI_MaterialShortAnalysis_REG"
str_input_dir = "Input/MaterialShortAnalysis_REG"
str_output_dir = "Output/MaterialShortAnalysis_REG"
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

    print(f"🟧 planweek: {planweek}")

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



if __name__ == '__main__':
    logger.debug(f'[START] {str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    logger.Start()

    # Output 테이블 선언
    out_Material_Short_Analysis_W = pd.DataFrame()

    try:

        if is_local:
            # 로컬인 경우 Output 폴더를 정리한다.
            for file in os.scandir(str_output_dir):
                os.remove(file.path)

            # 로컬인 경우 파일을 읽어 입력 변수를 정의한다.
            Param_OUT_VERSION = 'CWV_MP'
            Param_Exception_Flag = ''
            Param_PLANTYPE = ''

            in_Material_Short_Analysis_W = pd.read_csv(str_input_dir + "/in_Material_Short_Analysis_W.csv", encoding="UTF8")
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
        fn_check_input_table(in_Material_Short_Analysis_W, 'in_Material_Short_Analysis_W', '0')
        fn_check_input_table(in_Version, 'in_Version', '0')

        ################################################################################################################
        # STEP 0. 전처리
        ################################################################################################################

        # 컬럼명 선언: Material Short Analysis W
        col_sub_loc = CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.SUB_LOCATION)     # 'Sub Location.[Sub Location]'
        col_item = CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.ITEM_RAW_MATERIAL)   # 'Item Raw Material.[Item Raw Material]'
        col_week = CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.WEEK)                #'Time.[Week]'

        # STEP 0-0. in_Version 에서 planweek 추출
        v_Planweek = in_Version[CL_Version.clean_column_name(CL_Version.PLANWEEK)][0]
        print(f"🟩 planweek: {v_Planweek}")

        # STEP 0-1. Sub Location, Item Raw Material별로 Planweek 부터 Planweek 포함 34주차를 데이터 프레임에 추가.
        # Sub Loc., Item Raw Mtrl. 별로 Week 정렬렬
        in_Material_Short_Analysis_W = in_Material_Short_Analysis_W.sort_values([col_sub_loc, col_item, col_week], kind="mergesort").reset_index(drop=True)

        # 주차 결측치 추가 [Planweek 포함 34주 구간]
        dict_log = {
            'p_step_no': 1000,
            'p_step_desc': 'STEP 1. 전처리. 컬럼 클래스 및 planweek 포함 34주차 생성',
            'p_df_name': 'in_Material_Short_Analysis_W_init'
        }
        in_Material_Short_Analysis_W_init = expand_df_weeks_with_mode(
            in_Material_Short_Analysis_W,
            v_Planweek,
            col_sub_loc=col_sub_loc,
            col_item=col_item,
            col_week=col_week,
            n_weeks=34,
            mode="truncate",
            fill_missing_weeks=True,
            add_flag_is_new=True, **dict_log
        )

        # in_Material_Short_Analysis_W_init 의 is_new 컬럼이 True이고, SHORT와 RESOLVING 컬럼의 값이 NaN인 행들을 찾아서
        # SHORT와 RESOLVING을 0으로 채우고, IS_SHORT를 'Y'로 채우는 코드
        mask = ((in_Material_Short_Analysis_W_init['is_new'] == True) 
                & in_Material_Short_Analysis_W_init[CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.SHORT)].isna() 
                & in_Material_Short_Analysis_W_init[CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.RESOLVING)].isna()
        )

        in_Material_Short_Analysis_W_init.loc[mask, CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.SHORT)] = 0
        in_Material_Short_Analysis_W_init.loc[mask, CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.IS_SHORT)] = 'Y'

        # Version 컬럼 값 설정 'CWV_MP'
        in_Material_Short_Analysis_W_init[CL_Mat_Short_Analysis_W.clean_column_name(CL_Mat_Short_Analysis_W.VERSION)] = 'CWV_MP'

        # Material_Short_Analysis_W 빈 데이터 프레임 생성 [컬럼 리스트 활용]
        out_Material_Short_Analysis_W_Cleaned = CL_Mat_Short_Analysis_W.get_cleaned_columns_dataframe()

        # in_Material_Short_Analysis_W_init 에서 out_Material_Short_Analysis_W_Cleaned 와 일치하는 컬럼만 필터링
        short_analysis_w_cols = [col for col in in_Material_Short_Analysis_W_init.columns if col in out_Material_Short_Analysis_W_Cleaned]
        out_Material_Short_Analysis_W = in_Material_Short_Analysis_W_init[short_analysis_w_cols]

        # 컬럼순서 재정렬
        out_Material_Short_Analysis_W = out_Material_Short_Analysis_W.reindex(columns=out_Material_Short_Analysis_W_Cleaned.columns)

    except Exception as e:
        trace_msg = traceback.format_exc()
        logger.Note(p_note=trace_msg, p_log_level=LOG_LEVEL.debug())
        logger.Error()

        if flag_exception:
            out_Material_PSI_W = None
            out_Material_PSI_Sub = None
            raise Exception(e)
        else:
            if out_Material_Short_Analysis_W.empty:
                out_Material_PSI_W = CL_Mat_Short_Analysis_W.get_cleaned_columns_dataframe()
            logger.info(f'{str_instance} exit - {time.strftime("%Y-%m-%d - %H:%M:%S")}')
    else:
        if out_Material_Short_Analysis_W.empty:
            out_Material_PSI_W = CL_Mat_Short_Analysis_W.get_cleaned_columns_dataframe()
        logger.Finish()

    finally:
        # MediumWeight 실행 시 Header 없는 빈 데이터프레임이 Output이 되는 경우 오류가 발생함.
        # 이 오류를 방지하기 위해 Output이 빈 경우을 체크하여 Header를 만들어어 줌.

        if out_Material_Short_Analysis_W.empty:
            out_Material_PSI_W = CL_Mat_Short_Analysis_W.get_cleaned_columns_dataframe()
            fn_log_dataframe(out_Material_Short_Analysis_W, 'out_Material_Short_Analysis_W')

        logger.info(f'{str_instance} {time.strftime("%Y-%m-%d - %H:%M:%S")}::: Finish :::')