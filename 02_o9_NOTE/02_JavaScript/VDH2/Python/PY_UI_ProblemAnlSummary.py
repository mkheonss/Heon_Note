"""
* Plugin Instance Name
    - PY_UI_ProblemAnlSummary

* 목적
    - Problem Analysis 데이터를 Location/Sub Location/Sales Domain/Time/Seq1 기준으로 집계
    - Demand Qty, Short Qty 합계 계산
    - Problem Reason 기준 상위 10 개 추출

* 수정이력    - 2026.03.23 / hnsk92.jeong / Create
              - 2026.03.24 / hnsk92.jeong / Update : [Sales Domain].[Customer Group] -> [Sales Domain].[Ship To] grain 변경사항 반영
              - 2026.03.25 / hnsk92.jeong / Update : [FCST Type].[FCST Type] -> [Demand Priority].[Demand Type Rank] grain 변경사항 반영


* Flow Summary
    STEP1. Input DataFrame 로드 및 전처리
    STEP2. Seq1 == 1인 데이터(Single Short만 대상) 처리 (Location/Sub Location/Sales Domain/Item/Time 기준 집계, Reason unique 추출)
    STEP3. Seq1 값 무관 전체 데이터(Multi Short 포함) 처리 (Location/Sub Location/Sales Domain/Item/Time 기준 집계, Reason unique 추출)
    STEP4. STEP2 & 3 결과 병합 (concat)
    STEP5. Output DataFrame 생성

* Execution

* Script Parameter
    - paramOutVersion : CWV_MP : 출력 Version.

* Input Tables
    - df_in_ProblemAnl : Select ([Location].[Location] * [Sub Location].[Sub Location] * [Sales Domain].[Ship To] *
                           [Time].[Week] * [To Time].[To Week] * [Problem Type].[Problem Reason] * [AIR Idx].[AIR Idx] *
                           [Demand Priority].[Demand Type Rank] * [Seq1].[Seq1] * [Seq2].[Seq2]) on row,
                          ({Measure.[Problem Anl_Demand Qty], Measure.[Problem Anl_Short Qty]}) on column where {[Version].[Version Name]};

    - df_in_ProblemType : Select ([Version].[Version Name] * [Problem Type].[Problem Reason] ) on row,
                          ({Measure.[Problem Type_Priority]}) on column;

* Output Tables
    - df_out_ProblemAnlSummary : Select ([Location].[Location] * [Sub Location].[Sub Location] * [Sales Domain].[Ship To] *
                                   [Item].[Item] * [Time].[Week]) on row,
                                  ({Measure.[Problem Anl Summary_Demand Qty], Measure.[Problem Anl Summary_Short Qty],
                                    Measure.[Problem Anl Summary_Short Reason1], ..., Measure.[Problem Anl Summary_Short Reason10]}) on column;

* 실행 명령어
    EXEC plugin instance [PY_UI_ProblemAnlSummary] for measures {[Problem Anl Summary_Demand Qty]}
    using scope (&CWVUI)
    using arguments {(paramOutVersion, "CWV_MP"), (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1)};

"""

import pandas as pd
import os
import traceback
import pyarrow

from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 변수 설정 및 로깅 설정 수행
########################################################################################################################
# o9 platform instanceName
str_instance = 'PY_UI_ProblemAnlSummary'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()
LOG_LEVEL = common.G_log_level

logger.debug(f'[START] {str_instance}')
logger.Start()

