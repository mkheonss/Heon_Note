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
# exec plugin instance [PY_UI_SOPAdjust_UpdateSETBOMPr] for measures {[W Activity Priority]} using scope ([Version].[Version Name].[CWV_MP] * &PlanningHorizon ) using arguments {("IgnoreMissingOutputs", true), ("IncludeNullRows", "False"), (ExecutionMode, "Mediumweight"), (MaxConcurrency, 1), (MaxSliceTableCells, 90000000)};

initTime = time.time()
logger.debug(f"START({initTime})")
logger.warn("@@@@@@@@@@@@@@@ PY_UI_SOPAdjust_UpdateSETBOMPr Started @@@@@@@@@@@@@@@")

in_SolverStartBucket = O9DataLake.get("in_SolverStartBucket")
in_SolverEndBucket = O9DataLake.get("in_SolverEndBucket")
in_BOMVersion= O9DataLake.get("in_BOMVersion")
in_BOMVersionW = O9DataLake.get("in_BOMVersionW")

logger.warn("in_SolverStartBucket : {}".format(in_SolverStartBucket.head()))
logger.warn("in_SolverEndBucket : {}".format(in_SolverEndBucket.head()))
logger.warn("in_BOMVersion: {}".format(in_BOMVersion.head()))
logger.warn("in_BOMVersionW : {}".format(in_BOMVersionW.head()))

############### Start ###############

out_ActivityParameters = pd.DataFrame()
out_ActivityTimeVaryingParameters = pd.DataFrame()

# in_SolverStartBucket ["Time.[Week]"] = pd.to_datetime(
# in_SolverStartBucket ["Time.[Week]"].apply(lambda x: str(x) + "-0"),
#    format="%Y%W-%w",
# )


##### BOMVersion #####
in_BOMVersion["Activity1.[Activity1]"] = (
    in_BOMVersion["Item.[Item]"]
    + "_"
    + in_BOMVersion["BOM Info.[BOM Version]"]
)
in_BOMVersion["Activity2.[Activity2]"] = (
    "RT_"
    + in_BOMVersion["Item.[Item]"]
    + "_"
    + in_BOMVersion["BOM Info.[BOM Version]"]
    + "@"
    + in_BOMVersion["Location.[Location]"]
)
in_BOMVersion["Activity3.[Activity3]"] = in_BOMVersion["Item.[Item]"]
in_BOMVersion.rename(
    columns={
        "BOM Version_Prty": "W Activity Priority",
    },
    inplace=True,
)
out_ActivityParameters = in_BOMVersion[
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Item.[Item]",
        "Location.[Location]",
        "W Activity Priority",
    ]
]

##### BOMVersionTimeVarying #####

in_BOMVersionW["Activity1.[Activity1]"] = (
    in_BOMVersionW["Item.[Item]"]
    + "_"
    + in_BOMVersionW["BOM Info.[BOM Version]"]
)
in_BOMVersionW["Activity2.[Activity2]"] = (
    "RT_"
    + in_BOMVersionW["Item.[Item]"]
    + "_"
    + in_BOMVersionW["BOM Info.[BOM Version]"]
    + "@"
    + in_BOMVersionW["Location.[Location]"]
)
in_BOMVersionW["Activity3.[Activity3]"] = in_BOMVersionW["Item.[Item]"]
in_BOMVersionW.rename(
    columns={
        "BOM Version Prty W_Prty": "W Activity Priority Time Varying",
    },
    inplace=True,
)
out_ActivityTimeVaryingParameters = in_BOMVersionW[
    [
        "Version.[Version Name]",
        "Activity1.[Activity1]",
        "Activity2.[Activity2]",
        "Activity3.[Activity3]",
        "Item.[Item]",
        "Location.[Location]",
        "Time.[Week]",
        "W Activity Priority Time Varying",
    ]
]
logger.warning(len(out_ActivityParameters.index))
logger.warn("out_ActivityParameters: {}".format(out_ActivityParameters.head()))
O9DataLake.put("out_ActivityParameters", out_ActivityParameters)
logger.warning(len(out_ActivityTimeVaryingParameters.index))
logger.warn("out_ActivityTimeVaryingParameters: {}".format(out_ActivityTimeVaryingParameters.head()))
O9DataLake.put("out_ActivityTimeVaryingParameters", out_ActivityTimeVaryingParameters)

endTime = time.time()
logger.debug(f"PY_UI_SOPAdjust_UpdateSETBOMPr END({endTime}): {endTime - initTime} secs")
