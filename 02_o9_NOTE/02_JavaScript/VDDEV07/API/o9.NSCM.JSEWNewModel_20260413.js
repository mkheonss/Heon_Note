define('o9.NSCM.JSEWNewModel', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function(){

    const programName = "o9.NSCM.JSEWNewModel";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();
    /*--------------------------------------------------------------------------------------------------*/
    // 프로그램명 : o9.NSCM.JSEWNewModel
    // Action Button : EWNewModel
    // 화면명 : New Model
    // 2025.07.29 최초 생성
    // 2025.08.25 fn_delete 추가함.
    // 2025.08.27 fn_save에서 C/U/D 모두 처리되도록 수정함.
    // 2025.09.23 update 일자 처리 수정
    // 2025.09.25 Update 일때... Create 할지? Update 할지? 분기함.
    // 2025.10.27 fn_cb_ap2 수정
    // 2025.12.11 신규,수정시 모두 CreateMember 처리함.
    // 2025.12.31 fn_loadFunction() 수정함. => parsedParams 값 체크 로직 추가
    // 2026.01.07 fn_cb_siteMF() 추가함 => View Filter 적용이 필요없음
    // 2026.01.09 GC, AP2 NameSet 적용
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

   /* ********************************************************************************** */
     // where 정 생성
     var fn_makeWhere = function(parsedParams){
        var whereStr = "";
        var where = parsedParams.fbParams["where"];
        for ( let key in where ) {
            if(where[key] != undefined && where[key] != null && where[key] != ""){
                whereStr += ( whereStr == "" ? "" : ", " ) + key + vdUtil.fn_filterStr(where[key]);
            }            
        }

        if ( whereStr == "" ) {
            return "";
        } else {
            return "where { " + whereStr + " } ";
        }
    };
   /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_siteMF" }
    // New Model 화면에서 View 필터 조건이 적용할 필요가 없어서 공통함수 사용하지 않음.(26.01.07)
		var fn_cb_siteMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&MFStageSETLocation'];

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
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
    
    // {"fbFuncName" : "fn_cb_section"}
    // fn_cb_section
    var fn_cb_section = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[Section].filter(#.Name != "-")'];

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "Section", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            //vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }    
    };
    
    var fn_cb_sectionFilter = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    
		    var dims = ['[Item New Model].[Section].filter(#.Name != "-")' + vdUtil.fn_getFilterQuery2(parsedParams, "[Item New Model].[Section]")];

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "Section", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            //vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }    
    };    
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_kdType"  ,"fbParams":{"includeField": "Item New Model:Section:Section"}}
    // ex){"fbFuncName" : "fn_cb_kdType", "fbParams" : {"where":{"[Item New Model].[Section]":"TV"}}}
    // ex){"fbFuncName" : "fn_cb_kdType", "fbParams" : {"includeField": "Item New Model:Section"}}
    var fn_cb_kdType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[KD Type].filter(#.Name != "-")'];

            if ( parsedParams.fbParams["includeField"] != "" ) {
                dims.push('[Item New Model].[Section]');
            }

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "KD Type", Sort : "DisplayName",
                                                includeField : parsedParams.fbParams.includeField,
                                                existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }    
    };
    /* ********************************************************************************** */
    // {"fbFuncName" : "fn_cb_project" }
    
    // ex:{"fbFuncName":"fn_cb_project","fbParams":{"where" : {"[Item New Model].[Section]" : "TV", "[Item New Model].[KD Type]" : "NOR"}} }
    // ex:{"fbFuncName":"fn_cb_project","fbParams":{"includeField":"Item New Model:Section:Section,Item New Model:KD Type:KD Type"}}
    var fn_cb_project = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[Project].filter(#.Name != "-")'];

            if ( parsedParams.fbParams["includeField"] != "" ) {
                dims.push('[Item New Model].[Section].filter(#.Name != "-")');
                dims.push('[Item New Model].[KD Type].filter(#.Name != "-")');
            }

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "Project", Sort : "DisplayName",
                                                includeField : parsedParams.fbParams.includeField,
                                                existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }    
    }  
    /* ********************************************************************************** */
    // {"fbFuncName" : "fn_cb_series" }
    //
    var fn_cb_series = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[Series].filter(#.Name != "-")'];

            if ( parsedParams.fbParams["includeField"] != "" ) {
                dims.push('[Item New Model].[Section].filter(#.Name != "-")');
                dims.push('[Item New Model].[KD Type].filter(#.Name != "-")');
                dims.push('[Item New Model].[Project].filter(#.Name != "-")');
            }

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "Series", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }    
    }

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_drType" }
    // fn_cb_drType
    var fn_cb_drType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[DR Type].filter(#.Name != "-")'];

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "DR Type", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }    
    }
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_inch" }
    // fn_cb_series
    var fn_cb_inch = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[Inch].filter(#.Name != "-")'];

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "Inch", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }    
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_grade" }
    // fn_cb_grade
    var fn_cb_grade = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[Grade].filter(#.Name != "-")'];

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "Grade", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }    
    };

    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_product" }
    // fn_cb_product
    var fn_cb_product = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    var dims = ['[Item New Model].[Product].filter(#.Name != "-")'];

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item New Model", DimAttbName : "Product", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }    
    }
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_gc" }
    var fn_cb_gc = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
		    //var dims = ['&NSUISalesStd1View.relatedmembers([GC])']; //2026.01.09 수정
            var dims = ['&NSUISalesStd1View.filter(#.[Sales Std1$IsDummy]==false).relatedmembers([GC]).filter(#.Name startswith"2")']; //2026.01.12 수정

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "GC", Sort : "DisplayName",
                                                 existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }    
    } 
    
    /* ********************************************************************************** */
    // { "fbFuncName" : "fn_cb_ap2" }
    /*{"fbFuncName" : "fn_cb_ap2", "fbParams" : { "where" : { "[Sales Domain].[GC]" : "201"} } }*/
    var fn_cb_ap2= function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
		try {
            var fbGC = parsedParams.fbParams["where"]["[Sales Domain].[GC]"]
    	    //var dims = ['&NSUISalesStd2View.relatedmembers([AP2])'];
            var dims = ['&NSUISalesStd2View.filter(#.[Sales Std2$IsDummy]==false).relatedmembers([AP2]).filter(#.Name startswith"3")']; //2026.01.12 수정
            dims.push('&NSUISalesStd1View.relatedmembers([GC])'+vdUtil.fn_filterStr(fbGC));

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sales Domain", DimAttbName : "AP2", Sort : "DisplayName",
                                                existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {

            return { "Code" : -1, "Msg" : e.message };
        }    
    } ;
    
    // { "fbFuncName" : "fn_cb_ap2Test" }
    var fn_validation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            let errorCnt = 0;
            let fbVersion = parsedParams.fbParams.version;

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];
                let fbItem = parsedParams.fbGridRows[i]["[Item New Model].[Item]"]; 
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];  //Plant
                let fbAP2 = parsedParams.fbGridRows[i]["[Sales Domain].[AP2]"];

                parsedParams.fbGridRows[i]["rowmsg"] = "";
                parsedParams.fbGridRows[i]["errorflag"] = "";

                if(rowStatus == "C"){
                     //validation 체크함.
                    //(1) Item(Model) 등록 여부 체크
                    let sDimension = [];
                    sDimension.push("[Version].[Version Name].["+fbVersion+"]");
                    sDimension.push("[Location].[Location].["+fbLocation+"]");
                    sDimension.push("[Sales Domain].[AP2].["+fbAP2+"]");
                    sDimension.push("[Category].[Category].["+"Plan"+"]");
                    sDimension.push("[Item New Model].[Item].["+fbItem+"]");
                    let sMeasure = [];
                    sMeasure.push("Measure.[New Model_Update Date]");
                    sMeasure.push("Measure.[New Model_Updated By]");                    
                   
                    if(vdCommon.existMeasure(sDimension, sMeasure, "")){
                        let errorMsg = "This is a registered model.";
                        errorCnt++;
                        parsedParams.fbGridRows[i]["rowmsg"] = errorMsg;
                        parsedParams.fbGridRows[i]["errorflag"] = "ERROR";
                    }                    
                }                
            }

            if(errorCnt > 0 ){
                //Error Row만 Return 함.
                let checkGridRows = parsedParams.fbGridRows;
                const errorRows = checkGridRows.filter((checkGridRows)=>{return checkGridRows.errorflag === "ERROR"});
                parsedParams.fbGridRows = errorRows;
                return { "Code" : -1, "Msg" : "validation Error", "Rows" : parsedParams.fbGridRows };
            }

            return { "Code" : 0, "Msg" : "" };
        }catch(e){
            return { "Code" : -1, "Msg" : e.message };
        }  
    } ;    

    /* ********************************************************************************** */
    var fn_createMember = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{
            //CreateMember
            let dimension = [];
            dimension.push('[Item New Model].[Item]');
            dimension.push('[Item New Model].[DR Type]');
            dimension.push('[Item New Model].[Grade]');
            dimension.push('[Item New Model].[Inch]');
            dimension.push('[Item New Model].[KD Type]');
            dimension.push('[Item New Model].[Product]');
            dimension.push('[Item New Model].[Project]');
            dimension.push('[Item New Model].[Section]');
            dimension.push('[Item New Model].[Series]');
            //dimension.push('[Item New Model].[Marketing Name]');
            let memberQuery = "";
            for(var k=0; k < dimension.length; k++){
                memberQuery += (memberQuery == "" ? "" : " ,") + dimension[k] + ' = {, "'+parsedParams[dimension[k]]+'"}\n'
            }

            memberQuery = 'Createmember('+memberQuery;
            memberQuery += ' ,[Item New Model].[Marketing Name] = {, "-"}';
            memberQuery += ');';
            
            vdCommon.executeQuery("fn_save(MemberCreate)]", memberQuery);

            return { "Code" : 0, "Msg" : "" };
        }catch(e){
            return { "Code" : -1, "Msg" : e.message };
        }
    };
    
    /*
        {"fbFuncName" : "fn_save",
         "fbParams": {"version":"CWV_MP"},
        "fbGridRows" : [
           {"rowstatus":"D", "rowindex":0
         ,"[Location].[Location]":"P406"
         ,"[Sales Domain].[AP2]":"300127"
         ,"[Item New Model].[Item]":"UE43TEST0827"
         },
        {"rowstatus":"U", "rowindex":0,	
        "[Location].[Location]":"P551","[Location].[LocationOld]":"P551"
        ,"[Sales Domain].[AP2]":"300341","[Sales Domain].[AP2Old]":"300341"
        , "[Category].[Category]":"Plan"
        ,"[Item New Model].[Item]":"QA55Q80DAUXSA"
        ,"[Item New Model].[ItemOld]":"QA55Q80DAUXSA"
        ,"Measure.[New Model_Air SOP Date]" : "4/18/2024"
        ,"Measure.[New Model_Year]":"2022"
        },
        {"rowstatus":"U", "rowindex":0,	
        "[Item New Model].[DR Type]": "32", "[Item New Model].[Grade]":"B","[Item New Model].[Inch]":"43"
        ,"[Item New Model].[KD Type]":"KD","[Item New Model].[Product]":"-","[Item New Model].[Section]":"TV"
        ,"[Item New Model].[Series]":"-","[Item New Model].[Project]":"-"
        ,"[Location].[Location]":"P406","[Location].[LocationOld]":"P406"
        ,"[Sales Domain].[AP2]":"300127","[Sales Domain].[AP2Old]":"300127"
        , "[Category].[Category]":"Plan", 
        "[Item New Model].[Item]":"UE43TEST0827_02","[Item New Model].[ItemOld]":"UE43TEST0827_02"
        ,"Measure.[New Model_BOM HQ Status]":"20240125"
        ,"Measure.[New Model_BOM Local Status]":"20240201"
        ,"Measure.[New Model_Code Status]":"20240111"
        ,"Measure.[New Model_LCM Code]":"CY-BD043HGCV1H/V"
        ,"Measure.[New Model_LCM From Site]":"SEHC(VD)_LCM"
        ,"Measure.[New Model_LCM Model]":"BN95-11030A"
        ,"Measure.[New Model_LCM TP Mode]":"VESSEL"
        ,"Measure.[New Model_LCM Vendor]":"HKC"
        ,"Measure.[New Model_Platform]":"KANT-SU2e(3in1)"
        ,"Measure.[New Model_SET Aging]":"4/22/2024"
        ,"Measure.[New Model_SET MP]":"4/18/2024"
        ,"Measure.[New Model_SET SOP]":"4/2/2024"
        ,"Measure.[New Model_SOP Date]":"4/1/2024"
        ,"Measure.[New Model_SOP Status]":"20240402"
        ,"Measure.[New Model_SR Date]":"4/18/2024"
        ,"Measure.[New Model_SR Prod Qty]":"0"
        ,"Measure.[New Model_SR Qty]":"96"
        ,"Measure.[New Model_Sales RTS]":"4/22/2024"
        ,"Measure.[New Model_Update Reason]":"."
        ,"Measure.[New Model_Year]":"2024"
        }
        {"rowstatus":"C", "rowindex":0,	
        "[Item New Model].[DR Type]": "32", "[Item New Model].[Grade]":"B","[Item New Model].[Inch]":"43"
        ,"[Item New Model].[KD Type]":"KD","[Item New Model].[Product]":"-","[Item New Model].[Section]":"TV"
        ,"[Item New Model].[Series]":"-","[Item New Model].[Project]":"-"
        ,"[Location].[Location]":"P406"
        ,"[Sales Domain].[AP2]":"300127", "[Category].[Category]":"Plan", "[Item New Model].[Item]":"UE43TEST0827_02"
        ,"Measure.[New Model_BOM HQ Status]":"20240125"
        ,"Measure.[New Model_BOM Local Status]":"20240201"
        ,"Measure.[New Model_Code Status]":"20240111"
        ,"Measure.[New Model_LCM Code]":"CY-BD043HGCV1H/V"
        ,"Measure.[New Model_LCM From Site]":"SEHC(VD)_LCM"
        ,"Measure.[New Model_LCM Model]":"BN95-11030A"
        ,"Measure.[New Model_LCM TP Mode]":"VESSEL"
        ,"Measure.[New Model_LCM Vendor]":"HKC"
        ,"Measure.[New Model_Platform]":"KANT-SU2e(3in1)"
        ,"Measure.[New Model_SET Aging]":"4/22/2024"
        ,"Measure.[New Model_SET MP]":"4/18/2024"
        ,"Measure.[New Model_SET SOP]":"4/2/2024"
        ,"Measure.[New Model_SOP Date]":"4/1/2024"
        ,"Measure.[New Model_SOP Status]":"20240402"
        ,"Measure.[New Model_SR Date]":"4/18/2024"
        ,"Measure.[New Model_SR Prod Qty]":"0"
        ,"Measure.[New Model_SR Qty]":"96"
        ,"Measure.[New Model_Sales RTS]":"4/22/2024"
        ,"Measure.[New Model_Update Reason]":"."
        ,"Measure.[New Model_Year]":"2024"
        }
        ]}
    */
    var fn_save = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug"); 
        try{

            let fbVersion = parsedParams.fbParams.version;   

            //validation 체크함.
            let errorData = fn_validation(parsedParams);
            if(errorData.Code == -1){
                return errorData
            }

            let measureList = [];
            measureList.push("Measure.[New Model_Air SOP Date]");
            measureList.push("Measure.[New Model_Air SOP Qty]");
            measureList.push("Measure.[New Model_Air SOP To Site]");
            measureList.push("Measure.[New Model_BOM HQ Status]");
            measureList.push("Measure.[New Model_BOM Local Status]");
            measureList.push("Measure.[New Model_Code Status]");
            measureList.push("Measure.[New Model_Dash Status]");
            measureList.push("Measure.[New Model_Dev DV]");
            measureList.push("Measure.[New Model_Dev DVR]");
            measureList.push("Measure.[New Model_Dev LMI]");
            measureList.push("Measure.[New Model_Dev PIA]");
            measureList.push("Measure.[New Model_Dev PR]");
            measureList.push("Measure.[New Model_Dev PRA]");
            measureList.push("Measure.[New Model_Dev PV]");
            measureList.push("Measure.[New Model_Dev PVR]");
            measureList.push("Measure.[New Model_LCM Approval]");
            measureList.push("Measure.[New Model_LCM CDR2]");
            measureList.push("Measure.[New Model_LCM Code]");
            measureList.push("Measure.[New Model_LCM CPA]");
            measureList.push("Measure.[New Model_LCM From Site]");
            measureList.push("Measure.[New Model_LCM L/BOM1]");
            measureList.push("Measure.[New Model_LCM Model]");
            measureList.push("Measure.[New Model_LCM MP]");
            measureList.push("Measure.[New Model_LCM SR]");
            measureList.push("Measure.[New Model_LCM SRA]");
            measureList.push("Measure.[New Model_LCM SRP-F]");
            measureList.push("Measure.[New Model_LCM SRP-S]");
            measureList.push("Measure.[New Model_LCM TP Mode]");
            measureList.push("Measure.[New Model_LCM Vendor]");
            measureList.push("Measure.[New Model_Mfg Date]");
            measureList.push("Measure.[New Model_Mfg Qty]");
            measureList.push("Measure.[New Model_MP DP Status]");
            measureList.push("Measure.[New Model_Platform]");
            measureList.push("Measure.[New Model_RTS DP Status]");
            measureList.push("Measure.[New Model_RUN/DROP]");
            measureList.push("Measure.[New Model_Sales LT]");
            measureList.push("Measure.[New Model_Sales RDD]");
            measureList.push("Measure.[New Model_Sales Reset]");
            measureList.push("Measure.[New Model_Sales RTS]");
            measureList.push("Measure.[New Model_SET Aging]");
            measureList.push("Measure.[New Model_SET MP]");
            measureList.push("Measure.[New Model_SET PLM SRA]");
            measureList.push("Measure.[New Model_SET SOP]");
            measureList.push("Measure.[New Model_SET SR]");
            measureList.push("Measure.[New Model_SET SRA]");
            measureList.push("Measure.[New Model_SET SRP-F]");
            measureList.push("Measure.[New Model_SET SRP-S]");
            measureList.push("Measure.[New Model_SOP Date]");
            measureList.push("Measure.[New Model_SOP Qty]");
            measureList.push("Measure.[New Model_SOP Register Date]");
            measureList.push("Measure.[New Model_SOP Status]");
            measureList.push("Measure.[New Model_SR Date]");
            measureList.push("Measure.[New Model_SR Prod Qty]");
            measureList.push("Measure.[New Model_SR Prod To Site]");
            measureList.push("Measure.[New Model_SR Qty]");
            measureList.push("Measure.[New Model_SR To Site]");
            measureList.push("Measure.[New Model_SRP Prod LCM Qty]");
            measureList.push("Measure.[New Model_SRP Prod SET Qty]");
            measureList.push("Measure.[New Model_Update Reason]");
            measureList.push("Measure.[New Model_Year]");
            
            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                let rowStatus = parsedParams.fbGridRows[i]["rowstatus"];

                let fbItem = parsedParams.fbGridRows[i]["[Item New Model].[Item]"]; 
                let fbLocation = parsedParams.fbGridRows[i]["[Location].[Location]"];  //Plant
                let fbAP2 = parsedParams.fbGridRows[i]["[Sales Domain].[AP2]"];
                let fbCategory = parsedParams.fbGridRows[i]["[Category].[Category]"];

                //OLD 값
                let fbLocationOld = parsedParams.fbGridRows[i]["[Location].[LocationOld]"];  //Plant
                let fbAP2Old = parsedParams.fbGridRows[i]["[Sales Domain].[AP2Old]"];  //AP2
                let fbItemOld = parsedParams.fbGridRows[i]["[Item New Model].[ItemOld]"]; 
                //vdCommon.debug("[OLD]["+fbLocationOld+"]["+fbAP2Old+"]["+fbItemOld+"]");

                if( rowStatus != "D"){
                    //Create Member 처리                    
                    fn_createMember( parsedParams.fbGridRows[i]);
                }                   
                    
                if(rowStatus == "C"){
                    //New Model 메져그룹 등록
                    let createDimension = [];
                    createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                    createDimension.push("[Location].[Location].["+fbLocation+"]");
                    createDimension.push("[Sales Domain].[AP2].["+fbAP2+"]");
                    createDimension.push("[Category].[Category].["+fbCategory+"]");
                    createDimension.push("[Item New Model].[Item].["+fbItem+"]");                    

                    let createMeasure = [];
                    for(var k = 0; k < measureList.length; k++ ){
                        let sCol = measureList[k];
                        let gridValue = parsedParams.fbGridRows[i][sCol];

                        if(gridValue != undefined && gridValue != null){
                            createMeasure.push(sCol + " = " + '"'+gridValue+'"' + ";");
                        }
                    }
                    createMeasure.push('Measure.[New Model_Updated By] = CurrentUser().[User Name];'); 
                    createMeasure.push('Measure.[New Model_Update Date]= Now();'); 
                    createMeasure.push("Measure.[New Model_New Valid Flag] = "+ '"Y"' +";");
                    vdCommon.createMeasure(createDimension, createMeasure);                
                }else if( rowStatus == "U") {

                    if(fbItem == fbItemOld && fbLocation == fbLocationOld && fbAP2 == fbAP2Old){
                        let updateDimension = [];
                        let updateMeasure=[];
    
                        updateDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        updateDimension.push("[Location].[Location].["+fbLocation+"]");
                        updateDimension.push("[Sales Domain].[AP2].["+fbAP2+"]");
                        updateDimension.push("[Category].[Category].["+fbCategory+"]");
                        updateDimension.push("[Item New Model].[Item].["+fbItem+"]");   
    
                        for(var k = 0; k < measureList.length; k++ ){
                            let sCol = measureList[k];
                            let gridValue = parsedParams.fbGridRows[i][sCol];
    
                            if(gridValue != undefined && gridValue != null){
                                updateMeasure.push(sCol + " = " + '"'+gridValue+'"' + ";");
                            }
                        }
                        vdCommon.updateMeasure(updateDimension, updateMeasure);
                    }else{
                        //OLD 값을 체크하여 신규 데이타인지 판단해야함.
                        let oldDimension = [];
                        oldDimension.push("[Version].[Version Name].["+fbVersion+"]");
                        oldDimension.push("[Location].[Location].["+fbLocationOld+"]");
                        oldDimension.push("[Sales Domain].[AP2].["+fbAP2Old+"]");
                        oldDimension.push("[Category].[Category].["+fbCategory+"]");
                        oldDimension.push("[Item New Model].[Item].["+fbItemOld+"]");
                        
                        let sMeasure = [];
                        sMeasure.push("Measure.[New Model_Update Date]");
                        sMeasure.push("Measure.[New Model_Updated By]");

                        if(vdCommon.existMeasure(oldDimension, sMeasure, "")){
                            //삭제 후 다시 생성함.

                            let sMeasure = [];
                            sMeasure.push("Measure.[New Model_Update Date]");
                            sMeasure.push("Measure.[New Model_Updated By]");                            
                            //++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                            //Old 데이타 삭제함.
                            let deleteWhere = [];
                            deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                            deleteWhere.push("[Location].[Location].["+fbLocationOld+"]");
                            deleteWhere.push("[Sales Domain].[AP2].["+fbAP2Old+"]");
                            deleteWhere.push("[Item New Model].[Item].["+fbItemOld+"]");
                            deleteWhere.push("[Category].[Category].["+fbCategory+"]");
            
                            vdCommon.deleteMeasure(deleteWhere, "New Model"); 
                            
                            //New Model 메져그룹 등록
                            let createDimension = [];
                            createDimension.push("[Version].[Version Name].["+fbVersion+"]");
                            createDimension.push("[Location].[Location].["+fbLocation+"]");
                            createDimension.push("[Sales Domain].[AP2].["+fbAP2+"]");
                            createDimension.push("[Category].[Category].["+fbCategory+"]");
                            createDimension.push("[Item New Model].[Item].["+fbItem+"]");

                            let createMeasure=[];
                            for(var k = 0; k < measureList.length; k++ ){
                                let sCol = measureList[k];
                                let gridValue = parsedParams.fbGridRows[i][sCol];
        
                                if(gridValue != undefined && gridValue != null){
                                    createMeasure.push(sCol + " = " + '"'+gridValue+'"' + ";");
                                }
                            }
                            createMeasure.push('Measure.[New Model_Updated By] = CurrentUser().[User Name];'); 
                            createMeasure.push('Measure.[New Model_Update Date]= Now();'); 
                            createMeasure.push("Measure.[New Model_New Valid Flag] = "+ '"Y"' +";");
                            vdCommon.createMeasure(createDimension, createMeasure);
                        }
                    }
                }else if( rowStatus == "D") {
                    let deleteWhere = [];
                    deleteWhere.push("[Version].[Version Name].["+fbVersion+"]");
                    deleteWhere.push("[Location].[Location].["+fbLocation+"]");
                    deleteWhere.push("[Sales Domain].[AP2].["+fbAP2+"]");
                    deleteWhere.push("[Item New Model].[Item].["+fbItem+"]");
    
                    vdCommon.deleteMeasure(deleteWhere, "New Model");                     
                }
            }

            return { "Code" : 0, "Msg" : "", "Rows" : "" };

        }catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    }
    
   /* 
    {"fbFuncName":"fn_filterInfo",
    "fbParams":{
        "filters":{
        "[Category].[Category]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"Category.[Category].filter(#.Name in {\"Actual\",\"Plan\"})"},
        "[Sales Domain].[AP2]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"&NSUISalesGrpAP2View","DimensionAliasName":"Sales"},
        "[Version].[Version Name]":{"SelectedMembers":["CWV_MP"],"SelectedMembersAlias":["202608_P"],"MemberFilter":"&CWVUI","DimensionAliasName":"Plan ID"},
        "[Filter].[Filter]":{"SelectedMembers":[],"SelectedMembersAlias":[],"MemberFilter":"","SelectedMembersExp":"filter(#.[FilterItem] contains \"QE32Q5FAAUXZZ\"))"}
        }
        ,"reportName":"[NSCM] EW VD New Model"
        ,"menuName":"New Model"
    }
    }

   */
    var fn_filterInfo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");
        try{
            let returnValue = "";
            let filterInfo = vdUtil.fn_getFilter(parsedParams, "[Filter].[Filter]");
            let filterValue = filterInfo["SelectedMembersExp"];
            
            if(filterValue == undefined || filterValue == ""){
                return { "Code" : 0, "Msg" : "", "IBPL": returnValue };
            }
            filterValue = filterValue.replace("filter","").replace("(","").replace(")","");
            filterValue = filterValue.split("&&");  
            vdCommon.debug("["+filterValue.length+"]"+JSON.stringify(filterValue));
            for(var k=0; k < filterValue.length; k++){

                if(filterValue[k].indexOf("[FilterItem]") > 0){
                    filterValue = filterValue[k].replace("(","").replace(")","").replace("[FilterItem]","Name").replace("contains", "containsregexp");
                    returnValue = "Item New Model].[Item].filter(" +filterValue + ")";
                }                
            }            

            return { "Code" : 0, "Msg" : "", "IBPL": returnValue };

        }catch (e) {
            return { "Code": -1, "Msg": e.message };
        }
   }    
    

    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
       "fn_cb_section"   : fn_cb_section
       ,"fn_cb_kdType"   : fn_cb_kdType
       ,"fn_cb_project"  : fn_cb_project
       ,"fn_cb_series"   : fn_cb_series
       ,"fn_cb_drType"   : fn_cb_drType
       ,"fn_cb_inch"     : fn_cb_inch
       ,"fn_cb_grade"    : fn_cb_grade
       ,"fn_cb_product"  : fn_cb_product
       ,"fn_cb_gc"       : fn_cb_gc
       ,"fn_cb_ap2"      : fn_cb_ap2
       ,"fn_cb_siteMF"   : fn_cb_siteMF
       ,"fn_save"        : fn_save
       ,"fn_cb_sectionFilter": fn_cb_sectionFilter
       ,"fn_filterInfo" : fn_filterInfo
    };

    return {
        fn_loadFunction : fn_loadFunction
    };

});