from o9_common_utils.O9DataLake import O9DataLake
import logging

logger = logging.getLogger("o9_logger")
import pandas as pd
import numpy as np
import time
from datetime import date, timedelta
from tabulate import tabulate

pd.options.display.max_rows = 25
pd.options.display.max_columns = 50
pd.options.display.max_colwidth = 100

############# Exec ###############
#exec plugin instance [PY_UI_SOPAdjust_CreateSOPWIP] for measures {[W WIP Material Production Quantity]} using scope ([Version].[Version Name].[CWV_MP] * &PlanningHorizon ) using arguments {("IgnoreMissingOutputs", #true), ("IncludeNullRows", "False"), (ExecutionMode, "Mediumweight"), (MaxConcurrency, 1), (MaxSliceTableCells, 90000000)};
initTime = time.time()
logger.debug(f"START({initTime})")
logger.warn(
   "@@@@@@@@@@@@@@@ PY_UI_SOPAdjust_CreateSOPWIP execution Started @@@@@@@@@@@@@@@"
)

SOP_W = O9DataLake.get("SOP_W")
SET_W = O9DataLake.get("SET_W")
ActivityLT = O9DataLake.get("ActivityLT")

logger.warn("SOP_W : {}".format(SOP_W.head()))
logger.warn("SET_W : {}".format(SET_W.head()))
logger.warn("ActivityLT: {}".format(ActivityLT.head()))

#SOP_W = pd.read_csv("C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.SOP_W.csv")
#SET_W = pd.read_csv("C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.SET_W.csv")
#ActivityLT = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.ActivityLeadTime.csv"
#)
#LCM_W = pd.read_csv("C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.LCM_W.csv")

############### Start ###############

# Negative_Prod_Output = pd.DataFrame()
Negative_Cons_Output = pd.DataFrame()
SupplyCode = pd.DataFrame()
Positive_Cons_Output = pd.DataFrame()
TotalDeductQty = pd.DataFrame()

# FillNA
SOP_W["BOM Info.[BOM Version]"].fillna("NA", inplace=True)

SOP_W[
    [
        "SOP W_LCM MFG Qty",
        "SOP W_LCM SOP Qty",
        "SOP W_SET MFG Qty",
        "SOP W_SET SOP Qty",
    ]
] = (
    SOP_W[
        [
            "SOP W_LCM MFG Qty",
            "SOP W_LCM SOP Qty",
            "SOP W_SET MFG Qty",
            "SOP W_SET SOP Qty",
        ]
    ]
    .apply(pd.to_numeric, errors="coerce")
    .fillna(0)
)

SET_W[
    [
        "SOP W_SET SOP Qty",
        "SOP Adjust SET W_SOP Adj Qty",
    ]
] = (
    SET_W[
        [
            "SOP W_SET SOP Qty",
            "SOP Adjust SET W_SOP Adj Qty",
        ]
    ]
    .apply(pd.to_numeric, errors="coerce")
    .fillna(0)
)

SET_W["SOP Adjust SET W_SOP Week"] = SET_W["SOP Adjust SET W_SOP Week"].fillna(
    SET_W["Time.[Week]"]
)

# BOM Version == "NA" then 0 out LCM MFG, LCM SOP, SET MFG.
SOP_W.loc[
    SOP_W["BOM Info.[BOM Version]"] == "NA",
    ["SOP W_LCM MFG Qty", "SOP W_LCM SOP Qty", "SOP W_SET MFG Qty"],
] = 0

# Find SET SOP vs SET MFG
TotalDeductQty = (
    SET_W.assign(
        Total_Deduction_Qty=lambda d: d["SOP W_SET SOP Qty"]
        - d["SOP Adjust SET W_SOP Adj Qty"]
    )
    .groupby(
        [
            "Version.[Version Name]",
            "Item.[Item]",
            "Location.[Location]",
            "To Location.[To Location]",
            "Time.[Week]",
            "Trans Mode.[Trans Mode]",
        ],
        as_index=False,
    )
    .agg(
        {
            "Total_Deduction_Qty": "sum",
            "SOP Adjust SET W_SOP Week": "max",
            "SOP Adjust SET W_Hub Site": "first",
        }
    )
)

logger.warn("TotalDeductQty: {}".format(TotalDeductQty.head()))

