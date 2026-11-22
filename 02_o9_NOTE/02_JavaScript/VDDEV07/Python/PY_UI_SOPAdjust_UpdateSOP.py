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

########### Exec ###############
# exec plugin instance [PY_UI_SOPAdjust_UpdateSOP] for measures {[SOP W_SET MFG Qty]} using scope ([Version].[Version Name].[CWV_MP] * &PlanningHorizon ) using arguments {("IgnoreMissingOutputs", true), ("IncludeNullRows", "False"), (ExecutionMode, "Mediumweight"), (MaxConcurrency, 1), (MaxSliceTableCells, 90000000)};
initTime = time.time()
logger.debug(f"START({initTime})")
logger.warn(
    "@@@@@@@@@@@@@@@ PY_UI_SOPAdjust_UpdateSOP execution Started @@@@@@@@@@@@@@@"
)
LCM_Reference_Input = O9DataLake.get("LCM_Reference_Input")
LCM_Input = O9DataLake.get("LCM_Input")
SET_Input = O9DataLake.get("SET_Input")
SET_SOPWIP_Input = O9DataLake.get("SET_SOPWIP_Input")
BOM_Version_Input = O9DataLake.get("BOM_Version_Input")
SolverCurrentBucket = O9DataLake.get("SolverCurrentBucket")
OpenCell_Input = O9DataLake.get("OpenCell_Input")
CodeMap_Input = O9DataLake.get("CodeMap_Input")
Sequence_Input = O9DataLake.get("Sequence_Input")
LCM_W_Input = O9DataLake.get("LCM_W_Input")
logger.warn("LCM_Reference_Input: {}".format(LCM_Reference_Input.head()))
logger.warn("LCM_Input : {}".format(LCM_Input.head()))
logger.warn("SET_Input : {}".format(SET_Input.head()))
logger.warn("SET_SOPWIP_Input: {}".format(SET_SOPWIP_Input.head()))
logger.warn("BOM_Version_Input : {}".format(BOM_Version_Input.head()))
logger.warn("SolverCurrentBucket : {}".format(SolverCurrentBucket.head()))
logger.warn("OpenCell_Input : {}".format(OpenCell_Input.head()))
logger.warn("CodeMap_Input : {}".format(CodeMap_Input.head()))
logger.warn("Sequence_Input: {}".format(Sequence_Input.head()))
logger.warn("LCM_W_Input: {}".format(LCM_W_Input.head()))
# LCM_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.LCM_Input.csv"
# )
# SET_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.SET_Input.csv"
# )
# LCM_Reference_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.LCM_Reference_Input.csv"
# )
# SET_SOPWIP_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.SET_SOPWIP_Input.csv"
# )
# BOM_Version_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.BOM_Version_Input.csv"
# )
# SolverCurrentBucket = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.SolverCurrentBucket.csv"
# )
# OpenCell_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\OpenCell_Input.csv"
# )
# CodeMap_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.CodeMap_Input.csv"
# )
# Sequence_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.Sequence_Input.csv"
# )
# LCM_W_Input = pd.read_csv(
#    "C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\Fact.LCM_W_Input.csv"
# )

############### Start ###############

Sequence_Input[
    [
        "Sequence.[Sequence]",
    ]
] = Sequence_Input[
    [
        "Sequence.[Sequence]",
    ]
].astype(
    int
)

SolverCurrentBucket_Input = SolverCurrentBucket["Time.[Week]"].iloc[0]

LCM_W_Input[
    [
        "Location.[Location]",
        "Sub Location.[Sub Location]",
        "To Trans Mode.[To Trans Mode]",
        "Item Component.[Item Component]",
        "Item Material.[Item Material]",
        "To Item.[To Item]",
        "Week1.[Week1]",
    ]
] = LCM_W_Input[
    [
        "Location.[Location]",
        "Sub Location.[Sub Location]",
        "To Trans Mode.[To Trans Mode]",
        "Item Component.[Item Component]",
        "Item Material.[Item Material]",
        "To Item.[To Item]",
        "Week1.[Week1]",
    ]
].astype(
    str
)

SET_SOPWIP_Input[
    [
        "Item.[Item]",
        "Location.[Location]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Documents.[OrderlineID]",
        "Time.[Week]",
    ]
] = SET_SOPWIP_Input[
    [
        "Item.[Item]",
        "Location.[Location]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Documents.[OrderlineID]",
        "Time.[Week]",
    ]
].astype(
    str
)

