define('o9.NSCM.JS.StockpileConfirm', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.StockpileConfirm';
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
    let fn_SubmitStockpileSet = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        let param = {};
        // User ID
        param.userId = daCommon.fn_getUserName();
        param.fb_Version = parsedParams.fb_Version;
        param.fb_Valid = parsedParams.fb_Valid;
        param.fb_ToSite = parsedParams.fb_ToSite == "-" ? "": parsedParams.fb_ToSite;
        param.fb_ToSite_Name = parsedParams.fb_ToSite == "-" ? "": QueryCommon.selectLocationName(parsedParams).Result[0].DisplayName;
        tupleList.forEach(e => {
            param.fb_SubLocation = e.fb_SubLocation.Value;
            param.fb_Location = e.fb_Location.Value;
            param.fb_Item = e.fb_Item.Value;
            param.fb_Seq = e.fb_Seq.Value;
            QueryCommon.executeCartesianStockpileSet(param);
        });
    }

    let fn_SubmitStockpileAdd = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let resultSet;
        // let paramObj = {};
        // site add시에 추가될 Seq번호를 받는 변수
        let useSeq;
        let checkedIdx;

        resultSet = QueryCommon.selectStockpileConfirm(parsedParams);

        if(resultSet.cs.rowCount !== 0) {
            let seqArr = [];
            for(let i= 0; i < resultSet.cs.rowCount; i++){
               seqArr.push(parseInt(daCommon.getMember(resultSet.cs, i, 'Seq', 'Seq').Name));
               // Seq.Seq 조건없이 전체를 돌리고 그중에 선택된 Seq가 몇번째 인지 checkedIdx에 저장
               if(parsedParams.fb_Seq == daCommon.getMember(resultSet.cs, i, 'Seq', 'Seq').Name){
                    checkedIdx = i;
               }
            }
            //Seq가 몇번째 인지 checkedIdx해당하는 measure값 가져온다
            parsedParams.planTarget = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Plan Target");
            parsedParams.planPreStartWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Plan Pre Start Week");
            parsedParams.planPreEndWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Plan Pre End Week");
            parsedParams.planInStartWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Plan In Start Week");
            parsedParams.planInEndWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Plan In End Week");
            parsedParams.userTarge = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_User Target");
            parsedParams.userPreStartWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_User Pre Start Week");
            parsedParams.userPreEndWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_User Pre End Week");
            parsedParams.userInStartWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_User In Start Week");
            parsedParams.userInEndWeek = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_User In End Week");
            parsedParams.validFlag = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Valid Flag");
            parsedParams.stockpileSite = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Stockpile Site");
            parsedParams.stockpileSiteName = daCommon.getMeasureValue(resultSet.cs, checkedIdx, "Stockpile Confirm_Stockpile Site Name");
            // 생성될 seq번호를 가져오는 함수 실행
            parsedParams.useSeq = findNextValue(seqArr);
        }
        // Add CartesianStockpileAdd 수행
        QueryCommon.executeCartesianStockpileAdd(parsedParams);
    }

    let fn_dsToSiteGroup3 = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        let resultSet
        let comboList = [];

        if(parsedParams.fb_Valid === "N"){
            comboList.push({ Name : "-", DisplayName : "-"});
        }else{
            resultSet = QueryCommon.selectToSiteGroup3(parsedParams);
            comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Location", DimAttbName : "Site Group3", Sort : "DisplayName", isDisplayNameWithCode : false});
        }
        return comboList;
    }

    let fn_dsToSite = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        let resultSet
        let comboList = [];

        if(parsedParams.fb_Valid === "N"){
            comboList.push({ Name : "-", DisplayName : "-"});
        }else{
            parsedParams.fb_ToSiteGroup3 = daUtil.fn_multiArr(parsedParams.fb_ToSiteGroup3);
            resultSet = QueryCommon.selectToSite(parsedParams);
            // comboList.push({ Name : "-", DisplayName : "-"});
            comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Location", DimAttbName : "Location", Sort : "Name", isDisplayNameWithCode : false});
        }
        return comboList;
    }

    let fn_SubmitStockpileDelete = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        let paramObj = {};
        let seqArr = [];
        paramObj.fb_Version = parsedParams.fb_Version;
        tupleList.forEach((e, index) => {
            if(e.fb_Seq.Value == "1"){
                seqArr.push(index+1);
            }else{
                paramObj.fb_SubLocation = e.fb_SubLocation.Value;
                paramObj.fb_Location = e.fb_Location.Value;
                paramObj.fb_Item = e.fb_Item.Value;
                paramObj.fb_Seq = e.fb_Seq.Value;
                QueryCommon.executeStockpileDelete(paramObj);
            }
        });
        if(seqArr.length > 0){
            RuleOutputToUI = {Status: 'Success', Message: `Among the selected items, the item with [Seq] 1 has been excluded and deleted. Excluded index(${seqArr.join()})`};
        }
    }

    let findNextValue = function (excludes = []) {
        const excluded = new Set(excludes);
        let current = 1;

        while (excluded.has(current)) {
            current++;
        }
        return current++;
    }

    class QueryCommon {
        static selectStockpileConfirm(parsedParams){
            let query = `
                Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Sub Location].[Sub Location].[${parsedParams.fb_SubLocation}]
                    * [Location].[Location].[${parsedParams.fb_Location}] 
                    * [Item].[Item].[${parsedParams.fb_Item}]
                    * [Seq].[Seq]
                ) on row, 
                ({
                    Measure.[Stockpile Confirm_Plan Target]
                    , Measure.[Stockpile Confirm_Plan Pre Start Week]
                    , Measure.[Stockpile Confirm_Plan Pre End Week]
                    , Measure.[Stockpile Confirm_Plan In Start Week]
                    , Measure.[Stockpile Confirm_Plan In End Week]
                    , Measure.[Stockpile Confirm_User Target]
                    , Measure.[Stockpile Confirm_User Pre Start Week]
                    , Measure.[Stockpile Confirm_User Pre End Week]
                    , Measure.[Stockpile Confirm_User In Start Week]
                    , Measure.[Stockpile Confirm_User In End Week]
                    , Measure.[Stockpile Confirm_Valid Flag]
                    , Measure.[Stockpile Confirm_Stockpile Site]
                    , Measure.[Stockpile Confirm_Stockpile Site Name]
                }) on column;
            `;

            // Log.Info("##########################selectStockpileConfirm:: "+query);
            return daCommon.selectQueryList('selectStockpileConfirm', query);
        }

        static executeCartesianSeasonalDelaySetWeightByYear(parsedParams) {
            let query =`
                cartesian scope: (
                                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                                    * [Sub Location].[Sub Location].[${parsedParams.fb_SubLocation.Value}] 
                                    * [Location].[Location].[${parsedParams.fb_Location.Value}]
                                    * [Activity1].[Activity1].[${parsedParams.fb_Activity1.Value}]
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

        static selectToSiteGroup3(parsedParams) {
            let query = `
                select ([Location].[Site Group3]) on row,
                () on column
                where {
                    &NSStockpileSite
                }
                orderby [Location].[Site Group3].DisplayName;
            `;
            return daCommon.selectQueryList('selectSubLocationName', query);
        }

        static selectToSite(parsedParams) {
            let query = `
                select ([Location].[Location].filter((#.[Location Valid Flag] == true || isNull(#.[Location Valid Flag]) && #.[MP Site Flag] == true ) )) on row,
                () on column
                where {
                    [Location].[Site Group3].filter(#.Name in {${parsedParams.fb_ToSiteGroup3}})
                };
            `;
            return daCommon.selectQueryList('selectToSite', query);
        }

        static executeCartesianStockpileSet(parsedParams) {
            let query =`
                cartesian scope : (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Sub Location].[Sub Location].[${parsedParams.fb_SubLocation}] 
                    * [Location].[Location].[${parsedParams.fb_Location}] 
                    * [Item].[Item].[${parsedParams.fb_Item}]
                    * [Seq].[Seq].[${parsedParams.fb_Seq}]
                );
                    Measure.[Stockpile Confirm_Valid Flag] = "${parsedParams.fb_Valid}";
                    Measure.[Stockpile Confirm_Stockpile Site] = "${parsedParams.fb_ToSite}";
                    Measure.[Stockpile Confirm_Stockpile Site Name] = "${parsedParams.fb_ToSite_Name}";
                    Measure.[Stockpile Confirm_Update Time] = Now();
                    Measure.[Stockpile Confirm_Updated By] = "${parsedParams.userId}";
                end scope;
                `
            // Log.Info("##########################executeCartesianStockpileSet:: "+query);
            return daCommon.executeQuery('executeCartesianStockpileSet', query);
        };

        static executeCartesianStockpileAdd(parsedParams) {
            let query =`
                cartesian scope: (
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    * [Sub Location].[Sub Location].[${parsedParams.fb_SubLocation}]
                    * [Location].[Location].[${parsedParams.fb_Location}] 
                    * [Item].[Item].[${parsedParams.fb_Item}]
                    * [Seq].[Seq].[${parsedParams.useSeq}]
                );
                    Measure.[Stockpile Confirm_Plan Target] = 0;
                    Measure.[Stockpile Confirm_Plan Pre Start Week] = ${parsedParams.planPreStartWeek};
                    Measure.[Stockpile Confirm_Plan Pre End Week] = ${parsedParams.planPreEndWeek};
                    Measure.[Stockpile Confirm_Plan In Start Week] = ${parsedParams.planInStartWeek};
                    Measure.[Stockpile Confirm_Plan In End Week] = ${parsedParams.planInEndWeek};
                    Measure.[Stockpile Confirm_User Target] = 0;
                    Measure.[Stockpile Confirm_User Pre Start Week] = ${parsedParams.userPreStartWeek};
                    Measure.[Stockpile Confirm_User Pre End Week] = ${parsedParams.userPreEndWeek};
                    Measure.[Stockpile Confirm_User In Start Week] = ${parsedParams.userInStartWeek};
                    Measure.[Stockpile Confirm_User In End Week] = ${parsedParams.userInEndWeek};
                    Measure.[Stockpile Confirm_Valid Flag] = "${daUtil.fn_nvl(parsedParams.validFlag, '')}";
                    Measure.[Stockpile Confirm_Stockpile Site] = "${daUtil.fn_nvl(parsedParams.stockpileSite, '')}";
                    Measure.[Stockpile Confirm_Stockpile Site Name] = "${daUtil.fn_nvl(parsedParams.stockpileSiteName, '')}";
                    Measure.[Stockpile Confirm_Creation Time] = Now();
                    Measure.[Stockpile Confirm_Created By] = CurrentUser().[User Name];
                end scope;
            `;
            // Log.Info("##########################executeCartesianStockpileAdd:: "+query);
            return daCommon.executeQuery('executeCartesianStockpileAdd', query);
        };

        static executeStockpileDelete(parsedParams) {
            let query =`
                delete data for model [Stockpile Confirm]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}] 
                    , [Sub Location].[Sub Location].[${parsedParams.fb_SubLocation}]
                    , [Location].[Location].[${parsedParams.fb_Location}]
                    , [Item].[Item].[${parsedParams.fb_Item}]
                    , [Seq].[Seq].[${parsedParams.fb_Seq}]
                };
            `;
            // Log.Info("##########################executeStockpileDelete:: "+query);
            return daCommon.executeQuery('executeStockpileDelete', query);
        };

        static selectLocationName(parsedParams) {
            let query =`
                select Location.Location.[${parsedParams.fb_ToSite}];
            `;
            // Log.Info("##########################executeStockpileDelete:: "+query);
            return daCommon.selectQuery('executeStockpileDelete', query);
        };
    }
    
    return {
        fn_SubmitStockpileSet : daCommon.fn_decorator(fn_SubmitStockpileSet)
        , fn_SubmitStockpileAdd : daCommon.fn_decorator(fn_SubmitStockpileAdd)
        , fn_SubmitStockpileDelete : daCommon.fn_decorator(fn_SubmitStockpileDelete)
        , fn_dsToSiteGroup3 : daCommon.fn_decorator(fn_dsToSiteGroup3)
        , fn_dsToSite : daCommon.fn_decorator(fn_dsToSite)
    };
});