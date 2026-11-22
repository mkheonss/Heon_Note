from o9_common_utils.O9DataLake import O9DataLake
import logging

logger = logging.getLogger("o9_logger")
import pandas as pd
import numpy as np
import time
from tabulate import tabulate

pd.options.display.max_rows = 25
pd.options.display.max_columns = 50
pd.options.display.max_colwidth = 100

############### Input Table ###############
# in_SolverStartBucket: SELECT (&SolverStartBucket);
# in_SolverEndBucket  : SELECT (&SolverEndBucket);
# in_BODItemMaterial  : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Sub Location].[Sub Location] * [Item Material].[Item Material] * [Trans Mode].[Trans Mode]) on row,  ({Measure.[BOD Item Mtrl_EFF Startdate], Measure.[BOD Item Mtrl_EFF Enddate], Measure.[BOD Item Mtrl_Time Varying Flag], Measure.[BOD Item Mtrl_Created Time]}) on column.filter(Measure.[SOP Updated Time] < Measure.[BOD Item Mtrl_Updated Time]);
# in_BODItemMaterialW : Select ([Version].[Version Name].[CWV_MP] * [Location].[Location] * [Sub Location].[Sub Location] * [Item Material].[Item Material] * [Trans Mode].[Trans Mode] * [Time].[Week]) on row,  ({Measure.[BOD Item Mtrl W_Total LT]}) on column.filter(Measure.[SOP Updated Time] < Measure.[BOD Item Mtrl_Updated Time]) orderby Time.Week.Name;

# 2026.02.25 추가
# in_CurrentWeek      : SELECT (&CurrentWeek);
# df_in_ItemMaterial  : Select ([Item Material].[Item Material] * [Item Material].[MSL5] * [Item Material].[MSL3]);
# df_in_SupplyFrozen1 : Select ([Location].[Location] * [Trans Mode].[Trans Mode]) on row, ({Measure.[Supply Frozen Mtrl Sub_Frozen]}) on column where {[Version].[Version Name]};
# df_in_SupplyFrozen2 : Select ([Location].[Location] * &CurrentWeek * [Item Material].[Item Material]) on row, ({Measure.[Supply Frozen Mtrl Item W_Fix Range], Measure.[Supply Frozen Mtrl Item W_IsRelativeWeek]}) on column where {[Version].[Version Name]};
# df_in_SupplyFrozen3 : Select (&CurrentWeek * [Item Material].[MSL5]) on row, ({Measure.[Supply Frozen Mtrl L5 W_Fix Range], Measure.[Supply Frozen Mtrl L5 W_IsRelativeWeek]}) on column where {[Version].[Version Name]};
# df_in_SupplyFrozen4 : Select (&CurrentWeek * [Item Material].[MSL3]) on row, ({Measure.[Supply Frozen Mtrl L3 W_Fix Range], Measure.[Supply Frozen Mtrl L3 W_IsRelativeWeek]}) on column where {[Version].[Version Name]};


############### Exec ###############
# exec plugin instance [PY_UI_SOPAdjust_UpdateMtrlBOD] for measures {[W Activity Priority]} using scope ([Version].[Version Name].[CWV_MP] * &PlanningHorizon ) using arguments {("IgnoreMissingOutputs", true), ("IncludeNullRows", "False"), (ExecutionMode, "Mediumweight"), (MaxConcurrency, 1), (MaxSliceTableCells, 90000000)};

initTime = time.time()
logger.debug(f"START({initTime})")
logger.warn("@@@@@@@@@@@@@@@ PY_UI_SOPAdjust_UpdateMtrlBOD Started @@@@@@@@@@@@@@@")

in_SolverStartBucket = O9DataLake.get("in_SolverStartBucket")
in_SolverEndBucket = O9DataLake.get("in_SolverEndBucket")
in_BODItemMaterial = O9DataLake.get("in_BODItemMaterial")
in_BODItemMaterialW = O9DataLake.get("in_BODItemMaterialW")

