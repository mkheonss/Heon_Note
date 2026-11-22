define('o9.NSCM.JS.DemandModification', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = 'o9.NSCM.JS.DemandModification';
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
    /*  BizCaseMgmt > Add ID > Biz Case ID 
        Biz Case ID는 자동생성, suffix 일련번호 Max값 + 1
        Action Button > ABCaseAdd > ds_createCaseID 호출
    */
    let fn_createCaseID = function(o9Params){
        /* parsed Param */
        // const parsedParams = JSON.parse(o9Params);
        let caseID = 'UC_DMD_001';
        /* 1. Case Type별 Sorting Desc suffix Max값 + 1 */
        const resultSet = QueryCommon.selectMaxUseCaseIDList(o9Params);
        /* BizCaseID dimension이 있을경우*/ 
        if(resultSet.cs.rowCount !== 0){
            Log.Info(`##########################resultSet.cs.rowCount: ${resultSet.cs.rowCount}`);
            let prefix = 'UC_DMD_';
            let index = 2;
            let oldCaseID = daCommon.getMember(resultSet.cs, 0, 'Group', 'Group ID').Name;
            Log.Info(`##########################oldCaseID: ${oldCaseID}`);
            let suffixNum = oldCaseID.split('_')[index];
            let nextSuffixNum = parseInt(suffixNum)+1;
            caseID = prefix + daUtil.fn_lpad(nextSuffixNum.toString(), 3, '0');
        }        
        return caseID;
    }
    
    /*  Demand Modification > Add Use Case > 'ABDemandModificationAddUseCase'
        Action Button > ABDemandModificationAddUseCase > ds_SalesGC 호출
    */
    let fn_salesGCCombo = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);

        const resultSet = QueryCommon.selectSalesGC(parsedParams);
        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Sales Domain", DimAttbName : "GC", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    }

    /* AP2 fb_SalesStd2 Combo */
    let fn_salesStd2Combo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* [],.. 형태로 변환 */

        /* AP2 list  */
        let resultSet  = QueryCommon.selectAP2List(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Sales Domain", DimAttbName : "AP2", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /* AP1 fb_SalesStd3 Combo */
    let fn_salesStd3Combo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        /* [],.. 형태로 변환 */
        // /* AP1 list  */
        let resultSet  = QueryCommon.selectAP1List(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Sales Domain", DimAttbName : "AP1", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /* shipTo Combo */
    let fn_shipToCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectAccountList(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Sales Domain", DimAttbName : "Account", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /* shipTo Combo */
    let fn_productGroupCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProductGroup(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /* shipTo Combo */
    let fn_productCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProduct(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Product", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /* shipTo Combo */
    let fn_productTypeCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProductType(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "ProductType", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /* shipTo Combo */
    let fn_projectCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProject(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /* shipTo Combo */
    let fn_itemCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* Ship To, Account list  */
        let resultSet = QueryCommon.selectItem(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    /*  BizCaseMgmt > Add Biz Case > Submit
        Action Button > Add Biz Case > Submit 버튼 실행
    */
    let fn_SubmitAddUseCase = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserId();
        // User ID
        parsedParams.seq = 1;

        parsedParams.useCaseID = fn_createCaseID(parsedParams);
        /* Group > Group ID > Description member update*/
        QueryCommon.updateMemberGroupIDDescription(parsedParams);
        /* Group > Group ID > Description member update*/
        QueryCommon.executeCartesianAddUseCase(parsedParams);
    }

    let fn_SubmitSetUseCaseIndex = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserId();
        parsedParams.useCaseID = parsedParams.fb_UseCaseID;
        parsedParams.seq = parsedParams.fb_Seq;

        /* Group > Group ID > Description member update*/
        QueryCommon.updateMemberGroupIDDescription(parsedParams);
        QueryCommon.executeCartesianAddUseCase(parsedParams);
    }

    /*  Demand Modification > Copy Use Case > Submit
        Action Button > Copy Use Case > Submit 버튼 실행
    */
    let fn_SubmitCopyUseCase = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserId();
        // User ID
        parsedParams.seq = 1;

        // let modGC, modAP2, modAP1, modAccount, modPGroup, modProduct, modProductType, modProject, modItem, modFromWeek, modToWeek, modRate, modOverrideWeek

        let resultSet = QueryCommon.selectCopyUseCaseMeasureList(parsedParams);

        if(resultSet.cs.rowCount !== 0) {
            parsedParams.useCaseID = fn_createCaseID(parsedParams);
            for(let i=0; i<resultSet.cs.rowCount; i++){
                // Use Case ID max seq + 1
                parsedParams.seq = i+1;
                parsedParams.modGC = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_GC');
                parsedParams.modAP2 = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_AP2');
                parsedParams.modAP1 = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_AP1');
                parsedParams.modAccount = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Account');
                parsedParams.modPGroup = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Product Group');
                parsedParams.modProduct = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Product');
                parsedParams.modProductType = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Product Type');
                parsedParams.modProject = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Project');
                parsedParams.modItem = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Item');
                parsedParams.modFromWeek = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_From Week');
                parsedParams.modToWeek = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_To Week');
                parsedParams.modRate = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Rate');
                parsedParams.modOverrideWeek = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Override Seq');
                /* executeCartesianCopyUseCase*/
                QueryCommon.executeCartesianCopyUseCase(parsedParams);
            }
            /* Group > Group ID > Description member update*/
            QueryCommon.updateMemberGroupIDDescription(parsedParams);
        }
    }

    let fn_SubmitAddUseCaseIndex = function(o9Params){
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserId();
        let newSeq = 1;
        // Use Case ID별 Index Max를 구하기 위한 
        let resultSet = QueryCommon.selectUseCaseIndexMaxSeq(parsedParams);
        if(resultSet.cs.rowCount !== 0){
            let oldUseCaseIDIdx = daCommon.getMember(resultSet.cs, 0, 'Seq', 'Seq').Name;
            Log.Info(`##########################oldUseCaseIDIdx: ${oldUseCaseIDIdx}`);
            newSeq = parseInt(oldUseCaseIDIdx)+1;
        }
        parsedParams.useCaseID = parsedParams.fb_UseCaseID
        parsedParams.seq = newSeq;

        /* Group > Group ID > Description member update*/
        QueryCommon.executeCartesianAddUseCase(parsedParams);
    }

    let fn_ValidationUseCase =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;

        daUtil.fn_validationMultiRowCheck(tupleList);
    }

    let fn_ValidationDeleteUseCase =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;
        let useCaseIDInBizCase = '';
        tupleList.forEach(element => {
            parsedParams.fb_GroupID = element.fb_GroupID.Value;
            let resultSet = QueryCommon.selectUseUseCaseInBizCase(parsedParams);
            if(resultSet.cs.rowCount !== 0) {
                useCaseIDInBizCase += parsedParams.fb_GroupID + ",";
            }
        });
        if(useCaseIDInBizCase != ''){
            let useCaseIDInBizCaseArr = useCaseIDInBizCase.split(',');
            useCaseIDInBizCaseArr = useCaseIDInBizCaseArr.splice(0, useCaseIDInBizCaseArr.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + useCaseIDInBizCaseArr.join(", ") + ") UsecaseID is being used in the Biz case. "};
            returnValue = 1;
        }
        return returnValue;
    }

    let fn_ValidationDeleteUseCaseIndex = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        let useCaseIDInBizCase = '';
        let returnValue = 0;
        // fb_GroupID별 count  
        const groupIDCntObj = {};
        // check box에 선택된 GroupID을 배열로 저장
        let groupIDArr = tupleList.map(e => 
            e.fb_GroupID.Value
        );
        // 체크된 groupID 개수를 Object type의 groupIDCntObj 저장
        groupIDArr.forEach(item => {
            groupIDCntObj[item] = (groupIDCntObj[item] || 0) + 1; 
        });
        // groupIDCntObj의 key만 가져온다.
        const groupIDList = Object.keys(groupIDCntObj);
        for(let i=0; i<groupIDList.length; i++){
            parsedParams.fb_UseCaseID = groupIDList[i];
            // groupID당 등록된 총 row갯수를 구하는 쿼리
            let resultSetRowCount = QueryCommon.selectCopyUseCaseMeasureList(parsedParams).cs.rowCount;
            // groupID당 등록된 총 row갯수와 체크된 갯수가 같으면 모두 지우는거 이기 때문에 Biz Case에서 사용중인지 함수 호출
            if(resultSetRowCount == groupIDCntObj[groupIDList[i]]){
                parsedParams.fb_GroupID = groupIDList[i];
                let resultSet = QueryCommon.selectUseUseCaseInBizCase(parsedParams);
                if(resultSet.cs.rowCount !== 0) {
                    useCaseIDInBizCase += groupIDList[i] + ",";
                }
            }
        }
        if(useCaseIDInBizCase != ''){
            let useCaseIDInBizCaseArr = useCaseIDInBizCase.split(',');
            useCaseIDInBizCaseArr = useCaseIDInBizCaseArr.splice(0, useCaseIDInBizCaseArr.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + useCaseIDInBizCaseArr.join(", ") + ") UsecaseID is being used in the Biz case. "};
            returnValue = 1;
        }
        return returnValue;
    }

    class QueryCommon {
        static selectMaxUseCaseIDList(params) {
            let query = `
                        select (Group.[Group Type].[USE_DMD].relatedmembers([Group ID])) on row,
                        (
                        ) on column
                        where {
                            Version.[Version Name].[${params.fb_Version}]
                            , Measure.[Use Case Master_Created By] != ""
                        }
                        orderby [Group].[Group ID].Key desc limit 1;
            `;
            // Log.Info("##########################selectMaxUseCaseIDList:: "+query);
            return daCommon.selectQueryList('selectMaxUseCaseIDList', query);
        }

        static selectMaxBizCaseIDList(params) {
            let query = `
            
            `
            return daCommon.selectQueryList('selectMaxBizCaseIDList', query);
        }
        
        static selectSalesGC(params) {
            let query = `
                Select ([Sales Domain].[GC].filter(~(#.Name == "-")));
            `;
            return daCommon.selectQueryList('selectSalesGC', query);
        }

        static selectAP2List(parsedParams) {
            let query =`
                Select ([Sales Domain].[Sales Std1]
                .filter(~(#.Name == "-"))
                ${parsedParams.fb_GC === "All"? "": `.filter(#.DisplayName == "${parsedParams.fb_GC}")`}
                .relatedmembers([AP2]));
            `;
              return daCommon.selectQueryList('selectAP2List', query);
        };

        static selectAP1List(parsedParams) {
            let query =`
                Select (
                    [Sales Domain].[Sales Std2]
                    .filter(~(#.Name == "-"))
                    ${parsedParams.fb_AP2 === "All"? "": `.filter(#.DisplayName == "${parsedParams.fb_AP2}")`}
                    .relatedmembers([AP1])
                );
            `;
              return daCommon.selectQueryList('selectAP1List', query);
        };

        static selectAccountList(parsedParams) {
            let query =
                `Select (
                    [Sales Domain].[Sales Std3]
                    .filter(~(#.Name == "-"))
                    ${parsedParams.fb_AP1 === "All"? "": `.filter(#.DisplayName == "${parsedParams.fb_AP1}")`}
                    .relatedmembers([Account])
                ) ; 
                `
            // Log.Info("##########################selectAccountList:: "+query);
            return daCommon.selectQueryList('selectAccountList', query);
        };

        static selectProductGroup(parsedParams) {
            let query =`
                select (Item.[Product Group].filter(~(#.[Name] == "-" ))) on row,
                () on column
                where {
                    &CWV_MP
                }
                `
            // Log.Info("##########################selectAccountList:: "+query);
            return daCommon.selectQueryList('selectProductGroup', query);
        };

        static selectProduct(parsedParams) {
            let query =`
               Select ([Item].[Product]) on row, 
                () on column
                where {
                    &CWV_MP, 
                    Item.[Product Group]${parsedParams.fb_ProductGroup === "All"? "": `.filter(#.DisplayName == "${parsedParams.fb_ProductGroup}")`}
                }
                `
            // Log.Info("##########################selectAccountList:: "+query);
            return daCommon.selectQueryList('selectProduct', query);
        };

        static selectProductType(parsedParams) {
            let query =`
                Select ([Item].[ProductType]) on row, 
                () on column
                where {
                    &CWV_MP,
                    Item.[Product Group]${parsedParams.fb_ProductGroup === "All"? "": `.filter(#.DisplayName == "${parsedParams.fb_ProductGroup}")`}
                }
                `
            // Log.Info("##########################selectAccountList:: "+query);
            return daCommon.selectQueryList('selectProductType', query);
        };

        static selectProject(parsedParams) {
            let query =`
                Select ([Item].[Project]) on row, 
                () on column
                where {
                    &CWV_MP,
                    Item.[Product Group]${parsedParams.fb_ProductGroup === "All"? ",": `.filter(#.DisplayName == "${parsedParams.fb_ProductGroup}"),`}
                    Item.[Product]${parsedParams.fb_Product === "All"? "": `.filter(#.DisplayName == "${parsedParams.fb_Product}")`}
                }
                `
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectProject', query);
        };

        static selectItem(parsedParams) {
            let query =`
                select (Item.[Item].filter(~(#.[Name] == "-" ))) on row,
                () on column
                where {
                    &CWV_MP,
                    Item.[Product Group]${parsedParams.fb_ProductGroup === "All"? ",": `.filter(#.DisplayName == "${parsedParams.fb_ProductGroup}"),`}
                    Item.[Product]${parsedParams.fb_Product === "All"? ",": `.filter(#.DisplayName == "${parsedParams.fb_Product}"),`}
                    Item.[Project]${parsedParams.fb_Project === "All"? "": `.filter(#.DisplayName == "${parsedParams.fb_Project}")`}
                }
                `
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectItem', query);
        };

        static updateMemberGroupIDDescription(parsedParams) {
            let query =`
                createmember(
                    Group.[Group ID] = {, "${parsedParams.useCaseID}"}, [Group].[Description] = {"${parsedParams.fb_UseCase}", }
                    , Group.[Group Type] = {, "USE_DMD"}
                );
                `
            // Log.Info("##########################updateMemberGroupIDDescription:: "+query);
            return daCommon.executeQuery('updateMemberGroupIDDescription', query);
        };

        static selectCopyUseCaseMeasureList(parsedParams) {
            let query =`
                select (
                    Version.[Version Name].[${parsedParams.fb_Version}]
                    * Group.[Group ID].[${parsedParams.fb_UseCaseID}]
                    * Seq.[Seq]
                ) on row,
                ({
                    Measure.[Scenario Demand Mod_GC]
                    , Measure.[Scenario Demand Mod_AP2]
                    , Measure.[Scenario Demand Mod_AP1]
                    , Measure.[Scenario Demand Mod_Account]
                    , Measure.[Scenario Demand Mod_Product Group]
                    , Measure.[Scenario Demand Mod_Product]
                    , Measure.[Scenario Demand Mod_Product Type]
                    , Measure.[Scenario Demand Mod_Project]
                    , Measure.[Scenario Demand Mod_Item]
                    , Measure.[Scenario Demand Mod_From Week]
                    , Measure.[Scenario Demand Mod_To Week]
                    , Measure.[Scenario Demand Mod_Rate]
                    , Measure.[Scenario Demand Mod_Override Seq]
                }) on column;
                `
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectCopyUseCaseMeasureList', query);
        };

        static executeCartesianAddUseCase(parsedParams) {
            let query =`
                cartesian scope: (
                    [Version].[Version Name].[CWV_MP]
                    * [Group].[Group ID].[${parsedParams.useCaseID}]
                    * [Seq].[Seq].[${parsedParams.seq}]
                );
                    Measure.[Scenario Demand Mod_GC] = "${parsedParams.fb_GC}";
                    Measure.[Scenario Demand Mod_AP2] = "${parsedParams.fb_AP2}";
                    Measure.[Scenario Demand Mod_AP1] = "${parsedParams.fb_AP1}";
                    Measure.[Scenario Demand Mod_Account] = "${parsedParams.fb_ShipTo}";
                    Measure.[Scenario Demand Mod_Product Group] = "${parsedParams.fb_ProductGroup}";
                    Measure.[Scenario Demand Mod_Product] = "${parsedParams.fb_Product}";
                    Measure.[Scenario Demand Mod_Product Type] = "${parsedParams.fb_ProductType}";
                    Measure.[Scenario Demand Mod_Project] = "${parsedParams.fb_Project}";
                    Measure.[Scenario Demand Mod_Item] = "${parsedParams.fb_Item}";
                    ${parsedParams.fb_ButtonName === "Set Use Case Index"? 
                    `Measure.[Use Case Master_Update Time] = dateadd(Now(),9,"hour");
                        Measure.[Use Case Master_Updated By] = "${parsedParams.userId}";
                    `: 
                    `Measure.[Use Case Master_Created By] = "${parsedParams.userId}";
                        Measure.[Use Case Master_Creation Time] = dateadd(Now(),9,"hour");
                    `
                    }
                    ${parsedParams.fb_ButtonName === "Set Use Case Index"? 
                    `Measure.[Scenario Demand Mod_Update Time] = dateadd(Now(),9,"hour");
                        Measure.[Scenario Demand Mod_Updated By] = "${parsedParams.userId}";
                    `: 
                    `Measure.[Scenario Demand Mod_Created By] = "${parsedParams.userId}";
                        Measure.[Scenario Demand Mod_Creation Time] = dateadd(Now(),9,"hour");
                    `
                    }
                end scope;
                `
            // Log.Info("##########################executeCartesianAddUseCase:: "+query);
            return daCommon.executeQuery('executeCartesianAddUseCase', query);
        };

        static executeCartesianCopyUseCase(parsedParams) {
            let query =`
                cartesian scope: (
                    [Version].[Version Name].[CWV_MP]
                    * [Group].[Group ID].[${parsedParams.useCaseID}]
                    * [Seq].[Seq].[${parsedParams.seq}]
                );
                    Measure.[Scenario Demand Mod_GC] = "${parsedParams.modGC}";
                    Measure.[Scenario Demand Mod_AP2] = "${parsedParams.modAP2}";
                    Measure.[Scenario Demand Mod_AP1] = "${parsedParams.modAP1}";
                    Measure.[Scenario Demand Mod_Account] = "${parsedParams.modAccount}";
                    Measure.[Scenario Demand Mod_Product Group] = "${parsedParams.modPGroup}";
                    Measure.[Scenario Demand Mod_Product] = "${parsedParams.modProduct}";
                    Measure.[Scenario Demand Mod_Product Type] = "${parsedParams.modProductType}";
                    Measure.[Scenario Demand Mod_Project] = "${parsedParams.modProject}";
                    Measure.[Scenario Demand Mod_Item] = "${parsedParams.modItem}";
                    ${parsedParams.modFromWeek == null ? "": `Measure.[Scenario Demand Mod_From Week] = "${parsedParams.modFromWeek}";`}
                    ${parsedParams.modToWeek == null ? "": `Measure.[Scenario Demand Mod_To Week] = "${parsedParams.modToWeek}";`}
                    ${parsedParams.modRate == null ? "": `Measure.[Scenario Demand Mod_Rate] = "${parsedParams.modRate}";`}
                    ${parsedParams.modOverrideWeek == null ? "": `Measure.[Scenario Demand Mod_Override Seq] = "${parsedParams.modOverrideWeek}";`}
                    Measure.[Use Case Master_Created By] = "${parsedParams.userId}";
                    Measure.[Use Case Master_Creation Time] = dateadd(Now(),9,"hour");
                    Measure.[Scenario Demand Mod_Created By] = "${parsedParams.userId}";
                    Measure.[Scenario Demand Mod_Creation Time] = dateadd(Now(),9,"hour");
                end scope;
                `
            // Log.Info("##########################executeCartesianCopyUseCase:: "+query);
            return daCommon.executeQuery('executeCartesianCopyUseCase', query);
        };

        static selectUseCaseIndexMaxSeq(parsedParams){
            let query = `
                select (
                    Seq.[Seq]
                ) on row,
                ({
                    Measure.[Scenario Demand Mod_Created By]
                }) on column
                where {
                    Version.[Version Name].[${parsedParams.fb_Version}]
                    , Group.[Group ID].[${parsedParams.fb_UseCaseID}]
                }
                orderby[Seq].[Seq].Key Desc
                limit 1;
            `;
            return daCommon.selectQueryList('selectUseCaseIndexMaxSeq', query);
        }

        static selectUseUseCaseInBizCase(parsedParams){
            let query = `
                Select (
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    * [Group].[Group ID].[${parsedParams.fb_GroupID}] 
                    * [Biz Case].[Biz Case] 
                ) on row, 
                ({
                    Measure.[Biz Case Use Case Asn_Created By]
                }) on column
                limit 1;
            `;
            Log.Info("##########################selectUseUseCaseInBizCase:: "+query);
            return daCommon.selectQueryList('selectUseUseCaseInBizCase', query);
        }
    }

    return {
        fn_createCaseID : daCommon.fn_decorator(fn_createCaseID)
        , fn_salesGCCombo : daCommon.fn_decorator(fn_salesGCCombo)
        , fn_salesStd2Combo : daCommon.fn_decorator(fn_salesStd2Combo)
        , fn_salesStd3Combo : daCommon.fn_decorator(fn_salesStd3Combo)
        , fn_shipToCombo : daCommon.fn_decorator(fn_shipToCombo)
        , fn_productGroupCombo : daCommon.fn_decorator(fn_productGroupCombo)
        , fn_productCombo : daCommon.fn_decorator(fn_productCombo)
        , fn_productTypeCombo : daCommon.fn_decorator(fn_productTypeCombo)
        , fn_projectCombo : daCommon.fn_decorator(fn_projectCombo)
        , fn_itemCombo : daCommon.fn_decorator(fn_itemCombo)
        , fn_SubmitAddUseCase: daCommon.fn_decorator(fn_SubmitAddUseCase)
        , fn_SubmitSetUseCaseIndex: daCommon.fn_decorator(fn_SubmitSetUseCaseIndex)
        , fn_SubmitCopyUseCase: daCommon.fn_decorator(fn_SubmitCopyUseCase)
        , fn_SubmitAddUseCaseIndex: daCommon.fn_decorator(fn_SubmitAddUseCaseIndex)
        , fn_ValidationUseCase: daCommon.fn_decorator(fn_ValidationUseCase)
        , fn_ValidationDeleteUseCase: daCommon.fn_decorator(fn_ValidationDeleteUseCase)
        , fn_ValidationDeleteUseCaseIndex: daCommon.fn_decorator(fn_ValidationDeleteUseCaseIndex)
    };
});