########################################################################################################################
# Single Short(Seq1 == 1) 및 Multi Short(Seq == 2) 공용 집계 함수
########################################################################################################################
def aggregate(df: pd.DataFrame, group_key: list) -> pd.DataFrame:
    """
    Demand/Short 합계 집계 및 Top10 Reason 추출 (벡터화 처리)
    """
    # 1. Demand / Short sum
    df_agg = (
        df
        .groupby(group_key, as_index=False, observed=True)
        .agg({problemAnl_DemandQty: "sum", problemAnl_ShortQty: "sum"},)
        .rename(columns={
            problemAnl_DemandQty: problemAnlSummary_DemandQty,
            problemAnl_ShortQty: problemAnlSummary_ShortQty
        })
    )
    vdCommon.gfn_saveDf(df_agg, "sum demand & short qty", True)

    # 2. Top10 Reason - apply 없이 벡터화 처리
    #    step1: group + reason 별 빈도 카운트
    df_reason_cnt = (
        df
        .groupby(group_key + [PROBLEM_REASON], observed=True)
        .size()
        .reset_index(name="_cnt")
    )
    vdCommon.gfn_saveDf(df_reason_cnt, "df_reason_cnt", True)

    #    step2: priority 매핑 (정렬 기준)
    df_reason_cnt["_priority"] = (
        df_reason_cnt[PROBLEM_REASON]
        .map(priority_map)
        .fillna(float("inf"))
    )
    vdCommon.gfn_saveDf(df_reason_cnt, "df_reason_cnt _priority", True)

    #    step3: group 내에서 빈도 내림차순 정렬 → rank 부여 (top10 필터)
    df_reason_cnt["_freq_rank"] = (
        df_reason_cnt
        .groupby(group_key, observed=True)["_cnt"]
        .rank(method="first", ascending=False)
    )
    vdCommon.gfn_saveDf(df_reason_cnt, "df_reason_cnt _freq_rank", True)

    df_top10 = df_reason_cnt[df_reason_cnt["_freq_rank"] <= 10].copy()
    vdCommon.gfn_saveDf(df_top10, "df_top10", True)

    #    step4: top10 내에서 priority 오름차순 정렬 → priority_rank 부여
    df_top10["_priority_rank"] = (
        df_top10
        .groupby(group_key, observed=True)["_priority"]
        .rank(method="first", ascending=True)
    ).astype(int)
    vdCommon.gfn_saveDf(df_top10, "df_top10 _priority_rank", True)

    #    step5: pivot → Reason1~10 컬럼 생성
    reason_cols_map = {}
    for rank in range(1, 11):
        col_name = problemAnlSummary_ShortReason_format.format(rank)
        rank_df = df_top10[df_top10["_priority_rank"] == rank][group_key + [PROBLEM_REASON]]
        rank_df = rank_df.rename(columns={PROBLEM_REASON: col_name})
        reason_cols_map[rank] = rank_df

    df_reasons = df_agg[group_key].drop_duplicates()
    for rank in range(1, 11):
        df_reasons = df_reasons.merge(reason_cols_map[rank], on=group_key, how="left")

    # 3. merge
    return df_agg.merge(df_reasons, on=group_key, how="left")


