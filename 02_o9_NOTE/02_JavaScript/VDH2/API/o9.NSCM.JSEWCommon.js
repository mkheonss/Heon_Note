define('o9.NSCM.JSEWCommon', ['o9/data/query', 'o9/data/cellset', 'o9.NSCM.commonLib'], function () {
	const programName = "o9.NSCM.JSEWCommon";
    const commonLib = require('o9.NSCM.commonLib');
    const vdUtil = new commonLib.VdUtil();

/************************************************* UI Call Common Logic *************************************************/
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
            // 콤보에 Blank 추가
            if ( parsedParams.fbParams["existBlank"] == undefined ) {
                parsedParams.fbParams["existBlank"] = false;
            }
            // where 조건 추가
            if ( parsedParams.fbParams["where"] == undefined ) {
                parsedParams.fbParams["where"] = {};
            }
            if ( parsedParams.fbParams["isDisplayNameWithCode"] == undefined ) {
                parsedParams.fbParams["isDisplayNameWithCode"] = true;
            }

            var rtn = functionMap[fbFuncName](parsedParams);

            vdCommon.programEnd();
            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
	};

/************************************************* combo logic *************************************************/
    // 여러개의 콤보를 한번에 가져올때
    // { "fbFuncName" : "fn_cb_common", "fbParams" : { "codes" : ["jdm", "mfSiteStageForMF", "subsidiaryForMF", "siteMF", "siteDC", "tpmodeGO"] } }
	var fn_cb_common = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var codes = parsedParams.fbParams.codes;
            var rtn = {};

            for ( var i = 0; i < codes.length; i++ ) {
                var sRtn = functionMap["fn_cb_" + codes[i]](parsedParams);
                rtn[codes[i]] = sRtn.Rows;
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : rtn };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_jdm" }
	var fn_cb_jdm = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","-"], ComboValues : ["Y","-"]});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_mfSiteStageForMF" }
	var fn_cb_mfSiteStageForMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Location].[MF Site Stage].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Location].[Location Type]"] = "MF";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "MF Site Stage", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_subsidiaryForMF" }
	var fn_cb_subsidiaryForMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Location].[Subsidiary].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Location].[Location Type]"] = "MF";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Subsidiary", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteMF" }
	var fn_cb_siteMF = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&MFStageSETLocation'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteDC" }
    var fn_cb_siteDC = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&NSUIToLocationDC'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "To Location", DimAttbName : "To Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_tpmodeGO" }
    var fn_cb_tpmodeGO = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&NSUITransModeView'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Trans Mode", DimAttbName : "Trans Mode", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_MPHorizon" }
    var fn_cb_MPHorizon = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&MPHorizon'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], "", "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Time", DimAttbName : "Week", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_SETItem_BODValid_csiteMF_csiteDC", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "S356" } }
    var fn_cb_SETItem_BODValid_csiteMF_csiteDC = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&SETItem'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var where = 'where { &CWVUI, Measure.[BOD List_BOD Valid] == "Y", ' +
                            '&nsuilocationplant.[' + parsedParams.fbParams["[Location].[Location]"] + '], ' +
                            '&nsuisublocationdc.[' + parsedParams.fbParams["[Sub Location].[Sub Location]"] + '], ' +
                            'Measure.[BOD Item_Asn]==1 }';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_inch", "fbParams" : { "includeField" : "Item:Product Group:UI Product Group,Item:Product:UI Product" } }
    // { "fbFuncName" : "fn_cb_inch", "fbParams" : { "includeField" : "Item:Product:UI Product" } }
	var fn_cb_inch = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Inch].filter(#.Name != "-").relatedmembers([Inch])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_project" }
    var fn_cb_project = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Project].filter(#.Name != "-").relatedmembers([Project])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setProject" }
    var fn_cb_setProject = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var dims = ['[Item].[Project].filter(#.Name != "-").relatedmembers([Project])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Project", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };

        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setBasic", "fbParams" : { "includeField" : "Item:Project:Project" } }
    // { "fbFuncName" : "fn_cb_setBasic", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G"} } }
    var fn_cb_setBasic = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Basic Name].filter(#.Name != "-").relatedmembers([Basic Name])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Basic Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "includeField" : "Item:Project:Project,Item:Basic Name:Basic Name" } }
    // { "fbFuncName" : "fn_cb_setInch", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU" } } }
    var fn_cb_setInch = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Inch].filter(#.Name != "-").relatedmembers([Inch])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Inch", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU", "[Item].[Inch]" : "50" } } }
    // { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ60G" } } }
    // { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "QAQ%" } } }
    // { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "%60G" } } }
    // { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : "%AQ60%" } } }
    // { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : ["QAQ60G", "QTQ60F"] } } }
    // { "fbFuncName" : "fn_cb_setItem", "fbParams" : { "where" : { "[Item].[Project]" : ["QAQ60G", "QTQ60F"] } } }
    var fn_cb_setItem = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Item]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_materialWithDesc" }
    var fn_cb_materialWithDesc = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ["[Item Material].[Item Material]", "[Item Material].[Description]"];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item Material", DimAttbName : "Item Material", DimDescAttbName : "Description", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setYear", "fbParams" : { "includeField" : "Item:Product Group:ProductGroup,Item:Definition:Definition,Item:Project:Project,Item:Marketing Name:MarketingName" } }
    var fn_cb_setYear = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Year].filter(#.Name != "-").relatedmembers([Year])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Year", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setDefinition", "fbParams" : { "includeField" : "Item:Product Group:ProductGroup,Item:Project:Project,Item:Marketing Name:MarketingName" } }
    var fn_cb_setDefinition = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Definition].filter(#.Name != "-").relatedmembers([Definition])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Definition", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setMarketingName", "fbParams" : { "includeField" : "Item:Product Group:ProductGroup,Item:Definition:Definition,Item:Project:Project" } }
    var fn_cb_setMarketingName = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Marketing Name].filter(#.Name != "-").relatedmembers([Marketing Name])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Marketing Name", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_productGroup" }
    var fn_cb_productGroup = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Product Group].filter(#.Name != "-").relatedmembers([Product Group])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setProductGroup" }
    var fn_cb_setProductGroup = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Item].[Product Group].filter(#.Name != "-").relatedmembers([Product Group])'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            // where절 세팅
            parsedParams.fbParams.where["[Item].[Item Stage]"] = "SET";

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Product Group", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteMFMtrl" }
    // { "fbFuncName" : "fn_cb_siteMFMtrl","fbParams" : {"includeField" : "Location:Company:Company" ,"where" : { "Location.[All Location]" : "All" }, "limit" : 10 ,"existAll" : true} }
    var fn_cb_siteMFMtrl = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&NSUILocationMFMtrlView'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteFrom" }
    var fn_cb_siteFrom = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
		    var dims = ['&NSUILocationPlant'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, ["Measure.[BOD List_BOD Valid]"],
                                             'where {&CWVUI, [Sub Location].[Sub Location], [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField,
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank,
                                                    isDisplayNameWithCode : parsedParams.fbParams.isDisplayNameWithCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

    // { "fbFuncName" : "fn_cb_siteTo","fbParams" : { "Location.[Location]" : ["P306","P54A"]} }
    var fn_cb_siteTo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

        try {
            var fbLocation = parsedParams.fbParams["Location.[Location]"];

            var dims = ['&NSUISubLocationDC'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, ["Measure.[BOD List_BOD Valid]"],
                                             'where { &CWVUI, [Location].[Location]' + vdUtil.fn_filterStr(fbLocation) + ', [Trans Mode].[Trans Mode], ' +
                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
                                             "",
                                             "");

            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll,
                                                    isDisplayNameWithCode : parsedParams.fbParams.isDisplayNameWithCode});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return comboList;
        } catch ( e ) {
            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
            return;
        }
    };

