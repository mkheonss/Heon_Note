define('o9.NSCM.JS.StockpileItem', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.StockpileItem.
     *
     *  SCM > SOP Smoothing > SOP Smoothing > Stockpile Item
     */
/**********************************************************************************************************************/
/***************** CONST 설정 ****************************************************************************/
/**********************************************************************************************************************/
    /* Program Name */
    const programName = "o9.NSCM.JS.StockpileItem";

    /* jsErrorMsg   */
    const jsErrorMsg = "Please contact the system administrator.";

    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

/**********************************************************************************************************************/
/***************** COMBO List START **********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** COMBO List END ************************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** TRANSACTION START *********************************************************************/
/**********************************************************************************************************************/


    function validateFiveChars(context) {
        if (context) {
            if (context.Location.length !== 5) {
                throw "입력값은 정확히 5자리여야 합니다.";
            }
        }
        return context;
    }

    /* Stockpile Item Add Submit   */
    let fn_AddStockpileItem = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();

        let sFromSite = parsedParams.fb_FromSite;
        let sBASEItem = parsedParams.fb_BASEItem;
        let sStockpileItem = parsedParams.fb_StockpileItem;

        //공백제거
        sFromSite = sFromSite.split(' ').join('').trim();
        sBASEItem = sBASEItem.split(' ').join('').trim();
        sStockpileItem = sStockpileItem.split(' ').join('').trim();

        //영문숫자_/만, 20자까지 허용
        const regex = /^[A-Za-z0-9_\/]+$/; // 영문숫자_/만 허용
        if ((!regex.test(sStockpileItem))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters and numbers."};
            return;
        }

        if(sStockpileItem.length > 20) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter 20 letters."};
            return;
        }

        //코드 대문자화
        sStockpileItem = sStockpileItem.toUpperCase();

        // // 1.중복 검사
        // let countQuery =`[Version].[Version Name].[${parsedParams.fb_Version}]*[Sub Location].[Sub Location].[${sFromSite}]*[Item].[Item].[${sBASEItem}]`;

        // let iCountExist = daCommon.selectCount(countQuery);

        // if(iCountExist > 0) {
        //     RuleOutputToUI = {Status: 'Error', Message: "Stockpile Item is duplicated."};
        //     return;
        // }

        parsedParams.fb_FromSite = sFromSite;
        parsedParams.fb_BASEItem = sBASEItem;
        parsedParams.fb_StockpileItem = sStockpileItem;

        // 3.cartesian scope
        QueryCommon.insert_cartesianScopeStockpileItem(parsedParams);

    };

    /* Loading Delete Submit */
    let fn_DeleteStockpileItem = function(o9Params){
        let parsedParams = JSON.parse(o9Params);

        let tupleList = parsedParams.fb_TupleList;

        tupleList.forEach(element => {

            parsedParams.fb_FromSite = element.fb_FromSite.Value;
            parsedParams.fb_BASEItem = element.fb_BASEItem.Value;

            //delete model
            QueryCommon.deleteStockpileItem(parsedParams);
        });

    };

    /*  
        fn_ValidMultiSelect : Multirow check 후 copy 버튼 클릭 시 retrun 1
    */
    let fn_ValidMultiSelect =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;

        daUtil.fn_validationMultiRowCheck(tupleList);

    };


/**********************************************************************************************************************/
/***************** TRANSACTION END ***********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** QUERY COMMON START  *******************************************************************/
/**********************************************************************************************************************/
    class QueryCommon {

        static insert_cartesianScopeStockpileItem(params){
        
            let query=
                `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                  * [Sub Location].[Sub Location].[${params.fb_FromSite}]
                                  * [Item].[Item].[${params.fb_BASEItem}]
                                );
                    Measure.[Stockpile Item_Stockpile Item] = "${params.fb_StockpileItem}";
                    Measure.[Stockpile Item_Created By] = "${params.userId}";
                    Measure.[Stockpile Item_Creation Time] = dateadd(Now(),0,"hour");
                end scope;
            `;
            daCommon.executeQuery('insert_cartesianScopeStockpileItem', query);
        };


        /*  
            selectCountLoadingValidFlagStatus : isValid 'N' 체크 Validation
        */
        static selectCountLoadingValidFlagStatus(parsedParams) {

            let lstDimension = [
                `[Version].[Version Name].[CWV_MP]`
                ,`[Loading Port].[Loading Port].[${parsedParams.fb_LoadingPort}]`
            ]
            let sMeasure = '';
            let sWhere = `where {Measure.[Loading Port Mapping_Valid Flag] == "N"}`;
            return daCommon.selectListCount(lstDimension, sMeasure, sWhere);
        };
                

        static deleteStockpileItem(parsedParams) {
            let query = `
                delete data for model [Stockpile Item]
                where {
                    [Version].[Version Name].[CWV_MP],
                    [Sub Location].[Sub Location].[${parsedParams.fb_FromSite}],
                    [Item].[Item].[${parsedParams.fb_BASEItem}]
                };
            `;
            // infLog("##########################deleteStockpileItem:: "+query);
            return daCommon.executeQuery('deleteStockpileItem', query);
        };

    
    }

/**********************************************************************************************************************/
/***************** QUERY COMMON END  *********************************************************************/
/**********************************************************************************************************************/

    return {
        //add StockpileItem
        fn_AddStockpileItem : daCommon.fn_decorator(fn_AddStockpileItem),
        //delete StockpileItem
        fn_DeleteStockpileItem : daCommon.fn_decorator(fn_DeleteStockpileItem),

        //fn_ValidMultiSelect
        fn_ValidMultiSelect : daCommon.fn_decorator(fn_ValidMultiSelect),

    };

});