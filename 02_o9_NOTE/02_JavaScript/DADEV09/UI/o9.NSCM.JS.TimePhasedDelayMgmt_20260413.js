define('o9.NSCM.JS.TimePhasedDelayMgmt', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.TimePhasedDelayMgmt';
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
    let fn_SubmitTimePhasedDelayMgmtAdd = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        let iWKFrom = parseInt(parsedParams.fb_WKFrom);
        let iWKTo = parseInt(parsedParams.fb_WKTo);
        if(iWKFrom>iWKTo) {
            RuleOutputToUI = {Status: 'Error', Message: "The WK (From) value cannot be greater than the WK (To) value."};
            return;
        }

        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        resultSet = QueryCommon.selectTimePhasedDelayForSeq(parsedParams);
        if(resultSet.cs.rowCount === 0){
            parsedParams.Seq = 1;
        }else{
            let oldBodNameIdx = daCommon.getMember(resultSet.cs, 0, 'Seq', 'Seq').Name;
            parsedParams.Seq = parseInt(oldBodNameIdx)+1;;
        }
        //Add
        QueryCommon.executeCartesianAddTimePhasedDelay(parsedParams);
    }

    let fn_SubmitTimePhasedDelayMgmtEdit = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        //
        QueryCommon.executeScopeEditTimePhasedDelay(parsedParams)
    }

    class QueryCommon {
        static updateMemberDelayCase(parsedParams) {
            let query =`
                createmember(
                    Group.[Group ID] = {, "${parsedParams.useCaseID}"}, [Group].[Description] = {"${parsedParams.fb_UseCase}", }
                    , Group.[Group Type] = {, "Biz_DMD"}
                );
                `
            // Log.Info("##########################updateMemberGroupIDDescription:: "+query);
            return daCommon.executeQuery('updateMemberDelayCase', query);
        };

        static selectBODNameForActivity1(paramsObj) {
            let query = `
                select (Activity1.Activity1.filter(#.Name == "${paramsObj.bodName}"));
            `;
            // Log.Info("##########################selectBODNameForActivity1:: "+query);
            return daCommon.selectQueryList('selectBODNameForActivity1', query);
        }

        static selectTimePhasedDelayForSeq(parsedParams) {
            let query = `
                Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}]
                    * [Location].[Location].[${parsedParams.fb_ToSite}]
                    * Activity2.[Activity2].[${parsedParams.fb_TransportMode}]
                    * Seq.Seq
                ) on row, 
                ({
                    Measure.[Time Phased Delay_Creation Time]
                }) on column 
                orderby[Seq].[Seq].Key Desc 
                limit 1;
            `;
            // Log.Info("##########################selectBODNameForActivity1:: "+query);
            return daCommon.selectQueryList('selectBODNameForActivity1', query);
        }

        static updateMemberBODNameForActivity1(parsedParams) {
            let query =`
                createmember(
                    Activity1.[Activity1] = {, "${parsedParams.bodName}"}
                    , [Activity1].[Activity1$DisplayName] = {"${parsedParams.bodName}", }
                );
                `
            // Log.Info("##########################updateMemberBODNameForActivity1:: "+query);
            return daCommon.executeQuery('updateMemberBODNameForActivity1', query);
        }

        static executeCartesianAddTimePhasedDelay(parsedParams) {
            let query =`
                cartesian scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}]
                    * [Location].[Location].[${parsedParams.fb_ToSite}]
                    * Activity2.[Activity2].[${parsedParams.fb_TransportMode}]
                    * Seq.Seq.[${parsedParams.Seq}]
                );
                    Measure.[Time Phased Delay_Category] = "${parsedParams.fb_Category}";
                    Measure.[Time Phased Delay_Delay] = ${parsedParams.fb_Delay};
                    Measure.[Time Phased Delay_Delay Code] = "${parsedParams.fb_DelayCode}";
                    Measure.[Time Phased Delay_From Week] = "${parsedParams.fb_WKFrom}";
                    Measure.[Time Phased Delay_Last Apply Date] = Now();
                    Measure.[Time Phased Delay_To Week] = "${parsedParams.fb_WKTo}";
                    Measure.[Time Phased Delay_Created By] = "${parsedParams.userId}";
                    Measure.[Time Phased Delay_Creation Time] = Now();
                end scope;
            `;
            // Log.Info("##########################executeCartesianAddTimePhasedDelay:: "+query);
            return daCommon.executeQuery('executeCartesianAddTimePhasedDelay', query);
        }

        static executeScopeEditTimePhasedDelay(parsedParams) {
            let query =`
                scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].filter(#.DisplayName == "${parsedParams.fb_SiteFrom}")
                    * [Location].[Location].filter(#.DisplayName == "${parsedParams.fb_SiteTo}")
                    * Activity2.[Activity2].[${parsedParams.fb_TransportMode}]
                    * Seq.Seq.[${parsedParams.fb_Seq}]
                );
                    Measure.[Time Phased Delay_Delay Code] = "${parsedParams.fb_DelayCode}";
                    Measure.[Time Phased Delay_Updated By] = "${parsedParams.userId}";
                    Measure.[Time Phased Delay_Update Time] = Now();
                end scope;
            `;
            // Log.Info("##########################executeScopeEditTimePhasedDelay:: "+query);
            return daCommon.executeQuery('executeScopeEditTimePhasedDelay', query);
        }
    }
    
    return {
        fn_SubmitTimePhasedDelayMgmtAdd : daCommon.fn_decorator(fn_SubmitTimePhasedDelayMgmtAdd)
        , fn_SubmitTimePhasedDelayMgmtEdit : daCommon.fn_decorator(fn_SubmitTimePhasedDelayMgmtEdit)
    };
});