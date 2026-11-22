define('o9.NSCM.JS.PoProcess', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.PoProcess';
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

    let fn_dsProductGroup = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        let resultSet;

        resultSet = QueryCommon.selectProductGroup(parsedParams);
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        
        return comboList;
    }

    let fn_dsFilterProductGroup = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        parsedParams.fb_Filter_Product = daUtil.fn_multiArr(parsedParams.fb_Filter_Product);
        let resultSet;
        if(false){
            resultSet = QueryCommon.selectProductGroup(parsedParams);
            comboList.unshift({ Name : "All", DisplayName : "All"});
        }else{
            resultSet = QueryCommon.selectFilterProductGroup(parsedParams);
        }
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName", isDisplayNameWithCode : false});
        
        return comboList;
    }

    let fn_dsFilterSubLocation = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        parsedParams.fb_Filter_SubLocation = daUtil.fn_multiArr(parsedParams.fb_Filter_SubLocation);
        let resultSet;
        if(false){
            resultSet = QueryCommon.selectProductGroup(parsedParams);
            comboList.unshift({ Name : "All", DisplayName : "All"});
        }else{
            resultSet = QueryCommon.selectFilterSubLocation(parsedParams);
        }
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", isDisplayNameWithCode : false});
        
        return comboList;
    }

    let fn_dsFilterLocation = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        parsedParams.fb_Filter_Location = daUtil.fn_multiArr(parsedParams.fb_Filter_Location);
        let resultSet;
        if(false){
            resultSet = QueryCommon.selectProductGroup(parsedParams);
            comboList.unshift({ Name : "All", DisplayName : "All"});
        }else{
            resultSet = QueryCommon.selectFilterLocation(parsedParams);
        }
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Location", DimAttbName : "Location", isDisplayNameWithCode : false});
        
        return comboList;
    }

     /* Call Exec Po Simulation : chk 메저 'Y'이고 reason이 null인 건만 자동 수행 */
    let fn_ExecPYUIPOSimulation = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        let resultSet;
        let lastStepMax;
        let lastStepMaxName;
        let stepName = {
            "1": "P"
            , "2": "M"
            , "3": "ADJ1"
            , "4": "ADJ2"
            , "5": "ADJ3"
        };
        let simulExecuteYN = false;
        // Loading Check (Simulation) 배치 수행
        try {
            //FB가 다중 선택이므로 다중 메져값 []붙여서 string return
            if(Array.isArray(parsedParams.fb_Product_Group)){
                parsedParams.fb_Product_Group = daUtil.fn_multiArr(parsedParams.fb_Product_Group);
            }else{
                parsedParams.fb_Product_Group = `[${parsedParams.fb_Product_Group}]`;
            }
            parsedParams.fb_SubLocation = daUtil.fn_multiArr(parsedParams.fb_SubLocation);
            parsedParams.fb_Location = daUtil.fn_multiArr(parsedParams.fb_Location);
            // 사용자 지정 Scope 범위 내의 데이터를 기준 Max(Last Step)을 구하는 쿼리 
            resultSet = QueryCommon.selectScopeLastStepMax(parsedParams);

            if(resultSet.cs.rowCount !== 0) {
                lastStepMax = daCommon.getMeasureValue(resultSet.cs, 0, 'PO Process Detail_Last Step');
                lastStepMaxName = stepName[lastStepMax];
            }else{
                RuleOutputToUI = {Status: 'Error', Message: "The scope setting does not exist in the po process list."};
                return;
            }

            Log.Info("##########################lastStepMaxName:: "+lastStepMaxName);

            switch(parsedParams.fb_ParamStep){
                case "P" :
                    if(lastStepMaxName == "P") {                // 1(P)만 Check Qty상관없이 가능
                        simulExecuteYN = true;
                    }else{                                      // 2~5(M~ADJ3) 무조건 불가능
                        simulExecuteYN = false;
                    }
                    break;
                case "M":
                    if(lastStepMaxName == "M") {                // 2(M)만 Check Qty상관없이 가능
                        simulExecuteYN = true;
                    }else{                                      //1(P), 3~5(ADJ1~ADJ3) 불가능
                        simulExecuteYN = false;
                    }
                    break;
                case "ADJ1":
                    if(lastStepMaxName == "ADJ1") {             // 3(ADJ1)만 Check Qty상관없이 가능
                        simulExecuteYN = true;
                    }else if(lastStepMaxName == "M"){           //2(M) 가능하지만 Check Qty(ADJ1)이 하나라도 채워져 있어야 가능
                        //Check Qty(ADJ1)이 하나라도 채워져 있음을 확인 하는 쿼리
                        resultSet = QueryCommon.selectScopeCheckQtyByStep(parsedParams, "ADJ1");
                        if(resultSet.cs.rowCount !== 0) {
                            simulExecuteYN = true;
                        }else{
                            simulExecuteYN = false;
                        }
                    }else{
                        simulExecuteYN = false;
                    }
                    break;
                case "ADJ2":
                    if(lastStepMaxName == "ADJ2") {             // 4(ADJ2)만 Check Qty상관없이 가능
                        simulExecuteYN = true;
                    }else if(lastStepMaxName == "ADJ1"){           //3(ADJ1) 가능하지만 Check Qty(ADJ2)이 하나라도 채워져 있어야 가능
                        //Check Qty(ADJ2)이 하나라도 채워져 있음을 확인 하는 쿼리
                        resultSet = QueryCommon.selectScopeCheckQtyByStep(parsedParams, "ADJ2");
                        if(resultSet.cs.rowCount !== 0) {
                            simulExecuteYN = true;
                        }else{
                            simulExecuteYN = false;
                        }
                    }else{
                        simulExecuteYN = false;
                    }
                    break;
                case "ADJ3":
                    if(lastStepMaxName == "ADJ3") {             // 5(ADJ3)만 Check Qty상관없이 가능
                        simulExecuteYN = true;
                    }else if(lastStepMaxName == "ADJ2"){           //4(ADJ2) 가능하지만 Check Qty(ADJ3)이 하나라도 채워져 있어야 가능
                        //Check Qty(ADJ3)이 하나라도 채워져 있음을 확인 하는 쿼리
                        resultSet = QueryCommon.selectScopeCheckQtyByStep(parsedParams, "ADJ3");
                        if(resultSet.cs.rowCount !== 0) {
                            simulExecuteYN = true;
                        }else{
                            simulExecuteYN = false;
                        }
                    }else{
                        simulExecuteYN = false;
                    }
                    break;
            }
            Log.Info("##########################simulExecuteYN:: "+simulExecuteYN);
            //simulExecuteYN이 true이면
            if(simulExecuteYN){
                //2-1. 초기화 (Container planning, Cal Master, Po, Po detail 초기화)
                QueryCommon.executeScopeSimulationInitialize(parsedParams);

                //2-2. Validation 실행
                try{
                    QueryCommon.execUIPOProcessValidNLoadREG(parsedParams);
                } catch(e) {
                    throw new Error('Valid Python Error');
                }

                /* Simulation 모듈 파이썬 실행 전후 처리 기능 명세  
                    Valiation 결과를 기준으로 Step 기준으로
                    Item Unit Load Mix Match Chk(Step)이 모두 "Y"이고, 
                    Lane Load Mix Match Chk(Step)이 모두 "Y"이고,
                    Valid Fail Reason(Step)이 모두 Null인 경우에 대해서만 Simulation 모듈 수행
                */
                resultSet = QueryCommon.selectMatchChkCount(parsedParams);
                let checkQtyZeroArr = []
                let CheckQtySmallArr = [];
                let processNoneSKUREGYN = false;
                if(resultSet.cs.rowCount !== 0) {
                    for(let i= 0; i < resultSet.cs.rowCount; i++){
                        checkQtyZeroArr.push(daCommon.getMeasureValue(resultSet.cs, i, 'CheckQtyZero'));
                        CheckQtySmallArr.push(daCommon.getMeasureValue(resultSet.cs, i, 'CheckQtySmall'));
                    }
                    //메져 CheckQtyZero가 모두 true인지 확인
                    let checkQtyAllTrue = checkQtyZeroArr.every(e => e === true);
                    //메져 CheckQtySmall 모두 true인지 확인
                    let checkQtySmallAllTrue = CheckQtySmallArr.every(e => e === true);
                    if(checkQtyAllTrue || checkQtySmallAllTrue) processNoneSKUREGYN = true;
                }else{
                    processNoneSKUREGYN = true;
                }
                Log.Info("##########################processNoneSKUREGYN:: "+processNoneSKUREGYN);
                if(processNoneSKUREGYN){
                    // //Simulation 모듈 실행 - 사용자 지정 Scope를 using scope 구문에 적용, 
                    QueryCommon.execUIPOProcessNoneSKUREG(parsedParams);
                }else{
                    RuleOutputToUI = {Status: 'Error', Message: "Please Check Valid!"};
                }
            }else{
                RuleOutputToUI = {Status: 'Error', Message: `The "${parsedParams.fb_ParamStep}" step condition for lastStepMax-"${lastStepMaxName}" is not met.`};
            }
        } catch(e) {
            //오류 발생시 초기화 (Container planning, Validation, Po, Po detail 초기화)
            QueryCommon.executeScopeSimulationInitialize(parsedParams);
            RuleOutputToUI = {Status: 'Error', Message: e.Message};
        }
    }

    class QueryCommon {
        static selectProductGroup(parsedParams) {
            let query =`
                    select (&NSMPProductGroup) on row;
                `
            // Log.Info("##########################executeCartesianSeasonalDelaySetWeightByYear:: "+query);
            return daCommon.selectQueryList('selectProductGroup', query);
        };

        static selectFilterProductGroup(parsedParams) {
            let query =`
                    select (
                        [Item].[Item Class].Filter(~ isnull(#.Name) && ~( #.Name in {"-"}) )
                        .relatedmembers([Item]).filter(#.[MP Item Flag] == true )
                        .relatedmembers([Product Group])) on row //&NSMPProductGroup namedSet 
                    where {
                        Item.[Product].filter(#.Name in {${parsedParams.fb_Filter_Product}})
                    };
                `
            // Log.Info("##########################executeCartesianSeasonalDelaySetWeightByYear:: "+query);
            return daCommon.selectQueryList('selectFilterProductGroup', query);
        };

        static selectFilterSubLocation(parsedParams) {
            let query =`
                    select (
                        [Sub Location].[Sub Location].filter(#.Name in {${parsedParams.fb_Filter_SubLocation}})
                    ) on row;
                `
            // Log.Info("##########################executeCartesianSeasonalDelaySetWeightByYear:: "+query);
            return daCommon.selectQueryList('selectFilterSubLocation', query);
        };

        static selectFilterLocation(parsedParams) {
            let query =`
                    select (
                        [Location].[Location Type].filter(#.Name == "DC").relatedmembers([Location]).filter(#.Name in {${parsedParams.fb_Filter_Location}})
                    ) on row;
                `
            // Log.Info("##########################executeCartesianSeasonalDelaySetWeightByYear:: "+query);
            return daCommon.selectQueryList('selectFilterLocation', query);
        };

        static selectScopeLastStepMax(params) {
            let query = `
                Select (
                    [Version].[Version Name].[${params.fb_Version}] 
                ) on row,
                ({
                    Measure.[PO Process Detail_Last Step]
                }) on column
                where {
                    [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    , [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    , Item.[Product Group]${params.fb_Product_Group === "All"?"":`.filter(#.Name in {${params.fb_Product_Group}})`}
                } ;
            `;
            Log.Info("##########################selectCopeLastStepMax:: "+query);
            return daCommon.selectQueryList('selectTotalLastStepMax', query);
        }

        static selectScopeCheckQtyByStep(params, byStepParam) {
            let query = `
                Select (
                    [Version].[Version Name].[${params.fb_Version}] 
                ) on row,
                ({
                    Measure.[PO Process Detail_Check Qty(${byStepParam})]
                }) on column
                where {
                    [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    , [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    , Item.[Product Group]${params.fb_Product_Group === "All"?"":`.filter(#.Name in {${params.fb_Product_Group}})`}
                } ;
            `;
            Log.Info("##########################selectScopeCheckQtyByStep:: "+query);
            return daCommon.selectQueryList('selectScopeCheckQtyByStep', query);
        }

        static executeScopeSimulationInitialize(params){
            //M simulation 인 경우, FINAL 메저 초기화 시 최종 step이 P인 row는 제외 하고 nullify한다.
            let compareStr = `
                if(
                    "${params.fb_ParamStep}" == "M"  
                    && Measure.[PO Process Detail_Last Step] == "1"
                )
            `;

            let query = `
                //Container planning Initialize (해당 Step의 container planning 만 삭제)
                delete data for model [Loading PO Container Plan]
                where {
                    &CWV_MP
                    , [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    , [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    , Item.[Product Group]${params.fb_Product_Group === "All"?"":`.filter(#.Name in {${params.fb_Product_Group}})`}
                    , [Plan Step].[Plan Step].filter(#.Name in {[${params.fb_ParamStep}], [FIANL]}) // final step까지 지우고
                };
                                    
                //Cal Master Initialize
                delete data for model [Loading PO Cal Master]
                where {
                    &CWV_MP
                    , [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    , [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    , Item.[Product Group]${params.fb_Product_Group === "All"?"":`.filter(#.Name in {${params.fb_Product_Group}})`}
                };
                                    
                //Po nullify ( 결과값 메저(p/m,  final) null)
                Scope: (
                    &CWV_MP 
                    * [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    * [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    * Item.[Product Group]${params.fb_Product_Group === "All"?".relatedmembers(Item)":`.filter(#.Name in {${params.fb_Product_Group}}).relatedmembers(Item)`}
                    // * [Seq].[Seq] 
                    * [Time].[Week]
                    * [SOP Week].[SOP Week] 
                    * [MFG Week].[MFG Week] 
                    * [Delivery Week].[Delivery Week] 
                );
                    Measure.[PO Process_Item Unit Load Mix Match Chk(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Item Unit Load Mix Match(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Lane Load Mix Match Chk(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Lane Load Mix Match(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Valid Fail Reason(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_CNTR FR(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Diff Qty(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Item FR(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Loading Qty(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Loading Status(${params.fb_ParamStep})] = null;
                    Measure.[PO Process_Item Unit Load Mix Match Chk(FINAL)] = null;
                    Measure.[PO Process_Item Unit Load Mix Match(FINAL)] = null;
                    Measure.[PO Process_Lane Load Mix Match Chk(FINAL)] = null;
                    Measure.[PO Process_Lane Load Mix Match(FINAL)] = null;
                    Measure.[PO Process_Valid Fail Reason(FINAL)] = null;
                    Measure.[PO Process_CNTR FR(FINAL)] = null;
                    Measure.[PO Process_Diff Qty(FINAL)] = null;
                    Measure.[PO Process_Item FR(FINAL)] = null;
                    Measure.[PO Process_Loading Qty(FINAL)] = null;
                    Measure.[PO Process_Loading Status(FINAL)] = null;
                    ${
                        params.fb_ParamStep == "M"?"Measure.[PO Process_Check Qty(ADJ1)] = null;"
                            :params.fb_ParamStep == "ADJ1"?"Measure.[PO Process_Check Qty(ADJ2)] = null;"
                                :params.fb_ParamStep == "ADJ2"?"Measure.[PO Process_Check Qty(ADJ3)] = null;"
                                    :params.fb_ParamStep == "ADJ3"?"Measure.[PO Process_Check Qty(FINAL)] = null;":""
                    }
                end scope;
                                
                //Po Detail nullfy ( 결과값 메저(p/m, final) null)
                scope: ( 
                    &CWV_MP  
                    * [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    * [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    * Item.[Product Group]${params.fb_Product_Group === "All"?".relatedmembers(Item)":`.filter(#.Name in {${params.fb_Product_Group}}).relatedmembers(Item)`}
                    * [Seq].[Seq] 
                    * [Time].[Week] 
                    * [MFG Week].[MFG Week] 
                );
                    Measure.[PO Process Detail_Item Unit Load Mix Match Chk(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Item Unit Load Mix Match(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Lane Load Mix Match Chk(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Lane Load Mix Match(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Valid Fail Reason(${params.fb_ParamStep})] = null;                                    
                    Measure.[PO Process Detail_CNTR FR(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Diff Qty(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Item FR(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Loading Qty(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Loading Status(${params.fb_ParamStep})] = null;
                    Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Item Unit Load Mix Match Chk(FINAL)] else null;
                    Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Item Unit Load Mix Match(FINAL)] else null;
                    Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Lane Load Mix Match Chk(FINAL)] else null;
                    Measure.[PO Process Detail_Lane Load Mix Match(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Lane Load Mix Match(FINAL)] else null;
                    Measure.[PO Process Detail_Valid Fail Reason(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Valid Fail Reason(FINAL)] else null;                                    
                    Measure.[PO Process Detail_CNTR FR(FINAL)] = ${compareStr} then Measure.[PO Process Detail_CNTR FR(FINAL)] else null;
                    Measure.[PO Process Detail_Diff Qty(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Diff Qty(FINAL)] else null;
                    Measure.[PO Process Detail_Item FR(FINAL)] = ${compareStr}  then Measure.[PO Process Detail_Item FR(FINAL)] else null;
                    Measure.[PO Process Detail_Loading Qty(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Loading Qty(FINAL)] else null;
                    Measure.[PO Process Detail_Loading Status(FINAL)] = ${compareStr} then Measure.[PO Process Detail_Loading Status(FINAL)] else null;
                    ${
                        params.fb_ParamStep == "M"?"Measure.[PO Process Detail_Check Qty(ADJ1)] = null;"
                            :params.fb_ParamStep == "ADJ1"?"Measure.[PO Process Detail_Check Qty(ADJ2)] = null;"
                                :params.fb_ParamStep == "ADJ2"?"Measure.[PO Process Detail_Check Qty(ADJ3)] = null;"
                                    :params.fb_ParamStep == "ADJ3"?"Measure.[PO Process Detail_Check Qty(FINAL)] = null;":""
                    }
                end scope; 
            `;

            Log.Info('executeScopeSimulationInitialize Query ::::::::::::::::::::::: ' + query);
            return daCommon.executeQuery('executeScopeSimulationInitialize', query);
        }

        static execUIPOProcessValidNLoadREG(params){
            let query = `
                EXEC plugin instance [PY_UI_POProcessValidNLoad_REG]
                for measures { [PO Process_Valid Fail Reason(${params.fb_ParamStep})] }
                using scope (
                    &CWV_MP
                    * [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    * [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    * Item.[Product Group]${params.fb_Product_Group === "All"?"":`.filter(#.Name in {${params.fb_Product_Group}})`}
                )
                using arguments {(ExecutionMode, "MediumWeight")
                                , (Param_OUT_VERSION, "CWV_MP")
                                , (Param_Exception_Flag, "N")
                                , (Param_Step, "${params.fb_ParamStep}")
                                , (Param_Check_Qty, "${params.fb_Check_Qty}")
                                , (MaxSliceTableCells, 200000000)
                                , (MaxConcurrency, 1)
                                , (IncludeNullRows, False)
                                , ([Param.o9_sys_log_level], "DEBUG")
                    };
            `;
            Log.Info('execUIPOProcessValidNLoadREG Query ::::::::::::::::::::::: ' + query);
            return daCommon.executeQuery('execUIPOProcessValidNLoadREG', query);
        }

        static execUIPOProcessNoneSKUREG(params){
            let query = `
                EXEC plugin instance [PY_UI_POProcessNoneSKU_REG]
                for measures {[PO Process Detail_Simulated By]}
                using scope (
                    &CWV_MP
                    * [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    * [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    * Item.[Product Group]${params.fb_Product_Group === "All"?"":`.filter(#.Name in {${params.fb_Product_Group}})`}
                )
                using arguments {(ExecutionMode, "MediumWeight")
                                , (Param_OUT_VERSION, "${params.fb_Version}")
                                , (Param_Adjust_Option1, "${params.fb_Adjust_Option1}")
                                , (Param_Adjust_Option2 , "${params.fb_Adjust_Option2}")
                                , (Param_User_Name , CurrentUser().[User Name])
                                , (Param_Step, "${params.fb_ParamStep}")
                                , (Param_Check_Qty, "${params.fb_Check_Qty}")
                                , (MaxSliceTableCells, 200000000)
                                , (MaxConcurrency, 1)
                                , (IncludeNullRows, False)
                                , ([Param.o9_sys_log_level], "DEBUG")
                    };
            `;
            Log.Info('execUIPOProcessNoneSKUREG Query ::::::::::::::::::::::: ' + query);
            return daCommon.executeQuery('execUIPOProcessNoneSKUREG', query);
        }

        static selectMatchChkCount(params) {
            // let query =`
            //     (
            //         Select (
            //             [Version].[Version Name].[${params.fb_Version}]
            //             * [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
            //             * [Location].[Location].filter(#.Name in {${params.fb_Location}})
            //             * Item.[Product Group]${params.fb_Product_Group === "All"?".relatedmembers(Item)":`.filter(#.Name == "${params.fb_Product_Group}").relatedmembers(Item)`}
            //             * [Seq].[Seq]
            //             * [Time].[Week]
            //             * [MFG Week].[MFG Week]
            //         ) on row,
            //             ({
            //                 Measure.[PO Process Detail_Created by]
            //             }) on column
            //         where {
            //             ~(
            //                 Measure.[PO Process Detail_Item Unit Load Mix Match Chk(${params.fb_ParamStep})] == "Y"
            //                 && Measure.[PO Process Detail_Lane Load Mix Match Chk(${params.fb_ParamStep})] == "Y"
            //                 && isnull(Measure.[PO Process Detail_Valid Fail Reason(${params.fb_ParamStep})])
            //             )
            //        }).count;`
            let query = `
                Select (
                    [Version].[Version Name].[${params.fb_Version}]
                    * [Sub Location].[Sub Location].filter(#.Name in {${params.fb_SubLocation}})
                    * [Location].[Location].filter(#.Name in {${params.fb_Location}})
                    * Item.[Product Group]${params.fb_Product_Group === "All"?".relatedmembers(Item)":`.filter(#.Name == "${params.fb_Product_Group}").relatedmembers(Item)`}
                    * [Seq].[Seq]
                    * [Time].[Week]
                    * [MFG Week].[MFG Week]
                ) on row,
                    ({
                        Measure.[PO Process Detail_Check Qty(P)]
                        , Measure.[Loading PO Cal Master_Min Qty]
                        , (Measure.[PO Process Detail_Check Qty(P)] == 0) as transient.[CheckQtyZero]
                        , (Measure.[PO Process Detail_Check Qty(P)] < COALESCE(Measure.[Loading PO Cal Master_Min Qty], 0)) as transient.[CheckQtySmall]
                    }) on column
                where {
                    ~(
                        Measure.[PO Process Detail_Item Unit Load Mix Match Chk(P)] == "Y"
                        && Measure.[PO Process Detail_Lane Load Mix Match Chk(P)] == "Y"
                        && isnull(Measure.[PO Process Detail_Valid Fail Reason(P)])
                    )
                }; 
            `;
            Log.Info('selectMatchChkCount Query ::::::::::::::::::::::: ' + query);
            return daCommon.selectQueryList('selectMatchChkCount', query);
        }

    }
    
    return {
        fn_SubmitSeasonalDelaySetWeightByYear : daCommon.fn_decorator(fn_SubmitSeasonalDelaySetWeightByYear)
        , fn_dsProductGroup : daCommon.fn_decorator(fn_dsProductGroup)
        , fn_ExecPYUIPOSimulation : daCommon.fn_decorator(fn_ExecPYUIPOSimulation)
        , fn_dsFilterProductGroup : daCommon.fn_decorator(fn_dsFilterProductGroup)
        , fn_dsFilterSubLocation : daCommon.fn_decorator(fn_dsFilterSubLocation)
        , fn_dsFilterLocation : daCommon.fn_decorator(fn_dsFilterLocation)
    };
});