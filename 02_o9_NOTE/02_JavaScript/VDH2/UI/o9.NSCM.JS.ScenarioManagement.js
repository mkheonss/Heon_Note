define('o9.NSCM.JS.ScenarioManagement', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.ScenarioManagement';
    /* jsErrorMsg   */
    const jsErrorMsg = 'An error occurred during the Scenario Management. \n Please contact the system administrator.';
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

    /*  Master Plan	Simulation > Master Data > Scenario Management 
        Action Button > ABSetBizCase > ds_BizCase 호출
    */
    let fn_bizCaseCombo = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        const resultSet = QueryCommon.selectBizCaseMaster(parsedParams);

        /* property를 DisplayAlias 변환*/
        let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Biz Case", "Biz Case", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(returnSet, {DimName : "Biz Case", DimAttbName : "Biz Case", Sort : "Name", isDisplayNameWithCode : true});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    }


    /*  Master Plan	Simulation > Master Data > Scenario Management 
        Action Button > ABSetBizCase > Submit 버튼 실행
    */
    let fn_SubmitSetBizCase = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserId();


        if (parsedParams.fb_BizCase.startsWith('BC_')) {
            if (parsedParams.fb_BizCaseAsIs === '-') {
                Log.Info("########################## Biz Case ID가 BC_로 시작하며 BizCaseAsIs가 -임");
                // 기존 Biz Case ID 에 해당하는 ASN 값 Null 처리
                QueryCommon.executeUpdateScenarioBizCaseAsn(parsedParams);

                // 새로 선택한 Biz Case ID에 해당하는 ASN 값 1 처리, Created 정보 기록
                QueryCommon.executeCartesianScenarioBizCaseAsn(parsedParams, true);

                // Scenario Master Update 정보 갱신
                QueryCommon.executeUpdateScenarioMaster(parsedParams);

            } else {
                Log.Info("########################## Biz Case ID가 BC_로 시작하지만 BizCaseAsIs가 -가 아님");
                // 기존 Biz Case ID 에 해당하는 ASN 값 Null 처리
                QueryCommon.executeUpdateScenarioBizCaseAsn(parsedParams);

                // 새로 선택한 Biz Case ID에 해당하는 ASN 값 1 처리, Updated 정보 기록
                QueryCommon.executeCartesianScenarioBizCaseAsn(parsedParams, false);

                // Scenario Master Update 정보 갱신
                QueryCommon.executeUpdateScenarioMaster(parsedParams);
            }
        } else {
            Log.Info("########################## Biz Case ID가 BC_로 시작하지 않음");
        }
    }


    let fn_ValidationUseCase =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;

        daUtil.fn_validationMultiRowCheck(tupleList);
    }


    let fn_ValidationScenarioStatus = (o9Params) => {
        const parsedParams = JSON.parse(o9Params);
        const tupleList = parsedParams.fb_TupleList;
        let returnValue = 0; // 0: 정상, 1: 오류메세지

        fb_cfScenario

        // Extract scenario from the fb_TupleList
        parsedParams.scenarioValue = parsedParams.fb_cfScenario;
        Log.Info("########################## parsedParams.scenarioValue:: ", tupleList.fb_Scenario);

        const resultSet = QueryCommon.selectScenarioStatus(parsedParams);
        const scenarioStatus = daCommon.getMeasureValue(resultSet.cs, 0, "Scenario Master_Scenario Status");

        // Check if the scenarioStatus value contains "not editable"
        if (scenarioStatus && scenarioStatus.toLowerCase().includes("not editable")) {
            RuleOutputToUI = { Status: 'Error', Message: "Scenario Status: Not Editable" };
            returnValue = 1;
        }

        return returnValue;
    };



    class QueryCommon {

        static selectBizCaseMaster(params) {
            let query = `
                select ([Version].[Version Name].[CWV_MP] * [Biz Case].[Biz Case] ) on row, 
                ({Measure.[Biz Case Master_Created By], 
                 Measure.[Biz Case Master_Creation Time], 
                 Measure.[Biz Case Master_Update Time], 
                 Measure.[Biz Case Master_Updated By]}
                ) on column;
            `;
            return daCommon.selectQueryList('selectBizCaseMaster', query);
        }

        static selectScenarioStatus(params) {
            let query = `
                select ([Version].[Version Name].[CWV_MP] * [Biz Case].[${params.scenarioValue}] ) on row, 
                ({Measure.[Scenario Master_Scenario Status]}
                ) on column;
            `;
            return daCommon.selectQueryList('selectScenarioStatus', query);
        }

        static executeCartesianScenarioBizCaseAsn(parsedParams, isCreate = false) {
            let query = `
                cartesian scope: (
                    [Version].[Version Name].[CWV_MP]
                    * [Scenario].[Scenario].[${parsedParams.fb_Scenario}]
                    * [Biz Case].[Biz Case].[${parsedParams.fb_BizCase}]
                );
                Measure.[Scenario Biz Case Asn_Asn] = "1";
                ${isCreate ? 
                    `Measure.[Scenario Biz Case Asn_Creation Time] = dateadd(Now(),0,"hour");
                    Measure.[Scenario Biz Case Asn_Created By] = "${parsedParams.userId}";` 
                    : 
                    `Measure.[Scenario Biz Case Asn_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[Scenario Biz Case Asn_Updated By] = "${parsedParams.userId}";`}
                end scope;
            `;
            // Log.Info("########################## executeCartesianScenarioBizCaseAsn:: "+query);
            return daCommon.executeQuery('executeCartesianScenarioBizCaseAsn', query);
        }

        static executeUpdateScenarioBizCaseAsn(parsedParams) {
            let query =`
                scope: (
                    [Version].[Version Name].[CWV_MP]
                    * [Scenario].[Scenario].[${parsedParams.fb_Scenario}]
                    * [Biz Case].[Biz Case].[${parsedParams.fb_BizCaseAsIs}]
                );
                    Measure.[Scenario Biz Case Asn_Asn] = Null;
                    Measure.[Scenario Biz Case Asn_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[Scenario Biz Case Asn_Updated By] = "${parsedParams.userId}";
                end scope;
                `
            // Log.Info("########################## executeUpdateScenarioBizCaseAsn:: "+query);
            return daCommon.executeQuery('executeUpdateScenarioBizCaseAsn', query);
        };

        static executeUpdateScenarioMaster(parsedParams) {
            let query =`
                scope: (
                    [Version].[Version Name].[CWV_MP]
                    * [Scenario].[Scenario].[${parsedParams.fb_Scenario}]
                );
                    Measure.[Scenario Master_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[Scenario Master_Updated By] = "${parsedParams.userId}";
                end scope;
                `
            // Log.Info("########################## executeUpdateScenarioMaster:: "+query);
            return daCommon.executeQuery('executeUpdateScenarioMaster', query);
        };

    }

    return {
        fn_bizCaseCombo : daCommon.fn_decorator(fn_bizCaseCombo)
        , fn_SubmitSetBizCase: daCommon.fn_decorator(fn_SubmitSetBizCase)
        , fn_ValidationUseCase: daCommon.fn_decorator(fn_ValidationUseCase)
        , fn_ValidationScenarioStatus: daCommon.fn_decorator(fn_ValidationScenarioStatus)
    };
});