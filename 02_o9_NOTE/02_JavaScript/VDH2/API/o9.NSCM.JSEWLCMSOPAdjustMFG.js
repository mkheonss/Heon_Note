define('o9.NSCM.JSEWLCMSOPAdjustMFG', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWLCMSOPAdjustMFG
    // 화면명 : LCM SOP Adjust MFG (EW)
    // Action Button : EWSOPAdjustmentLCMMFG
    // EW 개발자 : 김동수p
    // 최초생성 : 2025.09.16 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWLCMSOPAdjustMFG";
    const MPHorizon = "&MPHorizon";
    const MEAS_KEYS = ["adjQty","chgQty","reason","changedFlag"];   // changedFlag 11.17 추가
    const strSplit = "^";
    const queryModule = require('o9/data/query');

    //================================================== -[Combo Data] ==========================================//
    /*------------------------------------------------------------------------------------------------------------
    From Site           > EWCommonVD            > { "fbFuncName" : "fn_cb_siteMfLcm", "fbParams" : {} }
    To Site             > EWCommonVD            > { "fbFuncName" : "fn_cb_siteMF", "fbParams" : {} }
    TPMode Group        > EWCommonVD            > { "fbFuncName" : "fn_cb_tpmodeGO", "fbParams" : {} }
    To Item             > EWSOPAdjustmentLCMMFG > { "fbFuncName" : "fn_cb_item" , "fbParams" : { "[Location].[Location]" : "P406", "[Sub Location].[Sub Location]":"P551LCD" } }
    From Item           > EWSOPAdjustmentLCMMFG > 
    -------------------------------------------------------------------------------------------------------------*/

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

    // Item > Prod Item > Cell Code 순서 변경 (2025.05.07 노보람p요청)
    // Item  : [To Item].[To Item]
    var fn_cb_toItem = function(parsedParams){

        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {

            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));
            
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];

            // BOM 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ cUtil.fn_filterStr(fbSubLocation)          // From Site
            +', &NSUISiteGrp3LCMView '
            +', Item.[Item Stage].[OPEN_CELL] '
            // +', [Item].[Item]'+ cUtil.fn_filterStr(fbItemMaterial)                 // Cell code (순서 변경으로 삭제 2025.05.07)
            +', [BOM Info].[BOM ID] , Measure.[BOM Comp_Valid Flag] == true '
            +'}';
            var result = cLib.selectList(["[BOM Info].[Item]"],
                                                "",     // measure
                                                where,  // where
                                                "",     // "orderby [Item].[Item].Name desc",    // orderby
                                                "");    // limit
            // 2025.04.17 이전
            // var where = 'where {'
            //                 +' &CWVUI'
            //                 +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
            //                 +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
            //                 +', [Trans Mode].[Trans Mode]'+ cUtil.fn_filterStr(fbTPMode)
            //                 +'}';

            // // &LCMItem 중 BOD Item 에 없는 Item.Item List
            // var result = cLib.selectList(["&LCMItem"],
            //                                 ["Measure.[BOD Item_Asn]"
            //                                 ,"Measure.[BOD Item_Cur Status]"
            //                                 ,"Measure.[BOD Item_BOD Frozen]"
            //                                 ,"Measure.[BOD Item_Eff Startdate]"
            //                                 ,"Measure.[BOD Item_Eff Enddate]"
            //                                 ,"Measure.[BOD Item_Min Lot Qty]"
            //                                 ,"Measure.[BOD Item_Multi Lot Qty]"
            //                                 ],    // measure
            //                                 where,
            //                                 "",
            //                                 "");

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "BOM Info", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return comboList;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };
    
    // Prod Item : [Item Component].[Item Component]
    var fn_cb_itemComponent = function(parsedParams){

        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {

            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            var fbToItem = parsedParams.fbParams["[To Item].[To Item]"];

            // LCM Code MAP 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
                            +' &CWVUI'
                            +', [Location].[Location]'+ cUtil.fn_filterStr(fbSubLocation)  // From Site
                            +', [To Item].[To Item]'+ cUtil.fn_filterStr(fbToItem)
                            +', Measure.[LCM Code MAP_Status] == "COM" '
                            +'}';
            var result = cLib.selectList(["[Item].[Item]"],
                                            "",//["Measure.[LCM Code MAP_Status]"],
                                            where, // where                                           
                                            "",
                                            "");  //"limit 1000"

            // var where = 'where {'
            //                 +' &CWVUI'
            //                 +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
            //                 +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
            //                 +', [Trans Mode].[Trans Mode]'+ cUtil.fn_filterStr(fbTPMode)
            //                 +', ~isnull(Measure.[BOD Item_Prod Item]) '
            //                 +'}';

            // // dimension 총 4 Row
            // var result = cLib.selectList(["[Item].[Item]"+ cUtil.fn_filterStr(fbToItem)],
            //                                  ["Measure.[BOD Item_Prod Item]"],
            //                                 //   "where { ~isnull(Measure.[BOD Item_Prod Item]) }",
            //                                   where,
            //                                   "",
            //                                   "");

            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            // var comboList = cLib.fn_makeCombo(result, {MeasureName : "BOD Item_Prod Item",  existAll : false});            
            
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return comboList;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // Cell Code : [Item Material].[Item Material]
    var fn_cb_itemMaterial = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        try {

            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            
            let fbSubLocation = parsedParams.fbParams["[Sub Location].[Sub Location]"];
            var fbItemComponent = parsedParams.fbParams["[Item Component].[Item Component]"]; // Prod Item

            // dimension 총 79,610 Row
            // var result = cLib.selectList(["[Item Material].[Item Material]"],
            //                                  [],    // measure
            //                                   "",
            //                                   "",
            //                                   "");  // limit

            
            // BOM 정보 가져오기 (임재민p, 노보람p 요청 - 2025.04.17)
            var where = 'where {'
            +' &CWVUI'
            +', [Location].[Location]'+ cUtil.fn_filterStr(fbSubLocation)          // From Site
            +', &NSUISiteGrp3LCMView '
            +', Item.[Item Stage].[OPEN_CELL] '
            +', [BOM Info].[BOM ID] , Measure.[BOM Comp_Valid Flag] == true '
            +', [BOM Info].[Item]'+ cUtil.fn_filterStr(fbItemComponent)             // add 2025.05.07 테스트중..
            +'}';
            var result = cLib.selectList(["[Item].[Item]"],
                                                "",     // measure
                                                where,  // where
                                                "",     // "orderby [Item].[Item].Name desc",    // orderby
                                                "");    // limit

            cLib.printCsData(result, 3);

            // var comboList = cLib.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "Item Material", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return comboList;

        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // 중복체크
    var fn_chk_duplicated = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("row :: "+JSON.stringify(row));

            let fbVersion       = row["[Version].[Version Name]"];
            let fbLocation      = row["[Location].[Location]"];
            let fbSubLocation   = row["[Sub Location].[Sub Location]"];
            let fbTPMode        = row["[To Trans Mode].[To Trans Mode]"];
            let fbToItem        = row["[To Item].[To Item]"];
            let fbWeek          = row["[Week1].[Week1]"];
            let fbItemComponent = row["[Item Component].[Item Component]"];
            let fbItemMaterial  = row["[Item Material].[Item Material]"];
            
            var dimension = ["[Version].[Version Name].[" + fbVersion + "]"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[To Trans Mode].[To Trans Mode].[" + fbTPMode + "]"
                            ,"[To Item].[To Item].[" + fbToItem + "]"
                            ,"[Week1].[Week1].[" + fbWeek + "]"
                            ,"[Item Component].[Item Component].[" + fbItemComponent + "]"
                            ,"[Item Material].[Item Material].[" + fbItemMaterial + "]"
                            ];

            // 중복체크
            if ( cLib.existMeasure(dimension,["Measure.[SOP Adjust LCM W_SOP Adj Qty]","Measure.[SOP Adjust LCM W_Chg Qty]","Measure.[SOP Adjust LCM W_Chg Reason]"], "")) {
                return false;
            }else{
                return true;
            }
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    var fn_chk_item = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("fn_chk_item======================>");
        try {
            cLib.debug("row :: "+JSON.stringify(row));
            let fbLocation = row["[Location].[Location]"];
            let fbSubLocation = row["[Sub Location].[Sub Location]"];
            let fbToItem = row["[Item].[Item]"];
            let fbFromItem = row["[To Item].[To Item]"]; // 26.04.10 한승진 LCM PROD COPY KEY 변경 반영
            let fbItemComponent = row["[Item Component].[Item Component]"];

            cLib.debug("fbToItem :: "+fbToItem);

            // 입력 메저가 없으면 skip
            if( fbToItem === null || fbToItem === undefined){
                return false;
            }

            let dimension = ["&CWVUI"
                            ,"[Location].[Location].[" + fbSubLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbLocation + "]"
                            ,"[Item].[Item].[" + fbToItem + "]"   // PO ITEM(TO ITEM)
                            ,"[To Item].[To Item].[" + fbFromItem + "]"];   // PROD ITEM(FROM ITEM) 26.04.10 한승진 LCM PROD COPY KEY 변경 반영

            let where = 'where { '
                            +', Measure.[Code Map LCM_Prod Item] == "'+ fbItemComponent + '" '  // FROM ITEM 26.04.10 한승진 LCM PROD COPY KEY 변경 반영
                            +'}';
            let result = cLib.selectList(dimension
                                            , ['Measure.[Code Map LCM_Prod Item]','Measure.[Code Map LCM_PO Item]']
                                            , where, "", "");
            
            
            cLib.printCsData(result, 1);

            if( result.cs.rowCount > 0){
                return true;
            }else{
                return false;
            }
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    
    // Negative SOP Qty : 음수값 체크
    var fn_chk_adjQty = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("fn_chk_adjQty======================>");
        try {
            cLib.debug("row :: "+JSON.stringify(row));
            let adjQty = row["Measure.[SOP Adjust LCM W_SOP Adj Qty]"];

            cLib.debug("adjQty :: "+adjQty);

            // 입력 메저가 없으면 skip
            if( adjQty === null || adjQty === undefined){
                cLib.debug("###############  adjQty Check Skip ");
                return true;
            }

            // 입력 메저가 있으면 체크
            if( cUtil.fn_isInt(adjQty) && adjQty < 0 ){
                cLib.debug("###############  adjQty < 0 >> false ");
                return false;
            }else{
                cLib.debug("###############  adjQty > 0 >> true ");
                return true;
            }
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 유틸 함수
    // "YYYYWW^val" 파싱
    var parseToken = function(token){
        const s= String(token).trim();
        if (!s) return { week: "", raw: ""};
        const parts = s.split("^");
        const week = (parts[0] || "").trim();
        const raw = (parts[1] || "").trim();
        return {week, raw};
    }

    // 입력 값이 배열/문자열/단일값 모두 허용되게 변환
    var normalizeList = function(val){
        if ( Array.isArray(val)) return val;
        if (val == null) return [];
        const s = String(val).trim();
        if (!s) return [];
        return s.split(".").map(x => x.trim()).filter(Boolean);
    }

    const DB_KEYS = {
        version         : "[Version].[Version Name]"
       ,loc             : "[Location].[Location]"
       ,subLoc          : "[Sub Location].[Sub Location]"
       ,toTpmode        : "[To Trans Mode].[To Trans Mode]"
       ,toItem          : "[To Item].[To Item]"
       ,itemComponent   : "[Item Component].[Item Component]"
       ,itemMaterial    : "[Item Material].[Item Material]"
       ,week            : "[Week1].[Week1]"
    }

    // fbGridRows : col => row 로 변환
    var fn_colToRowData = function(rows){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        const bucket = new Map(); // key:groupkey|loc|toloc|week -> row

        for ( const row of (rows || {})){
            // 메저 키만 추출
            const measureKeys = Object.keys(row).filter(k => k.startsWith("Measure.["));

            for ( const mKey of measureKeys){
                const list = normalizeList(row[mKey]); // 배열 표준화

                for ( const token of list){
                    const {week, raw} = parseToken(token);
                    if( !week ) continue;

                    const rowstatus     = row.rowstatus;
                    const gk            = row.groupkey;
                    const version       = row[DB_KEYS.version];
                    const loc           = row[DB_KEYS.loc];
                    const subLoc        = row[DB_KEYS.subLoc];
                    const toTpmode      = row[DB_KEYS.toTpmode];
                    const toItem        = row[DB_KEYS.toItem];
                    const itemComponent = row[DB_KEYS.itemComponent];
                    const itemMaterial  = row[DB_KEYS.itemMaterial];

                    if (gk == null) continue;

                    // const key = [gk, loc, toloc, week].map(x => String(x || "")).join("|");
                    const key = [gk, week].map(x =>  String(x || "")).join("|");

                    let acc = bucket.get(key);
                    if( !acc) {
                        // acc = { groupkey: gk, version, loc, toloc, tpmode, item, week };
                        acc = { rowstatus, groupkey: gk, [DB_KEYS.version]:version, [DB_KEYS.loc]:loc, [DB_KEYS.subLoc]:subLoc, [DB_KEYS.toTpmode]:toTpmode, [DB_KEYS.toItem]:toItem
                                                       , [DB_KEYS.itemComponent]:itemComponent, [DB_KEYS.itemMaterial]:itemMaterial, [DB_KEYS.week]:week };
                        bucket.set(key, acc);
                    }

                    acc[mKey] = raw;
                }
            }
        }

        return Array.from(bucket.values());
    }

    /**
     * Picklist : SOPChgReason > [Category].[Category] Member에 등록 함 ( 2026.01.26 한승진p)
     * @returns 
     */
    var fn_getChgReason = function(){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            // SELECT ([Category].[Category]) where {[Category].[Category Type].[SOP Chg Reason]};
            let result = cLib.selectList(['[Category].[Category]'] ,[], 'where {[Category].[Category Type].[SOP Chg Reason]}', '', '');

            // SOP Chg Reason
            let sopChgReasonList = [];
            for ( k=0; k<result.cs.rowCount; k++){
                let getCategory = result.cs.row(k).cell(result.cs.memberColumnIndex("Category", "Category")).Name;
                sopChgReasonList.push(getCategory);
            }

            return sopChgReasonList;
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_appendError = function(str, flagStr){
        return (str || "") + strSplit + flagStr;
    }

    var fn_validation = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("#################### fn_validation params :: "+JSON.stringify(params));

            let MPHorizonDataJson = cLib.fn_getMondayForNS("MPHorizon");    // &MPHorizon Data
            cLib.debug("MPHorizonData :: "+JSON.stringify(MPHorizonDataJson));

            let sopChgReasonList = fn_getChgReason();    // Picklist > SOPChgReason

            let box = {};
            let errCnt = 0;  // 오류건수
            let warnCnt   = 0; // Warn 건수

            for (const row of params) {

                let gk = row.groupkey;
                if ( !box[gk] ) box[gk] = {groupkey: gk, rowvalid:[], rowmsg:[]};

                if( row.rowstatus !== "C" && row.rowstatus !== "U" ) coutinue;

                let weekVal = row["[Week1].[Week1]"];
                cLib.debug("####### weekVal :: "+weekVal);

                // params 에 해당주차의 월요일을 컬럼을 생성한다.
                if( MPHorizonDataJson.hasOwnProperty(weekVal) ){
                    row.weekMonday = MPHorizonDataJson[weekVal];
                }else{
                    row.weekMonday = null;    // 매핑주차가 없을 경우 null
                }

                // 1.[key] Horizon 체크
                if ( row.weekMonday == null ){
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("Horizon에 해당 주차가 존재하지 않음");
                }

                // 2.[key] Duplicated : Grain 중복 방지
                if( row.rowstatus == "C" ) {
                    if( !fn_chk_duplicated(row) ){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("key 값 중복");
                    }
                }
                
                // // 1.[value] Chg Reason : Chg Reason 없이 Qty입력 방지
                // if( !fn_chk_changeReason(row) ) {
                //     errCnt++;
                //     box[gk].rowvalid.push("Error");
                //     box[gk].rowmsg.push("CHG Reason을 입력하세요.");
                // }

                // [Category].[Category Type].[SOP Chg Reason]
                if( row["Measure.[SOP Adjust LCM W_Chg Reason]"] !== undefined && row["Measure.[SOP Adjust LCM W_Chg Reason]"] !== null && row["Measure.[SOP Adjust LCM W_Chg Reason]"] !== "" ){
                    if( !sopChgReasonList.includes(row["Measure.[SOP Adjust LCM W_Chg Reason]"])){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("유효한 CHG Reason을 입력하세요.");
                    }
                }

                if( !fn_chk_item(row) ){
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("Item(To Item) or Prod Item(From Item) 이 존재하지 않습니다.");
                }

                // 2.[value] Negative SOP Qty : Chg Qty입력시에도 체크
                if( !fn_chk_adjQty(row) ){
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("SOP는 음수가 될 수 없습니다.");
                }

            }

            let result = Object.values(box).map(r => ({
                groupkey : r.groupkey,
                rowvalid : r.rowvalid.length ? r.rowvalid.join("^") : null, 
                rowmsg   : r.rowmsg.length ? r.rowmsg.join("^") : null
            }));
            
            //=========================================================================================================//
            // 오류 Check
            //=========================================================================================================//
            cLib.debug("errCnt + warnCnt :: =========================[ "+(errCnt+warnCnt)+" ]");
            cLib.debug("################ validation return >> result =====> :: "+JSON.stringify(result));

            return { errCnt,  warnCnt, "Rows": result};

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 저장
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));

            let validationResult = {};
            let GridRow = {};

            let paramsOrg = parsedParams.fbGridRows;
            let gridType = parsedParams.fbParams["gridType"];  // row / col

            let validCheck = parsedParams.fbParams["validCheck"]; // Y / N
            if( validCheck === null || validCheck === undefined){
                validCheck = "N";
            }

            let saveType = parsedParams.fbParams["saveType"]; // API 저장 테스트용 임시 컬럼 (Test 화면에서) , 저장하지 않기 위함
            if( saveType === null || saveType === undefined || saveType === ""){
                saveType = "";
            }else{
                saveType = "save Skip";
            }

            if( gridType == "row"){
                GridRow = paramsOrg;
            } else if( gridType == "col"){
                GridRow = fn_colToRowData(paramsOrg);  // 전체 : Col => Row 로 변환 (validation Check 위함)
                cLib.debug("####  :: row 변환 Data >>>>>>>>>>>>>>>>>>>>>>"+ JSON.stringify(GridRow));
            }

            //############################  Validation 체크 구간.. 테스트로 주석 처리 2026.04.09 #####################//
            // if( validCheck == "N"){
            //     // validationResult = fn_validation(GridRow);    // validation Check  // 테스트로 주석처리
            //     validationResult = fn_validation(GridRow);    // validation Check // 신규 버전으로 테스트 후 전환 처리
            //
            //     cLib.debug("#### validation 하기 위한 포맷 :: validationResult :: "+ JSON.stringify(validationResult));
            //
            //     cLib.debug("######## error : "+(validationResult.errCnt + validationResult.warnCnt));
            //     if ( (validationResult.errCnt + validationResult.warnCnt) > 0 ){
            //         // validation 오류 : Code : 1
            //         return { "Code" : 1, "Msg" : "valid", "ErrorCount":validationResult.errCnt, "WarnCount":validationResult.warnCnt, "Rows" : validationResult.Rows};  // 오류 dataset Return
            //     }
            // }
            //########################################################################################################//

            if ( saveType != "save Skip"){  // Test 화면에서 테스트시 저장 skip 용, 일반 테스트는 저장 됨 (validation 테스트용으로..)

                // validation 성공시 저장
                for ( var i=0; i<GridRow.length; i++){
                    let rowstatus = GridRow[i]["rowstatus"];
                    cLib.debug("#### rowstatus : "+rowstatus);
                    if ( rowstatus == "C" ){
                        fn_create(GridRow[i]);
                    }else if ( rowstatus == "U" ){

                        if( gridType == "row"){
                            GridRow[i]["Measure.[changedFlag]"] = "Y";
                        }
                        fn_update(GridRow[i]);
                    }else if ( rowstatus == "D" ){
                        fn_delete(GridRow[i]);
                    }
                }
            }

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 신규생성 (add)
    var fn_create = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("row :: "+JSON.stringify(row));

            let fbVersion       = row["[Version].[Version Name]"];
            let fbLocation      = row["[Location].[Location]"];
            let fbSubLocation   = row["[Sub Location].[Sub Location]"];
            let fbTPMode        = row["[To Trans Mode].[To Trans Mode]"];
            let fbToItem        = row["[To Item].[To Item]"];
            let fbWeek          = row["[Week1].[Week1]"];
            let fbItemComponent = row["[Item Component].[Item Component]"];
            let fbItemMaterial  = row["[Item Material].[Item Material]"];

            // Measure
            let adjQty = row["Measure.[SOP Adjust LCM W_SOP Adj Qty]"];    // SOP Qty (Adj Qty)
            let chgQty = row["Measure.[SOP Adjust LCM W_Chg Qty]"];        // CHQ Qty
            let chgReason = row["Measure.[SOP Adjust LCM W_Chg Reason]"];  // CHQ Reason

            row["rowmsg"] = null;

            var dimension = ["[Version].[Version Name].[" + fbVersion + "]"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[To Trans Mode].[To Trans Mode].[" + fbTPMode + "]"
                            ,"[To Item].[To Item].[" + fbToItem + "]"
                            ,"[Week1].[Week1].[" + fbWeek + "]"
                            ,"[Item Component].[Item Component].[" + fbItemComponent + "]"
                            ,"[Item Material].[Item Material].[" + fbItemMaterial + "]"
                            ];
            // 중복체크
            if ( !cLib.existMeasure(dimension
                                        ,["Measure.[SOP Adjust LCM W_Before Adj Qty]", "Measure.[SOP Adjust LCM W_Chg Qty]"
                                        ,"Measure.[SOP Adjust LCM W_SOP Adj Qty]"    ,"Measure.[SOP Adjust LCM W_SOP Qty]", "Measure.[SOP Adjust LCM W_Chg Reason]"]
                                        , "")) {
                
                let measure = [];
                if( adjQty !== null && adjQty !== undefined ){
                    measure.push('Measure.[SOP Adjust LCM W_SOP Adj Qty]  = ' + adjQty + ';');     // SOP Qty : UI 에서 null 시 "" 로 데이타 넘김
                }
                if( chgQty !== null && chgQty !== undefined ){
                    measure.push('Measure.[SOP Adjust LCM W_Chg Qty]      = ' + chgQty + ';');     // CHG Qty : UI 에서 null 시 "" 로 데이타 넘김
                }
                if( chgReason !== null && chgReason !== undefined ){
                    measure.push('Measure.[SOP Adjust LCM W_Chg Reason]   = "' + chgReason + '";');     // CHG Reason
                }
                measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust LCM W_Created By]"));
                measure.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust LCM W_Create Time]"));
                measure.push(cUtil.fn_qMeaStr(null, "Measure.[SOP Adjust LCM W_Apply Flag]","A"));  // PY 실행시 : Add or update 된 데이터를 대상으로만 처리될 수 있게 하고자 Flag를 추가하고자 함 (추가 2026.04.09 한승진p)

                cLib.createMeasure(dimension, measure);
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // update 로직
    var fn_update = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("row :: "+JSON.stringify(row));

            let fbVersion       = row["[Version].[Version Name]"];
            let fbLocation      = row["[Location].[Location]"];
            let fbSubLocation   = row["[Sub Location].[Sub Location]"];
            let fbTPMode        = row["[To Trans Mode].[To Trans Mode]"];
            let fbToItem        = row["[To Item].[To Item]"];
            let fbWeek          = row["[Week1].[Week1]"];
            let fbItemComponent = row["[Item Component].[Item Component]"];
            let fbItemMaterial  = row["[Item Material].[Item Material]"];

            // Measure
            let adjQty = row["Measure.[SOP Adjust LCM W_SOP Adj Qty]"];    // SOP Qty (Adj Qty)
            let chgQty = row["Measure.[SOP Adjust LCM W_Chg Qty]"];        // CHQ Qty
            let chgReason = row["Measure.[SOP Adjust LCM W_Chg Reason]"];  // CHQ Reason  추가??? 2025.09.17
            let changedFlag = row["Measure.[changedFlag]"];                // ChangedFlag , 주차별 변경 여부 추가 - 한승진p요청(2025.11.17)
           
            row["rowmsg"] = null;

            var dimension = ["[Version].[Version Name].[" + fbVersion + "]"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[To Trans Mode].[To Trans Mode].[" + fbTPMode + "]"
                            ,"[To Item].[To Item].[" + fbToItem + "]"
                            ,"[Week1].[Week1].[" + fbWeek + "]"
                            ,"[Item Component].[Item Component].[" + fbItemComponent + "]"
                            ,"[Item Material].[Item Material].[" + fbItemMaterial + "]"
                            ];

            // measure => {"adjQty":1,"chgQty":50,"reason":"test05"}
            let measure = {};
            if( adjQty !== null && adjQty !== undefined ){
                measure[MEAS_KEYS[0]] = adjQty;
            }

            if( chgQty !== null && chgQty !== undefined ){
                measure[MEAS_KEYS[1]] = chgQty;
            }

            if( chgReason !== null && chgReason !== undefined ){
                measure[MEAS_KEYS[2]] = chgReason;
            }

            // ChangedFlag , 주차별 변경 여부 추가 - 한승진p요청(2025.11.17)
            if( changedFlag !== null && changedFlag !== undefined ){
                measure[MEAS_KEYS[3]] = changedFlag;
            }

            cLib.debug("##### fn_update >>>>> measure > " + JSON.stringify(measure));

            fn_updateCommon(dimension, measure);

            cLib.programEnd();

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // row/col Update 공통 처리 
    // measure {}
    // fn_updateCommon(dimensionW, row.measure);
    // measure => {"chgQty":50,"reason":"test05"}
    var fn_updateCommon = function(dimension, measure){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            let measureCheck = ["Measure.[SOP Adjust LCM W_SOP Adj Qty]", "Measure.[SOP Adjust LCM W_Chg Qty]", "Measure.[SOP Adjust LCM W_Chg Reason]", "Measure.[SOP Adjust LCM W_SOP Qty]"];

            let measureStr = [];
            if( measure.hasOwnProperty(MEAS_KEYS[0])){
                measureStr.push('Measure.[SOP Adjust LCM W_SOP Adj Qty] = ' + measure[MEAS_KEYS[0]] + ';');
            }

            if( measure.hasOwnProperty(MEAS_KEYS[1])){
                measureStr.push('Measure.[SOP Adjust LCM W_Chg Qty] = ' + measure[MEAS_KEYS[1]] + ';');
            }

            if( measure.hasOwnProperty(MEAS_KEYS[2])){
                measureStr.push('Measure.[SOP Adjust LCM W_Chg Reason] = "' + measure[MEAS_KEYS[2]] + '";');
            }

            // PY 실행시 : Add or update 된 데이터를 대상으로만 처리될 수 있게 하고자 Flag를 추가하고자 함 (추가 2026.04.09 한승진p)
            measureStr.push(cUtil.fn_qMeaStr(null, "Measure.[SOP Adjust LCM W_Apply Flag]","N"));

            // 중복이 없으면 생성
            if( measureStr.length > 0){
                if ( !cLib.existMeasure(dimension, measureCheck, "")){
                    fn_setUpdateByInfo("C", measure, measureStr);
                    cLib.createMeasure(dimension, measureStr);
                }else{
                    fn_setUpdateByInfo("U", measure, measureStr);
                    cLib.updateMeasure(dimension, measureStr);
                }
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // UI 에서 변경정보가 있는 주차일 경우 생성일자,생성자,수정일자,수정자 를 update 한다.
    // ChangedFlag , 주차별 변경 여부 추가 - 한승진p요청(2025.11.17)
    var fn_setUpdateByInfo = function(updateFlag, measure, measureStr){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("########### fn_setUpdateByInfo ");
            cLib.debug("measure :: "+JSON.stringify(measure));
            cLib.debug("measureStr :: "+JSON.stringify(measureStr));

            if( measure.hasOwnProperty(MEAS_KEYS[3])){
                if( measure[MEAS_KEYS[3]] == "Y" ){
                    if ( updateFlag == "C" ){
                        measureStr.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust LCM W_Created By]"));
                        measureStr.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust LCM W_Create Time]"));
                    } else if ( updateFlag == "U" ){
                        measureStr.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust LCM W_Updated By]"));
                        measureStr.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust LCM W_Update Time]"));
                    }
                }
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // delete 로직
    var fn_delete = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(row));

            let fbVersion       = row["[Version].[Version Name]"];
            let fbLocation      = row["[Location].[Location]"];
            let fbSubLocation   = row["[Sub Location].[Sub Location]"];
            let fbTPMode        = row["[To Trans Mode].[To Trans Mode]"];
            let fbToItem        = row["[To Item].[To Item]"];
            let fbWeek          = row["[Week1].[Week1]"];
            let fbItemComponent = row["[Item Component].[Item Component]"];
            let fbItemMaterial  = row["[Item Material].[Item Material]"];

            row["rowmsg"] = null;

            var dimension = ["[Version].[Version Name].[" + fbVersion + "]"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                            ,"[To Trans Mode].[To Trans Mode].[" + fbTPMode + "]"
                            ,"[To Item].[To Item].[" + fbToItem + "]"
                            ,"[Week1].[Week1].[" + fbWeek + "]"
                            ,"[Item Component].[Item Component].[" + fbItemComponent + "]"
                            ,"[Item Material].[Item Material].[" + fbItemMaterial + "]"
                            ];
    
            cLib.deleteMeasure(dimension, "SOP Adjustment LCM W");

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // PY_UI_SOPAdjustLCM 호출 함수 , 선택row 로 실행할지, 전체 실행할지 결정 필요........... 2025.06.26 syif1380.lee
    var fn_apply = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            // cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));
            cLib.debug(" PY 호출 ======================>PY_UI_SOPAdjustLCM");
            
            // let fbLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Location].[Location]"]))];
            // let fbSubLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Sub Location].[Sub Location]"]))];
            // let fbToItem = [...new Set(parsedParams.fbGridRows.map(row => row["[To Item].[To Item]"]))];

            // cLib.debug("=====>fn_savePostProcess :: fbLocation :: "+fbLocation);
            // cLib.debug("=====>fn_savePostProcess :: fbSubLocation :: "+fbSubLocation);
            // cLib.debug("=====>fn_savePostProcess :: fbToItem :: "+fbToItem);

            var execQuery = 'EXEC plugin instance [PY_UI_SOPAdjustLCM] ' +
                            'for measures {[SOP W_LCM MFG Qty]} ' +
                            'using scope ( &CWVUI ) ' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1), ([Param.o9_sys_log_level], "DEBUG")}; ';   // 2025.02.04 수정 (권태우B 요청)


            /* Validation 호출 (PY_UI_SOPAdjustLCM) */
            // var execQuery = 'EXEC plugin instance [PY_UI_SOPAdjustLCM] ' +
            //                 'for measures {[SOP W_LCM MFG Qty]} ' +
            //                 'using scope ( &CWVUI '
            //                             + ' * ' + '[Location].[Location]' + cUtil.fn_filterStr(fbLocation)
            //                             + ' * ' + '[To Location].[To Location]' + cUtil.fn_filterStr(fbSubLocation)
            //                             + ' * ' + '[Item].[Item]' + cUtil.fn_filterStr(fbItem)
            //                             ') ' +
            //                 'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")}; ';      // 2025.02.04 수정(권태우B 요청)

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_apply : PY_UI_SOPAdjustLCM Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 프로시저 호출 2026.03.18 생성
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_SOPAdjustLCM = async function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

        try {
            await fn_exec_procedure(parsedParams);
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * 프로시저 호출 담당
     * @param {*} parsedParams 
     * versionName(single select) , Location(Multi select) 
     * 
     * @returns 
     */
    var fn_exec_procedure = async function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
        cLib.debug("################# fn_exec_procedure >> 프로시저 Start");

        let Version = parsedParams.fbParams["[Version].[Version Name]"];

        cLib.debug("fn_exec_procedure >> ### Version : "+Version);
        
        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 1 : ex) Exec Procedure PR_UI_SOPAdjustLCM {"Version" : "{{Version}}"};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_UI_SOPAdjustLCM", `exec procedure PR_UI_SOPAdjustLCM ${JSON.stringify({ Version })} ;`);

        //##############   테스트 
        // let Location = ["P306"]; 
        // await fn_execution("PR_UI_BomAlloc_Test", `exec procedure PR_UI_BomAlloc_Test ${JSON.stringify({ Version, Location })} ;`);

        cLib.debug("################# fn_exec_procedure >> 프로시저 End");

    };

    var fn_execution = async function(prName, makeSql){  // 리턴 테스트 03.05 테스트
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printStep("#### fn_execution : Proc Name >> "+prName);

            var execQuery = makeSql;
            
            const res = await queryModule.update(execQuery);

            cLib.debug("############## fn_execution > #### Return >> prName : "+prName +" >>> isOkResult(res): "+isOkResult(res));

            if(!isOkResult(res)){
                throw {
                    procName: prName,
                    errorMsg: `[error 01] ${prName} :: failed`
                };
            }

            return res;

        } catch (e) {
            var msg = (e && e.errorMsg) ? e.errorMsg : String(e);
            throw {
                procName: prName,
                errorMsg: `[error 02] ${msg}`
            };
        }
    };

    function toObjIfJsonString(x){
        if (typeof x !== "string") return x;
        try { return JSON.parse(x); } catch (e) {return x;}
    }

    function isOkResult(res) {
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        cLib.debug("##########res >>>>>>>>>>>>>>>>> "+res);

        if( !res ) return false;    // undefined, null 체크

        if (res === true) return true;
        var r = toObjIfJsonString(res);
        
        if( !r || typeof r !== "object") return false;

        if (typeof r.Result === "undefined") return false;

        if (r && typeof r === "object" && r.Result === true) return true;

        // 어떤 환경은 "true" 문자열로 줄 수도 있어서 방어
        if (res === "true") return true;

        return String(r.Result).toLowerCase() === "true";
    }


    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_toItem"    : fn_cb_toItem
       ,"fn_cb_itemComponent" : fn_cb_itemComponent
       ,"fn_cb_itemMaterial"  : fn_cb_itemMaterial
       ,"fn_save"           : fn_save
       ,"fn_apply"          : fn_apply
       ,"fn_SOPAdjustLCM"   : fn_SOPAdjustLCM
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 프로그램명 : o9.NSCM.JSEWLCMSOPAdjustMFG
   화면명 : LCM SOP Adjust MFG (EW)
   Action Button : EWSOPAdjustmentLCMMFG
   [history]
   2025.09.16 | syif1380.lee | 생성
   2025.10.02 | syif1380.lee | col -> row 데이터 변환, fn_validation 수정
   2025.11.17 | syif1380.lee | fn_setUpdateByInfo() 추가 : 주차별 생성일자,생성자,수정일자,수정자 추가 로직 (한승진p요청)
   2026.01.26 | syif1380.lee | fn_validation() : rowstatus = C/U 일 경우만 로직 수행하도록 함
   2026.01.26 | syif1380.lee | fn_getChgReason() : Chg Reason Validation 체크 추가
   2026.03.18 | syif1380.lee | fn_SOPAdjustLCM() : 프로시저 호출 추가 (한승진P요청)
   2026.03.26 | commonLib 선언 부분 변경 및 공통함수 이름 변경
   2026.04.09 | syif1380.lee | add, update : fn_create , fn_update(fn_updateCommon) 수정 : Add or update 된 데이터를 대상으로만 처리될 수 있게 하고자 Flag를 추가하고자 함 (추가 2026.04.09 한승진p)
                                - 저장시 Measure.[SOP Adjust LCM W_Apply Flag] = "N" 업데이트 메저 추가
*/
/*--------------------------------------------------------------------------------------------------*/