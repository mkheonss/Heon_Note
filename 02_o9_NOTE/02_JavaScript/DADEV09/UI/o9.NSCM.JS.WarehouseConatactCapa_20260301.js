define('o9.NSCM.JS.WarehouseConatactCapa', ['o9.NSCM.commonLibDA'], function(commonLib)
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
    const programName = "o9.NSCM.JS.WarehouseConatactCapa";

    /* jsErrorMsg   */
    const jsErrorMsg = "Please contact the system administrator.";

    /* setting  */
    let daCommon = new commonLib.DACommon(programName);
    daCommon.setLogLevel("Debug")
    let daUtil = new commonLib.DAUtil();

    const scenarioType = "What if";

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

        // 0. valid check
        sPhysical_WH = parsedParams.fb_PhysicalWarehouse;
        sNSCM_WH = parsedParams.fb_NSCMWarehouse;

        //valid
        const regex = /^[a-zA-Z0-9_\/ ]*$/; // 영문 숫자 중간공백 _/ 만 허용
        if ((!regex.test(sPhysical_WH))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters in Physical W/H."};
            return;
        }

        if ((!regex.test(sNSCM_WH))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters in NSCM W/H."};
            return;
        }

        sPhysical_WH = sPhysical_WH.toUpperCase().trim();
        sNSCM_WH = sNSCM_WH.toUpperCase().trim();

        let iMaxCBM = parsedParams.fb_MAXCBM;
        if(iMaxCBM>=1000000000) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter the MAX CBM value within 9 digits."};
            return;
        }


        // 0.중복 검사
        let countQuery = `[Warehouse].[Warehouse].[${sPhysical_WH}]`;
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            RuleOutputToUI = {Status: 'Error', Message: "Warehouse is duplicated."};
            return;
        }

        parsedParams.fb_PhysicalWarehouse = sPhysical_WH;
        parsedParams.fb_NSCMWarehouse = sNSCM_WH;

        let resultSet = QueryCommon.selectCountryName(parsedParams);
        if(resultSet.cs.rowCount !== 0){
            parsedParams.fb_NationName = daCommon.getMember(resultSet.cs, 0, 'Country', 'Country').DisplayName;
        }else {
            parsedParams.fb_NationName = "-";
        }
        Log.Info("fb_NationName >>>>>>>>>>>>>>>> " + parsedParams.fb_NationName);
        
        
        // 1. max Seq 찾기 : ( Nation + sequence + 1 )
        resultSet = QueryCommon.selectMaxWarehouseID(parsedParams);
        if(resultSet.cs.rowCount !== 0) {
            let iValue = daCommon.getPropertyValue(resultSet.cs, 0, "Warehouse", "Warehouse", "Warehouse ID");
            Log.Info("iValue >>>>>>>>>>>>>>>> " + iValue);

            iValue = (iValue==null||iValue=='') ? '0000': iValue.slice(-4);
            sequence = Number(iValue) + 1;
        }

        Log.Info("sequence >>>>>>>>>>>>>>>> " + sequence);
        let s_sequence = '_'+ String(sequence).padStart(4, '0');
        // 2. WarehouseID 생성
        warehouseID = parsedParams.fb_NationName.concat(s_sequence);

        Log.Info("warehouseID >>>>>>>>>>>>>>>> " + warehouseID);

        //warehouseID setting
        parsedParams.warehouseID = warehouseID;
        
        // 3.creatememberWarehouseID
        QueryCommon.creatememberWarehouseID(parsedParams);
        QueryCommon.updatememberWarehouseIDproperty(parsedParams);
        QueryCommon.updatememberNationDisplayName(parsedParams);
        QueryCommon.updatememberNationName(parsedParams);

        // 4.cartesian scope WHContractCapa
        QueryCommon.insert_cartesianScopeWHContractCapa(parsedParams);

    }

    /* Edit Submit   */
    let fn_EditWarehouseID = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let warehouseID;


        let iMaxCBM = parsedParams.fb_MAXCBM;
        if(iMaxCBM>=1000000000) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter the MAX CBM value within 9 digits."};
            return;
        }
        
        // 2. WarehouseID 전달
        warehouseID = parsedParams.fb_WarehouseID;

        Log.Info("warehouseID >>>>>>>>>>>>>>>> " + warehouseID);

        //warehouseID setting
        parsedParams.warehouseID = warehouseID;

        // 3.creatememberWarehouseID
        // QueryCommon.creatememberWarehouseID(parsedParams);

        // 4.cartesian scope WHContractCapa
        QueryCommon.update_cartesianScopeWHContractCapa(parsedParams);

    }

    /* Delete Submit   */
    let fn_DeleteWarehouse = function(o9Params){

        let parsedParams = JSON.parse(o9Params);
        // 사용자Id
        parsedParams.userId = daCommon.fn_getUserName();
        let tupleList = parsedParams.fb_TupleList;

        tupleList.forEach(element => {
            parsedParams.warehouseID = element.fb_WarehouseID.Value;
            QueryCommon.deleteWarehouseContractCapacityW(parsedParams);
            QueryCommon.deleteModelWarehouseContractCapacity(parsedParams);
            QueryCommon.deleteMemberWarehouseContractCapacity(parsedParams);
        });
    };

    /*  
        fn_ValidationWarehouse : Multirow check 후 copy 버튼 클릭 시 retrun 1
    */
    let fn_ValidationWarehouse =  function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let returnValue = 0;                            /* 0: 정상, 1: 오류메세지  */
        let tupleList = parsedParams.fb_TupleList;

        daUtil.fn_validationMultiRowCheck(tupleList);
    };
    

    let fn_ValidAddWarehouse = function(o9Params){
        //valid
        let parsedParams = JSON.parse(o9Params);
        
        let sPhysical_WH = parsedParams.fb_PhysicalWarehouse;
        let sNSCM_WH = parsedParams.fb_NSCMWarehouse;

        const regex = /^[a-zA-Z0-9_\/ ]*$/; // 영문 숫자 중간공백 _/ 만 허용
        if ((!regex.test(sPhysical_WH))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters in Physical W/H."};
            return false;
        }

        if ((!regex.test(sNSCM_WH))) {
            RuleOutputToUI = {Status: 'Error', Message: "Please enter letters in NSCM W/H."};
            return false;
        }

        sPhysical_WH = sPhysical_WH.toUpperCase().trim();
        sNSCM_WH = sNSCM_WH.toUpperCase().trim();

        Log.Info("fn_ValidAddWarehouse >>>>>>>>>>>>>>>> " + sNSCM_WH);
        // 0.중복 검사
        let countQuery = `[Warehouse].[Physical Warehouse].[${sPhysical_WH}]*[Warehouse].[SCM Warehouse].[${sNSCM_WH}]*[Warehouse].[Warehouse Region].[${parsedParams.fb_Region}]*[Warehouse].[Warehouse Nation].[${parsedParams.fb_Nation}]`;
        let iCountExist = daCommon.selectCount(countQuery);

        if(iCountExist > 0) {
            Log.Info("fn_ValidAddWarehouse iCountExist >>>>>>>>>>>>>>>> " + iCountExist);
            // RuleOutputToUI = {Status: 'Error', Message: "Warehouse is duplicated."};
            return false;
        }

        // parsedParams.fb_PhysicalWarehouse = sPhysical_WH;
        // parsedParams.fb_NSCMWarehouse = sNSCM_WH;
        return true;
    };

    let fn_SelectMaxCBM = function(o9Params){
        let parsedParams = JSON.parse(o9Params);
        let query = `
            Select ([Warehouse].[Warehouse].[${parsedParams.fb_Warehouse}] ) on row, 
            ({Measure.[WH Contract Capa_Max CBM]}) on column
            where {
                [Version].[Version Name].CWV_MP
            };
        `;

        let resultSet =  daCommon.selectQueryList('fn_SelectMaxCBM', query);
        let sCBM = daCommon.getMeasureValue(resultSet.cs, 0, 'WH Contract Capa_Max CBM');
        return {'Name': sCBM}
    };

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
    
    // let fn_SelectRegion = function(o9Params){
    //     let parsedParams = JSON.parse(o9Params);
    //     let query = `
    //         Select ([Warehouse].[Warehouse].[${parsedParams.fb_Warehouse}] ) on row, 
    //         ({Measure.[WH Contract Capa_Region]}) on column
    //         where {
    //             [Version].[Version Name].CWV_MP
    //         };
    //     `;

    //     let resultSet =  daCommon.selectQueryList('fn_SelectRegion', query);
    //     let sRewion = daCommon.getMeasureValue(resultSet.cs, 0, 'WH Contract Capa_Region');
    //     return {'Name': sRewion}
    // };

