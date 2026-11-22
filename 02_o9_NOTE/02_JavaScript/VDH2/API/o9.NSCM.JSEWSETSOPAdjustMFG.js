define('o9.NSCM.JSEWSETSOPAdjustMFG', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLibVD'], function(){

    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWSETSOPAdjustMFG
    // 화면명 : SET SOP Adjust MFG (EW)
    // Action Button : EWSOPAdjustmentSETMFG
    // EW 개발자 : SET SOP Adjust. (MFG W) (col) : 김동수p
    // EW 개발자 : SET SOP Adjust. (MFG W) (row) : 김성희p
    // 최초생성 : 2025.06.20 / syif1380.lee
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

    const programName = "o9.NSCM.JSEWSETSOPAdjustMFG";
    const MPHorizon = "&MPHorizon";
    const MEAS_KEYS = ["adjQty","chgQty","reason","changedFlag"];   // changedFlag 11.17 추가
    const strSplit = "^";
    const queryModule = require('o9/data/query');

    //================================================== -[Combo Data] ==========================================//
    /*------------------------------------------------------------------------------------------------------------
    From Site           > EWCommonVD           >  { "fbFuncName" : "fn_cb_siteMF", "fbParams" : {} }
    To Site             > EWCommonVD           >  { "fbFuncName" : "fn_cb_siteDC", "fbParams" : {} }
    TPMode Group        > EWCommonVD           >  { "fbFuncName" : "fn_cb_tpmodeGO", "fbParams" : {} }
    Item                > EWSOPAdjustmentSETMFG>  { "fbFuncName" : "fn_cb_item", "fbParams" : { "[Location].[Location]" : "P306", "[To Location].[To Location]" : "S851", "[Trans Mode].[Trans Mode]" : "VESSEL", "ItemStd4" : ["TV_QLED_QLED_QLED","TV_OLED_OLED_OLED"]  } }
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

    /**
     * item 콤보
     * Actiion Button : EWSOPAdjustmentSETMFG
     * {"fbFuncName":"fn_cb_item","fbParams":{"[Location].[Location]":"P82A","filters":{"[Location].[Site Group1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp1LCMView","DimensionAliasName":"<MF>"},"[Location].[Site Group2]":{"SelectedMembers":["MF_NORTH_AMERICA"],"SelectedMembersAlias":["NORTH_AMERICA"],"MemberFilter":"&NSUISiteGrp2LCMView","DimensionAliasName":"<MF>"},"[Location].[Site Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISiteGrp4LCMView","DimensionAliasName":"<MF>"},"[Item].[Item Std1]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUIItemStd1LCMView","DimensionAliasName":"<LCM>"},"[Item].[Item Std2]":{"SelectedMembers":["LCD_TV","LCD_MONITOR"],"SelectedMembersAlias":["TV","MONITOR"],"MemberFilter":"&NSUIItemStd2LCMView","DimensionAliasName":"<LCM>"},"[Sub Location].[Sub Location Group3]":{"SelectedMembers":["MF_NORTH_AMERICA_SAMEX","MF_EUROPE_SEH"],"SelectedMembersAlias":["SAMEX","SEH"],"MemberFilter":"&NSUISubSiteGrp3SETView.unionwith(&NSUISubSiteGrp3KDView)","DimensionAliasName":"< MF >"},"[Sub Location].[Sub Location Group4]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISubSiteGrp4SETView.unionwith(&NSUISubSiteGrp4KDView)","DimensionAliasName":"< MF >"},"[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202547"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"}}}}
     * 
     * @param {*} parsedParams 
     * @returns 
     */
    var fn_cb_item = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            cLib.debug("parsedParams.fbParams :: "+JSON.stringify(parsedParams.fbParams));

            cLib.debug("fn_cb_item ====================> 시작");
            let fbLocation      = parsedParams.fbParams["[Location].[Location]"];
            let fbSubLocation   = parsedParams.fbParams["[To Location].[To Location]"];
            let fbTPMode        = parsedParams.fbParams["[Trans Mode].[Trans Mode]"];

            // let fbViewItemStd1   = cUtil.fn_getString(parsedParams.fbParams["[Item].[Item Std1]"]);
            // let fbViewItemStd2   = cUtil.fn_getString(parsedParams.fbParams["[Item].[Item Std2]"]);
            // let fbViewItemStd3   = cUtil.fn_getString(parsedParams.fbParams["[Item].[Item Std3]"]);
            // let fbViewItemStd4   = cUtil.fn_getString(parsedParams.fbParams["[Item].[Item Std4]"]);
            // var where = 'where {'
            //                 +' &CWVUI'
            //                 +', [Location].[Location]'+ cUtil.fn_filterStr(fbLocation)
            //                 +', [Sub Location].[Sub Location]'+ cUtil.fn_filterStr(fbSubLocation)
            //                 +', [Trans Mode].[Trans Mode]'+ cUtil.fn_filterStr(fbTPMode)
            //                 +', &NSUIItemStd1View'+ cUtil.fn_filterStr(fbViewItemStd1)
            //                 +', &NSUIItemStd2View'+ cUtil.fn_filterStr(fbViewItemStd2)
            //                 +', &NSUIItemStd3View'+ cUtil.fn_filterStr(fbViewItemStd3)
            //                 +', &NSUIItemStd4View'+ cUtil.fn_filterStr(fbViewItemStd4)
            //                 +', coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() '
            //                 +', coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() '
            //                 +', Measure.[BOD Item_Asn] == 1 '
            //                 +'} .filter(isnull(Measure.[SOP Adjust SET_Min LOT Qty]) && isnull(Measure.[SOP Adjust SET_Multiple LOT Qty])) ';
            // cLib.debug("Where >> "+where);

            //-----------------------------------------2025.12.29 filter 적용
            let conditions = [];
            conditions.push("&CWVUI");
            conditions.push("[Location].[Location]"+ cUtil.fn_filterStr(fbLocation));
            conditions.push("[Sub Location].[Sub Location]"+ cUtil.fn_filterStr(fbSubLocation));
            conditions.push("[Trans Mode].[Trans Mode]"+ cUtil.fn_filterStr(fbTPMode));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Item].[Item Std1]"));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Item].[Item Std2]"));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Item].[Item Std3]"));
            conditions.push(cUtil.fn_getFilterQuery(parsedParams,"[Item].[Item Std4]"));
            conditions.push('coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now()');
            conditions.push('coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now() ');
            conditions.push('Measure.[BOD Item_Asn] == 1 ');
            // conditions.push('Measure.[BOD Item_Asn] == 1 } .filter(isnull(Measure.[SOP Adjust SET_Min LOT Qty]) && isnull(Measure.[SOP Adjust SET_Multiple LOT Qty])) ');

            cLib.debug(" fn_cb_item >> conditions : "+JSON.stringify(conditions));

            let where = conditions.length ? `where { ${conditions.join(',')} }.filter(isnull(Measure.[SOP Adjust SET_Min LOT Qty]) && isnull(Measure.[SOP Adjust SET_Multiple LOT Qty])) ` : '' ;
            //-----------------------------------------
                        
            // BOD Item 에 있고 SOP Adjust 에 없는것.. Adjust에 등록할꺼니까..02.18 문지윤p
            // 다른 그레인은 동일하고, 
            // BOD Item 의 Sub Location 과 SOP Adjust SET 의 To Location 이 그레인이 달라도 member 가 동일하므로 join 됨.
            var result = cLib.selectList(["&SETItem"],
                                             ["Measure.[BOD Item_Asn]"
                                             ,"Measure.[BOD Item_Cur Status]"
                                             ,"Measure.[BOD Item_BOD LT]"],    // measure
                                             where,
                                              "",
                                              "");
            cLib.printCsData(result, 3);

            var comboList = cLib.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName", existAll : false, isDisplayNameWithCode : false});
            cLib.debug("ComboData : " + JSON.stringify(comboList));

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        } catch ( e ) {
            // RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_chk_bodValid = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("params :: "+JSON.stringify(params));

            let fbLocation      = params["[Location].[Location]"];
            let fbSubLocation   = params["[To Location].[To Location]"];
            let fbTPMode        = params["[Trans Mode].[Trans Mode]"];
            let fbItem          = params["[Item].[Item]"];
            let fbWeek          = params["[Time].[Week]"];
            let fbWeekMonday    = params["weekMonday"];
            
            // BOD Item 의 Startdate/Enddate 가져오기
            let dimChek = ["&CWVUI"
                        ,"[Location].[Location].[" + fbLocation + "]"
                        ,"[Sub Location].[Sub Location].[" + fbSubLocation + "]"
                        ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                        ,"[Item].[Item].[" + fbItem + "]"];
                        // '202505' // date
            let rtnValue = cLib.selectList(dimChek
                                , ["Measure.[BOD Item_Eff Startdate]", "Measure.[BOD Item_Eff Enddate]", "Measure.[BOD Item_Cur Status]"]
                                , "where { Measure.[BOD Item_Asn] == 1 }", "", "");
            
            cLib.printCsData(rtnValue, 1);

            let bodStartDate = "", bodEndDate = "";
            if( rtnValue.cs.rowCount > 0){
                bodStartDate = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("BOD Item_Eff Startdate"));
                bodEndDate = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("BOD Item_Eff Enddate"));
                bodItemFlag = "true";
            }
            cLib.debug("fbWeekMonday :: "+fbWeekMonday);
            cLib.debug("bodStartDate :: "+bodStartDate);
            cLib.debug("bodEndDate :: "+bodEndDate);

            let sDate = bodStartDate ? new Date(bodStartDate.substring(0,10)) : null;
            let eDate = bodEndDate ? new Date(bodEndDate.substring(0,10)) : null;
            let valueDate = fbWeekMonday ? new Date(fbWeekMonday) : null;

            cLib.debug("sDate :: "+sDate);
            cLib.debug("eDate :: "+eDate);
            cLib.debug("valueDate :: "+valueDate);
            
            if( isNaN(valueDate)) return false;  // 잘못된 날짜일 경우

            let resultBodItem = { flag : true};
            if( rtnValue.cs.rowCount == 0){  // 해당 Item 이 없을 경우
                resultBodItem = { flag : false};  // false : error 리턴
            }
            cLib.debug("#### resultBodItem :: "+JSON.stringify(resultBodItem));

            // return true >> error
            let resultEffValid = { flag : true};
            if( sDate && eDate ){
                if( !(valueDate >= sDate && valueDate <= eDate) ){
                    resultEffValid = { flag : false};
                };
            } else if ( sDate && !eDate ){
                if( !(valueDate >= sDate) ){
                    resultEffValid = { flag : false};
                };
            } else if ( !sDate && eDate ){
                if( !(valueDate <= eDate) ){
                    resultEffValid = { flag : false};
                };
            }else{
                resultEffValid = { flag : true};
            }

            cLib.debug("#### resultEffValid :: "+JSON.stringify(resultEffValid));

            return {resultBodItem, resultEffValid};
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // BOM Eff
    var fn_chk_bom = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("###### fn_chk_bom >> params :: "+JSON.stringify(params));

            let fbVersion       = params["[Version].[Version Name]"];
            let fbLocation      = params["[Location].[Location]"];
            let fbItem          = params["[Item].[Item]"];
            let fbWeek          = params["[Time].[Week]"];

            let dimChek = ["&CWVUI"
                          ,"[Location].[Location].[" + fbLocation + "]"
                          ,"[Item].[Item].[" + fbItem + "]"];

            let rtnValue = cLib.selectList(dimChek
                                            , ["Measure.[SOP Adjust SET Sub_BOM Eff End]", "Measure.[SOP Adjust SET Sub_BOM Eff Start]"
                                            , "Measure.[SOP Adjust SET Sub_BOM Issue]", "Measure.[SOP Adjust SET Sub_BOM Status]"
                                            , "Measure.[SOP Adjust SET Sub_EOP]", "Measure.[SOP Adjust SET Sub_SRA]"
                                            , "Measure.[SOP Adjust SET Sub_Panel Block End]", "Measure.[SOP Adjust SET Sub_Panel Block Start]"]
                                            , "", "", "");
            cLib.printCsData(rtnValue, 1);

            let bomEffEnd = "", bomEffStart = "", bomIssue = "", bomStatus = "", sEOP = "", sSRA = "", panelBlockEnd = "", panelBlockStart = "";

            let resultSRA = { flag : true};
            let resultEOP = { flag : true};
            let resultSetBlock = {flag : true};
            let resultBomEff = { flag : true};
            let resultBomProd = { flag : true, status : bomStatus};
            let resultBomTemp = { flag : true};

            if( rtnValue.cs.rowCount > 0){
                bomEffEnd = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_BOM Eff End"));      // "202520"
                bomEffStart = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_BOM Eff Start"));  // "202520"
                bomIssue = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_BOM Issue"));         // "202520"
                bomStatus = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_BOM Status"));       // "PROD" , "TEMP"
                sEOP = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_EOP"));                   // "202520"
                sSRA = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_SRA"));                   // "202520"
                panelBlockEnd = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_Panel Block End"));      // "202520"
                panelBlockStart = rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET Sub_Panel Block Start"));  // "202520"
            }else{
                // row == 0 이면 오류처리
                resultSRA = { flag : false};
                resultEOP = { flag : false};
                resultSetBlock = {flag : false};
                resultBomEff = { flag : false};
                resultBomProd = { flag : false, status : bomStatus};
                resultBomTemp = { flag : false};
                return {resultSRA, resultEOP, resultSetBlock, resultBomEff, resultBomProd, resultBomTemp};
            }
            cLib.debug("bomEffEnd :: "+bomEffEnd);
            cLib.debug("bomEffStart :: "+bomEffStart);
            cLib.debug("bomStatus :: "+bomStatus);
            cLib.debug("bomIssue :: "+bomIssue);
            
            cLib.debug("sSRA :: "+sSRA);            // 202505
            cLib.debug("sEOP :: "+sEOP);            // 202530
            cLib.debug("fbWeek :: "+fbWeek);        // 202508

            // PLC Week Problem (SRA) : "Week" < "SRA" => false(오류)
            if ( sSRA && (parseInt(fbWeek) < parseInt(sSRA)) ){
                resultSRA = { flag : false};
            }

            cLib.debug("#### resultSRA :: "+JSON.stringify(resultSRA));

            // PLC Week Problem (EOP) : "Week" > "EOP" => false(오류)
            if ( sEOP && (parseInt(fbWeek) > parseInt(sEOP)) ){
                resultEOP = { flag : false};
            }
            cLib.debug("#### resultEOP :: "+JSON.stringify(resultEOP));

            //========================== [SET Block] 로직 재정의 중 ..  2025.10.01 (한승진p)
            // SET Block : "Week" <= "Plan Start Week"  + 10W &&  (수정시점) =================>  수정시점 now() 의 주차를 가져오는 방법은?
            // currentWeek = cLib.selectResult("&CurrentWeek.element(0).Leadoffset(10).Name");
            // if( parseInt(fbWeek) <= parseInt(currentWeek) && bomIssue == null ){
            //     resultSetBlock = { flag : false};
            // }

            //========================== [BOM Eff] 로직 재정의 중 ..  2025.10.01 (한승진p)
            // BOM Eff : "Week" between nvl("start",-1) and nvl("end",999)
            // let iBomEffStart = (bomEffStart == null || bomEffStart === "") ? -1 : parseInt(bomEffStart);
            // let iBomEffEnd = (bomEffEnd == null || bomEffEnd === "") ? 999999 : parseInt(bomEffEnd);
            // // 범위 안
            // if ( !(parseInt(fbWeek) >= iBomEffStart && parseInt(fbWeek) <= iBomEffEnd)){
            //     resultBomEff = { flag : false};
            // }

            // bomStatus == "PROD"
            // BOM Status(Prod) : "Week" < "Issue"+2W 이면 오류
            let week2 = "";
            if ( bomIssue && bomStatus == "PROD" ){    // null, undefined, "" 제외
                // week2 = cLib.selectResult("[Time].[Week].["+bomIssue+"].leadoffset(2).DisplayName");
                week2 = cLib.selectResult("[Time].[Week].["+bomIssue+"].leadoffset(2).Name");
                cLib.debug("#### bomIssue + 2w : "+ week2);
                if( week2 && (parseInt(fbWeek) < parseInt(week2)) ){
                    resultBomProd = { flag : false, status : bomStatus}; // 오류
                }
            }
            cLib.debug("#### resultBomProd :: "+JSON.stringify(resultBomProd));

            // bomStatus == "TEMP"
            // BOM Status(Temp) : "Week" < &CurrentWeek+2w and "Issue" ==null 
            // &CurrentWeek 당주 + W2
            if( bomStatus == "TEMP" ){
                let weekTmp = cLib.selectResult("&CurrentWeek.element(0).Leadoffset(2).Name");
                cLib.debug("#### TEMP : &CurrentWeek + 2w : "+ weekTmp);
                cLib.debug("#### TEMP : fbWeek : "+ fbWeek);
                cLib.debug("#### TEMP : weekTmp : "+ weekTmp);
                cLib.debug("#### TEMP : bomIssue : "+ bomIssue);
                if( weekTmp && (parseInt(fbWeek) < parseInt(weekTmp) && (bomIssue == null || bomIssue == "")) ){
                    resultBomTemp = { flag : false};    // 오류
                }
            }
            cLib.debug("#### resultBomTemp :: "+JSON.stringify(resultBomTemp));

            return {resultSRA, resultEOP, resultSetBlock, resultBomEff, resultBomProd, resultBomTemp};
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    //  배수값 체크
    var isMultiple = function(input, base){
        if( input === null || input === undefined || input === ""){
            return false;
        }

        if( base === null || base === undefined || base === "" || base === 0){
            return false;
        }

        return parseInt(input) % parseInt(base) === 0;
    };

    var fn_chk_lotSize = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("params :: "+JSON.stringify(params));

            let fbVersion       = params["[Version].[Version Name]"];
            let fbLocation      = params["[Location].[Location]"];
            let fbSubLocation   = params["[To Location].[To Location]"];
            let fbTPMode        = params["[Trans Mode].[Trans Mode]"];
            let fbItem          = params["[Item].[Item]"];
            let adjQty          = params["Measure.[SOP Adjust SET W_SOP Adj Qty]"];    // SOP Qty (Adj Qty)

            // MDP의 SOP Adjust SET (MG) 조회
            let dimChek = ["&CWVUI"
                        ,"[Location].[Location].[" + fbLocation + "]"
                        ,"[To Location].[To Location].[" + fbSubLocation + "]"
                        ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                        ,"[Item].[Item].[" + fbItem + "]"];
            let rtnValue = cLib.selectList(dimChek
                                , ["Measure.[SOP Adjust SET_Min LOT Qty]","Measure.[SOP Adjust SET_Multiple LOT Qty]"]
                                , "", "", "");
            
            cLib.printCsData(rtnValue, 1);
            
            let minLotQty = 0, multiLotQty = 0;

            if( rtnValue.cs.rowCount > 0){
                minLotQty = parseInt(rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET_Min LOT Qty")));
                multiLotQty = parseInt(rtnValue.cs.row(0).cell(rtnValue.cs.measureColumnIndex("SOP Adjust SET_Multiple LOT Qty")));
            }
            cLib.debug("minLotQty :: "+minLotQty);
            cLib.debug("multiLotQty :: "+multiLotQty);
            
            // "SOP Qty" < "Min Lot" => false(오류)
            let resultMin = {};
            if( adjQty < minLotQty){
                resultMin = { flag : false, minQty : minLotQty, multiQty : multiLotQty , qty: adjQty};
            }else{
                resultMin = { flag : true, minQty : minLotQty, multiQty : multiLotQty , qty: adjQty};
            }

            // "SOP Qty" - "Min Lot"은 0 or "Multiple lot" 의 배수
            cLib.debug(" =======> 배수 : "+isMultiple(adjQty, multiLotQty));

            // multiLot 계산 2025.10.01 (한승진p)
            // > "Min Lot" 이 0 또는 1일때는 "SOP Qty" = "Multiple Lot"의 배수
            // > "Min Lot" 이 2 이상일때는 "SOP Qty" = "Min Lot" + "Multiple Lot"의 배수
            // > "Min Lot"이 Null일 경우 는 1로 치환 처리
            // >> 예시: MIN  LOT = 98 , MULTIPLE LOT = 14일떄  SOP QTY =  112 ,  126 ,...이 들어갈  수 있음

            let resultMulti = {};            
            if( minLotQty === null ) minLotQty = 1;

            // "Min Lot" 이 0 또는 1일때는 "SOP Qty" = "Multiple Lot"의 배수
            if( minLotQty == 0 || minLotQty == 1){
                if ( isMultiple(adjQty, multiLotQty) ){
                    cLib.debug("####  Multiple Lot => 배수");
                    resultMulti = { flag : true, minQty : minLotQty, multiQty : multiLotQty , qty: adjQty};
                }else{
                    cLib.debug("####  Multiple Lot => 배수 아님");
                    resultMulti = { flag : false, minQty : minLotQty, multiQty : multiLotQty , qty: adjQty};
                }

            // "Min Lot" 이 2 이상일때는 "SOP Qty" = "Min Lot" + "Multiple Lot"의 배수
            // 예시: MIN  LOT = 98 , MULTIPLE LOT = 14일떄  SOP QTY =  112 ,  126 ,...이 들어갈  수 있음
            // SOP QTY 값이 ("Min Lot" + "Multiple Lot") 값 이상의 "Multiple Lot"의 배수 체크
            } else if( minLotQty >= 2 ){
                if( (adjQty >= (minLotQty + multiLotQty)) && isMultiple(adjQty, multiLotQty) ){
                    resultMulti = { flag : true, minQty : minLotQty, multiQty : multiLotQty , qty: adjQty};
                }else{
                    resultMulti = { flag : false, minQty : minLotQty, multiQty : multiLotQty , qty: adjQty};
                }
            }
            
            cLib.debug("resultMin :: "+JSON.stringify(resultMin));
            cLib.debug("resultMulti :: "+JSON.stringify(resultMulti));

            return {resultMin, resultMulti};
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 중복체크
    var fn_chk_duplicated = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("params :: "+JSON.stringify(params));

            let fbVersion       = params["[Version].[Version Name]"];
            let fbLocation      = params["[Location].[Location]"];
            let fbSubLocation   = params["[To Location].[To Location]"];
            let fbTPMode        = params["[Trans Mode].[Trans Mode]"];
            let fbItem          = params["[Item].[Item]"];
            let fbWeek          = params["[Time].[Week]"];
            
            var dimension = ["[Version].[Version Name].[" + fbVersion + "]"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[To Location].[To Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                            ,"[Item].[Item].[" + fbItem + "]"
                            ,"[Time].[Week].[" + fbWeek + "]"];

            // 중복체크
            if ( cLib.existMeasure(dimension,["Measure.[SOP Adjust SET W_Exist Flag]"], "")) {
                return false;
            }else{
                return true;
            }
            
        } catch ( e ) {
            // RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Chg Reason 없이 Qty입력 방지
    var fn_chk_changeReason = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug(" ########  fn_chk_changeReason >> params :: "+JSON.stringify(params));

            let chgReason = params["Measure.[SOP Adjust SET W_Chg Reason]"];
            let sopQty = params["Measure.[SOP Adjust SET W_SOP Qty]"];
            let chgQty = params["Measure.[SOP Adjust SET W_Chg Qty]"];

            cLib.debug("### sopQty :: " + sopQty);
            cLib.debug("### chgQty :: " + chgQty);
            cLib.debug("### chgReason :: " + chgReason);

            if ( (sopQty !== null && sopQty !== undefined) && (chgQty !== null && chgQty !== undefined) && chgReason !== undefined){
                if( parseInt(sopQty) > 0 && parseInt(chgQty) != 0 ){
                    if (chgReason === null || chgReason ===""){
                        return false;
                    }
                }
            }

            return true;
            
        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Negative SOP Qty : 음수값 체크
    var fn_chk_adjQty = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("fn_chk_adjQty======================>");
        try {
            cLib.debug("params :: "+JSON.stringify(params));
            let adjQty = params["Measure.[SOP Adjust SET W_SOP Adj Qty]"];

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
        version     : "[Version].[Version Name]"
       ,loc         : "[Location].[Location]"
       ,toloc       : "[To Location].[To Location]"
       ,tpmode      : "[Trans Mode].[Trans Mode]"
       ,item        : "[Item].[Item]"
       ,week        : "[Time].[Week]"
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

                    const rowstatus = row.rowstatus;
                    const gk        = row.groupkey;
                    const version   = row[DB_KEYS.version];
                    const loc       = row[DB_KEYS.loc];
                    const toloc     = row[DB_KEYS.toloc];
                    const tpmode    = row[DB_KEYS.tpmode];
                    const item      = row[DB_KEYS.item];

                    if (gk == null) continue;

                    // const key = [gk, loc, toloc, week].map(x => String(x || "")).join("|");
                    const key = [gk, week].map(x =>  String(x || "")).join("|");

                    let acc = bucket.get(key);
                    if( !acc) {
                        // acc = { groupkey: gk, version, loc, toloc, tpmode, item, week };
                        acc = { rowstatus, groupkey: gk, [DB_KEYS.version]:version, [DB_KEYS.loc]:loc, [DB_KEYS.toloc]:toloc, [DB_KEYS.tpmode]:tpmode, [DB_KEYS.item]:item, [DB_KEYS.week]:week };
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

    //params[i]["rowvalid"] = params[i]["rowvalid"] + strSplit + "Error";
    var fn_appendError = function(str, flagStr){
        // return (str || "") + strSplit + "Error";
        return (str || "") + strSplit + flagStr;
    }

    // col/row 모두 신규 생성 및 테스트 2025.10.02
    //====================================================================================================================================================//
    // 오류 체크 :
    // key check
    // 1.Horizon : 테스트 필요 : O
    // 2.Duplicated : 생성 : 테스트 필요 : Ok
    // 3.BOD Valid : 생성 : 테스트 필요 : O
    // 4.BOD Eff Valid : 생성 : 테스트 필요 : O
    // 5.PLC Week Problem (SRA) : MG 확인필요
    // 6.PLC Week Problem (EOP) : MG 확인필요
    // 7.SET Block  or LCM Block : MG 확인필요
    // 8.BOM Eff : MG 확인필요
    // 9.BOM Status(Prod)  : MG 확인필요 : ok (warn->error 변경 2025.11.26)
    // 10.BOM Status(Temp) : MG 확인필요 : ok (warn->error 변경 2025.11.26)
    // 11.BOM Status(?)    : MG 확인필요
    //
    // value check
    // 1.Chg Reason : 생성 : 테스트 필요 : Ok
    // 2.Negative SOP Qty : 생성 : 테스트 필요 : O
    // 3.Lot Size (Min) : 생성 : 테스트 필요 : O
    // 4.Lot Size (Multi) : 생성 : 테스트 필요 : O
    //====================================================================================================================================================//
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

                let weekVal = row["[Time].[Week]"];
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

                let {resultBodItem, resultEffValid} = fn_chk_bodValid(row);
                // 3.[key] BOD Item Valid
                if( resultBodItem && !resultBodItem.flag ) {
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("Invliad BOD Item");
                }

                 // 4.[key] BOD Eff Valid
                 if( resultEffValid && !resultEffValid.flag ) {
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("Invalid BOD Effective");
                }
                
                //---------------------------------------------------------------------------------------------------//
                // 5.[key] PLC Week Problem (SRA) 메저 변경 ( 5, 6, 8, 9,10)
                let {resultSRA, resultEOP, resultSetBlock, resultBomEff, resultBomProd, resultBomTemp} = fn_chk_bom(row);
                cLib.debug("################ resultSRA =====> :: "+JSON.stringify(resultSRA));
                if( resultSRA && !resultSRA.flag ) {
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("MFG Week is earlier than SRA DATE");
                }

                // 6.[key] PLC Week Problem (EOP)
                if( resultEOP && !resultEOP.flag ) {
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("MFG Week is later than INACTIVE DATE");
                }
                //---------------------------------------------------------------------------------------------------//
                
                //======================================= 로직 재정의 구간 2025.10.01 ================================//
                // 로직 재정의 필요 2025.10.01 (한승진p)
                // 입력 제어로 구현방식 변경(주석처리 유지) : 2026.01.21 (한승진P)
                // // 7.[key] SET Block : "Week" <= "Plan Start Week"  + 10W &&  (수정시점 -> 현재일자)
                // if( resultSetBlock && !resultSetBlock.flag){
                //     errCnt++;
                //     box[gk].rowvalid.push("Error");
                //     box[gk].rowmsg.push("SET Block");
                // }

                // 로직 재정의 필요 2025.10.01 (한승진p)
                // KD의 일부 케이스가 해당 정보로 구분 가능함. >> SRA/EOP로 기능 사용 가능하므로, 제외함 (주석처리 유지): 2026.01.21 (한승진p)
                // // 8.[key] BOM Eff : "Week" between nvl("start",-1) and nvl("end",999)
                // cLib.debug("################ resultBomEff =====> :: "+JSON.stringify(resultBomEff));
                // if( resultBomEff && !resultBomEff.flag ) {
                //     errCnt++;
                //     box[gk].rowvalid.push("Error");
                //     box[gk].rowmsg.push("Invalid BOM Effective");
                // }
                //======================================================================================================//

                // 9.[key] BOM Status(Prod) : MFG Week is earlier than '||STATUS||' BOM Date + 2W : Error
                if( resultBomProd && !resultBomProd.flag ) {
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push(`MFG Week is earlier than ${resultBomProd.status} BOM Date + 2W`);
                }

                // 10.[key] BOM Status(Temp) : Error
                if( resultBomTemp && !resultBomTemp.flag ) {
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("MFG Week is earlier than Current Date + 2W");
                }

                //============================  정의되면 추가해야될 함수 들 ===========================================//
                // 8.[key] BOM Eff, BOM Status(Prod), BOM Status(Temp), BOM Status(?)
                //======================================================================================================//
 
                // // 10.[key] BOM Status(Temp) : Warn => 미정의
                // if( !resultBomTemp && resultBomTemp.flag ) {
                //     warnCnt++;
                //     params[i]["rowmsg"] = params[i]["rowmsg"] + strSplit + "MFG Week is earlier than Current Date + 2W";
                // }

                // 11.[key] BOM Status(?) : Warn ????  미정의

                //======================================================================================================//
                
                // 1.[value] Chg Reason : Chg Reason 없이 Qty입력 방지
                if( !fn_chk_changeReason(row) ) {
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("CHG Reason을 입력하세요.");
                }

                // [Category].[Category Type].[SOP Chg Reason]
                if( row["Measure.[SOP Adjust SET W_Chg Reason]"] !== undefined && row["Measure.[SOP Adjust SET W_Chg Reason]"] !== null && row["Measure.[SOP Adjust SET W_Chg Reason]"] !== "" ){
                    if( !sopChgReasonList.includes(row["Measure.[SOP Adjust SET W_Chg Reason]"])){
                        errCnt++;
                        box[gk].rowvalid.push("Error");
                        box[gk].rowmsg.push("유효한 CHG Reason을 입력하세요.");
                    }
                }

                // 2.[value] Negative SOP Qty : Chg Qty입력시에도 체크
                if( !fn_chk_adjQty(row) ){
                    errCnt++;
                    box[gk].rowvalid.push("Error");
                    box[gk].rowmsg.push("SOP는 음수가 될 수 없습니다.");
                }

                // min, multi lot 체크 로직 점검 테스트 완료 2025.10.01 syif1380.lee
                // 3.[value] Lot Size (Min) : "SOP Qty" < "Min Lot" >> Warn 메세지 후 저장은 가능
                let {resultMin, resultMulti} = fn_chk_lotSize(row);
                if( !resultMin.flag){
                    warnCnt++;
                    box[gk].rowvalid.push("Warn");
                    box[gk].rowmsg.push(`Min: ${resultMin.minQty} , 입력값: ${resultMin.qty}`);
                    // params[i]["rowmsg"] = params[i]["rowmsg"] + strSplit + "Min:"+resultMin.minQty+", 입력값:"+resultMin.qty;
                }else{
                    //---------------------------------------------------------------------------------------------------------------------------------------//
                    // ** Min Lot Validation에 해당(SOP Qty < Min Lot) 될 경우, Multi Lot에 대한 Validation은 수행하지 않아도 됨. (2025.12.22 한승진p 요청)
                    // ** min lot 오류시 multi lot 체크하지 않음.
                    //---------------------------------------------------------------------------------------------------------------------------------------//
                    // 4.[value] Lot Size (Multi) : "SOP Qty" - "Min Lot"은 0 or "Multiple lot" 의 배수 >> Warn 메세지 후 저장은 가능
                    if( !resultMulti.flag ){
                        warnCnt++;
                        box[gk].rowvalid.push("Warn");
                        box[gk].rowmsg.push(`Min: ${resultMulti.minQty} , Multi: ${resultMulti.multiQty}, 입력값: ${resultMulti.qty}`);
                        // params[i]["rowmsg"] = params[i]["rowmsg"] + strSplit + "Min:"+resultMulti.minQty+ ", Multi:"+resultMulti.multiQty+", 입력값:"+resultMulti.qty;
                    }
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

    // MFG (Col/Row) 같은 함수 호출 - 저장시 fn_save 로 통합 예정 2025.09.05
    // parsedParams.fbGridRows :: [{"rowstatus":"U","groupkey":"0,0,0,0,0","[Version].[Version Name]":"202508_P","[Location].[Location]":"P306","[To Location].[To Location]":"S321","[Trans Mode].[Trans Mode]":"TRUCK","[Item].[Item]":"HG43AU800NFXZA","measure":"SOP QTY","Measure.[SOP Adjust SET W_SOP Adj Qty]":["202508^1","202509^2","202510^3"],"Measure.[SOP Adjust SET W_Chg Qty]":[],"Measure.[SOP Adjust SET W_Chg Reason]":[]},{"rowstatus":"U","groupkey":"0,0,0,0,0","[Version].[Version Name]":"202508_P","[Location].[Location]":"P306","[To Location].[To Location]":"S321","[Trans Mode].[Trans Mode]":"TRUCK","[Item].[Item]":"HG43AU800NFXZA","measure":"CHG QTY","Measure.[SOP Adjust SET W_Chg Qty]":["202508^50","202510^70"]},{"rowstatus":"U","groupkey":"0,0,0,0,0","[Version].[Version Name]":"202508_P","[Location].[Location]":"P306","[To Location].[To Location]":"S321","[Trans Mode].[Trans Mode]":"TRUCK","[Item].[Item]":"HG43AU800NFXZA","measure":"Chg Reason","Measure.[SOP Adjust SET W_Chg Reason]":["202508^test05","202509^test06","202510^test07"]}]
    var fn_save = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let validationResult = {};
            let GridRow = {};

            let paramsOrg = parsedParams.fbGridRows;
            let gridType = parsedParams.fbParams["gridType"];  // row / col

            let validCheck = parsedParams.fbParams["validCheck"]; // Y / N
            if( validCheck === null || validCheck === undefined){
                validCheck = "N";
            }

            if( gridType == "row"){
                GridRow = paramsOrg;
            } else if( gridType == "col"){
                GridRow = fn_colToRowData(paramsOrg);  // 전체 : Col => Row 로 변환 (validation Check 위함)
                cLib.debug("####  :: row 변환 Data >>>>>>>>>>>>>>>>>>>>>>"+ JSON.stringify(GridRow));
            }

            cLib.debug("#### validCheck : "+validCheck);

            //=========================================================================================================================
            //############################## VDH2 테스트 임시 주석처리 - 현업테스트 요청으로 validation 주석처리 함 (2026.02.11 한승진p요청)
            // if( validCheck == "N"){
            //     validationResult = fn_validation(GridRow);    // validation Check // 신규 버전으로 테스트 후 전환 처리

            //     cLib.debug("#### validation 하기 위한 포맷 :: validationResult :: "+ JSON.stringify(validationResult));
            //     cLib.debug("######## error : "+(validationResult.errCnt + validationResult.warnCnt));

            //     if ( (validationResult.errCnt + validationResult.warnCnt) > 0 ){
            //         // validation 오류 : Code : 1
            //         return { "Code" : 1, "Msg" : "valid", "ErrorCount":validationResult.errCnt, "WarnCount":validationResult.warnCnt, "Rows" : validationResult.Rows};  // 오류 dataset Return
            //     }
            // }
            //=========================================================================================================================

            // validation 성공시 저장
            for ( var i=0; i<GridRow.length; i++){
                let rowstatus = GridRow[i]["rowstatus"];

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

            fn_savePostProcess(parsedParams);   // PY 호출 실행

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Insert 로직 신규테스트 2025.09.05 - 이걸로 통합 예정
    var fn_create = function(row){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("params :: "+JSON.stringify(row));

            // Measure
            let adjQty = row["Measure.[SOP Adjust SET W_SOP Adj Qty]"];    // SOP Qty (Adj Qty)
            let chgQty = row["Measure.[SOP Adjust SET W_Chg Qty]"];        // CHQ Qty
            let chgReason = row["Measure.[SOP Adjust SET W_Chg Reason]"];  // CHQ Reason
            
            row["rowmsg"] = null;

            let dimension = [];
            dimension.push(cUtil.fn_qDim(row, "[Version].[Version Name]"));
            dimension.push(cUtil.fn_qDim(row, "[Location].[Location]"));
            dimension.push(cUtil.fn_qDim(row, "[To Location].[To Location]"));
            dimension.push(cUtil.fn_qDim(row, "[Trans Mode].[Trans Mode]"));
            dimension.push(cUtil.fn_qDim(row, "[Item].[Item]"));

            let measure = [];
            measure.push(cUtil.fn_qMeaInt(row, "Measure.[SOP Adjust SET W_SOP Adj Qty]", row["Measure.[SOP Adjust SET W_SOP Adj Qty]"]));
            measure.push(cUtil.fn_qMeaInt(row, "Measure.[SOP Adjust SET W_Chg Qty]", row["Measure.[SOP Adjust SET W_Chg Qty]"]));
            measure.push(cUtil.fn_qMeaStr(row, "Measure.[SOP Adjust SET W_Chg Reason]", row["Measure.[SOP Adjust SET W_Chg Reason]"]));
            measure.push(cUtil.fn_qMeaInt(null, "Measure.[SOP Adjust SET W_Lock Flag]", 0));
            measure.push(cUtil.fn_qMeaInt(null, "Measure.[SOP Adjust SET W_JIT]", 0));
            measure.push(cUtil.fn_qMeaInt(null, "Measure.[SOP Adjust SET W_SS]", 0));
            measure.push(cUtil.fn_qMeaInt(null, "Measure.[SOP Adjust SET W_BLD]", 0));
            measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust SET W_Created By]"));
            measure.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust SET W_Create Time]"));
            measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust SET W_Updated By]"));
            measure.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust SET W_Update Time]"));
            measure.push("Measure.[SOP Adjust SET W_Exist Flag] = 1;");
            // measure.push("Measure.[SOP Adjust SET W_Del Flag] = 0;");

            // 중복체크
            if ( !cLib.existMeasure(dimension, ["Measure.[SOP Adjust SET_Min LOT Qty]","Measure.[SOP Adjust SET_Multiple LOT Qty]"], "")) {
                // SOP Adjustment SET 생성
                cLib.createMeasure(dimension
                                    ,['Measure.[SOP Adjust SET_Min LOT Qty]     = 0;'    // default data 정의 필요
                                    ,'Measure.[SOP Adjust SET_Multiple LOT Qty] = 0;']);
            }
            
            var dimensionW = [...dimension];    // dimension 을 복사후 추가 (Main MG의 Grain 에서 추가되는 경우 활용)
            dimensionW.push(cUtil.fn_qDim(row, "[Time].[Week]"));

            // SOP Adjustment SET W 생성
            // 주차별 생성일자, 생성자 추가, 한승진P요청 (2025.11.17)
            if ( !cLib.existMeasure(dimensionW, ["Measure.[SOP Adjust SET W_Exist Flag]"], "")) {
                cLib.createMeasure(dimensionW, ["Measure.[SOP Adjust SET W_Exist Flag] = 1;"]);
                cLib.updateMeasure(dimensionW, measure);
            }else{
                cLib.updateMeasure(dimensionW, measure);
            }

            cLib.programEnd();

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // update 로직 신규 2025.09.05 이걸로 통합 예정
    var fn_update = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("params :: "+JSON.stringify(params));

            let fbVersion       = params["[Version].[Version Name]"];
            let fbLocation      = params["[Location].[Location]"];
            let fbSubLocation   = params["[To Location].[To Location]"];
            let fbTPMode        = params["[Trans Mode].[Trans Mode]"];
            let fbItem          = params["[Item].[Item]"];
            let fbWeek          = params["[Time].[Week]"];

            // Measure
            let adjQty = params["Measure.[SOP Adjust SET W_SOP Adj Qty]"];    // SOP Qty (Adj Qty)
            let chgQty = params["Measure.[SOP Adjust SET W_Chg Qty]"];        // CHQ Qty
            let chgReason = params["Measure.[SOP Adjust SET W_Chg Reason]"];  // CHQ Reason
            let changedFlag = params["Measure.[changedFlag]"];                // ChangedFlag , 주차별 변경 여부 추가 - 한승진p요청(2025.11.17)
            
            params["rowmsg"] = null;

            var dimension = ["[Version].[Version Name].[" + fbVersion + "]"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[To Location].[To Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                            ,"[Item].[Item].[" + fbItem + "]"
                            ,"[Time].[Week].[" + fbWeek + "]"
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

            cLib.debug("##### fn_updateRow >>>>> measure > " + JSON.stringify(measure));

            fn_updateCommon(dimension, measure);

            cLib.programEnd();

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // 삭제 로직 2025.09.05 신규
    var fn_delete = function(params){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");
        cLib.debug("######################################  fn_delete >> ");
        try {
            cLib.debug("parsedParams :: "+JSON.stringify(params));

            let fbVersion       = params["[Version].[Version Name]"];
            let fbLocation      = params["[Location].[Location]"];
            let fbSubLocation   = params["[To Location].[To Location]"];
            let fbTPMode        = params["[Trans Mode].[Trans Mode]"];
            let fbItem          = params["[Item].[Item]"];
            let fbWeek          = params["[Time].[Week]"];

            params["rowmsg"] = null;

            var dimension = ["[Version].[Version Name].[" + fbVersion + "]"
                            ,"[Location].[Location].[" + fbLocation + "]"
                            ,"[To Location].[To Location].[" + fbSubLocation + "]"
                            ,"[Trans Mode].[Trans Mode].[" + fbTPMode + "]"
                            ,"[Item].[Item].[" + fbItem + "]"
                            ,"[Time].[Week].[" + fbWeek + "]"];
            
            cLib.debug("############# fn_delete >> dimension :: "+JSON.stringify(dimension));

            // col 화면에서 삭제되어 주차 editable 안돼는 것은 ew 에서 가능하도록 변경 , 기존 delete로 원복 2026.02.06
            cLib.deleteMeasure(dimension, "SOP Adjustment SET W");

            // Grain Delete에서 : 입력셀 = null , flag = delete 2026.01.27 변경
            // let measure = [];
            // measure.push("Measure.[SOP Adjust SET W_SOP Adj Qty] = null;");
            // measure.push("Measure.[SOP Adjust SET W_Chg Qty] = null;");
            // measure.push("Measure.[SOP Adjust SET W_Chg Reason] = null;");
            // // measure.push("Measure.[SOP Adjust SET W_Del Flag] = 1;");   // 삭제 flag
            // measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust SET W_Updated By]"));
            // measure.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust SET W_Update Time]"));
            // cLib.updateMeasure(dimension, measure);

            cLib.programEnd();

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // row/col Update 공통 처리 2025.09.03 테스트
    // measure {}
    // fn_updateCommon(dimensionW, row.measure);
    // measure => {"chgQty":50,"reason":"test05"}
    var fn_updateCommon = function(dimension, measure){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            // let measureCheck = ["Measure.[SOP Adjust SET W_SOP Adj Qty]", "Measure.[SOP Adjust SET W_Chg Qty]", "Measure.[SOP Adjust SET W_Chg Reason]", "Measure.[SOP Adjust SET W_SOP Qty]"];

            let measureStr = [];
            if( measure.hasOwnProperty(MEAS_KEYS[0])){
                measureStr.push('Measure.[SOP Adjust SET W_SOP Adj Qty] = ' + measure[MEAS_KEYS[0]] + ';');
            }

            if( measure.hasOwnProperty(MEAS_KEYS[1])){
                measureStr.push('Measure.[SOP Adjust SET W_Chg Qty] = ' + measure[MEAS_KEYS[1]] + ';');
            }

            if( measure.hasOwnProperty(MEAS_KEYS[2])){
                measureStr.push('Measure.[SOP Adjust SET W_Chg Reason] = "' + measure[MEAS_KEYS[2]] + '";');
            }

            // 중복이 없으면 생성
            if( measureStr.length > 0){
                if ( !cLib.existMeasure(dimension, ["Measure.[SOP Adjust SET W_Exist Flag]", "Measure.[SOP Adjust SET W_SOP Qty]"], "")){
                    fn_setUpdateByInfo("C", measure, measureStr);
                    cLib.createMeasure(dimension, measureStr);
                }else{
                    fn_setUpdateByInfo("U", measure, measureStr);
                    cLib.updateMeasure(dimension, measureStr);
                }
            }

            cLib.programEnd();

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
                        measureStr.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust SET W_Created By]"));
                        measureStr.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust SET W_Create Time]"));
                    } else if ( updateFlag == "U" ){
                        measureStr.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjust SET W_Updated By]"));
                        measureStr.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjust SET W_Update Time]"));
                    }
                }
            }

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // PY_UI_BODLoadingInfoApply 호출 함수 
    var fn_savePostProcess = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            // cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));
            cLib.debug(" PY 호출 ======================>PY_UI_BODLoadingInfoApply");

            // scope 추가 &SETMFLocation , &SETItem : 2025.12.04
            let fbLocation = [...new Set(parsedParams.fbGridRows.map(row => row["[Location].[Location]"]))];
            let fbItem = [...new Set(parsedParams.fbGridRows.map(row => row["[Item].[Item]"]))];

            // var execQuery = 'EXEC plugin instance [PY_UI_BODLoadingInfoApply] for Measures {[BOD Item_Min Lot Qty]} '
            //                 +'using scope (&MPV) '
            //                 +'using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )}; ';

            /* PY 호출 (PY_UI_BODLoadingInfoApply) 권태우B */
            // scope 추가 &SETMFLocation , &SETItem : 2025.12.04
            var execQuery = 'EXEC plugin instance [PY_UI_BODLoadingInfoApply] for Measures {[BOD Item_Min Lot Qty]} '
                            +' using scope ( '
                            +' &MPV'
                            +' * &SETMFLocation' + cUtil.fn_filterStr(fbLocation)
                            +' * &SETItem' + cUtil.fn_filterStr(fbItem)
                            +' ) '
                            +'using arguments {(ExecutionMode, "MediumWeight"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_savePostProcess : PY_UI_BODLoadingInfoApply Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // PY_UI_SOPAdjustSET 호출 함수 , 선택row 로 실행할지, 전체 실행할지 결정 필요........... 2025.06.26 syif1380.lee
    var fn_apply = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));
            // cLib.debug("parsedParams.fbGridRows :: "+JSON.stringify(parsedParams.fbGridRows));
            cLib.debug(" PY 호출 ======================>PY_UI_SOPAdjustSET");
            
            /* PY 호출 (PY_UI_SOPAdjustSET) 권태우B */
            var execQuery = 'EXEC plugin instance [PY_UI_SOPAdjustSET] ' +
                            'for measures {[SOP W_SET MFG Qty]} ' +
                            'using scope ( &CWVUI )' +
                            'using arguments {(ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")}; ';      // 2025.02.04 수정(권태우B 요청)

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_apply : PY_UI_SOPAdjustSET Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    var fn_bomAllocSave = async function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        //-------------------------------------------------------------------------------------//
        // 1) 시작 상태 무조건 기록 : Confirm Udate
        //-------------------------------------------------------------------------------------//
        try {
            cLib.debug("#### fn_bomAllocSave 시작");
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            await fn_confirmUpdate(parsedParams, {confirm:"Y", status:"-", msg:""});

            cLib.debug("#### fn_bomAllocSave >> 1");
        } catch ( e ) {
            // 시작 로그조차 실패하면 저장 자체를 막음. 아래 프로시저 실행 안하고 리턴
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }

        //-------------------------------------------------------------------------------------//
        // 2) 프로시저 실행 및 Confirm Udate (실행 결과에 대한 내용)
        //-------------------------------------------------------------------------------------//
        try {
            // 2) 프로시저 실행(순차, 실패 시 즉시 stop)
            await fn_exec_procedure(parsedParams);

            // 3) 전체 성공
            await fn_confirmUpdate(parsedParams, {confirm:"N", status:"Success", msg:""});

            cLib.programEnd();
            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {

            cLib.debug("###################### 프로시저 실패 리턴 : ["+ e.procName + "] "+ e.errorMsg);

            const procName = (e && e.procName) ? e.procName : "unknown";
            
            // 4) 프로시저 첫 실패에서 여기로 옴
            await fn_confirmUpdate(parsedParams, {confirm:"N", status:"Error", msg:procName});

            cLib.error(e.errorMsg);
            return { "Code" : -1, "Msg" : e.errorMsg };
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
        let Location = [...new Set(parsedParams.fbGridRows.map(row => row["[Location].[Location]"]))];

        cLib.debug("fn_exec_procedure >> ### Version : "+Version);

        let SourceKey = cLib.selectResult("[Version].[Version Name].["+Version+"].Key");  // select [Version].[Version Name].[CWV_MP].Key;
        let current_week = cLib.selectResult("&CurrentWeek.element(0).Name");  // select (&CurrentWeek.element(0) );
        let first_week = cLib.selectResult("&PlanningHorizon.first.Name");  // select (&CurrentWeek.element(0) );
        let last_week = cLib.selectResult("&PlanningHorizon.last.Name");  // select (&CurrentWeek.element(0) );

        cLib.debug("fn_exec_procedure >> ### SourceKey : "+SourceKey);
        cLib.debug("fn_exec_procedure >> ### current_week : "+current_week);
        cLib.debug("fn_exec_procedure >> ### first_week : "+first_week);
        cLib.debug("fn_exec_procedure >> ### last_week : "+last_week);

        let WSolverCurrentBucket = String(current_week);
        let WSolverStartingBucket = String(first_week);
        let WSolverEndingBucket = String(last_week);

        // ///============================================ Test중 ==========================================================//
        // // 프로시저에 변수 넘기는 테스트...
        // var sql_test = `exec procedure PR_UI_BomAlloc_Test ${JSON.stringify({ Version, Location })} ;`;
        // cLib.debug("fn_exec_procedure > Step TEST : "+sql_test);
        // //cLib.executeQuery("###########Test >>> PR_UI_BomAlloc_Test", sql_test);

        // let resutl = { flag : true, msg: ""};
        // resutl = fn_execution("test01", "PR_UI_BomAlloc_Test", sql_test);
        // if( !resutl ){
        //     return { "Code" : -1, "Msg" : resutl.msg, "Rows" : ""  };
        // }
        // //===============================================================================================================//

        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 1-1 : Deleting past scenario => deleteversion("{{Version}}(_SOPAdjustment)");
        //------------------------------------------------------------------------------------------------------------------------------------//
        cLib.printStep("[1-1] deleteversion");
        queryModule.update(`deleteversion("${Version}(_SOPAdjustment)");`);

        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 1-2 : Creating a archived version of most recent SOPAdjustment => createscenario({{SourceKey}} ,"{{Version}}(_SOPAdjustment)");
        //------------------------------------------------------------------------------------------------------------------------------------//
        cLib.printStep("[1-2] createscenario");
        queryModule.update(`createscenario(${SourceKey},"${Version}(_SOPAdjustment)");`);
                    
        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 1-3 : updatemember
        // updatemember(Version.[Version Name]={,"{{Version}}(_SOPAdjustment)"}, Version.[Version Expiry Date]={dateadd(Now(),1,"week"),});
        //------------------------------------------------------------------------------------------------------------------------------------//
        cLib.printStep("[1-3] updatemember");
        queryModule.update(`updatemember(Version.[Version Name]={,"${Version}(_SOPAdjustment)"}, Version.[Version Expiry Date]={dateadd(Now(),1,"week"),});`);
        
        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 2 : Pre Processing Rules : ex) Exec Procedure PR_DIM_Activity1_BOD {"Version" : "{{Version}}"};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_DIM_Activity1_BOD", `exec procedure PR_DIM_Activity1_BOD ${JSON.stringify({ Version })} ;`);    // 정상 Test 2026.03.06
        // await fn_execution("PR_DIM_Activity1_BOD", `exec procedure PR_DIM_Activity1_BOD ${JSON.stringify({ "Version2":Version })} ;`);    // 오류 Test 2026.03.06
        
        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 3 : Pre Processing Rules : ex) exec procedure PR_UI_SOPAdjust_Update_BODBOM {"Version":"{{Version}}"};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_UI_SOPAdjust_Update_BODBOM", `exec procedure PR_UI_SOPAdjust_Update_BODBOM ${JSON.stringify({ Version })} ;`);
        
        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 4 : Pre Processing Rules : ex) exec procedure PR_UI_SOPAdjust_SupplyPlan_AllocPur {"Version":"{{Version}}"};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_UI_SOPAdjust_SupplyPlan_AllocPur", `exec procedure PR_UI_SOPAdjust_SupplyPlan_AllocPur ${JSON.stringify({ Version })} ;`);
        
        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 5-2 : Pre Processing Rules : ex) exec procedure PR_UI_SOPAdjust_CreateSOPWIP {"Version":"{{Version}}", "Location": [{{#csv Version}}]};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_UI_SOPAdjust_CreateSOPWIP", `exec procedure PR_UI_SOPAdjust_CreateSOPWIP ${JSON.stringify({ Version, Location })} ;`);

        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 6 : Pre Processing Rules : ex) exec procedure PR_UI_InitializeBeforeSOPAdj {"Version":"{{Version}}", "Location": [{{#csv Location}}]};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_UI_InitializeBeforeSOPAdj", `exec procedure PR_UI_InitializeBeforeSOPAdj ${JSON.stringify({ Version, Location })} ;`);

        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 7 : Pre Processing Rules : ex) exec procedure PR_UI_InitBUPInput {"Version":"{{Version}}" , "WSolverCurrentBucket" : "{{WSolverCurrentBucket}}" ,"WSolverStartingBucket" : "{{WSolverStartingBucket}}" , "WSolverEndingBucket" : "{{WSolverEndingBucket}}", "Location": [{{#csv Version}}]};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_UI_InitBUPInput", `Exec procedure PR_UI_InitBUPInput ${JSON.stringify({ Version, WSolverCurrentBucket, WSolverStartingBucket, WSolverEndingBucket, Location })} ;`);

        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 8: Pre Processing Rules : ex) exec Procedure PR_UI_RunSCSSOPAdj {"Version" : "{{Version}}" , "WSolverCurrentBucket" : "{{WSolverCurrentBucket}}" ,"WSolverStartingBucket" : "{{WSolverStartingBucket}}" , "WSolverEndingBucket" : "{{WSolverEndingBucket}}"};
        //------------------------------------------------------------------------------------------------------------------------------------//
        await fn_execution("PR_UI_RunSCSSOPAdj", `exec procedure PR_UI_RunSCSSOPAdj ${JSON.stringify({ Version, WSolverCurrentBucket, WSolverStartingBucket, WSolverEndingBucket })} ;`);

        //------------------------------------------------------------------------------------------------------------------------------------//
        // Step 9 : Pre Processing Rules : ex) exec procedure PR_UI_SOPAdjust_UpdateSOP {"Version":"{{Version}}"}; // 2026.03.05 추가(한승진p)
        //------------------------------------------------------------------------------------------------------------------------------------//
        //============> 프로시저 오류남...
        await fn_execution("PR_UI_SOPAdjust_UpdateSOP", `exec procedure PR_UI_SOPAdjust_UpdateSOP ${JSON.stringify({ Version })} ;`);

        // await fn_execution("PR_UI_SOPAdjust_UpdateSOP", `exec procedure PR_UI_SOPAdjust_UpdateSOP ${JSON.stringify({ "Version2":Version })} ;`);    // 오류 테스트
        cLib.debug("################# fn_exec_procedure >> 프로시저 End");

    };

    var fn_execution = async function(prName, makeSql){  // 리턴 테스트 03.05 테스트
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.printStep("#### fn_execution : Proc Name >> "+prName);

            var execQuery = makeSql;
            
            const res = await queryModule.update(execQuery);    // 리턴 테스트 03.05 테스트

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

    var fn_confirmUpdate = async function(parsedParams, opt){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("fn_confirmUpdate ---------------> Start");
            // cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            let Location = [...new Set(parsedParams.fbGridRows.map(row => row["[Location].[Location]"]))];

            let dimension = [];
            dimension.push(cUtil.fn_qDimVersionName(parsedParams));
            dimension.push("[Location].[Location]"+cUtil.fn_filterStr(Location));

            let measure = [];
            measure.push(cUtil.fn_qMeaStr(null, "Measure.[SOP Adjustment SET BOM Alloc_Status]", opt.status));    // string
            measure.push(cUtil.fn_qMeaStr(null, "Measure.[SOP Adjustment SET BOM Alloc_Confirm YN]", opt.confirm));    // string
            measure.push(cUtil.fn_qMeaStr(null, "Measure.[SOP Adjustment SET BOM Alloc_MSG]", opt.msg));    // string
            measure.push(cUtil.fn_qMeaUpdateTime("Measure.[SOP Adjustment SET BOM Alloc_Update Time]"));
            measure.push(cUtil.fn_qMeaUpdateUserName("Measure.[SOP Adjustment SET BOM Alloc_Updated By]"));

            cLib.updateMeasure(dimension, measure);

            cLib.programEnd();
            cLib.debug("fn_confirmUpdate ---------------> End");

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /**
     * PY_UI_SOPAdjustSETSub 호출
     * Filter 의 버전 (Multi) 으로 scope 호출 (한승진p요청 2026.03.30)
     *
     * {"fbFuncName":"fn_reloaddata"
     * ,"fbParams":{"filters":{"[Version].[Version Name]":{"SelectedMembers":["202507_M","CWV_MP"],"SelectedMembersAlias":["202507_M","202547"],"MemberFilter":"&CWVUI.unionwith(&ReportVersion)","DimensionAliasName":"Plan ID"}}
     * }}
     *
     * @param parsedParams
     * @returns {{Code: number, Msg: *}}
     */
    var fn_reloaddata = function(parsedParams){
        const cLib = fn_cLib(programName + "." + arguments.callee.name);
        cLib.setLogLevel("Debug");

        try {
            cLib.debug("parsedParams :: "+JSON.stringify(parsedParams));

            cLib.debug("version :: Test -------------------------->");
            cLib.debug("version :: "+ cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]"));

            cLib.debug(" fn_reloaddata >> PY 호출 =======>PY_UI_SOPAdjustSETSub");

            /* PY 호출 (PY_UI_SOPAdjustSETSub) 양희영B */
            var execQuery = 'EXEC plugin instance [PY_UI_SOPAdjustSETSub] ' +
                            'for measures {[SOP Adjust SET Sub_SRA]} ' +
                            // 'using scope ( &CWVUI )' +
                            'using scope ( '+ cUtil.fn_getFilterQuery(parsedParams, "[Version].[Version Name]") +') ' +      // filter 의 버전(Multi) 넘기기
                            'using arguments {("IncludeNullRows", "False"), (ExecutionMode, "MediumWeight"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 )}; ';

            cLib.debug("execQuery: " + JSON.stringify(execQuery));
            cLib.executeQuery("fn_reloaddata : PY_UI_SOPAdjustSETSub Run", execQuery);

            cLib.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            cLib.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_item" : fn_cb_item
       ,"fn_save" : fn_save                         // 화면에서 save시 호출 (validation 포함)
       ,"fn_apply" : fn_apply                       // Apply
       ,"fn_bomAllocSave" : fn_bomAllocSave         // Bom Alloc.
       ,"fn_reloaddata" : fn_reloaddata
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});

/*--------------------------------------------------------------------------------------------------*/
/* 프로그램명 : o9.NSCM.JSEWSETSOPAdjustMFG
    화면명 : SET SOP Adjust (Col/Row) (EW)
    Action Button : EWSOPAdjustmentSETMFG
    Action Button : EWSOPAdjustmentSETMFGBomAlloc : (Bom Alloc.) : API 수행 후 IBPL 호출(Procedure 수행)
    [history]
    2025.06.20 | syif1380.lee | 생성
    2025.06.24 | syif1380.lee | 저장 기능 함수 : fn_save, fn_saveCall, fn_add, fn_delete, fn_update
    2025.06.25 | syif1380.lee | validation 기능 함수 : fn_chk_duplicated, fn_chk_bodValid, fn_chk_changeReason, fn_chk_adjQty, fn_chk_lotSize
    2025.06.30 | syif1380.lee | fn_savePostProcess 추가 (PY호출)
    2025.09.01 | syif1380.lee | fn_updateCol Week Col Type 으로 형태변경 저장 로직 테스트 완료
    2025.09.03 | syif1380.lee | fn_updateRow Week Col Type 으로 형태변경 저장 로직 테스트 완료
    2025.09.05 | syif1380.lee | fn_test , MFG (Col/Row) 저장 통합 테스트, fn_createRow, fn_updateRow, fn_deleteRow 사용 예정( 월요일 테스트 후 )
    2025.09.16 | syif1380.lee | fn_save, fn_create, fn_update, fn_delete 로 소스 통합
                                | fn_apply() 추가
    2025.09.26 | syif1380.lee | fn_save 시 fn_validation 로직 변경, 화면에서 validCheck == "Y" 는 validation 체크로직 수행하지 않고 Data 저장
    2025.10.02 | syif1380.lee | col -> row 데이터 변환, fn_validation 수정
    2025.10.21 | syif1380.lee | resultBomProd, resultBomTemp 수정 
    2025.11.17 | syif1380.lee | fn_setUpdateByInfo() 추가 : 주차별 생성일자,생성자,수정일자,수정자 추가 로직 (한승진p요청)
    2025.11.26 | syif1380.lee | fn_validation 변경 : BOM Status(Prod), BOM Status(Temp) > warn -> error 로 변경 (한승진p요청)
    2025.12.04 | syif1380.lee | PY_UI_BODLoadingInfoApply 는 Loading Master (UI) 저장시 사용함, 
                                #########  이 화면에서 PY_UI_BODLoadingInfoApply 를 사용하는 이유를 모르겠음 ##########
                                - 기능 : (input) Loading Master To Site 의  Loading Master To Site_Minimum Lot, Loading Master To Site_Multiple Lot
                                            =>
                                            (output) BOD Item 의 BOD Item_Min Lot Qty, BOD Item_Multi Lot Qty 입력
    2025.12.22 | syif1380.lee | Min Lot Validation에 해당(SOP Qty < Min Lot) 될 경우, Multi Lot에 대한 Validation은 수행하지 않아도 됨. 
                                (min lot 오류시 multi lot 체크하지 않음.) (2025.12.22 한승진p 요청)
    2025.12.29 : 콤보에 filter 적용
    2026.01.22 | syif1380.lee | fn_bomAllocSave() 추가 (Bom Alloc. Action Button 추가) - Action Button > EWSOPAdjustmentSETMFGBomAlloc 
    2026.01.26 | syif1380.lee | fn_validation() : rowstatus = C/U 일 경우만 로직 수행하도록 함
    2026.01.26 | syif1380.lee | fn_getChgReason() : Chg Reason Validation 체크 추가
    2026.01.28 | syif1380.lee | add > Measure.[SOP Adjust SET W_Exist Flag] =1 , delete > Measure.[SOP Adjust SET W_Del Flag] = 1 추가
    2026.02.06 | syif1380.lee | delete > W 주차 전체 삭제로 원복 함 (deleteMeasure)
    2026.02.24 | syif1380.lee | fn_bomAllocSave 저장 및 프로시저 호출 정의
    2026.02.27 | syif1380.lee | fn_exec_procedure() 수정, fn_execution() : 프로시저 통합 호출로직 추가
    2026.03.05 | syif1380.lee | fn_exec_procedure() 수정, PR_UI_RunSCSSOPAdj 변수에 Location 삭제 (한승진p 요청)
                                - PR_UI_SOPAdjust_UpdateSOP 추가 
                                - 프로시저 리턴 (오류/성공) 에 따른 confirm 업데이트 로직 추가 : fn_confirmUpdate()
    2026.03.10 | syif1380.lee | VDH2 validation 체크 주석처리 중...(한승진P요청)
    2026.03.12 | syif1380.lee | PR_UI_InitBUPInput  ->  PR_UI_RunSCSSOPAdj 순으로 진행되도록 변경(한승진P요청)
    2026.03.24 | syif1380.lee | fn_reloaddata 생성 - PY_UI_SOPAdjustSETSub 호출 (한승진P요청)
    2026.03.26 | syif1380.lee | commonLib 선언 부분 변경 및 공통함수 이름 변경
    2026.03.30 | syif1380.lee | fn_reloaddata() : Filter 의 멀티 버전으로 scope (한승진p요청)
*/
/*--------------------------------------------------------------------------------------------------*/