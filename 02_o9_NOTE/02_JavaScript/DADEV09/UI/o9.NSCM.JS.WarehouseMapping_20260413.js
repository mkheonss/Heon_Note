define('o9.NSCM.JS.WarehouseMapping', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.WarehouseMapping.
     *
     *  Master Data > Logistics > Ocean Contract Mgmt > Warehouse Mapping
     */
/**********************************************************************************************************************/
/***************** CONST 설정 ****************************************************************************/
/**********************************************************************************************************************/
    /* Program Name */
    const programName = "o9.NSCM.JS.WarehouseMapping";

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
    /*  
        fn_ValidationWarehouseMapping : Multirow check 후 copy 버튼 클릭 시 retrun 1
    */
        let fn_ValidationWarehouseMapping =  function(o9Params){
            let parsedParams = JSON.parse(o9Params);
            let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
            let tupleList = parsedParams.fb_TupleList;
    
            daUtil.fn_validationMultiRowCheck(tupleList);
        };
    

    let fn_UpdateWHMapping = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();

        QueryCommon.cartesianScopeWHMapping(parsedParams);
    };
/**********************************************************************************************************************/
/***************** TRANSACTION END ***********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** QUERY COMMON START  *******************************************************************/
/**********************************************************************************************************************/
    class QueryCommon {

        static cartesianScopeWHMapping(params){
            let query=
                `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                 * [Location].[Location].[${params.fb_SiteID}]
                                );
                    Measure.[WH Mapping_Updated By] = "${params.userId}";
                    Measure.[WH Mapping_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[WH Mapping_Map Status] = "${params.fb_MapStatus}";
                    Measure.[WH Mapping_SCM Warehouse] = "${params.fb_NSCMWarehouse}";
                    Measure.[WH Mapping_Valid Flag] = "${params.fb_Valid}";
                end scope;
                `;

            daCommon.executeQuery('cartesianScopeWHContractCapa', query);
        };

    }


/**********************************************************************************************************************/
/***************** QUERY COMMON END  *********************************************************************/
/**********************************************************************************************************************/

    return {
            //fn_UpdateWHMapping
            fn_UpdateWHMapping : daCommon.fn_decorator(fn_UpdateWHMapping)
            ,fn_ValidationWarehouseMapping : daCommon.fn_decorator(fn_ValidationWarehouseMapping)

    };

});