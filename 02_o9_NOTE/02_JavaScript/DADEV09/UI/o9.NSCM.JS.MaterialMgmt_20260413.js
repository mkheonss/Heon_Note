define('o9.NSCM.JS.MaterialMgmt', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.MaterialMgmt.
     *
     * MaterialMgmt 공용
     * 
     * Master Data > Procurement > Material Mgmt. > Material Mgmt.
     */

    /*********************************************************************/
    /**************************** const 설정 *****************************/
    /*********************************************************************/
    /* Program Name */
    const programName = 'o9.NSCM.JS.MaterialMgmt';

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
          - Master Data > Procurement > Material Mgmt. > Material Mgmt.
        대상 버튼 : Edit 'Material Mgmt' information
          - Action Button > ABMaterialMgmtEdit > 버튼 로딩시 Config > Validate
        Action Button > Config > Validate
          - Multi Row가 선택되면 Message 처리
    */
    let fn_ValidationMultiRowSelectionCheck = function(o9Params){
        const parsedParams = JSON.parse(o9Params);
        const tupleList = parsedParams.fb_TupleList;
        let returnValue = 0; // 0: 정상, 1: 오류메세지
    
        return daUtil.fn_validationMultiRowCheck(tupleList);
    };


    /** fn_SubmitEditMaterialMgmt
        대상 UI :
          - Master Data > Procurement > Material Mgmt. > Material Mgmt.
        대상 버튼 : Edit 'Material Mgmt' information
          - Action Button > ABMaterialMgmtEdit > Submit 버튼 실행
          - Multi Row가 선택되면 Message 처리
          - Single Row 선택시 Scenario Status가 Not Editable 이면 Message 처리
    */
    let fn_SubmitEditMaterialMgmt = function(o9Params){
        daCommon.infLog(`[fn_SubmitEditMaterialMgmt] o9Params:${o9Params}`, infLogFlag);
        /* parsed Param */
        const parsedParams = JSON.parse(o9Params);
        // User ID & Name
        parsedParams.userId = daCommon.fn_getUserId();
        parsedParams.userName = daCommon.fn_getUserName();

        // Map Status = 'CON' 상태일경우 Group2, Group2 Detail 항목 누락시 'Error' 체크
        // fb_Group2와 fb_Group2Detail 값 검사
        const fb_Group2Trimmed = parsedParams.fb_Group2 ? parsedParams.fb_Group2.trim() : '';
        const fb_Group2DetailTrimmed = parsedParams.fb_Group2Detail ? parsedParams.fb_Group2Detail.trim() : '';

        if (parsedParams.fb_MapStatus === 'CON') {

            if (!parsedParams.fb_Group2 || fb_Group2Trimmed === '' || !parsedParams.fb_Group2Detail || fb_Group2DetailTrimmed === '') {
                Log.Info("########################## CON 인 경우, fb_Group2 와 fb_Group2Detail 값 필수 입력해야 함");
                // 함수 종료: return;은 OK, 하지만 에러를 던지거나 다른 처리를 추가할 수 있음
                throw new Error("필수 값이 누락 : 'CON' 인 경우 Group2와 Group2Detail은 필수 입력입니다.");  // 또는 return false; 등
            } else {
                // 값 업데이트
                QueryCommon.executeUpdateMaterialMgmt(parsedParams);
            }

        } else {
            // 값 업데이트
            QueryCommon.executeUpdateMaterialMgmt(parsedParams);

        }
    }
    /*******************************************************************************/
    /**********************??? TRANSACTION END ???************************/
    /*******************************************************************************/



    /*******************************************************************************/
    /*********************??? QUERY COMMON START ???*********************/
    /*******************************************************************************/
    class QueryCommon {

        static executeUpdateMaterialMgmt(parsedParams) {
            let query =`
                scope: (
                    [Version].[Version Name].[CWV_MP]
                    * [Sub Location].[Sub Location].[${parsedParams.fb_Plant}]
                    * [Item Raw Material].[Item Raw Material].[${parsedParams.fb_Material}]
                );                
                    Measure.[Mat Master_Group1] = "${parsedParams.fb_Group1}";
                    Measure.[Mat Master_Group1 (Filter)] = "${parsedParams.fb_Group1}";
                    Measure.[Mat Master_Product Group] = "${parsedParams.fb_ProductGroup}";
                    Measure.[Mat Master_Group2] = "${daUtil.fn_trim(parsedParams.fb_Group2)}";
                    Measure.[Mat Master_Group2 (Filter)] = "${daUtil.fn_trim(parsedParams.fb_Group2)}";
                    Measure.[Mat Master_Group2 Detail] = "${daUtil.fn_trim(parsedParams.fb_Group2Detail)}";
                    Measure.[Mat Master_Map Status] = "${parsedParams.fb_MapStatus}";
                    Measure.[Mat Master_Mst Update time] = dateadd(Now(),0,"hour");
                    Measure.[Mat Master_Mst Updated by] = "${parsedParams.userName}";
                end scope;
                `
            // Log.Info("########################## executeUpdateMaterialMgmts:: "+query);
            return daCommon.executeQuery('executeUpdateMaterialMgmt', query);
        };

    }



    /**************************************************************************************************/
    /******************??? return start  o9.NSCM.JS.MaterialMgmt ???******************/
    /*************************************************************************************************/
    return {
        fn_ValidationMultiRowSelectionCheck: daCommon.fn_decorator(fn_ValidationMultiRowSelectionCheck)
        , fn_SubmitEditMaterialMgmt: daCommon.fn_decorator(fn_SubmitEditMaterialMgmt)
    };
});