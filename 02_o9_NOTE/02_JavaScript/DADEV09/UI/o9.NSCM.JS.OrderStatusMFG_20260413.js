define('o9.NSCM.JS.OrderStatusMFG', ['o9.NSCM.commonLibDA','o9.NSCM.JS.LoadingDirOrderMgmt'], function(commonLib, mgmtLib)
{
    /**
     * o9.NSCM.JS.LoadingOrderStatus.
     *
     *  Loading Dir Order Status 화면
     */
/**********************************************************************************************************************/
/***************** CONST 설정 ****************************************************************************/
/**********************************************************************************************************************/
    /* Program Name */
    const programName = "o9.NSCM.JS.LoadingOrderStatus";

 /* jsErrorMsg   */
    const jsErrorMsg = "An error occurred during the simulation. \n Please contact the system administrator.";

     /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
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

    const simulInfoMsg = 'Simulation needs to be re-run.';

/**********************************************************************************************************************/
/***************** COMBO List START **********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** COMBO List END ************************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** TRANSACTION START *********************************************************************/
/**********************************************************************************************************************/
    /* ADD Action Button    */
    let fn_ExcPYUIDirOrderMFG =  function(o9Params) {
        let parsedParams = JSON.parse(o9Params);
        let tupleList = parsedParams.fb_TupleList;
        let userId = daCommon.fn_getUserName();   //Daeun01.yun@partner.samsung.com @앞에까지 ID  -> CurrentUser().[User Name] 으로 변경 by Miss.Lee 25.08.22
        parsedParams.userId = userId;
        let queryStr = '';
        let grainStrArr = [];

        tupleList.forEach(
            item =>{
                    item.userId = userId;
                    item.fb_Version = parsedParams.fb_Version;
                    const grainStr = [
                        item.fb_SOCreate.Value
                        , item.fb_SiteFrom.Value
                        , item.fb_SiteTo.Value
                        , item.fb_AP1.Value
                        , item.fb_Seq.Value
                        , item.fb_Item.Value
                        , item.fb_MADRDD.Value
                    ];
                    grainStrArr.push(grainStr.join("^"));
                }
        )

        // /* grain Arr 생성 */
        parsedParams.grainStrArr = daUtil.fn_multiArr(grainStrArr);
        try {
            let delListArr = [];
            let fromSite, toSite, account, shipTo, adjProdWeek, mgmtGrainStr, isJigLine, jig, line, simulatedBy;
            let mgmtGrainStrArr = [];
            /* 1. Order Status : _chk flag 'Y' , Confirmed By, Confirmed Time update */
            QueryCommon.executeScopeLoadingOrderStatus(parsedParams);

            /* 2. Loading Dir Order Status화면에서 check된 SO Item, Sales Order Measure값을 구하는 select쿼리*/
            const { soItemArr, salesOrderArr } = fn_SelectOrderStatusMFGSoItem(parsedParams);
            /* 3. 가져온 Order Status SO Item, Sales Order 배열값으로 해당되는 DirOrderMgmt row를 가져온다. */
            let resultSet = QueryCommon.selectDirOrderMgmtList({ soItemArr, salesOrderArr, fb_Version : parsedParams.fb_Version });
        
            if(resultSet.cs.rowCount !== 0) {
                for(let i=0; i < resultSet.cs.rowCount; i++){
                    fromSite = daCommon.getMember(resultSet.cs, i, "Sub Location", "Sub Location");
                    toSite = daCommon.getMember(resultSet.cs, i, "Location", "Location");
                    account = daCommon.getMember(resultSet.cs, i, "Sales Domain", "Ship To");
                    shipTo = daCommon.getMeasureValue(resultSet.cs, i, "Loading Dir Order Mgmt_Ship To");
                    adjProdWeek = daCommon.getMeasureValue(resultSet.cs, i, "Loading Dir Order Mgmt_Adj Prod Week");
                    mgmtGrainStr = daCommon.getMeasureValue(resultSet.cs, i, "Loading Dir Order Mgmt_Chk Grain");
                    simulatedBy = daCommon.getMeasureValue(resultSet.cs, i, "Loading Dir Order Mgmt_Simulated By");
                    isJigLine = daCommon.getMeasureValue(resultSet.cs, i, "Loading Dir Order Cal Master_JIG Line");
                    jig = daCommon.getMeasureValue(resultSet.cs, i, "Loading Dir Order Cal Master_JIG");
                    line = daCommon.getMeasureValue(resultSet.cs, i, "Loading Dir Order Cal Master_Line");

                    let delKeyArr = [adjProdWeek, fromSite.Name, toSite.Name, account.Name, shipTo];
                    let jigLineValue = daUtil.fn_nvl(jig, '') + daUtil.fn_nvl(line, '')
                    /* 동일 경로 기준(삭제 key) : adj prod week + from + jigLineValue + to + account + shipTo */
                    if(isJigLine && !daUtil.fn_isEmpty(jigLineValue)){
                        delKeyArr = [ adjProdWeek, fromSite.Name, jigLineValue, toSite.Name, account.Name, shipTo];
                    }

                    /* 기존 simulation 존재 건(simulatedBy가 있는 건) 에 대해 삭제 key List 생성   */
                    if(!daUtil.fn_isEmpty(simulatedBy)) {
                        delListArr.push(delKeyArr.join("_"));
                    }

                    mgmtGrainStrArr.push(mgmtGrainStr);
                }

                mgmtGrainStr = daUtil.fn_multiArr(mgmtGrainStrArr);
            }

            if(delListArr.length > 0){
                /* 3. 동일경로 mgmt 업데이트, container planning 메저그룹 delete */
                parsedParams.delListArr = delListArr;
                // o9.NSCM.JS.LoadingDirOrderMgmt js fn_delDirOrderMgmtRelatedMember함수 호출
                mgmtLib.fn_delDirOrderMgmtRelatedMember(JSON.stringify(parsedParams));
            }

            if(!daUtil.fn_isEmpty(mgmtGrainStr)){
                /* 4. delete Order Status SO Item, Sales Order 해당되는 DirOrderMgmt row삭제*/
                QueryCommon.deleteDirOrderMgmtSoItemList({ fb_Version : parsedParams.fb_Version, mgmtGrainStr });
            }

            /* PYUILoadingDirOrderStatusREG 파이썬 실행   */
            QueryCommon.executePYUIOrderStatusMFGREG(parsedParams);

        } catch(e){
            let errMsg =  jsErrorMsg;
            if (e === "Val Error") {
                errMsg = "check validation.." ;
            }
            RuleOutputToUI = {Status: 'Error', Message: errMsg };

            /* 파이썬 에러 및 exception이 떨어지면,  flag , confirmed By null로 update (내가 confirmed By 인 건만) */
            QueryCommon.executeScopeOrderStatusMFGChkNull(parsedParams);
        }
    }

    let fn_SelectOrderStatusMFGSoItem = function(parsedParams){
        let paramObj = {};
        paramObj['fb_Version'] = parsedParams.fb_Version;
        paramObj['userId'] = parsedParams.userId;
        let soItemArr = [];
        let salesOrderArr = [];
        /* Order Status check 된 row의 So Item, Sales Order measure 가져오기 위한 select */
        let resultSet = QueryCommon.selectOrderStatusMFGSoItem(paramObj);

        if(resultSet.cs.rowCount !== 0) {
            for(let i=0; i < resultSet.cs.rowCount; i++){
                soItemArr.push(daCommon.getMeasureValue(resultSet.cs, i, 'Order Status Mfg Week_SO Item'));
                salesOrderArr.push(daCommon.getMeasureValue(resultSet.cs, i, 'Order Status Mfg Week_SO'));
            }
        }

        return {soItemArr: soItemArr, salesOrderArr: salesOrderArr};
    }

/**********************************************************************************************************************/
/***************** TRANSACTION END ***********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** QUERY COMMON START  *******************************************************************/
/**********************************************************************************************************************/
    class QueryCommon {
        static executeScopeLoadingOrderStatus(params){
            let query =
                `scope: ([Version].[Version Name].[${params.fb_Version}]);
                        Measure.[Order Status Mfg Week_Chk Flag] = 
                            if( Measure.[Order Status Mfg Week_Chk Grain] in {${params.grainStrArr}} ) then "Y";
                        Measure.[Order Status Mfg Week_Confirmed By] = 
                            if( Measure.[Order Status Mfg Week_Chk Grain] in {${params.grainStrArr}} ) then "${params.userId}";
                        Measure.[Order Status Mfg Week_Confirm time] = 
                            if( Measure.[Order Status Mfg Week_Chk Grain] in {${params.grainStrArr}} ) then  Now();
                end scope;`;

            daCommon.executeQuery('executeScopeLoadingDirOrderStatus', query);
        }

        static executeScopeOrderStatusMFGChkNull(params){
            let query =
                `scope: ([Version].[Version Name].[${params.fb_Version}]);
                    Measure.[Order Status Mfg Week_Chk Flag] =
                        if(    Measure.[Order Status Mfg Week_Chk Grain] in {${params.grainStrArr}}
                            && Measure.[Loading Order Status_Confirmed By] == "${params.userId}" ) then null;
                    Measure.[Order Status Mfg Week_Confirmed By] =
                        if(    Measure.[Order Status Mfg Week_Chk Grain] in {${params.grainStrArr}}
                            && Measure.[Loading Order Status_Confirmed By] == "${params.userId}" ) then null;
                    Measure.[Order Status Mfg Week_Confirm time] = 
                        if(Measure.[Order Status Mfg Week_Chk Grain] in {${params.grainStrArr}}) then null;                        
                end scope;`;
            daCommon.executeQuery('executeScopeLoadingOrderStatusChkNull', query);
        }

        static selectOrderStatusMFGSoItem(params){
            let query = `
                select (
                    [Version].[Version Name].[${params.fb_Version}]
                    * [Sub Location].[Sub Location]
                    * [Location].[Location]
                    * [Sales Domain].[Ship To]
                    * [Item].[Item] 
                    * [Time].[Day]
                    * [Seq].[Seq]
                    * [Common Code Master].[Master Code]
                ) on row,
                ({
                    Measure.[Order Status Mfg Week_SO],
                    Measure.[Order Status Mfg Week_SO Item]
                }) on column
                where {
                    Measure.[Order Status Mfg Week_Confirmed By] == "${params.userId}",
                    Measure.[Order Status Mfg Week_Chk Flag] == "Y"
                };            
            `
            return daCommon.selectQueryList('selectOrderStatusMFGSoItem', query);
        }

        static selectDirOrderMgmtList(params){
            Log.Info(`##########################selectDirOrderMgmtList params:: ${params.soItemArr}`);
            let soItemArr = params.soItemArr;
            let salesOrderArr = params.salesOrderArr;
            const str_select_where = soItemArr.map((soVal, index) =>
                `(Measure.[Loading Dir Order Mgmt_SO Item] == "${soVal}" && Measure.[Loading Dir Order Mgmt_Sales Order] == "${salesOrderArr[index]}")`
            ).join(' ||\n\t');
            // Log.Info(`##########################selectDirOrderMgmtList str_select_where:: ${str_select_where}`);
            let query=
                `Select (   
                             [Version].[Version Name].[${params.fb_Version}] 
                           * [Sub Location].[Sub Location] 
                           * [Location].[Location] 
                           * [Sales Domain].[Ship To] 
                           * [Item].[Item]   
                           * [Time].[Week] 
                           * [Seq].[Seq]
                         ) on row, 
                        ({
                              Measure.[Loading Dir Order Mgmt_Ship To]
                            , Measure.[Loading Dir Order Mgmt_Adj Prod Week]
                            , Measure.[Loading Dir Order Mgmt_Simulated By]
                            , Measure.[Loading Dir Order Mgmt_Chk Grain]                                
                            , Measure.[Loading Dir Order Cal Master_JIG Line]
                            , Measure.[Loading Dir Order Cal Master_JIG] 
                            , Measure.[Loading Dir Order Cal Master_Line]
                        }) on column
                where {
                        ${str_select_where}
                      };`
            return daCommon.selectQueryList('selectDirOrderMgmtList', query);
        }

        static deleteDirOrderMgmtSoItemList(params){
            let soItemArr = params.soItemArr;
            let salesOrderArr = params.salesOrderArr;
            let mgmtGrainStr = params.mgmtGrainStr;
            let query =
                `delete data for model [Loading Dir Order Mgmt] 
                 where {  
                          [Version].[Version Name].[${params.fb_Version}]
                        , Measure.[Loading Dir Order Mgmt_Chk Grain] in {${mgmtGrainStr}}
                       };`;

            daCommon.executeQuery('deleteDirOrderMgmtSoItemList', query);
        }

        static executePYUIOrderStatusMFGREG(params){
            let query =
                `EXEC plugin instance [PY_UI_OrderStatusMFG_REG]
                 for measures { [Order Status Mfg Week_Chk Flag] }
                    using scope ([Version].[Version Name].[${params.fb_Version}])
                    using arguments {(ExecutionMode, "MediumWeight")
                                  , (Param_OUT_VERSION, "${params.fb_Version}")
                                  , (Param_User_Name , CurrentUser().[User Name])
                                  , (MaxSliceTableCells, 200000000)
                                  , (MaxConcurrency, 1 )
                                  , (IncludeNullRows, False)
                                  , ([Param.o9_sys_log_level], "DEBUG")
                                  }
                    ;`

            return daCommon.executeQuery('executePYUILoadingDirOrderStatusREG', query);
        }
    }

/**********************************************************************************************************************/
/***************** QUERY COMMON END  *********************************************************************/
/**********************************************************************************************************************/

    return {
        fn_ExcPYUIDirOrderMFG : daCommon.fn_decorator(fn_ExcPYUIDirOrderMFG)
    };

});