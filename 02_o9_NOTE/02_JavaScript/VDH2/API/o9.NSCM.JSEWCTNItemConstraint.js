define('o9.NSCM.JSEWCTNItemConstraint', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){	
	const programName = "o9.NSCM.JSEWCTNItemConstraint";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWCTNItemConstraint
    // Action Button : EWCTNItemConst
    // 화면명 : CTN Item Constraint
    // 2025.08.26 최초 생성
    // 2025.09.15 fn_frozenWeek() 함수 변경 EOP 추가함
    // 2025.09.17 에러 메세지 수정
    // 2025.09.17 EW쪽 팝업을 처리하기 위해서 Code 값을 "1"로 처리함.
    // 2025.09.23 Update 수정
    // 2025.09.23 GC/AP2 Sales Domain에서 조회되도록 수정함. 
    // 2025.09.30 fn_cb_setItem() IBPL 조건 수정
    // 2025.10.15 fn_cb_setItem() IBPL 조건 추가 변경
    // 2025.10.24 fn_cb_siteMF() 추가함. 
    //            BOD Item 메져그룹에서 조회하도록 수정
    // 2025.11.05 fn_cb_masterType() 추가함.
    // 2025.11.07 AP2 조회 변경  &NSUISalesStd2View 반영함.
    // 2025.11.11 Save시 Version 정보를 Grid Row 단위로 받아서 처리함.
    // 2025.11.18 fn_filterConstWeek 추가함.
    // 2025.12.04 fn_validation() CHG Reason 컬럼 입력 여부 체크함.
    // 2025.12.10 fn_filterConstWeek() "-"에 대한 조회 조건 수정
    // 2025.12.23 fn_validation() 수정 => "\n" 제거함.
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가
    // 2026.01.02 View Filter 조건 처리 추가함.
    //  => fn_filterList(), fn_dataCheck(), lfn_extractWhere(), lfn_makeWhere_Filter(), lfn_makeWhere_bodItem()
    // 2026.01.07 Filter 조건 적용함.
    // 2026.01.08 fn_cb_setItem() 호출 부분 삭제(EW 공통 Item 팝업 사용)
    // 2026.01.19 API where 조건으로 묶어서 호출하여 하도록 수정함.
    // 2026.03.09 fn_merge() 추가함.
    // 2026.04.08 [Sales Domain].[AP2] 삭제함. 
    // 2026.04.08 fn_filterConstWeek() 함수 수정
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
            if ( parsedParams.fbParams["includeProperty"] == undefined ) {
                parsedParams.fbParams["includeProperty"] = "";
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
            // 콤보에 Blank 추가
            if ( parsedParams.fbParams["existBlank"] == undefined ) {
                parsedParams.fbParams["existBlank"] = false;
            }
            // 콤보에 - 추가
            if ( parsedParams.fbParams["existHyphen"] == undefined ) {
                parsedParams.fbParams["existHyphen"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }
            if ( parsedParams.fbParams["isDisplayNameWithCode"] == undefined ) {
                parsedParams.fbParams["isDisplayNameWithCode"] = true;
            }
            // filters 조건 추가
            if ( parsedParams.fbParams["filters"] == undefined ) {
                parsedParams.fbParams["filters"] = {};
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

    /****************************** Start : Filter 처리 (BOD Item 기준) ******************************/
    var fn_dataCheck = function(val){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {        
            var k = 0;

            if(vdUtil.fn_getString(val) == ""){
                return "";
            }

            if ( Array.isArray(val)){
                for (k = 0; k < val.length; k++){
                    if(val[k] == "All"){                    
                        return "";
                    }
                }
                return val;
            }

            let rtnValue = val.split("^");
            for (k = 0; k < rtnValue.length; k++){
                if(rtnValue[k] == "All"){
                    return "";
                }
            }
            return rtnValue;
        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }

    //wild card & multi select 데이타에 대한 Filter 조건  
    var fn_filterList = function (list) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        const vdUtil = new commonLib.VdUtil();
        vdCommon.setLogLevel("Debug");
        try {
            var strSelect = "";

            if (list == "All" || list == "") {
                return strSelect;
            }

            if ( list != "" && list.indexOf("%") == 1 ) {
                for (k = 0; k < list.length; k++) {
                    var sData = list[k];
                    if (String(sData).toUpperCase() === "ALL") {
                        strSelect = '';
                    } else {
    
                        var startChar = sData.substring(0, 1);
                        var endChar = sData.substring(sData.length - 1, sData.length);
    
                        if (k > 0) {
                            strSelect += ' || '; //OR 조건식 추가
                        }
    
                        if (startChar === "%" && endChar === "%") {
                            //console.log("중간체크") 
                            strSelect += '#.Name contains "' + sData.replace(/%/g, "") + '"';
                        } else if (startChar === "%") {
                            //console.log("끝")
                            strSelect += '#.Name endswith "' + sData.replace(/%/g, '') + '"';
                        } else if (endChar === "%") {
                            //console.log("startswith")
                            strSelect += '#.Name startswith "' + sData.replace(/%/g, '') + '"';
                        } else {
                            //console.log("equals")
                            strSelect += '#.Name == "' + sData.trim() + '"';
                        }
                    }
                }                
            }else{
                strSelect ='#.Name in {"' + list + '"}';
            }
            vdCommon.debug("[fn_filterList]" + strSelect);
            return strSelect;

        } catch (e) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
            return;
        }
    }

    //BOD Item WHere 절 생성
    var lfn_makeSales_Filter = function(parsedParams, filterStr){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            let filterInfo = vdUtil.fn_getFilter(parsedParams, filterStr);
            let returnValue ="";
            let selectResult, selectedMembers;
            let comboList = [];
            vdCommon.debug(JSON.stringify(filterInfo));
            if ( filterInfo == "" ) {
                return "";
            } else {
                if ( filterInfo["MemberFilter"] == "" && filterInfo["SelectedMembers"].length == 0 ) {
                    return "";
                }else{
                    if(filterStr == "[Sales Domain].[GC]"){
                        selectedMembers = vdUtil.fn_getFilterValue(parsedParams, filterStr);
                        if(selectedMembers.length > 0){
                            returnValue = selectedMembers;
                        }else{
                            selectResult = vdCommon.selectList([vdUtil.fn_getFilterQuery(parsedParams, filterStr)], [], "" ,"",parsedParams.fbParams.limit);
                            comboList = vdCommon.fn_makeCombo(selectResult, {DimName: "Sales Domain", DimAttbName: "GC", Sort: "DisplayName",existAll: false,isDisplayNameWithCode: false});
                            returnValue = comboList.map((value) => value.Name); //Array 형태
                        }                        
                    }else if(filterStr == "[Sales Domain].[AP2]"){
                        selectedMembers = vdUtil.fn_getFilterValue(parsedParams, filterStr);
                        if(selectedMembers.length > 0){
                            returnValue = selectedMembers;
                        }else{
                            selectResult = vdCommon.selectList([vdUtil.fn_getFilterQuery(parsedParams, filterStr)], [], "" ,"",parsedParams.fbParams.limit);
                            comboList = vdCommon.fn_makeCombo(selectResult, {DimName: "Sales Domain", DimAttbName: "AP2", Sort: "DisplayName",existAll: false,isDisplayNameWithCode: false});
                            vdCommon.debug("ComboData : " + JSON.stringify(comboList));
                            returnValue = comboList.map((value) => value.Name); //Array 형태
                        }
                    }              
                } 
            }
            vdCommon.debug("Filter[Sales]" + JSON.stringify(returnValue));
            return returnValue;

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }        
    };
    
    var lfn_makeWhere_Filter = function(parsedParams, filterStr){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            let returnValue ="";
        
            if(filterStr == "[Location]"){
                let fbFilters =  parsedParams.fbParams["filters"];
                let filterWhere = "";
                if(fbFilters != undefined){
                    for (let key in fbFilters) {
                        if(filterStr.includes(key.split(".")[0])){
                            //vdCommon.debug("[Key]" + key);
                            filterWhere += (filterWhere == ""?  "" : ",") + vdUtil.fn_getFilterQuery2(parsedParams, key) ;
                        }
                    }
                    returnValue = filterWhere;
                }
            } 
            return returnValue;
        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }        
    };    

    var lfn_makeWhere_bodItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let whereQuery = "";
            let fbWhere = parsedParams.fbParams["where"];
            let itemFilter = "";
            let itemCheck = false;

            whereQuery = " [Version].[Version Name].[" + fbVersion + "]";

            if(fbWhere != undefined){
                for (let key in fbWhere) {
                    if (key == "[Item].[Item]") {
                        //Itme Filter 조건 체크
                        itemFilter = fn_filterList(fbWhere[key]);
                        if (itemFilter.length > 0) {
                            itemFilter = ".filter(" + itemFilter + ")";
                        }
                        whereQuery += (whereQuery == "" ? "" : ", ") + "&SETItem" + itemFilter;
                        itemCheck = true;
                    } else if(key == "[Sales Domain].[GC]"){
                        whereQuery += (whereQuery == "" ? "" : ", " ) + "[Sub Location].[Sub Location GC]"+ vdUtil.fn_filterStr(fn_dataCheck(fbWhere[key])) ;     
                    } else if(key == "[Sales Domain].[AP2]"){
                        whereQuery += (whereQuery == "" ? "" : ", " ) + "[Sub Location].[Sub Location Rep AP2]"+ vdUtil.fn_filterStr(fn_dataCheck(fbWhere[key])) ; 
                    } else {
                        whereQuery += (whereQuery == "" ? "" : ", " ) + key + vdUtil.fn_filterStr(fn_dataCheck(fbWhere[key])); 
                    }                    
                    vdCommon.debug("Where(for)["+key+"]" + whereQuery);
                }
            };
    
            whereQuery += (itemCheck ? "" : ",[Item].[Item]")
            whereQuery += ",&NSUISubLocationDC";
            whereQuery += ",[Trans Mode].[Trans Mode]";
            whereQuery += ",Measure.[BOD Item_Asn] == 1";
            //whereQuery += ',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE"})';
            //whereQuery += ',(coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()) ';
            vdCommon.debug("WhereQuery =" + whereQuery);

            if ( whereQuery.length == 0) {
                return "";
            } else{
                return whereQuery;
            }
        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }        
    };
    
    /****************************** End : Filter 처리 (BOD Item 기준) ******************************/

    /* ********************************************************************************** */
    /* {"fbFuncName" : "fn_frozenWeek",
        "fbParams":{
            "where":{"[Item].[Item]":["HG40EC460KWXCI"], "[Location].[Location]":["P406"]}
            }
        }
    */
    var fn_frozenWeek = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let frozenWeek = "";

            if(vdUtil.fn_getString(frozenWeek) == ""){
                //CurrentWeek로 넘겨줌
                let result = vdCommon.selectQueryList("[CurrentWeek Select]", "Select (&CurrentWeek);");
                frozenWeek = vdCommon.getMember(result.cs, 0, "Time", "Week");
                vdCommon.debug("[Current]" + frozenWeek.Name);
            }

            // Measure.[PLC Mfg_EOP Cur Date] 데이타 조회
            let fbItem = parsedParams.fbParams.where["[Item].[Item]"];
            let fbLocation = parsedParams.fbParams.where["[Location].[Location]"];

            let eopDimension = [];
            let eopMeasure = [];
            eopDimension.push("[Version].[Version Name].["+fbVersion+"]");
            eopDimension.push("[Item].[Item]"+vdUtil.fn_filterStr(fbItem));
            eopDimension.push("[Location].[Location]"+vdUtil.fn_filterStr(fbLocation));

            eopMeasure.push("Measure.[PLC Mfg_EOP Cur Date]");
            eopMeasure.push("Measure.[Dummy]");

            let eopResult = vdCommon.selectList(eopDimension, eopMeasure, "","","");
            let eopDate = "";
            let eopWeek = "-";
            if(eopResult.cs.rowCount > 0){
                eopDate = vdCommon.getMeasureValue(eopResult.cs, 0, "PLC Mfg_EOP Cur Date");
                if(vdUtil.fn_getString(eopDate) != ""){
                    eopDate = eopDate.substring(0, 10);
                    //vdCommon.debug("[PLC Date]"+eopDate);
                    let weekResult = vdCommon.selectQueryList("[Week]", "Select ([Time].[Day].["+eopDate+"] * [Time].[Week]) on row, () on column;");
                    eopWeek = weekResult.cs.row(0).cell(weekResult.cs.memberColumnIndex("Time","Week")).Name;
                }
            }
            let comboList = [];
            comboList.push({ "FROZEN_WEEK" : frozenWeek.Name, "EOP_WEEK":eopWeek});

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }   

    /* ********************************************************************************** */
    /*{"fbFuncName" : "fn_cb_siteMF", 
      "fbParams":{
           "where":{"[Item].[Item]":["QN55LS01BAFXZA"]}
            ,"existAll":true
            }
    }
    */
    var fn_cb_siteMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            //vdCommon.debug("[parsedParams(1)]" + JSON.stringify(parsedParams));
            let comboList = [];
            parsedParams.fbParams.filterDimension =["[Location]"];
            let dimensionQuery =[];
            dimensionQuery.push('[Location].[Location]');
            
            let measureQuery = [];
            let whereQuery = lfn_makeWhere_bodItem(parsedParams);
            let filterQuery = lfn_makeWhere_Filter(parsedParams, "[Location]");            
            whereQuery = "Where {" + whereQuery + (whereQuery.length > 0 ? ",":"") + filterQuery + "}";
            
            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery ,"",parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName", 
                                                    existAll : false, isDisplayNameWithCode : false});

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    /* ********************************************************************************** */    
    /*{"fbFuncName" : "fn_cb_salesGC", 
       "fbParams":{
            "where":{"[Location].[Location]":["P306"],"[Item].[Item]":["QN55LS01BAFXZA"]}
            ,"existAll":true
            }
        }
    */
    var fn_cb_salesGC = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let comboList = [];
            parsedParams.fbParams.filterDimension = ["[Sales Domain]"];
            let dimensionQuery =[];
            dimensionQuery.push('[Sub Location].[Sub Location GC].filter(~(#.Name in {"All", "-"}))' + vdUtil.fn_filterStr(lfn_makeSales_Filter(parsedParams, "[Sales Domain].[GC]")));
            
            let measureQuery = [];
            let whereQuery = lfn_makeWhere_bodItem(parsedParams);
            whereQuery = "Where {" + whereQuery + "}";            

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery ,"",parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, 
                                            {DimName: "Sub Location", DimAttbName: "Sub Location GC", Sort: "DisplayName",
                                                existAll: false,isDisplayNameWithCode: false});

            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Sales Domain GC에서 다시 조회함.
            let arrayGC = comboList.map((value) => value.Name);
            vdCommon.debug("arrayGC : " + JSON.stringify(arrayGC));
            if(arrayGC.length == 0){
                comboList = [];
                return { "Code": 0, "Msg": "", "Rows":comboList};
            }
            //Sales Domain에서 조회함.
            let salesDomainSelect = vdCommon.selectList(["&NSUISalesGrpGCView.relatedmembers([GC])"+vdUtil.fn_filterStr(arrayGC)], 
                                                        [], "", "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(salesDomainSelect, {
                    DimName: "Sales Domain", DimAttbName: "GC", Sort: "DisplayName",
                    existAll: parsedParams.fbParams.existAll, isDisplayNameWithCode: false});
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    /* ********************************************************************************** */
    /*{"fbFuncName" : "fn_cb_salesAP2", 
       "fbParams":{
            "where":{"[Location].[Location]":["P306"],"[Item].[Item]":["QN55LS01BAFXZA"],"[Sales Domain].[GC]":["203"]}
            ,"existAll":true
            }
        }  
    }*/
    var fn_cb_salesAP2 = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let comboList = [];
            parsedParams.fbParams.filterDimension = ["[Sales Domain]"];
            
            let dimensionQuery =[];
            dimensionQuery.push('[Sub Location].[Sub Location Rep AP2].filter(~(#.Name in {"All", "-"}))'+ vdUtil.fn_filterStr(lfn_makeSales_Filter(parsedParams, "[Sales Domain].[AP2]")));
            
            let measureQuery = [];
            let whereQuery = lfn_makeWhere_bodItem(parsedParams);
            whereQuery = "Where {" + whereQuery + "}";

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery ,"",parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Sub Location", DimAttbName : "Sub Location Rep AP2", Sort : "DisplayName",
                                                    existAll : false, isDisplayNameWithCode : false});
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Sales Domain AP2에서 다시 조회함.
            let arrayAP2 = comboList.map((value) => value.Name);
            vdCommon.debug("arrayAP2 : " + JSON.stringify(arrayAP2));
            if(arrayAP2.length == 0){
                comboList = [];
                return { "Code": 0, "Msg": "", "Rows": comboList };
            }
            //Sales Domain에서 조회함.
            let salesDomainSelect = vdCommon.selectList(["&NSUISalesStd2View.relatedmembers([AP2])"+vdUtil.fn_filterStr(arrayAP2)], 
                                                        [], "", "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(salesDomainSelect, {
                    DimName: "Sales Domain", DimAttbName: "AP2", Sort: "DisplayName",
                    existAll: parsedParams.fbParams.existAll, isDisplayNameWithCode: false});
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };    

    /* ********************************************************************************** */
    /*{"fbFuncName" : "fn_cb_masterData",
       "fbParams":{
         "where":{"MasterType":"version", "DataType":"current"}
        }
       ) 
    */
    var fn_cb_masterData = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let comboList = [];
            
            let fbMasterType = parsedParams.fbParams.where["MasterType"];
            if(Array.isArray(fbMasterType)){
                fbMasterType = fbMasterType[0];
            }
            let fbDataType = parsedParams.fbParams.where["DataType"];
            if(Array.isArray(fbDataType)){
                fbDataType = fbDataType[0];
            }
            
            let dimensionQuery =[];
            let measureQuery = [];
            let whereQuery = "";

            if(String(fbDataType).toUpperCase() == "CURRENT"){
                dimensionQuery.push("&CWVUI");
                dimensionQuery.push("&CurrentWeek");                
            }else if(String(fbDataType).toUpperCase() == "LAST"){
                dimensionQuery.push("&LastSyncVersion");
                dimensionQuery.push("&LastPastWeek");
            }

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            let version = "", planId="", week = "";
            if(selectResult.cs.rowCount > 0){
                version = selectResult.cs.row(0).cell(selectResult.cs.memberColumnIndex("Version","Version Name")).Name;
                planId = selectResult.cs.row(0).cell(selectResult.cs.memberColumnIndex("Version","Version Name")).DisplayName;
                week = selectResult.cs.row(0).cell(selectResult.cs.memberColumnIndex("Time","Week")).Name;
            }            

            comboList.push({ "VERSION " : version, "PLANID": planId,"WEEK":week});
                                                    
            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /* {"fbFuncName" : "fn_filterConstWeek",
        "fbParams":{
                    "where":{"[From Week]":["202508"], "[To Week]":["202541"]}
                    }
        }
    */
    var fn_filterConstWeek= function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let fbFromWeek = parsedParams.fbParams.where["[From Week]"];
            let fbToWeek = parsedParams.fbParams.where["[To Week]"];

            let ibplQuery = '(Measure.[CTN Item Const_Start Week] >="'+fbFromWeek[0]+'" && Measure.[CTN Item Const_Start Week] <= "'+fbToWeek[0]+'")';
            ibplQuery += '|| (Measure.[CTN Item Const_End Week] >="'+fbFromWeek[0]+'" && Measure.[CTN Item Const_End Week] <= "'+fbToWeek[0]+'")';

            vdCommon.programEnd();                          
            return { "Code" : 0, "Msg" : "", "Rows" : [{Name : ibplQuery}]};                                                   

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    /* ********************************************************************************** */
    /* fn_Save() 관련 */
    var fn_validation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let errorCnt1 = 0;
            let errorCnt2 = 0;            
            let errorMsg1 = "Error : Duplicated Intersection(s)";            
            let errorMsg2 = 'Error : Please enter your "CHG Reason"';
            let fbVersion = parsedParams.fbParams.version;

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let fbItem = parsedParams.fbGridRows[i]["[Item].[Item]"]; 
                let fbChgReason = parsedParams.fbGridRows[i]["Measure.[CTN Item Const_Frozen SOP Override Reason]"];

                parsedParams.fbGridRows[i]["rowmsg"] = "";
                parsedParams.fbGridRows[i]["errorflag"] = "";

                if(rowStatus == "C"){
                     //validation 체크함.
                    //(1) 등록여부 확인 : CTN Item Const 메져그룹 데이타 존재 여부를 체크함.
                    let sDimension = [];
                    sDimension.push("[Version].[Version Name].["+fbVersion+"]");
                    sDimension.push("[Location].[Location].["+fbLocation+"]");
                    sDimension.push("[Item].[Item].["+fbItem+"]");

                    let sMeasure = [];
                    sMeasure.push("Measure.[CTN Item Const_Frozen Week]");

                    let chkFlag  = vdCommon.existMeasure(sDimension, sMeasure, "")
                    //vdCommon.debug("[CTN Item Const existMeasure]" + chkFlag);
                   
                    if(chkFlag){
                        errorCnt1++;
                        parsedParams.fbGridRows[i]["rowmsg"] = errorMsg1;
                        parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                    }
                }

                //CHG Reason 입력여부 체크
                if(rowStatus != "D"){
                    if(fbChgReason.trim() == ""){
                        errorCnt2++;
                        parsedParams.fbGridRows[i]["rowmsg"] = errorMsg2;
                        parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                    }
                }
            }
 
            let errorMsg = "";
            if(errorCnt1 > 0){
                errorMsg += (errorMsg == "" ? "" : " ")  + errorMsg1 ;
            }
            vdCommon
            if(errorCnt2 > 0){
                errorMsg += (errorMsg == "" ? "" : " ")  + errorMsg2 ;
            }  

            if(errorCnt1 + errorCnt2 > 0 ){
                //Error Row만 Return 함.
                let checkGridRows = parsedParams.fbGridRows;
                const errorRows = checkGridRows.filter((checkGridRows)=>{return checkGridRows.errorflag === "ERROR"});
                parsedParams.fbGridRows = errorRows;
                //2025. 09.17 EW쪽 팝업을 처리하기 위해서 Code 값을 "1"로 처리함.
                return { "Code" : 1, "Msg" : errorMsg, "Rows" : parsedParams.fbGridRows };
            }

            return { "Code" : 0, "Msg" : "" };
        }catch(e){
            return { "Code" : -1, "Msg" : e.message };
        }  
    };

    /*{"fbFuncName" : "fn_save",
    "fbParams": {"version":"CWV_MP"},
    "fbGridRows" : [
    {"rowstatus":"D", "rowindex":0
     ,"[Version].[Version Name]" : "CWV_MP"
    ,"[Item].[Item]" : "QE50Q60DAUXRU"
    ,"[Location].[Location]":"P701"
    },
    {"rowstatus":"U", "rowindex":1
        ,"[Version].[Version Name]" : "CWV_MP"
        ,"[Item].[Item]" : "QE50Q60DAUXSQ"
        ,"[Location].[Location]":"P401"
        ,"Measure.[CTN Item Const_AP2 Cap]":"Y"
        ,"Measure.[CTN Item Const_Apply Flag]": "N"
        ,"Measure.[CTN Item Const_Frozen Week]" : "202508"
        ,"Measure.[CTN Item Const_Start Week]" : "202509"
        ,"Measure.[CTN Item Const_End Week]" : "202610"
        ,"Measure.[CTN Item Const_Frozen SOP Override Qty]" : "10000"
        ,"Measure.[CTN Item Const_Frozen SOP Override Reason]" : "TEST_Update_01"
    },
    {"rowstatus":"C", "rowindex":2
        ,"[Version].[Version Name]" : "CWV_MP"
        ,"[Item].[Item]" : "QE50Q60DAUXSQ"
        ,"[Location].[Location]":"P306"
        ,"Measure.[CTN Item Const_AP2 Cap]":"Y"
        ,"Measure.[CTN Item Const_Apply Flag]": "Y"
        ,"Measure.[CTN Item Const_Frozen Week]" : "202509"
        ,"Measure.[CTN Item Const_Start Week]" : "202510"
        ,"Measure.[CTN Item Const_End Week]" : "202610"
        ,"Measure.[CTN Item Const_Frozen SOP Override Qty]" : "25000"
        ,"Measure.[CTN Item Const_Frozen SOP Override Reason]" : "TEST_CREATE_01"
    }
    ]}
    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            //Validation 체크
            let errorData = fn_validation(parsedParams);
            if(errorData.Code != 0){
                return errorData;
            }

            let dimension = [];
            let measure= [];
            let where = "";
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbVersion =  vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
                let fbItem = parsedParams.fbGridRows[i]["[Item].[Item]"];    
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];
                let fbAP2Cap= parsedParams.fbGridRows[i]["Measure.[CTN Item Const_AP2 Cap]"];
                let fbApply = parsedParams.fbGridRows[i]["Measure.[CTN Item Const_Apply Flag]"];
                let fbFrozenWeek = parsedParams.fbGridRows[i]["Measure.[CTN Item Const_Frozen Week]"];
                let fbConstStart = parsedParams.fbGridRows[i]["Measure.[CTN Item Const_Start Week]"];
                let fbConstEnd = parsedParams.fbGridRows[i]["Measure.[CTN Item Const_End Week]"];
                let fbFrozenSOPQty = parsedParams.fbGridRows[i]["Measure.[CTN Item Const_Frozen SOP Override Qty]"];
                let fbFrozenSOPReason = parsedParams.fbGridRows[i]["Measure.[CTN Item Const_Frozen SOP Override Reason]"];

                dimension = [];
                dimension.push("[Version].[Version Name].["+fbVersion+"]");
                dimension.push("[Location].[Location].["+fbLocation+"]");
                dimension.push("[Item].[Item].["+fbItem+"]");
                
                measure = [];
                measure.push('Measure.[CTN Item Const_AP2 Cap] = "' + fbAP2Cap + '";'); 
                measure.push('Measure.[CTN Item Const_Apply Flag] = "' + fbApply + '";'); 
                measure.push('Measure.[CTN Item Const_Frozen Week] = "' + fbFrozenWeek +'";');
                measure.push('Measure.[CTN Item Const_Start Week] = "' + fbConstStart + '";');
                measure.push('Measure.[CTN Item Const_End Week] = "' + fbConstEnd + '";');
                /*2026.04.17 수정*/
                if(fbFrozenSOPQty != undefined && fbFrozenSOPQty != null && fbFrozenSOPQty != ""){
                    measure.push('Measure.[CTN Item Const_Frozen SOP Override Qty] = "' + fbFrozenSOPQty + '";');
                }else{
                    measure.push('Measure.[CTN Item Const_Frozen SOP Override Qty] = null;');
                }
                measure.push('Measure.[CTN Item Const_Frozen SOP Override Reason] = "' + fbFrozenSOPReason + '";');
                measure.push('Measure.[CTN Item Const_Updated By] = CurrentUser().[User Name];');  
                measure.push('Measure.[CTN Item Const_Update Time] = Now();');              

                if(rowStatus == "C"){    
                    if(vdCommon.existMeasure(dimension, ["Measure.[CTN Item Const_Frozen Week]"])){
                        vdCommon.updateMeasure(dimension,measure );
                    }else{
                        measure.push('Measure.[CTN Item Const_Created By] = CurrentUser().[User Name];');  
                        measure.push('Measure.[CTN Item Const_Creation Time] = Now();');                        
                        vdCommon.createMeasure(dimension,measure );
                    }
                    
                }else if(rowStatus == "U"){
                    if(vdCommon.existMeasure(dimension, ["Measure.[CTN Item Const_Frozen Week]"])){
                        vdCommon.updateMeasure(dimension,measure );
                    }else{
                        measure.push('Measure.[CTN Item Const_Created By] = CurrentUser().[User Name];');  
                        measure.push('Measure.[CTN Item Const_Creation Time] = Now();');                       
                        vdCommon.createMeasure(dimension,measure );
                    }
                }else if(rowStatus == "D"){
                    //Delete
                    vdCommon.deleteMeasure(dimension, "CTN Item Const"); 
                }

                if(rowStatus != "D"){
                    //파이썬 호출 : Item 별로
                    let execQuery = 'EXEC plugin instance [PY_UI_CTNItemConst] for measures {[CTN Item Const_Apply Flag]} '
                    execQuery += 'using scope ([Version].[Version Name].['+fbVersion+'] * [Item].[Item].['+fbItem+']) '                          
                    execQuery += 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False")' ;
                    execQuery += ',(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;';

                    vdCommon.printStep("["+programName+"] EXEC Python Call SQL>>"+execQuery);
                    vdCommon.executeQuery("PY_UI_CTNItemConst ", execQuery);  
                }
            }

            return { "Code": 0, "Msg": "Save Successed."};

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    /* ********************************************************************************** */
    /* EW 공통 팝업 사용으로 불필요할 수 있음. {"fbFuncName" : "fn_cb_setItem" }            */        
    var fn_cb_setItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{

            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            
            //BOD List 메져에서 조회함.
            let dimensionQuery = [];
            // 2025.10.15 조건 추가
            dimensionQuery.push('&SETItem.filter(~(#.Name startswith "CY")) * [Item].[Item Stage].[SET] * [Item].[ProductType].filter(#.Name !="CRT")');
            
            let whereQuery = "Where {";
            whereQuery += "[Version].[Version Name].["+fbVersion+"]";
            whereQuery += ", [Location].[Location]";
            whereQuery += ", [Sub Location].[Sub Location]";
            whereQuery += ", [Trans Mode].[Trans Mode]";
            whereQuery += ", Measure.[BOD Item_Asn] == 1" ;
            whereQuery += "}";

            var selectResult = vdCommon.selectList(dimensionQuery, ["Measure.[BOD Item_Asn]"], whereQuery, "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            let comboList = vdCommon.fn_makeCombo(selectResult, {DimName : "Item", DimAttbName : "Item", existAll : false, Sort : "DisplayName", isDisplayNameWithCode : false});

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    /* Scenario Version => Current Version(CWV_MP) Merge  */
    /* case1) param.commitType = 1 ( selected )
       case2) param.commitType = 0 ( bulk )
    */ 
    /*
        {"fbFuncName" : "fn_merge",
            "fbParams":{ "commitType":1,
            "filters":{
                    "[Version].[Version Name]":{"SelectedMembers":["202608_M_WI_04"],"SelectedMembersAlias":["202608_M_WI_04"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
                    "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
                }
            },
            "fbGridRows" : [
                {"[Location].[Location]" : "S422",
                "[Item].[Item]" : "CY-BD40WD/EN",
                "[Sales Domain].[AP2]" : "300672"
                }
            ]
        }
    */
    var fn_merge = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let dimensionInfo = [];
            let dimensionValue = [];
            let measureUpdateInfo = [];
            let measure = [];
            let whereQuery = 'Where { (Measure.[CTN Item Const_Updated By] == CurrentUser().[User Name] || Measure.[CTN Item Const_Updated By] == CurrentUser().Name)}'; 
            let rtn = false;

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Item].[Item]");        

            measure.push("Measure.[CTN Item Const_AP2 Cap]");
            measure.push("Measure.[CTN Item Const_Apply Flag]");
            measure.push("Measure.[CTN Item Const_DP Qty from W0]");
            measure.push("Measure.[CTN Item Const_EOH at PSI]");
            measure.push("Measure.[CTN Item Const_End Week]");
            measure.push("Measure.[CTN Item Const_Frozen SOP DP Diff Qty]");
            measure.push("Measure.[CTN Item Const_Frozen SOP Override Qty]");
            measure.push("Measure.[CTN Item Const_Frozen SOP Override Reason]");
            measure.push("Measure.[CTN Item Const_Frozen SOP Qty]");
            measure.push("Measure.[CTN Item Const_Frozen Week]");
            measure.push("Measure.[CTN Item Const_Prod Result Qty before W0]");
            measure.push("Measure.[CTN Item Const_Start Week]");

            if(parsedParams.fbParams.commitType == 1){
                //Check 한 데이타 Merge
                for(var k=0; k < parsedParams.fbGridRows.length; k++ ){
                    dimensionValue = [];
                    for(var j=0; j < dimensionInfo.length; j++){
                        let dim = dimensionInfo[j];
                        if(dim == "[Version].[Version Name]"){
                            dimensionValue.push(dim + ".["+fbVersion+"]");
                        }else{
                            dimensionValue.push(dim + ".["+ parsedParams.fbGridRows[k][dim] + "]");
                        }
                    }

                    let result= vdCommon.selectList(dimensionValue, measure, whereQuery, "", "");
                    rtn = fn_mergeScope(result, dimensionInfo,  measure, fbVersion);
                }
            }else{
                //Current User 수정 데이타 전체 Merge
                dimensionValue = [];
                for(var j=0; j < dimensionInfo.length; j++){
                    let dim = dimensionInfo[j];
                    if(dim == "[Version].[Version Name]"){
                        dimensionValue.push(dim + ".["+fbVersion+"]");
                    }else{
                        dimensionValue.push(dim);
                    }
                }
                let result= vdCommon.selectList(dimensionValue, measure, whereQuery, "", "");
                fn_mergeScope(result, dimensionInfo,  measure, fbVersion);                
            }

            return { "Code" : 0, "Msg" : "" };       

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    var fn_mergeScope = function(object, dimension, measure, sVersion){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{

            for(var i=0; i < object.cs.rowCount ; i++){
                let dimensionValue = [];
                for(var m = 0; m < dimension.length; m++){                    
                    if(dimension[m] == "[Version].[Version Name]"){
                        dimensionValue.push("CWV_MP");
                    }else{
                        let dim = dimension[m].split(".");
                        dimensionValue.push(object.cs.row(i).cell(object.cs.memberColumnIndex(dim[0].replace("[","").replace("]",""), dim[1].replace("[","").replace("]",""))).Name);
                    }                   
                }
                let changeMeasure = [];
                for(var n=0; n < measure.length; n++){
                    let measureName = measure[n];
                    //changeMeasure.push(measureName + " = "+ measureName +"@([Version].[Version Name].["+scenarioVer+"]);");
                    changeMeasure.push(vdUtil.fn_qMeaForMerge(measureName, sVersion));
                }

                //CWV_MP 버젼 데이타 조회하여 createMeasure인지 updateMeasure 인치 체크함.
                let selectDimension = vdCommon.makeDimension(dimension, dimensionValue);

                //Merge 데이타 
                changeMeasure.push(vdUtil.fn_qMeaUpdateTime("Measure.[CTN Item Const_Update Time]"));
                changeMeasure.push(vdCommon.fn_mergeUser("Measure.[CTN Item Const_Updated By]",sVersion));   

                vdCommon.createMeasure(selectDimension, changeMeasure);
            }

        }catch ( e ) {
            this.error(e.message);
            throw e;
        }

    }    

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_frozenWeek" : fn_frozenWeek,        
        "fn_cb_siteMF"  : fn_cb_siteMF,
        "fn_cb_salesGC" : fn_cb_salesGC,
        "fn_cb_salesAP2" : fn_cb_salesAP2,
        "fn_save" : fn_save
      , "fn_cb_masterData" : fn_cb_masterData
      , "fn_filterConstWeek" : fn_filterConstWeek
      , "fn_merge" : fn_merge
    };

    return {
        fn_loadFunction : fn_loadFunction
    };    
});