# =============== 2026.02.25 추가 : add by (KTW) ==================
in_CurrentWeek = O9DataLake.get("in_CurrentWeek")
df_in_ItemMaterial = O9DataLake.get("df_in_ItemMaterial")
df_in_SupplyFrozen1 = O9DataLake.get("df_in_SupplyFrozen1")
df_in_SupplyFrozen2 = O9DataLake.get("df_in_SupplyFrozen2")
df_in_SupplyFrozen3 = O9DataLake.get("df_in_SupplyFrozen3")
df_in_SupplyFrozen4 = O9DataLake.get("df_in_SupplyFrozen4")
# ================================================================

logger.warn("in_SolverStartBucket : {}".format(in_SolverStartBucket.head()))
logger.warn("in_SolverEndBucket : {}".format(in_SolverEndBucket.head()))
logger.warn("in_BODItemMaterial: {}".format(in_BODItemMaterial.head()))
logger.warn("in_BODItemMaterialW : {}".format(in_BODItemMaterialW.head()))


############### Start ###############

out_ActivityParameters = pd.DataFrame()
out_ActivityTimeVaryingParameters = pd.DataFrame()
out_Consumption = pd.DataFrame()
out_Production = pd.DataFrame()

# in_SolverStartBucket ["Time.[Week]"] = pd.to_datetime(
# in_SolverStartBucket ["Time.[Week]"].apply(lambda x: str(x) + "-0"),
#    format="%Y%W-%w",
# )

######  TimeVarying  #####
in_BODItemMaterialW.rename(
    columns={
        "Item Material.[Item Material]": "Activity3.[Activity3]",
        "Trans Mode.[Trans Mode]": "Activity2.[Activity2]",
        "BOD Item Mtrl W_Total LT": "W Activity Lead Time Time Varying",
    },
    inplace=True,
)

in_BODItemMaterialW["Activity1.[Activity1]"] = (
    in_BODItemMaterialW["Location.[Location]"]
    + "_"
    + in_BODItemMaterialW["Sub Location.[Sub Location]"]
    + "_"
    + in_BODItemMaterialW["Activity2.[Activity2]"]
)

in_BODItemMaterialW = in_BODItemMaterialW.drop(
    columns=["Location.[Location]", "Sub Location.[Sub Location]"]
)

in_BODItemMaterialW["W Activity Lead Time Time Varying"] = (
    in_BODItemMaterialW["W Activity Lead Time Time Varying"] / 7
)

in_BODItemMaterialW["W Activity Lead Time Time Varying"].fillna(0, inplace=True)

logger.warn("in_BODItemMaterialW: {}".format(in_BODItemMaterialW.head()))

#####  BODItemMaterial  #####
in_BODItemMaterial.rename(
    columns={
        "Item Material.[Item Material]": "Activity3.[Activity3]",
        "Trans Mode.[Trans Mode]": "Activity2.[Activity2]",
        "BOD Item Mtrl_EFF Startdate": "W Activity Start Date",
        "BOD Item Mtrl_EFF Enddate": "W Activity End Date",
    },
    inplace=True,
)

in_BODItemMaterial["Activity1.[Activity1]"] = (
    in_BODItemMaterial["Location.[Location]"]
    + "_"
    + in_BODItemMaterial["Sub Location.[Sub Location]"]
    + "_"
    + in_BODItemMaterial["Activity2.[Activity2]"]
)

logger.warn("in_BODItemMaterial1: {}".format(in_BODItemMaterial.head()))



# ====================== 2026.02.23 추가 add by (KTW) : W_FROZEN_WINDOW_COLUMN 우선순위 설정 ======================
# 0. df_in_SupplyFrozen 가공.
#   df_in_SupplyFrozen3, df_in_SupplyFrozen4 는 df_in_ItemMaterial merge 하여 "Item Material.[Item Material]" 컬럼 획득
df_in_SupplyFrozen2 = df_in_SupplyFrozen2[[
    "Location.[Location]", "Item Material.[Item Material]", "Supply Frozen Mtrl Item W_Fix Range", "Supply Frozen Mtrl Item W_IsRelativeWeek"
]].drop_duplicates()

