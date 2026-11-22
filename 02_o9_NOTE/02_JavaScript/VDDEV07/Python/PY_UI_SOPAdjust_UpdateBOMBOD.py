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
# exec plugin instance [SOPAdjust_BOD] for measures {[BOD Item Mtrl_Updated Time]} using scope ([Version].[Version Name].[CWV_MP] * &PlanningHorizon ) using arguments {("IncludeNullRows", "False"), (ExecutionMode, "Mediumweight"), (MaxConcurrency, 1), (MaxSliceTableCells, 90000000)};

initTime = time.time()
logger.debug(f"START({initTime})")
logger.warn("@@@@@@@@@@@@@@@ EXP_PSI execution Started @@@@@@@@@@@@@@@")

in_SolverStartBucket = O9DataLake.get("in_SolverStartBucket")
in_SolverEndBucket = O9DataLake.get("in_SolverEndBucket")
in_ActivityParameters = O9DataLake.get("in_ActivityParameters")
in_ActivityTimeVaryingParameters = O9DataLake.get("in_ActivityTimeVaryingParameters")
in_Consumption = O9DataLake.get("in_Consumption")
in_Production = O9DataLake.get("in_Production")
in_PriorityTimeVarying = O9DataLake.get("in_PriorityTimeVarying")
in_BODItemMaterial = O9DataLake.get("in_BODItemMaterial")
in_BODItemMaterialW = O9DataLake.get("in_BODItemMaterialW")

logger.warn("in_SolverStartBucket : {}".format(in_SolverStartBucket.head()))
logger.warn("in_SolverEndBucket : {}".format(in_SolverEndBucket.head()))
logger.warn("in_ActivityParameters : {}".format(in_ActivityParameters.head()))
logger.warn(
    "in_ActivityTimeVaryingParameters : {}".format(
        in_ActivityTimeVaryingParameters.head()
    )
)
logger.warn("in_Consumption : {}".format(in_Consumption.head()))
logger.warn("in_Production : {}".format(in_Production.head()))
logger.warn("in_PriorityTimeVarying : {}".format(in_PriorityTimeVarying.head()))
logger.warn("in_BODItemMaterial : {}".format(in_BODItemMaterial.head()))
logger.warn("in_BODItemMaterialW : {}".format(in_BODItemMaterialW.head()))

############### Start ###############

# in_SolverStartBucket ["Time.[Week]"] = pd.to_datetime(
# in_SolverStartBucket ["Time.[Week]"].apply(lambda x: str(x) + "-0"),
#    format="%Y%W-%w",
# )


####### Mtrl BOD
in_BODItemMaterial["in_BODItemMaterial_Activity1"] = (
    in_BODItemMaterial["Location.[Location]"]
    + "_"
    + in_BODItemMaterial["Sub Location.[Sub Location]"]
    + "_"
    + in_BODItemMaterial["Trans Mode.[Trans Mode]"]
)

merged_in_ActivityParameters = in_BODItemMaterial.merge(
    in_ActivityParameters,
    left_on=[
        "in_BODItemMaterial_Activity1",
        "Trans Mode.[Trans Mode]",
        "Item Material.[Item Material]",
    ],
    right_on=[
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
    ],
    how="left",
    suffixes=("MDM", "_solverinput"),
)

in_ActivityParameters.loc[
    merged_in_ActivityParameters.index, "W Activity Start Date"
] = merged_in_ActivityParameters["BOD Item Mtrl_EFF Startdate"]
in_ActivityParameters.loc[merged_in_ActivityParameters.index, "W Activity End Date"] = (
    merged_in_ActivityParameters["BOD Item Mtrl_EFF Enddate"]
)

key_in_BODItemMaterial = in_BODItemMaterial.set_index(
    [
        "in_BODItemMaterial_Activity1",
        "Trans Mode.[Trans Mode]",
        "Item Material.[Item Material]",
    ]
).index

key_in_ActivityParameters = in_ActivityParameters.set_index(
    ["Activity1.[Activity1]", "Activity2.[Activity2]", "Activity3.[Activity3]"]
).index

mask = ~key_in_BODItemMaterial.isin(key_in_ActivityParameters)
newBODItemMaterial = in_BODItemMaterial[mask].reset_index(drop=True)

if not newBODItemMaterial.empty:
    createNewBOM = newBODItemMaterial.copy()
    createNewBOM["W Frozen Window"] = 34
    createNewBOM["W Material Consumption Association"] = 1
    createNewBOM["W Material Consumption Quantity Per"] = 1
    createNewBOM["W Material Production Association"] = 1
    createNewBOM["W Material Production Quantity Per"] = 1
    createNewBOM["W Activity Priority"] = 99
    createNewBOM["W Activity Lead Time"] = 0
    createNewBOM["Item.[Item]"] = createNewBOM["Item Material.[Item Material]"]
    createNewBOM.rename(
        columns={
            "in_BODItemMaterial_Activity1": "Activity1.[Activity1]",
            "Trans Mode.[Trans Mode]": "Activity2.[Activity2]",
            "Item Material.[Item Material]": "Activity3.[Activity3]",
            "BOD Item Mtrl_EFF Startdate": "W Activity Start Date",
            "BOD Item Mtrl_EFF Enddate": "W Activity End Date",
        },
        inplace=True,
    )

createNewActivityParameters = createNewBOM[
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "W Activity Start Date",
        "W Activity End Date",
        "W Frozen Window",
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
    [in_ActivityParameters, createNewActivityParameters], ignore_index=True
)

out_Consumption = createNewConsumption

out_Production = createNewProduction

in_BODItemMaterialW["BOD Item Mtrl W_Total LT"] = (
    in_BODItemMaterialW["BOD Item Mtrl W_Total LT"] / 7
)


in_BODItemMaterialW["Activity1.[Activity1]"] = (
    in_BODItemMaterialW["Location.[Location]"]
    + "_"
    + in_BODItemMaterialW["Sub Location.[Sub Location]"]
    + "_"
    + in_BODItemMaterialW["Trans Mode.[Trans Mode]"]
)

in_BODItemMaterialW.rename(
    columns={
        "Item Material.[Item Material]": "Activity3.[Activity3]",
        "Trans Mode.[Trans Mode]": "Activity2.[Activity2]",
        "BOD Item Mtrl W_Total LT": "W Activity Lead Time Time Varying",
    },
    inplace=True,
)

createNewActivityTimeVaryingParameters = in_BODItemMaterialW.merge(
    createNewBOM[
        [
            "Activity1.[Activity1]",
            "Activity2.[Activity2]",
            "Activity3.[Activity3]",
        ]
    ].drop_duplicates(),
    on=[
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
    ],
    how="inner",
)


out_ActivityTimeVaryingParameters = createNewActivityTimeVaryingParameters


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