TotalDeductQtyPositive = TotalDeductQty[
    TotalDeductQty["Total_Deduction_Qty"] < 0
].reset_index(drop=True)

# if SET SOP > SET MFG

Positive_Cons_Output = (
    TotalDeductQtyPositive[TotalDeductQtyPositive["Total_Deduction_Qty"] < 0]
    .rename(
        columns={
            "Trans Mode.[Trans Mode]": "Activity2.[Activity2]",
            "Time.[Week]": "Time.[Week]_Drop",
            "SOP Adjust SET W_SOP Week": "Time.[Week]",
        }
    )
    .assign(
        **{
            "Activity1.[Activity1]": lambda d: d["Location.[Location]"]
            + "_"
            + d["SOP Adjust SET W_Hub Site"].fillna(d["To Location.[To Location]"])
            + "_"
            + d["Activity2.[Activity2]"],
            "Activity3.[Activity3]": lambda d: d["Item.[Item]"],
            "Documents.[OrderlineID]": lambda d: "SNP_"
            + (d.index + 1).astype(str).str.zfill(10),
            "W WIP Material Consumption Quantity": lambda d: d["Total_Deduction_Qty"]
            * -1,
            "W WIP Material Consumption Quantity Init": lambda d: d[
                "Total_Deduction_Qty"
            ]
            * -1,
            "W WIP Pegging ID": 3,
            "W WIP SOP Adjust SET W_DC Site": lambda d: np.where(
                d["SOP Adjust SET W_Hub Site"].notna(),
                d["To Location.[To Location]"],
                "",
            ),
        },
    )
    .reset_index(drop=True)
).drop(
    columns=[
        "To Location.[To Location]",
        "Total_Deduction_Qty",
        "Time.[Week]_Drop",
        "SOP Adjust SET W_Hub Site",
    ]
)

TotalDeductQty = TotalDeductQty.drop(
    columns=[
        "SOP Adjust SET W_SOP Week",
    ]
)

# if SET SOP < SET MFG then recalculate LCM MFG, LCM SOP, SET MFG, SET SOP
SOP_W_Merge_SET = (
    SOP_W.merge(
        TotalDeductQty,
        on=[
            "Version.[Version Name]",
            "Item.[Item]",
            "Location.[Location]",
            "To Location.[To Location]",
            "Time.[Week]",
            "Trans Mode.[Trans Mode]",
        ],
        how="right",
    )
    .fillna({"Total_Deduction_Qty": 0})
    .assign(
        **{
            "BOM Version Prty W_Prty_coalesce": lambda d: d["BOM Version Prty W_Prty"]
            .fillna(d["BOM Version_Prty"])
            .fillna(99)
        }
    )
)

SOP_W_Merge_SET[
    [
        "SOP W_LCM MFG Qty_new",
        "SOP W_LCM SOP Qty_new",
        "SOP W_SET MFG Qty_new",
        "SOP W_SET SOP Qty_new",
    ]
] = SOP_W_Merge_SET[
    [
        "SOP W_LCM MFG Qty",
        "SOP W_LCM SOP Qty",
        "SOP W_SET MFG Qty",
        "SOP W_SET SOP Qty",
    ]
]


def apply_deduction(group: pd.DataFrame) -> pd.DataFrame:
    total = group["Total_Deduction_Qty"].iloc[0]
    if total <= 0:
        return group
    group = group.sort_values(
        [
            "BOM Version Prty W_Prty_coalesce",
            "SOP W_SET MFG Qty",
            "SOP W_LCM MFG Qty",
        ],
        ascending=[False, True, True],
    ).copy()

    for idx, row in group.iterrows():
        if total <= 0:
            break

        available = row["SOP W_SET SOP Qty_new"]

        if available <= 0:
            continue

        group_deduct = min(total, available)

        group.at[idx, "SOP W_LCM MFG Qty_new"] = max(
            (row["SOP W_LCM MFG Qty_new"] - group_deduct), 0
        )
        group.at[idx, "SOP W_LCM SOP Qty_new"] = max(
            (row["SOP W_LCM SOP Qty_new"] - group_deduct), 0
        )
        group.at[idx, "SOP W_SET MFG Qty_new"] = max(
            (row["SOP W_SET MFG Qty_new"] - group_deduct), 0
        )
        group.at[idx, "SOP W_SET SOP Qty_new"] = max(
            (row["SOP W_SET SOP Qty_new"] - group_deduct), 0
        )

        total -= group_deduct

    return group