df_in_SupplyFrozen3 = pd.merge(df_in_SupplyFrozen3, df_in_ItemMaterial, how="inner", on="Item Material.[MSL5]")
df_in_SupplyFrozen3.drop(columns=["Item Material.[MSL3]"], inplace=True)
df_in_SupplyFrozen3 = df_in_SupplyFrozen3[[
    "Item Material.[Item Material]", "Supply Frozen Mtrl L5 W_Fix Range", "Supply Frozen Mtrl L5 W_IsRelativeWeek"
]].drop_duplicates()

df_in_SupplyFrozen4 = pd.merge(df_in_SupplyFrozen4, df_in_ItemMaterial, how="inner", on="Item Material.[MSL3]")
df_in_SupplyFrozen4.drop(columns=["Item Material.[MSL5]"], inplace=True)
df_in_SupplyFrozen4 = df_in_SupplyFrozen4[[
    "Item Material.[Item Material]", "Supply Frozen Mtrl L3 W_Fix Range", "Supply Frozen Mtrl L3 W_IsRelativeWeek"
]].drop_duplicates()


# 1. [1순위] df_in_SupplyFrozen1 merge
df_SupplyFrozen1 = df_in_SupplyFrozen1[df_in_SupplyFrozen1["Trans Mode.[Trans Mode]"] == 'All'].copy()
df_SupplyFrozen2 = df_in_SupplyFrozen1[df_in_SupplyFrozen1["Trans Mode.[Trans Mode]"] != 'All'].copy()

#   Trans Mode.[Trans Mode] == All 인것만
in_BODItemMaterial_1 = in_BODItemMaterial.merge(
    df_SupplyFrozen1, how="inner", on="Location.[Location]"
).drop_duplicates()
in_BODItemMaterial_1.drop(columns=["Trans Mode.[Trans Mode]"], inplace=True)

#   Trans Mode.[Trans Mode] != All 인것만
in_BODItemMaterial_2 = in_BODItemMaterial.merge(
    df_SupplyFrozen2, how="inner",
    left_on=["Location.[Location]", "Activity2.[Activity2]"],
    right_on=["Location.[Location]", "Trans Mode.[Trans Mode]"],
).drop_duplicates()
in_BODItemMaterial_2.drop(columns=["Trans Mode.[Trans Mode]"], inplace=True)

in_BODItemMaterial_3 = pd.concat([in_BODItemMaterial_1, in_BODItemMaterial_2], ignore_index=True).drop_duplicates()

#   원본에 "Supply Frozen Mtrl Sub_Frozen" 추가
in_BODItemMaterial = in_BODItemMaterial.merge(
    in_BODItemMaterial_3, how="left",
    on=["Version.[Version Name]", "Location.[Location]", "Sub Location.[Sub Location]", "Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]"]
).drop_duplicates()

#   원본 컬럼 사용
in_BODItemMaterial.rename(columns={
    "W Activity Start Date" + '_x': "W Activity Start Date",
    "W Activity End Date" + '_x': "W Activity End Date",
    "BOD Item Mtrl_Created Time" + '_x': "BOD Item Mtrl_Created Time",
    "BOD Item Mtrl_Time Varying Flag" + '_x': "BOD Item Mtrl_Time Varying Flag",
}, inplace=True)



# 2. [2순위] df_in_SupplyFrozen2 merge
in_BODItemMaterial = in_BODItemMaterial.merge(
    df_in_SupplyFrozen2, how="left",
    left_on=["Location.[Location]", "Activity3.[Activity3]"],
    right_on=["Location.[Location]", "Item Material.[Item Material]"],
).drop_duplicates()
in_BODItemMaterial.drop(columns=["Item Material.[Item Material]"], inplace=True)


# 3. [3순위] df_in_SupplyFrozen3 merge
in_BODItemMaterial = in_BODItemMaterial.merge(
    df_in_SupplyFrozen3, how="left",
    left_on=["Activity3.[Activity3]"],
    right_on=["Item Material.[Item Material]"],
).drop_duplicates()
in_BODItemMaterial.drop(columns=["Item Material.[Item Material]"], inplace=True)


