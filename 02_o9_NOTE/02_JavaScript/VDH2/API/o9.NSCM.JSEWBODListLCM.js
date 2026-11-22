define('o9.NSCM.JSEWBODListLCM', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWBODListLCM
    // 화면명 : LCM BOD List
    // Action Button : EWBODListLCM
    // 최초생성 : 2025.07.28 / syif1380.lee
    /*--------------------------------------------------------------------------------------------------*/

    // fn_cLib 를 통해서 commonLib 를 생성 // 2026.03.26 공통적용변경
    const commonLib = require('o9.NSCM.commonLibVD');   // 2026.03.26 공통적용변경
    var fn_cLib = function(name) {
        return new commonLib.VdCommon(name);
    }
    var fn_cUtil = function() {
        return new commonLib.VdUtil();
    }

    const programName = "o9.NSCM.JSEWBODListLCM";
    
    const cUtil = fn_cUtil();                           // 2026.03.26 공통적용변경
    const queryModule = require('o9/data/query');
    const MDMHorizon = "&MDMHorizon";

    //================================= 공통 콤보 사용 ===============================//
    // Action Button : EWCommonVD
    // From Site : Location : fn_cb_siteMfLcm (임성민b)
    // TPMode    : Trans Mode   : fn_cb_tpmodeGO
    //================================================================================//
    // Action Button : EWBODListLCM
    // To Site   : Sub Location  : fn_cb_subLocation
    // Item Class Category : fn_cb_category
    //================================================================================//
    // BOD Item List 의 combo
    // Product Group : EWCommonVD : { "fbFuncName" : "fn_cb_lcmProductGroup" }
    // Product : EWBODListLCM : { "fbFuncName" : "fn_cb_product", "fbParams" : {"[Item].[Product Group]":"LCD"} }

    /*
    From Site > EWCommonVD : { "fbFuncName" : "fn_cb_siteMfLcm", "fbParams" : {} }
    To Site   > EWBODListLCM : { "fbFuncName" : "fn_cb_subLocation", "fbParams" : {"[Location].[Location]":"P306LCD"} }
    Material Group > EWBODListLCM : { "fbFuncName" : "fn_cb_category", "fbParams" : {"[Location].[Location]":"P306LCD"} }
    */

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
     * LCM BOD List / LCM BOD Item : To Site 콤보
     * Actiion Button : EWBODListLCM
     * { "fbFuncName" : "fn_cb_subLocation" , "fbParams" : { "[Location].[Location]" : "P306LCD" } }
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_subLocation = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            // let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            // selectList(dimension, measure, where, orderby, limit)
            // var where = "where {"
            //                    +"&CWVUI"
            //                    +",[Location].[Location].["+fbLocation+"]"
            //                    +"}";

            let conditions = [];
            // conditions.push("[Location].[Location]"+ cUtil.fn_filterStr(fbLocation));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group3]"));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Sub Location].[Sub Location Group4]"));
            // cLib.debug(" fn_cb_subLocation >> conditions : "+JSON.stringify(conditions));

            let where = conditions.length ? `where { ${conditions.join(',')} } ` : '' ;
            // cLib.debug(" fn_cb_subLocation >> where > " + where);

            var result = cLib.selectList(["&MFStageSETSubLocation.unionwith(&MFStageKDSubLocation)"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * LCM BOD List : Material Group 콤보
     * Actiion Button : EWBODListLCM
     * { "fbFuncName" : "fn_cb_category" "fbParams" : {"[Location].[Location]":"P306LCD"} }
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_category = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let fbLocation = parsedParams.fbParams["[Location].[Location]"];

            cLib.debug("fn_getFilterQuery : version >> "+cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));
            // &NSUIMasterVersionViewWtihScenario.filter(#.Name in {"CWV_MP"})

            var where = "where {"
                               + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                               +",[Location].[Location].["+fbLocation+"]"
                               +",Measure.[LCM BOD Mat Grp_Asn] > 0"
                               +"}";

            var result = cLib.selectList(["[Item].[Class Category]"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Class Category", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * LCM BOD Item : Product 콤보
     * Actiion Button : EWBODListLCM
     * { "fbFuncName" : "fn_cb_product", "fbParams" : {"[Item].[Product Group]":"LCD"} }
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_product = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let fbProductGroup = parsedParams.fbParams["[Item].[Product Group]"];
            var where = 'where {'
                            //    +'[Item].[Item Stage].filter(#.Name == "LCM")'
                               +'[Item].[Item Stage].filter(#.Name in {"LCM", "LED_MODULE"})'  // LCM 마스터 성 화면에서 LED도 함께 관리하기로 요건 추가 (2026.03.26 이상엽p)
                               +',[Item].[Product Group]' + cUtil.fn_filterStr(fbProductGroup)
                               +'}';
            var result = cLib.selectList(['[Item].[Product].filter(#.Name != "-").relatedmembers([Product])'],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * LCM BOD Item : To Item 의 Material Group(Class Category) 콤보
     * Actiion Button : EWBODListLCM
     * { "fbFuncName" : "fn_cb_itemClassCategory" "fbParams" : {"[Item].[Item]":"BN95-07748B"} }
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_itemClassCategory = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            let fbItem = parsedParams.fbParams["[Item].[Item]"];

            var result = cLib.selectList(["[Item].[Item]"+cUtil.fn_filterStr(fbItem), "[Item].[Class Category]"],
                                             [],
                                             "",
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Class Category", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : true});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * LCM BOD Item : To Item 콤보
     * Actiion Button : EWBODListLCM
     * {"fbFuncName" : "fn_cb_item", 
        "fbParams" : {"[Location].[Location]":"P306LCD","[Sub Location].[Sub Location]":"P306", "[Item].[Item]":"BN95-07824A"
        ,"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}
        }}
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_item = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            cLib.debug("########### test : "+cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));

            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];

            var where = 'where {'
                               + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                               +',[Location].[Location]' + cUtil.fn_filterStr(fbLocation)
                               +',[Sub Location].[Sub Location]' + cUtil.fn_filterStr(fbSubLocation)
                            //    +',Measure.[Code Map LCM_Valid Flag] == "Y"'
                               +',(Measure.[Code Map LCM_Valid Flag] == "Y" && Measure.[Code Map LCM_Map Status] == "CON" )'  // add 2026.03.26 이상엽p요청
                               +"}";

            var result = cLib.selectList(["[Item].[Item]"],
                                             [],
                                             where,
                                             "",
                                             "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * LCM BOD Item : Prod Item 콤보
     * Actiion Button : EWBODListLCM
     * { "fbFuncName" : "fn_cb_fromItem", "fbParams" : {"[Location].[Location]":"P306LCD","[Sub Location].[Sub Location]":"P306", "[Item].[Item]":"BN95-04320A"} }
     * {"fbFuncName" : "fn_cb_fromItem", 
                        "fbParams" : {"[Location].[Location]":"P306LCD","[Sub Location].[Sub Location]":"P306", "[Item].[Item]":"BN95-07824A"
                        ,"filters":{"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"MemberFilter":"&CWVUI"}}
                        }}
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_fromItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            let fbLocation = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            let fbItem = parsedParams.fbParams["[Item].[Item]"];

            var where = 'where {'
                               + cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]")
                               +',[Location].[Location]' + cUtil.fn_filterStr(fbLocation)
                               +',[Sub Location].[Sub Location]' + cUtil.fn_filterStr(fbSubLocation)
                               +',[Item].[Item]' + cUtil.fn_filterStr(fbItem)
                            //    +',Measure.[Code Map LCM_Valid Flag] == "Y"'
                               +',(Measure.[Code Map LCM_Valid Flag] == "Y" && Measure.[Code Map LCM_Map Status] == "CON" )'  // 2026.03.20 이상엽p요청
                               +"}";

            // Code Map LCM_Prod Item => To Item 으로 변경 (2026.03.10 이상엽P요청)
            var resultItem = cLib.selectList(["[To Item].[To Item]"],
                                             [],
                                             where,
                                             "",
                                             "");

            cLib.printCsData(resultItem, 3);

            // Name 으로 오름차순 정렬
            var comboList = cLib.fn_makeCombo(resultItem, {DimName : "To Item", DimAttbName : "To Item", Sort : "Name", existAll : false, isDisplayNameWithCode : false});

            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

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

    /**
     * fn_save : LCM BOD List 저장
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("Create >>  LCM BOD List : fn_save ==========================================================>");
        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let measureCheck = ["Measure.[LCM BOD List_BOD Valid]"
                                , "Measure.[LCM BOD List_BOD Priority]", "Measure.[LCM BOD List_Shipment LT]", "Measure.[LCM BOD List_Transit Time]"];

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){
                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                let fbLocation      = row["[Location].[Location]"];
                let fbSubLocation   = row["[Sub Location].[Sub Location]"];
                let fbTPMode        = row["[Trans Mode].[Trans Mode]"];
                let fbCategory      = row["[Item].[Class Category]"];

                // Measure
                let bodLt           = row["Measure.[LCM BOD List_Transit Time]"];
                let priority        = row["Measure.[LCM BOD List_BOD Priority]"];
                let shipLt          = row["Measure.[LCM BOD List_Shipment LT]"];
                let startDate       = row["Measure.[LCM BOD List_Eff Startdate]"];
                let endDate         = row["Measure.[LCM BOD List_Eff Enddate]"];
                let startWeek       = row["Measure.[LCM BOD List_Eff Startweek]"];
                let endWeek         = row["Measure.[LCM BOD List_Eff Endweek]"];
                let bodValid        = row["Measure.[LCM BOD List_BOD Valid]"];
                let bodName         = row["Measure.[LCM BOD List_BOD Name]"];

                let timePhasedBod   = row["Measure.[LCM BOD List_Time Phased Transit Time]"];
                let timePhasedPrty  = row["Measure.[LCM BOD List_Time Phased Priority]"];
                let timePhasedShipment = row["Measure.[LCM BOD List_Time Phased Shipment LT]"];

                if ( bodName === null || bodName === undefined || bodName === ""){
                    bodName = fbLocation + "_" + fbSubLocation + "_" + fbTPMode;    // P532_L5N0_EXPRESS    // UI 에서 BOD Name 을 넘기지 않을 경우 내부적으로 세팅 2025.10.15
                }

                // LCM BOD List 의 dimension 정의
                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));

                let dimensionList = [...dimension];
                dimensionList.push("[Item].[Class Category].[" + fbCategory + "]");

                // LCM BOD List Update 메저 정의 (update 기준)
                let measureList = [];
                measureList.push(cUtil.fn_qMeaInt(row, "Measure.[LCM BOD List_Transit Time]"));
                measureList.push(cUtil.fn_qMeaInt(row, "Measure.[LCM BOD List_BOD Priority]"));
                measureList.push(cUtil.fn_qMeaInt(row, "Measure.[LCM BOD List_Shipment LT]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List_Eff Startweek]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List_Eff Endweek]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List_Eff Startdate]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List_Eff Enddate]"));
                measureList.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List_BOD Valid]"));
                measureList.push(cUtil.fn_qMeaNotStr(row, "Measure.[LCM BOD List_Time Phased Transit Time]"));
                measureList.push(cUtil.fn_qMeaNotStr(row, "Measure.[LCM BOD List_Time Phased Priority]"));
                measureList.push(cUtil.fn_qMeaNotStr(row, "Measure.[LCM BOD List_Time Phased Shipment LT]"));
                measureList.push(cUtil.fn_qMeaUpdateUserName("Measure.[LCM BOD List_Up By]"));
                measureList.push(cUtil.fn_qMeaUpdateTime("Measure.[LCM BOD List_Up Dttm]"));

                // LCM BOD List W Sub : Time Phased 추가 2025.11.26 ( Time Phased 화면에서 N 인것은 UI 에서 안보이기 위함, PY 에서는 상속하지 않고 BOD Prod SET 값을 재설정)
                let measureListSub = [];
                // measureListSub.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List W Sub_Time Phased BOD LT]"));
                // measureListSub.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List W Sub_Time Phased Prty]"));
                // measureListSub.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List W Sub_Time Phased Shipment LT]"));

                // BOD Item : Measure 정의 (update 기준)
                let measureBodItem = [];
                measureBodItem.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item_Updated By]"));
                measureBodItem.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item_Update Time]"));
                measureBodItem.push("Measure.[BOD Item_PyRunFlag] = 1; ");  // Time Phased 의 PY 성능으로 추가 (테스트 2025.12.09 syif1380.lee) PY_UI_BODItemW 시 참고

                if( bodLt !== null && bodLt !== undefined ){
                    measureBodItem.push('Measure.[BOD Item_BOD LT]         = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatNoStrValue(bodLt) + ' else Measure.[BOD Item_BOD LT]; ');
                }
                if( priority !== null && priority !== undefined ){
                    measureBodItem.push('Measure.[BOD Item_Priority]       = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatNoStrValue(priority) + ' else Measure.[BOD Item_Priority]; ');
                }
                if( shipLt !== null && shipLt !== undefined ){
                    measureBodItem.push('Measure.[BOD Item_Shipment LT]    = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatNoStrValue(shipLt) + ' else Measure.[BOD Item_Shipment LT]; ');
                }
                if( startDate !== null && startDate !== undefined ){
                    measureBodItem.push('Measure.[BOD Item_Eff Startdate]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(startDate) + ' else toString(Measure.[BOD Item_Eff Startdate]); ');
                }
                if( endDate !== null && endDate !== undefined ){
                    measureBodItem.push('Measure.[BOD Item_Eff Enddate]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(endDate) + ' else toString(Measure.[BOD Item_Eff Enddate]); ');
                }
                if( startWeek !== null && startWeek !== undefined ){
                    measureBodItem.push('Measure.[BOD Item_Eff Startweek]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(startWeek) + ' else Measure.[BOD Item_Eff Startweek]; ');
                }
                if( endWeek !== null && endWeek !== undefined ){
                    measureBodItem.push('Measure.[BOD Item_Eff Endweek]  = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatStrValue(endWeek) + ' else Measure.[BOD Item_Eff Endweek]; ');
                }
                // Time Phased 는 Measure.[BOD Item_Lock Flag] 의 영향을 받지 않음
                if( timePhasedBod !== null && timePhasedBod !== undefined ){
                    measureBodItem.push(cUtil.fn_qMeaNotStr(null, "Measure.[BOD Item_Time Phased BOD]", timePhasedBod));
                    measureListSub.push(cUtil.fn_qMeaStr(null, "Measure.[LCM BOD List W Sub_Time Phased BOD LT]", timePhasedBod));
                }
                if( timePhasedPrty !== null && timePhasedPrty !== undefined ){
                    measureBodItem.push(cUtil.fn_qMeaNotStr(null, "Measure.[BOD Item_Time Phased Prty]", timePhasedPrty));
                    measureListSub.push(cUtil.fn_qMeaStr(null, "Measure.[LCM BOD List W Sub_Time Phased Prty]", timePhasedPrty));
                }
                if( timePhasedShipment !== null && timePhasedShipment !== undefined ){
                    measureBodItem.push(cUtil.fn_qMeaNotStr(null, "Measure.[BOD Item_Time Phased Shipment]", timePhasedShipment));
                    measureListSub.push(cUtil.fn_qMeaStr(null, "Measure.[LCM BOD List W Sub_Time Phased Shipment LT]", timePhasedShipment));
                }
                
                //===============================================================================================//
                // 그리드 공통 선언 부분 - End
                //===============================================================================================//
                
                if ( rowstatus == "C" ) {

                    // 기존 data 중복여부에 대한 체크
                    // 중복 체크 후 생성 (BOD List)
                    if ( !cLib.existMeasure(dimensionList, measureCheck, ""))
                    {
                        //========================================================================================================//
                        // LCM BOD List 생성
                        // 선언한 Measure 모두 Grain (cartesian scope) 시 속도가 느림, Grain 은 한번 생성 후 scope 으로 update
                        //========================================================================================================//
                        let measureCreate = [];
                        measureCreate.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List_BOD Valid]"));
                        cLib.createMeasure(dimensionList, measureCreate);

                        // Add시 메저 추가
                        measureList.push(cUtil.fn_qMeaStr(row, "Measure.[LCM BOD List_BOD Name]", bodName));
                        measureList.push(cUtil.fn_qMeaUpdateUserName("Measure.[LCM BOD List_Init By]"));
                        measureList.push(cUtil.fn_qMeaUpdateTime("Measure.[LCM BOD List_Init Dttm]"));

                        cLib.updateMeasure(dimensionList, measureList);

                        //================================================================================================================================//
                        // LCM BOD List W Sub : Update : 추가 2025.11.26 : Time Phased 추가 2025.11.26 ( Time Phased 화면에서 N 인것은 UI 에서 안보이기 위함, PY 에서는 상속하지 않고 BOD Prod SET 값을 재설정)
                        //================================================================================================================================//
                        if( measureListSub.length > 0){
                            cLib.updateMeasure(dimensionList, measureListSub);
                        }
                    }else{
                        return { "Code" : 1, "Msg" : "This is registerd data." };   // 중복 오류 리턴
                    }

                    //================================================================================================================================//
                    // BOD Item : LCM BOD List 의 확장 Update (신규 생성은 하지 않음)
                    //            - Measure.[BOD Item_Lock Flag] == N 인 경우만 update
                    //   ex) measureBodItem.push('Measure.[BOD Item_BOD LT]         = if( coalesce(Measure.[BOD Item_Lock Flag], "N") == "N") then ' + fn_formatNoStrValue(bodLt) + ' else Measure.[BOD Item_BOD LT]; ');
                    //================================================================================================================================//
                    if( bodValid != null && bodValid == "Y" ){
                        fn_bodItemUpdate(dimension, measureBodItem, fbCategory);
                    }

                } else if ( rowstatus == "U" ) {
                    //================================================================================================================================//
                    // LCM BOD List : Update 
                    //================================================================================================================================//
                    cLib.updateMeasure(dimensionList, measureList);

                    //================================================================================================================================//
                    // LCM BOD List W Sub : Update : 추가 2025.11.26 : Time Phased 추가 2025.11.26 ( Time Phased 화면에서 N 인것은 UI 에서 안보이기 위함, PY 에서는 상속하지 않고 BOD Prod SET 값을 재설정)
                    //================================================================================================================================//
                    cLib.updateMeasure(dimensionList, measureListSub);

                    //================================================================================================================================//
                    // BOD Item - update : LCM BOD List 의 확장 Update
                    //================================================================================================================================//
                    if( bodValid != null && bodValid == "Y" ){
                        fn_bodItemUpdate(dimension, measureBodItem, fbCategory);
                    }
                }
            } // end for

            // LCM BOD List (data) => BOD List (data) 저장 로직, 2025.12.31
            fn_toBodListSave(parsedParams);

            cLib.programEnd();

            //  정상 저장 후 리턴 값?? Warn 종류는 저장은 되고, 화면으로 메세지 리턴해줘야 함
            return { "Code" : 0, "Msg" : "", "Rows" : "" };  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // BOD Item : Update
    var fn_bodItemUpdate = function(dimension, measureBodItem, category){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let dimItem = [...dimension];
            // dimItem.push("&LCMItem");
            dimItem.push("&LCMItemIncludeLED");   // LED 포함 네임드셋으로 변경 2026.04.13 이상엽p 요청

            // BOD Item : Class Category 에 해당하는 Item 가져오기
            let where = 'where { Measure.[BOD Item_Asn] == 1 , [Item].[Class Category]'+cUtil.fn_filterStr(category)+'}';
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

                //-----------------------------2025.12.09 추가-----------------------------------------------------
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

    /**
     * LCM BOD List(MG) => BOD List(MG) 로 저장
     * 신승호P 요청, 2025.12.31 
     * 1. 선택 Row 중 version, Location, Sub Location, Tp Mode 기준으로 중복제거
     * 2. 1에서 중복제거된 데이터로 LCM BOD List 를 (version, Location, Sub Location, Tp Mode) 기준으로 조회 
     *  - (LCM BOD List_BOD Name, LCM BOD List_BOD Valid 메저 속성 Aggregation=Max로 설정)
     * 3. Rollup 된 데이터를 BOD List 에 저장
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_toBodListSave = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            //-------------------------------------------------------------------------------------------------------------------------------//
            // 1. 선택 Row 중 version, Location, Sub Location, Tp Mode 기준으로 중복제거
            //-------------------------------------------------------------------------------------------------------------------------------//
            const grainOnlyUnique = fn_getUniqueGrainRows(parsedParams.fbGridRows);

            cLib.debug("grainOnlyUnique :: "+JSON.stringify(grainOnlyUnique));

            // let fbVersion = cUtil.fn_qDimVersionName(grainOnlyUnique);
            let fbVersion = cUtil.fn_qDimVersionName(parsedParams);
            let fbLocation = [...new Set(grainOnlyUnique.map(row => row["[Location].[Location]"]))];
            let fbSubLocation = [...new Set(grainOnlyUnique.map(row => row["[Sub Location].[Sub Location]"]))];
            let fbTPMode = [...new Set(grainOnlyUnique.map(row => row["[Trans Mode].[Trans Mode]"]))];

            let dimension = [];
            dimension.push(fbVersion);
            dimension.push(cUtil.fn_qDim(null, "[Location].[Location]", fbLocation));
            dimension.push(cUtil.fn_qDim(null, "[Sub Location].[Sub Location]", fbSubLocation));
            dimension.push(cUtil.fn_qDim(null, "[Trans Mode].[Trans Mode]", fbTPMode));

            //-------------------------------------------------------------------------------------------------------------------------------//
            // 2. 1에서 중복제거된 데이터로 LCM BOD List 를 (version, Location, Sub Location, Tp Mode) 기준으로 조회
            //-------------------------------------------------------------------------------------------------------------------------------//
            // 수정된 Row 의 (Version, Location, Sub Location, Tp mode) 기준으로 Rollup
            // LCM BOD List 정보 조회
            // Version, Location, Sub Location, Tp mode , LCM BOD List_BOD Name(max), LCM BOD List_BOD Valid(max) 
            // 에제 Query) Select (&CWVUI*[Location].[Location].filter(#.Name in {"P105LCD","P551LCD"})*[Sub Location].[Sub Location].filter(#.Name in {"P306"})
            //                    *[Trans Mode].[Trans Mode].filter(#.Name in {"AIR"})) on row, 
            //                    ({Measure.[LCM BOD List_BOD Name],Measure.[LCM BOD List_BOD Valid]}) on column ;
            //-------------------------------------------------------------------------------------------------------------------------------//
            let result = cLib.selectList(dimension, ["Measure.[LCM BOD List_BOD Name]", "Measure.[LCM BOD List_BOD Valid]"], "", "", "");
            cLib.debug("result :: "+JSON.stringify(result));
            
            for ( j=0; j<result.cs.rowCount; j++){

                let dimUpdate = [];
                let measureCreate = [];
                let measureUpdate = [];

                // Grain
                dimUpdate.push(cUtil.fn_qDim(null, "[Version].[Version Name]"      , result.cs.row(j).cell(result.cs.memberColumnIndex("Version", "Version Name")).Name));
                dimUpdate.push(cUtil.fn_qDim(null, "[Location].[Location]"         , result.cs.row(j).cell(result.cs.memberColumnIndex("Location", "Location")).Name));
                dimUpdate.push(cUtil.fn_qDim(null, "[Sub Location].[Sub Location]" , result.cs.row(j).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location")).Name));
                dimUpdate.push(cUtil.fn_qDim(null, "[Trans Mode].[Trans Mode]"     , result.cs.row(j).cell(result.cs.memberColumnIndex("Trans Mode", "Trans Mode")).Name));

                // 생성 Measure
                measureCreate.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD List_Created By]"));
                measureCreate.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List_Creation Time]"));

                // 수정 Measure
                measureUpdate.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD List_Updated By]"));
                measureUpdate.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD List_Update Time]"));
                measureUpdate.push(cUtil.fn_qMeaStr(null, "Measure.[BOD List_BOD Name]", result.cs.row(j).cell(result.cs.measureColumnIndex("LCM BOD List_BOD Name"))));
                measureUpdate.push(cUtil.fn_qMeaStr(null, "Measure.[BOD List_BOD Valid]", result.cs.row(j).cell(result.cs.measureColumnIndex("LCM BOD List_BOD Valid"))));
                
                //-------------------------------------------------------------------------------------------------------------------------------//
                // 3. 2의 Rollup 된 데이터를 BOD List 에 저장
                //-------------------------------------------------------------------------------------------------------------------------------//
                if ( !cLib.existMeasure(dimUpdate, ["Measure.[BOD List_BOD Name]", "Measure.[BOD List_BOD Valid]", "Measure.[BOD List_Created By]"], "")){
                    cLib.createMeasure(dimUpdate, measureCreate);
                    cLib.updateMeasure(dimUpdate, measureUpdate);
                }else{
                    cLib.updateMeasure(dimUpdate, measureUpdate);
                }
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 선택 Row의 중복 제거 후 리턴
    var fn_getUniqueGrainRows = function(rows){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("rows :: "+JSON.stringify(rows));

            // 중복 제거 Grain
            // var grainCols = ["[Version].[Version Name]","[Location].[Location]","[Sub Location].[Sub Location]","[Trans Mode].[Trans Mode]"];
            var grainCols = ["[Location].[Location]","[Sub Location].[Sub Location]","[Trans Mode].[Trans Mode]"];
            var map = {};
            var result = [];
            rows = rows || [];

            for( var i = 0; i < rows.length; i++){
                var r = rows[i];

                // key 만들기 (null/undefiend 안전)
                var keyParts = [];
                for (var j=0; j < grainCols.length; j++){
                    var c = grainCols[j];
                    var v = (r && r[c] != null) ? r[c] : "";

                    keyParts.push(String(v));
                }
                var key = keyParts.join("^");

                if( !map[key]){
                    map[key] = true;

                    // 그레인 컬럼만 뽑아서 담기
                    var grainRow = {};
                    for( k = 0; k < grainCols.length; k++ ){
                        var col = grainCols[k];
                        grainRow[col] = r ? r[col] : undefined;
                    }
                    result.push(grainRow);
                }
            }
            return result;
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * fn_saveBodItem : BOD Item저장
     * 
     * @param {*} o9Params 
     * @returns 
     */
    var fn_saveBodItem = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("==========================> LCM BOD Item >> fn_saveBodItem ");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let measureCheck = ["Measure.[BOD Item_Asn]", "Measure.[BOD Item_BOD Valid]", "Measure.[BOD Item_Eff Endweek]", "Measure.[BOD Item_Eff Startweek]"];

            for ( var i=0; i<parsedParams.fbGridRows.length; i++){

                let row = parsedParams.fbGridRows[i];
                let rowstatus = row["rowstatus"];

                let fbLocation      = row["[Location].[Location]"];
                let fbSubLocation   = row["[Sub Location].[Sub Location]"];
                let fbTPMode        = row["[Trans Mode].[Trans Mode]"];

                // Measure
                let bodValid = row["Measure.[BOD Item_BOD Valid]"];
                let bodName = row["Measure.[BOD Item_BOD Name]"];

                if ( bodName === null || bodName === undefined || bodName === ""){
                    bodName = fbLocation + "_" + fbSubLocation + "_" + fbTPMode;    // P532_L5N0_EXPRESS    // UI 에서 BOD Name 을 넘기지 않을 경우 내부적으로 세팅 2025.10.15
                }

                let dimension = [];
                dimension.push(cUtil.fn_qDimVersionName(parsedParams));
                dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
                dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));

                let measureBodItem = [];
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_BOD LT]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Priority]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Shipment LT]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Multi Lot Qty]"));
                measureBodItem.push(cUtil.fn_qMeaInt(row, "Measure.[BOD Item_Min Lot Qty]"));
                measureBodItem.push(cUtil.fn_qMeaNotStr(row, "Measure.[BOD Item_Time Phased BOD]"));
                measureBodItem.push(cUtil.fn_qMeaNotStr(row, "Measure.[BOD Item_Time Phased Prty]"));
                measureBodItem.push(cUtil.fn_qMeaNotStr(row, "Measure.[BOD Item_Time Phased Shipment]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Startweek]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Endweek]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Startdate]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Eff Enddate]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Material Group]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Lock Flag]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Period1]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Period2]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Period3]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_BOD Valid]"));
                measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_Prod Item]"));    // 2026.02.26 add (이상엽p 요청)

                measureBodItem.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item_Updated By]"));
                measureBodItem.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item_Update Time]"));
                measureBodItem.push("Measure.[BOD Item_PyRunFlag] = 1; ");  // Time Phased 의 PY 성능으로 추가 (테스트 2025.11.28 syif1380.lee) PY_UI_BODItemW 시 참고

                //========================================================================================================//
                // BOD Item W 
                //========================================================================================================//
                let measureBodItemW = [];
                measureBodItemW.push("Measure.[BOD Item W_PyRunFlag] = 1; ");  // Time Phased 의 PY 성능으로 추가 (테스트 2025.12.09 syif1380.lee) PY_UI_BODItemW 시 참고
                let dimItemW = [...dimension];
                dimItemW.push(MDMHorizon);

                // 기존 data 중복여부에 대한 체크
                if( rowstatus == "C") {
                    if ( cLib.existMeasure(dimension, measureCheck, "")){
                        return { "Code" : 1, "Msg" : "This is registerd data."};   // 오류 리턴
                    }else{
                        // BOD Item 생성
                        // 선언한 Measure 모두 Grain (cartesian scope) 시 속도가 느림, Grain 은 한번 생성 후 scope 으로 update
                        cLib.createMeasure(dimension, ['Measure.[BOD Item_BOD Valid] = "' + bodValid + '";']);

                        // Add시 메저 추가
                        bodName = fbLocation + "_" + fbSubLocation + "_" + fbTPMode;    // P532_L5N0_EXPRESS    // UI 에서 BOD Name 을 넘기지 않을 경우 내부적으로 세팅 2025.10.15
                        measureBodItem.push(cUtil.fn_qMeaStr(row, "Measure.[BOD Item_BOD Name]", bodName));
                        measureBodItem.push(cUtil.fn_qMeaUpdateUserName("Measure.[BOD Item_Created By]"));
                        measureBodItem.push(cUtil.fn_qMeaUpdateTime("Measure.[BOD Item_Creation Time]"));

                        cLib.updateMeasure(dimension, measureBodItem);

                        //========================================================================================================//
                        // BOD Item W : Update
                        //========================================================================================================//
                        cLib.updateMeasure(dimItemW, measureBodItemW);

                    }

                } else if( rowstatus == "U") {
                    cLib.updateMeasure(dimension, measureBodItem);
                    //========================================================================================================//
                    // BOD Item W : Update
                    //========================================================================================================//
                    cLib.updateMeasure(dimItemW, measureBodItemW);
                }

            } // end for

            cLib.programEnd();

            //  정상 저장 후 리턴
            return { "Code" : 0, "Msg" : "", "Rows" : "" };  // 오류 dataset Return

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
         * fn_merge : Scenario Plan >> 테스트 필요..
         * 2026.03.04 생성
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
                + ',for model [LCM BOD List] '
                + ',for model [BOD Item] '
                +'); ';

                cLib.debug("UpdateScenario >> "+query);
                queryModule.update(query);

            }else if( parsedParams.fbParams["mergeType"] == "0"){

                for ( var i=0; i<parsedParams.fbGridRows.master.length; i++){

                    var row = parsedParams.fbGridRows.master[i];
                    // [Version].[Version Name] * [Location].[Location] * [Item].[Class Category] * [Sub Location].[Sub Location] * [Trans Mode].[Trans Mode]
                    // BOD List 의 dimension 정의
                    let dimBodList = [];
                    dimBodList.push(cUtil.fn_qDim(row, "[Location].[Location]"));
                    dimBodList.push(cUtil.fn_qDim(row, "[Sub Location].[Sub Location]"));
                    dimBodList.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));

                    // LCM BOD List
                    let dimLcmBod = [...dimBodList];
                    dimLcmBod.push(cUtil.fn_qDim(row, "[Item].[Class Category]"));

                    // BOD Item
                    let dimBodItem = [...dimBodList];
                    dimBodItem.push("[Item].[Item]");

                    //-------------------------------------------------------------------------------------
                    // 시나리오 버전 Copy ( fbVersion => toVersion (CWP_MP) 로 copy )
                    // 각 MG 의 시나리오 버전 데이터가 없는 경우 copy 안됨
                    //-------------------------------------------------------------------------------------
                    let query = 'UpdateScenario( '
                    + toVersion         // To 버전
                    + ',' + "[Version].[Version Name].["+fbVersion+"]"   // 시나리오 버전(from 버전)
                    + ',false'
                    + ',for model [LCM BOD List] using scope (' + dimLcmBod.join('*') + ')'
                    + ',for model [BOD Item] using scope (' + dimBodItem.join('*') + ')'
                    +'); ';

                    cLib.debug("UpdateScenario >> "+query);
                    queryModule.update(query);

                    //-------------------------------------------------------------------------------------
                    // LCM BOD List : 사용자 Update > 시나리오 버전 Data 가 존재할 때만 update
                    //-------------------------------------------------------------------------------------
                    let dimBodListChk = [...dimLcmBod];
                    dimBodListChk.push("[Version].[Version Name].["+fbVersion+"]"); // 시나리오 버전
                    if( cLib.existMeasure(dimBodListChk, ["Measure.[LCM BOD List_BOD Valid]"], "") ){

                        dimLcmBod.push(toVersion);

                        let measure = [];
                        measure.push(cLib.fn_mergeUser("Measure.[LCM BOD List_Up By]", fbVersion));
                        measure.push(cUtil.fn_qMeaUpdateTime("Measure.[LCM BOD List_Up Dttm]"));
                        cLib.updateMeasure(dimLcmBod, measure);
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
    //    ,"fn_cb_location"        : fn_cb_location
       "fn_cb_subLocation"     : fn_cb_subLocation
       ,"fn_cb_category"        : fn_cb_category
       ,"fn_cb_itemClassCategory" : fn_cb_itemClassCategory
       ,"fn_cb_item"            : fn_cb_item
       ,"fn_cb_fromItem"        : fn_cb_fromItem
       ,"fn_cb_product"         : fn_cb_product
       ,"fn_save"               : fn_save
       ,"fn_saveBodItem"        : fn_saveBodItem
       ,"fn_toBodListSave"      : fn_toBodListSave // 테스트 , 차후삭제 요기부분만
       ,"fn_merge"              : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 
    프로그램명 : o9.NSCM.JSEWBODListLCM
    화면명 : LCM BOD List (EW)
    Action Button : EWBODListLCM
    [history]
    js 파일 저장시 오류로 새로생성 2025.08.08
    20256.08.26 : syif1380.lee : combo > fn_cb_item, fn_cb_fromItem, fn_cb_product 생성
                    BOD Item : 저장 기능 추가 
    2025.09.02 : LCM BOD Item List 의 콤보 추가 (Material Group) : fn_cb_itemClassCategory
    2025.10.17 : 공통소스 반영
    2025.10.28 : 메저명 변경 : LCM BOD List_BOD Vaild  (변경 전)  => LCM BOD List_BOD Valid  (변경 후)
    2025.11.05 : fn_qMeaUpdateUser() => fn_qMeaUpdateUserName() 로 변경 
    2025.11.26 : fn_save() 수정 : BOD Alt 저장시 BOD Prod SET W Sub > 저장
                Measure.[LCM BOD List W Sub_Time Phased Prty]
                Measure.[LCM BOD List W Sub_Time Phased BOD LT]
                Measure.[LCM BOD List W Sub_Time Phased Shipment LT]
    2025.12.09 : Measure.[BOD Item_PyRunFlag] , Measure.[BOD Item W_PyRunFlag] = 1 세팅 로직 추가 (SET BOD Time Phased 화면에서 Reload시 성능향상을 위해 사용)
    2025.12.29 : 콤보에 filter 적용
    2025.12.31 : 저장시 : fn_toBodListSave 추가 : LCM BOD List(MG) => BOD List(MG) 로 저장 (신승호P 요청)
    2026.02.26 : 저장시 : fn_saveBodItem : Measure.[BOD Item_Prod Item] 추가 (이상엽p요청)
    2026.03.03 : fn_merge() : Scenario Plan 정의
                 콤보데이터 : &CWVUI 하디코딩 -> cUtil.fn_getFilterQuery 변경
    2026.03.04 : fn_merge() : Scenario Plan 정의 -> UpdateScenario 로 변경
    2026.03.10 : fn_cb_fromItem() : Code Map LCM_Prod Item => To Item 으로 변경 (2026.03.10 이상엽P요청)
    2026.03.18 : fn_merge() : mergeType 추가 정의
    2026.03.26 : commonLib 선언 부분 변경 및 공통함수 이름 변경
    2026.03.26 : fn_cb_product : where 조건 수정 : [Item].[Item Stage].filter(#.Name in {"LCM", "LED_MODULE"}) 이상엽p요청
                 - fn_cb_item, fn_cb_fromItem : where 조건 추가 : Measure.[Code Map LCM_Map Status] == "COM"'
    2026.04.13 : LED 포함 > NamedSet 변경 : &LCMItem => &LCMItemIncludeLED (이상엽p요청)
    2026.04.20 : fn_cb_fromItem : Measure.[Code Map LCM_Map Status] == "CON"' 변경 (이상엽p요청)
*/
/*--------------------------------------------------------------------------------------------------*/