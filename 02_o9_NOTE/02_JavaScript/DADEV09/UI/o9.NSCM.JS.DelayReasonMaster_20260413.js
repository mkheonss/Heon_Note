define('o9.NSCM.JS.DelayReasonMaster', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.DelayReasonMaster';
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
    let fn_SubmitDelayReasonMasterAdd = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        let delayCodeArr = [];

        let delayCode = daUtil.fn_trim(parsedParams.fb_Case.toUpperCase()) + " [" + daUtil.fn_trim(parsedParams.fb_Reason.toUpperCase()) + "]";
        
        let resultSet = QueryCommon.selectDelayReason(parsedParams);
        if(resultSet.cs.rowCount !== 0) {
            for(let i=0; i<resultSet.cs.rowCount; i++){
                delayCodeArr.push(daCommon.getMember(resultSet.cs, i, 'Delay Code', 'Delay Code').Name.toUpperCase());
            }
        }

        if(delayCodeArr.includes(delayCode)){
            RuleOutputToUI = { Status : 'Error', Message : "Delay Reason duplicated!!"};
        }else{
            QueryCommon.updateMemberDelayCase(parsedParams);
        }
    }
    

    class QueryCommon {
        static updateMemberDelayCase(parsedParams) {
            let query =`
                createmember(
                    [Delay Code].[Delay Code] = {, "${daUtil.fn_trim(parsedParams.fb_Case)}" + " [" + "${daUtil.fn_trim(parsedParams.fb_Reason)}" + "]"}, [Delay Code].[Delay Case] = {, "${daUtil.fn_trim(parsedParams.fb_Case)}"}, [Delay Code].[Delay Reason] = {, "${daUtil.fn_trim(parsedParams.fb_Reason)}"}
                );

                cartesian scope: (
                    &CWV_MP
                    * [Delay Code].[Delay Code]."${daUtil.fn_trim(parsedParams.fb_Case)} [${daUtil.fn_trim(parsedParams.fb_Reason)}]"
                );
                    //Measure.[Delay Reason Master_Delay Code] = "${daUtil.fn_trim(parsedParams.fb_Case)}" + " [" +"${daUtil.fn_trim(parsedParams.fb_Reason)}" + "]";
                    Measure.[Delay Reason Master_Created By] = CurrentUser().[User Name];
                    Measure.[Delay Reason Master_Creation Time] = Now();
                end scope;
                `
            // Log.Info("##########################updateMemberGroupIDDescription:: "+query);
            return daCommon.executeQuery('updateMemberDelayCase', query);
        };

        static selectDelayReason(parsedParams) {
            let query =`
                    Select (
                        [Version].[Version Name].[${parsedParams.fb_Version}] 
                        * [Delay Code].[Delay Code] 
                    ) on row, 
                    ({
                        Measure.[Delay Reason Master_Creation Time]
                    }) on column;  
                `;
            // Log.Info("##########################selectDelayReason:: "+query);
            return daCommon.selectQueryList('selectDelayReason', query);
        };
    }
    
    return {
        fn_SubmitDelayReasonMasterAdd : daCommon.fn_decorator(fn_SubmitDelayReasonMasterAdd)
    };
});