# 4. [4순위] df_in_SupplyFrozen4 merge
in_BODItemMaterial = in_BODItemMaterial.merge(
    df_in_SupplyFrozen4, how="left",
    left_on=["Activity3.[Activity3]"],
    right_on=["Item Material.[Item Material]"],
).drop_duplicates()
in_BODItemMaterial.drop(columns=["Item Material.[Item Material]"], inplace=True)


# 5. 절대주차 -> 상대주차로 변환
#   만약 당주 = 202609주차이고, 절대주차 = 202613 인 경우는, = (절대주차값 - 당주 + 1) = 5 로 반영.
#   만약 절대주차가 202601와 같이 당주보다 이전이라면 그냥 0으로 반영
val_cols = ["Supply Frozen Mtrl Item W_Fix Range", "Supply Frozen Mtrl L5 W_Fix Range", "Supply Frozen Mtrl L3 W_Fix Range"]
cond_cols = ["Supply Frozen Mtrl Item W_IsRelativeWeek", "Supply Frozen Mtrl L5 W_IsRelativeWeek", "Supply Frozen Mtrl L3 W_IsRelativeWeek"]

#   한 번에 모든 컬럼을 NumPy 배열로 변환
val_matrix = in_BODItemMaterial[val_cols].to_numpy(dtype=np.float64)
cond_matrix = in_BODItemMaterial[cond_cols].to_numpy()

#   조건 정의
current_week = int(in_CurrentWeek["Time.[Week]"].values[0])
is_false = cond_matrix == False
is_less = val_matrix < current_week

#   조건별 결과 (우선순위: 위에서 아래)
conditions = [
    is_false & is_less,    # 1순위: False이면서 val < w → 0
    is_false               # 2순위: False → 계산
]
choices = [
    0,
    val_matrix - current_week + 1
]

result = np.select(conditions, choices, default=val_matrix)

#   결과 반영
in_BODItemMaterial[val_cols] = result


# 6. 'W Frozen Window' 컬럼 설정. 2순위 부턴 tpmode_modes 인것만.
#   조건 정의 (순서대로 체크)
tpmode_modes = ['VESSEL', 'TRUCK', 'TRAIN']

# tpmode_modes 조건
tpmode_conditions = in_BODItemMaterial["Activity2.[Activity2]"].isin(tpmode_modes)

conditions = [
    # 1번째 조건: tpmode_modes 조건 없음
    in_BODItemMaterial["Supply Frozen Mtrl Sub_Frozen"].notna() & 
    (in_BODItemMaterial["Supply Frozen Mtrl Sub_Frozen"] != ''),
    
    # 2번째 조건부터: tpmode_modes 조건 추가
    tpmode_conditions &
    in_BODItemMaterial["Supply Frozen Mtrl Item W_Fix Range"].notna() & 
    (in_BODItemMaterial["Supply Frozen Mtrl Item W_Fix Range"] != ''),
    
    tpmode_conditions &
    in_BODItemMaterial["Supply Frozen Mtrl L5 W_Fix Range"].notna() & 
    (in_BODItemMaterial["Supply Frozen Mtrl L5 W_Fix Range"] != ''),
    
    tpmode_conditions &
    in_BODItemMaterial["Supply Frozen Mtrl L3 W_Fix Range"].notna() & 
    (in_BODItemMaterial["Supply Frozen Mtrl L3 W_Fix Range"] != '')
]

#   각 조건에 해당하는 값
choices = [
    in_BODItemMaterial["Supply Frozen Mtrl Sub_Frozen"],
    in_BODItemMaterial["Supply Frozen Mtrl Item W_Fix Range"],
    in_BODItemMaterial["Supply Frozen Mtrl L5 W_Fix Range"],
    in_BODItemMaterial["Supply Frozen Mtrl L3 W_Fix Range"]
]

