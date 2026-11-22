"""

o9Input_raw : Select ([Version].[Version Name] * [Group].[Group ID] * [Sequence].[Sequence] * [Biz Obj].[Area] * [Biz Obj].[Scope DisplayName] * [Biz Obj].[Biz Req] * [Biz Obj].[Scope]) on row,  ({Measure.[Biz Obj Base_Period], Measure.[Biz Obj Base_Priority Short], Measure.[Biz Obj Base_Priority Mid], Measure.[Biz Obj Base_Priority Long], Measure.[Biz Obj Base_Asn]}) on column;

o9Input
temp4

EXEC plugin instance [PY_UI_BizObjApply]
for measures {[Biz Obj Base_Period]}
using scope ( &CWVUI )
using arguments {(Version, "CWV_MP"), (Strategy, "Regular Plan"), (ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};



"""



import numpy as np
import pandas as pd
import os
import traceback
import warnings
from datetime import datetime, timedelta
from NSCMCommon import NSCMCommon as common
from NSCMCommon import VDCommon as vdCommon

########################################################################################################################
# Local 개발 시에 필요한 공통 변수 선언
########################################################################################################################
# o9에 저장된 instanceName
str_instance = 'PY_UI_BizObjApply'
is_local = common.gfn_get_isLocal()

########################################################################################################################
# log 설정 : PROGRAM file_name
########################################################################################################################
logger = common.G_Logger(p_py_name=str_instance)
common.gfn_set_local_logfile()

logger.Start()

########################################################################################################################
# 함수 정의
########################################################################################################################


