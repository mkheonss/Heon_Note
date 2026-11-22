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

############### Exec ###############
# exec plugin instance [PY_UI_SOPAdjust_UpdateLCMBOD] for measures {[W Activity Priority]} using scope ([Version].[Version Name].[CWV_MP] * &PlanningHorizon ) using arguments {("IgnoreMissingOutputs", true), ("IncludeNullRows", "False"), (ExecutionMode, "Mediumweight"), (MaxConcurrency, 1), (MaxSliceTableCells, 90000000)};
initTime = time.time()
logger.debug(f"START({initTime})")
logger.warn("@@@@@@@@@@@@@@@ PY_UI_SOPAdjust_UpdateLCMBOD execution Started @@@@@@@@@@@@@@@")

in_SolverStartBucket = O9DataLake.get("in_SolverStartBucket")
in_SolverEndBucket = O9DataLake.get("in_SolverEndBucket")
in_BODItem = O9DataLake.get("in_BODItem")
in_BODItemW = O9DataLake.get("in_BODItemW")

logger.warn("in_SolverStartBucket : {}".format(in_SolverStartBucket.head()))
logger.warn("in_SolverEndBucket : {}".format(in_SolverEndBucket.head()))
logger.warn("in_BODItem : {}".format(in_BODItem.head()))
logger.warn("in_BODItemW : {}".format(in_BODItemW.head()))

############### Start ###############

out_ActivityParameters = pd.DataFrame()
out_ActivityTimeVaryingParameters = pd.DataFrame()
out_ActivityPriority = pd.DataFrame()

# in_SolverStartBucket ["Time.[Week]"] = pd.to_datetime(
# in_SolverStartBucket ["Time.[Week]"].apply(lambda x: str(x) + "-0"),
#    format="%Y%W-%w",
# )

######  TimeVarying  #####
in_BODItemW.rename(
    columns={
        "Item.[Item]": "Activity3.[Activity3]",
        "Trans Mode.[Trans Mode]": "Activity2.[Activity2]",
        "BOD Item W_BOD LT": "W Activity Lead Time Time Varying",
        "BOD Item W_Shipment LT": "W Activity Mandatory Offset Time Varying",
    },
    inplace=True,
)

in_BODItemW["Activity1.[Activity1]"] = (
    in_BODItemW["Location.[Location]"]
    + "_"
    + in_BODItemW["Sub Location.[Sub Location]"]
    + "_"
    + in_BODItemW["Activity2.[Activity2]"]
)

in_BODItemW = in_BODItemW.drop(
    columns=["Location.[Location]", "Sub Location.[Sub Location]"]
)

in_BODItemW["W Activity Lead Time Time Varying"] = (
    in_BODItemW["W Activity Lead Time Time Varying"] / 7
)
in_BODItemW["W Activity Mandatory Offset Time Varying"] = (
    in_BODItemW["W Activity Mandatory Offset Time Varying"] / 7
)

in_BODItemW["W Activity Lead Time Time Varying"].fillna(0, inplace=True)
in_BODItemW["W Activity Mandatory Offset Time Varying"].fillna(0, inplace=True)

logger.warn("in_BODItemW: {}".format(in_BODItemW.head()))

##### None TimeVarying #####
in_BODItem.rename(
    columns={
        "Item.[Item]": "Activity3.[Activity3]",
        "Trans Mode.[Trans Mode]": "Activity2.[Activity2]",
        "BOD Item_Priority": "W Activity Priority",
        "BOD Item_Eff Startdate": "W Activity Start Date",
        "BOD Item_Eff Enddate": "W Activity End Date",
        "BOD Item_BOD Frozen": "W Frozen Window",
        "BOD Item_BOD LT": "W Activity Lead Time",
        "BOD Item_Shipment LT": "W Activity Mandatory Offset",
    },
    inplace=True,
)

in_BODItem["Activity1.[Activity1]"] = (
    in_BODItem["Location.[Location]"]
    + "_"
    + in_BODItem["Sub Location.[Sub Location]"]
    + "_"
    + in_BODItem["Activity2.[Activity2]"]
)

in_BODItem["W Activity Lead Time"] = in_BODItem["W Activity Lead Time"] / 7
in_BODItem["W Activity Mandatory Offset"] = (
    in_BODItem["W Activity Mandatory Offset"] / 7
)
in_BODItem["W Frozen Window"] = in_BODItem["W Frozen Window"] / 7

in_BODItem["W Activity Lead Time"].fillna(0, inplace=True)
in_BODItem["W Activity Mandatory Offset"].fillna(0, inplace=True)
in_BODItem["W Frozen Window"].fillna(0, inplace=True)
in_BODItem["W Activity Priority"].fillna(1, inplace=True)
in_BODItem["Item.[Item]"] = in_BODItem["Activity3.[Activity3]"]

out_ActivityParameters = in_BODItem[in_BODItem["BOD Item_Creation Time"].isna()][
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "W Activity Start Date",
        "W Activity End Date",
        "W Frozen Window",
        "W Activity Lead Time",
        "W Activity Mandatory Offset",
    ]
]

out_ActivityPriority = in_BODItem[in_BODItem["BOD Item_Creation Time"].isna()][
    [
        "Version.[Version Name]",
        "Sub Location.[Sub Location]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Item.[Item]",
        "W Activity Priority",
    ]
]
out_ActivityPriority.rename(
    columns={
        "Sub Location.[Sub Location]": "Location.[Location]",
    },
    inplace=True,
)


newBOD = in_BODItem[in_BODItem["BOD Item_Creation Time"].notna()][
    [
        "Version.[Version Name]",
        "Location.[Location]",
        "Sub Location.[Sub Location]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Item.[Item]",
        "W Activity Priority",
        "W Activity Start Date",
        "W Activity End Date",
        "W Frozen Window",
        "W Activity Lead Time",
        "W Activity Mandatory Offset",
    ]
]

if not newBOD.empty:
    createNewBOM = newBOD.copy()
    createNewBOM["W Material Consumption Association"] = 1
    createNewBOM["W Material Consumption Quantity Per"] = 1
    createNewBOM["W Material Production Association"] = 1
    createNewBOM["W Material Production Quantity Per"] = 1
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
            "W Activity Mandatory Offset",
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


# createNewActivityTimeVaryingParameters = FullBODW.merge(
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


out_ActivityTimeVaryingParameters = in_BODItemW[
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Time.[Week]",
        "W Activity Lead Time Time Varying",
        "W Activity Mandatory Offset Time Varying",
    ]
]

logger.warning(len(out_ActivityPriority.index))
logger.warn("out_ActivityPriority: {}".format(out_ActivityPriority.head()))
logger.warning(len(out_ActivityParameters.index))
logger.warn("out_ActivityParameters: {}".format(out_ActivityParameters.head()))
logger.warning(len(out_ActivityTimeVaryingParameters.index))
logger.warn(
    "out_ActivityTimeVaryingParameters: {}".format(
        out_ActivityTimeVaryingParameters.head()
    )
)
logger.warning(len(out_Consumption.index))
logger.warn("out_Consumption: {}".format(out_Consumption.head()))
logger.warning(len(out_Production.index))
logger.warn("out_Production: {}".format(out_Production.head()))
O9DataLake.put("out_ActivityParameters", out_ActivityParameters)
O9DataLake.put("out_ActivityTimeVaryingParameters", out_ActivityTimeVaryingParameters)
O9DataLake.put("out_Consumption", out_Consumption)
O9DataLake.put("out_Production", out_Production)

endTime = time.time()
logger.debug(f"END({endTime}): {endTime - initTime} secs")