#   Frozen Window 컬럼생성
in_BODItemMaterial["W Frozen Window"] = np.select(conditions, choices, default=34)
in_BODItemMaterial["W Frozen Window Org"] = in_BODItemMaterial["W Frozen Window"]
# ==============================================================================================================


# Frozen Window는 기존/신규 전부 34  : 2026.02.26 주석처리 (KTW)
# in_BODItemMaterial["W Frozen Window"] = 34
# in_BODItemMaterial["W Frozen Window Org"] = in_BODItemMaterial["W Frozen Window"]


# Lead Time은 Flag가 N일 경우 가장 빠른 주차 TimeVarying LT
in_BODItemMaterialW["Time.[Week]"] = pd.to_numeric(
    in_BODItemMaterialW["Time.[Week]"], errors="coerce"
)

min_date_data = in_BODItemMaterialW.loc[
    in_BODItemMaterialW.groupby(
        ["Activity3.[Activity3]", "Activity2.[Activity2]", "Activity1.[Activity1]"]
    )["Time.[Week]"].idxmin()
][
    [
        "Activity3.[Activity3]",
        "Activity2.[Activity2]",
        "Activity1.[Activity1]",
        "W Activity Lead Time Time Varying",
    ]
]

logger.warn("min_date_data: {}".format(min_date_data.head()))
in_BODItemMaterial = in_BODItemMaterial.merge(
    min_date_data,
    on=["Activity3.[Activity3]", "Activity2.[Activity2]", "Activity1.[Activity1]"],
    how="left",
)
logger.warn("in_BODItemMaterial2: {}".format(in_BODItemMaterial.head()))
in_BODItemMaterial.rename(
    columns={
        "W Activity Lead Time Time Varying": "W Activity Lead Time",
    },
    inplace=True,
)
in_BODItemMaterial["W Activity Lead Time"].fillna(0, inplace=True)

# TimeVarying LeadTime YN
TimeVaryingFlag = in_BODItemMaterial[
    in_BODItemMaterial["BOD Item Mtrl_Time Varying Flag"].isna()
    | (in_BODItemMaterial["BOD Item Mtrl_Time Varying Flag"] == "N")
][
    [
        "Activity3.[Activity3]",
        "Activity2.[Activity2]",
        "Activity1.[Activity1]",
        "W Activity Lead Time",
    ]
]

logger.warn("TimeVaryingFlag: {}".format(TimeVaryingFlag.head()))
in_BODItemMaterialW = in_BODItemMaterialW.merge(
    TimeVaryingFlag,
    on=["Activity3.[Activity3]", "Activity2.[Activity2]", "Activity1.[Activity1]"],
    how="left",
)

mask = in_BODItemMaterialW["W Activity Lead Time"].notna()
in_BODItemMaterialW.loc[mask, "W Activity Lead Time Time Varying"] = (
    in_BODItemMaterialW.loc[mask, "W Activity Lead Time"]
)

in_BODItemMaterialW = in_BODItemMaterialW.drop(columns="W Activity Lead Time")
logger.warn("in_BODItemMaterialW: {}".format(in_BODItemMaterialW.head()))
# None TimeVarying

out_ActivityParameters = in_BODItemMaterial[
    in_BODItemMaterial["BOD Item Mtrl_Created Time"].isna()
][
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "W Activity Start Date",
        "W Activity End Date",
        "W Frozen Window",
        "W Activity Lead Time",
    ]
]

newBOD = in_BODItemMaterial[in_BODItemMaterial["BOD Item Mtrl_Created Time"].notna()][
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Location.[Location]",
        "Sub Location.[Sub Location]",
        "W Activity Start Date",
        "W Activity End Date",
        "W Frozen Window",
        "W Activity Lead Time",
    ]
]