LCM_Input[
    [
        "from.[Item].[Item]",
        "from.[Location].[Location]",
        "from.[Activity1].[Activity1]",
        "from.[Activity2].[Activity2]",
        "from.[Activity3].[Activity3]",
        "from.[Documents].[OrderlineID]",
        "from.[Time].[Week]",
        "to.[To Item].[To Item]",
        "to.[To Location].[To Location]",
        "to.[Activity1].[Activity1]",
        "to.[Activity2].[Activity2]",
        "to.[Activity3].[Activity3]",
        "to.[Documents].[OrderlineID]",
        "to.[To Time].[To Week]",
        "to.[Item].[Item]",
        "to.[Location].[Location]",
        "to.[Time].[Week]",
        "to.[Demand].[DemandID]",
        "to.[Sales Domain].[Customer Group]",
        "to.[Demand Type].[Demand Type]",
        "from.[Activity1].[Activity Type1]",
    ]
] = LCM_Input[
    [
        "from.[Item].[Item]",
        "from.[Location].[Location]",
        "from.[Activity1].[Activity1]",
        "from.[Activity2].[Activity2]",
        "from.[Activity3].[Activity3]",
        "from.[Documents].[OrderlineID]",
        "from.[Time].[Week]",
        "to.[To Item].[To Item]",
        "to.[To Location].[To Location]",
        "to.[Activity1].[Activity1]",
        "to.[Activity2].[Activity2]",
        "to.[Activity3].[Activity3]",
        "to.[Documents].[OrderlineID]",
        "to.[To Time].[To Week]",
        "to.[Item].[Item]",
        "to.[Location].[Location]",
        "to.[Time].[Week]",
        "to.[Demand].[DemandID]",
        "to.[Sales Domain].[Customer Group]",
        "to.[Demand Type].[Demand Type]",
        "from.[Activity1].[Activity Type1]",
    ]
].astype(
    str
)

LCM_Reference_Input[
    [
        "from.[Item].[Item]",
        "from.[Location].[Location]",
        "from.[Activity1].[Activity1]",
        "from.[Activity2].[Activity2]",
        "from.[Activity3].[Activity3]",
        "from.[Documents].[OrderlineID]",
        "from.[Time].[Week]",
        "to.[To Item].[To Item]",
        "to.[To Location].[To Location]",
        "to.[Activity1].[Activity1]",
        "to.[Activity2].[Activity2]",
        "to.[Activity3].[Activity3]",
        "to.[Documents].[OrderlineID]",
        "to.[To Time].[To Week]",
        "to.[Item].[Item]",
        "to.[Location].[Location]",
        "to.[Time].[Week]",
        "to.[Demand].[DemandID]",
        "to.[Sales Domain].[Customer Group]",
        "to.[Demand Type].[Demand Type]",
    ]
] = LCM_Reference_Input[
    [
        "from.[Item].[Item]",
        "from.[Location].[Location]",
        "from.[Activity1].[Activity1]",
        "from.[Activity2].[Activity2]",
        "from.[Activity3].[Activity3]",
        "from.[Documents].[OrderlineID]",
        "from.[Time].[Week]",
        "to.[To Item].[To Item]",
        "to.[To Location].[To Location]",
        "to.[Activity1].[Activity1]",
        "to.[Activity2].[Activity2]",
        "to.[Activity3].[Activity3]",
        "to.[Documents].[OrderlineID]",
        "to.[To Time].[To Week]",
        "to.[Item].[Item]",
        "to.[Location].[Location]",
        "to.[Time].[Week]",
        "to.[Demand].[DemandID]",
        "to.[Sales Domain].[Customer Group]",
        "to.[Demand Type].[Demand Type]",
    ]
].astype(
    str
)

