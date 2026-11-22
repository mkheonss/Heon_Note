define('o9.NSCM.JS.MaterialShortAnalysis', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.MaterialShortAnalysis
     *
     * MaterialShortAnalysis 공용
     * 
     * Procurement > Analysis > Material Short Analysis > Material Short Analysis
     */

    /*********************************************************************/
    /**************************** const 설정 *****************************/
    /*********************************************************************/
    /* Program Name */
    const programName = 'o9.NSCM.JS.MaterialShortAnalysis';

    /* jsErrorMsg   */
    const jsErrorMsg = 'An error occurred during the Scenario Management. \n Please contact the system administrator.';

    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug");
    let daUtil = new commonLib.DAUtil();

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
    }

    /**
     * Prints the given parameters.
     *
     * @param {Array} params - The parameters to be printed.
     */
    let printParams = function(params) {
        daCommon.printParams(params);
    }

    /**
    * Print function init Log
    * @param {Object} arg - function arguments
    * @o9Params {String} o9Params - screen parameter
    */
    let initLog = function(arg, o9Params){
        let funcName = arg.callee.name;
        log(`${funcName} : ${o9Params}`);
    }



    /*******************************************************************************/
    /********************??? combo list 구성 함수 ???*********************/
    /*******************************************************************************/

    // /* Biz Case fb_BizCase Combo */
    // let fn_bizCaseCombo = function(o9Params){
    //     /* parsed Param */
    //     const parsedParams = JSON.parse(o9Params);

    //     const resultSet = QueryCommon.selectBizCaseMaster(parsedParams);

    //     /* property를 DisplayAlias 변환*/
    //     let returnSet = daCommon.fn_makeDisplayAlias(resultSet, "Biz Case", "Biz Case", "Description");

    //     /*  DisplayName(Code)  combo return */
    //     let comboList = daCommon.fn_makeCombo(returnSet, {DimName : "Biz Case", DimAttbName : "Biz Case", Sort : "Name", isDisplayNameWithCode : true});
    //     Log.Info("##########################");
    //     Log.Info(JSON.stringify(comboList));
    //     return comboList;
    // }

    /*******************************************************************************/
    /***********************??? combo list END ???************************/
    /*******************************************************************************/



    /*******************************************************************************/
    /**********************??? TRANSACTION START ???*********************/
    /*******************************************************************************/

    /** fn_ValidationMultiRowSelectionCheck
        대상 UI :
          - Procurement > Analysis > Material Short Analysis > Material Short Analysis
        대상 버튼 : Edit 'Material Constraint' information
          - Action Button > ABMaterialShortAnalysisRemarksEdit > 버튼 로딩시 Config > Validate
        Action Button > Config > Validate
          - Multi Row가 선택되면 Message 처리
    */
    let fn_ValidationMultiRowSelectionCheck = function(o9Params){
        const parsedParams = JSON.parse(o9Params);
        const tupleList = parsedParams.fb_TupleList;
        let returnValue = 0; // 0: 정상, 1: 오류메세지
    
        return daUtil.fn_validationMultiRowCheck(tupleList);
    };


    /** fn_SelectRemarks
        대상 UI :
          - Procurement > Analysis > Material Short Analysis > Material Short Analysis
        대상 버튼 : Edit 'Material Constraint' information
          - Action Button > ABMaterialShortAnalysisRemarksEdit > 버튼 로딩시 DataSource 로 조회
          - 선택된 행의 MDP [Mat Short Analysis_Remark] 값을 불러오기 위함
    */
    let fn_SelectRemarks = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let query = `
            Select ([Sub Location].[Sub Location].[${parsedParams.fb_Plant_ds}] * [Item Raw Material].[Item Raw Material].[${parsedParams.fb_Material_ds}] ) on row, 
            ({Measure.[Mat Short Analysis_Remark]}) on column
            where {
                [Version].[Version Name].CWV_MP
            };
        `;

        let resultSet =  daCommon.selectQueryList('fn_SelectRemarks', query);
        let sRemark = daCommon.getMeasureValue(resultSet.cs, 0, 'Mat Short Analysis_Remark');
        return {'Name': sRemark}
    };


    /** fn_SubmitEditMaterialShortAnalysis
        대상 UI :
          - Procurement > Analysis > Material Short Analysis > Material Short Analysis
        대상 버튼 : Edit 'Material Constraint' information
          - Action Button > ABMaterialShortAnalysisRemarksEdit > Submit 버튼 실행
          - Multi Row가 선택되면 Message 처리
          - Single Row 선택시 Scenario Status가 Not Editable 이면 Message 처리
    */
    let fn_SubmitEditMaterialShortAnalysis = function(o9Params){
        daCommon.infLog(`[fn_SubmitEditMaterialShortAnalysis] o9Params:${o9Params}`, infLogFlag);
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID & Name
        parsedParams.userId = daCommon.fn_getUserId();
        parsedParams.userName = daCommon.fn_getUserName()

        if (parsedParams.fb_Constraint === 'N') {
            // fb_Constraint가 'N'인 경우, fb_ConstraintPeriod를 체크
            if (parsedParams.fb_ConstraintPeriod != null && parsedParams.fb_ConstraintPeriod !== '') {
                // fb_ConstraintPeriod가 공백이나 Null이 아닌 경우 에러 발생
                throw new Error('Error: Constraint Period must be empty when Constraint is "N".');
            } else {
                // fb_ConstraintPeriod가 공백이나 Null인 경우, null을 기본값(예: 0)으로 대체하여 처리
                const safeParams = { ...parsedParams };  // 원래 객체 복사
                if (safeParams.fb_ConstraintPeriod == null) {
                    safeParams.fb_ConstraintPeriod = null;  // null을 0으로 대체하는 방법도 있음음
                }
                // 이제 안전한 파라미터로 쿼리 실행
                QueryCommon.executeUpdateMaterialShortAnalysis(safeParams);
            }

        } else {
            // 기존 MaterialShortAnalysis 값 변경
            QueryCommon.executeUpdateMaterialShortAnalysis(parsedParams);
        }
    }
    /*******************************************************************************/
    /**********************??? TRANSACTION END ???************************/
    /*******************************************************************************/



    /*******************************************************************************/
    /*********************??? QUERY COMMON START ???*********************/
    /*******************************************************************************/
    class QueryCommon {

        static executeUpdateMaterialShortAnalysis(parsedParams) {
            let query =`
                scope: (
                    [Version].[Version Name].[CWV_MP]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_Plant}]
                    * [Item Raw Material].[Item Raw Material].[${parsedParams.fb_Material}]
                );
                    Measure.[Mat Short Analysis_Remark] = "${daUtil.fn_trim(parsedParams.fb_Remark)}";
                    Measure.[Mat Short Analysis_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[Mat Short Analysis_Updated By] = "${parsedParams.userName}";
                end scope;
                `
            // Log.Info("########################## executeUpdateMaterialShortAnalysiss:: "+query);
            return daCommon.executeQuery('executeUpdateMaterialShortAnalysis', query);
        };

    }



    /**************************************************************************************************/
    /******************??? return start  o9.NSCM.JS.MaterialShortAnalysis ???******************/
    /*************************************************************************************************/
    return {
        fn_ValidationMultiRowSelectionCheck: daCommon.fn_decorator(fn_ValidationMultiRowSelectionCheck)
        , fn_SelectRemarks: daCommon.fn_decorator(fn_SelectRemarks)
        , fn_SubmitEditMaterialShortAnalysis: daCommon.fn_decorator(fn_SubmitEditMaterialShortAnalysis)
    };
});