SOP_W_Merge_SET[
    [
        "BOM Version Prty W_Prty_coalesce",
        "BOM Version Prty W_Prty",
        "BOM Version_Prty",
    ]
] = (
    SOP_W_Merge_SET[
        [
            "BOM Version Prty W_Prty_coalesce",
            "BOM Version Prty W_Prty",
            "BOM Version_Prty",
        ]
    ]
    .apply(pd.to_numeric, errors="coerce")
    .fillna(99)
)

SOP_W_Merge_SET = SOP_W_Merge_SET.groupby(
    [
        "Version.[Version Name]",
        "Item.[Item]",
        "Location.[Location]",
        "To Location.[To Location]",
        "Time.[Week]",
        "Trans Mode.[Trans Mode]",
    ],
    group_keys=False,
).apply(apply_deduction)

SOP_W_Adjust = SOP_W_Merge_SET.assign(
    **{
        "SOP W_LCM MFG Qty": lambda d: d["SOP W_LCM MFG Qty_new"],
        "SOP W_LCM SOP Qty": lambda d: d["SOP W_LCM SOP Qty_new"],
        "SOP W_SET MFG Qty": lambda d: d["SOP W_SET MFG Qty_new"],
        "SOP W_SET SOP Qty": lambda d: d["SOP W_SET SOP Qty_new"],
    }
).drop(
    columns=[
        "SOP W_LCM MFG Qty_new",
        "SOP W_LCM SOP Qty_new",
        "SOP W_SET MFG Qty_new",
        "SOP W_SET SOP Qty_new",
    ]
)

# Update SOP_W
SOP_W_Output = SOP_W_Adjust[SOP_W_Adjust["Total_Deduction_Qty"] > 0][
    [
        "Version.[Version Name]",
        "Item.[Item]",
        "Location.[Location]",
        "To Location.[To Location]",
        "Time.[Week]",
        "Trans Mode.[Trans Mode]",
        "To Item.[To Item]",
        "To Time.[To Week]",
        "Sub Location.[Sub Location]",
        "Week1.[Week1]",
        "Week2.[Week2]",
        "To Trans Mode.[To Trans Mode]",
        "BOM Info.[BOM Version]",
        "Sequence.[Sequence]",
        "Item Component.[Item Component]",
        "Item Material.[Item Material]",
        "SOP W_LCM MFG Qty",
        "SOP W_LCM SOP Qty",
        "SOP W_SET MFG Qty",
        "SOP W_SET SOP Qty",
    ]
].reset_index(drop=True)

SOP_W_Output["SOP W_LCM SOP Adj Qty"] = SOP_W_Output["SOP W_LCM SOP Qty"]
SOP_W_Output["SOP W_SET SOP Adj Qty"] = SOP_W_Output["SOP W_SET SOP Qty"]

logger.warn("SOP_W_Adjust: {}".format(SOP_W_Adjust.head()))

# Update LCM_W
LCM_W_Output = (
    SOP_W_Adjust[SOP_W_Adjust["Total_Deduction_Qty"] > 0][
        [
            "Version.[Version Name]",
            "Location.[Location]",
            "To Item.[To Item]",
            "Sub Location.[Sub Location]",
            "Item Material.[Item Material]",
            "Item Component.[Item Component]",
            "To Trans Mode.[To Trans Mode]",
            "Week1.[Week1]",
            "SOP W_LCM MFG Qty",
        ]
    ]
    .rename(
        columns={
            "SOP W_LCM MFG Qty": "SOP Adjust LCM W_SOP Adj Qty",
        }
    )
    .reset_index(drop=True)
)

LCM_W_Output["SOP Adjust LCM W_SOP Qty"] = LCM_W_Output["SOP Adjust LCM W_SOP Adj Qty"]
LCM_W_Output["SOP Adjust LCM W_Chg Qty"] = 0
LCM_W_Output["SOP Adjust LCM W_Chg Reason"] = "-"

logger.warn("LCM_W_Output: {}".format(LCM_W_Output.head()))