/**********************************************************************************************************************/
/***************** TRANSACTION END ***********************************************************************/
/**********************************************************************************************************************/

/**********************************************************************************************************************/
/***************** QUERY COMMON START  *******************************************************************/
/**********************************************************************************************************************/
    class QueryCommon {
        static selectCountryName(parsedParams) {
            let query = `
                select ([Country].[Country].[${parsedParams.fb_Nation}]) on row;
            `;
            return daCommon.selectQueryList('selectCountryName', query);
        };


        static selectMaxWarehouseID(params) {
            let query =
                `Select (
                            [Version].[Version Name].[${params.fb_Version}]
                            * [Warehouse].[Warehouse Nation].[${params.fb_Nation}] 
                            * [Warehouse].[Warehouse] 
                        ) on row, 
                        ({ 
                            Measure.[WH Contract Capa_Created By]
                            , Measure.[WH Contract Capa_Creation Time]
                            , Measure.[WH Contract Capa_Max CBM]
                            , Measure.[WH Contract Capa_Update Time]
                            , Measure.[WH Contract Capa_Updated By]
                        }) on column
                orderby [Warehouse].[Warehouse].[Warehouse ID] desc limit 1;`;

            return daCommon.selectQueryList('selectMaxWarehouseID', query);
        };

        static creatememberWarehouseID(params){
            // let query =
            //     `createmember ( [Warehouse].[Warehouse] = {,"${params.warehouseID}"},
            //                     [Warehouse].[Physical Warehouse] = {,"${params.fb_PhysicalWarehouse}"},
            //                     [Warehouse].[SCM Warehouse] = {,"${params.fb_NSCMWarehouse}"},
            //                     [Warehouse].[Warehouse Region] = {,"${params.fb_Region}"},
            //                     [Warehouse].[Warehouse Nation] = {,"${params.fb_Nation}"}
            //                 );`;
            let query =
                `createmember ( [Warehouse].[Warehouse] = {,"${params.fb_PhysicalWarehouse}"},
                                [Warehouse].[SCM Warehouse] = {,"${params.fb_NSCMWarehouse}"},
                                [Warehouse].[Warehouse Region] = {,"${params.fb_Region}"},
                                [Warehouse].[Warehouse Nation] = {,"${params.fb_Nation}"}
                            );`;

            daCommon.executeQuery('creatememberWarehouseID', query);
        };

        static updatememberWarehouseIDproperty(params){
            let query = 
            `updatemember([Warehouse].[Warehouse]={,"${params.fb_PhysicalWarehouse}"}
                        , [Warehouse].[Warehouse ID]={"${params.warehouseID}",}
                        );`;

            daCommon.executeQuery('updatememberWarehouseIDproperty', query);
        };


        static updatememberNationDisplayName(params){
            let query = 
            `updatemember([Warehouse].[Warehouse Nation]={,"${params.fb_Nation}"}
                        , [Warehouse].[Warehouse Nation$DisplayName]={"${params.fb_Nation}",}
                        );`;

            daCommon.executeQuery('updatememberNationDisplayName', query);
        };

        static updatememberNationName(params){
            let query = 
            `updatemember([Warehouse].[Warehouse Nation]={,"${params.fb_Nation}"}
                        , [Warehouse].[Warehouse Nation Name]={"${params.fb_NationName}",}
                        );`;

            daCommon.executeQuery('updatememberNationName', query);
        };

        static insert_cartesianScopeWHContractCapa(params){
            let query=
                `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                  * [Warehouse].[Warehouse].[${params.fb_PhysicalWarehouse}]
                                );
                    Measure.[WH Contract Capa_Created By] = "${params.userId}";
                    Measure.[WH Contract Capa_Creation Time] = dateadd(Now(),0,"hour");
                    Measure.[WH Contract Capa_Max CBM] = ${params.fb_MAXCBM};
                end scope;
                
                cartesian scope:( 
                                    [Version].[Version Name].[${params.fb_Version}]
                                    * [Warehouse].[Warehouse].[${params.fb_PhysicalWarehouse}]
                                    * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key 
                                                            && #.Key <= &CurrentWeek.element(0).LeadOffset(34).Key)
                                );
                    Measure.[WH Contract Capa W_CBM] = ${params.fb_MAXCBM};   
                end scope;
                `;

            daCommon.executeQuery('insert_cartesianScopeWHContractCapa', query);
        };

        static update_cartesianScopeWHContractCapa(params){
            let query=
                `cartesian scope:(
                                    [Version].[Version Name].[${params.fb_Version}]
                                  * [Warehouse].[Warehouse].[${params.fb_WarehouseID}]
                                );
                    Measure.[WH Contract Capa_Updated By] = "${params.userId}";
                    Measure.[WH Contract Capa_Update Time] = dateadd(Now(),0,"hour");
                    Measure.[WH Contract Capa_Max CBM] = ${params.fb_MAXCBM};
                end scope;

                cartesian scope:( 
                                    [Version].[Version Name].[${params.fb_Version}]
                                    * [Warehouse].[Warehouse].[${params.fb_WarehouseID}]
                                    * [Time].[Week].filter(#.Key >= &CurrentWeek.element(0).LeadOffset(0).Key 
                                                            && #.Key <= &CurrentWeek.element(0).LeadOffset(34).Key)
                                );
                    Measure.[WH Contract Capa W_CBM] = ${params.fb_MAXCBM};   
                end scope;
                `;

            daCommon.executeQuery('update_cartesianScopeWHContractCapa', query);
        };

        /*  
            deleteWarehouseContractCapacityW : Delete의 Submit 버튼 클릭시 delete data model
        */
        static deleteWarehouseContractCapacityW(parsedParams) {
            let query = `
                delete data for model [Warehouse Contract Capacity W]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}],
                    [Warehouse].[Warehouse].[${parsedParams.warehouseID}]
                };
            `;
            // infLog("##########################deleteWarehouseContractCapacityW:: "+query);
            return daCommon.executeQuery('deleteWarehouseContractCapacityW', query);
        };
    
        /*  
            deleteModelWarehouseContractCapacity : Delete의 Submit 버튼 클릭시 delete data model
        */
        static deleteModelWarehouseContractCapacity(parsedParams) {
            let query = `
                delete data for model [Warehouse Contract Capacity]
                where {
                    [Version].[Version Name].[${parsedParams.fb_Version}],
                    [Warehouse].[Warehouse].[${parsedParams.warehouseID}]
                };
            `;
            // infLog("##########################deleteModelWarehouseContractCapacity:: "+query);
            return daCommon.executeQuery('deleteModelWarehouseContractCapacity', query);
        };

        /*  
            deleteMemberWarehouseContractCapacity : Delete의 Submit 버튼 클릭시 delete member
        */
            static deleteMemberWarehouseContractCapacity(parsedParams) {
                let query = `
                    deletemember([Warehouse].[Warehouse] = {,[${parsedParams.warehouseID}]}) cascade;
                    purge members([Warehouse].[Warehouse]);
                `;
                // infLog("##########################deleteModelWarehouseContractCapacity:: "+query);
                return daCommon.executeQuery('deleteModelWarehouseContractCapacity', query);
            };
    }

/**********************************************************************************************************************/
/***************** QUERY COMMON END  *********************************************************************/
/**********************************************************************************************************************/

    return {
            //add warehouseID
            fn_AddWarehouseID : daCommon.fn_decorator(fn_AddWarehouseID)
            , fn_EditWarehouseID : daCommon.fn_decorator(fn_EditWarehouseID)
            , fn_ValidationWarehouse : daCommon.fn_decorator(fn_ValidationWarehouse)
            , fn_ValidAddWarehouse : daCommon.fn_decorator(fn_ValidAddWarehouse)
            , fn_SelectMaxCBM : daCommon.fn_decorator(fn_SelectMaxCBM)
            // , fn_SelectRegion : daCommon.fn_decorator(fn_SelectRegion)
            , fn_DeleteWarehouse : daCommon.fn_decorator(fn_DeleteWarehouse)
    };

});