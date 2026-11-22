define('o9.NSCM.JSEWPOProposal', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSEWPOProposal";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWProposal
    // Action Button : EWPOProposal
    // 화면명 : PO Proposal
    // 2025.11.10 최초 생성
    // 2026.03.23 fn_sel_incoterms2() 추가
    // 2026.03.24 fn_sel_incoterms1() 추가
    // 2026.03.31 CurrentWorking 사용 삭제함.
    // 2026.04.14 fn_reload() Reload 버튼은 선택값을 고려하지 않고 전체 데이터 대상으로 수행하도록 수정
    // 2026.04.14 fn_send() Status을 상태를 "SEND" => "REQ" 로 처리함.
    /*--------------------------------------------------------------------------------------------------*/    
	var fn_loadFunction = function(o9Params){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            let returnData = {};
            let obj = this;

            vdCommon.printParams(o9Params);

            // 파라메타 가져오기
            var parsedParams = JSON.parse(o9Params);
            var fbFuncName = parsedParams.fbFuncName;

            if ( functionMap[fbFuncName] == undefined ) {
                return { "Code" : 1, "Msg" : "No Function" };
            }

            if ( parsedParams["fbParams"] == undefined ) {
                parsedParams["fbParams"] = {};
            }
            if ( parsedParams.fbParams["includeField"] == undefined ) {
                parsedParams.fbParams["includeField"] = "";
            }
            // 조회시 기본 limit 지정( 3000개 )
            if ( parsedParams.fbParams["limit"] == undefined ) {
                parsedParams.fbParams["limit"] = "limit 3000";
            } else if ( parsedParams.fbParams["limit"] == -1 ) {
                parsedParams.fbParams["limit"] = "";
            } else {
                parsedParams.fbParams["limit"] = "limit " + parsedParams.fbParams.limit;
            }
            // 콤보에 All 추가
            if ( parsedParams.fbParams["existAll"] == undefined ) {
                parsedParams.fbParams["existAll"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    var fn_newSequence= function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");        
        try {
            let version = parsedParams[0]["version"];
            let timeWeek = parsedParams[0]["[Time].[Week]"];
            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";
            let orderbyQuery = "orderby [Sequence].[Sequence].Key desc";
            let limitQuery = "limit 1";
            let newSequence = "1";

            dimensionQuery.push("[Version].[Version Name].["+version+"]");
            dimensionQuery.push("[Location].[Location]");
            dimensionQuery.push("[Time].[Week].["+timeWeek+"]");
            dimensionQuery.push("[Sequence].[Sequence]");
            dimensionQuery.push("[Item Material].[Item Material]");
            dimensionQuery.push("[Sub Location].[Sub Location]");
            dimensionQuery.push("[Trans Mode].[Trans Mode]");
            
            measureQuery.push("Measure.[Panel PO Proposal_POP ID]");
            
            let result = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, orderbyQuery, limitQuery);

            if(result.cs.rowCount > 0 ){
               let sequence = result.cs.row(0).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name;
               newSequence = parseInt(sequence) + 1 ;
            }

            return newSequence;

        }catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }

    var fn_newPopId = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");        
        try {
            let version = parsedParams[0]["version"];;
            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";
            let orderbyQuery = "orderby Measure.[Panel PO Proposal_POP ID] desc";
            let limitQuery = "limit 1";
            let newPopId = "";

            dimensionQuery.push("[Version].[Version Name].["+version+"]");
            dimensionQuery.push("[Location].[Location]");
            dimensionQuery.push("[Time].[Week]");
            dimensionQuery.push("[Sequence].[Sequence]");
            dimensionQuery.push("[Item Material].[Item Material]");
            dimensionQuery.push("[Sub Location].[Sub Location]");
            dimensionQuery.push("[Trans Mode].[Trans Mode]");
            
            measureQuery.push("Measure.[Panel PO Proposal_POP ID]");
            
            let result = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, orderbyQuery, limitQuery);

            if(result.cs.rowCount > 0 ){
               let popId = vdCommon.getMeasureValue(result.cs, 0, "Panel PO Proposal_POP ID")
               newPopId = parseInt(popId) + 1 ;
            }else{
                newPopId = "2026022400000000"; //TEST
            }

            return newPopId;

        }catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }   

    /* ********************************************************************************** */
    /*
     { "fbFuncName" : "fn_cb_popReason", "fbParams":{"existAll":false, "existBlank":true}}
    */
     var fn_cb_popReason = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {

            let comboCodes = [];
            comboCodes.push("Normal (SOP)");
            comboCodes.push("New Multi BOM Panel");
            comboCodes.push("Supply in Advance");
            comboCodes.push("SOP Change");
            comboCodes.push("CTN");
            comboCodes.push("Others");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : comboCodes, 
                                                    ComboValues : comboCodes,
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    }   

    /* ********************************************************************************** */
    /*{"fbFuncName" : "fn_cb_erpVendor", 
     "fbParams":{
        "filters":{
        "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["CWV_MP"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
        "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
        },        
        "where" : {
            "[Location].[Location]" : "P306", 
            "[Item Material].[Item Material]" : "BN96-54530B", 
            "[Sub Location].[Sub Location]":"G3294027"
        }
     }}*/
    var fn_cb_erpVendor = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            let comboList = [];
            let result = fn_selectData(parsedParams);
            let rtnErpVendor = "";
            let rtnINCOTERMS1 = "";
            let rtnINCOTERMS2 = "";

            if(result.cs.rowCount > 0){
                rtnErpVendor = vdUtil.fn_getMeaValue(result, 0, "Panel PO Proposal_ERP Vendor");
                rtnINCOTERMS1 = vdUtil.fn_getMeaValue(result, 0, "Panel PO Proposal_Incoterms1");
                rtnINCOTERMS2 = vdUtil.fn_getMeaValue(result, 0, "Panel PO Proposal_Incoterms2");
            }
 
            comboList.push({"ERPVENDOR":rtnErpVendor,"INCOTERMS1":rtnINCOTERMS1, "INCOTERMS2":rtnINCOTERMS2});
           
            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /*
     { "fbFuncName" : "fn_cb_incoterms1", "fbParams":{"existAll":false, "existBlank":true}}*/
     var fn_cb_incoterms1 = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {

            let comboCodes = [];
            comboCodes.push("FOB");
            comboCodes.push("CIF");
            comboCodes.push("FCA");
            comboCodes.push("0ND");
            comboCodes.push("DAP");
            comboCodes.push("CIP");
            comboCodes.push("EXW");
            comboCodes.push("DDU");
            comboCodes.push("DDP");
            comboCodes.push("DEF");
            comboCodes.push("4PF");
            comboCodes.push("CPT");

            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : comboCodes, 
                                                    ComboValues : comboCodes,
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank});
            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    /*{"fbFuncName" : "fn_sel_incoterms1", 
     "fbParams":{
        "filters":{
        "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["CWV_MP"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
        "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
        },        
        "where" : {
            "[Location].[Location]" : "P306", 
            "[Item Material].[Item Material]" : "BN96-54530B", 
            "[Sub Location].[Sub Location]":"G3294027",
            "ERP_VENDOR":"DYYC"
        }
     }}*/
     var fn_sel_incoterms1 = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            let comboList = [];
            let rtnIncoterms1 = "";
            let paramsLocation = parsedParams.fbParams.where["[Location].[Location]"];
            let paramsItemMaterial = parsedParams.fbParams.where["[Item Material].[Item Material]"];
            let paramsSubLocation = parsedParams.fbParams.where["[Sub Location].[Sub Location]"];
            let paramsERPVendor = parsedParams.fbParams.where["ERP_VENDOR"];

            //let result = fn_selectData(parsedParams);
            let productGrpResult = vdCommon.selectQueryList("Product Group", "Select ([Item Material].[S09] * [Item Material].[Item Material].["+paramsItemMaterial+"]) on row, () on column;");
            if (productGrpResult.rowCount > 0) {
                let productGrp = productGrpResult.cs.row(0).cell(productGrpResult.cs.memberColumnIndex("Item Material", "S09")).Name;
                let result = vdCommon.selectList(["&CWVUI","[Location].[Location].["+paramsSubLocation+"]", 
                                                        "[Sub Location].[Sub Location].["+paramsLocation+"]",
                                                        "[Vendor].[Vendor].["+paramsERPVendor+"]",
                                                        "[Product].[Product Group].["+productGrp+"]"], 
                                                        ["Measure.[Purchasing Proposal Vendor_INCO1]"], "", "", "limit 1");
                if(result.cs.rowCount > 0){
                    rtnIncoterms1 = result.cs.row(0).cell(result.cs.measureColumnIndex("Purchasing Proposal Vendor_INCO1"));
                }
            }

            comboList.push({"INCOTERMS1":rtnIncoterms1});            
           
            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    }    

    /*{"fbFuncName" : "fn_cb_incoterms2", 
     "fbParams":{
        "filters":{
        "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["CWV_MP"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
        "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
        },        
        "where" : {
            "[Location].[Location]" : "P306", 
            "[Item Material].[Item Material]" : "BN96-54530B", 
            "[Sub Location].[Sub Location]":"G3294027",
            "ERP_VENDOR":"DYYC",
            "INCOTERMS1":"FOB"

        }
     }}*/
     var fn_cb_incoterms2 = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            let comboList = [];
            let result = fn_selectData(parsedParams);
            let rtnIncoterms2 = "";

            if(result.cs.rowCount > 0){
                rtnIncoterms2 = vdUtil.fn_getMeaValue(result, 0, "Panel PO Proposal_Incoterms2");
            }
 
            comboList.push({"INCOTERMS2":rtnIncoterms2});            
           
            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };    

    var fn_selectData = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {

            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";
            let orderbyQuery = "";
            let limitQuery = "";
            let fbWhere = parsedParams.fbParams["where"];
            /*
                1. ERP Vendor 조회
                과거 6개월 내 동일 Item * GT Code * To Site 를 갖고 Status = "PO_CREATE" 인 항목들 중 가장 큰 POPID를 갖는 데이터의 ERP Vendor를 복사
                (* 참조할 값 없으면 null로 입력)

                2. Inco2 조회
                과거 6개월 내 동일 Item * GT Code * To Site * ERP Vendor * Inco.1 를 갖고 Status = "PO_CREATE" 인 항목들 중 가장 큰 POPID 를 갖는 데이터의 Inco.2 를 복사
                (* 참조할 값 없으면 null로 입력)
            */
            measureQuery.push('Measure.[Panel PO Proposal_POP ID]');
            measureQuery.push('Measure.[Panel PO Proposal_ERP Vendor]');
            measureQuery.push('Measure.[Panel PO Proposal_Incoterms1]');
            measureQuery.push('Measure.[Panel PO Proposal_Incoterms2]');

            if(fbWhere != undefined){
                for (let key in fbWhere) {
                    if (key == "ERP_VENDOR") {
                        whereQuery += ',Measure.[Panel PO Proposal_ERP Vendor] == "'+fbWhere[key]+'"';
                    }else if(key == "INCOTERMS1" ){
                        whereQuery += ',Measure.[Panel PO Proposal_Incoterms1] == "'+fbWhere[key]+'"';
                    }else if(key == "INCOTERMS2"){
                        whereQuery += ',Measure.[Panel PO Proposal_Incoterms2] == "'+fbWhere[key]+'"';
                    }else{
                        dimensionQuery.push(key + vdUtil.fn_filterStr(fbWhere[key]));
                    }
                }
            }

            let where = 'Where{ [Version].[Version Name].['+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+']';
            where += ', [Time].[Planning Month].filter(#.Key < &CurrentMonth.element(0).LeadOffset(1).Key && #.Key > &CurrentMonth.element(0).LeadOffset(-6).Key)'; // 6개월 조건
            where += ', Measure.[Panel PO Proposal_POP Status] == "PO_CREATE"';
            where += whereQuery ;
            where += '}';

            orderbyQuery = "Orderby Measure.[Panel PO Proposal_POP ID] desc";
            limitQuery = "limit 1";

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, where, orderbyQuery, limitQuery);

            return selectResult;


        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }

    }

    /* ********************************************************************************** */
    /*  1. Current Week
        2. ETD Week, ETA Week 
        3. Save 시점 POPID, SEQ 데이타 저장시 처리함.        
    */
    /*{ "fbFuncName" : "fn_addInfo", 
    "fbParams":{
        "filters":{
        "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["CWV_MP"],"MemberFilter":"&CWV","DimensionAliasName":"Plan ID"},
        "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
        },
        "where":{"[Item Material].[Item Material]":"BN96-54530B",
                "[Location].[Location]":"P306", 
                "[Sub Location].[Sub Location]":"G3294027", 
                "[Trans Mode].[Trans Mode]":"VESSEL"
                }
            }
    }
    */
    var fn_addInfo =  function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            let comboList = [];
            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";
            let orderbyQuery = "";
            let limitQuery = "limit 1";
            let paramsLocation = parsedParams.fbParams.where["[Location].[Location]"];
            let paramsItemMaterial = parsedParams.fbParams.where["[Item Material].[Item Material]"];
            let paramsSubLocation = parsedParams.fbParams.where["[Sub Location].[Sub Location]"];
            let paramsTransMode = parsedParams.fbParams.where["[Trans Mode].[Trans Mode]"];

            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Current Week 조회
            dimensionQuery = [];
            measureQuery = [];
            whereQuery = "";
            orderbyQuery = "";

            dimensionQuery.push("&CurrentWeek");
            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, orderbyQuery, limitQuery);
            let currentWeek = "-"
            if(selectResult.cs.rowCount > 0){
                currentWeek = selectResult.cs.row(0).cell(selectResult.cs.memberColumnIndex("Time", "Week")).Name;
            }
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            /* ETD Week, ETA Week 처리 */
            //1. LT 조회함. 당주 기준
            dimensionQuery = [];
            //dimensionQuery.push("[Version].[Version Name].["+vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")+"]");
            dimensionQuery.push("[Version].[Version Name].[CWV_MP]");
            //당주
            dimensionQuery.push("&CurrentWeek");
            dimensionQuery.push("[Item Material].[Item Material].["+paramsItemMaterial+"]");
            dimensionQuery.push("[Location].[Location].["+paramsSubLocation+"]");
            dimensionQuery.push("[Sub Location].[Sub Location].["+paramsLocation+"]"); 
            dimensionQuery.push("[Trans Mode].[Trans Mode].["+paramsTransMode+"]");

            measureQuery.push("Measure.[BOD Item Mtrl W_Intransit LT]");

            selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, orderbyQuery, limitQuery);
            let etaLT = 0
            if(selectResult.cs.rowCount > 0){
                etaLT = selectResult.cs.row(0).cell(selectResult.cs.measureColumnIndex("BOD Item Mtrl W_Intransit LT"));
                etaLT = parseInt(etaLT) / 7;
            }
            //2. ETD Week(신규 제안 주차) = 당주 + POP Week - 1
            //   ETA Week = ETD Week + LT 주차를 조회함
            dimensionQuery = [];
            measureQuery = [];
            whereQuery = "";
            orderbyQuery = "Orderby [Time].[Week].Key";

            //POP WEEK 값 조회
            // Product Group 조회함.
            let POP_WEEK = 3 ;
            let productGrpResult = vdCommon.selectQueryList("Product Group", "Select ([Item Material].[S09] * [Item Material].[Item Material].["+paramsItemMaterial+"]) on row, () on column;");
            if (productGrpResult.rowCount > 0) {
                let productGrp = productGrpResult.cs.row(0).cell(productGrpResult.cs.memberColumnIndex("Item Material", "S09")).Name;
                let popWeekResult = vdCommon.selectList(["&CWVUI","[Location].[Location].["+paramsSubLocation+"]", 
                                                        "[Item].[Class Category]",
                                                        "[Trans Mode].[Trans Mode].["+paramsTransMode+"]",
                                                        "[Sub Location].[Sub Location].["+paramsLocation+"]",
                                                        "[Vendor].[Vendor]",
                                                        "[Product].[Product Group].["+productGrp+"]"], 
                                                        ["Measure.[Purchasing Proposal Master_POP Week]"], "", "", "");
                if(popWeekResult.cs.rowCount > 0){
                    POP_WEEK = popWeekResult.cs.row(0).cell(popWeekResult.cs.measureColumnIndex("Purchasing Proposal Master_POP Week"));
                }
            }
            //당주 + POP Week(3) - 1
            let offsetWeek = POP_WEEK - 1 ;            
            vdCommon.debug("POPWEEK["+POP_WEEK+"]["+offsetWeek+"]");
            let etdWeek = "-";
            let etaWeek = "-";

            dimensionQuery.push("[Time].[Week].Filter(#.Key == &CurrentWeek.element(0).LeadOffset("+offsetWeek+").Key || #.Key == &CurrentWeek.element(0).LeadOffset("+(parseInt(offsetWeek) + parseInt(etaLT)) +").Key)");
            selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, orderbyQuery, "");
     
            if(selectResult.cs.rowCount == 1){
                etdWeek = selectResult.cs.row(0).cell(selectResult.cs.memberColumnIndex("Time", "Week")).Name;
                etaWeek = etdWeek;
            }else if(selectResult.cs.rowCount == 2){
                etdWeek = selectResult.cs.row(0).cell(selectResult.cs.memberColumnIndex("Time", "Week")).Name;
                etaWeek = selectResult.cs.row(1).cell(selectResult.cs.memberColumnIndex("Time", "Week")).Name;
            }

            comboList.push({"CurrentWeek":currentWeek, "ETDWeek":etdWeek, "ETAWeek":etaWeek});            
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    /* ********************************************************************************** */
    /* { "fbFuncName" : "fn_save"}
     { "fbFuncName" : "fn_save",
      "fbParams":{
        "filters":{
            "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["CWV_MP"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
            "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
        }
      },
      "fbGridRows" : [
        {
        "rowstatus":"C", "rowindex":2,
        "[Version].[Version Name]" : "CWV_MP",
        "[Location].[Location]" : "P551LCD",
        "[Time].[Week]":"202508",
        "[Sequence].[Sequence]":"2",        
        "[Item Material].[Item Material]":"BN96-54530B",
        "[Sub Location].[Sub Location]": "P105",
        "[Trans Mode].[Trans Mode]": "VESSEL",
        "Measure.[Panel PO Proposal_POP ID]" : "",
        "Measure.[Panel PO Proposal_ETD Week]" : "202509",
        "Measure.[Panel PO Proposal_ETA Week]" : "202511",
        "Measure.[Panel PO Proposal_POP Reason]" : "",
        "Measure.[Panel PO Proposal_POP Reason Detail]" : "TEST",
        "Measure.[Panel PO Proposal_POP Status]" : "INI",
        "Measure.[Panel PO Proposal_ERP Vendor]" : "C100-AK",
        "Measure.[Panel PO Proposal_Incoterms1]" : "CIF",
        "Measure.[Panel PO Proposal_Incoterms2]" : "ORIGIN",
        "Measure.[Panel PO Proposal_ETD QTY]" : "12000",
        "Measure.[Panel PO Proposal_Open PO QTY]" :"2000" ,
        "Measure.[Panel PO Proposal_Calc QTY]" : "10000",
        "Measure.[Panel PO Proposal_Confirm POP QTY]" : "800"
        }
      ]
     }*/
     
    var fn_dataCheck = function(rowInfo, measurename){
        let value = rowInfo[measurename] ;
        if(value != undefined && value != null){
            return measurename +' = "'+value+'";';
        }else{
            return measurename + '= null ;'
        } 
    };
    
    var fn_save = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {

            let dimension = [];
            let measure = [];
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");

            let dimensionQuery = [];
            let measureQuery = [];
            
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                dimensionQuery = [];
                measureQuery = [] ;

                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let rows =  parsedParams.fbGridRows[i];

                /*for(var d = 0; d < dimension.length; d++){
                    let dimValue = parsedParams.fbGridRows[i][dimension[d]];
                    vdCommon.debug("["+dimension[d]+"]["+dimValue+"]");
                    dimensionQuery.push(dimension[d]+'.['+dimValue+']');
                } */               
                dimensionQuery.push("[Version].[Version Name].["+fbVersion+"]");
                dimensionQuery.push("[Location].[Location].["+rows["[Location].[Location]"]+"]");
                dimensionQuery.push("[Time].[Week].["+rows["[Time].[Week]"]+"]");
                dimensionQuery.push("[Item Material].[Item Material].["+rows["[Item Material].[Item Material]"]+"]");
                dimensionQuery.push("[Sub Location].[Sub Location].["+rows["[Sub Location].[Sub Location]"]+"]");
                dimensionQuery.push("[Trans Mode].[Trans Mode].["+rows["[Trans Mode].[Trans Mode]"]+"]");
                                
                /*for(var m = 0; m < measure.length; m++){
                    let measureValue = parsedParams.fbGridRows[i][measure[m]];
                    vdCommon.debug("["+measure[m]+"]["+measureValue+"]");
                    if(measureValue != undefined && measureValue != null && measureValue != ""){
                        measureQuery.push(measure[m]+' = "'+measureValue+'";');
                    }                    
                }*/
                measureQuery.push(fn_dataCheck(rows, "Measure.[Panel PO Proposal_ETD Week]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_ETA Week]"));
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_POP Reason]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_POP Reason Detail]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_POP Status]"));
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_ERP Vendor]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_Incoterms1]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_Incoterms2]"));
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_Price]"));            
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_Currency]"));
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_ETD QTY]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_Open PO QTY]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_Calc QTY]"));
                measureQuery.push(fn_dataCheck(rows,"Measure.[Panel PO Proposal_Confirm POP QTY]"));  


                if(rowStatus == "C"){ 
                    //New Seq, New POP ID 생성
                    let checkData = [{"version" : fbVersion, 
                                    "[Time].[Week]": rows["[Time].[Week]"]}]
                    //dimensionQuery.push('[Time].[Week].['+parsedParams.fbGridRows[i]["[Time].[Week]"]+']');
                    dimensionQuery.push('[Sequence].[Sequence].['+fn_newSequence(checkData)+']');
                    measureQuery.push('Measure.[Panel PO Proposal_POP ID] = "'+fn_newPopId(checkData) +'";');
                }

                measureQuery.push("Measure.[Panel PO Proposal_Update Time] = Now() ;");
                measureQuery.push("Measure.[Panel PO Proposal_Updated By] = CurrentUser().[User Name];");

                if(rowStatus == "C"){                    
                    vdCommon.createMeasure(dimensionQuery, measureQuery);
                }else{
                    dimensionQuery.push('[Sequence].[Sequence].['+parsedParams.fbGridRows[i]["[Sequence].[Sequence]"]+']');

                    if(rowStatus == "U"){       
                        vdCommon.updateMeasure(dimensionQuery, measureQuery);
                    }else if(rowStatus == "D"){
                        vdCommon.deleteMeasure(dimensionQuery, "Panel PO Proposal");
                    }
                }
            }

            return { "Code" : 0, "Msg" : "", "Rows" : "" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };     

    /*{ "fbFuncName" : "fn_send",
      "fbParams":{
        "filters":{
            "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["CWV_MP"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
            "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
        }
      },
      "fbGridRows" : [
        {
        "rowstatus":"C", "rowindex":2,
        "[Version].[Version Name]" : "CWV_MP",
        "[Location].[Location]" : "P551LCD",
        "[Time].[Week]":"202508",
        "[Sequence].[Sequence]":"2",        
        "[Item Material].[Item Material]":"BN96-54530B",
        "[Sub Location].[Sub Location]": "P105",
        "[Trans Mode].[Trans Mode]": "VESSEL",
        "Measure.[Panel PO Proposal_POP ID]" : "242225367807",
        "Measure.[Panel PO Proposal_ETD Week]" : "202509",
        "Measure.[Panel PO Proposal_ETA Week]" : "202511",
        "Measure.[Panel PO Proposal_POP Reason]" : "",
        "Measure.[Panel PO Proposal_POP Reason Detail]" : "TEST",
        "Measure.[Panel PO Proposal_Status]" : "INI",
        "Measure.[Panel PO Proposal_ERP Vendor]" : "C100-AK",
        "Measure.[Panel PO Proposal_Incoterms1]" : "CIF",
        "Measure.[Panel PO Proposal_Incoterms2]" : "ORIGIN",
        "Measure.[Panel PO Proposal_ETD QTY]" : "12000",
        "Measure.[Panel PO Proposal_Open PO QTY]" :"2000" ,
        "Measure.[Panel PO Proposal_Calc QTY]" : "10000",
        "Measure.[Panel PO Proposal_Confirm POP QTY]" : "800"
        }
      ]
     }*/
    var fn_send = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {           
            //vdCommon.debug("Grid Rows["+parsedParams.fbGridRows.length+"]");
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let dimensionUpdate = [];
                let measureUpdate= [];

                let sendQty = parsedParams.fbGridRows[i]["Measure.[Panel PO Proposal_Confirm POP QTY]"];

                // (1) Send 상태로 업데이트
                let version = parsedParams.fbGridRows[i]["[Version].[Version Name]"] ;
                let location = parsedParams.fbGridRows[i]["[Location].[Location]"] ;
                let week = parsedParams.fbGridRows[i]["[Time].[Week]"];
                let sequence = parsedParams.fbGridRows[i]["[Sequence].[Sequence]"];
                let itemMaterial = parsedParams.fbGridRows[i]["[Item Material].[Item Material]"];
                let subLocation = parsedParams.fbGridRows[i]["[Sub Location].[Sub Location]"];
                let transMode = parsedParams.fbGridRows[i]["[Trans Mode].[Trans Mode]"]

                dimensionUpdate.push("[Version].[Version Name].["+version+"]")                
                dimensionUpdate.push("[Location].[Location].["+location+"]");
                dimensionUpdate.push("[Time].[Week].["+week+"]");
                dimensionUpdate.push("[Sequence].[Sequence].["+sequence+"]");
                dimensionUpdate.push("[Item Material].[Item Material].["+itemMaterial+"]");
                dimensionUpdate.push("[Sub Location].[Sub Location].["+subLocation+"]");
                dimensionUpdate.push("[Trans Mode].[Trans Mode].["+transMode+"]");

                measureUpdate.push('Measure.[Panel PO Proposal_Confirm POP QTY] =' +sendQty + ";");
                //measureUpdate.push('Measure.[Panel PO Proposal_POP Status] = "SEND";');
                measureUpdate.push('Measure.[Panel PO Proposal_POP Status] = "REQ";');
                measureUpdate.push("Measure.[Panel PO Proposal_Send Date] = Now();");
                measureUpdate.push("Measure.[Panel PO Proposal_Send User] = CurrentUser().[User Name];");

                vdCommon.updateMeasure(dimensionUpdate, measureUpdate);

                //(2)Status가 INI인 데이타에 대해서 Send 수량을 합산함.
                let selectDim = [];
                let selectMeasure = [];
                selectDim.push("[Version].[Version Name].["+version+"]")
                selectDim.push("[Location].[Location].["+location+"]");
                selectDim.push("[Time].[Week].["+week+"]");
                selectDim.push('[Sequence].[Sequence].filter(#.Name != "'+sequence+'")');
                selectDim.push("[Item Material].[Item Material].["+itemMaterial+"]");
                selectDim.push("[Sub Location].[Sub Location].["+subLocation+"]");
                selectDim.push("[Trans Mode].[Trans Mode].["+transMode+"]");

                selectMeasure.push("Measure.[Panel PO Proposal_POP ID]");
                selectMeasure.push("Measure.[Panel PO Proposal_POP Status]");
                selectMeasure.push("Measure.[Panel PO Proposal_Open PO QTY]");

                let whereQuery = 'Where { Measure.[Panel PO Proposal_POP Status] in {"INI", "ERR"} }';

                let result = vdCommon.selectList(selectDim, selectMeasure, whereQuery, "","");
                
                for(var k=0; k < result.cs.rowCount; k++){                    
                    let scopeDim = [];
                    scopeDim.push("[Version].[Version Name].["+version+"]")
                    scopeDim.push("[Location].[Location].["+location+"]");
                    scopeDim.push("[Time].[Week].["+week+"]");
                    scopeDim.push("[Sequence].[Sequence].["+ result.cs.row(k).cell(result.cs.memberColumnIndex("Sequence", "Sequence")).Name+"]");
                    scopeDim.push("[Item Material].[Item Material].["+itemMaterial+"]");
                    scopeDim.push("[Sub Location].[Sub Location].["+subLocation+"]");
                    scopeDim.push("[Trans Mode].[Trans Mode].["+transMode+"]");
                    vdCommon.debug("Scope Dim ["+sendQty+"] "+ JSON.stringify(scopeDim));

                    let beforeOpenPOQty = result.cs.row(k).cell(result.cs.measureColumnIndex("Panel PO Proposal_Open PO QTY"));
                    
                    if(beforeOpenPOQty == undefined || beforeOpenPOQty == null){
                        beforeOpenPOQty = 0;
                    }

                    let tOpenPOQty = parseInt(beforeOpenPOQty) + parseInt(sendQty);

                    vdCommon.createMeasure(scopeDim, 
                        ["Measure.[Panel PO Proposal_Open PO QTY] = " + tOpenPOQty +";",
                        "Measure.[Panel PO Proposal_Update Time] = Now();",
                        "Measure.[Panel PO Proposal_Updated By] = CurrentUser().[User Name];"
                    ]);                    
                }            
            }
            return { "Code" : 0, "Msg" : "", "Rows" : "" };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    /*{ "fbFuncName" : "fn_reload",
      "fbParams":{
        "filters":{
            "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["CWV_MP"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
            "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
        }
      }
     }*/

    var fn_reload = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try { 
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let selectDim = [];
            let selectMeasure = [];
            selectDim.push("[Version].[Version Name].["+fbVersion+"]");
            selectDim.push("[Location].[Location]");
            selectDim.push("[Time].[Week]");
            selectDim.push("[Sequence].[Sequence]");
            selectDim.push("[Item Material].[Item Material]");
            selectDim.push("[Trans Mode].[Trans Mode]");
            selectDim.push("[Sub Location].[Sub Location]");

            selectMeasure.push("Measure.[Panel PO Proposal_POP Status]");
            let whereQuery = 'Where { Measure.[Panel PO Proposal_POP Status] in {"INI", "ERR"} }';

            let result = vdCommon.selectList(selectDim, selectMeasure, whereQuery, "","");

            for(var k=0; k < result.cs.rowCount; k++){ 

                let fbLocation = result.cs.row(k).cell(result.cs.memberColumnIndex("Location", "Location")).Name;
                let fbSubLocation = result.cs.row(k).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location")).Name;
                let fbItemMaterial = result.cs.row(k).cell(result.cs.memberColumnIndex("Item Material", "Item Material")).Name;
                let fbTransMode = result.cs.row(k).cell(result.cs.memberColumnIndex("Trans Mode", "Trans Mode")).Name;

                let execQuery = 'EXEC plugin instance [PY_UI_POProposal] for measures {[Panel PO Proposal_POP ID]} ';
                execQuery += 'using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView", "CWV_MP"}) *[Location].[Location].['+fbLocation+'] ';
                execQuery += '* [Item Material].[Item Material].['+fbItemMaterial+'] * [Sub Location].[Sub Location].['+fbSubLocation+'] * [Trans Mode].[Trans Mode].['+fbTransMode+'] ) ' ;
                execQuery += 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), ';
                execQuery += '(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};' ;
                //vdCommon.debug("<Reload>"+execQuery);
                /*EXEC plugin instance [PY_UI_POProposal] for measures {[Panel PO Proposal_POP ID]} 
                using scope ([Version].[Version Name].filter(#.Name in {"CurrentWorkingView", "CWV_MP"}) 
                *[Location].[Location].[P306] 
                * [Item Material].[Item Material].[BN07-01947A] 
                * [Sub Location].[Sub Location].[G2907059] 
                * [Trans Mode].[Trans Mode].[VESSEL] ) 
                using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False"), (paramOutVersion , "CWV_MP"), (MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")};
                */
                vdCommon.executeQuery("fn_reload(PO Proposal) ", execQuery); 
            }      

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_popReason" : fn_cb_popReason,
        "fn_cb_incoterms1" : fn_cb_incoterms1,
        "fn_sel_incoterms1" :fn_sel_incoterms1,
        "fn_cb_erpVendor" : fn_cb_erpVendor,
        "fn_cb_incoterms2" : fn_cb_incoterms2,
        "fn_addInfo": fn_addInfo,
        "fn_save": fn_save,
        "fn_send": fn_send,
        "fn_reload" : fn_reload
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});