SET_Input[
    [
        "from.[Item].[Item]",
        "from.[Location].[Location]",
        "from.[Activity1].[Activity1]",
        "from.[Activity2].[Activity2]",
        "from.[Activity3].[Activity3]",
        "from.[Documents].[OrderlineID]",
        "from.[Time].[Week]",
        "to.[To Item].[To Item]",
        "to.[To Location].[To Location]",
        "to.[Activity1].[Activity1]",
        "to.[Activity2].[Activity2]",
        "to.[Activity3].[Activity3]",
        "to.[Documents].[OrderlineID]",
        "to.[To Time].[To Week]",
        "to.[Item].[Item]",
        "to.[Location].[Location]",
        "to.[Time].[Week]",
        "to.[Demand].[DemandID]",
        "to.[Sales Domain].[Customer Group]",
        "to.[Demand Type].[Demand Type]",
    ]
] = SET_Input[
    [
        "from.[Item].[Item]",
        "from.[Location].[Location]",
        "from.[Activity1].[Activity1]",
        "from.[Activity2].[Activity2]",
        "from.[Activity3].[Activity3]",
        "from.[Documents].[OrderlineID]",
        "from.[Time].[Week]",
        "to.[To Item].[To Item]",
        "to.[To Location].[To Location]",
        "to.[Activity1].[Activity1]",
        "to.[Activity2].[Activity2]",
        "to.[Activity3].[Activity3]",
        "to.[Documents].[OrderlineID]",
        "to.[To Time].[To Week]",
        "to.[Item].[Item]",
        "to.[Location].[Location]",
        "to.[Time].[Week]",
        "to.[Demand].[DemandID]",
        "to.[Sales Domain].[Customer Group]",
        "to.[Demand Type].[Demand Type]",
    ]
].astype(
    str
)

SET_Input.rename(
    columns={
        "from.[Item].[Item]": "to.[To Item].[To Item]_SETMFG",
        "from.[Location].[Location]": "to.[To Location].[To Location]_SETMFG",
        "from.[Activity1].[Activity1]": "to.[Activity1].[Activity1]_SETMFG",
        "from.[Activity2].[Activity2]": "to.[Activity2].[Activity2]_SETMFG",
        "from.[Activity3].[Activity3]": "to.[Activity3].[Activity3]_SETMFG",
        "from.[Documents].[OrderlineID]": "to.[Documents].[OrderlineID]_SETMFG",
        "from.[Time].[Week]": "to.[To Time].[To Week]_SETMFG",
        "to.[To Item].[To Item]": "to.[To Item].[To Item]_SETSOP",
        "to.[To Location].[To Location]": "to.[To Location].[To Location]_SETSOP",
        "to.[Activity1].[Activity1]": "to.[Activity1].[Activity1]_SETSOP",
        "to.[Activity2].[Activity2]": "to.[Activity2].[Activity2]_SETSOP",
        "to.[Activity3].[Activity3]": "to.[Activity3].[Activity3]_SETSOP",
        "to.[Documents].[OrderlineID]": "to.[Documents].[OrderlineID]_SETSOP",
        "to.[To Time].[To Week]": "to.[To Time].[To Week]_SETSOP",
    },
    inplace=True,
)