########################################################################################################################
# Main Logic
########################################################################################################################
try:
    ################################################################################################################
    # Batch 시작
    ################################################################################################################
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    # Input DataFrame 로깅
    vdCommon.gfn_saveDf(df_in_ProblemAnl, "df_in_ProblemAnl", True)
    vdCommon.gfn_saveDf(df_in_ProblemType, "df_in_ProblemType", True)

    ################################################################################################################
    # DataFrame Column : 변수 처리
    ################################################################################################################
    vdCommon.gfn_stepLog('=====> DataFrame Column : 변수 처리')

    # grains
    VERSION_NAME = 'Version.[Version Name]'
    WEEK = 'Time.[Week]'
    ITEM = 'Item.[Item]'
    LOCATION = 'Location.[Location]'
    SHIP_TO = 'Sales Domain.[Ship To]'
    SUB_LOCATION = 'Sub Location.[Sub Location]'
    SEQ1 = 'Seq1.[Seq1]'
    SEQ2 = 'Seq2.[Seq2]'
    AIR_IDX = 'AIR Idx.[AIR Idx]'
    DMD_TYPE_RANK = 'Demand Priority.[Demand Type Rank]'
    TO_WEEK = 'To Time.[To Week]'
    PROBLEM_REASON = 'Problem Type.[Problem Reason]'

    # input measures
    problemAnl_DemandQty = 'Problem Anl_Demand Qty'
    problemAnl_ShortQty = 'Problem Anl_Short Qty'
    problemType_Priority = 'Problem Type_Priority'

    # output measures
    problemAnlSummary_DemandQty = 'Problem Anl Summary_Demand Qty'
    problemAnlSummary_ShortQty = 'Problem Anl Summary_Short Qty'
    problemAnlSummary_ShortReason_format = "Problem Anl Summary_Short Reason{}"
    reason_cols = [problemAnlSummary_ShortReason_format.format(i) for i in range(1, 11)]

    ####################################################################################################################
    # STEP1. 전처리
    ####################################################################################################################

    ####################################################################################################################
    # STEP1.1. 불필요 컬럼 제거 및 category dtype으로 메모리 절약
    ####################################################################################################################
    df_work = df_in_ProblemAnl.drop(
        columns=[SEQ2, TO_WEEK],
        errors="ignore",
    )

    # NaN 처리
    df_work[PROBLEM_REASON] = df_work[PROBLEM_REASON].astype(str)
    df_work[PROBLEM_REASON] = df_work[PROBLEM_REASON].fillna("")
    df_work[problemAnl_DemandQty] = df_work[problemAnl_DemandQty].fillna(0)
    df_work[problemAnl_ShortQty] = df_work[problemAnl_ShortQty].fillna(0)

    vdCommon.gfn_saveDf(df_work, "step1.1 preprocessed", True)

    ####################################################################################################################
    # STEP1.2. Category dtype 변환으로 메모리 절약
    ####################################################################################################################
    BASE_GROUP_KEY = [LOCATION, SUB_LOCATION, SHIP_TO, ITEM, WEEK]
    category_cols = BASE_GROUP_KEY + [SEQ1]
    for col in category_cols:
        if col in df_work.columns:
            df_work[col] = df_work[col].astype("category")

    vdCommon.gfn_saveDf(df_work, "step1.2 category converted", True)

    ####################################################################################################################
    # STEP1.3. Problem Type Priority 매핑 생성
    ####################################################################################################################
    # df_in_ProblemType에서 Problem Reason과 Priority 매핑 생성
    priority_map = df_in_ProblemType.set_index(PROBLEM_REASON)[problemType_Priority].to_dict()


    ####################################################################################################################
    # STEP2. Seq1 = 1인 데이터 처리
    ####################################################################################################################
    df_seq1 = aggregate(
        df_work[df_work[SEQ1] == "1"],
        BASE_GROUP_KEY
    )
    df_seq1[SEQ1] = "1"
    vdCommon.gfn_saveDf(df_seq1, "step2 seq1 aggregated", True)


    ####################################################################################################################
    # STEP3. Seq1 = 2 처리 (전체 row)
    ####################################################################################################################
    df_seq2 = aggregate(
        df_work,
        BASE_GROUP_KEY
    )
    df_seq2[SEQ1] = "2"
    vdCommon.gfn_saveDf(df_seq2, "step3 seq2 aggregated", True)

    ####################################################################################################################
    # STEP4. 컬럼 정렬 후 concat
    ####################################################################################################################
    output_cols = (
            BASE_GROUP_KEY
            + [SEQ1]
            + [problemAnlSummary_DemandQty, problemAnlSummary_ShortQty]
            + reason_cols
    )

    df_out_ProblemAnlSummary = (
        pd.concat(
            [df_seq1.reindex(columns=output_cols),
             df_seq2.reindex(columns=output_cols)],
            ignore_index=True
        )
    )

    vdCommon.gfn_saveDf(df_out_ProblemAnlSummary, "step4 concatenated", True)

    ####################################################################################################################
    # STEP5. Output DataFrame 생성
    ####################################################################################################################
    # Version Column 추가 (필수)
    df_out_ProblemAnlSummary.insert(0, VERSION_NAME, paramOutVersion)
    df_out_ProblemAnlSummary[reason_cols] = df_out_ProblemAnlSummary[reason_cols].fillna("")

    # Output 로깅
    vdCommon.gfn_saveDf(df_out_ProblemAnlSummary, "output", True)
    vdCommon.gfn_pyLog_end()

except Exception as e:
    trace_msg = traceback.format_exc()
    logger.Error(p_note=f'=====> try Exception : {trace_msg}', p_log_level=common.G_log_level.info())
    logger.Error()
    raise
