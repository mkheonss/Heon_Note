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
        let caseID = 'BC_DMD_001';
        /* 1. Case Type별 Sorting Desc suffix Max값 + 1 */
        const resultSet = QueryCommon.selectMaxUseCaseIDList(o9Params);
        /* BizCaseID dimension이 있을경우*/ 
        if(resultSet.cs.rowCount !== 0){
            Log.Info(`##########################resultSet.cs.rowCount: ${resultSet.cs.rowCount}`);
            let prefix = 'BC_DMD_';
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
        // displayName을 []감싸주는 함수 호출
        parsedParams.fb_GC = fn_disNameSquareBckConCat(parsedParams.fb_GC);
        
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
        // displayName을 []감싸주는 함수 호출
        parsedParams.fb_GC = fn_disNameSquareBckConCat(parsedParams.fb_GC);
        parsedParams.fb_AP2 = fn_disNameSquareBckConCat(parsedParams.fb_AP2);
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
        // displayName을 []감싸주는 함수 호출
        parsedParams.fb_GC = fn_disNameSquareBckConCat(parsedParams.fb_GC);
        parsedParams.fb_AP2 = fn_disNameSquareBckConCat(parsedParams.fb_AP2);
        parsedParams.fb_AP1 = fn_disNameSquareBckConCat(parsedParams.fb_AP1);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectAccountList(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Sales Domain", DimAttbName : "Account", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    let fn_scmType = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectScmType(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "SCM Type", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    }

    let fn_productGroupCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // fb_ScmType displayName을 []감싸주는 함수 호출
        parsedParams.fb_ScmType = fn_disNameSquareBckConCat(parsedParams.fb_ScmType);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProductGroup(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    let fn_productCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // displayName을 []감싸주는 함수 호출
        parsedParams.fb_ScmType = fn_disNameSquareBckConCat(parsedParams.fb_ScmType);
        parsedParams.fb_ProductGroup = fn_disNameSquareBckConCat(parsedParams.fb_ProductGroup);
       
        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProduct(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Product", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    let fn_productTypeCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // displayName을 []감싸주는 함수 호출
        parsedParams.fb_ScmType = fn_disNameSquareBckConCat(parsedParams.fb_ScmType);
        parsedParams.fb_ProductGroup = fn_disNameSquareBckConCat(parsedParams.fb_ProductGroup);
        parsedParams.fb_Product = fn_disNameSquareBckConCat(parsedParams.fb_Product);
        
        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProductType(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Prod Type", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

    let fn_projectCombo = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // displayName을 []감싸주는 함수 호출
        parsedParams.fb_ScmType = fn_disNameSquareBckConCat(parsedParams.fb_ScmType);
        parsedParams.fb_ProductGroup = fn_disNameSquareBckConCat(parsedParams.fb_ProductGroup);
        parsedParams.fb_Product = fn_disNameSquareBckConCat(parsedParams.fb_Product);

        /* Ship To, Account list  */
        let resultSet  = QueryCommon.selectProject(parsedParams);

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(resultSet, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName", isDisplayNameWithCode : false});
        comboList.unshift({ Name : "All", DisplayName : "All"});
        Log.Info("##########################");
        Log.Info(JSON.stringify(comboList));
        return comboList;
    };

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
        Action Button > Add Biz Case > Submit 버튼 실행CurrentUser().[User Name]
    */
    let fn_SubmitAddUseCase = function(o9Params){
        /* parsed Param */
        let parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        // User ID
        parsedParams.seq = 1;
        // Object key에 대한 value가 배열일때 'All'을 포함하고 있으면 All로 지정
        parsedParams = fn_allIncludePrc(parsedParams);

        parsedParams.useCaseID = fn_createCaseID(parsedParams);
        /* Group > Group ID > Description member update*/
        QueryCommon.updateMemberGroupIDDescription(parsedParams);
        /* Group > Group ID > Description member update*/
        QueryCommon.executeCartesianAddUseCase(parsedParams);
    }
    
    let fn_SubmitSetUseCaseIndex = function(o9Params){
        /* parsed Param */
        let parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
        parsedParams.useCaseID = parsedParams.fb_UseCaseID;
        parsedParams.seq = parsedParams.fb_Seq;

        // Object key에 대한 value가 배열일때 'All'을 포함하고 있으면 All로 지정
        parsedParams = fn_allIncludePrc(parsedParams);

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
        parsedParams.userId = daCommon.fn_getUserName();
        // User ID
        parsedParams.seq = 1;

        let resultSet = QueryCommon.selectCopyUseCaseMeasureList(parsedParams);

        if(resultSet.cs.rowCount !== 0) {
            parsedParams.useCaseID = fn_createCaseID(parsedParams);
            /* Group > Group ID > Description member update*/
            QueryCommon.updateMemberGroupIDDescription(parsedParams);
            for(let i=0; i<resultSet.cs.rowCount; i++){
                // Use Case ID max seq + 1
                parsedParams.seq = i+1;
                parsedParams.modGC = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_GC');
                parsedParams.modAP2 = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_AP2');
                parsedParams.modAP1 = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_AP1');
                parsedParams.modAccount = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_Account');
                parsedParams.modScmType = daCommon.getMeasureValue(resultSet.cs, i, 'Scenario Demand Mod_SCM Type');
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
            
        }
    }

    let fn_SubmitAddUseCaseIndex = function(o9Params){
        /* parsed Param */
        let parsedParams = JSON.parse(o9Params);
        // User ID
        parsedParams.userId = daCommon.fn_getUserName();
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

        // Object key에 대한 value가 배열일때 'All'을 포함하고 있으면 All로 지정
        parsedParams = fn_allIncludePrc(parsedParams);

        /* Group > Group ID > Description member update*/
        QueryCommon.executeCartesianAddUseCase(parsedParams);
    }

    let fn_SubmitDeleteUseCaseIndex = function(o9Params){
        /* parsed Param */
        let parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
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
        let param = {};
        groupIDList.forEach(groupID => {
            param.fb_UseCaseID = groupID;
            param.fb_Version = parsedParams.fb_Version;
            let resultSetRowCount = QueryCommon.selectCopyUseCaseMeasureList(param).cs.rowCount;
            if(resultSetRowCount == groupIDCntObj[groupID]){
                QueryCommon.deleteUseUseCase(param);
            }
        });
        //DeleteUseCaseIndex를 통해 Scenario Demand Modification 메져그룹 삭제
        tupleList.forEach(e => {
            e.fb_Version = parsedParams.fb_Version;
            QueryCommon.deleteUseUseCaseIndex(e);
        });
    }

    // let fn_ = function(){

    // }

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
            parsedParams.fb_UseCaseID = element.fb_GroupID.Value;
            let resultSet = QueryCommon.selectUseUseCaseInBizCase(parsedParams);
            if(resultSet.cs.rowCount !== 0) {
                useCaseIDInBizCase += parsedParams.fb_UseCaseID + ",";
            }
        });
        if(useCaseIDInBizCase != ''){
            let useCaseIDInBizCaseArr = useCaseIDInBizCase.split(',');
            useCaseIDInBizCaseArr = useCaseIDInBizCaseArr.splice(0, useCaseIDInBizCaseArr.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + useCaseIDInBizCaseArr.join(", ") + ") Biz. Case ID is being used in the Scenario Master. "};
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
        let param = {};
        groupIDList.forEach(groupID => {
            param.fb_UseCaseID = groupID;
            param.fb_Version = parsedParams.fb_Version;
            let resultSetRowCount = QueryCommon.selectCopyUseCaseMeasureList(param).cs.rowCount;

            if(resultSetRowCount == groupIDCntObj[groupID]){
                let resultSet = QueryCommon.selectUseUseCaseInBizCase(param);
                if(resultSet.cs.rowCount !== 0) {
                    useCaseIDInBizCase += groupID + ",";
                }
            }
        });

        if(useCaseIDInBizCase != ''){
            let useCaseIDInBizCaseArr = useCaseIDInBizCase.split(',');
            useCaseIDInBizCaseArr = useCaseIDInBizCaseArr.splice(0, useCaseIDInBizCaseArr.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + useCaseIDInBizCaseArr.join(", ") + ") Biz. Case ID is being used in the Scenario Master. "};
            returnValue = 1;
        }
        return returnValue;
    }

    // FB값을 배열을 넘겨받아 []으로 감싸주는 함수
    let fn_disNameSquareBckConCat = function(arrFbParam){
        // AB selectionType 옵션의 'Multiple' 일시 배열값중에 All의 index값을 찾는다.
        let paramAllIdx = arrFbParam.findIndex(ele => ele === 'All');
        if(paramAllIdx == -1){
            // 배열의 'All' 값이 없을시 배열값에 대해 []문자열을 입힌다.
            returnArr = arrFbParam.map(e => `[${e}]`);
        }else {
            // 배열에 All이 존재 하면 All로 지정
            return 'All';
        }

        return returnArr;
    }
    // FB에 값이 배열일때 배열 값이 All이 포함되어있으면 All로 처리하는 함수
    let fn_allIncludePrc = function(parsedParams){
        let parsedParamsKeys = Object.keys(parsedParams);
        parsedParamsKeys.forEach(key => {
            if(Array.isArray(parsedParams[key])){
                let allIdx = parsedParams[key].findIndex(ele => ele === 'All');
                if(allIdx != -1){
                    parsedParams[key] = 'All';
                }
            }
        });

        return parsedParams;
    }

    class QueryCommon {
        static selectMaxUseCaseIDList(params) {
            let query = `
                        select (Group.[Group Type].[Biz_DMD].relatedmembers([Group ID])) on row,
                        (
                        ) on column
                        where {
                            Version.[Version Name].[${params.fb_Version}]
                            , Measure.[Biz Case Master_Created By] != ""
                        }
                        orderby [Group].[Group ID].Name desc limit 1;
            `;
            // Log.Info("##########################selectMaxUseCaseIDList:: "+query);
            return daCommon.selectQueryList('selectMaxUseCaseIDList', query);
        }
        
        static selectSalesGC(params) {
            let query = `
                SELECT (&NSMPGC);
            `;
            return daCommon.selectQueryList('selectSalesGC', query);
        }

        static selectAP2List(parsedParams) {
            let query =`
                SELECT (&NSMPAP2)
                where {
                    [Sales Domain].[GC]${parsedParams.fb_GC === "All"?"":`.filter((#.DisplayName in {${parsedParams.fb_GC}}) || (#.[GC$DisplayAlias] in {${parsedParams.fb_GC}}))`}
                };
            `;
              return daCommon.selectQueryList('selectAP2List', query);
        };

        static selectAP1List(parsedParams) {
            let query =`
                select (&NSMPAP1)
                where {
                    [Sales Domain].[GC]${parsedParams.fb_GC === "All"?",":`.filter((#.DisplayName in {${parsedParams.fb_GC}}) || (#.[GC$DisplayAlias] in {${parsedParams.fb_GC}})),`}
                    [Sales Domain].[AP2]${parsedParams.fb_AP2 === "All"?"":`.filter((#.DisplayName in {${parsedParams.fb_AP2}}) || (#.[AP2$DisplayAlias] in {${parsedParams.fb_AP2}}))`}
                };
            `;
              return daCommon.selectQueryList('selectAP1List', query);
        };

        static selectAccountList(parsedParams) {
            let query =
                `
                select (&NSMPAccount)
                where {
                    [Sales Domain].[GC]${parsedParams.fb_GC === "All"?",":`.filter((#.DisplayName in {${parsedParams.fb_GC}}) || (#.[GC$DisplayAlias] in {${parsedParams.fb_GC}})),`}
                    [Sales Domain].[AP2]${parsedParams.fb_AP2 === "All"?",":`.filter((#.DisplayName in {${parsedParams.fb_AP2}}) || (#.[AP2$DisplayAlias] in {${parsedParams.fb_AP2}})),`}
                    [Sales Domain].[AP1]${parsedParams.fb_AP1 === "All"? "": `.filter((#.DisplayName in {${parsedParams.fb_AP1}}) || (#.[AP1$DisplayAlias] in {${parsedParams.fb_AP1}}))`}
                };
                `
            // Log.Info("##########################selectAccountList:: "+query);
            return daCommon.selectQueryList('selectAccountList', query);
        };

        static selectScmType(parsedParams) {
            let query =`
                select (&NSMPSCMType)
                where {
                    &CWV_MP
                };
                `
            // Log.Info("##########################selectScmType:: "+query);
            return daCommon.selectQueryList('selectScmType', query);
        };

        static selectProductGroup(parsedParams) {
            let query =`
                select (&NSMPProductGroup)
                where {
                    &CWV_MP,
                    Item.[SCM Type]${parsedParams.fb_ScmType == "All"?"":`.filter(#.DisplayName in {${parsedParams.fb_ScmType}})`}
                };
                `
            // Log.Info("##########################selectAccountList:: "+query);
            return daCommon.selectQueryList('selectProductGroup', query);
        };

        static selectProduct(parsedParams) {
            let query =`
               Select (&NSMPProduct)
                where {
                    &CWV_MP,
                    Item.[SCM Type]${parsedParams.fb_ScmType == "All"?",":`.filter(#.DisplayName in {${parsedParams.fb_ScmType}}),`}
                    Item.[Product Group]${parsedParams.fb_ProductGroup === "All"? "": `.filter(#.DisplayName in {${parsedParams.fb_ProductGroup}})`}
                };
                `
            // Log.Info("##########################parsedParams:: "+parsedParams.fb_ProductGroup);
            return daCommon.selectQueryList('selectProduct', query);
        };

        static selectProductType(parsedParams) {
            let query =`
                Select ([Item].[Prod Type]) on row, 
                () on column
                where {
                    &CWV_MP,
                    Item.[SCM Type]${parsedParams.fb_ScmType == "All"?",":`.filter(#.DisplayName in {${parsedParams.fb_ScmType}}),`}
                    Item.[Product Group]${parsedParams.fb_ProductGroup === "All"? ",": `.filter(#.DisplayName in {${parsedParams.fb_ProductGroup}}),`}
                    Item.[Product]${parsedParams.fb_Product === "All"? "": `.filter(#.DisplayName in {${parsedParams.fb_Product}})`}
                };
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
                    Item.[SCM Type]${parsedParams.fb_ScmType == "All"?",":`.filter(#.DisplayName in {${parsedParams.fb_ScmType}}),`}
                    Item.[Product Group]${parsedParams.fb_ProductGroup === "All"? ",": `.filter(#.DisplayName in {${parsedParams.fb_ProductGroup}}),`}
                    Item.[Product]${parsedParams.fb_Product === "All"? "": `.filter(#.DisplayName in {${parsedParams.fb_Product}})`}
                };
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
                };
                `
            // Log.Info("##########################selectProject:: "+query);
            return daCommon.selectQueryList('selectItem', query);
        };

        static updateMemberGroupIDDescription(parsedParams) {
            let query =`
                createmember(
                    Group.[Group ID] = {, "${parsedParams.useCaseID}"}, [Group].[Description] = {"${parsedParams.fb_UseCase}", }
                    , Group.[Group Type] = {, "Biz_DMD"}
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
                    , Measure.[Scenario Demand Mod_SCM Type]
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
                    Measure.[Scenario Demand Mod_GC] = "${Array.isArray(parsedParams.fb_GC)?parsedParams.fb_GC.join('^'):parsedParams.fb_GC}";
                    Measure.[Scenario Demand Mod_AP2] = "${Array.isArray(parsedParams.fb_AP2)?parsedParams.fb_AP2.join('^'):parsedParams.fb_AP2}";
                    Measure.[Scenario Demand Mod_AP1] = "${Array.isArray(parsedParams.fb_AP1)?parsedParams.fb_AP1.join('^'):parsedParams.fb_AP1}";
                    Measure.[Scenario Demand Mod_Account] = "${Array.isArray(parsedParams.fb_ShipTo)?parsedParams.fb_ShipTo.join('^'):parsedParams.fb_ShipTo}";
                    Measure.[Scenario Demand Mod_SCM Type] = "${Array.isArray(parsedParams.fb_ScmType)?parsedParams.fb_ScmType.join('^'):parsedParams.fb_ScmType}";
                    Measure.[Scenario Demand Mod_Product Group] = "${Array.isArray(parsedParams.fb_ProductGroup)?parsedParams.fb_ProductGroup.join('^'):parsedParams.fb_ProductGroup}";
                    Measure.[Scenario Demand Mod_Product] = "${Array.isArray(parsedParams.fb_Product)?parsedParams.fb_Product.join('^'):parsedParams.fb_Product}";
                    Measure.[Scenario Demand Mod_Product Type] = "${Array.isArray(parsedParams.fb_ProductType)?parsedParams.fb_ProductType.join('^'):parsedParams.fb_ProductType}";
                    Measure.[Scenario Demand Mod_Project] = "${Array.isArray(parsedParams.fb_Project)?parsedParams.fb_Project.join('^'):parsedParams.fb_Project}";
                    Measure.[Scenario Demand Mod_Item] = "${daUtil.fn_nvl(parsedParams.fb_Item, '')}";
                    ${parsedParams.fb_ButtonName === "Set Use Case Index"? 
                    `Measure.[Biz Case Master_Update Time] = Now();
                        Measure.[Biz Case Master_Updated By] = "${parsedParams.userId}";
                    `: 
                    `Measure.[Biz Case Master_Created By] = "${parsedParams.userId}";
                        Measure.[Biz Case Master_Creation Time] = Now();
                    `
                    }
                    ${parsedParams.fb_ButtonName === "Set Use Case Index"? 
                    `Measure.[Scenario Demand Mod_Update Time] = Now();
                        Measure.[Scenario Demand Mod_Updated By] = "${parsedParams.userId}";
                    `: 
                    `Measure.[Scenario Demand Mod_Created By] = "${parsedParams.userId}";
                        Measure.[Scenario Demand Mod_Creation Time] = Now();
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
                    Measure.[Scenario Demand Mod_SCM Type] = "${parsedParams.modScmType}";
                    Measure.[Scenario Demand Mod_Product Group] = "${parsedParams.modPGroup}";
                    Measure.[Scenario Demand Mod_Product] = "${parsedParams.modProduct}";
                    Measure.[Scenario Demand Mod_Product Type] = "${parsedParams.modProductType}";
                    Measure.[Scenario Demand Mod_Project] = "${parsedParams.modProject}";
                    Measure.[Scenario Demand Mod_Item] = "${parsedParams.modItem}";
                    ${parsedParams.modFromWeek == null ? "": `Measure.[Scenario Demand Mod_From Week] = "${parsedParams.modFromWeek}";`}
                    ${parsedParams.modToWeek == null ? "": `Measure.[Scenario Demand Mod_To Week] = "${parsedParams.modToWeek}";`}
                    ${parsedParams.modRate == null ? "": `Measure.[Scenario Demand Mod_Rate] = "${parsedParams.modRate}";`}
                    ${parsedParams.modOverrideWeek == null ? "": `Measure.[Scenario Demand Mod_Override Seq] = "${parsedParams.modOverrideWeek}";`}
                    Measure.[Biz Case Master_Created By] = "${parsedParams.userId}";
                    Measure.[Biz Case Master_Creation Time] = Now();
                    Measure.[Scenario Demand Mod_Created By] = "${parsedParams.userId}";
                    Measure.[Scenario Demand Mod_Creation Time] = Now();
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
                    * [Group2].[Group2 ID]
                    * [Group].[Group ID].[${parsedParams.fb_UseCaseID}] 
                ) on row, 
                ({
                   Measure.[Scenario Biz Case Asn_Creation Time]
                }) on column
                limit 1;
            `;
            Log.Info("##########################selectUseUseCaseInBizCase:: "+query);
            return daCommon.selectQueryList('selectUseUseCaseInBizCase', query);
        }

        static deleteUseUseCase(parsedParams){
            let query = `
                delete data for model [Biz Case Master]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    , Group.[Group ID].[${parsedParams.fb_UseCaseID}]
                };
            `
            Log.Info("##########################deleteUseUseCase:: "+query);
            return daCommon.executeQuery('deleteUseUseCase', query);
        }

        static deleteUseUseCaseIndex(parsedParams){
            let query = `
                delete data for model [Scenario Demand Modification]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}]
                    , [Group].[Group ID].[${parsedParams.fb_GroupID.Value}]
                    , [Seq].[Seq].[${parsedParams.fb_Seq.Value}]
                };
            `
            Log.Info("##########################deleteUseUseCaseIndex:: "+query);
            return daCommon.executeQuery('deleteUseUseCaseIndex', query);
        }
    }
    
    return {
        fn_createCaseID : daCommon.fn_decorator(fn_createCaseID)
        , fn_salesGCCombo : daCommon.fn_decorator(fn_salesGCCombo)
        , fn_salesStd2Combo : daCommon.fn_decorator(fn_salesStd2Combo)
        , fn_salesStd3Combo : daCommon.fn_decorator(fn_salesStd3Combo)
        , fn_shipToCombo : daCommon.fn_decorator(fn_shipToCombo)
        , fn_scmType : daCommon.fn_decorator(fn_scmType)
        , fn_productGroupCombo : daCommon.fn_decorator(fn_productGroupCombo)
        , fn_productCombo : daCommon.fn_decorator(fn_productCombo)
        , fn_productTypeCombo : daCommon.fn_decorator(fn_productTypeCombo)
        , fn_projectCombo : daCommon.fn_decorator(fn_projectCombo)
        , fn_itemCombo : daCommon.fn_decorator(fn_itemCombo)
        , fn_SubmitAddUseCase: daCommon.fn_decorator(fn_SubmitAddUseCase)
        , fn_SubmitSetUseCaseIndex: daCommon.fn_decorator(fn_SubmitSetUseCaseIndex)
        , fn_SubmitCopyUseCase: daCommon.fn_decorator(fn_SubmitCopyUseCase)
        , fn_SubmitAddUseCaseIndex: daCommon.fn_decorator(fn_SubmitAddUseCaseIndex)
        , fn_SubmitDeleteUseCaseIndex: daCommon.fn_decorator(fn_SubmitDeleteUseCaseIndex)
        , fn_ValidationUseCase: daCommon.fn_decorator(fn_ValidationUseCase)
        , fn_ValidationDeleteUseCase: daCommon.fn_decorator(fn_ValidationDeleteUseCase)
        , fn_ValidationDeleteUseCaseIndex: daCommon.fn_decorator(fn_ValidationDeleteUseCaseIndex)
    };
});