mask_LCM_MFG = SOP_W_Adjust["SOP W_LCM MFG Qty"] > 0

mask_LCM_SOP = SOP_W_Adjust["SOP W_LCM SOP Qty"] > 0

mask_SET_MFG = SOP_W_Adjust["SOP W_SET MFG Qty"] > 0

# if LCM_MFG > 0
LCM_MFG_Offset = 0
LCM_SOP_Offset = 0
SET_MFG_Offset = len(SOP_W_Adjust[SOP_W_Adjust["SOP W_LCM MFG Qty"] > 0])

LCM_MFG = (
    SOP_W_Adjust[mask_LCM_MFG]
    .reset_index(drop=True)
    .assign(
        **{
            # LCM_MFG
            "Item.[Item]_LCM_MFG": lambda d: d["To Item.[To Item]"],
            "Location.[Location]_LCM_MFG": lambda d: d["Sub Location.[Sub Location]"],
            "Activity1.[Activity1]_LCM_MFG": lambda d: d["To Item.[To Item]"] + "_NA",
            "Activity2.[Activity2]_LCM_MFG": lambda d: "RT_"
            + d["To Item.[To Item]"]
            + "_NA@"
            + d["Sub Location.[Sub Location]"],
            "Activity3.[Activity3]_LCM_MFG": lambda d: d["To Item.[To Item]"],
            "Documents.[OrderlineID]_LCM_MFG": lambda d: "MFG_"
            + (d.index + 1 + LCM_MFG_Offset).astype(str).str.zfill(10),
            "Time.[Week]_LCM_MFG": lambda d: d["Week1.[Week1]"],
            "W WIP Material Production Quantity_LCM_MFG": lambda d: d[
                "SOP W_LCM MFG Qty"
            ],
            "W WIP Material Production Quantity Init_LCM_MFG": lambda d: d[
                "SOP W_LCM MFG Qty"
            ],
            "W WIP Pegging ID_LCM_MFG": 3,
            # LCM_SOP
            "Item.[Item]_LCM_SOP": lambda d: d["To Item.[To Item]"],
            "Location.[Location]_LCM_SOP": lambda d: d["Sub Location.[Sub Location]"],
            "Activity1.[Activity1]_LCM_SOP": lambda d: d["Sub Location.[Sub Location]"]
            + "_"
            + d["Location.[Location]"]
            + "_"
            + d["To Trans Mode.[To Trans Mode]"],
            "Activity2.[Activity2]_LCM_SOP": lambda d: d[
                "To Trans Mode.[To Trans Mode]"
            ],
            "Activity3.[Activity3]_LCM_SOP": lambda d: d["To Item.[To Item]"],
            "Documents.[OrderlineID]_LCM_SOP": lambda d: "SOP_"
            + (d.index + 1 + LCM_SOP_Offset).astype(str).str.zfill(10),
            "Time.[Week]_LCM_SOP": lambda d: d["Week2.[Week2]"],
            "W WIP Material Consumption Quantity_LCM_SOP": lambda d: d[
                "SOP W_LCM SOP Qty"
            ],
            "W WIP Material Consumption Quantity Init_LCM_SOP": lambda d: d[
                "SOP W_LCM SOP Qty"
            ],
            "W WIP Pegging ID_LCM_SOP": 3,
            # SET_MFG
            "Item.[Item]_SET_MFG": lambda d: d["Item.[Item]"],
            "Location.[Location]_SET_MFG": lambda d: d["Location.[Location]"],
            "Activity1.[Activity1]_SET_MFG": lambda d: d["Item.[Item]"]
            + "_"
            + d["BOM Info.[BOM Version]"],
            "Activity2.[Activity2]_SET_MFG": lambda d: "RT_"
            + d["Item.[Item]"]
            + "_"
            + d["BOM Info.[BOM Version]"]
            + "@"
            + d["Location.[Location]"],
            "Activity3.[Activity3]_SET_MFG": lambda d: d["Item.[Item]"],
            "Documents.[OrderlineID]_SET_MFG": lambda d: "MFG_"
            + (d.index + 1 + SET_MFG_Offset).astype(str).str.zfill(10),
            "Time.[Week]_SET_MFG": lambda d: d["Time.[Week]"],
            "W WIP Material Production Quantity_SET_MFG": lambda d: d[
                "SOP W_SET MFG Qty"
            ],
            "W WIP Material Production Quantity Init_SET_MFG": lambda d: d[
                "SOP W_SET MFG Qty"
            ],
            "W WIP Pegging ID_SET_MFG": 3,
        },
    )
    .reset_index(drop=True)
)
logger.warn("LCM_MFG: {}".format(LCM_MFG.head()))

