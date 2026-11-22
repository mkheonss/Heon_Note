define('o9.NSCM.JSEWLCMTimePhasedBOD', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    /* 프로그램명 : o9.NSCM.JSEWLCMTimePhasedBOD                                                  */
    /* 화면명 : LCM Time Phased BOD (EW)                                                            */
    /* Action Button : EWLCMTimePhasedBOD                                                            */
    /* 최초생성 : 2025.08.22 / syif1380.lee                                                             */
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }
        
    const commonLib = require('o9.NSCM.commonLibVD');   // 2026.03.26 공통적용변경
    const cUtil = fn_cUtil();                           // 2026.03.26 공통적용변경

    const programName = "o9.NSCM.JSEWLCMTimePhasedBOD";
    const Horizon = "&MDMHorizon";
    const queryModule = require('o9/data/query');

	var fn_loadFunction = function(o9Params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

		try {
            let returnData = {};
            let obj = this;

            cLib.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
			var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            cLib.programEnd();
            return rtn;
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    /**
     * 주어진 값이 null or undefined or "null" 문자열이면 'null' 문자열을 반환하고,
     * 그 외의 값은 큰따옴표("") 로 감싼 문자열로 반환한다.
     * @param {any} val - 검사할 값 
     * @returns {String} 출력용 문자열 
     */
    var fn_formatValue = function(val){
        return (val === null || val === undefined || val === "null" ) ? 'null' : `"${val}"`;
    }

    /**
     * Reload Master
     * 배치 실행 프로그램
     * 
     * @param {*} o9Params 
     * @returns 
     */
    //======================[ PR_UI_BODListWLCM_OnDemand ] ============================
    // BOD Item까지 생성후, BOD Item W 데이터 생성 및 Backend Measure 생성.
    // BOD Item 생성 job 이후에 같이 돌아얗마.
    //BOD Item W 화면에서 AB(reload) 로도 호출됨
    /*
    Begin
    // BOD Item까지 생성후, BOD Item W 데이터 생성 및 Backend Measure 생성.
    // BOD Item 생성 job 이후에 같이 돌아얗마.
    //BOD Item W 화면에서 AB(reload) 로도 호출됨
    select ("=====> PR_UI_BODListWLCM_OnDemand - start");
    // 1.BOD Item W (LCM) 생성
    EXEC plugin instance [PY_UI_BODItemW_OnDemand] for measures {[BOD Item_Priority]} using scope ( &CWVUI * &MFStageLCMLocation * &MFStageSETSubLocation * &LCMItem )
    using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };
    // LCM 용 Alt : LCM BOD List 로 MG 변경 예정 2025.09.17
    // 2.BOD List 생성
    EXEC plugin instance [PY_UI_BODListW] for measures {[LCM BOD List W_BOD LT]} using scope ( &CWVUI )
    using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };
    // 3.Supply Filter Data 삭제
    delete data for model [LCM BOD List Prty] where {&CWVUI};
    delete data for model [BOD Item Prty] where {&CWVUI , &LCMItem};
    // 3-1. Supply Type 생성
    EXEC plugin instance [PY_UI_BODListW_SupplyFilterLCM] for measures {[BOD Item Prty_Supply Filter]} using scope ( &CWVUI )
    using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG") };
    // 4.Priority중복 체크
    EXEC plugin instance [PY_UI_BODItemLCMValid] for measures {[BOD Item_Eff Startdate]}
    using scope ( &CWVUI )
    using arguments {(ExecutionMode, "MediumWeight"), (pDetailLogFlag, "N") , (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )};
    // 5.사용자정보 update
    scope : (&CWVUI);
    Measure.[VersionInfo_Time Phased BOD LCM Master Update Time] = Now();
    Measure.[VersionInfo_Time Phased BOD LCM Master Update User] = CurrentUser().[User Name];
    end scope;
    select ("=====> PR_UI_BODListWLCM_OnDemand - end");
    // 6. BOD List 의 Valid 변경 건을 Time Phased 의 Valid 로 연결 (LCM BOD List / BOD Item)
    scope: (&CWVUI * [Location].[Location] * [Item].[Class Category] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode] ) ;
    Measure.[LCM BOD List W Sub_BOD Valid] = if(Measure.[LCM BOD List_BOD Valid]=="N") then "N" else Measure.[LCM BOD List W Sub_BOD Valid];
    end scope;
    // LCM 범위로 좁혀서 실행 2025.11.24 syif1380.lee
    scope: (&CWVUI * &MFStageLCMLocation * &LCMItem * &MFStageSETSubLocation * [Trans Mode].[Trans Mode] ) ;
    Measure.[BOD Item W Sub_BOD Valid] = if(Measure.[BOD Item_BOD Valid]=="N") then "N" else Measure.[BOD Item W Sub_BOD Valid];
    end scope;
    end;
    */
    var fn_execution = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            // Reload Master, Supply Type, Validation 실행
            // EXEC procedure PR_UI_BODListWLCM_Daily; => PR_UI_BODListWLCM_OnDemand 변경
            var execQuery = 'EXEC procedure PR_UI_BODListWLCM_OnDemand;';
            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("procedure Reload Master : PR_UI_BODListWLCM_OnDemand Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * Save
     * LCM BOD List W (그리드 Data) => 해당 Item.Class Category 에 해당하는 Item을 가져옴(BOD Item) => BOD Item W 데이터를 찾아 update
     * BOD Item W 상속될 당시 데이터 없는것을 Create 하지 않음.  
     * @param {*} o9Params 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                // LCM BOD List W : (Grain) Version, Location, SubLocation, Trans Mode, Product Group, Time Week
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let fbSubLocation = parsedParams.fbGridRows[i]["[Sub Location].[Sub Location]"];
                let fbTpMode = parsedParams.fbGridRows[i]["[Trans Mode].[Trans Mode]"];
                let fbClassCategory = parsedParams.fbGridRows[i]["[Item].[Class Category]"];

                let fbMeasurename = parsedParams.fbGridRows[i]["measurename"];

                if ( fbLocation     === null || fbLocation      === undefined || fbLocation     === "" ||
                     fbSubLocation  === null || fbSubLocation   === undefined || fbSubLocation  === "" ||
                     fbTpMode       === null || fbTpMode        === undefined || fbTpMode       === "" ||
                     fbClassCategory === null || fbClassCategory  === undefined || fbClassCategory === "" ||
                     fbMeasurename  === null || fbMeasurename   === undefined || fbMeasurename  === "" )
                {
                    return { "Code" : 1, "Msg" : "[Location].[Location] or [Sub Location].[Sub Location] or [Trans Mode].[Trans Mode] or [Item].[Class Category] or measurename 값이 존재하지 않음.", "Rows" : parsedParams.fbGridRows[i] };
                }

                // Measure
                //LCM BOD List W_Priority
                let fbBodLt = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W_BOD LT]"];
                let fbPriority = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W_Priority]"];
                let fbShipLt = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W_Shipment LT]"];

                // LCM BOD List W Sub  : (Grain) Version, Location, SubLocation, Trans Mode, Class Category
                // Category 별 Start/End Week 
                let fbBodLtStartWeek = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W Sub_BOD LT Startweek]"];
                let fbBodLtEndWeek = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W Sub_BOD LT Endweek]"];
                let fbPriorityStartWeek = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W Sub_Priority Startweek]"];
                let fbPriorityEndWeek = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W Sub_Priority Endweek]"];
                let fbShipmentLtStartWeek = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W Sub_Shipment LT Startweek]"]; 
                let fbShipmentLtEndWeek = parsedParams.fbGridRows[i]["Measure.[LCM BOD List W Sub_Shipment LT Endweek]"];

                let params = {};

                // LCM BOD List : dimension
                let dimProd = [cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                ,"[Location].[Location].[" + fbLocation + "]"
                                ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                                ,"[Trans Mode].[Trans Mode].[" + fbTpMode + "]"
                                ,"[Item].[Class Category].[" + fbClassCategory + "]"
                                ];

                // BOD List : dimension
                let dimBod = [cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                                ,"[Location].[Location].[" + fbLocation + "]"
                                ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                                ,"[Trans Mode].[Trans Mode].[" + fbTpMode + "]"
                                ];

                //================================================================================================================================//
                // [Item].[Product Group] 에 해당하는 BOD Item 을 조회한다.
                //================================================================================================================================//
                let dimItmeTmp = [...dimProd];
                dimItmeTmp.push("[Item].[Item]");
                let where = 'where { Measure.[BOD Item_Asn] == 1 , coalesce(Measure.[BOD Item_Lock Flag], "N") != "Y" } ';
                let rtnBodItemList = cLib.selectList(dimItmeTmp
                                                , ["Measure.[BOD Item_BOD LT]", "Measure.[BOD Item_Priority]", "Measure.[BOD Item_Shipment LT]", "Measure.[BOD Item_Lock Flag]"
                                                ,"Measure.[BOD Item_Eff Startweek]", "Measure.[BOD Item_Eff Endweek]", "Measure.[BOD Item_BOD Valid]"]
                                                , where, "", "");
                let getItemList = [];
                for ( k=0; k<rtnBodItemList.cs.rowCount; k++){

                    let getItem = rtnBodItemList.cs.row(k).cell(rtnBodItemList.cs.memberColumnIndex("Item", "Item")).Name;
                    getItemList.push(getItem);
                }
                // cLib.debug("###step: fn_save : BOD Item 갯수 > getItemList > "+getItemList.length);
                let dimBodItemKey = [];
                if( getItemList.length > 0){
                    dimBodItemKey = [...dimBod];
                    dimBodItemKey.push("[Item].[Item]"+cUtil.fn_filterStr(getItemList));
                    cLib.debug("###step: fn_save : BOD Item 조회 > "+dimBodItemKey);
                }

                //================================================================================================================================//
                // 주차 update (LCM BOD List W) > LCM BOD List W Sub (Startweek/Endweek): Update 
                //================================================================================================================================//
                ///// Measure.[LCM BOD List W Sub_BOD Valid] = if(Measure.[LCM BOD List_BOD Valid]=="N") then "N" else Measure.[LCM BOD List W Sub_BOD Valid];
                // Start/End Week Measure 정의
                let measureWeek = [];
                let measureItemWeek = [];
                if ( fbMeasurename == "LCM BOD List W_Priority"){
                    measureWeek = ['Measure.[LCM BOD List W Sub_Priority Startweek]  = "' + cUtil.fn_getString(fbPriorityStartWeek) + '";'
                                  ,'Measure.[LCM BOD List W Sub_Priority Endweek]   = "' + cUtil.fn_getString(fbPriorityEndWeek) + '";'];
                    measureItemWeek = ['Measure.[BOD Item W Sub_Priority Startweek]  = "' + cUtil.fn_getString(fbPriorityStartWeek) + '";'
                                      ,'Measure.[BOD Item W Sub_Priority Endweek]   = "' + cUtil.fn_getString(fbPriorityEndWeek) + '";'];
                } else if ( fbMeasurename == "LCM BOD List W_BOD LT"){
                    measureWeek = ['Measure.[LCM BOD List W Sub_BOD LT Startweek]  = "' + cUtil.fn_getString(fbBodLtStartWeek) + '";'
                                  ,'Measure.[LCM BOD List W Sub_BOD LT Endweek]    = "' + cUtil.fn_getString(fbBodLtEndWeek) + '";'];
                    measureItemWeek = ['Measure.[BOD Item W Sub_BOD LT Startweek]  = "' + cUtil.fn_getString(fbBodLtStartWeek) + '";'
                                      ,'Measure.[BOD Item W Sub_BOD LT Endweek]    = "' + cUtil.fn_getString(fbBodLtEndWeek) + '";'];
                } else if ( fbMeasurename == "LCM BOD List W_Shipment LT"){
                    measureWeek = ['Measure.[LCM BOD List W Sub_Shipment LT Startweek]  = "' + cUtil.fn_getString(fbShipmentLtStartWeek) + '";'
                                  ,'Measure.[LCM BOD List W Sub_Shipment LT Endweek]   = "' + cUtil.fn_getString(fbShipmentLtEndWeek) + '";'];
                    measureItemWeek = ['Measure.[BOD Item W Sub_Shipment LT Startweek]  = "' + cUtil.fn_getString(fbShipmentLtStartWeek) + '";'
                                      ,'Measure.[BOD Item W Sub_Shipment LT Endweek]   = "' + cUtil.fn_getString(fbShipmentLtEndWeek) + '";'];
                }
                if ( measureWeek.length > 0 ){
                    measureWeek.push(cUtil.fn_qMeaUpdateUserName("Measure.[LCM BOD List W Sub_Updated By]"));  // 추가 2026.01.28
                    measureWeek.push(cUtil.fn_qMeaUpdateTime("Measure.[LCM BOD List W Sub_Update Time]"));
                    cLib.updateMeasure(dimProd, measureWeek);
                }

                //================================================================================================================================//
                // 주차 update (BOD Item W) > BOD Item W Sub (Startweek/Endweek): Update 
                //================================================================================================================================//
                // let dimBodItemKey = [];
                if( getItemList.length > 0){
                    measureItemWeek.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item W Sub_Updated By]"));  // 추가 2026.01.28
                    measureItemWeek.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item W Sub_Update Time]"));
                    cLib.updateMeasure(dimBodItemKey, measureItemWeek);
                }

                //================================================================================================================================//
                // LCM BOD List W > Measure.[LCM BOD List W_Priority]  ex: "Measure.[LCM BOD List W_Priority]":["202508^2","202509^2","202510^2"]
                //================================================================================================================================//
                // 주차별 value
                if( fbPriority !== null && fbPriority !== undefined ){
                    // cLib.debug("###step: fn_save : =======================> 2-1 > LCM BOD List W_Priority");
                    params.bod  = {data:fbPriority, dimension:dimProd, measureGroup: "LCM BOD List W", measure: "Measure.[LCM BOD List W_Priority]"};
                    params.item = {data:fbPriority, dimension:dimBodItemKey, measureGroup: "BOD Item W", measure: "Measure.[BOD Item W_Prty]", itemList:getItemList};
                    fn_bodListW_update(params);
                }
                
                //================================================================================================================================//
                // LCM BOD List W > Measure.[LCM BOD List W_BOD LT]  ex: "Measure.[LCM BOD List W_BOD LT]":["202508^2","202509^2","202510^2"]
                //================================================================================================================================//
                if( fbBodLt !== null && fbBodLt !== undefined ){
                    // cLib.debug("###step: fn_save : =======================> 3-1 > LCM BOD List W_Priority");
                    params.bod  = {data:fbBodLt, dimension:dimProd, measureGroup: "LCM BOD List W", measure: "Measure.[LCM BOD List W_BOD LT]"};
                    params.item = {data:fbBodLt, dimension:dimBodItemKey, measureGroup: "BOD Item W", measure: "Measure.[BOD Item W_BOD LT]", itemList:getItemList};
                    fn_bodListW_update(params);
                }
                
                //================================================================================================================================//
                // LCM BOD List W > Measure.[LCM BOD List W_Shipment LT]  ex: "Measure.[LCM BOD List W_Shipment LT]]":["202508^2","202509^2","202510^2"]
                //================================================================================================================================//
                if( fbShipLt !== null && fbShipLt !== undefined ){
                    cLib.debug("###step: fn_save : =======================> 4-1 > LCM BOD List W_Shipment");
                    params.bod  = {data:fbShipLt, dimension:dimProd, measureGroup: "LCM BOD List W", measure: "Measure.[LCM BOD List W_Shipment LT]"};
                    params.item = {data:fbShipLt, dimension:dimBodItemKey, measureGroup: "BOD Item W", measure: "Measure.[BOD Item W_Shipment LT]", itemList:getItemList};
                    fn_bodListW_update(params);
                }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 신규 Data 생성은 없음, Update만 실행
     * 
     * 주차별 : BOD Prod SET W > Measure.[BOD Prod SET W_Priority] , Measure.[BOD Prod SET W_BOD LT], Measure.[BOD Prod SET W_Shipment LT]
     * 주차별 : BOD Item W     > Measure.[BOD Item W_Prty] , Measure.[BOD Item W_BOD LT], Measure.[BOD Item W_Shipment LT]
     * @param {*} params 
     * params.bod  = {data:fbPriority, dimension:dimProd, measureGroup: "BOD Prod SET W", measure: "Measure.[BOD Prod SET W_Priority]"};
     * params.item = {data:fbPriority, dimension:dimBodItemKey, measureGroup: "BOD Item W", measure: "Measure.[BOD Item W_Prty]", itemList:getItemList};
     * @returns 
     */

    var fn_bodListW_update = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {
            // cLib.debug("fn_save > fn_bodListW_update ==========================================================>시작");
            cLib.debug("params.bod :: "+JSON.stringify(params.bod));
            cLib.debug("params.item :: "+JSON.stringify(params.item));

            let bodProdData = params.bod;
            let bodItemData = params.item;

            // W_Update Time, W_Updated By 메저 삭제 2026.01.28
            // let measureProd = [cUtil.fn_qMeaUpdateTime("Measure.[LCM BOD List W_Update Time]")
            //                   ,cUtil.fn_qMeaUpdateUserName("Measure.[LCM BOD List W_Updated By]")];
            // let measureItem = [cUtil.fn_qMeaUpdateTime("Measure.[BOD Item W_Update Time]")
            //                   ,cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item W_Updated By]")];
            let measureProd = [];
            let measureItem = [];

            for ( var k=0; k < bodProdData.data.length; k++){
                
                let dataValue = bodProdData.data[k].split("^");
                // cLib.debug("###step: fn_save W : =======================> > [Time].[Week].["+dataValue[0]+"]  : value => " + dataValue[1] +" " );

                // BOD Prod SET W : week 별 Update (bodProdData : params.bod)
                let dimWeek = [...bodProdData.dimension];
                dimWeek.push("[Time].[Week].["+dataValue[0]+"]");
                measureProd.push(bodProdData.measure + ' = ' + (cUtil.fn_isInt(dataValue[1]) ? dataValue[1] : 'null') + ';');
                cLib.updateMeasure(dimWeek, measureProd);

                // BOD Item W : Week 별 Update (bodItemData : params.item)
                if( bodItemData.itemList.length > 0){
                    let dimItemWeek = [...bodItemData.dimension];
                    dimItemWeek.push("[Time].[Week].["+dataValue[0]+"]");
                    // cLib.debug("###step: fn_save : =======================> 2-3 > BOD Item : dimension > "+dimItemWeek);
                    measureItem.push(bodItemData.measure + ' = ' + (cUtil.fn_isInt(dataValue[1]) ? dataValue[1] : 'null') + ';');
                    cLib.updateMeasure(dimItemWeek, measureItem);
                }
            }

            cLib.programEnd();

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_merge : Scenario Plan >> 테스트 필요..
     * 2026.03.05 생성
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_merge = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_merge call ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            cLib.debug("fn_getFilterValue >>"+cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]"));

            // var fbVersion = parsedParams.fbParams["[Version].[Version Name]"];  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
            var fbVersion = cUtil.fn_getFilterValue(parsedParams, "[Version].[Version Name]");  // ew에서 버전이 어떻게 넘어 오는지??? (시나리오 버전)
            var toVersion = "[Version].[Version Name].[CWV_MP]";

            if( parsedParams.fbParams["mergeType"] == "1"){

                let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [LCM BOD List W Sub] '
                    + ',for model [LCM BOD List W] '
                    + ',for model [BOD Item W Sub] '
                    + ',for model [BOD Item W] '
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

            }else if( parsedParams.fbParams["mergeType"] == "0"){

                for ( var i=0; i<parsedParams.fbGridRows.alt.length; i++){

                    var row = parsedParams.fbGridRows.alt[i];
                    // dimension : LCM BOD List W Sub
                    let dimListSub = [];
                    dimListSub.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimListSub.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimListSub.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                    dimListSub.push(cUtil.fn_qDim(row, "[Item].[Class Category]"));

                    // dimension : LCM BOD List W
                    let dimListW = [...dimListSub];
                    dimListW.push(Horizon);

                    // dimension : BOD Item W Sub
                    let dimItemSub = [];
                    dimItemSub.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimItemSub.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimItemSub.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                    dimItemSub.push("[Item].[Item]");

                    // dimension : BOD Item W
                    let dimItemW = [...dimItemSub];
                    dimItemW.push(Horizon);

                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [LCM BOD List W Sub] using scope (' + dimListSub.join('*') + ')'
                    + ',for model [LCM BOD List W] using scope (' + dimListW.join('*') + ')'
                    + ',for model [BOD Item W Sub] using scope (' + dimItemSub.join('*') + ')'
                    + ',for model [BOD Item W] using scope (' + dimItemW.join('*') + ')'
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

                    //-------------------------------------------------------------------------------------
                    // LCM BOD List W Sub : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimListSubChk = [...dimListSub];
                    dimListSubChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimListSubChk, ["Measure.[LCM BOD List W Sub_BOD Valid]"], "") ){

                        dimListSub.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[LCM BOD List W Sub_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[LCM BOD List W Sub_Update Time]"));
                        cLib.updateMeasure(dimListSub, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // LCM BOD List W : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimListWChk = [...dimListW];
                    dimListWChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimListWChk, ["Measure.[LCM BOD List W_Update Time]"], "") ){

                        dimListW.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[LCM BOD List W_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[LCM BOD List W_Update Time]"));
                        cLib.updateMeasure(dimListW, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // BOD Item W Sub : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimItemSubChk = [...dimItemSub];
                    dimItemSubChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimItemSubChk, ["Measure.[BOD Item W Sub_BOD Valid]"], "") ){

                        dimItemSub.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[BOD Item W Sub_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item W Sub_Update Time]"));
                        cLib.updateMeasure(dimItemSub, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // BOD Item W : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimItemWChk = [...dimItemW];
                    dimItemWChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimItemWChk, ["Measure.[BOD Item W_Update Time]"], "") ){

                        dimItemW.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[BOD Item W_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item W_Update Time]"));
                        // Measure.[BOD Item W_PyRunFlag]  구현한데가 없는데 (메저는 있음)??
                        cLib.updateMeasure(dimItemW, measure);
                    }
                    
                }
            }

            cLib.programEnd();

            //  정상 저장 후 리턴
            return { "Code" : 0, "Msg" : "It was saved successfully." };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_execution"  : fn_execution
       ,"fn_save"       : fn_save
       ,"fn_merge"      : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWLCMTimePhasedBOD
    화면명 : LCM Time Phased BOD (EW)
    Action Button : EWLCMTimePhasedBOD
    [history]
    2025.08.27 : syif1380.lee : fn_save 로직 변경
    2025.08.29 : syif1380.lee : fn_bodListW_update() 추가  , 주차별 data update 함수로 만듬
    2025.12.10 : syif1380.lee : fn_execution - PR 이름 변경 ( PR_UI_BODListWLCM_Daily => PR_UI_BODListWLCM_OnDemand )
    2026.01.28 : syif1380.lee : W_Update Time, W_Updated By 메저 삭제 2026.01.28
                                Measure 추가
                                Measure.[BOD Item W Sub_Update Time]
                                Measure.[BOD Item W Sub_Updated By]
                                Measure.[LCM BOD List W Sub_Update Time]
                                Measure.[LCM BOD List W Sub_Updated By]
    2026.03.05 : fn_merge() : Scenario Plan 정의 -> UpdateScenario 로 작성
    2026.03.18 : fn_merge() : mergeType 추가 정의
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/