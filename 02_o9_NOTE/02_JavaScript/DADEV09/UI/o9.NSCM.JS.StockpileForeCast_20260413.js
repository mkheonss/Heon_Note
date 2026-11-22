define('o9.NSCM.JS.StockpileForeCast', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.StockpileForeCast';
    /* jsErrorMsg   */
    const jsErrorMsg = 'An error occurred during G/R Update. \n Please contact the system administrator.';
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
    let fn_SubmitStockpileForecastGRUpdate = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        let tupleList = parsedParams.fb_TupleList;
        let resultSet;
        let paramObj = {};
        paramObj.fb_Version = parsedParams.fb_Version;
        paramObj.fb_WKFrom = parsedParams.fb_WKFrom;
        paramObj.fb_WKTo = parsedParams.fb_WKTo;
        paramObj.fb_Gr = parsedParams.fb_Gr;
        
        tupleList.forEach(item => {
            let forecastWDmdArr = [];
            let wKFromToArr = [];
            paramObj.fb_AP2 = item.fb_AP2;
            paramObj.fb_ProductGroup = item.fb_ProductGroup;
            paramObj.fb_SCMType = item.fb_SCMType;
            resultSet = QueryCommon.selectStockpileForecastDetailWDemand(paramObj);

            for(let i = 0; i < resultSet.cs.rowCount; i++){
                wKFromToArr.push(daCommon.getMember(resultSet.cs, i, 'Time', 'Week').Name);
                // forecastWDmdArr.push(parseInt(daCommon.getMeasureValue(resultSet.cs, i, 'Stockpile FCST Detail W_Demand')));
                forecastWDmdArr.push(parseInt(daCommon.getMeasureValue(resultSet.cs, i, 'Stockpile FCST W_Source Demand')));    // Simulated Demand = Simulated G/R * Source Demand  [김태혁 | 01-08 19:56]
            }
            //Simulated Demand = Simulated G/R * Demand 로 Update해준다.
            let simulDmdArr = forecastWDmdArr.map(ele => ele * parsedParams.fb_Gr);

            for(let i = 0; i < wKFromToArr.length; i++){
                paramObj.simulDmd = simulDmdArr[i];
                paramObj.week = wKFromToArr[i];
                QueryCommon.executeCartesianSimulatedDemand(paramObj);
            }
            // Log.Info(`##########################wKFromToArr:: ${wKFromToArr}, forecastWDmdArr:: ${forecastWDmdArr}`);
        });
    }

    class QueryCommon {
        static selectStockpileForecastDetailWDemand(parsedParams) {
            let query =`
                Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Sales Domain].[Sales Std2].[${parsedParams.fb_AP2.Value}] 
                    * [Item].[Product Group].[${parsedParams.fb_ProductGroup.Value}] 
                    * [SCM Type].[SCM Type].[${parsedParams.fb_SCMType.Value}] 
                    * [Time].[Week].filter(#.Name >= [${parsedParams.fb_WKFrom}] && #.Name <= [${parsedParams.fb_WKTo}]) 
                ) on row, 
                ({
                     Measure.[Stockpile FCST Detail W_Demand]
                    , Measure.[Stockpile FCST W_Simulated Demand]
                    , Measure.[Stockpile FCST W_G/R]
                    , Measure.[Stockpile FCST W_Simulated G/R]
                    , Measure.[Stockpile FCST W_Source Demand]
                }) on column;
            `;
            // Log.Info("##########################selectStockpileForecastDetailWDemand:: "+query);
            return daCommon.selectQueryList('selectStockpileForecastDetailWDemand', query);
        };

        static selectDsWKFromTo(parsedParams) {
            let query =`
                select (
                    &AllWeeks.filter(#.Key >= &AllWeeks.Filter(#.Name == "${parsedParams.fb_WKFrom}").element(0).Key 
                    && #.Key <= &AllWeeks.Filter(#.Name == "${parsedParams.fb_WKTo}").element(0).Key)
                ) on row;
            `;
            // Log.Info("##########################selectDsWKFromTo:: "+query);
            return daCommon.selectQueryList('selectDsWKFromTo', query);
        };

        static executeCartesianSimulatedDemand(parsedParams) {
            let query =`
                scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Sales Domain].[Sales Std2].[${parsedParams.fb_AP2.Value}] 
                    * [Item].[Product Group].[${parsedParams.fb_ProductGroup.Value}]
                    * [SCM Type].[SCM Type].[${parsedParams.fb_SCMType.Value}]
                    * [Time].[Week].[${parsedParams.week}]
                );
                    Measure.[Stockpile FCST W_Simulated G/R] = ${parsedParams.fb_Gr};
                    Measure.[Stockpile FCST W_Simulated Demand] = ${parsedParams.simulDmd};
                end scope;
            `;
            // Log.Info("##########################executeCartesianSimulatedDemand:: "+query);
            return daCommon.executeQuery('executeCartesianSimulatedDemand', query);
        };

    }
    
    return {
        fn_SubmitStockpileForecastGRUpdate : daCommon.fn_decorator(fn_SubmitStockpileForecastGRUpdate),
    };
});