# if LCM_SOP > 0
LCM_SOP_Offset += len(LCM_MFG)
SET_MFG_Offset += len(LCM_MFG)

LCM_SOP = (
    SOP_W_Adjust[(~mask_LCM_MFG) & mask_LCM_SOP]
    .reset_index(drop=True)
    .assign(
        **{
            # LCM_SOP
            "Item.[Item]_LCM_SOP": lambda d: d["To Item.[To Item]"],
            "Location.[Location]_LCM_SOP": lambda d: d["Sub Location.[Sub Location]"],
            "Activity1.[Activity1]_LCM_SOP": lambda d: d["Sub Location.[Sub Location]"]
            + "_"
            + d["Location.[Location]"]
            + "_"
            + d["To Trans Mode.[To Trans Mode]"],
            "Activity2.[Activity2]_LCM_SOP": lambda d: d[
                "To Trans Mode.[To Trans Mode]"
            ],
            "Activity3.[Activity3]_LCM_SOP": lambda d: d["To Item.[To Item]"],
            "Documents.[OrderlineID]_LCM_SOP": lambda d: "SOP_"
            + (d.index + 1 + LCM_SOP_Offset).astype(str).str.zfill(10),
            "Time.[Week]_LCM_SOP": lambda d: d["Week2.[Week2]"],
            "W WIP Material Consumption Quantity_LCM_SOP": lambda d: d[
                "SOP W_LCM SOP Qty"
            ],
            "W WIP Material Consumption Quantity Init_LCM_SOP": lambda d: d[
                "SOP W_LCM SOP Qty"
            ],
            "W WIP Pegging ID_LCM_SOP": 3,
            # SET_MFG
            "Item.[Item]_SET_MFG": lambda d: d["Item.[Item]"],
            "Location.[Location]_SET_MFG": lambda d: d["Location.[Location]"],
            "Activity1.[Activity1]_SET_MFG": lambda d: d["Item.[Item]"]
            + "_"
            + d["BOM Info.[BOM Version]"],
            "Activity2.[Activity2]_SET_MFG": lambda d: "RT_"
            + d["Item.[Item]"]
            + "_"
            + d["BOM Info.[BOM Version]"]
            + "@"
            + d["Location.[Location]"],
            "Documents.[OrderlineID]_SET_MFG": lambda d: "MFG_"
            + (d.index + 1 + SET_MFG_Offset).astype(str).str.zfill(10),
            "Time.[Week]_SET_MFG": lambda d: d["Time.[Week]"],
            "Activity3.[Activity3]_SET_MFG": lambda d: d["Item.[Item]"],
            "W WIP Material Production Quantity_SET_MFG": lambda d: d[
                "SOP W_SET MFG Qty"
            ],
            "W WIP Material Production Quantity Init_SET_MFG": lambda d: d[
                "SOP W_SET MFG Qty"
            ],
            "W WIP Pegging ID_SET_MFG": 3,
        },
    )
    .reset_index(drop=True)
)

logger.warn("LCM_SOP: {}".format(LCM_SOP.head()))

# if SET_MFG > 0
LCM_SOP_Offset += len(LCM_SOP)
SET_MFG_Offset += len(LCM_SOP)

