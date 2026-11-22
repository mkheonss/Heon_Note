define('o9.NSCM.JSEWCTNGroupConst', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
    const programName = "o9.NSCM.JSEWCTNGroupConst";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWCTNGroupConst
    // Action Button : EWCTNGroupConst
    // 화면명 : CTN Group Constraint
    // 2025.09.03 최초 생성
    // 2025.09.15 fn_frozenWeek() 함수 변경 EOP 추가함
    // 2025.09.23 update 일자 처리 수정
    // 2025.09.23 GC/AP2 Sales Domain에서 조회되도록 수정함. 
    // 2025.11.11 Save시 Version 정보를 Grid Row 단위로 받아서 처리함.
    // 2025.11.18 fn_filterConstWeek 추가함.
    // 2025.11.19 fn_description() 함수 추가 Desc 미입력시 입력된 조건 기준으로 description 생성함.
    // 2025.12.04 fn_cb_salesGC(),fn_cb_salesAP2() 함수 수정
    // 2025.12.04 메져 변경
    //            Measure.[CTN Grp Const_GC ID] => Measure.[CTN Grp Const_GC Code]
    //            Measure.[CTN Grp Const_AP2 ID] => Measure.[CTN Grp Const_AP2 Code]
    // 2025.12.08 BOD Item 기준으로 조회되도록 API 함수 추가 및 수정함.
    // 2025.12.10 fn_filterConstWeek() "-"에 대한 조회 조건 수정
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가
    // 2026.01.02 View Filter 조건 처리 추가함.(운영미반영)
    //  => fn_filterList(), fn_dataCheck(), lfn_extractWhere(), lfn_makeWhere_Filter(), lfn_makeWhere_bodItem()
    // 2026.01.14 fn_cb_setYear_bodItem(), fn_cb_inch_bodItem() => NameSet 적용
    // 2026.01.27 BOD Item 조회 조건 변경
    // 2026.03.09 fn_merge() 추가함.
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
            //console.log("[fn_dataCheck]"+rtnValue);
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

            vdCommon.debug("[fn_filterList]" + strSelect);
            return strSelect;

        } catch (e) {
            RuleOutputToUI = { Status: 'Error', Message: "Js Logic Error : " + e.message };
            return;
        }
    }
    //BOD Item WHere 절 생성
    var lfn_makeWhere_Filter = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {        
            let fbVersion = parsedParams.fbParams["version"];
            if(vdUtil.fn_getString(fbVersion) == ""){
                fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            }
            let fbFilters =  parsedParams.fbParams["filters"];
            let filterDimension = parsedParams.fbParams["filterDimension"]; //Where 조건을 적용할 Filter 조건
            let filterSalesDomainGC = "";
            let filterSalesDomainAP2 = "";
            let selectResult = [];
            let comboList = [];
            let SelectedMembers = [];
            let filterWhere = "";

            if(fbFilters != undefined){
                for (let key in fbFilters) {
                    if(filterDimension.includes(key.split(".")[0])){
                        if(key == "[Sales Domain].[GC]"){
                            //GC 데이타를 조회함.
                            //let selectGC = "Select ("+vdUtil.fn_getFilterQuery(parsedParams, key)+");" 
                            SelectedMembers = vdUtil.fn_getFilterValue(parsedParams);
                            if(SelectedMembers.length > 0){
                                filterSalesDomainGC = SelectedMembers;
                            }else{
                                selectResult = vdCommon.selectList([vdUtil.fn_getFilterQuery(parsedParams, key)], [], "" ,"",parsedParams.fbParams.limit);
                                comboList = vdCommon.fn_makeCombo(selectResult, {DimName: "Sales Domain", DimAttbName: "GC", Sort: "DisplayName",existAll: false,isDisplayNameWithCode: false});
                                filterSalesDomainGC = comboList.map((value) => value.Name); //Array 형태
                            }
                            vdCommon.debug("Filter[GC]" + JSON.stringify(filterSalesDomainGC));
                        }else if(key == "[Sales Domain].[AP2]"){
                            SelectedMembers = vdUtil.fn_getFilterValue(parsedParams);
                            if(SelectedMembers.length > 0){
                                filterSalesDomainAP2 = SelectedMembers;
                            }else{
                                selectResult = vdCommon.selectList([vdUtil.fn_getFilterQuery(parsedParams, key)], [], "" ,"",parsedParams.fbParams.limit);
                                comboList = vdCommon.fn_makeCombo(selectResult, {DimName: "Sales Domain", DimAttbName: "AP2", Sort: "DisplayName",existAll: false,isDisplayNameWithCode: false});
                                filterSalesDomainAP2 = comboList.map((value) => value.Name); //Array 형태                                
                            }
                            vdCommon.debug("Filter[AP]" + JSON.stringify(filterSalesDomainAP2));
                        }else{
                            if(key != "[Item].[Item]"){ //예외처리
                                filterWhere += (filterWhere == ""?  "" : ",") + vdUtil.fn_getFilterQuery(parsedParams, key) ;
                            }
                            
                        }
                    }
                }
            }
            return filterWhere;
        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }        
    };

    //BOD Item WHere 절 생성
    var lfn_makeWhere_bodItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {        
            let fbVersion = parsedParams.fbParams["version"];
            if(vdUtil.fn_getString(fbVersion) == ""){
                fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            }
            let fbWhere = parsedParams.fbParams["where"];
            let itemFilter = "";
            let itemCheck = false;
            vdCommon.debug("Where["+JSON.stringify(fbWhere)+"]");
            whereQuery = "Where { [Version].[Version Name].[" + fbVersion + "]";
            
            if(fbWhere != undefined){
                for (let key in fbWhere) {
                    if (key == "[Item].[Item]") {
                        //Itme Filter 조건 체크
                        itemFilter = fn_filterList(fbWhere[key]);
                        if (itemFilter.length > 0) {
                            itemFilter = ".filter(" + itemFilter + ")";
                        }
                        whereQuery += (whereQuery == "" ? "" : ", ") + "&SETItemExcludeOPT" + itemFilter;
                        itemCheck = true;
                    } else if(key == "[Sales Domain].[GC]"){
                        whereQuery += (whereQuery == "" ? "" : ", " ) + "[Sub Location].[Sub Location GC]"+ vdUtil.fn_filterStr(fn_dataCheck(fbWhere[key])); 
                    } else if(key == "[Sales Domain].[AP2]"){
                        whereQuery += (whereQuery == "" ? "" : ", " ) + "[Sub Location].[Sub Location Rep AP2]"+ vdUtil.fn_filterStr(fn_dataCheck(fbWhere[key])); 
                    } else {
                        whereQuery += (whereQuery == "" ? "" : ", " ) + (key == "[Item].[Product Group]" ? "&NSUIItemProductGroupView" : key) + vdUtil.fn_filterStr(fn_dataCheck(fbWhere[key])); 
                    }                    
                }
            };
            whereQuery += (itemCheck ? "" : ",[Item].[Item]")
            //whereQuery += ',[Item].[Item Stage].filter(#.Name == "SET")';
            whereQuery += ",&NSUISubLocationDC";
            whereQuery += ",[Trans Mode].[Trans Mode]";
            whereQuery += ",Measure.[BOD Item_asn] == 1";
            whereQuery += ',(Measure.[BOD Item_Cur Status] in {"PLANNED","ACTIVE"})';
            whereQuery += ',(coalesce(Measure.[BOD Item_Eff Startdate],DATEADD(Now(),-1,"Day")) < now() && coalesce(Measure.[BOD Item_Eff Enddate],DATEADD(Now(),1,"Day")) > now()) ';
            whereQuery += "}";

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
    /* ********************************************************************************** */
    /* {"fbFuncName" : "fn_frozenWeek",
     "fbParams":{"version":"CWV_MP", "existAll":true,
                "where":{
                    "[Location].[Location]":"P306",
                    "[Item].[Product Group]":["TV","AV"],
                    "[Item].[Product]":"All",
                    "[Item].[Project]":["QN80FE","QN85DD"],
                    "[Item].[Series Name]":"All",
                    "[Item].[Marketing Name]":"All",
                    "[Item].[Inch]":"All",
                    "[Item].[CTN]":"All",
                    "[Item].[Year]":"All",
                    "[Item].[Item]":["QN55%","QN65","QN75"]
                }
            }
     } 
    */
    var fn_frozenWeek = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try{
            let comboList = [];
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let fbWhere = parsedParams.fbParams["where"];
            let fbFilters = parsedParams.fbParams["filters"];
            let itemFilterList = "";
            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";

            let frozenWeek = "";
            //CurrentWeek
            if (vdUtil.fn_getString(frozenWeek) == "") {
                //CurrentWeek로 넘겨줌
                let result = vdCommon.selectQueryList("[CurrentWeek Select]", "Select (&CurrentWeek);");
                frozenWeek = vdCommon.getMember(result.cs, 0, "Time", "Week");
                //vdCommon.debug("[Current]["+frozenWeek+"]" + frozenWeek.Name);
            }

            whereQuery = "Where { [Version].[Version Name].[" + fbVersion + "]";

            if (fbWhere != undefined) {
                for (let key in fbWhere) {
                    if (key == "[Item].[Item]") {
                        //Itme Filter 조건 체크
                        itemFilterList = fn_filterList(fbWhere[key]);
                        if (itemFilterList.length > 0) {
                            itemFilterList = ".filter(" + itemFilterList + ")";
                        }

                    } else {
                        whereQuery += (whereQuery == "" ? "" : ", ") + key + vdUtil.fn_filterStr(fn_dataCheck(fbWhere[key]));
                    }
                }
            };
            whereQuery += ",[Sub Location].[Sub Location]";
            whereQuery += ",[Trans Mode].[Trans Mode]";
            whereQuery += ",(Measure.[BOD Item_asn] >-1)";
            whereQuery += "}";

            dimensionQuery.push('[Item].[Item]'+itemFilterList);
            measureQuery.push("Measure.[BOD Item_Asn]");
            measureQuery.push("Measure.[PLC Mfg_EOP Cur Date]");
            measureQuery.push("Measure.[Dummy]");

            vdCommon.debug("[" + dimensionQuery + "][" + measureQuery + "][" + whereQuery + "]");

            let eopResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "orderby Measure.[PLC Mfg_EOP Cur Date] desc" , "limit 1");
            let eopDate = "";
            let eopWeek = "-";
            if (eopResult.cs.rowCount > 0) {
                eopDate = vdCommon.getMeasureValue(eopResult.cs, 0, "PLC Mfg_EOP Cur Date");
                vdCommon.debug("EOP Cur Date["+eopDate+"]");
                if (vdUtil.fn_getString(eopDate) != "") {
                    eopDate = eopDate.substring(0, 10);
                    //if(eopDate.substring(0,4) == "2028"){
                    //    eopDate = "2027-05-09";
                    //}                    
                    let weekResult = vdCommon.selectQueryList("[Week]", "Select ([Time].[Day].[" + eopDate + "] * [Time].[Week]) on row, () on column;");
                    if(weekResult.cs.rowCount > 0){
                        eopWeek = weekResult.cs.row(0).cell(weekResult.cs.memberColumnIndex("Time", "Week")).Name;
                    }
                }
            };

            comboList.push({ "FROZEN_WEEK": frozenWeek.Name, "EOP_WEEK": eopWeek });

            vdCommon.programEnd();
            return { "Code": 0, "Msg": "", "Rows": comboList };
        }catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /* ********************************************************************************** */
    /*{"fbFuncName" : "fn_filterConstWeek",
        "fbParams":{
            "where": {"[From Week]":"202508", "[To Week]":"202541"}
        }
      }    
    */
    var fn_filterConstWeek= function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let fbWhere = parsedParams.fbParams["where"];
            let fbFromWeek = fbWhere["[From Week]"];
            let fbToWeek = fbWhere["[To Week]"];
            let ibplQuery = '(Measure.[CTN Grp Const_Start Week]>="'+fbFromWeek+'" && Measure.[CTN Grp Const_End Week] <= "'+fbToWeek+'")';    
            ibplQuery += '|| (Measure.[CTN Grp Const_Start Week] >= "'+fbFromWeek+'" && Measure.[CTN Grp Const_End Week] == "-")';
            ibplQuery += '|| (Measure.[CTN Grp Const_Start Week] == "-" && Measure.[CTN Grp Const_End Week] <= "'+fbToWeek+'")';
            ibplQuery += '|| (Measure.[CTN Grp Const_Start Week] == "-" && Measure.[CTN Grp Const_End Week] == "-")';
            ibplQuery += '|| (Measure.[CTN Grp Const_Start Week] == "" && Measure.[CTN Grp Const_End Week] == "")';

            vdCommon.programEnd();                          
            return { "Code" : 0, "Msg" : "", "Rows" : [{Name : ibplQuery}] };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    /************************************************************************************/
    /*BOD Item 기준으로 Item 속성을 조회함.*/ 
    /* ***********************************************************************************/
    //{ "fbFuncName" : "fn_cb_siteMF" }
    var fn_cb_siteMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            vdCommon.printParams(parsedParams);

		    var dims = ['&MFStageSETLocation'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = vdUtil.fn_addIncludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], vdUtil.fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField,
                                                    includeProperty : parsedParams.fbParams.includeProperty,
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    existHyphen : parsedParams.fbParams.existHyphen});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    /* ***********************************************************************************/
    /* {"fbFuncName" : "fn_cb_product_bodItem",
     "fbParams":{"version":"CWV_MP", "existAll":true,
                "where":{
                    "[Location].[Location]":"P306",
                    "[Item].[Product Group]":["TV","AV"]
                 }
                }
     } */
     var fn_cb_product_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let comboList = [];
            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";

            //dimensionQuery.push('[Item].[Product].filter(~(#.Name in {"All", "-"}))');
            dimensionQuery.push('&NSUIItemStd2View.relatedmembers([Product]).filter(#.Name != "-")');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            vdCommon.debug("[" + dimensionQuery + "][" + measureQuery + "][" + whereQuery + "]");

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {
                            DimName: "Item", DimAttbName: "Product", Sort: "DisplayName",
                            existAll: parsedParams.fbParams.existAll,isDisplayNameWithCode: false});

            vdCommon.programEnd();
            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };
    /* ***********************************************************************************/
    /* {"fbFuncName" : "fn_cb_seriesName_bodItem", 
     "fbParams":{"version":"CWV_MP", "existAll":true,
                 "where":{
                          "[Location].[Location]":"P306",
                          "[Item].[Product Group]":["TV","AV"],
                          "[Item].[Product]":"All",
                          "[Item].[Project]":["QN80FE","QN85DD"]
                         }
                } 
     }*/
     var fn_cb_seriesName_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let comboList = [];
            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];

            dimensionQuery.push('&NSUIItemSeriesNameView.filter(#.Name != "-")');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {
                DimName: "Item", DimAttbName: "Series Name", Sort: "DisplayName",
                existAll: parsedParams.fbParams.existAll,
                isDisplayNameWithCode: false
            });

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /* ***********************************************************************************/
    /*{ "fbFuncName" : "fn_cb_ctn_bodItem", 
     "fbParams":{"version":"CWV_MP", "existAll":true,
                "where":{
                          "[Location].[Location]":"P306",
                          "[Item].[Product Group]":["TV","AV"],
                          "[Item].[Product]":"All",
                          "[Item].[Project]":["QN80FE","QN85DD"],
                          "[Item].[Series Name]":"All",
                          "[Item].[Marketing Name]":"All",
                          "[Item].[Inch]":"All"
                }
        } 
     }*/
     var fn_cb_ctn_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let comboList = [];
            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];

            dimensionQuery.push('&NSUIItemCTNView.filter(#.Name != "-")');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {
                DimName: "Item", DimAttbName: "CTN", Sort: "DisplayName",
                existAll: parsedParams.fbParams.existAll,
                isDisplayNameWithCode: false
            });

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /* ********************************************************************************** */
    /* {"fbFuncName" : "fn_cb_inch_bodItem", 
    "fbParams" : { "version":"CWV_MP", "existAll":true,
                    "where":{ "[Location].[Location]":"P306",
                                "[Item].[Product Group]" : "TV",
                                "[Sales Domain].[GC]" : ["226","205"],
                                "[Sales Domain].[AP2]" : ["300723","300122"]
                           }
                } 
    } */
	var fn_cb_inch_bodItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            let comboList = [];
            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];

            dimensionQuery.push('&NSUIItemInchView.filter(#.Name >= "0" && #.Name <= "9")');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {
                    DimName: "Item", DimAttbName: "Inch", Sort: "DisplayName",
                    existAll: parsedParams.fbParams.existAll,
                    isDisplayNameWithCode: false
            });

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    /************************************************************************************/
    /* {"fbFuncName" : "fn_cb_project_bodItem", 
    "fbParams" : { "version":"CWV_MP", "existAll":true,
                    "where":{ "[Location].[Location]":"P306",
                                "[Item].[Product Group]" : "TV",
                                "[Sales Domain].[GC]" : ["226","205"],
                                "[Sales Domain].[AP2]" : ["300723","300122"],
                                "[Item].[Inch]":["All","50"]
                           }
                } 
    } */
    var fn_cb_project_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let comboList = [];
            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];

            dimensionQuery.push('[Item].[Project].filter(#.Name != "-").relatedmembers([Project])');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {
                DimName: "Item", DimAttbName: "Project", Sort: "DisplayName",
                existAll: parsedParams.fbParams.existAll,
                isDisplayNameWithCode: false
            });

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /************************************************************************************/
    /* {"fbFuncName" : "fn_cb_setYear_bodItem", 
    "fbParams" : { "version":"CWV_MP", "existAll":true,
                    "where":{ "[Location].[Location]":"P306",
                                "[Item].[Product Group]" : "TV",
                                "[Sales Domain].[GC]" : ["226","205"],
                                "[Sales Domain].[AP2]" : ["300723","300122"],
                                "[Item].[Inch]":["All","50"],
                                "[Item].[Project]":"All"
                           }
                } 
    } */
    var fn_cb_setYear_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let comboList = [];
            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];

            dimensionQuery.push('&NSUIItemYearView.filter(#.Name >= "0" && #.Name <= "9")');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "orderby [Item].[Year].Name desc", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, 
                            {DimName: "Item", DimAttbName: "Year", existAll: parsedParams.fbParams.existAll,isDisplayNameWithCode: false
            });

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /************************************************************************************/
    /* {"fbFuncName" : "fn_cb_setMKTName_bodItem", 
    "fbParams" : { "version":"CWV_MP", "existAll":true,
                    "where":{ "[Location].[Location]":"P306",
                                "[Item].[Product Group]" : "TV",
                                "[Sales Domain].[GC]" : ["226","205"],
                                "[Sales Domain].[AP2]" : ["300723","300122"],
                                "[Item].[Inch]":["All","50"],
                                "[Item].[Project]":"All",
                                "[Item].[Year]":"All"
                           }
                } 
    } */
    var fn_cb_setMKTName_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let comboList = [];
            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];

            dimensionQuery.push('&NSUIItemMarketingNameView.filter(#.Name != "-").relatedmembers([Marketing Name])');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "orderby [Item].[Marketing Name].Name", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, 
                            {DimName: "Item", DimAttbName: "Marketing Name", existAll: parsedParams.fbParams.existAll,isDisplayNameWithCode: false
            });

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /* ********************************************************************************** */
    /* {"fbFuncName" : "fn_cb_setItem_bodItem",
         "fbParams":{"version":"CWV_MP",
                    "where":{"[Location].[Location]":"P306",
                            "[Item].[Product Group]":["TV","AV"],
                            "[Item].[Product]":"All",
                            "[Item].[Project]":["QN80FE","QN85DD"],
                            "[Item].[Series Name]":"All",
                            "[Item].[Marketing Name]":"All",
                            "[Item].[Inch]":["55","65","75"],
                            "[Item].[CTN]":"All",
                            "[Item].[Year]":"All"
                    }
                }
        }
    */
    var  fn_cb_setItem_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];

            //BOD List 메져에서 조회함.
            dimensionQuery.push("&SETItemExcludeOPT");

            //MeasureQuery
            measureQuery.push("Measure.[BOD Item_Asn]");

            //Where Query
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            var selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            let comboList = vdCommon.fn_makeCombo(selectResult, { DimName: "Item", DimAttbName: "Item", 
                                                    existAll: parsedParams.fbParams.existAll, Sort: "DisplayName", isDisplayNameWithCode: false });

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /* ********************************************************************************** */
    /* {"fbFuncName" : "fn_cb_setExceptItem_bodItem",
         "fbParams":{"version":"CWV_MP",
                    "where":{"[Location].[Location]":"P306",
                            "[Item].[Product Group]":["TV","AV"],
                            "[Item].[Product]":"All",
                            "[Item].[Project]":["QN80FE","QN85DD"],
                            "[Item].[Series Name]":"All",
                            "[Item].[Marketing Name]":"All",
                            "[Item].[Inch]":["55","65","75"],
                            "[Item].[CTN]":"All",
                            "[Item].[Year]":"All",
                            "[Item].[Item]":["QN55%","QN65","QN75"]
                    }
                }
     }
    */
    var fn_cb_setExceptItem_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            vdCommon.debug("1.[fn_cb_setExceptItem_bodItem]" + JSON.stringify(parsedParams));
            let whereQuery = "";
            let dimensionQuery = [];
            let measureQuery = [];
            let itemFilterList = "";
            let fbWhereParam = parsedParams.fbParams["where"];
            let newWhereParam = {};
            parsedParams.fbParams["where"] = "";

            //Item 조건은 Where Query 에서 제외시켜야함.
            for (let key in fbWhereParam) {
                if (key == "[Item].[Item]") {
                    itemFilterList = fn_filterList(fbWhereParam[key]);
                    if (itemFilterList.length > 0) {
                        itemFilterList = ".filter(" + itemFilterList + ")";
                    }                
                }else{
                    newWhereParam[key] = fbWhereParam[key];
                }
            }
            parsedParams.fbParams["where"] = newWhereParam;
            //Where Query
            //return {"whereQuery" : whereQuery, "itemFilter" : itemFilterList};
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            //BOD List 메져에서 조회함.
            dimensionQuery.push("&SETItemExcludeOPT"+itemFilterList);
            //MeasureQuery
            measureQuery.push("Measure.[BOD Item_Asn]");

            var selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            let comboList = vdCommon.fn_makeCombo(selectResult, { DimName: "Item", DimAttbName: "Item", existAll: parsedParams.fbParams.existAll, Sort: "DisplayName", isDisplayNameWithCode: false });
            
            vdCommon.programEnd();
            
            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /* ********************************************************************************** */
    /* {"fbFuncName" : "fn_cb_salesGC_bodItem",
     "fbParams":{"version":"CWV_MP", "existAll":true,
                "where":{
                    "[Location].[Location]":"P306",
                    "[Item].[Product Group]":["TV","AV"],
                    "[Item].[Product]":"All",
                    "[Item].[Project]":["QN80FE","QN85DD"],
                    "[Item].[Series Name]":"All",
                    "[Item].[Marketing Name]":"All",
                    "[Item].[Inch]":"All",
                    "[Item].[CTN]":"All",
                    "[Item].[Year]":"All",
                    "[Item].[Item]":["QN55%","QN65","QN75"]
                    }
                }
     } 
     */
     var fn_cb_salesGC_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let comboList = [];
            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";

            dimensionQuery.push('[Sub Location].[Sub Location GC].filter(#.Name != "-")');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            vdCommon.debug("[" + dimensionQuery + "][" + measureQuery + "][" + whereQuery + "]");

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {
                            DimName: "Sub Location", DimAttbName: "Sub Location GC", Sort: "DisplayName",
                            existAll: false,isDisplayNameWithCode: false});

            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Sales Domain GC에서 다시 조회함.
            let arrayGC = comboList.map((value) => value.Name);
            vdCommon.debug("arrayGC : " + JSON.stringify(arrayGC));
            //Sales Domain에서 조회함.
            //let salesDomainSelect = vdCommon.selectList(["[Sales Domain].[GC]"+vdUtil.fn_filterStr(arrayGC)], [], "", "", parsedParams.fbParams.limit);
            if(arrayGC.length == 0){
                return { "Code": 0, "Msg": "", "Rows": comboList };
            }
            let salesDomainSelect = vdCommon.selectList(["&NSUISalesStd1View.relatedmembers([GC])"+vdUtil.fn_filterStr(arrayGC)], [], "", "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(salesDomainSelect, {
                    DimName: "Sales Domain", DimAttbName: "GC", Sort: "DisplayName",
                    existAll: parsedParams.fbParams.existAll, isDisplayNameWithCode: false});
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    }
    /* ********************************************************************************** */
    /* {"fbFuncName" : "fn_cb_salesAP2_bodItem",
     "fbParams":{"version":"CWV_MP", "existAll":true,
                "where":{
                    "[Location].[Location]":"P306",
                    "[Item].[Product Group]":["TV","AV"],
                    "[Item].[Product]":"All",
                    "[Item].[Project]":["QN80FE","QN85DD"],
                    "[Item].[Series Name]":"All",
                    "[Item].[Marketing Name]":"All",
                    "[Item].[Inch]":["55","66","75"],
                    "[Item].[CTN]":"All",
                    "[Item].[Year]":"All",
                    "[Item].[Item]":["%55QN%","QN65%","QN75%"],
                    "[Sales Domain].[GC]":"All"
                    }
                }
     } 
     */
    var fn_cb_salesAP2_bodItem = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            let comboList = [];
            let dimensionQuery = [];
            let measureQuery = [];
            let whereQuery = "";

            dimensionQuery.push('[Sub Location].[Sub Location Rep AP2].filter(#.Name != "-")');
            measureQuery.push("Measure.[BOD Item_asn]");
            whereQuery = lfn_makeWhere_bodItem(parsedParams);

            let selectResult = vdCommon.selectList(dimensionQuery, measureQuery, whereQuery, "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(selectResult, {
                        DimName: "Sub Location", DimAttbName: "Sub Location Rep AP2", Sort: "DisplayName",
                        existAll: false, isDisplayNameWithCode: false});

            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Sales Domain AP2에서 다시 조회함.
            let arrayAP2 = comboList.map((value) => value.Name);
            vdCommon.debug("arrayAP2 : " + JSON.stringify(arrayAP2));
            //Sales Domain에서 조회함.
            if(arrayAP2.length == 0){
                comboList.push({ Name: "All", DisplayName: "All" });
                return { "Code": 0, "Msg": "", "Rows": comboList };
            }
            let salesDomainSelect = vdCommon.selectList(["&NSUISalesStd2View.relatedmembers([AP2])"+vdUtil.fn_filterStr(arrayAP2)], [], "", "", parsedParams.fbParams.limit);
            comboList = vdCommon.fn_makeCombo(salesDomainSelect, {
                    DimName: "Sales Domain", DimAttbName: "AP2", Sort: "DisplayName",
                    existAll: parsedParams.fbParams.existAll, isDisplayNameWithCode: false});
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": comboList };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };
    /*************************************************************************************/
    /******************** Start: fn_save 관련 함수 ****************************************/

    var fn_description = function (rowData) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            let sDescription = "";
            let sLocation = "";
            let description = [];
            let fbLocation = rowData["Measure.[CTN Grp Const_From Site ID]"];

            if(fbLocation.toString().toUpperCase().indexOf("ALL") != -1){
                sDescription += "";
            }else{
                var arrayLocation = fbLocation.split("^");
                var result = vdCommon.selectList(["Location.[Location]" + vdUtil.fn_filterStr(arrayLocation)], [], "", "", "");
                for(var i = 0; i < result.cs.rowCount ; i++){                    
                    var valueName = vdCommon.getPropertyValue(result.cs, i, "Location", "Location", "Location Site ID");
                    var valueCode  = vdCommon.getMember(result.cs, i, "Location", "Location")
                    sLocation += ( sLocation == "" ? "" : "^" ) + valueName+"("+valueCode.Name+")";
                }
                sDescription += sLocation ;
            }
            
            let fbItemDesc = rowData["Measure.[CTN Grp Const_Item Description]"];
    
            if(fbItemDesc != "" && fbItemDesc != undefined && fbItemDesc != null){
                sDescription = fbItemDesc ;
            }else{       
                description.push("Measure.[CTN Grp Const_Product Grp]");
                description.push("Measure.[CTN Grp Const_Product]");
                description.push("Measure.[CTN Grp Const_Project]");
                description.push("Measure.[CTN Grp Const_Series]");
                description.push("Measure.[CTN Grp Const_MKT Name]");
                description.push("Measure.[CTN Grp Const_Inch]");
                description.push("Measure.[CTN Grp Const_Item CTN Attr]");
                description.push("Measure.[CTN Grp Const_Year]");
                description.push("Measure.[CTN Grp Const_Item]");
                description.push("Measure.[CTN Grp Const_GC]");
                description.push("Measure.[CTN Grp Const_AP2]");
                
                for(var k=0; k < description.length ; k++ ){
                    var value = rowData[description[k]]
                    if(value.toString().toUpperCase().indexOf("ALL") != -1){
                        sDescription += "";
                    }else{
                        //sDescription += value + " ";
                        sDescription += ( sDescription == "" ? "" : "," ) + value;
                    }
                }
            }
            
            //sDescription = sDescription.replace(/ /g, ",");
            return sDescription;
            
        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };

    /* 2026.01.15 :  CTN Group ID 채번 */ 
    var fn_ctn_groupId = function(pVersion){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            
            let fbGroupID ="";
            let dimension = [];
            let measure = [];

            dimension.push("[Version].[Version Name].["+pVersion+"]");
            dimension.push("[Group].[Group ID].filter(#.Name startswith([MCT_]))");

            measure.push("Measure.[CTN Grp Const_From Site ID]");
            measure.push("Measure.[CTN Grp Const_Created By]"); 
            measure.push("Measure.[CTN Grp Const_Creation Time]");             
            measure.push("Measure.[CTN Grp Const_Update Time]"); 
            measure.push("Measure.[CTN Grp Const_Updated By]");

            let resultData = vdCommon.selectList(dimension, measure, "", "orderby [Group].[Group ID].Name desc", "limit 1");

            if(resultData.cs.rowCount > 0){
                fbGroupID = resultData.cs.row(0).cell(resultData.cs.memberColumnIndex("Group", "Group ID")).Name; 
                fbGroupID = String(fbGroupID).substring(4, 9); //ex) PAC_00001 => 00001 자르기
                fbGroupID =  parseInt(fbGroupID) + 1 ;
                fbGroupID = "MCT_" + String(fbGroupID).padStart(5, "0") ;
            }else{
                fbGroupID = "MCT_00001";
            }          

            //Member 등록여부 확인
            var memberSql = "[Group].[Group ID] ";
            if (!vdCommon.existMember(memberSql, fbGroupID) ) {
                vdCommon.createMember(memberSql, fbGroupID);
            }
            return fbGroupID;
        }catch(e){
            return -1;
        }
    };
    
    var fn_validation_OLD = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            let errorCnt1 = 0;
            let errorMsg1 = "Error : Duplicated Intersection(s)";
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");

            for (var i = 0; i < parsedParams.fbGridRows.length; i++) {
                let rows = parsedParams.fbGridRows[i]
                let rowStatus = rows["rowstatus"];
                
                rows["rowmsg"] = "";
                rows["errorflag"] = "";

                let chkFlag = false;
                if (rowStatus == "C") {

                    let selectQuery = "Select ([Version].[Version Name].["+fbVersion+"] * [Group].[Group ID] ) on row,";
                    selectQuery += " ({Measure.[CTN Grp Const_From Site]}) on column ";
                    selectQuery += 'Where{ Measure.[CTN Grp Const_From Site ID] == "'+rows["Measure.[CTN Grp Const_From Site ID]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_GC Code] == "'+rows["Measure.[CTN Grp Const_GC Code]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_AP2 Code] == "'+rows["Measure.[CTN Grp Const_AP2 Code]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Product Grp] == "'+rows["Measure.[CTN Grp Const_Product Grp]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Product] == "'+rows["Measure.[CTN Grp Const_Product]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Project] == "'+rows["Measure.[CTN Grp Const_Project]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Series] == "'+rows["Measure.[CTN Grp Const_Series]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_MKT Name] == "'+rows["Measure.[CTN Grp Const_MKT Name]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Inch] == "'+rows["Measure.[CTN Grp Const_Inch]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Item CTN Attr] == "'+rows["Measure.[CTN Grp Const_Item CTN Attr]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Year] == "'+rows["Measure.[CTN Grp Const_Year]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Item] == "'+rows["Measure.[CTN Grp Const_Item]"]+'"';
                    selectQuery += ' ,Measure.[CTN Grp Const_Except Item] == "'+rows["Measure.[CTN Grp Const_Except Item]"]+'"';
                    selectQuery += "};";

                    
                    let result = vdCommon.selectQueryList('CTN Grp Duplicated Check', selectQuery);

                    if(result.cs.rowCount > 0){
                        errorCnt1++;
                        rows["rowmsg"] = errorMsg1;
                        rows["errorflag"] = "ERROR";
                    }
                }
            };

            let errorMsg = "";
            if(errorCnt1 > 0){
                errorMsg += (errorMsg == "" ? "" : " ")  + errorMsg1 ;
                //Error Row만 Return 함.
                let checkGridRows = parsedParams.fbGridRows;
                const errorRows = checkGridRows.filter((checkGridRows)=>{return checkGridRows.errorflag === "ERROR"});
                parsedParams.fbGridRows = errorRows;

                return { "Code" : -1, "Msg" : errorMsg, "Rows" : parsedParams.fbGridRows };
            }

            return { "Code": 0, "Msg": "" };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };
    var fn_save_OLD = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {
            //Validation 체크
            let errorData = fn_validation(parsedParams);
            if(errorData.Code == -1){
                return errorData;
            }

            for (var i = 0; i < parsedParams.fbGridRows.length; i++) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbVersion = parsedParams.fbGridRows[i]["[Version].[Version Name]"];
                let fbLocation = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_From Site ID]"];
                let fbItemDesc = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Item Description]"];
                let fbProductGrp = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Product Grp]"];
                let fbProduct = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Product]"];
                let fbProject = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Project]"];
                let fbSeriesName = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Series]"];
                let fbMKTName = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_MKT Name]"];
                let fbInch = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Inch]"];
                let fbCTNAttr = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Item CTN Attr]"];
                let fbYear = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Year]"];
                let fbItem = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Item]"];
                let fbExceptItem = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Except Item]"];
                let fbApplyFlag = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Apply Flag]"];
                let fbFrozenWeek = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Frozen Week]"];
                let fbStartWeek = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Start Week]"];
                let fbEndWeek = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_End Week]"];
                let fbGCID = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_GC Code]"];
                let fbGC = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_GC]"];
                let fbAP2ID = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_AP2 Code]"];
                let fbAP2 = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_AP2]"];
                let fbSOPQty = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Frozen SOP Override Qty]"];
                let fbSOPReason = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_Frozen SOP Override Reason]"];
                // 26.01.15 추가
                let fbEOPMax = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_EOP MAX]"];
                let fbAP2Cap = parsedParams.fbGridRows[i]["Measure.[CTN Grp Const_AP2 Cap]"];
                let fbGroupID = "";

                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                //Site Name 조회
                var result = vdCommon.selectList(['&MFStageSETLocation.filter(#.Name == "'+fbLocation+'")'], [], "", "", "");
                let fbLocationName = vdCommon.getPropertyValue(result.cs, 0, "Location", "Location", "Location Site ID");
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                let dimension = [];
                let measure = [];
                
                if(fbItemDesc.length == 0){
                    fbItemDesc = fn_description(parsedParams.fbGridRows[i])
                }
                
                measure.push('Measure.[CTN Grp Const_From Site ID] = "' + fbLocation + '";');
                measure.push('Measure.[CTN Grp Const_From Site] = "' + fbLocationName + '";');
                measure.push('Measure.[CTN Grp Const_Item Description] = "' + fbItemDesc + '";');
                measure.push('Measure.[CTN Grp Const_Product Grp] = "' + fbProductGrp + '";');
                measure.push('Measure.[CTN Grp Const_Product] = "' + fbProduct + '";');
                measure.push('Measure.[CTN Grp Const_Project] = "' + fbProject + '";');
                measure.push('Measure.[CTN Grp Const_Series] = "' + fbSeriesName + '";');
                measure.push('Measure.[CTN Grp Const_MKT Name] = "' + fbMKTName + '";');
                measure.push('Measure.[CTN Grp Const_Inch] = "' + fbInch + '";');
                measure.push('Measure.[CTN Grp Const_Item CTN Attr] = "' + fbCTNAttr + '";');
                measure.push('Measure.[CTN Grp Const_Year] = "' + fbYear + '";');
                measure.push('Measure.[CTN Grp Const_Item] = "' + fbItem + '";');
                measure.push('Measure.[CTN Grp Const_Except Item] = "' + fbExceptItem + '";');
                measure.push('Measure.[CTN Grp Const_Apply Flag] = "' + vdUtil.fn_getString(fbApplyFlag) + '";');
                measure.push('Measure.[CTN Grp Const_Frozen Week] = "' + vdUtil.fn_getString(fbFrozenWeek) + '";');
                measure.push('Measure.[CTN Grp Const_Start Week] = "' + vdUtil.fn_getString(fbStartWeek) + '";');
                //End Week
                measure.push('Measure.[CTN Grp Const_End Week] = "' + vdUtil.fn_getString(fbEndWeek) + '";');  
                //GC
                measure.push('Measure.[CTN Grp Const_GC Code] = "' + vdUtil.fn_getString(fbGCID) + '";');
                let strGCist = "";
                if (fbGC == "" || fbGC == undefined) {
                    let gcList = fbGCID.split("^");
                    for (var k = 0; k < gcList.length; k++) {
                        strGCist += (strGCist == "" ? "" : "^") + vdCommon.fn_getCodeName("[Sales Domain].[GC]", gcList[k]);
                    }
                    measure.push('Measure.[CTN Grp Const_GC] = "' + strGCist + '";');

                } else {
                    measure.push('Measure.[CTN Grp Const_GC] = "' + (fbGC == "All" ? "All" : fbGC) + '";');
                }
                //AP2
                measure.push('Measure.[CTN Grp Const_AP2 Code] = "' + vdUtil.fn_getString(fbAP2ID) + '";');

                let strAP2ist = "";
                if (fbAP2 == "" || fbAP2 == undefined) {
                    let ap2List = fbAP2ID.split("^");
                    for (var k = 0; k < ap2List.length; k++) {
                        strAP2ist += (strAP2ist == "" ? "" : "^") + vdCommon.fn_getCodeName("[Sales Domain].[AP2]", ap2List[k]);
                    }
                    measure.push('Measure.[CTN Grp Const_AP2] = "' + strAP2ist + '";');

                } else {
                    measure.push('Measure.[CTN Grp Const_AP2] = "' + (fbAP2 == "All" ? "All" : fbAP2) + '";');
                }

                if (fbSOPQty != undefined) {
                    measure.push('Measure.[CTN Grp Const_Frozen SOP Override Qty] = ' + fbSOPQty + ';');
                }
                if (fbSOPReason != undefined) {
                    measure.push('Measure.[CTN Grp Const_Frozen SOP Override Reason] = "' + fbSOPReason + '";');
                }
                //-------------------------------------------------------------------------------
                //26.01.19 추가 메져 처리
                measure.push('Measure.[CTN Grp Const_EOP MAX] = "'+fbEOPMax +'";');
                measure.push('Measure.[CTN Grp Const_AP2 Cap] = "'+fbAP2Cap +'";');
                //-------------------------------------------------------------------------------
                measure.push('Measure.[CTN Grp Const_Updated By] = CurrentUser().[User Name];');
                measure.push('Measure.[CTN Grp Const_Update Time] = Now();');

                if (rowStatus == "C") {
                    //신규 GroupID 생성
                    fbGroupID = fn_ctn_groupId(fbVersion);
                    dimension.push('[Version].[Version Name].[' + fbVersion + ']');
                    dimension.push('[Group].[Group ID].[' + fbGroupID + ']');

                    measure.push('Measure.[CTN Grp Const_Created By] = CurrentUser().[User Name];');
                    measure.push('Measure.[CTN Grp Const_Creation Time] = Now();');

                    vdCommon.createMeasure(dimension, measure);

                } else if (rowStatus == "U") {
                    //Update
                    fbGroupID = parsedParams.fbGridRows[i]["[Group].[Group ID]"];

                    dimension.push('[Version].[Version Name].[' + fbVersion + ']');
                    dimension.push('[Group].[Group ID].[' + fbGroupID + ']');

                    vdCommon.updateMeasure(dimension, measure);
                }else if(rowStatus == "D"){
                    fbGroupID = parsedParams.fbGridRows[i]["[Group].[Group ID]"];
                    
                    let deleteWhere = [];
                    deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                    deleteWhere.push("[Group].[Group ID].["+fbGroupID+"]");                    
    
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const");
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Ecp");
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Filter");//2026.01.15 추가함.
                }

                /*******************************************************************************/
                //CTN Grp Const Filter 처리
                /*******************************************************************************/
                if (rowStatus != "D") {
                    dimension = [];
                    measure = [];

                    if(rowStatus == "U"){
                        //수정상태인 경우는 기존 데이타를 삭제 후 Create 시킴.
                        let deleteWhere = [];
                        deleteWhere.push('[Version].[Version Name].['+fbVersion+']');
                        deleteWhere.push('[Group].[Group ID].['+fbGroupID+']');

                        vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Filter");
                    }

                    dimension.push("[Sub Location].[Sub Location Rep AP2]"+ vdUtil.fn_filterStr(fn_dataCheck(fbAP2ID)));            
                    dimension.push("[Item].[Item Std1]"+vdUtil.fn_filterStr(fn_dataCheck(fbProductGrp)));

                    measure.push("Measure.[BOD Item_asn]");

                    let whereQuery = 'Where {[Version].[Version Name].['+fbVersion+']';
                    whereQuery += ',[Location].[Location]' + vdUtil.fn_filterStr(fn_dataCheck(fbLocation));
                    whereQuery += ',[Item].[Item]'//+ (fbItemList.length > 0 ? '.filter('+fbItemList+')':'');
                    //whereQuery += ",[Item].[Project]"+ vdUtil.fn_filterStr(fn_dataCheck(fbProject));
                    //whereQuery += ",[Item].[Marketing Name]"+ vdUtil.fn_filterStr(fn_dataCheck(fbMarketingName));
                    //whereQuery += ",[Item].[Inch]"+ vdUtil.fn_filterStr(fn_dataCheck(fbInch));
                    //whereQuery += ",[Item].[Year]"+ vdUtil.fn_filterStr(fn_dataCheck(fbYear));
                    whereQuery += ',&NSUISubLocationDC';
                    whereQuery += ',[Sub Location].[Sub Location GC]'+ vdUtil.fn_filterStr(fn_dataCheck(fbGCID));
                    whereQuery += ',[Trans Mode].[Trans Mode]';
                    whereQuery += ',(Measure.[BOD Item_asn] >-1)';
                    whereQuery += '}';

                    let result= vdCommon.selectList(dimension, measure, whereQuery, '', '');

                    for(var k = 0; k < result.cs.rowCount; k++){
                        dimension = [];
                        measure = [];

                        dimension.push('[Version].[Version Name].['+fbVersion+']');
                        dimension.push('[Location].[Location].['+fbLocation+']');
                        dimension.push('[Sales Domain].[AP2].['+result.cs.row(k).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location Rep AP2")).Name+']');
                        dimension.push('[Group].[Group ID].['+fbGroupID+']');
                        dimension.push('[Item].[Item Std1].['+result.cs.row(k).cell(result.cs.memberColumnIndex("Item", "Item Std1")).Name+']');

                        measure.push('Measure.[CTN Grp Const Filter_Asn] = "1";');

                        vdCommon.createMeasure(dimension, measure);                    
                    }
                    /*******************************************************************************/
                }

                /*******************************************************************************/
                //26.01.26 한재현프로님, 이재연위원님 요구 => Apply Flag가 "Y"인 경우.. 
                if (rowStatus != "D" && fbApplyFlag == "Y") {
                    //파이썬 호출 전 데이타 삭제함.
                    let deleteWhere = [];
                    deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                    deleteWhere.push("[Group].[Group ID].["+fbGroupID+"]");
   
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Ecp");
                    //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    //파이썬 호출 : Item 별로
                    let filterList = "";
                    let execQuery = 'EXEC plugin instance [PY_UI_CTNMgmt] for measures {[CTN Grp Const_From Site]} '
                    execQuery += 'using scope ([Version].[Version Name].[' + fbVersion + '] * [Group].[Group ID].[' + fbGroupID + ']'
                    itemList = fbItem.split("^");
                    vdCommon.debug("<EXEC plugin>"+itemList.length);
                    filterList = fn_filterList(itemList);                    
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Item].filter(" + filterList + ")";
                    }

                    filterList = fn_dataCheck(fbProductGrp.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Product Group]"+ vdUtil.fn_filterStr(filterList);

                    }
                    filterList = fn_dataCheck(fbProduct.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Product]"+ vdUtil.fn_filterStr(filterList);
                    }
                    
                    filterList = fn_dataCheck(fbSeriesName.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Series Name]"+ vdUtil.fn_filterStr(filterList);
                    }

                    filterList = fn_dataCheck(fbMKTName.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Marketing Name]"+ vdUtil.fn_filterStr(filterList);
                    }

                    filterList = fn_dataCheck(fbInch.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Inch]"+ vdUtil.fn_filterStr(filterList);
                    }

                    filterList = fn_dataCheck(fbCTNAttr.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[CTN]"+ vdUtil.fn_filterStr(filterList);
                    } 

                    filterList = fn_dataCheck(fbYear.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Year]"+ vdUtil.fn_filterStr(filterList);
                    }
                    
                    execQuery += ')';
                    execQuery += 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False")';
                    execQuery += ',(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;';

                    vdCommon.printStep("[" + programName + "] EXEC Python Call SQL>>" + execQuery);
                    vdCommon.executeQuery("PY_UI_CTNItemConst ", execQuery);
                }
            }

            vdCommon.programEnd();

            return { "Code": 0, "Msg": "", "Rows": "" };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };
    /* {"fbFuncName" : "fn_save",
    "fbParams": {"version":"CWV_MP"},
    "fbGridRows" : [
    {"rowstatus":"C"
    , "rowindex":2
        ,"[Group].[Group ID]" : ""
        ,"[Version].[Version Name]" : "CWV_MP"
        ,"Measure.[CTN Grp Const_From Site ID]": "P306"
        ,"Measure.[CTN Grp Const_Item Description]" : "TEST_250912"
        ,"Measure.[CTN Grp Const_Product Grp]" : "TV"
        ,"Measure.[CTN Grp Const_Product]" : "All"
        ,"Measure.[CTN Grp Const_Project]" : "All"
        ,"Measure.[CTN Grp Const_Series]" : "All"
        ,"Measure.[CTN Grp Const_MKT Name]" : "All"
        ,"Measure.[CTN Grp Const_Inch]" : "All"
        ,"Measure.[CTN Grp Const_Item CTN Attr]" : "All"
        ,"Measure.[CTN Grp Const_Year]" : "All"
        ,"Measure.[CTN Grp Const_Item]" : "All"
        ,"Measure.[CTN Grp Const_Except Item]" : "All"
        ,"Measure.[CTN Grp Const_Apply Flag]" : "Y"
        ,"Measure.[CTN Grp Const_Frozen Week]" : "202509"
        ,"Measure.[CTN Grp Const_Start Week]" : "202510"
        ,"Measure.[CTN Grp Const_End Week]": "202605"
        ,"Measure.[CTN Grp Const_GC Code]" : "207^203"
        ,"Measure.[CTN Grp Const_GC]" : "LATIN AMERICA^NORTH AMERICA"
        ,"Measure.[CTN Grp Const_AP2 Code]" : "All"
        ,"Measure.[CTN Grp Const_AP2]" : "All"
        ,"Measure.[CTN Grp Const_Frozen SOP Override Qty]": 100
        ,"Measure.[CTN Grp Const_Frozen SOP Override Reason]":"메져변경_TEST"
        ,"Measure.[CTN Grp Const_EOP MAX]":"20260119"
        ,"Measure.[CTN Grp Const_AP2 Cap]":"true"
    }]}
    */
    
    /*2026.03.25 Validation 변경*/
    var fn_validation = function (rows, fbVersion) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let errorMsg1 = "Error : Duplicated Intersection(s)";
            let errorMsg2 = "Error : There is registered Item.";            
            //let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");

            //for (var i = 0; i < parsedParams.fbGridRows.length; i++) {
            let rowStatus = rows["rowstatus"];
            vdCommon.debug("[fn_validationNew(ROWS)]"+ JSON.stringify(rows));
            
            rows["rowmsg"] = "";
            rows["errorflag"] = "";

            if (rowStatus == "C") {
                let selectQuery = "Select ([Version].[Version Name].["+fbVersion+"] * [Group].[Group ID] ) on row,";
                selectQuery += " ({Measure.[CTN Grp Const_From Site]}) on column ";
                selectQuery += 'Where{ Measure.[CTN Grp Const_From Site ID] == "'+rows["Measure.[CTN Grp Const_From Site ID]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_GC Code] == "'+rows["Measure.[CTN Grp Const_GC Code]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_AP2 Code] == "'+rows["Measure.[CTN Grp Const_AP2 Code]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Product Grp] == "'+rows["Measure.[CTN Grp Const_Product Grp]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Product] == "'+rows["Measure.[CTN Grp Const_Product]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Project] == "'+rows["Measure.[CTN Grp Const_Project]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Series] == "'+rows["Measure.[CTN Grp Const_Series]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_MKT Name] == "'+rows["Measure.[CTN Grp Const_MKT Name]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Inch] == "'+rows["Measure.[CTN Grp Const_Inch]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Item CTN Attr] == "'+rows["Measure.[CTN Grp Const_Item CTN Attr]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Year] == "'+rows["Measure.[CTN Grp Const_Year]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Item] == "'+rows["Measure.[CTN Grp Const_Item]"]+'"';
                selectQuery += ' ,Measure.[CTN Grp Const_Except Item] == "'+rows["Measure.[CTN Grp Const_Except Item]"]+'"';
                selectQuery += "};";

                
                let result = vdCommon.selectQueryList('CTN Grp Duplicated Check', selectQuery);

                if(result.cs.rowCount > 0){
                    rows["rowmsg"] = errorMsg1;
                    rows["errorflag"] = "ERROR";
                    return { "Code" : -1, "Msg" : errorMsg1, "Rows" : rows };
                }  
            }

            let testResult = fn_dataCheck(rows["Measure.[CTN Grp Const_Item]"]);
            vdCommon.debug("2." + testResult);
            //Item checking
            let param = ' {"fbFuncName" : "fn_cb_setExceptItem_bodItem",';
            param += '"fbParams":{"version":"'+fbVersion+'",';
            param += '"limit" : "limit 3000",';
            param += '"where":{"[Location].[Location]":"'+rows["Measure.[CTN Grp Const_From Site ID]"]+'",';
            param += '"[Item].[Product Group]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Product Grp]"]))+',';
            param += '"[Item].[Product]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Product]"]))+',';
            param += '"[Item].[Project]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Project]"]))+',';
            param += '"[Item].[Series Name]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Series]"]))+',';
            param += '"[Item].[Marketing Name]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_MKT Name]"]))+',';
            param += '"[Item].[Inch]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Inch]"]))+',';
            param += '"[Item].[CTN]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Item CTN Attr]"]))+',';
            param += '"[Item].[Year]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Year]"]))+',';
            param += '"[Item].[Item]":'+JSON.stringify(fn_dataCheck(rows["Measure.[CTN Grp Const_Item]"]))+'';
            param += "}}}";
            const obj = JSON.parse(param);
            vdCommon.debug("[fn_validationNew]"+JSON.stringify(obj));
            let itemResult = fn_cb_setExceptItem_bodItem(obj);
            let itemList = JSON.parse(JSON.stringify(itemResult.Rows));
            vdCommon.debug("[TypeOf(2)]" +typeof itemList)
            itemList = itemList.map((value) => value.Name);

            //CTN Grp Const Ecp 메져그룹 조회
            let itemCount = 0;
            if(rowStatus == "C"){
                itemCount = vdCommon.selectListCount(
                            ["[Version].[Version Name].["+fbVersion+"]",
                            "[Location].[Location].["+rows["Measure.[CTN Grp Const_From Site ID]"]+"]",
                            "[Group].[Group ID]",
                            "[Item].[Item]"+vdUtil.fn_filterStr(itemList)], 
                            ["Measure.[CTN Grp Const Ecp_Ecp Flag]"], "");
            }else if(rowStatus == "U"){
                let fbGroupID = rows["[Group].[Group ID]"];
                itemCount = vdCommon.selectListCount(
                    ["[Version].[Version Name].["+fbVersion+"]",
                    "[Location].[Location].["+rows["Measure.[CTN Grp Const_From Site ID]"]+"]",
                    '[Group].[Group ID].filter(~(#.Name == "'+fbGroupID+'"))',
                    "[Item].[Item]"+vdUtil.fn_filterStr(itemList)], 
                    ["Measure.[CTN Grp Const Ecp_Ecp Flag]"], "");
            }

            if(itemCount > 0){
                vdCommon.debug("[Msg]" +errorMsg2 );
                rows["rowmsg"] = errorMsg2;
                rows["errorflag"] = "ERROR";
                return { "Code" : -1, "Msg" : errorMsg1, "Rows" : rows };
            }

            return { "Code": 0, "Msg": "" };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };    

    var fn_save = function (parsedParams) {
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try {

            let errorList = [];
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]")

            for (var i = 0; i < parsedParams.fbGridRows.length; i++) {
                let rows = parsedParams.fbGridRows[i];
                let rowStatus = rows["rowstatus"];
                /* */
                if(rowStatus != "D"){
                    let errorData = fn_validation(rows,fbVersion);
                    if(errorData.Code == -1){
                        errorList.push(errorData.Rows);
                        continue;
                    }
                } 
                
                //let fbVersion = rows["[Version].[Version Name]"];
                let fbLocation = rows["Measure.[CTN Grp Const_From Site ID]"];
                let fbItemDesc = rows["Measure.[CTN Grp Const_Item Description]"];
                let fbProductGrp = rows["Measure.[CTN Grp Const_Product Grp]"];
                let fbProduct = rows["Measure.[CTN Grp Const_Product]"];
                let fbProject = rows["Measure.[CTN Grp Const_Project]"];
                let fbSeriesName = rows["Measure.[CTN Grp Const_Series]"];
                let fbMKTName = rows["Measure.[CTN Grp Const_MKT Name]"];
                let fbInch = rows["Measure.[CTN Grp Const_Inch]"];
                let fbCTNAttr = rows["Measure.[CTN Grp Const_Item CTN Attr]"];
                let fbYear = rows["Measure.[CTN Grp Const_Year]"];
                let fbItem = rows["Measure.[CTN Grp Const_Item]"];
                let fbExceptItem = rows["Measure.[CTN Grp Const_Except Item]"];
                let fbApplyFlag = rows["Measure.[CTN Grp Const_Apply Flag]"];
                let fbFrozenWeek = rows["Measure.[CTN Grp Const_Frozen Week]"];
                let fbStartWeek = rows["Measure.[CTN Grp Const_Start Week]"];
                let fbEndWeek = rows["Measure.[CTN Grp Const_End Week]"];
                let fbGCID = rows["Measure.[CTN Grp Const_GC Code]"];
                let fbGC = rows["Measure.[CTN Grp Const_GC]"];
                let fbAP2ID = rows["Measure.[CTN Grp Const_AP2 Code]"];
                let fbAP2 = rows["Measure.[CTN Grp Const_AP2]"];
                let fbSOPQty = rows["Measure.[CTN Grp Const_Frozen SOP Override Qty]"];
                let fbSOPReason = rows["Measure.[CTN Grp Const_Frozen SOP Override Reason]"];
                // 26.01.15 추가
                let fbEOPMax = rows["Measure.[CTN Grp Const_EOP MAX]"];
                let fbAP2Cap = rows["Measure.[CTN Grp Const_AP2 Cap]"];
                let fbGroupID = "";

                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                //Site Name 조회
                var result = vdCommon.selectList(['&MFStageSETLocation.filter(#.Name == "'+fbLocation+'")'], [], "", "", "");
                let fbLocationName = vdCommon.getPropertyValue(result.cs, 0, "Location", "Location", "Location Site ID");
                //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                let dimension = [];
                let measure = [];
                
                if(fbItemDesc.length == 0){
                    fbItemDesc = fn_description(rows)
                }
                
                measure.push('Measure.[CTN Grp Const_From Site ID] = "' + fbLocation + '";');
                measure.push('Measure.[CTN Grp Const_From Site] = "' + fbLocationName + '";');
                measure.push('Measure.[CTN Grp Const_Item Description] = "' + fbItemDesc + '";');
                measure.push('Measure.[CTN Grp Const_Product Grp] = "' + fbProductGrp + '";');
                measure.push('Measure.[CTN Grp Const_Product] = "' + fbProduct + '";');
                measure.push('Measure.[CTN Grp Const_Project] = "' + fbProject + '";');
                measure.push('Measure.[CTN Grp Const_Series] = "' + fbSeriesName + '";');
                measure.push('Measure.[CTN Grp Const_MKT Name] = "' + fbMKTName + '";');
                measure.push('Measure.[CTN Grp Const_Inch] = "' + fbInch + '";');
                measure.push('Measure.[CTN Grp Const_Item CTN Attr] = "' + fbCTNAttr + '";');
                measure.push('Measure.[CTN Grp Const_Year] = "' + fbYear + '";');
                measure.push('Measure.[CTN Grp Const_Item] = "' + fbItem + '";');
                measure.push('Measure.[CTN Grp Const_Except Item] = "' + fbExceptItem + '";');
                measure.push('Measure.[CTN Grp Const_Apply Flag] = "' + vdUtil.fn_getString(fbApplyFlag) + '";');
                measure.push('Measure.[CTN Grp Const_Frozen Week] = "' + vdUtil.fn_getString(fbFrozenWeek) + '";');
                measure.push('Measure.[CTN Grp Const_Start Week] = "' + vdUtil.fn_getString(fbStartWeek) + '";');
                //End Week
                measure.push('Measure.[CTN Grp Const_End Week] = "' + vdUtil.fn_getString(fbEndWeek) + '";');                
                //GC
                measure.push('Measure.[CTN Grp Const_GC Code] = "' + vdUtil.fn_getString(fbGCID) + '";');
                let strGCist = "";
                if (fbGC == "" || fbGC == undefined) {
                    let gcList = fbGCID.split("^");
                    for (var k = 0; k < gcList.length; k++) {
                        strGCist += (strGCist == "" ? "" : "^") + vdCommon.fn_getCodeName("[Sales Domain].[GC]", gcList[k]);
                    }
                    measure.push('Measure.[CTN Grp Const_GC] = "' + strGCist + '";');

                } else {
                    measure.push('Measure.[CTN Grp Const_GC] = "' + (fbGC == "All" ? "All" : fbGC) + '";');
                }
                //AP2
                measure.push('Measure.[CTN Grp Const_AP2 Code] = "' + vdUtil.fn_getString(fbAP2ID) + '";');

                let strAP2ist = "";
                if (fbAP2 == "" || fbAP2 == undefined) {
                    let ap2List = fbAP2ID.split("^");
                    for (var k = 0; k < ap2List.length; k++) {
                        strAP2ist += (strAP2ist == "" ? "" : "^") + vdCommon.fn_getCodeName("[Sales Domain].[AP2]", ap2List[k]);
                    }
                    measure.push('Measure.[CTN Grp Const_AP2] = "' + strAP2ist + '";');

                } else {
                    measure.push('Measure.[CTN Grp Const_AP2] = "' + (fbAP2 == "All" ? "All" : fbAP2) + '";');
                }

                if (fbSOPQty != undefined) {
                    measure.push('Measure.[CTN Grp Const_Frozen SOP Override Qty] = ' + fbSOPQty + ';');
                }
                if (fbSOPReason != undefined) {
                    measure.push('Measure.[CTN Grp Const_Frozen SOP Override Reason] = "' + fbSOPReason + '";');
                }
                //-------------------------------------------------------------------------------
                //26.01.19 추가 메져 처리
                measure.push('Measure.[CTN Grp Const_EOP MAX] = "'+fbEOPMax +'";');
                measure.push('Measure.[CTN Grp Const_AP2 Cap] = "'+fbAP2Cap +'";');
                //-------------------------------------------------------------------------------
                measure.push('Measure.[CTN Grp Const_Updated By] = CurrentUser().[User Name];');
                measure.push('Measure.[CTN Grp Const_Update Time] = Now();');

                if (rowStatus == "C") {
                    //신규 GroupID 생성
                    fbGroupID = fn_ctn_groupId(fbVersion);
                    dimension.push('[Version].[Version Name].[' + fbVersion + ']');
                    dimension.push('[Group].[Group ID].[' + fbGroupID + ']');

                    measure.push('Measure.[CTN Grp Const_Created By] = CurrentUser().[User Name];');
                    measure.push('Measure.[CTN Grp Const_Creation Time] = Now();');

                    vdCommon.createMeasure(dimension, measure);

                } else if (rowStatus == "U") {
                    //Update
                    fbGroupID = rows["[Group].[Group ID]"];

                    dimension.push('[Version].[Version Name].[' + fbVersion + ']');
                    dimension.push('[Group].[Group ID].[' + fbGroupID + ']');

                    vdCommon.updateMeasure(dimension, measure);
                }else if(rowStatus == "D"){
                    fbGroupID = rows["[Group].[Group ID]"];
                    
                    let deleteWhere = [];
                    deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                    deleteWhere.push("[Group].[Group ID].["+fbGroupID+"]");                    
    
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const");
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Ecp");
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Filter");//2026.01.15 추가함.
                }

                /*******************************************************************************/
                //CTN Grp Const Filter 처리
                /*******************************************************************************/
                if (rowStatus != "D") {
                    dimension = [];
                    measure = [];

                    if(rowStatus == "U"){
                        //수정상태인 경우는 기존 데이타를 삭제 후 Create 시킴.
                        let deleteWhere = [];
                        deleteWhere.push('[Version].[Version Name].['+fbVersion+']');
                        deleteWhere.push('[Group].[Group ID].['+fbGroupID+']');

                        vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Filter");
                    }

                    dimension.push("[Sub Location].[Sub Location Rep AP2]"+ vdUtil.fn_filterStr(fn_dataCheck(fbAP2ID)));            
                    dimension.push("[Item].[Item Std1]"+vdUtil.fn_filterStr(fn_dataCheck(fbProductGrp)));

                    measure.push("Measure.[BOD Item_asn]");

                    let whereQuery = 'Where {[Version].[Version Name].['+fbVersion+']';
                    whereQuery += ',[Location].[Location]' + vdUtil.fn_filterStr(fn_dataCheck(fbLocation));
                    whereQuery += ',[Item].[Item]'//+ (fbItemList.length > 0 ? '.filter('+fbItemList+')':'');
                    //whereQuery += ",[Item].[Project]"+ vdUtil.fn_filterStr(fn_dataCheck(fbProject));
                    //whereQuery += ",[Item].[Marketing Name]"+ vdUtil.fn_filterStr(fn_dataCheck(fbMarketingName));
                    //whereQuery += ",[Item].[Inch]"+ vdUtil.fn_filterStr(fn_dataCheck(fbInch));
                    //whereQuery += ",[Item].[Year]"+ vdUtil.fn_filterStr(fn_dataCheck(fbYear));
                    whereQuery += ',&NSUISubLocationDC';
                    whereQuery += ',[Sub Location].[Sub Location GC]'+ vdUtil.fn_filterStr(fn_dataCheck(fbGCID));
                    whereQuery += ',[Trans Mode].[Trans Mode]';
                    whereQuery += ',(Measure.[BOD Item_asn] >-1)';
                    whereQuery += '}';

                    let result= vdCommon.selectList(dimension, measure, whereQuery, '', '');

                    for(var k = 0; k < result.cs.rowCount; k++){
                        dimension = [];
                        measure = [];

                        dimension.push('[Version].[Version Name].['+fbVersion+']');
                        dimension.push('[Location].[Location].['+fbLocation+']');
                        dimension.push('[Sales Domain].[AP2].['+result.cs.row(k).cell(result.cs.memberColumnIndex("Sub Location", "Sub Location Rep AP2")).Name+']');
                        dimension.push('[Group].[Group ID].['+fbGroupID+']');
                        dimension.push('[Item].[Item Std1].['+result.cs.row(k).cell(result.cs.memberColumnIndex("Item", "Item Std1")).Name+']');

                        measure.push('Measure.[CTN Grp Const Filter_Asn] = "1";');

                        vdCommon.createMeasure(dimension, measure);                    
                    }
                    /*******************************************************************************/
                }

                /*******************************************************************************/
                //26.01.26 한재현프로님, 이재연위원님 요구 => Apply Flag가 "Y"인 경우.. 
                if (rowStatus != "D" && fbApplyFlag == "Y") {
                    //파이썬 호출 전 데이타 삭제함.
                    let deleteWhere = [];
                    deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                    deleteWhere.push("[Group].[Group ID].["+fbGroupID+"]");
   
                    vdCommon.deleteMeasure(deleteWhere, "CTN Grp Const Ecp");
                    //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    //파이썬 호출 : Item 별로
                     let filterList = "";
                    let execQuery = 'EXEC plugin instance [PY_UI_CTNMgmt] for measures {[CTN Grp Const_From Site]} '
                    execQuery += 'using scope ([Version].[Version Name].[' + fbVersion + '] * [Group].[Group ID].[' + fbGroupID + ']'

                    itemList = fbItem.split("^");
                    filterList = fn_filterList(itemList);
                    //vdCommon.debug("PY-[Item Data]"+ JSON.stringify(filterList));                
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Item].filter(" + filterList + ")";
                    }

                    filterList = fn_dataCheck(fbProductGrp.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Product Group]"+ vdUtil.fn_filterStr(filterList);

                    }
                    filterList = fn_dataCheck(fbProduct.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Product]"+ vdUtil.fn_filterStr(filterList);
                    }
                    
                    filterList = fn_dataCheck(fbSeriesName.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Series Name]"+ vdUtil.fn_filterStr(filterList);
                    }

                    filterList = fn_dataCheck(fbMKTName.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Marketing Name]"+ vdUtil.fn_filterStr(filterList);
                    }

                    filterList = fn_dataCheck(fbInch.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Inch]"+ vdUtil.fn_filterStr(filterList);
                    }

                    filterList = fn_dataCheck(fbCTNAttr.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[CTN]"+ vdUtil.fn_filterStr(filterList);
                    } 

                    filterList = fn_dataCheck(fbYear.split("^"));
                    if (filterList.length > 0) {
                        execQuery += " * [Item].[Year]"+ vdUtil.fn_filterStr(filterList);
                    }

                    execQuery += ')';
                    execQuery += 'using arguments {(ExecutionMode, "MediumWeight"), ("IncludeNullRows", "False")';
                    execQuery += ',(MaxSliceTableCells, 200000000), (MaxConcurrency, 1 ), ([Param.o9_sys_log_level], "DEBUG")} ;';

                    vdCommon.printStep("[" + programName + "] EXEC Python Call SQL>>" + execQuery);
                    vdCommon.executeQuery("PY_UI_CTNItemConst ", execQuery);
                }
            }

            vdCommon.programEnd();

            let totalRows = parsedParams.fbGridRows.length;
            let errorCnt =  errorList.length;
            let successCnt = parseInt(totalRows) - parseInt(errorCnt);
            let errorMsg = "" ;
            if(errorCnt > 0){                
                if(successCnt == 0){
                    errorMsg = "Save Failed. Please check if the Item is duplicated in a different Group ID." ;
                    return { "Code": -1, "Msg": errorMsg };
                }else{
                    errorMsg = "Partial save completed: ["+successCnt+"] Success / ["+errorCnt+"] Failure. Please check if the Item is duplicated in a different Group ID." ;
                    return { "Code": 0, "Msg": errorMsg };
                }                
            }

            return { "Code": 0, "Msg": "Save Successed." };

        } catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
    };  
    
    /******************** End: fn_save 관련 함수 ****************************************/
    
    /* 관련 Measure Group 
    1. CTN Grp Const
    2. CTN Grp Const Ecp
    3. CTN Grp Const Filter

    {"fbFuncName" : "fn_merge",
        "fbParams":{ "commitType":1,
        "filters":{
                "[Version].[Version Name]":{"SelectedMembers":["202608_M_WI_04"],"SelectedMembersAlias":["202608_M_WI_04"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
                "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":""}
            }
        },
        "fbGridRows" : [
        {"rowstatus":"U", "rowindex":0,	
        "[Version].[Version Name]" : "CWV_MP",
        "[Group].[Group ID]" : "PAC_00554"
        },
        {"rowstatus":"U", "rowindex":0,	
        "[Version].[Version Name]" : "CWV_MP",
        "[Group].[Group ID]" : "PAC_00556"
        }
        ]
    } 
    */
    var fn_merge = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            var userName = vdCommon.fn_getUserId();
            vdCommon.debug("[User Name]" + userName);            
            let fbVersion = vdUtil.fn_getFilterValue(parsedParams,"[Version].[Version Name]");
            let dimensionQuery = [];
            let comboList = [];
            let arrayGroupID = [];
            let deleteWhere = [];
            let deleteMeasureGroup = "";

            let dimensionInfo = [];
            let measureInfo = [];
            let measureUpdateInfo = [];
            let whereQuery = 'Where {(Measure.[CTN Grp Const_Updated By] == CurrentUser().[User Name] ||  Measure.[CTN Grp Const_Updated By] == CurrentUser().Name)}';

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Group].[Group ID]");

            measureInfo.push("Measure.[CTN Grp Const_AP2]");
            measureInfo.push("Measure.[CTN Grp Const_AP2 Cap]");
            measureInfo.push("Measure.[CTN Grp Const_AP2 Code]");
            measureInfo.push("Measure.[CTN Grp Const_AP2 ID]");
            measureInfo.push("Measure.[CTN Grp Const_Apply Flag]");
            measureInfo.push("Measure.[CTN Grp Const_Created By]");
            measureInfo.push("Measure.[CTN Grp Const_Creation Time]");
            measureInfo.push("Measure.[CTN Grp Const_DP Qty from W0]");
            measureInfo.push("Measure.[CTN Grp Const_EOH at PSI]");
            measureInfo.push("Measure.[CTN Grp Const_EOP MAX]");
            measureInfo.push("Measure.[CTN Grp Const_Ecp Flag]");
            measureInfo.push("Measure.[CTN Grp Const_End Week]");
            measureInfo.push("Measure.[CTN Grp Const_Except Item]");
            measureInfo.push("Measure.[CTN Grp Const_From Site]");
            measureInfo.push("Measure.[CTN Grp Const_From Site ID]");
            measureInfo.push("Measure.[CTN Grp Const_Frozen SOP Override Qty]");
            measureInfo.push("Measure.[CTN Grp Const_Frozen SOP Override Reason]");
            measureInfo.push("Measure.[CTN Grp Const_Frozen SOP Qty]");
            measureInfo.push("Measure.[CTN Grp Const_Frozen Week]");
            measureInfo.push("Measure.[CTN Grp Const_GC]");
            measureInfo.push("Measure.[CTN Grp Const_GC Code]");
            measureInfo.push("Measure.[CTN Grp Const_GC ID]");
            measureInfo.push("Measure.[CTN Grp Const_Inch]");
            measureInfo.push("Measure.[CTN Grp Const_Insert Flag]");
            measureInfo.push("Measure.[CTN Grp Const_Item]");
            measureInfo.push("Measure.[CTN Grp Const_Item CTN Attr]");
            measureInfo.push("Measure.[CTN Grp Const_Item Description]");
            measureInfo.push("Measure.[CTN Grp Const_MKT Name]");
            measureInfo.push("Measure.[CTN Grp Const_PLC EOP Curr Week]");
            measureInfo.push("Measure.[CTN Grp Const_PLC SRA Curr Week]");
            measureInfo.push("Measure.[CTN Grp Const_Prod Result Qty before W0]");
            measureInfo.push("Measure.[CTN Grp Const_Product]");
            measureInfo.push("Measure.[CTN Grp Const_Product Grp]");
            measureInfo.push("Measure.[CTN Grp Const_Project]");
            measureInfo.push("Measure.[CTN Grp Const_Series]");
            measureInfo.push("Measure.[CTN Grp Const_Start Week]");
            measureInfo.push("Measure.[CTN Grp Const_Total SOP Qty from W0]");
            measureInfo.push("Measure.[CTN Grp Const_Year]");
  
            measureUpdateInfo.push(vdUtil.fn_qMeaUpdateTime("Measure.[CTN Grp Const_Update Time]"));
            measureUpdateInfo.push(vdCommon.fn_mergeUser("Measure.[CTN Grp Const_Updated By]",fbVersion));
            //vdCommon.debug("["+parsedParams.fbGridRows+"]" + parsedParams.fbGridRows.length);  
            if(parsedParams.fbParams.commitType == 1){
                //Check 한 데이타 Merge
                for(var k=0; k < parsedParams.fbGridRows.length; k++ ){
                    dimensionQuery = [];
                    for(var j=0; j < dimensionInfo.length; j++){
                        let dim = dimensionInfo[j];

                        if(dim == "[Version].[Version Name]"){
                            dimensionQuery.push(dim + ".["+fbVersion+"]");
                        }else{
                            dimensionQuery.push(dim + ".["+ parsedParams.fbGridRows[k][dim] + "]");
                        }
                    }

                    result= vdCommon.selectList(dimensionQuery, measureInfo, whereQuery, "", "");
                    comboList = vdCommon.fn_makeCombo(result, {
                        DimName: "Group", DimAttbName: "Group ID", Sort: "DisplayName",
                        existAll: false,isDisplayNameWithCode: false});

                    arrayGroupID = comboList.map((value) => value.Name);
                    vdCommon.debug("arrayGroupID : " + JSON.stringify(arrayGroupID));
                    fn_mergeScope(result, dimensionInfo, measureInfo, measureUpdateInfo, fbVersion);
                }
            }else{
                dimensionQuery = [];
                for(var j=0; j < dimensionInfo.length; j++){
                    let dim = dimensionInfo[j];
                    if(dim == "[Version].[Version Name]"){
                        dimensionQuery.push(dim + ".["+fbVersion+"]");
                    }else{
                        dimensionQuery.push(dim);
                    }
                }

                result= vdCommon.selectList(dimensionQuery, measureInfo, whereQuery, "", "");
                comboList = vdCommon.fn_makeCombo(result, {
                    DimName: "Group", DimAttbName: "Group ID", Sort: "DisplayName",
                    existAll: false,isDisplayNameWithCode: false});

                arrayGroupID = comboList.map((value) => value.Name);
                vdCommon.debug("arrayGroupID : " + JSON.stringify(arrayGroupID));
                //fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, fbVersion, arrayGroupID);
                fn_mergeScope(result, dimensionInfo, measureInfo, measureUpdateInfo, fbVersion);
            }
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //CTN Grp Const Ecp
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            dimensionInfo = [];
            measureInfo = [];
            measureUpdateInfo = [];
            whereQuery = 'Where {(Measure.[CTN Grp Const Ecp_Updated By] == CurrentUser().[User Name] ||  Measure.[CTN Grp Const Ecp_Updated By] == CurrentUser().Name)}';

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Group].[Group ID]");
            dimensionInfo.push("[Item].[Item]");

            measureInfo.push("Measure.[CTN Grp Const Ecp_DP Qty from W0]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_EOH at PSI]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_Ecp Flag]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_End Week]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_PLC EOP Curr Date]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_PLC EOP Curr Week]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_PLC SRA Curr Week]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_Prod Result Qty before W0]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_Start Week]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_Total SOP DP Diff Qty]");
            measureInfo.push("Measure.[CTN Grp Const Ecp_Total SOP Qty from W0]");
            
            measureUpdateInfo.push(vdUtil.fn_qMeaUpdateTime("Measure.[CTN Grp Const Ecp_Update Time]"));
            measureUpdateInfo.push(vdCommon.fn_mergeUser("Measure.[CTN Grp Const Ecp_Updated By]",fbVersion));

            vdCommon.debug("[CTN Grp Const Ecp]");
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Delete가 필요함.
            deleteWhere = [];
            deleteMeasureGroup = "CTN Grp Const Ecp";
            deleteWhere.push("[Version].[Version Name].[CWV_MP]");
            deleteWhere.push("[Group].[Group ID]"+vdUtil.fn_filterStr(arrayGroupID));            
            vdCommon.deleteMeasure(deleteWhere, deleteMeasureGroup)            
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

            fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, fbVersion, arrayGroupID);

            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //CTN Grp Const Filter
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++            
            dimensionInfo = [];
            measureInfo = [];
            measureUpdateInfo = [];
            whereQuery = '';

            dimensionInfo.push("[Version].[Version Name]");
            dimensionInfo.push("[Location].[Location]");
            dimensionInfo.push("[Group].[Group ID]");
            dimensionInfo.push("[Item].[Item Std1]");

            measureInfo.push("Measure.[CTN Grp Const Filter_Asn]");
            
            vdCommon.debug("[CTN Grp Const Filter]");
           //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            //Delete가 필요함.
            deleteWhere = [];
            deleteMeasureGroup = "CTN Grp Const Filter";
            deleteWhere.push("[Version].[Version Name].[CWV_MP]");
            deleteWhere.push("[Group].[Group ID]"+vdUtil.fn_filterStr(arrayGroupID));            
            vdCommon.deleteMeasure(deleteWhere, deleteMeasureGroup)            
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            fn_mergeSetting(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, fbVersion, arrayGroupID);
            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++     
            return { "Code" : 0, "Msg" : "" };
            
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }

    var fn_mergeSetting = function(dimensionInfo, measureInfo, whereQuery, measureUpdateInfo, sVersion, arrayGroupID){        
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let dimensionQuery = [];
            vdCommon.debug("[fn_mergeSetting]"+dimensionInfo.length);
            for(var j=0; j < dimensionInfo.length; j++){

                if(dimensionInfo[j] == "[Version].[Version Name]"){
                    dimensionQuery.push(dimensionInfo[j] + ".["+sVersion+"]");
                }else if(dimensionInfo[j] == "[Group].[Group ID]"){
                    dimensionQuery.push(dimensionInfo[j] + vdUtil.fn_filterStr(arrayGroupID));
                }else{
                    dimensionQuery.push(dimensionInfo[j]);
                }
            }
            vdCommon.debug("<DIM> " + JSON.stringify(dimensionQuery));
            vdCommon.debug("<Measure> " + JSON.stringify(measureInfo));
            vdCommon.debug("<Where> " +whereQuery);
            result= vdCommon.selectList(dimensionQuery, measureInfo, whereQuery, "", "");
            fn_mergeScope(result, dimensionInfo, measureInfo,measureUpdateInfo, sVersion);

        }catch ( e ) {
            this.error(e.message);
            throw e;
        }
    }    

    var fn_mergeScope = function(result, dimensionInfo, measureInfo, measureUpdateInfo, sVersion){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            vdCommon.debug("[fn_mergeScope] Count:" +result.cs.rowCount);
            for(var k=0; k < result.cs.rowCount ; k++){
                let dimension = [];
                let changeMeasure = [];
                // Dimension 처리
                for(var i=0; i < dimensionInfo.length ; i++){
                    if(dimensionInfo[i] == "[Version].[Version Name]"){
                        dimension.push(dimensionInfo[i] +".[CWV_MP]");
                    }else{                        
                        let dim = dimensionInfo[i].split(".");
                        let dimValue = result.cs.row(k).cell(result.cs.memberColumnIndex(dim[0].replace("[","").replace("]",""), dim[1].replace("[","").replace("]",""))).Name;
                        vdCommon.debug(dim +"["+dimValue+"]");
                        dimension.push(dimensionInfo[i] + ".["+dimValue+"]");
                    }
                    
                }
                vdCommon.debug("For-End[Dim Info]"+JSON.stringify(dimension));
                //Measure 처리
                vdCommon.debug("[fn_mergeScope] Measure Info:" +measureInfo.length);
                for(var j=0; j < measureInfo.length ; j++){  
                    changeMeasure.push(vdUtil.fn_qMeaForMerge(measureInfo[j], sVersion));
                }

                for(var m=0; m < measureUpdateInfo.length; m++){                    
                    changeMeasure.push(measureUpdateInfo[m]);
                }
                
                vdCommon.createMeasure(dimension, changeMeasure);
            }

        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }      
    }  
    
    /******************** End: fn_merge 관련 함수 ****************************************/

    /************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_save": fn_save
        ,"fn_frozenWeek": fn_frozenWeek
        ,"fn_filterConstWeek" : fn_filterConstWeek
        ,"fn_cb_siteMF":fn_cb_siteMF
        ,"fn_cb_product_bodItem": fn_cb_product_bodItem
        ,"fn_cb_seriesName_bodItem": fn_cb_seriesName_bodItem
        ,"fn_cb_ctn_bodItem": fn_cb_ctn_bodItem
        ,"fn_cb_inch_bodItem":fn_cb_inch_bodItem
        ,"fn_cb_project_bodItem":fn_cb_project_bodItem
        ,"fn_cb_setYear_bodItem":fn_cb_setYear_bodItem
        ,"fn_cb_setMKTName_bodItem":fn_cb_setMKTName_bodItem
        ,"fn_cb_setItem_bodItem":fn_cb_setItem_bodItem
        ,"fn_cb_setExceptItem_bodItem": fn_cb_setExceptItem_bodItem
        ,"fn_cb_salesGC_bodItem":fn_cb_salesGC_bodItem        
        ,"fn_cb_salesAP2_bodItem":fn_cb_salesAP2_bodItem
        ,"fn_merge":fn_merge
    };

    return {
        fn_loadFunction: fn_loadFunction
    };
});