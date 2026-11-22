
"""

* 프로그램명
    - PY_MG_AmendSOPLotSize

* 내용
     - Documents.[OrderlineID] '%SCS_LOT%' 작업대상
       그외는  W Material Consumption Quantity Plan Output 작업없이 저장


* 변경이력
- 2024.11.18 / de0413.shin (신동언) / Create
- 2025.04.10 / 신동언 / Update
- 2025.05.30 / 신동언 / Update
- 2026.01.06 / 박병훈 / Update
- 2026.02.10 / 박병훈 / Update df_in_WSolverLotSizeOption 빈데이터 입력시 Error 발생 부분 수정
- 2026.03.05 / 박병훈 / 'W LotSize Period_2', 'W LotSize Remain Config_2' 추가로 로직 수정 및 업데이트
- 2026.03.15 / 박병훈 / Min Lot Size 반영 로직 수정
- 2026.03.27 / 박병훈 / Min Lot Size 반영 로직 수정  함수로 로직 수정
- 2026.04.01 / 박병훈 / Fix 구간 데이터 누락 주차 확장 설정 변경 & 그룹별로 마지막 주차가 Down 인 경우 강제로 Keep로 변경하기  ASIS Logig 제거 (신규 로직 + LPS 결과 적용) --- > 2026.04.01 수정
- 2026.04.02 / 박병훈 / W Solver Lotsize Option 실행 시점 변경


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.


* Input Table
   - df_in_MPCurrWeek       = Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
   - df_in_AllWeek          = Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
   - df_in_PlanOrgQty       = Select ([Version].[Version Name] * [Item].[Plan Group] * [Item].[Item Stage].[SET].relatedmembers("Item") * [Time].[Week] * [Location].[Site Stage].filter(#.Name in {"MF","MF_KD","MF_SET"}).relatedmembers("Location") * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2].filter(~(#.Name Startswith ("RT_"))) * [Activity3].[Activity3] ) on row,({Measure.[W Material Consumption Quantity Plan Output], Measure.[W Frozen Window LotSize],Measure.[W LotSize Period],Measure.[W LotSize Remain Config],Measure.[W LotSize Period_2],Measure.[W LotSize Remain Config_2],  Measure.[W MinUtil Fence] }) on column;
   - df_in_WSoftLotSize      = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item Stage].[SET].relatedmembers("Item") * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W LotSize Increment],  Measure.[W Min LotSize]}) on column;
    - df_in_Location         = Select ([Location].[Location] *[Location].[Location Type].[DC] * [Location].[Shipment Type] * [Location].[Site Stage]) on row;
   - df_in_WSolverLotSizeOption = Select ([Version].[Version Name]) on row, ({Measure.[W Solver Lotsize Option], Measure.[Dummy]}) on column;

* Output Table
    - df_out_Amend_SOP_MfgSOPQty = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Activity1].[Activity1] * [Documents].[OrderlineID] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,
                                     ({Measure.[Amend SOP_MfgSOP Qty], Measure.[Amend SOP_ORG SOP Qty], Measure.[Amend SOP_SOP Qty]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_AmendSOPLotSize] for measures {[Amend SOP_SOP Qty]} using scope ([Version].[Version Name].[CWV_MP])
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};




실행 전 프로시져를 통해 MF Site 삭제  필요

"""


########################################################################################################################
# common - start
########################################################################################################################
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
str_instance = 'PY_MG_AmendSOPLotSize'
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
logger.Start()

########################################################################################################################
# local function
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

# Logic Function 설정

def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
       return df[column_name].values[0]
    return None  # 기본값 반환