if not LCM_Input.empty:
    LCMMFG = LCM_Input[
        (
            LCM_Input[
                "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]"
            ]
            > 0
        )
        & (LCM_Input["from.[Activity1].[Activity Type1]"] == "Manufacturing")
    ].reset_index(drop=True)

    LCMSOP = LCM_Input[
        LCM_Input[
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]"
        ]
        > 0
    ].reset_index(drop=True)

    LCMMFG = LCMMFG.drop(
        columns=[
            "from.[Activity1].[Activity Type1]",
        ]
    )
    LCMSOP = LCMSOP.drop(
        columns=[
            "from.[Activity1].[Activity Type1]",
        ]
    )

    LCMMFG_Merged = LCMMFG.merge(
        LCM_Reference_Input,
        on=[
            "from.[Item].[Item]",
            "from.[Location].[Location]",
            "from.[Activity1].[Activity1]",
            "from.[Activity2].[Activity2]",
            "from.[Activity3].[Activity3]",
            "from.[Documents].[OrderlineID]",
            "from.[Time].[Week]",
            "to.[Item].[Item]",
            "to.[Location].[Location]",
            "to.[Time].[Week]",
            "to.[Demand].[DemandID]",
            "to.[Sales Domain].[Customer Group]",
            "to.[Demand Type].[Demand Type]",
        ],
        how="left",
        suffixes=("_SETSOP", "_SETMFG"),
    )
    LCMSOP_Merged = LCMSOP.merge(
        LCM_Reference_Input,
        on=[
            "from.[Item].[Item]",
            "from.[Location].[Location]",
            "from.[Activity1].[Activity1]",
            "from.[Activity2].[Activity2]",
            "from.[Activity3].[Activity3]",
            "from.[Documents].[OrderlineID]",
            "from.[Time].[Week]",
            "to.[Item].[Item]",
            "to.[Location].[Location]",
            "to.[Time].[Week]",
            "to.[Demand].[DemandID]",
            "to.[Sales Domain].[Customer Group]",
            "to.[Demand Type].[Demand Type]",
        ],
        how="left",
        suffixes=("_SETSOP", "_SETMFG"),
    )

    LCMSOP_Merged = LCMSOP_Merged.drop(
        columns=[
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Producer From Pegged]",
        ]
    )
    LCMMFG_Merged = LCMMFG_Merged.drop(
        columns=[
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Producer From Pegged]",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Producer From Pegged]",
        ]
    )

    LCM_Merged = LCMMFG_Merged.merge(
        LCMSOP_Merged,
        on=[
            "to.[To Item].[To Item]_SETMFG",
            "to.[To Location].[To Location]_SETMFG",
            "to.[Activity1].[Activity1]_SETMFG",
            "to.[Activity2].[Activity2]_SETMFG",
            "to.[Activity3].[Activity3]_SETMFG",
            "to.[Documents].[OrderlineID]_SETMFG",
            "to.[To Time].[To Week]_SETMFG",
            "to.[To Item].[To Item]_SETSOP",
            "to.[To Location].[To Location]_SETSOP",
            "to.[Activity1].[Activity1]_SETSOP",
            "to.[Activity2].[Activity2]_SETSOP",
            "to.[Activity3].[Activity3]_SETSOP",
            "to.[Documents].[OrderlineID]_SETSOP",
            "to.[To Time].[To Week]_SETSOP",
            "to.[Item].[Item]",
            "to.[Location].[Location]",
            "to.[Time].[Week]",
            "to.[Demand].[DemandID]",
            "to.[Sales Domain].[Customer Group]",
            "to.[Demand Type].[Demand Type]",
        ],
        how="left",
        suffixes=("_LCMMFG", "_LCMSOP"),
    )

    LCM_Merged.rename(
        columns={
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]": "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]_LCMSOP",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]": "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]_LCMMFG",
        },
        inplace=True,
    )

    SET_LCM_Merged = SET_Input.merge(
        LCM_Merged,
        on=[
            "to.[To Item].[To Item]_SETMFG",
            "to.[To Location].[To Location]_SETMFG",
            "to.[Activity1].[Activity1]_SETMFG",
            "to.[Activity2].[Activity2]_SETMFG",
            "to.[Activity3].[Activity3]_SETMFG",
            "to.[Documents].[OrderlineID]_SETMFG",
            "to.[To Time].[To Week]_SETMFG",
            "to.[To Item].[To Item]_SETSOP",
            "to.[To Location].[To Location]_SETSOP",
            "to.[Activity1].[Activity1]_SETSOP",
            "to.[Activity2].[Activity2]_SETSOP",
            "to.[Activity3].[Activity3]_SETSOP",
            "to.[Documents].[OrderlineID]_SETSOP",
            "to.[To Time].[To Week]_SETSOP",
            "to.[Item].[Item]",
            "to.[Location].[Location]",
            "to.[Time].[Week]",
            "to.[Demand].[DemandID]",
            "to.[Sales Domain].[Customer Group]",
            "to.[Demand Type].[Demand Type]",
        ],
        how="left",
    )
else:
    SET_LCM_Merged = SET_Input.reindex(
        columns=[
            "to.[To Location].[To Location]_SETSOP",
            "to.[To Item].[To Item]_SETSOP",
            "to.[To Time].[To Week]_SETSOP",
            "to.[Activity1].[Activity1]_SETSOP",
            "to.[Activity2].[Activity2]_SETSOP",
            "to.[Activity3].[Activity3]_SETSOP",
            "to.[To Time].[To Week]_SETMFG",
            "to.[To Item].[To Item]_SETMFG",
            "to.[To Location].[To Location]_SETMFG",
            "to.[Activity1].[Activity1]_SETMFG",
            "from.[Location].[Location]_LCMMFG",
            "from.[Activity2].[Activity2]_LCMSOP",
            "from.[Item].[Item]_LCMMFG",
            "from.[Time].[Week]_LCMMFG",
            "from.[Time].[Week]_LCMSOP",
            "to.[Location].[Location]",
            "from.[Activity1].[Activity Type1]",
            "to.[Documents].[OrderlineID]_SETSOP",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]_LCMMFG",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]_LCMSOP",
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]",
            "SOP Bottom Up Pegging Output Graph.[W WIP SOP Adjust SET W_DC Site]",
        ]
    ).fillna(
        {
            "from.[Location].[Location]_LCMMFG": "-",
            "from.[Activity2].[Activity2]_LCMSOP": "-",
            "from.[Item].[Item]_LCMMFG": "-",
            "from.[Time].[Week]_LCMMFG": SolverCurrentBucket_Input,
            "from.[Time].[Week]_LCMSOP": SolverCurrentBucket_Input,
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]_LCMMFG": 0,
            "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]_LCMSOP": 0,
        }
    )