// 필요할까?
    // { "fbFuncName" : "fn_cb_siteFromTo" }
//    var fn_cb_siteFromTo = function(parsedParams){
//        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
//        vdCommon.setLogLevel("Debug");
//
//        try {
//            // location 을 구한다.
//            var fbLocation = [];
//            var result = vdCommon.selectList(['&SETLocation'], ["Measure.[BOD List_BOD Valid]"],
//                                             'where {&CWVUI, [Sub Location].[Sub Location], [Trans Mode].[Trans Mode], ' +
//                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
//                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
//                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
//                                             "",
//                                             "");
//            for ( var i = 0; i < result.cs.rowCount; i++ ) {
//                fbLocation.push(result.cs.row(i).cell(result.cs.memberColumnIndex("Location", "Location")).Name);
//            }
//
//            // Sub Location 을 가져온다.
//            var dims = ['&NSUISubLocationDC', '[Location].[Location]' + vdUtil.fn_filterStr(fbLocation)];
//
//		    // Casecade 를 위해서 Dimension 추가
//		    parsedParams.fbParams.includeField = "Location:Location:Location";
//
//            var result = vdCommon.selectList(dims, ["Measure.[BOD List_BOD Valid]"],
//                                             'where { &CWVUI, [Trans Mode].[Trans Mode], ' +
//                                                'Measure.[BOD List_BOD Valid] == "Y", ' +
//                                                'coalesce(Measure.[BOD List_Eff Startdate],DATEADD(Now(),-1,"Day")) < now(), ' +
//                                                'coalesce(Measure.[BOD List_Eff Enddate],DATEADD(Now(),1,"Day")) > now()}',
//                                             "",
//                                             "");
//
//            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName",
//                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll,
//                                                    isDisplayNameWithCode : parsedParams.fbParams.isDisplayNameWithCode});
//            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));
//
//            vdCommon.programEnd();
//
//            return comboList;
//        } catch ( e ) {
//            RuleOutputToUI = { Status : 'Error', Message : "Js Logic Error : " + e.message };
//            return;
//        }
//    };

    // { "fbFuncName" : "fn_cb_shipmentType" }
	var fn_cb_shipmentType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["ALL","INDIR","DIR_S"], ComboValues : ["ALL","INDIR","DIR_S"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setYNH" }
	var fn_cb_setYNH = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N","-"], ComboValues : ["Y","N","-"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setYN" }
	var fn_cb_setYN = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["Y","N"], ComboValues : ["Y","N"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_planGroup" }
    var fn_cb_planGroup = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['Item.[Plan Group]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Plan Group", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_locationJdmType" }
    var fn_cb_locationJdmType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["JDM","Nomal"], ComboValues : ["JDM","Nomal"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_scmType" }
    var fn_cb_scmType = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['Item.[SCM Type].filter(~(#.Name =="-"))'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "SCM Type", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_confirm" }
    var fn_cb_confirm = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var comboList = vdCommon.fn_makeCombo(null, {ComboCodes : ["REQ","CON"], ComboValues : ["REQ","CON"],
                                                    existAll : parsedParams.fbParams.existAll,
                                                    existBlank : parsedParams.fbParams.existBlank});

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteMfValidBod" }
    var fn_cb_siteMfValidBod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Location].[Location]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var where = 'where { &CWVUI, Measure.[BOD List_BOD Valid] == "Y", Measure.[BOD Item_Asn]==1 }';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby [Location].[Location].DisplayName", parsedParams.fbParams.limit);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteMfDcValidBod", "fbParams" : { "[Location].[Location]" : "P105" } }
    var fn_cb_siteMfDcValidBod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['[Sub Location].[Sub Location]',
		                    '[Location].[Location]' + vdUtil.fn_filterStr(parsedParams.fbParams["[Location].[Location]"])];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            parsedParams.fbParams.includeField += ( parsedParams.fbParams.includeField == "" ? "" : "," ) + "Location:Location:Location";


            var where = 'where { &CWVUI, Measure.[BOD List_BOD Valid] == "Y", Measure.[BOD Item_Asn]==1 }';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby [Sub Location].[Sub Location].DisplayName", parsedParams.fbParams.limit);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Sub Location", DimAttbName : "Sub Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_setItemValidBod", "fbParams" : { "[Location].[Location]" : "P105", "[Sub Location].[Sub Location]" : "S356" } }
    var fn_cb_setItemValidBod = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&SETItem'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var where = 'where { &CWVUI, Measure.[BOD List_BOD Valid] == "Y", ';
            if ( parsedParams.fbParams["[Location].[Location]"] != undefined ) {
                where += '[Location].[Location].[' + parsedParams.fbParams["[Location].[Location]"] + '], ';
            }
            if ( parsedParams.fbParams["[Sub Location].[Sub Location]"] != undefined ) {
                where += '[Sub Location].[Sub Location].[' + parsedParams.fbParams["[Sub Location].[Sub Location]"] + '], ';
            }
            where += 'Measure.[BOD Item_Asn]==1 }';
            var result = vdCommon.selectList(dims, ["Measure.[BOD Item_Asn]"], where, "orderby Item.Item.DisplayName", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Item", DimAttbName : "Item", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_siteMfLcm" }
	var fn_cb_siteMfLcm = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['&MFStageLCMLocation'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Location", DimAttbName : "Location", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_company" }
	var fn_cb_company = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['Company.[Company]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Company", DimAttbName : "Company", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_cb_country" }
	var fn_cb_country = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var dims = ['Country.[Country]'];

		    // Casecade 를 위해서 Dimension 추가
		    dims = fn_addincludeField(dims, parsedParams);

            var result = vdCommon.selectList(dims, [], fn_makeWhere(parsedParams), "", parsedParams.fbParams.limit);
            //vdCommon.printCsData(result, 3);
            var comboList = vdCommon.fn_makeCombo(result, {DimName : "Country", DimAttbName : "Country", Sort : "DisplayName",
                                                    includeField : parsedParams.fbParams.includeField, existAll : parsedParams.fbParams.existAll});
            vdCommon.debug("ComboData : " + JSON.stringify(comboList.slice(0,3)));

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : comboList };
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };



/************************************************* common logic *************************************************/
    // { "fbFuncName" : "fn_updateInfo", "fbParams" : { "version" : "CWV_MP", "measureList" : ["Measure.[VersionInfo_Time Phased BOD Master Update User]", "Measure.[VersionInfo_Time Phased BOD Master Update Time]"] } }
    var fn_updateInfo = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
            var result = vdCommon.selectList(["[Version].[Version Name].[" + parsedParams.fbParams.version + "]"], parsedParams.fbParams.measureList, "", "", "");
            var rtn = { "Code" : 0, "Msg" : "" };
            for ( var i = 0; i < result.cs.rowCount; i++ ) {
                for ( var m = 0; m < parsedParams.fbParams.measureList.length; m++ ) {
                    var measure = parsedParams.fbParams.measureList[m];
                    rtn[measure] = result.cs.row(i).cell(result.cs.measureColumnIndex(fn_getMeasureName(measure)));
                }
            }

            vdCommon.programEnd();

            return rtn;
        } catch ( e ) {
            vdCommon.error(e.message);
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* util logic *************************************************/
    // Dimension 에 includeField의 정보를 추가한다.
    var fn_addincludeField = function(dims, parsedParams){
        if ( parsedParams.fbParams["includeField"] != "" ) {
            var includeField = parsedParams.fbParams.includeField.split(",");
            for ( var i = 0; i < includeField.length; i++ ) {
                var tSplit = includeField[i].split(":");
                dims.push("[" + tSplit[0] + "].[" + tSplit[1] + "]");
            }
        }

        return dims;
    }

    var fn_getMeasureName = function(measure){
        var measureSplit = measure.split(".");
        return measureSplit[1].replace("[", "").replace("]", "")
    }

    // where 절 생성
    var fn_makeWhere = function(parsedParams){
        var whereStr = "";
        var where = parsedParams.fbParams["where"];
        for ( let key in where ) {
            whereStr += ( whereStr == "" ? "" : ", " ) + key + vdUtil.fn_filterStr(where[key]);
        }

        if ( whereStr == "" ) {
            return "";
        } else {
            return "where { " + whereStr + " } ";
        }
    }

/************************************************* sample logic *************************************************/

    //{ "fbFuncName" : "fn_validation", "fbGridRows" : [{ "Field11" : "11", "Field12" : "12", "Field13" : "13"}, { "Field11" : "21", "Field12" : "22", "Field13" : "23"}, { "Field11" : "31", "Field12" : "32", "Field13" : "33"}] }
    var fn_validation = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {

            for ( var i = 0; i < parsedParams.fbGridRows.length; i++ ) {
                parsedParams.fbGridRows[i]["Rtn1"] = i;
                parsedParams.fbGridRows[i]["Rtn2"] = i + 1;
            }

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : parsedParams.fbGridRows };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

    // { "fbFuncName" : "fn_commonTest" }
    var fn_commonTest = function(parsedParams){
        const vdCommon = new commonLib.VdCommon(programName + "." + arguments.callee.name);
        vdCommon.setLogLevel("Debug");

		try {
		    var rtn = {};

            rtn["fn_cb_jdm"] = fn_cb_jdm(parsedParams).Rows;
            rtn["fn_cb_mfSiteStageForMF"] = fn_cb_mfSiteStageForMF(parsedParams).Rows;
            rtn["fn_cb_subsidiaryForMF"] = fn_cb_subsidiaryForMF(parsedParams).Rows;
            rtn["fn_cb_siteMF"] = fn_cb_siteMF(parsedParams).Rows;
            rtn["fn_cb_siteDC"] = fn_cb_siteDC(parsedParams).Rows;
            rtn["fn_cb_tpmodeGO"] = fn_cb_tpmodeGO(parsedParams).Rows;
            rtn["fn_cb_MPHorizon"] = fn_cb_MPHorizon(parsedParams).Rows;
            parsedParams.fbParams["[Location].[Location]"] = "P105";
            parsedParams.fbParams["[Sub Location].[Sub Location]"] = "S356";
            rtn["fn_cb_SETItem_BODValid_csiteMF_csiteDC"] = fn_cb_SETItem_BODValid_csiteMF_csiteDC(parsedParams).Rows;
            parsedParams.fbParams.where = {};
            parsedParams.fbParams["includeField"] = "Item:Product Group:UI Product Group,Item:Product:UI Product";
            rtn["fn_cb_inch"] = fn_cb_inch(parsedParams).Rows;
            parsedParams.fbParams.where = {};
            parsedParams.fbParams["includeField"] = "";
            rtn["fn_cb_setProject"] = fn_cb_setProject(parsedParams).Rows;
            parsedParams.fbParams.where = {};
            parsedParams.fbParams.where["[Item].[Project]"] = "QAQ60G";
            rtn["fn_cb_setBasic"] = fn_cb_setBasic(parsedParams).Rows;
            parsedParams.fbParams.where = {};
            parsedParams.fbParams.where["[Item].[Basic Name]"] = "QTV-F55Q60A/EU";
            rtn["fn_cb_setInch"] = fn_cb_setInch(parsedParams).Rows;
            parsedParams.fbParams.where = {};
            parsedParams.fbParams.where["[Item].[Inch]"] = "50";
            rtn["fn_cb_setItem"] = fn_cb_setItem(parsedParams).Rows;
//            parsedParams.fbParams.where = {};
//            parsedParams.fbParams.where["[Item].[Project]"] = "QAQ%";
//            parsedParams.fbParams.where["[Item].[Basic Name]"] = "";
//            parsedParams.fbParams.where["[Item].[Inch]"] = "";
//            rtn["fn_cb_setItem2"] = fn_cb_setItem(parsedParams).Rows;
//            parsedParams.fbParams.where["[Item].[Project]"] = "%60G";
//            rtn["fn_cb_setItem3"] = fn_cb_setItem(parsedParams).Rows;
//            parsedParams.fbParams.where["[Item].[Project]"] = "%AQ60%";
//            rtn["fn_cb_setItem4"] = fn_cb_setItem(parsedParams).Rows;
//            parsedParams.fbParams.where["[Item].[Project]"] = ["QAQ60G", "QTQ60F"];
//            rtn["fn_cb_setItem5"] = fn_cb_setItem(parsedParams).Rows;

            rtn["fn_getMondayForWeek"] = vdCommon.fn_getMondayForWeek("202501,202502,202503");
            rtn["fn_getMondayForNS"] = vdCommon.fn_getMondayForNS("MPHroizon");

            vdCommon.programEnd();

            return { "Code" : 0, "Msg" : "", "Rows" : rtn };
        } catch ( e ) {
            return { "Code" : -1, "Msg" : e.message };
        }
    };

/************************************************* Mapping logic *************************************************/
    // Mapping 함수 정의, 마지막에 선언을 해야 함수를 정상적으로 인식함
    const functionMap = {
        "fn_cb_common" : fn_cb_common
        ,"fn_cb_jdm" : fn_cb_jdm
        ,"fn_cb_mfSiteStageForMF" : fn_cb_mfSiteStageForMF
        ,"fn_cb_subsidiaryForMF" : fn_cb_subsidiaryForMF
        ,"fn_cb_siteMF" : fn_cb_siteMF
        ,"fn_cb_siteDC" : fn_cb_siteDC
        ,"fn_cb_tpmodeGO" : fn_cb_tpmodeGO
        ,"fn_updateInfo" : fn_updateInfo
        ,"fn_validation" : fn_validation
        ,"fn_cb_inch" : fn_cb_inch
        ,"fn_cb_MPHorizon" : fn_cb_MPHorizon
        ,"fn_cb_SETItem_BODValid_csiteMF_csiteDC" : fn_cb_SETItem_BODValid_csiteMF_csiteDC
        ,"fn_cb_setProject" : fn_cb_setProject
        ,"fn_cb_project" : fn_cb_project
        ,"fn_cb_setBasic" : fn_cb_setBasic
        ,"fn_cb_setInch" : fn_cb_setInch
        ,"fn_cb_setItem" : fn_cb_setItem
        ,"fn_cb_materialWithDesc" : fn_cb_materialWithDesc
        ,"fn_cb_setYear" : fn_cb_setYear
        ,"fn_cb_setDefinition" : fn_cb_setDefinition
        ,"fn_cb_setMarketingName" : fn_cb_setMarketingName
        ,"fn_cb_productGroup" : fn_cb_productGroup
        ,"fn_cb_setProductGroup" : fn_cb_setProductGroup
        ,"fn_cb_siteMFMtrl" : fn_cb_siteMFMtrl
        ,"fn_cb_siteFrom" : fn_cb_siteFrom
        ,"fn_cb_siteTo" : fn_cb_siteTo
//        ,"fn_cb_siteFromTo" : fn_cb_siteFromTo
        ,"fn_cb_shipmentType" : fn_cb_shipmentType
        ,"fn_cb_setYNH" : fn_cb_setYNH
        ,"fn_cb_setYN" : fn_cb_setYN
        ,"fn_commonTest" : fn_commonTest
        ,"fn_cb_planGroup" : fn_cb_planGroup
        ,"fn_cb_locationJdmType" : fn_cb_locationJdmType
        ,"fn_cb_scmType" : fn_cb_scmType
        ,"fn_cb_confirm" : fn_cb_confirm
        ,"fn_cb_siteMfValidBod" : fn_cb_siteMfValidBod
        ,"fn_cb_siteMfDcValidBod" : fn_cb_siteMfDcValidBod
        ,"fn_cb_setItemValidBod" : fn_cb_setItemValidBod
        ,"fn_cb_siteMfLcm" : fn_cb_siteMfLcm
        ,"fn_cb_company" : fn_cb_company
        ,"fn_cb_country" : fn_cb_country
    };

    return {
        fn_loadFunction : fn_loadFunction
    };
});