if not newBOD.empty:
    createNewBOM = newBOD.copy()
    createNewBOM["W Frozen Window"].fillna(34, inplace=True)
    createNewBOM["W Material Consumption Association"] = 1
    createNewBOM["W Material Consumption Quantity Per"] = 1
    createNewBOM["W Material Production Association"] = 1
    createNewBOM["W Material Production Quantity Per"] = 1
    createNewBOM["W Activity Priority"] = 99
    createNewBOM["W Activity Lead Time"].fillna(0, inplace=True)
    createNewBOM["Item.[Item]"] = createNewBOM["Activity3.[Activity3]"]

    createNewActivityParameters = createNewBOM[
        [
            "Version.[Version Name]",
            "Activity1.[Activity1]",
            "Activity2.[Activity2]",
            "Activity3.[Activity3]",
            "W Activity Start Date",
            "W Activity End Date",
            "W Frozen Window",
            "W Activity Lead Time",
        ]
    ]

    createNewConsumption = createNewBOM[
        [
            "Version.[Version Name]",
            "Activity1.[Activity1]",
            "Activity2.[Activity2]",
            "Activity3.[Activity3]",
            "Location.[Location]",
            "Item.[Item]",
            "W Material Consumption Association",
            "W Material Consumption Quantity Per",
        ]
    ]

    createNewProduction = createNewBOM[
        [
            "Version.[Version Name]",
            "Activity1.[Activity1]",
            "Activity2.[Activity2]",
            "Activity3.[Activity3]",
            "Sub Location.[Sub Location]",
            "Item.[Item]",
            "W Material Production Association",
            "W Material Production Quantity Per",
            "W Activity Priority",
        ]
    ]

    createNewProduction.rename(
        columns={
            "Sub Location.[Sub Location]": "Location.[Location]",
        },
        inplace=True,
    )

    out_ActivityParameters = pd.concat(
        [out_ActivityParameters, createNewActivityParameters], ignore_index=True
    )

    out_Consumption = createNewConsumption
    out_Production = createNewProduction
else:
    out_Consumption = pd.DataFrame(
        columns=[
            "Version.[Version Name]",
            "Activity1.[Activity1]",
            "Activity2.[Activity2]",
            "Activity3.[Activity3]",
            "Location.[Location]",
            "Item.[Item]",
            "W Material Consumption Association",
            "W Material Consumption Quantity Per",
        ]
    )

    out_Production = pd.DataFrame(
        columns=[
            "Version.[Version Name]",
            "Activity1.[Activity1]",
            "Activity2.[Activity2]",
            "Activity3.[Activity3]",
            "Location.[Location]",
            "Item.[Item]",
            "W Material Production Association",
            "W Material Production Quantity Per",
            "W Activity Priority",
        ]
    )

# createNewActivityTimeVaryingParameters = in_BODItemMaterialW.merge(
#     createNewBOM[
#         [
#             "Activity1.[Activity1]",
#             "Activity2.[Activity2]",
#             "Activity3.[Activity3]",
#         ]
#     ].drop_duplicates(),
#     on=[
#         "Activity1.[Activity1]",
#         "Activity2.[Activity2]",
#         "Activity3.[Activity3]",
#     ],
#     how="inner",
# )

out_ActivityTimeVaryingParameters = in_BODItemMaterialW[
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Time.[Week]",
        "W Activity Lead Time Time Varying",
    ]
]

logger.warning(len(out_Consumption.index))
logger.warn("out_Consumption: {}".format(out_Consumption.head()))
logger.warning(len(out_Production.index))
logger.warn("out_Production: {}".format(out_Production.head()))
logger.warning(len(out_ActivityParameters.index))
logger.warn("out_ActivityParameters: {}".format(out_ActivityParameters.head()))
logger.warning(len(out_ActivityTimeVaryingParameters.index))
logger.warn(
    "out_ActivityTimeVaryingParameters: {}".format(
        out_ActivityTimeVaryingParameters.head()
    )
)
O9DataLake.put("out_ActivityParameters", out_ActivityParameters)
O9DataLake.put("out_ActivityTimeVaryingParameters", out_ActivityTimeVaryingParameters)
O9DataLake.put("out_Consumption", out_Consumption)
O9DataLake.put("out_Production", out_Production)

endTime = time.time()
logger.debug(f"PY_UI_SOPAdjust_UpdateMtrlBOD END({endTime}): {endTime - initTime} secs")