# Hub to DC
SET_LCM_Merged["to.[Location].[Location]"] = np.where(SET_LCM_Merged["SOP Bottom Up Pegging Output Graph.[W WIP SOP Adjust SET W_DC Site]"].notna(),SET_LCM_Merged["SOP Bottom Up Pegging Output Graph.[W WIP SOP Adjust SET W_DC Site]"],SET_LCM_Merged["to.[Location].[Location]"],)

logger.warn("SET_LCM_Merged: {}".format(SET_LCM_Merged.head()))

# Merge SOPWIP
SET_SOPWIP_Input.rename(
    columns={
        "Item.[Item]": "to.[To Item].[To Item]_SETSOP",
        "Location.[Location]": "to.[To Location].[To Location]_SETSOP",
        "Activity1.[Activity1]": "to.[Activity1].[Activity1]_SETSOP",
        "Activity2.[Activity2]": "to.[Activity2].[Activity2]_SETSOP",
        "Activity3.[Activity3]": "to.[Activity3].[Activity3]_SETSOP",
        "Documents.[OrderlineID]": "to.[Documents].[OrderlineID]_SETSOP",
        "Time.[Week]": "to.[To Time].[To Week]_SETSOP",
    },
    inplace=True,
)

Master_Merged = SET_LCM_Merged.merge(
    SET_SOPWIP_Input,
    on=[
        "to.[To Item].[To Item]_SETSOP",
        "to.[To Location].[To Location]_SETSOP",
        "to.[Activity1].[Activity1]_SETSOP",
        "to.[Activity2].[Activity2]_SETSOP",
        "to.[Activity3].[Activity3]_SETSOP",
        "to.[Documents].[OrderlineID]_SETSOP",
        "to.[To Time].[To Week]_SETSOP",
    ],
    how="left",
)

# Merge BOM Version and Open Cell

if not BOM_Version_Input.empty:
    BOM_Version_Input["to.[Activity1].[Activity1]_SETMFG"] = (
        BOM_Version_Input["Item.[Item]"]
        + "_"
        + BOM_Version_Input["BOM Info.[BOM Version]"]
    )

    OpenCell_Input.rename(
        columns={
            "Item.[Item]": "Item Material.[Item Material]",
        },
        inplace=True,
    )

    BOM_Version_Merged = BOM_Version_Input.merge(
        OpenCell_Input,
        on=[
            "Item Material.[Item Material]",
        ],
        how="left",
    )
    BOM_Version_Merged["Item Material.[Item Material]"] = np.where(
        BOM_Version_Merged["Item.[Item Stage]"].isna(), 
        "-",
        BOM_Version_Merged["Item Material.[Item Material]"],
    )

    BOM_Version_Merged.rename(
        columns={
            "Item.[Item]": "to.[To Item].[To Item]_SETMFG",
            "Location.[Location]": "to.[To Location].[To Location]_SETMFG",
        },
        inplace=True,
    )

    Master_Merged = Master_Merged.merge(
        BOM_Version_Merged,
        on=[
            "to.[To Item].[To Item]_SETMFG",
            "to.[To Location].[To Location]_SETMFG",
            "to.[Activity1].[Activity1]_SETMFG",
        ],
        how="left",
    )
else:
    Master_Merged["Item Material.[Item Material]"] = Master_Merged.get(
        "Item Material.[Item Material]", "-"
    )
    Master_Merged["BOM Info.[BOM Version]"] = Master_Merged.get(
        "BOM Info.[BOM Version]", "-"
    )
logger.warn("BOM_Version: {}".format(Master_Merged.head()))