/*
* Call
{
    "fbFuncName" : "fn_cb_setDefinition" => 함수 정의
    ,"fbParams" : {
        "includeField" : "Item:Product Group:ProductGroup,Item:Project:Project,Item:Marketing Name:MarketingName" => 화면에서 lookup 콤보 구성할 때
        ,"where" : { "[Item].[Project]" : "QAQ60G", "[Item].[Basic Name]" : "QTV-F55Q60A/EU" } => 조건을 걸 때
        ,"limit" : 10 => 갯수를 제한할 때
        ,"existAll" : true => 상단에 All 을 추가할 때
        ,"existBlank" : true => 상단에 Blank 을 추가할 때(선택을 안할 경우에 사용)
        ,"version" : "CWV_MP" => 파라미터를 넘길 때
        ,"measureList" : ["Measure.[VersionInfo_Time Phased BOD Master Update User]", "Measure.[VersionInfo_Time Phased BOD Master Update Time]"] => 파라미터를 넘길 때
    }
    ,"fbGridRows" : [
        {"rowstatus":"C","rowindex":0,"Measure.[Vendor_code]":"P406","Measure.[Vendor_Name]":"SEH(VD)","Measure.[Data Type_Code]":"SOP","Measure.[Plant_Code]":"P306","Measure.[Validation]":"-","[Version].[Version Name]":"VD","[Personnel].[Email]":"sungmin0.lim@partner.samsung.com","[Seg].[Seg]":"SEH(VD)","[Layout].[Layout]":"Standard","[Seq].[Seq]":"1","Measure.[Base]":"202442","Measure.[Plant]":"P306-SAMEX","Measure.[Material]":"","Measure.[Vendor]":"솔루엠","Measure.[Data type]":"SOP","Measure.[LT]":"","Measure.[W01]":"2593","Measure.[W02]":"1360","Measure.[W03]":"2600","Measure.[W04]":"324","Measure.[W05]":"1467","Measure.[W06]":"4268","Measure.[W07]":"3230","Measure.[W08]":"403","Measure.[W09]":"1892","Measure.[W10]":"1347","Measure.[W11]":"0","Measure.[W12]":"3340","Measure.[W13]":"126","Measure.[W14]":"3150","Measure.[W15]":"1170","Measure.[W16]":"0","Measure.[W17]":"0","Measure.[W18]":"0","Measure.[W19]":"3580","Measure.[W20]":"2600","Measure.[W21]":"4250","Measure.[W22]":"2500","Measure.[W23]":"1100","Measure.[W24]":"1100"}
        ,{"rowstatus":"C","rowindex":1,"Measure.[Vendor_code]":"P406","Measure.[Vendor_Name]":"SEH(VD)","Measure.[Data Type_Code]":"SOP(W-1)","Measure.[Plant_Code]":"P306","Measure.[Validation]":"-","[Version].[Version Name]":"VD","[Personnel].[Email]":"sungmin0.lim@partner.samsung.com","[Seg].[Seg]":"SEH(VD)","[Layout].[Layout]":"Standard","[Seq].[Seq]":"2","Measure.[Base]":"202442","Measure.[Plant]":"P306-SAMEX","Measure.[Material]":"","Measure.[Vendor]":"솔루엠","Measure.[Data type]":"SOP(W-1)","Measure.[LT]":"","Measure.[W01]":"0","Measure.[W02]":"1360","Measure.[W03]":"4400","Measure.[W04]":"1999","Measure.[W05]":"990","Measure.[W06]":"1300","Measure.[W07]":"3150","Measure.[W08]":"0","Measure.[W09]":"1090","Measure.[W10]":"1272","Measure.[W11]":"0","Measure.[W12]":"3340","Measure.[W13]":"126","Measure.[W14]":"2200","Measure.[W15]":"950","Measure.[W16]":"4170","Measure.[W17]":"0","Measure.[W18]":"1500","Measure.[W19]":"3330","Measure.[W20]":"2050","Measure.[W21]":"3300","Measure.[W22]":"2200","Measure.[W23]":"1100","Measure.[W24]":"0"}
    ] => 추가, 수정, 삭제 데이타를 넘길 때
}

* Return
{
    "Code" : -1, 0, 1
    ,"Msg" : ""
    ,"Rows" : [{},{},{}]
}


*/

/**************************** o9.NSCM.JSEWCommon ****************************
    2025-06-17 : 신규 생성
    2025-06-23 : 콤보 데이타 조회시 갯수 제한 ( 3,000 개 )
    2025-06-24 : 콤보 구성시 existAll 파라미터 추가
    2025-07-03 : 콤보 구성시 existBlank 파라미터 추가
    2025-07-30 : 사용안함 -> o9.NSCM.JSEWCommonVD 로 관리
*********************************************************************/