SET_MFG = (
    SOP_W_Adjust[(~mask_LCM_MFG) & (~mask_LCM_SOP) & mask_SET_MFG]
    .reset_index(drop=True)
    .assign(
        **{
            "Item.[Item]_SET_MFG": lambda d: d["Item.[Item]"],
            "Location.[Location]_SET_MFG": lambda d: d["Location.[Location]"],
            "Activity1.[Activity1]_SET_MFG": lambda d: d["Item.[Item]"]
            + "_"
            + d["BOM Info.[BOM Version]"],
            "Activity2.[Activity2]_SET_MFG": lambda d: "RT_"
            + d["Item.[Item]"]
            + "_"
            + d["BOM Info.[BOM Version]"]
            + "@"
            + d["Location.[Location]"],
            "Activity3.[Activity3]_SET_MFG": lambda d: d["Item.[Item]"],
            "Documents.[OrderlineID]_SET_MFG": lambda d: "MFG_"
            + (d.index + 1 + SET_MFG_Offset).astype(str).str.zfill(10),
            "Time.[Week]_SET_MFG": lambda d: d["Time.[Week]"],
            "W WIP Material Production Quantity_SET_MFG": lambda d: d[
                "SOP W_SET MFG Qty"
            ],
            "W WIP Material Production Quantity Init_SET_MFG": lambda d: d[
                "SOP W_SET MFG Qty"
            ],
            "W WIP Pegging ID_SET_MFG": 3,
        },
    )
    .reset_index(drop=True)
)

logger.warn("SET_MFG: {}".format(SET_MFG.head()))

# Supply Code Map
SOP_W_AdjustFinal = pd.concat([LCM_MFG, LCM_SOP, SET_MFG], ignore_index=True)

SupplyCode = pd.DataFrame()

SupplyCode_LCM_MFG = SOP_W_AdjustFinal[
    SOP_W_AdjustFinal["Documents.[OrderlineID]_LCM_MFG"].notna()
].reset_index(drop=True)

SupplyCode_LCM_MFG = (
    SupplyCode_LCM_MFG[
        [
            "Version.[Version Name]",
            "Documents.[OrderlineID]_LCM_MFG",
            "Documents.[OrderlineID]_SET_MFG",
        ]
    ]
    .rename(
        columns={
            "Documents.[OrderlineID]_LCM_MFG": "from.[Documents].[OrderlineID]",
            "Documents.[OrderlineID]_SET_MFG": "to.[Documents].[OrderlineID]",
        }
    )
    .reset_index(drop=True)
)
SupplyCode = pd.concat([SupplyCode, SupplyCode_LCM_MFG])

SupplyCode_LCM_SOP = SOP_W_AdjustFinal[
    SOP_W_AdjustFinal["Documents.[OrderlineID]_LCM_SOP"].notna()
].reset_index(drop=True)

SupplyCode_LCM_SOP = (
    SupplyCode_LCM_SOP[
        [
            "Version.[Version Name]",
            "Documents.[OrderlineID]_LCM_SOP",
            "Documents.[OrderlineID]_SET_MFG",
        ]
    ]
    .rename(
        columns={
            "Documents.[OrderlineID]_LCM_SOP": "from.[Documents].[OrderlineID]",
            "Documents.[OrderlineID]_SET_MFG": "to.[Documents].[OrderlineID]",
        }
    )
    .reset_index(drop=True)
)

SupplyCode = pd.concat([SupplyCode, SupplyCode_LCM_SOP])

SupplyCode_SET_MFG = SOP_W_AdjustFinal[
    SOP_W_AdjustFinal["Documents.[OrderlineID]_SET_MFG"].notna()
].reset_index(drop=True)

SupplyCode_SET_MFG = (
    SupplyCode_SET_MFG[
        [
            "Version.[Version Name]",
            "Documents.[OrderlineID]_SET_MFG",
        ]
    ]
    .rename(
        columns={
            "Documents.[OrderlineID]_SET_MFG": "from.[Documents].[OrderlineID]",
        }
    )
    .reset_index(drop=True)
)
SupplyCode_SET_MFG["to.[Documents].[OrderlineID]"] = SupplyCode_SET_MFG[
    "from.[Documents].[OrderlineID]"
]

SupplyCode = pd.concat(
    [SupplyCode, SupplyCode_SET_MFG],
    ignore_index=True,
)
SupplyCode["001.007W Solver Inputs Supply Code Mapping.[W Lot Supply Code Map]"] = 1

