define('o9.NSCM.JS.OceanContractMgmt', ['o9.NSCM.commonLibDA'], function(commonLib){
    /**
     * o9.NSCM.JS.OceanContractMgmt.
     *
     * OceanContractMgmt 공용
     * 
     * Master Data > Logistics > Ocean Contract Mgmt > Ocean Contract Mgmt
     */

    /*********************************************************************/
    /**************************** const 설정 *****************************/
    /*********************************************************************/

    /* programName */
    const programName = "o9.NSCM.JS.OceanContractMgmt";

    /* setting  */
    // let commonLib = require('o9.NSCM.JScommon_DA');
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

    /* jsErrorMsg */
    const jsErrorMsg = "Please contact the system administrator.";

    /* set flag to print log */
    const infLogFlag = true;
    
    /**
     * Logs the given message.
     *
     * @param {string} msg - The message to be logged.
     * @returns {void}
     */
    let log = function(msg) {
        daCommon.debug(msg);
    };

    /* infLog */
    let infLog = function (msg, printFlag) {
        if (printFlag) {
            let logMsg = `${this.preFix}[${this.programName}] ${msg}`;
            Log.Info(logMsg);
        }
    };

    /* errLog */
    let errLog = function (msg, printFlag) {
        if (printFlag) {
            let logMsg = `${this.errorPreFix}[${this.programName}] ${msg}`;
            Log.Error(logMsg);
        }
    };

    /*******************************************************************************/
    /**************************** combo list 구성 함수 ******************************/
    /*******************************************************************************/

    let fn_LoadingPortCombo = function(o9Params) {
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        const resultSet = QueryCommon.selectLoadingPort(parsedParams);

        // /* property를 DisplayAlias 변환*/
        // let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Group", "Group ID", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Loading Port",
                DimAttbName : "Loading SCM Port",
                Sort : "DisplayName",
                isDisplayNameWithCode : false});

        return comboList;
    };

    
    let fn_DischargePortCombo = function(o9Params) {
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        const resultSet = QueryCommon.selectDischargePort(parsedParams);

        // /* property를 DisplayAlias 변환*/
        // let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Group", "Group ID", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Discharge Port",
            DimAttbName : "Discharge SCM Port",
            Sort : "DisplayName",
            isDisplayNameWithCode : false});

        return comboList;
    };

    let fn_DestPortCombo = function(o9Params) {
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        const resultSet = QueryCommon.selectDestPort(parsedParams);

        // /* property를 DisplayAlias 변환*/
        // let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Group", "Group ID", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Dest Port",
            DimAttbName : "Dest SCM Port",
            Sort : "DisplayName",
            isDisplayNameWithCode : false});

        return comboList;
    };
    


    /*******************************************************************************/
    /**************************** combo list END ***********************************/
    /*******************************************************************************/

    /*******************************************************************************/
    /**************************** TRANSACTION START ********************************/
    /*******************************************************************************/
    let fn_AddOceanContract = function(o9Params){
        try {
            daCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);

            // validation
            let iFromWeek = parseInt(parsedParams.fb_FromWeek);
            let iToWeek = parseInt(parsedParams.fb_ToWeek);
            if(iFromWeek > iToWeek){
                RuleOutputToUI = {Status: 'Error', Message: '"From Week" cannot be greater than "To Week".'};
                return;
            }



            // 0.중복 검사
            let dimensionOceanContract = [
                `[Version].[Version Name].[${parsedParams.fb_Version}]`
                , `[Time].[Planning Quarter].[${parsedParams.fb_ContractQuarter}]`
                , `[Carrier].[Carrier].[${parsedParams.fb_Carrier}]`
                , `[Loading Port].[Loading SCM Port].[${parsedParams.fb_LoadingNSCMPortCode}]`
                , `[Discharge Port].[Discharge SCM Port].[${parsedParams.fb_DischargeNSCMPortCode}]`
                , `[Dest Port].[Dest SCM Port].[${parsedParams.fb_DestNSCMPortCode}]`
            ];

            let measureQuery = ["Measure.[Ocean Contract_Created By]"];
            let iCountExist = daCommon.selectListCount(dimensionOceanContract,measureQuery,"");

            if(iCountExist > 0) {
                RuleOutputToUI = {Status: 'Error', Message: "Contract is duplicated."};
                return;
            }

            let countCarrier = `[Carrier].[Carrier].[${parsedParams.fb_Carrier}]`;
            let cntDimensionCarrier = daCommon.selectCount(countCarrier);

            if (cntDimensionCarrier === 0) {
                //createmember
                // infLog(`##########################createmember 전 cntDimensionScenario:: ${cntDimensionScenario} `, infLogFlag);
                
                let creatMemberCarrier = `createmember([Carrier].[Carrier] = {, "${parsedParams.fb_Carrier}"});`;
                daCommon.executeQuery('creatMemberCarrier', creatMemberCarrier);

                // infLog(`##########################createmember 후 cntDimensionScenario:: ${cntDimensionScenario} `, infLogFlag);
            }



            let sUserName = daCommon.fn_getUserName();
            let measure = [
                `Measure.[Ocean Contract_Capa Qty] = "${parsedParams.fb_CapaPerWeek}";`
                ,`Measure.[Ocean Contract_Delivery Term] = "${parsedParams.fb_DeliveryTerm}";`
                ,`Measure.[Ocean Contract_From Week] = "${parsedParams.fb_FromWeek}";`
                ,`Measure.[Ocean Contract_To Week] = "${parsedParams.fb_ToWeek}";`
                ,`Measure.[Ocean Contract_Route Type] = "${parsedParams.fb_RouteType}";`
                ,`Measure.[Ocean Contract_Creation Time] = dateadd(Now(),0,"hour");`
                ,`Measure.[Ocean Contract_Created By] = "${sUserName}";`
            ];

            // infLog(`##########################createMeasure 1번실행 fbBizCase:: ${fbBizCase} `, infLogFlag);
            daCommon.createMeasure(dimensionOceanContract, measure);

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    let fn_DeleteOceanContract = function(o9Params) {
        try {
            daCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);

            infLog("##########################fn_DeleteOceanContract start:: "+parsedParams.fb_Version);

            let tupleList = parsedParams.fb_TupleList;
            
            tupleList.forEach(element => {

                parsedParams.fb_Version = parsedParams.fb_Version;
                parsedParams.fb_PlanningQuarter = element.fb_PlanningQuarter.Value;
                parsedParams.fb_Carrier = element.fb_Carrier.Value;
                parsedParams.fb_LoadingNSCMPortCode = element.fb_LoadingNSCMPortCode.Value;
                parsedParams.fb_DischargeNSCMPortCode = element.fb_DischargeNSCMPortCode.Value;
                parsedParams.fb_DestNSCMPortCode = element.fb_DestNSCMPortCode.Value;

                QueryCommon.deleteOceanContract(parsedParams);
            });
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };


    let fn_GenerateOceanContract = function(o9Params) {
        try {
            daCommon.printParams(o9Params);

            var parsedParams = JSON.parse(o9Params);

            infLog("##########################deleteOceanCapaWCapaQty start:: "+parsedParams.fb_Version);
            QueryCommon.deleteOceanCapaWCapaQty(parsedParams);
            infLog("##########################deleteOceanCapaWCapaQty end:: "+parsedParams.fb_Version);

            infLog("##########################executePYLogisticsOceanContractMgmt start:: "+parsedParams.fb_Version);
            QueryCommon.executePYLogisticsOceanContractMgmt(parsedParams);
            infLog("##########################executePYLogisticsOceanContractMgmt end:: "+parsedParams.fb_Version);

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

    };



    /*  
        fn_ValidationMultiSelect : Multirow check 후 copy 버튼 클릭 시 retrun 1
    */
    let fn_ValidationMultiSelect =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;

        daUtil.fn_validationMultiRowCheck(tupleList);
    };

    /*******************************************************************************/
    /**************************** QUERY COMMON START *******************************/
    /*******************************************************************************/
    class QueryCommon {

        /*  
            selectLoadingPort : Loading Port 콤보 쿼리
        */
        static selectLoadingPort(params) {
            let query =
            //// ABOceanContractMgmtAdd // ds_LoadingPort // Loading Port
            `select ([Loading Port].[Loading Port]*[Loading Port].[Loading SCM Port]) on row,
                ({Measure.[Loading Port Mapping_Status]}) on column
            where {
                    Version.[Version Name].[CWV_MP],
                    Measure.[Loading Port Mapping_Valid Flag]=="Y",
                    Measure.[Loading Port Mapping_Status]=="CON"
            }
            orderby [Loading Port].[Loading SCM Port].DisplayName asc;
            `;
            return daCommon.selectQueryList('selectLoadingPort', query);
        }

        /*  
            selectDischargePort : Discharge Port 콤보 쿼리
        */
        static selectDischargePort(params) {
            let query =
                //// ABOceanContractMgmtAdd // ds_DischargePort // Discharge Port
            `select ([Discharge Port].[Discharge Port]*[Discharge Port].[Discharge SCM Port]) on row,
                    ({Measure.[Discharge Port Mapping_Status]}) on column
            where {
                    Version.[Version Name].[CWV_MP],
                    Measure.[Discharge Port Mapping_Valid Flag]=="Y",
                    Measure.[Discharge Port Mapping_Status]=="CON"
            }
            orderby [Discharge Port].[Discharge SCM Port].DisplayName asc;
            `;
            return daCommon.selectQueryList('selectDischargePort', query);
        }

        /*  
            selectDestPort : Dest Port 콤보 쿼리
        */
            static selectDestPort(params) {
            let query =
                //// ABOceanContractMgmtAdd // ds_DestPort // Dest Port
            `select ([Dest Port].[Dest Port]*[Dest Port].[Dest SCM Port]) on row,
                    ({Measure.[Dest Port Mapping_Status]}) on column
            where {
                    Version.[Version Name].[CWV_MP],
                    Measure.[Dest Port Mapping_Valid Flag]=="Y",
                    Measure.[Dest Port Mapping_Status]=="CON"
            }
            orderby [Dest Port].[Dest SCM Port].DisplayName asc;
            `;
            return daCommon.selectQueryList('selectDestPort', query);
        }

        /*  
            deleteOceanContract : Delete Contract Mgmt의 Submit 버튼 클릭시 delete data model
        */
            static deleteOceanContract(parsedParams) {
                let query = `
                    delete data for model [Ocean Contract]
                    where {
                        [Version].[Version Name].[${parsedParams.fb_Version}],
                        [Carrier].[Carrier].[${parsedParams.fb_Carrier}],
                        [Time].[Planning Quarter].[${parsedParams.fb_PlanningQuarter}],
                        [Loading Port].[Loading SCM Port].[${parsedParams.fb_LoadingNSCMPortCode}],
                        [Discharge Port].[Discharge SCM Port].[${parsedParams.fb_DischargeNSCMPortCode}],
                        [Dest Port].[Dest SCM Port].[${parsedParams.fb_DestNSCMPortCode}]
                    };
                `;
                infLog("##########################deleteOceanContract:: "+query);
                return daCommon.executeQuery('deleteOceanContract', query);
            };

        /*  
            deleteOceanCapaWCapaQty : Delete Contract Mgmt의 generate 버튼 클릭시 delete data model
        */
            static deleteOceanCapaWCapaQty(parsedParams) {
                let query = `
                    delete data for model [Ocean Capacity W]
                    where {
                        [Version].[Version Name].[${parsedParams.fb_Version}]
                    };
                `;
                return daCommon.executeQuery('deleteOceanCapaWCapaQty', query);
            };
        /*
            executePYLogisticsOceanContractMgmt: generate 의 python 호출
        */
            static executePYLogisticsOceanContractMgmt(parsedParams){
                let query =
                    `EXEC plugin instance [PY_Logistics_Ocean_Contract_Mgmt]
                    for measures {[Ocean Capa W_Capa Qty]}
                        using scope ([Version].[Version Name].[${parsedParams.fb_Version}])
                        using arguments {
                            (ExecutionMode, "MediumWeight")
                            , ([FailedExecutionCount],1)
                            , ([FailedExecutionPercent],0.0)
                            , ([ThrowExceptionOnFailure],true)
                            , ([MaxSliceTableCells],2000000000)
                            , ("IncludeNullRows","False")
                            , (Param_OUT_VERSION, "${parsedParams.fb_Version}")
                        };`
                return daCommon.executeQuery('executePYLogisticsOceanContractMgmt', query);
            }
    }
    /*******************************************************************************/
    /**************************** QUERY COMMON END *********************************/
    /*******************************************************************************/

    /*******************************************************************************/
    /****************** return start o9.NSCM.JS.OceanContractMgmt *****************/
    /*******************************************************************************/
    return{
        fn_LoadingPortCombo : daCommon.fn_decorator(fn_LoadingPortCombo)
        , fn_DischargePortCombo : daCommon.fn_decorator(fn_DischargePortCombo)
        , fn_DestPortCombo : daCommon.fn_decorator(fn_DestPortCombo)
        , fn_AddOceanContract : daCommon.fn_decorator(fn_AddOceanContract)
        , fn_DeleteOceanContract : daCommon.fn_decorator(fn_DeleteOceanContract)
        , fn_GenerateOceanContract : daCommon.fn_decorator(fn_GenerateOceanContract)
        , fn_ValidationMultiSelect : daCommon.fn_decorator(fn_ValidationMultiSelect)
    };
    /*******************************************************************************/
    /****************** return end o9.NSCM.JS.OceanContractMgmt *******************/
    /*******************************************************************************/
});