# Merge CodeMap
if not CodeMap_Input.empty:

    CodeMap_Input.rename(
        columns={
            "Item.[Item]": "from.[Item].[Item]_LCMMFG",
            "Location.[Location]": "from.[Location].[Location]_LCMMFG",
            "Sub Location.[Sub Location]": "to.[To Location].[To Location]_SETSOP",
        },
        inplace=True,
    )

    Master_Merged = Master_Merged.merge(
        CodeMap_Input,
        on=[
            "from.[Item].[Item]_LCMMFG",
            "from.[Location].[Location]_LCMMFG",
            "to.[To Location].[To Location]_SETSOP",
        ],
        how="left",
    )
else:
    Master_Merged["Code Map LCM_Prod Item"] = Master_Merged.get(
        "Code Map LCM_Prod Item", "-"
    )

logger.warn("CodeMap: {}".format(Master_Merged.head()))

# Add Sequence

Sequence_Input["Sequence.[Sequence]"] = (
    Sequence_Input["Sequence.[Sequence]"].fillna(0) + 1
)
MaxSequence = Sequence_Input["Sequence.[Sequence]"].iloc[0].astype(int)

Master_Merged["Sequence.[Sequence]"] = MaxSequence + pd.RangeIndex(len(Master_Merged))

logger.warn("Sequence: {}".format(Master_Merged.head()))
# SOP_W
SOP_W = Master_Merged[
    [
        "Version.[Version Name]",
        "to.[To Location].[To Location]_SETSOP",
        "to.[To Item].[To Item]_SETSOP",
        "to.[To Time].[To Week]_SETSOP",
        "from.[Location].[Location]_LCMMFG",
        "from.[Activity2].[Activity2]_LCMSOP",
        "from.[Item].[Item]_LCMMFG",
        "to.[Activity2].[Activity2]_SETSOP",
        "from.[Time].[Week]_LCMMFG",
        "from.[Time].[Week]_LCMSOP",
        "to.[To Time].[To Week]_SETMFG",
        "BOM Info.[BOM Version]",
        "to.[Location].[Location]",
        "Sequence.[Sequence]",
        "from.[Activity1].[Activity Type1]",
        "Item Material.[Item Material]",
        "Code Map LCM_Prod Item",
        "to.[Documents].[OrderlineID]_SETSOP",
        "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]_LCMMFG",
        "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]_LCMSOP",
        "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]",
    ]
]

# Rename
SOP_W.rename(
    columns={
        "to.[To Location].[To Location]_SETSOP": "Location.[Location]",
        "to.[To Item].[To Item]_SETSOP": "Item.[Item]",
        "to.[To Time].[To Week]_SETSOP": "To Time.[To Week]",
        "from.[Location].[Location]_LCMMFG": "Sub Location.[Sub Location]",
        "from.[Activity2].[Activity2]_LCMSOP": "To Trans Mode.[To Trans Mode]",
        "Code Map LCM_Prod Item": "Item Component.[Item Component]",
        "from.[Item].[Item]_LCMMFG": "To Item.[To Item]",
        "to.[Location].[Location]": "To Location.[To Location]",
        "to.[Activity2].[Activity2]_SETSOP": "Trans Mode.[Trans Mode]",
        "from.[Time].[Week]_LCMMFG": "Week1.[Week1]",
        "from.[Time].[Week]_LCMSOP": "Week2.[Week2]",
        "to.[To Time].[To Week]_SETMFG": "Time.[Week]",
        "to.[Documents].[OrderlineID]_SETSOP": "SOP W_SOP ID",
        "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]_LCMMFG": "SOP W_LCM MFG Qty",
        "SOP Bottom Up Pegging Output Graph.[SOP BUP Consumer to Consumer From Pegged]_LCMSOP": "SOP W_LCM SOP Qty",
        "SOP Bottom Up Pegging Output Graph.[SOP BUP Producer to Consumer From Pegged]": "SOP W_SET MFG Qty",
    },
    inplace=True,
)

# FillNA -
SOP_W[
    [
        "Item Material.[Item Material]",
        "Item Component.[Item Component]",
        "BOM Info.[BOM Version]",
        "To Item.[To Item]",
        "To Trans Mode.[To Trans Mode]",
        "Sub Location.[Sub Location]",
    ]
] = SOP_W[
    [
        "Item Material.[Item Material]",
        "Item Component.[Item Component]",
        "BOM Info.[BOM Version]",
        "To Item.[To Item]",
        "To Trans Mode.[To Trans Mode]",
        "Sub Location.[Sub Location]",
    ]
].fillna(
    "-"
)