########### if SET SOP =< SET MFG
SET_SOP = SOP_W_AdjustFinal.assign(
    **{
        "Item.[Item]_SET_SOP": lambda d: d["Item.[Item]"],
        "Location.[Location]_SET_SOP": lambda d: d["Location.[Location]"],
        "Activity1.[Activity1]_SET_SOP": lambda d: d["Location.[Location]"]
        + "_"
        + d["SOP Adjust SET W_Hub Site"].fillna(d["To Location.[To Location]"])
        + "_"
        + d["Trans Mode.[Trans Mode]"],
        "Activity2.[Activity2]_SET_SOP": lambda d: d["Trans Mode.[Trans Mode]"],
        "Activity3.[Activity3]_SET_SOP": lambda d: d["Item.[Item]"],
        "Documents.[OrderlineID]_SET_SOP": lambda d: "SOP_"
        + (d.index + 1 + LCM_SOP_Offset).astype(str).str.zfill(10),
        "Time.[Week]_SET_SOP": lambda d: d["To Time.[To Week]"],
        "W WIP Material Consumption Quantity_SET_SOP": lambda d: d["SOP W_SET SOP Qty"],
        "W WIP Material Consumption Quantity Init_SET_SOP": lambda d: d[
            "SOP W_SET SOP Qty"
        ],
        "W WIP Pegging ID_SET_SOP": 3,
        "W WIP SOP Adjust SET W_DC Site": lambda d: np.where(
            d["SOP Adjust SET W_Hub Site"].notna(), d["To Location.[To Location]"], ""
        ),
    },
).reset_index(drop=True)

logger.warn("SET_SOP: {}".format(SET_SOP.head()))

SET_SOP["W WIP Acceptable Lot_SET_SOP"] = SET_SOP[
    "Documents.[OrderlineID]_SET_MFG"
].where(SET_SOP["SOP W_SET MFG Qty"] > 0)

# Concat all Prod/Cons

LCM_MFG_Output = SOP_W_AdjustFinal[
    SOP_W_AdjustFinal["W WIP Material Production Quantity_LCM_MFG"] > 0
][
    ["Version.[Version Name]"]
    + [col for col in SOP_W_AdjustFinal.columns if col.endswith("_LCM_MFG")]
].rename(
    columns={
        col: col.replace("_LCM_MFG", "")
        for col in SOP_W_AdjustFinal.columns
        if col.endswith("_LCM_MFG")
    }
)
logger.warn("LCM_MFG_Output: {}".format(LCM_MFG_Output.head()))

LCM_SOP_Output = SOP_W_AdjustFinal[
    SOP_W_AdjustFinal["W WIP Material Consumption Quantity_LCM_SOP"] > 0
][
    ["Version.[Version Name]"]
    + [col for col in SOP_W_AdjustFinal.columns if col.endswith("_LCM_SOP")]
].rename(
    columns={
        col: col.replace("_LCM_SOP", "")
        for col in SOP_W_AdjustFinal.columns
        if col.endswith("_LCM_SOP")
    }
)
logger.warn("LCM_SOP_Output: {}".format(LCM_SOP_Output.head()))

SET_MFG_Output = SOP_W_AdjustFinal[
    SOP_W_AdjustFinal["W WIP Material Production Quantity_SET_MFG"] > 0
][
    ["Version.[Version Name]"]
    + [col for col in SOP_W_AdjustFinal.columns if col.endswith("_SET_MFG")]
].rename(
    columns={
        col: col.replace("_SET_MFG", "")
        for col in SOP_W_AdjustFinal.columns
        if col.endswith("_SET_MFG")
    }
)
logger.warn("SET_MFG_Output: {}".format(SET_MFG_Output.head()))

SET_SOP_Cons_Output = SET_SOP[
    ["Version.[Version Name]","To Location.[To Location]"]
    + [col for col in SET_SOP.columns if col.endswith("_SET_SOP")]
].rename(
    columns={
        col: col.replace("_SET_SOP", "")
        for col in SET_SOP.columns
        if col.endswith("_SET_SOP")
    }
)
logger.warn("SET_SOP_Cons_Output: {}".format(SET_SOP_Cons_Output.head()))

# Activity Lead Time to Week Calculation
SET_SOP_Prod_Output = (
    SET_SOP_Cons_Output.merge(
        ActivityLT,
        on=[
            "Version.[Version Name]",
            "Activity1.[Activity1]",
            "Activity2.[Activity2]",
            "Activity3.[Activity3]",
        ],
        how="left",
    ).fillna({"W Activity Lead Time": 0})
    #    .assign(**{"Time.[Week]": lambda d: d["Time.[Week]"] + d["W Activity Lead Time"]})
).rename(
    columns={
        "W WIP Material Consumption Quantity": "W WIP Material Production Quantity",
        "W WIP Material Consumption Quantity Init": "W WIP Material Production Quantity Init",
        "Location.[Location]": "Location.[Location]_Drop",
        "To Location.[To Location]": "Location.[Location]",
    }
).drop(
    columns=[
        "Location.[Location]_Drop",
    ]
)

