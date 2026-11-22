define('o9.NSCM.JSEWBODListSET', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWBODListSET
    // 화면명 : SET BOD List (EW)
    // Action Button : EWBODListSET
    // 최초생성 : 2025.07.11 / syif1380.lee
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSEWBODListSET";
    const commonLib = require('o9.NSCM.commonLibVD');   // 2026.03.26 공통적용변경
    const cUtil = fn_cUtil();                           // 2026.03.26 공통적용변경

    const queryModule = require('o9/data/query');
    const MDMHorizon = "&MDMHorizon";

    //================================= 공통 콤보 사용 ===============================//
    // Action Button : EWCommonVD
    // From Site : Location     : fn_cb_siteMFDC (2025.12.09)
    // To Site   : Sub Location  : fn_cb_siteDC
    // TPMode    : Trans Mode   : fn_cb_tpmodeGO
    //================================================================================//

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
    // var fn_formatValue = function(val){
    //     return (val === null || val === undefined || val === "null" ) ? 'null' : `"${val}"`;
    // }

    /**
     * 주어진 값이 null or  "null" 문자열이면 null 반환하고,
     * 그 외의 값은 큰따옴표("") 로 감싼 문자열로 반환한다.
     * @param {any} val - 검사할 값 
     * @returns {String} 출력용 문자열 
     */
    var fn_formatStrValue = function(val){
        return (val === null || val === "null" ) ? 'null' : `"${val}"`;
    }

    /**
     * 주어진 값이 null or  "null" 문자열이면 null 반환하고,
     * 그 외의 값은  그대로 반환한다.
     * @param {any} val - 검사할 값 
     * @returns {String} 출력용 문자열 
     */
    var fn_formatNoStrValue = function(val){
        return (val === null || val === "null" ) ? 'null' : `${val}`;
    }

    var fn_BooleanValue = function(val){
        return (val === null || val === undefined || val === "false" || val === 0 || val === "0" ) ? false : true;
    }

    // BOD List : Save
    var fn_saveBodList = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_save call ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                //===============================================================================================//
                // 그리드 공통 선언 부분 - Start
                //===============================================================================================//
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                let fbLocation = row["[Location].[Location]"];
                let fbSubLocation = row["[Sub Location].[Sub Location]"];
                let fbTPMode = row["[Trans Mode].[Trans Mode]"];

                // Measure
                let bodValid = row["Measure.[BOD List_BOD Valid]"];
                let bodName = row["Measure.[BOD List_BOD Name]"];
                let bodLt = row["Measure.[BOD List_BOD LT]"];
                let priority = row["Measure.[BOD List_Priority]"];
                let shipLt = row["Measure.[BOD List_Shipment LT]"];
                let startDate = row["Measure.[BOD List_Eff Startdate]"];
                let endDate = row["Measure.[BOD List_Eff Enddate]"];
                let startWeek = row["Measure.[BOD List_Eff Startweek]"];    // add 2025.08.05
                let endWeek = row["Measure.[BOD List_Eff Endweek]"];        // add 2025.08.05

                // row 의 값에 따라 ...... bod alt 생성 로직 추가(현 설계서상)
                let productTv = row["Measure.[BOD List_Product TV]"];
                let productAv = row["Measure.[BOD List_Product AV]"];
                let productMonitor = row["Measure.[BOD List_Product MNT]"];

                if ( bodName === null || bodName === undefined || bodName === ""){
                    bodName = fbLocation + "_" + fbSubLocation + "_" + fbTPMode;    // P532_L5N0_EXPRESS    // UI 에서 BOD Name 을 넘기지 않을 경우 내부적으로 세팅 2025.10.15
                }

                // BOD List 의 dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));

                // BOD List Update 메저 정의 (update 기준)
                // BOD List : Update
                let measureList = [];
                measureList.push(cUtil.fn_qMeaInt(row, "Measure.[BOD List_BOD LT]"));
                measureList.push(cUtil.fn_qMeaInt(row, "Measure.[BOD List_Priority]"));
                measureList.push(cUtil.fn_qMeaInt(row, "Measure.[BOD List_Shipment LT]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_Eff Startdate]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_Eff Enddate]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_Eff Startweek]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_Eff Endweek]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_BOD Valid]"));
                measureList.push(cUtil.fn_qMeaNotStr(row, "Measure.[BOD List_Product TV]"));
                measureList.push(cUtil.fn_qMeaNotStr(row, "Measure.[BOD List_Product AV]"));
                measureList.push(cUtil.fn_qMeaNotStr(row, "Measure.[BOD List_Product MNT]"));
                measureList.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD List_Updated By]"));
                measureList.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List_Update Time]"));

                // BOD List > BOD Prod SET > BOD Item 상속 메저 정의 (update 기준)
                // BOD Alt : Update 메저 정의
                // Priority 상속시 Lock Flag 고려하지 않음. 2025.08.06
                let measureAlt = [];
                measureAlt.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Prod SET_Updated By]"));
                measureAlt.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Prod SET_Update Time]"));
                
                let measureBodItem = [];
                measureBodItem.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item_Updated By]"));
                measureBodItem.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item_Update Time]"));
                measureBodItem.push("Measure.[BOD Item_PyRunFlag] = 1; ");  // Time Phased 의 PY 성능으로 추가 (테스트 2025.11.28 syif1380.lee) PY_UI_BODItemW 시 참고

                if( bodLt !== null && bodLt !== undefined ){
                    measureAlt.push(cUtil.fn_qMeaInt(null, "Measure.[BOD Prod SET_BOD LT]", bodLt));
                    measureBodItem.push('Measure.[BOD Item_BOD LT]         = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatNoStrValue(bodLt) + ' else Measure.[BOD Item_BOD LT]; ');
                }
                if( priority !== null && priority !== undefined ){
                    measureAlt.push(cUtil.fn_qMeaInt(null, "Measure.[BOD Prod SET_Priority]", priority));
                }
                if( shipLt !== null && shipLt !== undefined ){
                    measureAlt.push(cUtil.fn_qMeaInt(null, "Measure.[BOD Prod SET_Shipment LT]", shipLt));
                    measureBodItem.push('Measure.[BOD Item_Shipment LT]    = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatNoStrValue(shipLt) + ' else Measure.[BOD Item_Shipment LT]; ');
                }
                if( startDate !== null && startDate !== undefined ){
                    measureAlt.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET_Eff Startdate]", startDate));
                    measureBodItem.push('Measure.[BOD Item_Eff Startdate]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(startDate) + ' else toString(Measure.[BOD Item_Eff Startdate]); ');
                }
                if( endDate !== null && endDate !== undefined ){
                    measureAlt.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET_Eff Enddate]", endDate));
                    measureBodItem.push('Measure.[BOD Item_Eff Enddate]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(endDate) + ' else toString(Measure.[BOD Item_Eff Enddate]); ');
                }
                if( startWeek !== null && startWeek !== undefined ){
                    measureAlt.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET_Eff Startweek]", startWeek));
                    measureBodItem.push('Measure.[BOD Item_Eff Startweek]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(startWeek) + ' else Measure.[BOD Item_Eff Startweek]; ');
                }
                if( endWeek !== null && endWeek !== undefined ){
                    measureAlt.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET_Eff Endweek]", endWeek));
                    measureBodItem.push('Measure.[BOD Item_Eff Endweek]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(endWeek) + ' else Measure.[BOD Item_Eff Endweek]; ');
                }
                //===============================================================================================//
                // 그리드 공통 선언 부분 - End
                //===============================================================================================//

                if ( rowstatus == "C" ) {

                    // 중복 체크 후 생성 (BOD List)
                    if ( !cLib.existMeasure(dimension,["Measure.[BOD List_BOD Valid]","Measure.[BOD List_BOD Name]"], ""))
                    {
                        //========================================================================================================//
                        // BOD List 생성
                        // 선언한 Measure 모두 Grain (cartesian scope) 시 속도가 느림, Grain 은 한번 생성 후 scope 으로 update
                        //========================================================================================================//
                        let measureCreate = [];
                        measureCreate.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_BOD Valid]"));
                        cLib.createMeasure(dimension, measureCreate);

                        // Add시 메저 추가
                        measureList.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_BOD Name]", bodName));
                        measureList.push(cUtil.fn_qMeaStr(row, "Measure.[BOD List_LT Uom]"));
                        measureList.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD List_Created By]"));
                        measureList.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List_Creation Time]"));

                        cLib.updateMeasure(dimension, measureList);
                        
                    }else{
                        return { "Code" : 1, "Msg" : "This is registerd data.", "Rows" : "" };  // 중복 메세지 Return
                    }

                    //========================================================================================================//
                    // BOD Product SET 생성
                    // - Measure.[BOD List_BOD Valid] == Y 인 경우만 생성 => Y/N 모두 생성으로 변경 :이상엽P요청 (2025.11.05)
                    //========================================================================================================//
                    // if( bodValid != null && bodValid == "Y" && (productTv || productAv || productMonitor)){
                    if( productTv || productAv || productMonitor){
                        fn_bodProdSetUpdate(row, dimension, measureAlt, bodName);
                    }
                
                } else if ( rowstatus == "U" ) {

                    //========================================================================================================//
                    // BOD List : Update
                    //========================================================================================================//
                    cLib.updateMeasure(dimension, measureList);

                    //-----------------------------------------------------------------------------//
                    // BOD Prod SET : Create, update : Check
                    //                Valid = 'N'    : unCheck
                    // - Measure.[BOD List_BOD Valid] == Y 인 경우만 생성 => Y/N 모두 생성으로 변경 :이상엽P요청 (2025.11.05)
                    //-----------------------------------------------------------------------------//
                    if( bodValid == "Y" || bodValid == "N" ){
    
                        let productGroupArry = [];      // Product Group : Check
                        let productGroupArryDel = [];   // Product Group : UnCheck
    
                        if( fn_BooleanValue(productTv) ){
                            productGroupArry.push("TV");
                        }else{
                            productGroupArryDel.push("TV");
                        }
    
                        if( fn_BooleanValue(productAv) ){
                            productGroupArry.push("AV");
                        }else{
                            productGroupArryDel.push("AV");
                        }
    
                        if( fn_BooleanValue(productMonitor) ){
                            productGroupArry.push("MONITOR");
                        }else{
                            productGroupArryDel.push("MONITOR");
                        }
    
                        if( productGroupArry.length > 0 ){

                            //========================================================================================================//
                            // BOD Prod SET : Update
                            //========================================================================================================//
                            // if( bodValid != null && bodValid == "Y" && (productTv || productAv || productMonitor)){
                            if( productTv || productAv || productMonitor ){
                            
                                fn_bodProdSetUpdate(row, dimension, measureAlt, bodName);
                            }

                            //========================================================================================================//
                            // BOD Item : Update
                            //========================================================================================================//
                            fn_bodItemUpdate(dimension, measureBodItem, productGroupArry);
                        }
                        
                        // Product Group : BOD List 에서 unCheck 인 경우 valid = "N" 처리
                        if( productGroupArryDel.length > 0 ){
                            let dimProdSetDel = [...dimension];
                            dimProdSetDel.push("[Item].[Product Group]"+cUtil.fn_filterStr(productGroupArryDel));
                            cLib.updateMeasure(dimProdSetDel, ['Measure.[BOD Prod SET_BOD Valid] = "N";']);
                        }
                        
                    }
                }
            }

            cLib.programEnd();

            //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
            return { "Code" : 0, "Msg" : "", "Rows" : parsedParams.fbGridRows };  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // BOD Item : Update
    var fn_bodItemUpdate = function(dimension, measureBodItem, productGroupArry){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let dimItem = [...dimension];
            dimItem.push("&SETItem");

            // BOD Item : Product Group 에 해당하는 Item 가져오기
            let where = 'where { Measure.[BOD Item_Asn] == 1 , [Item].[Product Group]'+cUtil.fn_filterStr(productGroupArry)+'}';
            let rtnBodItemList = cLib.selectList(dimItem
                                            , ["Measure.[BOD Item_BOD LT]", "Measure.[BOD Item_Priority]", "Measure.[BOD Item_Shipment LT]", "Measure.[BOD Item_Lock Flag]"
                                            ,"Measure.[BOD Item_Eff Startdate]", "Measure.[BOD Item_Eff Enddate]"]
                                            , where, "", "");
            
            // 대상 Item 을 조회한다.
            let getItemList = [];
            for ( k=0; k<rtnBodItemList.cs.rowCount; k++){

                let getItem = rtnBodItemList.cs.row(k).cell(rtnBodItemList.cs.memberColumnIndex("Item", "Item")).Name;
                getItemList.push(getItem);
            }
            
            // 대상 Item 을 저장한다.
            if( getItemList.length > 0){

                let dimBodItemKey = [...dimension];
                dimBodItemKey.push("[Item].[Item]"+cUtil.fn_filterStr(getItemList));

                // 조회된 Item 을 update 
                cLib.updateMeasure(dimBodItemKey, measureBodItem);

                //-----------------------------2025.11.28 추가-----------------------------------------------------
                // Time Phased 의 PY 성능으로 추가 (테스트 2025.11.28 syif1380.lee) PY_UI_BODItemW 시 참고
                // BOD Item W 존재하는 것들만 update
                let dimBodItemKey_W = [...dimBodItemKey];
                // dimBodItemKey_W.push("&MDMHorizon");
                dimBodItemKey_W.push(MDMHorizon);
                let measureBodItemW = [];
                measureBodItemW.push("Measure.[BOD Item W_PyRunFlag] = 1; ");
                // 조회된 Item 을 update 
                cLib.updateMeasure(dimBodItemKey_W, measureBodItemW);
                //----------------------------------------------------------------------------------
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // BOD Prod SET : Create, Update
    var fn_bodProdSetUpdate = function(row, dimension, measureAlt, bodName){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("rowstatus :: "+row["rowstatus"]);
            cLib.debug("bodName :: "+bodName);
            cLib.debug("row :: "+JSON.stringify(row));

            let productTv = row["Measure.[BOD List_Product TV]"];
            let productAv = row["Measure.[BOD List_Product AV]"];
            let productMonitor = row["Measure.[BOD List_Product MNT]"];

            let dimTv = "[Item].[Product Group].[TV]";
            let dimAv = "[Item].[Product Group].[AV]";
            let dimMonitor = "[Item].[Product Group].[MONITOR]";

            let measureCheck = ["Measure.[BOD Prod SET_BOD Valid]", "Measure.[BOD Prod SET_Lock Flag]", "Measure.[BOD Prod SET_Asn]"
                            , "Measure.[BOD Prod SET_BOD LT]", "Measure.[BOD Prod SET_Priority]", "Measure.[BOD Prod SET_Shipment LT]"];

            // 신규 생성시 메저 추가 정의
            let measureAltInsert = [...measureAlt];
            measureAltInsert.push("Measure.[BOD Prod SET_Asn] = 1; ");
            measureAltInsert.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Prod SET_Created By]"));
            measureAltInsert.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Prod SET_Creation Time]"));
            if( bodName !== null && bodName !== undefined ){
                measureAltInsert.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET_BOD Name]", bodName));
            }

            // TV : [Item].[Product Group].[TV]
            // if( productTv != null && (productTv == "true" || productTv == true)){
            if( fn_BooleanValue(productTv) ){
                let dimensionTv = [...dimension];
                dimensionTv.push(dimTv);
                // 중복 체크 후 생성
                if ( !cLib.existMeasure(dimensionTv, measureCheck, ""))
                {
                    cLib.createMeasure(dimensionTv, ['Measure.[BOD Prod SET_BOD Valid] = "N" ;']);

                    // measureAlt.push("Measure.[BOD Prod SET_Asn] = 1; ");
                    // measureAlt.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Prod SET_Created By]"));
                    // measureAlt.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Prod SET_Creation Time]"));
                    // if( bodName !== null && bodName !== undefined ){
                    //     measureAlt.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET_BOD Name]", bodName));
                    // }
                    cLib.updateMeasure(dimensionTv, measureAltInsert);
                }else{
                    
                    cLib.updateMeasure(dimensionTv, measureAlt);
                }
            }

            // AV : [Item].[Product Group].[AV]
            // if( productAv != null && (productAv == "true" || productAv == true)){
            if( fn_BooleanValue(productAv) ){
                let dimensionAv = [...dimension];
                dimensionAv.push(dimAv);
                // 중복 체크 후 생성
                if ( !cLib.existMeasure(dimensionAv, measureCheck, ""))
                {   
                    cLib.createMeasure(dimensionAv, ['Measure.[BOD Prod SET_BOD Valid] = "N" ;']);
                    cLib.updateMeasure(dimensionAv, measureAltInsert);
                }else{
                    cLib.updateMeasure(dimensionAv, measureAlt);
                }
            }

            // MONITOR : [Item].[Product Group].[MONITOR]
            // if( productMonitor != null && (productMonitor == "true" || productMonitor == true)){
            if( fn_BooleanValue(productMonitor) ){
                let dimensionMonitor = [...dimension];
                dimensionMonitor.push(dimMonitor);
                // 중복 체크 후 생성
                if ( !cLib.existMeasure(dimensionMonitor, measureCheck, ""))
                {
                    cLib.createMeasure(dimensionMonitor, ['Measure.[BOD Prod SET_BOD Valid] = "N" ;']);
                    cLib.updateMeasure(dimensionMonitor, measureAltInsert);
                }else{
                    cLib.updateMeasure(dimensionMonitor, measureAlt);
                }
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_saveBodProdSet
     * 두번째 Tab : 로직
     * BOD Prod SET : 저장 :  BOD Alt 그리드에는 Add 기능 없음
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveBodProdSet = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                //===============================================================================================//
                // 그리드 공통 선언 부분 - Start
                //===============================================================================================//
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                let fbLocation      = row["[Location].[Location]"];
                let fbSubLocation   = row["[Sub Location].[Sub Location]"];
                let fbTPMode        = row["[Trans Mode].[Trans Mode]"];
                let fbProductGroup  = row["[Item].[Product Group]"];

                // Measure
                let priority = row["Measure.[BOD Prod SET_Priority]"];
                let bodValid = row["Measure.[BOD Prod SET_BOD Valid]"];

                let timePhasedBod = row["Measure.[BOD Prod SET_Time Phased BOD LT]"];
                let timePhasedPrty = row["Measure.[BOD Prod SET_Time Phased Prty]"];
                let timePhasedShipment = row["Measure.[BOD Prod SET_Time Phased Shipment LT]"];

                // BOD Prod SET 의 dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));

                let dimProd = [...dimension];
                dimProd.push("[Item].[Product Group].[" + fbProductGroup + "]");

                let measureAlt = [];
                measureAlt.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Prod SET_Priority]"));
                measureAlt.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Prod SET_Time Phased BOD LT]"));
                measureAlt.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Prod SET_Time Phased Prty]"));
                measureAlt.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Prod SET_Time Phased Shipment LT]"));
                measureAlt.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Prod SET_BOD Valid]"));
                measureAlt.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Prod SET_Updated By]"));
                measureAlt.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Prod SET_Update Time]"));

                // BOD Prod SET W Sub : Time Phased 추가 2025.11.26 ( Time Phased 화면에서 N 인것은 UI 에서 안보이기 위함, PY 에서는 상속하지 않고 BOD Prod SET 값을 재설정)
                let measureAltSub = [];
                // measureAltSub.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Prod SET W Sub_Time Phased BOD LT]"));
                // measureAltSub.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Prod SET W Sub_Time Phased Prty]"));
                // measureAltSub.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Prod SET W Sub_Time Phased Shipment LT]"));
                
                let measureBodItem = [];
                measureBodItem.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item_Updated By]"));
                measureBodItem.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item_Update Time]"));
                if( priority !== null && priority !== undefined ){
                    measureBodItem.push(cUtil.fn_qMeaInt(null, "Measure.[BOD Item_Priority]", priority));
                }
                if( timePhasedBod !== null && timePhasedBod !== undefined ){
                    measureBodItem.push(cUtil.fn_qMeaInt(null, "Measure.[BOD Item_Time Phased BOD]", timePhasedBod));
                    measureAltSub.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET W Sub_Time Phased BOD LT]", timePhasedBod));
                }
                if( timePhasedPrty !== null && timePhasedPrty !== undefined ){
                    measureBodItem.push(cUtil.fn_qMeaInt(null, "Measure.[BOD Item_Time Phased Prty]", timePhasedPrty));
                    measureAltSub.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET W Sub_Time Phased Prty]", timePhasedPrty));
                }
                if( timePhasedShipment !== null && timePhasedShipment !== undefined ){
                    measureBodItem.push(cUtil.fn_qMeaInt(null, "Measure.[BOD Item_Time Phased Shipment]", timePhasedShipment));
                    measureAltSub.push(cUtil.fn_qMeaStr(null, "Measure.[BOD Prod SET W Sub_Time Phased Shipment LT]", timePhasedShipment));
                }

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "U") {
                    
                    //================================================================================================================================//
                    // BOD Prod SET : Update 
                    //================================================================================================================================//
                    cLib.updateMeasure(dimProd, measureAlt);

                    //================================================================================================================================//
                    // BOD Prod SET W Sub : Update : 추가 2025.11.26 : Time Phased 추가 2025.11.26 ( Time Phased 화면에서 N 인것은 UI 에서 안보이기 위함, PY 에서는 상속하지 않고 BOD Prod SET 값을 재설정)
                    //================================================================================================================================//
                    if( measureAltSub.length > 0){
                        cLib.updateMeasure(dimProd, measureAltSub);
                    }

                    //================================================================================================================================//
                    // BOD Item : Update (BOD Prod SET 의 확장 Update) : Priority 상속 (Lock Flag 고려하지 않음) ==> fn_savePostProcess() : PY_UI_BODItem_NewAlt 호출로 변경
                    //================================================================================================================================//
                    // if( bodValid != null && bodValid == "Y" ){
                    //     fn_bodItemUpdate(dimension, measureBodItem, fbProductGroup);
                    // }

                }

            } // end for

            //================================================================================================================================//
            // BOD Item : 생성 or 상속 PY 호출로 변경 - 이상엽p 요청 (2025.10.27)
            //================================================================================================================================//
            if( parsedParams.fbGridRows.length > 0){
                fn_savePostProcess(parsedParams);
            }

            cLib.programEnd();
            
            //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
            return { "Code" : 0, "Msg" : "", "Rows" : parsedParams.fbGridRows };  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_savePostProcess
     * BOD Item : 생성 or 상속 : PY_UI_BODItem_NewAlt 호출 함수 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_savePostProcess = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));


            // Sub Location의 값도 Location에 포함되어 필터 조건으로 호출 될수 있도록 아래와 같이 파라미터가 넘어가 호출 되도록 요청 (2025.10.29 이상엽프로 요청)
            // ex) P306,S311,S312
            let fbLocation = [...new Set([
                ...parsedParams.fbGridRows.map(row => row["[Location].[Location]"]),
                ...parsedParams.fbGridRows.map(row => row["[Sub Location].[Sub Location]"])
            ])];

            let fbTPMode = [...new Set(parsedParams.fbGridRows.map(row => row["[Trans Mode].[Trans Mode]"]))];
            let fbProductGroup = [...new Set(parsedParams.fbGridRows.map(row => row["[Item].[Product Group]"]))];

            cLib.debug(" PY 호출 ======================>PY_UI_BODItem_NewAlt : fbLocation : "+ fbLocation);
            // cLib.debug(" PY 호출 ======================>PY_UI_BODItem_NewAlt : fbSubLocation : "+ fbSubLocation);
            // cLib.debug(" PY 호출 ======================>PY_UI_BODItem_NewAlt : fbTPMode : "+ fbTPMode);
            // cLib.debug(" PY 호출 ======================>PY_UI_BODItem_NewAlt : fbProductGroup : "+ fbProductGroup);

            /* PY 호출 (PY_UI_BODItem_NewAlt) 권태우B */
            var execQuery = 'EXEC plugin instance [PY_UI_BODItem_NewAlt] for measures {[BOD Item_BOD LT]}'
                            +' using scope ( '
                            +' &MPV'
                            +' * [Location].[Location]'+cUtil.fn_filterStr(fbLocation)
                            +' * [Trans Mode].[Trans Mode]'+cUtil.fn_filterStr(fbTPMode)
                            +' * [Item].[Product Group]'+cUtil.fn_filterStr(fbProductGroup)
                            +' ) '
                            +'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_savePostProcess : PY_UI_BODItem_NewAlt Run", execQuery);

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_saveBodItem
     * 세번째 Tab : 로직 2025.12.09 생성
     * BOD Item : 저장 :
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveBodItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_saveBodItem call ==========================================================>");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                //===============================================================================================//
                // 그리드 공통 선언 부분 - Start
                //===============================================================================================//
                var row = parsedParams.fbGridRows[i];
                var rowstatus = row["rowstatus"];

                // BOD Item 의 dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));

                let measureBodItem = [];
                measureBodItem.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item_Updated By]"));
                measureBodItem.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item_Update Time]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Priority]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_BOD LT]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Shipment LT]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Min Lot Qty]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Multi Lot Qty]"));

                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Startdate]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Enddate]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Startweek]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Endweek]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Lock Flag]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_BOD Valid]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Period1]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Period2]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Period3]"));

                measureBodItem.push("Measure.[BOD Item_PyRunFlag] = 1; ");  // Time Phased 의 PY 성능으로 추가 (테스트 2025.11.28 syif1380.lee) PY_UI_BODItemW 시 참고

                //===============================================================================================//
                // 그리드 공통 선언 부분 - End
                //===============================================================================================//

                if ( rowstatus == "C" ) {
                    // 생성 로직 없음
                } else if ( rowstatus == "U" ) {

                    //========================================================================================================//
                    // BOD Item : Update
                    //========================================================================================================//
                    cLib.updateMeasure(dimension, measureBodItem);

                    //========================================================================================================//
                    // BOD Item W : Update
                    //========================================================================================================//
                    let measureBodItemW = [];
                    measureBodItemW.push("Measure.[BOD Item W_PyRunFlag] = 1; ");  // Time Phased 의 PY 성능으로 추가 (테스트 2025.12.09 syif1380.lee) PY_UI_BODItemW 시 참고
                    let dimItemW = [...dimension];
                    dimItemW.push(MDMHorizon);
                    cLib.updateMeasure(dimItemW, measureBodItemW);
                }
            }

            cLib.programEnd();

            //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
            return { "Code" : 0, "Msg" : "", "Rows" : parsedParams.fbGridRows };  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_merge : Scenario Plan >> 테스트 필요.... 2026.02.26
     * 2026.02.25 생성
     * @param {*} o9Params 
     * @returns 
     */
    // { "fbFuncName" : "fn_merge"
    // ,"fbParams" : { "commitType" : "1", "grid" : "Lv3"
    // ,"filters" : { "[Version].[Version Name]" : {"SelectedMembers" : ["202605_P_WI_01"], "MemberFilter" : ""} }
    // }
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
                    + ',for model [BOD List] '
                    + ',for model [BOD Product SET] '
                    + ',for model [BOD Item] '
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

            }else if( parsedParams.fbParams["mergeType"] == "0"){

                for ( var i=0; i<parsedParams.fbGridRows.master.length; i++){

                    var row = parsedParams.fbGridRows.master[i];

                    // BOD List 의 dimension 정의
                    let dimBodList = [];
                    dimBodList.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimBodList.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimBodList.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));

                    let dimAlt = [...dimBodList];
                    dimAlt.push("[Item].[Product Group]");

                    let dimBodItem = [...dimBodList];
                    dimBodItem.push("[Item].[Item]");

                    //// toVersion, FromVersion, false
                    // UpdateScenario([Version].[Version Name].[CWV_MP], [Version].[Version Name].[202605_M_WI_01], false,
                    //     for model [BOD List] using scope ( [Location].[Location].[P105] * [Sub Location].[Sub Location].[S356] * [Trans Mode].[Trans Mode].[VESSEL] )
                    //     );
                    
                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    // >>> py 에서 실행하는지 확인 필요
                    // BOD Prod SET W Sub  > copy ? >>> py 에서 실행하는지 확인 필요
                    // BOD Item W > copy ? >>> py 에서 실행하는지 확인 필요
                    // BOD Item W Sub > copy ? >>> py 에서 실행하는지 확인 필요
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [BOD List] using scope (' + dimBodList.join('*') + ')'
                    + ',for model [BOD Product SET] using scope (' + dimAlt.join('*') + ')'
                    + ',for model [BOD Item] using scope (' + dimBodItem.join('*') + ')'
                    // + ',for model [BOD Prod SET W Sub] using scope (' + dimAlt.join('*') + ')'  // py 에서 실행하는지 확인 필요
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

                    //-------------------------------------------------------------------------------------
                    // BOD List : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimBodListChk = [...dimBodList];
                    dimBodListChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimBodListChk, ["Measure.[BOD List_BOD Valid]"], "") ){

                        dimBodList.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[BOD List_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List_Update Time]"));
                        cLib.updateMeasure(dimBodList, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // BOD Prod Set : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimAltChk = [...dimAlt];
                    dimAltChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimAltChk, ["Measure.[BOD Prod SET_Asn]","Measure.[BOD Prod SET_BOD Valid]"], "") ){

                        dimAlt.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[BOD Prod SET_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Prod SET_Update Time]"));
                        cLib.updateMeasure(dimAlt, measure);
                    }

                    //-------------------------------------------------------------------------------------
                    // BOD Item : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimItemChk = [...dimBodItem];
                    dimItemChk.push("[Version].[Version Name].["+fbVersion+"]");    // 시나리오 버전
                    if( cLib.existMeasure(dimItemChk, ["Measure.[BOD Item_Asn]","Measure.[BOD Item_BOD Valid]"], "") ){
                        
                        dimBodItem.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[BOD Item_Updated By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item_Update Time]"));
                        measure.push("Measure.[BOD Item_PyRunFlag] = 1; ");
                        cLib.updateMeasure(dimBodItem, measure);
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
        "fn_saveBodList"    : fn_saveBodList
       ,"fn_saveBodProdSet" : fn_saveBodProdSet
       ,"fn_saveBodItem"    : fn_saveBodItem
       ,"fn_merge"          : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWBODListSET
    화면명 : SET BOD List (EW)
    Action Button : EWBODListSET
    [history]
    2025.08.05 : Eff StartWeek/Eff EndWeek 추가
    2025.08.05 : BOD list : Priority > BOD Alt : Priority 상속 , BOD List : BOD LT, Shipment LT, Eff Start/end date (week) > BOD Item 상속
    2025.08.08 : Add시 Measure.[BOD List_LT Uom] 저장
    2025.10.16 : 공통소스 반영
    2025.10.27 : BOD Alt 탭에서 저장시 BOD Item 은 PY_UI_BODItem_NewAlt 호출로 상속,생성 함 (이상엽P요청, 2025.10.27)
    2025.10.29 : PY_UI_BODItem_NewAlt 호출시 UI 그리드에서 선택된 Row 의 Location, Sub Location 을 Location의 scope 에 넣는다. (이상엽프로 요청)
    2025.11.05 :- BOD Alt 생성시, Measure.[BOD List_BOD Valid] == Y 인 경우만 생성,수정 
                    => Measure.[BOD List_BOD Valid] == Y/N 모두 생성,수정 변경 :이상엽P요청 (2025.11.05)
                - fn_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경
    2025.11.26 : fn_saveBodProdSet() 수정 : BOD Alt 저장시 BOD Prod SET W Sub > 저장
                Measure.[BOD Prod SET W Sub_Time Phased Prty]
                Measure.[BOD Prod SET W Sub_Time Phased BOD LT]
                Measure.[BOD Prod SET W Sub_Time Phased Shipment LT]
    2025.12.09 : BOD List 상속, BOD Item 수정시 Measure.[BOD Item_PyRunFlag], Measure.[BOD Item W_PyRunFlag] = 1 로 세팅 (SET BOD Time Phased 화면에서 Reload시 성능향상을 위해 사용)
    2025.12.09 : fn_saveBodItem() - 추가 : BOD Item 저장 함수 (EW 저장 -> API 저장)
    2026.03.03 : fn_merge() : Scenario Plan 정의, combo > &cwvui 없음
    2026.03.04 : fn_merge() : Scenario Plan 정의 -> UpdateScenario 로 변경
    2026.03.18 : fn_merge() : mergeType 추가 정의
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
*/
/*--------------------------------------------------------------------------------------------------*/