# FillNA 0
SOP_W[["SOP W_LCM MFG Qty", "SOP W_LCM SOP Qty", "SOP W_SET MFG Qty"]] = SOP_W[
    ["SOP W_LCM MFG Qty", "SOP W_LCM SOP Qty", "SOP W_SET MFG Qty"]
].fillna(0)

# FillNA SolverCurrentBucket

SOP_W[["Time.[Week]", "Week1.[Week1]", "Week2.[Week2]"]] = SOP_W[
    ["Time.[Week]", "Week1.[Week1]", "Week2.[Week2]"]
].fillna(SolverCurrentBucket_Input)

SOP_W["SOP W_LCM SOP Adj Qty"] = SOP_W["SOP W_LCM MFG Qty"]
SOP_W["SOP W_SET SOP Adj Qty"] = SOP_W["SOP W_SET MFG Qty"]
SOP_W["SOP W_SET SOP Qty"] = SOP_W["SOP W_SET MFG Qty"]
SOP_W["SOP W_LCM Plant"] = SOP_W["Sub Location.[Sub Location]"]

# If Not Manufacturing (SETMFG pegging does not exist)

SOP_W["Time.[Week]"] = np.where(
    SOP_W["from.[Activity1].[Activity Type1]"] == "Manufacturing",
    SOP_W["Time.[Week]"],
    SolverCurrentBucket_Input,
)

SOP_W["SOP W_SET MFG Qty"] = np.where(
    SOP_W["from.[Activity1].[Activity Type1]"] == "Manufacturing",
    SOP_W["SOP W_SET MFG Qty"],
    0,
)

SOP_W = SOP_W.drop(
    columns=[
        "from.[Activity1].[Activity Type1]",
    ]
)

# LCM W
LCM_W_Agg = (
    SOP_W[
        [
            "Version.[Version Name]",
            "Location.[Location]",
            "Sub Location.[Sub Location]",
            "To Trans Mode.[To Trans Mode]",
            "Item Component.[Item Component]",
            "Item Material.[Item Material]",
            "To Item.[To Item]",
            "Week1.[Week1]",
            "SOP W_LCM SOP Qty",
        ]
    ]
    .groupby(
        [
            "Version.[Version Name]",
            "Location.[Location]",
            "Sub Location.[Sub Location]",
            "To Trans Mode.[To Trans Mode]",
            "Item Component.[Item Component]",
            "Item Material.[Item Material]",
            "To Item.[To Item]",
            "Week1.[Week1]",
        ]
    )["SOP W_LCM SOP Qty"]
    .sum()
    .reset_index()[lambda x: x["SOP W_LCM SOP Qty"] > 0]
)

LCM_W = LCM_W_Agg.merge(
    LCM_W_Input,
    on=[
        "Location.[Location]",
        "Sub Location.[Sub Location]",
        "To Trans Mode.[To Trans Mode]",
        "Item Component.[Item Component]",
        "Item Material.[Item Material]",
        "To Item.[To Item]",
        "Week1.[Week1]",
    ],
    how="left",
)

LCM_W[["SOP Adjust LCM W_SOP Qty"]] = LCM_W[
    ["SOP Adjust LCM W_SOP Qty"]
].fillna(0)

LCM_W["SOP Adjust LCM W_SOP Qty"] = (
    LCM_W["SOP Adjust LCM W_SOP Qty"] + LCM_W["SOP W_LCM SOP Qty"]
)

LCM_W["SOP Adjust LCM W_SOP Adj Qty"] = LCM_W["SOP Adjust LCM W_SOP Qty"]

LCM_W= LCM_W.drop(
    columns=[
        "SOP W_LCM SOP Qty",
    ]
)

# LCM_W.to_csv(
#    r"C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\LCM_W.csv",
#    index=False,
# )
#
# SOP_W.to_csv(
#    r"C:\\Users\\kisoonk.kim\\Documents\\Python Scripts\\SOP_W.csv",
#    index=False,
# )

logger.warning(len(SOP_W.index))
logger.warn("SOP_W: {}".format(SOP_W.head()))
logger.warning(len(LCM_W.index))
logger.warn("LCM_W: {}".format(LCM_W.head()))

O9DataLake.put("SOP_W", SOP_W)
O9DataLake.put("LCM_W", LCM_W)

endTime = time.time()
logger.debug(f"END({endTime}): {endTime - initTime} secs")
