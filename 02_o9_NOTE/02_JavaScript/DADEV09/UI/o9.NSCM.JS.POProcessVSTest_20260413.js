define('o9.NSCM.JS.POProcessVSTest', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.POProcessVSTest
     *
     * Test for validation and simulation in PO Process
     */

    /******************************************************************************************************************/
    /* SET CONST ******************************************************************************************************/

    /* Program Name */
    const programName = "o9.NSCM.JS.POProcessVSTest";
    /* jsErrorMsg   */
    const jsErrorMsg = "Please contact the system administrator.";

    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    let daUtil = new commonLib.DAUtil();

    /* set flag to print log */
    const infLogFlag = true;
    const errLogFlag = true;

    /* set action type */
    const ACTION_TYPE = {
        MASTER_COPY : 'MST_COPY',
        MASTER_DELETE : 'MST_DEL',
        MASTER_EDIT : 'MST_EDIT',
        DETAIL_DELETE : 'DTL_DEL'
    };

    /* SET CONST ******************************************************************************************************/
    /******************************************************************************************************************/

    /******************************************************************************************************************/
    /* QUERY COMMON START *********************************************************************************************/

    class QueryCommon{
        static deletePOCalMaster(parsedParams) {
            let query =
                ` Delete data for model [Loading PO Cal Master] where {[Version].[Version Name].[CWV_MP]}; `;

            daCommon.executeQuery('deletePOCalMaster', query);
        }

        static nullifyPOProcessValidation(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]` +
                     ` * [Delivery Week].[Delivery Week]);` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(${parsedParams.fb_Step})] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(FINAL)] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(FINAL)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(FINAL)] = null;` +
                ` end scope; `;

            daCommon.executeQuery('nullifyPOProcessValidation', query);
        }

        static nullifyPOProcessValidationAll(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]` +
                     ` * [Delivery Week].[Delivery Week]);` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(P)] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(P)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(P)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(P)] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(P)] = null;` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(M)] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(M)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(M)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(M)] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(M)] = null;` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(ADJ1)] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(ADJ1)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(ADJ1)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(ADJ1)] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(ADJ1)] = null;` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(ADJ2)] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(ADJ2)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(ADJ2)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(ADJ2)] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(ADJ2)] = null;` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(ADJ3)] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(ADJ3)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(ADJ3)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(ADJ3)] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(ADJ3)] = null;` +
                     ` Measure.[PO Process_Item Unit Load Mix Match Chk(FINAL)] = null; ` +
                     ` Measure.[PO Process_Item Unit Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match Chk(FINAL)] = null;` +
                     ` Measure.[PO Process_Lane Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process_Valid Fail Reason(FINAL)] = null;` +
                ` end scope; `;

            daCommon.executeQuery('nullifyPOProcessValidationAll', query);
        }

        static nullifyPOProcessDetailValidation(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week] );` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(FINAL)] = null;` +
                ` end scope;`;

            daCommon.executeQuery('nullifyPOProcessDetailValidation', query);
        }

        static nullifyPOProcessDetailValidationAll(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week] );` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(P)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(P)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(P)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(P)] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(P)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(M)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(M)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(M)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(M)] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(M)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Lane Load Mix Match(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Valid Fail Reason(FINAL)] = null;` +
                ` end scope;`;

            daCommon.executeQuery('nullifyPOProcessDetailValidationAll', query);
        }

        static nullifyPOProcessSimulation(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]` +
                     ` * [SOP Week].[SOP Week] * [Delivery Week].[Delivery Week]);` +
                     ` Measure.[PO Process_Loading Status(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Loading Qty(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Diff Qty(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Item FR(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_CNTR FR(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process_Check Qty(FINAL)] = null; ` +
                     ` Measure.[PO Process_Loading Status(FINAL)] = null;` +
                     ` Measure.[PO Process_Loading Qty(FINAL)] = null;` +
                     ` Measure.[PO Process_Diff Qty(FINAL)] = null;` +
                     ` Measure.[PO Process_Item FR(FINAL)] = null;` +
                     ` Measure.[PO Process_CNTR FR(FINAL)] = null;` +
                     ` Measure.[PO Process_Simulation Time] = null;` +
                     ` Measure.[PO Process_Simulated By] = null;` +
                ` end scope;`;

            daCommon.executeQuery('nullifyPOProcessSimulation', query);
        }

        static nullifyPOProcessSimulationAll(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]` +
                     ` * [SOP Week].[SOP Week] * [Delivery Week].[Delivery Week]);` +
                     ` Measure.[PO Process_Loading Status(P)] = null;` +
                     ` Measure.[PO Process_Loading Qty(P)] = null;` +
                     ` Measure.[PO Process_Diff Qty(P)] = null;` +
                     ` Measure.[PO Process_Item FR(P)] = null;` +
                     ` Measure.[PO Process_CNTR FR(P)] = null;` +
                     ` Measure.[PO Process_Check Qty(M)] = null; ` +
                     ` Measure.[PO Process_Loading Status(M)] = null;` +
                     ` Measure.[PO Process_Loading Qty(M)] = null;` +
                     ` Measure.[PO Process_Diff Qty(M)] = null;` +
                     ` Measure.[PO Process_Item FR(M)] = null;` +
                     ` Measure.[PO Process_CNTR FR(M)] = null;` +
                     ` Measure.[PO Process_Check Qty(ADJ1)] = null; ` +
                     ` Measure.[PO Process_Loading Status(ADJ1)] = null;` +
                     ` Measure.[PO Process_Loading Qty(ADJ1)] = null;` +
                     ` Measure.[PO Process_Diff Qty(ADJ1)] = null;` +
                     ` Measure.[PO Process_Item FR(ADJ1)] = null;` +
                     ` Measure.[PO Process_CNTR FR(ADJ1)] = null;` +
                     ` Measure.[PO Process_Check Qty(ADJ2)] = null; ` +
                     ` Measure.[PO Process_Loading Status(ADJ2)] = null;` +
                     ` Measure.[PO Process_Loading Qty(ADJ2)] = null;` +
                     ` Measure.[PO Process_Diff Qty(ADJ2)] = null;` +
                     ` Measure.[PO Process_Item FR(ADJ2)] = null;` +
                     ` Measure.[PO Process_CNTR FR(ADJ2)] = null;` +
                     ` Measure.[PO Process_Check Qty(ADJ3)] = null; ` +
                     ` Measure.[PO Process_Loading Status(ADJ3)] = null;` +
                     ` Measure.[PO Process_Loading Qty(ADJ3)] = null;` +
                     ` Measure.[PO Process_Diff Qty(ADJ3)] = null;` +
                     ` Measure.[PO Process_Item FR(ADJ3)] = null;` +
                     ` Measure.[PO Process_CNTR FR(ADJ3)] = null;` +
                     ` Measure.[PO Process_Check Qty(FINAL)] = null; ` +
                     ` Measure.[PO Process_Loading Status(FINAL)] = null;` +
                     ` Measure.[PO Process_Loading Qty(FINAL)] = null;` +
                     ` Measure.[PO Process_Diff Qty(FINAL)] = null;` +
                     ` Measure.[PO Process_Item FR(FINAL)] = null;` +
                     ` Measure.[PO Process_CNTR FR(FINAL)] = null;` +
                     ` Measure.[PO Process_Simulation Time] = null;` +
                     ` Measure.[PO Process_Simulated By] = null;` +
                ` end scope;`;

            daCommon.executeQuery('nullifyPOProcessSimulationAll', query);
        }

        static nullifyPOProcessDetailSimulation(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]);` +
                     ` Measure.[PO Process Detail_Loading Status(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_Item FR(${parsedParams.fb_Step})] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(${parsedParams.fb_Step})] = null;`;
                if (parsedParams.fb_NextStep !== null && parsedParams.fb_NextStep !== "") {
                     query = query +
                         ` Measure.[PO Process Detail_Check Qty(${parsedParams.fb_NextStep})] = null; `;
                }
                query = query +
                     ` Measure.[PO Process Detail_Check Qty(FINAL)] = null; ` +
                     ` Measure.[PO Process Detail_Loading Status(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Item FR(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Simulation Time] = null;` +
                     ` Measure.[PO Process Detail_Simulated By] = null;` +
                ` end scope;`;

            daCommon.executeQuery('nullifyPOProcessDetailSimulation', query);
        }

        static nullifyPOProcessDetailSimulationAll(parsedParams) {
            let query =
                ` Scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]);` +
                     ` Measure.[PO Process Detail_Loading Status(P)] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(P)] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(P)] = null;` +
                     ` Measure.[PO Process Detail_Item FR(P)] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(P)] = null;` +
                     ` Measure.[PO Process Detail_Loading Status(M)] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(M)] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(M)] = null;` +
                     ` Measure.[PO Process Detail_Item FR(M)] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(M)] = null;` +
                     ` Measure.[PO Process Detail_Check Qty(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Loading Status(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Item FR(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(ADJ1)] = null;` +
                     ` Measure.[PO Process Detail_Check Qty(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Loading Status(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Item FR(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(ADJ2)] = null;` +
                     ` Measure.[PO Process Detail_Check Qty(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Loading Status(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Item FR(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(ADJ3)] = null;` +
                     ` Measure.[PO Process Detail_Check Qty(FINAL)] = null; ` +
                     ` Measure.[PO Process Detail_Loading Status(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Loading Qty(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Diff Qty(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Item FR(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_CNTR FR(FINAL)] = null;` +
                     ` Measure.[PO Process Detail_Simulation Time] = null;` +
                     ` Measure.[PO Process Detail_Simulated By] = null;` +
                ` end scope;`;

            daCommon.executeQuery('nullifyPOProcessDetailSimulationAll', query);
        }

        static deletePOContainerPlan(parsedParams) {
            let query =
                ` Delete data for model [Loading PO Container Plan]` +
                 ` where {[Version].[Version Name].[CWV_MP]` +
                      `, [Plan Step].[Plan Step].filter(#.Name in {${parsedParams.fb_Step}, FINAL})}; `;

            daCommon.executeQuery('deletePOContainerPlan', query);
        }

        static deletePOContainerPlanAll(parsedParams) {
            let query =
                ` Delete data for model [Loading PO Container Plan]` +
                 ` where {[Version].[Version Name].[CWV_MP]}; `;

            daCommon.executeQuery('deletePOContainerPlanAll', query);
        }

        static execValidation(parsedParams) {
            let query =
                ` EXEC plugin instance [PY_UI_POProcessValidNLoad_REG]` +
                     ` for measures { [PO Process_Valid Fail Reason(P)] }` +
                     ` using scope ([Version].[Version Name].[CWV_MP])` +
                     ` using arguments {(ExecutionMode, "MediumWeight")` +
                                    `, (Param_OUT_VERSION, "CWV_MP")` +
                                    `, (Param_Exception_Flag, "N")` +
                                    `, (Param_Step, "${parsedParams.fb_Step}")` +
                                    `, (MaxSliceTableCells, 200000000)` +
                                    `, (MaxConcurrency, 1)` +
                                    `, (IncludeNullRows, False)` +
                                    `, ([Param.o9_sys_log_level], "DEBUG")` +
                                    `};`;

            daCommon.executeQuery('execValidation', query);
        }

        static execSimulation(parsedParams) {
            let query =
                ` EXEC plugin instance [PY_UI_POProcessNoneSKU_REG]` +
                     ` for measures { [PO Process Detail_Simulated By] }` +
                     ` using scope ([Version].[Version Name].[CWV_MP])` +
                     ` using arguments {(ExecutionMode, "MediumWeight")` +
                                    `, (Param_OUT_VERSION, "CWV_MP")` +
                                    `, (Param_Exception_Flag, "N")` +
                                    `, (Param_Adjust_Option1, "MAX")` +
                                    `, (Param_Adjust_Option2, "Max Profit")` +
                                    `, (Param_User_Name, "${daCommon.fn_getUserId()}")` +
                                    `, (Param_Step, "${parsedParams.fb_Step}")` +
                                    `, (MaxSliceTableCells, 200000000)` +
                                    `, (MaxConcurrency, 1)` +
                                    `, (IncludeNullRows, False)` +
                                    `, ([Param.o9_sys_log_level], "DEBUG")` +
                                    `};`;
            daCommon.executeQuery('execSimulation', query);
        }

        static updateLastStepP(parsedParams) {
            let query =
                ` scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]);` +
                     ` Measure.[PO Process Detail_Last Step] = if (Measure.[PO Process Detail_Chk Last Step(P)] == "Y")` +
                                                             ` then 1 else 2;`+
                  ` end scope;`;

            daCommon.executeQuery('updateLastStepP', query);
        }

        static updateLastStepE(parsedParams) {
            let query =
                ` scope: ([Version].[Version Name].[CWV_MP] * [Sub Location].[Sub Location] * [Seq].[Seq]` +
                     ` * [Item].[Item] * [Location].[Location] * [Time].[Week] * [MFG Week].[MFG Week]);` +
                     ` Measure.[PO Process Detail_Last Step] = if (Measure.[PO Process Detail_Last Step] ==` +
                                                                ` ${parsedParams.fb_LastStep})` +
                                                             ` then ${parsedParams.fb_CurStep}` +
                                                             ` else Measure.[PO Process Detail_Last Step];`+
                  ` end scope;`;
        }
    }
    /* QUERY COMMON END ***********************************************************************************************/
    /******************************************************************************************************************/

    /******************************************************************************************************************/
    /* Inner Function START *******************************************************************************************/

    /* Inner Function END *********************************************************************************************/
    /******************************************************************************************************************/

    /******************************************************************************************************************/
    /* Transaction START **********************************************************************************************/

    let fn_executeTest = function (o9Params) {
        daCommon.infLog(`[fn_executeTest] o9Params:${o9Params}`, infLogFlag);
        let parsedParams = JSON.parse(o9Params);
        daCommon.infLog(`[fn_executeTest] parsedParams:${JSON.stringify(parsedParams)}`);

        parsedParams.fb_NextStep = "";
        if (parsedParams.fb_Step === "ALL") {
            QueryCommon.nullifyPOProcessSimulationAll(parsedParams);
            QueryCommon.nullifyPOProcessDetailSimulationAll(parsedParams);
            QueryCommon.deletePOContainerPlanAll(parsedParams);
            QueryCommon.updateLastStepP(parsedParams);
            if (parsedParams.fb_Option === "1") {
                // 전체 step에 대해서 validation 데이터 초기화
                QueryCommon.deletePOCalMaster(parsedParams);
                QueryCommon.nullifyPOProcessValidationAll(parsedParams);
                QueryCommon.nullifyPOProcessDetailValidationAll(parsedParams);
            }
        } else {
            if (parsedParams.fb_Step === "P") {
                parsedParams.fb_NextStep = "";
                parsedParams.fb_LastStep = 1;
                parsedParams.fb_CurStep = 0;
            } else if (parsedParams.fb_Step === "M") {
                parsedParams.fb_NextStep = "ADJ1";
                parsedParams.fb_LastStep = 2;
                parsedParams.fb_CurStep = 1;
            } else if (parsedParams.fb_Step === "ADJ1") {
                parsedParams.fb_NextStep = "ADJ2";
                parsedParams.fb_LastStep = 3;
                parsedParams.fb_CurStep = 2;
            } else if (parsedParams.fb_Step === "ADJ2") {
                parsedParams.fb_NextStep = "ADJ3";
                parsedParams.fb_LastStep = 4;
                parsedParams.fb_CurStep = 3;
            } else if (parsedParams.fb_Step === "ADJ3") {
                parsedParams.fb_NextStep = "";
                parsedParams.fb_LastStep = 5;
                parsedParams.fb_CurStep = 4;
            }
            // 선택한 step에 대해서 simulation 데이터 초기화
            QueryCommon.nullifyPOProcessSimulation(parsedParams);
            QueryCommon.nullifyPOProcessDetailSimulation(parsedParams);
            QueryCommon.deletePOContainerPlan(parsedParams);
            if (parsedParams.fb_CurStep === 0) {
                QueryCommon.updateLastStepP(parsedParams);
            } else {
                QueryCommon.updateLastStepE(parsedParams);
            }
            if (parsedParams.fb_Option === "1") {
                // 선택한 step에 대해서 Validation 데이터 초기화
                QueryCommon.deletePOCalMaster(parsedParams);
                QueryCommon.nullifyPOProcessValidation(parsedParams);
                QueryCommon.nullifyPOProcessDetailValidation(parsedParams);
            }
        }
    };

    /* Transaction END ************************************************************************************************/
    /******************************************************************************************************************/

    return {
        fn_executeTest : daCommon.fn_decorator(fn_executeTest)
    };

});