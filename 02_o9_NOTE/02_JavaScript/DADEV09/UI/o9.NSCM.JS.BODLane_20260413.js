define('o9.NSCM.JS.BODLane', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.BODLane';
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
    let fn_SubmitBODLaneCapaUpdate = function(o9Params){
        /* parsed Param */
        let parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        let ratioMeasure, capaMeasure;
        let validNIdxArr = [];
        let resultSet;

        //이우미차장님 파이썬 로직 먼저 실행
        QueryCommon.executePYUIBODLaneCalREG(parsedParams);

        switch(parsedParams.fb_MeasureSet){
            case "4W":
                ratioMeasure = "BOD Port_Ratio(BOD per Port 4W)";
                capaMeasure = "BOD Port_Capa Qty(4W)";
                break;
            case "12W":
                ratioMeasure = "BOD Port_Ratio(BOD per Port 12W)";
                capaMeasure = "BOD Port_Capa Qty(12W)";
                break;
            case "LY":
                ratioMeasure = "BOD Port_Ratio(BOD per Port Y-1)";
                capaMeasure = "BOD Port_Capa Qty(Y-1)";
                break;
            case "SMLY":
                ratioMeasure = "BOD Port_Ratio(BOD per Port Y-1 M)";
                capaMeasure = "BOD Port_Capa Qty(Y-1 M)";
                break;
        }
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        tupleList.forEach((item, index) => {
            let getTupleParam = {};
            getTupleParam.fb_Version = parsedParams.fb_Version;
            getTupleParam.fb_SubLocation = item.fb_SubLocation.Value;
            getTupleParam.fb_Location = item.fb_Location.Value;
            getTupleParam.fb_Activity2 = item.fb_Activity2.Value;
            getTupleParam.fb_LoadingPort = item.fb_LoadingPort.Value;
            getTupleParam.fb_DischargePort = item.fb_DischargePort.Value;
            getTupleParam.fb_DestPort = item.fb_DestPort.Value;
            getTupleParam.fb_MeasureSet = parsedParams.fb_MeasureSet;
            //MDP는 ParentMeasure값을 ActionButton에서 직접가져올수 없어 Select한다.
            //2025-12-15 Ocean Contract Mgmt 쿼리를 위해 Loading Logistics Port, Discharge Logistics Port 디멘져 추가
            resultSet = QueryCommon.selectBODLanePortRatioCapaPerWk(getTupleParam);
            getTupleParam.loadingLogiPort = daCommon.getMember(resultSet.cs, 0, "Loading Port", "Loading Logistics Port").Name;
            getTupleParam.dischargeLogiPort = daCommon.getMember(resultSet.cs, 0, "Discharge Port", "Discharge Logistics Port").Name;
            getTupleParam.validFlag = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Valid Flag');
            getTupleParam.portRatio = daCommon.getMeasureValue(resultSet.cs, 0, ratioMeasure);
            // getTupleParam.capaPerQty = daCommon.getMeasureValue(resultSet.cs, 0, capaMeasure) === null? 0 :daCommon.getMeasureValue(resultSet.cs, 0, capaMeasure);
            getTupleParam.fb_Week = daUtil.fn_multiArr(parsedParams.fb_Week);
            getTupleParam.userId = parsedParams.userId;
            //Ocean Contract Mgmt화면 Loading Logistics Port, Discharge Logistics Port select된 "Ocean Capa W_Capa Qty"메져에 "BOD Port Ratio"곱을 구하게 위한 select
            resultSet = QueryCommon.selectBODPortWCapaQtyByBODRatio(getTupleParam);
             // Vaild Y(BOD Port_Valid Flag)일 경우 해당 내용으로 업데이트 한다.
            if(getTupleParam.validFlag == "Y"){
                Log.Info("##########################");
                // Capa per WK[Guideline] 값을 모든 주차에 Copy 한다.
                if(resultSet.cs.rowCount !== 0) {
                    for(let i= 0; i < resultSet.cs.rowCount; i++){
                        getTupleParam.week = daCommon.getMember(resultSet.cs, i, "Time", "Week").Name;
                        getTupleParam.capaPerQty = daCommon.getMeasureValue(resultSet.cs, i, "BOD Port W_Capa Qty BY BOD Port Ratio");
                        QueryCommon.executeCartesianBODLaneCapaQty(getTupleParam);
                    }
                }
                //선택한 Measure Set에 Port Ratio per BOD[Guideline] 컬럼 값을 Port Ratio per BOD(BOD Port_Ratio(Port / BOD)) 컬럼에 Copy한다.
                QueryCommon.executeCartesianBODLaneCapaPortRatio(getTupleParam);
            }else{
                validNIdxArr.push(index+1);
            }
        });

        if(validNIdxArr.length > 0){
            RuleOutputToUI = {Status: 'Success', Message: `${validNIdxArr.join()} BOD Port_Valid Flag Is N`};
        }
    }

    let fn_SubmitBODLaneSetValid = function(o9Params){
        /* parsed Param */
        let parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        tupleList.forEach(e => {
            e.fb_Version = parsedParams.fb_Version;
            e.userId = parsedParams.userId;
            e.valid = parsedParams.fb_Valid;
            QueryCommon.executeCartesianBODLaneSetValid(e);
        });
    }

    let fn_SubmitBODPortRatioper = function(o9Params){
        /* parsed Param */
        let parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        // let resultSet = QueryCommon.selectBODLanePortRatioCapaPerWk(parsedParams);
        // parsedParams.portRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(Port / BOD)');
        QueryCommon.executeBODPortRatioper(parsedParams);
    }

    let fn_SubmitAddBODLane = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        parsedParams.fb_Week = daUtil.fn_multiArr(parsedParams.fb_Week);

        let resultSetDuplList = QueryCommon.selectCopyBODLaneMeasureDuplList(parsedParams);
        if(resultSetDuplList.cs.rowCount !== 0) {
            RuleOutputToUI = {Status: 'Error', Message: "BOD Lane duplicated!"};
            return;
        }

        QueryCommon.executeCartesianAddBODLane(parsedParams);
        // Log.Info("##########################parsedParams:: "+JSON.stringify(parsedParams));
    }

    let fn_SubmitCopyBODLane = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        parsedParams.weeks = daUtil.fn_multiArr(parsedParams.fb_Week);

        let resultSetDuplList = QueryCommon.selectCopyBODLaneMeasureDuplList(parsedParams);
        if(resultSetDuplList.cs.rowCount !== 0) {
            RuleOutputToUI = {Status: 'Error', Message: "BOD Lane duplicated!"};
            return;
        }
        
        let resultSet = QueryCommon.selectCopyBODLaneMeasureList(parsedParams);
        if(resultSet.cs.rowCount !== 0) {
            parsedParams.PB4WRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(Port per BOD 4W)');
            parsedParams.BP4WRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(BOD per Port 4W)');
            parsedParams.BP4WQty = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Capa Qty(4W)');

            parsedParams.PB12WRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(Port per BOD 12W)');
            parsedParams.BP12WRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(BOD per Port 12W)');
            parsedParams.BP12WQty = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Capa Qty(12W)');
            
            parsedParams.PBY1Ratio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(Port per BOD Y-1)');
            parsedParams.BPY1Ratio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(BOD per Port Y-1)');
            parsedParams.BPY1Qty = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Capa Qty(Y-1)');

            parsedParams.PBY1MRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(Port per BOD Y-1 M)');
            parsedParams.BPY1MRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(BOD per Port Y-1 M)');
            parsedParams.BPY1MQty = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Capa Qty(Y-1 M)');

            parsedParams.BPRatio = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Ratio(Port / BOD)');
            parsedParams.BPCount = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Recent Year Used Count');
            parsedParams.BPVolumeCNTR = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Recent Year Volume CNTR');
            parsedParams.valid = daCommon.getMeasureValue(resultSet.cs, 0, 'BOD Port_Valid Flag');

            QueryCommon.executeCartesianCopyBODLane(parsedParams);
        }
        // BOD Port W 메져그룹에 BOD Port W_Capa Qty 메져값 가져오기
        let resultSetSecond = QueryCommon.selectCopyBODLaneWMeasureList(parsedParams);
        let wCapaQtyArr = [];
        if(resultSetSecond.cs.rowCount !== 0) {
            for(let i=0; i<resultSetSecond.cs.rowCount; i++){
                parsedParams.wCapaQty = daCommon.getMeasureValue(resultSetSecond.cs, i, 'BOD Port W_Capa Qty');
                parsedParams.week = parsedParams.fb_Week[i];
                QueryCommon.executeCartesianCopyBODLaneW(parsedParams);
            }
        }
    }

    let fn_LoadingPortCombo = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        const resultSet = QueryCommon.selectLoadingPortList(parsedParams);
        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Loading Port", DimAttbName : "Loading Port", isDisplayNameWithCode : false});
        return comboList;
    }

    let fn_DischargePortCombo = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        const resultSet = QueryCommon.selectDischargePortList(parsedParams);
        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Discharge Port", DimAttbName : "Discharge Port", isDisplayNameWithCode : false});
        return comboList;
    }

    let fn_DestPortCombo = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        const resultSet = QueryCommon.selectDestPortList(parsedParams);
        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Dest Port", DimAttbName : "Dest Port", isDisplayNameWithCode : false});
        return comboList;
    }

    class QueryCommon {
        static executePYUIBODLaneCalREG(paramsObj) {
            let query = `
                EXEC plugin instance [PY_UI_BODLaneCal_REG]
                for measures { [BOD Port_Capa Qty(12W)]
                            , [BOD Port_Capa Qty(4W)]
                            , [BOD Port_Capa Qty(Y-1 M)]
                            , [BOD Port_Capa Qty(Y-1)]
                            , [BOD Port_Ratio(BOD per Port 12W)]
                            , [BOD Port_Ratio(BOD per Port 4W)]
                            , [BOD Port_Ratio(BOD per Port Y-1 M)]
                            , [BOD Port_Ratio(BOD per Port Y-1)]
                            }
                using scope ([Version].[Version Name].[${paramsObj.fb_Version}])
                using arguments {(ExecutionMode, "MediumWeight")
                                , (Param_OUT_VERSION, "${paramsObj.fb_Version}")
                                , (MaxSliceTableCells, 200000000)
                                , (MaxConcurrency, 1 )
                                , (IncludeNullRows, False)
                                , ([Param.o9_sys_log_level], "DEBUG")
                                };
            `;
            // Log.Info("##########################executePYUIBODLaneCalREG:: "+query);
            return daCommon.executeQuery('executePYUIBODLaneCalREG', query);
        };

        static selectBODLanePortRatioCapaPerWk(paramsObj) {
            let query = `
                Select (
                    [Version].[Version Name].[${paramsObj.fb_Version}]
                    * [Sub Location].[Sub Location].[${paramsObj.fb_SubLocation}] 
                    * [Location].[Location].[${paramsObj.fb_Location}]  
                    * [Activity2].[Activity2].[${paramsObj.fb_Activity2}]  
                    * [Loading Port].[Loading Port].[${paramsObj.fb_LoadingPort}] 
                    * [Loading Port].[Loading Port].filter(#.Name == "${paramsObj.fb_LoadingPort}").relatedmembers([Loading Logistics Port])
                    * [Discharge Port].[Discharge Port].[${paramsObj.fb_DischargePort}]  
                    * [Discharge Port].[Discharge Port].filter(#.Name == "${paramsObj.fb_DischargePort}").relatedmembers([Discharge Logistics Port])
                    * [Dest Port].[Dest Port].[${paramsObj.fb_DestPort}] 
                ) on row,
                ({
                    Measure.[BOD Port_Valid Flag],
                    ${paramsObj.fb_MeasureSet === "4W"?
                        "Measure.[BOD Port_Ratio(BOD per Port 4W)], Measure.[BOD Port_Capa Qty(4W)]"
                        :paramsObj.fb_MeasureSet === "12W"?
                            "Measure.[BOD Port_Ratio(BOD per Port 12W)], Measure.[BOD Port_Capa Qty(12W)]"
                            :paramsObj.fb_MeasureSet === "LY"?
                                "Measure.[BOD Port_Ratio(BOD per Port Y-1)], Measure.[BOD Port_Capa Qty(Y-1)]"
                                :paramsObj.fb_MeasureSet === "SMLY"?
                                    "Measure.[BOD Port_Ratio(BOD per Port Y-1 M))], Measure.[BOD Port_Capa Qty(Y-1 M)]"
                                    :""
                    }
                }) on column;
            `;
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectBODLanePortRatioCapaPerWk', query);
        }

        static executeCartesianBODLaneCapaQty(paramsObj) {
            let query = `
                cartesian scope: (
                    [Version].[Version Name].[${paramsObj.fb_Version}]
                    * [Sub Location].[Sub Location].[${paramsObj.fb_SubLocation}] 
                    * [Location].[Location].[${paramsObj.fb_Location}]  
                    * [Activity2].[Activity2].[${paramsObj.fb_Activity2}]  
                    * [Loading Port].[Loading Port].[${paramsObj.fb_LoadingPort}]  
                    * [Discharge Port].[Discharge Port].[${paramsObj.fb_DischargePort}]  
                    * [Dest Port].[Dest Port].[${paramsObj.fb_DestPort}]
                    * [Time].[Week].filter(#.Name == "${paramsObj.week}")
                );
                    Measure.[BOD Port W_Capa Qty] = ${paramsObj.capaPerQty};
                    // Measure.[BOD Port_Last Used Date] = Now();
                    Measure.[BOD Port_Update Time] = Now();
                    Measure.[BOD Port_Updated By] = "${paramsObj.userId}";
                end scope;
            `;
            // Log.Info("##########################executeCartesianBODLaneCapaQty:: "+query);
            return daCommon.executeQuery('executeCartesianBODLaneCapaQty', query);
        }

        static executeCartesianBODLaneCapaPortRatio(paramsObj) {
            let query = `
                cartesian scope: (
                    [Version].[Version Name].[${paramsObj.fb_Version}]
                    * [Sub Location].[Sub Location].[${paramsObj.fb_SubLocation}] 
                    * [Location].[Location].[${paramsObj.fb_Location}]  
                    * [Activity2].[Activity2].[${paramsObj.fb_Activity2}]  
                    * [Loading Port].[Loading Port].[${paramsObj.fb_LoadingPort}]  
                    * [Discharge Port].[Discharge Port].[${paramsObj.fb_DischargePort}]  
                    * [Dest Port].[Dest Port].[${paramsObj.fb_DestPort}]
                );
                    Measure.[BOD Port_Ratio(Port / BOD)] = ${paramsObj.portRatio};
                end scope;
            `;
            // Log.Info("##########################executeCartesianBODLaneCapaPortRatio:: "+query);
            return daCommon.executeQuery('executeCartesianBODLaneCapaPortRatio', query);
        }

        static executeCartesianBODLaneSetValid(paramsObj) {
            let query = `
                cartesian scope: (
                    [Version].[Version Name].[${paramsObj.fb_Version}]
                    * [Sub Location].[Sub Location].[${paramsObj.fb_SubLocation.Value}] 
                    * [Location].[Location].[${paramsObj.fb_Location.Value}]  
                    * [Activity2].[Activity2].[${paramsObj.fb_Activity2.Value}]  
                    * [Loading Port].[Loading Port].[${paramsObj.fb_LoadingPort.Value}]  
                    * [Discharge Port].[Discharge Port].[${paramsObj.fb_DischargePort.Value}]  
                    * [Dest Port].[Dest Port].[${paramsObj.fb_DestPort.Value}]
                );
                    Measure.[BOD Port_Valid Flag] = "${paramsObj.valid}";
                    Measure.[BOD Port_Update Time] = Now();
                    // Measure.[BOD Port_Last Used Date] = Now();
                    Measure.[BOD Port_Updated By] = "${paramsObj.userId}";
                end scope;
            `;
            // Log.Info("##########################executeCartesianBODLaneCapaPortRatio:: "+query);
            return daCommon.executeQuery('executeCartesianBODLaneSetValid', query);
        }

        // static selectBODLanePortRatio(paramsObj) {
        //     let query = `
        //         Select (
        //             [Version].[Version Name].[${paramsObj.fb_Version}]
        //             * [Sub Location].[Sub Location].[${paramsObj.fb_SubLocation}] 
        //             * [Location].[Location].[${paramsObj.fb_Location}]  
        //             * [Activity2].[Activity2].[${paramsObj.fb_Activity2}]  
        //             * [Loading Port].[Loading Port].[${paramsObj.fb_LoadingPort}]  
        //             * [Discharge Port].[Discharge Port].[${paramsObj.fb_DischargePort}]  
        //             * [Dest Port].[Dest Port].[${paramsObj.fb_DestPort}] 
        //         ) on row,
        //         ({
        //             Measure.[BOD Port_Valid Flag]
        //             , Measure.[BOD Port_Ratio(Port / BOD)]
        //         }) on column;
        //     `;
        //     // Log.Info("##########################selectProject:: "+query);
        //     return daCommon.selectQueryList('selectBODLanePortRatioCapaPerWk', query);
        // }

        static executeBODPortRatioper(paramsObj) {
            let query = `
                cartesian scope: (
                    [Version].[Version Name].[${paramsObj.fb_Version}]
                    * [Sub Location].[Sub Location].[${paramsObj.fb_SubLocation}] 
                    * [Location].[Location].[${paramsObj.fb_Location}]  
                    * [Activity2].[Activity2].[${paramsObj.fb_Activity2}]  
                    * [Loading Port].[Loading Port].[${paramsObj.fb_LoadingPort}]  
                    * [Discharge Port].[Discharge Port].[${paramsObj.fb_DischargePort}]  
                    * [Dest Port].[Dest Port].[${paramsObj.fb_DestPort}]
                );
                    Measure.[BOD Port_Ratio(Port / BOD)] = ${paramsObj.fb_PortRatio};
                    Measure.[BOD Port_Update Time] = Now();
                    // Measure.[BOD Port_Last Used Date] = Now();
                    Measure.[BOD Port_Updated By] = "${paramsObj.userId}";
                end scope;
            `;
            // Log.Info("##########################executeCartesianBODLaneCapaPortRatio:: "+query);
            return daCommon.executeQuery('executeCartesianBODLaneSetValid', query);
        }

        static selectCopyBODLaneMeasureList(parsedParams) {
            let query =`
                select (
                    Version.[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite_Prev}]
                    * [Location].[Location].[${parsedParams.fb_ToSite_Prev}] 
                    * [Activity2].[Activity2].[${parsedParams.fb_TransportMode_Prev}] 
                    * [Loading Port].[Loading Port].[${parsedParams.fb_PortcodeLoading_Prev}] 
                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_PortcodeDischarge_Prev}] 
                    * [Dest Port].[Dest Port].[${parsedParams.fb_PortcodeDestination_Prev}] 
                ) on row,
                ({
                    Measure.[BOD Port_Ratio(Port per BOD 4W)]
                    , Measure.[BOD Port_Ratio(BOD per Port 4W)]
                    , Measure.[BOD Port_Capa Qty(4W)]
                    , Measure.[BOD Port_Ratio(Port per BOD 12W)]
                    , Measure.[BOD Port_Ratio(BOD per Port 12W)]
                    , Measure.[BOD Port_Capa Qty(12W)]
                    , Measure.[BOD Port_Ratio(Port per BOD Y-1)]
                    , Measure.[BOD Port_Ratio(BOD per Port Y-1)]
                    , Measure.[BOD Port_Capa Qty(Y-1)]
                    , Measure.[BOD Port_Ratio(Port per BOD Y-1 M)]
                    , Measure.[BOD Port_Ratio(BOD per Port Y-1 M)]
                    , Measure.[BOD Port_Capa Qty(Y-1 M)]
                    , Measure.[BOD Port_Ratio(Port / BOD)]
                    , Measure.[BOD Port_Recent Year Used Count]
                    , Measure.[BOD Port_Recent Year Volume CNTR]
                    , Measure.[BOD Port_Valid Flag]
                }) on column;
                `
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectCopyBODLaneMeasureList', query);
        };

        static selectCopyBODLaneMeasureDuplList(parsedParams) {
            let query =`
                select (
                    Version.[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}]
                    * [Location].[Location].[${parsedParams.fb_ToSite}] 
                    * [Activity2].[Activity2].[${parsedParams.fb_TransportMode}] 
                    * [Loading Port].[Loading Port].[${parsedParams.fb_PortcodeLoading}] 
                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_PortcodeDischarge}] 
                    * [Dest Port].[Dest Port].[${parsedParams.fb_PortcodeDestination}] 
                ) on row,
                ({
                    Measure.[BOD Port_Created By]
                }) on column;
                `
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectCopyBODLaneMeasureDuplList', query);
        };

        static selectCopyBODLaneWMeasureList(parsedParams) {
            let query =`
                select (
                    Version.[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite_Prev}]
                    * [Location].[Location].[${parsedParams.fb_ToSite_Prev}] 
                    * [Activity2].[Activity2].[${parsedParams.fb_TransportMode_Prev}] 
                    * [Loading Port].[Loading Port].[${parsedParams.fb_PortcodeLoading_Prev}] 
                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_PortcodeDischarge_Prev}] 
                    * [Dest Port].[Dest Port].[${parsedParams.fb_PortcodeDestination_Prev}]
                    * [Time].[Week].filter(#.Name in {${parsedParams.weeks}})
                ) on row,
                ({
                    Measure.[BOD Port W_Capa Qty]
                }) on column;
                `
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectCopyBODLaneMeasureList', query);
        };

        static executeCartesianAddBODLane(parsedParams) {
            let query =`
                cartesian scope: (
                    Version.[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}]
                    * [Location].[Location].[${parsedParams.fb_ToSite}] 
                    * [Activity2].[Activity2].[${parsedParams.fb_TransportMode}] 
                    * [Loading Port].[Loading Port].[${parsedParams.fb_PortcodeLoading}] 
                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_PortcodeDischarge}] 
                    * [Dest Port].[Dest Port].[${parsedParams.fb_PortcodeDestination}] 
                );
                    // Measure.[BOD Port_Last Used Date] = Now();
                    Measure.[BOD Port_Ratio(Port per BOD 4W)] = 0;
                    Measure.[BOD Port_Ratio(BOD per Port 4W)] = 0;
                    Measure.[BOD Port_Capa Qty(4W)] = 0;
                    Measure.[BOD Port_Ratio(Port per BOD 12W)] = 0;
                    Measure.[BOD Port_Ratio(BOD per Port 12W)] = 0;
                    Measure.[BOD Port_Capa Qty(12W)] = 0;
                    Measure.[BOD Port_Ratio(Port per BOD Y-1)] = 0;
                    Measure.[BOD Port_Ratio(BOD per Port Y-1)] = 0;
                    Measure.[BOD Port_Capa Qty(Y-1)] = 0;
                    Measure.[BOD Port_Ratio(Port per BOD Y-1 M)] = 0;
                    Measure.[BOD Port_Ratio(BOD per Port Y-1 M)] = 0;
                    Measure.[BOD Port_Capa Qty(Y-1 M)] = 0;
                    Measure.[BOD Port_Valid Flag] = "Y";
                    // Measure.[BOD Port_Last Used Date] = Now();
                    Measure.[BOD Port_Ratio(Port / BOD)] = 0;
                    Measure.[BOD Port_Recent Year Used Count] = 0;
                    Measure.[BOD Port_Recent Year Volume CNTR] = 0;
                    Measure.[BOD Port_Created By] = "${parsedParams.userId}";
                    Measure.[BOD Port_Creation Time] = Now();
                end scope;

                cartesian scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}] 
                    * [Location].[Location].[${parsedParams.fb_ToSite}]  
                    * [Activity2].[Activity2].[${parsedParams.fb_TransportMode}]  
                    * [Loading Port].[Loading Port].[${parsedParams.fb_PortcodeLoading}]  
                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_PortcodeDischarge}]  
                    * [Dest Port].[Dest Port].[${parsedParams.fb_PortcodeDestination}]
                    * [Time].[Week].filter(#.Name in {${parsedParams.fb_Week}})
                );
                    Measure.[BOD Port W_Capa Qty] = 0;
                end scope;
                `
            // Log.Info("##########################executeCartesianAddBODLane:: "+query);
            return daCommon.executeQuery('executeCartesianAddBODLane', query);
        };

        static executeCartesianCopyBODLane(parsedParams) {
            let query =`
                cartesian scope: (
                    Version.[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}]
                    * [Location].[Location].[${parsedParams.fb_ToSite}] 
                    * [Activity2].[Activity2].[${parsedParams.fb_TransportMode}] 
                    * [Loading Port].[Loading Port].[${parsedParams.fb_PortcodeLoading}] 
                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_PortcodeDischarge}] 
                    * [Dest Port].[Dest Port].[${parsedParams.fb_PortcodeDestination}] 
                );
                    // Measure.[BOD Port_Last Used Date] = Now();
                    Measure.[BOD Port_Ratio(Port per BOD 4W)] = ${parsedParams.PB4WRatio};
                    Measure.[BOD Port_Ratio(BOD per Port 4W)] = ${parsedParams.BP4WRatio};
                    Measure.[BOD Port_Capa Qty(4W)] = ${parsedParams.BP4WQty};
                    Measure.[BOD Port_Ratio(Port per BOD 12W)] = ${parsedParams.PB12WRatio};
                    Measure.[BOD Port_Ratio(BOD per Port 12W)] = ${parsedParams.BP12WRatio};
                    Measure.[BOD Port_Capa Qty(12W)] = ${parsedParams.BP12WQty};
                    Measure.[BOD Port_Ratio(Port per BOD Y-1)] = ${parsedParams.PBY1Ratio};
                    Measure.[BOD Port_Ratio(BOD per Port Y-1)] = ${parsedParams.BPY1Ratio};
                    Measure.[BOD Port_Capa Qty(Y-1)] = ${parsedParams.BPY1Qty};
                    Measure.[BOD Port_Ratio(Port per BOD Y-1 M)] = ${parsedParams.PBY1MRatio};
                    Measure.[BOD Port_Ratio(BOD per Port Y-1 M)] = ${parsedParams.BPY1MRatio};
                    Measure.[BOD Port_Capa Qty(Y-1 M)] = ${parsedParams.BPY1MQty};
                    // Measure.[BOD Port_Last Used Date] = Now();
                    Measure.[BOD Port_Ratio(Port / BOD)] = ${parsedParams.BPRatio};
                    Measure.[BOD Port_Recent Year Used Count] = ${parsedParams.BPCount};
                    Measure.[BOD Port_Recent Year Volume CNTR] = ${parsedParams.BPVolumeCNTR};
                    Measure.[BOD Port_Valid Flag] = "${parsedParams.valid}";
                    Measure.[BOD Port_Created By] = "${parsedParams.userId}";
                    Measure.[BOD Port_Creation Time] = Now();
                end scope;
            `;
            // Log.Info("##########################executeCartesianCopyBODLane:: "+query);
            return daCommon.executeQuery('executeCartesianCopyBODLane', query);
        }

        static executeCartesianCopyBODLaneW(parsedParams) {
            let query =`
                cartesian scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}] 
                    * [Location].[Location].[${parsedParams.fb_ToSite}]  
                    * [Activity2].[Activity2].[${parsedParams.fb_TransportMode}]  
                    * [Loading Port].[Loading Port].[${parsedParams.fb_PortcodeLoading}]  
                    * [Discharge Port].[Discharge Port].[${parsedParams.fb_PortcodeDischarge}]  
                    * [Dest Port].[Dest Port].[${parsedParams.fb_PortcodeDestination}]
                    * [Time].[Week].filter(#.Name == "${parsedParams.week}")
                );
                    Measure.[BOD Port W_Capa Qty] = ${parsedParams.wCapaQty};
                end scope;
            `;
            // Log.Info("##########################executeCartesianCopyBODLane:: "+query);
            return daCommon.executeQuery('executeCartesianCopyBODLane', query);
        }

        static selectLoadingPortList(parsedParams) {
            let query =`
                Select ([Version].[Version Name].[${parsedParams.fb_Version}] * [Loading Port].[Loading Port] ) on row, 
                ({
                    Measure.[Loading Port Mapping_Status]
                    , Measure.[Loading Port Mapping_Valid Flag]
                }) on column
                where {
                        Measure.[Loading Port Mapping_Valid Flag] == "Y"
                    ,   Measure.[Loading Port Mapping_Status] == "CON"
                }
                orderby [Loading Port].[Loading Port].Name;
            `;
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectLoadingPortList', query);
        };

        static selectDischargePortList(parsedParams) {
            let query =`
                Select ([Version].[Version Name].[${parsedParams.fb_Version}] * [Discharge Port].[Discharge Port] ) on row, 
                ({
                    Measure.[Discharge Port Mapping_Status]
                    , Measure.[Discharge Port Mapping_Valid Flag]
                }) on column
                where {
                        Measure.[Discharge Port Mapping_Valid Flag] == "Y"
                    ,   Measure.[Discharge Port Mapping_Status] == "CON"
                }
                orderby [Discharge Port].[Discharge Port].Name;
            `;
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectDischargePortList', query);
        };

        static selectDestPortList(parsedParams) {
            let query =`
                Select ([Version].[Version Name].[${parsedParams.fb_Version}] * [Dest Port].[Dest Port] ) on row, 
                ({
                    Measure.[Dest Port Mapping_Status]
                    , Measure.[Dest Port Mapping_Valid Flag]
                }) on column
                where {
                        Measure.[Dest Port Mapping_Valid Flag] == "Y"
                    ,   Measure.[Dest Port Mapping_Status] == "CON"
                }
                orderby [Dest Port].[Dest Port].Name;
            `;
            // Log.Info("##########################selectDestPortList:: "+query);
            return daCommon.selectQueryList('selectDestPortList', query);
        };

        static selectBODPortWCapaQtyByBODRatio(parsedParams) {
            let query =`
                Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Loading Port].[Loading Logistics Port].[${parsedParams.loadingLogiPort}] 
                    * [Discharge Port].[Discharge Logistics Port].[${parsedParams.dischargeLogiPort}] 
                    * [Time].[Planning Month] 
                    * [Time].[Week].filter(#.Name in {${parsedParams.fb_Week}})
                ) on row, 
                ({
                    Measure.[Ocean Capa W_Capa Qty]
                    , (Measure.[Ocean Capa W_Capa Qty] * ${parsedParams.portRatio}) as transient.[BOD Port W_Capa Qty BY BOD Port Ratio]
                }) on column;
            `;
            // Log.Info("##########################selectBODPortWCapaQtyByBODRatio:: "+query);
            return daCommon.selectQueryList('selectBODPortWCapaQtyByBODRatio', query);
        };
    }
    
    return {
        fn_SubmitBODLaneCapaUpdate : daCommon.fn_decorator(fn_SubmitBODLaneCapaUpdate)
        , fn_SubmitBODLaneSetValid : daCommon.fn_decorator(fn_SubmitBODLaneSetValid)
        , fn_SubmitBODPortRatioper : daCommon.fn_decorator(fn_SubmitBODPortRatioper)
        , fn_SubmitAddBODLane: daCommon.fn_decorator(fn_SubmitAddBODLane)
        , fn_SubmitCopyBODLane: daCommon.fn_decorator(fn_SubmitCopyBODLane)
        , fn_LoadingPortCombo: daCommon.fn_decorator(fn_LoadingPortCombo)
        , fn_DischargePortCombo: daCommon.fn_decorator(fn_DischargePortCombo)
        , fn_DestPortCombo: daCommon.fn_decorator(fn_DestPortCombo)
    };
});