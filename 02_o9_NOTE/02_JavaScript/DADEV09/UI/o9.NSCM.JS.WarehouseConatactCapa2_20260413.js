define('o9.NSCM.JS.WarehouseConatactCapa2', ['o9.NSCM.commonLibDA'], function(commonLib)
{
    /**
     * o9.NSCM.JS.WarehouseConatactCapa.
     *
     *  Master Data > Logistics > Ocean Contract Mgmt > Warehouse Contract Capa.
     */
/**********************************************************************************************************************/
/***************** CONST 설정 ****************************************************************************/
/**********************************************************************************************************************/
    /* Program Name */
    const programName = "o9.NSCM.JS.WarehouseConatactCapa2";

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
    /* Add Submit   */
    let fn_AddWarehouseID = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let sequence = 1;
        let warehouseID;

         // 1. max Seq 찾기 : ( Nation + sequence + 1 )
        let resultSet = QueryCommon.selectMaxWarehouseID(parsedParams);
        if(resultSet.cs.rowCount !== 0) {
            sequence = Number((daCommon.getMember(resultSet.cs, 0, "Warehouse", "Warehouse").Name).slice(-4)) + 1;
        }

        Log.Info("sequence >>>>>>>>>>>>>>>> " + sequence);

        // 2. WarehouseID 생성
        warehouseID = parsedParams.fb_Nation.concat(String(sequence).padStart(4, '0'));

        Log.Info("warehouseID >>>>>>>>>>>>>>>> " + warehouseID);

        //warehouseID setting
        parsedParams.warehouseID = warehouseID;

        // 3.creatememberWarehouseID
        QueryCommon.creatememberWarehouseID(parsedParams);

        // 4.cartesian scope WHContractCapa
        QueryCommon.cartesianScopeWHContractCapa(parsedParams);

    }
    let fn_SelectMaxCBM = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let query = `
            Select ([Warehouse].[Warehouse].[${parsedParams.fb_Warehouse}] ) on row, 
            ({Measure.[WH Contract Capa W_CBM]}) on column
            where {
                [Version].[Version Name].CWV_MP
            };
        `;

        let resultSet =  daCommon.selectQueryList('fn_SelectMaxCBM', query);
        let wCBM = daCommon.getMeasureValue(resultSet.cs, 0, 'WH Contract Capa W_CBM');
        return {'Name': wCBM}
    }

    let fn_SelectMaxCBM2 = function(o9Params){
        Log.Info("777777777777777777777777777777777777777777777777777777)");
        let parsedParams = JSON.parse(o9Params);
        let query = `
            Select ([Warehouse].[Warehouse].[${parsedParams.fb_Warehouse}] ) on row, 
            ({Measure.[WH Contract Capa W_CBM]}) on column
            where {
                [Version].[Version Name].CWV_MP
            };
        `;

        let resultSet =  daCommon.selectQueryList('fn_SelectMaxCBM', query);
        let wCBM = daCommon.getMeasureValue(resultSet.cs, 0, 'WH Contract Capa W_CBM');
        return {'Name': wCBM}
    }
/**********************************************************************************************************************/
/***************** TRANSACTION END ***********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** QUERY COMMON START  *******************************************************************/
/**********************************************************************************************************************/
    class QueryCommon {
        static selectMaxWarehouseID(params) {
            let query =
                `Select (
                              [Version].[Version Name].[${params.fb_Version}] 
                            * [Warehouse].[Warehouse] 
                        ) on row, 
                        ({ 
                              Measure.[WH Contract Capa_Created By]
                            , Measure.[WH Contract Capa_Creation Time]
                        }) on column
                where { 
                            Measure.[WH Contract Capa_Nation] == "${params.fb_Nation}" 
                       }
                orderby [Warehouse].[Warehouse].Name desc limit 1;`;

            return daCommon.selectQueryList('selectMaxWarehouseID', query);
        }

        static creatememberWarehouseID(params){
             let query =
                `createmember ( [Warehouse].[Warehouse] = {,"${params.warehouseID}"},
                                [Warehouse].[Physical Warehouse] = {,"${params.fb_PhysicalWarehouse}"},
                                [Warehouse].[SCM Warehouse] = {,"${params.fb_NSCMWarehouse}"}
                               );`;

            daCommon.executeQuery('creatememberWarehouseID', query);
        }

        static cartesianScopeWHContractCapa(params){
             let query=
                 `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                  * [Warehouse].[Warehouse].[${params.warehouseID}]
                                  );
                    Measure.[WH Contract Capa_Created By] = "${params.userId}";
                    Measure.[WH Contract Capa_Creation Time] = dateadd(Now(),0,"hour");
                    Measure.[WH Contract Capa_Max CBM] = ${params.fb_MAXCBM};
                    Measure.[WH Contract Capa_Nation] = "${params.fb_Nation}";
                    Measure.[WH Contract Capa_Region] = "${params.fb_Region}";
                 end scope;
                 
                 cartesian scope:( 
                                      [Version].[Version Name].[${params.fb_Version}]
                                    * [Warehouse].[Warehouse].[${params.warehouseID}]
                                    * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key 
                                                          && #.Key <= &CurrentWeek.element(0).LeadOffset(34).Key)
                                );
                    Measure.[WH Contract Capa W_CBM] = null;   
                end scope;
                 `;

             daCommon.executeQuery('cartesianScopeWHContractCapa', query);
        }

    }

/**********************************************************************************************************************/
/***************** QUERY COMMON END  *********************************************************************/
/**********************************************************************************************************************/

    return {
            //add warehouseID
            fn_AddWarehouseID : daCommon.fn_decorator(fn_AddWarehouseID)
            , fn_SelectMaxCBM : daCommon.fn_decorator(fn_SelectMaxCBM)
            , fn_SelectMaxCBM2 : daCommon.fn_decorator(fn_SelectMaxCBM2)
    };

});