########################################################################################################################
# Main Logic
########################################################################################################################
try:
    # Batch 시작
    vdCommon.gfn_pyLog_start("CWV_MP", str_instance, logger, common.gfn_get_isLocal(), (os.path.dirname(__file__) if common.gfn_get_isLocal() else ""))

    vdCommon.gfn_stepLog("plugin Execution Start ")
    vdCommon.gfn_stepLog(common.G_SourceVersion)
    vdCommon.gfn_stepLog(vdCommon.G_VD_SourceVersion)

    pd.set_option('mode.chained_assignment',  None) # <==== 경고를 끈다
    warnings.simplefilter(action='ignore', category=FutureWarning)

    if is_local:
        o9Input_raw = pd.read_csv(os.path.dirname(__file__) + "\\" + f"in_df_o9Input_raw.csv", encoding="UTF-8")

        Version = "CWV_MP"
        Strategy = "Regular Plan"

    # input 출력
    vdCommon.gfn_saveDf(o9Input_raw, "o9Input_raw", True)

    # Parameter Input
    TotalShort = 8
    TotalMid = 8
    TotalLong = 18

    o9Input = pd.DataFrame(
        columns=['Version.[Version Name]', 'Sequence.[Sequence]', 'Biz Obj.[Scope]', 'Group.[Group ID]',
                 'Biz Obj Base_Period'])
    temp4 = pd.DataFrame(
        columns=['Version.[Version Name]', 'Sequence.[Sequence]', 'Biz Obj.[Scope DisplayName]', 'Group.[Group ID]',
                 'Time Biz Obj.[Day]', 'Biz Obj Sum_End Date'])

    # 1. Data Preprocessing
    if o9Input_raw.empty:
        o9Input = pd.DataFrame(
            columns=['Version.[Version Name]', 'Sequence.[Sequence]', 'Biz Obj.[Scope]', 'Group.[Group ID]',
                     'Biz Obj Base_Period'])
        temp4 = pd.DataFrame(
            columns=['Version.[Version Name]', 'Sequence.[Sequence]', 'Biz Obj.[Scope DisplayName]', 'Group.[Group ID]',
                     'Time Biz Obj.[Day]', 'Biz Obj Sum_End Date'])
    else:
        # reorder index by Biz Obj Base_Priority Short
        o9Input = o9Input_raw[o9Input_raw['Biz Obj Base_Asn'] == 1]
        o9Input = o9Input.sort_values(by=['Biz Obj Base_Priority Short', 'Sequence.[Sequence]']).reset_index(drop=True)
        o9Input['Sequence.[Sequence]'] = range(1, len(o9Input) + 1)

        # priority 다시 채번
        priorities = pd.concat([
            o9Input['Biz Obj Base_Priority Short'],
            o9Input['Biz Obj Base_Priority Mid'],
            o9Input['Biz Obj Base_Priority Long']
        ], ignore_index=True)

        ranked_priorities = priorities.dropna().rank(method='dense').astype(int)
        priorities.loc[~priorities.isna()] = ranked_priorities

        o9Input['Biz Obj Base_Priority Short'] = priorities.iloc[:len(o9Input)].values
        o9Input['Biz Obj Base_Priority Mid'] = priorities.iloc[len(o9Input):2 * len(o9Input)].values
        o9Input['Biz Obj Base_Priority Long'] = priorities.iloc[2 * len(o9Input):].values

        # Association Measure Update
        o9Input_raw['Biz Obj Base_Asn'] = 0

        grain = list(o9Input_raw.columns.drop([
            'Biz Obj Base_Period', 'Biz Obj Base_Priority Short',
            'Biz Obj Base_Priority Mid', 'Biz Obj Base_Priority Long',
            'Biz Obj Base_Asn'
        ]))
        o9Input_raw[grain] = o9Input_raw[grain].astype(str)
        o9Input[grain] = o9Input[grain].astype(str)

        merged = pd.merge(o9Input_raw, o9Input, on=grain, how='inner')
        no_asn = o9Input_raw[~o9Input_raw[grain].isin(merged[grain]).all(axis=1)]

        o9Input = pd.concat([no_asn, o9Input]).reset_index(drop=True)
        o9Input['Sequence.[Sequence]'] = o9Input['Sequence.[Sequence]'].astype(int)

        temp1 = o9Input[o9Input['Biz Obj Base_Asn'] == 1].copy()

        temp1['Biz Obj Base_Priority Short'] = pd.to_numeric(temp1['Biz Obj Base_Priority Short'],
                                                             errors='coerce').fillna(
            0).astype(int)
        temp1['Biz Obj Base_Priority Mid'] = pd.to_numeric(temp1['Biz Obj Base_Priority Mid'], errors='coerce').fillna(
            0).astype(int)
        temp1['Biz Obj Base_Priority Long'] = pd.to_numeric(temp1['Biz Obj Base_Priority Long'],
                                                            errors='coerce').fillna(
            0).astype(int)

        temp1 = temp1.drop(['Version.[Version Name]', 'Biz Obj.[Biz Req]', 'Biz Obj.[Scope]'], axis=1)
        temp1 = temp1[temp1['Biz Obj.[Scope DisplayName]'] != '-']


        # Null인 period, priority 처리 함수
        def min_ignore_zero(x):
            filtered = x[x != 0]
            return filtered.min() if not filtered.empty else 0


        def max_ignore_zero(x):
            filtered = x[x != 0]
            return filtered.max() if not filtered.empty else 0


        # Drop specified columns
        temp1 = temp1.groupby(['Biz Obj.[Area]', 'Biz Obj.[Scope DisplayName]']).agg({
            'Sequence.[Sequence]': 'min',
            'Biz Obj Base_Period': max_ignore_zero,
            'Biz Obj Base_Priority Short': min_ignore_zero,
            'Biz Obj Base_Priority Mid': min_ignore_zero,
            'Biz Obj Base_Priority Long': min_ignore_zero
        }).reset_index().sort_values(by='Sequence.[Sequence]').reset_index(drop=True)

        # 2. Calculation (1) flag
        temp1['short_temp'] = temp1.apply(
            lambda row: f"{row['Biz Obj.[Scope DisplayName]']}_{int(row['Biz Obj Base_Priority Short'])}", axis=1)
        temp1['mid_temp'] = temp1.apply(
            lambda row: f"{row['Biz Obj.[Scope DisplayName]']}_{int(row['Biz Obj Base_Priority Mid'])}", axis=1)
        temp1['long_temp'] = temp1.apply(
            lambda row: f"{row['Biz Obj.[Scope DisplayName]']}_{int(row['Biz Obj Base_Priority Long'])}", axis=1)

        temp_dict = pd.concat([
            temp1[['short_temp', 'Sequence.[Sequence]', 'Biz Obj.[Area]', 'Biz Obj.[Scope DisplayName]',
                   'Biz Obj Base_Period']].assign(flag_s=1, flag_m=0, flag_l=0).rename(columns={'short_temp': 'Scope'}),
            temp1[['mid_temp', 'Sequence.[Sequence]', 'Biz Obj.[Area]', 'Biz Obj.[Scope DisplayName]',
                   'Biz Obj Base_Period']].assign(flag_s=0, flag_m=1, flag_l=0).rename(columns={'mid_temp': 'Scope'}),
            temp1[['long_temp', 'Sequence.[Sequence]', 'Biz Obj.[Area]', 'Biz Obj.[Scope DisplayName]',
                   'Biz Obj Base_Period']].assign(flag_s=0, flag_m=0, flag_l=1).rename(columns={'long_temp': 'Scope'})
        ], ignore_index=True)

        temp2 = temp_dict.groupby(['Scope', 'Sequence.[Sequence]', 'Biz Obj.[Area]', 'Biz Obj.[Scope DisplayName]',
                                   'Biz Obj Base_Period']).sum().reset_index()

        temp2['Priority'] = temp2['Scope'].apply(lambda x: int(x.split('_')[-1]))
        temp2 = temp2[temp2['Priority'] != 0].drop(columns=['Scope', 'Biz Obj Base_Period'])


        # (3) 각 scope_base에 대해 period_s, period_m, period_l 할당
        def assign_periods(df, temp1):
            Periods_dic = temp1.set_index('Biz Obj.[Scope DisplayName]')['Biz Obj Base_Period'].to_dict()

            def calculate_periods(row):
                nonlocal Periods_dic
                scope_name = row['Biz Obj.[Scope DisplayName]']
                PeriodLeft = Periods_dic.get(scope_name, 0)
                periods = {
                    'period_s': 0,
                    'period_m': 0,
                    'period_l': 0
                }

                if row['flag_s'] == 1 and PeriodLeft > 0:
                    periods['period_s'] = min(PeriodLeft, TotalShort)
                    PeriodLeft -= periods['period_s']
                if row['flag_m'] == 1 and PeriodLeft > 0:
                    periods['period_m'] = min(PeriodLeft, TotalMid)
                    PeriodLeft -= periods['period_m']
                if row['flag_l'] == 1 and PeriodLeft > 0:
                    periods['period_l'] = min(PeriodLeft, TotalLong)
                    PeriodLeft -= periods['period_l']

                Periods_dic[scope_name] = PeriodLeft  # Period 저장된 딕셔너리에 잔여 Period 업데이트

                return pd.Series(periods)

            periods_df = df.apply(calculate_periods, axis=1)
            df = pd.concat([df, periods_df], axis=1)
            return df


        temp3 = assign_periods(temp2, temp1).sort_values(by=['Priority', 'Sequence.[Sequence]']).reset_index(drop=True)

        # 4. Calculation (3) start/end date
        base_dates = {
            'period_s': datetime(2024, 1, 1),
            'period_m': datetime(2024, 1, 9),
            'period_l': datetime(2024, 1, 17)
        }


        def calculate_dates(row, base_dates):
            periods = []
            for period_type in ['period_s', 'period_m', 'period_l']:
                if row[period_type] > 0:
                    start = base_dates[period_type]
                    end = start + timedelta(days=row[period_type])
                    periods.append((start, end))
            return periods


        new_rows = []

        # 각 행에 대해 start와 end 날짜 계산
        for index, row in temp3.iterrows():
            periods = calculate_dates(row, base_dates)

            if periods:
                periods.sort()
                merged_periods = [periods[0]]

                # 연속되는 기간 한 행으로 합치기
                for current_start, current_end in periods[1:]:
                    last_start, last_end = merged_periods[-1]
                    if current_start <= last_end:
                        merged_periods[-1] = (last_start, max(last_end, current_end))
                    else:
                        merged_periods.append((current_start, current_end))

                # 같은 scope에 2개의 구간이 존재할 경우 행 분리
                for start, end in merged_periods:
                    scope = row['Biz Obj.[Scope DisplayName]']
                    new_rows.append({
                        'Priority': row['Priority'],
                        'Biz Obj.[Scope DisplayName]': scope,
                        'Time Biz Obj.[Day]': start,
                        'Biz Obj Sum_End Date': end,
                        'Biz Obj Sum_Description': scope
                    })

        temp4 = pd.DataFrame(new_rows).reset_index()

        # 'Sequence.[Sequence]' 재할당
        idx = 0
        prev_priority = 0
        prev_scope = None
        prev_end_date = None

        for i in range(len(temp4)):
            if temp4.at[i, 'Priority'] != prev_priority or temp4.at[i, 'Biz Obj.[Scope DisplayName]'] != prev_scope or (
                    prev_end_date is not None and temp4.at[i, 'Time Biz Obj.[Day]'] < prev_end_date):
                prev_scope = temp4.at[i, 'Biz Obj.[Scope DisplayName]']
                prev_priority = temp4.at[i, 'Priority']
                idx += 1
            temp4.at[i, 'Sequence.[Sequence]'] = idx
            prev_end_date = temp4.at[i, 'Biz Obj Sum_End Date']

        temp4['Sequence.[Sequence]'] = temp4['Sequence.[Sequence]'].astype(int)
        temp4['Version.[Version Name]'] = str(Version)
        temp4['Group.[Group ID]'] = str(Strategy)
        temp4 = temp4[
            ['Version.[Version Name]', 'Group.[Group ID]', 'Sequence.[Sequence]', 'Biz Obj.[Scope DisplayName]',
             'Time Biz Obj.[Day]', 'Biz Obj Sum_End Date', 'Biz Obj Sum_Description']]

    vdCommon.gfn_stepLog('plugin Execution End')
except Exception as e:
    logger.Note(p_note=traceback.format_exc(), p_log_level=common.G_log_level.info())
    logger.Error()
    vdCommon.gfn_pyLog_error(traceback.format_exc())

    df_out = pd.DataFrame([], columns=[])
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


