define('o9.NSCM.JS.BizCaseDefinition', ['o9.NSCM.commonLibDA'], function(commonLib){
    const programName = "o9.NSCM.JS.BizCaseDefinition";

    /* setting  */
    // let commonLib = require('o9.NSCM.JScommon_DA');
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

    /* jsErrorMsg */
    const jsErrorMsg = "Please contact the system administrator.";

    /**
     * Logs the given message.
     *
     * @param {string} msg - The message to be logged.
     * @returns {void}
     */
    let log = function(msg) {
        daCommon.debug(msg);
    }

    /* set flag to print log */
    const infLogFlag = true;
    const errLogFlag = true;

    let infLog = function (msg, printFlag) {
        if (printFlag) {
            let logMsg = `${this.preFix}[${this.programName}] ${msg}`;
            Log.Info(logMsg);
        }
    };

    let errLog = function (msg, printFlag) {
        if (printFlag) {
            let logMsg = `${this.errorPreFix}[${this.programName}] ${msg}`;
            Log.Error(logMsg);
        }
    };


    let fn_useCaseCombo = function(o9Params){
        try {            

            var parsedParams = JSON.parse(o9Params);
            let fbButtonType = parsedParams.fbButtonType;   //fbButtonType : bod / prod

            let where = "";
            // where = "where { &CWVUI, Measure.[BOD List_BOD Valid] == Y}";

            // dimension, measure, where, orderby, limit
            var result = daCommon.selectList(["&MFStageSETLocation"], // 2024.10.29 변경 &SETLocation
                                             [],    // measure
                                             where,    // where
                                             "",    // orderby
                                             "");   // limit
            daCommon.printCsData(result, 3);

            var comboList = daCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            daCommon.debug("ComboData : " + JSON.stringify(comboList));

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };    

    let fn_createBizCase = function(o9Params){
        try {

            daCommon.printParams(o9Params);

            // 파라미터 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbBizCase = fn_GetBizCodeMaxCode(o9Params);

            infLog(`##########################fn_GetBizCodeMaxCode로직 후 fbBizCase:: ${fbBizCase} `, infLogFlag);
            
            var fbUseCase = parsedParams.fb_UseCase;
            let len_fb_UseCaseDemand = parsedParams.fb_UseCaseDemand.length;
            let strLen = '';
            let arrSeq = [];
            for(let i=0;i<len_fb_UseCaseDemand;i++){
                let num = i+2;
                strLen += "["+num.toString()+"],";
                arrSeq.push(num);
            }
            if(len_fb_UseCaseDemand>0) strLen = strLen.slice(0,-1);

            infLog(`##########################중복체크 전 fbBizCase:: ${fbBizCase} `, infLogFlag);

            var dimension = [`[Version].[Version Name].[${parsedParams.fb_Version}]`
                            ,"[Biz Case].[Biz Case].[" + fbBizCase + "]"
                            ,"[Group].[Group ID].[" + fbUseCase + "]"];

            // 중복체크
            if ( daCommon.existMeasure(dimension
                                    ,["Measure.[Biz Case Use Case Asn_Override Seq]"
                                    ,"Measure.[Biz Case Master_Creation Time]"
                                    ,"Measure.[Biz Case Master_Created By]"
                                    ,"Measure.[Biz Case Master_Update Time]"
                                    ,"Measure.[Biz Case Master_Updated By]"]
                                    , "")) {
                RuleOutputToUI = { Status : 'Error', Message : "The data has already been registered." };
                return;
            }

            infLog(`##########################중복체크 후 fbBizCase:: ${fbBizCase} `, infLogFlag);

            let countQuery = "[Biz Case].[Biz Case].[" + fbBizCase +"]";
            let cntDimensionBizCase = daCommon.selectCount(countQuery);
            
            infLog(`##########################executeCountDimensionBizCase 후 cntDimensionBizCase:: ${cntDimensionBizCase} `, infLogFlag);
            
            if (cntDimensionBizCase === 0) {
                //createmember
                infLog(`##########################createmember 전 cntDimensionBizCase:: ${cntDimensionBizCase} `, infLogFlag);
                
                let creatMemberQuery = `createmember([Biz Case].[Biz Case] = {, "${fbBizCase}"}, [Biz Case].[Biz Case$InActive]={null,})`;
                daCommon.executeQuery('creatMemberBizCase', creatMemberQuery);
                //NSCMCommon.createMember('[Biz Case].[Biz Case]', fbBizCase);

                infLog(`##########################createmember 후 cntDimensionBizCase:: ${cntDimensionBizCase} `, infLogFlag);
            }

            QueryCommon.updateMemberGroupIDDescription(fbBizCase, parsedParams);

            var dimensionBizCaseMaster = [
                            `[Version].[Version Name].[${parsedParams.fb_Version}]`
                            ,"[Biz Case].[Biz Case].[" + fbBizCase + "]"
                            ];

            infLog(`##########################createMeasure 전 0 fbUseCase:: ${fbUseCase} `, infLogFlag);

            let sUserId = daCommon.fn_getUserId();
            let measure1 = [
                `Measure.[Biz Case Master_Creation Time] = dateadd(Now(),0,"hour");`
                ,`Measure.[Biz Case Master_Created By] = "${sUserId}";`
            ];


            infLog(`##########################createMeasure 1번실행 fbUseCase:: ${fbUseCase} `, infLogFlag);
            daCommon.createMeasure(dimensionBizCaseMaster, measure1);


            let measure2 = [
                //`Measure.[Biz Case Use Case Asn_Override Seq]="1";`
                `Measure.[Biz Case Use Case Asn_Creation Time] = dateadd(Now(),0,"hour");`
                ,`Measure.[Biz Case Use Case Asn_Created By] = "${sUserId}";`
            ];

            infLog(`##########################createMeasure 2번실행 fbUseCase:: ${fbUseCase} `, infLogFlag);
            daCommon.createMeasure(dimension, measure2);

            infLog(`##########################createMeasure 후 fbUseCase:: ${fbUseCase} `, infLogFlag);

            arrUseCase = parsedParams.fb_UseCaseDemand;
            // arrUseCase.forEach(useCase => {
            //     NSCMCommon.createDimension(['[Version].[Version Name]','[Biz Case].[Biz Case]','[Group].[Group ID]']
            //         ,['CWV_MP',fbBizCase,useCase]);
            // });

            // //Cartesian 처리
            parsedParams.useCaseDemandList = daUtil.fn_multiArr(arrUseCase);

            let iArrSeq = 0;
            arrUseCase.forEach(useCase => {

                infLog(`##########################createMeasure 전 00 fbUseCaseDemend:: ${useCase} `, infLogFlag);

                dimension = [`[Version].[Version Name].[${parsedParams.fb_Version}]`
                                ,"[Biz Case].[Biz Case].[" + fbBizCase + "]"
                                ,"[Group].[Group ID].["+useCase+"]"];
                
                measure1 = [`Measure.[Biz Case Master_Creation Time] = dateadd(Now(),0,"hour");`
                                    ,`Measure.[Biz Case Master_Created By] = "${sUserId}";`
                        ];
                infLog(`##########################createMeasure 3번실행 fbUseCase:: ${fbUseCase} `, infLogFlag);
                daCommon.createMeasure(dimension, measure1);

                measure2 = [//`Measure.[Biz Case Use Case Asn_Override Seq] = "${arrSeq[iArrSeq]}";`
                                    `Measure.[Biz Case Use Case Asn_Creation Time] = dateadd(Now(),0,"hour");`
                                    ,`Measure.[Biz Case Use Case Asn_Created By] = "${sUserId}";`
                        ];
                infLog(`##########################createMeasure 4번실행 fbUseCase:: ${fbUseCase} `, infLogFlag);

                daCommon.createMeasure(dimension, measure2);

                iArrSeq++;

                infLog(`##########################createMeasure 후 fbUseCaseDemend:: ${useCase} `, infLogFlag);

            });

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    let fn_GetBizCodeMaxCode = function (parsedParams) {
        let maxSeq = '';
        infLog(`[fn_GetBizCodeMaxCode] parsedParams:${JSON.stringify(parsedParams)}`, infLogFlag);

        /* 1. Retrieves the largest Seq under a given condition. */
        let resultSet = QueryCommon.selectMaxBizCaseIdList(parsedParams).cs;
        if (resultSet.rowCount === 0) {
            /* 1-1. If there is no search result, assign '1'. */
            maxSeq = 'BC_001';
        } else {
            bizCode = resultSet.row(0).cell(resultSet.memberColumnIndex('Biz Case', 'Biz Case')).Name;
            bizNum = bizCode.split("_")[1]

            /* 1-2. If there is a search result, allocate the retrieved Seq + 1. */
            maxSeq = 'BC_'+(Number(bizNum) + 1).toString().padStart(3,'0');
        }

        /* 2. Returns the generated new Seq. */
        return maxSeq;
    };

    let fn_useCaseOBJCombo = function(o9Params) {
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        parsedParams.fb_Version = parsedParams.fb_Version1;
        const resultSet = QueryCommon.selectUseCase_OBJ(parsedParams);

        /* property를 DisplayAlias 변환*/
        let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Group", "Group ID", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(returnSet, {DimName : "Group", DimAttbName : "Group ID", Sort : "Name", isDisplayNameWithCode : true});

        return comboList;
    }

    let fn_useCaseDMDCombo = function(o9Params) {
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        parsedParams.fb_Version = parsedParams.fb_Version2;
        const resultSet = QueryCommon.selectUseCase_DMD(parsedParams);

        /* property를 DisplayAlias 변환*/
        let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Group", "Group ID", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(returnSet, {DimName : "Group", DimAttbName : "Group ID", Sort : "Name", isDisplayNameWithCode : true});

        return comboList;
    }

    let fn_useCaseOBJComboSel = function(o9Params) {
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
		parsedParams.bizCaseID = parsedParams.fb_dsBizCaseID;
        parsedParams.fb_Version = parsedParams.fb_Version3;

        const resultSet = QueryCommon.selectUseCase_OBJSel(parsedParams);

        /* property를 DisplayAlias 변환*/
        let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Group", "Group ID", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(returnSet, {DimName : "Group", DimAttbName : "Group ID", Sort : "Name", isDisplayNameWithCode : true});

        return comboList;
    }

    let fn_useCaseDMDComboSel = function(o9Params) {
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        parsedParams.bizCaseID = parsedParams.fb_dsBizCaseID2;
        parsedParams.fb_Version = parsedParams.fb_Version4;
        
        const resultSet = QueryCommon.selectUseCase_DMDSel(parsedParams);

        /* property를 DisplayAlias 변환*/
        let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Group", "Group ID", "Description");

        /*  DisplayName(Code)  combo return */
        let comboList = daCommon.fn_makeCombo(returnSet, {DimName : "Group", DimAttbName : "Group ID", Sort : "Name", isDisplayNameWithCode : true});

        return comboList;
    }

    let fn_ValidationBizCase =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;

        daUtil.fn_validationMultiRowCheck(tupleList);
    }

    
    let fn_ValidationDeleteBizCase =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;
        let useBizCase = '';
        
        returnValue = daUtil.fn_validationMultiRowCheck(tupleList);

        if(returnValue > 0) return returnValue;
        
        tupleList.forEach(element => {
            parsedParams.fb_BizCaseID = element.fb_BizCase.Value;
            let cntBizCaseValid = QueryCommon.selectCountDeleteBizCaseValid(parsedParams);
            if(cntBizCaseValid > 0) {
                useBizCase += parsedParams.fb_BizCaseID + ",";
            }
        });
        if(useBizCase != ''){
            let arrUseBizCase = useBizCase.split(',');
            arrUseBizCase = arrUseBizCase.splice(0, arrUseBizCase.length-1);
            RuleOutputToUI = { Status : 'Error', Message : "(" + arrUseBizCase.join(", ") + ") BizCaseID is being used in the Scenario Management. "};
            returnValue = 1;
        }

        return returnValue;
    }


    let fn_addBizCase = function(o9Params){
        fn_createBizCase(o9Params);
    };

    let fn_copyBizCase = function(o9Params){
        fn_createBizCase(o9Params);
    };

    let fn_setUseCase = function(o9Params){
        try {

            let parsedParams = JSON.parse(o9Params);
            let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
            let useBizCase = '';
            let sUserId = daCommon.fn_getUserId();

            //Use Case 삭제
            // parsedParams.fb_BizCaseID = element.fb_BizCase.Value;
            QueryCommon.deleteModelUseCase(parsedParams);

            //Use Case 입력
            let fbBizCase = parsedParams.fb_BizCaseID;
            let fbUseCase = parsedParams.fb_UseCase;
            let len_fb_UseCaseDemand = parsedParams.fb_UseCaseDemand.length;
            let strLen = '';
            let arrSeq = [];
            for(let i=0;i<len_fb_UseCaseDemand;i++){
                let num = i+2;
                strLen += "["+num.toString()+"],";
                arrSeq.push(num);
            }
            if(len_fb_UseCaseDemand>0) strLen = strLen.slice(0,-1);

            QueryCommon.updateMemberGroupIDDescription(fbBizCase, parsedParams);

            let dimension = [`[Version].[Version Name].[${parsedParams.fb_Version}]`
                            ,"[Biz Case].[Biz Case].[" + fbBizCase + "]"
                            ,"[Group].[Group ID].[" + fbUseCase + "]"];

            let measure2 = [
                //`Measure.[Biz Case Use Case Asn_Override Seq]="1";`
                `Measure.[Biz Case Use Case Asn_Creation Time] = dateadd(Now(),0,"hour");`
                ,`Measure.[Biz Case Use Case Asn_Created By] = "${sUserId}";`
            ];

            infLog(`##########################createMeasure 2번실행 fbUseCase:: ${fbUseCase} `, infLogFlag);
            daCommon.createMeasure(dimension, measure2);

            infLog(`##########################createMeasure 후 fbUseCase:: ${fbUseCase} `, infLogFlag);

            arrUseCase = parsedParams.fb_UseCaseDemand;
            // arrUseCase.forEach(useCase => {
            //     NSCMCommon.createDimension(['[Version].[Version Name]','[Biz Case].[Biz Case]','[Group].[Group ID]']
            //         ,['CWV_MP',fbBizCase,useCase]);
            // });

            // //Cartesian 처리
            parsedParams.useCaseDemandList = daUtil.fn_multiArr(arrUseCase);

            let iArrSeq = 0;
            arrUseCase.forEach(useCase => {

                infLog(`##########################createMeasure 전 00 fbUseCaseDemend:: ${useCase} `, infLogFlag);

                dimension = [`[Version].[Version Name].[${parsedParams.fb_Version}]`
                                ,"[Biz Case].[Biz Case].[" + fbBizCase + "]"
                                ,"[Group].[Group ID].["+useCase+"]"];
                
                measure2 = [//`Measure.[Biz Case Use Case Asn_Override Seq] = "${arrSeq[iArrSeq]}";`
                                    `Measure.[Biz Case Use Case Asn_Creation Time] = dateadd(Now(),0,"hour");`
                                    ,`Measure.[Biz Case Use Case Asn_Created By] = "${sUserId}";`
                        ];
                infLog(`##########################createMeasure 4번실행 fbUseCase:: ${fbUseCase} `, infLogFlag);

                daCommon.createMeasure(dimension, measure2);

                iArrSeq++;

                infLog(`##########################createMeasure 후 fbUseCaseDemend:: ${useCase} `, infLogFlag);

            });


        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    let fn_deleteBizCase = function(o9Params){
        try {

            let parsedParams = JSON.parse(o9Params);
            let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
            let tupleList = parsedParams.fb_TupleList;
            let useBizCase = '';

            tupleList.forEach(element => {
                parsedParams.fb_BizCaseID = element.fb_BizCase.Value;
                QueryCommon.deleteModelUseCase(parsedParams);
                QueryCommon.deleteMemberBizCase(parsedParams);
            });

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }

    };

    /******************************************************************************************************************/
    /* QUERY COMMON START *********************************************************************************************/
    class QueryCommon {

        static selectMaxBizCaseIdList(params) {
            let query =
                `Select (
                    [Biz Case].[Biz Case]
                    ) on row,
                    () on column
                    orderby [Biz Case].[Biz Case].Name desc 
                    limit 1;`

            return daCommon.selectQueryList('selectMaxBizCaseIdList', query);
        }

        static selectUseCase_OBJ(params) {
            let query =
            //// ABBizCaseDefinitionAddList // ds_UseCaseUSE_OBJ // Use Case (목적식)
            `select (Group.[Group Type].[USE_OBJ].relatedmembers([Group ID])) on row, 
                () on column
            where {
                    Version.[Version Name].[${params.fb_Version}]
            }
            orderby [Group].[Group ID].Key asc;
            `;
            return daCommon.selectQueryList('selectUseCase_OBJ', query);
        }

        static selectUseCase_DMD(params) {
            let query =
            //// ABBizCaseDefinitionAddList // ds_UseCaseUSE_DMD // Use Case (Demand)
            `select (Group.[Group Type].[USE_DMD].relatedmembers([Group ID])) on row,
                () on column
                where {
                    Version.[Version Name].[${params.fb_Version}]
                    , Measure.[Scenario Demand Mod_Created By] != ""
                }
                orderby [Group].[Group ID].Key asc;
            `;
            return daCommon.selectQueryList('selectUseCase_DMD', query);
        }

        static selectUseCase_OBJSel(params) {
            let query =
            //// ABBizCaseDefinitionAddList // ds_UseCaseUSE_OBJ // Use Case (목적식)
            `select (
                    [Group].[Group Type].[USE_OBJ].relatedmembers([Group ID])
                    ) on row,
                    () on column
                    where {
                        Version.[Version Name].[${params.fb_Version}]
                        , [Biz Case].[Biz Case].[${params.bizCaseID}]
                        , Measure.[Biz Case Use Case Asn_Created By] != ""
                    };
            `;
            infLog(`##########################selectUseCase_OBJSel:: ${params.bizCaseID} `, infLogFlag);
            return daCommon.selectQueryList('selectUseCase_OBJSel', query);
        }

        static selectUseCase_DMDSel(params) {
            let query =
            //// ABBizCaseDefinitionAddList // ds_UseCaseUSE_DMD // Use Case (Demand)
            `select (
                    [Group].[Group Type].[USE_DMD].relatedmembers([Group ID])
                    ) on row,
                    () on column
                    where {
                        Version.[Version Name].[${params.fb_Version}]
                        , [Biz Case].[Biz Case].[${params.bizCaseID}]
                        , Measure.[Biz Case Use Case Asn_Created By] != ""
                    };
            `;
            infLog(`##########################selectUseCase_DMDSel:: ${params.bizCaseID} `, infLogFlag);
            return daCommon.selectQueryList('selectUseCase_DMDSel', query);
        }


        static selectCountDeleteBizCaseValid(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[${parsedParams.fb_Version}]`
                ,'[Scenario].[Scenario]'
                ,`[Biz Case].[Biz Case].[${parsedParams.fb_BizCaseID}]`
            ]
            let sMeasure = '';
            let sWhere = 'where {Measure.[Scenario Biz Case Asn_Asn] == 1}';
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        }

        static updateMemberGroupIDDescription(fbBizCaseID, parsedParams) {
            let query =`
                updatemember(
                    [Biz Case].[Biz Case] = {, "${fbBizCaseID}"}, [Biz Case].[Description] = {"${parsedParams.fb_BizCase}", }
                );
                `;
            infLog("##########################updateMemberGroupIDDescription:: "+query);
            return daCommon.executeQuery('updateMemberGroupIDDescription', query);
        };        

        static deleteModelUseCase(parsedParams) {
            let query = `
                delete data for model [Biz Case Use Case Asn]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}],
                    [Biz Case].[Biz Case].[${parsedParams.fb_BizCaseID}]
                };
            `;
            infLog("##########################deleteModelBizCase:: "+query);
            return daCommon.executeQuery('deleteModelBizCase', query);
        };

        static deleteMemberBizCase(parsedParams) {
            let query = `
                deletemember([Biz Case].[Biz Case] = {,[${parsedParams.fb_BizCaseID}]});
            `;
            infLog("##########################deleteMemberBizCase:: "+query);
            return daCommon.executeQuery('deleteMemberBizCase', query);
        };

    }
    /* QUERY COMMON END ***********************************************************************************************/
    /******************************************************************************************************************/

    return{
            fn_useCaseCombo : daCommon.fn_decorator(fn_useCaseCombo)
            ,fn_useCaseOBJCombo : daCommon.fn_decorator(fn_useCaseOBJCombo)
            ,fn_useCaseDMDCombo : daCommon.fn_decorator(fn_useCaseDMDCombo)
            ,fn_useCaseOBJComboSel : daCommon.fn_decorator(fn_useCaseOBJComboSel)
            ,fn_useCaseDMDComboSel : daCommon.fn_decorator(fn_useCaseDMDComboSel)
            ,fn_ValidationBizCase : daCommon.fn_decorator(fn_ValidationBizCase)
            ,fn_ValidationDeleteBizCase : daCommon.fn_decorator(fn_ValidationDeleteBizCase)
        /* Add Biz. Case 버튼 */
            ,fn_addBizCase : daCommon.fn_decorator(fn_addBizCase)
        /* Copy Biz. Case 버튼 */
            ,fn_copyBizCase : daCommon.fn_decorator(fn_copyBizCase)
        /* Delete Biz. Case 버튼 */
            ,fn_deleteBizCase : daCommon.fn_decorator(fn_deleteBizCase)
        /* Set Use Case 버튼 */
            ,fn_setUseCase : daCommon.fn_decorator(fn_setUseCase)
    };
});