def lot_size(df_part : pd.DataFrame) -> pd.DataFrame:
    """
    함수 요약
    ----------------------------------------------------------------------------------------------------
    그룹 기준 : 'Version.[Version Name]', 'Item.[Item]', 'Location.[Location]', 'Activity2.[Activity2]'
    주차별 처리 : 같은 그릅 기준 안에서 'Time.[Week]' 순서대로 처리
    1차 :
        1) 'W Material Consumption Quantity Plan Output' < 'W Min LotSize' 이면 할당 시 0 으로 처리
           'W Material Consumption Quantity Plan Output' >= 'W Min LotSize' 이면 W Material Consumption Quantity Plan Output 반영
        2) 1차 대상을 기준으로 'W LotSize Increment' 기준으로 기본 할당
    1차 pool :
        3) ('W Material Consumption Quantity Plan Output' < 'W Min LotSize' 이라 1차 할당 못한 수량) +
           (1차 기본 할당 후 남은 잔량) + (이전 주차 Carry_in)
   2차
        4) 위 pool을 'W LotSize Increment' 기준으로 재 할당
           단, 현재 할당 수량  + 'W LotSize Increment' >= 'W Min LotSize' 인 경우만 할당
           우선순위 : abs('W Material Consumption Quantity Plan Output' - 현 할당 수량) 큰 순
           동정미면 현재 할당 수량 작은 순, 그래도 같으면 원래 순서
   keep / down :
        5) pool이 남고 keep 주차면 우선순위대로 강제할당 시도...
           단, 현재 할당 수량 + 남은 수량 pool >= 'W Min LotSize' 경우에만 할당
        6) Down 주차면  pool은 Carry_out 으로 다음 주차로 넘김
   참고 :
        keep인 경우에도 'W Min LotSize' 조건 때문에 어느 곳에도 할당하지 못하면 수량 보전을 위애 Carry_out 처리
    """
    df_part = df_part.copy().reset_index(drop=True)    # 데이터 프레임 복사
    if df_part.empty:
        return df_part
    df_part['_orig_order'] = np.arange(len(df_part))  # 데이터 프레임 인덱스 재 설정

    # --------------------------------------------------------------------------------------------
    # 컬럼명 정의 (지역변수 설정)
    # --------------------------------------------------------------------------------------------
    COL_VER        = 'Version.[Version Name]'
    COL_ITEM       = 'Item.[Item]'
    COL_WEEK       = 'Time.[Week]'
    COL_LOCATION   = 'Location.[Location]'
    COL_TRANSMODE  = 'Activity2.[Activity2]'
    COL_TYPE       = 'W LotSize Remain Config'
    COL_QTY        = 'W Material Consumption Quantity Plan Output'
    COL_LOT        = 'W LotSize Increment'
    COL_FLAG       = 'minLot_flag'
    COL_MINLOT     = 'W Min LotSize'

    GROUP_KEYS = [COL_VER ,COL_ITEM ,COL_LOCATION ,COL_TRANSMODE]

    KEEP_VAL       = 'KEEP'
    DOWN_VAL       = 'DOWN'

    TYPE_NORM      = '_type_norm'

    # --------------------------------------------------------------------------------------------
    # 데이터 타입 정리
    # --------------------------------------------------------------------------------------------
    df_part[COL_WEEK]     = pd.to_numeric(df_part[COL_WEEK], errors='coerce').astype(int)
    df_part[COL_QTY]      = pd.to_numeric(df_part[COL_QTY], errors='coerce').fillna(0).astype(int)
    df_part[COL_LOT]      = pd.to_numeric(df_part[COL_LOT], errors='coerce').fillna(0).astype(int)
    df_part[COL_MINLOT]  = pd.to_numeric(df_part[COL_MINLOT], errors='coerce').fillna(0).astype(int)
    df_part[COL_FLAG]  = df_part[COL_FLAG].astype(str).str.strip().str.upper()


    df_part[COL_FLAG] = (
        df_part[COL_FLAG]
        .fillna('N')
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # 원본 Type 컬럼을 보존하고 비교용만 생성
    df_part[TYPE_NORM] = (
        df_part[COL_TYPE]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------------------------------------------
    # carry_in_seed 없으면 생성
    # --------------------------------------------------------------------------------------------
    if 'carry_in_seed' not in df_part.columns:
        df_part['carry_in_seed'] = 0

    df_part['carry_in_seed']  = pd.to_numeric(
        df_part['carry_in_seed'], errors='coerce'
    ).fillna(0).astype(int)
    # --------------------------------------------------------------------------------------------
    # 동일 그룹 안에서 keep / down 이 썩여 있으면 에러 처리
    # --------------------------------------------------------------------------------------------
    type_check = (
        df_part.groupby(GROUP_KEYS + [COL_WEEK])[TYPE_NORM]
        .nunique(dropna=False)
    )
    bad_keys = type_check[type_check >1]
    if not bad_keys.empty:
        raise ValueError(
            f'같은 주차에  Keep/Down 이 같이 썩여 있음 : {bad_keys.index.tolist()}')
    # ##############################################################################
    # 주차별 keep / down lookup
    # ##############################################################################
    week_type_lookup = (
        df_part[GROUP_KEYS + [COL_WEEK ,TYPE_NORM]]
        .drop_duplicates()
        .set_index(GROUP_KEYS + [COL_WEEK])[TYPE_NORM]
        .to_dict()
    )

    # ##############################################################################
    # 기존 결과 컬럼이 있으면 초기화를 위한 컬럼 설정
    # ##############################################################################
    result_cols = [
        'base_qty_1st' , 'alloc_1st', 'rem_1st', 'rem_1st_week_sum', 'abs_diff_1st',
        'carry_in', 'pool_in_2nd', 'alloc_2nd_base', 'realloc_2nd', 'alloc_current',
        'abs_diff_2nd', 'keep_force_add', 'keep_priority', 'keep_selected',
        'pool_after_2nd', 'pool_after_keep', 'carry_out', 'final_qty', 'rounds_2nd'
    ]

    for c in result_cols:
        if c in df_part.columns:
            df_part.drop(columns=c, axis=1, inplace=True)

    out_list = []

    # ##############################################################################
    # 그룹별 독립 계산
    # ##############################################################################
    for group_key, g in df_part.groupby(GROUP_KEYS, sort=False):
        g = g.copy().sort_values([COL_WEEK, '_orig_order']).reset_index(drop=True)
        # --------------------------------------------------------------------------------
        # 결과 컬럼 초기화
        # --------------------------------------------------------------------------------
        g['base_qty_1st']             = 0            # 1차 대상 수량
        g['alloc_1st']                = 0            # 1차 기본 할당
        g['rem_1st']                  = 0            # 1차 잔량
        g['rem_1st_week_sum']         = 0            # 주차 별 1차 잔량 합
        g['abs_diff_1st']             = 0            # abs(Qty - alloc_1st)

        g['carry_in']                 = 0            # 이전 주차 carry
        g['pool_in_2nd']              = 0            # 2차 시작 pool

        g['alloc_2nd_base']           = 0            # 2차 시작 시 현재 할당량 (=alloc_1st)
        g['realloc_2nd']              = 0            # 2차 재 할당
        g['alloc_current']            = 0            # 현 할당량
        g['abs_diff_2nd']             = 0            # abs(Qty - 현재 할당량)

        g['keep_force_add']           = 0            # keep 강제 할당 수량
        g['keep_priority']            = np.nan       # keep 우선순위 값
        g['keep_selected']            = False        # keep 강제 할당 선택 여부

        g['pool_after_2nd']           = 0            # 2차 할당 후 남은 pool
        g['pool_after_keep']          = 0            # Keep 처리 후 남음 pool
        g['carry_out']                = 0            # 다음 주차로 넘길 carry
        g['final_qty']                = 0            # 최종 할당 수량
        g['rounds_2nd']               = 0            # 2차 재 할당 라운드 수

        carry = 0
        week_list = sorted([int(x) for x in g[COL_WEEK].dropna().unique().tolist()])

        # ##########################################################################
        # 주차별 로직 처리
        # ##########################################################################
        for wk in week_list:
            rows = g.index[g[COL_WEEK] == wk].tolist()
            if not rows:
                continue

            # 현재 주차의 Keep / Down 타입 확인
            week_type = str(week_type_lookup.get((*group_key ,wk), DOWN_VAL)).strip().upper()

            # 이전 주차의 Carry 기록
            g.loc[rows, 'carry_in'] = int(carry)

            # Table_Seq1 --> Table_Seq2 에서 넘어온 seed carry
            carry_seed = int(g.loc[rows ,'carry_in_seed'].sum())

            # ########################################################################
            # 1차 기본 할당
            # ########################################################################
            for j in rows:
                qty  = int(g.at[j, COL_QTY])
                minlot = int(g.at[j, COL_MINLOT])
                lot  = int(g.at[j, COL_LOT])
                flag = str(g.at[j, COL_FLAG]).strip().upper()

                # --------------------------------------------------------------------
                # 신규 로직
                # Qty <  MinLot 이면 Base_qty = 0
                # Qty >= MinLot 이면 Base_qty = Qty
                # --------------------------------------------------------------------
                if flag == 'Y':
                    base_qty = qty if qty >= minlot else 0
                # --------------------------------------------------------------------
                # 예전 로직
                # base_qty  = Qty 그대로
                # --------------------------------------------------------------------
                else:
                    base_qty = qty

                # 1차 기본 할당
                alloc_1st = (base_qty // lot) * lot if lot > 0 else 0

                # 1차 잔량
                rem_1st = qty - alloc_1st

                # 결과기록
                g.at[j, 'base_qty_1st']        = int(base_qty)
                g.at[j, 'alloc_1st']           = int(alloc_1st)
                g.at[j, 'rem_1st']             = int(rem_1st)
                g.at[j, 'abs_diff_1st']        = abs(int(qty) - int(alloc_1st))

            # 주차별 1차 잔량 합
            g.loc[rows, 'rem_1st_week_sum'] = int(g.loc[rows, 'rem_1st'].sum())
            # ########################################################################
            # 2차 pool
            # = 1차 잔량 합  + carry_seed + 이전 주차 carry
            # ########################################################################
            pool = int(g.loc[rows, 'rem_1st'].sum()) + int(carry_seed) + int(carry)

            g.loc[rows, 'pool_in_2nd'] = int(pool)

            # 2차 시작 시 현재 할당량 = 1차 할당량
            g.loc[rows, 'alloc_2nd_base']  = g.loc[rows, 'alloc_1st']
            g.loc[rows, 'alloc_current']   = g.loc[rows, 'alloc_1st']

            # ########################################################################
            # 2차 재 할당
            # ########################################################################
            rounds = 0

            if pool > 0 :
                while True:
                    rounds += 1

                    eligible = [
                        j for j in rows
                        if int(g.at[j ,COL_LOT]) > 0
                    ]

                    # 우선 순위
                    # 1) abs(Qty - 현재 할당량) 큰 순
                    # 2) 현재 할당량 작은 순
                    # 3) 원래 순서
                    eligible = sorted(
                        eligible,
                        key = lambda j: (
                            -abs(int(g.at[j ,COL_QTY]) - int(g.at[j, 'alloc_current'])),
                            int(g.at[j ,'alloc_current']),
                            int(g.at[j ,'_orig_order']),
                        ))
                    allocated_any = False

                    for j in eligible:
                        qty           = int(g.at[j ,COL_QTY])
                        minlot        = int(g.at[j, COL_MINLOT])
                        lot           = int(g.at[j, COL_LOT])
                        flag          = str(g.at[j, COL_FLAG]).strip().upper()
                        current_alloc = int(g.at[j, 'alloc_current'])

                        if flag != 'Y':
                            if pool < lot:
                                continue

                            g.at[j, 'realloc_2nd']   += lot
                            g.at[j, 'alloc_current'] += lot
                            pool -= lot
                            allocated_any = True
                            break

                        if current_alloc >= minlot:
                            if pool < lot:
                                continue

                            g.at[j, 'realloc_2nd'] += lot
                            g.at[j, 'alloc_current'] += lot
                            pool -= lot
                            allocated_any = True
                            break


                        # 아직 MinLot 미만의 경우
                        needed = minlot - current_alloc

                        # MinLot으로 할당하기 위해 최소 수량을 배수로 할당
                        needed_rounded = ((needed + lot - 1) // lot) * lot

                        if pool < needed_rounded:
                            continue
                        # N 인 경우는 기존 로직 : MinLot 조럽 없이 진행

                        # 할당 수량
                        g.at[j, 'realloc_2nd']   += needed_rounded
                        g.at[j, 'alloc_current'] += needed_rounded
                        pool -= needed_rounded
                        allocated_any = True
                        break
                    if pool == 0 or (not allocated_any):
                        break

            g.loc[rows, 'rounds_2nd']     = int(rounds)
            g.loc[rows, 'pool_after_2nd'] = int(pool)

            # 2차 현재 차이
            g.loc[rows, 'abs_diff_2nd'] = (
                    g.loc[rows, COL_QTY] - g.loc[rows, 'alloc_current']
            ).abs()

            # ########################################################################
            # Kepp / Down 처리
            # ########################################################################
            if week_type == KEEP_VAL:
                j_keep = None

                if pool > 0:
                    keep_rows = sorted(
                        rows,
                        key = lambda j: (
                            -abs(int(g.at[j ,COL_QTY]) - int(g.at[j ,'alloc_current'])),
                            int(g.at[j ,'alloc_current']),
                            int(g.at[j ,'_orig_order']),
                        )
                    )

                    for j in keep_rows:
                        minlot        = int(g.at[j, COL_MINLOT])
                        flag          = str(g.at[j ,COL_FLAG]).strip().upper()
                        current_alloc = int(g.at[j, 'alloc_current'])

                        can_allocate = False

                        # ------------------------------------------------------------
                        # Y 인 경우
                        # 현재 할당량 + 남은 pool >= MinLot 이어야 강제 할당 가능
                        # ------------------------------------------------------------
                        if flag == 'Y':
                            if current_alloc >= minlot:
                                can_allocate = True
                            elif current_alloc + pool >= minlot:
                                can_allocate = True
                        else:
                            can_allocate = True

                        if can_allocate:
                            j_keep = j
                            break

                if j_keep is not None:
                    # N인 경우는 예전 로직 : Minlot 조건 없이 가능
                    g.at[j_keep, 'keep_paiority'] = abs(
                        int(g.at[j_keep, COL_QTY]) - int(g.at[j_keep, 'alloc_current'])
                    )
                    g.at[j_keep , 'keep_force_add']  += int(pool)
                    g.at[j_keep , 'alloc_current']   += int(pool)
                    g.at[j_keep , 'keep_selected']    = True
                    pool                         = 0

                # keep 주차는 pool을 소진하려고 시도 했지만
                # 모든 후보가 Y 조건을 못 만족하면 pool이 남을 수 있음
                # 수량 보전을 위해 carry_out으로 넘김
                g.loc[rows, 'pool_after_keep']  = int(pool)
                g.loc[rows, 'carry_out']        = int(pool)
                carry                           = int(pool)

            else:
                g.loc[rows, 'pool_after_keep']  = int(pool)
                g.loc[rows, 'carry_out']        = int(pool)
                carry                           = int(pool)

            # 최종 수량
            g.loc[rows, 'final_qty'] = g.loc[rows, 'alloc_current']

        out_list.append(g)

    # ##########################################################################
    # 그룹 결과 합치기
    # ##########################################################################
    if not out_list:
        return df_part.reset_index(drop=True)

    result = pd.concat(out_list, ignore_index=True)
    result = result.sort_values('_orig_order').drop(columns='_orig_order').reset_index(drop=True)

    # 보조 컬럼 삭제
    for c in [TYPE_NORM, '_orig_order']:
        if c in result.columns:
            result = result.drop(columns=[c], errors='ignore')

    return result

"""
    - Tabel Seq 조건에 따라 1차 2차 할당 나누어 할당 후 합치기 
    - 1차 할당에서  Carry out (잔량)을 Seq2 테이블 첫 주차에 더함 
    - lot_size 수행 후 1개 데이터 합치기 
"""
def seq2_first_qty(df_all):
    df_all = df_all.copy().reset_index(drop=True)

    if df_all.empty:
        return df_all

    base_keys = [VERSION_NAME_COLUMN, ITEM_ITEM, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION,
                 ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3]

    flow_kes = [VERSION_NAME_COLUMN, ITEM_ITEM ,LOCATION_LOCATION
                ,ACTIVITY2_ACTIVITY2] # 2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)



    df_all['_orig_order'] = np.arange(len(df_all))

    # if 'carry_out' not in df_all.columns:
    #     df_all['carry_out'] = 0

    df_all[TIME_WEEK] = pd.to_numeric(df_all[TIME_WEEK], errors='coerce').astype(int)
    df_all['carry_out'] = pd.to_numeric(df_all['carry_out'], errors='coerce').fillna(0)

    # 추적용 컬럼
    if 'carry_in_seed' not in df_all.columns:
        df_all['carry_in_seed'] = 0

    df_all['carry_in_seed']  = pd.to_numeric(
        df_all['carry_in_seed'], errors='coerce'
    ).fillna(0).astype(int)

    # table_Sqe 을 통해 데이터 프레임 분리
    df1 = df_all[df_all['table_Seq'] == 1].copy()
    df2 = df_all[df_all['table_Seq'] == 2].copy()

    if df1.empty:
        return df_all.sort_values('_orig_order').drop(columns='_orig_order').reset_index(drop=True)

    if df2.empty:
        return df_all.sort_values('_orig_order').drop(columns='_orig_order').reset_index(drop=True)

    if 'carry_out' not in df_all.columns:
        df_all['carry_out'] = 0
        df1['carry_out'] = 0
    else:
        df_all['carry_out'] = pd.to_numeric(
            df_all['carry_out'], errors='coerce').fillna(0).astype(int)
        df1['carry_out'] = pd.to_numeric(
            df1['carry_out'], errors='coerce').fillna(0).astype(int)


    # Seq1 의 경우 마지막 주차 나머지 추출
    df1['_max_week'] = df1.groupby(flow_kes)[TIME_WEEK].transform('max')

    # 마지막 주차 행만 추출
    df1_last =(
        df1.loc[df1[TIME_WEEK] == df1['_max_week']]
        .sort_values(flow_kes + [TIME_WEEK, '_orig_order']).copy()
    )

    # 같은 키 + 마지막 주차 안에서 대표 1행 번호 부여
    df1_last['rn_last'] = df1_last.groupby(flow_kes + [TIME_WEEK]).cumcount()

    # 마지막 주차만 필터링
    carry_df = (
        df1_last.loc[
            (df1_last['rn_last'] == 0) &
            (df1_last['carry_out'] > 0),
            flow_kes + ['carry_out']
        ]
        .rename(columns={'carry_out': 'carry_qty'}).copy())

    # carry 가 전혀 없으면 그대로 반환
    if carry_df.empty:
        result = (
            df_all.sort_values('_orig_order')
            .drop(columns='_orig_order')
            .reset_index(drop=True)
        )

        return result

    # Seq2 첫 주자
    df2['_min_week'] = df2.groupby(flow_kes)[TIME_WEEK].transform('min')

    # 같은 주차 + 키 안에서 대표 1행
    df2 = (
        df2.sort_values(flow_kes + [TIME_WEEK, '_orig_order'])
        .reset_index(drop=True)
    )
    df2['_rn_first'] = df2.groupby(flow_kes + [TIME_WEEK]).cumcount()

    df2 = df2.merge(
        carry_df,
        on=flow_kes,
        how='left',
        validate='m:1',
    )

    df2['carry_qty'] = df2['carry_qty'].fillna(0).astype(int)

    mask = (df2[TIME_WEEK] == df2['_min_week']) & (df2['_rn_first'] == 0)

    # df2.loc[mask,'W Material Consumption Quantity Plan Output'] = (
    #     df2.loc[mask,'W Material Consumption Quantity Plan Output'] + df2.loc[mask,'carry_qty']
    # )

    df2.loc[mask, 'carry_in_seed'] = (
            df2.loc[mask, 'carry_in_seed'] + df2.loc[mask, 'carry_qty']
    )

    df1 = df1.drop(columns=['_max_week'], errors='ignore')
    df2 = df2.drop(columns=['_min_week', '_rn_first', 'carry_qty'], errors='ignore')

    result = pd.concat([df1, df2], ignore_index=True)
    result = (
        result.sort_values('_orig_order')
        .drop(columns='_orig_order')
        .reset_index(drop=True)
    )

    return result


"""
    - lot_size & seq2_first_qty 함수 합하여 한번에 실행하기 

"""


def run_lot_size(df_all):
    df_all = df_all.copy().reset_index(drop=True)

    if df_all.empty:
        return df_all

    df_seq1 = df_all[df_all['table_Seq'] == 1].copy()
    df_seq2 = df_all[df_all['table_Seq'] == 2].copy()

    if not df_seq1.empty:
        df_seq1 = lot_size(df_seq1)

    frames_mid = [x for x in [df_seq1, df_seq2] if not x.empty]

    if frames_mid:
        df_mid = pd.concat([df_seq1, df_seq2], axis=0, ignore_index=True)
    else:
        df_mid = df_all.iloc[0,0].copy()


    if not df_seq1.empty and not df_mid.empty:
        df_mid = seq2_first_qty(df_mid)

    df_seq1_final = df_mid[df_mid['table_Seq'] == 1].copy()
    df_seq2_input = df_mid[df_mid['table_Seq'] == 2].copy()

    df_seq2_result = lot_size(df_seq2_input)

    return pd.concat([df_seq1_final, df_seq2_result], axis=0, ignore_index=True)

if __name__ == '__main__':

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
        # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
        ################################################################################################################
        step('=====> STEP1 Start : 전처리 - 모듈 내에서 사용될 input table load')
        # # Value 변수 선언
        # PARAM_OUTVERSION_VALUE = "CWV_MP"

        # 데이터 파일 읽기
        if is_local:
        # 로컬일 경우 버전 처리
        # paramOutVersion = PARAM_OUTVERSION_VALUE
            df_in_MPCurrWeek             = read_csv_file('df_in_MPCurrWeek_H2')
            df_in_AllWeek                = read_csv_file('df_in_AllWeek_H2')
            df_in_PlanOrgQty             = read_csv_file('df_in_PlanOrgQty_H2')
            df_in_WSoftLotSize           = read_csv_file('df_in_WSoftLotSize_H2')
            df_in_Location               = read_csv_file('df_in_Location_H2')
            df_in_WSolverLotSizeOption   = read_csv_file('df_in_WSolverLotSizeOption_H2')
            paramOutVersion = "CWV_MP"

        dataframes = {
            'df_in_MPCurrWeek'            :  df_in_MPCurrWeek,
            'df_in_AllWeek'               :  df_in_AllWeek,
            'df_in_PlanOrgQty'            :  df_in_PlanOrgQty,
            'df_in_WSoftLotSize'          :  df_in_WSoftLotSize,
            'df_in_Location'              :  df_in_Location,
            'df_in_WSolverLotSizeOption'  :  df_in_WSolverLotSizeOption
        }

        for name, df in dataframes.items():
            print_df(df, f'input table load .... {name}')

        step('=====> STEP1 End')

        ################################################################################################################
        # STEP 2 : DataFrame Column 변수 처리
        ################################################################################################################
        step('=====> STEP2 Start : DataFrame Column 변수 처리')

        VERSION_NAME_COLUMN = 'Version.[Version Name]'
        ITEM_ITEM = 'Item.[Item]'
        TIME_WEEK = 'Time.[Week]'
        LOCATION_LOCATION = 'Location.[Location]'
        ACTIVITY1_ACTIVITY1 = 'Activity1.[Activity1]'
        ACTIVITY2_ACTIVITY2 = 'Activity2.[Activity2]'
        ACTIVITY3_ACTIVITY3 = 'Activity3.[Activity3]'
        DOCUMENTS_ORDERLINEID = 'Documents.[OrderlineID]'
        TIME_WEEK_COLUMN = 'Time.[Week]'
        SUB_LOCATION_SUB_LOCATION = 'Sub Location.[Sub Location]'
        TRANS_MODE_TRANS_MODE = 'Trans Mode.[Trans Mode]'
        Location_Location_Type_COLUMN = 'Location.[Location Type]'
        Location_Shipment_Type_COLUMN = 'Location.[Shipment Type]'
        Location_Site_Stage_COLUMN = 'Location.[Site Stage]'
        Resource_Resource_Type = 'Resource.[Resource Type]'
        Resource_Resource = 'Resource.[Resource]'

        BOD_Item_Multi_Lot_Qty = 'BOD Item_Multi Lot Qty'
        W_LotSize_Increment = 'W LotSize Increment'
        W_MinUtil_Fence = 'W MinUtil Fence'
        W_Min_LotSize = 'W Min LotSize'
        ORG_QTY = 'W Material Consumption Quantity Plan Output'
        FROZEND_LOTSIZE = 'W Frozen Window LotSize'
        Sequence = 'Sequence'

        Amend_SOP_ORG_SOP_Qty = 'Amend SOP_ORG SOP Qty'
        Amend_SOP_SOP_Qty = 'Amend SOP_SOP Qty'
        W_Resource_Consumption_Association = 'W Resource Consumption Association'

        W_LotSize_Period = 'W LotSize Period'
        W_LotSize_Period_2 = 'W LotSize Period_2'
        W_LotSize_Remain_Config = 'W LotSize Remain Config'
        W_LotSize_Remain_Config_2 = 'W LotSize Remain Config_2'
        W_SolverLotsize_Option = 'W Solver Lotsize Option'
        Dummy = 'Dummy'

        step('=====> STEP2 End')

        ################################################################################################################
        # STEP 3 :  input data machining
        ################################################################################################################
        step('=====> STEP3 Start : input data machining')

        current_week = get_first_value(df_in_MPCurrWeek, TIME_WEEK_COLUMN)
        note(f'=====> current_week : {current_week}')

        filter_cols = [
            VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION,
            ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty, Amend_SOP_SOP_Qty]

        # 신규 로직 진행 여부를 결정하기 위한 Flag 설정
        if df_in_WSolverLotSizeOption.empty:
            flag = "N"
        else:
            v = df_in_WSolverLotSizeOption[W_SolverLotsize_Option].iat[0]
            flag = "Y" if str(v).strip() == "2" else "N"
        note(f"flag data 확인 =============================> {flag}")

        if flag == 'Y':
            # W_LotSize_Remain_Config 값이 Null 인 경우 Keep을 반영 추후 변경될 수도 있음.....
            df_in_PlanOrgQty.loc[:, [W_LotSize_Remain_Config, W_LotSize_Remain_Config_2]] = df_in_PlanOrgQty[
                [W_LotSize_Remain_Config, W_LotSize_Remain_Config_2]].fillna('Keep')
            df_in_PlanOrgQty.loc[:, [W_LotSize_Remain_Config, W_LotSize_Remain_Config_2]] = df_in_PlanOrgQty[
                [W_LotSize_Remain_Config, W_LotSize_Remain_Config_2]].astype(str).apply(lambda s: s.str.strip())
            df_in_PlanOrgQty.loc[:, [W_LotSize_Period, W_LotSize_Period_2]] = df_in_PlanOrgQty[
                [W_LotSize_Period, W_LotSize_Period_2]].fillna(0).astype(int)

            col_list = [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID,
                        LOCATION_LOCATION, ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2,
                        ACTIVITY3_ACTIVITY3, ORG_QTY, FROZEND_LOTSIZE, W_LotSize_Period,
                        W_LotSize_Period_2, W_LotSize_Remain_Config, W_LotSize_Remain_Config_2, W_MinUtil_Fence]

            # df_in_Plan_Org_Qty : 엔진에서 나온 계획 결과(수량)
            df_in_Plan = df_in_PlanOrgQty[col_list]
            df_in_Plan.loc[:, FROZEND_LOTSIZE] = df_in_Plan[FROZEND_LOTSIZE].fillna(0).astype(int)

            # df_in_AllWeek : CurrentWeek 기준으로 -52주차부터 +52주차까지 데이터
            # 중목된 주차를 삭제처리
            df_in_AllWeek = df_in_AllWeek[[TIME_WEEK]].drop_duplicates()
            # current 주차보다 큰 주차만 작업대상으로 복사처리
            df_AllWeek = df_in_AllWeek.loc[(df_in_AllWeek[TIME_WEEK] >= current_week)].copy()

            # 주차 소트하여 인덱스 재설정처리
            df_AllWeek = df_AllWeek.reset_index(drop='true')
            df_AllWeek[Sequence] = df_AllWeek.index + 1  # 2026.04.01 범위 시작이 1부터 시작함으로 수정

            # plan_org에  재설정한 All_Week을 Merge처리한다.
            df_in_Plan = df_in_Plan.merge(df_AllWeek, on=[TIME_WEEK], how='left')

            df_in_Plan['key_cols'] = df_in_Plan[ACTIVITY1_ACTIVITY1] + "_" + df_in_Plan[
                ACTIVITY3_ACTIVITY3]

            print_df(df_in_Plan , 'df_in_Plan________________ 확인 1')

            if df_in_WSoftLotSize.empty:
                df_in_WSoft_LotSize = pd.DataFrame(columns=df_in_WSoftLotSize.columns)

            df_in_WSoftLotSize['key_cols'] = df_in_WSoftLotSize[ACTIVITY1_ACTIVITY1] + "_" + df_in_WSoftLotSize[
                ACTIVITY3_ACTIVITY3]

            df_in_Plan = df_in_Plan.merge(
                df_in_WSoftLotSize[['key_cols', W_LotSize_Increment, W_Min_LotSize]],
                on='key_cols', how='left').drop(columns='key_cols', axis=1)

            # number 컬럼 빈값 0으로 채우기
            numeric_cols = [W_LotSize_Increment, W_MinUtil_Fence, W_Min_LotSize, Sequence,
                            FROZEND_LOTSIZE, W_LotSize_Period, W_LotSize_Period_2]
            df_in_Plan.loc[:, numeric_cols] = df_in_Plan.loc[:, numeric_cols].fillna(0).astype(int)

            # minLot_flag 설정  Sequence >= W_MinUtil_Fence 이면 'Y','N', Y이면 min lot size 적용 구간
            df_in_Plan['minLot_flag'] = np.where(df_in_Plan[Sequence].le(df_in_Plan[W_MinUtil_Fence]), 'Y', 'N')

            print_df(df_in_Plan, 'df_in_Plan________________ 확인 2')

            df_in_plan_SCS_ORG = df_in_Plan.loc[(df_in_Plan[FROZEND_LOTSIZE] < df_in_Plan[Sequence])].copy()
            print_df(df_in_plan_SCS_ORG, 'df_in_plan_SCS_ORG______________ 확인 1')

            df_in_Plan_SCSB = df_in_plan_SCS_ORG.loc[
                df_in_plan_SCS_ORG[DOCUMENTS_ORDERLINEID].str.contains('SCS')].copy() #Lot Size 작업 대상
            df_in_Plan_NSCS = df_in_plan_SCS_ORG.loc[
                ~df_in_plan_SCS_ORG[DOCUMENTS_ORDERLINEID].str.contains('SCS')].copy()

            print_df(df_in_Plan_SCSB, 'df_in_Plan_SCSB 작업 대상 ______________ 확인 1')

            # 신규 데이터 프레임 생성
            df_in_Plan_SCSB_new = pd.DataFrame()  # 신규 빈 데이터 프레임 생성
            # flag가 Y 이면 신규 로직 수행
            df_in_Plan_SCSB_new_temp = df_in_Plan_SCSB.copy()

            # 2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)
            df_in_Plan_SCSB_group = df_in_Plan_SCSB_new_temp.groupby(
                [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, LOCATION_LOCATION, ACTIVITY2_ACTIVITY2],
                as_index=False).agg(
                W_Frozen_Window_LotSize=(FROZEND_LOTSIZE, 'min'),
                W_LotSize_Period=(W_LotSize_Period, 'min'),
                W_LotSize_Period_2=(W_LotSize_Period_2, 'min'),
                W_LotSize_Remain_Config=(W_LotSize_Remain_Config, 'max'),
                W_LotSize_Remain_Config_2=(W_LotSize_Remain_Config_2, 'max')).rename(columns={
                'W_Frozen_Window_LotSize': FROZEND_LOTSIZE, 'W_LotSize_Period': W_LotSize_Period,
                'W_LotSize_Remain_Config': W_LotSize_Remain_Config, 'W_LotSize_Period_2': W_LotSize_Period_2,
                'W_LotSize_Remain_Config_2': W_LotSize_Remain_Config_2})

            print_df(df_in_Plan_SCSB_group, 'df_in_Plan_SCSB_group 데이터 확인')

            df_in_Plan_SCSB_new_temp = df_in_Plan_SCSB_new_temp.drop(
                columns=[FROZEND_LOTSIZE, W_LotSize_Period, W_LotSize_Remain_Config,
                         W_LotSize_Period_2, W_LotSize_Remain_Config_2], axis=1).merge(
                df_in_Plan_SCSB_group,
                on=[VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, LOCATION_LOCATION, ACTIVITY2_ACTIVITY2],
                how='left')  # 기준추가 2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)

            # 데이터 타입 변경
            df_in_Plan_SCSB_new_temp[TIME_WEEK] = pd.to_numeric(df_in_Plan_SCSB_new_temp[TIME_WEEK]).astype(int)

            print_df(df_in_Plan_SCSB_new_temp, 'df_in_Plan_SCSB_new_temp 데이터 확인')

            m_window = ((df_in_Plan_SCSB_new_temp[Sequence] > df_in_Plan_SCSB_new_temp[FROZEND_LOTSIZE] - 1) &
                        (df_in_Plan_SCSB_new_temp[Sequence] <= df_in_Plan_SCSB_new_temp[W_LotSize_Period]))
            # W_LotSize_Period1  수정 필요........

            # m_windows에 필터 되는 내용 확인
            df_in_Plan_SCSB_new_m = df_in_Plan_SCSB_new_temp.loc[m_window].drop(
                columns=[W_LotSize_Period_2, W_LotSize_Remain_Config_2]).copy()

            print_df(df_in_Plan_SCSB_new_m, 'df_in_Plan_SCSB_new_m_데이터 확인')

            # 첫번재 조건 테이블 표시
            df_in_Plan_SCSB_new_m['table_Seq'] = 1
            # m_window 조건 (1차 조건에 포함되지 않은 데이터 프레임 필터)
            df_in_Plan_SCSB_new_temp = df_in_Plan_SCSB_new_temp.loc[~m_window].copy()

            print_df(df_in_Plan_SCSB_new_temp, 'df_in_Plan_SCSB_new_temp 확인')

            # 두번째 조건 필털를 위한 masking 지정
            m_window1 = ((df_in_Plan_SCSB_new_temp[Sequence] > df_in_Plan_SCSB_new_temp[W_LotSize_Period]) &
                         (df_in_Plan_SCSB_new_temp[Sequence] <= df_in_Plan_SCSB_new_temp[W_LotSize_Period_2]))

            # 2차 필터한 데이터 프레임 지정 및 concat을 위한불필요한 데이터 프레임 컬럼 삭제
            df_in_Plan_SCSB_new_m1 = df_in_Plan_SCSB_new_temp.loc[m_window1].drop(
                columns=[W_LotSize_Period, W_LotSize_Remain_Config]).copy()
            # concat을 위한 데이터 프레임 컬럼명 변경
            df_in_Plan_SCSB_new_m1 = df_in_Plan_SCSB_new_m1.rename(
                columns={W_LotSize_Period_2: W_LotSize_Period, W_LotSize_Remain_Config_2: W_LotSize_Remain_Config})
            # 두번째 데이터 프레임 표시
            df_in_Plan_SCSB_new_m1['table_Seq'] = 2

            # 데이터 프레임 합치기
            df_in_Plan_SCSB_new_m = pd.concat([df_in_Plan_SCSB_new_m, df_in_Plan_SCSB_new_m1], axis=0,
                                              ignore_index=True)

            print_df(df_in_Plan_SCSB_new_m, 'df_in_Plan_SCSB_new_m_확인', True)
            note(f"===========  df_in_Plan_SCSB_new_m =====================> {df_in_Plan_SCSB_new_m.shape} 첫번째")

            df_in_Plan_SCSB_new_m['To_location'] = df_in_Plan_SCSB_new_m[ACTIVITY1_ACTIVITY1].str.split('_').str[1]

            df_in_Plan_SCSB_new_m = df_in_Plan_SCSB_new_m.merge(
                df_in_Location.rename(columns={LOCATION_LOCATION: 'To_location'}),
                on='To_location', how='left')

            df_in_Plan_SCSB_new_m[W_LotSize_Increment] = df_in_Plan_SCSB_new_m[W_LotSize_Increment].fillna(0).astype(
                int)

            # 우선 순위 정하기
            # 1) Location_Shipment_Type_COLUMN 우선순위
            # DIR_S 1순위, DIR_D 2 순위 , 그 외 = 99
            df_in_Plan_SCSB_new_m['p_ship'] = np.select(
                [df_in_Plan_SCSB_new_m[Location_Shipment_Type_COLUMN].eq('DIR_S'),
                 df_in_Plan_SCSB_new_m[Location_Shipment_Type_COLUMN].eq('DIR_D')],
                [1, 2], default=99)

            # 2) Location_Site_Stage_COLUMN 의 순서 지정
            df_in_Plan_SCSB_new_m['p_site'] = np.where(
                df_in_Plan_SCSB_new_m[Location_Site_Stage_COLUMN].astype(str).str.contains('HUB', na=False),
                3, 4)

            # 3) 정렬 순서
            #  1. Week 오름차순
            #  2. Item 오름차순
            #  3. To_Location  오름차순
            #  4. Location_Shipment_Type_COLUMN, Location_Site_Stage_COLUMN, W_LotSize_Increment 순서 ....

            df_in_Plan_SCSB_new_m = df_in_Plan_SCSB_new_m.sort_values(
                by=[ITEM_ITEM, TIME_WEEK, 'p_ship', 'p_site', W_LotSize_Increment, 'To_location', LOCATION_LOCATION,
                    ACTIVITY2_ACTIVITY2],
                ascending=[True, True, True, True, False, True, True, True],
                kind='mergesort').drop(columns=['p_ship', 'p_site'],
                                       axis=1)  # 2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)

            df_in_Plan_SCSB_new_m[W_LotSize_Increment] = df_in_Plan_SCSB_new_m[W_LotSize_Increment].fillna(0).astype(
                int)
            df_in_Plan_SCSB_new_m.reset_index(drop=True, inplace=True)

            df_in_Plan_SCSB_new_m_cal = df_in_Plan_SCSB_new_m.copy()

            # 그룹별로 마지막 주차가 Down 인 경우 강제로 Keep로 변경하기  --- > 2026.04.01 수정
            df_in_Plan_SCSB_new_m_cal[TIME_WEEK] = pd.to_numeric(df_in_Plan_SCSB_new_m_cal[TIME_WEEK]).astype(int)

            # 그룹이 되어야 하는 컬럼 설정
            table2_groupby_col = [VERSION_NAME_COLUMN, ITEM_ITEM, LOCATION_LOCATION, ACTIVITY2_ACTIVITY2]

            # 마지막 주차 찾기
            df_in_Plan_SCSB_new_m_cal['_last_week'] = df_in_Plan_SCSB_new_m_cal.groupby(
                table2_groupby_col)[TIME_WEEK].transform('max')

            # 마지막 주차인 행만 Keep으로 변경
            mask_last_week = df_in_Plan_SCSB_new_m_cal[TIME_WEEK] == df_in_Plan_SCSB_new_m_cal['_last_week']
            df_in_Plan_SCSB_new_m_cal.loc[mask_last_week, W_LotSize_Remain_Config] = 'Keep'

            # 불필요한 컬럼 삭제
            df_in_Plan_SCSB_new_m_cal = df_in_Plan_SCSB_new_m_cal.drop(columns=['_last_week'])  # 2024.04.01 수정 완료

            print_df(df_in_Plan_SCSB_new_m_cal, 'df_in_Plan_SCSB_new_m_cal_마지막 주차 확인', True)

            # 함수 실행
            df_in_Plan_SCSB_new_m_cal = run_lot_size(df_in_Plan_SCSB_new_m_cal)
            # 컬럼명 변경
            df_in_Plan_SCSB_new_m_cal = df_in_Plan_SCSB_new_m_cal.rename(
                columns={ORG_QTY: Amend_SOP_ORG_SOP_Qty, 'final_qty': Amend_SOP_SOP_Qty})

            print_df(df_in_Plan_SCSB_new_m_cal, 'df_in_Plan_SCSB_new_m_cal_중간 데이터 확인', True)

            # 필요한 컬럼만 필터
            df_in_Plan_SCSB_new_m_cal = df_in_Plan_SCSB_new_m_cal.reindex(columns=filter_cols)

            print_df(df_in_Plan_SCSB_new_m_cal, 'df_in_Plan_SCSB_new_m_cal 데이터 확인', True)

            note(
                f"===========  df_in_Plan_SCSB_new_m_cal =====================> {df_in_Plan_SCSB_new_m_cal.shape} 최종확인")

            # 최종 out_put 설정
            df_in_Plan_SCSB_new = df_in_Plan_SCSB_new_m_cal.copy()
            df_in_Plan_SCSB_new = df_in_Plan_SCSB_new.loc[
                ~df_in_Plan_SCSB_new[ACTIVITY2_ACTIVITY2].str.contains('RT_')].copy()

            print_df(df_in_Plan_SCSB_new, 'df_in_Plan_SCSB_new _ 분리되고 로직이 진행된 데이터 프레임 확인', False)

            index_col = [
                VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION,
                ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3]

            df_in_Plan_SCSB_new[TIME_WEEK] = df_in_Plan_SCSB_new[TIME_WEEK].astype(str).str.strip()
            df_in_Plan[TIME_WEEK] = df_in_Plan[TIME_WEEK].astype(str).str.strip()

            df_in_plan_temp_index = df_in_Plan_SCSB_new.set_index(index_col).index
            df_in_Plan_org_index = df_in_Plan.set_index(index_col).index

            df_in_Plan = df_in_Plan.rename(columns={ORG_QTY: Amend_SOP_ORG_SOP_Qty}).copy()
            df_in_Plan[Amend_SOP_SOP_Qty] = df_in_Plan[Amend_SOP_ORG_SOP_Qty].copy()
            df_in_Plan = df_in_Plan[filter_cols]

            df_in_Plan_org_temp = df_in_Plan[~df_in_Plan_org_index.isin(df_in_plan_temp_index)]

            print_df(df_in_Plan_org_temp, 'df_in_Plan_org_temp_필터된 데이터 확인')

            df_out_Amend_SOP_MfgSOPQty = pd.concat([df_in_Plan_org_temp, df_in_Plan_SCSB_new], ignore_index=True,
                                                   axis=0)
            print_df(df_out_Amend_SOP_MfgSOPQty, 'df_out_Amend_SOP_MfgSOPQty_로직수행 데이터 확인', True)

        else:
            df_out_Amend_SOP_MfgSOPQty = df_in_PlanOrgQty.rename(columns={ORG_QTY: Amend_SOP_ORG_SOP_Qty}).copy()
            df_out_Amend_SOP_MfgSOPQty[Amend_SOP_SOP_Qty] = df_out_Amend_SOP_MfgSOPQty[Amend_SOP_ORG_SOP_Qty].copy()
            df_out_Amend_SOP_MfgSOPQty = df_out_Amend_SOP_MfgSOPQty[filter_cols]
            print_df(df_out_Amend_SOP_MfgSOPQty, "df_out_Amend_SOP_MfgSOPQty", True)

        step('=====> STEP3 End')
        ################################################################################################################
        # STEP 5 :  input data machining
        ################################################################################################################
        step('=====> STEP4 Start : Final output table create')
        df_out_Amend_SOP_MfgSOPQty["Version.[Version Name]"] = paramOutVersion

        if is_local:
            note(f'=====> Final output table create')
            print_df(df_out_Amend_SOP_MfgSOPQty, 'df_out_Amend_SOP_MfgSOPQty', True)

        print_df(df_out_Amend_SOP_MfgSOPQty, 'df_out_Amend_SOP_MfgSOPQty', True)

        row_count, col_count = df_out_Amend_SOP_MfgSOPQty.shape
        note(f'=====> Final df_out_Amend_SOP_MfgSOPQty rows : {row_count} , Columns : {col_count}')


    except CustomException as e:
        step(f'=====> CustomException : {e}')
        df_out_Amend_SOP_MfgSOPQty = pd.DataFrame([], columns=[])


    except Exception as ex:
        step(f'=====> Exception : {traceback.format_exc()}')
        logger.Error()
        vdCommon.gfn_pyLog_error(traceback.format_exc())


    finally:
        # 현재 메모리 사용량과 피크 메모리 사용량 체크 / 실행 시간 계산 (초 단위 -> 분 단위로 변환)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        step(f'=====> current: {format_size(current)}, peak: {format_size(peak)}, execution time: {run_time_minutes(start_time)}')
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
