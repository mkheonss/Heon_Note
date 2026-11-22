

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


* Flow Summary


* ProductIon Constraint


* Script Parameter
    - paramOutVersion : 기본값 : CurrentWorkingView, 호출시에, 결과데이터를 Version Name을 별도로 지정하는데에 사용.


* Input Table
   - df_in_MPCurrWeek       = Select ([Time].[Week].filter(#.Key >= &CurrentWeek.element(0).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
   - df_in_AllWeek          = Select (Time.[Day] * Time.[Day of Week] * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(-52).Key && #.Key <= &CurrentWeek.element(0).LeadOffset(52).Key));
   - df_in_Plan_Org_Qty     = Select ([Version].[Version Name] * [Item].[Plan Group] * [Item].[Item Stage].[SET].relatedmembers("Item") * [Time].[Week] * [Location].[Site Stage].filter(#.Name in {"MF","MF_KD","MF_SET"}).relatedmembers("Location") * [Documents].[OrderlineID] * [Activity1].[Activity1] * [Activity2].[Activity2].filter(~(#.Name Startswith ("RT_"))) * [Activity3].[Activity3] ) on row,({Measure.[W Material Consumption Quantity Plan Output], Measure.[W Frozen Window LotSize],Measure.[W LotSize Period],Measure.[W LotSize Remain Config],Measure.[W LotSize Period_2],Measure.[W LotSize Remain Config_2], Measure.[Dummy]}) on column;
   - df_in_WSoft_LotSize    = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item Stage].[SET].relatedmembers("Item") * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W LotSize Increment],  Measure.[W Min LotSize],  Measure.[W MinUtil Fence],Measure.[Dummy]}) on column;
   - df_in_WResource_Consum = Select ([Version].[Version Name] * [Location].[Location] * [Activity1].[Activity1] * [Resource].[Resource] * [Resource].[Resource Type].filter(#.Name in {"MCT","SCT","MFT","SRT"}) * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,({Measure.[W Resource Consumption Association], Measure.[Dummy]}) on column;
   - df_in_WResource_Capa   = Select ([Version].[Version Name] * [Location].[Location] * [Time].[Week] * [Resource].[Resource Type].filter(#.Name in {"MFT"}).relatedmembers([Resource])) on row,({ Measure.[W Coarser Maximum Utilization Quantity],Measure.[W Coarser Minimum Utilization Quantity],Measure.[Dummy]}) on column where { Measure.[W Coarser Minimum Utilization Quantity] > 0};
   - df_in_Shipment_LT      = Select ([Version].[Version Name] * [Activity1].[Activity1] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row, ({Measure.[W Activity Mandatory Offset], Measure.[Dummy]}) on column;
   - df_in_Location         = Select ([Location].[Location] *[Location].[Location Type].[DC] * [Location].[Shipment Type] * [Location].[Site Stage]) on row;
   - df_in_WSolverLotSizeOption = Select ([Version].[Version Name]) on row, ({Measure.[W Solver Lotsize Option], Measure.[Dummy]}) on column;

* Output Table
    - df_out_Amend_SOP_MfgSOPQty = Select ([Version].[Version Name] * [Location].[Location] * [Item].[Item] * [Time].[Week] * [Activity1].[Activity1] * [Documents].[OrderlineID] * [Activity2].[Activity2] * [Activity3].[Activity3] ) on row,
                                     ({Measure.[Amend SOP_MfgSOP Qty], Measure.[Amend SOP_ORG SOP Qty], Measure.[Amend SOP_SOP Qty]}) on column;

* 테스트 스크립트
    EXEC plugin instance [PY_MG_AmendSOPLotSize] for measures {[Amend SOP_SOP Qty]} using scope ([Version].[Version Name].[CurrentWorkingView])
    using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CurrentWorkingView"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")};




실행 전 프로시져를 통해 MF Site 삭제  필요

"""


########################################################################################################################
# common - start
########################################################################################################################
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon
import os
import time
import datetime
import decimal
import warnings
import math
import traceback
import gc
import tracemalloc

import numpy as np
import tabulate
import pandas as pd
import logging
import platform
import re

from dateutil import parser as date_parser
from typing import Union

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_MG_AmendSOPLotSize'

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
def delete_dfs(*dfs):
    for df in dfs:
        del df
        gc.collect()

def fn_math(val1,val2):
    return math.trunc(val1 / val2) * val2

# 스트링을 넘겨준다.
def gfn_get_str(val):
    if (type(val) is str):
        return val
    elif (type(val) is float):
        if (pd.isna(val)):
            return ""
        else:
            return str(val)

def print_df(df, df_name, _localFlag=True):
    vdCommon.gfn_saveDf(df, df_name, _localFlag)

def gfn_lpad(val, width, fillchar='0'):
    return str(val).rjust(width, fillchar)

def step(string):
    vdCommon.gfn_stepLog(string)

def get_first_value(df, column_name):
    if not df.empty and column_name in df.columns:
       return df[column_name].values[0]
    return None  # 기본값 반환

def note(string, p_log_level=LOG_LEVEL.debug()):
    logger.Note(p_note=f'{string}', p_log_level=p_log_level)

# Logic Function 설정

# Logic Function 설정

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

    GROUP_KEYS = [COL_VER,COL_ITEM,COL_LOCATION,COL_TRANSMODE]

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
    bad_keys = type_check[type_check>1]
    if not bad_keys.empty:
        raise ValueError(
            f'같은 주차에  Keep/Down 이 같이 썩여 있음 : {bad_keys.index.tolist()}')
    # ##############################################################################
    # 주차별 keep / down lookup
    # ##############################################################################
    week_type_lookup = (
        df_part[GROUP_KEYS + [COL_WEEK,TYPE_NORM]]
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
            week_type = str(week_type_lookup.get((*group_key,wk), DOWN_VAL)).strip().upper()

            # 이전 주차의 Carry 기록
            g.loc[rows, 'carry_in'] = int(carry)

            # Table_Seq1 --> Table_Seq2 에서 넘어온 seed carry
            carry_seed = int(g.loc[rows,'carry_in_seed'].sum())

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
                        if int(g.at[j,COL_LOT]) > 0
                    ]

                    # 우선 순위
                    # 1) abs(Qty - 현재 할당량) 큰 순
                    # 2) 현재 할당량 작은 순
                    # 3) 원래 순서
                    eligible = sorted(
                        eligible,
                        key = lambda j: (
                            -abs(int(g.at[j,COL_QTY]) - int(g.at[j, 'alloc_current'])),
                            int(g.at[j,'alloc_current']),
                            int(g.at[j,'_orig_order']),
                        ))
                    allocated_any = False

                    for j in eligible:
                        qty           = int(g.at[j,COL_QTY])
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
                            -abs(int(g.at[j,COL_QTY]) - int(g.at[j,'alloc_current'])),
                            int(g.at[j,'alloc_current']),
                            int(g.at[j,'_orig_order']),
                        )
                    )

                    for j in keep_rows:
                        minlot        = int(g.at[j, COL_MINLOT])
                        flag          = str(g.at[j,COL_FLAG]).strip().upper()
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

    flow_kes = [VERSION_NAME_COLUMN, ITEM_ITEM,LOCATION_LOCATION,ACTIVITY2_ACTIVITY2] #2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)



    df_all['_orig_order'] = np.arange(len(df_all))

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

    if df1.empty and df2.empty:
        return df_all.reset_index(drop=True)

    if df1.empty:
        return df2.reset_index(drop=True)

    if df2.empty:
        return df1.reset_index(drop=True)

    if df2.empty:
        result = (
            df_all.sort_values('_orig_order')
                .drop(columns='_orig_order')
                .reset_index(drop=True)
        )
        return result

    # Seq1 의 경우 마지막 주차 나머지 추출
    df1['_max_week'] = df1.groupby(flow_kes)[TIME_WEEK].transform('max')

    # 마지막 주차 행만 추출
    df1_last =(
        df1.loc[df1[TIME_WEEK] == df1['_max_week']]
            .sort_values(flow_kes + [TIME_WEEK,'_orig_order']).copy()
    )

    # 같은 키 + 마지막 주차 안에서 대표 1행 번호 부여
    df1_last['rn_last'] = df1_last.groupby(flow_kes+[TIME_WEEK]).cumcount()

    # 마지막 주차만 필터링
    carry_df = (
       df1_last.loc[
           (df1_last['rn_last'] == 0) &
           (df1_last['carry_out'] >0),
           flow_kes + ['carry_out']
       ]
        .rename(columns={'carry_out' : 'carry_qty'}).copy())

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
        on = flow_kes,
        how = 'left',
        validate = 'm:1',
    )

    df2['carry_qty'] = df2['carry_qty'].fillna(0).astype(int)

    mask = (df2[TIME_WEEK] == df2['_min_week']) & (df2['_rn_first'] == 0 )

    # df2.loc[mask,'W Material Consumption Quantity Plan Output'] = (
    #     df2.loc[mask,'W Material Consumption Quantity Plan Output'] + df2.loc[mask,'carry_qty']
    # )

    df2.loc[mask,'carry_in_seed'] = (
        df2.loc[mask, 'carry_in_seed'] + df2.loc[mask, 'carry_qty']
    )

    df1 = df1.drop(columns=['_max_week'], errors='ignore')
    df2 = df2.drop(columns=['_min_week', '_rn_first','carry_qty'], errors='ignore')

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

    df_seq1_result = lot_size(df_seq1)

    df_mid = pd.concat([df_seq1_result, df_seq2], axis=0, ignore_index=True)
    df_mid = seq2_first_qty(df_mid)

    df_seq1_final = df_mid[df_mid['table_Seq'] == 1].copy()
    df_seq2_input = df_mid[df_mid['table_Seq'] == 2].copy()

    df_seq2_result = lot_size(df_seq2_input)

    return pd.concat([df_seq1_final, df_seq2_result], axis=0, ignore_index=True)


try:
    ################################################################################################################
    # logic start
    # 전처리 : 모듈 내에서 사용될 데이터에 대한 정합성 체크 및 데이터 선 가공
    ################################################################################################################
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))
    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    ################################################################################################################
    # STEP 1 : input table load
    ################################################################################################################
    if common.gfn_get_isLocal():
        df_in_MPCurrWeek = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_MPCurrWeek_H3.csv", encoding="UTF-8")
        df_in_AllWeek = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_AllWeek_H3.csv", encoding="UTF-8")
        df_in_Plan_Org_Qty = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_PlanOrgQty_H3.csv", encoding="UTF-8")
        df_in_WSoft_LotSize = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_WSoftLotSize_H3.csv", encoding="UTF-8")
        df_in_WResource_Consum = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_WResourceConsum_H3.csv", encoding="UTF-8")
        df_in_WResource_Capa = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_WResourceCapa_H3.csv", encoding="UTF-8")
        df_in_Shipment_LT = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_ShipmentLT_H3.csv", encoding="UTF-8")
        df_in_Location = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_Location_H3.csv", encoding="UTF-8")
        df_in_WSolverLotSizeOption = pd.read_csv(os.path.dirname(__file__) + "\\" + f"df_in_WSolverLotSizeOption_H3.csv", encoding="UTF-8")
        paramOutVersion = "CurrentWorkingView"

    # Input 출력
    vdCommon.gfn_saveDf(df_in_MPCurrWeek, "df_in_MPCurrWeek", True)
    vdCommon.gfn_saveDf(df_in_AllWeek, "df_in_AllWeek", True)
    vdCommon.gfn_saveDf(df_in_Plan_Org_Qty, "df_in_Plan_Org_Qty", True)
    vdCommon.gfn_saveDf(df_in_WSoft_LotSize, "df_in_WSoft_LotSize", True)
    vdCommon.gfn_saveDf(df_in_WResource_Consum, "df_in_WResource_Consum", True)
    vdCommon.gfn_saveDf(df_in_WResource_Capa, "df_in_WResource_Capa", True)
    vdCommon.gfn_saveDf(df_in_Shipment_LT, "df_in_Shipment_LT", True)
    vdCommon.gfn_saveDf(df_in_Location, "df_in_Location", True)
    vdCommon.gfn_saveDf(df_in_WSolverLotSizeOption, "df_in_WSolverLotSizeOption", True)

    ################################################################################################################
    # Step 2 (1) 데이터 프레임 변수 지정 및 이름 변경
    ################################################################################################################
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

    ################################################################################################################
    # Step 3 out 데이터 프레임 기초 데이터 셋팅
    ###############################################################################################################
    # current_week = str(df_in_CurrWeek[TIME_WEEK_COLUMN].values[0])
    current_week = get_first_value(df_in_MPCurrWeek, TIME_WEEK_COLUMN)
    note(f'=====> current_week : {current_week}')

    # 신규 로직 진행 여부를 결정하기 위한 Flag 설정
    if df_in_WSolverLotSizeOption.empty:
        flag = "N"
    else:
        v = df_in_WSolverLotSizeOption[W_SolverLotsize_Option].iat[0]
        flag = "Y" if str(v).strip() == "2" else "N"
    note(f"flag data 확인 =============================> {flag}")

    # W_LotSize_Remain_Config 값이 Null 인 경우 Keep을 반영 추후 변경될 수도 있음.....
    df_in_Plan_Org_Qty.loc[:, [W_LotSize_Remain_Config,W_LotSize_Remain_Config_2]] = df_in_Plan_Org_Qty[
        [W_LotSize_Remain_Config,W_LotSize_Remain_Config_2]].fillna('Keep')
    df_in_Plan_Org_Qty.loc[:, [W_LotSize_Remain_Config,W_LotSize_Remain_Config_2]] = df_in_Plan_Org_Qty[
        [W_LotSize_Remain_Config,W_LotSize_Remain_Config_2]].astype(str).apply(lambda s : s.str.strip())
    df_in_Plan_Org_Qty.loc[:, [W_LotSize_Period,W_LotSize_Period_2]] = df_in_Plan_Org_Qty[
        [W_LotSize_Period,W_LotSize_Period_2]].fillna(0).astype(int)

    col_list = [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID,
                LOCATION_LOCATION, ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2,
                ACTIVITY3_ACTIVITY3, ORG_QTY, FROZEND_LOTSIZE,W_LotSize_Period,
                W_LotSize_Period_2, W_LotSize_Remain_Config, W_LotSize_Remain_Config_2]

    #df_in_Plan_Org_Qty : 엔진에서 나온 계획 결과(수량)
    df_in_Plan = df_in_Plan_Org_Qty[col_list]
    df_in_Plan.loc[:,FROZEND_LOTSIZE] = df_in_Plan[FROZEND_LOTSIZE].fillna(0).astype(int)

    #df_in_AllWeek : CurrentWeek 기준으로 -52주차부터 +52주차까지 데이터
    #중목된 주차를 삭제처리
    df_in_AllWeek = df_in_AllWeek[[TIME_WEEK]].drop_duplicates()
    #current 주차보다 큰 주차만 작업대상으로 복사처리
    df_AllWeek = df_in_AllWeek.loc[(df_in_AllWeek[TIME_WEEK] >= current_week)].copy()

    #주차 소트하여 인덱스 재설정처리
    df_AllWeek = df_AllWeek.reset_index(drop='true')
    df_AllWeek[Sequence] = df_AllWeek.index
    vdCommon.gfn_saveDf(df_AllWeek, "df_AllWeek", False)

    # df_in_WResource_Consum Location, ACTIVITY3(item) 기준으로 중복된 데이터 삭제
    df_in_WResource_Consum1 = df_in_WResource_Consum[
        [VERSION_NAME_COLUMN,LOCATION_LOCATION, ACTIVITY3_ACTIVITY3]].drop_duplicates()
    df_in_WResource_Consum_MFT = df_in_WResource_Consum.loc[df_in_WResource_Consum[Resource_Resource_Type]
        .str.contains('MFT')].copy()
    df_in_WResource_Consum_MCT = df_in_WResource_Consum.loc[df_in_WResource_Consum[Resource_Resource_Type]
        .str.contains('MCT')].copy()


    #ResouceType 'MFT' 인것만 남기고 ('MFT','MCT')중복된 데이터 삭제
    df_in_WResource_Consum2 = pd.merge(df_in_WResource_Consum_MFT, df_in_WResource_Consum_MCT,
                                       how='left', on=[VERSION_NAME_COLUMN, ACTIVITY3_ACTIVITY3],
                                       suffixes=('', '_y'), indicator=True)
    del df_in_WResource_Consum_MFT, df_in_WResource_Consum_MCT
    df_in_WResource_Consum2 = df_in_WResource_Consum2[df_in_WResource_Consum2['_merge']=='left_only']
    col_list = [VERSION_NAME_COLUMN, LOCATION_LOCATION, Resource_Resource, Resource_Resource_Type,
                ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, W_Resource_Consumption_Association]
    df_in_WResource_Consum2 = df_in_WResource_Consum2[col_list]

    vdCommon.gfn_saveDf(df_in_WResource_Consum1, "df_in_WResource_Consum1", False)
    vdCommon.gfn_saveDf(df_in_WResource_Consum2, "df_in_WResource_Consum2", False)

    # plan_org에  재설정한 All_Week을 Merge처리한다.
    df_in_Plan = df_in_Plan.merge(df_AllWeek, on=[TIME_WEEK], how='left')


    ############################## 2026.03.12 ybest7.park(박병훈) #######################################################
    # W_LotSize_Increment(lot 수량) & W_Min_LotSize(min lot Size) & W_MinUtil_Fence (기간) 에 대한 merge
    # merge 순서를 변경

    df_in_Plan['key_cols'] = df_in_Plan[ACTIVITY1_ACTIVITY1] + "_" + df_in_Plan[
        ACTIVITY3_ACTIVITY3]

    if df_in_WSoft_LotSize.empty:
        df_in_WSoft_LotSize = pd.DataFrame(columns=df_in_WSoft_LotSize.columns)

    df_in_WSoft_LotSize['key_cols'] = df_in_WSoft_LotSize[ACTIVITY1_ACTIVITY1] + "_" + df_in_WSoft_LotSize[
        ACTIVITY3_ACTIVITY3]

    print_df(df_in_WSoft_LotSize, 'df_in_WSoft_LotSize_데이터 확인', )
    print_df(df_in_Plan, 'df_in_Plan 확인', )

    df_in_Plan = df_in_Plan.merge(
        df_in_WSoft_LotSize[['key_cols', W_LotSize_Increment, W_MinUtil_Fence, W_Min_LotSize]],
        on='key_cols', how='left').drop(columns='key_cols', axis=1)

    # number 컬럼 빈값 0으로 채우기
    numeric_cols = [W_LotSize_Increment, W_MinUtil_Fence, W_Min_LotSize, Sequence,
                    FROZEND_LOTSIZE, W_LotSize_Period, W_LotSize_Period_2]
    df_in_Plan.loc[:, numeric_cols] = df_in_Plan.loc[:, numeric_cols].fillna(0).astype(int)

    # minLot_flag 설정  Sequence >= W_MinUtil_Fence 이면 'Y','N', Y이면 min lot size 적용 구간
    df_in_Plan['minLot_flag'] = np.where(df_in_Plan[Sequence].le(df_in_Plan[W_MinUtil_Fence]),'Y','N')
    vdCommon.gfn_saveDf(df_in_Plan, "df_in_Plan", False)

    # 'W Frozen Window LotSize'와 sequence을 비교하여 sequence값보다 같거나 작은 데이터만 작업대상으로 한다(df_in_plan_SCS_ORG)
    df_in_plan_SCS_TMP = df_in_Plan.loc[(df_in_Plan[FROZEND_LOTSIZE] > df_in_Plan[Sequence])].copy()
    # 비작업대상은(df_in_plan_SCS_TMP)에 적재한다.
    df_in_plan_SCS_ORG = df_in_Plan.loc[(df_in_Plan[FROZEND_LOTSIZE] <= df_in_Plan[Sequence])].copy()
    # df_in_plan_SCS_TMP = df_in_Plan.loc[(df_in_Plan[FROZEND_LOTSIZE] > df_in_Plan['Sequence'])].copy()

    vdCommon.gfn_saveDf(df_in_plan_SCS_ORG, "df_in_plan_SCS_ORG _데이터 확인", True)
    vdCommon.gfn_saveDf(df_in_plan_SCS_TMP, "df_in_plan_SCS_TMP", False)

    #위에서 작업대상인 df_in_plan_SCS_ORG df_in_plan_SCS_TMP데이터프레임으로 한번더 작업대상을 구분한다.(df_in_Plan_SCSB)
    #2번째로 비작업대상 데이터프레임(df_in_Plan_NSCS)
    # DOCUMENTS_ORDERLINEID '%SCS%' DataSet 구분
    df_in_Plan_SCSB = df_in_plan_SCS_ORG.loc[df_in_plan_SCS_ORG[DOCUMENTS_ORDERLINEID].str.contains('SCS')].copy()
    df_in_Plan_NSCS = df_in_plan_SCS_ORG.loc[~df_in_plan_SCS_ORG[DOCUMENTS_ORDERLINEID].str.contains('SCS')].copy()

    # #비작업대상으로 하나의 데이터 프레임으로 합친다.(df_in_Plan_NSCS)
    # vdCommon.gfn_saveDf(df_in_Plan_NSCS, "df_in_Plan_NSCS_concat 전 확인", False)
    # vdCommon.gfn_saveDf(df_in_plan_SCS_TMP, "df_in_plan_SCS_TMP_concat 전 확인", False)
    # df_in_Plan_NSCS = pd.concat([df_in_Plan_NSCS, df_in_plan_SCS_TMP])
    #
    # groupby_cols = [
    #     VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID,
    #     LOCATION_LOCATION, ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2,
    #     ACTIVITY3_ACTIVITY3, FROZEND_LOTSIZE, W_LotSize_Period, W_LotSize_Remain_Config,
    #     W_LotSize_Period_2, W_LotSize_Remain_Config_2,Sequence]
    #
    # #각 데이데set을 W Material Consumption Quantity Plan Output을 group by 기준으로 합계처리한다
    # df_in_Plan_SCSB = df_in_Plan_SCSB.groupby(
    #     groupby_cols, as_index=False)[ORG_QTY].sum()
    # df_in_Plan_NSCS = df_in_Plan_NSCS.groupby(
    #     groupby_cols, as_index=False)[ORG_QTY].sum()

    vdCommon.gfn_saveDf(df_in_Plan_SCSB, "df_in_Plan_SCSB", True)
    vdCommon.gfn_saveDf(df_in_Plan_NSCS, "df_in_plan_NSCS", True)
    # if 1=0
    # df_in_Plan_SCSB New_구간 설정
    ####################################################################################################################
    # # 데이터 타입 변경
    # numeric_cols = [
    #     FROZEND_LOTSIZE, W_LotSize_Period, W_LotSize_Period_2,Sequence]
    #
    # df_in_Plan_SCSB[numeric_cols] = df_in_Plan_SCSB[numeric_cols].astype(int)

    # 신규 데이터 프레임 생성
    df_in_Plan_SCSB_new = pd.DataFrame()  # 신규 빈 데이터 프레임 생성
    # flag가 Y 이면 신규 로직 수행
    filter_cols = [
        VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION,
        ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty, Amend_SOP_SOP_Qty]

    if flag == 'Y':
        df_in_Plan_SCSB_new_temp = df_in_Plan_SCSB.copy()
        vdCommon.gfn_saveDf(df_in_Plan_SCSB_new_temp, "df_in_Plan_SCSB_new____확인", True)

        # 2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)
        df_in_Plan_SCSB_group = df_in_Plan_SCSB_new_temp.groupby(
            [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, LOCATION_LOCATION,ACTIVITY2_ACTIVITY2], as_index=False).agg(
            W_Frozen_Window_LotSize=(FROZEND_LOTSIZE, 'min'),
            W_LotSize_Period=(W_LotSize_Period, 'min'),
            W_LotSize_Period_2=(W_LotSize_Period_2, 'min'),
            W_LotSize_Remain_Config=(W_LotSize_Remain_Config, 'max'),
            W_LotSize_Remain_Config_2=(W_LotSize_Remain_Config_2, 'max')).rename(columns={
            'W_Frozen_Window_LotSize': FROZEND_LOTSIZE, 'W_LotSize_Period': W_LotSize_Period,
            'W_LotSize_Remain_Config': W_LotSize_Remain_Config, 'W_LotSize_Period_2': W_LotSize_Period_2,
            'W_LotSize_Remain_Config_2': W_LotSize_Remain_Config_2})


        print_df(df_in_Plan_SCSB_group, 'df_in_Plan_SCSB_group 데이터 확인', True)

        df_in_Plan_SCSB_new_temp = df_in_Plan_SCSB_new_temp.drop(
            columns=[FROZEND_LOTSIZE, W_LotSize_Period, W_LotSize_Remain_Config,
                     W_LotSize_Period_2, W_LotSize_Remain_Config_2], axis=1).merge(
            df_in_Plan_SCSB_group,
            on=[VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK,LOCATION_LOCATION,ACTIVITY2_ACTIVITY2], how='left') # 기준추가 2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)

        # 데이터 타입 변경
        df_in_Plan_SCSB_new_temp[TIME_WEEK] = pd.to_numeric(df_in_Plan_SCSB_new_temp[TIME_WEEK]).astype(int)
        vdCommon.gfn_saveDf(df_in_Plan_SCSB_new_temp, "df_in_Plan_SCSB_new_temp 데이터 타입 확인", True)

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
        df_in_Plan_SCSB_new_m = pd.concat([df_in_Plan_SCSB_new_m, df_in_Plan_SCSB_new_m1], axis=0, ignore_index=True)
        # 필터에 걸리지 않은 데이터 만들기
        df_in_Plan_SCSB_new_temp = df_in_Plan_SCSB_new_temp.loc[~m_window1].copy()

        vdCommon.gfn_saveDf(df_in_Plan_SCSB_new_m, "df_in_Plan_SCSB_new_m_확인", True)
        vdCommon.gfn_saveDf(df_in_Plan_SCSB_new_temp, "df_in_Plan_SCSB_new_temp_확인", True)
        vdCommon.gfn_saveDf(df_in_Plan_SCSB_new_m1, "df_in_Plan_SCSB_new_m1_데이터 확인", True)

        note(f"===========  df_in_Plan_SCSB_new_m =====================> {df_in_Plan_SCSB_new_m.shape} 첫번째")
        note(f"==========  df_in_Plan_SCSB_new    =====================> {df_in_Plan_SCSB_new_temp.shape} 첫번째")
        note(f"==========  df_in_Plan_SCSB_new _합계    =====> {df_in_Plan_SCSB_new_temp.shape[0] + df_in_Plan_SCSB_new_m.shape[0]}")

        # # Lot Size merge를 위한 Key 설정
        # df_in_Plan_SCSB_new_m['key_cols'] = df_in_Plan_SCSB_new_m[ACTIVITY1_ACTIVITY1] + "_" + df_in_Plan_SCSB_new_m[
        #     ACTIVITY3_ACTIVITY3]
        # df_in_WSoft_LotSize['key_cols'] = df_in_WSoft_LotSize[ACTIVITY1_ACTIVITY1] + "_" + df_in_WSoft_LotSize[
        #     ACTIVITY3_ACTIVITY3]
        # # Lot Size merge
        # df_in_Plan_SCSB_new_m = df_in_Plan_SCSB_new_m.merge(
        #     df_in_WSoft_LotSize[['key_cols', W_LotSize_Increment,W_MinUtil_Fence]],
        #     on='key_cols', how='left').drop(columns='key_cols', axis=1)

        note(f"=====================================> {df_in_Plan_SCSB_new_m.shape} 두번째")

        df_in_Plan_SCSB_new_m['To_location'] = df_in_Plan_SCSB_new_m[ACTIVITY1_ACTIVITY1].str.split('_').str[1]

        df_in_Plan_SCSB_new_m = df_in_Plan_SCSB_new_m.merge(
            df_in_Location.rename(columns={LOCATION_LOCATION: 'To_location'}),
            on='To_location', how='left')

        df_in_Plan_SCSB_new_m[W_LotSize_Increment] = df_in_Plan_SCSB_new_m[W_LotSize_Increment].fillna(0).astype(int)

        note(f"=====================================> {df_in_Plan_SCSB_new_m.shape} 세번째")

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
            by=[ITEM_ITEM, TIME_WEEK, 'p_ship', 'p_site', W_LotSize_Increment, 'To_location', LOCATION_LOCATION, ACTIVITY2_ACTIVITY2],
            ascending=[True, True, True, True, False, True, True,True],
            kind='mergesort').drop(columns=['p_ship', 'p_site'], axis=1) #2026.03.16 추가 필요 Location(생산지),  Activity2 (Trans_Mode)

        df_in_Plan_SCSB_new_m[W_LotSize_Increment] = df_in_Plan_SCSB_new_m[W_LotSize_Increment].fillna(0).astype(int)
        df_in_Plan_SCSB_new_m.reset_index(drop=True, inplace=True)

        # 계산이 필요한 컬럼 나눔
        df_in_Plan_SCSB_new_m_cal = df_in_Plan_SCSB_new_m[df_in_Plan_SCSB_new_m[W_LotSize_Increment] > 1].copy()
        df_in_Plan_SCSB_new_m = df_in_Plan_SCSB_new_m[df_in_Plan_SCSB_new_m[W_LotSize_Increment] <= 1].copy()

        note(f"==========  df_in_Plan_SCSB_new_m_합계    =====> {df_in_Plan_SCSB_new_m_cal.shape[0] + df_in_Plan_SCSB_new_m.shape[0]}")


        # 함수 실행
        df_in_Plan_SCSB_new_m_cal = run_lot_size(df_in_Plan_SCSB_new_m_cal)
        # 컬럼명 변경
        df_in_Plan_SCSB_new_m_cal = df_in_Plan_SCSB_new_m_cal.rename(
                    columns={ORG_QTY: Amend_SOP_ORG_SOP_Qty, 'final_qty': Amend_SOP_SOP_Qty})

        print_df(df_in_Plan_SCSB_new_m_cal, 'df_in_Plan_SCSB_new_m_cal_중간 데이터 확인',True)


        # 필요한 컬럼만 필터
        df_in_Plan_SCSB_new_m_cal = df_in_Plan_SCSB_new_m_cal.reindex(columns=filter_cols)

        print_df(df_in_Plan_SCSB_new_m_cal, 'df_in_Plan_SCSB_new_m_cal concat 확인', False)

        note(f"===========  df_in_Plan_SCSB_new_m_cal =====================> {df_in_Plan_SCSB_new_m_cal.shape} 최종확인")


        # 필터가 되지 않은 데이터 프레임 처리
        df_in_Plan_SCSB_new_m = df_in_Plan_SCSB_new_m.groupby(
            [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION,
             ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3], as_index=False).agg(
            ORG_QTY=(ORG_QTY, 'sum')).rename(columns={'ORG_QTY': Amend_SOP_SOP_Qty})

        df_in_Plan_SCSB_new_m[Amend_SOP_ORG_SOP_Qty] = df_in_Plan_SCSB_new_m[Amend_SOP_SOP_Qty].copy()

        note(f"===========  df_in_Plan_SCSB_new_m =====================> {df_in_Plan_SCSB_new_m.shape} 최종확인")
        note(f"==========  df_in_Plan_SCSB_new_m_합계    =====> {df_in_Plan_SCSB_new_m_cal.shape[0] + df_in_Plan_SCSB_new_m.shape[0]}")

        # 최종 out_put 설정
        df_in_Plan_SCSB_new = pd.concat([df_in_Plan_SCSB_new_m, df_in_Plan_SCSB_new_m_cal])
        df_in_Plan_SCSB_new = df_in_Plan_SCSB_new.loc[~df_in_Plan_SCSB_new[ACTIVITY2_ACTIVITY2].str.contains('RT_')].copy()


        df_in_Plan_SCSB = df_in_Plan_SCSB_new_temp[
            [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION,
             ACTIVITY1_ACTIVITY1 , ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3,ORG_QTY,'minLot_flag',W_Min_LotSize]].copy()

        print_df(df_in_Plan_SCSB, 'df_in_Plan_SCSB _ 분리된 데이터 프레임 확인', False)
        print_df(df_in_Plan_SCSB_new, 'df_in_Plan_SCSB_new _ 분리되고 로직이 진행된 데이터 프레임 확인', False)
    else:
        df_in_Plan_SCSB_new = pd.DataFrame(columns=filter_cols)
        vdCommon.gfn_saveDf(df_in_Plan_SCSB_new, "df_in_Plan_SCSB_new", True)

    ################################################################################################################
    # Step 4 1차 Mfg Sop Qty을 구하기 위한 step
    ###############################################################################################################
    # plan_org에서 데이터 필터 한 후 작업시작
    # 작업대상 데이터프레임(df_in_Plan_SCSB에 LOtSize수량(df_in_WSoft_LotSize)을 ITEM, ACTIVITY1 조건으로 left join하여 새로운 데이터 프레임 df_in_Plan_SCS생성한다.
    df_in_Plan_SCS = pd.merge(df_in_Plan_SCSB, df_in_WSoft_LotSize, how='left',
                              on=[VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1], suffixes=('', '_y'),
                              indicator=True)
    vdCommon.gfn_saveDf(df_in_Plan_SCS, "df_in_Plan_SCS", False)

    # lotSize컬럼이 (null일경우 1, 0일떄 1)으로 치환한다
    df_in_Plan_SCS[W_LotSize_Increment] = np.where(df_in_Plan_SCS[W_LotSize_Increment].isna(), 1,
                                                   np.where(df_in_Plan_SCS[W_LotSize_Increment] == 0, 1,
                                                            df_in_Plan_SCS[W_LotSize_Increment]))

    df_in_Plan_SCS[W_Min_LotSize] = np.where(df_in_Plan_SCS[W_Min_LotSize].isna(), 1,
                                                   np.where(df_in_Plan_SCS[W_Min_LotSize] == 0, 1,
                                                            df_in_Plan_SCS[W_Min_LotSize]))

    df_in_Plan_SCS = df_in_Plan_SCS[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, ORG_QTY, W_LotSize_Increment,W_Min_LotSize,'minLot_flag']]

    # ResourceConsum을 Location, ACTIVITY3조건으로 leftjoin하여 작업대상 DataSet에 Merge처리
    df_in_Plan_SCS = pd.merge(df_in_Plan_SCS, df_in_WResource_Consum1, how='left',
                              on=[VERSION_NAME_COLUMN, LOCATION_LOCATION, ACTIVITY3_ACTIVITY3], suffixes=('', '_y'),
                              indicator=True)
    vdCommon.gfn_saveDf(df_in_Plan_SCS, "df_in_Plan_SCS ---- 데이터 확인", True)

    # cumsum, Max주차를  Item,ACTIVITY1기준으로 컬럼 생성하여 데이터 입력처리한다
    # df_in_Plan_cumsum : 주차별로 'W Material Consumption Quantity Plan Output' 데이터를 누적처리한다.
    # df_in_Plan_MaxWeek : 마직막 주차여부 확인을 위해 컬럼을 생성한다.

    # 컬럼 방버 코딩
    df_in_Plan_SCS['df_in_Plan_cumsum'] = pd.Series(dtype='float64')

    df_in_Plan_SCS['ORG_QTY'] = pd.to_numeric(df_in_Plan_SCS['df_in_Plan_cumsum'], errors='coerce').fillna(0)
    df_in_Plan_SCS['df_in_Plan_cumsum'] = \
    df_in_Plan_SCS.groupby([VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1], as_index=False)[ORG_QTY].cumsum()

    # if df_in_Plan_SCS.empty:
    #     df_in_Plan_SCS = df_in_Plan_SCS.reindex(columns=list(df_in_Plan_SCS.columns) + ['df_in_Plan_cumsum'])
    #     df_in_Plan_SCS['df_in_Plan_cumsum'] = pd.Series(dtype = 'float64')
    # else:
    #     df_in_Plan_SCS['ORG_QTY'] = pd.to_numeric(df_in_Plan_SCS['df_in_Plan_cumsum'], errors='coerce').fillna(0)
    #     df_in_Plan_SCS['df_in_Plan_cumsum'] = df_in_Plan_SCS.groupby([VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1], as_index=False)[ORG_QTY].cumsum()


    # df_in_Plan_SCS['df_in_Plan_cumsum'] = \
    # df_in_Plan_SCS.groupby([VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1], as_index=False)[ORG_QTY].cumsum()
    df_in_Plan_SCS['df_in_Plan_MaxWeek'] = \
    df_in_Plan_SCS.groupby([VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1], as_index=False)[TIME_WEEK].transform(
        'max')

    # cum_sum구할떄 소수점을 버림처리
    df_in_Plan_SCS['floor_qty'] = (df_in_Plan_SCS['df_in_Plan_cumsum'] // df_in_Plan_SCS[W_LotSize_Increment]) * \
                                  df_in_Plan_SCS[W_LotSize_Increment]

    # VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1 기준으로 데이터 다음 레코드로 복사처리한후 null일떄 0으로 처리
    df_in_Plan_SCS['New_qty'] = \
    df_in_Plan_SCS.groupby([VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1], as_index=False)['floor_qty'].shift()
    df_in_Plan_SCS['New_qty'] = df_in_Plan_SCS['New_qty'].fillna(0)

    df_in_Plan_SCS['New_qty_1'] = df_in_Plan_SCS['floor_qty'] - df_in_Plan_SCS['New_qty']
    df_in_Plan_SCS['New_qty_1'] = df_in_Plan_SCS['New_qty_1'].fillna(0)
    # vdCommon.gfn_saveDf(df_in_Plan_SCS, "df_in_Plan_SCS1", True)

    # df_in_WResource_Consum에 등록된 Item을 처리한다.
    # Consum에 등록된 Itemd: f_in_Plan_SCS['df_in_Plan_cumsum'] - df_in_Plan_SCS['New_qty']  Consum에 등록되지않은 Item: df_in_Plan_SCS['floor_qty'] - df_in_Plan_SCS['New_qty']
    df_in_Plan_SCS['New_qty_1'] = np.where((df_in_Plan_SCS['_merge'].str.contains('both')) & (
                df_in_Plan_SCS[TIME_WEEK] == df_in_Plan_SCS['df_in_Plan_MaxWeek']),
                                           df_in_Plan_SCS['df_in_Plan_cumsum'] - df_in_Plan_SCS['New_qty'],
                                           df_in_Plan_SCS['floor_qty'] - df_in_Plan_SCS['New_qty'])


    # df_in_Plan_SCS = minLotSize(df_in_Plan_SCS)

    vdCommon.gfn_saveDf(df_in_Plan_SCS, "df_in_Plan_SCS2", True)

    ################################################################################################################
    # STEP 5 : Amend_SOP_MfgSOPQty : 1차 Sop Mfg Qty 확정
    ################################################################################################################
    # df_in_Plan_NASCS: 'W LotSize Increment'이 null인경우와 1보자 작은 데이터를 분리한다.
    df_in_Plan_NASCS = df_in_Plan_SCS.loc[
        df_in_Plan_SCS['W LotSize Increment'].isna() | (df_in_Plan_SCS['W LotSize Increment'] <= 1)].copy()
    vdCommon.gfn_saveDf(df_in_Plan_NASCS, "df_in_Plan_NASCS", True)

    # W LotSize Increment(Lot Size)가 1보다 큰 데이터만 갖고온다.
    df_in_Plan_SCS = df_in_Plan_SCS.loc[df_in_Plan_SCS['W LotSize Increment'] > 1].copy()

    df_in_Plan_NASCS = df_in_Plan_NASCS[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, ORG_QTY,'minLot_flag']]

    # 기존 계산에서 제외된 데이터프레임 df_in_Plan_NASCS데이터를 합친다
    df_in_Plan_NSCS = pd.concat([df_in_Plan_NSCS, df_in_Plan_NASCS])

    df_in_Plan_NSCS.rename(columns={'W Material Consumption Quantity Plan Output': Amend_SOP_ORG_SOP_Qty},
                           inplace=True)
    df_in_Plan_NSCS[Amend_SOP_SOP_Qty] = df_in_Plan_NSCS[Amend_SOP_ORG_SOP_Qty]

    df_in_Plan_NSCS = df_in_Plan_NSCS[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty, Amend_SOP_SOP_Qty ,'minLot_flag',W_Min_LotSize]]

    ####################################################################################################################
    # 2026.03.17 추가
    def minLotSize(df):
        df = df.copy()
        df['minLot_flag'] = df['minLot_flag'].fillna('N').astype(str)
        df[W_Min_LotSize] = pd.to_numeric(df[W_Min_LotSize], errors='coerce').fillna(0)
        df[Amend_SOP_SOP_Qty] = pd.to_numeric(df[Amend_SOP_SOP_Qty], errors='coerce').fillna(0)
        mask_flag = (df['minLot_flag'] == 'Y') & (
            df[W_Min_LotSize] > df[Amend_SOP_SOP_Qty])

        df.loc[mask_flag,Amend_SOP_SOP_Qty] = 0

        return df

    df_in_Plan_NSCS = minLotSize(df_in_Plan_NSCS)
    vdCommon.gfn_saveDf(df_in_Plan_NSCS, "df_in_Plan_NSCS____확인 값 비교", True)

    # 내부적으로 사용한 New_qty_1을  Amend SOP_ORG SOP Qty으로 Rename한다
    df_in_Plan_SCS.rename(columns={'New_qty_1': Amend_SOP_ORG_SOP_Qty}, inplace=True)

    # df_Amend_SOP_MfgSOPQty에 임시로 사용된 컬럼을 제외하고 재지정한다.
    df_Amend_SOP_MfgSOPQty = df_in_Plan_SCS[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty,'minLot_flag',W_Min_LotSize]]

    # 1차로  MfgSOPQty 데이터 처리 완성
    # ACTIVITY2 데이터 중 'RT_'로 시작하는 데이터 삭제한다.
    df_Amend_SOP_MfgSOPQty = df_Amend_SOP_MfgSOPQty.loc[
        ~df_Amend_SOP_MfgSOPQty[ACTIVITY2_ACTIVITY2].str.contains('RT_')].copy()

    vdCommon.gfn_saveDf(df_Amend_SOP_MfgSOPQty, "df_Amend_SOP_MfgSOPQty", True)

    ################################################################################################################
    # STEP 6 : MFT(기획생산)인 대상에 대한 물량만 처리 step
    ################################################################################################################
    #
    # MCT(단종) 관련 설정이 없는 품목기준으로, MFT(기획생산)인 대상에 대한 설정값 MAX 추차를 초과하는 구간이후에 물량중 가장 마지막 주자의 물량에서 LotSize만큼 물량을 제외함 (음수가 나올경우 0처리)
    #
    # 주차컬럼 데이터 형식을 integer로 치환한다
    # 치환하지 않으면 Local에서는 문제가 없지만 O9에서는 에러가 발생되므로 치환한다
    df_in_WResource_Capa[TIME_WEEK] = df_in_WResource_Capa[TIME_WEEK].astype('int64')

    # df_Resource_Capa : df_in_WResource_Consum2, df_in_WResource_Capa을 inner조건으로 새로운 데이터프레임을 구성한다.(LOCATION_LOCATION, 'Resource.[Resource]')
    df_Resource_Capa = pd.merge(df_in_WResource_Consum2, df_in_WResource_Capa, how='inner',
                                on=[VERSION_NAME_COLUMN, LOCATION_LOCATION, 'Resource.[Resource]'], suffixes=('', '_y'),
                                indicator=True)
    # Resource기준으로 Max(주차) 구한다
    df_Resource_Capa['Rank'] = \
    df_Resource_Capa.groupby(['Resource.[Resource]', ACTIVITY3_ACTIVITY3, LOCATION_LOCATION])[TIME_WEEK].rank(
        method="first", ascending=False)
    vdCommon.gfn_saveDf(df_Resource_Capa, "df_Resource_Capa0", False)
    # df_Resource_Capa에서 Max주차인 데이터만 재정의한다.
    df_Resource_Capa = df_Resource_Capa.loc[(df_Resource_Capa['Rank'] == 1)].copy()
    vdCommon.gfn_saveDf(df_Resource_Capa, "df_Resource_Capa1", False)
    col_list = [VERSION_NAME_COLUMN, 'Resource.[Resource]', 'Resource.[Resource Type]', LOCATION_LOCATION, TIME_WEEK,
                ACTIVITY3_ACTIVITY3]
    df_Resource_Capa = df_Resource_Capa[col_list]

    # ConSUM 에서 MFT(기획생산) 대상만 Resource Merge한다
    # df_Resource: df_Resource_Capa,df_Resource_Capa을 inner조건으로 새로운 데이터프레임을 구성한다(LOCATION_LOCATION, 'Resource.[Resource]')
    # df_Resource = pd.merge(df_in_WResource_Consum2, df_Resource_Capa, how='inner',
    #                        on=[VERSION_NAME_COLUMN, LOCATION_LOCATION, 'Resource.[Resource]'], suffixes=('', '_y'))
    # vdCommon.gfn_saveDf(df_Resource_Capa, "df_Resource_Capa", False)

    # step5에서 작성한 데이터프레임에 Resource_Capa을추가한다.
    # df_Amend_Qty : df_Amend_SOP_MfgSOPQty, df_Resource_Capa을 Outjoin으로 데이터프레임을 구성한다.(LOCATION_LOCATION,ACTIVITY3_ACTIVITY3)
    df_Amend_Qty = pd.merge(df_Amend_SOP_MfgSOPQty, df_Resource_Capa, how='left',
                            on=[VERSION_NAME_COLUMN, LOCATION_LOCATION, ACTIVITY3_ACTIVITY3], suffixes=('', '_y'),
                            indicator=True)
    vdCommon.gfn_saveDf(df_Amend_Qty, "df_Amend_Qty10", False)

    # df_out_Amend_Qty,df_in_WSoft_LotSize(LotSize수량)을 OutJoin으로 데이터프레임 구성한다(ITEM_ITEM, ACTIVITY1_ACTIVITY1)
    df_out_Amend_Qty = pd.merge(df_Amend_Qty, df_in_WSoft_LotSize, how='left',
                                on=[VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1], suffixes=('', '_y'))

    # 재구성한 df_out_Amend_Qty('both', 'left_only')으로 작업대상을 분리한다.
    df_out_Amend_Qty1 = df_out_Amend_Qty.loc[df_out_Amend_Qty['_merge'].str.contains('both')].copy()
    df_out_Amend_Qty2 = df_out_Amend_Qty.loc[df_out_Amend_Qty['_merge'].str.contains('left_only')].copy()

    vdCommon.gfn_saveDf(df_out_Amend_Qty1, "df_out_Amend_Qty1", False)
    vdCommon.gfn_saveDf(df_out_Amend_Qty2, "df_out_Amend_Qty2", False)

    # 각작업대상에 Shipment_LT을 OutJoin으로 추가한다(ACTIVITY1_ACTIVITY1, ACTIVITY3_ACTIVITY3)
    df_out_Amend_Qty1 = df_out_Amend_Qty1.merge(df_in_Shipment_LT,
                                                on=[VERSION_NAME_COLUMN, ACTIVITY1_ACTIVITY1, ACTIVITY3_ACTIVITY3],
                                                how='left')
    df_out_Amend_Qty2 = df_out_Amend_Qty2.merge(df_in_Shipment_LT,
                                                on=[VERSION_NAME_COLUMN, ACTIVITY1_ACTIVITY1, ACTIVITY3_ACTIVITY3],
                                                how='left')

    df_out_Amend_Qty1[TIME_WEEK] = df_out_Amend_Qty1[TIME_WEEK].astype('int64')
    df_out_Amend_Qty1.rename(columns={'Activity2.[Activity2]_x': ACTIVITY2_ACTIVITY2}, inplace=True)
    df_out_Amend_Qty1['Rank'] = df_out_Amend_Qty1.groupby([ITEM_ITEM, ACTIVITY1_ACTIVITY1, ACTIVITY3_ACTIVITY3])[
        TIME_WEEK].rank(method="first", ascending=False)

    # Max주차에  Shipment_LT을 더한다.
    df_out_Amend_Qty1['Time.[Week]_x'] = df_out_Amend_Qty1['Time.[Week]_y'] + df_out_Amend_Qty1[
        'W Activity Mandatory Offset']
    vdCommon.gfn_saveDf(df_out_Amend_Qty1, "df_out_Amend_Qty12", False)

    # 최종적으로  'Amend SOP_SOP Qty' 계산처리한다.
    df_out_Amend_Qty1[Amend_SOP_SOP_Qty] = np.where(
        (df_out_Amend_Qty1[TIME_WEEK] > df_out_Amend_Qty1['Time.[Week]_x']) & (df_out_Amend_Qty1['Rank'] == 1),
        df_out_Amend_Qty1[Amend_SOP_ORG_SOP_Qty] - df_out_Amend_Qty1['W LotSize Increment'],
        df_out_Amend_Qty1[Amend_SOP_ORG_SOP_Qty])
    df_out_Amend_Qty1[Amend_SOP_SOP_Qty] = np.where(df_out_Amend_Qty1[Amend_SOP_SOP_Qty] <= 0, 0,
                                                      df_out_Amend_Qty1[Amend_SOP_SOP_Qty])
    # 최종적으로 MFT(기획생산)인 대상 데이터set 저장한다.
    df_out_Amend_Qty1[Amend_SOP_SOP_Qty] = np.where(df_out_Amend_Qty1[Amend_SOP_SOP_Qty] < 0, 0,
                                                      df_out_Amend_Qty1[Amend_SOP_SOP_Qty])

    vdCommon.gfn_saveDf(df_out_Amend_Qty1, "df_out_Amend_Qty1", False)

    # df_out_Amend_SOP_MfgSOPQty = df_out_Amend_Qty[[VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1, ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3,'Amend SOP_ORG SOP Qty', 'Amend SOP_SOP Qty']]

    ################################################################################################################
    # STEP 7 : 확정대상 ("MCT","SCT","MFT","SRT") 이 아닌 일반물량 처리 step
    ################################################################################################################
    #
    # 2) 확정대상 ("MCT","SCT","MFT","SRT") 이 아닌 일반물량은 가장 마지막 주자의 물량에서 LotSize만큼 물량을 제외함 (음수가 나올경우 0처리)
    #

    df_out_Amend_Qty2[TIME_WEEK] = df_out_Amend_Qty2[TIME_WEEK].astype('int64')
    df_out_Amend_Qty2.rename(columns={'Activity2.[Activity2]_x': ACTIVITY2_ACTIVITY2}, inplace=True)
    vdCommon.gfn_saveDf(df_out_Amend_Qty2, "df_out_Amend_Qty21", False)
    df_out_Amend_Qty2 = df_out_Amend_Qty2[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty]]
    # 확정대상이 아닌 물량에 df_in_WResource_Consum1을합친다
    # df_out_Amend_Qty3 : df_out_Amend_Qty2, df_in_WResource_Consum1을 OutJoin으로 구성한다.(ACTIVITY3_ACTIVITY3)
    df_out_Amend_Qty3 = pd.merge(df_out_Amend_Qty2, df_in_WResource_Consum1, how='left',
                                 on=[VERSION_NAME_COLUMN, ACTIVITY3_ACTIVITY3], suffixes=('', '_y'), indicator=True)

    vdCommon.gfn_saveDf(df_out_Amend_Qty3, "df_out_Amend_Qty22", True)
    # df_out_Amend_Qty4 : 바로 위에서 작업한 df_out_Amend_Qty3에 df_in_WSoft_LotSize을 추가한다(ITEM_ITEM, ACTIVITY1_ACTIVITY1,ACTIVITY3_ACTIVITY3)
    df_out_Amend_Qty4 = pd.merge(df_out_Amend_Qty3, df_in_WSoft_LotSize, how='left',
                                 on=[VERSION_NAME_COLUMN, ITEM_ITEM, ACTIVITY1_ACTIVITY1, ACTIVITY3_ACTIVITY3],
                                 suffixes=('', '_y'))

    df_out_Amend_Qty4[W_LotSize_Increment] = np.where(df_out_Amend_Qty4[W_LotSize_Increment].isna(), 0,
                                                      np.where(df_out_Amend_Qty4[W_LotSize_Increment] == 0, 0,
                                                               df_out_Amend_Qty4[W_LotSize_Increment]))
    df_out_Amend_Qty4['Rank'] = df_out_Amend_Qty4.groupby([ITEM_ITEM, ACTIVITY1_ACTIVITY1])[TIME_WEEK].rank(
        method="first", ascending=False)
    vdCommon.gfn_saveDf(df_out_Amend_Qty4, "df_out_Amend_Qty41", False)

    # 가장 마지막 주자의 물량에서 LotSize만큼 물량을 제외한다.
    df_out_Amend_Qty4[Amend_SOP_SOP_Qty] = np.where(
        (df_out_Amend_Qty4['Rank'] == 1) % (df_out_Amend_Qty4['_merge'].str.contains('left_only')),
        df_out_Amend_Qty4[Amend_SOP_ORG_SOP_Qty] - df_out_Amend_Qty4['W LotSize Increment'],
        df_out_Amend_Qty4[Amend_SOP_ORG_SOP_Qty])
    df_out_Amend_Qty4[Amend_SOP_SOP_Qty] = np.where(df_out_Amend_Qty4[Amend_SOP_SOP_Qty] <= 0, 0,
                                                      df_out_Amend_Qty4[Amend_SOP_SOP_Qty])

    df_out_Amend_Qty1 = df_out_Amend_Qty1[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty, Amend_SOP_SOP_Qty]]
    df_out_Amend_Qty4 = df_out_Amend_Qty4[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty, Amend_SOP_SOP_Qty]]

    vdCommon.gfn_saveDf(df_out_Amend_Qty4, "df_out_Amend_Qty4", False)
    vdCommon.gfn_saveDf(df_out_Amend_Qty1, "df_out_Amend_Qty1", False)

    # 위 작업한 1) 과 2)을 합친다.
    # df_Amend_SOP_MfgSOPQty : MFT(기획생산)인 대상에 대한 물량과 확정대상 ("MCT","SCT","MFT","SRT") 이 아닌 일반물량을 하나의 데이터프레임으로 합친다.
    df_Amend_SOP_MfgSOPQty = pd.concat([df_out_Amend_Qty1, df_out_Amend_Qty4], ignore_index=False)

    df_Amend_SOP_MfgSOPQty = df_Amend_SOP_MfgSOPQty[
        [VERSION_NAME_COLUMN, ITEM_ITEM, TIME_WEEK, DOCUMENTS_ORDERLINEID, LOCATION_LOCATION, ACTIVITY1_ACTIVITY1,
         ACTIVITY2_ACTIVITY2, ACTIVITY3_ACTIVITY3, Amend_SOP_ORG_SOP_Qty, Amend_SOP_SOP_Qty]]

    vdCommon.gfn_saveDf(df_Amend_SOP_MfgSOPQty, "df_Amend_SOP_MfgSOPQty", False)

    df_Amend_SOP_MfgSOPQty = df_Amend_SOP_MfgSOPQty.reset_index(drop=True)
    df_in_Plan_NSCS = df_in_Plan_NSCS.reset_index(drop=True)

    vdCommon.gfn_saveDf(df_in_Plan_NSCS, "df_in_Plan_NSCS_확인_old_version", True)
    vdCommon.gfn_saveDf(df_in_Plan_SCSB_new, "df_in_Plan_SCSB_new_확인_old_version", False)
    vdCommon.gfn_saveDf(df_Amend_SOP_MfgSOPQty, "df_Amend_SOP_MfgSOPQty_확인_old_version", False)

    #최종적으로 작업한 dataset이랑 비작업대상인 DataSet을 합친다.

    df_out_Amend_SOP_MfgSOPQty = pd.concat( [df_Amend_SOP_MfgSOPQty, df_in_Plan_NSCS, df_in_Plan_SCSB_new],ignore_index=True, axis=0)


    ###################################################################################################################
    # df_out_Amend_SOP_MfgSOPQty['minLot_flag'] = df_out_Amend_SOP_MfgSOPQty['minLot_flag'].fillna('N').astype(str)
    # df_out_Amend_SOP_MfgSOPQty[W_Min_LotSize] = df_out_Amend_SOP_MfgSOPQty[W_Min_LotSize].fillna(0).astype(int)
    # mask_flag = (df_out_Amend_SOP_MfgSOPQty['minLot_flag'] == 'Y') & (
    #             df_out_Amend_SOP_MfgSOPQty[W_Min_LotSize] > df_out_Amend_SOP_MfgSOPQty[Amend_SOP_SOP_Qty])
    # df_out_Amend_SOP_MfgSOPQty.loc[mask_flag,Amend_SOP_SOP_Qty] = 0

    df_out_Amend_SOP_MfgSOPQty = df_out_Amend_SOP_MfgSOPQty.drop(columns=[W_Min_LotSize,'minLot_flag'], axis=1)
    df_out_Amend_SOP_MfgSOPQty[Amend_SOP_ORG_SOP_Qty] = pd.to_numeric(
        df_out_Amend_SOP_MfgSOPQty[Amend_SOP_ORG_SOP_Qty], errors='coerce').fillna(0).astype(int)

    df_out_Amend_SOP_MfgSOPQty[Amend_SOP_SOP_Qty] = pd.to_numeric(
        df_out_Amend_SOP_MfgSOPQty[Amend_SOP_SOP_Qty], errors='coerce').fillna(0).astype(int)
    ###################################################################################################################

    row_count, col_count = df_out_Amend_SOP_MfgSOPQty.shape

    df_out_Amend_SOP_MfgSOPQty["Version.[Version Name]"] = paramOutVersion

    vdCommon.gfn_saveDf(df_out_Amend_SOP_MfgSOPQty, "df_out_Amend_SOP_MfgSOPQty_New_확인", True)

    #위 로직에서 사용한 데이터프레임을 삭제한다.
    del df_AllWeek, df_in_Plan, df_in_plan_SCS_ORG, df_in_plan_SCS_TMP
    del df_in_Plan_SCSB, df_in_Plan_NSCS
    del df_in_WResource_Consum1, df_in_WResource_Consum2
    del df_in_Plan_SCS, df_in_Plan_NASCS, df_Amend_SOP_MfgSOPQty
    # del df_Resource_Capa, df_Resource
    del df_out_Amend_Qty, df_out_Amend_Qty1, df_out_Amend_Qty2, df_out_Amend_Qty3, df_out_Amend_Qty4

    vdCommon.gfn_stepLog('plugin Execution End')

    ################################################################################################################
    # Step 3. 종료
    ################################################################################################################

except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out_Amend_SOP_MfgSOPQty = pd.DataFrame([], columns=[])

finally:
    # Batch 종료
    vdCommon.gfn_pyLog_end()

    df_out_log = vdCommon.gfn_getLog()
    df_out_logDetail = vdCommon.gfn_getLogDetail()

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

