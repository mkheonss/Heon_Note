define('o9.NSCM.JS.SeasonalDelay', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.Simulation.
     *
     * Simulation 공용
     */
    /***********************************************************************/
    /******************* const 설정                  ************************/
    /***********************************************************************/
    /* Program Name */
    const programName = 'o9.NSCM.JS.SeasonalDelay';
    /* jsErrorMsg   */
    const jsErrorMsg = 'An error occurred during the Simulation. \n Please contact the system administrator.';
    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug");
    let daUtil = new commonLib.DAUtil();
    /**
     * Logs the given message.
     *
     * @param {string} msg - The message to be logged.
     * @returns {void}
     */
    let log = function(msg) {
        daCommon.debug(msg);
    }
    /**
     * Prints the given parameters.
     *
     * @param {Array} params - The parameters to be printed.
     */
    let printParams = function(params) {
        daCommon.printParams(params);
    }
/**********************************************************************************************************************/
/***************** TRANSACTION START *********************************************************************/
/**********************************************************************************************************************/
    let fn_SubmitSeasonalDelaySetWeightByYear = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        let param = {};
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        tupleList.forEach(e => {
            e.fb_Version = parsedParams.fb_Version;
            e.fb_Y1 = parsedParams.fb_Y1;
            e.fb_Y2 = parsedParams.fb_Y2;
            e.fb_Y3 = parsedParams.fb_Y3;
            QueryCommon.executeCartesianSeasonalDelaySetWeightByYear(e);
        });
    }
    

    class QueryCommon {
        static executeCartesianSeasonalDelaySetWeightByYear(parsedParams) {
            let query =`
                cartesian scope: (
                                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                                    * [Sub Location].[Sub Location].[${parsedParams.fb_SubLocation.Value}] 
                                    * [Location].[Location].[${parsedParams.fb_Location.Value}]
                                    * [Activity2].[Activity2].[${parsedParams.fb_Activity2.Value}] 
                                    * [Horizon].[Horizon].[${parsedParams.fb_Horizon.Value}] 
                                );
                    Measure.[Seasonal Delay BOD_Y-1 Weight] = ${parsedParams.fb_Y1};
                    Measure.[Seasonal Delay BOD_Y-2 Weight] = ${parsedParams.fb_Y2};
                    Measure.[Seasonal Delay BOD_Y-3 Weight] = ${parsedParams.fb_Y3};              
                end scope;
                `
            // Log.Info("##########################executeCartesianSeasonalDelaySetWeightByYear:: "+query);
            return daCommon.executeQuery('executeCartesianSeasonalDelaySetWeightByYear', query);
        };

        static selectBODLanePortRatioCapaPerWk(paramsObj) {
            let query = `
                
            `;
            // Log.Info("##########################selectProject:: "+query);
            // return daCommon.selectQueryList('selectBODLanePortRatioCapaPerWk', query);
        }
    }
    
    return {
        fn_SubmitSeasonalDelaySetWeightByYear : daCommon.fn_decorator(fn_SubmitSeasonalDelaySetWeightByYear)
    };
});