SET_SOP_Prod_Output["Time.[Week]"] = (
    SET_SOP_Prod_Output["Time.[Week]"].astype(float).astype(int).astype(str)
)

SET_SOP_Prod_Output["year"] = SET_SOP_Prod_Output["Time.[Week]"].str[:4].astype(int)
SET_SOP_Prod_Output["week"] = SET_SOP_Prod_Output["Time.[Week]"].str[4:].astype(int)


def iso_week_thursday(y, w):
    return date.fromisocalendar(y, w, 4)


SET_SOP_Prod_Output["thursday"] = SET_SOP_Prod_Output.apply(
    lambda r: iso_week_thursday(r["year"], r["week"]), axis=1
)
SET_SOP_Prod_Output["thursday"] = pd.to_datetime(SET_SOP_Prod_Output["thursday"])

SET_SOP_Prod_Output["thursday_ActivityLeadTime"] = SET_SOP_Prod_Output[
    "thursday"
] + pd.to_timedelta(SET_SOP_Prod_Output["W Activity Lead Time"], unit="W")

newWeek = SET_SOP_Prod_Output["thursday_ActivityLeadTime"].dt.isocalendar()
SET_SOP_Prod_Output["Time.[Week]"] = newWeek["year"].astype(str) + newWeek[
    "week"
].astype(str).str.zfill(2)

SET_SOP_Cons_Output = SET_SOP_Cons_Output.drop(
    columns=[
        "To Location.[To Location]",
    ]
)

SET_SOP_Prod_Output = SET_SOP_Prod_Output.drop(
    columns=[
        "year",
        "week",
        "thursday",
        "thursday_ActivityLeadTime",
        "W Activity Lead Time",
    ]
)

Negative_Prod_Output = pd.concat(
    [LCM_MFG_Output, SET_MFG_Output, SET_SOP_Prod_Output], ignore_index=True
)

Negative_Cons_Output = pd.concat(
    [LCM_SOP_Output, SET_SOP_Cons_Output], ignore_index=True
)

# Negative_Prod_Output.to_csv(
#    r"C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Negative_Prod_Output.csv",
#    index=False,
# )
#
# Negative_Cons_Output.to_csv(
#    r"C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Negative_Cons_Output.csv",
#    index=False,
# )
#
# SupplyCode.to_csv(
#    r"C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\SupplyCode.csv",
#    index=False,
# )
#
# Positive_Cons_Output.to_csv(
#    r"C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Positive_Cons_Output.csv",
#    index=False,
# )

logger.warning(len(Negative_Prod_Output.index))
logger.warn("Negative_Prod_Output: {}".format(Negative_Prod_Output.head()))
logger.warning(len(Negative_Cons_Output.index))
logger.warn("Negative_Cons_Output: {}".format(Negative_Cons_Output.head()))
logger.warning(len(SupplyCode.index))
logger.warn("SupplyCode: {}".format(SupplyCode.head()))
logger.warning(len(Positive_Cons_Output.index))
logger.warn("Positive_Cons_Output: {}".format(Positive_Cons_Output.head()))
logger.warning(len(LCM_W_Output.index))
logger.warn("LCM_W_Output: {}".format(LCM_W_Output.head()))
logger.warning(len(SOP_W_Output.index))
logger.warn("SOP_W_Output: {}".format(SOP_W_Output.head()))
O9DataLake.put("Negative_Prod_Output", Negative_Prod_Output)
O9DataLake.put("Negative_Cons_Output", Negative_Cons_Output)
O9DataLake.put("SupplyCode", SupplyCode)
O9DataLake.put("Positive_Cons_Output", Positive_Cons_Output)
O9DataLake.put("LCM_W_Output", LCM_W_Output)
O9DataLake.put("SOP_W_Output", SOP_W_Output)

endTime = time.time()
logger.debug(f"END({endTime}): {endTime - initTime} secs")
